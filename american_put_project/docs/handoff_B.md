# B handoff: reviewed LCP solver

> Historical planning or handoff record. For current commands and status, see the repository README.

Date: 2026-11-05. Topic: Problem Pack 5.3, perpetual American put.

## Contribution and scope

Reviewed the existing policy-iteration prototype, retained A's assembly and
public solve signature, and added scale-dependent floating-point-floor handling,
explicit termination reasons, numerical-control validation, non-finite failure
checks, a separately testable contact classifier, and safe smooth-fit indexing.
The independent ODE routine is preserved and remains E's review responsibility.

See derivation_B.md for the report section and precomputation_B.md for predictions
recorded before the tests. No prior experiment outputs were relabelled or rerun
as B's formal contribution. C/D still own the four-level studies.

## Executed validation

From american_put_project/: `python -m pytest -q -p no:cacheprovider`.
Result: **60 passed** (A's 35 and B's 25). Python 3.10.14, NumPy 1.26.4,
SciPy 1.15.3. Tests use pytest from a workspace dependency directory; this is
not a clean-machine installation test.

- All active sets enumerated on 1/3/7-unknown grids for Stage 1 with exact or
  zero right endpoints and Stage 2 with zero endpoint: agreement passed.
- Boundary reconstruction, contiguous threshold, isolated contact detection,
  exclusion of the far endpoint and contact-tolerance sensitivity: passed.
- Invalid controls, iteration-budget exhaustion, non-finite solves, repeated
  policies with large defects and honest floating-point-floor status: passed.
- Both stage representative solves: independently reconstructed dense residual,
  payoff lower bound and monotone values passed within numerical tolerances.

Predictions supported. The initial maxiter test used a coarse grid that solved
in one step; changed the test to h=1 and tol=1e-30 to exercise budget exhaustion,
without changing solver behavior to force a failure.

## Representative outcomes (Smax=400, h=1, contact_tol=1e-7)

| Case | Right data | Iterations | LCP residual | Requested tol | Met tol | Contact transition |
|---|---|---:|---:|---:|---|---|
| Stage 1 | exact | 29 | 6.1462e-13 | 1e-8 | yes | [71,72] |
| Stage 2 | zero | 31 | 1.2861e-12 | 1e-8 | yes | [69,70] |
| Stage 1 tight | exact | 30 | 6.1462e-13 | 1e-30 | no: floating-point floor | [71,72] |

The scaled policy-system backward residuals were 4.80e-15 and 9.89e-15.
Stage 2's minimum payoff gap was -1.29e-12 (round-off); no claim of exact
inequality satisfaction in floating point is made. These nodal transition
brackets are not certified continuous-boundary enclosures.

## Next owners and AI transparency

A reviews that B uses the agreed assembly unchanged; E independently reviews
the LCP checks, floor heuristic and contact rule. C/D can use the preserved solve
interface but must inspect met_requested_tol and termination_reason before using
any results. Policy repetition is not successful requested-tolerance convergence.

Codex assisted solver review/changes, test and documentation authoring. This
automated validation does not constitute independent human review or completion
of the course's official five-gate worksheets. Formal worksheets and sign-offs
remain pending; no earlier AI audit record was overwritten.
