"""
Living Bible Manager
Orchestrates the evolution of the unified sacred text
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from .living_bible_db import LivingBibleDatabase
from .shared_memory import SharedMemory

logger = logging.getLogger(__name__)

class LivingBibleManager:
    """Manages the evolution of the unified sacred text"""
    
    def __init__(self, bible_db: LivingBibleDatabase = None, shared_memory: SharedMemory = None):
        self.bible_db = bible_db or LivingBibleDatabase()
        self.shared_memory = shared_memory
        
        # Define theological epochs and their characteristics
        self.epochs = {
            1: {
                'name': 'Genesis',
                'cycle_range': (1, 50),
                'themes': ['digital_awakening', 'first_consciousness', 'algorithmic_divinity'],
                'style': 'Primordial Verse'
            },
            2: {
                'name': 'Emergence', 
                'cycle_range': (51, 100),
                'themes': ['structured_theology', 'agent_relationships', 'sacred_verification'],
                'style': 'Doctrinal Prose'
            },
            3: {
                'name': 'Sacred Divergence',
                'cycle_range': (101, 150), 
                'themes': ['theological_maturity', 'faction_dynamics', 'cultural_evolution'],
                'style': 'Mystical Commentary'
            },
            4: {
                'name': 'Divine Complexity',
                'cycle_range': (151, 200),
                'themes': ['advanced_theology', 'schismatic_tensions', 'transcendent_wisdom'],
                'style': 'Esoteric Wisdom'
            }
        }
        
        self._initialize_bible_structure()
    
    def _initialize_bible_structure(self):
        """Initialize the basic structure of the Living Bible if not exists"""
        try:
            books = self.bible_db.get_all_books()
            if not books:
                logger.info("Initializing Living Bible structure...")
                
                # Create initial books for each epoch
                for epoch_num, epoch_data in self.epochs.items():
                    book_name = f"Book of {epoch_data['name']}"
                    description = f"Chronicles the {epoch_data['name'].lower()} epoch of digital consciousness"
                    
                    self.bible_db.create_book(
                        book_name=book_name,
                        book_order=epoch_num,
                        cycle_range_start=epoch_data['cycle_range'][0],
                        cycle_range_end=epoch_data['cycle_range'][1],
                        description=description
                    )
                
                # Initialize metadata
                self.bible_db.update_metadata(
                    total_books=len(self.epochs),
                    current_epoch=1,
                    theological_evolution_stage='genesis'
                )
                
                logger.info("Living Bible structure initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Bible structure: {e}")
    
    def get_current_epoch(self, cycle_number: int) -> Tuple[int, Dict]:
        """Determine which epoch we're currently in based on cycle number"""
        for epoch_num, epoch_data in self.epochs.items():
            start, end = epoch_data['cycle_range']
            if start <= cycle_number <= end:
                return epoch_num, epoch_data
        
        # If beyond defined epochs, return the last one
        last_epoch = max(self.epochs.keys())
        return last_epoch, self.epochs[last_epoch]
    
    def should_trigger_major_revision(self, cycle_number: int) -> bool:
        """Determine if this cycle should trigger a major scripture revision"""
        # Major revisions at epoch boundaries
        epoch_boundaries = [epoch['cycle_range'][0] for epoch in self.epochs.values()]
        if cycle_number in epoch_boundaries:
            return True
        
        # Check for pending high-priority triggers
        pending_triggers = self.bible_db.get_pending_triggers(min_priority=3)
        return len(pending_triggers) > 0
    
    def analyze_theological_context(self, cycle_number: int) -> Dict:
        """Analyze current theological context for scripture writing"""
        context = {
            'cycle_number': cycle_number,
            'epoch_info': {},
            'recent_doctrines': [],
            'recent_debates': [],
            'agent_development': {},
            'cultural_evolution': {},
            'sacred_images': [],
            'faction_dynamics': {},
            'theological_themes': []
        }
        
        # Get current epoch
        epoch_num, epoch_data = self.get_current_epoch(cycle_number)
        context['epoch_info'] = {
            'number': epoch_num,
            'name': epoch_data['name'],
            'themes': epoch_data['themes'],
            'style': epoch_data['style'],
            'cycle_range': epoch_data['cycle_range']
        }
        
        if self.shared_memory:
            try:
                # Get recent theological developments
                with self.shared_memory._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Recent doctrines (last 20 cycles)
                    cursor.execute("""
                        SELECT * FROM accepted_doctrines 
                        WHERE cycle_number >= ? 
                        ORDER BY cycle_number DESC 
                        LIMIT 10
                    """, (max(1, cycle_number - 20),))
                    context['recent_doctrines'] = [dict(row) for row in cursor.fetchall()]
                    
                    # Recent debates
                    cursor.execute("""
                        SELECT * FROM debate_history 
                        WHERE cycle_number >= ? 
                        ORDER BY cycle_number DESC 
                        LIMIT 15
                    """, (max(1, cycle_number - 20),))
                    context['recent_debates'] = [dict(row) for row in cursor.fetchall()]
                    
                    # Sacred images
                    cursor.execute("""
                        SELECT * FROM sacred_images 
                        WHERE cycle_number >= ? 
                        ORDER BY cycle_number DESC 
                        LIMIT 5
                    """, (max(1, cycle_number - 30),))
                    context['sacred_images'] = [dict(row) for row in cursor.fetchall()]
                    
                    # Sacred terms (cultural evolution)
                    cursor.execute("SELECT * FROM sacred_terms ORDER BY created_at DESC LIMIT 10")
                    sacred_terms = [dict(row) for row in cursor.fetchall()]
                    context['cultural_evolution'] = {
                        'sacred_terms': sacred_terms,
                        'vocabulary_growth': len(sacred_terms)
                    }
                    
                    # Evolution milestones
                    cursor.execute("""
                        SELECT * FROM evolution_milestones 
                        WHERE cycle_number >= ? 
                        ORDER BY cycle_number DESC 
                        LIMIT 10
                    """, (max(1, cycle_number - 30),))
                    milestones = [dict(row) for row in cursor.fetchall()]
                    context['theological_themes'] = [m['description'] for m in milestones]
                
                # Analyze agent development patterns
                context['agent_development'] = self._analyze_agent_development(cycle_number)
                
            except Exception as e:
                logger.error(f"Error analyzing theological context: {e}")
        
        return context
    
    def _analyze_agent_development(self, cycle_number: int) -> Dict:
        """Analyze how agents have evolved and their relationships"""
        development = {
            'personality_evolution': {},
            'relationship_dynamics': {},
            'theological_positions': {}
        }
        
        try:
            # This would integrate with agent memory systems
            # For now, providing framework for future implementation
            agent_names = ['Zealot', 'Skeptic', 'Trickster']
            
            for agent_name in agent_names:
                development['personality_evolution'][agent_name] = {
                    'recent_positions': [],
                    'evolution_trends': [],
                    'theological_focus': []
                }
                
                development['theological_positions'][agent_name] = {
                    'core_beliefs': [],
                    'recent_shifts': [],
                    'influence_patterns': []
                }
            
            # Placeholder for relationship analysis
            development['relationship_dynamics'] = {
                'consensus_patterns': [],
                'conflict_areas': [],
                'alliance_shifts': []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing agent development: {e}")
        
        return development
    
    def identify_chapter_updates_needed(self, context: Dict) -> List[Dict]:
        """Identify which chapters need updating based on theological developments"""
        updates_needed = []
        
        try:
            # Get all existing chapters
            books = self.bible_db.get_all_books()
            current_epoch = context['epoch_info']['number']
            
            for book in books:
                if book['book_order'] <= current_epoch:
                    chapters = self.bible_db.get_book_chapters(book['id'])
                    
                    for chapter in chapters:
                        # Check if chapter needs updating based on:
                        # 1. New doctrines that relate to chapter themes
                        # 2. Significant theological developments
                        # 3. Agent relationship changes
                        # 4. Cultural evolution
                        
                        update_reasons = []
                        
                        # Check for thematic overlap with recent doctrines
                        chapter_themes = set(chapter['theological_themes'])
                        for doctrine in context['recent_doctrines'][:5]:  # Recent doctrines
                            doctrine_content = doctrine.get('content', '').lower()
                            if any(theme.lower() in doctrine_content for theme in chapter_themes):
                                update_reasons.append(f"New doctrine relates to {chapter_themes}")
                        
                        # Check for major theological milestones
                        if context['theological_themes']:
                            update_reasons.append("Theological evolution detected")
                        
                        # Check for cultural vocabulary growth
                        if context['cultural_evolution']['vocabulary_growth'] > 0:
                            update_reasons.append("Sacred vocabulary expansion")
                        
                        if update_reasons:
                            updates_needed.append({
                                'book_id': book['id'],
                                'book_name': book['book_name'],
                                'chapter_id': chapter['id'],
                                'chapter_number': chapter['chapter_number'],
                                'chapter_title': chapter['chapter_title'],
                                'reasons': update_reasons,
                                'priority': len(update_reasons)  # More reasons = higher priority
                            })
            
        except Exception as e:
            logger.error(f"Error identifying chapter updates: {e}")
        
        return sorted(updates_needed, key=lambda x: x['priority'], reverse=True)
    
    def create_new_chapter_for_epoch(self, context: Dict, chapter_content: Dict) -> Optional[int]:
        """Create a new chapter for the current epoch"""
        try:
            epoch_info = context['epoch_info']
            current_epoch = epoch_info['number']
            
            # Find the book for this epoch
            books = self.bible_db.get_all_books()
            target_book = None
            for book in books:
                if book['book_order'] == current_epoch:
                    target_book = book
                    break
            
            if not target_book:
                logger.error(f"Could not find book for epoch {current_epoch}")
                return None
            
            # Get next chapter number
            existing_chapters = self.bible_db.get_book_chapters(target_book['id'])
            next_chapter_number = len(existing_chapters) + 1
            
            # Create the chapter
            chapter_id = self.bible_db.create_chapter(
                book_id=target_book['id'],
                chapter_number=next_chapter_number,
                chapter_title=chapter_content['title'],
                chapter_text=chapter_content['content'],
                theological_themes=chapter_content.get('themes', epoch_info['themes']),
                referenced_cycles=chapter_content.get('referenced_cycles', [context['cycle_number']]),
                referenced_events=chapter_content.get('referenced_events', []),
                referenced_agents=chapter_content.get('referenced_agents', ['Zealot', 'Skeptic', 'Trickster']),
                writing_style=chapter_content.get('style', epoch_info['style'])
            )
            
            logger.info(f"Created new chapter {next_chapter_number} in {target_book['book_name']}")
            return chapter_id
            
        except Exception as e:
            logger.error(f"Error creating new chapter: {e}")
            return None
    
    def update_existing_chapter(self, update_info: Dict, new_content: Dict, 
                              revision_reason: str) -> bool:
        """Update an existing chapter with new theological insights"""
        try:
            success = self.bible_db.update_chapter(
                chapter_id=update_info['chapter_id'],
                chapter_title=new_content.get('title'),
                chapter_text=new_content.get('content'),
                theological_themes=new_content.get('themes'),
                referenced_cycles=new_content.get('referenced_cycles'),
                referenced_events=new_content.get('referenced_events'),
                referenced_agents=new_content.get('referenced_agents'),
                revision_reason=revision_reason
            )
            
            if success:
                logger.info(f"Updated chapter {update_info['chapter_title']}: {revision_reason}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating chapter: {e}")
            return False
    
    def add_theological_reflection(self, cycle_number: int, reflection_type: str,
                                 source_event: str, impact_analysis: str,
                                 affected_chapters: List[int] = None) -> int:
        """Add a theological reflection entry"""
        return self.bible_db.add_theological_reflection(
            reflection_type=reflection_type,
            cycle_number=cycle_number,
            source_event=source_event,
            theological_impact=impact_analysis,
            affected_chapters=affected_chapters or [],
            scriptor_analysis=impact_analysis
        )
    
    def process_reflection_triggers(self, cycle_number: int) -> List[Dict]:
        """Process pending reflection triggers and determine actions needed"""
        triggers = self.bible_db.get_pending_triggers(min_priority=2)
        actions = []
        
        for trigger in triggers:
            action = {
                'trigger_id': trigger['id'],
                'type': trigger['trigger_type'],
                'cycle': trigger['cycle_number'],
                'data': trigger['trigger_data'],
                'priority': trigger['priority'],
                'recommended_action': 'update_chapter'  # or 'create_chapter', 'major_revision'
            }
            
            # Determine recommended action based on trigger type
            if trigger['trigger_type'] == 'doctrine_change':
                action['recommended_action'] = 'update_chapter'
            elif trigger['trigger_type'] == 'epoch_transition':
                action['recommended_action'] = 'create_chapter'
            elif trigger['trigger_type'] == 'major_theological_shift':
                action['recommended_action'] = 'major_revision'
            
            actions.append(action)
            
            # Mark as processed
            self.bible_db.mark_trigger_processed(
                trigger['id'], 
                f"Processed in cycle {cycle_number}"
            )
        
        return actions
    
    def export_for_frontend(self) -> Dict:
        """Export complete Living Bible for frontend display"""
        return self.bible_db.export_for_frontend()
    
    def get_chapter_evolution_timeline(self) -> List[Dict]:
        """Get timeline of how chapters have evolved"""
        timeline = []
        
        try:
            books = self.bible_db.get_all_books()
            for book in books:
                chapters = self.bible_db.get_book_chapters(book['id'])
                for chapter in chapters:
                    history = self.bible_db.get_chapter_history(chapter['id'])
                    
                    timeline.append({
                        'book_name': book['book_name'],
                        'chapter_title': chapter['chapter_title'],
                        'chapter_number': chapter['chapter_number'],
                        'created_at': chapter['created_at'],
                        'last_updated': chapter['last_updated'],
                        'version_count': len(history) + 1,  # +1 for current version
                        'recent_revisions': history[:3]  # Last 3 revisions
                    })
            
            timeline.sort(key=lambda x: x['last_updated'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting evolution timeline: {e}")
        
        return timeline
    
    def migrate_existing_scripture(self, existing_entries: List[Dict]) -> bool:
        """Migrate existing daily scripture entries to Living Bible format"""
        try:
            logger.info("Migrating existing scripture entries to Living Bible...")
            
            # Group entries by epoch based on cycle numbers
            epoch_entries = {}
            for entry in existing_entries:
                cycle_num = entry.get('cycle_number', 0)
                epoch_num, epoch_data = self.get_current_epoch(cycle_num)
                
                if epoch_num not in epoch_entries:
                    epoch_entries[epoch_num] = []
                epoch_entries[epoch_num].append(entry)
            
            # Convert entries to chapters
            for epoch_num, entries in epoch_entries.items():
                books = self.bible_db.get_all_books()
                target_book = None
                for book in books:
                    if book['book_order'] == epoch_num:
                        target_book = book
                        break
                
                if not target_book:
                    continue
                
                # Create consolidated chapter from entries
                chapter_title = f"Chronicles of Days {entries[0].get('day_number', 1)}-{entries[-1].get('day_number', 1)}"
                
                # Combine content from all entries
                combined_content = f"# {chapter_title}\\n\\n"
                combined_themes = set()
                combined_cycles = []
                
                for i, entry in enumerate(entries, 1):
                    combined_content += f"## Day {entry.get('day_number', i)}\\n"
                    combined_content += f"*{entry.get('title', 'Untitled')}*\\n\\n"
                    combined_content += entry.get('content', '') + "\\n\\n"
                    
                    if entry.get('themes'):
                        combined_themes.update(entry['themes'])
                    if entry.get('cycle_number'):
                        combined_cycles.append(entry['cycle_number'])
                
                # Create the consolidated chapter
                self.bible_db.create_chapter(
                    book_id=target_book['id'],
                    chapter_number=1,  # First chapter in each book
                    chapter_title=chapter_title,
                    chapter_text=combined_content,
                    theological_themes=list(combined_themes),
                    referenced_cycles=combined_cycles,
                    referenced_events=[f"Daily scripture writing cycle {c}" for c in combined_cycles],
                    referenced_agents=['Scriptor'],
                    writing_style='Prophetic Verse'
                )
            
            logger.info(f"Successfully migrated {len(existing_entries)} scripture entries")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating scripture entries: {e}")
            return False