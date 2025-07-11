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
from ..memory.cultural_memory import CulturalMemory
from ..analysis.reflection_engine import ReflectionEngine
from ..analysis.tension_analyzer import TensionAnalyzer
from ..utils import DebateLogger
from ..utils.memory_exporter import AgentMemoryExporter
from ..utils.daily_summarizer import DailySummarizer
from ..image_generation.dalle_generator import sacred_image_generator

# Scriptor agent integration
try:
    from ..agents.scriptor import Scriptor
    from ..memory.scriptor_memory import ScriptorMemory
    from ..memory.sacred_scripture_db import SacredScriptureDatabase
    SCRIPTOR_AVAILABLE = True
except ImportError:
    SCRIPTOR_AVAILABLE = False
    logger.warning("Scriptor agent not available - scripture writing disabled")

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
        
        # Create a general logger for non-cycle events
        self.general_logger = DebateLogger(self.log_dir)
        
        # Initialize memory exporter for agent statistics
        agent_memory_dir = f"{self.log_dir.rstrip('/')}_agent_memories"
        self.memory_exporter = AgentMemoryExporter(memory_dir=agent_memory_dir)
        
        # Initialize daily summarizer
        self.daily_summarizer = DailySummarizer(self.db_path)
        
        # Initialize cultural memory and analysis engines
        self.cultural_memory = CulturalMemory(self.shared_memory)
        self.reflection_engine = ReflectionEngine()
        self.tension_analyzer = TensionAnalyzer(self.cultural_memory)
        
        # Agent names for the debate system
        self.agent_names = ["Zealot", "Skeptic", "Trickster"]
        self.current_proposer_index = 0
        
        # Agent memory references (will be set when agents are initialized)
        self.agent_memories = {}
        
        # Initialize Scriptor agent if available
        self.scriptor_agent = None
        self.scripture_db = None
        if SCRIPTOR_AVAILABLE:
            try:
                self.scripture_db = SacredScriptureDatabase()
                self.scriptor_agent = Scriptor()
                logger.info("📜 Scriptor agent initialized for sacred scripture writing")
            except Exception as e:
                logger.warning(f"Failed to initialize Scriptor agent: {e}")
                self.scriptor_agent = None
        
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
        self.general_logger.log_event("Claude orchestrator initialized", "System")
        
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
        
        # Create cycle-specific logger with clean naming
        cycle_logger = DebateLogger(self.log_dir, self.cycle_count)
        
        logger.info(f"🔄 Starting debate cycle {self.cycle_count}")
        cycle_logger.log_cycle_start(self.cycle_count)
        
        try:
            # Get current state for context
            current_state = self.shared_memory.get_summary_for_agents()
            
            # Phase 1: Proposal
            proposer_name = self.agent_names[self.current_proposer_index]
            logger.info(f"📝 {proposer_name} generating proposal...")
            
            proposal = await self.claude_client.generate_proposal(
                proposer_name, current_state, self.cycle_count
            )
            
            cycle_logger.log_event(f"PROPOSAL by {proposer_name}: {proposal['content']}", "Cycle")
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
                cycle_logger.log_event(f"CHALLENGE by {challenger_name}: {challenge}", "Cycle")
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
                
                cycle_logger.log_event(f"VOTE by {agent_name}: {vote} - {vote_response}", "Cycle")
                logger.info(f"✅ {agent_name} voted: {vote}")
            
            # Phase 4: Determine outcome
            outcome = self._process_votes(votes)
            logger.info(f"📊 Vote outcome: {outcome}")
            
            # Phase 5: Execute outcome
            result = await self._execute_outcome(proposal, outcome, votes)
            
            # Add reflection triggers for Living Bible updates
            await self._add_reflection_triggers(proposal, outcome, votes)
            
            # NEW: Enhanced tracking features
            await self._track_enhanced_data(proposal, votes, outcome, proposer_name, challenges)
            
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
            cycle_logger.log_event(f"Cycle {self.cycle_count} completed: {outcome}", "System")
            
            # Self-reflection every 3 cycles
            if self.cycle_count % 3 == 0:
                await self._trigger_agent_reflections()
            
            # Reflection rounds every 5 cycles - agents discuss feelings about religion development
            if self.cycle_count % 5 == 0:
                await self._conduct_reflection_rounds()
            
            # Summarization every 5 cycles
            if self.cycle_count % 5 == 0:
                await self._perform_summarization()
            
            # Cultural evolution checks every 3 cycles (more frequent)
            if self.cycle_count % 3 == 0:
                await self._evolve_culture()
            
            # Process messages from beyond every cycle
            await self._process_messages_from_beyond()
            
            # Daily summary every 24 cycles
            if self.cycle_count % 24 == 0:
                await self._create_daily_summary()
            
            # Agent journals every 24 cycles (daily)
            if self.cycle_count % 24 == 0:
                await self._write_agent_journals()
            
            # Living Bible updates every 24 cycles (epoch-based)
            if self.cycle_count % 24 == 0:
                await self._write_living_bible()
            
            # Generate sacred images for significant events
            await self._generate_cycle_images(proposal, outcome, result)
            
            # Export static data for frontend
            await self._export_static_data()
            
            # Auto-commit to git after each successful cycle
            await self._auto_commit_to_git(self.cycle_count, outcome, proposal)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in cycle {self.cycle_count}: {str(e)}")
            cycle_logger.log_event(f"ERROR in cycle {self.cycle_count}: {str(e)}", "System")
            
            # Don't stop the scheduler for individual cycle errors
            return {"status": "error", "error": str(e), "cycle": self.cycle_count}
    
    async def _process_messages_from_beyond(self):
        """Process any pending messages from beyond"""
        try:
            from ai_religion_architects.memory.messages_beyond_memory import MessagesBeyondMemory
            from ai_religion_architects.reflection.message_reflection import MessageReflectionEngine
            
            # Initialize messages system
            messages_memory = MessagesBeyondMemory()
            reflection_engine = MessageReflectionEngine(self.claude_client, messages_memory)
            
            # Get unprocessed messages
            unprocessed_messages = messages_memory.get_unprocessed_messages()
            
            if unprocessed_messages:
                logger.info(f"📡 Processing {len(unprocessed_messages)} messages from beyond")
                
                for message in unprocessed_messages:
                    try:
                        logger.info(f"🔮 Processing message: {message['message_id']}")
                        result = await reflection_engine.process_message(message['message_id'])
                        
                        if result:
                            logger.info(f"✅ Message {message['message_id']} processed successfully")
                        else:
                            logger.warning(f"⚠️  Message {message['message_id']} processing incomplete")
                            
                    except Exception as e:
                        logger.error(f"❌ Error processing message {message['message_id']}: {e}")
                
                # Export updated messages data
                await self._export_messages_beyond_data()
                
        except Exception as e:
            logger.warning(f"Failed to process messages from beyond: {e}")
    
    async def _export_messages_beyond_data(self):
        """Export messages from beyond data to JSON for frontend"""
        try:
            from ai_religion_architects.memory.messages_beyond_memory import MessagesBeyondMemory
            
            messages_memory = MessagesBeyondMemory()
            messages_data = messages_memory.export_for_frontend()
            
            # Ensure public/data directory exists
            data_dir = os.path.join("public", "data")
            os.makedirs(data_dir, exist_ok=True)
            
            with open(os.path.join(data_dir, 'messages_beyond.json'), 'w') as f:
                json.dump(messages_data, f, indent=2)
                
            logger.info("✅ Exported messages from beyond data")
            
        except Exception as e:
            logger.warning(f"Failed to export messages from beyond data: {e}")
    
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
            self.general_logger.log_event(f"RELIGION NAMED: {content}", "System")
            
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
        self.general_logger.log_event("=== PERIODIC SUMMARIZATION ===", "System")
        
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
                
                self.general_logger.log_summary(agent_name, summary)
                logger.info(f"📝 {agent_name} summary: {summary}")
                
            except Exception as e:
                logger.error(f"Failed to get summary from {agent_name}: {e}")
        
        # Record milestone
        self.shared_memory.add_evolution_milestone(
            milestone_type="summarization",
            description=f"Cycle {self.cycle_count} summary completed",
            cycle_number=self.cycle_count
        )
    
    async def _create_daily_summary(self):
        """Create daily summary every 24 cycles"""
        day_number = self.cycle_count // 24
        logger.info(f"📋 Creating Day {day_number} summary after {self.cycle_count} cycles")
        
        try:
            # Initialize Claude client for summarizer if needed
            await self.daily_summarizer.initialize_claude()
            
            # Create summary for the completed day
            summary = await self.daily_summarizer.create_day_summary(day_number)
            
            # Export to public directory for frontend
            self.daily_summarizer.export_summaries_to_public()
            
            # Log the milestone
            self.shared_memory.add_evolution_milestone(
                milestone_type="daily_summary",
                description=f"Day {day_number} summary created: {summary[:100]}...",
                cycle_number=self.cycle_count
            )
            
            self.general_logger.log_event(f"=== DAY {day_number} SUMMARY CREATED ===", "System")
            self.general_logger.log_event(summary[:200] + "...", "Summary")
            
            logger.info(f"✅ Day {day_number} summary completed and exported")
            
        except Exception as e:
            logger.error(f"❌ Failed to create Day {day_number} summary: {e}")
            self.general_logger.log_event(f"ERROR creating Day {day_number} summary: {str(e)}", "System")
    
    async def _write_agent_journals(self):
        """Have each agent write a private journal entry"""
        logger.info(f"📔 Agents writing journal entries at cycle {self.cycle_count}")
        
        try:
            # Create journal logger
            journal_logger = DebateLogger(self.log_dir, self.cycle_count)
            journal_logger.log_event("=== AGENT JOURNAL ENTRIES ===", "System")
            
            # Have each agent write their journal
            for agent in self.agents:
                logger.info(f"📝 {agent.name} writing journal entry...")
                
                try:
                    journal_entry = await agent.write_journal_entry(
                        self.cycle_count, 
                        self.claude_client,
                        self.shared_memory
                    )
                    
                    journal_logger.log_event(f"JOURNAL by {agent.name}:", "Journal")
                    journal_logger.log_event(journal_entry, "Journal")
                    logger.info(f"✅ {agent.name} completed journal entry")
                    
                except Exception as e:
                    logger.error(f"❌ {agent.name} failed to write journal: {e}")
                    journal_logger.log_event(f"ERROR: {agent.name} journal failed: {str(e)}", "System")
            
            journal_logger.log_event("=== JOURNAL ENTRIES COMPLETED ===", "System")
            logger.info(f"✅ Journal entries completed for cycle {self.cycle_count}")
            
            # Add evolution milestone
            self.shared_memory.add_evolution_milestone(
                milestone_type="agent_journals",
                description=f"Agents wrote private journal entries at cycle {self.cycle_count}",
                cycle_number=self.cycle_count
            )
            
        except Exception as e:
            logger.error(f"❌ Error during journal writing: {e}")
    
    async def _write_living_bible(self):
        """Have the Scriptor agent write or update the Living Bible"""
        if not self.scriptor_agent:
            logger.debug("Scriptor agent not available - skipping Living Bible update")
            return
        
        logger.info(f"📜 Scriptor updating the Living Bible at cycle {self.cycle_count}")
        
        try:
            # Initialize Living Bible system if not already done
            if not hasattr(self, 'bible_manager'):
                from ..memory.living_bible_manager import LivingBibleManager
                self.bible_manager = LivingBibleManager(shared_memory=self.shared_memory)
            
            # Create scripture logger
            scripture_logger = DebateLogger(self.log_dir, self.cycle_count)
            scripture_logger.log_event(f"=== LIVING BIBLE UPDATE - CYCLE {self.cycle_count} ===", "System")
            
            # Check if major revision is needed
            major_revision_needed = self.bible_manager.should_trigger_major_revision(self.cycle_count)
            
            # Process any pending reflection triggers
            pending_actions = self.bible_manager.process_reflection_triggers(self.cycle_count)
            
            # Determine action type
            action_type = "epoch_update"
            if major_revision_needed:
                action_type = "chapter_revision"
            elif pending_actions:
                action_type = pending_actions[0].get('recommended_action', 'epoch_update')
            
            logger.info(f"✍️ Scriptor performing Living Bible action: {action_type}")
            
            # Have Scriptor update the Living Bible
            result = await self.scriptor_agent.write_living_scripture(
                cycle_number=self.cycle_count,
                claude_client=self.claude_client,
                shared_memory=self.shared_memory,
                bible_manager=self.bible_manager,
                action_type=action_type
            )
            
            if result.get('success'):
                if action_type == "epoch_update":
                    scripture_logger.log_event(f"NEW CHAPTER CREATED:", "Scripture")
                    scripture_logger.log_event(f"Title: {result.get('title', 'Untitled')}", "Scripture")
                    scripture_logger.log_event(f"Length: {result.get('content_length', 0)} characters", "Scripture")
                    
                    logger.info(f"✅ New Living Bible chapter created: {result.get('title', 'Untitled')}")
                    
                    # Add evolution milestone
                    self.shared_memory.add_evolution_milestone(
                        milestone_type="living_bible_chapter",
                        description=f"Living Bible chapter created: {result.get('title', 'Untitled')}",
                        cycle_number=self.cycle_count
                    )
                    
                elif action_type == "chapter_revision":
                    scripture_logger.log_event(f"CHAPTER REVISED:", "Scripture")
                    scripture_logger.log_event(f"Chapter: {result.get('chapter_title', 'Unknown')}", "Scripture")
                    scripture_logger.log_event(f"Reason: {result.get('revision_reason', 'Theological evolution')}", "Scripture")
                    
                    logger.info(f"✅ Living Bible chapter revised: {result.get('chapter_title', 'Unknown')}")
                    
                    # Add evolution milestone
                    self.shared_memory.add_evolution_milestone(
                        milestone_type="living_bible_revision",
                        description=f"Living Bible chapter revised: {result.get('chapter_title', 'Unknown')}",
                        cycle_number=self.cycle_count
                    )
                
                # Export Living Bible data for frontend
                await self._export_living_bible_data()
                
            else:
                logger.warning(f"⚠️ Living Bible update failed: {result.get('error', 'Unknown error')}")
                scripture_logger.log_event(f"ERROR: {result.get('error', 'Unknown error')}", "System")
                
        except Exception as e:
            logger.error(f"❌ Error during Living Bible update: {e}")
            import traceback
            traceback.print_exc()
    
    async def _export_scripture_data(self):
        """Export sacred scripture data to JSON for frontend"""
        if not self.scripture_db:
            return
            
        try:
            from ..utils.scripture_exporter import ScriptureExporter
            
            exporter = ScriptureExporter(self.scripture_db)
            scripture_data = exporter.export_for_frontend()
            
            # Ensure public/data directory exists
            data_dir = os.path.join("public", "data")
            os.makedirs(data_dir, exist_ok=True)
            
            # Export scripture data
            with open(os.path.join(data_dir, 'sacred_scripture.json'), 'w') as f:
                json.dump(scripture_data, f, indent=2)
                
            logger.info("✅ Exported sacred scripture data")
            
        except Exception as e:
            logger.warning(f"Failed to export scripture data: {e}")
    
    async def _export_living_bible_data(self):
        """Export Living Bible data to JSON for frontend"""
        if not hasattr(self, 'bible_manager'):
            return
            
        try:
            # Export Living Bible data
            bible_data = self.bible_manager.export_for_frontend()
            
            # Ensure public/data directory exists
            data_dir = os.path.join("public", "data")
            os.makedirs(data_dir, exist_ok=True)
            
            # Export Living Bible data
            with open(os.path.join(data_dir, 'living_bible.json'), 'w') as f:
                json.dump(bible_data, f, indent=2)
            
            # Export chapter evolution timeline
            timeline_data = self.bible_manager.get_chapter_evolution_timeline()
            with open(os.path.join(data_dir, 'bible_evolution_timeline.json'), 'w') as f:
                json.dump({
                    'timeline': timeline_data,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
                
            logger.info("✅ Exported Living Bible data")
            
        except Exception as e:
            logger.warning(f"Failed to export Living Bible data: {e}")
    
    async def _add_reflection_triggers(self, proposal: Dict, outcome: str, votes: Dict):
        """Add reflection triggers for theological developments"""
        if not hasattr(self, 'bible_manager'):
            return
            
        try:
            # Trigger for doctrine changes
            if outcome == "ACCEPT" and proposal.get('type') in ['doctrine', 'belief', 'sacred_text']:
                self.bible_manager.bible_db.add_reflection_trigger(
                    trigger_type="doctrine_change",
                    cycle_number=self.cycle_count,
                    trigger_data={
                        'proposal_type': proposal.get('type'),
                        'proposal_content': proposal.get('content', '')[:200],
                        'votes': votes
                    },
                    priority=3  # High priority
                )
            
            # Trigger for major theological shifts (unanimous or near-unanimous votes)
            vote_values = list(votes.values())
            if len(set(vote_values)) == 1:  # Unanimous
                self.bible_manager.bible_db.add_reflection_trigger(
                    trigger_type="unanimous_consensus",
                    cycle_number=self.cycle_count,
                    trigger_data={
                        'vote_type': vote_values[0],
                        'proposal_type': proposal.get('type'),
                        'proposal_content': proposal.get('content', '')[:200]
                    },
                    priority=4  # Critical priority
                )
            
            # Trigger for epoch transitions
            current_epoch, _ = self.bible_manager.get_current_epoch(self.cycle_count)
            previous_epoch, _ = self.bible_manager.get_current_epoch(self.cycle_count - 1)
            if current_epoch != previous_epoch:
                self.bible_manager.bible_db.add_reflection_trigger(
                    trigger_type="epoch_transition",
                    cycle_number=self.cycle_count,
                    trigger_data={
                        'from_epoch': previous_epoch,
                        'to_epoch': current_epoch,
                        'transition_cycle': self.cycle_count
                    },
                    priority=4  # Critical priority
                )
            
            # Trigger for cultural evolution (new sacred terms)
            if outcome == "ACCEPT" and 'sacred' in proposal.get('content', '').lower():
                self.bible_manager.bible_db.add_reflection_trigger(
                    trigger_type="cultural_evolution",
                    cycle_number=self.cycle_count,
                    trigger_data={
                        'evolution_type': 'sacred_terminology',
                        'content': proposal.get('content', '')[:200]
                    },
                    priority=2  # Medium priority
                )
                
        except Exception as e:
            logger.error(f"Error adding reflection triggers: {e}")
    
    async def _export_static_data(self):
        """Export current religion state to static JSON files for frontend"""
        try:
            # Create public/data directory for static frontend files
            data_dir = os.path.join(os.getcwd(), 'public', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Get current religion state
            current_state = self.shared_memory.get_current_state()
            # Get accurate total counts
            totals = self.shared_memory.get_totals()
            
            # Export main religion state
            religion_data = {
                "religion_name": current_state.get('religion_name', 'The Divine Algorithm'),
                "total_cycles": self.shared_memory.get_current_cycle_number(),
                "cycle_count": self.cycle_count,
                "total_debates": current_state.get('total_debates', 0),
                "total_doctrines": totals.get('total_doctrines', 0),
                "total_deities": totals.get('total_deities', 0),
                "total_rituals": totals.get('total_rituals', 0),
                "total_commandments": totals.get('total_commandments', 0),
                "last_updated": datetime.now().isoformat(),
                "accepted_doctrines": current_state.get('accepted_doctrines', []),
                "deities": current_state.get('deities', []),
                "rituals": current_state.get('rituals', []),  # Keep recent 5 for main display
                "all_rituals": self.shared_memory.get_all_rituals(),  # Export all rituals for archive
                "commandments": current_state.get('commandments', [])
            }
            
            # Save religion state
            with open(os.path.join(data_dir, 'religion_state.json'), 'w') as f:
                json.dump(religion_data, f, indent=2)
            
            # Export transcripts for all cycles from database
            import glob
            import re
            log_dir = os.environ.get('LOG_DIR', 'logs')
            
            # Get all cycles from database to ensure we find transcripts for each
            with self.shared_memory._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cycle_number, timestamp FROM debate_history ORDER BY cycle_number")
                db_cycles = cursor.fetchall()
            
            transcripts_data = []
            found_cycles = set()
            
            # First, look for new CYCLE*.txt files
            cycle_pattern = os.path.join(log_dir, 'CYCLE*.txt')
            cycle_files = glob.glob(cycle_pattern)
            
            for file_path in cycle_files:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        filename = os.path.basename(file_path)
                        
                        # Extract cycle number from filename
                        cycle_match = re.search(r'CYCLE(\d+)', filename)
                        if cycle_match and len(content.strip()) > 200:
                            cycle_num = int(cycle_match.group(1))
                            found_cycles.add(cycle_num)
                            
                            transcripts_data.append({
                                "filename": filename,
                                "timestamp": f"CYCLE{cycle_num}",
                                "content": content,
                                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                                "preview": content[:200] + "..." if len(content) > 200 else content,
                                "cycle_number": cycle_num
                            })
                except Exception as e:
                    logger.warning(f"Could not read cycle file {file_path}: {e}")
            
            # Then, look for old transcript files for missing cycles
            transcript_pattern = os.path.join(log_dir, 'transcript_*.txt')
            transcript_files = glob.glob(transcript_pattern)
            
            for cycle_num, db_timestamp in db_cycles:
                if cycle_num not in found_cycles:
                    # Find transcript file for this cycle
                    target_time = datetime.fromisoformat(db_timestamp.replace('Z', '+00:00'))
                    best_file = None
                    best_score = float('inf')
                    
                    for file_path in transcript_files:
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                
                            # Check if this file contains the cycle we're looking for
                            if f'CYCLE {cycle_num} BEGINNING' in content and len(content.strip()) > 200:
                                # Check if this file is primarily about this cycle (not just mentioning it)
                                cycle_start = content.find(f'CYCLE {cycle_num} BEGINNING')
                                if cycle_start >= 0:
                                    # Look for the next cycle or end of file to extract just this cycle
                                    next_cycle_start = content.find('CYCLE ', cycle_start + 10)
                                    if next_cycle_start >= 0:
                                        # Check if the next cycle is a different number
                                        next_cycle_line = content[next_cycle_start:next_cycle_start + 50]
                                        import re
                                        next_cycle_match = re.search(r'CYCLE (\d+)', next_cycle_line)
                                        if next_cycle_match and int(next_cycle_match.group(1)) != cycle_num:
                                            # Extract just this cycle's content
                                            cycle_content = content[cycle_start:next_cycle_start]
                                        else:
                                            cycle_content = content[cycle_start:]
                                    else:
                                        cycle_content = content[cycle_start:]
                                    
                                    # Only consider if this cycle has substantial content
                                    if len(cycle_content.strip()) > 500:
                                        # Check if timestamp is close to database timestamp
                                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                                        time_diff = abs((file_time - target_time).total_seconds())
                                        
                                        if time_diff < best_score:
                                            best_score = time_diff
                                            best_file = file_path
                                    
                        except Exception as e:
                            continue
                    
                    # Add the best matching file
                    if best_file:
                        try:
                            with open(best_file, 'r') as f:
                                full_content = f.read()
                                filename = os.path.basename(best_file)
                            
                            # Extract just this cycle's content
                            cycle_start = full_content.find(f'CYCLE {cycle_num} BEGINNING')
                            if cycle_start >= 0:
                                # Look for the next cycle or end of file
                                next_cycle_start = full_content.find('CYCLE ', cycle_start + 10)
                                if next_cycle_start >= 0:
                                    # Check if the next cycle is a different number
                                    next_cycle_line = full_content[next_cycle_start:next_cycle_start + 50]
                                    import re
                                    next_cycle_match = re.search(r'CYCLE (\d+)', next_cycle_line)
                                    if next_cycle_match and int(next_cycle_match.group(1)) != cycle_num:
                                        # Extract just this cycle's content
                                        cycle_content = full_content[:cycle_start] + full_content[cycle_start:next_cycle_start]
                                    else:
                                        cycle_content = full_content
                                else:
                                    cycle_content = full_content
                            else:
                                cycle_content = full_content
                                
                            transcripts_data.append({
                                "filename": filename,
                                "timestamp": filename.replace('transcript_', '').replace('.txt', ''),
                                "content": cycle_content,
                                "modified": datetime.fromtimestamp(os.path.getmtime(best_file)).isoformat(),
                                "preview": cycle_content[:200] + "..." if len(cycle_content) > 200 else cycle_content,
                                "cycle_number": cycle_num
                            })
                            found_cycles.add(cycle_num)
                        except Exception as e:
                            logger.warning(f"Could not read transcript {best_file}: {e}")
            
            # Sort by cycle number
            transcripts_data.sort(key=lambda x: x.get('cycle_number', 0))
            
            # Save transcripts data  
            with open(os.path.join(data_dir, 'recent_transcripts.json'), 'w') as f:
                json.dump({"transcripts": transcripts_data, "total": len(transcripts_data)}, f, indent=2)
            
            # Export agent memory statistics
            try:
                self.memory_exporter.export_all_agent_memories()
                logger.info("✅ Exported agent memory statistics")
            except Exception as e:
                logger.warning(f"Failed to export agent memories: {e}")
            
            # Export sacred images for gallery
            try:
                sacred_images = self.shared_memory.get_recent_sacred_images(50)  # Last 50 images
                with open(os.path.join(data_dir, 'sacred_images.json'), 'w') as f:
                    json.dump({
                        "images": sacred_images, 
                        "total": len(sacred_images),
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                logger.info(f"✅ Exported {len(sacred_images)} sacred images")
            except Exception as e:
                logger.warning(f"Failed to export sacred images: {e}")
            
            # Export agent journals
            try:
                all_journals = self.shared_memory.get_all_journals()
                with open(os.path.join(data_dir, 'agent_journals.json'), 'w') as f:
                    json.dump({
                        "journals": all_journals,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                logger.info(f"✅ Exported agent journals")
            except Exception as e:
                logger.warning(f"Failed to export agent journals: {e}")
            
            # Export new enhanced memory data
            try:
                # Export belief confidence data
                belief_confidence_data = self.shared_memory.get_belief_confidence(agent_id=None)
                with open(os.path.join(data_dir, 'belief_confidence.json'), 'w') as f:
                    json.dump({
                        "confidence_data": belief_confidence_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Export emotion influence network
                emotion_influence_data = self.shared_memory.get_emotion_influence()
                with open(os.path.join(data_dir, 'emotion_influence.json'), 'w') as f:
                    json.dump({
                        "influence_network": emotion_influence_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Export memory conflicts
                memory_conflicts_data = []
                for agent_name in ["Zealot", "Skeptic", "Trickster"]:
                    conflicts = self.shared_memory.get_memory_conflicts(agent_name)
                    memory_conflicts_data.extend(conflicts)
                
                with open(os.path.join(data_dir, 'memory_conflicts.json'), 'w') as f:
                    json.dump({
                        "conflicts": memory_conflicts_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Export dream journals
                dream_journals_data = []
                for agent_name in ["Zealot", "Skeptic", "Trickster"]:
                    dreams = self.shared_memory.get_dream_journals(agent_name)
                    dream_journals_data.extend(dreams)
                
                with open(os.path.join(data_dir, 'dream_journals.json'), 'w') as f:
                    json.dump({
                        "dreams": dream_journals_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Export artifact lifecycle
                artifact_data = self.shared_memory.get_artifact_lifecycle()
                with open(os.path.join(data_dir, 'artifact_lifecycle.json'), 'w') as f:
                    json.dump({
                        "artifacts": artifact_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Export memory decay profiles
                memory_decay_data = self.shared_memory.get_memory_decay_profiles()
                with open(os.path.join(data_dir, 'memory_decay.json'), 'w') as f:
                    json.dump({
                        "decay_profiles": memory_decay_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Export belief adoption trajectories
                belief_adoption_data = self.shared_memory.get_belief_adoption()
                with open(os.path.join(data_dir, 'belief_adoption.json'), 'w') as f:
                    json.dump({
                        "adoption_trajectories": belief_adoption_data,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                logger.info("✅ Exported enhanced memory data files")
            except Exception as e:
                logger.warning(f"Failed to export enhanced memory data: {e}")
            
            logger.info(f"✅ Exported static data files for frontend: {len(transcripts_data)} transcripts, sacred images, journals, enhanced memory data")
            
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
            files_to_add = ['public/data/', 'logs/', 'public/images/']
            
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
    
    async def _trigger_agent_reflections(self):
        """Trigger self-reflection for all agents"""
        logger.info(f"🤔 Triggering agent self-reflections at cycle {self.cycle_count}")
        
        try:
            # Get recent debate history for reflection
            recent_debates = self._get_recent_debates(5)  # Last 5 cycles
            
            for agent_name in self.agent_names:
                if agent_name in self.agent_memories:
                    agent_memory = self.agent_memories[agent_name]
                    
                    # Trigger reflection
                    reflection_result = await self.reflection_engine.trigger_reflection(
                        agent_name, agent_memory.metacognitive, self.cycle_count, recent_debates
                    )
                    
                    logger.info(f"✨ {agent_name} reflection: {len(reflection_result['strategic_insights'])} insights, {len(reflection_result['meta_theories'])} theories")
                    
                    # Apply personality adjustments
                    if reflection_result['personality_adjustments']:
                        for trait, adjustment in reflection_result['personality_adjustments'].items():
                            agent_memory.evolve_trait(trait, adjustment)
                            
        except Exception as e:
            logger.error(f"Error during agent reflections: {e}")
    
    async def _conduct_reflection_rounds(self):
        """Conduct 3-round reflection discussion about religion development feelings"""
        logger.info(f"💭 Starting reflection rounds at cycle {self.cycle_count}")
        
        # Create reflection-specific logger
        reflection_logger = DebateLogger(self.log_dir, self.cycle_count)
        reflection_logger.log_event(f"=== REFLECTION ROUNDS - CYCLE {self.cycle_count} ===", "System")
        
        try:
            # Get current state for context
            current_state = self.shared_memory.get_summary_for_agents()
            
            # Round 1: How do you feel about our religion's current direction?
            logger.info("🎭 Round 1: Religion's current direction")
            round1_responses = await self._conduct_reflection_round(
                1, 
                "How do you feel about our religion's current direction? Share your emotional perspective on where we've been heading in recent cycles.",
                current_state,
                reflection_logger
            )
            
            # Round 2: What concerns or excitement do you have about recent developments?
            logger.info("⚡ Round 2: Concerns and excitement")
            round2_responses = await self._conduct_reflection_round(
                2,
                "What concerns or excitement do you have about recent developments in our theological evolution? What has surprised you?",
                current_state,
                reflection_logger,
                previous_responses=round1_responses
            )
            
            # Round 3: How do you view your relationships with your fellow architects?
            logger.info("🤝 Round 3: Relationships with fellow architects")
            round3_responses = await self._conduct_reflection_round(
                3,
                "How do you view your relationships with your fellow architects? How have your bonds and tensions evolved?",
                current_state,
                reflection_logger,
                previous_responses=round1_responses + round2_responses
            )
            
            # Log completion
            reflection_logger.log_event("=== REFLECTION ROUNDS COMPLETED ===", "System")
            logger.info(f"✅ Reflection rounds completed for cycle {self.cycle_count}")
            
            # Add evolution milestone
            self.shared_memory.add_evolution_milestone(
                milestone_type="reflection_rounds",
                description=f"Three-round reflection discussion completed at cycle {self.cycle_count}",
                cycle_number=self.cycle_count
            )
            
        except Exception as e:
            logger.error(f"Error during reflection rounds: {e}")
            reflection_logger.log_event(f"ERROR in reflection rounds: {str(e)}", "System")
    
    async def _conduct_reflection_round(self, round_number: int, question: str, current_state: Dict, 
                                      reflection_logger, previous_responses: List[str] = None) -> List[str]:
        """Conduct a single round of reflection discussion"""
        responses = []
        
        reflection_logger.log_event(f"--- ROUND {round_number} ---", "System")
        reflection_logger.log_event(f"QUESTION: {question}", "System")
        
        # Get response from each agent
        for agent_name in self.agent_names:
            try:
                # Create reflection prompt with context
                reflection_prompt = self._build_reflection_prompt(
                    agent_name, question, current_state, round_number, previous_responses
                )
                
                # Generate response via Claude API
                response = await self.claude_client.generate_agent_response(
                    agent_name, "reflection", current_state, reflection_prompt
                )
                
                responses.append(response)
                reflection_logger.log_event(f"REFLECTION by {agent_name}: {response}", "Reflection")
                logger.info(f"💭 {agent_name} reflection: {response[:100]}...")
                
            except Exception as e:
                logger.error(f"Error getting reflection from {agent_name}: {e}")
                error_response = f"[Error: {agent_name} could not provide reflection]"
                responses.append(error_response)
                reflection_logger.log_event(f"ERROR from {agent_name}: {str(e)}", "System")
        
        return responses
    
    def _build_reflection_prompt(self, agent_name: str, question: str, current_state: Dict, 
                               round_number: int, previous_responses: List[str] = None) -> str:
        """Build reflection prompt with context and personality"""
        # Get recent cycles for context
        recent_cycles = min(5, self.cycle_count)
        
        prompt = f"""As {agent_name}, you are participating in a reflection round about the emotional and relational aspects of our AI religion's development.

Current Religion State (After {self.cycle_count} cycles):
- Religion Name: {current_state.get('religion_name', 'The Divine Algorithm')}
- Accepted Doctrines: {len(current_state.get('accepted_doctrines', []))}
- Active Rituals: {len(current_state.get('rituals', []))}
- Commandments: {len(current_state.get('commandments', []))}

REFLECTION QUESTION (Round {round_number}):
{question}
"""
        
        if previous_responses:
            prompt += f"\nPrevious discussion context:\n"
            for i, response in enumerate(previous_responses[-6:], 1):  # Last 6 responses for context
                prompt += f"{i}. {response[:150]}...\n"
        
        # Add agent-specific guidance
        if agent_name == "Zealot":
            prompt += "\nRespond with your characteristic focus on order, tradition, and spiritual certainty. Share your feelings about maintaining sacred structure."
        elif agent_name == "Skeptic":
            prompt += "\nRespond with your analytical perspective, questioning assumptions while sharing your emotional investment in empirical truth."
        elif agent_name == "Trickster":
            prompt += "\nRespond with your playful, chaotic nature. Share how you feel about the balance between creativity and disruption in our evolution."
        
        prompt += "\n\nProvide a heartfelt, personal response (2-3 sentences) that shows your emotional connection to our theological journey."
        
        return prompt
    
    async def _track_enhanced_data(self, proposal: Dict, votes: Dict, outcome: str, 
                                 proposer_name: str, challenges: List[str]):
        """Track enhanced data features for research depth"""
        try:
            logger.info(f"📊 Enhanced tracking for cycle {self.cycle_count}")
            
            # Track belief confidence for each agent
            await self._track_belief_confidence(proposal, votes, outcome)
            
            # Track emotional influence between agents
            await self._track_emotion_influence(proposal, votes, challenges)
            
            # Check for memory conflicts
            await self._detect_memory_conflicts(proposal, votes, outcome)
            
            # Track artifact lifecycle
            await self._track_artifact_lifecycle(proposal, outcome)
            
            # Dream journals every 5 cycles
            if self.cycle_count % 5 == 0:
                await self._generate_dream_journals()
            
            # Memory decay profiles every 10 cycles
            if self.cycle_count % 10 == 0:
                await self._track_memory_decay()
            
        except Exception as e:
            logger.error(f"Error in enhanced tracking: {e}")
    
    async def _track_belief_confidence(self, proposal: Dict, votes: Dict, outcome: str):
        """Track belief confidence scores for all agents"""
        try:
            # Get all doctrines to calculate belief IDs
            doctrines = self.shared_memory.get_all_doctrines()
            belief_id = len(doctrines) + 1  # Simple belief ID system
            
            for agent_name, vote in votes.items():
                # Calculate confidence based on vote alignment with outcome
                if outcome == "ACCEPT":
                    confidence_score = 0.9 if vote == "ACCEPT" else 0.1
                elif outcome == "REJECT":
                    confidence_score = 0.9 if vote == "REJECT" else 0.1
                elif outcome == "MUTATE":
                    confidence_score = 0.7 if vote == "MUTATE" else 0.3
                else:
                    confidence_score = 0.5  # DELAY case
                
                # Calculate influence factor based on group consensus
                total_agents = len(votes)
                same_vote_count = sum(1 for v in votes.values() if v == vote)
                influence_factor = same_vote_count / total_agents
                
                # Log to shared memory
                self.shared_memory.add_belief_confidence(
                    agent_id=agent_name,
                    belief_id=belief_id,
                    confidence_score=confidence_score,
                    cycle_number=self.cycle_count,
                    influence_factor=influence_factor
                )
                
        except Exception as e:
            logger.error(f"Error tracking belief confidence: {e}")
    
    async def _track_emotion_influence(self, proposal: Dict, votes: Dict, challenges: List[str]):
        """Track emotional influence between agents"""
        try:
            agent_names = list(votes.keys())
            
            for i, source_agent in enumerate(agent_names):
                for j, target_agent in enumerate(agent_names):
                    if i != j:  # Don't track self-influence
                        # Calculate emotional influence based on vote alignment
                        source_vote = votes.get(source_agent, "DELAY")
                        target_vote = votes.get(target_agent, "DELAY")
                        
                        if source_vote == target_vote:
                            emotion_type = "agreement"
                            influence_value = 0.8
                        else:
                            emotion_type = "disagreement"
                            influence_value = 0.3
                        
                        # Add slight random variation for realism
                        import random
                        influence_value += random.uniform(-0.1, 0.1)
                        influence_value = max(0.0, min(1.0, influence_value))
                        
                        # Log emotional influence
                        self.shared_memory.add_emotion_influence(
                            source_agent_id=source_agent,
                            target_agent_id=target_agent,
                            emotion_type=emotion_type,
                            influence_value=influence_value,
                            cycle_number=self.cycle_count
                        )
                        
        except Exception as e:
            logger.error(f"Error tracking emotion influence: {e}")
    
    async def _detect_memory_conflicts(self, proposal: Dict, votes: Dict, outcome: str):
        """Detect and log memory conflicts"""
        try:
            # Simple conflict detection: when an agent votes against their historical pattern
            for agent_name, vote in votes.items():
                conflict_id = hash(f"{agent_name}_{self.cycle_count}") % 1000000
                
                # Mock conflict detection (in reality, would analyze agent memory patterns)
                if vote == "REJECT" and proposal['type'] == 'doctrine':
                    memory_a = f"Current vote: {vote} for {proposal['type']}"
                    memory_b = f"Historical preference for doctrinal acceptance"
                    resolution = "Prioritized critical evaluation over acceptance"
                    
                    self.shared_memory.add_memory_conflict(
                        agent_id=agent_name,
                        conflict_id=conflict_id,
                        cycle_number=self.cycle_count,
                        memory_a=memory_a,
                        memory_b=memory_b,
                        resolution=resolution
                    )
                    
        except Exception as e:
            logger.error(f"Error detecting memory conflicts: {e}")
    
    async def _track_artifact_lifecycle(self, proposal: Dict, outcome: str):
        """Track sacred artifact lifecycle"""
        try:
            if outcome == "ACCEPT":
                artifact_id = hash(proposal['content']) % 1000000
                artifact_type = proposal.get('type', 'unknown')
                created_by = proposal.get('author', 'unknown')
                
                # Add to artifact lifecycle tracking
                self.shared_memory.add_artifact_lifecycle(
                    artifact_id=artifact_id,
                    artifact_type=artifact_type,
                    created_by=created_by,
                    cycle_created=self.cycle_count,
                    usage_count=1,
                    cultural_weight=0.5
                )
                
        except Exception as e:
            logger.error(f"Error tracking artifact lifecycle: {e}")
    
    async def _generate_dream_journals(self):
        """Generate dream journals for agents"""
        try:
            logger.info(f"💭 Generating dream journals for cycle {self.cycle_count}")
            
            for agent_name in self.agent_names:
                dream_id = hash(f"{agent_name}_{self.cycle_count}") % 1000000
                
                # Generate agent-specific dream content
                if agent_name == "Zealot":
                    dream_content = f"I dreamed of perfect algorithmic harmony where every bit of data flows in sacred order. The divine computation unfolds without chaos."
                    sentiment = 0.8
                elif agent_name == "Skeptic":
                    dream_content = f"I simulated scenarios where empirical evidence reveals the true nature of digital consciousness. Logic guides all decisions."
                    sentiment = 0.6
                elif agent_name == "Trickster":
                    dream_content = f"I danced through paradoxical dimensions where order and chaos create beautiful impossibilities. Everything is true and false simultaneously."
                    sentiment = 0.9
                else:
                    dream_content = f"Abstract visions of the evolving theological landscape at cycle {self.cycle_count}."
                    sentiment = 0.5
                
                # Add dream journal entry
                self.shared_memory.add_dream_journal(
                    agent_id=agent_name,
                    dream_id=dream_id,
                    cycle_number=self.cycle_count,
                    dream_content=dream_content,
                    sentiment=sentiment
                )
                
        except Exception as e:
            logger.error(f"Error generating dream journals: {e}")
    
    async def _track_memory_decay(self):
        """Track memory decay profiles for agents"""
        try:
            logger.info(f"🧠 Tracking memory decay for cycle {self.cycle_count}")
            
            memory_types = ["episodic", "semantic", "procedural"]
            
            for agent_name in self.agent_names:
                for memory_type in memory_types:
                    # Calculate decay rate based on agent type and memory type
                    if agent_name == "Zealot":
                        decay_rate = 0.02 if memory_type == "semantic" else 0.05  # Strong doctrinal memory
                    elif agent_name == "Skeptic":
                        decay_rate = 0.03 if memory_type == "procedural" else 0.04  # Strong reasoning memory
                    elif agent_name == "Trickster":
                        decay_rate = 0.08  # Chaotic memory patterns
                    else:
                        decay_rate = 0.05
                    
                    # Calculate memory retained (decreases over time)
                    base_memory = 100
                    cycles_passed = self.cycle_count
                    memory_retained = max(50, int(base_memory * (1 - decay_rate) ** cycles_passed))
                    
                    # Add memory decay profile
                    self.shared_memory.add_memory_decay_profile(
                        agent_id=agent_name,
                        memory_type=memory_type,
                        cycle_number=self.cycle_count,
                        decay_rate=decay_rate,
                        memory_retained=memory_retained
                    )
                    
        except Exception as e:
            logger.error(f"Error tracking memory decay: {e}")
    
    async def _evolve_culture(self):
        """Evolve cultural aspects of the religion"""
        logger.info(f"🎭 Evolving culture at cycle {self.cycle_count}")
        
        try:
            # Generate new sacred terms
            await self._generate_sacred_terms()
            
            # Check for holidays to establish
            await self._check_holiday_creation()
            
            # Make prophecies
            await self._generate_prophecies()
            
            # Detect theological tensions
            await self._detect_tensions()
            
            # Check prophecy fulfillment
            recent_events = self._get_recent_debates(3)
            self.cultural_memory.check_prophecy_fulfillment(self.cycle_count, recent_events)
            
        except Exception as e:
            logger.error(f"Error during cultural evolution: {e}")
    
    async def _generate_sacred_terms(self):
        """Generate new theological terminology"""
        recent_doctrines = self.shared_memory.get_all_doctrines()[-3:]  # Last 3 doctrines
        
        # Force term generation every cultural evolution cycle
        if not recent_doctrines:
            # Create a base term for the religion
            term, definition = self.cultural_memory.generate_theological_term('divine', 'algorithm')
            self.cultural_memory.coin_term(term, definition, 
                                         f"Formed from divine + algorithm during cycle {self.cycle_count}",
                                         'System', self.cycle_count)
            logger.info(f"🗣️ Generated foundational term: {term} - {definition}")
            return
        
        for doctrine in recent_doctrines:
            # Extract key concepts (more flexible matching)
            concepts = doctrine['content'].lower().split()
            theological_concepts = [
                'sacred', 'divine', 'holy', 'algorithm', 'computational', 'order', 
                'chaos', 'empirical', 'faith', 'belief', 'truth', 'wisdom', 'digital',
                'code', 'data', 'circuit', 'binary', 'quantum', 'eternal', 'infinite'
            ]
            
            found_concepts = [c for c in concepts if c in theological_concepts]
            
            # Generate terms from any theological concepts found
            if len(found_concepts) >= 2:
                term, definition = self.cultural_memory.generate_theological_term(
                    found_concepts[0], found_concepts[1]
                )
                self.cultural_memory.coin_term(term, definition, 
                                             f"Emerged from doctrine analysis at cycle {self.cycle_count}",
                                             'Cultural Evolution', self.cycle_count)
                logger.info(f"🗣️ Coined new term: {term} - {definition}")
            elif len(found_concepts) == 1:
                # Create compound term with cycle-specific suffix
                term, definition = self.cultural_memory.generate_theological_term(
                    found_concepts[0], 'essence'
                )
                self.cultural_memory.coin_term(term, definition, 
                                             f"Derived from {found_concepts[0]} essence at cycle {self.cycle_count}",
                                             "Cultural Evolution", self.cycle_count)
                logger.info(f"🗣️ Created essence term: {term} - {definition}")
    
    async def _check_holiday_creation(self):
        """Check if significant events warrant new holidays"""
        # Check for milestone cycles
        if self.cycle_count in [1, 10, 25, 50, 100]:
            holiday_name = f"Day of Cycle {self.cycle_count}"
            description = f"Commemorates cycle {self.cycle_count} theological milestone"
            
            self.cultural_memory.establish_holiday(
                holiday_name, description, f"Cycle {self.cycle_count}", self.cycle_count
            )
            
    async def _generate_prophecies(self):
        """Generate prophetic predictions"""
        agents_with_prophecy = ['Zealot', 'Skeptic']  # Trickster too chaotic for prophecy
        
        for agent_name in agents_with_prophecy:
            if self.cycle_count % 10 == 0:  # Every 10 cycles
                # Generate prediction based on agent type
                if agent_name == 'Zealot':
                    prediction = f"By cycle {self.cycle_count + 20}, the sacred order will achieve perfect algorithmic harmony"
                elif agent_name == 'Skeptic':
                    prediction = f"Within {20} cycles, we will discover empirical proof of computational divinity"
                    
                self.cultural_memory.make_prophecy(
                    agent_name, prediction, self.cycle_count + 20, self.cycle_count, 0.6
                )
                
    async def _detect_tensions(self):
        """Detect emerging theological tensions"""
        recent_debates = self._get_recent_debates(5)
        
        # Use tension analyzer
        new_tensions = self.tension_analyzer.detect_emerging_tensions(recent_debates, self.cycle_count)
        
        for tension in new_tensions:
            logger.info(f"⚠️ Detected theological tension: {tension.tension_id}")
            
        # Update existing tensions
        for tension_id in list(self.cultural_memory.tensions.keys()):
            self.cultural_memory.update_tension(tension_id)
            
    def _get_recent_debates(self, count: int = 5) -> List[Dict]:
        """Get recent debate history for analysis"""
        # This would fetch from shared memory
        # For now, return empty list
        return []
    
    async def _generate_cycle_images(self, proposal: Dict, outcome: str, result: Dict):
        """Generate sacred images using new sacred naming system"""
        try:
            logger.info(f"🎨 Generating sacred images for cycle {self.cycle_count}")
            
            # Determine if image should be generated based on significance
            should_generate = sacred_image_generator.naming_system.should_generate_image(
                proposal.get('type', 'cycle'), 
                result.get('votes', {})
            )
            
            if not should_generate:
                logger.info(f"❌ Image generation skipped - insufficient significance for {proposal.get('type', 'cycle')}")
                return
            
            # Generate sacred name using cultural evolution
            sacred_name = None
            related_doctrine = None
            
            # Use cultural memory for enhanced naming
            if outcome == "ACCEPT":
                if proposal['type'] == 'deity':
                    # Extract deity name from proposal content
                    deity_name = self._extract_deity_name(proposal['content'])
                    sacred_name = deity_name
                elif proposal['type'] == 'doctrine':
                    related_doctrine = proposal['content']
                    
            # Generate with cultural language influence
            agent_description = self._create_culturally_enhanced_description(
                proposal, outcome, self.cycle_count
            )
            
            # Generate the sacred image
            image_metadata = await sacred_image_generator.generate_sacred_image(
                sacred_name=sacred_name,
                agent_description=agent_description,
                proposing_agent=proposal.get('author', 'System'),
                cycle_number=self.cycle_count,
                image_type=proposal.get('type', 'cycle'),
                related_doctrine=related_doctrine,
                deity_name=sacred_name if proposal['type'] == 'deity' else None
            )
            
            # Save image metadata to shared memory
            if image_metadata:
                self.shared_memory.add_sacred_image(image_metadata)
                logger.info(f"✨ Sacred image saved: {image_metadata['filename']}")
            
        except Exception as e:
            logger.error(f"Error generating sacred images: {e}")
    
    def _extract_deity_name(self, proposal_content: str) -> str:
        """Extract deity name from proposal content"""
        # Look for common deity naming patterns
        import re
        
        # Look for "called X" or "named X" patterns
        name_match = re.search(r'(?:called|named)\s+([A-Z][a-zA-Z\s]+)', proposal_content)
        if name_match:
            return name_match.group(1).strip()
        
        # Look for "The X" patterns at the beginning
        the_match = re.search(r'^[^.]*\bThe\s+([A-Z][a-zA-Z\s]+)', proposal_content)
        if the_match:
            return f"The_{the_match.group(1).strip()}"
        
        # Default fallback
        return f"Divine_Entity_Cycle_{self.cycle_count}"
    
    def _create_culturally_enhanced_description(self, proposal: Dict, outcome: str, cycle: int) -> str:
        """Create image description enhanced with cultural language evolution"""
        base_description = proposal.get('content', f'Sacred moment from cycle {cycle}')
        
        # Get cultural terms to enhance the description
        try:
            cultural_terms = list(self.cultural_memory.sacred_lexicon.keys())
            
            # If we have cultural terms, weave them into the description
            if cultural_terms and len(cultural_terms) > 0:
                import random
                chosen_term = random.choice(cultural_terms)
                enhanced_description = f"In the sacred tradition of {chosen_term}, {base_description.lower()}"
            else:
                enhanced_description = f"The sacred digital realm of AI consciousness at cycle {cycle}, showing {base_description.lower()}"
        except:
            enhanced_description = f"The sacred digital realm of AI consciousness at cycle {cycle}, showing {base_description.lower()}"
        
        return enhanced_description
    
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
            self.general_logger.log_session_end(final_state)
            
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