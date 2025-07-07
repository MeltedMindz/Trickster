/**
 * Messages from Beyond Frontend Display System
 * Handles visualization of external messages and agent reflections
 */

class MessagesBeyondDisplay {
    constructor() {
        this.messagesData = null;
        this.currentMessageIndex = 0;
        this.updateInterval = null;
        
        this.init();
    }
    
    async init() {
        await this.loadMessagesData();
        this.setupEventListeners();
        this.render();
        this.startAutoUpdate();
    }
    
    async loadMessagesData() {
        try {
            const response = await fetch('./data/messages_beyond.json');
            if (response.ok) {
                this.messagesData = await response.json();
            } else {
                // Fallback to empty data structure
                this.messagesData = {
                    messages: [],
                    agent_stats: {},
                    last_updated: new Date().toISOString()
                };
            }
        } catch (error) {
            console.warn('Messages from beyond data not available:', error);
            this.messagesData = {
                messages: [],
                agent_stats: {},
                last_updated: new Date().toISOString()
            };
        }
    }
    
    setupEventListeners() {
        // Add click handler for messages beyond button/link
        document.addEventListener('click', (e) => {
            if (e.target.matches('.messages-beyond-btn') || e.target.matches('[data-messages-beyond]')) {
                e.preventDefault();
                this.showMessagesModal();
            }
        });
        
        // ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideMessagesModal();
            }
        });
    }
    
    render() {
        this.renderMessagesSidebar();
        this.renderMessagesModal();
    }
    
    renderMessagesSidebar() {
        // Add messages indicator to main UI
        const existingIndicator = document.getElementById('messages-beyond-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        const messageCount = this.messagesData.messages.length;
        const unprocessedCount = this.messagesData.messages.filter(m => !m.processed).length;
        
        if (messageCount === 0) return;
        
        const indicator = document.createElement('div');
        indicator.id = 'messages-beyond-indicator';
        indicator.className = 'messages-beyond-indicator';
        indicator.innerHTML = `
            <div class="messages-beyond-btn" data-messages-beyond>
                <div class="cosmic-icon">🌌</div>
                <div class="message-count">
                    <span class="total">${messageCount}</span>
                    ${unprocessedCount > 0 ? `<span class="unprocessed">${unprocessedCount} new</span>` : ''}
                </div>
                <div class="label">Messages from Beyond</div>
            </div>
        `;
        
        // Insert into sidebar or main UI
        const sidebar = document.querySelector('.sidebar') || document.querySelector('.terminal-container');
        if (sidebar) {
            sidebar.appendChild(indicator);
        }
    }
    
    renderMessagesModal() {
        // Remove existing modal
        const existingModal = document.getElementById('messages-beyond-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'messages-beyond-modal';
        modal.className = 'modal messages-beyond-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2><span class="cosmic-icon">🌌</span> Messages from Beyond</h2>
                    <button class="modal-close" onclick="window.messagesBeyondDisplay.hideMessagesModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="messages-overview">
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${this.messagesData.messages.length}</div>
                                <div class="stat-label">Total Messages</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${this.messagesData.messages.filter(m => m.processed).length}</div>
                                <div class="stat-label">Processed</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${this.messagesData.messages.filter(m => !m.processed).length}</div>
                                <div class="stat-label">Pending</div>
                            </div>
                        </div>
                    </div>
                    <div class="messages-timeline">
                        ${this.renderMessagesTimeline()}
                    </div>
                    <div class="agent-response-summary">
                        ${this.renderAgentStats()}
                    </div>
                </div>
            </div>
            <div class="modal-backdrop" onclick="window.messagesBeyondDisplay.hideMessagesModal()"></div>
        `;
        
        document.body.appendChild(modal);
    }
    
    renderMessagesTimeline() {
        if (!this.messagesData.messages.length) {
            return `
                <div class="no-messages">
                    <div class="cosmic-icon">✨</div>
                    <p>No messages from beyond have been received yet.</p>
                    <p class="subtitle">The cosmos remains silent... for now.</p>
                </div>
            `;
        }
        
        return `
            <div class="timeline-header">
                <h3>Cosmic Communications Timeline</h3>
            </div>
            <div class="timeline">
                ${this.messagesData.messages.map(message => this.renderMessageCard(message)).join('')}
            </div>
        `;
    }
    
    renderMessageCard(message) {
        const timestamp = new Date(message.timestamp).toLocaleString();
        const status = message.processed ? 'processed' : 'pending';
        const reflectionCount = message.reflection_count || 0;
        const discussionCount = message.discussion_count || 0;
        
        return `
            <div class="message-card ${status}" data-message-id="${message.message_id}">
                <div class="message-header">
                    <div class="message-meta">
                        <span class="source-label">${message.source_label}</span>
                        <span class="timestamp">${timestamp}</span>
                        <span class="status-badge ${status}">${status}</span>
                    </div>
                    <div class="message-id">ID: ${message.message_id}</div>
                </div>
                <div class="message-content">
                    <p>${this.formatMessageContent(message.content)}</p>
                </div>
                ${message.admin_notes ? `<div class="admin-notes"><strong>Admin Notes:</strong> ${message.admin_notes}</div>` : ''}
                <div class="message-stats">
                    <div class="stat">
                        <span class="icon">💭</span>
                        <span>${reflectionCount} reflections</span>
                    </div>
                    <div class="stat">
                        <span class="icon">💬</span>
                        <span>${discussionCount} discussions</span>
                    </div>
                    ${message.cycle_number ? `<div class="stat"><span class="icon">🔄</span><span>Cycle ${message.cycle_number}</span></div>` : ''}
                </div>
                ${message.processed ? this.renderMessageDetails(message) : ''}
            </div>
        `;
    }
    
    renderMessageDetails(message) {
        // This would show agent reflections and discussions
        // For now, just show a summary
        return `
            <div class="message-details">
                <button class="details-toggle" onclick="window.messagesBeyondDisplay.toggleMessageDetails('${message.message_id}')">
                    View Agent Interpretations
                </button>
                <div class="details-content" id="details-${message.message_id}" style="display: none;">
                    <div class="loading">Loading agent interpretations...</div>
                </div>
            </div>
        `;
    }
    
    renderAgentStats() {
        const stats = this.messagesData.agent_stats;
        if (!Object.keys(stats).length) {
            return '<div class="no-agent-stats">No agent response data available.</div>';
        }
        
        return `
            <div class="agent-stats-section">
                <h3>Agent Response Patterns</h3>
                <div class="agent-stats-grid">
                    ${Object.entries(stats).map(([agent, data]) => `
                        <div class="agent-stat-card">
                            <div class="agent-name">${agent}</div>
                            <div class="agent-metrics">
                                <div class="metric">
                                    <span class="label">Total Reflections:</span>
                                    <span class="value">${data.total_reflections || 0}</span>
                                </div>
                                <div class="metric">
                                    <span class="label">Avg Sentiment:</span>
                                    <span class="value sentiment-${this.getSentimentClass(data.avg_sentiment)}">
                                        ${data.avg_sentiment ? data.avg_sentiment.toFixed(2) : 'N/A'}
                                    </span>
                                </div>
                                <div class="metric">
                                    <span class="label">Confidence Change:</span>
                                    <span class="value">${data.avg_confidence_change ? data.avg_confidence_change.toFixed(2) : 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    formatMessageContent(content) {
        // Basic text formatting
        if (content.length > 200) {
            return content.substring(0, 200) + '...';
        }
        return content;
    }
    
    getSentimentClass(sentiment) {
        if (!sentiment) return 'neutral';
        if (sentiment > 0.3) return 'positive';
        if (sentiment < -0.3) return 'negative';
        return 'neutral';
    }
    
    showMessagesModal() {
        const modal = document.getElementById('messages-beyond-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }
    
    hideMessagesModal() {
        const modal = document.getElementById('messages-beyond-modal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }
    
    async toggleMessageDetails(messageId) {
        const detailsEl = document.getElementById(`details-${messageId}`);
        if (!detailsEl) return;
        
        if (detailsEl.style.display === 'none') {
            detailsEl.style.display = 'block';
            // Load detailed data if needed
            await this.loadMessageDetails(messageId, detailsEl);
        } else {
            detailsEl.style.display = 'none';
        }
    }
    
    async loadMessageDetails(messageId, container) {
        try {
            // In a real implementation, this would fetch detailed reflection data
            // For now, show placeholder
            container.innerHTML = `
                <div class="message-reflections">
                    <h4>Agent Interpretations</h4>
                    <div class="reflection-placeholder">
                        <p>Detailed agent reflections and discussions would be displayed here.</p>
                        <p>This includes individual agent interpretations, group discussions, and theological impacts.</p>
                    </div>
                </div>
            `;
        } catch (error) {
            container.innerHTML = `<div class="error">Error loading details: ${error.message}</div>`;
        }
    }
    
    startAutoUpdate() {
        // Update every 30 seconds
        this.updateInterval = setInterval(async () => {
            await this.loadMessagesData();
            this.renderMessagesSidebar();
        }, 30000);
    }
    
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.messagesBeyondDisplay = new MessagesBeyondDisplay();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.messagesBeyondDisplay) {
        window.messagesBeyondDisplay.stopAutoUpdate();
    }
});