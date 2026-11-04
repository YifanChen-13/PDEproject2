# PDE Project 2: Mixed Boundary Data

[English](#english) | [中文](#中文)

## English

We solve the Poisson equation on the unit square using finite differences and compare two treatments of the right boundary: a first-order one-sided difference and a ghost-point closure. Each treatment is tested with Neumann and Robin conditions, giving four cases with the same interior discretisation and problem data.

### Problem setup

$$
-\Delta u=f,\qquad (x,y)\in(0,1)^2.
$$

The manufactured solution is $`u^*(x,y)=e^{x+y}`$, with source term $`f=-2e^{x+y}`$. Dirichlet data $`g=u^*`$ are prescribed on the left, bottom and top edges, including all four corners. On the open right edge $`x=1,\ 0<y<1`$, we use:

- **Neumann:** $`u_x=q(y)=e^{1+y}`$;
- **Robin:** $`u_x+2u=r(y)=3e^{1+y}`$.

The uniform nodal grid has spacing $`h=1/N`$. Here, `N` is the number of intervals in each direction, so each edge has `N+1` nodes. See [Problem and interfaces](docs/interfaces.md) for the indexing, array shapes and function contracts.

### Team responsibilities

| Member | Main work | Deliverables |
|---|---|---|
| A | Problem data, grid and indexing, interior five-point stencil, Dirichlet elimination | `problem.py`, `grid.py`, `core.py`, basic tests, interface and handoff notes |
| B | First-order Neumann and Robin boundary closures | `boundary_first_order.py`, boundary-row derivations, boundary tests and method description |
| C | Ghost-point Neumann and Robin boundary closures | `boundary_ghost.py`, ghost-point elimination, boundary tests and method description |
| D | Error norms, experiments on four mesh levels, convergence analysis and plots | `error_metrics.py`, experiment scripts, CSV tables, error plots and results discussion |
| E | Sparse solver, residual and matrix diagnostics, integration checks | `solver.py`, independent solver comparison, matrix plots, audit records and report integration |

Each member writes their own report section and commits through their own account. B and C review each other's boundary derivations. E checks A's assembly and reruns D's experiments; D checks the residual and error-norm definitions used in E's diagnostics. The [team plan](docs/team_plan.md) gives the completion criteria and branch arrangements.

### Current status

A's baseline assembly is complete, with **27 basic tests passed**; see [A's handoff notes](docs/handoff_A.md).

B's baseline is currently complete
- Implemented first-order Neumann and Robin boundary closures in `boundary_first_order.py`, preserving interior equations and Dirichlet corners.
- Added 11 tests covering N=2/N=4 hand-calculated rows, repeated application, manufactured-solution defects, affine derivative probes, and small integrated solves.
- **All 38 local tests passed** (27 existing + 11 new). Small-grid errors approximately halve under refinement, consistent with first-order convergence.
- Completed [boundary derivations], [precomputation predictions], and [handoff notes].

B's code remains on the feature branch until merged. C's independent review, E's solver integration, D's formal convergence experiments, and the official course audit remain pending. The main branch still contains the B–E placeholder entry points.

`assemble_core` leaves the right-boundary rows and their right-hand-side entries at zero for B and C to fill. This matrix is incomplete until a boundary closure has been applied.

### Installation and checks

Use Python 3.10 or newer. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/YifanChen-13/PDEproject2.git
cd PDEproject2
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments/inspect_core.py --N 8
```

On macOS / Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python experiments/inspect_core.py --N 8
```

The inspection script reports the number of unknowns, reserved boundary rows and the defect obtained by inserting the manufactured solution into the interior difference equations. This defect measures discrete consistency; it is distinct from the numerical solution error and the linear-solver residual.

### Repository layout

| Path | Contents |
|---|---|
| `src/pde_bvp/` | Problem data, grid, matrix assembly, boundary closures, solver and error functions |
| `tests/` | Basic tests; each member adds tests for their own implementation |
| `experiments/` | Core-assembly inspection; full experiment scripts will be added here |
| [docs/interfaces.md](docs/interfaces.md) | Mathematical problem, indexing, array shapes and function contracts |
| [docs/team_plan.md](docs/team_plan.md) | Tasks, completion criteria, branches and review arrangements |
| [docs/handoff_A.md](docs/handoff_A.md) | A's validation results and the next member's starting steps |
| [docs/precomputation.md](docs/precomputation.md) | Predictions recorded before running the checks |
| [docs/ai_audit.md](docs/ai_audit.md) | Scope of AI assistance, completed checks and outstanding course audit work |

### Next steps

Review and merge B's `feature/first-order` implementation. C implements the ghost-point closure, E connects the sparse direct solver, and D develops the error functions. Integrate B's first-order cases through E's solver, then complete the remaining combinations and four-mesh experiments.

The final experiments will report global, right-boundary and interior errors, a scaled algebraic residual, and matrix nonsymmetry. Convergence rates will be calculated from the computed data. The complete coursework also requires the report, independent reviews and the course's five-gate audit.

---

## 中文

采用有限差分法求解单位正方形上的 Poisson 方程，比较右边界使用一阶单边差分和 ghost-point 闭合时的误差与收敛表现。两种闭合分别搭配 Neumann 和 Robin 条件，共四组实验；内部离散和问题数据保持一致。

### 问题设置

$$
-\Delta u=f,\qquad (x,y)\in(0,1)^2.
$$

制造解为 $`u^*(x,y)=e^{x+y}`$，对应源项 $`f=-2e^{x+y}`$。左、下、上三条边给定 Dirichlet 数据 $`g=u^*`$，全部四个角点也按 Dirichlet 条件处理。开放右边界 $`x=1,\ 0<y<1`$ 分别使用：

- **Neumann：** $`u_x=q(y)=e^{1+y}`$；
- **Robin：** $`u_x+2u=r(y)=3e^{1+y}`$。

使用步长为 $`h=1/N`$ 的均匀节点网格。`N` 是每个方向的区间数，因此每边有 `N+1` 个节点。节点编号、数组形状和函数约定见 [问题与接口](docs/interfaces.md)。

### 小组分工

| 成员 | 主要工作 | 交付内容 |
|---|---|---|
| A | 问题数据、网格与编号、内部五点差分、Dirichlet 消元 | `problem.py`、`grid.py`、`core.py`、基础测试、接口和交接说明 |
| B | Neumann / Robin 的一阶边界闭合 | `boundary_first_order.py`、边界行推导、边界测试和方法说明 |
| C | Neumann / Robin 的 ghost-point 闭合 | `boundary_ghost.py`、ghost 消元推导、边界测试和方法说明 |
| D | 误差范数、四级网格实验、收敛分析与作图 | `error_metrics.py`、实验脚本、CSV 表格、误差图和结果分析 |
| E | 稀疏求解、残差与矩阵诊断、集成核验 | `solver.py`、独立求解对照、矩阵图、审计记录和报告整合 |

每人撰写自己部分的报告，并用自己的账号提交代码。B、C 互查边界推导；E 检查 A 的基础装配并复跑 D 的实验；D 核查 E 的诊断中使用的残差与误差范数定义。完成标准和分支安排见 [分工与协作](docs/team_plan.md)。

### 当前进度

A 的基础装配已经完成，**27 项基础测试通过**，详见 [A 的交接记录](docs/handoff_A.md)。

B 完成实现和本地验证，待复核并合入 main。**
- 完成 `boundary_first_order.py` 中 Neumann / Robin 两种一阶边界闭合，保留内部方程和 Dirichlet 角点。
- 新增 11 项测试，覆盖 N=2/N=4 手算边界行、重复调用、制造解缺陷、线性函数导数和小规模集成求解。
- **本地 38 项测试全部通过**（原有 27 项 + 新增 11 项）。小网格误差随加密约减半，符合一阶预期。
- 完成[边界公式推导]、[计算前预测]和[交接记录]。
B 的代码在合并前仍位于工作分支。C 的独立复核、E 的正式求解器集成、D 的正式收敛实验和课程审计尚待完成；main 分支目前仍保留 B–E 的占位函数入口。

`assemble_core` 将右边界矩阵行和对应右端项保留为零，交由 B、C 填入。在接入边界闭合之前，这个矩阵尚未装配完整。

### 安装与检查

需要 Python 3.10 或更新版本。先克隆仓库并建立虚拟环境：

```bash
git clone https://github.com/YifanChen-13/PDEproject2.git
cd PDEproject2
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments/inspect_core.py --N 8
```

macOS / Linux：

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python experiments/inspect_core.py --N 8
```

检查脚本输出未知量数、预留边界行数，以及将制造解代入内部差分方程得到的缺陷。这个缺陷用于检查离散一致性，与数值解误差、线性求解残差含义不同。

### 文件位置

| 路径 | 内容 |
|---|---|
| `src/pde_bvp/` | 问题数据、网格、矩阵装配、边界闭合、求解与误差函数 |
| `tests/` | 已实现的基础测试；各成员补充自己部分的测试 |
| `experiments/` | 基础装配检查；后续加入完整实验脚本 |
| [docs/interfaces.md](docs/interfaces.md) | 数学问题、节点编号、数组形状和函数约定 |
| [docs/team_plan.md](docs/team_plan.md) | 五人任务、完成标准、分支与核验安排 |
| [docs/handoff_A.md](docs/handoff_A.md) | A 的验证结果和下一位成员的接手步骤 |
| [docs/precomputation.md](docs/precomputation.md) | 运行检查前记录的预期 |
| [docs/ai_audit.md](docs/ai_audit.md) | AI 辅助范围、已做检查和待完成的课程审计 |

### 后续安排

先复核并合并 B 的 `feature/first-order` 实现。C 实现 ghost-point 闭合，E 接入稀疏直接求解器，D 完成误差函数。通过 E 的正式求解器接入 B 的一阶闭合，再完成其余组合和四级网格实验。

正式实验将报告全局、右边界和内部误差、经过缩放的代数残差，以及矩阵的非对称性。收敛阶根据实际计算数据求得。完整作业还需完成报告、组员独立复核和课程要求的五关审计。
