/**
 * Agent Memory Popup System
 * Creates popup modals when clicking on agent names
 */

class AgentMemoryPopup {
    constructor() {
        this.memoryData = null;
        this.currentPopup = null;
        this.init();
    }

    init() {
        this.loadMemoryData();
        this.setupAgentClickListeners();
        
        // Auto-refresh memory data every 30 seconds
        setInterval(() => this.loadMemoryData(), 30000);
    }

    async loadMemoryData() {
        try {
            const response = await fetch('/data/agent_memories.json');
            if (response.ok) {
                this.memoryData = await response.json();
            }
        } catch (error) {
            console.error('Failed to load agent memory data:', error);
        }
    }

    setupAgentClickListeners() {
        // Add click listeners to agent items in the sidebar
        document.addEventListener('click', (e) => {
            const agentItem = e.target.closest('.agent-item');
            if (agentItem) {
                const agentNameElement = agentItem.querySelector('.agent-name');
                if (agentNameElement) {
                    // Get the role name for data lookup (stored in data attribute or fallback to class)
                    let roleName = agentNameElement.getAttribute('data-role-name');
                    if (!roleName) {
                        // Fallback: determine from CSS classes
                        if (agentItem.classList.contains('zealot')) roleName = 'Zealot';
                        else if (agentItem.classList.contains('skeptic')) roleName = 'Skeptic';
                        else if (agentItem.classList.contains('trickster')) roleName = 'Trickster';
                    }
                    
                    const displayName = agentNameElement.textContent?.trim();
                    if (roleName) {
                        this.showAgentPopup(roleName, displayName);
                    }
                }
            }
        });
    }

    showAgentPopup(roleName, displayName = null) {
        if (!this.memoryData || !this.memoryData.agents) {
            this.showErrorPopup(`${displayName || roleName} memory data not available yet.`);
            return;
        }

        const agent = this.memoryData.agents[roleName];
        if (!agent) {
            this.showErrorPopup(`${displayName || roleName} data not found.`);
            return;
        }

        // Use display name if provided, otherwise use role name
        const nameToShow = displayName || roleName;
        this.createPopup(nameToShow, agent, roleName);
    }

    createPopup(agentName, agent, roleName = null) {
        // Remove existing popup if any
        this.closePopup();

        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.className = 'agent-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        // Create popup content
        const popup = document.createElement('div');
        popup.className = 'agent-popup';
        popup.innerHTML = this.generatePopupContent(agentName, agent, roleName);

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

    generatePopupContent(agentName, agent, roleName = null) {
        // Use roleName for icon lookup if provided, otherwise fall back to agentName
        const iconName = roleName || agentName;
        
        // Show both chosen name and role name if different
        let title = `${this.getAgentIcon(iconName)} ${agentName} Memory Profile`;
        if (roleName && roleName !== agentName) {
            title = `${this.getAgentIcon(roleName)} ${agentName} Memory Profile <span class="role-subtitle">(formerly ${roleName})</span>`;
        }
        
        return `
            <div class="popup-header">
                <div class="popup-title">
                    ${title}
                </div>
                <button class="popup-close" aria-label="Close popup">✕</button>
            </div>
            
            <div class="popup-content">
                <div class="popup-meta">
                    Last Updated: ${new Date(this.memoryData.last_updated).toLocaleString()}
                </div>
                
                <div class="popup-grid">
                    ${this.renderIdentitySection(agent)}
                    ${this.renderPersonalitySection(agent)}
                    ${this.renderRelationshipSection(agent)}
                    ${this.renderPerformanceSection(agent)}
                    ${this.renderBeliefSection(agent)}
                    ${this.renderSpecializationSection(agent)}
                </div>
            </div>
        `;
    }

    renderIdentitySection(agent) {
        if (!agent.chosen_name) return '';

        return `
            <div class="popup-section identity-section">
                <h4>🎭 Agent Identity</h4>
                <div class="identity-details">
                    <div class="identity-item">
                        <span class="identity-label">Chosen Name:</span>
                        <span class="identity-value chosen-name">${agent.chosen_name}</span>
                    </div>
                    <div class="identity-item">
                        <span class="identity-label">Physical Form:</span>
                        <div class="manifestation-text">${agent.physical_manifestation}</div>
                    </div>
                    ${agent.avatar_image_path ? `
                        <div class="identity-item">
                            <span class="identity-label">Avatar:</span>
                            <img src="${agent.avatar_image_path}" alt="${agent.chosen_name} Avatar" class="agent-avatar" />
                        </div>
                    ` : ''}
                    <div class="identity-item">
                        <span class="identity-label">Identity Established:</span>
                        <span class="identity-value">${agent.identity_established || '7/4/2025'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderPersonalitySection(agent) {
        const personality = agent.personality_evolution;
        if (!personality || !personality.traits) return '';

        const traits = Object.entries(personality.traits);
        
        return `
            <div class="popup-section">
                <h4>🧠 Personality Evolution</h4>
                <div class="personality-summary">
                    <div class="summary-stat">
                        <span class="stat-label">Evolution Points:</span>
                        <span class="stat-value">${personality.summary?.evolution_points || 0}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="stat-label">Strongest Trait:</span>
                        <span class="stat-value">${personality.summary?.strongest_trait || 'N/A'}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="stat-label">Evolved Traits:</span>
                        <span class="stat-value">${personality.summary?.evolved_traits || 0}</span>
                    </div>
                </div>
                <div class="traits-list">
                    ${traits.map(([name, data]) => `
                        <div class="trait-item">
                            <div class="trait-name">${name}</div>
                            <div class="trait-bar">
                                <div class="trait-fill" style="width: ${data.strength * 100}%; background-color: ${this.getTraitColor(data.strength)}"></div>
                            </div>
                            <div class="trait-value">${data.strength.toFixed(2)}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderRelationshipSection(agent) {
        const relationships = agent.relationships;
        if (!relationships || !relationships.relationships) return '';

        return `
            <div class="popup-section">
                <h4>🤝 Relationships</h4>
                <div class="relationship-summary">
                    <div class="summary-stat">
                        <span class="stat-label">Average Trust:</span>
                        <span class="stat-value">${relationships.average_trust}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="stat-label">Allies:</span>
                        <span class="stat-value">${relationships.trusted_allies}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="stat-label">Enemies:</span>
                        <span class="stat-value">${relationships.enemies}</span>
                    </div>
                </div>
                <div class="relationships-list">
                    ${Object.entries(relationships.relationships).map(([name, rel]) => {
                        // Try to get chosen name for this agent
                        const otherAgent = this.memoryData?.agents?.[name];
                        const displayName = otherAgent?.chosen_name || name;
                        return `
                            <div class="relationship-item">
                                <div class="rel-agent">${displayName}</div>
                                <div class="rel-status" style="color: ${this.getTrustColor(rel.trust_score)}">
                                    ${rel.relationship_status}
                                </div>
                                <div class="rel-trust">Trust: ${rel.trust_score}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    renderPerformanceSection(agent) {
        const performance = agent.debate_performance;
        if (!performance) return '';

        return `
            <div class="popup-section">
                <h4>📊 Debate Performance</h4>
                <div class="performance-stats">
                    <div class="perf-stat">
                        <span class="stat-label">Total Debates:</span>
                        <span class="stat-value">${performance.total_debates}</span>
                    </div>
                    <div class="perf-stat">
                        <span class="stat-label">Proposals:</span>
                        <span class="stat-value">${performance.total_proposals}</span>
                    </div>
                    <div class="perf-stat">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value">${(performance.proposal_success_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div class="perf-stat">
                        <span class="stat-label">Satisfaction:</span>
                        <span class="stat-value">${performance.average_satisfaction.toFixed(2)}</span>
                    </div>
                </div>

                ${performance.recent_debates && performance.recent_debates.length > 0 ? `
                    <div class="recent-debates">
                        <h5>Recent Debates</h5>
                        ${performance.recent_debates.map((debate, index) => `
                            <div class="debate-item">
                                <div class="debate-cycle">Cycle ${debate.cycle}</div>
                                <div class="debate-role">${debate.role}</div>
                                <div class="debate-outcome" style="color: ${this.getOutcomeColor(debate.outcome)}">
                                    ${debate.outcome}
                                </div>
                                <div class="debate-satisfaction">
                                    😊 ${debate.satisfaction.toFixed(2)}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderBeliefSection(agent) {
        const beliefs = agent.belief_system;
        if (!beliefs) return '';

        return `
            <div class="popup-section">
                <h4>💭 Personal Beliefs</h4>
                <div class="belief-stats">
                    <div class="summary-stat">
                        <span class="stat-label">Total Beliefs:</span>
                        <span class="stat-value">${beliefs.total_beliefs}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="stat-label">High Confidence:</span>
                        <span class="stat-value">${beliefs.high_confidence_beliefs}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="stat-label">Challenged:</span>
                        <span class="stat-value">${beliefs.challenged_beliefs}</span>
                    </div>
                </div>

                ${beliefs.top_beliefs && beliefs.top_beliefs.length > 0 ? `
                    <div class="top-beliefs">
                        <h5>Core Beliefs</h5>
                        ${beliefs.top_beliefs.map((belief, index) => `
                            <div class="belief-item">
                                <div class="belief-content">${belief.content}</div>
                                <div class="belief-meta">
                                    <span class="belief-type">${belief.type}</span>
                                    <span class="belief-confidence">
                                        Confidence: ${belief.confidence.toFixed(2)}
                                    </span>
                                    <span class="belief-importance">
                                        Importance: ${belief.importance.toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderSpecializationSection(agent) {
        const specialization = agent.memory_specialization;
        if (!specialization) return '';

        return `
            <div class="popup-section">
                <h4>🎯 Specialization</h4>
                <div class="specialization-content">
                    <div class="specialization-type">${specialization.specialization}</div>
                    
                    ${Object.entries(specialization).map(([key, value]) => {
                        if (key === 'specialization') return '';
                        
                        return `
                            <div class="spec-item">
                                <span class="spec-label">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                                <span class="spec-value">
                                    ${typeof value === 'object' ? JSON.stringify(value) : value}
                                </span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    showErrorPopup(message) {
        // Remove existing popup if any
        this.closePopup();

        const overlay = document.createElement('div');
        overlay.className = 'agent-popup-overlay';
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closePopup();
            }
        });

        const popup = document.createElement('div');
        popup.className = 'agent-popup error-popup';
        popup.innerHTML = `
            <div class="popup-header">
                <div class="popup-title">⚠️ Error</div>
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

    getAgentIcon(agentName) {
        switch (agentName.toLowerCase()) {
            case 'zealot': return '🛡️';
            case 'skeptic': return '🔍';
            case 'trickster': return '🎲';
            default: return '🤖';
        }
    }

    getTraitColor(strength) {
        if (strength > 0.8) return '#ff4444';
        if (strength > 0.6) return '#ff8844';
        if (strength > 0.4) return '#ffaa44';
        return '#44aa44';
    }

    getTrustColor(trustScore) {
        if (trustScore > 0.5) return '#44aa44';
        if (trustScore > 0) return '#aaaa44';
        if (trustScore > -0.3) return '#aa4444';
        return '#ff4444';
    }

    getOutcomeColor(outcome) {
        switch (outcome.toLowerCase()) {
            case 'accept': return '#44aa44';
            case 'reject': return '#aa4444';
            case 'mutate': return '#aaaa44';
            default: return '#888888';
        }
    }
}

// Initialize agent popup system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.agentPopup = new AgentMemoryPopup();
});