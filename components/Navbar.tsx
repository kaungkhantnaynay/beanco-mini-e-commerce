'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Coffee, ShoppingBag } from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import Container from './Container';
import Button from './Button';
import ButtonLink from './ButtonLink';
import { cn } from '@/lib/utils';

const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const pathname = usePathname();
    const prefersReducedMotion = useReducedMotion();
    const isHeroMode = pathname === '/' && !isScrolled;

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 0);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { href: '/', label: 'Home' },
        { href: '/products', label: 'Collection' },
        { href: '/about', label: 'About' },
        { href: '/contact', label: 'Contact' },
    ];

    return (
        <header
            className={cn(
                'fixed top-0 z-50 w-full transition-[background-color,box-shadow] duration-200',
                isHeroMode ? 'bg-transparent' : 'bg-background/90 backdrop-blur-md shadow-sm'
            )}
        >
            <Container>
                <div className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <Coffee aria-hidden="true" className={cn('h-8 w-8', isHeroMode ? 'text-white' : 'text-primary')} />
                        <span className={cn('text-xl font-bold tracking-tight', isHeroMode ? 'text-white' : 'text-foreground')}>
                            BeanCo
                        </span>
                    </Link>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex items-center gap-8">
                        {navLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                aria-current={pathname === link.href || (link.href === '/products' && pathname.startsWith('/products/')) ? 'page' : undefined}
                                className={cn(
                                    'text-sm font-medium transition-colors',
                                    isHeroMode ? 'text-white/80 hover:text-white' : 'text-muted-foreground hover:text-primary'
                                )}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>

                    {/* Actions */}
                    <div className="flex items-center gap-3">
                        <ButtonLink
                            href="/cart"
                            variant="ghost"
                            size="sm"
                            aria-label="View cart"
                            aria-current={pathname === '/cart' ? 'page' : undefined}
                            className={cn(isHeroMode ? 'text-white hover:bg-white/10 hover:text-white' : '')}
                        >
                            <ShoppingBag className="h-5 w-5" aria-hidden="true" />
                            <span className="ml-2 hidden lg:inline">Cart</span>
                        </ButtonLink>
                        <ButtonLink href="/contact" size="sm" className="hidden sm:inline-flex">
                            Partner With Us
                        </ButtonLink>

                        <Button
                            variant="ghost"
                            size="sm"
                            className="md:hidden"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            aria-label={isMobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
                            aria-expanded={isMobileMenuOpen}
                            aria-controls="mobile-navigation"
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
                        id="mobile-navigation"
                        initial={prefersReducedMotion ? false : { opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }}
                        transition={{ duration: prefersReducedMotion ? 0 : 0.18, ease: [0.23, 1, 0.32, 1] }}
                        className="md:hidden border-t bg-background"
                    >
                        <Container className="py-4">
                            <nav className="flex flex-col gap-4">
                                {navLinks.map((link) => (
                                    <Link
                                        key={link.href}
                                        href={link.href}
                                        aria-current={pathname === link.href || (link.href === '/products' && pathname.startsWith('/products/')) ? 'page' : undefined}
                                        className="text-sm font-medium text-foreground hover:text-primary"
                                        onClick={() => setIsMobileMenuOpen(false)}
                                    >
                                        {link.label}
                                    </Link>
                                ))}
                                <ButtonLink href="/contact" className="w-full" onClick={() => setIsMobileMenuOpen(false)}>
                                    Partner With Us
                                </ButtonLink>
                            </nav>
                        </Container>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
};

export default Navbar;
