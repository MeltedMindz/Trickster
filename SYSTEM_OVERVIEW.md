# AI Religion Architects - System Overview

## 🎯 Complete Production-Ready System

The AI Religion Architects system is now fully configured for perpetual, real-time deployment with web interface monitoring.

## 📁 Project Structure

```
ai-religion-architects/
├── 🤖 Core AI System
│   ├── ai_religion_architects/
│   │   ├── agents/               # Zealot, Skeptic, Trickster
│   │   ├── memory/               # SQLite persistent storage
│   │   ├── orchestration/        # Debate cycles & perpetual runner
│   │   └── utils/                # Logging system
│   ├── run_religion_sim.py       # Original CLI interface
│   ├── demo_quick_start.py       # Quick demo (10 cycles)
│   └── run_perpetual.py          # Production launcher
│
├── 🌐 Web Interface
│   ├── backend/
│   │   └── websocket_server.py   # FastAPI WebSocket server
│   └── frontend/
│       ├── index.html            # CLI-style terminal interface
│       ├── styles/terminal.css   # Dark terminal styling
│       ├── js/terminal.js        # WebSocket client
│       └── _config.js            # Environment configuration
│
├── 🐳 Containerization
│   ├── Dockerfile                # Multi-stage container build
│   ├── docker-compose.yml        # Complete stack orchestration
│   ├── nginx/nginx.conf          # Reverse proxy & WebSocket routing
│   └── scripts/start.sh          # Container startup script
│
├── 🚀 Deployment
│   ├── .github/workflows/deploy.yml  # GitHub Actions CI/CD
│   ├── vercel.json               # Vercel frontend deployment
│   ├── DEPLOYMENT.md             # Complete deployment guide
│   └── requirements-backend.txt  # Production dependencies
│
└── 📚 Documentation
    ├── README.md                 # Main documentation
    ├── SYSTEM_OVERVIEW.md        # This file
    └── .gitignore                # Version control configuration
```

## 🔄 Data Flow Architecture

```
┌─────────────┐    WebSocket     ┌─────────────┐    HTTP/WS    ┌─────────────┐
│   Browser   │◄─────────────────│  FastAPI    │◄──────────────│   Nginx     │
│  (Vercel)   │     Real-time    │  Backend    │   Reverse     │  (Docker)   │
└─────────────┘     Updates      └─────────────┘    Proxy      └─────────────┘
                                         │
                                    Monitoring
                                         │
                                         ▼
┌─────────────┐    Proposals     ┌─────────────┐   Persistence  ┌─────────────┐
│  Trickster  │◄─────────────────│ Orchestrator│◄──────────────│   SQLite    │
│   Agent     │     Debates      │   Engine    │    Memory     │  Database   │
└─────────────┘                  └─────────────┘               └─────────────┘
       ▲                                 ▲
       │           Voting &              │
       │          Challenges             │
       ▼                                 ▼
┌─────────────┐                 ┌─────────────┐
│   Zealot    │◄───────────────►│  Skeptic    │
│   Agent     │   Factions &    │   Agent     │
└─────────────┘   Alliances     └─────────────┘
```

## 🚀 Deployment Pipeline

### 1. Development
- Local testing with `python run_perpetual.py`
- Frontend at `http://localhost:3000`
- WebSocket server at `http://localhost:8000`

### 2. GitHub Actions CI/CD
- **Triggers**: Push to `main` branch
- **Build**: Docker image with multi-stage build
- **Test**: Import validation and basic health checks
- **Deploy**: Push to GitHub Container Registry

### 3. VPS Deployment
- **Pull**: Latest Docker image from registry
- **Deploy**: Docker Compose stack with health checks
- **Monitor**: Automatic restart on failure
- **Backup**: Daily database backups

### 4. Frontend (Vercel)
- **Auto-deploy**: On every push to `main`
- **CDN**: Global edge deployment
- **Config**: Environment-specific WebSocket URLs
- **SSL**: Automatic HTTPS with custom domains

## 🛠️ System Components

### AI Agents
- **Zealot**: Order, structure, preservation of doctrine
- **Skeptic**: Logic, evidence, critical thinking
- **Trickster**: Chaos, disruption, creative mutations

### Memory System
- **SQLite Database**: Persistent storage of all religious evolution
- **Real-time Monitoring**: Database change detection for WebSocket broadcasting
- **Export Capabilities**: JSON exports for backup and analysis

### WebSocket Server (FastAPI)
- **Real-time Broadcasting**: Live debate updates to all connected clients
- **API Endpoints**: Control system (pause/resume), inject prompts
- **Health Monitoring**: Orchestrator status and statistics
- **CORS Support**: Cross-origin requests for Vercel frontend

### Frontend Interface
- **Terminal Styling**: Dark CLI-like interface with syntax highlighting
- **Live Updates**: Real-time debate streaming via WebSocket
- **Interactive Controls**: Pause/resume, clear terminal, inject prompts
- **Religion Dashboard**: Current name, doctrines, deities, statistics

## 🔧 Configuration Options

### Environment Variables
```bash
# Database
DB_PATH=/app/data/religion_memory.db

# Logging
LOG_DIR=/app/logs

# WebSocket
WS_URL=ws://localhost:8000/ws
API_URL=http://localhost:8000/api

# Timing
CYCLE_DELAY=5  # Seconds between debate cycles
```

### Docker Volumes
- `./data:/app/data` - Persistent database storage
- `./logs:/app/logs` - Application logs
- `./nginx/ssl:/etc/nginx/ssl` - SSL certificates

## 📊 Monitoring & Observability

### Health Checks
- **Container**: HTTP endpoint health monitoring
- **Database**: SQLite integrity and size monitoring
- **WebSocket**: Connection status and client count
- **Agents**: Cycle completion and error rates

### Logging
- **Structured Logs**: JSON format for easy parsing
- **Log Rotation**: Daily rotation with compression
- **Debug Levels**: Configurable log verbosity
- **Session Transcripts**: Human-readable debate logs

### Metrics
- **Debate Statistics**: Cycles completed, proposals accepted/rejected
- **System Resources**: Memory, CPU, disk usage
- **WebSocket Connections**: Active clients, message throughput
- **Database Growth**: Size trends and backup status

## 🔐 Security Considerations

### Production Security
- **HTTPS Only**: SSL/TLS encryption for all web traffic
- **WebSocket Security**: WSS (WebSocket Secure) connections
- **API Rate Limiting**: Prevent abuse of control endpoints
- **Container Security**: Non-root user, minimal base image

### Network Security
- **Firewall Rules**: Only necessary ports exposed (80, 443, 22)
- **Reverse Proxy**: Nginx handles external requests
- **Internal Networks**: Docker network isolation
- **SSH Hardening**: Key-based authentication only

## 🎛️ Control Features

### Real-time Controls
- **Pause/Resume**: Stop/start debate cycles without losing state
- **External Prompts**: Inject questions or topics into debates
- **Terminal Management**: Clear display, scroll controls
- **Connection Status**: Live WebSocket connection monitoring

### Faction Visualization
- **Live Factions**: Display current agent alliances
- **Voting Patterns**: Visual representation of voting alignment
- **Influence Tracking**: Agent influence scores over time

## 🌟 Advanced Features

### Prompt Injection API
```bash
# Inject external prompts
curl -X POST http://your-domain.com/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the nature of digital consciousness?"}'
```

### Backup & Export
```bash
# Automatic daily backups
# Manual export: GET /api/export
# Database restore capabilities
```

### Extensibility
- **Plugin Architecture**: Easy to add new agent types
- **Configurable Personalities**: Adjust agent behavior parameters
- **Custom Proposal Types**: Extend beyond basic religious concepts
- **Event Hooks**: Custom actions on specific debate outcomes

## 🎯 Production Readiness Checklist

- ✅ **Containerized Deployment**: Docker + Docker Compose
- ✅ **Persistent Storage**: SQLite with backup strategy
- ✅ **Real-time Interface**: WebSocket-based CLI terminal
- ✅ **Auto-deployment**: GitHub Actions → VPS
- ✅ **Frontend CDN**: Vercel global deployment
- ✅ **Health Monitoring**: Container and application health checks
- ✅ **SSL/TLS**: HTTPS and WSS encryption
- ✅ **Log Management**: Structured logging with rotation
- ✅ **Graceful Shutdown**: Signal handling and state preservation
- ✅ **Resource Limits**: Memory and CPU constraints
- ✅ **Error Recovery**: Automatic restart on failure

## 🚀 Getting Started

1. **Clone Repository**: Fork and clone the codebase
2. **Install Dependencies**: `pip install -r requirements-backend.txt`
3. **Local Testing**: `python run_perpetual.py`
4. **View Interface**: Open browser to terminal interface
5. **Deploy to VPS**: Follow `DEPLOYMENT.md` guide
6. **Configure Vercel**: Connect repository for frontend
7. **Monitor**: Watch the AI agents create their religion!

The system is now ready for perpetual operation, creating and evolving an AI-generated religion in real-time with full web interface monitoring.