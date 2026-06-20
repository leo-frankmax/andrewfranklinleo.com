import { readFileSync } from 'fs';
import { join } from 'path';

export interface ParsedOffering {
  name: string;
  slug: string;
  parentId: string;
}

export interface ParsedVenture {
  name: string;
  slug: string;
  mission: string;
  parentId: string;
  offerings: ParsedOffering[];
}

export interface ParsedGroup {
  name: string;
  slug: string;
  mission: string;
  parentId: string;
  ventures: ParsedVenture[];
}

export interface ParseResult {
  groups: ParsedGroup[];
  counts: {
    groups: number;
    ventures: number;
    totalOfferings: number;
  };
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

function toSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

export class ConversationParser {
  parseVentures(conversationText: string): ParseResult {
    const groups: ParsedGroup[] = [];
    const lines = conversationText.split('\n');
    let currentGroup: ParsedGroup | null = null;
    let currentVenture: ParsedVenture | null = null;

    for (const line of lines) {
      const trimmed = line.trim();

      // Match group headers: ## Group Name
      const groupMatch = trimmed.match(/^##\s+(.+?)(?:\s+Group)?$/i);
      if (groupMatch && !trimmed.startsWith('###')) {
        const name = groupMatch[1].replace(/\s+Group$/, '').trim();
        currentGroup = {
          name,
          slug: toSlug(name),
          mission: '',
          parentId: 'leo-global-holdings',
          ventures: [],
        };
        groups.push(currentGroup);
        currentVenture = null;
        continue;
      }

      // Match venture headers: ### Venture Name
      const ventureMatch = trimmed.match(/^###\s+(.+)$/);
      if (ventureMatch && currentGroup) {
        const name = ventureMatch[1].trim();
        currentVenture = {
          name,
          slug: toSlug(name),
          mission: '',
          parentId: currentGroup.slug,
          offerings: [],
        };
        currentGroup.ventures.push(currentVenture);
        continue;
      }

      // Match mission statements (quoted text after group/venture)
      if (trimmed.startsWith('"') && trimmed.endsWith('"') && currentGroup && !currentVenture) {
        currentGroup.mission = trimmed.slice(1, -1);
        continue;
      }

      // Match offering list items: - Offering Name
      const offeringMatch = trimmed.match(/^[-*]\s+(.+)$/);
      if (offeringMatch && currentVenture) {
        const name = offeringMatch[1].trim();
        currentVenture.offerings.push({
          name,
          slug: toSlug(name),
          parentId: currentVenture.slug,
        });
      }
    }

    const totalOfferings = groups.reduce(
      (sum, g) => sum + g.ventures.reduce((vSum, v) => vSum + v.offerings.length, 0),
      0
    );

    return {
      groups,
      counts: {
        groups: groups.length,
        ventures: groups.reduce((sum, g) => sum + g.ventures.length, 0),
        totalOfferings,
      },
    };
  }

  parseMission(text: string): string {
    return text
      .replace(/^["'"']/, '')
      .replace(/["'"']$/, '')
      .replace(/^\*\*Mission:\*\*\s*/, '')
      .trim();
  }

  parseStakeholders(text: string): string[] {
    const match = text.match(/\*\*Stakeholders:\*\*\s*(.+)$/i);
    if (!match) return [];
    return match[1].split(',').map(s => s.trim()).filter(Boolean);
  }

  validate(groups: ParsedGroup[]): ValidationResult {
    const errors: string[] = [];

    for (const group of groups) {
      if (!group.slug) errors.push(`Group '${group.name}' missing slug`);
      if (!group.mission) errors.push(`Group '${group.name}' missing mission`);
      if (!group.parentId) errors.push(`Group '${group.name}' missing parentId`);

      for (const venture of group.ventures) {
        if (!venture.slug) errors.push(`Venture '${venture.name}' missing slug`);
        if (!venture.parentId) errors.push(`Venture '${venture.name}' missing parentId`);

        for (const offering of venture.offerings) {
          if (!offering.slug) errors.push(`Offering '${offering.name}' missing slug`);
        }
      }
    }

    return { valid: errors.length === 0, errors };
  }

  parseFromFile(filePath: string): ParseResult {
    const content = readFileSync(filePath, 'utf-8');
    return this.parseVentures(content);
  }
}
