'use client';

import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import { useCartStore } from '@/store/cartStore';
import Image from 'next/image';
import Link from 'next/link';
import { Minus, Plus, Trash2 } from 'lucide-react';

export default function CartPage() {
    const { items, removeItem, updateQuantity, total } = useCartStore();

    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="pt-32 pb-16">
                <Container>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl mb-8">
                        Shopping Cart
                    </h1>

                    {items.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-card">
                            <p className="text-lg text-muted-foreground mb-4">Your cart is empty</p>
                            <Link href="/products">
                                <Button>Continue Shopping</Button>
                            </Link>
                        </div>
                    ) : (
                        <div className="grid gap-8 lg:grid-cols-12">
                            <div className="lg:col-span-8">
                                <div className="space-y-4">
                                    {items.map((item) => (
                                        <div key={item.id} className="flex gap-4 border rounded-lg p-4 bg-card">
                                            <div className="relative h-24 w-24 overflow-hidden rounded-md border bg-muted">
                                                <Image
                                                    src={item.image}
                                                    alt={item.name}
                                                    fill
                                                    className="object-cover"
                                                />
                                            </div>
                                            <div className="flex flex-1 flex-col justify-between">
                                                <div className="flex justify-between">
                                                    <h3 className="font-medium text-lg">{item.name}</h3>
                                                    <p className="font-semibold text-lg">${(item.price * item.quantity).toFixed(2)}</p>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            variant="outline"
                                                            size="sm"
                                                            className="h-8 w-8 p-0"
                                                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                                        >
                                                            <Minus className="h-3 w-3" />
                                                        </Button>
                                                        <span className="w-8 text-center text-sm">{item.quantity}</span>
                                                        <Button
                                                            variant="outline"
                                                            size="sm"
                                                            className="h-8 w-8 p-0"
                                                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                                        >
                                                            <Plus className="h-3 w-3" />
                                                        </Button>
                                                    </div>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="text-destructive hover:text-destructive"
                                                        onClick={() => removeItem(item.id)}
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                        <span className="ml-2 hidden sm:inline">Remove</span>
                                                    </Button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="lg:col-span-4">
                                <div className="rounded-lg border bg-card p-6">
                                    <h2 className="text-lg font-semibold mb-4">Order Summary</h2>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Subtotal</span>
                                            <span>${total().toFixed(2)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Shipping</span>
                                            <span>Free</span>
                                        </div>
                                        <div className="border-t pt-2 mt-2 flex justify-between font-semibold text-lg">
                                            <span>Total</span>
                                            <span>${total().toFixed(2)}</span>
                                        </div>
                                    </div>
                                    <Link href="/checkout">
                                        <Button className="w-full mt-6" size="lg">
                                            Proceed to Checkout
                                        </Button>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    )}
                </Container>
            </div>

            <Footer />
        </main>
    );
}
