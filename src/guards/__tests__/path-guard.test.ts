import { describe, it, expect } from 'vitest';
import { PathGuard, WRITE_ROOTS } from '../path-guard.js';

describe('PathGuard — C1: Path allowlist enforcement', () => {
  const guard = new PathGuard({
    writeRoots: WRITE_ROOTS,
    readRoots: ['sites', 'docs', 'ventures.json', 'memory'],
    blockTraversal: true,
  });

  describe('WRITE: allowed paths', () => {
    it('allows writing to sites/leo-global-holdings/**', () => {
      expect(guard.isWriteAllowed('sites/leo-global-holdings/frankmax/index.html')).toBe(true);
    });

    it('allows writing to docs/**', () => {
      expect(guard.isWriteAllowed('docs/index.html')).toBe(true);
      expect(guard.isWriteAllowed('docs/frankmax/frankmax-talent/index.html')).toBe(true);
    });

    it('allows writing to ventures.json', () => {
      expect(guard.isWriteAllowed('ventures.json')).toBe(true);
    });
  });

  describe('WRITE: blocked paths', () => {
    it('blocks writing to memory/', () => {
      expect(guard.isWriteAllowed('memory/secret.md')).toBe(false);
    });

    it('blocks writing to .github/', () => {
      expect(guard.isWriteAllowed('.github/workflows/test.yml')).toBe(false);
    });

    it('blocks writing to docker/', () => {
      expect(guard.isWriteAllowed('docker/compose.yml')).toBe(false);
    });

    it('blocks writing to src/', () => {
      expect(guard.isWriteAllowed('src/guards/test.ts')).toBe(false);
    });

    it('blocks writing to package.json', () => {
      expect(guard.isWriteAllowed('package.json')).toBe(false);
    });

    it('blocks writing to node_modules/', () => {
      expect(guard.isWriteAllowed('node_modules/pkg/index.js')).toBe(false);
    });
  });

  describe('PATH TRAVERSAL: blocked', () => {
    it('blocks ../ escape from sites/', () => {
      expect(guard.isWriteAllowed('sites/../package.json')).toBe(false);
    });

    it('blocks ../../ escape', () => {
      expect(guard.isWriteAllowed('sites/../../etc/passwd')).toBe(false);
    });

    it('blocks absolute paths', () => {
      expect(guard.isWriteAllowed('/etc/passwd')).toBe(false);
      expect(guard.isWriteAllowed('C:\\Windows\\System32')).toBe(false);
    });

    it('blocks ~ expansion', () => {
      expect(guard.isWriteAllowed('~/.ssh/id_rsa')).toBe(false);
    });

    it('blocks dot-prefixed traversal', () => {
      expect(guard.isWriteAllowed('sites/./../../secret')).toBe(false);
    });
  });

  describe('READ: allowed paths', () => {
    it('allows reading from sites/', () => {
      expect(guard.isReadAllowed('sites/leo-global-holdings/frankmax/index.html')).toBe(true);
    });

    it('allows reading from memory/', () => {
      expect(guard.isReadAllowed('memory/chatgpt-conversation-andrew-franklin-leo.md')).toBe(true);
    });

    it('allows reading ventures.json', () => {
      expect(guard.isReadAllowed('ventures.json')).toBe(true);
    });
  });

  describe('READ: blocked paths', () => {
    it('blocks reading .env files', () => {
      expect(guard.isReadAllowed('.env')).toBe(false);
      expect(guard.isReadAllowed('.env.local')).toBe(false);
    });

    it('blocks reading .git/', () => {
      expect(guard.isReadAllowed('.git/config')).toBe(false);
    });

    it('blocks reading docker secrets', () => {
      expect(guard.isReadAllowed('docker/secrets/openai-key.txt')).toBe(false);
    });
  });

  describe('VALIDATE: path validation', () => {
    it('returns error object for invalid paths', () => {
      const result = guard.validate('write', '../escape');
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('traversal');
    });

    it('returns success for valid paths', () => {
      const result = guard.validate('write', 'sites/leo-global-holdings/test.html');
      expect(result.allowed).toBe(true);
    });
  });
});
