import os

collect_ignore_glob = [
    os.path.join("*", "apps", "handlers", "*", "test_*.py"),
    os.path.join("*", "apps", "handlers", "*", "*", "test_*.py"),
]
