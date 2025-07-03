/**
 * Sacred Text Archive Popup System
 * Timeline of scriptures, myths, commandments, and belief revisions
 */

class SacredArchivePopup {
    constructor() {
        this.religionData = null;
        this.currentPopup = null;
        this.init();
    }

    init() {
        this.loadReligionData();
        this.setupArchiveClickListeners();
        
        // Auto-refresh religion data every 2 minutes
        setInterval(() => this.loadReligionData(), 120000);
    }

    async loadReligionData() {
        try {
            const response = await fetch('/data/religion_state.json');
            if (response.ok) {
                this.religionData = await response.json();
            }
        } catch (error) {
            console.error('Failed to load religion data:', error);
        }
    }

    setupArchiveClickListeners() {
        // Add click listener to Sacred Text Archive section header
        document.addEventListener('click', (e) => {
            const archiveSectionHeader = e.target.closest('.panel-section h3');
            if (archiveSectionHeader && archiveSectionHeader.textContent.includes('Sacred Text Archive')) {
                this.showSacredArchive();
            }
            
            // Also handle clicks on doctrine items (if any are shown)
            const doctrineItem = e.target.closest('.doctrine-item');
            if (doctrineItem) {
                this.showSacredArchive();
            }
        });
    }

    showSacredArchive() {
        if (!this.religionData) {
            this.showErrorPopup('Sacred text archive not available yet.');
            return;
        }

        this.createArchivePopup();
    }

    createArchivePopup() {
        // Remove existing popup if any
        this.closePopup();

        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.className = 'archive-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        // Create popup content
        const popup = document.createElement('div');
        popup.className = 'archive-popup';
        popup.innerHTML = this.generateArchiveContent();

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

    generateArchiveContent() {
        const timeline = this.buildTimeline();
        
        return `
            <div class="popup-header">
                <div class="popup-title">
                    📜 Sacred Text Archive - Version Control for Faith
                </div>
                <button class="popup-close" aria-label="Close archive">✕</button>
            </div>
            
            <div class="popup-content">
                <div class="archive-meta">
                    <div class="archive-stats">
                        <div class="stat">
                            <span class="stat-label">Total Doctrines:</span>
                            <span class="stat-value">${this.religionData.total_doctrines}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Rituals:</span>
                            <span class="stat-value">${this.religionData.total_rituals}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Commandments:</span>
                            <span class="stat-value">${this.religionData.total_commandments}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Last Updated:</span>
                            <span class="stat-value">${new Date(this.religionData.last_updated).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                
                <div class="timeline-container">
                    ${this.renderTimeline(timeline)}
                </div>
            </div>
        `;
    }

    buildTimeline() {
        const timeline = [];
        
        // Add doctrines
        if (this.religionData.accepted_doctrines) {
            this.religionData.accepted_doctrines.forEach((doctrine, index) => {
                timeline.push({
                    type: 'doctrine',
                    content: doctrine,
                    order: index + 1,
                    status: 'accepted',
                    icon: '📖'
                });
            });
        }

        // Add rituals
        if (this.religionData.rituals) {
            this.religionData.rituals.forEach((ritual, index) => {
                timeline.push({
                    type: 'ritual',
                    name: ritual.name,
                    content: ritual.description,
                    order: this.extractCycleNumber(ritual.name) || (index + 100),
                    status: 'active',
                    icon: '🕯️'
                });
            });
        }

        // Add commandments
        if (this.religionData.commandments) {
            this.religionData.commandments.forEach((commandment, index) => {
                timeline.push({
                    type: 'commandment',
                    content: commandment,
                    order: index + 200,
                    status: 'sacred',
                    icon: '⚖️'
                });
            });
        }

        // Sort by creation order
        timeline.sort((a, b) => a.order - b.order);
        
        return timeline;
    }

    extractCycleNumber(name) {
        const match = name.match(/(\d+)/);
        return match ? parseInt(match[1]) : null;
    }

    renderTimeline(timeline) {
        if (timeline.length === 0) {
            return '<div class="timeline-empty">No sacred texts have been created yet...</div>';
        }

        return `
            <div class="timeline">
                <div class="timeline-header">
                    <h3>📚 Chronological Evolution of Faith</h3>
                    <p>Track how the religion evolved through cycles of divine inspiration and debate</p>
                </div>
                
                <div class="timeline-items">
                    ${timeline.map((item, index) => this.renderTimelineItem(item, index)).join('')}
                </div>
                
                <div class="timeline-footer">
                    <p>🤖 All texts generated through autonomous AI theological debates</p>
                </div>
            </div>
        `;
    }

    renderTimelineItem(item, index) {
        const typeColors = {
            doctrine: '#4CAF50',
            ritual: '#ff8844',
            commandment: '#0066cc'
        };

        return `
            <div class="timeline-item ${item.type}" style="--accent-color: ${typeColors[item.type]}">
                <div class="timeline-marker">
                    <div class="marker-icon">${item.icon}</div>
                    <div class="marker-line"></div>
                </div>
                
                <div class="timeline-content">
                    <div class="timeline-header">
                        <div class="timeline-type">${item.type.toUpperCase()}</div>
                        <div class="timeline-status status-${item.status}">${item.status}</div>
                        ${item.name ? `<div class="timeline-name">${item.name}</div>` : ''}
                    </div>
                    
                    <div class="timeline-text">
                        ${this.formatContent(item.content)}
                    </div>
                    
                    <div class="timeline-meta">
                        <span class="timeline-order">#${item.order}</span>
                        <span class="timeline-type-label">${this.getTypeDescription(item.type)}</span>
                    </div>
                </div>
            </div>
        `;
    }

    formatContent(content) {
        if (content.length > 200) {
            return `
                <div class="content-preview">${content.substring(0, 200)}...</div>
                <div class="content-full" style="display: none;">${content}</div>
                <button class="expand-btn" onclick="this.previousElementSibling.style.display='block'; this.previousElementSibling.previousElementSibling.style.display='none'; this.style.display='none'; this.nextElementSibling.style.display='inline';">Read More</button>
                <button class="collapse-btn" style="display: none;" onclick="this.previousElementSibling.previousElementSibling.previousElementSibling.style.display='block'; this.previousElementSibling.previousElementSibling.style.display='none'; this.previousElementSibling.style.display='inline'; this.style.display='none';">Show Less</button>
            `;
        }
        return content;
    }

    getTypeDescription(type) {
        const descriptions = {
            doctrine: 'Core belief or teaching',
            ritual: 'Sacred practice or ceremony',
            commandment: 'Divine law or directive'
        };
        return descriptions[type] || type;
    }

    showErrorPopup(message) {
        // Remove existing popup if any
        this.closePopup();

        const overlay = document.createElement('div');
        overlay.className = 'archive-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        const popup = document.createElement('div');
        popup.className = 'archive-popup error-popup';
        popup.innerHTML = `
            <div class="popup-header">
                <div class="popup-title">⚠️ Archive Error</div>
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

// Initialize sacred archive popup system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sacredArchive = new SacredArchivePopup();
});