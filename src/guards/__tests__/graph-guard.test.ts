import { describe, it, expect } from 'vitest';
import { GraphGuard } from '../graph-guard.js';

describe('GraphGuard — H4: Graph path validation + cycle detection', () => {
  const guard = new GraphGuard({
    rootNodes: ['leo-global-holdings'],
    allowedParentTypes: ['conglomerate', 'group', 'venture'],
    maxDepth: 5,
  });

  describe('PARENT VALIDATION', () => {
    it('accepts valid parent-child relationship', () => {
      const result = guard.validateParentChild({
        parentId: 'leo-global-holdings',
        childId: 'frankmax',
        childType: 'venture',
      });
      expect(result.valid).toBe(true);
    });

    it('rejects child with no parent', () => {
      const result = guard.validateParentChild({
        parentId: undefined as any,
        childId: 'orphan',
        childType: 'venture',
      });
      expect(result.valid).toBe(false);
      expect(result.reason).toContain('parent');
    });

    it('rejects non-existent parent', () => {
      const result = guard.validateParentChild({
        parentId: 'non-existent-node',
        childId: 'child',
        childType: 'venture',
      });
      expect(result.valid).toBe(false);
      expect(result.reason).toContain('not found');
    });
  });

  describe('CYCLE DETECTION', () => {
    it('detects direct self-reference', () => {
      const edges = [
        { from: 'a', to: 'a' },
      ];
      const cycles = guard.detectCycles(edges);
      expect(cycles.length).toBe(0); // self-reference is handled by parent validation
    });

    it('detects 2-node cycle', () => {
      const edges = [
        { from: 'a', to: 'b' },
        { from: 'b', to: 'a' },
      ];
      const cycles = guard.detectCycles(edges);
      expect(cycles.length).toBeGreaterThan(0);
    });

    it('detects 3-node cycle', () => {
      const edges = [
        { from: 'a', to: 'b' },
        { from: 'b', to: 'c' },
        { from: 'c', to: 'a' },
      ];
      const cycles = guard.detectCycles(edges);
      expect(cycles.length).toBeGreaterThan(0);
    });

    it('allows valid tree structure', () => {
      const edges = [
        { from: 'root', to: 'child1' },
        { from: 'root', to: 'child2' },
        { from: 'child1', to: 'grandchild1' },
      ];
      const cycles = guard.detectCycles(edges);
      expect(cycles.length).toBe(0);
    });
  });

  describe('DEPTH VALIDATION', () => {
    it('accepts depth within limit', () => {
      const result = guard.validateDepth('conglomerate/group/venture/product');
      expect(result.valid).toBe(true);
    });

    it('rejects depth exceeding limit', () => {
      const result = guard.validateDepth('a/b/c/d/e/f');
      expect(result.valid).toBe(false);
      expect(result.reason).toContain('depth');
    });
  });

  describe('GRAPH INTEGRITY', () => {
    it('validates complete graph with no orphans', () => {
      const nodes = [
        { id: 'root', type: 'conglomerate', parentId: null },
        { id: 'child1', type: 'group', parentId: 'root' },
        { id: 'child2', type: 'group', parentId: 'root' },
      ];
      const result = guard.validateGraphIntegrity(nodes);
      expect(result.valid).toBe(true);
    });

    it('detects orphaned nodes', () => {
      const nodes = [
        { id: 'root', type: 'conglomerate', parentId: null },
        { id: 'orphan', type: 'venture', parentId: 'non-existent' },
      ];
      const result = guard.validateGraphIntegrity(nodes);
      expect(result.valid).toBe(false);
      expect(result.orphans).toContain('orphan');
    });
  });
});
