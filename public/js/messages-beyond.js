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
        const sidebarContainer = document.getElementById('messages-beyond-sidebar');
        const statusContainer = document.getElementById('messages-status');
        
        if (!sidebarContainer) return;
        
        const messageCount = this.messagesData.messages.length;
        const processedCount = this.messagesData.messages.filter(m => m.processed).length;
        const pendingCount = this.messagesData.messages.filter(m => !m.processed).length;
        
        // Update status
        if (statusContainer) {
            statusContainer.innerHTML = `
                <span class="status-label">Messages:</span>
                <span class="status-value">${pendingCount} pending, ${processedCount} processed</span>
            `;
        }
        
        // Update messages list
        if (messageCount === 0) {
            sidebarContainer.innerHTML = '<div class="empty-state">No messages from beyond yet...</div>';
            return;
        }
        
        // Show latest 5 messages
        const recentMessages = this.messagesData.messages
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 5);
            
        sidebarContainer.innerHTML = recentMessages.map(message => {
            const status = message.processed ? 'processed' : 'pending';
            const time = new Date(message.timestamp).toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            const preview = message.content.length > 60 ? 
                message.content.substring(0, 60) + '...' : 
                message.content;
            
            return `
                <div class="messages-beyond-item ${status}" data-message-id="${message.message_id}" onclick="window.messagesBeyondDisplay.showMessagesModal()">
                    <div class="message-preview">${preview}</div>
                    <div class="message-meta-sidebar">
                        <span class="message-source-sidebar">${message.source_label}</span>
                        <span class="message-time-sidebar">${time}</span>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add agent reflection logs to terminal if there are processed messages
        this.addAgentReflectionsToTerminal();
    }
    
    addAgentReflectionsToTerminal() {
        const terminalOutput = document.getElementById('terminal-output');
        if (!terminalOutput) return;
        
        // Get processed messages with reflections
        const processedMessages = this.messagesData.messages.filter(m => m.processed);
        
        processedMessages.forEach(message => {
            // Check if we already added this message to terminal
            const existingEntry = terminalOutput.querySelector(`[data-message-id="${message.message_id}"]`);
            if (existingEntry) return;
            
            // Add message received log
            const messageReceivedLine = document.createElement('div');
            messageReceivedLine.className = 'terminal-line system';
            messageReceivedLine.setAttribute('data-message-id', message.message_id);
            messageReceivedLine.innerHTML = `
                <span class="timestamp">[${new Date(message.timestamp).toLocaleTimeString()}]</span>
                <span class="content">📡 Message from Beyond received: "${message.content.substring(0, 80)}${message.content.length > 80 ? '...' : ''}"</span>
            `;
            terminalOutput.appendChild(messageReceivedLine);
            
            // Add agent reflection logs
            if (message.agent_reflections) {
                Object.entries(message.agent_reflections).forEach(([agent, reflection]) => {
                    const reflectionLine = document.createElement('div');
                    reflectionLine.className = 'terminal-line agent';
                    reflectionLine.innerHTML = `
                        <span class="timestamp">[${new Date(reflection.timestamp || message.timestamp).toLocaleTimeString()}]</span>
                        <span class="content">🤖 ${agent} reflects: "${reflection.interpretation?.substring(0, 100) || 'Processing message...'}${reflection.interpretation?.length > 100 ? '...' : ''}"</span>
                    `;
                    terminalOutput.appendChild(reflectionLine);
                });
            }
            
            // Add processing complete log
            const processingLine = document.createElement('div');
            processingLine.className = 'terminal-line success';
            processingLine.innerHTML = `
                <span class="timestamp">[${new Date(message.timestamp).toLocaleTimeString()}]</span>
                <span class="content">✅ Message processing complete - theological implications analyzed</span>
            `;
            terminalOutput.appendChild(processingLine);
        });
        
        // Scroll to bottom
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
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
        
        const isLongContent = message.content.length > 200;
        const shortContent = isLongContent ? message.content.substring(0, 200) + '...' : message.content;
        
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
                    <div class="message-text">
                        <p class="message-preview-text" id="preview-${message.message_id}">${shortContent}</p>
                        ${isLongContent ? `<p class="message-full-text" id="full-${message.message_id}" style="display: none;">${message.content}</p>` : ''}
                    </div>
                    ${isLongContent ? `
                        <button class="read-more-btn" onclick="window.messagesBeyondDisplay.toggleMessageContent('${message.message_id}')">
                            <span class="read-more-text">Read More</span>
                            <span class="read-less-text" style="display: none;">Read Less</span>
                        </button>
                    ` : ''}
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
        const hasReflections = message.agent_reflections && Object.keys(message.agent_reflections).length > 0;
        
        if (!hasReflections) {
            return `
                <div class="message-details">
                    <button class="details-toggle" onclick="window.messagesBeyondDisplay.toggleMessageDetails('${message.message_id}')">
                        View Agent Interpretations
                    </button>
                    <div class="details-content" id="details-${message.message_id}" style="display: none;">
                        <div class="no-reflections">No agent reflections available yet.</div>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="message-details">
                <button class="details-toggle" onclick="window.messagesBeyondDisplay.toggleMessageDetails('${message.message_id}')">
                    View Agent Interpretations
                </button>
                <div class="details-content" id="details-${message.message_id}" style="display: none;">
                    <div class="agent-reflections">
                        <h4>Agent Interpretations</h4>
                        ${Object.entries(message.agent_reflections).map(([agent, reflection]) => `
                            <div class="agent-reflection">
                                <div class="agent-reflection-header">
                                    <span class="agent-reflection-name">${agent}</span>
                                    <span class="sentiment-score sentiment-${this.getSentimentClass(reflection.sentiment_score)}">${reflection.sentiment_score?.toFixed(2) || 'N/A'}</span>
                                </div>
                                <div class="agent-reflection-text">${reflection.interpretation}</div>
                            </div>
                        `).join('')}
                    </div>
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
    
    toggleMessageContent(messageId) {
        const previewEl = document.getElementById(`preview-${messageId}`);
        const fullEl = document.getElementById(`full-${messageId}`);
        const btn = document.querySelector(`[onclick*="${messageId}"]`);
        
        if (!previewEl || !fullEl || !btn) return;
        
        const readMoreText = btn.querySelector('.read-more-text');
        const readLessText = btn.querySelector('.read-less-text');
        
        if (fullEl.style.display === 'none') {
            // Show full text
            previewEl.style.display = 'none';
            fullEl.style.display = 'block';
            readMoreText.style.display = 'none';
            readLessText.style.display = 'inline';
        } else {
            // Show preview text
            previewEl.style.display = 'block';
            fullEl.style.display = 'none';
            readMoreText.style.display = 'inline';
            readLessText.style.display = 'none';
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