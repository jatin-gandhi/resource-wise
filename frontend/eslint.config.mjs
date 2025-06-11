import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { fixupConfigRules, fixupPluginRules } from '@eslint/compat';
import { FlatCompat } from '@eslint/eslintrc';
import js from '@eslint/js';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import _import from 'eslint-plugin-import';
import simpleImportSort from 'eslint-plugin-simple-import-sort';
import prettier from 'eslint-plugin-prettier';
import jest from 'eslint-plugin-jest';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
});

export default [
  {
    ignores: ['build/', '**/node_modules/**', 'cdk.out/', 'coverage/']
  },

  ...fixupConfigRules(
    compat.extends('eslint:recommended', 'plugin:@typescript-eslint/recommended')
  ),

  {
    plugins: {
      '@typescript-eslint': fixupPluginRules(typescriptEslint),
      'simple-import-sort': fixupPluginRules(simpleImportSort),
      import: fixupPluginRules(_import),
      prettier: fixupPluginRules(prettier)
    },

    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        project: 'tsconfig.json'
      }
    },

    rules: {
      '@typescript-eslint/no-inferrable-types': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          args: 'none'
        }
      ],
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error',
      'import/first': 'error',
      'import/newline-after-import': 'error',
      'import/no-duplicates': 'error',
      'prettier/prettier': 'error',
      'no-unused-vars': 'off'
    },

    files: ['**/*.tsx', '**/*.ts']
  },
  {
    files: ['**/*.test.ts', '**/*.test.tsx'],
    plugins: { jest: fixupPluginRules(jest) },
    rules: {
      'jest/prefer-expect-assertions': 'off',
      'jest/expect-expect': 'off',
      'jest/no-hooks': ['error', { allow: ['afterAll', 'beforeEach', 'beforeAll'] }]
    }
  }
];
