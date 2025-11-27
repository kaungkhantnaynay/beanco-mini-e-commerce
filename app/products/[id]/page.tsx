'use client';

import { useParams } from 'next/navigation';
import Image from 'next/image';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import CartDrawer from '@/components/CartDrawer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import { products } from '@/lib/data';
import { useCartStore } from '@/store/cartStore';
import { ShoppingCart } from 'lucide-react';

export default function ProductDetailPage() {
    const params = useParams();
    const id = params?.id as string;
    const product = products.find((p) => p.id === id);
    const addItem = useCartStore((state) => state.addItem);

    if (!product) {
        return (
            <main className="min-h-screen bg-background font-sans antialiased">
                <Navbar />
                <Container className="pt-32">
                    <h1 className="text-2xl font-bold">Product not found</h1>
                </Container>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />
            <CartDrawer />

            <div className="pt-32 pb-16">
                <Container>
                    <div className="grid gap-12 lg:grid-cols-2">
                        {/* Image */}
                        <div className="relative aspect-square overflow-hidden rounded-2xl bg-muted">
                            <Image
                                src={product.image}
                                alt={product.name}
                                fill
                                className="object-cover"
                            />
                        </div>

                        {/* Details */}
                        <div className="flex flex-col justify-center">
                            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                                {product.name}
                            </h1>
                            <p className="mt-4 text-2xl font-semibold text-primary">
                                ${product.price.toFixed(2)}
                            </p>
                            <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
                                {product.description}
                            </p>

                            <div className="mt-8 flex gap-4">
                                <Button size="lg" onClick={() => addItem(product)}>
                                    <ShoppingCart className="mr-2 h-5 w-5" />
                                    Add to Cart
                                </Button>
                            </div>

                            <div className="mt-12 border-t pt-8">
                                <h3 className="font-semibold text-foreground mb-4">Product Details</h3>
                                <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
                                    <li>Origin: Ethically sourced</li>
                                    <li>Roast Level: Medium-Dark</li>
                                    <li>Process: Washed</li>
                                    <li>Net Weight: 12oz (340g)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </Container>
            </div>

            <Footer />
        </main>
    );
}
