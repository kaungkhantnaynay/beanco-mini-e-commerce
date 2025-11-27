'use client';

import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import { useCartStore } from '@/store/cartStore';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { CreditCard, Wallet, Banknote } from 'lucide-react';

export default function CheckoutPage() {
    const { items, total, clearCart } = useCartStore();
    const router = useRouter();
    const [isProcessing, setIsProcessing] = useState(false);
    const [paymentMethod, setPaymentMethod] = useState('card');
    const [isSuccess, setIsSuccess] = useState(false);

    useEffect(() => {
        if (items.length === 0 && !isSuccess) {
            router.push('/cart');
        }
    }, [items, router, isSuccess]);

    const handlePayment = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsProcessing(true);

        await new Promise(resolve => setTimeout(resolve, 2000));

        setIsProcessing(false);
        setIsSuccess(true);
        clearCart();

        setTimeout(() => {
            router.push('/profile');
        }, 3000);
    };

    if (items.length === 0 && !isSuccess) return null;

    if (isSuccess) {
        return (
            <main className="min-h-screen bg-background font-sans antialiased">
                <Navbar />
                <div className="flex min-h-[80vh] items-center justify-center pt-24 pb-12">
                    <Container className="max-w-md text-center">
                        <div className="rounded-full bg-green-100 p-6 inline-flex mb-6">
                            <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h1 className="text-3xl font-bold mb-4">Payment Successful!</h1>
                        <p className="text-muted-foreground mb-8">
                            Thank you for your purchase. Your order has been confirmed.
                            Redirecting you to your profile...
                        </p>
                    </Container>
                </div>
                <Footer />
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="pt-32 pb-16">
                <Container>
                    <h1 className="text-3xl font-bold mb-8">Checkout</h1>

                    <div className="grid gap-8 lg:grid-cols-12">
                        {/* Payment Form */}
                        <div className="lg:col-span-8">
                            <div className="rounded-lg border bg-card p-6">
                                <h2 className="text-xl font-semibold mb-6">Payment Method</h2>

                                <div className="grid grid-cols-3 gap-4 mb-8">
                                    <button
                                        type="button"
                                        onClick={() => setPaymentMethod('card')}
                                        className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${paymentMethod === 'card'
                                                ? 'border-primary bg-primary/5 text-primary'
                                                : 'border-muted hover:border-primary/50'
                                            }`}
                                    >
                                        <CreditCard className="h-6 w-6 mb-2" />
                                        <span className="text-sm font-medium">Card</span>
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setPaymentMethod('paypal')}
                                        className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${paymentMethod === 'paypal'
                                                ? 'border-primary bg-primary/5 text-primary'
                                                : 'border-muted hover:border-primary/50'
                                            }`}
                                    >
                                        <Wallet className="h-6 w-6 mb-2" />
                                        <span className="text-sm font-medium">PayPal</span>
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setPaymentMethod('apple')}
                                        className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all ${paymentMethod === 'apple'
                                                ? 'border-primary bg-primary/5 text-primary'
                                                : 'border-muted hover:border-primary/50'
                                            }`}
                                    >
                                        <Banknote className="h-6 w-6 mb-2" />
                                        <span className="text-sm font-medium">Apple Pay</span>
                                    </button>
                                </div>

                                <form onSubmit={handlePayment} className="space-y-4">
                                    {paymentMethod === 'card' && (
                                        <>
                                            <div>
                                                <label className="block text-sm font-medium mb-1">Card Number</label>
                                                <input
                                                    type="text"
                                                    required
                                                    placeholder="0000 0000 0000 0000"
                                                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                />
                                            </div>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-sm font-medium mb-1">Expiry Date</label>
                                                    <input
                                                        type="text"
                                                        required
                                                        placeholder="MM/YY"
                                                        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium mb-1">CVC</label>
                                                    <input
                                                        type="text"
                                                        required
                                                        placeholder="123"
                                                        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-1">Name on Card</label>
                                                <input
                                                    type="text"
                                                    required
                                                    placeholder="John Doe"
                                                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                />
                                            </div>
                                        </>
                                    )}

                                    {(paymentMethod === 'paypal' || paymentMethod === 'apple') && (
                                        <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                                            You will be redirected to {paymentMethod === 'paypal' ? 'PayPal' : 'Apple Pay'} to complete your purchase securely.
                                        </div>
                                    )}

                                    <Button
                                        type="submit"
                                        className="w-full mt-6"
                                        size="lg"
                                        disabled={isProcessing}
                                    >
                                        {isProcessing ? 'Processing...' : `Pay $${total().toFixed(2)}`}
                                    </Button>
                                </form>
                            </div>
                        </div>

                        {/* Order Summary */}
                        <div className="lg:col-span-4">
                            <div className="rounded-lg border bg-card p-6 sticky top-24">
                                <h2 className="text-lg font-semibold mb-4">Order Summary</h2>
                                <div className="space-y-4 mb-6">
                                    {items.map((item) => (
                                        <div key={item.id} className="flex justify-between text-sm">
                                            <span className="text-muted-foreground">
                                                {item.quantity}x {item.name}
                                            </span>
                                            <span>${(item.price * item.quantity).toFixed(2)}</span>
                                        </div>
                                    ))}
                                </div>
                                <div className="border-t pt-4 space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Subtotal</span>
                                        <span>${total().toFixed(2)}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Shipping</span>
                                        <span>Free</span>
                                    </div>
                                    <div className="flex justify-between font-bold text-lg pt-2">
                                        <span>Total</span>
                                        <span>${total().toFixed(2)}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </Container>
            </div>

            <Footer />
        </main>
    );
}
