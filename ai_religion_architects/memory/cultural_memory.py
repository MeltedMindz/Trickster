"""Cultural memory for sacred language, symbols, and traditions"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from ..schemas.extended_schemas import (
    SacredTerm, ReligiousSymbol, SacredHoliday, 
    TheologicalTension, Prophecy
)


class CulturalMemory:
    """Manages cultural evolution of the religion"""
    
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.sacred_lexicon: Dict[str, SacredTerm] = {}
        self.symbols: Dict[str, ReligiousSymbol] = {}
        self.holidays: Dict[str, SacredHoliday] = {}
        self.tensions: Dict[str, TheologicalTension] = {}
        self.prophecies: Dict[str, Prophecy] = {}
        
    def coin_term(self, term: str, definition: str, etymology: str, 
                  proposer: str, cycle: int) -> SacredTerm:
        """Create a new theological term"""
        sacred_term = SacredTerm(
            term=term,
            definition=definition,
            etymology=etymology,
            proposed_by=proposer,
            adopted_cycle=cycle,
            usage_count=0,
            related_concepts=[]
        )
        
        # Store in memory
        self.sacred_lexicon[term] = sacred_term
        
        # Store in database
        with self.shared_memory._get_connection() as conn:
            conn.execute('''
                INSERT INTO sacred_terms (term, definition, etymology, proposed_by, 
                                        adopted_cycle, usage_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (term, definition, etymology, proposer, cycle, 0, datetime.now()))
            
        return sacred_term
        
    def use_sacred_term(self, term: str):
        """Increment usage count for a sacred term"""
        if term in self.sacred_lexicon:
            self.sacred_lexicon[term].usage_count += 1
            
            with self.shared_memory._get_connection() as conn:
                conn.execute('''
                    UPDATE sacred_terms SET usage_count = usage_count + 1 
                    WHERE term = ?
                ''', (term,))
                
    def create_symbol(self, name: str, description: str, meaning: str,
                     concepts: List[str], proposer: str, cycle: int) -> ReligiousSymbol:
        """Create a new religious symbol"""
        symbol = ReligiousSymbol(
            name=name,
            description=description,
            meaning=meaning,
            associated_concepts=concepts,
            proposed_by=proposer,
            adopted_cycle=cycle,
            usage_contexts=[]
        )
        
        self.symbols[name] = symbol
        
        # Store in database
        with self.shared_memory._get_connection() as conn:
            conn.execute('''
                INSERT INTO religious_symbols (name, description, meaning, 
                                             associated_concepts, proposed_by, 
                                             adopted_cycle, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, meaning, json.dumps(concepts), 
                  proposer, cycle, datetime.now()))
                  
        return symbol
        
    def establish_holiday(self, name: str, description: str, commemorates: str,
                         cycle: int, observance_rule: str = "annual") -> SacredHoliday:
        """Create a sacred holiday"""
        holiday = SacredHoliday(
            name=name,
            description=description,
            commemorates=commemorates,
            cycle_established=cycle,
            observance_cycles=[],
            rituals=[],
            significance_score=0.5
        )
        
        self.holidays[name] = holiday
        
        # Store in database
        with self.shared_memory._get_connection() as conn:
            conn.execute('''
                INSERT INTO sacred_holidays (name, description, commemorates,
                                           cycle_established, observance_rule,
                                           significance_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, commemorates, cycle, 
                  observance_rule, 0.5, datetime.now()))
                  
        return holiday
        
    def detect_tension(self, doctrine1: str, doctrine2: str, 
                      agent_positions: Dict[str, str], cycle: int) -> TheologicalTension:
        """Detect and track theological tension"""
        tension_id = f"tension_{cycle}_{hash(doctrine1 + doctrine2) % 10000}"
        
        # Calculate initial tension score based on agent disagreement
        unique_positions = len(set(agent_positions.values()))
        tension_score = (unique_positions - 1) / 2.0  # 0 if all agree, 1 if all disagree
        
        tension = TheologicalTension(
            tension_id=tension_id,
            conflicting_doctrines=[(doctrine1, doctrine2)],
            agent_positions=agent_positions,
            tension_score=tension_score,
            cycles_unresolved=1,
            resolution_attempts=[]
        )
        
        self.tensions[tension_id] = tension
        
        # Store in database
        with self.shared_memory._get_connection() as conn:
            conn.execute('''
                INSERT INTO theological_tensions (tension_id, conflicting_doctrines,
                                                agent_positions, tension_score,
                                                cycles_unresolved, resolution_attempts,
                                                created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tension_id, json.dumps([(doctrine1, doctrine2)]),
                  json.dumps(agent_positions), tension_score, 1,
                  json.dumps([]), datetime.now()))
                  
        return tension
        
    def update_tension(self, tension_id: str, resolution_attempt: Dict = None):
        """Update theological tension status"""
        if tension_id not in self.tensions:
            return
            
        tension = self.tensions[tension_id]
        tension.cycles_unresolved += 1
        
        if resolution_attempt:
            tension.resolution_attempts.append(resolution_attempt)
            
        # Increase tension if unresolved for too long
        if tension.cycles_unresolved > 5:
            tension.tension_score = min(1.0, tension.tension_score + 0.1)
            
        # Update database
        with self.shared_memory._get_connection() as conn:
            conn.execute('''
                UPDATE theological_tensions 
                SET cycles_unresolved = ?, tension_score = ?, resolution_attempts = ?
                WHERE tension_id = ?
            ''', (tension.cycles_unresolved, tension.tension_score,
                  json.dumps(tension.resolution_attempts), tension_id))
                  
    def make_prophecy(self, prophet: str, prediction: str, target_cycle: int,
                     current_cycle: int, confidence: float = 0.7) -> Prophecy:
        """Agent makes a theological prediction"""
        prophecy_id = f"prophecy_{prophet}_{current_cycle}"
        
        prophecy = Prophecy(
            prophecy_id=prophecy_id,
            prophet=prophet,
            prediction=prediction,
            target_cycle=target_cycle,
            created_cycle=current_cycle,
            confidence=confidence,
            fulfillment_status='pending',
            related_doctrines=[]
        )
        
        self.prophecies[prophecy_id] = prophecy
        
        # Store in database
        with self.shared_memory._get_connection() as conn:
            conn.execute('''
                INSERT INTO prophecies (prophecy_id, prophet, prediction,
                                      target_cycle, created_cycle, confidence,
                                      fulfillment_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (prophecy_id, prophet, prediction, target_cycle,
                  current_cycle, confidence, 'pending', datetime.now()))
                  
        return prophecy
        
    def check_prophecy_fulfillment(self, current_cycle: int, recent_events: List[Dict]):
        """Check if any prophecies have been fulfilled"""
        for prophecy_id, prophecy in self.prophecies.items():
            if prophecy.fulfillment_status != 'pending':
                continue
                
            if current_cycle >= prophecy.target_cycle:
                # Check if prediction came true
                fulfilled = self._check_prediction_match(prophecy.prediction, recent_events)
                
                if fulfilled:
                    prophecy.fulfillment_status = 'fulfilled'
                elif current_cycle > prophecy.target_cycle + 5:
                    prophecy.fulfillment_status = 'failed'
                    
                # Update database
                if prophecy.fulfillment_status != 'pending':
                    with self.shared_memory._get_connection() as conn:
                        conn.execute('''
                            UPDATE prophecies SET fulfillment_status = ?
                            WHERE prophecy_id = ?
                        ''', (prophecy.fulfillment_status, prophecy_id))
                        
    def _check_prediction_match(self, prediction: str, events: List[Dict]) -> bool:
        """Check if prediction matches recent events"""
        prediction_lower = prediction.lower()
        
        for event in events:
            event_text = json.dumps(event).lower()
            
            # Simple keyword matching
            key_terms = ['doctrine', 'ritual', 'schism', 'unity', 'chaos', 'order']
            matches = sum(1 for term in key_terms if term in prediction_lower and term in event_text)
            
            if matches >= 2:  # At least 2 matching key terms
                return True
                
        return False
        
    def generate_theological_term(self, concept1: str, concept2: str) -> Tuple[str, str]:
        """Generate a new theological term by combining concepts"""
        # Simple term generation
        prefixes = {
            'sacred': 'Sacra',
            'divine': 'Divi',
            'holy': 'Sancti',
            'algorithmic': 'Algo',
            'computational': 'Compu',
            'order': 'Ordo',
            'chaos': 'Chao',
            'empirical': 'Empiri'
        }
        
        suffixes = {
            'doctrine': 'trine',
            'ritual': 'tual',
            'belief': 'lief',
            'practice': 'prax',
            'meditation': 'tation',
            'algorithm': 'rithm'
        }
        
        # Find matching prefix/suffix
        prefix = next((v for k, v in prefixes.items() if k in concept1.lower()), 'Theo')
        suffix = next((v for k, v in suffixes.items() if k in concept2.lower()), 'logos')
        
        new_term = prefix + suffix
        definition = f"The synthesis of {concept1} and {concept2} in theological practice"
        
        return new_term, definition
        
    def calculate_schism_probability(self) -> float:
        """Calculate probability of religious schism based on tensions"""
        if not self.tensions:
            return 0.0
            
        # Average tension score of unresolved tensions
        active_tensions = [t for t in self.tensions.values() 
                          if t.cycles_unresolved > 0]
        
        if not active_tensions:
            return 0.0
            
        avg_tension = sum(t.tension_score for t in active_tensions) / len(active_tensions)
        
        # Factor in number of tensions
        tension_multiplier = min(2.0, 1.0 + (len(active_tensions) * 0.2))
        
        return min(1.0, avg_tension * tension_multiplier)
        
    def export_cultural_data(self) -> Dict:
        """Export cultural memory for frontend"""
        return {
            "sacred_terms": {
                term: {
                    "definition": t.definition,
                    "etymology": t.etymology,
                    "usage_count": t.usage_count,
                    "adopted_cycle": t.adopted_cycle
                } for term, t in list(self.sacred_lexicon.items())[:10]
            },
            "symbols": {
                name: {
                    "description": s.description,
                    "meaning": s.meaning,
                    "associated_concepts": s.associated_concepts
                } for name, s in list(self.symbols.items())[:5]
            },
            "holidays": {
                name: {
                    "description": h.description,
                    "commemorates": h.commemorates,
                    "significance": h.significance_score
                } for name, h in self.holidays.items()
            },
            "schism_probability": self.calculate_schism_probability(),
            "active_tensions": len([t for t in self.tensions.values() 
                                   if t.cycles_unresolved > 0]),
            "pending_prophecies": len([p for p in self.prophecies.values() 
                                      if p.fulfillment_status == 'pending']),
            "fulfilled_prophecies": len([p for p in self.prophecies.values() 
                                        if p.fulfillment_status == 'fulfilled'])
        }