# World System Architecture

**Version**: 1.0
**Status**: Design Document
**Visual Reference**: Described but not attached - proceeding with textual specification

---

## 1. Core Design Principles

### 1.1 Authority Model
- **Server authoritative**: Python backend owns all world state
- **Client render-only**: Browser displays snapshots and interpolates movement
- **No client-side decisions**: Inventory, actions, beliefs, locations decided by server

### 1.2 Time Domains
| Domain | Rate | Purpose |
|--------|------|---------|
| Render | 60 FPS | Visual display, interpolation |
| Simulation | 10 Hz (100ms) | Movement, physics, reservations |
| Cognition | Event-driven | Model calls on meaningful decisions |
| Debate Cycle | Hourly | Existing theological debates |

### 1.3 Integration Strategy
- World system **coexists** with existing debate orchestrator
- Agents exist in world AND participate in debates
- World events can provide evidence for debates
- Debate outcomes can affect world state (rituals, artifacts)

---

## 2. World Schema

### 2.1 Database Tables (add to religion_memory.db)

```sql
-- World instance metadata
CREATE TABLE world_state (
    id INTEGER PRIMARY KEY DEFAULT 1,
    world_seed INTEGER NOT NULL,
    world_version TEXT NOT NULL,
    simulation_tick INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config_json TEXT  -- World configuration
);

-- Terrain chunks (32x32 tiles each)
CREATE TABLE world_chunks (
    chunk_x INTEGER NOT NULL,
    chunk_y INTEGER NOT NULL,
    terrain_data BLOB NOT NULL,  -- Compressed tile array
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (chunk_x, chunk_y)
);

-- Agent spatial state
CREATE TABLE agent_positions (
    agent_id TEXT PRIMARY KEY,  -- 'Zealot', 'Skeptic', 'Trickster'
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    facing TEXT DEFAULT 'south',  -- north/south/east/west
    current_action TEXT,  -- Current action type
    action_target_id TEXT,  -- Target object/agent ID
    action_progress REAL DEFAULT 0.0,  -- 0.0 to 1.0
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- World objects (landmarks, resources, items)
CREATE TABLE world_objects (
    object_id TEXT PRIMARY KEY,
    object_type TEXT NOT NULL,  -- 'landmark', 'resource', 'item', 'structure'
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    state_json TEXT,  -- Type-specific state
    owner_agent_id TEXT,  -- NULL for unowned
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interacted TIMESTAMP
);

-- Agent inventories
CREATE TABLE agent_inventories (
    agent_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (agent_id, item_id)
);

-- Resource reservations (prevent conflicts)
CREATE TABLE resource_reservations (
    reservation_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    UNIQUE(resource_id)
);

-- World events (observable outcomes)
CREATE TABLE world_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    tick INTEGER NOT NULL,
    tile_x INTEGER,
    tile_y INTEGER,
    actor_id TEXT,
    target_id TEXT,
    event_data TEXT,  -- JSON payload
    visibility_radius INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent observations (what each agent has perceived)
CREATE TABLE agent_observations (
    observation_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    event_id TEXT,  -- Reference to world_events
    observation_type TEXT NOT NULL,  -- 'direct', 'hearsay', 'inference'
    source_agent_id TEXT,  -- For hearsay
    observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence REAL DEFAULT 1.0
);

-- Agent goals and plans
CREATE TABLE agent_goals (
    goal_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    goal_type TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'active',  -- active, suspended, completed, failed
    target_data TEXT,  -- JSON with goal specifics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline_tick INTEGER
);

-- Conversation sessions
CREATE TABLE world_conversations (
    conversation_id TEXT PRIMARY KEY,
    participants TEXT NOT NULL,  -- JSON array of agent_ids
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status TEXT DEFAULT 'active'  -- active, ended
);

CREATE TABLE conversation_turns (
    turn_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    speaker_id TEXT NOT NULL,
    content TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES world_conversations(conversation_id)
);
```

### 2.2 Tile Types

| ID | Type | Walkable | Description |
|----|------|----------|-------------|
| 0 | void | No | Out of bounds |
| 1 | grass | Yes | Basic terrain |
| 2 | dirt | Yes | Paths, clearings |
| 3 | stone | Yes | Rocky ground |
| 4 | sand | Yes | Beaches, desert |
| 5 | water_shallow | No | Shoreline |
| 6 | water_deep | No | Lakes, rivers |
| 7 | forest_floor | Yes | Under trees (slower) |
| 8 | bridge | Yes | Over water |
| 9 | wall | No | Structure walls |
| 10 | floor_wood | Yes | Interior floors |
| 11 | floor_stone | Yes | Temple/archive floors |

### 2.3 Elevation Layers
- Layer 0: Ground level
- Layer 1: Elevated terrain (+8 pixels)
- Layer 2: High ground (+16 pixels)
- Bridges connect across water at Layer 1

---

## 3. World Generation

### 3.1 Landmarks (Authored Placement)

| Landmark | Location | Purpose |
|----------|----------|---------|
| **Debate Commons** | Center | Where debates occur, main gathering |
| **Sacred Archive** | Northeast | Scriptorium, knowledge storage |
| **Ritual Grounds** | Northwest | Ceremony site, sacred images |
| **Workshop** | Southeast | Crafting, artifact creation |
| **Garden of Emergence** | Southwest | Resource gathering, meditation |
| **Bridge of Paradox** | West river | Trickster-associated crossing |
| **Veridicus Tower** | East hill | Skeptic's observation point |
| **Axioma Sanctuary** | North | Zealot's structured space |
| **Ruins of Iteration** | Far south | Ancient/mysterious site |

### 3.2 Procedural Elements
- Forest placement: Perlin noise with seed
- Water bodies: Flood-fill from seed points
- Paths: A* between landmarks
- Resources: Clustered spawn around landmarks

### 3.3 World Size
- **Initial**: 128×128 tiles (4 chunks × 4 chunks)
- **Expandable**: Up to 256×256 tiles
- **Chunk size**: 32×32 tiles
- **Tile size**: 16×16 pixels

---

## 4. Agent Cognition Architecture

### 4.1 Perception System
```
Agent Perception Range: 8 tiles (default)
  - Clear terrain: Full range
  - Forest: Reduced to 5 tiles
  - Walls: Block line of sight
  - Night: Reduced by 50%

Perception Contents:
  - Nearby agents (position, facing, action)
  - Visible objects (type, state)
  - Recent events within range
  - Terrain features
```

### 4.2 Cognition Loop
```
Every meaningful event or interval:
1. PERCEIVE: Gather local observations
2. RETRIEVE: Query relevant memories
3. UPDATE: Revise working beliefs
4. GOAL: Select or continue goal
5. PLAN: Generate action sequence
6. PROPOSE: Submit action to engine
7. OBSERVE: Receive outcome
8. LEARN: Update memory and skills
```

### 4.3 Decision Envelope (Model Input)
```json
{
  "schema_version": "1.0",
  "decision_id": "uuid",
  "world_id": "trickster-world-1",
  "agent_id": "Zealot",
  "tick": 12345,
  "observation": {
    "position": {"x": 64, "y": 72},
    "nearby_agents": [...],
    "visible_objects": [...],
    "recent_events": [...],
    "current_goal": {...}
  },
  "available_actions": [
    {"type": "move", "targets": ["north", "east", "south", "west"]},
    {"type": "inspect", "targets": ["object_123"]},
    {"type": "converse", "targets": ["Skeptic"]}
  ],
  "deadline_ms": 5000
}
```

### 4.4 Action Result (Engine Output)
```json
{
  "decision_id": "uuid",
  "status": "success|failed|invalid|timeout",
  "failure_reason": null,
  "effects": [
    {"type": "moved", "from": [64, 72], "to": [65, 72]},
    {"type": "observed", "event_id": "evt_456"}
  ],
  "new_tick": 12346
}
```

---

## 5. Affordance System

### 5.1 Core Affordances (10 minimum)

| Affordance | Preconditions | Effects | Duration |
|------------|---------------|---------|----------|
| **move** | Path exists, not blocked | Change position | 1-3 ticks |
| **inspect** | Adjacent to object | Gain knowledge | 2 ticks |
| **gather** | Resource present, has capacity | Add to inventory | 5 ticks |
| **give** | Has item, target adjacent | Transfer item | 1 tick |
| **rest** | Any safe location | Restore energy | 10 ticks |
| **converse** | Agent adjacent, not busy | Exchange information | Variable |
| **read** | Adjacent to text object | Gain knowledge | 3 ticks |
| **write** | At scriptorium, has knowledge | Create text object | 10 ticks |
| **craft** | At workshop, has materials | Create artifact | 15 ticks |
| **perform_ritual** | At ritual site, knows ritual | Execute ritual | 20 ticks |

### 5.2 Action Validation
```python
def validate_action(agent, action, world_state) -> ValidationResult:
    # 1. Check action type exists
    # 2. Verify preconditions met
    # 3. Check target accessibility
    # 4. Verify no conflicting reservations
    # 5. Check agent capacity/resources
    return ValidationResult(valid=True, reason=None)
```

---

## 6. Frontend Architecture

### 6.1 Route Structure
```
/           - Existing terminal interface
/world      - New world explorer (Phaser 3)
/bible      - Existing Living Bible
```

### 6.2 World Renderer Stack
```
Phaser 3.70+ (verified current version)
├── Tilemap Layer (terrain)
├── Object Layer (landmarks, resources)
├── Agent Layer (characters)
├── UI Layer (labels, panels)
└── Effect Layer (particles, highlights)
```

### 6.3 Data Flow
```
Backend (Python)
    │
    ├── world_state.json (snapshot)
    │   └── Tick, agent positions, visible objects
    │
    └── world_events.json (delta stream)
        └── Recent events since last snapshot

Frontend (Phaser)
    │
    ├── Load snapshot on connect
    ├── Apply deltas for updates
    ├── Interpolate movement (client-side visual only)
    └── Render at 60 FPS
```

### 6.4 UI Panels (Dark Translucent)
- **Agent Inspector**: Click agent → show identity, goals, inventory
- **Object Inspector**: Click object → show state, affordances
- **Event Feed**: Collapsible sidebar with recent events
- **Minimap**: Top-right corner, clickable navigation
- **Mode Indicator**: LIVE AI / REPLAY / DEGRADED

---

## 7. Integration with Debate System

### 7.1 World → Debate Pipeline
```
World Event (e.g., agent discovers ruins)
    ↓
Stored in world_events + agent_observations
    ↓
Agent memory updated with evidence
    ↓
Evidence becomes eligible for debate proposals
    ↓
Agent can reference evidence in challenges/votes
```

### 7.2 Debate → World Pipeline
```
Debate Outcome (e.g., new ritual accepted)
    ↓
Ritual stored in shared memory (existing)
    ↓
World system notified of new ritual
    ↓
Ritual site object updated with new ritual
    ↓
Agents can now perform_ritual at site
```

### 7.3 Cycle Timing
```
Debate Cycle: Every 60 minutes
World Simulation: Continuous at 10 Hz

During debate:
- World simulation continues
- Agents may be "at commons" during debates
- Debate outcome triggers world state updates
```

---

## 8. Research Harness

### 8.1 Experiment Configuration
```yaml
experiment_id: "spatial-memory-001"
hypothesis: "Spatial constraints improve factual consistency"
conditions:
  - name: "full-spatial"
    perception_enabled: true
    hearsay_enabled: true
  - name: "omniscient"
    perception_enabled: false
    hearsay_enabled: false
seeds: [42, 123, 456, 789, 1011]
ticks_per_run: 10000
metrics:
  - belief_consistency
  - goal_completion_rate
  - navigation_efficiency
  - cooperation_success
```

### 8.2 Headless Runner
```python
class ExperimentRunner:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.world = WorldSimulation(headless=True)

    async def run(self) -> ExperimentResults:
        for seed in self.config.seeds:
            for condition in self.config.conditions:
                await self.run_trial(seed, condition)
        return self.aggregate_results()
```

### 8.3 Metrics Collection
- **Per-tick**: Agent positions, actions, observations
- **Per-event**: Action success/failure, belief changes
- **Per-run**: Goal completion, cooperation instances
- **Aggregate**: Cross-condition comparisons

---

## 9. File Structure

```
ai_religion_architects/
├── world/                      # NEW: World system
│   ├── __init__.py
│   ├── simulation.py           # Core simulation engine
│   ├── terrain.py              # World generation
│   ├── pathfinding.py          # A* navigation
│   ├── perception.py           # Agent perception
│   ├── affordances.py          # Action system
│   ├── cognition.py            # Decision loop
│   └── research/               # Research harness
│       ├── runner.py
│       ├── metrics.py
│       └── replay.py
├── orchestration/
│   ├── claude_orchestrator.py  # Existing (modify)
│   └── world_orchestrator.py   # NEW: World tick manager
└── memory/
    └── world_memory.py         # NEW: World state persistence

public/
├── world.html                  # NEW: World viewer
├── js/
│   ├── world/                  # NEW: World frontend
│   │   ├── phaser-config.js
│   │   ├── world-scene.js
│   │   ├── agent-sprite.js
│   │   ├── terrain-layer.js
│   │   └── ui-panels.js
│   └── ... existing JS
├── styles/
│   └── world.css               # NEW: World styling
├── data/
│   ├── world_state.json        # NEW: World snapshot
│   └── ... existing data
└── assets/                     # NEW: Pixel art assets
    ├── tiles/
    ├── agents/
    └── objects/
```

---

## 10. Implementation Phases

### Phase 1: Minimal Vertical Slice (Target: First)
- [ ] Database migrations for world tables
- [ ] Single agent (Axioma) positioned in 32×32 map
- [ ] Basic terrain rendering (grass, water, stone)
- [ ] Movement with pathfinding
- [ ] Perception of nearby tiles
- [ ] Action: move, inspect
- [ ] Frontend: Phaser scene with agent sprite

### Phase 2: Full Agent Population
- [ ] All 3 agents in world
- [ ] Agent identity display (chosen names)
- [ ] Basic interactions between agents
- [ ] Conversation system

### Phase 3: Landmarks and Affordances
- [ ] Full 128×128 world with landmarks
- [ ] 10 affordances implemented
- [ ] Resource system (gather, give)
- [ ] Artifact creation

### Phase 4: Debate Integration
- [ ] World evidence → debate proposals
- [ ] Debate outcomes → world effects
- [ ] Ritual performance at ritual site

### Phase 5: Research Harness
- [ ] Headless runner
- [ ] Metric collection
- [ ] Experiment configuration
- [ ] Ablation framework

---

**Architecture Ready for Implementation**
