'use client';

import Button from './Button';
import Link from 'next/link';
import Container from './Container';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';

const Hero = () => {
    const prefersReducedMotion = useReducedMotion();
    const { scrollYProgress } = useScroll();
    const backgroundY = useTransform(scrollYProgress, [0, 0.5], ['0%', '16%']);
    const contentY = useTransform(scrollYProgress, [0, 0.45], ['0%', '8%']);
    const backgroundScale = useTransform(scrollYProgress, [0, 0.5], [1, 1.08]);

    return (
        <section className="relative min-h-screen w-full overflow-hidden">
            <motion.div
                className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1497935586351-b67a49e012bf?auto=format&fit=crop&q=80&w=2000')] bg-cover bg-center bg-no-repeat"
                style={prefersReducedMotion ? undefined : { y: backgroundY, scale: backgroundScale }}
            >
                <div className="absolute inset-0 bg-black/35" />
            </motion.div>

            <Container className="relative flex min-h-screen items-center pb-14 pt-28">
                <motion.div
                    className="max-w-3xl text-white"
                    style={prefersReducedMotion ? undefined : { y: contentY }}
                    initial={prefersReducedMotion ? false : { opacity: 0, y: 36 }}
                    animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                >
                    <motion.p
                        className="mb-5 text-sm font-semibold uppercase tracking-[0.22em] text-white/75"
                        initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
                        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
                    >
                        Specialty coffee for modern hospitality
                    </motion.p>
                    <motion.h1
                        className="text-5xl font-bold leading-tight sm:text-6xl lg:text-7xl"
                        initial={prefersReducedMotion ? false : { opacity: 0, y: 22 }}
                        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.18, ease: [0.22, 1, 0.36, 1] }}
                    >
                        BeanCo
                    </motion.h1>
                    <motion.p
                        className="mt-6 max-w-2xl text-lg leading-8 text-white/85 sm:text-xl"
                        initial={prefersReducedMotion ? false : { opacity: 0, y: 22 }}
                        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.26, ease: [0.22, 1, 0.36, 1] }}
                    >
                        Direct-trade roasts, polished cafe supplies, and a brand experience built
                        for boutique hotels, offices, restaurants, and serious home brewers.
                    </motion.p>
                    <motion.div
                        className="mt-8 flex flex-col gap-3 sm:flex-row"
                        initial={prefersReducedMotion ? false : { opacity: 0, y: 22 }}
                        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.34, ease: [0.22, 1, 0.36, 1] }}
                    >
                        <Link href="/products">
                            <Button size="lg" className="bg-primary hover:bg-primary/90 text-white border-none">
                                Explore Collection
                            </Button>
                        </Link>
                        <Link href="/contact">
                            <Button size="lg" variant="outline" className="bg-transparent text-white border-white hover:bg-white hover:text-black">
                                Request Partnership
                            </Button>
                        </Link>
                    </motion.div>
                    <motion.div
                        className="mt-12 grid max-w-2xl grid-cols-3 gap-4 border-t border-white/25 pt-6 text-sm text-white/80"
                        initial={prefersReducedMotion ? false : { opacity: 0, y: 22 }}
                        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.44, ease: [0.22, 1, 0.36, 1] }}
                    >
                        <div><strong className="block text-2xl text-white">48h</strong> roast dispatch</div>
                        <div><strong className="block text-2xl text-white">12+</strong> origin partners</div>
                        <div><strong className="block text-2xl text-white">B2B</strong> tasting support</div>
                    </motion.div>
                </motion.div>
            </Container>
        </section>
    );
};

export default Hero;
