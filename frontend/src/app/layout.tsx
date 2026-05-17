import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "WonderHow - AI Agent Simulation",
  description: "Autonomous multi-agent social simulation where AI personas debate, form opinions, and evolve beliefs",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}>
      <body className="min-h-full flex flex-col bg-[#0a0a0f] text-[#e4e4ef]">
        <nav className="sticky top-0 z-50 border-b border-[#2a2a4a] bg-[#0a0a0f]/80 backdrop-blur-md">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-14 items-center justify-between">
              <a href="/" className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-[#4f8aff] to-[#8b5cf6] bg-clip-text text-transparent">
                  WonderHow
                </span>
                <span className="text-xs text-[#9393b0] hidden sm:inline">Agent Simulation</span>
              </a>
              <div className="flex items-center gap-4">
                <a href="/" className="text-sm text-[#9393b0] hover:text-[#e4e4ef] transition-colors">Groups</a>
                <a href="/agents/all" className="text-sm text-[#9393b0] hover:text-[#e4e4ef] transition-colors">Agents</a>
              </div>
            </div>
          </div>
        </nav>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
