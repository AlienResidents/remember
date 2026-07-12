---
type: Source Code
description: "// REMEMBER Web UI — Main Application"
resource: server/webui/app.js
timestamp: 2026-07-12T02:15:00Z
---

# app

Source path: `server/webui/app.js`

## Content

```javascript
// REMEMBER Web UI — Main Application

const API_BASE = window.location.origin + '/api';

import { escapeHtml, renderMarkdown } from './utils.js';

// State
let memories = [];
let currentMemory = null;

// URL state management — encodes search query + filters + selected memory
// as query params so refresh preserves state and memory URLs are shareable.
// Schema: ?q=<query>&type=<type>&status=<status>&memory=<id>
function getUrlState() {
    const params = new URLSearchParams(window.location.search);
    return {
        q: params.get('q') || '',
        type: params.get('type') || '',
        status: params.get('status') || '',
        memory: params.get('memory') || '',
    };
}

function getCurrentSearchState() {
    return {
        q: document.getElementById('search-input').value,
        type: document.getElementById('filter-type').value,
        status: document.getElementById('filter-status').value,
    };
}

function updateUrl(state, { push = false } = {}) {
    const params = new URLSearchParams();
    if (state.q) params.set('q', state.q);
    if (state.type) params.set('type', state.type);
    if (state.status) params.set('status', state.status);
    if (state.memory) params.set('memory', state.memory);
    const search = params.toString();
    const url = search
        ? `${window.location.pathname}?${search}`
        : window.location.pathname;
    if (push) {
        history.pushState({}, '', url);
    } else {
        history.replaceState({}, '', url);
    }
}

function redirectToLogin() {
    // Preserve the current URL (including query params) as `next` so the user
    // returns to the same state — e.g. a shared memory deep link — after auth.
    const next = window.location.pathname + window.location.search;
    window.location.href = '/login?next=' + encodeURIComponent(next);
}

// Authenticated fetch wrapper — sends cookies and redirects to /login on 401
async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        credentials: 'same-origin',
    });
    if (response.status === 401) {
        redirectToLogin();
        throw new Error('Not authenticated — redirecting to login');
    }
    return response;
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Check auth status — redirect to /login if not authenticated.
    // Pass the current URL as `next` so the user returns to the same state
    // (e.g. a shared memory deep link) after the OAuth round-trip completes.
    try {
        const resp = await fetch('/auth/status', { credentials: 'same-origin' });
        const auth = await resp.json();
        if (!auth.authenticated) {
            redirectToLogin();
            return;
        }
    } catch {
        redirectToLogin();
        return;
    }

    initParticles();
    initSearch();
    initCreateForm();
    initThemeToggle();

    // Restore state from URL (refresh / deep-link / back-forward persistence).
    const urlState = getUrlState();
    document.getElementById('search-input').value = urlState.q;
    document.getElementById('filter-type').value = urlState.type;
    document.getElementById('filter-status').value = urlState.status;

    if (urlState.q.trim()) {
        await performSearch({ pushHistory: false });
    }
    if (urlState.memory) {
        await showDetail(urlState.memory, { pushHistory: false });
    }

    window.addEventListener('popstate', handlePopState);
```

*…truncated — full source at `server/webui/app.js`*

## URL state management

The webui uses query-param-based routing (not hash routing) for two features:

1. **Refresh persistence** — search query + filters + selected memory survive page refresh. On `DOMContentLoaded`, `getUrlState()` parses `?q=&type=&status=&memory=` from the URL, populates the search form, auto-runs `performSearch()` if `q` is present, and opens the detail panel if `memory` is present.

2. **Shareable memory URLs** — `?memory=<id>` opens a specific memory directly. The "Copy link" button (`copyLink()`) copies `${origin}/?memory=<id>` to the clipboard (search params excluded — those are personal context, not part of the shareable link).

### History semantics

- **`performSearch()`** → `replaceState` (don't spam history with each search; also closes detail panel for fresh context).
- **`showDetail()` user click** → `pushState` (back button returns to search results without memory open).
- **`showDetail()` on initial load / popstate** → `replaceState` / no URL update (responding to URL change, not initiating one).
- **`handlePopState()`** → re-renders detail panel from URL: opens memory if `?memory=` present, closes panel otherwise. Does NOT update URL (prevents pushState loop).

### Auth redirect preservation

`redirectToLogin()` passes the current URL (pathname + search) as `?next=` to `/login`. The server stores `next` in the session and redirects to it after `/auth/callback`. This ensures shared memory deep links work for unauthenticated recipients — they land on the same memory after logging in.