"use client";

import { useState, useEffect } from "react";
import { API_BASE } from "../constants";
import { useAuth } from "../context/AuthContext";
import LoadingSpinner from "./LoadingSpinner";

const TOOLS_LIST = [
    { id: "powerbi.pbi_tools", name: "Power BI Pro Tools", description: "Schema Parser, Data Dictionary, Calc Groups" },
    { id: "powerbi.star_schema_validator", name: "Star Schema Validator", description: "Audit model for bi-directional filters & risks" },
    { id: "d365fo.set_based_wizard", name: "Set-Based Wizard", description: "Refactor while select to update_recordset" },
    { id: "d365fo.coc_scaffold", name: "CoC Scaffolder", description: "Generate best-practice X++ extensions" },
    { id: "d365fo.d365_metadata", name: "D365FO Metadata & Trace", description: "Table Metadata, Trace Parser, SysOps Scaffolder" },
    { id: "d365fo.project_primer", name: "D365FO Project Primer", description: "Prime JGPT with your project's custom objects" },
    { id: "powerbi.model_primer", name: "Power BI Model Primer", description: "Inject model schema into JGPT persistent memory" },
];

const PRESETS: Record<string, string> = {
    "powerbi.pbi_tools": '{"model": {"tables": [{"name": "Sales", "columns": [], "measures": []}]}}',
    "powerbi.star_schema_validator": '{"model": {"relationships": [{"fromTable": "Sales", "toTable": "Product", "crossFilteringBehavior": "bothDirections"}]}}',
    "d365fo.set_based_wizard": 'while select forupdate custTable\n{\n    custTable.CreditMax = 5000;\n    custTable.update();\n}',
    "d365fo.coc_scaffold": "// Method: insert on CustTable",
    "d365fo.project_primer": '{"project_name": "MyExtension", "objects": ["CustTable.Extension", "SalesLine.Extension"], "description": "Core sales extensions"}',
    "powerbi.model_primer": '{"model_name": "Sales Model", "bim_content": "{...}"}'
};

export default function WorkbenchPanel() {
    const { token } = useAuth();
    const [selectedTool, setSelectedTool] = useState(TOOLS_LIST[0].id);
    const [recentlyUsed, setRecentlyUsed] = useState<string[]>([]);
    const [activeContext, setActiveContext] = useState<string[]>([]); // To be populated from backend check

    function handleToolSelect(id: string) {
        setSelectedTool(id);
        if (PRESETS[id]) setInput(PRESETS[id]);

        // Track usage
        setRecentlyUsed(prev => {
            const next = [id, ...prev.filter(x => x !== id)];
            return next.slice(0, 3);
        });
    }
    const [input, setInput] = useState("");
    const [action, setAction] = useState("");
    const [output, setOutput] = useState<any>(null);
    const [busy, setBusy] = useState(false);
    const [executionStatus, setExecutionStatus] = useState<"idle" | "executing" | "success" | "error">("idle");

    useEffect(() => {
        // Heuristic: Check for primer files in public folder or via specialized endpoint
        // In this mock setup, we'll just simulate detection
        // In a real app, this would be an API call like /api/tools/context-status
        setTimeout(() => {
            setActiveContext(["D365FO", "PowerBI"]);
        }, 1000);
    }, []);

    async function runTool() {
        if (!token) {
            alert("Authentication Required: Please log in to execute tools.");
            return;
        }
        setBusy(true);
        setExecutionStatus("executing");
        setOutput(null);

        // Heuristic to set action if not specified
        let toolInput: any = { action };
        if (selectedTool.includes("pbi_tools")) {
            if (input.includes("{")) {
                toolInput.bim_content = input;
                if (!action) toolInput.action = "parse_schema";
            } else {
                toolInput.action = action || "calc_group_scaffold";
            }
        } else if (selectedTool.includes("d365_metadata")) {
            if (input.startsWith("SQL statement:")) {
                toolInput.trace_text = input;
                toolInput.action = "trace_parser";
            } else {
                toolInput.table_name = input;
                toolInput.action = action || "metadata_lookup";
            }
        } else if (selectedTool.includes("primer")) {
            try {
                toolInput = JSON.parse(input);
            } catch {
                toolInput = { error: "Primer requires valid JSON input" };
            }
        } else {
            toolInput = { ...toolInput, dax: input, code: input };
        }

        try {
            const r = await fetch(`${API_BASE}/tools/execute`, {
                method: "POST",
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                body: JSON.stringify({ tool_name: selectedTool, input: toolInput })
            });

            if (r.status === 401) {
                alert("Session Expired: Please log in again.");
                setExecutionStatus("error");
                setOutput({ error: "Unauthorized: Session expired or invalid." });
                return;
            }

            if (!r.ok) {
                const text = await r.text();
                setOutput({ error: `Execution failed (${r.status})`, detail: text });
                setExecutionStatus("error");
                return;
            }

            const j = await r.json();
            setOutput(j);
            setExecutionStatus("success");
        } catch (e) {
            console.error("Tool execution error:", e);
            setOutput({ error: "Execution failed: Network error or server unreachable." });
            setExecutionStatus("error");
        } finally {
            setBusy(false);
        }
    }

    return (
        <div className="p-8 max-w-6xl mx-auto h-full flex flex-col gap-6">
            <div className="flex flex-col gap-2">
                <h2 className="text-3xl font-extrabold text-brand-gradient">Developer Workbench</h2>
                <div className="flex items-center gap-4">
                    <p className="text-white/50">Execute specialized developer tools directly on your data.</p>
                    <div className="flex gap-2">
                        {activeContext.includes("D365FO") && <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 text-[10px] font-bold border border-blue-500/30 uppercase">D365FO Primed</span>}
                        {activeContext.includes("PowerBI") && <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 text-[10px] font-bold border border-purple-500/30 uppercase">PBI Primed</span>}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 min-h-0">
                {/* Configuration side */}
                <div className="flex flex-col gap-6">
                    {recentlyUsed.length > 0 && (
                        <div className="panel-card p-6 flex flex-col gap-4">
                            <label className="text-xs font-bold text-white/40 uppercase tracking-widest">Recently Used</label>
                            <div className="flex flex-wrap gap-2">
                                {recentlyUsed.map(id => (
                                    <button
                                        key={id}
                                        onClick={() => handleToolSelect(id)}
                                        className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 text-[11px] hover:bg-white/10 text-white/80"
                                    >
                                        {TOOLS_LIST.find(t => t.id === id)?.name.split(' ')[0]}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="panel-card p-6 flex flex-col gap-4">
                        <label className="text-xs font-bold text-white/40 uppercase tracking-widest">Select Tool</label>
                        <div className="flex flex-col gap-2">
                            {TOOLS_LIST.map(t => (
                                <button
                                    key={t.id}
                                    onClick={() => handleToolSelect(t.id)}
                                    className={`text-left p-4 rounded-xl border transition-all ${selectedTool === t.id
                                        ? "bg-white/10 border-blue-500/50 shadow-lg shadow-blue-500/10"
                                        : "bg-white/5 border-white/5 hover:bg-white/8 text-white/60"
                                        }`}
                                >
                                    <div className="font-bold text-sm text-white">{t.name}</div>
                                    <div className="text-xs opacity-50">{t.description}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="panel-card p-6 flex flex-col gap-4">
                        <label className="text-xs font-bold text-white/40 uppercase tracking-widest">Action (Optional)</label>
                        <input
                            type="text"
                            value={action}
                            onChange={e => setAction(e.target.value)}
                            placeholder="e.g. parse_schema, trace_parser"
                            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500/50"
                        />
                    </div>

                    <div className="panel-card p-6 flex flex-col gap-4 border-blue-500/20 bg-blue-500/5">
                        <label className="text-xs font-bold text-blue-400/60 uppercase tracking-widest">Execution Control</label>
                        <button
                            onClick={runTool}
                            disabled={busy || !token}
                            className={`btn-primary py-4 rounded-xl font-bold flex items-center justify-center gap-2 shadow-xl transition-all duration-300 ${!token ? 'opacity-50 cursor-not-allowed grayscale' :
                                executionStatus === 'success' ? 'shadow-green-500/30 border-green-500/50 hover:shadow-green-500/50 bg-green-500/10' :
                                    executionStatus === 'error' ? 'shadow-red-500/30 border-red-500/50 hover:shadow-red-500/50 bg-red-500/10' :
                                        executionStatus === 'executing' ? 'shadow-blue-500/40 border-blue-500/60 animate-pulse' :
                                            'shadow-blue-500/20'
                                }`}
                        >
                            {!token && "🔒 Login Required"}
                            {token && executionStatus === 'executing' && (
                                <>
                                    <LoadingSpinner size="sm" />
                                    <span>⚙️ Processing...</span>
                                </>
                            )}
                            {executionStatus === 'success' && "✅ Success! Re-run"}
                            {executionStatus === 'error' && "❌ Error - Retry"}
                            {executionStatus === 'idle' && "⚡ Execute Tool"}
                        </button>
                    </div>
                </div>

                {/* Input/Output side */}
                <div className="lg:col-span-2 flex flex-col gap-6 min-h-0">
                    <div className="flex-1 flex flex-col gap-2 min-h-0">
                        <label className="text-xs font-bold text-white/40 uppercase tracking-widest px-1">Raw Input (JSON / Text / SQL Trace)</label>
                        <textarea
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            className="flex-1 bg-[#030307]/50 border border-white/10 rounded-2xl p-6 text-sm font-mono focus:outline-none focus:border-blue-500/30 resize-none overflow-auto"
                            placeholder="Paste your .bim content, DAX, or SQL trace output here..."
                        />
                    </div>

                    <div className="flex-1 flex flex-col gap-2 min-h-0">
                        <label className="text-xs font-bold text-white/40 uppercase tracking-widest px-1">Execution Output</label>
                        <div className="flex-1 bg-[#030307]/80 border border-white/5 rounded-2xl p-6 overflow-auto relative">
                            {output ? (
                                <pre className="text-sm font-mono text-blue-300">
                                    {JSON.stringify(output, null, 2)}
                                </pre>
                            ) : busy ? (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <LoadingSpinner size="lg" text="Processing..." />
                                </div>
                            ) : (
                                <div className="h-full flex items-center justify-center text-white/20 italic">
                                    Output will appear here after execution.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
