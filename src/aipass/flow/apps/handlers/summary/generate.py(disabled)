#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: generate.py - Plan Summary Generation Handler
# Date: 2025-11-21
# Version: 1.2.0
# Category: flow/handlers/summary
#
# CHANGELOG:
#   - v1.2.0 (2026-02-14): Fix content extraction to handle all template types (master, proposal, default)
#   - v1.1.0 (2026-02-14): Sequential processing with backoff - delay between API calls, stop on rate limit
#   - v1.0.0 (2025-11-21): Extracted from archive_temp/flow_plan_summarizer.py
#
# CODE STANDARDS:
#   - 3-tier compliant: NO Prax imports, NO logging
#   - Raises exceptions for errors (module logs them)
# =============================================
"""
Plan Summary Generation Handler

Pure handler for generating AI-powered summaries of PLAN files.
Extracts content from PLAN files, generates summaries via OpenRouter API,
and manages summary cache.

This handler does NOT write CLAUDE.json or CLAUDE.local.md files.
Output generation is handled by the dashboard/update_local handler.
"""

from pathlib import Path
import sys
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

AIPASS_ROOT = Path.home() / 'aipass_core'
sys.path.insert(0, str(AIPASS_ROOT))

# Import API provider for summarization (via module entry point - encapsulation)
try:
    from api.apps.modules.openrouter_client import get_response
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# =============================================
# CONSTANTS
# =============================================

FLOW_ROOT = AIPASS_ROOT / "flow"
FLOW_JSON_DIR = FLOW_ROOT / "flow_json"
REGISTRY_FILE = FLOW_JSON_DIR / "flow_registry.json"
SUMMARIES_FILE = FLOW_JSON_DIR / "plan_summaries.json"
API_DELAY_SECONDS = 3  # Delay between sequential API calls to avoid rate limits
CONFIG_FILE = FLOW_JSON_DIR / "flow_plan_summarizer_config.json"
SHARED_API_CONFIG = FLOW_ROOT / "apps" / "handlers" / "json_templates" / "custom" / "api_config.json"

# Template detection markers (matches flow_plan.py auto-delete logic)
# Covers default, master, and proposal template placeholders
TEMPLATE_INDICATORS = [
    # Default template markers
    "[What do you want to achieve? Be specific about the end state.]",
    "[Break down into 3-5 concrete goals. What must be accomplished?]",
    "[How will you tackle this? Research first? Agents for broad analysis? Direct work?]",
    "[Document each significant action with outcome]",
    "[Working notes, discoveries, important context]",
    "[What defines complete for this specific PLAN?]",
    # Master plan template markers
    "[What is the end state when ALL phases complete?]",
    "[List planning docs, specs, existing code to reference]",
    "[What defines DONE for the entire project?]",
    "[What this phase accomplishes]",
    "[What the agent will build]",
    "[Patterns discovered that span multiple phases]",
    "[Significant blockers and how resolved]",
    "[What specifically defines the project complete?]",
    # Proposal template markers
    "[Clear description of the idea, feature, improvement, or fix]",
    "[Why is this valuable? What problem does it solve? What does it enable?]",
    "[Any other branches, services, or approvals needed?]",
    "[How would I tackle this? High-level steps.]",
    "[What exists now? What's the starting point?]",
    "[Anything you need clarity on before proceeding?]",
]

# =============================================
# CONFIGURATION
# =============================================

def load_config() -> Dict[str, Any]:
    """
    Load summarizer configuration from JSON file.

    If config file doesn't exist, creates it with default values.
    This allows config changes by editing JSON, not Python code.

    Returns:
        Config dict with structure:
        {
            "module_name": str,
            "version": str,
            "config": {
                "enabled": bool,
                "api_settings": {...},
                "cache_settings": {...},
                "summary_settings": {...}
            }
        }
    """
    # Default configuration (model removed - loaded from shared config)
    default_config = {
        "module_name": "flow_plan_summarizer",
        "version": "1.0.0",
        "config": {
            "enabled": True,
            "api_settings": {
                "timeout_seconds": 120,
                "max_tokens": 500
            },
            "cache_settings": {
                "enabled": True,
                "max_cache_entries": 50
            },
            "summary_settings": {
                "hide_empty_plans": True
            }
        }
    }

    # If config doesn't exist, create it with defaults
    if not CONFIG_FILE.exists():
        try:
            FLOW_JSON_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
        except Exception as e:
            raise Exception(f"Failed to create config file: {e}")

    # Load existing config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load config: {e}")

def load_shared_api_config() -> Optional[str]:
    """
    Load model from shared API config.

    Reads from: json_templates/custom/api_config.json
    Location priority:
        1. config.model (standard location)
        2. config.default_model (alternate location)
        3. api_settings.model (legacy fallback)

    Returns:
        Model name from shared config, or None if config doesn't exist
    """
    try:
        if not SHARED_API_CONFIG.exists():
            return None

        with open(SHARED_API_CONFIG, 'r', encoding='utf-8') as f:
            shared_config = json.load(f)

            # Try config.model first (standard location)
            model = shared_config.get("config", {}).get("model")

            # Try config.default_model as alternate
            if not model:
                model = shared_config.get("config", {}).get("default_model")

            # Fall back to api_settings.model if needed
            if not model:
                model = shared_config.get("api_settings", {}).get("model")

            return model
    except Exception:
        return None

# =============================================
# REGISTRY & CACHE ACCESS
# =============================================

def load_registry() -> Dict[str, Any]:
    """Load the flow registry"""
    if not REGISTRY_FILE.exists():
        return {"plans": {}}

    try:
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load registry: {e}")

def load_summaries() -> Dict[str, Any]:
    """Load existing summaries cache and clean up failed entries"""
    if not SUMMARIES_FILE.exists():
        return {}

    try:
        with open(SUMMARIES_FILE, 'r', encoding='utf-8') as f:
            summaries = json.load(f)

        # Self-healing: Remove failed summaries so they get retried
        cleaned_summaries = {}
        for plan_num, summary_data in summaries.items():
            summary_text = summary_data.get("summary", "")
            # Skip failed summaries (they'll be regenerated)
            if "Summary generation failed" not in summary_text and "Unable to generate summary" not in summary_text:
                cleaned_summaries[plan_num] = summary_data

        return cleaned_summaries

    except Exception as e:
        raise Exception(f"Failed to load summaries cache: {e}")

def save_summaries(summaries: Dict[str, Any]) -> None:
    """Save summaries cache"""
    try:
        FLOW_JSON_DIR.mkdir(parents=True, exist_ok=True)
        with open(SUMMARIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Failed to save summaries cache: {e}")

# =============================================
# CONTENT EXTRACTION
# =============================================

def extract_content_from_plan(plan_path: Path) -> str:
    """
    Extract meaningful content from a PLAN file (any template type).

    Works with all template types (default, master, proposal) by extracting
    content after the metadata header and filtering out template boilerplate.
    Instead of looking for specific section names, it identifies user-written
    content by excluding known template text.

    Args:
        plan_path: Path to PLAN file

    Returns:
        First 500 chars of meaningful content or "Empty plan template"
    """
    try:
        content = plan_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Skip metadata header (everything before first --- separator)
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip() == '---':
                content_start = i + 1
                break

        # Sections that are pure template boilerplate (instructions, not user content)
        # These appear in templates but never contain user-written content
        boilerplate_sections = {
            "## What Are Flow Plans?",
            "## When to Use This vs Master Plan",
            "## Master Plan vs Default Plan",
            "## Branch Directory Structure",
            "## Critical: Branch Manager Role",
            "## Seek Branch Expertise",
            "## Notepad",
            "## Command Reference",
            "## Agent Preparation (Before Deploying)",
            "## Agent Instructions Template",
            "## Execution Philosophy",
            "## What is a Master Plan?",
            "## Close Command",
            "## Ready for Green Light",
        }

        # Sections that contain user-editable content (these get extracted)
        # Covers default, master, and proposal templates
        content_sections = {
            # Default template
            "## Planning Phase", "## Execution Log", "## Notes",
            "## Completion Checklist",
            # Master plan template
            "## Project Overview", "## Phase Definitions", "## Phase Tracking",
            "## Issues Log", "## Master Plan Notes", "## Final Completion Checklist",
            # Proposal template
            "## What I Want to Work On", "## Why This Matters", "## What I'd Need",
            "## My Approach", "## Current State", "## Questions for DEV_CENTRAL",
            # Legacy section names (backward compatibility)
            "## Work Log", "## Objectives",
        }

        # Extract content from user-editable sections
        in_content_section = False
        meaningful_lines = []

        for line in lines[content_start:]:
            stripped = line.strip()

            # Detect section headers
            if stripped.startswith("## "):
                if stripped in boilerplate_sections:
                    in_content_section = False
                    continue
                elif stripped in content_sections:
                    in_content_section = True
                    continue
                else:
                    # Unknown section - assume it's user content (safer than ignoring)
                    in_content_section = True
                    continue

            # Skip --- separators
            if stripped == '---':
                in_content_section = False
                continue

            # Only collect from content sections
            if not in_content_section:
                continue

            # Skip empty lines, sub-headers, and template placeholders
            if not stripped:
                continue
            if stripped.startswith("### ") and stripped.endswith(": [Name]"):
                continue

            # Skip template placeholder lines (text inside square brackets)
            if stripped.startswith("[") and stripped.endswith("]"):
                continue

            # Skip template indicator lines
            is_indicator = False
            for indicator in TEMPLATE_INDICATORS:
                if indicator in line:
                    is_indicator = True
                    break
            if is_indicator:
                continue

            # Skip unchecked checkbox-only lines from templates (e.g. "- [ ] Agent deployed")
            # but keep checked ones (e.g. "- [x] Agent deployed") as they indicate real work
            if stripped.startswith("- [ ]"):
                continue

            # Skip boilerplate meta lines
            if stripped.startswith("**Status:**") and ("Pending" in stripped):
                continue
            if stripped.startswith("**Notes:**") and stripped.endswith("[Outcomes, issues, adjustments]"):
                continue

            # Skip table header/separator rows
            if stripped.startswith("|") and all(c in "|- " for c in stripped):
                continue

            # This line has real content
            meaningful_lines.append(stripped)

        # If no meaningful content found, it's a template
        if not meaningful_lines:
            return "Empty plan template"

        # Return first 500 chars of meaningful content
        result = " ".join(meaningful_lines)[:500]
        return result if result else "Empty plan template"

    except Exception as e:
        raise Exception(f"Error reading plan file: {e}")

def is_template_file(plan_path: Path) -> bool:
    """
    Check if PLAN file is empty template using marker detection.

    Uses same logic as flow_plan.py auto-delete (4+ markers = empty).

    Args:
        plan_path: Path to PLAN file

    Returns:
        True if file is empty template (4+ markers present)
    """
    try:
        content = plan_path.read_text(encoding='utf-8')
        markers_found = sum(1 for indicator in TEMPLATE_INDICATORS if indicator in content)
        return markers_found >= 4
    except Exception:
        return False

# =============================================
# AI SUMMARY GENERATION
# =============================================

def generate_ai_summary(content: str, plan_num: str) -> str:
    """
    Generate ~20 word AI summary of plan content.

    Args:
        content: Extracted plan content
        plan_num: Plan number (e.g., "0001")

    Returns:
        15-20 word summary or error message

    Error formats:
        - "API NOT AVAILABLE - no API modules found"
        - "API CONNECTION ERROR - no internet or invalid key"
        - "API RESPONSE ERROR - invalid response format"
        - "INVALID KEY - wrong prefix or too short"
    """
    # Check if it's an empty template
    if "Empty plan template" in content:
        return "Inactive - empty template, no work started"

    if not API_AVAILABLE:
        return f"FPLAN-{plan_num} - API NOT AVAILABLE: Cannot generate summary without AI"

    try:
        # Load model from shared config (json_templates/custom/api_config.json)
        model = load_shared_api_config()

        if model is None:
            # Shared config missing - raise error (no silent fallbacks)
            raise Exception(f"Shared API config not found at: {SHARED_API_CONFIG}")

        # Load summary settings from config
        config = load_config()
        summary_settings = config.get("config", {}).get("summary_settings", {})
        content_max = summary_settings.get("content_max_chars", 10000)
        word_min = summary_settings.get("word_limit_min", 30)
        word_max = summary_settings.get("word_limit_max", 40)
        word_truncate = summary_settings.get("word_truncate_at", 50)

        # Use API to generate summary
        prompt = f"""Generate a concise {word_min}-{word_max} word summary of this PLAN content.
Focus on the main objective, key goals, and any notable outcomes or conclusions.
If the plan is empty or just template text, respond with "Empty plan, no work started yet"

Content:
{content[:content_max]}

Summary ({word_min}-{word_max} words):"""

        response = get_response(prompt, model=model, caller="flow_plan_summarizer")

        if response:
            summary = response['content'].strip()  # Extract content from dict first
            # Ensure reasonable length
            if len(summary.split()) > word_truncate:
                summary = " ".join(summary.split()[:word_max]) + "..."
            return summary
        else:
            # No response - API failed
            return f"FPLAN-{plan_num} - API CONNECTION ERROR: Check API key and internet"

    except Exception as e:
        # Distinguish between different error types
        error_msg = str(e)

        # Check for specific error patterns
        if "API CONNECTION ERROR" in error_msg:
            return f"FPLAN-{plan_num} - API CONNECTION ERROR: No internet or invalid key"
        elif "API RESPONSE ERROR" in error_msg:
            return f"FPLAN-{plan_num} - API RESPONSE ERROR: Invalid response format"
        elif "missing required prefix" in error_msg.lower():
            return f"FPLAN-{plan_num} - INVALID KEY: Wrong API key prefix"
        elif "key too short" in error_msg.lower():
            return f"FPLAN-{plan_num} - INVALID KEY: API key too short"
        else:
            # Generic error
            return f"FPLAN-{plan_num} - ERROR: {error_msg[:50]}"

# =============================================
# CACHE MANAGEMENT
# =============================================

def needs_summary_update(plan_info: Dict, cached_summary: Optional[Dict]) -> bool:
    """
    Check if a plan needs its summary regenerated.

    Args:
        plan_info: Plan metadata from registry
        cached_summary: Cached summary data (or None)

    Returns:
        True if summary needs regeneration

    Checks:
        - File modified since last summary
        - Registry metadata changed
        - Plan status changed
    """
    if not cached_summary:
        return True

    # Check if plan file was modified since last summary
    plan_path = Path(plan_info.get("file_path", ""))
    if plan_path.exists():
        file_modified = datetime.fromtimestamp(plan_path.stat().st_mtime, timezone.utc).isoformat()
        summary_generated = cached_summary.get("generated_at", "")

        if file_modified > summary_generated:
            return True

    # Check if registry info was modified since last summary
    plan_modified = plan_info.get("closed") or plan_info.get("created")
    summary_generated = cached_summary.get("generated_at", "")

    if plan_modified and plan_modified > summary_generated:
        return True

    # Check if status changed
    if plan_info.get("status") != cached_summary.get("status"):
        return True

    return False

# =============================================
# MAIN ENTRY POINT
# =============================================

def generate_summaries() -> Dict[str, Any]:
    """
    Main entry point: Generate summaries for all plans.

    Returns:
        Status dict with format:
        {
            'success': True,
            'data': {
                plan_num: {
                    'summary': str,
                    'status': str,
                    'location': str,
                    'subject': str,
                    'file_path': str,
                    'generated_at': str (ISO 8601),
                    'is_empty': bool
                }
            }
        }

        OR on error:
        {
            'success': False,
            'error': 'Error message'
        }
    """
    try:
        registry = load_registry()
        cached_summaries = load_summaries()
        updated_summaries = {}

        api_call_count = 0
        rate_limited = False
        for plan_num, plan_info in registry.get("plans", {}).items():
            try:
                # Check if summary needs update
                cached = cached_summaries.get(plan_num)
                if not needs_summary_update(plan_info, cached):
                    # Use cached summary but ensure file_path is current from registry
                    if cached is None:
                        # Defensive: if cache unexpectedly missing, initialize minimal record
                        cached = {
                            "summary": "",
                            "status": plan_info.get("status", "unknown"),
                            "location": plan_info.get("relative_path", "unknown"),
                            "subject": plan_info.get("subject", ""),
                            "file_path": plan_info.get("file_path", ""),
                            "generated_at": datetime.now(timezone.utc).isoformat(),
                            "is_empty": False
                        }
                    else:
                        cached['file_path'] = plan_info.get("file_path", "")
                    updated_summaries[plan_num] = cached
                    continue

                # Stop processing if we hit a rate limit - try again later
                if rate_limited:
                    continue

                # Read plan file
                plan_path = Path(plan_info["file_path"])
                if not plan_path.exists():
                    # File missing - likely moved to backup after memory bank processing
                    # Remove from summaries cache so it doesn't show in CLAUDE outputs
                    if plan_num in cached_summaries:
                        del cached_summaries[plan_num]
                    continue

                # Check if this is an empty template BEFORE calling AI (save API calls)
                if is_template_file(plan_path):
                    # Skip AI call for empty templates - use fixed summary
                    summary = "Empty plan template - no content added"
                else:
                    # Add delay between API calls (not before the first one)
                    if api_call_count > 0:
                        time.sleep(API_DELAY_SECONDS)

                    # Extract content
                    content = extract_content_from_plan(plan_path)

                    # Generate summary with AI
                    summary = generate_ai_summary(content, plan_num)
                    api_call_count += 1

                # Check if summary generation failed
                if any(error in summary for error in ["ERROR:", "CONNECTION ERROR", "RESPONSE ERROR", "INVALID KEY", "API NOT AVAILABLE"]):
                    # Detect rate limit - stop processing remaining plans
                    if "429" in summary or "rate limit" in summary.lower():
                        rate_limited = True
                    # Don't cache failed summaries - let them retry next time
                    continue

                # Store successful summary with metadata
                updated_summaries[plan_num] = {
                    "summary": summary,
                    "status": plan_info.get("status", "unknown"),
                    "location": plan_info.get("relative_path", "unknown"),
                    "subject": plan_info.get("subject", ""),
                    "file_path": plan_info.get("file_path", ""),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "is_empty": "Empty plan" in summary or "Inactive" in summary
                }

            except Exception as e:
                # Detect rate limit in exceptions - stop processing
                error_str = str(e)
                if "429" in error_str or "rate limit" in error_str.lower():
                    rate_limited = True
                # Skip individual plan failures, continue with others
                continue

        # Save updated summaries
        save_summaries(updated_summaries)

        return {
            'success': True,
            'data': updated_summaries
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
