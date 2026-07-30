# Splitting State-Space Method for Converter-Integrated Power Systems EMT Simulations

- 作者：Xiaopeng Fu, Wei Wu, Peng Li, Jean Mahseredjian, Jianzhong Wu, Chengshan Wang
- 出处：IEEE Transactions on Power Delivery, 40(1): 584-595
- 年份：2025（卷期；ORCA cover 的 citation 行写作 2024）
- DOI：10.1109/TPWRD.2024.3514294
- Zotero key：P93T3JQ8（附件 GYLI9AQD）
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。
- 版本说明：源 PDF 是 Cardiff ORCA 保存的 author accepted manuscript；封面明确提醒其排版和页码可能不同于正式出版版（PDF 物理页 1，ORCA source cover）。[pdf:E01]

## § 1 — 研究问题与重要性

这篇论文解决的是一个很具体的计算瓶颈：在 converter-integrated power system 的 EMT 仿真中，开关动作不断改变状态矩阵；如果每次都对整个时变状态矩阵计算 matrix exponential，计算量会随着状态维数和开关频率快速增长。作者指出，实际研究又同时向更长时间尺度、更大系统规模和更高开关频率扩展，半导体开关频率可达数百 kHz，小时间常数也迫使仿真采用更小步长；因此，高保真详细模型与可接受的执行时间发生直接冲突（PDF 物理页 2，Abstract 与 Section I）。[pdf:E02]

论文的目标不是把 converter 换成平均模型，而是在保留详细开关 EMT 模型的前提下少算昂贵的矩阵指数。其工程价值在于：若能把每次开关真正影响的局部动态从大系统中分离出来，大部分系统动态可以复用预计算结果，而只有小规模、稀疏的时变部分需要更新；这样才有机会把详细建模扩展到多 converter、wind farm 和 MMC 等场景（PDF 物理页 2，Abstract；物理页 4，Fig. 1-2）。[pdf:E02][pdf:E04]

## § 2 — 前人工作与不足

论文把既有加速路线分成几类。第一类是 circuit-based decoupling：用 transmission-line propagation delay、compensation、multirate 或 parallel computation 分割网络；它们能降低耦合计算，但传统线路延时并非任意位置都有，任意切分仍需 compensation。第二类是 state-space nodal、automatic circuit partitioning 和 region folding：它们能分组 switching event、选择性显式化储能元件，或利用重复结构预计算逆矩阵，但对通用 converter topology 的自动高效解耦仍不充分。第三类是 constant admittance/state matrix、associated discrete circuit 和 source-pair model：它们通过近似开关或引入一步延迟保持系数矩阵不变，适合 real-time 场景，却改变了开关表示或依赖特定模型结构（PDF 物理页 2-3，Section I）。[pdf:E02][pdf:E03]

对 MMC 还存在专用 reduced-order equivalent model。作者明确说，它由特定拓扑的静态电路原理推导，适用于 nodal-analysis 程序，并不是本文要竞争的对象；本文的诉求是基于 differential equation/state-space 的通用拓扑处理。这一边界很重要：论文证明的是同一套解耦原则能作用于 Cuk、MMC 等拓扑，并没有证明它在每一种特定 converter 上都优于专用等值模型（PDF 物理页 7，Fig. 5-6 后正文）。[pdf:E07]

## § 3 — 重建作者的思考路径

下面是基于论文背景与方法结构的合理重建，不是作者逐字陈述。

第一步，详细 EMT 的主要代价并不只是积分步数多，而是开关使大状态矩阵反复变化，matrix exponential 的通用计算复杂度为 \(O(N^3)\)。第二步，物理上一次开关只直接改变与其相邻电感、电容有关的少量状态方程，因此“全矩阵都变”是代数表示造成的过度计算，不是系统每一部分都真的在同一时刻改变。第三步，若按 converter 对开关分组，再找出 switch adjacent state variables（SASV），时变元素应该落入若干局部块，而其余矩阵可保持常量（PDF 物理页 3，Section II.A；物理页 4，Fig. 1）。[pdf:E03][pdf:E04]

第四步，operator splitting 已经提供了把 \(\exp(h(A_1+A_2))\) 写成多个较小矩阵指数乘积的工具；只要把常量部分放在 \(A_1\)、局部时变部分放在 \(A_2\)，就能预计算 \(\exp(hA_1)\)，并用低阶 Taylor 近似快速更新 \(\exp(hA_2)\)。最后，splitting 会引入新误差，所以不能只追求 speedup；必须用误差矩阵和阈值，在仿真前选择步长与 splitting order（PDF 物理页 3-5，Eq. (4)-(17)）。[pdf:E03][pdf:E04][pdf:E05]

## § 4 — 核心 Intuition

核心直觉是：converter 开关并没有让整个电力系统同时变成“新系统”，它只改变了紧邻开关的少量储能状态之间的功率转换关系。把这些局部、时变关系抽成稀疏的 \(A_2\)，把大而不变的网络动态留在 \(A_1\)，就可以重复使用 \(A_1\) 的矩阵指数，只在开关变化时更新小块 \(A_2\)。Trotter/Strang splitting 负责重新组合两部分动态，误差估计则决定这种省算是否仍在可接受范围内（PDF 物理页 4，Fig. 1-2；物理页 5，Eq. (11)-(17)）。[pdf:E04][pdf:E05]

## § 5 — 具体方法与完整 Pipeline

以论文的 half-bridge 示例为线索，完整 pipeline 如下。

1. **输入模型。** 从线性、分段时变的 state-space 方程出发，把 forcing term 通过辅助状态并入增广状态，得到 autonomous form。converter switch 在每个固定开关状态下由 binary resistance 等模型给出相应的状态矩阵（PDF 物理页 3，Eq. (1)-(3) 与 Section II.A）。[pdf:E03]
2. **开关分组。** 扫描拓扑，把共享 switch-node set \(N_s\) 的开关归为一个 converter group。不同组原则上对应不同 converter，因此后续识别具有潜在并行性（PDF 物理页 6，Section III.A 与 Fig. 4）。[pdf:E06]
3. **识别 SASV。** 找出连接到 \(N_s\) 的电感电流和电容电压。half-bridge 中 \(I_L,U_{C1},U_{C2}\) 都是 SASV；只有它们对应状态方程中的系数随 \(S_1,S_2\) 改变（PDF 物理页 5-6，Fig. 3 与 Eq. (18)）。[pdf:E05][pdf:E06]
4. **构造两个子系统。** 对 constant-part subcircuit，把 converter 支路注入 SASV capacitor 的电流置零、把 SASV inductor 的 switch-adjacent terminal 电压置零；time-varying subcircuit 取互补关系。若 SASV inductor 有串联电阻、capacitor 有并联电阻，相应电阻保留在时变子电路。由此得到常量 \(A_1\) 和按 converter 分块、随 \(s(t)\) 改变的 \(A_2(s(t))\)（PDF 物理页 6，Eq. (18)-(19) 与 Fig. 4）。[pdf:E06]
5. **时间推进。** 仿真开始时只计算一次 \(\exp(hA_1)\)。开关状态变化后，对小而稀疏的 \(A_2\) 用有限项 Taylor polynomial \(f_k\) 近似其 exponential，再按 first-order Trotter 或 second-order Strang 的子步顺序推进并组合状态（PDF 物理页 4，Eq. (8)-(10) 与 Fig. 2）。[pdf:E04]
6. **误差配置。** 用 splitting error 与 Taylor truncation error 的组合估计 \(S_m\)，对候选步长 \(h\) 和 splitting order 检查 \(S_m<t_E\)。论文把这一步用于仿真前的 setting selection；报告案例没有展示 runtime adaptive step-size controller（PDF 物理页 5，Eq. (11)-(17)）。[pdf:E05]
7. **输出。** 输出仍是详细开关模型的 EMT waveform，而非 average-model waveform。论文的实现用 MATLAB 运行 exponential schemes，并与 EMTP 比较；它没有报告 FPGA mapping、fixed-point representation、DSP/BRAM/LUT 消耗、pipeline latency、硬件实时 deadline 或板级执行结果。作者仅把并行化和 GPU acceleration 列为后续工作，因此不能从本文外推 FPGA 实时性能（PDF 物理页 10，Section IV.C；物理页 11，Section V）。[pdf:E10][pdf:E11]

## § 6 — 核心数学推导（无形式化数学则跳过）

原始线性系统为

\[
\dot{x}=Ax+Bu,\qquad x(0)=x_0.
\]

作者通过 auxiliary state 把输入并入增广系统 \(\dot{\tilde{x}}=\tilde{A}\tilde{x}\)，于是一步精确推进写成

\[
x(t)=e^{tA}x(0).
\]

这一步的意义是把 EMT 时间推进归结为 matrix exponential，但通用求解代价为 \(O(N^3)\)。[pdf:E03]（PDF 物理页 3，Eq. (1)-(3)）

将状态矩阵拆为 \(A=A_1+A_2\) 后，first-order Trotter formula 为

\[
e^{h(A_1+A_2)}=e^{hA_1}e^{hA_2}+O(h^2),
\]

其主导差异来自两个矩阵不交换：

\[
e^{h(A_1+A_2)}-e^{hA_1}e^{hA_2}
=\frac{h^2}{2}(A_2A_1-A_1A_2)+O(h^3).
\]

若使用对称组合，second-order Strang formula 为

\[
e^{h(A_1+A_2)}
=e^{\frac h2 A_2}e^{hA_1}e^{\frac h2 A_2}+O(h^3).
\]

普通语言解释是：Trotter 先走完一个子系统再走另一个子系统，所以顺序会留下 commutator error；Strang 把时变子系统分成两个半步夹住常量子系统，抵消一部分低阶顺序误差。[pdf:E03]（PDF 物理页 3，Eq. (4)-(6)）

对 converter-integrated system，作者把状态按 SASV 分成 \(x_1,x_2\)：

\[
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\end{bmatrix}
=
\begin{bmatrix}A_{11}&A_{12}\\A_{21}&A_{22}\end{bmatrix}
\begin{bmatrix}x_1\\x_2\end{bmatrix}.
\]

\(A_{11},A_{12},A_{21}\) 保持常量，时变元素集中在 \(A_{22}\) 内与各 converter 对应的 diagonal blocks \(g_i\)。对时变 exponential，论文采用

\[
f_k(hA_2(s(t_n)))=\sum_{i=0}^{k}\frac{(hA_2(s(t_n)))^i}{i!}.
\]

Strang 的三个子步是先用 \(f_2(\tfrac h2A_2)\) 更新 \(x_2\)，再用 \(e^{hA_1}\) 更新全状态，最后再做一个 \(A_2\) 半步；这样昂贵的大矩阵指数只属于常量部分。[pdf:E04]（PDF 物理页 4，Fig. 1-2，Eq. (7)-(10)）

误差控制把 formula error \(E_m\) 与 Taylor truncation error \(E_t\) 相加为 \(E_s=E_m+E_t\)。first-order splitting 的主导矩阵为

\[
E_2=\frac{h^2}{2}(A_2A_1-A_1A_2),
\]

而一阶 Taylor 截断的主导项是 \(h^2A_2^2/2+O(h^3)\)。作者用 logarithmic norm

\[
\mu(A)=\lim_{h\to0^+}\frac{\lVert I+hA\rVert-1}{h}
\]

估计局部误差，并在 binary-resistance switch model 下把 all-off 状态作为最坏上界。若 \(\mu(A_1)=a\)、all-off 时 \(\mu(A_2)=b_0\)，且假设 \(b_0/a\ll1\)，first-order error 近似为

\[
S_1\approx h^2ab_0,
\]

最终以 \(S_m<t_E\) 选择 splitting order 和 time-step。[pdf:E05]（PDF 物理页 5，Eq. (11)-(17)）

half-bridge 的 Eq. (18)-(19) 给出这一代数拆分的电路含义：switch-dependent system 只保留 \(S_1,S_2\) 控制的 capacitor-inductor 功率交换，constant system 则保留外部网络与储能元件的充放电通道（PDF 物理页 6，Eq. (18)-(19) 与 Fig. 4）。[pdf:E06]

## § 7 — 实验设计与结论

**问题 1：不同 splitting order 是否保持准确？** → IEEE-13 node + DC load 采用 74 个状态，仿真 5 s、步长 10 μs，以 EMTP 5 μs 结果为 benchmark，并比较 Exp、两种 first-order 子步顺序和 second-order sExp。→ Fig. 8 显示 sExp-2nd 最准，sExp-1st-12 次之，sExp-1st-21 的 absolute error 更大；估计 splitting error 对 first-order 为 0.31%，对 second-order 为 0.08%。但正文随后又把“较大 absolute error”归因到 sExp-1st-12，与前一句和图中趋势不一致，因此该归因不能作为已闭合结论（PDF 物理页 7-8，Section IV.A 与 Fig. 7-8）。[pdf:E07][pdf:E08]

**问题 2：误差阈值能否指导高频 LLC 的步长与阶数？** → 500 kHz LLC 用 8 维状态、binary-resistance IGBT、0.1 s 仿真；以 EMTP 1 ns 为 benchmark。Table I 给出：在 4 ns 时 sExp-1st error 为 \(7.75\times10^{-3}\)，sExp-2nd 为 \(7.55\times10^{-4}\)，只有后者低于 0.1% 阈值；first-order 要到 0.5 ns 才降到 \(8.05\times10^{-4}\)。→ second-order 允许在同一阈值下使用更大步长；该案例中 Exp integration 用时 56.51 s，sExp-1st 用时 19.52 s，作者报告 speedup 2.89（PDF 物理页 8-9，Section IV.B、Fig. 9-10 与 Table I）。[pdf:E08][pdf:E09]

**问题 3：多 converter 规模扩大时是否有实际 speedup？** → type-4 wind farm 每台 converter 含 12 对 IGBT/anti-parallel diode；50 WTG 时状态维数 2135。测试在 \(t=1\) s 施加三相接地故障、5 cycles 后切除，\(t=2\) s 风速从 12 m/s 变为 10 m/s；sExp 步长 5 μs，以 EMTP 1 μs 为 benchmark，并从 2 扩展到 50 WTG。→ 10-WTG 波形按故障距离形成三组：active power 约下降 8%、67%、95%，DC voltage 分别升至 1.10、1.42、1.54 p.u.；sExp-2nd error 接近 unsplit Exp。50 WTG 时 Table II 报告 EMTP、sExp-1st、sExp-2nd 分别用时 24138.12、4607.38、15151.93 s；由表中时间计算，对 EMTP 的 speedup 分别约为 5.24 和 1.59。所有 exponential schemes 用 MATLAB，EMTP 与各方案比较在 single core 上进行，因此这些数字不是语言、硬件完全等价的算法基准（PDF 物理页 9-10，Section IV.C、Fig. 11-14 与 Table II）。[pdf:E09][pdf:E10]

**问题 4：局部时变块增大时，收益是否随规模增长？** → MMC 每臂从 4 扩展到 200 个 SM；200 SM/arm 时有 404 个状态，仿真 0.1 s、步长 20 μs，以 EMTP 5 μs 为 waveform benchmark。→ 5-level MMC 中 sExp 略逊于 EMTP 和 Exp，但波形与 benchmark 一致；相对 unsplit Exp 的 speedup 随 voltage level 从 5、11、21、51、101、201 增长，分别为 1.06、1.30、1.37、2.55、6.18、16.63。这里的 16.63 是相对 Exp，不是相对 EMTP（PDF 物理页 10-11，Section IV.D、Fig. 15 与 Table III-IV）。[pdf:E10][pdf:E11]

四组案例共同支持“local splitting 能减少重复 matrix exponential 计算，并允许在 order/step-size 间权衡”的 claim；它们没有证明硬实时 deadline、FPGA 资源可实现性、非线性器件细节下的误差保证，也没有与 converter-specific reduced model 做统一精度-速度比较（PDF 物理页 7，Section III.B-IV；物理页 10-11，Section IV.C-V）。[pdf:E07][pdf:E10][pdf:E11]

## § 8 — Take-aways

**5 句话：**

1. 论文把开关造成的时变状态矩阵限制在 SASV 对应的局部块，使大而常量的网络矩阵指数能够复用（PDF 物理页 4，Fig. 1；物理页 6，Fig. 4）。[pdf:E04][pdf:E06]
2. Trotter/Strang splitting 与低阶 Taylor approximation 把一次大矩阵指数改写成常量大块和时变小块的分阶段推进（PDF 物理页 3-4，Eq. (4)-(10)）。[pdf:E03][pdf:E04]
3. logarithmic-norm error criterion 用于仿真前选择 time-step 和 splitting order，LLC 案例展示 second-order scheme 在 0.1% 阈值下可用 4 ns，而 first-order 需 0.5 ns（PDF 物理页 5，Eq. (11)-(17)；物理页 9，Table I）。[pdf:E05][pdf:E09]
4. wind farm 与 MMC 的规模实验显示，局部块复用的收益会随 converter 数量或 voltage level 增加，但 speedup 基线、实现语言与精度设置必须一起阅读（PDF 物理页 10-11，Table II 与 Table IV）。[pdf:E10][pdf:E11]
5. 论文未完成 FPGA、fixed-point、real-time deadline 或板级资源验证，所以它提供的是可映射的数值结构，不是已验证的 FPGA EMT engine（PDF 物理页 10-11，Section IV.C-V）。[pdf:E10][pdf:E11]

**3 句话：**

1. 只更新真正受开关影响的状态块，是本文降低 detailed EMT 计算量的核心（PDF 物理页 4，Fig. 1-2）。[pdf:E04]
2. 省算并非免费：splitting order、time-step、Taylor truncation 和 switch-event localization 共同决定误差（PDF 物理页 5，Eq. (11)-(17)；物理页 8，Fig. 8 后正文）。[pdf:E05][pdf:E08]
3. 当前证据支持 CPU/MATLAB 案例中的可调精度与规模收益，不支持硬件实时性能外推（PDF 物理页 10-11，Table II、Table IV 与 Section V）。[pdf:E10][pdf:E11]

**1 句话：**

这是一种“把开关局部性变成矩阵局部性，再用有误差控制的 operator splitting 复用大系统计算”的 EMT 加速方法（PDF 物理页 4-5，Fig. 1-2 与 Eq. (11)-(17)）。[pdf:E04][pdf:E05]

## § 9 — 最脆弱的假设

最脆弱的假设不是“splitting formula 存在”，而是 **binary-resistance 模型的 all-off 状态给出所有 switch state 的误差上界，且 \(b_0/a\ll1\)**。如果某个导通、换流或 simultaneous-switching 状态产生更大的 \(\mu(A_2)\)，或者 SASV 的惯性不够大使 \(b_0\) 与 \(a\) 同量级，那么仿真前计算的 \(S_m<t_E\) 可能低估真实局部误差，论文最重要的“可据此选 order/step-size”结论就会直接失效（PDF 物理页 5，Eq. (11)-(17) 前后正文）。[pdf:E05]

论文给出的正面证据是 LLC 的 Table I：second-order 在 4 ns 时通过 0.1% 阈值并获得与 benchmark 相符的 waveform（PDF 物理页 8-9，Fig. 10 与 Table I）。[pdf:E08][pdf:E09] 但反面信号也来自论文自身：IEEE-13 案例明确说低阶 splitting error 并非 dominant，switch operation 的误算会放大 absolute error，而且该段对是哪一种 first-order 顺序出现了内部表述不一致（PDF 物理页 8，Fig. 8 后正文）。[pdf:E08] 因而，现有证据说明这个 criterion 对测试案例有用，却没有证明它对所有 converter topology、所有 switch combination 和 event interpolation 都是严格上界。

## § 10 — 最小复现实验

一周内最小而有证伪力的实验，不必复现整个 wind farm，可以复现 Fig. 3 half-bridge 的 state matrix splitting。

1. 按 Eq. (18)-(19) 写出含 \(C_1,C_2,L,R\) 的全矩阵 \(A(s)\)、constant \(A_1\) 和 switch-dependent \(A_2(s)\)，并在实验记录中明确写出所选元件参数（PDF 物理页 5-6，Fig. 3 与 Eq. (18)-(19)）。[pdf:E05][pdf:E06]
2. 枚举两对开关的全部合法/故障组合；对每种状态直接计算 reference transition \(e^{hA(s)}\)，再计算 sExp-1st 和 sExp-2nd transition。
3. 对 \(h\) 做至少一个 decade sweep，记录 one-step matrix error、短时 waveform error、\(\mu(A_2)\)、论文估计的 \(S_m\) 和实际 worst-state。
4. 支持 claim 的判据是：all-off 确实给出最大误差；first- 与 second-order 的主导误差随 \(h\) 呈预期阶次下降；所有满足 \(S_m<t_E\) 的组合，其实际误差都不越过预先声明的阈值。
5. 只要发现一个非 all-off 状态超过估计上界，或通过 \(S_m<t_E\) 的设置仍系统性越界，就反驳“该 criterion 足以指导 setting selection”的强版本；这比只复画论文波形更能检验核心机制。

## § 11 — 最强反例设计

最强反例是构造一个 **多个 converter 直接共享低惯性 DC-link/LC 状态、并发生 simultaneous commutation** 的系统。这样，论文依赖的两个结构条件会同时受压：不同 converter 的时变元素不再自然落在彼此独立的小 diagonal block 中，且导通/换流状态可能比 all-off 状态产生更大的 \(A_2\) logarithmic norm。对同一 piecewise-linear switch model，完整枚举 switch combinations，比较 full Exp、sExp-1st、sExp-2nd 与 fine-step reference；再在同一误差上限下记录 runtime（事实前提见 PDF 物理页 4，Fig. 1；物理页 5，Eq. (11)-(17) 前后正文）。[pdf:E04][pdf:E05]

如果出现以下结果，论文的 general-purpose 强表述就被真正挑战：自动分组仍把系统拆成小块，但实际 off-diagonal time-varying coupling 不可忽略；预计算的 \(S_m\) 通过阈值而 waveform error 越界；为了恢复精度必须把 \(A_2\) 扩成接近全系统，最终 speedup 消失。这个反例不依赖更复杂的非线性器件模型，因此无法用“模型超出论文范围”轻易回避；它直接攻击 block sparsity 和 error upper bound 两个核心机制。论文只展示 converter 由 filter/line 分隔的案例，并未覆盖这种直接共享低惯性状态的边界（PDF 物理页 4，Fig. 1；物理页 9-10，Fig. 11 与 Section IV.C）。[pdf:E04][pdf:E09][pdf:E10]

## § 12 — Follow-up Research Idea

**候选方向：从 heuristic pre-check 改成 event-aware、可认证的 EMT splitting controller。** 这里的研究目标不再是“选一个大概可用的 order/step-size”，而是：对每次 topology transition，在线给出可验证的局部误差上界和 deadline 预算；当 block coupling 或 switch-event error 破坏原有假设时，自动合并局部块、提高 order，或暂时回退 full exponential。该方向来自第 9 节的未满足需求：论文的 pre-simulation criterion 依赖 all-off worst case 和 \(b_0/a\ll1\)，而其案例也显示 event localization error 可能越过低阶 splitting error 成为主因（事实前提见 PDF 物理页 5，Eq. (11)-(17)；物理页 8，Fig. 8 后正文）。[pdf:E05][pdf:E08]

在 power-system EMT 领域，高影响价值应来自严格误差证据、可扩展计算和工程平台上的可实现性，而不仅是多一个 case。可以借鉴 hybrid systems 的 reachability/error envelope、sparse graph 的 dynamic partition，以及 real-time scheduling 的 worst-case execution-time analysis，把“数值误差”和“实时 deadline”作为同一个受约束决策问题。论文已经展示 block splitting 的计算收益，并把 parallel/GPU acceleration 留作未来工作；新方向要进一步证明 bound 与执行平台之间的闭环，而不是只把现有 MATLAB 代码移植到 GPU/FPGA（PDF 物理页 10，Table II 与 MATLAB 实现说明；物理页 11，Section V）。[pdf:E10][pdf:E11]

第一个证伪实验就是第 11 节的 shared low-inertia multi-converter 系统：有限枚举全部 switch pattern 和 simultaneous event，检查在线 bound 是否覆盖每一个 measured local error，同时比较 full Exp 的 deadline。若存在未覆盖误差，或认证开销吃掉 splitting speedup，这个方向应被否决。与本文的实质区别是：本文在仿真前用一个代表性 worst-state 选择 setting；候选方法把 topology/event uncertainty 当作运行时对象，并要求逐事件给出可检查保证。本文未完成针对这一方向的相关工作检索，因此这里只提出候选问题，不声称 novelty。
