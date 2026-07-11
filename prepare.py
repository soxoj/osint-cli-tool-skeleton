#!/usr/bin/env python3
"""
Rename the skeleton to your own project name.

Replaces the package name everywhere it appears — package directory, intra-package
imports, docs and packaging metadata — so the renamed project keeps working as a
CLI, library, HTTP server and MCP server.

    $ python prepare.py                 # interactive
    $ python prepare.py my_new_tool     # non-interactive
"""
import os
import re
import shutil
import sys

OLD_NAME = "osint_cli_tool_skeleton"
# Extensions whose contents get the textual replacement.
TEXT_EXTS = {".py", ".md", ".toml", ".cfg", ".txt", ".yml", ".yaml", ".in"}
# Directories to skip while walking.
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "build", "dist", ".pytest_cache"}


def iter_text_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")]
        for name in filenames:
            if os.path.splitext(name)[1] in TEXT_EXTS:
                yield os.path.join(dirpath, name)


def main():
    if not os.path.isdir(OLD_NAME):
        print(f"Package directory '{OLD_NAME}' not found — run this from the repo root.")
        sys.exit(1)

    new_name = (sys.argv[1] if len(sys.argv) > 1 else input("Enter new project name: "))
    new_name = new_name.strip().replace("-", "_")

    if not new_name or not re.match(r"^[a-zA-Z_][0-9a-zA-Z_]*$", new_name):
        print("Invalid name — must be a valid Python identifier (no leading digit).")
        sys.exit(1)
    if new_name == OLD_NAME:
        print("New name is the same as the old one; nothing to do.")
        return

    # 1) Replace the name inside every text file (imports, docs, metadata).
    changed = 0
    for path in iter_text_files("."):
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        if OLD_NAME in content:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content.replace(OLD_NAME, new_name))
            changed += 1

    # 2) Rename the package directory itself.
    shutil.move(OLD_NAME, new_name)

    print(f"Renamed '{OLD_NAME}' -> '{new_name}' ({changed} files updated).")
    print("Next: `pip install -e .` then `python -m", new_name, "--list-plugins`.")


if __name__ == "__main__":
    main()
