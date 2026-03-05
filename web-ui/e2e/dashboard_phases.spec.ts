import { test, expect } from '@playwright/test';

test.describe('Dashboard Phase 38 and 39 E2E', () => {
    test.beforeEach(async ({ page }) => {
        // Authenticate
        await page.goto('/');
        await page.evaluate(() => {
            // nosemgrep: generic.secrets.security.detected-jwt-token.detected-jwt-token
            localStorage.setItem('sovereign_token', 'mock_jwt_token');
        });

        // Mock Backend (Zero Tech-Debt E2E Iso)
        await page.route('**/v1/**', route => {
            const url = route.request().url();
            if (url.includes('/projects')) return route.fulfill({ status: 200, json: [] });
            if (url.includes('/quarantine')) return route.fulfill({ status: 200, json: [] });
            if (url.includes('/auth/status')) return route.fulfill({ status: 200, json: { is_setup: true } });
            if (url.includes('/settings')) return route.fulfill({ status: 200, json: { sensus_mode: 'standard' } });
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
            return route.fulfill({ status: 200, json: {} });
        });

        await page.goto('/dashboard');
        await page.waitForTimeout(1000);
    });

    test('should tab switch to God Mode Cockpit and render its specific UI', async ({ page }) => {
        // Click the God Mode icon/tab
        await page.getByRole('button', { name: 'Command Hub' }).click();

        // Assert the header changed
        await expect(page.locator('text=Radar de Ação Tática')).toBeVisible();

        // Assert the structural sections exist
        await expect(page.locator('text=Projetos em Voo')).toBeVisible();
    });

    test('should tab switch to The Sentinel (Quarentena) and render its blank state', async ({ page }) => {
        // Click the Sentinel tab
        await page.getByRole('button', { name: 'The Sentinel' }).click();

        // Assert the Sentinel UI exists
        await expect(page.locator('text=Logs de Quarentena')).toBeVisible();

        // Blank state should be visible initially
        await expect(page.locator('text=Bastião Seguro')).toBeVisible();
    });
});
