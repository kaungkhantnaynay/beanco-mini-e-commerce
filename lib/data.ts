export interface Product {
    id: string;
    name: string;
    price: number;
    image: string;
    description: string;
    profile: string;
}

export const products: Product[] = [
    {
        id: '1',
        name: 'Ethiopian Yirgacheffe',
        price: 850,
        image: 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&q=80&w=1000',
        description: 'Bright and floral with notes of jasmine and lemon. A classic Ethiopian coffee.',
        profile: 'Floral, citrus, honey',
    },
    {
        id: '2',
        name: 'Colombian Supremo',
        price: 650,
        image: 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&q=80&w=1000',
        description: 'Balanced and smooth with caramel sweetness and nutty undertones.',
        profile: 'Caramel, almond, cocoa',
    },
    {
        id: '3',
        name: 'Sumatra Mandheling',
        price: 780,
        image: '/images/sumatra-mandheling.png',
        description: 'Full-bodied and earthy with a rich, complex flavor profile.',
        profile: 'Earthy, spice, dark chocolate',
    },
    {
        id: '4',
        name: 'Espresso Blend',
        price: 700,
        image: '/images/espresso-blend.png',
        description: 'A bold and intense blend perfect for espresso shots and milk-based drinks.',
        profile: 'Molasses, toasted nut, crema',
    },
    {
        id: '5',
        name: 'Ceramic Coffee Cup',
        price: 420,
        image: '/images/ceramic-cup.png',
        description: 'Minimalist ceramic cup with a matte finish, perfect for your daily brew.',
        profile: 'Cafe-grade ceramic',
    },
    {
        id: '6',
        name: 'Pour Over Kit',
        price: 1550,
        image: '/images/pour-over-kit.png',
        description: 'Complete pour over kit including a glass carafe, dripper, and kettle.',
        profile: 'Precision brewing kit',
    },
    {
        id: '7',
        name: 'Coffee Grinder',
        price: 2990,
        image: '/images/coffee-grinder.png',
        description: 'Premium electric grinder for consistent and precise coffee grounds.',
        profile: 'Consistent cafe grind',
    },
    {
        id: '8',
        name: 'Travel Mug',
        price: 850,
        image: '/images/travel-mug.png',
        description: 'Insulated stainless steel travel mug to keep your coffee hot on the go.',
        profile: 'Insulated stainless steel',
    },
];
