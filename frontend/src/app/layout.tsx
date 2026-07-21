import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { LayoutDashboard, FileText, History, BarChart3, Settings } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Chethas | Autonomous Multi-Agent Intelligence",
  description: "Research-grade autonomous multi-agent intelligence platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-primary text-slate-100 flex min-h-screen`}>
        {/* Sidebar */}
        <aside className="w-64 border-r border-white/10 glass-card flex flex-col fixed inset-y-0 left-0 z-50">
          <div className="p-6 h-20 flex items-center">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white font-bold text-xl shadow-[0_0_15px_rgba(99,102,241,0.5)] group-hover:scale-110 transition-transform">
                C
              </div>
              <span className="text-xl font-bold tracking-tight gradient-text">Chethas</span>
            </Link>
          </div>
          
          <nav className="flex-1 px-4 py-4 space-y-1">
            <Link href="/" className="flex items-center gap-3 px-3 py-2.5 rounded-md bg-white/5 text-white font-medium">
              <LayoutDashboard className="w-5 h-5 text-indigo-400" />
              Overview
            </Link>
            <Link href="/documents" className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-white/5 text-slate-300 hover:text-white transition-colors font-medium">
              <FileText className="w-5 h-5 text-slate-400" />
              Documents
            </Link>
            <Link href="/history" className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-white/5 text-slate-300 hover:text-white transition-colors font-medium">
              <History className="w-5 h-5 text-slate-400" />
              History
            </Link>
            <Link href="/benchmarks" className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-white/5 text-slate-300 hover:text-white transition-colors font-medium">
              <BarChart3 className="w-5 h-5 text-slate-400" />
              Benchmarks
            </Link>
          </nav>
          
          <div className="p-4 mt-auto">
            <button className="flex items-center gap-3 px-3 py-2.5 w-full rounded-md hover:bg-white/5 text-slate-300 hover:text-white transition-colors font-medium">
              <Settings className="w-5 h-5 text-slate-400" />
              Settings
            </button>
          </div>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 pl-64 flex flex-col min-h-screen">
          <div className="flex-1 w-full relative">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
