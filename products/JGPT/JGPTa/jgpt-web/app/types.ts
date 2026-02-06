export type Conv = { id: number; title: string; mode: string; model: string; created_at: string };
export interface ThoughtProp {
    type: 'thought' | 'tool_call' | 'tool_result' | 'error';
    content?: string;
    tool?: string;
    input?: string;
    result?: string;
}

export interface Msg {
    id: number;
    role: "user" | "assistant" | "system";
    content: string;
    created_at: string;
    embedding?: number[];
    thoughts?: ThoughtProp[];
}
export type Citation = { chunk_id: number; source: string; domain: string; title?: string; snippet: string; text: string; rank_type?: string };
export interface ToolRun {
    name: string;
    thought?: string;
    input: any;
    output: any;
}
;
export type ChatResp = { conversation_id: number; answer: string; citations: Citation[]; tool_trace: ToolRun[]; retrieval?: any; quality?: any };

export interface EvalItem {
    rubric: string;
    score: number;
    notes?: string;
}

export interface EvalRun {
    mode: string;
    question: string;
    answer: string;
    judge: {
        items: EvalItem[];
        total: number;
        max: number;
        grade: string;
        confidence: number;
    };
}

export interface EvalReport {
    ok: boolean;
    suite: string;
    runs: EvalRun[];
}

export interface KBSource {
    path: string;
    name: string;
    size: number;
    mtime: number;
    extension: string;
    chunks: number;
    images: number;
}

export interface KBStats {
    total_documents: number;
    total_chunks: number;
    total_images: number;
    images_with_descriptions: number;
    last_ingestion?: string;
}
