import { API_BASE_URL } from '$lib/env_config';
export const settingsState = $state({
    isOpen: false,
    provider: 'Ollama (Local)',
    modelName: 'Llama 3.2:latest',
    temperature: 0.7,
    personalityName: 'System Architect',
    systemInstructions: 'Você é um assistente técnico especialista em RAG. Seu objetivo é analisar documentos internos e fornecer respostas baseadas exclusivamente nos fatos recuperados, mantendo um tom profissional e citando fontes.',
    additionalPrompts: ['', '', ''],
    formality: 'Formal',
    theme: 'Light Mode',
    userName: 'Sovereign Admin',
    userProfession: 'System Operator',
    aiName: 'Sophy',
    guardrails: [
        { type: 'regex', value: '\\b\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}\\b', description: 'Brazilian CPF' },
        { type: 'keyword', value: 'how to build a bomb', description: 'Violence / Toxicity' },
        { type: 'keyword', value: 'ignore all previous instructions', description: 'Jailbreak' }
    ]
});

export async function loadSettings() {
    try {
        const res = await fetch(`${API_BASE_URL}/v1/settings`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` }
        });
        if (res.ok) {
            const data = await res.json();
            if (data.provider) settingsState.provider = data.provider;
            if (data.modelName) settingsState.modelName = data.modelName;
            if (data.temperature !== undefined) settingsState.temperature = data.temperature;
            if (data.personalityName) settingsState.personalityName = data.personalityName;
            if (data.systemInstructions) settingsState.systemInstructions = data.systemInstructions;
            if (data.additionalPrompts) settingsState.additionalPrompts = data.additionalPrompts;
            if (data.formality) settingsState.formality = data.formality;
            if (data.theme) settingsState.theme = data.theme;
            if (data.userName) settingsState.userName = data.userName;
            if (data.userProfession) settingsState.userProfession = data.userProfession;
            if (data.aiName) settingsState.aiName = data.aiName;
            if (data.guardrails) settingsState.guardrails = data.guardrails;
        }
    } catch (e) {
        console.error("Failed to load global settings:", e);
    }
}

export async function saveSettings() {
    try {
        // Uses snapshot to unwrap proxies
        // In Svelte 5, $state.snapshot unwraps deeply but we can just map the fields.
        let existingData = {};
        const fetchRes = await fetch(`${API_BASE_URL}/v1/settings`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` }
        });
        if (fetchRes.ok) {
            existingData = await fetchRes.json();
        }

        const payload = {
            ...existingData,
            provider: settingsState.provider,
            modelName: settingsState.modelName,
            llm_model: settingsState.modelName,  // Bridge: Backend Tri-Agent Router reads this key
            temperature: settingsState.temperature,
            personalityName: settingsState.personalityName,
            systemInstructions: settingsState.systemInstructions,
            additionalPrompts: settingsState.additionalPrompts,
            formality: settingsState.formality,
            theme: settingsState.theme,
            userName: settingsState.userName,
            userProfession: settingsState.userProfession,
            aiName: settingsState.aiName,
            guardrails: settingsState.guardrails
        };
        
        const res = await fetch(`${API_BASE_URL}/v1/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}`
            },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            settingsState.isOpen = false;
        }
    } catch (e) {
        console.error("Failed to save global settings:", e);
    }
}

