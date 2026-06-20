# MCP Servers

5 Model Context Protocol servers running as Docker containers. Agents discover and call these via stdio/HTTP to perform their work.

## Server List

| Server | Port | Base Image | Purpose |
|--------|------|------------|---------|
| `fs-mcp` | 3001 | `python:3.12-slim` | File system operations |
| `content-mcp` | 3002 | `python:3.12-slim` | LLM content generation |
| `template-mcp` | 3003 | `python:3.12-slim` | Template rendering |
| `graph-mcp` | 3004 | `python:3.12-slim` | Site graph management |
| `registry-mcp` | 3005 | `python:3.12-slim` | Plugin/skill registry |

---

## fs-mcp — File System Operations

**Responsibility:** Read, write, and manage all site files and metadata.

### Tools

| Tool | Description |
|------|-------------|
| `read_file(path)` | Read file contents from `sites/` |
| `write_file(path, content)` | Write file to `sites/` |
| `create_directory(path)` | Create directory structure |
| `list_directory(path)` | List contents of directory |
| `delete_file(path)` | Remove file |
| `read_json(path)` | Read and parse JSON metadata file |
| `write_json(path, data)` | Write JSON metadata file |
| `move_file(src, dst)` | Move/rename file |
| `copy_file(src, dst)` | Copy file |
| `file_exists(path)` | Check if file exists |
| `get_file_size(path)` | Get file size in bytes |

### Configuration

```yaml
root_path: /data/sites
allowed_extensions:
  - .html
  - .json
  - .css
  - .js
  - .md
  - .xml
max_file_size: 10MB
```

---

## content-mcp — LLM Content Generation

**Responsibility:** Call LLM to generate venture descriptions, product pages, SEO metadata, biography content.

### Tools

| Tool | Description |
|------|-------------|
| `generate_venture_description(venture_data)` | Write full venture page content |
| `generate_offering_description(offering_data)` | Write product/service/solution page |
| `generate_seo_meta(page_data)` | Generate meta tags, JSON-LD |
| `generate_biography(person_data)` | Write executive/founder biography |
| `generate_mission_statement(entity_data)` | Create mission/vision text |
| `generate_group_overview(group_data)` | Write group landing page content |
| `expand_venture_list(group, master_prompt)` | Apply master prompt to generate new ventures |
| `generate_breadcrumb_trail(node_data)` | Create breadcrumb text |

### Configuration

```yaml
provider: openai  # or: local, anthropic
model: gpt-4.1
api_key_env: OPENAI_API_KEY
max_tokens: 4096
temperature: 0.7
fallback_provider: local
local_model: llama3.1:8b
```

---

## template-mcp — Template Management

**Responsibility:** Render HTML pages from templates, apply consistent layouts, inject variables.

### Tools

| Tool | Description |
|------|-------------|
| `render_template(template_name, variables)` | Render template with variables |
| `get_template(name)` | Get template content |
| `list_templates()` | List available templates |
| `apply_global_layout(content, title)` | Wrap content in base layout |
| `render_breadcrumb(nodes)` | Render breadcrumb HTML |
| `render_nav(current_group, current_venture)` | Render navigation HTML |
| `render_card(data, type)` | Render venture/offering card |
| `validate_html(html)` | Basic HTML validation |

### Template Variables

```yaml
global:
  site_name: "Andrew Franklin Leo"
  site_url: "https://andrewfranklinleo.com"
  logo: "/assets/logo.svg"
  theme: "professional"
  colors:
    primary: "#1a365d"
    secondary: "#2563eb"
    accent: "#f59e0b"

node_types:
  conglomerate:
    template: conglomerate-home.html
  group:
    template: group-landing.html
  venture:
    template: venture-landing.html
  offering:
    template: offering-landing.html
```

---

## graph-mcp — Site Graph Management

**Responsibility:** Maintain parent/child/sibling relationships, cross-links, navigation between all nodes.

### Tools

| Tool | Description |
|------|-------------|
| `get_node(path)` | Get node with all relationships |
| `get_children(path)` | Get direct children |
| `get_parent(path)` | Get parent node |
| `get_siblings(path)` | Get sibling nodes |
| `get_ancestors(path)` | Get full ancestor chain |
| `add_node(path, metadata)` | Add node to graph |
| `remove_node(path)` | Remove node from graph |
| `update_node(path, metadata)` | Update node metadata |
| `get_related(path, max_depth)` | Get related nodes across graph |
| `get_cross_links(path)` | Get cross-reference links |
| `build_global_nav()` | Generate full navigation tree |
| `validate_graph()` | Check for orphans, cycles, broken links |
| `get_ecosystem_flows()` | Get flow relationships (Frankmax→Virginbay, etc.) |
| `find_gaps()`` | Find missing nodes in hierarchy |

### Graph Structure

```json
{
  "path": "leo-global-holdings/frankmax/frankmax-talent/executive-search",
  "type": "offering",
  "parent": "leo-global-holdings/frankmax/frankmax-talent",
  "group": "frankmax",
  "venture": "frankmax-talent",
  "siblings": ["recruitment", "workforce-management", "talent-intelligence", "career-planning"],
  "related": ["leo-global-holdings/glosbe/glosbe-communities/professional-networks"],
  "ecosystem_flows": {
    "upstream": [],
    "downstream": ["leo-global-holdings/virginbay/virginbay-services/professional-services"]
  }
}
```

---

## registry-mcp — Plugin/Skill Registry

**Responsibility:** Discovery, versioning, dependency resolution for plugins, skills, and hooks.

### Tools

| Tool | Description |
|------|-------------|
| `list_plugins()` | List available plugins |
| `get_plugin(name)` | Get plugin details |
| `register_plugin(name, config)` | Register new plugin |
| `list_skills()` | List available skills |
| `get_skill(name)` | Get skill details |
| `register_skill(name, config)` | Register new skill |
| `list_hooks()` | List available hooks |
| `register_hook(name, config)` | Register new hook |
| `resolve_dependencies(name)` | Get dependency tree |
| `get_plugin_config(name)` | Get plugin configuration |
| `update_plugin_config(name, config)` | Update plugin config |

### Registry Structure

```json
{
  "plugins": {
    "seo-enhancer": {
      "version": "1.0.0",
      "enabled": true,
      "dependencies": [],
      "hooks": ["post-generate"]
    },
    "analytics-injector": {
      "version": "1.0.0",
      "enabled": true,
      "dependencies": [],
      "hooks": ["post-generate"]
    }
  },
  "skills": {
    "venture-lister": {
      "version": "1.0.0",
      "mcp_servers": ["content-mcp", "graph-mcp", "fs-mcp"]
    }
  }
}
```
