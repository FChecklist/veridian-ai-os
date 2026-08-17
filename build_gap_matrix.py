#!/usr/bin/env python3
"""
Build the gap matrix by joining reference functions with our product inventory.
Status: PRESENT_REAL, PRESENT_STUB, PRESENT_PARTIAL, DUPLICATE, MISSING, UNVERIFIABLE
"""

import yaml
from pathlib import Path
from difflib import SequenceMatcher

# Load reference functions
with open('reference_functions.yaml', 'r') as f:
    ref_data = yaml.safe_load(f)
    reference_functions = ref_data['reference_functions']

# Load our product inventory
with open('our_product_inventory.yaml', 'r') as f:
    our_data = yaml.safe_load(f)
    our_inventory = our_data['details']

print(f"Reference functions: {len(reference_functions)}")
print(f"Our product repos: {len(our_inventory)}")

# Extract all our routes and pages for matching
our_routes = []
our_pages = []
our_tables = []

for repo_name, repo_inventory in our_inventory.items():
    if 'api_routes' in repo_inventory:
        for route in repo_inventory['api_routes']:
            our_routes.append({
                'repo': repo_name,
                'path': route.get('path', ''),
                'file': route.get('file', ''),
                'methods': route.get('methods', ''),
                'type': 'API Route'
            })

    if 'pages' in repo_inventory:
        for page in repo_inventory['pages']:
            our_pages.append({
                'repo': repo_name,
                'path': page.get('path', ''),
                'file': page.get('file', ''),
                'type': 'Page'
            })

    if 'db_tables' in repo_inventory:
        for table in repo_inventory['db_tables']:
            our_tables.append({
                'repo': repo_name,
                'name': table.get('name', ''),
                'file': table.get('file', ''),
                'type': 'DB Table'
            })

print(f"Total our routes: {len(our_routes)}")
print(f"Total our pages: {len(our_pages)}")
print(f"Total our tables: {len(our_tables)}")

def similarity_ratio(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_matches(ref_func, our_routes, our_pages, our_tables):
    """Find potential matches for a reference function."""

    name = ref_func['name'].lower()
    option_const = ref_func['option_constant'].lower()

    matches = []

    # Try matching by name similarity in routes
    for route in our_routes:
        route_path_lower = route['path'].lower()
        if similarity_ratio(name, route_path_lower) > 0.6:
            matches.append({
                'type': 'API Route',
                'item': route,
                'score': similarity_ratio(name, route_path_lower)
            })

    # Try matching by option constant in routes
    for route in our_routes:
        route_path_lower = route['path'].lower()
        if option_const.replace('_', '').replace('com', '') in route_path_lower.replace('_', '').replace('-', ''):
            matches.append({
                'type': 'API Route',
                'item': route,
                'score': 0.8
            })

    # Try matching by name in pages
    for page in our_pages:
        if similarity_ratio(name, page['path'].lower()) > 0.6:
            matches.append({
                'type': 'Page',
                'item': page,
                'score': similarity_ratio(name, page['path'].lower())
            })

    # Try matching by name in tables
    for table in our_tables:
        if similarity_ratio(name, table['name'].lower()) > 0.6:
            matches.append({
                'type': 'DB Table',
                'item': table,
                'score': similarity_ratio(name, table['name'].lower())
            })

    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches[:3]  # Return top 3 matches

# Build gap matrix
gap_matrix = []

for ref_func in reference_functions:
    matches = find_matches(ref_func, our_routes, our_pages, our_tables)

    # Determine status
    if not matches:
        status = 'MISSING'
        evidence = None
    elif len(matches) > 1:
        # Check for duplicates
        status = 'PRESENT_PARTIAL'  # Found but unsure which
        evidence = [m['item'] for m in matches]
    else:
        match = matches[0]
        # For now, mark as UNVERIFIABLE since we haven't actually tested
        status = 'UNVERIFIABLE'  # Found route/page but not verified with real API test
        evidence = match['item']

    gap_row = {
        'ref_id': ref_func['id'],
        'name': ref_func['name'],
        'module': ref_func['module'],
        'reference_kind': ref_func['kind'],
        'reference_option': ref_func['option_constant'],
        'status': status,
        'evidence': evidence,
        'notes': f"Found {len(matches)} potential matches" if matches else "No matches found"
    }

    gap_matrix.append(gap_row)

# Summary
summary = {}
for row in gap_matrix:
    status = row['status']
    summary[status] = summary.get(status, 0) + 1

print(f"\nGap Matrix Summary:")
for status in ['PRESENT_REAL', 'PRESENT_STUB', 'PRESENT_PARTIAL', 'DUPLICATE', 'MISSING', 'UNVERIFIABLE']:
    count = summary.get(status, 0)
    print(f"  {status}: {count}")

# Write gap matrix
output = {
    'gap_matrix': gap_matrix,
    'summary': summary,
    'total_reference_functions': len(reference_functions),
    'our_product_counts': {
        'api_routes': len(our_routes),
        'pages': len(our_pages),
        'db_tables': len(our_tables),
    }
}

with open('gap_matrix.yaml', 'w') as f:
    yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"\n✓ Gap matrix written to gap_matrix.yaml")
