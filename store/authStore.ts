import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
    name: string;
    email: string;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    login: (user: User) => void;
    logout: () => void;
    register: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            isAuthenticated: false,
            login: (user) => set({ user, isAuthenticated: true }),
            logout: () => set({ user: null, isAuthenticated: false }),
            register: (user) => set({ user, isAuthenticated: true }),
        }),
        {
            name: 'auth-storage',
        }
    )
);
