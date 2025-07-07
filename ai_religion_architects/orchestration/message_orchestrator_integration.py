"""
Message Processing Integration for Claude Religion Orchestrator
Adds message from beyond processing capabilities to the main orchestrator
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..memory.messages_beyond_memory import MessagesBeyondMemory
from ..reflection.message_reflection import MessageReflectionEngine
from ..claude_client import get_claude_client

logger = logging.getLogger(__name__)


class MessageOrchestratorIntegration:
    """Integration module for adding message processing to the main orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.messages_memory = MessagesBeyondMemory(orchestrator.db_path)
        self.claude_client = None
        self.reflection_engine = None
        
        # Message processing state
        self.message_processing_active = False
        self.last_message_check = None
    
    async def initialize(self):
        """Initialize message processing components"""
        self.claude_client = get_claude_client()
        self.reflection_engine = MessageReflectionEngine(
            self.claude_client,
            self.messages_memory
        )
        logger.info("✅ Message processing system initialized")
    
    async def check_and_process_messages(self):
        """Check for new messages and process them"""
        if self.message_processing_active:
            logger.debug("Message processing already active, skipping")
            return
        
        try:
            self.message_processing_active = True
            unprocessed_messages = self.messages_memory.get_unprocessed_messages()
            
            if not unprocessed_messages:
                return
            
            logger.info(f"🔮 Found {len(unprocessed_messages)} unprocessed messages from beyond")
            
            for message in unprocessed_messages:
                await self.process_single_message(message)
            
        except Exception as e:
            logger.error(f"Error in message processing: {e}")
        finally:
            self.message_processing_active = False
            self.last_message_check = datetime.now()
    
    async def process_single_message(self, message: Dict):
        """Process a single message through the reflection system"""
        message_id = message['message_id']
        logger.info(f"📜 Processing message {message_id}: {message['content'][:50]}...")
        
        try:
            # Check if this should interrupt current cycle
            if await self.should_interrupt_cycle(message):
                logger.info(f"🚨 Message {message_id} triggering cycle interruption")
                await self.interrupt_current_cycle(message)
            
            # Process the message through reflection engine
            result = await self.reflection_engine.process_message(message_id)
            
            if result and 'error' not in result:
                logger.info(f"✅ Successfully processed message {message_id}")
                
                # Update agent memories with influences
                await self.apply_message_influences(result)
                
                # Export updated data for frontend
                await self.orchestrator._export_static_data()
                
            else:
                logger.error(f"❌ Failed to process message {message_id}: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
    
    async def should_interrupt_cycle(self, message: Dict) -> bool:
        """Determine if a message should interrupt the current debate cycle"""
        # Check message priority keywords
        urgent_keywords = ['urgent', 'immediate', 'crisis', 'emergency', 'now']
        content_lower = message['content'].lower()
        
        if any(keyword in content_lower for keyword in urgent_keywords):
            return True
        
        # Check if message is very short (might be command-like)
        if len(message['content'].strip()) < 50:
            return True
        
        # Default: don't interrupt, process between cycles
        return False
    
    async def interrupt_current_cycle(self, message: Dict):
        """Interrupt current cycle to process urgent message"""
        logger.info(f"⚡ Interrupting current cycle for urgent message: {message['message_id']}")
        
        # Log the interruption
        interruption_log = {
            'type': 'message_interruption',
            'message_id': message['message_id'],
            'cycle_number': self.orchestrator.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'reason': 'Urgent message from beyond'
        }
        
        # Store interruption in shared memory
        self.orchestrator.shared_memory.add_evolution_milestone(
            'system_interruption',
            f"Cycle {self.orchestrator.cycle_count} interrupted by message {message['message_id']}",
            json.dumps(interruption_log)
        )
    
    async def apply_message_influences(self, processing_result: Dict):
        """Apply message influences to agent memories and beliefs"""
        if 'influences' not in processing_result:
            return
        
        for influence in processing_result['influences']:
            try:
                await self.apply_single_influence(influence, processing_result['message_id'])
            except Exception as e:
                logger.error(f"Error applying influence: {e}")
    
    async def apply_single_influence(self, influence: Dict, message_id: str):
        """Apply a single influence to the appropriate agent or system"""
        influence_type = influence['type']
        magnitude = influence['magnitude']
        agent_affected = influence.get('agent_affected')
        
        if influence_type == 'belief_confidence_change' and agent_affected:
            # Update agent's belief confidence
            await self.update_agent_confidence(agent_affected, magnitude, message_id)
        
        elif influence_type == 'theological_shift' and agent_affected:
            # Record theological shift in agent memory
            await self.record_theological_shift(agent_affected, influence['description'], message_id)
        
        elif influence_type == 'consensus_formation':
            # Update cultural memory with consensus
            await self.record_consensus(influence['description'], message_id)
    
    async def update_agent_confidence(self, agent_name: str, magnitude: float, message_id: str):
        """Update an agent's belief confidence based on message influence"""
        try:
            # Get agent memory if available
            if agent_name in self.orchestrator.agent_memories:
                agent_memory = self.orchestrator.agent_memories[agent_name]
                
                # Update personality traits related to confidence
                if hasattr(agent_memory, 'update_trait_strength'):
                    confidence_change = magnitude * 0.1  # Scale influence
                    agent_memory.update_trait_strength('certainty', confidence_change)
                    
                    logger.info(f"📈 Updated {agent_name}'s certainty by {confidence_change:.3f} due to message {message_id}")
        
        except Exception as e:
            logger.error(f"Error updating {agent_name}'s confidence: {e}")
    
    async def record_theological_shift(self, agent_name: str, description: str, message_id: str):
        """Record a theological shift in agent memory"""
        try:
            # Add to agent's debate memories as a significant event
            if agent_name in self.orchestrator.agent_memories:
                agent_memory = self.orchestrator.agent_memories[agent_name]
                
                if hasattr(agent_memory, 'add_debate_memory'):
                    agent_memory.add_debate_memory(
                        cycle_number=self.orchestrator.cycle_count,
                        topic=f"Message from Beyond ({message_id})",
                        outcome='THEOLOGICAL_SHIFT',
                        satisfaction=0.8,  # Generally positive about divine guidance
                        insights=description
                    )
                    
                    logger.info(f"📚 Recorded theological shift for {agent_name}: {description[:50]}...")
        
        except Exception as e:
            logger.error(f"Error recording theological shift for {agent_name}: {e}")
    
    async def record_consensus(self, description: str, message_id: str):
        """Record consensus formation in cultural memory"""
        try:
            # Add to cultural memory as an evolution milestone
            self.orchestrator.cultural_memory.add_cultural_artifact(
                artifact_type='consensus',
                content=description,
                created_by='collective_interpretation',
                context=f"Message interpretation: {message_id}"
            )
            
            logger.info(f"🤝 Recorded consensus formation: {description[:50]}...")
        
        except Exception as e:
            logger.error(f"Error recording consensus: {e}")
    
    def get_message_stats(self) -> Dict:
        """Get statistics about message processing"""
        try:
            messages = self.messages_memory.get_recent_messages(20, True)
            total_messages = len(messages)
            processed_messages = len([m for m in messages if m['processed']])
            
            return {
                'total_messages': total_messages,
                'processed_messages': processed_messages,
                'pending_messages': total_messages - processed_messages,
                'last_check': self.last_message_check.isoformat() if self.last_message_check else None,
                'processing_active': self.message_processing_active
            }
        except Exception as e:
            logger.error(f"Error getting message stats: {e}")
            return {'error': str(e)}
    
    async def export_messages_for_frontend(self) -> Dict:
        """Export message data for frontend display"""
        try:
            return self.messages_memory.export_messages_data()
        except Exception as e:
            logger.error(f"Error exporting messages for frontend: {e}")
            return {'error': str(e), 'messages': [], 'agent_stats': {}}