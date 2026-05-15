"use client";

import { useEffect, useState } from "react";
import { loansApi, booksApi, membersApi, type Loan, type Book, type Member } from "@/lib/api";

const STATUS_COLORS: Record<string, string> = {
  active: "bg-sky-100 text-sky-700",
  returned: "bg-gray-100 text-gray-500",
  overdue: "bg-rose-100 text-rose-700",
};

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [showBorrow, setShowBorrow] = useState(false);
  const [books, setBooks] = useState<Book[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [selectedBook, setSelectedBook] = useState("");
  const [selectedMember, setSelectedMember] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = (status?: string) =>
    loansApi.list(status || undefined).then(setLoans).catch(() => {});

  useEffect(() => { load(); }, []);

  const applyFilter = (s: string) => {
    setStatusFilter(s);
    load(s);
  };

  const openBorrow = async () => {
    const [b, m] = await Promise.all([
      booksApi.list({ available_only: true }),
      membersApi.list({ active_only: true }),
    ]);
    setBooks(b);
    setMembers(m);
    setSelectedBook("");
    setSelectedMember("");
    setError("");
    setShowBorrow(true);
  };

  const handleBorrow = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBook || !selectedMember) return;
    setLoading(true);
    setError("");
    try {
      await loansApi.borrow(selectedBook, selectedMember);
      setShowBorrow(false);
      load(statusFilter || undefined);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (loanId: string) => {
    if (!confirm("Mark this book as returned?")) return;
    try {
      await loansApi.returnBook(loanId);
      load(statusFilter || undefined);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const fmt = (d: string) => new Date(d).toLocaleDateString();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Loans</h1>
        <button onClick={openBorrow} className="btn-primary">+ Borrow Book</button>
      </div>

      {/* Status filter tabs */}
      <div className="flex gap-2 mb-6">
        {["", "active", "overdue", "returned"].map((s) => (
          <button
            key={s}
            onClick={() => applyFilter(s)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              statusFilter === s ? "bg-indigo-600 text-white" : "bg-white border text-gray-600 hover:bg-gray-50"
            }`}
          >
            {s === "" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Borrow modal */}
      {showBorrow && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <form onSubmit={handleBorrow} className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md space-y-3">
            <h2 className="text-xl font-semibold">Borrow a Book</h2>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <div>
              <label className="block text-sm font-medium mb-1">Book (available only)</label>
              <select
                className="input w-full"
                required
                value={selectedBook}
                onChange={(e) => setSelectedBook(e.target.value)}
              >
                <option value="">— select book —</option>
                {books.map((b) => (
                  <option key={b.id} value={b.id}>{b.title} by {b.author} ({b.available_copies} left)</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Member</label>
              <select
                className="input w-full"
                required
                value={selectedMember}
                onChange={(e) => setSelectedMember(e.target.value)}
              >
                <option value="">— select member —</option>
                {members.map((m) => (
                  <option key={m.id} value={m.id}>{m.name} ({m.email})</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={loading} className="btn-primary flex-1">
                {loading ? "Processing…" : "Confirm Borrow"}
              </button>
              <button type="button" onClick={() => setShowBorrow(false)} className="btn-ghost flex-1">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              {["Book", "Member", "Borrowed", "Due Date", "Returned", "Fine", "Status", "Actions"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-gray-600">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {loans.length === 0 && (
              <tr><td colSpan={8} className="text-center py-8 text-gray-400">No loans found</td></tr>
            )}
            {loans.map((l) => (
              <tr key={l.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{l.book?.title ?? l.book_id.slice(0, 8)}</td>
                <td className="px-4 py-3">{l.member?.name ?? l.member_id.slice(0, 8)}</td>
                <td className="px-4 py-3 text-gray-500">{fmt(l.borrowed_at)}</td>
                <td className="px-4 py-3 text-gray-500">{l.due_date}</td>
                <td className="px-4 py-3 text-gray-500">{l.returned_at ? fmt(l.returned_at) : "—"}</td>
                <td className="px-4 py-3 text-gray-500">
                  {parseFloat(l.fine_amount) > 0 ? (
                    <span className="text-rose-600 font-medium">${l.fine_amount}</span>
                  ) : "—"}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[l.status] ?? ""}`}>
                    {l.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {l.status !== "returned" && (
                    <button onClick={() => handleReturn(l.id)} className="text-emerald-600 hover:underline text-xs">
                      Return
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
