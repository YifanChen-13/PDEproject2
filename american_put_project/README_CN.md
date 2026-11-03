# 阅读与运行说明

先打开 American_Put_Report.pdf：8 页英文报告，包含模型、离散推导、实际计算的表格和图、结果解释及误差分析。

## 文件怎么用

- solver.py：求解器，包含单调有限差分、策略迭代和独立 ODE 验证。
- run_project.py：一键重跑所有实验。
- build_report.py：根据实际实验结果重新生成报告。
- Report_Source.md：可编辑的英文报告正文。
- results：CSV 表格、完整诊断数据、NPZ 数值解及运行日志。
- figures：PNG 和矢量 PDF 图。
- protocols：计算前预测、结果核对、AI 使用说明及自定义审核。

解压后可以将整个 american_put_project 文件夹移入桌面的 ODE_Project。
本项目不会覆盖该文件夹原有的 SDE、Van der Pol 等项目。

## 重新运行

Python 需要 numpy、scipy、matplotlib；依赖清单在 requirements.txt。
在本项目目录打开终端后依次运行：

```sh
python -m pip install -r requirements.txt
python run_project.py
python build_report.py
```

如果电脑上使用 python3 命令，请把上述 python 换成 python3。
报告生成不需要 LaTeX。更细的参考网格是最耗时的一部分。

## 结果的含义

常波动率情形的精确行权阈值为 71.42857143；h=0.0625 的接触节点为
71.4375，最大价格误差约为 0.00736，数值收敛阶约为 1。

局部波动率情形在 [0,600] 上的连续 ODE 阈值约为 69.26448；
h=0.0625 的最后接触节点为 69.25。这个数对应有限计算域，不能直接宣称
为原无限域问题的精确阈值。扩大计算域带来的影响仍明显，报告已单独分析。

原始诊断表保留了未达到请求精度的极紧容差实验，没有把浮点数精度瓶颈
掩盖为已达到容差。它们的实际残差、停止状态和价格变化均有记录。

课程的官方预测与五关审核模板未提供，附带的是自定义记录；提交时需要
对照老师的原模板完成对应表格。本包没有虚构组员贡献或独立学生审核。
