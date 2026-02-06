import { useState } from "react";
import { Citation } from "../types";

export default function CitationPanel({ citations }: { citations: Citation[] }) {
    const [peek, setPeek] = useState<Citation | null>(null);

    if (!citations.length) return <div className="muted">No citations yet.</div>;

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {citations.map((c) => (
                <div key={c.chunk_id} className="card glass" style={{ padding: "12px", border: "1px solid var(--borderLighter)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "8px" }}>
                        <div>
                            <div style={{ fontWeight: "600", fontSize: "0.9rem", color: "var(--accent2)" }}>
                                {c.title || c.source.split("/").pop()}
                            </div>
                            <div className="muted" style={{ fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "8px" }}>
                                <span>{c.source} · chunk {c.chunk_id}</span>
                                {c.rank_type && (
                                    <span className="pill" style={{
                                        fontSize: "0.6rem",
                                        padding: "2px 6px",
                                        background: c.rank_type === 'hybrid' ? 'rgba(0, 239, 140, 0.1)' :
                                            c.rank_type === 'fts' ? 'rgba(255, 172, 47, 0.1)' :
                                                'rgba(0, 163, 255, 0.1)',
                                        color: c.rank_type === 'hybrid' ? '#00ef8c' :
                                            c.rank_type === 'fts' ? '#ffac2f' :
                                                '#00a3ff',
                                        border: `1px solid ${c.rank_type === 'hybrid' ? 'rgba(0, 239, 140, 0.3)' :
                                                c.rank_type === 'fts' ? 'rgba(255, 172, 47, 0.3)' :
                                                    'rgba(0, 163, 255, 0.3)'
                                            }`
                                    }}>
                                        {c.rank_type.toUpperCase()}
                                    </span>
                                )}
                            </div>
                        </div>
                        <button
                            className="btn"
                            style={{ padding: "4px 8px", fontSize: "0.7rem", minWidth: "auto" }}
                            onClick={() => setPeek(c)}
                        >
                            Peek
                        </button>
                    </div>
                    <div className="cardBody" style={{ fontSize: "0.85rem", opacity: 0.8, display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                        {c.snippet}
                    </div>
                </div>
            ))}

            {peek && (
                <div className="modal-overlay" style={{
                    position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
                    background: "rgba(0,0,0,0.7)", backdropFilter: "blur(4px)",
                    display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
                    padding: "20px"
                }} onClick={() => setPeek(null)}>
                    <div className="card glass" style={{
                        maxWidth: "800px", width: "100%", maxHeight: "80vh", overflowY: "auto",
                        padding: "24px", position: "relative", boxShadow: "0 20px 50px rgba(0,0,0,0.5)"
                    }} onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                            <h3 style={{ margin: 0 }}>Source Explorer</h3>
                            <button className="btn" onClick={() => setPeek(null)}>Close</button>
                        </div>
                        <div style={{ marginBottom: "16px" }}>
                            <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "4px" }}>Source Path</div>
                            <code style={{ fontSize: "0.9rem", color: "var(--accent1)" }}>{peek.source}</code>
                        </div>
                        <div style={{ background: "rgba(0,0,0,0.3)", padding: "16px", borderRadius: "8px", border: "1px solid var(--borderLighter)" }}>
                            <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "12px", borderBottom: "1px solid var(--borderLighter)", paddingBottom: "8px" }}>
                                Full Context Chunk ({peek.chunk_id})
                            </div>
                            <div style={{ whiteSpace: "pre-wrap", fontSize: "0.95rem", lineHeight: "1.6", fontFamily: "inherit" }}>
                                {peek.text || peek.snippet}
                            </div>
                        </div>
                        <div style={{ marginTop: "20px", textAlign: "right" }}>
                            <button className="btn primary" onClick={() => setPeek(null)}>Got it</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
