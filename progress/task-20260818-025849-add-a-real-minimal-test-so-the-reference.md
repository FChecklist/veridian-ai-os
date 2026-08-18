# PROGRESS -- task-20260818-025849-add-a-real-minimal-test-so-the-reference

## Objective
Add ONE real, meaningful test script that validates the real gap-matrix deliverables:
- gap_matrix.yaml and our_product_inventory.yaml parse as valid YAML and are non-empty
- reference_functions.yaml parses as valid YAML
- build_gap_matrix.py, crawler.js, enumerate_our_product.py, extract_reference_functions.py pass real syntax/lint checks

The test must genuinely fail if artifacts are missing or malformed (not a stub).

## Completed
- [x] Verified existing artifacts in worker/task-20260817-184922-land-the-real-reference-erp-gap-matrix-a branch:
  - gap_matrix.yaml (72K, 295 reference functions)
  - our_product_inventory.yaml (163K, 1199 API routes / 248 pages)
  - reference_functions.yaml exists (2.4K, real reference function catalog)
  - build_gap_matrix.py, crawler.js, enumerate_our_product.py, extract_reference_functions.py all present
  - snapshot-archive/ with 20 phase files (22 files total, 517KB)
  - All artifacts are real, coherent, and properly structured
- [x] Created test.js that validates all artifacts:
  - YAML validity checks for gap_matrix.yaml, our_product_inventory.yaml, reference_functions.yaml
  - Verifies expected root keys and non-empty content
  - Python syntax validation via py_compile (build_gap_matrix.py, enumerate_our_product.py, extract_reference_functions.py)
  - JavaScript syntax validation via Function() constructor (crawler.js)
  - Snapshot archive validation (checks for 20 Phase_*.txt files)
  - Supports WORKSPACE_ROOT env var to test against any directory
  - Auto-detects gap-matrix workspace location
  - **Test passes with all artifacts present** ✓
  - **Test fails (exit code 1) when artifacts missing** ✓
- [x] Updated package.json test script to run test.js
- [x] Verified test works correctly with both present and missing artifacts

## Remaining
- [ ] Commit test.js and package.json to this branch
- [ ] Open/reuse PR with SUCCESS_CRITERIA describing this as data/tooling artifact
- [ ] Get genuinely independent AUDIT:PASS
- [ ] Merge on real green CI
- [ ] Verify on post-merge main
- [ ] Record completion in UMR registry
