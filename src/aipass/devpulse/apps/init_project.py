"""
aipass init — Bootstrap an AIPass project in any directory.

Temporary home in devpulse. Will port to CLI branch once proven.

Usage:
    python -m aipass.devpulse.apps.init_project [target_dir]

What it does:
    1. Generates a UUID for the project registry
    2. Creates *_REGISTRY.json with metadata.id
    3. Creates .trinity/ (passport with registry_id)
    4. Creates .aipass/ (aipass_local_prompt.md)
    5. Creates AIPASS.md (project prompt)
"""

import json
import re
import sys
import uuid
from datetime import date
from pathlib import Path


def _sanitize_name(raw: str) -> str:
    """Sanitize a project name for use in filenames.

    Replaces non-alphanumeric characters (except underscore/hyphen) with
    underscores and strips leading/trailing underscores.
    """
    return re.sub(r"[^A-Z0-9_-]", "_", raw.upper()).strip("_")


def init_project(target: Path, project_name: str | None = None) -> dict:
    """Initialize an AIPass project in the target directory.

    Args:
        target: Directory to initialize
        project_name: Name for the registry (defaults to directory name)

    Returns:
        dict with created files and registry_id
    """
    target = target.resolve()
    if not target.exists():
        target.mkdir(parents=True)

    raw_name = project_name or target.name
    name = _sanitize_name(raw_name)
    if not name:
        raise ValueError(
            f"Cannot derive project name from '{raw_name}'. "
            "Pass a project name explicitly."
        )
    registry_id = str(uuid.uuid4())
    today = date.today().isoformat()
    created = []

    # 1. Registry
    registry_filename = f"{name}_REGISTRY.json"
    registry_path = target / registry_filename
    if registry_path.exists():
        raise FileExistsError(f"Registry already exists: {registry_path}")

    registry_data = {
        "metadata": {
            "id": registry_id,
            "name": name,
            "version": "1.0.0",
            "created": today,
            "last_updated": today,
            "total_branches": 0,
        },
        "branches": [],
    }
    registry_path.write_text(
        json.dumps(registry_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    created.append(str(registry_path))

    # 2. .trinity/
    trinity_dir = target / ".trinity"
    trinity_dir.mkdir(exist_ok=True)

    passport = {
        "document_metadata": {
            "document_type": "project_identity",
            "document_name": f"{name}.PASSPORT",
            "version": "1.0.0",
            "created": today,
            "last_updated": today,
        },
        "identity": {
            "project_name": name,
            "role": "project_root",
            "purpose": "",
        },
        "citizenship": {
            "registered": True,
            "registry_id": registry_id,
            "registry_name": name,
        },
    }
    passport_path = trinity_dir / "passport.json"
    if passport_path.exists():
        raise FileExistsError(
            f"Passport already exists: {passport_path}. "
            "Remove .trinity/passport.json to re-initialize."
        )
    passport_path.write_text(
        json.dumps(passport, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    created.append(str(passport_path))

    # local.json + observations.json
    for filename in ("local.json", "observations.json"):
        p = trinity_dir / filename
        if not p.exists():
            p.write_text("{}\n", encoding="utf-8")
            created.append(str(p))

    # 3. .aipass/
    aipass_dir = target / ".aipass"
    aipass_dir.mkdir(exist_ok=True)

    prompt_path = aipass_dir / "aipass_local_prompt.md"
    if not prompt_path.exists():
        prompt_path.write_text(
            f"# {name} — Local Prompt\n\nInjected every turn. Add project-specific context here.\n",
            encoding="utf-8",
        )
        created.append(str(prompt_path))

    # 4. AIPASS.md
    aipass_md = target / "AIPASS.md"
    if not aipass_md.exists():
        aipass_md.write_text(
            "# AIPass — Project Prompt\n\n"
            "Project-level instructions. Persists in context for the entire conversation.\n\n"
            "## Startup\n\n"
            "On any greeting, silently read these files from CWD and run the commands "
            "— no narration, no announcing steps. Just do it and respond with the status.\n\n"
            "**Read:** `.trinity/passport.json`, `.trinity/local.json`, "
            "`.trinity/observations.json`, `README.md`\n"
            "**Run:** `git status`\n\n"
            "## Memories\n\n"
            "Update `.trinity/` at natural breakpoints, after milestones, and on `/memo`. "
            "If compaction hits before you save, it's gone.\n",
            encoding="utf-8",
        )
        created.append(str(aipass_md))

    return {
        "registry_id": registry_id,
        "registry_file": registry_filename,
        "project_name": name,
        "target": str(target),
        "created_files": created,
    }


def main():
    """CLI entry point."""
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    name = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = init_project(target, name)
    except (FileExistsError, ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Initialized AIPass project: {result['project_name']}")
    print(f"Registry: {result['registry_file']} (id: {result['registry_id'][:8]}...)")
    print(f"Created {len(result['created_files'])} files:")
    for f in result["created_files"]:
        print(f"  {f}")


if __name__ == "__main__":
    main()
