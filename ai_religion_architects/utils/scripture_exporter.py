import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from ..memory.sacred_scripture_db import SacredScriptureDatabase

logger = logging.getLogger(__name__)


class ScriptureExporter:
    """
    Utility class for exporting sacred scripture data to JSON files
    for frontend consumption.
    """
    
    def __init__(self, scripture_db_path: str = "data/sacred_scripture.db"):
        self.scripture_db = SacredScriptureDatabase(scripture_db_path)
        
    def export_for_frontend(self, output_dir: str = "public/data") -> Dict[str, Any]:
        """Export comprehensive scripture data for frontend"""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Get comprehensive data
            scripture_data = self._compile_scripture_data()
            
            # Export main scripture file
            main_file = os.path.join(output_dir, "sacred_scripture.json")
            self._write_json_file(main_file, scripture_data)
            
            # Export theme index
            theme_file = os.path.join(output_dir, "scripture_themes.json")
            self._write_json_file(theme_file, scripture_data["themes_index"])
            
            # Export agent portrayals
            portrayal_file = os.path.join(output_dir, "scripture_agent_portrayals.json")
            self._write_json_file(portrayal_file, scripture_data["agent_portrayals"])
            
            logger.info(f"📚 Scripture data exported to {output_dir}")
            return scripture_data
            
        except Exception as e:
            logger.error(f"❌ Failed to export scripture data: {e}")
            return {"error": str(e)}
    
    def _compile_scripture_data(self) -> Dict[str, Any]:
        """Compile comprehensive scripture data"""
        # Get basic scripture data
        recent_scriptures = self.scripture_db.get_scripture_entries(limit=50)
        themes_summary = self.scripture_db.get_themes_summary(limit=30)
        agent_portrayals = self.scripture_db.get_agent_portrayals(limit=100)
        statistics = self.scripture_db.get_scripture_statistics()
        
        # Compile for frontend
        return {
            "scripture_entries": self._format_scriptures_for_frontend(recent_scriptures),
            "themes_index": self._format_themes_for_frontend(themes_summary),
            "agent_portrayals": self._format_portrayals_for_frontend(agent_portrayals),
            "statistics": statistics,
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_entries": len(recent_scriptures),
                "export_version": "1.0"
            }
        }
    
    def _format_scriptures_for_frontend(self, scriptures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format scripture entries for frontend display"""
        formatted = []
        
        for scripture in scriptures:
            # Create excerpt for preview
            content = scripture.get('content', '')
            excerpt = self._create_excerpt(content, max_length=200)
            
            # Format for frontend
            formatted_scripture = {
                "id": scripture.get('id'),
                "cycle_number": scripture.get('cycle_number'),
                "title": scripture.get('title', f"Scripture {scripture.get('cycle_number')}"),
                "excerpt": excerpt,
                "full_content": content,
                "scripture_type": scripture.get('scripture_type', 'Daily Chronicle'),
                "poetic_style": scripture.get('poetic_style', 'Mystical Prose'),
                "themes": scripture.get('themes', []),
                "mystical_elements": scripture.get('mystical_elements', []),
                "referenced_agents": scripture.get('referenced_agents', []),
                "referenced_doctrines": scripture.get('referenced_doctrines', []),
                "word_count": scripture.get('word_count', 0),
                "verse_count": scripture.get('verse_count', 0),
                "created_at": scripture.get('created_at'),
                "scriptor_mood": scripture.get('scriptor_mood', 'contemplative'),
                "display_metadata": {
                    "is_recent": scripture.get('cycle_number', 0) > (max([s.get('cycle_number', 0) for s in scriptures]) - 10) if scriptures else False,
                    "has_agent_references": len(scripture.get('referenced_agents', [])) > 0,
                    "theme_count": len(scripture.get('themes', [])),
                    "mystical_density": len(scripture.get('mystical_elements', [])) / max(1, scripture.get('word_count', 1))
                }
            }
            
            formatted.append(formatted_scripture)
        
        return formatted
    
    def _format_themes_for_frontend(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format themes for frontend display"""
        # Group themes by frequency
        theme_groups = {
            "dominant": [],  # frequency > 3
            "emerging": [],  # frequency 2-3
            "nascent": []    # frequency 1
        }
        
        for theme in themes:
            frequency = theme.get('frequency_count', 0)
            theme_data = {
                "name": theme.get('theme_name'),
                "description": theme.get('theme_description'),
                "frequency": frequency,
                "first_appearance": theme.get('first_appearance'),
                "last_appearance": theme.get('last_appearance'),
                "importance_score": theme.get('importance_score', 0.0),
                "associated_cycles": theme.get('associated_cycles', [])
            }
            
            if frequency > 3:
                theme_groups["dominant"].append(theme_data)
            elif frequency >= 2:
                theme_groups["emerging"].append(theme_data)
            else:
                theme_groups["nascent"].append(theme_data)
        
        return {
            "grouped_themes": theme_groups,
            "all_themes": themes,
            "theme_statistics": {
                "total_themes": len(themes),
                "dominant_count": len(theme_groups["dominant"]),
                "emerging_count": len(theme_groups["emerging"]),
                "nascent_count": len(theme_groups["nascent"])
            }
        }
    
    def _format_portrayals_for_frontend(self, portrayals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format agent portrayals for frontend display"""
        # Group by agent
        by_agent = {}
        for portrayal in portrayals:
            agent_name = portrayal.get('agent_name')
            if agent_name not in by_agent:
                by_agent[agent_name] = []
            by_agent[agent_name].append(portrayal)
        
        # Calculate statistics per agent
        agent_stats = {}
        for agent_name, agent_portrayals in by_agent.items():
            reverence_levels = [p.get('reverence_level', 0.5) for p in agent_portrayals]
            agent_stats[agent_name] = {
                "total_portrayals": len(agent_portrayals),
                "average_reverence": sum(reverence_levels) / len(reverence_levels) if reverence_levels else 0.5,
                "recent_portrayals": sorted(agent_portrayals, key=lambda x: x.get('cycle_number', 0), reverse=True)[:5],
                "most_common_role": self._get_most_common_role(agent_portrayals)
            }
        
        return {
            "by_agent": by_agent,
            "agent_statistics": agent_stats,
            "portrayal_summary": {
                "total_portrayals": len(portrayals),
                "agents_portrayed": list(by_agent.keys()),
                "most_portrayed": max(by_agent.keys(), key=lambda k: len(by_agent[k])) if by_agent else None
            }
        }
    
    def _get_most_common_role(self, portrayals: List[Dict[str, Any]]) -> str:
        """Get the most common narrative role for an agent"""
        roles = [p.get('narrative_role', 'Unknown') for p in portrayals]
        if not roles:
            return "Unknown"
        
        # Count roles
        role_counts = {}
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Return most common
        return max(role_counts.keys(), key=lambda k: role_counts[k])
    
    def _create_excerpt(self, content: str, max_length: int = 200) -> str:
        """Create an excerpt from scripture content"""
        if not content:
            return ""
        
        # Split into sentences and take complete sentences until we reach limit
        sentences = content.split('.')
        excerpt = ""
        
        for sentence in sentences:
            if len(excerpt + sentence + ".") <= max_length:
                excerpt += sentence + "."
            else:
                break
        
        # If excerpt is empty (first sentence too long), truncate
        if not excerpt and content:
            excerpt = content[:max_length - 3] + "..."
        
        return excerpt.strip()
    
    def _write_json_file(self, filepath: str, data: Any):
        """Write data to JSON file with proper formatting"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, separators=(',', ': '))
    
    def export_scripture_search_index(self, output_dir: str = "public/data") -> Dict[str, Any]:
        """Export a search index for scripture content"""
        try:
            # Get all scriptures
            all_scriptures = self.scripture_db.get_scripture_entries(limit=1000)
            
            # Build search index
            search_index = []
            for scripture in all_scriptures:
                # Create searchable text
                searchable_text = f"{scripture.get('title', '')} {scripture.get('content', '')}"
                searchable_text += f" {' '.join(scripture.get('themes', []))}"
                searchable_text += f" {' '.join(scripture.get('mystical_elements', []))}"
                
                search_entry = {
                    "id": scripture.get('id'),
                    "cycle_number": scripture.get('cycle_number'),
                    "title": scripture.get('title'),
                    "searchable_text": searchable_text.lower(),
                    "themes": scripture.get('themes', []),
                    "agents": scripture.get('referenced_agents', []),
                    "word_count": scripture.get('word_count', 0)
                }
                
                search_index.append(search_entry)
            
            # Export search index
            search_file = os.path.join(output_dir, "scripture_search_index.json")
            self._write_json_file(search_file, {
                "search_index": search_index,
                "metadata": {
                    "total_entries": len(search_index),
                    "last_updated": datetime.now().isoformat()
                }
            })
            
            logger.info(f"🔍 Scripture search index exported to {search_file}")
            return {"search_index": search_index}
            
        except Exception as e:
            logger.error(f"❌ Failed to export search index: {e}")
            return {"error": str(e)}