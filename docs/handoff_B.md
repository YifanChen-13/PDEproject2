# B 交接与 AI 辅助记录

2026-11-04，基于远端 main `04403ad0c50197ae95be49fd56e320caee2a4477`。
通过 GitHub 连接器读取上游文件；本机 Git HTTPS 克隆因网络连接失败未完成。
本地目录是用于实现和测试的源文件快照，不是已经成功克隆的完整 Git 工作副本。

## 已完成

- `boundary_first_order.py`：两种一阶边界行，原位替换及重复调用保护。
- `tests/test_first_order.py`：11 项新增测试；原 27 项测试也通过，共 38 项。
- `derivation_first_order.md`：报告可用的公式、手算、误差与方法说明。
- `precomputation_B.md`：运行前预测，保留原记录。

测试环境：Windows，Python 3.10，NumPy/SciPy（SciPy 1.15.3）、pytest 9.2.0。
pytest 安装在工作区外层 `tmp/pde-test-deps`，未加入项目依赖或产品代码。
首次运行 38 passed，只有测试缓存写入警告；禁用缓存后复跑见执行记录。

## 与预测核对的小规模结果

使用 A 的装配 + B 的闭合 + SciPy spsolve；未调用尚待 E 实现的求解器。
没有设置直接求解器容差，spsolve 无该参数。

| 条件 | N | 全局节点 Linf | 开放右边界 Linf | 分量后向残差 eta |
|---|---:|---:|---:|---:|
| Neumann | 8 | 1.24755487e-1 | 1.24755487e-1 | 1.558e-16 |
| Neumann | 16 | 5.83201386e-2 | 5.83201386e-2 | 2.138e-16 |
| Neumann | 32 | 2.81492140e-2 | 2.81492140e-2 | 3.046e-16 |
| Robin | 8 | 7.07032431e-2 | 7.07032431e-2 | 1.401e-16 |
| Robin | 16 | 3.43049385e-2 | 3.43049385e-2 | 2.149e-16 |
| Robin | 32 | 1.68506999e-2 | 1.68506999e-2 | 3.829e-16 |

误差随网格加密约减半，与一阶预测相符；这是 B 的集成冒烟检查，不替代 D 的
四级、四种组合、统一范数的正式实验。指数样本边界缺陷负号及一阶趋势通过测试，
内部行、角点和线性探针也符合运行前预测。

## 待完成

C 独立复核边界推导；E 接入正式求解器并做代数误差独立对照；D 完成正式实验。
Codex 辅助编写实现、测试和本文。未取得正式五关审计表，未声明通过正式课程
审计或组员人审；这些记录应随 A 的 AI 辅助记录一起交给 E。

## Git 交接

GitHub 连接器创建 `feature/first-order` 返回 HTTP 403
`Resource not accessible by integration`。虽然账户仓库权限显示 push=true，
当前集成仍不能创建远端分支。因此尚未 push，也未创建 PR。

在正常克隆的项目目录中，先执行 `git switch main`、`git pull --ff-only origin main`，
再执行 `git switch -c feature/first-order`。把补丁应用到该工作副本，运行测试后：

```bash
git add src/pde_bvp/boundary_first_order.py tests/test_first_order.py docs/derivation_first_order.md docs/precomputation_B.md docs/handoff_B.md
git commit -m "Implement first-order Neumann and Robin rows"
git push -u origin feature/first-order
```

随后向 main 建立 PR，由 C 复核。使用本人 Git 身份与关联邮箱。
