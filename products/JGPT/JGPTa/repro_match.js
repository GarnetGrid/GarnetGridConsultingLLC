
const MODELS = [
    { value: "llama3.2", label: "Llama 3.2", description: "Latest Llama model" },
    { value: "codellama", label: "Code Llama", description: "Specialized for code" },
];

const apiModels = [
    { name: "llama3.2:latest", size: 2019393189 },
    { name: "codellama:7b", size: 3825910662 }
];

const opts = apiModels.map(m => {
    const modelName = m.name?.trim();
    const definedModel = MODELS.find(dm => {
        if (!modelName || !dm.value) return false;
        const match = dm.value === modelName || modelName.startsWith(dm.value + ":");
        if (match) console.log(`Matched ${modelName} to ${dm.value}`);
        return match;
    });

    if (!definedModel) console.log(`No match for ${modelName}`);

    return {
        value: modelName,
        label: definedModel?.label || modelName,
        description: definedModel?.description || "Fallback"
    };
});

console.log(JSON.stringify(opts, null, 2));
