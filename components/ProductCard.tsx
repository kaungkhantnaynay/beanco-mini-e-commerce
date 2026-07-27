import Image from 'next/image';
import Link from 'next/link';
import Button from './Button';
import { Product } from '@/lib/data';
import { formatTHB } from '@/lib/format';
import ScrollReveal from './ScrollReveal';

interface ProductCardProps {
    product: Product;
    index?: number;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, index = 0 }) => {
    return (
        <ScrollReveal delay={Math.min(index * 0.06, 0.24)} className="h-full">
            <article className="group h-full overflow-hidden rounded-lg border bg-card shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                <Link href={`/products/${product.id}`} className="block aspect-[4/5] overflow-hidden bg-muted">
                    <Image
                        src={product.image}
                        alt={product.name}
                        width={500}
                        height={500}
                        className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                </Link>
                <div className="p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                        {product.profile}
                    </p>
                    <h3 className="mt-3 text-lg font-semibold text-card-foreground">
                        <Link href={`/products/${product.id}`}>{product.name}</Link>
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                        {product.description}
                    </p>
                    <div className="mt-5 flex items-center justify-between gap-3">
                        <span className="text-lg font-bold text-primary">
                            From {formatTHB(product.price)}
                        </span>
                        <Link href={`/products/${product.id}`}>
                            <Button size="sm" variant="outline">View</Button>
                        </Link>
                    </div>
                </div>
            </article>
        </ScrollReveal>
    );
};

export default ProductCard;
