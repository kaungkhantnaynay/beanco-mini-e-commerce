'use client';

import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Container from '@/components/Container';
import Button from '@/components/Button';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ProfilePage() {
    const { user, isAuthenticated, logout } = useAuthStore();
    const router = useRouter();

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, router]);

    if (!isAuthenticated || !user) {
        return null;
    }

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    return (
        <main className="min-h-screen bg-background font-sans antialiased">
            <Navbar />

            <div className="pt-32 pb-16">
                <Container>
                    <div className="flex items-center justify-between mb-8">
                        <h1 className="text-3xl font-bold">My Profile</h1>
                        <Button variant="outline" onClick={handleLogout}>
                            Sign Out
                        </Button>
                    </div>

                    <div className="rounded-lg border bg-card p-6">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-2xl font-bold text-primary uppercase">
                                {user.name.charAt(0)}
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold">{user.name}</h2>
                                <p className="text-muted-foreground">{user.email}</p>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <h3 className="font-semibold mb-4">Order History</h3>
                                <p className="text-muted-foreground">No orders yet.</p>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-4">Account Settings</h3>
                                <Button variant="outline">Edit Profile</Button>
                            </div>
                        </div>
                    </div>
                </Container>
            </div>

            <Footer />
        </main>
    );
}
