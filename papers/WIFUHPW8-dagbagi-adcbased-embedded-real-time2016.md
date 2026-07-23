# ADC-Based Embedded Real-Time Simulator of a Power Converter Implemented in a Low-Cost FPGA: Application to a Fault-Tolerant Control of a Grid-Connected Voltage-Source Rectifier

**作者：** Mohamed Dagbagi；Asma Hemdani；Lahoucine Idkhajine；Mohamed Wissem Naouar；Eric Monmasson；Ilhem Slama-Belkhodja（PDF 物理页 1，题名与作者）[pdf:E01]

**出处：** *IEEE Transactions on Industrial Electronics*, Vol. 63, No. 2（PDF 物理页 1，期刊页眉）[pdf:E01]

**年份：** 2016（PDF 物理页 1，期刊页眉）[pdf:E01]

**DOI：** 10.1109/TIE.2015.2491883（PDF 物理页 1，首页 DOI）[pdf:E01]

**Zotero key：** WIFUHPW8

**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是一般意义上的 hardware-in-the-loop（HIL，硬件在环）仿真，而是一个更苛刻的问题：**能否把包含开关细节的 power-converter real-time simulator（电力变换器实时仿真器）作为 Intellectual Property（IP，知识产权核）直接放进低成本 FPGA 控制器，与控制算法同时运行，并在电流传感器故障后充当“虚拟传感器”维持闭环运行。** 作者把这一目标落实为三相并网两电平 voltage-source rectifier（VSR，电压源整流器）的 grid-current estimator（电网电流估计器）；估计值在传感器故障时替代实测电流，论文的 Abstract 明确把 HIL 与实物实验中的服务连续性作为验证目标（PDF 物理页 1，Abstract）[pdf:E01]。

重要性来自三个同时存在、彼此冲突的工程要求。第一，变换器的开关瞬态要求亚微秒级时间步；论文指出，为表示 switching effects（开关效应），仿真步长通常要低于 1 μs（PDF 物理页 2，Introduction）[pdf:E02]。第二，嵌入式仿真器与控制器共用同一片低成本 FPGA，不能像实验室 HIL 平台那样依赖昂贵器件和宽裕资源。第三，模型必须足够可信，才能把估计电流真正送入闭环，而不只是做监测。作者因此把问题概括为“模型复杂度—精度—FPGA 面积/成本”的折中，并把 embedded RT simulator 定义为与控制器同片、同时运行的系统模型 IP（PDF 物理页 2，embedded RT simulator 定义与论文贡献）[pdf:E03]。

这项工作的直接价值是以计算冗余代替部分硬件冗余：当电流传感器失效时，控制器仍有可用的三相电流反馈；同一类 IP 还可能支持 observation、diagnostic、health monitoring。需要注意的是，论文**没有研究故障检测本身**，只研究故障被判定之后如何切换到估计电流，因此其结论是 fault accommodation（故障容纳）可行性，而不是完整的 fault-detection-and-isolation（故障检测与隔离）方案（PDF 物理页 4，Section IV 开头）[pdf:E08]。

## § 2 — 前人工作与不足

以下相关工作判断是**论文对既有文献的归纳**，不是本卡在包外进行的独立文献核验。

最接近的第一条路线是 time-average model（时间平均模型）。论文引用 Lian 和 Lehn 的 VSC 实时平均模型 [11]；这类模型计算量较小，但作者认为即使配合复杂接口，也难以准确再现开关效应，因此无法直接支撑本文所需的 switching-level estimator（PDF 物理页 2，Introduction；PDF 物理页 11，References [11]）[pdf:E02] [pdf:E04]。不足并非“没有考虑开关”这么简单，而是开关细节一旦保留，时间步会压到 1 μs 以下，原本可接受的通用求解流程就可能无法在廉价器件上按时完成。

第二条路线是 device-behavioral model（器件行为模型）。论文概述的方案把由数据手册或实验得到的开关器件行为模型存进存储器，并高速寻址；References [13] 对应 Myaing 和 Dinavahi 的器件级详细 FPGA 实时仿真工作（PDF 物理页 2，Introduction；PDF 物理页 11，References [13]）[pdf:E02] [pdf:E04]。这条路线能增加器件细节，但代价转移到模型数据、存储访问和实现复杂度，不天然适合与控制器争夺同一低成本 FPGA 的资源。

第三条路线是 Pejovic 和 Maksimovic 提出的 associated discrete circuit（ADC，关联离散电路）方法 [14]。它给每个元件建立 companion circuit（伴随电路），通过参数选择使开关状态变化时的 conductance matrix（电导矩阵）保持不变；后续工作再加入阻尼以压制换相时的数值振荡 [15], [16]（PDF 物理页 2，ADC 相关工作；PDF 物理页 11，References [14]–[16]）[pdf:E02] [pdf:E04]。这已经提供了本文最关键的数值基础，本文的新增工作不能简单表述为“发明 ADC”，而是把 ADC 求解器压缩、定点化、流水化并嵌入低成本控制器，再把它用于 VSR 电流传感器故障后的闭环替代。

第四条路线是高性能 FPGA HIL 平台和 floating-point（浮点）求解器。论文提到 Ould Bachir 等人的高性能浮点 ADC 计算引擎，以及常用 Virtex、Stratix 等较昂贵器件；这类工作证明了高速详细仿真可以做，但 HIL 场景往往不把成本放在首位，不能直接回答“控制器与仿真器同片、资源受限”这一问题（PDF 物理页 2，平台与浮点实现讨论；PDF 物理页 11，References [18]）[pdf:E03] [pdf:E04]。论文还引用 Jimenez 等人的嵌入式 resonant-converter emulator [24]，说明“模型 IP 进入控制器”已有先例；本文作者所声称的区别是 ADC-based VSR estimator、三相 RL filter estimator、故障容错闭环和一套面向 FPGA embedded RT simulator 的设计流程（PDF 物理页 2，贡献段；PDF 物理页 11，References [24]）[pdf:E03] [pdf:E04]。

因此，这篇论文真正填补的是一个**工程组合缺口**：先前工作分别证明了详细模型、高性能 FPGA、嵌入式模型 IP 或故障容错控制的可行性，但尚未在作者设定的低成本、亚微秒、同片闭环约束下，把这些要素闭合成一个可综合、可计时、可 HIL、可上实物的系统。关于这一组合是否在 2016 年具有独立 novelty，本卡只转述作者定位，不作包外确认。

## § 3 — 重建作者的思考路径

可以从论文之前已知的约束，逆向得到如下思考链，而不先假设本文方案一定正确。

1. **先从故障容错需求出发。** 电流传感器一旦失效，控制器缺少闭环状态；增加物理冗余传感器会增加成本和故障点，因此可考虑用已知开关命令、母线电压和电网电压在线重建电流。
2. **再否定过粗模型。** 若估计器只保留平均动态，它可能在低频上正确，却无法解释换相附近的电压、电流关系；而传感器切换恰好要求模型在闭环中长期保持同步。论文把 switching system 的步长经验约束写成最小开关周期的约百分之一，并把电磁系统步长约束写成最小时间常数的 5%–10%（PDF 物理页 3，Section II-1）[pdf:E05]。
3. **寻找能固定计算图的详细模型。** 常规开关网络随拓扑改变，若每个时间步都重新组矩阵或求逆，亚微秒实时性很难保证；ADC 的吸引力在于把不同开关状态映射成同一电导，从而让主矩阵固定。
4. **把数值算法改写成硬件数据流。** FPGA 的优势不是“时钟天然更快”，而是并行、流水和 hardwired DSP；但浮点算子、乘法器数量、关键路径和资源上限会共同限制可实现的步长。论文明确把算法复杂度、数值格式、并行度、最大时钟和资源占用列为耦合约束（PDF 物理页 3，Section II-3/4）[pdf:E06]。
5. **用模块化与 factorization 控制面积。** 设计者先做系统规格，再选模型、分模块、离散化和验证；进入 FPGA 后再在 latency 与 area 之间选择并行或局部串行，最后依次做 HIL 和实物实验。Fig. 2 把这一流程画成 preliminary specification → algorithm development → FPGA implementation → experimentations，并引入 Algorithm Architecture Adequation（A3，算法-架构适配）来复用重算子（PDF 物理页 4，Fig. 2 与 Section III）[pdf:E07]。

这条思考路径改变了一个关键假设：仿真器不再是控制器外部的测试设备，而是控制器内部、必须服从同一芯片预算和闭环截止时间的计算部件。由此，模型选择标准也从“离线尽量精细”变成“在固定最坏执行时间内，保留对控制有价值的开关动态”。

## § 4 — 核心 Intuition

把每个开关的 ON 与 OFF 等效支路参数选到**离散电导相同**，网络电导矩阵就不再随开关状态改变；昂贵的矩阵求逆可离线完成，实时阶段只更新 dependent current sources（受控电流源）并执行固定的 matrix-vector product（矩阵-向量乘法）（PDF 物理页 7，Fig. 6 与 Eq. (2)–(4)；PDF 物理页 8，Eq. (6) 与时序）[pdf:E15] [pdf:E16] [pdf:E18]。这把“不断改变拓扑的电路求解”变成适合 FPGA 流水线的固定数据流，从而有机会在 500 ns 内生成 line voltages，再由 RL filter 递推得到三相 grid-current estimates。故障时，控制器只需把反馈源从传感器切到这些估计值。

## § 5 — 具体方法与完整 Pipeline

以论文的三相并网 VSR 为例，输入、处理和输出可还原为下面的端到端 pipeline。

1. **被控对象与信号入口。** 实验系统包括 230 V、50 Hz 三相电网，三相 RL filter 的参数为 \(R=0.8\ \Omega\)、\(L=20\ \text{mH}\)，20 kVA 两电平 VSR，直流侧电容为 1100 μF/800 V，另有 100 Ω/2.5 A 电阻负载和接触器（PDF 物理页 4，Section IV-1；PDF 物理页 5，Fig. 3 下文）[pdf:E08] [pdf:E09]。估计器接收 grid voltages、测得的 \(V_{dc}\)、控制器开关命令 \(S_a,S_b,S_c\) 以及上一时间步的开关内部量；输出是三相估计电流 \(\hat i_{ga},\hat i_{gb},\hat i_{gc}\)。
2. **采样与控制。** 目标器件是 Xilinx Zynq XC7Z020 ZedBoard。片上 XADC 配置成双 12-bit、1-MSPS simultaneous sampling，并通过外部 analog multiplexer 轮询所需信号；实测转换时间为 1.18 μs，考虑 multiplexer settling 后采样周期设为 2 μs（PDF 物理页 5，XADC 描述；PDF 物理页 6，Fig. 5 与实测转换时间）[pdf:E10] [pdf:E12]。控制器采用 direct sliding-mode power control（DSMPC，直接滑模功率控制）：外环 PI 调 \(V_{dc}\)，内环在 \(dq\) 坐标下用两个 hysteresis controllers 和 switching table 生成三相开关信号；控制采样周期为 50 μs，控制数据格式为 20Q12（PDF 物理页 5，Fig. 4 与控制器实现）[pdf:E10]。
3. **VSR 的 ADC 开关模型。** 每个 transistor/diode 在 ON 状态用小电感 \(L_{sw}\) 表示，在 OFF 状态用小电容 \(C_{sw}\) 与串联阻尼 \(R_{sw}\) 表示；离散后两种状态都化为“受控电流源并联电导”的统一支路（PDF 物理页 6，model selection；PDF 物理页 7，Fig. 6）[pdf:E14] [pdf:E15]。
4. **每个 500 ns 步的开关事件处理。** 先依据控制命令以及上一时间步的开关电压、电流判定 transistor/diode 状态；再更新 \(J_{Ti}[k]\)、\(J_{Di}[k]\)，组合右端向量 \(b[k]\)；由于 \(H^{-1}\) 已离线计算，实时只求 \(x[k]=H^{-1}b[k]\)，得到三相 line voltages、公共节点电压与 dc current；最后回算各开关电压和电流，供下一时间步使用（PDF 物理页 8，modular partitioning 与处理顺序）[pdf:E18]。
5. **三相 RL filter 递推。** VSR 模型输出的三相 line voltages 与 measured grid voltages 进入 backward-Euler 离散的 RL filter 模型，由 Eq. (1) 分别递推三相电流。该 filter estimator 与 VSR estimator 同步，步长同为 500 ns（PDF 物理页 6，Eq. (1) 与参数说明）[pdf:E13]。
6. **多速率调度。** 全系统同时存在三种速率：controller 50 μs、XADC 2 μs、VSR 与 RL filter estimators 500 ns。Fig. 11 给出了它们的嵌套时序，意味着快速模型在一次控制更新期间运行 100 次，而 XADC 在一次控制更新期间运行 25 次（PDF 物理页 9，Fig. 11 与 time/area evaluation）[pdf:E22]。
7. **数值表示。** 仿真器变量按 563 V 和 4 A 基值归一化，VSR 与 RL filter 使用 32Q28 fixed-point；四个整数位用于避免 overflow。控制器使用 20Q12。作者选择 backward Euler，理由是降低开关事件附近的数值振荡（PDF 物理页 6，RL filter 数据格式与 ADC model selection；PDF 物理页 8，digital realization）[pdf:E14] [pdf:E19]。
8. **FPGA 映射。** 每个 IP 都分成 datapath 与 finite-state-machine sequencer；架构插入寄存器形成深流水，并用 A3 factorization 复用乘法器，在面积和 latency 间折中。由于 500 ns 截止时间，VSR estimator 完全在 programmable logic 中实现，而不是放到 ARM 上（PDF 物理页 8，FPGA architecture design）[pdf:E21]。VSR 的一个 \(x[k]\) 元素数据路径被复制五份以并行计算整个状态向量；所选 factorization 用 44 个 32-bit multipliers 完成 88 次乘法（PDF 物理页 9，Fig. 10/11 与资源说明）[pdf:E22]。
9. **故障切换。** 正常时控制器使用 measured grid currents；模拟传感器故障后，一个简单开关把反馈改为 estimated currents。论文只实现这一切换，不实现自动 fault detection（PDF 物理页 5，Fig. 3；PDF 物理页 10，Step 3/4 与 Fig. 15）[pdf:E09] [pdf:E25]。

最终输出不是一份离线波形，而是每 500 ns 更新一次、可直接进入控制闭环的三相电流估计（PDF 物理页 6、8，RL filter 同步步长与 digital realization）[pdf:E13] [pdf:E18]。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有复杂的稳定性定理，核心数学是把连续电路离散成**固定矩阵、固定时序**的迭代计算。

首先，三相 RL filter 对每一相采用 backward Euler。论文 Eq. (1) 可写为

\[
 i_{g\phi}[k]=a_1\bigl(v_{g\phi}[k]-v_{L\phi}[k]\bigr)+a_2 i_{g\phi}[k-1],\qquad \phi\in\{a,b,c\},
\]

其中

\[
 a_1=\frac{T_s}{T_sR+L},\qquad a_2=\frac{L}{T_sR+L}.
\]

它的工程含义是：本步电流由本步 filter 两端电压差驱动，同时保留上一时刻电流；当 \(T_s\ll L/R\) 时，\(a_2\) 接近 1，符合电感电流连续性（PDF 物理页 6，Eq. (1)）[pdf:E13]。

其次，ADC 模型把开关两种状态离散成电导。ON 状态为

\[
 G_{T/D}^{\mathrm{ON}}=\frac{T_s}{L_{sw}},
\]

OFF 状态为

\[
 G_{T/D}^{\mathrm{OFF}}=\frac{C_{sw}}{R_{sw}C_{sw}+T_s}.
\]

这两式对应论文 Eq. (2) 与 Eq. (3)（PDF 物理页 7，Eq. (2)–(3)）[pdf:E16]。若要求两种状态的离散电导相等，则

\[
 \frac{T_s}{L_{sw}}=\frac{C_{sw}}{R_{sw}C_{sw}+T_s}
\]

经过交叉相乘可得

\[
 R_{sw}=\frac{L_{sw}}{T_s}-\frac{T_s}{C_{sw}},
\]

即论文 Eq. (6)（PDF 物理页 8，Eq. (6)）[pdf:E18]。这是整篇论文最关键的一步：开关状态改变只改变受控源，不改变 conductance matrix。

随后用 modified nodal analysis（改进节点分析）写成

\[
 Hx[k]=b[k],
\]

其中 \(x[k]\) 收集公共节点电压、三相 line voltages 和 dc current，\(b[k]\) 由各 transistor/diode 的受控电流源、三相 grid currents 与 \(V_{dc}\) 组成（PDF 物理页 7，Eq. (4) 及变量说明）[pdf:E16]。因此每步解为

\[
 x[k]=H^{-1}b[k].
\]

论文 Eq. (5) 给出了该三相两电平 VSR 的完整 \(H^{-1}\) 与 \(b[k]\) 结构（PDF 物理页 7，Eq. (5)）[pdf:E17]。因为 \(H\) 不随开关状态变化，\(H^{-1}\) 可在离线阶段求好并固化为系数；FPGA 实时阶段只做受控源更新、加法和乘法。这是算法从电路求解器变成确定性硬件流水线的数学原因。

作者在离线验证中把 \(R_{sw},L_{sw},C_{sw}\) 手工调为 7.5 Ω、160 μH、1.6 nF，并采用 \(T_s=500\) ns（PDF 物理页 8，algorithm validation）[pdf:E19]。把这些数代入 Eq. (6)，\(L_{sw}/T_s=320\ \Omega\)，\(T_s/C_{sw}=312.5\ \Omega\)，差值正好为 7.5 Ω，说明这组参数严格满足“ON/OFF 等电导”条件。这个代数一致性只证明矩阵可固定，**不证明该 RLC companion model 对真实器件在所有工况下都准确**；物理精度仍取决于参数、dead time、器件压降和被控对象参数是否匹配。

## § 7 — 实验设计与结论

论文的验证链条可以按“问题 → 实验 → 答案”拆成五层。

1. **开关离散模型能否产生合理的换相波形？** → 作者先在 MATLAB/Simulink 中做离散时间、32Q28 fixed-point offline simulation，观察 IGBT 与 diode 的 ON/OFF、OFF/ON 电压电流波形，并手工选择 \(R_{sw}=7.5\ \Omega\)、\(L_{sw}=160\ \mu\text{H}\)、\(C_{sw}=1.6\ \text{nF}\) → Fig. 8 显示换相尖峰和阻尼后的瞬态，证明算法至少能生成预期形态，但没有与器件级测量误差做定量对比（PDF 物理页 8，digital realization、algorithm validation 与 Fig. 8）[pdf:E19] [pdf:E20]。
2. **估计电流进入闭环后能否承受负载接入？** → 在完整离线闭环模型中连接负载，把 estimated currents 注入 controller → Fig. 9 中 measured/emulated 与 estimated current 基本重合，\(V_{dc}\) 保持在 200 V reference，作者还报告 grid current 与 voltage 同相 → nominal simulation 支持闭环可用性（PDF 物理页 8，Fig. 9 与正文）[pdf:E20]。
3. **FPGA 是否真正满足实时截止时间与面积预算？** → 在 XC7Z020 上综合并测量 latency、clock 与资源 → VSR estimator latency 为 28 个 100-MHz 周期，即 280 ns；三相 RL filter 为 15 周期，即 150 ns，均低于 500 ns 步长。整套系统报告总资源占 19.68%，但 DSP48E1 占用达到 84.54%；VSR estimator 单独使用 180 个 DSP48E1、3982 LUT 和 6410 flip-flops（PDF 物理页 6，Table I；PDF 物理页 9，Fig. 11 与 time/area evaluation）[pdf:E11] [pdf:E22]。答案是“时序闭合，但 DSP 余量很小”。
4. **在真实时间闭环中，估计器是否跟得上被仿真对象？** → 作者把同一 IP library 组成 FPGA-based power-system emulator，进行 closed-loop HIL，在负载接入与稳态比较 emulated 与 estimated currents → Fig. 12 中两者视觉上相近，作者据此判定 HIL 通过（PDF 物理页 9，Fig. 12 与 HIL tests）[pdf:E23]。
5. **在实物 VSR 上发生传感器故障时能否维持服务？** → 实验先让变换器处于 diode VSR 模式，再闭环调到 \(V_{dc}=200\) V，连接负载，然后用简单开关把 measured currents 换成 estimated currents，并在故障期间反复接入/断开负载 → Fig. 14 显示 diode 模式下 measured/estimated current 匹配，Fig. 15 显示切换后 \(V_{dc}\) 只有轻微扰动且继续受控，Fig. 16 显示负载断开时三相 measured/estimated currents 相近，Fig. 17 给出实测开关换相波形（PDF 物理页 9，实验 Step 1/2；PDF 物理页 10，Fig. 13–17 与 Step 3–5）[pdf:E24] [pdf:E25] [pdf:E26]。答案是“在这套 nominal lab setup 中，故障后的闭环服务连续性得到演示”。

不能外推的范围同样重要。论文只验证了一套 20 kVA VSR、给定 RL 参数、手工调好的 ADC 参数和有限负载步骤；主要证据是波形视觉重合和 \(V_{dc}\) 仍受控，未报告统一的 RMSE、峰值误差、相位误差、长期漂移、参数扫描或统计置信区间。故障检测不在范围内，dead time 和在线参数识别被留作后续工作（PDF 物理页 4，scope；PDF 物理页 11，Conclusion and perspectives）[pdf:E08] [pdf:E27]。因此，实验充分支持“可实现、可实时、在给定平台上可维持服务”，但不足以支持“对广泛器件、参数漂移和故障模式均有可证明精度”。

## § 8 — Take-aways

**5 句话：**

1. 论文把 real-time simulator 从外部 HIL 设备变成与控制器同片运行的 virtual sensor，并用它处理三相电流传感器故障（PDF 物理页 2，贡献段）[pdf:E03]。
2. 核心算法不是更快地在线求逆，而是通过 ADC 参数约束让矩阵永远不变，从根本上删除在线求逆（PDF 物理页 8，Eq. (6) 与处理顺序）[pdf:E18]。
3. 固定点、深流水和 A3 factorization 使 VSR 与 RL filter 的计算分别在 280 ns 和 150 ns 内完成，满足 500 ns 步长（PDF 物理页 6，Table I；PDF 物理页 9，timing）[pdf:E11] [pdf:E22]。
4. HIL 与实物波形表明，在论文的 nominal setup 中，用 estimated currents 替代 sensors 后 \(V_{dc}\) 仍可受控（PDF 物理页 9–10，Fig. 12、Fig. 15–16）[pdf:E23] [pdf:E25] [pdf:E26]。
5. 证据的主要边界是模型参数手工调节、缺少定量误差与鲁棒性扫描，而且 dead time 和 online identification 尚未纳入（PDF 物理页 11，perspectives）[pdf:E27]。

**3 句话：**

1. 算法层面的贡献是把 switching topology 变化转化为固定系数的数据流（PDF 物理页 8，Eq. (6) 与处理顺序）[pdf:E18]。
2. 系统层面的贡献是从公式、定点实现、时序资源到 HIL 和实物故障切换形成完整闭环（PDF 物理页 6、9–10，Table I 与 Fig. 12–17）[pdf:E11] [pdf:E23] [pdf:E26]。
3. 论文证明的是 nominal feasibility，而不是 model-mismatch 下的可靠性保证（PDF 物理页 8–11，固定矩阵、时序、实验与未来工作）[pdf:E18] [pdf:E22] [pdf:E26] [pdf:E27]。

**1 句话：**

这是一篇把 ADC switching solver 压进低成本 FPGA 并用于 fault-tolerant current feedback 的端到端可行性论文，最强处是实现闭环，最弱处是鲁棒性和定量精度证据不足（PDF 物理页 8–11，核心机制、实验与局限）[pdf:E18] [pdf:E26] [pdf:E27]。

## § 9 — 最脆弱的假设

最脆弱的假设是：**传感器失效后，依据 nominal 参数、开关命令和有限电压测量运行的开环模型，仍会与真实 VSR 保持足够同步，因而其电流估计可以长期安全地替代反馈。** 这不是“模型有一点误差也没关系”的普通假设；一旦失效，控制器会把模型误差当作真实电流误差进行调节，闭环可能围绕一个虚构状态运行，核心的 service-continuity claim 就会直接失效。

这个假设在现实中可能被多种 command-to-plant mismatch 打破：gate-driver dead time、开关延迟和器件压降使实际拓扑切换时刻不同于逻辑命令；电感受温度或饱和影响，\(R,L\) 偏离 nominal；电网不平衡、传感器/ADC 偏置和 multiplexer 延迟也会造成相位偏差。论文的 ADC 参数是手工调节的，且作者把 dead time 与 online identification 明确列为未来工作（PDF 物理页 8，手工参数；PDF 物理页 11，perspectives）[pdf:E19] [pdf:E27]。这正说明作者也意识到同步依赖模型匹配。

论文为该假设提供的证据是 nominal HIL 与实物测试：estimated 与 emulated/measured currents 在负载步骤和传感器切换后视觉上相近，\(V_{dc}\) 继续受控（PDF 物理页 9，Fig. 12；PDF 物理页 10，Fig. 15–16）[pdf:E23] [pdf:E25] [pdf:E26]。缺少的证据是参数与 dead-time 扫描、误差上界、长时运行、噪声与偏置注入、器件温升、grid imbalance，以及“估计器何时不再可信”的在线判据。**基于证据的推断：** 当前结果能证明一个工作点附近的容错演示，不能证明失去传感器校正后模型误差不会积累。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 20 kVA 硬件，而是论文最核心的联合 claim：**固定矩阵 ADC estimator 在 nominal 条件下既能达到足够的电流精度，又能满足 500 ns deadline，并在传感器切换后维持 dc-link control。**（PDF 物理页 4、9–10，系统规格、时序与故障实验）[pdf:E08] [pdf:E22] [pdf:E25]

建议做一个可证伪的 software-first、synthesis-second 实验：

1. **数据与工况。** 使用论文报告的 230 V/50 Hz grid、\(R=0.8\ \Omega\)、\(L=20\ \text{mH}\)、1100 μF dc-link、100 Ω load、\(T_s=500\) ns，以及 \(R_{sw}=7.5\ \Omega\)、\(L_{sw}=160\ \mu\text{H}\)、\(C_{sw}=1.6\ \text{nF}\)（PDF 物理页 4、6、8，system specification、Eq. (1)、algorithm validation）[pdf:E08] [pdf:E13] [pdf:E19]。构造一次 load connection，并在稳态后把三相 current measurements 全部置为不可用。
2. **实现。** 用 Python、MATLAB/Simulink 或 C 实现 Eq. (1)–(6)：离线求 \(H^{-1}\)，在线按论文顺序更新 switch states、dependent sources、\(b[k]\)、\(x[k]\) 和 RL currents；同时做 bit-true 32Q28 版本。以更小步长的独立 switched ODE/SPICE model 作为 truth model，避免用同一 ADC 方程自证（PDF 物理页 7–8，Eq. (2)–(6) 与处理顺序）[pdf:E16] [pdf:E17] [pdf:E18]。
3. **测量。** 记录三相 current NRMSE、最大绝对误差、相位误差，fault switch 前后的 \(V_{dc}\) overshoot 与 settling time，以及 fixed-point 相对 floating-point 的误差。把 matrix-vector kernel 综合到 XC7Z020 或等价资源模型，报告 worst-case latency 和 DSP/LUT 数；论文基线是 VSR 280 ns、RL filter 150 ns（PDF 物理页 9，time/area evaluation）[pdf:E22]。
4. **预注册判据。** 作为复现实验自定而非论文报告的标准，可把“支持”定义为：nominal 工况下三相 current NRMSE 不超过 5%，fault switch 后 \(V_{dc}\) 峰值偏差不超过 reference 的 5%，且最坏计算时间低于 500 ns；任一项在 nominal 工况下失败即反驳核心 claim。随后再把 \(R,L\) 各扫 ±20%、dead time 扫 0–3 μs，画出 claim 开始失效的边界，而不是只给一条成功波形。

这个复现刻意不重做 fault detector，因为原论文也未覆盖它；它直接检验“模型精度—fixed-point—deadline—闭环切换”四者能否同时成立。

## § 11 — 最强反例设计

最有力的反例是制造**逻辑开关命令与真实功率级拓扑之间的系统性偏差**，并加入一个更简单的 baseline，检验论文成功是否真的来自 switching-level ADC fidelity。

实验可在可编程 HIL 或实物台架上进行：保持 estimator 使用论文 nominal \(R,L,R_{sw},L_{sw},C_{sw}\)，但在真实 plant 端逐步增加 0–3 μs dead time、器件导通压降，并让 line inductance 在负载升高时下降 10%–30%；在电流峰值附近同时触发 sensor fault 与 load connection。比较三组闭环：A 组使用 measured currents，B 组使用论文 ADC estimator，C 组使用只匹配基波幅值和相位的 time-average estimator。评价三相 peak/phase error、\(V_{dc}\) overshoot、THD、过流或保护触发，并记录失稳边界。

这个设计同时攻击两个可能的替代解释。第一，若 B 组在很小的 dead-time 或参数偏差下迅速失去同步，则 nominal 实验不能支持实际 service continuity；这直接命中论文尚未处理 dead time 与 online identification 的缺口（PDF 物理页 8，手工调参；PDF 物理页 11，future work）[pdf:E19] [pdf:E27]。第二，若 C 组与 B 组在故障容错指标上无显著差别，则现有实验只能说明 controller 对“近似正确的电流”有容忍度，不能证明详细 ADC switching model 是闭环成功的因果关键；这会挑战作者关于 ADC 精度提升 controller reliability 的论述（PDF 物理页 6，model selection）[pdf:E14]。反之，只有当 B 组在可观的 mismatch 下仍显著优于 C 组，且保持 \(V_{dc}\) 与电流安全，论文的核心机制才得到更强支持。

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty：** 把“给出一个 nominal point estimate”改成“给出带可信边界、能自我校准、会在不可信时主动降级的 embedded digital twin（嵌入式数字孪生）”。目标不再只是估计 \(i_g\)，而是实时输出 \([\underline i_g,\overline i_g]\) 或 confidence score，并把“是否允许用模型替代传感器”纳入 fault-tolerant control 决策。

**(a) 未满足的需求。** 原系统在 sensor fault 后失去电流测量校正，而 ADC 参数、line \(R/L\)、dead time 和器件特性会漂移；论文自己把 dead time 和 online identification 留作未来工作（PDF 物理页 11，perspectives）[pdf:E27]。真正的工程需求不是在一个 nominal 实验中看起来重合，而是知道估计误差是否仍在安全域内。

**(b) 可能产生的研究价值。** 在电力电子与控制领域，高影响结果通常需要同时满足物理机制明确、实时可实现、硬件闭环验证和可推广的鲁棒性。若系统能给出经过校准的误差包络，并在包络过宽时切换到限功率、开环安全或冗余控制模式，它把“模型可用性演示”提升为“可验证的 service-continuity envelope”。

**(c) 可借鉴的相邻方法。** 快速 500 ns plant update 继续留在 FPGA fabric；较慢的参数更新放到 Zynq 的 ARM processor。可结合 set-membership identification（集合成员辨识）、interval observer（区间观测器）、moving-horizon estimation（移动窗估计）或 robust MPC（鲁棒模型预测控制），用健康传感器阶段持续辨识 \(R,L\)、dead time 与电压偏置，再把系数和不确定度下发给固定矩阵内核。该硬软分层也回应了现有设计的资源现实：论文整套系统已占 84.54% DSP48E1，不能简单复制更多并行模型（PDF 物理页 5，Zynq/ARM 平台；PDF 物理页 6，Table I）[pdf:E09] [pdf:E11]。

**(d) 第一个能够证伪它的实验。** 在温升、\(R/L\) 扫描、0–3 μs dead time、grid imbalance、ADC bias 和 load step 的组合矩阵中随机触发 sensor fault；比较原 deterministic ADC estimator、仅在线参数点估计版本、以及带 interval/confidence 的版本。候选方法必须同时满足：真实电流落入预测区间的覆盖率达到预注册目标、区间不过宽、故障后 \(V_{dc}\) 和电流保持安全，而且 FPGA fast path 仍在 500 ns 内；任何一项失败都否证该方向的实际价值（PDF 物理页 9，原系统 500 ns 时序基线）[pdf:E22]。

**(e) 与本文工作的实质区别。** 本文优化的是一个 nominal model 的速度与面积，并把 point estimate 直接送入 controller；候选工作改变的是问题定义——系统不仅估计状态，还估计自己的不确定性，并据此决定何时信任模型、何时降级。它不是给现有架构多加一个模块，而是把 fault accommodation 从“盲目切换到模型”改成“有证据地授权模型接管”。
