# FireAxe：面向大规模 RTL 设计的分区式 FPGA 加速仿真

作者：Joonho Whangbo、Edwin Lim、Chengyi Lux Zhang、Kevin Anderson、Abraham Gonzalez、Raghav Gupta、Nivedha Krishnakumar、Sagar Karandikar、Borivoje Nikolić、Yakun Sophia Shao、Krste Asanović  
出处：2024 ACM/IEEE 51st Annual International Symposium on Computer Architecture（ISCA 2024）  
DOI：10.1109/ISCA59077.2024.00044  
Zotero key：9E2J63DH

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

FireAxe 要解决的不是“怎样让一块 FPGA 上的 RTL 仿真再快一点”，而是一个更先验的容量问题：当待验证的单体 RTL 已经放不进一块 FPGA 时，怎样把它可靠地拆到多块 FPGA 上，同时仍保留足够高的速度、确定性和 RTL 级 fidelity，使完整软件栈和系统级 workload 仍然跑得动。论文把这个问题放在 pre-silicon validation 的语境中：单独评估一个模块不能捕获它与其他硬件、操作系统和应用的交互；抽象 simulator 虽灵活，却需要另行验证模型，而单 FPGA 的 FireSim 又受器件容量上限约束。FireAxe 的核心主张是用 FireRipper 对用户指定的边界做自动 RTL partitioning，并在 exact-mode 与 fast-mode 之间显式交换 fidelity 和吞吐率。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这项工作的价值首先是让“规模增长”不再立即等同于“换更大的一块 FPGA”。论文展示了三种以前很难在学术环境中完成的任务：把 24 个 OoO core 的 SoC 放到 5 块 datacenter FPGA 上、把单卡放不下的大型 OoO core 拆到两卡、以及运行足够长的 full-stack workload 来观察 RTL bug、leaky-DMA 和 Go garbage collection 的系统效应。[pdf:E01]（PDF 物理页 1，Abstract）但更重要的工程结论是：容量扩展并非免费。增加 FPGA 会引入跨卡 token 传输、同步等待、序列化和边界语义问题；因此“能拆开”只是第一道门，真正决定系统是否有用的是边界宽度、每个 target cycle 需要跨链路的次数、bitstream 频率和互连延迟。

论文事实与本文判断需要分开。论文证明的是若干具体设计和平台上的可行性与性能；“FireAxe 已解决任意规模 RTL 的一般扩展问题”并不是论文给出的结论。后文会把这种外推风险集中到第 9 和第 11 节。

## § 2 — 前人工作与不足

FireAxe 直接建立在 FireSim、Golden Gate、FAME 和 LI-BDN 之上。FireSim 能把 RTL 转成 FPGA 上的 cycle-exact simulator，并达到几十到几百 MHz，但其 monolithic target 必须放进单块 FPGA；Golden Gate 的 FAME-1 transformation 用 latency-insensitive bounded dataflow network（LI-BDN）把 target clock 与 host FPGA clock 解耦，使 target 只有在输入 token 齐备且输出可以推进时才前进一步。[pdf:E02]（PDF 物理页 2，Section II-A/II-B 与 Fig. 1）

已有 multi-FPGA 工具有三类不足。第一，ProtoCompiler、Palladium PPC 等工业工具能够做多 FPGA partitioning，但成本和封闭性使它们不适合学术研究、startup 或早期 co-design；IBM 的 LI-BDN multi-FPGA simulator 依赖定制平台且没有开放。第二，SMAPPIC 虽能跨 FPGA，却不做 target/host clock decoupling，因而不能提供同等的确定性和性能验证能力，且 partition point 限于 tile boundary；MEG 仍是单 FPGA，也不会自动把一般 ASIC RTL 变成 FPGA simulator。第三，RepCut、Manticore 等工作主要从 software RTL simulation 或定制 simulation ASIC 中提取 fine-grained parallelism，优化目标不是突破 commodity FPGA 的资源容量。[pdf:E12]（PDF 物理页 12，Section VII）

因此，FireAxe 改变的不是“partitioning 从无到有”，而是把四件以往分散的能力接起来：commodity/cloud FPGA、RTL source-of-truth、host-clock decoupling、以及编译器驱动的用户指导分区。它仍然保留用户选择边界和分配模块的责任，这一点非常关键：FireRipper 自动完成的是边界分析、层次结构改写和 simulator 生成，不是全自动找到全局最优 partition。

## § 3 — 重建作者的思考路径

如果不预设 FireAxe 的答案，可以从三个已知事实推到它的设计。

第一，直接在 FPGA 上跑 ASIC RTL 会把 FPGA 的物理时钟错当成 target 的逻辑时钟。例如论文用 1 GHz ASIC、100 ns DRAM 与 100 MHz FPGA 说明：未经 decoupling，原本应为 100 个 target cycle 的访问会变成 10 个 cycle，性能测量失真。LI-BDN 已经给出解决这一问题的基本机制：target 只有在 token 条件满足时推进。[pdf:E02]（PDF 物理页 2，Section II-A）

第二，如果把一个 LI-BDN 从中间切开，单卡内部原本“一次 host cycle 内完成”的组合依赖会变成跨卡消息依赖。把所有 I/O 粗暴地捆成一个 channel 会形成循环等待；因此 exact simulation 必须识别 source/sink port 的组合依赖并分开传 token。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Section III-A1）这一步自然导出第一个设计分叉：要么保留原 RTL，接受一个 target cycle 需要多次跨卡交换；要么只在 latency-insensitive boundary 上人为注入一拍并修改 ready-valid 边界，以减少同步次数。

第三，跨 FPGA latency 通常远大于一小段本地 combinational work。FAME-5 已知可以把 N 个重复模块的 combinational logic 共享、sequential state 复制，再由 hardware scheduler 逐个选择本 cycle 要更新的状态。若在一次跨卡等待期间轮流推进多个重复 tile，那么通信延迟可能被这些本地工作摊薄。[pdf:E03]（PDF 物理页 3，FAME-5 背景）这不是把 partition 动态迁移到另一块 FPGA，而是把固定放置后的重复实例做 simulator-level multithreading。

由此可重建出 FireAxe 的路线：保留 LI-BDN 的时间语义；让用户提供具有微架构意义的静态边界；编译器把边界变成可组合的多卡 simulator；再用 fast-mode 或 FAME-5 分别减少、摊薄同步成本。这个思考路径也预示了它的软肋：一旦找不到窄、规则、可解耦或高度重复的边界，容量收益会被通信和同步成本吃掉。

## § 4 — 核心 Intuition

FireAxe 的 intuition 是：不要把多 FPGA 看成一块更大的组合逻辑画布，而要把每个 partition 变成能靠 token 独立推进的 LI-BDN，再把跨 partition 的逻辑依赖显式化。exact-mode 用更多跨链路交换换取原 RTL 的 cycle-exact；fast-mode 在 latency-insensitive boundary 注入一拍并修正 backpressure，用局部语义变化换取接近两倍的速度。[pdf:E04]（PDF 物理页 4，Section III-A）

规模扩展能否成立，则取决于“释放的 FPGA 资源”是否大于“新增的边界宽度与同步代价”。重复模块较多时，FAME-5 可在一次通信间隔内轮流推进多个 instance，让更大设计的本地工作填满原本的跨卡等待；但它不是普遍的动态负载均衡。[pdf:E11]（PDF 物理页 11，Section VI-B 与 Fig. 14）

## § 5 — 具体方法与完整 Pipeline

以“把 ring-NoC SoC 中若干 core tile 拆到另一块 FPGA”为例，完整 pipeline 如下。

1. **输入与静态决策。** 输入是 FIRRTL 表示的 monolithic target RTL。用户选择 exact-mode 或 fast-mode，给出 FPGA 数量，并静态指定每个 partition 里的 module。默认模式需要逐一列出 module；NoC-partition-mode 则让用户给出 router node index，FireRipper 利用 credit-based、latency-insensitive 的 router boundary，沿层次结构自动收集与这些 router 相连的 protocol converter、CDC 和 tile。[pdf:E05]（PDF 物理页 5，Fig. 4 与 Section III-B）

2. **边界语义分析。** exact-mode 不改 target RTL。FireRipper 按 module hierarchy 做 topological ordering，再遍历 FIRRTL AST，找出 output 对 input 的 combinational dependency，把有依赖的 sink port 与无依赖的 source port 分开聚合成不同 LI-BDN channel。这样可以打破 token 的循环等待，但一个 target cycle 需要两次 token transfer；若输入输出间的组合依赖链长度大于 2，compiler 会终止并返回导致失败的 port chain。[pdf:E03]（PDF 物理页 3，Section III-A1）；[pdf:E04]（PDF 物理页 4，exact-mode 限制）

3. **fast-mode 边界改写。** fast-mode 在两侧 channel 预置 seed token，使两个 partition 能并行推进一个 cycle，然后再交换结果；代价是在 boundary 注入一个 target cycle latency。对 ready-valid interface，直接注入 latency 会破坏 backpressure，因此 FireRipper 在 sink 侧插入 skid buffer，并把 source 侧的 valid 改成 `valid & ready`，防止丢请求或重复发送。结果相对于修改后的 RTL 仍是 cycle-exact，但相对于原始 RTL 只应称 cycle-approximate。[pdf:E04]（PDF 物理页 4，Fig. 3）；[pdf:E05]（PDF 物理页 5，fast-mode transformation）

4. **层次结构改写与 partition 生成。** FireRipper 对选中的 module 执行 Reparent，把它们拉到 hierarchy 顶层并逐级打通 I/O；执行 Grouping，把属于同一 FPGA 的 module 包进 wrapper；执行 Extract 或 Remove，分别生成“只保留 wrapper 的 partition”和“删除 wrapper、保留其余设计的 partition”；最后把每个 partition 交给 Golden Gate 做 FAME-1，转换为 LI-BDN simulator。[pdf:E06]（PDF 物理页 6，Fig. 5 与 Section III-C）

5. **传输机制。** FireAxe 提供三条跨卡路径。host-managed PCIe 由每卡对应的 C++ driver 通过 512-bit PCIe DMA 拉取 token，再经 host shared memory 交给另一 driver，通用但最高只有 26.4 KHz；AWS F1 的 peer-to-peer PCIe 让 FPGA 直接交换 AXI4 transaction，可到 1 MHz；本地 U250 通过约 25 美元的 QSFP direct-attach cable 和 Aurora/AXI4-Stream 接口，论文报告可到 1.6 MHz。[pdf:E06]（PDF 物理页 6，Section IV-A/IV-B）；[pdf:E02]（PDF 物理页 2，平台概览）；[pdf:E07]（PDF 物理页 7，Section IV-C）

6. **运行时同步。** 每个 partition 的 LI-BDN channel queue 保存输入/输出 token；output FSM 等待所有组合相关输入有效，fireFSM 则在输入齐备且输出已 fire 或正在 fire 时推进一个 target cycle。跨卡同步不是全局 barrier 的抽象描述，而是由这些 token availability 条件具体决定。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II-A）

7. **静态与动态工作分配的边界。** module-to-FPGA placement 是编译前静态分配；论文没有实现运行时 module migration、work stealing 或按负载重分区。所谓动态部分来自 FAME-5：对 N 个重复 module，combinational logic 共享，sequential state 复制，hardware scheduler 在运行时选择本轮更新哪份 state。这个 scheduler 在一个固定 partition 内调度 simulator thread，用来节省 LUT 并摊薄通信，而不是把“忙 FPGA”的模块转移到“闲 FPGA”。[pdf:E03]（PDF 物理页 3，FAME-5 定义）；[pdf:E11]（PDF 物理页 11，Section VI-B）

输出是每个 FPGA 的 bitstream、对应的 host driver 和跨卡 transport 连接起来的 deterministic simulator。对需要原 RTL 性能数字的工作，应使用 exact-mode；fast-mode 更适合 boundary 本身 latency-insensitive、且研究问题能容忍边界额外一拍的场景。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出定理、优化目标或封闭形式的吞吐模型，因此不存在可逐式复现的“核心数学推导”。它给出的主要是离散的 cost relation，可以用来理解工程含义。

exact-mode 中，论文示例需要两次跨卡 token transfer 才能完成一个 target cycle；组合依赖链长度同时决定独立 I/O channel 数和 link crossing 数，FireRipper 只接受长度不超过 2 的边界。[pdf:E04]（PDF 物理页 4，Section III-A1）fast-mode 通过 seed token 把两侧一个 cycle 的计算并行化，把结果从 cycle N 延迟到另一侧的 cycle N+1，因此减少交换次数却改变原 RTL 的边界时间语义。[pdf:E04]（PDF 物理页 4，Section III-A2）

FAME-5 的成本关系更清楚：N 个重复 instance 共享 combinational logic、复制 N 份 sequential state，hardware scheduler 因而要花 N 个 host FPGA cycle 才完成一个 target cycle。FireAxe 的判断是，跨卡 latency 显著大于相对单 instance 多出的 N-1 个本地 cycle，所以这些 cycle 能落在原本的通信等待中。[pdf:E11]（PDF 物理页 11，Section VI-B）这不是一个对所有 N 都成立的渐近证明，因为 interface bits 也会随 thread 数增加，且最慢 partition、link topology 和 bitstream timing 都可能改变。

一个更实用的心智模型是：

`target-cycle time ≈ max(partition local work, required link round trips + serialization) + residual synchronization`

这是本文基于论文机制整理出的解释式，不是作者给出的公式。它说明了为什么提高 bitstream frequency 只能减少 local work 与 serializer cost，却不能消除物理 link latency；也说明了为什么更宽 boundary、更多 link crossing 和更多 FPGA 会产生与容量收益相反的增长项。

## § 7 — 实验设计与结论

**问题一：跨卡后还能保持原 RTL 的 cycle count 吗？** 作者把 Rocket tile、Sha3Accel、Gemmini 分别从 SoC 中拆到另一块 FPGA，并与 monolithic FireSim 比较。exact-mode 三项均为 No Error；fast-mode 的绝对 cycle-count error 分别为 0.98%、6.62% 和 0.22%。答案是 exact-mode 在这些 workload 上闭合了 fidelity claim，而 fast-mode 的误差与 workload 对边界 latency 的敏感度有关，不能统一校正。[pdf:E12]（PDF 物理页 12，Table II）

**问题二：吞吐由什么控制？** 作者在两 FPGA 上同时扫 partition interface width、bitstream frequency 与 mode，并分别使用本地 QSFP 和 AWS peer-to-peer PCIe。论文归纳出四个 knob：interconnect、partitioning mode、module selection 所决定的 boundary width、bitstream frequency。QSFP 上 boundary 小于约 1500 bit 时，fast-mode 相对 exact-mode 约有 2 倍收益；超过这一宽度后，serialization/deserialization 与通信延迟相当，fast-mode 优势变小。cloud 整体比本地低约 1.5 倍，原因是更高的跨卡延迟。[pdf:E10]（PDF 物理页 10，Fig. 11、Fig. 12 与 Section VI-A）

**问题三：增加 FPGA 数量是否近似线性扩展？** 作者保持 NoC boundary width 不变，把 3 到 6 块 FPGA 连成 ring。虽然每块卡只与邻居交换 token，simulation frequency 仍随卡数增加而下降，作者归因于 token exchange 的轻微 timing issue。[pdf:E11]（PDF 物理页 11，Fig. 13）答案是否定的：多卡提供容量，不自动提供线性吞吐扩展。

**问题四：重复 module 能否掩蔽通信？** 作者把 1 到 6 个 BOOM tile 全部分到另一块 FPGA 并应用 FAME-5，固定 tile 侧为 15 MHz、SoC 侧为 20 或 30 MHz。tile 数从 1 增至 6 时，simulation performance 下降不到 2 倍，尽管跨卡 bits 随 thread 数线性增加。[pdf:E11]（PDF 物理页 11，Fig. 14 与 Section VI-B）答案是“在这个重复 tile 场景中可以显著摊薄”，而不是“任意更大设计都接近零开销”。

**问题五：容量扩展是否真的打开了新 workload？** 24-core BOOM SoC 被按 ring NoC boundary 分到 5 块 U250：4 块各放 6 个 FAME-5 multithreaded tile，第 5 块放 SoC subsystem，整体跑到 0.58 MHz。系统在 30 亿 cycle 后触发 BOOM RTL bug，不到 2 小时到达；商业 software RTL simulator 为 1.26 KHz，作者报告 FireAxe 快 460 倍。[pdf:E07]（PDF 物理页 7，Fig. 6 与 Section V-A）这支持“容量加速能使深层 full-stack bug 进入可观测时间窗”，但 bug 根因在论文中仍未确定。

**问题六：单核也能通过 partitioning 变大吗？** GC40 BOOM 的 monolithic 10 MHz bitstream 因 congestion 构建失败；作者以 exact-mode 把 backend/LSU 与 frontend/memory 拆开。两侧分别占 63% 和 18% 的 FPGA LUT，boundary 超过 7000 bit，最终 Linux boot simulation 为 0.2 MHz。[pdf:E07]（PDF 物理页 7，Section V-B）这个案例证明“能跑”，同时也是 workload imbalance 和宽边界代价的警示。

**问题七：系统级研究是否获得了单模块 benchmark 没有的信息？** 在 leaky-DMA 案例中，server 是 12 个 BOOM core、分布在 3 块 FPGA；随着转发 packet 的 core 增加，NIC 看到的 read/write latency 上升，XBar 在超过 6 个 core 后 write latency 比 ring NoC 增长更快。[pdf:E08]（PDF 物理页 8，Fig. 9）；[pdf:E09]（PDF 物理页 9，实验设置与解释）在 Go GC 案例中，4 个 5-wide BOOM core 分到 2 块 FPGA；GOMAXPROCS=1 时 99th-percentile tail latency 很高，而同 NUMA node 的 2 core Xeon 为 28 ms、跨 NUMA node 为 42 ms，作者据此把结果解释为 cache affinity 与 coherency overhead 的竞争，但明确把更深因果确认留给 future work。[pdf:E09]（PDF 物理页 9，Fig. 10 与 Section V-D）

实验边界也很明确：主要本地平台是 U250，topology 受每卡两个 QSFP cage 限制；完整 artifact 要求至少 4 块 U250、约 300 GB 磁盘，作者估计脚本化准备 1 小时、完整实验约 40 小时。[pdf:E13]（PDF 物理页 13，Artifact checklist）

## § 8 — Take-aways

**5 句话。** FireAxe 把超过单 FPGA 容量的 monolithic RTL 转成由多个 LI-BDN partition 组成的 simulator。FireRipper 自动化了 dependency analysis、hierarchy rewrite、partition extraction 和 FAME transformation，但 module placement 仍主要由用户静态指导。exact-mode 保留原 RTL cycle semantics，却要为组合依赖支付多次 link crossing；fast-mode 减少同步，却只对修改后的 RTL cycle-exact。真实瓶颈不是 FPGA 数量本身，而是边界宽度、link latency、每 target cycle 的 crossing 数和最慢 partition。FAME-5 只在重复 module 场景中提供一种很有价值的运行时调度，使本地工作能摊薄通信等待。

**3 句话。** 多 FPGA 给 FireSim 带来的是容量弹性，不是免费的吞吐 scaling。好的 partition 应同时释放大量 LUT、保持窄而 latency-insensitive 的边界，并让两侧工作量与互连成本相称。论文最有启发性的贡献，是把 partition semantics、transport 与 simulator multithreading 放在同一个性能模型里讨论。

**1 句话。** FireAxe 说明“大设计能否在多卡上高效仿真”取决于是否能找到让资源收益压过同步与序列化成本的语义边界。

## § 9 — 最脆弱的假设

最脆弱的假设是：**现实设计里存在既能显著释放 FPGA 资源、又足够窄且具有可处理时间语义的 partition boundary。**

这个假设一旦失败，两种 mode 会从不同方向失效。若 boundary 含超过两级的跨端口组合依赖，exact-mode 直接编译终止；即使合法，它也要为一个 target cycle 多次跨 link。若 boundary 不是 latency-insensitive，fast-mode 注入的一拍会改变 backpressure 和 workload cycle count，只能通过局部 interface transform 缓解，而不能保证对原 RTL 无误差。[pdf:E04]（PDF 物理页 4，exact/fast 限制）；[pdf:E05]（PDF 物理页 5，fidelity 边界）若 boundary 太宽，serialization 取代 link latency 成为主导，约 1500 bit 之后 fast-mode 的相对优势在作者平台上已经明显缩小。[pdf:E10]（PDF 物理页 10，Section VI-A1）若为了容纳设计继续增加 FPGA，ring 实验又显示 simulation frequency 会随卡数下降。[pdf:E11]（PDF 物理页 11，Fig. 13）

论文提供了 NoC router、accelerator、core tile 和 GC40 core 的正例，也展示了 exact-mode 的三项零 cycle error 与 fast-mode 的 workload-dependent error；但没有给出大规模 RTL corpus 上“可用 boundary 的分布”，也没有自动 resource/synchronization co-optimization。作者自己把 RTL-level resource estimation 和 graph partitioning 列为 future work。[pdf:E13]（PDF 物理页 13，Section VIII-B）

因此，基于证据的判断是：FireAxe 已证明“某些有结构的 SoC 能跨卡”，尚未证明“任意资源超限设计都能找到高效边界”。这不是对系统实现的否定，而是对 scale claim 的正确作用域限定。

## § 10 — 最小复现实验

一周内最值得复现的不是 24-core 全系统案例，而是“边界宽度与同步 mode 是否按论文声称共同决定吞吐与 fidelity”。

硬件上优先使用论文 artifact 支持的 U250/QSFP server；完整 artifact 的硬件、磁盘和时间要求已给出，脚本会依次编译 target software、host driver、烧录预构建 bitstream、运行 simulation 并生成 plot。[pdf:E13]（PDF 物理页 13，Artifact checklist）；[pdf:E14]（PDF 物理页 14，Experiment workflow）只运行两 FPGA 子集即可，不必复现全部 40 小时实验。

实验选择一个可改变 core-tile 数量、从而改变 boundary width 的 SoC：

1. 对相同 RTL 分别构建 monolithic FireSim、FireAxe exact-mode、FireAxe fast-mode。
2. 至少选择三档 boundary width，覆盖论文所示 1500 bit 以下与以上；固定 bitstream frequency 和物理互连。
3. 每档测 simulation frequency、实际 link bytes、serializer busy cycle、两侧 LI-BDN stall cycle，并运行固定 workload 记录 total target cycles。
4. 支持 claim 的结果应同时满足：exact-mode cycle count 与 monolithic 一致；窄边界时 fast-mode 接近 2 倍；边界变宽时两种 mode 均下降且 fast-mode 优势收窄。
5. 若 exact-mode 出现非零 cycle error，或窄边界 fast-mode 并未减少等待，或宽度增长不对应 serializer/stall 的增长，则核心机制至少有一项被反驳，需要先排除 driver 与 bitstream frequency 差异。

这个实验比只复画 Fig. 11 更强，因为它同时检查结果曲线和机制计数器，能区分“link latency 主导”与“host driver、timing closure 或负载不平衡”这些替代解释。

## § 11 — 最强反例设计

最强反例应主动构造一种**资源释放很大、但边界同时宽、强反馈且负载不平衡**的 RTL，而不是只换一块更慢的 FPGA。

可以设计两个共享 directory/coherence 或集中仲裁器的 partition：一侧有大量 request source，另一侧有 memory scheduler；跨界既有数千 bit data，又有 ready/credit/priority 的组合反馈。逐步把反馈链从 1 增到 3，把 boundary width 从数百 bit 增到数千 bit，并把 2 块卡扩到 6 块 ring。对每个点同时尝试 exact-mode 与 fast-mode，测 compile success、cycle error、simulation frequency、每 target cycle 的 link round trip、serializer utilization 和最慢 partition stall。

这个反例有三个可证伪出口。第一，dependency chain 超过 2 时 exact-mode 按设计会拒绝编译；如果为了合法化边界而插寄存器，就已经改变了待验证 RTL。第二，fast-mode 对强反馈边界注入一拍后，仲裁顺序、cache miss overlap 或队列 occupancy 可能系统性改变，Table II 中已有 workload-dependent error 先例。[pdf:E12]（PDF 物理页 12，Table II）第三，即使两种 mode 都能运行，宽边界的 serialization、ring 中更多 FPGA 的 token timing，以及两侧资源/工作量不平衡可能共同使 6 卡吞吐低到不如更小的抽象 simulator。

若 FireAxe 在这个构造下仍能保持 exact-mode 零误差，且吞吐退化主要与可预测的 link/serializer cost 一致，那么反例失败，反而强化论文机制。若找不到一个既合法又高效的 boundary，则它会直接挑战“规模增长可通过继续加卡解决”的外推，而不仅是报告一个边角性能回退。

## § 12 — Follow-up Research Idea

**候选方向：带边界语义合同的 partition-and-schedule co-design。** 这是基于本论文证据提出的候选研究方向，未做充分相关工作检索，不声称 novelty。

**（a）未满足的需求。** FireRipper 目前把 placement 主要留给用户，编译器只在给定边界后判断是否合法；runtime 的 FAME-5 scheduler 又只看到固定 partition 内的重复 module。用户真正需要的是在 build 之前知道：哪条边界能放得下、会引入多少同步、允许多少 latency、以及 workload 是否足以用本地 work 覆盖 link wait。

**（b）潜在研究价值。** 该方向把问题从“自动找一个图切分”改成“联合选择资源放置、边界时间语义和 simulator schedule”。在 ISCA/FPGA 类系统研究中，它只有在同时给出 fidelity contract、编译成功率、真实 bitstream 与跨 workload 的 scaling 曲线时才有高影响价值；单纯增加一个 heuristic partitioner 不够。

**（c）可借鉴的方法。** 可以借鉴 synchronous dataflow 的 repetition vector、distributed discrete-event simulation 的 conservative synchronization，以及 network calculus/queueing 中的 backlog bound。编译器为每条候选边界生成合同：组合依赖深度、是否 latency-insensitive、最大允许额外 latency、预计 bits/cycle、资源释放量；scheduler 再按合同选择 exact token round、fast token round 或 FAME-5 thread batch，而不是只用一个全局 mode。

**（d）第一个证伪实验。** 在 NoC tile、accelerator、GC40-like wide boundary 和第 11 节强反馈反例上，与手工最佳 FireAxe 配置比较。若 co-design 在保持 exact workload 的 cycle count 时不能提高 geometric-mean simulation frequency，或编译器预测的 stall/serialization 与硬件计数偏差持续超过可接受阈值，或合同硬件本身造成 timing/resource 回退，则该方向应被否决。

**（e）与现有工作的实质区别。** 论文自己的 future work 提到 RTL resource estimation 与 graph partitioning；这里进一步要求把“边界是否可延迟”“每 cycle 同步轮数”和“运行时可用的重复 work”作为同一个可验证对象，而不是先静态切图、再被动测性能。[pdf:E13]（PDF 物理页 13，Section VIII-B）它也不等同于一般 runtime load balancing：RTL state 不能随意迁移，任何动态 schedule 都必须由边界合同证明不会改变要求保留的 target semantics。
