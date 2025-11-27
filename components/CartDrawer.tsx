'use client';

import { X, Minus, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';
import { useCartStore } from '@/store/cartStore';
import Button from './Button';

const CartDrawer = () => {
    const { items, isOpen, toggleCart, removeItem, updateQuantity, total } = useCartStore();

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={toggleCart}
                        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
                    />

                    {/* Drawer */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
                        className="fixed right-0 top-0 z-50 h-full w-full max-w-md bg-background shadow-xl"
                    >
                        <div className="flex h-full flex-col">
                            <div className="flex items-center justify-between border-b p-4">
                                <h2 className="text-lg font-semibold">Shopping Cart</h2>
                                <Button variant="ghost" size="sm" onClick={toggleCart}>
                                    <X className="h-5 w-5" />
                                </Button>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4">
                                {items.length === 0 ? (
                                    <div className="flex h-full flex-col items-center justify-center text-center">
                                        <p className="text-muted-foreground">Your cart is empty</p>
                                        <Button variant="primary" className="mt-4" onClick={toggleCart}>
                                            Continue Shopping
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {items.map((item) => (
                                            <div key={item.id} className="flex gap-4">
                                                <div className="relative h-20 w-20 overflow-hidden rounded-md border bg-muted">
                                                    <Image
                                                        src={item.image}
                                                        alt={item.name}
                                                        fill
                                                        className="object-cover"
                                                    />
                                                </div>
                                                <div className="flex flex-1 flex-col justify-between">
                                                    <div className="flex justify-between">
                                                        <h3 className="font-medium">{item.name}</h3>
                                                        <p className="font-semibold">${(item.price * item.quantity).toFixed(2)}</p>
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
                                                        </Button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {items.length > 0 && (
                                <div className="border-t p-4">
                                    <div className="mb-4 flex items-center justify-between text-lg font-semibold">
                                        <span>Total</span>
                                        <span>${total().toFixed(2)}</span>
                                    </div>
                                    <Link href="/checkout" onClick={toggleCart}>
                                        <Button className="w-full" size="lg">
                                            Checkout
                                        </Button>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default CartDrawer;
