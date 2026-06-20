import { describe, it, expect } from 'vitest';
import { DeterministicSerializer } from '../deterministic.js';

describe('DeterministicSerializer — D1: Deterministic JSON serialization', () => {
  const serializer = new DeterministicSerializer();

  it('sorts object keys alphabetically', () => {
    const input = { z: 1, a: 2, m: 3 };
    const result = serializer.serialize(input);
    expect(result).toBe('{"a":2,"m":3,"z":1}');
  });

  it('sorts nested object keys', () => {
    const input = { b: { z: 1, a: 2 }, a: 1 };
    const result = serializer.serialize(input);
    expect(result).toBe('{"a":1,"b":{"a":2,"z":1}}');
  });

  it('sorts array elements by JSON representation', () => {
    const input = { items: ['c', 'a', 'b'] };
    const result = serializer.serialize(input);
    expect(result).toBe('{"items":["a","b","c"]}');
  });

  it('sorts arrays of objects by first key', () => {
    const input = [
      { id: 'c', name: 'C' },
      { id: 'a', name: 'A' },
      { id: 'b', name: 'B' },
    ];
    const result = serializer.serialize(input);
    const parsed = JSON.parse(result);
    expect(parsed[0].id).toBe('a');
    expect(parsed[1].id).toBe('b');
    expect(parsed[2].id).toBe('c');
  });

  it('produces same output for same content regardless of insertion order', () => {
    const a = { x: 1, y: 2, z: 3 };
    const b = { z: 3, x: 1, y: 2 };
    expect(serializer.serialize(a)).toBe(serializer.serialize(b));
  });

  it('handles dates as ISO strings', () => {
    const date = new Date('2025-01-15T10:30:00Z');
    const result = serializer.serialize(date);
    expect(result).toContain('2025-01-15');
  });

  it('handles null and undefined', () => {
    expect(serializer.serialize(null)).toBe('null');
    expect(serializer.serialize(undefined)).toBeUndefined();
  });

  it('handles numbers and strings', () => {
    expect(serializer.serialize(42)).toBe('42');
    expect(serializer.serialize('hello')).toBe('"hello"');
  });

  it('computes hash of serialized content', () => {
    const input = { name: 'test', version: 1 };
    const hash = serializer.hash(input);
    expect(hash).toMatch(/^[a-f0-9]{64}$/); // SHA-256 hex
  });

  it('same content produces same hash', () => {
    const a = { z: 1, a: 2 };
    const b = { a: 2, z: 1 };
    expect(serializer.hash(a)).toBe(serializer.hash(b));
  });

  it('different content produces different hash', () => {
    const a = { name: 'test' };
    const b = { name: 'test2' };
    expect(serializer.hash(a)).not.toBe(serializer.hash(b));
  });

  it('detects content drift', () => {
    const original = { name: 'test', data: [1, 2, 3] };
    const modified = { name: 'test', data: [1, 2, 4] };
    expect(serializer.hasDrift(original, modified)).toBe(true);
  });

  it('no drift for identical content', () => {
    const a = { name: 'test', data: [1, 2, 3] };
    const b = { data: [1, 2, 3], name: 'test' };
    expect(serializer.hasDrift(a, b)).toBe(false);
  });
});
