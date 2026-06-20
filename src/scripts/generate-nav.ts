import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

interface NavItem {
  label: string;
  url: string;
  slug: string;
}

interface NavGroup extends NavItem {
  mission: string;
  ventures: NavItem[];
}

interface NavData {
  home: NavItem;
  groups: NavGroup[];
  strategicVerticals: NavItem[];
}

export function generateNav(venturesJsonPath: string): NavData {
  const data = JSON.parse(readFileSync(venturesJsonPath, 'utf-8'));

  const groups: NavGroup[] = (data.groups || [])
    .filter((g: any) => g.type === 'group')
    .map((g: any) => ({
      label: g.name,
      url: `/${g.id}/`,
      slug: g.id,
      mission: g.mission || '',
      ventures: (data.ventures || [])
        .filter((v: any) => v.parentId === g.id)
        .map((v: any) => ({
          label: v.name,
          url: `/${g.id}/${v.id}/`,
          slug: v.id,
        })),
    }));

  const strategicVerticals: NavItem[] = (data.groups || [])
    .filter((g: any) => g.type === 'strategic-vertical')
    .map((g: any) => ({
      label: g.name,
      url: `/${g.id}/`,
      slug: g.id,
    }));

  return {
    home: { label: 'Home', url: '/', slug: '' },
    groups,
    strategicVerticals,
  };
}

export function generateNavJson(projectRoot: string): void {
  const venturesPath = join(projectRoot, 'ventures.json');
  const outputPath = join(projectRoot, 'docs', 'nav.json');

  if (!existsSync(venturesPath)) {
    throw new Error('ventures.json not found');
  }

  const nav = generateNav(venturesPath);
  const dir = join(projectRoot, 'docs');
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
  writeFileSync(outputPath, JSON.stringify(nav, null, 2), 'utf-8');
  console.log(`Generated nav.json with ${nav.groups.length} groups`);
}

// CLI entry point
if (process.argv[1] && process.argv[1].endsWith('generate-nav.ts')) {
  const projectRoot = process.argv[2] || process.cwd();
  generateNavJson(projectRoot);
}
