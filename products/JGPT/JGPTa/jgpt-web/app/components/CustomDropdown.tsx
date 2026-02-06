"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";
import { DropdownOption } from "../constants";
import Tooltip from "./Tooltip";

interface CustomDropdownProps {
    value: string | string[];
    onChange: (value: string | string[]) => void;
    options: DropdownOption[];
    label?: string;
    borderColor?: string;
    searchable?: boolean;
    className?: string;
    multiSelect?: boolean;
    showRecent?: boolean;
}

export default function CustomDropdown({
    value,
    onChange,
    options,
    label,
    borderColor,
    searchable = false,
    className = "",
    multiSelect = false,
    showRecent = false
}: CustomDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const dropdownRef = useRef<HTMLDivElement>(null);
    const [recentValues, setRecentValues] = useState<string[]>([]);

    // Load recent values on mount
    useEffect(() => {
        if (showRecent && label) {
            const saved = localStorage.getItem(`jgpt_recent_${label}`);
            if (saved) {
                try {
                    setRecentValues(JSON.parse(saved));
                } catch (e) {
                    console.error("Failed to parse recent values", e);
                }
            }
        }
    }, [showRecent, label]);

    // Save selection to recent
    const addToRecent = (val: string) => {
        if (!showRecent || !label) return;

        const newRecent = [val, ...recentValues.filter(v => v !== val)].slice(0, 3);
        setRecentValues(newRecent);
        localStorage.setItem(`jgpt_recent_${label}`, JSON.stringify(newRecent));
    };

    const handleSelect = (optionValue: string) => {
        if (multiSelect) {
            const currentValues = Array.isArray(value) ? value : (value ? [value] : []);
            let newValues: string[];

            if (currentValues.includes(optionValue)) {
                newValues = currentValues.filter(v => v !== optionValue);
            } else {
                newValues = [...currentValues, optionValue];
                addToRecent(optionValue);
            }
            // cast to any to allow array
            onChange(newValues as any);
            // Don't close on multi-select
        } else {
            addToRecent(optionValue);
            onChange(optionValue as any);
            setIsOpen(false);
            setSearchTerm("");
        }
    };

    const filteredOptions = searchable
        ? options.filter(opt =>
            opt.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
            opt.description?.toLowerCase().includes(searchTerm.toLowerCase())
        )
        : options;

    const recentOptions = showRecent
        ? options.filter(opt => recentValues.includes(opt.value))
        : [];

    // Filter out recents from main list to avoid duplication if desired, 
    // but usually better to show them again or just keep as is. 
    // Let's keep them in both for now for consistency of category grouping if we had it.

    // Display text logic
    const getDisplayText = () => {
        if (multiSelect && Array.isArray(value) && value.length > 0) {
            if (value.length === 1) {
                const opt = options.find(o => o.value === value[0]);
                return opt?.label || value[0];
            }
            return `${value.length} selected`;
        }
        if (!multiSelect && !Array.isArray(value)) {
            const opt = options.find(o => o.value === value);
            return opt?.label || label || "Select...";
        }
        return label || "Select...";
    };

    const displayIcon = !multiSelect && !Array.isArray(value)
        ? options.find(o => o.value === value)?.icon
        : null;

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
                setSearchTerm("");
            }
        };

        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isOpen]);

    // Keyboard navigation
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Escape") {
            setIsOpen(false);
            setSearchTerm("");
        } else if (e.key === "Enter" && !isOpen) {
            setIsOpen(true);
        }
    };

    const renderOption = (option: DropdownOption) => {
        const isSelected = Array.isArray(value)
            ? value.includes(option.value)
            : option.value === value;

        return (
            <Tooltip
                key={option.value}
                content={option.description || option.label}
                position="right"
            >
                <button
                    type="button"
                    onClick={() => handleSelect(option.value)}
                    className={`w-full px-3 py-2.5 text-left text-xs flex items-center gap-2 transition-all ${isSelected
                        ? 'bg-purple-500/20 text-white border-l-2 border-purple-500'
                        : 'text-white/70 hover:bg-white/5 hover:text-white border-l-2 border-transparent'
                        }`}
                    style={option.color && isSelected ? { borderLeftColor: option.color } : {}}
                >
                    {/* Checkbox for multi-select */}
                    {multiSelect && (
                        <div className={`w-3 h-3 rounded border flex items-center justify-center transition-colors ${isSelected ? 'bg-purple-500 border-purple-500' : 'border-white/30'}`}>
                            {isSelected && <span className="text-[8px] text-white">✓</span>}
                        </div>
                    )}

                    {option.icon && (
                        <span className="text-base">{option.icon}</span>
                    )}
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <span className="truncate">{option.label}</span>
                            {option.badge && (
                                <span className="text-[9px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded-full whitespace-nowrap">
                                    {option.badge}
                                </span>
                            )}
                        </div>
                        {option.description && (
                            <div className="text-[10px] text-white/70 mt-0.5 truncate">
                                {option.description}
                            </div>
                        )}
                    </div>
                    {!multiSelect && isSelected && (
                        <span className="text-purple-400">✓</span>
                    )}
                </button>
            </Tooltip>
        );
    };

    return (
        <div ref={dropdownRef} className={`relative ${className}`} onKeyDown={handleKeyDown}>
            {/* Trigger Button */}
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className="bg-[#141428]/60 border border-white/5 text-white/80 rounded-md px-3 py-2 text-xs outline-none focus:border-purple-500 transition-all cursor-pointer hover:bg-white/5 flex items-center gap-2 w-full group relative"
                style={borderColor ? { borderLeft: `3px solid ${borderColor}` } : {}}
            >
                {/* Gradient border effect on focus */}
                {isOpen && (
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-600 rounded-md opacity-50 blur-sm -z-10"></div>
                )}

                <span className="flex items-center gap-2 flex-1 min-w-0">
                    {displayIcon && <span className="text-sm flex-shrink-0">{displayIcon}</span>}
                    <span className="truncate flex-1 min-w-0">{getDisplayText()}</span>
                    {!multiSelect && !Array.isArray(value) && options.find(o => o.value === value)?.badge && (
                        <span className="text-[9px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded-full whitespace-nowrap flex-shrink-0">
                            {options.find(o => o.value === value)?.badge}
                        </span>
                    )}
                </span>
                <ChevronDown
                    className={`w-3 h-3 transition-transform duration-200 flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`}
                />
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-[#0d0d1a] border border-white/10 rounded-lg shadow-2xl z-[60] overflow-hidden animate-fade-in min-w-[220px]">
                    {/* Search Input */}
                    {searchable && (
                        <div className="p-2 border-b border-white/5">
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search..."
                                className="w-full bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-purple-500 transition-colors"
                                autoFocus
                            />
                        </div>
                    )}

                    {/* Options List */}
                    <div className="max-h-64 overflow-y-auto custom-scrollbar">
                        {/* Recent Selections */}
                        {showRecent && recentOptions.length > 0 && !searchTerm && (
                            <>
                                <div className="px-3 py-1.5 text-[10px] uppercase tracking-wider text-white/30 font-semibold bg-white/5">
                                    Recent
                                </div>
                                {recentOptions.map(renderOption)}
                                <div className="h-px bg-white/5 my-1" />
                                <div className="px-3 py-1.5 text-[10px] uppercase tracking-wider text-white/30 font-semibold bg-white/5">
                                    All Options
                                </div>
                            </>
                        )}

                        {filteredOptions.length === 0 ? (
                            <div className="px-3 py-2 text-xs text-white/40 text-center">
                                No options found
                            </div>
                        ) : (
                            filteredOptions.map(renderOption)
                        )}
                    </div>

                    {/* Clear All for Multi-select */}
                    {multiSelect && Array.isArray(value) && value.length > 0 && (
                        <div className="p-2 border-t border-white/5 bg-[#0d0d1a]">
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onChange([] as any);
                                }}
                                className="w-full text-center text-xs text-purple-400 hover:text-purple-300 py-1"
                            >
                                Clear Selection
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
