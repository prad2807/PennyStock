import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PennyStock Hidden Growth Platform",
  description: "Disciplined Indian hidden-growth and momentum research dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
