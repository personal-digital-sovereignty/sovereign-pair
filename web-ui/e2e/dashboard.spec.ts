import { test, expect } from '@playwright/test';

test.describe('Dashboard View E2E', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to a blank page on the site's origin to set localStorage first
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('sovereign_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJKZWZlcnNvbiIsImV4cCI6MTc3MzE5NjY3NH0.MYwyQBf1IcSxxmT_mxTzJKgynZ-ovfYfqABafcsVeeI');
        });

        // Mock Backend API (Zero Tech-Debt E2E Iso)
        await page.route('**/v1/**', route => {
            const url = route.request().url();
            if (url.includes('/agenda')) {
                return route.fulfill({
                    status: 200,
                    json: {
                        'today': { docs: [], tasks: [] },
                        'this_week': { docs: [], tasks: [] },
                        'this_month': { docs: [], tasks: [] }
                    }
                });
            }
            if (url.includes('/auth/status')) return route.fulfill({ status: 200, json: { is_setup: true } });
            if (url.includes('/settings')) return route.fulfill({ status: 200, json: { sensus_mode: 'standard' } });
            if (url.includes('/projects')) return route.fulfill({ status: 200, json: [] });
            return route.fulfill({ status: 200, json: {} });
        });

        // Log browser errors and page content
        page.on('console', msg => console.log('BROWSER CONSOLE: ', msg.type(), msg.text()));
        page.on('pageerror', error => console.log('BROWSER PAGE ERROR: ', error.message));

        // Navigate to the dashboard
        await page.goto('/dashboard');
        await page.waitForTimeout(1000);
        console.log('DOM POST-LOAD: ', await page.content());
    });

    test('should display the Sensus Dashboard header', async ({ page }) => {
        await expect(page.locator('text=Centro de Comando Temporal')).toBeVisible();
        await expect(page.locator('text=Sovereign Cognitive Hub')).toBeVisible();
    });

    test('should render the Atividades Recentes section', async ({ page }) => {
        await page.getByRole('button', { name: 'Hoje' }).click();
        await expect(page.locator('text=Fluxo de Conhecimento (Notas Modificadas)')).toBeVisible();
    });

    test('should render the Pendências (Vault Tasks) section', async ({ page }) => {
        await page.getByRole('button', { name: 'Hoje' }).click();
        await expect(page.locator('text=Ações Requeridas (Vault Tasks)')).toBeVisible();
    });
});
