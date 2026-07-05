import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Image from 'next/image';

export default function AboutPage() {
    const team = [
        {
            name: 'Sarah Lee',
            role: 'Head Roaster',
            image: '/images/user-1.png',
            bio: 'Sarah brings over 15 years of roasting experience, ensuring every batch is roasted to perfection.'
        },
        {
            name: 'David Kim',
            role: 'Sourcing Manager',
            image: '/images/user-2.png',
            bio: 'David travels the world to find the most unique and sustainable coffee beans for our customers.'
        },
        {
            name: 'Elena Rivera',
            role: 'Head Barista',
            image: '/images/user-3.png',
            bio: 'Elena is an award-winning barista who trains our team and develops our signature brewing recipes.'
        }
    ];

    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="pt-24 pb-12">
                <Container>
                    {/* Hero Section */}
                    <div className="grid gap-12 lg:grid-cols-2 lg:items-center mb-24">
                        <div>
                            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl mb-6">
                                About BeanCo
                            </h1>
                            <div className="prose prose-lg text-muted-foreground">
                                <p className="mb-4">
                                    Welcome to BeanCo, where passion for coffee meets exceptional quality.
                                    We started with a simple mission: to bring the world&apos;s finest, ethically sourced
                                    coffee beans directly to your doorstep.
                                </p>
                                <p className="mb-4">
                                    Our journey began in a small roastery, fueled by a love for the craft and a
                                    dedication to sustainability. We work closely with farmers across the globe
                                    to ensure that every bean we roast tells a story of hard work, tradition,
                                    and excellence.
                                </p>
                                <p>
                                    Today, we help cafes, hotels, offices, and retail partners present coffee
                                    with the same care they bring to their own brands.
                                </p>
                            </div>
                        </div>
                        <div className="relative aspect-square overflow-hidden rounded-2xl bg-muted">
                            <Image
                                src="/images/espresso-blend.png"
                                alt="About BeanCo"
                                fill
                                className="object-cover"
                            />
                        </div>
                    </div>

                    {/* Our History Section */}
                    <div className="mb-24">
                        <h2 className="text-3xl font-bold tracking-tight text-foreground mb-8 text-center">
                            Our History
                        </h2>
                        <div className="max-w-3xl mx-auto space-y-8">
                            <div className="flex gap-4">
                                <div className="flex-none w-24 font-bold text-primary text-right pt-1">2010</div>
                                <div className="flex-1 border-l-2 border-muted pl-8 pb-8 relative">
                                    <div className="absolute -left-[9px] top-2 h-4 w-4 rounded-full bg-primary" />
                                    <h3 className="text-xl font-semibold mb-2">The Beginning</h3>
                                    <p className="text-muted-foreground">
                                        BeanCo was founded in a small garage with a 1kg roaster and a big dream.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex-none w-24 font-bold text-primary text-right pt-1">2015</div>
                                <div className="flex-1 border-l-2 border-muted pl-8 pb-8 relative">
                                    <div className="absolute -left-[9px] top-2 h-4 w-4 rounded-full bg-primary" />
                                    <h3 className="text-xl font-semibold mb-2">First Cafe</h3>
                                    <p className="text-muted-foreground">
                                        We opened our flagship cafe downtown, serving our signature blends to the community.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex-none w-24 font-bold text-primary text-right pt-1">2020</div>
                                <div className="flex-1 border-l-2 border-muted pl-8 pb-8 relative">
                                    <div className="absolute -left-[9px] top-2 h-4 w-4 rounded-full bg-primary" />
                                    <h3 className="text-xl font-semibold mb-2">Going Digital</h3>
                                    <p className="text-muted-foreground">
                                        Launched our online store to share our coffee with lovers worldwide.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex-none w-24 font-bold text-primary text-right pt-1">2023</div>
                                <div className="flex-1 border-l-2 border-muted pl-8 relative">
                                    <div className="absolute -left-[9px] top-2 h-4 w-4 rounded-full bg-primary" />
                                    <h3 className="text-xl font-semibold mb-2">Sustainability Award</h3>
                                    <p className="text-muted-foreground">
                                        Recognized for our commitment to ethical sourcing and eco-friendly practices.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h2 className="text-3xl font-bold tracking-tight text-foreground mb-12 text-center">
                            Roastery Leadership
                        </h2>
                        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                            {team.map((member) => (
                                <div key={member.name} className="group relative overflow-hidden rounded-2xl bg-card border shadow-sm transition-all hover:shadow-md">
                                    <div className="relative h-48 w-48 mx-auto mt-6 overflow-hidden rounded-full bg-muted">
                                        <Image
                                            src={member.image}
                                            alt={member.name}
                                            fill
                                            className="object-cover transition-transform duration-300 group-hover:scale-105"
                                        />
                                    </div>
                                    <div className="p-6">
                                        <h3 className="text-xl font-bold">{member.name}</h3>
                                        <p className="text-sm text-primary font-medium mb-4">{member.role}</p>
                                        <p className="text-muted-foreground text-sm">
                                            {member.bio}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                </Container>
            </div>

            <Footer />
        </main>
    );
}
