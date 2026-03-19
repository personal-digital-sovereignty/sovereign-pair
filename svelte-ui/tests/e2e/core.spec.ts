import { test, expect } from '@playwright/test';

test.describe('Cybrid Svelte UI E2E Assurance', () => {

    test('Loads the Shell OS layout successfully', async ({ page }) => {
        await page.goto('/');
        
        // Assert the OS Route text appears
        await expect(page.locator('text=O.S Route:')).toBeVisible();

        // Target the newly accessible Sidebar button
        const toggleButton = page.getByRole('button', { name: 'Toggle Navigation' });
        await expect(toggleButton).toBeVisible();
    });

    test('Navigates flawlessly to the Vault Interface', async ({ page }) => {
        await page.goto('/');

        // Click on the Vault (Folder Icon matching href="/vault")
        await page.locator('a[href="/vault"]').click();

        // The Vault must have the `Knowledge Vault` title
        await expect(page.locator('text=Knowledge Vault')).toBeVisible();

        // TipTap Markdown Placeholder should exist
        await expect(page.locator('.ProseMirror')).toBeVisible();
    });

    test('Settings UI mounts with specific components', async ({ page }) => {
        await page.goto('/settings');
        
        // The Identity header
        await expect(page.locator('text=Sovereign Identity')).toBeVisible();
    });

});
