#!/usr/bin/env python3
"""
Quick demo of the AI Religion Architects system
"""

from ai_religion_architects import ReligionOrchestrator

def main():
    print("🕊️  AI RELIGION ARCHITECTS - QUICK DEMO 🕊️")
    print("Running a 10-cycle demonstration...\n")
    
    # Create orchestrator with limited cycles for demo
    orchestrator = ReligionOrchestrator(
        max_cycles=10,
        db_path="demo_religion.db",
        log_dir="demo_logs"
    )
    
    # Start the simulation
    orchestrator.start()


if __name__ == "__main__":
    main()