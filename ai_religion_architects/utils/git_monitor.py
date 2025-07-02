"""Git synchronization monitoring and management utilities"""

import subprocess
import logging
import time
from typing import Tuple, Optional
import os

logger = logging.getLogger(__name__)


class GitSyncMonitor:
    """Monitor and ensure git commits are successfully pushed to remote"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
        self.max_retries = 3
        self.retry_delay = 30  # seconds
        
    def check_git_status(self) -> Tuple[bool, str, int, int]:
        """
        Check git repository status
        Returns: (has_uncommitted, branch_name, commits_ahead, commits_behind)
        """
        try:
            # Check for uncommitted changes
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            has_uncommitted = bool(status_result.stdout.strip())
            
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            branch_name = branch_result.stdout.strip()
            
            # Check commits ahead/behind
            rev_list_result = subprocess.run(
                ['git', 'rev-list', '--left-right', '--count', f'origin/{branch_name}...{branch_name}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            commits_behind = 0
            commits_ahead = 0
            if rev_list_result.returncode == 0 and rev_list_result.stdout:
                parts = rev_list_result.stdout.strip().split()
                if len(parts) == 2:
                    commits_behind = int(parts[0])
                    commits_ahead = int(parts[1])
            
            return has_uncommitted, branch_name, commits_ahead, commits_behind
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git status check failed: {e}")
            return False, "unknown", 0, 0
    
    def ensure_git_configured(self):
        """Ensure git user is configured"""
        try:
            # Check if user.email is configured
            email_result = subprocess.run(
                ['git', 'config', 'user.email'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if not email_result.stdout.strip():
                # Configure git user
                subprocess.run(
                    ['git', 'config', 'user.email', 'meltedmindz1@gmail.com'],
                    cwd=self.repo_path,
                    check=True
                )
                subprocess.run(
                    ['git', 'config', 'user.name', 'MeltedMindz'],
                    cwd=self.repo_path,
                    check=True
                )
                logger.info("✅ Git user configured")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to configure git: {e}")
    
    def commit_changes(self, files_to_add: list, commit_message: str) -> bool:
        """
        Commit changes with specified files
        Returns: True if successful, False otherwise
        """
        try:
            # Add files
            for file_pattern in files_to_add:
                subprocess.run(
                    ['git', 'add', file_pattern],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False  # Don't fail if file doesn't exist
                )
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully committed changes")
                return True
            elif "nothing to commit" in result.stdout:
                logger.debug("No changes to commit")
                return True
            else:
                logger.error(f"Commit failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            return False
    
    def push_with_retry(self) -> bool:
        """
        Push to remote with retry logic
        Returns: True if successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                # First, pull with rebase to handle any conflicts
                pull_result = subprocess.run(
                    ['git', 'pull', '--rebase'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if pull_result.returncode != 0 and "CONFLICT" in pull_result.stdout:
                    logger.error("⚠️ Git pull resulted in conflicts. Manual intervention required.")
                    return False
                
                # Now push
                push_result = subprocess.run(
                    ['git', 'push'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if push_result.returncode == 0:
                    logger.info("📤 Successfully pushed to remote repository")
                    return True
                else:
                    logger.warning(f"Push attempt {attempt + 1} failed: {push_result.stderr}")
                    
                    if attempt < self.max_retries - 1:
                        logger.info(f"⏳ Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Git push failed: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"❌ Failed to push after {self.max_retries} attempts")
        return False
    
    def sync_repository(self, files_to_add: list, commit_message: str) -> bool:
        """
        Complete sync workflow: commit and push with monitoring
        Returns: True if successful, False otherwise
        """
        # Ensure git is configured
        self.ensure_git_configured()
        
        # Check initial status
        has_uncommitted, branch, ahead, behind = self.check_git_status()
        
        if behind > 0:
            logger.warning(f"⚠️ Local branch is {behind} commits behind remote. Pulling first...")
            pull_result = subprocess.run(
                ['git', 'pull', '--rebase'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if pull_result.returncode != 0:
                logger.error(f"Failed to pull: {pull_result.stderr}")
                return False
        
        # Commit if needed
        if files_to_add:
            if not self.commit_changes(files_to_add, commit_message):
                return False
        
        # Check if we have commits to push
        _, _, ahead, _ = self.check_git_status()
        
        if ahead > 0:
            logger.info(f"📊 {ahead} commit(s) ahead of remote. Pushing...")
            return self.push_with_retry()
        else:
            logger.debug("✅ Repository is up to date with remote")
            return True
    
    def get_sync_health_status(self) -> dict:
        """Get detailed sync health status for monitoring"""
        has_uncommitted, branch, ahead, behind = self.check_git_status()
        
        health_status = {
            "healthy": ahead == 0 and behind == 0 and not has_uncommitted,
            "branch": branch,
            "uncommitted_changes": has_uncommitted,
            "commits_ahead": ahead,
            "commits_behind": behind,
            "needs_push": ahead > 0,
            "needs_pull": behind > 0,
            "status_message": self._get_status_message(has_uncommitted, ahead, behind)
        }
        
        return health_status
    
    def _get_status_message(self, has_uncommitted: bool, ahead: int, behind: int) -> str:
        """Generate human-readable status message"""
        if ahead == 0 and behind == 0 and not has_uncommitted:
            return "✅ Repository is fully synchronized"
        
        messages = []
        if has_uncommitted:
            messages.append("uncommitted changes")
        if ahead > 0:
            messages.append(f"{ahead} unpushed commit(s)")
        if behind > 0:
            messages.append(f"{behind} commit(s) behind remote")
        
        return f"⚠️ Repository has: {', '.join(messages)}"


def monitor_git_health(repo_path: Optional[str] = None) -> dict:
    """Quick function to check git repository health"""
    monitor = GitSyncMonitor(repo_path)
    return monitor.get_sync_health_status()