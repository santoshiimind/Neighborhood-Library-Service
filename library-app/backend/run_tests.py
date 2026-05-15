import sys
import time
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"
RUN = int(time.time())  # unique suffix per run


def req(method, path, data=None):
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    r = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            body = resp.read()
            try:
                return resp.status, json.loads(body) if body else {}
            except json.JSONDecodeError:
                return resp.status, {}
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body) if body else {}
        except json.JSONDecodeError:
            return e.code, {}


def show(label, status, body):
    print(f"\n{'='*55}")
    print(f"[{status}] {label}")
    print(json.dumps(body, indent=2, default=str)[:600])


passed = 0
failed = 0


def check(label, condition, status, body):
    global passed, failed
    if condition:
        print(f"  PASS: {label}")
        passed += 1
    else:
        print(f"  FAIL: {label}  (status={status})")
        print(f"        {body}")
        failed += 1


# ── Stats ─────────────────────────────────────────────────────
s, stats = req("GET", "/stats")
show("GET /stats", s, stats)
check("stats returns 200", s == 200, s, stats)

# ── Create books ──────────────────────────────────────────────
s, book = req("POST", "/books", {
    "title": f"Clean Code {RUN}",
    "author": "Robert Martin",
    "isbn": f"978-{RUN}",
    "genre": "Software Engineering",
    "published_year": 2008,
    "total_copies": 2,
})
show("POST /books", s, book)
check("book created (201)", s == 201, s, book)
check("available_copies == total_copies on create", book.get("available_copies") == 2, s, book)
book_id = book["id"]

s, book2 = req("POST", "/books", {
    "title": "The Pragmatic Programmer",
    "author": "David Thomas",
    "total_copies": 1,
})
show("POST /books (2nd)", s, book2)
check("2nd book created", s == 201, s, book2)
book2_id = book2["id"]

# Duplicate ISBN
s, r = req("POST", "/books", {"title": "Dup", "author": "X", "isbn": f"978-{RUN}", "total_copies": 1})
show("POST /books duplicate ISBN", s, r)
check("duplicate ISBN rejected (409)", s == 409, s, r)

# ── Create members ────────────────────────────────────────────
s, member = req("POST", "/members", {
    "name": f"Alice Johnson {RUN}",
    "email": f"alice.{RUN}@example.com",
    "phone": "555-0100",
})
show("POST /members", s, member)
check("member created (201)", s == 201, s, member)
member_id = member["id"]

s, member2 = req("POST", "/members", {"name": f"Bob Smith {RUN}", "email": f"bob.{RUN}@example.com"})
show("POST /members (2nd)", s, member2)
check("2nd member created", s == 201, s, member2)
member2_id = member2["id"]

# Duplicate email
s, r = req("POST", "/members", {"name": "Alice2", "email": f"alice.{RUN}@example.com"})
show("POST /members duplicate email", s, r)
check("duplicate email rejected (409)", s == 409, s, r)

# ── Borrow operations ─────────────────────────────────────────
s, loan = req("POST", "/loans/borrow", {"book_id": book_id, "member_id": member_id})
show("POST /loans/borrow", s, loan)
check("borrow succeeds (201)", s == 201, s, loan)
check("loan status is active", loan.get("status") == "active", s, loan)
check("loan has due_date", bool(loan.get("due_date")), s, loan)
loan_id = loan["id"]

# Check book available_copies decremented
s, b = req("GET", f"/books/{book_id}")
check("available_copies decremented to 1", b.get("available_copies") == 1, s, b)

# Duplicate active loan for same member+book
s, r = req("POST", "/loans/borrow", {"book_id": book_id, "member_id": member_id})
show("POST /loans/borrow (duplicate)", s, r)
check("duplicate loan rejected (409)", s == 409, s, r)

# Borrow book2 (1 copy)
s, loan2 = req("POST", "/loans/borrow", {"book_id": book2_id, "member_id": member2_id})
show("POST /loans/borrow (book2 by Bob)", s, loan2)
check("book2 borrowed", s == 201, s, loan2)
loan2_id = loan2["id"]

# No copies left for book2
s, r = req("POST", "/loans/borrow", {"book_id": book2_id, "member_id": member_id})
show("POST /loans/borrow (no copies)", s, r)
check("no copies available rejected (409)", s == 409, s, r)

# ── Query loans ───────────────────────────────────────────────
s, loans = req("GET", "/loans")
show(f"GET /loans (all)", s, loans)
check("list all loans returns 200", s == 200, s, loans)
check("loan count >= 2", len(loans) >= 2, s, loans)

s, alice_loans = req("GET", f"/loans/member/{member_id}")
show("GET /loans/member/alice", s, alice_loans)
check("Alice has 1 active loan", len(alice_loans) == 1, s, alice_loans)

s, book_history = req("GET", f"/loans/book/{book_id}")
show("GET /loans/book/{id}", s, book_history)
check("book loan history returns list", isinstance(book_history, list), s, book_history)

# ── Return book ───────────────────────────────────────────────
s, r = req("POST", f"/loans/{loan_id}/return")
show(f"POST /loans/{loan_id}/return", s, r)
check("return succeeds (200)", s == 200, s, r)
check("status is returned", r.get("status") == "returned", s, r)
check("returned_at is set", bool(r.get("returned_at")), s, r)

# available_copies incremented back
s, b = req("GET", f"/books/{book_id}")
check("available_copies restored to 2", b.get("available_copies") == 2, s, b)

# Return again
s, r = req("POST", f"/loans/{loan_id}/return")
show("POST /loans/return (already returned)", s, r)
check("double return rejected (409)", s == 409, s, r)

# ── Update operations ─────────────────────────────────────────
s, r = req("PUT", f"/books/{book_id}", {"genre": "Engineering", "total_copies": 3})
show("PUT /books/{id}", s, r)
check("book updated (200)", s == 200, s, r)
check("genre updated", r.get("genre") == "Engineering", s, r)
check("total_copies updated to 3", r.get("total_copies") == 3, s, r)
check("available_copies scaled correctly (was 2, +1 = 3)", r.get("available_copies") == 3, s, r)

s, r = req("PUT", f"/members/{member_id}", {"phone": "555-9999"})
show("PUT /members/{id}", s, r)
check("member updated (200)", s == 200, s, r)
check("phone updated", r.get("phone") == "555-9999", s, r)

# ── List/search ───────────────────────────────────────────────
s, books = req("GET", f"/books?search=Clean+Code+{RUN}")
show(f"GET /books?search=Clean+Code+{RUN}", s, books)
check("search returns matching book", len(books) == 1 and "Clean" in books[0]["title"], s, books)

s, books = req("GET", "/books?available_only=true")
check("available_only filter works", all(b["available_copies"] > 0 for b in books), s, books)

s, members = req("GET", f"/members?search=alice.{RUN}")
check("member search works", len(members) == 1, s, members)

# ── Final stats ───────────────────────────────────────────────
s, stats = req("GET", "/stats")
show("GET /stats (final)", s, stats)
check("final stats: books > 0", stats.get("total_books", 0) >= 2, s, stats)
check("final stats: members > 0", stats.get("total_members", 0) >= 2, s, stats)
check("final stats: 1 active loan", stats.get("active_loans") == 1, s, stats)

# ── Delete operations ─────────────────────────────────────────
# Try deleting book with active loan (should 409)
s, r = req("DELETE", f"/books/{book2_id}")
show("DELETE /books with active loan", s, r)
check("delete blocked while on loan (409)", s == 409, s, r)

# Return loan2 first, then delete
req("POST", f"/loans/{loan2_id}/return")
s, r = req("DELETE", f"/books/{book2_id}")
check("delete succeeds after return (204)", s == 204, s, r)

print(f"\n{'='*55}")
print(f"Results: {passed} passed, {failed} failed")
if failed:
    sys.exit(1)
