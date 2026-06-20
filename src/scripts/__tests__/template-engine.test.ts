import { describe, it, expect } from 'vitest';
import { TemplateEngine, TemplateContext } from '../template-engine.js';

describe('TemplateEngine', () => {
  const engine = new TemplateEngine();

  describe('renderTemplate', () => {
    it('renders basic template with variables', () => {
      const template = '<h1>{{title}}</h1><p>{{description}}</p>';
      const result = engine.renderTemplate(template, {
        title: 'Hello World',
        description: 'A test page',
      });
      expect(result).toBe('<h1>Hello World</h1><p>A test page</p>');
    });

    it('renders nested variables', () => {
      const template = '<h1>{{venture.name}}</h1>';
      const result = engine.renderTemplate(template, {
        venture: { name: 'Frankmax Talent' },
      });
      expect(result).toBe('<h1>Frankmax Talent</h1>');
    });

    it('handles missing variables gracefully', () => {
      const template = '<h1>{{missing}}</h1>';
      const result = engine.renderTemplate(template, {});
      expect(result).toBe('<h1></h1>');
    });
  });

  renderBreadcrumbs: describe('renderBreadcrumbs', () => {
    it('renders breadcrumb trail', () => {
      const crumbs = [
        { label: 'Home', url: '/' },
        { label: 'Frankmax', url: '/frankmax/' },
        { label: 'Frankmax Talent', url: '/frankmax/frankmax-talent/' },
      ];
      const result = engine.renderBreadcrumbs(crumbs);
      expect(result).toContain('Home');
      expect(result).toContain('Frankmax');
      expect(result).toContain('Frankmax Talent');
      expect(result).toContain('/');
    });

    it('marks last item as current page', () => {
      const crumbs = [
        { label: 'Home', url: '/' },
        { label: 'Current', url: '/current/' },
      ];
      const result = engine.renderBreadcrumbs(crumbs);
      expect(result).toContain('aria-current');
    });
  }),

  describe('renderNav', () => {
    it('renders global navigation', () => {
      const nav = {
        home: { label: 'Home', url: '/' },
        groups: [
          { label: 'Frankmax', url: '/frankmax/', mission: 'Empowering Every Professional', ventures: [] },
        ],
        strategicVerticals: [
          { label: 'Leo Technologies', url: '/leo-technologies/' },
        ],
      };
      const result = engine.renderNav(nav, '/');
      expect(result).toContain('Frankmax');
      expect(result).toContain('Leo Technologies');
    });
  });

  describe('renderCard', () => {
    it('renders a card component', () => {
      const result = engine.renderCard({
        title: 'Test Card',
        description: 'Card description',
        url: '/test/',
        icon: 'building',
      });
      expect(result).toContain('Test Card');
      expect(result).toContain('Card description');
      expect(result).toContain('/test/');
    });
  });

  describe('renderGrid', () => {
    it('renders grid of cards', () => {
      const items = [
        { title: 'A', description: 'Desc A', url: '/a/', icon: 'a' },
        { title: 'B', description: 'Desc B', url: '/b/', icon: 'b' },
      ];
      const result = engine.renderGrid(items);
      expect(result).toContain('A');
      expect(result).toContain('B');
      expect(result).toContain('grid');
    });
  });

  describe('sanitize', () => {
    it('strips script tags', () => {
      const result = engine.sanitize('<p>safe</p><script>alert(1)</script>');
      expect(result).not.toContain('<script>');
      expect(result).toContain('safe');
    });
  });
});
