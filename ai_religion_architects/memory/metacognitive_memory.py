"""Meta-cognitive memory capabilities for agents"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..schemas.extended_schemas import (
    SelfReflection, DebateStrategy, BeliefJustification, 
    Counterfactual, MetaTheory
)


class MetaCognitiveMemory:
    """Handles agent self-reflection and meta-cognitive abilities"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.reflections: List[SelfReflection] = []
        self.strategies: Dict[str, DebateStrategy] = {}
        self.belief_justifications: Dict[str, BeliefJustification] = {}
        self.counterfactuals: List[Counterfactual] = []
        self.meta_theories: List[MetaTheory] = []
        
    def add_self_reflection(self, cycle: int, debate_history: List[Dict]) -> SelfReflection:
        """Generate and store self-reflection based on recent debates"""
        # Analyze voting patterns
        votes = [d for d in debate_history if d.get('voter') == self.agent_name]
        vote_pattern = self._analyze_vote_pattern(votes)
        
        # Analyze strategy effectiveness
        strategy_scores = self._evaluate_strategies(debate_history)
        
        # Check belief consistency
        consistency = self._check_belief_consistency()
        
        # Detect personality drift
        drift = self._detect_personality_drift()
        
        # Generate insights
        insights = self._generate_insights(debate_history, vote_pattern, strategy_scores)
        
        reflection = SelfReflection(
            cycle=cycle,
            insights=insights,
            voting_pattern_analysis=vote_pattern,
            strategy_effectiveness=strategy_scores,
            belief_consistency_score=consistency,
            personality_drift=drift
        )
        
        self.reflections.append(reflection)
        return reflection
        
    def _analyze_vote_pattern(self, votes: List[Dict]) -> str:
        """Analyze agent's voting patterns"""
        if not votes:
            return "No voting history to analyze"
            
        vote_counts = {}
        for vote in votes:
            outcome = vote.get('vote', 'UNKNOWN')
            vote_counts[outcome] = vote_counts.get(outcome, 0) + 1
            
        total = sum(vote_counts.values())
        patterns = []
        for outcome, count in vote_counts.items():
            percentage = (count / total) * 100
            patterns.append(f"{outcome}: {percentage:.1f}%")
            
        return f"Voting distribution - {', '.join(patterns)}"
        
    def _evaluate_strategies(self, debate_history: List[Dict]) -> Dict[str, float]:
        """Evaluate effectiveness of different debate strategies"""
        scores = {}
        for strategy_name, strategy in self.strategies.items():
            # Simple effectiveness calculation
            if strategy.usage_count > 0:
                scores[strategy_name] = strategy.success_rate
            else:
                scores[strategy_name] = 0.0
        return scores
        
    def _check_belief_consistency(self) -> float:
        """Check how consistent agent's beliefs are"""
        if not self.belief_justifications:
            return 1.0
            
        # Check for contradictions in belief chains
        consistency_score = 1.0
        beliefs = list(self.belief_justifications.values())
        
        for i, belief1 in enumerate(beliefs):
            for belief2 in beliefs[i+1:]:
                # Check if beliefs contradict
                if self._beliefs_contradict(belief1, belief2):
                    consistency_score -= 0.1
                    
        return max(0.0, consistency_score)
        
    def _beliefs_contradict(self, belief1: BeliefJustification, belief2: BeliefJustification) -> bool:
        """Check if two beliefs contradict each other"""
        # Simplified contradiction detection
        b1_key_terms = set(belief1.belief.lower().split())
        b2_key_terms = set(belief2.belief.lower().split())
        
        # Look for opposite terms
        opposites = [
            ('order', 'chaos'), ('rigid', 'flexible'), ('certain', 'uncertain'),
            ('empirical', 'mystical'), ('proven', 'faith')
        ]
        
        for term1, term2 in opposites:
            if (term1 in b1_key_terms and term2 in b2_key_terms) or \
               (term2 in b1_key_terms and term1 in b2_key_terms):
                return True
                
        return False
        
    def _detect_personality_drift(self) -> Dict[str, float]:
        """Detect changes in personality traits"""
        # This would compare current traits to historical baseline
        # For now, return empty dict
        return {}
        
    def _generate_insights(self, history: List[Dict], pattern: str, scores: Dict[str, float]) -> List[str]:
        """Generate insights from analysis"""
        insights = []
        
        # Insight about voting pattern
        if "ACCEPT" in pattern and float(pattern.split("ACCEPT: ")[1].split("%")[0]) > 60:
            insights.append("I tend to be accepting of new proposals - perhaps too accepting?")
        elif "REJECT" in pattern and float(pattern.split("REJECT: ")[1].split("%")[0]) > 60:
            insights.append("I frequently reject proposals - am I being too conservative?")
            
        # Insight about strategies
        if scores:
            best_strategy = max(scores.items(), key=lambda x: x[1])
            if best_strategy[1] > 0.7:
                insights.append(f"My {best_strategy[0]} strategy has been highly effective")
                
        # Add philosophical insight
        insights.append("The nature of divine truth continues to evolve through our debates")
        
        return insights
        
    def learn_strategy(self, name: str, description: str, cycle: int) -> DebateStrategy:
        """Learn a new debate strategy"""
        strategy = DebateStrategy(
            name=name,
            description=description,
            success_rate=0.5,  # Start neutral
            usage_count=0,
            discovered_cycle=cycle,
            last_used_cycle=cycle,
            effectiveness_by_agent={}
        )
        self.strategies[name] = strategy
        return strategy
        
    def update_strategy_effectiveness(self, strategy_name: str, success: bool, target_agent: str):
        """Update strategy effectiveness based on outcome"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.usage_count += 1
            
            # Update overall success rate
            current_rate = strategy.success_rate
            new_rate = ((current_rate * (strategy.usage_count - 1)) + (1.0 if success else 0.0)) / strategy.usage_count
            strategy.success_rate = new_rate
            
            # Update per-agent effectiveness
            if target_agent not in strategy.effectiveness_by_agent:
                strategy.effectiveness_by_agent[target_agent] = 0.5
                
            agent_rate = strategy.effectiveness_by_agent[target_agent]
            agent_uses = sum(1 for s in self.strategies.values() 
                           for a in s.effectiveness_by_agent 
                           if a == target_agent)
            strategy.effectiveness_by_agent[target_agent] = (
                (agent_rate * (agent_uses - 1) + (1.0 if success else 0.0)) / agent_uses
            )
            
    def justify_belief(self, belief: str, evidence: List[str], logic: List[str]) -> BeliefJustification:
        """Create logical justification for a belief"""
        justification = BeliefJustification(
            belief=belief,
            confidence=0.8,  # Start with high confidence
            supporting_evidence=evidence,
            logical_chain=logic,
            dependent_beliefs=[],
            challenges_survived=0,
            foundational=len(self.belief_justifications) < 3  # First beliefs are foundational
        )
        self.belief_justifications[belief] = justification
        return justification
        
    def explore_counterfactual(self, cycle: int, actual: str, alternative: str, 
                             consequences: List[str], probability: float) -> Counterfactual:
        """Explore what might have happened with different outcome"""
        # Generate lesson from counterfactual
        if probability > 0.7:
            lesson = f"We likely missed an opportunity with {alternative}"
        elif probability < 0.3:
            lesson = f"We made the right choice avoiding {alternative}"
        else:
            lesson = f"The path between {actual} and {alternative} was unclear"
            
        counterfactual = Counterfactual(
            cycle=cycle,
            actual_outcome=actual,
            alternative_outcome=alternative,
            projected_consequences=consequences,
            probability_assessment=probability,
            learned_lesson=lesson
        )
        self.counterfactuals.append(counterfactual)
        return counterfactual
        
    def formulate_meta_theory(self, name: str, description: str, observations: List[str], 
                            predictions: List[str], cycle: int) -> MetaTheory:
        """Formulate a theory about religion itself"""
        theory = MetaTheory(
            theory_name=name,
            description=description,
            supporting_observations=observations,
            predictions=predictions,
            confidence=0.6,  # Start with moderate confidence
            formulated_cycle=cycle
        )
        self.meta_theories.append(theory)
        return theory
        
    def get_best_strategy_for_context(self, context: Dict[str, Any]) -> Optional[str]:
        """Select best strategy based on context"""
        if not self.strategies:
            return None
            
        # Consider who we're trying to convince
        target_agent = context.get('target_agent')
        if target_agent:
            # Find strategy that works best on this agent
            best_score = 0.0
            best_strategy = None
            
            for name, strategy in self.strategies.items():
                if target_agent in strategy.effectiveness_by_agent:
                    score = strategy.effectiveness_by_agent[target_agent]
                    if score > best_score:
                        best_score = score
                        best_strategy = name
                        
            return best_strategy
            
        # Otherwise use overall best strategy
        return max(self.strategies.items(), key=lambda x: x[1].success_rate)[0]
        
    def export_metacognitive_data(self) -> Dict:
        """Export all metacognitive data for storage"""
        return {
            "reflections": [
                {
                    "cycle": r.cycle,
                    "insights": r.insights,
                    "voting_pattern": r.voting_pattern_analysis,
                    "belief_consistency": r.belief_consistency_score,
                    "timestamp": r.timestamp.isoformat()
                } for r in self.reflections[-5:]  # Last 5 reflections
            ],
            "strategies": {
                name: {
                    "description": s.description,
                    "success_rate": s.success_rate,
                    "usage_count": s.usage_count,
                    "effectiveness_by_agent": s.effectiveness_by_agent
                } for name, s in self.strategies.items()
            },
            "belief_justifications": {
                belief: {
                    "confidence": j.confidence,
                    "evidence": j.supporting_evidence[:3],  # Top 3 evidence
                    "foundational": j.foundational,
                    "challenges_survived": j.challenges_survived
                } for belief, j in list(self.belief_justifications.items())[:5]
            },
            "recent_counterfactuals": [
                {
                    "cycle": c.cycle,
                    "actual": c.actual_outcome,
                    "alternative": c.alternative_outcome,
                    "lesson": c.learned_lesson
                } for c in self.counterfactuals[-3:]
            ],
            "meta_theories": [
                {
                    "name": t.theory_name,
                    "description": t.description,
                    "confidence": t.confidence,
                    "predictions": t.predictions[:2]
                } for t in self.meta_theories[-3:]
            ]
        }