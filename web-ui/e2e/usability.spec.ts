import { test, expect } from '@playwright/test';

test.describe('Usability and Physical Limits E2E', () => {

    test.beforeEach(async ({ page }) => {
        // Authenticate implicitly
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('sovereign_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_e2e_token');
        });

        // Mock Basic Backend
        await page.route('**/v1/**', route => {
            const url = route.request().url();
            if (url.includes('/auth/status')) return route.fulfill({ status: 200, json: { is_setup: true } });
            if (url.includes('/settings')) return route.fulfill({ status: 200, json: { sensus_mode: 'standard' } });

            // For the Graph Stress Test
            if (url.includes('/vault/graph')) {
                // Generate 1500 nodes and 2000 links
                const nodes = [];
                const links = [];
                for (let i = 0; i < 1500; i++) {
                    nodes.push({ id: `node_${i}`, name: `Massive Node ${i}`, type: i % 5 === 0 ? 'folder' : 'file', val: (i % 3) + 1 });
                    if (i > 0) {
                        links.push({ source: `node_${i}`, target: `node_${Math.floor(Math.random() * i)}`, type: 'semantic' });
                    }
                }
                return route.fulfill({ status: 200, json: { nodes, links } });
            }
            return route.fulfill({ status: 200, json: {} });
        });
    });

    test('should maintain layout containment on Mobile Viewports (Responsiveness)', async ({ page }) => {
        // iPhone 12 Pro dimensions
        await page.setViewportSize({ width: 390, height: 844 });

        await page.goto('/dashboard');
        await page.waitForTimeout(1500);

        // Core Layout containers shouldn't blow past the strict 100vw
        const width = await page.evaluate(() => document.documentElement.scrollWidth);
        const windowWidth = await page.evaluate(() => window.innerWidth);

        // Assert no horizontal scrollbar overflow leak caused by bad CSS
        expect(width).toBeLessThanOrEqual(windowWidth);

        // Activity Bar should remain constrained
        const nav = page.locator('nav');
        await expect(nav).toBeVisible();
    });

    test('should NOT crash the GPU Physics Engine under Massive DOM/Canvas Loads (CognitiveGraph)', async ({ page }) => {
        // Standard Desktop Viewport
        await page.setViewportSize({ width: 1920, height: 1080 });

        // Log performance metrics
        page.on('console', msg => {
            if (msg.type() === 'error') console.log('GPU/CANVAS ERROR:', msg.text());
        });

        await page.goto('/dashboard');

        // Navigate to Cognitive Graph (Triggers massive load mocked above)
        await page.getByRole('button', { name: 'Grafo Cognitivo' }).click();

        // Wait 3 seconds for D3 Force Physics to stabilize the 1500 elements
        await page.waitForTimeout(3000);

        // Verify Canvas is rendered and injected (Vue ref='graphContainer')
        const canvasCount = await page.locator('canvas').count();
        expect(canvasCount).toBeGreaterThan(0);

        // Verify the UI didn't freeze completely by checking the overlay DOM update
        await expect(page.locator('text=1500 NODES')).toBeVisible();

        // If Playwright made it here, the page didn't OOM (Out of Memory) crash on Chromium
        expect(true).toBeTruthy();
    });

});
