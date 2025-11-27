'use client';

import Link from 'next/link';
import { ShoppingBag, Menu, X, Coffee } from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Container from './Container';
import Button from './Button';
import { useCartStore } from '@/store/cartStore';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { items, toggleCart } = useCartStore();
    const { isAuthenticated, user } = useAuthStore();

    const cartCount = items.reduce((acc, item) => acc + item.quantity, 0);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 0);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { href: '/', label: 'Home' },
        { href: '/products', label: 'Shop' },
        { href: '/about', label: 'About' },
        { href: '/contact', label: 'Contact' },
    ];

    return (
        <header
            className={cn(
                'fixed top-0 z-50 w-full transition-all duration-300',
                isScrolled ? 'bg-background/80 backdrop-blur-md shadow-sm' : 'bg-transparent'
            )}
        >
            <Container>
                <div className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <Coffee className="h-8 w-8 text-primary" />
                        <span className="text-xl font-bold tracking-tight text-foreground">
                            BeanCo
                        </span>
                    </Link>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex items-center gap-8">
                        {navLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>

                    {/* Actions */}
                    <div className="flex items-center gap-4">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="relative"
                            onClick={toggleCart}
                        >
                            <ShoppingBag className="h-5 w-5" />
                            {cartCount > 0 && (
                                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                                    {cartCount}
                                </span>
                            )}
                        </Button>

                        {isAuthenticated ? (
                            <Link href="/profile">
                                <Button variant="ghost" size="sm" className="relative">
                                    <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary uppercase">
                                        {user?.name?.charAt(0) || 'U'}
                                    </div>
                                </Button>
                            </Link>
                        ) : (
                            <Link href="/login">
                                <Button variant="ghost" size="sm">
                                    Sign In
                                </Button>
                            </Link>
                        )}

                        {/* Mobile Menu Button */}
                        <Button
                            variant="ghost"
                            size="sm"
                            className="md:hidden"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        >
                            {isMobileMenuOpen ? (
                                <X className="h-5 w-5" />
                            ) : (
                                <Menu className="h-5 w-5" />
                            )}
                        </Button>
                    </div>
                </div>
            </Container>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden border-t bg-background"
                    >
                        <Container className="py-4">
                            <nav className="flex flex-col gap-4">
                                {navLinks.map((link) => (
                                    <Link
                                        key={link.href}
                                        href={link.href}
                                        className="text-sm font-medium text-foreground hover:text-primary"
                                        onClick={() => setIsMobileMenuOpen(false)}
                                    >
                                        {link.label}
                                    </Link>
                                ))}
                            </nav>
                        </Container>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
};

export default Navbar;
