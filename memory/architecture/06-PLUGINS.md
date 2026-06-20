# Plugins

Post-processing modules that run after agents complete their work. Each plugin is a Docker container that operates on the built site.

## Plugin List

| Plugin | Trigger | Docker Image | Purpose |
|--------|---------|-------------|---------|
| `seo-enhancer` | post-generate | `plugins/seo-enhancer` | Meta tags, sitemap, JSON-LD |
| `analytics-injector` | post-generate | `plugins/analytics-injector` | GA4/Matomo tracking |
| `accessibility-auditor` | post-generate | `plugins/accessibility-auditor` | WCAG compliance |
| `performance-optimizer` | post-generate | `plugins/performance-optimizer` | Minify, optimize |

---

## seo-enhancer

**Input:** All `index.html` files in `docs/`

**Processing:**
1. Read each HTML file
2. Inject `<head>` meta tags from `_*.json` metadata:
   - `<title>` — "{Offering} | {Venture} | {Group} | Andrew Franklin Leo"
   - `<meta name="description">` — Generated from mission/description
   - `<meta property="og:title">` — Page title
   - `<meta property="og:description">` — Page description
   - `<meta property="og:image">` — Default or page-specific image
   - `<meta property="og:url">` — Canonical URL
   - `<meta name="twitter:card">` — summary_large_image
3. Generate JSON-LD structured data:
   - `Organization` for conglomerate
   - `Organization` for groups
   - `Service` for ventures
   - `Product` for offerings
4. Generate `sitemap.xml` with all pages
5. Generate `robots.txt`

**Output:** Modified HTML files + `sitemap.xml` + `robots.txt`

---

## analytics-injector

**Input:** All `index.html` files in `docs/`

**Processing:**
1. Inject Google Analytics 4 (GA4) script:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```
2. Add custom event tracking for:
   - Page views (group, venture, offering)
   - Navigation clicks
   - Related venture clicks
   - External link clicks
3. Inject Matomo fallback if GA4 unavailable

**Config:**
```yaml
provider: ga4
measurement_id: "G-XXXXXXXXXX"
enabled: true
custom_events:
  - name: "venture_view"
    trigger: "page_load"
  - name: "offering_view"
    trigger: "page_load"
  - name: "cross_link_click"
    trigger: "click"
    selector: ".cross-link"
```

---

## accessibility-auditor

**Input:** All `index.html` files in `docs/`

**Processing:**
1. Audit HTML for WCAG 2.1 AA compliance:
   - Missing `alt` attributes on images
   - Missing `lang` attribute on `<html>`
   - Missing `aria-label` on interactive elements
   - Color contrast issues (if CSS available)
   - Heading hierarchy (h1 → h2 → h3)
   - Form labels
   - Link text (avoid "click here")
2. Auto-fix safe issues:
   - Add `lang="en"` to `<html>`
   - Add `aria-label` to nav, footer, sidebar
   - Add `role` attributes where needed
3. Generate accessibility report:
   - `docs/a11y-report.json`
   - List of issues found
   - List of auto-fixes applied
   - List of manual fixes needed

**Output:** Fixed HTML files + `a11y-report.json`

---

## performance-optimizer

**Input:** All files in `docs/`

**Processing:**
1. HTML minification:
   - Remove HTML comments
   - Collapse whitespace
   - Remove optional tags
2. Add performance hints:
   - `<link rel="preconnect">` for external resources
   - `<link rel="preload">` for critical CSS/fonts
   - `loading="lazy"` on images
3. Generate `manifest.json` for PWA readiness
4. Calculate and report:
   - Total page count
   - Average file size
   - Total site size
   - Largest pages

**Output:** Optimized files + `perf-report.json`

---

## Plugin Execution Order

```
Agents complete
    │
    ▼
seo-enhancer (meta tags, sitemap)
    │
    ▼
analytics-injector (tracking scripts)
    │
    ▼
accessibility-auditor (WCAG fixes)
    │
    ▼
performance-optimizer (minify, optimize)
    │
    ▼
docs/ ready for deployment
```

## Plugin Configuration

Plugins read config from `docker/plugins/{name}/config.yaml`:

```yaml
# docker/plugins/seo-enhancer/config.yaml
base_url: "https://andrewfranklinleo.com"
site_name: "Andrew Franklin Leo"
default_og_image: "/assets/og-default.png"
jsonld_enabled: true
sitemap_enabled: true
```

## Plugin Registration

Plugins are registered in `registry-mcp`:

```json
{
  "plugins": {
    "seo-enhancer": {
      "version": "1.0.0",
      "enabled": true,
      "trigger": "post-generate",
      "docker_image": "plugins/seo-enhancer",
      "config_file": "docker/plugins/seo-enhancer/config.yaml",
      "dependencies": [],
      "order": 1
    },
    "analytics-injector": {
      "version": "1.0.0",
      "enabled": true,
      "trigger": "post-generate",
      "docker_image": "plugins/analytics-injector",
      "dependencies": [],
      "order": 2
    },
    "accessibility-auditor": {
      "version": "1.0.0",
      "enabled": true,
      "trigger": "post-generate",
      "docker_image": "plugins/accessibility-auditor",
      "dependencies": [],
      "order": 3
    },
    "performance-optimizer": {
      "version": "1.0.0",
      "enabled": true,
      "trigger": "post-generate",
      "docker_image": "plugins/performance-optimizer",
      "dependencies": [],
      "order": 4
    }
  }
}
```
