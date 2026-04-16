<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Trash2, Loader2 } from 'lucide-svelte';

    interface ModelMatrixRow {
        model_name: string; parameter_size: number; supports_tools: boolean;
        is_reasoner: boolean; is_master: boolean; is_scribe: boolean; is_auditor: boolean;
        is_agent: boolean; is_coder: boolean; is_chat: boolean; is_project: boolean; is_installed: boolean;
    }
    let modelMatrix = $state<ModelMatrixRow[]>([]);
    let isSavingMatrix = $state(false);

    onMount(async () => {
        try {
            const matrixRes = await fetch(`${API_BASE_URL}/v1/settings/model_capabilities`);
            if (matrixRes.ok) modelMatrix = await matrixRes.json();
        } catch(e) { console.error("Failed to load Model Matrix:", e); }
    });

    async function toggleMatrixCapability(modelName: string, fieldName: keyof ModelMatrixRow, value: boolean) {
        if (isSavingMatrix) return;
        isSavingMatrix = true;
        try {
            const model = modelMatrix.find(m => m.model_name === modelName);
            if (!model) return;
            const payload = { model_name: model.model_name,
                supports_tools: fieldName === 'supports_tools' ? value : model.supports_tools,
                is_reasoner: fieldName === 'is_reasoner' ? value : model.is_reasoner,
                is_master: fieldName === 'is_master' ? value : model.is_master,
                is_scribe: fieldName === 'is_scribe' ? value : model.is_scribe,
                is_auditor: fieldName === 'is_auditor' ? value : model.is_auditor,
                is_agent: fieldName === 'is_agent' ? value : model.is_agent,
                is_coder: fieldName === 'is_coder' ? value : model.is_coder,
                is_chat: fieldName === 'is_chat' ? value : model.is_chat,
                is_project: fieldName === 'is_project' ? value : model.is_project,
                is_installed: fieldName === 'is_installed' ? value : model.is_installed
            };
            const res = await fetch(`${API_BASE_URL}/v1/settings/model_capabilities/toggles`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            if (res.ok) (model as any)[fieldName] = value;
        } catch(e) { console.error("Failed to update matrix toggle:", e); }
        finally { isSavingMatrix = false; }
    }

    async function deleteMatrixEntry(modelName: string) {
        if (!confirm(`⚠️ Remover '${modelName}' da Matrix?\n\nO Discover automático pode re-registrá-lo ao reiniciar.`)) return;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/model_capabilities/${encodeURIComponent(modelName)}`, { method: 'DELETE' });
            if (res.ok) modelMatrix = modelMatrix.filter(m => m.model_name !== modelName);
        } catch(e) { console.error('Failed to delete matrix entry:', e); }
    }

    const CAPS: {field: keyof ModelMatrixRow, label: string, color: string, requiresTools?: boolean}[] = [
        { field: 'supports_tools', label: 'Tools', color: 'emerald' },
        { field: 'is_reasoner', label: 'Think', color: 'fuchsia' },
        { field: 'is_master', label: 'Master', color: 'primary', requiresTools: true },
        { field: 'is_scribe', label: 'Scribe', color: 'primary' },
        { field: 'is_auditor', label: 'Audit', color: 'amber' },
        { field: 'is_agent', label: 'Agent', color: 'primary', requiresTools: true },
        { field: 'is_coder', label: 'Coder', color: 'primary' },
        { field: 'is_chat', label: 'Chat', color: 'primary' },
        { field: 'is_project', label: 'Project', color: 'primary' },
        { field: 'is_installed', label: 'Live', color: 'sky' },
    ];
</script>

<div class="p-8 h-full flex flex-col">
    <div class="w-full space-y-10 flex-1">
        <div class="flex justify-between items-end mb-10">
            <div>
                <nav class="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-2">
                    <span>Settings</span>
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span class="text-primary font-extrabold">AI Models</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight">Model Capabilities Matrix</h2>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 bg-tertiary-container/10 text-on-tertiary-fixed-variant rounded-full border border-tertiary-container/20">
                <span class="text-[12px] font-bold tracking-tight">{modelMatrix.length} models registered</span>
            </div>
        </div>

        <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10 pb-12">
            <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                <div class="p-3 bg-primary-fixed/50 rounded-2xl shadow-inner">
                    <span class="material-symbols-outlined text-primary text-[28px]" style="font-variation-settings: 'FILL' 1;">psychology</span>
                </div>
                <div>
                    <h3 class="text-xl font-bold text-on-surface">Operations Matrix</h3>
                    <p class="text-[11px] font-medium text-on-surface-variant mt-1">Toggle capabilities for each installed model. Changes are saved instantly.</p>
                </div>
            </div>

            <div class="overflow-x-auto rounded-2xl border border-outline-variant/10">
                <table class="w-full text-left text-sm text-on-surface">
                    <thead class="text-[10px] uppercase bg-surface-container-high/50 text-on-surface-variant tracking-widest">
                        <tr>
                            <th class="px-4 py-3.5 font-semibold">Model</th>
                            {#each CAPS as cap}
                            <th class="px-2 py-3.5 font-semibold text-center">
                                <span class="text-{cap.color}-500 dark:text-{cap.color}-400">{cap.label}</span>
                            </th>
                            {/each}
                            <th class="px-2 py-3.5 font-semibold text-center">Del</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-outline-variant/10">
                        {#each modelMatrix as row}
                        <tr class="hover:bg-surface-container-low/50 transition-colors">
                            <td class="px-4 py-3">
                                <div class="font-medium {row.is_installed ? 'text-on-surface' : 'text-on-surface-variant line-through opacity-50'}">{row.model_name}</div>
                                <div class="text-[11px] text-on-surface-variant mt-0.5">{(row.parameter_size).toFixed(1)}B params</div>
                            </td>
                            {#each CAPS as cap}
                            <td class="px-2 py-3 text-center">
                                <input type="checkbox"
                                    class="w-4 h-4 rounded border-outline-variant/30 bg-surface-container text-primary focus:ring-primary cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed accent-primary"
                                    checked={row[cap.field] as boolean}
                                    disabled={isSavingMatrix || (cap.requiresTools && !row.supports_tools) || (cap.field !== 'supports_tools' && cap.field !== 'is_installed' && !row.is_installed)}
                                    onchange={(e) => toggleMatrixCapability(row.model_name, cap.field, (e.target as HTMLInputElement).checked)}
                                />
                            </td>
                            {/each}
                            <td class="px-2 py-3 text-center">
                                <button title="Remove {row.model_name}" onclick={() => deleteMatrixEntry(row.model_name)}
                                    class="text-on-surface-variant/50 hover:text-error transition-colors cursor-pointer p-1 rounded hover:bg-error-container/20">
                                    <Trash2 class="w-3.5 h-3.5" />
                                </button>
                            </td>
                        </tr>
                        {:else}
                        <tr><td colspan="12" class="px-4 py-8 text-center text-on-surface-variant italic">No models registered. They auto-register when the system starts.</td></tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
</style>
