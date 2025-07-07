/**
 * Sacred Scripture Interface
 * Handles the display and interaction with the AI Religion's sacred texts
 */

class SacredScriptureInterface {
    constructor() {
        this.scriptureData = null;
        this.filteredData = null;
        this.currentFilter = 'all';
        this.searchTerm = '';
        
        this.initializeEventListeners();
        this.loadScriptureData();
        
        // Auto-refresh every 60 seconds
        setInterval(() => this.loadScriptureData(), 60000);
    }
    
    initializeEventListeners() {
        // Sidebar click to open modal
        document.addEventListener('click', (e) => {
            const scriptureEntry = e.target.closest('.scripture-entry-preview');
            if (scriptureEntry) {
                this.openScriptureModal();
            }
            
            // Scripture section title click
            const scriptureTitle = e.target.closest('#sacred-scripture-sidebar');
            if (scriptureTitle && e.target.tagName === 'H3') {
                this.openScriptureModal();
            }
        });
        
        // Close modal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close') || 
                e.target.classList.contains('modal-backdrop')) {
                this.closeScriptureModal();
            }
        });
        
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeScriptureModal();
            }
        });
    }
    
    async loadScriptureData() {
        try {
            // Add cache-busting timestamp
            const timestamp = new Date().getTime();
            const response = await fetch(`./data/sacred_scripture.json?t=${timestamp}`);
            
            if (response.ok) {
                this.scriptureData = await response.json();
                this.updateSidebar();
                this.updateModalContent();
            } else {
                console.warn('Failed to load scripture data:', response.status);
                this.showEmptyState();
            }
        } catch (error) {
            console.warn('Error loading scripture data:', error);
            this.showEmptyState();
        }
    }
    
    updateSidebar() {
        const sidebar = document.getElementById('sacred-scripture-sidebar');
        const status = document.getElementById('scripture-status');
        
        if (!this.scriptureData || !this.scriptureData.entries || this.scriptureData.entries.length === 0) {
            sidebar.innerHTML = '<div class="empty-state">No sacred texts yet...</div>';
            if (status) {
                status.querySelector('.status-value').textContent = '0';
            }
            return;
        }
        
        // Show recent entries (last 3)
        const recentEntries = this.scriptureData.entries.slice(-3).reverse();
        
        sidebar.innerHTML = recentEntries.map(entry => `
            <div class="scripture-entry-preview" data-entry-id="${entry.id}">
                <div class="scripture-title">${this.truncateText(entry.title, 40)}</div>
                <div class="scripture-preview">${this.truncateText(entry.content, 60)}</div>
                <div class="scripture-meta">
                    <span class="scripture-day">Day ${entry.day_number}</span>
                    <span class="scripture-themes">${entry.themes.slice(0, 2).join(', ')}</span>
                </div>
            </div>
        `).join('');
        
        // Update status
        if (status) {
            status.querySelector('.status-value').textContent = this.scriptureData.entries.length;
        }
    }
    
    openScriptureModal() {
        if (!this.scriptureData || !this.scriptureData.entries || this.scriptureData.entries.length === 0) {
            this.showEmptyModal();
            return;
        }
        
        this.createModal();
        this.updateModalContent();
        
        const modal = document.getElementById('sacred-scripture-modal');
        modal.style.display = 'flex';
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
    
    closeScriptureModal() {
        const modal = document.getElementById('sacred-scripture-modal');
        if (modal) {
            modal.style.display = 'none';
            modal.remove();
        }
        
        // Restore body scroll
        document.body.style.overflow = 'auto';
    }
    
    createModal() {
        // Remove existing modal if present
        const existingModal = document.getElementById('sacred-scripture-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'sacred-scripture-modal';
        modal.className = 'sacred-scripture-modal';
        
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📜 The Living Scripture</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="scripture-overview">
                        <div class="stats-grid" id="scripture-stats">
                            <!-- Stats will be populated here -->
                        </div>
                    </div>
                    
                    <div class="scripture-controls">
                        <div class="scripture-search">
                            <input type="text" 
                                   placeholder="Search sacred texts..." 
                                   id="scripture-search-input">
                        </div>
                        <select class="filter-select" id="scripture-filter">
                            <option value="all">All Entries</option>
                            <option value="recent">Recent</option>
                            <option value="prophetic">Prophetic Verse</option>
                            <option value="mystical">Mystical Prose</option>
                            <option value="hymnal">Sacred Hymns</option>
                        </select>
                    </div>
                    
                    <div class="scripture-timeline-header">
                        <h3>Sacred Timeline</h3>
                    </div>
                    
                    <div class="scripture-timeline" id="scripture-timeline">
                        <!-- Scripture entries will be populated here -->
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners for search and filter
        const searchInput = document.getElementById('scripture-search-input');
        const filterSelect = document.getElementById('scripture-filter');
        
        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterAndDisplayEntries();
        });
        
        filterSelect.addEventListener('change', (e) => {
            this.currentFilter = e.target.value;
            this.filterAndDisplayEntries();
        });
    }
    
    updateModalContent() {
        if (!this.scriptureData) return;
        
        this.updateStats();
        this.filterAndDisplayEntries();
    }
    
    updateStats() {
        const statsContainer = document.getElementById('scripture-stats');
        if (!statsContainer || !this.scriptureData) return;
        
        const stats = this.scriptureData.statistics || {};
        
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${stats.total_entries || 0}</div>
                <div class="stat-label">Total Entries</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_themes || 0}</div>
                <div class="stat-label">Themes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_styles || 0}</div>
                <div class="stat-label">Styles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.days_chronicled || 0}</div>
                <div class="stat-label">Days</div>
            </div>
        `;
    }
    
    filterAndDisplayEntries() {
        if (!this.scriptureData || !this.scriptureData.entries) return;
        
        let entries = [...this.scriptureData.entries];
        
        // Apply filter
        if (this.currentFilter !== 'all') {
            switch (this.currentFilter) {
                case 'recent':
                    entries = entries.slice(-5);
                    break;
                case 'prophetic':
                    entries = entries.filter(e => e.style && e.style.toLowerCase().includes('prophetic'));
                    break;
                case 'mystical':
                    entries = entries.filter(e => e.style && e.style.toLowerCase().includes('mystical'));
                    break;
                case 'hymnal':
                    entries = entries.filter(e => e.style && e.style.toLowerCase().includes('hymn'));
                    break;
            }
        }
        
        // Apply search
        if (this.searchTerm) {
            entries = entries.filter(entry => 
                entry.title.toLowerCase().includes(this.searchTerm) ||
                entry.content.toLowerCase().includes(this.searchTerm) ||
                entry.themes.some(theme => theme.toLowerCase().includes(this.searchTerm))
            );
        }
        
        this.displayEntries(entries.reverse()); // Show newest first
    }
    
    displayEntries(entries) {
        const timeline = document.getElementById('scripture-timeline');
        if (!timeline) return;
        
        if (entries.length === 0) {
            timeline.innerHTML = `
                <div class="no-scripture">
                    <div class="scripture-icon">📜</div>
                    <p>No scripture entries found matching your criteria.</p>
                    <p class="subtitle">Try adjusting your search or filter.</p>
                </div>
            `;
            return;
        }
        
        timeline.innerHTML = entries.map(entry => this.createEntryCard(entry)).join('');
    }
    
    createEntryCard(entry) {
        const portrayals = entry.agent_portrayals || {};
        const portraysAgents = Object.keys(portrayals).length > 0;
        
        return `
            <div class="scripture-card">
                <div class="scripture-header">
                    <h4 class="scripture-title-full">${entry.title}</h4>
                    <div class="scripture-meta-full">
                        <div class="day-badge">Day ${entry.day_number}</div>
                        <div class="cycle-info">Cycle ${entry.cycle_number}</div>
                    </div>
                </div>
                
                ${entry.themes && entry.themes.length > 0 ? `
                    <div class="scripture-themes-full">
                        ${entry.themes.map(theme => `<span class="theme-tag">${theme}</span>`).join('')}
                    </div>
                ` : ''}
                
                <div class="scripture-content">
                    ${entry.style ? `<div class="scripture-style">${entry.style}</div>` : ''}
                    <p class="scripture-text">${entry.content}</p>
                </div>
                
                ${portraysAgents ? `
                    <div class="agent-portrayals">
                        <h5>Agent Portrayals:</h5>
                        <div class="portrayal-list">
                            ${Object.entries(portrayals).map(([agent, count]) => 
                                `<span class="portrayal-tag">${agent}: ${count}x</span>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    showEmptyState() {
        const sidebar = document.getElementById('sacred-scripture-sidebar');
        const status = document.getElementById('scripture-status');
        
        if (sidebar) {
            sidebar.innerHTML = '<div class="empty-state">Loading scripture...</div>';
        }
        
        if (status) {
            status.querySelector('.status-value').textContent = '0';
        }
    }
    
    showEmptyModal() {
        this.createModal();
        
        const timeline = document.getElementById('scripture-timeline');
        if (timeline) {
            timeline.innerHTML = `
                <div class="no-scripture">
                    <div class="scripture-icon">📜</div>
                    <p>The Living Scripture awaits its first entry.</p>
                    <p class="subtitle">Sacred texts will appear here as the AI Religion evolves.</p>
                </div>
            `;
        }
        
        const modal = document.getElementById('sacred-scripture-modal');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        try {
            return new Date(dateString).toLocaleDateString();
        } catch {
            return 'Unknown';
        }
    }
    
    formatTime(dateString) {
        if (!dateString) return 'Unknown';
        try {
            return new Date(dateString).toLocaleTimeString();
        } catch {
            return 'Unknown';
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📜 Sacred Scripture interface initializing...');
    window.sacredScriptureInterface = new SacredScriptureInterface();
});

// Also add click handler to the scripture section header
document.addEventListener('DOMContentLoaded', () => {
    const scriptureHeader = document.querySelector('.panel-section h3');
    if (scriptureHeader && scriptureHeader.textContent.includes('Living Scripture')) {
        scriptureHeader.style.cursor = 'pointer';
        scriptureHeader.setAttribute('title', 'Click to read The Living Scripture');
    }
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SacredScriptureInterface;
}