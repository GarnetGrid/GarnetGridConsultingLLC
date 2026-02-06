"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { useAuth } from "./context/AuthContext";
import { Conv, Msg, Citation, ToolRun, ChatResp, EvalReport, KBSource, KBStats, ThoughtProp } from "./types";
import { API_BASE } from "./constants";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import EvalsPanel from "./components/EvalsPanel";
import IngestionPanel from "./components/IngestionPanel";
import SourcesDashboard from "./components/SourcesDashboard";
import AdminPanel from "./components/AdminPanel";
import WorkbenchPanel from "./components/WorkbenchPanel";

import LandingPage from "./components/LandingPage";

function HomeContent() {
  const { token, user, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // No auto-redirect here anymore

  const initialTab = (searchParams.get("tab") as any) || "chat";
  const [tab, setTab] = useState<"chat" | "evals" | "knowledge" | "admin" | "workbench">(initialTab);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#030307] text-white">
        <div className="text-xl animate-pulse text-blue-400 font-medium">Loading JGPT...</div>
      </div>
    );
  }

  // If no token, show Public Landing Page
  if (!token) {
    return <LandingPage />;
  }

  const [mode, setMode] = useState<"powerbi" | "d365fo">("powerbi");
  const [dept, setDept] = useState<string | string[]>("all");
  const [model, setModel] = useState<string>("llama3.2");
  const [modelOptions, setModelOptions] = useState<{ temperature?: number; num_ctx?: number }>({ temperature: 0.7, num_ctx: 4096 });
  const [kbSources, setKbSources] = useState<KBSource[]>([]);
  const [kbStats, setKbStats] = useState<KBStats | null>(null);
  const [input, setInput] = useState<string>("");

  const [convs, setConvs] = useState<Conv[]>([]);
  const [activeId, setActiveId] = useState<number | undefined>(undefined);
  const [messages, setMessages] = useState<Msg[]>([]);

  const [busy, setBusy] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [answer, setAnswer] = useState<string>("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [thoughts, setThoughts] = useState<ThoughtProp[]>([]);
  const [toolTrace, setToolTrace] = useState<ToolRun[]>([]);
  const [retrieval, setRetrieval] = useState<any>(null);
  const [quality, setQuality] = useState<any>(null);
  const [audit, setAudit] = useState<any>(null);
  const [agentStatus, setAgentStatus] = useState<string>("");
  const [doGrade, setDoGrade] = useState<boolean>(false);
  const [evalReport, setEvalReport] = useState<EvalReport | null>(null);

  const [showCites, setShowCites] = useState(true);
  const [showTools, setShowTools] = useState(true);
  const [showDeep, setShowDeep] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false); // Sidebar visible by default
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [convsLoading, setConvsLoading] = useState(false);

  const [showIngest, setShowIngest] = useState(false);
  const [projectContext, setProjectContext] = useState<string>("");

  const [isReasoning, setIsReasoning] = useState(false);

  async function refreshConvs() {
    if (!token) return;
    setConvsLoading(true);
    try {
      const r = await fetch(`${API_BASE}/conversations`, { headers: { Authorization: `Bearer ${token}` } });
      if (r.status === 401) {
        alert("Session Expired: Please log in again.");
        return;
      }
      if (!r.ok) return;
      const j = await r.json();
      setConvs(j || []);
    } finally {
      setConvsLoading(false);
    }
  }

  async function loadConv(id: number) {
    if (!token) return;
    const r = await fetch(`${API_BASE}/conversations/${id}`, { headers: { Authorization: `Bearer ${token}` } });
    if (!r.ok) return;
    const j = await r.json();
    setActiveId(id);
    setMode((j.mode || "powerbi") as any);
    setModel(j.model || "llama3.2");
    setMessages(j.messages || []);
    // reset per-turn panels
    setAnswer("");
    setCitations([]);
    setToolTrace([]);
    setRetrieval(null);
  }

  async function refreshKB() {
    if (!token) return;
    try {
      const resSources = await fetch(`${API_BASE}/kb/sources`, { headers: { Authorization: `Bearer ${token}` } });
      const resStats = await fetch(`${API_BASE}/kb/stats`, { headers: { Authorization: `Bearer ${token}` } });
      if (resSources.ok) setKbSources(await resSources.json());
      if (resStats.ok) setKbStats(await resStats.json());
    } catch (e) {
      console.error("KB refresh failed", e);
    }
  }

  useEffect(() => {
    if (token) {
      refreshConvs();
      refreshKB();
    }
  }, [token]);

  async function send() {
    const msg = input.trim();
    if (!msg || busy) return;
    setBusy(true);
    setStreaming(true);
    setInput("");

    setMessages(prev => [...prev, { id: Date.now(), role: "user", content: msg, created_at: new Date().toISOString() }]);

    // Reset loop state
    setAnswer("");
    setCitations([]);
    setThoughts([]);
    setToolTrace([]);
    setRetrieval(null);
    setQuality(null);
    setAudit(null);
    setAgentStatus("");

    const body = {
      persona: mode,
      model,
      options: modelOptions,
      message: msg,
      conversation_id: activeId,
      grade: doGrade,
      project_context: projectContext,
      department: dept
    };

    // Create abort controller for cancellation
    const controller = new AbortController();
    setAbortController(controller);

    try {
      // Choose endpoint based on mode
      const endpoint = isReasoning ? `${API_BASE}/reason/chat` : `${API_BASE}/chat`;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
        signal: controller.signal
      });

      if (response.status === 401) {
        alert("Session Expired: Please log in again.");
        setBusy(false);
        setStreaming(false);
        return;
      }

      if (!response.ok) {
        alert("Chat failure: " + response.statusText);
        setBusy(false);
        setStreaming(false);
        return;
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedAnswer = "";

      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "metadata") {
                if (!activeId && data.conversation_id) {
                  setActiveId(data.conversation_id);
                  refreshConvs();
                }
                setCitations(data.citations || []);
                setRetrieval(data.retrieval || null);
              } else if (data.type === "thought") {
                // Handle both old plain-text thoughts and new structural thoughts
                const content = data.content || data.text;
                if (content) {
                  setAgentStatus("Thinking...");
                  setThoughts(prev => [...prev, { type: 'thought', content }]);
                }
              } else if (data.type === "tool_call") {
                setThoughts(prev => [...prev, { type: 'tool_call', tool: data.tool, input: data.input }]);
                setAgentStatus(`Executing ${data.tool}...`);
              } else if (data.type === "tool_result") {
                setThoughts(prev => [...prev, { type: 'tool_result', result: data.result }]);
              } else if (data.type === "tool") {
                // Legacy tool trace from main chat
                setToolTrace(prev => [...prev, data]);
              } else if (data.type === "answer") {
                // Reasoner sends { type: 'answer', content: '...' }
                // Regular chat sends { type: 'answer', chunk: '...' }
                const text = data.content || data.chunk || "";
                accumulatedAnswer += text;
                setAnswer(accumulatedAnswer);
              } else if (data.type === "audit") {
                setAudit(data.report || null);
              } else if (data.type === "done") {
                setQuality(data.quality || null);
                setStreaming(false);
                setAgentStatus("");
              } else if (data.error) {
                alert("Error: " + data.error);
              }
            } catch (e) {
              console.error("Failed to parse SSE line", line, e);
            }
          }
        }
      }

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: "assistant",
        content: accumulatedAnswer,
        created_at: new Date().toISOString(),
        thoughts: thoughts // Save final thoughts with message
      }]);

    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('Stream cancelled by user');
        // Add partial response to messages if any
        if (answer) {
          setMessages(prev => [...prev, {
            id: Date.now() + 1,
            role: "assistant",
            content: answer + " [Generation stopped]",
            created_at: new Date().toISOString()
          }]);
        }
      } else {
        console.error(err);
        alert("Stream error: " + err);
      }
    } finally {
      setBusy(false);
      setStreaming(false);
      setAgentStatus("");
      setAbortController(null);
    }
  }

  function stopGeneration() {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
  }


  async function ingestWebKB() {
    setBusy(true);
    const r = await fetch(`${API_BASE}/ingest/web`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    const txt = await r.text();
    setBusy(false);
    if (!r.ok) {
      alert(`Web ingest failed: ${r.status}\n\n${txt}`);
      return;
    }
    alert("Web KB fetched + ingested. You can start chatting with fresher citations.");
  }

  async function runEvals() {
    setBusy(true);
    setEvalReport(null); // Clear previous report
    const r = await fetch(`${API_BASE}/eval`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ suite: "default" }) });
    if (!r.ok) {
      const t = await r.text();
      alert(`Eval error: ${r.status}\n\n${t}`);
      setBusy(false);
      return;
    }
    const j = await r.json();
    setEvalReport(j as EvalReport);
    setBusy(false);
    alert("Eval suite finished. Results displayed below.");
  }

  async function loadLatestEval() {
    const r = await fetch(`${API_BASE}/eval/latest`, { headers: { Authorization: `Bearer ${token}` } });
    if (!r.ok) { alert("No eval report yet."); return; }
    const j = await r.json();
    if (!j.ok) { alert(j.error || "No eval report yet."); return; }
    setEvalReport(j as EvalReport);
  }

  function newConv() {
    setActiveId(undefined);
    setMessages([]);
    setAnswer("");
    setCitations([]);
    setToolTrace([]);
    setRetrieval(null);
    setAudit(null);
    refreshConvs();
  }

  async function deleteConv(id: number) {
    const r = await fetch(`${API_BASE}/conversations/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) {
      if (activeId === id) {
        setActiveId(undefined);
        setMessages([]);
      }
      refreshConvs();
    } else {
      alert("Delete failed.");
    }
  }

  async function exportThread() {
    if (!activeId) return;
    setBusy(true);
    const r = await fetch(`${API_BASE}/conversations/${activeId}/export`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    const j = await r.json();
    setBusy(false);
    if (r.ok) alert(`Thread exported to: ${j.path}`);
    else alert("Export failed.");
  }

  async function exportFullReport() {
    if (!activeId) return;
    setBusy(true);
    const r = await fetch(`${API_BASE}/conversations/${activeId}/export/full`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    const j = await r.json();
    setBusy(false);
    if (r.ok) alert(`Full report generated at: ${j.path}`);
    else alert("Full export failed.");
  }

  async function ingestUrl(url: string) {
    if (!url) return;
    setBusy(true);
    const r = await fetch(`${API_BASE}/ingest/url?url=${encodeURIComponent(url)}`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    const j = await r.json();
    setBusy(false);
    if (r.ok) {
      alert(`Successfully ingested ${j.chunks} chunks from ${url}`);
      refreshConvs();
    } else {
      alert(`Ingestion failed: ${j.error}`);
    }
  }

  return (
    <div className="wrap">

      <Header
        tab={tab} onTabChange={setTab}
        mode={mode} onModeChange={(m) => setMode(m as any)}
        model={model} onModelChange={setModel}
        modelOptions={modelOptions} onModelOptionsChange={setModelOptions}
        dept={dept} onDeptChange={setDept}
        role={user?.role}
        showIngest={showIngest}
        onToggleIngest={() => setShowIngest(!showIngest)}
      />

      {showIngest && (
        <IngestionPanel
          onClose={() => setShowIngest(false)}
          busy={busy}
          setBusy={setBusy}
        />
      )}

      <div className="flex flex-1 overflow-hidden relative">
        <div
          className={`
            transition-all duration-300 ease-in-out border-r border-white/5 bg-[#0d0d1a]/70 backdrop-blur-md shrink-0 h-full
            ${isCollapsed ? 'w-0 opacity-0 overflow-hidden' : 'w-96 opacity-100'}
            ${mobileMenuOpen ? 'absolute z-50 w-96 shadow-2xl' : 'relative'}
            md:relative
          `}
        >
          <Sidebar
            convs={convs}
            activeId={activeId}
            onNew={newConv}
            onLoad={(id) => { loadConv(id); setMobileMenuOpen(false); }}
            onDelete={deleteConv}
            onIngest={ingestUrl}
            projectContext={projectContext}
            onContextChange={setProjectContext}
            loading={convsLoading}
          />
        </div>

        {/* Sidebar Toggle Handle (Desktop) - on outer edge */}
        {!mobileMenuOpen && (
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`
              absolute top-1/2 -translate-y-1/2 z-20 w-6 h-16 bg-[#0d0d1a]/80 hover:bg-white/10 
              border border-white/10 rounded-r-md flex items-center justify-center 
              transition-all duration-300 hidden md:flex backdrop-blur-md
              shadow-lg hover:shadow-xl
            `}
            style={{ left: isCollapsed ? '0' : '384px' }}
          >
            <span className="text-sm text-white/60 hover:text-white/90 transition-colors">
              {isCollapsed ? '▶' : '◀'}
            </span>
          </button>
        )}

        {/* Mobile Menu Toggle */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden absolute top-4 left-4 z-50 p-2 bg-black/50 rounded-lg text-white/70 border border-white/10"
        >
          {mobileMenuOpen ? '✕' : '☰'}
        </button>

        {/* Mobile Overlay */}
        {mobileMenuOpen && (
          <div
            className="absolute inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}

        <main className="main flex-1 h-full min-w-0">
          {tab === "chat" && (
            <ChatArea
              messages={messages}
              input={input}
              setInput={setInput}
              send={send}
              busy={busy}
              streaming={streaming}
              onStop={() => abortController?.abort()}
              answer={answer}
              citations={citations}
              toolTrace={toolTrace}
              retrieval={retrieval}
              showDeep={showDeep}
              setShowDeep={setShowDeep}
              showCites={showCites}
              setShowCites={setShowCites}
              showTools={showTools}
              setShowTools={setShowTools}
              onExport={exportThread}
              onRegen={(id) => console.log("Regen", id)} // Placeholder for now
              onFullExport={exportFullReport}
              audit={audit}
              agentStatus={agentStatus}
              thoughts={thoughts}
              isCollapsed={false}
              toggleSearch={() => { }}
              isReasoning={isReasoning}
              setIsReasoning={setIsReasoning}
            />
          )}

          {tab === "knowledge" && (
            <SourcesDashboard sources={kbSources} stats={kbStats} onRefresh={refreshKB} />
          )}

          {tab === "evals" && (
            <EvalsPanel
              busy={busy}
              runEvals={runEvals}
              ingestWebKB={ingestWebKB}
              loadLatestEval={loadLatestEval}
              report={evalReport}
            />
          )}

          {tab === "admin" && (
            <AdminPanel />
          )}

          {tab === "workbench" && (
            <WorkbenchPanel />
          )}
        </main>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="h-screen w-screen flex items-center justify-center bg-[#030307] text-white">Loading JGPT...</div>}>
      <HomeContent />
    </Suspense>
  );
}
