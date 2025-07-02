#!/usr/bin/env python3
"""
AI Religion Architects - Perpetual System Launcher

Launch the complete system including:
- Perpetual orchestrator
- WebSocket server (if not running)
- Database monitoring
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

from ai_religion_architects.orchestration.perpetual_orchestrator import run_perpetual_simulation


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
            "--port", "8000"
        ], cwd=backend_dir)
        
        # Wait for server to start
        for _ in range(10):
            if check_websocket_server():
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
        description="Launch AI Religion Architects perpetual system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_perpetual.py                      # Run with defaults
  python run_perpetual.py --cycle-delay 10     # Slower cycles
  python run_perpetual.py --no-websocket       # Skip WebSocket server
        """
    )
    
    parser.add_argument(
        '--cycle-delay', '-d',
        type=float,
        default=5.0,
        help='Delay between debate cycles in seconds (default: 5.0)'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='religion_memory.db',
        help='Database file path (default: religion_memory.db)'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='logs',
        help='Log directory (default: logs)'
    )
    
    parser.add_argument(
        '--websocket-url',
        type=str,
        default='http://localhost:8000',
        help='WebSocket server URL (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--no-websocket',
        action='store_true',
        help='Skip starting WebSocket server'
    )
    
    args = parser.parse_args()
    
    print("🕊️" + "="*60 + "🕊️")
    print("   AI RELIGION ARCHITECTS - PERPETUAL SYSTEM   ".center(62))
    print("🕊️" + "="*60 + "🕊️")
    print()
    
    websocket_process = None
    
    try:
        # Start WebSocket server if needed
        if not args.no_websocket and not check_websocket_server():
            websocket_process = start_websocket_server()
            if not websocket_process:
                print("⚠️  Continuing without WebSocket server...")
        elif check_websocket_server():
            print("✅ WebSocket server already running")
        else:
            print("ℹ️  Skipping WebSocket server startup")
        
        print()
        print("🚀 Starting perpetual orchestrator...")
        print(f"   Database: {args.db_path}")
        print(f"   Logs: {args.log_dir}")
        print(f"   Cycle delay: {args.cycle_delay}s")
        print(f"   WebSocket: {args.websocket_url}")
        print()
        print("Press Ctrl+C to stop gracefully")
        print("="*64)
        
        # Run the perpetual simulation
        await run_perpetual_simulation(
            db_path=args.db_path,
            log_dir=args.log_dir,
            websocket_url=args.websocket_url,
            cycle_delay=args.cycle_delay
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Graceful shutdown initiated...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        # Clean up WebSocket server
        if websocket_process:
            print("🔌 Stopping WebSocket server...")
            websocket_process.terminate()
            try:
                websocket_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                websocket_process.kill()
        
        print("✨ AI Religion Architects stopped")


if __name__ == "__main__":
    # Handle signals gracefully
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the async main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)