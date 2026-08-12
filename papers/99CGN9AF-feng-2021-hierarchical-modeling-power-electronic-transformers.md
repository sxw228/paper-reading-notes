# Hierarchical Modeling Scheme for High-Speed Electromagnetic Transient Simulations of Power Electronic Transformers

作者：Moke Feng、Chenxiang Gao、Jiangping Ding、Hui Ding、Jianzhong Xu、Chengyong Zhao [pdf:E01]（PDF 物理页 1，标题页）

出处：IEEE Transactions on Power Electronics，Vol. 36，No. 9，September 2021，pp. 9994–10004 [pdf:E01]（PDF 物理页 1，页眉与首页）

年份：2021 [pdf:E01]（PDF 物理页 1，标题页）

DOI：10.1109/TPEL.2021.3061421 [pdf:E01]（PDF 物理页 1，Digital Object Identifier）

Zotero key：99CGN9AF

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的问题是：在不把 Power Electronic Transformer（PET，电力电子变压器）的高频开关、故障过程和内部状态平均掉的前提下，怎样显著加快 Electromagnetic Transient（EMT，电磁暂态）仿真。作者指出，详细模型每个时间步都要处理超高阶节点导纳矩阵，而 PET 又要求微秒量级步长并包含大量高频器件与隔离变压器，因此直接 EMT 仿真的计算时间不可接受；论文把目标明确设为“接近详细模型精度，但把主求解器看到的系统规模大幅压缩” [pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 2，Introduction 左栏首段）。

这个问题重要，不只是因为 PET 本身电路大。典型 CHB-DAB（Cascaded H-Bridge Dual Active Bridge，级联 H 桥双有源桥）PET 由三条 phase leg（PL，相臂）组成，每条 PL 又串联多个 power module（PM，功率模块），输入侧串联、输出侧并联；每个 PM 内含开关桥、储能元件和高频隔离变压器。系统级故障、闭环控制和绝缘相关暂态要求保留这些器件的时域相互作用，不能只看周期平均功率 [pdf:E01]（PDF 物理页 1，Fig. 1 与 Introduction）。

论文的工程价值在于把“物理细节保真”与“全局矩阵规模”拆开：内部节点可以从主 EMT 方程中消去，但其电压、电流和历史源仍能逆向恢复。这样，系统级求解器只处理每条 PL 的小型端口等值，而局部模块细节留在层级化前向消元和反向恢复中 [pdf:E03]（PDF 物理页 2，Fig. 2 与 Section II 开头）[pdf:E04]（PDF 物理页 11，Conclusion）。论文验证的是 PSCAD/EMTDC 下的仿真加速，而不是实时硬件或 FPGA 实现；这一边界不能外推 [pdf:E01]（PDF 物理页 1，Abstract）。

## § 2 — 前人工作与不足

**论文对相关文献的归纳，未用外部全文独立复核：**

详细 EMT 模型通常被当作精度基准，但其节点数、开关事件和全系统回溯计算使速度过慢。平均模型则通过删除或平均开关器件、变压器电流和电容纹波来换取速度：论文列举的模型有的把 DAB 替换成受控平均电流源，有的忽略电感电流动态或开关压降，有的只保留一个周期内的平均电流。作者认为，这类模型会丢失暂态、内部器件身份、故障状态或电容电压波动，因此不能满足本文追求的故障级 EMT 保真度 [pdf:E02]（PDF 物理页 2，Introduction 对文献 [15]–[19] 的归纳）。

另一条路线是端口等值。文献 [20] 所述方法把隔离变压器表示成背靠背单端口 Norton/Thevenin 等值，并对历史电压做一个时间步的近似；论文承认该近似未引发稳定性问题，但指出端口电压精度下降。文献 [22] 的 generalized Norton equivalent（广义 Norton 等值）通过节点消元保留电路方程，可用于 MMC 的任意 multiport submodule（多端口子模块），但作者指出它不能直接处理含高频隔离变压器的模块 [pdf:E05]（PDF 物理页 2，Introduction 对文献 [20]–[22] 的归纳）。

因此，本文真正填补的空档不是“又做一个 reduced-order model（降阶模型）”，而是把两件此前分开的工作接起来：先把磁耦合变压器转成不做单步端口近似的 two-port companion circuit（两端口伴随电路），再用严格的节点消元把 PM 和 PL 递归压缩。这里的“新”只能理解为论文相对其所列文献的自我定位；由于输入包没有相关论文全文，本卡不把它升级为独立 novelty 结论。

## § 3 — 重建作者的思考路径

**基于全文证据的逆向重建：**

1. 首先观察到 PET 天然有 PM → PL → 整机的层级，而且 CHB-DAB PM 对外是严格 two-port，PL 内部又是重复的 ISOP 连接。只要一种局部等值在合并后仍保持同样的 two-port 形式，就可以递归使用同一个消元操作，而不必每个时间步反演整台 PET 的大矩阵 [pdf:E03]（PDF 物理页 2，Fig. 2 与 Section II）。
2. 现有 generalized Norton node elimination 已经说明：对固定线性电路，消去内部节点可以精确保留端口电压—电流关系。真正的障碍是隔离变压器不能以磁路形式直接放入 EMT 导纳矩阵，因此应先把变压器的耦合微分方程离散成电气 two-port Norton 伴随模型 [pdf:E05]（PDF 物理页 2，文献 [22] 的能力边界）[pdf:E06]（PDF 物理页 3，Fig. 3 与 Eq. (1)–(4)）。
3. PM 内的开关在正常工况下由互补 gate signal（门极信号）决定导通组合，电容和变压器的动态则由历史电流源承载。于是可以把“随门极变化、但状态数有限的静态导纳”与“由上一步状态决定的动态注入”分离：前者离线预计算，后者在线更新 [pdf:E07]（PDF 物理页 3，Fig. 4–5 与 Section II-B）[pdf:E08]（PDF 物理页 5，precalculation 说明）。
4. 对一个 PM 做 Schur complement（舒尔补）后，得到的对象仍是广义 Norton two-port；把两个相邻 PM 按实际连接写成联合导纳，再消去连接节点，输出仍是同类型 two-port。这个“类型闭包”使二叉式递归合并成为可能 [pdf:E09]（PDF 物理页 4，Eq. (9)–(14)）[pdf:E10]（PDF 物理页 5，Fig. 7 与递归说明）。
5. 只做前向降阶还不够，因为 trapezoidal integration（梯形积分）下一步所需的历史源依赖内部电压和支路电流。因此求完外部系统后必须沿消元树逆向展开，恢复 PL、PM、变压器和电容内部量，再更新历史源 [pdf:E11]（PDF 物理页 6，Fig. 10 与 Step 1–3）。
6. blocking（闭锁）破坏正常互补开关假设，所以需要单独建模 partial blocking（部分闭锁）和 complete blocking（完全闭锁）；这不是附属功能，而是论文能覆盖启动、故障和恢复工况的必要条件 [pdf:E10]（PDF 物理页 5，Fig. 8）[pdf:E12]（PDF 物理页 6，Fig. 9 与 Eq. (16)）。

这条思考路径最后形成的设计目标是：不靠周期平均删掉动态，而是把计算从“全局大矩阵反复求解”迁移到“局部小矩阵预计算、层级合并和逆向恢复”。

## § 4 — 核心 Intuition

把每个 PM 在当前离散时刻压缩成一个只保留端口电压—电流关系的 generalized Norton two-port，内部节点暂时从主 EMT 求解器中消失，但并没有从模型状态中丢失 [pdf:E09]（PDF 物理页 4，Eq. (10)–(13)）。相邻 two-port 合并后仍是 two-port，所以可以沿 PL 递归合并，最终只把一个四节点等值接入外部系统 [pdf:E10]（PDF 物理页 5，Fig. 7 与末段）。求解结束后再沿相反方向恢复内部量并更新历史源，因此加速来自改变求解组织方式，而不是把开关暂态平均掉 [pdf:E11]（PDF 物理页 6，Fig. 10 与 inverse solution）。

## § 5 — 具体方法与完整 Pipeline

以 A 相一条含 `M` 个 CHB-DAB PM 的 PL 为例，输入是电路参数、当前 gate signals、上一步电容与变压器历史量，以及外部网络在本时间步的边界条件；输出既包括 PL 对外注入，也包括每个 PM 的内部节点电压和支路电流。

1. **建立离散 companion circuit。** 电容用等效 conductance（电导）与 Norton history current source（Norton 历史电流源）表示；隔离变压器由 Section II-A 的 two-port Norton 模型替代。正常开关组用 `G_on/G_off` 两值电导表示，论文依据电容钳位关系认为 gate signals 可决定正常导通状态 [pdf:E06]（PDF 物理页 3，Fig. 3 与 Eq. (1)–(4)）[pdf:E07]（PDF 物理页 3，Fig. 4–5）。
2. **按端口和内部节点分块。** 选一个节点为参考后，单个 PM 的导纳矩阵是 `9×9`；去掉参考节点后的方程按 3 个外部变量与 6 个内部变量分成 `G11、G12、G21、G22` 四块。对 `G22` 做舒尔补，得到 `3×3` 的相对端口导纳 `G_EQ` 和 `3×1` 注入 `I_EQ`，对应含参考节点在内的四节点 two-port [pdf:E09]（PDF 物理页 4，Eq. (6)、(10)–(14) 与 Fig. 6）。
3. **预计算有限开关状态。** 一个 CHB-DAB PM 有 6 组互补开关，正常运行只需预计算 `2^6 = 64` 个静态等值；若把 24 个器件逐个看作独立开关，则需 `2^24 = 16,777,216` 种组合。历史电流源依赖前一步结果，不能预计算，只在运行时更新 [pdf:E08]（PDF 物理页 5，precalculation 段落）。
4. **处理 blocking。** partial blocking 额外有 `2^2 = 4` 个可预计算状态，所以正常与部分闭锁共存储 `64 + 4 = 68` 个等值及其 `G_EQ、G12、G22^{-1}`。complete blocking 留下不可控二极管网络，论文另建一条聚合的 PL 级闭锁电路，串联表示高压侧电容与二极管通道，低压侧并联电容用单端口 Norton 等值表示；该状态不能沿用普通预计算 [pdf:E12]（PDF 物理页 6，Fig. 9 与 Eq. (16)）[pdf:E11]（PDF 物理页 6，`64 + 4 = 68` 与 inverse solution 上方）。
5. **递归合并 PL。** 每两个相邻 PM 先写成联合导纳，再消去它们之间的连接节点；所得 EC 与单 PM EC 具有相同形式，于是继续两两合并，直到得到 `EC-1-M`。最终每条 PL 只用四个外部节点接入主系统，外部导纳矩阵不再随 PM 内部节点数膨胀 [pdf:E10]（PDF 物理页 5，Fig. 7 与递归合并末段）。
6. **主 EMT 求解。** 当前三条 PL 的小型等值叠加到外部网络导纳矩阵，求得各 PL 的外部节点电压。论文没有改变外部 EMT solver（求解器）的基本时间推进，只改变 PET 进入该求解器的接口规模 [pdf:E03]（PDF 物理页 2，Fig. 2 与 4×4 matrix 说明）。
7. **逆向恢复。** 先用已存的 `G22^{-1}` 和 `G21` 从 PL 外部电压恢复 PL 内连接节点，再对每个 PM 做同样操作，最后得到电容和变压器端电压、支路电流，并更新下一步的 history sources [pdf:E11]（PDF 物理页 6，Fig. 10 与 Step 1–3）。
8. **拓扑扩展。** 对 CLLC resonant PM（CLLC 谐振功率模块），作者把谐振电感并入 two-port transformer matrix，扩大内部矩阵维度，但沿用相同的预计算、PM 消元、PL 合并和逆恢复流程。论文给出了 Eq. (17)–(23) 的推导，没有给出 CLLC 的独立精度或速度实验 [pdf:E13]（PDF 物理页 7，Section II-F 与 Eq. (17)–(23)）。

**计算依赖与并行性：** 前向过程是一棵 PM 等值合并树，反向过程是一棵内部量恢复树；从依赖图看可做同层并行，但论文没有给出并行调度、内存布局或通信代价。验证平台是 PSCAD/EMTDC V4.6.1 与 Intel Core i7-10710U CPU，数值字长、fixed-point（定点）误差、FPGA 映射、logic/DSP/BRAM 资源、pipeline latency（流水延迟）、实时步长抖动和硬件在环结果均未报告 [pdf:E14]（PDF 物理页 9，CPU Time Efficiency Test 与平台说明）。

## § 6 — 核心数学推导（无形式化数学则跳过）

核心数学不是经验拟合，而是“梯形积分后的 Norton 化 + 舒尔补消元”。

**1. 先把隔离变压器写成两端口微分关系。** 论文忽略铜耗、铁耗和磁芯饱和后，把辅助电感、漏感和励磁电感写成耦合电感矩阵：

\[
\begin{bmatrix}
v_{T1}(t)\\
v_{T2}(t)
\end{bmatrix}
=
\begin{bmatrix}
L_e+L_1+L_m & L_m/N\\
L_m/N & L_m/N^2+L_2
\end{bmatrix}
\begin{bmatrix}
\mathrm d i_{T1}/\mathrm dt\\
\mathrm d i_{T2}/\mathrm dt
\end{bmatrix}.
\]

这是 Eq. (1)：电压由两个端口电流变化率共同决定，非对角项 `L_m/N` 保留磁耦合 [pdf:E06]（PDF 物理页 3，Eq. (1) 与 Fig. 3）。

**2. 用梯形积分得到 Norton 形式。** 定义

\[
G_T=\frac{\Delta t}{2\Gamma}
\begin{bmatrix}
L_m/N^2+L_2 & -L_m/N\\
-L_m/N & L_e+L_1+L_m
\end{bmatrix},
\]

\[
\Gamma=\left(L_m/N^2+L_2\right)\left(L_e+L_1+L_m\right)-L_m^2/N^2.
\]

于是

\[
\mathbf i_T(t)=G_T\bigl[\mathbf v_T(t)+\mathbf v_T(t-\Delta t)\bigr]+\mathbf i_T(t-\Delta t),
\]

并可把上一时刻部分收进

\[
\mathbf J_{T,\mathrm{HIS}}(t)=G_T\mathbf v_T(t-\Delta t)+\mathbf i_T(t-\Delta t).
\]

工程直觉是：当前端口电流等于“当前端口电压乘等效导纳”加“由上一时间步记忆形成的独立电流源”，所以磁耦合元件可以进入常规 nodal admittance matrix（节点导纳矩阵） [pdf:E06]（PDF 物理页 3，Eq. (2)–(4)）。

**3. 对 PM 做舒尔补。** 将离散 PM 方程写成

\[
\begin{bmatrix}
G_{11} & G_{12}\\
G_{21} & G_{22}
\end{bmatrix}
\begin{bmatrix}
V_{EX}\\
V_{IN}
\end{bmatrix}
=
\begin{bmatrix}
I_{EX}\\
I_{IN}
\end{bmatrix}.
\]

先由内部方程得到

\[
V_{IN}=G_{22}^{-1}(I_{IN}-G_{21}V_{EX}),
\]

再代回外部方程：

\[
G_{EQ}=G_{11}-G_{12}G_{22}^{-1}G_{21},
\qquad
I_{EQ}=I_{EX}-G_{12}G_{22}^{-1}I_{IN}.
\]

`G_EQ` 是消去内部节点后端口看到的导纳，`I_EQ` 是内部 history sources 投影到端口后的等效注入。这个变换对给定离散线性拓扑是代数恒等式；Eq. (10) 同时保存了以后恢复 `V_IN` 的公式 [pdf:E09]（PDF 物理页 4，Eq. (9)–(14)）。

**4. 递归成立的原因。** 两个 PM 连接后仍可写成“外部节点 + 一个连接内部节点”的分块导纳，消去该连接节点后又得到同类型的 `(G_EQ, I_EQ)`。因此同一舒尔补可以从 PM 级重复到整条 PL，最终形成四物理节点的端口电路 [pdf:E10]（PDF 物理页 5，Fig. 7 与递归说明）。

**5. “无近似”的准确含义。** 论文所说的 nonapproximated（无近似）是指：在已经选定的梯形离散、线性变压器和两值开关 companion model 内，端口消元没有再引入平均化或单步端口近似。它不等于原始物理器件完全无近似；磁芯饱和、损耗和器件开关瞬态没有进入该推导 [pdf:E15]（PDF 物理页 2，Section II-A 的变压器假设）[pdf:E07]（PDF 物理页 3，两值开关模型）。

## § 7 — 实验设计与结论

**问题 1：等值模型能否跨越启动、闭锁、直流故障和恢复，而不只是在稳态吻合？**

实验把每条 PL 的级联 PM 数设为 3：`0–0.5 s` 完全闭锁，`0.5–1.0 s` 部分闭锁，`1.0–2.5 s` 解锁；`2.5 s` 发生 LVdc 极间短路，`0.005 s` 后完全闭锁；`2.6 s` 清除故障，`0.005 s` 后部分解锁，`3.0 s` 完全解锁。作者比较 detailed model（DM，详细模型）与 equivalent model（EM，等值模型）的电容电压、LVdc 电压和端口电流 [pdf:E16]（PDF 物理页 8，Accuracy Test、Fig. 13–14）。答案是：在该理想器件与控制配置下，启动、故障和恢复波形基本重合，全文报告的最大相对误差不超过 `2.34%`；恢复阶段各观测量的标注 MRE 也低于该上限 [pdf:E17]（PDF 物理页 9，Fig. 15 与 accuracy 结论）。

**问题 2：PM 数增加时，计算量是否从详细模型的快速膨胀变为近线性增长？**

实验在 PSCAD/EMTDC V4.6.1 中建立单相 DM 与 EM，隔离变压器频率为 `5 kHz`，仿真步长为 `1 μs`，PM 数从 3 增加到 61。DM 的 CPU 时间从 `13.69 s` 增至 `6626.38 s`，EM 从 `7.13 s` 增至 `94.06 s`；speedup factor（加速比）从 `1.92` 增至 `70.45` [pdf:E14]（PDF 物理页 9，Table II 与 Fig. 16）。答案是：在论文的软件和 CPU 上，EM 的时间随 PM 数近似线性，而 DM 的增长远快于线性；最大规模点达到约两个数量级的加速。

**问题 3：开关/变压器频率提高后，加速是否仍存在？**

固定 11 个 PM 和 `1 μs` 步长，将频率从 `1 kHz` 扫到 `10 kHz`。DM 的 CPU 时间从 `47.34 s` 增到 `153.11 s`，EM 保持在约 `18.81–19.34 s`，加速比从 `2.50` 提升到 `7.92`。作者把差异归因于 PSCAD 对详细开关模型进行 zero-crossing backtracking（过零回溯）和重算，而 EM 不承担这部分代价 [pdf:E18]（PDF 物理页 9，Table III 与频率扫描解释）。答案是：在固定时间步的该实现中，EM 对频率不敏感，DM 则随频率升高而变慢。

**问题 4：相对更快的既有 EM2，本文方法换来了什么、付出了什么？**

系统级 active power（有功功率）比较中，EM 和 EM2 的 MRE 分别是 `0.44%` 与 `0.52%`；但 EM2 的变压器内部电压出现一个时间步的延迟，论文认为这可能影响闭环控制 [pdf:E19]（PDF 物理页 10，Fig. 18–19 与 Accuracy 小节）。速度方面，61 个 PM 时 EM 为 `94.06 s`，EM2 为 `24.75 s`，后者约快 3.8 倍 [pdf:E20]（PDF 物理页 10，Table IV）。作者的结论是：EM2 更快，但依赖 strict port（严格端口）且牺牲内部精度；本文 EM 更全面，但不是最快 [pdf:E21]（PDF 物理页 10，Table V 与比较段落）。

**不得外推的范围：** 所有结果都是 PSCAD 软件 CPU 时间，没有硬实时 deadline、FPGA 时钟周期、片上资源、定点误差、通信延迟或真实 PET 硬件波形。CLLC 拓扑只有方程扩展示例，没有对应实验；“任意 PM 电路”是作者结论中的范围主张，不等于已覆盖任意非线性器件和任意连接方式 [pdf:E13]（PDF 物理页 7，CLLC 推导）[pdf:E04]（PDF 物理页 11，Conclusion）。

## § 8 — Take-aways

**5 句话：**

1. 论文把 PET EMT 的主要瓶颈定位为全局高阶导纳矩阵、微秒步长与大量开关事件的组合，而不是单个器件模型本身 [pdf:E02]（PDF 物理页 2，Introduction）。
2. 它先把隔离变压器离散成 two-port Norton 伴随模型，再用舒尔补消去 PM 内部节点，因此在选定离散模型内保留端口方程 [pdf:E06]（PDF 物理页 3，Eq. (1)–(4)）[pdf:E09]（PDF 物理页 4，Eq. (10)–(13)）。
3. two-port 等值在合并后保持同类型，使整条 PL 可以递归压缩为四节点接口，同时通过逆过程恢复内部状态 [pdf:E10]（PDF 物理页 5，Fig. 7）[pdf:E11]（PDF 物理页 6，Fig. 10）。
4. 在论文的 PSCAD 测试中，最大相对误差低于 `2.34%`，61 个 PM 时达到 `70.45×` 加速 [pdf:E17]（PDF 物理页 9，accuracy 结论）[pdf:E14]（PDF 物理页 9，Table II）。
5. 代价是模型仍依赖有限状态线性 companion circuit，且比带单步近似的 EM2 慢；FPGA、定点和真实硬件实时性没有验证 [pdf:E20]（PDF 物理页 10，Table IV）[pdf:E15]（PDF 物理页 2，线性变压器假设）[pdf:E14]（PDF 物理页 9，CPU 平台说明）。

**3 句话：**

1. 这篇论文不是用平均化删掉暂态，而是用 exact-for-the-discretized-model（对离散模型代数精确）的端口消元减小主 EMT 求解规模。
2. 方法成立的关键是 PM 等值在递归合并后仍保持 two-port 形式，并能反向恢复 history sources [pdf:E10]（PDF 物理页 5，Fig. 7）[pdf:E11]（PDF 物理页 6，inverse solution）。
3. 结果证明了理想化 PSCAD 模型中的精度和 CPU 标度，但没有证明非线性磁性、器件级换流细节或 FPGA 实时实现下仍保持同样优势 [pdf:E14]（PDF 物理页 9，CPU 测试平台）[pdf:E15]（PDF 物理页 2，线性变压器假设）。

**1 句话：** 论文用“局部精确消元、全局小接口、事后恢复内部状态”把 PET 的 EMT 计算从大矩阵问题改写成层级 two-port 组合问题。

## § 9 — 最脆弱的假设

最脆弱的假设是：**每个 PM 在一个时间步内都能落入有限个、线性且由 gate/blocking mode 唯一确定的 companion topology（伴随拓扑），因此对应的 `G_EQ` 与 `G22^{-1}` 可以预计算并复用。** 论文在正常工况中把 IGBT/diode 组建模为 `G_on/G_off` 两值电导，并用电容钳位论证 gate signal 决定导通状态；随后把 64 个正常状态和 4 个部分闭锁状态全部离线存储 [pdf:E07]（PDF 物理页 3，Fig. 5 与两值开关模型）[pdf:E08]（PDF 物理页 5，64-state precalculation）[pdf:E11]（PDF 物理页 6，68 ECs）。变压器推导还明确不考虑铜耗、铁耗和磁芯饱和 [pdf:E15]（PDF 物理页 2，Section II-A）。

如果这个假设不成立，例如励磁电感随磁通进入饱和、残磁使启动电流高度状态相关，或二极管导通取决于器件动态而不只由门极逻辑决定，那么预存的线性矩阵就不再描述当前电路。舒尔补本身仍然是正确的代数工具，但必须在每一步或每次非线性迭代中重新组装、分解 `G22`；论文最重要的速度来源会被削弱，所谓“无近似”也只能保留为对错误或过简物理模型的精确消元。

论文提供的支持是：3 个 PM/PL 的启动—故障—恢复波形与理想化 DM 接近，最大 MRE 不超过 `2.34%`，并且在 3–61 个 PM 的 CPU 扫描中表现出近线性时间增长 [pdf:E16]（PDF 物理页 8，Fig. 13–14）[pdf:E17]（PDF 物理页 9，Fig. 15）[pdf:E14]（PDF 物理页 9，Table II）。缺少的证据是：非线性 B-H 曲线、残磁与涌流、器件 reverse recovery（反向恢复）、dead time（死区）、参数离散、温度变化及硬件测量。因而最危险的不是“舒尔补是否正确”，而是“被舒尔补的 PM 模型是否仍属于可穷举的线性状态族”。

## § 10 — 最小复现实验

一周内最值得复现的不是整套闭环 PET，而是论文核心的两个可证伪命题：**端口消元在固定离散拓扑下是否数值等价，以及 PL 级计算是否随 PM 数近线性增长。**

**数据与模型：** 按 Fig. 4 重建一个 CHB-DAB PM companion circuit，变压器使用 Eq. (1)–(4)，电容使用梯形积分；可用 Table I 的系统量作尺度参考，但 `G_on/G_off` 等未完整报告的器件参数采用公开记录的、固定且可复现的归一化值。因为舒尔补等价性与具体参数无关，只要求 `G22` 可逆 [pdf:E06]（PDF 物理页 3，Eq. (1)–(4)）[pdf:E22]（PDF 物理页 8，Table I）。

**实现：**

1. 用 Python/NumPy、Julia 或 MATLAB 写一个 full nodal solver（完整节点求解器），对 64 个正常开关状态逐一生成 `9×9` PM 导纳；随机生成多组合法 history currents 和端口边界，直接解完整方程。
2. 按 Eq. (10)–(13) 生成 reduced solver（降阶求解器），求 `G_EQ、I_EQ`，再用逆公式恢复 `V_IN`；逐状态比较完整解与降阶解 [pdf:E09]（PDF 物理页 4，Eq. (10)–(13)）。
3. 将同一 PM 复制成 `M = 3、11、21、41、61` 的 ISOP 链，分别实现全局详细矩阵求解和 Fig. 7 的递归 two-port 合并；每个时间步完成前向合并、四节点外部求解和反向恢复 [pdf:E10]（PDF 物理页 5，Fig. 7）[pdf:E11]（PDF 物理页 6，Fig. 10）。
4. 用固定 `1 μs` 步长和预先生成的 `5 kHz` gate sequence 跑短时段，不复现复杂控制；记录每步 wall time、矩阵维度、分解次数和内存流量，并与论文 Table II 的趋势而非绝对秒数比较 [pdf:E14]（PDF 物理页 9，Table II 与测试设置）。

**测量与判据：** 若所有 64 个状态中，端口电流、内部节点电压和恢复后的支路量与完整解的归一化误差接近 floating-point roundoff（例如双精度下 `10^-9` 量级以内），且递归模型的主系统矩阵维度保持不变、总时间随 `M` 近线性，则核心代数 claim 得到支持。若在相同离散方程、相同参数和相同开关状态下仍出现系统性波形误差，或反向恢复/状态选择使运行时间明显超线性，则直接反驳核心实现。这个最小实验不验证论文的故障控制结论，但能最干净地验证其加速机制。

## § 11 — 最强反例设计

最强反例应只改变一个物理假设：**把线性励磁支路换成带残磁的 nonlinear B-H core（非线性 B-H 磁芯），其余拓扑、gate sequence、控制和时间步都保持不变。** 先用线性磁芯复现论文的启动—故障—恢复基线；再在相同 `2.5 s` 故障、`2.6 s` 清除和后续解锁序列中给每个高频变压器设置可控残余磁通，使解锁发生在最不利的磁通相位。详细模型每步用非线性磁化曲线更新 Jacobian（雅可比矩阵），而论文 EM 仍使用预计算的线性 `G_T` 和 PM 等值 [pdf:E16]（PDF 物理页 8，故障与恢复时序）[pdf:E15]（PDF 物理页 2，明确忽略 core saturation）。

测量 magnetizing current peak（励磁电流峰值）、变压器端电压、第一只 CHB 电容电压、LVdc 端口功率及控制器限幅/闭锁动作。若线性基线仍吻合，而加入残磁与饱和后 EM 漏掉涌流、内部电流峰值误差超过预设工程阈值，甚至给出不同的闭锁或恢复轨迹，就说明论文报告的精度主要来自 DM 与 EM 共享同一理想线性器件，而不是层级等值天然能覆盖强非线性。这个反例直接攻击预计算矩阵可复用性，也能区分“层级消元错误”与“底层物理模型过简”：前者在线性基线就会失败，后者只在非线性磁芯实验中暴露。

## § 12 — Follow-up Research Bet

**候选研究押注：把固定步长 Norton 快照改成可组合的 event-to-event two-port state-transition operator（事件到事件两端口状态转移算子），并把算子合并树直接映射到 FPGA。** 这是候选判断，不声称 novelty；输入包没有外部相关全文，最近工作比较只能依据本文对 average model、EM2 和 generalized Norton 方法的描述。

**新的研究问题。** 对每一个 PM 开关字 `s` 和相邻开关事件间隔 `τ`，能否不再每隔固定 `1 μs` 生成一次 `(G_EQ, I_EQ)`，而是构造一个同时推进端口量与内部动态状态的 affine operator（仿射算子）

\[
\mathcal T_s(\tau):\quad (x_k,u_{port})\mapsto(x_{k+1},y_{port}),
\]

并定义一种在 ISOP 连接下可结合的 two-port composition law（两端口组合律），使 `M` 个 PM 的事件区间算子可以沿二叉树合成为整条 PL 的状态转移？

**首次可能实现的能力。** 系统不再要求“所有 PM 在每个全局微步都更新一次”，而是按真实 gate event（门极事件）直接从一个事件推进到下一个事件，同时保留开关级时序、端口响应和可恢复的内部状态。对多 PM、相移 PWM 的 PET，只有发生事件的叶节点及其祖先算子需要更新；其余子树沿用当前区间算子。FPGA 上可把 PM 算子求值、同层两两组合和反向状态恢复做成固定流水树，评价对象从 CPU 总运行时间改为“每事件周期数、并发事件吞吐量、内部状态恢复带宽和端口误差”。这改变了状态表示、时间模型、硬件映射和评价对象，而不是在原方法外面加一个监测模块。

**机制与因果链。** 本文的 `G_T` 本来就显式依赖 `Δt`，说明每个固定开关状态对应一个参数化的离散 two-port；静态导纳与动态 history source 又已被分离，并且正常/部分闭锁状态只有有限个 [pdf:E06]（PDF 物理页 3，Eq. (2)–(4)）[pdf:E08]（PDF 物理页 5，static/dynamic split 与 64 states）[pdf:E11]（PDF 物理页 6，68 ECs）。下一步可以把“导纳快照 + history current”提升为“在任意区间 `τ` 上推进内部 state vector 的状态转移算子”，再利用本文已证明的 two-port 递归闭包，把算子而非单时刻导纳沿 Fig. 7 合并；反向算子对应 Fig. 10 的内部状态恢复 [pdf:E10]（PDF 物理页 5，Fig. 7）[pdf:E11]（PDF 物理页 6，Fig. 10）。如果该组合律成立，计算量将由“全局步数 × 全部 PM”转向“真实事件数 × 受影响树路径”，FPGA 树流水则把同层组合的并行性变成硬件吞吐。

**全文中的支持细节。** 论文已经显示，固定步长 EM 避免了详细模型的 zero-crossing backtracking，因此从 `1–10 kHz` 扫频时 CPU 时间几乎不变；但在固定频率下，EM 时间仍从 3 个 PM 的 `7.13 s` 线性涨到 61 个 PM 的 `94.06 s` [pdf:E18]（PDF 物理页 9，Table III）[pdf:E14]（PDF 物理页 9，Table II）。这暗示剩余主成本不是外部 `4×4` 求解，而是每步对所有 PM 进行状态注入、层级合并和逆恢复。事件区间算子正面改变这一成本结构，而不仅是把现有循环放到更快硬件上。

**最大收益与最大科学风险。** 最大收益是：在保持 switch-event resolution（开关事件分辨率）的同时，得到可综合到 FPGA 的拓扑层级算子，使大规模 PET EMT 可能从离线加速走向实时或超实时仿真，并能原生输出内部器件状态。最大风险有三个：外部网络电压在事件间并非常量，可能使局部算子无法独立闭合；多个 PM 的异步事件可能破坏简单结合律并引入全局同步；`τ` 连续变化会让算子库膨胀，若依赖插值又可能重新引入时间近似。非线性磁性和器件动态还会使有限状态仿射假设失效。

**最小区分实验。** 取 11 个 PM、相同 `1–10 kHz` 扫频和参数，建立三条基线：高分辨率 DM、论文的 `1 μs` fixed-step EM、事件区间算子原型。门极序列加入不规则 phase shift 与小幅 timing jitter，使事件间隔不再只有少数固定值；比较端口功率、一个变压器电流、一个电容电压、更新次数、CPU 每事件时间和 FPGA cycle count。再做交叉对照：在 CPU 上运行事件算子，在 FPGA 上运行原 fixed-step EM。若 CPU 事件算子已显著减少更新数并加速，而 FPGA fixed-step 仍受“每步遍历全部 PM”限制，则核心机制确实来自新的时间表示；若只有 FPGA 版本变快，则最强替代解释是普通硬件并行，而不是事件算子本身。

**与本文所述最近方法的实质区别。** average model 在周期或半周期上平均电流，改变的是物理分辨率并丢失暂态；EM2 用单时间步端口近似换速度，并要求 strict port [pdf:E02]（PDF 物理页 2，average model 局限）[pdf:E19]（PDF 物理页 10，EM2 的一步延迟）[pdf:E21]（PDF 物理页 10，strict-port 限制）。本文 EM 保留固定步长 companion equation，但每步重新选择/更新等值。候选方法既不周期平均，也不引入单步端口延迟，而是把数学对象从“某一时刻的导纳与历史源”改成“跨事件区间的状态转移 two-port”，并把实验对象从 CPU 软件总时间改为事件吞吐与内部状态可恢复性。

**Wild-card alternative：** 用主动多音端口激励和同步内部传感，直接辨识包含磁饱和与寄生耦合的 nonlinear two-port state atlas（非线性两端口状态图谱），再把图谱的组合规则而非电路导纳映射到层级求解器；这改变的是数据生成方式和状态表示，机制与事件算子不同。
