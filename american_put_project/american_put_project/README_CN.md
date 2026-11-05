# 永久美式看跌期权

[English project overview](../README.md#english) | [中文项目说明](../README.md#中文)

本目录对应选定的障碍/自由边界 BVP。模型、两个阶段的实验和五人分工见仓库首页的中英文说明。

## A 的基础工作与交接

- `problem.py`：收益函数、阶段 1 精确数据、股息率和波动率数据。
- `discretization.py`：单调三对角 -L 装配与 Dirichlet 端点消元。
- `tests/test_foundation.py`：模型恒等式、手算差分行和多项式检查。
- `inspect_assembly.py`：装配诊断，不进行 LCP 求解。
- [问题定义](docs/problem_definition.md)、[五人分工](docs/team_plan.md)与 [A 的交接说明](docs/handoff_A.md)。

A 的 35 项基础测试已通过。在本目录中使用准备好的 Python 环境运行：

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python inspect_assembly.py
```

## D 的阶段 2 实验

D 的脚本、测试、报告和实际结果已整合到本目录，使用共用的 A/B 模块。
运行 `python -m pytest -q -p no:cacheprovider` 会收集全部 64 项 A/B/D 测试。
运行 `python stage2_studies.py` 会创建新的 `stage2_D_runs/<UTC 时间戳>/`。
再用输出的目录运行 `python verify_stage2_D.py <结果目录>` 和
`python build_stage2_docs.py <结果目录>`，可复查数组并更新 D 的报告表格。
详见[中文指南](docs/guide_D_CN.md)及[交接说明](docs/handoff_D.md)。
根目录 `Member_D/` 保留原上传副本；后续使用本目录。人工复核和官方审计仍待完成。

## 已有原型

`solver.py`、`run_project.py`、`build_report.py`、`Report_Source.md` 以及 `results/`、`figures/`、`protocols/` 是仓库原先已有的文件。B-E 继续复核求解器、重跑实验并撰写各自的报告。A 本次验证模型与装配，未重新认证先前的完整求解结果。旧校验和文件记录的是此前的文件版本。

结果经复核后，可用报告生成脚本生成 `American_Put_Report.pdf`；仓库当前没有跟踪这份生成的报告。课程官方表格与组员独立审核仍需按课程要求完成。
