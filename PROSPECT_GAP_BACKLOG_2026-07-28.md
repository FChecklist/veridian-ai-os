# Prospect Requirement Gap Backlog — 2026-07-28

Source: Owner-supplied handwritten specs (construction/design-studio project
management), Sales Pipeline dashboard mockups, daily-timesheet spec, and a
real BoQ Excel file (`Sample Scope with Sub Task.xlsx`, 160 rows, Category ->
Task -> Sub-Task -> Breakdown% -> Rate -> Amount). Target: PROJEXA
(construction-facing) + compliance-tracker (VERIDIAN backend), per the
established "PROJEXA = thin client on full VERIDIAN OS" architecture.

## Confirmed already-built (verify against real data, do not rebuild)
- Hierarchical BoQ breakdown-% (PR #596, `constructionBoqLineItems`,
  `computeHierarchicalAmount`) — real-world shape matches the uploaded
  Excel file closely. ACTION: verify the Excel BoQ importer
  (`construction-boq-import-service.ts`) parses this exact file correctly,
  including section header rows (e.g. "PARTITION AND LINING") and
  multi-line descriptions with embedded location annotations — fix the
  importer if it chokes on these real-world quirks, don't rebuild the
  hierarchy logic itself.
- Interim billing/retention/tax (PR #596 fix).
- Timesheet budget-vs-actual report (PR #597) — cross-check against the
  "Daily timesheets for Design Studio" spec below; PR #597 may already
  cover most of this.
- PWA offline work-progress queue (PR #54, projexa).
- PM/Site-Engineer/Client-Viewer roles (PR #56, projexa).
- VERIDIAN revenue/expense integration into PROJEXA dashboard (working
  today, confirmed live).

## Real gaps to dispatch (each a candidate for its own scoped task)

### 1. Permits module
Data entry + PDF upload. Fields: permit name, issue date, end date. Check
if any existing "compliance item"/"licenses" table in compliance-tracker
already covers this shape before building new schema.

### 2. Drawings & 3D module
Upload DWG files + 3D walkthrough files/links, associated per project.

### 3. Documents module
Generic upload (PDF/email/permit-related), categorized, per project.

### 4. MoMs (Minutes of Meeting)
Live meeting-notes creation, save as PDF, send via WhatsApp. Check if
VERI Meeting Intelligence (mentioned in earlier memory, `veri-meeting-service.ts`)
already covers live MoM creation — likely yes, this may be a wiring gap
into PROJEXA's UI, not a new build.

### 5. Scope of Works + Variations
Upload Excel of scope, record variations (+ve/-ve) against original scope
with revision history (Rev1/Rev2/...), compare versions. Real business
rule from the Owner's own notes: "-ve variations must be checked against
Work Progress Report in case work is already done" (prevent negative-scope
changes on already-completed work) — this is a real validation rule, not
optional. Also: "option of uploading site instruction form" (format TBD,
flag as blocked-on-Owner-input, don't invent a format).

### 6. Work Progress Report (WPR)
Date-range filter, daily entry of qty + site pictures per activity, save
as PDF + WhatsApp. Real report shape from the Owner's sketch: columns
S.No/Category/Code/Description, then grouped columns for
Qty[Unit/Rate/Amt], Amt[Prev/Current/Total], Percentage[Prev/Current/Total]
— the percentage columns are formulas over the amount columns (Prev/Total,
Current/Total etc per the sketch's "B1/A1" style annotations), not raw
input. Reports needed: category-wise, scope-wise, manpower-wise,
vendor-wise breakdowns of the same underlying data.
Real cross-cutting requirement: scope changes from item 5 must
automatically update WPR line items.

### 7. Manpower module
Manpower database: ID, Name, Trade, Salary. Daily attendance recorded
trade-wise, rolling into a daily cost report. Attendance report shape:
S.No | ID | Name | Company | Salary, filtered by trade.

### 8. Material module
Material database: spec, cost, qty. Track material inbound (receiving),
roll into a cost report.

### 9. Budget module
Per-scope-item budget default at 25% (Owner-configurable per line item,
not hardcoded), tracked against vendor name/vendor amount/material/
manpower per scope item. Budget summary report: S.No | Category | Code |
Description | Qty | Rate | Amount | Vendor 1 | Vendor Amount, filterable.
Cross-check against item 5's variation-revision tracking — budget should
reflect current revision, not just original scope.

### 10. Schedule module
Upload Excel schedule, track progress against it over time.

### 11. Reports & Dashboard (cross-cutting)
All reports must be real interactive dashboards, not static exports.
Confirmed real report list from Owner's notes: Work Progress Report,
Weekly Project Report (category-wise, date-filtered vs total), Project
Status Report (Revenue/Budget/Expense + Subcontractor/Budget breakup),
Attendance Report, Site Picture Report (daily photos), Scope of Work
report (with subcontractor rate/amount/vendor columns).
Dashboard hierarchy per Owner's diagram: Company (UAE/India) -> Dept
(Projects/Studio) -> Project -> Details (Revenue/Budget/Expense/Progress,
date-range filterable), click any project for graphical detail reports.
Category distribution chart needed per project (e.g. Gypsum/Civil/
Joinery/Paint/Misc split, both as pie chart and as a bar chart showing
completed-vs-total per category) — this is a real, specific chart type
requirement, not generic "add charts."
Also needed: a simple multi-project status-bar dashboard (horizontal bar
per project showing % complete, per Owner's simple sketch) as a
lightweight overview separate from the detailed drill-down dashboards.

### 12. Design Studio timesheets (distinct from field/site work above)
Daily work recording by designer at end of day. Status flow: designer
enters daily work -> manager validates on review. Timesheet fields: Date |
Project | Category | Task | Hours. Cost analysis (marked IMPORTANT by
Owner): Budget vs Actual, broken down category-wise, designer-wise,
project-wise, PLUS a designer-wise status view. Work analysis view. KPI
flow: designer fills KPI, manager reviews/approves. Cross-check against
PR #597's existing budget-vs-actual timesheet report before building new
-- likely needs extension (designer-wise cuts, KPI/approval workflow) more
than a rebuild.

### 13. Sales Pipeline dashboard (CRM-side, likely compliance-tracker/CRM module)
Real KPI tiles: Sales Value, Hold %, Lost %, Success %, Health %, Regret %.
Two charts: Sales Lead Performance (bar, count of value by salesperson)
and Pipeline Status Overview (bar, count by stage: Awarded/Lost/Hold/
Pitched/Lead/Regret/Estimation/Follow-up). Monthly Revenue Trend: 3-line
chart (Target/Achieved/Shortfall) over months, plus a KPI table below with
the same rows. Right-side panel: Project Value Status Analysis, a
scrollable list of named deals with their current status and value.
Real interaction requirement confirmed by the 2 screenshots: clicking a
pipeline-status bar (e.g. "Awarded") filters the ENTIRE dashboard to that
status -- all KPI tiles, both charts, and the table recompute for the
filtered subset (screenshot 2 shows the drilled-down "Sales Pipeline
Awarded" state). This is a real cross-filtering requirement, not a
static report. Check compliance-tracker's existing CRM opportunity-stage
tracking before building new fields -- likely already has stage data,
gap is the dashboard/interaction layer.

## Constraints for all dispatched work in this backlog
- Zero duplication: check existing schema/services first (compliance-tracker
  is ~10,900 lines in schema.ts alone -- grep before adding tables).
- Every module needs real screens (not stubs), real business logic (not
  hardcoded placeholder data), matching the specific field-level detail
  above where given.
- PROJEXA branding, not raw VERIDIAN copy, for anything user-facing in
  projexa-ai.com.
- Real supervisor audit before merge, tier1 auto-merge / tier2 queued for
  Owner review -- do not bypass this gate.
