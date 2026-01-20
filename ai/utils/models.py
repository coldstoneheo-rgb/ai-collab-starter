# ai/utils/models.py
"""
Data models for AI-Collab-Starter.
Defines common data structures used across the system.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class FileChange:
    """Represents a single file change in a PR."""
    filename: str
    status: str  # 'added', 'modified', 'removed', 'renamed'
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None  # The actual diff content
    previous_filename: Optional[str] = None  # For renamed files

    @property
    def is_binary(self) -> bool:
        """Check if this is a binary file (no patch available)."""
        return self.patch is None or self.patch == ""


@dataclass
class Comment:
    """Represents a comment on a PR."""
    id: int
    author: str
    body: str
    created_at: datetime
    updated_at: datetime
    path: Optional[str] = None  # File path for file comments
    position: Optional[int] = None  # Line position for inline comments
    commit_id: Optional[str] = None

    @property
    def is_review_comment(self) -> bool:
        """Check if this is a file review comment (not a general PR comment)."""
        return self.path is not None


@dataclass
class PRInfo:
    """Represents complete PR information."""
    number: int
    title: str
    description: str
    author: str
    state: str  # 'open', 'closed', 'merged'
    created_at: datetime
    updated_at: datetime
    base_branch: str
    head_branch: str
    base_sha: str
    head_sha: str

    # Collections
    files: List[FileChange] = field(default_factory=list)
    comments: List[Comment] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)

    # Statistics
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    commits: int = 0

    # URLs
    html_url: str = ""
    diff_url: str = ""

    def get_changed_paths(self) -> List[str]:
        """Get list of changed file paths."""
        return [f.filename for f in self.files]

    def get_file_by_path(self, path: str) -> Optional[FileChange]:
        """Get a specific file change by path."""
        for file in self.files:
            if file.filename == path:
                return file
        return None

    def has_sensitive_changes(self) -> bool:
        """Check if PR contains changes to sensitive paths."""
        sensitive_prefixes = (
            'migrations/', 'infra/', 'terraform/', 'k8s/',
            'security/', 'auth/', 'payments/', '.github/workflows/',
            'db/', '.env'
        )
        for path in self.get_changed_paths():
            if any(path.startswith(prefix) for prefix in sensitive_prefixes):
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'number': self.number,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'state': self.state,
            'base_branch': self.base_branch,
            'head_branch': self.head_branch,
            'changed_files': self.changed_files,
            'additions': self.additions,
            'deletions': self.deletions,
            'html_url': self.html_url,
            'files': [f.filename for f in self.files],
            'labels': self.labels,
        }


@dataclass
class AIResponse:
    """Represents an AI agent's response to a review request."""
    agent: str  # 'claude', 'gemini', 'perplexity', 'gpt'
    content: str
    model: str

    # Token usage
    input_tokens: int
    output_tokens: int
    total_tokens: int

    # Cost
    cost_usd: float

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'agent': self.agent,
            'model': self.model,
            'content': self.content,
            'tokens': {
                'input': self.input_tokens,
                'output': self.output_tokens,
                'total': self.total_tokens,
            },
            'cost_usd': self.cost_usd,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.metadata,
        }
