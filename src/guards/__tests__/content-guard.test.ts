import { describe, it, expect } from 'vitest';
import { ContentGuard } from '../content-guard.js';

describe('ContentGuard — C6: HTML sanitization + output schema validation', () => {
  const guard = new ContentGuard();

  describe('HTML SANITIZATION', () => {
    it('strips <script> tags', () => {
      const result = guard.sanitizeHtml('<p>Hello</p><script>alert("xss")</script><p>World</p>');
      expect(result).not.toContain('<script>');
      expect(result).toContain('Hello');
      expect(result).toContain('World');
    });

    it('strips <iframe> tags', () => {
      const result = guard.sanitizeHtml('<iframe src="evil.com"></iframe>');
      expect(result).not.toContain('<iframe');
    });

    it('strips on* event handlers', () => {
      const result = guard.sanitizeHtml('<img src="x" onerror="alert(1)">');
      expect(result).not.toContain('onerror');
    });

    it('strips javascript: URLs', () => {
      const result = guard.sanitizeHtml('<a href="javascript:alert(1)">click</a>');
      expect(result).not.toContain('javascript:');
    });

    it('allows safe HTML elements', () => {
      const result = guard.sanitizeHtml(
        '<h1>Title</h1><p>Text <strong>bold</strong> <a href="https://example.com">link</a></p>'
      );
      expect(result).toContain('<h1>');
      expect(result).toContain('<p>');
      expect(result).toContain('<strong>');
      expect(result).toContain('<a');
    });

    it('preserves safe attributes (class, id, href)', () => {
      const result = guard.sanitizeHtml('<div class="container" id="main">content</div>');
      expect(result).toContain('class="container"');
      expect(result).toContain('id="main"');
    });

    it('strips style attributes (potential CSS injection)', () => {
      const result = guard.sanitizeHtml('<div style="background: url(javascript:alert(1))">x</div>');
      expect(result).not.toContain('style=');
    });

    it('handles malformed HTML gracefully', () => {
      const result = guard.sanitizeHtml('<p>unclosed<p>another');
      expect(result).toBeDefined();
    });
  });

  describe('OUTPUT SCHEMA VALIDATION', () => {
    const validPageSchema = {
      type: 'object',
      required: ['path', 'title', 'description', 'content', 'meta', 'layout'],
      properties: {
        path: { type: 'string' },
        title: { type: 'string' },
        description: { type: 'string' },
        content: { type: 'string' },
        meta: { type: 'object' },
        layout: { type: 'string' },
      },
    };

    it('validates correct page output', () => {
      const result = guard.validateSchema({
        path: 'index.html',
        title: 'Leo Global Holdings',
        description: 'Conglomerate overview',
        content: '<h1>Leo Global Holdings</h1>',
        meta: { ogImage: 'og.png' },
        layout: 'conglomerate',
      });
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('rejects missing required fields', () => {
      const result = guard.validateSchema({ path: 'index.html' }, validPageSchema);
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('rejects wrong types', () => {
      const result = guard.validateSchema({
        path: 123, // should be string
        title: 'Test',
        description: 'Test',
        content: 'Test',
        meta: 'not-an-object',
        layout: 'default',
      }, validPageSchema);
      expect(result.valid).toBe(false);
    });

    it('validates venture schema', () => {
      const ventureSchema = {
        type: 'object',
        required: ['id', 'name', 'type', 'parentId', 'offerings'],
      };

      const validVenture = {
        id: 'frankmax',
        name: 'Frankmax',
        type: 'venture',
        parentId: 'leo-global-holdings',
        offerings: [],
      };

      const result = guard.validateSchema(validVenture, ventureSchema);
      expect(result.valid).toBe(true);
    });
  });

  describe('CONTENT LENGTH LIMITS', () => {
    it('rejects content exceeding max length', () => {
      const result = guard.validateContentLength('x'.repeat(100001), 100000);
      expect(result.valid).toBe(false);
      expect(result.reason).toContain('exceeds');
    });

    it('accepts content within limits', () => {
      const result = guard.validateContentLength('short content', 100000);
      expect(result.valid).toBe(true);
    });
  });
});
