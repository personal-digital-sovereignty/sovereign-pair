import { test, expect } from '@playwright/test';

test.describe('Dashboard View E2E (Sovereign Masterplan)', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('sovereign_token', 'fake-session-auth-id-string');
        });

        // Mock Backend API
        await page.route('**/v1/**', route => {
            const url = route.request().url();
            if (url.includes('/auth/status')) return route.fulfill({ status: 200, json: { is_setup: true } });
            if (url.includes('/settings')) return route.fulfill({ status: 200, json: { sensus_mode: 'standard' } });
            return route.fulfill({ status: 200, json: {} });
        });

        await page.goto('/dashboard');
        await page.waitForTimeout(1000);
    });

    test('should display the Sovereign Masterplan header', async ({ page }) => {
        await expect(page.locator('text=Sovereign Masterplan (God Mode)')).toBeVisible();
        await expect(page.locator('text=Terminal Cíbrido Integrado & Observabilidade de LLMs')).toBeVisible();
    });

    test('should render the Overview Tab (Tri-Core)', async ({ page }) => {
        // Aba Overview ativa (padrão)
        await expect(page.locator('text=Overview').first()).toBeVisible();

        // Deve carregar o HackerCommandLine (Terminal) e TokenMetrics
        await expect(page.locator('text=System Ready')).toBeVisible();
    });

    test('should navigate to Cognitive Graph Tab', async ({ page }) => {
        // Clicar na aba Graph
        await page.locator('text=Cognitive Graph').first().click();

        // Verifica se componentes do Graph carregaram (Canvas)
        const canvas = page.locator('canvas');
        await expect(canvas.first()).toBeVisible();
    });
});
