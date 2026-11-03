# Perpetual American put: complete computational project

Start with **American_Put_Report.pdf**. The report is in English and contains the
model, derivation, executed experiments, tables, interpretation and limitations.
Report_Source.md is an editable text version; build_report.py is the editable
typesetting source. No LaTeX installation is required.

## Run

Use Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python run_project.py
python build_report.py
```

The fine references are the most expensive part. Results are deterministic apart
from timings, timestamps, and floating-point differences between platforms.
The tested software versions are in results/summary.json.

## Files

- solver.py: monotone upwind FDM, banded policy solves, independent ODE shooting.
- run_project.py: complete experiments with assertions and predictive logging.
- results/: all convergence tables, diagnostics, NPZ solution arrays, summary and run log.
- figures/: PNG and vector PDF plots.
- protocols/: custom audit, predictions, reconciliation and AI transparency.

## Reading the numbers

Stage 1 imposes the exact upper boundary so its errors isolate discretisation.
Stage 2 imposes zero at the upper boundary and separates fixed-domain mesh error
from domain sensitivity. The threshold is the last contiguous contact node, not
an interpolated continuous free boundary. Grid reference results are not exact.
Do not interpret the Smax=600 result as a certified infinite-domain solution.

The detailed diagnostic tables include unsuccessful requested stopping thresholds:
when a policy repeats at roundoff, actual residual and floating_point_floor are
recorded, and met_requested_tol is false. These are deliberate transparent records.

## Course records

The exact official worksheets were not supplied. Custom records are included,
with this limitation stated. They do not replace required official templates or
independent student verification. No student contribution claims are invented.

The package does not alter or depend on existing files in Desktop/ODE_Project.
