"""
Perception System

Handles what agents can observe based on:
- Distance and line of sight
- Terrain effects (forest reduces vision)
- Time of day (optional)
- Agent-specific perception traits
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set, Any
from datetime import datetime
from enum import Enum


class ObservationType(Enum):
    """Types of observations agents can make."""
    DIRECT = "direct"           # Saw it happen
    HEARSAY = "hearsay"         # Told by another agent
    INFERENCE = "inference"     # Deduced from evidence
    MEMORY = "memory"           # Recalled from past


@dataclass
class Observation:
    """A single observation made by an agent."""
    observation_id: str
    agent_id: str
    observation_type: ObservationType
    content: Dict[str, Any]
    tile_x: int
    tile_y: int
    confidence: float = 1.0
    source_agent_id: Optional[str] = None
    event_id: Optional[str] = None
    observed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            'observation_id': self.observation_id,
            'agent_id': self.agent_id,
            'type': self.observation_type.value,
            'content': self.content,
            'position': {'x': self.tile_x, 'y': self.tile_y},
            'confidence': self.confidence,
            'source': self.source_agent_id,
            'event_id': self.event_id,
        }


@dataclass
class AgentView:
    """What an agent can see about another agent."""
    agent_id: str
    chosen_name: str
    tile_x: int
    tile_y: int
    facing: str
    current_action: Optional[str]
    action_target: Optional[str]
    distance: float

    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'name': self.chosen_name,
            'position': {'x': self.tile_x, 'y': self.tile_y},
            'facing': self.facing,
            'action': self.current_action,
            'target': self.action_target,
            'distance': self.distance,
        }


@dataclass
class ObjectView:
    """What an agent can see about a world object."""
    object_id: str
    object_type: str
    subtype: Optional[str]
    tile_x: int
    tile_y: int
    visible_state: Dict[str, Any]
    distance: float

    def to_dict(self) -> Dict:
        return {
            'object_id': self.object_id,
            'type': self.object_type,
            'subtype': self.subtype,
            'position': {'x': self.tile_x, 'y': self.tile_y},
            'state': self.visible_state,
            'distance': self.distance,
        }


@dataclass
class PerceptionResult:
    """Complete perception result for an agent."""
    agent_id: str
    position: Tuple[int, int]
    tick: int

    # What is visible
    visible_agents: List[AgentView] = field(default_factory=list)
    visible_objects: List[ObjectView] = field(default_factory=list)
    visible_tiles: Set[Tuple[int, int]] = field(default_factory=set)

    # Recent events in perception range
    recent_events: List[Dict] = field(default_factory=list)

    # Current landmark context
    current_landmark: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'position': {'x': self.position[0], 'y': self.position[1]},
            'tick': self.tick,
            'nearby_agents': [a.to_dict() for a in self.visible_agents],
            'visible_objects': [o.to_dict() for o in self.visible_objects],
            'visible_tile_count': len(self.visible_tiles),
            'recent_events': self.recent_events,
            'landmark': self.current_landmark,
        }


class PerceptionSystem:
    """
    Manages agent perception of the world.

    Agents perceive:
    - Other agents within range
    - Objects within range
    - Events that occurred within range
    - Terrain features

    Perception is affected by:
    - Base perception range (default 8 tiles)
    - Terrain (forest reduces to 5)
    - Line of sight blocking
    - Agent-specific modifiers
    """

    DEFAULT_RANGE = 8
    FOREST_RANGE = 5
    NIGHT_MULTIPLIER = 0.5  # Future: time-based reduction

    def __init__(
        self,
        get_tile: callable,
        blocks_sight: callable,
        line_of_sight: callable
    ):
        """
        Initialize perception system.

        Args:
            get_tile: Function(x, y) -> TileType
            blocks_sight: Function(x, y) -> bool
            line_of_sight: Function(from, to, blocks_sight) -> bool
        """
        self.get_tile = get_tile
        self.blocks_sight = blocks_sight
        self.line_of_sight_check = line_of_sight

        # Agent perception modifiers
        self._agent_modifiers: Dict[str, float] = {
            'Zealot': 1.0,      # Standard perception
            'Skeptic': 1.2,     # Enhanced observation
            'Trickster': 0.9,   # Slightly reduced (distracted by chaos)
        }

    def get_perception_range(self, agent_id: str, x: int, y: int) -> int:
        """Get effective perception range for agent at position."""
        # Base range
        base = self.DEFAULT_RANGE

        # Check if in forest (tile type 7)
        tile = self.get_tile(x, y)
        if tile == 7:  # FOREST_FLOOR
            base = self.FOREST_RANGE

        # Apply agent modifier
        modifier = self._agent_modifiers.get(agent_id, 1.0)
        return int(base * modifier)

    def calculate_visible_tiles(
        self,
        center: Tuple[int, int],
        perception_range: int
    ) -> Set[Tuple[int, int]]:
        """
        Calculate all tiles visible from a center point.

        Uses simple radial visibility with line-of-sight checks.
        """
        visible = set()
        cx, cy = center

        # Check all tiles in square around center
        for dx in range(-perception_range, perception_range + 1):
            for dy in range(-perception_range, perception_range + 1):
                # Distance check (circular range)
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > perception_range:
                    continue

                tx, ty = cx + dx, cy + dy

                # Line of sight check
                if self.line_of_sight_check(center, (tx, ty), self.blocks_sight):
                    visible.add((tx, ty))

        return visible

    def perceive(
        self,
        agent_id: str,
        agent_x: int,
        agent_y: int,
        tick: int,
        all_agents: Dict[str, Dict],
        all_objects: List[Dict],
        recent_events: List[Dict],
        landmarks: List[Dict]
    ) -> PerceptionResult:
        """
        Generate complete perception for an agent.

        Args:
            agent_id: ID of perceiving agent
            agent_x, agent_y: Agent's current position
            tick: Current simulation tick
            all_agents: Dict of agent_id -> {tile_x, tile_y, facing, action, ...}
            all_objects: List of object dicts with position
            recent_events: List of recent world events
            landmarks: List of landmarks

        Returns:
            PerceptionResult with all visible information
        """
        position = (agent_x, agent_y)
        perception_range = self.get_perception_range(agent_id, agent_x, agent_y)

        # Calculate visible tiles
        visible_tiles = self.calculate_visible_tiles(position, perception_range)

        # Find visible agents
        visible_agents = []
        for other_id, other_data in all_agents.items():
            if other_id == agent_id:
                continue

            other_pos = (other_data['tile_x'], other_data['tile_y'])
            if other_pos in visible_tiles:
                dist = math.sqrt(
                    (other_pos[0] - agent_x) ** 2 +
                    (other_pos[1] - agent_y) ** 2
                )
                visible_agents.append(AgentView(
                    agent_id=other_id,
                    chosen_name=other_data.get('chosen_name', other_id),
                    tile_x=other_data['tile_x'],
                    tile_y=other_data['tile_y'],
                    facing=other_data.get('facing', 'south'),
                    current_action=other_data.get('current_action'),
                    action_target=other_data.get('action_target_id'),
                    distance=dist
                ))

        # Sort by distance
        visible_agents.sort(key=lambda a: a.distance)

        # Find visible objects
        visible_objects = []
        for obj in all_objects:
            obj_pos = (obj['tile_x'], obj['tile_y'])
            if obj_pos in visible_tiles:
                dist = math.sqrt(
                    (obj_pos[0] - agent_x) ** 2 +
                    (obj_pos[1] - agent_y) ** 2
                )
                # Filter visible state (don't expose hidden properties)
                visible_state = self._filter_object_state(obj.get('state_json', {}))
                visible_objects.append(ObjectView(
                    object_id=obj['object_id'],
                    object_type=obj['object_type'],
                    subtype=obj.get('subtype'),
                    tile_x=obj['tile_x'],
                    tile_y=obj['tile_y'],
                    visible_state=visible_state,
                    distance=dist
                ))

        visible_objects.sort(key=lambda o: o.distance)

        # Filter recent events by visibility
        visible_events = []
        for event in recent_events:
            event_pos = (event.get('tile_x'), event.get('tile_y'))
            if event_pos[0] is None:
                # Non-spatial event, include if recent
                visible_events.append(event)
            elif event_pos in visible_tiles:
                visible_events.append(event)

        # Limit events
        visible_events = visible_events[:20]

        # Find current landmark
        current_landmark = None
        for lm in landmarks:
            lm_pos = (lm['tile_x'], lm['tile_y'])
            dist = math.sqrt(
                (lm_pos[0] - agent_x) ** 2 +
                (lm_pos[1] - agent_y) ** 2
            )
            if dist <= lm['radius']:
                current_landmark = lm['name']
                break

        return PerceptionResult(
            agent_id=agent_id,
            position=position,
            tick=tick,
            visible_agents=visible_agents,
            visible_objects=visible_objects,
            visible_tiles=visible_tiles,
            recent_events=visible_events,
            current_landmark=current_landmark
        )

    def _filter_object_state(self, state: Dict) -> Dict:
        """Filter object state to only visible properties."""
        if not state:
            return {}

        # Hide internal properties
        hidden_keys = {'internal_', 'hidden_', '_secret'}
        return {
            k: v for k, v in state.items()
            if not any(k.startswith(h) for h in hidden_keys)
        }

    def can_see_agent(
        self,
        observer_id: str,
        observer_x: int,
        observer_y: int,
        target_x: int,
        target_y: int
    ) -> bool:
        """Check if observer can see a target position."""
        perception_range = self.get_perception_range(observer_id, observer_x, observer_y)
        dist = math.sqrt((target_x - observer_x) ** 2 + (target_y - observer_y) ** 2)

        if dist > perception_range:
            return False

        return self.line_of_sight_check(
            (observer_x, observer_y),
            (target_x, target_y),
            self.blocks_sight
        )

    def get_nearby_agents(
        self,
        agent_id: str,
        agent_x: int,
        agent_y: int,
        all_agents: Dict[str, Dict],
        max_range: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """Get list of (agent_id, distance) for nearby agents."""
        if max_range is None:
            max_range = self.get_perception_range(agent_id, agent_x, agent_y)

        nearby = []
        for other_id, other_data in all_agents.items():
            if other_id == agent_id:
                continue

            dist = math.sqrt(
                (other_data['tile_x'] - agent_x) ** 2 +
                (other_data['tile_y'] - agent_y) ** 2
            )

            if dist <= max_range:
                if self.can_see_agent(
                    agent_id, agent_x, agent_y,
                    other_data['tile_x'], other_data['tile_y']
                ):
                    nearby.append((other_id, dist))

        nearby.sort(key=lambda x: x[1])
        return nearby

    def create_observation(
        self,
        agent_id: str,
        observation_type: ObservationType,
        content: Dict[str, Any],
        tile_x: int,
        tile_y: int,
        confidence: float = 1.0,
        source_agent_id: Optional[str] = None,
        event_id: Optional[str] = None
    ) -> Observation:
        """Create a new observation record."""
        import uuid
        return Observation(
            observation_id=str(uuid.uuid4()),
            agent_id=agent_id,
            observation_type=observation_type,
            content=content,
            tile_x=tile_x,
            tile_y=tile_y,
            confidence=confidence,
            source_agent_id=source_agent_id,
            event_id=event_id,
            observed_at=datetime.now()
        )

    def hearsay_confidence_decay(
        self,
        original_confidence: float,
        transmission_count: int
    ) -> float:
        """Calculate confidence decay for hearsay information."""
        # Each transmission reduces confidence by 20%
        decay = 0.8 ** transmission_count
        return original_confidence * decay
