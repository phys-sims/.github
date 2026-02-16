# .github

Contains default templates and org-wide docs.

## Health reporting

This repo includes health tooling that can generate an org-wide report and embed key findings into `profile/README.md`:

- `scripts/health/run_cloc.sh <repos_dir>` computes LOC JSON files under `.health/cloc_json/`.
- `scripts/health/generate_health_report.py --org <org> --repos-dir <repos_dir>` writes `docs/HEALTH_REPORT.md` and updates the `<!-- HEALTH:START --> ... <!-- HEALTH:END -->` block in `profile/README.md`.
