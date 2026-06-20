import { AgentContract } from '../guards/tool-guard.js';

export const AGENT_CONTRACTS: Record<string, AgentContract> = {
  'venture-generator': {
    name: 'venture-generator',
    allowedTools: [
      'content-mcp.expand_venture_list',
      'content-mcp.generate_venture_description',
      'content-mcp.generate_offering_descriptions',
      'graph-mcp.add_node',
      'graph-mcp.find_gaps',
      'graph-mcp.validate_parent_child',
      'fs-mcp.read_json',
      'fs-mcp.write_json',
    ],
    deniedTools: [
      'fs-mcp.delete_file',
      'fs-mcp.move_file',
      'fs-mcp.write_file',
      '*exec*',
      '*eval*',
    ],
  },

  'site-creator': {
    name: 'site-creator',
    allowedTools: [
      'fs-mcp.create_directory',
      'fs-mcp.write_file',
      'fs-mcp.read_json',
      'template-mcp.render_template',
      'template-mcp.render_component',
      'template-mcp.render_nav',
      'graph-mcp.build_global_nav',
      'graph-mcp.get_children',
      'graph-mcp.get_siblings',
      'content-mcp.generate_page_content',
      'content-mcp.sanitize_html',
    ],
    deniedTools: [
      'fs-mcp.delete_file',
      'fs-mcp.move_file',
      'content-mcp.expand_venture_list',
      '*exec*',
      '*eval*',
    ],
  },

  'content-writer': {
    name: 'content-writer',
    allowedTools: [
      'content-mcp.generate_page_content',
      'content-mcp.sanitize_html',
      'content-mcp.validate_schema',
      'fs-mcp.read_json',
      'fs-mcp.read_file',
      'graph-mcp.get_children',
      'graph-mcp.get_node',
    ],
    deniedTools: [
      'fs-mcp.write_file',
      'fs-mcp.delete_file',
      'fs-mcp.move_file',
      'template-mcp.render_template',
      '*exec*',
      '*eval*',
    ],
  },

  'graph-builder': {
    name: 'graph-builder',
    allowedTools: [
      'graph-mcp.add_node',
      'graph-mcp.add_edge',
      'graph-mcp.remove_node',
      'graph-mcp.find_gaps',
      'graph-mcp.detect_cycles',
      'graph-mcp.validate_depth',
      'graph-mcp.build_global_nav',
      'graph-mcp.get_children',
      'graph-mcp.get_siblings',
      'graph-mcp.get_node',
      'fs-mcp.read_json',
      'fs-mcp.write_json',
    ],
    deniedTools: [
      'fs-mcp.write_file',
      'fs-mcp.delete_file',
      'template-mcp.render_template',
      'content-mcp.generate_page_content',
      '*exec*',
      '*eval*',
    ],
  },

  'qa-validator': {
    name: 'qa-validator',
    allowedTools: [
      'fs-mcp.read_file',
      'fs-mcp.read_json',
      'fs-mcp.list_directory',
      'content-mcp.validate_schema',
      'content-mcp.sanitize_html',
      'graph-mcp.validate_integrity',
      'graph-mcp.detect_cycles',
      'graph-mcp.find_gaps',
    ],
    deniedTools: [
      'fs-mcp.write_file',
      'fs-mcp.write_json',
      'fs-mcp.delete_file',
      'fs-mcp.move_file',
      'fs-mcp.create_directory',
      'template-mcp.render_template',
      'content-mcp.generate_page_content',
      '*exec*',
      '*eval*',
    ],
  },
};

export function getAgentContract(agentName: string): AgentContract {
  const contract = AGENT_CONTRACTS[agentName];
  if (!contract) {
    throw new Error(`No contract defined for agent: ${agentName}`);
  }
  return contract;
}

export function listAgentNames(): string[] {
  return Object.keys(AGENT_CONTRACTS);
}
