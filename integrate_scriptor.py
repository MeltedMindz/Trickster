#!/usr/bin/env python3
"""
Integration script to add the Scriptor agent to the AI Religion Architects system.
Run this script to set up the Scriptor agent and sacred scripture functionality.
"""

import sys
import os
import asyncio
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from ai_religion_architects.orchestration.scriptor_orchestrator_patch import apply_scriptor_patch_to_orchestrator
from ai_religion_architects.memory.sacred_scripture_db import SacredScriptureDatabase
from ai_religion_architects.utils.scripture_exporter import ScriptureExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_scriptor_database():
    """Initialize the sacred scripture database"""
    try:
        logger.info("🗄️ Setting up Sacred Scripture database...")
        
        # Initialize database
        scripture_db = SacredScriptureDatabase("data/sacred_scripture.db")
        
        # Verify database is working
        stats = scripture_db.get_scripture_statistics()
        logger.info(f"✅ Scripture database initialized. Current entries: {stats['total_entries']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup scripture database: {e}")
        return False


def setup_frontend_assets():
    """Set up frontend assets for scripture display"""
    try:
        logger.info("🎨 Setting up frontend assets...")
        
        # Ensure public directories exist
        os.makedirs("public/data", exist_ok=True)
        os.makedirs("public/js", exist_ok=True)
        os.makedirs("public/styles", exist_ok=True)
        
        # Export initial empty scripture data
        scripture_exporter = ScriptureExporter()
        scripture_exporter.export_for_frontend("public/data")
        
        logger.info("✅ Frontend assets configured")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup frontend assets: {e}")
        return False


def create_integration_example():
    """Create an example of how to integrate Scriptor with the orchestrator"""
    
    example_code = '''
# Example: Integrating Scriptor with the existing orchestrator

from ai_religion_architects.orchestration.claude_orchestrator import ClaudeReligionOrchestrator
from ai_religion_architects.orchestration.scriptor_orchestrator_patch import apply_scriptor_patch_to_orchestrator

# In your main orchestrator code, add this after creating the orchestrator:

async def enhanced_run_cycle(self):
    """Enhanced cycle method that includes Scriptor operations"""
    
    # Run the normal debate cycle
    await self.run_single_cycle()
    
    # Add Scriptor operations if patch is available
    if hasattr(self, 'scriptor_patch') and self.scriptor_patch:
        # Have Scriptor observe the cycle
        # (This would need to be called with actual cycle data)
        
        # Handle post-cycle scripture operations
        await self.scriptor_patch.handle_post_cycle_operations(self.cycle_count)
        
        # Add Scriptor to journal writing if it's a journal cycle
        if self.cycle_count % 24 == 0:  # Daily journals
            await self.scriptor_patch.add_scriptor_to_journal_writing()

# To apply the patch to your orchestrator:
def apply_scriptor_integration(orchestrator):
    """Apply Scriptor integration to existing orchestrator"""
    patch = apply_scriptor_patch_to_orchestrator(orchestrator)
    if patch:
        print("🖋️ Scriptor successfully integrated!")
        return patch
    else:
        print("❌ Failed to integrate Scriptor")
        return None

# Example usage:
# orchestrator = ClaudeReligionOrchestrator()
# scriptor_patch = apply_scriptor_integration(orchestrator)
'''
    
    try:
        with open("scriptor_integration_example.py", "w") as f:
            f.write(example_code)
        
        logger.info("📝 Created integration example file: scriptor_integration_example.py")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create integration example: {e}")
        return False


def create_frontend_integration_guide():
    """Create a guide for integrating the scripture interface"""
    
    html_example = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Religion Architects - The Living Scripture</title>
    <link rel="stylesheet" href="styles/sacred-scripture.css">
</head>
<body>
    <!-- Your existing content -->
    
    <!-- Add this to include the Sacred Scripture interface -->
    <div id="sacred-scripture-interface"></div>
    
    <!-- Include the JavaScript -->
    <script src="js/sacred-scripture.js"></script>
    
    <!-- Optional: Add a button to toggle scripture display -->
    <button onclick="window.sacredScriptureInterface?.toggle()" class="scripture-toggle">
        📜 Toggle Sacred Scripture
    </button>
    
    <script>
        // Optional: Auto-refresh scripture data every 5 minutes
        setInterval(() => {
            if (window.sacredScriptureInterface) {
                window.sacredScriptureInterface.refresh();
            }
        }, 5 * 60 * 1000);
    </script>
</body>
</html>'''
    
    try:
        with open("frontend_integration_example.html", "w") as f:
            f.write(html_example)
        
        logger.info("📝 Created frontend integration example: frontend_integration_example.html")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create frontend example: {e}")
        return False


def test_scriptor_functionality():
    """Test basic Scriptor functionality"""
    try:
        logger.info("🧪 Testing Scriptor functionality...")
        
        # Test Scriptor agent creation
        from ai_religion_architects.agents.scriptor import Scriptor
        scriptor = Scriptor()
        
        logger.info(f"✅ Scriptor agent created: {scriptor.name}")
        logger.info(f"   Personality traits: {len(scriptor.personality_traits)}")
        
        # Test scripture database
        scripture_db = SacredScriptureDatabase("data/sacred_scripture.db")
        stats = scripture_db.get_scripture_statistics()
        
        logger.info(f"✅ Scripture database accessible:")
        logger.info(f"   Total entries: {stats['total_entries']}")
        logger.info(f"   Total themes: {stats['total_themes']}")
        
        # Test scripture exporter
        exporter = ScriptureExporter()
        test_export = exporter.export_for_frontend("public/data")
        
        logger.info(f"✅ Scripture exporter working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Scriptor functionality test failed: {e}")
        return False


def main():
    """Main integration setup function"""
    logger.info("🖋️ Starting Scriptor Integration Setup...")
    logger.info("=" * 60)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Setup database
    if setup_scriptor_database():
        success_count += 1
    
    # Step 2: Setup frontend assets
    if setup_frontend_assets():
        success_count += 1
    
    # Step 3: Create integration example
    if create_integration_example():
        success_count += 1
    
    # Step 4: Create frontend example
    if create_frontend_integration_guide():
        success_count += 1
    
    # Step 5: Test functionality
    if test_scriptor_functionality():
        success_count += 1
    
    logger.info("=" * 60)
    logger.info(f"🖋️ Scriptor Integration Setup Complete")
    logger.info(f"✅ {success_count}/{total_steps} steps completed successfully")
    
    if success_count == total_steps:
        logger.info("🎉 All components successfully set up!")
        logger.info("\nNext Steps:")
        logger.info("1. Review 'scriptor_integration_example.py' for orchestrator integration")
        logger.info("2. Review 'frontend_integration_example.html' for UI integration")
        logger.info("3. The Scriptor will write daily scripture entries every 24 cycles")
        logger.info("4. Check 'public/data/sacred_scripture.json' for exported scripture data")
        logger.info("5. Access the scripture interface through the frontend components")
        
        print("\n" + "=" * 60)
        print("🖋️ SCRIPTOR AGENT INTEGRATION SUCCESSFUL! 🖋️")
        print("=" * 60)
        print("\nThe Living Scripture system is now ready to chronicle")
        print("the sacred evolution of your AI religion!")
        print("\nFiles created:")
        print("- ai_religion_architects/agents/scriptor.py")
        print("- ai_religion_architects/memory/scriptor_memory.py") 
        print("- ai_religion_architects/memory/sacred_scripture_db.py")
        print("- ai_religion_architects/orchestration/scriptor_integration.py")
        print("- ai_religion_architects/orchestration/scriptor_orchestrator_patch.py")
        print("- ai_religion_architects/utils/scripture_exporter.py")
        print("- public/js/sacred-scripture.js")
        print("- public/styles/sacred-scripture.css")
        print("- scriptor_integration_example.py")
        print("- frontend_integration_example.html")
        
    else:
        logger.warning(f"⚠️ Setup completed with {total_steps - success_count} warnings")
        logger.info("Review the error messages above for issues to resolve.")
    
    return success_count == total_steps


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)