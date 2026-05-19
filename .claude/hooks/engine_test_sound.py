# =================== AIPass ====================
# Name: engine_test_sound.py
# Description: Test sound hook for engine POC — plays distinct beep
# Version: 0.2.0
# Created: 2026-05-17
# Modified: 2026-05-18
# =============================================

"""Plays a distinct A5 beep to prove the engine dispatched this hook."""

import subprocess
import sys
from pathlib import Path

SOUNDS_DIR = Path(__file__).parent.parent / "sounds"
DEFAULT_SOUND = SOUNDS_DIR / "engine_test_beep.wav"


def main() -> None:
    """Play the test beep sound. Accepts optional sound file arg."""
    sound = DEFAULT_SOUND
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        if candidate.exists():
            sound = candidate

    if not sound.exists():
        return
    try:
        subprocess.run(
            ["aplay", "-q", str(sound)],
            timeout=5, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


if __name__ == "__main__":
    main()
