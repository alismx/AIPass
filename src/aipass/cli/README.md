# CLI

Display and output formatting service for AIPass modules. Provides consistent terminal output — headers, success/error/warning messages, section breaks, and operation templates — so every module looks the same without duplicating Rich formatting code.

## Usage

```python
from aipass.cli import header, success, error, warning, section

header("Creating Branch", {"Name": "feature", "Type": "module"})
success("Files created", items=12, time="2.3s")
error("Path not found", suggestion="Check spelling")
warning("Config missing, using defaults")
section("Results")
```

### Operation Templates

```python
from aipass.cli import operation_start, operation_complete

operation_start("Processing", count=10)
# ... do work ...
operation_complete(created=5, skipped=3, failed=0)
```

### Direct Console Access

```python
from aipass.cli import console

console.print("[bold cyan]Custom Rich output[/bold cyan]")
```

## Architecture

```
cli/
├── apps/
│   ├── cli.py                  # Entry point
│   ├── modules/
│   │   ├── display.py          # header, success, error, warning, section
│   │   └── templates.py        # operation_start, operation_complete
│   └── handlers/
│       └── json/               # JSON file management
└── tests/
```

- `apps/modules/` — Public API. Import from here.
- `apps/handlers/` — Internal implementation. Don't import directly.
