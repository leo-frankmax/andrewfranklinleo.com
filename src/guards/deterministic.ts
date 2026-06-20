import { createHash } from 'crypto';

export class DeterministicSerializer {
  serialize(value: unknown): string | undefined {
    if (value === undefined) return undefined;
    return JSON.stringify(value, this.replacer.bind(this));
  }

  private replacer(key: string, value: unknown): unknown {
    if (value instanceof Date) {
      return value.toISOString();
    }
    if (Array.isArray(value)) {
      return [...value].sort((a, b) => {
        const sa = JSON.stringify(a);
        const sb = JSON.stringify(b);
        return sa < sb ? -1 : sa > sb ? 1 : 0;
      });
    }
    if (value !== null && typeof value === 'object' && !(value instanceof Date)) {
      const sorted: Record<string, unknown> = {};
      for (const k of Object.keys(value).sort()) {
        sorted[k] = (value as Record<string, unknown>)[k];
      }
      return sorted;
    }
    return value;
  }

  hash(value: unknown): string {
    const serialized = this.serialize(value);
    return createHash('sha256').update(serialized || '').digest('hex');
  }

  hasDrift(a: unknown, b: unknown): boolean {
    return this.serialize(a) !== this.serialize(b);
  }
}
