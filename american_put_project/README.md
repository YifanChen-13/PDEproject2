# 永久美式看跌期权数值项目

项目总入口是[仓库根目录 README](../README.md)。本项目使用单调迎风有限差分与策略迭代求解一维永久美式看跌期权障碍问题。Stage 1 对照常波动率解析解，Stage 2 对局部波动率分别进行网格加密、计算域截断和容差实验。

## 安装与测试

在仓库根目录执行以下命令，Windows 用户将虚拟环境激活命令替换为 `.venv\Scripts\activate`。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r american_put_project/requirements-dev.txt
python -m pytest -q
python american_put_project/run_all.py
```

也可以在本目录执行 `python -m pytest -q` 或 `python run_all.py`。完整计算包含细网格参考解，可能需要数分钟。运行产生带 UTC 时间戳的新目录，旧的 Stage 2 结果不会被覆盖。统一入口会生成 Stage 1 数据、旧版原型的数值表和图、原型 PDF、Stage 2 新结果、50 项数组复核，以及独立配点和 PSOR 对比。控制台会打印输出路径。

## 分项运行

以下命令从本目录执行。

```bash
python inspect_assembly.py
python stage1_validation.py
python stage2_studies.py
python verify_stage2_D.py stage2_D_runs/20261105T132543802032Z
python independent_audit.py
```

Stage 1 单独运行时会更新本目录下对应 CSV 和图片。Stage 2 会新建目录。核验脚本会在指定结果目录更新 `verification_D.json` 和点值对照 CSV，因此如需保留原始文件的字节内容，请先复制结果目录。独立审核默认更新 `results/independent_audit/`。

较早的 `run_project.py` 可直接运行，也支持 `--output-dir <目录>` 将结果、图和预测记录写入指定目录。直接运行会更新旧版 `results/`、`figures/` 和 `protocols/ai_solver_audit.json`，预测记录会使用新的时间戳文件。`build_report.py --input-root <目录>` 生成基于该目录旧版原型结果的 PDF。它生成的八页 PDF 与 `report/main.pdf` 为两份不同阶段的草稿。

## 数据与结论

- `docs/report_D.md` 和 `stage2_D_runs/20261105T132543802032Z/` 记录 D 的原始实验。网格研究固定 $S_{max}=600$，域研究固定 $h=0.0625$。
- `results/independent_audit/` 包含独立配点和同条件 PSOR 对比。两种连续方法使用相同模型，计算方法不同。
- 历史细网格参考的实际残差高于请求的 $10^{-8}$，程序将其标记为浮点下限。域上界从 400 扩至 600，$V_h(100)$ 增加约 0.2343。有限域参考值与无穷域精度需要分别讨论。
- `report/main.tex` 和 `slides/main.tex` 对应当前仓库的单调迎风方法。报告使用历史已保存数据中的数字，重跑产生的新数字需要人工核对后更新文稿。
- `archive/` 保留旧上传包及当时的校验和。历史文件的路径和状态描述代表当时的交付，不作为现在的操作说明。

## 审核与待完成事项

`docs/technical_audit.md` 列出已经执行的代码和数值审核及其范围。组员仍需实际完成本人算前预测与核对、独立复现、五关表格与讨论、个人贡献说明，以及报告中的真实姓名和组别。现有记录和技术审核由 AI 协助完成，不能代签学生审核。
