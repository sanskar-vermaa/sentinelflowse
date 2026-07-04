import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SentinelFlow",
  description: "AI incident response and workflow automation"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

