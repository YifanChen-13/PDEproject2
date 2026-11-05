"""D's reproducible Stage 2 studies; never overwrites the prototype outputs.

Run from any directory: python /path/to/stage2_studies.py
Outputs: stage2_D_runs/<UTC timestamp>/ (a fresh directory on every invocation).
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/pde_d_mpl')
import csv
import datetime as dt
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from solver import solve
from problem import K

ROOT = Path(__file__).resolve().parent
BASELINE = '489f549136502ff37e57a71cf2c73292f007ace3'


def nested_sample(s, fine_s, fine_v):
    """Use coincident nodes only; reject offsets, non-nesting or extrapolation."""
    idx = np.rint(s / (fine_s[1] - fine_s[0])).astype(int)
    if idx[-1] >= len(fine_s) or not np.allclose(fine_s[idx], s, rtol=0, atol=1e-10):
        raise ValueError('Comparison grids must be nested and share origin zero')
    return fine_v[idx]


def norms(s, error):
    h = s[1] - s[0]
    # Trapezoidal integral, NOT RMS: endpoints carry half weight.
    return dict(Linf=float(np.max(np.abs(error))),
                L2=float(np.sqrt(h * (np.sum(error[1:-1]**2)
                                      + .5*(error[0]**2 + error[-1]**2)))))


def csvout(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output_root = Path(os.environ.get('PDE_STAGE2_OUTPUT_ROOT', ROOT / 'stage2_D_runs'))
    out = output_root.resolve() / stamp
    out.mkdir(parents=True, exist_ok=False)
    figdir = out / 'figures'
    figdir.mkdir()
    log = out / 'prediction_outcome_log.jsonl'
    allstats = []

    def append(data):
        with log.open('a') as f:
            f.write(json.dumps(dict(timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                                   **data), allow_nan=False) + '\n')

    def run(label, L, h, tol=1e-8):
        settings = dict(smax=L, h=h, stage=2, tol=tol,
                        exact_boundary=False, contact_tol=1e-7)
        append(dict(kind='prediction', label=label, settings=settings,
                    prediction='Expect decreasing convex obstacle values, contiguous contact, '
                    'mesh convergence, and larger-domain values weakly higher. Tight tolerances '
                    'may terminate at a floating-point floor; inspect actual residual. '
                    'See docs/precomputation_D.md for study-specific predictions.'))
        s, v, stats = solve(**settings)
        stats = dict(experiment=label, **stats)
        append(dict(kind='outcome', label=label, diagnostics=stats))
        np.savez_compressed(out / (label + '.npz'), S=s, V=v)
        allstats.append(stats)
        print(f'{label}: h={h:g}, L={L:g}, star={stats["star"]:g}, '
              f'residual={stats["lcp_residual"]:.3g}, '
              f'iterations={stats["iterations"]}, {stats["termination_reason"]}', flush=True)
        if not stats['contiguous']:
            raise RuntimeError('Noncontiguous contact set')
        # Check raw nodal differences, without presenting these as exact inequalities.
        if (stats['min_above_payoff'] < -1e-6 or stats['max_above_K'] > 1e-6
                or stats['max_first_difference'] > 1e-6
                or stats['min_second_difference'] < -1e-6):
            raise RuntimeError('Shape/invariant diagnostic exceeds tolerance 1e-6')
        return s, v, stats

    rs, rv, ref = run('reference_h0.0078125', 600., 1/128)
    fs, fv, fine = run('reference_h0.00390625', 600., 1/256)
    delta = norms(rs, rv - nested_sample(rs, fs, fv))
    # An extra tolerance experiment on the finest reference quantifies solver sensitivity.
    ts, tv, tightref = run('reference_tight_tol', 600., 1/256, 1e-10)
    reference_solver_change = norms(fs, fv-tv)

    mesh, curves = [], {}
    for h in [.5, .25, .125, .0625]:
        s, v, st = run(f'mesh_h{h}', 600., h)
        e = norms(s, v - nested_sample(s, rs, rv))
        ef = norms(s, v - nested_sample(s, fs, fv))
        mesh.append(dict(**st, value_Linf=e['Linf'], value_L2=e['L2'],
                         value_Linf_vs_finer=ef['Linf'], value_L2_vs_finer=ef['L2'],
                         threshold_difference_vs_ref=abs(st['star']-ref['star']),
                         threshold_difference_vs_finer=abs(st['star']-fine['star'])))
        curves[h] = s, v, st
    for i, row in enumerate(mesh):
        row['value_order'] = None if i == 0 else float(np.log2(mesh[i-1]['value_Linf']/row['value_Linf']))
        row['value_order_vs_finer'] = None if i == 0 else float(np.log2(mesh[i-1]['value_Linf_vs_finer']/row['value_Linf_vs_finer']))
        row['reference_change_fraction'] = delta['Linf'] / row['value_Linf']

    ds, dv, dst = curves[.0625]
    domain, domaincurves = [], {}
    for L in [300., 400., 600.]:
        # Reuse the EXACT same executed finest mesh solve at L=600.
        s, v, st = (ds, dv, dst) if L == 600 else run(f'domain_L{L:g}', L, .0625)
        row = dict(st, V100=float(v[round(100/.0625)]), V200=float(v[round(200/.0625)]),
                   threshold_shift_vs_600=st['star']-dst['star'],
                   reused_mesh_solve=(L == 600))
        for end in [200., 300.]:
            mask = s <= end
            diff = v[mask] - nested_sample(s[mask], ds, dv)
            metrics = norms(s[mask], diff)
            row.update({f'Linf_0_{end:g}_vs_600': metrics['Linf'],
                        f'L2_0_{end:g}_vs_600': metrics['L2'],
                        f'max_signed_difference_0_{end:g}': float(diff.max())})
        domain.append(row)
        domaincurves[L] = s, v

    tolerances = [dict(dst, Linf_change_vs_tol1e8=0.)]
    for tol in [1e-6, 1e-10]:
        s, v, st = run(f'tolerance_{tol:g}', 600., .0625, tol)
        tolerances.append(dict(st, Linf_change_vs_tol1e8=float(np.max(np.abs(v-dv)))))

    csvout(out/'mesh_convergence_D.csv', mesh)
    csvout(out/'domain_sensitivity_D.csv', domain)
    csvout(out/'reference_check_D.csv', [dict(ref, Linf_change_to_finer=delta['Linf'],
        L2_change_to_finer=delta['L2'], threshold_shift_to_finer=ref['star']-fine['star']), fine, tightref])
    csvout(out/'solver_tolerance_D.csv', tolerances)
    csvout(out/'all_diagnostics_D.csv', allstats)

    def save(name):
        plt.tight_layout()
        plt.savefig(figdir/(name+'.png'), dpi=180)
        plt.savefig(figdir/(name+'.pdf'))
        plt.close()

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].loglog([r['h'] for r in mesh], [r['value_Linf'] for r in mesh], 'o-', label='vs h=1/128')
    ax[0].loglog([r['h'] for r in mesh], [r['value_Linf_vs_finer'] for r in mesh], 's--', label='vs h=1/256')
    ax[0].axhline(delta['Linf'], color='gray', linestyle=':', label='Reference change')
    ax[0].set(xlabel='Mesh spacing h', ylabel='Maximum nodal value difference', title='Fixed domain [0,600]')
    ax[0].legend()
    ax[1].plot([r['h'] for r in mesh], [r['star'] for r in mesh], 'o-', label='Last contact node')
    ax[1].axhline(fine['star'], linestyle='--', label='h=1/256 contact node')
    ax[1].set(xlabel='Mesh spacing h', ylabel='Nodal exercise threshold', title='Grid quantisation')
    ax[1].legend()
    save('mesh_and_threshold_D')

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for L, (s, v) in domaincurves.items():
        mask = s <= 300
        ax[0].plot(s[mask], v[mask], label=f'Smax={L:g}')
        ax[1].plot(s[mask], v[mask]-nested_sample(s[mask], ds, dv), label=f'Smax={L:g}')
    ax[0].set(xlabel='Asset price S', ylabel='Option value', title='Fixed h=0.0625')
    ax[1].set(xlabel='Asset price S', ylabel='Value minus Smax=600 value', title='Common interval [0,300]')
    for a in ax:
        a.legend()
    save('domain_truncation_D')

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    mask = ds <= 250
    ax[0].plot(ds[mask], dv[mask], label='Stage 2 value')
    ax[0].plot(ds[mask], np.maximum(K-ds[mask], 0), '--', label='Payoff')
    ax[0].set(xlabel='Asset price S', ylabel='Value', title='Local volatility, Smax=600')
    for h, (s, v, st) in curves.items():
        mask = (s >= 68) & (s <= 73)
        ax[1].plot(s[mask], (v-np.maximum(K-s, 0))[mask], label=f'h={h:g}')
    ax[1].set(xlabel='Asset price S', ylabel='Value minus payoff', title='Contact-to-continuation transition')
    for a in ax:
        a.legend()
    save('value_and_contact_D')

    sources = ['problem.py', 'discretization.py', 'solver.py', 'stage2_studies.py',
               'docs/precomputation_D.md']
    summary = dict(source_baseline_commit=BASELINE, mesh=mesh, domain=domain,
        reference=ref, finer_reference=fine, reference_change=delta,
        finest_reference_solver_change=reference_solver_change,
        solver_tolerances=tolerances, common_intervals=[[0,200],[0,300]],
        reference_warning='Two-grid difference is an empirical sensitivity, not a certified error bound.',
        audit_status='AI-assisted execution only. Official worksheets and independent C/E review pending.',
        environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                         matplotlib=matplotlib.__version__, platform=platform.platform()),
        source_sha256={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources})
    (out/'summary_D.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print('OUTPUT_DIRECTORY='+str(out), flush=True)


if __name__ == '__main__':
    main()
