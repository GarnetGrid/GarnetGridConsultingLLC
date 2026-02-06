import React, { useState } from 'react';
import { ChevronDown, ChevronRight, BrainCircuit, Terminal, Activity } from 'lucide-react';

import { ThoughtProp } from '../types';
interface ThinkingBubbleProps {
    thoughts: ThoughtProp[];
    isThinking: boolean;
}

export const ThinkingBubble: React.FC<ThinkingBubbleProps> = ({ thoughts, isThinking }) => {
    const [isExpanded, setIsExpanded] = useState(true);

    if (thoughts.length === 0 && !isThinking) return null;

    return (
        <div className="my-4 rounded-lg border border-cyan-500/20 bg-cyan-950/10 overflow-hidden text-sm">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center gap-2 p-3 bg-cyan-950/20 hover:bg-cyan-950/30 transition-colors text-cyan-400 font-mono text-xs uppercase tracking-wider"
            >
                {isThinking ? (
                    <Activity className="w-4 h-4 animate-pulse" />
                ) : (
                    <BrainCircuit className="w-4 h-4" />
                )}
                <span>{isThinking ? "Reasoning Engine Active..." : "Thought Process Complete"}</span>
                <span className="ml-auto text-cyan-500/50">
                    {thoughts.length} Steps
                </span>
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>

            {isExpanded && (
                <div className="p-4 space-y-3 font-mono text-xs leading-relaxed max-h-96 overflow-y-auto">
                    {thoughts.map((step, idx) => (
                        <div key={idx} className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
                            <div className="mt-0.5 shrink-0 opacity-50">
                                {step.type === 'thought' && <span className="text-cyan-400">▍</span>}
                                {step.type === 'tool_call' && <Terminal className="w-3 h-3 text-amber-400" />}
                                {step.type === 'tool_result' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1" />}
                            </div>

                            <div className="flex-1 overflow-hidden">
                                {step.type === 'thought' && (
                                    <p className="text-cyan-100/80">{step.content?.replace(/^Thinking:\s*/, '')}</p>
                                )}

                                {step.type === 'tool_call' && (
                                    <div className="bg-black/30 p-2 rounded border border-amber-500/20">
                                        <span className="text-amber-500 font-bold block mb-1">EXECUTE {step.tool}</span>
                                        <code className="text-amber-200/80 block whitespace-pre-wrap">{step.input}</code>
                                    </div>
                                )}

                                {step.type === 'tool_result' && (
                                    <div className="text-emerald-400/80 pl-2 border-l-2 border-emerald-500/20">
                                        {step.result?.replace(/^Observation:\s*/, '')}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {isThinking && (
                        <div className="flex items-center gap-2 text-cyan-500/50 pt-2 animate-pulse">
                            <div className="w-2 h-2 bg-cyan-500 rounded-full" />
                            <span>Computing...</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
