import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import ScrollReveal from '@/components/ScrollReveal';

export default function ContactPage() {
    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="pt-24 pb-12">
                <Container>
                    <div className="mx-auto max-w-5xl">
                        <ScrollReveal className="text-center mb-12">
                            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl mb-4">
                                Start a BeanCo Partnership
                            </h1>
                            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
                                Tell us about your venue, office, retail shelf, or event. Our team
                                will follow up with tasting notes, service options, and next steps.
                            </p>
                        </ScrollReveal>

                        <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
                            <ScrollReveal direction="right" className="rounded-lg border bg-card p-8 shadow-sm">
                                <form action="mailto:partnerships@beanco.example" method="post" encType="text/plain" className="space-y-6">
                                    <div className="grid gap-6 sm:grid-cols-2">
                                        <div className="space-y-2">
                                            <label htmlFor="name" className="text-sm font-medium leading-none">
                                                Name
                                            </label>
                                            <input
                                                type="text"
                                                id="name"
                                                name="name"
                                                required
                                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                                placeholder="Your name"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label htmlFor="email" className="text-sm font-medium leading-none">
                                                Email
                                            </label>
                                            <input
                                                type="email"
                                                id="email"
                                                name="email"
                                                required
                                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                                placeholder="you@company.com"
                                            />
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <label htmlFor="subject" className="text-sm font-medium leading-none">
                                            Inquiry Type
                                        </label>
                                        <input
                                            type="text"
                                            id="subject"
                                            name="subject"
                                            required
                                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                            placeholder="Wholesale, office coffee, event, retail, or tasting"
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <label htmlFor="message" className="text-sm font-medium leading-none">
                                            Project Details
                                        </label>
                                        <textarea
                                            id="message"
                                            name="message"
                                            required
                                            rows={5}
                                            className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y"
                                            placeholder="Tell us about volume, location, timeline, and what kind of coffee experience you want to create."
                                        />
                                    </div>

                                    <Button type="submit" className="w-full">
                                        Send Inquiry
                                    </Button>
                                </form>
                            </ScrollReveal>
                            <ScrollReveal direction="left" delay={0.08} className="rounded-lg border bg-secondary/30 p-8">
                                <h2 className="text-xl font-semibold">Commercial Support</h2>
                                <dl className="mt-6 space-y-5 text-sm">
                                    <div>
                                        <dt className="font-medium text-foreground">Response window</dt>
                                        <dd className="mt-1 text-muted-foreground">Within two business days</dd>
                                    </div>
                                    <div>
                                        <dt className="font-medium text-foreground">Best fit</dt>
                                        <dd className="mt-1 text-muted-foreground">Cafes, hotels, offices, retail shelves, and catered events</dd>
                                    </div>
                                    <div>
                                        <dt className="font-medium text-foreground">Email</dt>
                                        <dd className="mt-1 text-muted-foreground">partnerships@beanco.example</dd>
                                    </div>
                                </dl>
                            </ScrollReveal>
                        </div>
                    </div>
                </Container>
            </div>

            <Footer />
        </main>
    );
}
