# Perpetual American Put: Obstacle and Free-Boundary BVP

[English](#english) | [中文](#中文)

## English

We study the value and exercise threshold of a perpetual American put. The price stays above the exercise payoff, and the exercise region is recovered from the solution. The working directory for this topic is [`american_put_project/`](american_put_project/).

### Model and method

For $`\psi(S)=\max(K-S,0)`$, the operator and obstacle problem are

$$
\mathcal{L}V=\tfrac12\sigma(S)^2S^2V''+(r-q)SV'-rV,
\qquad\min\{-\mathcal{L}V,V-\psi\}=0.
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

Each member writes their own report section and commits through their own account. E reviews A and B; A checks B's matrix integration; C and D review each other's comparison grids and error calculations. Completion criteria and branches are in the [team plan](american_put_project/docs/team_plan.md).

### Current progress

**A's foundation is complete: 35 tests passed.** It includes scalar/array model data, safe endpoint handling, shared tridiagonal assembly, hand-calculated rows, matrix-sign checks and polynomial consistency tests. The environment, commands and results are in [A's handoff](american_put_project/docs/handoff_A.md).

An American-put solver prototype, experiment scripts and numerical records were already in this repository. A's change separates the foundation and preserves the existing solver interface. B–E still need to review and reproduce their assigned parts. The earlier output files do not establish completed student contributions; the group must also complete the official course worksheets and independent review.

### Installation and A's checks

Use Python 3.10 or later:

```bash
git clone https://github.com/YifanChen-13/PDEproject2.git
cd PDEproject2
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r american_put_project/requirements-dev.txt
cd american_put_project
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe inspect_assembly.py
```

macOS / Linux:

```bash
.venv/bin/python -m pip install -r american_put_project/requirements-dev.txt
cd american_put_project
../.venv/bin/python -m pytest -q
../.venv/bin/python inspect_assembly.py
```

The inspection script checks the model and matrix rows without solving an LCP. Row margins and consistency defects are assembly diagnostics. B–E will review and reproduce the full experiments in the existing `run_project.py` after auditing the solver.

### Files and handoff

| Path under `american_put_project/` | Contents |
|---|---|
| `problem.py`, `discretization.py` | A's model and operator |
| `tests/test_foundation.py`, `inspect_assembly.py` | A's tests and assembly inspection |
| `docs/` | Problem definition, team plan, predictions and handoff |
| `solver.py`, `run_project.py` | Existing solver prototype and experiment driver |
| `results/`, `figures/`, `protocols/` | Earlier numerical output and protocol records |
| `Report_Source.md`, `build_report.py` | Existing report text and generation script |

B starts with [A's handoff](american_put_project/docs/handoff_A.md), reviews policy iteration and adds independent small-grid LCP tests. C and D can prepare their studies in parallel. Former Poisson files remain in the repository-level `src/pde_bvp/`, `tests/` and `docs/`; the active code and progress for this topic are inside `american_put_project/`.

---

## 中文

研究永久美式看跌期权的价值与行权阈值。期权价格高于或等于立即行权收益，行权区域随数值解一起确定。本题的工作目录是 [`american_put_project/`](american_put_project/)。

### 模型与方法

令 $`\psi(S)=\max(K-S,0)`$，算子与障碍问题为

$$
\mathcal{L}V=\tfrac12\sigma(S)^2S^2V''+(r-q)SV'-rV,
\qquad\min\{-\mathcal{L}V,V-\psi\}=0.
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

每人撰写自己部分的报告，并用自己的账号提交。E 复核 A、B；A 检查 B 是否正确接入矩阵；C、D 互查比较网格和误差计算。完成标准与分支安排见[五人分工](american_put_project/docs/team_plan.md)。

### 当前进度

**A 的基础工作已完成，35 项测试通过。** 包含标量/数组模型数据、安全的端点处理、共用三对角装配、手算差分行、矩阵符号检查和多项式一致性测试。环境、命令与结果记录在 [A 的交接说明](american_put_project/docs/handoff_A.md)。

仓库原先已有一份 American put 求解器原型、实验脚本和数值记录。这次将基础模块独立出来，并保留已有求解器接口。B–E 继续复核和重跑自己部分的工作，已有输出不作为组员完成贡献的证明；小组还需完成课程官方表格与独立复核。

### 安装与 A 的检查

需要 Python 3.10 或更新版本：

```bash
git clone https://github.com/YifanChen-13/PDEproject2.git
cd PDEproject2
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pip install -r american_put_project/requirements-dev.txt
cd american_put_project
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe inspect_assembly.py
```

macOS / Linux：

```bash
.venv/bin/python -m pip install -r american_put_project/requirements-dev.txt
cd american_put_project
../.venv/bin/python -m pytest -q
../.venv/bin/python inspect_assembly.py
```

检查脚本检查模型与矩阵行，不进行 LCP 求解。行占优余量和一致性缺陷用于检查装配。已有 `run_project.py` 中的完整实验由 B–E 在求解器审计后复核和重跑。

### 文件与交接

| `american_put_project/` 内路径 | 内容 |
|---|---|
| `problem.py`、`discretization.py` | A 的模型与算子 |
| `tests/test_foundation.py`、`inspect_assembly.py` | A 的测试与装配检查 |
| `docs/` | 问题定义、五人分工、计算前预测和交接说明 |
| `solver.py`、`run_project.py` | 已有求解器原型和实验入口 |
| `results/`、`figures/`、`protocols/` | 先前的数值输出和过程记录 |
| `Report_Source.md`、`build_report.py` | 已有报告正文和生成脚本 |

B 从 [A 的交接说明](american_put_project/docs/handoff_A.md)开始，复核策略迭代并加入独立的小网格 LCP 测试。C、D 可同时准备实验。之前的 Poisson 文件保留在仓库根目录下的 `src/pde_bvp/`、`tests/` 和 `docs/`；本题代码与进度以 `american_put_project/` 为准。
