# Wide Voltage Input Full Bridge(FB)/Half Bridge(HB) Morphing-Based LLC DC–DC Converter Using Numerical Optimal Trajectory Control

作者：Deshang Sha；Xiao Yang

出处：IEEE Transactions on Industrial Electronics, Vol. 70, No. 4, pp. 3697-3707（卷期为 2023 年 4 月；在线发表日期为 2022 年 6 月 1 日）

年份：2022

DOI：10.1109/TIE.2022.3177810

Zotero key：UV322KHI

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是 LLC 能不能覆盖宽输入电压，而是采用 full-bridge/half-bridge（FB/HB）拓扑 morphing 以后，怎样在输入电压变化时既迅速切换桥型，又把输出电压扰动、谐振电流峰值和稳定时间压低。传统 LLC 依靠 zero-voltage switching（ZVS）和整流二极管低电流关断获得高效率，但单一桥型若靠大范围变频来覆盖宽输入，容易进入高频、低增益、轻载下难控制的区域；两级 LLC-DCX 方案又增加一个常常硬开关的非隔离级，牺牲效率和功率密度。作者因此选择只保留一个谐振腔和四只整流二极管的 FB/HB morphing 结构：低输入时用 FB，高输入时令 \(Q_3\) 常关、\(Q_4\) 常开而变成 HB，以离散的桥型增益变化换取较窄的连续变频范围。[pdf:E01][pdf:E02]

真正困难发生在桥型边界。先前的多周期 duty 调节需要许多开关周期且可能导致 transformer magnetic deviation；已有一周期 optimal trajectory control（OTC）虽能沿状态平面轨迹切换，却把转换增益固定在一个水平轨迹上，无法直接处理输入电压在切换过程中改变的情形。本文的核心技术 claim 是：把含寄生参数的离线数值模型做成按输入/负载索引的查找表，再让状态平面轨迹的圆心、起终半径和切换频率随实际增益改变，就能在一个过渡周期内直接到达新稳态。[pdf:E02][pdf:E03]

这一问题的重要性来自工程约束的叠加：宽输入通常要求拓扑重构，而高功率密度又不允许增加第二个功率级或长时间过渡。论文用一台 640 W、220-760 V 输入、400 V 输出的原型验证其方案；这相当于约 3.45:1 的输入范围，并报告了全范围稳压、多个输入点的 ZVS、较小的桥型切换电压偏差和 97.8% 峰值效率。[pdf:E01][pdf:E09][pdf:E10][pdf:E11]

## § 2 — 前人工作与不足

论文把既有方案分成“扩大 LLC 连续增益范围”和“改变功率拓扑”两类。前一类包括 variable-frequency 加 phase-shift、轻载 burst、secondary-side notch filter、多谐振腔等；它们分别面临全负载 ZVS 难保证、重载不适用、系统阶次与控制难度上升等问题。后一类包括切换 transformer turns ratio、可重构整流器、H5 bridge、three-phase/multiple-mode LLC；这些方法能扩大范围，但常需额外有源器件、额外谐振腔或更复杂的功率路径。论文的判断不是这些路线“无效”，而是它们在器件数、独立谐振腔、环流、导通损耗或控制复杂度上付出不同代价。[pdf:E01][pdf:E02]

与本文最接近的是 topology morphing 与 OTC。Jovanović 和 Irving 的 on-the-fly morphing 通过多个周期逐步改变 duty，速度受限且论文归纳其存在 magnetic deviation；Wei 和 Mantooth 的策略在固定输入阈值切换，输出振荡仍大；Wen 等的 trajectory transition 能一周期切换且无磁偏，但过渡期间保持固定 gain，未展示输入电压变化响应。其他 SOTC/OTC 工作分别面向负载跃变、轻载 burst 或 48 V DCX 的效率切换，通常固定 switching frequency、pulse width 或输入电压。[pdf:E02][pdf:E08][pdf:E09]

Table III 和 Table IV 给出了作者自己的边界判断：本文方案的相对优势是 variable transition gain、one-cycle transition、不同负载适用、输入电压变化试验和更高的 gain-curve accuracy；代价是需要 lookup table、较大存储空间，而且 sampling sensitivity 被列为 high。也就是说，论文并没有证明一种无条件更优的 OTC，而是把计算量前移到离线仿真和存储，以换取在线一次过渡的准确性。[pdf:E09]

## § 3 — 重建作者的思考路径

以下是基于论文证据重建的合理推断，不是作者逐句陈述的研发日志。

第一步，研究者会先观察到，FB 与 HB 共用同一谐振腔和整流级，但理想基波近似下工作增益区间分别形成两条曲线；在某一输入电压处切换桥型，原则上能让 LLC 避免极端 switching frequency。问题是固定 gain 的水平轨迹只在输入、输出恰好满足该 gain 时成立，一旦输入在切换前后不同，轨迹终点就不再对应目标稳态。[pdf:E02]

第二步，他们会把“切换慢”重新表述为“缺少准确的起点和终点”。OTC 的一周期几何构造本身已经存在，缺的是新稳态的 switching frequency 与状态平面圆半径。若能预先知道任意 \(V_{in}\) 和 \(I_o\) 下 FB/HB 的这些量，在线控制器就不必求解高阶微分方程，只需查表并算一个 transition period 与 duty。[pdf:E03]

第三步，FHA 不能提供足够准确的表。论文指出 transformer winding capacitance、secondary leakage inductance、MOSFET output capacitance 和 rectifier junction capacitance 会改变 gain-frequency 曲线，尤其在谐振频率以上和轻载区域；因此先在 Maxwell/PSIM 中识别或加入寄生量，再做参数扫描，把 FB/HB 的 frequency-gain 和 radius-gain 数据导入 MATLAB 排序成二维 surface。[pdf:E03][pdf:E04]

最后，在线端只保留一个有限状态机：每个 program interrupt 采样 \(V_{in}\) 与 \(I_o\)，用 \(V_{th}\) 和 hysteresis \(V_h\) 判定桥型；需要 morphing 时，从当前与目标工况的表项取得 frequency/radius，计算 \(T_{tran}\) 和 \(D_{tran}\)，让 trajectory control 临时接管，然后把 PI 输出直接置到目标稳态频率。这个路径把不可实时求解的高阶模型变成“离线数值求解 + 在线常数时间查表与代数计算”。[pdf:E03]

## § 4 — 核心 Intuition

核心 intuition 是：不要在桥型切换后让 PI 慢慢寻找新工作点，而要在切换前就从含寄生参数的查找表知道新稳态在哪里。[pdf:E03][pdf:E04] 然后用一次非对称开关周期，把谐振腔的状态从旧圆轨迹直接送到新圆轨迹；输入变化引起的 gain 改变表现为轨迹圆心和半径改变，而不是被强迫沿固定 gain 的水平线移动。[pdf:E02][pdf:E06] 其速度来自一次轨迹跳转，其准确性则依赖离线模型、采样值和查表项是否真的代表当下硬件。

## § 5 — 具体方法与完整 Pipeline

以 400 V 输出、输入电压上升并触发 FB 到 HB 为例，完整 pipeline 如下。

1. **功率级 morphing。** FB 时四个 primary MOSFET 组成全桥；HB 时 \(Q_3\) 常关、\(Q_4\) 常开，只改变 primary 激励幅度，不增加第二个谐振腔。正常稳态仍由 PI 通过 variable-frequency control 调压。[pdf:E02][pdf:E03]

2. **离线寄生参数建模。** 作者在功率模型中加入 MOSFET \(C_{oss}\)、secondary-side transformer leakage \(L_{lks}\)、transformer wiring capacitance \(C_{TR}\) 和 rectifier junction capacitance \(C_{jc}\)。Table I 报告 \(C_{oss}=66\ \mathrm{pF}\)、\(C_{TR}=200\ \mathrm{pF}\)、\(L_{lks}=1.5\ \mu\mathrm{H}\)、\(C_{jc}=160\ \mathrm{pF}\)；其中 Maxwell 3D 对 PQ32/30 两层绕组给出的 \(C_{TR}\) 分项合计为 200.079 pF。[pdf:E03][pdf:E04]

3. **离线数值扫描。** 在 PSIM 中改变输入电压和负载，分别得到 FB/HB 的 steady-state switching frequency 与 state-plane track radius；数据导出到文本后在 MATLAB 中按 load 排序为以 gain 和 \(I_o\) 为坐标的二维 surface。论文同时限制低 gain/轻载下会要求极高频率的区域，而不是让控制器在整张曲面上无条件运行。[pdf:E04]

4. **在线状态判定。** DSP 每次中断采样 \(V_{in}\) 和 \(I_o\)，先读取 `curstate`。例如当前为 HB 且 \(V_{in}<V_{th}-V_h\) 时，用最新 \(V_{in},I_o\) 查目标 frequency/radius，用上一次中断的 \(V_{in},I_o\) 查起始 frequency/radius，随后把 `curstate` 置为 FB；反向切换使用 \(V_{th}+V_h\)，hysteresis 用来抑制阈值附近来回切换。[pdf:E03]

5. **一次 trajectory transition。** 由旧、新轨迹几何关系计算 \(T_{tran}\) 与 \(D_{tran}\)。在这个非对称 transition cycle 内，`cmd_d` 替代稳态 duty，`cmd_sw` 改变 \(Q_3,Q_4\) 的工作模式；过渡后控制权交回 linear PI，并把 PI 输出直接对齐到查表得到的新稳态频率，避免积分器从旧频率重新搜索。[pdf:E03][pdf:E06]

6. **输出。** 目标不是输出一个新的控制参考，而是让谐振电容电压 \(v_{Cr}\)、谐振电感电流 \(i_{Lr}\) 与 magnetizing current 在一次切换周期后落到目标桥型的稳态轨道，同时维持 400 V 输出并抑制峰值与磁偏。[pdf:E06][pdf:E07][pdf:E10]

论文的计算与实现边界必须保留：实际平台是 TMS32028335 DSP 和 SiC primary switch C3M0065090J，不是 FPGA；lookup grid density、插值算法、表项字长、定点/浮点格式、DSP memory bytes、单次查表与计算 latency、ADC sampling rate、program interrupt period、dead time、PWM resolution、并行映射和实时仿真步长均未报告。文中也没有 EMT network discretization 或 multirate FPGA time advance；其“numerical”指离线电路仿真生成查找表，而不是在线 numerical integration。[pdf:E03][pdf:E09]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，其核心不是重新求解含全部寄生的高阶电路，而是用寄生感知的数值查找表给出稳态端点，再在简化 LLC state plane 上构造一次过渡。

**1. 归一化与圆轨迹。** 作者用固定的 \(nV_o\) 而不是会突变的 \(V_{in}\) 归一化电压，用 \(nV_o/Z_o\) 归一化电流，其中
\[
Z_o=\sqrt{L_r/C_r}.
\]
固定归一化基准使输入变化前后的轨迹可在同一几何平面比较。各子模态都写成
\[
[v_{CrN}-c_k]^2+i_{LrN}^2=\rho_k^2,
\]
即圆心 \(c_k\) 随桥型、导通器件和反射输出电压改变。Eq. (2)-(5) 分别给出 FB/HB 的 mode I 与 mode III 圆：例如 FB mode I 的中心为 \(V_{in1N}-1\)，FB mode III 为 \(-V_{in1N}+1\)，HB mode I 为 \(V_{in2N}-1\)，HB mode III 的方程中心为 1。[pdf:E05]

**2. FB 到 HB 的时间构造。** 输入从 \(V_{in1}\) 升到 \(V_{in2}\) 时，作者假设 transition 极快，单个 switching cycle 内轨迹半径不再变化。secondary 被输出电压钳位到 \(i_{Lr}=i_{Lm}\) 的第一段持续半个 resonant period：
\[
t_1-t_0=T_r/2.
\]
归一化 magnetizing current 为
\[
I_{LmN}=\frac{nV_oT_r}{L_m}\frac{1}{4nV_o/Z_o}.
\]
由旧圆上 \(t_0\) 的 capacitor voltage 和新圆心，Eq. (8)-(11) 计算 dynamic radius \(\rho_{tran}\) 及 \(v_{CrN}(t_1),v_{CrN}(t_2)\)；随后把 \(L_m\) 较大所带来的近似用于 mode II，认为 magnetizing current 近似常值地给 \(C_r\) 充电：
\[
t_2-t_1=\frac{C_r\,[v_{CrN}(t_2)-v_{CrN}(t_1)]\,nV_o}{I_{Lm}}.
\]
这些式子合并为 Eq. (13) 的总导通时间 \(t_{\mathrm{total}}\)，再得到
\[
T_{tran}=t_{\mathrm{total}}+\frac{0.5}{f_{Vin2}},\qquad
D_{tran}=\frac{t_{\mathrm{total}}}{t_{\mathrm{total}}+0.5/f_{Vin2}}.
\]
这里 \(f_{Vin2}\) 是按新 gain \(nV_o/V_{in2}\) 与 load 查表得到的目标 steady-state frequency；工程上，前半段负责从旧轨迹离开，后半段用目标稳态的半周期把状态接到新轨迹。[pdf:E06]

**3. HB 到 FB 的反向构造。** Eq. (16)-(19) 重新列出反向切换四种子模态的圆方程，Eq. (20)-(21) 由新的圆心位移推导 \(v_{CrN}(t_2)\) 和总导通时间，duty 定义仍沿用 Eq. (14)-(15)。这不是把前向 PWM 简单倒放，因为 FB/HB 激励幅值与圆心不同，反向式中出现不同的 \(V_{inN}\) 组合。[pdf:E07][pdf:E08]

**4. 寄生参数如何进入。** Maxwell 3D 给出
\[
C_{TR}=C_{PU1,PU2}+C_{PD1,PD2}
+\frac{C_{SU1,SU2}+C_{SD1,SD2}}{n^2}
=200.079\ \mathrm{pF},
\]
并与其他寄生量一起进入离线仿真，改变 frequency surface 和 radius surface。[pdf:E04] 因此，寄生量不是显式出现在 Eq. (2)-(21) 的每个圆方程中，而是通过数值 steady-state lookup table 修正轨迹起终参数。这个“高阶模型离线求端点、二阶几何在线求过渡”的分工，是本文可在 DSP 上实现的关键，也是模型偏差会直接影响控制准确度的来源。

## § 7 — 实验设计与结论

**问题 1：寄生感知的查找表是否有必要？ → 实验：** 在 full load、FB mode 下比较考虑与不考虑寄生参数的 gain-frequency 曲线。**答案：** 谐振频率以下，含寄生的真实曲线低于简化曲线；Fig. 10 给出的例子是用不准确表搜索 gain 1.82 时得到过高 frequency，而该 frequency 在准确曲线上只对应 gain 1.73，目标 gain 误差约 0.09。这个实验支持“端点误差足以造成输出稳态误差”，但只展示了选定模型和工作点，没有给出整张表相对硬件测量的误差统计。[pdf:E04][pdf:E05]

**问题 2：variable-gain、parasitic-aware NOTC 是否优于两种退化版本？ → 实验：** 以 Table II 的 \(L_r=100\ \mu\mathrm{H}\)、\(L_m=300\ \mu\mathrm{H}\)、\(C_r=15\ \mathrm{nF}\)、\(V_o=400\ \mathrm{V}\)、turns ratio 1.125:1 和 640 W rated power 仿真 300 V 到 525 V 的 FB→HB 切换，并比较无寄生 lookup、fixed-gain horizontal OTC 和 proposed NOTC。**答案：** Fig. 13 对 \(V_{oN}\) 的图中标注依次约为 0.08/至少 0.4 ms、0.155/至少 0.4 ms、0.035/0.27 ms；proposed NOTC 的输出摆动与 settling time 最小。[pdf:E07]

反向 HB→FB 仿真采用相同三类控制。Fig. 16 的 \(V_{oN}\) 图中标注依次约为 0.24/至少 0.4 ms、0.48/至少 0.4 ms、0.036/0.275 ms；作者据此认为准确 lookup 和 variable trajectory center 对两个方向都必要。[pdf:E08] 这些是 simulation waveform 上的标注，不应外推为所有输入、负载或硬件参数下的界限。

**问题 3：硬件能否覆盖 220-760 V 输入并维持 400 V 输出和 ZVS？ → 实验：** 构建 640 W 原型，谐振频率 130 kHz；Table V 报告 \(L_r=100.4\ \mu\mathrm{H}\)、\(L_m=299.5\ \mu\mathrm{H}\)、\(C_r=15.03\ \mathrm{nF}\)，primary MOSFET 为 C3M0065090J、rectifier 为 BYV29X-600AQ、DSP 为 TMS32028335、transformer ferrite 为 PQ32/30。作者在 500 W 下展示 220 V 与 760 V 的稳态波形，并在 220、440、460、760 V 展示 primary switch \(S_1\) 的 ZVS。**答案：** 图示工况下输出调节到 400 V，且所示 \(S_1\) 波形满足 ZVS。[pdf:E09] 论文未报告所有 primary switches、全负载矩阵、温度角点或启动/故障期间的 ZVS，因此“全范围所有器件始终 ZVS”不能由这些图推出。

**问题 4：相对 existing OTC，硬件动态是否改善？ → 实验：** 在约 450 V 的 morphing 边界，用同一套硬件、相同参数比较 existing OTC 与 proposed NOTC。**答案：** FB→HB 的 Fig. 21 图中标注从 15.9 V、long settling time 改善为 4.5 V、12.02 ms；HB→FB 的 Fig. 22 图中标注从 11.5 V、long settling time 改善为 3.5 V、8.8 ms。Fig. 23 的局部波形被作者解释为没有 magnetic bias。[pdf:E10] 论文没有给出重复次数、误差条、统计检验，也没有定量定义 “long settling time” 与 settling band。

**问题 5：输入电压变化时能否完成桥型切换？ → 实验：** 采用 EA-PSB 9750-60 直流源，在 500 W 下做 350→550 V 和 450→250 V 的输入变化。电源本身的最小 step-up time 是 20 ms、step-down time 是 60 ms。**答案：** Fig. 24 和 Fig. 25 显示 transition window 内波形连续，作者称切换 fast and smooth。[pdf:E10] 这验证了给定电源斜率下的响应，却没有验证理想阶跃、微秒级 HV bus commutation 或输入变化与负载跃变同时发生的情形。

**问题 6：宽输入是否仍有高效率？ → 实验：** 在 220、370、450、660、760 V 与 200-640 W 多个点绘制 efficiency curve，并在 500 W 计算 conduction、turn-off、sampling、magnetic core/copper 等 loss breakdown。**答案：** 论文报告 peak efficiency 97.8%；同时指出 220 V/FB 与 450 V/HB 因较低频率而 core loss 较大，sampling loss 随输入电压增加。[pdf:E10][pdf:E11] 论文没有提供 calorimetric validation、测量不确定度或所有曲线点的表格数值，不能从图中估读更多精确效率数字。

## § 8 — Take-aways

**5 句话**

1. FB/HB morphing 用同一谐振腔覆盖 220-760 V，但真正的控制难点是让桥型切换后立即落在新的 steady-state trajectory。[pdf:E02]
2. 本文把 MOSFET、transformer 和 rectifier 寄生量纳入离线仿真，生成按 gain/load 索引的 frequency 与 radius lookup tables。[pdf:E03][pdf:E04]
3. 在线 DSP 根据 \(V_{in}\)、\(I_o\) 和有限状态机计算一次非对称 OTC 周期，并把 PI 直接对齐到目标 frequency。[pdf:E03][pdf:E06]
4. 仿真与 640 W 原型在所示工况下都表明 proposed NOTC 的过渡扰动小于 fixed-gain 或寄生不准确的 OTC，并展示 400 V 稳压、多个输入点 ZVS 与 97.8% 峰值效率。[pdf:E07][pdf:E08][pdf:E09][pdf:E10][pdf:E11]
5. 其可信度最依赖离线表与实际硬件的匹配，而论文未报告查表分辨率、插值、温漂、采样时序和快速输入边沿下的鲁棒性。

**3 句话**

1. 作者用“离线高阶数值模型 + 在线二阶状态平面几何”替代 DSP 上实时求解高阶 LLC 动力学。[pdf:E03][pdf:E06]
2. 这种分工使 FB/HB 能以 variable gain 在一个 OTC cycle 内过渡，并在论文所测原型上减少输出偏差和 settling time。[pdf:E09][pdf:E10]
3. 代价是 high sampling sensitivity、large lookup storage 与未量化的 model-to-hardware mismatch 风险。[pdf:E09]

**1 句话**

本文最重要的贡献，是把 FB/HB morphing 的“固定 gain 一周期切换”改成由寄生感知查找表定位起终状态的“variable gain 一周期切换”，但其强鲁棒性仍未被验证。

## § 9 — 最脆弱的假设

最脆弱的假设是：离线 lookup table 在实际过渡发生时仍能准确代表硬件的 steady-state frequency 与 trajectory radius，而且 \(V_{in}\)、\(I_o\) 的离散采样足以选择正确表项。这个假设一旦失效，NOTC 不是仅仅“稍慢”，而会算错 \(T_{tran}\)、\(D_{tran}\) 与目标 frequency，直接把状态送到错误的圆轨迹；论文自己的 Fig. 10 已显示，忽略所选寄生参数即可把目标 gain 1.82 变成实际 1.73，误差约 0.09。[pdf:E04][pdf:E05]

论文为该假设提供的证据，是所建原型在几个输入点维持 400 V、实现所示 \(S_1\) ZVS，并在约 450 V 边界的两个方向上优于 existing OTC。[pdf:E09][pdf:E10] 但缺失证据更接近实际失效条件：\(C_{oss}\) 的电压非线性、\(C_r/L_m\) 温漂、transformer parasitics 的批次差异、load 与 input 同时变化、lookup grid/interpolation error、ADC noise/delay、表项量化以及长期 aging 均未报告；Table III 反而明确把 sampling sensitivity 列为 high、storage space 列为 large。[pdf:E09]

此外，“dramatic input variation”的硬件验证使用最短上升 20 ms、下降 60 ms 的直流源，而 130 kHz 的 resonant period 约为 7.69 μs；基于这两个报告数字计算，输入边沿跨越约 2600 或 7800 个谐振周期。[pdf:E09][pdf:E10] 因此，实验尚未证明控制器能在接近一个 switching cycle 的输入突变下仍用前一中断的起始表项和最新采样的目标表项准确闭合轨迹。

## § 10 — 最小复现实验

一周内最值得做的是一个可证伪的 switched-circuit 数字复现，不先复制完整 640 W 硬件。

- **数据与模型：** 使用论文原型的 \(L_r=100.4\ \mu\mathrm{H}\)、\(L_m=299.5\ \mu\mathrm{H}\)、\(C_r=15.03\ \mathrm{nF}\)、400 V 输出，以及 Table I 的 \(C_{oss}=66\ \mathrm{pF}\)、\(C_{TR}=200\ \mathrm{pF}\)、\(L_{lks}=1.5\ \mu\mathrm{H}\)、\(C_{jc}=160\ \mathrm{pF}\) 建立开关模型；按论文流程仅在 500 W 和一个轻载点生成 FB/HB frequency/radius tables，足以检验核心机制。[pdf:E04][pdf:E09]
- **实现：** 实现三条完全共享功率模型和 PI 参数的控制路径：parasitic-aware variable-gain NOTC、fixed-gain horizontal OTC、使用 parasitic-free lookup 的 NOTC。复现 350→550 V 与 450→250 V，再加入一个快得多但仍数值可解析的输入边沿；不在比较后重新调参。[pdf:E10]
- **测量：** 对两个方向记录 \(\max |V_o-400|\)、进入并持续保持在 2% band 的 settling time、peak \(|i_{Lr}|\)、过渡后 steady-state error、\(\int v_{Lm}\,dt\) 的偏移代理，以及是否保持 ZVS。额外对 \(L_m,C_r,C_{TR},C_{oss}\) 做 ±20% 一次只变一个参数的 sweep，并加入采样一拍延迟。
- **支持条件：** nominal 条件下，proposed NOTC 在两个方向都同时降低 output deviation 与 settling time，且 peak current 不比两个 baseline 高 10% 以上、最终误差低于 1%、磁通积分没有累积漂移；结果趋势应与 Fig. 13、16、21、22 一致。[pdf:E07][pdf:E08][pdf:E10]
- **反驳条件：** 任一方向在统一参数下不能优于 fixed-gain OTC，或只要合理的元件偏差/一拍延迟就出现错误桥型、明显更大峰值、失去 ZVS 或持续磁偏，则“查表即可形成准确的一周期 variable-gain transition”这一核心 claim 被削弱。论文未给出 lookup grid 与 interpolation，复现者应公开所用网格并做收敛检查，而不能把插值选择隐藏在调参中。

## § 11 — 最强反例设计

最强反例不是再挑一个静态输入点，而是在 morphing threshold 附近同时施加“快输入边沿 + 负载跃变 + 热态参数偏移”。具体可让输入在小于 100 μs 内从 350 V 升到 550 V，同时把输出从 500 W 切到轻载或反向，并让 \(C_{oss}\)、\(C_r\)、\(L_m\) 使用热态实测值；重复两个切换方向。控制器在 program interrupt 中用最新 \(V_{in},I_o\) 查目标 radius，却用上一次中断的 \(V_{in},I_o\) 表示起始状态，因此这个工况会有意识地破坏“采样对与真实状态一致”的前提。[pdf:E03]

需要观测的不只是 \(V_o\) overshoot，还包括过渡开始瞬间的 \(i_{Lr},v_{Cr}\)、primary leg volt-second、每个 MOSFET 的 ZVS、是否跨过错误的查表区域和 hysteresis 是否重入。若 proposed NOTC 在 nominal 慢斜率下仍好、但在这一工况中比 fixed-gain OTC 出现更大 current spike、失去 ZVS、重复 morphing 或累积 magnetic bias，就形成对核心机制的直接反例，而不只是外围实现瑕疵。

这个反例还检验一个具体替代解释：Fig. 24/25 的“fast and smooth”可能主要来自电源 20/60 ms 的慢斜率，使 PI、采样和查表在许多千个 resonant cycles 内逐步跟随，而不是 NOTC 对真正 sudden input step 的鲁棒性。[pdf:E10] 若把输入边沿加快后优势消失，则现有硬件结果不能支撑论文对 dramatic input variation 的广泛表述。

## § 12 — Follow-up Research Idea

在 power electronics 与 industrial electronics 中，高影响工作通常不仅要求更小的波形扰动，还要求机制可解释、全工况效率/ZVS、器件与磁件可实现性、对参数与时序不确定性的硬件验证，以及相对强 baseline 的可重复比较。本文已经具备真实 640 W 原型和宽输入覆盖，但最关键的未满足需求是：一次开环轨迹跳转缺少对 lookup mismatch、采样延迟和并发扰动的最坏情况保证。

**候选研究方向：从 point trajectory lookup 改写为 uncertainty-tube morphing control。** 不再要求控制器命中一个由 nominal table 给出的圆，而是用在线可观测的 \(i_{Lr},v_{Cr},V_{in},I_o\) 建立一个含参数和采样误差的 reachable state tube；桥型切换只在该 tube 的所有状态都能于限定周期内进入目标 invariant set、保持 ZVS 且不产生净 volt-second 时获准。无法保证一次完成时，控制目标不是盲目坚持 one-cycle，而是在明确约束下选择一到数个安全脉冲。

（a）驱动力是实际 converter 的 parasitics、温度和采样时序会变，而 nominal LUT 把这种变化压缩成单点；（b）如果能给出宽输入 morphing 的 worst-case voltage/current/ZVS guarantee，并在高功率原型上验证，它比单一工况波形改善更接近本领域认可的系统价值；（c）可借鉴 hybrid systems reachability、tube model predictive control、set-membership parameter estimation 和 event-triggered control；（d）第一个证伪实验就是第 11 节的快输入边沿、同步 load step 与热态参数 sweep，若 reachable tube 预测安全但硬件仍失去 ZVS或超出电压/电流界限，方向立即失败；（e）它与本文的实质区别是把“nominal endpoint 是否准确”改成“所有允许不确定状态是否都安全可达”，改变了问题定义与验收目标，而不是在原查找表旁再加一个补偿模块。

本卡严格采用 PDF-only，未进行外部相关工作检索，因此这一方向只是基于本文证据约束的候选判断，不声称 novelty。
