import CheckoutFlow from "@/components/CheckoutFlow";
import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function CheckoutPage() {
  return <main className="min-h-screen bg-background font-sans antialiased"><Navbar /><Container className="pb-20 pt-32"><h1 className="mb-8 text-4xl font-bold tracking-tight">Checkout</h1><CheckoutFlow /></Container><Footer /></main>;
}
