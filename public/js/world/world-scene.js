/**
 * World Scene
 * Main Phaser scene for the world view
 */

class WorldScene extends Phaser.Scene {
    constructor() {
        super({ key: 'WorldScene' });

        this.terrainRenderer = null;
        this.agentSprites = null;
        this.worldState = null;
        this.landmarks = [];
        this.landmarkGraphics = null;
    }

    preload() {
        // No external assets needed - we generate textures procedurally
    }

    create() {
        // Set up camera
        const worldPixelSize = WORLD_CONFIG.WORLD_SIZE * WORLD_CONFIG.TILE_SIZE;
        this.cameras.main.setBounds(0, 0, worldPixelSize, worldPixelSize);
        this.cameras.main.setZoom(WORLD_CONFIG.CAMERA_ZOOM);

        // Enable camera drag
        this.input.on('pointermove', (pointer) => {
            if (pointer.isDown && pointer.button === 0) {
                this.cameras.main.scrollX -= (pointer.x - pointer.prevPosition.x) / this.cameras.main.zoom;
                this.cameras.main.scrollY -= (pointer.y - pointer.prevPosition.y) / this.cameras.main.zoom;
            }
        });

        // Zoom with mouse wheel
        this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY) => {
            const zoom = this.cameras.main.zoom;
            const newZoom = Phaser.Math.Clamp(
                zoom - deltaY * 0.001,
                WORLD_CONFIG.MIN_ZOOM,
                WORLD_CONFIG.MAX_ZOOM
            );
            this.cameras.main.setZoom(newZoom);
        });

        // Initialize terrain renderer
        this.terrainRenderer = new TerrainRenderer(this);
        this.terrainRenderer.init();

        // Initialize agent sprites
        this.agentSprites = new AgentSprites(this);
        this.agentSprites.init();

        // Create landmark graphics
        this.landmarkGraphics = this.add.graphics();
        this.landmarkGraphics.setDepth(3);

        // Create landmark labels container
        this.landmarkLabels = [];

        // Load initial data
        this.loadWorldState();

        // Set up update event
        this.events.on('agentSelected', (agentId) => {
            if (window.uiController) {
                window.uiController.showAgentInfo(agentId, this.worldState?.agents?.[agentId]);
            }
        });

        // Click on empty space to deselect
        this.input.on('pointerdown', (pointer) => {
            // Check if clicking on terrain, not an agent
            const worldPoint = this.cameras.main.getWorldPoint(pointer.x, pointer.y);
            const clickedAgent = Object.values(this.agentSprites.sprites).find(sprite => {
                const dx = worldPoint.x - sprite.x;
                const dy = worldPoint.y - sprite.y;
                return Math.sqrt(dx * dx + dy * dy) < WORLD_CONFIG.TILE_SIZE / 2;
            });

            if (!clickedAgent && pointer.button === 0) {
                this.agentSprites.clearSelection();
            }
        });

        // Start centered on the debate commons
        this.cameras.main.centerOn(
            64 * WORLD_CONFIG.TILE_SIZE,
            64 * WORLD_CONFIG.TILE_SIZE
        );
    }

    /**
     * Load world state from JSON
     */
    async loadWorldState() {
        try {
            // Load world state
            const response = await fetch(WORLD_CONFIG.DATA_PATH + WORLD_CONFIG.WORLD_STATE_FILE);
            if (response.ok) {
                this.worldState = await response.json();
                this.updateFromState();
            }
        } catch (e) {
            console.error('Failed to load world state:', e);
        }

        // Load terrain
        await this.terrainRenderer.loadTerrain();
        this.terrainRenderer.render();

        // Render minimap
        this.renderMinimap();
    }

    /**
     * Update scene from world state
     */
    updateFromState() {
        if (!this.worldState) return;

        // Update tick display
        if (window.uiController) {
            window.uiController.updateTick(this.worldState.tick);
        }

        // Update agents
        if (this.worldState.agents) {
            this.agentSprites.updateAgents(this.worldState.agents);

            // Update agent list in UI
            if (window.uiController) {
                window.uiController.updateAgentList(this.worldState.agents);
            }
        }

        // Update landmarks
        if (this.worldState.landmarks) {
            this.landmarks = this.worldState.landmarks;
            this.renderLandmarks();

            if (window.uiController) {
                window.uiController.updateLandmarkList(this.landmarks);
            }
        }

        // Update events
        if (this.worldState.recent_events && window.uiController) {
            window.uiController.updateEventFeed(this.worldState.recent_events);
        }
    }

    /**
     * Render landmarks on the map
     */
    renderLandmarks() {
        this.landmarkGraphics.clear();

        // Clear old labels
        this.landmarkLabels.forEach(label => label.destroy());
        this.landmarkLabels = [];

        for (const landmark of this.landmarks) {
            const x = landmark.x * WORLD_CONFIG.TILE_SIZE;
            const y = landmark.y * WORLD_CONFIG.TILE_SIZE;
            const radius = landmark.radius * WORLD_CONFIG.TILE_SIZE;

            // Get color based on type
            const color = WORLD_CONFIG.LANDMARK_COLORS[landmark.type] || 0xffffff;

            // Draw landmark radius indicator
            this.landmarkGraphics.lineStyle(1, color, 0.3);
            this.landmarkGraphics.strokeCircle(x + WORLD_CONFIG.TILE_SIZE / 2, y + WORLD_CONFIG.TILE_SIZE / 2, radius);

            // Draw center marker
            this.landmarkGraphics.fillStyle(color, 0.5);
            this.landmarkGraphics.fillCircle(x + WORLD_CONFIG.TILE_SIZE / 2, y + WORLD_CONFIG.TILE_SIZE / 2, 4);

            // Add label
            const label = this.add.text(
                x + WORLD_CONFIG.TILE_SIZE / 2,
                y - 10,
                landmark.name,
                {
                    fontFamily: 'JetBrains Mono',
                    fontSize: '9px',
                    color: '#ffffff',
                    backgroundColor: '#000000aa',
                    padding: { x: 2, y: 1 },
                }
            );
            label.setOrigin(0.5, 1);
            label.setDepth(4);
            this.landmarkLabels.push(label);
        }
    }

    /**
     * Render minimap
     */
    renderMinimap() {
        const canvas = document.getElementById('minimap-canvas');
        if (!canvas) return;

        // Render terrain
        this.terrainRenderer.renderMinimap(canvas);

        // Render landmarks
        const ctx = canvas.getContext('2d');
        const scale = canvas.width / WORLD_CONFIG.WORLD_SIZE;

        for (const landmark of this.landmarks) {
            const color = WORLD_CONFIG.LANDMARK_COLORS[landmark.type] || 0xffffff;
            const r = (color >> 16) & 0xff;
            const g = (color >> 8) & 0xff;
            const b = color & 0xff;

            ctx.fillStyle = `rgba(${r},${g},${b},0.8)`;
            ctx.beginPath();
            ctx.arc(
                landmark.x * scale,
                landmark.y * scale,
                2,
                0,
                Math.PI * 2
            );
            ctx.fill();
        }

        // Render agents
        this.agentSprites.renderOnMinimap(ctx, scale);

        // Render camera viewport
        const cam = this.cameras.main;
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 1;
        ctx.strokeRect(
            cam.scrollX / WORLD_CONFIG.TILE_SIZE * scale,
            cam.scrollY / WORLD_CONFIG.TILE_SIZE * scale,
            (cam.width / cam.zoom) / WORLD_CONFIG.TILE_SIZE * scale,
            (cam.height / cam.zoom) / WORLD_CONFIG.TILE_SIZE * scale
        );
    }

    /**
     * Center camera on agents
     */
    centerOnAgents() {
        if (!this.worldState?.agents) return;

        const agents = Object.values(this.worldState.agents);
        if (agents.length === 0) return;

        // Find center of all agents
        let sumX = 0, sumY = 0;
        for (const agent of agents) {
            sumX += agent.tile_x;
            sumY += agent.tile_y;
        }

        const centerX = (sumX / agents.length) * WORLD_CONFIG.TILE_SIZE;
        const centerY = (sumY / agents.length) * WORLD_CONFIG.TILE_SIZE;

        this.cameras.main.centerOn(centerX, centerY);
    }

    /**
     * Focus on a specific agent
     */
    focusOnAgent(agentId) {
        this.agentSprites.focusOnAgent(agentId);
        this.agentSprites.selectAgent(agentId);
    }

    /**
     * Focus on a landmark
     */
    focusOnLandmark(landmarkId) {
        const landmark = this.landmarks.find(l => l.id === landmarkId);
        if (landmark) {
            this.cameras.main.centerOn(
                landmark.x * WORLD_CONFIG.TILE_SIZE,
                landmark.y * WORLD_CONFIG.TILE_SIZE
            );
        }
    }

    update() {
        // Update terrain (for camera culling)
        if (this.terrainRenderer) {
            this.terrainRenderer.update();
        }

        // Update agent sprites
        if (this.agentSprites) {
            this.agentSprites.update();
        }

        // Update minimap periodically
        if (this.time.now % 500 < 20) {
            this.renderMinimap();
        }

        // Update cursor coordinates
        const pointer = this.input.activePointer;
        const worldPoint = this.cameras.main.getWorldPoint(pointer.x, pointer.y);
        const tile = this.terrainRenderer?.getTileAt(worldPoint.x, worldPoint.y);

        if (tile && window.uiController) {
            window.uiController.updateCoordinates(tile.x, tile.y, tile.name);
        }
    }
}
