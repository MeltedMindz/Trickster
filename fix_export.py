#!/usr/bin/env python3
import json
import glob
import os
import sqlite3
import re
from datetime import datetime

# Skip database check for local fix
db_cycles = []

transcripts_data = []
found_cycles = set()

# Only look for CYCLE files - ignore old timestamp files
cycle_files = glob.glob("logs/CYCLE*.txt")

# Process each CYCLE file
for file_path in cycle_files:
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        # Extract cycle number from filename (CYCLE1.txt -> 1)
        cycle_match = re.search(r'CYCLE(\d+)', filename)
        if cycle_match:
            cycle_num = int(cycle_match.group(1))
            
            with open(file_path, "r") as f:
                content = f.read()
            
            transcripts_data.append({
                "filename": filename,
                "timestamp": f"CYCLE{cycle_num}",
                "content": content,
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                "preview": content[:200] + "..." if len(content) > 200 else content,
                "cycle_number": cycle_num
            })
            found_cycles.add(cycle_num)

# Sort by cycle number
transcripts_data.sort(key=lambda x: x.get("cycle_number", 0))

print(f"Found cycles: {sorted(found_cycles)}")
print(f"Total transcripts: {len(transcripts_data)}")

# Save the corrected export
os.makedirs("public/data", exist_ok=True)
with open("public/data/recent_transcripts.json", "w") as f:
    json.dump({"transcripts": transcripts_data, "total": len(transcripts_data)}, f, indent=2)

print("Complete export finished!")