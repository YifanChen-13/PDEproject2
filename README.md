# PDE Project 2: Mixed Boundary Data

这是我们五人小组的 PDE 边值问题作业。我们在单位正方形上用有限差分法求解 Poisson 方程，比较右边界采用一阶单边差分和 ghost-point 闭合时的误差与收敛表现。右边界分别使用 Neumann 和 Robin 条件，共四组实验，其余设置保持一致。

## 问题设置

$$-\Delta u=f,\qquad (x,y)\in(0,1)^2.$$

制造解为 $u^*(x,y)=e^{x+y}$，因此 $f=-2e^{x+y}$。左、下、上三条边给定 $g=u^*$，并负责全部四个角点。开放右边界 $x=1,\ 0<y<1$ 使用：

- Neumann：$u_x=q(y)=e^{1+y}$；
- Robin：$u_x+2u=r(y)=3e^{1+y}$。

我们使用 $h=1/N$ 的均匀节点网格。`N` 是每个方向的区间数，所以每边有 `N+1` 个节点。完整约定见 [问题与接口](docs/interfaces.md)。

## 小组分工

目前用 A–E 标记成员，姓名由小组确定后补充。

| 成员 | 主要工作 | 交付内容 |
|---|---|---|
| A | 问题定义、网格与编号、内部五点差分、Dirichlet 消元 | `problem.py`、`grid.py`、`core.py`、基础测试、接口和交接说明 |
| B | Neumann / Robin 的一阶边界闭合 | `boundary_first_order.py`、手推边界行、边界测试、相应方法说明 |
| C | Neumann / Robin 的 ghost-point 闭合 | `boundary_ghost.py`、ghost 消元推导、边界测试、相应方法说明 |
| D | 误差范数、四级网格实验、收敛分析与作图 | `error_metrics.py`、实验脚本、CSV 表格、误差图和结果分析 |
| E | 稀疏求解、残差与矩阵诊断、集成核验 | `solver.py`、独立求解对照、矩阵图、审计记录和报告整合 |

每人撰写自己部分的报告，并用自己的账号提交代码。B、C 互查边界推导；E 检查 A 的基础装配并复跑 D 的结果；D 核查 E 使用的残差与误差范数。具体完成标准见 [分工与协作](docs/team_plan.md)。

## 当前进度

A 的基础装配已经完成，27 项基础测试通过，实际环境与检查结果记在 [A 的交接记录](docs/handoff_A.md)。B、C、D、E 的函数入口已保留，调用时会明确提示尚未实现。当前仓库能检查网格、内部矩阵和已知边界项，完整的混合边界求解还需要接入两种边界闭合和求解器。

`assemble_core` 返回的右边界行是零行，这是留给 B、C 的接口。不要直接求解这一个未完成的矩阵，也不要把制造解填入右边界来绕过边界实现。

## 安装与检查

需要 Python 3.10 或更新版本。以下命令在仓库根目录执行。

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

检查脚本输出未知量数、预留边界行数及制造解代入内部差分行的缺陷。这里的缺陷是离散一致性检查，不是数值解的误差或线性求解残差。

## 文件位置

```text
src/pde_bvp/       问题数据、网格、矩阵、边界、求解与误差函数
tests/             已实现的基础测试；后续成员补充各自测试
experiments/       基础装配检查；后续加入完整实验脚本
docs/interfaces.md 数学问题、节点编号、数据形状和函数约定
docs/team_plan.md  五人任务、完成标准、分支与核验安排
docs/handoff_A.md  A 的检查结果，以及下一位成员的接手步骤
docs/precomputation.md 运行前写下的预期
docs/ai_audit.md   AI 辅助范围、已做检查和待完成的课程审计
```

## 接下来怎么做

B、C 从当前 `main` 分别建立分支，填入自己的边界行；E 接入稀疏直接求解器；D 先实现误差工具。先打通 Neumann + first-order 的小网格算例，再接入其余三种组合，最后统一运行四级网格实验。

完整实验需分别报告全局误差、右边界误差、内部误差和经过缩放的代数残差，并检查矩阵的非对称性。收敛阶必须从实际数据判断。报告及课程要求的五关审计完成前，不把代码检查结果写成整个作业已经完成。
