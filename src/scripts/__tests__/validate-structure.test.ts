import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'fs';
import { join } from 'path';
import { validateVenturesJson, validateSiteStructure } from '../validate-structure.js';
import { generateNav } from '../generate-nav.js';

const TMP_DIR = join(process.cwd(), '.test-tmp-validate');

beforeAll(() => {
  mkdirSync(TMP_DIR, { recursive: true });
});

afterAll(() => {
  rmSync(TMP_DIR, { recursive: true, force: true });
});

describe('validateVenturesJson', () => {
  it('rejects missing file', () => {
    const result = validateVenturesJson('/nonexistent');
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('not found');
  });

  it('rejects invalid JSON', () => {
    writeFileSync(join(TMP_DIR, 'ventures.json'), 'not json');
    const result = validateVenturesJson(TMP_DIR);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('not valid JSON');
  });

  it('validates correct structure', () => {
    const data = {
      conglomerate: { id: 'leo-global-holdings', name: 'Leo Global Holdings' },
      groups: [
        { id: 'frankmax', name: 'Frankmax', slug: 'frankmax', mission: 'Test', parentId: 'leo-global-holdings', type: 'group' },
      ],
      ventures: [
        { id: 'frankmax-talent', name: 'Frankmax Talent', slug: 'frankmax-talent', parentId: 'frankmax', type: 'venture',
          offerings: [{ id: 'executive-search', name: 'Executive Search', slug: 'executive-search', parentId: 'frankmax-talent' }],
        },
      ],
      counts: { groups: 1, ventures: 1, totalOfferings: 1 },
    };
    writeFileSync(join(TMP_DIR, 'ventures.json'), JSON.stringify(data));
    const result = validateVenturesJson(TMP_DIR);
    expect(result.valid).toBe(true);
    expect(result.errors.length).toBe(0);
  });

  it('detects wrong parentId', () => {
    const data = {
      conglomerate: { id: 'leo-global-holdings', name: 'Leo Global Holdings' },
      groups: [],
      ventures: [
        { id: 'test', name: 'Test', slug: 'test', parentId: 'nonexistent', type: 'venture', offerings: [] },
      ],
    };
    writeFileSync(join(TMP_DIR, 'ventures.json'), JSON.stringify(data));
    const result = validateVenturesJson(TMP_DIR);
    expect(result.valid).toBe(false);
  });
});

describe('validateSiteStructure', () => {
  it('warns when sites/ missing', () => {
    const result = validateSiteStructure('/nonexistent');
    expect(result.warnings.length).toBeGreaterThan(0);
  });
});

describe('generateNav', () => {
  it('generates nav from ventures.json', () => {
    const data = {
      groups: [
        { id: 'frankmax', name: 'Frankmax', type: 'group', mission: 'Empowering', parentId: 'leo-global-holdings' },
        { id: 'leo-technologies', name: 'Leo Technologies', type: 'strategic-vertical', parentId: 'leo-global-holdings' },
      ],
      ventures: [
        { id: 'frankmax-talent', name: 'Frankmax Talent', parentId: 'frankmax' },
        { id: 'frankmax-learning', name: 'Frankmax Learning', parentId: 'frankmax' },
      ],
    };
    const path = join(TMP_DIR, 'nav-test.json');
    writeFileSync(path, JSON.stringify(data));
    const nav = generateNav(path);
    expect(nav.groups.length).toBe(1);
    expect(nav.groups[0].ventures.length).toBe(2);
    expect(nav.strategicVerticals.length).toBe(1);
  });
});
