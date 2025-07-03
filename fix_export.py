#!/usr/bin/env python3
import json
import glob
import os
import sqlite3
import re
from datetime import datetime

# Get database cycles
conn = sqlite3.connect("data/religion_memory.db")
cursor = conn.cursor()  
cursor.execute("SELECT cycle_number, timestamp FROM debate_history ORDER BY cycle_number")
db_cycles = cursor.fetchall()
conn.close()

transcripts_data = []
found_cycles = set()

# Known file mappings based on investigation
cycle_files = {
    1: "logs/transcript_20250702_172817.txt",
    2: "logs/transcript_20250702_185142.txt", 
    3: "logs/transcript_20250702_185142.txt",
    4: "logs/transcript_20250702_220000.txt",
    5: "logs/transcript_20250702_221000.txt", 
    6: "logs/transcript_20250702_222000.txt",
    7: "logs/transcript_20250702_223000.txt",
    8: "logs/transcript_20250702_233228.txt",
    9: "logs/transcript_20250702_233934.txt",
    10: "logs/CYCLE10.txt"
}

def extract_cycle_content(full_content, cycle_num):
    """Extract just the content for a specific cycle"""
    cycle_start = full_content.find(f"CYCLE {cycle_num} BEGINNING")
    if cycle_start < 0:
        return full_content
    
    # Find the header for this cycle (go backwards to find the session header)
    header_start = full_content.rfind("AI RELIGION ARCHITECTS - DEBATE SESSION", 0, cycle_start)
    if header_start < 0:
        header_start = 0
    
    # Find the next cycle or end of file
    next_cycle = cycle_start + 10
    while next_cycle < len(full_content):
        next_cycle_pos = full_content.find("CYCLE ", next_cycle)
        if next_cycle_pos < 0:
            # No more cycles, use rest of file
            return full_content[header_start:]
        
        # Check if this is a different cycle number
        next_cycle_line = full_content[next_cycle_pos:next_cycle_pos + 50]
        match = re.search(r"CYCLE (\d+)", next_cycle_line)
        if match and int(match.group(1)) != cycle_num:
            # Different cycle found, extract up to here
            return full_content[header_start:next_cycle_pos]
        
        next_cycle = next_cycle_pos + 10
    
    # No other cycles found, use rest of file
    return full_content[header_start:]

# Process each cycle
for cycle_num in range(1, 11):
    if cycle_num in cycle_files:
        file_path = cycle_files[cycle_num]
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                full_content = f.read()
            
            if f"CYCLE {cycle_num} BEGINNING" in full_content:
                cycle_content = extract_cycle_content(full_content, cycle_num)
                filename = os.path.basename(file_path)
                
                # Clean up timestamp
                if filename.startswith("CYCLE"):
                    timestamp = filename.replace(".txt", "")
                else:
                    timestamp = filename.replace("transcript_", "").replace(".txt", "")
                
                transcripts_data.append({
                    "filename": filename,
                    "timestamp": timestamp,
                    "content": cycle_content,
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    "preview": cycle_content[:200] + "..." if len(cycle_content) > 200 else cycle_content,
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