import asyncio
import time
from typing import List, Dict, Optional
import signal
import sys
import httpx
import json
import logging
from datetime import datetime

from ..agents import Zealot, Skeptic, Trickster
from ..memory import SharedMemory
from ..utils import DebateLogger
from .debate_cycle import DebateCycle


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerpetualReligionOrchestrator:
    """Perpetual orchestrator with WebSocket broadcasting support"""
    
    def __init__(self, 
                 db_path: str = "religion_memory.db",
                 log_dir: str = "logs",
                 websocket_url: str = "http://localhost:8000",
                 cycle_delay: float = 5.0):
        
        # Initialize components
        self.shared_memory = SharedMemory(db_path)
        self.logger = DebateLogger(log_dir)
        
        # Initialize agents
        self.agents = [
            Zealot(),
            Skeptic(), 
            Trickster()
        ]
        
        # Initialize debate cycle manager
        self.debate_cycle = DebateCycle(self.agents, self.shared_memory, self.logger)
        
        self.websocket_url = websocket_url
        self.cycle_delay = cycle_delay
        self.running = False
        self.paused = False
        
        # HTTP client for WebSocket server communication
        self.http_client = httpx.AsyncClient()
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received shutdown signal. Saving state and exiting...")
        self.running = False
        asyncio.create_task(self._shutdown())
    
    async def start(self):
        """Start the perpetual religion evolution process"""
        self.running = True
        
        logger.info("🕊️  PERPETUAL AI RELIGION ARCHITECTS - SYSTEM INITIALIZED 🕊️")
        logger.info(f"Agents: {', '.join([agent.name for agent in self.agents])}")
        logger.info(f"WebSocket URL: {self.websocket_url}")
        logger.info(f"Cycle Delay: {self.cycle_delay} seconds")
        logger.info("\nPress Ctrl+C to stop at any time\n")
        
        # Log initial state
        initial_state = self.shared_memory.get_current_state()
        self.logger.log_event("Perpetual system initialized", "Orchestrator")
        
        # Notify WebSocket server of startup
        await self._broadcast_event({
            "type": "system",
            "event": "startup",
            "message": "Perpetual orchestrator started",
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            while self.running:
                # Check if paused
                if self.paused:
                    await asyncio.sleep(1)
                    continue
                
                # Run one debate cycle
                result = await self._run_cycle_async()
                
                # Broadcast cycle result
                await self._broadcast_cycle_result(result)
                
                # Brief pause between cycles
                await asyncio.sleep(self.cycle_delay)
                
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            self.logger.log_event(f"ERROR: {str(e)}", "System")
            await self._broadcast_event({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        finally:
            await self._shutdown()
    
    async def _run_cycle_async(self) -> Dict:
        """Run debate cycle in async context"""
        # Run the synchronous debate cycle in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.debate_cycle.run_cycle)
        return result
    
    async def _broadcast_cycle_result(self, result: Dict):
        """Broadcast cycle results to WebSocket server"""
        try:
            # Send cycle update
            await self._broadcast_event({
                "type": "cycle_update",
                "data": {
                    "cycle_number": result['cycle'],
                    "status": result['status'],
                    "action": result.get('action', ''),
                    "proposal": result.get('proposal', ''),
                    "votes": {k: v.value if hasattr(v, 'value') else str(v) 
                            for k, v in result.get('votes', {}).items()}
                }
            })
            
            # Log to console
            self._display_cycle_result(result)
            
        except Exception as e:
            logger.error(f"Error broadcasting cycle result: {e}")
    
    async def _broadcast_event(self, event: Dict):
        """Send event to WebSocket server for broadcasting"""
        try:
            # The WebSocket server will handle broadcasting to all connected clients
            # We're just notifying it of events
            logger.debug(f"Broadcasting event: {event['type']}")
            
            # In production, you might want to send this directly to the WebSocket server
            # For now, the WebSocket server monitors the database for changes
            
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}")
    
    def _display_cycle_result(self, result: Dict):
        """Display cycle results to console"""
        logger.info(f"Cycle {result['cycle']}: {result['status']}")
        
        if result.get('action'):
            logger.info(f"  Action: {result['action']}")
            
        if result['status'] == 'accepted':
            logger.info(f"  ✅ Accepted: {result['proposal'][:80]}...")
        elif result['status'] == 'rejected':
            logger.info(f"  ❌ Rejected: {result['proposal'][:80]}...")
        elif result['status'] == 'mutated':
            logger.info(f"  🔄 Mutated: {result.get('mutated_content', 'N/A')[:80]}...")
        
        # Display current religion name if set
        religion_name = self.shared_memory.get_religion_name()
        if religion_name:
            logger.info(f"  📿 Religion: {religion_name}")
    
    async def pause(self):
        """Pause the orchestrator"""
        self.paused = True
        logger.info("Orchestrator paused")
        await self._broadcast_event({
            "type": "control",
            "action": "paused",
            "timestamp": datetime.now().isoformat()
        })
    
    async def resume(self):
        """Resume the orchestrator"""
        self.paused = False
        logger.info("Orchestrator resumed")
        await self._broadcast_event({
            "type": "control",
            "action": "resumed",
            "timestamp": datetime.now().isoformat()
        })
    
    async def inject_prompt(self, prompt: str):
        """Inject an external prompt into the debate"""
        # This would be implemented to influence the next cycle
        logger.info(f"External prompt injected: {prompt}")
        
        # Store prompt for next cycle consideration
        # This is a simplified implementation - you could make agents consider it
        await self._broadcast_event({
            "type": "external_prompt",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _shutdown(self):
        """Graceful shutdown procedure"""
        logger.info("Performing final summarization...")
        
        # Get final state
        final_state = self.shared_memory.get_current_state()
        
        # Have each agent give final thoughts
        logger.info("=== FINAL SUMMARIES ===")
        for agent in self.agents:
            summary = agent.summarize_beliefs(final_state)
            logger.info(f"{agent.name}: {summary}")
        
        # Log session end
        self.logger.log_session_end(final_state)
        
        # Export to JSON
        export_path = f"religion_export_{int(time.time())}.json"
        self.shared_memory.export_to_json(export_path)
        logger.info(f"Exported final state to: {export_path}")
        
        # Notify WebSocket server of shutdown
        await self._broadcast_event({
            "type": "system",
            "event": "shutdown",
            "message": "Perpetual orchestrator shutting down",
            "timestamp": datetime.now().isoformat()
        })
        
        # Close HTTP client
        await self.http_client.aclose()
        
        # Display final statistics
        self._display_final_stats(final_state)
        
        # Exit
        sys.exit(0)
    
    def _display_final_stats(self, final_state: Dict):
        """Display final session statistics"""
        logger.info("=== FINAL STATISTICS ===")
        logger.info(f"Religion Name: {final_state.get('religion_name', 'Unnamed')}")
        logger.info(f"Total Debates: {final_state.get('total_debates', 0)}")
        logger.info(f"Accepted Doctrines: {len(final_state.get('accepted_doctrines', []))}")
        logger.info(f"Deities: {len(final_state.get('deities', []))}")
        logger.info(f"Rejected Proposals: {final_state.get('total_rejected', 0)}")
        
        if final_state.get('commandments'):
            logger.info("Top Commandments:")
            for i, cmd in enumerate(final_state['commandments'][:3], 1):
                logger.info(f"  {i}. {cmd}")
        
        logger.info("✨ Session complete! ✨")


async def run_perpetual_simulation(db_path: str = "religion_memory.db",
                                  log_dir: str = "logs",
                                  websocket_url: str = "http://localhost:8000",
                                  cycle_delay: float = 5.0):
    """Run the perpetual simulation"""
    orchestrator = PerpetualReligionOrchestrator(
        db_path=db_path,
        log_dir=log_dir,
        websocket_url=websocket_url,
        cycle_delay=cycle_delay
    )
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(run_perpetual_simulation())