# Design, implementation and validation of a real-time digital simulator for protection relay testing

**作者**：M. Kezunovic；J. Domaszewicz；V. Skendzic；M. Aganagic；J. K. Bladow；S. M. McKenna；D. M. Hamai  
**出处**：IEEE Transactions on Power Delivery, Vol. 11, No. 1, January 1996, pp. 158–164  
**年份**：1996  
**DOI**：10.1109/61.484012  
**Zotero key**：RUVP93QN  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个明确的工程问题：能否用当时可购买的低成本通用计算机和系统软件，构建一台真正闭环、可实时响应保护继电器动作的数字电力系统暂态仿真器，而不是只离线生成故障波形。作者把目标具体化为三个并行测试端、图形界面、最低约 50 μs 的仿真步长，并要求能够模拟含串联电容、MOV、仪用互感器和受继电器控制断路器的实际网络；系统最终面向 Western Area Power Administration（WAPA）建设并交付。[pdf:E01]（PDF 物理页 1，Abstract）

重要性不只是“算得更快”。保护继电器测试的关键是因果闭环：仿真器输出电压、电流，继电器依据这些信号动作，动作命令又必须及时改变仿真网络拓扑。此前低成本数字方案多为 open-loop，只能回放预先计算的波形，无法直接验证“继电器动作—断路器响应—网络再演化”这一整条链路。[pdf:E02]（PDF 物理页 1，Introduction）论文把实时接口收敛为输出互感器二次电压电流、接收 breaker Open/Close 命令并生成辅助触点，同时用继电器负载的一阶近似避免昂贵的完整闭环负载计算。[pdf:E03]（PDF 物理页 2，Real-time interaction）因此，这篇论文的价值在于把电磁暂态计算、模拟量重构、保护设备接口和实时调度放进同一个可运行系统，并尝试证明通用硬件也能达到继电保护测试所需的时限。

## § 2 — 前人工作与不足

论文对既有工作的概括分三类。第一类是缩比模拟电力系统和混合电子模拟器，技术成熟但专用硬件成本高、配置灵活性有限。第二类是过去十年出现的低成本数字 fault simulator，它们提高了灵活性，却主要以 open-loop 方式工作，不能直接支持被测继电器与模拟电网的实时交互。第三类是面向实时 EMT 的并行计算架构；作者承认已有研究证明并行机能够达到实时性能，但项目在 1991 年评估后认为当时可获得的商用并行平台不适合该应用，于是转向高性能单处理器加专用 DSP 的折中架构。[pdf:E02]（PDF 物理页 1，Introduction）[pdf:E04]（PDF 物理页 1，Real-Time Simulator Design Requirements）

这里的“不足”不是前人不会做暂态计算，而是系统级约束没有同时闭合：既要有足够带宽和模型复杂度，又要接收断路器命令、输出继电器可用的模拟量，还要在每一步验证 deadline。作者的设计改变了成本假设：不追求一台昂贵的全并行专机，而是把主网络计算留在 IBM RISC 工作站，把互感器、断路器和 I/O 相关任务下沉到多个 DSP 与硬件接口。[pdf:E05]（PDF 物理页 4，Fig. 6–7 与 Real-time Simulator Design Implementation）以上是论文对 prior work 的直接叙述，本卡未联网独立核验其完整性或优先权。

## § 3 — 重建作者的思考路径

可以从论文给出的约束逆向重建出以下思路。

首先，继电保护关注的输出带宽并不要求把整个 EMT 计算无限加速，但步长必须足够小。论文用 trapezoidal integration 的误差经验指出，采样频率应至少约为目标输出带宽的十倍；对大于 500 Hz 的保护测试带宽，对应采样频率大于 5 kHz、步长小于 100 μs。[pdf:E06]（PDF 物理页 2，Real-Time Simulator Design Requirements）这给出了“必须实时完成”的硬预算。

其次，作者观察到电网模型并非一个不可拆分的整体。传播时间长于步长的输电线路会自然把节点导纳矩阵切成 block-diagonal 子网，适合分任务求解；MOV 的非线性则通过把器件与周围网络组合成复杂元件，并改用电压更新而非每次重构矩阵，把运算增长从 quadratic 降到 linear。[pdf:E07]（PDF 物理页 2，Fig. 2 与 Simulation Problem Properties）[pdf:E08]（PDF 物理页 2，Simulation Problem Properties）

再次，作者把物理设备本身的延迟当作调度资源。断路器从收到命令到机械触头真正运动存在显著延迟，传输线路也有传播延迟；这些 latency 可以从设备任务中“抽出”，转化为队列和 look-ahead 空间，从而吸收主处理器逐步计算时间的波动。[pdf:E09]（PDF 物理页 3，Simulation Problem Properties）[pdf:E10]（PDF 物理页 4，Fig. 5）

最后，只有在输出波形、设备模型和实时监控也被拆成独立层后，通用主机才可能专注于主网络求解。因此形成了“RISC 主网络 + DSP 设备模型 + 硬件时钟/I/O + 独立 GUI”的分层系统，而不是单纯优化一个数值求解器。[pdf:E05]（PDF 物理页 4，Fig. 6–7）这是基于论文证据的思路重建，不是作者逐字给出的推导过程。

## § 4 — 核心 Intuition

核心 intuition 是：不要要求一颗处理器在每个物理事件发生的瞬间完成全部 EMT、设备和 I/O 工作，而要利用网络传播、互感器弱耦合和断路器机械延迟，把系统拆成带 latency 的任务图。主网络计算的抖动由 FIFO、look-ahead 和分层时钟吸收，仪用互感器与断路器任务交给 DSP，最严格的采样抖动则由硬件完成。[pdf:E10]（PDF 物理页 4，Fig. 5）[pdf:E11]（PDF 物理页 4，Fig. 8）因此，实时性来自“物理延迟 + 架构分工 + deadline 监测”的共同设计，而不是单一算法的峰值速度。

## § 5 — 具体方法与完整 Pipeline

以一个三端线路保护测试为例，完整 pipeline 如下。

1. **场景与模型输入**：用户通过独立 GUI 配置主网络、故障事件、线路模型、串联电容与 MOV，以及三个保护测试端。论文要求支持最多三个独立继电器同时与同一网络交互。[pdf:E01]（PDF 物理页 1，Abstract）
2. **主网络离散与分区**：主网络采用 EMTP 类节点方程和 trapezoidal integration。传播时间大于当前步长的输电线路把网络自然解耦成子网，对应 block-diagonal conductance matrix；论文没有在本文重新给出完整 EMT 元件方程，而把相关算法细节指向此前工作。[pdf:E06]（PDF 物理页 2，采样关系）[pdf:E07]（PDF 物理页 2，Fig. 2）
3. **非线性元件处理**：对串联补偿电容的 MOV，作者把非线性元件及其邻近电路作为一个复合元件，用 voltage-updating scheme 代替 conventional matrix updating，以减少实时迭代成本。[pdf:E08]（PDF 物理页 2，Simulation Problem Properties）
4. **互感器任务解耦**：作者用 CCVT 输入阻抗随频率和负载的仿真说明，在多数负载条件下其一次侧近似电容性，因此可忽略一次、二次的互相影响，或在主网络中用等效电容近似，把 CCVT/PT/CT 的详细模型移到独立处理器。[pdf:E09]（PDF 物理页 3，Fig. 3 及相邻正文）
5. **处理器映射**：IBM RS/6000/580 执行主网络；三个 TMS320C40 DSP 分别执行三个端口的 instrument transformer 模型；第四个 DSP 执行 breaker model，并负责主机与其他 DSP 的数据分发。每个端口还有 I/O、waveform reconstruction 和 amplifier 子系统。[pdf:E05]（PDF 物理页 4，Fig. 6–7）论文没有 FPGA 映射，也未报告定点/浮点位宽或数值格式。
6. **模拟量重构**：离散电压、电流经 8 倍 oversampling digital filter 与 brick-wall analog low-pass filter 重构。该子系统支持 3.2–44 kHz 可变采样频率，论文报告在所有高于 \(f_s/2\) 的频率上带外衰减超过 85 dB。[pdf:E12]（PDF 物理页 3，Fig. 4 与相邻正文）
7. **闭环动作**：继电器接收放大后的模拟量，返回 Open/Close 命令。断路器模型按 T1–T4 机械动作时间推进，并输出 a、aa、b、bb 四个辅助触点；“To RTS”信号允许选择主网络何时真正改变开关状态。[pdf:E13]（PDF 物理页 5，Fig. 10–11）
8. **多层实时约束**：第一层硬件按每个 50–100 μs 采样周期向 D/A 送数，实际发送时刻要控制在理想采样边沿的约 ±1 ns 内；第二层由四个 DSP 在步长尺度同步；第三层 RISC 主网络利用断路器延迟把可用调度窗口放宽到 10–50 ms。[pdf:E11]（PDF 物理页 4，Fig. 8 与 First Layer）[pdf:E14]（PDF 物理页 5，Second/Third Layer）
9. **执行监控与失败处理**：系统允许某次 run 因 deadline 失败，但必须立即检测、通知并安全停机。实时运行时，AIX 的后台服务和其他并发应用被停用，实时进程被 pin 到物理内存，系统中断也被关闭，以避免 page fault 和不可控抢占。[pdf:E04]（PDF 物理页 1，设计要求）[pdf:E14]（PDF 物理页 5，Operating System Support）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有给出一套新的 EMT 数学理论，也没有编号方程；核心形式化内容是步长约束和带 latency 的队列模型。

对采样步长，论文写出 Nyquist 关系

\[
f_N=\frac{f_s}{2}=\frac{1}{2t_s}.
\]

其中 \(f_s\) 是仿真采样频率，\(t_s\) 是单步时长。作者进一步采用一个工程经验：为使 trapezoidal integration 的输出误差保持在约 10% 以下，\(f_s\) 至少应为目标输出带宽 \(B\) 的十倍，即 \(f_s\gtrsim10B\)。若保护测试需要 \(B>500\,\text{Hz}\)，则 \(f_s>5\,\text{kHz}\)，所以 \(t_s<100\,\mu\text{s}\)。[pdf:E06]（PDF 物理页 2，Real-Time Simulator Design Requirements）这不是严格误差上界证明，而是作者据引用文献采用的设计准则。

对任务同步，每个 task 由 execution time、input data set 和 latency 描述。latency 表示在当前输入集下还能向前产生多少帧输出；把这些延迟移入 FIFO 后，慢任务可以与快任务异步推进。论文声称系统吞吐量由最慢任务决定，且为了避免丢帧，一条数据链路上的 FIFO 容量至少应覆盖该链路各任务 latency 之和；Fig. 5 用两个任务的 \(\tau_1\)、\(\tau_2\) 示意这一规则。[pdf:E15]（PDF 物理页 3，Real-time Program Model）[pdf:E10]（PDF 物理页 4，Fig. 5 与相邻正文）其工程含义是：实时系统不是消除所有执行时间波动，而是用可证明足够的缓冲深度把波动隔离在因果允许的窗口内。

## § 7 — 实验设计与结论

**问题 1：互感器模型能否从主网络解耦？** → 作者仿真典型 CCVT 在不同二次负载下的一次侧输入阻抗，并观察其随频率的变化 → 除一次回路 60 Hz 谐振附近、尤其二次短路时偏差明显外，从很低的 10 Ω 负载起曲线已接近理想电容，因此作者认为可忽略一次侧影响，或在主网中用等效电容近似，再把详细 IT 模型放到独立处理器。[pdf:E09]（PDF 物理页 3，Fig. 3）

**问题 2：可变采样波形重构是否有足够带宽？** → 作者在电压放大器输出端测量重构系统频率响应，比较 3.2、10、20、36、44 kHz 等采样设置 → 系统在 3.2–44 kHz 范围工作，且高于 \(f_s/2\) 的带外衰减超过 85 dB；高频噪声底上升被归因于 12-bit FFT 分析仪的分辨率。[pdf:E12]（PDF 物理页 3，Fig. 4）

**问题 3：主机单步时间怎样随事件变化？** → 作者对 RS/6000/580 的主网络求解及向 TMS320C40 传输进行逐步 profiling，Fig. 9 给出约 2500 个 step 的时间轨迹 → 计算时间并非常数；一次 breaker 或 time-controlled switch 操作约增加一个 18 μs 量级的单步惩罚，单个 MOV 活动约增加 3 μs，简单、不利用物理延迟的设计在该案例中最短步长需约 87 μs，系统最多支持 9 个继电器控制的 breaker pole。[pdf:E16]（PDF 物理页 5，Design Verification）Fig. 9 的最高标注约为 86.5 μs，与这一结论相符。[pdf:E17]（PDF 物理页 5，Fig. 9）

**问题 4：利用断路器 latency 后能否跑到约 65 μs？** → 作者选择一个基于实测参数的两周波断路器模型，开断延迟与行程合计形成 19.6 ms 的机械响应窗口，即超过 300 个步长；用该窗口让主网络最多提前约 300 sample 计算 → 对 Fig. 9 的工作负载，作者估算可达 64.7 μs，并用一次实际 real-time run 验证了 65 μs 步长。[pdf:E18]（PDF 物理页 6，Fig. 12 前后正文）

**问题 5：通用平台是否具有持续运行余量？** → 作者报告 RISC CPU 在实时 run 中持续利用率超过 90%，并提供一个非实时 profiling 版本，以平均执行时间加约 4–7 μs I/O 开销来预测下一次实时 run 的起始步长 → 论文认为这使 3.2–44 kHz 的可变运行点可被实际选定。[pdf:E19]（PDF 物理页 6，Design Verification）

论文最后直接声称：低成本商用硬件和系统软件可以构建保护继电器实时数字仿真器，复杂网络下 50–100 μs 步长可实现，并可随商用硬件升级。[pdf:E20]（PDF 物理页 6，Conclusions）但不得外推的是：本文展示的验证重点是 timing、bandwidth 和若干部件建模依据，未给出继电器动作正确率、端到端波形误差统计、与另一台实时仿真器的系统级对照，也没有展开摘要所称 WAPA 实际系统模型的详细验证结果。[pdf:E01]（PDF 物理页 1，Abstract）这是本卡基于证据范围作出的批评性判断。

## § 8 — Take-aways

**5 句话**：第一，这篇论文证明了实时 EMT 继电保护测试可以被重新表述为一个带物理 latency 的任务调度问题，而不只是一个矩阵求解速度问题。[pdf:E10]（PDF 物理页 4，Fig. 5）第二，作者把主网络、互感器、断路器、I/O 和 GUI 分到 RISC、四个 DSP 与硬件接口，形成了三个保护端口的闭环系统。[pdf:E05]（PDF 物理页 4，Fig. 6–7）第三，步长目标由保护带宽和 trapezoidal integration 的误差约束给出，核心门槛是小于约 100 μs。[pdf:E06]（PDF 物理页 2）第四，单步峰值本来接近 87 μs，但借助约 19.6 ms 断路器机械延迟，实机运行达到 65 μs。[pdf:E16]（PDF 物理页 5）[pdf:E18]（PDF 物理页 6）第五，证据支持“该案例可实时运行”，但还不足以证明跨网络、跨继电器和跨快速开关设备的普适性能。

**3 句话**：系统的真正创新点是协同利用网络解耦、设备弱耦合和机械延迟，把不均匀计算负载转成可缓冲的任务流。[pdf:E07]（PDF 物理页 2）[pdf:E09]（PDF 物理页 3）硬件层负责纳秒级采样时钟，DSP 负责设备模型，RISC 负责主网络，从而在商用平台上达到 50–100 μs 级实时步长。[pdf:E11]（PDF 物理页 4）[pdf:E20]（PDF 物理页 6）最需要谨慎的是，65 μs 成绩依赖具体断路器 latency 和事件组合，而非无条件的 worst-case deadline 保证。

**1 句话**：这是一种用电力设备的因果延迟换取通用计算机实时性的系统架构。[pdf:E18]（PDF 物理页 6）

## § 9 — 最脆弱的假设

最脆弱的假设是：**被模拟设备和网络中始终存在足够大的、可预测的物理 latency，能够覆盖主网络计算的峰值和事件突发。** 这不是辅助假设，而是 65 μs 结果成立的关键。论文自己的 profiling 表明，不使用 latency 隐藏时，该案例单步要求约 87 μs；真正达到 65 μs，是因为两周波断路器给出 19.6 ms、超过 300 step 的 look-ahead 窗口。[pdf:E16]（PDF 物理页 5，Design Verification）[pdf:E18]（PDF 物理页 6，Fig. 12 前后正文）

该假设在实际中可能失效的原因是：某些测试目标可能需要把断路器或开关动作延迟设得很短；多个端口可能在相近时刻触发；MOV 可能同时、持续导通；或者线路传播时间不再大于步长，减少自然子网解耦。论文对常规机械断路器给出 1 到大于 5 个周波的延迟范围，并用一个具体两周波模型验证，但没有给出 latency 接近零、事件高度聚集时的 deadline 结果。[pdf:E13]（PDF 物理页 5，Fig. 10–11 与相邻正文）因此，证据支持“在该类机械延迟条件下有效”，不支持“对任意保护设备和事件时序都有效”。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 WAPA 电网，而是“断路器 latency 是否真的把不可实时的 workload 变成可实时”这一核心 claim。

数据方面，源包没有 Fig. 9 的原始 trace，因此建立一个透明的 synthetic workload：基础单步时间使用一个低于 65 μs 的可调分布生成，这一分布是复现实验假设而非论文报告值；再加入 Fig. 9 明确标注的约 86.5 μs 峰值，breaker event 每次增加约 18 μs，MOV active 每个器件每步增加约 3 μs；断路器参数采用 Fig. 12 的 19.6 ms 响应窗口。[pdf:E16]（PDF 物理页 5）[pdf:E17]（PDF 物理页 5，Fig. 9）[pdf:E18]（PDF 物理页 6，Fig. 12）这些数值只用于重建论文报告的调度压力，不声称复现电磁波形。

实现两个 scheduler：A 是每步必须在 65 μs 内完成的 naive scheduler；B 是按 Fig. 5 的 latency/FIFO 模型允许主网络在断路器真正改变拓扑前 look ahead 的 scheduler。[pdf:E10]（PDF 物理页 4，Fig. 5）测量 deadline miss 数、最大 lateness、FIFO 最大占用、是否发生数据覆盖，以及在 2500 step 运行中输出时间戳是否保持 65 μs 周期。

支持 claim 的结果是：A 在 breaker/MOV 峰值处出现 miss，而 B 在 19.6 ms latency 下零 miss 且 FIFO 不溢出；反驳 claim 的结果是：即使采用论文给定 latency，B 仍出现 miss、需要不可接受的 FIFO，或输出事件顺序与输入因果关系不一致。这个实验只验证调度机制，不验证 CCVT、MOV 或继电器动作的电气准确性。

## § 11 — 最强反例设计

最强反例是构造一个“零松弛事件簇”：把断路器从论文验证的两周波机械响应改成只剩 1–2 个仿真步长的有效延迟，同时让三个端口的 9 个 breaker pole 在相邻 step 动作，并让多个 MOV 在同一窗口持续导通。主网络仍以论文报告的约 65 μs 周期运行，比较 latency-aware scheduler 与离线无 deadline 的参考执行。[pdf:E16]（PDF 物理页 5，9 poles、breaker/MOV 代价）

攻击点不是简单说“硬件太慢”，而是切断作者机制中的因果缓冲：当设备命令几乎立即改变网络拓扑时，主机不能提前计算，FIFO 也不能隐藏 breaker 引起的约 18 μs 单步峰值。若此时出现 deadline miss、事件次序错位，或继电器看到的电压电流序列与离线参考不同，就说明论文的实时性来自特定机械延迟，而不是架构本身对最坏事件的保证。反过来，如果系统仍能稳定满足 65 μs，并保持端到端波形和动作时序一致，这个反例就被否证。

## § 12 — Follow-up Research Idea

候选研究方向是：**面向零物理松弛的“deadline-certified、relay-decision-equivalent” EMT 双路径仿真器**。这里不声称 novelty，因为按输入边界没有检索 1996 年之后的相关工作。

（a）驱动需求：原系统靠断路器和线路 latency 隐藏计算峰值；一旦设备动作接近即时，实时保证就失去基础。[pdf:E18]（PDF 物理页 6）新目标不再是“尽量精确地逐点复现所有波形”，而是“在固定 deadline 内保证被测继电器会作出与高保真参考一致的保护决策，并显式给出波形误差预算”。

（b）潜在研究价值：保护测试真正关心的是 trip/no-trip、动作时间和状态序列。若能在 commodity CPU 上用高保真 EMT 路径计算常态区间，在事件突发时切到固定时延的保守近似路径，并证明两条路径在继电器决策边界上等价，就能把性能保证从依赖机械延迟改成依赖可验证的误差界。

（c）可借鉴工具：real-time scheduling、hybrid systems、reduced-order modeling、anytime algorithm，以及 FPGA 的固定时延流水线。FPGA 不必复刻全部 EMTP，而可只承载最坏时刻的 nodal update、MOV 复合元件和短窗 surrogate；CPU/DSP 在 deadline 之外回补高保真状态。原论文没有 FPGA 实现，因此这是候选架构，不是对原系统的事实描述。

（d）第一个证伪实验：使用第 11 节的零松弛事件簇，把 breaker latency 压缩到 1–2 step；同时运行离线高保真基线与双路径实时系统。若任一案例发生 deadline miss，或继电器 trip decision、动作时刻超出预设容差，该想法立即被否证。

（e）实质区别：原论文通过物理 latency 让主网络“提前算”；候选系统在 latency 不存在时，通过有误差界的计算模式切换和固定时延硬件路径保证“按时给出对保护决策足够正确的结果”。它改变了优化目标和正确性定义，而不是仅给原架构增加一块更快的加速器。
