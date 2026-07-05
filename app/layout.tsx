import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BeanCo | Specialty Coffee for Hospitality",
  description: "A commercial specialty coffee website for hospitality, office, retail, and tasting partnerships.",
  icons: {
    icon: "/favicon.ico.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
