import prettier from 'eslint-config-prettier';
import vue from 'eslint-plugin-vue';

import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript';

export default defineConfigWithVueTs(
    vue.configs['flat/essential'],
    vueTsConfigs.recommended,
    {
        ignores: ['vendor', 'node_modules', 'public', 'bootstrap/ssr', 'tailwind.config.js', 'resources/js/components/ui/*'],
    },
    {
        rules: {
            // Vue-specific rules
            'vue/multi-word-component-names': 'off',
            'vue/max-attributes-per-line': 'off', // Let Prettier handle this
            'vue/first-attribute-linebreak': 'off', // Let Prettier handle this
            'vue/html-closing-bracket-newline': 'off', // Let Prettier handle this
            'vue/html-indent': 'off', // Let Prettier handle this
            'vue/html-closing-bracket-spacing': 'off', // Let Prettier handle this
            'vue/singleline-html-element-content-newline': 'off', // Let Prettier handle this
            'vue/multiline-html-element-content-newline': 'off', // Let Prettier handle this
            
            // TypeScript rules
            '@typescript-eslint/no-explicit-any': 'off',
            '@typescript-eslint/no-unused-vars': ['error', { 'argsIgnorePattern': '^_' }],
            
            // General code quality rules
            'no-console': 'warn',
            'no-debugger': 'warn',
            'prefer-const': 'error',
            'no-var': 'error',
        },
    },
    prettier,
);
