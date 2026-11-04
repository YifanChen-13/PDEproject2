# Problem definition: Perpetual American put

**Topic:** Problem Pack, Section 5.3, pp. 8-9. **Method:** monotone 1D finite
differences for an obstacle problem. This compact sheet records the model and
stencil for transfer to the official course template.

## Continuous problem

For S>0, define psi(S)=max(K-S,0) and

```
L V = 0.5*sigma(S)^2*S^2*V'' + (r-q)*S*V' - r*V
min(-L V, V-psi) = 0.
```

Thus -L V>=0, V>=psi and (-L V)(V-psi)=0. In a contact interval [0,S*], V=K-S;
continuation satisfies L V=0. Value matching V(S*)=K-S* and smooth fit
V'(S*)=-1 are verified when recovering S*, rather than imposed at a guessed edge.

K=100 and r=0.05. Stage 1 has q=0, sigma=0.20, lambda=-2.5, S*=500/7, and the
exact continuation value `(K-S*)*(S/S*)**lambda`. Stage 2 has q=0.02 and
`sigma(S)=0.20*(1+0.35*tanh(log(S/K)/0.40))`, with right limit 0.13 at zero.

On [0,Smax], impose V(0)=K. Stage 1's main mesh-validation case uses the exact
V(Smax) to isolate discretisation. Stage 2 uses V(Smax)=0 and studies
Smax=300,400,600 separately from mesh refinement. There is no PDE row at zero.

## Discrete problem

Use S_i=i*h, N=Smax/h and unknowns i=1,...,N-1. Write
d_i=0.5*sigma(S_i)^2*S_i^2, b_i=(r-q)*S_i, b+=max(b,0), b-=max(-b,0).

```
lo_i = -d_i/h^2 - b-_i/h
diag_i = 2*d_i/h^2 + abs(b_i)/h + r
up_i = -d_i/h^2 - b+_i/h
min(A*v-rhs, v-psi_interior) = 0, with A=-L_h.
```

Move known endpoints into rhs with their negative off-diagonal coefficients.
The upwind choice gives nonpositive off-diagonals and diagonal-dominance margin
r>0, including near the degenerate endpoint. A tridiagonal LCP suits this 1D
model; B takes ownership of policy iteration and its independent tests.

Use four mesh levels h=0.5,0.25,0.125,0.0625. C validates values and thresholds
against Stage 1's exact data. D uses a refined-grid reference for Stage 2. E
checks complementarity, shape, tolerance sensitivity and an independent ODE.
