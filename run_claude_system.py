#!/usr/bin/env python3
"""
AI Religion Architects - Claude API System Launcher

Launch the complete system with Claude API integration including:
- APScheduler for hourly debate cycles
- Claude API for intelligent agent responses
- WebSocket server for real-time monitoring
- Proper error handling and retry logic
"""

import asyncio
import argparse
import os
import sys
import signal
import subprocess
import time
from pathlib import Path

# Add the ai_religion_architects module to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration first to validate environment
from ai_religion_architects.config import init_config, Config
from ai_religion_architects.orchestration.claude_orchestrator import run_claude_orchestrator


def check_websocket_server(port=8000):
    """Check if WebSocket server is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False


def start_websocket_server():
    """Start the WebSocket server in background"""
    backend_dir = Path(__file__).parent / "backend"
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return None
    
    try:
        print("🔌 Starting WebSocket server...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "websocket_server:app", 
            "--host", "0.0.0.0", 
            "--port", str(Config.WEBSOCKET_PORT)
        ], cwd=backend_dir)
        
        # Wait for server to start
        for _ in range(10):
            if check_websocket_server(Config.WEBSOCKET_PORT):
                print("✅ WebSocket server started successfully")
                return process
            time.sleep(1)
        
        print("⚠️  WebSocket server may not have started properly")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start WebSocket server: {e}")
        return None


async def main():
    parser = argparse.ArgumentParser(
        description="Launch AI Religion Architects with Claude API integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables Required:
  CLAUDE_API_KEY - Your Anthropic Claude API key
  
Optional Environment Variables:
  CLAUDE_MODEL - Claude model to use (default: claude-3-sonnet-20240229)
  CYCLE_INTERVAL_HOURS - Hours between debate cycles (default: 1)
  CLAUDE_MAX_TOKENS - Max tokens per response (default: 2000)

Examples:
  python run_claude_system.py                     # Run with defaults (1 hour cycles)
  python run_claude_system.py --no-websocket      # Skip WebSocket server
  python run_claude_system.py --test-cycle        # Run one test cycle and exit
        """
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default=None,
        help=f'Database file path (default: {Config.DB_PATH})'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default=None,
        help=f'Log directory (default: {Config.LOG_DIR})'
    )
    
    parser.add_argument(
        '--no-websocket',
        action='store_true',
        help='Skip starting WebSocket server'
    )
    
    parser.add_argument(
        '--test-cycle',
        action='store_true',
        help='Run one test cycle and exit (for testing)'
    )
    
    args = parser.parse_args()
    
    print("🕊️" + "="*70 + "🕊️")
    print("   AI RELIGION ARCHITECTS - CLAUDE API SYSTEM   ".center(72))
    print("🕊️" + "="*70 + "🕊️")
    print()
    
    # Initialize configuration
    try:
        init_config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure you have:")
        print("1. Set CLAUDE_API_KEY environment variable")
        print("2. Created a .env file with your configuration")
        print("3. Installed requirements: pip install -r requirements-backend.txt")
        return 1
    
    # Display configuration summary
    config_summary = Config.get_summary()
    print(f"📊 System Configuration:")
    print(f"   Claude Model: {config_summary['claude_model']}")
    print(f"   Max Tokens: {config_summary['claude_max_tokens']}")
    print(f"   Cycle Interval: {config_summary['cycle_interval_hours']} hour(s)")
    print(f"   Database: {config_summary['db_path']}")
    print(f"   API Key Configured: {'✅' if config_summary['api_key_configured'] else '❌'}")
    print()
    
    if not config_summary['api_key_configured']:
        print("❌ CLAUDE_API_KEY is not configured!")
        print("Please set your Claude API key in the environment or .env file")
        return 1
    
    websocket_process = None
    
    try:
        # Start WebSocket server if needed
        if not args.no_websocket and not check_websocket_server(Config.WEBSOCKET_PORT):
            websocket_process = start_websocket_server()
            if not websocket_process:
                print("⚠️  Continuing without WebSocket server...")
        elif check_websocket_server(Config.WEBSOCKET_PORT):
            print("✅ WebSocket server already running")
        else:
            print("ℹ️  Skipping WebSocket server startup")
        
        print()
        print("🚀 Starting Claude-powered orchestrator...")
        print(f"   Next cycle will run in: {Config.CYCLE_INTERVAL_HOURS} hour(s)")
        print(f"   WebSocket monitoring: http://localhost:{Config.WEBSOCKET_PORT}")
        print()
        print("🔄 APScheduler will handle timing - NO INFINITE LOOPS")
        print("Press Ctrl+C to stop gracefully")
        print("="*72)
        
        # For testing, we could run a single cycle
        if args.test_cycle:
            print("🧪 Running test cycle...")
            from ai_religion_architects.orchestration.claude_orchestrator import ClaudeReligionOrchestrator
            orchestrator = ClaudeReligionOrchestrator(args.db_path, args.log_dir)
            await orchestrator._run_scheduled_cycle()
            print("✅ Test cycle completed")
            return 0
        
        # Run the Claude orchestrator with APScheduler
        await run_claude_orchestrator(
            db_path=args.db_path,
            log_dir=args.log_dir
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Graceful shutdown initiated...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean up WebSocket server
        if websocket_process:
            print("🔌 Stopping WebSocket server...")
            websocket_process.terminate()
            try:
                websocket_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                websocket_process.kill()
        
        print("✨ AI Religion Architects (Claude) stopped")
        return 0


if __name__ == "__main__":
    # Handle signals gracefully
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the async main
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutdown complete.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)