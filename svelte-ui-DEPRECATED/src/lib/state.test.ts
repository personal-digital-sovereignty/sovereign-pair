import { expect, test, describe } from 'vitest';
import { globalState, toggleSidebar, setSidebarWidth } from './state.svelte';

describe('Global OS Core State ($state Runes)', () => {
    test('Should initialize with expanded sidebar and standard width', () => {
        expect(globalState.isSidebarOpen).toBe(true);
        expect(globalState.sidebarWidth).toBe(260);
    });

    test('Should toggle sidebar expansion autonomously', () => {
        const initialState = globalState.isSidebarOpen;
        toggleSidebar();
        expect(globalState.isSidebarOpen).toBe(!initialState);
        toggleSidebar(); // Revert
    });

    test('Should respect boundaries when setting width', () => {
        setSidebarWidth(150); // Under minimum bounding box (usually ~200)
        // Note: The logic in state.svelte.ts enforces boundaries: Math.max(200, Math.min(600, w))
        expect(globalState.sidebarWidth).toBe(200);

        setSidebarWidth(800); // Over maximum bounding box
        expect(globalState.sidebarWidth).toBe(600);
        
        setSidebarWidth(350); // Valid
        expect(globalState.sidebarWidth).toBe(350);
    });
});
