// AI Religion Architects - Frontend Configuration
window.AI_RELIGION_CONFIG = {
    // Production VPS endpoints
    WS_URL: 'ws://5.78.71.231:8000/ws',
    API_URL: 'http://5.78.71.231:8000/api',
    
    // Fallback to localhost for development
    FALLBACK_WS_URL: 'ws://localhost:8000/ws',
    FALLBACK_API_URL: 'http://localhost:8000/api',
    
    // Frontend settings
    AUTO_RECONNECT: true,
    RECONNECT_INTERVAL: 5000,
    PING_INTERVAL: 30000
};

// Auto-detect environment and set appropriate URLs
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔧 Development mode detected - using localhost endpoints');
    window.AI_RELIGION_CONFIG.WS_URL = window.AI_RELIGION_CONFIG.FALLBACK_WS_URL;
    window.AI_RELIGION_CONFIG.API_URL = window.AI_RELIGION_CONFIG.FALLBACK_API_URL;
} else {
    console.log('🚀 Production mode detected - using VPS endpoints');
}

console.log('⚙️ AI Religion Config loaded:', window.AI_RELIGION_CONFIG);