#!/usr/bin/env python3
"""Drift detection: compares generated output against source data to detect inconsistencies."""

import json
import sys
from pathlib import Path


def detect_drift(data_root):
    data_root = Path(data_root)

    report = {
        'orphaned_dirs': [],
        'missing_pages': [],
        'extra_files': [],
        'stale_metadata': [],
        'issues': []
    }

    # Load ventures.json
    ventures_path = data_root / 'ventures.json'
    if not ventures_path.exists():
        report['issues'].append('ventures.json not found')
        return report

    with open(ventures_path) as f:
        data = json.load(f)

    sites_root = data_root / 'sites' / 'leo-global-holdings'
    if not sites_root.exists():
        report['issues'].append('sites/leo-global-holdings not found')
        return report

    # Build expected paths from ventures.json
    expected_dirs = set()
    expected_dirs.add('index.html')

    for group in data.get('groups', []):
        gid = group['id']
        expected_dirs.add(f'{gid}/index.html')
        for venture in data.get('ventures', []):
            if venture.get('parentId') == gid:
                vid = venture['id']
                expected_dirs.add(f'{gid}/{vid}/index.html')
                for offering in venture.get('offerings', []):
                    oid = offering['id']
                    expected_dirs.add(f'{gid}/{vid}/{oid}/index.html')

    # Find actual HTML files
    actual_files = set()
    for f in sites_root.rglob('index.html'):
        rel = str(f.relative_to(sites_root)).replace('\\', '/')
        actual_files.add(rel)

    # Check for missing pages
    for expected in expected_dirs:
        if expected not in actual_files:
            report['missing_pages'].append(expected)

    # Check for orphaned dirs (HTML files not in expected set)
    for actual in actual_files:
        if actual not in expected_dirs:
            report['extra_files'].append(actual)

    # Check metadata freshness
    for f in sites_root.rglob('_metadata.json'):
        rel = str(f.relative_to(sites_root))
        try:
            meta = json.loads(f.read_text())
            if 'generated' not in meta:
                report['stale_metadata'].append(rel)
        except (json.JSONDecodeError, KeyError):
            report['stale_metadata'].append(rel)

    # Check for global-nav.json
    nav_path = sites_root / 'global-nav.json'
    if nav_path.exists():
        try:
            nav = json.loads(nav_path.read_text())
            nav_groups = len(nav.get('groups', []))
            # Only groups with type='group' appear in nav (strategic-verticals are excluded)
            source_nav_groups = len([g for g in data.get('groups', []) if g.get('type') == 'group'])
            if nav_groups != source_nav_groups:
                report['issues'].append(
                    f'Nav groups ({nav_groups}) != source nav-eligible groups ({source_nav_groups})'
                )
        except (json.JSONDecodeError, KeyError):
            report['issues'].append('global-nav.json invalid')
    else:
        report['issues'].append('global-nav.json missing')

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python drift-detection.py <data-root>")
        sys.exit(1)

    data_root = sys.argv[1]
    report = detect_drift(data_root)

    print("=" * 50)
    print("DRIFT DETECTION REPORT")
    print("=" * 50)
    print(f"  Missing pages: {len(report['missing_pages'])}")
    print(f"  Extra files: {len(report['extra_files'])}")
    print(f"  Stale metadata: {len(report['stale_metadata'])}")
    print(f"  Issues: {len(report['issues'])}")

    if report['missing_pages']:
        print("\n  Missing pages:")
        for p in report['missing_pages']:
            print(f"    - {p}")

    if report['extra_files']:
        print("\n  Extra files (not in ventures.json):")
        for f in report['extra_files']:
            print(f"    - {f}")

    if report['stale_metadata']:
        print("\n  Stale metadata:")
        for m in report['stale_metadata']:
            print(f"    - {m}")

    if report['issues']:
        print("\n  Issues:")
        for issue in report['issues']:
            print(f"    - {issue}")

    passed = (
        len(report['missing_pages']) == 0 and
        len(report['issues']) == 0
    )

    print(f"\n  DRIFT CHECK: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
