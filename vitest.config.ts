import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { svelteTesting } from '@testing-library/svelte/vite';
import path from 'path';

export default defineConfig({
	plugins: [svelte(), svelteTesting()],
	test: {
		environment: 'jsdom',
		include: ['src/**/*.{test,spec}.{js,ts}'],
		setupFiles: ['./src/setupTest.ts'],
		globals: true
	},
    resolve: {
		alias: {
			$lib: path.resolve('./src/lib'),
            $app: path.resolve('./node_modules/@sveltejs/kit/src/runtime/app')
		}
	}
});
