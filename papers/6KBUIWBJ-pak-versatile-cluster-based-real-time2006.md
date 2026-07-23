# A Versatile Cluster-Based Real-Time Digital Simulator for Power Engineering Research

**作者：** Lok-Fu Pak, M. Omar Faruque, Xin Nie, Venkata Dinavahi  
**出处：** IEEE Transactions on Power Systems, Vol. 21, No. 2, 2006  
**DOI：** 10.1109/TPWRS.2006.873414  
**Zotero key：** 6KBUIWBJ

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的问题不是“如何把离线仿真算得更快”，而是如何用通用、可扩展的硬件，在每个物理时间步结束前确定性地完成电力系统模型计算，并同时容纳真实控制器、保护装置和模拟/数字 I/O。离线工具可以在数值时间轴上任意快慢地推进，但 hardware-in-the-loop（HIL，真实硬件处于仿真闭环中）要求仿真时钟追上墙上时钟；若某个时间步超时，外部硬件看到的就不再是可信的实时对象。作者把最困难的对象明确为含高速开关和复杂电路的电力电子系统，并把快速硬件、并行软件、实时操作系统与外部 I/O 一起视为解决条件。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

RTX-Lab 的工程目标是做一个由 commodity-off-the-shelf（COTS，商用现成）组件构成、能够扩容、支持标准 MATLAB/SIMULINK 工作流并可连接真实硬件的研究平台，而不是为某一种电路定制专用模拟器。论文报告的平台由 8 个 cluster node 组成，每节点有两颗 3.0 GHz Intel Xeon，共 16 个处理器；节点间可使用高速网络，FPGA 负责多通道 I/O 和精细事件时间戳。[pdf:E01][pdf:E02][pdf:E03]（PDF 物理页 1–3，Abstract、Section II）

这项工作的价值有三层。第一，研究者可以在控制器或保护装置真正接入之前复现故障和快速开关过程。第二，通用处理器与标准建模环境缩短模型开发周期。第三，cluster 的潜在扩展性使“计算量超过一颗 CPU”不必立刻转向昂贵专机。不过，后文实验也表明“增加节点”与“缩短实时步长”不是同义词；通信开销可能吞掉并行收益。[pdf:E05][pdf:E09][pdf:E10]（PDF 物理页 5、9–10，Sections IV–V）

## § 2 — 前人工作与不足

论文把当时的实时数字仿真器分为 DSP、RISC、CISC 和 VLSI 等路线，并指出专用处理器方案的主要代价是成本与开发周期；通用处理器更便宜，也更容易沿用成熟的软件工具。作者还提到 FPGA 当时主要作为高速外围 I/O，而不是核心求解器；PC cluster 则已成为可负担高性能计算的一条路线。[pdf:E01]（PDF 物理页 1，Introduction）

对本论文最直接的先行方向是已有的 DSP 实时仿真器、基于 PC 的电气系统实时仿真器，以及 Hollman 与 Marti 的 PC-cluster 实时网络仿真。[pdf:E01][pdf:E10]（PDF 物理页 1、10，Introduction 与 References）论文没有逐项重现实验比较这些平台，因此它证明的是“RTX-Lab 这一完整组合可以工作”，而不是在同一模型、同一步长与同一成本口径下优于所有 prior work。作者真正补上的工程拼图是：双 Xeon 节点、实时 Linux 的 CPU shielding、节点间多种通信链路、FPGA I/O、MATLAB/SIMULINK 模型入口、multirate 和开关事件时间戳被组织成一个可运行平台。[pdf:E02][pdf:E03][pdf:E04]（PDF 物理页 2–4，Sections II–III）

此前方案“不够”的原因可以更精确地表述为三个接口断裂：专用算力与通用模型开发环境之间的断裂，单机实时计算预算与复杂电力电子模型规模之间的断裂，以及纯数字计算与真实硬件时序之间的断裂。RTX-Lab 分别用 COTS PC 与 SIMULINK、空间并行与多速率、FPGA I/O 与硬件同步来接这些接口。这个判断是基于论文架构的重建，不是作者做过受控 baseline 消融后的结论。

## § 3 — 重建作者的思考路径

可以从实时仿真的硬约束倒推这套设计。

第一步，任何模型都必须满足
\[
T_{\mathrm{I/O}}+T_{\mathrm{comm}}+T_{\mathrm{compute}}+T_{\mathrm{acq}}+T_{\mathrm{sync}}\leq h,
\]
其中 \(h\) 是实时步长。这不是论文给出的编号公式，而是根据 Fig. 5 的时间步 anatomy 所作的工程化重写。[pdf:E05]（PDF 物理页 5，Fig. 5）

第二步，操作系统的中断、context switch 与非抢占调用会制造 jitter，使平均计算够快但最坏时间仍可能越过 \(h\)。于是需要实时 Linux，并把一颗 CPU shield 给确定性计算，另一颗处理操作系统事务。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Sections III-A、IV-B）

第三步，一颗 CPU 不够时，自然想到把模型拆成 subsystem 并行计算；但节点之间必须交换边界量，因此需要明确 master/slave 的 send、receive、compute、acquisition 顺序，并把通信也计入 deadline。[pdf:E05]（PDF 物理页 5，Fig. 5 与 Section IV-A）

第四步，电机等慢动态不必按电力电子开关的最快步长重复求解，于是把快慢模型放到整数倍采样率下运行 multirate，以节省计算。[pdf:E05]（PDF 物理页 5，Section IV-C）

第五步，外部 PWM 边沿不一定落在仿真时间格点上；仅靠 CPU 步长会丢掉亚步长时序。因此让 100 MHz FPGA 捕获事件，再配合插值将有效事件精度推进到 1 μs 以内。[pdf:E03]（PDF 物理页 3，Section II-C）

这条路径的核心不是单独发明某种求解器，而是把 deadline、jitter、partition、rate 和 event timing 当成一个端到端系统问题。

## § 4 — 核心 Intuition

实时电力仿真能否成立，取决于每一步最坏执行路径是否收在 deadline 以内，而不是处理器的标称峰值速度。作者的办法是把不同性质的工作放到最合适的位置：CPU cluster 负责可并行的模型计算，实时 Linux 隔离 jitter，FPGA 负责精细 I/O 时序，multirate 避免慢动态无谓重复计算。[pdf:E03][pdf:E04][pdf:E05]（PDF 物理页 3–5）

更深一层的 intuition 是：并行只有在模型存在可用的计算独立性、且节省的计算时间大于通信与同步成本时才有价值。论文自己的两节点结果正好说明了这一限制。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Section V-G）

## § 5 — 具体方法与完整 Pipeline

以论文的三电平 12-pulse vector-controlled AC drive 为例，完整 pipeline 如下。

1. **建立对象模型。** 电源、串联滤波器、三绕组变压器、双三相二极管整流桥和 DC filter 组成线性 state-space 部分；三电平 12-pulse IGBT converter 用 switching-function 的 time-stamped bridge 表示；squirrel-cage induction motor（SCIM）使用五阶 Park 模型。[pdf:E05][pdf:E06]（PDF 物理页 5–6，Fig. 6、Fig. 7）
2. **压缩每步计算。** 作者合并串联滤波电感与变压器一次侧电感，并把二、三次绕组电感折算到一次侧，从原 state-space 模型减少 4 个状态；同时移除双整流桥的 snubber，并缩小主模型的输入、输出向量。[pdf:E06]（PDF 物理页 6，Section V-C）
3. **按动态速度选积分。** 慢速 induction machine 用 forward Euler，系统其余部分用 fourth-order Runge–Kutta。作者的理由是小步长可以减轻 Euler 误差，且 Euler 避免在 SIMULINK 中形成 algebraic loop。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Section V-C）
4. **生成控制信号。** 测得的三相定子电流经 Clarke/Park 变换进入同步旋转 \(dq\) 坐标；速度 PI 产生 torque reference，磁链与转矩回路生成 \(i_d^\ast,i_q^\ast\)，再逆变换成三相电压 reference，与 carrier 比较生成 12 路 PWM gate signal。[pdf:E07]（PDF 物理页 7，Fig. 8 与 Section V-D）
5. **安排实时执行。** 单节点时，一步依次经历 I/O、compute、acquisition 和等待同步。两节点时，线性电路在 master，machine、converter 和 controller 在 slave；二者交换上一个时间步产生的数据，console 在 host 上监控与调参。[pdf:E05][pdf:E07]（PDF 物理页 5、7，Fig. 5、Section V-E）
6. **同步与外部接口。** 没有硬件 I/O 时可由 RTOS/CPU clock 同步；接入模拟或数字 I/O 时由 FPGA hardware timer 触发。FPGA 的 100 MHz 时钟提供 10 ns I/O resolution，并与 real-time interpolation 配合处理步内开关事件。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Sections II-C、IV）
7. **输出与核对。** 实时波形可经 FPGA I/O 接到 oscilloscope，也可送到 host；论文用 PSCAD/EMTDC 的离线仿真作为数值参照，并记录 steady-state、transient、harmonic 与每步 execution time。[pdf:E07][pdf:E08][pdf:E09]（PDF 物理页 7–9，Section V-F）

论文没有把核心电磁求解映射到 FPGA；FPGA 在这套系统中承担的是 I/O、事件捕获和硬件同步。也没有报告 fixed-point 数值格式；计算节点是通用 Xeon CPU，证据只支持 CPU 上的软件求解。[pdf:E02][pdf:E03][pdf:E06]（PDF 物理页 2–3、6，hardware architecture、FPGA I/O 与 case model）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有提出新的数值分析理论，但给出了构成实时模型的两个数学层次。

线性电路写成标准连续时间 state-space：
\[
\dot{\mathbf{x}}=\mathbf{A}\mathbf{x}+\mathbf{B}\mathbf{u},\qquad
\mathbf{y}=\mathbf{C}\mathbf{x}+\mathbf{D}\mathbf{u}.
\]
案例中 \(\mathbf{x}\in\mathbb{R}^{6}\)、\(\mathbf{u}\in\mathbb{R}^{17}\)、\(\mathbf{y}\in\mathbb{R}^{14}\)；六个状态由 DC-link 两个电感电流、两个电容电压和变压器两个相关电感电流组成。[pdf:E06]（PDF 物理页 6，Eq. (1)–(2)）

物理上，\(\mathbf{A}\) 描述不施加新输入时储能状态怎样自行演化，\(\mathbf{B}\) 把电源与非线性反馈注入状态，\(\mathbf{C},\mathbf{D}\) 把内部状态和直接通道映射为输出。Fig. 7(b) 中的稀疏性意味着并非每个状态都强耦合；减少状态和接口维度会直接减少每步矩阵运算，但这并不自动保证跨节点可并行，因为通信依赖由 subsystem 边界而不是仅由矩阵大小决定。[pdf:E06]（PDF 物理页 6，Fig. 7）

vector control 使用
\[
T_e^\ast=i_q^\ast\psi_r^\ast\frac{3}{2}\frac{P}{2}\frac{L_m}{L_r},
\qquad
\psi_r^\ast=L_m i_d^\ast,
\]
其中 \(L_m\) 是 mutual inductance，\(L_r\) 是 rotor inductance，\(P\) 是 pole pairs 数。第一式说明在 rotor flux reference 固定后，quadrature-axis current \(i_q^\ast\) 直接调节 torque；第二式说明 direct-axis current \(i_d^\ast\) 用来设定 rotor flux。这种解耦使速度环与磁链环可以分别由 PI controller 形成 reference。[pdf:E07]（PDF 物理页 7，Eq. (3)–(4)、Fig. 8）

真正决定实时性的“数学”是 deadline inequality：每步所有阶段的最坏耗时必须小于 \(h\)。论文报告的 10 μs 不是积分法推导出的稳定上限，而是模型、I/O、软件调度和硬件共同达到的执行预算；不能把它外推成任意系统都能使用的固定步长。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Section V-G、Table II）

## § 7 — 实验设计与结论

**问题 1：该实时模型能否复现离线参照的 steady-state 电压、电流与 harmonic？**  
实验：在 10 μs step、2.5 kHz PWM carrier 下运行三电平 12-pulse drive，并与 PSCAD/EMTDC 比较。实时结果的 \(V_{ab}\) RMS 为 436 V，离线为 439 V；\(I_a\) RMS 为 42.30 A，离线为 43.95 A；两者 fundamental frequency 都是 53 Hz。Table I 还报告了 peak-to-peak、THD 和 V/Hz ratio。[pdf:E07][pdf:E08][pdf:E09]（PDF 物理页 7–9，Fig. 9–11、Table I）  
答案：在这组 operating point 和共享参数下，论文展示了接近的 steady-state 数值与 harmonic 位置。它没有证明对所有开关工况或所有模型误差都准确。

**问题 2：动态 reference 改变时，实时响应是否接近离线参照？**  
实验：在 10 s 改变 torque reference，观察 torque 与 current；另保持 140 N·m torque reference，把 speed reference 从 120 rad/s 改到 160 rad/s。实时与离线波形均显示相近的过渡；Table I 给出的 speed 变化均为 40 rad/s，因 speed step 引起的最大 \(I_a\) 分别为 100.0 A 和 101.3 A。[pdf:E08][pdf:E09]（PDF 物理页 8–9，Fig. 12–15、Table I）  
答案：选定的两个 reference step 下，实时与离线响应接近。这里的 baseline 是另一个仿真器，不是电机实验台测量，因此只能验证实现之间的一致性，不能单独证明物理模型完备。

**问题 3：单节点是否满足 10 μs realtime deadline？**  
实验：分解一步的 execution time。Table II 报告 computation 5.347666667 μs、data acquisition 1.0 μs、idle 2.492333333 μs，总 step-size 为 10 μs；作者称动态 I/O parameter 改变时进一步缩短步长会发生 overrun。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Section V-G、Table II）  
答案：该模型在一台 target node 上以 10 μs 步长运行且无 overrun；论文没有给出长时间 deadline-miss 分布或极端 I/O 负载压力测试。

**问题 4：拆成两节点能否进一步缩短步长？**  
实验：master/slave 并行。各自最大 computation time 降至 2.46 μs 与 3.51 μs；但约 4 μs communication overhead 抵消收益，assigned step-size 反而变成 12 μs。开启 hyper-threading 后两者最大 computation time 为 1.91 μs 与 3.47 μs。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Section V-G）  
答案：计算阶段得到并行加速，端到端实时步长没有改善。这是论文对自身“scalable”主张最重要的限定。

## § 8 — Take-aways

**5 句话：** 这篇论文把 COTS Xeon cluster、实时 Linux、FPGA I/O、SIMULINK 工作流与多速率调度组合成一个电力工程实时仿真平台。[pdf:E01][pdf:E02][pdf:E03][pdf:E04] 它用三电平 12-pulse vector-controlled AC drive 展示了 10 μs 步长和 5.35 μs 最大计算时间。[pdf:E09][pdf:E10] 实时结果在选定 steady-state 与 transient 工况下接近 PSCAD/EMTDC。[pdf:E08][pdf:E09] 模型优化依赖减少状态、压缩接口、对快慢动态选不同积分器，以及对开关事件做 time-stamp。[pdf:E05][pdf:E06] 最重要的反面结果是：两节点虽然算得更快，通信却把整体步长推到 12 μs，说明 cluster 扩展性必须以计算/通信比和耦合结构为条件。[pdf:E09][pdf:E10]

**3 句话：** 实时性能来自端到端 deadline engineering，而不是某一个求解器或某一块 FPGA。该案例证明一套 COTS 平台能以 10 μs 运行复杂 drive model，并与离线仿真取得接近结果。它同时证明“更多节点”不保证“更小步长”，通信与同步必须进入真实性能模型。

**1 句话：** 论文最持久的贡献，是把电力实时仿真的核心从峰值算力改写为“模型分解、最坏时延、I/O 时序和数值误差必须共同闭合”。

## § 9 — 最脆弱的假设

最脆弱的假设是：随着模型增大，能够找到一种 subsystem partition，使各节点的并行计算收益大于跨节点通信、同步和因一步延迟交换产生的数值代价。若这个假设不成立，cluster 的节点数虽可增加，实时可处理模型的规模或最小步长却不会随之改善；论文“flexible and scalable”的核心工程价值会被削弱。

论文给出的支持主要是架构论证：Fig. 5 明确了 master/slave 流水，multirate 允许慢动态少算，作者也指出只有大型模型才可能摊薄 inter-node latency。[pdf:E05]（PDF 物理页 5，Sections IV-A、IV-C）但唯一量化的两节点结果恰好没有实现端到端加速：计算时间下降后，约 4 μs 通信开销仍让步长从 10 μs 增至 12 μs。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Section V-G）

缺失的证据包括：随节点数和模型规模变化的 scaling curve、不同 partition 的 dependency graph、通信 payload、deadline-miss tail、一步延迟边界交换造成的误差，以及高 I/O 负载下的最坏时延。因此，“大型复杂系统的收益明显”在本文中仍是作者判断，不是被案例数据闭合的结论。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重建整套 2006 年硬件，而是复现“并行何时改善端到端 realtime step”这一机制。

1. 用一个小型 switched-converter + RL/DC-link + induction-machine surrogate，保留线性 state-space、开关函数和慢速 machine state；离线用 1 μs 或更小步长生成 reference。
2. 在同一台现代多核实时 Linux 主机上先做单 worker，然后做 master/slave 两 worker；再把两 worker 放到两台机器上。实现 Fig. 5 的上一步边界量交换，固定 10 μs deadline。
3. 逐级增加每个 subsystem 的独立计算负载和交换向量维度，记录每步 compute、communication、synchronization、total latency、overrun count，以及相对离线 reference 的电压、电流误差。
4. 每个工况连续运行至少 \(10^7\) 步，并报告 maximum 与高分位 latency，不能只报平均值。
5. **支持 claim 的标准：** 存在明确的模型规模区间，使两节点 total worst-case step 小于单节点，同时误差不因边界延迟显著增大。**反驳 claim 的标准：** 在可现实达到的模型与网络条件下，所有 partition 都因通信、同步或耦合误差而不能优于单节点。

这个实验不会复现论文的全部 drive 波形，但能以最小成本直接检验第 9 节最脆弱的 scaling 假设。

## § 11 — 最强反例设计

最强反例是一类“计算很多、但电气耦合更强”的系统：多个 grid-forming converter 通过低阻抗网络紧密连接，并在同一时间窗内触发 current limit、PWM edge 和 protection logic。把每个 converter 分到不同节点后，若沿用论文的上一步数据交换，则每个节点看到的是过期端口量；若改成同一步迭代或 barrier，又可能破坏 10 μs deadline。

实验应比较三种方案：单节点 monolithic reference、上一步交换的两/四节点方案、同一步迭代收敛的两/四节点方案。攻击指标不是平均加速比，而是故障瞬间的能量不平衡、false trip、current peak error、deadline miss 和数值稳定性。若上一步交换产生不可接受的相位/能量误差，而迭代交换又持续超时，就得到一个可预测的失败条件：强耦合系统不能同时满足并行独立性、数值忠实性和实时 deadline。

该反例比“换一个更大模型”更强，因为它直接否定“模型越大越适合切分”的朴素外推：规模增加可能同时增加跨分区耦合，使额外算力无法转化为可信实时能力。这是基于论文分区机制与通信结果的推断，不是论文已完成的实验。[pdf:E05][pdf:E09][pdf:E10]

## § 12 — Follow-up Research Idea

电力实时仿真领域通常把高影响工作建立在三项同时成立之上：数值/物理可信、最坏时延可证、真实硬件闭环可运行。基于本文最脆弱的 scaling 假设，一个非增量的候选方向是把研究目标从“可增加多少节点”改成“能否自动合成一份同时满足误差预算与 deadline 预算的分布式仿真契约”。这里不声称 novelty，相关工作还需要对现代 RTDS、FPGA solver、distributed HIL、parallel discrete-event simulation 和 passivity-based co-simulation 做系统检索。

**(a) 未满足的需求。** 现有 partition 主要围绕计算负载，但强耦合电力电子系统还需要控制边界延迟带来的能量误差；只优化 load balance 可能得到更快但不可信的仿真。

**(b) 研究价值。** 若能在运行前证明“这个 partition 在给定网络与 I/O 下既不会 overrun，也不会超过端口能量误差”，cluster scaling 才从经验调参变成可审计工程能力。这比单纯增加节点或更换网卡改变了问题定义。

**(c) 可借鉴方法。** 从 real-time distributed systems 借 worst-case execution/communication analysis，从 networked control 借 delay robustness，从 passivity-based co-simulation 借端口能量约束，从 graph partitioning 借 dependency-aware cut；FPGA time-stamp 则继续承担亚步长事件观测。[pdf:E03][pdf:E05]

**(d) 第一个证伪实验。** 在第 11 节的多 converter 强耦合系统上，给定 10 μs deadline 和预先规定的端口能量误差上限，尝试自动生成两节点与四节点 partition。若算法声称可行但实测发生 deadline miss 或误差越界，或在一组具有现实意义的拓扑中始终找不到可行解，这个研究假设就被证伪。

**(e) 与本文的实质区别。** 本文先由工程师划分 master/slave，再测通信是否抵消收益；候选工作把“是否可划分”变成带数值忠实性与最坏时延双约束的核心求解对象。它不再把 scalability 定义为硬件可加节点，而定义为在可验证契约下可扩展的可信实时仿真。
