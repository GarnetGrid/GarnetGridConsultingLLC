import { useState, useEffect } from "react";
import { Conv } from "../types";
import { useAuth } from "../context/AuthContext";
import { Trash2, MessageSquare, Plus, LogOut } from "lucide-react";
import LoadingSpinner from "./LoadingSpinner";

interface SidebarProps {
    convs: Conv[];
    activeId?: number;
    onNew: () => void;
    onLoad: (id: number) => void;
    onDelete: (id: number) => void;
    onIngest: (url: string) => void;
    projectContext: string;
    onContextChange: (ctx: string) => void;
    loading?: boolean;
}

export default function Sidebar({
    convs,
    activeId,
    onNew,
    onLoad,
    onDelete,
    onIngest,
    projectContext,
    onContextChange,
    loading = false,
}: SidebarProps) {
    const { user, logout } = useAuth();
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        setIsAdmin(user?.role === "admin");
    }, [user]);

    // Group conversations by date
    const groupedConvs = convs.reduce((acc, c) => {
        const d = new Date(c.created_at).toDateString();
        if (!acc[d]) acc[d] = [];
        acc[d].push(c);
        return acc;
    }, {} as Record<string, Conv[]>);

    return (
        <div className="h-full flex flex-col bg-[#0d0d1a]/50 backdrop-blur-xl border-r border-white/5">
            <div className="shrink-0 p-4 border-b border-white/5 flex items-center justify-between">
                <span className="text-sm font-bold uppercase tracking-wider text-white/50">History</span>
                <button
                    onClick={onNew}
                    className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-white/70 hover:text-white border border-white/10 hover:border-white/20"
                    title="New Chat"
                >
                    <Plus size={18} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-1.5 space-y-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <LoadingSpinner size="md" text="Loading conversations..." />
                    </div>
                ) : (
                    <>
                        {Object.entries(groupedConvs).map(([date, items]) => (
                            <div key={date}>
                                <div className="px-3 py-1.5 text-[10px] font-bold uppercase text-white/30 tracking-widest sticky top-0 bg-[#0d0d1a]/90 backdrop-blur-md z-10 block rounded-md mb-0.5">
                                    {date}
                                </div>
                                <div className="space-y-0.5">
                                    {items.map((c) => (
                                        <div
                                            key={c.id}
                                            onClick={() => onLoad(c.id)}
                                            className={`group relative text-xs py-2 px-2.5 rounded-md cursor-pointer transition-all duration-200 border border-transparent ${activeId === c.id
                                                ? "bg-white/10 text-white border-white/5 shadow-sm"
                                                : "text-white/60 hover:bg-white/5 hover:text-white/90"
                                                }`}
                                        >
                                            <div className="font-medium truncate pr-6 text-[11px]">{c.title || "New Chat"}</div>
                                            <div className="text-[9px] text-white/30 mt-0.5 flex items-center gap-1.5">
                                                <span className="uppercase tracking-wider">{c.model || "LLAMA"}</span>
                                                {c.mode && <span className="px-1 py-0 rounded bg-white/5 border border-white/5">{c.mode}</span>}
                                            </div>

                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    if (confirm("Delete conversation?")) onDelete(c.id);
                                                }}
                                                className="absolute right-1 top-1/2 -translate-y-1/2 p-1 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 rounded-md transition-all"
                                            >
                                                <Trash2 size={10} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}

                        {convs.length === 0 && (
                            <div className="flex flex-col items-center justify-center py-10 text-center opacity-40">
                                <MessageSquare size={32} className="mb-2" />
                                <p className="text-xs">No conversations yet</p>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Bottom section - pinned to bottom */}
            <div className="shrink-0 p-3 border-t border-white/5 bg-black/20 space-y-3">
                {/* Project Context Input */}
                <div className="space-y-1.5">
                    <label className="text-[10px] font-bold uppercase text-white/30 tracking-wider px-1">Project Context</label>
                    <textarea
                        className="w-full bg-black/20 border border-white/5 rounded-lg p-2 text-[11px] text-white/80 placeholder:text-white/20 focus:outline-none focus:border-white/20 focus:bg-black/40 transition-all resize-none font-mono"
                        rows={3}
                        placeholder="Add context for this session..."
                        value={projectContext}
                        onChange={(e) => onContextChange(e.target.value)}
                    />
                </div>

                <div className="pt-2 border-t border-white/5">
                    <div className="flex items-center gap-3 px-2 py-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-pink-500 to-cyan-500 p-[1px]">
                            <div className="w-full h-full rounded-full bg-black flex items-center justify-center text-xs font-bold">
                                {user?.email?.charAt(0).toUpperCase() || "U"}
                            </div>
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-xs font-medium truncate text-white/90">{user?.email}</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">{user?.role}</div>
                        </div>
                        <button
                            onClick={logout}
                            className="p-1.5 hover:bg-white/10 rounded-md text-white/40 hover:text-white transition-colors"
                            title="Logout"
                        >
                            <LogOut size={14} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
