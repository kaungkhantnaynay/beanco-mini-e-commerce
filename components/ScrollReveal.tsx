'use client';

import { motion, useReducedMotion } from 'framer-motion';
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type ScrollRevealProps = {
    children: ReactNode;
    className?: string;
    delay?: number;
    direction?: 'up' | 'down' | 'left' | 'right';
    distance?: number;
};

const directionOffset = {
    up: { y: 48 },
    down: { y: -48 },
    left: { x: 48 },
    right: { x: -48 },
};

const ScrollReveal = ({
    children,
    className,
    delay = 0,
    direction = 'up',
    distance = 48,
}: ScrollRevealProps) => {
    const prefersReducedMotion = useReducedMotion();
    const offset = directionOffset[direction];
    const hiddenOffset = Object.fromEntries(
        Object.entries(offset).map(([axis, value]) => [axis, Math.sign(value) * distance])
    );

    if (prefersReducedMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={cn(
                'will-change-transform',
                (direction === 'left' || direction === 'right') && 'scroll-reveal-horizontal',
                className,
            )}
            initial={{ opacity: 0, ...hiddenOffset }}
            whileInView={{ opacity: 1, x: 0, y: 0 }}
            viewport={{ once: true, amount: 0.22 }}
            transition={{
                duration: 0.8,
                delay,
                ease: [0.22, 1, 0.36, 1],
            }}
        >
            {children}
        </motion.div>
    );
};

export default ScrollReveal;
