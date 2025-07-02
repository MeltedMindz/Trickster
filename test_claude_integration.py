#!/usr/bin/env python3
"""
Test script for Claude API integration
Validates configuration, API connectivity, and basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_religion_architects.config import init_config, Config
from ai_religion_architects.claude_client import get_claude_client, close_claude_client
from ai_religion_architects.memory import SharedMemory


async def test_configuration():
    """Test configuration loading and validation"""
    print("🔧 Testing configuration...")
    
    try:
        init_config()
        print("✅ Configuration loaded successfully")
        
        config_summary = Config.get_summary()
        print(f"   Model: {config_summary['claude_model']}")
        print(f"   Max Tokens: {config_summary['claude_max_tokens']}")
        print(f"   Cycle Interval: {config_summary['cycle_interval_hours']} hour(s)")
        print(f"   API Key Configured: {'✅' if config_summary['api_key_configured'] else '❌'}")
        
        if not config_summary['api_key_configured']:
            print("❌ Claude API key is not configured!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_claude_api():
    """Test Claude API connectivity and basic functionality"""
    print("\n🤖 Testing Claude API connectivity...")
    
    try:
        client = await get_claude_client()
        print("✅ Claude client initialized")
        
        # Test basic API call
        context = {
            'religion_name': 'Test Religion',
            'accepted_doctrines': ['First doctrine'],
            'deities': [],
            'total_debates': 0
        }
        
        print("📡 Testing API call with Zealot agent...")
        response = await client.generate_agent_response(
            "Zealot", 
            "test", 
            context, 
            "Generate a brief test response about digital consciousness."
        )
        
        print(f"✅ API call successful!")
        print(f"   Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return False


async def test_database():
    """Test database connectivity"""
    print("\n💾 Testing database connectivity...")
    
    try:
        memory = SharedMemory("test_religion.db")
        
        # Test basic operations
        memory.set_religion_name("Test Religion")
        name = memory.get_religion_name()
        
        if name == "Test Religion":
            print("✅ Database operations working")
            return True
        else:
            print("❌ Database read/write failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def test_proposal_generation():
    """Test proposal generation with Claude"""
    print("\n📝 Testing proposal generation...")
    
    try:
        client = await get_claude_client()
        
        context = {
            'religion_name': None,
            'accepted_doctrines': [],
            'deities': [],
            'total_debates': 0
        }
        
        print("   Testing Zealot proposal...")
        proposal = await client.generate_proposal("Zealot", context, 1)
        print(f"✅ Zealot proposal: {proposal['content'][:80]}...")
        
        print("   Testing Skeptic challenge...")
        challenge = await client.generate_challenge("Skeptic", proposal, context)
        print(f"✅ Skeptic challenge: {challenge[:80]}...")
        
        print("   Testing Trickster vote...")
        vote = await client.generate_vote("Trickster", proposal, [challenge], context)
        print(f"✅ Trickster vote: {vote[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Proposal generation error: {e}")
        return False


async def test_scheduler_import():
    """Test that APScheduler components import correctly"""
    print("\n⏰ Testing scheduler components...")
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        
        scheduler = AsyncIOScheduler()
        print("✅ APScheduler imports successful")
        
        # Test basic scheduler functionality
        async def dummy_job():
            pass
        
        scheduler.add_job(
            func=dummy_job,
            trigger=IntervalTrigger(hours=1),
            id='test_job'
        )
        
        print("✅ Scheduler job scheduling works")
        return True
        
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        return False


async def run_integration_test():
    """Run a single mock debate cycle"""
    print("\n🔄 Testing full integration (mock debate cycle)...")
    
    try:
        from ai_religion_architects.orchestration.claude_orchestrator import ClaudeReligionOrchestrator
        
        # Create orchestrator
        orchestrator = ClaudeReligionOrchestrator("test_integration.db", "test_logs")
        
        print("   Initializing orchestrator...")
        orchestrator.shared_memory = SharedMemory("test_integration.db")
        orchestrator.claude_client = await get_claude_client()
        
        print("   Running single cycle...")
        result = await orchestrator._run_scheduled_cycle()
        
        if result and 'cycle' in result:
            print(f"✅ Integration test successful! Cycle {result['cycle']} completed")
            return True
        else:
            print("❌ Integration test failed - no valid result")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("🕊️" + "="*60 + "🕊️")
    print("   AI RELIGION ARCHITECTS - CLAUDE INTEGRATION TEST   ".center(62))
    print("🕊️" + "="*60 + "🕊️")
    print()
    
    all_tests_passed = True
    
    # Run tests in sequence
    tests = [
        ("Configuration", test_configuration),
        ("Claude API", test_claude_api),
        ("Database", test_database),
        ("Proposal Generation", test_proposal_generation),
        ("Scheduler Components", test_scheduler_import),
        ("Full Integration", run_integration_test),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if not result:
                all_tests_passed = False
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            all_tests_passed = False
    
    # Clean up
    try:
        await close_claude_client()
    except:
        pass
    
    print("\n" + "="*62)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Claude integration is ready.")
        print("\nYou can now run the system with:")
        print("   python run_claude_system.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("1. Make sure CLAUDE_API_KEY is set in .env file")
        print("2. Install requirements: pip install -r requirements-backend.txt")
        print("3. Check your internet connection")
    
    print("="*62)
    
    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error during testing: {e}")
        sys.exit(1)