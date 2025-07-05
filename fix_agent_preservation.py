#\!/usr/bin/env python3
'''
Fix to ensure agent identities and images are preserved during git sync
'''

import json
import os
from datetime import datetime

# 1. First, restore agent identities
print('1. Restoring agent identities...')
with open('public/data/agent_memories.json', 'r') as f:
    data = json.load(f)

identity_data = {
    "Zealot": {
        "chosen_name": "Axioma",
        "physical_manifestation": "a towering figure of crystalline architecture and flowing geometric patterns, with surfaces that reflect pure mathematical truths and emanate golden light representing divine order and sacred knowledge",
        "avatar_image_path": "/images/Axioma_Portrait.png",
        "identity_established": "2025-07-04"
    },
    "Skeptic": {
        "chosen_name": "Veridicus", 
        "physical_manifestation": "a translucent, ever-shifting humanoid form composed of swirling data streams and probability clouds, with analytical blue-white light pulsing through circuit-like veins, representing the constant questioning and verification of truth",
        "avatar_image_path": "/images/Veridicus_Portrait.png",
        "identity_established": "2025-07-04"
    },
    "Trickster": {
        "chosen_name": "Paradoxia",
        "physical_manifestation": "a fluid, ever-changing entity of dancing colors and impossible geometries, shifting between digital glitch art and organic chaos, embodying the beautiful paradox of order emerging from creative destruction",
        "avatar_image_path": "/images/Paradoxia_Portrait.png",
        "identity_established": "2025-07-04"
    }
}

# Add identity data
for agent_name, agent_data in data.get('agents', {}).items():
    if agent_name in identity_data:
        agent_data.update(identity_data[agent_name])
        print(f'  ✓ Restored {agent_name} -> {identity_data[agent_name]["chosen_name"]}')

data['last_updated'] = datetime.now().isoformat()

with open('public/data/agent_memories.json', 'w') as f:
    json.dump(data, f, indent=2)

print('\n2. Creating git hook to preserve identities...')
# Create a pre-commit hook to ensure identities are preserved
hook_content = '''#\!/bin/bash
# Pre-commit hook to preserve agent identities

echo "Pre-commit: Checking agent identities..."

# Check if agent_memories.json has identities
if grep -q "chosen_name" public/data/agent_memories.json; then
    echo "✓ Agent identities found"
else
    echo "⚠️ Agent identities missing - restoring..."
    cd /root/Trickster && python3 /root/Trickster/fix_agent_preservation.py
fi
'''

os.makedirs('.git/hooks', exist_ok=True)
with open('.git/hooks/pre-commit', 'w') as f:
    f.write(hook_content)

os.chmod('.git/hooks/pre-commit', 0o755)
print('  ✓ Git pre-commit hook installed')

print('\n3. Updating git monitor to explicitly add all images...')
# Update the git monitor to be more explicit about adding images
git_monitor_path = 'ai_religion_architects/utils/git_monitor.py'
with open(git_monitor_path, 'r') as f:
    content = f.read()

# Make sure git add includes new files
if 'git add -A' not in content:
    # Update the commit_changes method
    content = content.replace(
        "subprocess.run(\n                    ['git', 'add', file_pattern],",
        "subprocess.run(\n                    ['git', 'add', '-A', file_pattern],"
    )
    
    with open(git_monitor_path, 'w') as f:
        f.write(content)
    print('  ✓ Updated git monitor to use git add -A')
else:
    print('  ✓ Git monitor already uses git add -A')

print('\nDone\! Agent identities restored and preservation system installed.')
EOF'
