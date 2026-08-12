# Lotus: A Multi-FPGA Task Dataflow Architecture to Accelerate Cycle-Level Simulation

作者：Fares Elsabbagh；Joel S. Emer；Daniel Sanchez  
出处：2026 ACM/IEEE 53rd Annual International Symposium on Computer Architecture（ISCA）  
年份：2026  
DOI：10.1109/ISCA66397.2026.00129  
Zotero key：HQQHEMP5  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是“怎样把 RTL 再综合得更快”，而是一个更根本的系统问题：**能否不用把待模拟电路空间映射成 FPGA 逻辑，而把 cycle-level simulation（周期级仿真）改造成可在数千个通用小核上执行的软件 task dataflow（任务数据流），并且扩展到多 FPGA 后仍达到 emulator（硬件仿真器）级速度。** 作者指出，传统多 FPGA emulator 把门级逻辑分散到多片器件上，并在每个模拟周期交换跨片信号；单片 FPGA 本可运行在数百 MHz，但跨片时延把大系统压到几 MHz，使 FPGA 远低于可达频率运行。Lotus 因而把“空间映射电路”改成“时间复用 task”，让多个 task 重用同一批 core，并把通信与计算重叠起来。论文的摘要和引言把这一核心问题、dataflow、priority 与 selective execution 三个机制，以及 8-FPGA 原型的总体结论放在一起陈述。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 1，Introduction，通信瓶颈与 temporal mapping 论证）

问题重要，是因为现有两条路线各有结构性障碍。emulator 的大设计编译可耗时数天到数周，设备规模限制可模拟电路规模，而且主要服务 RTL；普通多核 CPU 上的软件仿真又被细粒度通信与同步拖住。Lotus 想保留软件模型的快速编译、可编程性和跨抽象层能力，同时取得接近专用 emulator 的吞吐。论文直接声称，在手写 Lotus DSL 的四个大设计上，8-FPGA Lotus 相对其 emulator 基线几何平均快 42%，使用的 FPGA 数量几何平均少 2.85 倍；但这个结论有严格适用范围，不能扩展成“任意 RTL 都优于 emulator”。[pdf:E03]（PDF 物理页 10，Emulator baseline 与 Evaluation 开头）

这里的“cycle-level”指同步数字系统按逻辑周期演化，不是电磁暂态 EMT 的数值积分步。论文没有定义 EMT 中完整 old-state 到 new-state 的全系统原子提交，也没有讨论网络方程、迭代收敛或多速率积分。因此，本卡只把 Lotus 解释成数字系统的 cycle-level task runtime，绝不把其模拟周期边界自动写成 EMT 完整步提交。论文结论本身也把贡献限定为 task-level dataflow 对 cycle-level simulation 的加速，并强调其软件可编程性与 FPGA 资源效率。[pdf:E04]（PDF 物理页 13，Conclusion）

## § 2 — 前人工作与不足

论文对相关工作的陈述可以分成三类；以下是**论文自己的归纳**，不是本卡对外部文献的独立复核。

第一类是软件 RTL simulator。Verilator 把电路 dataflow graph 的 node 分配到线程，并在线程内静态排序；跨线程的 same-cycle edge 需要同步，所以通常难扩展到少数线程以上。RepCut 通过复制 node、把通信限制到模拟周期间来改善扩展性，但论文称其仍只扩展到数十线程。这里的瓶颈不是“缺少更多 PE”，而是共享内存上的细粒度通信与同步成本。[pdf:E05]（PDF 物理页 3，Section II-B）

第二类是专用软件仿真架构。ASH 已经采用小 task、priority 和 selective execution，但它在单芯片 ASIC 上动态展开 dataflow graph：task 执行时携带并发送函数指针、priority 等 metadata；selective execution 依赖 speculative Time Warp（乐观时间扭曲）与 rollback。Manticore 采用 static bulk-synchronous scheduling（静态批同步调度），并以全局暂停处理动态时延事件，但同样是单芯片方案。Lotus 继承 ASH 的三个高层思想，却利用 graph 静态这一条件，把全部 task metadata 常驻 task unit，并用非推测的 null-token 同步取代 rollback；论文报告这种 task 管理逻辑相对 ASH 等价结构少 17 倍逻辑，selective execution 只占约 1% 设计逻辑。[pdf:E06]（PDF 物理页 2，贡献与 ASH 对比）[pdf:E07]（PDF 物理页 3，静态 graph 与 task-unit storage）

第三类是 emulator 与 FPGA prototyping。传统 emulator 把电路直接映射到 FPGA 或 gate processor，跨片信号每周期通信；FireSim、DIABLO、SMAPPIC 等多 FPGA 平台能利用组件之间本来就较长的通信时延，但论文认为它们不适合需要逐周期通信的大型单体设计。RAMP Gold、FAME、HASim 通过 time-division multiplexing（时分复用）在 FPGA 上模拟多个 core，却要求面向特定模型的人工改造。Lotus 的差异是把“通用 task runtime”本身做成硬件，并由编译器从高层 SDF graph 自动产生静态配置与 tile executable，而不是为每个被模拟系统做一份离线逐周期 PE/bank schedule。[pdf:E05]（PDF 物理页 3，Section II-B/II-C）[pdf:E08]（PDF 物理页 8，Fig. 9–10，DSL 与 compilation flow）

## § 3 — 重建作者的思考路径

从论文给出的背景出发，可以逆向重建出如下思路。

首先，多 FPGA emulator 的根本代价已经由跨片逐周期通信决定；既然 spatial mapping（空间映射）不能让每片 FPGA 接近自身时钟上限，继续为每个 gate 占用固定 FPGA 资源就不再划算。更合理的方向是让高频 FPGA 执行大量软件 task，以时间复用换容量，并让跨片 token 在后台飞行。[pdf:E02]（PDF 物理页 1，Introduction）

其次，普通 CPU 上的 task 太小，线程、队列、共享内存和同步开销会吞掉有用工作，所以需要把最频繁的 runtime 动作下沉到硬件：收 token、计数、判定 ready、选 task、送 core、发输出。ASH 证明了 task dataflow、critical-path priority 和 low-activity skipping 有价值，但动态 graph metadata 与 speculation 对 FPGA 太昂贵。若 graph 在一次仿真运行中本来就是静态的，就应把 taskId、输入槽、输出目的地和 priority 预装到分布式 task unit，运行时只处理 invocation 状态。[pdf:E07]（PDF 物理页 3，静态 graph 观察）

再次，单纯“有很多 ready task”并不保证一个模拟周期尽快结束。same-cycle dependency 的长链会成为 critical path，所以 runtime 应在已 ready 的集合中优先执行关键 task；但 priority queue 本身也必须足够便宜。静态、稠密 taskId 使 hierarchical bitmap（分层位图）成为可能：低 taskId 表示高优先级，队列每硬件周期可入队和出队一个 invocation。[pdf:E09]（PDF 物理页 5，Section III-C）[pdf:E10]（PDF 物理页 6，Fig. 6 与位图队列）

最后，tiny task 的执行开销和跨 tile token 流量仍可能过大，因此必须由编译器共同解决：选择 token 或 memory communication，插入只携带顺序的 order edge，合并小 task，并在需要跨周期合并时 temporal unroll（时间展开）graph。这样，硬件只实现简单的 0/1-cycle token 协议，复杂的切分与重写留给编译期。[pdf:E11]（PDF 物理页 9，Fig. 11、Order Edges、Coarsening and Temporal Unrolling）

## § 4 — 核心 Intuition

Lotus 的核心直觉是：**多 FPGA 的性能已经被通信时延钳住，因此不要把电路永久铺在 FPGA 上，而要把静态 dataflow graph 的 tiny task 时间复用到高频小核上。** 编译器只决定 graph 结构、通信形式、task priority 和 FPGA/tile placement；运行时由 token 是否齐全决定 invocation 是否 ready，并在 ready 集合中按 priority 发射。输入未变化时，task unit 不让 core 重算，而是发送 null token 让下游沿用旧值；跨 FPGA 通信则通过异步 token 网络与计算重叠，而不是每周期全局 lockstep。[pdf:E12]（PDF 物理页 2，Fig. 1 与 temporal execution）[pdf:E13]（PDF 物理页 4，Section III-A）[pdf:E14]（PDF 物理页 6，Section III-D）

## § 5 — 具体方法与完整 Pipeline

以论文的二级流水例子为主线。其逻辑关系是

\[
y[n] = a\cdot x[n-1] + b\cdot y[n-1],
\]

Fig. 1 把乘法和加法写成 node，把 wire 写成 same-cycle edge，把 register 写成 cross-cycle edge。[pdf:E12]（PDF 物理页 2，Fig. 1）从这个高层模型到硬件执行，pipeline 如下。

1. **写 task function 与 graph。** Lotus DSL 中，task function 用 `In/Out/InOut` 或 partial-access 参数声明读写；graph definition 用 `Wire<T>` 表示 same-cycle edge，用带初值的 `Reg<T>` 表示 cross-cycle edge。编译器通过编译并执行 graph definition，得到一份文本 graph；它还不是 Lotus executable，因为 task 尚未被放置，参数数目也未受硬件上限约束。[pdf:E08]（PDF 物理页 8，Fig. 9–10、Section V-A/V-B）

2. **决定 token communication 与 memory communication。** 小值、跨 tile 值和非 constant 输入优先走 dataflow token；cache、SRAM 等部分访问的大对象放在 memory。若 task 的 token 输入超过硬件上限，剩余值进入 overflow memory。这个决策是数据表示与位置选择，不是对每一模拟周期做 bank-by-bank 静态排程。[pdf:E11]（PDF 物理页 9，Communication 段落）

3. **插入静态 order edge。** order edge 是无数据 token，用来约束 task invocation 的先后。例如 `A@N` 通过单缓冲 memory 给 `B@N` 写值时，必须保证 `B@N` 在 `A@N+1` 覆盖该值前执行，于是编译器插入 `B@N → A@N+1`。order edge 只表达依赖；它不规定具体硬件时刻，也不是全局 barrier。[pdf:E11]（PDF 物理页 9，Order Edges）

4. **coarsening 与 temporal unrolling。** 编译器把多个 tiny task 合并，减少 task initiation 和 token 开销。若被合并 task 之间有 cross-cycle edge，直接合并可能产生硬件不支持的两周期或更长输出边；编译器因此复制多个时间实例，把高 delay 关系展开到扩展 graph 中，再完成合并。Fig. 11 展示的是 graph 变换，不是运行时把每个 core 离线排进固定周期槽。[pdf:E11]（PDF 物理页 9，Fig. 11）

5. **分层 placement。** 编译器用 PaToH hypergraph partitioning 先把 task 分到 FPGA，再分到该 FPGA 内的 tile，同时平衡工作量、减少通信并避免把高时延通信放到 critical path。两条硬约束尤其关键：same-cycle edge 两端必须在同一 FPGA；通过 memory 通信的 task 必须在同一 tile，因为 tile 之间没有 coherence。[pdf:E15]（PDF 物理页 8，Section V-C，Mapping）

6. **priority 编码。** 每个 task 都获得 taskId，较小 taskId 表示更高 priority。编译器 flow 中有独立 Prioritization pass，但论文没有完整公开从 graph 到 taskId 的全部启发式；实验文字只说明其效果与 critical path、长通信时延和少数长 task 有关。因此可说它生成静态 priority order，不能把它写成一张完整、逐周期的静态执行表。[pdf:E09]（PDF 物理页 5，Prioritized execution）[pdf:E16]（PDF 物理页 13，Fig. 17 与 prioritization 分析）

7. **装载 tile 配置。** 编译结果由 task-unit configuration data 与每个 tile 的 task code/data executable 组成。一个 task 静态绑定到单一 tile，并总在该 tile 执行；task unit 保存函数入口、输入槽、输出 token 目的地等 graph 信息。原型每 FPGA 有 68 个 tile、每 tile 4 个 RV32IM core、一个 128 KB L2 与可容纳 1024 个 task 的 task unit；这些是空间容量配置，不是把 task 永久绑定到某个 core。[pdf:E17]（PDF 物理页 7，Fig. 8、Table I–II）

8. **运行时 ready-driven 发射。** token 携带 `(cycleId, taskId)`，input unit 写入输入值并递减 remaining-token count；只有全部入边 token 到齐，invocation 才进入 ready queue。dispatcher 从 ready queue 取出最高优先级 invocation，向 tile 内可用 core 流送函数入口与参数；task 调用 `finish_task` 后，output unit 按静态 fan-out 产生各条出边 token。由此可见，**静态的是 tile placement、edge 与 priority；动态的是每个 invocation 何时 ready、何时获得 core。论文没有 compiler-to-core 的固定 placement。**[pdf:E13]（PDF 物理页 4，Section III-A）[pdf:E18]（PDF 物理页 5，Fig. 4–5 与 Task unit organization）

9. **跨周期重叠。** task unit 保存偶数周期和奇数周期两套 invocation-specific 输入与 token count，使相邻模拟周期可以重叠执行。它意味着系统不是在每个模拟周期末执行一个全局 barrier；不同 cycleId 的 invocation 可以同时驻留，只要 token dependency 允许。[pdf:E09]（PDF 物理页 5，Versioning）

10. **selective execution。** input unit 比较本周期 non-null 输入与旧版本；若全部相同且 task 可跳过，dispatcher 不把它送到 core，而把 invocation 直接交给 output unit，由后者发送 null token。消费者收到 null token 后把旧输入复制到当前版本。带 side effect 的 task，或收到 non-null order token 的 invocation，不能跳过。这里的 Chandy–Misra–Bryant conservative synchronization 是显式 null-message 因果协议，不是模拟周期间的全局同步，也不含 speculative rollback。[pdf:E14]（PDF 物理页 6，Section III-D）[pdf:E19]（PDF 物理页 6，Section III-D 结尾与 Fig. 7）

11. **多 FPGA 通信何时参与决策。** 编译期，跨 FPGA 的高时延直接影响 partitioning，same-cycle edge 因而被限制在同一 FPGA。运行期，跨片 output token 经 all-to-all optical links 异步到达；其到达时间通过 remaining-token count 影响 ready 时刻，进而间接影响 priority queue 中谁能被选择。8-FPGA 原型报告约 200 ns FPGA-to-FPGA latency 与 350 GB/s bisection bandwidth；这些 link 不参与逐周期全局 commit，而是作为 token readiness 的时延来源。[pdf:E19]（PDF 物理页 6，Fig. 7 与 Prototype system）

**四条不能混写的边界：**

- static task placement/order edge 决定“在哪里执行、必须先于谁”，runtime ready-driven dispatch 决定“这个 invocation 现在能否发射”；
- task 静态映射到 tile，不等于静态映射到 core，更不等于离线逐周期 PE/bank schedule；
- same-/cross-cycle edge 定义逻辑 cycleId 关系，偶/奇 version 允许实际执行交叠；
- 论文没有给出完整全局状态的 old-state→new-state atomic commit。其 memory model 只保证 task store 先于 later-task load，并明确说 concurrent task access 没有顺序保证；需要的先后关系由 token/order edge 表达。[pdf:E18]（PDF 物理页 5，task-oriented memory model）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有新的定理、误差界或复杂数学推导；形式化内容主要是 SDF 的周期关系与 task runtime 规则。Fig. 1 的递推式

\[
y[n] = a x[n-1] + b y[n-1]
\]

说明 `Reg` edge 把生产者在周期 \(N\) 的结果交给消费者的周期 \(N+1\)，而 `Wire` edge 在同一周期内传播。[pdf:E12]（PDF 物理页 2，Fig. 1）

为了精确表达论文文字，可把每条入边 \(e\) 的 delay 记为 \(\delta_e\in\{0,1\}\)。对 task \(v\) 的周期 \(N\) invocation，runtime readiness 可写成

\[
\operatorname{ready}(v,N)
\iff
\forall e=(u,v),\; \operatorname{token}(e,N-\delta_e)\text{ 已到达}.
\]

这不是论文给出的新公式，而是对“收到所有 incoming-edge token 后才 ready”的等价形式化。[pdf:E13]（PDF 物理页 4，Section III-A）ready 后，tile 内 dispatcher 的选择规则可简写为

\[
(v^*,N^*) = \arg\min_{(v,N)\in R_{tile}} \operatorname{taskId}(v),
\]

其中 \(R_{tile}\) 是当前 ready invocation 集合；较小 taskId 优先。hierarchical bitmap 只是把这个 `argmin` 做成每硬件周期可 dequeue 的流水结构。[pdf:E09]（PDF 物理页 5，Prioritized execution）[pdf:E10]（PDF 物理页 6，Fig. 6）

selective execution 的逻辑条件可概括为：所有有效输入与上一周期相同，且 task 无 side effect，也没有要求本次执行的 non-null order token 时，才允许 skip；skip 后仍必须为每条出边发 null token，使下游 invocation 的 token count 正常闭合并复用旧值。这个规则保持 dataflow 因果关系，但不等于把整个模拟状态在一个瞬间提交。[pdf:E14]（PDF 物理页 6，Section III-D）

周期语义上最重要的结论是：论文把 cycleId 放进 token，并用偶/奇两套 buffer 让 \(N\) 与 \(N+1\) 的 task 交叠；因此“一个逻辑模拟周期”不是“所有 FPGA 同时完成一次物理 barrier”。同样，实验中“cycles spent committing instructions”指 RISC-V core pipeline 的指令提交占比，不是模拟模型从旧全局状态到新全局状态的原子 commit。[pdf:E20]（PDF 物理页 11，Fig. 12 解释）把这些术语直接移植为 EMT 完整步原子提交，会超出论文证据。

## § 7 — 实验设计与结论

**问题一：Lotus 能否达到 emulator 级速度并提高 FPGA 效率？** 实验用 8 片 Alveo U55C 跑四个手写 Lotus DSL benchmark 和两个 Verilog/Verilator benchmark，并与 128-core CPU server 及估算 emulator baseline 比较。四个 DSL benchmark 的 Lotus 速度分别为 2474、1452、953、485 KHz；相对 800 KHz emulator baseline，几何平均为 1.42 倍，所需 FPGA 数估算少 2.85 倍，performance per FPGA 为 4.05 倍；相对 CPU 为 7.98 倍。[pdf:E21]（PDF 物理页 10，Table IV）答案是：**对手写、经良好 graph 化的 DSL 设计成立；对自动 Verilog 路径不成立。** 两个 Verilog benchmark 相对 emulator 的几何平均只有 0.17 倍，说明 compiler quality 是决定性条件，而不是硬件本身自动保证优势。[pdf:E21]（PDF 物理页 10，Table IV）[pdf:E22]（PDF 物理页 11，Verilog bottleneck 分析）

**问题二：selective execution 是否真的省下有效工作？** Fig. 12 对比 selective on/off 的 core cycle breakdown。NTT 与 MatMult 每周期输入变化，几乎无收益；Multicore 因低 activity，执行指令减少 3.29 倍，速度提高 2.31 倍，但 idle 比例升到约 60%，暴露出 selective execution 引起的 load imbalance。[pdf:E20]（PDF 物理页 11，Fig. 12 与正文）答案是：机制能显著减少低 activity 工作，但只在输入稳定、且跳过后的任务分布仍可负载均衡时转化为速度。

**问题三：多 FPGA 扩展是否有效？** 论文从 1 扩到 8 FPGA。NTT 因通信略低于线性，MatMult 因更多 task-queue capacity 略超线性，Cores 因 memory reuse 略低于线性，Multicore 到 4 FPGA 略超线性、8 FPGA 因 load imbalance 回落。[pdf:E20]（PDF 物理页 11，Fig. 13）答案是：所测四个 DSL graph 能扩展，但不同 benchmark 的限制分别来自网络、memory locality 与负载均衡，不能用单一“线性扩展”概括。

**问题四：编译器 placement 是否关键？** Fig. 16 比较 random、flat hypergraph 与 hierarchical hypergraph mapping。hierarchical mapping 相对 random 为 3.3–10.3 倍；Multicore 中把 cross-device bytes 比例从 0.57% 降到 0.49%，就带来 1.7 倍速度提升。[pdf:E23]（PDF 物理页 12，Fig. 16 与正文）答案是：即使跨片流量占比已经很小，微小差异仍可能支配性能；多 FPGA 通信在编译期 placement 和运行期 ready latency 两处都参与结果。

**问题五：coarsening 与 temporal unrolling 是否值得？** NTT 使用 2 倍 unrolling 得到 3.0 倍加速，MatMult 使用 4 倍 unrolling 得到 3.4 倍；Cores 虽减少 12% 指令，却只快 5%，因为更大 task 增加 cache miss 并削弱 selective execution；Multicore 不采用 unrolling，因为跨周期合并会增加指令和 overflow-memory 开销。[pdf:E24]（PDF 物理页 12，Fig. 15 与 Section VII-E）答案是：它不是普适优化，收益取决于 task 粒度、输入数、code footprint 与 activity。

**问题六：priority 是否有效？** Fig. 17 用 random priority 对比论文的 priority。对少量长 task 主导、parallelism 有限的 Verilator graph，错误 priority 最多损失接近 1.9 倍；对没有 same-cycle dependency 且 task 长度均匀的 NTT，收益很小。[pdf:E16]（PDF 物理页 13，Fig. 17）答案是：priority 只在 critical path 能被 ready-order 改变时有效；它不能创造不存在的 parallelism。

**问题七：结果覆盖了什么，不能外推到什么？** Table III 的六个 benchmark 包括 NTT、256×256 systolic MatMult、4096 个独立 core、4096-core mesh multicore，以及两个 Verilog 设计；前三个 DSL benchmark 是作者按“好的 RTL-to-C compiler 应产生的抽象层”手写，Multicore 的部分 router 还使用高于 RTL 的建模。[pdf:E25]（PDF 物理页 9，Table III 与 Methodology）emulator 性能不是同设计实测商业机器，而是采用 FireAxe 两片直连 FPGA 的 800 KHz cycle-exact 结果，并乐观假设 FPGA 数增加后仍保持 800 KHz；emulator 所需 FPGA 数也由单片可容纳规模外推，忽略额外 virtual-wire 逻辑与通信瓶颈。[pdf:E03]（PDF 物理页 10，Emulator baseline）因此，论文有力证明的是“Lotus 原型加合适 graph/compiler 可以到达该量级”，不是“所有 RTL、所有 emulator 配置都具有表中倍率”。

原型本身由 8 片 U55C、544 个 tile、2176 个 core 组成，运行 400 MHz；互连采用直接 all-to-all optical topology。这个规模证明了 runtime 可以真正跨芯片运行，而不是只在 simulator 中估算。[pdf:E19]（PDF 物理页 6，Fig. 7）[pdf:E17]（PDF 物理页 7，Table I–II）

## § 8 — Take-aways

**5 句话：**

1. Lotus 把多 FPGA 从“被模拟电路的空间载体”改造成“高频 task runtime”，通过时间复用提高容量与利用率。[pdf:E01]（PDF 物理页 1，Abstract）
2. 编译期只静态决定 task graph、order、priority 与 FPGA/tile placement；运行期仍由 token-ready 状态动态发射到 tile 内 core。[pdf:E13]（PDF 物理页 4，Section III-A）
3. same-cycle edge 必须留在同一 FPGA、memory-sharing task 必须留在同一 tile，这两条约束既保护性能，也限定了可映射 graph 的形状。[pdf:E15]（PDF 物理页 8，Mapping）
4. selective execution 用 null token 保持因果而不 rollback，在低 activity 的 Multicore 上有效，但在每周期都变化的流水设计上几乎无效。[pdf:E14]（PDF 物理页 6，Section III-D）[pdf:E20]（PDF 物理页 11，Fig. 12）
5. 论文最强结果来自手写 DSL graph；Verilog 路径远慢于 emulator，说明 compiler 与 code reuse 不是配角，而是系统能否兑现硬件潜力的核心。[pdf:E21]（PDF 物理页 10，Table IV）[pdf:E22]（PDF 物理页 11，Verilog 分析）

**3 句话：**

1. Lotus 的 placement 是静态 tile placement，不是静态 core schedule。
2. Lotus 的执行是 runtime token-ready + priority，不是每模拟周期全局 barrier。
3. cycleId、cross-cycle edge 与双版本 buffer 保持周期关系，但论文没有声称完整 old-state→new-state atomic commit。

**1 句话：** Lotus 证明了“静态放置 graph、动态发射 invocation”的多 FPGA task dataflow 可以把一部分 cycle-level simulation 推到 emulator 量级，但性能与适用性高度依赖 graph 可分割性、communication locality 和 compiler quality。

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标设计的 same-cycle dependency graph 能被切成若干都可容纳于单片 FPGA 的连通区域，同时仍保留足够的跨区域 cross-cycle slack。** 论文直接规定每条 same-cycle edge 的两个 task 必须放在同一 FPGA，以免约 200 ns 跨片时延进入 critical path。[pdf:E15]（PDF 物理页 8，Mapping restrictions）基于这一规则可以推出：沿 same-cycle edge 连通的整个 component 会被传递性地限制在同一 FPGA。若一个大 combinational component 超过单片 task/storage/code capacity，当前映射约束不是“变慢”，而是可能无可行解；若放松约束，又会把多次跨片时延直接压到一个模拟周期的 critical path。

论文提供的正面证据是，六个 benchmark 能被映射，且 hierarchical partitioning 显著优于 random；这说明所测 graph 有可利用的 locality。[pdf:E25]（PDF 物理页 9，Table III）[pdf:E23]（PDF 物理页 12，Fig. 16）但论文没有报告 same-cycle connected-component size 分布、编译失败样例、最大 component 相对单 FPGA 容量的余量，也没有系统扫描“从可放置到不可放置”的边界。四个高性能 DSL benchmark 又包含规则流水、systolic array 与作者手写 graph；Verilog 路径已经显示自动生成 graph 的 code locality 和 parallelism 可能很差。[pdf:E03]（PDF 物理页 10，Methodology）[pdf:E22]（PDF 物理页 11，Verilog caveat）如果该假设在一般 SoC 的大 combinational cone、全局仲裁或复杂 bypass/network logic 上不成立，Lotus 的“用更多 FPGA 扩大可模拟设计”这一核心价值会直接受损。

## § 10 — 最小复现实验

一周内最值得复现的不是 8-FPGA 绝对 MHz，而是**静态 placement + 双版本 token runtime 是否在周期重叠、priority 与 selective execution 同时开启时仍严格等价于顺序 SDF 参考模型**。这是可证伪的核心语义点。

- **数据：** 生成三组小 graph。第一组是 Fig. 1 的递推流水扩展版，混合 same-/cross-cycle edge；第二组加入低 activity 区域，使连续多个周期输入不变；第三组用单缓冲 memory 与 `B@N → A@N+1` order edge制造覆盖风险。再给 tile 间 token 注入随机但有限的通信时延。[pdf:E12]（PDF 物理页 2，Fig. 1）[pdf:E11]（PDF 物理页 9，Order Edges）
- **实现：** 写两个 simulator。参考端按每个逻辑周期完整计算 SDF；实验端实现 `(cycleId,taskId)` token、remaining count、偶/奇版本、ready bitmap、priority dispatch 与 null-token selective execution。task 固定映射到 tile，但由 runtime 动态选择 tile 内 core。[pdf:E13]（PDF 物理页 4，执行规则）[pdf:E09]（PDF 物理页 5，Versioning/Priority）
- **测量：** 对随机输入运行至少数千逻辑周期，逐周期比较所有 observable output 与 memory trace；同时记录 task firing 数、null token 数、ready-to-finish makespan、critical-path 延迟和不同 cycleId 同时在飞的 invocation 数。
- **支持标准：** 所有 trace 与顺序参考完全一致；改变 runtime priority 只改变完成时间，不改变结果；selective execution 在低 activity graph 中显著减少 firing，且 side-effect/order-token case 从不被错误跳过。
- **反驳标准：** 任一随机通信延迟导致 cycleId 串扰、旧值复用错误、单缓冲覆盖、priority 改变功能结果，或必须增加全局 per-cycle barrier 才能正确。出现这些结果，就说明论文描述的局部 token/order 规则不足以闭合重叠周期语义。

这个实验不验证 400 MHz、FPGA resource 或 emulator speedup；它只验证最关键的执行语义，并明确区分逻辑 cycle boundary 与全局 atomic commit。

## § 11 — 最强反例设计

最强反例是一类**超出单 FPGA 容量的全局 same-cycle combinational graph**。构造一个参数化的宽 butterfly/permutation network：每个模拟周期注入完全不同的数据，经过多级 same-cycle routing、priority encode 和 global reduction，末端只通过一个 register feedback 到下一周期。把网络做成一个沿 same-cycle edge 连通的 component，并逐步把 task 数、code footprint 和 fan-out 增大到超过一片 FPGA 的可用 task-unit 与 instruction capacity；同时令所有输入每周期变化，使 selective execution 无法省工。

攻击分两路。第一路严格保留论文的 mapping restriction：因为 same-cycle component 不能拆到不同 FPGA，compiler 应在某个规模后无可行 placement，直接反驳“固定 FPGA 数只需以更长时间模拟更大设计”的一般性。第二路放松 restriction 允许 same-cycle edge 跨 FPGA：测量每个模拟周期 critical path 上的跨片 hop 数；若 200 ns 级 link latency 随级数累积，Lotus 的高频 core 与 task throughput 将无法抵消通信。[pdf:E19]（PDF 物理页 6，跨 FPGA latency）

为了排除“只是 partitioner 太差”这一替代解释，应同时给出 component 连通性的图论证明：任意合法切分都会割开 same-cycle edge。为了排除“priority 能救回来”，让所有 ready task 的长链依赖固定；priority 只能重排独立工作，不能缩短必须串行的跨片 hop。最后与同一设计的空间 emulator 或单机软件 reference 比较：若 Lotus 无法映射，或放松约束后每周期时间随跨片级数增长，而 emulator 仍以固定逐周期节拍运行，这就是对 Lotus 核心机制最有力的反例，而不是泛泛的“某 benchmark 慢”。

## § 12 — Follow-up Research Bet

**候选研究押注：Polychronous Lotus——把单一整数 `cycleId` 提升为可组合的多逻辑时钟 actor。** 新问题是：能否在同一多 FPGA task dataflow machine 上，原生组合 cycle-accurate RTL、event-driven microarchitecture 和 transaction-level SystemC actor，同时保持边界交互的因果精确，而不把所有组件强制压到同一个全局模拟周期？这首次可能让一个大系统的不同部分使用不同时间对象：RTL 部分仍以 cycle edge 推进，事件模型用 timestamp frontier，transaction actor 用有界时间区间；跨 actor edge 携带的不是“每周期一个值或 null”，而是带逻辑时钟关系的 causal interval token。

核心机制是把当前 `(cycleId, taskId)` 和偶/奇两版本 invocation state 一般化为 `(clock-domain, causal-frontier, taskId)`。编译器先识别 zero-delay causal component，把它们静态放在同一 FPGA；每个 actor 声明自身从输入 frontier 到输出 frontier 的状态转移关系。task unit 只有在所有入边覆盖同一 causal frontier 时才发射 actor，并允许一个 actor 一次推进一个时间区间。这样，低 activity 或高层模型不再需要为每个空周期发送一串 null token；跨 FPGA link 传输的是更稀疏、语义更强的 frontier token，而紧耦合 RTL 区域仍保留逐周期精度。它改变了时间表示、task state、graph edge 类型、硬件 ready 条件和跨 FPGA 通信对象，而不是在原方法外加一个监测器。[pdf:E13]（PDF 物理页 4，当前 cycleId/token runtime）[pdf:E09]（PDF 物理页 5，双版本状态）[pdf:E14]（PDF 物理页 6，null-token selective execution）

这项押注有两条论文特异依据。方法侧，Lotus 已经证明静态 graph、异步 token、temporal unrolling 与 invocation versioning 可以把逻辑周期和物理执行时间解耦。[pdf:E11]（PDF 物理页 9，Fig. 11）实验侧，跨设备通信占比从 0.57% 降到 0.49% 就能带来 1.7 倍加速，说明“减少跨片因果边的消息频度”可能比继续增加 core 更有价值；而 selective execution 只在低 activity Multicore 上显著获益，说明空周期具有可压缩结构，但当前逐周期 null-token 表示还未把这种结构提升为一等时间对象。[pdf:E23]（PDF 物理页 12，Fig. 16）[pdf:E20]（PDF 物理页 11，Fig. 12）论文结尾也明确提出把 Lotus 扩展到 event-driven microarchitectural simulation、SystemC transaction-level modeling，并与 RTL 混合；本 idea 把这句未来工作变成一个新的时间语义与硬件执行模型，而不只是接入另一种前端。[pdf:E26]（PDF 物理页 13，future work）

最大收益是让多 FPGA 仿真不再只有“全系统每周期前进一步”这一种评价对象，而能研究跨抽象层、跨时间尺度的大系统，并以 frontier 稀疏性而非原始周期数决定通信量。最大科学风险是：一般 RTL 的 zero-delay feedback 与数据相关 event 可能使 causal interval 无法紧凑表示，actor 的状态转移关系可能指数膨胀，最终退化回单周期 token。

首个判别实验应在两片 FPGA 上组合三个组件：cycle-accurate cache-coherence controller、event-driven core cluster、transaction-level DRAM。固定 task code、placement 与 link，比较三种时间表示：当前每周期 token、固定 \(K\)-cycle batching、polychronous causal-frontier actor。三者都与全 cycle reference 比较 output/memory trace；再测跨片 token bytes、task firing 和 wall-clock。只有 causal-frontier 方案在事件密度变化时仍保持精确、并显著优于固定 batching，才支持“新时间对象”而非“只是把 task 做大”的核心机制；若收益与固定 batching 相同或 feedback 迫使全部 actor 回到 cycle token，则该押注失败。

与本论文及其所述 Manticore/emulator 的实质区别在于：Lotus 使用统一 cycleId、0/1-cycle edge 和双版本 invocation；Manticore 依赖 bulk-synchronous cycle 边界；emulator 依赖跨片 lockstep。这里把 problem 从“加速一个统一周期模型”改成“执行由多个逻辑时钟和抽象层组成的因果网络”，并把 representation 从标量 cycleId 改成可组合 frontier。由于本任务未检索附件之外的相关全文，这只是候选判断，不声称 novelty。

**Wild-card alternative：** 把 Verilator 生成的 replicated task 从“每实例一份代码”改写为 `(parameterized code template, state slice, constants)` 三元组，并设计 tile 级共享取指/广播执行，使数千个逻辑 task 复用同一 instruction object；这改变 executable representation 与硬件取指拓扑，直接攻击论文观察到的 instruction-reuse 瓶颈，而不是给现有 runtime 再包一层优化。[pdf:E22]（PDF 物理页 11，Verilog instruction-reuse caveat）
