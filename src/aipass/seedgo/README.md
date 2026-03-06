# Seedgo

Standards compliance platform for AIPass modules. Audits Python code against configurable standard packs, scores each file, and reports violations. Ships with the `aipass` pack (21 standards covering imports, architecture, naming, logging, documentation, and more).

## Usage

### CLI

```bash
seedgo --help                        # Show packs and usage
seedgo audit aipass                  # Audit all modules against aipass standards
seedgo checklist aipass <file>       # Check a single file
seedgo list                          # Show installed standard packs
seedgo verify                        # Self-check seedgo internals
```

### Python

```python
from aipass.seedgo.apps.seedgo import main, discover_packs

# List available standard packs
packs = discover_packs()
print(packs)  # {'aipass': PosixPath('...')}
```

## Architecture

```
seedgo/
├── apps/
│   ├── seedgo.py              # Entry point + pack router
│   ├── modules/
│   │   └── seedgo_verify.py   # Self-check module
│   └── standards/
│       └── aipass/             # Built-in standard pack (21 standards)
│           ├── pack.json       # Pack manifest
│           ├── pack_entry.py   # Pack entry point
│           ├── handlers/       # Standard check implementations
│           └── modules/        # Standard display + orchestrators
├── tests/
└── README.md
```

## Standard Packs

The `aipass` pack checks: architecture, CLI, CLI flags, diagnostics, documentation, encapsulation, error handling, handlers, imports, JSON structure, log handler, log level, log visibility, meta headers, modules, naming, permission flags, readme, shebang, testing, and trigger patterns.

Custom packs go in `apps/standards/` — each needs a `pack.json` manifest and `pack_entry.py` entry point. See `apps/standards/app_development.example/` for a template.

## Dependencies

- `aipass.cli` — Rich-based display formatting
- `aipass.prax` — structured logging
