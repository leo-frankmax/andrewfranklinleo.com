#!/usr/bin/env python3
"""End-to-end integration test: runs the full pipeline locally."""

import sys
import json
import os
import tempfile
import shutil
import importlib.util
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_agent_module(agent_name):
    """Load agent module from dash-named directory."""
    agent_path = PROJECT_ROOT / 'docker' / 'agents' / agent_name / 'agent.py'
    spec = importlib.util.spec_from_file_location(agent_name.replace('-', '_'), str(agent_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load agents via importlib (dash-named directories)
vg_mod = load_agent_module('venture-generator')
sc_mod = load_agent_module('site-creator')
cw_mod = load_agent_module('content-writer')
gb_mod = load_agent_module('graph-builder')
qa_mod = load_agent_module('qa-validator')

VentureGenerator = vg_mod.VentureGenerator
SiteCreator = sc_mod.SiteCreator
ContentWriter = cw_mod.ContentWriter
GraphBuilder = gb_mod.GraphBuilder
QaValidator = qa_mod.QaValidator


def run_pipeline():
    print("=" * 60)
    print("ANDREW FRANKLIN LEO CMS - INTEGRATION TEST")
    print("=" * 60)

    # Use a temp directory for the test run
    test_root = Path(tempfile.mkdtemp(prefix='afl-integration-'))
    print(f"\nTest directory: {test_root}")

    try:
        # Load ventures.json
        ventures_path = PROJECT_ROOT / 'ventures.json'
        with open(ventures_path) as f:
            original_data = json.load(f)

        data = json.loads(json.dumps(original_data))  # deep copy

        # =========================================================
        # STEP 1: Venture Generator
        # =========================================================
        print("\n" + "=" * 60)
        print("STEP 1: Venture Generator")
        print("=" * 60)

        vg_agent = VentureGenerator(data_root=str(test_root))
        vg_result = vg_agent.run(data)

        print(f"  Groups processed: {vg_result['groups_processed']}")
        print(f"  Ventures created: {vg_result['ventures_created']}")
        print(f"  Offerings created: {vg_result['offerings_created']}")
        print(f"  Iterations: {vg_agent.iteration_count}")
        print(f"  Success: {vg_result['success']}")

        assert vg_result['success'], f"venture-generator failed: {vg_result['errors']}"
        assert vg_result['groups_processed'] >= 8, f"Expected >= 8 groups, got {vg_result['groups_processed']}"
        assert vg_result['ventures_created'] >= 30, f"Expected >= 30 ventures, got {vg_result['ventures_created']}"

        # Validate output
        validation = vg_agent.validate_output(vg_result['ventures_data'])
        print(f"  Validation: {validation}")
        assert validation['valid'], f"Validation failed: {validation['errors']}"

        # Save updated ventures.json
        updated_data = vg_result['ventures_data']

        # =========================================================
        # STEP 2: Site Creator
        # =========================================================
        print("\n" + "=" * 60)
        print("STEP 2: Site Creator")
        print("=" * 60)

        sc_agent = SiteCreator(data_root=str(test_root))
        sc_result = sc_agent.run(updated_data)

        print(f"  Directories created: {sc_result['directories_created']}")
        print(f"  Pages created: {sc_result['pages_created']}")
        print(f"  Metadata created: {sc_result['metadata_created']}")
        print(f"  Iterations: {sc_agent.iteration_count}")
        print(f"  Success: {sc_result['success']}")

        assert sc_result['success'], f"site-creator failed: {sc_result['errors']}"
        assert sc_result['pages_created'] >= 50, f"Expected >= 50 pages, got {sc_result['pages_created']}"

        # Verify key files exist
        sites_root = test_root / 'sites' / 'leo-global-holdings'
        assert (sites_root / 'index.html').exists(), "Missing conglomerate portal"
        assert (sites_root / 'frankmax' / 'index.html').exists(), "Missing frankmax group page"
        assert (sites_root / 'frankmax' / 'frankmax-talent' / 'index.html').exists(), "Missing frankmax-talent venture page"
        print("  Key files verified: OK")

        # =========================================================
        # STEP 3: Content Writer
        # =========================================================
        print("\n" + "=" * 60)
        print("STEP 3: Content Writer")
        print("=" * 60)

        cw_agent = ContentWriter(data_root=str(test_root))
        cw_result = cw_agent.run(updated_data)

        print(f"  Pages enriched: {cw_result['pages_enriched']}")
        print(f"  SEO generated: {cw_result['seo_generated']}")
        print(f"  Iterations: {cw_agent.iteration_count}")
        print(f"  Success: {cw_result['success']}")

        assert cw_result['success'], f"content-writer failed: {cw_result['errors']}"

        # Verify enriched content
        offering_page = sites_root / 'frankmax' / 'frankmax-talent' / 'executive-search' / 'index.html'
        if offering_page.exists():
            content = offering_page.read_text()
            assert 'Executive Search' in content, "Offering name missing from enriched page"
            print("  Content enrichment verified: OK")

        # =========================================================
        # STEP 4: Graph Builder
        # =========================================================
        print("\n" + "=" * 60)
        print("STEP 4: Graph Builder")
        print("=" * 60)

        gb_agent = GraphBuilder(data_root=str(test_root))
        gb_result = gb_agent.run(updated_data)

        print(f"  Nav updated: {gb_result['nav_updated']}")
        print(f"  Cross-links added: {gb_result['cross_links_added']}")
        print(f"  Metadata updated: {gb_result['metadata_updated']}")
        print(f"  Iterations: {gb_agent.iteration_count}")
        print(f"  Success: {gb_result['success']}")

        assert gb_result['success'], f"graph-builder failed: {gb_result['errors']}"
        assert gb_result['nav_updated'], "Global nav not created"

        # Verify nav file
        nav_path = sites_root / 'global-nav.json'
        assert nav_path.exists(), "global-nav.json missing"
        nav = json.loads(nav_path.read_text())
        assert len(nav['groups']) >= 4, f"Expected >= 4 groups in nav, got {len(nav['groups'])}"
        print("  Navigation verified: OK")

        # =========================================================
        # STEP 5: QA Validator
        # =========================================================
        print("\n" + "=" * 60)
        print("STEP 5: QA Validator")
        print("=" * 60)

        qa_agent = QaValidator(data_root=str(test_root))
        qa_result = qa_agent.run(updated_data)

        print(f"  Pages validated: {qa_result['pages_validated']}")
        print(f"  Orphan pages: {len(qa_result['orphan_pages'])}")
        print(f"  Broken links: {len(qa_result['broken_links'])}")
        print(f"  Missing metadata: {len(qa_result['missing_metadata'])}")
        print(f"  Validation passed: {qa_result['validation_passed']}")
        print(f"  Iterations: {qa_agent.iteration_count}")
        print(f"  Success: {qa_result['success']}")

        assert qa_result['success'], f"qa-validator failed: {qa_result['errors']}"

        # =========================================================
        # SUMMARY
        # =========================================================
        print("\n" + "=" * 60)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 60)

        total_pages = sc_result['pages_created']
        total_dirs = sc_result['directories_created']
        total_enriched = cw_result['pages_enriched']
        total_orphans = len(qa_result['orphan_pages'])
        total_broken = len(qa_result['broken_links'])

        print(f"  Total directories: {total_dirs}")
        print(f"  Total pages: {total_pages}")
        print(f"  Pages enriched: {total_enriched}")
        print(f"  Orphan pages: {total_orphans}")
        print(f"  Broken links: {total_broken}")
        print(f"  Navigation: {'OK' if gb_result['nav_updated'] else 'FAIL'}")
        print(f"  QA passed: {'YES' if qa_result['validation_passed'] else 'NO'}")

        # Count actual files on disk
        html_files = list(sites_root.rglob('index.html'))
        json_files = list(sites_root.rglob('_*.json'))
        print(f"  HTML files on disk: {len(html_files)}")
        print(f"  JSON metadata files: {len(json_files)}")

        # Expectations
        assert total_orphans == 0, f"Found {total_orphans} orphan pages"
        assert total_broken == 0, f"Found {total_broken} broken links"
        assert len(html_files) >= 50, f"Expected >= 50 HTML files, got {len(html_files)}"

        print("\n  ALL CHECKS PASSED")
        return True

    except Exception as e:
        print(f"\n  INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        shutil.rmtree(test_root, ignore_errors=True)
        print(f"\nCleaned up: {test_root}")


if __name__ == '__main__':
    success = run_pipeline()
    sys.exit(0 if success else 1)
