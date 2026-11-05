# 成员 D 交付包

本包用于仓库 YifanChen-13/PDEproject2 的美式期权题目。
依据 main 提交 `489f549136502ff37e57a71cf2c73292f007ace3` 中的五人分工。

## 先阅读

1. `american_put_project/docs/guide_D_CN.md`：中文解释任务、实验、结果和注意事项。
2. `american_put_project/docs/report_D.md`：有实际数值的英文报告章节草稿。
3. `american_put_project/docs/handoff_D.md`：交接说明与复核状态。

## 放入原仓库

压缩包只包含本次 D 新增的文件。解压后，将其中 `american_put_project/`
的内容合并到原仓库同名目录。保留原仓库 A/B 的 `problem.py`、
`discretization.py`、`solver.py` 和依赖文件。此包不覆盖这些模块，
也不包含或覆盖原有 `results/`、`figures/`、`protocols/` 或总报告。

新增文件：

- `stage2_studies.py`：重跑实验。
- `build_stage2_docs.py`：根据指定结果目录更新报告表格。
- `verify_stage2_D.py`：不调用求解器，复查已保存的数组与比较结果。
- `tests/test_stage2_studies.py`：比较网格和误差范数的四项测试。
- `docs/precomputation_D.md`：计算前预测。
- `docs/report_D.md`、`docs/guide_D_CN.md`、`docs/handoff_D.md`：报告与交接。
- `stage2_D_runs/20261105T132543802032Z/`：实际执行结果。

这次执行时间为北京时间 2026-11-05 21:25 起；目录名使用 UTC。
目录中有四级网格、两级参考、三个计算域和求解容差比较结果，
共 11 次实际求解（Smax=600 的计算域基线复用网格实验，不重复求解）。
正式结果包括 6 份 CSV、11 份压缩数组、3 组 PNG/PDF 图、预测/结果
JSONL、摘要与源文件校验信息、保存数组复查结果。

## 重跑命令

在原仓库的 `american_put_project/` 中运行，使用安装了原依赖的 Python：

```bash
python -m pytest -q -p no:cacheprovider
python stage2_studies.py
```

脚本会输出新的时间戳目录，不覆盖旧结果。再运行以下命令时，
把目录名替换为新输出的目录：

```bash
python verify_stage2_D.py stage2_D_runs/20261105T132543802032Z
python build_stage2_docs.py stage2_D_runs/20261105T132543802032Z
```

本次 64 项 pytest 检查通过，保存数组与表格的另 50 项核对通过。
当前电脑的 NumPy longdouble 与 float64 精度相同；保存数组残差复查
没有获得额外精度，未被描述成高精度独立验证。

## 提交和复核状态

本包已在本地执行并整理；上传分支为 `feature/stage2-studies-d`，
主分支整合与人工复核状态请查看对应 Pull Request。
这是 AI 协助完成的实验和英文草稿；C/E 的人工独立复核、课程正式
计算前问答与 five-gate audit 表格和签字仍待完成。请先理解并检查
自己的部分，再用自己的 GitHub 账号提交实际认可的工作。
