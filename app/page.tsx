import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import ProductCard from '@/components/ProductCard';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import ButtonLink from '@/components/ButtonLink';
import Image from 'next/image';
import PromotionSection from '@/components/PromotionSection';
import Testimonials from '@/components/Testimonials';
import ScrollReveal from '@/components/ScrollReveal';
import { getProducts } from '@/lib/api/catalog';
import { CatalogState } from '@/components/CatalogState';
import type { ProductSummary } from '@/lib/types/api';

export default async function Home() {
  let featuredProducts: ProductSummary[] = [];
  let catalogError = '';

  try {
    const catalog = await getProducts({ featured: true, page_size: 4 });
    featuredProducts = catalog.results;
  } catch (error) {
    catalogError = error instanceof Error ? error.message : 'The catalog is temporarily unavailable.';
  }

  return (
    <main className="min-h-screen bg-background font-sans antialiased">
      <Navbar />

      <Hero />

      <section className="py-24">
        <Container>
          <ScrollReveal className="mb-12 flex items-end justify-between">
            <div>
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Signature Collection
              </h2>
              <p className="mt-4 text-muted-foreground">
                Commercial-ready coffee and equipment selected for consistent service.
              </p>
            </div>
            <ButtonLink href="/products" variant="ghost" className="hidden sm:inline-flex">
              View Collection &rarr;
            </ButtonLink>
          </ScrollReveal>

          {catalogError ? (
            <CatalogState
              title="The signature collection is temporarily unavailable"
              detail={catalogError}
              retryHref="/"
            />
          ) : featuredProducts.length ? (
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {featuredProducts.map((product, index) => (
                <ProductCard key={product.slug} product={product} index={index} />
              ))}
            </div>
          ) : (
            <CatalogState
              title="New coffees are on the way"
              detail="There are no featured products right now. Browse the full collection or check back soon."
            />
          )}

          <div className="mt-12 flex justify-center sm:hidden">
            <ButtonLink href="/products" variant="outline">View All Products</ButtonLink>
          </div>
        </Container>
      </section>

      <section className="bg-secondary/30 py-24">
        <Container>
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            <ScrollReveal direction="right" className="relative aspect-square overflow-hidden rounded-lg lg:aspect-auto lg:h-[600px]">
              <Image
                src="https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&q=80&w=1000"
                alt="Coffee brewing"
                fill
                sizes="(min-width: 1024px) 50vw, 100vw"
                className="object-cover"
              />
            </ScrollReveal>
            <ScrollReveal direction="left" delay={0.08}>
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Built for Repeatable Quality
              </h2>
              <p className="mt-6 text-lg text-muted-foreground">
                BeanCo presents a polished coffee program for venues that need reliable
                flavor, clean packaging, and a supplier that understands daily service.
              </p>
              <p className="mt-4 text-lg text-muted-foreground">
                From origin selection to brew support, every touchpoint is designed to
                help your brand serve better coffee without adding operational friction.
              </p>
              <div className="mt-8">
                <ButtonLink href="/contact" size="lg">Request a Tasting</ButtonLink>
              </div>
            </ScrollReveal>
          </div>
        </Container>
      </section>

      <Testimonials />

      <PromotionSection />

      <Footer />
    </main>
  );
}
