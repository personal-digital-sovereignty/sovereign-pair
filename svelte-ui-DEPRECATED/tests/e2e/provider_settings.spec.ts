import { test, expect } from '@playwright/test';

test.describe('Provider Settings E2E — Alibaba Qwen & NVIDIA NIM', () => {

    test.beforeEach(async ({ page }) => {
        // Inject auth token to bypass login wall
        await page.addInitScript(() => {
            window.localStorage.setItem('sovereign_token', 'e2e-mock-token-123456');
        });
    });

    test('Should display and interact with Alibaba Qwen settings', async ({ page }) => {
        await page.goto('/dashboard');
        
        // Open Settings Modal
        await page.getByLabel('Open Settings').click();
        
        // Click on Alibaba Qwen tab
        await page.getByRole('button', { name: 'Alibaba Qwen' }).click();
        
        // Assert header is visible
        await expect(page.getByText('Alibaba Qwen (DashScope)')).toBeVisible();
        
        // Assert input fields with correct IDs/labels are present
        const apiKeyInput = page.locator('#qwenApiKeyInput');
        await expect(apiKeyInput).toBeVisible();
        
        const modelInput = page.locator('#qwenModelInput');
        await expect(modelInput).toBeVisible();
        await expect(modelInput).toHaveValue('qwen-plus');

        // Test the "KMS Protected" indicator
        await expect(page.getByText('KMS Protected').first()).toBeVisible();
    });

    test('Should display and interact with NVIDIA NIM settings', async ({ page }) => {
        await page.goto('/dashboard');
        
        // Open Settings Modal
        await page.getByLabel('Open Settings').click();
        
        // Click on NVIDIA NIM tab
        await page.getByRole('button', { name: 'NVIDIA NIM' }).click();
        
        // Assert header is visible
        await expect(page.getByText('NVIDIA NIM (Accelerated Inference)')).toBeVisible();
        
        // Assert input fields with correct IDs/labels are present
        const apiKeyInput = page.locator('#nvidiaApiKeyInput');
        await expect(apiKeyInput).toBeVisible();
        
        const modelInput = page.locator('#nvidiaModelInput');
        await expect(modelInput).toBeVisible();
        await expect(modelInput).toHaveValue('meta/llama-3.1-405b-instruct');
    });

    test('Switching providers should preserve UI state', async ({ page }) => {
        await page.goto('/dashboard');
        
        // Open Settings Modal
        await page.getByLabel('Open Settings').click();
        
        // Go to Qwen
        await page.getByRole('button', { name: 'Alibaba Qwen' }).click();
        await page.locator('#qwenModelInput').fill('qwen-max-test');
        
        // Switch to NVIDIA
        await page.getByRole('button', { name: 'NVIDIA NIM' }).click();
        await expect(page.locator('#nvidiaModelInput')).toBeVisible();
        
        // Switch back to Qwen
        await page.getByRole('button', { name: 'Alibaba Qwen' }).click();
        await expect(page.locator('#qwenModelInput')).toHaveValue('qwen-max-test');
    });
});
