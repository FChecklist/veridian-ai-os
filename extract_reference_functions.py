#!/usr/bin/env python3
"""
Extract reference ERP functions from snapshot phase files.
Produces YAML inventory of all functions found in the reference application.
"""

import os
import re
import yaml
from pathlib import Path

SNAPSHOT_DIR = Path('/opt/veridian/ai-os/tasks/task-20260817-045516-build-the-evidenced-reference-erp-functi/workspace/snapshot-archive')
OUTPUT_FILE = Path('/opt/veridian/ai-os/tasks/task-20260817-045516-build-the-evidenced-reference-erp-functi/workspace/reference_functions.yaml')

# Known module-to-phase mappings from the snapshot
PHASE_MAPPING = {
    'Phase_01.txt': 'Organization & System',
    'Phase_02.txt': 'Auth & Users',
    'Phase_03.txt': 'Organization & Master Data',
    'Phase_04.txt': 'Inventory & Items',
    'Phase_05.txt': 'Vendor Management',
    'Phase_06.txt': 'Requisitions',
    'Phase_07.txt': 'Quotations',
    'Phase_08.txt': 'Invoicing & Payments',
    'Phase_09_Gate_Passes_and_Inventory_Movements.txt': 'Gate Passes',
    'Phase_10_Sales_Management_and_Customer_Lifecycle.txt': 'Sales',
    'Phase_11_Accounting_and_Financial_Management.txt': 'Accounting',
    'Phase_12_Human_Resources_and_Employee_Management.txt': 'HR',
    'Phase_13_HR_Operations_-_Attendance,_Leave_and_Shifts.txt': 'HR Operations',
    'Phase_14_Payroll_and_Compensation.txt': 'Payroll',
    'Phase_15_Performance_Management_and_Appraisals.txt': 'Performance Mgmt',
    'Phase_16_Asset_and_Inventory_Management.txt': 'Asset Mgmt',
    'Phase_17_Recruitment_and_Onboarding.txt': 'Recruitment',
    'Phase_18_Reimbursement,_Expenses_and_Petty_Cash.txt': 'Expenses',
    'Phase_19_Vendor_Management_and_Contracts.txt': 'Vendor Contracts',
    'Phase_20_Rental,_ESOP,_AMC_and_Specialized_Modules.txt': 'Specialized',
}

def extract_module_table(text):
    """Extract module listing tables from phase content."""
    modules = []

    # Pattern: Module name | Option Constant | Category | Description
    # Look for lines with pipes that have consistent table structure
    lines = text.split('\n')

    # Find table rows (lines with | characters that look like a table)
    table_start = -1
    for i, line in enumerate(lines):
        if '|' in line and 'Option' in line and ('Category' in line or 'Description' in line):
            table_start = i + 1  # Skip header
            break

    if table_start == -1:
        return modules

    # Parse table rows
    for i in range(table_start, len(lines)):
        line = lines[i].strip()
        if not line or not '|' in line:
            break

        # Split by | and clean up
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue

        name = parts[0].strip()
        option = parts[1].strip()

        # Skip header and malformed rows
        if not name or name == 'Module Name' or 'COM_' not in option:
            continue

        # Handle different table formats
        if len(parts) >= 4:
            category = parts[2].strip()
            description = parts[3].strip()
        else:
            category = 'System'
            description = parts[2].strip() if len(parts) > 2 else ''

        modules.append({
            'name': name,
            'option': option,
            'category': category,
            'description': description,
        })

    return modules

def extract_from_prose(text, phase_name):
    """Extract COM_ constants mentioned in prose text with context."""
    modules = []

    # Simple approach: find all COM_* constants
    com_pattern = r'COM_[A-Z_/]+'
    matches = set(re.findall(com_pattern, text))

    # For each match, try to extract context
    for com_const in sorted(matches):
        # Find the line containing this COM_* constant
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if com_const in line:
                # Extract name from context
                # Look for patterns like "The XXX module ... accessed through COM_*"
                name_match = re.search(r'The\s+([\w\s]+?)\s+(?:module|system|interface|page)', line, re.IGNORECASE)

                if name_match:
                    name = name_match.group(1).strip()
                else:
                    # Try previous lines
                    context = ' '.join(lines[max(0, i-2):i+1])
                    name_match = re.search(r'The\s+([\w\s]+?)\s+(?:module|system|interface)', context, re.IGNORECASE)
                    if name_match:
                        name = name_match.group(1).strip()
                    else:
                        name = com_const.replace('COM_', '').replace('_', ' ').replace('/', ' ').title()

                # Get description from the sentence containing COM_*
                # Look for text after COM_* until the next period or newline
                desc_match = re.search(re.escape(com_const) + r'[,.]?\s*([^.]{0,200}?)(?:\.|$)', line)
                description = desc_match.group(1).strip() if desc_match else ''

                if not description and i + 1 < len(lines):
                    description = lines[i+1].strip()[:200]

                modules.append({
                    'name': name,
                    'option': com_const,
                    'category': 'System',
                    'description': description[:500],
                })
                break

    return modules

def generate_function_id(name, option):
    """Generate stable slug ID from module name and option."""
    # Use option constant as primary key (it's more stable)
    slug = option.lower().replace('com_', '').replace('_', '-')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    return slug

def extract_functions_from_phase(phase_file):
    """Extract functions from a single phase file."""
    try:
        with open(phase_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {phase_file}: {e}")
        return []

    # Get module category from phase mapping
    phase_name = os.path.basename(phase_file)
    module_category = PHASE_MAPPING.get(phase_name, 'System')

    # Extract module tables first (structured data)
    modules = extract_module_table(content)

    # If no table found, extract from prose
    if not modules:
        modules = extract_from_prose(content, phase_name)

    functions = []
    for mod in modules:
        # Determine kind based on category and content patterns
        if mod['category'].lower() == 'master':
            kind = 'page'  # Master data pages
        elif mod['category'].lower() == 'transaction':
            kind = 'page'  # Transaction pages
        else:
            kind = 'page'  # Default to page

        func_id = generate_function_id(mod['name'], mod['option'])

        functions.append({
            'id': func_id,
            'module': module_category,
            'name': mod['name'],
            'kind': kind,
            'category': mod['category'],
            'option_constant': mod['option'],
            'description': mod['description'],
            'evidence': f"{phase_name}",
        })

    return functions

def main():
    """Extract all reference functions from phase files."""
    print(f"Scanning {SNAPSHOT_DIR} for phase files...")

    all_functions = []

    # Process each phase file
    for phase_file in sorted(SNAPSHOT_DIR.glob('Phase_*.txt')):
        print(f"Processing {phase_file.name}...")
        functions = extract_functions_from_phase(phase_file)
        all_functions.extend(functions)
        print(f"  Found {len(functions)} functions")

    # Remove duplicates (same option constant)
    seen = set()
    unique_functions = []
    for func in all_functions:
        key = func['option_constant']
        if key not in seen:
            seen.add(key)
            unique_functions.append(func)

    # Sort by module and name
    unique_functions.sort(key=lambda x: (x['module'], x['name']))

    # Build YAML structure
    output = {
        'reference_functions': unique_functions,
        'metadata': {
            'source': 'https://x1mw26zqhcr1-d.space-z.ai',
            'snapshot_date': '2026-08-17',
            'total_functions': len(unique_functions),
            'extraction_date': '2026-08-17',
        }
    }

    # Write YAML file
    with open(OUTPUT_FILE, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n✓ Extracted {len(unique_functions)} unique reference functions")
    print(f"✓ Written to {OUTPUT_FILE}")

    # Print summary by module
    print("\nSummary by module:")
    modules = {}
    for func in unique_functions:
        mod = func['module']
        modules[mod] = modules.get(mod, 0) + 1

    for mod in sorted(modules.keys()):
        print(f"  {mod}: {modules[mod]} functions")

if __name__ == '__main__':
    main()
