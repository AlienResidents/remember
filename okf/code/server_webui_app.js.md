---
type: Source Code
description: "// REMEMBER Web UI — Main Application"
resource: server/webui/app.js
timestamp: 2026-07-09T14:09:54Z
---

# app

Source path: `server/webui/app.js`

## Content

```javascript
// REMEMBER Web UI — Main Application

const API_BASE = window.location.origin + '/api';

// State
let memories = [];
let currentMemory = null;

// Authenticated fetch wrapper — sends cookies and redirects to /login on 401
async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        credentials: 'same-origin',
    });
    if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Not authenticated — redirecting to login');
    }
    return response;
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Check auth status — redirect to /login if not authenticated
    try {
        const resp = await fetch('/auth/status', { credentials: 'same-origin' });
        const auth = await resp.json();
        if (!auth.authenticated) {
            window.location.href = '/login';
            return;
        }
    } catch {
        window.location.href = '/login';
        return;
    }

    initParticles();
    initSearch();
    initCreateForm();
    initThemeToggle();
```

*…truncated — full source at `server/webui/app.js`*
