# phys-sims

Physics-first simulation tooling in Python — focused on **reproducibility**, **typed contracts**, and **deterministic pipelines**.

If you're an employer: this org is a portfolio of applied scientific software work (simulation architecture, testing/CI discipline, and API design for research tooling).
If you're a collaborator (or future me): start at the “How the repos fit together” section and then jump into the repo that matches your goal.

---

## Highlights

- **Deterministic simulation cores** with stable input/output contracts (schemas + typed models)
- **Pipeline architecture**: modular stages, provenance, caching hooks, optional artifact recording
- **Engineering quality**: pytest discipline (including slow-test separation), linting/pre-commit, type-checking, docs/ADRs

---

## Flagship projects

### 1) fiber-link-sim — deterministic fiber-optic link simulator core
**What it is:** a physics backend with a stable `SimulationSpec → SimulationResult` contract, versioned schemas, and a staged link pipeline (Tx → Channel → Rx → DSP → FEC → Metrics).  
**Why it matters:** this is the kind of “real” simulation backbone that upstream tools (GUIs, orchestrators, sweep runners) can reliably build on.  
Repo: https://github.com/phys-sims/fiber-link-sim

### 2) phys-pipeline — typed runtime for physics simulation pipelines
**What it is:** a lightweight framework for building and executing simulations as typed stages with deterministic execution, provenance/caching hooks, and optional artifact recording.  
Repo: https://github.com/phys-sims/phys-pipeline

### 3) abcdef-sim — ABCD ray tracing with dispersion
**What it is:** extends ABCD ray tracing to include dispersion effects.  
Repo: https://github.com/phys-sims/abcdef-sim

### 4) cpa-architecture — cross-repo ADRs and system-level conventions
**What it is:** the “governance + architecture spine” for decisions that span multiple repos, including an ecosystem ADR process and repo-boundary rules.  
Repo: https://github.com/phys-sims/cpa-architecture

---

## How the repos fit together (mental model)

- **phys-pipeline** = general-purpose pipeline runtime (typed stages, provenance/caching, artifacts)
- **fiber-link-sim** = an end-to-end fiber link simulator that uses a staged pipeline approach + stable schemas for orchestration
- **abcdef-sim** = a focused optics/ray-tracing simulator module
- **cpa-architecture** = cross-repo ADRs + system conventions

---

## Getting started (contributors)

1. Pick a repo above and read its README.
2. Install in editable mode and run the fast test suite.
3. If you’re adding architecture or changing contracts, write/update ADRs.

---

## Templates & repo bootstrap

To keep new repos consistent (layout, tooling, CI expectations), this org also includes Cookiecutter templates:

- `cookiecutter-phys` — bootstrap a new physics Python package repo
- `cookiecutter-testbench` — bootstrap a testbench repo layout

(These are intentionally minimal template repos; see their cookiecutter configs.)

---

## Collaboration

- Use Issues for bugs/feature proposals.
- Use PRs for changes; keep them small and include tests.
- When touching cross-repo contracts, document the decision (ADRs) and link related ADRs across repos.
