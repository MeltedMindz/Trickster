"""Extended schemas for meta-cognitive abilities and cultural depth"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class SelfReflection:
    """Agent's self-analysis of their behavior"""
    cycle: int
    insights: List[str]
    voting_pattern_analysis: str
    strategy_effectiveness: Dict[str, float]
    belief_consistency_score: float
    personality_drift: Dict[str, float]  # Trait changes recognized
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DebateStrategy:
    """Learned debate tactics"""
    name: str
    description: str
    success_rate: float
    usage_count: int
    discovered_cycle: int
    last_used_cycle: int
    effectiveness_by_agent: Dict[str, float]  # How well it works on each agent


@dataclass
class BeliefJustification:
    """Logical justification tree for beliefs"""
    belief: str
    confidence: float
    supporting_evidence: List[str]
    logical_chain: List[str]  # Step by step reasoning
    dependent_beliefs: List[str]  # What relies on this
    challenges_survived: int
    foundational: bool  # Core belief or derived


@dataclass
class Counterfactual:
    """Alternative history reasoning"""
    cycle: int
    actual_outcome: str
    alternative_outcome: str
    projected_consequences: List[str]
    probability_assessment: float
    learned_lesson: str


@dataclass
class MetaTheory:
    """Agent's theory about religion itself"""
    theory_name: str
    description: str
    supporting_observations: List[str]
    predictions: List[str]
    confidence: float
    formulated_cycle: int


@dataclass
class SacredTerm:
    """Theological terminology"""
    term: str
    definition: str
    etymology: str  # How it was formed
    proposed_by: str
    adopted_cycle: int
    usage_count: int
    related_concepts: List[str]


@dataclass
class ReligiousSymbol:
    """Sacred iconography"""
    name: str
    description: str  # Visual description
    meaning: str  # Theological significance
    associated_concepts: List[str]
    proposed_by: str
    adopted_cycle: int
    usage_contexts: List[str]


@dataclass
class SacredHoliday:
    """Religious observances"""
    name: str
    description: str
    commemorates: str  # What event/concept
    cycle_established: int
    observance_cycles: List[int]  # When it occurs
    rituals: List[str]  # Associated practices
    significance_score: float


@dataclass
class TheologicalTension:
    """Potential schism tracking"""
    tension_id: str
    conflicting_doctrines: List[Tuple[str, str]]
    agent_positions: Dict[str, str]  # Agent -> position
    tension_score: float  # 0-1, likelihood of schism
    cycles_unresolved: int
    resolution_attempts: List[Dict]


@dataclass
class Prophecy:
    """Theological predictions"""
    prophecy_id: str
    prophet: str  # Which agent
    prediction: str
    target_cycle: int  # When it should occur
    created_cycle: int
    confidence: float
    fulfillment_status: str  # pending/fulfilled/failed
    related_doctrines: List[str]