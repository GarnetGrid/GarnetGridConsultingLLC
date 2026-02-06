"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface User {
    email: string;
    role: "admin" | "viewer";
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Check for token on mount
        const storedToken = localStorage.getItem("jgpt_token");
        if (storedToken) {
            try {
                const parts = storedToken.split(".");
                if (parts.length !== 3) throw new Error("Invalid token format");

                const payload = JSON.parse(atob(parts[1]));
                // Basic expiration check (if exp exists)
                if (payload.exp && Date.now() >= payload.exp * 1000) {
                    throw new Error("Token expired");
                }

                setToken(storedToken);
                setUser({ email: payload.sub, role: payload.role });
            } catch (e) {
                console.error("Auth initialization failed:", e);
                localStorage.removeItem("jgpt_token");
                setToken(null);
                setUser(null);
            }
        }
        setIsLoading(false);
    }, []);

    const login = (newToken: string) => {
        try {
            const parts = newToken.split(".");
            if (parts.length !== 3) throw new Error("Invalid token format");

            const payload = JSON.parse(atob(parts[1]));
            localStorage.setItem("jgpt_token", newToken);
            setToken(newToken);
            setUser({ email: payload.sub, role: payload.role });

            // Redirect based on role or default
            if (payload.role === "admin") {
                router.push("/?tab=admin");
            } else {
                router.push("/");
            }
        } catch (e) {
            console.error("Login failed decoding:", e);
            alert("Login failed: Invalid session token received.");
        }
    };

    const logout = () => {
        localStorage.removeItem("jgpt_token");
        setToken(null);
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
