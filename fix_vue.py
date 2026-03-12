import re

with open('web-ui/src/views/DashboardView.vue', 'r') as f:
    content = f.read()

pattern = re.compile(r'(<!-- THE GOD MODE COCKPIT.*?)(<!-- QUARANTINE)', re.DOTALL)

new_cockpit = r'''<!-- THE GOD MODE COCKPIT (PHASE 27: FULL-WIDTH MASTERPLAN) -->
        <div v-show="activeTab === 'cockpit'" class="absolute inset-0 w-full h-full overflow-y-auto p-6 bg-surface-900/90 custom-scroll">
            <div class="w-full flex flex-col gap-6 relative min-h-full">
                
                <!-- O.S Terminal Integrado (The Hacker's CLI) -->
                <HackerCommandLine class="shrink-0 z-20" />
                
                <!-- Tri-Core Trackers (Telemetria, Cronos, RAG) -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 shrink-0 min-h-[220px]">
                    <div class="bg-surface-900/80 border border-surface-700/50 rounded-xl overflow-hidden relative p-4 flex flex-col justify-center shadow-xl">
                        <TokenMetricsTracker />
                    </div>
                    
                    <CronosTimeMap class="h-full shadow-xl" />
                    <RagPipelineTracker class="h-full shadow-xl" />
                </div>
                
                <!-- Sovereign Event Stream -->
                <div class="flex-1 min-h-[300px] h-full bg-surface-900/80 border border-surface-700/50 rounded-xl overflow-hidden flex flex-col p-4 custom-scroll shadow-xl">
                    <RealtimeLogs />
                </div>

            </div>
        </div>

        '''

new_content = pattern.sub(new_cockpit + r'\2', content)

with open('web-ui/src/views/DashboardView.vue', 'w') as f:
    f.write(new_content)
