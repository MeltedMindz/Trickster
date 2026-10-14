"""
World Simulation Engine

Core engine that manages:
- World state and tick progression
- Agent movement and actions
- Event generation and persistence
- Integration with existing systems
"""

import sqlite3
import json
import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime
from pathlib import Path
import threading
import queue

from .terrain import TerrainGenerator, TileType, TILE_PROPERTIES, save_landmarks_to_database
from .pathfinding import Pathfinder, Path as NavPath, PathResult
from .perception import PerceptionSystem, PerceptionResult, ObservationType
from .affordances import (
    AffordanceRegistry, Action, ActionType, ActionOutcome, ActionResult
)
from .migrations import run_migrations, initialize_agent_positions, verify_schema


@dataclass
class AgentState:
    """Runtime state of an agent in the world."""
    agent_id: str
    tile_x: int
    tile_y: int
    facing: str = 'south'
    current_action: Optional[ActionType] = None
    action_target_id: Optional[str] = None
    action_progress: float = 0.0
    action_started_tick: int = 0
    energy: float = 1.0
    chosen_name: str = ''
    current_path: Optional[NavPath] = None
    path_index: int = 0

    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'tile_x': self.tile_x,
            'tile_y': self.tile_y,
            'facing': self.facing,
            'current_action': self.current_action.value if self.current_action else None,
            'action_target_id': self.action_target_id,
            'action_progress': self.action_progress,
            'energy': self.energy,
            'chosen_name': self.chosen_name,
        }


@dataclass
class WorldEvent:
    """An event that occurred in the world."""
    event_id: str
    event_type: str
    tick: int
    tile_x: Optional[int]
    tile_y: Optional[int]
    actor_id: Optional[str]
    target_id: Optional[str]
    event_data: Dict
    visibility_radius: int = 5
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'event_id': self.event_id,
            'type': self.event_type,
            'tick': self.tick,
            'position': {'x': self.tile_x, 'y': self.tile_y} if self.tile_x else None,
            'actor': self.actor_id,
            'target': self.target_id,
            'data': self.event_data,
        }


class WorldSimulation:
    """
    Main world simulation engine.

    Manages:
    - Terrain and world generation
    - Agent positions and movement
    - Action validation and execution
    - Event generation
    - State persistence
    """

    AGENT_IDS = ['Zealot', 'Skeptic', 'Trickster']
    TICK_DURATION_MS = 100  # 10 Hz simulation

    def __init__(
        self,
        db_path: str = 'data/religion_memory.db',
        headless: bool = False,
        world_seed: Optional[int] = None
    ):
        """
        Initialize world simulation.

        Args:
            db_path: Path to SQLite database
            headless: If True, run without any display
            world_seed: Optional seed for world generation
        """
        self.db_path = db_path
        self.headless = headless

        # Ensure database schema is ready
        self._initialize_database()

        # Load or create world seed
        if world_seed is None:
            world_seed = self._get_or_create_seed()
        self.world_seed = world_seed

        # Initialize subsystems
        self.terrain = TerrainGenerator(world_seed, world_size=128)
        self.pathfinder = Pathfinder(
            is_walkable=self.terrain.is_walkable,
            get_cost=self.terrain.get_movement_cost,
            world_width=128,
            world_height=128
        )
        self.perception = PerceptionSystem(
            get_tile=self.terrain.get_tile,
            blocks_sight=self.terrain.blocks_sight,
            line_of_sight=self.pathfinder.line_of_sight
        )
        self.affordances = AffordanceRegistry()

        # Runtime state
        self.tick: int = 0
        self.agents: Dict[str, AgentState] = {}
        self.objects: Dict[str, Dict] = {}
        self.recent_events: List[WorldEvent] = []
        self.running: bool = False

        # Action queue for thread-safe action submission
        self._action_queue: queue.Queue = queue.Queue()

        # Load state from database
        self._load_state()

    def _initialize_database(self) -> None:
        """Initialize database with world schema."""
        result = run_migrations(self.db_path)
        if not result['success']:
            raise RuntimeError(f"Database migration failed: {result['errors']}")

        # Verify schema
        verify = verify_schema(self.db_path)
        if not verify['complete']:
            raise RuntimeError(f"Missing tables: {verify['missing_tables']}")

    def _get_or_create_seed(self) -> int:
        """Get existing world seed or create new one."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT world_seed FROM world_state WHERE id = 1")
            row = cursor.fetchone()
            if row:
                return row[0]

            # Create new seed
            import random
            seed = random.randint(1, 999999999)
            cursor.execute("""
                INSERT INTO world_state (id, world_seed, world_version)
                VALUES (1, ?, '1.0')
            """, (seed,))
            conn.commit()
            return seed
        finally:
            conn.close()

    def _load_state(self) -> None:
        """Load simulation state from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Load tick count
            cursor.execute("SELECT simulation_tick FROM world_state WHERE id = 1")
            row = cursor.fetchone()
            if row:
                self.tick = row['simulation_tick']

            # Load agent positions
            cursor.execute("SELECT * FROM agent_positions")
            for row in cursor.fetchall():
                agent_id = row['agent_id']
                self.agents[agent_id] = AgentState(
                    agent_id=agent_id,
                    tile_x=row['tile_x'],
                    tile_y=row['tile_y'],
                    facing=row['facing'] or 'south',
                    current_action=ActionType(row['current_action']) if row['current_action'] else None,
                    action_target_id=row['action_target_id'],
                    action_progress=row['action_progress'] or 0.0,
                    action_started_tick=row['action_started_tick'] or 0,
                    energy=row['energy'] or 1.0
                )

            # Initialize missing agents
            for agent_id in self.AGENT_IDS:
                if agent_id not in self.agents:
                    result = initialize_agent_positions(self.db_path, [agent_id])
                    # Reload after initialization
                    cursor.execute(
                        "SELECT * FROM agent_positions WHERE agent_id = ?",
                        (agent_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        self.agents[agent_id] = AgentState(
                            agent_id=agent_id,
                            tile_x=row['tile_x'],
                            tile_y=row['tile_y'],
                            facing='south',
                            energy=1.0
                        )

            # Load agent chosen names from existing system
            self._load_agent_identities()

            # Load world objects
            cursor.execute("SELECT * FROM world_objects")
            for row in cursor.fetchall():
                self.objects[row['object_id']] = dict(row)

            # Load recent events (last 100)
            cursor.execute("""
                SELECT * FROM world_events
                ORDER BY tick DESC LIMIT 100
            """)
            for row in cursor.fetchall():
                event = WorldEvent(
                    event_id=row['event_id'],
                    event_type=row['event_type'],
                    tick=row['tick'],
                    tile_x=row['tile_x'],
                    tile_y=row['tile_y'],
                    actor_id=row['actor_id'],
                    target_id=row['target_id'],
                    event_data=json.loads(row['event_data']) if row['event_data'] else {},
                    visibility_radius=row['visibility_radius'] or 5
                )
                self.recent_events.append(event)

            # Sort events by tick
            self.recent_events.sort(key=lambda e: e.tick)

        finally:
            conn.close()

        # Generate terrain if needed
        if not self._has_terrain_chunks():
            self.terrain.generate_full_world()
            self.terrain.save_to_database(self.db_path)
            save_landmarks_to_database(self.db_path)

        # Update pathfinder with agent obstacles
        self._update_pathfinder_obstacles()

    def _has_terrain_chunks(self) -> bool:
        """Check if terrain chunks exist in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM world_chunks")
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()

    def _load_agent_identities(self) -> None:
        """Load agent chosen names from the existing identity system."""
        # Try to load from agent_memories.json if exists
        try:
            json_path = Path(self.db_path).parent.parent / 'public' / 'data' / 'agent_memories.json'
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                    agents_data = data.get('agents', {})
                    for agent_id, agent_info in agents_data.items():
                        if agent_id in self.agents:
                            identity = agent_info.get('identity', {})
                            self.agents[agent_id].chosen_name = identity.get('chosen_name', agent_id)
        except Exception:
            pass

        # Default names if not loaded
        default_names = {
            'Zealot': 'Axioma',
            'Skeptic': 'Veridicus',
            'Trickster': 'Paradoxia'
        }
        for agent_id, agent in self.agents.items():
            if not agent.chosen_name:
                agent.chosen_name = default_names.get(agent_id, agent_id)

    def _update_pathfinder_obstacles(self) -> None:
        """Update pathfinder with current agent positions."""
        obstacles = {(a.tile_x, a.tile_y) for a in self.agents.values()}
        self.pathfinder.update_obstacles(obstacles)

    def simulate_tick(self) -> List[WorldEvent]:
        """
        Run one simulation tick.

        Returns:
            List of events that occurred this tick
        """
        self.tick += 1
        events = []

        # Process queued actions
        while not self._action_queue.empty():
            try:
                action = self._action_queue.get_nowait()
                outcome = self._execute_action(action)
                if outcome.result == ActionResult.SUCCESS:
                    for effect in outcome.effects:
                        event = self._create_event_from_effect(action, effect)
                        if event:
                            events.append(event)
            except queue.Empty:
                break

        # Update ongoing actions
        for agent_id, agent in self.agents.items():
            if agent.current_action:
                self._update_action_progress(agent)

            # Continue pathfinding movement
            if agent.current_path and agent.current_path.result == PathResult.SUCCESS:
                self._continue_movement(agent)

        # Energy regeneration (slow)
        for agent in self.agents.values():
            if agent.energy < 1.0 and not agent.current_action:
                agent.energy = min(1.0, agent.energy + 0.001)

        # Store events
        for event in events:
            self.recent_events.append(event)
            self._store_event(event)

        # Trim recent events
        if len(self.recent_events) > 200:
            self.recent_events = self.recent_events[-100:]

        # Update pathfinder obstacles
        self._update_pathfinder_obstacles()

        # Save tick to database periodically
        if self.tick % 10 == 0:
            self._save_tick()

        return events

    def _execute_action(self, action: Action) -> ActionOutcome:
        """Execute a validated action."""
        agent = self.agents.get(action.agent_id)
        if not agent:
            return ActionOutcome(
                result=ActionResult.INVALID,
                action_id=action.action_id,
                action_type=action.action_type,
                agent_id=action.agent_id,
                tick=self.tick,
                failure_reason="Agent not found"
            )

        # Validate action
        agent_state = agent.to_dict()
        world_state = {'objects': self.objects}
        is_valid, error = self.affordances.validate_action(action, agent_state, world_state)

        if not is_valid:
            return ActionOutcome(
                result=ActionResult.INVALID,
                action_id=action.action_id,
                action_type=action.action_type,
                agent_id=action.agent_id,
                tick=self.tick,
                failure_reason=error
            )

        # Execute based on action type
        effects = []

        if action.action_type == ActionType.MOVE:
            success, effect = self._execute_move(agent, action)
            if success:
                effects.append(effect)
            else:
                return ActionOutcome(
                    result=ActionResult.FAILED,
                    action_id=action.action_id,
                    action_type=action.action_type,
                    agent_id=action.agent_id,
                    tick=self.tick,
                    failure_reason=effect.get('reason', 'Move failed')
                )

        elif action.action_type == ActionType.INSPECT:
            effects.append(self._execute_inspect(agent, action))

        elif action.action_type == ActionType.CONVERSE:
            effects.append(self._execute_converse(agent, action))

        else:
            # Generic action handling
            agent.current_action = action.action_type
            agent.action_target_id = action.target_id
            agent.action_started_tick = self.tick
            agent.action_progress = 0.0

            duration = self.affordances.get_duration(action.action_type)
            effects.append({
                'type': 'action_started',
                'action': action.action_type.value,
                'duration': duration
            })

        # Apply energy cost
        cost = self.affordances.get_energy_cost(action.action_type)
        agent.energy = max(0.0, min(1.0, agent.energy - cost))

        return ActionOutcome(
            result=ActionResult.SUCCESS,
            action_id=action.action_id,
            action_type=action.action_type,
            agent_id=action.agent_id,
            tick=self.tick,
            effects=effects,
            duration_ticks=self.affordances.get_duration(action.action_type)
        )

    def _execute_move(self, agent: AgentState, action: Action) -> Tuple[bool, Dict]:
        """Execute a movement action."""
        target = action.target_position
        if not target:
            # Direction-based movement
            direction = action.parameters.get('direction', 'south')
            dx, dy = {
                'north': (0, -1),
                'south': (0, 1),
                'east': (1, 0),
                'west': (-1, 0)
            }.get(direction, (0, 0))
            target = (agent.tile_x + dx, agent.tile_y + dy)

        # Check walkability
        if not self.terrain.is_walkable(target[0], target[1]):
            return False, {'reason': 'Target not walkable'}

        # Check for other agents
        for other_id, other in self.agents.items():
            if other_id != agent.agent_id and (other.tile_x, other.tile_y) == target:
                return False, {'reason': 'Position occupied'}

        # Move agent
        old_pos = (agent.tile_x, agent.tile_y)
        agent.tile_x = target[0]
        agent.tile_y = target[1]
        agent.facing = self.pathfinder.get_direction(old_pos, target)

        return True, {
            'type': 'moved',
            'from': old_pos,
            'to': target,
            'facing': agent.facing
        }

    def _execute_inspect(self, agent: AgentState, action: Action) -> Dict:
        """Execute an inspect action."""
        target_id = action.target_id
        target_obj = self.objects.get(target_id)

        if target_obj:
            return {
                'type': 'inspected',
                'target': target_id,
                'object_type': target_obj.get('object_type'),
                'state': target_obj.get('state_json', {})
            }
        else:
            # Inspecting another agent
            target_agent = self.agents.get(target_id)
            if target_agent:
                return {
                    'type': 'inspected',
                    'target': target_id,
                    'agent_name': target_agent.chosen_name,
                    'action': target_agent.current_action.value if target_agent.current_action else None
                }

        return {'type': 'inspect_failed', 'target': target_id}

    def _execute_converse(self, agent: AgentState, action: Action) -> Dict:
        """Execute a conversation action."""
        target_id = action.target_id
        target_agent = self.agents.get(target_id)

        if not target_agent:
            return {'type': 'converse_failed', 'reason': 'Target not found'}

        # Check adjacency
        dist = abs(agent.tile_x - target_agent.tile_x) + abs(agent.tile_y - target_agent.tile_y)
        if dist > 3:
            return {'type': 'converse_failed', 'reason': 'Too far'}

        return {
            'type': 'conversation_started',
            'initiator': agent.agent_id,
            'target': target_id,
            'position': {'x': agent.tile_x, 'y': agent.tile_y}
        }

    def _update_action_progress(self, agent: AgentState) -> None:
        """Update progress on an ongoing action."""
        if not agent.current_action:
            return

        duration = self.affordances.get_duration(agent.current_action)
        elapsed = self.tick - agent.action_started_tick
        agent.action_progress = min(1.0, elapsed / duration)

        if agent.action_progress >= 1.0:
            # Action complete
            agent.current_action = None
            agent.action_target_id = None
            agent.action_progress = 0.0

    def _continue_movement(self, agent: AgentState) -> None:
        """Continue following a path."""
        if not agent.current_path or agent.path_index >= len(agent.current_path.waypoints):
            agent.current_path = None
            agent.path_index = 0
            return

        next_pos = agent.current_path.waypoints[agent.path_index]

        # Check if path is still valid
        if not self.terrain.is_walkable(next_pos[0], next_pos[1]):
            agent.current_path = None
            agent.path_index = 0
            return

        # Check for blocking agents
        for other_id, other in self.agents.items():
            if other_id != agent.agent_id and (other.tile_x, other.tile_y) == next_pos:
                # Wait for path to clear
                return

        # Move to next position
        old_pos = (agent.tile_x, agent.tile_y)
        agent.tile_x = next_pos[0]
        agent.tile_y = next_pos[1]
        agent.facing = self.pathfinder.get_direction(old_pos, next_pos)
        agent.path_index += 1

    def _create_event_from_effect(self, action: Action, effect: Dict) -> Optional[WorldEvent]:
        """Create a world event from an action effect."""
        agent = self.agents.get(action.agent_id)
        if not agent:
            return None

        return WorldEvent(
            event_id=str(uuid.uuid4()),
            event_type=effect.get('type', 'action'),
            tick=self.tick,
            tile_x=agent.tile_x,
            tile_y=agent.tile_y,
            actor_id=action.agent_id,
            target_id=action.target_id,
            event_data=effect,
            visibility_radius=5
        )

    def _store_event(self, event: WorldEvent) -> None:
        """Store event in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO world_events
                (event_id, event_type, tick, tile_x, tile_y, actor_id, target_id, event_data, visibility_radius)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.event_type,
                event.tick,
                event.tile_x,
                event.tile_y,
                event.actor_id,
                event.target_id,
                json.dumps(event.event_data),
                event.visibility_radius
            ))
            conn.commit()
        finally:
            conn.close()

    def _save_tick(self) -> None:
        """Save current tick to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE world_state SET simulation_tick = ?, last_updated = ?
                WHERE id = 1
            """, (self.tick, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()

    def save_state(self) -> None:
        """Save complete simulation state to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Save tick
            cursor.execute("""
                UPDATE world_state SET simulation_tick = ?, last_updated = ?
                WHERE id = 1
            """, (self.tick, datetime.now().isoformat()))

            # Save agent positions
            for agent_id, agent in self.agents.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_positions
                    (agent_id, tile_x, tile_y, facing, current_action,
                     action_target_id, action_progress, action_started_tick, energy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent_id,
                    agent.tile_x,
                    agent.tile_y,
                    agent.facing,
                    agent.current_action.value if agent.current_action else None,
                    agent.action_target_id,
                    agent.action_progress,
                    agent.action_started_tick,
                    agent.energy
                ))

            conn.commit()
        finally:
            conn.close()

    def get_perception(self, agent_id: str) -> Optional[PerceptionResult]:
        """Get perception result for an agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        # Convert agents to dict format for perception
        all_agents = {
            aid: {
                'agent_id': aid,
                'tile_x': a.tile_x,
                'tile_y': a.tile_y,
                'facing': a.facing,
                'current_action': a.current_action.value if a.current_action else None,
                'action_target_id': a.action_target_id,
                'chosen_name': a.chosen_name,
            }
            for aid, a in self.agents.items()
        }

        # Convert objects to list
        all_objects = list(self.objects.values())

        # Convert recent events to dicts
        recent = [e.to_dict() for e in self.recent_events[-50:]]

        # Get landmarks
        landmarks = [
            {
                'landmark_id': lm.landmark_id,
                'name': lm.name,
                'tile_x': lm.tile_x,
                'tile_y': lm.tile_y,
                'radius': lm.radius,
            }
            for lm in self.terrain.get_landmarks()
        ]

        return self.perception.perceive(
            agent_id=agent_id,
            agent_x=agent.tile_x,
            agent_y=agent.tile_y,
            tick=self.tick,
            all_agents=all_agents,
            all_objects=all_objects,
            recent_events=recent,
            landmarks=landmarks
        )

    def submit_action(self, action: Action) -> None:
        """Submit an action for execution on next tick."""
        self._action_queue.put(action)

    def move_agent_to(self, agent_id: str, target_x: int, target_y: int) -> bool:
        """
        Start moving an agent to a target position.

        Returns True if path found.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        start = (agent.tile_x, agent.tile_y)
        goal = (target_x, target_y)

        path = self.pathfinder.find_path(start, goal, current_tick=self.tick)

        if path.result == PathResult.SUCCESS:
            agent.current_path = path
            agent.path_index = 0
            return True

        return False

    def get_state_snapshot(self) -> Dict:
        """Get complete state snapshot for frontend."""
        return {
            'tick': self.tick,
            'seed': self.world_seed,
            'agents': {aid: a.to_dict() for aid, a in self.agents.items()},
            'objects': self.objects,
            'recent_events': [e.to_dict() for e in self.recent_events[-20:]],
            'landmarks': [
                {
                    'id': lm.landmark_id,
                    'name': lm.name,
                    'x': lm.tile_x,
                    'y': lm.tile_y,
                    'radius': lm.radius,
                    'type': lm.landmark_type,
                }
                for lm in self.terrain.get_landmarks()
            ]
        }

    def export_to_json(self, output_path: str) -> None:
        """Export current state to JSON file."""
        snapshot = self.get_state_snapshot()
        with open(output_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
