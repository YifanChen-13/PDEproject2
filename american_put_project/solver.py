"""Monotone finite-difference LCP solver. Run run_project.py for all experiments."""
import time
import numpy as np
from scipy.linalg import solve_banded
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from problem import K, R, EXACT_STAR, exact, volatility
from discretization import assemble, action

def contact_threshold(s, full, contact_tol=1e-7):
    """Last contact node connected to zero; bracket is nodal, not certified.

    The artificial far endpoint and all S>=K nodes are excluded. No
    interpolation is used. A large tolerance can change this classification.
    """
    if not np.isfinite(contact_tol) or contact_tol < 0:
        raise ValueError("contact_tol must be finite and nonnegative")
    gaps = full - np.maximum(K-s, 0)
    eligible = (s < K) & (np.abs(gaps) <= contact_tol)
    eligible[-1] = False
    k = 0
    while k+1 < len(s) and eligible[k+1]:
        k += 1
    contiguous = bool(eligible[0] and not np.any(eligible[k+1:]))
    return k, contiguous

def solve(smax=600., h=.125, stage=2, tol=1e-8, exact_boundary=False,
          contact_tol=1e-7, maxiter=20000):
    """Payoff-initialised policy iteration; ties choose continuation.

    Absolute LCP residual controls convergence. A repeated policy can stop at
    a scale-dependent floating-point floor, but never counts as meeting tol.
    """
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError("tol must be finite and positive")
    if isinstance(maxiter, bool) or not isinstance(maxiter, (int, np.integer)) or maxiter < 1:
        raise ValueError("maxiter must be a positive integer")
    if not np.isfinite(contact_tol) or contact_tol < 0:
        raise ValueError("contact_tol must be finite and nonnegative")
    start=time.perf_counter()
    s,lo,diag,up,f,right=assemble(smax,h,stage,exact_boundary)
    psi=np.maximum(K-s[1:-1],0)
    v=psi.copy()
    old_policy=None
    for it in range(1,maxiter+1):
        a=action(lo,diag,up,v)-f
        gap=v-psi
        # Continue at exact ties. At the payoff initialisation, the zero tail has
        # a=gap=0; treating it as exercise would propagate continuation one node
        # per iteration and make fine-grid runs unnecessarily expensive.
        exercise=gap < a
        ab=np.zeros((3,len(v)))
        ab[1]=np.where(exercise,1,diag)
        ab[0,1:]=np.where(exercise[:-1],0,up[:-1])
        ab[2,:-1]=np.where(exercise[1:],0,lo[1:])
        rhs=np.where(exercise,psi,f)
        v=solve_banded((1,1),ab,rhs,check_finite=False)
        a=action(lo,diag,up,v)-f
        gap=v-psi
        residual=float(np.max(np.abs(np.minimum(a,gap))))
        if not np.all(np.isfinite(v)) or not np.isfinite(residual):
            raise RuntimeError("Non-finite policy solution or LCP residual")
        # Componentwise scale of cancellation in A*v-rhs. This is a numerical
        # floor heuristic, not a forward-error bound or a relaxed requested tol.
        scale = np.abs(diag*v) + np.abs(f)
        scale[1:] += np.abs(lo[1:]*v[:-1])
        scale[:-1] += np.abs(up[:-1]*v[1:])
        residual_floor = 100*np.finfo(float).eps*max(1.,float(scale.max()),float(np.abs(v).max()))
        if residual<=tol:
            termination_reason="requested_tolerance"
            break
        # If a policy repeats, all remaining defect is floating-point linear-solve error.
        if old_policy is not None and np.array_equal(exercise,old_policy):
            if residual > residual_floor:
                raise RuntimeError(f"Repeated policy with large defect {residual}")
            termination_reason="floating_point_floor"
            break
        old_policy=exercise.copy()
    else:
        raise RuntimeError(f"Policy iteration exceeded maxiter={maxiter}; residual={residual:.6g}, requested_tol={tol:.6g}")
    full=np.r_[K,v,right]
    gaps=full-np.maximum(K-s,0)
    # Restrict contact classification to S<K: zero far-field data is not exercise.
    k,contiguous=contact_threshold(s,full,contact_tol)
    row_norm=diag.copy()
    row_norm[1:] += np.abs(lo[1:])
    row_norm[:-1] += np.abs(up[:-1])
    lin_res=action(lo,diag,up,v)-f
    lin_res[exercise]=v[exercise]-psi[exercise]
    denom=np.where(exercise,1,row_norm)*np.max(np.abs(v))+np.abs(np.where(exercise,psi,f))
    stats=dict(stage=stage,smax=smax,h=h,N=len(s)-1,iterations=it,
        seconds=time.perf_counter()-start,star=float(s[k]),star_upper=float(s[k+1]),
        min_a=float(a.min()),min_gap=float(gap.min()),lcp_residual=residual,
        scaled_backward_residual=float(np.max(np.abs(lin_res)/np.maximum(denom,1))),
        requested_tol=tol,met_requested_tol=bool(residual<=tol),
        floating_point_floor=bool(residual>tol),contact_tol=contact_tol,
        termination_reason=termination_reason,residual_floor_estimate=float(residual_floor),
        contiguous=bool(contiguous),min_above_payoff=float(gaps.min()),
        max_above_K=float(np.max(full-K)),max_first_difference=float(np.max(np.diff(full))),
        min_second_difference=float(np.min(np.diff(full,n=2))),
        min_diagonal_margin=float(np.min(diag-np.abs(lo)-np.abs(up))),
        max_offdiagonal=float(max(lo.max(),up.max())),
        smooth_fit_defect=float(abs((full[k+2]-full[k+1])/h+1)) if k+2<len(full) else float("nan"))
    return s,full,stats

def continuous_reference(smax=600.,stage=2):
    """Independent truncated-domain ODE shooting; no FDM matrix or policy iteration."""
    q=0 if stage==1 else .02
    def ode(s,y):
        sig=float(volatility(np.array([s]),stage)[0])
        return [y[1], (R*y[0]-(R-q)*s*y[1])/(.5*sig**2*s*s)]
    sol=solve_ivp(ode,(smax,10.),[0.,-1.],rtol=2e-11,atol=1e-12,dense_output=True,max_step=1.)
    assert sol.success
    def match(s):
        y=sol.sol(s)
        return y[0]+(K-s)*y[1]
    root=brentq(match,30.,99.,xtol=1e-11)
    scale=-1/sol.sol(root)[1]
    def value(s):
        s=np.asarray(s)
        out=K-s
        mask=s>root
        out[mask]=scale*sol.sol(s[mask])[0]
        return out
    return root,value
