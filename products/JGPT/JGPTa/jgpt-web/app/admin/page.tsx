"use client";

import React, { useState, useEffect } from "react";
import AdminDashboard from "../components/AdminDashboard";
import { KBStats } from "../types";
import { useAuth } from "../context/AuthContext";
import { API_BASE } from "../constants";

export default function AdminPage() {
    const [stats, setStats] = useState<KBStats | null>(null);
    const { token } = useAuth();

    const fetchStats = async () => {
        try {
            const res = await fetch(`${API_BASE}/kb/stats`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        if (token) fetchStats();
    }, [token]);

    return (
        <div className="container mx-auto p-8 max-w-7xl animate-fade-in">
            <div className="mb-10">
                <h1 className="text-4xl font-extrabold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 tracking-tight">
                    Admin Console
                </h1>
                <p className="text-[var(--muted)] text-lg">
                    Monitor system health, knowledge base stats, and perform maintenance.
                </p>
            </div>

            <AdminDashboard stats={stats} onRefresh={fetchStats} />
        </div>
    );
}
