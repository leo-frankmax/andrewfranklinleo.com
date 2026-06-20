import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TerminationGuard } from '../termination-guard.js';

describe('TerminationGuard — H1: Agent termination criteria', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('creates guard with max iterations and timeout', () => {
    const guard = new TerminationGuard({
      agentName: 'venture-generator',
      maxIterations: 500,
      timeoutMs: 1800000, // 30 min
    });
    expect(guard).toBeDefined();
  });

  it('tracks iteration count', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 3,
      timeoutMs: 60000,
    });

    expect(guard.shouldStop()).toBe(false);
    guard.increment();
    expect(guard.shouldStop()).toBe(false);
    guard.increment();
    expect(guard.shouldStop()).toBe(false);
    guard.increment();
    expect(guard.shouldStop()).toBe(true);
  });

  it('returns reason when max iterations exceeded', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 2,
      timeoutMs: 60000,
    });

    guard.increment();
    guard.increment();
    const reason = guard.getStopReason();
    expect(reason).toContain('max iterations');
    expect(reason).toContain('2');
  });

  it('detects timeout', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 1000,
      timeoutMs: 5000,
    });

    // Advance time past timeout
    vi.advanceTimersByTime(6000);
    expect(guard.shouldStop()).toBe(true);
    const reason = guard.getStopReason();
    expect(reason).toContain('timeout');
  });

  it('returns null reason when not stopped', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 100,
      timeoutMs: 60000,
    });

    expect(guard.getStopReason()).toBeNull();
  });

  it('reports elapsed time', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 100,
      timeoutMs: 60000,
    });

    vi.advanceTimersByTime(3000);
    expect(guard.getElapsedMs()).toBeGreaterThanOrEqual(3000);
  });

  it('reports iteration count', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 100,
      timeoutMs: 60000,
    });

    guard.increment();
    guard.increment();
    guard.increment();
    expect(guard.getIterationCount()).toBe(3);
  });

  it('resets state', () => {
    const guard = new TerminationGuard({
      agentName: 'test',
      maxIterations: 2,
      timeoutMs: 60000,
    });

    guard.increment();
    guard.increment();
    expect(guard.shouldStop()).toBe(true);

    guard.reset();
    expect(guard.shouldStop()).toBe(false);
    expect(guard.getIterationCount()).toBe(0);
  });
});
