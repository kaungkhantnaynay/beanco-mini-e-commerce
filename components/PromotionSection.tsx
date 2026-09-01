import ButtonLink from './ButtonLink';
import Container from './Container';
import ScrollReveal from './ScrollReveal';

const PromotionSection = () => {
    return (
        <section className="bg-primary py-24 text-primary-foreground">
            <Container>
                <ScrollReveal className="mx-auto max-w-3xl text-center">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
                        Bring BeanCo to Your Space
                    </h2>
                    <p className="text-lg mb-8 text-primary-foreground/90">
                        Build a coffee program with polished packaging, dependable roast profiles,
                        and tasting support for your team.
                    </p>
                    <ButtonLink href="/contact" size="lg" variant="secondary" className="font-semibold">
                        Start a Conversation
                    </ButtonLink>
                    <p className="mt-4 text-sm text-primary-foreground/70">
                        Wholesale, office, retail, and hospitality inquiries welcome.
                    </p>
                </ScrollReveal>
            </Container>
        </section>
    );
};

export default PromotionSection;
