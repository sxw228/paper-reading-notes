# FPGA-Based Real-Time Simulation of a DC/DC Converter

- 作者：Matthias Deter、Quang Ha、Markus Plöger、Frank Puschmann [pdf:E11]
- 出处：ATZelektronik worldwide，Volume 9，2014
- DOI：10.1365/s38314-014-0236-8
- Zotero key：25FW7XW4

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样设计一个更好的 DC/DC converter”，而是“怎样让真实 ECU 在 hardware-in-the-loop（HiL）测试中看到一个响应足够快、又能保留开关细节的 converter plant”。车辆电气化把 12 V 系统、high-voltage battery、supercapacitor 等不同电压层级连接在一起，DC/DC converter 的 ECU 因而直接参与整车能量流管理；作者据此把可实时测试的 converter 模型视为 ECU 开发工具链中的缺口 [pdf:E01]。

真正困难在时间尺度。功率半导体既有由 gate signal 触发的外部事件，也有二极管电流过零关断这类由电路状态触发的内部事件。离线仿真可以用 variable step size 和 zero-crossing detection 追踪它们，而实时平台只能在固定时刻推进；事件落在两个采样点之间，就会被推迟或错判 [pdf:E02]。作者给出的工程经验是，为减小这种延迟误差，仿真频率与开关频率之比应大于 100；但目标 converter 的开关频率约为 100 kHz，普通实时处理器难以达到相应计算速率 [pdf:E02]。

因此，本文的价值在于把“实时性”从只要求每个 PWM 周期算完一次，提升为在一个 PWM 周期内多次解析电流纹波、换流和控制闭环。作者报告，FPGA 路线把可测的硬件输入到输出延迟由 processor-based model 的典型 25–30 μs 降至约 1 μs，并每 100 ns 输出一次模拟电流 [pdf:E02][pdf:E04]。这些数字说明了 FPGA 的潜力，但不是本文所有工况下的误差保证。

## § 2 — 前人工作与不足

最直接的 prior system 是 SimPowerSystems 一类离线电路仿真器。它通过 variable step size 与 zero-crossing detection 精确定位开关时刻，精度高，却不能保证每个计算周期都在固定 wall-clock deadline 前结束，因此不能直接承担 ECU 的实时闭环 HiL [pdf:E02]。

实时 HiL 中常见的替代方案是 mean-value model：不逐个重建半导体开关事件，而是模拟一个周期内的平均行为。论文指出，这类模型在电驱 HiL 中可用于最高约 20 kHz 的开关频率，并且某些处理器在仿真频率等于开关频率、即 sampling ratio 为 1 时仍能给出够用的平均精度 [pdf:E02]。不足不是“平均模型从未有效”，而是它抹掉了本文关心的内部换流与 ripple；论文还指出，measurement variable 返回控制器会产生 1–2 个 sample time 的延迟，对高度动态的 DC/DC converter 往往不可接受 [pdf:E02]。

已有 FPGA oversampling 与 power-electronics HiL 工作为本文提供了平台方向，但这篇短文聚焦的是一个具体 phase-shifted PWM full-bridge ZVS converter：如何把其有效开关拓扑、内部二极管状态和离散 differential equations 组织成能在 FPGA 上实时执行的模型 [pdf:E03][pdf:E04]。论文没有做系统性的 prior-work benchmark，因此这里能确认的是工程实现差异，不能仅凭本文声称更广泛的学术 novelty。

## § 3 — 重建作者的思考路径

可以把作者到达该方案的路径重建为四步。第一，工程人员先观察到 converter ECU 的闭环是否稳定，取决于仿真器能否及时返回电压、电流，而不只是最终稳态是否正确；processor model 的 25–30 μs 典型 I/O latency 已接近甚至跨过多个高速开关事件 [pdf:E02]。第二，mean-value model 虽然便宜，却把最容易影响控制器的 ripple、二极管过零和 commutation 隐去了 [pdf:E02]。

第三，若继续沿“统一连续电路方程、每步求解整个网络”的方向增加处理器算力，固定步长下仍要承担开关组合变化和过零判定的串行负担。更自然的重构是：先问当前是哪一种 effective topology，再只执行该 topology 对应的状态更新。对于论文的电路，Q5、Q6 可控，使 power stage 可分成四种有效拓扑 [pdf:E04][pdf:E05]。

第四，FPGA 的优势不只是 clock 快，而是可以把状态判定和不同 topology 的 `(u,i) Calculator` 做成固定数据通路。于是得到“State Detector 选择方程，Calculator 推进一步，新的电压电流再反馈给 Detector”的闭环结构 [pdf:E08]。这是基于论文结构的合理重建，不是作者逐字陈述的发现过程。

## § 4 — 核心 Intuition

核心 intuition 是：不要在每个实时步内重新求解一个带所有开关的通用电路，而要把 converter 预先拆成少数 effective topologies，用 State Detector 在运行时选择当前有效的那组 differential equations [pdf:E04][pdf:E08]。FPGA 让这套“判状态—算电压电流—反馈再判状态”以固定、很短的节拍执行；真正保留内部换流细节的关键，则是把 Q5、Q6 的电压和电流、尤其是零电流条件纳入状态判定 [pdf:E06]。

## § 5 — 具体方法与完整 Pipeline

论文对象是 phase-shifted PWM full-bridge ZVS converter。高压侧由 Q1–Q4 组成 full bridge，经含 C1、L1、R1 的 transformer 支路耦合到低压侧；低压侧包含 Q5、Q6、L2、L3 和 C2 [pdf:E03]。Q1/Q2 与 Q3/Q4 分别互补，bridge legs 之间的 phase shift 调节 transformer winding L1 的电流；低压侧若主动控制则可支持双向能流，但本文实现仍未完成 bipolar energy-flow 扩展 [pdf:E04][pdf:E07]。

以“ECU 把相移从 0 改到 25%”为例，完整 pipeline 如下：

1. **输入与高压侧等效。** FPGA 接收 Q1–Q4 的控制，论文把高压侧 power electronics 等效为 voltage generator；施加到当前 topology 的电压由 primary current 和 Q1–Q4 状态决定 [pdf:E04]。
2. **检测当前 topology。** State Detector 同时查看 Q1–Q4 控制以及 Q5、Q6 的电压和电流，判断四种 effective topologies 中哪一种有效，并输出 `States` [pdf:E04][pdf:E05]。当 Q5/Q6 的主动控制撤去，反并联二极管接管电流；State Detector 继续观察支路电流，检测到 zero current flow 后才结束 diode–diode 或 diode–MOSFET commutation [pdf:E06]。
3. **执行对应状态更新。** `(u,i) Calculator` 为每一种有效 topology 保存相应 differential equations，只计算当前激活 topology 的电压与电流，再把 `(u,i)` 反馈给 State Detector，形成下一步判定所需状态 [pdf:E04][pdf:E08]。模型还纳入 transformer leakage inductance、transformer resistance、semiconductor forward voltage 与 resistance，避免把关键寄生量完全理想化 [pdf:E06]。
4. **固定时序映射。** 整体模型用 Xilinx System Generator 和 dSpace XSG Utils 建立，以 discrete timing 和 fixed-point arithmetic 执行。作者报告正常模型 step size 为 60 ns，可面向最高 150 kHz 的 control frequency 做 quasi-continuous simulation [pdf:E06]。
5. **输出与闭环。** 电压、电流由 FPGA 持续输出给 ECU。论文早先给出的系统说明是模拟电流每 100 ns 输出一次；验证波形记录时又把 observation resolution 调到 50 ns [pdf:E04][pdf:E07]。这三个时间量分别描述模型步长、一般输出节拍和该次观察分辨率，不能混写成同一个指标。

论文称 topology 变化时只需识别并实现新的 effective structures，framework 可以继续使用 [pdf:E06]。但它没有展示第二种 converter 的迁移结果，因此“generic”在本文中仍是架构主张，不是跨拓扑实验结论。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有打印具体 differential equation、离散化公式、transformer ratio、元件参数或 fixed-point word length，所以不存在可忠实重建的正式数学推导。它只说明每个 effective topology 有一组 differential equations，`(u,i) Calculator` 按 `States` 选择并计算当前电压、电流 [pdf:E04][pdf:E08]。

从工程意义看，这相当于一个 switched state-space model：同一组储能状态在不同开关组合下遵循不同的导数关系，State Detector 决定当前使用哪一组关系；电流过零则是 topology 切换的事件面。这一句是帮助理解的抽象，不是论文给出的公式。由于原文没有 solver 类型、离散积分法和缩放规则，不能进一步推导 numerical stability，也不能从 60 ns step size 自动推出误差上界。

## § 7 — 实验设计与结论

- **问题 1：FPGA 固定步长模型能否重现参考模型的 transient 与 ripple？** 实验把 Q5 同步到 Q2、Q6 同步到 Q1，将 Q1+Q2 与 Q3+Q4 两个 half bridge 的 phase shift 从 0 跳到 25%，高压侧输入固定为 420 V；reference 是 variable-step 的 offline SimPowerSystems model [pdf:E09]。作者用 oscilloscope 记录 FPGA 输出，observation resolution 为 50 ns [pdf:E07]。图 5 对比 `v_C2`、`i_L1`、`i_L23`，两组曲线在展示区间内视觉上高度重合，作者结论是 voltage/current behavior “match well” [pdf:E10]。
- **问题 2：硬件路径是否足够快并能接真实 ECU？** 论文说明图 5 只显示 FPGA outputs，不含 converter 等 I/O latency；所用 dSpace FPGA board 的 analog-output latency 为 250 ns，digital-input latency 为 10 ns [pdf:E07]。作者还报告模型已与一辆 hybrid vehicle 的真实 DC/DC converter ECU 成功运行 [pdf:E07]。这证明至少存在一次实际 ECU 接入，不等于覆盖了所有闭环工况。
- **问题 3：是否验证了双向能流与通用拓扑迁移？** 没有。Summary 明确说 bipolar energy flow 尚待扩展 [pdf:E07]；第二种 topology 的移植、resource utilization、timing slack、长期实时 overrun、数值误差指标和硬件实测 converter waveforms 均未报告。因而本文可以支持“该 controlled transient 下 FPGA 与同源 offline model 波形相近”，不能支持“任意 DC/DC topology、任意工况下都有已量化精度保证”。

## § 8 — Take-aways

**5 句话。**

1. 高速 DC/DC converter 的 HiL 难点是内部开关事件和固定步长之间的时间错位，而不只是算术吞吐不足 [pdf:E02]。
2. 论文把 plant 切成四种 effective topologies，用 State Detector 选择当前 differential equations，再由 `(u,i) Calculator` 更新电压电流 [pdf:E04][pdf:E05][pdf:E08]。
3. Q5/Q6 电流过零判定使模型能够描述 discontinuous current mode 与 diode/MOSFET commutation，这是比“把方程搬到 FPGA”更关键的机制 [pdf:E06]。
4. 60 ns fixed-point step 和 50 ns observation resolution 展示了纳秒级执行能力，单个 0→25% phase-shift transient 与 offline SimPowerSystems 曲线视觉吻合 [pdf:E06][pdf:E07][pdf:E09][pdf:E10]。
5. 证据仍是短篇工程示例：没有数值误差、FPGA 资源、第二 topology 或 bipolar energy-flow 验证 [pdf:E07][pdf:E10]。

**3 句话。**

1. 作者用“先判有效 topology、再算该 topology”把高频 converter 的实时仿真变成适合 FPGA 的确定性数据通路 [pdf:E08]。
2. 实验说明这条通路能在一个受控相移阶跃下跟随 variable-step reference，并已连接真实 ECU [pdf:E07][pdf:E09][pdf:E10]。
3. 但论文没有证明最危险的换流边界、双向能流和参数扰动下仍保持同样精度。

**1 句话。**

本文最值得保留的不是某个 latency 数字，而是把内部开关事件显式提升为 FPGA 实时模型的状态选择问题 [pdf:E06][pdf:E08]。

## § 9 — 最脆弱的假设

最脆弱的假设是：在 60 ns fixed step 与 fixed-point arithmetic 下，State Detector 仍能可靠识别 Q5/Q6 电流过零，并在正确的时刻切换 effective topology [pdf:E06]。如果零点落在采样间隙、量化后电流在零附近抖动，或 dead time 与 I/O latency 改变了实际换流顺序，Detector 可能提前、延后或反复切换。这样一来，后级 `(u,i) Calculator` 即使算得再快，也是在执行错误的 differential equation，核心贡献会从“高精度实时”退化成“高速地产生错误轨迹”。

论文对此给出的证据，是图 5 中一个同步控制、420 V、0→25% phase-shift transient 的视觉重合，以及已接真实 ECU 的陈述 [pdf:E07][pdf:E09][pdf:E10]。它没有报告零交越 timing error、topology misclassification、quantization sensitivity、dead-time sweep 或 discontinuous-conduction 边界测试。因此，State Detector 的可靠性是基于证据的核心疑点，不应被 FPGA 的高 sampling rate 自动掩盖。

## § 10 — 最小复现实验

一周内最小复现应只验证“State Detector + effective-topology Calculator 能否在最敏感的换流点保持正确”，不必复制完整 dSpace 产品链。

1. 按图 2、图 3 重建 phase-shifted full bridge 与四种 effective topologies，保留 transformer leakage/resistance 和 semiconductor forward drop/resistance [pdf:E03][pdf:E05][pdf:E06]。
2. 建立两个同参数模型：variable-step、带 zero-crossing 的高精度 reference，以及 60 ns、fixed-point 的 state-machine model。复现论文的 Q5↔Q2、Q6↔Q1 同步控制、420 V 和 0→25% phase-shift step [pdf:E06][pdf:E09]。
3. 除 `v_C2`、`i_L1`、`i_L23` 外，额外记录 reference 的真实 zero-crossing 时刻、Detector 选择的 topology 和每次 commutation 的持续时间。逐步降低负载，使系统跨过 continuous/discontinuous conduction 边界。
4. 预先定义判据：若 100 个稳态 switching cycles 内没有 topology mismatch，零交越误差不超过一个 60 ns step，并且三条波形的 normalized RMSE 均不超过 2%，则暂时支持核心 claim；任一 missed commutation、持续错误 topology 或误差跨过阈值即反驳。这里的 100 cycles、1 step 与 2% 是复现实验的预注册标准，不是论文报告值。

这个实验比只重画图 5 更有信息量，因为它直接测量作者方法中最可能失败的内部变量，而不是仅看两个共享元件参数的模型能否给出相似外部波形。

## § 11 — 最强反例设计

最强反例是在 continuous/discontinuous conduction 边界制造“采样点两侧符号不同、量化后却同号或为零”的换流。具体做法是同时 sweep load、phase shift、dead time、transformer leakage inductance 与 current-sensor offset，让 Q5/Q6 电流过零恰好落在 60 ns step 的任意相位；再把论文说明但图 5 未包含的 250 ns analog-output 与 10 ns digital-input latency 放回闭环 [pdf:E06][pdf:E07]。

比较对象应有三组：高精度 variable-step circuit、FPGA state-machine output，以及真实低功率 prototype 的 gate/current measurement。若图 5 的吻合主要来自“受控同步开关 + 相同 component model + 未计 I/O latency”，那么在这组 adversarial commutation 下会出现可预测结果：Detector 错选 topology，`i_L1` 或 `i_L23` 产生相位/幅值偏差，ECU 又据此改变下一周期 gate timing，误差形成闭环放大。只要这种失败在论文宣称的工作范围内稳定复现，就足以推翻“高 sampling rate 自然带来 precise and stable closed-loop representation”的广义解释；它不会否定 FPGA 平台本身快，只会否定当前状态判定机制已经足够可靠。

## § 12 — Follow-up Research Idea

电力电子与 HiL 领域通常看重可量化精度、real-time deadline、闭环稳定性、跨工况验证和可落地硬件，而不只看某次波形截图。基于第 9 节，候选研究方向是 **event-certified FPGA HiL**：把“当前 topology 是否唯一可判”作为模型的显式输出，在电流过零、dead time 和量化误差造成歧义时，Calculator 不盲选一个分支，而是传播一个有界状态集合或触发可控的局部细化。

- **未满足需求：** 现有结构把 State Detector 的判定当作确定事实，但最危险的 commutation 恰恰发生在传感、量化和采样最不确定的零附近 [pdf:E06]。
- **可能的研究价值：** 若每次 topology transition 都能同时给出 deadline 与误差界，HiL 结果就从“波形看起来相近”升级为“控制器在已知不确定性内接受了什么 plant response”，更适合安全相关 ECU verification。
- **可借鉴工具：** hybrid-systems reachability、interval arithmetic、runtime monitor 和 formal invariant checking；它们可把 zero-crossing 附近的多分支可能性映射成并行 FPGA datapath。
- **首个证伪实验：** 使用第 11 节的 adversarial commutation sweep。若 bounded-state 版本仍频繁漏掉真实 prototype 的 topology，或为维持覆盖而使状态界持续发散、无法在 60 ns deadline 内更新，则该想法失败。
- **与本文的实质区别：** 本文追求更快地选择并执行一个人工识别的 effective topology [pdf:E05][pdf:E08]；候选方案把“事件时刻本身不确定”纳入问题定义，并要求模型在不能唯一判定时可观测地承认不确定性。

这是一项由本文证据边界驱动的候选想法。本文及本次阅读没有完成足够的相关工作检索，因此不声称该方向具有 novelty。
