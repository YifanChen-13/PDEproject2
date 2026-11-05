"""B: independent dense active-set oracle and solver failure checks."""
from itertools import product
import numpy as np
import pytest
import solver
from discretization import assemble
from problem import K, payoff

def enumerate_lcp(smax, h, stage, exact_boundary):
    # Build a dense matrix and try every policy, independently of band storage.
    s, lo, d, up, f, right = assemble(smax,h,stage,exact_boundary)
    A=np.diag(d)+np.diag(lo[1:],-1)+np.diag(up[:-1],1)
    psi=payoff(s[1:-1]); feasible=[]
    for bits in product([False,True],repeat=len(d)):
        active=np.array(bits); B=A.copy(); rhs=f.copy()
        B[active]=np.eye(len(d))[active]; rhs[active]=psi[active]
        v=np.linalg.solve(B,rhs); a=A@v-f; gap=v-psi
        if min(a.min(),gap.min())>=-1e-9 and np.max(abs(np.minimum(a,gap)))<1e-9:
            feasible.append(v)
    assert feasible
    for v in feasible: np.testing.assert_allclose(v,feasible[0],atol=1e-9)
    return s,feasible[0],right

@pytest.mark.parametrize('stage,exact_boundary',[(1,False),(1,True),(2,False)])
@pytest.mark.parametrize('h',[100.,50.,25.])
def test_exhaustive_active_sets_and_reconstruction(stage,exact_boundary,h):
    s,v,right=enumerate_lcp(200.,h,stage,exact_boundary)
    S,V,st=solver.solve(200.,h,stage,exact_boundary=exact_boundary,tol=1e-10)
    np.testing.assert_array_equal(S,s)
    np.testing.assert_allclose(V[1:-1],v,atol=1e-9)
    assert V[0]==K and V[-1]==right
    assert st['met_requested_tol'] and st['lcp_residual']<=st['requested_tol']
    assert st['min_a']>=-1e-9 and st['min_gap']>=-1e-9

def test_threshold_contiguous_prefix_and_artificial_endpoint():
    s=np.array([0.,25.,50.,75.,100.,125.])
    V=payoff(s)+[0,0,0,1,2,0]
    assert solver.contact_threshold(s,V)==(2,True)
    V[2]+=1; V[3]=payoff(s)[3]
    assert solver.contact_threshold(s,V)==(1,False)

def test_contact_tolerance_sensitivity():
    s=np.array([0.,50.,100.,150.]); V=payoff(s)+[0,1e-6,1,0]
    assert solver.contact_threshold(s,V,1e-7)[0]==0
    assert solver.contact_threshold(s,V,1e-5)[0]==1

@pytest.mark.parametrize('kwargs',[{'tol':0},{'tol':np.nan},{'tol':-1},{'maxiter':0},{'maxiter':True},{'maxiter':1.5},{'contact_tol':-1},{'contact_tol':np.inf}])
def test_invalid_controls(kwargs):
    with pytest.raises(ValueError): solver.solve(**kwargs)

def test_iteration_budget_failure():
    with pytest.raises(RuntimeError,match='maxiter=1'):
        solver.solve(400.,1.,1,maxiter=1,tol=1e-30,exact_boundary=True)

def test_nonfinite_linear_solve_fails(monkeypatch):
    monkeypatch.setattr(solver,'solve_banded',lambda bands,ab,rhs,**kw: np.full_like(rhs,np.nan))
    with pytest.raises(RuntimeError,match='Non-finite'): solver.solve(200.,50.,1)

def test_repeated_large_defect_fails(monkeypatch):
    monkeypatch.setattr(solver,'solve_banded',lambda bands,ab,rhs,**kw: np.zeros_like(rhs))
    with pytest.raises(RuntimeError,match='Repeated policy'): solver.solve(200.,50.,1)

def test_floating_point_floor_is_not_convergence():
    _,_,st=solver.solve(400.,1.,1,tol=1e-30,exact_boundary=True)
    assert st['termination_reason']=='floating_point_floor'
    assert not st['met_requested_tol'] and st['floating_point_floor']
    assert st['requested_tol']<st['lcp_residual']<=st['residual_floor_estimate']

@pytest.mark.parametrize('stage',[1,2])
def test_representative_solve_recomputed_residual(stage):
    s,V,st=solver.solve(400.,1.,stage,exact_boundary=(stage==1))
    _,lo,d,up,f,_=assemble(400.,1.,stage,stage==1)
    A=np.diag(d)+np.diag(lo[1:],-1)+np.diag(up[:-1],1)
    a=A@V[1:-1]-f; gap=V[1:-1]-payoff(s[1:-1])
    assert np.max(abs(np.minimum(a,gap)))<1e-8
    assert st['contiguous'] and st['star']<K and st['star_upper']-st['star']==1
    assert np.min(V-payoff(s))>=-1e-9
    assert np.max(V)<=K+1e-9 and np.max(np.diff(V))<1e-9
