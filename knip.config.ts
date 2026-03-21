import type { KnipConfig } from 'knip';
import { parse } from 'vue/compiler-sfc';

const config: KnipConfig = {
    // Custom Vue SFC compiler using the real vue/compiler-sfc parser.
    // Fixes a Knip limitation: <script setup> components have an implicit
    // default export that Knip's built-in regex compiler doesn't see.
    // Without the synthetic `export default {}`, --trace and --trace-file
    // return empty results for Composition API components.
    compilers: {
        vue: (text: string) => {
            const { descriptor } = parse(text, { sourceMap: false });
            const scripts = descriptor.scriptSetup?.content ?? '';
            const script = descriptor.script?.content ?? '';
            const styles = descriptor.styles?.map(s => s.content).join('\n') ?? '';

            // <script setup> creates an implicit default export that the
            // raw content alone doesn't express. Add it so Knip can trace it.
            const syntheticExport = descriptor.scriptSetup ? '\nexport default {};' : '';

            return [scripts, script, syntheticExport, styles].join('\n');
        },
    },

    // Entry points — where Knip starts tracing the dependency tree
    entry: [
        // Main app entry
        'resources/js/app.ts',
        // SSR entry
        'resources/js/ssr.ts',
        // Inertia pages — only actual page files, not shared sub-components
        'resources/js/pages/**/*.vue',
        '!resources/js/pages/**/_components/**',
        '!resources/js/pages/**/Components/**',
    ],

    // Files that are part of the project (what Knip should analyze)
    project: [
        'resources/js/**/*.{vue,ts,js,tsx}',
    ],

    // Directories to completely ignore
    ignore: [
        // shadcn UI components (vendored library, not all are used by design)
        'resources/js/components/ui/**',
    ],

    // Disable Vite plugin auto-detection of entry points — it picks up
    // import.meta.glob('./pages/**/*.vue') from app.ts and adds ALL files
    // (including _components/) as entry points, bypassing our negation.
    vite: false,

    // Unresolved imports that are valid (tsconfig types field references)
    ignoreUnresolved: [
        './resources/js/types',
    ],

    // Ignore specific dependencies that are used implicitly
    ignoreDependencies: [
        // Tailwind v4 Vite plugin (loaded via vite config)
        '@tailwindcss/vite',
        // Vite plugins
        '@vitejs/plugin-vue',
        // CSS imports (used in resources/css/app.css, not JS)
        'tailwindcss',
        'tw-animate-css',
        // Used in composer.json scripts, not package.json scripts
        'concurrently',
        // Peer dependency of @vue/eslint-config-typescript
        '@eslint/js',
        'typescript-eslint',
    ],
};

export default config;
