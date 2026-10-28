import { createRequire } from "node:module";

// Resolve prepared dependencies from the image, never from learner projects.
const require = createRequire("/opt/formatters/package.json");
const js = require("@eslint/js");
const ts = require("typescript-eslint");
const globals = require("globals");

// Browser pads run through AsyncFunction in browser-sandbox.html. Parse them
// in the same async-function context without executing any learner program.
const browserPad = {
  processors: {
    async: {
      preprocess(source) {
        return [`(async function () {\n${source}\n})();`];
      },
      postprocess(results) {
        return results.flat().map((message) => ({
          ...message,
          line: Math.max(1, message.line - 1),
          ...(message.endLine ? { endLine: Math.max(1, message.endLine - 1) } : {}),
        }));
      },
      supportsAutofix: false,
    },
  },
};

export default [
  {
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: { ecmaVersion: "latest" },
    rules: {
      ...js.configs.recommended.rules,
      "no-empty": ["error", { allowEmptyCatch: true }],
      // Browser globals such as window.status may have legitimate local names.
      // Duplicate declarations within the program are still rejected.
      "no-redeclare": ["error", { builtinGlobals: false }],
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
    files: ["**/*.{ts,tsx,mts,cts}"],
  })),
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx,mts,cts}"],
    languageOptions: {
      globals: { ...globals.es2024 },
    },
  },
  {
    files: [
      "**/*.{mjs,cjs}",
      "scripts/**/*.{js,ts,tsx,mts,cts}",
      "docker/**/*.{js,ts,tsx,mts,cts}",
      "courses/javascript-typescript/**/*.{ts,tsx,mts,cts}",
    ],
    languageOptions: { globals: { ...globals.node } },
  },
  {
    files: [
      "src/ds60sqlpy/assets/**/*.js",
      "courses/javascript-typescript/**/*.js",
      "courses/data-ml-engineering/projects/inference-service/app.js",
    ],
    languageOptions: {
      sourceType: "script",
      globals: { ...globals.browser },
    },
  },
  {
    files: ["courses/javascript-typescript/{lessons,solutions}/js-0{4,5,6}*.js"],
    languageOptions: { globals: { d3: "readonly" } },
    plugins: { classroom: browserPad },
    processor: "classroom/async",
  },
  {
    files: ["courses/data-visualization/{authoring,lessons,references}/*.js"],
    languageOptions: {
      sourceType: "script",
      globals: { ...globals.browser },
    },
  },
  {
    files: ["courses/data-visualization/{lessons,references}/viz-*.js"],
    plugins: { classroom: browserPad },
    processor: "classroom/async",
  },
  {
    files: ["src/ds60sqlpy/assets/classroom.js"],
    // The classroom server supplies this value in the page before the asset.
    languageOptions: { globals: { SERVER_TOKEN: "readonly" } },
  },
  {
    files: ["courses/javascript-typescript/solutions/js-002_solution.mjs"],
    // These assertions deliberately teach NaN and negative-zero equality.
    rules: { "use-isnan": "off", "no-compare-neg-zero": "off" },
  },
  {
    files: ["courses/javascript-typescript/solutions/js-003_solution.mjs"],
    // Literal operands demonstrate the different behavior of || and ??.
    rules: { "no-constant-binary-expression": "off" },
  },
  {
    files: ["**/*.cjs"],
    languageOptions: { sourceType: "commonjs" },
  },
];
