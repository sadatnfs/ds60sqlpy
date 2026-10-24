import { createRequire } from "node:module";

// Resolve prepared dependencies from the image, never from learner projects.
const require = createRequire("/opt/formatters/package.json");
const js = require("@eslint/js");
const ts = require("typescript-eslint");
const globals = require("globals");

export default [
  {
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: { ecmaVersion: "latest" },
    rules: {
      ...js.configs.recommended.rules,
      "no-empty": ["error", { allowEmptyCatch: true }],
      "no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
  },
  ...ts.configs.recommended.map((config) => ({
    ...config,
    files: ["**/*.{ts,tsx}"],
  })),
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx}"],
    languageOptions: {
      globals: { ...globals.es2024 },
    },
  },
  {
    files: [
      "**/*.{mjs,cjs}",
      "scripts/**/*.{js,ts,tsx}",
      "docker/**/*.{js,ts,tsx}",
      "courses/javascript-typescript/**/*.{ts,tsx}",
    ],
    languageOptions: { globals: { ...globals.node } },
  },
  {
    files: ["src/ds60sqlpy/assets/**/*.js", "courses/javascript-typescript/**/*.js"],
    languageOptions: {
      sourceType: "script",
      globals: { ...globals.browser },
    },
  },
  {
    files: ["courses/javascript-typescript/lessons/js-0{4,5,6}*.js"],
    languageOptions: { globals: { d3: "readonly" } },
  },
  {
    files: ["**/*.cjs"],
    languageOptions: { sourceType: "commonjs" },
  },
];
