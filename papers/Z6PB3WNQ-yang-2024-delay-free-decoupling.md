# A Delay-Free Decoupling Method for FPGA-Based Real-Time Simulation of Power Electronic Systems

**作者：** Yiming Yang, Jin Xu, Keyou Wang, Pan Wu, Zirun Li, Guojie Li  
**出处：** IEEE Journal of Emerging and Selected Topics in Industrial Electronics, Vol. 6, No. 1, pp. 391–402  
**年份：** 2025（online publication：2024-10-15）  
**DOI：** 10.1109/JESTIE.2024.3481270  
**Zotero key：** Z6PB3WNQ  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“FPGA 能不能做 EMT 实时仿真”，而是更具体的并行化瓶颈：大型级联电力电子系统为了追踪快速开关过程，需要很小的仿真步长；如果把全系统作为一个节点方程求解，矩阵维数和开关状态组合会迅速膨胀。传统把网络切开的办法又常依赖线路自然传播延时或人为插入延时；当接口电压、电流以高频变化时，延时线可能不够长，人为延时还会破坏数值稳定性或精度。作者因此追问：能否不引入一个时间步的接口延时，同时把系统切成可在 FPGA 上并行计算的小子模块？论文摘要把目标概括为在保持数值稳定性的同时降低矩阵乘法维数和开关状态组合数，并在 250 ns 步长下验证级联电力电子系统。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，因为硬实时仿真有两条同时成立的约束：每个时间步必须在截止时间前完成，而且波形误差不能因分区而失真。论文引用的一个 FPGA 稀疏矩阵例子仅线性方程求解就需 2.6 μs，而高频电力电子系统往往要求整个单步循环在 1 μs 或更短时间内完成；同时，网状电力电子电路的矩阵未必足够稀疏，LU factorization 又具有串行依赖。[pdf:E02]（PDF 物理页 2，Introduction 左栏）因此，真正价值不是一般意义上的“加速”，而是把原本的全局耦合计算改造成更多局部、固定结构、可展开的矩阵—向量运算，同时保留同一步内的电气耦合。

## § 2 — 前人工作与不足

**相关文献中的已有结论（仅按本文的 related-work 叙述）：** Thevenin/Norton 等值模型已经用于 MMC、级联 DAB 和级联 PET，通过消去内部节点降低网络规模；稀疏矩阵算法以减少节点导纳矩阵存储和加速 LU factorization 为主；delay-based partitioning 利用自然传播延时或人工延时；delay-free 路线则包括基于 diakoptics 的 MATE、node splitting 和 bordered-block-diagonal 方法。[pdf:E01][pdf:E02]（PDF 物理页 1–2，Introduction）这些是本文对前人工作的归纳，本卡没有联网核验每篇参考文献的全文。

作者认为上述路线各自卡在不同位置。等值建模能消节点，却不必然解决高阶状态向量和大量开关组合；稀疏矩阵方法的 LU 分解难以形成很短的纯流水线，而且 PE 网状结构可能不够稀疏；delay-based 方法在高频接口上会受延时长度、稳定性和精度限制；既有 delay-free 方法虽然避免了延时，却仍有较多串行步骤和中间变量，不够贴合 FPGA 的并行数据通路。[pdf:E02]（PDF 物理页 2，Introduction 与三点贡献）

本文改变的关键假设是：接口耦合不必通过“上一时间步的远端量”传递，也不必在每个时间步完整执行传统 EMTP 的节点注入、节点电压、支路电流串行链。它把接口电流当作子模块的扩展输入，把子模块压缩成离散 state-space map，再把边界电流拆成各子模块可独立贡献的分段；这样只保留分段向量求和这一条串行归并路径。[pdf:E03][pdf:E09]（PDF 物理页 2，Fig. 1；物理页 5，Fig. 4 及相邻正文）

## § 3 — 重建作者的思考路径

下面是**基于论文证据的合理推断**，不是作者逐句陈述的发明过程。

第一步，从工程失败模式出发：人工延时使接口在时间上错位，而高频 PE 接口恰恰对这种错位敏感。因此应保留同一时间步内的联立约束，转向 delay-free diakoptics。第二步，直接套用传统 delay-free 分区仍会产生较长的全局求解链，所以要问哪些量才是真正跨子模块共享的最小集合。串联接口只有一个独立 mesh current，并联接口有 (N-1) 个独立 port currents；于是边界电流可以成为系统间唯一的耦合坐标。[pdf:E03]（PDF 物理页 2，Fig. 1 与 Section II-A）

第三步，把每个固定开关状态下的 RLC 子模块视为线性网络。由 superposition，把节点电压、支路电流分成“内部源贡献”和“外部边界源贡献”；内部部分只依赖本子模块的历史源和独立源，外部部分只依赖边界电流，两部分可以并行计算。[pdf:E05]（PDF 物理页 3，Fig. 2 与 Eq. (3)）第四步，把传统 EMTP 的多级计算消元成以历史电流 (I_h) 为 state、独立源 (I_s) 和边界电流 (I_u) 为 input 的预计算矩阵映射，避免运行时求逆。[pdf:E06][pdf:E07]（PDF 物理页 4，Eq. (4)–(14)）

最后一步是 FPGA 视角下的重排：如果总边界电流能写成各子模块局部状态的贡献之和，每个计算核就可同时算本模块内部量和自己的边界贡献，之后只做一次树形加法，再并行算外部贡献。作者由此把“网络分区问题”转写成“局部矩阵乘法 + 一次向量 reduction”的硬件数据流问题。[pdf:E08][pdf:E10]（PDF 物理页 5，Fig. 3 与 Eq. (15)–(17)；物理页 6，FPGA loop 分析）

## § 4 — 核心 Intuition

不要让子模块通过延迟后的端口波形彼此通信，而是在当前时间步联立求出少量边界电流。再利用线性叠加，把每个子模块对边界电流的贡献先在本地算好，最后只做一次向量求和；边界量得到后，各子模块的电压、电流与历史状态仍可并行更新。[pdf:E05][pdf:E08]（PDF 物理页 3，Eq. (3)；物理页 5，Fig. 3 与 Eq. (15)–(17)）

让旧方法失效的核心是高频接口不容忍人为时间错位；让本文方法奏效的核心则是每个开关状态下子模块的线性离散映射可预计算，并且全局耦合能压缩为低维边界电流的同一步求和。

## § 5 — 具体方法与完整 Pipeline

以三个 ISOP-DAB 子模块为例，输入是当前开关信号、上一步历史电流 (I_h^{t-Delta t})、CPU 给出的独立源 (I_s^t)，输出是关注的节点电压、支路电流和下一步历史电流。论文的实际平台由 Intel i7-3610QE 嵌入式 CPU 与 Xilinx Kintex-7 XC7K410T FPGA 组成：控制侧步长 100 μs，网络侧步长 250 ns，PWM 频率 20 kHz；FPGA 变量使用 (\langle\pm24,14\rangle) fixed-point，一次 25b × 18b 乘法用一个 DSP，而该 fixed-point 乘法需要两个 DSP。[pdf:E09]（PDF 物理页 5，Fig. 4、Section III-A）

完整 pipeline 如下。

1. **离线初始化。** 对每类子模块按开关状态建立节点/支路数据，形成并预存 (A_{in},B_{in},C_{in},A_{ex},B_{ex},C_{ex},D_i) 等系数矩阵。相同结构、相同参数的子模块可以共享开关状态数据，作者据此主张实际存储量还可低于逐模块保存。[pdf:E04][pdf:E07][pdf:E09]（PDF 物理页 3，Eq. (2) 后正文；物理页 4，Eq. (9)–(14)；物理页 5，Fig. 4）
2. **读取本步输入。** 每个核取得开关状态，用它选择预存矩阵；把上一时间步的 (I_h) 与本步 (I_s) 组合成内部输入。[pdf:E10]（PDF 物理页 6，Step 0–1）
3. **全并行计算内部量与局部边界贡献。** 每个子模块核同时计算 (V_{n,in},I_{b,in},I_{h,in}) 以及分段边界量 (I_{u,i})。矩阵—向量乘法完全展开，乘法并行，内部加法用树形 reduction。[pdf:E10]（PDF 物理页 6，Step 1 与 Fig. 7 说明）
4. **唯一全局归并。** 把各核的 (I_{u,i}) 相加得到完整边界向量 (I_u)。论文把这一简单向量加法称为整个循环唯一的串行步骤。[pdf:E08][pdf:E09]（PDF 物理页 5，Eq. (15)、Fig. 3–4 与相邻正文）
5. **全并行计算外部贡献。** 每个核用同一个 (I_u) 计算 (V_{n,ex},I_{b,ex},I_{h,ex})。[pdf:E07][pdf:E10]（PDF 物理页 4，Eq. (12)–(14)；物理页 6，Step 3）
6. **合成与交接。** 内外两部分相加得到完整 (V_n,I_b,I_h)；(V_n,I_b) 送 CPU 或 I/O，(I_h) 写入寄存器作为下一步 state。[pdf:E10][pdf:E11]（PDF 物理页 6，Step 4；物理页 7，Fig. 6）

事件处理在本文中体现为“每步先按控制信号更新开关状态，再选择对应预存矩阵”，不是独立的零交叉定位或变步长事件求解器。[pdf:E09] 数值表示只报告了上述 fixed-point 格式；论文没有报告 rounding mode、overflow policy、量化误差预算、综合频率、端到端 worst-case execution time 或跨 FPGA 通信。

## § 6 — 核心数学推导（无形式化数学则跳过）

先把每个子模块 (i) 的节点方程与接口 KVL 约束写成一个鞍点式 block system。用紧凑记法，它等价于

\[
Y_{n,i}V_{n,i}-Q_iI_u=I_{inj,i},\qquad
\sum_{i=1}^{N}Q_i^T V_{n,i}=0.
\]

其中 (Y_{n,i}) 是子模块节点导纳矩阵，(Q_i) 是边界电流 incidence matrix；串联接口的 (I_u) 阶数为 1，并联接口为 (N-1)。消去各 (V_{n,i}) 后，论文 Eq. (2) 得到

\[
I_u=-\left(\sum_iQ_i^TY_{n,i}^{-1}Q_i\right)^{-1}
\left(\sum_iQ_i^TY_{n,i}^{-1}I_{inj,i}\right),
\]

再由 (V_{n,i}=Y_{n,i}^{-1}(I_{inj,i}+Q_iI_u)) 回代。[pdf:E04]（PDF 物理页 3，Eq. (1)–(2)）物理意义是：括号中的小矩阵只描述接口“看到”的等效阻抗；全系统节点电压不必一起求解，只需先求低维边界电流，再回到子模块。

资源收益来自两个不同的缩减。第一，矩阵乘法维数由全系统降为若干子模块；第二，若开关采用 binary resistance model，非分区系统需面对 (2^{\sum_i m_i}) 个组合，而分区后是 (\sum_i2^{m_i})。论文还指出同构同参数子模块可共享数据。[pdf:E04]（PDF 物理页 3，Eq. (2) 后正文）

接着对每个子模块做离散化。论文用 trapezoidal rule 把支路写成

\[
I_b^{t+\Delta t}=Y_bV_b^{t+\Delta t}+I_h^{t+\Delta t}+I_s^{t+\Delta t},
\quad
I_h^{t+\Delta t}=\alpha Y_bV_b^t+\beta I_b^t.
\]

电阻、感抗、电容的 (Y_b,\alpha,\beta) 分别是 ((R,0,0))、((\Delta t/(2L),1,1))、((2C/\Delta t,-1,-1))。结合 (V_b=M^TV_n) 与 (I_{inj}=-M(I_h+I_s))，可把传统逐级 EMTP 计算压缩成 state-space map。[pdf:E06]（PDF 物理页 4，Eq. (4)–(8)）

内部源部分为

\[
V_{n,in}^t=A_{in}(I_h^t+I_s^t),\quad
I_{b,in}^t=B_{in}(I_h^t+I_s^t),\quad
I_{h,in}^t=C_{in}(I_h^{t-\Delta t}+I_s^{t-\Delta t}),
\]

外部源部分为

\[
V_{n,ex}^t=A_{ex}I_u^t,\quad
I_{b,ex}^t=B_{ex}I_u^t,\quad
I_{h,ex}^t=C_{ex}I_u^{t-\Delta t}.
\]

Eq. (14) 把两部分相加，得到完整输出与下一步 state。所有系数随开关状态变化，因此作者在运行前为不同开关状态预计算并存储矩阵，运行时只选择矩阵而不求逆。[pdf:E07]（PDF 物理页 4，Eq. (9)–(14) 及相邻正文）

最后，把边界电流写成分段和：(I_u^t=\sum_iI_{u,i}^t)，局部贡献由 (D_i) 与本地 (I_{h,i}^t+I_{s,i}^t) 决定，(D_i) 包含接口等效矩阵的逆与 (Q_i^TA_{in,i})。[pdf:E08]（PDF 物理页 5，Eq. (15)–(17)）这里有一个必须保留的原文问题：PDF 的 Eq. (16) 在 (I_{u,i}^t) 右侧又印了对 (i=1\ldots N) 的求和，这与“每个 (I_{u,i}) 是独立局部段”、Fig. 3 以及 Eq. (15) 再求一次总和的叙述不一致。**基于证据的判断：** 这很可能是指标或排版错误，但本卡不替作者静默修正式子；复现前应从推导重新确认 Eq. (16) 的正确索引。

## § 7 — 实验设计与结论

**问题 1：delay-free 分区是否真的比 delay-based 分区稳定且准确？** 作者用 MMC-PET 做数值稳定性验证。仿真先令输出电压为 4.2 kV，0.075 s 时给定降至 2.6 kV，0.15 s 时负载电阻改为 8 Ω；在 bridge-arm inductor 处分区时，delay-based 曲线数值发散，而本文方法与 PSCAD 的输出电压、变压器原边电流和原边电压相合，文中报告相对误差小于 2%。[pdf:E11][pdf:E12]（PDF 物理页 7，Section IV-A；物理页 8，Fig. 9–10）

**问题 2：硬实时平台能否保留高频内部波形？** MMC-PET 与 ISOP-DAB 都在 250 ns 网络步长的平台上比较 real-time 和 offline 波形。MMC-PET 的 transformer voltage/current 以 20 kHz 变化；ISOP-DAB 的 input current 和 transformer voltage 也以 20 kHz 变化，作者据波形重合认为端口和子模块内部的高频瞬态可被实时模拟。[pdf:E09][pdf:E13][pdf:E14]（PDF 物理页 5，平台参数；物理页 9，Fig. 11 与相邻正文；物理页 10，Fig. 16）这证明的是给定两类拓扑、给定工况下的波形一致性，不是对任意开关事件或数值刚性的普遍证明。

**问题 3：方法能否覆盖串联与并联两类接口？** ISOP-DAB 同时含 serial 和 parallel interfaces。输出给定先为 900 V，0.075 s 降到 600 V，0.15 s 施加 0.1 Ω 输出短路。delay-based 方法虽能跟随稳态输出电压，却在电流和瞬态波形上出现明显失真；本文方法相对 PSCAD 的最大相对误差约 0.2%。[pdf:E12][pdf:E13][pdf:E14]（PDF 物理页 8，Section IV-B 与 Fig. 14；物理页 10，Fig. 15）作者据此把结果解释为对两端口子模块及两类接口的适用性证据。

**问题 4：资源压缩是否转化为更大可实时仿真的规模？** 对 MMC-PET，本文方法最大为 72 个子模块，nondecoupled 为 32，MATE 为 48，即分别为 2.25 倍和 1.5 倍。[pdf:E11][pdf:E13]（PDF 物理页 7，效率结论；物理页 9，Fig. 12）对 ISOP-DAB，本文方法最大为 70，nondecoupled 为 12，MATE 为 15，即 5.84 倍和 4.67 倍。[pdf:E13][pdf:E14]（PDF 物理页 9–10，Fig. 17 与相邻正文）作者把差异归因于消除 injection current、branch voltage 等中间量，以及只保留关心观测量对应的系数矩阵行列；主要瓶颈是 logic slices 与 DSP，BRAM 相对较少。[pdf:E14]

实验边界也很清楚：两张参数表都只用 3 个子模块验证波形，switching frequency 均为 20 kHz，simulation time step 均为 250 ns；MMC-PET 与 ISOP-DAB 的具体电气参数见 Table I–II。[pdf:E15]（PDF 物理页 11，Appendix，Table I–II）资源“最大规模”来自单一 XC7K410T 平台的资源曲线，不等同于跨器件可迁移的性能定律；论文也未给出统计重复、综合时序裕量、端到端 WCET 或与实物功率级量测的闭环比较。

## § 8 — Take-aways

**5 句话。** ① 本文把 delay-free diakoptics 改写成适合 FPGA 的局部 state-space maps。② 串联/并联接口的电气影响被压缩为同一步内求得的边界电流，不引入人工延时。③ superposition 让内部源贡献与外部边界源贡献分开并行，运行时矩阵求逆被预计算矩阵选择取代。④ 各子模块先独立产生边界电流分段，唯一全局归并是向量加法。⑤ 在 XC7K410T、250 ns 步长、20 kHz 开关的 MMC-PET 与 ISOP-DAB 案例中，作者报告了对 PSCAD 的较小误差和相对 nondecoupled/MATE 更大的可仿真子模块数。[pdf:E07][pdf:E08][pdf:E13][pdf:E14]

**3 句话。** 这项工作的本质不是简单网络切块，而是把切块后的代数依赖重新排列成 FPGA 能完全展开的固定矩阵数据流。实验说明该排列在两个级联 PET 拓扑上可以避免 delay-based 接口失真，并显著改善资源随子模块数增长的速度。它的可信范围仍主要限于按开关状态线性、可预计算的 RLC/理想开关模型和单一 FPGA 平台。

**1 句话。** 用当前步的低维边界电流联立取代延迟端口量，再把其求解拆成局部贡献加一次 reduction，是本文同时获得稳定性与 FPGA 并行度的核心。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在一个开关状态和固定步长内，每个子模块可被线性、时不变的离散 map 精确表示，因而 superposition 成立且所有系数矩阵可以预先计算。** 这不是普通实现细节，而是 Eq. (3) 的内外源分解、Eq. (9)–(14) 的矩阵压缩以及“运行时只选矩阵、不求逆”的共同前提。[pdf:E05][pdf:E07]（PDF 物理页 3–4）一旦模型含明显 state-dependent 元件，例如磁饱和、温度/电压相关的半导体导通参数或 nonlinear capacitance，(Y_n) 和离散 map 会随连续状态变化；预存的有限开关状态矩阵不再足够，superposition 也不再直接成立。此时若加入迭代求解，本文宣称的短、固定、几乎全并行循环可能同时失去精度与实时性。

论文给出的支持是：在两个由离散开关状态、RLC 元件和变压器构成的级联 PET 模型上，250 ns 步长的 fixed-point FPGA 结果与 PSCAD 波形接近，并且 delay-based 对照在所选高频接口上失稳或失真。[pdf:E12][pdf:E14][pdf:E15] 但它没有给出含 state-dependent nonlinear devices 的实验，也没有报告矩阵参数失配、磁饱和或器件级寄生下的结果。因此，“不限制 topology structure 或 modeling time step”的结论是作者原文声称，[pdf:E15]（PDF 物理页 11，Conclusion）不能直接外推为“不限制元件非线性或刚性”。

## § 10 — 最小复现实验

一周内最值得复现的是“分区本身在同一离散模型下不引入明显误差，并且保持短的依赖链”，不必先复刻完整平台。

1. 按 Table II 建立 3-submodule ISOP-DAB：1.2 kV 输入、20 Ω 负载、1800 μF 输出电容、2:1 变比、160 μH leakage inductance、20 kHz、250 ns。[pdf:E15]（PDF 物理页 11，Table II）
2. 用同一 trapezoidal discretization 和 double precision 实现两条路径：monolithic nodal EMTP，以及按 Eq. (1)–(17) 的 delay-free 分区。先独立重推 Eq. (16) 索引，不照抄疑似排版错误。[pdf:E04][pdf:E06][pdf:E07][pdf:E08]
3. 复现论文工况：输出给定 900 V，在 0.075 s 改为 600 V，在 0.15 s 施加 0.1 Ω 短路；记录输出电压、输入电流、变压器原边电压、边界电流和每步残差。[pdf:E12][pdf:E14]
4. **预注册判据（本卡提出，不是论文阈值）：** 若分区与 monolithic 路径在稳态和两次瞬态窗口的最大相对误差均不超过 0.5%，且接口 KVL residual 不随时间增长，则支持“代数重排未显著改变解”；若误差系统性超过 0.5%、Eq. (16) 无法得到一致实现，或 residual 累积，则反驳该最小 claim。0.5% 取在作者对该案例报告的约 0.2% 之上，给独立实现留出余量。[pdf:E12]
5. 若尚有时间，把 3、6、12 个子模块的核心矩阵—向量路径综合到 XC7K410T 或同族器件，只比较 critical path、DSP、LUT/logic 与 BRAM 的增长趋势；这一步验证硬件映射，但不把综合估算冒充 250 ns 的真实硬实时闭环。

## § 11 — 最强反例设计

最强反例不是再换一种输出阶跃，而是在边界附近加入会破坏“固定线性子模块 map”的物理元件：把 ISOP-DAB 变压器的 leakage/magnetizing branch 改为带明显饱和的 state-dependent inductance，并加入 voltage-dependent switch output capacitance；再安排多个子模块在相邻 250 ns 步内换相。基线采用每步 Newton iteration 的 monolithic EMT 解，攻击对象采用论文的预存开关状态矩阵与一次边界 reduction，二者使用同一容差和相同时间网格。

这个反例直接检验因果链：非线性使 (Y_n(x)) 随 state 改变 → 预存 (A/B/C/D) 不再表示当前局部电路 → 内外源 superposition 与一次边界求和不能给出同一步自洽解 → 要么出现边界 KVL residual、相位/峰值误差或数值发散，要么必须加入迭代并失去固定低延迟数据流。[pdf:E04][pdf:E05][pdf:E07][pdf:E08] 如果攻击版本仍能在强饱和和集中换相时维持与 monolithic 解一致，并保持 250 ns 内的固定循环，论文核心机制将得到远强于原实验的支持；反之，即使原两组波形仍可复现，也会推翻它对“各种 PE devices”的宽泛适用暗示。[pdf:E15]

## § 12 — Follow-up Research Bet

**主 idea：面向 switching-event spacetime 的异步无延时边界求解。** 新问题是：能否不再让所有子模块共享一个 250 ns 全局时间格，而把每个子模块表示为“从一个 switching instant 到下一个 switching instant 的解析/高阶离散 state transition”，再只在接口相关事件的 spacetime wavefront 上联立边界电流？这将首次使同一 FPGA 上的不同子模块按各自开关频率和局部电气时间尺度推进，同时仍在发生耦合的物理时刻满足 delay-free interface constraint，而不是用人工延时或固定倍率 multirate interpolation 交换旧值。

核心机制的因果链是：论文已经把子模块压成由 (I_h,I_s,I_u) 驱动的离散 map，且全局依赖只剩低维 (I_u) reduction；[pdf:E07][pdf:E08]（PDF 物理页 4–5，Eq. (9)–(17)）若把 fixed-step map 改成带时间戳的 interval transition，并把边界变量从“某一全局 tick 的向量”改成“事件区间上的 piecewise-polynomial port trajectory”，那么无事件的子模块可以跨越多个短 tick，一组相关接口事件则形成需要共同求解的 wavefront。FPGA 不再按“一个子模块一个每 tick 必跑的核”映射，而按 event batch 部署 transition engines 与 boundary-reduction fabric。基本设计变量由统一 time step、每 tick 全模块执行、瞬时边界向量，改为 local interval、event batch、端口轨迹阶次和 wavefront 宽度；这至少改变了时间表示、数据生成方式、硬件映射与评价对象。

论文特异依据有两组。方法侧，开关状态变化只要求选择对应的预存矩阵，state 由历史电流承载，边界耦合又已被压缩成一次低维求和，这提供了 interval transition 和事件 wavefront 的结构入口。[pdf:E07][pdf:E09] 实验侧，两类案例都用 20 kHz switching 却统一以 250 ns 运行，且本文方法的最大规模主要受 state-vector order、logic slices 和 DSP 增长限制，而非 BRAM；[pdf:E09][pdf:E14][pdf:E15]（PDF 物理页 5、10–11）这提示“每 tick 重算所有模块”可能是下一层可消除的工作量，而不只是继续压缩存储。

成功后的最大收益，是把可实时规模从“每个固定 tick 可容纳多少子模块”改写为“单位物理时间内实际发生多少相互耦合的 switching events”，从而让频率异质、局部静止的大型 PE 网络获得新的 FPGA 尺度律。最大科学风险是：边界电流在事件之间并非低阶可表示，多个接口事件会形成近乎全局同步的 dense wavefront；此时异步表示既不能减少计算，也可能因事件排序和轨迹插值引入新的误差。

最小区分实验用 6 个 ISOP-DAB 子模块，故意设置互不整除的 switching frequencies 与相位，并保持论文相同的 RLC 参数量级。比较三者：全局 250 ns 本文基线、普通 multirate 端口插值、event-spacetime 求解。关键观测是端口 KVL residual、峰值/相位误差、每毫秒实际执行的 matrix-vector 次数和 FPGA critical wavefront 宽度。只有 event-spacetime 方法在相同误差下显著少算，而且优势随“事件稀疏度”而不是人为设定的 local step 比例变化，才能把核心机制与“只是普通 multirate interpolation”这一最强替代解释区分开。

**候选判断：** 本卡未补做相关全文检索，因此不声称 novelty 已闭合。它与本文最近的 delay-free 方法在 problem 上从“固定步长资源压缩”改为“事件密度决定的实时容量”，在 mechanism 上从每 tick reduction 改为 event wavefront 联立，在 representation 上从瞬时 state vector 改为带时间戳的 interval transition/port trajectory，在 experimental object 上从同步级联 PET 改为频率异质、事件稀疏的耦合网络。

**Wild-card alternative：** 用电气拓扑的 symmetry quotient 把大量同构子模块投影成少数公共 mode，再只对参数离散与开关相位造成的 symmetry-breaking modes 做 FPGA state evolution，以“群对称模态数”而非子模块数决定计算规模；这是不同于事件时间表示的状态空间压缩机制，同样只是待检索、待证伪的候选判断。
