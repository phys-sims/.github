#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import tomllib  # Python 3.11+

ROOT = Path(__file__).resolve().parents[2]
OUT_REPORT = ROOT / "docs" / "HEALTH_REPORT.md"
CLOC_DIR = ROOT / ".health" / "cloc_json"
PROFILE_README = ROOT / "profile" / "README.md"

METRICS_START = "<!-- HEALTH:START -->"
METRICS_END = "<!-- HEALTH:END -->"

ORG = os.environ.get("ORG", "").strip()
REPOS_DIR = Path(os.environ.get("REPOS_DIR", "/tmp/org_repos")).resolve()

if not ORG:
    raise SystemExit("ORG env var is required (e.g. ORG=phys-sims).")

def sh(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def gh_api_json(path: str) -> dict:
    out = sh(["gh", "api", path])
    return json.loads(out) if out else {}

def gh_api_json_slurp(path: str) -> List[dict]:
    out = sh(["gh", "api", "--paginate", "--slurp", path])
    return json.loads(out) if out else []

def parse_iso(dt: str) -> datetime:
    # e.g. 2026-02-12T21:12:34Z
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))

def fmt_date(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")

@dataclass
class RepoRow:
    name: str
    full_name: str
    private: bool
    archived: bool
    default_branch: str
    pushed_at: datetime
    open_issues: int
    open_prs: int
    code: int
    comment: int
    blank: int
    top_langs: List[Tuple[str, int]]
    has_pyproject: bool
    project_name: Optional[str]
    has_tests: bool
    workflow_count: int
    has_precommit: bool

def load_cloc(repo_name: str) -> Tuple[int, int, int, List[Tuple[str, int]]]:
    fp = CLOC_DIR / f"{repo_name}.json"
    if not fp.exists():
        return (0, 0, 0, [])
    data = json.loads(fp.read_text(encoding="utf-8"))

    s = data.get("SUM", {})
    code = int(s.get("code", 0))
    comment = int(s.get("comment", 0))
    blank = int(s.get("blank", 0))

    langs: List[Tuple[str, int]] = []
    for k, v in data.items():
        if k in ("header", "SUM"):
            continue
        langs.append((k, int(v.get("code", 0))))
    langs.sort(key=lambda x: x[1], reverse=True)
    return (code, comment, blank, langs[:5])

def inspect_repo_files(repo_dir: Path) -> Tuple[bool, Optional[str], bool, int, bool]:
    """
    Returns:
      has_pyproject, project_name, has_tests, workflow_count, has_precommit
    """
    pyproject = repo_dir / "pyproject.toml"
    has_pyproject = pyproject.exists()
    project_name: Optional[str] = None

    if has_pyproject:
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            project = data.get("project", {})
            if isinstance(project, dict):
                name = project.get("name")
                if isinstance(name, str) and name.strip():
                    project_name = name.strip()
        except Exception:
            # Don't fail the whole report if a repo has a weird pyproject
            project_name = None

    has_tests = (repo_dir / "tests").is_dir()
    workflows_dir = repo_dir / ".github" / "workflows"
    workflow_count = 0
    if workflows_dir.is_dir():
        workflow_count = len([p for p in workflows_dir.glob("*.y*ml") if p.is_file()])

    has_precommit = (repo_dir / ".pre-commit-config.yaml").exists()
    return has_pyproject, project_name, has_tests, workflow_count, has_precommit

def count_open_prs(owner: str, repo: str) -> int:
    q = f"repo:{owner}/{repo} is:pr is:open"
    res = gh_api_json(f"search/issues?q={q}")
    return int(res.get("total_count", 0))

def count_open_issues(owner: str, repo: str) -> int:
    q = f"repo:{owner}/{repo} is:issue is:open"
    res = gh_api_json(f"search/issues?q={q}")
    return int(res.get("total_count", 0))

def list_repos(owner: str) -> List[dict]:
    return gh_api_json_slurp(f"orgs/{owner}/repos?per_page=100&type=all")

def build_rows(owner: str) -> List[RepoRow]:
    repos = list_repos(owner)
    rows: List[RepoRow] = []

    for r in repos:
        name = r["name"]
        full_name = r["full_name"]
        private = bool(r.get("private", False))
        archived = bool(r.get("archived", False))
        default_branch = r.get("default_branch") or "main"
        pushed_at = parse_iso(r["pushed_at"])

        # Separate issues vs PRs using search API (correct counts)
        open_prs = count_open_prs(owner, name)
        open_issues = count_open_issues(owner, name)

        code, comment, blank, top_langs = load_cloc(name)

        repo_dir = REPOS_DIR / name
        has_pyproject, project_name, has_tests, workflow_count, has_precommit = inspect_repo_files(repo_dir)

        rows.append(
            RepoRow(
                name=name,
                full_name=full_name,
                private=private,
                archived=archived,
                default_branch=default_branch,
                pushed_at=pushed_at,
                open_issues=open_issues,
                open_prs=open_prs,
                code=code,
                comment=comment,
                blank=blank,
                top_langs=top_langs,
                has_pyproject=has_pyproject,
                project_name=project_name,
                has_tests=has_tests,
                workflow_count=workflow_count,
                has_precommit=has_precommit,
            )
        )

    # Default: exclude archived repos from “management view”
    return [x for x in rows if not x.archived]

def render_report(rows: List[RepoRow]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    total_code = sum(r.code for r in rows)
    total_comment = sum(r.comment for r in rows)
    total_blank = sum(r.blank for r in rows)
    total_issues = sum(r.open_issues for r in rows)
    total_prs = sum(r.open_prs for r in rows)
    private_ct = sum(1 for r in rows if r.private)

    with_ci = sum(1 for r in rows if r.workflow_count > 0)
    with_tests = sum(1 for r in rows if r.has_tests)
    with_pyproject = sum(1 for r in rows if r.has_pyproject)
    with_precommit = sum(1 for r in rows if r.has_precommit)

    stale_cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    stale = [r for r in rows if r.pushed_at < stale_cutoff]

    by_loc = sorted(rows, key=lambda r: r.code, reverse=True)
    by_recent = sorted(rows, key=lambda r: r.pushed_at, reverse=True)

    lines: List[str] = []
    lines.append("# Org Health Report")
    lines.append("")
    lines.append(f"_Auto-generated: **{now}**_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Repos counted: **{len(rows)}** (private: **{private_ct}**)")
    lines.append(f"- LOC (code): **{total_code:,}**  |  comment: **{total_comment:,}**  |  blank: **{total_blank:,}**")
    lines.append(f"- Open issues: **{total_issues:,}**  |  Open PRs: **{total_prs:,}**")
    lines.append(f"- CI workflows present: **{with_ci}/{len(rows)}**")
    lines.append(f"- `tests/` present: **{with_tests}/{len(rows)}**")
    lines.append(f"- `pyproject.toml` present: **{with_pyproject}/{len(rows)}**")
    lines.append(f"- pre-commit config present: **{with_precommit}/{len(rows)}**")
    lines.append("")

    lines.append("## Top repos by LOC")
    lines.append("")
    lines.append("| Repo | Private | Project | LOC (code) | Last push | Issues | PRs | CI | Tests |")
    lines.append("|---|:---:|---|---:|---:|---:|---:|:---:|:---:|")
    for r in by_loc[:15]:
        proj = r.project_name or ""
        lines.append(
            f"| `{r.name}` | {'🔒' if r.private else ''} | {proj} | {r.code:,} | {fmt_date(r.pushed_at)} | {r.open_issues:,} | {r.open_prs:,} | {'✅' if r.workflow_count>0 else ''} | {'✅' if r.has_tests else ''} |"
        )
    lines.append("")

    lines.append("## Most recently updated")
    lines.append("")
    lines.append("| Repo | Last push | LOC (code) |")
    lines.append("|---|---:|---:|")
    for r in by_recent[:15]:
        lines.append(f"| `{r.name}` | {fmt_date(r.pushed_at)} | {r.code:,} |")
    lines.append("")

    if stale:
        lines.append("## Stale repos (no push in 90 days)")
        lines.append("")
        lines.append("| Repo | Last push | LOC (code) |")
        lines.append("|---|---:|---:|")
        for r in sorted(stale, key=lambda x: x.pushed_at):
            lines.append(f"| `{r.name}` | {fmt_date(r.pushed_at)} | {r.code:,} |")
        lines.append("")

    lines.append("## Full repo table")
    lines.append("")
    lines.append("| Repo | Private | Default branch | Project | LOC (code) | Last push | Issues | PRs | Workflows | Top langs (code LOC) |")
    lines.append("|---|:---:|---|---|---:|---:|---:|---:|---:|---|")
    for r in sorted(rows, key=lambda x: x.name.lower()):
        langs = ", ".join([f"{k}:{v:,}" for k, v in r.top_langs]) if r.top_langs else ""
        proj = r.project_name or ""
        lines.append(
            f"| `{r.name}` | {'🔒' if r.private else ''} | `{r.default_branch}` | {proj} | {r.code:,} | {fmt_date(r.pushed_at)} | {r.open_issues:,} | {r.open_prs:,} | {r.workflow_count} | {langs} |"
        )
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- LOC is computed by `cloc` with common cache/build/vendor directories excluded.")
    lines.append("- Issues/PRs are counted via GitHub search (so PRs are not mistakenly included in issue counts).")
    lines.append("- Archived repos are excluded by default (edit script if you want them included).")
    lines.append("")
    return "\n".join(lines)

def render_readme_block(rows: List[RepoRow]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total_code = sum(r.code for r in rows)
    total_issues = sum(r.open_issues for r in rows)
    total_prs = sum(r.open_prs for r in rows)
    private_ct = sum(1 for r in rows if r.private)

    by_loc = sorted(rows, key=lambda r: r.code, reverse=True)[:5]
    by_recent = sorted(rows, key=lambda r: r.pushed_at, reverse=True)[:3]

    block: List[str] = []
    block.append(METRICS_START)
    block.append("")
    block.append("## Org health (auto-updated)")
    block.append("")
    block.append(f"- **{len(rows)} repos** (private: **{private_ct}**) — updated **{now}**")
    block.append(f"- **LOC (code): {total_code:,}+**  |  **Open issues:** {total_issues:,}  |  **Open PRs:** {total_prs:,}")
    block.append("")
    block.append("**Top repos by LOC**")
    for r in by_loc:
        block.append(f"- `{r.name}` — {r.code:,}{' (private)' if r.private else ''}")
    block.append("")
    block.append("**Most recently updated**")
    for r in by_recent:
        block.append(f"- `{r.name}` — {fmt_date(r.pushed_at)}")
    block.append("")
    block.append("_Full report: `docs/HEALTH_REPORT.md`_")
    block.append("")
    block.append(METRICS_END)
    return "\n".join(block)

def update_profile_readme(rows: List[RepoRow]) -> None:
    if not PROFILE_README.exists():
        return

    text = PROFILE_README.read_text(encoding="utf-8")
    new_block = render_readme_block(rows)

    if METRICS_START in text and METRICS_END in text:
        pattern = re.compile(
            re.escape(METRICS_START) + r".*?" + re.escape(METRICS_END),
            flags=re.DOTALL,
        )
        text2 = pattern.sub(new_block, text)
    else:
        text2 = text.rstrip() + "\n\n" + new_block + "\n"

    PROFILE_README.write_text(text2, encoding="utf-8")

def main() -> None:
    CLOC_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    if not REPOS_DIR.exists():
        raise SystemExit(f"REPOS_DIR does not exist: {REPOS_DIR} (workflow should clone repos first)")

    rows = build_rows(ORG)
    OUT_REPORT.write_text(render_report(rows), encoding="utf-8")
    update_profile_readme(rows)
    print("Wrote docs/HEALTH_REPORT.md and updated profile/README.md (if present).")

if __name__ == "__main__":
    main()
