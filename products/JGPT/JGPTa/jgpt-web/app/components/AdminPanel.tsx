"use client";

import { useState, useEffect } from "react";
import AdminDashboard from "./AdminDashboard";
import SourcesDashboard from "./SourcesDashboard";
import SettingsForm from "./SettingsForm";
import ConnectionManager from "./ConnectionManager";
import { KBSource, KBStats } from "../types";

export default function AdminPanel() {
    const [tab, setTab] = useState("dashboard");
    const [sources, setSources] = useState<KBSource[]>([]);
    const [stats, setStats] = useState<KBStats | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshData = async () => {
        setLoading(true);
        try {
            const [sResp, stResp] = await Promise.all([
                fetch("/api/kb/sources", { headers: { "X-API-Key": "jgpt_master_key_change_me" } }),
                fetch("/api/kb/stats", { headers: { "X-API-Key": "jgpt_master_key_change_me" } })
            ]);
            if (sResp.ok) setSources(await sResp.json());
            if (stResp.ok) setStats(await stResp.json());
        } catch (e) {
            console.error("Failed to fetch admin data", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        refreshData();
    }, []);

    return (
        <div className="max-w-7xl mx-auto p-6">
            {/* Tab Navigation */}
            <div className="flex gap-6 mb-8 border-b border-white/10 pb-1">
                <button
                    onClick={() => setTab("dashboard")}
                    className={`px-4 py-3 font-semibold transition-all relative ${tab === 'dashboard'
                        ? 'text-[var(--accent)] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[var(--accent)]'
                        : 'text-white/50 hover:text-white/80'
                        }`}
                >
                    Dashboard
                </button>
                <button
                    onClick={() => setTab("knowledge")}
                    className={`px-4 py-3 font-semibold transition-all relative ${tab === 'knowledge'
                        ? 'text-[var(--accent)] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[var(--accent)]'
                        : 'text-white/50 hover:text-white/80'
                        }`}
                >
                    Management
                </button>
                <button
                    onClick={() => setTab("connections")}
                    className={`px-4 py-3 font-semibold transition-all relative ${tab === 'connections'
                        ? 'text-[var(--accent)] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[var(--accent)]'
                        : 'text-white/50 hover:text-white/80'
                        }`}
                >
                    Connections
                </button>
                <button
                    onClick={() => setTab("settings")}
                    className={`px-4 py-3 font-semibold transition-all relative ${tab === 'settings'
                        ? 'text-[var(--accent)] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[var(--accent)]'
                        : 'text-white/50 hover:text-white/80'
                        }`}
                >
                    Settings
                </button>
            </div>

            {/* Tab Content */}
            {tab === "dashboard" && (
                <AdminDashboard stats={stats} onRefresh={refreshData} />
            )}

            {tab === "knowledge" && (
                <SourcesDashboard
                    sources={sources}
                    stats={stats}
                    onRefresh={refreshData}
                    adminMode={true}
                />
            )}

            {tab === "settings" && (
                <div className="panel-card p-8 animate-fade-in">
                    <h2 className="text-2xl font-bold mb-2">System Configuration</h2>
                    <p className="text-white/60 mb-6">Tunable parameters for the RAG engine and Vision models.</p>
                    <hr className="border-white/10 mb-8" />
                    <SettingsForm />
                </div>
            )}

            {tab === "connections" && (
                <div className="animate-fade-in space-y-6">
                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold mb-2">Enterprise Data Gateway</h2>
                        <p className="text-white/60">Manage secure SQL connections for the Analyst functionality.</p>
                    </div>
                    <ConnectionManager />
                </div>
            )}
        </div>
    );
}
