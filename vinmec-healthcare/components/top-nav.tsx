"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Trang chủ" },
  { href: "/today", label: "Lịch hôm nay" },
  { href: "/chat", label: "Chat AI" },
  { href: "/demo", label: "Demo" },
];

export function TopNav() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center gap-2 text-sm">
      {links.map((link) => {
        const isActive = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={isActive ? "page" : undefined}
            className={[
              "rounded-full px-3 py-1.5 font-medium transition",
              isActive
                ? "border border-emerald-900/15 bg-emerald-50 text-[var(--color-primary)]"
                : "text-slate-700 hover:bg-emerald-50 hover:text-emerald-800",
            ].join(" ")}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
