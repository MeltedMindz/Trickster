/**
 * Terrain Renderer
 * Handles rendering the tile-based terrain using Phaser graphics
 */

class TerrainRenderer {
    constructor(scene) {
        this.scene = scene;
        this.tileSize = WORLD_CONFIG.TILE_SIZE;
        this.worldSize = WORLD_CONFIG.WORLD_SIZE;

        // Graphics object for terrain
        this.terrainGraphics = null;

        // Terrain data (2D array of tile types)
        this.terrainData = null;

        // Cached textures
        this.tileTextures = {};
    }

    /**
     * Initialize terrain graphics
     */
    init() {
        this.terrainGraphics = this.scene.add.graphics();
        this.terrainGraphics.setDepth(0);

        // Create tile textures
        this.createTileTextures();
    }

    /**
     * Create procedural textures for each tile type
     */
    createTileTextures() {
        const graphics = this.scene.make.graphics({ x: 0, y: 0, add: false });

        for (let type = 0; type <= 11; type++) {
            const color = WORLD_CONFIG.TILE_COLORS[type] || 0x000000;
            const key = `tile_${type}`;

            graphics.clear();

            // Base fill
            graphics.fillStyle(color, 1);
            graphics.fillRect(0, 0, this.tileSize, this.tileSize);

            // Add some texture variation based on type
            if (type === 1) { // Grass - add dots
                graphics.fillStyle(0x2d5e2d, 0.3);
                for (let i = 0; i < 4; i++) {
                    const x = Math.floor(Math.random() * (this.tileSize - 2)) + 1;
                    const y = Math.floor(Math.random() * (this.tileSize - 2)) + 1;
                    graphics.fillRect(x, y, 2, 2);
                }
            } else if (type === 7) { // Forest - add darker spots
                graphics.fillStyle(0x1a3a1a, 0.4);
                for (let i = 0; i < 3; i++) {
                    const x = Math.floor(Math.random() * (this.tileSize - 3)) + 1;
                    const y = Math.floor(Math.random() * (this.tileSize - 3)) + 1;
                    graphics.fillRect(x, y, 3, 3);
                }
            } else if (type === 5 || type === 6) { // Water - add wave lines
                graphics.lineStyle(1, 0xffffff, 0.2);
                const offset = type === 6 ? 2 : 0;
                graphics.lineBetween(2 + offset, 6, 14 - offset, 6);
                graphics.lineBetween(4 + offset, 10, 12 - offset, 10);
            }

            // Add subtle border
            graphics.lineStyle(1, 0x000000, 0.1);
            graphics.strokeRect(0, 0, this.tileSize, this.tileSize);

            graphics.generateTexture(key, this.tileSize, this.tileSize);
            this.tileTextures[type] = key;
        }

        graphics.destroy();
    }

    /**
     * Load terrain data from JSON
     */
    async loadTerrain() {
        try {
            const response = await fetch(WORLD_CONFIG.DATA_PATH + WORLD_CONFIG.TERRAIN_FILE);
            if (response.ok) {
                const data = await response.json();
                this.terrainData = data.terrain;
                return true;
            }
        } catch (e) {
            console.warn('Could not load terrain file, generating placeholder');
        }

        // Generate placeholder terrain if no file
        this.generatePlaceholderTerrain();
        return false;
    }

    /**
     * Generate placeholder terrain for testing
     */
    generatePlaceholderTerrain() {
        this.terrainData = [];

        for (let y = 0; y < this.worldSize; y++) {
            const row = [];
            for (let x = 0; x < this.worldSize; x++) {
                // Simple noise-based terrain
                const nx = x / this.worldSize;
                const ny = y / this.worldSize;

                // Create some variation
                const noise = Math.sin(nx * 10) * Math.cos(ny * 10) +
                              Math.sin(nx * 20 + ny * 15) * 0.5;

                let tile = 1; // Default grass

                // River on west side
                if (Math.abs(x - 20) < 3 && y > 20 && y < 108) {
                    tile = Math.abs(x - 20) < 1 ? 6 : 5;
                }
                // Central area - stone floor
                else if (Math.sqrt((x - 64) ** 2 + (y - 64) ** 2) < 5) {
                    tile = 11;
                }
                // Paths
                else if ((y >= 62 && y <= 66 && x > 20 && x < 108) ||
                         (x >= 62 && x <= 66 && y > 20 && y < 108)) {
                    tile = 2;
                }
                // Forest patches
                else if (noise > 0.5) {
                    tile = 7;
                }
                // Stone patches
                else if (noise < -0.7) {
                    tile = 3;
                }

                row.push(tile);
            }
            this.terrainData.push(row);
        }
    }

    /**
     * Render terrain to the scene
     */
    render() {
        if (!this.terrainData) return;

        // Clear existing terrain
        this.terrainGraphics.clear();

        // Get camera bounds for culling
        const camera = this.scene.cameras.main;
        const startX = Math.max(0, Math.floor((camera.scrollX - 50) / this.tileSize));
        const startY = Math.max(0, Math.floor((camera.scrollY - 50) / this.tileSize));
        const endX = Math.min(this.worldSize, Math.ceil((camera.scrollX + camera.width / camera.zoom + 50) / this.tileSize));
        const endY = Math.min(this.worldSize, Math.ceil((camera.scrollY + camera.height / camera.zoom + 50) / this.tileSize));

        // Render visible tiles
        for (let y = startY; y < endY; y++) {
            for (let x = startX; x < endX; x++) {
                const tileType = this.terrainData[y]?.[x] ?? 0;
                const color = WORLD_CONFIG.TILE_COLORS[tileType] || 0x000000;

                const px = x * this.tileSize;
                const py = y * this.tileSize;

                this.terrainGraphics.fillStyle(color, 1);
                this.terrainGraphics.fillRect(px, py, this.tileSize, this.tileSize);

                // Add subtle grid lines
                this.terrainGraphics.lineStyle(1, 0x000000, 0.1);
                this.terrainGraphics.strokeRect(px, py, this.tileSize, this.tileSize);
            }
        }
    }

    /**
     * Render minimap
     */
    renderMinimap(canvas) {
        if (!this.terrainData) return;

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Scale factor
        const scale = canvas.width / this.worldSize;

        for (let y = 0; y < this.worldSize; y++) {
            for (let x = 0; x < this.worldSize; x++) {
                const tileType = this.terrainData[y]?.[x] ?? 0;
                const color = WORLD_CONFIG.TILE_COLORS[tileType] || 0x000000;

                // Convert hex to CSS color
                const r = (color >> 16) & 0xff;
                const g = (color >> 8) & 0xff;
                const b = color & 0xff;
                ctx.fillStyle = `rgb(${r},${g},${b})`;

                ctx.fillRect(
                    Math.floor(x * scale),
                    Math.floor(y * scale),
                    Math.ceil(scale),
                    Math.ceil(scale)
                );
            }
        }
    }

    /**
     * Get tile at world position
     */
    getTileAt(worldX, worldY) {
        const tileX = Math.floor(worldX / this.tileSize);
        const tileY = Math.floor(worldY / this.tileSize);

        if (tileX < 0 || tileX >= this.worldSize || tileY < 0 || tileY >= this.worldSize) {
            return { type: 0, name: 'Void' };
        }

        const type = this.terrainData?.[tileY]?.[tileX] ?? 0;
        return {
            type: type,
            name: TILE_NAMES[type] || 'Unknown',
            x: tileX,
            y: tileY,
        };
    }

    /**
     * Update terrain rendering (called on camera move)
     */
    update() {
        this.render();
    }
}
