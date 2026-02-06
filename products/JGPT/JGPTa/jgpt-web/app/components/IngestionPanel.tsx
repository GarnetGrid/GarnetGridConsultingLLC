import { useState } from "react";
import { API_BASE } from "../constants";
import { useAuth } from "../context/AuthContext";
import { X } from "lucide-react";

interface IngestionPanelProps {
    onClose: () => void;
    busy: boolean;
    setBusy: (b: boolean) => void;
}

export default function IngestionPanel({ onClose, busy, setBusy }: IngestionPanelProps) {
    const { token } = useAuth();
    const [type, setType] = useState<"url" | "text" | "file">("url");
    const [url, setUrl] = useState("");
    const [text, setText] = useState("");

    async function handleIngest() {
        if (busy) return;
        setBusy(true);

        try {
            if (type === "url") {
                if (!token) { alert("You must be logged in to ingest."); return; }
                const r = await fetch(`${API_BASE}/ingest/url?url=${encodeURIComponent(url)}`, {
                    method: "POST",
                    headers: { "Authorization": `Bearer ${token}` }
                });
                const res = await r.json();
                if (res.ok) alert(`Successfully ingested URL. ${res.chunks} chunks indexed.`);
                else alert("Error: " + res.error);
            } else if (type === "text") {
                alert("Text ingestion coming soon (backend update needed).");
            } else {
                alert("File ingestion coming soon.");
            }
        } catch (e) {
            alert("Ingestion failed: " + e);
        } finally {
            setBusy(false);
        }
    }

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-2xl mx-4">
                <div className="panel-card p-8 animate-fade-in">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold">Knowledge Center</h2>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/60 hover:text-white"
                        >
                            <X size={24} />
                        </button>
                    </div>

                    {/* Type Selector */}
                    <div className="flex gap-3 mb-6">
                        <button
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${type === "url"
                                    ? "bg-[var(--accent)] text-white shadow-lg"
                                    : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white"
                                }`}
                            onClick={() => setType("url")}
                        >
                            URL
                        </button>
                        <button
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${type === "text"
                                    ? "bg-[var(--accent)] text-white shadow-lg"
                                    : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white"
                                }`}
                            onClick={() => setType("text")}
                        >
                            Raw Text
                        </button>
                        <button
                            className={`px-4 py-2 rounded-lg font-medium transition-all ${type === "file"
                                    ? "bg-[var(--accent)] text-white shadow-lg"
                                    : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white"
                                }`}
                            onClick={() => setType("file")}
                        >
                            File Upload
                        </button>
                    </div>

                    {/* URL Input */}
                    {type === "url" && (
                        <div className="mb-6">
                            <label className="block text-sm font-semibold text-white/70 mb-2">
                                Enter Documentation URL
                            </label>
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="https://docs.example.com/..."
                                className="input-field w-full"
                            />
                        </div>
                    )}

                    {/* Text Input */}
                    {type === "text" && (
                        <div className="mb-6">
                            <label className="block text-sm font-semibold text-white/70 mb-2">
                                Paste Raw Markdown/Text
                            </label>
                            <textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                className="input-field w-full h-40 resize-none"
                                placeholder="Paste your content here..."
                            />
                        </div>
                    )}

                    {/* File Upload Placeholder */}
                    {type === "file" && (
                        <div className="mb-6 text-center py-12 border-2 border-dashed border-white/20 rounded-lg">
                            <p className="text-white/40">File upload coming soon</p>
                        </div>
                    )}

                    {/* Action Button */}
                    <button
                        className="btn-primary w-full py-4 text-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={busy || (type === "url" && !url) || (type === "text" && !text)}
                        onClick={handleIngest}
                    >
                        {busy ? "Ingesting..." : "Ingest into Knowledge Base"}
                    </button>
                </div>
            </div>
        </>
    );
}
