"use client";

import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { API_BASE } from "../constants";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            // Derive auth URL from API_BASE (remove /api suffix if present)
            const baseUrl = API_BASE.replace(/\/api$/, "");
            const res = await fetch(`${baseUrl}/auth/token`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: formData,
            });

            if (!res.ok) {
                throw new Error("Invalid credentials");
            }

            const data = await res.json();
            login(data.access_token);
        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("Login failed");
            }
        }
    };

    return (
        <div className="absolute inset-0 z-10 flex min-h-screen items-center justify-center p-4">
            {/* Background Glow (Local override if global misses) */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div key="glow-1" className="absolute top-[-10%] left-[-10%] w-1/2 h-1/2 rounded-full bg-blue-500/20 blur-[120px]" />
                <div key="glow-2" className="absolute bottom-[-10%] right-[-10%] w-1/2 h-1/2 rounded-full bg-purple-500/20 blur-[120px]" />
            </div>

            {/* Main Card */}
            <div className="w-full max-w-md bg-white/5 backdrop-blur-2xl border border-white/10 rounded-2xl p-8 shadow-2xl relative z-20 animate-fade-in ring-1 ring-white/5">

                {/* Header */}
                <div className="mb-8 text-center">
                    <h1 className="text-4xl md:text-5xl font-black mb-3 tracking-tighter drop-shadow-sm">
                        <span className="bg-gradient-to-r from-white via-white to-gray-400 bg-clip-text text-transparent block">Garnet Grid</span>
                        <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent text-3xl md:text-4xl block mt-1">AI Engine</span>
                    </h1>
                    <p className="text-gray-400 text-xs md:text-sm font-light tracking-wide">
                        Unified Intelligence & Orchestration
                    </p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-200 rounded-lg text-sm flex items-center gap-3 backdrop-blur-sm">
                        <svg className="w-5 h-5 shrink-0 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span className="font-medium">{error}</span>
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-xs uppercase tracking-wider font-semibold text-gray-400 ml-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full bg-black/40 border border-white/5 rounded-xl px-4 py-3.5 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all font-light"
                            placeholder="admin@jgpt.com"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs uppercase tracking-wider font-semibold text-gray-400 ml-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full bg-black/40 border border-white/5 rounded-xl px-4 py-3.5 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all font-light"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-4 px-6 rounded-xl transition-all transform hover:translate-y-[-1px] shadow-lg hover:shadow-purple-500/25 active:scale-[0.98] mt-2"
                    >
                        Sign In
                    </button>
                </form>

                {/* Footer */}
                <div className="mt-8 text-center pt-6 border-t border-white/5">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/5">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                        <p className="text-[10px] text-gray-400 uppercase tracking-widest font-medium">
                            System Operational
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
