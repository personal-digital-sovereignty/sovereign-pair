import { test, expect } from '@playwright/test';

test.describe('Top-Level Navigation E2E', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('sovereign_token', 'fake-session-auth-id-string');
        });

        // Mock Backend API
        await page.route('**/v1/**', route => {
            const url = route.request().url();
            if (url.includes('/auth/status')) return route.fulfill({ status: 200, json: { is_setup: true } });
            if (url.includes('/settings')) return route.fulfill({ status: 200, json: { sensus_mode: 'standard', db_encryption_key: null } });
            if (url.includes('/projects')) return route.fulfill({ status: 200, json: [] });
            return route.fulfill({ status: 200, json: {} });
        });

        await page.goto('/dashboard');
        await page.waitForTimeout(1000);
    });

    test('should load the App and Sidebar Navigation without crashing', async ({ page }) => {
        // Verifica que o Sidebar carrega
        await expect(page.locator('nav').first()).toBeVisible();
    });

    test('should navigate to Sovereign Chat', async ({ page }) => {
        // Rota /chat (Sovereign Chat)
        await page.goto('/chat');
        await expect(page.getByRole('heading', { name: 'Sovereign Pair' }).first()).toBeVisible();
        await expect(page.getByPlaceholder('Mensagem para Sovereign Pair...')).toBeVisible();
    });

    test('should navigate to Settings View', async ({ page }) => {
        // Rota /settings
        await page.goto('/settings');
        // Deve carregar o header
        await expect(page.locator('text=Configurações da Engine')).toBeVisible();
    });
});
