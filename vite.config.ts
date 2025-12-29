import vue from '@vitejs/plugin-vue';
import laravel from 'laravel-vite-plugin';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        host: '0.0.0.0',
        origin: process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173',
        cors: true,
        hmr: {
            host: process.env.VITE_HMR_HOST || 'localhost',
            protocol: (process.env.VITE_HMR_PROTOCOL as 'ws' | 'wss') || 'ws',
            clientPort: process.env.VITE_HMR_CLIENT_PORT
                ? parseInt(process.env.VITE_HMR_CLIENT_PORT)
                : undefined,
        },
    },
    plugins: [
        laravel({
            input: ['resources/js/app.ts'],
            ssr: 'resources/js/ssr.ts',
            refresh: true,
        }),
        tailwindcss(),
        vue({
            template: {
                transformAssetUrls: {
                    base: null,
                    includeAbsolute: false,
                },
            },
        }),
    ],
});
