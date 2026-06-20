export interface TerminationConfig {
  agentName: string;
  maxIterations: number;
  timeoutMs: number;
}

export class TerminationGuard {
  private config: TerminationConfig;
  private iterationCount = 0;
  private startTime: number;

  constructor(config: TerminationConfig) {
    this.config = config;
    this.startTime = Date.now();
  }

  increment(): void {
    this.iterationCount++;
  }

  getIterationCount(): number {
    return this.iterationCount;
  }

  getElapsedMs(): number {
    return Date.now() - this.startTime;
  }

  shouldStop(): boolean {
    if (this.iterationCount >= this.config.maxIterations) return true;
    if (this.getElapsedMs() >= this.config.timeoutMs) return true;
    return false;
  }

  getStopReason(): string | null {
    if (this.iterationCount >= this.config.maxIterations) {
      return `Agent '${this.config.agentName}' reached max iterations (${this.config.maxIterations})`;
    }
    if (this.getElapsedMs() >= this.config.timeoutMs) {
      return `Agent '${this.config.agentName}' timeout after ${this.config.timeoutMs}ms`;
    }
    return null;
  }

  reset(): void {
    this.iterationCount = 0;
    this.startTime = Date.now();
  }
}
