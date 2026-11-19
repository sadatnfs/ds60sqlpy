// Rebuild the vendored editor bundle and its checksum manifest:
//   npm ci && npm run build
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const here = dirname(fileURLToPath(import.meta.url));
const vendor =
  process.env.DS60_VENDOR_DIR || join(here, "..", "..", "src", "ds60sqlpy", "assets", "vendor");
const bundle = "codemirror.v6.min.js";
await build({
  entryPoints: [join(here, "entry.mjs")],
  outfile: join(vendor, bundle),
  bundle: true,
  minify: true,
  format: "iife",
  globalName: "DS60Editor",
  target: ["es2020"],
  legalComments: "none",
  charset: "utf8",
});
const lock = JSON.parse(readFileSync(join(here, "package-lock.json"), "utf8"));
const packages = Object.fromEntries(
  Object.entries(lock.packages)
    .filter(([path]) =>
      /^node_modules\/(@codemirror|@lezer|crelt|style-mod|w3c-keyname)/.test(path),
    )
    .map(([path, item]) => [path.replace(/^node_modules\//, ""), item.version])
    .sort(([a], [b]) => a.localeCompare(b)),
);
const sha256 = (name) =>
  createHash("sha256")
    .update(readFileSync(join(vendor, name)))
    .digest("hex");
const manifest = {
  package: "codemirror",
  version: "6",
  license: "MIT",
  recipe: "scripts/codemirror-bundle",
  packages,
  files: {
    [bundle]: sha256(bundle),
    "LICENSE.codemirror.txt": sha256("LICENSE.codemirror.txt"),
  },
};
writeFileSync(join(vendor, "codemirror-manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log(`Wrote ${bundle} (${readFileSync(join(vendor, bundle)).length} bytes)`);
