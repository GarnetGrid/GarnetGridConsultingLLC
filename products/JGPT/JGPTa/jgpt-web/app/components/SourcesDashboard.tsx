"use client";

import { KBSource, KBStats } from "../types";
import { useAuth } from "../context/AuthContext";
import { RefreshCw, RotateCw, Trash2 } from "lucide-react";

interface Props {
    sources: KBSource[];
    stats: KBStats | null;
    onRefresh: () => void;
    busy?: boolean;
    adminMode?: boolean;
}

export default function SourcesDashboard({ sources, stats, onRefresh, busy, adminMode }: Props) {
    const { token } = useAuth();

    const handleDelete = async (path: string) => {
        if (!confirm(`Are you sure you want to delete ${path}?`)) return;
        if (!token) return;
        try {
            const resp = await fetch(`/api/kb/sources/${encodeURIComponent(path)}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (resp.ok) onRefresh();
            else alert("Failed to delete source.");
        } catch (e) {
            console.error(e);
            alert("Error deleting source.");
        }
    };

    const handleReingest = async (path: string) => {
        if (!token) return;
        try {
            const resp = await fetch(`/api/kb/sources/${encodeURIComponent(path)}/reingest`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (resp.ok) {
                alert("Re-ingestion started.");
                onRefresh();
            } else {
                alert("Failed to start re-ingestion.");
            }
        } catch (e) {
            console.error(e);
            alert("Error re-ingesting source.");
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    };

    const formatDate = (ts: number) => {
        return new Date(ts * 1000).toLocaleString();
    };

    return (
        <div className="p-6 max-w-7xl mx-auto animate-fade-in">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="panel-card p-6 text-center hover:-translate-y-1 transition-transform">
                    <div className="text-4xl font-bold text-[var(--accent2)] mb-2">
                        {stats?.total_documents || 0}
                    </div>
                    <div className="text-sm text-white/60 uppercase tracking-wider">Documents</div>
                </div>
                <div className="panel-card p-6 text-center hover:-translate-y-1 transition-transform">
                    <div className="text-4xl font-bold text-[var(--accent2)] mb-2">
                        {stats?.total_chunks || 0}
                    </div>
                    <div className="text-sm text-white/60 uppercase tracking-wider">Vector Chunks</div>
                </div>
                <div className="panel-card p-6 text-center hover:-translate-y-1 transition-transform">
                    <div className="text-4xl font-bold text-[var(--accent2)] mb-2">
                        {stats?.total_images || 0}
                    </div>
                    <div className="text-sm text-white/60 uppercase tracking-wider">Images Found</div>
                </div>
                <div className="panel-card p-6 text-center hover:-translate-y-1 transition-transform">
                    <div className="text-4xl font-bold text-green-400 mb-2">
                        {stats?.images_with_descriptions || 0}
                    </div>
                    <div className="text-sm text-white/60 uppercase tracking-wider">AI Described 👁️</div>
                </div>
            </div>

            {/* Sources Table */}
            <div className="panel-card overflow-hidden">
                {/* Table Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
                    <h3 className="text-xl font-bold">Knowledge Base Explorer</h3>
                    <button
                        className="btn px-4 py-2 flex items-center gap-2 text-sm disabled:opacity-50"
                        onClick={onRefresh}
                        disabled={busy}
                    >
                        <RefreshCw size={16} className={busy ? "animate-spin" : ""} />
                        {busy ? "Refreshing..." : "Refresh Stats"}
                    </button>
                </div>

                {/* Table */}
                <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                        <thead>
                            <tr className="bg-white/5 text-left border-b border-white/10">
                                <th className="px-6 py-4 text-sm font-semibold text-white/70">File Name</th>
                                <th className="px-6 py-4 text-sm font-semibold text-white/70">Type</th>
                                <th className="px-6 py-4 text-sm font-semibold text-white/70">Size</th>
                                <th className="px-6 py-4 text-sm font-semibold text-white/70">Chunks</th>
                                <th className="px-6 py-4 text-sm font-semibold text-white/70">Vision</th>
                                <th className="px-6 py-4 text-sm font-semibold text-white/70">Last Sync</th>
                                {adminMode && <th className="px-6 py-4 text-sm font-semibold text-white/70">Actions</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {sources.length === 0 && (
                                <tr>
                                    <td colSpan={adminMode ? 7 : 6} className="text-center py-20 text-white/40">
                                        <div className="text-5xl mb-3">📚</div>
                                        <p>No documents found in knowledge base.</p>
                                    </td>
                                </tr>
                            )}
                            {sources.map((src, i) => (
                                <tr key={i} className="border-t border-white/5 hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-mono text-sm text-white/90">{src.path}</td>
                                    <td className="px-6 py-4">
                                        <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-medium opacity-70">
                                            {src.extension.replace(".", "")}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-white/70">{formatSize(src.size)}</td>
                                    <td className="px-6 py-4 text-sm font-bold">{src.chunks}</td>
                                    <td className="px-6 py-4 text-sm">
                                        {src.images > 0 ? (
                                            <span className={src.chunks > 0 ? "text-[var(--accent2)]" : "text-white/40"}>
                                                {src.images} imgs
                                            </span>
                                        ) : (
                                            <span className="text-white/30">-</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-xs text-white/50">{formatDate(src.mtime)}</td>
                                    {adminMode && (
                                        <td className="px-6 py-4">
                                            <div className="flex gap-2">
                                                <button
                                                    className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/60 hover:text-white"
                                                    onClick={() => handleReingest(src.path)}
                                                    title="Re-ingest"
                                                >
                                                    <RotateCw size={16} />
                                                </button>
                                                <button
                                                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400 hover:text-red-300"
                                                    onClick={() => handleDelete(src.path)}
                                                    title="Delete"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                        </td>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
