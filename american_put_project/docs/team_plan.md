# Perpetual American put: five-member plan

The selected topic is Problem Pack, Section 5.3, pages 8-9. The active working
directory is `american_put_project/`. Each member writes their own report section,
records actual checks and commits through their own account. A-E are role labels;
names can be added when the group agrees on them.

## A: model and discrete foundation

- Fix K=100, r=0.05, the payoff, both volatility cases and dividend rates.
- State the global obstacle problem and the endpoint conditions.
- Derive and assemble a monotone tridiagonal discretisation of -L, including
  Dirichlet elimination and unknown ordering.
- Supply analytic Stage 1 data, independent hand-row tests and interface notes.

Deliver: `problem.py`, `discretization.py`, `inspect_assembly.py`, foundation tests,
and [handoff_A.md](handoff_A.md). Completion means model identities, boundary
contributions, matrix signs and the documented interface have been checked.
E independently reviews the stencil and tests. A reviews B's matrix integration.

## B: LCP solver

- Take ownership of policy iteration in the existing `solver.py` prototype.
- Explain the initial payoff iterate, policy choice, treatment of ties, banded
  solve and residual-based stopping rule. Policy iteration has no SOR omega.
- Check a small LCP by enumerating all active sets independently; test boundary
  reconstruction, stagnation, failure reporting and requested tolerance status.
- Define the last contiguous contact-node threshold, its tolerance and bracket.
  Exclude the artificial zero-value far endpoint from exercise classification.

Deliver: reviewed solver, solver tests, derivation and a handoff to C and D.
Completion means independent small-grid agreement and honest convergence status,
including cases stopped at a floating-point residual floor. E reviews the LCP
checks; A verifies that the solver uses the agreed assembly without changing it.

## C: Stage 1 exact validation

- Use q=0 and sigma=0.20, with exact threshold S*=500/7.
- Use the analytic right endpoint in the primary validation table to isolate
  mesh error. Label this endpoint choice explicitly.
- Run h=0.5, 0.25, 0.125, 0.0625 at Smax=400 after B's solver is reviewed.
- Tabulate maximum value error, threshold error, actual residual, requested
  tolerance and iterations. Define any additional L2 weights.
- Examine observed orders and smooth fit; discuss contact-node quantisation.

Deliver: Stage 1 script/table/plots and its report section. Completion means four
executed levels with reproducible values and supported convergence claims.
D checks norm definitions and error/order calculations; E reruns one level.

## D: Stage 2 numerical and truncation studies

- Use q=0.02 and the specified local volatility, with zero at Smax.
- At fixed Smax=600, run the same four mesh sizes and compare with a refined-grid
  reference. Refine that reference once more to quantify its uncertainty.
- Separately vary Smax=300, 400, 600 at fixed h=0.0625. Compare values on a common
  asset-price interval and report the movement of the exercise threshold.
- Keep mesh, reference and domain errors distinct; report cost and solver
  diagnostics, not only prices and convergence slopes.

Deliver: Stage 2 script, reference check, domain table, plots and report section.
Completion means two clearly separated studies; Smax=600 is not automatically
a certified infinite-domain answer. C reviews the comparison grids and rates;
E reruns a representative case.

## E: independent verification and report integration

- Review A's matrix signs, diagonal dominance, endpoint handling and LCP signs.
- Review B's complementarity checks and contact-set rule; verify payoff <= V <= K,
  nonincreasing values, convexity and a single contact interval from zero.
- Review and validate the independent continuation ODE in the existing prototype;
  compare with FDM on the same truncated domain, using independently derived data.
- Perform solver-tolerance and contact-tolerance sensitivity checks. Report a
  scaled/backward residual separately from solution error.
- Coordinate the report, reproducibility instructions and course audit records.
  Each author remains responsible for their own section and actual contribution.

Deliver: independent-check scripts, diagnostic tables and review records, plus
the integrated report. C and D check E's error/residual calculations. Official
worksheet completion and human sign-off require the actual course templates.

## Working order and branches

1. A publishes the model and assembly contract; B and E review the foundation.
2. B works on `feature/lcp-solver`; E starts independent validation.
3. C works on `feature/stage1-validation`; D on `feature/stage2-studies`, using
   B's reviewed solver. Their experiment setups and report derivations can begin
   before the solver is final.
4. E works on `feature/independent-checks` and integrates reviewed results.

Before each new solve, record predictions in the course worksheet, then append
the actual outcome without rewriting the prediction. The official AI five-gate
audit must be completed before solver output is used as course evidence.

## Existing files and contribution status

The repository already contained `solver.py`, experiment scripts, report source,
plots and numerical output before this topic correction. They are a starting
prototype and earlier records. Their presence does not establish that B-E have
completed or independently verified their assigned work. A's current foundation
checks do not certify those earlier solver runs.
