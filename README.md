# Perpetual American Put: Obstacle and Free-Boundary BVP

[English](#english) | [中文](#中文) | [Report PDF](american_put_project/report/main.pdf) | [Slides PDF](american_put_project/slides/main.pdf)

## English

We study the value and exercise threshold of a perpetual American put. The price stays above the exercise payoff, and the exercise region is recovered from the solution. The working directory for this topic is [`american_put_project/`](american_put_project/).

### Model and method

For $`\psi(S)=\max(K-S,0)`$, the operator and obstacle problem are

$$
\mathcal{L}V=\tfrac12\sigma(S)^2S^2V''+(r-q)SV'-rV,
\qquad\min\bigl(-\mathcal{L}V,\,V-\psi\bigr)=0.
$$

We use `K=100` and `r=0.05`, with the two stages in the Problem Pack, Section 5.3:

| Stage | Parameters | Validation |
|---|---|---|
| 1: constant volatility | `q=0`, `sigma=0.20` | Exact value and exercise threshold $`S^*=500/7`$ |
| 2: local volatility | `q=0.02`, $`\sigma(S)=0.20[1+0.35\tanh(\log(S/100)/0.40)]`$ | Refined-grid reference and a separate domain study |

On `[0,Smax]`, the left endpoint is `V(0)=K`. Stage 1 uses the exact right endpoint in its main mesh-validation case. Stage 2 uses `V(Smax)=0`, comparing `Smax=300,400,600` at fixed spacing. Mesh refinement uses `h=0.5,0.25,0.125,0.0625`.

Monotone upwind finite differences give a tridiagonal M-matrix. After eliminating the endpoints, the LCP is `min(A*v-rhs,v-psi)=0`, with `A=-L_h`; policy iteration supplies the solver. The [problem definition](american_put_project/docs/problem_definition.md) records the model and stencil.

### Team responsibilities

| Member | Work | Deliverables |
|---|---|---|
| A | Model data, exact benchmark, grid, monotone operator and endpoint elimination | `problem.py`, `discretization.py`, foundation tests, problem definition and handoff |
| B | LCP policy iteration, stopping rule and exercise-threshold extraction | Reviewed `solver.py`, small-grid active-set checks and solver tests |
| C | Stage 1 exact validation and four-level refinement | Value/threshold error tables, plots, convergence analysis and report section |
| D | Stage 2 local-volatility and domain-truncation experiments | Refined-grid reference, separate mesh/domain studies, plots and report section |
| E | Independent verification and report integration | ODE comparison, complementarity/shape checks, tolerance studies and audit records |

The team plan assigns each member a report section and a record of their own work. E reviews A and B; A checks B's matrix integration; C and D review each other's comparison grids and error calculations. Completion criteria and branches are in the [team plan](american_put_project/docs/team_plan.md).

### Current progress

**A — Model and discretisation.** `problem.py` implements the payoff, both volatility models and the Stage 1 exact solution. `discretization.py` assembles the interior tridiagonal matrix and moves both Dirichlet endpoints to the right-hand side. The 35 foundation tests cover endpoint handling, hand-calculated rows, coefficient signs and polynomial consistency. [A's handoff](american_put_project/docs/handoff_A.md) · [Assembly inspection](american_put_project/inspect_assembly.py)

**B — LCP solver.** Policy iteration starts from the payoff, selects the exercise or continuation row at each interior node, and stops on the componentwise minimum residual. The solver records a separate status when a repeated policy reaches the floating-point floor above the requested tolerance. The exercise threshold is the last node in the contiguous contact block from zero, using a price-gap tolerance of `1e-7` and excluding the imposed far endpoint. The 25 solver tests include exhaustive active-set enumeration on tiny grids. [B's derivation](american_put_project/docs/derivation_B.md) · [Handoff](american_put_project/docs/handoff_B.md)

**C — Stage 1 validation.** Four grids on `[0,400]` use the exact right boundary so that the price errors measure discretisation. As `h` decreases from `0.5` to `0.0625`, the maximum nodal price error falls from `0.058473` to `0.007363`, with a fitted order of `0.996`. The finest contact node is `71.4375` against the exact `500/7`, and the threshold error is nonmonotone over the four grids. [Stage 1 script](american_put_project/stage1_validation.py) · [Results](american_put_project/stage1_validation_results.csv) · [Plot](american_put_project/stage1_value_comparison.png)

**D — Stage 2 mesh, domain and tolerance studies.** The four study grids at `Smax=600` are compared on coincident nodes with references at `h=1/128` and `1/256`. The finest study mesh differs from the primary reference by `0.004604` in maximum norm. The two references differ by at most `0.0003284` and both record a floating-point residual floor above `1e-8`. A separate study holds `h=0.0625` fixed and compares `Smax=300,400,600`. At `S=100`, the computed prices are `15.45604`, `15.83102` and `16.06528`, respectively. The `400→600` domain change is about 51 times the finest mesh-to-reference difference at that same asset price. The finest study vector is unchanged across the three tested stopping tolerances. [D's handoff](american_put_project/docs/handoff_D.md) · [Study report](american_put_project/docs/report_D.md) · [Saved run](american_put_project/stage2_D_runs/20261105T132543802032Z/)

**E — Independent checks and integration.** Shooting and adaptive collocation agree on the continuous Stage 2 solutions for all three truncated domains. On `[0,600]`, the continuous value at `S=100` is approximately `16.06008` and the threshold is `69.26448`. Policy iteration and projected SOR also agree within `4e-8` in maximum norm on the two matched comparison grids, with a common residual target of `1e-8`. Saved diagnostics cover complementarity, price bounds, monotonicity and convexity. The unified run, English LaTeX report and slide deck bring the studies together. [Independent results](american_put_project/results/independent_audit/) · [Technical audit](american_put_project/docs/technical_audit.md)

The integrated suite contains 64 tests, with 35 foundation, 25 solver and 4 Stage 2 comparison tests. A full Stage 2 rerun agreed with the 11 saved solution arrays within the stated tolerances, and the saved-array checker passed 50 checks. The remaining course work is the team’s own cross-review, individual reproduction, individual contribution statements and official pre-computation and five-gate audit records. [Team plan](american_put_project/docs/team_plan.md) · [AI transparency log](american_put_project/protocols/AI_Transparency_Log.md)

### Installation and reproduction

Use Python 3.10 or later. Run the commands from the root of this checkout.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r american_put_project/requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe american_put_project/inspect_assembly.py
.\.venv\Scripts\python.exe american_put_project/run_all.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r american_put_project/requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python american_put_project/inspect_assembly.py
.venv/bin/python american_put_project/run_all.py
```

The inspection script prints matrix-row and boundary checks. The full run takes several minutes and saves new data and figures under `american_put_project/reproduction_runs/<UTC timestamp>/`. It runs the separate Stage 1 and Stage 2 studies, verifies the Stage 2 arrays, and runs the independent checks and solver comparison. It also reproduces the earlier prototype’s figures and Matplotlib PDF. The current LaTeX report and slides use the saved evidence identified in their sources. To rebuild either PDF, run `tectonic main.tex` from its own `report/` or `slides/` directory. For individual commands and their output locations, see the [project guide](american_put_project/README.md).

### Files and handoff

| Path under `american_put_project/` | Contents |
|---|---|
| `problem.py`, `discretization.py`, `inspect_assembly.py` | Model, shared operator and assembly diagnostics |
| `solver.py`, `tests/` | Policy iteration, contact extraction and A/B/D tests |
| `stage1_validation.py`, `stage1_validation_results.csv`, `stage1_value_comparison.png` | Stage 1 standalone experiment and outputs |
| `stage2_studies.py`, `verify_stage2_D.py`, `build_stage2_docs.py` | Stage 2 runs, saved-array checks and D report builder |
| `stage2_D_runs/` | Saved mesh, reference, domain and tolerance results with arrays and figures |
| `independent_audit.py`, `results/independent_audit/` | Independent continuous comparison and matched PSOR experiment |
| `run_all.py`, `reproduction_runs/` | Unified reproduction entry point and local outputs |
| `report/`, `slides/` | Current English LaTeX sources and PDFs |
| `docs/`, `protocols/` | Derivations, predictions, handoffs and audit records |
| `run_project.py`, `build_report.py`, `Report_Source.md`, `results/`, `figures/` | Prototype experiment and report trail, including results reused by the current LaTeX report |
| `archive/` | Historical deliveries, instructions and checksums |

---

## 中文

研究永久美式看跌期权的价值与行权阈值。期权价格高于或等于立即行权收益，行权区域随数值解一起确定。本题的工作目录是 [`american_put_project/`](american_put_project/)。

### 模型与方法

令 $`\psi(S)=\max(K-S,0)`$，算子与障碍问题为

$$
\mathcal{L}V=\tfrac12\sigma(S)^2S^2V''+(r-q)SV'-rV,
\qquad\min\bigl(-\mathcal{L}V,\,V-\psi\bigr)=0.
$$

固定 `K=100`、`r=0.05`，按照题目包第 5.3 节分为两个阶段：

| 阶段 | 参数 | 验证方式 |
|---|---|---|
| 1：常波动率 | `q=0`、`sigma=0.20` | 对照精确价格和行权阈值 $`S^*=500/7`$ |
| 2：局部波动率 | `q=0.02`、$`\sigma(S)=0.20[1+0.35\tanh(\log(S/100)/0.40)]`$ | 细网格参考解，并单独研究计算域截断 |

在 `[0,Smax]` 上，左端条件为 `V(0)=K`。阶段 1 的主要网格验证采用精确右端值；阶段 2 使用 `V(Smax)=0`，在固定步长下比较 `Smax=300、400、600`。网格加密使用 `h=0.5、0.25、0.125、0.0625`。

单调迎风有限差分得到三对角 M 矩阵。消去两端已知值后，LCP 为 `min(A*v-rhs,v-psi)=0`，其中 `A=-L_h`，由策略迭代求解。模型和差分行见[问题定义](american_put_project/docs/problem_definition.md)。

### 小组分工

| 成员 | 工作 | 交付内容 |
|---|---|---|
| A | 模型数据、精确基准、网格、单调算子与端点消元 | `problem.py`、`discretization.py`、基础测试、问题定义和交接说明 |
| B | LCP 策略迭代、停止准则与行权阈值提取 | 经复核的 `solver.py`、小网格活动集核验和求解器测试 |
| C | 阶段 1 精确解验证与四级网格加密 | 价格/阈值误差表、图、收敛分析及报告章节 |
| D | 阶段 2 局部波动率与计算域截断实验 | 细网格参考解、分开的网格/计算域研究、图及报告章节 |
| E | 独立核验与报告整合 | ODE 对照、互补性和形状检查、容差研究及审计记录 |

按分工，每人负责自己部分的报告和实际工作记录。E 复核 A、B；A 检查 B 是否正确接入矩阵；C、D 互查比较网格和误差计算。完成标准与分支安排见[五人分工](american_put_project/docs/team_plan.md)。

### 当前进度

**A · 模型与离散。** `problem.py` 实现收益函数、两种波动率和阶段 1 解析解。`discretization.py` 装配内点三对角矩阵，并把两端 Dirichlet 已知值移到右端项。35 项基础测试覆盖端点处理、手算矩阵行、系数符号和多项式一致性。 [A 的交接说明](american_put_project/docs/handoff_A.md) · [装配检查脚本](american_put_project/inspect_assembly.py)

**B · 互补求解器。** 策略迭代从收益函数出发，逐节点选择行权行或继续持有行，以逐分量最小值构造互补残差。若策略重复且残差停在请求容差以上的浮点下限，程序单独记录这个状态。阈值取从零开始的连续接触区最后一个节点，价格差容差为 `1e-7`，排除人为指定的右端点。25 项求解器测试包含小网格活动集穷举核验。 [B 的推导](american_put_project/docs/derivation_B.md) · [交接说明](american_put_project/docs/handoff_B.md)

**C · 阶段 1 解析验证。** 在 `[0,400]` 的四级网格上使用精确右端值，单独测量离散误差。步长从 `0.5` 缩小到 `0.0625` 时，最大节点价格误差由 `0.058473` 降到 `0.007363`，整体拟合阶为 `0.996`。最细网格的接触节点为 `71.4375`，解析阈值为 `500/7`，四级阈值误差并非单调下降。 [阶段 1 脚本](american_put_project/stage1_validation.py) · [结果表](american_put_project/stage1_validation_results.csv) · [对比图](american_put_project/stage1_value_comparison.png)

**D · 阶段 2 网格、截断域与容差实验。** 固定 `Smax=600`，在重合节点上将四级研究网格与 `h=1/128` 和 `1/256` 的参考网格对比。最细研究网格相对第一套参考的最大差为 `0.004604`，两套参考之间的最大差为 `0.0003284`，两套参考均记录了高于 `1e-8` 的浮点残差下限。另固定 `h=0.0625`，比较 `Smax=300、400、600`，执行价处的数值价格分别为 `15.45604、15.83102、16.06528`。同样在 `S=100`，外边界从 400 移到 600 带来的价格变化，约为最细研究网格与参考差异的 51 倍。最细研究网格在三档停止容差下给出相同的数值解。 [D 的交接](american_put_project/docs/handoff_D.md) · [实验报告](american_put_project/docs/report_D.md) · [原始结果目录](american_put_project/stage2_D_runs/20261105T132543802032Z/)

**E · 独立核验与整合。** 射击法和自适应配点法对三个截断域上的连续解给出一致的结果。在 `[0,600]` 上，连续解的执行价处价格约为 `16.06008`，阈值约为 `69.26448`。策略迭代和投影 SOR 在两套匹配网格上使用同一 `1e-8` 残差目标，最大节点价格差低于 `4e-8`。保存的诊断包含互补性、价格上下界、单调性和凸性。统一运行入口、英文 LaTeX 报告和演示稿汇总了这些工作。 [独立核验数据](american_put_project/results/independent_audit/) · [技术审核](american_put_project/docs/technical_audit.md)

整合后共 64 项测试，包括 35 项基础测试、25 项求解器测试和 4 项阶段 2 比较测试。完整重跑阶段 2 后，11 份解数组在记录的误差容限内一致，50 项保存数组检查通过。组员仍需完成实际交叉复核、个人复现、个人贡献声明，以及课程要求的算前记录和五关审核。 [五人分工](american_put_project/docs/team_plan.md) · [AI 使用记录](american_put_project/protocols/AI_Transparency_Log.md)

### 安装与复现

使用 Python 3.10 或更新版本。以下命令都从当前仓库根目录执行。

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r american_put_project/requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe american_put_project/inspect_assembly.py
.\.venv\Scripts\python.exe american_put_project/run_all.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r american_put_project/requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python american_put_project/inspect_assembly.py
.venv/bin/python american_put_project/run_all.py
```

装配检查会打印矩阵行与边界数据核对结果。完整运行需要数分钟，在 `american_put_project/reproduction_runs/<UTC 时间戳>/` 保存新生成的数据和图。它会分别运行两个阶段、核对阶段 2 的数组、执行独立核验及求解器对比，并复现早期原型的图和 Matplotlib PDF。当前 LaTeX 报告和幻灯片引用源文件中注明的保存结果。若需重编 PDF，分别进入 `report/` 或 `slides/` 后运行 `tectonic main.tex`。分项命令及其输出位置见[项目操作说明](american_put_project/README.md)。

### 文件与交接

| `american_put_project/` 内路径 | 内容 |
|---|---|
| `problem.py`、`discretization.py`、`inspect_assembly.py` | 模型、共用算子和装配诊断 |
| `solver.py`、`tests/` | 策略迭代、阈值提取及 A/B/D 测试 |
| `stage1_validation.py`、`stage1_validation_results.csv`、`stage1_value_comparison.png` | 阶段 1 独立脚本、结果表及图 |
| `stage2_studies.py`、`verify_stage2_D.py`、`build_stage2_docs.py` | 阶段 2 实验、保存数组核验与 D 报告生成 |
| `stage2_D_runs/` | 保存的网格、参考、截断域及容差数据、数组和图 |
| `independent_audit.py`、`results/independent_audit/` | 连续解交叉核验与匹配 PSOR 实验 |
| `run_all.py`、`reproduction_runs/` | 统一复现入口及本地新运行产物 |
| `report/`、`slides/` | 当前英文 LaTeX 源文件和 PDF |
| `docs/`、`protocols/` | 推导、预测、交接与审核记录 |
| `run_project.py`、`build_report.py`、`Report_Source.md`、`results/`、`figures/` | 原型实验与报告记录，含当前 LaTeX 报告引用的结果 |
| `archive/` | 历史交付包、说明及校验和 |
