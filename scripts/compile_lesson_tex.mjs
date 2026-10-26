#!/usr/bin/env node
// Compile a bounded set of explicit formulas. No shell escape, network or file macros.
import fs from "node:fs";
import { createRequire } from "node:module";
import crypto from "node:crypto";
const require = createRequire(import.meta.url);
const katex = require("../src/ds60sqlpy/assets/vendor/textbook/katex.js");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
if (!Array.isArray(input) || input.length > 50000) throw new Error("Invalid TeX input set");
const expressions = {};
for (const item of input) {
  if (
    typeof item.source !== "string" ||
    item.source.length > 8192 ||
    typeof item.display !== "boolean"
  )
    throw new Error("Invalid TeX source");
  const key = crypto
    .createHash("sha256")
    .update((item.display ? "display" : "inline") + "\n" + item.source)
    .digest("hex");
  const html = katex.renderToString(item.source, {
    displayMode: item.display,
    output: "htmlAndMathml",
    throwOnError: true,
    trust: false,
    strict: "error",
    maxExpand: 1000,
    maxSize: 20,
    globalGroup: false,
    macros: {},
  });
  expressions[key] = { source: item.source, display: item.display, html };
}
process.stdout.write(
  JSON.stringify({ schema_version: 1, compiler: "KaTeX 0.19.1", expressions }) + "\n",
);
