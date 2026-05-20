<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

    import { Mic, Loader2, Square } from 'lucide-svelte';
    import { createEventDispatcher, onDestroy, onMount } from 'svelte';
    import { fly } from 'svelte/transition';

    let { disabled = false }: { disabled?: boolean } = $props();
    
    const dispatch = createEventDispatcher();
    
    let isRecording = $state(false);
    let isTranscribing = $state(false);
    let mediaRecorder: MediaRecorder | null = null;
    let audioChunks: Blob[] = [];
    let stream: MediaStream | null = null;
    let recordingTime = $state(0);
    let timerInterval: any = null;

    async function startRecording() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Try to use a codec that Whisper can easily ingest (webm/opus is default on browsers)
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                isRecording = false;
                clearInterval(timerInterval);
                recordingTime = 0;
                
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendToWhisper(audioBlob);
                
                // Cleanup stream tracks
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            };

            mediaRecorder.start();
            isRecording = true;
            
            timerInterval = setInterval(() => {
                recordingTime++;
            }, 1000);
            
        } catch (err) {
            console.error("Microphone access denied or failed:", err);
            dispatch('error', 'Microphone access denied.');
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
        }
    }

    async function sendToWhisper(blob: Blob) {
        isTranscribing = true;
        
        const formData = new FormData();
        // The endpoint api_multimodal.rs expects the field "audio"
        formData.append('audio', blob, 'recording.webm');
        
        try {
            const response = await fetch(`${API_BASE_URL}/v1/multimodal/audio/transcribe`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.text) {
                    dispatch('transcription', data.text);
                } else {
                    dispatch('error', data.error || 'Transcription failed');
                }
            } else {
                dispatch('error', 'HTTP ' + response.status);
            }
        } catch (err) {
            console.error("Transcriber API error:", err);
            dispatch('error', 'API error.');
        } finally {
            isTranscribing = false;
        }
    }
    
    function toggleRecording() {
        if (disabled && !isRecording && !isTranscribing) return;
        
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }
    
    function formatTime(seconds: number): string {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    }

    onDestroy(() => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        clearInterval(timerInterval);
    });
</script>

<div class="relative flex items-center">
    {#if isRecording}
        <div transition:fly={{ y: 5, duration: 200 }} class="absolute -top-10 left-1/2 -translate-x-1/2 bg-rose-500 text-white text-[10px] font-bold px-2 py-1 rounded shadow-lg flex items-center gap-1.5 whitespace-nowrap">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            {formatTime(recordingTime)}
        </div>
    {/if}

    <button type="button" 
        onclick={toggleRecording}
        disabled={disabled && !isRecording && !isTranscribing}
        class="p-2.5 rounded-lg transition-colors cursor-pointer disabled:opacity-50 flex items-center gap-2 group {isRecording ? 'text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10' : 'text-slate-400 dark:text-slate-500 hover:text-indigo-500 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-[#1d253b]'}" 
        title={isRecording ? 'Stop Recording' : 'Voice Typing (Whisper)'}>
        
        {#if isTranscribing}
            <Loader2 class="w-5 h-5 animate-spin text-indigo-500" />
        {:else if isRecording}
            <Square class="w-5 h-5 fill-rose-500" />
        {:else}
            <Mic class="w-5 h-5" />
        {/if}
    </button>
</div>
