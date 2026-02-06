"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

export default function ThemeToggle() {
    const [theme, setTheme] = useState<"dark" | "light">("dark");

    useEffect(() => {
        // Init from storage or system preference
        const saved = localStorage.getItem("theme");
        if (saved) {
            setTheme(saved as "dark" | "light");
            document.documentElement.setAttribute("data-theme", saved);
        } else {
            // Default dark
            document.documentElement.setAttribute("data-theme", "dark");
        }
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === "dark" ? "light" : "dark";
        setTheme(newTheme);
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
    };

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-all border border-transparent hover:border-white/10"
            title={`Toggle Theme (${theme === "dark" ? "Light" : "Dark"} Mode)`}
            aria-label="Theme Toggle"
        >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
    );
}
