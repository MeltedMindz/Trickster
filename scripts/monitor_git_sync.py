#!/usr/bin/env python3
"""
Git synchronization monitoring script
Run this to check the health of git sync and manually trigger sync if needed
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_religion_architects.utils.git_monitor import GitSyncMonitor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Monitor and manage git synchronization')
    parser.add_argument('--check', action='store_true', help='Check git sync status')
    parser.add_argument('--sync', action='store_true', help='Force sync with remote')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix sync issues')
    parser.add_argument('--path', type=str, default=None, help='Repository path (default: current directory)')
    
    args = parser.parse_args()
    
    # Create monitor
    repo_path = args.path or os.getcwd()
    monitor = GitSyncMonitor(repo_path)
    
    if args.check or (not args.sync and not args.fix):
        # Check status
        print("\n🔍 Checking git synchronization status...\n")
        status = monitor.get_sync_health_status()
        
        print(f"📊 Repository: {repo_path}")
        print(f"🌿 Branch: {status['branch']}")
        print(f"📝 Status: {status['status_message']}")
        print(f"\nDetails:")
        print(f"  - Uncommitted changes: {'Yes' if status['uncommitted_changes'] else 'No'}")
        print(f"  - Commits ahead: {status['commits_ahead']}")
        print(f"  - Commits behind: {status['commits_behind']}")
        print(f"  - Health: {'✅ Healthy' if status['healthy'] else '⚠️ Needs attention'}")
        
        if not status['healthy']:
            print("\n💡 Recommendations:")
            if status['uncommitted_changes']:
                print("  - Commit or stash uncommitted changes")
            if status['commits_ahead'] > 0:
                print(f"  - Push {status['commits_ahead']} commit(s) to remote")
            if status['commits_behind'] > 0:
                print(f"  - Pull {status['commits_behind']} commit(s) from remote")
            print("\nRun with --sync to attempt automatic synchronization")
    
    if args.sync or args.fix:
        print("\n🔄 Attempting to synchronize repository...\n")
        
        # Create a sync commit message
        commit_message = f"Manual sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🔧 Synchronized by monitor script"
        
        # Files to add (same as auto-commit)
        files_to_add = ['public/data/', 'logs/']
        
        # Perform sync
        success = monitor.sync_repository(files_to_add, commit_message)
        
        if success:
            print("\n✅ Repository successfully synchronized!")
        else:
            print("\n❌ Synchronization failed. Manual intervention may be required.")
            print("\nTroubleshooting steps:")
            print("1. Check git status: git status")
            print("2. Check remote: git remote -v")
            print("3. Check conflicts: git diff")
            print("4. If needed, manually resolve conflicts and push")
    
    # Final status check
    if args.sync or args.fix:
        print("\n📊 Final status:")
        final_status = monitor.get_sync_health_status()
        print(f"  {final_status['status_message']}")


if __name__ == "__main__":
    main()