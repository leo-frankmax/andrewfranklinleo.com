import sanitizeHtmlLib from 'sanitize-html';

export interface SchemaValidationResult {
  valid: boolean;
  errors: string[];
}

export interface ContentLengthResult {
  valid: boolean;
  reason?: string;
}

export class ContentGuard {
  private defaultSanitizeOptions: sanitizeHtmlLib.IOptions = {
    allowedTags: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'ul', 'ol', 'li',
      'a', 'img',
      'strong', 'em', 'b', 'i', 'u',
      'blockquote', 'pre', 'code',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'div', 'span',
      'dl', 'dt', 'dd',
    ],
    allowedAttributes: {
      'a': ['href', 'title', 'target', 'rel'],
      'img': ['src', 'alt', 'title', 'width', 'height'],
      'div': ['class', 'id'],
      'span': ['class', 'id'],
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
      'blockquote': ['class', 'id'],
      'pre': ['class', 'id'],
      'code': ['class', 'id'],
    },
    allowedSchemes: ['http', 'https', 'mailto'],
  };

  sanitizeHtml(html: string): string {
    return sanitizeHtmlLib(html, this.defaultSanitizeOptions);
  }

  validateSchema(data: unknown, schema?: Record<string, unknown>): SchemaValidationResult {
    const errors: string[] = [];

    if (!schema) {
      return { valid: true, errors: [] };
    }

    const s = schema as Record<string, any>;

    if (s.type === 'object' && (data === null || typeof data !== 'object')) {
      return { valid: false, errors: [`Expected object, got ${typeof data}`] };
    }

    if (s.required && Array.isArray(s.required)) {
      for (const field of s.required) {
        if (data === null || data === undefined || !(field in (data as object))) {
          errors.push(`Missing required field: ${field}`);
        }
      }
    }

    if (s.properties && typeof data === 'object' && data !== null) {
      for (const [key, propSchema] of Object.entries(s.properties as Record<string, any>)) {
        const value = (data as Record<string, unknown>)[key];
        if (value !== undefined && propSchema && propSchema.type) {
          const actualType = typeof value;
          if (propSchema.type === 'array') {
            if (!Array.isArray(value)) {
              errors.push(`Field '${key}' expected array, got ${actualType}`);
            }
          } else if (actualType !== propSchema.type) {
            errors.push(`Field '${key}' expected ${propSchema.type}, got ${actualType}`);
          }
        }
      }
    }

    return { valid: errors.length === 0, errors };
  }

  validateContentLength(content: string, maxLength: number): ContentLengthResult {
    if (content.length > maxLength) {
      return {
        valid: false,
        reason: `Content length ${content.length} exceeds max ${maxLength}`,
      };
    }
    return { valid: true };
  }
}
