# tests/test_pr_collector.py
"""
Unit tests for PR Collector.
Uses mocking to avoid actual GitHub API calls.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from ai.utils.pr_collector import PRCollector
from ai.utils.models import PRInfo, FileChange, Comment


class TestPRCollector:
    """Test suite for PRCollector class."""

    @patch('ai.utils.pr_collector.Github')
    def test_init_with_token(self, mock_github):
        """Test initialization with explicit token."""
        collector = PRCollector(token='test_token', repo_name='owner/repo')
        assert collector.token == 'test_token'
        assert collector.repo_name == 'owner/repo'
        mock_github.assert_called_once_with('test_token')

    @patch.dict('os.environ', {'GITHUB_TOKEN': 'env_token'})
    @patch('ai.utils.pr_collector.Github')
    def test_init_with_env_token(self, mock_github):
        """Test initialization with environment variable token."""
        collector = PRCollector(repo_name='owner/repo')
        assert collector.token == 'env_token'
        mock_github.assert_called_once_with('env_token')

    @patch('ai.utils.pr_collector.Github')
    def test_get_pr_info(self, mock_github):
        """Test fetching PR information."""
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()

        # Set up PR data
        mock_pr.number = 6
        mock_pr.title = "Test PR"
        mock_pr.body = "Test description"
        mock_pr.user.login = "testuser"
        mock_pr.state = "open"
        mock_pr.created_at = datetime(2026, 1, 15)
        mock_pr.updated_at = datetime(2026, 1, 16)
        mock_pr.base.ref = "main"
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.sha = "abc123"
        mock_pr.head.sha = "def456"
        mock_pr.additions = 100
        mock_pr.deletions = 50
        mock_pr.changed_files = 5
        mock_pr.commits = 3
        mock_pr.html_url = "https://github.com/owner/repo/pull/6"
        mock_pr.diff_url = "https://github.com/owner/repo/pull/6.diff"
        mock_pr.labels = []

        # Mock files
        mock_file = MagicMock()
        mock_file.filename = "test.py"
        mock_file.status = "modified"
        mock_file.additions = 10
        mock_file.deletions = 5
        mock_file.changes = 15
        mock_file.patch = "@@ -1,1 +1,1 @@\n-old\n+new"
        mock_pr.get_files.return_value = [mock_file]

        # Mock comments
        mock_pr.get_issue_comments.return_value = []
        mock_pr.get_review_comments.return_value = []

        mock_repo.get_pull.return_value = mock_pr
        mock_github.return_value.get_repo.return_value = mock_repo

        # Test
        collector = PRCollector(token='test_token', repo_name='owner/repo')
        pr_info = collector.get_pr_info(6)

        # Assertions
        assert pr_info.number == 6
        assert pr_info.title == "Test PR"
        assert pr_info.author == "testuser"
        assert pr_info.state == "open"
        assert pr_info.base_branch == "main"
        assert pr_info.head_branch == "feature-branch"
        assert pr_info.additions == 100
        assert pr_info.deletions == 50
        assert pr_info.changed_files == 5
        assert len(pr_info.files) == 1
        assert pr_info.files[0].filename == "test.py"

    def test_pr_info_has_sensitive_changes(self):
        """Test sensitive path detection."""
        pr_info = PRInfo(
            number=1,
            title="Test",
            description="",
            author="test",
            state="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="feature",
            base_sha="abc",
            head_sha="def",
        )

        # No sensitive files
        pr_info.files = [
            FileChange(filename="README.md", status="modified", additions=1, deletions=0, changes=1)
        ]
        assert pr_info.has_sensitive_changes() is False

        # Has sensitive file
        pr_info.files.append(
            FileChange(filename="infra/deployment.yml", status="modified", additions=1, deletions=0, changes=1)
        )
        assert pr_info.has_sensitive_changes() is True

    def test_file_change_is_binary(self):
        """Test binary file detection."""
        # Text file with patch
        text_file = FileChange(
            filename="test.py",
            status="modified",
            additions=1,
            deletions=0,
            changes=1,
            patch="@@ -1,1 +1,1 @@"
        )
        assert text_file.is_binary is False

        # Binary file without patch
        binary_file = FileChange(
            filename="image.png",
            status="added",
            additions=0,
            deletions=0,
            changes=0,
            patch=None
        )
        assert binary_file.is_binary is True

    def test_comment_is_review_comment(self):
        """Test review comment detection."""
        # General comment
        general_comment = Comment(
            id=1,
            author="test",
            body="Great work!",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert general_comment.is_review_comment is False

        # Review comment with file path
        review_comment = Comment(
            id=2,
            author="test",
            body="Fix this",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            path="test.py",
            position=10,
        )
        assert review_comment.is_review_comment is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
