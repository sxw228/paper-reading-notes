# Electromagnetic Transient Simulation of Large-Scale Inverter-Based Resources With High-Granularity

**作者**：Jongchan Choi；Yaosuo Xue；Hong Wang。[pdf:E01]

**出处**：IEEE Open Access Journal of Power and Energy，Vol. 12。[pdf:E01]

**年份**：2025。[pdf:E01]

**DOI**：10.1109/OAJPE.2025.3615786。[pdf:E01]

**Zotero key**：UT6F8MTW

**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：这篇论文解决的是“怎样在不把大型 IBR plant（基于逆变器资源电站）压缩成单一等值机的前提下，把高粒度 EMT（electromagnetic transient，电磁暂态）仿真做到可计算”。** 传统聚合模型虽然便宜，却会抹掉 individual inverter、controller、transformer 与 collector system 之间的差异；论文特别指出，这会妨碍对 partial tripping、momentary cessation 以及大扰动后非一致响应的刻画。与此同时，逐台保留设备又意味着大量开关器件、控制状态和网络节点都要在很小的 EMT time step 上推进，计算量迅速失控。[pdf:E02]（PDF 物理页 1，Section I）

论文给出的代表性对象是一座包含 125 台 PV inverter、25 台 IBR unit transformer 和完整中压 collector network 的大型光伏电站；其核心目标不是再做一个更粗的等值模型，而是在保留 unit-level heterogeneity（单元级异质性）和 spatial electrical paths（空间电气路径）的同时缩短线性方程求解时间。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要有三层原因。第一，IBR 主导电网中的控制交互、开关谐波、不平衡故障和故障后恢复都发生在快时间尺度，phasor-domain 或单机等值模型可能遗漏关键动态。第二，电站内部不同 inverter 的控制参数、PLL、滤波器、线路阻抗和接入位置并不相同，局部差异可能汇聚成 plant-level 行为。第三，若高粒度 EMT 的计算成本高到无法用于批量工况、规划研究或硬件在环，就算模型更真实也缺乏工程可用性。论文因此把“物理粒度”和“线性代数结构”同时当作设计对象，而不是让两者互相牺牲。[pdf:E02]（PDF 物理页 1，Section I）

## § 2 — 前人工作与不足

**论文对相关工作的归纳是：已有加速方法很多，但它们往往优化了“大电网”或“单台 inverter”，没有同时闭合大型 IBR plant 内部的 individual units、unit transformers 与 collector system。** 论文列举了 multi-time stepping、EMT–phasor hybrid simulation、sparse matrix、Functional Mock-up Interface（FMI）co-simulation、ParaEMT/HPC、cloud deployment、GPU fine-grained decomposition，以及实现 microsecond-level real-time simulation 的 FPGA EMT modeling。作者认为，这些工作分别改善了时间尺度、并行性或硬件吞吐，却没有充分覆盖“数百台详细 inverter 经复杂 collector network 耦合”的完整对象。[pdf:E03]（PDF 物理页 2，Section I；这是论文对相关文献的总结，本卡未独立核验这些外部文献）

更直接的 baseline 是 aggregated single-inverter model 或 averaged model。它们把许多并联 inverter 合成少数等值单元，计算规模可控，但代价是看不到制造商参数差异、控制调谐差异、独立 switching behavior 和不同线路路径造成的响应分散。[pdf:E02]（PDF 物理页 1，Section I）

作者此前已经在 component level 使用 stiffness-based hybrid discretization、DAE clustering/aggregation 和 multi-order discretization；本论文把研究重心推进到 collector system 的大矩阵求解，并提出 matrix splitting 与 Schur complement 两条路径。[pdf:E04]（PDF 物理页 6，Fig. 8 与 Section III-A）论文还把“首次将这些算法用于大型 IBR plant 的高粒度 EMT、且不牺牲精度”列为贡献之一；由于本任务严格只使用源 PDF，这一 novelty 只能记作**论文直接声称**，不能当作已完成独立文献检索后的结论。[pdf:E05]（PDF 物理页 2，Contributions）

真正的不足不是“前人没有想到并行”这么简单，而是缺少一个与 IBR plant 物理层级相匹配的数值分解：individual inverter 需要保留独立状态，transformer 需要聚合局部电流，而 collector bus 又把多个 feeder 强耦合起来。若直接把所有离散方程装成一个 monolithic matrix，规模和 factorization 成本随 collector nodes 增长；若粗暴拆分，又可能在接口处引入时延和数值不稳定。本文的贡献正落在这个结构性矛盾上。

## § 3 — 重建作者的思考路径

**基于证据的合理重建如下。**

1. 先接受一个工程事实：为了看见 inverter 间非一致响应，不能继续把整座电站当成一台平均 inverter。于是模型必须分层保留 PV array、DC-DC stage、DC-AC inverter、LCL filter、controller、unit transformer、feeder 和 collector bus。[pdf:E05]（PDF 物理页 2，Section II 开头）
2. 再观察结构：每台 inverter 内部方程很多，但这些单元主要通过 unit transformer 和 feeder 接到共同 collector bus；也就是说，系统并非“任意稠密耦合”，而是大量局部模块围绕一个较小公共接口连接。Fig. 6 所示的 5 个 feeder、25 台 transformer、125 台 inverter 正好具备这种层级结构。[pdf:E06]（PDF 物理页 5，Fig. 6 与 Section II-D）
3. 把 collector line 的三相 PI-section DAE 离散后，得到 double-bordered block diagonal 形态的线性系统。真正的瓶颈不再是“有没有模型”，而是每个 time step 都要解一个 306×306 的 bordered matrix。[pdf:E07]（PDF 物理页 7，Eq. (13) 与 Section III-B.1）
4. 然后自然出现两个数值选择：其一，把边界耦合移到右端并用上一 time step 的接口状态近似，换取完全 block-diagonal 的 matrix splitting；其二，用 Schur complement 精确消元，保留当前时刻耦合，但多做一些 block inverse/matrix-vector operations。[pdf:E08]（PDF 物理页 7，Eq. (14) 与 Section III-B.2）[pdf:E09]（PDF 物理页 8，Eqs. (15)–(18) 与 Section III-B.3）
5. 最后用同一 plant model 比较 monolithic、delayed splitting 和 exact elimination，观察速度、精度、稳定性与 modularity 的交换关系，而不是只报告单一最优算法。[pdf:E10]（PDF 物理页 12，Table 3）

这条思考路径的关键，是先从物理拓扑找到 matrix structure，再选择与结构匹配的 solver；不是先选某个通用加速器，再把系统硬塞进去。

## § 4 — 核心 Intuition

把大型 IBR plant 看成许多可独立求解的 feeder/transformer/inverter blocks，而真正需要全局协调的只是较小的 collector-bus interface。[pdf:E07]（PDF 物理页 7，Eq. (13)）Matrix splitting 用一个 time-step delay 换取最强 modularity 和最高速度，Schur complement 则通过精确消元保留当前时刻耦合，以少量额外运算换取更好的 transient accuracy 与 stability。[pdf:E11]（PDF 物理页 8，Section III-B.2）[pdf:E09]（PDF 物理页 8，Section III-B.3）核心不是降低 EMT fidelity，而是重排同一组离散方程，让“最大一次线性求解”显著缩小。

## § 5 — 具体方法与完整 Pipeline

以论文的 125-inverter PV plant 为例，完整 pipeline 可以重建为以下步骤。

1. **建立 individual inverter EMT model。** 每个 PV inverter module 包含 PV array、DC-DC boost converter、DC-AC voltage-source inverter 和 LCL filter；Eq. (1)–(6)描述输入电容、boost inductor、DC link、inverter-side inductor、filter capacitor 和 grid-side inductor 的动态，并显式保留 switching states。[pdf:E12]（PDF 物理页 3，Fig. 2 与 Eqs. (1)–(6)）
2. **为每台 inverter 独立实例化 controller。** DC-DC 侧使用 MPPT 与 inductor-current control，DC-AC 侧使用 DC-link voltage、reactive power 和 dq current loops。论文允许 MPPT response、PLL configuration、loop bandwidth 和 tracking dynamics 在单元间不同；switching signal generation 与 full EMT circuit 使用 1 μs resolution，DC-DC control step 为 unit-specific 50–100 μs，DC-AC control step 为 100 μs。[pdf:E13]（PDF 物理页 4，Fig. 3 与 Section II-B）
3. **形成 IBR unit transformer subsystem。** 5 台独立 PV inverter 接到一台 480 V/34.5 kV unit transformer；每台 inverter 的 switching/control behavior 仍被分别追踪，再通过 transformer DAE 汇合到中压侧。[pdf:E14]（PDF 物理页 4，Figs. 4–5 与 Eqs. (7)–(8)）
4. **搭建 collector network。** 5 个 MV feeder 各接 5 台 unit transformer，总计 25 个 PV systems 与 125 台 inverter。每条电气路径不同；main line 为 60 m、lateral line 为 30 m，并用含相间 mutual coupling 的三相 PI-section model 表示。[pdf:E06]（PDF 物理页 5，Fig. 6 与 Section II-D）[pdf:E15]（PDF 物理页 5，Fig. 7 与 Eqs. (10)–(12)）
5. **按数值 stiffness 离散。** Inverter DAE 中 Eq. (2)、(4)–(6)用 backward Euler，Eq. (1)、(3)用 forward Euler；transformer/aggregated dynamics 与 collector-line equations 使用 second-order trapezoidal integration。论文把这种跨模块的一阶/二阶组合称为 hybrid 与 multi-order discretization。[pdf:E04]（PDF 物理页 6，Section III-A）
6. **装配 collector system 的线性系统。** 每个 EMT time step 形成 \(A x=b\)，其中 \(x\)是当前时刻 node voltages/branch currents，\(b\)包含前一时刻状态、source 和控制贡献。对论文网络，full collector matrix 为 306×306，并呈 double-bordered block diagonal structure。[pdf:E07]（PDF 物理页 7，Eq. (13)）
7. **选择求解配置。** SA（Single A Matrix）直接解 full matrix；MS（Matrix Splitting）把 5 个 feeder 与 collector bus 分成 6 个模块，将 border coupling 用上一 time step 的状态写入 \(\hat b\)；SC（Schur Complement）精确消去 feeder blocks，再解 reduced collector-bus equation。MS 与 SC 的最大 operated matrix 都从 306×306 降到 60×60。[pdf:E08]（PDF 物理页 7，Eq. (14)）[pdf:E09]（PDF 物理页 8，Eq. (18)及相邻正文）
8. **推进工况并输出波形。** 论文比较 normal operation、power-reference step 和 POI voltage depression 下的 inverter current、DC-link voltage、P/Q、transformer current、feeder current 与 POC current。[pdf:E16]（PDF 物理页 9，Section IV-A/C）

**实现边界。** Baseline 使用 PSCAD library；SA、MS、SC 使用 PSCAD/EMTDC 中的 Fortran scripts 与 custom components。[pdf:E16]（PDF 物理页 9，Section IV-A）论文没有报告 CPU/GPU/FPGA 型号、线程数、memory footprint、compiler optimization、floating-point precision 或真实 multi-processor schedule；虽然方法结构支持 feeder-level parallelism，但本文没有给出实际并行硬件执行结果。FPGA mapping 也未报告，文中的 FPGA 只属于 related work。[pdf:E03]（PDF 物理页 2，Section I）

Appendix 给出了 PI-line、transformer 与 inverter passive-component parameters，可用于重建 circuit；但 controller gains、unit-specific 参数分布、MS terminal capacitor 的具体数值和完整 source/reference traces 没有完整列出。[pdf:E17]（PDF 物理页 12，Table 4）[pdf:E18]（PDF 物理页 13，Tables 5–6 与 Appendix）此外，Abstract 写“52-bus collector system”，而 Fig. 6/Section IV 写“153-node”，Appendix 又写 51 条 MV feeder lines；这很可能是 bus、phase-node 与 line 的不同计数口径，但论文没有显式给出三者映射，复现者需要自行澄清。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E06]（PDF 物理页 5，Fig. 6）[pdf:E18]（PDF 物理页 13，Appendix）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有形式化数学，但重点不是提出新的连续时间物理方程，而是把已有 component DAE 组织成可分解的 discrete linear system。

**第一步：从三相线路 DAE 到离散网络方程。** 以 phase A 为例，Eq. (10)把本相与相间 mutual inductance/resistance 一起写入 branch-current dynamics；Eqs. (11)–(12)用 shunt capacitance 描述两端 node voltage dynamics。工程直觉是：每条 line segment 既有 series current state，也有两端的 capacitive current balance，因此离散后自然形成局部 block；不同 feeder 只在 collector bus 处产生 border coupling。[pdf:E15]（PDF 物理页 5，Eqs. (10)–(12)）

**第二步：形成 double-bordered system。** 论文的 Eq. (13)可抽象写成：

\[
\begin{bmatrix}
A_{11}&A_{12}&A_{13}&\cdots&A_{1n}\\
A_{21}&A_{22}&0&\cdots&0\\
A_{31}&0&A_{33}&\cdots&\vdots\\
\vdots&\vdots&\vdots&\ddots&0\\
A_{n1}&0&\cdots&0&A_{nn}
\end{bmatrix}
\begin{bmatrix}x_1\\x_2\\x_3\\\vdots\\x_n\end{bmatrix}
=
\begin{bmatrix}b_1\\b_2\\b_3\\\vdots\\b_n\end{bmatrix}.
\]

这里 \(x_1\)可理解为公共 collector-bus/interface states，\(x_i\;(i\ge 2)\)对应各 feeder block；\(A_{1i},A_{i1}\)就是跨接口耦合。论文实例的 full matrix 为 306×306。[pdf:E07]（PDF 物理页 7，Eq. (13)及相邻正文）

**第三步：matrix splitting。** 将 border terms 移到右端，并用上一 time step 的接口状态构造 \(\hat b_i\)，可得到：

\[
\operatorname{blkdiag}(A_{11},A_{22},\ldots,A_{nn})x=\hat b.
\]

这样每个 block 可独立 factorize/solve，最大 matrix 降为 60×60；代价是 feeder 与 bus 之间出现 single-time-step delay。[pdf:E08]（PDF 物理页 7，Eq. (14)及相邻正文）为抑制延迟状态的快速变化，论文建议在 subsystem terminals 加 small capacitors，但这实际上改变了被仿真的电路，并可能在 transient 中引入额外误差或振荡。[pdf:E11]（PDF 物理页 8，Section III-B.2）

**第四步：Schur complement。** 对 \(i\ge 2\)，先由 feeder equation 得到：

\[
x_i=A_{ii}^{-1}(b_i-A_{i1}x_1).
\]

代回第一行，可得与论文 Eq. (18)等价的 reduced interface equation：

\[
x_1=
\left(A_{11}-\sum_{i=2}^{n}A_{1i}A_{ii}^{-1}A_{i1}\right)^{-1}
\left(b_1-\sum_{i=2}^{n}A_{1i}A_{ii}^{-1}b_i\right).
\]

直觉上，每个 feeder 先被压缩成“它对 collector bus 的当前时刻等效响应”，再由 bus equation 统一协调；求出 \(x_1\)后，再 back-substitute 得到各 \(x_i\)。因此 SC 保留 current-step coupling，没有 MS 的 one-step delay，同时仍把最大 operated matrix 降至 60×60。[pdf:E09]（PDF 物理页 8，Eqs. (15)–(18)与相邻正文）

需要注意，论文把方法称为 multi-order discretization，并在概述中提到不同区域可采用不同 stepping；但正式算法展示的是 forward Euler、backward Euler 与 trapezoidal integration 的阶数/稳定性组合，没有给出动态 time-step controller、误差估计器或 step-size adaptation law。[pdf:E04]（PDF 物理页 6，Section III）因此更稳妥的理解是“跨模块混合离散阶数”，而不是已经验证的 adaptive multi-rate time stepping。

## § 7 — 实验设计与结论

**问题 1：算法能否显著缩短高粒度 EMT 的运行时间？ → 实验：** 在同一 125-inverter plant 上比较 Baseline、SA、MS、SC，并统计 0.25 s EMT simulation 的 wall-clock time。**答案：** Baseline 为 58 h，SA 为 2.58 h，MS 为 0.18 h，SC 为 0.21 h；相对 speed-up 分别为 1×、22.4×、326.4×、273.5×。[pdf:E19]（PDF 物理页 9，Tables 1–2）这强烈支持“缩小最大 linear solve 能显著降低运行时间”，但 absolute runtime 不能跨机器复用，因为硬件与编译环境未报告，而且 Baseline 是 PSCAD library、其余是 custom Fortran implementation，算法收益与实现收益没有完全解耦。[pdf:E16]（PDF 物理页 9，Section IV-A/B）

**问题 2：MS/SC 会不会破坏 steady-state fidelity？ → 实验：** 在 normal operation 下比较 inverter-side \(i_{L,pv}\)、\(v_{dc}\)、\(P_{inv}/Q_{inv}\)，以及 transformer、feeder、POC currents。**答案：** SA 与 SC trajectories 基本重合，MS 保持相同总体趋势但在 switching ripple 与局部波形上有小偏差。[pdf:E20]（PDF 物理页 10，Fig. 13 前正文与 Fig. 10 的解释）[pdf:E21]（PDF 物理页 11，Fig. 14）

**问题 3：动态功率指令下，接口处理方式是否影响 transient？ → 实验：** 在 \(t=0.25\,\text{s}\)把 PV inverter power reference 从 1.0 pu 降到 0.5 pu，观察 3 s 内的 inverter current、DC-link voltage、P/Q 与 plant currents。**答案：** SA 与 SC 维持接近的 transient response；MS 因 one-step delay 和 added capacitors 出现更明显的偏差与较慢 convergence。[pdf:E16]（PDF 物理页 9，Scenario 2 定义）[pdf:E22]（PDF 物理页 10，Fig. 11）[pdf:E21]（PDF 物理页 11，Fig. 15）

**问题 4：grid voltage depression 下是否仍稳定？ → 实验：** 在 \(t=0.25\,\text{s}\)将 POI voltage 从 1.0 pu 降到 0.8 pu，三周波后恢复。**答案：** 论文的总体结论是 SA 与 SC recovery 更稳定，MS 在 transient period 出现 oscillation；因此 MS 更适合 normal condition，SC 更适合要求 transient accuracy/stability 的场景。[pdf:E16]（PDF 物理页 9，Scenario 3 定义）[pdf:E22]（PDF 物理页 10，Fig. 12）[pdf:E21]（PDF 物理页 11，Fig. 16）[pdf:E23]（PDF 物理页 12，Discussion 与 Conclusion）

**问题 5：误差是否只是无结构的小扰动？ → 实验：** 作者画出多组 comparison error histograms，并指出分布近似对称、中心接近零、形状“Gaussian alike”。**答案：** 论文据此推断误差接近 random/white noise，认为没有更多 modeling information 可提取。[pdf:E20]（PDF 物理页 10，Fig. 13 与相邻正文）这个结论证据不足：deterministic solver error 即使直方图对称，也不等于时间上独立、更不等于 white noise；论文没有给 autocorrelation、power spectral density、phase-conditioned error 或正式 normality test。因此 Fig. 13最多支持“边际误差分布大致居中且没有明显单边偏置”，不能证明误差没有系统结构。

**不得外推的范围。** 实验只覆盖一个 radial collector topology、一个 plant scale、三类较温和工况；没有 protection action、partial tripping、controller saturation、asymmetric fault、topology switching、meshed collector、hardware-in-the-loop、real-time deadline 或 scaling curve。Table 3 的 speed/accuracy/stability/modularity 仍主要是单一案例上的定性归纳。[pdf:E10]（PDF 物理页 12，Table 3）

## § 8 — Take-aways

**5 句话。** 这篇论文证明了高粒度 IBR-plant EMT 的主要瓶颈可以从“设备数量太多”进一步定位为 collector-system linear solve 的结构问题。[pdf:E07]（PDF 物理页 7，Eq. (13)）它保留 125 台 inverter 的独立控制与 switching dynamics，并利用 feeder 围绕 collector bus 的 block structure 做数值分解。[pdf:E13]（PDF 物理页 4，Section II-B）SA 准确但仍受 full matrix 限制，MS 最快且最模块化但引入 one-step delay，SC 稍慢于 MS却避免该 delay。[pdf:E10]（PDF 物理页 12，Table 3）在论文平台上，MS 与 SC 把 0.25 s simulation 从 58 h 分别降到 0.18 h 与 0.21 h。[pdf:E19]（PDF 物理页 9，Table 2）最可信的结论是“结构化消元有效”，而不是“所有大型 IBR plant 都能稳定获得 273–326× speed-up”。

**3 句话。** 方法的本质是把 radial collector network 变成 small-interface block problem。最强证据是同一 plant 上 SA/MS/SC 的 runtime 与 transient waveform 对照。[pdf:E19]（PDF 物理页 9，Table 2）最大不确定性是硬件、实现细节、参数分布和 topology scaling 都没有充分披露。

**1 句话。** 这是一篇把高粒度 EMT 的物理层级成功映射到 block linear algebra 的工程论文，但其可推广性仍取决于 collector topology 是否持续拥有“小接口、大局部块”的结构。

## § 9 — 最脆弱的假设

**失败代价最大的假设是：大型 IBR plant 的 collector system 始终可以被分成多个近似独立 feeder blocks，并由一个相对小的公共接口耦合。** 论文实例是 5 个 radial feeder 汇聚到 collector bus，Eq. (13)因此形成 double-bordered block diagonal matrix；这正是 full 306×306 matrix 能被缩成最大 60×60 block 的根本原因。[pdf:E06]（PDF 物理页 5，Fig. 6）[pdf:E07]（PDF 物理页 7，Eq. (13)）

**基于证据的推断：** 若 collector 是 ring/mesh、存在多条 cross-feeder tie、动态开关重构、共享滤波支路或强 plant-level control coupling，那么 separator 会变大，Schur complement 可能产生 dense fill-in，MS 需要延迟的 border states 也会增加。此时 SC 的 reduced matrix 不再小，MS 的 interface error 也不再局限于单个 bus，论文的 speed-up 与 modularity 可能同时坍塌。SC 本身在数学上仍成立，但“只解 60×60”这一工程优势不再成立。[pdf:E08]（PDF 物理页 7，Eq. (14)）[pdf:E09]（PDF 物理页 8，Eq. (18)）

论文给出的支持证据只有一个典型 radial layout 和一次 306→60 的降维示例；没有改变 feeder 数、tie-line 数、separator size 或 sparsity pattern 的 scaling study，也没有展示 topology switching 后 factorization/communication cost 如何变化。[pdf:E10]（PDF 物理页 12，Table 3）因此，这个假设目前是“在所测案例中成立”，还不是对一般 large-scale IBR collector 的充分证明。

## § 10 — 最小复现实验

**一周内最值得复现的是 collector solver claim，而不是整套 125 台 switching inverter。** 这样能直接验证论文最核心、也最容易证伪的机制。

- **数据与网络：** 按 Appendix 重建 51 条三相 PI-section line、25 个 transformer connection points 与 5-feeder radial topology；line、transformer 和 inverter passive parameters 直接取 Tables 4–6。[pdf:E17]（PDF 物理页 12，Table 4）[pdf:E18]（PDF 物理页 13，Tables 5–6 与 Appendix）为节省时间，把每个 transformer 下游的 5 台 inverter 替换成可编程三相 Norton current source，其参考波形来自同一组预定义 P/Q trajectory。
- **实现：** 用 1 μs step 和 trapezoidal companion model实现 collector equations，分别写 SA、MS、SC。所有版本使用同一语言、同一 sparse/dense library、同一 compiler flags，并预先规定是否重用 factorization，避免把代码差异误当成算法差异。
- **工况：** 运行 normal condition、\(1.0\rightarrow0.5\) pu power-current command，以及 \(1.0\rightarrow0.8\) pu、持续三周波的 bus-voltage depression，分别对应论文三类场景。[pdf:E16]（PDF 物理页 9，Section IV-C）
- **测量：** 分开记录 matrix assembly、factorization、forward/back substitution、Schur formation 与 total wall time；以 SA 为 reference，计算 node-voltage/branch-current 的 normalized RMS error、maximum transient error、settling time、dominant error spectrum 和 memory footprint。
- **支持结果：** SC 在 current-step trajectory 上与 SA 保持到预先设定的 numerical tolerance，同时 collector solve 明显快于 SA；MS 更快，但其 transient error 与 one-step delay/terminal capacitance 呈可重复关系。
- **反驳结果：** SC 在相同数学模型与同一实现栈上没有明显速度优势，或在 voltage depression 中出现系统性相位/幅值偏差；又或者 MS 的误差与 delay/capacitor 无关，说明论文给出的机制解释不充分。

这个实验不应试图复现论文的 58 h、0.18 h 或 0.21 h 绝对时间，因为原文没有给硬件与软件栈；应验证相对计算分解和误差机制。[pdf:E19]（PDF 物理页 9，Table 2）

## § 11 — 最强反例设计

**最强反例是：保持设备数量不变，但把 radial collector 改成带 cross-ties 的 meshed collector，并在接口附近施加不平衡故障与 topology switching。** 具体做法是从 Fig. 6 的 5-feeder network 出发，在不同 feeder 末端之间加入两到三条 normally-open tie line；在 \(t=0.25\,\text{s}\)发生单相 voltage depression 时闭合其中一条 tie，再在故障清除后重新开断。设备、time step、line model 与 total node count 尽量保持一致，只改变 graph separator 与 dynamic coupling。[pdf:E06]（PDF 物理页 5，Fig. 6）[pdf:E15]（PDF 物理页 5，Fig. 7）

攻击逻辑有两层。第一，原 Eq. (13) 的 double-bordered structure 会被更多 off-diagonal blocks 打破；Schur complement 的 interface dimension 和 fill-in 增大，可能失去 306→60 的优势。第二，MS 若仍按原 6 个模块切分，就要在多条 tie 上传递 delayed states；快速故障和开关重构会让 one-step delay 产生可预测的 nonphysical energy exchange 或 oscillation，而 terminal capacitors 只能通过改变电路来掩盖问题。[pdf:E07]（PDF 物理页 7，Eq. (13)）[pdf:E11]（PDF 物理页 8，matrix-splitting limitation）

判据应同时看 accuracy 与 mechanism：若 SC speed-up 随 tie-line 数迅速下降，而 MS 在 tie closure 时相对 SA 出现增长的 phase error、spurious oscillation 或错误 settling state，就说明论文的主要收益来自“特定 radial sparsity”，而不是高粒度 IBR plant 的普遍可扩展性。反之，若在 separator 扩大和拓扑切换后 SC 仍维持显著加速且与 SA 一致，论文的 generality 才得到更强支持。[pdf:E09]（PDF 物理页 8，Schur complement derivation）

## § 12 — Follow-up Research Bet

**主押注（候选判断，不声称已完成 novelty 检索）：把每台 inverter 的 PWM carrier phase 与 control-sampling offset 从“不可控差异”变成 plant-level 可编程的时空编码变量，用高粒度 EMT 主动合成 POI waveform。**

新的研究问题是：在不增加额外 filter hardware、也不改变平均 P/Q 指令的情况下，能否联合设计 125 台 inverter 的 carrier phases、sampling offsets 与其在 collector electrical paths 上的分配，使 switching ripple 在 transformer、feeder 和 POI 处发生可控的 destructive interference，同时避免某些 LCL capacitor 或 semiconductor 承受局部峰值？这首次把高粒度 EMT 从“被动复现单元差异”推进到“主动设计电站内部的时空开关干涉场”。

因果链是明确的：每台 inverter 在 1 μs resolution 下产生独立 switching waveform；unit-specific control timing 决定局部相位与侧带；不同 60 m/30 m line paths、mutual coupling 和 transformer impedance 对这些高频分量施加不同 phase/amplitude transfer；若 carrier phase 与 electrical path assignment 协同设计，POI 处的谐波可以相消，而局部 device stress 仍受约束。[pdf:E13]（PDF 物理页 4，multi-rate control 与 1 μs switching）[pdf:E06]（PDF 物理页 5，spatially distinct collector paths）[pdf:E15]（PDF 物理页 5，mutually coupled PI-line model）Fig. 11–12 的局部放大已经显示，微小的 time-step/interface phase difference 会在 \(i_{L,pv}\) 与 \(v_{dc}\) ripple 上留下可辨差异，这说明该 simulator 至少具备观察 phase-level effects 的分辨率。[pdf:E22]（PDF 物理页 10，Figs. 11–12）

它改变了至少四个基本设计变量：研究目标从“更快求解”改为“plant-level waveform synthesis”；可控变量新增 carrier phase、sampling offset 和 inverter-to-path assignment；数据生成方式从被动运行固定工况改为主动扫相位/注入编码；硬件映射则可把每个 feeder block 放到独立 FPGA processing lane，并由确定性 global scheduler 维护跨 lane 的 sub-microsecond phase relation。当前论文没有 FPGA implementation，但其 6-block decomposition、60×60 reduced solve 和 1 μs step 为这种 algorithm–hardware–communication co-design 提供了直接结构基础。[pdf:E08]（PDF 物理页 7，six-subsystem matrix split）[pdf:E19]（PDF 物理页 9，runtime comparison）

最大研究收益是把大量 inverter 的“异质性”从仿真负担变成新的 physical degree of freedom：可能在不加硬件的情况下重塑 harmonic spectrum、降低 POI ripple，并揭示 topology-dependent coherent switching phenomena。最大科学风险是 carrier coherence 会被 PLL drift、clock jitter、manufacturer firmware 与 grid disturbances 快速冲散；优化得到的 phase code 也可能只对一个 topology 有效，或把 POI 谐波转移成局部 transformer/LCL stress。

最小区分实验使用完整 125-inverter model，比较三组 carrier schedule：全同步、保持同一 phase histogram 的随机分配、以及联合 topology 优化的 phase–path assignment。关键判别不是只看 THD 是否下降，而是把**同一组 phases 在不同 electrical paths 之间置换**：若结果随 phase–path pairing 显著变化，就支持“空间传播与相干干涉”机制；若只由 phase histogram 决定，则更可能只是普通 statistical averaging。测量 POI harmonic spectrum、各 transformer current ripple、LCL capacitor peak current 和 disturbance 后 phase coherence，并用 Fig. 14–16 所示 plant-level current channels作为观测层级。[pdf:E21]（PDF 物理页 11，Figs. 14–16）

在源 PDF 给出的最近工作边界内，本文和其引用的 FPGA work 都把目标放在 EMT accuracy、speed 或 real-time execution；这个押注把 scientific object 改为“可设计的分布式 switching interference”，不是给原 solver 加一个 wrapper，也不是在危险时切换模型。[pdf:E03]（PDF 物理页 2，related work）由于本任务不联网，这一差异只能作为候选判断。

**Wild-card alternative：** 用选定 inverter 注入正交 multisine probing，直接把每个 feeder 的 Schur boundary response 识别成可组合的 frequency-dependent operator，使高粒度 EMT 同时成为 plant-scale active system-identification instrument；其核心机制是主动激励与边界算子辨识，而不是 carrier-phase interference。
