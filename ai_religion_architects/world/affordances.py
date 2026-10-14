"""
Affordance System

Defines actions agents can take and validates their execution.
Actions have preconditions, effects, and outcomes.
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable, Set
from enum import Enum
from datetime import datetime


class ActionType(str, Enum):
    """Types of actions agents can perform."""
    MOVE = "move"
    INSPECT = "inspect"
    GATHER = "gather"
    GIVE = "give"
    REST = "rest"
    CONVERSE = "converse"
    READ = "read"
    WRITE = "write"
    CRAFT = "craft"
    PERFORM_RITUAL = "perform_ritual"
    MEDITATE = "meditate"
    WAIT = "wait"


class ActionResult(str, Enum):
    """Possible outcomes of an action."""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID = "invalid"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


@dataclass
class ActionOutcome:
    """Result of executing an action."""
    result: ActionResult
    action_id: str
    action_type: ActionType
    agent_id: str
    tick: int
    effects: List[Dict[str, Any]] = field(default_factory=list)
    failure_reason: Optional[str] = None
    duration_ticks: int = 0
    event_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'result': self.result.value,
            'action_id': self.action_id,
            'type': self.action_type.value,
            'agent': self.agent_id,
            'tick': self.tick,
            'effects': self.effects,
            'failure_reason': self.failure_reason,
            'duration': self.duration_ticks,
            'events': self.event_ids,
        }


@dataclass
class Action:
    """An action request from an agent."""
    action_id: str
    action_type: ActionType
    agent_id: str
    target_id: Optional[str] = None
    target_position: Optional[tuple] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    requested_at_tick: int = 0

    def to_dict(self) -> Dict:
        return {
            'action_id': self.action_id,
            'type': self.action_type.value,
            'agent': self.agent_id,
            'target_id': self.target_id,
            'target_position': self.target_position,
            'parameters': self.parameters,
            'tick': self.requested_at_tick,
        }


@dataclass
class AffordanceDefinition:
    """Definition of an affordance (possible action type)."""
    action_type: ActionType
    name: str
    description: str
    base_duration: int  # Ticks to complete
    energy_cost: float  # 0.0 to 1.0
    requires_target: bool = False
    requires_position: bool = False
    requires_adjacency: bool = False
    max_range: int = 1
    interruptible: bool = True
    required_object_types: Set[str] = field(default_factory=set)
    required_skills: Set[str] = field(default_factory=set)


# Core affordance definitions
AFFORDANCES: Dict[ActionType, AffordanceDefinition] = {
    ActionType.MOVE: AffordanceDefinition(
        action_type=ActionType.MOVE,
        name="Move",
        description="Move to an adjacent tile",
        base_duration=1,
        energy_cost=0.01,
        requires_position=True,
        requires_adjacency=True,
    ),
    ActionType.INSPECT: AffordanceDefinition(
        action_type=ActionType.INSPECT,
        name="Inspect",
        description="Examine an object or agent closely",
        base_duration=2,
        energy_cost=0.02,
        requires_target=True,
        requires_adjacency=True,
        max_range=2,
    ),
    ActionType.GATHER: AffordanceDefinition(
        action_type=ActionType.GATHER,
        name="Gather",
        description="Collect a resource",
        base_duration=5,
        energy_cost=0.05,
        requires_target=True,
        requires_adjacency=True,
        required_object_types={'resource'},
    ),
    ActionType.GIVE: AffordanceDefinition(
        action_type=ActionType.GIVE,
        name="Give",
        description="Transfer an item to another agent",
        base_duration=1,
        energy_cost=0.01,
        requires_target=True,
        requires_adjacency=True,
    ),
    ActionType.REST: AffordanceDefinition(
        action_type=ActionType.REST,
        name="Rest",
        description="Recover energy",
        base_duration=10,
        energy_cost=-0.2,  # Negative = restore
        interruptible=True,
    ),
    ActionType.CONVERSE: AffordanceDefinition(
        action_type=ActionType.CONVERSE,
        name="Converse",
        description="Start or continue a conversation",
        base_duration=3,  # Per turn
        energy_cost=0.02,
        requires_target=True,
        requires_adjacency=True,
        max_range=3,
    ),
    ActionType.READ: AffordanceDefinition(
        action_type=ActionType.READ,
        name="Read",
        description="Read a text or inscription",
        base_duration=3,
        energy_cost=0.02,
        requires_target=True,
        requires_adjacency=True,
        required_object_types={'text', 'scripture', 'inscription'},
    ),
    ActionType.WRITE: AffordanceDefinition(
        action_type=ActionType.WRITE,
        name="Write",
        description="Create a written record",
        base_duration=10,
        energy_cost=0.08,
        requires_target=True,
        requires_adjacency=True,
        required_object_types={'scriptorium', 'writing_surface'},
    ),
    ActionType.CRAFT: AffordanceDefinition(
        action_type=ActionType.CRAFT,
        name="Craft",
        description="Create an artifact",
        base_duration=15,
        energy_cost=0.15,
        requires_target=True,
        requires_adjacency=True,
        required_object_types={'workshop', 'forge'},
        required_skills={'crafting'},
    ),
    ActionType.PERFORM_RITUAL: AffordanceDefinition(
        action_type=ActionType.PERFORM_RITUAL,
        name="Perform Ritual",
        description="Execute a sacred ritual",
        base_duration=20,
        energy_cost=0.2,
        requires_target=True,
        requires_adjacency=True,
        required_object_types={'ritual_site', 'altar'},
    ),
    ActionType.MEDITATE: AffordanceDefinition(
        action_type=ActionType.MEDITATE,
        name="Meditate",
        description="Deep reflection and contemplation",
        base_duration=8,
        energy_cost=-0.1,  # Restores some energy
        interruptible=True,
    ),
    ActionType.WAIT: AffordanceDefinition(
        action_type=ActionType.WAIT,
        name="Wait",
        description="Do nothing for a tick",
        base_duration=1,
        energy_cost=0.0,
    ),
}


class AffordanceRegistry:
    """
    Registry and validator for affordances.

    Validates action preconditions and executes effects.
    """

    def __init__(self):
        self.affordances = AFFORDANCES.copy()

        # Custom validators by action type
        self._validators: Dict[ActionType, Callable] = {}

        # Custom executors by action type
        self._executors: Dict[ActionType, Callable] = {}

    def get_affordance(self, action_type: ActionType) -> Optional[AffordanceDefinition]:
        """Get affordance definition by type."""
        return self.affordances.get(action_type)

    def get_available_actions(
        self,
        agent_id: str,
        agent_position: tuple,
        agent_energy: float,
        agent_skills: Set[str],
        nearby_agents: List[Dict],
        nearby_objects: List[Dict],
        agent_inventory: List[Dict]
    ) -> List[Dict]:
        """
        Get list of currently available actions for an agent.

        Returns list of action templates with valid targets.
        """
        available = []

        for action_type, definition in self.affordances.items():
            # Check energy
            if definition.energy_cost > 0 and agent_energy < definition.energy_cost:
                continue

            # Check skills
            if definition.required_skills and not definition.required_skills.issubset(agent_skills):
                continue

            action_info = {
                'type': action_type.value,
                'name': definition.name,
                'description': definition.description,
                'duration': definition.base_duration,
                'energy_cost': definition.energy_cost,
                'targets': [],
            }

            # Find valid targets
            if definition.requires_target:
                # Check nearby agents as targets
                for agent in nearby_agents:
                    if self._is_valid_target(definition, agent, agent_position, 'agent'):
                        action_info['targets'].append({
                            'target_type': 'agent',
                            'target_id': agent['agent_id'],
                            'name': agent.get('chosen_name', agent['agent_id']),
                        })

                # Check nearby objects as targets
                for obj in nearby_objects:
                    if self._is_valid_target(definition, obj, agent_position, 'object'):
                        action_info['targets'].append({
                            'target_type': 'object',
                            'target_id': obj['object_id'],
                            'name': obj.get('name', obj['object_type']),
                        })

                # Only include if has valid targets
                if action_info['targets'] or not definition.requires_target:
                    available.append(action_info)
            else:
                # No target required
                if definition.requires_position:
                    # Movement - find valid adjacent tiles
                    directions = ['north', 'east', 'south', 'west']
                    action_info['targets'] = directions
                available.append(action_info)

        return available

    def _is_valid_target(
        self,
        definition: AffordanceDefinition,
        target: Dict,
        agent_position: tuple,
        target_type: str
    ) -> bool:
        """Check if a target is valid for an affordance."""
        # Get target position
        target_pos = (target.get('tile_x', 0), target.get('tile_y', 0))

        # Check range
        dx = abs(target_pos[0] - agent_position[0])
        dy = abs(target_pos[1] - agent_position[1])
        distance = dx + dy  # Manhattan distance

        if definition.requires_adjacency and distance > 1:
            return False
        if distance > definition.max_range:
            return False

        # Check object type requirements
        if definition.required_object_types and target_type == 'object':
            obj_type = target.get('object_type', '')
            if obj_type not in definition.required_object_types:
                return False

        return True

    def validate_action(
        self,
        action: Action,
        agent_state: Dict,
        world_state: Dict
    ) -> tuple[bool, Optional[str]]:
        """
        Validate an action before execution.

        Args:
            action: The action to validate
            agent_state: Current state of the agent
            world_state: Current state of relevant world data

        Returns:
            (is_valid, error_message)
        """
        definition = self.affordances.get(action.action_type)
        if not definition:
            return False, f"Unknown action type: {action.action_type}"

        # Check energy
        agent_energy = agent_state.get('energy', 0.0)
        if definition.energy_cost > 0 and agent_energy < definition.energy_cost:
            return False, "Insufficient energy"

        # Check target requirements
        if definition.requires_target and not action.target_id:
            return False, "Action requires a target"

        if definition.requires_position and not action.target_position:
            return False, "Action requires a position"

        # Check adjacency if required
        if definition.requires_adjacency and action.target_position:
            agent_pos = (agent_state['tile_x'], agent_state['tile_y'])
            target_pos = action.target_position
            dx = abs(target_pos[0] - agent_pos[0])
            dy = abs(target_pos[1] - agent_pos[1])
            if dx + dy > 1:
                return False, "Target not adjacent"

        # Check range
        if action.target_position:
            agent_pos = (agent_state['tile_x'], agent_state['tile_y'])
            target_pos = action.target_position
            dx = abs(target_pos[0] - agent_pos[0])
            dy = abs(target_pos[1] - agent_pos[1])
            if dx + dy > definition.max_range:
                return False, f"Target out of range (max {definition.max_range})"

        # Check object type requirements for object targets
        if definition.required_object_types and action.target_id:
            target_obj = world_state.get('objects', {}).get(action.target_id)
            if target_obj:
                if target_obj.get('object_type') not in definition.required_object_types:
                    return False, f"Invalid target type for {action.action_type.value}"

        # Check skill requirements
        if definition.required_skills:
            agent_skills = set(agent_state.get('skills', []))
            missing = definition.required_skills - agent_skills
            if missing:
                return False, f"Missing skills: {missing}"

        # Run custom validator if registered
        if action.action_type in self._validators:
            validator = self._validators[action.action_type]
            is_valid, error = validator(action, agent_state, world_state)
            if not is_valid:
                return False, error

        return True, None

    def create_action(
        self,
        action_type: ActionType,
        agent_id: str,
        tick: int,
        target_id: Optional[str] = None,
        target_position: Optional[tuple] = None,
        **parameters
    ) -> Action:
        """Create a new action request."""
        return Action(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            agent_id=agent_id,
            target_id=target_id,
            target_position=target_position,
            parameters=parameters,
            requested_at_tick=tick
        )

    def get_duration(self, action_type: ActionType) -> int:
        """Get base duration for an action type."""
        definition = self.affordances.get(action_type)
        return definition.base_duration if definition else 1

    def get_energy_cost(self, action_type: ActionType) -> float:
        """Get energy cost for an action type."""
        definition = self.affordances.get(action_type)
        return definition.energy_cost if definition else 0.0

    def register_validator(
        self,
        action_type: ActionType,
        validator: Callable[[Action, Dict, Dict], tuple[bool, Optional[str]]]
    ) -> None:
        """Register a custom validator for an action type."""
        self._validators[action_type] = validator

    def register_executor(
        self,
        action_type: ActionType,
        executor: Callable[[Action, Dict, Dict], ActionOutcome]
    ) -> None:
        """Register a custom executor for an action type."""
        self._executors[action_type] = executor
