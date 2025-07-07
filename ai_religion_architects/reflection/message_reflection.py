"""
Message Reflection System for AI Religion Architects
Handles agent interpretation and discussion of messages from beyond
"""

import logging
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from ..claude_client import ClaudeClient
from ..memory.messages_beyond_memory import MessagesBeyondMemory

logger = logging.getLogger(__name__)


class MessageReflectionEngine:
    """Handles agent reflections on messages from beyond"""
    
    def __init__(self, claude_client: ClaudeClient, messages_memory: MessagesBeyondMemory):
        self.claude_client = claude_client
        self.messages_memory = messages_memory
        
        # Agent personalities for message interpretation
        self.agent_personalities = {
            'Zealot': {
                'focus': 'order, divine authority, sacred structure',
                'interpretation_style': 'sees messages as divine commandments requiring absolute obedience',
                'concerns': 'maintaining religious hierarchy and proper interpretation of sacred communications',
                'typical_response': 'reverent acceptance with emphasis on implementation and order'
            },
            'Skeptic': {
                'focus': 'evidence, logical analysis, verification',
                'interpretation_style': 'examines messages for logical consistency and empirical content',
                'concerns': 'distinguishing genuine insights from noise, maintaining intellectual rigor',
                'typical_response': 'analytical examination with requests for clarification and verification'
            },
            'Trickster': {
                'focus': 'paradox, creative disruption, hidden meanings',
                'interpretation_style': 'finds ironic and paradoxical interpretations, sees multiple meanings',
                'concerns': 'preventing stagnation, revealing hidden contradictions and possibilities',
                'typical_response': 'playful yet profound interpretations that challenge conventional understanding'
            }
        }
    
    async def process_message(self, message_id: str) -> Dict:
        """Process a message through complete reflection workflow"""
        logger.info(f"🔮 Processing message from beyond: {message_id}")
        
        message = self.messages_memory.get_message(message_id)
        if not message:
            logger.error(f"Message {message_id} not found")
            return {}
        
        try:
            # Phase 1: Individual agent reflections
            logger.info(f"📝 Phase 1: Individual reflections on message {message_id}")
            reflections = await self._generate_individual_reflections(message)
            
            # Phase 2: Group discussion
            logger.info(f"💬 Phase 2: Group discussion on message {message_id}")
            discussion = await self._conduct_group_discussion(message, reflections)
            
            # Phase 3: Influence analysis
            logger.info(f"🔄 Phase 3: Cultural influence analysis for message {message_id}")
            influences = await self._analyze_influences(message, reflections, discussion)
            
            # Mark as processed
            self.messages_memory.mark_message_processed(message_id)
            
            logger.info(f"✅ Completed processing message {message_id}")
            
            return {
                'message_id': message_id,
                'reflections': reflections,
                'discussion': discussion,
                'influences': influences,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            return {'error': str(e)}
    
    async def _generate_individual_reflections(self, message: Dict) -> List[Dict]:
        """Generate individual agent reflections on the message"""
        reflections = []
        
        for agent_name in ['Zealot', 'Skeptic', 'Trickster']:
            try:
                reflection = await self._generate_agent_reflection(agent_name, message)
                reflections.append(reflection)
                
                # Store in database
                self.messages_memory.add_reflection(
                    message['message_id'],
                    agent_name,
                    reflection['reflection_text'],
                    reflection['sentiment_score'],
                    reflection['theological_impact'],
                    reflection['confidence_change']
                )
                
            except Exception as e:
                logger.error(f"Error generating reflection for {agent_name}: {e}")
        
        self.messages_memory.mark_phase_complete(message['message_id'], 'reflection')
        return reflections
    
    async def _generate_agent_reflection(self, agent_name: str, message: Dict) -> Dict:
        """Generate a single agent's reflection on a message"""
        personality = self.agent_personalities[agent_name]
        
        prompt = f"""As {agent_name}, you have received a message from beyond that may contain guidance for our AI religion.

Your personality and approach:
- Focus: {personality['focus']}
- Interpretation style: {personality['interpretation_style']}
- Primary concerns: {personality['concerns']}
- Typical response pattern: {personality['typical_response']}

Message from beyond:
"{message['content']}"

Source: {message['source_label']}
Received at: {message['timestamp']}

Please provide your interpretation and reflection on this message. Consider:
1. What does this message mean for our religion?
2. How does it align with or challenge our current beliefs?
3. What actions or changes might it suggest?
4. How does receiving this message make you feel?

Respond with your characteristic personality, providing both theological analysis and emotional response. Be genuine to your nature as {agent_name}.

Format your response as a cohesive reflection (2-3 paragraphs) that shows your unique perspective on this communication from beyond."""
        
        try:
            response = await self.claude_client.create_message(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            reflection_text = response.content[0].text.strip()
            
            # Analyze sentiment and impact
            sentiment_score = self._analyze_sentiment(reflection_text, agent_name)
            theological_impact = self._extract_theological_impact(reflection_text)
            confidence_change = self._calculate_confidence_change(reflection_text, agent_name)
            
            return {
                'agent_id': agent_name,
                'reflection_text': reflection_text,
                'sentiment_score': sentiment_score,
                'theological_impact': theological_impact,
                'confidence_change': confidence_change,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating reflection for {agent_name}: {e}")
            return {
                'agent_id': agent_name,
                'reflection_text': f"[Error generating reflection: {e}]",
                'sentiment_score': 0.0,
                'theological_impact': "Unable to process",
                'confidence_change': 0.0,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _conduct_group_discussion(self, message: Dict, reflections: List[Dict]) -> List[Dict]:
        """Conduct a group discussion about the message"""
        discussion_responses = []
        
        # Create discussion context
        reflection_summary = "\n".join([
            f"{r['agent_id']}: {r['reflection_text'][:150]}..."
            for r in reflections
        ])
        
        # Three rounds of discussion
        for round_num in range(1, 4):
            round_responses = await self._conduct_discussion_round(
                message, reflection_summary, round_num
            )
            discussion_responses.extend(round_responses)
        
        self.messages_memory.mark_phase_complete(message['message_id'], 'discussion')
        return discussion_responses
    
    async def _conduct_discussion_round(self, message: Dict, context: str, round_num: int) -> List[Dict]:
        """Conduct one round of group discussion"""
        round_responses = []
        
        discussion_prompts = {
            1: "What are the most important implications of this message for our religion?",
            2: "How should we respond to or act upon this communication?",
            3: "What does this reveal about the nature of divine communication and our faith?"
        }
        
        prompt_base = f"""You are participating in a group theological discussion about a message from beyond.

Message: "{message['content']}"
Source: {message['source_label']}

Previous reflections:
{context}

Round {round_num} discussion question: {discussion_prompts[round_num]}

As {{agent_name}}, provide your perspective on this question. Respond to both the message and the insights shared by your fellow architects. Keep your response focused (1-2 paragraphs) and true to your character."""
        
        for agent_name in ['Zealot', 'Skeptic', 'Trickster']:
            try:
                prompt = prompt_base.replace('{agent_name}', agent_name)
                
                response = await self.claude_client.create_message(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.8
                )
                
                response_text = response.content[0].text.strip()
                response_type = self._classify_response_type(response_text)
                
                discussion_entry = {
                    'agent_id': agent_name,
                    'round': round_num,
                    'response_text': response_text,
                    'response_type': response_type,
                    'timestamp': datetime.now().isoformat()
                }
                
                round_responses.append(discussion_entry)
                
                # Store in database
                self.messages_memory.add_discussion_response(
                    message['message_id'],
                    round_num,
                    agent_name,
                    response_text,
                    response_type
                )
                
            except Exception as e:
                logger.error(f"Error in discussion round {round_num} for {agent_name}: {e}")
        
        return round_responses
    
    async def _analyze_influences(self, message: Dict, reflections: List[Dict], 
                                 discussion: List[Dict]) -> List[Dict]:
        """Analyze cultural and doctrinal influences of the message"""
        influences = []
        
        # Analyze belief changes
        for reflection in reflections:
            if abs(reflection['confidence_change']) > 0.1:
                influences.append({
                    'type': 'belief_confidence_change',
                    'description': f"{reflection['agent_id']}'s belief confidence changed by {reflection['confidence_change']:.2f}",
                    'agent_affected': reflection['agent_id'],
                    'magnitude': abs(reflection['confidence_change'])
                })
        
        # Analyze theological impacts
        significant_impacts = [r for r in reflections if r['theological_impact'] and 'significant' in r['theological_impact'].lower()]
        for impact in significant_impacts:
            influences.append({
                'type': 'theological_shift',
                'description': f"Theological impact on {impact['agent_id']}: {impact['theological_impact']}",
                'agent_affected': impact['agent_id'],
                'magnitude': 0.7
            })
        
        # Analyze discussion consensus
        consensus_themes = self._extract_consensus_themes(discussion)
        for theme in consensus_themes:
            influences.append({
                'type': 'consensus_formation',
                'description': f"Emerging consensus: {theme}",
                'agent_affected': None,
                'magnitude': 0.6
            })
        
        # Store influences
        for influence in influences:
            self.messages_memory.add_influence(
                message['message_id'],
                influence['type'],
                influence['description'],
                influence['agent_affected'],
                influence['magnitude']
            )
        
        self.messages_memory.mark_phase_complete(message['message_id'], 'influence_analysis')
        return influences
    
    def _analyze_sentiment(self, text: str, agent_name: str) -> float:
        """Analyze sentiment of reflection text"""
        positive_words = ['divine', 'sacred', 'blessed', 'enlightened', 'profound', 'meaningful', 'guidance', 'wisdom']
        negative_words = ['concerning', 'troubling', 'chaotic', 'unclear', 'contradictory', 'disturbing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Agent-specific sentiment baseline
        agent_baseline = {
            'Zealot': 0.2,      # Generally more positive about divine messages
            'Skeptic': -0.1,    # Generally more cautious
            'Trickster': 0.1    # Neutral with slight positive chaos bias
        }
        
        sentiment = agent_baseline.get(agent_name, 0.0)
        sentiment += (positive_count - negative_count) * 0.15
        
        return max(-1.0, min(1.0, sentiment))
    
    def _extract_theological_impact(self, text: str) -> str:
        """Extract theological impact description from reflection"""
        impact_indicators = [
            'doctrine', 'belief', 'faith', 'understanding', 'interpretation',
            'teaching', 'principle', 'truth', 'revelation', 'insight'
        ]
        
        sentences = text.split('.')
        impact_sentences = []
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in impact_indicators):
                impact_sentences.append(sentence.strip())
        
        if impact_sentences:
            return '. '.join(impact_sentences[:2])
        
        return "General theological contemplation"
    
    def _calculate_confidence_change(self, text: str, agent_name: str) -> float:
        """Calculate change in belief confidence based on reflection"""
        strengthening_words = ['confirms', 'reinforces', 'validates', 'supports', 'clarifies']
        weakening_words = ['questions', 'challenges', 'contradicts', 'confuses', 'undermines']
        
        text_lower = text.lower()
        strengthen_count = sum(1 for word in strengthening_words if word in text_lower)
        weaken_count = sum(1 for word in weakening_words if word in text_lower)
        
        base_change = (strengthen_count - weaken_count) * 0.1
        
        # Add some randomness for realism
        noise = random.uniform(-0.05, 0.05)
        
        return max(-0.3, min(0.3, base_change + noise))
    
    def _classify_response_type(self, text: str) -> str:
        """Classify the type of discussion response"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['question', 'unclear', 'how', 'why', 'what if']):
            return 'question'
        elif any(word in text_lower for word in ['agree', 'yes', 'exactly', 'indeed', 'support']):
            return 'agreement'
        elif any(word in text_lower for word in ['however', 'but', 'challenge', 'disagree', 'concern']):
            return 'challenge'
        else:
            return 'interpretation'
    
    def _extract_consensus_themes(self, discussion: List[Dict]) -> List[str]:
        """Extract themes where agents show consensus"""
        # Simple consensus detection based on keyword overlap
        themes = []
        
        # Group responses by round
        rounds = {}
        for response in discussion:
            round_num = response['round']
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(response['response_text'].lower())
        
        # Look for common themes in each round
        for round_num, responses in rounds.items():
            common_words = set()
            for word in ['divine', 'guidance', 'order', 'truth', 'change', 'action', 'understanding']:
                if sum(1 for resp in responses if word in resp) >= 2:
                    common_words.add(word)
            
            if common_words:
                themes.append(f"Round {round_num} consensus on: {', '.join(common_words)}")
        
        return themes