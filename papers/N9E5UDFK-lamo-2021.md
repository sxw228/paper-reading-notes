# Hardware-in-the-Loop and Digital Control Techniques Applied to Single-Phase PFC Converters

作者：Paula Lamo、Angel de Castro、Alberto Sanchez、Gustavo A. Ruiz、Francisco J. Azcondo、Alberto Pigazo  
出处：Electronics，2021，10，1563（Review）  
年份：2021  
DOI：10.3390/electronics10131563  
Zotero key：N9E5UDFK  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文不是提出一种新的 PFC 控制器或 HIL 求解器，而是在回答一个工程选择问题：面向单相 power factor correction（PFC，功率因数校正）变换器，如何把 HIL 类型、变换器数学模型、数值算术、实时硬件平台、数字控制结构和 I/O 需求放进同一套权衡框架。作者把 HIL 的价值概括为：用实时数字模型替代尚未建成或不宜直接冒险测试的功率级，让真实控制器在 nominal、abnormal 和 fault 条件下接受闭环验证；同时指出性能与成本取决于模型、平台和通道配置，而不是只取决于“有没有 FPGA”。这是论文摘要直接陈述的范围与动机，见 PDF 物理页 1 的标题与 Abstract。[pdf:E01]

这个问题重要，首先因为 PFC 的控制目标同时涉及输入电流波形合规与 DC 母线电压调节；其次因为 PFC 动态按电网频率展开，为观察暂态行为常要模拟数百毫秒，而开关模型本身又要求远小于开关周期的实时步长。论文直接指出，HIL 可在建造真实 plant 之前测试控制器，减少局部样机、故障损坏和验证成本；FPGA 因并行计算和较小 time-step 而常被优先选择，但 fixed-point 分辨率不足也可能造成 limit cycle、稳定性问题和稳态误差。相关表述位于 PDF 物理页 2、Introduction。[pdf:E02]

因此，这篇综述的实际价值不是给出一个“最佳工具名单”，而是提醒设计者：PFC-HIL 是闭环系统工程，真实性由模型、solver、算术、事件时序、I/O latency 和控制器需求共同决定。后一句是基于论文证据的归纳，不是作者给出的形式化定理。

## § 2 — 前人工作与不足

论文回顾的前置路线大致分为四层。

第一层是 HIL 之前的 mixed-signal simulator、带模拟扩展的仿真器或多仿真器协同。论文直接陈述，这些方案存在仿真时间长、开发复杂的问题；HIL 的变化是把被控功率级离散化并放到实时数字设备中，把实际 controller 作为 Hardware-under-Test（HuT，被测硬件）。标题页与 Introduction 给出了这一问题转移。[pdf:E01]

第二层是 HIL 形态。Controller hardware-in-the-loop（CHIL，控制器硬件在环）只交换低功率信号，不发生真实能量交换；Power hardware-in-the-loop（PHIL，功率硬件在环）则把真实功率设备接入回路，需要功率源或功率汇。论文在 PDF 物理页 2、Section 2 明确定义二者，[pdf:E03] 并在物理页 3、Figure 1 用接口框图展示 feedback、control/forward signals、A/D 与 D/A conversion 以及 HuT 的边界。[pdf:E04]

第三层是平台与工具。相关工作已经能通过 Typhoon HIL、dSPACE、Opal-RT、RTDS、LabVIEW FPGA、MATLAB/Simulink 等环境，把 schematic 或手写方程映射到微处理器、FPGA 或混合架构。论文引用的商业系统可处理复杂模型，典型 integration step 约 1 µs、PWM 输入读取约 10–20 ns，但资源和步长未必经过针对特定应用的优化；定制 HDL 则可换取更细粒度控制，却要求更高建模与硬件设计成本。该总结来自 PDF 物理页 3、Section 2。[pdf:E05] 物理页 4 对商业工具的比较还指出：Typhoon 的集成能力较完整，LabVIEW 更便于模型定制，而 Simulink 的实时能力依赖运行模式和外部硬件；这些是论文转述的相关文献结论，不是本文在统一实验条件下重新测得的结果。[pdf:E06]

第四层是模型和控制。已有 HIL 采用 average model、switched model、state space、Euler–Lagrange、Port-Controlled Hamiltonian（PCH）以及 Padé approximation 等建模方式；论文称多数 HIL 使用 switched model，因为它能逐步更新状态并复现高频开关事件，而 averaged LTI approximation 对 PFC 往往不够准确。相关综述位于 PDF 物理页 6、Section 3.1。[pdf:E07] Table 2 又把不同文献的模型、变换器、验证方式和平台并列，但案例横跨 LLC、Buck、Boost、SEPIC 与 rectifier PFC，验证基准也不同。[pdf:E08]

这些前人工作真正的不足不是“没有 HIL”，而是缺少可直接迁移的共同决策尺度：工具表比较的是厂商模式和 headline specification，模型表比较的是不同 converter 与不同验证对象，控制分类又按照电流环机制展开。**基于全文覆盖的判断**：论文自身也没有报告系统综述常见的检索式、纳入/排除标准、质量分级或统一 benchmark，因此它提供的是工程 taxonomy（分类框架）与选型线索，不是可复算的 meta-analysis（元分析）。

## § 3 — 重建作者的思考路径

以下是基于证据对作者思考路径的逆向重建，不把论文贡献预设为前提。

1. 先从验证瓶颈出发：真实 PFC 功率级在故障与极端工况下昂贵且可能损坏，纯离线开关仿真又要覆盖数百毫秒暂态，因此需要把真实 controller 留在环中、把 plant 换成实时模型。[pdf:E02]
2. 再确定 HIL 边界：若目标只是验证 controller 的采样、PWM 和闭环逻辑，CHIL 已足够；若要验证真实功率硬件与接口算法，则进入 PHIL，并承担真实能量交换与接口稳定性问题。Section 2 与 Figure 1 给出了这个分叉。[pdf:E03] [pdf:E04]
3. 然后处理实时性：模型必须在 deadline 内完成一次状态推进。选择 switched model 能保留开关事件，但计算压力更大；选择 average 或线性化模型更快，却可能丢掉闭环调试所需的高频行为。[pdf:E07]
4. 接着处理实现成本：floating-point 易于从方程翻译到代码，fixed-point 通常更快、资源更省，但必须为每个变量设计整数位与小数位，并承担量化和重配置成本。论文在 PDF 物理页 7、Section 3.2 明确列出 real、float、fixed 三种算术及其代价。[pdf:E09]
5. 最后把 controller 放回系统：PFC 的内电流环快、外电压环慢，PWM/carrier 的采样和更新又引入额外数字延迟；所以 HIL 的必要分辨率不能脱离控制类型与采样机制单独决定。PDF 物理页 8、Section 5 给出双环结构、latency 与四类电流控制的入口。[pdf:E10]

由此自然得到论文的中心视角：HIL 不是一个孤立的“实时模型”，而是模型、算术、target、I/O 和 digital controller 的 co-design（协同设计）问题。这个中心视角是基于全文结构和结论的合理推断。

## § 4 — 核心 Intuition

核心 intuition 是：**不要把最小 time-step 当成独立目标，而要让 HIL 的模型保真度、计算 deadline、数值表示和 controller 的闭环带宽彼此匹配。** 真实 controller 只会“看到”经模型、solver、I/O 和 PWM 时序共同塑造后的 plant，因此任何一环失真都会成为整体 fidelity 的上限。论文直接强调 customized tool 通常能通过选择更合适的 target、model 和 solver 获得更高分辨率，而 general-purpose tool 的优势是工具链集成；FPGA 的优势来自并发数字块和 clock resolution。[pdf:E11] 最终应优化的是验证速度、可信度和成本的整体 Pareto trade-off，而不是单一硬件指标；这是对论文结论的工程化概括。[pdf:E12]

## § 5 — 具体方法与完整 Pipeline

论文是一篇 review，没有给出单一可执行算法。下面用“低压 Boost PFC 的 CHIL 验证”重建它隐含的完整 pipeline；这是基于论文各节拼合出的工程示例，不是作者报告的一次统一实验。

1. **定义 HuT 与闭环边界。** 把真实数字 controller 作为 HuT，把整流级、Boost 功率级、电网和负载放入 real-time simulator。controller 输出 gate/switch commands，HIL 经 A/D、D/A 或等效数字接口返回输入电压、输出电压和输入电流。CHIL/PHIL 的接口边界与信号方向见 PDF 物理页 2、Section 2 和物理页 3、Figure 1。[pdf:E03] [pdf:E04]
2. **选择数学模型。** 若目标是控制律早期验证和长时间动态，可考虑 average/state-space；若要观察 switching noise、采样误差、过零点与拓扑切换，则优先 switched model。论文直接说 switched model 在小步长内更新每个 state variable，适合 closed-loop debugging；state-space、Euler–Lagrange、PCH 和 Padé-based 分解则提供不同物理解释与实现复杂度。[pdf:E07]
3. **离散化与事件处理。** 连续 differential equations 离散后，每个 simulation step 用当前 state 更新下一状态；switch state 决定该步使用的拓扑。论文没有给出统一离散方程、solver 阶次或稳定性界，因此这些实现细节属于“未报告”，不能从综述中补写成标准答案。Table 2 只能说明不同文献采用了不同模型和验证平台。[pdf:E08]
4. **安排多速率时序。** controller 常以 switching period 采样，PWM/carrier 可以在更细的 clock 上更新。Figure 3 区分 natural sampling、数字 controller 的 double digitization 和每个 switching period 起点的 uniform sampling，并显示由此产生的 delay。[pdf:E13] 论文还给出一个商业例子：Typhoon HIL602 的 PWM sampling step 为 20 ns，而 simulation step 为 500 ns；文献中的 PWM 每周期样本数从至少 20 到数百乃至数千不等。[pdf:E14] 这说明 controller update、PWM edge detection 和 plant state integration 不必使用同一速率。
5. **选择数值表示。** real arithmetic 只适合早期不可综合验证；synthesizable floating-point 易用但资源多；fixed-point 需要逐变量分配位宽，却更适合 time-step 紧张的场景。论文在 Section 3.2 给出三类算术的定义与设计代价。[pdf:E09]
6. **映射到 FPGA 并做并行调度。** 将状态更新、switch/event logic、I/O conditioning 和必要的 control-support blocks 放入并发硬件路径；若采用 FPGA+processor 混合架构，可让 FPGA 承担采样与信号调理，processor 负责较慢的管理与通信。论文对 FPGA 并发性和混合架构的描述位于 PDF 物理页 11、Section 5.1 前文。[pdf:E13]
7. **执行闭环工况。** 输入电网幅值、负载和异常事件，记录 HIL 的状态输出、controller gate signals、latency、deadline miss、资源和与可信 reference 的 waveform error。论文列出的测试方向包括 Monte Carlo failure cases、低成本 multi-solver 环境、fault-tolerant controller 验证，以及 time/frequency-domain impedance fidelity；这些是相关工作中的代表性验证方式。[pdf:E10]
8. **根据 controller 反向调整 HIL。** 四类 PFC current control 对传感带宽、noise immunity、稳定区域和 sinusoidal reference 的依赖不同，Figure 2 给出了 Group I–IV 的闭环结构。[pdf:E15] [pdf:E16] 若 controller 使用 current rebuilding 或高分辨率 carrier，HIL 的 I/O、solver 与 time resolution 必须随之提高；论文结论明确指出 controller 类型会反向决定模型、solver 和 target。[pdf:E17]

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇综述**没有给出可连续复现的核心数学推导**，也没有统一的 PFC state equation、离散化公式、误差界或 real-time schedulability proof，因此不能把它当作某一种 HIL 数值方法的理论论文。可保留的数学骨架只有模型族的工程含义：

- **Switched model**：在每个小 time-step 内，根据开关状态直接推进每个 state variable，因而能表示高频 switching event；代价是更高计算负担。
- **Averaged/linearized model**：围绕 operating point 线性化，电路解释直观、求解快，但论文明确说 averaged LTI approximation 对 PFC 不够准确。
- **State-space model**：把变换器写成 differential equations，离散后逐步更新状态。
- **Euler–Lagrange 与 PCH model**：状态与电感、电容等储能元件相关；PCH 把系统表示为端口互联，端口变量乘积对应功率，即能量变化率。论文还指出 PCH 可由 EL 得到，二者与 state-space 在数学上相近。
- **Padé-based 分解**：把 PFC stage 分成线性 state-space 部分和由 switch state 决定的非线性 feedback 部分。

以上都来自 PDF 物理页 6、Section 3.1。[pdf:E07]

论文真正量化的是实现代价而非控制理论。Table 3 在同一 xc7a100t-csg324-1 FPGA 上列出：float32 加法 88.970 ns、int32 加法 4.658 ns；float32 乘法 52.435 ns、int32 乘法 19.315 ns。按表内数字计算，加法时延比约为 19.1 倍，乘法约为 2.7 倍；Table 4 还显示 floating-point 乘法可通过 DSP48E 与 LUT 的不同组合换取 78.780–52.435 ns 的时延。[pdf:E18] 值得注意的是，正文在前一页概括为“32-bit integer 比 32-bit floating point 快九倍”，但没有说明对应操作，且与表内两种操作的比值都不一致。[pdf:E09] [pdf:E18] 这不是核心理论错误，却暴露了综述把异质综合结果压缩成单一结论时的风险。

## § 7 — 实验设计与结论

由于本文是 review，以下“实验”实际是作者汇总的比较证据，而不是统一 test bench 上的原创实验。

**问题 1：不同 HIL 工具在实时能力与工程便利性上如何权衡？ → 证据：** Table 1 汇总 Typhoon HIL、LabVIEW 两种模式和 Simulink 两种模式。表中 HIL402 给出 50 MHz virtual-machine clock、200 kHz switching frequency 和 500 ns minimum simulation step；LabVIEW FPGA/myRIO 条目给出 40 MHz clock 与理论 25 ns minimum；Simulink Real Time Desktop 列出 normal mode 1 ms、external mode 50 µs。许可、资源报告和 online/offline 模式也不相同。[pdf:E19] **答案：** 论文认为 Typhoon 的集成能力更强，LabVIEW 定制自由度更高，Simulink 更依赖模式与硬件；但这些 headline numbers 来自不同执行语义，不能直接当作同一负载下的速度排名。[pdf:E06]

**问题 2：哪类模型适合 PFC-HIL？ → 证据：** Section 3.1 说明多数 HIL 倾向 switched model，因为它更能复现高频事件；average LTI 对 PFC 可能不够准确。[pdf:E07] Table 2 的五个案例分别采用 LTI+state space、average switch、state space/Euler–Lagrange、Euler–Lagrange 和 Padé+oversampling，平台涵盖 PC、DSP、FPGA，验证对象也不同。[pdf:E08] **答案：** 论文没有证明某个模型全局最优，而是支持“模型必须按闭环调试目标、实时预算和平台选择”的条件性结论。

**问题 3：算术选择是否显著影响 FPGA 性能？ → 证据：** Table 3/4 显示 fixed-point 与 floating-point 在 LUT、DSP48E 和 timing 上差异明显，且同一 floating-point multiplication 也可用不同资源配置换取时延。[pdf:E18] **答案：** 方向性结论成立：fixed-point 可能更快、更省资源，但需要更高位宽设计成本；精确倍数不能脱离 operation、pipeline 和 synthesis configuration 外推。正文“九倍”与表内数据不一致，进一步说明只能把它当示例，不能当普适比例。[pdf:E09] [pdf:E18]

**问题 4：controller 为什么会决定 HIL 要求？ → 证据：** 论文把 PFC current control 分成 DCM/边界模式、NLC、linear average-current 和 phasor-based 四组，并讨论了 bandwidth、noise immunity、bidirectional stability 与 grid-disturbance immunity 的差异。[pdf:E10] [pdf:E15] Figure 2 给出四组控制的结构差异，[pdf:E16] Figure 3 则展示 PWM 采样和数字延迟。[pdf:E13] **答案：** HIL 的必要 time resolution、I/O 通道与模型复杂度必须围绕 controller 的采样、carrier 和状态需求设计，不能先选平台再被动塞入模型。[pdf:E17]

**不得外推的范围：** 论文没有用同一 PFC topology、同一 controller、同一 FPGA、同一 I/O latency 和同一 waveform-error metric 重测各方案；也没有统计纳入文献的偏差。因此，表格能支持 taxonomy 和初步选型，不能支持严格的跨平台 superiority claim。

## § 8 — Take-aways

**5 句话：** ① 单相 PFC-HIL 的核心任务，是让真实数字 controller 在安全、可重复的实时 plant 模型上完成闭环验证。[pdf:E01] ② 模型 fidelity、solver、time-step、arithmetic、FPGA mapping、I/O 和 controller sampling 必须协同设计，任何单项 headline specification 都不足以代表整体真实性。[pdf:E12] ③ switched model 更适合保留高频事件，average/state-space/EL/PCH 等模型则在速度、解释性与实现复杂度之间提供不同折中。[pdf:E07] ④ FPGA 的并发性使其适合高时间分辨率，但 fixed-point 的收益伴随位宽设计、量化和重配置成本。[pdf:E09] ⑤ 这篇论文最有用的是分类与问题地图，最不足的是缺少统一 benchmark、系统综述协议和可复算的跨方案误差比较。

**3 句话：** PFC-HIL 不是“买一台实时仿真器”即可完成的任务，而是 controller-aware 的模型与硬件 co-design。论文提供了工具、模型、算术和控制结构的横向地图，并用表格显示成本与时序差异。[pdf:E19] [pdf:E08] 这些表格适合生成候选方案，不足以单独决定最终架构。

**1 句话：** 可信的 PFC-HIL 应以闭环误差和 deadline 为目标，以 time-step 为手段，而不是反过来。

## § 9 — 最脆弱的假设

最脆弱的假设是：**不同 HIL 方案的最大 time resolution 或 minimum simulation step，可以作为跨模型、跨工具、跨 controller 的共同 fidelity proxy，并据此指导平台选择。** 论文直接写道，HIL 平台时间分辨率越高，结果越接近实际 converter，并据此强调 FPGA 的并发性和 clock resolution；结论还称 FPGA 在可用 target 中提供最佳时间分辨率。[pdf:E11]

这个假设一旦不成立，论文最实用的选型主线就会失效。原因是闭环误差不仅来自 integration step，还来自：average 与 switched model 的结构性 model mismatch，[pdf:E07] PWM sampling 和数字 delay，[pdf:E13] I/O latency 与 controller bandwidth，[pdf:E10] fixed-point quantization，[pdf:E09] 以及不同 current-control group 在过零、DCM/CCM 边界和 grid disturbance 下的行为差异。[pdf:E15] 一个更细的 time-step 无法自动补偿错误的 topology/event treatment、错误的 sensor/actuator delay 或过度简化的 plant model。

论文为该假设提供的证据主要是异质文献和厂商规格：Table 1 的工具运行模式不同，[pdf:E19] Table 2 的 converter、模型与验证对象不同，[pdf:E08] Table 3/4 只比较基础算术 operator。[pdf:E18] 它没有给出同一闭环任务上的 error-versus-step-size 曲线，也没有把 latency、model order 和 arithmetic 保持不变。再加上“九倍”概括与表内数据不一致，当前证据只能支持“分辨率重要”，不能支持“分辨率是可跨方案比较的主导尺度”。

## § 10 — 最小复现实验

一周内最值得做的不是复现整篇综述，而是验证它最关键、也最脆弱的 claim：**在模型与接口保持一致时，提高 HIL 时间分辨率是否稳定改善真实闭环 fidelity，以及这种改善是否值得额外 FPGA 资源。**

实验可以这样收敛：

1. 选一个低压 Boost PFC 或等价安全功率级，使用一个固定的数字双环 controller；controller 作为 HuT，输入为 HIL 返回的 `vin`、`vout`、`iin`，输出为 PWM/gate signal。双环与三变量结构来自 PDF 物理页 8、Section 5。[pdf:E10]
2. 在同一 FPGA 上实现一个固定 topology 的 switched state-space HIL kernel，只改变两项：simulation step 取三档，数值表示取 float32 与经 range analysis 设计的 fixed-point；其余 solver、PWM edge treatment、I/O latency 和 pipeline 保持一致。模型与算术选择依据 Section 3。[pdf:E07] [pdf:E09]
3. 用离线超细步长 switched simulation，或经过限压限流的真实功率级，作为 reference。施加稳态、负载阶跃、电网过零与一次输入电压跌落；后两类场景与论文讨论的控制难点相符。[pdf:E15]
4. 测量每个工况的输入电流 waveform error、DC 母线 overshoot/settling、switching-event timing error、闭环 latency、deadline miss、LUT/DSP 使用和最高可持续 real-time rate。Table 3/4 可作为资源方向性的预期，不把其倍数当作验收标准。[pdf:E18]
5. **支持 claim 的结果：** 在无 deadline miss 且其他条件一致时，步长减小能单调降低关键闭环误差，并形成可解释的 accuracy-resource Pareto front；fixed-point 在相同误差约束下释放足够资源或缩短 critical path。**反驳 claim 的结果：** 误差不随步长单调改善，或更细步长因量化、event handling、pipeline latency 导致结果更差；又或者模型类型的影响远大于步长。

这项实验不需要复现所有商业平台，却能直接检验综述选型逻辑中最关键的一环。

## § 11 — 最强反例设计

最强反例不是证明某个平台“慢”，而是构造一个**更细 time-step 反而更不真实**的闭环对照。

在同一 FPGA、同一 I/O 和同一 controller 下实现两个 HIL kernel：A 使用很细步长的 averaged/LTI model；B 使用较粗步长但保留 switch state、PWM edge 和 DCM/CCM topology transition 的 switched/event-aware model。然后在 PFC 输入过零、DCM/CCM 边界、AC voltage drop 与负载阶跃下，同步对照低压真实 plant。论文已经指出 averaged LTI 对 PFC 可能不够准确、switched model 更适合复现高频事件，[pdf:E07] 也展示了四类控制结构及过零和电压跌落处理问题。[pdf:E15] [pdf:E16]

若 B 在输入电流形状、母线暂态和 gate-event timing 上持续优于 A，即使 B 的 simulation step 更大，就出现了对论文主导直觉的直接攻击：**fidelity 的关键变量是正确的模型边界与事件语义，而不是 nominal time resolution 本身。** 再向两个 kernel 注入相同的可控 I/O latency，可以检验“更高计算分辨率”是否会被接口延迟完全淹没。这个反例还提供一个替代解释：论文观察到的 FPGA 优势可能来自 switched/event logic 与并行 I/O 的整体实现，而不只是更小步长。

## § 12 — Follow-up Research Idea

**候选研究方向：controller-aware adaptive-fidelity HIL compiler（控制器感知的自适应保真 HIL 编译器）。** 由于本任务严格不补充包外相关工作，下面不声称 novelty，只说明由本文局限推导出的研究假设。

**（a）未满足需求。** 现有综述把 model、solver、arithmetic、target 和 controller 列为需要平衡的因素，[pdf:E12] 但实际工作流仍常先固定一个全局 model 与 time-step，再看是否能实时运行。这样会在平稳区间浪费资源，在 PWM edge、过零、DCM/CCM 转换或故障区间又可能保真不足。

**（b）可能的研究价值。** 把目标从“最小化固定步长”改成“在一组闭环风险场景上满足可验证的 fidelity contract，同时不 miss deadline”。系统根据 controller group、当前 operating mode 和误差预算，动态选择 switched/averaged local model、积分步长、fixed/float precision 与 FPGA 并行度。它直接回应论文指出的模型、算术、平台和 controller 必须共同平衡的问题，而不是再增加一个孤立模块。[pdf:E07] [pdf:E09] [pdf:E17]

**（c）可借鉴的相邻工具。** 候选工具包括 real-time systems 的 worst-case execution-time analysis、mixed-criticality scheduling，formal methods 的 mode-transition verification，以及 mixed-precision 与 model-order adaptation。这里是研究设计建议，不是论文原文结论。

**（d）第一个证伪实验。** 在同一 FPGA 与同一 PFC controller 上，比较三种方案：固定细步长 switched baseline、固定粗步长 average baseline、候选 adaptive-fidelity compiler。覆盖稳态、负载阶跃、输入过零、DCM/CCM 边界和电压跌落，测 worst-case closed-loop error、deadline miss、LUT/DSP、功耗和可覆盖仿真时长。若候选方案不能在任一严格误差阈值下改善 error-resource Pareto，或 mode switch 本身引入不可接受的伪暂态，就应否定该方向。

**（e）与已有工作的实质区别。** 它不是把某个既有 HIL 移植到另一块 FPGA，也不是单纯缩小 step；它把“controller 的闭环风险”作为编译输入，把模型族、事件处理、数值精度和硬件调度作为联合决策变量，并要求输出可测的场景级 fidelity guarantee。Figure 2 的控制结构差异与 Figure 3 的采样延迟说明这种 controller-aware 目标是必要的。[pdf:E16] [pdf:E13]
