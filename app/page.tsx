import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import ProductCard from '@/components/ProductCard';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import { products } from '@/lib/data';
import Link from 'next/link';
import Button from '@/components/Button';
import Image from 'next/image';
import PromotionSection from '@/components/PromotionSection';
import Testimonials from '@/components/Testimonials';

export default function Home() {
  const featuredProducts = products.slice(0, 4);

  return (
    <main className="min-h-screen bg-background font-sans antialiased">
      <Navbar />

      <Hero />

      <section className="py-24">
        <Container>
          <div className="mb-12 flex items-end justify-between">
            <div>
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Signature Collection
              </h2>
              <p className="mt-4 text-muted-foreground">
                Commercial-ready coffee and equipment selected for consistent service.
              </p>
            </div>
            <Link href="/products" className="hidden sm:block">
              <Button variant="ghost">View Collection &rarr;</Button>
            </Link>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          <div className="mt-12 flex justify-center sm:hidden">
            <Link href="/products">
              <Button variant="outline">View All Products</Button>
            </Link>
          </div>
        </Container>
      </section>

      <section className="bg-secondary/30 py-24">
        <Container>
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            <div className="relative aspect-square overflow-hidden rounded-lg lg:aspect-auto lg:h-[600px]">
              <Image
                src="https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&q=80&w=1000"
                alt="Coffee brewing"
                fill
                className="object-cover"
              />
            </div>
            <div>
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
                <Link href="/contact">
                  <Button size="lg">Request a Tasting</Button>
                </Link>
              </div>
            </div>
          </div>
        </Container>
      </section>

      <Testimonials />

      <PromotionSection />

      <Footer />
    </main>
  );
}
