#!/usr/bin/env python3
"""
Convert relative image URLs in write_up_filler.md to point to the public GitHub repo.
"""

import argparse
import re

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/rgreenblatt/multi_hop/master"

def convert_image_urls(content: str) -> str:
    """
    Convert relative image URLs to GitHub raw URLs.

    Matches markdown image syntax: ![alt](path)
    Only converts relative paths (not starting with http:// or https://)
    """
    def replace_url(match):
        alt_text = match.group(1)
        url = match.group(2).strip()

        # Skip if already an absolute URL
        if url.startswith(('http://', 'https://')):
            return match.group(0)

        # Convert relative path to GitHub raw URL
        new_url = f"{GITHUB_RAW_BASE}/{url}"
        return f"![{alt_text}]({new_url})"

    # Pattern matches ![alt text](url) - alt text can be empty
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_url, content)


def main():
    parser = argparse.ArgumentParser(
        description="Convert relative image URLs to GitHub raw URLs"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="write_up.md",
        help="Input markdown file (default: write_up.md)"
    )
    parser.add_argument(
        "--inplace", "-i",
        action="store_true",
        help="Modify the file in place instead of printing to stdout"
    )
    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        content = f.read()

    converted = convert_image_urls(content)

    if args.inplace:
        with open(args.input_file, 'w') as f:
            f.write(converted)
        print(f"Updated {args.input_file} in place")
    else:
        print(converted)


if __name__ == "__main__":
    main()
