<template>
  <div class="p-8 h-full overflow-y-auto w-full bg-[#111111] text-zinc-100 flex flex-col gap-6">
    <header class="flex flex-col gap-1 pb-4 border-b border-white/5">
      <h1 class="text-3xl font-light tracking-tight text-white flex items-center gap-3">
        <div class="px-2 py-1 bg-white/5 border border-white/10 rounded-md shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
            <span class="text-cyan-400">🗂️</span>
        </div>
        Virtual Projects Hub
      </h1>
      <p class="text-sm text-zinc-500 font-mono tracking-wider ml-1">WORKFLOW & TEMPLATE ORCHESTRATION</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Projetos Ativos -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        <section class="bg-[#151518] border border-white/5 rounded-xl p-5 shadow-2xl backdrop-blur-sm">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-medium text-cyan-400 flex items-center gap-2">
                    <span class="i-ph-folder-star-duotone text-xl"></span>
                    Agrupamentos Lógicos (Tags)
                </h2>
                <button class="bg-white/5 hover:bg-white/10 text-xs px-3 py-1.5 rounded-md border border-white/10 transition-colors flex items-center gap-1">
                    <span class="i-ph-plus-bold"></span> Novo Virtual Hub
                </button>
            </div>
            
            <div v-if="loadingTags" class="flex justify-center items-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
            </div>
            <div v-else-if="tags.length === 0" class="text-center py-8 text-zinc-500 text-sm border border-dashed border-white/10 rounded-lg">
                Nenhuma tag encontrada no cofre Sensus.
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div 
                    v-for="tag in tags" 
                    :key="tag.name"
                    class="group flex flex-col p-4 rounded-lg bg-black/20 border border-white/5 hover:border-cyan-500/30 transition-all cursor-pointer relative overflow-hidden"
                    @click="filterByTag(tag.name)"
                >
                    <div class="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-medium text-zinc-200 group-hover:text-white capitalize truncate pr-2">#{{ tag.name }}</h3>
                        <span class="text-[10px] font-mono bg-cyan-500/10 text-cyan-400 px-2 rounded-full border border-cyan-500/20 whitespace-nowrap">{{ tag.count }} Docs</span>
                    </div>
                </div>
            </div>
        </section>
      </div>

      <!-- Templates (DoR / Specs) -->
      <div class="flex flex-col gap-6">
        <section class="bg-[#151518] border border-white/5 rounded-xl p-5 shadow-2xl backdrop-blur-sm flex-1 flex flex-col">
          <h2 class="text-lg font-medium text-purple-400 mb-4 flex items-center gap-2">
              <span class="i-ph-magic-wand-duotone text-xl"></span>
              Templates (DoR)
          </h2>
          
          <div v-if="loadingTemplates" class="flex justify-center items-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500"></div>
          </div>
          <div v-else class="space-y-3">
              <button 
                  v-for="template in templates" 
                  :key="template.id"
                  @click="useTemplate(template)"
                  class="w-full text-left p-3 flex flex-col gap-1 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 hover:border-purple-500/30 transition-all"
              >
                  <strong class="text-sm font-medium text-zinc-200 flex items-center gap-2">
                      <span :class="template.icon || 'i-ph-file-text-duotone'"></span>
                      {{ template.name }}
                  </strong>
                  <span class="text-xs text-zinc-500">{{ template.description }}</span>
              </button>
              
              <button disabled class="w-full text-left p-3 flex flex-col gap-1 rounded-lg bg-black text-center border border-dashed border-white/20 opacity-50 cursor-not-allowed transition-all text-zinc-500">
                  <span class="text-sm font-medium flex items-center justify-center gap-2">
                      <span class="i-ph-plus"></span> Criar Novo Template (Em Breve)
                  </span>
              </button>
          </div>
        </section>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface TagInfo {
  name: string
  count: number
}

interface TemplateInfo {
  id: string
  name: string
  description: string
  icon: string
}

const tags = ref<TagInfo[]>([])
const templates = ref<TemplateInfo[]>([])
const loadingTags = ref(true)
const loadingTemplates = ref(true)

const fetchHubData = async () => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const token = localStorage.getItem('sovereign_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  
  try {
    loadingTags.value = true
    const tagsRes = await axios.get(`${baseURL}/v1/vault/tags`, { headers })
    tags.value = tagsRes.data.tags || []
  } catch (error) {
    console.error("Failed to fetch tags:", error)
  } finally {
    loadingTags.value = false
  }

  try {
    loadingTemplates.value = true
    const tplRes = await axios.get(`${baseURL}/v1/vault/templates`, { headers })
    templates.value = tplRes.data.templates || []
  } catch (error) {
    console.error("Failed to fetch templates:", error)
  } finally {
    loadingTemplates.value = false
  }
}

const filterByTag = (tagName: string) => {
  console.log(`Pivoting vault view logic to show tag: ${tagName}. (Phase 16.5)`)
  // TODO: Navigate or emit global state change to filter SidebarTree
}

const useTemplate = (template: TemplateInfo) => {
  console.log(`Instantiating template from template.id: ${template.id} ... (Phase 16.5)`)
  // TODO: Create a physical file / empty slot populated with the selected Markdown Schema, then route to the Block Editor
  alert(`Criação a partir do molde "${template.name}" em construção.`)
}

onMounted(() => {
  fetchHubData()
})
</script>

