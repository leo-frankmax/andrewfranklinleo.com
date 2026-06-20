import { resolve, normalize, relative } from 'path';

export interface PathGuardConfig {
  writeRoots: string[];
  readRoots: string[];
  blockTraversal: boolean;
}

export const WRITE_ROOTS = [
  'sites',
  'docs',
  'ventures.json',
];

export class PathGuard {
  private config: PathGuardConfig;

  constructor(config: PathGuardConfig) {
    this.config = config;
  }

  private normalizePath(p: string): string {
    return normalize(p).replace(/\\/g, '/');
  }

  private hasTraversal(p: string): boolean {
    if (!this.config.blockTraversal) return false;
    const normalized = this.normalizePath(p);
    if (normalized.startsWith('/') || /^[A-Z]:/i.test(normalized)) return true;
    if (normalized.startsWith('~')) return true;
    if (normalized.includes('..')) return true;
    if (normalized.includes('./') || normalized.includes('/.')) return true;
    return false;
  }

  private isInRoots(p: string, roots: string[]): boolean {
    const normalized = this.normalizePath(p);
    return roots.some(root => {
      const normalizedRoot = this.normalizePath(root);
      return normalized === normalizedRoot || normalized.startsWith(normalizedRoot + '/');
    });
  }

  isWriteAllowed(p: string): boolean {
    if (this.hasTraversal(p)) return false;
    return this.isInRoots(p, this.config.writeRoots);
  }

  isReadAllowed(p: string): boolean {
    if (this.hasTraversal(p)) return false;
    const blocked = ['.env', '.env.local', '.env.production', '.git'];
    const normalized = this.normalizePath(p);
    if (blocked.some(b => normalized === b || normalized.startsWith(b + '/'))) return false;
    if (normalized.startsWith('docker/secrets/')) return false;
    return this.isInRoots(p, this.config.readRoots);
  }

  validate(operation: 'read' | 'write', p: string): { allowed: boolean; reason?: string } {
    const normalized = this.normalizePath(p);

    if (this.hasTraversal(p)) {
      return { allowed: false, reason: `Path traversal detected: ${normalized}` };
    }

    if (operation === 'write') {
      if (!this.isWriteAllowed(p)) {
        return { allowed: false, reason: `Write not allowed to: ${normalized}. Allowed roots: ${this.config.writeRoots.join(', ')}` };
      }
    } else {
      if (!this.isReadAllowed(p)) {
        return { allowed: false, reason: `Read not allowed to: ${normalized}` };
      }
    }

    return { allowed: true };
  }
}
