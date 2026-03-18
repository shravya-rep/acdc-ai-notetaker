import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ACDC AI Notetaker",
  description: "Autonomous meeting intelligence for ACDC Teams meetings",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">
        <nav className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <h1 className="text-lg font-semibold text-blue-700">ACDC AI Notetaker</h1>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
