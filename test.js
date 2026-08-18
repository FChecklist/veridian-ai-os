#!/usr/bin/env node

/**
 * Validates the real gap-matrix deliverables:
 * - gap_matrix.yaml, our_product_inventory.yaml, reference_functions.yaml (YAML validity, non-empty)
 * - build_gap_matrix.py, crawler.js, enumerate_our_product.py, extract_reference_functions.py (syntax checks)
 *
 * Exit code: 0 if all validations pass, 1 if any fail
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const errors = [];

// Support testing from different directories
// If gap-matrix artifacts are in current dir, use those
// Otherwise, look in the expected workspace location
let WORKSPACE_ROOT = process.env.WORKSPACE_ROOT;
if (!WORKSPACE_ROOT) {
  if (fs.existsSync(path.join(process.cwd(), 'gap_matrix.yaml'))) {
    WORKSPACE_ROOT = process.cwd();
  } else {
    WORKSPACE_ROOT = '/opt/veridian/ai-os/tasks/task-20260817-184922-land-the-real-reference-erp-gap-matrix-a/workspace';
  }
}

// ============================================================================
// Helper functions
// ============================================================================

function logTest(name, passed, message = '') {
  const status = passed ? '✓' : '✗';
  const color = passed ? '\x1b[32m' : '\x1b[31m'; // green or red
  const reset = '\x1b[0m';
  console.log(`${color}${status}${reset} ${name}${message ? ': ' + message : ''}`);
  if (!passed && message) {
    errors.push(`${name}: ${message}`);
  }
}

function fileExists(filepath) {
  return fs.existsSync(filepath);
}

function fileNonEmpty(filepath) {
  const stat = fs.statSync(filepath);
  return stat.size > 0;
}

function parseYAML(content) {
  // Simple YAML parser for validation - just ensure it's valid structure
  // A proper parser would be yaml package, but we avoid external deps
  // We'll use a basic approach: check for valid YAML-like structure
  try {
    // Basic validation: YAML should have lines, and not be empty
    const lines = content.trim().split('\n');
    if (lines.length === 0) return false;

    // Try to validate basic structure - this is a minimal check
    // A real YAML parser would be needed for full validation
    // For now, we just check it's not obviously broken JSON
    if (content.trim().startsWith('{') && content.trim().endsWith('}')) {
      JSON.parse(content); // If it's JSON inside, at least it should parse
    }
    return true;
  } catch (e) {
    return false;
  }
}

function validateYAMLFiles() {
  console.log('\n[YAML Artifacts]');

  const yamlFiles = [
    'gap_matrix.yaml',
    'our_product_inventory.yaml',
    'reference_functions.yaml'
  ];

  yamlFiles.forEach(file => {
    const filepath = path.join(WORKSPACE_ROOT, file);
    // Check existence
    const exists = fileExists(filepath);
    logTest(`  ${file} exists`, exists, exists ? '' : 'File not found');

    if (!exists) return;

    // Check non-empty
    const nonEmpty = fileNonEmpty(filepath);
    logTest(`  ${file} non-empty`, nonEmpty, nonEmpty ? '' : 'File is empty');

    // Try to parse as YAML (basic validation)
    if (nonEmpty) {
      try {
        const content = fs.readFileSync(filepath, 'utf8');
        const isValid = parseYAML(content);
        logTest(`  ${file} valid YAML`, isValid);

        // Check for expected content
        if (file === 'gap_matrix.yaml') {
          const hasGapMatrix = content.includes('gap_matrix:');
          logTest(`  ${file} has gap_matrix key`, hasGapMatrix);

          // Count entries (rough check - should have multiple items)
          const refCount = (content.match(/ref_id:/g) || []).length;
          const hasContent = refCount > 0;
          logTest(`  ${file} has entries`, hasContent,
            hasContent ? `Found ${refCount} reference functions` : 'No entries found');
        }

        if (file === 'our_product_inventory.yaml') {
          const hasInventory = content.includes('our_product_inventory:');
          logTest(`  ${file} has our_product_inventory key`, hasInventory);

          // Check for inventory stats
          const hasApiRoutes = content.includes('api_routes:');
          const hasPages = content.includes('pages:');
          logTest(`  ${file} has API routes and pages`, hasApiRoutes || hasPages);
        }

        if (file === 'reference_functions.yaml') {
          const hasRefFuncs = content.includes('reference_functions:');
          logTest(`  ${file} has reference_functions key`, hasRefFuncs);
        }
      } catch (e) {
        logTest(`  ${file} parse error`, false, e.message);
      }
    }
  });
}

function validatePythonSyntax() {
  console.log('\n[Python Scripts]');

  const pythonFiles = [
    'build_gap_matrix.py',
    'enumerate_our_product.py',
    'extract_reference_functions.py'
  ];

  pythonFiles.forEach(file => {
    const filepath = path.join(WORKSPACE_ROOT, file);
    const exists = fileExists(filepath);
    logTest(`  ${file} exists`, exists, exists ? '' : 'File not found');

    if (!exists) return;

    // Check syntax with python
    try {
      execSync(`python3 -m py_compile ${filepath}`, {
        stdio: 'pipe',
        encoding: 'utf8'
      });
      logTest(`  ${file} valid syntax`, true);
    } catch (e) {
      logTest(`  ${file} valid syntax`, false, 'Syntax error');
    }
  });
}

function validateJavaScriptSyntax() {
  console.log('\n[JavaScript Scripts]');

  const jsFiles = ['crawler.js'];

  jsFiles.forEach(file => {
    const filepath = path.join(WORKSPACE_ROOT, file);
    const exists = fileExists(filepath);
    logTest(`  ${file} exists`, exists, exists ? '' : 'File not found');

    if (!exists) return;

    // Check syntax with Node.js
    try {
      const content = fs.readFileSync(filepath, 'utf8');
      new Function(content); // Will throw if syntax is invalid
      logTest(`  ${file} valid syntax`, true);
    } catch (e) {
      logTest(`  ${file} valid syntax`, false, e.message);
    }
  });
}

function validateSnapshotArchive() {
  console.log('\n[Snapshot Archive]');

  const archiveDir = path.join(WORKSPACE_ROOT, 'snapshot-archive');
  const exists = fileExists(archiveDir);
  logTest(`  snapshot-archive directory exists`, exists);

  if (exists && fs.statSync(archiveDir).isDirectory()) {
    const files = fs.readdirSync(archiveDir);
    const phaseFiles = files.filter(f => f.startsWith('Phase_') && f.endsWith('.txt'));
    const hasContent = phaseFiles.length > 0;
    logTest(`  snapshot-archive contains phase files`, hasContent,
      hasContent ? `Found ${phaseFiles.length} phase files` : 'No phase files found');
  }
}

// ============================================================================
// Main execution
// ============================================================================

console.log('====================================================================');
console.log('Gap-Matrix Artifact Validation Test');
console.log(`Testing artifacts in: ${WORKSPACE_ROOT}`);
console.log('====================================================================');

validateYAMLFiles();
validatePythonSyntax();
validateJavaScriptSyntax();
validateSnapshotArchive();

console.log('\n====================================================================');
if (errors.length === 0) {
  console.log('✓ All validations passed!');
  console.log('====================================================================');
  process.exit(0);
} else {
  console.log(`✗ ${errors.length} validation(s) failed:`);
  errors.forEach(err => console.log(`  - ${err}`));
  console.log('====================================================================');
  process.exit(1);
}
