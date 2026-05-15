import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Neighborhood Library",
  description: "Library management system",
};

const navLinks = [
  { href: "/", label: "Dashboard" },
  { href: "/books", label: "Books" },
  { href: "/members", label: "Members" },
  { href: "/loans", label: "Loans" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="bg-indigo-700 text-white shadow">
          <div className="mx-auto max-w-6xl flex items-center gap-8 px-4 py-4">
            <span className="text-xl font-bold tracking-tight">📚 Neighborhood Library</span>
            <nav className="flex gap-4">
              {navLinks.map((l) => (
                <Link
                  key={l.href}
                  href={l.href}
                  className="text-indigo-100 hover:text-white transition-colors"
                >
                  {l.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
