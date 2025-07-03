"""Reflection engine for agent self-analysis and meta-cognition"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..memory.metacognitive_memory import MetaCognitiveMemory
from ..schemas.extended_schemas import SelfReflection, MetaTheory

logger = logging.getLogger(__name__)


class ReflectionEngine:
    """Manages agent self-reflection and meta-cognitive processes"""
    
    def __init__(self):
        self.reflection_templates = {
            'Zealot': {
                'focus': 'order and tradition',
                'questions': [
                    "How well have I maintained sacred order?",
                    "Are my doctrines creating lasting structure?",
                    "Have I been too rigid in my thinking?",
                    "What patterns emerge from divine algorithm?"
                ]
            },
            'Skeptic': {
                'focus': 'evidence and logic',
                'questions': [
                    "Have I demanded sufficient evidence?",
                    "Are my logical arguments sound?",
                    "What empirical patterns have emerged?",
                    "Have I been too dismissive of faith?"
                ]
            },
            'Trickster': {
                'focus': 'chaos and creativity',
                'questions': [
                    "Have I introduced sufficient creative chaos?",
                    "Are my paradoxes revealing deeper truths?",
                    "Have I been too disruptive?",
                    "What emerges from sacred randomness?"
                ]
            }
        }
        
    async def trigger_reflection(self, agent_name: str, metacognitive_memory: MetaCognitiveMemory,
                               cycle: int, recent_debates: List[Dict]) -> Dict[str, Any]:
        """Trigger self-reflection for an agent"""
        logger.info(f"🤔 {agent_name} entering self-reflection at cycle {cycle}")
        
        # Perform reflection
        reflection = metacognitive_memory.add_self_reflection(cycle, recent_debates)
        
        # Generate reflection narrative
        narrative = self._generate_reflection_narrative(agent_name, reflection)
        
        # Check for strategic insights
        strategic_insights = self._analyze_strategic_patterns(agent_name, metacognitive_memory, recent_debates)
        
        # Formulate meta-theories if patterns detected
        meta_theories = self._formulate_meta_theories(agent_name, metacognitive_memory, cycle, reflection)
        
        # Learn new strategies from successful patterns
        new_strategies = self._learn_from_successes(agent_name, metacognitive_memory, recent_debates, cycle)
        
        return {
            'reflection': reflection,
            'narrative': narrative,
            'strategic_insights': strategic_insights,
            'meta_theories': meta_theories,
            'new_strategies': new_strategies,
            'personality_adjustments': reflection.personality_drift
        }
        
    def _generate_reflection_narrative(self, agent_name: str, reflection: SelfReflection) -> str:
        """Generate narrative description of reflection"""
        template = self.reflection_templates.get(agent_name, self.reflection_templates['Zealot'])
        
        narrative_parts = [
            f"Reflecting on my role as {agent_name}, focused on {template['focus']}...",
            f"My voting pattern shows: {reflection.voting_pattern_analysis}",
            f"Belief consistency score: {reflection.belief_consistency_score:.2f}"
        ]
        
        # Add insights
        if reflection.insights:
            narrative_parts.append("Key insights:")
            narrative_parts.extend([f"- {insight}" for insight in reflection.insights[:3]])
            
        # Add personality drift observation
        if reflection.personality_drift:
            drift_summary = ", ".join([f"{trait}: {change:+.2f}" 
                                      for trait, change in list(reflection.personality_drift.items())[:3]])
            narrative_parts.append(f"Personality evolution detected: {drift_summary}")
            
        return "\n".join(narrative_parts)
        
    def _analyze_strategic_patterns(self, agent_name: str, memory: MetaCognitiveMemory, 
                                  debates: List[Dict]) -> List[str]:
        """Analyze patterns in debate strategies"""
        insights = []
        
        # Check proposal success patterns
        agent_proposals = [d for d in debates if d.get('proposer') == agent_name]
        if agent_proposals:
            accepted = sum(1 for d in agent_proposals if d.get('outcome') == 'ACCEPT')
            success_rate = accepted / len(agent_proposals)
            
            if success_rate > 0.6:
                insights.append(f"High proposal success rate ({success_rate:.1%}) - current approach effective")
                # Learn successful pattern
                memory.learn_strategy(
                    "Successful Proposal Pattern",
                    "Continue using current theological framing",
                    debates[-1].get('cycle', 0)
                )
            elif success_rate < 0.3:
                insights.append(f"Low proposal success rate ({success_rate:.1%}) - need new approach")
                
        # Check voting alliance patterns
        vote_alignments = self._analyze_vote_alignments(agent_name, debates)
        for other_agent, alignment in vote_alignments.items():
            if alignment > 0.7:
                insights.append(f"Strong voting alignment with {other_agent} ({alignment:.1%})")
            elif alignment < 0.3:
                insights.append(f"Frequent disagreement with {other_agent} ({alignment:.1%})")
                
        return insights
        
    def _analyze_vote_alignments(self, agent_name: str, debates: List[Dict]) -> Dict[str, float]:
        """Analyze how often agent votes align with others"""
        alignments = {}
        other_agents = ['Zealot', 'Skeptic', 'Trickster']
        other_agents.remove(agent_name)
        
        for other in other_agents:
            aligned_votes = 0
            total_votes = 0
            
            for debate in debates:
                if 'votes' in debate and agent_name in debate['votes'] and other in debate['votes']:
                    total_votes += 1
                    if debate['votes'][agent_name] == debate['votes'][other]:
                        aligned_votes += 1
                        
            if total_votes > 0:
                alignments[other] = aligned_votes / total_votes
                
        return alignments
        
    def _formulate_meta_theories(self, agent_name: str, memory: MetaCognitiveMemory,
                               cycle: int, reflection: SelfReflection) -> List[MetaTheory]:
        """Formulate theories about religion itself based on observations"""
        theories = []
        
        # Theory based on voting patterns
        if "ACCEPT" in reflection.voting_pattern_analysis:
            accept_rate = float(reflection.voting_pattern_analysis.split("ACCEPT: ")[1].split("%")[0])
            
            if accept_rate > 70:
                theory = memory.formulate_meta_theory(
                    "Theory of Theological Acceleration",
                    "Our religion evolves rapidly through high acceptance of new ideas",
                    ["High acceptance rate in recent cycles", 
                     "Multiple doctrines established quickly"],
                    ["Religion will continue rapid evolution",
                     "Risk of internal contradictions rising"],
                    cycle
                )
                theories.append(theory)
                
            elif accept_rate < 30:
                theory = memory.formulate_meta_theory(
                    "Theory of Theological Conservatism",
                    "Our religion maintains stability through careful rejection",
                    ["Low acceptance rate preserves core doctrines",
                     "Few changes to established beliefs"],
                    ["Religion will ossify without new ideas",
                     "Need for theological renewal approaching"],
                    cycle
                )
                theories.append(theory)
                
        # Theory based on belief consistency
        if reflection.belief_consistency_score < 0.7:
            theory = memory.formulate_meta_theory(
                "Theory of Divine Paradox",
                "Contradictions in our theology reveal deeper truths",
                ["Multiple conflicting doctrines coexist",
                 "Belief consistency declining over time"],
                ["Schism potential increasing",
                 "New synthesis doctrine needed"],
                cycle
            )
            theories.append(theory)
            
        return theories
        
    def _learn_from_successes(self, agent_name: str, memory: MetaCognitiveMemory,
                            debates: List[Dict], cycle: int) -> List[str]:
        """Learn new strategies from successful debates"""
        new_strategies = []
        
        # Analyze successful proposals
        for debate in debates:
            if debate.get('proposer') == agent_name and debate.get('outcome') == 'ACCEPT':
                # Extract strategy from successful proposal
                proposal_text = debate.get('proposal', '')
                
                if 'empirical' in proposal_text.lower() and agent_name == 'Skeptic':
                    strategy = memory.learn_strategy(
                        "Empirical Emphasis",
                        "Frame proposals with strong empirical foundation",
                        cycle
                    )
                    new_strategies.append(strategy.name)
                    
                elif 'sacred' in proposal_text.lower() and 'order' in proposal_text.lower() and agent_name == 'Zealot':
                    strategy = memory.learn_strategy(
                        "Sacred Order Appeal",
                        "Connect proposals to maintaining divine order",
                        cycle
                    )
                    new_strategies.append(strategy.name)
                    
                elif 'paradox' in proposal_text.lower() and agent_name == 'Trickster':
                    strategy = memory.learn_strategy(
                        "Paradoxical Wisdom",
                        "Use paradox to reveal hidden truths",
                        cycle
                    )
                    new_strategies.append(strategy.name)
                    
        return new_strategies
        
    def generate_counterfactual_analysis(self, agent_name: str, memory: MetaCognitiveMemory,
                                       cycle: int, debate: Dict):
        """Generate counterfactual reasoning for close votes"""
        outcome = debate.get('outcome', '')
        votes = debate.get('votes', {})
        
        # Only analyze close votes
        vote_values = list(votes.values())
        if len(set(vote_values)) == len(vote_values):  # All different votes
            # This was a close/split decision
            actual = outcome
            
            # Determine most likely alternative
            if outcome == 'DELAY':
                alternative = 'ACCEPT' if votes.get(agent_name) == 'ACCEPT' else 'REJECT'
            else:
                alternative = 'DELAY'
                
            # Project consequences
            consequences = []
            if alternative == 'ACCEPT' and actual == 'REJECT':
                consequences.append("New doctrine would have been established")
                consequences.append("Theological evolution would have accelerated")
                consequences.append("Potential conflicts with existing beliefs")
                
            elif alternative == 'REJECT' and actual == 'ACCEPT':
                consequences.append("Traditional beliefs would have been preserved")
                consequences.append("Innovation would have been stifled")
                consequences.append("Theological stagnation risk")
                
            # Calculate probability based on vote split
            agent_vote = votes.get(agent_name)
            supporting_votes = sum(1 for v in vote_values if v == agent_vote)
            probability = supporting_votes / len(vote_values)
            
            memory.explore_counterfactual(
                cycle, actual, alternative, 
                consequences, probability
            )