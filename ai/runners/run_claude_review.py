#!/usr/bin/env python3
"""
Claude PM Review Runner.
Collects PR information, generates review prompt, calls Claude API, and posts comment.
"""
import os
import sys
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai.utils.pr_collector import PRCollector
from ai.utils.prompt_loader import build_claude_review_prompt
from ai.runners.clients.claude_client import ClaudeClient
from ai.runners.clients.base_client import AIClientError, APIKeyMissingError
from ai.utils.audit_logger import log_ai_event
from ai.utils.safety_policy import MANUAL_APPROVAL_REQUIRED_MSG


def update_cost_tracker(cost_usd: float):
    """
    Update cost tracking budget file.

    Args:
        cost_usd: Cost in USD to add
    """
    budget_file = Path('.ai/budget.json')

    if not budget_file.exists():
        print(f"⚠️ Budget file not found: {budget_file}")
        return

    try:
        with open(budget_file, 'r') as f:
            budget = json.load(f)

        # Update Claude cost
        budget['cost_tracking']['claude'] = budget.get('cost_tracking', {}).get('claude', 0) + cost_usd
        budget['monthly_spent_usd'] = budget.get('monthly_spent_usd', 0) + cost_usd

        with open(budget_file, 'w') as f:
            json.dump(budget, f, indent=2)

        print(f"💰 Cost updated: +${cost_usd:.6f}")
        print(f"   Total spent: ${budget['monthly_spent_usd']:.6f} / ${budget['monthly_budget_usd']}")

        # Check budget warning
        if budget['monthly_spent_usd'] > budget['monthly_budget_usd'] * 0.8:
            print(f"⚠️ WARNING: 80% of monthly budget used!")

    except Exception as e:
        print(f"⚠️ Failed to update cost tracker: {e}")


def main():
    """Main entry point for Claude review runner."""
    parser = argparse.ArgumentParser(description='Run Claude PM review on a PR')
    parser.add_argument(
        '--pr-number',
        type=int,
        required=True,
        help='Pull request number to review'
    )
    parser.add_argument(
        '--post-comment',
        action='store_true',
        default=True,
        help='Post review as PR comment (default: True)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without posting comment or updating costs'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=4000,
        help='Maximum tokens for Claude response (default: 4000)'
    )

    args = parser.parse_args()
    decision_reason = os.getenv("ROUTER_REASON", "runner_local_or_unknown")

    print(f"🤖 Claude PM Review - PR #{args.pr_number}")
    print("=" * 60)

    # Check for dry run
    if args.dry_run:
        print("🏃 DRY RUN MODE - No comments will be posted, no costs recorded")
        print()

    # Step 1: Collect PR information
    print("📥 Step 1: Collecting PR information...")
    try:
        collector = PRCollector()
        pr_info = collector.get_pr_info(args.pr_number)

        print(f"   ✅ PR #{pr_info.number}: {pr_info.title}")
        print(f"   📝 Author: {pr_info.author}")
        print(f"   🌿 Branch: {pr_info.head_branch} → {pr_info.base_branch}")
        print(f"   📊 Changes: +{pr_info.additions} -{pr_info.deletions} in {pr_info.changed_files} files")

        if pr_info.has_sensitive_changes():
            print(f"   ⚠️ SENSITIVE CHANGES DETECTED")

        print()

    except Exception as e:
        print(f"   ❌ Failed to collect PR information: {e}")
        log_ai_event(
            agent="claude",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="pr_collection_failed",
            error_message=str(e),
            tags=["runner", "claude", "failure"],
        )
        sys.exit(1)

    # Step 2: Build review prompt
    print("📝 Step 2: Building review prompt...")
    try:
        prompt = build_claude_review_prompt(pr_info)
        prompt_tokens = len(prompt) // 4  # Rough estimate
        print(f"   ✅ Prompt built (~{prompt_tokens} tokens)")
        print()

    except FileNotFoundError as e:
        print(f"   ❌ Prompt template not found: {e}")
        print(f"   💡 Make sure .github/AI_PROMPTS/claude_pm_review_v1.txt exists")
        log_ai_event(
            agent="claude",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="prompt_template_missing",
            error_message=str(e),
            tags=["runner", "claude", "failure"],
        )
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Failed to build prompt: {e}")
        log_ai_event(
            agent="claude",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="prompt_build_failed",
            error_message=str(e),
            tags=["runner", "claude", "failure"],
        )
        sys.exit(1)

    # Step 3: Send to Claude API
    print("🧠 Step 3: Sending to Claude API...")
    try:
        client = ClaudeClient()
        print(f"   📡 Using model: {client.model}")
        print(f"   ⏳ Waiting for response...")

        response = client.send_prompt(prompt, max_tokens=args.max_tokens)

        print(f"   ✅ Response received")
        print(f"   📊 Tokens: {response.input_tokens} in + {response.output_tokens} out = {response.total_tokens} total")
        print(f"   💰 Cost: ${response.cost_usd:.6f}")
        print()

    except APIKeyMissingError:
        print(f"   ❌ CLAUDE_API_KEY not found in environment")
        print(f"   💡 Set CLAUDE_API_KEY environment variable")
        log_ai_event(
            agent="claude",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="api_key_missing",
            error_message="CLAUDE_API_KEY not found",
            tags=["runner", "claude", "failure"],
        )
        sys.exit(1)
    except AIClientError as e:
        print(f"   ❌ Claude API error: {e}")
        log_ai_event(
            agent="claude",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="api_client_error",
            error_message=str(e),
            tags=["runner", "claude", "failure"],
        )
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        log_ai_event(
            agent="claude",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="unexpected_error",
            error_message=str(e),
            tags=["runner", "claude", "failure"],
        )
        sys.exit(1)

    # Step 4: Post comment to PR
    if args.post_comment and not args.dry_run:
        print("💬 Step 4: Posting review comment...")
        comment_posted = False
        try:
            # Format review comment
            manual_notice = ""
            if pr_info.has_sensitive_changes():
                manual_notice = (
                    f"> ⚠️ **{MANUAL_APPROVAL_REQUIRED_MSG}**\n\n"
                )
            review_comment = f"""## 🤖 Claude PM Review

{manual_notice}{response.content}

---
<sub>Review by Claude ({client.model}) | Tokens: {response.total_tokens} | Cost: ${response.cost_usd:.6f}</sub>
"""

            comment_id = collector.post_comment(args.pr_number, review_comment)
            print(f"   ✅ Comment posted (ID: {comment_id})")
            print()
            comment_posted = True

        except Exception as e:
            print(f"   ❌ Failed to post comment: {e}")
            # Don't exit - we still want to update costs
            print()
    elif args.dry_run:
        print("💬 Step 4: Posting review comment...")
        print("   ⏭️ Skipped (dry run)")
        print()
    else:
        print("💬 Step 4: Posting review comment...")
        print("   ⏭️ Skipped (--no-post-comment)")
        print()

    # Step 5: Update cost tracker
    if not args.dry_run:
        print("💰 Step 5: Updating cost tracker...")
        update_cost_tracker(response.cost_usd)
        print()
    else:
        print("💰 Step 5: Updating cost tracker...")
        print("   ⏭️ Skipped (dry run)")
        print()

    # Summary
    print("=" * 60)
    print("✅ Claude PM Review Complete")
    print()
    print("📊 Summary:")
    print(f"   PR: #{pr_info.number} - {pr_info.title}")
    print(f"   Model: {client.model}")
    print(f"   Tokens: {response.total_tokens}")
    print(f"   Cost: ${response.cost_usd:.6f}")

    tags = ["runner", "claude", "success"]
    if pr_info.has_sensitive_changes():
        tags.append("sensitive_changes")
    if args.dry_run:
        tags.append("dry_run")
    log_ai_event(
        agent="claude",
        pr_number=args.pr_number,
        status="success",
        decision_reason=decision_reason,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        total_tokens=response.total_tokens,
        cost_usd=response.cost_usd if not args.dry_run else 0.0,
        tags=tags,
        metadata={
            "model": client.model,
            "prompt_tokens_estimate": prompt_tokens,
            "comment_posted": bool(args.dry_run or not args.post_comment) or locals().get("comment_posted", False),
            "sensitive_changes": pr_info.has_sensitive_changes(),
            "changed_files": pr_info.changed_files,
        },
    )

    if args.dry_run:
        print()
        print("🏃 This was a DRY RUN - no changes were made")

    # Output review content for debugging/logging
    print()
    print("📄 Review Content Preview:")
    print("-" * 60)
    preview = response.content[:500]
    print(preview)
    if len(response.content) > 500:
        print("... (truncated)")
    print("-" * 60)


if __name__ == '__main__':
    main()
