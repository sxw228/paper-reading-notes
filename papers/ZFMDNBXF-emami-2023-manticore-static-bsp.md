# Manticore：用 Static Bulk-Synchronous Parallelism 加速 RTL 仿真

- 作者：Mahyar Emami、Sahand Kashani、Keisuke Kamahori、Mohammad Sepehr Pourghannad、Ritik Raj、James R. Larus
- 出处：ASPLOS 2023
- 年份：2023
- DOI：10.1145/3623278.3624750
- Zotero key：ZFMDNBXF

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的问题是：RTL 电路天然含有大量门级和寄存器级并行，为什么主流多核 CPU 上的 cycle-accurate 仿真仍常常不能靠加核提速，以及能否设计一种专用并行机，把这些细粒度任务真正并行起来。作者给出的背景数字是，最快的软件 RTL 模拟器通常只有 1–1000 kHz，比硬件慢三个数量级以上；这种差距直接拖慢设计迭代、长时间软件负载和大规模验证。[pdf:E01](_evidence/E01-p001-abstract-core-claim.png)

关键矛盾不在“有没有并行任务”，而在每个任务太短。RTL 在一个时钟边沿之间只有有限组合逻辑，切成多核任务后，通信、依赖唤醒和 barrier 的固定成本会迅速压过有效计算。论文把单时钟 netlist 拆成 current/next register value 构成的 DAG；一次 RTL cycle 就是沿 DAG 计算所有 next value，再整体提交为下一轮 current value。[pdf:E02](_evidence/E02-p002-rtl-dag-contributions.png) 因而，正确性天然要求一个全局时序边界，而性能取决于这个边界能否从运行时协调变成编译期事实。

工程价值是缩短 time-to-result，而不是取代所有验证工具。Manticore 试图占据“软件仿真编译快但运行慢”和“FPGA prototype 运行快但编译数小时至数天”之间的位置：把 RTL 编译成专用处理器阵列上的软件，在分钟级编译后获得长仿真的吞吐收益。[pdf:E13](_evidence/E13-p012-limitations-related-work.png)

## § 2 — 前人工作与不足

论文比较的主基线是 Verilator。它也是 full-cycle、cycle-accurate 模拟器，把 RTL 编译成 C++；其并行模式先把 DAG 聚合为 macro-task，再静态分给线程池，但运行时仍用 atomic fetch-and-add 协调任务，并在时钟边沿用 barrier 汇合。论文的测量显示，EPYC 上各 benchmark 大约到 8 个线程便达到可扩展性极限，小任务甚至因同步成本而变慢。[pdf:E08](_evidence/E08-p008-verilator-benchmarks.png) [pdf:E09](_evidence/E09-p009-performance-table.png)

已有路线各自解决了不同问题。event-driven GPU 模拟器通过跳过不活跃事件来降低工作量；RTLFlow 利用 many-stimulus 的批并行；FPGA prototype 直接把 RTL 映射为门；商业 emulation platform 则把 RTL 指令化并运行在大型处理器阵列上。它们分别受制于活动率、单 stimulus 性能、编译与调试成本或昂贵硬件，不能直接回答“单个 full-cycle RTL 仿真如何稳定利用数百个细粒度核”。论文也明确指出，Manticore 与 event-driven 系统并非同类比较，而与 FPGA prototype 的根本区别是它在 FPGA 上运行仿真程序，并不把被测 RTL 直接综合到 FPGA fabric。[pdf:E13](_evidence/E13-p012-limitations-related-work.png)

Manticore 延续了 Valiant BSP、Raw/VLIW 机器和确定性加速器的思路，但把适用条件收紧到 RTL：控制流通常没有长时间 divergence，电路依赖图在编译期可见，故编译器有机会同时安排计算、NoC 路由和同步。[pdf:E03](_evidence/E03-p003-static-bsp-key-ideas.png) 论文真正改变的假设不是“多核更快”，而是“细粒度并行必须在运行时动态协调”。

## § 3 — 重建作者的思考路径

下面是基于论文背景与实验组织重建的思考路径，不是作者逐字陈述。

第一步，从 RTL 语义出发：单时钟 full-cycle 仿真可以化为重复求值一个无环依赖图，独立路径确有并行性；但每轮结束必须让所有 next-state 同时成为 current-state。第二步，在 CPU 上测量理想化 workload：即使忽略跨核数据搬运，只保留每 RTL cycle 两次 barrier，计算粒度越小，强扩展越早转负；加入 instruction-cache 压力后，现象更严重。[pdf:E07](_evidence/E07-p007-barrier-scaling-model.png)

第三步，把 barrier 看成“已知最迟到达时间”，而不是运行时协议。若每条指令、每条消息路径和每个存储访问的延迟都可预测，编译器便能在快核末尾填 NOp/sleep，使所有核在一个共同的 Vcycle 长度上对齐。第四步，为了让这件事成立，硬件必须主动放弃会引入时序不确定性的机制：无动态调度、无 shared-memory coherence、无分支预测、无 NoC buffer arbitration；所有核只访问本地固定延迟状态，罕见的 DRAM 或 host exception 则冻结整个 compute clock domain。[pdf:E03](_evidence/E03-p003-static-bsp-key-ideas.png) [pdf:E04](_evidence/E04-p004-core-noc-architecture.png)

第五步，真正的性能问题转移到编译器：怎样切 DAG，既让最慢核短，又不让 Send 消息把 buffer-less NoC 塞爆。于是作者用通信感知的 split/merge heuristic 做负载均衡，再用 cycle-accurate list scheduling 同时消除 pipeline hazard 和 link collision。[pdf:E05](_evidence/E05-p005-compiler-partitioning.png) [pdf:E06](_evidence/E06-p006-custom-schedule-routing.png)

## § 4 — 核心 Intuition

Static BSP 的核心是把每个 virtual cycle 的 barrier 从“运行时大家到齐后再放行”改成“编译器事先算出统一结束时刻，短路径原地等待”。这只有在执行核、存储和片上网络都给出确定性延迟时才成立；作为交换，Manticore 消除了细粒度同步和路由仲裁的运行时开销。最终性能由最长分区的 scheduled length 决定，所以负载均衡与通信拥塞其实是在最小化同一个量：virtual critical-path length（VCPL）。

## § 5 — 具体方法与完整 Pipeline

以论文中的单时钟 RTL 输入为例，完整路径如下。

1. **建立语义 DAG。** Yosys frontend 解析 Verilog，把寄存器拆成 current/next value，使组合逻辑依赖成为 DAG。一个 Vcycle 消耗所有 current state，产出所有 next state；论文当前只处理 single-clock、full-cycle、cycle-accurate 语义。[pdf:E02](_evidence/E02-p002-rtl-dag-contributions.png)
2. **Lowering 与普通优化。** backend 把任意位宽的 netlist assembly 降到 16-bit datapath 指令，执行 dead-code elimination、constant folding 和 common sub-expression elimination。控制分支改为 predication，并执行所有路径，以换取固定执行时间。[pdf:E03](_evidence/E03-p003-static-bsp-key-ideas.png) [pdf:E05](_evidence/E05-p005-compiler-partitioning.png)
3. **最大化切分。** 对每个 sink 反向遍历，形成产出一个 next value 的细小 process；访问同一 memory region 的指令保持同分区，privileged instruction 也集中在同一 process，避免每 Vcycle 搬运大块状态。切分允许复制 DAG 节点，用更多计算换取并行。[pdf:E05](_evidence/E05-p005-compiler-partitioning.png)
4. **通信感知合并与负载均衡。** 从执行时间最短的 process 开始，优先与有通信边的邻居合并，目标是减少 Send 同时避免形成 straggler。合并后仍可继续优化，因为少一次跨核值传递或消除重复表达式，可能让总执行时间下降。[pdf:E06](_evidence/E06-p006-custom-schedule-routing.png)
5. **定制逻辑指令。** 每个分区抽取最多 4 输入的 bitwise MFFC，用 logic-equivalence 分组，再用 MILP 选择互不重叠、节省指令最多的一组，映射为每核最多 32 个 programmable custom functions。[pdf:E06](_evidence/E06-p006-custom-schedule-routing.png)
6. **联合调度计算与通信。** 编译器对一整个 Vcycle 做 abstract cycle-accurate simulation。普通指令只有在 predecessor 完成后才能发射；Send 只有在沿 dimension-ordered torus 的每条 link 都不会与其他消息冲突时才能发射，否则插 NOp。大 register file 让 linear-scan allocation 几乎不 spill。[pdf:E04](_evidence/E04-p004-core-noc-architecture.png) [pdf:E06](_evidence/E06-p006-custom-schedule-routing.png)
7. **执行与周期提交。** Send 在计算中途发起，但目的核直到 Vcycle 末尾才从 instruction-memory-backed queue 接收并更新寄存器。所有核按编译期 sleep 长度同步回到下一轮起点；boot 时则用每核 countdown 抵消 DRAM 装载的非确定时延，保证同时开跑。[pdf:E04](_evidence/E04-p004-core-noc-architecture.png) [pdf:E15](_evidence/E15-p015-runtime-lockstep.png)
8. **处理不可预测事件。** 只有 privileged core 能访问 off-chip DRAM 或触发 host service。cache access 或 exception 会通过 clock gating 冻结全部 cores 与 NoC，处理完成后再恢复，以保存精确、lockstep 的 RTL 状态；代价是一次慢事件成为全机停顿。[pdf:E04](_evidence/E04-p004-core-noc-architecture.png) [pdf:E15](_evidence/E15-p015-runtime-lockstep.png)

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出定理或封闭形式的核心数学推导；关键量是编译器可精确计数的 VCPL。VCPL 定义为最慢 core 在一个 Vcycle 中执行的总 machine cycle 数，包括为了 pipeline hazard、消息接收和 NoC contention 插入的 NOp；在没有 off-chip access 时，它就是模拟一个 RTL cycle 所需的 FPGA cycles。[pdf:E09](_evidence/E09-p009-performance-table.png)

可以用一个非论文公式来解释其工程含义。若第 \(i\) 个分区的本地计算、Send 与等待分别为 \(C_i\)、\(S_i\)、\(N_i\)，则理想情况下每轮长度由 \(\max_i(C_i+S_i+N_i)\) 决定，而不是所有核的平均工作量。static barrier 只是把每个较短分区补到这个最大值；它消除了 runtime barrier 的协议成本，却没有消除“最慢者决定全局进度”的 BSP 结构。因此，partitioning 的目标不能只平衡 \(C_i\)，还必须压低跨核 Send 与因 link collision 产生的 \(N_i\)。

这也解释了作者的两个结果。通信感知分区相较 longest-processing-time-first，在九个 benchmark 中将 Send 数减少 28.0%–94.1%，除 vta 外均降低 VCPL；但 custom instruction 虽让非 NOp 指令数减少 2.9%–17.8%，端到端 VCPL 改善仍全部低于 10%，因为被缩短的可能不是 straggler 路径。[pdf:E11](_evidence/E11-p010-communication-aware-partitioning.png) [pdf:E12](_evidence/E12-p011-custom-compile-cost-limits.png)

## § 7 — 实验设计与结论

**问题一：CPU 的细粒度 parallel RTL simulation 为什么扩不起来？** 作者构造了保持总指令数不变、每 RTL cycle 执行两次 barrier 的强扩展模型，先只计同步，再完全展开循环加入 i-cache pressure。结果是，粒度越细，增加线程越早造成性能下降；这给出的是偏乐观上界，因为模型还忽略真实数据搬运。[pdf:E07](_evidence/E07-p007-barrier-scaling-model.png)

**问题二：专用确定性硬件是否真的快于 Verilator？** 作者在九个 RTL workload 上比较 Verilator v5.006 与 225-core、475 MHz 的 Alveo U200 原型；两边关闭 waveform dump 和多余打印并开最高优化，运行 1M 到 1B 个 RTL cycles 取得 steady state。Manticore 在 8/9 个 benchmark 上胜出；对 EPYC multithreaded Verilator 的 geometric-mean speedup 为 2.07×，对 Xeon 为 4.16×，但在含强顺序 Huffman lookup 的 jpeg 上只有 214.2 kHz，明显输给 EPYC 的 1239 kHz。[pdf:E09](_evidence/E09-p009-performance-table.png)

**问题三：数百核是否仍有扩展性？** 编译器用 VCPL 预测不含 off-chip access 的性能，Fig. 7 显示多数 workload 到 200–300 cores 仍有改善，但 jpeg 很早平台化；作者同时承认大量并行收益只是补偿 Manticore 单核相对 x86 的低频、窄 datapath 和低 IPC。[pdf:E09](_evidence/E09-p009-performance-table.png) [pdf:E10](_evidence/E10-p010-scaling-global-stall.png)

**问题四：off-chip state 会怎样？** 1×1、500 MHz 的 FIFO/RAM microbenchmark 分别测试 1 KiB、64 KiB、512 KiB 状态，每 Vcycle 做一次 load 和 store，共运行 16 Mi Vcycles。顺序 FIFO 因 locality 好，扩容后仍不主要受 stall 限制；伪随机 RAM 随 off-chip access 增多显著变慢，而且即使 cache hit，保守的全局 stall 仍有成本。[pdf:E10](_evidence/E10-p010-scaling-global-stall.png)

**问题五：编译器优化真正影响什么？** communication-aware partitioning 大幅减少 Send，并通常缩短 straggler 的 VCPL；custom function 对总指令数有中等收益，但对最长路径不足 10%。这说明系统首要矛盾是全局关键路径和通信，而不是单核位运算吞吐。[pdf:E11](_evidence/E11-p010-communication-aware-partitioning.png) [pdf:E12](_evidence/E12-p011-custom-compile-cost-limits.png)

不得外推之处是：benchmark 被刻意缩放到 state 可装入 scratchpad，以便编译器准确预测；系统只支持 single-clock、少量 SystemVerilog 和基础 system call，尚无经评估的 waveform debugging；原型最多约 900k instructions，且论文称其仍是 prototype，不是 Verilator replacement。[pdf:E09](_evidence/E09-p009-performance-table.png) [pdf:E13](_evidence/E13-p012-limitations-related-work.png)

## § 8 — Take-aways

**5 句话。** 第一，RTL 的 DAG 并行性本身不稀缺，稀缺的是低成本、可预测的同步和通信。第二，Manticore 用确定性核、buffer-less torus NoC、fixed-latency local memory 与 branch-free execution，把 runtime barrier 改成 compile-time schedule。第三，编译器通过通信感知分区、straggler balancing 和 cycle-exact routing，把一个 RTL cycle 变成固定长度 Vcycle。第四，225-core、475 MHz 原型在九个 benchmark 的八个上超过 Verilator，但 serial dependency、off-chip random access 和有限片上 SRAM 会迅速侵蚀优势。第五，对系统设计最重要的经验是：当所有参与者必须 lockstep 时，平均负载没有意义，尾部最长路径才是吞吐与 deadline 的决定量。

**3 句话。** Static BSP 并没有消除 barrier，而是把 barrier 的发现时间从运行时提前到编译期。这个交换只有在执行与通信延迟可静态界定、rare event 可以全局冻结时才可靠。Manticore 的实验表明，优化跨核通信和 straggler 比继续堆单核指令优化更重要。

**1 句话。** Manticore 用“可预测性换动态性”，让编译器而非运行时负责数百核 RTL 仿真的同步、路由与最慢核。

## § 9 — 最脆弱的假设

最脆弱的假设是：**一个 Vcycle 内的计算与通信时延能够在编译期给出紧且稳定的上界，罕见的不可预测事件可以通过全局冻结隔离。** 这比“RTL 有并行性”更关键；一旦某个核、link、memory access 或 host service 的完成时刻不可预测，预插入 sleep 就不再等价于 barrier，可能出现下一轮过早开始而破坏语义，或只能按最坏情况留出巨大空洞。

论文为该假设提供的证据是受控原型中的 deterministic pipeline、静态路由、fixed-latency local state，以及无 off-chip access 时 VCPL 与真实 cycle count 一致；它还通过 global clock gating 把 cache 和 exception 的不确定性变成全机 stall。[pdf:E03](_evidence/E03-p003-static-bsp-key-ideas.png) [pdf:E04](_evidence/E04-p004-core-noc-architecture.png) 但证据缺口同样明确：benchmark state 被安排进 scratchpad；随机大 RAM 已显示全局停顿代价；多 clock、timing control、复杂 testbench、DPI 和 waveform collection 尚未闭合。[pdf:E10](_evidence/E10-p010-scaling-global-stall.png) [pdf:E13](_evidence/E13-p012-limitations-related-work.png)

**对多卡 EMT 的迁移判断。** 可迁移的是“预先生成通信表、固定 packet route、按最长 stage 做静态 slotting、把所有跨卡状态更新放在 step boundary 提交”的架构思想。根本差异是，Manticore 的 NoC 与核在同一 FPGA compute clock domain，可用 clock gating 真正冻结；多卡 EMT 穿过 SerDes、交换芯片、PCIe 或 Ethernet，链路有 arbitration、retransmission、clock drift、温度降频和软件干扰，无法自然提供 cycle-exact latency。EMT 还有 solver iteration、开关事件和数值收敛导致的数据相关工作量，而论文的 full-cycle RTL 执行路径被 predication 固定。因此，多卡系统若照搬 static sleep，确定性 deadline 不是“平均能赶上”，而必须证明每个 timestep 的 worst-case completion 加同步裕量不超过实时步长。

barrier 尾延迟在这里是首要风险：一次 step 的完成时间等于所有卡中最慢者，卡数增加会放大极端尾部；即使单卡平均时延不变，最大值分布仍会右移。Manticore 通过硬件确定性把这个尾部压成编译期常数，而多卡 EMT 通常只能做 deadline-aware admission、bounded-latency transport、冗余执行或局部异步边界，不能假定尾部自动消失。这是基于论文机制的迁移推断，不是论文已验证的结论。

## § 10 — 最小复现实验

一周内不必复刻 225-core FPGA，可验证最核心的“static schedule 是否比 runtime barrier 更适合细粒度确定性 workload”。

选一个可生成的 single-clock RTL DAG workload：每轮 50k–200k 个简单 16-bit operation，固定依赖图，并可控制跨分区 edge density 和负载偏斜。实现两个执行器：A 用 8–32 个 CPU thread、runtime barrier 与 queue；B 离线把 DAG 分区、生成固定 per-worker instruction/Send schedule，并以预定 slot 执行，不做运行时 ready checking。两者必须逐 cycle 比对 register state，确保语义完全一致。

测量每 RTL cycle 的 median、p99、p99.9 和 maximum latency，另记 barrier time、message count、最慢分区长度与空等比例。先在 pinned core、内存预热、无系统干扰下运行，再注入 0.1% 的单 worker 随机 5–50 μs pause。若 B 在无扰动时显著降低 p99 latency 且输出一致，支持“静态协调能消除细粒度 runtime overhead”；若有微小扰动便出现错误或必须按最坏暂停填充到失去优势，则反驳其对非确定平台的可迁移性。

再加一个 EMT 映射的小实验：把 4 个固定导纳子网的 Norton history current 更新分到 4 个进程，每个 timestep 在边界交换端口量。比较 static time-triggered slots 与 runtime barrier，deadline 设为 50 μs。支持迁移的标准不是平均更快，而是连续至少 \(10^7\) steps 零 deadline miss，并且 p99.999 留有明确裕量；这部分是候选验证设计，不是论文复现结果。

## § 11 — 最强反例设计

最强反例不是再找一个“并行度较小”的 jpeg，而是构造**平均负载高度平衡、但每轮出现稀有且不可预测长尾**的正确 RTL/仿真 workload。具体做法是：32 个分区平时执行等长本地逻辑，每 10,000–100,000 cycles 中随机一轮由数据触发 privileged global memory access 或 host exception；同时让多个分区通过同一组 NoC cut links 发送消息。控制平均额外工作低于 1%，使 average throughput 看似理想，但测量每轮 completion tail、全局冻结占比和静态 NOp 裕量。

这个反例会区分两种解释。若 Manticore 的收益来自真正消除了同步成本，那么稀有事件之外的 cycle 应保持稳定；若收益依赖 benchmark 将不确定 state 排除在 scratchpad 外，那么很低频的 global stall 也会让 p99.99/max latency 和总 time-to-result 急剧恶化。论文的 RAM microbenchmark已证明 cache hit 本身也会触发保守 stall，limitations 又承认 event control、复杂 DPI 与 waveform 尚不支持，因此该攻击直指假设边界，而非无关功能缺失。[pdf:E10](_evidence/E10-p010-scaling-global-stall.png) [pdf:E13](_evidence/E13-p012-limitations-related-work.png)

对多卡 EMT，进一步把随机暂停换成真实链路抖动与一次 solver non-convergence。若为了零 deadline miss 必须把每步 barrier budget 提高到最坏卡时延，导致可支持模型规模低于普通动态 barrier；或若任一卡慢一次就让所有卡错过实时步长，则 static BSP 的“无 runtime overhead”不能转化为 hard real-time 收益。这里挑战的是确定性 deadline，而不只是平均仿真速率。

## § 12 — Follow-up Research Idea

**候选方向：把 static BSP 从“固定完成时刻”改造成“可证明 deadline 的分层时间触发 EMT 执行模型”。不声称 novelty；尚未对 real-time co-simulation、time-triggered network、PDES 与多 FPGA EMT 的相关工作做充分检索。**

（a）未满足需求是：多卡 EMT 需要在几十微秒级步长内完成求解与跨卡端口交换，但真实链路和事件负载具有长尾；完全动态 barrier 难以给 hard deadline，完全静态 sleep 又会被最坏情况拖垮。

（b）潜在研究价值不在“把 Manticore 用到 EMT”，而在给出一个可验收的实时语义：每个 partition 有离线计算预算和通信 slot，正常 step 走无仲裁的 fast path；开关事件、solver iteration 或链路抖动触发有界 recovery epoch。系统必须同时证明数值结果与集中式 reference 的误差边界、零 deadline miss 的运行区间，以及失效时的 fail-safe 行为。

（c）可借鉴的相邻工具是 time-triggered Ethernet/TSN 的 gate control list、real-time scheduling 的 response-time analysis、PDES 的 conservative lookahead，以及 Manticore 的 communication-aware partitioning 与 VCPL 概念。需要把 VCPL 改写成 worst-case step response：本地 solver WCET、序列化、链路 worst-case delay、clock skew、recovery budget 和最大 straggler，而不是平均指令数。

（d）第一个证伪实验是 4 卡 EMT 原型上运行包含高频开关事件、参数不平衡和链路 burst jitter 的网络，目标步长 50 μs，持续 \(10^8\) steps。若任何合法工况需要无界 recovery，或为了零 miss 配置的静态裕量使可模拟规模/精度不优于单卡或普通 barrier，方向即被证伪。

（e）它与 Manticore 的实质区别是：Manticore在一个可统一冻结的确定性 FPGA clock domain 内用 compile-time sleep 取代 runtime barrier，并以吞吐为主要指标；候选系统面对不能统一停钟的多卡物理网络，研究目标是带异常包络的 deadline guarantee。论文结论证明了确定性硬件与静态调度能释放细粒度 RTL 并行，但没有证明跨设备 jitter 下的 hard real-time 性质。[pdf:E14](_evidence/E14-p013-conclusion.png)
