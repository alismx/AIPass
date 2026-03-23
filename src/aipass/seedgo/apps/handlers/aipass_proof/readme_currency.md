# README Currency Proof — Documentation Accuracy
**Version:** 1.0.0
**Created:** 2026-03-22
**Modified:** 2026-03-22
**Status:** Placeholder

---

## Purpose

The README currency proof verifies that a pack's `README.md` accurately reflects the actual state of the pack. README files are the first thing branches and humans read to understand pack coverage. Stale READMEs erode trust and cause confusion.

---

## What Gets Checked

### 1. Checker Count Accuracy

The README typically states how many standards the pack contains (e.g., "24 active standards"). This proof compares that stated count against the actual number of `*_check.py` files in the pack.

```
README says:  "24 active standards"
Actual count: glob("*_check.py") -> 26 files
Result:       FAIL — count mismatch (off by 2)
```

### 2. Undocumented Standards

Every `*_check.py` in the pack should have a corresponding mention in the README. A standard that exists in the pack but is never mentioned in the README is "undocumented."

```
Pack contains:  stderr_routing_check.py
README mentions: (no reference to stderr_routing)
Result:          FAIL — undocumented standard
```

### 3. Stale References

The README should not reference standards that no longer exist in the pack. If a standard was archived or removed, its README entry must also be removed.

```
README mentions: diagnostics_check.py
Pack contains:   (no such file — moved to .archive/)
Result:          FAIL — stale reference
```

---

## How Detection Works

<!-- TODO: Document the exact detection algorithm once scanner is built -->

1. **Count extraction**: Parse the README for numeric patterns near keywords like "standards", "checkers", "active"
2. **Standard enumeration**: Glob `*_check.py` in the pack directory, extract standard names
3. **Cross-reference**: For each standard name, search the README text for a mention
4. **Stale detection**: For each standard name found in the README, verify the corresponding `*_check.py` exists

---

## What "Undocumented" Means

A standard is undocumented if:
- Its `*_check.py` file exists in the pack directory
- The README.md contains no reference to that standard's name
- It is not listed in any standards table or section of the README

This does not require a full section per standard — a mention in a list or table is sufficient. But total absence means the README is incomplete.

---

## Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Count mismatch | Standards added/removed without updating README count | Update the count |
| Undocumented standard | New checker added, README not updated | Add entry to README |
| Stale reference | Standard archived/removed, README not updated | Remove the entry |

---

## How to Fix

1. **Count**: Run `ls *_check.py | wc -l` in the pack directory, update the README count
2. **Undocumented**: Add a line or section for each missing standard
3. **Stale**: Remove or mark as archived any references to non-existent standards

---

## Related

- **DPLAN-0044**: Self-audit tooling design
- **tools/readme_currency_scanner.py**: Original prototype
- **Checker**: `readme_currency.py` in this directory
