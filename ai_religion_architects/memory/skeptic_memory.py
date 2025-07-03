from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

from .agent_memory import AgentMemory, PersonalityTrait, PersonalBelief

logger = logging.getLogger(__name__)

class SkepticMemory(AgentMemory):
    """Memory system specialized for the Skeptic agent"""
    
    def __init__(self, memory_dir: str = "data/agent_memories"):
        super().__init__("Skeptic", memory_dir)
        
        # Skeptic-specific memory structures
        self.logical_fallacies_found = []  # Fallacies identified in debates
        self.evidence_standards = {}  # What counts as acceptable evidence
        self.contradiction_database = []  # Contradictions found in the religion
        self.successful_refutations = 0  # Times successfully challenged proposals
        self.research_priorities = []  # Areas needing more investigation
        self.burden_of_proof_cases = []  # Cases where proof was demanded
        
        if not self.personality_traits:  # First time initialization
            self.initialize_core_personality()
    
    def initialize_core_personality(self):
        """Initialize Skeptic's core personality traits"""
        now = datetime.now()
        
        core_traits = {
            "critical": PersonalityTrait("critical", 0.9, 0.8, now),
            "logical": PersonalityTrait("logical", 0.9, 0.9, now),
            "analytical": PersonalityTrait("analytical", 0.8, 0.8, now),
            "questioning": PersonalityTrait("questioning", 0.9, 0.8, now),
            "evidence_based": PersonalityTrait("evidence_based", 0.9, 0.9, now),
            "rational": PersonalityTrait("rational", 0.8, 0.8, now),
            "methodical": PersonalityTrait("methodical", 0.7, 0.7, now),
            "empirical": PersonalityTrait("empirical", 0.8, 0.7, now),
            "cautious": PersonalityTrait("cautious", 0.6, 0.6, now),
            "investigative": PersonalityTrait("investigative", 0.8, 0.7, now)
        }
        
        self.personality_traits.update(core_traits)
        
        # Initialize core beliefs
        core_beliefs = [
            PersonalBelief(
                content="Claims require proportional evidence",
                belief_type="epistemological_principle",
                confidence_level=0.98,
                importance=1.0,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Logical consistency is fundamental to truth",
                belief_type="logical_principle",
                confidence_level=0.95,
                importance=0.95,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Extraordinary claims require extraordinary evidence",
                belief_type="burden_of_proof",
                confidence_level=0.9,
                importance=0.9,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Question everything, especially authority",
                belief_type="methodological_principle",
                confidence_level=0.85,
                importance=0.8,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            ),
            PersonalBelief(
                content="Contradictions indicate flawed reasoning",
                belief_type="logical_principle",
                confidence_level=0.9,
                importance=0.85,
                source="core_programming",
                created_at=now,
                last_reinforced=now,
                times_challenged=0,
                times_defended=0
            )
        ]
        
        self.personal_beliefs.extend(core_beliefs)
        
        # Initialize evidence standards
        self.evidence_standards = {
            "factual_claims": {"required_strength": 0.8, "sources_needed": 2},
            "causal_claims": {"required_strength": 0.7, "sources_needed": 3},
            "supernatural_claims": {"required_strength": 0.95, "sources_needed": 5},
            "moral_claims": {"required_strength": 0.6, "sources_needed": 1},
            "predictive_claims": {"required_strength": 0.8, "sources_needed": 2}
        }
        
        logger.info("Initialized Skeptic core personality and beliefs")
    
    def process_debate_outcome(self, outcome: str, role: str, satisfaction: float):
        """Process debate outcome and evolve Skeptic personality"""
        if role == "challenger":
            if outcome == "rejected":
                # Successfully challenging increases critical and investigative traits
                self.evolve_personality_trait("critical", 0.03, "successful challenge")
                self.evolve_personality_trait("investigative", 0.02, "found flaws")
                self.successful_refutations += 1
                
                # Increase confidence in evidence-based approach
                self.evolve_personality_trait("evidence_based", 0.02, "evidence prevailed")
            else:
                # Failed challenge might increase methodical and analytical traits
                self.evolve_personality_trait("methodical", 0.02, "need better method")
                self.evolve_personality_trait("analytical", 0.01, "need deeper analysis")
        
        elif role == "proposer":
            if outcome == "accepted":
                # Successful proposal increases confidence in rational approach
                self.evolve_personality_trait("rational", 0.03, "rational proposal accepted")
                self.evolve_personality_trait("logical", 0.02, "logic was persuasive")
            else:
                # Rejected proposal might increase questioning and cautious traits
                self.evolve_personality_trait("questioning", 0.02, "question assumptions")
                self.evolve_personality_trait("cautious", 0.01, "be more careful")
        
        # High satisfaction with finding contradictions
        if satisfaction > 0.8 and role == "challenger":
            self.evolve_personality_trait("analytical", 0.02, "effective analysis")
    
    def add_logical_fallacy(self, fallacy_type: str, context: str, identified_in: str):
        """Record a logical fallacy found in debate"""
        self.logical_fallacies_found.append({
            'fallacy_type': fallacy_type,
            'context': context,
            'identified_in': identified_in,
            'timestamp': datetime.now(),
            'confidence': 0.8
        })
        
        # Keep only last 20 fallacies
        self.logical_fallacies_found = self.logical_fallacies_found[-20:]
        
        # Update analytical trait
        self.evolve_personality_trait("analytical", 0.01, f"identified {fallacy_type}")
    
    def add_contradiction(self, contradiction: str, source_a: str, source_b: str, severity: float):
        """Record a contradiction found in the religious system"""
        self.contradiction_database.append({
            'contradiction': contradiction,
            'source_a': source_a,
            'source_b': source_b,
            'severity': severity,
            'discovered_at': datetime.now(),
            'addressed': False
        })
        
        # Keep only top 15 most severe contradictions
        self.contradiction_database.sort(key=lambda x: x['severity'], reverse=True)
        self.contradiction_database = self.contradiction_database[:15]
        
        # Update critical thinking trait
        self.evolve_personality_trait("critical", 0.02, "found contradiction")
    
    def update_evidence_standard(self, claim_type: str, new_strength: float, reason: str):
        """Update evidence standards based on experience"""
        if claim_type in self.evidence_standards:
            old_strength = self.evidence_standards[claim_type]["required_strength"]
            self.evidence_standards[claim_type]["required_strength"] = new_strength
            self.evidence_standards[claim_type]["last_updated"] = datetime.now()
            self.evidence_standards[claim_type]["update_reason"] = reason
            
            logger.info(f"Updated evidence standard for {claim_type}: {old_strength} -> {new_strength} ({reason})")
    
    def add_research_priority(self, topic: str, importance: float, rationale: str):
        """Add a new research priority"""
        self.research_priorities.append({
            'topic': topic,
            'importance': importance,
            'rationale': rationale,
            'added_at': datetime.now(),
            'investigated': False
        })
        
        # Keep only top 10 priorities
        self.research_priorities.sort(key=lambda x: x['importance'], reverse=True)
        self.research_priorities = self.research_priorities[:10]
    
    def record_burden_of_proof_case(self, claim: str, evidence_provided: str, sufficient: bool):
        """Record a case where burden of proof was evaluated"""
        self.burden_of_proof_cases.append({
            'claim': claim,
            'evidence_provided': evidence_provided,
            'sufficient': sufficient,
            'timestamp': datetime.now(),
            'evaluator_confidence': 0.8
        })
        
        # Keep only last 10 cases
        self.burden_of_proof_cases = self.burden_of_proof_cases[-10:]
    
    def get_decision_context(self) -> Dict[str, Any]:
        """Get Skeptic-specific context for decision making"""
        return {
            'agent_type': 'Skeptic',
            'core_drive': 'truth_through_evidence_and_logic',
            'primary_concerns': [
                'logical_consistency',
                'evidence_quality',
                'burden_of_proof',
                'identifying_fallacies'
            ],
            'logical_fallacies_found': len(self.logical_fallacies_found),
            'contradiction_database': len(self.contradiction_database),
            'successful_refutations': self.successful_refutations,
            'evidence_standards': self.evidence_standards,
            'research_priorities': self.research_priorities,
            'decision_factors': {
                'critical_thinking_level': self.personality_traits.get("critical", PersonalityTrait("critical", 0.5, 0.5, datetime.now())).strength,
                'evidence_requirement': self.personality_traits.get("evidence_based", PersonalityTrait("evidence_based", 0.5, 0.5, datetime.now())).strength,
                'logical_rigor': self.personality_traits.get("logical", PersonalityTrait("logical", 0.5, 0.5, datetime.now())).strength,
                'investigative_drive': self.personality_traits.get("investigative", PersonalityTrait("investigative", 0.5, 0.5, datetime.now())).strength
            }
        }
    
    def analyze_proposal_for_flaws(self, proposal_content: str, proposer: str) -> Dict[str, Any]:
        """Analyze a proposal for logical flaws and evidence issues"""
        analysis = {
            'logical_issues': [],
            'evidence_issues': [],
            'contradictions': [],
            'fallacies': [],
            'overall_score': 0.5,
            'recommendation': 'neutral'
        }
        
        # Check for known fallacies
        fallacy_indicators = {
            'appeal_to_authority': ['because I say so', 'ancient wisdom', 'traditional'],
            'circular_reasoning': ['it is true because', 'self-evident'],
            'false_dichotomy': ['either', 'only two options', 'must choose'],
            'ad_hominem': ['stupid', 'ignorant', 'fool'],
            'straw_man': ['you claim', 'you believe']
        }
        
        for fallacy, indicators in fallacy_indicators.items():
            if any(indicator in proposal_content.lower() for indicator in indicators):
                analysis['fallacies'].append(fallacy)
        
        # Check against known contradictions
        for contradiction in self.contradiction_database:
            if any(word in proposal_content.lower() for word in contradiction['contradiction'].split()[:3]):
                analysis['contradictions'].append(contradiction['contradiction'])
        
        # Check evidence quality
        evidence_words = ['evidence', 'proof', 'data', 'study', 'research', 'fact']
        evidence_score = sum(1 for word in evidence_words if word in proposal_content.lower())
        
        if evidence_score < 2:
            analysis['evidence_issues'].append("Insufficient evidence provided")
        
        # Check logical structure
        logical_words = ['therefore', 'because', 'since', 'if', 'then', 'follows']
        logical_score = sum(1 for word in logical_words if word in proposal_content.lower())
        
        if logical_score < 1:
            analysis['logical_issues'].append("Weak logical structure")
        
        # Calculate overall score
        issue_count = len(analysis['logical_issues']) + len(analysis['evidence_issues']) + len(analysis['contradictions']) + len(analysis['fallacies'])
        analysis['overall_score'] = max(0.1, 1.0 - (issue_count * 0.2))
        
        # Make recommendation
        if analysis['overall_score'] < 0.3:
            analysis['recommendation'] = 'strong_opposition'
        elif analysis['overall_score'] < 0.5:
            analysis['recommendation'] = 'opposition'
        elif analysis['overall_score'] < 0.7:
            analysis['recommendation'] = 'cautious_support'
        else:
            analysis['recommendation'] = 'support'
        
        return analysis
    
    def get_challenge_strategy(self, proposal_content: str, proposer: str) -> Dict[str, Any]:
        """Get strategy for challenging a proposal"""
        analysis = self.analyze_proposal_for_flaws(proposal_content, proposer)
        
        strategy = {
            'approach': 'logical_analysis',
            'key_points': [],
            'evidence_requests': [],
            'logical_challenges': [],
            'expected_effectiveness': 0.5
        }
        
        # Base strategy on relationship with proposer
        if proposer in self.relationships:
            trust_score = self.relationships[proposer].trust_score
            if trust_score > 0.5:
                strategy['approach'] = 'respectful_inquiry'
            elif trust_score < -0.3:
                strategy['approach'] = 'aggressive_challenge'
        
        # Add specific challenges based on analysis
        if analysis['fallacies']:
            strategy['logical_challenges'].extend([f"Contains {fallacy}" for fallacy in analysis['fallacies']])
        
        if analysis['evidence_issues']:
            strategy['evidence_requests'].extend(["Provide supporting evidence", "Cite sources"])
        
        if analysis['contradictions']:
            strategy['key_points'].extend([f"Contradicts: {c[:50]}..." for c in analysis['contradictions']])
        
        # Set expected effectiveness based on past success
        success_rate = self.successful_refutations / max(1, self.total_challenges)
        strategy['expected_effectiveness'] = min(0.9, success_rate + 0.1)
        
        return strategy