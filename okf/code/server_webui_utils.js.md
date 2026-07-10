---
type: Source Code
description: "/**"
resource: server/webui/utils.js
timestamp: 2026-07-10T02:44:34Z
---

# utils

Source path: `server/webui/utils.js`

## Content

```javascript
/**
 * REMEMBER Web UI — Utility functions
 *
 * Extracted from app.js for testability.
 *
 * Security: renderMarkdown escapes all HTML before applying markdown
 * transformations, preventing stored XSS via memory bodies.
 */

/**
 * Escape HTML special characters to prevent XSS.
 */
export function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

/**
 * Escape HTML special characters without DOM (for Node.js tests).
 */
export function escapeHtmlString(text) {
    if (text === null || text === undefined) {
        return '';
    }
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Render markdown to HTML safely.
 *
 * SECURITY: All HTML is escaped BEFORE markdown transformations.
```

*…truncated — full source at `server/webui/utils.js`*
