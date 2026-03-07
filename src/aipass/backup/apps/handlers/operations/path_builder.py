
# ===================AIPASS====================
# META DATA HEADER
# Name: path_builder.py - Backup path construction
# Date: 2025-11-18
# Version: 1.0.0
# Category: handlers
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-18): Extracted from backup_core.py
#     * Extracted path construction logic for versioned mode
#     * Handles long filename hashing
#     * Mode-specific path building
#
# CODE STANDARDS:
#   - Follow seed 3-layer architecture
#   - Handlers must be independent and transportable
#   - No cross-handler imports except within same domain
# =============================================

"""
Path Builder - Backup destination path construction

Constructs destination paths based on backup mode and file structure.
"""

# =============================================
# IMPORTS
# =============================================

import hashlib
from pathlib import Path

# =============================================
# PATH CONSTRUCTION OPERATIONS
# =============================================

def build_backup_path(source_file: Path, source_dir: Path, backup_path: Path, mode: str) -> Path:
    """Construct backup destination path based on mode.

    Args:
        source_file: Source file path
        source_dir: Source directory root
        backup_path: Backup destination root
        mode: Backup mode ('snapshot' or 'versioned')

    Returns:
        Full backup file path
    """
    rel_path = source_file.relative_to(source_dir)

    if mode == 'versioned':
        # Versioned mode: file-based folders for version tracking
        # Check if filename is too long (>50 chars) and needs shortening
        if len(rel_path.name) > 50:
            # Use shortened hash-based folder name for long filenames
            name_hash = hashlib.md5(rel_path.name.encode()).hexdigest()[:8]
            short_name = rel_path.name[:30] + f"_{name_hash}"

            if str(rel_path.parent) == ".":
                file_folder = backup_path / "root" / short_name
            else:
                file_folder = backup_path / rel_path.parent / short_name
            return file_folder / rel_path.name
        else:
            # Normal path structure for shorter filenames
            if str(rel_path.parent) == ".":
                # Root-level file: AGENTS.md -> root/AGENTS.md/AGENTS.md
                file_folder = backup_path / "root" / rel_path.name
                return file_folder / rel_path.name
            else:
                # Subfolder file: backup.py -> backup_system/backup.py/backup.py
                file_folder = backup_path / rel_path.parent / rel_path.name
                return file_folder / rel_path.name
    else:
        # Snapshot and other modes: keep original flat structure
        return backup_path / rel_path


# =============================================
# MODULE INITIALIZATION
# =============================================

# Pure handler - no initialization needed
