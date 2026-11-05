"""Recheck saved D arrays and tables without invoking the LCP solver."""
import csv
import json
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import trapezoid
from discretization import assemble


def verify(run):
    summary = json.loads((run/'summary_D.json').read_text())
    checks = 0
    def close(a, b):
        nonlocal checks
        np.testing.assert_allclose(a, b, rtol=1e-10, atol=1e-11)
        checks += 1

    def load(name):
        with np.load(run/(name+'.npz')) as z:
            return z['S'], z['V']

    rs, rv = load('reference_h0.0078125')
    fs, fv = load('reference_h0.00390625')
    close(rs, fs[::2])
    close(np.max(abs(rv-fv[::2])), summary['reference_change']['Linf'])
    points = []
    residuals = []
    for stats in summary['mesh'] + [summary['reference'], summary['finer_reference']]:
        s, v = load(stats['experiment'])
        close(s[1]-s[0], stats['h'])
        assert len(s) == stats['N']+1 and v[0] == 100 and v[-1] == 0
        checks += 1
        sample = rv[::round(stats['h']/(1/128))] if stats['h'] >= 1/128 else None
        if stats in summary['mesh']:
            close(s, rs[::round(stats['h']/(1/128))])
            error = v-sample
            close(np.max(abs(error)), stats['value_Linf'])
            # Independent integration API rather than the driver's manual weights.
            close(np.sqrt(trapezoid(error**2, s)), stats['value_L2'])
            for price in [100., 200.]:
                i = round(price/stats['h'])
                ir, iff = round(price/(1/128)), round(price/(1/256))
                points.append(dict(h=stats['h'], S=price, value=float(v[i]),
                    primary_reference=float(rv[ir]), finer_reference=float(fv[iff]),
                    abs_diff_primary=float(abs(v[i]-rv[ir])),
                    abs_diff_finer=float(abs(v[i]-fv[iff]))))
        # Re-evaluate the stored float64 matrix's residual in the widest local
        # NumPy float type; precision availability is reported, not assumed.
        _, lo, d, up, rhs, _ = assemble(stats['smax'],stats['h'],2,False)
        w = v[1:-1].astype(np.longdouble)
        a = d.astype(np.longdouble)*w-rhs.astype(np.longdouble)
        a[1:] += lo[1:].astype(np.longdouble)*w[:-1]
        a[:-1] += up[:-1].astype(np.longdouble)*w[1:]
        b = w-np.maximum(100-s[1:-1],0).astype(np.longdouble)
        rho = float(np.max(abs(np.minimum(a,b))))
        assert rho <= 2e-6
        checks += 1
        residuals.append(dict(experiment=stats['experiment'],
            reported_float64_residual=stats['lcp_residual'],
            recomputed_residual=rho, precision_epsilon=float(np.finfo(np.longdouble).eps)))

    base_s, base_v = load('mesh_h0.0625')
    for stats in summary['domain']:
        name = stats['experiment']
        s, v = load(name)
        for end in [200, 300]:
            n = round(end/.0625)+1
            close(s[:n],base_s[:n])
            close(np.max(abs(v[:n]-base_v[:n])),stats[f'Linf_0_{end}_vs_600'])
        close(v[1600],stats['V100'])
        close(v[3200],stats['V200'])
    with (run/'pointwise_mesh_comparison_D.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(points[0]), lineterminator='\n')
        writer.writeheader();writer.writerows(points)
    result=dict(checks=checks,status='passed',residual_rechecks=residuals,
                scope='Automated saved-array verification, not independent human/course audit.')
    (run/'verification_D.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    verify(Path(sys.argv[1]).resolve())
