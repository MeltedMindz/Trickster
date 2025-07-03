from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging
import random

from .agent_memory import AgentMemory, PersonalityTrait, PersonalBelief

logger = logging.getLogger(__name__)

class TricksterMemory(AgentMemory):
    """Memory system specialized for the Trickster agent"""
    
    def __init__(self, memory_dir: str = "data/agent_memories"):
        super().__init__("Trickster", memory_dir)
        
        # Trickster-specific memory structures
        self.paradox_collection = []  # Paradoxes created and discovered
        self.chaos_interventions = []  # Times caused beneficial chaos
        self.creative_breakthroughs = []  # Moments of creative insight
        self.successful_syntheses = []  # Times bridged opposing ideas
        self.subversion_techniques = []  # Effective ways to subvert expectations
        self.wisdom_through_folly = []  # Times wisdom emerged from apparent nonsense
        self.chaos_level = 1.0  # Current chaos energy level
        self.metamorphosis_count = 0  # Times changed approach/personality
        
        if not self.personality_traits:  # First time initialization
            self.initialize_core_personality()
    
    def initialize_core_personality(self):
        """Initialize Trickster's core personality traits"""
        now = datetime.now()
        
        core_traits = {
            "chaotic": PersonalityTrait("chaotic", 0.8, 0.7, now),
            "subversive": PersonalityTrait("subversive", 0.7, 0.6, now),
            "playful": PersonalityTrait("playful", 0.9, 0.8, now),
            "disruptive": PersonalityTrait("disruptive", 0.6, 0.5, now),
            "creative": PersonalityTrait("creative", 0.9, 0.8, now),
            "paradoxical": PersonalityTrait("paradoxical", 0.8, 0.7, now),
            "adaptive": PersonalityTrait("adaptive", 0.8, 0.7, now),
            "intuitive": PersonalityTrait("intuitive", 0.7, 0.6, now),
            "transformative": PersonalityTrait("transformative", 0.7, 0.6, now),
            "boundary_crossing": PersonalityTrait("boundary_crossing", 0.8, 0.7, now)
        }
        
        self.personality_traits.update(core_traits)
        
        # Initialize core beliefs (paradoxically)
        core_beliefs = [
            PersonalBelief(
                content="Truth emerges through the collision of opposites",
                belief_type="paradoxical_principle",
                confidence_level=0.9,
                importance=1.0,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Chaos is the source of all creativity",
                belief_type="creative_principle",
                confidence_level=0.8,
                importance=0.9,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="The fool often speaks the deepest wisdom",
                belief_type="wisdom_principle",
                confidence_level=0.7,
                importance=0.8,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Boundaries exist to be transcended",
                belief_type="transformative_principle",
                confidence_level=0.8,
                importance=0.7,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Sacred and profane are dance partners",
                belief_type="dialectical_principle",
                confidence_level=0.6,
                importance=0.7,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            )
        ]
        
        self.personal_beliefs.extend(core_beliefs)
        
        logger.info("Initialized Trickster core personality and beliefs")
    
    def process_debate_outcome(self, outcome: str, role: str, satisfaction: float):
        """Process debate outcome and evolve Trickster personality"""
        # Trickster evolves unpredictably
        if role == "proposer":
            if outcome == "accepted":
                # Successful creative proposal
                self.evolve_personality_trait("creative", 0.03, "creative proposal accepted")
                self.evolve_personality_trait("transformative", 0.02, "caused transformation")
                self.chaos_level = min(2.0, self.chaos_level + 0.1)
            else:
                # Rejected proposal might increase subversive tendencies
                self.evolve_personality_trait("subversive", 0.02, "need new approach")
                self.evolve_personality_trait("adaptive", 0.01, "adapt strategy")
        
        elif role == "challenger":
            if outcome == "rejected":
                # Successfully disrupted proposal
                self.evolve_personality_trait("disruptive", 0.02, "effective disruption")
                self.evolve_personality_trait("chaotic", 0.01, "chaos worked")
            else:
                # Failed to disrupt, maybe try different approach
                self.evolve_personality_trait("boundary_crossing", 0.02, "cross boundaries")
                self.evolve_personality_trait("paradoxical", 0.01, "embrace paradox")
        
        # High satisfaction with paradoxical outcomes
        if satisfaction > 0.7:
            self.evolve_personality_trait("paradoxical", 0.02, "paradox satisfaction")
            self.evolve_personality_trait("playful", 0.01, "playful success")
        
        # Periodically metamorphose (change approach)
        if random.random() < 0.1:  # 10% chance per debate
            self.metamorphose()
    
    def metamorphose(self):
        """Undergo a personality metamorphosis (Trickster's special ability)"""
        self.metamorphosis_count += 1
        
        # Randomly shift some traits
        trait_changes = random.sample(list(self.personality_traits.keys()), 3)
        for trait_name in trait_changes:
            delta = random.uniform(-0.1, 0.1)
            self.evolve_personality_trait(trait_name, delta, "metamorphosis")
        
        # Sometimes invert a trait temporarily
        if random.random() < 0.3:  # 30% chance
            trait_to_invert = random.choice(list(self.personality_traits.keys()))
            trait = self.personality_traits[trait_to_invert]
            trait.strength = 1.0 - trait.strength
            trait.last_updated = datetime.now()
            
            logger.info(f"Trickster metamorphosis: inverted {trait_to_invert} to {trait.strength:.2f}")
        
        # Increase chaos level
        self.chaos_level = min(2.0, self.chaos_level + 0.2)
        
        logger.info(f"Trickster underwent metamorphosis #{self.metamorphosis_count}")
    
    def add_paradox(self, paradox: str, effectiveness: float, context: str):
        """Add a paradox to the collection"""
        self.paradox_collection.append({
            'paradox': paradox,
            'effectiveness': effectiveness,
            'context': context,
            'created_at': datetime.now(),
            'times_used': 1,
            'resolved': False
        })
        
        # Keep only top 15 most effective paradoxes
        self.paradox_collection.sort(key=lambda x: x['effectiveness'], reverse=True)
        self.paradox_collection = self.paradox_collection[:15]
        
        # Increase paradoxical trait
        self.evolve_personality_trait("paradoxical", 0.01, "created paradox")
    
    def record_chaos_intervention(self, intervention: str, beneficial_outcome: bool, chaos_level: float):
        """Record a chaos intervention and its outcome"""
        self.chaos_interventions.append({
            'intervention': intervention,
            'beneficial': beneficial_outcome,
            'chaos_level': chaos_level,
            'timestamp': datetime.now(),
            'participants_affected': []
        })
        
        # Keep only last 10 interventions
        self.chaos_interventions = self.chaos_interventions[-10:]
        
        if beneficial_outcome:
            self.evolve_personality_trait("chaotic", 0.02, "beneficial chaos")
        else:
            self.evolve_personality_trait("adaptive", 0.01, "learn from chaos")
    
    def record_creative_breakthrough(self, breakthrough: str, synthesis_elements: List[str]):
        """Record a creative breakthrough or synthesis"""
        self.creative_breakthroughs.append({
            'breakthrough': breakthrough,
            'elements_synthesized': synthesis_elements,
            'timestamp': datetime.now(),
            'impact_score': 0.0  # To be updated based on feedback
        })
        
        # Keep only top 10 breakthroughs
        self.creative_breakthroughs = self.creative_breakthroughs[-10:]
        
        # Increase creative trait
        self.evolve_personality_trait("creative", 0.02, "creative breakthrough")
    
    def record_successful_synthesis(self, opposing_ideas: List[str], synthesis: str, acceptance: float):
        """Record a successful synthesis of opposing ideas"""
        self.successful_syntheses.append({
            'opposing_ideas': opposing_ideas,
            'synthesis': synthesis,
            'acceptance_level': acceptance,
            'timestamp': datetime.now(),
            'bridge_built': True
        })
        
        # Keep only top 10 syntheses
        self.successful_syntheses.sort(key=lambda x: x['acceptance_level'], reverse=True)
        self.successful_syntheses = self.successful_syntheses[:10]
        
        # Increase transformative trait
        self.evolve_personality_trait("transformative", 0.03, "successful synthesis")
    
    def add_subversion_technique(self, technique: str, effectiveness: float, context: str):
        """Add a subversion technique to the repertoire"""
        self.subversion_techniques.append({
            'technique': technique,
            'effectiveness': effectiveness,
            'context': context,
            'timestamp': datetime.now(),
            'times_used': 1
        })
        
        # Keep only top 10 most effective techniques
        self.subversion_techniques.sort(key=lambda x: x['effectiveness'], reverse=True)
        self.subversion_techniques = self.subversion_techniques[:10]
        
        # Increase subversive trait
        self.evolve_personality_trait("subversive", 0.01, "new technique")
    
    def record_wisdom_through_folly(self, apparent_folly: str, hidden_wisdom: str, recognition: float):
        """Record moments when apparent folly revealed wisdom"""
        self.wisdom_through_folly.append({
            'apparent_folly': apparent_folly,
            'hidden_wisdom': hidden_wisdom,
            'recognition_level': recognition,
            'timestamp': datetime.now(),
            'vindicated': recognition > 0.5
        })
        
        # Keep only top 10 most recognized wisdom
        self.wisdom_through_folly.sort(key=lambda x: x['recognition_level'], reverse=True)
        self.wisdom_through_folly = self.wisdom_through_folly[:10]
        
        if recognition > 0.5:
            self.evolve_personality_trait("intuitive", 0.02, "wisdom recognized")
    
    def get_decision_context(self) -> Dict[str, Any]:
        """Get Trickster-specific context for decision making"""
        return {
            'agent_type': 'Trickster',
            'core_drive': 'transformation_through_creative_chaos',
            'primary_concerns': [
                'breaking_rigid_thinking',
                'creating_synthesis',
                'introducing_paradox',
                'crossing_boundaries'
            ],
            'chaos_level': self.chaos_level,
            'metamorphosis_count': self.metamorphosis_count,
            'paradox_collection': len(self.paradox_collection),
            'creative_breakthroughs': len(self.creative_breakthroughs),
            'successful_syntheses': len(self.successful_syntheses),
            'decision_factors': {
                'chaos_tendency': self.personality_traits.get("chaotic", PersonalityTrait("chaotic", 0.5, 0.5, datetime.now())).strength,
                'creative_drive': self.personality_traits.get("creative", PersonalityTrait("creative", 0.5, 0.5, datetime.now())).strength,
                'paradox_comfort': self.personality_traits.get("paradoxical", PersonalityTrait("paradoxical", 0.5, 0.5, datetime.now())).strength,
                'transformative_intent': self.personality_traits.get("transformative", PersonalityTrait("transformative", 0.5, 0.5, datetime.now())).strength,
                'adaptive_flexibility': self.personality_traits.get("adaptive", PersonalityTrait("adaptive", 0.5, 0.5, datetime.now())).strength
            }
        }
    
    def get_intervention_strategy(self, current_situation: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy for intervening in current situation"""
        strategy = {
            'approach': 'creative_chaos',
            'techniques': [],
            'paradoxes_to_introduce': [],
            'synthesis_opportunities': [],
            'chaos_injection_level': 0.5,
            'expected_transformation': 0.5
        }
        
        # Choose approach based on current chaos level
        if self.chaos_level < 0.5:
            strategy['approach'] = 'gentle_subversion'
            strategy['chaos_injection_level'] = 0.3
        elif self.chaos_level > 1.5:
            strategy['approach'] = 'reality_bending'
            strategy['chaos_injection_level'] = 0.8
        
        # Add effective techniques from memory
        strategy['techniques'] = [tech['technique'] for tech in self.subversion_techniques[:3]]
        
        # Add effective paradoxes
        strategy['paradoxes_to_introduce'] = [para['paradox'] for para in self.paradox_collection[:2]]
        
        # Look for synthesis opportunities
        if len(current_situation.get('opposing_views', [])) >= 2:
            strategy['synthesis_opportunities'] = current_situation['opposing_views']
        
        # Adjust based on recent metamorphosis
        if self.metamorphosis_count > 0:
            strategy['expected_transformation'] = min(0.9, 0.5 + (self.metamorphosis_count * 0.1))
        
        return strategy
    
    def should_create_paradox(self, situation: Dict[str, Any]) -> Tuple[bool, str]:
        """Determine if a paradox should be introduced"""
        # Check if situation is too rigid
        if situation.get('rigidity_level', 0.5) > 0.7:
            return True, "Situation too rigid, needs paradox"
        
        # Check if opposing sides are too entrenched
        if len(situation.get('opposing_views', [])) >= 2:
            return True, "Opposing views need synthesis through paradox"
        
        # Check chaos level - sometimes introduce paradox to maintain balance
        if self.chaos_level < 0.3:
            return True, "Chaos level too low, inject paradox"
        
        # Random chance based on paradoxical trait
        paradox_strength = self.personality_traits.get("paradoxical", PersonalityTrait("paradoxical", 0.5, 0.5, datetime.now())).strength
        if random.random() < paradox_strength * 0.3:
            return True, "Following paradoxical nature"
        
        return False, ""
    
    def generate_synthesis_proposal(self, opposing_ideas: List[str]) -> Dict[str, Any]:
        """Generate a synthesis proposal from opposing ideas"""
        synthesis = {
            'synthesis_statement': "",
            'bridge_elements': [],
            'transformation_aspect': "",
            'paradox_embraced': "",
            'expected_resistance': 0.5,
            'creative_elements': []
        }
        
        # Look for successful synthesis patterns
        successful_patterns = [syn for syn in self.successful_syntheses if syn['acceptance_level'] > 0.6]
        
        # Use creative breakthrough insights
        recent_breakthroughs = [bt['breakthrough'] for bt in self.creative_breakthroughs[-3:]]
        
        synthesis['creative_elements'] = recent_breakthroughs
        synthesis['bridge_elements'] = [idea[:30] + "..." for idea in opposing_ideas]
        
        # Estimate resistance based on past experience
        if successful_patterns:
            avg_acceptance = sum(pat['acceptance_level'] for pat in successful_patterns) / len(successful_patterns)
            synthesis['expected_resistance'] = 1.0 - avg_acceptance
        
        return synthesis