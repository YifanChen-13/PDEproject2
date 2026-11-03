# 五人分工与协作

目标是完成同一问题的四组可比较实验：Neumann / Robin × first-order / ghost。每人都有代码、验证和报告任务；核验过程也保留可查看的记录。

## A：基础问题与内部装配

负责 `problem.py`、`grid.py`、`core.py`，建立安装方式和公共接口。提交网格编号、角点归属、五点差分及 Dirichlet 移项的测试。

完成标准：小网格系数能与手算逐项对应；保留所有右边界未知量；右边界行保持空白；制造解代入内部差分的缺陷符合二阶预期。交给 E 核查。报告中说明连续问题、网格、未知量编号和内部离散。

## B：一阶边界闭合

负责 `boundary_first_order.py`，新增 `tests/test_first_order.py` 与 `docs/derivation_first_order.md`。

完成标准：两种边界数据都能装配；在 `N=2`、`N=4` 上逐项检查边界系数与右端；内部行未改动；角点仍由 Dirichlet 控制；替入制造解检查边界缺陷，并在接入求解器后检查边界误差。与 C 互查推导。报告中解释边界行替代 PDE 行及一阶闭合的误差来源。

## C：ghost-point 边界闭合

负责 `boundary_ghost.py`，新增 `tests/test_ghost.py` 与 `docs/derivation_ghost.md`。

完成标准：从中心边界条件推导消元后的 PDE 行；两种边界数据都实现；检查向内耦合系数、Robin 对角项、边界数据符号，以及邻近上、下边的已知项；矩阵中没有 ghost 自由度。与 B 互查推导。报告中解释该方法与一阶边界行在方程结构上的差异。

## D：实验与误差分析

负责 `error_metrics.py`，新增 `experiments/convergence.py`、`experiments/visualize.py` 和误差工具测试。原始数值表放 `results/tables/`，图放 `results/figures/`，运行参数和版本写入结果说明。

完成标准：误差工具对精确解返回零，对已知常数偏移返回可手算的范数；四种组合各运行四级网格；记录全局 L2/Linf、内部与右边界 Linf、实际观测阶和 E 提供的缩放残差；说明拟合使用的渐近区间。核对 E 的范数定义和残差缩放，结果交给 E 复跑。报告中分析数据，不预填收敛结论。

## E：求解、诊断与核验

负责 `solver.py`，新增 `tests/test_solver.py` 和 `experiments/diagnostics.py`，维护集成核验记录。

完成标准：正确切换四种组合；输入不支持的闭合名时明确报错；返回约定的数据形状；报告缩放残差、矩阵非对称性和结构图；在一个代表网格上做代数误差的独立对照。复查 A 的手算行并从干净环境复跑 D 的结果。对照课程正式的五关审计表完成审计，整合报告格式、符号、图表和复现命令；方法与结果正文仍由各部分负责人撰写。

## 交接顺序

1. A 提交基础接口、代码及测试。
2. B、C 并行实现边界；D 同时写误差工具；E 同时编写求解器与诊断。边界实现未合并时，E 可以先检查派发逻辑与矩阵输入，不使用制造解替代边界实现。
3. B 的一阶闭合先接入 E 的求解器，打通一个粗网格 Neumann 算例；随后接入 C 和 Robin 分支。
4. 所有边界和求解测试通过后，D 运行统一实验，E 独立复跑。发现问题回到对应模块修改，不能只修表格中的数字。
5. 各人完成自己的报告部分；E 整合，五人逐项核对后提交课程作业。

## GitHub 协作

| 成员 | 工作分支 |
|---|---|
| B | `feature/first-order` |
| C | `feature/ghost-point` |
| D | `feature/convergence` |
| E | `feature/validation` |

A 的初始化作为当前基线；后续修正使用 `fix/core`。其余成员先拉取当前 `main`，再建立上表中的分支。分支在各人开始工作时创建，不提前堆放空分支。

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/first-order
# 完成自己的实现和测试后
git add src/pde_bvp/boundary_first_order.py tests/test_first_order.py docs/derivation_first_order.md
git commit -m "Implement first-order Neumann and Robin rows"
git push -u origin feature/first-order
```

在 GitHub 建立 PR，写明新增功能、验证命令及仍未解决的问题，由表中安排的同学检查。使用各自账号和已关联的提交邮箱，保留真实贡献记录。修改公共接口前在 PR 中说明受影响的成员。每次合并前运行全部已有测试，避免各自通过、集成后失败。
