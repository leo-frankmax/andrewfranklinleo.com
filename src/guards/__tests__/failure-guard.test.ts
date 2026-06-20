import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { FailureGuard, FailureArtifact } from '../failure-guard.js';
import { mkdtempSync, rmSync, existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

describe('FailureGuard — H3: Failure artifact emission', () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'failure-guard-test-'));
  });

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true });
  });

  it('creates error artifact on failure', async () => {
    const guard = new FailureGuard({
      agentName: 'venture-generator',
      outputDir: tmpDir,
    });

    await guard.emitFailure(new Error('LLM timeout'), {
      ventureCount: 0,
      lastSuccessfulStep: 'read-input',
    });

    const errorFile = join(tmpDir, 'venture-generator.error.json');
    expect(existsSync(errorFile)).toBe(true);

    const artifact: FailureArtifact = JSON.parse(readFileSync(errorFile, 'utf-8'));
    expect(artifact.agent).toBe('venture-generator');
    expect(artifact.error).toContain('LLM timeout');
    expect(artifact.context.ventureCount).toBe(0);
    expect(artifact.timestamp).toBeDefined();
    expect(artifact.runId).toBeDefined();
  });

  it('includes stack trace in artifact', async () => {
    const guard = new FailureGuard({
      agentName: 'test-agent',
      outputDir: tmpDir,
    });

    const error = new Error('test error');
    await guard.emitFailure(error, {});

    const artifact: FailureArtifact = JSON.parse(
      readFileSync(join(tmpDir, 'test-agent.error.json'), 'utf-8')
    );
    expect(artifact.stack).toBeDefined();
  });

  it('generates unique run IDs', async () => {
    const guard1 = new FailureGuard({ agentName: 'a', outputDir: tmpDir });
    const guard2 = new FailureGuard({ agentName: 'b', outputDir: tmpDir });

    await guard1.emitFailure(new Error('err1'), {});
    await guard2.emitFailure(new Error('err2'), {});

    const a1: FailureArtifact = JSON.parse(readFileSync(join(tmpDir, 'a.error.json'), 'utf-8'));
    const a2: FailureArtifact = JSON.parse(readFileSync(join(tmpDir, 'b.error.json'), 'utf-8'));
    expect(a1.runId).not.toBe(a2.runId);
  });

  it('emits failure artifact even if write fails', async () => {
    const guard = new FailureGuard({
      agentName: 'test',
      outputDir: '/nonexistent/path/that/does/not/exist',
    });

    // Should not throw
    await expect(
      guard.emitFailure(new Error('test'), {})
    ).resolves.toBeUndefined();
  });

  it('returns void (no throw)', async () => {
    const guard = new FailureGuard({
      agentName: 'test',
      outputDir: tmpDir,
    });

    const result = await guard.emitFailure(new Error('fail'), {});
    expect(result).toBeUndefined();
  });
});
