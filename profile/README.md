# phys-sims

Physics-first simulation tooling in Python — focused on **reproducibility**, **typed contracts**, and **deterministic pipelines**.

**Code owner / maintainer:** Ryaan Lari (@RyaanLari)  
**Status snapshot date:** 2026-02-12

## What this org is about

This org is a portfolio + working ecosystem for:
- deterministic simulation cores with stable input/output contracts
- pipeline-based execution (typed stages, provenance/caching hooks, artifacts-by-reference)
- research tooling for reproducible experiments, sweeps, and optimization workflows

## Ecosystem map (what fits where)

- **phys-pipeline** → pipeline runtime + typed stage contracts (sequential + DAG, caching hooks, artifacts)
- **fiber-link-sim** → end-to-end deterministic fiber link simulator with stable `SimulationSpec → SimulationResult`
- **research-utils** → deterministic experimentation + optimization + agent tooling (sim-agnostic core)
- **abcdef-sim** → optics ABCDEF simulator scaffold built to sit on phys-pipeline (architecture-first; physics stage WIP)
- **cpa-architecture** → cross-repo ADRs + ecosystem governance (repo boundaries, policies)
- **cpa-workspace** (private) → meta repo to sync/dev multiple repos together
- **abcdef-testbench** (private) → private experiment/testbench repo for abcdef work
- **cookiecutter-phys / cookiecutter-testbench** → templates for consistent new repos

## Repositories (status + purpose)

| Repo | Status | What it is | Key entry points |
|---|---|---|---|
| https://github.com/phys-sims/phys-pipeline | **Active** | Typed pipeline runtime (sequential + DAG), caching/provenance, artifacts | `README.md`, `docs/how-to-build-simulations.md`, `docs/adr/INDEX.md`, `docs/v2-release-notes.md` |
| https://github.com/phys-sims/fiber-link-sim | **Active** | Deterministic fiber link simulator with stable schemas and staged pipeline | `README.md`, `STATUS.md`, `src/fiber_link_sim/schema/README.md`, `docs/stages_and_flags.md`, `docs/hft_latency_demo.md`, `docs/roadmaps/phys_pipeline_readiness.md` |
| https://github.com/phys-sims/research-utils | **Active** | Deterministic experimentation + optimization + agent tooling (sim-agnostic) | `README.md`, `STATUS.md`, `docs/how-to-use-agents.md`, `docs/v0.3-roadmap.md`, `docs/v0.4-roadmap.md` |
| https://github.com/phys-sims/abcdef-sim | **Active (scaffold; physics stage WIP)** | Architecture-first ABCDEF optics sim on phys-pipeline | `README.md`, `docs/architecture.md`, `docs/how-to-use.md`, `docs/adr/INDEX.md` |
| https://github.com/phys-sims/cpa-architecture | **Active** | Cross-repo ADRs + ecosystem governance | `README.md`, `docs/adr/INDEX.md`, `docs/adr/ECO-0004-repository-roles-boundaries.md` |
| https://github.com/phys-sims/cookiecutter-phys | **Active** | Cookiecutter template for new physics Python repos | `cookiecutter.json`, `{{cookiecutter.project_slug}}/README.md` |
| https://github.com/phys-sims/cookiecutter-testbench | **Maintenance** | Cookiecutter template for private testbench repos | `cookiecutter.json`, `{{cookiecutter.project_slug}}/README.md` |
| (private) https://github.com/phys-sims/cpa-workspace | **Active** | Multi-repo workspace orchestrator | `README.md`, `repos.toml`, `AGENTS.md` |
| (private) https://github.com/phys-sims/abcdef-testbench | **Maintenance** | Private research testbench scaffold | `README.md` |

## Getting started (fast path)

Pick the repo that matches your goal:

- Want the simulation runtime concepts? → start with **phys-pipeline**
- Want an end-to-end simulator with a stable spec/result contract? → **fiber-link-sim**
- Want reproducible experiments + optimization tooling? → **research-utils**
- Want the optics ABCDEF simulator architecture? → **abcdef-sim**
- Want cross-repo governance/decisions? → **cpa-architecture**

## Contributing (single-owner model)

- Use Issues for bug reports and feature proposals.
- Use PRs for code changes; keep PRs small and include tests.
- If you change a public contract or cross-repo boundary, add/update an ADR and link it.

(Org-wide issue/PR templates are intended to live in this repository to standardize contributions.)

## Org Health Summary 
<!-- HEALTH:START -->
<!-- HEALTH:END -->