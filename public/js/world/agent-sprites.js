/**
 * Agent Sprites
 * Handles rendering and animating agent characters
 */

class AgentSprites {
    constructor(scene) {
        this.scene = scene;
        this.tileSize = WORLD_CONFIG.TILE_SIZE;

        // Sprite containers by agent ID
        this.sprites = {};

        // Label texts
        this.labels = {};

        // Selection indicator
        this.selectionIndicator = null;
        this.selectedAgentId = null;
    }

    /**
     * Initialize agent sprite system
     */
    init() {
        // Create procedural agent textures
        this.createAgentTextures();

        // Create selection indicator
        this.createSelectionIndicator();
    }

    /**
     * Create procedural textures for agents
     */
    createAgentTextures() {
        const graphics = this.scene.make.graphics({ x: 0, y: 0, add: false });
        const size = this.tileSize;

        for (const [agentId, color] of Object.entries(WORLD_CONFIG.AGENT_COLORS)) {
            // Create standing sprite
            graphics.clear();

            // Body (circle)
            graphics.fillStyle(color, 1);
            graphics.fillCircle(size / 2, size / 2, size / 2 - 2);

            // Outline
            graphics.lineStyle(2, 0x000000, 0.5);
            graphics.strokeCircle(size / 2, size / 2, size / 2 - 2);

            // Direction indicator (small triangle)
            graphics.fillStyle(0xffffff, 0.8);
            graphics.fillTriangle(
                size / 2, 2,
                size / 2 - 3, 6,
                size / 2 + 3, 6
            );

            graphics.generateTexture(`agent_${agentId}`, size, size);

            // Create highlighted version
            graphics.clear();
            graphics.fillStyle(color, 1);
            graphics.fillCircle(size / 2, size / 2, size / 2 - 1);
            graphics.lineStyle(2, 0xffffff, 1);
            graphics.strokeCircle(size / 2, size / 2, size / 2 - 1);
            graphics.fillStyle(0xffffff, 0.8);
            graphics.fillTriangle(
                size / 2, 2,
                size / 2 - 3, 6,
                size / 2 + 3, 6
            );

            graphics.generateTexture(`agent_${agentId}_highlight`, size, size);
        }

        graphics.destroy();
    }

    /**
     * Create selection indicator
     */
    createSelectionIndicator() {
        const graphics = this.scene.add.graphics();
        graphics.setDepth(5);

        const size = this.tileSize + 4;

        // Animated selection ring
        graphics.lineStyle(2, 0x00ff00, 1);
        graphics.strokeRect(-size / 2, -size / 2, size, size);

        graphics.setVisible(false);
        this.selectionIndicator = graphics;

        // Add pulsing animation
        this.scene.tweens.add({
            targets: graphics,
            alpha: { from: 1, to: 0.5 },
            duration: 500,
            yoyo: true,
            repeat: -1,
        });
    }

    /**
     * Update agents from state data
     */
    updateAgents(agentsData) {
        // Update or create sprites for each agent
        for (const [agentId, data] of Object.entries(agentsData)) {
            if (!this.sprites[agentId]) {
                this.createAgentSprite(agentId, data);
            } else {
                this.updateAgentSprite(agentId, data);
            }
        }

        // Remove sprites for agents no longer present
        for (const agentId of Object.keys(this.sprites)) {
            if (!agentsData[agentId]) {
                this.removeAgentSprite(agentId);
            }
        }
    }

    /**
     * Create sprite for an agent
     */
    createAgentSprite(agentId, data) {
        const x = data.tile_x * this.tileSize + this.tileSize / 2;
        const y = data.tile_y * this.tileSize + this.tileSize / 2;

        // Create sprite
        const sprite = this.scene.add.sprite(x, y, `agent_${agentId}`);
        sprite.setDepth(10);
        sprite.setInteractive();
        sprite.setData('agentId', agentId);

        // Set rotation based on facing
        this.setFacing(sprite, data.facing || 'south');

        // Create label
        const name = data.chosen_name || WORLD_CONFIG.AGENT_NAMES[agentId] || agentId;
        const label = this.scene.add.text(x, y - this.tileSize, name, {
            fontFamily: 'JetBrains Mono',
            fontSize: '10px',
            color: '#ffffff',
            backgroundColor: '#000000aa',
            padding: { x: 3, y: 1 },
        });
        label.setOrigin(0.5, 1);
        label.setDepth(15);

        // Store references
        this.sprites[agentId] = sprite;
        this.labels[agentId] = label;

        // Click handler
        sprite.on('pointerdown', () => {
            this.selectAgent(agentId);
        });

        // Hover effects
        sprite.on('pointerover', () => {
            sprite.setTexture(`agent_${agentId}_highlight`);
            this.scene.game.canvas.style.cursor = 'pointer';
        });

        sprite.on('pointerout', () => {
            sprite.setTexture(`agent_${agentId}`);
            this.scene.game.canvas.style.cursor = 'default';
        });
    }

    /**
     * Update existing agent sprite
     */
    updateAgentSprite(agentId, data) {
        const sprite = this.sprites[agentId];
        const label = this.labels[agentId];

        if (!sprite) return;

        const targetX = data.tile_x * this.tileSize + this.tileSize / 2;
        const targetY = data.tile_y * this.tileSize + this.tileSize / 2;

        // Smooth movement interpolation
        const dx = targetX - sprite.x;
        const dy = targetY - sprite.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > 1) {
            // Animate movement
            this.scene.tweens.add({
                targets: [sprite, label],
                x: targetX,
                y: (target) => target === sprite ? targetY : targetY - this.tileSize,
                duration: 200,
                ease: 'Linear',
            });
        } else {
            sprite.x = targetX;
            sprite.y = targetY;
            label.x = targetX;
            label.y = targetY - this.tileSize;
        }

        // Update facing
        this.setFacing(sprite, data.facing || 'south');

        // Update action indicator
        if (data.current_action) {
            label.setText(`${data.chosen_name || agentId}\n[${data.current_action}]`);
        } else {
            label.setText(data.chosen_name || WORLD_CONFIG.AGENT_NAMES[agentId] || agentId);
        }
    }

    /**
     * Remove agent sprite
     */
    removeAgentSprite(agentId) {
        if (this.sprites[agentId]) {
            this.sprites[agentId].destroy();
            delete this.sprites[agentId];
        }
        if (this.labels[agentId]) {
            this.labels[agentId].destroy();
            delete this.labels[agentId];
        }
    }

    /**
     * Set sprite facing direction
     */
    setFacing(sprite, facing) {
        const rotations = {
            'north': 0,
            'east': Math.PI / 2,
            'south': Math.PI,
            'west': -Math.PI / 2,
        };
        sprite.setRotation(rotations[facing] || Math.PI);
    }

    /**
     * Select an agent
     */
    selectAgent(agentId) {
        this.selectedAgentId = agentId;
        const sprite = this.sprites[agentId];

        if (sprite && this.selectionIndicator) {
            this.selectionIndicator.setVisible(true);
            this.selectionIndicator.setPosition(sprite.x, sprite.y);

            // Dispatch custom event
            this.scene.events.emit('agentSelected', agentId);
        }
    }

    /**
     * Clear selection
     */
    clearSelection() {
        this.selectedAgentId = null;
        if (this.selectionIndicator) {
            this.selectionIndicator.setVisible(false);
        }
        this.scene.events.emit('selectionCleared');
    }

    /**
     * Get selected agent
     */
    getSelectedAgent() {
        return this.selectedAgentId;
    }

    /**
     * Focus camera on agent
     */
    focusOnAgent(agentId) {
        const sprite = this.sprites[agentId];
        if (sprite) {
            this.scene.cameras.main.centerOn(sprite.x, sprite.y);
        }
    }

    /**
     * Update selection indicator position
     */
    update() {
        if (this.selectedAgentId && this.selectionIndicator) {
            const sprite = this.sprites[this.selectedAgentId];
            if (sprite) {
                this.selectionIndicator.setPosition(sprite.x, sprite.y);
            }
        }
    }

    /**
     * Render agents on minimap
     */
    renderOnMinimap(ctx, scale) {
        for (const [agentId, sprite] of Object.entries(this.sprites)) {
            const color = WORLD_CONFIG.AGENT_COLORS[agentId];
            const r = (color >> 16) & 0xff;
            const g = (color >> 8) & 0xff;
            const b = color & 0xff;

            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.beginPath();
            ctx.arc(
                sprite.x / this.tileSize * scale,
                sprite.y / this.tileSize * scale,
                3,
                0,
                Math.PI * 2
            );
            ctx.fill();
        }
    }
}
