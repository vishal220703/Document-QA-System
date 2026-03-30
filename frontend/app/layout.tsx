import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DocQuest",
  description: "Modern document Q&A interface",
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
