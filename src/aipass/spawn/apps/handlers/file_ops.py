"""Template copy and file rename operations."""

import shutil
from pathlib import Path

from aipass.spawn.apps.handlers.placeholders import replace_placeholders

# Patterns to skip during template copy
SKIP_NAMES = {"__pycache__", ".git", ".template_registry.json"}


def copy_template(template_dir, target_dir, replacements):
    """
    Recursively copy template to target, replacing placeholders in text files.

    Args:
        template_dir: Path to template directory
        target_dir: Path to target directory
        replacements: Placeholder mapping dict

    Returns:
        Tuple of (copied_files, skipped_files) lists
    """
    template_dir = Path(template_dir)
    target_dir = Path(target_dir)
    copied = []
    skipped = []

    for item in _walk(template_dir):
        rel_path = item.relative_to(template_dir)

        # Check exclusions
        if _should_skip(rel_path):
            skipped.append(str(rel_path))
            continue

        # Apply placeholder replacement to path components
        dest_rel = _replace_path_placeholders(rel_path, replacements)
        dest = target_dir / dest_rel

        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            copied.append(f"{dest_rel}/ (dir)")
        elif item.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                content = item.read_text(encoding="utf-8")
                content = replace_placeholders(content, replacements)
                dest.write_text(content, encoding="utf-8")
                copied.append(str(dest_rel))
            except (UnicodeDecodeError, UnicodeEncodeError):
                shutil.copy2(item, dest)
                copied.append(f"{dest_rel} (binary)")

    return copied, skipped


def rename_placeholder_paths(target_dir, branch_name):
    """
    Rename any remaining {{BRANCH}}_json style directories and files.

    Args:
        target_dir: Path to spawned branch
        branch_name: Raw branch folder name

    Returns:
        List of rename operation strings
    """
    target_dir = Path(target_dir)
    lower = branch_name.lower().replace("-", "_")
    renamed = []

    # Rename directories first (bottom-up to avoid path invalidation)
    dirs_to_rename = []
    for d in sorted(target_dir.rglob("*"), reverse=True):
        if d.is_dir() and "{{BRANCH}}" in d.name:
            dirs_to_rename.append(d)

    for d in dirs_to_rename:
        new_name = d.name.replace("{{BRANCH}}", lower)
        new_path = d.parent / new_name
        if not new_path.exists():
            d.rename(new_path)
            renamed.append(f"{d.name} -> {new_name}")

    # Rename files
    for f in target_dir.rglob("*"):
        if f.is_file() and "{{BRANCH}}" in f.name:
            new_name = f.name.replace("{{BRANCH}}", lower)
            new_path = f.parent / new_name
            if not new_path.exists():
                f.rename(new_path)
                renamed.append(f"{f.name} -> {new_name}")

    return renamed


def _walk(directory):
    """Walk directory tree including hidden files, yielding all items."""
    directory = Path(directory)
    for item in sorted(directory.iterdir()):
        yield item
        if item.is_dir() and item.name != ".git":
            yield from _walk(item)


def _should_skip(rel_path):
    """Check if a relative path should be skipped during copy."""
    parts = rel_path.parts
    for part in parts:
        if part in SKIP_NAMES:
            return True
    # Skip .gitkeep files (template needs them, branches don't)
    if rel_path.name == ".gitkeep":
        return True
    return False


def _replace_path_placeholders(rel_path, replacements):
    """Replace {{PLACEHOLDER}} patterns in path components."""
    parts = []
    for part in rel_path.parts:
        new_part = replace_placeholders(part, replacements)
        parts.append(new_part)
    return Path(*parts) if parts else rel_path
