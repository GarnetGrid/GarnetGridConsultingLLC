"use client";

import { KBStats } from "../types";
import { useAuth } from "../context/AuthContext";
import { API_BASE } from "../constants";
import { Activity, Database, Eye, AlertOctagon, Trash2 } from "lucide-react";
import PowerBIUploader from "./PowerBIUploader";

interface AdminDashboardProps {
    stats: KBStats | null;
    onRefresh: () => void;
}

export default function AdminDashboard({ stats, onRefresh }: AdminDashboardProps) {
    const { token } = useAuth();

    const handleClearSystem = async () => {
        if (!confirm("Are you sure you want to clear EVERYTHING? This deletes all documents, chats, and vectors.")) return;

        try {
            const resp = await fetch(`${API_BASE}/admin/maintenance/clear-db`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (resp.ok) {
                alert("System cleared successfully.");
                onRefresh();
            } else {
                alert("Failed to clear system.");
            }
        } catch (e) {
            console.error(e);
            alert("Error clearing system.");
        }
    };

    return (
        <div className="animate-fade-in space-y-8">
            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* ID 14: Backend Status */}
                <div className="panel-card p-6 flex items-center justify-between group">
                    <div>
                        <div className="text-xs font-bold uppercase text-[var(--muted)] tracking-wider mb-2">Backend Status</div>
                        <div className="text-2xl font-bold flex items-center gap-3">
                            <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                            </span>
                            Healthy
                        </div>
                    </div>
                    <div className="p-3 rounded-xl bg-green-500/10 text-green-400 border border-green-500/20 group-hover:scale-110 transition-transform">
                        <Activity size={24} />
                    </div>
                </div>

                {/* ID 15: Vision Model */}
                <div className="panel-card p-6 flex items-center justify-between group">
                    <div>
                        <div className="text-xs font-bold uppercase text-[var(--muted)] tracking-wider mb-2">Active Vision Model</div>
                        <div className="text-2xl font-bold text-[var(--accent2)]">LLaVA:7b</div>
                    </div>
                    <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 group-hover:scale-110 transition-transform">
                        <Eye size={24} />
                    </div>
                </div>

                {/* ID 16: Knowledge Stats */}
                <div className="panel-card p-6 flex items-center justify-between group">
                    <div>
                        <div className="text-xs font-bold uppercase text-[var(--muted)] tracking-wider mb-2">Knowledge Chunks</div>
                        <div className="text-2xl font-bold">{stats?.total_chunks?.toLocaleString() || 0}</div>
                    </div>
                    <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 group-hover:scale-110 transition-transform">
                        <Database size={24} />
                    </div>
                </div>
            </div>

            {/* Ingestion Panel */}
            <div className="panel-card p-6 border-blue-500/20 bg-blue-500/5">
                <h3 className="text-xl font-bold flex items-center gap-2 mb-4">
                    <Database size={20} className="text-blue-400" />
                    Knowledge Ingestion
                </h3>

                <div className="mb-8">
                    <PowerBIUploader />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Quick URL Ingest */}
                    <div className="space-y-3">
                        <label className="text-sm font-medium text-[var(--muted)]">Quick URL Ingest</label>
                        <div className="flex gap-2">
                            <input
                                type="url"
                                placeholder="https://example.com/article"
                                className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm focus:border-blue-500/50 outline-none"
                                id="ingest-url-input"
                            />
                            <button
                                onClick={async () => {
                                    const input = document.getElementById('ingest-url-input') as HTMLInputElement;
                                    if (!input.value) return;
                                    try {
                                        const btn = document.getElementById('ingest-btn');
                                        if (btn) btn.innerHTML = '...';

                                        const res = await fetch(`${API_BASE}/ingest/url?url=${encodeURIComponent(input.value)}`, {
                                            method: 'POST',
                                            headers: { "Authorization": `Bearer ${token}` }
                                        });
                                        const data = await res.json();
                                        alert(JSON.stringify(data, null, 2));
                                        onRefresh();
                                    } catch (e) {
                                        console.error(e);
                                        alert("Ingestion failed");
                                    } finally {
                                        const btn = document.getElementById('ingest-btn');
                                        if (btn) btn.innerText = 'Ingest';
                                    }
                                }}
                                id="ingest-btn"
                                className="px-4 py-2.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-xl font-medium transition-colors"
                            >
                                Ingest
                            </button>
                        </div>
                    </div>

                    {/* Bulk Actions */}
                    <div className="space-y-3">
                        <label className="text-sm font-medium text-[var(--muted)]">Bulk Actions</label>
                        <div className="flex gap-3">
                            <button
                                onClick={async () => {
                                    if (!confirm("Re-ingest all local files?")) return;
                                    const res = await fetch(`${API_BASE}/ingest/kb`, {
                                        method: 'POST',
                                        headers: { "Authorization": `Bearer ${token}` }
                                    });
                                    alert(await res.text());
                                    onRefresh();
                                }}
                                className="flex-1 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm font-medium transition-colors"
                            >
                                Re-Sync Repo
                            </button>
                            <button
                                onClick={async () => {
                                    if (!confirm("Crawl curated web sources?")) return;
                                    const res = await fetch(`${API_BASE}/ingest/web`, {
                                        method: 'POST',
                                        headers: { "Authorization": `Bearer ${token}` }
                                    });
                                    alert(await res.text());
                                    onRefresh();
                                }}
                                className="flex-1 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm font-medium transition-colors"
                            >
                                Fetch Web
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Danger Zone */}
            <div className="panel-card p-8 border-red-500/20 bg-red-500/5 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                    <AlertOctagon size={120} className="text-red-500 rotate-12" />
                </div>

                <div className="relative z-10">
                    <h3 className="text-xl font-bold text-red-400 flex items-center gap-2 mb-2">
                        <AlertOctagon size={20} />
                        System Maintenance
                    </h3>
                    <p className="text-[var(--muted)] mb-6 max-w-2xl text-sm">
                        These actions are destructive and cannot be undone. This will wipe the vector database, SQL records, and chat history.
                    </p>

                    <button
                        onClick={handleClearSystem}
                        className="px-6 py-3 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 font-semibold transition-all flex items-center gap-2 hover:shadow-[0_0_20px_rgba(239,68,68,0.2)]"
                    >
                        <Trash2 size={18} />
                        Nuke Database (Clear All)
                    </button>
                </div>
            </div>
        </div>
    );
}
