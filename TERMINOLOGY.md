# 论文卡片术语账本

本文件记录跨论文复用时容易混淆的术语。每条只保存论文原词、推荐表达、使用范围和来源卡片。只在真实使用中出现过误解、纠正或表达取舍时新增条目，不主动补全术语。具体项目的正式术语仍由该项目自己的 `CONTEXT.md` 决定。

| 概念 | 论文原词 / 别名 | 推荐表达 | 避免表达 | 适用范围 | 来源卡片 |
| --- | --- | --- | --- | --- | --- |
| 设备对外端口导纳在运行时保持不变 | `EMTP-type constant admittance equivalent`、`constant admittance matrix` | 固定端口导纳 | 无开关模型、平均值模型、所有矩阵都固定 | 指端口电压—电流关系中的导纳保持不变；开关、储能状态和输入仍可通过源项或状态更新改变响应。 | [X98GS3IY](papers/X98GS3IY-xu-state-variables-elimination-based2025.md)、[S2N95R33](papers/S2N95R33-constant-admittance-multi-converter-rts.md) |
| 设备以标准端口关系接入三相网络 | `Norton equivalent`、`port equivalent`、`I=GU+J` | 三相诺顿接口 | 网络等值、低阶模型、近似等值 | 指设备向三相外部网络暴露的端口电压—电流关系，不概括设备内部模型本身。 | [X98GS3IY](papers/X98GS3IY-xu-state-variables-elimination-based2025.md)、[JKF7XR53](papers/JKF7XR53-xu-high-speed-emtmodeling2017.md) |
| 全部设备和元件向节点方程提供的注入量 | `current-injection vector`、`I_n`、assembled history currents | 节点注入电流向量 | RHS、右端项、右端向量、把整个向量称为历史源 | 指组装后进入全局节点方程的向量；单个元件的 `history current source` 仍可按论文原义使用。 | [MXWJUTSZ](papers/MXWJUTSZ-xiong-2024-paraemt-open-source-parallelizable-hpc-compatible-emt-simulator.md)、[WGUS4P5R](papers/WGUS4P5R-liang-2026-general-fpga-solver.md) |
| 当前仿真步内端口量与网络节点电压共同求得 | `simultaneous solution`、`same-step solution`、`same-step network closure` | 本步端口—网络联立求解 | 闭合、端口—网络闭合、`network closure` | 指不插入一步接口延迟、在当前步内完成端口与网络的相互求解；不用于上一时步量驱动的延迟解耦。 | [L43KXQGH](papers/L43KXQGH-xia-nested-fast-simultaneous-solution.md)、[S2N95R33](papers/S2N95R33-constant-admittance-multi-converter-rts.md) |
| 按单元、支路、子站和电站层次组织网络求解 | `nested fast and simultaneous solution (NFSS)`、`hierarchical solution`、`recursive Schur complement` | 层级 EMT 网络求解 | 把 Schur、Rake/Compress 或 forward/backward sweep 当作整套电气方法名称 | 指面向电气层次和端口关系组织的完整求解方法；底层推导仍可准确使用 `Schur complement`。 | [L43KXQGH](papers/L43KXQGH-xia-nested-fast-simultaneous-solution.md)、[99CGN9AF](papers/99CGN9AF-feng-2021-hierarchical-modeling-power-electronic-transformers.md) |
| 先消去内部节点，再由外部解恢复内部电压 | `node elimination method (NEM)`、`Schur's complement`、`outward/inward flow` | 节点消元—电压恢复 | Schur 图、Rake/Compress 图、factor 图 | 指精确的消元与恢复依赖；描述具体代数步骤时仍使用论文原有术语。 | [X98GS3IY](papers/X98GS3IY-xu-state-variables-elimination-based2025.md)、[JKF7XR53](papers/JKF7XR53-xu-high-speed-emtmodeling2017.md) |
| 一个仿真步结束后统一进入下一步 | `barrier`、`static BSP`、synchronised cycle boundary | 步级同步屏障 | 原子提交、状态提交 | 指所有参与计算的下一状态或输出在共同边界后才对下一步可见；单纯广播启动脉冲不等于全局屏障。 | [ZFMDNBXF](papers/ZFMDNBXF-emami-2023-manticore-static-bsp.md)、[2PHB9G4M](papers/2PHB9G4M-li-2017-synchronisation-multi-fpga-microgrids.md) |
