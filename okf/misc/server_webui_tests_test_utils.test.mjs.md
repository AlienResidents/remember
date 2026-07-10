---
type: Other
description: "/**"
resource: server/webui/tests/test_utils.test.mjs
timestamp: 2026-07-10T02:44:34Z
---

# test utils.test

Source path: `server/webui/tests/test_utils.test.mjs`

## Content

/**
 * Tests for web UI utility functions — XSS prevention.
 *
 * Run with: node --test server/webui/tests/test_utils.test.mjs
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

import { escapeHtmlString, renderMarkdown } from '../utils.js';

describe('escapeHtmlString', () => {
    test('escapes < and >', () => {
        assert.equal(
            escapeHtmlString('<script>alert(1)</script>'),
            '&lt;script&gt;alert(1)&lt;/script&gt;',
        );
    });

    test('escapes & to prevent entity injection', () => {
        assert.equal(escapeHtmlString('a & b'), 'a &amp; b');
    });

    test('escapes double quotes', () => {
        assert.equal(escapeHtmlString('"hello"'), '&quot;hello&quot;');
    });

    test('escapes single quotes', () => {
        assert.equal(escapeHtmlString("it's"), 'it&#039;s');
    });

    test('handles null/undefined', () => {
        assert.equal(escapeHtmlString(null), '');
        assert.equal(escapeHtmlString(undefined), '');
    });

    test('handles numbers', () => {
        assert.equal(escapeHtmlString(42), '42');
    });
});

describe('renderMarkdown — XSS prevention', () => {
    test('escapes script tags in memory body', () => {
        const malicious = '<script>alert(document.cookie)</script>';
        const result = renderMarkdown(malicious);
        assert.equal(result, '&lt;script&gt;alert(document.cookie)&lt;/script&gt;');
        // Critical: no raw <script> tag survives
        assert.ok(!result.includes('<script>'));
    });

    test('escapes img onerror XSS', () => {
        const malicious = '<img src=x onerror=alert(1)>';
        const result = renderMarkdown(malicious);
        // Critical: the <img tag must not survive as an HTML element
        assert.ok(!result.includes('<img'));
        assert.ok(result.includes('&lt;img'));
    });

    test('escapes event handlers in markdown headings', () => {
        const malicious = '### <img src=x onerror=alert(1)>';
        const result = renderMarkdown(malicious);
        // The <h3> tag is our markdown output (safe)
        assert.ok(result.includes('<h3>'));
        // The <img tag must be escaped — no raw HTML elements from user content
        assert.ok(!result.includes('<img'));
        assert.ok(result.includes('&lt;img'));
    });

    test('preserves markdown bold after escaping', () => {
        const result = renderMarkdown('**bold text**');
        assert.ok(result.includes('<strong>bold text</strong>'));
    });

    test('preserves markdown italic after escaping', () => {
        const result = renderMarkdown('*italic text*');
        assert.ok(result.includes('<em>italic text</em>'));
    });

    test('preserves markdown code after escaping', () => {
        const result = renderMarkdown('`code`');
        assert.ok(result.includes('<code>code</code>'));
    });

    test('preserves markdown headings after escaping', () => {
        const result = renderMarkdown('# Heading 1\n## Heading 2\n### Heading 3');
        assert.ok(result.includes('<h1>Heading 1</h1>'));
        assert.ok(result.includes('<h2>Heading 2</h2>'));
        assert.ok(result.includes('<h3>Heading 3</h3>'));
    });

    test('escapes ampersands in markdown content', () => {
        const result = renderMarkdown('**A & B**');
        assert.ok(result.includes('<strong>A &amp; B</strong>'));
    });

    test('handles null/undefined input', () => {
        assert.equal(renderMarkdown(null), '');
        assert.equal(renderMarkdown(undefined), '');
    });

    test('does not allow breaking out of attribute via single quote', () => {
        // This tests the onclick='showDetail(...)' pattern —
        // if mem.id contained a single quote, it could break out.
        // escapeHtmlString escapes single quotes to &#039;.
        const maliciousId = "'; alert(1); '";
        const escaped = escapeHtmlString(maliciousId);
        assert.ok(!escaped.includes("'"));
        assert.ok(escaped.includes('&#039;'));
    });
});