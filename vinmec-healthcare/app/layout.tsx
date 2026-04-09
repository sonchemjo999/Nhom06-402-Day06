import type { Metadata } from "next";
import Link from "next/link";
import { TopNav } from "@/components/top-nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vinmec Healthcare",
  description: "Vinmec AI Assistant MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="h-full antialiased">
      <body className="min-h-full bg-[var(--color-surface)] text-slate-900">
        <div className="app-backdrop" aria-hidden />

        <header className="sticky top-0 z-30 border-b border-emerald-950/10 bg-white/85 backdrop-blur-md">
          <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
            <Link href="/" className="group inline-flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-700 transition group-hover:scale-125" />
              <p className="text-sm font-semibold tracking-[0.08em] text-[var(--color-primary)] uppercase">
                Vinmec AI Care
              </p>
            </Link>

            <TopNav />
          </div>
        </header>

        {children}
      </body>
    </html>
  );
}
