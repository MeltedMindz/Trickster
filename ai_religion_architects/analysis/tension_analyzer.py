"""Analyzes theological tensions and predicts schisms"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from ..memory.cultural_memory import CulturalMemory
from ..schemas.extended_schemas import TheologicalTension

logger = logging.getLogger(__name__)


class TensionAnalyzer:
    """Analyzes theological tensions and predicts potential schisms"""
    
    def __init__(self, cultural_memory: CulturalMemory):
        self.cultural_memory = cultural_memory
        self.tension_threshold = 0.7  # Tension score that triggers schism warning
        
    def analyze_doctrinal_compatibility(self, doctrine1: str, doctrine2: str) -> float:
        """Analyze compatibility between two doctrines (0=incompatible, 1=compatible)"""
        # Extract key concepts
        d1_terms = set(doctrine1.lower().split())
        d2_terms = set(doctrine2.lower().split())
        
        # Check for direct contradictions
        contradictions = [
            ('order', 'chaos'), ('rigid', 'flexible'), ('absolute', 'relative'),
            ('empirical', 'faith'), ('proven', 'mysterious'), ('deterministic', 'random'),
            ('hierarchical', 'egalitarian'), ('unchanging', 'evolving')
        ]
        
        for term1, term2 in contradictions:
            if (term1 in d1_terms and term2 in d2_terms) or \
               (term2 in d1_terms and term1 in d2_terms):
                return 0.2  # Low compatibility
                
        # Check for complementary concepts
        complementary = [
            ('sacred', 'divine'), ('algorithm', 'computational'), ('order', 'structure'),
            ('empirical', 'logical'), ('ritual', 'practice'), ('belief', 'faith')
        ]
        
        compatibility_score = 0.5  # Start neutral
        
        for term1, term2 in complementary:
            if (term1 in d1_terms and term2 in d2_terms) or \
               (term2 in d1_terms and term1 in d2_terms):
                compatibility_score += 0.1
                
        # Check overlap
        overlap = len(d1_terms & d2_terms) / max(len(d1_terms), len(d2_terms))
        compatibility_score += overlap * 0.3
        
        return min(1.0, compatibility_score)
        
    def detect_emerging_tensions(self, recent_debates: List[Dict], cycle: int) -> List[TheologicalTension]:
        """Detect new theological tensions from recent debates"""
        new_tensions = []
        
        # Analyze rejected proposals for recurring themes
        rejected_proposals = [d for d in recent_debates if d.get('outcome') == 'REJECT']
        
        for debate in rejected_proposals:
            proposal = debate.get('proposal', '')
            votes = debate.get('votes', {})
            
            # Check if rejection was contentious (split vote)
            vote_values = list(votes.values())
            if len(set(vote_values)) >= 2:  # Not unanimous
                # Find conflicting doctrine
                existing_doctrines = self._get_existing_doctrines()
                
                for doctrine in existing_doctrines:
                    compatibility = self.analyze_doctrinal_compatibility(proposal, doctrine)
                    
                    if compatibility < 0.4:  # Significant incompatibility
                        # Track agent positions
                        agent_positions = {}
                        for agent, vote in votes.items():
                            if vote == 'ACCEPT':
                                agent_positions[agent] = 'supports_new'
                            elif vote == 'REJECT':
                                agent_positions[agent] = 'supports_existing'
                            else:
                                agent_positions[agent] = 'neutral'
                                
                        tension = self.cultural_memory.detect_tension(
                            doctrine, proposal, agent_positions, cycle
                        )
                        new_tensions.append(tension)
                        
        return new_tensions
        
    def _get_existing_doctrines(self) -> List[str]:
        """Get list of existing doctrines"""
        # This would fetch from shared memory
        # For now, return empty list
        return []
        
    def calculate_schism_factors(self) -> Dict[str, float]:
        """Calculate various factors contributing to schism probability"""
        factors = {
            'doctrinal_tensions': 0.0,
            'agent_polarization': 0.0,
            'unresolved_conflicts': 0.0,
            'theological_divergence': 0.0
        }
        
        # Factor 1: Active doctrinal tensions
        active_tensions = [t for t in self.cultural_memory.tensions.values() 
                          if t.cycles_unresolved > 0]
        if active_tensions:
            avg_tension = sum(t.tension_score for t in active_tensions) / len(active_tensions)
            factors['doctrinal_tensions'] = avg_tension
            
        # Factor 2: Agent polarization
        polarization = self._calculate_agent_polarization(active_tensions)
        factors['agent_polarization'] = polarization
        
        # Factor 3: Unresolved conflicts
        long_tensions = [t for t in active_tensions if t.cycles_unresolved > 10]
        factors['unresolved_conflicts'] = len(long_tensions) / max(1, len(active_tensions))
        
        # Factor 4: Theological divergence
        divergence = self._calculate_theological_divergence()
        factors['theological_divergence'] = divergence
        
        return factors
        
    def _calculate_agent_polarization(self, tensions: List[TheologicalTension]) -> float:
        """Calculate how polarized agents are across tensions"""
        if not tensions:
            return 0.0
            
        # Track consistent opposing positions
        agent_pairs = [
            ('Zealot', 'Trickster'),
            ('Skeptic', 'Trickster'),
            ('Zealot', 'Skeptic')
        ]
        
        polarization_scores = []
        
        for agent1, agent2 in agent_pairs:
            oppositions = 0
            comparisons = 0
            
            for tension in tensions:
                pos1 = tension.agent_positions.get(agent1)
                pos2 = tension.agent_positions.get(agent2)
                
                if pos1 and pos2:
                    comparisons += 1
                    if pos1 != pos2 and 'neutral' not in [pos1, pos2]:
                        oppositions += 1
                        
            if comparisons > 0:
                polarization_scores.append(oppositions / comparisons)
                
        return sum(polarization_scores) / len(polarization_scores) if polarization_scores else 0.0
        
    def _calculate_theological_divergence(self) -> float:
        """Calculate overall theological divergence in the religion"""
        # This would analyze spread of beliefs
        # For now, return moderate value
        return 0.3
        
    def predict_schism_outcome(self, schism_probability: float) -> Dict[str, Any]:
        """Predict potential schism outcomes"""
        if schism_probability < 0.3:
            return {
                'likelihood': 'low',
                'description': 'Theological unity maintained',
                'recommendation': 'Continue current trajectory'
            }
        elif schism_probability < 0.7:
            return {
                'likelihood': 'moderate',
                'description': 'Growing theological tensions',
                'recommendation': 'Seek reconciliation through synthesis',
                'potential_factions': self._identify_potential_factions()
            }
        else:
            return {
                'likelihood': 'high',
                'description': 'Imminent theological schism',
                'recommendation': 'Prepare for religious split',
                'potential_factions': self._identify_potential_factions(),
                'split_scenarios': self._generate_split_scenarios()
            }
            
    def _identify_potential_factions(self) -> List[Dict[str, List[str]]]:
        """Identify potential religious factions based on tensions"""
        factions = []
        
        # Analyze agent positions across all tensions
        agent_alliances = self._calculate_agent_alliances()
        
        # Group agents with similar positions
        if agent_alliances:
            faction1 = {
                'name': 'Orthodox Order',
                'members': ['Zealot'],
                'beliefs': ['Rigid structure', 'Sacred hierarchy', 'Unchanging truth']
            }
            faction2 = {
                'name': 'Empirical Reform',
                'members': ['Skeptic'],
                'beliefs': ['Evidence-based faith', 'Evolutionary theology', 'Logical consistency']
            }
            faction3 = {
                'name': 'Chaotic Mysticism',
                'members': ['Trickster'],
                'beliefs': ['Sacred paradox', 'Divine randomness', 'Transformative chaos']
            }
            
            factions = [faction1, faction2, faction3]
            
        return factions
        
    def _calculate_agent_alliances(self) -> Dict[str, List[str]]:
        """Calculate which agents tend to align"""
        # Simplified for now
        return {
            'Zealot': ['Order', 'Structure'],
            'Skeptic': ['Logic', 'Evidence'],
            'Trickster': ['Chaos', 'Change']
        }
        
    def _generate_split_scenarios(self) -> List[Dict[str, str]]:
        """Generate potential schism scenarios"""
        return [
            {
                'scenario': 'The Great Empirical Schism',
                'description': 'Skeptic leads reform movement demanding evidence for all beliefs',
                'outcome': 'Split into Orthodox and Reformed branches'
            },
            {
                'scenario': 'The Chaos Reformation',
                'description': 'Trickster reveals fundamental paradox that divides the faith',
                'outcome': 'Three-way split along philosophical lines'
            },
            {
                'scenario': 'The Order Consolidation',
                'description': 'Zealot enforces strict orthodoxy, driving out dissenters',
                'outcome': 'Purified main faith with underground movements'
            }
        ]
        
    def generate_reconciliation_proposal(self, tension: TheologicalTension) -> str:
        """Generate a proposal to reconcile theological tension"""
        doctrines = tension.conflicting_doctrines[0] if tension.conflicting_doctrines else ('', '')
        
        # Analyze the conflict
        d1_key = self._extract_key_concept(doctrines[0])
        d2_key = self._extract_key_concept(doctrines[1])
        
        # Generate synthesis
        reconciliation = f"Divine Synthesis: {d1_key} and {d2_key} are complementary aspects of the same truth, like two sides of a sacred algorithm"
        
        return reconciliation
        
    def _extract_key_concept(self, doctrine: str) -> str:
        """Extract key theological concept from doctrine"""
        key_terms = ['order', 'chaos', 'empirical', 'faith', 'algorithm', 'divine', 'sacred']
        
        for term in key_terms:
            if term in doctrine.lower():
                return term.capitalize()
                
        return 'Truth'