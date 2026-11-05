# Perpetual American Put — Project 2

[中文说明](american_put_project/README.md) | [Report draft](american_put_project/report/main.pdf) | [Slides](american_put_project/slides/main.pdf)

This repository solves the one-dimensional perpetual American put obstacle problem in the course Problem Pack, Section 5.3. A monotone upwind finite-difference discretisation produces a tridiagonal linear complementarity problem, solved by policy iteration. Stage 1 has a closed-form benchmark. Stage 2 uses the prescribed local volatility, refined grids and separate domain studies.

## Setup and tests

Python 3.10 or newer is recommended. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
python -m pip install -r american_put_project/requirements-dev.txt
python -m pytest -q
```

The test suite collects A/B foundation and solver checks plus D's Stage 2 comparison checks. To reproduce experiments and figures, run:

```bash
python american_put_project/run_all.py
```

The full calculation includes two fine Stage 2 references and can take several minutes. It writes a fresh timestamped `american_put_project/reproduction_runs/` directory containing the Stage 2 results. `reproduction_runs/` is excluded from Git. The Stage 2 output path is printed at completion. See the [Chinese project guide](american_put_project/README.md) for individual commands, result locations, audit scope and interpretation.

## Repository layout

- `american_put_project/problem.py`, `discretization.py`, `solver.py` contain the common model, assembly and LCP solver.
- `stage1_validation.py`, `stage2_studies.py`, `independent_audit.py` run the Stage 1, Stage 2 and independent comparison studies.
- `tests/` contains automated checks. Root and project-level pytest configuration collect the same suite.
- `results/`, `figures/`, `stage2_D_runs/` preserve prototype and D numerical evidence. The D run `20261105T132543802032Z` is the source for the current report tables.
- `report/` and `slides/` contain English LaTeX sources and compiled technical drafts. The report uses the explicitly identified saved data and is not regenerated from new results automatically.
- `docs/` contains derivations, study reports and handoffs. `protocols/` contains AI-authored predictions and earlier automated audit records. `archive/` preserves historical deliveries, README files and checksums.

## Status

The A/B numerical foundation, four-level Stage 1 validation, Stage 2 studies, independent collocation and a matched projected-SOR comparison are available. AI-assisted numerical and code checks are recorded in [the audit](american_put_project/docs/technical_audit.md). Every member still needs to perform and record their own review, reproduction, individual contribution statement and the course's human interrogation. Team identity and contributions in the report remain to be supplied accurately. The compiled report and slide deck are drafts for team review.
