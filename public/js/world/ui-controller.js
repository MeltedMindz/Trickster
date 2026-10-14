/**
 * UI Controller
 * Manages the HTML interface panels
 */

class UIController {
    constructor() {
        this.elements = {};
        this.panelCollapsed = false;
    }

    /**
     * Initialize UI elements
     */
    init() {
        // Cache DOM elements
        this.elements = {
            modeIndicator: document.getElementById('mode-indicator'),
            tickDisplay: document.getElementById('tick-display'),
            agentList: document.getElementById('agent-list'),
            landmarkList: document.getElementById('landmark-list'),
            eventFeed: document.getElementById('event-feed'),
            selectionSection: document.getElementById('selection-section'),
            selectionInfo: document.getElementById('selection-info'),
            coordDisplay: document.getElementById('cursor-coords'),
            panelContent: document.getElementById('panel-content'),
            panelToggle: document.getElementById('panel-toggle'),
            btnCenter: document.getElementById('btn-center'),
            btnFullscreen: document.getElementById('btn-fullscreen'),
            minimapCanvas: document.getElementById('minimap-canvas'),
        };

        // Set up event listeners
        this.setupEventListeners();

        // Set mode indicator
        this.elements.modeIndicator.textContent = WORLD_CONFIG.REFRESH_INTERVAL > 0 ? 'LIVE' : 'STATIC';
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Panel toggle
        if (this.elements.panelToggle) {
            this.elements.panelToggle.addEventListener('click', () => {
                this.togglePanel();
            });
        }

        // Center button
        if (this.elements.btnCenter) {
            this.elements.btnCenter.addEventListener('click', () => {
                if (window.worldScene) {
                    window.worldScene.centerOnAgents();
                }
            });
        }

        // Fullscreen button
        if (this.elements.btnFullscreen) {
            this.elements.btnFullscreen.addEventListener('click', () => {
                this.toggleFullscreen();
            });
        }

        // Minimap click to navigate
        if (this.elements.minimapCanvas) {
            this.elements.minimapCanvas.addEventListener('click', (e) => {
                const rect = this.elements.minimapCanvas.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width * WORLD_CONFIG.WORLD_SIZE;
                const y = (e.clientY - rect.top) / rect.height * WORLD_CONFIG.WORLD_SIZE;

                if (window.game) {
                    const scene = window.game.scene.getScene('WorldScene');
                    if (scene) {
                        scene.cameras.main.centerOn(
                            x * WORLD_CONFIG.TILE_SIZE,
                            y * WORLD_CONFIG.TILE_SIZE
                        );
                    }
                }
            });
        }
    }

    /**
     * Toggle panel collapsed state
     */
    togglePanel() {
        this.panelCollapsed = !this.panelCollapsed;

        if (this.panelCollapsed) {
            this.elements.panelContent.style.display = 'none';
            this.elements.panelToggle.textContent = '+';
        } else {
            this.elements.panelContent.style.display = 'block';
            this.elements.panelToggle.textContent = '−';
        }
    }

    /**
     * Toggle fullscreen
     */
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            this.elements.btnFullscreen.textContent = '[ ]';
        } else {
            document.exitFullscreen();
            this.elements.btnFullscreen.textContent = '[ ]';
        }
    }

    /**
     * Update tick display
     */
    updateTick(tick) {
        if (this.elements.tickDisplay) {
            this.elements.tickDisplay.textContent = `Tick: ${tick}`;
        }
    }

    /**
     * Update agent list
     */
    updateAgentList(agents) {
        if (!this.elements.agentList) return;

        let html = '';
        for (const [agentId, data] of Object.entries(agents)) {
            const name = data.chosen_name || WORLD_CONFIG.AGENT_NAMES[agentId] || agentId;
            const color = WORLD_CONFIG.AGENT_COLORS[agentId];
            const colorHex = '#' + color.toString(16).padStart(6, '0');

            html += `
                <div class="agent-item" data-agent-id="${agentId}">
                    <span class="agent-marker" style="background: ${colorHex}"></span>
                    <div class="agent-info">
                        <span class="agent-name">${name}</span>
                        <span class="agent-pos">(${data.tile_x}, ${data.tile_y})</span>
                    </div>
                    <span class="agent-action">${data.current_action || 'idle'}</span>
                </div>
            `;
        }

        this.elements.agentList.innerHTML = html;

        // Add click handlers
        this.elements.agentList.querySelectorAll('.agent-item').forEach(item => {
            item.addEventListener('click', () => {
                const agentId = item.dataset.agentId;
                if (window.game) {
                    const scene = window.game.scene.getScene('WorldScene');
                    if (scene) {
                        scene.focusOnAgent(agentId);
                    }
                }
            });
        });
    }

    /**
     * Update landmark list
     */
    updateLandmarkList(landmarks) {
        if (!this.elements.landmarkList) return;

        let html = '';
        for (const landmark of landmarks) {
            const color = WORLD_CONFIG.LANDMARK_COLORS[landmark.type];
            const colorHex = color ? '#' + color.toString(16).padStart(6, '0') : '#ffffff';

            html += `
                <div class="landmark-item" data-landmark-id="${landmark.id}">
                    <span class="landmark-marker" style="background: ${colorHex}"></span>
                    <div class="landmark-info">
                        <span class="landmark-name">${landmark.name}</span>
                        <span class="landmark-type">${landmark.type}</span>
                    </div>
                </div>
            `;
        }

        this.elements.landmarkList.innerHTML = html;

        // Add click handlers
        this.elements.landmarkList.querySelectorAll('.landmark-item').forEach(item => {
            item.addEventListener('click', () => {
                const landmarkId = item.dataset.landmarkId;
                if (window.game) {
                    const scene = window.game.scene.getScene('WorldScene');
                    if (scene) {
                        scene.focusOnLandmark(landmarkId);
                    }
                }
            });
        });
    }

    /**
     * Update event feed
     */
    updateEventFeed(events) {
        if (!this.elements.eventFeed) return;

        let html = '';
        const recentEvents = events.slice(-10).reverse();

        for (const event of recentEvents) {
            const time = event.tick ? `T${event.tick}` : '';
            const actor = event.actor || '';
            const type = event.type || 'event';

            html += `
                <div class="event-item">
                    <span class="event-time">${time}</span>
                    <span class="event-actor">${actor}</span>
                    <span class="event-type">${type}</span>
                </div>
            `;
        }

        this.elements.eventFeed.innerHTML = html || '<div class="event-empty">No recent events</div>';
    }

    /**
     * Show agent info in selection panel
     */
    showAgentInfo(agentId, data) {
        if (!this.elements.selectionSection || !this.elements.selectionInfo) return;

        this.elements.selectionSection.style.display = 'block';

        const name = data?.chosen_name || WORLD_CONFIG.AGENT_NAMES[agentId] || agentId;
        const color = WORLD_CONFIG.AGENT_COLORS[agentId];
        const colorHex = '#' + color.toString(16).padStart(6, '0');

        let html = `
            <div class="selection-header">
                <span class="agent-marker large" style="background: ${colorHex}"></span>
                <span class="selection-name">${name}</span>
            </div>
            <div class="selection-details">
                <div class="detail-row">
                    <span class="detail-label">Role:</span>
                    <span class="detail-value">${agentId}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Position:</span>
                    <span class="detail-value">(${data?.tile_x || '?'}, ${data?.tile_y || '?'})</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Facing:</span>
                    <span class="detail-value">${data?.facing || 'south'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Energy:</span>
                    <span class="detail-value">${((data?.energy || 1) * 100).toFixed(0)}%</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Action:</span>
                    <span class="detail-value">${data?.current_action || 'idle'}</span>
                </div>
            </div>
        `;

        this.elements.selectionInfo.innerHTML = html;
    }

    /**
     * Clear selection panel
     */
    clearSelection() {
        if (this.elements.selectionSection) {
            this.elements.selectionSection.style.display = 'none';
        }
    }

    /**
     * Update coordinate display
     */
    updateCoordinates(x, y, tileName) {
        if (this.elements.coordDisplay) {
            this.elements.coordDisplay.textContent = `(${x}, ${y}) ${tileName}`;
        }
    }
}

// Global instance
window.uiController = null;
