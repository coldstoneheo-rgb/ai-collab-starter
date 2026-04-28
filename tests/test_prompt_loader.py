# tests/test_prompt_loader.py
"""
Unit tests for Prompt Loader utilities.
"""
import pytest
from datetime import datetime
from pathlib import Path

from ai.utils.prompt_loader import (
    load_prompt_template,
    build_pr_context,
    build_claude_review_prompt,
)
from ai.utils.models import PRInfo, FileChange, Comment


class TestPromptLoader:
    """Test suite for prompt loading utilities."""

    def test_load_prompt_template(self):
        """Test loading prompt template."""
        # This will only work if the file exists
        # For now, we'll test the file not found case
        with pytest.raises(FileNotFoundError):
            load_prompt_template("nonexistent_prompt")

    def test_build_pr_context_basic(self):
        """Test building basic PR context."""
        pr_info = PRInfo(
            number=123,
            title="Add new feature",
            description="This PR adds a new feature",
            author="testuser",
            state="open",
            created_at=datetime(2026, 1, 15),
            updated_at=datetime(2026, 1, 16),
            base_branch="main",
            head_branch="feature-branch",
            base_sha="abc123",
            head_sha="def456",
            additions=100,
            deletions=50,
            changed_files=3,
            html_url="https://github.com/owner/repo/pull/123",
        )

        pr_info.files = [
            FileChange(
                filename="src/feature.py",
                status="added",
                additions=50,
                deletions=0,
                changes=50,
            ),
            FileChange(
                filename="src/main.py",
                status="modified",
                additions=30,
                deletions=20,
                changes=50,
            ),
        ]

        context = build_pr_context(pr_info, include_diffs=False)

        # Check key elements are present
        assert "PR #123: Add new feature" in context
        assert "testuser" in context
        assert "feature-branch → main" in context
        assert "+100 -50" in context
        assert "src/feature.py" in context
        assert "src/main.py" in context
        assert "✨" in context  # added file icon
        assert "✏️" in context  # modified file icon

    def test_build_pr_context_with_diffs(self):
        """Test building PR context with diffs."""
        pr_info = PRInfo(
            number=456,
            title="Fix bug",
            description="Fixes critical bug",
            author="bugfixer",
            state="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="bugfix",
            base_sha="aaa",
            head_sha="bbb",
            additions=10,
            deletions=5,
            changed_files=1,
            html_url="https://github.com/owner/repo/pull/456",
        )

        pr_info.files = [
            FileChange(
                filename="src/buggy.py",
                status="modified",
                additions=10,
                deletions=5,
                changes=15,
                patch="@@ -1,1 +1,1 @@\n-old line\n+new line",
            )
        ]

        context = build_pr_context(pr_info, include_diffs=True)

        assert "```diff" in context
        assert "-old line" in context
        assert "+new line" in context

    def test_build_pr_context_with_comments(self):
        """Test building PR context with comments."""
        pr_info = PRInfo(
            number=789,
            title="Update docs",
            description="",
            author="docwriter",
            state="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="docs",
            base_sha="xxx",
            head_sha="yyy",
            additions=5,
            deletions=0,
            changed_files=1,
            html_url="https://github.com/owner/repo/pull/789",
        )

        pr_info.comments = [
            Comment(
                id=1,
                author="reviewer1",
                body="Looks good!",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Comment(
                id=2,
                author="reviewer2",
                body="Please fix typo in line 5",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                path="README.md",
                position=5,
            )
        ]

        context = build_pr_context(pr_info, include_diffs=False)

        assert "Existing Comments" in context
        assert "reviewer1" in context
        assert "Looks good!" in context
        assert "📄 Review" in context  # review comment icon

    def test_build_pr_context_max_files(self):
        """Test limiting number of files in context."""
        pr_info = PRInfo(
            number=100,
            title="Many files",
            description="",
            author="author",
            state="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="feature",
            base_sha="a",
            head_sha="b",
            additions=100,
            deletions=0,
            changed_files=100,
            html_url="https://github.com/owner/repo/pull/100",
        )

        # Create 100 files
        pr_info.files = [
            FileChange(
                filename=f"file{i}.py",
                status="added",
                additions=1,
                deletions=0,
                changes=1,
            )
            for i in range(100)
        ]

        context = build_pr_context(pr_info, include_diffs=False, max_files=10)

        # Should only show first 10 files
        assert "file0.py" in context
        assert "file9.py" in context
        assert "file10.py" not in context
        assert "... and 90 more files" in context

    def test_build_pr_context_sensitive_paths(self):
        """Test that sensitive paths don't affect context building."""
        pr_info = PRInfo(
            number=999,
            title="Update infra",
            description="",
            author="devops",
            state="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="infra-update",
            base_sha="x",
            head_sha="y",
            additions=20,
            deletions=10,
            changed_files=2,
            html_url="https://github.com/owner/repo/pull/999",
        )

        pr_info.files = [
            FileChange(
                filename="infra/deployment.yml",
                status="modified",
                additions=10,
                deletions=5,
                changes=15,
            ),
            FileChange(
                filename=".github/workflows/ci.yml",
                status="modified",
                additions=10,
                deletions=5,
                changes=15,
            )
        ]

        # Should still build context normally
        context = build_pr_context(pr_info, include_diffs=False)
        assert "infra/deployment.yml" in context
        assert ".github/workflows/ci.yml" in context

        # Check if PR detects sensitive changes
        assert pr_info.has_sensitive_changes() is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
