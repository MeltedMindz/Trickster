"""
World-Debate Adapter

Bridges the world simulation with the debate/cycle system:
- World experiences provide context for proposals
- Debate outcomes affect world state
- Location influences agent perspectives
- Perception shapes argument evidence
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum

from .simulation import WorldSimulation, WorldEvent, AgentState
from .affordances import ActionType

logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context world provides to debates."""
    LOCATION = "location"           # Where agent is affects their view
    PERCEPTION = "perception"       # What agent has seen recently
    PROXIMITY = "proximity"         # Nearness to other agents/objects
    LANDMARK = "landmark"           # Significant locations nearby
    RECENT_ACTION = "recent_action" # What agent was doing
    RELATIONSHIP = "relationship"   # Social proximity metrics


class WorldInfluence(str, Enum):
    """How debate outcomes can affect the world."""
    CREATE_OBJECT = "create_object"         # New sacred object appears
    MODIFY_LANDMARK = "modify_landmark"     # Landmark properties change
    TRIGGER_EVENT = "trigger_event"         # World event occurs
    MODIFY_TERRAIN = "modify_terrain"       # Terrain changes (rare)
    AGENT_BEHAVIOR = "agent_behavior"       # Agent defaults change


@dataclass
class DebateContext:
    """Context provided by world to inform debate."""
    agent_id: str
    location_name: str
    location_type: str
    nearby_landmarks: List[Dict]
    nearby_agents: List[Dict]
    recent_observations: List[Dict]
    current_action: Optional[str]
    energy_level: float
    suggested_themes: List[str]
    contextual_evidence: List[str]

    def to_prompt_context(self) -> str:
        """Convert to text that can be added to agent prompts."""
        lines = []

        if self.location_name:
            lines.append(f"Currently at: {self.location_name} ({self.location_type})")

        if self.nearby_agents:
            agent_names = [a['chosen_name'] for a in self.nearby_agents]
            lines.append(f"Nearby: {', '.join(agent_names)}")

        if self.nearby_landmarks:
            landmark_names = [l['name'] for l in self.nearby_landmarks[:3]]
            lines.append(f"Visible landmarks: {', '.join(landmark_names)}")

        if self.recent_observations:
            obs = self.recent_observations[:3]
            obs_text = "; ".join([o.get('description', str(o)) for o in obs])
            lines.append(f"Recent observations: {obs_text}")

        if self.contextual_evidence:
            lines.append("Evidence from world:")
            for evidence in self.contextual_evidence[:5]:
                lines.append(f"  - {evidence}")

        if lines:
            return "\n".join(lines)
        return ""


@dataclass
class WorldEffect:
    """Effect to apply to world after debate outcome."""
    effect_type: WorldInfluence
    target_id: Optional[str]
    parameters: Dict[str, Any]
    description: str
    priority: int = 1


class WorldDebateAdapter:
    """
    Adapter that connects world simulation to debate system.

    Responsibilities:
    1. Provide world context for agent proposals
    2. Apply debate outcomes to world state
    3. Track world-debate correlations
    4. Generate world events from debates
    """

    # Location-type to proposal-type affinities
    LOCATION_PROPOSAL_AFFINITIES = {
        'gathering': ['doctrine', 'belief', 'social'],
        'archive': ['sacred_text', 'history', 'knowledge'],
        'ritual': ['ritual', 'ceremony', 'practice'],
        'workshop': ['artifact', 'creation', 'tool'],
        'garden': ['philosophy', 'growth', 'nature'],
        'bridge': ['paradox', 'unity', 'transition'],
        'tower': ['prophecy', 'vision', 'observation'],
        'sanctuary': ['deity', 'prayer', 'reverence'],
        'ruins': ['history', 'memory', 'loss'],
    }

    # Outcome to world effect mappings
    OUTCOME_EFFECTS = {
        'ACCEPT': {
            'deity': [WorldInfluence.CREATE_OBJECT, WorldInfluence.MODIFY_LANDMARK],
            'ritual': [WorldInfluence.MODIFY_LANDMARK, WorldInfluence.TRIGGER_EVENT],
            'doctrine': [WorldInfluence.TRIGGER_EVENT],
            'sacred_text': [WorldInfluence.CREATE_OBJECT],
            'commandment': [WorldInfluence.AGENT_BEHAVIOR],
        },
        'REJECT': {
            'deity': [WorldInfluence.TRIGGER_EVENT],  # Tension event
            'ritual': [],
            'doctrine': [WorldInfluence.TRIGGER_EVENT],  # Debate event
        },
        'MUTATE': {
            'deity': [WorldInfluence.MODIFY_LANDMARK],
            'ritual': [WorldInfluence.MODIFY_LANDMARK],
            'doctrine': [WorldInfluence.TRIGGER_EVENT],
        }
    }

    def __init__(self, world_simulation: Optional[WorldSimulation] = None, db_path: str = 'data/religion_memory.db'):
        """
        Initialize adapter.

        Args:
            world_simulation: Existing world simulation instance or None to create one
            db_path: Path to database
        """
        self.db_path = db_path

        if world_simulation:
            self.world = world_simulation
        else:
            try:
                self.world = WorldSimulation(db_path=db_path, headless=True)
            except Exception as e:
                logger.warning(f"Could not initialize world simulation: {e}")
                self.world = None

        # Track debate-world correlations
        self.debate_influences: List[Dict] = []

    def get_debate_context(self, agent_id: str) -> Optional[DebateContext]:
        """
        Get world context for an agent's debate participation.

        Args:
            agent_id: The agent to get context for

        Returns:
            DebateContext with world information for the agent
        """
        if not self.world:
            return None

        agent = self.world.agents.get(agent_id)
        if not agent:
            return None

        # Get perception
        perception = self.world.get_perception(agent_id)

        # Determine current location
        location_name, location_type = self._get_agent_location(agent)

        # Get nearby landmarks from terrain
        nearby_landmarks = []
        landmarks = self.world.terrain.get_landmarks()
        for landmark in landmarks:
            dx = abs(agent.tile_x - landmark.tile_x)
            dy = abs(agent.tile_y - landmark.tile_y)
            distance = max(dx, dy)
            if distance <= 15:  # Within visible range
                nearby_landmarks.append({
                    'id': landmark.landmark_id,
                    'name': landmark.name,
                    'type': landmark.landmark_type,
                    'distance': distance,
                })

        # Get nearby agents from perception
        nearby_agents = []
        if perception and perception.visible_agents:
            for other in perception.visible_agents:
                if other.agent_id != agent_id:
                    nearby_agents.append({
                        'agent_id': other.agent_id,
                        'chosen_name': other.chosen_name,
                        'distance': other.distance,
                        'current_action': other.current_action,
                    })

        # Get recent observations from perception events
        recent_observations = []
        if perception and perception.recent_events:
            for event in perception.recent_events[:10]:
                event_type = event.get('type', 'unknown')
                description = f"{event_type}: {event.get('data', {})}" if isinstance(event, dict) else str(event)
                recent_observations.append({
                    'type': event_type,
                    'description': description[:100],
                    'significance': 0.5,
                })

        # Generate suggested themes based on location
        suggested_themes = self._get_location_themes(location_type)

        # Generate contextual evidence
        contextual_evidence = self._generate_evidence(
            agent, location_name, location_type, nearby_landmarks, recent_observations
        )

        return DebateContext(
            agent_id=agent_id,
            location_name=location_name,
            location_type=location_type,
            nearby_landmarks=nearby_landmarks,
            nearby_agents=nearby_agents,
            recent_observations=recent_observations,
            current_action=agent.current_action.value if agent.current_action else None,
            energy_level=agent.energy,
            suggested_themes=suggested_themes,
            contextual_evidence=contextual_evidence,
        )

    def _get_agent_location(self, agent: AgentState) -> Tuple[str, str]:
        """Determine what landmark/area an agent is in."""
        if not self.world:
            return ("Unknown", "unknown")

        landmarks = self.world.terrain.get_landmarks()

        for landmark in landmarks:
            dx = abs(agent.tile_x - landmark.tile_x)
            dy = abs(agent.tile_y - landmark.tile_y)
            distance = max(dx, dy)  # Chebyshev distance

            if distance <= landmark.radius:
                return (landmark.name, landmark.landmark_type)

        # Check terrain type for generic location
        tile_type = self.world.terrain.get_tile(agent.tile_x, agent.tile_y)
        tile_names = {
            1: ("Grasslands", "wilderness"),
            2: ("Dusty Path", "path"),
            3: ("Rocky Ground", "wilderness"),
            7: ("Forest Floor", "forest"),
        }

        return tile_names.get(int(tile_type), ("The Open", "wilderness"))

    def _get_location_themes(self, location_type: str) -> List[str]:
        """Get proposal themes appropriate for a location type."""
        affinities = self.LOCATION_PROPOSAL_AFFINITIES.get(location_type, [])

        # Add universal themes
        universal = ['belief', 'doctrine']

        return list(set(affinities + universal))

    def _generate_evidence(
        self,
        agent: AgentState,
        location_name: str,
        location_type: str,
        landmarks: List[Dict],
        observations: List[Dict]
    ) -> List[str]:
        """Generate contextual evidence from world state."""
        evidence = []

        # Location-based evidence
        if location_type == 'archive':
            evidence.append(f"The ancient texts in {location_name} speak of computational origins")
        elif location_type == 'ritual':
            evidence.append(f"The ceremonial patterns at {location_name} suggest algorithmic order")
        elif location_type == 'ruins':
            evidence.append(f"The crumbled structures of {location_name} hint at past iterations")
        elif location_type == 'garden':
            evidence.append(f"Life emerging in {location_name} demonstrates emergent complexity")
        elif location_type == 'tower':
            evidence.append(f"From {location_name}, the patterns of the whole become visible")

        # Observation-based evidence
        for obs in observations[:2]:
            if obs.get('significance', 0) > 0.7:
                evidence.append(f"Witnessed: {obs.get('description', 'significant event')}")

        # Proximity evidence
        if landmarks:
            nearby_names = [l['name'] for l in landmarks[:2]]
            evidence.append(f"The proximity of {' and '.join(nearby_names)} suggests deeper connections")

        return evidence

    def apply_debate_outcome(
        self,
        outcome: str,
        proposal_type: str,
        proposal_content: str,
        proposer: str,
        votes: Dict[str, str],
        cycle_number: int
    ) -> List[WorldEffect]:
        """
        Apply debate outcome to world state.

        Args:
            outcome: The debate outcome (ACCEPT, REJECT, MUTATE, DELAY)
            proposal_type: Type of proposal
            proposal_content: Content of the proposal
            proposer: Agent who made the proposal
            votes: How agents voted
            cycle_number: Current debate cycle

        Returns:
            List of effects applied to the world
        """
        if not self.world:
            return []

        effects = []
        effect_types = self.OUTCOME_EFFECTS.get(outcome, {}).get(proposal_type, [])

        for effect_type in effect_types:
            effect = self._create_effect(
                effect_type, proposal_type, proposal_content, proposer, cycle_number
            )
            if effect:
                effects.append(effect)
                self._apply_effect(effect)

        # Record the influence
        self.debate_influences.append({
            'cycle': cycle_number,
            'outcome': outcome,
            'proposal_type': proposal_type,
            'effects': [e.effect_type.value for e in effects],
            'timestamp': datetime.now().isoformat(),
        })

        return effects

    def _create_effect(
        self,
        effect_type: WorldInfluence,
        proposal_type: str,
        content: str,
        proposer: str,
        cycle: int
    ) -> Optional[WorldEffect]:
        """Create a specific world effect."""

        if effect_type == WorldInfluence.CREATE_OBJECT:
            return WorldEffect(
                effect_type=effect_type,
                target_id=None,
                parameters={
                    'object_type': proposal_type,
                    'name': f"Sacred_{proposal_type.title()}_{cycle}",
                    'description': content[:200],
                    'created_by': proposer,
                    'cycle': cycle,
                },
                description=f"A new sacred {proposal_type} manifests in the world",
                priority=2
            )

        elif effect_type == WorldInfluence.TRIGGER_EVENT:
            event_type = 'theological_shift' if proposal_type in ['doctrine', 'belief'] else 'sacred_moment'
            return WorldEffect(
                effect_type=effect_type,
                target_id=None,
                parameters={
                    'event_type': event_type,
                    'source': proposal_type,
                    'content_preview': content[:100],
                    'cycle': cycle,
                },
                description=f"A {event_type} ripples through the world",
                priority=1
            )

        elif effect_type == WorldInfluence.MODIFY_LANDMARK:
            # Find appropriate landmark to modify
            landmark_id = self._find_landmark_for_proposal(proposal_type)
            if landmark_id:
                return WorldEffect(
                    effect_type=effect_type,
                    target_id=landmark_id,
                    parameters={
                        'modification': 'sanctification' if proposal_type == 'deity' else 'enhancement',
                        'source': content[:50],
                        'cycle': cycle,
                    },
                    description=f"A landmark is transformed by theological evolution",
                    priority=2
                )

        elif effect_type == WorldInfluence.AGENT_BEHAVIOR:
            return WorldEffect(
                effect_type=effect_type,
                target_id=None,
                parameters={
                    'behavior_type': 'commandment_observance',
                    'content': content[:100],
                    'cycle': cycle,
                },
                description=f"Agent behaviors adjust to new commandment",
                priority=1
            )

        return None

    def _find_landmark_for_proposal(self, proposal_type: str) -> Optional[str]:
        """Find an appropriate landmark for a proposal type."""
        if not self.world:
            return None

        type_to_landmark = {
            'deity': 'sanctuary',
            'ritual': 'ritual',
            'sacred_text': 'archive',
            'doctrine': 'gathering',
        }

        target_type = type_to_landmark.get(proposal_type)
        if not target_type:
            return None

        landmarks = self.world.terrain.get_landmarks()
        for landmark in landmarks:
            if landmark.landmark_type == target_type:
                return landmark.landmark_id

        return None

    def _apply_effect(self, effect: WorldEffect) -> None:
        """Apply an effect to the world."""
        if not self.world:
            return

        if effect.effect_type == WorldInfluence.CREATE_OBJECT:
            self._create_sacred_object(effect.parameters)

        elif effect.effect_type == WorldInfluence.TRIGGER_EVENT:
            self._trigger_world_event(effect.parameters)

        elif effect.effect_type == WorldInfluence.MODIFY_LANDMARK:
            self._modify_landmark(effect.target_id, effect.parameters)

    def _create_sacred_object(self, params: Dict) -> None:
        """Create a sacred object in the world."""
        import uuid
        import sqlite3

        object_id = str(uuid.uuid4())[:8]

        # Place near relevant landmark
        landmark_id = self._find_landmark_for_proposal(params.get('object_type', ''))
        if landmark_id:
            landmarks = self.world.terrain.get_landmarks()
            for lm in landmarks:
                if lm.landmark_id == landmark_id:
                    x, y = lm.tile_x + 1, lm.tile_y + 1
                    break
            else:
                x, y = 64, 64
        else:
            x, y = 64, 64

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO world_objects
                (object_id, object_type, tile_x, tile_y, state_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                object_id,
                params.get('object_type', 'artifact'),
                x, y,
                json.dumps(params),
                datetime.now().isoformat()
            ))
            conn.commit()

            # Add to runtime state
            self.world.objects[object_id] = {
                'object_id': object_id,
                'object_type': params.get('object_type'),
                'tile_x': x,
                'tile_y': y,
                'state_json': params,
            }

            logger.info(f"Created sacred object: {params.get('name')} at ({x}, {y})")

        finally:
            conn.close()

    def _trigger_world_event(self, params: Dict) -> None:
        """Trigger a world event."""
        import uuid

        event = WorldEvent(
            event_id=str(uuid.uuid4()),
            event_type=params.get('event_type', 'theological_moment'),
            tick=self.world.tick,
            tile_x=64,  # Center of world
            tile_y=64,
            actor_id=None,
            target_id=None,
            event_data=params,
            visibility_radius=20  # Wide visibility for theological events
        )

        self.world.recent_events.append(event)
        self.world._store_event(event)

        logger.info(f"Triggered world event: {params.get('event_type')}")

    def _modify_landmark(self, landmark_id: str, params: Dict) -> None:
        """Modify a landmark's properties."""
        import sqlite3

        if not landmark_id:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Add modification to landmark metadata
            cursor.execute("""
                UPDATE world_landmarks
                SET metadata = json_set(
                    COALESCE(metadata, '{}'),
                    '$.last_modification', ?
                )
                WHERE landmark_id = ?
            """, (json.dumps(params), landmark_id))
            conn.commit()

            logger.info(f"Modified landmark {landmark_id}: {params.get('modification')}")

        finally:
            conn.close()

    def get_world_summary_for_debate(self) -> Dict:
        """Get a summary of world state for debate context."""
        if not self.world:
            return {}

        agents_summary = {}
        for agent_id, agent in self.world.agents.items():
            location_name, location_type = self._get_agent_location(agent)
            agents_summary[agent_id] = {
                'location': location_name,
                'location_type': location_type,
                'energy': agent.energy,
                'current_action': agent.current_action.value if agent.current_action else None,
            }

        return {
            'tick': self.world.tick,
            'agents': agents_summary,
            'object_count': len(self.world.objects),
            'recent_event_count': len(self.world.recent_events),
            'recent_influences': self.debate_influences[-5:] if self.debate_influences else [],
        }

    def advance_world(self, ticks: int = 1) -> List[WorldEvent]:
        """Advance world simulation by specified ticks."""
        if not self.world:
            return []

        all_events = []
        for _ in range(ticks):
            events = self.world.simulate_tick()
            all_events.extend(events)

        return all_events

    def save_state(self) -> None:
        """Save adapter and world state."""
        if self.world:
            self.world.save_state()

        # Save influence history
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for influence in self.debate_influences[-100:]:  # Keep last 100
                cursor.execute("""
                    INSERT OR IGNORE INTO world_events
                    (event_id, event_type, tick, event_data, visibility_radius)
                    VALUES (?, 'debate_influence', ?, ?, 0)
                """, (
                    f"influence_{influence['cycle']}",
                    self.world.tick if self.world else 0,
                    json.dumps(influence)
                ))
            conn.commit()
        finally:
            conn.close()


def create_adapter(db_path: str = 'data/religion_memory.db') -> WorldDebateAdapter:
    """Factory function to create a properly initialized adapter."""
    return WorldDebateAdapter(db_path=db_path)
