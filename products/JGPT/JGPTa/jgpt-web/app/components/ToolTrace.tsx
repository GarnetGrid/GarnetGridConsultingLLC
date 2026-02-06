import { ToolRun } from "../types";
import { useState } from "react";
import { ChevronDown, ChevronRight, Brain, Wrench } from "lucide-react";

export default function ToolTrace({ traces }: { traces: ToolRun[] }) {
    const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());

    if (!traces.length) {
        return (
            <div className="flex items-center justify-center h-full text-white/20 text-xs text-center px-4">
                No reasoning trace available yet.
            </div>
        );
    }

    const toggleExpand = (idx: number) => {
        const newSet = new Set(expandedItems);
        if (newSet.has(idx)) {
            newSet.delete(idx);
        } else {
            newSet.add(idx);
        }
        setExpandedItems(newSet);
    };

    return (
        <div className="p-3 space-y-3">
            {traces.map((t, idx) => {
                const isExpanded = expandedItems.has(idx);
                return (
                    <div key={idx} className="relative">
                        {/* Timeline connector */}
                        {idx < traces.length - 1 && (
                            <div className="absolute left-[15px] top-[32px] bottom-[-12px] w-[2px] bg-gradient-to-b from-cyan-500/30 to-transparent" />
                        )}

                        {/* Thought Section (if exists) */}
                        {t.thought && (
                            <div className="flex gap-3 mb-2">
                                <div className="shrink-0 w-[30px] h-[30px] rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                                    <Brain size={14} className="text-purple-400" />
                                </div>
                                <div className="flex-1 bg-purple-500/5 border border-purple-500/20 rounded-lg p-3">
                                    <div className="text-[10px] font-bold text-purple-400 uppercase tracking-wider mb-1">
                                        💭 Thought Process
                                    </div>
                                    <div className="text-xs text-white/70 italic leading-relaxed">
                                        {t.thought}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Tool Execution Section */}
                        <div className="flex gap-3">
                            <div className="shrink-0 w-[30px] h-[30px] rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
                                <Wrench size={14} className="text-cyan-400" />
                            </div>
                            <div className="flex-1 bg-cyan-500/5 border border-cyan-500/20 rounded-lg overflow-hidden">
                                {/* Tool Header */}
                                <div
                                    className="flex items-center justify-between p-3 cursor-pointer hover:bg-cyan-500/10 transition-colors"
                                    onClick={() => toggleExpand(idx)}
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-bold text-cyan-400">
                                            🔧 {t.name}
                                        </span>
                                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300">
                                            Step {idx + 1}
                                        </span>
                                    </div>
                                    {isExpanded ? (
                                        <ChevronDown size={14} className="text-white/40" />
                                    ) : (
                                        <ChevronRight size={14} className="text-white/40" />
                                    )}
                                </div>

                                {/* Expanded Details */}
                                {isExpanded && (
                                    <div className="border-t border-cyan-500/20 p-3 space-y-3">
                                        <div>
                                            <div className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-1">
                                                Input
                                            </div>
                                            <pre className="text-[11px] font-mono text-cyan-300/80 bg-black/20 rounded p-2 overflow-x-auto">
                                                {JSON.stringify(t.input, null, 2)}
                                            </pre>
                                        </div>
                                        <div>
                                            <div className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-1">
                                                Output
                                            </div>
                                            <pre className="text-[11px] font-mono text-cyan-300/80 bg-black/20 rounded p-2 overflow-x-auto max-h-[200px]">
                                                {JSON.stringify(t.output, null, 2).slice(0, 1000)}
                                                {JSON.stringify(t.output).length > 1000 ? "\n..." : ""}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
