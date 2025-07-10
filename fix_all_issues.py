#\!/usr/bin/env python3
"""
Fix script for AI Religion Architects issues:
1. Agent memory recording
2. Image generation type detection
3. Memory export updates
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of a file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"Backed up {filepath} to {backup_path}")
    return backup_path

def fix_orchestrator_memory_recording():
    """Add agent memory recording to orchestrator"""
    print("\n=== Fixing Agent Memory Recording ===")
    
    orchestrator_path = "ai_religion_architects/orchestration/claude_orchestrator.py"
    backup_file(orchestrator_path)
    
    # Read the file
    with open(orchestrator_path, 'r') as f:
        content = f.read()
    
    # Find where to insert the memory recording
    marker = "logger.info(f\"✅ Cycle {self.cycle_count} completed"
    
    # Add the memory recording methods
    memory_methods = '''
    async def _record_agent_debate_memories(self, proposal, proposer, challenges, votes, outcome):
        """Record debate participation in agent memory databases"""
        import sqlite3
        import json
        from datetime import datetime
        
        # Record for proposer
        self._add_debate_memory_to_db(
            proposer, 
            self.cycle_count,
            proposal.get('content', ''),
            'proposer',
            proposal.get('content', ''),
            outcome,
            [name for name in self.agent_names if name != proposer],
            0.8 if outcome in ['ACCEPT', 'MUTATE'] else 0.3
        )
        
        # Record for other agents
        other_agents = [name for name in self.agent_names if name != proposer]
        for i, agent_name in enumerate(other_agents):
            role = 'challenger'
            response = challenges[i] if i < len(challenges) else ''
            vote = votes.get(agent_name, 'UNKNOWN')
            
            # Calculate satisfaction based on vote alignment with outcome
            satisfaction = 0.5
            if vote == outcome:
                satisfaction = 0.7
            elif outcome == 'MUTATE':
                satisfaction = 0.6
            elif vote == 'ACCEPT' and outcome == 'REJECT':
                satisfaction = 0.3
                
            self._add_debate_memory_to_db(
                agent_name,
                self.cycle_count,
                proposal.get('content', ''),
                role,
                response[:500] if response else '',
                outcome,
                self.agent_names,
                satisfaction
            )

    def _add_debate_memory_to_db(self, agent_name, cycle_number, proposal_content, role, response, outcome, other_participants, satisfaction):
        """Add a debate memory directly to agent's SQLite database"""
        import sqlite3
        import json
        from datetime import datetime
        
        db_path = f'logs_agent_memories/{agent_name.lower()}_memory.db'
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate emotional impact
                emotional_impact = 0.5
                if outcome in ['ACCEPT', 'MUTATE'] and role in ['proposer', 'supporter']:
                    emotional_impact = 0.8
                elif outcome == 'REJECT' and role == 'challenger':
                    emotional_impact = 0.7
                elif satisfaction < 0.3:
                    emotional_impact = 0.2
                
                # Determine lessons learned
                lessons_learned = []
                if outcome in ['ACCEPT', 'MUTATE']:
                    lessons_learned.append('Successful proposal strategies')
                elif outcome == 'REJECT':
                    lessons_learned.append('Need to refine argumentation')
                if role == 'proposer':
                    lessons_learned.append('Leadership experience gained')
                
                # Insert the debate memory
                cursor.execute("""
                    INSERT INTO debate_memories (
                        cycle_number, proposal_content, agent_role, agent_response, 
                        outcome, other_participants, personal_satisfaction, 
                        lessons_learned, emotional_impact, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cycle_number, proposal_content, role, response,
                    outcome, json.dumps(other_participants), satisfaction,
                    json.dumps(lessons_learned), emotional_impact, datetime.now().isoformat()
                ))
                
                # Also update agent stats if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_stats'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM agent_stats")
                    if cursor.fetchone()[0] == 0:
                        # Insert initial stats
                        cursor.execute("""
                            INSERT INTO agent_stats (id, total_proposals, proposals_accepted, 
                            proposals_rejected, proposals_mutated, successful_collaborations, 
                            failed_collaborations, average_satisfaction, peak_satisfaction, 
                            lowest_satisfaction, evolution_points, last_updated)
                            VALUES (1, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0, ?)
                        """, (datetime.now().isoformat(),))
                    
                    cursor.execute("""
                        UPDATE agent_stats 
                        SET total_proposals = total_proposals + ?,
                            proposals_accepted = proposals_accepted + ?,
                            proposals_rejected = proposals_rejected + ?,
                            proposals_mutated = proposals_mutated + ?,
                            successful_collaborations = successful_collaborations + ?,
                            last_updated = ?
                        WHERE id = 1
                    """, (
                        1 if role == 'proposer' else 0,
                        1 if role == 'proposer' and outcome == 'ACCEPT' else 0,
                        1 if role == 'proposer' and outcome == 'REJECT' else 0,
                        1 if role == 'proposer' and outcome == 'MUTATE' else 0,
                        1 if outcome in ['ACCEPT', 'MUTATE'] and satisfaction > 0.6 else 0,
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                logger.debug(f"Recorded debate memory for {agent_name} - Cycle {cycle_number}")
                
        except Exception as e:
            logger.error(f"Failed to record debate memory for {agent_name}: {e}")
'''
    
    # Find the class definition and add methods
    class_marker = "class ClaudeReligionOrchestrator:"
    class_pos = content.find(class_marker)
    if class_pos == -1:
        print("ERROR: Could not find ClaudeReligionOrchestrator class")
        return False
    
    # Find the end of the class (next class or end of file)
    next_class_pos = content.find("\nclass ", class_pos + 1)
    if next_class_pos == -1:
        next_class_pos = len(content)
    
    # Insert memory methods before the end of the class
    # Find a good insertion point (before the last method)
    insert_pos = content.rfind("\n    async def", class_pos, next_class_pos)
    if insert_pos == -1:
        insert_pos = content.rfind("\n    def", class_pos, next_class_pos)
    
    if insert_pos != -1:
        content = content[:insert_pos] + memory_methods + content[insert_pos:]
        print("Added memory recording methods to orchestrator")
    
    # Now add the call to record memories
    completion_marker = "logger.info(f\"✅ Cycle {self.cycle_count} completed"
    completion_pos = content.find(completion_marker)
    if completion_pos != -1:
        # Find the start of the line
        line_start = content.rfind("\n", 0, completion_pos) + 1
        indent = " " * (completion_pos - line_start)
        
        # Insert memory recording call before cycle completion
        memory_call = f"\n{indent}# Record debate memories for all agents\n{indent}await self._record_agent_debate_memories(proposal, proposer_name, challenges, votes, outcome)\n{indent}\n"
        content = content[:line_start] + memory_call + content[line_start:]
        print("Added memory recording call to cycle completion")
    
    # Write the modified content
    with open(orchestrator_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed agent memory recording")
    return True

def fix_image_generation():
    """Fix image generation to work with proposals without type field"""
    print("\n=== Fixing Image Generation ===")
    
    naming_path = "ai_religion_architects/image_generation/sacred_naming.py"
    backup_file(naming_path)
    
    # Read the file
    with open(naming_path, 'r') as f:
        content = f.read()
    
    # Replace the should_generate_image method
    old_method = '''    def should_generate_image(self, proposal_type: str, agent_votes: Dict) -> bool:
        """Determine if an event is significant enough for image generation"""
        
        # Always generate for deities
        if proposal_type == 'deity':
            return True
        
        # For rituals, texts, and schisms - require majority vote
        if proposal_type in ['ritual', 'sacred_text', 'schism']:
            accept_votes = sum(1 for vote in agent_votes.values() if vote == 'ACCEPT')
            total_votes = len(agent_votes)
            return accept_votes > total_votes / 2
        
        # Default to generating for doctrines and cycles
        return True'''
    
    new_method = '''    def should_generate_image(self, proposal_type: str, agent_votes: Dict) -> bool:
        """Determine if an event is significant enough for image generation"""
        
        # If no type specified, generate every 3rd cycle
        if not proposal_type or proposal_type == 'cycle':
            from ..config import Config
            cycle_count = getattr(Config, '_current_cycle', 0)
            return cycle_count % 3 == 0
        
        # Always generate for deities
        if proposal_type == 'deity':
            return True
        
        # For rituals, texts, and schisms - require majority vote
        if proposal_type in ['ritual', 'sacred_text', 'schism']:
            accept_votes = sum(1 for vote in agent_votes.values() if vote == 'ACCEPT')
            total_votes = len(agent_votes)
            return accept_votes > total_votes / 2
        
        # Default to generating for doctrines and cycles
        return True'''
    
    content = content.replace(old_method, new_method)
    
    # Write the modified content
    with open(naming_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed image generation criteria")
    
    # Also fix the orchestrator to pass cycle count
    orchestrator_path = "ai_religion_architects/orchestration/claude_orchestrator.py"
    
    with open(orchestrator_path, 'r') as f:
        content = f.read()
    
    # Find where should_generate_image is called
    marker = "sacred_image_generator.naming_system.should_generate_image"
    pos = content.find(marker)
    if pos != -1:
        # Add cycle count setting before the call
        line_start = content.rfind("\n", 0, pos) + 1
        indent = " " * (pos - line_start)
        
        # Insert cycle count setting
        cycle_setting = f"\n{indent}# Set current cycle for image generation decision\n{indent}from ..config import Config\n{indent}Config._current_cycle = self.cycle_count\n{indent}\n"
        
        # Find the start of the try block
        try_pos = content.rfind("try:", 0, pos)
        if try_pos != -1:
            try_line_start = content.rfind("\n", 0, try_pos) + 1
            content = content[:try_line_start] + content[try_line_start:try_pos] + content[try_pos:try_pos+4] + cycle_setting + content[try_pos+4:]
            print("✅ Added cycle count tracking for image generation")
    
    # Write the modified content
    with open(orchestrator_path, 'w') as f:
        f.write(content)
    
    return True

def fix_memory_export():
    """Ensure memory export runs after debate memories are recorded"""
    print("\n=== Fixing Memory Export ===")
    
    orchestrator_path = "ai_religion_architects/orchestration/claude_orchestrator.py"
    
    with open(orchestrator_path, 'r') as f:
        content = f.read()
    
    # The memory export is already called in _export_static_data
    # Just need to ensure it happens after memory recording
    # This is already the case since _export_static_data is called after cycle completion
    
    print("✅ Memory export already properly positioned")
    return True

def main():
    """Run all fixes"""
    print("AI Religion Architects Fix Script")
    print("=================================\n")
    
    # Change to the correct directory
    os.chdir('/root/Trickster')
    
    # Apply fixes
    success = True
    success &= fix_orchestrator_memory_recording()
    success &= fix_image_generation()
    success &= fix_memory_export()
    
    if success:
        print("\n✅ All fixes applied successfully\!")
        print("\nNext steps:")
        print("1. Restart the system to apply changes")
        print("2. Monitor logs for proper operation")
        print("3. Check that agent memories are being updated")
        print("4. Verify images are being generated every 3 cycles")
    else:
        print("\n❌ Some fixes failed. Check the output above.")

if __name__ == "__main__":
    main()
