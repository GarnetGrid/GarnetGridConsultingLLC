"use client";

import { EvalReport } from "../types";
import LoadingSpinner from "./LoadingSpinner";

interface EvalsPanelProps {
    busy: boolean;
    runEvals: () => void;
    ingestWebKB: () => void;
    loadLatestEval: () => void;
    report: EvalReport | null;
}

export default function EvalsPanel({ busy, runEvals, ingestWebKB, loadLatestEval, report }: EvalsPanelProps) {
    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 mb-6">
                <button
                    className="btn-primary px-6 py-3 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105"
                    onClick={runEvals}
                    disabled={busy}
                >
                    {busy ? "Running Suite..." : "🚀 Run Full Eval Suite"}
                </button>
                <button
                    className="btn px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all"
                    onClick={loadLatestEval}
                >
                    📂 Load Latest Report
                </button>
                <button
                    className="btn px-6 py-3 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    onClick={ingestWebKB}
                    disabled={busy}
                >
                    {busy ? "Updating..." : "🌐 Sync Web Knowledge"}
                </button>
            </div>

            {/* Results Table */}
            {report && (
                <div className="panel-card overflow-hidden">
                    {/* Table Header */}
                    <div className="bg-blue-500/10 px-6 py-4 border-b border-white/10">
                        <h3 className="font-semibold text-lg">Evaluation Results: {report.suite}</h3>
                    </div>

                    {/* Table Container with Horizontal Scroll */}
                    <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                            <thead>
                                <tr className="bg-white/5 text-left border-b border-white/10">
                                    <th className="px-6 py-4 text-sm font-semibold text-white/80">Mode</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-white/80">Question</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-white/80">Grade</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-white/80">Confidence</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-white/80">Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(report.runs || []).map((run, idx) => {
                                    const grade = run.judge?.grade || "N/A";
                                    const gradeColorClass =
                                        grade === "A" ? "text-green-500" :
                                            grade === "B" ? "text-blue-500" :
                                                grade === "C" ? "text-yellow-500" :
                                                    "text-red-500";

                                    return (
                                        <tr key={idx} className="border-t border-white/5 hover:bg-white/5 transition-colors">
                                            <td className="px-6 py-4">
                                                <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-medium">
                                                    {run.mode}
                                                </span>
                                            </td>
                                            <td
                                                className="px-6 py-4 max-w-md truncate text-sm"
                                                title={run.question}
                                            >
                                                {run.question}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`font-bold text-lg ${gradeColorClass}`}>
                                                    {grade}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm text-white/70">
                                                {((run.judge?.confidence || 0) * 100).toFixed(0)}%
                                            </td>
                                            <td className="px-6 py-4 text-sm text-white/70">
                                                {run.judge?.total || 0}/{run.judge?.max || 0}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!report && !busy && (
                <div className="text-center py-20 text-white/40">
                    <div className="text-6xl mb-4">📊</div>
                    <p className="text-lg">No evaluation data loaded.</p>
                    <p className="text-sm mt-2">Run the suite to see performance analytics.</p>
                </div>
            )}

            {/* Loading State */}
            {busy && !report && (
                <div className="flex items-center justify-center py-20">
                    <LoadingSpinner size="lg" text="Running evaluations..." />
                </div>
            )}
        </div>
    );
}
