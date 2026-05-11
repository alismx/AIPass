# Windows Compatibility
**Status:** Draft v1
**Date:** 2026-05-10

---

## What It Is

A standard that ensures Python code runs on both Linux and Windows by detecting
POSIX-only APIs used without platform guards.  Windows CI (GitHub Actions on
Windows Server 2022) validates compliance end-to-end.

---

## Why It Matters

AIPass is pip-installable and must work cross-platform.  POSIX-only patterns
like bare `import fcntl` or `os.waitpid(-1, os.WNOHANG)` crash immediately on
Windows with `ImportError` or `WinError 87`.  The Windows CI caught 71 failures
from these systemic patterns.  This standard prevents regressions.

---

## What the Checker Scans For

AST-parses every `.py` file and flags POSIX-only usage outside platform guards.

### Rule 1 — POSIX-only imports
`import fcntl`, `import pwd`, `import grp`, `import termios`, `import resource`
without `if sys.platform` or `try/except ImportError`.

### Rule 2 — POSIX-only constants
`os.WNOHANG`, `signal.SIGPIPE` without platform guard or `hasattr()` check.

### Rule 3 — POSIX-only calls
`os.fork()`, `os.setpgid()`, `os.killpg()`, `os.getpgid()`, `os.waitpid()`
without platform guard.

### Rule 4 — os.kill without exception handling
`os.kill(pid, signal)` without `try/except OSError`.  Windows raises
`OSError: [WinError 87] The parameter is incorrect` for invalid PIDs.

### Valid Guards (recognized by checker)
- `if sys.platform != "win32":` / `if sys.platform == "linux":`
- `if os.name != "nt":` / `if os.name == "posix":`
- `try: ... except ImportError:`
- `try: ... except OSError:`
- `if hasattr(signal, "SIGPIPE"):`

### Skips
- `__init__.py` files
- Non-`.py` files

---

## Code Examples

### Violation — bare POSIX import
```python
import fcntl
fcntl.flock(fd, fcntl.LOCK_EX)
```

### Fix 1 — platform guard with Windows fallback
```python
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

def lock_file(fd):
    if sys.platform == "win32":
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
    else:
        fcntl.flock(fd, fcntl.LOCK_EX)
```

### Fix 2 — try/except import
```python
try:
    import fcntl
except ImportError:
    fcntl = None
```

### Violation — unguarded os.WNOHANG
```python
pid, _ = os.waitpid(-1, os.WNOHANG)
```

### Fix — platform guard
```python
if sys.platform != "win32":
    pid, _ = os.waitpid(-1, os.WNOHANG)
```

### Violation — os.kill without exception handling
```python
os.kill(pid, 0)  # Crashes on Windows with WinError 87
```

### Fix — wrap in try/except
```python
try:
    os.kill(pid, 0)
except OSError:
    return False
```

---

## Scoring
- **Scope:** AUDIT_SCOPE = "all_files"
- **Checks per file:** 1 (Windows compat)
- **Score 100:** No unguarded POSIX-only patterns found
- **Score 0:** One or more unguarded patterns found
- **Failure message:** "N unguarded POSIX pattern(s): L42: import fcntl; ..."
- **Overall pass threshold:** 75%

---

## Bypass

File-level bypass (entire file is Linux-only):
```json
{"file": "apps/handlers/dispatch/daemon.py", "standard": "windows_compat",
 "reason": "Daemon process management is Linux-only by design"}
```

Line-level bypass (specific line has a valid reason):
```json
{"file": "apps/config.py", "standard": "windows_compat", "lines": [89],
 "reason": "fcntl used only in POSIX lock path, Windows path above"}
```

---

## Reference
- **Checker:** windows_compat_check.py
- **Scope:** all_files
- **Entry point:** check_module()
- **Standard label:** WINDOWS_COMPAT
- **Windows CI:** .github/workflows/windows-test.yml
- **Issue:** #326 (Input-X Windows platform report)
