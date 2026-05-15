"use client";

import { useEffect, useState } from "react";
import { booksApi, type Book } from "@/lib/api";

const emptyForm = {
  title: "",
  author: "",
  isbn: "",
  genre: "",
  published_year: "",
  total_copies: "1",
};

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Book | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async (q?: string) => {
    const data = await booksApi.list({ search: q }).catch(() => []);
    setBooks(data);
  };

  useEffect(() => { load(); }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load(search);
  };

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setError("");
    setShowForm(true);
  };

  const openEdit = (b: Book) => {
    setEditing(b);
    setForm({
      title: b.title,
      author: b.author,
      isbn: b.isbn ?? "",
      genre: b.genre ?? "",
      published_year: b.published_year?.toString() ?? "",
      total_copies: b.total_copies.toString(),
    });
    setError("");
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        title: form.title,
        author: form.author,
        isbn: form.isbn || undefined,
        genre: form.genre || undefined,
        published_year: form.published_year ? parseInt(form.published_year) : undefined,
        total_copies: parseInt(form.total_copies),
      };
      if (editing) {
        await booksApi.update(editing.id, payload);
      } else {
        await booksApi.create(payload);
      }
      setShowForm(false);
      load();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this book?")) return;
    try {
      await booksApi.delete(id);
      load();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Books</h1>
        <button onClick={openCreate} className="btn-primary">+ Add Book</button>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          className="input flex-1"
          placeholder="Search by title or author…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit" className="btn-secondary">Search</button>
        <button type="button" className="btn-ghost" onClick={() => { setSearch(""); load(); }}>Clear</button>
      </form>

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md space-y-3">
            <h2 className="text-xl font-semibold">{editing ? "Edit Book" : "Add Book"}</h2>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <input className="input w-full" placeholder="Title *" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <input className="input w-full" placeholder="Author *" required value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} />
            <input className="input w-full" placeholder="ISBN" value={form.isbn} onChange={(e) => setForm({ ...form, isbn: e.target.value })} />
            <input className="input w-full" placeholder="Genre" value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })} />
            <input className="input w-full" placeholder="Published Year" type="number" value={form.published_year} onChange={(e) => setForm({ ...form, published_year: e.target.value })} />
            <input className="input w-full" placeholder="Total Copies *" type="number" min="1" required value={form.total_copies} onChange={(e) => setForm({ ...form, total_copies: e.target.value })} />
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={loading} className="btn-primary flex-1">{loading ? "Saving…" : "Save"}</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-ghost flex-1">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              {["Title", "Author", "Genre", "ISBN", "Year", "Copies", "Available", "Actions"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-gray-600">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {books.length === 0 && (
              <tr><td colSpan={8} className="text-center py-8 text-gray-400">No books found</td></tr>
            )}
            {books.map((b) => (
              <tr key={b.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{b.title}</td>
                <td className="px-4 py-3">{b.author}</td>
                <td className="px-4 py-3 text-gray-500">{b.genre ?? "—"}</td>
                <td className="px-4 py-3 text-gray-500">{b.isbn ?? "—"}</td>
                <td className="px-4 py-3 text-gray-500">{b.published_year ?? "—"}</td>
                <td className="px-4 py-3">{b.total_copies}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${b.available_copies > 0 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {b.available_copies}
                  </span>
                </td>
                <td className="px-4 py-3 flex gap-2">
                  <button onClick={() => openEdit(b)} className="text-indigo-600 hover:underline text-xs">Edit</button>
                  <button onClick={() => handleDelete(b.id)} className="text-red-500 hover:underline text-xs">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
