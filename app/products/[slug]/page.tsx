import Image from "next/image";
import { notFound } from "next/navigation";
import { MessageSquare } from "lucide-react";
import ButtonLink from "@/components/ButtonLink";
import { CatalogState } from "@/components/CatalogState";
import Container from "@/components/Container";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import ProductPurchase from "@/components/ProductPurchase";
import { getProduct } from "@/lib/api/catalog";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { ProductDetail } from "@/lib/types/api";

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  let product: ProductDetail | null = null;
  let error = "";

  try {
    product = await getProduct(slug);
  } catch (caught) {
    if (caught instanceof ApiRequestError && caught.status === 404) notFound();
    error = caught instanceof Error ? caught.message : "This product could not be loaded.";
  }

  if (!product) {
    return (
      <main className="min-h-screen bg-background font-sans antialiased">
        <Navbar />
        <Container className="pb-20 pt-32">
          <CatalogState title="We could not load this product" detail={error} retryHref={`/products/${slug}`} />
        </Container>
        <Footer />
      </main>
    );
  }

  const image = product.primary_image ?? product.images[0] ?? null;

  return (
    <main className="min-h-screen bg-background font-sans antialiased">
      <Navbar />
      <div className="pb-16 pt-32">
        <Container>
          <div className="grid gap-12 lg:grid-cols-2">
            <div className="relative aspect-square overflow-hidden rounded-2xl bg-muted">
              {image ? (
                <Image
                  src={image.url}
                  alt={image.alt_text}
                  fill
                  sizes="(min-width: 1024px) 50vw, 100vw"
                  className="object-cover"
                  priority
                />
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">Image coming soon</div>
              )}
            </div>

            <div className="flex flex-col justify-center">
              <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                {product.profile || product.category.name}
              </p>
              <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                {product.name}
              </h1>
              <p className="mt-4 text-2xl font-semibold text-primary">
                Program pricing from {formatTHB(product.starting_price)}
              </p>
              <p className="mt-6 text-lg leading-relaxed text-muted-foreground">{product.description}</p>
              <p className="mt-4 text-sm font-medium text-muted-foreground">
                {product.available
                  ? "Available for current programs"
                  : "Currently unavailable — ask about future availability"}
              </p>

              <div className="mt-8">
                <ProductPurchase productName={product.name} variants={product.variants} />
              </div>

              <div className="mt-5 flex gap-4">
                <ButtonLink href="/contact" size="lg">
                  <MessageSquare className="mr-2 h-5 w-5" aria-hidden="true" />
                  Request Details
                </ButtonLink>
              </div>

              <div className="mt-10 border-t pt-8">
                <h2 className="mb-4 font-semibold text-foreground">Available options</h2>
                <ul className="space-y-3 text-sm text-muted-foreground">
                  {product.variants.map((variant) => (
                    <li key={variant.sku} className="flex items-center justify-between gap-4 rounded-md border px-4 py-3">
                      <span>{variant.option_name || variant.sku}</span>
                      <span className="font-medium text-foreground">{formatTHB(variant.price)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </Container>
      </div>
      <Footer />
    </main>
  );
}
