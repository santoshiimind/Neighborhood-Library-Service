const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  genre?: string;
  published_year?: number;
  total_copies: number;
  available_copies: number;
  created_at: string;
  updated_at: string;
}

export interface Member {
  id: string;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  is_active: boolean;
  membership_date: string;
  created_at: string;
  updated_at: string;
}

export interface Loan {
  id: string;
  book_id: string;
  member_id: string;
  borrowed_at: string;
  due_date: string;
  returned_at?: string;
  fine_amount: string;
  status: "active" | "returned" | "overdue";
  book?: Book;
  member?: Member;
}

export interface Stats {
  total_books: number;
  total_members: number;
  active_loans: number;
  overdue_loans: number;
}

// ── Books API ─────────────────────────────────────────────────────────────────

export const booksApi = {
  list: (params?: { search?: string; genre?: string; available_only?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.search) q.set("search", params.search);
    if (params?.genre) q.set("genre", params.genre);
    if (params?.available_only) q.set("available_only", "true");
    return request<Book[]>(`/books?${q}`);
  },
  get: (id: string) => request<Book>(`/books/${id}`),
  create: (data: Omit<Book, "id" | "available_copies" | "created_at" | "updated_at">) =>
    request<Book>("/books", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Book>) =>
    request<Book>(`/books/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/books/${id}`, { method: "DELETE" }),
};

// ── Members API ───────────────────────────────────────────────────────────────

export const membersApi = {
  list: (params?: { search?: string; active_only?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.search) q.set("search", params.search);
    if (params?.active_only) q.set("active_only", "true");
    return request<Member[]>(`/members?${q}`);
  },
  get: (id: string) => request<Member>(`/members/${id}`),
  create: (data: Omit<Member, "id" | "membership_date" | "created_at" | "updated_at">) =>
    request<Member>("/members", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Member>) =>
    request<Member>(`/members/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/members/${id}`, { method: "DELETE" }),
};

// ── Loans API ─────────────────────────────────────────────────────────────────

export const loansApi = {
  list: (status?: string) => {
    const q = status ? `?status=${status}` : "";
    return request<Loan[]>(`/loans${q}`);
  },
  byMember: (memberId: string, status?: string) => {
    const q = status ? `?status=${status}` : "";
    return request<Loan[]>(`/loans/member/${memberId}${q}`);
  },
  overdue: () => request<Loan[]>("/loans/overdue"),
  borrow: (bookId: string, memberId: string) =>
    request<Loan>("/loans/borrow", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, member_id: memberId }),
    }),
  returnBook: (loanId: string) =>
    request<Loan>(`/loans/${loanId}/return`, { method: "POST" }),
};

// ── Stats API ─────────────────────────────────────────────────────────────────

export const statsApi = {
  get: () => request<Stats>("/stats"),
};
