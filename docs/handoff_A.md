# A 的交接记录

日期：2026-11-03。接手人：B；C、D、E 可同时按分工开始工作。

## 已交付

- 固定课程制造解、源项、Dirichlet / Neumann / Robin 数据。
- `N+1` 个节点的网格，以及消去 Dirichlet 后的未知量编号。
- 内部五点差分和正确符号的 Dirichlet 右端贡献。
- 预留开放右边界的 `N-1` 行；两侧右角点始终属于 Dirichlet。
- LIL 装配接口、完整节点数组恢复工具和基础测试。
- B、C、D、E 的函数入口，以及数据形状、分工、预计算和 AI 使用说明。

## 验证记录

在项目虚拟环境完成可编辑安装后运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments/inspect_core.py --N 8
.\.venv\Scripts\python.exe experiments/inspect_core.py --N 16
.\.venv\Scripts\python.exe experiments/inspect_core.py --N 32
```

结果：**27 项测试全部通过**。测试环境为 Python 3.13.2、NumPy 2.2.4、SciPy 1.15.2、pytest 9.2.0。虚拟环境沿用本机 Python 中已有的 NumPy / SciPy，测试和绘图依赖安装在项目环境中；这不是一次全新系统的安装测试。

| N | 未知量 | 内部行 | 预留右边界行 | 非零元 | 内部制造解代入缺陷 Linf |
|---|---:|---:|---:|---:|---:|
| 8 | 56 | 49 | 7 | 224 | 1.49937518e-2 |
| 16 | 240 | 225 | 15 | 1080 | 4.24587776e-3 |
| 32 | 992 | 961 | 31 | 4712 | 1.12981800e-3 |

上述三个网格的右边界矩阵行和对应右端均为零，符合计算前记录。

测试还逐点比较了装配后的缺陷与独立差分恒等式 `-Delta_h exp(x+y) = -8 exp(x+y) sinh(h/2)**2 / h**2`。将缺陷除以该节点的 `exp(x+y)` 后，连续两次加密的观测阶约为 `2.00056` 和 `2.00014`，符合内部二阶一致性预期。表中未归一化的最大缺陷还受最大取值节点随网格变化的影响。

这些数值是内部装配的一致性检查；本阶段没有完整混合边界数值解，不能把它们写成解误差或整个问题的收敛阶。

## B 从哪里接手

先读 [interfaces.md](interfaces.md)，重点是 `U[j,i]`、`grid.index_map[j,i]` 和 `grid.right_rows`。接着完成 `src/pde_bvp/boundary_first_order.py`。

```python
from pde_bvp import Problem, assemble_core, build_grid
from pde_bvp.boundary_first_order import apply_first_order

problem = Problem(N=4, bc_type="neumann")
grid = build_grid(problem)
A, b = assemble_core(problem, grid)
# 下面这一行需等 B 实现后才能运行：
A, b = apply_first_order(A, b, problem, grid)
```

对于 `j=1,...,N-1`，边界行号为 `grid.index_map[j,N]`，向内邻点为 `grid.index_map[j,N-1]`。只填右边界行，不要改变 A 已经组装的内部行。分别添加 Neumann 与 Robin 测试，先与手算核对，再与 E 接求解器。

建议第一份 PR 包含：

1. 两种一阶边界条件的实现；
2. `N=2` 和 `N=4` 的行系数及右端测试；
3. 内部行不变和 Dirichlet 角点不被覆盖的检查；
4. 简短手推说明及实际运行的验证命令。

请 C 复查 B 的边界公式。C 在独立基础矩阵上实现 ghost 闭合；不得把 B 的矩阵再改成 ghost 矩阵作为对比实验。

## 尚未完成

B、C 的边界算法、D 的误差和实验、E 的求解器及集成诊断均待对应成员完成。正式四级网格误差表、报告、组员独立复核和课程五关审计也尚未完成。当前交付可供下一位同学开发，不能作为完整课程作业提交。
