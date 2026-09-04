import type { ReactNode } from "react";
import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function AccountShell({ children }: { children: ReactNode }) {
  return <main className="min-h-screen bg-background font-sans antialiased"><Navbar /><Container className="pb-20 pt-32">{children}</Container><Footer /></main>;
}
