import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export function validateVenturesJson(projectRoot: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const filePath = join(projectRoot, 'ventures.json');

  if (!existsSync(filePath)) {
    return { valid: false, errors: ['ventures.json not found'], warnings: [] };
  }

  let data: any;
  try {
    data = JSON.parse(readFileSync(filePath, 'utf-8'));
  } catch (e) {
    return { valid: false, errors: ['ventures.json is not valid JSON'], warnings: [] };
  }

  // Check root structure
  if (!data.conglomerate) errors.push('Missing conglomerate');
  if (!data.groups || !Array.isArray(data.groups)) errors.push('Missing or invalid groups array');
  if (!data.ventures || !Array.isArray(data.ventures)) errors.push('Missing or invalid ventures array');
  if (!data.counts) warnings.push('Missing counts object');

  // Validate groups
  if (Array.isArray(data.groups)) {
    for (const group of data.groups) {
      if (!group.id) errors.push(`Group missing id: ${JSON.stringify(group)}`);
      if (!group.name) errors.push(`Group '${group.id}' missing name`);
      if (!group.slug) errors.push(`Group '${group.id}' missing slug`);
      if (!group.mission) warnings.push(`Group '${group.id}' missing mission`);
      if (group.parentId !== 'leo-global-holdings') {
        errors.push(`Group '${group.id}' has wrong parentId: ${group.parentId}`);
      }
    }
  }

  // Validate ventures
  if (Array.isArray(data.ventures)) {
    const groupIds = new Set((data.groups || []).map((g: any) => g.id));
    const ventureIds = new Set<string>();

    for (const venture of data.ventures) {
      if (!venture.id) errors.push(`Venture missing id`);
      if (!venture.name) errors.push(`Venture '${venture.id}' missing name`);
      if (!venture.slug) errors.push(`Venture '${venture.id}' missing slug`);
      if (!venture.parentId) errors.push(`Venture '${venture.id}' missing parentId`);
      if (venture.parentId && !groupIds.has(venture.parentId) && !ventureIds.has(venture.parentId)) {
        errors.push(`Venture '${venture.id}' parentId '${venture.parentId}' not found in groups or ventures`);
      }
      ventureIds.add(venture.id);

      // Validate offerings
      if (Array.isArray(venture.offerings)) {
        for (const offering of venture.offerings) {
          if (!offering.id) errors.push(`Offering in '${venture.id}' missing id`);
          if (!offering.name) errors.push(`Offering '${offering.id}' in '${venture.id}' missing name`);
          if (!offering.slug) errors.push(`Offering '${offering.id}' in '${venture.id}' missing slug`);
          if (offering.parentId !== venture.id) {
            errors.push(`Offering '${offering.id}' has wrong parentId: ${offering.parentId}`);
          }
        }
      }
    }

    // Count validation
    if (data.counts) {
      if (data.counts.groups !== data.groups.length) {
        warnings.push(`Group count mismatch: ${data.counts.groups} vs ${data.groups.length}`);
      }
      if (data.counts.ventures !== data.ventures.length) {
        warnings.push(`Venture count mismatch: ${data.counts.ventures} !== ${data.ventures.length}`);
      }
    }
  }

  return { valid: errors.length === 0, errors, warnings };
}

export function validateSiteStructure(projectRoot: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const sitesDir = join(projectRoot, 'sites');

  if (!existsSync(sitesDir)) {
    warnings.push('sites/ directory not found (expected after site-creator agent runs)');
  }

  return { valid: errors.length === 0, errors, warnings };
}

// CLI entry point
if (process.argv[1] && process.argv[1].endsWith('validate-structure.ts')) {
  const projectRoot = process.argv[2] || process.cwd();
  console.log('Validating ventures.json...');
  const venturesResult = validateVenturesJson(projectRoot);

  if (venturesResult.errors.length > 0) {
    console.error('ERRORS:');
    venturesResult.errors.forEach(e => console.error(`  - ${e}`));
  }
  if (venturesResult.warnings.length > 0) {
    console.warn('WARNINGS:');
    venturesResult.warnings.forEach(w => console.warn(`  - ${w}`));
  }

  if (venturesResult.valid) {
    console.log('ventures.json: VALID');
  } else {
    console.error('ventures.json: INVALID');
    process.exit(1);
  }

  console.log('\nValidating site structure...');
  const siteResult = validateSiteStructure(projectRoot);
  if (siteResult.warnings.length > 0) {
    siteResult.warnings.forEach(w => console.warn(`  - ${w}`));
  }
  if (siteResult.valid) {
    console.log('site structure: VALID');
  }
}
