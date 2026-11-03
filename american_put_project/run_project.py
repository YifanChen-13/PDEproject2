"""Reproduce every numerical table/figure with Python + NumPy/SciPy/Matplotlib."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/american_put_matplotlib')
import csv, json, itertools, datetime, platform, sys
from pathlib import Path
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from solver import solve,assemble,action,exact,EXACT_STAR,continuous_reference

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'; FIG=ROOT/'figures'; LOG=ROOT/'protocols'
for p in (OUT,FIG,LOG): p.mkdir(exist_ok=True)
PRED=LOG/'prediction_log.jsonl'
PRED.write_text('')

def run(label,**kw):
    rec=dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        experiment=label,parameters=kw,prediction=(
        'Expect a monotone obstacle solution; first-order upwind value error; '
        'grid-quantised boundary; small complementarity defect subject to roundoff. '
        'For larger domains expect higher values and a lower exercise threshold.'))
    with PRED.open('a') as f:f.write(json.dumps(rec)+'\n')
    s,v,st=solve(**kw)
    st['experiment']=label
    print(label,kw,'star',st['star'],'res',st['lcp_residual'],'iter',st['iterations'],flush=True)
    return s,v,st

def csvout(name,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def ode_run(L,stage=2):
    with PRED.open('a') as f:
        f.write(json.dumps(dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            experiment='independent_ODE',smax=L,stage=stage,
            prediction='Expect the same fixed-domain limit as FDM, higher value and lower threshold as domain grows.'))+'\n')
    return continuous_reference(L,stage)

def gates():
    with PRED.open('a') as f:
        f.write(json.dumps(dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            experiment='independent_small_grid_active_set_enumeration',
            prediction='A unique feasible LCP value should match all feasible active-set candidates.'))+'\n')
    # Independent dense active-set enumeration on a genuinely small grid.
    s,lo,d,up,f,right=assemble(180,30,1,True)
    A=np.diag(d)+np.diag(up[:-1],1)+np.diag(lo[1:],-1)
    assert np.max(np.abs(A@np.ones(len(d))-action(lo,d,up,np.ones(len(d)))))<1e-12
    assert np.all(d>0) and np.all(lo<=0) and np.all(up<=0)
    assert np.min(d+lo+up)>.0499999
    # Hand row: S=100,h=1,sigma=.2,r=.05,q=0 -> (-200,405.05,-205).
    _,l,dd,u,_,_=assemble(200,1,1)
    assert np.allclose([l[99],dd[99],u[99]],[-200,405.05,-205],atol=1e-11)
    psi=np.maximum(100-s[1:-1],0);feasible=[]
    for bits in itertools.product([False,True],repeat=len(d)):
        mask=np.array(bits); B=A.copy();rhs=f.copy()
        B[mask]=np.eye(len(d))[mask];rhs[mask]=psi[mask]
        v=np.linalg.solve(B,rhs);a=A@v-f;gap=v-psi
        if a.min()>-1e-9 and gap.min()>-1e-9 and np.max(np.abs(np.minimum(a,gap)))<1e-8:
            feasible.append(v)
    sg,vg,st=run('gate_small_grid',smax=180,h=30,stage=1,exact_boundary=True)
    assert feasible and max(np.max(np.abs(v-vg[1:-1])) for v in feasible)<1e-9
    # Degenerate endpoint never evaluates log(0); exact solution matches C1 traces.
    delta=1e-4
    assert abs(float(exact(np.array([EXACT_STAR+delta]))[0])-(100-EXACT_STAR-delta))<1e-8
    return dict(gate1='PASS: signs, stencil, obstacle and endpoint treatment derived',
        gate2='PASS: independent hand row and dense matrix-action check',
        gate3='PASS: exhaustive small-grid active-set comparison',
        gate4='Pending: exact-solution refinement and independent ODE comparison',
        gate5='Pending: tolerance sensitivity, invariants and reproducibility',
        official_worksheet_available=False)

def main():
    audit=gates()
    stage1=[]; hs=[.5,.25,.125,.0625]
    for h in hs:
        s,v,st=run('stage1_exact_boundary',smax=400,h=h,stage=1,exact_boundary=True)
        err=v-exact(s)
        st.update(value_Linf=float(np.max(np.abs(err))),value_L2=float(np.sqrt(h*np.sum(err**2))),
                  star_error=abs(st['star']-EXACT_STAR))
        stage1.append(st)
        np.savez(OUT/f'stage1_h{h}.npz',S=s,V=v,exact=exact(s))
    for i,r in enumerate(stage1):
        r['value_order']=None if i==0 else float(np.log2(stage1[i-1]['value_Linf']/r['value_Linf']))
    ref_s,ref_v,ref=run('stage2_fine_grid_reference',smax=600,h=.0078125,stage=2,tol=2e-6)
    finer_s,finer_v,finer=run('stage2_reference_check',smax=600,h=.00390625,stage=2,tol=1e-5)
    reference_change=float(np.max(np.abs(ref_v-finer_v[::2])))
    ode_star,ode_value=ode_run(600,2)
    stage2=[]
    curves={}
    for h in hs:
        s,v,st=run('stage2_h_study',smax=600,h=h,stage=2)
        ref_sample=ref_v[::round(h/ref['h'])]
        st.update(value_Linf=float(np.max(np.abs(v-ref_sample))),
                  value_L2=float(np.sqrt(h*np.sum((v-ref_sample)**2))),
                  error_vs_ODE=float(np.max(np.abs(v-ode_value(s)))),
                  star_error_vs_ODE=abs(st['star']-ode_star))
        stage2.append(st);curves[h]=(s,v)
        np.savez(OUT/f'stage2_h{h}.npz',S=s,V=v,reference=ref_sample)
    for i,r in enumerate(stage2):
        r['value_order']=None if i==0 else float(np.log2(stage2[i-1]['value_Linf']/r['value_Linf']))
    domain=[];domain_curves=[]
    for L in [300,400,600]:
        s,v,st=run('stage2_domain_study',smax=L,h=.0625,stage=2)
        root,val=ode_run(L,2)
        st.update(V100=float(np.interp(100,s,v)),V200=float(np.interp(200,s,v)),
            ODE_star=root,ODE_V100=float(val(np.array([100.]))[0]),
            Linf_common_vs_600=float(np.max(np.abs(v[s<=300]-curves[.0625][1][curves[.0625][0]<=300]))))
        domain.append(st);domain_curves.append((s,v))
    tolerances=[];baseline=None
    for tol in [1e-4,1e-6,1e-8,1e-10]:
        s,v,st=run('tolerance_study',smax=600,h=.125,stage=2,tol=tol)
        if baseline is None:baseline=v.copy()
        st['Linf_change_vs_first']=float(np.max(np.abs(v-baseline)))
        tolerances.append(st)
    # Exercise classification sensitivity at the final study grid.
    ct=[]
    for tol in [1e-9,1e-7,1e-5]:
        s,v,st=run('contact_tolerance_study',smax=600,h=.0625,stage=2,contact_tol=tol)
        ct.append(st)
    allrows=stage1+stage2+domain+tolerances+ct+[ref,finer]
    assert all(r['contiguous'] and r['min_above_payoff']>-1e-6 and r['max_above_K']<1e-6 and
        r['max_first_difference']<1e-6 and r['min_second_difference']>-1e-6 for r in allrows)
    assert stage1[-1]['value_Linf']<stage1[0]['value_Linf']/5
    assert stage2[-1]['error_vs_ODE']<stage2[0]['error_vs_ODE']/5
    assert domain[0]['V100']<=domain[1]['V100']<=domain[2]['V100']
    audit['gate4']='PASS: four-level exact convergence and independent continuous ODE verification'
    audit['gate5']='PASS: physical inequalities, tolerance sweep, contact tolerance sweep, domain sensitivity'
    audit['scope']='Custom five-gate audit; not the unavailable official course worksheet or student sign-off.'
    (LOG/'ai_solver_audit.json').write_text(json.dumps(audit,indent=2))
    tail=[]
    for L in [600,1200,2400]:
        root,val=ode_run(L,2)
        tail.append(dict(smax=L,star=root,V100=float(val(np.array([100.]))[0])))
    csvout('ODE_domain_extension.csv',tail)
    csvout('stage1_convergence.csv',stage1);csvout('stage2_convergence.csv',stage2)
    csvout('domain_sensitivity.csv',domain);csvout('tolerance_sensitivity.csv',tolerances)
    csvout('contact_tolerance.csv',ct);csvout('all_diagnostics.csv',allrows)
    summary=dict(exact_star=EXACT_STAR,stage1=stage1,stage2=stage2,domain=domain,
        tolerances=tolerances,contact_tolerances=ct,reference=ref,finer_reference=finer,
        reference_change=reference_change,ode_star=ode_star,
        ref_ODE_error=float(np.max(np.abs(ref_v-ode_value(ref_s)))),
        finer_ODE_error=float(np.max(np.abs(finer_v-ode_value(finer_s)))),
        ODE_tail_study=tail,audit=audit,environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
        matplotlib=matplotlib.__version__,platform=platform.platform()))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(name):
        plt.tight_layout();plt.savefig(FIG/(name+'.png'),dpi=180);plt.savefig(FIG/(name+'.pdf'));plt.close()
    fig,ax=plt.subplots(1,2,figsize=(10,3.7))
    s,v=curves[.0625];mask=s<=250
    ax[0].plot(s[mask],np.maximum(100-s[mask],0),'--',label='Exercise payoff')
    ax[0].plot(s[mask],v[mask],label='Stage 2 value')
    ax[0].axvline(stage2[-1]['star'],color='gray',ls=':',label='Last contact node')
    ax[0].set(xlabel='Asset price S',ylabel='Option value');ax[0].legend()
    for r in stage1:ax[1].plot(r['h'],r['value_Linf'],'o',color='#167d9a')
    ax[1].loglog(hs,[r['value_Linf'] for r in stage1],'-',label='Stage 1 vs exact')
    ax[1].loglog(hs,[r['value_Linf'] for r in stage2],'s-',label='Stage 2 vs fine grid')
    ax[1].set(xlabel='Grid spacing h',ylabel='Maximum value error');ax[1].legend();save('value_and_convergence')
    fig,ax=plt.subplots(1,2,figsize=(10,3.7))
    for (s,v),L in zip(domain_curves,[300,400,600]):
        mask=s<=300;ax[0].plot(s[mask],v[mask],label=f'Smax={L}')
    ax[0].set(xlabel='Asset price S',ylabel='Option value');ax[0].legend()
    ax[1].plot(hs,[r['star'] for r in stage2],'o-',label='Last contact node')
    ax[1].axhline(ode_star,color='gray',ls='--',label='ODE threshold, Smax=600')
    ax[1].set(xlabel='Grid spacing h',ylabel='Exercise threshold');ax[1].legend();save('domain_and_boundary')
    fig,ax=plt.subplots(1,2,figsize=(10,3.7))
    for h in [.5,.125,.0625]:
        s,v=curves[h];mask=(s>60)&(s<110)
        ax[0].plot(s[mask],(v-np.maximum(100-s,0))[mask],label=f'h={h}')
    ax[0].set(xlabel='Asset price S',ylabel='Value minus payoff');ax[0].legend()
    s,v=curves[.0625]; mask=(s[1:-1]>80)&(s[1:-1]<250)
    ax[1].plot(s[1:-1][mask],(np.diff(v,n=2)/.0625**2)[mask])
    ax[1].set(xlabel='Asset price S',ylabel='Discrete gamma');save('contact_and_convexity')
    print(json.dumps({k:summary[k] for k in ['ode_star','reference_change','ref_ODE_error','finer_ODE_error']},indent=2))

if __name__=='__main__':main()
