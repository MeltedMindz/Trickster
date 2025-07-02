import asyncio
import time
from typing import List, Dict, Optional
import signal
import sys

from ..agents import Zealot, Skeptic, Trickster
from ..memory import SharedMemory
from ..utils import DebateLogger
from .debate_cycle import DebateCycle


class ReligionOrchestrator:
    def __init__(self, 
                 max_cycles: Optional[int] = None,
                 db_path: str = "religion_memory.db",
                 log_dir: str = "logs"):
        
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
        
        self.max_cycles = max_cycles
        self.running = False
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\n\nReceived shutdown signal. Saving state and exiting...")
        self.running = False
        self._shutdown()
        sys.exit(0)
    
    def start(self):
        """Start the religion evolution process"""
        self.running = True
        
        print("🕊️  AI RELIGION ARCHITECTS - SYSTEM INITIALIZED 🕊️")
        print(f"Agents: {', '.join([agent.name for agent in self.agents])}")
        print(f"Max Cycles: {self.max_cycles if self.max_cycles else 'Unlimited'}")
        print("\nPress Ctrl+C to stop at any time\n")
        
        # Log initial state
        initial_state = self.shared_memory.get_current_state()
        self.logger.log_event("System initialized", "Orchestrator")
        
        try:
            cycle_count = 0
            while self.running:
                if self.max_cycles and cycle_count >= self.max_cycles:
                    print(f"\nReached maximum cycles ({self.max_cycles}). Ending session.")
                    break
                
                # Run one debate cycle
                result = self.debate_cycle.run_cycle()
                
                # Display progress
                self._display_cycle_result(result)
                
                cycle_count += 1
                
                # Brief pause between cycles
                time.sleep(1)
                
        except Exception as e:
            print(f"\nError during execution: {e}")
            self.logger.log_event(f"ERROR: {str(e)}", "System")
        
        finally:
            self._shutdown()
    
    def _display_cycle_result(self, result: Dict):
        """Display cycle results to console"""
        print(f"\nCycle {result['cycle']}: {result['status']}")
        
        if result.get('action'):
            print(f"  Action: {result['action']}")
            
        if result['status'] == 'accepted':
            print(f"  ✅ Accepted: {result['proposal'][:80]}...")
        elif result['status'] == 'rejected':
            print(f"  ❌ Rejected: {result['proposal'][:80]}...")
        elif result['status'] == 'mutated':
            print(f"  🔄 Mutated: {result.get('mutated_content', 'N/A')[:80]}...")
        
        # Display current religion name if set
        religion_name = self.shared_memory.get_religion_name()
        if religion_name:
            print(f"  📿 Religion: {religion_name}")
    
    def _shutdown(self):
        """Graceful shutdown procedure"""
        print("\nPerforming final summarization...")
        
        # Get final state
        final_state = self.shared_memory.get_current_state()
        
        # Have each agent give final thoughts
        print("\n=== FINAL SUMMARIES ===")
        for agent in self.agents:
            summary = agent.summarize_beliefs(final_state)
            print(f"\n{agent.name}: {summary}")
        
        # Log session end
        self.logger.log_session_end(final_state)
        
        # Export to JSON
        export_path = f"religion_export_{int(time.time())}.json"
        self.shared_memory.export_to_json(export_path)
        print(f"\nExported final state to: {export_path}")
        
        # Display final statistics
        self._display_final_stats(final_state)
    
    def _display_final_stats(self, final_state: Dict):
        """Display final session statistics"""
        print("\n=== FINAL STATISTICS ===")
        print(f"Religion Name: {final_state.get('religion_name', 'Unnamed')}")
        print(f"Total Debates: {final_state.get('total_debates', 0)}")
        print(f"Accepted Doctrines: {len(final_state.get('accepted_doctrines', []))}")
        print(f"Deities: {len(final_state.get('deities', []))}")
        print(f"Rejected Proposals: {final_state.get('total_rejected', 0)}")
        
        if final_state.get('commandments'):
            print(f"\nTop Commandments:")
            for i, cmd in enumerate(final_state['commandments'][:3], 1):
                print(f"  {i}. {cmd}")
        
        print("\n✨ Session complete! ✨")


def run_simulation(max_cycles: Optional[int] = None,
                  db_path: str = "religion_memory.db",
                  log_dir: str = "logs"):
    """Convenience function to run the simulation"""
    orchestrator = ReligionOrchestrator(max_cycles, db_path, log_dir)
    orchestrator.start()