# Embedded Fully FPGA-Based Real-Time Simulators for Static Power Converters With Power Switch Characteristics Approximated by Identification

作者：Lahoucine Idkhajine；Eric Monmasson

出处：IEEE Transactions on Industrial Electronics，Vol. 69，No. 9，pp. 9624–9633

年份：2022

DOI：10.1109/TIE.2021.3112999

Zotero key：6DT5727A

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是 device-level real-time simulation 中一个很具体的矛盾：模拟器既要在几十纳秒的时间尺度上重现功率开关的导通、关断过渡，又要和控制器一起装进资源有限的 FPGA，不能依赖每一步都求解大型非线性电路。作者把约束归纳为三项同时存在的压力：开关模型要足够细、仿真步长要足够短以覆盖快速瞬态、硬件资源却不能无限扩张；当模型还要嵌入控制器旁边，用于诊断、健康监测或状态估计时，这个矛盾更尖锐。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

论文提出的答案不是更快地求解完整器件方程，而是先用 system identification 把每个开关的电压、电流过渡压缩成系数随状态切换的离散 transfer function，再把开关单元及 transfer function 全部并行映射到 FPGA。作者在摘要中把目标明确限定为“proof of concept”，并以半桥 dc–dc、全桥 dc–ac、5-level 与 9-level cascaded H-bridge 为案例，而不是声称已经形成覆盖任意拓扑、任意器件和任意工况的通用求解器。[pdf:E01]（PDF 物理页 1，Abstract）

工程价值有两层。第一层是 HIL：如果开关瞬态能以 50 ns 步长运行，控制器测试看到的不再只是理想开关。第二层是 embedded RT digital twin：模型可与控制器共置，为在线诊断或健康监测提供参考变量。需要注意，第二层在本文中只是作者提出的应用潜力；论文实际验证的是仿真波形、FPGA 时序与资源，不是在线诊断任务本身。

## § 2 — 前人工作与不足

作者把紧密相关方法分为四类，并给出了各自的工程瓶颈。[pdf:E02]（PDF 物理页 2，Section I）

- Associate discrete circuit（ADC）用 ON 状态的电感、OFF 状态的 RC 等组合代替开关，但精细描述每个器件时，admittance matrix 既要随开关状态和工况变化，又可能需要在线求逆。已有工作通常固定矩阵以换取实时性，时间步长多在百纳秒量级。
- Nonlinear equivalent-circuit 用可调 RC 与受控源表示非线性瞬态，并用 Newton–Raphson 等迭代法求整个网络。它能接近离线工具结果，但迭代和处理延迟使其更适合小规模、soft-switching converter，文中概括的步长通常为微秒量级。
- Piecewise linear model 把一次换流分成多个阶段，每段用线性式近似。作者引用的 FPGA 工作已做到 50 ns，但代价是需要投入较多硬件设计工作来优化 time/area。
- Curve fitting 把实验或离线仿真波形存进 lookup table，每步读取并按稳态电压、电流缩放。引用工作曾以 80 MHz Altera Stratix FPGA 做到 12 ns，但当拓扑复杂、每只开关都要在多种电气/热工况下单独表征时，存储量会迅速成为问题。

本文试图组合 linear model 和 curve fitting 的优点：仍从波形辨识器件的真实过渡，但不存整段波形，而是存 transfer function 系数；再用 parallel-form IIR 让模型阶次主要增加并行资源，而不直接拉长关键执行路径。这个定位很重要：它不是在同一硬件、同一器件、同一误差指标下证明全面优于上述四类方法，而是给出一种新的 time/area 取舍，并用多个拓扑证明其可实现性。[pdf:E02]（PDF 物理页 2，Section I 的方法定位与 contributions）

## § 3 — 重建作者的思考路径

以下是基于论文背景和实现顺序重建的思考路径，不是作者逐句陈述的研究日志。

第一步，从失败模式出发：如果在线保留完整器件非线性并求解全网，迭代与矩阵运算会占满几十纳秒预算；如果直接回放波形，则跨器件、跨工况的存储规模又会失控。研究者因此会寻找一种比波形表更紧凑、比器件方程更容易流水化的动态表示。

第二步，把一次开关换流看成受 gate event 触发的局部 step response。只要能够从电压、电流波形中截取 turn-ON 与 turn-OFF 时间窗，就可以分别辨识离散线性模型，再在运行时按状态切换系数。论文的 Fig. 1 正是从“采集每只开关波形”和“把变换器拆成 switching cell”两条路径汇合到 system identification、digital filter realization、FPGA implementation 与 RT validation。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Section II）

第三步，利用功率变换器结构上的局部重复：一个 switching cell 含两只 transistor 与两只 diode，cell 的输入是 \(V_{dc}\)、\(I_L\) 和 gate signals，输出是器件电压、电流。把每个 cell 做成相同接口的 RT model 后，拓扑扩展变成复制并并联执行 cell，而不是扩大一个集中式求解器。[pdf:E03]（PDF 物理页 3，Fig. 2）

第四步，处理“辨识阶次越高、延迟越大”的潜在反噬。普通 direct-form IIR 的递推链会把模型阶次带进关键路径；把高阶函数分解成并行的一阶、二阶 section 后，关键延迟由最慢的二阶 section 决定。由此得到本文的核心工程构型：开关内并行、cell 间并行、拓扑层再并行。

## § 4 — 核心 Intuition

不要在实时步内重新求解开关的完整非线性物理过程，而要提前从其 turn-ON/turn-OFF 波形中辨识一个紧凑的局部动态映射，运行时只按开关状态和事件延迟切换系数。再把高阶映射拆成并行的一阶、二阶 IIR section，并把所有开关单元并行执行，模型精度主要消耗 FPGA 面积，而不是直接消耗仿真步长。其成立的物理前提是：待模拟工况下的换流瞬态确实能由这些局部、状态条件化的线性动态充分代表。

## § 5 — 具体方法与完整 Pipeline

以半桥 proof of concept 为主线，完整 pipeline 如下。

1. **取得表征数据。** 初始案例使用 PSPICE 中 STGW15M120DF3 IGBT 的波形，开关频率为 100 kHz，\(V_{dc}=600\ \mathrm{V}\)、\(I_L=40\ \mathrm{A}\)，并把离线波形采样、平均到 50 ns resolution。[pdf:E03]（PDF 物理页 3，Section II-A）
2. **切分事件时间窗。** 对每只 transistor 分别截取 turn-ON 与 turn-OFF 的电压、电流过渡。Fig. 3 显示时间窗不是从 gate edge 机械开始，而是在 gate edge 后加入针对电流和电压的独立 delay；这些 delay 应由实验测量或 datasheet 特性取得，并可能随真实工况变化。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Section II-B）
3. **辨识状态条件化模型。** MATLAB/Simulink System Identification Toolbox 从每段测量数据生成 discrete-time linear model。作者用 trial-and-error 调整阶次，目标 fitting threshold 为 90%；半桥案例得到 third-order 结构。每个 cell 形成四个统一 transfer function：\(H_{iT1}(z)\)、\(H_{vT1}(z)\)、\(H_{iT2}(z)\)、\(H_{vT2}(z)\)，各自在 ON/OFF 时读取不同系数。
4. **运行时重配置。** Reconfiguration block 先根据 gate signal 与 \(I_L\) 符号判断 transistor state；状态变化后等待对应 delay，从 memory block 读入系数，并翻转 transfer function 的 unit-step input。这里没有每步重新辨识，在线工作只是查系数、切状态和执行 filter。[pdf:E04]（PDF 物理页 4，Section II-B）
5. **后处理。** 四个 transfer function 输出 per-unit transistor variables；postprocessing block 用 \(V_{dc}\) 与 \(I_L\) 缩放，并利用它们的符号恢复剩余 diode variables。论文展示了数据路径，但没有报告饱和、舍入、overflow 或系数量化误差的独立分析。
6. **变成可定时的数字结构。** 每个高阶 transfer function 被拆成 parallel-form IIR。半桥的 third-order 情形由一个二阶 IIR、一个一阶 IIR 和一个乘法因子并行组合；四个 transfer function 同时运行。每个 ON/OFF、每个函数存 7 个系数，因此一个 cell 共存 56 个系数。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Section II-C）
7. **FPGA 映射与时间推进。** 设计由作者手工完成，没有使用 code generation；目标是 Xilinx Artix-7 XC7A200T-2（AC701），system clock 200 MHz，数值格式 25Q18 fixed point。Xilinx pipelined IP 执行算术，25-bit multiplier 完全流水化、5 个 clock cycle 出结果；总设计为 9-cycle latency、45 ns execution time，因而选择固定 50 ns RT step。[pdf:E05]（PDF 物理页 5，Section II-D）[pdf:E06]（PDF 物理页 6，Section II-D）
8. **替换数据源并按拓扑复制。** 作者先用真实 Buck converter 数据替换 PSPICE 数据：负载 \(R=25\ \Omega\)、\(L=3\ \mathrm{mH}\)，器件为 CMF20120D SiC MOSFET，开关频率 500 kHz，数据同样以 50 ns resolution 采样和平均；重新辨识系数后复用同一数字结构。[pdf:E07]（PDF 物理页 7，Section II-F）随后，Full-bridge 用两个独立 switching cell，5-level 与 9-level cascaded H-bridge 分别由两个和四个 H-bridge module 构成；cell、load model 与各 bridge model 在层级间继续并行。[pdf:E08]（PDF 物理页 8，Fig. 13 与 Section III）论文没有使用 adaptive time step；控制器/PWM 与 50 ns simulator 通过独立时钟和误差估算协调。除文中给出的 RL load 实现外，更一般的网络求解接口、代数环处理和跨 cell 寄生耦合均未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有从 semiconductor physics 推导开关模型，核心数学是“辨识得到的离散 transfer function 如何变成定时可预测的 FPGA filter”。

Appendix 给出的 third-order 统一形式为

\[
H(z)=
\frac{b_0+b_1z^{-1}+b_2z^{-2}+b_3z^{-3}}
{1+a_1z^{-1}+a_2z^{-2}+a_3z^{-3}}.
\]

其中 \(z^{-1}\) 表示一个采样延迟，\(b_i\) 决定输入历史如何进入输出，\(a_i\) 决定输出历史如何反馈。系数不是在线优化量，而是离线 system identification 的结果；运行时依据 ON/OFF state 选用一组系数。[pdf:E09]（PDF 物理页 9，Appendix 公式与 PSPICE coefficient table）

对于一般 numerator order \(M\) 与 denominator order \(N\)，作者采用 parallel decomposition：把 \(H(z)\) 展开成多个二阶 IIR、至多一个一阶 IIR，以及在 \(M\ge N\) 时出现的 \(K=M-N\) 阶 FIR 部分。半桥中 \(M=N=3\)，所以 \(K=0\) 的高阶 FIR 不出现，只留下二阶、一阶 IIR 和直接乘法项。并行结构的工程含义是：增加 filter order 会增加 section 数量和乘加资源，但只要所有 section 真正并行，执行时间由最慢的二阶 section 决定，而不是随总阶次串行增长。[pdf:E04]（PDF 物理页 4，Fig. 4）[pdf:E05]（PDF 物理页 5，Section II-C）

Full-bridge 案例还显式估算了 PWM 与 simulator 的同步误差。13-bit carrier 使用 variable-step counter：

\[
F_{\mathrm{PWM}}
=\mathrm{step}\,F_{\mathrm{PWM\_clk}}\,2^{-13}
=100\ \mathrm{kHz},
\]

\[
\mathrm{Res}_{\mathrm{PWM}}
=\mathrm{step}\,T_{\mathrm{PWM\_clk}}
\approx 30.5\ \mathrm{ns},
\]

\[
\varepsilon_{\mathrm{sync}}
=2F_{\mathrm{PWM}}
\left(\mathrm{Res}_{\mathrm{PWM}}+T_{\mathrm{sim}}\right)
=1.61\%.
\]

因 gate signal 每个 PWM period 变化两次，式中有系数 2；作者据此判断同步误差对负载瞬时平均电压可忽略。[pdf:E08]（PDF 物理页 8，Section III）

需要明确数学闭合的边界：论文没有公开 System Identification Toolbox 的具体 objective、regularization、模型选择准则、稳定性约束或置信区间，也没有推导“任意阶并行实现都保持 45 ns”这一普遍结论。45 ns 是本文选定阶次、IP pipeline、器件与 200 MHz 时钟下的实现结果。[pdf:E06]（PDF 物理页 6，Section II-D）

## § 7 — 实验设计与结论

**问题一：第三阶辨识模型能否重现用于辨识的器件换流波形？**  
实验先以固定工况 PSPICE 波形辨识半桥模型，再比较 MATLAB/Simulink filter、FPGA 输出与初始数据。作者报告，在整个 PWM period 上，平均 fitting error 为 current 0.066%、voltage 0.3%；FPGA 结果与 MATLAB/Simulink 结果相同，并保持相对初始波形的 fitting level。[pdf:E04]（PDF 物理页 4，Fig. 5 与 Section II-A）[pdf:E07]（PDF 物理页 7，Section II-E）答案是在已辨识的固定数据与工况内可以高拟合，但这不是 held-out generalization。

**问题二：同一 FPGA 结构能否接受真实器件数据，而不重新设计 datapath？**  
实验使用 CMF20120D SiC MOSFET 的 Buck converter 实测 turn-ON/OFF 波形，重新辨识 third-order 系数，然后复用同一数字结构。Appendix 报告的四项 fitting level 分别为：current turn-ON 91.87%、current turn-OFF 96.18%、voltage turn-ON 98.92%、voltage turn-OFF 96.99%。[pdf:E10]（PDF 物理页 10，Appendix experimental coefficient table）答案是这一个实验器件和工况下可以复用结构；论文没有展示跨温度、跨 gate resistance、跨 \(V_{dc}\)/\(I_L\) 的同一系数泛化。

**问题三：完整 cell 能否在 FPGA 上闭合 50 ns 固定步长？**  
设计运行于 200 MHz，25-bit multiplier 用 5-stage pipeline；作者报告总 latency 9 cycles、execution time 45 ns，进而使用 50 ns simulation step。56 个参数占用 1.4 Kb RAM，即目标 RAM 的 0.011%。[pdf:E06]（PDF 物理页 6，Section II-D）答案是在 XC7A200T-2 的这一手工设计上可以时序闭合；论文未给出独立的 post-route timing report、功耗或温升数据。

**问题四：扩展拓扑后是否仍保持实时步长与可接受误差？**  
Full-bridge 案例使用 \(R=5\ \Omega\)、\(L=15\ \mathrm{mH}\)、\(V_{dc}=600\ \mathrm{V}\)、100 kHz PWM 和 200 Hz sinusoidal reference，保持 50 ns step。其资源为 4318 Flip-Flops、2418 LUT（作者写为 2% available slices）和 122 DSP48E（16%），load current average relative error 为 0.6%。9-level 模型同样保持 50 ns step，使用 13640 Flip-Flops、7689 LUT（6%）和 470 DSP48E（64%）；5-level/9-level 波形以 1 μs resolution 采集，作者报告 average fitting error 小于 2%。[pdf:E08]（PDF 物理页 8，Fig. 13 与 Section III）[pdf:E09]（PDF 物理页 9，Sections III–V）答案是本文所测 1、2、4、8 个 switching-cell 规模仍保持固定步长，但 DSP 占用已随 9-level 案例升至 64%，作者也承认复杂拓扑还需进一步优化资源。

**不得外推的范围。** 全文没有同硬件条件下与 ADC、nonlinear equivalent-circuit、piecewise linear 或 lookup-table 方法的 head-to-head benchmark；没有闭环 HIL instability/fault test；没有多温度、多老化状态、器件批次、寄生参数或 hard/soft switching 混合工况 sweep；没有报告长期数值稳定性、能量误差或开关损耗误差。因此证据支持“固定案例上的实时高拟合与拓扑复制”，不支持“在未知工况下保持器件级物理准确性”。

## § 8 — Take-aways

**5 句话**

1. 论文把开关器件的 turn-ON/turn-OFF 波形辨识成状态切换的离散 transfer function，避免在每个实时步内求解完整非线性网络。
2. 高阶函数被拆成并行的一阶、二阶 IIR section，使模型阶次主要增加面积，而不直接增加关键执行时间。
3. 在 Artix-7、200 MHz、25Q18 实现中，作者报告 9-cycle latency、45 ns execution time 和 50 ns fixed simulation step。[pdf:E06]
4. 半桥、全桥、5-level 与 9-level 案例展示了同一 cell 构型的层级复制，但 9-level 已消耗 64% DSP，资源扩展不是免费的。[pdf:E09]
5. 最关键的证据缺口不是训练波形拟合度，而是模型对未辨识电气、热、寄生与老化条件的 held-out 有效性。

**3 句话**

1. 这是一种用离线 identification 换取在线确定性时延的 FPGA device-level RT modeling 方法。
2. 其真实贡献是把 coefficient switching、parallel IIR 和 cell-level full parallelism 组合成可运行的 50 ns proof of concept。
3. 其真实边界是验证集中在已辨识波形和少数固定拓扑工况，尚未证明跨条件的器件模型能力。

**1 句话**

论文证明“学到的开关瞬态可以被并行流水化到 50 ns”，但没有证明“在未见工况下仍是同一个真实开关”。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**给定 gate state、事件 delay、\(V_{dc}\) 与 \(I_L\) 后，开关的电压/电流瞬态可以由一组局部线性 transfer function 表示；未显式建模的温度、gate driver、寄生回路、器件老化和相邻 cell 耦合，要么不重要，要么能通过预存另一组系数解决。**

这个假设一旦失效，full parallelism 仍然可以很快，但得到的只是很快地产生错误瞬态。尤其是同样的 \(V_{dc}\)、\(I_L\) 和 gate command，在不同 junction temperature、gate resistance 或 commutation-loop inductance 下可能产生不同的 delay、overshoot、ringing 和 switching energy；这些 hidden condition 没有进入本文 transfer function 的显式输入。此时单一状态到单一输出轨迹的映射本身就不再唯一，单纯提高阶次或把 filter 做得更并行不能修复。

论文为该假设提供的证据是：固定 \(600\ \mathrm{V}/40\ \mathrm{A}\) PSPICE 案例具有很低的 period-average fitting error；一个 500 kHz SiC Buck 实验也能用 third-order 结构获得 91.87%–98.92% 的 fitting level；作者还说明系数“可以”扩展到不同电气/热工况。[pdf:E03][pdf:E10] 缺少的证据更关键：没有 coefficient grid 的实际构造、在线工况识别、不同网格间插值、leave-one-condition-out 测试或误差上界。因此“可扩展到真实电气/热环境”目前是作者提出的潜力，不是被本文实验闭合的结论。

## § 10 — 最小复现实验

一周内最值得复现的是：**一只开关的 third-order parallel IIR 是否能同时满足波形误差和 50 ns hardware deadline。** 不需要先复现完整 9-level converter。

1. 用 SPICE 建立论文半桥条件：STGW15M120DF3、\(V_{dc}=600\ \mathrm{V}\)、\(I_L=40\ \mathrm{A}\)、100 kHz switching，并以 50 ns resolution 导出 \(i_T\)、\(v_T\) 的 turn-ON/OFF 窗口。若器件模型不可取得，可使用可公开取得的等额定器件，但必须把它标为结构复现而非数值复现。
2. 对四段波形各辨识一个 third-order discrete transfer function，记录训练窗外的完整 PWM-period 误差；再将其分解为二阶、一阶 parallel IIR 与直接项。
3. 用 25Q18 fixed point 实现一个 transistor 的 current/voltage datapath，再复制为一个 switching cell；在 Artix-7 或等价 FPGA 上执行 synthesis 与 place-and-route，目标 clock 200 MHz。
4. 测量四类结果：floating-point 与 fixed-point waveform error、训练窗外 error、post-route worst negative slack、从 event 到输出的 cycle latency；资源只作为次要指标。
5. 支持核心 claim 的标准是：200 MHz 时序闭合、总 execution time 不超过 50 ns，并且 fixed-point 相对 SPICE 的误差接近论文量级，至少不因 parallel decomposition 明显恶化。若必须降低时钟、增加跨步串行计算，或固定点误差显著高于 floating-point identification error，就反驳“高拟合不牺牲 timing”的核心实现 claim。

这个实验仍不会验证跨工况泛化，但能把论文最核心的 identification-to-hardware 链条压缩到一周内，并明确区分“模型本身拟合失败”和“FPGA 映射失败”。

## § 11 — 最强反例设计

最强反例不是再找一个更复杂拓扑，而是构造**相同显式输入、不同真实瞬态**的不可辨识场景。

设计一组 double-pulse tests：固定 \(V_{dc}\)、\(I_L\) 与 gate command，使本文模型看到完全相同的输入；只改变模型未观察到的 commutation-loop inductance、gate resistance 与 junction temperature。用训练条件辨识系数，然后不重辨识地预测其他条件下的 \(v_T/i_T\)、overshoot、ringing frequency、turn-on/off delay 与 switching energy。为了排除“只是整体缩放错误”的解释，要求测试条件保持稳态电压、电流相同，差异只来自 hidden condition。

如果不同硬件条件产生显著不同的过渡，而同一 \(H(z)\) 只能输出一条轨迹，那么反例在结构上成立：误差不是系数阶次不够，而是模型输入缺少决定性状态。进一步把多个 cell 接到共享 dc link，并引入可控 bus inductance；若单 cell 独立模型在 isolated test 中拟合良好，却在同步换流时系统性漏掉耦合尖峰或 switching energy，这会直接挑战“把 converter 拆成独立 cell 后仍保持器件级 fidelity”的主机制。

反例的判据不应只看视觉波形。至少报告 peak-voltage error、delay error、ringing-frequency error、per-event energy error，以及这些误差相对原论文 50 ns step 与 fitting level 的量级。若模型在训练点仍维持高 fitting、却在同 \(V_{dc}/I_L\) 的隐藏条件变化下失效，就排除了“FPGA 数值实现不好”这一替代解释，并把问题定位到状态表示本身。

## § 12 — Follow-up Research Idea

在 power electronics 与 industrial electronics 中，高影响研究通常同时要求：器件或系统层面的物理可信度、严格的跨工况实验、可复现的硬件时序与资源结果，以及对实际 HIL、诊断或可靠性任务的增益。仅把另一个拓扑复制进相同架构，通常不足以形成非增量贡献。

候选方向是：**带可证伪误差包络的 condition-aware switching digital twin**。它不再把 operating condition 仅视为人工选择 coefficient bank 的索引，而是把温度、寄生参数、gate driver 与老化状态作为 latent condition 在线估计；模型输出同时给出开关瞬态和当前误差包络。底层仍保留本文的 parallel IIR 以守住硬实时预算，但系数由低维 Linear Parameter-Varying（LPV）模型或 hybrid state estimator 连续生成，并加入 passivity/energy consistency 约束，避免多个 cell 组合后出现非物理能量。

（a）驱动需求是：设备在线温升、老化和回路变化时，固定 coefficient bank 没有可验证的有效范围。  
（b）研究价值在于把“某个训练波形拟合得好”改写为“在声明的工况集合内，50 ns digital twin 的误差和失效信号可被验证”，这直接服务 HIL 与 health monitoring。  
（c）可借鉴相邻领域的 LPV/subspace identification、hybrid systems、set-membership estimation、conformal prediction 与 reachability analysis；选择何者要服从 FPGA 延迟，而不是先堆叠算法。  
（d）第一个证伪实验是 leave-one-condition-family-out double-pulse test：按温度、gate resistance、loop inductance 留出整类条件，检查真实 \(v_T/i_T\) 是否落入预测包络，同时测量实现是否仍闭合 50 ns。若包络频繁漏真值、宽到失去诊断意义，或 condition estimator 破坏硬实时预算，该想法即被证伪。  
（e）它与本文的实质区别不是“多存几组系数”，而是显式承认 hidden condition、在线估计其状态，并对未见工况给出可检验的不确定性与组合一致性。

本卡只使用论文 PDF，没有补检外部相关工作；因此这是由第 9 节证据缺口驱动的候选研究想法，不声称 novelty。论文自己的 References 已包含 FPGA device-level simulation、parallel-form IIR 与 reliability/digital-twin 邻接方向，可作为后续正式检索的起点。[pdf:E10]（PDF 物理页 10，References [17]–[26]）
