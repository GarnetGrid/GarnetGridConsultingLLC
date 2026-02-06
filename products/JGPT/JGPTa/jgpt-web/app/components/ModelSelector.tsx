"use client";

import { useState, useEffect } from "react";
import CustomDropdown from "./CustomDropdown";
import { API_BASE, DropdownOption, MODELS } from "../constants";
import { useAuth } from "../context/AuthContext";

interface ModelSelectorProps {
    value: string;
    onChange: (model: string) => void;
    persona: string;
}

export default function ModelSelector({ value, onChange, persona }: ModelSelectorProps) {
    // @ts-ignore
    if (typeof window !== 'undefined') (window as any).DEBUG_MODELS = MODELS;

    const { token } = useAuth();
    const [options, setOptions] = useState<DropdownOption[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        async function fetchModelsAndConfig() {
            if (!token) return;
            setLoading(true);
            try {
                // Fetch models and persona config in parallel
                const [modelsRes, configRes] = await Promise.all([
                    fetch(`${API_BASE}/models`, {
                        headers: { Authorization: `Bearer ${token}` }
                    }),
                    fetch(`${API_BASE}/personas/${persona}/config`, {
                        headers: { Authorization: `Bearer ${token}` }
                    }).catch(() => null)
                ]);

                if (modelsRes.ok) {
                    const models = await modelsRes.json();
                    let recommended: string[] = [];
                    if (configRes && configRes.ok) {
                        const config = await configRes.json();
                        recommended = config.recommended_models || [];
                    }

                    console.log('Fetching models success. Models:', models);
                    console.log('Available constants:', MODELS);

                    const opts: DropdownOption[] = models.map((m: any) => {
                        const modelName = m.name?.trim();
                        // Find matching model constant
                        const definedModel = MODELS.find(
                            dm => {
                                if (!modelName || !dm.value) return false;
                                return dm.value === modelName || modelName.startsWith(dm.value + ":");
                            }
                        );

                        return {
                            value: modelName,
                            label: definedModel?.label || modelName,
                            description: definedModel?.description || `${(m.size / 1024 / 1024 / 1024).toFixed(1)} GB`,
                            icon: definedModel?.icon || "🤖",
                            badge: recommended.includes(modelName) ? "Recommended" : definedModel?.badge,
                            color: recommended.includes(modelName) ? "#10b981" : definedModel?.color // green
                        };
                    });
                    setOptions(opts);
                }
            } catch (e) {
                console.error("Failed to fetch models or config", e);
            } finally {
                setLoading(false);
            }
        }
        fetchModelsAndConfig();
    }, [token, persona]);

    return (
        <CustomDropdown
            value={value}
            onChange={(v) => onChange(v as string)}
            options={options}
            label={loading ? "Loading..." : "Model"}
            searchable={true}
            showRecent={true}
            borderColor="#8b5cf6" // purple
        />
    );
}
