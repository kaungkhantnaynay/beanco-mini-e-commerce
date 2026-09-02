import CartPage from "@/components/CartPage";
import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function CartRoute() {
  return <main className="min-h-screen bg-background font-sans antialiased"><Navbar /><Container className="pb-20 pt-32"><h1 className="mb-8 text-4xl font-bold tracking-tight">Your cart</h1><CartPage /></Container><Footer /></main>;
}
