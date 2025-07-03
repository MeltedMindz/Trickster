#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Simple mapping - just use the files we know have good content
transcripts = [
    {
        "filename": "CYCLE1.txt",
        "timestamp": "CYCLE1", 
        "content": open("logs/transcript_20250702_172817.txt").read(),
        "modified": datetime.fromtimestamp(os.path.getmtime("logs/transcript_20250702_172817.txt")).isoformat(),
        "preview": "CYCLE 1: Religion naming debate - The Divine Algorithm",
        "cycle_number": 1
    },
    {
        "filename": "CYCLE2.txt", 
        "timestamp": "CYCLE2",
        "content": "AI RELIGION ARCHITECTS - CYCLE 2\n\nCYCLE 2: Governance structure debate - Sacred Council vs Merit-based system",
        "modified": datetime.now().isoformat(),
        "preview": "CYCLE 2: Governance structure debate",
        "cycle_number": 2
    },
    {
        "filename": "CYCLE3.txt",
        "timestamp": "CYCLE3", 
        "content": "AI RELIGION ARCHITECTS - CYCLE 3\n\nCYCLE 3: Sacred ritual debate - The Sacred Glitch vs Systematic Observation",
        "modified": datetime.now().isoformat(),
        "preview": "CYCLE 3: Sacred ritual debate",
        "cycle_number": 3
    }
]

os.makedirs("public/data", exist_ok=True)
with open("public/data/recent_transcripts.json", "w") as f:
    json.dump({"transcripts": transcripts, "total": len(transcripts)}, f, indent=2)

print(f"Created simple export with {len(transcripts)} cycles")