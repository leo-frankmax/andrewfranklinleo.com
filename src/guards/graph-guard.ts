export interface GraphEdge {
  from: string;
  to: string;
}

export interface GraphNode {
  id: string;
  type: string;
  parentId: string | null;
}

export interface GraphGuardConfig {
  rootNodes: string[];
  allowedParentTypes: string[];
  maxDepth: number;
}

export interface ParentChildValidation {
  valid: boolean;
  reason?: string;
}

export interface GraphIntegrityResult {
  valid: boolean;
  orphans: string[];
  errors: string[];
}

export class GraphGuard {
  private config: GraphGuardConfig;

  constructor(config: GraphGuardConfig) {
    this.config = config;
  }

  validateParentChild(rel: { parentId: string; childId: string; childType: string }): ParentChildValidation {
    if (!rel.parentId) {
      return { valid: false, reason: `Node '${rel.childId}' has no parent` };
    }
    if (!this.config.rootNodes.includes(rel.parentId)) {
      return { valid: false, reason: `Parent '${rel.parentId}' not found in root nodes` };
    }
    if (rel.childType && !this.config.allowedParentTypes.includes(rel.childType)) {
      return { valid: false, reason: `Node type '${rel.childType}' not in allowed types` };
    }
    return { valid: true };
  }

  detectCycles(edges: GraphEdge[]): string[][] {
    const cycles: string[][] = [];
    const adjacency = new Map<string, string[]>();

    for (const edge of edges) {
      if (!adjacency.has(edge.from)) adjacency.set(edge.from, []);
      adjacency.get(edge.from)!.push(edge.to);
    }

    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const path: string[] = [];

    const dfs = (node: string): void => {
      visited.add(node);
      recursionStack.add(node);
      path.push(node);

      const neighbors = adjacency.get(node) || [];
      for (const neighbor of neighbors) {
        if (neighbor === node) continue; // skip self-references
        if (!visited.has(neighbor)) {
          dfs(neighbor);
        } else if (recursionStack.has(neighbor)) {
          const cycleStart = path.indexOf(neighbor);
          if (cycleStart >= 0) {
            cycles.push(path.slice(cycleStart));
          }
        }
      }

      path.pop();
      recursionStack.delete(node);
    };

    const allNodes = new Set<string>();
    for (const edge of edges) {
      allNodes.add(edge.from);
      allNodes.add(edge.to);
    }

    for (const node of allNodes) {
      if (!visited.has(node)) {
        dfs(node);
      }
    }

    return cycles;
  }

  validateDepth(path: string): { valid: boolean; reason?: string } {
    const depth = path.split('/').length;
    if (depth > this.config.maxDepth) {
      return { valid: false, reason: `Path depth ${depth} exceeds max ${this.config.maxDepth}` };
    }
    return { valid: true };
  }

  validateGraphIntegrity(nodes: GraphNode[]): GraphIntegrityResult {
    const orphans: string[] = [];
    const errors: string[] = [];
    const nodeIds = new Set(nodes.map(n => n.id));

    for (const node of nodes) {
      if (node.parentId !== null && !nodeIds.has(node.parentId)) {
        orphans.push(node.id);
        errors.push(`Node '${node.id}' references non-existent parent '${node.parentId}'`);
      }
    }

    return { valid: orphans.length === 0, orphans, errors };
  }
}
