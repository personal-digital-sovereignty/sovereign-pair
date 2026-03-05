import { test, expect } from '@playwright/test';

test.describe('Pomodoro Widget E2E', () => {
    test.beforeEach(async ({ page }) => {
        // Bypass authentication for E2E tests
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('sovereign_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJKZWZlcnNvbiIsImV4cCI6MTc3MzE5NjY3NH0.MYwyQBf1IcSxxmT_mxTzJKgynZ-ovfYfqABafcsVeeI');
        });

        // Mock Backend (Zero Tech-Debt E2E Iso)
        await page.route('**/v1/**', route => {
            const url = route.request().url();
            if (url.includes('/auth/status')) return route.fulfill({ status: 200, json: { is_setup: true } });
            if (url.includes('/settings')) return route.fulfill({ status: 200, json: { sensus_mode: 'standard' } });
            if (url.includes('/agenda')) {
                return route.fulfill({
                    status: 200,
                    json: {
                        'today': { docs: [], tasks: [] }
                    }
                });
            }
            return route.fulfill({ status: 200, json: {} });
        });

        // Navigate to the dashboard where Pomodoro is injected
        await page.goto('/dashboard');
        await page.waitForTimeout(1000);
        // Switch to an agenda tab to see Pomodoro
        await page.getByRole('button', { name: 'Hoje' }).click();
    });

    test('should display Pomodoro timer modes', async ({ page }) => {
        await expect(page.locator('text=Pomodoro')).toBeVisible();
        await expect(page.locator('text=Pausa Curta')).toBeVisible();
        await expect(page.locator('text=Pausa Longa')).toBeVisible();
    });

    test('should default to 25 minutes for Focus mode', async ({ page }) => {
        await expect(page.locator('text=25:00')).toBeVisible();
    });

    test('should change time when switching modes', async ({ page }) => {
        await page.click('text=Pausa Curta');
        await expect(page.locator('text=05:00')).toBeVisible();

        await page.click('text=Pausa Longa');
        await expect(page.locator('text=15:00')).toBeVisible();
    });
});
