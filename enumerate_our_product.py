#!/usr/bin/env python3
"""
Enumerate our product implementation: API routes, pages, DB tables, reports, jobs
from the three product repositories.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

REPOS = {
    'compliance-tracker': '/opt/veridian/repos/compliance-tracker',
    'projexa': '/opt/veridian/repos/projexa',
    'veda-advisors': '/opt/veridian/repos/veda-advisors',
}

OUTPUT_FILE = Path('/opt/veridian/ai-os/tasks/task-20260817-045516-build-the-evidenced-reference-erp-functi/workspace/our_product_inventory.yaml')

def scan_api_routes(repo_path):
    """Extract API routes from app/api directories."""
    routes = []
    api_dir = Path(repo_path) / 'src' / 'app' / 'api'

    if not api_dir.exists():
        # Try alternative patterns
        api_dir = Path(repo_path) / 'app' / 'api'

    if not api_dir.exists():
        return routes

    # Find all route files (route.ts and route.js)
    route_files = list(api_dir.rglob('route.ts')) + list(api_dir.rglob('route.js'))

    for route_file in route_files:
        rel_path = route_file.relative_to(repo_path)
        # Extract route path from file structure
        # src/app/api/[category]/[resource]/route.ts -> /api/category/resource
        parts = route_file.parent.relative_to(api_dir).parts

        # Get HTTP method from file content if possible
        try:
            with open(route_file, 'r', errors='ignore') as f:
                content = f.read()
                methods = []
                if re.search(r'export\s+(?:async\s+)?function\s+GET', content):
                    methods.append('GET')
                if re.search(r'export\s+(?:async\s+)?function\s+POST', content):
                    methods.append('POST')
                if re.search(r'export\s+(?:async\s+)?function\s+PUT', content):
                    methods.append('PUT')
                if re.search(r'export\s+(?:async\s+)?function\s+DELETE', content):
                    methods.append('DELETE')
                if re.search(r'export\s+(?:async\s+)?function\s+PATCH', content):
                    methods.append('PATCH')
        except:
            methods = []

        methods_str = ', '.join(methods) if methods else 'GET'

        routes.append({
            'path': f"/api/{'/'.join(parts)}",
            'file': str(rel_path),
            'methods': methods_str,
        })

    return routes

def scan_pages(repo_path):
    """Extract application pages."""
    pages = []
    app_dir = Path(repo_path) / 'src' / 'app'

    if not app_dir.exists():
        app_dir = Path(repo_path) / 'app'

    if not app_dir.exists():
        return pages

    # Find all page files (multiple extensions)
    page_files = []
    for ext in ['tsx', 'ts', 'jsx', 'js']:
        page_files.extend(app_dir.rglob(f'page.{ext}'))

    for page_file in page_files:
        rel_path = page_file.relative_to(app_dir)
        # Get route from directory structure
        route_parts = list(rel_path.parent.parts)
        # Filter out internal next.js directories
        route_parts = [p for p in route_parts if not p.startswith('_')]
        route = '/' + '/'.join(route_parts) if route_parts else '/'

        pages.append({
            'path': route,
            'file': str(page_file.relative_to(repo_path)),
        })

    return pages

def scan_db_tables(repo_path):
    """Extract database tables from schema files."""
    tables = []

    # Look for Drizzle schema files - search for any db-like paths
    search_patterns = [
        'src/lib/db',
        'src/db',
        'lib/db',
        'drizzle',
    ]

    found_files = []
    for pattern in search_patterns:
        pattern_path = Path(repo_path) / pattern
        if pattern_path.exists():
            # Find all TypeScript files in this directory
            for ts_file in pattern_path.rglob('*.ts'):
                # Skip node_modules and dist
                if 'node_modules' not in str(ts_file) and 'dist' not in str(ts_file):
                    found_files.append(ts_file)

    for schema_file in found_files:
        try:
            with open(schema_file, 'r', errors='ignore') as f:
                content = f.read()

            # Find table definitions (pgTable or similar)
            table_pattern = r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:pgTable|mysqlTable|sqliteTable|table)\s*\('
            matches = re.findall(table_pattern, content)

            for table_name in matches:
                tables.append({
                    'name': table_name,
                    'file': str(schema_file.relative_to(repo_path)),
                    'type': 'DB Table',
                })
        except:
            pass

    return tables

def scan_jobs(repo_path):
    """Extract background jobs or scheduled tasks."""
    jobs = []

    # Look for job files in common locations
    job_patterns = [
        'src/jobs',
        'src/lib/jobs',
        'src/api/jobs',
        'jobs',
    ]

    for pattern in job_patterns:
        job_dir = Path(repo_path) / pattern
        if job_dir.exists():
            for job_file in job_dir.rglob('*.{ts,js}'):
                rel_path = job_file.relative_to(repo_path)
                jobs.append({
                    'name': job_file.stem,
                    'file': str(rel_path),
                    'type': 'Background Job',
                })

    # Also look for cron jobs or scheduled tasks
    for file in Path(repo_path).rglob('*.{ts,js}'):
        try:
            with open(file, 'r', errors='ignore') as f:
                content = f.read()
                if 'cron' in content.lower() or 'schedule' in content.lower() or 'interval' in content.lower():
                    # Check if it's a job/worker file
                    if any(x in str(file) for x in ['job', 'worker', 'schedule', 'cron', 'task']):
                        rel_path = file.relative_to(repo_path)
                        jobs.append({
                            'name': file.stem,
                            'file': str(rel_path),
                            'type': 'Scheduled Task',
                        })
        except:
            pass

    return jobs

def scan_reports(repo_path):
    """Extract report definitions."""
    reports = []

    # Look for report files
    report_patterns = [
        'src/lib/reports',
        'src/reports',
        'reports',
    ]

    for pattern in report_patterns:
        report_dir = Path(repo_path) / pattern
        if report_dir.exists():
            for report_file in report_dir.rglob('*.{ts,js}'):
                rel_path = report_file.relative_to(repo_path)
                reports.append({
                    'name': report_file.stem,
                    'file': str(rel_path),
                    'type': 'Report',
                })

    return reports

def main():
    print("Enumerating our product implementation...")

    all_inventory = {
        'api_routes': [],
        'pages': [],
        'db_tables': [],
        'jobs': [],
        'reports': [],
        'by_repo': {}
    }

    for repo_name, repo_path in REPOS.items():
        if not os.path.exists(repo_path):
            print(f"⚠ Repo not found: {repo_path}")
            continue

        print(f"\n=== {repo_name} ===")

        repo_inventory = {
            'api_routes': scan_api_routes(repo_path),
            'pages': scan_pages(repo_path),
            'db_tables': scan_db_tables(repo_path),
            'jobs': scan_jobs(repo_path),
            'reports': scan_reports(repo_path),
        }

        all_inventory['by_repo'][repo_name] = repo_inventory

        # Aggregate
        all_inventory['api_routes'].extend([(repo_name, r) for r in repo_inventory['api_routes']])
        all_inventory['pages'].extend([(repo_name, p) for p in repo_inventory['pages']])
        all_inventory['db_tables'].extend([(repo_name, t) for t in repo_inventory['db_tables']])
        all_inventory['jobs'].extend([(repo_name, j) for j in repo_inventory['jobs']])
        all_inventory['reports'].extend([(repo_name, r) for r in repo_inventory['reports']])

        print(f"API Routes: {len(repo_inventory['api_routes'])}")
        print(f"Pages: {len(repo_inventory['pages'])}")
        print(f"DB Tables: {len(repo_inventory['db_tables'])}")
        print(f"Jobs: {len(repo_inventory['jobs'])}")
        print(f"Reports: {len(repo_inventory['reports'])}")

    # Write summary YAML
    output = {
        'our_product_inventory': {
            'total_api_routes': len(all_inventory['api_routes']),
            'total_pages': len(all_inventory['pages']),
            'total_db_tables': len(all_inventory['db_tables']),
            'total_jobs': len(all_inventory['jobs']),
            'total_reports': len(all_inventory['reports']),
            'by_repo': {}
        },
        'details': all_inventory['by_repo']
    }

    with open(OUTPUT_FILE, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n✓ Inventory written to {OUTPUT_FILE}")
    print(f"\nSummary:")
    print(f"  API Routes: {len(all_inventory['api_routes'])}")
    print(f"  Pages: {len(all_inventory['pages'])}")
    print(f"  DB Tables: {len(all_inventory['db_tables'])}")
    print(f"  Jobs: {len(all_inventory['jobs'])}")
    print(f"  Reports: {len(all_inventory['reports'])}")

if __name__ == '__main__':
    main()
