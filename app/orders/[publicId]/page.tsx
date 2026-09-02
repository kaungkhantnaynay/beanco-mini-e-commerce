import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import OrderStatus from "@/components/OrderStatus";

export default async function OrderPage({ params }: { params: Promise<{ publicId: string }> }) {
  const { publicId } = await params;
  return <main className="min-h-screen bg-background font-sans antialiased"><Navbar /><Container className="pb-20 pt-32"><OrderStatus publicId={publicId} /></Container><Footer /></main>;
}
