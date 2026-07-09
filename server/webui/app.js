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

async function performSearch() {
    const query = document.getElementById('search-input').value;
    const type = document.getElementById('filter-type').value;
    const status = document.getElementById('filter-status').value;
    
    if (!query.trim()) {
        showToast('Please enter a search query', 'error');
        return;
    }
    
    const btn = document.getElementById('search-btn');
    btn.classList.add('loading');
    
    try {
        const params = new URLSearchParams({
            query,
            ...(type && { type }),
            ...(status && { status }),
        });
        
        const response = await apiFetch(`${API_BASE}/search?${params}`, {
            headers: { 'Accept': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Search failed');
        
        const results = await response.json();
        displayResults(results);
    } catch (error) {
        showToast('Search failed: ' + error.message, 'error');
    } finally {
        btn.classList.remove('loading');
    }
}

function displayResults(results) {
    const container = document.getElementById('results-list');
    const count = document.getElementById('result-count');
    
    memories = results;
    count.textContent = results.length;
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◇</div>
                <p>No memories found. Try a different search.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = results.map(mem => `
        <div class="result-item" onclick="showDetail('${mem.id}')">
            <div class="result-content">
                <div class="result-name">${escapeHtml(mem.name)}</div>
                <div class="result-desc">${escapeHtml(mem.description)}</div>
                <div class="result-meta">
                    <span class="tag">${mem.type}</span>
                    <span class="status-badge status-${mem.status}">${mem.status}</span>
                    ${(mem.tags || []).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// Detail view
async function showDetail(memoryId) {
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-content');
    
    panel.style.display = 'block';
    content.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await apiFetch(`${API_BASE}/get/${memoryId}`, {
            headers: { 'Accept': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to fetch memory');
        
        const memory = await response.json();
        currentMemory = memory;
        
        content.innerHTML = `
            <div class="detail-meta">
                <div class="detail-meta-item">
                    <span class="detail-meta-label">Type</span>
                    <span class="detail-meta-value">${memory.type}</span>
                </div>
                <div class="detail-meta-item">
                    <span class="detail-meta-label">Status</span>
                    <span class="detail-meta-value"><span class="status-badge status-${memory.status}">${memory.status}</span></span>
                </div>
                <div class="detail-meta-item">
                    <span class="detail-meta-label">Owner</span>
                    <span class="detail-meta-value">${memory.owner_id}</span>
                </div>
                <div class="detail-meta-item">
                    <span class="detail-meta-label">Created</span>
                    <span class="detail-meta-value">${new Date(memory.created_at).toLocaleString()}</span>
                </div>
            </div>
            <div class="detail-body">
                ${renderMarkdown(memory.body)}
            </div>
            ${memory.tags && memory.tags.length > 0 ? `
                <div class="detail-tags">
                    ${memory.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
        `;
        
        // Setup action buttons
        document.getElementById('verify-btn').onclick = () => verifyMemory(memoryId);
        document.getElementById('archive-btn').onclick = () => archiveMemory(memoryId);
        document.getElementById('refute-btn').onclick = () => refuteMemory(memoryId);
        
    } catch (error) {
        showToast('Failed to load memory: ' + error.message, 'error');
        content.innerHTML = '<div class="error">Failed to load memory</div>';
    }
}

// Create form
function initCreateForm() {
    const form = document.getElementById('create-form');
    form.addEventListener('submit', handleCreate);
}

async function handleCreate(e) {
    e.preventDefault();
    
    const btn = e.target.querySelector('button[type="submit"]');
    btn.classList.add('loading');
    
    const data = {
        name: document.getElementById('mem-name').value,
        type: document.getElementById('mem-type').value,
        description: document.getElementById('mem-desc').value,
        body: document.getElementById('mem-body').value,
        tags: document.getElementById('mem-tags').value.split(',').map(t => t.trim()).filter(t => t),
    };
    
    try {
        const response = await apiFetch(`${API_BASE}/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to save memory');
        
        const result = await response.json();
        showToast('Memory saved successfully!', 'success');
        form.reset();
    } catch (error) {
        showToast('Failed to save memory: ' + error.message, 'error');
    } finally {
        btn.classList.remove('loading');
    }
}

// Actions
async function verifyMemory(id) {
    await performAction('verify', id, 'Memory verified');
}

async function archiveMemory(id) {
    await performAction('archive', id, 'Memory archived');
}

async function refuteMemory(id) {
    const reason = prompt('Why are you refuting this memory?');
    if (!reason) return;
    
    await performAction('refute', id, 'Memory refuted', { reason });
}

async function performAction(action, id, successMsg, extra = {}) {
    try {
        const response = await apiFetch(`${API_BASE}/${action}/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(extra)
        });
        
        if (!response.ok) throw new Error('Action failed');
        
        showToast(successMsg, 'success');
        if (currentMemory && currentMemory.id === id) {
            showDetail(id); // Refresh detail
        }
    } catch (error) {
        showToast(`Failed: ${error.message}`, 'error');
    }
}

// Theme toggle
function initThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    let dark = true;
    
    btn.addEventListener('click', () => {
        dark = !dark;
        document.body.style.setProperty('--bg-primary', dark ? '#0a0e17' : '#f9fafb');
        document.body.style.setProperty('--text-primary', dark ? '#e5e7eb' : '#111827');
        showToast(dark ? 'Dark theme enabled' : 'Light theme enabled', 'info');
    });
}

// Utilities
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    // Simple markdown renderer
    return text
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
