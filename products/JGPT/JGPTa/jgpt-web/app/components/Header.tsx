import { DEPARTMENTS, MODES } from "../constants";
import CustomDropdown from "./CustomDropdown";
import { Plus, X } from "lucide-react";
import ModelSelector from "./ModelSelector";
import ModelSettings from "./ModelSettings";
import ThemeToggle from "./ThemeToggle";

interface HeaderProps {
    tab: "chat" | "evals" | "knowledge" | "admin" | "workbench";
    onTabChange?: (t: "chat" | "evals" | "knowledge" | "admin" | "workbench") => void;
    mode?: string;
    onModeChange?: (m: string) => void;
    model?: string;
    onModelChange?: (m: string) => void;
    modelOptions?: { temperature?: number; num_ctx?: number };
    onModelOptionsChange?: (opts: { temperature?: number; num_ctx?: number }) => void;
    dept?: string | string[];
    onDeptChange?: (d: string | string[]) => void;
    role?: "admin" | "viewer";
    showIngest?: boolean;
    onToggleIngest?: () => void;
}



export default function Header({
    tab, onTabChange,
    mode, onModeChange,
    model, onModelChange,
    modelOptions, onModelOptionsChange,
    dept, onDeptChange,
    role,
    showIngest,
    onToggleIngest
}: HeaderProps) {
    return (
        <header className="h-16 shrink-0 border-b border-white/5 bg-[#030307]/80 backdrop-blur-md flex items-center justify-between px-6 z-50 sticky top-0">
            {/* Left: Branding */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-cyan-500 flex items-center justify-center font-bold text-white shadow-lg">
                        J
                    </div>
                    <div>
                        <h1 className="text-2xl font-extrabold text-brand-gradient leading-none">JGPT</h1>
                        <p className="text-xs text-white/50 leading-none mt-0.5">Garnet Grid AI Engine</p>
                    </div>
                </div>
            </div>

            <div className="flex bg-[#141428]/60 p-1 rounded-full border border-white/5">
                {(["chat", "evals", "knowledge", "workbench", "admin"] as const).map((t) => {
                    if (t === "admin" && role !== "admin") return null;
                    const isActive = tab === t;
                    return (
                        <button
                            key={t}
                            onClick={() => onTabChange?.(t)}
                            className={`px-4 py-1.5 rounded-full text-[11px] font-bold transition-all ${isActive
                                ? "bg-white text-black shadow-md shadow-black/20"
                                : "text-white/40 hover:text-white/80 hover:bg-white/5"
                                }`}
                        >
                            {t.charAt(0).toUpperCase() + t.slice(1)}
                        </button>
                    )
                })}
            </div>

            <div className="flex items-center gap-3">
                <CustomDropdown
                    value={dept || "all"}
                    onChange={(v) => onDeptChange?.(Array.isArray(v) ? v : [v])}
                    options={DEPARTMENTS}
                    borderColor="#05d9e8"
                    label="Department"
                    multiSelect={true}
                    showRecent={true}
                />
                <CustomDropdown
                    value={mode || "powerbi"}
                    onChange={(v) => onModeChange?.(v as string)}
                    options={MODES}
                    label="Mode"
                    showRecent={true}
                />
                <ModelSelector
                    value={model || "llama3.2"}
                    onChange={(v) => onModelChange?.(v)}
                    persona={Array.isArray(dept) ? dept[0] : (dept || "powerbi")}
                />

                <ModelSettings
                    options={modelOptions || {}}
                    onChange={(opts) => onModelOptionsChange?.(opts)}
                />

                {/* Theme Toggle */}
                <ThemeToggle />

                {/* Add Knowledge Button */}
                <button
                    onClick={onToggleIngest}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-2 border ${showIngest
                        ? 'bg-white/10 text-white border-white/20 hover:bg-white/15'
                        : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white border-transparent hover:from-purple-500 hover:to-pink-500 shadow-lg shadow-purple-500/25'
                        }`}
                >
                    {showIngest ? (
                        <>
                            <X size={14} />
                            Close
                        </>
                    ) : (
                        <>
                            <Plus size={14} />
                            Add Knowledge
                        </>
                    )}
                </button>
            </div>
        </header>
    );
}
