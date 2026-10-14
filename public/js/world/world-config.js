/**
 * World Configuration
 * Constants and settings for the world viewer
 */

window.WORLD_CONFIG = {
    // Tile settings
    TILE_SIZE: 16,
    CHUNK_SIZE: 32,
    WORLD_SIZE: 128,

    // Display settings
    CAMERA_ZOOM: 2,
    MIN_ZOOM: 0.5,
    MAX_ZOOM: 4,

    // Colors for tile types (indexed by TileType enum)
    TILE_COLORS: {
        0: 0x000000,   // VOID - Black
        1: 0x3d6e3d,   // GRASS - Forest green
        2: 0x8b7355,   // DIRT - Brown
        3: 0x707070,   // STONE - Gray
        4: 0xc2b280,   // SAND - Tan
        5: 0x4a90a4,   // WATER_SHALLOW - Light blue
        6: 0x1e5f74,   // WATER_DEEP - Dark blue
        7: 0x2d5a2d,   // FOREST_FLOOR - Dark green
        8: 0x8b4513,   // BRIDGE - Brown wood
        9: 0x4a4a4a,   // WALL - Dark gray
        10: 0xa0522d,  // FLOOR_WOOD - Sienna
        11: 0x696969,  // FLOOR_STONE - Dim gray
    },

    // Agent colors
    AGENT_COLORS: {
        'Zealot': 0xffd700,      // Gold
        'Skeptic': 0x4169e1,     // Royal blue
        'Trickster': 0x9932cc,   // Purple
    },

    // Agent chosen names
    AGENT_NAMES: {
        'Zealot': 'Axioma',
        'Skeptic': 'Veridicus',
        'Trickster': 'Paradoxia',
    },

    // Landmark colors by type
    LANDMARK_COLORS: {
        'gathering': 0xffffff,
        'archive': 0x4169e1,
        'ritual': 0xffd700,
        'workshop': 0xff8c00,
        'garden': 0x32cd32,
        'bridge': 0x8b4513,
        'tower': 0x4169e1,
        'sanctuary': 0xffd700,
        'ruins': 0x808080,
    },

    // Data paths
    DATA_PATH: './data/',
    WORLD_STATE_FILE: 'world_state.json',
    TERRAIN_FILE: 'world_terrain.json',

    // Refresh interval (ms) - 0 for static mode
    REFRESH_INTERVAL: 0,

    // UI settings
    PANEL_WIDTH: 280,
    MINIMAP_SIZE: 128,
};

// Tile type names for display
window.TILE_NAMES = [
    'Void',
    'Grass',
    'Dirt Path',
    'Stone',
    'Sand',
    'Shallow Water',
    'Deep Water',
    'Forest Floor',
    'Bridge',
    'Wall',
    'Wood Floor',
    'Stone Floor',
];
