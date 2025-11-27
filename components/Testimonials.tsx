'use client';

import { Swiper, SwiperSlide } from 'swiper/react';
import { Pagination, Autoplay } from 'swiper/modules';
import Container from './Container';
import { Star } from 'lucide-react';
import 'swiper/css';
import 'swiper/css/pagination';

const testimonials = [
    {
        id: 1,
        name: 'Emily Watson',
        role: 'Coffee Enthusiast',
        quote: "The Ethiopian Yirgacheffe is hands down the best coffee I've ever tasted. The floral notes are incredible!",
        rating: 5,
    },
    {
        id: 2,
        name: 'Michael Chen',
        role: 'Home Barista',
        quote: "I love the subscription service. Fresh beans delivered right to my door, and the quality is consistently amazing.",
        rating: 5,
    },
    {
        id: 3,
        name: 'Sarah Johnson',
        role: 'Cafe Owner',
        quote: "BeanCo's sourcing transparency is what drew me in, but the flavor is what keeps me coming back. Highly recommended.",
        rating: 5,
    },
    {
        id: 4,
        name: 'David Miller',
        role: 'Daily Drinker',
        quote: "The Espresso Blend makes the perfect morning latte. Rich, bold, and smooth. My mornings aren't the same without it.",
        rating: 4,
    },
];

const Testimonials = () => {
    return (
        <section className="py-24 bg-secondary/10">
            <Container>
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                        What Our Customers Say
                    </h2>
                    <p className="mt-4 text-lg text-muted-foreground">
                        Don't just take our word for it. Here's what coffee lovers are saying about BeanCo.
                    </p>
                </div>

                <Swiper
                    modules={[Pagination, Autoplay]}
                    spaceBetween={30}
                    slidesPerView={1}
                    pagination={{ clickable: true }}
                    autoplay={{
                        delay: 5000,
                        disableOnInteraction: false,
                    }}
                    breakpoints={{
                        640: {
                            slidesPerView: 1,
                        },
                        768: {
                            slidesPerView: 2,
                        },
                        1024: {
                            slidesPerView: 3,
                        },
                    }}
                    className="pb-12"
                >
                    {testimonials.map((testimonial) => (
                        <SwiperSlide key={testimonial.id} className="pb-12">
                            <div className="h-full rounded-2xl border bg-card p-8 shadow-sm transition-shadow hover:shadow-md">
                                <div className="flex gap-1 mb-4">
                                    {[...Array(5)].map((_, i) => (
                                        <Star
                                            key={i}
                                            className={`h-5 w-5 ${i < testimonial.rating
                                                    ? 'fill-primary text-primary'
                                                    : 'fill-muted text-muted-foreground'
                                                }`}
                                        />
                                    ))}
                                </div>
                                <blockquote className="text-lg text-foreground mb-6">
                                    "{testimonial.quote}"
                                </blockquote>
                                <div>
                                    <div className="font-semibold">{testimonial.name}</div>
                                    <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                                </div>
                            </div>
                        </SwiperSlide>
                    ))}
                </Swiper>
            </Container>
        </section>
    );
};

export default Testimonials;
