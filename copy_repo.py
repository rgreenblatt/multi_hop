#!/usr/bin/env python3
"""Copy repo files to a specified directory, excluding gitignored and json/jsonl files."""

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def get_repo_files():
    """Get all files tracked by git + untracked but not ignored."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.strip().split("\n"))


def get_all_png_files():
    """Get all PNG files including ignored ones."""
    return set(str(p) for p in Path(".").rglob("*.png"))


def should_include(filepath: str) -> bool:
    """Check if file should be included."""
    path = Path(filepath)

    # Exclude venv directory
    if filepath.startswith("venv/") or "/venv/" in filepath:
        return False

    if path.name == "compositional_questions.json":
        return False

    return True


def copy_repo(dest_dir: str):
    """Copy repo files to destination directory."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    # Get git-tracked files + all PNGs (even ignored)
    files = get_repo_files() | get_all_png_files()
    copied = 0

    for filepath in sorted(files):
        if not filepath:
            continue

        src = Path(filepath)
        if not src.is_file():
            continue

        if not should_include(filepath):
            print(f"Skipped: {filepath}")
            continue

        dst = dest / filepath
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Special handling for .gitignore
        if src.suffix.lower() == ".md":
            content = src.read_text()
            new_content = re.sub(
                r'https://docs\.google\.com/document/d/[a-zA-Z0-9_-]+(/[^\s)]*)?',
                "FIXURL",
                content
            )
            if new_content != content:
                dst.write_text(new_content)
                shutil.copystat(src, dst)
                print(f"Copied (with URL replacement): {filepath}")
            else:
                shutil.copy2(src, dst)
                print(f"Copied: {filepath}")
        elif filepath == ".gitignore":
            with open(src, "r") as f:
                content = f.read()

            # Add compositional question files if not already present
            files_to_add = [
                "/data/",
            ]

            for file in files_to_add:
                if file not in content:
                    if not content.endswith("\n"):
                        content += "\n"
                    content += f"{file}\n"

            with open(dst, "w") as f:
                f.write(content)
            print(f"Copied (with modifications): {filepath}")
        else:
            shutil.copy2(src, dst)
            print(f"Copied: {filepath}")

        copied += 1

    print(f"\nDone! {copied} files copied to: {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy repo files excluding gitignored and json/jsonl files"
    )
    parser.add_argument("destination", help="Destination directory")
    args = parser.parse_args()

    copy_repo(args.destination)
