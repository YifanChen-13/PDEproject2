# A's handoff: Perpetual American put

> Historical planning or handoff record. For current commands and status, see the repository README.

Date: 2026-11-04. Next owner: B. E reviews the foundation independently; C and D
can prepare their experiment definitions in parallel.

## 1. Continuous problem and sign convention

Source: Problem Pack, Section 5.3, pp. 8-9; common protocols on p. 10.

For S>0,

```
psi(S) = max(K-S, 0)
L V = 0.5*sigma(S)^2*S^2*V'' + (r-q)*S*V' - r*V
min(-L V, V-psi) = 0
```

K=100 and r=0.05. The complementarity conditions hold throughout the domain:
`-L V >= 0`, `V-psi >= 0`, and their product is zero. In the contact region
`V=K-S`; in continuation `L V=0`. The free boundary is recovered from the solution.
Value matching and smooth fit are properties to verify, not a replacement for
the obstacle condition on the full contact region.

| Case | q | sigma(S) | Right endpoint |
|---|---:|---|---|
| Stage 1 exact validation | 0 | 0.20 | analytic V(Smax) for mesh validation |
| Stage 2 numerical model | 0.02 | `0.20*(1+0.35*tanh(log(S/100)/0.40))` | 0 |

The left endpoint is always V(0)=K. The PDE is not evaluated at S=0, where the
operator degenerates. `volatility(0, 2)` returns the right limit 0.13 without
evaluating log(0). Stage 2 rejects `exact_boundary=True`.

For Stage 1, lambda=-2.5 and S*=lambda*K/(lambda-1)=500/7. The exact value is
K-S for S<=S*, and `(K-S*)*(S/S*)**lambda` for S>S*. `exact` is Stage 1 data
only. `payoff`, `exact` and `volatility` accept nonnegative finite scalars or
arrays; integer input is converted to floating point.

## 2. Grid, unknown ordering and operator

`S_i=i*h`, i=0,...,N, N=Smax/h. The ratio must be an integer, N>=2, Smax>K.
Unknown `v[k]` corresponds to `S[k+1]`, i.e. interior node i=k+1. Boundary nodes
are eliminated, leaving N-1 unknowns.

Put `d_i=0.5*sigma(S_i)^2*S_i^2` and `b_i=(r-q)*S_i`. With b+ = max(b,0) and
b- = max(-b,0), the row of A=-L_h is

```
lo_i   = -d_i/h^2 - b-_i/h
diag_i =  2*d_i/h^2 + abs(b_i)/h + r
up_i   = -d_i/h^2 - b+_i/h
```

For this pack b>0. The first derivative in L is approximated by
`(V[i+1]-V[i])/h`; this is the monotone upwind choice for the drift coefficient
`-b` in -L. Both off-diagonals are nonpositive and
`diag_i - abs(lo_i) - abs(up_i) = r > 0`. The unknown-only matrix is strictly
diagonally dominant with the same signs, hence a nonsingular M-matrix.

Known endpoints contribute

```
rhs[0]  -= lo[0]  * K
rhs[-1] -= up[-1] * right_value
```

For a single interior unknown both contributions accumulate in the same row.
The eliminated matrix is generally nonsymmetric. A monotone matrix is useful
for the obstacle discretisation; it does not turn the LCP into one linear solve.

## 3. Interface for B

Run scripts from `american_put_project/`.

```python
from problem import K, payoff
from discretization import assemble, action

S, lo, diag, up, rhs, right = assemble(400.0, 0.5, stage=1, exact_boundary=True)
psi = payoff(S[1:-1])
v0 = psi.copy()  # proposed initial iterate for B's policy iteration
a0 = action(lo, diag, up, v0) - rhs
gap0 = v0 - psi
```

- S has shape `(N+1,)`; lo, diag, up and rhs have shape `(N-1,)`.
- lo[0] and up[-1] retain the known-boundary coefficients for inspection.
- `action` uses only lo[1:] and up[:-1]; it applies A to interior unknowns.
- B solves `min(A*v-rhs, v-psi)=0` componentwise.
- Reconstruct the full value as `np.r_[K, v, right]`.
- Return actual residuals and requested-tolerance status. Repeated policies
  alone do not prove that the requested residual tolerance was met.

The existing solver and experiment driver keep their public function names:
`solver.py` now imports these shared data/assembly functions. B should review
the existing policy-iteration prototype and add solver-specific tests. A has
not rerun or certified its full experiment outputs.

## 4. Hand checks supplied

At S=100, h=1, the (lo, diag, up) rows are

```
Stage 1: (-200, 405.05, -205)
Stage 2: (-200, 403.05, -203)
```

At Smax=200, h=50, Stage 1 has three interior unknowns:

```
A = [[ 0.14, -0.07,  0   ],
     [-0.08,  0.31, -0.18],
     [ 0,    -0.18,  0.56]]
rhs = [2, 0, 0.33*V_exact(200)]
```

Independent polynomial checks use `(-L)(c+m*S)=r*c+q*m*S`. For V=S^2, the
forward-drift consistency defect at a fixed node is `-(r-q)*S*h`. Refinement
should therefore halve this defect. This is an operator check, not a solved
option value or the global LCP convergence rate.

## 5. Validation record

Predictions are preserved separately in [precomputation_A.md](precomputation_A.md).
The following checks were executed on 2026-11-04 from `american_put_project/`
using the repository's `.venv`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe inspect_assembly.py
```

Result: **35 tests passed**. Environment: Python 3.13.2, NumPy 2.2.4,
SciPy 1.15.2, pytest 9.2.0 and matplotlib 3.11.2. The virtual environment uses
the machine's existing NumPy/SciPy and installs test/plot dependencies locally;
this is not a clean-machine installation test.

| Check | Actual outcome |
|---|---|
| Stage 1 lambda, value matching, smooth fit and continuation equation | Passed |
| Stage 2 q, sigma(K), endpoint limit and integer inputs | Passed; sigma(0)=0.13, sigma(K)=0.20 |
| Hand row at S=100, h=1 | Stage 1 (-200,405.05,-205); Stage 2 (-200,403.05,-203) |
| Three-unknown matrix and single-unknown endpoint accumulation | Passed |
| Off-diagonal signs and complete-stencil dominance margin | Passed; margin approximately 0.05 in both stages |
| Constant and affine operator identities | Passed |
| Quadratic defect at fixed S=100, scaled by 100^2 | Halves with h in both stages, as predicted |
| Invalid domain, mesh and Stage 2 analytic-boundary requests | Rejected |
| Existing solver imports and assembly interface | Preserved; see compatibility check below |

The assembly-only inspection used Smax=400, h=1 and 399 interior unknowns.
The Stage 1 analytic right value was 0.38500102711758233; Stage 2's right value
was zero. All eight pre-check predictions were supported by these checks.

For compatibility, all 12 returned arrays/scalars from the original and split
assemblers were compared at Smax=400, h=0.5 for both stages, with maximum
absolute difference **0.0**. The original
assembly snapshot is retained locally outside the repository. No LCP solve was
run in this A validation, and no old result, figure or prediction log was changed.

## 6. What B should deliver next

1. Review the existing policy choice, banded policy system and stopping rule.
2. Check tiny-grid solutions against exhaustive active-set enumeration.
3. Report complementarity minima/residual, actual tolerance status and iterations.
4. Verify full boundary reconstruction and the contiguous contact-set rule.
5. Hand a tested solver to C and D; ask E to independently review the checks.

The complete coursework still needs B-E's reviewed implementations/experiments,
report sections, independent verification and the official course audit. Earlier
results in `results/` are preserved as previous records, not relabelled as this
run. `file_checksums.json` belongs to that older snapshot; it is not a current
manifest for A's changed source files.
