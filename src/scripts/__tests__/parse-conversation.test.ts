import { describe, it, expect } from 'vitest';
import { ConversationParser, ParsedVenture, ParsedGroup } from '../parse-conversation.js';

describe('ConversationParser', () => {
  const sampleConversation = `
# Turn 1
**Andrew Franklin Leo:** I want to build an empire. Let me tell you about my vision.

**ChatGPT:** Tell me more about your vision.

# Turn 8
**Andrew Franklin Leo:** Here's the empire structure:

## Frankmax Group
"Empowering Every Professional"

### Frankmax Talent
Recruit and develop world-class professionals.
- Recruitment
- Executive Search
- Workforce Management
- Talent Intelligence
- Career Development

### Frankmax Learning
Continuous capability enhancement.
- Universities
- Academies
- Certifications
- Skill Development
- Lifelong Learning

## Virginbay Group
"Powering Global Commerce"

### Virginbay Marketplace
Enable every transaction.
- Consumer Commerce
- B2B Commerce
- Digital Commerce
- Global Trade
`;

  const parser = new ConversationParser();

  describe('parseVentures', () => {
    it('extracts groups from conversation', () => {
      const result = parser.parseVentures(sampleConversation);
      expect(result.groups.length).toBeGreaterThanOrEqual(2);
      expect(result.groups[0].name).toContain('Frankmax');
      expect(result.groups[1].name).toContain('Virginbay');
    });

    it('extracts ventures within groups', () => {
      const result = parser.parseVentures(sampleConversation);
      const frankmax = result.groups.find(g => g.name.includes('Frankmax'));
      expect(frankmax).toBeDefined();
      expect(frankmax!.ventures.length).toBeGreaterThanOrEqual(2);
    });

    it('extracts offerings within ventures', () => {
      const result = parser.parseVentures(sampleConversation);
      const frankmax = result.groups.find(g => g.name.includes('Frankmax'));
      const talent = frankmax!.ventures.find(v => v.name.includes('Talent'));
      expect(talent).toBeDefined();
      expect(talent!.offerings.length).toBeGreaterThanOrEqual(4);
    });

    it('generates slugs from names', () => {
      const result = parser.parseVentures(sampleConversation);
      const frankmax = result.groups.find(g => g.name.includes('Frankmax'));
      expect(frankmax!.slug).toBe('frankmax');
    });

    it('counts total offerings', () => {
      const result = parser.parseVentures(sampleConversation);
      expect(result.counts.totalOfferings).toBeGreaterThanOrEqual(9);
    });
  });

  describe('parseMission', () => {
    it('extracts mission statements', () => {
      const result = parser.parseMission('"Empowering Every Professional"');
      expect(result).toBe('Empowering Every Professional');
    });

    it('strips quotes and formatting', () => {
      const result = parser.parseMission('**Mission:** Build the future');
      expect(result).toBe('Build the future');
    });
  });

  describe('parseStakeholders', () => {
    it('extracts stakeholder list', () => {
      const result = parser.parseStakeholders('**Stakeholders:** Students, Professionals, Entrepreneurs');
      expect(result).toEqual(['Students', 'Professionals', 'Entrepreneurs']);
    });
  });

  describe('validate', () => {
    it('validates correct structure', () => {
      const data: ParsedGroup[] = [{
        name: 'Test Group',
        slug: 'test-group',
        mission: 'Test mission',
        parentId: 'leo-global-holdings',
        ventures: [{
          name: 'Test Venture',
          slug: 'test-venture',
          mission: 'Test venture mission',
          parentId: 'test-group',
          offerings: [{
            name: 'Test Offering',
            slug: 'test-offering',
            parentId: 'test-venture',
          }],
        }],
      }];
      const result = parser.validate(data);
      expect(result.valid).toBe(true);
      expect(result.errors.length).toBe(0);
    });

    it('detects missing slugs', () => {
      const data: ParsedGroup[] = [{
        name: 'Test',
        slug: '',
        mission: 'm',
        parentId: 'leo-global-holdings',
        ventures: [],
      }];
      const result = parser.validate(data);
      expect(result.valid).toBe(false);
    });
  });
});
