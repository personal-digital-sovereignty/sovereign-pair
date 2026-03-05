import { test, expect } from '@playwright/test';

test.describe('Usability and Physical Limits E2E', () => {

    test.beforeEach(async ({ page }) => {
        // Authenticate implicitly
        await page.goto('/');
        await page.evaluate(() => {
