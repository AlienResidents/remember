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
 * This prevents stored XSS — a memory body containing
 * `<script>alert('xss')</script>` renders as escaped text, not
 * executable HTML. Markdown syntax characters (#, *, _, `, >) are
 * not HTML-special and survive escaping, so markdown still works.
 */
export function renderMarkdown(text) {
    if (text === null || text === undefined) {
        return '';
    }

    // Step 1: Escape all HTML
    const escaped = escapeHtmlString(text);

    // Step 2: Apply markdown transformations on the escaped text
    return escaped
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}