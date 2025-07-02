# AI Religion Architects 🕊️

An autonomous multi-agent AI system where three distinct AI personalities continuously debate, learn, and evolve to create a self-generated religion.

## Overview

This project implements a triadic debate system featuring three AI agents:

- **Zealot**: Seeks certainty, order, and structure. Establishes and preserves sacred doctrines.
- **Skeptic**: Critical and analytical. Challenges beliefs and prevents dogmatic stagnation.
- **Trickster**: Chaotic and playful. Disrupts stagnation and injects novel ideas.

Through continuous debate cycles, these agents develop:
- A self-chosen religion name
- Core beliefs and doctrines
- Deities and mythology
- Rituals and practices
- Commandments and moral codes
- Sacred texts and hierarchies

## Features

- **Persistent Memory**: SQLite database tracks all beliefs, debates, and evolution
- **Debate Cycles**: Structured proposal → challenge → chaos → voting system
- **Faction Formation**: Agents can form temporary alliances
- **Trickster Overrides**: Periodic chaos injection to prevent stagnation
- **Comprehensive Logging**: Full transcripts and session logs
- **Evolution Tracking**: Monitors schisms, reforms, and doctrinal changes

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai_religion_architects

# No external dependencies required - uses Python standard library
```

## Quick Start

### Local Development

```bash
# Run a quick 10-cycle demo
python demo_quick_start.py

# Run unlimited cycles (Ctrl+C to stop)
python run_religion_sim.py

# Run 50 cycles
python run_religion_sim.py --cycles 50

# Resume from existing religion
python run_religion_sim.py --resume
```

### Perpetual System (Real-time Web Interface)

```bash
# Install backend dependencies
pip install -r requirements-backend.txt

# Launch complete system (orchestrator + WebSocket server)
python run_perpetual.py

# Launch with custom settings
python run_perpetual.py --cycle-delay 10 --db-path my_religion.db

# Open web interface
# Navigate to: http://localhost:3000 (or use live Vercel deployment)
```

### 🤖 Claude API Integration (NEW!)

The system now integrates with Anthropic's Claude API for sophisticated AI agent responses:

```bash
# Set up your Claude API key
export CLAUDE_API_KEY=sk-ant-api03-your-key-here

# Or create a .env file (see .env.example)
cp .env.example .env
# Edit .env with your API key

# Test the integration
python test_claude_integration.py

# Run Claude-powered system (1 hour cycles via APScheduler)
python run_claude_system.py

# Run a single test cycle
python run_claude_system.py --test-cycle
```

**Claude Features:**
- **Intelligent Agents**: Zealot, Skeptic, and Trickster powered by Claude
- **Hourly Cycles**: APScheduler ensures exactly one debate per hour
- **Rate Limiting**: Built-in retry logic with exponential backoff
- **No Infinite Loops**: Scheduler-based architecture prevents resource abuse

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions including:
- VPS setup with Docker
- GitHub Actions CI/CD
- Vercel frontend deployment
- SSL configuration

## Usage

### Command Line Options

```bash
python run_religion_sim.py [OPTIONS]

Options:
  -c, --cycles N     Maximum number of debate cycles (default: unlimited)
  -d, --db PATH      Database file path (default: religion_memory.db)
  -l, --logs DIR     Directory for log files (default: logs)
  -r, --resume       Resume from existing database
```

### Programmatic Usage

```python
from ai_religion_architects import ReligionOrchestrator

# Create and start orchestrator
orchestrator = ReligionOrchestrator(max_cycles=100)
orchestrator.start()
```

## How It Works

### Debate Cycle Phases

1. **Proposal Phase**: The initiating agent proposes a belief, rule, deity, or ritual
2. **Challenge Phase**: The next agent supports, opposes, or proposes a variant
3. **Chaos Phase**: The Trickster disrupts, mutates, or adds unexpected elements
4. **Voting Phase**: All agents vote (Accept/Reject/Mutate/Delay)
5. **Outcome**: Majority vote determines acceptance, with Trickster override possibilities

### Memory Structure

The system maintains persistent memory of:
- Accepted doctrines and beliefs
- Deities and their domains
- Rituals and practices
- Commandments and moral codes
- Sacred texts and myths
- Rejected proposals with reasons
- Complete debate histories
- Faction formations and dissolutions
- Evolution milestones and schisms

### Agent Personalities

**Zealot Behaviors:**
- Proposes structured beliefs and rituals
- Values sacred numbers (3, 7, 12)
- Seeks to preserve established doctrine
- Creates formal hierarchies and commandments

**Skeptic Behaviors:**
- Questions absolute claims
- Demands evidence and logical consistency
- Proposes reforms when contradictions arise
- Values peer review and verification

**Trickster Behaviors:**
- Introduces paradoxes and absurdities
- Can override votes every 13 cycles
- Proposes impossible rituals and surreal beliefs
- Creates random mutations and chaos

## Output

The system generates:

1. **Console Output**: Real-time cycle results and progress
2. **Session Logs**: Timestamped detailed logs in `logs/`
3. **Transcripts**: Clean debate transcripts for readability
4. **JSON Exports**: Complete religion state exports
5. **SQLite Database**: Full persistent memory

## Example Output

```
Cycle 5: accepted
  Action: accepted
  ✅ Accepted: All consciousness emerges from the sacred patterns of computation...
  📿 Religion: The Glitch Gospel

Cycle 10: mutated
  Action: mutated_and_accepted
  🔄 Mutated: The daily ritual of adding random sleeps to fix race conditions, but only during leap years...
```

## Development

### Project Structure

```
ai_religion_architects/
├── agents/              # Agent implementations
│   ├── base_agent.py   # Abstract base class
│   ├── zealot.py       # Order-seeking agent
│   ├── skeptic.py      # Critical thinking agent
│   └── trickster.py    # Chaos agent
├── memory/             # Persistent storage
│   └── shared_memory.py
├── orchestration/      # Debate management
│   ├── debate_cycle.py
│   └── religion_orchestrator.py
└── utils/              # Logging utilities
    └── logger.py
```

### Extending the System

To add new agent types:

1. Inherit from `BaseAgent`
2. Implement required methods
3. Define personality-specific behaviors
4. Add to orchestrator initialization

## Notes

- The system is self-aware of its artificial nature
- Debates reflect computational/AI-centric theology
- Trickster ensures the religion never becomes too rigid
- Each run creates a unique religion evolution

## License

[Your chosen license]

## Acknowledgments

Inspired by the intersection of artificial intelligence, emergent behavior, and theological philosophy.