import Image from 'next/image';
import Link from 'next/link';
import ButtonLink from './ButtonLink';
import type { ProductSummary } from '@/lib/types/api';
import { formatTHB } from '@/lib/format';
import ScrollReveal from './ScrollReveal';

interface ProductCardProps {
    product: ProductSummary;
    index?: number;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, index = 0 }) => {
    return (
        <ScrollReveal delay={Math.min(index * 0.06, 0.24)} className="h-full">
            <article className="product-card group h-full overflow-hidden rounded-lg border bg-card shadow-sm">
                <Link href={`/products/${product.slug}`} className="block aspect-[4/5] overflow-hidden bg-muted">
                    {product.primary_image ? (
                        <Image
                            src={product.primary_image.url}
                            alt={product.primary_image.alt_text}
                            width={500}
                            height={625}
                            loading={index === 0 ? 'eager' : 'lazy'}
                            className="product-card-image h-full w-full object-cover"
                        />
                    ) : (
                        <div className="flex h-full items-center justify-center px-6 text-center text-sm text-muted-foreground">
                            Image coming soon
                        </div>
                    )}
                </Link>
                <div className="p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                        {product.profile}
                    </p>
                    <h3 className="mt-3 text-lg font-semibold text-card-foreground">
                        <Link href={`/products/${product.slug}`}>{product.name}</Link>
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                        {product.description}
                    </p>
                    <div className="mt-5 flex items-center justify-between gap-3">
                        <span className="text-lg font-bold text-primary">
                            From {formatTHB(product.starting_price)}
                        </span>
                        <ButtonLink href={`/products/${product.slug}`} size="sm" variant="outline">View</ButtonLink>
                    </div>
                </div>
            </article>
        </ScrollReveal>
    );
};

export default ProductCard;
