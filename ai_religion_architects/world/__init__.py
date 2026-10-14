"""
World System for AI Religion Architects

This module implements a persistent spatial world where agents physically inhabit
the environment, pursue goals, interact with objects, develop relationships,
and create culture through their actions.

Core components:
- simulation: Main world tick engine
- terrain: World generation and tile management
- pathfinding: A* navigation
- perception: Agent observation system
- affordances: Action validation and execution
- debate_adapter: Bridge between world and debate systems
- research: Experiment runner and analysis tools
"""

from .simulation import WorldSimulation
from .terrain import TerrainGenerator, TileType
from .pathfinding import Pathfinder
from .perception import PerceptionSystem
from .affordances import AffordanceRegistry, Action, ActionResult
from .debate_adapter import WorldDebateAdapter, DebateContext, WorldEffect
from .export import export_all

__all__ = [
    'WorldSimulation',
    'TerrainGenerator',
    'TileType',
    'Pathfinder',
    'PerceptionSystem',
    'AffordanceRegistry',
    'Action',
    'ActionResult',
    'WorldDebateAdapter',
    'DebateContext',
    'WorldEffect',
    'export_all',
]
