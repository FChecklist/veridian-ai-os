#!/usr/bin/env node
// feature-completion-audit.mjs
//
// Automated, deterministic, re-runnable re-baseline of the tracked
// comparison-CSV feature lists (PLAN-08) against the CURRENT repo state.
// No manual row-by-row checking -- this script IS the checker.
//
// Usage:
//   node feature-completion-audit.mjs <repoRoot> <csvPath> [<csvPath2> ...]
//
// What it does (fully mechanical, no free-text judgment):
//   1. Parses each comparison CSV (skips the leading Owner-instruction
//      rows, finds the real header row by locating "Feature_ID").
//   2. Builds a token corpus of the CURRENT codebase from three sources:
//        a. every route.ts / page.tsx path under src/app/**
//        b. every drizzle table + column identifier in src/lib/db/schema.ts
//        c. every top-level directory name under src/lib and src/components
//   3. For each feature row, tokenizes Feature_Name + Submodule +
//      Feature_Category (lowercase, split on non-alnum, drop stopwords
//      and tokens < 4 chars), and computes what fraction of those
//      significant tokens appear in the corpus token set.
//   4. Assigns a deterministic verdict from the match ratio:
//        >= 0.66  -> IMPLEMENTED
//        0.34-0.65 -> PARTIAL
//        <  0.34  -> GAP
//      (thresholds are constants below -- change them, not the logic,
//      if the Owner wants a stricter/looser bar)
//   5. Writes a JSON results file (one row per feature, full token trail)
//      next to each input CSV, plus a console summary of counts by
//      verdict and by module.
//
// This mirrors the same style of mechanical, keyword/evidence-based
// verdict already used by ai-os/scripts/audit198/evidence-engine.mjs --
// same philosophy: software produces the count, not a human skimming
// 693 rows.

import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

const STOPWORDS = new Set([
  "the", "and", "for", "with", "from", "into", "this", "that", "have",
  "has", "are", "was", "were", "will", "shall", "can", "all", "any",
  "per", "via", "each", "based", "using", "used", "management", "system",
  "data", "report", "reports", "view", "views", "generic", "standard",
  "basic", "advanced", "module", "feature", "features", "support",
  "level", "type", "types", "status", "detail", "details", "process",
  "processing", "capability", "capabilities", "workflow", "workflows",
]);

const IMPLEMENTED_THRESHOLD = 0.66;
const PARTIAL_THRESHOLD = 0.34;

function tokenize(str) {
  if (!str) return [];
  return String(str)
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 4 && !STOPWORDS.has(t) && !/^\d+$/.test(t));
}

function walk(dir, out, maxDepth, depth = 0) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const e of entries) {
    if (e.name === "node_modules" || e.name === ".git" || e.name === ".next") continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      out.push(e.name);
      if (depth < maxDepth) walk(full, out, maxDepth, depth + 1);
    } else if (e.isFile()) {
      out.push(e.name.replace(/\.(tsx?|jsx?|mjs)$/, ""));
    }
  }
}

function buildCorpus(repoRoot) {
  const names = [];

  // a. every route.ts / page.tsx directory path under src/app
  walk(path.join(repoRoot, "src", "app"), names, 12);

  // b. drizzle table + column identifiers in src/lib/db/schema.ts
  const schemaPath = path.join(repoRoot, "src", "lib", "db", "schema.ts");
  try {
    const schema = readFileSync(schemaPath, "utf8");
    // export const fooBar = pgTable("foo_bar", { colOne: ..., col_two: ... })
    const tableMatches = [...schema.matchAll(/export const (\w+)\s*=\s*pgTable\(\s*["'`]([\w]+)["'`]/g)];
    for (const m of tableMatches) {
      names.push(m[1], m[2]);
    }
    const colMatches = [...schema.matchAll(/^\s*(\w+):\s*\w+\(["'`]?([\w]*)["'`]?\)/gm)];
    for (const m of colMatches) {
      names.push(m[1]);
      if (m[2]) names.push(m[2]);
    }
  } catch (e) {
    console.error("[feature-audit] WARNING: could not read schema.ts:", e.message);
  }

  // c. top-level dirs under src/lib and src/components (service/component names)
  for (const sub of ["lib", "components", "services"]) {
    walk(path.join(repoRoot, "src", sub), names, 6);
  }

  const tokenSet = new Set();
  for (const n of names) {
    for (const t of tokenize(n)) tokenSet.add(t);
  }
  return tokenSet;
}

function verdictFor(ratio) {
  if (ratio >= IMPLEMENTED_THRESHOLD) return "IMPLEMENTED";
  if (ratio >= PARTIAL_THRESHOLD) return "PARTIAL";
  return "GAP";
}

// minimal CSV parser that handles quoted multi-line fields (RFC4180-ish)
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else field += c;
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ",") { row.push(field); field = ""; }
      else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
      else if (c === "\r") { /* skip */ }
      else field += c;
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows;
}

function auditCsv(csvPath, corpus) {
  const text = readFileSync(csvPath, "utf8");
  const allRows = parseCsv(text);
  const headerIdx = allRows.findIndex((r) => r[0] && r[0].trim() === "Feature_ID");
  if (headerIdx === -1) {
    console.error(`[feature-audit] ${csvPath}: no Feature_ID header row found, skipping`);
    return null;
  }
  const headers = allRows[headerIdx];
  const col = (name) => headers.indexOf(name);
  const idIdx = col("Feature_ID");
  const modIdx = col("Module");
  const subIdx = col("Submodule");
  const catIdx = col("Feature_Category");
  const nameIdx = col("Feature_Name");

  // Some of these CSVs repeat the header row once per module section (a
  // human-authoring artifact, not real data) -- exclude any row whose
  // Feature_ID column literally re-reads "Feature_ID".
  const dataRows = allRows
    .slice(headerIdx + 1)
    .filter((r) => r.length > 1 && r[idIdx] && r[idIdx].trim() !== "Feature_ID");
  const results = [];
  for (const r of dataRows) {
    const sigTokens = new Set([
      ...tokenize(r[nameIdx]),
      ...tokenize(r[subIdx]),
      ...tokenize(r[catIdx]),
    ]);
    const total = sigTokens.size;
    let matched = 0;
    const matchedTokens = [];
    for (const t of sigTokens) {
      if (corpus.has(t)) { matched++; matchedTokens.push(t); }
    }
    const ratio = total > 0 ? matched / total : 0;
    results.push({
      feature_id: r[idIdx],
      module: r[modIdx],
      submodule: r[subIdx],
      feature_name: r[nameIdx],
      match_ratio: Number(ratio.toFixed(2)),
      matched_tokens: matchedTokens,
      verdict: total > 0 ? verdictFor(ratio) : "REVIEW_NO_TOKENS",
    });
  }
  return results;
}

function summarize(results) {
  const counts = {};
  const byModule = {};
  for (const r of results) {
    counts[r.verdict] = (counts[r.verdict] || 0) + 1;
    byModule[r.module] = byModule[r.module] || {};
    byModule[r.module][r.verdict] = (byModule[r.module][r.verdict] || 0) + 1;
  }
  return { total: results.length, counts, byModule };
}

const [, , repoRoot, ...csvPaths] = process.argv;
if (!repoRoot || csvPaths.length === 0) {
  console.error("Usage: node feature-completion-audit.mjs <repoRoot> <csvPath> [<csvPath2> ...]");
  process.exit(1);
}

console.log("[feature-audit] building corpus from", repoRoot);
const corpus = buildCorpus(repoRoot);
console.log("[feature-audit] corpus token count:", corpus.size);

for (const csvPath of csvPaths) {
  console.log("\n=== ", csvPath, " ===");
  const results = auditCsv(csvPath, corpus);
  if (!results) continue;
  const summary = summarize(results);
  console.log(JSON.stringify(summary, null, 2));
  const outPath = csvPath.replace(/\.csv$/, "") + ".feature-audit-results.json";
  writeFileSync(outPath, JSON.stringify({ generated: new Date().toISOString(), summary, results }, null, 2));
  console.log("[feature-audit] wrote", outPath);
}
