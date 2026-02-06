import { Msg, Citation, ToolRun, ChatResp, ThoughtProp } from "../types";
import CitationPanel from "./CitationPanel";
import ToolTrace from "./ToolTrace";
import { useMemo, useState } from "react";
import { ArrowUp, StopCircle, RefreshCw, FileText, Download, ChevronDown, ChevronUp, Brain, Sparkles } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import ChartRenderer from './ChartRenderer';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ThinkingBubble } from "./ThinkingBubble";

interface ChatAreaProps {
    messages: Msg[];
    input: string;
    setInput: (s: string) => void;
    send: () => void;
    busy: boolean;
    streaming: boolean;
    onStop: () => void;
    answer: string;
    citations: Citation[];
    toolTrace: ToolRun[];
    retrieval: any;
    showDeep: boolean;
    setShowDeep: (b: boolean) => void;
    showCites: boolean;
    setShowCites: (b: boolean) => void;
    showTools: boolean;
    setShowTools: (b: boolean) => void;
    onExport: () => void;
    onRegen: (id: number) => void;
    onFullExport?: () => void;
    audit: any;
    isCollapsed: boolean;
    toggleSearch: () => void;
    agentStatus?: string;
    thoughts?: ThoughtProp[];
    isReasoning: boolean;
    setIsReasoning: (b: boolean) => void;
}

function splitShortDeep(answer: string): { short: string; deep: string } {
    const a = answer || "";
    const idx = a.toLowerCase().indexOf("**deep dive");
    if (idx === -1) return { short: a, deep: "" };
    return { short: a.slice(0, idx).trim(), deep: a.slice(idx).trim() };
}

export default function ChatArea(props: ChatAreaProps) {
    const {
        messages, input, setInput, send, busy, streaming, onStop, answer,
        citations, toolTrace, retrieval,
        showDeep, setShowDeep, showCites, setShowCites, showTools, setShowTools,
        onExport, onRegen, onFullExport, audit, isCollapsed, toggleSearch,
        agentStatus, thoughts = [], isReasoning, setIsReasoning
    } = props;

    const shortDeep = useMemo(() => splitShortDeep(answer), [answer]);
    const [panelsOpen, setPanelsOpen] = useState(true);

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Messages Area - Flex Grow to take available space */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                {messages.map((m, i) => (
                    <div key={i} className={`flex flex-col max-w-[85%] ${m.role === "user" ? "self-end items-end ml-auto" : "self-start items-start mr-auto"}`}>
                        <div className={`text-[10px] uppercase font-bold mb-1 opacity-60 ${m.role === "user" ? "text-right" : "text-left"}`}>
                            {m.role}
                        </div>
                        <div className={`rounded-xl px-5 py-4 text-base leading-relaxed shadow-lg ${m.role === "user"
                            ? "bg-[#ff2a6d] text-white shadow-[#ff2a6d]/10 rounded-tr-sm"
                            : "bg-[#0d0d1a]/80 backdrop-blur-md border border-white/10 rounded-tl-sm"
                            }`}>

                            {/* Render saved thoughts for historical messages */}
                            {m.role === "assistant" && m.thoughts && m.thoughts.length > 0 && (
                                <ThinkingBubble thoughts={m.thoughts} isThinking={false} />
                            )}

                            {/* Dynamic Content Rendering */}
                            <ReactMarkdown
                                components={{
                                    code({ node, inline, className, children, ...props }: any) {
                                        const match = /language-(\w+)/.exec(className || '')
                                        const lang = match ? match[1] : ''

                                        // Chart Rendering Logic
                                        if (!inline && lang === 'json:chart') {
                                            try {
                                                const config = JSON.parse(String(children).replace(/\n$/, ''))
                                                return <ChartRenderer config={config} />
                                            } catch (e) {
                                                return <div className="text-red-400 text-xs p-2 border border-red-400/20 rounded">Invalid Chart Config</div>
                                            }
                                        }

                                        return !inline && match ? (
                                            <SyntaxHighlighter
                                                {...props}
                                                style={oneDark}
                                                language={match[1]}
                                                PreTag="div"
                                            >
                                                {String(children).replace(/\n$/, '')}
                                            </SyntaxHighlighter>
                                        ) : (
                                            <code {...props} className={className}>
                                                {children}
                                            </code>
                                        )
                                    }
                                }}
                            >
                                {m.content}
                            </ReactMarkdown>
                        </div>
                    </div>
                ))}

                {/* ... Empty state ... */}
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center p-10 animate-fade-in">
                        <div className="animate-float mb-6">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-cyan-500 opacity-20 blur-2xl absolute"></div>
                            <div className="relative text-6xl">💬</div>
                        </div>
                        <h3 className="text-4xl font-extrabold mb-4 text-brand-gradient">
                            How can I help you today?
                        </h3>
                        <p className="text-lg text-white/60 max-w-md mb-8">
                            I can answer questions, analyze documents, and provide citations from your knowledge base.
                        </p>
                        <div className="flex flex-wrap gap-3 justify-center max-w-2xl">
                            <button className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm transition-all hover:scale-105">
                                📚 Summarize a document
                            </button>
                            <button className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm transition-all hover:scale-105">
                                🔍 Search knowledge base
                            </button>
                            <button className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm transition-all hover:scale-105">
                                💡 Get insights
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="shrink-0 p-6 bg-[#0d0d1a]/50 backdrop-blur-lg border-t border-white/5 z-10 transition-all">
                <div className="max-w-4xl mx-auto">
                    {/* Reasoner Toggle */}
                    <div className="flex mb-2">
                        <button
                            onClick={() => !streaming && setIsReasoning(!isReasoning)}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all border ${isReasoning
                                ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                                : "bg-white/5 border-white/10 text-white/40 hover:bg-white/10 hover:text-white/60"
                                } ${streaming ? "opacity-50 cursor-not-allowed" : ""}`}
                            disabled={streaming}
                        >
                            {isReasoning ? <Brain size={14} className="animate-pulse" /> : <Brain size={14} />}
                            {isReasoning ? "Reasoning Mode ON" : "Reasoning Mode OFF"}
                        </button>
                    </div>

                    <div className="flex gap-4 p-4 bg-[#0d0d1a] border border-white/10 rounded-xl shadow-lg ring-1 ring-white/5 relative overflow-hidden group">
                        {isReasoning && <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-cyan-400 to-blue-600 opacity-80" />}
                        <input
                            className="flex-1 bg-transparent border-none outline-none text-lg px-2 placeholder:text-white/40"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isReasoning ? "Ask a complex reasoning question..." : "Ask a question..."}
                            onKeyDown={(e) => { if (e.key === "Enter" && !streaming) send(); }}
                            disabled={streaming}
                        />
                        {streaming ? (
                            <button
                                className="px-6 py-2 bg-[#ff2a6d] text-white rounded-lg text-base font-bold flex items-center gap-2 hover:opacity-90 min-h-[48px]"
                                onClick={onStop}
                            >
                                <StopCircle size={18} /> Stop
                            </button>
                        ) : (
                            <button
                                className={`px-6 py-2 rounded-lg text-base font-bold flex items-center gap-2 transition-all min-h-[48px] ${isReasoning
                                    ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25 hover:hue-rotate-15"
                                    : "bg-white text-black hover:bg-gray-200"
                                    } disabled:opacity-50`}
                                onClick={send}
                                disabled={busy}
                            >
                                {busy ? <RefreshCw size={18} className="animate-spin" /> : (isReasoning ? <Sparkles size={18} /> : <ArrowUp size={18} />)}
                                Send
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Answer & Panels Area */}
            {(answer || citations.length > 0 || toolTrace.length > 0 || thoughts.length > 0) && (
                <div className={`shrink-0 border-t border-white/10 bg-[#050510]/50 backdrop-blur-sm overflow-hidden flex flex-col transition-all duration-300 ease-in-out ${panelsOpen ? 'h-[40vh]' : 'h-10'}`}>
                    {/* Panel Controls */}
                    <div
                        className="flex items-center gap-3 px-4 py-2 border-b border-white/5 bg-[#0d0d1a]/80 text-[11px] font-medium text-white/50 shrink-0 cursor-pointer hover:bg-[#0d0d1a]"
                        onClick={() => setPanelsOpen(!panelsOpen)}
                    >
                        <button className="text-white/40 hover:text-white transition-colors">
                            {panelsOpen ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
                        </button>

                        <span className="font-bold uppercase tracking-wider text-white/40">Dashboard</span>

                        {panelsOpen && (
                            <>
                                <div className="h-4 w-px bg-white/10 mx-1" />
                                <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors" onClick={e => e.stopPropagation()}>
                                    <input type="checkbox" className="accent-[#ff2a6d] scale-90" checked={showDeep} onChange={(e) => setShowDeep(e.target.checked)} />
                                    <span>Deep Dive</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors" onClick={e => e.stopPropagation()}>
                                    <input type="checkbox" className="accent-[#ff2a6d] scale-90" checked={showCites} onChange={(e) => setShowCites(e.target.checked)} />
                                    <span>Citations</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors" onClick={e => e.stopPropagation()}>
                                    <input type="checkbox" className="accent-[#ff2a6d] scale-90" checked={showTools} onChange={(e) => setShowTools(e.target.checked)} />
                                    <span>Tools</span>
                                </label>
                            </>
                        )}

                        <div className="ml-auto flex items-center gap-2" onClick={e => e.stopPropagation()}>
                            {retrieval && (
                                <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/5 text-[10px] font-mono">
                                    {retrieval.ms}ms · {retrieval.selected} docs
                                </span>
                            )}
                            <button onClick={onExport} className="flex items-center gap-1 px-2 py-1 rounded-md bg-white/5 hover:bg-white/10 text-white/70 transition-colors">
                                <Download size={10} />
                            </button>
                            {onFullExport && (
                                <button onClick={onFullExport} className="flex items-center gap-1 px-2 py-1 rounded-md bg-[#05d9e8]/10 text-[#05d9e8] hover:bg-[#05d9e8]/20 transition-colors">
                                    <FileText size={10} />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Panels Grid */}
                    <div className="flex-1 overflow-y-auto p-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 h-full">

                            {/* Answer Panel */}
                            <section className="flex flex-col bg-[#0d0d1a]/40 border border-white/5 rounded-xl overflow-hidden h-full min-h-[200px]">
                                <div className="px-3 py-2 border-b border-white/5 bg-[#0d0d1a]/50 font-bold text-[10px] uppercase tracking-wider text-white/30 sticky top-0 flex items-center justify-between">
                                    <span>Answer</span>
                                </div>
                                <div className="p-3 overflow-y-auto flex-1 text-[13px] leading-relaxed space-y-3">

                                    {/* Active Thoughts (Live) */}
                                    {thoughts.length > 0 && streaming && (
                                        <ThinkingBubble thoughts={thoughts} isThinking={true} />
                                    )}

                                    {answer ? (
                                        <>
                                            {streaming && <span className="inline-block w-1.5 h-3 bg-[#ff2a6d] animate-pulse ml-1 align-middle" />}
                                            <div className="prose prose-invert prose-sm max-w-none text-white/90">
                                                <div className="whitespace-pre-wrap font-sans">{shortDeep.short}</div>
                                                {showDeep && shortDeep.deep && (
                                                    <div className="mt-4 pt-4 border-t border-white/5">
                                                        <h4 className="text-[#05d9e8] font-bold text-[10px] uppercase mb-2">Deep Dive</h4>
                                                        <div className="whitespace-pre-wrap text-white/70">{shortDeep.deep}</div>
                                                    </div>
                                                )}
                                            </div>

                                            {audit && (
                                                <div className="mt-4 p-2 rounded-lg border border-[#ff2a6d]/20 bg-[#ff2a6d]/5">
                                                    <div className="flex items-baseline gap-3 text-[11px]">
                                                        <span className="text-[#ff2a6d] font-bold uppercase">Truth Audit</span>
                                                        <span className="text-white/60">Confidence: <b>{audit.score}%</b></span>
                                                        <span className="text-white/60">Grade: <b style={{ color: audit.grade === 'High' ? '#00ef8c' : '#ffac2f' }}>{audit.grade}</b></span>
                                                    </div>
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center h-full text-white/20 text-xs text-center px-4 transition-all">
                                            {busy ? (
                                                agentStatus ? (
                                                    <div className="flex flex-col items-center gap-3 animate-pulse">
                                                        <Brain className="text-purple-400 opacity-80" size={24} />
                                                        <span className="text-purple-300 font-medium tracking-wide">{agentStatus}</span>
                                                    </div>
                                                ) : (
                                                    "Analyzing Knowledge Grid..."
                                                )
                                            ) : (
                                                "Waiting for query..."
                                            )}
                                        </div>
                                    )}
                                </div>
                            </section>

                            {/* Citations Panel */}
                            {showCites && createPanel("Citations", <CitationPanel citations={citations} />)}

                            {/* Tools Panel */}
                            {showTools && createPanel("Tool Trace", <ToolTrace traces={toolTrace} />)}

                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function createPanel(title: string, content: React.ReactNode) {
    return (
        <section className="flex flex-col bg-[#0d0d1a]/40 border border-white/5 rounded-xl overflow-hidden h-full min-h-[200px]">
            <div className="px-3 py-2 border-b border-white/5 bg-[#0d0d1a]/50 font-bold text-[10px] uppercase tracking-wider text-white/30 sticky top-0">
                {title}
            </div>
            <div className="p-0 overflow-y-auto flex-1 text-[13px]">
                {content}
            </div>
        </section>
    )
}
