'use client';

import Image from 'next/image';
import Link from 'next/link';
import { ShoppingCart } from 'lucide-react';
import { motion } from 'framer-motion';
import Button from './Button';
import { Product, useCartStore } from '@/store/cartStore';

interface ProductCardProps {
    product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
    const addItem = useCartStore((state) => state.addItem);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="group relative overflow-hidden rounded-lg bg-card shadow-sm transition-shadow hover:shadow-md"
        >
            <Link href={`/products/${product.id}`} className="block aspect-square overflow-hidden bg-muted">
                <Image
                    src={product.image}
                    alt={product.name}
                    width={500}
                    height={500}
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
            </Link>
            <div className="p-4">
                <h3 className="text-lg font-semibold text-card-foreground">
                    <Link href={`/products/${product.id}`}>{product.name}</Link>
                </h3>
                <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                    {product.description}
                </p>
                <div className="mt-4 flex items-center justify-between">
                    <span className="text-lg font-bold text-primary">
                        ${product.price.toFixed(2)}
                    </span>
                    <Button
                        size="sm"
                        onClick={() => addItem(product)}
                        className="opacity-0 transition-opacity group-hover:opacity-100"
                    >
                        <ShoppingCart className="mr-2 h-4 w-4" />
                        Add
                    </Button>
                </div>
            </div>
        </motion.div>
    );
};

export default ProductCard;
