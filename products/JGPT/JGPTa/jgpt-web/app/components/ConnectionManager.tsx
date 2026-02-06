"use client";

import { useState, useEffect } from "react";
import { Plus, Trash, Database, CheckCircle, XCircle, RefreshCw } from "lucide-react";

interface Connection {
    id: number;
    name: string;
    type: string;
    host: string;
    port: number;
    database: string;
    username: string;
    is_active: boolean;
}

export default function ConnectionManager() {
    const [connections, setConnections] = useState<Connection[]>([]);
    const [loading, setLoading] = useState(true);
    const [testing, setTesting] = useState<number | null>(null);
    const [testResult, setTestResult] = useState<{ id: number, success: boolean, msg: string } | null>(null);
    const [showForm, setShowForm] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        name: "",
        type: "postgres",
        host: "",
        port: 5432,
        database: "",
        username: "",
        password: ""
    });

    const fetchConnections = async () => {
        setLoading(true);
        try {
            const r = await fetch("/api/connections", {
                headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` } // Assuming token is stored
            });
            if (r.ok) setConnections(await r.json());
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConnections();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const r = await fetch("/api/connections", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(formData)
            });
            if (r.ok) {
                setShowForm(false);
                setFormData({ name: "", type: "postgres", host: "", port: 5432, database: "", username: "", password: "" });
                fetchConnections();
            } else {
                alert("Failed to create connection");
            }
        } catch (e) {
            alert("Error creating connection");
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure you want to delete this connection?")) return;
        try {
            const r = await fetch(`/api/connections/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
            });
            if (r.ok) fetchConnections();
        } catch (e) {
            alert("Delete failed");
        }
    };

    const handleTest = async (id: number) => {
        setTesting(id);
        setTestResult(null);
        try {
            const r = await fetch(`/api/connections/${id}/test`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
            });
            const j = await r.json();
            setTestResult({ id, success: r.ok, msg: j.message || j.detail });
        } catch (e) {
            setTestResult({ id, success: false, msg: "Network error" });
        } finally {
            setTesting(null);
        }
    };

    return (
        <div className="bg-[#0d0d1a]/50 border border-white/5 rounded-xl p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <Database className="text-blue-400" size={20} />
                    Data Connections
                </h3>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="btn btn-primary flex items-center gap-2 text-sm"
                >
                    <Plus size={16} /> New Connection
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleCreate} className="mb-8 p-4 bg-[#0d0d1a] border border-white/10 rounded-lg space-y-4 animate-fade-in">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Name</label>
                            <input required className="input-field" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Sales DB" />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Type</label>
                            <select className="input-field" value={formData.type} onChange={e => setFormData({ ...formData, type: e.target.value })}>
                                <option value="postgres">PostgreSQL</option>
                                <option value="mssql">SQL Server</option>
                                <option value="mysql">MySQL</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Host</label>
                            <input required className="input-field" value={formData.host} onChange={e => setFormData({ ...formData, host: e.target.value })} placeholder="localhost" />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Port</label>
                            <input type="number" required className="input-field" value={formData.port} onChange={e => setFormData({ ...formData, port: parseInt(e.target.value) })} />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Database</label>
                            <input required className="input-field" value={formData.database} onChange={e => setFormData({ ...formData, database: e.target.value })} />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Username</label>
                            <input required className="input-field" value={formData.username} onChange={e => setFormData({ ...formData, username: e.target.value })} />
                        </div>
                        <div className="col-span-2">
                            <label className="block text-xs font-bold text-white/40 uppercase mb-1">Password</label>
                            <input type="password" required className="input-field" value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })} />
                        </div>
                    </div>
                    <div className="flex justify-end gap-2 pt-2">
                        <button type="button" onClick={() => setShowForm(false)} className="px-3 py-2 rounded hover:bg-white/10 text-sm">Cancel</button>
                        <button type="submit" className="btn btn-primary text-sm">Save Connection</button>
                    </div>
                </form>
            )}

            {loading ? (
                <div className="text-center text-white/30 py-8">Loading connections...</div>
            ) : (
                <div className="space-y-3">
                    {connections.length === 0 && (
                        <div className="text-center text-white/30 py-8 italic">No connections configured.</div>
                    )}
                    {connections.map(c => (
                        <div key={c.id} className="flex items-center justify-between p-4 bg-[#0d0d1a] border border-white/5 rounded-lg hover:border-white/20 transition-all">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded bg-blue-500/20 flex items-center justify-center">
                                    <Database size={20} className="text-blue-400" />
                                </div>
                                <div>
                                    <div className="font-bold text-white/90">{c.name}</div>
                                    <div className="text-xs text-white/50 font-mono">{c.type}://{c.username}@{c.host}:{c.port}/{c.database}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {testResult && testResult.id === c.id && (
                                    <span className={`text-xs font-bold px-2 py-1 rounded ${testResult.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                        {testResult.msg}
                                    </span>
                                )}
                                <button
                                    onClick={() => handleTest(c.id)}
                                    disabled={testing === c.id}
                                    className="p-2 hover:bg-white/10 rounded text-white/70 hover:text-white transition-colors"
                                    title="Test Connection"
                                >
                                    {testing === c.id ? <RefreshCw className="animate-spin" size={16} /> : <CheckCircle size={16} />}
                                </button>
                                <button
                                    onClick={() => handleDelete(c.id)}
                                    className="p-2 hover:bg-red-500/20 rounded text-red-400/70 hover:text-red-400 transition-colors"
                                    title="Delete Connection"
                                >
                                    <Trash size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
