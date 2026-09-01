import ContactForm from "@/components/ContactForm";
import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import ScrollReveal from "@/components/ScrollReveal";

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-background font-sans antialiased">
      <Navbar />
      <div className="pb-12 pt-24">
        <Container>
          <div className="mx-auto max-w-5xl">
            <ScrollReveal className="mb-12 text-center">
              <h1 className="mb-4 text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                Start a BeanCo Partnership
              </h1>
              <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
                Tell us about your venue, office, retail shelf, or event. Our team will follow up
                with tasting notes, service options, and next steps.
              </p>
            </ScrollReveal>

            <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
              <ScrollReveal direction="right" className="rounded-lg border bg-card p-6 shadow-sm sm:p-8">
                <ContactForm />
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
                    <dd className="mt-1 text-muted-foreground">
                      Cafes, hotels, offices, retail shelves, and catered events
                    </dd>
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
