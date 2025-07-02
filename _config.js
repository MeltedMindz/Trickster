// Configuration for different environments
const config = {
  development: {
    WS_URL: 'ws://localhost:8000/ws',
    API_URL: 'http://localhost:8000/api'
  },
  production: {
    // Replace with your VPS domain
    WS_URL: 'wss://your-vps-domain.com/ws',
    API_URL: 'https://your-vps-domain.com/api'
  }
};

// Auto-detect environment
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const currentConfig = isProduction ? config.production : config.development;

// Export configuration
window.AI_RELIGION_CONFIG = currentConfig;