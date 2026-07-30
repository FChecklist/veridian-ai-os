#!/usr/bin/env node
// ai-os/planning/scripts/enable-product-branch.mjs
//
// Reusable tool: given an org id + a product_branch_id (or branch_key),
// prints the exact idempotent SQL to enable that branch for that org via
// compliance.org_product_branch_enablements. Companion to
// create-or-reset-demo-login.mjs -- getting a demo user LOGGED IN and
// getting the ORG the right MODULES enabled are two separate, independent
// gates in this codebase (confirmed by reading
// src/lib/services/product-branch-service.ts + module-registry-service.ts
// and cross-checking live data), so both scripts are needed for a full
// working demo.
//
// This script does not hold a direct Postgres connection (same posture as
// scripts/wave111-create-hero-logins.ts and create-or-reset-demo-login.mjs
// -- DATABASE_URL is a Vercel-Sensitive var not available on this dev
// box). It looks up the branch's real id via the Supabase MCP
// execute_sql tool is NOT done here (no MCP access from a plain node
// script) -- pass the already-resolved product_branch_id as an argument,
// or pass --branch-key and consult platform.product_branches yourself
// first (one query, shown in the printed instructions below).
//
// USAGE:
//   node enable-product-branch.mjs --org-id <compliance.organisations.id> --branch-id <platform.product_branches.id> [--branch-key <label for the printed comment>]
//
// Output: prints the exact idempotent SQL (safe to re-run) to execute via
// the Supabase MCP execute_sql tool against project pcrjmlpuqsbocqfwoxod.

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      const key = argv[i].slice(2);
      out[key] = argv[i + 1];
      i++;
    }
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
const orgId = args["org-id"];
const branchId = args["branch-id"];
const branchKey = args["branch-key"] || "(unspecified)";

if (!orgId || !branchId) {
  console.error("Usage: node enable-product-branch.mjs --org-id <org id> --branch-id <product_branch_id> [--branch-key <key>]");
  console.error("\nDon't have the branch-id yet? Look it up first (read-only):");
  console.error("  SELECT id, branch_key, display_name FROM platform.product_branches WHERE branch_key = '<key>';");
  process.exit(1);
}

console.log(`[enable-branch] org_id=${orgId} branch_id=${branchId} (${branchKey})`);
console.log("\nRun this via the Supabase MCP execute_sql tool, project pcrjmlpuqsbocqfwoxod:\n");
console.log(`INSERT INTO compliance.org_product_branch_enablements (org_id, product_branch_id, is_enabled, enabled_at)`);
console.log(`VALUES ('${orgId}', '${branchId}', true, now())`);
console.log(`ON CONFLICT (org_id, product_branch_id)`);
console.log(`DO UPDATE SET is_enabled = true, enabled_at = now(), disabled_at = null;`);
console.log(`\n-- verify:`);
console.log(`SELECT org_id, product_branch_id, is_enabled FROM compliance.org_product_branch_enablements WHERE org_id = '${orgId}' AND product_branch_id = '${branchId}';`);
