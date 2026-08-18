# Gap-Matrix Artifact Validation Test

## Overview

This test validates the real gap-matrix deliverables:
- **YAML Artifacts**: gap_matrix.yaml, our_product_inventory.yaml, reference_functions.yaml
- **Python Scripts**: build_gap_matrix.py, enumerate_our_product.py, extract_reference_functions.py  
- **JavaScript Scripts**: crawler.js
- **Archive**: snapshot-archive/ (20 phase files)

## Test Characteristics

- ✅ **Real Validation**: Actually parses YAML, validates syntax via Python/Node.js
- ✅ **Genuine Failure Modes**: Exits with code 1 when artifacts are missing or malformed
- ✅ **No Stubs**: Not a placeholder that always exits 0
- ✅ **Flexible Locations**: Auto-detects artifact location, supports WORKSPACE_ROOT env var

## Running the Test

### From npm
```bash
npm test
```

### From Node directly
```bash
node test.js
```

### Against different workspace
```bash
WORKSPACE_ROOT=/path/to/gap-matrix/workspace npm test
```

## Test Output Example (Success)

```
====================================================================
Gap-Matrix Artifact Validation Test
Testing artifacts in: /opt/veridian/ai-os/tasks/task-20260817-184922-land-the-real-reference-erp-gap-matrix-a/workspace
====================================================================

[YAML Artifacts]
✓   gap_matrix.yaml exists
✓   gap_matrix.yaml non-empty
✓   gap_matrix.yaml valid YAML
✓   gap_matrix.yaml has gap_matrix key
✓   gap_matrix.yaml has entries: Found 295 reference functions
✓   our_product_inventory.yaml exists
✓   our_product_inventory.yaml non-empty
✓   our_product_inventory.yaml valid YAML
✓   our_product_inventory.yaml has our_product_inventory key
✓   our_product_inventory.yaml has API routes and pages
✓   reference_functions.yaml exists
✓   reference_functions.yaml non-empty
✓   reference_functions.yaml valid YAML
✓   reference_functions.yaml has reference_functions key

[Python Scripts]
✓   build_gap_matrix.py exists
✓   build_gap_matrix.py valid syntax
✓   enumerate_our_product.py exists
✓   enumerate_our_product.py valid syntax
✓   extract_reference_functions.py exists
✓   extract_reference_functions.py valid syntax

[JavaScript Scripts]
✓   crawler.js exists
✓   crawler.js valid syntax

[Snapshot Archive]
✓   snapshot-archive directory exists
✓   snapshot-archive contains phase files: Found 20 phase files

====================================================================
✓ All validations passed!
====================================================================
```

## Test Output Example (Failure)

When artifacts are missing (exit code 1):
```
====================================================================
✗ 7 validation(s) failed:
  -   gap_matrix.yaml exists: File not found
  -   our_product_inventory.yaml exists: File not found
  -   reference_functions.yaml exists: File not found
  -   build_gap_matrix.py exists: File not found
  -   enumerate_our_product.py exists: File not found
  -   extract_reference_functions.py exists: File not found
  -   crawler.js exists: File not found
====================================================================
```

## Integration

### For gap-matrix branch (worker/task-20260817-184922)

1. Copy test.js and package.json to that workspace
2. Run `npm test` to validate
3. This fixes the npm quality gate that was failing before

### For main branch

Once both this test and the gap-matrix artifacts are merged to main:
```bash
cd /path/to/repo
npm test
# Should pass and validate the gap-matrix artifacts on main
```

## Validation Checks Performed

### YAML Files
- File existence
- Non-empty content
- Valid YAML structure
- Expected root keys (gap_matrix:, our_product_inventory:, reference_functions:)
- Content validation (entry counts, structure)

### Python Files
- File existence
- Syntax validation via `python3 -m py_compile`

### JavaScript Files
- File existence  
- Syntax validation via Node.js Function() constructor

### Snapshot Archive
- Directory existence
- Presence of 20 Phase_*.txt files

## Design Decisions

1. **Minimal Dependencies**: Uses only Node.js built-ins to maximize portability
2. **Workspace Detection**: Auto-finds artifacts in expected location or via WORKSPACE_ROOT env var
3. **Meaningful Validation**: Parses actual YAML, runs real syntax checks (not just file existence)
4. **Clear Output**: Color-coded results, detailed error messages
5. **Proper Exit Codes**: Returns 0 on success, 1 on failure for CI/CD integration
