# 问题、离散与代码接口

依据课程 Problem Pack 的 Direction 2（第 3–5 页）；深度比较说明在第 7 页，共同核验要求在第 10 页。原始课程文件未随公开仓库转载。

## 连续问题

在 `(0,1)^2` 上求解 `-Delta u = f`。固定制造解 `u*=exp(x+y)`，源项 `f=-2 exp(x+y)`。

`x=0`、`y=0`、`y=1` 施加 Dirichlet 条件 `g=exp(x+y)`，包括四个角点。只在开放右边界 `x=1, 0<y<1` 施加 Neumann 或 Robin 条件。右侧外法向是 `(1,0)`，所以这里的 `q` 是 `u_x`，不是物理热流的负号定义。`q=exp(1+y)`，`beta=2`，`r=3 exp(1+y)`。

三条 Dirichlet 边非空；本题无需纯 Neumann 问题的兼容性条件或定标。纯 Neumann 扩展不在当前分工范围。

## 网格与未知量

- `N` 表示区间数，`h=1/N`，`x_i=i*h, y_j=j*h`。
- 完整节点数组使用 `U[j, i]`，形状为 `(N+1, N+1)`。第一个索引沿 y，第二个沿 x。
- Dirichlet 节点已消元。未知节点为 `1 <= i <= N, 1 <= j <= N-1`，共 `N*(N-1)` 个。
- 向量编号 `k=(j-1)*N+(i-1)`，即 x 方向先变化。
- `grid.index_map[j,i]` 给出 `k`；已知节点标为 `-1`。两个右角点也是 `-1`。
- `grid.interior_rows` 对应 `1 <= i,j <= N-1`；`grid.right_rows` 对应 `i=N, 1 <= j <= N-1`。
- `grid.to_nodal(uh)` 把长度为 `N*(N-1)` 的向量恢复为完整 `U`，同时填回三条已知边。

例如 `N=4` 时，未知量编号为：

```text
          i=0   i=1   i=2   i=3   i=4
j=4        D     D     D     D     D
j=3        D     8     9    10    11
j=2        D     4     5     6     7
j=1        D     0     1     2     3
j=0        D     D     D     D     D
```

右边界行是 `3,7,11`；`D` 不进入未知量向量。

## A 已实现的内部行

在 `1 <= i,j <= N-1`，五点差分为

$$\frac{4U_{i,j}-U_{i-1,j}-U_{i+1,j}-U_{i,j-1}-U_{i,j+1}}{h^2}=f_{i,j}.$$

未知邻点的系数为 `-1/h**2`，对角元为 `4/h**2`。每个已知 Dirichlet 邻点把 `+g/h**2` 加入 `b`。靠近右边界的内部行仍然保留与右边界未知量的耦合，不能把它当作已知制造解消掉。

`N=2` 时，未知量依次是 `(1/2,1/2)` 和 `(1,1/2)`。基础矩阵和右端为：

```text
A = [[16, -4],
     [ 0,  0]]
b = [-2*e + 4*(2*exp(1/2) + exp(3/2)), 0]
```

## B、C 的边界接口

```python
A, b = assemble_core(problem, grid)
A, b = apply_first_order(A, b, problem, grid)  # B
# 或者从新的基础矩阵开始：
A, b = apply_ghost(A, b, problem, grid)        # C
```

输入 `A` 是 SciPy LIL 稀疏矩阵，方便修改行；`b` 是一维浮点数组。两个函数原位填入右边界行，再返回同一个 `(A,b)`。不得修改内部行、重复加上一次边界贡献或覆盖 Dirichlet 角点。比较两种方法时必须各自重新调用 `assemble_core`，不能在同一矩阵上先后施加两种闭合。

- B 按课程给定的一阶后向差分构造边界行。这一行替代右边界处的 PDE 行。
- C 先用中心差分边界条件消掉 ghost 值，再在右边界处施加 PDE。线性系统中不得留下 ghost 未知量。
- 两人分别处理 `problem.bc_type == 'neumann'` 和 `'robin'`，调用 `neumann_data` / `robin_data`，并考虑靠近上、下边界的已知邻点。
- 需要从头手推并核查所有符号与 h 的幂次；不能只依据最终图像判断正确。

## E 的求解接口

```python
U, A, b, grid = solve_problem(Problem(N=32, bc_type="neumann"), closure="ghost")
```

`closure` 仅接受 `'first_order'` 或 `'ghost'`。装配完成后转成 CSR，用 `scipy.sparse.linalg.spsolve` 求解，再由 `grid.to_nodal` 恢复 `U`。返回的 `A` 是完整装配后的 CSR 矩阵，`U` 是完整二维节点数组，`b` 仍是一维数组。

两种闭合一般都产生非对称矩阵，不直接使用 CG。量化 `||A-A.T||_F / ||A||_F`，并画矩阵结构图。直接求解器 `spsolve` 没有可设置的迭代容差；需要报告残差，并在代表网格上做条件性估计或独立紧容差求解对照，以判断代数误差是否小于离散误差。

建议共同使用的分量缩放残差：

$$\eta=\max_k\frac{|(A u_h-b)_k|}{(|A|\,|u_h|+|b|)_k}.$$

分母与分子均为零时，该项取零。若分母为零而分子非零，必须报告异常。保留原始矩阵计算；不要通过改写 PDE 行来混淆残差的缩放。E 记录所用范数与实际判据，D 在所有网格上保持一致。

## D 的误差接口

```python
errors = compute_errors(U, problem, grid)
# keys: l2, linf, interior_linf, right_linf
```

设 `e[j,i]=U[j,i]-exp(x_i+y_j)`。`linf` 是全部节点上的最大绝对误差，`interior_linf` 只取 `1 <= i,j <= N-1`，`right_linf` 只取开放右边界。

`l2` 使用完整节点上的二维梯形权重：每个方向的两个端点权重为 `1/2`，其余为 `1`，即 `sqrt(h**2 * sum(w_y[j]*w_x[i]*e[j,i]**2))`。报告中明确称为梯形加权离散 L2 范数。

正式加密实验建议 `N=8,16,32,64`，四种组合使用相同网格、范数和代数误差标准。B、C、E 的小网格测试通过后再生成正式结果。先记录预期，再运行；观测阶由误差表确定，不把期望的一阶或二阶硬编码成结果。
