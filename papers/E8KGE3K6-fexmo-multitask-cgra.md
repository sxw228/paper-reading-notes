# FexMo: Enabling Fuse Execution Mode for Multi-task CGRAs

- 作者：Yufei Yang、Chenhao Xie、Chuliang Guo、Liansheng Liu、Xiyuan Peng、Datong Liu、Yu Peng
- 出处：58th IEEE/ACM International Symposium on Microarchitecture（MICRO ’25）
- 年份：2025
- DOI：10.1145/3725843.3756019
- Zotero key：E8KGE3K6
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文问的是：CGRA 同时运行多个独立任务时，能否不再把 tiles 固定切成互不重叠的空间分区，而让所有任务在时间维度共享整个阵列，同时仍能在 load miss 下保持正确执行和高吞吐？现有 fixed 或 adaptive spatial partition 虽能隔离任务，却会把某个任务暂时用不到的时隙锁死在其分区内；FexMo 把这个浪费重新表述为“时间利用率”问题。论文在摘要中报告，相对 partition execution mode，完整方案平均提高 36.9% tile utilization、取得 1.99× throughput；FexMo-Mapper 的平均 mapping quality 为 conventional mapper 的 2.72×，实现流在 ASAP7 下达到 434 MHz，并报告 1.22× energy efficiency。[pdf:E01]（PDF 物理页 1，Abstract 与 ACM Reference Format）

重要性在于：II（initiation interval）决定流水迭代之间隔多少个周期启动，空间上“已经分到 tile”不代表时间上“每周期都在工作”。如果多任务能填补彼此的 pipeline bubbles，同样大小的 CGRA 可以在不复制计算阵列的前提下提高吞吐。但这种共享也打破了空间分区天然提供的故障隔离：一个任务的 load miss 会因同步配置发射而拖住所有任务，或者在继续发射时让错误数据向后传播。因此，这不是单纯换一个 mapper，而是 architecture 与 mapping 必须共同闭环的问题。论文明确把 distributed checkpoints、NOP override、clock gating 与 inter-DFGs co-scheduling 作为一体化贡献。[pdf:E02]（PDF 物理页 2，Introduction contributions 与 Fig. 1）

## § 2 — 前人工作与不足

论文把已有多任务资源分配分为两类。Fixed spatial partition 离线估算任务需求并在生命周期内保持分区；adaptive spatial partition（文中以 DRIPS、MultiSky 等为代表）根据输入变化或任务创建/销毁调整空间分区。它们解决的是“给每个任务多少 tiles”，却没有让不同任务逐周期复用同一批 tiles。已有 CGRA mapper 则主要优化单个 DFG；architecture-specific 方法依赖特定互连或 tile，architecture-agnostic 方法包括 SA/GA、ILP/SAT 和 ML/RL，但论文认为这些工作没有处理多个独立 DFG 的联合 modulo scheduling。[pdf:E02]（PDF 物理页 2，Introduction 与 contributions）

不足不是“前人忘了共享”这么简单。空间分区保留了任务隔离和简单的运行时语义；改为 fuse execution 后，所有 tiles 同步从同一配置地址取指，任一任务未完成当前 load 就会卡住配置地址。若无视 miss 继续取配置，后继节点会消费无效值。另一方面，若 mapper 只是依次把多个 DFG 塞入空闲时隙，它会让先映射任务占据有利 modulo cycles，后映射任务反复失败并迫使 II 增大。FexMo 因而改变了两个既有假设：运行时不再要求所有任务同步前进；离线映射也不再把每个 DFG 的 schedule 当作彼此独立的既成事实。

## § 3 — 重建作者的思考路径

可以从一个最小例子重建这条路线。两个各有 4 个节点、各运行 1000 次迭代的任务若分别占用 1×2 子阵列，会因缺少本地 register file 产生空洞，II=3，总计 3000 cycles；让二者共享 2×2 阵列后，彼此的节点填入空洞，II 降到 2，总计 2000 cycles。论文又用 2、3、4 个 PolyBench kernels 的初步实验观察到 fuse mode 平均增加 17.7% utilization，并改善 24.9% II。[pdf:E03]（PDF 物理页 3，Fig. 2、Fig. 3 与 Section 2.2）

接下来会自然遇到两个反例。第一，load miss 发生时，全局停顿损失了融合带来的吞吐；不停顿又会传播错误。第二，即使硬件允许异步前进，naïve scheduling 仍可能把 8 个节点排成相邻 modulo cycles 上的 6/2 不平衡，只得到 66.67% utilization 和 II=3；把第二个 DFG 循环平移一个 modulo cycle 后可变为 4/4、100% utilization、II=2。由此，作者分别引出“保存落后任务的执行前沿”和“联合选择各 DFG 的相位偏移”两条设计线。[pdf:E04]（PDF 物理页 4，Fig. 4、Fig. 5 与 Section 2.3）

## § 4 — 核心 Intuition

FexMo 的核心不是把任务切得更细，而是允许不同任务拥有不同的逻辑进度：正常任务继续随全局配置流前进，miss 的任务把自己的进度冻结，并在配置再次回到同一 modulo cycle 时重试。离线端则把各任务 DFG 看成可以循环平移的周期负载，先找让每个 modulo cycle 节点数更均匀的相位组合，再做 placement 与 routing。前者解除“一个 miss 拖住全阵列”，后者避免“共享了阵列却仍把节点挤在同几个周期”。tile 内的 task-specific register、configuration override 与 narrow `Ctrl` 数据路共同把这个直觉落成硬件。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Sections 3.1–3.3）

## § 5 — 具体方法与完整 Pipeline

以两个 loop tasks 融合到同一 CGRA 为例，完整 pipeline 如下。

1. LLVM frontend 从各任务 kernel 提取独立 DFG；mapper 读取 DFG 集合和 CGRA architecture。
2. Inter-DFGs co-scheduling 先分析每个 DFG 在给定 II 下各 modulo cycle 的节点数。除第一个任务固定相位外，其余任务枚举 cyclic shift，形成候选的跨任务节点分布，选择最均匀的 `optimalSchedCase`。[pdf:E06]（PDF 物理页 6，Algorithm 1）
3. Utilization-aware mapper 从 `max(ResMII, RecMII)` 开始构造 MRRG。每个节点用 Static Routing Cost、Used Adjacent Resources Cost 和 Memory Resource Cost 选择 tile，再严格按 `optimalSchedCase` 调度和路由；失败就令 II 加 1，重新生成 schedule 与 MRRG，最终输出带 `TaskID` 的 configurations。[pdf:E07]（PDF 物理页 7，Fig. 8、Algorithm 2 与 Section 4.2）
4. 运行时，memory access monitor 汇总每个 SPM bank、每个 task 的 hit/miss bit，生成窄位宽 `Ctrl`。每个 tile 的原有 operand/register 路径旁增加 task-specific checkpoint registers，并保存 operand 与 `CfgAddr`；当前配置的 `TaskID` 决定读写哪份 task context。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Sections 3.1–3.2）
5. 某任务 miss 后，其后继配置被覆盖为 NOP，对应 tiles clock-gated；其他任务继续执行。当当前 `CfgAddr` 再次等于该任务保存的地址时，`Retry=1`，恢复保存的 operand 并重试 load。Fig. 7 的 II=4 例子中，Task 1 在 cycle 0 miss、cycle 2 的“+”变 NOP、cycle 4 重试命中；与此同时 Task 2 已从 iteration 0 前进到 iteration 1。[pdf:E06]（PDF 物理页 6，Fig. 7 与 Section 3.4）

论文没有报告 RTL source 的公开位置、配置格式的完整位宽、store/atomic 的处理规则、多个 outstanding misses 的状态机或 FPGA 实板结果；这些内容不能从当前 PDF 推定。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有定理式推导，核心数学是 modulo scheduling 的搜索空间与目标函数。

首先，Algorithm 2 以

\[
II_0=\max(ResMII, RecMII),\qquad
ResMII=\frac{\#\text{DFG nodes}}{\#\text{CGRA tiles}}
\]

作为起始 II。`ResMII` 表示平均资源容量至少需要多少周期，`RecMII` 表示 DFG recurrence 对流水间隔的下界；二者取最大值才同时满足资源与依赖。若 placement/schedule/route 失败，就执行 `II ← II+1` 并从联合 schedule 重新开始。[pdf:E07]（PDF 物理页 7，Algorithm 2 lines 1–18）

其次，对任务数 \(T\) 和给定 II，Algorithm 1 枚举约 \(II^{T-1}\) 个相位组合：第一个 DFG 固定，其他每个 DFG 可循环平移 0 到 \(II-1\) 个周期。每个组合先把各 DFG 的 `schedNodeCnts` 相加成 `schedTotalNodeCnts`，再用相邻 modulo cycles 的差构造 `avgDiff`，选择差异最小的组合。论文的 II=2、T=2 例子从 `[6,2]` 的不平衡分布，经一次 cyclic shift 得到 `[4,4]`，`avgDiff` 从 4 降到 0。[pdf:E06]（PDF 物理页 6，Algorithm 1 lines 1–16）

这里有一个复现风险：伪代码写的是 `diff = schedTotalNodeCnts.diff(dim=1)` 和 `avgDiff = diff.sum()/(II-1)`，却没有明确 `diff` 是否取绝对值、平方或固定方向；若直接对有符号相邻差求和，不同位置的不均衡可能相互抵消。Fig. 8 的示例能确定作者想衡量“均匀度”，但不足以唯一确定一般情况下的 score 实现。这是基于证据的批评，不是论文显式承认的限制。

## § 7 — 实验设计与结论

- **融合执行是否提高吞吐与利用率？** 论文选择 16 个 PolyBench static-control inner loops，组成 16 组双任务和 16 组四任务 case；在 4×4/6×6 CGRA 上比较 PartitionBase、会全局阻塞的 FuseBase 与 FexMo。load miss rate 来自 Gem5 L1 data cache miss rate，并把 L1 容量设为对应 CGRA SPM 容量；cycle-accurate simulator 输出 throughput、temporal tile utilization 和 gated cycles。[pdf:E08]（PDF 物理页 8，Tables 2–3 与 Sections 5.2–5.3）答案是：三种场景的平均 utilization 增益为 36.9%；相对 PartitionBase，FuseBase 平均 1.69× throughput，FexMo 平均 1.99×。任务从 2 增到 4 时，FexMo 与 FuseBase 的吞吐差距从 0.23× 增到 0.42×，作者把它归因于更高的 miss competition。[pdf:E09]（PDF 物理页 9，Fig. 9 与 Sections 6.1.1–6.1.3）
- **联合调度是否改善 mapping？** 对同一批 cases 比较 sequential MapperBase 与 FexMo-Mapper，指标是 normalized mapping quality（本质上由更小 II 转换而来）和 mapping time。FexMo-Mapper 在三种场景平均取得 2.72× mapping quality；平均 mapping time 为 40.32 s，而 MapperBase 为 58.02 s。四任务 4×4 场景中，FexMo-Mapper 用 96.64 s 对 MapperBase 的 159.70 s，并取得 4.11× quality。[pdf:E10]（PDF 物理页 10，Fig. 10 与 Section 6.3）
- **硬件代价是否可接受？** 作者用参数化 Verilog 生成 4×4、5×5、6×6 CGRA，加入 FexMo 逻辑，在 ASAP7 上经 Synopsys Design Compiler 与 Cadence Innovus 做 synthesis、placement、routing。三种尺寸都报告 434 MHz；checkpoint registers 平均只占 0.55% area，却平均占总 power 的 37.9%。4×4/5×5/6×6 的总 power 为 88.1/132.9/186.9 mW，checkpoint 部分为 32.4/50.6/72.9 mW；尽管如此，Fig. 11 报告平均 1.22× normalized energy efficiency。[pdf:E10]（PDF 物理页 10，Table 5、Fig. 11 与 Sections 6.2.1–6.2.3）

这些结论不能外推到大于 6×6 的 monolithic CGRA、动态控制流任务、真实片上 SPM/DMA 系统或硅后测量。论文自己建议优先用 NoC 连接多个 4×4 CGRA，而不是直接扩到 8×8/16×16，因为 centralized control 与 mapper search space 可能成为瓶颈。[pdf:E11]（PDF 物理页 11，Sections 7.1–7.2）

## § 8 — Take-aways

**5 句话：**

1. FexMo 把多任务 CGRA 的优化对象从空间分区改成全阵列的时间复用。
2. 它用 task-specific context 让 miss 的任务停在自己的逻辑进度上，而不停止其他任务。
3. 它用跨 DFG cyclic shift 先平衡 modulo-cycle 负载，再做 placement 与 routing。
4. 在论文的 PolyBench/Gem5/simulator 评测中，这套 co-design 平均带来 36.9% utilization 增益和 1.99× throughput。
5. 代价的主要矛盾不是 area，而是 checkpoint registers 的动态 power 与小规模验证之外的扩展性。

**3 句话：** FexMo 通过“运行时任务进度解耦 + 离线跨 DFG 相位对齐”让多个任务在时间上共享同一 CGRA。实验支持它在 2–4 个静态 loop tasks、4×4–6×6 阵列上的吞吐与 mapping 优势。最需要谨慎的是独立任务、简单 miss/retry 语义与小规模 centralized control 这些边界。

**1 句话：** 这篇论文证明，多任务 CGRA 的空闲周期可以像空间资源一样被重新分配，但前提是 architecture 与 modulo mapper 同时理解“任务身份和任务进度”。

## § 9 — 最脆弱的假设

最脆弱的假设是：一个任务在 load miss 后可以把后续节点替换成 NOP，并在同一 modulo cycle 重试 load，而不改变程序可见语义。这个假设对独立、静态控制、以 load 为主要不确定延迟来源的 PolyBench loops 较合理；论文的 benchmark 正是 16 个 static-control inner loops，仿真也用 Gem5 的 L1 miss rate 驱动，而不是执行完整的共享内存一致性协议。[pdf:E08]（PDF 物理页 8，Section 5.1–5.2）

实际系统中，store、atomic、I/O、副作用操作、跨任务 producer–consumer 依赖、多个 outstanding misses 或不同 cache-bank 返回次序都可能让“冻结一个任务、其他任务越过它”产生不可逆的可见重排。论文展示了 operand 与 `CfgAddr` 的保存，并通过 NOP 阻止本任务内部错误传播，但没有报告如何回滚已发出的副作用，也没有对跨任务共享状态给出 memory model。因此，现有证据支持的是受控独立任务下的正确性机制，尚不能证明一般多任务共享内存语义。

## § 10 — 最小复现实验

一周内最值得复现的是“checkpoint/NOP/retry 能否在 load miss 下保持结果正确，同时解除无关任务阻塞”，无需先复现完整 mapper。

1. 按 Fig. 7 实现一个 II=4、单 tile、双任务的 cycle-level simulator；Task 1 执行 load→add，Task 2 执行 load→multiply，configuration 带 `TaskID` 与 `CfgAddr`。
2. 实现三种语义：全局 block、无 checkpoint 的持续发射、FexMo 的 per-task saved operand/`CfgAddr` + NOP + retry。
3. 对 Task 1 注入 1–8 cycles 的确定性 miss，并随机化 miss 出现的 iteration；用顺序 CPU 结果作 oracle。
4. 测量两任务完成 cycles、Task 2 在 Task 1 miss 期间的有效进度、错误输出数和 NOP/gated cycles。

若 FexMo 在所有注入下与 oracle 一致，且 Task 2 的完成时间不随 Task 1 的 miss latency 一比一增长，就支持“任务进度解耦”这一核心 claim；若出现错误结果，或 Task 2 仍被等量拖慢，就反驳该 claim。这个实验只验证架构语义，不宣称复现 36.9% 或 1.99× 的全论文平均结果。

## § 11 — 最强反例设计

最强反例不是再挑一个 tile utilization 低的 kernel，而是构造两个通过共享内存形成 producer–consumer 关系的循环：Task A 写入 ring buffer 并更新 atomic tail，Task B 读取 tail 后消费数据；让 A 的数据 load 和 B 的 metadata load 以可控次序 miss，同时保留 store/atomic 的真实可见性。对照组使用顺序一致的 CPU reference 与全局 block CGRA，攻击目标是检查 FexMo 的“异步前进仍保持正确”是否成立。

如果 B 在 A 的 checkpoint 期间越过了尚未提交的数据，或 A 重试后重复/乱序产生副作用，即使 tile utilization 和 throughput 仍好看，也足以推翻核心机制可用于一般多任务的解释。若实现为了通过测试而重新引入跨任务全局等待，则说明吞吐优势依赖“任务之间没有可见依赖”这一更窄前提。论文的 scalability discussion 还指出 monolithic 8×8/16×16 可能使 centralized control 和 mapping search 爆炸；因此可在相同反例上增加 4×4→8×8 延迟模型，区分语义失败与规模导致的时序失败。[pdf:E11]（PDF 物理页 11，Section 7.2）

## § 12 — Follow-up Research Bet

**主 idea：跨任务商图执行（cross-task quotient-DFG execution）。** 新问题不再是“怎样让独立任务共享空闲 tiles”，而是“怎样把多个任务中语义相同的子计算合并为一次执行，并把结果分发给多个任务前沿”。例如感知、控制和通信任务可能都进行相同的坐标变换、滤波前处理或矩阵 tile 读取；现有 FexMo 只把它们的节点错峰放置，仍会重复计算。新系统先把多 DFG 中可证明等价的子图折叠成带 consumer-set 的 quotient DFG，再联合选择相位、placement、multicast route 和共享值的生命周期；task-specific 节点仍保留各自身份，但公共节点只执行一次。

这首次使“跨程序计算复用”成为 CGRA 多任务调度的一等能力，而不只是提高已有节点的占用率。因果链是：识别等价子图 → 折叠重复节点与重复 memory reads → 降低每个 modulo cycle 的必需节点数和片上流量 → 释放 tiles/links 给 task-specific 节点 → 在同一阵列上提高可并发任务数或降低 II。它同时改变了问题定义（从空洞填充到跨任务消冗）、状态表示（从独立 DFG 集合到带 consumer-set 的 quotient graph）、硬件映射（需要多播与共享值生命周期）和实验对象（共享计算比例可控的任务族）。

论文特异依据有两组。方法侧，FexMo 已经把多 DFG 的节点计数放进同一个 modulo-cycle search，并证明 cyclic shift 能把 6/2 分布变为 4/4；Algorithm 2 也已在统一 MRRG 上联合 placement/routing，这为商图而非独立图集合提供了直接接口。[pdf:E06]（PDF 物理页 6，Algorithm 1）[pdf:E07]（PDF 物理页 7，Fig. 8 与 Algorithm 2）实验侧，4-task 场景比 2-task 场景提供更多节点组合，FuseBase/FexMo utilization 从 75.4% 增到 81.9%，说明跨任务组合自由度确实有价值；但现有方案仍只利用“错峰”，没有利用“等价计算可合并”。[pdf:E09]（PDF 物理页 9，Fig. 9 与 Section 6.1.2）

最大研究收益是让 CGRA 从 multi-program temporal sharing 迈向 multi-program computational sharing：在相同功耗预算下，不仅减少 idle cycles，还减少实际运算和数据搬运。最大科学风险是“跨任务等价子图”在真实 workload 中稀少，或因不同精度、exception、memory alias 与执行速率而无法安全复用；一旦等价性条件过严，quotient graph 会退化回原始 FexMo，新增复杂度没有收益。

首个证伪实验应生成三组总节点数、单任务 II 和 memory footprint 匹配的 task pairs，仅改变可共享子图比例（0%、25%、50%）。比较原始 FexMo、quotient-DFG 方案和“只做更均匀调度但不合并节点”的强 baseline，测 II、执行节点数、NoC/片上 link traffic、throughput 与结果一致性。若收益只是更好的负载均衡，那么在平衡程度匹配后不应随共享比例单调增长；只有当执行节点数与流量随共享比例下降、且 throughput 额外提高，才支持“计算复用”机制。与论文所述 DRIPS/MultiSky 的 spatial repartition、现有 single-DFG mappers，以及 FexMo 的 independent-DFG phase shift 相比，这个候选在 problem、mechanism、representation 和 experimental object 上都不同。[pdf:E12]（PDF 物理页 12，Section 8 与 Section 9）由于本任务没有联网检索 2025 年后相关工作，这里只作候选判断，不声称 novelty。

**Wild-card alternative：** 把多个 4×4 CGRA 组成 phase-addressed dataflow mesh，让一个任务的不同 DFG regions 以 modulo epoch 为单位跨芯粒流动，从“多任务共享单阵列”改成“任务波前共享网络化微阵列”，其核心设计变量是拓扑、epoch 与通信路由，而不是商图复用。
