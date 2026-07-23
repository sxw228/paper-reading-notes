# Comprehensive Real-Time Simulation of the Smart Grid

- 作者：Feng Guo, Luis Herrera, Robert Murawski, Ernesto Inoa, Chih-Lun Wang, Philippe Beauchamp, Eylem Ekici, Jin Wang
- 出处：IEEE Transactions on Industry Applications, 2013, 49(2): 899–908
- DOI：10.1109/TIA.2013.2240642
- Zotero key：ENI8NE24

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是单一求解器加速问题，而是一个跨域的实时闭环问题：怎样在物理时间内同时运行含大量高速开关的电力电子微电网模型和有协议、路由、排队、带宽、时延的通信网络模型，使控制命令经历通信网络后再真正作用于电力系统。作者把困难拆成两部分。第一，smart grid 中的大量 PWM 变换器要求小步长，但长期离线仿真过慢，也缺少连接真实设备的接口；第二，把通信只压缩成一个固定延迟，会丢掉竞争接入、路由和负载变化引起的非线性时延。论文因此把“电力系统是否稳定”与“信息何时到达”放在同一个 wall-clock 闭环中研究。[pdf:E01][pdf:E02]

重要性首先来自实验成本：大型 smart grid 的实体试验平台昂贵，即使微电网试验台在当时也很少；实时仿真则允许长期运行、HIL 接口和控制器原型测试。[pdf:E01] 更关键的是，通信延迟不是附加的显示误差，而会改变动作顺序。论文的负荷切除案例表明，MCC 看到的 LES 直流母线电压晚于本地电压，导致断路器重开推迟，直流母线跌得更深并带来更大的交流母线电压下降。[pdf:E08] 所以本文的价值不是“把两个软件连起来”，而是让通信行为进入电力系统因果链。

## § 2 — 前人工作与不足

在电力实时仿真一侧，传统 digital real-time simulator 已能运行大型、慢频率、少开关的电网模型并支持 power-in-the-loop，但高速功率电子器件把计算约束推到了更小步长。作者列出的对比很具体：已有单个三相逆变器实时模型使用 10 μs 步长，FPGA 上的二极管箝位三电平 VSC 可达 500 ns；然而一个包含两个可再生能源单元和两个逆变器的微电网只能以 1 kHz 开关频率实时运行。它们分别证明了“小对象可很快”和“小系统可实时”，却没有解决大量高速开关同时存在时的规模问题。[pdf:E01]

在通信—电力联合仿真一侧，已有工作研究过 17-bus 电网中的带宽与时延，RTDS 也被用于保护继电器测试，另有实时 HIL 电网连接两个物理通信节点来研究监控和 cyber vulnerability；但这些方案要么是离线联合模型，要么把通信网络分开研究，要么只用很小的物理网络。作者认为它们不足以同时表达电力电子细节与可重构的通信协议、路由、排队和传输过程。[pdf:E02]

还要注意一个边界：论文没有用统一 benchmark 定量比较上述系统的精度、最大网络规模和总成本。因而“comprehensive”在本文中应理解为电力、通信和控制的集成范围更完整，而不是已经证明在所有性能维度上优于前人。这是基于论文实验设计的判断，不是作者给出的排名结论。

## § 3 — 重建作者的思考路径

可以从两个已知失败模式逆向走到本文方案。第一条路径来自电力实时仿真：开关事件可能落在固定计算步内部；一味减小全局步长会破坏实时约束，一味增大步长又会错过事件。既然事件稀疏而连续状态仍可按较大步长推进，就应把步内开关时刻单独处理；当开关数增加导致拓扑组合近似按 \(O(2^N)\) 膨胀时，再把全局状态空间拆成较小矩阵组，并把子系统分发到多核并行执行。[pdf:E03]

第二条路径来自网络控制：随机接入网络中，源到达率和时延不是线性关系。20 个上报节点在低流量时全部竞争信道很快，但流量越过阈值后延迟陡增；把节点分成四组虽然引入轮候，却能把拥塞点推迟到更高到达率。[pdf:E02][pdf:E03] 这说明“给控制信号加一个常数 delay”不能覆盖状态切换时的网络重构和拥塞。于是自然的下一步是让成熟的离散网络模拟器接收真实 packet traffic，再用 SITL gateway 把它与实时电力模型和外部 MCC 连接。

最后一步是选择能同时触发两类难题的案例：具有 LES、PV、DFIG 风机、功率电子负载、固态断路器和 MCC 的社区微电网。孤岛切换同时要求高速开关模型保持稳定、局部控制切换参考量、MCC 经通信网络执行 load shedding，因此它能在一次实验里观察计算实时性和通信闭环效应。[pdf:E05][pdf:E06][pdf:E07]

## § 4 — 核心 Intuition

本文的核心 intuition 是：不要用一个更小的全局步长硬扛所有开关，也不要用一个常数时延代替整个通信网。电力侧把步内事件、拓扑组合和子系统计算分别交给 event interpolation、SSN 与并行核；通信侧让真实 packet 经过 OPNET 的缓存、协议、路由、发送与接收，再让两个模型按同一 wall clock 并行闭环。[pdf:E03][pdf:E04] 这样，实时性来自分解计算负担，系统真实性来自保留跨域交互的因果顺序。

## § 5 — 具体方法与完整 Pipeline

以论文的社区微电网为例，完整 pipeline 如下。

1. **建立电力模型。** 在 Matlab/Simulink 中建立 LES、PV、DFIG 风机、三路非关键负荷、关键负荷、功率变换器和固态断路器。LES 模型考虑 SOC 与温度，PV 使用数学阵列模型，风机使用 DFIG 和 back-to-back inverter；整个案例接近 100 个开关，grid-connected 与 islanding 两种模式都保持 10 kHz 开关频率。[pdf:E05][pdf:E06]
2. **把高速开关模型放进实时求解框架。** RT-EVENTS 与 FPGA 处理落在一个计算步内部的离散开关事件，允许模型使用较大步长而不直接丢掉事件时刻；SSN 把全系统状态空间矩阵拆成较小矩阵组，避免开关拓扑组合带来的矩阵数量爆炸；子系统再分发到多台 simulator 的不同 CPU core 同步执行。平台由四台实时模拟器、八颗 CPU、48 个 core、五片 FPGA 和 500 多个模拟/数字 I/O 构成，论文报告单个 subsystem 可超过 100 个开关，整体最多 48 个 subsystem。[pdf:E03]
3. **建立通信网络。** OPNET 中为 breaker、sensor、LES 电压节点和 MCC 建立独立 IP subnet、router/gateway 与静态路由。论文示例使用六个 SITL gateway，其中五个连接电力网络接口，第六个连接 MCC；非关键负荷断路器通过 51.8 Mb/s 的 SONET OC-1 模拟光纤，PCC 断路器经 WiFi 802.11，LES 直流母线节点经 Ethernet。[pdf:E04][pdf:E05]
4. **连接两个时间域。** 电力模型在 Linux 实时模拟器上运行，OPNET 在另一台电脑上运行，MCC 位于第二台外部电脑。Linux 外部 C 代码通过 TCP/IP 或 UDP/IP 和物理 Ethernet 交换数据。OPNET 不只附加 delay，而是逐包执行过滤、缓存、协议处理、路由、发送和接收；电力连续模型与通信离散模型都以 wall clock 速率运行，因此可在真实时间互相闭环。[pdf:E04][pdf:E05]
5. **执行控制。** 并网时三个 grid-tied inverter 采用外直流电压环、内交流电流环；孤岛后 PV 与 DFIG 仍按电流源运行，LES inverter 改为控制交流母线电压并承担 swing bus，LES dc/dc converter 则改为维持直流母线。MCC 根据运行模式更新保护设置、监测状态并发出网络重构和负荷切除命令。[pdf:E05][pdf:E06][pdf:E07]
6. **比较通信假设。** 三相短路触发 PCC 断开。理想通信实验令数据瞬时到达；综合实验让 MCC 每 10 ms 上报/发送，并保留各路径不同 latency。MCC 先切除三路非关键负荷，再每 0.1 s 重接一路；若 730 V 直流母线阈值被越过，就重新断开最后接入的负荷。最后比较本地与 MCC 观测电压、断路器动作时刻和母线波形。[pdf:E07][pdf:E08]

数值表示方面，论文没有报告 CPU/FPGA 上的定点或浮点格式、位宽、LUT/BRAM 使用量、代码生成细节或 FPGA 中实际映射了多少开关；不能从“五片 FPGA”外推为全部电力求解都已 FPGA 化。

## § 6 — 核心数学推导

论文的数学分成通信排队近似和 inverter 小信号环路，两者都用于说明设计，而不是给出整个平台的统一收敛或稳定性证明。

通信侧先用已有 CSMA/CA 性能模型 \(F\) 估计服务率：

\[
\mu_0=F(N,\lambda),\qquad D_0=\frac{1}{\mu_0-\lambda}\ {\rm s}.
\]

这里 \(N\) 是竞争节点数，\(\lambda\) 是每节点 packet arrival rate，\(D_0\) 是含排队时间的平均 delay。若分成 \(K\) 组，每次仅 \(N/K\) 个节点竞争，则

\[
\mu_k=F(N/K,\lambda),
\]

\[
D_k=t\left(\frac{K-1}{2}+
\left\lfloor\frac{1}{t(\mu_s-\lambda)}\right\rfloor K+1\right).
\]

第二式把等待本组 active slot 的时间和 active 时段内的竞争等待合并起来；源 PDF 在该式使用 \(\mu_s\)，而前文服务率写作 \(\mu_k\)，本文保留原符号并不替作者消除这个记号不一致。[pdf:E02] 在 \(t=35\) ms 的例子中，\(K=1\) 在 \(\lambda<2.5\) packets/node/s 时更低延迟；超过该点后 \(K=4\) 更合适，其延迟陡增被推迟到 \(\lambda>8\) packets/node/s。若 \(T_A=T_B=150\) ms，常规模式可用 \(K=1\)，异常上报率越过 2.5 后应考虑 \(K=4\)。[pdf:E03]

电力控制侧，grid-connected 模式下 LES inverter 的简化电流对象为

\[
\frac{I_d}{V_{dl}^{*}}=\frac{1}{L_f s+R_f},
\tag{1}
\]

它表示 filter inductor \(L_f\) 与 resistor \(R_f\) 决定从 d 轴电压指令到 d 轴电流的一级动态。把内电流环视作理想后，dc-link voltage 外环对象为

\[
\frac{V_{dc}}{I_d^{*}}=\frac{1}{Cs}.
\tag{2}
\]

直观上，电容 \(C\) 对净电流积分，所以电流指令决定直流母线电压变化率。作者据此为内外环都选 PI controller。[pdf:E05]

islanding 模式下，LES inverter 要从并网电流源切换为交流电压源。加入输出 capacitor \(C_f\) 后，电流对象变为二阶：

\[
\frac{I_d}{V_{dl}^{*}}=
\frac{C_f s}{L_fC_f s^2+R_fC_f s+1},
\tag{3}
\]

而含内电流 PI 参数 \(K_{cp},K_{ci}\) 的外电压对象为

\[
\frac{V_d}{I_d^{*}}=
\frac{K_{cp}s+K_{ci}}
{L_fC_f s^3+(R_fC_f+K_{cp}C_f)s^2+(K_{ci}C_f+1)s}.
\tag{4}
\]

Eq. (3)–(4) 的工程意义是：孤岛时输出电容与 filter 共同形成更高阶动态，外环不能继续照搬并网时的纯电容积分对象；局部 controller 的结构仍保持多环，只改变 LES inverter 的外环 feedback/reference，因而避免在模式切换瞬间重构全部局部控制器。[pdf:E06][pdf:E07]

论文没有展开 switch event interpolation 或 SSN 的核心矩阵推导，也没有给 Eq. (1)–(4) 的参数整定值、闭环极点、稳定裕度或离散化误差证明。因此这些公式能解释控制结构，却不足以单独证明“数百开关、10 kHz”条件下的数值精度与稳定性。

## § 7 — 实验设计与结论

**问题 1：平台能否在 real time 运行含大量高速开关的详细微电网？** 作者构建接近 100 个开关、开关频率 10 kHz 的社区微电网，先不考虑通信 latency，制造三相短路并观察 grid-connected 到 islanding 的切换。Table I 给出 60 Hz 系统频率、800 V 直流母线、240 V line-to-ground 交流母线、5.3 kW PV、10 kW 风机、10 kW critical load 与 15 kW noncritical load 等条件。[pdf:E06] Fig. 9 的示波器波形显示切换后直流母线、交流母线和负荷电流保持受控，作者报告电压、电流 spike 不超过正常值的两倍，并据此认为局部控制与实时平台能处理该模型。[pdf:E07][pdf:E08] 结论页还报告该通信/案例仿真占用不超过平台计算能力的 10%，并把能力概括为数百开关、最高 10 kHz。[pdf:E09]

**问题 2：显式通信模型会不会改变电力系统结论？** 作者在 islanding 时构造 23.6 kW 最大供电与 25 kW 总负荷的功率缺口：LES 8.3 kW、PV 5.3 kW、wind 10 kW；三路 noncritical load 各 5 kW，critical load 10 kW。MCC 每 0.1 s 重接一路负荷，并以 730 V 为 LES 直流母线阈值。[pdf:E07] 对照组假定通信瞬时；实验组加入 OPNET 路径 latency 且 MCC 每 10 ms 发送数据。Fig. 10 显示实验组的非关键负荷不能与 PCC 同时断开，也不能严格每 0.1 s 重接，MCC 看到的直流母线电压滞后于本地值，CB3 重开更晚，直流与交流母线下降更大。[pdf:E08] 因而作者的答案是：忽略通信会给出过于乐观的动态响应。

**问题 3：本文证明到什么边界？** 它证明了这套指定 hardware/software 组合能 real-time 运行一个细节丰富的案例，并在同一平台上观察到 communication-aware 与 ideal-communication 的不同。它没有报告与离线高精度 EMT reference 的逐波形误差、deadline miss 统计、clock drift、端到端 timestamp 校准、资源利用率分解，也没有用真实通信网络重复 Fig. 10。因此不能外推为所有 topology、网络负载、故障类型下都准确，更不能把“实时跑完”自动等同于“数值结果已对地面真值验证”。

## § 8 — Take-aways

**5 句话。** 第一，smart grid 的实时仿真瓶颈同时来自高速开关计算和通信闭环，单独解决一侧会漏掉系统级行为。[pdf:E01] 第二，event interpolation、SSN 分解与多核并行分别处理步内事件、拓扑组合和计算吞吐。[pdf:E03] 第三，OPNET SITL 让 packet 真正经历协议、路由、缓存和传输，再与电力模型按 wall clock 闭环。[pdf:E04] 第四，在接近 100 个 10 kHz 开关的微电网案例中，作者演示了并网到孤岛的受控切换。[pdf:E05][pdf:E07] 第五，显式通信 latency 使负荷切除和重接推迟、母线跌落加深，说明理想通信假设可能改变控制结论。[pdf:E08]

**3 句话。** 本文贡献是一套 communication-aware power real-time co-simulation platform，而不只是一个更快的 EMT solver。它用分层计算保住实时性，用 packet-level SITL 保住跨域因果链，并以 islanding/load-shedding 案例展示二者的必要性。[pdf:E03][pdf:E04][pdf:E08] 但论文主要证明“能运行且结果会不同”，尚未证明跨域 timing 与电磁暂态的绝对精度。

**1 句话。** 智能电网控制的结果取决于电能如何流动，也取决于信息何时到达，因此两者必须在同一个实时闭环里验证。[pdf:E08]

## § 9 — 最脆弱的假设

最脆弱的假设是：OPNET、Ethernet adapter、外部 MCC 与多台实时 simulator 以 wall clock 并行运行，就足以让所观察到的端到端 timing 代表目标 smart grid 的真实通信—控制时序。论文直接陈述两类模型都按 wall-clock rate 运行，并把这种同步视为平台优势；它还把 Fig. 10 中本地电压与 MCC 电压的时间差解释为总通信 delay。[pdf:E04][pdf:E08]

这个假设一旦失效，核心贡献会从“通信网络改变电力动态”退化成“本实验的软件调度与接口延迟改变了动态”。例如 OPNET SITL batching、操作系统 scheduler jitter、TCP/UDP adapter buffering、多 simulator clock drift 或示波器通道对齐误差，都可能叠加到协议与路由 latency 上。论文没有给硬件 timestamp、clock offset/drift、deadline miss 分布，也没有把软件接口延迟与模拟网络延迟分离，更没有用物理通信网络做 trace 对照。这些是基于证据的批评，不是论文已证实存在的 bug。

作者提供的支持是闭环波形和平台实物/拓扑，证明系统确实联机运行；缺少的则是跨域时间基准的校准证据。[pdf:E04][pdf:E05][pdf:E08] 因此最关键的未决问题不是“波形看起来是否稳定”，而是 Fig. 10 中多出来的 delay 究竟有多少来自被研究的通信机制、多少来自 co-simulation plumbing。

## § 10 — 最小复现实验

一周内不应复现整套四 simulator、五 FPGA 平台，而应只验证本文最关键、最可证伪的 claim：显式通信时序会使 load-shedding 动作推迟并加深母线跌落。

1. 在可用的实时 simulator 或固定步长 Simulink 环境中建立简化 dc-link energy balance、LES voltage control、三路 5 kW noncritical load 和一路 10 kW critical load；供电上限采用 LES 8.3 kW、PV 5.3 kW、wind 10 kW，阈值设为 730 V。若硬件允许，再加入论文 Table I 的 800 V dc bus 与 10 kHz switching；否则明确使用 averaged converter，只复现通信 claim。[pdf:E06][pdf:E07]
2. 实现同一套 MCC state machine：PCC fault 后切除三路非关键负荷，每 0.1 s 重接一路，监测电压跌破阈值后断开最后接入的负荷。运行三种条件：零延迟；固定 10 ms sample/transport delay；从一段可重复的 packet trace 回放 jitter 与 loss。[pdf:E07][pdf:E08]
3. 所有进程使用同一硬件 clock 或 PTP timestamp。记录本地 \(V_{dc}\) 采样时刻、MCC 接收时刻、command 发出/到达时刻、CB3 实际动作时刻、最低 \(V_{dc}\)、最低 \(V_{bus}\) 和每步 deadline overrun。
4. 支持本文 claim 的最低结果是：在零 overrun 且 clock offset 可忽略时，加入通信 trace 会稳定地增加 MCC 观测滞后与 CB3 动作延迟，并使母线 nadir 更低；反驳结果是差异在 timestamp 校正后消失，或主要由 simulator overrun/adapter buffering 解释，而不是被注入的 network timing。

这个实验刻意不复现“数百开关”能力，因为那需要原平台和大量模型工程；它用最小系统隔离本文最重要的跨域因果关系。

## § 11 — 最强反例设计

最强反例不是把 latency 设得更大，而是让“同一条真实通信 trace”在两种执行路径中得到不同电力结论。具体做法是用硬件 timestamp 在一套物理 Ethernet/WiFi/SONET-equivalent testbed 上采集每个 packet 的发送、排队、到达与丢失时刻，然后把完全相同的 trace 分别驱动：A）OPNET SITL 闭环；B）不经过 OPNET、直接按 timestamp 向 MCC/电力模型重放。两边使用同一电力模型、同一初始状态、同一 MCC 逻辑和同一 clock。

若 A 与 B 的 CB3 动作时刻、\(V_{dc}\) nadir 或 \(V_{bus}\) 跌落显著不同，且差异随 SITL gateway 数、CPU load 或 adapter buffering 改变，那么本文 Fig. 10 的替代解释就是 co-simulation infrastructure 产生了额外 timing artifact，而不是被建模通信网络本身造成响应变化。这个反例直接攻击第 9 节的关键假设，因为本文架构确实让 OPNET、外部 MCC 与实时 simulator 经多个 gateway 和物理 Ethernet 串接，却没有给出端到端时间校准。[pdf:E04][pdf:E05]

反之，如果 hardware-timestamp replay 与 OPNET 闭环在动作时刻和母线指标上都落入预先规定的误差带，且改变 host load 不影响结论，本文最脆弱的一环就得到比原论文更强的支持。

## § 12 — Follow-up Research Idea

**候选想法：从“communication-aware co-simulation”推进到“可归因、可认证的跨域时序 EMT-HIL”。** 这里不声称 novelty，因为本卡没有系统检索 2013 年后的 time-sensitive networking、co-simulation synchronization、real-time scheduling 与 cyber-physical HIL 文献。

**（a）未满足需求。** 现有平台能显示“加入通信后波形不同”，但不能把差异可靠分解为协议排队、network jitter、gateway buffering、clock drift 和 real-time deadline miss。工程用户真正需要的不是另一条波形，而是一份 causal timing budget：某类时延来自哪里，它以多大置信度导致保护误动、母线越限或稳定裕度下降。这个需求直接来自本文 wall-clock 联合架构与 Fig. 10 之间尚未校准的证据缺口。[pdf:E04][pdf:E08]

**（b）潜在研究价值。** 电力电子与电力系统领域通常重视数值精度、实时 deadline、HIL/PHIL 可实现性、可重复工况以及对真实控制/保护设计的价值。若一个平台能在每次运行中同时给出 EMT state error、跨域 clock error、packet causal path 和保护动作归因，它会把“演示型联合仿真”提升为可用于控制器验收的测量系统。

**（c）可借鉴工具。** 可结合 distributed systems 的 PTP/hardware timestamp、real-time scheduling 的 worst-case response-time analysis、network calculus 的 delay envelope，以及 control 领域的 reachability/robustness analysis。每个 packet 和每个 power-step 都携带统一时间戳与因果 ID，平台在线计算 communication uncertainty 到 voltage/current safety margin 的传播，而不是只报告平均 latency。

**（d）首个证伪实验。** 在同一微电网和 MCC 上回放一组具有相同平均 latency、但不同 burst/jitter/loss correlation 的 hardware traces；同时独立改变 host CPU load。若模型预测的母线安全包络无法覆盖实测 \(V_{dc}\)、\(V_{bus}\) nadir，或把 host load artifact 错归因给 network traffic，这个想法即被证伪。

**（e）与本文的实质区别。** 本文的目标是把电力和通信模型在 real time 接起来，并展示通信效应。[pdf:E03][pdf:E04] 候选方向改变了问题定义：目标不再是“是否能联合运行”，而是“能否证明每个跨域动态差异来自哪条 timing causal path，并给出可审计误差界”。这不是增加一个新的 network module，而是把联合仿真从功能平台改造成可认证的 cyber-physical measurement instrument。
