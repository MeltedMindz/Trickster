/**
 * Agent Journal Popup System
 * Creates popup modals to display private agent journal entries
 */

class AgentJournalPopup {
    constructor() {
        this.journalData = null;
        this.currentPopup = null;
        this.init();
    }

    init() {
        this.loadJournalData();
        this.setupJournalClickListeners();
        
        // Auto-refresh journal data every 30 seconds
        setInterval(() => this.loadJournalData(), 30000);
    }

    async loadJournalData() {
        try {
            const response = await fetch('/data/agent_journals.json');
            if (response.ok) {
                const data = await response.json();
                this.journalData = data.journals || {};
            }
        } catch (error) {
            console.error('Failed to load agent journal data:', error);
        }
    }

    setupJournalClickListeners() {
        // Add click listeners to journal links
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('journal-link')) {
                e.preventDefault();
                e.stopPropagation(); // Prevent triggering the agent memory popup
                
                const agentName = e.target.getAttribute('data-agent');
                if (agentName) {
                    this.showJournalPopup(agentName);
                }
            }
        });
    }

    showJournalPopup(agentName) {
        if (!this.journalData) {
            this.showErrorPopup(`Journal data not available yet.`);
            return;
        }

        const journals = this.journalData[agentName];
        if (!journals || journals.length === 0) {
            this.showErrorPopup(`${agentName} has not written any journal entries yet.`);
            return;
        }

        this.createPopup(agentName, journals);
    }

    createPopup(agentName, journals) {
        // Remove existing popup if any
        this.closePopup();

        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.className = 'journal-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        // Create popup content
        const popup = document.createElement('div');
        popup.className = 'journal-popup';
        popup.innerHTML = this.generatePopupContent(agentName, journals);

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
    }

    generatePopupContent(agentName, journals) {
        const totalEntries = journals.length;
        
        // Generate journal entries HTML
        const journalEntriesHtml = journals.map(journal => {
            const date = new Date(journal.timestamp);
            const formattedDate = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            return `
                <div class="journal-entry">
                    <div class="journal-header">
                        <span class="journal-cycle">Cycle ${journal.cycle_number}</span>
                        <span class="journal-date">${formattedDate}</span>
                    </div>
                    <div class="journal-content">
                        ${journal.journal_entry.split('\n').map(para => 
                            para.trim() ? `<p>${para}</p>` : ''
                        ).join('')}
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="popup-header">
                <h2>📔 ${agentName}'s Private Journal</h2>
                <button class="popup-close">×</button>
            </div>
            <div class="popup-subheader">
                <span class="entry-count">${totalEntries} ${totalEntries === 1 ? 'entry' : 'entries'}</span>
                <span class="privacy-notice">🔒 Private thoughts never shared in debates</span>
            </div>
            <div class="popup-body journal-entries">
                ${journalEntriesHtml}
            </div>
        `;
    }

    showErrorPopup(message) {
        // Remove existing popup if any
        this.closePopup();

        const overlay = document.createElement('div');
        overlay.className = 'journal-popup-overlay';
        overlay.addEventListener('click', () => this.closePopup());

        const popup = document.createElement('div');
        popup.className = 'journal-popup error-popup';
        popup.innerHTML = `
            <div class="popup-header">
                <h2>📔 Journal Not Available</h2>
                <button class="popup-close">×</button>
            </div>
            <div class="popup-body">
                <p>${message}</p>
                <p>Journals are written every 24 cycles. Check back later!</p>
            </div>
        `;

        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        this.currentPopup = overlay;

        const closeBtn = popup.querySelector('.popup-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closePopup());
        }
    }

    handleEscapeKey(e) {
        if (e.key === 'Escape') {
            this.closePopup();
        }
    }

    closePopup() {
        if (this.currentPopup) {
            this.currentPopup.remove();
            this.currentPopup = null;
            document.removeEventListener('keydown', this.handleEscapeKey.bind(this));
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.agentJournalPopup = new AgentJournalPopup();
});