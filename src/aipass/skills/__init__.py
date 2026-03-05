"""aipass.skills — User-built add-ons that compose infrastructure.

Skills are self-contained folders that import from AIPass infrastructure
modules (drone, api, prax, mail, etc.) to create new capabilities.

Infrastructure = the plumbing (modules/handlers/plugins inside each module).
Skills = what users build ON TOP of the plumbing.

Each skill is a directory with a SKILL.md describing what it does
and Python files that import what they need from aipass.*.
"""
