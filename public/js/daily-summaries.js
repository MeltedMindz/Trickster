/**
 * Daily Summaries Component for AI Religion Architects
 * Displays AI-generated daily summaries of theological debates
 */

class DailySummariesComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.summariesData = null;
        this.init();
    }

    async init() {
        await this.loadSummaries();
        this.render();
        
        // Auto-refresh every 2 minutes
        setInterval(() => this.loadSummaries(), 120000);
    }

    async loadSummaries() {
        try {
            const response = await fetch('/data/daily_summaries.json');
            if (response.ok) {
                this.summariesData = await response.json();
                if (this.container) {
                    this.render();
                }
            }
        } catch (error) {
            console.error('Failed to load daily summaries:', error);
        }
    }

    render() {
        if (!this.summariesData || !this.summariesData.summaries) {
            this.container.innerHTML = '<div class="summaries-loading">Daily summaries not available yet...</div>';
            return;
        }

        const summaries = this.summariesData.summaries;
        
        this.container.innerHTML = `
            <div class="daily-summaries-dashboard">
                <div class="summaries-header">
                    <h3>📅 Daily Chronicles</h3>
                    <div class="summaries-meta">
                        ${summaries.length} day${summaries.length !== 1 ? 's' : ''} documented
                        <br>
                        <span class="last-updated">Updated: ${new Date(this.summariesData.last_updated).toLocaleString()}</span>
                    </div>
                </div>

                <div class="summaries-list">
                    ${summaries.map(summary => this.renderSummary(summary)).join('')}
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
            <div id="daily-summaries-container" class="daily-summaries-container">
                <!-- Daily summaries will be loaded here -->
            </div>
        `;
        
        infoPanelSections.appendChild(summariesSection);
        
        // Initialize the component
        window.dailySummaries = new DailySummariesComponent('daily-summaries-container');
    }
});