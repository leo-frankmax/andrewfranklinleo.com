# Skills

MCP-callable domain-specific content generators. Skills are invoked by agents to perform specialized tasks.

## Skill List

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `biography-generator` | `content-mcp.generate_biography()` | Write founder, executive, or entity biographies |
| `venture-lister` | `content-mcp.expand_venture_list()` | Apply master prompt to generate venture portfolios |
| `product-detailer` | `content-mcp.generate_offering_description()` | Write detailed product/service/solution pages |
| `landing-page-styler` | `template-mcp.render_template()` | Apply consistent styling, SEO, schema.org |

---

## biography-generator

**Input:**
```json
{
  "entity_name": "Andrew Franklin Leo",
  "entity_type": "founder",
  "context": "visionary entrepreneur, systems architect, philanthropist",
  "achievements": ["founded Frankmax", "created Universal Prosperity Ecosystem"],
  "philosophy": "Universal Humanism",
  "mission": "Build systems that help people flourish",
  "tone": "formal",
  "length": "long"
}
```

**Output:** Full HTML biography section with early life, education, philosophy, achievements, legacy.

---

## venture-lister

**Input:**
```json
{
  "group_name": "Frankmax Group",
  "group_mission": "Empowering Every Professional",
  "existing_ventures": ["frankmax-talent", "frankmax-learning"],
  "sectors_to_cover": ["Human Resources", "Education", "Consulting", "Technology"],
  "venture_categories": ["core", "strategic", "emerging", "support", "social"],
  "ecosystem_flows": {
    "upstream": [],
    "downstream": ["virginbay"]
  }
}
```

**Output:** Expanded venture list with 15-30 ventures per group, each with offerings.

---

## product-detailer

**Input:**
```json
{
  "offering_name": "Executive Search",
  "venture_name": "Frankmax Talent",
  "group_name": "Frankmax Group",
  "functions": ["C-suite recruitment", "Board placement"],
  "customers": ["Enterprises", "Boards of Directors"],
  "related_offerings": ["workforce-management", "career-development"],
  "ecosystem_position": "Frankmax develops talent → Virginbay employs talent"
}
```

**Output:** Full HTML page with description, features, benefits, use cases, CTA, related links.

---

## landing-page-styler

**Input:**
```json
{
  "page_type": "offering",
  "content_html": "...",
  "title": "Executive Search | Frankmax Talent",
  "description": "World-class executive recruitment...",
  "breadcrumbs": ["Home", "Frankmax", "Frankmax Talent", "Executive Search"],
  "parent_group": "frankmax",
  "parent_venture": "frankmax-talent",
  "schema_type": "Service",
  "og_image": "/assets/frankmax/executive-search.jpg"
}
```

**Output:** Complete styled HTML page with consistent header, nav, breadcrumbs, footer, meta tags, schema.org markup.

---

## Skill Registration

Skills are registered in `registry-mcp` and available to all agents:

```json
{
  "skills": {
    "biography-generator": {
      "version": "1.0.0",
      "mcp_servers": ["content-mcp", "template-mcp"],
      "required_tools": ["generate_biography", "render_template"],
      "dependencies": []
    },
    "venture-lister": {
      "version": "1.0.0",
      "mcp_servers": ["content-mcp", "graph-mcp", "fs-mcp"],
      "required_tools": ["expand_venture_list", "add_node", "write_json"],
      "dependencies": []
    },
    "product-detailer": {
      "version": "1.0.0",
      "mcp_servers": ["content-mcp", "template-mcp"],
      "required_tools": ["generate_offering_description", "render_template"],
      "dependencies": []
    },
    "landing-page-styler": {
      "version": "1.0.0",
      "mcp_servers": ["template-mcp", "fs-mcp"],
      "required_tools": ["render_template", "write_file"],
      "dependencies": []
    }
  }
}
```
