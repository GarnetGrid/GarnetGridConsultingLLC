"use client";

import { useState, useEffect } from "react";
import LoadingSpinner from "./LoadingSpinner";

interface Settings {
    chunk_size: number;
    chunk_overlap: number;
    rerank: number;
    vision_model: string;
    embed_model: string;
    chat_model: string;
}

export default function SettingsForm() {
    const [settings, setSettings] = useState<Settings | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const resp = await fetch("/api/admin/settings", {
                    headers: { "X-API-Key": "jgpt_master_key_change_me" }
                });
                if (resp.ok) setSettings(await resp.json());
            } catch (e) {
                console.error("Failed to fetch settings", e);
            } finally {
                setLoading(false);
            }
        };
        fetchSettings();
    }, []);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!settings) return;
        setSaving(true);
        try {
            const resp = await fetch("/api/admin/settings", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": "jgpt_master_key_change_me"
                },
                body: JSON.stringify(settings)
            });
            if (resp.ok) {
                alert("Settings updated for current session.");
            } else {
                alert("Failed to save settings.");
            }
        } catch (e) {
            console.error(e);
            alert("Error saving settings.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return (
        <div className="p-8 flex items-center justify-center min-h-[400px]">
            <LoadingSpinner size="lg" text="Loading system configuration..." />
        </div>
    );
    if (!settings) return <div className="p-8 text-center text-red-400">Error loading settings.</div>;

    return (
        <form onSubmit={handleSave} className="flex flex-col gap-6 max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-200">Chunk Size</label>
                    <input
                        type="number"
                        value={settings.chunk_size}
                        onChange={e => setSettings({ ...settings, chunk_size: parseInt(e.target.value) })}
                        className="input-field"
                    />
                    <small className="text-xs text-muted">Target tokens per chunk (default: 300)</small>
                </div>
                <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-200">Chunk Overlap</label>
                    <input
                        type="number"
                        value={settings.chunk_overlap}
                        onChange={e => setSettings({ ...settings, chunk_overlap: parseInt(e.target.value) })}
                        className="input-field"
                    />
                    <small className="text-xs text-muted">Token overlap between chunks (default: 100)</small>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-200">Reranking Limit</label>
                    <input
                        type="number"
                        value={settings.rerank}
                        onChange={e => setSettings({ ...settings, rerank: parseInt(e.target.value) })}
                        className="input-field"
                    />
                    <small className="text-xs text-muted">Number of chunks to rerank via LLM (0 = Disabled)</small>
                </div>
                <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-200">Vision Model</label>
                    <input
                        type="text"
                        value={settings.vision_model}
                        onChange={e => setSettings({ ...settings, vision_model: e.target.value })}
                        className="input-field"
                    />
                    <small className="text-xs text-muted">Model used for image captioning (e.g., llava:7b)</small>
                </div>
            </div>

            <div className="pt-4 border-t border-white/5">
                <button
                    type="submit"
                    className="btn btn-primary w-full md:w-auto min-w-[150px]"
                    disabled={saving}
                >
                    {saving ? "Saving..." : "Apply Changes"}
                </button>
                <p className="mt-3 text-xs text-muted/60">
                    Note: Changes apply to the current server session and may be reset on container restart if not updated in .env.
                </p>
            </div>
        </form>
    );
}

