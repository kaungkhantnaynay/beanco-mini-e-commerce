'use client';

import { motion } from 'framer-motion';
import Button from './Button';
import Link from 'next/link';
import Container from './Container';

const Hero = () => {
    return (
        <section className="relative h-[90vh] w-full overflow-hidden">
            {/* Background Image */}
            <div
                className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1497935586351-b67a49e012bf?auto=format&fit=crop&q=80&w=2000')] bg-cover bg-center bg-no-repeat"
            >
                <div className="absolute inset-0 bg-black/40" />
            </div>

            <Container className="relative flex h-full items-center">
                <div className="max-w-2xl text-white">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="text-5xl font-bold leading-tight sm:text-6xl lg:text-7xl"
                    >
                        Experience the Art of Coffee
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="mt-6 text-lg text-gray-200 sm:text-xl"
                    >
                        Ethically sourced, expertly roasted, and delivered fresh to your door.
                        Discover your perfect brew today.
                    </motion.p>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.4 }}
                        className="mt-8 flex gap-4"
                    >
                        <Link href="/products">
                            <Button size="lg" className="bg-primary hover:bg-primary/90 text-white border-none">
                                Shop Now
                            </Button>
                        </Link>
                        <Link href="/about">
                            <Button size="lg" variant="outline" className="bg-transparent text-white border-white hover:bg-white hover:text-black">
                                Our Story
                            </Button>
                        </Link>
                    </motion.div>
                </div>
            </Container>
        </section>
    );
};

export default Hero;
