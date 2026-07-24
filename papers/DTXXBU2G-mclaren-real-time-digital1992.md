# A real time digital simulator for testing relays

作者：P. G. McLaren、R. Kuffel、R. Wierckx、J. Giesbrecht、L. Arendt  
出处：IEEE Transactions on Power Delivery, Vol. 7, No. 1, pp. 207–213  
年份：1992  
DOI：10.1109/61.108909  
Zotero key：DTXXBU2G  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述的研究问题**是：怎样把电磁暂态电力系统仿真真正放进继电保护测试闭环，让实际 relay（继电器）接收由仿真器实时产生的电压、电流，并把跳闸触点反馈给仿真中的 breaker（断路器），而不是仅播放预先算好的波形。作者给出的 RTDS（Real Time Digital Simulator，实时数字仿真器）采用并行 DSP（Digital Signal Processor，数字信号处理器）架构，以 50–100 μs 的时间步长运行，并允许 physical device（物理装置）参与闭环交互；论文用商用 distance relay（距离保护）作了示范。（PDF 物理页 1，Abstract）[pdf:E01]

这个问题重要，不只是因为测试速度更快，而是因为保护动作会改变被测系统本身。早期慢速机电式继电器可以用工频重电流台验证；随着“instantaneous”电子继电器出现，故障直流偏置、travelling wave（行波）、transducer distortion（互感器/传感链畸变）等亚周波细节会同时影响正确动作与误动作。昂贵的 analogue TNA（模拟暂态网络分析仪）能保留闭环，却规模有限；offline EMTP（离线电磁暂态程序）能提高模型复杂度，但播放固定波形时失去真实交互，参数修改和重算也慢，且文中指出输出存储通常只覆盖约 0.5 s 故障波形。（PDF 物理页 1，Introduction）[pdf:E02]

因此，论文的工程价值是把“算法算得像不像”与“真实保护装置在动态系统里怎样动作”连接起来。它把测试对象从孤立 relay 扩展为 relay–breaker–power-system 的闭环系统，这对 back-up protection（后备保护）、power-swing blocking（功率摆动闭锁）和 adaptive protection（自适应保护）尤其关键，因为这些功能的结果取决于先前动作造成的系统状态变化。（PDF 物理页 1，Introduction）[pdf:E02]

## § 2 — 前人工作与不足

论文把既有路线分成四类。第一类是工频重电流试验台和 point-on-wave switching（选相合闸）设备，适合较慢保护或有限的暂态重放；第二类是大型 analogue TNA，可闭环但昂贵、稀缺、搭建复杂；第三类是 offline EMTP 先算波形、再经 D/A 与功率放大器重放，模型细但不能自然接受 relay 动作后继续求解；第四类是论文引用的早期实时系统，包括 1988 年的 digitally controlled real-time analog simulator、1990 年的 Digital Model Power System、1989 年的 parallel machine，以及 1991 年用数字实时仿真器闭环测试 joint var controller 的工作。这里对相关文献的描述仅来自本论文参考文献表，未做外部核验。（PDF 物理页 1，Introduction；物理页 6，References [3]–[6]）[pdf:E02][pdf:E03]

这些方法“不够”的原因并不相同。模拟平台的问题是成本、规模和模型复用性；离线数字重放的问题是 causal interaction（因果交互）被切断，relay 的 trip signal 不能在同一求解过程中改变 breaker、重合闸和后续 power swing；把 relay 也建模进离线程序，又会把“测试真实装置”替换成“测试一个 relay 模型”，引出模型有效性问题。论文真正针对的是这个三角矛盾：**足够细的电磁暂态模型、硬件闭环、以及每个时间步都按时完成**，此前很难同时满足。（PDF 物理页 1，Introduction 与 Simulator hardware）[pdf:E02][pdf:E04]

## § 3 — 重建作者的思考路径

以下是**基于证据的重建**，不是作者逐字陈述。

研究者首先会观察到：保护动作时间进入几十毫秒后，测试波形不能再只保留工频包络，必须保留故障起始角、直流偏置和传播暂态。接着会发现，离线计算虽然准确，但一旦 relay 的触点动作需要改变 breaker 状态，预计算波形就失去闭环意义；而纯模拟平台又难以扩展和复用。（PDF 物理页 1，Introduction）[pdf:E02]

第二步是把瓶颈写成 real-time deadline（实时截止期）：电磁暂态研究约需 50 μs 级时间步，而论文估计其测试系统每步需要数亿次浮点运算，普通 workstation 当时只能间歇达到少量 MFLOPS，因此必须采用 special-purpose parallel processing（专用并行计算）。（PDF 物理页 1，Simulator hardware）[pdf:E04]

第三步是利用电力网络的稀疏结构。作者让 compiler 用 diakoptic techniques（分块解耦/分割技术）把系统模型拆成可在多个 rack/processor 上并行执行的 block，并只在下一时间步需要时交换跨 rack 数据。这样，计算并行、通信依赖和物理 I/O 被组织成固定周期流水，而 host workstation 只负责建模、编译、下载和诊断，不进入硬实时求解。（PDF 物理页 2，PE/IRC/WIC；物理页 3，Simulator software）[pdf:E05][pdf:E06]

最后一步是把“仿真输出”变成“测试台接口”：每个 PE 提供可缩放 analogue channel，把电压电流送入 conditioning amplifier；relay 触点作为 logic input 返回，触发 breaker model。由此，数字求解器不再只是波形生成器，而成为可被真实装置改变状态的实验对象。（PDF 物理页 2，Fig. 1 与硬件说明）[pdf:E05][pdf:E07]

## § 4 — 核心 Intuition

核心 intuition 是：**把电力系统方程按网络稀疏性拆开，让多个 DSP 在每个固定时间步内并行完成各自的局部求解，再用确定的通信与 I/O 把真实 relay 嵌入闭环。** relay 看到的是实时生成的二次侧电压电流，relay 的 trip contact 又立即改变仿真 breaker，因此测试保留了“装置动作会改变后续波形”的因果链。（PDF 物理页 1–3，Simulator hardware、Fig. 1、Simulator software）[pdf:E04][pdf:E07][pdf:E06]

## § 5 — 具体方法与完整 Pipeline

以论文的距离保护测试为例，完整 pipeline 如下。

1. **搭建系统。** 用户在 host workstation 的 DRAFT 图形界面中，从元件库拖拽 generator、line、breaker、fault 等 icon，输入元件参数；另一输入程序提供 governor、AVR、故障时刻/类型和 prefault load flow。DRAFT 的画面与组件库见 Fig. 3。（PDF 物理页 3，Fig. 3 与 Simulator software）[pdf:E06]
2. **编译与分配。** compiler 把图形数据和动态数据合并，使用 diakoptic techniques 将系统分成 decoupled blocks，分配到可用的 PE/IRC card；各元件的 processor machine code 由手工汇编并存于 host library，用户不直接接触底层代码。（PDF 物理页 3，Simulator software）[pdf:E06]
3. **硬实时执行。** RTDS 由标准 19 英寸 rack 组成，每 rack 含 18 张 PE card、1 张 IRC 和 1 张 WIC；本次 relay 测试用了 2 个 rack。每张 PE 最多 13 MFLOPS，提供 2 个 analogue monitor channel 和 6144-location circular buffer；IRC 交换下一时间步所需的 rack 间数据，论文把其传输标为 500 MHz，WIC 通过 10 MHz Ethernet 完成下载与诊断但不参与实时求解。（PDF 物理页 1–2，Simulator hardware）[pdf:E04][pdf:E05]
4. **外部接口。** PE analogue output 经 voltage/current conditioning amplifier 驱动 relay；relay trip signal 作为 logic input 回到 simulator，形成 Fig. 1 的闭环。测试装置主要外设是 6 路电流和 6 路电压 conditioning amplifier。（PDF 物理页 2，Fig. 1 与测试装置说明）[pdf:E07]
5. **运行工况。** compiler 完成后，系统先在 turbine governor 控制下运行到 prefault steady state；操作者确认放大器和记录设备就绪后施加故障。relay 触点闭合后，breaker model 在第一个电流过零投入 pre-insertion resistor，并在下一个电流过零切断电流；论文为保持系统同步，在故障移除后 100 ms 重合闸，这一处理用于连续测试而非复现实际保护规程。（PDF 物理页 3–4，Results 与 Fig. 4 上方正文）[pdf:E06][pdf:E08]
6. **记录与观察。** 变量可保存在 PE circular buffer，也可从 analogue channel 输出到数字示波器。论文记录 relay 处的三相电压、电流、trip signal，以及重合闸后的 machine rotor Δω 动态波形，用来观察故障、跳闸、重合闸和 power swing 的连续过程。（PDF 物理页 4–6，Figs. 5–10）[pdf:E09][pdf:E10][pdf:E11]

模型与平台边界同样重要：论文采用 DSP 与 programmable VLSI card，不是 FPGA implementation；它说明使用高速 floating-point arithmetic，但没有报告数值位宽、舍入策略、solver 形式或 FPGA mapping。论文也没有多速率算法，报告的是统一的 50–100 μs 实时步长；CT/CVT 模型虽已有代码，本次实验没有启用。（PDF 物理页 1、4，Simulator hardware 与 Results）[pdf:E01][pdf:E04][pdf:E12]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文**没有给出可复述的核心数学推导**：没有展示 transmission-line、generator、breaker 的离散方程，没有矩阵分块公式，也没有稳定性、截断误差或收敛分析。因此这里不能把后来的 EMT/real-time simulation 数学框架倒灌进论文。

论文提供的数学层信息只有三点。第一，数字仿真器通过求解各元件行为方程来代替 analogue scaled model；第二，电磁暂态需要约 50 μs 级步长，并要求每个时间步内完成数亿级浮点工作；第三，compiler 用 diakoptic techniques 把网络分成 decoupled blocks 并在多个 processor/rack 上执行。（PDF 物理页 1，Simulator hardware；物理页 3，Simulator software）[pdf:E04][pdf:E06]

其工程 intuition 可以这样理解：每个 block 在当前 step 内根据本地状态和边界量更新，下一个 step 前通过 IRC 交换必要耦合量；只要计算、通信和 I/O 总延迟不越过固定 step deadline，仿真时钟就能与物理时钟同步。这是**基于架构证据的解释**，不是论文给出的定理。论文未报告误差界，因此“能按时跑”不能自动推出“数值足够准确”。

## § 7 — 实验设计与结论

**问题 1：系统能否让实际 distance relay 进入闭环并完成故障切除？**  
实验：作者搭建两端电源、两段 100 km transmission line、breaker 和 fault point 的系统，relay 位于线路一端；一端是 ideal source，另一端是含 governor 与 AVR 的 turbo-alternator model，prefault 从发电机送出 263.73 MW、unity power factor。被测装置是三段式 circular mho distance relay，zone 1 对应 80 km，zone 2 为 zone 1 的 120%，zone 3 正向为 zone 2 的 150%、反向为 zone 1 的 25%。（PDF 物理页 4，Fig. 4 与测试系统正文）[pdf:E08][pdf:E12]  
答案：三相故障位于线路 50 km 处时，Fig. 5 的 fault initiation 到 relay trip 相隔 22.4 ms；相间故障报告 21.6 ms，说明真实 relay 的 trip signal 已进入仿真 breaker 流程。（PDF 物理页 4，Fig. 5 与结果正文）[pdf:E09]

**问题 2：平台能否呈现会影响 relay decision 的波形差异？**  
实验：作者比较 line-to-ground fault 的无直流偏置、最大偏置、最大偏置加 5 Ω fault resistance，以及 close-up reverse fault；Figs. 6–9 保留电压、电流与 relay trip trace。（PDF 物理页 5，Figs. 6–9）[pdf:E10]  
答案：论文直接陈述，加入 5 Ω fault resistance 后 trip time 增加；近区反向故障只在故意设为 40 ms 的 zone 3 timer 到时后动作，而 zone 1/zone 2 未 pickup，作者据此判断 memory polarisation 行为正确。（PDF 物理页 4，结果正文；物理页 5，Fig. 9）[pdf:E09][pdf:E10]

**问题 3：系统能否连续呈现重合闸后的 electromechanical dynamics（机电动态）？**  
实验：比较 100 ms 与 200 ms reclose interval 的 machine rotor signal，并在 100 ms case 中同时记录 phase-a current。（PDF 物理页 6，Fig. 10(a)(b)）[pdf:E11]  
答案：波形显示重合闸后存在持续 power swing，且不同重合闸间隔产生不同的摆动轨迹；这证明平台能把 relay/breaker event 与秒级后续动态接在同一次实时运行中。（PDF 物理页 4、6，Results 与 Fig. 10）[pdf:E08][pdf:E11]

**不能外推的结论：** 这些实验主要证明“系统能实时闭环运行并产生合理的 relay response”，没有提供 RTDS 对高精度 offline EMTDC、analogue simulator 或实测录波的定量 waveform error；没有统计 deadline miss、jitter、I/O latency；本次未启用 CT/CVT model，电流放大器上限为 20 A rms，故障电流被人为限制在该范围内。（PDF 物理页 4，测试约束；物理页 6，Conclusions）[pdf:E12][pdf:E13]

## § 8 — Take-aways

**5 句话：**  
1. 论文把实时数字电磁暂态求解器变成了可接实际 relay 的 closed-loop test bench，而不是离线波形播放器。（PDF 物理页 1–2，Abstract 与 Fig. 1）[pdf:E01][pdf:E07]  
2. 其关键工程选择是用网络分块和多 DSP rack 并行，把 50–100 μs step 的计算、通信与 I/O 压进固定 deadline。（PDF 物理页 1–3，Simulator hardware 与 software）[pdf:E04][pdf:E05][pdf:E06]  
3. DRAFT 图形输入、compiler 自动分配和元件代码库使同一硬件可复用为 generator、line 等不同模型，降低了相对 analogue simulator 的重配置成本。（PDF 物理页 2–3）[pdf:E05][pdf:E06]  
4. 距离保护实验覆盖三相、相间、接地、fault resistance、reverse fault 和 reclose/power swing，展示的是闭环能力和工况连贯性，而不是严格的数值精度认证。（PDF 物理页 4–6，Figs. 5–10）[pdf:E09][pdf:E10][pdf:E11]  
5. 论文最欠缺的是 quantitative validation：没有误差、latency、jitter 和 robustness budget，且测试省略 CT/CVT dynamics。（PDF 物理页 4、6）[pdf:E12][pdf:E13]

**3 句话：**  
RTDS 的贡献不是单纯“更快的 EMTP”，而是让真实保护装置能改变实时求解中的 breaker 和后续系统状态。（PDF 物理页 1–2）[pdf:E01][pdf:E07]  
并行 DSP、diakoptic partition 与硬件 I/O 共同完成了这一闭环，论文用距离保护和重合闸后 power swing 给出可见示范。（PDF 物理页 3–6）[pdf:E06][pdf:E09][pdf:E11]  
但它证明了 capability，还没有证明 fidelity envelope（可信精度边界）。（PDF 物理页 4、6）[pdf:E12][pdf:E13]

**1 句话：**  
这篇论文奠定的核心范式是：用确定时限的并行数字仿真，把真实保护硬件放进可交互的电力系统暂态闭环。[pdf:E04][pdf:E07]

## § 9 — 最脆弱的假设

最脆弱的假设是：**50–100 μs 的离散求解、rack 间通信、D/A–conditioning amplifier–relay–logic input 链路，以及被省略的测量链动态，不会改变 relay 的关键判据。** 如果这个假设不成立，实验看到的 trip/no-trip、zone selection 和 operating time 可能是 simulator/interface artifact，而不是原电力系统下 relay 的真实性能。

论文为该假设提供的证据主要是行为一致性：三相和相间故障在约 22 ms 内跳闸、5 Ω fault resistance 延迟动作、reverse fault 只触发 zone 3、重合闸后出现预期 power swing。（PDF 物理页 4–6，Figs. 5–10）[pdf:E09][pdf:E10][pdf:E11] 但缺失的证据更关键：没有与高精度 reference waveform 的误差比较，没有端到端 latency/jitter 测量，没有 step overrun 统计；电流 amplifier 上限为 20 A rms，测试故意限制 fault current，且 CT/CVT model 未在本实验使用。（PDF 物理页 4，Results）[pdf:E12]

所以这篇论文最需要的不是更多“看起来合理”的波形，而是从 primary-system equation 到 relay terminal signal 再到 breaker event 的全链路误差预算。只要某一项误差把 apparent impedance 推过 mho characteristic 边界，closed-loop 仍可实时运行，却可能得出错误保护结论。这一判断是**基于证据的推断**。

## § 10 — 最小复现实验

一周内最有信息量的复现，不必重建整套 rack，而应复现论文的**核心因果 claim：实时步长和接口误差是否会改变距离保护动作**。

- **数据与模型：** 按 Appendix 建立 590 MVA、230 kV base 的两端系统，使用两段 100 km travelling-wave line；采用文中 263.73 MW、unity power factor 的 prefault operating point，并复现 50 km 三相故障。（PDF 物理页 4、6，Fig. 4 与 Appendix）[pdf:E08][pdf:E14]
- **实现：** 做两个版本：一个采用很小 step 的 offline reference，另一个强制 50 μs 和 100 μs wall-clock step；两者输出同一 relay algorithm 或同一台 physical relay。实时版本记录每步 execution time、deadline miss、端到端 I/O latency 与 relay trip time。
- **测量：** 比较故障前后一个周波内的 voltage/current waveform error、apparent impedance trajectory、zone pickup、trip time，以及 breaker event 后波形是否保持一致。
- **支持条件：** 预先规定工程阈值：不得出现 deadline miss，zone decision 必须一致，trip time 与阻抗轨迹误差必须落在复现实验者预注册的容差内。这里的容差是复现实验者提出的判据，不是论文原始 claim。
- **反驳条件：** 只要 50/100 μs step 或 I/O delay 导致 zone 变化、误动/拒动，或 trip time 差异稳定超过预注册阈值，就说明“实时完成”不足以保证“保护结论可信”。

这个实验同时保留论文的最小系统结构和最核心的 relay-in-the-loop 闭环，又增加了原文缺失的 reference comparison 与 deadline measurement。

## § 11 — 最强反例设计

最强反例不是再找一个更大系统，而是构造一个**保护判据恰好对测量链暂态和采样时刻敏感的边界故障**。

具体做法：在 zone 1 reach 附近设置带 fault resistance 的 line-to-ground fault，并加入强 CT saturation 或 CVT transient；用高带宽 reference source 向同一 physical relay 注入“含真实 transducer dynamics”的波形，同时让论文式 RTDS case 保持 CT/CVT 省略、50 μs 与 100 μs step 各运行一次。逐次扫 fault inception angle、DC offset 和 fault resistance，使 apparent impedance trajectory 擦过 mho circle 边界。论文已经显示最大 offset 与 5 Ω fault resistance 会改变 trip timing，而本次测试又明确未使用 CT/CVT model，因此这些变量正好攻击其最薄弱处。（PDF 物理页 4–5，Results 与 Figs. 7–8）[pdf:E12][pdf:E10]

真正有力的反例结果是：reference injection 下 relay 稳定 trip，但 RTDS 下稳定 no-trip，或反之；并且差异可由 step size、I/O latency 或 transducer omission 单独解释。如果这种差异只在保护边界附近出现，它仍足以推翻“该平台可直接用于评价 relay 性能”的宽泛解释，因为工程事故往往就发生在 reach boundary、reverse fault 和 power swing blocking 的边缘条件。

## § 12 — Follow-up Research Idea

在电力系统实时仿真与保护测试领域，高影响工作通常不只追求更大规模或更小 step，还要求**严格的实验验证、工程可实现性和对实际保护决策的可解释保证**。基于第 9 节，候选方向是：建立 **uncertainty-aware and latency-certified relay HIL（不确定性感知、时延可认证的继电保护硬件在环）**。这是候选判断；由于本任务不联网且未系统检索 1992 年后的相关工作，不声称 novelty。

(a) **未满足需求。** 现有示范能证明闭环“跑起来”，但不能回答某次 trip decision 对 step size、solver error、rack communication、D/A、amplifier、CT/CVT 和 logic-input delay 各有多敏感。论文只给出 nominal waveform 与 relay action，没有 fidelity envelope。（PDF 物理页 4、6）[pdf:E12][pdf:E13]

(b) **潜在研究价值。** 把研究目标从“实时速度/模型规模”改成“对保护决策给出可验证置信边界”，能直接服务 relay type test、setting validation 和现场 commissioning；成果可以同时是数值方法、实时调度和硬件测量链的统一认证方法。

(c) **可借鉴工具。** 从 real-time systems 引入 worst-case execution-time 与 jitter analysis，从 robust control / reachability 引入 uncertainty set propagation，从 software verification 引入 counterexample-guided test generation。它们的共同目标不是提高平均速度，而是寻找会改变 relay discrete decision 的最坏误差组合。

(d) **第一个证伪实验。** 在 mho reach boundary 附近自动搜索 fault inception angle、fault resistance、CT saturation、CVT transient 和 I/O delay 的组合；系统先预测一个“必 trip / 必不 trip / 不确定”decision envelope，再用 physical relay 重复注入验证。若实际动作落在预测 envelope 之外，方法立即被证伪。

(e) **与本文的实质区别。** 本文的目标是构造并展示一台并行 DSP RTDS，证明它能以 50–100 μs step 接入真实 relay 并运行闭环。（PDF 物理页 1–3）[pdf:E01][pdf:E04][pdf:E07] 候选研究把“实时能力”降为前提，把“保护结论在数值与接口不确定性下是否仍然可靠”提升为核心问题；这不是增加一个模块，而是改变验收对象。
