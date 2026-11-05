# Perpetual American Put

[English project overview](../README.md#english) | [中文项目说明](../README.md#中文)

This directory contains the selected obstacle/free-boundary BVP. The repository overview gives the model, both stages and the five-member division of work.

## D's Stage 2 studies

Run `python -m pytest -q -p no:cacheprovider` here or at the repository root
for all 64 A/B/D tests. Run `python stage2_studies.py` here to create a fresh
`stage2_D_runs/<UTC timestamp>/`. Then run `python verify_stage2_D.py <run>` and
`python build_stage2_docs.py <run>` to verify arrays and refresh D's report tables.
See [D's handoff](docs/handoff_D.md). The original `Member_D/` upload is preserved;
this directory is the maintained runnable version. C/E review and official audit remain pending.

## A's foundation and handoff

- `problem.py`: payoff, Stage 1 exact data, dividend rates and volatility data.
- `discretization.py`: monotone tridiagonal -L assembly and Dirichlet elimination.
- `tests/test_foundation.py`: independent model, hand-row and polynomial checks.
- `inspect_assembly.py`: assembly diagnostics without an LCP solve.
- [Problem definition](docs/problem_definition.md), [team plan](docs/team_plan.md) and [A's handoff](docs/handoff_A.md).

A's 35 foundation tests passed. From this directory, with the intended Python environment active:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python inspect_assembly.py
```

## Existing prototype

`solver.py`, `run_project.py`, `build_report.py`, `Report_Source.md`, `results/`, `figures/` and `protocols/` were already present. B-E review the solver, reproduce the experiments and write their own report sections. A's validation covers the model and assembly, not the earlier full solver runs. The older checksum file describes that earlier snapshot.

The report-generation script can create `American_Put_Report.pdf` after the results have been reviewed. The generated report is not currently tracked in this repository. Official course worksheets and independent student sign-off remain separate requirements.
