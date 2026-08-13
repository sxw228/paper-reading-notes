# CRUSH: A Credit-Based Approach for Functional Unit Sharing in Dynamically Scheduled HLS

作者：Jiahui Xu；Lana Josipović  
出处：Proceedings of the 30th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 1（ASPLOS ’25）  
年份：2025  
DOI：10.1145/3669940.3707273  
Zotero key：QGBJPJEI  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 这篇论文解决的问题是：在 dynamically scheduled HLS（动态调度高层综合）生成的握手式 dataflow circuit（数据流电路）中，怎样让多个操作共享昂贵的 functional unit（功能单元），同时不引入死锁，并尽量保持共享前的 initiation interval，II（启动间隔）与执行性能。动态数据流电路能够在控制流或内存访问难以静态预测时按 token 就绪情况推进，但其代价是硬件资源开销高；朴素共享又会让一个暂时无法排出的结果堵住共享流水线，形成 head-of-line blocking（队首阻塞）和循环依赖。[pdf:E01]（PDF 物理页 2，Abstract 与 §1）[pdf:E02]（PDF 物理页 4，Fig. 1 与 §3）

这个问题的重要性不是“省一点面积”，而是决定设计能否放进 FPGA。论文把 `gesummv` 内层循环展开 75 倍后，在目标 Kintex-7 上，无共享版本需要 `790/600` 个 DSP，即容量的 `132%`；采用 CRUSH 后只用 `60/600` 个 DSP，即 `10%`，同时 LUT 和 FF 也从 `76k/101k`、`115k/202k` 降到 `46k/101k`、`45k/202k`。[pdf:E03]（PDF 物理页 10，Table 1）这说明功能单元共享可以把“根本无法实现”的并行设计变成可落地设计，并释放资源给同一 FPGA 上的其他计算。

**基于证据的推断。** CRUSH 的价值在于同时处理三层约束：用 credit 保证局部流控安全，用 dependency-aware priority（依赖感知优先级）避免无谓串行化，再用可扩展图分析替代逐个候选方案的昂贵全局性能求解。因此，它不仅是一个 sharing wrapper（共享封装），也是一套从候选分组、仲裁、buffer/credit 配置到 RTL 映射的编译策略。[pdf:E04]（PDF 物理页 6，Fig. 3、Eq. 1 与 §4.3）[pdf:E05]（PDF 物理页 9，Algorithm 1–2）

## § 2 — 前人工作与不足

**论文直接陈述。** 标准 HLS 通常依赖编译期可预测的控制和内存行为；动态数据流 HLS 则让计算单元依据 valid-ready handshake（有效-就绪握手）在运行时推进。功能单元共享本身是经典 HLS 优化，但作者认为，已有 dataflow sharing 工作多数只覆盖有限场景；据作者所述，最接近的工作是 Josipović 等人的 *Resource Sharing in Dataflow Circuits*，它既指出朴素共享会死锁，也用 total token order（token 全序）来规避死锁。[pdf:E06]（PDF 物理页 3，贡献列表与 §2.1–§2.2）

该 prior method 的第一个不足是**安全性以执行顺序保守化为代价**。Fig. 2 的例子中，若强制 `M1, M3, M1, M3, …` 的全序，下一次 `M1` 必须等待前一迭代的 `M3` 启动，形成长度为 4 个 cycle 的依赖环，使可达 II 从理论上的 `2` 恶化为 `4`；允许 out-of-order access（乱序访问）则可以维持 II=`2`。[pdf:E07]（PDF 物理页 5，Fig. 2 与 §3）这直接削弱了 dynamically scheduled circuit 原本依赖运行时就绪性获取并行度的优势。

第二个不足是**优化成本高**。In-order baseline 需要反复求解 MILP 来评估共享决策；在 Table 2 的基准集合上，CRUSH 相对 In-order 平均把优化时间降低 `90%`，同时进一步减少 `12%` DSP、`15%` FF 和 `7%` Slice。[pdf:E08]（PDF 物理页 11，Table 2）第三个不足是**绑定 basic block，BB（基本块）组织**：In-order 依赖 BB 次序，而较新的 fast-token dataflow circuit 不保留这种组织，因而该方法不能直接应用；CRUSH 的局部 credit 机制不依赖 BB，作者把未修改的 CRUSH 接入 fast-token 电路后仍获得资源下降。[pdf:E09]（PDF 物理页 13，Table 3、Fig. 11 与 §6.5）

## § 3 — 重建作者的思考路径

以下是**基于论文证据的逆向重建**，不是作者逐句给出的研究日记。

第一步，先看到一个结构性矛盾：长延迟 floating-point unit（浮点单元）在 II 大于 1 的循环中常常没有满载，因此共享有明显空间；但 dataflow circuit 没有中央调度器，任一结果被下游堵住，都可能反向阻塞共享单元中的其他操作。[pdf:E10]（PDF 物理页 3，§2.1 的 token occupancy 定义）[pdf:E02]（PDF 物理页 4，Fig. 1b 的队首阻塞链）

第二步，把死锁拆成两个互不相同的来源。其一是 shared unit 与**后继**之间的队首阻塞：某操作的结果没有可用输出槽，挡住其他操作的结果。其二是 shared unit 与**前驱**之间的错误仲裁依赖：固定轮转若等待一个尚未出现的请求，会同时挡住真正可运行、且可能生成该请求所需数据的操作。[pdf:E02]（PDF 物理页 4，Fig. 1b–1e）

第三步，从 interconnect（互连）中的 credit-based flow control（基于信用的流控）抽取一个局部不变量：只有在目标输出容量已经被 credit 预留时，操作才能进入共享流水线。这样每个在途结果都“带着自己的落脚点”，共享单元头部不需要等待一个不存在的 buffer slot。[pdf:E11]（PDF 物理页 5，§4.1）

第四步，意识到 correctness（正确性）和 performance（性能）必须分开处理。credit 解决结果能否排出；仲裁器则不能把“优先级”实现成“必须轮到某人”，而应当在高优先级请求缺席时立即让低优先级请求运行。随后，优先级仍要服从数据依赖，否则即使不死锁，也可能把 II 从 `2` 拉到 `3`。[pdf:E04]（PDF 物理页 6，§4.2–§4.3 与 Fig. 3）[pdf:E12]（PDF 物理页 7，Fig. 4）

第五步，面对组合爆炸，不再穷举每种共享方案，而把“哪些操作能共享、谁先运行”压缩成 SCC（strongly connected component，强连通分量）、拓扑次序、最大路径距离和平均 occupancy 的图问题。Fig. 5 先给出一个关键反例：两个 operation 若在同一 SCC 中总是同时就绪，则任何 priority 都无法保持原 II，说明 grouping 必须先排除这种结构。[pdf:E13]（PDF 物理页 7，Fig. 5）由此形成两个 heuristic（启发式）：Algorithm 1 贪心合并 sharing group，Algorithm 2 按 SCC graph 的拓扑顺序整理访问优先级。[pdf:E14]（PDF 物理页 8，§5.2–§5.4）[pdf:E05]（PDF 物理页 9，Algorithm 1–2）

## § 4 — 核心 Intuition

CRUSH 的核心是：不要用一个全局执行全序来“管住”共享单元，而要给每个共享操作一套独立 credit，让它只有在自己的结果出口已经预留容量时才能发射。[pdf:E11]（PDF 物理页 5，§4.1）共享单元的仲裁使用可跳过缺席请求的 priority，而不是固定轮转，因此既不人为制造前驱依赖，也保留 out-of-order access。[pdf:E02]（PDF 物理页 4，Fig. 1d–1e）最后再用 SCC 与 occupancy heuristic 排除会破坏 II 的组合，使安全机制与性能选择彼此解耦。[pdf:E14]（PDF 物理页 8，§5.2–§5.4）

## § 5 — 具体方法与完整 Pipeline

本文对象是 clocked handshake dataflow circuit，不是 EMT 数值仿真：没有微分方程离散、开关器件事件处理或多速率积分；这里的“时间推进”是 cycle、pipeline latency 和 II，事件是 token/handshake 的到达与阻塞。电路由 fork、join、merge、mux、branch、buffer 等单元组成，channel 传递 data token 与 valid-ready 信号。[pdf:E10]（PDF 物理页 3，§2.1）

完整 pipeline 如下。

1. **输入分析。** 编译器取得 dataflow graph、performance-critical CFC（choice-free circuit，无条件分支子电路）、每个 operation 的类型与 latency、目标 II、token occupancy、候选共享操作，以及目标 FPGA 上 shared unit 与 wrapper 的资源成本。论文主要共享 floating-point adder/multiplier；可据正文复原的精确浮点位宽未报告，因此不应自行假设。[pdf:E10]（PDF 物理页 3，§2.1）[pdf:E15]（PDF 物理页 10，§6.1）

2. **构建 dependency abstraction。** 对每个关键 CFC 求 SCC，并把 SCC 压缩成 DAG。Algorithm 1 初始时令每个候选操作独占一个 group，再贪心尝试合并。[pdf:E14]（PDF 物理页 8，§5.2）[pdf:E05]（PDF 物理页 9，Algorithm 1）

3. **筛选 sharing group。** 合并必须通过三类规则：R1 要求 operation type 相同；R2 要求一个关键 CFC 中该组 operation 的 occupancy 总和不超过 unit capacity；R3 用同一 SCC 内到候选操作的最大距离，排除总是同时就绪、因而无论谁优先都会损害 II 的组合。通过规则后，还要确认合并确实降低 Eq. 2 的资源成本。[pdf:E14]（PDF 物理页 8，§5.2）[pdf:E05]（PDF 物理页 9，Algorithm 1）

4. **生成 access priority。** Algorithm 2 把 group priority 表示为 operation 列表，并类似 bubble sort 地比较相邻 operation；若二者位于同一 CFC 的不同 SCC，则让上游 SCC 中的 operation 优先。Fig. 4 展示了原因：当 `M2` 依赖 `M1` 时，`M1 ≺ M2` 能维持 II=`2`，反向优先级会把 II 增至 `3`。[pdf:E12]（PDF 物理页 7，Fig. 4）[pdf:E05]（PDF 物理页 9，Algorithm 2）

5. **实例化 sharing wrapper。** 每个 operation `op_i` 前放置一个 join，将 operands 与 credit counter `CC_i` 同步；priority merge 与 operand mux 把被选请求送进 shared unit；condition buffer 记住请求来源；branch 把结果送往对应 `OB_i` output buffer；lazy fork 只有在结果已被后继接受、输出槽真正释放后，才把 credit 退回 `CC_i`。[pdf:E04]（PDF 物理页 6，Fig. 3 与 §4.3）

6. **配置 buffer 与 credit。** correctness 要求每个 operation 的初始 credit 数不超过自己的 output-buffer slot 数；performance 配置则使用 occupancy 加一个额外 credit。buffer slot 因此既是存储，也是每个已发射结果的空间预留。[pdf:E04]（PDF 物理页 6，Eq. 1）[pdf:E16]（PDF 物理页 9，Eq. 3 与 §5.4）

7. **运行时例子。** 在 Fig. 1 的 `M2/M3` 共享中，二者各有一个 credit。`M2` 发射后若结果尚未离开，其 credit 变为 0，因此新的 `M2` 被挡在 wrapper 输入；`M3` 仍有 credit，能够越过 `M2` 运行。由于每个发射 token 都已有自己的输出槽，head token 不会因目的 buffer 满而卡死；结果离开后，credit 才返回。[pdf:E02]（PDF 物理页 4，Fig. 1b–1c）[pdf:E11]（PDF 物理页 5，§4.1）

8. **输出与执行平台。** 输出是减少了 physical functional unit、增加局部 wrapper/credit/buffer 逻辑的 RTL dataflow circuit。论文在 Dynamatic 中生成和优化电路，用 ModelSim 统计 cycle 并核对结果/死锁，用 Vivado 2019.1 对 Kintex-7 `xc7k160tfbg484-1` 做 place-and-route，目标 clock period 为 `6 ns`；MILP 使用 Gurobi 11.0.3，timeout 为 `2 min`。[pdf:E15]（PDF 物理页 10，§6.1）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有复杂定理，但有四个决定机制是否成立的数学对象。

**1. Occupancy：把 latency 换成平均容量需求。** 对 operation `op`，论文定义

\[
\Phi_{op}=\frac{lat_{op}}{II_{CFC}}.
\]

`lat_op` 是流水线 latency，`II_CFC` 是所在 CFC 的启动间隔。直觉是：如果一个 latency 为 4 cycle 的单元每 2 cycle 接收一次新迭代，则稳态平均有 2 个 token 占据该单元；多个 operation 共享时，它们的 occupancy 之和不能超过 shared unit capacity。[pdf:E10]（PDF 物理页 3，§2.1）这一量是 Algorithm 1 的 R2 与后续 credit 配置的共同输入。[pdf:E05]（PDF 物理页 9，Algorithm 1）

**2. Deadlock-safety 不变量：每个在途结果都有预留出口。** 对每个共享 operation `i`，论文要求

\[
N_{CC,i}\leq N_{OB,i},\qquad \forall i. \tag{1}
\]

其中 `N_CC,i` 是初始 credit 数，`N_OB,i` 是该 operation 输出 buffer 的 slot 数。[pdf:E04]（PDF 物理页 6，Eq. 1 与 Fig. 3）每次发射消耗一个 credit，结果真正离开 output buffer 后才返还，所以“可用 credit + 尚未退休的该 operation token”保持为初始 credit 总量。只要初始 credit 不多于目的输出槽，系统就不会允许多于可容纳数量的结果进入共享流水线；这就是消除 shared-unit head-of-line blocking 的工程含义。这里是基于作者机制描述重述的不变量解释，不是论文给出的形式化证明。

**3. Sharing 是否值得：unit 节省与 wrapper 增长的离散权衡。** 对某类 operation `T`，论文使用

\[
C_T\,|groups|+\sum_{G_i\in groups}C_{WP}(|G_i|). \tag{2}
\]

第一项是剩余 physical unit 的总成本，group 越少越低；第二项是各 sharing wrapper 的成本，group 越大，merge、mux、branch、buffer 与仲裁越复杂。[pdf:E17]（PDF 物理页 6，Eq. 2 与 §4.3）因此“尽可能多人共享一个单元”并非总是最优：例如便宜的 integer adder 可能比 wrapper 还便宜，Algorithm 1 只在合并降低该成本时接受合并。

**4. Performance credit：满载需求再加一个返回延迟槽。** 论文给出

\[
N_{CC,op}=\Phi_{op}+1. \tag{3}
\]

其中 `\Phi_op` 个 credit 用来保持 shared unit 利用率，额外一个 credit 覆盖结果暂留 output buffer 与 credit 返回的 latency。[pdf:E16]（PDF 物理页 9，Eq. 3 与 §5.4）作者进一步论证：一个 operation 因其他 group member 被推迟的最长时间为 `|G|-1=II-1`，所以最坏情况下每个 II 至少收到一个返还 credit，`\Phi_op+1` 足以维持该 operation 每 II 发射一次。[pdf:E18]（PDF 物理页 10，Eq. 3 的充分性说明）正文没有在该处明确给出 `\Phi_op` 非整数时的取整规则；最小复现应以实现代码为准，而不能自行选择 floor 或 ceil。

**数学边界。** Eq. 1 是局部容量安全条件；Eq. 3 与 R2/R3 是保持 II 的 heuristic timing argument。论文没有给出对任意 variable-latency unit、任意 token arrival trace 或任意有限 buffer 网络的全局吞吐定理，因此不能把实验中的“无死锁且性能近似不变”外推成普适形式化保证。

## § 7 — 实验设计与结论

**问题 1：共享是否真的决定 FPGA 能否容纳设计？ → 实验：** 把 `gesummv` 内层循环展开 75 倍，在同一 Kintex-7 上比较 no sharing 与 CRUSH 的综合资源。**答案：** no sharing 需要 `790` 个 DSP，而器件只有 `600` 个；CRUSH 用 `60` 个 DSP 后可以放入，说明在高并行展开下 sharing 是可实现性的必要条件，而非边际优化。[pdf:E03]（PDF 物理页 10，Table 1）

**问题 2：相对完全不共享，CRUSH 能否大幅省资源且基本不损失性能？ → 实验：** 在 `atax、bicg、gsum、gsumif、2mm、3mm、symm、gemm、gesummv、mvt、syr2k` 上比较 Naive 与 CRUSH，记录 functional-unit count、DSP/Slice/LUT/FF、clock period、cycles、execution time 与 optimization time。**答案：** 平均相对 Naive，CRUSH 减少 `66%` DSP、`32%` FF、`17%` Slice、`6%` LUT；execution time 平均增加 `1%`，optimization time 增加 `47%`，但正文说明通常仍在约 1 秒量级。[pdf:E08]（PDF 物理页 11，Table 2）[pdf:E19]（PDF 物理页 11，Fig. 7 与 §6.3）

**问题 3：相对 prior In-order，CRUSH 是否同时得到更多 sharing opportunity 与更低编译成本？ → 实验：** 在同一 benchmark、同一性能目标下比较 total-order In-order 与 CRUSH。**答案：** CRUSH 平均再减少 `12%` DSP、`15%` FF、`7%` Slice、`3%` LUT，把 optimization time 降低 `90%`，execution time 还平均降低 `4%`；作者把部分 cycle 改善归因于 CRUSH 消除了 shared pipeline 的 head-of-line stall，而不是预期中的算法性加速。[pdf:E08]（PDF 物理页 11，Table 2）[pdf:E19]（PDF 物理页 11，Fig. 8 与 §6.3）

**问题 4：wrapper 自身会不会吃掉节省？ → 实验：** 单独综合不同 group size 的 floating-point adder 与 wrapper，并拆分 LUT/FF 来源。**答案：** CRUSH 与 In-order wrapper 的总资源相近；随着 group size 增长，LUT 成本上升，group size 为 7 时 output buffer 约占 sharing overhead 的 `50% LUT`。共享还会增加 combinational path，论文指出 group 很大时 clock-period overhead 变明显，`gsumif` 是一个例子。[pdf:E20]（PDF 物理页 12，Fig. 9–10 与 §6.4）这说明论文的资源收益主要来自昂贵 FP unit，而不是 wrapper 天生廉价。

**问题 5：方法是否依赖 Dynamatic 的 BB 组织？ → 实验：** 把未修改的 CRUSH 接入不以 BB 组织 unit 的 fast-token dataflow HLS，并与 sharing 前电路比较。**答案：** 平均减少 `66%` DSP、`29%` FF、`14%` Slice、`7%` LUT，execution time 的平均变化为 `-0%`，optimization time 增加 `21%`；Fig. 11 中方案整体 Pareto-optimal 或 Pareto-dominant。[pdf:E09]（PDF 物理页 13，Table 3、Fig. 11 与 §6.5）这支持“对控制流组织方式较独立”，但只覆盖两种 dataflow generation strategy，不能等同于对所有 HLS 架构普适。

**问题 6：功能正确性和死锁如何检查？ → 实验：** 作者用 ModelSim 获取 cycle count，确认 RTL 与 C code 输出一致且测试中不死锁，再用 Vivado place-and-route 得到资源和最大频率。[pdf:E15]（PDF 物理页 10，§6.1）**答案：** 所报告 benchmark 均通过这些检查；但证据是 benchmark-level simulation 与综合结果，不是对所有输入/状态的 model checking 或机械化证明。

实验外推范围应受以下设置约束：目标器件是单一 Kintex-7，clock target 为 `6 ns`；共享对象主要是固定长延迟 floating-point arithmetic unit；所有测试 kernel 都因 floating-point loop-carried dependency 而有 II>`1`；MILP timeout 为 `2 min`。[pdf:E15]（PDF 物理页 10，§6.1）Artifact Appendix 还说明 place-and-route 资源数可能受 MILP 非确定性影响，复现时应更看重 reduction ratio，而不是要求每个 LUT/FF 完全相同。[pdf:E21]（PDF 物理页 14，Appendix A.6）

## § 8 — Take-aways

**5 句话。** 1. CRUSH 用 per-operation credit 把“是否能安全发射”转化为“目标输出是否已预留容量”，从局部上消除共享流水线的队首阻塞。[pdf:E11]（PDF 物理页 5，§4.1） 2. 它用可跳过缺席请求的 priority 代替固定轮转，因此不需要用全局 token 全序换取安全。[pdf:E02]（PDF 物理页 4，Fig. 1d–1e） 3. SCC、拓扑次序与 occupancy heuristic 让编译器能快速决定 group 和 priority，而不必对每个候选反复求解 MILP。[pdf:E05]（PDF 物理页 9，Algorithm 1–2） 4. 在论文的固定浮点 benchmark 上，CRUSH 相对 In-order 平均少用 `12%` DSP、`15%` FF，并把优化时间降低 `90%`。[pdf:E08]（PDF 物理页 11，Table 2） 5. 主要边界是 wrapper 的 LUT/critical-path 增长，以及静态 occupancy 对 variable-latency、burst traffic 的覆盖不足。[pdf:E20]（PDF 物理页 12，Fig. 9–10 与 §6.4）

**3 句话。** 1. CRUSH 把 shared functional unit 变成一组拥有独立出口配额的虚拟通道，而不是一个受全局顺序约束的单队列。 2. correctness 由 credit-buffer invariant 支撑，performance 由 dependency-aware heuristic 近似维护。[pdf:E04]（PDF 物理页 6，Eq. 1、Fig. 3） 3. 论文证明了这种分层设计在所测 FPGA/HLS 流程中有效，但没有证明它对任意动态 latency 和 token trace 都性能无损。

**1 句话。** CRUSH 的关键贡献是用局部 credit 保留动态调度的乱序性，再用图启发式把这一机制变成可综合、可扩展且资源收益显著的 HLS 优化。

## § 9 — 最脆弱的假设

最脆弱的假设是：**静态 latency、平均 occupancy 与 SCC/topological dependency 足以代表运行时 contention（争用）的时序结构。** Grouping R2 使用 `\Phi=lat/II` 的平均占用，priority 由 SCC 拓扑次序决定，credit sizing 再假设一个 operation 最多被其他 `|G|-1` 个成员各推迟一次，因此 `\Phi+1` 足够。[pdf:E10]（PDF 物理页 3，occupancy 定义）[pdf:E14]（PDF 物理页 8，§5.2–§5.4）[pdf:E16]（PDF 物理页 9，Eq. 3）

这个假设在真实动态电路中可能失效，因为相同平均 occupancy 可以对应完全不同的 arrival correlation（到达相关性）：请求均匀交错时几乎无争用，数据相关 branch 让请求成簇到达时却会形成长队；variable-latency divider、memory-dependent unit 或多 phase loop 还会让实际 service time 偏离静态 `lat_op`。若高优先级 operation 的 burst 与低优先级反馈路径重叠，后者的等待可能远大于平均模型预期，II 或 tail latency 会显著恶化。

论文为该假设提供的证据是：固定长延迟 floating-point benchmark 上，两个不同 dataflow HLS 组织中都观察到接近不变的 execution time，并通过 simulation 验证无死锁。[pdf:E15]（PDF 物理页 10，§6.1）[pdf:E09]（PDF 物理页 13，Table 3 与 Fig. 11）缺少的证据是 variable-latency functional unit、强 burst/相关分支 trace、per-operation starvation/tail-wait 分布，以及跨器件/更高频率约束的测试。

若该假设不成立，Eq. 1 所表达的局部容量安全仍可能成立，因此电路未必死锁；但论文更有工程价值的“尽量共享且不伤 II”会直接失效，CRUSH 可能把平均看似空闲、峰值却高度同步的 operation 合并，从而以少量 DSP 节省换来不可接受的吞吐下降。

## § 10 — 最小复现实验

一周内最有价值的最小复现不是跑完所有表，而是复现 `gsum` 与 `gsumif`，因为这两个 case 最清楚地区分 CRUSH 的 out-of-order sharing 与 In-order baseline。

**环境。** 使用论文 artifact 的 Ubuntu 22.04 Docker 流程，准备至少 `32 GB` memory 与约 `180 GB` disk，安装 Vivado 2019.1、ModelSim 20.1 和 Gurobi 11.0.3。Artifact Appendix 估计准备约 `2.5 h`、完整实验约 `4 h`，并提供自动生成 Tables 1–3/Figures 7–11 的脚本。[pdf:E21]（PDF 物理页 14，Appendix A.1–A.5）

**实现与比较。** 对两个 kernel 分别生成 Naive、In-order、CRUSH 三个 RTL：先用 ModelSim 检查输出与 C reference 一致并运行到完成；再按论文设置对 Kintex-7、`6 ns` target 做 place-and-route；记录 functional-unit count、DSP/LUT/FF、CP、cycles、`CP×cycles` execution time 与 optimization time。[pdf:E15]（PDF 物理页 10，§6.1）

**预期锚点。** `gsum` 中，In-order 是 `5 fadd + 4 fmul、22 DSP、3642 cycles、33.6 s` optimization time，CRUSH 是 `1 fadd + 1 fmul、5 DSP、3642 cycles、1.0 s`；`gsumif` 中，In-order 是 `3 fadd + 2 fmul、12 DSP、3624 cycles、61.4 s`，CRUSH 是 `1 fadd + 1 fmul、5 DSP、3556 cycles、1.2 s`。[pdf:E08]（PDF 物理页 11，Table 2）

**本复现实验的支持判据。** 两个 CRUSH 电路都应输出正确、无死锁；functional-unit/DSP 数应复现相同结构性下降；optimization time 至少应比 In-order 快一个数量级；execution time 应保持在 In-order 的 ±5% 内。LUT/FF/Slice 不要求逐项完全相同，因为 artifact 明确指出 MILP 与综合的非确定性可能造成差异，但 reduction ratio 应接近。[pdf:E21]（PDF 物理页 14，Appendix A.6）

**反驳判据。** 任一 kernel 出现死锁或错误结果，直接反驳 correctness claim；若在相同 clock target 下 CRUSH 不能减少 expensive unit，或 execution time 恶化超过 5% 且无法由综合噪声解释，则反驳“这些代表性 out-of-order case 能在保持性能时得到更多共享”的核心实验结论。

## § 11 — 最强反例设计

我会攻击 performance-preserving heuristic，而不是先攻击较强的 Eq. 1 局部安全不变量。

构造两个**静态描述相同、动态 trace 不同**的 dataflow microbenchmark。二者具有相同 CFC、SCC graph、operation type、标称 latency、II 和 `\Phi=lat/II`，所以 Algorithm 1/2 会给出相同 sharing group 与 priority；区别只在输入数据控制的 branch correlation。Trace A 让两个共享 operation 的请求均匀交错；Trace B 让请求周期性成簇到达，并把低优先级 operation 放在 loop-carried feedback critical path 上，把高优先级 operation 放在非关键前馈路径上。[pdf:E14]（PDF 物理页 8，§5.2–§5.4）[pdf:E05]（PDF 物理页 9，Algorithm 1–2）

再把 shared unit 换成具有数据相关 service time 的迭代式 operation，或用受控 stall 注入模拟 variable latency；保持两个 trace 的长期平均 occupancy 相同，但让 Trace B 的长 latency 与请求 burst 同相。比较四种实现：不共享、CRUSH、相同 group 但 round-robin/fair priority、以及知道未来 trace 的 oracle schedule。测量 steady-state II、throughput、每个 operation 的等待时间分布、99th-percentile latency、output-buffer occupancy 与是否 starvation。

**最有力的反例结果**是：Trace A 中 CRUSH 维持 II，而 Trace B 中 CRUSH 的低优先级反馈 operation 出现长尾等待和 II 大幅上升；不共享与 fair/oracle 版本没有同等退化。因为两者的 SCC 与平均 occupancy 完全相同，这会排除“只是资源不够”的替代解释，直接说明论文采用的静态特征不能识别 arrival correlation。反之，若 CRUSH 在这种相位相关、variable-latency 压力下仍维持吞吐且无 starvation，那么这一反例失败，并显著加强论文未覆盖的外部有效性。

## § 12 — Follow-up Research Bet

**候选判断，不声称已具备文献 novelty：Credit-Routed Functional-Unit Fabric（信用路由功能单元织构）。**

新的研究问题是：能否把 CRUSH 中“每个 operation 的局部 credit counter”提升为一个 chip-level routing primitive（芯片级路由原语），让多个 CFC、多个 loop，甚至多个并驻 kernel 通过一个分布式服务网络共享 floating-point unit，而不再预先固定 local sharing group？这首次可能让昂贵 functional unit 从“某几个 operation 的局部共享资源”变成“全芯片可路由的计算服务”，把跨图区域的 phase diversity 转化为更高全局利用率。

核心机制是把 request/result token 包装为带有 operation type、destination、iteration/causal tag 的 packet，并为每个 destination virtual channel 维护独立 credit。request 只有在其结果出口已获得 credit 时才能进入任一兼容 service unit；distributed matcher 把它发送到空闲 unit；结果按 tag 路由到对应 virtual output queue，credit 在真实消费后沿返回网络释放。因果链是：per-destination credit 预留 egress capacity → virtual channel 隔离不同 consumer 的阻塞 → 任意兼容 unit 可接单 → 不同 CFC/kernel 的 burst 可以在空间上重分配，而不是被一个大 mux/branch wrapper 串在一起。CRUSH 的 Fig. 3 与 Eq. 1 已证明局部 per-destination credit 能把安全性与控制流组织解耦，是这一机制的直接起点。[pdf:E04]（PDF 物理页 6，Fig. 3 与 Eq. 1）

这项押注至少改变四个基本设计变量：物理拓扑从 local wrapper 变成 service network；状态表示从 scalar `CC_i` 变成按 destination/route/stage 划分的 credit vector；hardware mapping 从编译期固定 group 变成运行时可路由的 unit pool；评价对象从单 kernel 的 DSP/II 扩展为多 kernel 的 aggregate throughput、tail latency、routing congestion、buffer amortization 与 fairness。论文的 Eq. 2 和 Fig. 10 显示 wrapper 成本随 group size 增长，group size 为 7 时 output buffer 约占 sharing overhead 的 `50% LUT`，因此把多个局部 wrapper 的 buffer/mux 成本合并为共享网络既有潜在收益，也有明确失败风险。[pdf:E17]（PDF 物理页 6，Eq. 2）[pdf:E20]（PDF 物理页 12，Fig. 9–10 与 §6.4）Table 3 又表明 credit mechanism 已能跨越 BB-organized 与 fast-token 两类 dataflow organization，这为扩大系统边界提供了论文特异的第二个依据。[pdf:E09]（PDF 物理页 13，Table 3 与 §6.5）

最大的研究收益是：当多个 kernel 的 peak demand 不同相时，少量 service unit 可能替代每个局部 group 的峰值配置，并允许系统在 workload 变化时自动重分配算力。最大的科学风险是：routing、matching、tag storage 与长 credit-return loop 的 LUT/FF/critical-path 成本可能超过省下的 DSP/FP pipeline；更严重的是，全局网络可能引入 CRUSH 局部 wrapper 中不存在的新循环依赖，使“虚拟通道 + credit”仍不足以保证 progress。

首个可证伪实验应让三个 CFC 或三个 kernel 同时运行，构造可控的 request phase shift，并固定三种实现拥有完全相同的 physical fadd/fmul 数与总 output-storage budget：原始 local CRUSH、把所有 operation 塞进一个 monolithic large CRUSH group、以及 credit-routed fabric。扫过 producer-consumer 距离、burst correlation 与 phase shift，测量 aggregate throughput、每 kernel tail latency、LUT/FF、routing delay 和 fmax。最强替代解释是“收益只来自更大的 pooling，不来自 credit routing”；因此只有当 fabric 在相同 FU 数、相同 storage、相同请求集合下，持续优于 monolithic large group，且优势随通信距离或 phase diversity 系统变化，才支持新机制；若三者性能相同或 fabric 仅靠更多 buffer 获胜，该押注即被否证。

与源 PDF 中最近的方案相比，这一方向不再用 In-order 的 BB total order，也不再使用 CRUSH 的固定 local group/priority；它也不同于 fast-token delivery，因为后者改变 token 传播方式，而这里改变的是 functional unit 的系统边界、通信拓扑和资源所有权。由于本任务未联网检索相关全文，这一差异仅是相对本论文及其引用脉络的候选判断，不宣称对全部最近工作具有 novelty。

**Wild-card alternative：** 构建 operation-tagged、stage-level mode-polymorphic pipeline（带操作标签的阶段级多态流水线），用每个 pipeline stage 的 vector credit 让 fadd、fmul、FMA 等不同类型 operation 共享同一可重构 datapath，从根本上放宽 Algorithm 1 的 R1“同类型才能共享”约束，而不是扩大同类型 group。[pdf:E05]（PDF 物理页 9，Algorithm 1 的 R1）
