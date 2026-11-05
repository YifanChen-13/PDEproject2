# D: Stage 2 local-volatility and domain studies

## Scope and source

This contribution uses A's model/assembly and B's solver from main commit
`489f549136502ff37e57a71cf2c73292f007ace3`. Neither module was changed.
The source is Problem Pack Section 5.3, pp. 8–9, with protocols on p. 10.
The existing prototype's results, figures, report and protocol records are not
overwritten. New outputs live in `stage2_D_runs/<UTC timestamp>/`.

## Run

From `american_put_project/`, with Python 3.10+ and the requirements installed:

```bash
python -m pytest -q -p no:cacheprovider
python stage2_studies.py
```

Each invocation creates a fresh run directory. The fine references require
153599 interior unknowns and thousands of policy iterations; allow a few
minutes. `seconds` measures one solver call, excluding plotting and compression;
it is one observed timing, not a repeated timing benchmark. `N` counts intervals,
so the number of interior unknowns is `N-1`. Tridiagonal storage is O(N).

## Experiment definitions

- Mesh: Smax=600, h=0.5,0.25,0.125,0.0625; reference h=1/128; check h=1/256.
- Domain: h=0.0625, Smax=300,400,600; compare coincident nodes on [0,300]
  and [0,200]. Reuse the same h=0.0625, Smax=600 solve from the mesh study.
- Algebraic sensitivity: h=0.0625 at tolerances 1e-6,1e-8,1e-10; finest
  reference at 1e-8 and 1e-10. All requested-tolerance flags remain explicit.
- Left value K=100; zero right endpoint in every D solve. q=0.02 and the
  specified local volatility. Policy iteration starts from payoff and has no
  relaxation parameter. Contact tolerance 1e-7; no interpolation.

`nested_sample` rejects comparison nodes outside the reference domain or not
coincident with reference nodes. The maximum norm is a nodal maximum. The L2
norm is sqrt(h*(sum of squared interior errors + half the squared endpoint
errors)); it is a trapezoidal integral norm, not RMS. Orders are log2 of
successive errors at h and h/2. `star` is the last contiguous contact node;
`star_upper` is the next node. Their interval is not a certified enclosure of
the continuous free boundary. Threshold differences to reference nodes are
reference comparisons, not exact threshold errors.

## Deliverables

`stage2_studies.py`: reproducible experiment driver.
`tests/test_stage2_studies.py`: norm weighting and nested-grid safeguards.
`precomputation_D.md`: predictions preserved before numerical execution.
`report_D.md`: English report section with measured tables and limitations.
`guide_D_CN.md`: Chinese explanation and interpretation of D's contribution.
Each run contains mesh/domain/reference/tolerance/diagnostic CSVs, compressed
solution arrays, three PNG/PDF figure pairs, JSON metadata/source checksums,
and a prediction/outcome JSONL log.

## Review status

Local automated checks: 64 passed (35 A foundation, 25 B solver, 4 D comparison
checks). Environment: Python 3.12.7, NumPy 1.26.4, SciPy 1.13.1,
Matplotlib 3.9.2, pytest 7.4.4; see summary_D.json for authoritative full version
strings. This uses existing installed packages, not a clean installation.

C still needs to review node alignment, norms and reported rates. E still
needs to rerun one representative D case and complete independent solver
review. Codex assisted with the script, tests, execution, analysis and text.
These are AI-assisted draft results. The official precomputation and five-gate
audit worksheets and actual human sign-offs remain to be completed before
using solver output as course evidence. No human review or course sign-off is
claimed here, and no prior audit record is relabelled as completed.
