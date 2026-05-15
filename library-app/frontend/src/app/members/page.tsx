"use client";

import { useEffect, useState } from "react";
import { membersApi, type Member } from "@/lib/api";

const emptyForm = { name: "", email: "", phone: "", address: "", is_active: true };

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Member | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = (q?: string) =>
    membersApi.list({ search: q }).then(setMembers).catch(() => {});

  useEffect(() => { load(); }, []);

  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); load(search); };

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setError("");
    setShowForm(true);
  };

  const openEdit = (m: Member) => {
    setEditing(m);
    setForm({ name: m.name, email: m.email, phone: m.phone ?? "", address: m.address ?? "", is_active: m.is_active });
    setError("");
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = { ...form, phone: form.phone || undefined, address: form.address || undefined };
      if (editing) {
        await membersApi.update(editing.id, payload);
      } else {
        await membersApi.create(payload);
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
    if (!confirm("Delete this member?")) return;
    try { await membersApi.delete(id); load(); } catch (e: any) { alert(e.message); }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Members</h1>
        <button onClick={openCreate} className="btn-primary">+ Add Member</button>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input className="input flex-1" placeholder="Search by name or email…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <button type="submit" className="btn-secondary">Search</button>
        <button type="button" className="btn-ghost" onClick={() => { setSearch(""); load(); }}>Clear</button>
      </form>

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md space-y-3">
            <h2 className="text-xl font-semibold">{editing ? "Edit Member" : "Add Member"}</h2>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <input className="input w-full" placeholder="Full Name *" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input className="input w-full" placeholder="Email *" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input className="input w-full" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <textarea className="input w-full resize-none" placeholder="Address" rows={2} value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
              Active member
            </label>
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
              {["Name", "Email", "Phone", "Joined", "Status", "Actions"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-gray-600">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {members.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">No members found</td></tr>
            )}
            {members.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{m.name}</td>
                <td className="px-4 py-3">{m.email}</td>
                <td className="px-4 py-3 text-gray-500">{m.phone ?? "—"}</td>
                <td className="px-4 py-3 text-gray-500">{m.membership_date}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${m.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    {m.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="px-4 py-3 flex gap-2">
                  <button onClick={() => openEdit(m)} className="text-indigo-600 hover:underline text-xs">Edit</button>
                  <button onClick={() => handleDelete(m.id)} className="text-red-500 hover:underline text-xs">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
