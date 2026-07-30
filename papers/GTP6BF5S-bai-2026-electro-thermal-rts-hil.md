# Multilayer Device-Level Electro-Thermal Real-Time Simulation and Multipurpose HIL Testing of Power Electronics Converters

- 作者：Hao Bai, Xinyang Li, Jiaxin Tang, Zhen Yao, Ning Mao, Rui Ma, Wentao Jiang, Yang Zhou, Shengrong Zhuo, Fei Gao
- 出处：IEEE Transactions on Power Electronics, Vol. 41, No. 6, June 2026
- DOI：10.1109/TPEL.2025.3650187
- Zotero key：GTP6BF5S

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是一个很具体的工程矛盾：power electronics converter 的 HIL 需要在每个真实时钟步内完成计算，但 SiC MOSFET 的开关瞬态只有纳秒量级，若同时求解器件非线性、损耗、结温与温度敏感电参数，计算量很快超过实时预算。传统 system-level RTS 通常只保留开通、关断两个静态状态，足以测试控制器，却看不到 Miller plateau、反向恢复、过冲、振荡、开关损耗和结温；而论文希望让同一套 HIL 同时承担控制、热管理、器件保护和故障策略验证。作者把这项任务表述为“在保持计算效率的同时，联合处理 electro-thermal coupling 与 semiconductor switching characteristics”，并在 interleaved bidirectional DC–DC converter 上做 FPGA/HIL 验证。[pdf:E01]（PDF 物理页 1，题名与 Abstract）

关键之处不是把整个高精度器件模型硬塞进每一个实时步，而是重新定义“并发”：对控制和热状态真正需要逐步闭环的部分保持实时；对昂贵的器件瞬态以较慢但确定的节拍重建，再把新得到的开关能量、器件应力和温度相关参数回灌到实时层。论文的正式框架确实把 electrical model、power-loss module、thermal model 和 electrical-parameter update module 闭成一条双向链，而不是把温度当作仿真结束后的离线后处理。[pdf:E03]（PDF 物理页 3，Fig. 1）

这项工作的价值因此有两层。第一层是模型价值：在有限 FPGA 资源上保留 system-level 实时闭环，同时提供可观察的 device-level switching waveform。第二层是测试价值：HIL 的输出从电压、电流扩展到损耗、结温和器件应力，使早期控制设计能够讨论“性能—热安全”的权衡。需要从一开始保留的边界是：论文并没有证明每一个器件瞬态都实时求解；Layer 2 明确是 slower-than-real-time。

## § 2 — 前人工作与不足

论文给出的技术谱系不是简单的“以前没有 device-level RTS”。已有工作包括：需要迭代求解的 IGBT/diode 非线性模型；把时间步降到 50 ns 的 piecewise-linear IGBT/diode 模型，但难以表达高频振荡；依赖离线波形按工作点缩放的 curve-fitting 模型，其泛化能力受限；25 ns 的 adaptive curve fitting；用 system-level 结果回算最高 5 ns 分辨率波形的 two-level quasi-transient RTS；以及用 neural network 生成瞬态波形的 data-driven RTS。[pdf:E02]（PDF 物理页 2，Introduction 对 [14]–[22] 的综述）

这些方法“不够”的原因至少有三种，并不能混成一句“没有考虑热效应”。

1. **数值预算不够。** 直接非线性迭代需要微秒级仿真时间步或更长的求解时间，无法追上 SiC 的纳秒级开关事件。
2. **简化会丢失关键形状。** 单段线性化能提速，却可能丢掉由寄生参数和状态切换造成的过冲、反向恢复与高频振荡；而纯 curve fitting 又容易把训练或测量过的工作点当成普遍规律。
3. **测试输出维度不够。** 传统 controller-HIL 主要校验闭环电气行为；若实时模型不给出可信的损耗、结温与器件应力，thermal management、device protection、health monitoring 等策略只能在别的工具或更晚的开发阶段验证。作者把这项缺口明确列为研究动机。[pdf:E02]（PDF 物理页 2，Introduction 下半页）

论文相对这些 prior methods 的实质推进，是把“多速率器件瞬态”“电—热双向反馈”“FPGA 映射”和“多用途 HIL”接成一条可运行链路。它不是证明某个全新的半导体物理模型，而是对求解时序、piecewise approximation 和 HIL 信息流作系统级组合。

## § 3 — 重建作者的思考路径

下面是**基于证据的合理推断**，不是作者逐字给出的发明史。

第一步，先接受一个事实：控制状态、热状态与开关瞬态不处在同一时间尺度。控制与电感、电容状态必须按真实时间连续推进，结温变化更慢；但单次开关瞬态虽短，却决定开关能量和器件峰值应力。于是没必要要求所有状态都用同一个最小时间步计算。

第二步，把输出需求拆开。Layer 1 负责实时的 converter electrical/thermal state；Layer 2 只在选定工作点重建短暂的 device waveform，并返回 switching-energy LUT 与温度相关器件参数。Fig. 3 和 Fig. 4 已显示，两层通过 \(I_L\)、\(V_{CC}\)、\(T_j\) 与 \(LUT_E\) 交换信息，而 Layer 2 的真实执行时间可以跨越多个 switching period。[pdf:E05]（PDF 物理页 4，Fig. 3、Fig. 4、Eq. (3)–(4)）

第三步，发现“分层”只放宽了时限，并没有消除非线性求解。作者因而继续利用开关过程本身的物理分段：cutoff、反向恢复/换流、linear/saturation 三类区间对应不同的等效电路和边界条件。把一个全局非线性问题改写成若干局部线性状态空间问题，既减少迭代，又暴露出 FPGA 可并行执行的矩阵运算。[pdf:E07]（PDF 物理页 5，Fig. 5–7、Eq. (7)）

第四步，用 LUT 处理仍然随 \(v_{gs}\)、\(v_{ds}\)、\(T_j\) 变化的通道电流和结电容，并把结温对阈值、电阻等 TSEP 的影响反馈到电气模型。这样，快速瞬态不必每周期重算，但其损耗结果仍能改变之后的温度与电气参数。[pdf:E08]（PDF 物理页 6，Fig. 8–10、Eq. (8)–(10)）

这条思路真正冒险的地方，是默认相邻两次 Layer 2 更新之间，工作点变化不会快到使刚得到的瞬态与损耗失去代表性。作者用“有意义的工作点变化通常需要若干 switching cycle”来解释异步更新的合理性，并要求 monitoring interval 大于完成一次瞬态重建的总时间。[pdf:E06]（PDF 物理页 4，Eq. (5)–(6) 后的 timing example 与说明）

## § 4 — 核心 Intuition

不要让最昂贵的 SiC switching-transient solver 阻塞每一个真实时钟步：实时层先维持 converter 的电气—热闭环，器件层在后台按代表性工作点重建瞬态。再把器件层得到的 switching loss、stress 和温度相关参数反馈给实时层，使“慢更新的高分辨率局部真相”持续校正“快更新的系统级状态”。为了让器件层适合 FPGA，按物理工作区间切换线性子模型，而不是每步迭代求一个全局非线性解。

## § 5 — 具体方法与完整 Pipeline

以论文的两相 interleaved bidirectional converter 为例，输入是拓扑、PWM、上一步电感电流/电容电压、器件结温以及当前 \(V_{CC}\)、\(I_L\)。选用器件为 Wolfspeed C3M0060065J；case-study 基本工况包含 \(V_{in}=128\text{ V}\)、\(I_{load}=6\text{ A}\)、\(C_{out}=440\,\mu\text{F}\)、两只 \(800\,\mu\text{H}\) 电感、\(50\text{ kHz}\) switching frequency、0.6 duty cycle、\(10\,\Omega\) gate resistance 和 \(-5/16\text{ V}\) gate voltage。[pdf:E09]（PDF 物理页 7，Fig. 12、Table II）

完整 pipeline 如下。

1. **Layer 1 读取历史状态并判定拓扑状态。** PWM 与电感电流共同决定每个 half bridge 的导通状态；通过插入电感电流的 delay 解耦两个 half bridge，再更新电感电流与电容电压。Layer 1 在 10 MHz single-cycle timed loop 中执行，RTS time-step 为 100 ns。[pdf:E10]（PDF 物理页 7，Section IV-B、IV-C）
2. **在实时层计算损耗与温度。** 导通电流、稳态电压/电流和开关状态进入 loss module；conduction loss 与 LUT 给出的 switching loss 驱动一维 Cauer 或 Foster thermal network；算出的 \(T_j\) 再更新 \(R_{on}\)、\(V_{th}\) 等 TSEP。[pdf:E04]（PDF 物理页 3，Fig. 2、Eq. (1)–(2) 及相邻正文）
3. **把代表性工作点送入 Layer 2。** Layer 2 接收 \(T_j\)、\(V_{CC}\)、\(I_L\)，先确定开关阶段，再取得 \(i_{mos}\)、\(C_{ds}\)、\(C_{dg}\) 对应的 LUT 系数。其控制流不是一套固定矩阵：Stage 1、2、3 使用不同状态更新路径。[pdf:E11]（PDF 物理页 8，Fig. 13、Fig. 14）
4. **求解分段器件模型。** 半桥换流被分为三段：Stage 1 为 MOSFET cutoff、二极管导通；Stage 2 为 MOSFET 进入 linear region 且发生 diode reverse recovery；Stage 3 为二极管截止、MOSFET 位于 linear/saturation 区。状态为 \(v_{gs},v_{ds},i_{ds},i_{Lrr}\)，分段边界由 \(v_{gs}\)、\(V_{th}\)、\(i_d\)、\(K v_{Lrr}\) 与 \(V_{ds\_off}\) 判断。[pdf:E07]（PDF 物理页 5，Fig. 7、Eq. (7) 及 stage criteria 正文）
5. **在段内线性化非线性器件特性。** \(i_{mos}\) 用 \(v_{gs}\)-\(v_{ds}\) 二维 LUT 和双线性插值表示；\(C_{ds}\)、\(C_{dg}\) 的 voltage-dependent curve 按区间视为常数。作者明确指出，这个 solver 以 half-bridge commutation unit 为基本单元，难以直接处理不能分解为 half bridge 的 switched-capacitor converter 或 current-source inverter。[pdf:E08]（PDF 物理页 6，Eq. (8)–(10)）；[pdf:E09]（PDF 物理页 7，Fig. 12 下方的适用边界）
6. **以较慢节拍重建波形并回写。** 实际实现中，Layer 2 的 simulation time-step 是 0.25 ns，但每步执行需 5 μs；100 ns 瞬态含 400 个模型步，共需 2000 μs。在 50 kHz 工况下，器件波形每 100 个 switching cycle 才更新一次。[pdf:E10]（PDF 物理页 7，Section IV-C）
7. **输出给 multipurpose HIL。** HIL 不只输出电压、电流，还输出 loss、junction temperature 与 stress，供 closed-loop control、thermal management、device protection、fault prediction、health monitoring 和 fault-tolerant control 使用；实物平台包含 FPGA board、DSP controller、real-signal interface、host computer 和 oscilloscope。[pdf:E14]（PDF 物理页 9，Fig. 19、Fig. 20）

硬件资源不是附带细节，而是方法是否落地的约束。XC7Z100 实现使用 32,452/54,650 slices、95,082/277,400 LUTs、690/755 Block RAMs 和 1,012/2,020 DSP48s；其中 Block RAM 已到 91.4%，说明增加 LUT 维度、更多器件实例或更密分段会很快触到容量上限。[pdf:E09]（PDF 物理页 7，Table I）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有形式化模型，但核心不是证明一个定理，而是把物理量转换为 FPGA 能按固定节拍更新的状态方程。

**第一层：从电流与开关能量得到热源。** 导通损耗为

\[
P_{\mathrm{con}}=I_{\mathrm{on}}^2R_{\mathrm{on}},
\]

开关能量 LUT 则通过

\[
P_{\mathrm{sw}}=\frac{LUT_E(V,I)}{T_{\mathrm{on}}\ \text{or}\ T_{\mathrm{off}}}
\]

均匀摊入选定的 turn-on/turn-off duration。直觉上，前式是熟悉的 \(I^2R\)，后式则把“一次开关损失多少焦耳”换成这段时间内的平均瓦特数，供 thermal network 积分。[pdf:E04]（PDF 物理页 3，Eq. (1)、Eq. (2)）

**第二层：明确两个时间尺度怎样嵌套。** 若 switching period 为 \(T_{sw}\)，Layer 1 取

\[
T_{\mathrm{sys}}=h_{\mathrm{sys}}=\frac{1}{m}T_{sw}.
\]

Layer 2 的模型步长和真实执行时间分别为

\[
h_{\mathrm{dev}}=\frac{1}{k}h_{\mathrm{sys}},\qquad
T_{\mathrm{dev}}=n h_{\mathrm{dev}}.
\]

这里 \(k\) 决定器件波形分辨率，\(n\) 表示硬件算一步比模型时间慢多少倍。[pdf:E05]（PDF 物理页 4，Eq. (3)、Eq. (4)）若一个瞬态需要 \(p\) 个器件步，则

\[
T_{\mathrm{dev}}=\frac{n}{mk}T_{sw},\qquad
T_{\mathrm{tot}}=pT_{\mathrm{dev}}=\frac{np}{mk}T_{sw}=NT_{sw}.
\]

论文的解释例取 \(T_{sw}=10\,\mu s\)、\(m=200\)、\(k=50\)、\(p=100\)、\(n=5000\)，得到 \(T_{\mathrm{tot}}=50T_{sw}\)，即每 50 个 switching cycle 才能产生一次新波形。[pdf:E06]（PDF 物理页 4，Eq. (5)、Eq. (6) 与 timing example）这组数用于解释一般框架；case-study 的实际 FPGA 参数则是每 100 个 switching cycle 更新一次，二者不要混为同一实验设置。

**第三层：把全局非线性改为分段状态空间。** 每一阶段都写成

\[
\dot{x}=Ax+Bu,\qquad
x=[v_{gs},v_{ds},i_{ds},i_{Lrr}]^T,
\]

但 \(A,B\) 随 Stage 1–3 改变。[pdf:E07]（PDF 物理页 5，Eq. (7)）通道电流先按阈值分段：

\[
i_{\mathrm{mos}}=
\begin{cases}
0,&v_{gs}\le V_{th},\\
LUT(v_{ds},v_{gs}),&v_{gs}>V_{th}.
\end{cases}
\]

在每个 LUT 平面内，再用一阶展开

\[
i_{\mathrm{mos}}=k_1+k_2v_{gs}+k_3v_{ds}
\]

代替原非线性 surface；\(C_{ds}=f(v_{ds})\)、\(C_{dg}=g(v_{dg})\) 也按电压区间 piecewise constant。[pdf:E08]（PDF 物理页 6，Eq. (8)–(10)、Fig. 10）

**第四层：把连续状态方程变为离散硬件更新。** 对统一形式 \(\dot X=AX+Bu\) 使用 backward Euler，得到

\[
X^{n+1}=(I-hA)^{-1}X^n+h(I-hA)^{-1}Bu.
\]

[pdf:E18]（PDF 物理页 12，Eq. (A17)、Eq. (A18)）工程直觉是：每个固定步先选对 stage 与相应矩阵，再求一个小规模线性系统；最大的 state matrix 只有四维，作者用基于 Gaussian elimination 的并行矩阵求逆来适配 FPGA。这里的代价从“迭代全局非线性”变成“stage 判定 + LUT 读取 + 小矩阵线性代数”。

## § 7 — 实验设计与结论

**问题 1：Layer 1 能否保持 system-level 电气实时精度？ →** 作者在 IBC open-loop boost startup 中比较 FPGA 与 manufacturer LTspice reference model，并改变电压工况。**→ 答案：** 论文报告电压、电流的平均稳态误差均小于 1%。[pdf:E12]（PDF 物理页 8，Fig. 15 及下方 system-level result）

**问题 2：分段 SiC 模型能否重建器件瞬态？ →** 在 \(V_{CC}=400\text{ V}, I_L=10\text{ A}\) 下比较 \(v_{gs},i_{ds},v_{ds}\) 的 turn-on/turn-off waveform；再在 \(V_{CC}=100\)–\(600\text{ V}\)、\(I_L=10\)–\(30\text{ A}\) 的 30 个均匀工作点上统计 timing 与 switching-energy error。**→ 答案：** FPGA 波形保留了 current overshoot、Miller plateau 与 turn-off oscillation；平均相对误差分别为 turn-on delay 9.48%、rise time 6.55%、turn-off delay 2.08%、fall time 0.02%、diode reverse-recovery time 0.28%，switching-energy error 在全部工况中 turn-on 低于 3%、turn-off 低于 8%。[pdf:E12]（PDF 物理页 8，Fig. 16）；[pdf:E13]（PDF 物理页 9，Fig. 17 与相邻报告数字）

**问题 3：损耗—热模型是否跟得上工作点变化？ →** 在 \(50^\circ\text{C}\) ambient、理想 case cooling 条件下，交替改变 \(V_{CC}\) 与 \(I_L\)，比较 FPGA 与 LTspice 的 junction-temperature response。**→ 答案：** 论文报告 steady-state temperature deviation 约 \(0.1^\circ\text{C}\)。[pdf:E13]（PDF 物理页 9，Fig. 18 与 Thermal Simulation Results）这支持“给定 thermal network 与理想散热边界时实现一致”，不能直接外推到真实散热器、气流和界面热阻。

**问题 4：多用途 HIL 的电气与热结果能否对上低压实物？ →** closed-loop test 使用 \(24\text{ V}\) 输入、\(48\text{ V}\) reference、\(1\text{ A}\) load、\(50\text{ kHz}\) switching frequency 与 \(25^\circ\text{C}\) ambient，执行 48↔72 V reference step 和 1↔3 A load step；用红外相机测 case temperature。**→ 答案：** 三个正常工况的 HIL/实物 case-temperature relative error 为 0.9%、1.7%、2.6%，电气 step response 趋势也相近。[pdf:E15]（PDF 物理页 10，Fig. 22–24、Table III）

**问题 5：故障状态下是否仍能给出电—热信息？ →** 禁用 \(S_{22}\)，使 converter 只剩一相工作，并比较 HIL 与实物。**→ 答案：** 两者都出现小的瞬态波动和更大 ripple；健康相 \(S_{21}\) 的 static case temperature 为 HIL \(35.4^\circ\text{C}\)、实物 \(37.1^\circ\text{C}\)，relative error 约 4.6%。[pdf:E16]（PDF 物理页 11，Fig. 25、Fig. 26）

**问题 6：热信息能否参与 controller design？ →** 在 \(128\text{ V}\) 输入、\(270\text{ V}\) 输出、\(5\text{ A}\) load、\(50\text{ kHz}\) baseline 和假定 \(50^\circ\text{C}\) ambient 下，分别提高或降低 switching frequency。**→ 答案：** 热余量较大时提高到 100 kHz；负载从 5 A 增至 8 A 时，将 switching frequency 降到 25 kHz，论文报告由负载增加造成的温升减少 \(14.4^\circ\text{C}\)。[pdf:E17]（PDF 物理页 11，Fig. 27 与相邻正文）

最重要的外推限制是：实物闭环和 fault-injection validation 只覆盖 48–72 V 输出；270 V active-thermal-control test 只在 HIL 中执行，并无同电压实物对照。[pdf:E14]（PDF 物理页 9，Fig. 20 后实验范围说明）因此，论文证明了“低压实物校准后的 HIL 能开展一个高压策略演示”，没有证明高压器件应力与结温在实物上达到同样误差。

## § 8 — Take-aways

**5 句话：**

1. 这项工作用多速率分层而不是单一超小时间步，缓解 SiC device-level electro-thermal RTS 的精度—速度冲突。
2. Layer 1 保持 100 ns 的 system-level 实时闭环，Layer 2 以 0.25 ns 模型步重建瞬态，但实际只每 100 个 switching cycle 更新一次。[pdf:E10]
3. 三阶段等效电路、\(i_{mos}\)/capacitance LUT 与 backward Euler，把非线性器件问题变成适合 FPGA 的小矩阵更新。[pdf:E08] [pdf:E18]
4. LTspice 对比、低压实物闭环与 fault injection 说明该链路能同时给出电气和热信息，但高压 active-thermal-control 仍只有 HIL 演示。[pdf:E13] [pdf:E14]
5. 论文最值得继承的是“不同信息按其物理时间尺度更新”的系统设计，而不是把 slower-than-real-time Layer 2 误称为逐周期的完整 device-level real-time simulation。

**3 句话：**

1. 快层保证控制闭环，慢层重建昂贵的开关瞬态，并用损耗与 TSEP 回馈修正快层。
2. 分段线性化在 30 个器件工作点和一个 IBC 平台上给出有竞争力的误差，但 Block RAM 已用到 91.4%，且物理验证范围集中在低压。[pdf:E09] [pdf:E13]
3. 真正未解决的是：当工作点在两次器件层更新之间快速变化时，旧瞬态和旧 loss LUT 是否还可信。

**1 句话：**

这是一套把“实时系统状态”和“异步高分辨率器件快照”闭环耦合起来的可落地 FPGA/HIL 架构，而不是所有 SiC 瞬态都在真实时间内连续求解。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**在相邻两次 Layer 2 更新之间，影响 switching waveform 和 loss 的工作点变化足够慢，因此最近一次重建的器件瞬态可以代表接下来的若干 switching cycle。**

这不是一个措辞问题，而是两层能够同时成立的条件。若必须每个 cycle 都重建，Layer 2 的 2000 μs 计算时间便无法服务 50 kHz converter；若仍按每 100 cycle 更新，而 \(I_L\)、\(V_{CC}\)、\(T_j\)、换流模式或寄生振荡在窗口内快速变化，Layer 1 使用的 \(LUT_E\) 就会滞后。此时控制电压仍可能看起来正确，但 peak \(v_{ds}\)、peak \(i_{ds}\)、累计 switching energy 与 junction-temperature trajectory 会遗漏最危险的中间事件。[pdf:E06]（PDF 物理页 4，monitoring interval 条件）；[pdf:E10]（PDF 物理页 7，实际每 100 cycle 更新）

论文为该假设给出的证据，是 startup、稳态工作点网格、较慢温度 step、closed-loop step 和一次单开关失效后的对比；故障实验显示 HIL 与实物的稳态与宏观瞬态趋势相近。[pdf:E13] [pdf:E16] 但它没有报告“更新窗口内连续发生多次换流模式变化”的误差，也没有给出在 event-dense transient 下 switching-energy/peak-stress 的 worst-case bound。故现有证据支持被测工况，不足以证明这个时间尺度假设对所有 intended HIL fault/thermal-management use case 都成立。

## § 10 — 最小复现实验

一周内最值得复现的不是整套双层 FPGA/HIL，而是最能决定方法成败的 **half-bridge Layer 2 switching-energy accuracy**。

- **数据与参考：** 取得 Wolfspeed C3M0060065J datasheet 与 manufacturer LTspice model；按论文 Fig. 5–10 建立同一 half-bridge commutation unit。论文没有公开完整 LUT 网格、全部寄生参数和 thermal-network 参数，因此要把“按 datasheet/厂家模型重新提取”明确记录为复现差异，不能假装是 byte-exact reproduction。[pdf:E07] [pdf:E08]
- **实现：** 在 MATLAB、Julia 或 Python 中实现 Stage 1–3 判定、\(i_{mos}\) bilinear LUT、\(C_{ds}/C_{dg}\) piecewise-constant LUT 和 Eq. (A18) backward Euler；仿真步长取 0.25 ns。先不实现 Layer 1、thermal network 与 FPGA code generation。
- **工况：** 复用论文的 \(V_{CC}=100\)–\(600\text{ V}\)、\(I_L=10\)–\(30\text{ A}\) 30-point grid，并至少保留 \(400\text{ V},10\text{ A}\) 波形作为人工检查样本。[pdf:E12] [pdf:E13]
- **测量：** 对 LTspice reference 与分段模型比较 turn-on/turn-off switching energy、delay/rise/fall/reverse-recovery time，并确认 overshoot、Miller plateau、turn-off oscillation 是否同时存在；另外记录 stage switching 是否产生 chatter 或数值不连续。
- **判据：** 若重新提取的模型仍能在大多数网格上接近论文的 turn-on energy <3%、turn-off energy <8% envelope，且关键波形形状不靠事后滤波才出现，就支持“piecewise solver 保留主要器件信息”的 claim；若在网格内部而非仅边界工况就频繁超过 10%，或 energy 看似准确但 peak/oscillation 明显错误，就反驳该 claim 的可复现性。论文报告的 timing/energy 基准见 Fig. 17。[pdf:E13]

这个实验不会证明 real-time FPGA resource、thermal accuracy 或 multipurpose HIL；它只用最小成本检验最关键的器件模型近似是否站得住。

## § 11 — 最强反例设计

最强反例应在作者声称适用的 half-bridge converter 内部攻击时间尺度假设，而不是直接换成作者已经承认不适用的 switched-capacitor topology。

设计一个 event-dense 工况：让 IBC 在接近 discontinuous-conduction boundary 的位置运行，在一个 100-cycle Layer 2 更新窗口内依次触发 load step、PWM mode transition、单相开关失效与恢复，使 \(I_L\)、commutation direction 和器件温度相关参数连续改变。用高带宽实物测量或经过校准的 offline device-level model 作为参考，同时运行论文式“每 100 cycle 更新一次”的 HIL。逐 cycle 积分 switching energy，并比较窗口内最大 \(v_{ds}\)、最大 \(i_{ds}\)、累计损耗、\(T_j\) 峰值和保护动作时刻。

反例的预测是：HIL 的低频输出电压仍会因 controller regulation 而快速恢复，造成“系统行为正确”的表象；但 Layer 2 只重建窗口端点附近的一个代表性 transient，因而漏掉窗口内部的最坏 switching stress。论文现有 fault test 主要展示输出/输入响应、ripple 与稳态 case temperature，并没有给出 fault edge 附近逐 cycle switching-energy/stress 的实物对照。[pdf:E16]（PDF 物理页 11，Fig. 25、Fig. 26）低压实物验证也不能排除高压下由寄生参数放大的过冲误差，因为 270 V case 没有物理平台对照。[pdf:E14]

若该实验显示所有窗口内 peak 与累计损耗仍被准确捕获，或者保护判据在完整工作区间从不依赖遗漏的中间 transient，那么这个反例失败；反之，即使平均温度和输出电压仍吻合，也足以推翻“异步器件层可普遍支撑 device protection/fault prediction”的较强解释。

## § 12 — Follow-up Research Idea

在 power electronics 领域，高影响工作通常不只要求一个更复杂的模型，还要求明确的物理机制、可实现的实时计算、真实硬件时序/资源证据，以及跨工况的实验验证。基于第 9 节的缺口，一个值得研究的候选方向是：

**event-triggered、带误差证书的 device-layer RTS：不再固定每 \(N\) 个 switching cycle 生成一张器件快照，而由实时层持续估计“当前 LUT/瞬态模型仍然有效”的误差上界；当工作点创新量、换流模式或预测 stress 接近边界时才触发新的高分辨率求解，并在结果返回前输出保守的 loss/stress envelope。**

（a）**未满足需求。** 当前固定更新周期把计算负担变得可控，却不能保证窗口内部没有漏掉 peak stress；而 device protection 与 fault prediction 恰恰关心最坏瞬间，不只关心平均波形。[pdf:E06] [pdf:E10]

（b）**研究价值。** 如果能在固定 FPGA deadline 和资源预算内给出“未漏过危险 switching event”的可检验上界，评价目标就从平均精度提升为 safety-relevant fidelity。这比单纯再缩短 time-step 更贴合 HIL 的工程用途。

（c）**相邻领域工具。** 可借鉴 event-triggered estimation、set-membership/reachability analysis、real-time scheduling 与 anytime computation：快层维护 operating-point reachable set，慢层返回局部 surrogate 及可信域，scheduler 根据 bound 而不是固定计数决定是否重算。

（d）**第一个证伪实验。** 直接使用 §11 的 event-dense 序列；若 bound 经常宽到无法指导保护，或为了收紧 bound 而频繁触发 Layer 2、导致 deadline miss/Block RAM 超预算，则该想法被证伪。现有实现的 Block RAM 已使用 91.4%，因此资源不是可以忽略的次要指标。[pdf:E09]

（e）**与本文的实质区别。** 本文解决的是“如何让一个慢器件模型周期性校正实时层”；候选方向改写为“如何证明慢器件模型在未更新期间仍安全可用，并只在证书失效时重算”。它改变了调度目标和输出语义，不是简单增加第三层或换一块更快 FPGA。

以上是**候选研究想法**。这里只依据本文及其参考文献重建问题，没有完成面向 event-triggered EMT/HIL、reachability-certified surrogate 与 device-stress bounding 的系统相关工作检索，因此不声称 novelty。
