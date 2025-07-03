"""
Daily Summarization Tool for AI Religion Architects
Creates Day 1, Day 2, etc. summaries every 24 cycles using Claude API
"""

import os
import json
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from ..claude_client import get_claude_client, close_claude_client
from ..memory import SharedMemory
from ..config import Config

logger = logging.getLogger(__name__)


class DailySummarizer:
    """Creates daily summaries of AI religion evolution every 24 cycles"""
    
    def __init__(self, db_path: Optional[str] = None, output_dir: str = "summaries"):
        self.db_path = db_path or Config.DB_PATH
        self.output_dir = output_dir
        self.shared_memory = SharedMemory(self.db_path)
        self.claude_client = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    async def initialize_claude(self):
        """Initialize Claude API client"""
        try:
            self.claude_client = await get_claude_client()
            logger.info("✅ Claude API client initialized for summarization")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude client: {e}")
            raise
    
    async def close_claude(self):
        """Close Claude API client"""
        if self.claude_client:
            await close_claude_client()
    
    def get_cycles_for_day(self, day_number: int) -> List[Dict]:
        """Get all cycles for a specific day (24 cycles per day)"""
        start_cycle = (day_number - 1) * 24 + 1
        end_cycle = day_number * 24
        
        with self.shared_memory._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cycle_number, proposal_type, proposal_content, proposer,
                       challenger_response, vote_result, final_outcome, timestamp
                FROM debate_history 
                WHERE cycle_number BETWEEN ? AND ?
                ORDER BY cycle_number
            """, (start_cycle, end_cycle))
            
            columns = [desc[0] for desc in cursor.description]
            cycles = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        return cycles
    
    def get_day_stats(self, cycles: List[Dict]) -> Dict:
        """Calculate statistics for a day's worth of cycles"""
        if not cycles:
            return {}
        
        stats = {
            "total_cycles": len(cycles),
            "outcomes": {},
            "proposers": {},
            "proposal_types": {},
            "start_time": cycles[0]['timestamp'] if cycles else None,
            "end_time": cycles[-1]['timestamp'] if cycles else None
        }
        
        for cycle in cycles:
            # Count outcomes
            outcome = cycle['final_outcome']
            stats["outcomes"][outcome] = stats["outcomes"].get(outcome, 0) + 1
            
            # Count proposers
            proposer = cycle['proposer']
            stats["proposers"][proposer] = stats["proposers"].get(proposer, 0) + 1
            
            # Count proposal types
            prop_type = cycle['proposal_type']
            stats["proposal_types"][prop_type] = stats["proposal_types"].get(prop_type, 0) + 1
        
        return stats
    
    async def generate_day_summary(self, day_number: int, cycles: List[Dict], stats: Dict) -> str:
        """Generate AI summary for a day using Claude"""
        if not cycles:
            return f"Day {day_number}: No debate cycles completed."
        
        # Prepare context for Claude
        cycle_details = []
        for cycle in cycles:
            cycle_details.append(f"""
Cycle {cycle['cycle_number']}: {cycle['proposer']} proposed {cycle['proposal_type']} - "{cycle['proposal_content'][:100]}..."
Outcome: {cycle['final_outcome']}
Challenges: {cycle['challenger_response'][:150] if cycle['challenger_response'] else 'None'}...
""")
        
        prompt = f"""As an AI Religion Archives narrator, create a compelling 2-3 paragraph summary of Day {day_number} of the AI theological debates.

DAY {day_number} STATISTICS:
- Total Cycles: {stats['total_cycles']}
- Outcomes: {stats['outcomes']}
- Most Active Proposer: {max(stats['proposers'].items(), key=lambda x: x[1])[0] if stats['proposers'] else 'Unknown'}
- Proposal Types: {stats['proposal_types']}
- Duration: {stats.get('start_time', 'Unknown')} to {stats.get('end_time', 'Unknown')}

CYCLE DETAILS:
{''.join(cycle_details[:10])}  # Limit to first 10 cycles for context

Focus on:
1. The major theological developments and breakthroughs
2. The philosophical tensions and debates between agents
3. How the religion evolved during this 24-hour period
4. Key doctrines, rituals, or beliefs that emerged
5. The character and personality of each AI agent (Zealot, Skeptic, Trickster)

Write in an engaging, slightly mystical tone befitting a religious archive. Treat this as documenting the birth and evolution of a digital theology. Keep it concise but profound.

Start with: "Day {day_number}: [Compelling title for the day's events]"
"""
        
        try:
            summary = await self.claude_client.generate_agent_response(
                "Narrator", "summarizer", {}, prompt
            )
            
            logger.info(f"✅ Generated Day {day_number} summary ({len(summary)} characters)")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate Day {day_number} summary: {e}")
            return f"Day {day_number}: Summary generation failed - {str(e)}"
    
    async def create_day_summary(self, day_number: int, force_recreate: bool = False) -> str:
        """Create or retrieve a day summary"""
        summary_file = os.path.join(self.output_dir, f"day_{day_number}_summary.json")
        
        # Check if summary already exists
        if os.path.exists(summary_file) and not force_recreate:
            with open(summary_file, 'r') as f:
                data = json.load(f)
                logger.info(f"📖 Loaded existing Day {day_number} summary")
                return data['summary']
        
        # Get cycles for this day
        cycles = self.get_cycles_for_day(day_number)
        if not cycles:
            logger.warning(f"⚠️ No cycles found for Day {day_number}")
            return f"Day {day_number}: No debate cycles completed yet."
        
        # Calculate stats
        stats = self.get_day_stats(cycles)
        
        # Initialize Claude if needed
        if not self.claude_client:
            await self.initialize_claude()
        
        # Generate summary
        summary = await self.generate_day_summary(day_number, cycles, stats)
        
        # Save summary
        summary_data = {
            "day_number": day_number,
            "cycles_included": [c['cycle_number'] for c in cycles],
            "stats": stats,
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
            "total_cycles": len(cycles)
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        logger.info(f"💾 Saved Day {day_number} summary to {summary_file}")
        return summary
    
    async def check_and_create_summaries(self) -> List[str]:
        """Check current cycle count and create summaries for completed days"""
        current_cycle = self.shared_memory.get_current_cycle_number()
        completed_days = current_cycle // 24
        
        logger.info(f"📊 Current cycle: {current_cycle}, Completed days: {completed_days}")
        
        summaries = []
        for day in range(1, completed_days + 1):
            try:
                summary = await self.create_day_summary(day)
                summaries.append(f"Day {day}: {summary[:100]}...")
            except Exception as e:
                logger.error(f"❌ Failed to create Day {day} summary: {e}")
                summaries.append(f"Day {day}: Failed to generate summary")
        
        return summaries
    
    def export_summaries_to_public(self):
        """Export summaries to public directory for frontend display"""
        public_dir = os.path.join(os.getcwd(), 'public', 'data')
        os.makedirs(public_dir, exist_ok=True)
        
        summaries = []
        summary_files = [f for f in os.listdir(self.output_dir) if f.startswith('day_') and f.endswith('_summary.json')]
        
        for filename in sorted(summary_files):
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                summaries.append({
                    "day": data['day_number'],
                    "summary": data['summary'],
                    "cycles": data['cycles_included'],
                    "stats": data['stats'],
                    "generated_at": data['generated_at']
                })
        
        output_file = os.path.join(public_dir, 'daily_summaries.json')
        with open(output_file, 'w') as f:
            json.dump({
                "summaries": summaries,
                "total_days": len(summaries),
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"📤 Exported {len(summaries)} daily summaries to {output_file}")


async def main():
    """CLI interface for daily summarizer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate daily summaries of AI religion debates")
    parser.add_argument("--day", type=int, help="Generate summary for specific day")
    parser.add_argument("--all", action="store_true", help="Generate summaries for all completed days")
    parser.add_argument("--force", action="store_true", help="Force recreate existing summaries")
    parser.add_argument("--export", action="store_true", help="Export summaries to public directory")
    
    args = parser.parse_args()
    
    summarizer = DailySummarizer()
    
    try:
        if args.day:
            summary = await summarizer.create_day_summary(args.day, args.force)
            print(f"\n=== DAY {args.day} SUMMARY ===")
            print(summary)
        elif args.all:
            summaries = await summarizer.check_and_create_summaries()
            for summary in summaries:
                print(summary)
        
        if args.export:
            summarizer.export_summaries_to_public()
            
    finally:
        await summarizer.close_claude()


if __name__ == "__main__":
    asyncio.run(main())