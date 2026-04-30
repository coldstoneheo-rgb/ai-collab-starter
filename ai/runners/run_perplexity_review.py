#!/usr/bin/env python3
"""
Perplexity Compliance Review Runner.
Collects PR information, generates review prompt, calls Perplexity API, and posts comment.
"""
import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai.utils.pr_collector import PRCollector
from ai.utils.prompt_loader import build_perplexity_compliance_prompt
from ai.runners.clients.perplexity_client import PerplexityClient
from ai.runners.clients.base_client import AIClientError, APIKeyMissingError
from ai.utils.audit_logger import log_ai_event
from ai.utils.safety_policy import MANUAL_APPROVAL_REQUIRED_MSG
from ai.utils.cost_monitor import record_cost, BudgetExceededError


def main():
    """Main entry point for Perplexity review runner."""
    parser = argparse.ArgumentParser(description='Run Perplexity compliance review on a PR')
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
        help='Maximum tokens for Perplexity response (default: 4000)'
    )

    args = parser.parse_args()
    decision_reason = os.getenv("ROUTER_REASON", "runner_local_or_unknown")

    print(f"⚖️ Perplexity Compliance Review - PR #{args.pr_number}")
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
            agent="perplexity",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="pr_collection_failed",
            error_message=str(e),
            tags=["runner", "perplexity", "failure"],
        )
        sys.exit(1)

    # Step 2: Build review prompt
    print("📝 Step 2: Building review prompt...")
    try:
        prompt = build_perplexity_compliance_prompt(pr_info)
        prompt_tokens = len(prompt) // 4  # Rough estimate
        print(f"   ✅ Prompt built (~{prompt_tokens} tokens)")
        print()

    except FileNotFoundError as e:
        print(f"   ❌ Prompt template not found: {e}")
        print(f"   💡 Make sure .github/AI_PROMPTS/perplexity_compliance_v1.txt exists")
        log_ai_event(
            agent="perplexity",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="prompt_template_missing",
            error_message=str(e),
            tags=["runner", "perplexity", "failure"],
        )
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Failed to build prompt: {e}")
        log_ai_event(
            agent="perplexity",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="prompt_build_failed",
            error_message=str(e),
            tags=["runner", "perplexity", "failure"],
        )
        sys.exit(1)

    # Step 3: Check budget before API call
    if not args.dry_run:
        print("💰 Step 3: Checking budget...")
        try:
            from ai.utils.cost_monitor import get_budget_status
            budget_status = get_budget_status()
            if budget_status["is_over_budget"]:
                print(f"   ❌ Budget exhausted: ${budget_status['monthly_spent_usd']:.2f} / ${budget_status['monthly_budget_usd']:.2f}")
                log_ai_event(
                    agent="perplexity",
                    pr_number=args.pr_number,
                    status="failed",
                    decision_reason=decision_reason,
                    error_type="budget_exceeded",
                    error_message="Monthly budget exhausted",
                    tags=["runner", "perplexity", "failure", "budget"],
                )
                sys.exit(1)
            print(f"   ✅ Budget OK: ${budget_status['remaining_usd']:.2f} remaining ({budget_status['usage_pct']:.1f}% used)")
            print()
        except Exception as e:
            print(f"   ⚠️ Budget check failed: {e}")
            print()

    # Step 4: Send to Perplexity API
    print("🧠 Step 4: Sending to Perplexity API...")
    try:
        client = PerplexityClient()
        print(f"   📡 Using model: {client.model}")
        print(f"   ⏳ Waiting for response...")

        response = client.send_prompt(prompt, max_tokens=args.max_tokens)

        print(f"   ✅ Response received")
        print(f"   📊 Tokens: {response.input_tokens} in + {response.output_tokens} out = {response.total_tokens} total")
        print(f"   💰 Cost: ${response.cost_usd:.6f}")
        print()

    except APIKeyMissingError:
        print(f"   ❌ PERPLEXITY_API_KEY not found in environment")
        print(f"   💡 Set PERPLEXITY_API_KEY environment variable")
        log_ai_event(
            agent="perplexity",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="api_key_missing",
            error_message="PERPLEXITY_API_KEY not found",
            tags=["runner", "perplexity", "failure"],
        )
        sys.exit(1)
    except AIClientError as e:
        print(f"   ❌ Perplexity API error: {e}")
        log_ai_event(
            agent="perplexity",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="api_client_error",
            error_message=str(e),
            tags=["runner", "perplexity", "failure"],
        )
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        log_ai_event(
            agent="perplexity",
            pr_number=args.pr_number,
            status="failed",
            decision_reason=decision_reason,
            error_type="unexpected_error",
            error_message=str(e),
            tags=["runner", "perplexity", "failure"],
        )
        sys.exit(1)

    # Step 5: Post comment to PR
    if args.post_comment and not args.dry_run:
        print("💬 Step 5: Posting review comment...")
        comment_posted = False
        try:
            # Format review comment
            manual_notice = ""
            if pr_info.has_sensitive_changes():
                manual_notice = (
                    f"> ⚠️ **{MANUAL_APPROVAL_REQUIRED_MSG}**\n\n"
                )
            review_comment = f"""## ⚖️ Perplexity Compliance Review

{manual_notice}{response.content}

---
<sub>Review by Perplexity ({client.model}) | Tokens: {response.total_tokens} | Cost: ${response.cost_usd:.6f}</sub>
"""

            comment_id = collector.post_comment(args.pr_number, review_comment)
            print(f"   ✅ Comment posted (ID: {comment_id})")
            print()
            comment_posted = True

        except Exception as e:
            print(f"   ❌ Failed to post comment: {e}")
            print()
    elif args.dry_run:
        print("💬 Step 5: Posting review comment...")
        print("   ⏭️ Skipped (dry run)")
        print()
    else:
        print("💬 Step 5: Posting review comment...")
        print("   ⏭️ Skipped (--no-post-comment)")
        print()

    # Step 6: Update cost tracker
    if not args.dry_run:
        print("💰 Step 6: Updating cost tracker...")
        try:
            record_cost("perplexity", response.cost_usd)
            print(f"   ✅ Cost recorded: ${response.cost_usd:.6f}")
            print()
        except BudgetExceededError as e:
            print(f"   ⚠️ Budget exceeded after this call: {e}")
            print()
        except Exception as e:
            print(f"   ⚠️ Failed to update cost tracker: {e}")
            print()
    else:
        print("💰 Step 6: Updating cost tracker...")
        print("   ⏭️ Skipped (dry run)")
        print()

    # Summary
    print("=" * 60)
    print("✅ Perplexity Compliance Review Complete")
    print()
    print("📊 Summary:")
    print(f"   PR: #{pr_info.number} - {pr_info.title}")
    print(f"   Model: {client.model}")
    print(f"   Tokens: {response.total_tokens}")
    print(f"   Cost: ${response.cost_usd:.6f}")

    tags = ["runner", "perplexity", "success"]
    if pr_info.has_sensitive_changes():
        tags.append("sensitive_changes")
    if args.dry_run:
        tags.append("dry_run")
    log_ai_event(
        agent="perplexity",
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
