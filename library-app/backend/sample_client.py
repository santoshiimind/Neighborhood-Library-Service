"""
Sample client demonstrating all library API operations.
Run:  python sample_client.py
Requires:  pip install httpx
"""

import httpx

BASE = "http://localhost:8000"


def pretty(label: str, resp: httpx.Response):
    print(f"\n{'─'*50}")
    print(f"{label}  [{resp.status_code}]")
    print(resp.json())


with httpx.Client(base_url=BASE, timeout=10) as c:

    # ── Stats ──────────────────────────────────────────────────────
    pretty("GET /stats", c.get("/stats"))

    # ── Create a book ──────────────────────────────────────────────
    r = c.post("/books", json={
        "title": "The Pragmatic Programmer",
        "author": "David Thomas",
        "isbn": "978-0135957059",
        "genre": "Software Engineering",
        "published_year": 2019,
        "total_copies": 3,
    })
    pretty("POST /books", r)
    book_id = r.json()["id"]

    # ── Create a member ────────────────────────────────────────────
    r = c.post("/members", json={
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "phone": "555-0100",
    })
    pretty("POST /members", r)
    member_id = r.json()["id"]

    # ── Borrow the book ────────────────────────────────────────────
    r = c.post("/loans/borrow", json={"book_id": book_id, "member_id": member_id})
    pretty("POST /loans/borrow", r)
    loan_id = r.json()["id"]

    # ── List active loans for this member ──────────────────────────
    pretty(f"GET /loans/member/{member_id}?status=active",
           c.get(f"/loans/member/{member_id}", params={"status": "active"}))

    # ── Attempt to borrow same book again (should 409) ─────────────
    r2 = c.post("/loans/borrow", json={"book_id": book_id, "member_id": member_id})
    pretty("POST /loans/borrow (duplicate – expected 409)", r2)

    # ── Return the book ────────────────────────────────────────────
    pretty(f"POST /loans/{loan_id}/return", c.post(f"/loans/{loan_id}/return"))

    # ── Check stats again ──────────────────────────────────────────
    pretty("GET /stats (after return)", c.get("/stats"))

    # ── Update book ────────────────────────────────────────────────
    pretty("PUT /books/{id}", c.put(f"/books/{book_id}", json={"genre": "Engineering"}))

    print("\nDone!")
