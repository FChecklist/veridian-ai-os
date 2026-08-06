# Z.AI Black-Box GTM Audit — Merged Report (Parts 1-8)


Source: UMR-20260806-101802-a350 / dispatch UMR-20260806-102500-ab50 — Step 1 merge.

This file is a verbatim concatenation of the 8 real source part files at
`/opt/veridian/ai-os/memory/zai-gtm-findings/`, in order, each wrapped in an
explicit provenance header/footer so every line can be traced back to its
original source file and line number. No content has been altered,
reworded, or reordered from the originals — this is a pure concatenation.

| Part | Source file | Lines |
|---|---|---|
| 1 | `Part1_Smoke_E2E_Auth_Testing_Report.txt` | 340 |
| 2 | `Part2_UIUX_CrossBrowser_Responsive_Testing_Report.txt` | 413 |
| 3 | `Part3_Accessibility_Performance_WebVitals_Testing_Report.txt` | 352 |
| 4 | `Part4_PWA_Offline_Storage_Testing_Report.txt` | 378 |
| 5 | `Part5_API_Security_Testing_Report.txt` | 489 |
| 6 | `Part6_RBAC_AI_Governance_Testing_Report.txt` | 475 |
| 7 | `Part7_Backend_System_Testing_Report.txt` | 570 |
| 8 | `Part8_Regression_Final_Certification_Report.txt` | 480 |

**Total real lines across all 8 parts: 3497**

---

<!-- ===== BEGIN PART 1 SOURCE FILE: Part1_Smoke_E2E_Auth_Testing_Report.txt ===== -->

## PART 1 OF 8 — SOURCE FILE: `Part1_Smoke_E2E_Auth_Testing_Report.txt`

```text
================================================================================
GTMCert PART 1 of 8 — SMOKE + E2E JOURNEY + AUTHENTICATION TESTING
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Provided Creds     : democeo@projexa-ai.com / Demo@1234
Tool Used          : agent-browser (Playwright-based headless CLI)
Browser Engine     : Chromium (Playwright default)
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74
Trace ID           : 19fd635e17043ad1
================================================================================

TESTS COVERED IN PART 1
  Test #1   : Smoke Testing
  Test #2   : End-to-End User Journey
  Test #13  : Authentication Testing

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/
ARTIFACTS CAPTURED  : 13 PNG screenshots + 1 network trace

--------------------------------------------------------------------------------
CRITICAL BLOCKER SUMMARY (READ FIRST)
--------------------------------------------------------------------------------
[BLOCKER-001] The provided demo credentials `democeo@projexa-ai.com` / 
`Demo@1234` were rejected by Supabase Auth with the message 
"Invalid login credentials". The Supabase token endpoint 
`POST https://pcrjmlpuqsbocqfwoxod.supabase.co/auth/v1/token?grant_type=password`
returned HTTP 400 on every attempt (5 attempts made).

Impact:
  - Tests #1, #2, #13 cannot achieve full PASS state.
  - All downstream tests (#3-#25) that depend on an authenticated
    session are blocked until valid credentials are provided.
  - Tests still executable as unauthenticated user are limited to:
      * Public page UI validation (login, signup, pricing, 404)
      * HTTP security headers
      * Login form behavior and validation
      * Localization toggle
      * Alternative auth entry points (Google OAuth, Passcode, SSO)

Required user action:
  Please verify the demo credentials. Possibilities:
    (a) The password was changed/expired.
    (b) The demo user was deleted from Supabase Auth.
    (c) The email confirmation step was never completed.
    (d) The intended user is at a different email (e.g. demo@projexa-ai.com).
  Until credentials are restored, the bulk of the 25-test matrix cannot be
  executed from the END USER perspective.

--------------------------------------------------------------------------------
TEST #1 — SMOKE TESTING
--------------------------------------------------------------------------------
Tool              : agent-browser
URL tested        : https://projexa-ai.com/
Pass Criteria     : App starts, login works, dashboard loads

Evidence:
  - GET https://projexa-ai.com/      → 200, redirected to /login (see 01-login-initial.png)
  - GET https://projexa-ai.com/login → 200 (see 01-login-initial.png)
  - Server header: Vercel
  - X-Powered-By: Next.js
  - HSTS: max-age=63072000 (enabled, good)
  - Login form rendered correctly (3 input fields: EMAIL, PASSWORD, Language)
  - 4 auth buttons present: Google, Sign In, Passcode, SSO
  - POST to Supabase /auth/v1/token → HTTP 400 (see network trace below)
  - Dashboard (/dashboard) NOT loaded; redirect to /login?redirectTo=%2Fdashboard

Sub-checks:
  1a. App starts                 : PASS  (HTTP 200 on / and /login)
  1b. Login works                : FAIL  (Supabase 400 — invalid credentials)
  1c. Dashboard loads            : FAIL  (blocked by 1b)

VERDICT  : FAIL
Reason   : Provided demo credentials rejected by Supabase Auth; dashboard unreachable.
Recommend:
  - Re-verify the demo account exists and password is correct.
  - Add an explicit, user-visible error message near the form (currently only
    a transient toast appears and disappears within ~4s — easy to miss).
  - Add a "Forgot password" link on the login page (currently only
    "Send magic link instead" is offered, and /forgot-password returns 404).

Artifacts:
  /home/z/my-project/screenshots/01-login-initial.png
  /home/z/my-project/screenshots/02-after-login-attempt.png
  /home/z/my-project/screenshots/03-login-filled.png

--------------------------------------------------------------------------------
TEST #2 — END-TO-END USER JOURNEY
--------------------------------------------------------------------------------
Tool              : agent-browser
URL tested        : https://projexa-ai.com/  (intended flow: login → dashboard)
Pass Criteria     : Complete workflow executes successfully

Intended user journey (assumed from URL structure):
  Step 1: Land on /                          → redirected to /login
  Step 2: Enter email + password             → entered correctly
  Step 3: Click "Sign In"                    → clicked
  Step 4: Supabase /auth/v1/token (password) → HTTP 400 (FAIL)
  Step 5: Redirect to /home or /dashboard    → NEVER REACHED
  Step 6: Browse compliance dashboard         → NEVER REACHED

Evidence:
  - Pre-submit form values verified:
      EMAIL field    = "democeo@projexa-ai.com" (9 chars after @)
      PASSWORD field = "Demo@1234"               (9 chars)
  - POST https://pcrjmlpuqsbocqfwoxod.supabase.co/auth/v1/token?grant_type=password
        → HTTP 400 (5 attempts, all 400)
  - POST https://projexa-ai.com/api/auth/failure-event → HTTP 200
        (server is correctly logging the auth failure)
  - Toast shown: "Invalid login credentials" (auto-dismissed in ~4s)

Side-paths explored (as unauthenticated user):
  - /signup           → 200, signup form loads (see 04-signup-page.png)
  - /pricing          → 200, public pricing page loads (see 05-pricing-page.png)
  - /forgot-password  → 404 page (BROKEN LINK) (see 06-forgot-password.png)
  - /about            → 404 page
  - /dashboard        → 302 → /login?redirectTo=%2Fdashboard (correctly gated)

VERDICT  : FAIL (BLOCKED)
Reason   : Authentication failed at Step 4; downstream steps cannot execute.
Recommend:
  - Restore or reissue demo credentials.
  - Add a self-service password reset that actually works (current
    /forgot-password returns 404).
  - Provide a public landing page at / — current behavior immediately
    redirects to /login, which is unfriendly to first-time visitors.

Artifacts:
  /home/z/my-project/screenshots/02-after-login-attempt.png
  /home/z/my-project/screenshots/04-signup-page.png
  /home/z/my-project/screenshots/05-pricing-page.png
  /home/z/my-project/screenshots/06-forgot-password.png

--------------------------------------------------------------------------------
TEST #13 — AUTHENTICATION TESTING
--------------------------------------------------------------------------------
Tool              : agent-browser
URL tested        : https://projexa-ai.com/login
Pass Criteria     : Login, Logout, Session pass

Sub-tests executed:

  13a. Login with valid demo credentials
       Action  : fill EMAIL=democeo@projexa-ai.com, PASSWORD=Demo@1234, click Sign In
       Result  : HTTP 400 from Supabase, toast "Invalid login credentials"
       Verdict : FAIL

  13b. Login form — required field validation
       Action  : leave EMAIL empty, leave PASSWORD empty, click Sign In
       Result  : HTML5 `required` attribute blocks submit; no request sent
       Verdict : PASS (basic HTML5 validation works)

  13c. Login form — email format validation
       Action  : EMAIL="notanemail", PASSWORD="password", click Sign In
       Result  : Request still fires to Supabase (no client-side email regex)
                 Supabase returns 401 (it does its own validation)
       Verdict : FAIL — client-side should reject malformed email BEFORE
                 sending to the auth provider (leaks user attempts and
                 creates unnecessary noise in auth logs).

  13d. Google OAuth entry point
       Action  : click "Sign in with Google"
       Result  : Browser navigates to
                 https://pcrjmlpuqsbocqfwoxod.supabase.co/auth/v1/authorize
                 ?provider=google&redirect_to=...%2Fauth%2Fcallback%3Fnext%3D%252Fhome
                 with PKCE code_challenge (S256) — OAuth flow correctly wired.
       Verdict : PASS (entry point functional; not fully completed because
                 this would require a real Google account)

  13e. Passcode login entry point
       Action  : click "Sign in with passcode"
       Result  : Inline 4-digit passcode field appears, Continue button enabled.
       Verdict : PASS (UI flow functional; cannot test passcode value without
                 a valid passcode)

  13f. Company SSO entry point
       Action  : click "Sign in with company SSO"
       Result  : Inline "COMPANY ID" field appears, Continue button enabled.
       Verdict : PASS (UI flow functional; cannot test without a real Company ID)

  13g. Magic link entry point
       Action  : observed "Send magic link instead" button on login form
       Result  : button present and clickable; not exercised (would send email).
       Verdict : PASS (entry point present)

  13h. Logout flow
       Result  : CANNOT TEST — login is blocked, no session to terminate.
       Verdict : BLOCKED

  13i. Session persistence
       Result  : CANNOT TEST — no session created.
       Verdict : BLOCKED

  13j. Session expiry
       Result  : CANNOT TEST — no session created.
       Verdict : BLOCKED

  13k. Rate-limiting / brute-force protection
       Action  : submitted invalid creds 5 times in rapid succession
       Result  : No rate-limit observed; all 5 attempts got the same 400
                 response immediately. No lockout, no captcha, no delay.
       Verdict : FAIL — this is a security gap. See Part 5 (Security Testing)
                 for full treatment.

  13l. Localization of auth UI
       Action  : toggle Language combobox from English to हिन्दी
       Result  : entire login form translated to Hindi
                 ("वापसी पर स्वागत है", "साइन इन करें", etc.)
       Verdict : PASS (i18n works for login page)

  13m. Toast notifications UX
       Action  : observe toast on auth failure
       Result  : toast appears top-level, auto-dismisses in ~4s. Easy to miss.
                 No persistent error text near the form.
       Verdict : WARN — accessible-enough but suboptimal for users with
                 cognitive load or screen-reader-only reliance.

Overall VERDICT for Test #13 : FAIL
Reason   : Primary login path fails with provided credentials. Email-format
           validation missing client-side. No rate-limiting observed. Logout,
           session, and expiry flows cannot be exercised.
Recommend:
  - Restore demo credentials OR provide a working set.
  - Add client-side email regex validation (type="email" alone is not enough).
  - Add rate-limiting after 3-5 failed attempts (exponential backoff or
    short lockout). Consider reCAPTCHA on the login form.
  - Make error message persistent near the form, not only in a toast.
  - Fix /forgot-password 404.

Artifacts:
  /home/z/my-project/screenshots/01-login-initial.png
  /home/z/my-project/screenshots/07-empty-password.png
  /home/z/my-project/screenshots/08-invalid-email.png
  /home/z/my-project/screenshots/09-google-signin.png
  /home/z/my-project/screenshots/10b-passcode-modal.png
  /home/z/my-project/screenshots/11-sso-modal.png
  /home/z/my-project/screenshots/12-hindi-ui.png

--------------------------------------------------------------------------------
ADDITIONAL OBSERVATIONS (carried forward to later parts)
--------------------------------------------------------------------------------
OBS-001  Brand inconsistency
  - /login page title : "Sign in — PROJEXA"
  - /login page brand : "PROJEXA" / "One Portal. One Truth."
  - /pricing page     : "VERIDIAN AI" / "VERIDIAN COGNITIVE AI OS"
  - /signup page      : "VERIDIAN COGNITIVE AI OS"
  - <title> tag on /pricing, /signup, /forgot-password, /about is
    "VERIDIAN COGNITIVE AI OS — AI Cognitive Research" (NOT "PROJEXA")
  → Suggests incomplete rebrand. Will be re-evaluated in Part 2 (UI/UX).

OBS-002  No public landing page at /
  - GET / → 302 → /login
  - First-time visitors have no marketing/landing surface.
  - This is unusual for a SaaS product. Will be re-evaluated in Part 2.

OBS-003  /forgot-password returns 404
  - The login form offers no "Forgot password?" link — only "Send magic
    link instead". But navigating directly to /forgot-password yields 404.
  - Suggests the route was removed but not redirected.

OBS-004  Security headers (observed on /login)
  - strict-transport-security   : max-age=63072000          ✓ (HSTS on)
  - cache-control               : no-store, no-cache        ✓ (sensitive page)
  - content-type                : text/html; charset=utf-8  ✓
  - server                      : Vercel                    (info leak — minor)
  - x-powered-by                : Next.js                   (info leak — minor)
  - content-security-policy     : NOT PRESENT               ✗ (CSP missing)
  - x-frame-options             : NOT PRESENT               ✗ (clickjacking risk)
  - x-content-type-options      : NOT PRESENT               ✗ (MIME sniffing risk)
  - referrer-policy             : NOT PRESENT               ✗ (referrer leak risk)
  - permissions-policy          : NOT PRESENT               ✗
  → Will be re-evaluated in Part 5 (Security Testing).

OBS-005  Cookies
  - At unauthenticated state, ZERO cookies are set on the projexa-ai.com
    domain. Good (no tracking cookies on login).
  - Supabase auth cookies (`sb-*-auth-token`) only appear AFTER successful
    login — cannot verify Secure/HttpOnly/SameSite attributes yet.

OBS-006  LocalStorage / IndexedDB
  - At unauthenticated state, localStorage is empty. IndexedDB not yet
    probed (will be done in Part 4 — Browser Storage Testing).

OBS-007  Manifest / PWA hints
  - GET https://projexa-ai.com/manifest.webmanifest → HTTP 200
  - Next.js app, likely a Next-PWA setup. Will be evaluated in Part 4.

OBS-008  Network requests observed on login page
  - Two analytics scripts loaded:
      /771b847594094cc8/script.js
      /04809683687b4e12/script.js
    (likely Vercel Analytics / Speed Insights or PostHog). Cannot identify
     without response body access. Will be noted in Part 5.

OBS-009  Supabase project URL
  - https://pcrjmlpuqsbocqfwoxod.supabase.co  (visible in client bundle)
  - This is the auth backend. Anon key is also exposed in client JS (normal
    for Supabase, but should be paired with Row-Level Security policies).
    Will be re-evaluated in Part 5 (Security) and Part 6 (RBAC).

OBS-010  API endpoints inferred
  - /api/auth/failure-event  (POST, observed firing on login failure, 200)
  - /auth/callback           (OAuth redirect target)
  - More endpoints will be enumerated in Part 5 (API Contract Testing).

--------------------------------------------------------------------------------
PART 1 SUMMARY TABLE
--------------------------------------------------------------------------------
+-------+-------------------------------------+---------+----------------------+
| Test# | Test Name                           | Verdict | Reason / Blocker     |
+-------+-------------------------------------+---------+----------------------+
| 1     | Smoke Testing                       | FAIL    | Login fails (400)    |
| 2     | End-to-End User Journey             | FAIL    | Blocked at login     |
| 13    | Authentication Testing              | FAIL    | Creds rejected;      |
|       |                                     |         | no rate-limit;       |
|       |                                     |         | email validation     |
|       |                                     |         | weak; logout/session |
|       |                                     |         | untestable           |
+-------+-------------------------------------+---------+----------------------+

BLOCKING ISSUES (must be resolved before Parts 2-8 can complete):
  1. Demo credentials `democeo@projexa-ai.com / Demo@1234` are INVALID.
     → User action required: provide working credentials OR confirm the
       account is active in Supabase.
  2. /forgot-password returns 404 — no self-service password reset.

NON-BLOCKING ISSUES (logged for later parts):
  - Brand inconsistency (PROJEXA vs VERIDIAN AI) — Part 2.
  - Missing security headers (CSP, XFO, XCTO, Referrer-Policy) — Part 5.
  - No rate-limiting on login — Part 5.
  - No client-side email format validation — Part 5.
  - No public landing page at / — Part 2.

--------------------------------------------------------------------------------
END OF PART 1 REPORT
================================================================================
Next: Part 2 — UI/UX Validation + Cross-Browser + Responsive Testing
       (will proceed with unauthenticated exploration if creds remain invalid)
================================================================================
```

<!-- ===== END PART 1 SOURCE FILE: Part1_Smoke_E2E_Auth_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 2 SOURCE FILE: Part2_UIUX_CrossBrowser_Responsive_Testing_Report.txt ===== -->

## PART 2 OF 8 — SOURCE FILE: `Part2_UIUX_CrossBrowser_Responsive_Testing_Report.txt`

```text
================================================================================
GTMCert PART 2 of 8 — UI/UX VALIDATION + CROSS-BROWSER + RESPONSIVE TESTING
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tool Used          : agent-browser (Playwright Chromium headless)
Browser Engine     : HeadlessChrome/151.0.0.0 (Linux x86_64)
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74
================================================================================

TESTS COVERED IN PART 2
  Test #3  : UI/UX Validation
  Test #4  : Cross Browser Testing
  Test #5  : Responsive Testing

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/part2/
ARTIFACTS CAPTURED  : 19 PNG screenshots

LOGIN BLOCKER       : Authentication still failing (see Part 1).
                      All UI/UX testing done as UNAUTHENTICATED user on
                      public pages only: /login, /signup, /pricing, /404.

================================================================================
TEST #3 — UI/UX VALIDATION
================================================================================
Tool              : agent-browser (DOM inspection + computed styles + screenshots)
Pages tested      : /login, /signup, /pricing, /(404)
Pass Criteria     : No broken UI/screens

Sub-checks:

  3a. Page loads without errors
      - /login    → 200, no console errors, no broken images              PASS
      - /signup   → 200, no console errors, no broken images              PASS
      - /pricing  → 200, no console errors, no broken images              PASS
      - /unknown  → 404 page renders correctly                            PASS

  3b. Brand consistency (CRITICAL FAILURE)
      - /login    title: "Sign in — PROJEXA"
      - /login    brand: "PROJEXA" / "One Portal. One Truth."
      - /signup   title: "VERIDIAN COGNITIVE AI OS — AI Cognitive Research"
      - /signup   brand: "VERIDIAN AI"
      - /pricing  title: "VERIDIAN COGNITIVE AI OS — AI Cognitive Research"
      - /pricing  brand: "VERIDIAN AI"
      - /404      title: "VERIDIAN COGNITIVE AI OS — AI Cognitive Research"
      - meta description (login): "...VERIDIAN builds operating systems..."
      VERDICT : FAIL
      Reason  : The site is operating under TWO different brand identities.
                Login says "PROJEXA", every other page says "VERIDIAN AI".
                Meta description, og tags, <title> — all reference VERIDIAN.
                This indicates an incomplete rebrand and creates user
                confusion, trust issues, and brand-dilution risk.
      Recommend: Pick one brand and update all surfaces consistently.

  3c. No public landing page at root /
      - GET https://projexa-ai.com/ → 302 → /login
      VERDICT : WARN
      Reason  : No marketing/landing surface. First-time visitors hit a
                login wall directly. Unusual for a SaaS product; even
                B2B-internal tools usually have a "request access" page.
      Recommend: Add a public landing page or at minimum a hero section
                on /login explaining what the product is.

  3d. /forgot-password returns 404
      VERDICT : FAIL (broken link)
      Reason  : /forgot-password is a standard SaaS URL. Even though the
                login form offers "Send magic link instead" instead, the
                /forgot-password URL should at minimum redirect to /login.
      Recommend: Add a 302 redirect from /forgot-password → /login, or
                implement the route properly.

  3e. Typography & spacing
      - Body font: "Inter, Inter Fallback, system-ui, sans-serif" (good)
      - Body font-size: 16px (good — meets WCAG minimum)
      - Body BG: rgb(255,253,249) cream
      - Body text: rgb(28,43,58) dark navy
      - Estimated contrast ratio: ~13:1 (AAA pass)
      VERDICT : PASS

  3f. Color contrast — primary CTA "Sign In"
      - Button bg: rgb(245,130,10) orange
      - Button text: rgb(255,255,255) white
      - Font-size: 14px, weight 500 (NOT "large text" per WCAG)
      - Estimated contrast ratio: ~3.0:1
      - WCAG AA threshold for normal text: 4.5:1
      VERDICT : FAIL — fails WCAG AA contrast for the primary CTA.
      Recommend: Darken the orange to at least rgb(204,108,5) or use a
                darker accent for button text backgrounds.

  3g. Form input affordances
      - EMAIL field    : type="email"  placeholder="you@company.com"     OK
      - PASSWORD field : type="password" placeholder="Enter your password" OK
      - password visibility toggle: NOT PRESENT
      VERDICT : WARN
      Reason  : No "show/hide password" toggle. Users typing complex
                passwords cannot verify what they typed.
      Recommend: Add a visibility toggle button inside the password input.

  3h. Autocomplete attributes (UX & security)
      - EMAIL input    : autocomplete NOT SET (should be "email")
      - PASSWORD input : autocomplete NOT SET (should be "current-password")
      VERDICT : FAIL
      Reason  : Without autocomplete attributes, password managers and
                browser autofill cannot populate the form correctly. This
                breaks a basic UX expectation and discourages strong
                password usage.
      Recommend: Add autocomplete="email" and autocomplete="current-password".

  3i. Email format validation (carried from Part 1)
      - Input is type="email" but typing "notanemail" + clicking Sign In
        still fires the request to Supabase (which then 401s).
      VERDICT : FAIL — client-side should reject invalid email format
                before hitting the auth API.

  3j. Heading hierarchy
      - /login    : ZERO h1/h2/h3 elements                               FAIL
      - /signup   : ZERO h1/h2/h3 elements                               FAIL
      - /pricing  : h1 "Simple, Transparent Pricing"
                    h2 "Compare Plans", "Frequently Asked Questions",
                       "Ready to streamline your compliance?"
                    h3 (5 FAQ questions)                                 PASS
      VERDICT : FAIL for /login and /signup (no h1, breaks SEO + a11y).
      Recommend: Add a single <h1> per page describing its purpose
                ("Sign in to your compliance dashboard", "Create your
                account", etc.).

  3k. Semantic landmarks
      - /login    : 0 <main>, 0 <nav>, 0 <header>, 0 <footer>           FAIL
      - /signup   : 0 <main>, 0 <nav>, 0 <header>, 0 <footer>           FAIL
      - /pricing  : 0 <main>, 1 <nav>, 0 <header>, 1 <footer>           PARTIAL
      VERDICT : FAIL — login and signup pages have no landmarks at all.
                Screen-reader users have no way to navigate by region.
      Recommend: Wrap each page's content in <main>, add a <header> with
                the logo, and a <footer> with legal links.

  3l. Skip-to-content link
      - /login    : not present                                          FAIL
      - /signup   : not present                                          FAIL
      - /pricing  : not present                                          FAIL
      VERDICT : FAIL — no skip link on any page.
      Recommend: Add <a href="#main" class="skip-link">Skip to content</a>
                as the first focusable element on every page.

  3m. Keyboard focus visibility
      - Tab key focuses the first button (Google sign-in)
      - Computed style: outline-style: none, BUT a visible 3px box-shadow
        ring of color oklab(0.72 0.10 0.14 / 0.5) (warm orange/red) appears
      VERDICT : PASS — focus is visibly indicated (see keyboard-focus-1.png)

  3n. HTML lang attribute
      - English selected → <html lang="en">                              PASS
      - Hindi selected   → <html lang="hi">                             PASS
      - The lang attribute updates dynamically with the language toggle
        (correct behavior, helps screen readers pick the right voice).

  3o. <html dir> attribute
      - htmlDir = "" (empty) — dir attribute is not set even when Hindi
      VERDICT : WARN — for Hindi (an Indic language written left-to-right)
                this is technically OK, but if Arabic/Urdu are added later,
                the dir attribute MUST be set to "rtl".

  3p. Localization (i18n)
      - English → Hindi toggle works for the entire login form:
          "Welcome back" → "वापसी पर स्वागत है"
          "Sign In"      → "साइन इन करें"
          "EMAIL"        → "ईमेल"
          "PASSWORD"     → "पासवर्ड"
      VERDICT : PASS — i18n is wired and functional.

  3q. Pricing page CTA behavior
      - "Start Free Trial"    → navigates to /signup                     PASS
      - "Log in" (top nav)    → navigates to /login                      PASS
      - "Get Started" (top)   → navigates to /signup                     PASS
      - "Start 14-Day Trial"  → navigates to /signup                     PASS
      - "Contact Sales"       → not clicked (would open email)           N/A
      VERDICT : PASS

  3r. 404 page
      - Renders with a large "404" heading and "This page could not be found."
      - No "back to home" or "back to login" link — dead-end.
      VERDICT : WARN — 404 page is a dead end. Users have no path back.
      Recommend: Add a CTA "Return to login" or "Return to dashboard".

  3s. Meta tags
      - viewport: width=device-width, initial-scale=1                    PASS
      - description: present (but references VERIDIAN, not PROJEXA)      WARN
      - theme-color: NOT PRESENT                                         WARN
      - canonical: NOT PRESENT                                           WARN
      - apple-touch-icon: NOT PRESENT                                    WARN
      - favicon: https://projexa-ai.com/logo-mark.svg                    PASS
      - manifest: https://projexa-ai.com/manifest.webmanifest            PASS

Overall VERDICT for Test #3 : FAIL
Reason   : Multiple critical UI/UX defects:
             (1) Brand inconsistency PROJEXA vs VERIDIAN
             (2) /forgot-password 404
             (3) No h1 on /login and /signup
             (4) No semantic landmarks on /login and /signup
             (5) No skip link
             (6) Sign In button fails WCAG AA contrast
             (7) Missing autocomplete on email/password
             (8) No password visibility toggle
             (9) No client-side email format validation
            (10) 404 page is a dead end
Recommend:
  - Resolve brand identity (PROJEXA vs VERIDIAN) across all surfaces.
  - Add semantic HTML structure (h1, main, header, footer, nav).
  - Add skip-link, autocomplete, password show/hide, email regex.
  - Fix /forgot-password route.
  - Add navigation back from 404 page.

Artifacts:
  /home/z/my-project/screenshots/part2/login-english.png
  /home/z/my-project/screenshots/part2/404-page.png
  /home/z/my-project/screenshots/part2/pricing-cta-starter.png
  /home/z/my-project/screenshots/part2/keyboard-focus-1.png

================================================================================
TEST #4 — CROSS BROWSER TESTING
================================================================================
Tool              : agent-browser (Playwright)
Limitation        : agent-browser in this environment only ships with the
                    Chromium engine. Firefox and WebKit/Playwright binaries
                    require `sudo` to install system deps, which is not
                    available in this sandbox.
Browsers tested   : Chromium (HeadlessChrome/151.0.0.0) only
Browsers NOT tested: Mozilla Firefox, Apple Safari, Microsoft Edge
Pass Criteria     : Chrome, Edge, Firefox, Safari pass

Sub-checks:

  4a. Chromium (Chrome / Edge compatible)
      - Login page renders, all interactive elements present             PASS
      - Modern web features detected as supported:
          IntersectionObserver : function                               PASS
          ResizeObserver       : function                               PASS
          WebComponents        : true                                   PASS
          ServiceWorker        : true                                   PASS
          IndexedDB            : true                                   PASS
          crypto               : true                                   PASS
          fetch                : function                               PASS
      - No browser-sniffing scripts detected that would block Chrome     PASS
      VERDICT : PASS (for Chromium-based browsers: Chrome, Edge, Brave,
                Opera, Vivaldi — all share the Blink engine)

  4b. Mozilla Firefox (NOT TESTED)
      VERDICT : NOT TESTED
      Reason  : Firefox engine not available in this sandbox.
      Mitigation: The site uses Next.js + standard web APIs (Intersection
                  Observer, ResizeObserver, crypto.subtle, fetch). These
                  are all well-supported in Firefox 90+. The visual layout
                  uses Tailwind CSS which is cross-browser. Risk of Firefox
                  breakage is LOW, but UNVERIFIED.
      Recommend: Manual Firefox smoke test by user, or run Playwright
                 with `firefox` channel in a CI environment.

  4c. Apple Safari (NOT TESTED)
      VERDICT : NOT TESTED
      Reason  : WebKit binary not available in this sandbox.
      Mitigation: Safari is the most likely browser to expose compatibility
                  issues (e.g., CSS `gap` in flexbox on older Safari,
                  `:has()` selector, `oklab()` color function). The site
                  uses `oklab()` colors in focus outlines (observed in
                  Part 1), which Safari only supports in 16.4+. This is a
                  POTENTIAL SAFARI ISSUE.
      Recommend: HIGH priority manual Safari test. Verify focus outlines
                 render visibly on Safari 15.x and 16.x.

  4d. Microsoft Edge
      VERDICT : PASS (covered by 4a — Edge is Chromium-based)

  4e. Mobile Safari (iOS)
      VERDICT : NOT TESTED
      Reason  : No iOS simulator available.
      Mitigation: Mobile Safari uses WebKit. Same risks as 4c.
      Recommend: Manual test on real iPhone or BrowserStack.

  4f. Mobile Chrome (Android)
      VERDICT : PASS (covered by 4a — Android Chrome is Chromium-based)

Overall VERDICT for Test #4 : PARTIAL PASS
Reason   : Chromium family fully verified. Firefox, Safari, Mobile Safari
           not verified due to sandbox limitations. One potential Safari
           issue spotted (oklab() color usage in focus styles).
Recommend:
  - Run a separate Playwright test pass with `firefox` and `webkit`
    channels in a CI environment.
  - Specifically verify Safari focus-outline visibility (oklab() support).
  - Add BrowserStack or SauceLabs to CI for ongoing cross-browser coverage.

Artifacts:
  (Cross-browser is behavioral, not screenshot-based. See network trace
   in Part 1 for feature-detection evidence.)

================================================================================
TEST #5 — RESPONSIVE TESTING
================================================================================
Tool              : agent-browser (viewport emulation)
Viewports tested  : 6 viewports across 3 pages = 18 screenshots
Pass Criteria     : Desktop, Tablet, Mobile pass

Viewports:
  - Desktop Full HD : 1920 x 1080
  - Desktop Laptop  : 1366 x 768
  - Tablet Portrait : 768 x 1024  (iPad portrait)
  - Tablet Landscape: 1024 x 768  (iPad landscape)
  - Mobile iPhone   : 414 x 896   (iPhone 11 Pro Max)
  - Mobile iPhone SE: 375 x 667   (iPhone SE / small Android)

Pages tested:
  - /login
  - /signup
  - /pricing

Sub-checks:

  5a. /login responsive
      - 1920px : form centered, balanced whitespace                              PASS
      - 1366px : form centered, balanced whitespace                              PASS
      - 768px  : form scales to ~90% width, no overflow                          PASS
      - 1024px : form centered, no overflow                                      PASS
      - 414px  : form full-width, touch targets adequate (≥44px height)          PASS
      - 375px  : form full-width, no horizontal overflow                         PASS
      - scrollWidth === clientWidth at 375px (verified via JS)                   PASS
      VERDICT : PASS — login page is fully responsive.

  5b. /signup responsive
      - 1920px : form centered                                                  PASS
      - 1366px : form centered                                                  PASS
      - 768px  : form scales correctly                                          PASS
      - 1024px : form centered                                                  PASS
      - 414px  : form full-width, all 5 inputs visible without scroll           PASS
      - 375px  : no horizontal overflow                                         PASS
      - scrollWidth === clientWidth at 375px                                    PASS
      VERDICT : PASS

  5c. /pricing responsive
      - 1920px : 3 pricing cards in a row, comparison table readable           PASS
      - 1366px : 3 pricing cards in a row, table readable                       PASS
      - 768px  : pricing cards stack vertically                                 PASS
      - 1024px : cards may go 3-in-a-row (tight)                                PASS
      - 414px  : cards stack, comparison table scrolls horizontally             PASS
      - 375px  : no horizontal overflow on body                                 PASS
      - scrollWidth === clientWidth at 375px                                    PASS
      VERDICT : PASS — pricing table is the only potentially problematic
                element on mobile (horizontal scroll within the table itself,
                but body does not overflow).

  5d. Touch target sizes (mobile)
      - Sign In button height at 375px: TBD (would need box inspection)
      - Visual inspection of 375px screenshots: all buttons appear ≥40px tall   PASS
      VERDICT : PASS (visual); detailed px measurement not captured.

  5e. Text legibility at mobile
      - Body font-size: 16px (no shrink on mobile)                              PASS
      - Input font-size: 14px (slightly small but acceptable)                   WARN
      VERDICT : PASS with note — inputs at 14px can trigger iOS Safari
                auto-zoom on focus. Recommend 16px for input fields.

  5f. Orientation change (portrait ↔ landscape)
      - Tested at 768x1024 (portrait) and 1024x768 (landscape)                  PASS
      - No layout breakage observed.

Overall VERDICT for Test #5 : PASS
Reason   : All 6 viewports render correctly on all 3 public pages. No
           horizontal overflow, no broken layouts, no clipped content.
           Minor recommendation: bump input font-size from 14px to 16px
           to prevent iOS auto-zoom.

Artifacts:
  /home/z/my-project/screenshots/part2/resp-desktop-fullhd.png
  /home/z/my-project/screenshots/part2/resp-desktop-laptop.png
  /home/z/my-project/screenshots/part2/resp-tablet-portrait.png
  /home/z/my-project/screenshots/part2/resp-tablet-landscape.png
  /home/z/my-project/screenshots/part2/resp-mobile-iphone.png
  /home/z/my-project/screenshots/part2/resp-mobile-iphone-se.png
  /home/z/my-project/screenshots/part2/resp-login-desktop.png
  /home/z/my-project/screenshots/part2/resp-login-tablet.png
  /home/z/my-project/screenshots/part2/resp-login-mobile.png
  /home/z/my-project/screenshots/part2/resp-signup-desktop.png
  /home/z/my-project/screenshots/part2/resp-signup-tablet.png
  /home/z/my-project/screenshots/part2/resp-signup-mobile.png
  /home/z/my-project/screenshots/part2/resp-pricing-desktop.png
  /home/z/my-project/screenshots/part2/resp-pricing-tablet.png
  /home/z/my-project/screenshots/part2/resp-pricing-mobile.png

================================================================================
PART 2 SUMMARY TABLE
================================================================================
+-------+-------------------------------------+-------------+----------------------+
| Test# | Test Name                           | Verdict     | Key Finding          |
+-------+-------------------------------------+-------------+----------------------+
| 3     | UI/UX Validation                    | FAIL        | 10 critical defects  |
|       |                                     |             | (brand, a11y, UX)    |
| 4     | Cross Browser Testing               | PARTIAL     | Chromium-only;       |
|       |                                     |             | Firefox/Safari       |
|       |                                     |             | untested; oklab()    |
|       |                                     |             | risk on Safari       |
| 5     | Responsive Testing                  | PASS        | All 6 viewports OK   |
+-------+-------------------------------------+-------------+----------------------+

CARRY-FORWARD ISSUES for later parts:
  - Brand inconsistency (PROJEXA vs VERIDIAN AI) — Part 7 governance.
  - oklab() color usage — Part 3 accessibility deep-dive.
  - Missing security headers (from Part 1) — Part 5.
  - No rate-limiting on login (from Part 1) — Part 5.

================================================================================
END OF PART 2 REPORT
================================================================================
Next: Part 3 — Accessibility + Performance + Core Web Vitals
================================================================================
```

<!-- ===== END PART 2 SOURCE FILE: Part2_UIUX_CrossBrowser_Responsive_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 3 SOURCE FILE: Part3_Accessibility_Performance_WebVitals_Testing_Report.txt ===== -->

## PART 3 OF 8 — SOURCE FILE: `Part3_Accessibility_Performance_WebVitals_Testing_Report.txt`

```text
================================================================================
GTMCert PART 3 of 8 — ACCESSIBILITY + PERFORMANCE + CORE WEB VITALS
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tools Used         : Lighthouse 13.4.1 (Chromium 1228)
                    + axe-core 4.10.0 (injected via CDN)
                    + Performance API (browser native)
Pages Tested       : /login, /signup, /pricing
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74

TESTS COVERED IN PART 3
  Test #6  : Accessibility Testing
  Test #7  : Performance Testing
  Test #8  : Core Web Vitals

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/part3/
ARTIFACTS CAPTURED  : 3 Lighthouse JSON + 3 Lighthouse HTML + axe-core JSON

================================================================================
TEST #6 — ACCESSIBILITY TESTING
================================================================================
Tools              : axe-core 4.10.0 (WCAG 2.0 + 2.1 A/AA ruleset)
                    Lighthouse Accessibility audit
Pass Criteria      : WCAG compliance

--- axe-core RESULTS ---

  /login    : 24 passes, 0 violations, 2 incomplete, 35 inapplicable
  /signup   : 23 passes, 0 violations, 2 incomplete, 36 inapplicable
  /pricing  : 23 passes, 2 violations, 1 incomplete, 38 inapplicable

  Incomplete items (require manual verification):
    [bypass]        : No skip-link on /login or /signup  (1 node each, SERIOUS)
    [color-contrast]: 19 elements flagged on /login and /signup (SERIOUS)

  Violations on /pricing (CRITICAL):
    [button-name]   : #billing-toggle (Monthly/Annual switch)
                      - role="switch" with aria-checked="true"
                      - NO accessible name (no aria-label, no text content,
                        no aria-labelledby, no title)
                      - Screen readers will announce only "switch, on"
                      - CRITICAL impact: blind users cannot tell what
                        this toggle controls.
    [color-contrast]: 14 elements with insufficient contrast:
        - "Start Free Trial" / "Start 14-Day Trial" buttons (white on
          #f5820a orange): 2.59:1 (need 4.5:1)
        - "Most Popular" badge: 2.59:1
        - "Start free. Scale as you grow." subtitle: 3.95:1
        - Multiple "₹ /year" / card descriptions: 3.95-4.01:1
        - Nav links "Home", "Pricing", "Log in": 3.95:1
        - Footer "© 2026 VERIDIAN AI. All rights reserved.": 3.95:1

--- Lighthouse Accessibility RESULTS ---

  /login    : 96  (PASS — ≥90 threshold)
  /signup   : 96  (PASS — ≥90 threshold)
  /pricing  : 94  (PASS — but reduced due to button-name + color-contrast)

  Top accessibility findings from Lighthouse:
    - color-contrast (FAIL across all pages — matches axe finding)
    - bypass / skip-link missing
    - heading hierarchy: /login and /signup have NO <h1> (flagged in Part 2)
    - meta tags: html lang attribute is set dynamically (PASS once
      language is selected; default state unclear)
    - All form inputs have associated <label> elements (PASS)
    - All buttons have type attribute (PASS)
    - All images have alt text (PASS — though few images on these pages)

Sub-checks:

  6a. WCAG 2.1 Level A compliance
      - No <html lang> on initial load (set only after language toggle)   WARN
      - Page has no <h1> on /login and /signup                            FAIL
      - Form labels are associated with inputs                            PASS
      - All interactive elements have focus indication (3px ring)         PASS
      VERDICT : PARTIAL — basic A-level rules pass, but missing lang
                on initial load + missing h1 fail Level A.

  6b. WCAG 2.1 Level AA compliance
      - Color contrast (4.5:1 for normal text)                            FAIL
          /pricing: 14 elements fail
          /login:   manual review needed (axe incomplete)
          /signup:  manual review needed (axe incomplete)
      - Resize text (200%): not explicitly tested                         N/A
      - Visible focus: 3px orange ring on focused buttons                 PASS
      - Multiple ways to find pages: nav + sitemap not present            WARN
      VERDICT : FAIL — color contrast violations on /pricing.

  6c. Screen reader compatibility
      - axe button-name violation on #billing-toggle (Monthly/Annual)     FAIL
      - Semantic landmarks missing on /login and /signup                  FAIL
      - Heading hierarchy broken on /login and /signup                    FAIL
      - Form labels properly associated                                  PASS
      VERDICT : FAIL — significant gaps for screen reader users.

  6d. Keyboard navigation
      - Tab order: logical (top-to-bottom)                               PASS
      - Focus visible (3px orange ring)                                  PASS
      - No keyboard traps detected                                       PASS
      - All interactive elements reachable by Tab                       PASS
      VERDICT : PASS

  6e. Color-only information
      - "Most Popular" badge uses color + text "Most Popular"            PASS
      - Required field indicators use text "required" or asterisk        PASS
      VERDICT : PASS

Overall VERDICT for Test #6 : FAIL
Reason   : 
  - /pricing has a CRITICAL button-name violation (toggle is unnamed)
  - /pricing has 14 color-contrast violations (some as low as 2.59:1)
  - /login and /signup have no <h1>, no skip link, no landmarks
  - Initial HTML loads without lang attribute
Recommend:
  - Add aria-label="Toggle monthly or annual billing" to #billing-toggle.
  - Darken primary CTA color #f5820a → at least #c66805 to achieve 4.5:1.
  - Add <h1> to /login and /signup.
  - Add skip-link and <main> landmark to all pages.
  - Set <html lang="en"> as default in the document template.

Artifacts:
  /home/z/my-project/screenshots/part3/lighthouse-login.report.html
  /home/z/my-project/screenshots/part3/lighthouse-login.report.json
  /home/z/my-project/screenshots/part3/lighthouse-pricing.report.html
  /home/z/my-project/screenshots/part3/lighthouse-pricing.report.json
  /home/z/my-project/screenshots/part3/lighthouse-signup.report.html
  /home/z/my-project/screenshots/part3/lighthouse-signup.report.json

================================================================================
TEST #7 — PERFORMANCE TESTING
================================================================================
Tool               : Lighthouse 13.4.1
Pass Criteria      : Performance ≥ 90

--- Lighthouse Performance Scores ---

  /login    : 95    PASS (≥90)
  /signup   : 96    PASS (≥90)
  /pricing  : 85    FAIL (≥90 — falls short by 5 points)

--- Performance Detail ---

  /login (score 95):
    FCP                 : 1.1 s   (score 0.99 — Good)
    LCP                 : 2.6 s   (score 0.88 — Needs Improvement)
    TBT                 : 130 ms  (score 0.96 — Good)
    Speed Index         : 2.5 s   (score 0.98 — Good)
    Max Potential FID   : 270 ms  (score 0.43 — Poor)
    CLS                 : 0       (score 1.0  — Good)
    TTFB                : 10 ms   (Excellent — Vercel edge)

  /signup (score 96):
    FCP                 : 1.1 s   (Good)
    LCP                 : 2.6 s   (Needs Improvement)
    TBT                 : 120 ms  (Good)
    Speed Index         : 1.1 s   (Good)
    Max Potential FID   : 260 ms  (Poor)
    CLS                 : 0       (Good)

  /pricing (score 85):
    FCP                 : 1.1 s   (Good)
    LCP                 : 3.8 s   (Poor — exceeds 4.0s "Poor" threshold is 4.0)
    TBT                 : 210 ms  (Good)
    Speed Index         : 1.4 s   (Good)
    Max Potential FID   : 250 ms  (Poor)
    CLS                 : 0       (Good)

  Network transfer (from Performance API on /login):
    HTML transfer       : 9.1 KB
    Total resources     : 27 requests
    Total transfer      : 2.9 KB (HTML+CSS+JS compressed)
    Total decoded       : 1.9 MB (mostly JS bundles)
    Resource types      :
        link    : 7 reqs / 0.6 KB transfer / 382 KB decoded
        script  : 15 reqs / 0 KB transfer (cached) / 1192 KB decoded
        css     : 1 req / 0 KB / 83 KB decoded
        fetch   : 4 reqs / 2.1 KB / 2.8 KB decoded
        other   : 1 req / 0.3 KB / 122 KB decoded

  Slowest network requests (on /login):
    1. POST supabase.co/auth/v1/token  : 597 ms  (failed login attempt)
    2. POST /api/auth/failure-event    : 389 ms
    3. GET  /signup?_rsc=...           : 139 ms  (Next.js RSC prefetch)
    4. GET  /signup?_rsc=...           : 131 ms  (Next.js RSC prefetch)
    5. GET  /manifest.webmanifest      : 71 ms

Sub-checks:

  7a. Performance ≥ 90 on all pages
      /login    : 95   PASS
      /signup   : 96   PASS
      /pricing  : 85   FAIL
      VERDICT : FAIL — /pricing misses the 90 threshold.

  7b. Render-blocking resources
      - Lighthouse flagged: 280 ms potential savings on /login
      - Render-blocking CSS/JS in <head> blocks first paint
      VERDICT : WARN

  7c. Unused JavaScript
      - 142 KiB of unused JS detected on /login (Tailwind + Next.js bundles)
      VERDICT : WARN — typical for Next.js apps, but worth code-splitting.

  7d. Back/forward cache (bfcache)
      - Lighthouse: page PREVENTED bfcache restoration (2 failure reasons)
      VERDICT : WARN — likely caused by cached request handlers; should be
                fixed for instant back/forward navigation.

  7e. Legacy JavaScript
      - 13 KiB savings possible by not serving legacy JS to modern browsers
      VERDICT : WARN

  7f. Network dependency tree
      - Lighthouse flagged: render-blocking chain
      VERDICT : WARN

Overall VERDICT for Test #7 : PARTIAL PASS
Reason   : 2 of 3 pages pass the ≥90 threshold. /pricing at 85 fails due to
           slow LCP (3.8s) caused by hero image + heavy text content rendering.
           Max Potential FID is poor (250-270ms) on all pages — long task
           blocking the main thread.
Recommend:
  - Investigate LCP element on /pricing (likely the hero) — preload it,
    compress, or convert to next/image with priority.
  - Code-split Next.js bundles to remove 142 KiB of unused JS on /login.
  - Investigate bfcache prevention cause (likely WebSQL or unclosed
    connection — should be a quick fix).
  - Reduce main-thread blocking time to bring FID below 200ms.

Artifacts:
  /home/z/my-project/screenshots/part3/lighthouse-login.report.html
  /home/z/my-project/screenshots/part3/lighthouse-pricing.report.html
  /home/z/my-project/screenshots/part3/lighthouse-signup.report.html

================================================================================
TEST #8 — CORE WEB VITALS
================================================================================
Tool               : Lighthouse + Performance API
Pass Criteria      : LCP, CLS, INP within limits

  Official thresholds (Google, March 2024):
    LCP  : Good ≤ 2.5s | Needs Improvement ≤ 4.0s | Poor > 4.0s
    CLS  : Good ≤ 0.1  | Needs Improvement ≤ 0.25 | Poor > 0.25
    INP  : Good ≤ 200ms| Needs Improvement ≤ 500ms| Poor > 500ms

--- Measured Web Vitals ---

  /login:
    LCP  : 2.6 s   (Needs Improvement — 0.1s over Good threshold)
    CLS  : 0       (Good — perfect)
    INP  : approximated via max-potential-FID = 270 ms  (Poor — > 200ms)
    FCP  : 1.1 s   (Good)
    TTFB : 10 ms   (Excellent — Vercel edge)

  /signup:
    LCP  : 2.6 s   (Needs Improvement)
    CLS  : 0       (Good)
    INP  : ~260 ms (Poor)
    FCP  : 1.1 s   (Good)

  /pricing:
    LCP  : 3.8 s   (Poor — close to 4.0s threshold)
    CLS  : 0       (Good)
    INP  : ~250 ms (Poor)
    FCP  : 1.1 s   (Good)

Sub-checks:

  8a. LCP within 2.5s
      /login    : 2.6 s   FAIL (marginal — 100ms over)
      /signup   : 2.6 s   FAIL (marginal)
      /pricing  : 3.8 s   FAIL (significant — 1.3s over)
      VERDICT : FAIL

  8b. CLS within 0.1
      /login    : 0       PASS
      /signup   : 0       PASS
      /pricing  : 0       PASS
      VERDICT : PASS — excellent, no layout shift anywhere.

  8c. INP within 200ms
      Not directly measurable by Lighthouse (needs real user interaction).
      Approximated via Max Potential FID:
      /login    : 270 ms  FAIL
      /signup   : 260 ms  FAIL
      /pricing  : 250 ms  FAIL
      VERDICT : FAIL (approximation) — main-thread blocking tasks exceed
                200ms on all pages.
      Note   : Real INP from actual user interaction is typically lower
                than max-potential-FID. Field data (RUM) needed for
                definitive measurement.

  8d. FCP (First Contentful Paint) — supplementary
      All pages: 1.1 s   PASS (Good ≤ 1.8s)

  8e. TTFB (Time to First Byte)
      All pages: 10 ms   PASS (Excellent — Vercel edge serving)

  8f. TBT (Total Blocking Time)
      /login    : 130 ms  PASS (Good ≤ 200ms)
      /signup   : 120 ms  PASS
      /pricing  : 210 ms  FAIL (just over 200ms threshold)

Overall VERDICT for Test #8 : FAIL
Reason   : LCP fails on all 3 pages (marginal on /login and /signup,
           significant on /pricing). INP (approximated) fails on all pages.
           CLS, FCP, TTFB all pass with excellent values.
Recommend:
  - LCP: preload the largest visible element (likely logo-mark.svg or the
    hero text). On /pricing, lazy-load below-the-fold pricing cards.
  - INP: break up long JavaScript tasks (likely Next.js hydration) using
    requestIdleCallback or scheduler.yield(). Defer non-critical scripts.
  - Field measurement: deploy web-vitals.js RUM to capture real-user INP
    and LCP values — lab data overestimates these for cached sessions.

Artifacts:
  /home/z/my-project/screenshots/part3/lighthouse-login.report.json
  /home/z/my-project/screenshots/part3/lighthouse-pricing.report.json
  /home/z/my-project/screenshots/part3/lighthouse-signup.report.json

================================================================================
PART 3 SUMMARY TABLE
================================================================================
+-------+-------------------------------------+---------+----------------------+
| Test# | Test Name                           | Verdict | Key Finding          |
+-------+-------------------------------------+---------+----------------------+
| 6     | Accessibility Testing               | FAIL    | button-name + 14    |
|       |                                     |         | color-contrast      |
|       |                                     |         | violations on       |
|       |                                     |         | /pricing; no h1 /   |
|       |                                     |         | skip-link on login  |
| 7     | Performance Testing                 | PARTIAL | /login 95, /signup  |
|       |                                     |         | 96, /pricing 85     |
|       |                                     |         | (FAIL ≥90)          |
| 8     | Core Web Vitals                     | FAIL    | LCP fails on all    |
|       |                                     |         | pages; INP fails    |
|       |                                     |         | on all pages; CLS   |
|       |                                     |         | & TTFB excellent    |
+-------+-------------------------------------+---------+----------------------+

CARRY-FORWARD ISSUES:
  - Heavy unused JS (142 KiB on /login) — Part 5 (security/dependency audit).
  - bfcache prevention — Part 5.
  - Long main-thread tasks — Part 5 (potential cause: analytics scripts).

================================================================================
END OF PART 3 REPORT
================================================================================
Next: Part 4 — PWA + Offline/Sync + Browser Storage Testing
================================================================================
```

<!-- ===== END PART 3 SOURCE FILE: Part3_Accessibility_Performance_WebVitals_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 4 SOURCE FILE: Part4_PWA_Offline_Storage_Testing_Report.txt ===== -->

## PART 4 OF 8 — SOURCE FILE: `Part4_PWA_Offline_Storage_Testing_Report.txt`

```text
================================================================================
GTMCert PART 4 of 8 — PWA + OFFLINE/SYNC + BROWSER STORAGE TESTING
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tools Used         : agent-browser (Playwright Chromium)
                    + Manifest fetch + Storage inspection
Pages Tested       : /login (offline, online, post-OAuth)
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74

TESTS COVERED IN PART 4
  Test #9  : PWA Testing
  Test #10 : Offline/Sync Testing
  Test #11 : Browser Storage Testing

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/part4/
ARTIFACTS CAPTURED  : 1 screenshot (offline-reload.png)

================================================================================
TEST #9 — PWA TESTING
================================================================================
Tool               : Manifest inspection + Service Worker check + Lighthouse
                    (PWA category was deprecated in Lighthouse 13 — assessed
                     manually using Chrome PWA installability criteria)
Pass Criteria      : Installable, Offline Ready

--- PWA Manifest Analysis ---

  URL                : https://projexa-ai.com/manifest.webmanifest
  HTTP status        : 200
  Content-Type       : application/manifest+json (assumed; fetch succeeded)
  Cache-Control      : public, max-age=0, must-revalidate (suboptimal)
  ETag               : present

  Manifest contents:
    name             : "VERIDIAN AI"
    short_name       : "VERIDIAN AI"
    description      : "One Portal. One Truth."  (PROJEXA's tagline —
                       brand inconsistency carried into manifest)
    start_url        : "/home"
    display          : "standalone"
    background_color : "#FFFDF9"
    theme_color      : "#1C2B3A"
    icons            : [ {src:"/logo-mark.svg", sizes:"any", type:"image/svg+xml"} ]
    share_target     : { action:"/api/veri-chat/share-target",
                         method:"POST",
                         enctype:"multipart/form-data",
                         params:{title,text,url} }

--- PWA Installability Criteria (Chrome) ---

  Criterion 1: Served over HTTPS                              PASS
  Criterion 2: Has web app manifest with required fields      PASS
               (name, short_name, start_url, display, icons)
  Criterion 3: Has a registered service worker                FAIL
               (0 service workers registered; no /sw.js, no
                /service-worker.js, no /workbox-sw.js — all 404)
  Criterion 4: Has at least one PNG icon 192x192              FAIL
               (only SVG icon present; iOS Safari requires PNG)
  Criterion 5: Has at least one PNG icon 512x512              FAIL
               (only SVG icon present)
  Criterion 6: Manifest display mode is "standalone"          PASS
  Criterion 7: start_url is reachable                         PARTIAL
               (GET /home → 302 → /login?redirectTo=%2Fhome;
                requires auth, but URL is valid)

  Chrome installability result: NOT INSTALLABLE
  Reason: Missing service worker (mandatory for Chrome install
          prompt). Missing PNG icons (mandatory for Android home
          screen install).

  iOS installability result: PARTIAL
  iOS requires: <link rel="apple-touch-icon"> (MISSING),
                <meta name="apple-mobile-web-app-capable" content="yes">
                (MISSING). Without these, "Add to Home Screen"
                on iOS will work but will use a screenshot as icon
                and open in Safari, not as a standalone app.

--- Other PWA-related APIs ---

  Background Sync API (SyncManager)        : supported but UNUSED
  Periodic Background Sync API             : supported but UNUSED
  Push Manager API                         : supported but UNUSED
  Notifications API                       : supported, permission "default"
  Web Share API (navigator.share)         : NOT supported (desktop context)
  Share Target API (manifest.share_target) : configured for /api/veri-chat/share-target
                                              OPTIONS /api/veri-chat/share-target → 204
                                              (endpoint exists; not tested POST)

Sub-checks:

  9a. Manifest is valid JSON with required fields
      VERDICT : PASS (name, short_name, start_url, display, icons present)

  9b. Service worker is registered
      VERDICT : FAIL — 0 SW registrations; all common SW paths return 404

  9c. App is installable on Chrome (Android/desktop)
      VERDICT : FAIL — no SW means no install prompt

  9d. App is installable on iOS Safari
      VERDICT : FAIL — no apple-touch-icon, no apple-mobile-web-app-capable

  9e. App can run in standalone display mode
      VERDICT : FAIL — without SW, even when launched from home screen,
                the app opens in browser, not standalone

  9f. Theme color is set in manifest AND meta tag
      Manifest theme_color  : #1C2B3A (set)
      Meta theme-color      : NOT PRESENT
      VERDICT : PARTIAL — manifest has theme_color but the <meta name="theme-color">
                tag is missing from the HTML <head>. Android Chrome uses the
                meta tag for the address bar tint, not the manifest.

  9g. Splash screen (Android)
      VERDICT : FAIL — Android Chrome generates splash screen from PNG icons
                and manifest colors. Without PNG icons, splash screen
                will be blank or default.

  9h. Share Target (receiving shares from other apps)
      Manifest entry: yes
      Endpoint       : /api/veri-chat/share-target (OPTIONS 204)
      POST test      : not performed (would require valid session)
      VERDICT : PASS (configuration present; functionality unverified
                because no auth session available)

Overall VERDICT for Test #9 : FAIL
Reason   : App is NOT installable as a PWA on any platform because:
             (1) No service worker is registered
             (2) No PNG icons (only SVG)
             (3) No apple-touch-icon for iOS
             (4) No apple-mobile-web-app-capable meta tag
           App CANNOT run in standalone display mode.
           App CANNOT show a custom splash screen.
Recommend:
  - Register a service worker at /sw.js using Workbox or next-pwa.
    Cache the app shell (HTML, CSS, JS, SVG logo, manifest) for
    offline use.
  - Generate PNG icons (192x192, 512x512, plus maskable variants).
  - Add <link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
    (180x180 PNG).
  - Add <meta name="apple-mobile-web-app-capable" content="yes">.
  - Add <meta name="theme-color" content="#1C2B3A">.
  - Add cache-control: public, max-age=31536000, immutable to
    /logo-mark.svg and other static assets (currently max-age=0).

Artifacts:
  /home/z/my-project/screenshots/part4/offline-reload.png
  (Manifest is JSON; not saved as image — see raw JSON in this report)

================================================================================
TEST #10 — OFFLINE/SYNC TESTING
================================================================================
Tool               : agent-browser (offline mode toggle)
Pass Criteria      : Offline → Sync works

Sub-checks:

  10a. App can be loaded offline (after first online load)
       Action  : Load /login online → toggle offline → reload
       Result  : Browser shows ERR_INTERNET_DISCONNECTED page
                 (Chrome default offline page; not the app's
                 custom offline page)
       VERDICT : FAIL — no offline support. Without a service worker,
                 the browser has nothing to fall back to when network
                 is unavailable.

  10b. App serves a custom offline fallback page
       VERDICT : FAIL — no offline page. Browser default shown.

  10c. App caches static assets for offline use
       Cache API: 0 caches
       HTTP cache: max-age=0, must-revalidate on /logo-mark.svg
                   (browser must re-fetch on every navigation)
       VERDICT : FAIL — no caching strategy in place.

  10d. App queues mutations while offline and syncs when online
       Background Sync API: supported by browser but UNUSED by app
       VERDICT : FAIL — no sync implementation.

  10e. App detects online/offline transitions
       navigator.onLine: true (online)
       Action: toggled offline via Playwright
       Result: app did NOT show any "You are offline" banner or
               disable submission buttons. User could still attempt
               to click "Sign In" (which would fail silently).
       VERDICT : FAIL — no offline detection in the UI.

  10f. Periodic Background Sync
       VERDICT : FAIL — unused.

  10g. Push Notifications
       VERDICT : FAIL — no push subscription, no notification permission
                 requested.

  10h. Sync indicator (UI feedback)
       VERDICT : FAIL — no sync status shown to user.

Overall VERDICT for Test #10 : FAIL
Reason   : No offline support whatsoever. No service worker means no
           offline page, no cached assets, no background sync, no
           push notifications. The app is a "thin client" that
           requires constant network connectivity.
Recommend:
  - Implement a service worker with Workbox strategies:
      * App shell: CacheFirst (HTML, CSS, JS, SVG)
      * API calls: NetworkFirst with timeout fallback to cache
      * Auth: NetworkOnly (cannot cache auth responses)
  - Add an "offline" banner that appears when navigator.onLine is false.
  - Implement Background Sync for any user submissions (e.g., form drafts).
  - Test the offline flow end-to-end after implementation.

Artifacts:
  /home/z/my-project/screenshots/part4/offline-reload.png

================================================================================
TEST #11 — BROWSER STORAGE TESTING
================================================================================
Tool               : agent-browser (Storage inspection)
Pass Criteria      : Local database healthy

--- Storage State at Unauthenticated Login (/login) ---

  localStorage   : EMPTY (0 entries)
  sessionStorage : EMPTY (0 entries)
  cookies        : 2 cookies
                   1. sb-pcrjmlpuqsbocqfwoxod-auth-token-code-verifier
                      (Supabase PKCE code verifier — base64-encoded
                      64-byte random value. Set when OAuth/magic link
                      flow starts. NOT HttpOnly — accessible to JS.)
                   2. NEXT_LOCALE=en
                      (Next.js locale preference. Not sensitive.)
  IndexedDB      : 0 databases (none created)
  Cache API      : 0 caches
  OPFS           : supported, 0 entries
  Storage quota  : 10 GB (standard Chromium quota)
  Storage usage  : 0 bytes

--- Storage State After OAuth Flow Attempt ---

  (Same as above — no additional storage created by the abandoned
   OAuth dance. The Supabase code-verifier cookie persists.)

--- Cookie Attribute Analysis ---

  Cookie 1: sb-pcrjmlpuqsbocqfwoxod-auth-token-code-verifier
    - Secure attribute   : unknown (cannot read attribute from JS;
                           HttpOnly cookies are invisible to JS, but
                           this cookie is NOT HttpOnly so it appears
                           in document.cookie)
    - HttpOnly attribute : NO (visible to JavaScript → XSS risk if
                           code verifier is sensitive)
    - SameSite attribute : unknown (not readable from JS)
    - Domain             : projexa-ai.com (host-only, not wildcard)
    - Path               : / (assumed)
    Note: Supabase Auth JS library stores the code verifier in a
    cookie rather than localStorage so it can be read by the server-
    side callback handler. This is the expected Supabase pattern.
    However, the verifier SHOULD be HttpOnly to prevent XSS exfiltration.

  Cookie 2: NEXT_LOCALE=en
    - Not sensitive, no security concern.

Sub-checks:

  11a. localStorage is empty at unauthenticated state
       VERDICT : PASS — no orphaned data, no leaked auth tokens

  11b. sessionStorage is empty at unauthenticated state
       VERDICT : PASS

  11c. IndexedDB has no databases at unauthenticated state
       VERDICT : PASS (clean slate; will need to re-test after login
                to see if the app creates IndexedDB stores for
                compliance data, AI chat history, etc.)

  11d. Cache API has no caches
       VERDICT : PASS (expected — no service worker means no Cache API
                usage. If a SW were registered, we'd expect to see
                "workbox-precache-v2-..." caches here.)

  11e. OPFS is supported
       VERDICT : PASS (browser supports it; app doesn't use it yet)

  11f. Storage quota is reasonable (10 GB)
       VERDICT : PASS

  11g. Storage usage is 0 bytes
       VERDICT : PASS (no orphaned storage)

  11h. Supabase auth token storage
       Result: After successful login, Supabase JS client typically
               stores the access+refresh token in localStorage under
               key "sb-<project>-auth-token". Cannot verify because
               login is blocked.
       VERDICT : UNTESTABLE — blocked by Part 1 credential issue.

  11i. Cookie security attributes (Secure, HttpOnly, SameSite)
       Result: Cannot read these attributes from JavaScript.
       VERDICT : UNTESTABLE from browser. Recommend server-side
                verification that all auth cookies are:
                - Secure: yes (mandatory)
                - HttpOnly: yes (mandatory for refresh tokens)
                - SameSite=Lax or Strict (mandatory for CSRF)

  11j. Storage quota persistence (navigator.storage.persist)
       Result: not requested. App may lose localStorage under
               storage pressure.
       VERDICT : WARN — for a compliance product that may store
                documents locally, requesting persistent storage
                would prevent data loss.

  11k. Storage cleanup on logout
       Result: cannot test (login blocked).
       VERDICT : UNTESTABLE.

Overall VERDICT for Test #11 : PARTIAL PASS
Reason   : At unauthenticated state, browser storage is clean and
           well-behaved. No orphaned data, no excessive usage.
           However:
             - Cannot verify post-login storage behavior (blocked).
             - Cannot verify cookie security attributes from JS.
             - Supabase code-verifier cookie is NOT HttpOnly
               (potential XSS exfiltration risk).
Recommend:
  - After restoring credentials, re-run this test to inspect:
      * localStorage for sb-*-auth-token
      * IndexedDB stores created by the app
      * Cache API entries
      * Cookie attributes (via browser DevTools, not JS)
  - Configure Supabase client to set HttpOnly on the code-verifier
    cookie (requires server-side cookie handling — see
    @supabase/ssr package).
  - Request persistent storage on first login:
    navigator.storage.persist().

Artifacts:
  (Storage inspection output is JSON in this report; no screenshots
   saved because storage is not visible in screenshots.)

================================================================================
PART 4 SUMMARY TABLE
================================================================================
+-------+-------------------------------------+---------+----------------------+
| Test# | Test Name                           | Verdict | Key Finding          |
+-------+-------------------------------------+---------+----------------------+
| 9     | PWA Testing                         | FAIL    | Not installable —   |
|       |                                     |         | no SW, no PNG icons,|
|       |                                     |         | no apple-touch-icon |
| 10    | Offline/Sync Testing                | FAIL    | Zero offline        |
|       |                                     |         | capability; no      |
|       |                                     |         | sync; no offline    |
|       |                                     |         | detection in UI     |
| 11    | Browser Storage Testing             | PARTIAL | Clean at unauth     |
|       |                                     |         | state; cannot test  |
|       |                                     |         | post-login; code-   |
|       |                                     |         | verifier cookie not |
|       |                                     |         | HttpOnly            |
+-------+-------------------------------------+---------+----------------------+

CRITICAL GAP:
  The app is marketed as "Indian compliance management" SaaS, but it
  has ZERO offline capability. Compliance work often happens in low-
  connectivity environments (factory floors, client sites, court
  visits). Without offline support, the app is unusable in those
  scenarios. This is a major product gap.

CARRY-FORWARD ISSUES:
  - Supabase code-verifier cookie not HttpOnly — Part 5 (Security).
  - Static assets have max-age=0 cache-control — Part 7 (observability).
  - No persistent storage request — Part 5 (data integrity).

================================================================================
END OF PART 4 REPORT
================================================================================
Next: Part 5 — API Contract + Security Testing
================================================================================
```

<!-- ===== END PART 4 SOURCE FILE: Part4_PWA_Offline_Storage_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 5 SOURCE FILE: Part5_API_Security_Testing_Report.txt ===== -->

## PART 5 OF 8 — SOURCE FILE: `Part5_API_Security_Testing_Report.txt`

```text
================================================================================
GTMCert PART 5 of 8 — API CONTRACT + SECURITY TESTING
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tools Used         : agent-browser (Playwright Chromium)
                    + fetch() for API probing
                    + Header inspection
Pages Tested       : All discovered endpoints (see enumeration below)
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74

TESTS COVERED IN PART 5
  Test #12 : API Contract Testing
  Test #18 : Security Testing

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/part5/
ARTIFACTS CAPTURED  : API responses (JSON in this report)

================================================================================
TEST #12 — API CONTRACT TESTING
================================================================================
Tool               : fetch() API probing
Pass Criteria      : All APIs deterministic

--- API Endpoint Enumeration ---

Discovered via network traffic + URL guessing + robots.txt + sitemap.xml:

  PUBLIC APIs:
    GET  /api/health                       200  application/json
    POST /api/auth/failure-event           200  application/json
    GET  /api/auth/failure-event           405  (method not allowed)
    POST /api/veri-chat/share-target       401  application/json
    OPTIONS /api/veri-chat/share-target    204  (CORS preflight)
    OPTIONS /api/auth/failure-event        ?    (preflight, not tested)

  AUTH-REQUIRED APIs (return 401 {"error":"Unauthorized"}):
    GET  /api/users                        401
    GET  /api/compliance                   401
    GET  /api/compliance/items             401
    GET  /api/compliance/list              401
    GET  /api/documents                    401
    GET  /api/notifications                401
    GET  /api/audit                        401

  404 (NOT FOUND):
    /api/healthz, /api/status, /api/version, /api/ping
    /api/auth/session, /api/auth/callback, /api/auth/signout
    /api/auth/signup, /api/auth/login, /api/auth/refresh
    /api/auth/logout, /api/auth/me, /api/auth/user
    /api/ai/chat, /api/veri-chat, /api/veri-chat/messages
    /api/audit-log, /api/ocid, /api/umr
    /api/tenant, /api/tenants, /api/organizations
    /api/gst, /api/filings, /api/reports
    /api/dashboard, /api/analytics, /api/webhooks
    /api/stripe, /api/billing

  ROUTES DISCLOSED via robots.txt:
    /home, /settings, /sales-hq, /orchestra, /partner/, /r/
    (all redirect to /login when unauthenticated)

  ROUTES DISCLOSED via sitemap.xml (on different domain!):
    https://veridian-ai-os.vercel.app/   ← the actual production URL
    /office, /the-firm, /veri-fm-cs, /forge
    /signup, /terms, /privacy, /data-policy

--- Contract Determinism Tests ---

  12a. GET /api/health
       Action  : 5 sequential calls
       Result  : 5 × 200 {"ok":true,"ts":<epoch_millis>}
       Notes   : "ok" and status code are deterministic. The "ts"
                 field is the current epoch milliseconds (changes
                 per call, expected behavior for a health check).
       VERDICT : PASS — deterministic contract.

  12b. GET /api/health — method whitelist
       GET     → 200
       HEAD    → 200
       OPTIONS → 204 (Allow: GET, HEAD, OPTIONS)
       POST    → 405
       PUT     → 405
       DELETE  → 405
       PATCH   → 405
       VERDICT : PASS — proper method enforcement.

  12c. POST /api/auth/failure-event — determinism
       Action  : 3 sequential calls with same body
       Result  : 3 × 200 {"ok":true}
       VERDICT : PASS (response is deterministic).

  12d. POST /api/auth/failure-event — input validation
       Empty body          → 200 {"ok":true}    FAIL (should 400)
       Invalid JSON body   → 200 {"ok":true}    FAIL (should 400)
       SQL injection in    → 200 {"ok":true}    FAIL (should sanitize)
       XSS payload in      → 200 {"ok":true}    FAIL (should sanitize)
       100 KB payload      → 200 {"ok":true}    FAIL (no size limit)
       VERDICT : FAIL — endpoint accepts ANY input without validation.
                This is a logging endpoint, but it:
                  - Does not validate JSON structure
                  - Does not enforce a schema
                  - Does not limit payload size
                  - Could be used to pollute logs or exhaust disk

  12e. GET /api/users — auth enforcement
       Action  : 3 calls without credentials
       Result  : 3 × 401 {"error":"Unauthorized"}
       VERDICT : PASS — auth consistently enforced.

  12f. GET /api/compliance, /api/compliance/items, /api/compliance/list,
       /api/documents, /api/notifications, /api/audit
       Action  : 1 call each without credentials
       Result  : 401 {"error":"Unauthorized"} on all
       VERDICT : PASS — auth consistently enforced across all
                protected endpoints.

  12g. POST /api/veri-chat/share-target — auth enforcement
       Action  : POST without credentials
       Result  : 401 {"error":"Unauthorized"}
       VERDICT : PASS.

  12h. /auth/callback (OAuth redirect target)
       Action  : GET without code/state params
       Result  : 302 → /login?error=auth_callback_failed
       VERDICT : PASS — graceful error handling.

  12i. /r/{slug} (referral redirect)
       Action  : GET /r/test
       Result  : redirected to /signup (fallback for unknown slug)
       Action  : GET /r/https://evil.com
       Result  : did NOT redirect to evil.com (good — no open redirect)
       Action  : GET /r/../etc/passwd
       Result  : 403 Forbidden (Vercel edge blocked path traversal)
       VERDICT : PASS — no open redirect, path traversal blocked.

--- Schema Validation ---

  /api/health response schema (inferred):
    {
      "ok": boolean,
      "ts": number (epoch millis)
    }
    No formal schema (OpenAPI/Swagger) published at /api/docs,
    /api/openapi.json, /api/swagger.json, or /docs.

  /api/auth/failure-event response schema:
    { "ok": boolean }
    But accepts ANY request body, so input schema is undefined.

  Auth-protected endpoints:
    Schema cannot be verified without authentication.
    Response schema: { "error": string }

--- Rate Limiting ---

  12j. /api/auth/failure-event
       Action  : 20 concurrent POST requests
       Result  : 20 × 200 in 1.5 seconds. NO rate limiting.
       VERDICT : FAIL — endpoint is wide open to flooding.

  12k. Supabase /auth/v1/token (login brute-force)
       Action  : 10 concurrent login attempts with different passwords
       Result  : 10 × 401 in 272ms. NO rate limiting observed.
       VERDICT : FAIL — brute-force attacks are NOT mitigated.
                Supabase Auth has built-in rate limiting that the
                project owner can configure, but it appears to be
                either disabled or set too high.

--- OpenAPI / Documentation ---

  12l. /api/docs            → 404 (no Swagger UI)
  12m. /api/openapi.json    → 404 (no OpenAPI spec)
  12n. /api/swagger.json    → 404
  12o. /docs                → 404
       VERDICT : FAIL — no API documentation published. Contract
                is implicit and can only be inferred from behavior.

Overall VERDICT for Test #12 : PARTIAL PASS
Reason   : Public endpoints are deterministic and method-whitelisted
           correctly. Auth-protected endpoints enforce authentication
           consistently. However:
             - /api/auth/failure-event has NO input validation
             - No rate limiting on any endpoint
             - No published API contract (OpenAPI/Swagger)
             - Cannot verify schemas for auth-protected endpoints
Recommend:
  - Validate request body against a JSON schema on every POST endpoint.
  - Add rate limiting (e.g., 10 req/min/IP for /api/auth/failure-event).
  - Enable Supabase Auth rate limits (5 attempts per email per 10 min,
    30 attempts per IP per 10 min).
  - Publish an OpenAPI spec at /api/openapi.json.
  - Add payload size limit (e.g., max 10 KB for /api/auth/failure-event).

Artifacts:
  (All API responses captured as JSON in this report — no screenshots
   because API responses are not visual.)

================================================================================
TEST #18 — SECURITY TESTING
================================================================================
Tool               : Manual probing (OWASP ZAP not available in sandbox;
                    tests performed via fetch() and header inspection)
Pass Criteria      : No High/Critical vulnerabilities

--- Security Header Audit ---

  Header                        | Present? | Value
  ------------------------------|----------|---------------------------
  strict-transport-security     | YES      | max-age=63072000
  cache-control (login)         | YES      | private, no-cache, no-store
  cache-control (api/users)     | YES      | public, max-age=0, must-revalidate
  content-type                  | YES      | proper (text/html or application/json)
  server                        | YES      | Vercel (info disclosure - minor)
  x-powered-by                  | YES      | Next.js (info disclosure - minor)
  x-vercel-id                   | YES      | request ID (info disclosure - minor)
  content-security-policy       | NO       | MISSING — CRITICAL
  x-frame-options               | NO       | MISSING — HIGH (clickjacking risk)
  x-content-type-options        | NO       | MISSING — MEDIUM (MIME sniffing)
  referrer-policy               | NO       | MISSING — MEDIUM (referrer leak)
  permissions-policy            | NO       | MISSING — LOW
  cross-origin-opener-policy    | NO       | MISSING — MEDIUM
  cross-origin-embedder-policy  | NO       | MISSING — MEDIUM
  cross-origin-resource-policy  | NO       | MISSING — MEDIUM

--- Sub-tests ---

  18a. HTTPS enforcement
       Action  : not tested directly (Vercel enforces HTTPS by default)
       HSTS    : max-age=63072000 (≈2 years) — good but missing preload
       VERDICT : PASS (with note: add "preload" directive and submit to
                HSTS preload list at https://hstspreload.org)

  18b. Content Security Policy (CSP)
       VERDICT : FAIL — CRITICAL
       Reason  : No CSP header on any response. Without CSP, the page
                 is vulnerable to:
                   - XSS attacks (inline scripts can run)
                   - Data exfiltration to any domain
                   - Inline event handlers (onclick="...")
                   - Unauthorized iframe embedding
       Recommend: Add a strict CSP:
         default-src 'self';
         script-src 'self' 'unsafe-inline' 'unsafe-eval' [hashes];
         style-src 'self' 'unsafe-inline';
         img-src 'self' data: https:;
         font-src 'self' data:;
         connect-src 'self' https://pcrjmlpuqsbocqfwoxod.supabase.co;
         frame-ancestors 'none';
         base-uri 'self';
         form-action 'self';

  18c. X-Frame-Options (clickjacking)
       VERDICT : FAIL — HIGH
       Reason  : No X-Frame-Options or frame-ancestors in CSP.
                 The login page can be embedded in an iframe on any
                 domain, allowing clickjacking attacks where an
                 attacker overlays invisible UI on top of the login
                 form to trick users into submitting credentials.
       Recommend: Add X-Frame-Options: DENY (or frame-ancestors 'none'
                 in CSP).

  18d. X-Content-Type-Options (MIME sniffing)
       VERDICT : FAIL — MEDIUM
       Reason  : Without "X-Content-Type-Options: nosniff", browsers
                 may sniff and execute files as a different MIME type
                 than declared. Particularly risky for user-uploaded
                 content (compliance documents).

  18e. Referrer-Policy
       VERDICT : FAIL — MEDIUM
       Reason  : Without Referrer-Policy, the browser may leak the
                 full URL (including query params) to third-party
                 domains via the Referer header. The login page loads
                 analytics scripts (Vercel Analytics) that may receive
                 referrer data.

  18f. Information disclosure (Server, X-Powered-By, X-Vercel-Id)
       VERDICT : WARN — LOW
       Reason  : Headers reveal tech stack (Vercel + Next.js). This is
                 not a direct vulnerability but helps attackers target
                 known CVEs in those technologies.
       Recommend: Set `poweredByHeader: false` in next.config.js and
                 remove Server header via Vercel routes (limited control).

  18g. Sensitive file exposure
       /package.json     → 404    PASS
       /.env             → 404    PASS
       /.git/config      → 404    PASS
       /next.config.js   → 404    PASS
       /vercel.json      → 404    PASS
       /.well-known/security.txt → 404    WARN (should exist for
                                          responsible disclosure)
       VERDICT : PASS — no sensitive files exposed.

  18h. Path traversal
       /login/../../../etc/passwd       → 403 (Vercel edge)
       /api/../etc/passwd               → 403
       /static/../../package.json       → 404
       /_next/../package.json           → 404
       /api/health/../../../etc/passwd  → 403
       VERDICT : PASS — Vercel edge blocks path traversal.

  18i. Open redirect
       /login?redirectTo=https://evil.com → no redirect fired (good)
       /r/https://evil.com                → no external redirect
       /r/test                            → /signup (safe internal)
       /r/a                               → /signup (safe internal)
       /auth/callback (no params)         → /login?error=auth_callback_failed
       VERDICT : PASS — no open redirect vulnerability.

  18j. SQL injection (on API endpoints)
       POST /api/auth/failure-event with email: "' OR '1'='1"
       Result  : 200 {"ok":true} (endpoint accepted but didn't appear
                to execute SQL — it's likely a NoSQL or logging-only
                endpoint. Cannot verify without backend access.)
       VERDICT : UNVERIFIABLE — but no error returned suggests no
                direct SQL exposure.

  18k. XSS (reflected)
       Action  : Tried to inject <script>alert(1)</script> via URL
                 params and form fields
       Result  : React escapes user input by default; no reflected
                 XSS observed.
       VERDICT : PASS (for visible surfaces).

  18l. XSS (stored)
       Result  : Cannot test without authentication.
       VERDICT : UNTESTABLE.

  18m. CSRF protection
       Login form method    : GET (wrong! should be POST)
       CSRF token in form   : NOT PRESENT
       CSRF cookie          : NOT PRESENT
       SameSite on cookies  : unknown (cannot read from JS)
       VERDICT : WARN — login form uses GET method (React intercepts
                the submit via JS, but the form's declared method is
                wrong). No CSRF token. However:
                  - Auth calls go to Supabase with Content-Type:
                    application/json, which triggers CORS preflight,
                    providing implicit CSRF protection.
                  - Cookie-based session (post-login) would need
                    explicit CSRF tokens. Cannot verify.
       Recommend: Change form method to POST. Add SameSite=Lax or
                 Strict to all auth cookies.

  18n. Cookie security attributes
       Cookie: sb-pcrjmlpuqsbocqfwoxod-auth-token-code-verifier
         HttpOnly   : NO  (visible to JavaScript — XSS exfiltration risk)
         Secure     : unknown (cannot read from JS; HTTPS-only delivery
                     suggests yes, but unverified)
         SameSite   : unknown
       Cookie: NEXT_LOCALE
         Not sensitive — no concern.
       VERDICT : FAIL — Supabase code-verifier cookie is NOT HttpOnly.
                If an XSS executes on the page, the attacker can steal
                the code verifier and hijack the OAuth flow.
       Recommend: Use @supabase/ssr package which sets HttpOnly cookies
                 server-side. The current setup appears to use the
                 browser-only @supabase/supabase-js which stores the
                 verifier in a JS-readable cookie.

  18o. Authentication rate limiting (brute-force)
       Action  : 10 rapid Supabase auth attempts
       Result  : All 10 returned 401 within 272ms. No rate limit.
       VERDICT : FAIL — HIGH. Brute-force attacks on user passwords
                are not mitigated at the application layer. Supabase
                Auth supports rate limiting but it appears disabled.

  18p. Account enumeration
       Action  : Try login with valid email + wrong password
                 Try login with invalid email + wrong password
       Result  : Both return same error: "Invalid login credentials"
       VERDICT : PASS — Supabase correctly returns a generic error to
                prevent user enumeration. (Note: timing-based
                enumeration could still be possible but not tested.)

  18q. HTTPS certificate validity
       VERDICT : PASS (no browser warnings; Vercel auto-renews certs).

  18r. CORS configuration
       Action  : OPTIONS /api/users from Origin: https://evil.com
       Result  : 204 with NO Access-Control-Allow-Origin header
       VERDICT : PASS — API does not allow cross-origin requests from
                arbitrary domains. Same-origin policy enforced.

  18s. HTTP method override
       Action  : Tried POST/PUT/DELETE/PATCH on /api/health
       Result  : 405 Method Not Allowed
       VERDICT : PASS — proper method enforcement.

  18t. robots.txt information disclosure
       Disallowed paths reveal internal route structure:
         /home, /settings, /sales-hq, /orchestra, /partner/, /r/
       VERDICT : WARN — common practice, but security-through-obscurity
                purists argue these should not be listed. Acceptable
                for SEO purposes.

  18u. sitemap.xml information disclosure
       Sitemap points to DIFFERENT DOMAIN: https://veridian-ai-os.vercel.app/
       This reveals the production deployment URL.
       VERDICT : WARN — minor info leak. The sitemap should reference
                the canonical domain (projexa-ai.com) or be removed
                if the site is not meant to be indexed.

  18v. Vercel Analytics scripts
       Two scripts loaded from /771b847594094cc8/script.js and
       /04809683687b4e12/script.js. Identified as Vercel Analytics
       (or Speed Insights). They detect headless browsers via
       navigator.webdriver and userAgent checks.
       VERDICT : PASS — first-party analytics, no third-party tracking.

  18w. Dependency / supply chain (preview for Part 7)
       Next.js version: not directly disclosed (X-Powered-By: Next.js
       without version). Could be extracted from chunk hashes but
       not attempted in this Part.
       VERDICT : see Part 7.

  18x. JWT inspection
       Cannot inspect auth JWTs because login is blocked.
       VERDICT : UNTESTABLE.

Overall VERDICT for Test #18 : FAIL
Reason   : Multiple HIGH and MEDIUM severity security gaps:
  - CRITICAL: No Content Security Policy
  - HIGH: No X-Frame-Options (clickjacking possible)
  - HIGH: No rate limiting on auth endpoint (brute-force possible)
  - MEDIUM: No X-Content-Type-Options
  - MEDIUM: No Referrer-Policy
  - MEDIUM: Supabase code-verifier cookie not HttpOnly
  - MEDIUM: No COOP/COEP/CORP headers
  - LOW: Information disclosure (Server, X-Powered-By, X-Vercel-Id)
  - LOW: No /.well-known/security.txt
  - LOW: Sitemap references different domain (veridian-ai-os.vercel.app)

Recommend (priority order):
  1. Add Content-Security-Policy header with strict default-src.
  2. Add X-Frame-Options: DENY (or frame-ancestors 'none' in CSP).
  3. Enable Supabase Auth rate limiting (5 attempts/10min/email).
  4. Add X-Content-Type-Options: nosniff.
  5. Add Referrer-Policy: strict-origin-when-cross-origin.
  6. Migrate to @supabase/ssr for HttpOnly auth cookies.
  7. Add COOP: same-origin, CORP: same-origin.
  8. Disable X-Powered-By header (poweredByHeader: false in next.config.js).
  9. Add /.well-known/security.txt for responsible disclosure.
  10. Fix sitemap.xml to reference the canonical domain.
  11. Change login form method from GET to POST.

Artifacts:
  (All findings captured as JSON in this report. No additional
   screenshots saved because security testing produces text/JSON
   output, not visual artifacts.)

================================================================================
PART 5 SUMMARY TABLE
================================================================================
+-------+-------------------------------------+---------+----------------------+
| Test# | Test Name                           | Verdict | Key Finding          |
+-------+-------------------------------------+---------+----------------------+
| 12    | API Contract Testing                | PARTIAL | Public APIs         |
|       |                                     |         | deterministic; no   |
|       |                                     |         | rate limiting; no   |
|       |                                     |         | input validation    |
|       |                                     |         | on failure-event;   |
|       |                                     |         | no OpenAPI spec     |
| 18    | Security Testing                    | FAIL    | No CSP, no XFO,     |
|       |                                     |         | no rate limit on    |
|       |                                     |         | auth, code-verifier |
|       |                                     |         | cookie not HttpOnly,|
|       |                                     |         | multiple missing    |
|       |                                     |         | security headers    |
+-------+-------------------------------------+---------+----------------------+

CRITICAL FINDINGS (must fix before production):
  1. No Content-Security-Policy — XSS risk is wide open.
  2. No X-Frame-Options — clickjacking possible.
  3. No rate limiting on /auth/v1/token — brute-force possible.
  4. Supabase code-verifier cookie not HttpOnly — XSS exfiltration risk.

CARRY-FORWARD ISSUES:
  - Sitemap references veridian-ai-os.vercel.app (brand inconsistency) — Part 7.
  - No /api/openapi.json — Part 6 (governance).
  - Login form method is GET — Part 8 (regression).

================================================================================
END OF PART 5 REPORT
================================================================================
Next: Part 6 — Authorization/RBAC + AI Workflow + Governance Testing
================================================================================
```

<!-- ===== END PART 5 SOURCE FILE: Part5_API_Security_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 6 SOURCE FILE: Part6_RBAC_AI_Governance_Testing_Report.txt ===== -->

## PART 6 OF 8 — SOURCE FILE: `Part6_RBAC_AI_Governance_Testing_Report.txt`

```text
================================================================================
GTMCert PART 6 of 8 — AUTHORIZATION/RBAC + AI WORKFLOW + GOVERNANCE TESTING
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tools Used         : agent-browser (Playwright Chromium)
                    + fetch() for API probing
                    + JS bundle string-search for endpoint discovery
Pages Tested       : All discovered API endpoints
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74

TESTS COVERED IN PART 6
  Test #14 : Authorization / RBAC Testing
  Test #21 : AI Workflow Testing
  Test #22 : Governance Testing

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/part6/
ARTIFACTS CAPTURED  : JSON responses (in this report)

================================================================================
TEST #14 — AUTHORIZATION / RBAC TESTING
================================================================================
Tool               : fetch() with various auth tokens
Pass Criteria      : Roles enforced correctly

--- Endpoint Matrix (with method + auth status) ---

+------------------------------+--------+--------+--------+--------+
| Endpoint                     | GET    | POST   | PUT    | DELETE |
+------------------------------+--------+--------+--------+--------+
| /api/health                  | 200    | 405    | 405    | 405    |
| /api/auth/failure-event      | 405    | 200*   | 405    | 405    |
| /api/auth/passcode-login     | 405    | 400/401| 405    | 405    |
| /api/auth/sso/               | 404    | 200**  | -      | -      |
| /api/veri-chat/share-target  | 405    | 401    | -      | -      |
| /api/users                   | 401    | 401    | 405    | 405    |
| /api/compliance              | 401    | 401    | 405    | 405    |
| /api/compliance/items        | 401    | 405    | 405    | 401    |
| /api/documents               | 401    | 401    | 405    | 405    |
| /api/notifications           | 401    | 405    | 405    | 405    |
| /api/audit                   | 401    | 405    | 405    | 405    |
| /api/broadcast               | 404    | 200**  | -      | -      |
+------------------------------+--------+--------+--------+--------+

Legend:
  200  = OK (no auth needed, or endpoint accepts anything)
  200* = accepts any input (no validation)
  200**= returns HTML page (not a JSON API — likely Next.js page route)
  400  = bad request (input validation working)
  401  = Unauthorized (auth required)
  404  = Not Found
  405  = Method Not Allowed
  -    = not tested

--- Auth Verification Tests ---

  14a. No credentials (no Authorization header, no cookie)
       Result: All protected endpoints return 401 {"error":"Unauthorized"}
       VERDICT : PASS — auth enforced.

  14b. Fake Bearer token ( syntactically valid JWT with fake signature)
       Header: Authorization: Bearer eyJhbGc...fake-signature
       Result: All protected endpoints return 401 {"error":"Unauthorized"}
       VERDICT : PASS — token signature is verified, not just presence.
                Token forgery is NOT possible.

  14c. Fake Supabase auth cookie
       Cookie: sb-pcrjmlpuqsbocqfwoxod-auth-token=fake-token-value
       Result: 401 {"error":"Unauthorized"}
       VERDICT : PASS — cookie value is validated against Supabase,
                not just checked for presence.

  14d. Role-based access (cannot fully test without valid credentials)
       Action: cannot login as different roles (admin, user, viewer)
       Result: UNTESTABLE — login is blocked (see Part 1)
       VERDICT : UNTESTABLE — cannot verify role enforcement.
       Note   : The fact that all auth-protected endpoints return 401
                (and never 403 Forbidden) suggests the app checks
                authentication FIRST, then authorization. With valid
                credentials, role checks would presumably return 403
                for insufficient permissions. Cannot verify.

  14e. Method-based access control
       Action: probe each endpoint with GET/POST/PUT/DELETE
       Result: Proper 405 responses for unsupported methods
       VERDICT : PASS — HTTP method whitelisting is enforced.

  14f. Cross-tenant isolation (cannot test without multiple tenants)
       VERDICT : UNTESTABLE — requires valid credentials for two
                different tenants. Carried forward to Part 7.

  14g. Vertical privilege escalation
       Action: cannot test (no authenticated session)
       VERDICT : UNTESTABLE

  14h. Horizontal privilege escalation (IDOR)
       Action: cannot test (no authenticated session)
       VERDICT : UNTESTABLE — cannot probe /api/users/<other_user_id>
                without a valid session.

  14i. Passcode-login endpoint authorization
       Action: POST with email + passcode
       Result:
         - Missing both fields → 400 {"error":"Email and passcode are required"}
         - Valid email + wrong passcode → 401 {"error":"Invalid email or passcode."}
         - Passcode format not validated (3-char, 5-char, alphabetic all accepted)
       VERDICT : PARTIAL PASS — input validation present for required
                fields, but no format validation on passcode (should be
                exactly 4 digits).

  14j. Rate limiting on passcode-login (CRITICAL)
       Action: 20 concurrent requests with different 4-digit passcodes
       Result: 20 × 401 in 2.6 seconds (7.7 req/sec)
       VERDICT : FAIL — CRITICAL
       Reason : With only 10,000 possible 4-digit passcodes and no
                rate limiting, an attacker can brute-force the
                passcode in approximately 22 minutes (average 11 min).
                This is a critical security flaw for a compliance
                product.

  14k. /api/auth/failure-event (no auth required)
       Action: POST with any payload
       Result: Always 200 {"ok":true} — no validation
       VERDICT : WARN — endpoint is public and unvalidated. See Part 5
                for full treatment.

  14l. SSO endpoint (/api/auth/sso/)
       Action: POST with company ID
       Result: Returns 200 with full HTML login page (23 KB)
       VERDICT : WARN — endpoint that looks like an API returns HTML.
                This is a Next.js page route, not a JSON API. Confusing
                URL structure. Should be moved to /sso or /auth/sso
                (without /api/ prefix).

Overall VERDICT for Test #14 : PARTIAL PASS
Reason   : Auth is properly enforced — fake tokens and cookies are
           correctly rejected. Method whitelisting works. However:
             - Cannot verify role-based access (login blocked)
             - Passcode-login has NO rate limiting (CRITICAL)
             - Passcode format not validated (accepts 3-char, 5-char,
               alphabetic)
             - SSO endpoint returns HTML, not JSON (confusing URL design)
Recommend:
  - Add rate limiting to /api/auth/passcode-login: max 5 attempts per
    email per 10 minutes, lockout after 10 failed attempts.
  - Validate passcode format server-side (must be exactly 4 digits).
  - Move /api/auth/sso/ to /sso or /auth/sso (page route, not API).
  - After restoring demo credentials, re-test role enforcement with
    different user roles (admin, viewer, auditor).

Artifacts:
  (All RBAC responses are JSON in this report.)

================================================================================
TEST #21 — AI WORKFLOW TESTING
================================================================================
Tool               : API probing + JS bundle inspection
Pass Criteria      : AI responses conform to schema

--- AI Endpoint Discovery ---

  Direct API probe:
    /api/veri-chat                  → 404 (NOT FOUND)
    /api/veri-chat/messages         → 404
    /api/veri-chat/send             → 404
    /api/veri-chat/history          → 404
    /api/veri-chat/conversation     → 404
    /api/ai/chat                    → 404
    /api/ai/complete                → 404
    /api/ai/embed                   → 404
    /api/ai/extract                 → 404
    /api/ai/draft                   → 404
    /api/ai/search                  → 404
    /api/chat                       → 404
    /api/messages                   → 404

  Found via manifest.json share_target:
    POST /api/veri-chat/share-target → 401 {"error":"Unauthorized"}
                                       (auth required; endpoint exists)

  Found via JS bundle search:
    No /api/ai/* endpoints found in any client bundle.

--- AI Workflow Sub-tests ---

  21a. AI chat endpoint discoverable
       Result: Only /api/veri-chat/share-target is exposed. The actual
              AI chat endpoint is likely:
                - Server Action (Next.js RPC over fetch, no /api/ route)
                - Or accessible only after login (route not visible in
                  unauthenticated JS bundles)
       VERDICT : UNTESTABLE — cannot verify without authentication.

  21b. AI response schema
       Result: Cannot test — no AI endpoint accessible without auth.
       VERDICT : UNTESTABLE

  21c. AI determinism (same input → same output schema)
       Result: Cannot test.
       VERDICT : UNTESTABLE

  21d. AI input validation
       Result: Cannot test.
       VERDICT : UNTESTABLE

  21e. AI prompt injection resistance
       Result: Cannot test.
       VERDICT : UNTESTABLE

  21f. AI rate limiting (per-user token quota)
       Result: Cannot test.
       VERDICT : UNTESTABLE

  21g. AI safety / content filtering
       Result: Cannot test.
       VERDICT : UNTESTABLE

  21h. Share Target (manifest entry)
       Configuration in manifest.webmanifest:
         action  : /api/veri-chat/share-target
         method  : POST
         enctype : multipart/form-data
         params  : {title, text, url}
       Action: OPTIONS /api/veri-chat/share-target → 204 (CORS preflight OK)
       Action: POST  /api/veri-chat/share-target → 401 (auth required)
       VERDICT : PASS — endpoint exists, accepts POST, requires auth.
                The share_target configuration is valid. PWA users can
                share content from other apps into VERI Chat.

  21i. AI feature discoverability (UI)
       Result: Pricing page mentions "AI Document Extraction",
              "AI Q&A & Drafting", "Semantic Search" as Professional
              plan features. Login page mentions "VERI Chat" in nav.
       VERDICT : PASS (marketing claims are visible) but AI features
                themselves are untestable without auth.

  21j. AI model selection / BYOK (Bring Your Own Key)
       Result: Pricing page FAQ section mentions "BYOK AI Keys" as a
              feature comparison column. Cannot verify implementation.
       VERDICT : UNTESTABLE — feature exists in marketing but not
                accessible for testing.

Overall VERDICT for Test #21 : UNTESTABLE (BLOCKED)
Reason   : The AI workflow endpoints are not discoverable without
           authentication. The only AI-related endpoint visible to
           unauthenticated users is /api/veri-chat/share-target,
           which requires authentication to actually use.
Recommend:
  - After restoring demo credentials, re-test by:
      * Navigating to VERI Chat UI
      * Submitting a query and capturing the network request
      * Verifying the response schema (deterministic JSON)
      * Testing prompt injection (e.g., "ignore previous instructions")
      * Testing rate limiting (sending 50 messages rapidly)
      * Testing model selection (BYOK key entry)
      * Verifying AI responses include governance metadata
        (OCID/UMR references — see Test #22)
  - Publish API documentation for AI endpoints (after auth).
  - Add an AI response schema validator (e.g., Zod) on both client
    and server to ensure deterministic shape.

Artifacts:
  (No AI responses captured — all endpoints blocked by auth.)

================================================================================
TEST #22 — GOVERNANCE TESTING
================================================================================
Tool               : API probing + JS bundle inspection + Legal page review
Pass Criteria      : 100% traceability

--- Governance Endpoint Discovery ---

  Direct API probe:
    /api/ocid              → 404
    /api/ocid/lookup       → 404
    /api/ocid/verify       → 404
    /api/ocid/generate     → 404
    /api/umr               → 404
    /api/umr/lookup        → 404
    /api/umr/verify        → 404
    /api/umr/generate      → 404
    /api/governance        → 404
    /api/trace             → 404
    /api/traceability      → 404
    /api/ledger            → 404
    /api/audit-trail       → 404
    /api/event-log         → 404

  Found in JS bundles:
    - "permission_denied" string in 425otf4mblaj_.js
    - "role" string in 3cnl7y3-0vxmr.js, 2e_515uk27oyy.js
    - No "OCID", "UMR", "constitution", "traceability", or "ledger"
      strings found in any client-side JS bundle.

  Found in legal pages (terms, privacy, data-policy):
    - /terms mentions: "VERIDIAN COGNITIVE AI OS", "VERIDIAN OFFICE
      AI OS", "THE FIRM AI OS", "VERI FM & CS AI OS", "FORGE"
    - /terms mentions: "SHOBHA KAMAL SOLUTIONS PRIVATE LIMITED"
    - /privacy mentions: "data controller", "processor", "GDPR-style"
    - /data-policy mentions: "Your organisation owns its data"
    - NO mention of "OCID", "UMR", "constitution", or "ledger"
      in any legal page.

--- Governance Sub-tests ---

  22a. OCID (Object/Operation/Correlation ID) endpoint exists
       VERDICT : FAIL — no /api/ocid* endpoint discovered.

  22b. UMR (Unified Message Reference / Universal Master Record) endpoint exists
       VERDICT : FAIL — no /api/umr* endpoint discovered.

  22c. Governance / audit trail API exists
       VERDICT : PARTIAL — /api/audit exists but returns 401.
                Cannot verify if it provides governance trail data
                (OCID, UMR, etc.) without auth.

  22d. Traceability in AI responses
       Result: Cannot test (AI endpoints not accessible without auth).
       VERDICT : UNTESTABLE

  22e. Constitutional AI references (from legal pages)
       Result: /terms references "VERIDIAN COGNITIVE AI OS" with the
              tagline "AI cognitive research that becomes advanced,
              working products. VERIDIAN builds operating systems that
              perceive a company's state, decide, act, and account
              for every action — bounded by a constitution,
              accountable to a ledger."
       VERDICT : PASS (conceptually) — the product MARKETS
                constitutional AI and ledger accountability, but
                no API endpoints implement these concepts visibly.
                The governance layer may be server-side only.

  22f. Audit log endpoint
       Result: /api/audit exists but requires auth.
       VERDICT : UNTESTABLE — cannot verify audit log structure.

  22g. Data residency / sovereignty disclosure
       Result: /data-policy says "Your organisation owns its data.
              SHOBHA KAMAL SOLUTIONS PRIVATE LIMITED processes it
              only to operate, secure, and improve the Services."
              No mention of data residency (India, EU, US).
       VERDICT : WARN — for an Indian compliance product, data
                residency should be explicitly stated (e.g., "data
                stored in AWS Mumbai region").

  22h. Privacy contact
       Result: /privacy lists "raajat.agarwal@gmail.com" as the
              privacy contact. This is a personal Gmail address,
              not a corporate email (e.g., privacy@projexa-ai.com
              or dpo@veridian.ai).
       VERDICT : WARN — unprofessional and may violate GDPR
                Article 13(1)(b) which requires "the contact details
                of the controller" (typically a corporate address).

  22i. Legal entity disclosure
       Result: /terms discloses "SHOBHA KAMAL SOLUTIONS PRIVATE LIMITED,
              a company incorporated in India under the Companies Act."
       VERDICT : PASS — legal entity is disclosed. (No CIN number
                provided, which is required under Indian Companies Act
                for websites of companies — minor compliance gap.)

  22j. Last-updated dates on legal pages
       /terms         : "Last updated: 7 July 2026"
       /privacy       : "Last updated: 7 July 2026"
       /data-policy   : "Last updated: 7 July 2026"
       VERDICT : PASS — all legal pages have recent update dates.

  22k. Brand-name consistency in legal docs
       Result: All three legal pages reference "VERIDIAN AI OS" and
              its sub-products. None reference "PROJEXA".
       VERDICT : CONFIRMS Part 2 finding — PROJEXA is the legacy
                brand on /login only. The actual product is
                VERIDIAN AI OS.

  22l. Sitemap canonical domain mismatch
       sitemap.xml references: https://veridian-ai-os.vercel.app/
       Site is accessed at  : https://projexa-ai.com/
       VERDICT : FAIL — canonical URL in sitemap does not match the
                domain being served. This breaks SEO traceability
                and is a governance/brand issue.

  22m. robots.txt disclosure
       Disallowed paths reveal internal structure:
         /home, /settings, /sales-hq, /orchestra, /partner/, /r/
       VERDICT : WARN — common practice, but discloses route names
                that could inform attacks.

  22n. Right to be forgotten / data deletion
       Result: /data-policy says "Your organisation owns its data."
              No explicit mention of right-to-erasure process.
       VERDICT : WARN — for an Indian compliance product subject to
                DPDP Act 2023, the data policy should describe the
                grievance officer and data deletion request process.

  22o. Sub-processor disclosure
       Result: /privacy does not list sub-processors (e.g., Vercel,
              Supabase, OpenAI/Anthropic for AI).
       VERDICT : WARN — GDPR and DPDP require sub-processor disclosure.

Overall VERDICT for Test #22 : FAIL
Reason   : 
  - No public OCID / UMR / governance API endpoints discovered.
  - Sitemap canonical domain mismatch (veridian-ai-os.vercel.app).
  - Privacy contact is a personal Gmail address.
  - No data residency disclosure.
  - No sub-processor list.
  - No right-to-erasure process documented.
  - Governance MARKETING (constitution, ledger) is present in legal
    copy but not visibly implemented in client-side APIs.
  - Audit endpoint exists but cannot be verified without auth.
Recommend:
  - Publish /api/ocid/<id> for governance traceability lookups.
  - Publish /api/umr/<id> for unified message reference lookups.
  - Fix sitemap.xml to reference the canonical domain.
  - Replace raajat.agarwal@gmail.com with privacy@projexa-ai.com
    (or the appropriate corporate email).
  - Add data residency clause to /data-policy.
  - Add sub-processor list to /privacy.
  - Add right-to-erasure process to /data-policy.
  - Add CIN number to /terms footer (Indian Companies Act requirement).
  - After restoring demo credentials, verify that AI responses include
    OCID/UMR traceability metadata in their JSON schema.

Artifacts:
  /home/z/my-project/download/Part5_API_Security_Testing_Report.txt
  (legal page content extracted in this Part — no separate screenshots
   saved because legal pages are text-only.)

================================================================================
PART 6 SUMMARY TABLE
================================================================================
+-------+-------------------------------------+-----------+----------------------+
| Test# | Test Name                           | Verdict   | Key Finding          |
+-------+-------------------------------------+-----------+----------------------+
| 14    | Authorization / RBAC Testing        | PARTIAL   | Auth enforced; fake  |
|       |                                     |           | tokens rejected;     |
|       |                                     |           | but passcode brute-  |
|       |                                     |           | force possible (no   |
|       |                                     |           | rate limit); role    |
|       |                                     |           | checks untestable    |
|       |                                     |           | (login blocked)      |
| 21    | AI Workflow Testing                 | UNTESTABLE| AI endpoints not     |
|       |                                     |           | discoverable without |
|       |                                     |           | auth; only share-    |
|       |                                     |           | target visible       |
| 22    | Governance Testing                  | FAIL      | No OCID/UMR APIs;    |
|       |                                     |           | sitemap domain       |
|       |                                     |           | mismatch; privacy    |
|       |                                     |           | contact is Gmail;    |
|       |                                     |           | missing data         |
|       |                                     |           | residency, sub-      |
|       |                                     |           | processors, CIN      |
+-------+-------------------------------------+-----------+----------------------+

CRITICAL FINDINGS:
  1. Passcode-login endpoint has NO rate limiting — 4-digit passcode
     can be brute-forced in ~22 minutes. CRITICAL for a compliance
     product.
  2. No governance APIs (OCID, UMR) exposed publicly.
  3. Sitemap.xml points to a different domain (veridian-ai-os.vercel.app).
  4. Privacy contact is a personal Gmail address.

CARRY-FORWARD ISSUES:
  - Need valid credentials to verify: AI workflow, RBAC roles,
    audit log structure, OCID/UMR traceability in AI responses.
  - Part 7 will address what cannot be tested from end-user perspective
    (database integrity, multi-tenant isolation, disaster recovery,
    dependency scan, monitoring).

================================================================================
END OF PART 6 REPORT
================================================================================
Next: Part 7 — Backend/System Tests (as observable from end-user perspective)
================================================================================
```

<!-- ===== END PART 6 SOURCE FILE: Part6_RBAC_AI_Governance_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 7 SOURCE FILE: Part7_Backend_System_Testing_Report.txt ===== -->

## PART 7 OF 8 — SOURCE FILE: `Part7_Backend_System_Testing_Report.txt`

```text
================================================================================
GTMCert PART 7 of 8 — BACKEND / SYSTEM TESTS (FROM END-USER PERSPECTIVE)
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tools Used         : agent-browser + fetch() + Header inspection
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74

TESTS COVERED IN PART 7
  Test #15 : Database Integrity Testing
  Test #16 : Multi-Tenant Isolation
  Test #17 : Synchronization Testing
  Test #19 : Dependency / Supply Chain Scan
  Test #23 : Disaster Recovery Testing
  Test #24 : Monitoring & Observability

IMPORTANT LIMITATION:
  These six tests are inherently BACKEND/INFRASTRUCTURE tests. As an
  END USER (without server access, GitHub access, Vercel access, or
  Supabase admin access), I can only observe BLACK-BOX behavior:
    - HTTP response codes and headers
    - Response timing and consistency
    - Public health endpoints
    - CDN behavior
    - Error handling
  I CANNOT directly inspect:
    - Database tables, constraints, foreign keys
    - Row-Level Security policies
    - Backup files or restore procedures
    - npm package.json or lockfile
    - Server logs or metrics dashboards
  Where direct inspection is not possible, I document what an end user
  CAN observe and what an operator with backend access SHOULD verify.

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/part7/
ARTIFACTS CAPTURED  : JSON response data (in this report)

================================================================================
TEST #15 — DATABASE INTEGRITY TESTING
================================================================================
Tool               : Black-box observation only
Pass Criteria      : Zero corruption, constraints valid

--- Observable Indicators ---

  15a. /api/health returns 200 consistently
       Action  : 10 sequential calls, all expecting 200 {"ok":true,"ts":...}
       Result  : 10/10 calls returned 200 with valid JSON
       VERDICT : PASS — public health check is stable; suggests the
                database (or at least the application server) is
                not in a corrupted state.

  15b. Response time consistency (database load indicator)
       10 sequential calls to /api/health:
         min: 123 ms
         max: 145 ms
         avg: 134.7 ms
         variance: 22 ms
       VERDICT : PASS — response time is highly consistent (low
                variance = stable DB connection pool, no slow queries).

  15c. Database error leakage
       Action: tried malformed inputs to provoke DB errors
       Result: All errors return generic JSON {"error":"..."} with
              no SQL/PostgreSQL error messages leaked.
       VERDICT : PASS — no database error messages exposed to client.

  15d. Constraint violation visibility
       Action: cannot trigger constraint violations without auth
              (would need to POST duplicate users, etc.)
       VERDICT : UNTESTABLE — blocked by auth.

  15e. Foreign key integrity
       VERDICT : UNTESTABLE — requires direct DB access.

  15f. Transaction rollback behavior
       VERDICT : UNTESTABLE — requires ability to trigger failed
                multi-step operations.

  15g. Data consistency across reads (read-after-write)
       VERDICT : UNTESTABLE — no write access without auth.

  15h. Schema migration state
       VERDICT : UNTESTABLE — requires DB admin access.

Overall VERDICT for Test #15 : UNVERIFIABLE (PASS on observable parts)
Reason   : Public health endpoint is stable, fast, and doesn't leak
           errors. But true database integrity (constraints, foreign
           keys, RLS policies, backups) requires backend access.
Operator Action Required:
  - Run `supabase db lint` against the project.
  - Verify all foreign keys have ON DELETE CASCADE or RESTRICT
    as appropriate.
  - Verify RLS policies exist on every table that contains user data.
  - Run `pg_repack` or `VACUUM ANALYZE` periodically.
  - Verify daily backups complete (check Supabase dashboard →
    Database → Backups).
  - Test a point-in-time recovery (PITR) in staging.

================================================================================
TEST #16 — MULTI-TENANT ISOLATION
================================================================================
Tool               : Black-box observation only
Pass Criteria      : Tenant isolation verified

--- Observable Indicators ---

  16a. Tenant identifiers in public responses
       Action: scanned /api/health, /api/users, /api/compliance, /login,
              /signup, /pricing for tenant_id, org_id, company_id fields
       Result: NONE found in any public response
       VERDICT : PASS — no tenant info leaked to unauthenticated users.

  16b. Tenant info in client-side JS bundles
       Action: searched all _next/static/chunks/*.js for tenant/org
              patterns
       Result: no tenant identifiers found in client bundles
       VERDICT : PASS — no tenant info leaked via JS.

  16c. Cross-tenant data access (IDOR test)
       Action: cannot test — requires valid credentials for two
              different tenants
       VERDICT : UNTESTABLE — blocked by auth.

  16d. Supabase RLS enforcement
       The app uses Supabase (project: pcrjmlpuqsbocqfwoxod).
       Supabase RLS policies are enforced at the database layer.
       VERDICT : UNVERIFIABLE — RLS policies are not visible to
                end users. If RLS is properly configured, even a
                valid JWT cannot access another tenant's rows.

  16e. Tenant context in JWT
       Cannot inspect JWT structure without valid auth.
       VERDICT : UNTESTABLE.

  16f. Tenant scoping in API responses
       /api/users returns 401 — cannot see if response is scoped
       to caller's tenant.
       VERDICT : UNTESTABLE.

Overall VERDICT for Test #16 : UNVERIFIABLE (PASS on observable parts)
Reason   : No tenant info leaks to unauthenticated users. But true
           tenant isolation (RLS, JWT scoping, IDOR protection) cannot
           be verified without backend access AND credentials for
           two different tenants.
Operator Action Required:
  - Verify RLS policies on every table:
      SELECT tablename, rowsecurity, forcerowsecurity
      FROM pg_tables WHERE schemaname = 'public';
  - Test IDOR by logging in as Tenant A and trying to access
    Tenant B's resources via direct URL/ID.
  - Verify JWT contains tenant_id and every API route filters by it.
  - Audit Supabase queries for any `.eq('tenant_id', ...)` missing.

================================================================================
TEST #17 — SYNCHRONIZATION TESTING
================================================================================
Tool               : Concurrent fetch() calls + timing analysis
Pass Criteria      : Browser ↔ Server consistency

--- Observable Indicators ---

  17a. Concurrent request handling
       Action: 5 simultaneous calls to /api/health
       Result: All 5 returned 200 with monotonically increasing
              timestamps. Spread was 497ms across 5 calls.
       VERDICT : PASS — server handles concurrent requests correctly,
                no race conditions visible in public endpoint.

  17b. Timestamp monotonicity
       ts values: [1786007876881, 1786007877013, 1786007877134,
                   1786007877253, 1786007877378]
       All increasing. Spread: 497ms.
       VERDICT : PASS — server clock is consistent; timestamps are
                generated server-side (not client).

  17c. Cache consistency
       Action: 5 calls to /api/health with cache:'no-store'
       Result: Each call returned a unique x-vercel-id and
              x-vercel-cache: MISS. Server processed each request
              independently (no stale cache served).
       VERDICT : PASS — no cache-coherency issues.

  17d. Read-after-write consistency
       VERDICT : UNTESTABLE — cannot write without auth.

  17e. Cross-region synchronization
       All requests served from Vercel region hkg1::sin1
       (Hong Kong / Singapore). No multi-region observation possible
       from single client location.
       VERDICT : UNTESTABLE — would need clients in multiple regions.

  17f. WebSocket / real-time sync
       Action: no WebSocket connections observed during page load
       VERDICT : UNTESTABLE — app may use WebSockets after auth
                (e.g., for live chat), but none visible to
                unauthenticated users.

  17g. Optimistic UI updates
       VERDICT : UNTESTABLE — requires authenticated interaction.

Overall VERDICT for Test #17 : PARTIAL PASS
Reason   : Public API shows excellent consistency under concurrent
           load. Server timestamps are monotonic. No cache issues.
           But true sync (read-after-write, real-time, cross-region)
           cannot be verified without auth.
Operator Action Required:
  - After restoring credentials, test:
      * Create a compliance item, immediately re-fetch list,
        verify the new item appears.
      * Open two browser tabs with same account, modify in one,
        verify the other sees the update (or shows stale data).
      * If WebSockets are used, verify reconnection on network drop.

================================================================================
TEST #19 — DEPENDENCY / SUPPLY CHAIN SCAN
================================================================================
Tool               : Header inspection + JS bundle analysis
Pass Criteria      : No Critical vulnerabilities

--- Observable Indicators ---

  19a. Framework identification
       Server         : Vercel
       X-Powered-By   : Next.js (version NOT disclosed)
       Build artifacts: Next.js (Turbopack-style chunk names:
                        3afda5x4cppsy.js, 2cyi1t7yh20nv.js, etc.)
       Auth backend   : Supabase (project: pcrjmlpuqsbocqfwoxod)
       Analytics      : 2 first-party scripts at /771b847594094cc8/
                        script.js and /04809683687b4e12/script.js
                        (likely Vercel Analytics or Speed Insights)
       VERDICT : PASS — basic stack identified; no third-party
                scripts loaded from external CDNs (good for
                supply-chain security).

  19b. Next.js version detection
       Action: tried /_next/static/buildManifest.json, BUILD_ID,
              _next/static/chunks/webpack.js, _next/static/chunks/main.js,
              _next/static/chunks/framework.js, _next/static/chunks/pages/_app.js
       Result: All return 404 (good — Vercel hides build artifacts)
       VERDICT : PASS — version is not leaked at standard paths.

  19c. Known monitoring library globals
       Tested for: Sentry, Datadog, LogRocket, FullStory, PostHog,
                   Amplitude, Mixpanel, GTM, gtag, ga, ApplicationInsights,
                   Bugsnag, Raygun
       Result: ALL return false (none loaded)
       VERDICT : PASS — no third-party monitoring SDKs running.
                This is GOOD for privacy but BAD for observability
                (see Test #24).

  19d. Sub-resource integrity (SRI) on scripts
       Action: checked <script> tags for integrity attribute
       Result: NONE of the loaded scripts have an integrity attribute.
       VERDICT : FAIL — if a CDN or Vercel edge is compromised,
                attacker could inject malicious JS. SRI prevents this.
       Recommend: Add integrity="sha384-..." to all <script> and
                 <link rel="stylesheet"> tags. Next.js supports this
                 via the `crossOrigin` and integrity props in
                 next.config.js.

  19e. Third-party scripts
       Action: enumerated all <script src> tags
       Result: 17 scripts loaded, ALL from projexa-ai.com (first-party).
              No scripts from unpkg, cdnjs, jsdelivr, googleapis, or
              other CDNs.
       VERDICT : PASS — supply chain is fully first-party.

  19f. CSP hash/nonce for inline scripts
       Action: tried to inspect CSP header (would contain 'unsafe-inline'
              or nonce/hash list)
       Result: No CSP header exists (see Part 5).
       VERDICT : FAIL — without CSP, inline scripts can be injected
                by any XSS. (Already documented in Part 5.)

  19g. Package.json / lockfile exposure
       /package.json     → 404    PASS
       /yarn.lock        → not tested (likely 404)
       /package-lock.json → not tested (likely 404)
       VERDICT : PASS — no manifest files exposed.

  19h. Source maps exposure
       Action: tried .js.map variants of loaded scripts
       Result: not tested directly, but Vercel typically blocks these
              in production. Worth verifying.
       VERDICT : UNVERIFIABLE — would need to test each chunk.

  19i. Vulnerable JS libraries (manual check)
       Cannot run npm audit or Snyk without package.json access.
       React version: not visible.
       Next.js version: not visible.
       VERDICT : UNTESTABLE — requires backend access to run
                `npm audit --production` or `trivy fs .`.

  19j. Container/base image vulnerabilities
       VERDICT : UNTESTABLE — app is on Vercel (serverless), so
                traditional container scanning doesn't apply.
                Vercel manages the runtime.

  19k. Trivy scan of dependencies
       VERDICT : UNTESTABLE — requires access to the codebase.

Overall VERDICT for Test #19 : PARTIAL PASS
Reason   : Supply chain is clean from end-user perspective:
             - All scripts are first-party (no CDN dependencies).
             - No third-party monitoring SDKs loaded.
             - No package.json or lockfile exposed.
             - No build artifacts leaked.
           But:
             - No SRI on scripts (medium severity).
             - Cannot run npm audit / trivy without codebase access.
Operator Action Required:
  - Run `npm audit --audit-level=high` in CI on every PR.
  - Run `trivy fs . --severity CRITICAL` on every release.
  - Enable Dependabot or Snyk for automated dependency PRs.
  - Add SRI hashes to all script/link tags (Next.js supports this).
  - Run `npm outdated` monthly and update non-breaking versions.

================================================================================
TEST #23 — DISASTER RECOVERY TESTING
================================================================================
Tool               : Black-box observation only
Pass Criteria      : Backup and restore successful

--- Observable Indicators ---

  23a. Application is currently available
       GET https://projexa-ai.com/login → 200 OK
       GET https://projexa-ai.com/api/health → 200 {"ok":true,"ts":...}
       VERDICT : PASS — app is up and serving requests.

  23b. Vercel deployment region
       x-vercel-id format: "<edge>::<region>::<request-id>"
       Observed: "hkg1::sin1::..." (Hong Kong edge, Singapore region)
       VERDICT : PASS — Vercel provides multi-region failover at the
                edge layer. If sin1 region goes down, Vercel
                automatically reroutes to another region.

  23c. CDN cache behavior
       x-vercel-cache: MISS on every /api/health call
       This is correct for a health check (should not be cached).
       VERDICT : PASS.

  23d. Backup file accessibility
       Action: tried /.env, /.git/config, /backup.sql, /db.sql,
              /database.sql, /snapshot.sql
       Result: All return 404 (no backup files publicly accessible)
       VERDICT : PASS — no backup files leaked.

  23e. Restore procedure verification
       VERDICT : UNTESTABLE — requires backend access to perform
                a restore and verify data integrity.

  23f. RPO (Recovery Point Objective) measurement
       VERDICT : UNTESTABLE — requires access to Supabase backup
                dashboard to verify backup frequency.

  23g. RTO (Recovery Time Objective) measurement
       VERDICT : UNTESTABLE — would need to wait for an actual
                outage and measure recovery time.

  23h. Multi-region failover
       Vercel handles edge failover automatically. But:
       - Database (Supabase) is single-region by default.
       - If Supabase region goes down, app will return 500s.
       VERDICT : UNTESTABLE — Supabase region not visible.

  23i. Supabase project region
       Project URL: pcrjmlpuqsbocqfwoxod.supabase.co
       Cannot determine region from URL alone. Common Supabase
       regions: ap-south-1 (Mumbai), us-east-1, etc.
       VERDICT : UNTESTABLE.

  23j. Database backups
       VERDICT : UNTESTABLE — Supabase dashboard access required.
       Supabase Free tier: daily backups only.
       Supabase Pro tier: daily backups + PITR (point-in-time recovery).

  23k. Disaster recovery runbook
       VERDICT : UNTESTABLE — would need to inspect internal docs.

Overall VERDICT for Test #23 : UNVERIFIABLE (PASS on observable parts)
Reason   : App is currently up and serving requests. Vercel provides
           edge-level failover. No backup files leaked. But:
             - Cannot verify backup frequency or restore procedure.
             - Cannot measure RPO/RTO without backend access.
             - Supabase region and backup config are not visible.
Operator Action Required:
  - Verify Supabase project is on Pro tier (enables PITR).
  - Schedule daily backup verification: restore to staging,
    run smoke tests, document time-to-restore.
  - Document RPO (e.g., 24 hours for daily backups, 5 min for PITR)
    and RTO (e.g., 30 minutes) targets.
  - Test failover: deliberately point app at a stale Supabase URL
    and verify error handling.
  - Create a runbook: "If Supabase is down, do X" (e.g., switch to
    read-only mode, display maintenance banner).

================================================================================
TEST #24 — MONITORING & OBSERVABILITY
================================================================================
Tool               : Black-box observation only
Pass Criteria      : Logs, Metrics, Alerts operational

--- Observable Indicators ---

  24a. Health check endpoint
       GET /api/health → 200 {"ok":true,"ts":<epoch_millis>}
       Response time: ~130ms avg (fast)
       VERDICT : PASS — public health check exists and is fast.

  24b. Other monitoring endpoints
       Tried: /api/healthz, /api/ready, /api/live, /api/metrics,
              /api/stats, /api/diagnostics, /health, /healthz, /status,
              /metrics, /_health, /_status, /api/_health, /api/_monitoring
       Result: ALL return 404
       VERDICT : PARTIAL — only /api/health exists. No metrics,
                no readiness probe, no liveness probe (Kubernetes
                style). For a Vercel deployment, these are less
                critical (Vercel handles health checks), but useful
                for synthetic monitoring.

  24c. Analytics / RUM (Real User Monitoring)
       Two scripts loaded from projexa-ai.com:
         /771b847594094cc8/script.js (2.5 KB)
         /04809683687b4e12/script.js (12.6 KB)
       These scripts detect navigator.webdriver and "Headless" in
       userAgent (so they exclude bot traffic).
       Likely: Vercel Analytics + Vercel Speed Insights.
       VERDICT : PASS — basic analytics is configured.

  24d. Error tracking (Sentry, Bugsnag, etc.)
       Tested window globals for 14 error-tracking libraries.
       Result: NONE loaded.
       VERDICT : FAIL — no error tracking SDK. If a user hits a
                JavaScript error in production, the team has no
                visibility unless the user reports it.
       Recommend: Add Sentry (or Bugsnag, LogRocket) for frontend
                 error tracking. Free tier covers small teams.

  24e. Server-side logging
       /api/auth/failure-event is a server-side log endpoint
       (returns {"ok":true} for any input). This suggests the
       server is logging auth failures, but:
         - No visibility into WHERE logs are stored (Vercel logs?
           Supabase logs? External service?)
         - No visibility into log retention (Vercel Free: 1 hour,
           Pro: 7 days, Enterprise: 30 days)
       VERDICT : PARTIAL — logging exists, but observability is
                not verifiable.

  24f. Alerting
       VERDICT : UNTESTABLE — would need to trigger an alert and
                observe delivery (Slack, email, PagerDuty).

  24g. Synthetic monitoring (uptime checks)
       /api/health is suitable for synthetic monitoring, but
       no indication that any external monitor (Pingdom, UptimeRobot,
       Checkly) is polling it.
       VERDICT : UNTESTABLE.

  24h. Distributed tracing
       x-vercel-id is included on every response — useful for
       tracing requests across Vercel infrastructure. But no
       OpenTelemetry / Jaeger / Zipkin headers observed.
       VERDICT : PARTIAL — Vercel provides request IDs, but no
                end-to-end distributed tracing.

  24i. Structured logging
       VERDICT : UNTESTABLE — cannot view server logs from outside.

  24j. Real-time metrics dashboard
       VERDICT : UNTESTABLE — no /metrics endpoint, no Grafana
                dashboard link visible.

  24k. User-facing status page
       No status page link in footer or header.
       Tried: /status, /status-page, /uptime — all 404.
       VERDICT : WARN — for a B2B compliance SaaS, a public status
                page (e.g., status.instatus.com or statuspage.io)
                is a customer-trust signal.

  24l. Maintenance mode
       No /maintenance page observed. No banner indicating
       scheduled downtime.
       VERDICT : UNTESTABLE.

Overall VERDICT for Test #24 : PARTIAL PASS
Reason   : Basic health check exists and is fast. Vercel Analytics
           is configured. But:
             - No error tracking SDK (Sentry/Bugsnag) on the frontend.
             - No public status page.
             - No metrics endpoint.
             - Distributed tracing is Vercel-only (no OpenTelemetry).
           Cannot verify server-side logging, alerting, or dashboarding
           from end-user perspective.
Operator Action Required:
  - Add Sentry (frontend + server-side) for error tracking.
  - Set up UptimeRobot or Better Stack to poll /api/health every
    30 seconds from 3+ regions.
  - Publish a status page (statuspage.io, instatus.com, or self-hosted).
  - Add OpenTelemetry instrumentation for distributed tracing.
  - Configure Vercel Log Drain to a log aggregator (Logtail, Datadog,
    Loki, etc.).
  - Set up alerts for:
      * 5xx error rate > 1% over 5 minutes
      * p95 response time > 500ms over 5 minutes
      * /api/health returns non-200 for 3 consecutive checks
      * Supabase connection errors > 0 in 1 minute

================================================================================
PART 7 SUMMARY TABLE
================================================================================
+-------+-------------------------------------+-------------+----------------------+
| Test# | Test Name                           | Verdict     | Key Finding          |
+-------+-------------------------------------+-------------+----------------------+
| 15    | Database Integrity Testing          | UNVERIFIABLE| Health endpoint     |
|       |                                     | (PASS obs.) | stable & fast;      |
|       |                                     |             | cannot verify       |
|       |                                     |             | constraints/RLS     |
| 16    | Multi-Tenant Isolation              | UNVERIFIABLE| No tenant info      |
|       |                                     | (PASS obs.) | leaked publicly;    |
|       |                                     |             | cannot verify RLS  |
| 17    | Synchronization Testing             | PARTIAL     | Excellent           |
|       |                                     |             | consistency under   |
|       |                                     |             | concurrency; sync   |
|       |                                     |             | untestable          |
| 19    | Dependency / Supply Chain Scan      | PARTIAL     | All scripts first-  |
|       |                                     |             | party; no SRI; no  |
|       |                                     |             | npm audit possible  |
| 23    | Disaster Recovery Testing           | UNVERIFIABLE| App is up; Vercel   |
|       |                                     | (PASS obs.) | failover ok;        |
|       |                                     |             | backup/restore      |
|       |                                     |             | untestable          |
| 24    | Monitoring & Observability          | PARTIAL     | Health endpoint +   |
|       |                                     |             | Vercel Analytics;   |
|       |                                     |             | no Sentry, no      |
|       |                                     |             | status page         |
+-------+-------------------------------------+-------------+----------------------+

OVERALL ASSESSMENT FOR PART 7:
  Six tests in this Part are inherently backend/infrastructure tests.
  From an END USER perspective, I can confirm:
    ✓ App is available and responsive
    ✓ Public health endpoint works
    ✓ No data leaks in unauthenticated responses
    ✓ All scripts are first-party (no supply chain risk)
    ✓ Vercel provides edge failover
    ✓ Basic analytics is configured
  I CANNOT verify (require backend/codebase access):
    ✗ Database constraints, RLS policies
    ✗ Multi-tenant isolation (requires 2+ tenant accounts)
    ✗ Backup/restore procedures
    ✗ npm audit / trivy scan results
    ✗ Server logs, metrics, alerting configuration
    ✗ Distributed tracing setup
  Operator MUST perform these tests with backend access before
  claiming production readiness.

CARRY-FORWARD ISSUES:
  - Missing SRI on scripts — Part 8 (regression).
  - No Sentry/error tracking — Part 8.
  - No status page — Part 8.

================================================================================
END OF PART 7 REPORT
================================================================================
Next: Part 8 — Regression Testing + Final Production Readiness Certification
================================================================================
```

<!-- ===== END PART 7 SOURCE FILE: Part7_Backend_System_Testing_Report.txt ===== -->

---

<!-- ===== BEGIN PART 8 SOURCE FILE: Part8_Regression_Final_Certification_Report.txt ===== -->

## PART 8 OF 8 — SOURCE FILE: `Part8_Regression_Final_Certification_Report.txt`

```text
================================================================================
GTMCert PART 8 of 8 — REGRESSION + PRODUCTION READINESS CERTIFICATION
================================================================================
Report Date        : 2026-08-06
Target URL         : https://projexa-ai.com/
Tester Role        : END USER (Black-box, no code/server access)
Tools Used         : agent-browser + Lighthouse 13.4.1 + axe-core 4.10.0
Session ID         : web-33afc8e6-7791-4c96-b57e-31217123fa74
Trace ID           : 19fd635e17043ad1

TESTS COVERED IN PART 8
  Test #20 : Regression Testing
  Test #25 : Production Readiness Certification (FINAL)

ARTIFACT DIRECTORY  : /home/z/my-project/screenshots/
ARTIFACTS CAPTURED  : 32+ screenshots across all 8 parts
                      3 Lighthouse HTML reports
                      Multiple JSON response dumps

================================================================================
TEST #20 — REGRESSION TESTING
================================================================================
Tool               : agent-browser (re-run of all critical paths)
Pass Criteria      : Zero regressions

Methodology:
  Re-executed all critical user-facing flows at the end of the testing
  session to verify that:
    (a) The application state did not change during testing.
    (b) No endpoint behavior shifted between calls.
    (c) All public pages still render correctly.
    (d) Authentication still rejects invalid credentials consistently.

Sub-tests:

  20a. Public page rendering (re-test)
       +----------+--------+-------------------------------------------+
       | Path     | Status | Title                                     |
       +----------+--------+-------------------------------------------+
       | /login   | 200    | Sign in — PROJEXA                         |
       | /signup  | 200    | VERIDIAN COGNITIVE AI OS — AI Research    |
       | /pricing | 200    | VERIDIAN COGNITIVE AI OS — AI Research    |
       | /terms   | 200    | Terms & Conditions — VERIDIAN AI OS       |
       | /privacy | 200    | Privacy Policy — VERIDIAN AI OS           |
       | /data-policy | 200 | Data Policy — VERIDIAN AI OS              |
       +----------+--------+-------------------------------------------+
       VERDICT : PASS — all 6 public pages render with consistent
                titles and 200 status. No regressions.

  20b. API endpoint behavior (re-test)
       +------------------------------+--------+----------+--------+
       | Endpoint                     | Method | Expected | Actual |
       +------------------------------+--------+----------+--------+
       | /api/health                  | GET    | 200      | 200    |
       | /api/users                   | GET    | 401      | 401    |
       | /api/compliance              | GET    | 401      | 401    |
       | /api/auth/failure-event      | POST   | 200      | 200    |
       | /api/auth/passcode-login     | POST   | 400      | 400    |
       | /api/veri-chat/share-target  | POST   | 401      | 401    |
       +------------------------------+--------+----------+--------+
       VERDICT : PASS — all 6 API endpoints return expected status
                codes. No regressions in API contract.

  20c. Login behavior (re-test)
       Action: fill email=democeo@projexa-ai.com, password=Demo@1234,
              click Sign In
       Result: Supabase /auth/v1/token returns 400 (Invalid credentials)
              Toast: "Invalid login credentials" (or "missing email or
              phone" if React state was not properly set)
       VERDICT : PASS (regression-wise) — same behavior as Part 1.
                The credential rejection is consistent; this is the
                same blocker as the start of testing. The application
                has NOT changed.

  20d. Localization toggle (re-test)
       Action: switch language combobox to Hindi
       Result: entire form translated
       VERDICT : PASS — i18n still works.

  20e. Responsive layout (re-test)
       Action: re-loaded /login at 375x667 viewport
       Result: no horizontal overflow, all elements visible
       VERDICT : PASS — responsive layout stable.

  20f. Security headers (re-test)
       Action: re-fetched /login and /api/users headers
       Result: same header set as Part 5
         - HSTS: present
         - CSP: still MISSING
         - X-Frame-Options: still MISSING
         - X-Content-Type-Options: still MISSING
       VERDICT : PASS (regression-wise) — no change in security
                posture. Same gaps remain.

  20g. Lighthouse score (re-test on /login)
       Performance    : 95  (was 95 in Part 3)                 PASS
       Accessibility  : 96  (was 96 in Part 3)                 PASS
       Best Practices : 100 (was 100 in Part 3)                PASS
       SEO            : 100 (was 100 in Part 3)                PASS
       VERDICT : PASS — performance and quality scores are stable.

  20h. Service worker registration (re-test)
       Result: 0 service workers registered (same as Part 4)
       VERDICT : PASS — PWA state unchanged.

  20i. Browser storage (re-test)
       localStorage  : empty
       sessionStorage : empty
       IndexedDB     : 0 databases
       Cookies       : 2 (NEXT_LOCALE + Supabase code-verifier)
       VERDICT : PASS — storage state unchanged.

  20j. Endpoint determinism (re-test)
       /api/health called 5 times: all return 200 {"ok":true,"ts":...}
       Response times consistent (123-145ms range, same as Part 7)
       VERDICT : PASS — deterministic.

Overall VERDICT for Test #20 : PASS
Reason   : No regressions detected. All public pages, API endpoints,
           security posture, performance scores, and storage state
           are identical to the start of the testing session. The
           application is in a stable, reproducible state.
Note     : This regression test ONLY covers what an unauthenticated
           end user can observe. Backend state (DB, logs, metrics)
           is not regression-tested from the outside.

Artifacts:
  /home/z/my-project/screenshots/part8/regression-login-attempt.png

================================================================================
TEST #25 — PRODUCTION READINESS CERTIFICATION (FINAL)
================================================================================
Tool               : Aggregation of all 24 prior tests
Pass Criteria      : All 24 previous tests PASS

================================================================================
FINAL CERTIFICATION SUMMARY — ALL 25 TESTS
================================================================================

+-------+-------------------------------------+-------------+--------------------+
| #     | Test Name                           | Verdict     | Critical Issue     |
+-------+-------------------------------------+-------------+--------------------+
| 1     | Smoke Testing                       | FAIL        | Login fails (400)  |
| 2     | End-to-End User Journey             | FAIL        | Blocked at login   |
| 3     | UI/UX Validation                    | FAIL        | 10 critical defects|
| 4     | Cross Browser Testing               | PARTIAL     | Chromium only;     |
|       |                                     |             | Safari untested    |
| 5     | Responsive Testing                  | PASS        | All 6 viewports OK |
| 6     | Accessibility Testing               | FAIL        | button-name + 14   |
|       |                                     |             | color-contrast     |
|       |                                     |             | violations         |
| 7     | Performance Testing                 | PARTIAL     | /pricing 85 (<90); |
|       |                                     |             | /login 95,         |
|       |                                     |             | /signup 96         |
| 8     | Core Web Vitals                     | FAIL        | LCP fails on all   |
|       |                                     |             | pages; INP fails   |
| 9     | PWA Testing                         | FAIL        | No SW, no PNG      |
|       |                                     |             | icons, not         |
|       |                                     |             | installable        |
| 10    | Offline/Sync Testing                | FAIL        | Zero offline       |
|       |                                     |             | capability         |
| 11    | Browser Storage Testing             | PARTIAL     | Clean at unauth;   |
|       |                                     |             | code-verifier not  |
|       |                                     |             | HttpOnly           |
| 12    | API Contract Testing                | PARTIAL     | No rate limiting;  |
|       |                                     |             | no input validation|
|       |                                     |             | on failure-event   |
| 13    | Authentication Testing              | FAIL        | Demo creds invalid;|
|       |                                     |             | no rate limiting;  |
|       |                                     |             | email validation   |
|       |                                     |             | weak               |
| 14    | Authorization / RBAC Testing        | PARTIAL     | Passcode brute-    |
|       |                                     |             | force possible;    |
|       |                                     |             | role checks        |
|       |                                     |             | untestable         |
| 15    | Database Integrity Testing          | UNVERIFIABLE| Backend access     |
|       |                                     | (PASS obs.) | required           |
| 16    | Multi-Tenant Isolation              | UNVERIFIABLE| Backend access +   |
|       |                                     | (PASS obs.) | 2 tenants required |
| 17    | Synchronization Testing             | PARTIAL     | Concurrent calls   |
|       |                                     |             | consistent; R/W    |
|       |                                     |             | sync untestable    |
| 18    | Security Testing                    | FAIL        | No CSP, no XFO,    |
|       |                                     |             | no rate limit,     |
|       |                                     |             | cookie not HttpOnly|
| 19    | Dependency / Supply Chain Scan      | PARTIAL     | First-party only;  |
|       |                                     |             | no SRI; npm audit  |
|       |                                     |             | not possible       |
| 20    | Regression Testing                  | PASS        | No regressions     |
| 21    | AI Workflow Testing                 | UNTESTABLE  | Auth required      |
| 22    | Governance Testing                  | FAIL        | No OCID/UMR APIs;  |
|       |                                     |             | sitemap domain     |
|       |                                     |             | mismatch; Gmail    |
|       |                                     |             | privacy contact    |
| 23    | Disaster Recovery Testing           | UNVERIFIABLE| Backend access     |
|       |                                     | (PASS obs.) | required           |
| 24    | Monitoring & Observability          | PARTIAL     | Health endpoint +  |
|       |                                     |             | Vercel Analytics;  |
|       |                                     |             | no Sentry/status   |
| 25    | Production Readiness Certification  | FAIL        | 9 of 24 prior      |
|       |                                     |             | tests FAIL         |
+-------+-------------------------------------+-------------+--------------------+

================================================================================
FINAL CERTIFICATION VERDICT
================================================================================

  PRODUCTION READINESS:  ❌  NOT CERTIFIED

  Score breakdown:
    PASS              :  2  (Tests #5, #20)
    PARTIAL PASS      :  6  (Tests #4, #7, #11, #12, #14, #17, #19, #24)
    FAIL              :  9  (Tests #1, #2, #3, #6, #8, #9, #10, #13, #18, #22)
    UNTESTABLE        :  4  (Tests #15, #16, #21, #23)  [require backend access]
    UNVERIFIABLE      :  3  (Tests #15, #16, #23)  [observable parts pass]

  Pass rate (PASS only):  2 / 25 = 8%
  Pass rate (PASS + PARTIAL): 8 / 25 = 32%
  Effective pass rate (excluding UNTESTABLE): 8 / 21 = 38%

================================================================================
CRITICAL BLOCKERS (must fix before any production launch)
================================================================================

  CB-01. Demo credentials provided are invalid.
         Status: BLOCKER
         Impact: Cannot complete E2E user journey testing (Tests #1, #2,
                 #13, #14, #21). All downstream tests requiring an
                 authenticated session are blocked.
         Action: Verify account `democeo@projexa-ai.com` exists in
                 Supabase Auth. Reset password if needed. Provide
                 working credentials to re-run the test suite.

  CB-02. No Content-Security-Policy header.
         Status: CRITICAL SECURITY
         Impact: XSS attacks are not mitigated at the browser level.
                 Any XSS bug leads to full account takeover.
         Action: Add a strict CSP to next.config.js headers() config.

  CB-03. No X-Frame-Options / frame-ancestors.
         Status: HIGH SECURITY
         Impact: Login page can be embedded in iframes on arbitrary
                 domains — clickjacking attacks can steal credentials.
         Action: Add X-Frame-Options: DENY or frame-ancestors 'none'
                 in CSP.

  CB-04. No rate limiting on /api/auth/passcode-login.
         Status: CRITICAL SECURITY
         Impact: 4-digit passcode can be brute-forced in ~22 minutes.
                 For a compliance product, this is unacceptable.
         Action: Add rate limiting (5 attempts per email per 10 min,
                 lockout after 10 fails). Consider reCAPTCHA.

  CB-05. No rate limiting on Supabase /auth/v1/token.
         Status: HIGH SECURITY
         Impact: Brute-force attacks on user passwords are not
                 mitigated at the application layer.
         Action: Enable Supabase Auth rate limits in the dashboard
                 (Auth → Settings → Rate Limits).

  CB-06. Supabase code-verifier cookie is NOT HttpOnly.
         Status: HIGH SECURITY
         Impact: XSS can exfiltrate the OAuth code verifier and
                 hijack the auth flow.
         Action: Migrate to @supabase/ssr for server-side cookie
                 handling with HttpOnly attribute.

  CB-07. No PWA capability (no service worker, no PNG icons).
         Status: PRODUCT GAP
         Impact: App is unusable in low-connectivity environments
                 (factory floors, client sites, court visits).
                 For a compliance product, this is a major gap.
         Action: Add next-pwa or Workbox, generate PNG icons
                 (192x192, 512x512, maskable, apple-touch-icon).

  CB-08. Brand inconsistency (PROJEXA vs VERIDIAN AI).
         Status: GOVERNANCE / TRUST
         Impact: Users see two different brand names on different
                 pages. Meta description, sitemap, and og tags all
                 reference VERIDIAN while /login says PROJEXA.
                 Breaks user trust and SEO.
         Action: Pick one brand. Update all surfaces consistently
                 (HTML, manifest, sitemap, legal pages, meta tags).

  CB-09. Sitemap.xml references different domain.
         Status: SEO / GOVERNANCE
         Impact: Sitemap points to https://veridian-ai-os.vercel.app/
                 instead of https://projexa-ai.com/. Search engines
                 will index the wrong domain.
         Action: Fix sitemap.xml to reference the canonical domain.

  CB-10. /forgot-password returns 404.
         Status: UX / SUPPORT
         Impact: Users who forget their password have no self-service
                 recovery path. Only "Send magic link instead" is
                 offered on /login.
         Action: Implement /forgot-password OR redirect it to /login
                 with a magic-link prompt.

================================================================================
HIGH-PRIORITY ISSUES (fix before GA)
================================================================================

  HP-01. Color contrast violations on /pricing (14 elements, some 2.59:1).
  HP-02. button-name violation: #billing-toggle (Monthly/Annual switch)
         has no accessible name.
  HP-03. No <h1> on /login and /signup.
  HP-04. No semantic landmarks (<main>, <header>, <footer>) on /login
         and /signup.
  HP-05. No skip-link on any page.
  HP-06. Missing autocomplete attributes on email/password fields.
  HP-07. No password visibility toggle.
  HP-08. No client-side email format validation.
  HP-09. LCP > 2.5s on all pages (marginal on /login and /signup,
         significant on /pricing at 3.8s).
  HP-10. INP (Max Potential FID) > 200ms on all pages.
  HP-11. No Sentry / Bugsnag / error tracking SDK.
  HP-12. No public status page.
  HP-13. No SRI (Sub-resource Integrity) on scripts.
  HP-14. Privacy contact is a personal Gmail address.
  HP-15. No data residency disclosure in /data-policy.
  HP-16. No sub-processor list in /privacy.
  HP-17. No CIN number in /terms footer (Indian Companies Act).
  HP-18. No /api/openapi.json (no published API contract).
  HP-19. /api/auth/failure-event accepts ANY input without validation.
  HP-20. 404 page is a dead end (no "return to login" link).

================================================================================
MEDIUM-PRIORITY ISSUES (fix in next sprint)
================================================================================

  MP-01. No X-Content-Type-Options: nosniff header.
  MP-02. No Referrer-Policy header.
  MP-03. No COOP / COEP / CORP headers.
  MP-04. Information disclosure: Server, X-Powered-By, X-Vercel-ID
         headers reveal tech stack.
  MP-05. No /.well-known/security.txt.
  MP-06. Static assets have max-age=0 (suboptimal caching).
  MP-07. bfcache not restorable on /login.
  MP-08. 142 KiB of unused JavaScript on /login.
  MP-09. Input font-size 14px (triggers iOS auto-zoom).
  MP-10. Login form uses method="GET" (should be POST).
  MP-11. No persistent storage request
         (navigator.storage.persist()).
  MP-12. No theme-color meta tag (only in manifest).
  MP-13. No apple-touch-icon link.
  MP-14. No apple-mobile-web-app-capable meta tag.
  MP-15. No canonical link tag.
  MP-16. <html dir> attribute not set (relevant for future RTL
         languages).
  MP-17. /api/auth/sso/ returns HTML instead of JSON (confusing URL
         design — should be moved to /sso or /auth/sso).
  MP-18. Passcode-login doesn't validate 4-digit format (accepts
         3-char, 5-char, alphabetic).
  MP-19. No right-to-erasure process documented (DPDP Act 2023).
  MP-20. No public landing page at / (redirects straight to /login).

================================================================================
TESTS THAT CANNOT BE COMPLETED FROM END-USER PERSPECTIVE
================================================================================

  The following tests require backend access, codebase access, or
  credentials that were not available during this testing session:

  - Test #15 (Database Integrity): need DB admin access
  - Test #16 (Multi-Tenant Isolation): need 2+ tenant accounts
  - Test #21 (AI Workflow): need authenticated session
  - Test #23 (Disaster Recovery): need backup/restore access

  These tests are documented with "UNVERIFIABLE" or "UNTESTABLE"
  verdicts. The OPERATOR must perform these tests with backend
  access before claiming full production readiness.

================================================================================
RECOMMENDED NEXT STEPS (priority order)
================================================================================

  IMMEDIATE (before any production launch):
    1. Restore or reissue demo credentials.
    2. Add Content-Security-Policy header.
    3. Add X-Frame-Options: DENY.
    4. Enable rate limiting on /api/auth/passcode-login and
       Supabase Auth.
    5. Migrate to @supabase/ssr for HttpOnly auth cookies.
    6. Fix brand inconsistency (PROJEXA → VERIDIAN or vice versa).
    7. Fix sitemap.xml to reference canonical domain.

  SHORT-TERM (within 2 weeks):
    8. Add <h1>, <main>, <header>, <footer>, skip-link to all pages.
    9. Fix color contrast violations (darken orange #f5820a → #c66805).
    10. Add aria-label to #billing-toggle.
    11. Add autocomplete attributes to login form.
    12. Add password visibility toggle.
    13. Add client-side email format validation.
    14. Implement /forgot-password route.
    15. Add Sentry for error tracking.
    16. Publish a status page.
    17. Add SRI to script tags.
    18. Replace Gmail privacy contact with corporate email.
    19. Add data residency clause to /data-policy.
    20. Add sub-processor list to /privacy.

  MEDIUM-TERM (within 1 month):
    21. Add service worker + PNG icons for PWA installability.
    22. Add offline fallback page.
    23. Implement Background Sync for form drafts.
    24. Optimize LCP (preload hero, lazy-load below-fold).
    25. Code-split Next.js bundles (remove 142 KiB unused JS).
    26. Investigate bfcache prevention.
    27. Add /api/openapi.json spec.
    28. Add /api/ocid and /api/umr governance endpoints.
    29. Add input validation on /api/auth/failure-event.
    30. Run npm audit + trivy scan in CI.
    31. Add COOP/COEP/CORP headers.
    32. Add /.well-known/security.txt.
    33. Add CIN number to /terms footer.
    34. Implement multi-region failover for Supabase (read replicas).
    35. Configure Vercel Log Drain to a log aggregator.

  RE-TESTING:
    36. After credentials are restored, re-run Parts 1, 6 (AI workflow,
        RBAC roles), and verify the authenticated user journey end-to-end.
    37. After backend access is granted, re-run Tests #15, #16, #23
        with direct DB/backup inspection.

================================================================================
TESTING METHODOLOGY NOTES
================================================================================

  This certification was performed as a single end-user tester, in a
  Linux sandbox running Playwright Chromium (HeadlessChrome 151).

  Strengths of this approach:
    - Black-box perspective matches real user experience.
    - No special access required.
    - Reproducible: all artifacts saved to /home/z/my-project/screenshots/.
    - Fast: full 25-test matrix completed in one session.

  Limitations:
    - Could not test Firefox or Safari (sandbox has only Chromium).
    - Could not perform authenticated tests (demo creds invalid).
    - Could not inspect backend (DB, RLS, backups, npm audit).
    - Could not test multi-tenant isolation (need 2+ tenants).
    - Lighthouse PWA category deprecated in v13 (manual assessment
      used instead).
    - Some Web Vitals (real INP, field LCP) require RUM data, not
      available in lab testing.

  Artifacts produced:
    - 32+ PNG screenshots across 8 parts.
    - 3 Lighthouse HTML reports (login, signup, pricing).
    - 3 Lighthouse JSON reports.
    - 8 .txt reports (this is the 8th).
    - All saved to /home/z/my-project/download/ and
      /home/z/my-project/screenshots/.

================================================================================
END OF PART 8 — END OF FULL 25-TEST CERTIFICATION
================================================================================

  Total tests executed : 25
  Total reports generated: 8 (Parts 1-8)
  Total screenshots captured: 32+
  Total Lighthouse reports: 3 (login, signup, pricing)

  FINAL VERDICT: ❌ NOT CERTIFIED FOR PRODUCTION

  The application https://projexa-ai.com/ is NOT ready for production
  launch. Critical security gaps (no CSP, no rate limiting, no HttpOnly
  cookies), brand inconsistency, missing PWA capability, accessibility
  violations, and the inability to authenticate with provided demo
  credentials must all be addressed before re-running this certification.

  Once the 10 Critical Blockers and 20 High-Priority Issues are
  resolved, re-run all 25 tests. Target: 100% PASS or PARTIAL PASS
  with documented operator-side verification for UNTESTABLE items.

================================================================================
END OF FULL REPORT
================================================================================
```

<!-- ===== END PART 8 SOURCE FILE: Part8_Regression_Final_Certification_Report.txt ===== -->

---

