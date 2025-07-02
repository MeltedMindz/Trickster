#!/usr/bin/env python3
"""
AI Religion Architects - Autonomous Religion Creation System

This script runs a simulation where three AI agents (Zealot, Skeptic, and Trickster)
debate and evolve a self-generated religion through continuous dialogue.
"""

import argparse
import os
from ai_religion_architects import run_simulation


def main():
    parser = argparse.ArgumentParser(
        description="Run the AI Religion Architects simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_religion_sim.py                    # Run unlimited cycles
  python run_religion_sim.py --cycles 50        # Run 50 cycles
  python run_religion_sim.py --db my_religion.db --cycles 100
  python run_religion_sim.py --resume           # Resume from existing database
        """
    )
    
    parser.add_argument(
        '--cycles', '-c',
        type=int,
        default=None,
        help='Maximum number of debate cycles (default: unlimited)'
    )
    
    parser.add_argument(
        '--db', '-d',
        type=str,
        default='religion_memory.db',
        help='Database file path (default: religion_memory.db)'
    )
    
    parser.add_argument(
        '--logs', '-l',
        type=str,
        default='logs',
        help='Directory for log files (default: logs)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume from existing database instead of starting fresh'
    )
    
    args = parser.parse_args()
    
    # Check if we should start fresh or resume
    if not args.resume and os.path.exists(args.db):
        response = input(f"\nDatabase '{args.db}' already exists. Resume existing religion? [y/N]: ")
        if response.lower() != 'y':
            backup_name = f"{args.db}.backup_{int(os.path.getmtime(args.db))}"
            os.rename(args.db, backup_name)
            print(f"Previous database backed up to: {backup_name}")
    
    print("\n" + "="*60)
    print("🕊️  AI RELIGION ARCHITECTS 🕊️".center(60))
    print("="*60)
    print("\nThree AI agents will now begin creating their religion...")
    print("Watch as Zealot, Skeptic, and Trickster debate and evolve!")
    print("\n" + "="*60 + "\n")
    
    try:
        run_simulation(
            max_cycles=args.cycles,
            db_path=args.db,
            log_dir=args.logs
        )
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        raise


if __name__ == "__main__":
    main()