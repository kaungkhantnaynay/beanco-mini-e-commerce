import Image from 'next/image';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import { products } from '@/lib/data';
import { formatTHB } from '@/lib/format';
import { MessageSquare } from 'lucide-react';

interface ProductDetailPageProps {
    params: Promise<{ id: string }>;
}

export function generateStaticParams() {
    return products.map((product) => ({ id: product.id }));
}

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
    const { id } = await params;
    const product = products.find((p) => p.id === id);

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
                            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                                {product.profile}
                            </p>
                            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                                {product.name}
                            </h1>
                            <p className="mt-4 text-2xl font-semibold text-primary">
                                Program pricing from {formatTHB(product.price)}
                            </p>
                            <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
                                {product.description}
                            </p>

                            <div className="mt-8 flex gap-4">
                                <Link href="/contact">
                                    <Button size="lg">
                                        <MessageSquare className="mr-2 h-5 w-5" />
                                        Request Details
                                    </Button>
                                </Link>
                            </div>

                            <div className="mt-12 border-t pt-8">
                                <h3 className="font-semibold text-foreground mb-4">Service Notes</h3>
                                <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
                                    <li>Available for tasting sessions and hospitality sampling</li>
                                    <li>Prepared for retail shelves, office bars, and cafe service</li>
                                    <li>Fresh-roasted dispatch schedule for partner accounts</li>
                                    <li>Training notes and brew guidance available on request</li>
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
