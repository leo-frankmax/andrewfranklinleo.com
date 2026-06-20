import sanitizeHtmlLib from 'sanitize-html';

export interface BreadcrumbItem {
  label: string;
  url: string;
}

export interface NavGroup {
  label: string;
  url: string;
  mission: string;
  ventures: { label: string; url: string }[];
}

export interface NavData {
  home: { label: string; url: string };
  groups: NavGroup[];
  strategicVerticals: { label: string; url: string }[];
}

export interface CardData {
  title: string;
  description: string;
  url: string;
  icon: string;
}

export interface TemplateContext {
  [key: string]: unknown;
}

export class TemplateEngine {
  private sanitizeOptions: sanitizeHtmlLib.IOptions = {
    allowedTags: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'ul', 'ol', 'li',
      'a', 'img',
      'strong', 'em', 'b', 'i', 'u',
      'blockquote', 'pre', 'code',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'div', 'span', 'nav', 'main', 'header', 'footer', 'section', 'article',
    ],
    allowedAttributes: {
      'a': ['href', 'title', 'target', 'rel', 'class', 'id', 'aria-current'],
      'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
      'div': ['class', 'id', 'role'],
      'span': ['class', 'id'],
      'nav': ['class', 'id', 'aria-label'],
      'main': ['class', 'id'],
      'header': ['class', 'id'],
      'footer': ['class', 'id'],
      'section': ['class', 'id'],
      'article': ['class', 'id'],
      'p': ['class', 'id'],
      'h1': ['class', 'id'],
      'h2': ['class', 'id'],
      'h3': ['class', 'id'],
      'h4': ['class', 'id'],
      'h5': ['class', 'id'],
      'h6': ['class', 'id'],
      'ul': ['class', 'id'],
      'ol': ['class', 'id'],
      'li': ['class', 'id'],
      'table': ['class', 'id'],
      'tr': ['class', 'id'],
      'th': ['class', 'id', 'colspan', 'rowspan'],
      'td': ['class', 'id', 'colspan', 'rowspan'],
    },
    allowedSchemes: ['http', 'https', 'mailto'],
  };

  renderTemplate(template: string, context: TemplateContext): string {
    let result = template;
    for (const [key, value] of Object.entries(context)) {
      if (typeof value === 'object' && value !== null) {
        for (const [subKey, subValue] of Object.entries(value as Record<string, unknown>)) {
          const regex = new RegExp(`\\{\\{${key}\\.${subKey}\\}\\}`, 'g');
          result = result.replace(regex, String(subValue ?? ''));
        }
      } else {
        const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
        result = result.replace(regex, String(value ?? ''));
      }
    }
    // Strip remaining unresolved placeholders
    result = result.replace(/\{\{[^}]+\}\}/g, '');
    return result;
  }

  renderBreadcrumbs(items: BreadcrumbItem[]): string {
    const lis = items.map((item, i) => {
      const isLast = i === items.length - 1;
      if (isLast) {
        return `<li><a href="${item.url}" aria-current="page">${item.label}</a></li>`;
      }
      return `<li><a href="${item.url}">${item.label}</a></li>`;
    }).join('\n          ');
    return `<nav aria-label="Breadcrumb" class="breadcrumb">\n  <ol>\n    ${lis}\n  </ol>\n</nav>`;
  }

  renderNav(nav: NavData, currentPath: string): string {
    const groups = nav.groups.map(g => `
      <li class="nav-group">
        <a href="${g.url}" ${currentPath.startsWith(g.url) ? 'aria-current="page"' : ''}>${g.label}</a>
      </li>`).join('');

    const verticals = nav.strategicVerticals.map(v => `
      <li>
        <a href="${v.url}" ${currentPath === v.url ? 'aria-current="page"' : ''}>${v.label}</a>
      </li>`).join('');

    return `<nav aria-label="Global Navigation" class="global-nav">
  <ul>
    <li><a href="${nav.home.url}" ${currentPath === '/' ? 'aria-current="page"' : ''}>${nav.home.label}</a></li>
    ${groups}
    <li class="nav-divider" aria-hidden="true"></li>
    ${verticals}
  </ul>
</nav>`;
  }

  renderCard(data: CardData): string {
    return `<article class="card">
  <div class="card-icon" aria-hidden="true">${data.icon}</div>
  <h3><a href="${data.url}">${data.title}</a></h3>
  <p>${data.description}</p>
</article>`;
  }

  renderGrid(items: CardData[]): string {
    const cards = items.map(item => this.renderCard(item)).join('\n');
    return `<div class="grid">\n${cards}\n</div>`;
  }

  sanitize(html: string): string {
    return sanitizeHtmlLib(html, this.sanitizeOptions);
  }
}
