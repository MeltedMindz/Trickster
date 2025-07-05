/**
 * Enhanced Memory Viewer for new database schemas
 * Handles belief confidence, emotion influence, memory conflicts, dream journals, etc.
 */

class EnhancedMemoryViewer {
    constructor() {
        this.data = {
            beliefConfidence: [],
            emotionInfluence: [],
            memoryConflicts: [],
            dreamJournals: [],
            artifactLifecycle: [],
            memoryDecay: [],
            beliefAdoption: []
        };
        this.isVisible = false;
        this.currentView = 'belief_confidence';
        this.initializeComponent();
    }

    async initializeComponent() {
        // Create enhanced memory viewer UI
        this.createUI();
        this.loadData();
        
        // Set up periodic refresh
        setInterval(() => this.loadData(), 60000); // Refresh every minute
    }

    createUI() {
        // Create main container
        const container = document.createElement('div');
        container.id = 'enhanced-memory-viewer';
        container.className = 'enhanced-memory-container';
        container.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 400px;
            max-height: 600px;
            background: rgba(0, 20, 40, 0.95);
            border: 2px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            z-index: 1000;
            display: none;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            color: #00ff88;
        `;

        // Create header with toggle button
        const header = document.createElement('div');
        header.className = 'enhanced-memory-header';
        header.innerHTML = `
            <h3 style="margin: 0 0 10px 0; color: #00ff88;">Enhanced Memory Analysis</h3>
            <div class="view-selector" style="margin-bottom: 15px;">
                <select id="memory-view-select" style="background: #001122; color: #00ff88; border: 1px solid #00ff88; padding: 5px;">
                    <option value="belief_confidence">Belief Confidence</option>
                    <option value="emotion_influence">Emotion Influence</option>
                    <option value="memory_conflicts">Memory Conflicts</option>
                    <option value="dream_journals">Dream Journals</option>
                    <option value="artifact_lifecycle">Artifact Lifecycle</option>
                    <option value="memory_decay">Memory Decay</option>
                    <option value="belief_adoption">Belief Adoption</option>
                </select>
            </div>
        `;

        // Create content area
        const content = document.createElement('div');
        content.id = 'enhanced-memory-content';
        content.className = 'enhanced-memory-content';

        // Create close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 15px;
            background: none;
            border: none;
            color: #00ff88;
            font-size: 20px;
            cursor: pointer;
        `;
        closeBtn.onclick = () => this.hide();

        container.appendChild(closeBtn);
        container.appendChild(header);
        container.appendChild(content);
        document.body.appendChild(container);

        // Set up view selector
        document.getElementById('memory-view-select').addEventListener('change', (e) => {
            this.currentView = e.target.value;
            this.renderCurrentView();
        });

        this.container = container;
        this.contentArea = content;

        // Add toggle button to main interface
        this.addToggleButton();
    }

    addToggleButton() {
        // Add button to the existing interface
        const existingControls = document.querySelector('.mobile-controls') || document.body;
        
        const toggleBtn = document.createElement('button');
        toggleBtn.innerHTML = '🧠 Enhanced Memory';
        toggleBtn.className = 'enhanced-memory-toggle';
        toggleBtn.style.cssText = `
            position: fixed;
            top: 60px;
            right: 10px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            z-index: 999;
        `;
        
        toggleBtn.onclick = () => this.toggle();
        document.body.appendChild(toggleBtn);
    }

    async loadData() {
        try {
            // Load all new data files
            const dataFiles = [
                'belief_confidence.json',
                'emotion_influence.json', 
                'memory_conflicts.json',
                'dream_journals.json',
                'artifact_lifecycle.json',
                'memory_decay.json',
                'belief_adoption.json'
            ];

            const dataKeys = [
                'beliefConfidence',
                'emotionInfluence',
                'memoryConflicts', 
                'dreamJournals',
                'artifactLifecycle',
                'memoryDecay',
                'beliefAdoption'
            ];

            for (let i = 0; i < dataFiles.length; i++) {
                try {
                    const response = await fetch(`./data/${dataFiles[i]}`);
                    if (response.ok) {
                        const data = await response.json();
                        this.data[dataKeys[i]] = data;
                    }
                } catch (e) {
                    // File might not exist yet, that's okay
                    console.log(`Enhanced memory file ${dataFiles[i]} not found yet`);
                }
            }

            if (this.isVisible) {
                this.renderCurrentView();
            }
        } catch (error) {
            console.error('Error loading enhanced memory data:', error);
        }
    }

    renderCurrentView() {
        if (!this.contentArea) return;

        let content = '';
        
        switch (this.currentView) {
            case 'belief_confidence':
                content = this.renderBeliefConfidence();
                break;
            case 'emotion_influence':
                content = this.renderEmotionInfluence();
                break;
            case 'memory_conflicts':
                content = this.renderMemoryConflicts();
                break;
            case 'dream_journals':
                content = this.renderDreamJournals();
                break;
            case 'artifact_lifecycle':
                content = this.renderArtifactLifecycle();
                break;
            case 'memory_decay':
                content = this.renderMemoryDecay();
                break;
            case 'belief_adoption':
                content = this.renderBeliefAdoption();
                break;
        }

        this.contentArea.innerHTML = content;
    }

    renderBeliefConfidence() {
        const data = this.data.beliefConfidence.confidence_data || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No belief confidence data yet</div>';

        let html = '<h4>Belief Confidence Tracking</h4>';
        data.slice(0, 10).forEach(entry => {
            const confidence = (entry.confidence_score * 100).toFixed(1);
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #004488;">
                    <strong>${entry.agent_id}</strong> - Belief ${entry.belief_id}<br/>
                    Confidence: ${confidence}% | Cycle: ${entry.cycle_number}<br/>
                    Influence: ${(entry.influence_factor * 100).toFixed(1)}%
                </div>
            `;
        });
        return html;
    }

    renderEmotionInfluence() {
        const data = this.data.emotionInfluence.influence_network || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No emotion influence data yet</div>';

        let html = '<h4>Emotion Influence Network</h4>';
        data.slice(0, 10).forEach(entry => {
            const influence = (entry.influence_value * 100).toFixed(1);
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #004488;">
                    <strong>${entry.source_agent_id}</strong> → <strong>${entry.target_agent_id}</strong><br/>
                    ${entry.emotion_type}: ${influence}% | Cycle: ${entry.cycle_number}
                </div>
            `;
        });
        return html;
    }

    renderMemoryConflicts() {
        const data = this.data.memoryConflicts.conflicts || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No memory conflicts yet</div>';

        let html = '<h4>Memory Conflicts & Resolutions</h4>';
        data.slice(0, 5).forEach(entry => {
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #884400;">
                    <strong>${entry.agent_id}</strong> - Cycle ${entry.cycle_number}<br/>
                    <small>Memory A: ${entry.memory_a}</small><br/>
                    <small>Memory B: ${entry.memory_b}</small><br/>
                    <em>Resolution: ${entry.resolution}</em>
                </div>
            `;
        });
        return html;
    }

    renderDreamJournals() {
        const data = this.data.dreamJournals.dreams || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No dreams yet</div>';

        let html = '<h4>Agent Dream Journals</h4>';
        data.slice(0, 5).forEach(entry => {
            const sentiment = entry.sentiment > 0.5 ? '😊' : entry.sentiment > 0.3 ? '😐' : '😔';
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #440088;">
                    <strong>${entry.agent_id}</strong> ${sentiment} - Cycle ${entry.cycle_number}<br/>
                    <small style="font-style: italic;">"${entry.dream_content.substring(0, 100)}..."</small>
                </div>
            `;
        });
        return html;
    }

    renderArtifactLifecycle() {
        const data = this.data.artifactLifecycle.artifacts || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No artifacts tracked yet</div>';

        let html = '<h4>Sacred Artifact Lifecycle</h4>';
        data.slice(0, 10).forEach(entry => {
            const status = entry.cycle_retired ? 'Retired' : 'Active';
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #448800;">
                    <strong>${entry.artifact_type}</strong> by ${entry.created_by}<br/>
                    Created: Cycle ${entry.cycle_created} | Status: ${status}<br/>
                    Usage: ${entry.usage_count} | Weight: ${(entry.cultural_weight * 100).toFixed(1)}%
                </div>
            `;
        });
        return html;
    }

    renderMemoryDecay() {
        const data = this.data.memoryDecay.decay_profiles || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No memory decay data yet</div>';

        let html = '<h4>Memory Decay Profiles</h4>';
        data.slice(0, 15).forEach(entry => {
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #888800;">
                    <strong>${entry.agent_id}</strong> - ${entry.memory_type}<br/>
                    Decay Rate: ${(entry.decay_rate * 100).toFixed(2)}% | Retained: ${entry.memory_retained}%<br/>
                    Cycle: ${entry.cycle_number}
                </div>
            `;
        });
        return html;
    }

    renderBeliefAdoption() {
        const data = this.data.beliefAdoption.adoption_trajectories || [];
        if (data.length === 0) return '<div style="color: #ffaa00;">No belief adoption data yet</div>';

        let html = '<h4>Belief Adoption Trajectories</h4>';
        data.slice(0, 10).forEach(entry => {
            const status = entry.cycle_dropped ? `Dropped (Cycle ${entry.cycle_dropped})` : 'Active';
            html += `
                <div style="margin: 5px 0; padding: 5px; border: 1px solid #008888;">
                    <strong>${entry.agent_id}</strong> - Belief ${entry.belief_id}<br/>
                    Adopted: Cycle ${entry.cycle_acquired} | Status: ${status}
                </div>
            `;
        });
        return html;
    }

    show() {
        this.isVisible = true;
        this.container.style.display = 'block';
        this.renderCurrentView();
    }

    hide() {
        this.isVisible = false;
        this.container.style.display = 'none';
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.enhancedMemoryViewer = new EnhancedMemoryViewer();
    });
} else {
    window.enhancedMemoryViewer = new EnhancedMemoryViewer();
}