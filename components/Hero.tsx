import Button from './Button';
import Link from 'next/link';
import Container from './Container';

const Hero = () => {
    return (
        <section className="relative min-h-screen w-full overflow-hidden">
            <div
                className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1497935586351-b67a49e012bf?auto=format&fit=crop&q=80&w=2000')] bg-cover bg-center bg-no-repeat"
            >
                <div className="absolute inset-0 bg-black/35" />
            </div>

            <Container className="relative flex min-h-screen items-center pb-14 pt-28">
                <div className="max-w-3xl text-white">
                    <p className="mb-5 text-sm font-semibold uppercase tracking-[0.22em] text-white/75">
                        Specialty coffee for modern hospitality
                    </p>
                    <h1 className="text-5xl font-bold leading-tight sm:text-6xl lg:text-7xl">
                        BeanCo
                    </h1>
                    <p className="mt-6 max-w-2xl text-lg leading-8 text-white/85 sm:text-xl">
                        Direct-trade roasts, polished cafe supplies, and a brand experience built
                        for boutique hotels, offices, restaurants, and serious home brewers.
                    </p>
                    <div className="mt-8 flex flex-col gap-3 sm:flex-row">
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
                    </div>
                    <div className="mt-12 grid max-w-2xl grid-cols-3 gap-4 border-t border-white/25 pt-6 text-sm text-white/80">
                        <div><strong className="block text-2xl text-white">48h</strong> roast dispatch</div>
                        <div><strong className="block text-2xl text-white">12+</strong> origin partners</div>
                        <div><strong className="block text-2xl text-white">B2B</strong> tasting support</div>
                    </div>
                </div>
            </Container>
        </section>
    );
};

export default Hero;
