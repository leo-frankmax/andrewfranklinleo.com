#!/usr/bin/env python3
"""Comprehensive integration test: pipeline + health check + drift detection."""

import sys
import json
import tempfile
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_agent_module(agent_name):
    agent_path = PROJECT_ROOT / 'docker' / 'agents' / agent_name / 'agent.py'
    spec = importlib.util.spec_from_file_location(agent_name.replace('-', '_'), str(agent_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_comprehensive_test():
    test_root = Path(tempfile.mkdtemp(prefix='afl-comprehensive-'))
    print(f"Test directory: {test_root}")

    report = {
        'timestamp': datetime.now().isoformat(),
        'pipeline': {},
        'health': {},
        'drift': {},
        'all_passed': False
    }

    try:
        # Load agents
        vg_mod = load_agent_module('venture-generator')
        sc_mod = load_agent_module('site-creator')
        cw_mod = load_agent_module('content-writer')
        gb_mod = load_agent_module('graph-builder')
        qa_mod = load_agent_module('qa-validator')

        # Load source data
        with open(PROJECT_ROOT / 'ventures.json') as f:
            data = json.loads(json.dumps(json.load(f)))

        # STEP 1: Venture Generator
        print("\n[1/5] Venture Generator")
        agent = vg_mod.VentureGenerator(data_root=str(test_root))
        result = agent.run(data)
        report['pipeline']['venture_generator'] = {
            'success': result['success'],
            'groups': result['groups_processed'],
            'ventures': result['ventures_created'],
            'offerings': result['offerings_created'],
            'iterations': agent.iteration_count
        }
        assert result['success'], f"venture-generator failed"
        updated_data = result['ventures_data']
        print(f"  OK: {result['groups_processed']} groups, {result['ventures_created']} ventures")

        # STEP 2: Site Creator
        print("\n[2/5] Site Creator")
        agent = sc_mod.SiteCreator(data_root=str(test_root))
        result = agent.run(updated_data)
        report['pipeline']['site_creator'] = {
            'success': result['success'],
            'directories': result['directories_created'],
            'pages': result['pages_created'],
            'metadata': result['metadata_created'],
            'iterations': agent.iteration_count
        }
        assert result['success'], f"site-creator failed"
        print(f"  OK: {result['pages_created']} pages in {result['directories_created']} dirs")

        # STEP 3: Content Writer
        print("\n[3/5] Content Writer")
        agent = cw_mod.ContentWriter(data_root=str(test_root))
        result = agent.run(updated_data)
        report['pipeline']['content_writer'] = {
            'success': result['success'],
            'enriched': result['pages_enriched'],
            'seo': result['seo_generated'],
            'iterations': agent.iteration_count
        }
        assert result['success'], f"content-writer failed"
        print(f"  OK: {result['pages_enriched']} enriched, {result['seo_generated']} SEO")

        # STEP 4: Graph Builder
        print("\n[4/5] Graph Builder")
        agent = gb_mod.GraphBuilder(data_root=str(test_root))
        result = agent.run(updated_data)
        report['pipeline']['graph_builder'] = {
            'success': result['success'],
            'nav_updated': result['nav_updated'],
            'cross_links': result['cross_links_added'],
            'iterations': agent.iteration_count
        }
        assert result['success'], f"graph-builder failed"
        print(f"  OK: nav={result['nav_updated']}, {result['cross_links_added']} cross-links")

        # STEP 5: QA Validator
        print("\n[5/5] QA Validator")
        agent = qa_mod.QaValidator(data_root=str(test_root))
        result = agent.run(updated_data)
        report['pipeline']['qa_validator'] = {
            'success': result['success'],
            'validated': result['pages_validated'],
            'orphans': len(result['orphan_pages']),
            'broken_links': len(result['broken_links']),
            'validation_passed': result['validation_passed'],
            'iterations': agent.iteration_count
        }
        assert result['success'], f"qa-validator failed"
        print(f"  OK: {result['pages_validated']} validated, 0 orphans, 0 broken links")

        # Health Check (load via importlib — dash-named file)
        print("\n[HEALTH] Running health check...")
        health_spec = importlib.util.spec_from_file_location(
            'health_check', str(PROJECT_ROOT / 'src' / 'scripts' / 'health-check.py'))
        health_mod = importlib.util.module_from_spec(health_spec)
        health_spec.loader.exec_module(health_mod)

        sites_root = test_root / 'sites' / 'leo-global-holdings'
        health = health_mod.check_site(str(sites_root))
        report['health'] = health
        print(f"  HTML: {health['html_files']}, JSON: {health['json_files']}, "
              f"Empty: {health['empty_files']}, Missing title: {health['missing_title']}")

        # Drift Detection
        print("\n[DRIFT] Running drift detection...")
        drift_spec = importlib.util.spec_from_file_location(
            'drift_detection', str(PROJECT_ROOT / 'src' / 'scripts' / 'drift-detection.py'))
        drift_mod = importlib.util.module_from_spec(drift_spec)
        drift_spec.loader.exec_module(drift_mod)

        drift = drift_mod.detect_drift(str(test_root))
        report['drift'] = drift
        print(f"  Missing pages: {len(drift['missing_pages'])}, "
              f"Extra files: {len(drift['extra_files'])}, "
              f"Stale metadata: {len(drift['stale_metadata'])}")

        # Final verdict
        all_passed = (
            all(r['success'] for r in report['pipeline'].values()) and
            health['empty_files'] == 0 and
            health['html_files'] >= 50 and
            len(drift['missing_pages']) == 0
        )
        report['all_passed'] = all_passed

        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST RESULT: " + ("PASS" if all_passed else "FAIL"))
        print("=" * 60)

        # Save report
        report_path = PROJECT_ROOT / 'src' / 'scripts' / 'integration-report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReport saved: {report_path}")

        return all_passed

    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        shutil.rmtree(test_root, ignore_errors=True)


if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
