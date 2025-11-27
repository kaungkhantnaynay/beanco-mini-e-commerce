import { Product } from '@/store/cartStore';

export const products: Product[] = [
    {
        id: '1',
        name: 'Ethiopian Yirgacheffe',
        price: 24.00,
        image: 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&q=80&w=1000',
        description: 'Bright and floral with notes of jasmine and lemon. A classic Ethiopian coffee.',
    },
    {
        id: '2',
        name: 'Colombian Supremo',
        price: 18.50,
        image: 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&q=80&w=1000',
        description: 'Balanced and smooth with caramel sweetness and nutty undertones.',
    },
    {
        id: '3',
        name: 'Sumatra Mandheling',
        price: 22.00,
        image: '/images/sumatra-mandheling.png',
        description: 'Full-bodied and earthy with a rich, complex flavor profile.',
    },
    {
        id: '4',
        name: 'Espresso Blend',
        price: 20.00,
        image: '/images/espresso-blend.png',
        description: 'A bold and intense blend perfect for espresso shots and milk-based drinks.',
    },
    {
        id: '5',
        name: 'Ceramic Coffee Cup',
        price: 12.00,
        image: '/images/ceramic-cup.png',
        description: 'Minimalist ceramic cup with a matte finish, perfect for your daily brew.',
    },
    {
        id: '6',
        name: 'Pour Over Kit',
        price: 45.00,
        image: '/images/pour-over-kit.png',
        description: 'Complete pour over kit including a glass carafe, dripper, and kettle.',
    },
    {
        id: '7',
        name: 'Coffee Grinder',
        price: 85.00,
        image: '/images/coffee-grinder.png',
        description: 'Premium electric grinder for consistent and precise coffee grounds.',
    },
    {
        id: '8',
        name: 'Travel Mug',
        price: 25.00,
        image: '/images/travel-mug.png',
        description: 'Insulated stainless steel travel mug to keep your coffee hot on the go.',
    },
];
