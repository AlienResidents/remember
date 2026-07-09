---
type: Source Code
description: "// REMEMBER Web UI — Main Application"
resource: server/webui/app.js
timestamp: 2026-07-09T01:43:40Z
---

# app

Source path: `server/webui/app.js`

## Content

```javascript
// REMEMBER Web UI — Main Application

const API_BASE = window.location.origin + '/mcp';

// State
let memories = [];
let currentMemory = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initSearch();
    initCreateForm();
    initThemeToggle();
});

// Particle background
function initParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (10 + Math.random() * 10) + 's';
        container.appendChild(particle);
    }
}

// Search
function initSearch() {
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');
    
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
}

```

*…truncated — full source at `server/webui/app.js`*
