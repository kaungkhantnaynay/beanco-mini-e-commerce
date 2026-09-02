import Link from 'next/link';
import { Coffee, Facebook, Instagram, Twitter } from 'lucide-react';
import Container from './Container';
import NewsletterForm from './NewsletterForm';

const Footer = () => {
    return (
        <footer className="bg-secondary/30 pt-16 pb-8">
            <Container>
                <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
                    <div>
                        <Link href="/" className="flex items-center gap-2 mb-4">
                            <Coffee className="h-6 w-6 text-primary" />
                            <span className="text-lg font-bold text-foreground">BeanCo</span>
                        </Link>
                        <p className="text-sm text-muted-foreground">
                            Crafting the perfect cup, one bean at a time. Experience the finest
                            coffee from around the world.
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-foreground mb-4">Collection</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><Link href="/products" className="hover:text-primary">Coffee Program</Link></li>
                            <li><Link href="/products?type=coffee" className="hover:text-primary">Coffee</Link></li>
                            <li><Link href="/products?availability=true" className="hover:text-primary">Available Now</Link></li>
                            <li><Link href="/products?type=equipment" className="hover:text-primary">Brew Equipment</Link></li>
                            <li><Link href="/cart" className="hover:text-primary">Cart</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-semibold text-foreground mb-4">Company</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><Link href="/about" className="hover:text-primary">About Us</Link></li>
                            <li><Link href="/contact" className="hover:text-primary">Contact</Link></li>
                            <li><Link href="/products" className="hover:text-primary">Collection</Link></li>
                            <li><Link href="/contact" className="hover:text-primary">Partnerships</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-semibold text-foreground mb-4">Connect</h4>
                        <div className="flex gap-4 text-muted-foreground">
                            <a href="#" aria-label="BeanCo on Instagram" className="hover:text-primary"><Instagram className="h-5 w-5" aria-hidden="true" /></a>
                            <a href="#" aria-label="BeanCo on Facebook" className="hover:text-primary"><Facebook className="h-5 w-5" aria-hidden="true" /></a>
                            <a href="#" aria-label="BeanCo on X" className="hover:text-primary"><Twitter className="h-5 w-5" aria-hidden="true" /></a>
                        </div>
                        <div className="mt-4">
                            <h5 className="text-sm font-medium mb-2">Newsletter</h5>
                            <NewsletterForm />
                        </div>
                    </div>
                </div>
                <div className="mt-16 border-t border-border pt-8 text-center text-sm text-muted-foreground">
                    © {new Date().getFullYear()} BeanCo. All rights reserved.
                </div>
            </Container>
        </footer>
    );
};

export default Footer;
