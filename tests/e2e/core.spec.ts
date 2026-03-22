import { test, expect } from '@playwright/test';

test.describe('Cybrid Svelte UI E2E Assurance', () => {

    test.beforeEach(async ({ page }) => {
        // Inject auth token to bypass the Pin Login wall globally for all E2E tests
        await page.addInitScript(() => {
            window.localStorage.setItem('sovereign_token', 'e2e-mock-token-123456');
        });
    });

    test('Loads the Shell OS layout successfully', async ({ page }) => {
        await page.goto('/');
        
        // Assert the main sidebar Navigation loads
        await expect(page.locator('aside')).toBeVisible();

        // Control Hub Header should be present
        await expect(page.locator('header')).toBeVisible();
    });

    test('Navigates flawlessly to the Vault Interface', async ({ page }) => {
        await page.goto('/vault');

        // The Vault must have the main `<main>` container
        await expect(page.locator('main')).toBeVisible();
    });

    test('Settings UI mounts with specific components', async ({ page }) => {
        await page.goto('/settings');
        
        // The Settings main wrapper
        await expect(page.locator('main')).toBeVisible();
    });

});
