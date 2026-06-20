import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { CircuitBreaker, CircuitState } from '../circuit-breaker.js';

describe('CircuitBreaker — H6: Circuit breaker for runaway agents', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts in CLOSED state', () => {
    const cb = new CircuitBreaker({
      agentName: 'test-agent',
      failureThreshold: 3,
      resetTimeoutMs: 30000,
    });
    expect(cb.getState()).toBe(CircuitState.CLOSED);
  });

  it('records successes', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 3,
      resetTimeoutMs: 30000,
    });

    cb.recordSuccess();
    cb.recordSuccess();
    expect(cb.getSuccessCount()).toBe(2);
    expect(cb.getFailureCount()).toBe(0);
  });

  it('records failures', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 3,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    expect(cb.getFailureCount()).toBe(1);
  });

  it('opens circuit after threshold failures', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 3,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    cb.recordFailure();
    expect(cb.getState()).toBe(CircuitState.CLOSED);

    cb.recordFailure();
    expect(cb.getState()).toBe(CircuitState.OPEN);
  });

  it('rejects calls when circuit is OPEN', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 2,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    cb.recordFailure();
    expect(cb.getState()).toBe(CircuitState.OPEN);

    expect(cb.canExecute()).toBe(false);
  });

  it('moves to HALF_OPEN after reset timeout', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 2,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    cb.recordFailure();
    expect(cb.getState()).toBe(CircuitState.OPEN);

    vi.advanceTimersByTime(31000);
    expect(cb.getState()).toBe(CircuitState.HALF_OPEN);
    expect(cb.canExecute()).toBe(true);
  });

  it('closes circuit on success in HALF_OPEN', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 2,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    cb.recordFailure();
    vi.advanceTimersByTime(31000);
    expect(cb.getState()).toBe(CircuitState.HALF_OPEN);

    cb.recordSuccess();
    expect(cb.getState()).toBe(CircuitState.CLOSED);
  });

  it('opens circuit on failure in HALF_OPEN', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 2,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    cb.recordFailure();
    vi.advanceTimersByTime(31000);
    expect(cb.getState()).toBe(CircuitState.HALF_OPEN);

    cb.recordFailure();
    expect(cb.getState()).toBe(CircuitState.OPEN);
  });

  it('resets failure count on success', () => {
    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 3,
      resetTimeoutMs: 30000,
    });

    cb.recordFailure();
    cb.recordFailure();
    cb.recordSuccess();
    expect(cb.getFailureCount()).toBe(0);
  });

  it('provides state change callbacks', () => {
    const onOpen = vi.fn();
    const onClose = vi.fn();

    const cb = new CircuitBreaker({
      agentName: 'test',
      failureThreshold: 2,
      resetTimeoutMs: 30000,
      onOpen,
      onClose,
    });

    cb.recordFailure();
    cb.recordFailure();
    expect(onOpen).toHaveBeenCalledOnce();
  });
});
