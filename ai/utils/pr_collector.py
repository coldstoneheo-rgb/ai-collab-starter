# ai/utils/pr_collector.py
"""
PR Collector: Collects PR information from GitHub API.
Gathers PR metadata, file changes, diffs, and comments.
"""
import os
import sys
from typing import Optional, List
from datetime import datetime

try:
    from github import Github, GithubException
    from github.PullRequest import PullRequest
    from github.Repository import Repository
except ImportError:
    print("⚠️ PyGithub not installed. Install with: pip install PyGithub")
    sys.exit(1)

from ai.utils.models import PRInfo, FileChange, Comment


class PRCollector:
    """Collects PR information from GitHub."""

    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize PR Collector.

        Args:
            token: GitHub personal access token (default: GITHUB_TOKEN env var)
            repo_name: Repository name in format 'owner/repo' (default: auto-detect from git remote)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token not provided. Set GITHUB_TOKEN env var or pass token parameter.")

        self.github = Github(self.token)
        self.repo_name = repo_name or self._detect_repo_name()
        self.repo: Repository = self.github.get_repo(self.repo_name)

    def _detect_repo_name(self) -> str:
        """Auto-detect repository name from git remote."""
        import subprocess
        try:
            result = subprocess.check_output(
                ['git', 'remote', 'get-url', 'origin'],
                text=True,
                timeout=5
            ).strip()

            # Parse various GitHub URL formats
            if 'github.com' in result:
                # https://github.com/owner/repo.git
                # git@github.com:owner/repo.git
                parts = result.split('github.com')[-1]
                parts = parts.strip('/:').replace('.git', '')
                return parts
            else:
                raise ValueError(f"Could not parse GitHub repo from remote URL: {result}")
        except Exception as e:
            raise ValueError(f"Could not auto-detect repository. Please provide repo_name parameter. Error: {e}")

    def get_pr_info(self, pr_number: int) -> PRInfo:
        """
        Collect complete PR information.

        Args:
            pr_number: Pull request number

        Returns:
            PRInfo object with all PR data
        """
        try:
            pr: PullRequest = self.repo.get_pull(pr_number)
        except GithubException as e:
            raise ValueError(f"Failed to fetch PR #{pr_number}: {e}")

        # Basic info
        pr_info = PRInfo(
            number=pr.number,
            title=pr.title,
            description=pr.body or "",
            author=pr.user.login,
            state=pr.state,
            created_at=pr.created_at,
            updated_at=pr.updated_at,
            base_branch=pr.base.ref,
            head_branch=pr.head.ref,
            base_sha=pr.base.sha,
            head_sha=pr.head.sha,
            additions=pr.additions,
            deletions=pr.deletions,
            changed_files=pr.changed_files,
            commits=pr.commits,
            html_url=pr.html_url,
            diff_url=pr.diff_url,
            labels=[label.name for label in pr.labels],
        )

        # Collect file changes
        pr_info.files = self.get_changed_files(pr)

        # Collect comments
        pr_info.comments = self.get_comments(pr)

        return pr_info

    def get_changed_files(self, pr: PullRequest) -> List[FileChange]:
        """
        Get list of changed files with diffs.

        Args:
            pr: PullRequest object from PyGithub

        Returns:
            List of FileChange objects
        """
        files = []
        for file in pr.get_files():
            file_change = FileChange(
                filename=file.filename,
                status=file.status,
                additions=file.additions,
                deletions=file.deletions,
                changes=file.changes,
                patch=file.patch,  # May be None for binary files
                previous_filename=file.previous_filename if hasattr(file, 'previous_filename') else None,
            )
            files.append(file_change)
        return files

    def get_comments(self, pr: PullRequest) -> List[Comment]:
        """
        Get all comments on the PR (both general and review comments).

        Args:
            pr: PullRequest object from PyGithub

        Returns:
            List of Comment objects
        """
        comments = []

        # General PR comments (issue comments)
        try:
            for comment in pr.get_issue_comments():
                comments.append(Comment(
                    id=comment.id,
                    author=comment.user.login,
                    body=comment.body,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                ))
        except GithubException as e:
            print(f"⚠️ Failed to fetch issue comments: {e}")

        # File review comments (inline comments)
        try:
            for comment in pr.get_review_comments():
                comments.append(Comment(
                    id=comment.id,
                    author=comment.user.login,
                    body=comment.body,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    path=comment.path,
                    position=comment.position if hasattr(comment, 'position') else None,
                    commit_id=comment.commit_id,
                ))
        except GithubException as e:
            print(f"⚠️ Failed to fetch review comments: {e}")

        return comments

    def get_pr_diff(self, pr_number: int) -> str:
        """
        Get the raw diff for a PR.

        Args:
            pr_number: Pull request number

        Returns:
            Raw diff string
        """
        pr = self.repo.get_pull(pr_number)
        return pr.diff_url

    def post_comment(self, pr_number: int, body: str) -> int:
        """
        Post a comment on the PR.

        Args:
            pr_number: Pull request number
            body: Comment body (markdown supported)

        Returns:
            Comment ID
        """
        pr = self.repo.get_pull(pr_number)
        comment = pr.create_issue_comment(body)
        return comment.id

    def post_review(self, pr_number: int, body: str, event: str = "COMMENT") -> int:
        """
        Post a review on the PR.

        Args:
            pr_number: Pull request number
            body: Review body
            event: Review event type ('APPROVE', 'REQUEST_CHANGES', 'COMMENT')

        Returns:
            Review ID
        """
        pr = self.repo.get_pull(pr_number)
        review = pr.create_review(body=body, event=event)
        return review.id


def main():
    """Test PR Collector with a sample PR."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ai.utils.pr_collector <pr_number>")
        print("Example: python -m ai.utils.pr_collector 6")
        sys.exit(1)

    pr_number = int(sys.argv[1])

    print(f"🔍 Fetching PR #{pr_number}...")

    try:
        collector = PRCollector()
        pr_info = collector.get_pr_info(pr_number)

        print(f"\n✅ PR #{pr_info.number}: {pr_info.title}")
        print(f"   Author: {pr_info.author}")
        print(f"   State: {pr_info.state}")
        print(f"   Branch: {pr_info.head_branch} → {pr_info.base_branch}")
        print(f"   Changes: +{pr_info.additions} -{pr_info.deletions}")
        print(f"   Files: {pr_info.changed_files}")
        print(f"   Commits: {pr_info.commits}")
        print(f"   Labels: {', '.join(pr_info.labels) if pr_info.labels else 'None'}")
        print(f"   URL: {pr_info.html_url}")

        print(f"\n📁 Changed Files ({len(pr_info.files)}):")
        for file in pr_info.files[:10]:  # Show first 10 files
            status_icon = {
                'added': '✨',
                'modified': '✏️',
                'removed': '🗑️',
                'renamed': '📝'
            }.get(file.status, '❓')
            print(f"   {status_icon} {file.filename} (+{file.additions} -{file.deletions})")

        if len(pr_info.files) > 10:
            print(f"   ... and {len(pr_info.files) - 10} more files")

        print(f"\n💬 Comments ({len(pr_info.comments)}):")
        for comment in pr_info.comments[:5]:  # Show first 5 comments
            comment_type = "📄 Review" if comment.is_review_comment else "💭 General"
            print(f"   {comment_type} by {comment.author}: {comment.body[:60]}...")

        if len(pr_info.comments) > 5:
            print(f"   ... and {len(pr_info.comments) - 5} more comments")

        print(f"\n🔒 Sensitive Changes: {'Yes ⚠️' if pr_info.has_sensitive_changes() else 'No ✅'}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
