// AI Religion Architects - Static Frontend Configuration
window.AI_RELIGION_CONFIG = {
    // Static mode - no live connections
    STATIC_MODE: true,
    
    // API endpoints (only used for manual data loading)
    API_URL: 'http://5.78.71.231:8000/api',
    
    // Frontend settings
    AUTO_REFRESH: false,
    UPDATE_INTERVAL: 0, // No auto-updates
    
    // Data sources
    STATIC_DATA_PATH: './data/',
    TRANSCRIPTS_PATH: './logs/'
};

console.log('📊 Static AI Religion Config loaded - updates via repository pushes only');