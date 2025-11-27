import Link from 'next/link';
import Button from './Button';
import Container from './Container';

const PromotionSection = () => {
    return (
        <section className="bg-primary py-24 text-primary-foreground">
            <Container>
                <div className="mx-auto max-w-3xl text-center">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
                        Join the BeanCo Family
                    </h2>
                    <p className="text-lg mb-8 text-primary-foreground/90">
                        Sign up today and get <span className="font-bold">15% off</span> your first order of premium coffee beans.
                        Experience the difference of ethically sourced, expertly roasted coffee.
                    </p>
                    <Link href="/register">
                        <Button
                            size="lg"
                            variant="secondary"
                            className="font-semibold"
                        >
                            Sign Up Now
                        </Button>
                    </Link>
                    <p className="mt-4 text-sm text-primary-foreground/70">
                        *Discount applied automatically at checkout for new accounts.
                    </p>
                </div>
            </Container>
        </section>
    );
};

export default PromotionSection;
