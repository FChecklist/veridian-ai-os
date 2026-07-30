#!/usr/bin/env node
// ai-os/planning/scripts/create-or-reset-demo-login.mjs
//
// Reusable, idempotent tool for PLAN-15/PLAN-16: gives a compliance-tracker
// / PROJEXA user a REAL working password login. Not a one-off manual DB
// edit -- same script works for any user, any org, run as many times as
// needed.
//
// WHY THIS MECHANISM (verified against the live app, not assumed):
//   - compliance.users.password_hash is a LEGACY NOT NULL column. It is
//     NEVER read for login. See src/lib/supabase/auth-guard.ts:165 --
//     regular signups set it to the literal string "supabase-auth-managed"
//     and never touch it again. Writing a bcrypt/argon2 hash into that
//     column would do NOTHING -- real authentication is 100% delegated to
//     Supabase Auth (auth.users in the "verdian-ai" project,
//     pcrjmlpuqsbocqfwoxod).
//   - The ONLY correct way to set/reset a working password is the Supabase
//     Auth Admin API (service-role key), exactly as prior art
//     scripts/wave111-create-hero-logins.ts already does for hero-persona
//     logins: admin.auth.admin.createUser({ email, password, email_confirm }).
//   - compliance.users is matched to auth.users BY EMAIL, not by a
//     pre-wired id: src/lib/supabase/auth-guard.ts:270
//       dbUser = db.query.users.findFirst({ where: eq(users.email, email) })
//     and if dbUser.authUserId doesn't match the live Supabase auth id yet,
//     the app self-heals it on the very next authenticated request
//     (auth-guard.ts:275-277). This script ALSO writes it immediately via
//     direct SQL so the fix is confirmed without waiting on a live login.
//
// USAGE (run from inside a checkout that has .env.local with
// NEXT_PUBLIC_SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY for project
// pcrjmlpuqsbocqfwoxod -- e.g. /opt/veridian/repos/compliance-tracker):
//
//   node --env-file=.env.local /opt/veridian/ai-os/planning/scripts/create-or-reset-demo-login.mjs \
//     --email democeo@projexa-ai.com --password 'DemoVeridian2026!'
//
// Output: prints the auth_user_id, and prints (does NOT execute) the exact
// verification/link SQL to run via the Supabase MCP execute_sql tool
// against project pcrjmlpuqsbocqfwoxod. Run that SQL as a separate,
// explicit step -- this script deliberately does not touch Postgres
// directly (no DATABASE_URL dependency), matching wave111's own pattern.

import { createClient } from "@supabase/supabase-js";

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
const email = args.email;
const password = args.password;

if (!email || !password) {
  console.error("Usage: node create-or-reset-demo-login.mjs --email <email> --password <password>");
  process.exit(1);
}

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
  console.error("Missing NEXT_PUBLIC_SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY in the environment.");
  console.error("Run with: node --env-file=.env.local create-or-reset-demo-login.mjs ...");
  console.error("from a checkout that has .env.local (e.g. /opt/veridian/repos/compliance-tracker).");
  process.exit(1);
}

const admin = createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function findExistingAuthUserByEmail(targetEmail) {
  // supabase-js admin has no getUserByEmail; page through listUsers.
  let page = 1;
  const perPage = 200;
  for (;;) {
    const { data, error } = await admin.auth.admin.listUsers({ page, perPage });
    if (error) throw error;
    const hit = data.users.find((u) => u.email?.toLowerCase() === targetEmail.toLowerCase());
    if (hit) return hit;
    if (data.users.length < perPage) return null;
    page++;
  }
}

async function main() {
  console.log(`[demo-login] target email: ${email}`);

  const { data: created, error: createErr } = await admin.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  });

  let authUserId;
  if (!createErr) {
    authUserId = created.user.id;
    console.log(`[demo-login] created NEW auth.users row: ${authUserId}`);
  } else if (/already.*registered|already exists/i.test(createErr.message || "")) {
    console.log(`[demo-login] auth user already exists, looking it up to reset password instead...`);
    const existing = await findExistingAuthUserByEmail(email);
    if (!existing) {
      console.error(`[demo-login] FAILED: createUser said "already registered" but listUsers found no match for ${email}.`);
      process.exit(1);
    }
    const { data: updated, error: updateErr } = await admin.auth.admin.updateUserById(existing.id, {
      password,
      email_confirm: true,
    });
    if (updateErr) {
      console.error(`[demo-login] FAILED to reset password for ${email}: ${updateErr.message}`);
      process.exit(1);
    }
    authUserId = updated.user.id;
    console.log(`[demo-login] reset password on EXISTING auth.users row: ${authUserId}`);
  } else {
    console.error(`[demo-login] FAILED to create auth user for ${email}: ${createErr.message}`);
    process.exit(1);
  }

  console.log("\n[demo-login] SUCCESS. Login is live immediately at the app's /login page with:");
  console.log(`  email:    ${email}`);
  console.log(`  password: ${password}`);
  console.log("\n[demo-login] Belt-and-suspenders step (optional -- the app self-heals this on first");
  console.log("login per auth-guard.ts:275-277, but run this now via the Supabase MCP execute_sql tool");
  console.log(`against project pcrjmlpuqsbocqfwoxod to confirm the link immediately, with no login required:`);
  console.log(`\n  UPDATE compliance.users SET auth_user_id = '${authUserId}' WHERE email = '${email}';`);
  console.log(`\n  -- verify:`);
  console.log(`  SELECT id, email, auth_user_id, is_active FROM compliance.users WHERE email = '${email}';`);
}

main().catch((e) => {
  console.error("[demo-login] UNEXPECTED ERROR:", e);
  process.exit(1);
});
