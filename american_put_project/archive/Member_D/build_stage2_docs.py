"""Build D's measured report from one completed run; does not rerun the solver."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |',
                       '| '+' | '.join(['---']*len(headers))+' |']
                      + ['| '+' | '.join(map(str, row))+' |' for row in rows])


def build(run):
    j = json.loads((run/'summary_D.json').read_text())
    mesh, domain = j['mesh'], j['domain']
    ref, fine = j['reference'], j['finer_reference']
    delta = j['reference_change']['Linf']
    mesh_table = table(['h', 'Unknowns', 'Maximum difference', 'L2 difference',
                        'Observed order', 'Last contact node'],
        [[f"{r['h']:g}", r['N']-1, f"{r['value_Linf']:.8f}",
          f"{r['value_L2']:.8f}", '—' if r['value_order'] is None else f"{r['value_order']:.4f}",
          f"{r['star']:.6f}"] for r in mesh])
    costs = table(['h', 'Iterations', 'Solve seconds', 'min a', 'min b', 'LCP residual', 'Met 1e-8?'],
        [[f"{r['h']:g}", r['iterations'], f"{r['seconds']:.4f}",
          f"{r['min_a']:.3e}", f"{r['min_gap']:.3e}", f"{r['lcp_residual']:.3e}",
          'yes' if r['met_requested_tol'] else 'no (floor)'] for r in mesh+[ref,fine]])
    domain_table = table(['Smax', 'V(100)', 'V(200)', 'Contact node', 'Max difference [0,200]', 'Max difference [0,300]'],
        [[f"{r['smax']:g}", f"{r['V100']:.8f}", f"{r['V200']:.8f}", f"{r['star']:.6f}",
          f"{r['Linf_0_200_vs_600']:.8f}", f"{r['Linf_0_300_vs_600']:.8f}"] for r in domain])
    diagnostics = table(['Smax', 'Iterations', 'Seconds', 'min a', 'min b', 'Residual', 'Contact transition'],
        [[f"{r['smax']:g}",r['iterations'],f"{r['seconds']:.4f}",f"{r['min_a']:.3e}",
          f"{r['min_gap']:.3e}",f"{r['lcp_residual']:.3e}",
          f"[{r['star']:g}, {r['star_upper']:g}]"] for r in domain])
    figures = '../'+str(run.relative_to(ROOT))+'/figures/'
    report = r'''# Stage 2: local volatility and domain truncation

Status: AI-assisted draft based on executed experiments, 5 November 2026.
Independent C/E review and the course's official worksheets/audit are pending.

## Model and experiment design

We consider the perpetual American put with $K=100$, $r=0.05$, $q=0.02$ and

$$\sigma(S)=0.20\left[1+0.35\tanh\left(\frac{\log(S/100)}{0.40}\right)\right].$$

The global obstacle problem is $\min(-\mathcal LV,V-\psi)=0$, where
$\psi=(100-S)^+$ and
$\mathcal LV=\tfrac12\sigma(S)^2S^2V''+0.03SV'-0.05V$.
All experiments impose $V(0)=100$ and $V(S_{\max})=0$. No Stage 1 analytic
right boundary or closed-form value is used in Stage 2. A's monotone upwind
assembly and B's payoff-initialised policy iteration are used unchanged.
Ties select continuation. Policy iteration has no relaxation parameter.
The actual componentwise LCP residual is
$\rho=\|\min(a,b)\|_\infty$, with $a=Av-f$, $b=v-\psi$ after eliminating
the endpoints. The requested absolute tolerance is $10^{-8}$ unless stated.

To separate errors, the mesh study fixes $S_{\max}=600$ and uses
$h=0.5,0.25,0.125,0.0625$. The domain study fixes $h=0.0625$ and varies
$S_{\max}=300,400,600$. Consequently the mesh table measures approach to
a fixed truncated-domain problem, while the domain table measures sensitivity
to the artificial boundary at a fixed mesh spacing.

## Norms and exercise threshold

All comparisons use coincident nodes, selected by integer grid indices and
checked for equality. No interpolation or extrapolation is used. For error
$e_i$ on $[0,L]$, we report

$$E_\infty=\max_i|e_i|,\qquad
E_2=\left[h\left(\tfrac12 e_0^2+\sum_{i=1}^{N-1}e_i^2+
\tfrac12 e_N^2\right)\right]^{1/2}.$$

The second quantity approximates an integral L2 norm and is not RMS.
The observed order is $p=\log_2(E_h/E_{h/2})$ using the same reference.
The threshold is the last node in the contact interval connected to zero,
with $|V_i-\psi_i|\le10^{-7}$ and $S_i<K$. The artificial far endpoint
is excluded. No subgrid interpolation is applied. The next grid node is
reported as `star_upper`; this nodal transition interval is not a certified
enclosure of the continuous free boundary.

## Fixed-domain mesh refinement

The primary reference uses $h_r=1/128=0.0078125$ on $[0,600]$. The following
errors are differences to that reference sampled at the study nodes, rather
than errors to an exact Stage 2 solution.

{{MESH}}

The maximum difference decreases from 0.04121838 to 0.00460369. The measured
orders 1.0121, 1.0493 and 1.1010 support approximately first-order convergence,
consistent with upwind drift differencing. The mild rise above one is partly
a finite-reference effect. Using the finer $h=1/256$ reference instead gives
maximum differences 0.04154680, 0.02076502, 0.01020324 and 0.00493213,
with orders 1.0006, 1.0251 and 1.0487. These two comparisons support the same
qualitative convergence conclusion without treating either reference as exact.

The threshold remains 69.25 for the last three study levels. This plateau
is caused by nodal quantisation and does not demonstrate an exact threshold.
Both reference grids give 69.265625; the finest reference's next node is
69.26953125. On the finest study mesh the reference-node difference is
0.015625, and the nodal transition is [69.25,69.3125]. No threshold convergence
order is inferred from the plateau.

![Mesh convergence and contact-node threshold]({{FIG}}mesh_and_threshold_D.png)

## Reference sensitivity, algebraic diagnostics and cost

The reference is refined once more to $h_r/2=1/256=0.00390625$. Comparing
the two reference solutions on the coarser reference nodes gives

$$\|V_{1/128}-V_{1/256}\|_\infty=0.0003284326202,\qquad
\|V_{1/128}-V_{1/256}\|_{2,h}=0.003422319842.$$

The maximum change is about 7.13% of the finest study-grid difference to the
primary reference. Reference uncertainty is therefore smaller than the study
error, but not negligible at the finest level. This two-grid difference is an
empirical sensitivity, not a rigorous error bound. Under an assumed first-order
asymptotic expansion, it estimates the finer reference's leading error and
twice it estimates the primary reference's leading error; that assumption has
not been independently established for these two grids alone.

{{COST}}

Here N counts mesh intervals; interior unknowns number N-1. Timings are single
solver-call measurements, excluding compression and plotting. Tridiagonal
storage is linear in N, while total work also depends on policy iterations.
The finest reference takes approximately four times as long as the primary
reference, because both the number of unknowns and the iterations roughly double.

Every study-grid solve meets the requested $10^{-8}$ tolerance. The reference
solves terminate at B's floating-point-floor condition, with actual residuals
approximately $2.98\times10^{-8}$ and $1.19\times10^{-7}$. They do not meet
the requested tolerance. Their scaled policy-system backward residuals are
approximately $1.79\times10^{-11}$ and $1.44\times10^{-10}$; these are
reported separately and are not forward solution errors.

On the finest study grid, requesting $10^{-6}$, $10^{-8}$ and $10^{-10}$
produces identical stored values (maximum difference zero). The strictest call
takes one additional iteration and stops at the floor with residual
$9.56\times10^{-10}$. Repeating the finest reference with tolerance
$10^{-10}$ also produces identical stored values and the same floor residual.
These checks show tolerance insensitivity at this precision. They do not
exclude systematic round-off error shared by both calls or certify a forward
error bound.

All runs have one contiguous contact interval, nonincreasing nodal values and
values no greater than K. The most negative payoff gap and raw second difference
across all runs are about $-2.34\times10^{-9}$, consistent with small floating-
point violations. Convexity is checked using the sign of raw second differences,
with allowance $10^{-6}$; it is not a claim that the divided second derivative
has the same tolerance. The CSV files retain all raw shape diagnostics.

## Fixed-mesh domain-truncation study

At fixed $h=0.0625$, we compare each domain with the $S_{\max}=600$ solution
on the identical nodes of [0,300]. We additionally compare on [0,200], away
from the artificial endpoint at 300. The larger-domain solution is a baseline,
not an exact infinite-domain answer.

{{DOMAIN}}

{{DOMAIN_DIAGNOSTICS}}

Increasing the domain raises continuation values and lowers the contact
threshold. At S=100, increasing Smax from 300 to 600 raises the value by
0.60923847; increasing it from 400 to 600 still raises it by 0.23426500.
The contact node shifts downward by 0.4375 and 0.1875 respectively relative
to those smaller domains. The maximum difference on [0,300] is 3.73960665
for Smax=300 and 1.43361124 for Smax=400. The former includes the forced zero
value at S=300; even on [0,200] the differences remain 2.13966887 and
0.82046949, so the sensitivity is not confined to the endpoint.

The price differences between domains substantially exceed the fixed-domain
mesh/reference differences, including at S=100 (see the pointwise CSV values).
The small positive signed differences, below $10^{-9}$, occur only at the
round-off scale in contact values. The numerical pattern agrees with the
prediction that a closer zero boundary depresses continuation values and
favours earlier exercise. This follows from the truncated obstacle problem;
the comparison does not establish that Smax=600 is sufficiently large for an
infinite-domain accuracy target. Further domain extension or an independently
validated asymptotic boundary treatment would be needed for that claim.

![Domain sensitivity at fixed mesh spacing]({{FIG}}domain_truncation_D.png)

## Reproducibility and interpretation

Run `python stage2_studies.py` from the project directory. It creates a new
timestamped directory and preserves previous results. Output includes full
solution arrays, comparison tables, raw diagnostics, PNG/PDF figures, source
checksums, environment versions and pre-solve predictions followed by outcomes.
The executed source baseline is main commit
`489f549136502ff37e57a71cf2c73292f007ace3`. The environment was Python 3.12.7,
NumPy 1.26.4, SciPy 1.13.1 and Matplotlib 3.9.2. The existing 60 checks plus
four D comparison/norm checks pass (64 total).

The evidence supports approximately first-order fixed-domain value convergence,
quantised contact-node estimates and substantial domain sensitivity over the
tested truncations. Mesh difference, reference sensitivity, algebraic residual
and domain sensitivity are reported separately. Independent C/E review and the
official course protocol records remain pending; no human audit or sign-off is
asserted by these automated results.
'''
    for key, value in {'{{MESH}}':mesh_table,'{{COST}}':costs,'{{DOMAIN}}':domain_table,
                        '{{DOMAIN_DIAGNOSTICS}}':diagnostics,'{{FIG}}':figures}.items():
        report = report.replace(key,value)
    (ROOT/'docs/report_D.md').write_text(report)
    cn = '''# 成员 D：你负责的内容与本次结果

这份工作研究的是**永久美式看跌期权**，没有到期时间，不是带时间推进的有限期限 Black–Scholes PDE。
你的核心任务是验证第二阶段数值解，并研究远端边界放在哪里会怎样影响答案。A 负责模型与离散，B 负责 LCP 求解；你使用他们的模块进行实验，没有修改他们的求解算法。

## 1. 为什么需要两组分开的实验？

第一组固定计算域 [0,600]，只把网格步长从 0.5 减半到 0.0625。它回答：同一个截断问题，用更密的网格算，结果有没有稳定下来？

第二组固定步长 0.0625，只把计算域右端从 300 改成 400、600。它回答：强行令远端期权价值为零，会怎样影响内部价格？

必须一次只改变一个因素。网格越来越密，只能更准确地求解当前截断问题，不能自动消除右端放得太近所造成的误差。

## 2. 第二阶段没有精确解，怎么衡量误差？

在 [0,600] 上另外用 h=1/128 算一份细网格参考解，再用 h=1/256 检查它。四个实验网格的节点都与参考网格重合，代码直接取相应节点，没有插值。

最大误差就是所有比较节点上的价格差的绝对值取最大值。L2 使用梯形积分权重后开平方，不是把误差平方求平均再开方。英文报告写出了公式。

'''+mesh_table+'''

这里的“误差”准确地说是**与有限细网格参考解的差异**。三次观测阶约为 1.012、1.049、1.101，支持价格约一阶收敛。改用更细参考后，观测阶约为 1.001、1.025、1.049，更接近一阶。

两份参考解最大差约为 **0.00032843**，约占最细实验网格误差的 **7.13%**。所以参考解足够更精细，但不能当作完全没有误差的真值；两网格差也不是严格数学误差上界。

## 3. 为什么行权阈值好几行都是 69.25？

我们把从 S=0 开始连续接触 payoff 的最后一个网格点当作阈值，接触容差为 1e-7，不做插值。真实转折可能落在两个节点之间，所以几次加密仍可能报同一个节点。

例如最细实验网格给出接触节点 69.25，下一节点 69.3125；更细参考的接触节点是 69.265625，下一节点 69.26953125。这个节点区间只是数值接触转换位置，不能称作严格包住连续真阈值的证明。阈值暂时不变也不意味着已经精确收敛。

## 4. 计算域实验的结论是什么？

'''+domain_table+'''

表中所有价格都来自同一个步长 h=0.0625。随着远端变远，内部期权价格升高，行权阈值降低。V(100) 从约 15.456 增到 16.065；即便从 400 增到 600，仍变化约 0.2343。

在 [0,300] 比较时，Smax=300 的端点被强迫为零，可能放大最大差。因此额外给出 [0,200] 内部区间；差异仍然明显。说明边界的影响已经传到了内部，不能仅靠网格加密解决。

**不能写“600 已经代表无穷远、答案已精确”。** 本次只验证了在这些计算域之间结果仍有明显变化。若要宣称某个无限域精度，需要继续扩域或验证更好的远端条件。

## 5. 残差、求解容差与价格误差有什么区别？

残差衡量当前向量对离散 LCP 方程满足得怎样；价格误差衡量它离参考价格有多远；计算域差异衡量换远端位置有多大影响。它们是不同量。

四个实验网格都达到请求的 1e-8 残差容差。两个参考解因为浮点运算的抵消误差，分别停在约 2.98e-8、1.19e-7，没有达到请求容差，表里如实写了 floor 状态。

最细实验网格把容差设成 1e-6、1e-8、1e-10，输出价格完全相同；最细参考再收紧到 1e-10，输出价格也相同。说明继续收紧这个参数没有改变存储结果，但这不能证明共同存在的舍入误差为零。

## 6. 文件怎么使用？

- `stage2_studies.py`：只重跑 D 的实验；每次创建新的结果目录。
- `docs/report_D.md`：可整合进总报告的英文草稿，已有公式、表、结论和局限。
- `docs/handoff_D.md`：给 C/E 的交接和核验说明。
- `docs/precomputation_D.md`：计算前写下的预测。
- `stage2_D_runs/`：本次实际算出的 CSV、数组、图、环境与预测/结果记录。
- `tests/test_stage2_studies.py`：防止比较网格错位和 L2 权重算错的检查。

在 `american_put_project` 中运行 `python stage2_studies.py` 可重现实验；需要 requirements 中的 NumPy、SciPy、Matplotlib。运行 `python -m pytest -q -p no:cacheprovider` 可检查测试（本次 64 项通过）。新实验完成后，用 `python build_stage2_docs.py stage2_D_runs/对应目录名` 更新英文表格。该报告生成器的解释文字对应本次实验设计和数值量级，改变模型或设计后必须同步复核文字。

## 7. 交给组员前还需要的实际复核

本次是 AI 协助编写、运行与分析的草稿。C 还要核对比较网格、误差和观测阶；E 还要独立重跑一个代表案例并复核求解器。课程要求的正式计算前问答与 five-gate audit 表格及人工签字仍待完成，不能把自动测试或这份文档冒充这些步骤。已有仓库原始报告与旧结果没有被本次结果覆盖。
'''
    (ROOT/'docs/guide_D_CN.md').write_text(cn)


if __name__ == '__main__':
    build(Path(sys.argv[1]).resolve())
