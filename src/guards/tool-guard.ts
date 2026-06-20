export interface AgentContract {
  name: string;
  allowedTools: string[];
  deniedTools: string[];
}

interface ToolLogEntry {
  tool: string;
  allowed: boolean;
  timestamp: number;
}

export class ToolGuard {
  private contract: AgentContract;
  private log: ToolLogEntry[] = [];

  constructor(contract: AgentContract) {
    this.contract = contract;
  }

  private matchesPattern(tool: string, pattern: string): boolean {
    if (pattern.startsWith('*') && pattern.endsWith('*')) {
      return tool.includes(pattern.slice(1, -1));
    }
    if (pattern.startsWith('*')) {
      return tool.endsWith(pattern.slice(1));
    }
    if (pattern.endsWith('*')) {
      return tool.startsWith(pattern.slice(0, -1));
    }
    return tool === pattern;
  }

  isToolAllowed(tool: string): boolean {
    // Check denylist first (explicit deny takes precedence)
    const denied = this.contract.deniedTools.some(d => this.matchesPattern(tool, d));
    if (denied) {
      this.log.push({ tool, allowed: false, timestamp: Date.now() });
      return false;
    }

    // Check allowlist
    const allowed = this.contract.allowedTools.some(a => this.matchesPattern(tool, a));
    this.log.push({ tool, allowed, timestamp: Date.now() });
    return allowed;
  }

  getLog(): ToolLogEntry[] {
    return [...this.log];
  }

  getAgentName(): string {
    return this.contract.name;
  }
}
