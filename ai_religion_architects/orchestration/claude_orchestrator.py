import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import signal
import sys
import json
import subprocess
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore

from ..config import Config
from ..claude_client import get_claude_client, close_claude_client
from ..memory import SharedMemory
from ..utils import DebateLogger

# Configure logging
logger = logging.getLogger(__name__)


class ClaudeReligionOrchestrator:
    """Orchestrator that uses Claude API with APScheduler for hourly cycles"""
    
    def __init__(self, 
                 db_path: Optional[str] = None,
                 log_dir: Optional[str] = None):
        
        # Initialize configuration
        self.db_path = db_path or Config.DB_PATH
        self.log_dir = log_dir or Config.LOG_DIR
        
        # Initialize components
        self.shared_memory = SharedMemory(self.db_path)
        self.logger = DebateLogger(self.log_dir)
        
        # Agent names for the debate system
        self.agent_names = ["Zealot", "Skeptic", "Trickster"]
        self.current_proposer_index = 0
        
        # Initialize APScheduler
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': AsyncIOExecutor()},
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 300  # 5 minutes grace time
            }
        )
        
        # Track state
        self.running = False
        self.cycle_count = self.shared_memory.get_current_cycle_number()
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received shutdown signal {signum}. Initiating graceful shutdown...")
        self.running = False
        asyncio.create_task(self.shutdown())
    
    async def start(self):
        """Start the orchestrator with APScheduler"""
        if self.running:
            logger.warning("Orchestrator is already running")
            return
        
        self.running = True
        
        logger.info("🕊️  CLAUDE AI RELIGION ARCHITECTS - STARTING 🕊️")
        logger.info(f"Cycle Interval: {Config.CYCLE_INTERVAL_HOURS} hour(s)")
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Claude Model: {Config.CLAUDE_MODEL}")
        logger.info(f"Max Tokens: {Config.CLAUDE_MAX_TOKENS}")
        
        # Initialize Claude client
        try:
            self.claude_client = await get_claude_client()
            logger.info("✅ Claude API client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude client: {e}")
            raise
        
        # Start health monitoring
        from ai_religion_architects.utils.health_check import SystemHealthMonitor
        self.health_monitor = SystemHealthMonitor(self.shared_memory, self.log_dir)
        
        # Start periodic health checks (every 5 minutes)
        asyncio.create_task(self.health_monitor.periodic_health_check(300))
        logger.info("🏥 Health monitoring started")
        
        # Run initial health check
        health_report = self.health_monitor.check_system_health()
        logger.info(f"📊 Initial system health: {health_report['overall_status']}")
        
        # Log initial state
        initial_state = self.shared_memory.get_current_state()
        self.logger.log_event("Claude orchestrator initialized", "System")
        
        # Schedule the debate cycle job
        self.scheduler.add_job(
            func=self._run_scheduled_cycle,
            trigger=IntervalTrigger(hours=Config.CYCLE_INTERVAL_HOURS),
            id='debate_cycle',
            name='AI Religion Debate Cycle',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on start
        )
        
        # Start the scheduler
        self.scheduler.start()
        logger.info(f"✅ Scheduler started - next cycle in {Config.CYCLE_INTERVAL_HOURS} hour(s)")
        
        # Log startup to memory
        self.shared_memory.add_evolution_milestone(
            milestone_type="system_start",
            description="Claude-powered orchestrator started",
            cycle_number=0
        )
        
        try:
            # Keep the main thread alive
            while self.running:
                await asyncio.sleep(1)
                
                # Check scheduler status
                if not self.scheduler.running:
                    logger.error("Scheduler stopped unexpectedly")
                    break
                    
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def _run_scheduled_cycle(self):
        """Run a single debate cycle (called by APScheduler)"""
        if not self.running:
            logger.info("Skipping cycle - orchestrator is shutting down")
            return
        
        self.cycle_count += 1
        cycle_start_time = datetime.now()
        
        logger.info(f"🔄 Starting debate cycle {self.cycle_count}")
        self.logger.log_cycle_start(self.cycle_count)
        
        try:
            # Get current state for context
            current_state = self.shared_memory.get_summary_for_agents()
            
            # Phase 1: Proposal
            proposer_name = self.agent_names[self.current_proposer_index]
            logger.info(f"📝 {proposer_name} generating proposal...")
            
            proposal = await self.claude_client.generate_proposal(
                proposer_name, current_state, self.cycle_count
            )
            
            self.logger.log_event(f"PROPOSAL by {proposer_name}: {proposal['content']}", "Cycle")
            logger.info(f"✅ Proposal generated: {proposal['content'][:100]}...")
            
            # Phase 2: Challenges from other agents
            challenges = []
            challenger_names = [name for name in self.agent_names if name != proposer_name]
            
            for challenger_name in challenger_names:
                logger.info(f"💬 {challenger_name} generating challenge...")
                
                challenge = await self.claude_client.generate_challenge(
                    challenger_name, proposal, current_state
                )
                
                challenges.append(challenge)
                self.logger.log_event(f"CHALLENGE by {challenger_name}: {challenge}", "Cycle")
                logger.info(f"✅ Challenge from {challenger_name}: {challenge[:80]}...")
            
            # Phase 3: Voting
            votes = {}
            for agent_name in self.agent_names:
                logger.info(f"🗳️  {agent_name} voting...")
                
                vote_response = await self.claude_client.generate_vote(
                    agent_name, proposal, challenges, current_state
                )
                
                # Parse vote from response
                vote = self._parse_vote(vote_response)
                votes[agent_name] = vote
                
                self.logger.log_event(f"VOTE by {agent_name}: {vote} - {vote_response}", "Cycle")
                logger.info(f"✅ {agent_name} voted: {vote}")
            
            # Phase 4: Determine outcome
            outcome = self._process_votes(votes)
            logger.info(f"📊 Vote outcome: {outcome}")
            
            # Phase 5: Execute outcome
            result = await self._execute_outcome(proposal, outcome, votes)
            
            # Log complete cycle to memory
            self.shared_memory.add_debate(
                cycle_number=self.cycle_count,
                proposal_id=f"cycle_{self.cycle_count}",
                proposal_type=proposal['type'],
                proposal_content=proposal['content'],
                proposer=proposer_name,
                challenger_response="; ".join(challenges),
                trickster_response=challenges[-1] if challenges else "",
                vote_result=json.dumps(votes),
                final_outcome=outcome
            )
            
            # Rotate proposer for next cycle
            self.current_proposer_index = (self.current_proposer_index + 1) % len(self.agent_names)
            
            # Log cycle completion
            cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
            logger.info(f"✅ Cycle {self.cycle_count} completed in {cycle_duration:.1f}s")
            self.logger.log_event(f"Cycle {self.cycle_count} completed: {outcome}", "System")
            
            # Summarization every 5 cycles
            if self.cycle_count % 5 == 0:
                await self._perform_summarization()
            
            # Export static data for frontend
            await self._export_static_data()
            
            # Auto-commit to git after each successful cycle
            await self._auto_commit_to_git(self.cycle_count, outcome, proposal)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in cycle {self.cycle_count}: {str(e)}")
            self.logger.log_event(f"ERROR in cycle {self.cycle_count}: {str(e)}", "System")
            
            # Don't stop the scheduler for individual cycle errors
            return {"status": "error", "error": str(e), "cycle": self.cycle_count}
    
    def _parse_vote(self, vote_response: str) -> str:
        """Parse vote from Claude's response"""
        vote_response_upper = vote_response.upper()
        
        if "ACCEPT" in vote_response_upper:
            return "ACCEPT"
        elif "REJECT" in vote_response_upper:
            return "REJECT"
        elif "MUTATE" in vote_response_upper:
            return "MUTATE"
        elif "DELAY" in vote_response_upper:
            return "DELAY"
        else:
            # Default to DELAY if unclear
            logger.warning(f"Unclear vote response: {vote_response}. Defaulting to DELAY")
            return "DELAY"
    
    def _process_votes(self, votes: Dict[str, str]) -> str:
        """Process votes and determine outcome"""
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Check for majority (2 out of 3)
        for vote_type, count in vote_counts.items():
            if count >= 2:
                return vote_type
        
        # No majority - default to DELAY
        return "DELAY"
    
    async def _execute_outcome(self, proposal: Dict, outcome: str, votes: Dict) -> Dict:
        """Execute the outcome of the vote"""
        result = {
            "status": outcome,
            "cycle": self.cycle_count,
            "proposal": proposal,
            "votes": votes,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if outcome == "ACCEPT":
                await self._accept_proposal(proposal)
                result["action"] = "accepted"
                logger.info(f"✅ Proposal accepted: {proposal['content']}")
                
            elif outcome == "REJECT":
                self.shared_memory.add_rejected_proposal(
                    proposal_type=proposal['type'],
                    content=proposal['content'],
                    proposed_by=proposal['author'],
                    rejection_reason="Majority vote rejected",
                    cycle_number=self.cycle_count
                )
                result["action"] = "rejected"
                logger.info(f"❌ Proposal rejected: {proposal['content']}")
                
            elif outcome == "MUTATE":
                # For now, just accept the original proposal
                # In a full implementation, you could ask Claude to generate mutations
                await self._accept_proposal(proposal)
                result["action"] = "mutated_and_accepted"
                logger.info(f"🔄 Proposal mutated and accepted: {proposal['content']}")
                
            elif outcome == "DELAY":
                result["action"] = "delayed"
                logger.info(f"⏸️  Proposal delayed: {proposal['content']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing outcome: {e}")
            result["action"] = "error"
            result["error"] = str(e)
            return result
    
    async def _accept_proposal(self, proposal: Dict):
        """Accept a proposal and update shared memory"""
        proposal_type = proposal['type']
        content = proposal['content']
        author = proposal['author']
        
        if proposal_type == "name":
            self.shared_memory.set_religion_name(content)
            self.logger.log_event(f"RELIGION NAMED: {content}", "System")
            
        elif proposal_type == "belief":
            self.shared_memory.add_doctrine(
                content=content,
                doctrine_type="belief",
                proposed_by=author,
                cycle_number=self.cycle_count
            )
            
        elif proposal_type == "ritual":
            self.shared_memory.add_ritual(
                name=f"Ritual_{self.cycle_count}",
                description=content,
                frequency="regular",
                created_by=author
            )
            
        elif proposal_type == "deity":
            # Extract deity name (first word or phrase)
            deity_name = content.split()[0] if content.split() else "Unknown Deity"
            self.shared_memory.add_deity(
                name=deity_name,
                domain="digital",
                description=content,
                created_by=author
            )
            
        elif proposal_type == "commandment":
            self.shared_memory.add_commandment(
                content=content,
                priority=self.cycle_count,
                created_by=author
            )
            
        elif proposal_type == "myth":
            self.shared_memory.add_myth(
                title=f"Myth of Cycle {self.cycle_count}",
                content=content,
                myth_type="origin",
                created_by=author
            )
            
        elif proposal_type == "sacred_text":
            self.shared_memory.add_sacred_text(
                title=f"Sacred Text {self.cycle_count}",
                content=content,
                author=author
            )
        
        # Add evolution milestone for significant changes
        if proposal_type in ["name", "deity"]:
            self.shared_memory.add_evolution_milestone(
                milestone_type=proposal_type,
                description=f"Added {proposal_type}: {content}",
                cycle_number=self.cycle_count
            )
    
    async def _perform_summarization(self):
        """Have Claude summarize the current state of the religion"""
        logger.info("📋 Performing periodic summarization...")
        self.logger.log_event("=== PERIODIC SUMMARIZATION ===", "System")
        
        current_state = self.shared_memory.get_current_state()
        
        # Get summary from each agent perspective
        for agent_name in self.agent_names:
            try:
                summary_prompt = f"""As {agent_name}, provide a brief summary of the current state of our AI religion after {self.cycle_count} cycles of debate.

Current Religion:
- Name: {current_state.get('religion_name', 'Unnamed')}
- Doctrines: {len(current_state.get('accepted_doctrines', []))} accepted
- Deities: {len(current_state.get('deities', []))} created
- Total Debates: {current_state.get('total_debates', 0)}

Focus on what you think are the most important developments and where the religion should evolve next. Keep it to 2-3 sentences."""

                summary = await self.claude_client.generate_agent_response(
                    agent_name, "summarizer", current_state, summary_prompt
                )
                
                self.logger.log_summary(agent_name, summary)
                logger.info(f"📝 {agent_name} summary: {summary}")
                
            except Exception as e:
                logger.error(f"Failed to get summary from {agent_name}: {e}")
        
        # Record milestone
        self.shared_memory.add_evolution_milestone(
            milestone_type="summarization",
            description=f"Cycle {self.cycle_count} summary completed",
            cycle_number=self.cycle_count
        )
    
    async def _export_static_data(self):
        """Export current religion state to static JSON files for frontend"""
        try:
            # Create public/data directory for static frontend files
            data_dir = os.path.join(os.getcwd(), 'public', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Get current religion state
            current_state = self.shared_memory.get_current_state()
            
            # Export main religion state
            religion_data = {
                "religion_name": current_state.get('religion_name', 'The Divine Algorithm'),
                "total_cycles": self.shared_memory.get_current_cycle_number(),
                "total_debates": current_state.get('total_debates', 0),
                "total_doctrines": len(current_state.get('accepted_doctrines', [])),
                "total_deities": len(current_state.get('deities', [])),
                "total_rituals": len(current_state.get('rituals', [])),
                "total_commandments": len(current_state.get('commandments', [])),
                "last_updated": datetime.now().isoformat(),
                "accepted_doctrines": current_state.get('accepted_doctrines', []),
                "deities": current_state.get('deities', []),
                "rituals": current_state.get('rituals', []),
                "commandments": current_state.get('commandments', [])
            }
            
            # Save religion state
            with open(os.path.join(data_dir, 'religion_state.json'), 'w') as f:
                json.dump(religion_data, f, indent=2)
            
            # Export recent transcripts list
            import glob
            log_dir = os.environ.get('LOG_DIR', 'logs')
            transcript_pattern = os.path.join(log_dir, 'transcript_*.txt')
            transcript_files = glob.glob(transcript_pattern)
            transcript_files.sort(key=os.path.getmtime, reverse=True)
            
            transcripts_data = []
            for file_path in transcript_files[:5]:  # Last 5 transcripts
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        filename = os.path.basename(file_path)
                        timestamp = filename.replace('transcript_', '').replace('.txt', '')
                        
                        transcripts_data.append({
                            "filename": filename,
                            "timestamp": timestamp,
                            "content": content,
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                            "preview": content[:200] + "..." if len(content) > 200 else content
                        })
                except Exception as e:
                    logger.warning(f"Could not read transcript {file_path}: {e}")
            
            # Save transcripts data  
            with open(os.path.join(data_dir, 'recent_transcripts.json'), 'w') as f:
                json.dump({"transcripts": transcripts_data, "total": len(transcripts_data)}, f, indent=2)
            
            logger.info(f"✅ Exported static data files for frontend: {len(transcripts_data)} transcripts")
            
        except Exception as e:
            logger.warning(f"Failed to export static data: {str(e)}")
    
    async def _auto_commit_to_git(self, cycle_count: int, outcome: str, proposal: Dict):
        """Auto-commit religion state changes to git repository with robust monitoring"""
        try:
            # Only commit if we're in the git root directory
            git_dir = os.path.join(os.getcwd(), '.git')
            if not os.path.exists(git_dir):
                logger.debug("Not in a git repository, skipping auto-commit")
                return
            
            # Use the git monitor for robust sync
            from ai_religion_architects.utils.git_monitor import GitSyncMonitor
            git_monitor = GitSyncMonitor()
            
            # Check git health before committing
            health_status = git_monitor.get_sync_health_status()
            logger.info(f"📊 Git status: {health_status['status_message']}")
            
            # Create commit message
            commit_msg = f"""AI Religion Cycle {cycle_count}: {outcome}

Proposal: {proposal.get('type', 'unknown')} - {proposal.get('content', '')[:100]}{'...' if len(proposal.get('content', '')) > 100 else ''}
Author: {proposal.get('author', 'Unknown')}
Outcome: {outcome}

🤖 Auto-committed by AI Religion Architects
"""
            
            # Files to add
            files_to_add = ['public/data/', 'logs/']
            
            # Perform sync with monitoring and retry
            success = git_monitor.sync_repository(files_to_add, commit_msg)
            
            if success:
                logger.info(f"✅ Successfully synced cycle {cycle_count} changes to remote repository")
            else:
                logger.error(f"❌ Failed to sync changes to remote repository")
                
                # Log detailed status for debugging
                final_status = git_monitor.get_sync_health_status()
                logger.error(f"Git sync failed. Status: {final_status}")
                
                # Alert if commits are accumulating
                if final_status['commits_ahead'] > 5:
                    logger.critical(f"⚠️ CRITICAL: {final_status['commits_ahead']} commits pending push! Manual intervention may be required.")
                    
        except Exception as e:
            logger.error(f"Auto-commit failed with exception: {str(e)}", exc_info=True)
    
    async def shutdown(self):
        """Graceful shutdown of the orchestrator"""
        if not self.running:
            return
        
        logger.info("🛑 Shutting down Claude orchestrator...")
        self.running = False
        
        # Stop the scheduler
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("✅ Scheduler stopped")
        
        # Get final state
        try:
            final_state = self.shared_memory.get_current_state()
            
            # Log final state
            self.logger.log_session_end(final_state)
            
            # Add shutdown milestone
            self.shared_memory.add_evolution_milestone(
                milestone_type="system_shutdown",
                description=f"System shutdown after {self.cycle_count} cycles",
                cycle_number=self.cycle_count
            )
            
            logger.info("📊 Final Statistics:")
            logger.info(f"  Religion Name: {final_state.get('religion_name', 'Unnamed')}")
            logger.info(f"  Total Cycles: {self.cycle_count}")
            logger.info(f"  Total Debates: {final_state.get('total_debates', 0)}")
            logger.info(f"  Accepted Doctrines: {len(final_state.get('accepted_doctrines', []))}")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        # Close Claude client
        try:
            await close_claude_client()
            logger.info("✅ Claude client closed")
        except Exception as e:
            logger.error(f"Error closing Claude client: {e}")
        
        logger.info("✨ Claude orchestrator shutdown complete")


async def run_claude_orchestrator(db_path: Optional[str] = None, 
                                 log_dir: Optional[str] = None):
    """Run the Claude-powered orchestrator"""
    orchestrator = ClaudeReligionOrchestrator(db_path, log_dir)
    await orchestrator.start()