#!/usr/bin/env python3
"""Health check script: validates a generated site directory."""

import json
import sys
from pathlib import Path
from html.parser import HTMLParser


class LinkChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a' and 'href' in d:
            self.links.append(d['href'])
        if tag == 'img' and 'src' in d:
            self.images.append(d['src'])


def check_site(sites_root):
    sites_root = Path(sites_root)
    report = {
        'html_files': 0,
        'json_files': 0,
        'empty_files': 0,
        'missing_title': 0,
        'missing_nav': 0,
        'missing_footer': 0,
        'orphan_pages': [],
        'broken_internal_links': [],
        'issues': []
    }

    all_pages = {}
    for f in sites_root.rglob('index.html'):
        rel = f.relative_to(sites_root)
        all_pages[str(rel)] = f
        report['html_files'] += 1
        content = f.read_text(encoding='utf-8')

        if len(content.strip()) == 0:
            report['empty_files'] += 1
            report['issues'].append(f'Empty file: {rel}')
            continue

        if '<title>' not in content:
            report['missing_title'] += 1

        if 'nav' not in content.lower() and 'navigation' not in content.lower():
            report['missing_nav'] += 1

        if 'footer' not in content.lower():
            report['missing_footer'] += 1

    for f in sites_root.rglob('_*.json'):
        report['json_files'] += 1

    for f in sites_root.rglob('global-nav.json'):
        try:
            nav = json.loads(f.read_text())
            if 'groups' not in nav:
                report['issues'].append('global-nav.json missing groups key')
        except json.JSONDecodeError:
            report['issues'].append('global-nav.json invalid JSON')

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python health-check.py <sites-root>")
        sys.exit(1)

    sites_root = sys.argv[1]
    report = check_site(sites_root)

    print("=" * 50)
    print("SITE HEALTH CHECK REPORT")
    print("=" * 50)
    print(f"  HTML files: {report['html_files']}")
    print(f"  JSON files: {report['json_files']}")
    print(f"  Empty files: {report['empty_files']}")
    print(f"  Missing title: {report['missing_title']}")
    print(f"  Missing nav: {report['missing_nav']}")
    print(f"  Missing footer: {report['missing_footer']}")
    print(f"  Issues: {len(report['issues'])}")

    if report['issues']:
        print("\n  Issues found:")
        for issue in report['issues']:
            print(f"    - {issue}")
    else:
        print("\n  No issues found")

    passed = (
        report['empty_files'] == 0 and
        report['missing_title'] == 0 and
        len(report['issues']) == 0 and
        report['html_files'] >= 50
    )

    print(f"\n  HEALTH CHECK: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
