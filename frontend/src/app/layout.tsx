import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LeadForge",
  description: "Intelligent sales agent system",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
