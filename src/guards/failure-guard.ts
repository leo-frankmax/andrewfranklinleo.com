import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { randomUUID } from 'crypto';

export interface FailureContext {
  [key: string]: unknown;
}

export interface FailureArtifact {
  agent: string;
  error: string;
  stack?: string;
  timestamp: string;
  runId: string;
  context: FailureContext;
}

export interface FailureGuardConfig {
  agentName: string;
  outputDir: string;
}

export class FailureGuard {
  private config: FailureGuardConfig;

  constructor(config: FailureGuardConfig) {
    this.config = config;
  }

  async emitFailure(error: Error, context: FailureContext): Promise<void> {
    const artifact: FailureArtifact = {
      agent: this.config.agentName,
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      runId: randomUUID(),
      context,
    };

    try {
      const filePath = join(this.config.outputDir, `${this.config.agentName}.error.json`);
      const dir = dirname(filePath);
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }
      writeFileSync(filePath, JSON.stringify(artifact, null, 2), 'utf-8');
    } catch {
      // Swallow write errors — failure emission must not crash
    }
  }
}
