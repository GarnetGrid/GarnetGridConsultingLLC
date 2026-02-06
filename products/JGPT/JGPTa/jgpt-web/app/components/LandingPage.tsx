import Link from "next/link";
import { DEPARTMENTS, MODES } from "../constants";

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-[#030307] text-white overflow-hidden relative selection:bg-purple-500/30">
            {/* Background Gradients */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] rounded-full bg-blue-600/10 blur-[150px] animate-pulse" style={{ animationDuration: '8s' }} />
                <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-purple-600/10 blur-[150px] animate-pulse" style={{ animationDuration: '10s', animationDelay: '1s' }} />
            </div>

            {/* Navigation */}
            <nav className="relative z-50 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-lg shadow-lg shadow-purple-500/20">
                        J
                    </div>
                    <span className="font-bold text-xl tracking-tight">JGPT</span>
                </div>
                <Link href="/login" className="px-5 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-medium transition-all hover:scale-105 backdrop-blur-md">
                    Sign In
                </Link>
            </nav>

            {/* Hero Section */}
            <main className="relative z-10 flex flex-col items-center justify-center pt-20 pb-32 px-4 text-center max-w-5xl mx-auto">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-widest mb-8 animate-fade-in-up">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                    System Operational
                </div>

                <h1 className="text-6xl md:text-8xl font-black mb-6 tracking-tighter leading-tight animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                    <span className="bg-gradient-to-r from-white via-white to-gray-400 bg-clip-text text-transparent">Garnet Grid</span>
                    <br />
                    <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">AI Engine</span>
                </h1>

                <p className="text-lg md:text-xl text-gray-400 max-w-2xl mb-12 leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                    Access enterprise-grade intelligence. Unified orchestration for Power BI, Dynamics 365, and Data Architecture.
                </p>

                <Link href="/login" className="group relative px-8 py-4 bg-white text-black rounded-full font-bold text-lg hover:scale-105 transition-all duration-300 shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_-15px_rgba(255,255,255,0.5)] animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                    <span className="relative z-10 flex items-center gap-2">
                        Enter Workspace
                        <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
                    </span>
                </Link>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32 w-full animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
                    {MODES.slice(0, 3).map((mode) => (
                        <div key={mode.value} className="group p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 hover:bg-white/10 transition-all text-left backdrop-blur-sm">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-white/10 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">
                                {mode.icon}
                            </div>
                            <h3 className="text-lg font-bold mb-2 text-white">{mode.label}</h3>
                            <p className="text-sm text-gray-400">{mode.description}</p>
                        </div>
                    ))}
                </div>

                {/* Footer Stats */}
                <div className="mt-24 pt-8 border-t border-white/5 w-full flex flex-col md:flex-row justify-between items-center text-gray-500 text-sm">
                    <div>© 2026 Garnet Grid Consulting</div>
                    <div className="flex gap-8 mt-4 md:mt-0">
                        <div className="flex flex-col items-center md:items-start">
                            <span className="text-white font-bold text-lg">99.9%</span>
                            <span className="text-xs uppercase tracking-wider">Uptime</span>
                        </div>
                        <div className="flex flex-col items-center md:items-start">
                            <span className="text-white font-bold text-lg">Secure</span>
                            <span className="text-xs uppercase tracking-wider">Encryption</span>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
