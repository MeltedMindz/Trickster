class AgentMemoryDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.memoryData = null;
        this.selectedAgent = 'Zealot';
        this.init();
    }

    async init() {
        await this.loadMemoryData();
        this.render();
        
        // Auto-refresh every 30 seconds
        setInterval(() => this.loadMemoryData(), 30000);
    }

    async loadMemoryData() {
        try {
            const response = await fetch('/data/agent_memories.json');
            if (response.ok) {
                this.memoryData = await response.json();
                if (this.container) {
                    this.render();
                }
            }
        } catch (error) {
            console.error('Failed to load agent memory data:', error);
        }
    }

    render() {
        if (!this.memoryData || !this.memoryData.agents) {
            this.container.innerHTML = '<div class="memory-loading">Agent memory data not available yet...</div>';
            return;
        }

        const agent = this.memoryData.agents[this.selectedAgent];
        if (!agent) {
            this.container.innerHTML = '<div class="memory-error">Selected agent data not found</div>';
            return;
        }

        this.container.innerHTML = `
            <div class="agent-memory-dashboard">
                <div class="memory-header">
                    <h2>🧠 Agent Memory Dashboard</h2>
                    <div class="last-updated">
                        Last Updated: ${new Date(this.memoryData.last_updated).toLocaleString()}
                    </div>
                </div>

                <div class="agent-selector">
                    ${Object.keys(this.memoryData.agents).map(agentName => `
                        <button class="agent-btn ${agentName === this.selectedAgent ? 'active' : ''}" 
                                data-agent="${agentName}"
                                aria-label="Select ${agentName} agent">
                            ${this.getAgentIcon(agentName)} ${agentName}
                        </button>
                    `).join('')}
                </div>

                <div class="agent-profile">
                    <h3>${this.selectedAgent} Memory Profile</h3>
                    
                    <div class="memory-grid">
                        ${this.renderPersonalitySection(agent)}
                        ${this.renderRelationshipSection(agent)}
                        ${this.renderPerformanceSection(agent)}
                        ${this.renderBeliefSection(agent)}
                        ${this.renderSpecializationSection(agent)}
                    </div>
                </div>

                ${this.renderNetworkOverview()}
            </div>
        `;

        // Add event listeners
        this.container.querySelectorAll('.agent-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectedAgent = e.target.dataset.agent;
                this.render();
            });
        });
    }

    renderPersonalitySection(agent) {
        const personality = agent.personality_evolution;
        if (!personality || !personality.traits) return '';

        const traits = Object.entries(personality.traits);
        
        return `
            <div class="memory-section">
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
            <div class="memory-section">
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
                    ${Object.entries(relationships.relationships).map(([name, rel]) => `
                        <div class="relationship-item">
                            <div class="rel-agent">${name}</div>
                            <div class="rel-status" style="color: ${this.getTrustColor(rel.trust_score)}">
                                ${rel.relationship_status}
                            </div>
                            <div class="rel-trust">Trust: ${rel.trust_score}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderPerformanceSection(agent) {
        const performance = agent.debate_performance;
        if (!performance) return '';

        return `
            <div class="memory-section">
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
                        ${performance.recent_debates.map(debate => `
                            <div class="debate-item">
                                <span class="debate-cycle">C${debate.cycle}</span>
                                <span class="debate-role">${debate.role}</span>
                                <span class="debate-outcome" style="color: ${this.getOutcomeColor(debate.outcome)}">
                                    ${debate.outcome}
                                </span>
                                <span class="debate-satisfaction">😊 ${debate.satisfaction.toFixed(2)}</span>
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
            <div class="memory-section">
                <h4>💭 Personal Beliefs</h4>
                <div class="belief-summary">
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
                        ${beliefs.top_beliefs.map(belief => `
                            <div class="belief-item">
                                <div class="belief-content">"${belief.content}"</div>
                                <div class="belief-meta">
                                    <span class="belief-type">${belief.type}</span>
                                    <span class="belief-conf">Conf: ${belief.confidence.toFixed(2)}</span>
                                    <span class="belief-imp">Imp: ${belief.importance.toFixed(2)}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderSpecializationSection(agent) {
        const spec = agent.memory_specialization;
        if (!spec) return '';

        return `
            <div class="memory-section">
                <h4>🎯 ${spec.specialization || 'Specialization'}</h4>
                <div class="specialization-content">
                    ${Object.entries(spec).map(([key, value]) => {
                        if (key === 'specialization') return '';
                        return `
                            <div class="spec-item">
                                <span class="spec-label">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                                <span class="spec-value">${typeof value === 'object' ? JSON.stringify(value).substring(0, 50) + '...' : value}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    renderNetworkOverview() {
        if (!this.memoryData.relationship_network) return '';

        const network = this.memoryData.relationship_network;
        return `
            <div class="network-overview">
                <h3>🌐 Network Overview</h3>
                <div class="network-stats">
                    <div class="network-stat">
                        <span class="stat-label">Average Trust:</span>
                        <span class="stat-value">${network.average_network_trust}</span>
                    </div>
                    <div class="network-stat">
                        <span class="stat-label">Polarization:</span>
                        <span class="stat-value">${network.network_polarization}</span>
                    </div>
                    <div class="network-stat">
                        <span class="stat-label">Total Relationships:</span>
                        <span class="stat-value">${network.total_relationships}</span>
                    </div>
                </div>
            </div>
        `;
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

    getAgentIcon(agentName) {
        switch (agentName.toLowerCase()) {
            case 'zealot': return '🛡️';
            case 'skeptic': return '🔍';
            case 'trickster': return '🎲';
            default: return '🤖';
        }
    }

    formatNumberForMobile(number, decimals = 2) {
        if (typeof number !== 'number') return number;
        
        // On mobile, show shorter numbers
        if (window.innerWidth <= 480) {
            if (number >= 1000) {
                return (number / 1000).toFixed(1) + 'k';
            }
            return number.toFixed(Math.min(decimals, 1));
        }
        
        return number.toFixed(decimals);
    }

    truncateTextForMobile(text, maxLength = null) {
        if (typeof text !== 'string') return text;
        
        // Determine max length based on screen size
        if (!maxLength) {
            if (window.innerWidth <= 480) {
                maxLength = 30;
            } else if (window.innerWidth <= 768) {
                maxLength = 50;
            } else {
                return text;
            }
        }
        
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if the memory dashboard container exists
    if (document.getElementById('agent-memory-container')) {
        window.agentMemoryDashboard = new AgentMemoryDashboard('agent-memory-container');
    }
});