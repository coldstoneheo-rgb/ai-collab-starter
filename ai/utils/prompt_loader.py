# ai/utils/prompt_loader.py
"""
Prompt loading and formatting utilities.
Loads prompt templates from .github/AI_PROMPTS/ and injects PR context.
"""
import os
from pathlib import Path
from typing import Dict, Any

from ai.utils.models import PRInfo


def load_prompt_template(name: str, version: str = "v1") -> str:
    """
    Load prompt template from .github/AI_PROMPTS/.

    Args:
        name: Prompt name (e.g., "claude_pm_review", "gemini_uiux")
        version: Version suffix (default: "v1")

    Returns:
        Prompt template content

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    filename = f"{name}_{version}.txt"
    path = Path(".github/AI_PROMPTS") / filename

    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def build_pr_context(pr_info: PRInfo, include_diffs: bool = False, max_files: int = 50) -> str:
    """
    Build PR context string from PRInfo.

    Args:
        pr_info: PR information
        include_diffs: Whether to include file diffs (can be large)
        max_files: Maximum number of files to include

    Returns:
        Formatted PR context
    """
    context_parts = []

    # Basic info
    context_parts.append(f"# PR #{pr_info.number}: {pr_info.title}")
    context_parts.append(f"**Author:** {pr_info.author}")
    context_parts.append(f"**Branch:** {pr_info.head_branch} → {pr_info.base_branch}")
    context_parts.append(f"**Changes:** +{pr_info.additions} -{pr_info.deletions}")
    context_parts.append(f"**Files changed:** {pr_info.changed_files}")
    context_parts.append(f"**URL:** {pr_info.html_url}")
    context_parts.append("")

    # Description
    if pr_info.description:
        context_parts.append("## Description")
        context_parts.append(pr_info.description)
        context_parts.append("")

    # Changed files
    context_parts.append("## Changed Files")
    files_to_show = pr_info.files[:max_files]
    for file in files_to_show:
        status_icon = {
            'added': '✨',
            'modified': '✏️',
            'removed': '🗑️',
            'renamed': '📝'
        }.get(file.status, '❓')

        context_parts.append(f"{status_icon} `{file.filename}` (+{file.additions} -{file.deletions})")

        # Include diff if requested and available
        if include_diffs and file.patch and not file.is_binary:
            context_parts.append("```diff")
            # Limit diff size (max 50 lines per file)
            diff_lines = file.patch.split('\n')[:50]
            context_parts.append('\n'.join(diff_lines))
            if len(file.patch.split('\n')) > 50:
                context_parts.append("... (diff truncated)")
            context_parts.append("```")
            context_parts.append("")

    if pr_info.changed_files > max_files:
        context_parts.append(f"... and {pr_info.changed_files - max_files} more files")
    context_parts.append("")

    # Existing comments (if any)
    if pr_info.comments:
        context_parts.append("## Existing Comments")
        for comment in pr_info.comments[:10]:  # Show first 10 comments
            comment_type = "📄 Review" if comment.is_review_comment else "💬 General"
            context_parts.append(f"**{comment_type}** by {comment.author}:")
            context_parts.append(comment.body[:200])  # Truncate long comments
            if len(comment.body) > 200:
                context_parts.append("... (truncated)")
            context_parts.append("")

    return "\n".join(context_parts)


def build_claude_review_prompt(pr_info: PRInfo) -> str:
    """
    Build complete prompt for Claude PM review.

    Args:
        pr_info: PR information

    Returns:
        Complete prompt ready to send to Claude
    """
    # Load template
    template = load_prompt_template("claude_pm_review")

    # Build PR context
    pr_context = build_pr_context(pr_info, include_diffs=True, max_files=30)

    # Combine template + context
    # Template should have {pr_context} placeholder
    if "{pr_context}" in template:
        return template.replace("{pr_context}", pr_context)
    else:
        # If no placeholder, just append context
        return f"{template}\n\n{pr_context}"


def build_gemini_uiux_prompt(pr_info: PRInfo) -> str:
    """
    Build complete prompt for Gemini UI/UX review.

    Args:
        pr_info: PR information

    Returns:
        Complete prompt ready to send to Gemini
    """
    template = load_prompt_template("gemini_uiux")

    # Focus on UI-related files
    ui_extensions = ('.tsx', '.jsx', '.vue', '.html', '.css', '.scss')
    ui_files = [f for f in pr_info.files if f.filename.endswith(ui_extensions)]

    pr_context = build_pr_context(pr_info, include_diffs=True, max_files=20)

    # Add UI-specific context
    if ui_files:
        ui_context = f"\n## UI Files ({len(ui_files)} files)\n"
        for file in ui_files:
            ui_context += f"- `{file.filename}`\n"
        pr_context = pr_context + ui_context

    if "{pr_context}" in template:
        return template.replace("{pr_context}", pr_context)
    else:
        return f"{template}\n\n{pr_context}"


def build_perplexity_compliance_prompt(pr_info: PRInfo) -> str:
    """
    Build complete prompt for Perplexity compliance review.

    Args:
        pr_info: PR information

    Returns:
        Complete prompt ready to send to Perplexity
    """
    template = load_prompt_template("perplexity_compliance")

    # Check if sensitive paths are involved
    has_sensitive = pr_info.has_sensitive_changes()

    pr_context = build_pr_context(pr_info, include_diffs=False, max_files=50)

    if has_sensitive:
        pr_context = "⚠️ **SENSITIVE CHANGES DETECTED**\n\n" + pr_context

    if "{pr_context}" in template:
        return template.replace("{pr_context}", pr_context)
    else:
        return f"{template}\n\n{pr_context}"


def build_gpt_backend_prompt(pr_info: PRInfo) -> str:
    """
    Build complete prompt for GPT backend review.

    Args:
        pr_info: PR information

    Returns:
        Complete prompt ready to send to GPT
    """
    template = load_prompt_template("gpt_backend")

    # Focus on backend files
    backend_extensions = ('.py', '.go', '.java', '.rs', '.ts', '.js')
    backend_files = [f for f in pr_info.files if f.filename.endswith(backend_extensions)]

    pr_context = build_pr_context(pr_info, include_diffs=True, max_files=30)

    # Add backend-specific context
    if backend_files:
        backend_context = f"\n## Backend Files ({len(backend_files)} files)\n"
        for file in backend_files:
            backend_context += f"- `{file.filename}`\n"
        pr_context = pr_context + backend_context

    if "{pr_context}" in template:
        return template.replace("{pr_context}", pr_context)
    else:
        return f"{template}\n\n{pr_context}"
