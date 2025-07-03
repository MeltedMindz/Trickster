/**
 * Daily Summaries Component for AI Religion Architects
 * Displays AI-generated daily summaries of theological debates
 */

class DailySummariesComponent {
    constructor() {
        this.summariesData = null;
        this.currentPopup = null;
        this.init();
    }

    async init() {
        await this.loadSummaries();
        this.setupChroniclesClickListeners();
        
        // Auto-refresh every 2 minutes
        setInterval(() => this.loadSummaries(), 120000);
    }

    async loadSummaries() {
        try {
            const response = await fetch('/data/daily_summaries.json');
            if (response.ok) {
                this.summariesData = await response.json();
                this.updateChroniclesSection();
            }
        } catch (error) {
            console.error('Failed to load daily summaries:', error);
        }
    }

    setupChroniclesClickListeners() {
        // Add click listener to daily chronicles section
        document.addEventListener('click', (e) => {
            const chroniclesHeader = e.target.closest('.panel-section h3');
            if (chroniclesHeader && chroniclesHeader.textContent.includes('Daily Chronicles')) {
                this.showChroniclesPopup();
            }
            
            // Also handle clicks on chronicles container
            const chroniclesContainer = e.target.closest('#daily-chronicles-container');
            if (chroniclesContainer) {
                this.showChroniclesPopup();
            }
        });
    }

    updateChroniclesSection() {
        const chroniclesContainer = document.getElementById('daily-chronicles-container');
        if (!chroniclesContainer) return;

        if (!this.summariesData || !this.summariesData.summaries || this.summariesData.summaries.length === 0) {
            chroniclesContainer.innerHTML = `
                <div class="chronicles-preview">
                    <div class="chronicles-status">No daily summaries yet...</div>
                    <div class="chronicles-hint">Daily summaries will appear after 24 cycles</div>
                </div>
            `;
            return;
        }

        const summaries = this.summariesData.summaries;
        const latestSummary = summaries[summaries.length - 1];
        
        chroniclesContainer.innerHTML = `
            <div class="chronicles-preview clickable-chronicles" title="Click to view all daily chronicles">
                <div class="chronicles-status">
                    ${summaries.length} day${summaries.length !== 1 ? 's' : ''} documented
                </div>
                <div class="chronicles-latest">
                    <strong>Latest:</strong> ${this.extractDayTitle(latestSummary.summary)}
                </div>
                <div class="chronicles-hint">📖 Click to read full chronicles</div>
            </div>
        `;
    }

    showChroniclesPopup() {
        if (!this.summariesData || !this.summariesData.summaries || this.summariesData.summaries.length === 0) {
            this.showErrorPopup('Daily chronicles not available yet. Summaries are generated every 24 cycles.');
            return;
        }

        this.createChroniclesPopup();
    }

    createChroniclesPopup() {
        // Remove existing popup if any
        this.closePopup();

        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.className = 'chronicles-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        // Create popup content
        const popup = document.createElement('div');
        popup.className = 'chronicles-popup';
        popup.innerHTML = this.generateChroniclesContent();

        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        this.currentPopup = overlay;

        // Close on escape key
        document.addEventListener('keydown', this.handleEscapeKey.bind(this));

        // Add close button listener
        const closeBtn = popup.querySelector('.popup-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closePopup());
        }

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    generateChroniclesContent() {
        const summaries = this.summariesData.summaries;
        
        return `
            <div class="popup-header">
                <div class="popup-title">
                    📅 Daily Chronicles - AI Theological Evolution
                </div>
                <button class="popup-close" aria-label="Close chronicles">✕</button>
            </div>
            
            <div class="popup-content">
                <div class="chronicles-meta">
                    <div class="chronicles-stats">
                        <div class="stat">
                            <span class="stat-label">Total Days:</span>
                            <span class="stat-value">${summaries.length}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Latest Update:</span>
                            <span class="stat-value">${new Date(this.summariesData.last_updated).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                
                <div class="chronicles-list">
                    ${summaries.map(summary => this.renderChronicle(summary)).join('')}
                </div>
            </div>
        `;
    }

    renderChronicle(summary) {
        const dayTitle = this.extractDayTitle(summary.summary);
        const summaryText = this.extractSummaryText(summary.summary);
        
        return `
            <div class="chronicle-item" data-day="${summary.day}">
                <div class="chronicle-header">
                    <div class="day-badge">Day ${summary.day}</div>
                    <div class="day-title">${dayTitle}</div>
                    <div class="chronicle-meta">
                        Cycles ${summary.cycles[0]}-${summary.cycles[summary.cycles.length - 1]} 
                        (${summary.cycles.length} cycles)
                    </div>
                </div>
                
                <div class="chronicle-content">
                    <div class="chronicle-text">${summaryText}</div>
                    
                    <div class="chronicle-stats">
                        <div class="stat-item">
                            <span class="stat-label">Outcomes:</span>
                            <span class="stat-details">
                                ${Object.entries(summary.stats.outcomes).map(([outcome, count]) => 
                                    `<span class="outcome-badge outcome-${outcome.toLowerCase()}">${outcome}: ${count}</span>`
                                ).join(' ')}
                            </span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">Most Active Agent:</span>
                            <span class="stat-details">
                                ${this.getMostActive(summary.stats.proposers)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderSummary(summary) {
        const dayTitle = this.extractDayTitle(summary.summary);
        const summaryText = this.extractSummaryText(summary.summary);
        
        return `
            <div class="summary-item" data-day="${summary.day}">
                <div class="summary-header">
                    <div class="day-number">Day ${summary.day}</div>
                    <div class="day-title">${dayTitle}</div>
                    <div class="summary-stats">
                        Cycles ${summary.cycles[0]}-${summary.cycles[summary.cycles.length - 1]} 
                        (${summary.cycles.length} total)
                    </div>
                </div>
                
                <div class="summary-content">
                    <div class="summary-text">${summaryText}</div>
                    
                    <div class="summary-metrics">
                        <div class="metric">
                            <span class="metric-label">Outcomes:</span>
                            <span class="metric-value">
                                ${Object.entries(summary.stats.outcomes).map(([outcome, count]) => 
                                    `${outcome}: ${count}`
                                ).join(', ')}
                            </span>
                        </div>
                        
                        <div class="metric">
                            <span class="metric-label">Most Active:</span>
                            <span class="metric-value">
                                ${this.getMostActive(summary.stats.proposers)}
                            </span>
                        </div>
                        
                        <div class="metric">
                            <span class="metric-label">Proposal Types:</span>
                            <span class="metric-value">
                                ${Object.keys(summary.stats.proposal_types).join(', ')}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    extractDayTitle(summary) {
        // Extract title after "Day X: "
        const match = summary.match(/^Day \d+:\s*([^\n\r]+)/);
        return match ? match[1] : 'Theological Evolution';
    }

    extractSummaryText(summary) {
        // Remove the title line and return the rest
        const lines = summary.split('\n').filter(line => line.trim());
        return lines.slice(1).join(' ').trim();
    }

    getMostActive(proposers) {
        if (!proposers || Object.keys(proposers).length === 0) return 'Unknown';
        
        const sorted = Object.entries(proposers).sort(([,a], [,b]) => b - a);
        const [agent, count] = sorted[0];
        return `${agent} (${count} proposals)`;
    }

    showErrorPopup(message) {
        // Remove existing popup if any
        this.closePopup();

        const overlay = document.createElement('div');
        overlay.className = 'chronicles-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        const popup = document.createElement('div');
        popup.className = 'chronicles-popup error-popup';
        popup.innerHTML = `
            <div class="popup-header">
                <div class="popup-title">⚠️ Chronicles Error</div>
                <button class="popup-close" aria-label="Close popup">✕</button>
            </div>
            <div class="popup-content">
                <p>${message}</p>
            </div>
        `;

        const closeBtn = popup.querySelector('.popup-close');
        closeBtn.addEventListener('click', () => this.closePopup());

        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        this.currentPopup = overlay;

        document.addEventListener('keydown', this.handleEscapeKey.bind(this));
        document.body.style.overflow = 'hidden';
    }

    closePopup() {
        if (this.currentPopup) {
            this.currentPopup.remove();
            this.currentPopup = null;
            document.body.style.overflow = '';
            document.removeEventListener('keydown', this.handleEscapeKey.bind(this));
        }
    }

    handleEscapeKey(e) {
        if (e.key === 'Escape') {
            this.closePopup();
        }
    }
}

// Initialize daily summaries component when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if we should add daily summaries to the info panel
    const infoPanelSections = document.querySelector('.info-panel');
    if (infoPanelSections) {
        // Add daily summaries section to info panel
        const summariesSection = document.createElement('div');
        summariesSection.className = 'panel-section';
        summariesSection.innerHTML = `
            <h3>📅 Daily Chronicles</h3>
            <div id="daily-chronicles-container" class="daily-chronicles-container">
                <!-- Daily chronicles will be loaded here -->
            </div>
        `;
        
        infoPanelSections.appendChild(summariesSection);
        
        // Initialize the component
        window.dailySummaries = new DailySummariesComponent();
    }
});