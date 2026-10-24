"""Create the demo issues from samples/issues.json in a GitHub repo.

Runs inside the "Seed demo issues" workflow (uses its GITHUB_TOKEN), or locally:
    GITHUB_TOKEN=... python seed_issues.py --repo owner/name
"""

import argparse
import json
import os
from pathlib import Path

from triage import GH_TOKEN, GitHub

ROOT = Path(__file__).parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--branch", default=os.environ.get("GITHUB_REF_NAME", "main"))
    args = ap.parse_args()
    if not (args.repo and GH_TOKEN):
        raise SystemExit("Need --repo (or GITHUB_REPOSITORY) and GITHUB_TOKEN.")

    image_base = f"https://raw.githubusercontent.com/{args.repo}/{args.branch}/samples"
    raw = (ROOT / "samples" / "issues.json").read_text(encoding="utf-8")
    issues = json.loads(raw.replace("{{IMAGE_BASE}}", image_base))

    gh = GitHub(args.repo)
    existing = {i["title"] for i in gh.open_issues()}
    for issue in issues:
        if issue["title"] in existing:
            print(f"skip (exists): {issue['title']}")
            continue
        created = gh.call("/issues", {"title": issue["title"], "body": issue["body"]})
        print(f"created #{created['number']}: {issue['title']}", flush=True)


if __name__ == "__main__":
    main()
