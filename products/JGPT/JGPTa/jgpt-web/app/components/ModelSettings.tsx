"use client";

import { useState, useRef, useEffect } from "react";
import { Settings, X } from "lucide-react";

interface ModelSettingsProps {
    options: { temperature?: number; num_ctx?: number };
    onChange: (opts: { temperature?: number; num_ctx?: number }) => void;
}

export default function ModelSettings({ options, onChange }: ModelSettingsProps) {
    const [isOpen, setIsOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    // Close on click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (ref.current && !ref.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        if (isOpen) document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [isOpen]);

    const update = (key: string, val: number) => {
        onChange({ ...options, [key]: val });
    };

    return (
        <div className="relative" ref={ref}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`p-2 rounded-lg border transition-all ${isOpen
                        ? "bg-white/10 border-purple-500 text-purple-400"
                        : "bg-[#141428]/60 border-white/5 text-white/60 hover:text-white"
                    }`}
                title="Model Settings"
            >
                <Settings size={16} />
            </button>

            {isOpen && (
                <div className="absolute top-full right-0 mt-2 w-64 bg-[#0d0d1a] border border-white/10 rounded-xl shadow-2xl p-4 z-50 animate-fade-in">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider">Params</h3>
                        <button onClick={() => setIsOpen(false)} className="text-white/40 hover:text-white">
                            <X size={14} />
                        </button>
                    </div>

                    {/* Temperature */}
                    <div className="mb-4">
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-white/70">Temperature</span>
                            <span className="text-purple-400 font-mono">{options.temperature ?? 0.7}</span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={options.temperature ?? 0.7}
                            onChange={(e) => update("temperature", parseFloat(e.target.value))}
                            className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                        />
                        <div className="flex justify-between text-[9px] text-white/30 mt-1">
                            <span>Precise</span>
                            <span>Creative</span>
                        </div>
                    </div>

                    {/* Context Window */}
                    <div>
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-white/70">Context Window</span>
                            <span className="text-cyan-400 font-mono">{options.num_ctx ?? 4096}</span>
                        </div>
                        <select
                            value={options.num_ctx ?? 4096}
                            onChange={(e) => update("num_ctx", parseInt(e.target.value))}
                            className="w-full bg-white/5 border border-white/10 rounded px-2 py-1 text-xs text-white outline-none focus:border-cyan-500"
                        >
                            <option value={2048}>2048 (Fast)</option>
                            <option value={4096}>4096 (Standard)</option>
                            <option value={8192}>8192 (Large)</option>
                            <option value={16384}>16384 (Huge)</option>
                            <option value={32768}>32768 (Max)</option>
                        </select>
                    </div>
                </div>
            )}
        </div>
    );
}
