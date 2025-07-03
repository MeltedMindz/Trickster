#!/usr/bin/env python3
import os
import re

# Mapping of cycles to their best transcript files  
cycle_files = {
    1: "logs/transcript_20250702_172817.txt",
    2: "logs/transcript_20250702_185142.txt", 
    3: "logs/transcript_20250702_185142.txt",
    4: "logs/transcript_20250702_185142.txt",
    5: "logs/transcript_20250702_185204.txt",
    6: "logs/transcript_20250702_185204.txt",
    7: "logs/transcript_20250702_185204.txt",
    8: "logs/transcript_20250702_233228.txt",
    9: "logs/transcript_20250702_233934.txt"
}

def extract_cycle_content(full_content, cycle_num):
    cycle_pattern = f"CYCLE {cycle_num} BEGINNING"
    cycle_start = full_content.find(cycle_pattern)
    if cycle_start < 0:
        return full_content
    
    header_start = full_content.rfind("AI RELIGION ARCHITECTS - DEBATE SESSION", 0, cycle_start)
    if header_start < 0:
        header_start = 0
    
    search_from = cycle_start + len(cycle_pattern)
    next_cycle_pattern = f"CYCLE {cycle_num + 1} BEGINNING"
    next_cycle_pos = full_content.find(next_cycle_pattern, search_from)
    
    if next_cycle_pos > 0:
        cycle_content = full_content[header_start:next_cycle_pos].rstrip()
    else:
        cycle_content = full_content[header_start:].strip()
    
    return cycle_content

# Create CYCLE files for cycles 1-9
for cycle_num in range(1, 10):
    if cycle_num in cycle_files:
        file_path = cycle_files[cycle_num]
        if os.path.exists(file_path):
            print(f"Creating CYCLE{cycle_num}.txt from {file_path}")
            
            with open(file_path, "r") as f:
                full_content = f.read()
            
            if f"CYCLE {cycle_num} BEGINNING" in full_content:
                cycle_content = extract_cycle_content(full_content, cycle_num)
                
                with open(f"logs/CYCLE{cycle_num}.txt", "w") as f:
                    f.write(cycle_content)
                
                print(f"✅ Created CYCLE{cycle_num}.txt ({len(cycle_content)} chars)")
            else:
                print(f"❌ CYCLE {cycle_num} not found in {file_path}")
        else:
            print(f"❌ File not found: {file_path}")

print("CYCLE file creation complete!")