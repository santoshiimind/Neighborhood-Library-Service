"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { statsApi, type Stats } from "@/lib/api";

function StatCard({
  label,
  value,
  color,
  href,
}: {
  label: string;
  value: number;
  color: string;
  href: string;
}) {
  return (
    <Link href={href}>
      <div className={`rounded-xl p-6 text-white shadow ${color} hover:opacity-90 transition`}>
        <p className="text-4xl font-bold">{value}</p>
        <p className="mt-1 text-sm opacity-90">{label}</p>
      </div>
    </Link>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    statsApi
      .get()
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-gray-500 mb-8">Library overview at a glance</p>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      {stats ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Total Books" value={stats.total_books} color="bg-indigo-600" href="/books" />
          <StatCard label="Members" value={stats.total_members} color="bg-emerald-600" href="/members" />
          <StatCard label="Active Loans" value={stats.active_loans} color="bg-sky-600" href="/loans?status=active" />
          <StatCard label="Overdue" value={stats.overdue_loans} color="bg-rose-600" href="/loans?status=overdue" />
        </div>
      ) : (
        !error && <p className="text-gray-400">Loading…</p>
      )}

      <div className="mt-10 grid md:grid-cols-3 gap-6">
        {[
          { href: "/books", title: "Manage Books", desc: "Add, edit, and browse the library catalogue." },
          { href: "/members", title: "Manage Members", desc: "Register new members and update contact info." },
          { href: "/loans", title: "Borrow & Return", desc: "Record borrowing and returning of books." },
        ].map((card) => (
          <Link key={card.href} href={card.href}>
            <div className="rounded-xl border bg-white p-6 shadow-sm hover:shadow-md transition">
              <h2 className="font-semibold text-lg mb-1">{card.title}</h2>
              <p className="text-gray-500 text-sm">{card.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
