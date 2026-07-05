import Navbar from '@/components/Navbar';
import ProductCard from '@/components/ProductCard';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import { products } from '@/lib/data';

export default function ProductsPage() {
    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="pt-24 pb-12">
                <Container>
                    <div className="mb-12">
                        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                            Coffee Collection
                        </h1>
                        <p className="mt-4 text-lg text-muted-foreground">
                            Review the roasts, brew tools, and service-ready essentials behind the BeanCo program.
                        </p>
                    </div>

                    <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
                        {products.map((product) => (
                            <ProductCard key={product.id} product={product} />
                        ))}
                    </div>
                </Container>
            </div>

            <Footer />
        </main>
    );
}
