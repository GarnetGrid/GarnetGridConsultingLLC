import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                border: "var(--glass-border)",
                input: "var(--glass-border)",
                ring: "var(--accent)",
                background: "var(--bg)",
                foreground: "var(--text)",
                primary: {
                    DEFAULT: "var(--accent)",
                    foreground: "#ffffff",
                },
                secondary: {
                    DEFAULT: "var(--accent2)",
                    foreground: "#ffffff",
                },
                destructive: {
                    DEFAULT: "#ff4444",
                    foreground: "#ffffff",
                },
                muted: {
                    DEFAULT: "var(--muted)",
                    foreground: "#ccccff",
                },
                accent: {
                    DEFAULT: "var(--accent)",
                    foreground: "#ffffff",
                },
                popover: {
                    DEFAULT: "var(--panel)",
                    foreground: "var(--text)",
                },
                card: {
                    DEFAULT: "var(--panel)",
                    foreground: "var(--text)",
                },
            },
            borderRadius: {
                lg: "12px",
                md: "8px",
                sm: "4px",
            },
        },
    },
    plugins: [],
};
export default config;
