/**
 * World Application Entry Point
 * Initializes Phaser and the world viewer
 */

// Global references
window.game = null;
window.worldScene = null;

/**
 * Initialize the world viewer
 */
function initWorld() {
    // Initialize UI controller
    window.uiController = new UIController();
    window.uiController.init();

    // Phaser game configuration
    const config = {
        type: Phaser.AUTO,
        parent: 'game-container',
        width: window.innerWidth - WORLD_CONFIG.PANEL_WIDTH - 20,
        height: window.innerHeight - 60,
        backgroundColor: '#0a0a0a',
        pixelArt: true,
        roundPixels: true,
        antialias: false,
        scene: WorldScene,
        scale: {
            mode: Phaser.Scale.RESIZE,
            autoCenter: Phaser.Scale.CENTER_BOTH,
        },
        render: {
            pixelArt: true,
            antialias: false,
        },
    };

    // Create Phaser game
    window.game = new Phaser.Game(config);

    // Store scene reference when ready
    window.game.events.on('ready', () => {
        window.worldScene = window.game.scene.getScene('WorldScene');
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.game) {
            const panelWidth = document.getElementById('info-panel')?.offsetWidth || WORLD_CONFIG.PANEL_WIDTH;
            window.game.scale.resize(
                window.innerWidth - panelWidth - 20,
                window.innerHeight - 60
            );
        }
    });

    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        if (!window.worldScene) return;

        const cam = window.worldScene.cameras.main;
        const moveSpeed = 50;

        switch (e.key) {
            case 'ArrowUp':
            case 'w':
                cam.scrollY -= moveSpeed / cam.zoom;
                break;
            case 'ArrowDown':
            case 's':
                cam.scrollY += moveSpeed / cam.zoom;
                break;
            case 'ArrowLeft':
            case 'a':
                cam.scrollX -= moveSpeed / cam.zoom;
                break;
            case 'ArrowRight':
            case 'd':
                cam.scrollX += moveSpeed / cam.zoom;
                break;
            case '+':
            case '=':
                cam.setZoom(Math.min(cam.zoom * 1.2, WORLD_CONFIG.MAX_ZOOM));
                break;
            case '-':
                cam.setZoom(Math.max(cam.zoom / 1.2, WORLD_CONFIG.MIN_ZOOM));
                break;
            case 'c':
                window.worldScene.centerOnAgents();
                break;
            case '1':
                window.worldScene.focusOnAgent('Zealot');
                break;
            case '2':
                window.worldScene.focusOnAgent('Skeptic');
                break;
            case '3':
                window.worldScene.focusOnAgent('Trickster');
                break;
            case 'Escape':
                window.worldScene.agentSprites.clearSelection();
                window.uiController.clearSelection();
                break;
        }
    });

    console.log('World viewer initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWorld);
} else {
    initWorld();
}
