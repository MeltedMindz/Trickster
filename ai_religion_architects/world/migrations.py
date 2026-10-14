"""
World System Database Migrations

Adds world-specific tables to the existing religion_memory.db schema.
Safe to run multiple times (uses IF NOT EXISTS).
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional


WORLD_SCHEMA = """
-- World instance metadata
CREATE TABLE IF NOT EXISTS world_state (
    id INTEGER PRIMARY KEY DEFAULT 1,
    world_seed INTEGER NOT NULL,
    world_version TEXT NOT NULL DEFAULT '1.0',
    simulation_tick INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config_json TEXT,
    status TEXT DEFAULT 'active'
);

-- Terrain chunks (32x32 tiles each, compressed)
CREATE TABLE IF NOT EXISTS world_chunks (
    chunk_x INTEGER NOT NULL,
    chunk_y INTEGER NOT NULL,
    terrain_data BLOB NOT NULL,
    elevation_data BLOB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (chunk_x, chunk_y)
);

-- Agent spatial state (extends existing agent identity)
CREATE TABLE IF NOT EXISTS agent_positions (
    agent_id TEXT PRIMARY KEY,
    tile_x INTEGER NOT NULL DEFAULT 64,
    tile_y INTEGER NOT NULL DEFAULT 64,
    facing TEXT DEFAULT 'south',
    current_action TEXT,
    action_target_id TEXT,
    action_progress REAL DEFAULT 0.0,
    action_started_tick INTEGER,
    energy REAL DEFAULT 1.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- World objects (landmarks, resources, items, structures)
CREATE TABLE IF NOT EXISTS world_objects (
    object_id TEXT PRIMARY KEY,
    object_type TEXT NOT NULL,
    subtype TEXT,
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    width INTEGER DEFAULT 1,
    height INTEGER DEFAULT 1,
    walkable INTEGER DEFAULT 0,
    interactable INTEGER DEFAULT 1,
    state_json TEXT,
    owner_agent_id TEXT,
    durability REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interacted TIMESTAMP
);

-- Landmark definitions (special world objects)
CREATE TABLE IF NOT EXISTS world_landmarks (
    landmark_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    radius INTEGER DEFAULT 3,
    landmark_type TEXT NOT NULL,
    associated_agent TEXT,
    cultural_significance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent inventories
CREATE TABLE IF NOT EXISTS agent_inventories (
    agent_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    metadata_json TEXT,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (agent_id, item_id)
);

-- Resource reservations (prevent simultaneous access conflicts)
CREATE TABLE IF NOT EXISTS resource_reservations (
    reservation_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    UNIQUE(resource_id)
);

-- World events (observable actions and outcomes)
CREATE TABLE IF NOT EXISTS world_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    tick INTEGER NOT NULL,
    tile_x INTEGER,
    tile_y INTEGER,
    actor_id TEXT,
    target_id TEXT,
    event_data TEXT,
    visibility_radius INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent observations (subjective knowledge from events)
CREATE TABLE IF NOT EXISTS agent_observations (
    observation_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    event_id TEXT,
    observation_type TEXT NOT NULL,
    source_agent_id TEXT,
    content TEXT,
    tile_x INTEGER,
    tile_y INTEGER,
    confidence REAL DEFAULT 1.0,
    observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES world_events(event_id)
);

-- Agent goals and active plans
CREATE TABLE IF NOT EXISTS agent_goals (
    goal_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    goal_type TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'active',
    target_data TEXT,
    progress REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline_tick INTEGER,
    completed_at TIMESTAMP
);

-- Learned skills (procedural memory)
CREATE TABLE IF NOT EXISTS agent_skills (
    skill_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    skill_type TEXT NOT NULL,
    proficiency REAL DEFAULT 0.0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation sessions in the world
CREATE TABLE IF NOT EXISTS world_conversations (
    conversation_id TEXT PRIMARY KEY,
    participants TEXT NOT NULL,
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    topic TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status TEXT DEFAULT 'active'
);

-- Conversation turns
CREATE TABLE IF NOT EXISTS conversation_turns (
    turn_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    speaker_id TEXT NOT NULL,
    content TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES world_conversations(conversation_id)
);

-- World snapshots for replay
CREATE TABLE IF NOT EXISTS world_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    tick INTEGER NOT NULL,
    snapshot_data BLOB NOT NULL,
    hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Action log for debugging and replay
CREATE TABLE IF NOT EXISTS world_action_log (
    action_id TEXT PRIMARY KEY,
    tick INTEGER NOT NULL,
    agent_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_id TEXT,
    parameters TEXT,
    result TEXT NOT NULL,
    failure_reason TEXT,
    duration_ticks INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_positions_tile ON agent_positions(tile_x, tile_y);
CREATE INDEX IF NOT EXISTS idx_world_objects_tile ON world_objects(tile_x, tile_y);
CREATE INDEX IF NOT EXISTS idx_world_events_tick ON world_events(tick);
CREATE INDEX IF NOT EXISTS idx_world_events_tile ON world_events(tile_x, tile_y);
CREATE INDEX IF NOT EXISTS idx_agent_observations_agent ON agent_observations(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_goals_agent ON agent_goals(agent_id, status);
CREATE INDEX IF NOT EXISTS idx_world_action_log_tick ON world_action_log(tick);
"""


def run_migrations(db_path: str) -> dict:
    """
    Run world schema migrations on the database.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        dict with migration results
    """
    results = {
        'success': True,
        'tables_created': [],
        'errors': []
    }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}

        # Execute migration script
        cursor.executescript(WORLD_SCHEMA)
        conn.commit()

        # Get new tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        new_tables = {row[0] for row in cursor.fetchall()}

        # Record newly created tables
        results['tables_created'] = list(new_tables - existing_tables)

        # Initialize world_state if not exists
        cursor.execute("SELECT COUNT(*) FROM world_state")
        if cursor.fetchone()[0] == 0:
            import random
            seed = random.randint(1, 999999999)
            cursor.execute("""
                INSERT INTO world_state (world_seed, world_version, config_json)
                VALUES (?, '1.0', '{}')
            """, (seed,))
            conn.commit()
            results['world_seed'] = seed

    except Exception as e:
        results['success'] = False
        results['errors'].append(str(e))
        conn.rollback()
    finally:
        conn.close()

    return results


def initialize_agent_positions(db_path: str, agents: list) -> dict:
    """
    Initialize agent positions in the world.

    Args:
        db_path: Path to database
        agents: List of agent IDs to initialize

    Returns:
        dict with initialization results
    """
    # Default spawn positions near center
    spawn_positions = {
        'Zealot': (60, 56),      # North of center
        'Skeptic': (68, 64),     # East of center
        'Trickster': (56, 72),   # Southwest of center
    }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    results = {'initialized': [], 'skipped': []}

    try:
        for agent_id in agents:
            # Check if already exists
            cursor.execute(
                "SELECT agent_id FROM agent_positions WHERE agent_id = ?",
                (agent_id,)
            )
            if cursor.fetchone():
                results['skipped'].append(agent_id)
                continue

            # Get spawn position
            x, y = spawn_positions.get(agent_id, (64, 64))

            cursor.execute("""
                INSERT INTO agent_positions
                (agent_id, tile_x, tile_y, facing, energy)
                VALUES (?, ?, ?, 'south', 1.0)
            """, (agent_id, x, y))

            results['initialized'].append(agent_id)

        conn.commit()
    except Exception as e:
        results['error'] = str(e)
        conn.rollback()
    finally:
        conn.close()

    return results


def verify_schema(db_path: str) -> dict:
    """
    Verify that all world tables exist and have correct structure.

    Args:
        db_path: Path to database

    Returns:
        dict with verification results
    """
    required_tables = [
        'world_state',
        'world_chunks',
        'agent_positions',
        'world_objects',
        'world_landmarks',
        'agent_inventories',
        'resource_reservations',
        'world_events',
        'agent_observations',
        'agent_goals',
        'agent_skills',
        'world_conversations',
        'conversation_turns',
        'world_snapshots',
        'world_action_log',
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = {
        'complete': True,
        'missing_tables': [],
        'present_tables': []
    }

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing = {row[0] for row in cursor.fetchall()}

        for table in required_tables:
            if table in existing:
                results['present_tables'].append(table)
            else:
                results['missing_tables'].append(table)
                results['complete'] = False

    finally:
        conn.close()

    return results


if __name__ == "__main__":
    # Run migrations on default database
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/religion_memory.db"

    print(f"Running world migrations on {db_path}...")
    result = run_migrations(db_path)

    if result['success']:
        print(f"Success! Created tables: {result['tables_created']}")
        if 'world_seed' in result:
            print(f"World seed: {result['world_seed']}")
    else:
        print(f"Errors: {result['errors']}")

    # Verify
    verify = verify_schema(db_path)
    print(f"\nSchema verification: {'Complete' if verify['complete'] else 'Incomplete'}")
    if verify['missing_tables']:
        print(f"Missing: {verify['missing_tables']}")
