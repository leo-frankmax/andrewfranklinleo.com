import { describe, it, expect } from 'vitest';
import { ToolGuard, AgentContract } from '../tool-guard.js';

describe('ToolGuard — H2: Agent tool allowlist enforcement', () => {
  const ventureGenContract: AgentContract = {
    name: 'venture-generator',
    allowedTools: [
      'content-mcp.expand_venture_list',
      'content-mcp.generate_venture_description',
      'graph-mcp.add_node',
      'graph-mcp.find_gaps',
      'fs-mcp.read_json',
      'fs-mcp.write_json',
    ],
    deniedTools: ['fs-mcp.delete_file', 'fs-mcp.move_file', '*exec*', '*eval*'],
  };

  const guard = new ToolGuard(ventureGenContract);

  describe('ALLOWED: tools in allowlist', () => {
    it('allows content-mcp.expand_venture_list', () => {
      expect(guard.isToolAllowed('content-mcp.expand_venture_list')).toBe(true);
    });

    it('allows fs-mcp.read_json', () => {
      expect(guard.isToolAllowed('fs-mcp.read_json')).toBe(true);
    });

    it('allows graph-mcp.add_node', () => {
      expect(guard.isToolAllowed('graph-mcp.add_node')).toBe(true);
    });
  });

  describe('BLOCKED: tools not in allowlist', () => {
    it('blocks fs-mcp.delete_file', () => {
      expect(guard.isToolAllowed('fs-mcp.delete_file')).toBe(false);
    });

    it('blocks fs-mcp.move_file', () => {
      expect(guard.isToolAllowed('fs-mcp.move_file')).toBe(false);
    });

    it('blocks unknown tools', () => {
      expect(guard.isToolAllowed('random-tool.do_something')).toBe(false);
    });

    it('blocks exec-like tools', () => {
      expect(guard.isToolAllowed('shell-exec.run')).toBe(false);
    });

    it('blocks eval-like tools', () => {
      expect(guard.isToolAllowed('eval-code.run')).toBe(false);
    });
  });

  describe('DENIED: explicit denylist takes precedence', () => {
    it('denies tools matching denylist patterns', () => {
      const contract: AgentContract = {
        name: 'test',
        allowedTools: ['*'],
        deniedTools: ['fs-mcp.delete_file'],
      };
      const g = new ToolGuard(contract);
      expect(g.isToolAllowed('fs-mcp.delete_file')).toBe(false);
    });
  });

  describe('LOGGING: tool calls are logged', () => {
    it('logs allowed tool calls', () => {
      guard.isToolAllowed('content-mcp.expand_venture_list');
      const logs = guard.getLog();
      expect(logs.length).toBeGreaterThan(0);
      expect(logs[0].tool).toBe('content-mcp.expand_venture_list');
      expect(logs[0].allowed).toBe(true);
    });

    it('logs blocked tool calls', () => {
      guard.isToolAllowed('fs-mcp.delete_file');
      const logs = guard.getLog();
      const blocked = logs.filter(l => !l.allowed);
      expect(blocked.length).toBeGreaterThan(0);
    });
  });

  describe('MULTIPLE AGENTS: different contracts', () => {
    it('enforces different allowlists per agent', () => {
      const siteCreatorContract: AgentContract = {
        name: 'site-creator',
        allowedTools: [
          'fs-mcp.create_directory',
          'fs-mcp.write_file',
          'template-mcp.render_template',
          'graph-mcp.build_global_nav',
          'graph-mcp.get_children',
        ],
        deniedTools: [],
      };
      const g = new ToolGuard(siteCreatorContract);

      // site-creator can use fs-mcp.create_directory
      expect(g.isToolAllowed('fs-mcp.create_directory')).toBe(true);

      // site-creator cannot use content-mcp tools
      expect(g.isToolAllowed('content-mcp.expand_venture_list')).toBe(false);
    });
  });
});
