# Real-Time Simulation Method for High-Frequency Power Electronic Converters With Blocking Mode

**作者：** Zonghui Sun、Yu Zhang、Zhuolan Li  
**出处：** *IEEE Transactions on Industrial Electronics*（已接收，未来期次，页码未定）  
**年份：** 2025  
**DOI：** 10.1109/TIE.2025.3589443  
**Zotero key：** 8TC6G8FU  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的是一个很具体的实时仿真矛盾：高频 bridge-based power electronic converter（BHPEC）若采用精度较高的 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 开关模型，就必须正确识别二极管既不正向也不反向导通的 blocking mode；传统迭代判态会增加计算延迟，而不识别 blocking mode 又会在 discontinuous conduction mode（DCM）的过零处或谐振过程中制造数值振荡。对 100–200 kHz 量级的变换器，仿真步长还要足够小，才能对 gating signal 过采样。作者把目标压缩为：用非迭代、可映射到 FPGA 的办法识别半桥臂 blocking mode，同时保持 backward Euler（BE）的数值稳定性和较低资源消耗。论文摘要报告的最终实现是 100 kHz SLR 与 200 kHz LLC 两个 FPGA 实时模型，步长均为 20 ns。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题的重要性不只是“算得更快”。固定步长求解器通常不会恰好采到电感电流的零点；若用电流符号直接决定二极管状态，真实电路中应出现的无电流区会被虚假的正、负导通来回替代。结果是仿真波形中出现本不属于物理系统的 chattering 或谐振振荡，进而削弱 controller/HIL 验证的可信度。论文还指出，高频应用中通常希望把步长设为 switching period 的 \(1/50\) 甚至 \(1/100\)；因此每一步多做一次大规模 matrix-vector operation（MVO），会直接挤压可实现的 switching frequency、模型规模或 I/O 余量。[pdf:E01]（PDF 物理页 1，Introduction）

## § 2 — 前人工作与不足

论文把既有路线分成三类。第一类是 associated discrete circuit（ADC）模型：它适合快速开关网络求解，但存在 virtual loss，且作者引用的既有结果指出其高频建模精度会恶化。第二类是 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 模型：它更接近开关导通/关断电阻，却通常需要迭代更新二极管和反并联二极管状态。第三类是消除迭代的专用或预测方法，但各有代价：按电感电流方向判态会漏掉 blocking mode；只处理 gating signal 驱动的开关不能覆盖含二极管电路；面向 MMC submodule 或 LLC full bridge 的 direct mapping 缺乏拓扑通用性；把全部 switching network 当整体分析会增加 FPGA 计算量；采用 forward Euler 的 status prematching 容易出现数值振荡；改用 BE 的前一版 prediction-correction 方法则需要在一个步长中计算两次状态方程。[pdf:E02]（PDF 物理页 2，Introduction 与 Section II）

最直接的 baseline 是作者自己的文献 [30]：它用旧状态组合预测 \(x^p(k)\)，据此预判自然换流状态，再另算真实 \(x(k)\)。优点是按半桥臂判态、天然可解耦，也能识别 blocking mode；不足是预测路径与真实状态路径各有一次 MVO，串行实现增加 critical path，并行实现也会重复乘法和 DSP 资源。论文要改的不是 blocking criterion 本身，而是“预测量只用于判态、不能直接成为真实状态”这一计算组织方式。[pdf:E03]（PDF 物理页 3，Eq. (7) 前后）

需要保留一个比较边界：论文列举的 prior work 及其不足均来自本文的相关工作叙述，本卡没有联网取得这些论文的全文，因此这里只能准确重述作者如何定位 baseline，不能独立认证每一篇 prior work 的限制。

## § 3 — 重建作者的思考路径

下面是基于论文给出的失败模式与公式关系重建的思考路径，属于“基于证据的合理推断”，不是作者逐字叙述。

1. 先保留 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 模型，因为 blocking mode 本质上是开关状态问题，不能靠平滑化或忽略二极管自然换流来换取速度。
2. 再保留 BE，因为已有 forward Euler 判态法虽便宜，却可能把高频谐振系统的数值不稳定带回来。
3. 观察旧 prediction-correction 方法：在开关状态不变时，按旧状态预测的 \(x^p(k)\) 与真实 \(x(k)\) 相同；两者只在状态发生变化的离散时刻分叉。于是，逐步重复计算两套状态并非必要。
4. 进一步把 gating signal 已知的强制状态先写进 corrected status \(\sigma^\*(k)\)。这样，gating signal 的跳变不再令预测状态与真实状态分叉，剩下需要修正的只有自然换流中的 diode status change。[pdf:E03]（PDF 物理页 3，Eq. (8)–(10) 及相邻正文）
5. 对剩余的事件时刻，不再重算一套完整状态：事件当步先保持 \(x(k)=x(k-1)\)，下一步用 \(2\Delta t\) 的 BE 系数一次跨过两个小步。再用一个 flag 在 \(\Delta t\) 与 \(2\Delta t\) 两组预存矩阵之间选择，就可把正常步与事件恢复步统一成一次 MVO。[pdf:E04]（PDF 物理页 4，Eq. (11)–(19)）

因此，这篇论文的发明点更像是“事件稀疏条件下的计算重排”，而不是新的器件模型或新的 blocking 判据：把每一步都要付出的第二次 MVO，变成仅在判定到自然换流事件时进行的离散状态保持与下一步补偿。

## § 4 — 核心 Intuition

核心 intuition 是：真实状态与预测状态只会在二极管自然换流的极少数离散时刻不一致，所以没必要在每个 20 ns 步长里都算两遍状态方程。先把 gating signal 已知的状态变化吸收到预测矩阵中，再在二极管状态变化的那个步长冻结状态、下一步用 \(2\Delta t\) 补偿，就能让主计算路径保持一次 MVO，同时继续显式识别 blocking mode。[pdf:E03]（PDF 物理页 3，Section III）[pdf:E04]（PDF 物理页 4，Eq. (11)–(19)）

## § 5 — 具体方法与完整 Pipeline

以论文的 SLR converter 为例，一步仿真的输入是 gating signals、当前输入电压 \(u(k)=v_{\mathrm{in}}\)、前一步状态 \(x(k-1)=[i_{Lr},v_{Cr},v_o]^\mathsf{T}\)、各半桥臂上一时刻自然状态以及 flag。输出是更新后的状态 \(x(k)\) 和可送往 DAC/后续计算的电流、电压。

1. **先合成 corrected switch status。** 每个半桥臂在两路 gating signal 都为低时沿用上一自然换流状态；有 gating signal 为高时，按强制导通逻辑选择 positive、negative 或 short-circuit mode。各半桥臂状态按四进制权重合成系统 \(\sigma^\*(k)\)，因此判态仍按臂独立，避免把所有桥臂耦合进一个整体开关网络求解。[pdf:E03]（PDF 物理页 3，Eq. (9)–(10)）
2. **用一次 MVO 产生候选状态。** 读取 flag 选择预存的 \(\Delta t\) 或 \(2\Delta t\) BE 系数，计算
   \[
   x^c(k)=P^{\sigma^\*}(k)x(k-1)+Q^{\sigma^\*}(k)u(k).
   \]
   若前一步不是事件步，\(P,Q\) 取普通 \(\Delta t\) 矩阵；若前一步 flag 为 1，则取 \(2\Delta t\) 矩阵。两种情况共用同一个 MVO datapath。[pdf:E04]（PDF 物理页 4，Eq. (14)–(16)）
3. **预测自然状态并生成事件 flag。** 把 \(x^c(k)\) 代入半桥臂端口电流/电压的 blocking criterion，得到预测自然状态。若它相对上一自然状态发生变化，且前一步不是事件步，则令 flag 为 1；下一步 flag 复位。[pdf:E04]（PDF 物理页 4，Eq. (17) 与相邻正文）
4. **修正真实状态。** 正常步直接令 \(x(k)=x^c(k)\)；事件步令 \(x(k)=x(k-1)\)。下一步由于选择了 \(2\Delta t\) 系数，状态从事件前状态一次推进两个小步，补偿冻结的那一步。自然状态随后按 Eq. (19) 更新，必要时先回到 blocking mode，避免越过无电流区。[pdf:E04]（PDF 物理页 4，Eq. (18)–(19)）
5. **FPGA 时序和并行。** 论文把一步分为“预测状态—并行修正各半桥状态—修正状态变量”三阶段。时变矩阵和 \(x^c\) 在 `posedge clk` 更新，switch status、flag 等由 combinational logic 更新；主路径只有一次 MVO，常数 \(R_{\mathrm{ON}}\)、\(R_{\mathrm{OFF}}\) 相关乘法用 shift-add operation（SAO）替代 DSP 乘法。[pdf:E05]（PDF 物理页 5，Fig. 3 与 Section IV）[pdf:E06]（PDF 物理页 6，Fig. 4）

工程实现方面，论文使用 XC7K325TFFG900-2，片上资源总量为 203800 LUT、407600 FlipFlop、445 BRAM 和 840 DSP48；模型由 Vivado 中的 HDL 构建，时钟为 50 MHz，固定仿真步长为 20 ns。SLR 的状态/输入采用 40 bit fixed-point（28 fractional、11 integer、1 sign），系数矩阵采用 34 bit（32 fractional、1 integer、1 sign）；LLC 相应为 37 bit（27 fractional、9 integer、1 sign）和 29 bit（27 fractional、1 integer、1 sign）。[pdf:E05]（PDF 物理页 5，Section IV）[pdf:E06]（PDF 物理页 6，Table I 下方正文）

论文**未报告** fixed-point 的 rounding、saturation、overflow 策略，也未报告由定点量化单独造成的误差。它使用单一 20 ns 固定步长，**未报告** multirate partition、异步 event localization 或步长自适应。实际展示的是开环 gating 下的 FPGA real-time simulation、DAC 输出到示波器，以及独立 LLC 实物波形对比；controller-in-the-loop 的闭环 I/O、plant/controller 延迟预算、接口同步和故障注入协议均**未报告**。外部 EMT 网络的 nodal coupling、输电系统规模、多变换器并联以及与通用 EMT solver 的接口也**未报告**。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文从状态空间模型
\[
\dot{x}=A^\sigma x+B^\sigma u
\]
出发，用 BE 离散为
\[
x(k)=F^\sigma(k)x(k-1)+H^\sigma(k)u(k),
\quad
F^\sigma=[I-\Delta t A^\sigma]^{-1},\quad
H^\sigma=\Delta t F^\sigma B^\sigma .
\]
\(\sigma\) 表示系统开关状态组合。BE 的工程意义是：当前步状态由隐式方程求出，相比 forward Euler 对刚性或谐振动态更稳定；由于各开关组合对应的矩阵可离线预存，实时阶段变为查表加 MVO。[pdf:E02]（PDF 物理页 2，Eq. (1)–(3)）

旧方法用
\[
x^p(k)=F^{\sigma(k-1)}x(k-1)+H^{\sigma(k-1)}u(k)
\]
预测自然换流状态，但 gating signal 或 diode status 任一变化都会令 \(\sigma(k)\ne \sigma(k-1)\)，所以 \(x^p(k)\) 不能普遍替代真实 \(x(k)\)。本文先把 gating signal 决定的强制状态写入 \(\sigma^\*(k)\)，改成
\[
x^p(k)=F^{\sigma^\*(k)}x(k-1)+H^{\sigma^\*(k)}u(k).
\]
这样，当只发生 gating transition 而 diode status 不变时，\(\sigma^\*(k)=\sigma(k)\)，预测即为真实状态；预测误差被限制到自然换流事件。[pdf:E03]（PDF 物理页 3，Eq. (7)–(10)）

对自然状态在 \(k-1\to k\) 发生变化的情形，作者规定事件步
\[
x(k)=x(k-1),
\]
下一步使用
\[
x_{2\Delta t}(k+1)=F_{2\Delta t}^{\sigma^\*}x(k-1)
H_{2\Delta t}^{\sigma^\*}u(k+1),
\]
其中
\[
F_{2\Delta t}^{\sigma^\*}=[I-2\Delta t A^{\sigma^\*}]^{-1},\qquad
H_{2\Delta t}^{\sigma^\*}=2\Delta t F_{2\Delta t}^{\sigma^\*}B^{\sigma^\*}.
\]
直观上，这是把“事件当步冻结”和“下一步跨两步推进”配对，使两步末端重新回到 BE 轨迹附近。作者再用 flag 把普通与 \(2\Delta t\) 系数复用到 \(P,Q\) 中，从而只计算一次 \(x^c=P x+Q u\)。[pdf:E04]（PDF 物理页 4，Eq. (11)–(18)）

这套等价变换依赖一个明确假设：自然换流事件不会在两个连续小步中发生。论文把它表述为在足够小的步长下，连续两步发生 natural switching event “not realistic”。这不是由 BE 本身推出的定理，而是算法正确性的事件稀疏前提；论文没有给出按电路参数、dead time、\(\Delta t\) 和状态斜率计算的充分条件。[pdf:E04]（PDF 物理页 4，Eq. (12)–(13) 之间正文）

## § 7 — 实验设计与结论

**问题 1：一次 MVO 的修正法能否保持 SLR 的稳态精度？**  
实验：作者用 Table I 的 100 kHz 开环 SLR（\(L_r=14~\mu\mathrm{H}\)、\(C_r=40~\mathrm{nF}\)、\(f_r=212~\mathrm{kHz}\)、dead time 300 ns、输入 200 V、额定功率 400 W），以 MATLAB/Simulink 为 reference，并和文献 [30] 的双状态计算法比较，步长均为 20 ns。答案：论文报告 \(i_{Lr}\) 绝对误差小于 0.09 A、\(v_{Cr}\) 绝对误差小于 0.08 V，稳态精度与 [30] 基本一致；进入/离开 blocking mode 时保持一拍造成的影响在该工况下很小。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E07]（PDF 物理页 7，Fig. 6 及正文）

**问题 2：SLR 在故障暂态中能否实时运行？**  
实验：AX7325B FPGA board 通过 14 bit AD9767 DAC 把数字输出送到示波器；作者施加输出短路故障，比较 20 ns RTS 与 reference 的 \(i_{Lr}\)、\(v_{Cr}\)。答案：论文称波形没有错误振荡或 overshoot，且没有 timing error，但未给出该故障段的数值误差上界、硬件在环闭环对象或重复试验统计。[pdf:E07]（PDF 物理页 7，Fig. 7–8 及正文）

**问题 3：方法能否覆盖带次级二极管桥的高频 LLC？**  
实验：作者构建 200 kHz 开环 LLC，\(L_r=14~\mu\mathrm{H}\)、\(L_m=75~\mu\mathrm{H}\)、\(C_r=29~\mathrm{nF}\)、\(f_r=251~\mathrm{kHz}\)、变比 17:3、dead time 250 ns、输入 400 V、额定功率 1 kW；以 20 ns 步长比较 proposed model、[30] 与 reference。答案：论文报告 \(i_{Lr},i_{Lm},v_{Cr},v_o\) 的绝对误差分别小于 0.14 A、0.12 A、4.7 V、0.0097 V。blocking transition 的单步误差峰值高于稳态，但随后由 \(2\Delta t\) 更新恢复。[pdf:E08]（PDF 物理页 8，Table II、Fig. 10 及正文）

**问题 4：RTS 与真实 LLC 硬件是否接近？**  
实验：实物使用 G3R30MT12J MOSFET 和 IPB060N15N5 diode，比较 20 ns RTS 与硬件 \(i_{Lr}\) 波形。答案：200 kHz 下最大电流绝对误差小于 1.8 A。作者同时承认 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 是理想开关模型，忽略寄生参数，因此不能复现开关电压振荡引起的暂态电流振荡。[pdf:E08]（PDF 物理页 8，Fig. 11–12 及正文）

**问题 5：是否真的节省 FPGA 资源和步长？**  
实验：Table III 与 [29]、[30]、[36] 比较。本文 SLR 使用 3447 LUT、36 DSP48、0 BRAM、239 FlipFlop；LLC 使用 2593 LUT、68 DSP48、0 BRAM、984 FlipFlop，步长均为 20 ns。作者称相对 [30]，更新状态变量的乘法数理论上接近减半；同一 XC7K325 上 [30] 的 LLC 行使用 116 DSP48、25 ns 步长。答案：数据支持本文实现能在 20 ns 内完成并减少 DSP 使用，但表中不同文献的 circuit、switching frequency、步长和部分 FPGA 型号并不完全一致，因此它不是严格受控的 apples-to-apples resource benchmark。[pdf:E09]（PDF 物理页 9，Table III 与 Section V-C）

实验没有报告综合后的 worst negative slack、critical-path 数值、功耗、temperature/voltage corner、长时运行统计、随机 gating phase sweep、不同 \(\Delta t\) 的收敛阶、定点与 floating-point 的单独误差，也没有展示多半桥臂规模扩展曲线。因此，“在两个给定模型上实现 20 ns 并节省资源”有直接证据；“对任意 BHPEC 都更准、更省或能稳定扩展”不能从这些实验外推。

## § 8 — Take-aways

**5 句话：**

1. 论文解决的是 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 高频实时仿真中 blocking mode 判态既要准确又不能迭代的问题。
2. 方法先吸收 gating signal 已知状态，再只对自然换流事件做一拍冻结和下一拍 \(2\Delta t\) 补偿。
3. 这一计算重排把主路径压缩为一次 MVO，并保留 BE 与按半桥臂解耦判态。
4. 100 kHz SLR 和 200 kHz LLC 都在 XC7K325 上达到 20 ns 步长，报告的稳态误差和 FPGA 资源结果支持作者的工程 claim。[pdf:E09]（PDF 物理页 9，Conclusion）
5. 最需要警惕的是连续自然换流事件不会发生这一未形式化假设，以及跨论文资源比较并非完全同工况。

**3 句话：**

1. 作者把“每步算两套状态”改成“事件步冻结、下一步补偿”，使 blocking-aware BE 求解只需一次 MVO。
2. 两个谐振变换器的 FPGA 实现证明了 20 ns 的可行性和较低 DSP 占用，但验证范围仍是开环、固定拓扑和给定工况。
3. 方法是否真正通用，取决于事件是否足够稀疏，以及在更强换流耦合、步长错相和寄生振荡下能否保持判态正确。

**1 句话：**

这是一种用稀疏事件修正换取 FPGA 主路径减半的 blocking-mode 实时仿真方法，其工程证据扎实到两个样机，但通用性尚未被事件密集型反例检验。

## § 9 — 最脆弱的假设

最脆弱的假设是：在所选 \(\Delta t\) 下，自然换流状态不会在连续两个离散步中变化。算法在事件步令 \(x(k)=x(k-1)\)，并假设下一步可以安全地用 \(2\Delta t\) 矩阵跨过两步；如果下一步又有自然换流，所选矩阵对应的 \(\sigma^\*\) 已不再覆盖整个 \(2\Delta t\) 区间，补偿就失去物理和数值依据。[pdf:E04]（PDF 物理页 4，Eq. (11)–(18)）

这一假设可能在电流贴近零点且斜率快速反转、dead-time 边界与采样边界接近、两个耦合半桥臂几乎同时换流、控制产生窄脉冲，或 \(\Delta t\) 相对局部换流时间不够小时失效。论文给出的支持是两个 20 ns 工况中的 blocking transition 只产生单步误差峰，并能在下一步恢复；但它没有扫 gating phase、初始电流、dead time、参数容差或事件间隔，也没有给出“事件至少相隔两步”的可检查条件。[pdf:E07]（PDF 物理页 7，Fig. 6 与正文）[pdf:E08]（PDF 物理页 8，Fig. 10 与正文）

## § 10 — 最小复现实验

一周内最值得复现的是 SLR 的“单 MVO 仍保持 blocking transition 精度”这一点，而不是先做完整 FPGA 板级移植。

1. 按 Table I 实现理想 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) SLR，使用论文 Appendix 的状态矩阵；同时实现 proposed Eq. (8)–(19)、[30] 式双 MVO predictor-corrector，以及一个小步长或迭代判态 reference。
2. 固定主试验为 20 ns、100 kHz、dead time 300 ns；把 gating edge 相对仿真网格的相位扫过一个 20 ns 区间，并对 zero-current 初值作小范围扫描。
3. 记录每次 blocking enter/exit 的事件间隔、是否出现连续两步事件、\(i_{Lr}\) 与 \(v_{Cr}\) 的峰值/均方误差、过零振荡次数，以及每步乘法数量。
4. 若 proposed method 在所有基准相位下都无漏判，\(i_{Lr}<0.09\) A、\(v_{Cr}<0.08\) V，且 MVO 数约为 baseline 的一半，则支持论文的核心 claim；若存在连续事件导致漏判、持续振荡或补偿后误差不回落，则直接反驳其关键适用前提。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E07]（PDF 物理页 7，Fig. 6）

这一步先用 floating-point 验证算法，再切换到论文的 40/34 bit fixed-point 格式；否则无法区分算法误差与未报告的 rounding/overflow 策略。资源和 timing 可以在第二阶段用同一器件、同一约束综合，避免跨论文表格的工况差异。

## § 11 — 最强反例设计

最强反例不是再换一种普通 LLC 参数，而是主动制造“连续两个小步发生自然状态变化”的事件密集场景。构造一个半桥驱动的谐振支路，使电感电流在 dead time 内贴近零，并通过初始 capacitor voltage、gating edge phase 和 \(\Delta t\) 的组合，让预测判态在 \(k\) 从 positive/negative mode 进入 blocking mode、在 \(k+1\) 又离开；再加入第二个耦合半桥，使两臂的自然换流相隔不足一个主步长。

用 event-resolved variable-step reference 和迭代 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 模型作为真值，比较本文算法是否选错 \(2\Delta t\) 矩阵、漏掉第二次状态变化，或产生持续过零振荡。若错误仅来自寄生参数缺失，那只是器件模型局限；若即便使用同一理想开关模型也因连续事件而失败，就击中了 prediction-correction 机制本身。这个反例还应扫 gating-to-grid phase，因为论文当前两个固定工况可能只是没有把换流边界落在最不利采样位置。

## § 12 — Follow-up Research Idea

在 power electronics realtime simulation 领域，高影响工作通常需要同时给出明确的数值机制、可综合的延迟/资源结果、硬件或 HIL 级实验，以及跨拓扑的适用边界。基于上述最脆弱假设，一个更有潜力的候选方向是：把“blocking mode 判态”改写成**可认证的 hybrid-event envelope** 问题，而不是继续默认每个宏步最多一个自然换流事件。

（a）未满足需求是：20 ns 并不能自动保证所有拓扑、参数和 gating phase 下事件稀疏，现有方法缺少运行时可检查的正确性边界。  
（b）研究价值在于同时提供“什么时候可安全走单 MVO 快路径”和“什么时候必须局部细分或回退”的证书，使速度优势不再依赖不可观测假设。  
（c）可借鉴 hybrid systems 的 event localization、interval arithmetic 和 reachability bound：用当前 \(i_h,v_h\) 及其斜率区间预测下一宏步内可能穿越的 blocking boundary 数量；若至多一次，走本文路径；若可能多次，仅对相关半桥臂启动局部 micro-step，而不拖慢全系统。  
（d）第一个证伪实验就是第 11 节的连续事件相位扫描：若 envelope 经常误判“至多一次”，或保守回退率高到抵消一次 MVO 的收益，这个想法即失败。  
（e）它与本文的实质区别是把事件稀疏从默认前提变成显式、在线、可验证的求解条件，并允许一个宏步内多个自然换流事件；这改变了问题定义，而不只是再加一个 correction flag。

该方向只由本文证据和 hybrid-system 工具类比推出，相关工作尚未完整检索，因此是候选研究想法，不声称 novelty。
