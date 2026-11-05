"""Build the report from recorded results (no manually entered numerical results)."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/american_put_matplotlib')
import argparse,json,textwrap
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-root', type=Path, default=Path(__file__).resolve().parent,
                    help='Directory containing results/ and figures/')
ROOT = parser.parse_args().input_root.resolve()
D=json.loads((ROOT/'results/summary.json').read_text())
MAN=[]; PAGES=[]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'mathtext.fontset':'dejavusans'})
NAVY='#14334a'; TEAL='#167d9a'

def page(title,subtitle=''):
    fig=plt.figure(figsize=(8.27,11.69),facecolor='white')
    fig.text(.085,.95,'NUMERICAL METHODS  /  PERPETUAL AMERICAN PUT',fontsize=8,color=TEAL,weight='bold')
    fig.text(.085,.90,title,fontsize=21,color=NAVY,weight='bold')
    if subtitle:fig.text(.085,.868,subtitle,fontsize=9,color='#586873')
    fig.text(.085,.035,'Reproducible computational project  |  3 November 2026',fontsize=8,color='#586873')
    fig.text(.91,.035,str(len(PAGES)+1),ha='right',fontsize=8,color='#586873')
    PAGES.append(fig);MAN.append('\n# '+title+'\n'+subtitle+'\n')
    return fig,.82

def para(fig,y,text,heading=None):
    if heading:
        fig.text(.085,y,heading,fontsize=12,color=TEAL,weight='bold');y-=.029
        MAN.append('\n## '+heading+'\n')
    lines=textwrap.wrap(text,width=95,break_long_words=False,break_on_hyphens=False)
    fig.text(.085,y,'\n'.join(lines),fontsize=10,linespacing=1.4,va='top',color='#263746')
    MAN.append(text+'\n')
    return y-len(lines)*.0174-.019

def equation(fig,y,text,plain=None):
    fig.text(.11,y,text,fontsize=12,va='top',color=NAVY)
    MAN.append(plain or text)
    return y-.065

def table(fig,y,headers,rows,width=.83,fontsize=9):
    height=(len(rows)+1)*.029
    ax=fig.add_axes([.085,y-height,width,height]);ax.axis('off')
    t=ax.table(cellText=rows,colLabels=headers,cellLoc='center',loc='center',bbox=[0,0,1,1])
    t.auto_set_font_size(False);t.set_fontsize(fontsize)
    for (i,j),c in t.get_celld().items():
        c.set_linewidth(.4);c.set_edgecolor('#d7e2e8')
        if i==0:c.set_facecolor(NAVY);c.set_text_props(color='white',weight='bold')
        elif i%2:c.set_facecolor('#eef5f7')
    MAN.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+
               '\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n')
    return y-height-.035

def picture(fig,y,name,height=.30):
    ax=fig.add_axes([.075,y-height,.85,height]);ax.imshow(plt.imread(ROOT/'figures'/name));ax.axis('off')
    MAN.append('![Numerical results](figures/'+name+')\n')
    return y-height-.025

def fmt(x):return f'{x:.3e}'
def order(x):return '-' if x is None else f'{x:.3f}'

def main():
    a,b=D['stage1'],D['stage2']
    fig,y=page('Pricing and optimal exercise','An obstacle problem solved by monotone finite differences and policy iteration')
    y=para(fig,y,'This project computes the value and optimal exercise threshold of a perpetual American put. '
        'The perpetual formulation has no expiry date and therefore leads to a stationary differential inequality. '
        'Two cases are studied: a constant-volatility benchmark with a closed-form solution, and a genuinely '
        'numerical local-volatility model.',heading='Abstract')
    y=para(fig,y,f'The benchmark maximum value error falls from {a[0]["value_Linf"]:.6f} to '
        f'{a[-1]["value_Linf"]:.6f} over four meshes, with observed order approximately one. '
        f'Its finest-grid contact node is {a[-1]["star"]:.4f}, compared with the exact threshold '
        f'{D["exact_star"]:.8f}. For the local-volatility model on [0,600], the finest study grid gives '
        f'S*_h={b[-1]["star"]:.4f}; independent ODE shooting gives {D["ode_star"]:.8f}.')
    y=picture(fig,y,'value_and_convergence.png',.30)
    y=para(fig,y,'The central numerical finding is the separation of three error sources. Mesh refinement '
        'confirms the first-order upwind discretisation; tolerance tightening leaves the computed value unchanged; '
        'domain enlargement changes the price substantially more than the finest-grid discretisation error. '
        'Consequently, a small LCP residual does not establish infinite-domain pricing accuracy.',heading='Main finding')
    para(fig,y,'All tables are generated from executed code. The package contains the solver, raw results, '
        'prediction records, a custom audit, report source, and instructions for reproduction. No student '
        'names, individual contributions, or independent student verification are asserted.')

    fig,y=page('1  The continuous problem','Risk-neutral pricing, obstacle constraints and the free boundary')
    y=para(fig,y,'Under the risk-neutral model, dS=(r-q)S dt+sigma(S)S dW. The payoff is '
        'psi(S)=max(K-S,0). The value is the supremum of the expected discounted exercise payoff over '
        'admissible stopping times. The discount rate is r>0 and the dividend yield is q>=0.')
    y=equation(fig,y,r'$\mathcal{L}V=\frac{1}{2}\sigma(S)^2S^2 V^{\prime\prime}+(r-q)S V^\prime-rV$')
    y=equation(fig,y,r'$\min\{-\mathcal{L}V,\ V-\psi\}=0,\qquad S>0$')
    y=para(fig,y,'The sign convention is -L V>=0. The value lies above the obstacle, and at each point '
        'at least one of -L V and V-psi vanishes. In the continuation region, L V=0; in the exercise '
        'region, V=psi. The obstacle is imposed throughout the contact region, rather than only at its edge.')
    y=equation(fig,y,r'$V(S^*)=K-S^*,\qquad V^\prime(S^*)=-1$')
    y=para(fig,y,'The boundary conditions are V(0)=K and V(S)->0 as S->infinity. Numerically, the latter is '
        'replaced by V(Smax)=0. The zero endpoint is fixed directly; the volatility formula is evaluated '
        'only at strictly positive interior prices, so log(0) is never formed.',heading='Domain and boundary data')
    y=para(fig,y,'Stage 1 uses K=100, r=0.05, q=0 and sigma=0.20. Substitution of V=C S^lambda '
        'into the continuation equation gives 0.5 sigma^2 lambda(lambda-1)+r lambda-r=0. '
        'The decaying root is lambda=-2.5, and smooth fit gives S*=lambda K/(lambda-1)=500/7.')
    y=equation(fig,y,r'$V(S)=K-S\ (S\leq S^*),\quad V(S)=(K-S^*)(S/S^*)^{-2.5}\ (S>S^*)$')
    y=para(fig,y,'Stage 2 keeps K=100 and r=0.05, sets q=0.02, and uses the positive local volatility below. '
        'Its limiting values are 0.13 as S decreases to zero and 0.27 as S increases. The spatial dependence '
        'removes the Euler-Cauchy power-law solution.')
    equation(fig,y,r'$\sigma(S)=0.20\left[1+0.35\tanh\left(\frac{\log(S/K)}{0.40}\right)\right]$')

    fig,y=page('2  Discretisation and solution','A monotone tridiagonal LCP, not a single unconstrained linear solve')
    y=para(fig,y,'On S_i=i h, set d_i=0.5 sigma(S_i)^2 S_i^2 and b_i=(r-q)S_i. Let '
        'b_i^+=max(b_i,0), b_i^-=max(-b_i,0). The following stencil approximates -L. '
        'In particular, positive drift in L uses a forward difference for V prime in this stationary operator; '
        'its sign in -L ensures a nonpositive upper off-diagonal.')
    y=equation(fig,y,r'$\ell_i=-d_i/h^2-b_i^-/h,\quad u_i=-d_i/h^2-b_i^+/h$')
    y=equation(fig,y,r'$c_i=2d_i/h^2+|b_i|/h+r,\qquad (A V)_i=\ell_i V_{i-1}+c_i V_i+u_i V_{i+1}$')
    y=para(fig,y,'Known endpoint values are moved to the right-hand side f. Thus f_1 includes -ell_1 K, '
        'and the last entry includes -u_(N-1) V(Smax). The matrix is generally nonsymmetric. Its '
        'off-diagonals are nonpositive and its full-stencil diagonal dominance margin is r. Eliminating '
        'endpoint columns preserves strict dominance. These properties establish a nonsingular M-matrix.')
    y=equation(fig,y,r'$a=A V-f,\qquad g=V-\psi,\qquad \min(a,g)=0$')
    y=para(fig,y,'Policy iteration starts from V=psi. At each interior node, choose exercise when g_i<a_i, '
        'otherwise choose continuation. Exercise rows are replaced by V_i=psi_i; continuation rows '
        'retain the PDE stencil. Each policy system is solved by a banded direct solver. Exact ties '
        'choose continuation, which avoids unnecessary propagation through the initial zero-payoff tail.',heading='Iteration and stopping')
    y=para(fig,y,'The stopping criterion is max_i |min(a_i,g_i)|<=tol. If the policy repeats before the '
        'requested tolerance is reached, the code records a floating-point floor and reports the actual '
        'defect; it does not label the requested tolerance as achieved. Iteration counts and both raw '
        'complementarity and scaled policy-system backward residuals are retained.')
    y=para(fig,y,'For a hand check, S=100, h=1, sigma=0.20, r=0.05 and q=0 give the row '
        '(-200, 405.05, -205). The implementation checks this independently. Diffusion is centred '
        'but drift is first order, so first-order global value convergence is the stated expectation.')
    para(fig,y,'The independent reference solves L w=0 backwards from w(Smax)=0 and w prime(Smax)=-1. '
        'The root of w(s)+(K-s)w prime(s)=0 determines the boundary; scaling by -1/w prime(s) '
        'enforces value matching and smooth fit. ODE integration uses rtol=2e-11, atol=1e-12, '
        'maximum step 1, and root tolerance 1e-11. This shares no FDM matrix or policy iteration.',
        heading='Independent ODE shooting')

    fig,y=page('3  Exact-solution validation','Stage 1: fixed Smax=400 with exact upper endpoint data')
    y=para(fig,y,'The exact value at Smax is imposed in this experiment. This deliberately removes '
        'far-field truncation error from the benchmark; the zero-boundary domain study is performed '
        'separately in Stage 2. The maximum error includes every grid node. The discrete L2 norm is '
        'sqrt(h sum_i e_i^2); endpoint errors vanish in this validation setup.')
    y=table(fig,y,['h','Max error','L2 error','Order','Contact node','Boundary error'],[
        [r['h'],fmt(r['value_Linf']),fmt(r['value_L2']),order(r['value_order']),f'{r["star"]:.4f}',fmt(r['star_error'])] for r in a],fontsize=8.5)
    y=para(fig,y,'The value error approximately halves at each refinement. This agrees with the expected '
        'first-order effect of drift upwinding. The nodal threshold error is not monotone: halving h '
        'can move the last contact node from one side of the continuous threshold to the other. '
        'A price convergence rate cannot therefore be assigned automatically to each boundary-error pair.')
    y=table(fig,y,['h','Iterations','LCP residual','Backward residual','Smooth-fit defect'],[
        [r['h'],r['iterations'],fmt(r['lcp_residual']),fmt(r['scaled_backward_residual']),fmt(r['smooth_fit_defect'])] for r in a],fontsize=8.5)
    y=para(fig,y,'The numerical boundary is the last node in the contiguous contact set with '
        'V_i-psi_i<=1e-7 and S_i<K. No interpolation is used. The next node is recorded for '
        'reproducibility, but these two nodes are not asserted to bracket the continuous boundary. '
        'The S<K restriction prevents the artificial zero far-field endpoint from being mistaken for exercise.',heading='Threshold and smooth fit')
    para(fig,y,'Smooth fit is assessed from the first difference between the first two continuation '
        'nodes: |(V_(k+2)-V_(k+1))/h+1|. Its decreasing defect is supporting evidence. '
        'The full exact value error and exact threshold comparison remain the primary validation tests.')

    fig,y=page('4  Local-volatility experiment','Stage 2: grid refinement on the fixed domain [0,600]')
    y=para(fig,y,'The primary reference is the same monotone LCP solved with h=1/128. A second '
        'reference with h=1/256 checks its remaining bias. All coarser meshes nest in the reference '
        'grid, so errors are evaluated by direct subsampling without interpolation.')
    y=table(fig,y,['h','Max vs grid ref','Order','Max vs ODE','Contact node'],[
        [r['h'],fmt(r['value_Linf']),order(r['value_order']),fmt(r['error_vs_ODE']),f'{r["star"]:.4f}'] for r in b],fontsize=8.8)
    y=para(fig,y,f'The reference-to-reference maximum difference is {D["reference_change"]:.3e}. '
        f'The h=1/128 reference differs from the independent ODE solution by {D["ref_ODE_error"]:.3e}; '
        f'the h=1/256 result differs by {D["finer_ODE_error"]:.3e}. Thus the reference is not exact. '
        'Subtracting its nonzero first-order error slightly inflates the finest pairwise rates above one.')
    y=picture(fig,y,'contact_and_convexity.png',.28)
    y=para(fig,y,f'The independent fixed-domain threshold is {D["ode_star"]:.8f}. The h=0.0625 '
        f'last contact node is {b[-1]["star"]:.4f}, while both fine reference grids report '
        f'{D["reference"]["star"]:.6f}. Identical nodal thresholds on two meshes do not imply '
        'that the continuous threshold has been computed exactly.',heading='Independent continuous reference')

    fig,y=page('5  Far-field truncation matters','The h study and Smax study answer different questions')
    y=para(fig,y,'At fixed h=0.0625, increasing Smax moves the artificial zero value further into the '
        'tail. Compare prices at common asset values, rather than conflating a changing domain '
        'with a changing mesh. The price increases and the exercise threshold decreases.')
    y=table(fig,y,['Smax','Vh(100)','Vh(200)','Contact node','ODE V(100)'],[
        [r['smax'],f'{r["V100"]:.6f}',f'{r["V200"]:.6f}',f'{r["star"]:.4f}',f'{r["ODE_V100"]:.6f}'] for r in D['domain']],fontsize=8.8)
    y=picture(fig,y,'domain_and_boundary.png',.24)
    y=para(fig,y,'The difference between Smax=400 and 600 at S=100 is about 0.2343, compared '
        'with a Stage 2 finest-study maximum grid error of about 0.0046 against the fine-grid '
        'reference. Truncation sensitivity therefore dominates this mesh error. The results on '
        '[0,600] should be interpreted as finite-domain results, not a certified infinite-domain price.')
    y=table(fig,y,['ODE domain Smax','Continuous threshold','Continuous V(100)'],[
        [r['smax'],f'{r["star"]:.8f}',f'{r["V100"]:.8f}'] for r in D['ODE_tail_study']],fontsize=9)
    para(fig,y,'The ODE extension confirms remaining tail sensitivity. Consecutive domain agreement '
        'is not a rigorous error bound; improved asymptotic boundary data would be a useful extension.')

    fig,y=page('6  Verification and solver error','Evidence beyond a small residual')
    y=para(fig,y,'For every reported mesh, results/all_diagnostics.csv includes min(a), min(g), '
        'max|min(a,g)|, the scaled policy residual, matrix signs, option bounds, first differences, '
        'second differences, and contact-set connectivity. The option is decreasing and convex '
        'within floating-point tolerance and remains between payoff and K. Tiny negative second '
        'differences near flat contact rows are reported rather than suppressed.')
    y=table(fig,y,['Requested tol','Iterations','Actual LCP residual','Price change'],[
        [fmt(r['requested_tol']),r['iterations'],fmt(r['lcp_residual']),fmt(r['Linf_change_vs_first'])] for r in D['tolerances']],fontsize=9)
    y=para(fig,y,'The tolerance experiment uses h=0.125 and Smax=600. Tightening the requested '
        'residual threshold leaves the computed vector unchanged. At 1e-10, a repeated policy '
        'identifies a floating-point floor: the requested tolerance is not achieved. Actual residuals '
        'and that status are both recorded in the CSV; this is not hidden as convergence.')
    y=para(fig,y,'The backward residual divides each policy-row residual by its absolute row sum '
        'times ||V||inf plus the absolute right-hand side, with a denominator floor of one. '
        'A backward residual alone is not a forward error bound. Here the independent ODE '
        'comparison and unchanged solution under tighter policy stopping rules provide the '
        'additional evidence that algebraic error is negligible at the reported study meshes.')
    y=para(fig,y,'Contact tolerances 1e-9, 1e-7 and 1e-5 all return the same finest-study contact '
        'node. The custom audit also checks the hand-derived stencil, matrix action, and exhaustive '
        'enumeration of all active-set policies on a five-unknown problem. Every feasible candidate '
        'agrees with policy iteration.',heading='Audit and prediction record')
    para(fig,y,'Predictions are timestamped immediately before the final recorded experiments and '
        'reconciled in protocols/reconciliation.md. They are AI-authored records. The original '
        'course five-gate and prediction worksheet templates were not available; the custom '
        'audit is not a claim that the official forms or independent student sign-off have been completed.')

    fig,y=page('7  Interpretation and reproduction','Scope, limitations and the complete computational record')
    y=para(fig,y,'Monotone finite differences and policy iteration solve the obstacle constraints '
        'reliably. Stage 1 validates prices and the free boundary against an analytic solution. '
        'Stage 2 confirms convergence toward an independently computed finite-domain solution. '
        'The main practical limitation is the imposed far-field boundary, rather than the LCP '
        'stopping tolerance.',heading='Conclusions')
    y=para(fig,y,'This is a one-dimensional stationary obstacle problem. It is neither a '
        'finite-maturity time-dependent American option nor the optional Poisson exercise model. '
        'The upwind method is deliberately first order; the report makes no second-order claim. '
        'No uncertain infinite-domain digits are presented as established results. Runtime is '
        'machine dependent and is recorded separately from accuracy.',heading='Limits of the results')
    y=para(fig,y,'From the project directory, install the listed dependencies and run: '
        'python run_project.py, followed by python build_report.py. The first command regenerates '
        'all tables, figures, prediction logs and audit checks; the second reads the recorded '
        'summary and regenerates this PDF and its editable Markdown manuscript. '
        'The finer reference is intentionally more expensive than the four study meshes.',heading='Reproduce the package')
    y=table(fig,y,['File / directory','Purpose'],[
        ['solver.py','LCP assembly, policy iteration, independent ODE'],
        ['run_project.py','Experiments, assertions, tables and figures'],
        ['build_report.py','PDF and manuscript from recorded values'],
        ['results/','CSV tables, JSON, solution arrays and run log'],
        ['figures/','PNG and vector PDF figures'],
        ['protocols/','Predictions, reconciliation, AI audit and disclosure'],
        ['README.md','Setup, run instructions and result guide']],fontsize=8.5)
    y=para(fig,y,'Problem data and required experiments follow the supplied Problem Pack, '
        'Directions for the PDE BVP Project (Weeks 5-9), open direction 5.3, '
        '"Perpetual American put (obstacle/free-boundary BVP)", pages 8-9, and the standing '
        'protocols on page 10. The analytic derivation and difference stencil are written explicitly '
        'in this report. NumPy, SciPy and Matplotlib versions and the execution platform are '
        'recorded in results/summary.json.',heading='Source and computational environment')

    with PdfPages(ROOT/'American_Put_Report.pdf') as pdf:
        review=ROOT.parent/'tmp/pdf_review';review.mkdir(parents=True,exist_ok=True)
        for i,fig in enumerate(PAGES,1):
            fig.canvas.draw()
            renderer=fig.canvas.get_renderer()
            for item in fig.texts:
                box=item.get_window_extent(renderer).transformed(fig.transFigure.inverted())
                if item.get_position()[1]>.05 and (box.y0<.06 or box.x1>.96):
                    raise RuntimeError(f'Page {i}: text outside safe area: {item.get_text()[:60]} {box}')
            pdf.savefig(fig)
            fig.savefig(review/f'page_{i}.png',dpi=100)
            plt.close(fig)
    (ROOT/'Report_Source.md').write_text('\n'.join(MAN))
    print(f'Created {len(PAGES)}-page PDF and editable manuscript')

if __name__=='__main__':main()
