"""Monotone finite-difference LCP solver. Run run_project.py for all experiments."""
import time
import numpy as np
from scipy.linalg import solve_banded
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

K, R = 100.0, 0.05
EXACT_STAR = K * 2.5 / 3.5

def exact(s):
    s = np.asarray(s, dtype=float)
    v = K-s
    mask = s > EXACT_STAR
    v[mask] = (K-EXACT_STAR)*(s[mask]/EXACT_STAR)**(-2.5)
    return v

def volatility(s, stage):
    if stage == 1:
        return np.full_like(s, .2)
    return .2*(1+.35*np.tanh(np.log(s/K)/.4))

def assemble(smax, h, stage, exact_boundary=False):
    n = round(smax/h)
    assert abs(n*h-smax) < 1e-8
    s = np.linspace(0, smax, n+1)
    x = s[1:-1]
    q = 0 if stage == 1 else .02
    d = .5*volatility(x,stage)**2*x*x
    b = (R-q)*x
    lo = -d/h**2-np.maximum(-b,0)/h
    up = -d/h**2-np.maximum(b,0)/h
    diag = 2*d/h**2+np.abs(b)/h+R
    right = float(exact(np.array([smax]))[0]) if exact_boundary else 0.
    f = np.zeros(n-1)
    f[0] -= lo[0]*K
    f[-1] -= up[-1]*right
    return s,lo,diag,up,f,right

def action(lo,diag,up,v):
    a=diag*v
    a[1:] += lo[1:]*v[:-1]
    a[:-1] += up[:-1]*v[1:]
    return a

def solve(smax=600., h=.125, stage=2, tol=1e-8, exact_boundary=False,
          contact_tol=1e-7, maxiter=20000):
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
        if residual<=tol:
            break
        # If a policy repeats, all remaining defect is floating-point linear-solve error.
        if old_policy is not None and np.array_equal(exercise,old_policy):
            if residual > max(tol,2e-5):
                raise RuntimeError(f"Repeated policy with large defect {residual}")
            break
        old_policy=exercise.copy()
    else:
        raise RuntimeError("Policy iteration did not converge")
    full=np.r_[K,v,right]
    gaps=full-np.maximum(K-s,0)
    # Restrict contact classification to S<K: zero far-field data is not exercise.
    eligible=(s<K)&(gaps<=contact_tol)
    k=0
    while k+1<len(s) and eligible[k+1]: k+=1
    contiguous=not np.any(eligible[k+1:])
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
        contiguous=bool(contiguous),min_above_payoff=float(gaps.min()),
        max_above_K=float(np.max(full-K)),max_first_difference=float(np.max(np.diff(full))),
        min_second_difference=float(np.min(np.diff(full,n=2))),
        min_diagonal_margin=float(np.min(diag-np.abs(lo)-np.abs(up))),
        max_offdiagonal=float(max(lo.max(),up.max())),
        smooth_fit_defect=float(abs((full[k+2]-full[k+1])/h+1)))
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
