export interface DropdownOption {
    value: string;
    label: string;
    icon?: string;
    description?: string;
    color?: string;
    badge?: string;
}

export const DEPARTMENTS: DropdownOption[] = [
    { value: "all", label: "All Departments", icon: "🌐", description: "Search across entire knowledge base" },
    { value: "finance", label: "Finance", icon: "💰", description: "Financial documents and reports" },
    { value: "hr", label: "Human Resources", icon: "👥", description: "HR policies and procedures" },
    { value: "it", label: "IT / Operations", icon: "💻", description: "Technical documentation and IT resources" },
    { value: "supply", label: "Supply Chain", icon: "📦", description: "Supply chain and logistics" },
    { value: "marketing", label: "Marketing", icon: "📢", description: "Marketing materials and campaigns" },
    { value: "sales", label: "Sales", icon: "💼", description: "Sales resources and customer data" },
    { value: "legal", label: "Legal", icon: "⚖️", description: "Legal documents and compliance" },
    { value: "engineering", label: "Engineering", icon: "⚙️", description: "Engineering specs and technical docs" },
    { value: "support", label: "Customer Support", icon: "🎧", description: "Support documentation and FAQs" },
];

export const MODES: DropdownOption[] = [
    {
        value: "auto",
        label: "Auto Pilot",
        icon: "🧭",
        description: "Intelligent routing to the best expert agent",
        color: "#8b5cf6"
    },
    {
        value: "powerbi",
        label: "Power BI Pro",
        icon: "📊",
        description: "Expert in Power BI reports, DAX, and data visualization",
        color: "#F2C811"
    },
    {
        value: "d365fo",
        label: "Business Central / F&O",
        icon: "💼",
        description: "Dynamics 365 Finance & Operations specialist",
        color: "#0078D4"
    },
    {
        value: "sql",
        label: "SQL Architect",
        icon: "🗄️",
        description: "Database design, query optimization, and SQL best practices",
        color: "#CC2927"
    },
    {
        value: "universal",
        label: "Universal AI",
        icon: "🌐",
        description: "General-purpose AI assistant for any task",
        color: "#667eea"
    },
    {
        value: "truthkeeper",
        label: "TruthKeeper",
        icon: "🔍",
        description: "Fact-checking and source verification specialist",
        color: "#10b981"
    },
];

export interface ModelOption extends DropdownOption {
    speed?: 'fast' | 'medium' | 'slow';
    quality?: 'high' | 'medium' | 'low';
}

export const MODELS: ModelOption[] = [
    {
        value: "llama3.2",
        label: "Llama 3.2",
        description: "Latest Llama model - balanced performance",
        speed: "fast",
        quality: "high",
        badge: "Recommended"
    },
    {
        value: "llama3",
        label: "Llama 3",
        description: "Stable Llama model - reliable performance",
        speed: "fast",
        quality: "high"
    },
    {
        value: "phi3",
        label: "Phi 3",
        description: "Compact model - efficient for simple tasks",
        speed: "fast",
        quality: "medium"
    },
    {
        value: "mistral",
        label: "Mistral",
        description: "Excellent for reasoning and analysis",
        speed: "medium",
        quality: "high"
    },
    {
        value: "gemma",
        label: "Gemma",
        description: "Google's efficient open model",
        speed: "fast",
        quality: "medium"
    },
    {
        value: "codellama",
        label: "Code Llama",
        description: "Specialized for code generation and analysis",
        speed: "medium",
        quality: "high",
        icon: "💻"
    },
    {
        value: "llava",
        label: "LLaVA",
        description: "Vision-language model for image analysis",
        speed: "slow",
        quality: "high",
        icon: "👁️"
    },
    {
        value: "mxbai-embed-large",
        label: "MxBai Embed",
        description: "High-performance embedding model",
        speed: "fast",
        quality: "high",
        icon: "🧠"
    }
];

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
