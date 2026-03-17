<template>
  <div class="h-full bg-surface-900 text-surface-200 flex flex-col items-center justify-center" v-if="isLoading">
     <div class="animate-pulse flex items-center gap-2">
        <div class="w-4 h-4 rounded-full bg-emerald-500/50"></div> Carregando Documento Neural...
     </div>
  </div>
  
  <div v-else-if="fetchError" class="h-full flex items-center justify-center text-red-400">
     {{ fetchError }}
  </div>

  <div v-else class="h-full bg-surface-900 text-surface-200 relative">
    <!-- Discreet Spellcheck Notification -->
    <div v-if="showSpellcheckPrompt" class="absolute top-4 right-8 z-50 bg-surface-900 dark:bg-surface-800 border border-surface-700/50 rounded-lg shadow-2xl p-4 max-w-xs animate-in slide-in-from-top-4 fade-in duration-300">
      <div class="flex items-start gap-3">
        <div class="mt-0.5 text-emerald-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-surface-900 dark:text-surface-100 mb-1">Dicionário Ortográfico</h4>
          <p class="text-xs text-surface-400 leading-relaxed mb-3">
            O corretor do navegador está desativado para evitar falsos positivos no Markdown. Deseja reativar o dicionário Pt-BR?
          </p>
          <div class="flex items-center gap-2">
            <button @click="setSpellcheck(true)" class="text-xs bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 px-3 py-1.5 rounded transition-colors font-medium">
              Ativar Corretor
            </button>
            <button @click="setSpellcheck(false)" class="text-xs text-surface-400 hover:text-surface-900 dark:hover:text-surface-100 px-3 py-1.5 rounded transition-colors">
              Ignorar
            </button>
          </div>
        </div>
        <button @click="showSpellcheckPrompt = false" class="text-surface-500 hover:text-surface-900 dark:hover:text-surface-100">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>
    </div>

    <div class="h-full flex flex-col pt-12 relative">
      <!-- Floating Header Toolbar -->
      <div class="absolute top-4 left-6 z-40 bg-surface-900 rounded-lg border border-surface-700 p-1 flex gap-1 shadow-lg pointer-events-auto transition-all">
         <button @click="emit('update-view-mode', 'visual')" :class="viewMode === 'visual' ? 'bg-surface-700 text-white' : 'text-surface-600 hover:text-white'" class="px-3 py-1 text-xs rounded font-medium transition-colors">Visual</button>
         <button @click="emit('update-view-mode', 'split')" :class="viewMode === 'split' ? 'bg-surface-700 text-white' : 'text-surface-600 hover:text-white'" class="px-3 py-1 text-xs rounded font-medium transition-colors">Split</button>
         <button @click="emit('update-view-mode', 'source')" :class="viewMode === 'source' ? 'bg-surface-700 text-white' : 'text-surface-600 hover:text-white'" class="px-3 py-1 text-xs rounded font-medium transition-colors">Código</button>
         <div class="w-px h-4 bg-surface-700 mx-1 self-center"></div>
         <button @click="showProperties = !showProperties" :class="showProperties ? 'bg-primary-500/20 text-primary-400' : 'text-primary-500 hover:bg-surface-800'" class="px-2 py-1 text-xs rounded font-medium transition-colors flex items-center gap-1" title="Propriedades do Documento">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
            Props
         </button>
         <div class="w-px h-4 bg-zinc-700/50 mx-1 self-center"></div>
         <button @click="injectFileToAI" class="px-2 py-1 text-xs rounded font-medium text-emerald-400 hover:bg-emerald-500/10 hover:text-emerald-300 transition-colors flex items-center gap-1 animate-pulse hover:animate-none" title="Invocar Analista de Sistema IA para ler este Documento Abstrato">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><circle cx="12" cy="12" r="4"></circle></svg>
            Analisar
         </button>
      </div>

      <!-- Cell Coordinate Tooltip -->
      <Teleport to="body">
          <div v-show="hoveredCellCoordinate" 
               class="fixed z-[9999] pointer-events-none px-1.5 py-0.5 rounded text-[10px] bg-emerald-400 text-emerald-950 font-black tracking-widest shadow-xl transition-all duration-75"
               :style="{ top: hoveredCellPosition.y + 'px', left: hoveredCellPosition.x + 'px' }">
             {{ hoveredCellCoordinate }}
          </div>
      </Teleport>

      <!-- Split Container -->
      <div class="flex-1 w-full flex overflow-hidden" 
           @mousemove="handleEditorMouseMove" 
           @mouseleave="hoveredCellCoordinate = null">
        
        <!-- CODE FILE PANE Fallback -->
        <div v-if="isCodeFile" class="w-full max-w-4xl mx-auto h-full flex flex-col p-8 overflow-y-auto custom-scrollbar">
            <!-- Meta/Header -->
            <div class="mb-4 text-xs text-surface-500 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-emerald-500" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M10 10.5 8 13l2 2.5"/><path d="m14 10.5 2 2.5-2 2.5"/></svg>
                <span class="font-mono text-emerald-400 font-bold tracking-wider">{{ docData.path?.split('/').pop() || docData.name }}</span>
                <span class="ml-auto bg-surface-800/80 px-2 py-1 rounded text-[10px] text-surface-400">Somente Leitura (Protegido)</span>
            </div>
            <pre class="bg-[#111] p-6 rounded-xl border border-surface-700/50 text-surface-300 font-mono text-[13px] leading-relaxed overflow-x-auto shadow-inner"><code class="language-any">{{ rawMarkdown }}</code></pre>
        </div>

        <div v-else class="contents">
            <!-- SOURCE PANE -->
            <div v-show="viewMode === 'source' || viewMode === 'split'" 
                 :class="viewMode === 'split' ? 'w-1/2 border-r border-surface-800' : 'w-full max-w-4xl mx-auto'" 
                 class="h-full flex flex-col p-8 overflow-y-auto">
                <textarea 
                   v-model="rawMarkdown"
                   @input="handleSourceInput"
                   class="flex-1 w-full bg-transparent text-primary-400 font-mono text-[13px] leading-relaxed resize-none outline-none" 
                   spellcheck="false" 
                   placeholder="Escreva seu Markdown aqui..."></textarea>
            </div>

            <!-- VISUAL PANE (TipTap) -->
            <div v-show="viewMode === 'visual' || viewMode === 'split'" 
                 :class="viewMode === 'split' ? 'w-1/2' : 'w-full max-w-4xl mx-auto'"
                 class="h-full flex flex-col p-8 overflow-y-auto relative custom-scrollbar">
             
          <!-- Document Properties UI -->
          <div v-if="showProperties" class="mb-6 p-4 rounded-xl bg-surface-800 border border-surface-700 shadow-inner animate-in fade-in slide-in-from-top-2 flex-shrink-0">
             <div class="flex justify-between items-center mb-3">
                 <h3 class="text-[10px] font-bold uppercase tracking-widest text-surface-600 flex items-center gap-2">
                     <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg> Frontmatter YAML
                 </h3>
                 <button @click="showProperties = false" class="text-surface-600 hover:text-white transition-colors">
                     <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                 </button>
             </div>
             <div class="flex flex-col gap-2">
                 <div v-for="(_, key) in documentProperties" :key="key" class="flex items-center gap-2">
                     <input :value="key" @change="e => renameProperty(String(key), (e.target as HTMLInputElement).value)" class="text-xs bg-transparent text-surface-600 w-28 text-right font-mono outline-none focus:text-primary-400 transition-colors" placeholder="chave" />
                     <input v-model="documentProperties[key]" @change="syncPropertiesToSource" class="text-sm bg-surface-900 px-3 py-1.5 rounded-md text-slate-200 flex-1 outline-none border border-transparent focus:border-primary-500/30 transition-all font-mono" placeholder="valor" />
                     <button @click="removeProperty(key)" class="text-surface-600 hover:text-red-400 p-1 rounded transition-colors" title="Remover propriedade">
                         <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                     </button>
                 </div>
             </div>
             <button @click="addProperty" class="text-xs text-emerald-500 hover:text-emerald-400 hover:bg-emerald-500/10 px-2 py-1 rounded transition-colors mt-3 font-medium flex items-center gap-1">
                 <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="M12 5v14"/></svg> Adicionar Propriedade
             </button>
          </div>

          <!-- Meta/Header -->
          <div class="mb-8 border-b border-surface-700 pb-6 relative group flex-shrink-0">
        <input 
          type="text" 
          :value="docData.name || (docData.path ? docData.path.split('/').pop() : docData.autoTitle)"
          class="bg-transparent text-4xl font-bold tracking-tight text-surface-900 dark:text-surface-100 w-full outline-none placeholder:text-surface-600 focus:border-b focus:border-primary-500/30 transition-colors"
          placeholder="New Document Title"
          disabled
        />
        <div class="mt-4 flex flex-wrap gap-4 text-xs text-surface-500 items-center">
           <span class="max-w-[50%] flex items-center" :title="docData.path">
             <span class="truncate" dir="rtl">&lrm;{{ docData.path }}</span>
           </span>
           <span v-if="isBinaryFile" class="flex items-center gap-1.5 ml-2 text-amber-500/80 bg-amber-500/10 px-1.5 py-0.5 rounded text-[10px] font-medium border border-amber-500/20" title="Binário O.S protegido (Apenas Leitura via Pandoc/MuPdf)">
               <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
               Somente Leitura (Parser Dinâmico)
           </span>
           <span v-if="docData.has_vector && !docData.vector_id?.startsWith('ERROR')" class="flex items-center gap-1.5 ml-2 text-emerald-500/80 bg-emerald-500/10 px-1.5 py-0.5 rounded text-[10px] font-medium border border-emerald-500/20" title="Indexado para IA">
               <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
               <span class="font-mono opacity-80 uppercase tracking-widest">{{ docData.vector_id ? docData.vector_id.substring(0, 8) : 'VECTORIZED' }}</span>
           </span>
           <span v-else-if="!docData.has_vector || docData.vector_id?.startsWith('ERROR')" class="flex items-center gap-1.5 ml-2 text-zinc-500/80 bg-zinc-500/10 px-1.5 py-0.5 rounded text-[10px] font-medium border border-zinc-500/20" title="Ainda não lido pela arquitetura RAG Vector Database.">
               <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-60"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
               Não Indexado
           </span>
        </div>
        
        <!-- Tags -->
        <div class="mt-3 flex gap-2" v-if="docData.tags && docData.tags.length > 0">
           <span v-for="tag in docData.tags" :key="tag" class="px-2 py-0.5 bg-surface-800 text-surface-400 text-[11px] rounded uppercase font-medium tracking-wide border border-zinc-700">
             #{{ tag }}
           </span>
        </div>
      </div>
      
      <!-- TipTap Table Advanced Menu -->
      <bubble-menu 
        v-if="editor" 
        :editor="editor" 
        :should-show="shouldShowTableMenu"
        pluginKey="tableBubbleMenu"
        :tippy-options="{ duration: 150, placement: 'top' }"
        class="flex items-center gap-1 bg-surface-800 border border-surface-700 shadow-2xl rounded-lg px-2 py-1.5 backdrop-blur-md relative z-50 mb-2"
      >
        <!-- Columns Management -->
        <button @click="editor.chain().focus().addColumnBefore().run()" class="flex items-center gap-1 text-xs px-2 py-1 rounded text-surface-600 hover:text-white hover:bg-surface-700 transition-colors" title="Inserir Coluna à Esquerda">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 4v16"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h8"/><path d="M4 12h3M17 12h3M4 12H3"/><path d="M17 12h1"/></svg> Col +
        </button>
        <button @click="editor.chain().focus().deleteColumn().run()" class="flex items-center gap-1 text-xs px-2 py-1 rounded text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors" title="Excluir Coluna Atual">
           <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg> Col
        </button>

        <div class="h-4 w-px bg-surface-600 mx-0.5"></div>

        <!-- Rows Management -->
        <button @click="editor.chain().focus().addRowAfter().run()" class="flex items-center gap-1 text-xs px-2 py-1 rounded text-surface-300 hover:text-white hover:bg-surface-700 transition-colors" title="Inserir Linha Abaixo">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12h16"/><path d="M8 8v8"/><path d="M12 8v8"/><path d="M16 8v8"/><path d="M12 4v3M12 17v3M12 4V3"/><path d="M12 17v1"/></svg> Lin +
        </button>
        <button @click="editor.chain().focus().deleteRow().run()" class="flex items-center gap-1 text-xs px-2 py-1 rounded text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors" title="Excluir Linha Atual">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg> Lin
        </button>

        <div class="h-4 w-px bg-surface-600 mx-0.5"></div>

        <!-- Merging & Utilities -->
        <button @click="editor.chain().focus().mergeCells().run()" class="flex items-center gap-1 text-xs px-2 py-1 rounded text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 transition-colors" title="Mesclar Células Selecionadas">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 12h18"/><path d="M12 3v9"/></svg> Merge
        </button>
        
        <div class="h-4 w-px bg-surface-600 mx-0.5"></div>

        <!-- Delete Entire Table -->
        <button @click="editor.chain().focus().deleteTable().run()" class="flex items-center gap-1 text-xs p-1.5 rounded text-red-500 hover:text-red-400 hover:bg-red-500/20 transition-colors" title="Excluir Tabela Inteira">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
        </button>
      </bubble-menu>

      <!-- TipTap Bubble Menu (Floating Formatter - Oculto em Tabelas e Links) -->
      <bubble-menu 
        v-if="editor" 
        :editor="editor" 
        :should-show="shouldShowFormattingMenu"
        :tippy-options="{ duration: 150, zIndex: 50 }"
        class="flex items-center gap-0.5 bg-surface-900/85 backdrop-blur-xl border border-surface-700/60 shadow-2xl rounded-xl px-1.5 py-1 animate-in fade-in zoom-in-95"
      >
        <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'text-primary-400 bg-primary-500/10 shadow-sm border border-primary-500/20': editor.isActive('bold'), 'text-surface-300 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('bold') }" class="p-1.5 rounded-lg transition-all" title="Negrito (Cmd+B)">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 12a4 4 0 0 0 0-8H6v8"/><path d="M15 20a4 4 0 0 0 0-8H6v8Z"/></svg>
        </button>
        <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'text-primary-400 bg-primary-500/10 shadow-sm border border-primary-500/20': editor.isActive('italic'), 'text-surface-300 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('italic') }" class="p-1.5 rounded-lg transition-all" title="Itálico (Cmd+I)">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" x2="10" y1="4" y2="4"/><line x1="14" x2="5" y1="20" y2="20"/><line x1="15" x2="9" y1="4" y2="20"/></svg>
        </button>
        <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'text-primary-400 bg-primary-500/10 shadow-sm border border-primary-500/20': editor.isActive('strike'), 'text-surface-300 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('strike') }" class="p-1.5 rounded-lg transition-all" title="Tachado">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4H9a3 3 0 0 0-2.83 4"/><path d="M14 12a4 4 0 0 1 0 8H6"/><line x1="4" x2="20" y1="12" y2="12"/></svg>
        </button>
        <div class="h-5 w-px bg-surface-700/60 mx-1"></div>
        <button @click="editor.chain().focus().toggleCode().run()" :class="{ 'text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 shadow-sm': editor.isActive('code'), 'text-surface-300 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('code') }" class="p-1.5 rounded-lg transition-all" title="Código Inline">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </button>
        <button @click="editor.chain().focus().toggleBlockquote().run()" :class="{ 'text-primary-400 bg-primary-500/10 border border-primary-500/20 shadow-sm': editor.isActive('blockquote'), 'text-surface-300 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('blockquote') }" class="p-1.5 rounded-lg transition-all" title="Citação">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>
        </button>
        <div class="h-5 w-px bg-surface-700/60 mx-1"></div>
        <!-- Typography -->
        <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'text-primary-400 bg-primary-500/10 border border-primary-500/20 shadow-sm': editor.isActive('heading', { level: 1 }), 'text-surface-400 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('heading', { level: 1 }) }" class="p-1.5 rounded-lg transition-all font-bold text-xs" title="Título 1">H1</button>
        <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'text-primary-400 bg-primary-500/10 border border-primary-500/20 shadow-sm': editor.isActive('heading', { level: 2 }), 'text-surface-400 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('heading', { level: 2 }) }" class="p-1.5 rounded-lg transition-all font-bold text-xs" title="Título 2">H2</button>
        <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'text-primary-400 bg-primary-500/10 border border-primary-500/20 shadow-sm': editor.isActive('heading', { level: 3 }), 'text-surface-400 hover:text-white hover:bg-surface-700/50 border border-transparent': !editor.isActive('heading', { level: 3 }) }" class="p-1.5 rounded-lg transition-all font-bold text-xs" title="Título 3">H3</button>

        <div class="h-5 w-px bg-surface-700/60 mx-1"></div>
        <!-- AI Spotlight Injector -->
        <button @click="injectToSpotlight" class="flex items-center gap-1.5 px-2 py-1.5 text-[11px] font-bold tracking-wide rounded-lg text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-all whitespace-nowrap" title="Consultar AI sobre o trecho selecionado">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" class="animate-pulse" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> AI Ask
        </button>
      </bubble-menu>

      <!-- TipTap Floating Menu (Block Inserter) -->
      <floating-menu 
        v-if="editor" 
        :editor="editor" 
        :tippy-options="{ duration: 150, placement: 'left' }"
        class="flex flex-col gap-1 bg-surface-900 border border-surface-700 shadow-2xl rounded-lg p-1.5 backdrop-blur-md w-48"
      >
        <div class="text-[10px] font-bold text-surface-500 uppercase tracking-wider mb-1 px-2 pt-1 flex items-center justify-between">
           <span>Inserir Bloco</span>
           <span class="text-[8px] opacity-50 px-1 border border-surface-700 rounded bg-surface-800 text-surface-400">Markdown</span>
        </div>
        
        <!-- Headings -->
        <div class="grid grid-cols-3 gap-1 px-1 mb-1">
          <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" class="flex justify-center items-center py-1.5 rounded text-xs font-bold text-primary-500 hover:text-white hover:bg-primary-500/20 transition-colors">H1</button>
          <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" class="flex justify-center items-center py-1.5 rounded text-xs font-bold text-primary-500 hover:text-white hover:bg-primary-500/20 transition-colors">H2</button>
          <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" class="flex justify-center items-center py-1.5 rounded text-xs font-bold text-primary-500 hover:text-white hover:bg-primary-500/20 transition-colors">H3</button>
        </div>

        <div class="h-px bg-surface-700/50 my-1 mx-1"></div>

        <!-- Lists & Structure -->
        <button @click="editor.chain().focus().toggleBulletList().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-surface-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg> Lista
        </button>
        <button @click="editor.chain().focus().toggleOrderedList().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-surface-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" x2="21" y1="6" y2="6"/><line x1="10" x2="21" y1="12" y2="12"/><line x1="10" x2="21" y1="18" y2="18"/><path d="M4 6h1v4"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg> Numerada
        </button>
        <button @click="editor.chain().focus().toggleTaskList().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-surface-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 11 3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg> Tarefas (To-Do)
        </button>
        <button @click="editor.chain().focus().toggleBlockquote().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-surface-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg> Citação
        </button>
        <button @click="editor.chain().focus().toggleCodeBlock().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-surface-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg> Bloco de Código
        </button>
        <button @click="editor.chain().focus().setHorizontalRule().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-surface-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" x2="19" y1="12" y2="12"/></svg> Divisor Horizontal
        </button>

        <div class="h-px bg-surface-700/50 my-1 mx-1"></div>

        <!-- Tables -->
        <button @click="editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-surface-400 hover:text-white hover:bg-surface-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 text-primary-500"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg> Tabela (3x3)
        </button>

        <div class="h-px bg-surface-700/50 my-1 mx-1"></div>
        
        <!-- Extensões -->
        <button @click="insertPresentationBlock" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 transition-colors text-left w-full font-medium">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg> Slide (16:9)
        </button>
      </floating-menu>

      <!-- TipTap Editor -->
      <editor-content :editor="editor" class="flex-1 w-full prose max-w-none focus:outline-none pb-32" />

        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import { BubbleMenu, FloatingMenu } from '@tiptap/vue-3/menus'
import StarterKit from '@tiptap/starter-kit'
import Focus from '@tiptap/extension-focus'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableHeader from '@tiptap/extension-table-header'
import TableCell from '@tiptap/extension-table-cell'
import { Markdown } from 'tiptap-markdown'
import { VaultSyntaxHighlighter } from './decorators'
import { PresentationBlock } from './extensions/PresentationBlock'
import SlashCommand from './extensions/SlashCommand'
import suggestion from './extensions/suggestion'
import yaml from 'js-yaml'

// TipTap Extended Plugins for Data Ingestion
const SensusTableCell = TableCell.extend({
  name: 'tableCell',
  content: 'paragraph',
  addKeyboardShortcuts() {
    return {
      ...this.parent?.(),
      Enter: () => this.editor.commands.goToNextCell()
    }
  },
  addAttributes() {
    return {
      ...this.parent?.(),
      sensusValue: {
        default: null,
        parseHTML: element => element.getAttribute('data-sensus-value'),
        renderHTML: attributes => {
          if (!attributes.sensusValue) return {}
          return { 'data-sensus-value': attributes.sensusValue }
        }
      },
      sensusError: {
        default: false,
        parseHTML: element => element.getAttribute('data-sensus-error') === 'true',
        renderHTML: attributes => {
          if (!attributes.sensusError) return {}
          return { 'data-sensus-error': attributes.sensusError }
        }
      }
    }
  }
})

const SensusTableHeader = TableHeader.extend({
  name: 'tableHeader',
  content: 'paragraph',
  addKeyboardShortcuts() {
    return {
      ...this.parent?.(),
      Enter: () => this.editor.commands.goToNextCell()
    }
  },
  addAttributes() {
    return {
      ...this.parent?.(),
      sensusValue: {
        default: null,
        parseHTML: element => element.getAttribute('data-sensus-value'),
        renderHTML: attributes => {
          if (!attributes.sensusValue) return {}
          return { 'data-sensus-value': attributes.sensusValue }
        }
      },
      sensusError: {
        default: false,
        parseHTML: element => element.getAttribute('data-sensus-error') === 'true',
        renderHTML: attributes => {
          if (!attributes.sensusError) return {}
          return { 'data-sensus-error': attributes.sensusError }
        }
      }
    }
  }
})

const props = defineProps({
  fileId: { type: String, required: true },
  workspaceId: { type: Number, required: false }, // Fase 32 Multi-Drives
  viewMode: { type: String as () => 'visual' | 'source' | 'split', default: 'visual' }
})

const emit = defineEmits(['editor-stats', 'update-view-mode', 'editor-saving'])

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`
const RUST_CORE_URL = import.meta.env.VITE_RUST_CORE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:38001`
const isLoading = ref(true)
const fetchError = ref<string | null>(null)
const isSaving = ref(false)
let saveTimeout: ReturnType<typeof setTimeout> | null = null

// Spellcheck Preference Logic
const showSpellcheckPrompt = ref(false)
const spellcheckEnabled = ref(false)

// Document Properties State
const showProperties = ref(false)
const documentProperties = ref<Record<string, any>>({})

const docData = ref<any>({})
const rawMarkdown = ref('')
let sourceUpdateTimeout: ReturnType<typeof setTimeout> | null = null

const isBinaryFile = computed(() => {
    if (!docData.value?.name) return false
    const ext = docData.value.name.split('.').pop()?.toLowerCase() || ''
    return ['pdf', 'docx', 'odt', 'epub', 'rtf', 'pptx', 'xlsx'].includes(ext)
})

const isCodeFile = computed(() => {
    if (!docData.value?.name) return false
    const ext = docData.value.name.split('.').pop()?.toLowerCase() || ''
    return ['rs', 'py', 'ts', 'js', 'vue', 'json', 'toml', 'yaml', 'yml', 'sh', 'css', 'html', 'sql', 'cpp', 'c', 'go'].includes(ext)
})

const injectToSpotlight = () => {
    if (!editor.value) return
    const selection = editor.value.state.selection
    const text = editor.value.state.doc.textBetween(selection.from, selection.to, ' ')
    
    if (text && text.trim().length > 0) {
        window.dispatchEvent(new CustomEvent('sensus-spotlight-inject', { detail: { text: text.trim() } }))
    }
}

const injectFileToAI = () => {
    if (!docData.value?.path) return
    const sysPrompt = `Inicie Análise ou Estruturação Crítica O.S do documento atual: ${docData.value.path}`

    window.dispatchEvent(new CustomEvent('sensus-spotlight-inject', { 
         detail: { text: sysPrompt, autoSubmit: true } 
    }))
}

const parseFrontmatter = (markdown: string | undefined) => {
    if (!markdown) return { frontmatter: {}, content: '' }
    const yamlRegex = /^---\n([\s\S]*?)\n---(?:\n([\s\S]*))?$/
    const match = markdown.match(yamlRegex)
    if (match) {
        const safeMatchContent = match[2] || '';
        const contentAfterFrontmatter = safeMatchContent.trimStart();
        const linesData = contentAfterFrontmatter.split('\n');

        // Detect Title fallback if Frontmatter title empty
        const rawFirstLine = linesData[0];
        const autoTitle = rawFirstLine ? rawFirstLine.trim().replace(/^#{1,6}\s/, '') : 'Untitled Document';
        
        try {
            docData.value.frontmatter = yaml.load(match[1] as string) || {};
        } catch(e) {
            console.error("YAML Parse Error", e)
            docData.value.frontmatter = { "_invalid_yaml_parse_error": match[1] as string };
        }
        
        docData.value.content = contentAfterFrontmatter;
        docData.value.autoTitle = autoTitle;

        return {
            frontmatter: docData.value.frontmatter,
            content: docData.value.content
        }
    }
    const linesData = markdown ? markdown.split('\n') : [''];
    const rawFirstLine = linesData.length > 0 ? linesData[0] : '';
    const safeFirstLine = rawFirstLine || '';
    const autoTitle = safeFirstLine ? safeFirstLine.trim().replace(/^#{1,6}\s/, '') : 'Untitled Document';

    docData.value.frontmatter = {};
    docData.value.content = markdown;
    docData.value.autoTitle = autoTitle;
    
    return { frontmatter: {}, content: markdown }
}

const buildMarkdownWithFrontmatter = (content: string, propsObj: Record<string, any>) => {
    if (Object.keys(propsObj).length === 0) return content;
    try {
        const yamlString = yaml.dump(propsObj)
        return `---\n${yamlString}---\n${content}`
    } catch(e) {
        console.error("YAML Dump Error", e)
        return content
    }
}

const syncPropertiesToSource = () => {
    if (!editor.value) return;
    // @ts-expect-error
    let markdownContent = editor.value.storage.markdown.getMarkdown()
    
    // Sensus Patch: Evita que o TipTap escape os asteriscos de multiplicação em Fórmulas da Tabela
    markdownContent = markdownContent.split('\n').map((line: string) => {
        if (line.trim().startsWith('|') && line.includes('=')) return line.replace(/\\\*/g, '*');
        return line;
    }).join('\n');

    const fullMarkdown = buildMarkdownWithFrontmatter(markdownContent, documentProperties.value)
    rawMarkdown.value = fullMarkdown
    debounceSave(fullMarkdown)
    computeEditorStats(fullMarkdown)
}

const renameProperty = (oldKey: string, newKey: string) => {
    if (!newKey || newKey === oldKey) return;
    const value = documentProperties.value[oldKey]
    delete documentProperties.value[oldKey]
    documentProperties.value[newKey] = value
    syncPropertiesToSource()
}

const removeProperty = (key: string) => {
    delete documentProperties.value[key]
    syncPropertiesToSource()
}

const addProperty = () => {
    let key = "nova_prop"
    let counter = 1
    while (documentProperties.value[key]) {
        key = `nova_prop_${counter++}`
    }
    documentProperties.value[key] = ""
    syncPropertiesToSource()
}

// Cell Tracking for Smart Tables
const hoveredCellCoordinate = ref<string | null>(null)
const hoveredCellPosition = ref({ x: 0, y: 0 })

const handleEditorMouseMove = (e: MouseEvent) => {
    if (props.viewMode === 'source') {
        hoveredCellCoordinate.value = null; return;
    }
    
    const target = e.target as HTMLElement
    const cell = target.closest('td, th') as HTMLTableCellElement | null
    
    if (cell) {
        const row = cell.parentElement as HTMLTableRowElement
        const colLetter = String.fromCharCode(65 + cell.cellIndex)
        const rowNumber = row.rowIndex + 1
        
        hoveredCellCoordinate.value = `${colLetter}${rowNumber}`
        
        const rect = cell.getBoundingClientRect()
        // Anchor to Top-Right inside the cell
        hoveredCellPosition.value = {
            x: rect.right - 26,
            y: rect.top + 4
        }
    } else {
        hoveredCellCoordinate.value = null
    }
}

// Menu Visibility Handlers
const shouldShowTableMenu = ({ editor }: any) => {
    return editor.isActive('table')
}

const shouldShowFormattingMenu = ({ editor, from, to }: any) => {
    // Only show if there's a text selection and we are NOT in a table
    const isTable = editor.isActive('table')
    const hasSelection = from !== to
    return hasSelection && !isTable
}

let tableEvaluateTimeout: ReturnType<typeof setTimeout> | null = null

const debounceTableEvaluate = (editorInstance: any) => {
    if (tableEvaluateTimeout) clearTimeout(tableEvaluateTimeout)
    tableEvaluateTimeout = setTimeout(async () => {
        try {
            const tableEl = editorInstance.view.dom.querySelector('table')
            if (!tableEl) return;
            
            const cells: Record<string, string> = {}
            const rows = tableEl.querySelectorAll('tr')
            rows.forEach((row: any, rIdx: number) => {
                const cols = row.querySelectorAll('td, th')
                cols.forEach((col: any, cIdx: number) => {
                     const colLetter = String.fromCharCode(65 + cIdx)
                     const rowNumber = rIdx + 1
                     cells[`${colLetter}${rowNumber}`] = col.textContent.trim()
                })
            })

            const token = localStorage.getItem('sovereign_token')
            const headers: Record<string, string> = { "Content-Type": "application/json" }
            if (token) headers['Authorization'] = `Bearer ${token}`
            
            // Tenta enviar para avaliação matemática no Back-end
            const res = await fetch(`${API_BASE_URL}/v1/vault/table/evaluate`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ cells, deleted_column: null })
            })
            
            if (res.ok) {
                const data = await res.json()
                
                // Inject Results visuais (data.results) e Erros (data.errors) de volta na UI via ProseMirror (Não polui undo-history)
                const { state, view } = editorInstance;
                let tr = state.tr;
                let modified = false;
                
                let rIdx = 0;
                let cIdx = 0;
                state.doc.descendants((node: any, pos: number) => {
                    if (node.type.name === 'table') rIdx = 0;
                    if (node.type.name === 'tableRow') {
                        rIdx++;
                        cIdx = 0;
                    }
                    if (node.type.name === 'tableCell' || node.type.name === 'tableHeader') {
                        const colLetter = String.fromCharCode(65 + cIdx);
                        const cellId = `${colLetter}${rIdx}`;
                        const rawContent = cells[cellId] || "";
                        
                        const result = data.results[cellId];
                        const hasError = data.errors[cellId] !== undefined;
                        const isFocused = state.selection.from >= pos && state.selection.to <= pos + node.nodeSize;
                        
                        // Avoid mutating the currently focused cell to prevent ProseMirror from destroying cursor state
                        if (!isFocused) {
                            // O Visor Matemático de cálculo só cobre células cujo conteúdo inicia com '=' ou tem erros
                            if (rawContent.startsWith('=') || hasError) {
                                if (node.attrs.sensusValue !== result || !!node.attrs.sensusError !== hasError) {
                                   tr = tr.setNodeMarkup(pos, null, {
                                       ...node.attrs,
                                       sensusValue: result,
                                       sensusError: hasError
                                   });
                                   modified = true;
                                }
                            } else {
                                if (node.attrs.sensusValue !== null || node.attrs.sensusError !== false) {
                                   tr = tr.setNodeMarkup(pos, null, { ...node.attrs, sensusValue: null, sensusError: false });
                                   modified = true;
                                }
                            }
                        }
                        
                        cIdx++;
                    }
                });
                
                if (modified) {
                    view.dispatch(tr);
                    setTimeout(() => {
                        console.log("FINAL C1 MATCH ->", document.querySelector('[data-sensus-value]')?.outerHTML)
                        console.log("FULL TABLE DOM ->", editorInstance.view.dom.querySelector('table')?.outerHTML)
                    }, 100)
                }
                
                if (Object.keys(data.errors).length > 0) {
                    // Notificando o sistema de que há uma referência falha
                    console.warn("Table AST Errors Detected:", data.errors)
                }
            }
        } catch(e) {
            console.error("The Accountant Sync Error", e)
        }
    }, 1500) // Aguarda a edicação acalmar (1.5s)
}

const handleSourceInput = () => {
    debounceSave(rawMarkdown.value)
    computeEditorStats(rawMarkdown.value)
    
    const parsed = parseFrontmatter(rawMarkdown.value)
    documentProperties.value = parsed.frontmatter as Record<string, any>
    
    if (editor.value && props.viewMode === 'split') {
        if (sourceUpdateTimeout) clearTimeout(sourceUpdateTimeout)
        sourceUpdateTimeout = setTimeout(() => {
            // Sincroniza TipTap com Source sem triggar onUpdate infinito e sem Frontmatter
            editor.value?.commands.setContent(parsed.content, { emitUpdate: false })
            computeEditorStats(rawMarkdown.value)
            setTimeout(() => debounceTableEvaluate(editor.value), 100)
        }, 500)
    }
}

const editor = useEditor({
  content: '', 
  extensions: [
    StarterKit,
    Focus.configure({
      className: 'has-focus',
      mode: 'all',
    }),
    Markdown.configure({
        // Extract raw markdown instead of HTML
    }),
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ 
        resizable: true,
        HTMLAttributes: {
          class: 'border-collapse table-auto w-full my-6 bg-surface-800/50 rounded overflow-hidden shadow-sm border border-surface-700'
        }
    }),
    TableRow.configure({
        HTMLAttributes: {
           class: 'border-b border-surface-700 hover:bg-surface-700/50 transition-colors'
        }
    }),
    SensusTableHeader.configure({
        HTMLAttributes: {
           class: 'border border-surface-600 bg-surface-700/80 text-surface-200 font-semibold p-2 text-left text-sm'
        }
    }),
    SensusTableCell.configure({
        HTMLAttributes: {
           class: 'border border-surface-700 p-2 text-surface-300 text-sm align-top break-words'
        }
    }),
    VaultSyntaxHighlighter,
    PresentationBlock,
    SlashCommand.configure({ suggestion }),
  ],
  editorProps: {
    attributes: {
      class: 'tiptap ProseMirror focus:outline-none min-h-[500px] text-lg leading-relaxed text-surface-300',
    },
  },
  onUpdate: ({ editor }) => {
    // Convert current TipTap Editor State into pure Markdown
    // @ts-expect-error extension typings inject this dynamically
    let markdownContent = editor.storage.markdown.getMarkdown() 
    
    // Sensus Patch: Evita que o TipTap escape os asteriscos de multiplicação em Fórmulas da Tabela
    markdownContent = markdownContent.split('\n').map((line: string) => {
        if (line.trim().startsWith('|') && line.includes('=')) return line.replace(/\\\*/g, '*');
        return line;
    }).join('\n');

    const fullMarkdown = buildMarkdownWithFrontmatter(markdownContent, documentProperties.value)
    
    if (props.viewMode === 'visual' || props.viewMode === 'split') {
        rawMarkdown.value = fullMarkdown
    }
    debounceSave(fullMarkdown)
    computeEditorStats(fullMarkdown)
    
    if (editor.isActive('table')) {
        debounceTableEvaluate(editor)
    }
  },
  onSelectionUpdate: ({ editor }) => {
    // Retriggers AST verification when cursor selection changes to fix the "> 1.5s stationary cursor freezing" bug
    if (editor.isActive('table')) {
        debounceTableEvaluate(editor)
    }
  }
})

const computeEditorStats = (markdown: string) => {
    // Basic word count splitting by whitespace
    const words = markdown.trim().split(/\s+/).filter(w => w.length > 0)
    
    // TipTap Markdown ext often escapes literal consecutive brackets as \[\[
    const unescapedMarkdown = markdown.replace(/\\/g, '')
    const links = (unescapedMarkdown.match(/\[\[.*?\]\]/g) || []).length
    
    emit('editor-stats', {
        words: words.length,
        links: links,
        path: docData.value?.path || props.fileId || 'N/A'
    })
}

const insertPresentationBlock = () => {
    if (editor.value) {
        // @ts-expect-error Custom TipTap command not typed in ChainedCommands
        editor.value.chain().focus().setPresentationBlock().run()
    }
}

const fetchDocument = async () => {
    isLoading.value = true
    fetchError.value = null
    try {
        const token = localStorage.getItem('sovereign_token')
        const headers: Record<string, string> = {}
        if (token) headers['Authorization'] = `Bearer ${token}`

        const res = await fetch(`${RUST_CORE_URL}/v1/vault/document/${props.fileId}`, { headers })
        if (!res.ok) throw new Error("Documento não encontrado no Vault")
        
        docData.value = await res.json()
        
        // Atualiza o TipTap com o Markdown puro e diz pra não emitir update para evitar loop de savar inicial
        rawMarkdown.value = docData.value.content
        const parsed = parseFrontmatter(docData.value.content)
        documentProperties.value = parsed.frontmatter as Record<string, any>
        
        if (editor.value) {
           editor.value.commands.setContent(parsed.content, { emitUpdate: false }) 
           editor.value.setEditable(!isBinaryFile.value)
           computeEditorStats(docData.value.content)
           setTimeout(() => debounceTableEvaluate(editor.value), 500)
        }
        
    } catch(err: any) {
        fetchError.value = err.message
    } finally {
        isLoading.value = false
    }
}

const handleTocRequest = () => {
    if (!editor.value) {
        window.dispatchEvent(new CustomEvent('sensus-toc-ready', { detail: { items: [] } }))
        return
    }

    const jsonContent = editor.value.getJSON()
    if (!jsonContent.content) {
        window.dispatchEvent(new CustomEvent('sensus-toc-ready', { detail: { items: [] } }))
        return
    }

    const headings: Array<{level: number, text: string, id: string}> = []
    let counter = 0
    
    // Varredura Linear no AST do TipTap
    const traverse = (nodes: any[]) => {
       for (const node of nodes) {
           if (node.type === 'heading' && node.content && node.content.length > 0) {
              const text = node.content.map((n: any) => n.text).join('')
              headings.push({
                 level: node.attrs?.level || 1,
                 text: text,
                 id: `heading-${counter++}`
              })
           }
           if (node.content) {
              traverse(node.content)
           }
       }
    }
    
    traverse(jsonContent.content)
    
    // Responde ao Vue Root
    window.dispatchEvent(new CustomEvent('sensus-toc-ready', { detail: { items: headings } }))
}

const debounceSave = (content: string) => {
    if (isBinaryFile.value) return; // Disarms I/O saving mutabilities over OS binaries
    isSaving.value = true
    emit('editor-saving', true)
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(() => {
        saveDocument(content)
    }, 1500) // 1.5s debounce local
}

const saveDocument = async (markdownContent: string) => {
    if (!props.fileId) return
    
    try {
        const token = localStorage.getItem('sovereign_token')
        
        // O conteúdo já vem como Markdown correto do TipTap (editor.storage.markdown.getMarkdown())
        // Reconstrói com frontmatter se existir
        let finalOutput = markdownContent
        if (Object.keys(docData.value.frontmatter).length > 0) {
            const yamlStr = yaml.dump(docData.value.frontmatter)
            finalOutput = `---\n${yamlStr}---\n${markdownContent}`
        }

        const res = await fetch(`${RUST_CORE_URL}/v1/vault/document/${encodeURIComponent(props.fileId)}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            },
            body: JSON.stringify({
                 workspace_id: props.workspaceId ? Number(props.workspaceId) : null,
                 file_path: props.fileId,
                 content: finalOutput
            })
        })
        
        if (!res.ok) throw new Error('Falha ao salvar')
    } catch(e) {
        console.error("Auto-Save error", e)
    } finally {
        setTimeout(() => {
            isSaving.value = false
            emit('editor-saving', false)
        }, 800)
    }
}

// Em caso de troca de documento com o mesmo componente Editor montado
watch(() => props.fileId, (newId) => {
    if (newId) fetchDocument()
})

watch(() => props.viewMode, (newMode) => {
    if ((newMode === 'visual' || newMode === 'split') && editor.value) {
         setTimeout(() => debounceTableEvaluate(editor.value), 500)
    }
})

const handleTocNavigate = (e: Event) => {
  const customEvent = e as CustomEvent
  const targetText = customEvent.detail?.text
  
  if (!targetText || !editor.value) return
  
  const proseMirrorRawDom = document.querySelector('.ProseMirror')
  if (!proseMirrorRawDom) return
  
  const headers = proseMirrorRawDom.querySelectorAll('h1, h2, h3')
  for (const header of headers) {
    if (header.textContent === targetText) {
       header.scrollIntoView({ behavior: 'smooth', block: 'start' })
       
       const htmlHeader = header as HTMLElement
       const originalBg = htmlHeader.style.backgroundColor
       const originalColor = htmlHeader.style.color
       
       htmlHeader.style.transition = 'all 0.3s ease'
       htmlHeader.style.backgroundColor = 'rgba(16, 185, 129, 0.2)' 
       htmlHeader.style.color = '#10B981'
       
       setTimeout(() => {
         htmlHeader.style.backgroundColor = originalBg
         htmlHeader.style.color = originalColor
       }, 1200)
       
       break
    }
  }
}

const checkSpellcheckPreference = () => {
    const pref = localStorage.getItem('sensus_spellcheck')
    if (pref === null) {
        showSpellcheckPrompt.value = true
        spellcheckEnabled.value = false // Default off
    } else {
        showSpellcheckPrompt.value = false
        spellcheckEnabled.value = pref === 'true'
        updateEditorSpellcheck()
    }
}

const setSpellcheck = (enable: boolean) => {
    spellcheckEnabled.value = enable
    localStorage.setItem('sensus_spellcheck', enable.toString())
    showSpellcheckPrompt.value = false
    updateEditorSpellcheck()
}

const updateEditorSpellcheck = () => {
    if (editor.value) {
        editor.value.setOptions({
            editorProps: {
                ...editor.value.options.editorProps,
                attributes: {
                    ...editor.value.options.editorProps?.attributes,
                    spellcheck: spellcheckEnabled.value ? 'true' : 'false',
                    class: 'tiptap ProseMirror focus:outline-none min-h-[500px] text-lg leading-relaxed text-surface-300',
                }
            }
        })
    }
}

onMounted(() => {
    fetchDocument()
    checkSpellcheckPreference()
    
    // Registra ouvinte global para o Table_Of_Contents (TOC) Modal
    window.addEventListener('sensus-toc-navigate', handleTocNavigate)
    window.addEventListener('sensus-request-toc', handleTocRequest)
})

onBeforeUnmount(() => {
    if (saveTimeout) clearTimeout(saveTimeout)
    
    window.removeEventListener('sensus-toc-navigate', handleTocNavigate)
    window.removeEventListener('sensus-request-toc', handleTocRequest)
})
</script>

<style>
/* Estilos essenciais do TipTap */
.tiptap p.is-editor-empty:first-child::before {
  color: #52525b;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
.tiptap ul[data-type="taskList"] {
  list-style: none;
  padding: 0;
}
.tiptap li[data-type="taskItem"] {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}
.tiptap li[data-type="taskItem"] > label {
  margin-right: 0.5rem;
  user-select: none;
}

/* Tabela Sensus - Visualização Mágica de Fórmulas */
.tiptap td[data-sensus-value]:not([data-sensus-value=""]),
.tiptap th[data-sensus-value]:not([data-sensus-value=""]),
.tiptap td[data-sensus-error="true"],
.tiptap th[data-sensus-error="true"] {
  position: relative;
}

/* Esconde o texto real APENAS quando não tem foco */
.tiptap td[data-sensus-value]:not([data-sensus-value=""]):not(.has-focus) > p,
.tiptap th[data-sensus-value]:not([data-sensus-value=""]):not(.has-focus) > p,
.tiptap td[data-sensus-error="true"]:not(.has-focus) > p,
.tiptap th[data-sensus-error="true"]:not(.has-focus) > p {
  color: transparent !important;
  caret-color: transparent !important;
  min-height: 1.5rem;
}
.tiptap td[data-sensus-value]:not([data-sensus-value=""]):not(.has-focus) > p::selection,
.tiptap th[data-sensus-value]:not([data-sensus-value=""]):not(.has-focus) > p::selection,
.tiptap td[data-sensus-error="true"]:not(.has-focus) > p::selection,
.tiptap th[data-sensus-error="true"]:not(.has-focus) > p::selection {
  background: transparent !important;
  color: transparent !important;
}

/* Mostra o resultado calculado APENAS quando não tem foco */
.tiptap td[data-sensus-value]:not([data-sensus-value=""]):not(.has-focus)::before,
.tiptap th[data-sensus-value]:not([data-sensus-value=""]):not(.has-focus)::before {
  content: attr(data-sensus-value);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: inherit;
  padding-left: 0.75em;
  padding-top: 0.57em;
  background-color: transparent;
  color: #10B981 !important; /* Verde esmeralda para valores matematicos */
  font-weight: bold;
  pointer-events: none;
}

/* Erros de Fórmula Específicos (Sobrescrevem o verde) */
.tiptap td[data-sensus-error="true"]:not(.has-focus)::before,
.tiptap th[data-sensus-error="true"]:not(.has-focus)::before {
  content: "#ERROR!";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: inherit;
  padding-left: 0.75em;
  padding-top: 0.57em;
  background-color: transparent;
  color: #EF4444 !important; /* Vermelho para erro */
  font-weight: bold;
  pointer-events: none;
}
</style>
