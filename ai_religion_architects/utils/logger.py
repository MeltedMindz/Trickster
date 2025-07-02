import os
from datetime import datetime
from typing import Dict, Any
import json


class DebateLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create session log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = os.path.join(log_dir, f"debate_session_{timestamp}.log")
        self.transcript_file = os.path.join(log_dir, f"transcript_{timestamp}.txt")
        
        self._write_header()
    
    def _write_header(self):
        """Write session header"""
        header = f"""
{'='*80}
AI RELIGION ARCHITECTS - DEBATE SESSION
Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

"""
        with open(self.session_file, 'w') as f:
            f.write(header)
        with open(self.transcript_file, 'w') as f:
            f.write(header)
    
    def log_cycle_start(self, cycle_number: int):
        """Log the start of a debate cycle"""
        message = f"\n{'='*60}\nCYCLE {cycle_number} BEGINNING\n{'='*60}\n"
        self._write_to_files(message)
    
    def log_proposal(self, proposal: Any):
        """Log a proposal"""
        message = f"""
PROPOSAL by {proposal.author}:
Type: {proposal.type.value}
Content: {proposal.content}
Details: {json.dumps(proposal.details, indent=2)}
"""
        self._write_to_files(message)
    
    def log_challenge(self, challenger: str, response: str):
        """Log a challenge response"""
        message = f"\nCHALLENGE by {challenger}:\n{response}\n"
        self._write_to_files(message)
    
    def log_trickster_chaos(self, response: str):
        """Log Trickster's chaos injection"""
        message = f"\n🎲 TRICKSTER CHAOS 🎲:\n{response}\n"
        self._write_to_files(message)
    
    def log_votes(self, votes: Dict[str, Any]):
        """Log voting results"""
        message = "\nVOTING RESULTS:\n"
        for agent, vote in votes.items():
            message += f"  {agent}: {vote.value}\n"
        self._write_to_files(message)
    
    def log_mutation(self, agent: str, mutation: str):
        """Log a mutation proposal"""
        message = f"\nMUTATION by {agent}:\n{mutation}\n"
        self._write_to_files(message)
    
    def log_event(self, event: str, source: str):
        """Log a special event"""
        message = f"\n[{source}] {event}\n"
        self._write_to_files(message)
    
    def log_summary(self, agent: str, summary: str):
        """Log agent summary"""
        message = f"\nSUMMARY by {agent}:\n{summary}\n"
        self._write_to_files(message)
    
    def _write_to_files(self, message: str):
        """Write to both log files"""
        # Write to detailed log
        with open(self.session_file, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
        # Write to transcript (cleaner format)
        with open(self.transcript_file, 'a') as f:
            f.write(message)
    
    def log_session_end(self, final_state: Dict):
        """Log session end with final state"""
        message = f"""

{'='*80}
SESSION ENDED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
FINAL STATE:
{json.dumps(final_state, indent=2, default=str)}
{'='*80}
"""
        self._write_to_files(message)