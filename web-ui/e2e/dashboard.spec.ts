import { test, expect } from '@playwright/test';

test.describe('Dashboard View E2E', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to a blank page on the site's origin to set localStorage first
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('sovereign_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJKZWZlcnNvbiIsImV4cCI6MTc3MzE5NjY3NH0.MYwyQBf1IcSxxmT_mxTzJKgynZ-ovfYfqABafcsVeeI');
        });

        // Navigate to the dashboard
        await page.goto('/dashboard');
        // Assuming there is some initialization or we just wait for it to load
        await page.waitForTimeout(1000);
    });

    test('should display the Sensus Dashboard header', async ({ page }) => {
        await expect(page.locator('text=Centro de Comando Temporal')).toBeVisible();
        await expect(page.locator('text=Sovereign Cognitive Hub')).toBeVisible();
    });

    test('should render the Atividades Recentes section', async ({ page }) => {
        await expect(page.locator('text=Fluxo de Conhecimento (Notas Modificadas)')).toBeVisible();
    });

    test('should render the Pendências (Vault Tasks) section', async ({ page }) => {
        await expect(page.locator('text=Ações Requeridas (Vault Tasks)')).toBeVisible();
    });
});
