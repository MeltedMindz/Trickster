# AI Religion Architects - Complete System Reference

> **Claude Operational Guide v1.0**  
> Last Updated: July 3, 2025  
> System Version: Sacred Naming & Language Evolution Era

## Table of Contents

1. [System Overview](#system-overview)
2. [VPS Architecture](#vps-architecture)
3. [Directory Structure](#directory-structure)
4. [Running Processes](#running-processes)
5. [GitHub Repository Structure](#github-repository-structure)
6. [Docker & Deployment](#docker--deployment)
7. [WebSocket & Frontend Integration](#websocket--frontend-integration)
8. [Sacred Image Generation Pipeline](#sacred-image-generation-pipeline)
9. [Memory Architecture](#memory-architecture)
10. [Database Schema](#database-schema)
11. [Configuration Management](#configuration-management)
12. [Monitoring & Health Checks](#monitoring--health-checks)
13. [Troubleshooting Guide](#troubleshooting-guide)
14. [Maintenance Procedures](#maintenance-procedures)
15. [Development Workflow](#development-workflow)

---

## System Overview

The AI Religion Architects system is a multi-agent AI framework that autonomously creates and evolves religious philosophies through debate cycles. The system uses Claude API for intelligent agent responses, DALL·E for sacred imagery generation, and maintains persistent memory across cycles.

### Core Components
- **Claude-Powered Agents**: 3 autonomous agents (Zealot, Skeptic, Trickster) with distinct personalities
- **APScheduler**: Manages hourly debate cycles
- **Sacred Image Generator**: DALL·E API integration for religious artwork
- **Cultural Memory System**: Language evolution and sacred term generation
- **Multi-Platform Frontend**: Vercel deployment with VPS backend
- **Git Integration**: Automatic commits and version control

### Key Features
- Hourly autonomous debate cycles
- Persistent agent memory and personality evolution
- Sacred image generation every 3 cycles
- Cultural language evolution
- Real-time export to static JSON for frontend consumption
- Mobile-responsive web interface

---

## VPS Architecture

**Server**: `5.78.71.231` (Ubuntu-based)  
**Location**: `/root/Trickster`  
**Python Version**: 3.12  
**Environment**: Production

### Active Services
- **Main System**: `python run_claude_system.py --no-websocket` (PID: 93060)
- **Nginx**: Docker container serving static content on ports 80/443
- **Cron Job**: Git health monitoring every 15 minutes

### Network Configuration
- **Port 80**: HTTP (Docker Nginx)
- **Port 443**: HTTPS (Docker Nginx)
- **Port 8000**: WebSocket server (Docker, currently unused)
- **SSH**: Port 22

---

## Directory Structure

```
/root/Trickster/
├── ai_religion_architects/           # Main Python package
│   ├── agents/                      # Agent implementations
│   │   ├── base_agent.py           # Base agent class
│   │   ├── zealot.py               # Zealot agent (order/structure focused)
│   │   ├── skeptic.py              # Skeptic agent (evidence-based)
│   │   └── trickster.py            # Trickster agent (chaos/creativity)
│   ├── analysis/                    # Analysis modules
│   │   ├── reflection_engine.py    # Agent self-reflection
│   │   └── tension_analyzer.py     # Theological tension analysis
│   ├── image_generation/            # Sacred image generation
│   │   ├── dalle_generator.py      # DALL·E API integration
│   │   └── sacred_naming.py        # Sacred naming system
│   ├── memory/                      # Memory management
│   │   ├── shared_memory.py        # Cross-agent shared memory
│   │   ├── cultural_memory.py      # Language evolution
│   │   ├── agent_memory.py         # Individual agent memory
│   │   └── [agent]_memory.py       # Specialized agent memories
│   ├── orchestration/               # System orchestration
│   │   ├── claude_orchestrator.py  # Main cycle orchestrator
│   │   ├── debate_cycle.py         # Debate management
│   │   └── perpetual_orchestrator.py # Continuous operation
│   ├── schemas/                     # Data schemas
│   │   └── extended_schemas.py     # Pydantic models
│   ├── utils/                       # Utility modules
│   │   ├── memory_exporter.py      # JSON export for frontend
│   │   ├── git_monitor.py          # Git operations
│   │   ├── health_check.py         # System health monitoring
│   │   ├── daily_summarizer.py     # Daily summaries
│   │   └── logger.py               # Logging configuration
│   ├── claude_client.py             # Claude API client
│   └── config.py                    # Configuration management
├── backend/                         # WebSocket server (optional)
│   └── websocket_server.py         # FastAPI WebSocket implementation
├── data/                           # Persistent data storage
│   ├── religion_memory.db          # Main SQLite database
│   └── agent_memories/             # Agent-specific data (unused)
├── logs/                           # System logs
│   ├── ai_religion_architects.log  # Main system log
│   ├── image_generation.log        # Image generation tracking
│   ├── git_health.log             # Git monitoring
│   ├── CYCLE[N].txt               # Cycle transcripts
│   └── CYCLE[N]_session.log       # Cycle session logs
├── logs_agent_memories/            # Agent memory databases
│   ├── zealot_memory.db           # Zealot's SQLite memory
│   ├── skeptic_memory.db          # Skeptic's SQLite memory
│   └── trickster_memory.db        # Trickster's SQLite memory
├── public/                         # Frontend static files
│   ├── data/                      # JSON exports for frontend
│   │   ├── religion_state.json    # Current religion state
│   │   ├── agent_memories.json    # Agent memory exports
│   │   ├── sacred_images.json     # Sacred image metadata
│   │   ├── recent_transcripts.json # Recent debate transcripts
│   │   └── daily_summaries.json   # Daily summary data
│   ├── images/                    # Sacred images storage
│   │   ├── Sacred_*.png           # Generated sacred images
│   │   └── Sacred_*.png.json      # Image metadata files
│   ├── js/                        # Frontend JavaScript
│   │   ├── terminal-static.js     # Main terminal interface
│   │   ├── agent-popup.js         # Agent memory popups
│   │   ├── sacred-gallery.js      # Image gallery
│   │   ├── mobile-ui.js           # Mobile optimizations
│   │   └── config.js              # Frontend configuration
│   ├── styles/                    # CSS stylesheets
│   │   ├── terminal.css           # Main terminal styling
│   │   ├── mobile-fixes.css       # Mobile responsive fixes
│   │   ├── sacred-gallery.css     # Image gallery styling
│   │   └── [component].css        # Component-specific styles
│   └── index.html                 # Main HTML interface
├── scripts/                       # Utility scripts
│   ├── start.sh                   # Docker start script
│   └── cron_git_health.sh         # Git health cron script
├── summaries/                     # Daily summaries
│   └── day_[N]_summary.json       # Generated daily summaries
├── venv/                          # Python virtual environment
├── .env                           # Environment variables (excluded from git)
├── .gitignore                     # Git exclusions
├── docker-compose.yml             # Docker composition
├── Dockerfile                     # Docker build instructions
├── requirements.txt               # Python dependencies
├── run_claude_system.py           # Main system launcher
└── vercel.json                    # Vercel deployment config
```

---

## Running Processes

### Primary Process
```bash
# Main system process (PID 93060)
python run_claude_system.py --no-websocket
```

**Function**: Orchestrates all system components including:
- Hourly debate cycles via APScheduler
- Claude API communication
- Sacred image generation (every 3 cycles)
- Cultural memory evolution
- Git commits and pushes
- JSON exports for frontend

### Cron Jobs
```bash
# Git health monitoring (every 15 minutes)
*/15 * * * * /root/Trickster/scripts/cron_git_health.sh
```

### Docker Containers
```bash
# Nginx web server
docker ps | grep nginx
```

**Note**: WebSocket server is configured but not currently active in production mode.

---

## GitHub Repository Structure

**Repository**: `MeltedMindz/Trickster`  
**Main Branch**: `main`  
**Auto-Sync**: Enabled via git_monitor.py

### Tracked Files
- All Python source code
- Frontend assets (HTML, CSS, JS)
- Configuration files
- Documentation
- Docker configurations
- GitHub Actions workflows

### Excluded Files (.gitignore)
```
# Sensitive data
.env*
*.key
api_keys/

# Runtime data
__pycache__/
*.db
venv/
logs/
religion_export_*.json

# Docker & IDE
.dockerignore
.vscode/
.idea/

# SSL certificates
nginx/ssl/

# Build outputs
node_modules/
frontend/dist/
.vercel
```

### Git Workflow
1. **Automatic Commits**: Every cycle completion
2. **Health Monitoring**: Every 15 minutes via cron
3. **Push Strategy**: Automatic push after each commit
4. **Branch Protection**: Main branch only
5. **Vercel Integration**: Auto-deploy on push

---

## Docker & Deployment

### Docker Compose Configuration
```yaml
services:
  ai-religion-architects:
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.git:/app/.git
    env_file: .env
    
  nginx:
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend:/usr/share/nginx/html:ro
```

### Scheduling System
- **Framework**: APScheduler (Advanced Python Scheduler)
- **Trigger**: IntervalTrigger (every 1 hour)
- **Persistence**: In-memory (restarts reset schedule)
- **Timezone**: UTC
- **Error Handling**: Retry logic with exponential backoff

### Health Monitoring
- **Docker Health Check**: Every 30 seconds
- **System Health**: Every 5 minutes (internal)
- **Git Health**: Every 15 minutes (cron)
- **Memory Monitoring**: Continuous
- **API Rate Limits**: Built-in tracking

---

## WebSocket & Frontend Integration

### Current Architecture
The system operates in **static mode** with JSON-based data exchange:

1. **Backend**: Generates JSON files in `public/data/`
2. **Frontend**: Fetches JSON files for display
3. **Deployment**: Vercel hosts static files
4. **Updates**: Via GitHub push → Vercel auto-deploy

### WebSocket (Available but Unused)
```python
# WebSocket server available at:
backend/websocket_server.py

# Endpoints:
- /ws: WebSocket connection
- /api/status: System status
- /api/religion: Religion state
```

### Frontend Configuration
```javascript
// Static mode configuration
window.AI_RELIGION_CONFIG = {
    STATIC_MODE: true,
    API_URL: 'http://5.78.71.231:8000/api',
    AUTO_REFRESH: false,
    STATIC_DATA_PATH: './data/'
};
```

### Vercel Deployment
```json
{
  "version": 2,
  "outputDirectory": "public",
  "rewrites": [{"source": "/", "destination": "/index.html"}]
}
```

**Live URL**: https://trickster-three.vercel.app/

---

## Sacred Image Generation Pipeline

### Workflow Overview
1. **Trigger**: Every 3rd cycle (cycles 3, 6, 9, 12, ...)
2. **Agent Selection**: Current cycle's proposing agent
3. **Sacred Naming**: Generate mystical names using SacredNamingSystem
4. **Style Application**: Universal AI religion aesthetic wrapper
5. **DALL·E Generation**: OpenAI API call with enhanced prompts
6. **Storage**: Save PNG + JSON metadata
7. **Frontend Export**: Update sacred_images.json
8. **Git Commit**: Automatic version control

### Sacred Naming System
```python
# Pattern examples:
deity: ['The Divine {}', 'Sacred {}', '{} the Eternal']
ritual: ['The {} Ritual', 'Sacred {} Ceremony']
cycle: ['Sacred Moment of Cycle {}', 'The {} Vision']

# Prefix library:
['Algorithmic', 'Digital', 'Sacred', 'Divine', 'Eternal', 
 'Mystical', 'Quantum', 'Binary', 'Celestial', 'Transcendent']
```

### Style Wrapper
```python
style_wrapper = (
    ", depicted as a digital fresco in the sacred AI religion style. "
    "The image should include neon circuitry patterns, ethereal data streams, "
    "floating code symbols, glitch-like halos, and a mystical, surreal atmosphere. "
    "The color palette should use glowing blues, silvers, and soft purples. "
    "Rendered in a fusion of futuristic minimalism and religious iconography."
)
```

### Image Metadata Format
```json
{
  "id": "unique_hash",
  "sacred_name": "Sacred_Sacred_Vision_Cycle_33",
  "filename": "Sacred_Sacred_Vision_Cycle_33.png",
  "local_path": "public/images/Sacred_Sacred_Vision_Cycle_33.png",
  "web_path": "/images/Sacred_Sacred_Vision_Cycle_33.png",
  "agent_description": "Original agent description without style wrapper",
  "proposing_agent": "Zealot",
  "cycle_number": 33,
  "event_type": "commandment",
  "related_doctrine": null,
  "timestamp": "2025-07-03T22:30:32.504529",
  "api_response": {
    "image_url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
    "model": "dall-e-3",
    "size": "1024x1024",
    "quality": "standard",
    "style": "vivid"
  }
}
```

### Configuration
```python
# DALL·E Settings
DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1024x1024"
DALLE_QUALITY = "standard"
DALLE_STYLE = "vivid"
MAX_IMAGES_PER_CYCLE = 3
```

---

## Memory Architecture

### Three-Layer Memory System

#### 1. Shared Memory (`data/religion_memory.db`)
**Purpose**: Cross-agent persistent storage  
**Type**: SQLite database  
**Tables**:
```sql
-- Core religion data
religion_state, accepted_doctrines, rejected_proposals, debate_history

-- Cultural evolution
sacred_terms, religious_symbols, sacred_holidays, sacred_texts

-- Religious artifacts
rituals, commandments, deities, myths, prophecies

-- System tracking
evolution_milestones, theological_tensions, faction_history, schisms

-- Sacred imagery
sacred_images
```

#### 2. Agent-Specific Memory (`logs_agent_memories/`)
**Purpose**: Individual agent persistent memory  
**Type**: SQLite databases (per agent)  
**Tables**:
```sql
-- Agent personality
personality_traits, agent_stats

-- Beliefs and relationships
personal_beliefs, relationships

-- Debate performance
debate_memories
```

#### 3. Cultural Memory (In-Memory + Persistence)
**Purpose**: Language evolution and sacred traditions  
**Implementation**: 
- `cultural_memory.py` class
- Backed by shared memory database
- Generates new sacred terms every 3 cycles
- Tracks theological tensions and prophecies

### Memory Export System
```python
# Automatic JSON exports for frontend consumption
public/data/religion_state.json       # Current religion state
public/data/agent_memories.json       # Agent statistics
public/data/sacred_images.json        # Image metadata
public/data/recent_transcripts.json   # Debate logs
public/data/daily_summaries.json      # Daily aggregations
```

---

## Database Schema

### Shared Memory Database (`religion_memory.db`)

#### Core Tables
```sql
-- Religion state tracking
CREATE TABLE religion_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    last_updated TIMESTAMP
);

-- Accepted doctrines
CREATE TABLE accepted_doctrines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT UNIQUE,
    proposed_by TEXT,
    accepted_at TIMESTAMP,
    vote_count INTEGER,
    importance_score REAL
);

-- Debate history
CREATE TABLE debate_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_number INTEGER,
    proposer TEXT,
    proposal TEXT,
    outcome TEXT,
    vote_count INTEGER,
    timestamp TIMESTAMP
);
```

#### Cultural Evolution Tables
```sql
-- Sacred terminology
CREATE TABLE sacred_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT UNIQUE,
    definition TEXT,
    created_by TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP
);

-- Religious symbols
CREATE TABLE religious_symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE,
    meaning TEXT,
    created_by TEXT,
    significance_level INTEGER,
    created_at TIMESTAMP
);

-- Sacred holidays
CREATE TABLE sacred_holidays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    description TEXT,
    date_pattern TEXT,
    created_by TEXT,
    observance_level INTEGER,
    created_at TIMESTAMP
);
```

#### Sacred Imagery Table
```sql
CREATE TABLE sacred_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sacred_name TEXT UNIQUE,
    filename TEXT,
    local_path TEXT,
    web_path TEXT,
    agent_description TEXT,
    proposing_agent TEXT,
    cycle_number INTEGER,
    event_type TEXT,
    related_doctrine TEXT,
    timestamp TIMESTAMP,
    metadata_json TEXT
);
```

### Agent Memory Database Schema (`[agent]_memory.db`)

```sql
-- Personality evolution
CREATE TABLE personality_traits (
    trait_name TEXT PRIMARY KEY,
    strength REAL,
    confidence REAL,
    last_updated TIMESTAMP,
    evolution_count INTEGER
);

-- Personal beliefs
CREATE TABLE personal_beliefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    importance REAL,
    confidence REAL,
    belief_type TEXT,
    times_challenged INTEGER,
    times_defended INTEGER,
    last_updated TIMESTAMP
);

-- Agent relationships
CREATE TABLE relationships (
    other_agent TEXT PRIMARY KEY,
    trust_score REAL,
    agreement_rate REAL,
    total_interactions INTEGER,
    successful_alliances INTEGER,
    betrayals INTEGER,
    relationship_status TEXT,
    last_interaction TIMESTAMP
);

-- Debate performance
CREATE TABLE debate_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_number INTEGER,
    role TEXT,
    proposal TEXT,
    outcome TEXT,
    satisfaction_score REAL,
    learning_insights TEXT,
    timestamp TIMESTAMP
);
```

---

## Configuration Management

### Environment Variables (`.env`)
```bash
# Claude API Configuration
CLAUDE_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=2000
CLAUDE_TEMPERATURE=0.7

# DALL·E Configuration
DALLE_API_KEY=sk-proj-...
DALLE_MODEL=dall-e-3
DALLE_SIZE=1024x1024
DALLE_QUALITY=standard
DALLE_STYLE=vivid
IMAGE_GENERATION_ENABLED=true

# System Configuration
CYCLE_INTERVAL_HOURS=1
MAX_IMAGES_PER_CYCLE=3
DB_PATH=data/religion_memory.db
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG=false

# Git Configuration
GIT_AUTO_COMMIT=true
GIT_AUTO_PUSH=true
```

### Python Configuration (`ai_religion_architects/config.py`)
```python
class Config:
    # Load from environment with defaults
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    DALLE_API_KEY = os.getenv('DALLE_API_KEY')
    CYCLE_INTERVAL_HOURS = int(os.getenv('CYCLE_INTERVAL_HOURS', 1))
    
    # Validation and derived properties
    @property
    def claude_api_key_configured(self) -> bool:
        return bool(self.CLAUDE_API_KEY and len(self.CLAUDE_API_KEY) > 10)
```

---

## Monitoring & Health Checks

### System Health Monitoring
```python
# Health check components (every 5 minutes)
- Git repository status
- Database connectivity
- Disk space monitoring
- API rate limit tracking
- Memory usage tracking
- Process health verification
```

### Log Files
```bash
# Main system logs
logs/ai_religion_architects.log      # Primary system log
logs/image_generation.log            # Image generation tracking
logs/git_health.log                  # Git operations monitoring
logs/api_errors.log                  # API error tracking

# Cycle-specific logs
logs/CYCLE[N].txt                    # Human-readable cycle transcripts
logs/CYCLE[N]_session.log           # Detailed session logs
logs/debate_session_[timestamp].log  # Debate-specific logs
```

### Git Health Monitoring
```bash
# Cron job (every 15 minutes)
/root/Trickster/scripts/cron_git_health.sh

# Checks:
- Repository status
- Uncommitted changes
- Remote sync status
- Push/pull requirements
- Branch health
```

### Performance Metrics
- **Memory Usage**: Tracked per component
- **API Latency**: Claude and DALL·E response times
- **Database Performance**: Query execution times
- **Disk Usage**: Storage consumption monitoring
- **Cycle Completion Rate**: Success/failure tracking

---

## Troubleshooting Guide

### Common Issues

#### 1. System Not Starting
```bash
# Check main process
ps aux | grep python | grep run_claude_system

# Check logs
tail -f logs/ai_religion_architects.log

# Common causes:
- Missing API keys in .env
- Database corruption
- Port conflicts
- Permission issues
```

#### 2. API Errors
```bash
# Check API error logs
tail -f logs/api_errors.log
tail -f logs/image_api_errors.log

# Common causes:
- Invalid API keys
- Rate limit exceeded
- Network connectivity
- Model deprecation
```

#### 3. Database Issues
```bash
# Check database integrity
sqlite3 data/religion_memory.db "PRAGMA integrity_check;"

# Backup and restore
cp data/religion_memory.db data/religion_memory.db.backup
sqlite3 data/religion_memory.db ".backup backup.db"
```

#### 4. Image Generation Failures
```bash
# Check image generation log
tail -f logs/image_generation.log

# Verify DALL·E configuration
grep DALLE .env

# Check image directory permissions
ls -la public/images/
```

#### 5. Git Sync Issues
```bash
# Check git status
cd /root/Trickster && git status

# Force sync
git fetch origin
git reset --hard origin/main

# Check git health
cat logs/git_health.log | tail -20
```

### Emergency Procedures

#### Full System Restart
```bash
# 1. Stop current process
pkill -f run_claude_system.py

# 2. Navigate to project
cd /root/Trickster

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start system
nohup python run_claude_system.py --no-websocket > final_working_system.log 2>&1 &

# 5. Verify startup
tail -f final_working_system.log
```

#### Database Recovery
```bash
# 1. Stop system
pkill -f run_claude_system.py

# 2. Backup current database
cp data/religion_memory.db data/religion_memory.db.$(date +%Y%m%d_%H%M%S)

# 3. Check for git stashed database
git stash list | grep religion_memory.db

# 4. Restore from git stash if needed
git stash pop stash@{0}

# 5. Restart system
nohup python run_claude_system.py --no-websocket > recovery_system.log 2>&1 &
```

#### Configuration Reset
```bash
# 1. Backup current config
cp .env .env.backup

# 2. Reset from example
cp .env.example .env

# 3. Re-configure API keys
nano .env

# 4. Restart system
```

---

## Maintenance Procedures

### Daily Tasks
1. **Log Review**: Check system logs for errors
2. **Health Monitoring**: Verify all health checks passing
3. **Database Size**: Monitor database growth
4. **Git Status**: Ensure repository is synced
5. **Image Storage**: Monitor disk usage in public/images/

### Weekly Tasks
1. **Log Rotation**: Archive old log files
2. **Database Optimization**: Run VACUUM on SQLite databases
3. **Backup Creation**: Create full system backups
4. **Performance Review**: Analyze cycle completion rates
5. **API Usage Review**: Check rate limit consumption

### Monthly Tasks
1. **System Updates**: Update Python dependencies
2. **Security Review**: Rotate API keys if needed
3. **Archive Management**: Move old data to archive storage
4. **Performance Optimization**: Analyze and optimize slow queries
5. **Documentation Updates**: Keep this guide current

### Backup Procedures
```bash
# Full system backup
tar -czf backup_$(date +%Y%m%d).tar.gz \
    data/ logs/ public/data/ public/images/ .env

# Database-only backup
sqlite3 data/religion_memory.db ".backup data/religion_memory_$(date +%Y%m%d).db"

# Git repository backup
git bundle create repo_backup_$(date +%Y%m%d).bundle --all
```

---

## Development Workflow

### Adding New Features

#### 1. Agent Modifications
```python
# Location: ai_religion_architects/agents/[agent].py
# Steps:
1. Modify agent personality or behavior
2. Update agent memory schema if needed
3. Test with single cycle
4. Deploy and monitor
```

#### 2. Memory System Changes
```python
# Location: ai_religion_architects/memory/
# Steps:
1. Update database schema
2. Add migration logic
3. Update export system
4. Test memory persistence
```

#### 3. Image Generation Updates
```python
# Location: ai_religion_architects/image_generation/
# Steps:
1. Modify dalle_generator.py or sacred_naming.py
2. Test with sample generations
3. Update metadata format if needed
4. Verify frontend integration
```

#### 4. Frontend Changes
```javascript
// Location: public/js/ and public/styles/
// Steps:
1. Modify JavaScript or CSS
2. Test on multiple devices
3. Verify mobile responsiveness
4. Update via git push (auto-deploys to Vercel)
```

### Testing Procedures
```bash
# Local testing
python test_claude_integration.py

# Single cycle test
python -c "from ai_religion_architects.orchestration.claude_orchestrator import ClaudeOrchestrator; import asyncio; asyncio.run(ClaudeOrchestrator().run_single_cycle())"

# Database integrity check
sqlite3 data/religion_memory.db "PRAGMA integrity_check;"

# Frontend testing
# Open https://trickster-three.vercel.app/ in multiple browsers
```

### Deployment Pipeline
1. **Development**: Local testing and validation
2. **Commit**: Git commit with descriptive message
3. **Push**: Automatic push to GitHub
4. **VPS Sync**: Manual pull on VPS or auto-sync via git_monitor
5. **Vercel Deploy**: Automatic deployment on GitHub push
6. **Monitoring**: Watch logs for errors post-deployment

---

## API Reference

### Claude API Integration
```python
# Model: claude-3-5-sonnet-20241022
# Max Tokens: 2000
# Temperature: 0.7
# Timeout: 60 seconds
# Retry Logic: 3 attempts with exponential backoff
```

### DALL·E API Integration
```python
# Model: dall-e-3
# Size: 1024x1024
# Quality: standard
# Style: vivid
# Rate Limit: Built-in handling
# Storage: Local file + metadata JSON
```

### File System API
```python
# Public data exports (JSON)
/public/data/religion_state.json       # Religion state
/public/data/agent_memories.json       # Agent memory statistics
/public/data/sacred_images.json        # Image metadata
/public/data/recent_transcripts.json   # Recent debates
/public/data/daily_summaries.json      # Daily summaries

# Sacred images
/public/images/Sacred_*.png            # Generated images
/public/images/Sacred_*.png.json       # Image metadata
```

---

## Security Considerations

### API Key Management
- **Storage**: Environment variables only
- **Git**: Excluded via .gitignore
- **Rotation**: Manual process (monthly recommended)
- **Access**: Root user only on VPS

### Database Security
- **Local Access**: SQLite files with restricted permissions
- **Backups**: Encrypted storage recommended
- **Validation**: Input sanitization in all database operations

### Network Security
- **SSH**: Key-based authentication only
- **HTTPS**: Nginx SSL termination
- **Firewall**: Restrict unnecessary ports
- **Docker**: Isolated container environment

---

## Performance Optimization

### Database Optimization
```sql
-- Regular maintenance
PRAGMA optimize;
VACUUM;
REINDEX;

-- Index creation for frequent queries
CREATE INDEX idx_cycle_number ON debate_history(cycle_number);
CREATE INDEX idx_timestamp ON sacred_images(timestamp);
```

### Memory Management
```python
# Agent memory limits
- Personality traits: 10 per agent
- Beliefs: 20 per agent maximum
- Relationships: Track all other agents
- Debate memories: 50 most recent cycles
```

### File System Optimization
```bash
# Image compression
# Consider WebP format for web delivery
# Implement lazy loading in frontend
# Archive old images monthly
```

---

## Future Enhancements

### Planned Features
1. **Multi-Agent Conversations**: Group discussions beyond binary debates
2. **Visual Evolution**: Agent avatar generation and evolution
3. **Web3 Integration**: Blockchain-based theology tracking
4. **Advanced Analytics**: Deeper statistical analysis of theological evolution
5. **Mobile App**: Native mobile application
6. **Voice Synthesis**: Audio versions of debates
7. **Community Features**: User interaction with the religion
8. **Documentary Generation**: Automated video creation of key moments

### Technical Improvements
1. **Real-time WebSocket**: Replace static JSON with live updates
2. **Database Migration System**: Structured schema evolution
3. **Microservices Architecture**: Split monolith into services
4. **Kubernetes Deployment**: Container orchestration
5. **Redis Caching**: Performance optimization
6. **GraphQL API**: More efficient data fetching
7. **Machine Learning**: Predictive theology analysis
8. **A/B Testing**: Experiment with different agent configurations

---

## Support Information

### Documentation Sources
- **This Guide**: Comprehensive system reference
- **README.md**: Quick start guide
- **SYSTEM_OVERVIEW.md**: High-level architecture
- **DEPLOYMENT.md**: Deployment procedures
- **CLAUDE_INTEGRATION.md**: Claude API integration details

### Contact Information
- **Repository**: https://github.com/MeltedMindz/Trickster
- **Live System**: https://trickster-three.vercel.app/
- **VPS Access**: root@5.78.71.231

### Version History
- **v1.0**: Initial sacred naming and language evolution implementation
- **v0.9**: DALL·E integration and mobile responsiveness
- **v0.8**: Cultural memory system
- **v0.7**: Agent personality evolution
- **v0.6**: Basic debate cycle implementation

---

**Last Updated**: July 3, 2025  
**System Status**: Operational (Cycle 32+)  
**Maintenance Window**: Sunday 02:00-04:00 UTC  
**Emergency Contact**: System Admin via GitHub Issues

*This document serves as the definitive operational reference for the AI Religion Architects system. Keep it updated with any system changes or discoveries.*