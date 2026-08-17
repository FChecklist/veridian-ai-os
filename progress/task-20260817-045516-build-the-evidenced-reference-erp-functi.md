# Task: Build the Evidenced Reference ERP Function Inventory

## Objective
Produce ONE authoritative, machine-readable inventory that answers: for every single function of a reference ERP application: does it exist in our product, where, and is it real?

## Step 0 - Preserve the Reference (MANDATORY)
- [ ] Check if reference URL https://x1mw26zqhcr1-d.space-z.io is reachable
- [ ] Crawl with headless browser (Next.js client-rendered app)
- [ ] Save all routes, JS chunks, JSON, OpenAPI schemas
- [ ] Commit snapshot to repo with file/byte counts

## Step 1 - Enumerate Reference Surface
- [ ] Extract functions from snapshot into YAML
- [ ] Each row: id, module, name, kind, evidence

## Step 2 - Enumerate Our Product
- [ ] Extract from three repos: routes, pages, DB tables, reports, jobs
- [ ] Use read-only DB tooling

## Step 3 - Build Gap Matrix
- [ ] Join reference to our product
- [ ] Status: PRESENT_REAL, PRESENT_STUB, PRESENT_PARTIAL, DUPLICATE, MISSING, UNVERIFIABLE
- [ ] Every non-MISSING: code proof + API proof + DB proof

## Step 4 - Register Child Work Items
- [ ] Register work per module
- [ ] Honest complexity assessment

## Completed
- [x] Created progress tracking
- [x] Verified reference URL reachability (https://x1mw26zqhcr1-d.space-z.ai)
- [x] Created complete snapshot: 22 files, 517KB (index.html + 20 phase files)
- [x] Committed snapshot to repo
- [x] Extracted reference function inventory: 295 functions across 19 modules
  - Accounting: 28 | Asset Mgmt: 18 | Expenses: 8 | Gate Passes: 24
  - HR: 40 | HR Operations: 20 | Inventory & Items: 13 | Invoicing & Payments: 10
  - Organization & Master Data: 8 | Organization & System: 28 | Payroll: 14
  - Performance Mgmt: 10 | Quotations: 6 | Recruitment: 10 | Requisitions: 4
  - Sales: 20 | Specialized: 24 | Vendor Contracts: 6 | Vendor Management: 4

## Remaining
- [ ] Enumerate our product (three repos: check routes, pages, DB tables, reports, jobs)
- [ ] Build gap matrix (join reference to our product)
- [ ] Register child work items
- [ ] Final audit and reporting
