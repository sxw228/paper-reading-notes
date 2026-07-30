# A Modified Algorithm for the L/C-based Switch Model of Power Converters in Real-Time Simulation Based on FPGA

- 作者：Can Wang，Qinsheng Wang，Haowen Weng，Xuewei Pan
- 出处：IEEE Transactions on Industry Applications，Vol. 60，No. 5，pp. 7030–7037
- 年份：2024
- DOI：10.1109/TIA.2024.3407031
- Zotero key：85WBSMAJ
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个很具体的实时电磁暂态仿真误差：为了避免开关动作时重建节点导纳矩阵，系统级 power converter 模型常把导通开关等效为电感、关断开关等效为电容，再统一写成固定导纳的 associated discrete circuit（ADC）。这种 L/C-based switch model 很适合 FPGA，因为每一步可以沿用预先形成的矩阵；但它会产生并非来自真实器件的 virtual power loss，而且原模型的损耗会随载波频率上升。作者的目标不是再调一组 \(L/C\) 参数，而是解释这个非物理能量误差由何而来，并用尽量不增加 FPGA 延迟和资源的修正消除它。论文摘要把核心原因归结为开关动作瞬间的 initial error，并报告修正只增加一个 clock cycle。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，是因为 system-level HIL 关心的是理想开关层面的系统动态、控制器行为和设备间耦合，而不是器件级的真实开关损耗。若数值开关自身吞掉几十个百分点的功率，控制器看到的直流侧功率、交流侧波形和稳定裕度都会被模型误差污染。固定导纳 ADC 的价值在于不随开关状态更新导纳矩阵；代价则是开关频率升高时 virtual power loss 可能变得不可接受。[pdf:E02]（PDF 物理页 1，Introduction，system-level ADC 与 virtual power loss 段）因此，本文实际解决的是“如何保留固定矩阵这一实时优势，同时让离散开关更接近理想开关”的工程矛盾。

需要先澄清术语：本文的 virtual power loss 是数值开关模型引入的非物理能量误差，不是 IGBT/MOSFET 的 conduction loss 或 switching loss。这一区分决定了评价标准：目标不是拟合真实器件损耗，而是让 system-level ideal-switch model 不凭空改变系统能量。

## § 2 — 前人工作与不足

论文给出的 prior-work 图景可以分成五类。第一类是继续调 \(L_{\text{switch}}\) 与 \(C_{\text{switch}}\)：已有工作能降低损耗，但只能针对特定电路条件压小初始误差，不能消除其产生机制，频率升高后仍会恶化。第二类是换用更复杂的 ADC 数值方法；它们能改善开关误差，却增加建模和求解复杂度。第三类是在 L/C 开关中串联负电阻补偿损耗，但这样会让导通开关电压不再为零，破坏 ideal switch 语义。第四类是加入补偿电压源/电流源，其数值依赖外部电路参数。第五类是 reinitialization；它可以抑制开关瞬态振荡，但设计复杂、效率低，并增加 FPGA 的 logic 与 storage burden。[pdf:E02]（PDF 物理页 1，Introduction 后半；相关文献 [18]–[23]）[pdf:E03]（PDF 物理页 2，Introduction 续段与 Section II）

论文还特别指出，conference 版本 [26] 已经给出一种简单 modified algorithm，但附加算法对 FPGA 资源的影响尚未被充分评估。本文相对该版本的实质推进，是把“初值为何错”的数值解释、可复用的 IEM 表达式、state-machine FPGA 架构，以及资源与多拓扑实验放到同一个闭环中。[pdf:E03]（PDF 物理页 2，Introduction 续段）

这里的判断边界是：上述优缺点是本文作者对相关工作的总结，本卡没有联网独立复核这些 prior methods。可以确认的是，作者没有把问题简化成“以前没有人处理 virtual power loss”，而是把缺口收窄为：已有补偿要么破坏 ideal-switch 特性，要么依赖外部参数、增加复杂度，要么缺少 FPGA 成本验证。

## § 3 — 重建作者的思考路径

一种不借用论文最终贡献、但能从既有矛盾走到该方法的思考路径如下。

1. 先保留固定导纳 ADC，因为对严格实时步长而言，避免开关后重构节点矩阵比追求离线仿真的事件插值更重要。基线算法把每个元件写成 \(Y_b\) 与 history current source \(I_h\) 的并联，并用预计算矩阵把节点求解化为支路电压、电流的 matrix-vector multiplication。[pdf:E03]（PDF 物理页 2，Fig. 1、Table I、Eqs. (1)–(8)）
2. 然后不再从“储能元件必然有损耗”出发，而是逐拍检查开关刚换状态时 \(I_h\) 的数值。对上桥臂从 OFF 切到 ON 的例子，换态前 \(I_h=-Y_sU_{dc}\)，按新状态系数更新后首拍得到 \(I_h=0\)，而新稳态本应是 \(i_L\)。两者差值就是 initial error。[pdf:E04]（PDF 物理页 3，Fig. 3、Eqs. (9)–(11)）
3. initial error 迫使离散模型经历一个并不存在于 ideal switch 中的收敛振荡；振荡的幅值受电路工况与数值方法共同影响，所以仅调 \(L/C\) 参数只能在局部工况有效。由此可推断，应该修正的是换态首拍的 state initialization，而不是继续把能量误差解释成某个固定等效损耗。
4. 新状态的稳态电流或电压在当前拍尚未求出，但相邻 filter inductor current 与 filter capacitor voltage 在足够小的 \(\Delta t\) 内变化较慢。于是可以用上一拍相邻无源支路量近似新稳态值，直接重置 \(I_h\)，跳过错误初值后的收敛过程。[pdf:E04]（PDF 物理页 3，Section III-B 与 Fig. 4）其通用表达与成立条件由 Eqs. (12)–(14) 给出。[pdf:E05]（PDF 物理页 4，Eqs. (12)–(14)）
5. 最后才考虑 FPGA：如果这次条件重置单独配一套乘加器，算法收益会被资源和 critical path 抵消；因此应把它嵌入既有 state machine，在主要 matrix-vector multiplication 前后复用空闲 floating-point IP。[pdf:E06]（PDF 物理页 4，Section III-C，Figs. 5–6）

这条路径的关键转折不是“发明一个补偿量”，而是把问题从持续性的能量补偿改写为离散状态在 event boundary 上初始化错误。

## § 4 — 核心 Intuition

L/C-based switch 的 virtual power loss 主要不是因为等效电感或电容本身“耗能”，而是因为开关换态后的第一个 history-current sample 与新状态稳态值不一致，随后产生了不该存在的数值收敛过程。[pdf:E04]（PDF 物理页 3，Eqs. (9)–(11) 与 initial error 解释）IEM 在开关动作时不沿用这一个错误 sample，而是用相邻无源支路上一拍的电流或电压直接把 \(I_h\) 放到新稳态附近。[pdf:E05]（PDF 物理页 4，Eqs. (12)–(14)）只要相邻无源量在一个仿真步长内近似不变，模型就能跳过振荡收敛，同时继续使用同一固定导纳矩阵。FPGA 上再通过复用既有乘加资源，把这一条件重置压缩为一个额外 cycle。

## § 5 — 具体方法与完整 Pipeline

以论文的 two-level VSC bridge arm 为例，完整 pipeline 如下。

1. **离线形成固定导纳模型。** 每个电感、电容和 L/C switch 都写成支路导纳 \(Y_b\) 与 history current source \(I_h\) 的并联 ADC。开关 ON 时使用 \(Y_b=\Delta t/L_{\text{switch}}\)、\(\alpha=0,\beta=1\)；OFF 时使用 \(Y_b=C_{\text{switch}}/\Delta t\)、\(\alpha=-1,\beta=0\)。节点导纳矩阵及由它形成的 \(B,C\) 矩阵可以预先计算。[pdf:E03]（PDF 物理页 2，Table I、Eqs. (1)–(8)）
2. **每个实时步接收事件和源。** PWM gate signals 与 independent sources 在步首进入六状态 state machine。固定系数预存 RAM；需要逐步更新的 component coefficients、输出 voltage/current 和过程量放在 FPGA registers。论文使用 single-precision floating-point arithmetic IP。[pdf:E06]（PDF 物理页 4，Section III-C）
3. **无开关动作时走基线算法。** 先构造 \(I_{\text{temp}}=I_h+I_s\)，再用预计算的 \(B\) 与 \(C\) 分别得到 \(V_b\) 和 \(I_b\)，二者没有数据依赖，可以并行；最后更新下一拍 \(I_h\)。[pdf:E03]（PDF 物理页 2，Eqs. (3)、(6)–(8)）
4. **开关动作时插入 IEM。** 上桥臂 OFF 时令 \(I_h(t)=-Y_sU_{dc}(t-\Delta t)\)，ON 时令 \(I_h(t)=i_L(t-\Delta t)\)；下桥臂 ON 时电流参考方向相反，因此使用 \(-i_L(t-\Delta t)\)。推广形式是：OFF 取等效 parallel branch 的上一拍 voltage 乘 \(h_{\text{off}}\)，ON 取等效 series branch 的上一拍 current 乘 \(h_{\text{on}}\)。[pdf:E05]（PDF 物理页 4，Eqs. (12)–(13)）
5. **保持物理近似成立。** 作者要求 \(L_f\gg L_{\text{switch}}\) 且 \(C_f\gg C_{\text{switch}}\)，使相邻 filter inductor/current 或 filter capacitor/voltage 在一个 \(\Delta t\) 内可近似为 independent source。[pdf:E05]（PDF 物理页 4，Eq. (14)）
6. **映射到 FPGA 并复用资源。** State 3 承担最重的 matrix-vector multiplication，采用并行 pipeline；其他乘加被拆开放到 State 3 前后，从而复用该状态分配的 arithmetic IP。Table II 给出 State 3 为 \(b+1\) cycles，其余五个状态各 1 cycle；IEM 只新增 1 cycle。[pdf:E07]（PDF 物理页 5，Tables II–III 与相邻正文）
7. **输出与观测。** 论文平台使用 Xilinx Kintex-7 XC7K325T，仿真输出经 DA conversion module 送入 oscilloscope。论文没有报告实际达到的 FPGA clock frequency、完整 timing closure 结果、host-to-FPGA 通信延迟或 PWM 输入同步细节，因此不能从这篇论文推出任意网络规模下的可达实时步长。[pdf:E08]（PDF 物理页 5，Section IV-A 与 Fig. 8）

## § 6 — 核心数学推导（无形式化数学则跳过）

ADC 的基本状态式是

\[
I_h(t)=\alpha Y_bV_b(t-\Delta t)+\beta I_b(t-\Delta t).
\]

\(Y_b\) 是并联支路导纳，\(I_h\) 把上一拍的储能状态注入当前网络；\(\alpha,\beta\) 决定电感、电容或开关当前采用哪一种离散更新。节点分析经预计算后可写成

\[
V_b(t)=B I_{\text{temp}}(t),\qquad
I_b(t)=C I_{\text{temp}}(t),
\]
\[
B=-A^\mathsf{T}Y_n^{-1}A,\qquad
C=Y_bB+E,
\]
\[
I_h(t+\Delta t)=(\alpha+\beta)I_b(t)-\alpha I_{\text{temp}}(t).
\]

工程上最重要的是：网络拓扑的主要线性求解被吸收到固定 \(B,C\) 中，实时每拍只做 matrix-vector multiplication 和 history update；\(V_b\) 与 \(I_b\) 可以并行。[pdf:E03]（PDF 物理页 2，Eqs. (1)–(8)）

初始误差来自换态前后状态式不连续。以上桥臂 OFF→ON 为例，换态前

\[
I_h(t-\Delta t)=-Y_sU_{dc}(t-\Delta t),
\]

而按 ON 状态系数更新后，换态首拍得到 \(I_h(t)=0\)。理想导通后的稳态却要求

\[
I_h(t)=i_L(t).
\]

因此首拍误差就是 \(i_L(t)\)；ON→OFF 时对应误差为 \(-Y_sU_{dc}(t)\)。这个误差随后通过 history update 传播并收敛，形成数值振荡和 virtual power loss。由于误差幅值随外部工况变化，调 \(L/C\) 只能改变收敛过程，不能从结构上保证首拍正确。[pdf:E04]（PDF 物理页 3，Eqs. (9)–(11) 与相邻解释）

IEM 直接把换态首拍投影到估计稳态：

\[
I_h(t)=
\begin{cases}
h_{\text{off}}V_{b,\text{modified}}(t-\Delta t), & \text{OFF},\\
h_{\text{on}}I_{b,\text{modified}}(t-\Delta t), & \text{ON}.
\end{cases}
\]

\(h_{\text{on}}\) 由 series branch current 的参考方向决定，\(h_{\text{off}}\) 由 parallel branch voltage 参考方向与 switching branch admittance 决定。这里不是严格求解 \(t\) 时刻的新稳态，而是用 \(t-\Delta t\) 的相邻无源量做代理；其成立条件正是 \(L_f\gg L_{\text{switch}}\)、\(C_f\gg C_{\text{switch}}\)。[pdf:E05]（PDF 物理页 4，Eqs. (12)–(14)）

基于证据的推断：从数值分析角度，IEM 可看成一次 event-triggered state projection——它不改变固定导纳矩阵，只修正离散内部状态的初值。论文没有把它写成约束投影，也没有给出误差上界或 stability proof；因此“消除”是实验范围内的结果，不是对所有拓扑和步长的形式化定理。

## § 7 — 实验设计与结论

- **问题：IEM 的 FPGA 成本是否足够小？ → 实验：** 在 two-level converter 的 state-machine 实现中比较有无 IEM 的资源。**答案：** registers 从 15,753/407,600 增至 15,782/407,600，即增加 29；look-up tables 从 23,731/203,800 增至 24,457/203,800，即增加 726；RAM blocks 保持 31/445，DSP48 保持 128/840。作者据此把开销概括为一个额外 clock cycle 和少量 LUT，且没有额外 RAM/DSP。[pdf:E07]（PDF 物理页 5，Tables II–III）
- **问题：换态波形是否更接近 ideal switch？ → 实验：** 在 Kintex-7 XC7K325T 平台上仿真 two-level VSC、three-level VSC 和 Boost converter，并以 MATLAB/Simulink SimPowerSystems 的 ideal-switch offline model 为参考。主 converter 参数为 \(V_{dc}=700\ \text{V}\)、AC bus RMS \(220\ \text{V}\)、\(50\ \text{Hz}\)、\(L_f=1.5\ \text{mH}\)、\(C_f=60\ \mu\text{F}\)、\(C_{dc}=10000\ \mu\text{F}\)、PWM carrier \(10\ \text{kHz}\)、time-step \(1\ \mu\text{s}\)。[pdf:E07]（PDF 物理页 5，Fig. 7 与 Table IV）**答案：** IEM 的 switch voltage/current 视觉上接近 offline reference；无 IEM 时即便调整 switch parameters 仍出现明显 oscillation。two-level 与 three-level 对比见 Figs. 9–10，Boost 对比见 Fig. 11。[pdf:E09]（PDF 物理页 6，Figs. 9–10 与相邻正文）[pdf:E10]（PDF 物理页 7，Fig. 11）
- **问题：载波频率升高后 virtual power loss 是否仍被压住？ → 实验：** 对 DC chopper、two-level converter、three-level converter 扫描 2–20 kHz carrier frequency，比较 IEM 与 non-IEM。**答案：** non-IEM 三条曲线都随频率显著上升；IEM 三条曲线都留在接近零的插图尺度内。[pdf:E10]（PDF 物理页 7，Fig. 12）论文没有给这些曲线点的数值表，因此不应从图中估读成精确百分比。
- **问题：IEM 是否对 simulation time-step 敏感？ → 实验：** 比较 500 ns、1 µs、1.5 µs 三个步长。**答案：** without IEM 的 virtual power loss 分别为 19.84%、33.21%、42.84%；with IEM 分别为 0.10%、0.19%、0.27%。[pdf:E11]（PDF 物理页 7，Table V）在这三个已测点上，IEM 的损耗虽随步长增加而上升，但仍低于 0.3%，所以更准确的表述是“在已测范围内低敏感”，不是“与步长无关”。

实验结论的外推边界很重要。波形一致性主要由 oscilloscope/plot 视觉对比支持，没有 RMSE、THD、peak error 或 phase-error 统计；virtual power loss ratio 也没有在正文中给出明确计算式。论文没有报告 post-route maximum frequency、worst negative slack、端到端 latency、闭环控制器 HIL 或真实功率硬件对照。因此，它强力支持“该 FPGA 原型和这些工况下 IEM 显著降低模型虚损耗”，但不足以证明所有 converter topology、所有 network size 和任意 simultaneous switching event 下都成立。作者在结论中给出的 universality 与 frequency/time-step insensitivity 应按上述实验边界理解。[pdf:E12]（PDF 物理页 7，Conclusion）

## § 8 — Take-aways

**5 句话：**

1. 固定导纳 L/C switch 的主要误差源被定位为换态首拍的 history-current initial error，而不是一个必须长期补偿的固定损耗。
2. IEM 用相邻无源支路上一拍的电流或电压近似新状态稳态值，直接跳过错误初值后的数值收敛。[pdf:E04]（PDF 物理页 3，Section III-B）
3. 这一修正保留原有 \(B,C\) 固定矩阵，只在 switch event 上改变 \(I_h\)，所以适合插入既有 FPGA EMT pipeline。
4. 在论文的 two-level FPGA 实现中，IEM 增加 29 个 registers、726 个 LUT 和一个 cycle，不增加 RAM 或 DSP48。[pdf:E07]（PDF 物理页 5，Tables II–III）
5. three-level、Boost、carrier-frequency 和 time-step 实验都支持 IEM，但“通用”仍受相邻无源量一拍内近似不变这一条件约束。[pdf:E10]（PDF 物理页 7，Figs. 11–12）[pdf:E11]（PDF 物理页 7，Table V）

**3 句话：**

1. 论文把 virtual power loss 从参数调优问题重新解释为 event initialization 问题。
2. 修正很便宜，而且在所测三类 converter 与 0.5–1.5 µs 步长下把损耗压到接近零。
3. 最值得继续验证的不是再看一组漂亮波形，而是寻找相邻无源量不再近似恒定、多个开关同时动作时的失败边界。

**1 句话：**

IEM 的核心价值是用一次低成本的换态状态重置，换回固定导纳 ADC 原本丢失的 ideal-switch 一致性。

## § 9 — 最脆弱的假设

最脆弱的假设是：**开关换态后的正确稳态 history current，可以由相邻 series/parallel passive branch 在 \(t-\Delta t\) 的单个样本可靠代表。** 论文把这个假设具体化为 \(L_f\gg L_{\text{switch}}\)、\(C_f\gg C_{\text{switch}}\)，其物理含义是 filter inductor current 或 filter capacitor voltage 在一个仿真步长内足够慢，可近似 independent source。[pdf:E05]（PDF 物理页 4，Eq. (14)）

如果这个假设不成立，IEM 不再是“把状态放到正确稳态”，而只是把错误初值换成另一个带一拍延迟的估计。它可能在 \(L_f\) 与 \(L_{\text{switch}}\) 同量级、\(C_f\) 与 \(C_{\text{switch}}\) 同量级、高 \(di/dt\)/\(dv/dt\)、强谐振、相邻支路含受控源或多个开关同步换态时失效。失败代价不是精度略降，而是核心机制重新产生 oscillation 与 virtual power loss，甚至把不一致状态同时注入多个支路。

论文给出的支持证据，是 two-level、three-level 和 Boost 三类拓扑的波形，以及 2–20 kHz carrier 与 0.5–1.5 µs step 的扫描。[pdf:E09]（PDF 物理页 6，Figs. 9–10）[pdf:E10]（PDF 物理页 7，Figs. 11–12）[pdf:E11]（PDF 物理页 7，Table V）缺失证据则是：没有扫描 \(L_f/L_{\text{switch}}\) 与 \(C_f/C_{\text{switch}}\) 比值，没有同步多开关 event stress test，没有误差界或稳定性证明，也没有展示当代理量快速变化时 \(I_h\) reset 的残差。因此，论文验证了若干典型点，却没有测到这项最关键假设的边界。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不需要先重建完整 FPGA 平台；先在同一个 numerical kernel 中复现 event-level 误差，能更直接检验核心 claim。

1. **数据与模型：** 建一个 two-level VSC bridge arm，采用 Table IV 的 \(700\ \text{V}\)、\(220\ \text{V RMS}\)、\(50\ \text{Hz}\)、\(L_f=1.5\ \text{mH}\)、\(C_f=60\ \mu\text{F}\)、\(C_{dc}=10000\ \mu\text{F}\) 参数，并实现三条完全共享外部电路的路径：细步长 ideal-switch reference、原始 L/C ADC、带 IEM 的 L/C ADC。[pdf:E07]（PDF 物理页 5，Table IV）
2. **实现：** 严格按 Eqs. (1)–(8) 实现固定 \(B,C\) 的 baseline，再按 Eqs. (12)–(13) 只在 gate transition 上替换 switching-branch \(I_h\)。每次换态记录 reset 前后 \(I_h\)、相邻 \(i_L/v_C\) 和下一拍 KCL residual。[pdf:E03]（PDF 物理页 2，Eqs. (1)–(8)）[pdf:E05]（PDF 物理页 4，Eqs. (12)–(13)）
3. **扫参：** 先复现 carrier 2、5、10、15、20 kHz；再复现 \(\Delta t=0.5,1,1.5\ \mu\text{s}\)。第二天起额外扫描 \(L_f/L_{\text{switch}}\) 与 \(C_f/C_{\text{switch}}\)，因为这正是方法假设而不是普通性能参数。
4. **测量：** 预先明确定义 virtual power loss ratio 的能量积分窗口与符号；同时报告 switch voltage/current NRMSE、每次 event 的 initial-error magnitude、最大 KCL residual 和能量平衡残差。这样即使“总损耗很小”，也能看到是否只是正负误差抵消。
5. **支持标准：** 在论文三个步长上，IEM 的 loss ratio 应接近 Table V 的 0.10%、0.19%、0.27%，并且换态首拍误差、waveform NRMSE 和 energy residual 同时显著低于 non-IEM；容差应在运行前根据数值精度和测量窗口登记，而不是看完结果再调整。
6. **反驳标准：** 若 IEM 只能靠重新调 \(L_{\text{switch}}/C_{\text{switch}}\) 才有效，若它降低总能量误差却增加局部 KCL residual，或在满足 Eq. (14) 的基准点仍无法稳定压低首拍误差，则核心 claim 被反驳。若软件通过，可把相同 kernel 综合到目标 FPGA，单独检查“1 cycle、无额外 DSP/RAM”的工程 claim。

## § 11 — 最强反例设计

最强反例不是换一个 converter 名称，而是主动破坏 IEM 的信息来源。构造一个双开关同步换态的谐振 switching cell：让开关相邻支路同时包含与 \(L_{\text{switch}}\) 同量级的电感、与 \(C_{\text{switch}}\) 同量级的电容，并在换态前制造高 \(di/dt\) 或 \(dv/dt\)。此时 \(t-\Delta t\) 的相邻 branch current/voltage 既不近似当前稳态，也可能因为另一个开关同步换态而改变约束关系。

实验仍比较 ideal-switch reference、non-IEM ADC 和 IEM ADC，但二维扫描 \(\Delta t\) 与 \(L_f/L_{\text{switch}}\)（或 \(C_f/C_{\text{switch}}\)），并对每次 event 测量 reset 后 KCL/KVL residual、局部能量注入和后续振荡衰减。预期的攻击结果是：进入比例不再“远大于”的区域后，IEM 的首拍 residual 系统性增大，virtual power loss 不再接近零，甚至高于 non-IEM。若这一失败边界与 Eq. (14) 一致，论文的机制解释反而得到加强，但“universally applicable”必须收缩；若在作者声称的比例范围内也失败，则核心算法本身受到直接挑战。[pdf:E05]（PDF 物理页 4，Eq. (14)）[pdf:E12]（PDF 物理页 7，Conclusion）

还应排除一个替代解释：Fig. 9–11 的改善可能部分来自特定 \(L/C\) 参数与 oscilloscope 带宽对高频振荡的平滑，而不完全来自正确 initialization。反例实验因此必须同时保存未经 DA/示波器滤波的内部 state traces，不能只看显示波形。

## § 12 — Follow-up Research Idea

在 power electronics、EMT real-time simulation 与 FPGA 领域，高影响工作通常需要同时满足三点：数值机制可解释、实时硬件代价可实现、在代表性系统和极端工况下可复现。本文在机制解释和资源复用上很强，但缺少 event-level consistency guarantee 与失败边界，因此后续方向应优先补这两个缺口，而不是只增加更多 converter topology。

**候选研究想法：network-consistent event projection for fixed-admittance switching。** 这不是声称已验证 novelty，而是在未做充分相关工作检索时提出的候选方向。

- **(a) 未满足的需求：** 当前 IEM 对每个开关分别复制相邻无源量的上一拍样本；遇到 simultaneous switching、strong coupling 或快速变化代理量时，多个局部 reset 可能彼此不满足 KCL/KVL。需要在不重建全局导纳矩阵的前提下，让换态后的内部状态共同满足网络约束。
- **(b) 可能的研究价值：** 把“典型拓扑上损耗很小”提升为“给定局部条件时，event residual 有可计算上界”，并明确失效域。对该领域而言，这能同时提高模型可信度、composability 与 HIL 安全性。
- **(c) 可借鉴的方法：** 借鉴 constrained state projection、descriptor-system consistent initialization 和 energy-based residual correction。实现上不做新的全局 nonlinear solve，而是针对本次 switching cut-set 建一个小型局部约束块；固定拓扑的 factorization 预存，event 时只求低维 correction vector，再更新相关 \(I_h\)。
- **(d) 第一个证伪实验：** 使用第 11 节的双开关同步换态谐振 cell，比较原 IEM 与局部 projection。若 projection 不能在相同 step、相同 fixed-admittance matrix 下同时降低 KCL residual、energy error 与 virtual power loss，或者资源/latency 超过实时预算，这个方向应立即否决。
- **(e) 与本文的实质区别：** 本文用单个相邻 branch 的延迟样本启发式估计每个开关的新稳态；候选方法把一个 switching event 中的多个 history states 作为整体，通过显式网络约束求一致修正。问题定义从“消除单开关 initial error”变为“在固定导纳框架中保证多事件离散状态的一致初始化”。

这个方向只有在局部约束块能保持固定规模、可预因子化，并且 FPGA 上的额外 cycles 与 DSP/LUT 开销可控时才有工程意义。本文的 state-machine 资源复用思想提供了实现起点：State 3 保留并行 matrix-vector pipeline，projection 放在其前后并复用 arithmetic IP，而不是另建一套长 critical path。[pdf:E06]（PDF 物理页 4，Figs. 5–6）第一阶段不应宣称“更通用”，而应先画出原 IEM 与 projection 各自的可证伪适用域。
