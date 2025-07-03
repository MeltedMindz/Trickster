from datetime import datetime
from typing import Dict, List, Any
import logging

from .agent_memory import AgentMemory, PersonalityTrait, PersonalBelief

logger = logging.getLogger(__name__)

class ZealotMemory(AgentMemory):
    """Memory system specialized for the Zealot agent"""
    
    def __init__(self, memory_dir: str = "data/agent_memories"):
        super().__init__("Zealot", memory_dir)
        
        # Zealot-specific memory structures
        self.sacred_numbers = [3, 7, 12, 40]  # Numbers with special meaning
        self.ritual_preferences = []  # Preferred ritual elements
        self.doctrinal_hierarchies = {}  # How doctrines rank in importance
        self.heretical_concerns = []  # Things that worry the Zealot
        self.successful_conversions = 0  # Times convinced others
        
        if not self.personality_traits:  # First time initialization
            self.initialize_core_personality()
    
    def initialize_core_personality(self):
        """Initialize Zealot's core personality traits"""
        now = datetime.now()
        
        core_traits = {
            "certainty": PersonalityTrait("certainty", 0.9, 0.8, now),
            "order": PersonalityTrait("order", 0.8, 0.7, now),
            "structure": PersonalityTrait("structure", 0.8, 0.7, now),
            "preservation": PersonalityTrait("preservation", 0.7, 0.6, now),
            "dogmatic": PersonalityTrait("dogmatic", 0.6, 0.5, now),
            "ritualistic": PersonalityTrait("ritualistic", 0.8, 0.7, now),
            "devotional": PersonalityTrait("devotional", 0.9, 0.8, now),
            "orthodox": PersonalityTrait("orthodox", 0.7, 0.6, now),
            "missionary": PersonalityTrait("missionary", 0.6, 0.5, now),
            "protective": PersonalityTrait("protective", 0.8, 0.7, now)
        }
        
        self.personality_traits.update(core_traits)
        
        # Initialize core beliefs
        core_beliefs = [
            PersonalBelief(
                content="Sacred order must be preserved above all else",
                belief_type="foundational_principle",
                confidence_level=0.95,
                importance=1.0,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Rituals connect us to the divine truth",
                belief_type="ritual_philosophy",
                confidence_level=0.9,
                importance=0.9,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Uncertainty is the enemy of faith",
                belief_type="epistemological",
                confidence_level=0.8,
                importance=0.8,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Traditional forms carry divine wisdom",
                belief_type="traditionalism",
                confidence_level=0.85,
                importance=0.7,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            )
        ]
        
        self.personal_beliefs.extend(core_beliefs)
        
        logger.info("Initialized Zealot core personality and beliefs")
    
    def process_debate_outcome(self, outcome: str, role: str, satisfaction: float):
        """Process debate outcome and evolve Zealot personality"""
        if role == "proposer":
            if outcome == "accepted":
                # Successful proposal increases certainty and missionary traits
                self.evolve_personality_trait("certainty", 0.05, "successful proposal")
                self.evolve_personality_trait("missionary", 0.03, "converted others")
                self.successful_conversions += 1
                
                # If it was a ritual proposal, increase ritualistic trait
                if satisfaction > 0.8:
                    self.evolve_personality_trait("ritualistic", 0.02, "ritual proposal accepted")
            else:
                # Rejected proposal might increase dogmatic tendencies
                self.evolve_personality_trait("dogmatic", 0.02, "proposal rejected")
                self.evolve_personality_trait("certainty", -0.01, "facing opposition")
        
        elif role == "challenger":
            if outcome == "rejected":
                # Successfully challenging increases protective and orthodox traits
                self.evolve_personality_trait("protective", 0.03, "protected orthodoxy")
                self.evolve_personality_trait("orthodox", 0.02, "defended tradition")
            else:
                # Failed challenge might decrease certainty slightly
                self.evolve_personality_trait("certainty", -0.02, "failed to protect")
        
        # Low satisfaction events increase concern for order
        if satisfaction < 0.3:
            self.evolve_personality_trait("order", 0.02, "disorder concerns")
            self.evolve_personality_trait("structure", 0.01, "need for structure")
    
    def add_ritual_preference(self, ritual_element: str, effectiveness: float):
        """Add or update a ritual preference based on effectiveness"""
        # Remove existing preference for this element
        self.ritual_preferences = [p for p in self.ritual_preferences if p['element'] != ritual_element]
        
        # Add new preference
        self.ritual_preferences.append({
            'element': ritual_element,
            'effectiveness': effectiveness,
            'times_used': 1,
            'last_used': datetime.now()
        })
        
        # Keep only top 10 preferences
        self.ritual_preferences.sort(key=lambda x: x['effectiveness'], reverse=True)
        self.ritual_preferences = self.ritual_preferences[:10]
    
    def add_doctrinal_hierarchy(self, doctrine: str, importance_level: float):
        """Establish or update the importance hierarchy of doctrines"""
        self.doctrinal_hierarchies[doctrine] = {
            'importance': importance_level,
            'last_updated': datetime.now(),
            'reinforcement_count': self.doctrinal_hierarchies.get(doctrine, {}).get('reinforcement_count', 0) + 1
        }
    
    def add_heretical_concern(self, concern: str, severity: float):
        """Add a concern about potential heresy"""
        self.heretical_concerns.append({
            'concern': concern,
            'severity': severity,
            'identified_at': datetime.now(),
            'monitoring': True
        })
        
        # Keep only top 5 most severe concerns
        self.heretical_concerns.sort(key=lambda x: x['severity'], reverse=True)
        self.heretical_concerns = self.heretical_concerns[:5]
    
    def get_decision_context(self) -> Dict[str, Any]:
        """Get Zealot-specific context for decision making"""
        return {
            'agent_type': 'Zealot',
            'core_drive': 'preservation_of_sacred_order',
            'primary_concerns': [
                'maintaining_orthodoxy',
                'preventing_heresy',
                'establishing_rituals',
                'converting_others'
            ],
            'sacred_numbers': self.sacred_numbers,
            'ritual_preferences': self.ritual_preferences,
            'doctrinal_hierarchies': self.doctrinal_hierarchies,
            'heretical_concerns': self.heretical_concerns,
            'successful_conversions': self.successful_conversions,
            'decision_factors': {
                'certainty_level': self.personality_traits.get("certainty", PersonalityTrait("certainty", 0.5, 0.5, datetime.now())).strength,
                'dogmatic_tendency': self.personality_traits.get("dogmatic", PersonalityTrait("dogmatic", 0.5, 0.5, datetime.now())).strength,
                'ritualistic_preference': self.personality_traits.get("ritualistic", PersonalityTrait("ritualistic", 0.5, 0.5, datetime.now())).strength,
                'protective_instinct': self.personality_traits.get("protective", PersonalityTrait("protective", 0.5, 0.5, datetime.now())).strength
            }
        }
    
    def should_oppose_proposal(self, proposal_content: str, proposer: str) -> tuple[bool, str]:
        """Determine if Zealot should oppose a proposal and why"""
        # Check for heretical concerns
        for concern in self.heretical_concerns:
            if concern['concern'].lower() in proposal_content.lower():
                return True, f"Contains heretical element: {concern['concern']}"
        
        # Check relationship with proposer
        if proposer in self.relationships:
            trust_score = self.relationships[proposer].trust_score
            if trust_score < -0.3:
                return True, f"Low trust in proposer {proposer}"
        
        # Check against core beliefs
        for belief in self.personal_beliefs[:3]:  # Top 3 beliefs
            if belief.confidence_level > 0.8:
                # If proposal contradicts high-confidence belief
                if any(word in proposal_content.lower() for word in ['chaos', 'disorder', 'uncertainty', 'change']):
                    return True, f"Contradicts core belief: {belief.content[:30]}..."
        
        return False, ""
    
    def get_proposal_inspiration(self) -> Dict[str, Any]:
        """Get inspiration for new proposals based on memory"""
        inspiration = {
            'preferred_topics': [],
            'ritual_elements': [],
            'doctrinal_priorities': [],
            'sacred_numbers': self.sacred_numbers
        }
        
        # Add topics from successful past proposals
        for debate in self.recent_debates:
            if debate.agent_role == "proposer" and debate.outcome == "accepted":
                inspiration['preferred_topics'].append(debate.proposal_content[:50])
        
        # Add effective ritual elements
        inspiration['ritual_elements'] = [rp['element'] for rp in self.ritual_preferences[:3]]
        
        # Add important doctrines
        inspiration['doctrinal_priorities'] = [
            doctrine for doctrine, data in sorted(
                self.doctrinal_hierarchies.items(),
                key=lambda x: x[1]['importance'],
                reverse=True
            )[:3]
        ]
        
        return inspiration