'use client';

import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import Link from 'next/link';
import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const login = useAuthStore((state) => state.login);
    const router = useRouter();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!formData.email || !formData.password) {
            setError('Please fill in all fields');
            return;
        }
        
        login({ name: formData.email.split('@')[0], email: formData.email });
        router.push('/profile');
    };

    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="flex min-h-[80vh] items-center justify-center pt-24 pb-12">
                <Container className="max-w-md">
                    <div className="rounded-lg border bg-card p-8 shadow-sm">
                        <h1 className="text-2xl font-bold text-center mb-6">Welcome Back</h1>
                        {error && (
                            <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md mb-4">
                                {error}
                            </div>
                        )}
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1" htmlFor="email">Email</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                    placeholder="hello@example.com"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1" htmlFor="password">Password</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                />
                            </div>
                            <Button type="submit" className="w-full">Sign In</Button>
                        </form>
                        <div className="mt-4 text-center text-sm text-muted-foreground">
                            Don't have an account?{' '}
                            <Link href="/register" className="text-primary hover:underline">
                                Sign up
                            </Link>
                        </div>
                    </div>
                </Container>
            </div>

            <Footer />
        </main>
    );
}
