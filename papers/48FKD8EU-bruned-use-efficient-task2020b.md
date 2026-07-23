# Use of efficient task allocation algorithm for parallel real-time EMT simulation

- 作者：Boris Bruned、Pierre Rault、Sébastien Dennetière、Ian Menezes Martins
- 出处：*Electric Power Systems Research*, 189, 106604
- 年份：2020
- DOI：10.1016/j.epsr.2020.106604
- Zotero key：48FKD8EU

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是“怎样把电网切成可并行子网”本身，而是切分完成后更靠近机器执行的一步：怎样把已经形成的 EMT 计算任务分配到多核实时仿真器的处理器上，使每个仿真步都能在硬实时截止时间内完成，同时不过度增加跨处理器通信。作者把它形式化为 Task Allocation Problem（TAP）：任务有估计执行时间，处理器有由仿真步长给出的时间预算，任务之间还有通信边；任何一个处理器超时都会使映射失效，并可能造成实时仿真的数值不稳定。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，是因为 EMT 为了表示电力电子开关和快速电磁暂态，通常需要很小的固定步长；扩大网络规模不能靠“稍后算完”来补救。并行化确实能把更多模型塞进同一时间步，但并行收益取决于最慢处理器和处理器间通信，而不是平均算力。论文把价值落在三个层面：在数秒内完成大网络的自动映射；用精确优化结果判断启发式解是否足够接近最优；最后在带真实控制器的三端 HVDC HIL 中验证映射是否真的守住实时步长。[pdf:E01]（PDF 物理页 1，Abstract、Introduction）

## § 2 — 前人工作与不足

并行 EMT 的前一步已有多条技术路线。传播时延大于仿真步长的输电线可以天然解耦子网；不能靠线路时延解耦时，可用 Compensation/MATE、Hybrid formulation 或 Node Tearing 把网络方程拆成并行任务。论文明确区分“task separation”和后续“task mapping”：前者决定有哪些任务，后者决定每个任务去哪一个处理器。[pdf:E02]（PDF 物理页 2，§2.1–§2.2）

在映射方法上，作者列出 A*、spectral、multilevel 和 evolutionary graph partitioning 等路线。A* 逐层选择局部通信代价较小的任务—处理器对；graph partitioning 则把任务网络视为 Source Graph（SG），把处理器及其连接视为 Target Graph（TG），以加权路径长度为通信目标。已有工作已经在 Software-in-the-Loop 示例中显示 graph partitioning 有效，但论文指出两项缺口：缺少工业规模网络和真实仿真器架构上的系统评估，也缺少与精确解的质量对照。[pdf:E01]（PDF 物理页 1，Introduction）；[pdf:E03]（PDF 物理页 2，§2.3.2 与 Eq. 1）

更关键的不足是，通用 graph partitioning 把负载均衡作为弱约束，而实时 EMT 需要的是每个处理器都严格不超步长。也就是说，一个在图论意义上通信代价很好的分区，仍可能在物理执行时错过 deadline；这正是作者后续调参、随机种子重试和 exact-solution 对照要处理的问题。[pdf:E03]（PDF 物理页 2，§2.3.2 末段）

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为以下链条。第一，实时 EMT 已经能自动把网络拆成任务，但“可拆”不等于“可按时跑完”；真正失败点是最重处理器超时。第二，TAP 是 NP-complete，工业网络含数百到上千任务，逐一枚举不可行，因此必须接受启发式。第三，任务之间的通信天然构成图，而处理器拓扑也构成图，multilevel Recursive Bipartitioning（RB）因此是一个计算量小、已有成熟库实现的候选。第四，通用分图只给弱负载约束，所以不能把“Scotch 返回了一个分区”当成实时可行；必须在映射后检查 deadline，并通过 LIR、策略组合和随机种子改善可行率。第五，小规模实例仍可用 linear programming（LP）求 Pareto front，因而能给启发式质量一个外部标尺。最后，只有放到真实 HIL、让瞬态期间的实际执行时间也不越过步长，才算工程闭环。[pdf:E02]（PDF 物理页 2，TAP 定义）；[pdf:E05]（PDF 物理页 3，§3.1.1）；[pdf:E06]（PDF 物理页 4，§3.1.2–§3.2）

这是基于论文结构重建的推理，不是作者逐字声明的发现过程。

## § 4 — 核心 Intuition

核心直觉是：把“计算重的任务尽量摊匀”和“通信重的任务尽量放近”同时编码进图映射，但实时可行性首先由最重处理器是否越过步长决定。multilevel RB 先压缩图、在小图上递归二分，再逐级展开并局部修正，因此能用很短时间找到高质量候选；随后用偏向 balance 的策略和严格的映射后 deadline 检查，把通用分图结果变成可用于实时 EMT 的分配。[pdf:E05]（PDF 物理页 3，§3.1.1）

物理上，它不是让单个 EMT 方程算得更快，而是改变同一仿真步内计算与通信在各核之间的空间分布，使关键路径不被某一个过载处理器拖过 deadline。

## § 5 — 具体方法与完整 Pipeline

以一组已经由 EMT 工具拆出的网络任务为例，完整 pipeline 如下：

1. **形成两个图。** SG 的顶点是 EMT 任务，顶点权重是任务的估计执行时间；SG 边权 \(w_i\) 表示任务间通信。TG 的顶点是处理器，边表示处理器间通信路径。算法最小化源边映射到 TG 路径后的加权长度 \(\min\sum_i w_i|\rho_i|\)。[pdf:E03]（PDF 物理页 2，Eq. 1 与其上下文）
2. **执行 multilevel RB。** 外层 coarsening 先把大图缩小；RB 递归二分 SG 与 TG；每个小分区内再 coarsen，并用 Greedy Graph Partitioning Algorithm（GPA）完成二分；uncoarsening 阶段恢复原图并做局部后处理。[pdf:E05]（PDF 物理页 3，§3.1.1）
3. **选择策略。** Quality 更偏向降低通信目标，可能更慢且更不均衡；Balance 更偏向处理器负载均衡，并在最后用 Exactifier（EX）控制 Load Imbalance Ratio（LIR）。作者还构造 Specific 策略：保留 Quality 骨架、加入 EX、降低外层 coarsening 下界并增加 GPA 迭代，因为输电网图只有数千节点，允许多花一点搜索时间。[pdf:E05]（PDF 物理页 3，策略说明）；[pdf:E07]（PDF 物理页 4，§3.2.2）
4. **做实时可行性检查。** 通用分图过程本身没有给每个处理器施加强 deadline；映射后才检查处理器总执行时间。若某核超步长，就增加一个处理器并重新分区，直到找到有效映射或没有更多处理器可用。[pdf:E06]（PDF 物理页 4，§3.1.2）
5. **调节弱约束与随机性。** 通过减小 \(\delta\) 收紧 LIR，通过不同随机种子改变 GPA 的起始节点；每轮种子搜索后若仍无解，再增加处理器。随机种子能改善某些实例，但作者明确说它不能保证有效解。[pdf:E07]（PDF 物理页 4，§3.2.1–§3.2.3）
6. **离线验证并进入实时运行。** 小实例用 LP 构造 LIR–通信代价 Pareto front，判断 heuristic 解离 exact 解有多远；选定映射后，在 HYPERSIM/OP5031 上以固定步长运行 HIL，并观察稳态与瞬态执行时间。[pdf:E11]（PDF 物理页 6，Fig. 5、Table 5–6 与 §4.1）；[pdf:E13]（PDF 物理页 7，§4.2）

论文实际平台是多核 CPU 实时仿真器；HIL 案例中的一类 MMC valve model 部分运行在 FPGA 上，但论文没有把 task-allocation 算法实现到 FPGA，也没有报告该算法的 FPGA 资源、位宽或时序。因此不能把本文外推成“FPGA 任务调度器”。[pdf:E11]（PDF 物理页 6，§4.1）；[pdf:E12]（PDF 物理页 7，Fig. 6–7）

## § 6 — 核心数学推导

先看通信目标。源边 \(i\) 被映射到 TG 上的最短路径边集合 \(\rho_i\)，\(w_i\) 是该源边的通信权重，通用分图目标为

\[
\min \sum_i w_i\lvert\rho_i\rvert .
\]

它的工程含义是：通信越重的任务对，越应落在同一处理器或相邻处理器上。[pdf:E03]（PDF 物理页 2，Eq. 1）

为了得到可比较的 exact solution，作者定义 allocation 变量 \(x_{ij}\)：任务 \(i\) 分到处理器 \(j\) 时为 1；以及 dilation 变量 \(\rho_{ij}^{kl}\)：通信任务对 \(\{i,k\}\) 分别落到不同处理器 \(j,l\) 时为 1。LP 的双目标写成负载不均衡与跨处理器通信代价之和：

\[
\min\ \frac{1}{T}\sum_j\left|\bar T-\frac{1}{\mu}\sum_i t_i x_{ij}\right|
+\sum_{\{i,k\}}\sum_j\sum_{l\ne j}w_{ik}\rho_{ij}^{kl},
\]

其中 \(T\) 是全部任务评估时间，\(\bar T\) 是每处理器平均时间，\(\mu\) 是时间步约束，\(t_i\) 是任务 \(i\) 的评估执行时间，\(w_{ik}\) 是任务 \(i,k\) 的通信权重。[pdf:E09]（PDF 物理页 5，Eq. 2）

约束为

\[
\forall i,\ \sum_j x_{ij}=1;\qquad
\forall j,\ \sum_i t_i x_{ij}\le \mu ,
\]

\[
\forall\{i,k\},\forall j,l\mid j\ne l,\quad
\rho_{ij}^{kl}\ge x_{ij}+x_{kl}-1 .
\]

第一项保证每个任务恰好分配一次；第二项把每个处理器的任务时间总和硬限制在仿真步长内；第三项把“任务对跨处理器”与通信变量连接起来。作者把目标的两部分分别记为 LIR 与 Communication Cost（CC），再以 \(\alpha\mathrm{LIR}+\beta\mathrm{CC}\)、\(\alpha+\beta=1\) 扫描权重，得到离散 Pareto front。[pdf:E10]（PDF 物理页 5，Eq. 3–6）；[pdf:E11]（PDF 物理页 6，Eq. 7、Fig. 5）

这里最重要的数学—工程差异是：LP 把 \(\sum_i t_i x_{ij}\le\mu\) 写成硬约束，而 Scotch heuristic 的 LIR 只是弱约束。因此 LP 主要用于小实例的质量标尺，不是大工业网络在线求解器。

## § 7 — 实验设计与结论

**问题一：multilevel RB 在工业规模网络上是否足够快且解更好？** 作者在 SGI UV100 架构、40 μs 步长上比较 A* 与 Scotch。French 400 kV 网络含 460 个任务、16 个处理器时，A*/Scotch 的 mapping time 分别为 0.98 s/0.06 s，通信代价为 15096/6960，负载方差为 4.93/0.14；400 kV + 225 kV 网络含 1510 个任务、79 个处理器时，对应时间为 81.1 s/0.17 s。论文据此得出，在这两个实例上 Scotch 更快，通信代价与负载均衡也更好。[pdf:E04]（PDF 物理页 3，Table 1）

**问题二：收紧 LIR、专用策略和随机种子能否缓解弱 deadline？** 802-task、2052-edge 的测试网络映射到至多 19 个处理器，步长 40 μs，理论最少处理器数为 16。Table 3 显示 \(\delta\) 从 0.25 降至 0.01 时，三种策略都能在 17 个处理器上找到解，但通信代价上升；Table 4 显示随机种子迭代可让 Quality 从 19 个处理器降到 18 个，也可让原本无解的 Balance 找到 19-processor 解，代价是 mapping time 增加。作者的结论是这些调节能改善特定实例，但随机性不构成可行性保证。[pdf:E06]（PDF 物理页 4，测试条件）；[pdf:E08]（PDF 物理页 5，Table 3–4）

**问题三：heuristic 解离 exact Pareto front 有多远？** 作者对 35-bus、103-task、3-processor 实例建立 LP，用 190-core cluster 求解，并比较不同策略的 LIR–CC 点到 Pareto front 的距离；论文报告距离按 \(10^{-4}\) 量级解释为接近。这个实验支持“小实例上 heuristic 接近 exact trade-off”，但不能证明 1510-task 工业实例全局近最优，因为大实例没有 exact 解。[pdf:E10]（PDF 物理页 5，exact-solution 测试条件）；[pdf:E11]（PDF 物理页 6，Fig. 5、Table 5 及正文）

**问题四：映射能否在真实 HIL 瞬态中守住 deadline？** 三端 HVDC 系统包含 DCCB、CPU/FPGA MMC 模型、真实 ABB 控制硬件和 HYPERSIM；网络被分成 85 个任务。[pdf:E12]（PDF 物理页 7，Fig. 6–7 与 §4.1）；[pdf:E13]（PDF 物理页 7，§4.2）在 OP5031 的 32-core target 上，作者以 \(\delta=0.01\)、30 μs 步长比较三种策略；Table 6 报告 Quality 的最重处理器稳态执行时间为 31.5 μs，Balance 与 Specific 均为 24.0 μs，所以只有后两者满足实时约束。[pdf:E11]（PDF 物理页 6，Table 6）；[pdf:E13]（PDF 物理页 7，§4.2）

瞬态波形进一步显示，Balance 下三个最重处理器保持在 30 μs 以下，而 Quality 出现超过 30 μs 的执行时间；同一案例的 inter-processor communication time 相对很小。作者因此在该 HIL 案例中选择 Balance，并明确提醒：当架构异构、通信延迟影响更大时，这个结论可能不成立。[pdf:E14]（PDF 物理页 7，Fig. 8–9 及解释）故障场景中，较短 DC 电缆在 \(t=200\) ms 发生负极接地故障，DCCB 隔离故障后各站负极电压回到约 \(-320\) kV 工作点；这证明选定映射支撑了该 HIL 运行，但电压恢复主要验证保护与模型闭环，不是 task mapping 近最优性的独立证据。[pdf:E13]（PDF 物理页 7，§4.3 起始段）；[pdf:E15]（PDF 物理页 8，Fig. 10 与 Conclusions）

## § 8 — Take-aways

**5 句话：**

1. 论文把实时 EMT 的任务映射明确为同时受处理器 deadline 与任务通信影响的 TAP。
2. multilevel RB 通过 coarsen–partition–uncoarsen，在两个工业网络实例上比作者实现的 A* 显著更快且解质量更好。[pdf:E04]（PDF 物理页 3，Table 1）
3. 通用 graph partitioning 的关键缺口是 deadline 只是弱约束，因此必须映射后检查并通过 LIR、策略和随机种子改善可行性。[pdf:E06]（PDF 物理页 4，§3.1.2）
4. 小规模 LP/Pareto 对照说明 heuristic 在该 benchmark 上接近 exact trade-off，但不构成大实例的全局最优证明。[pdf:E11]（PDF 物理页 6，Fig. 5、Table 5）
5. HIL 案例表明，在通信开销很小且执行时间估计有误差时，Balance 比 Quality 更能守住 30 μs deadline。[pdf:E14]（PDF 物理页 7，Fig. 8–9）

**3 句话：** 这篇论文的主要贡献不是发明新的 EMT 离散公式，而是把成熟 graph partitioning 变成可审查的实时任务分配流程。它用工业规模性能、小实例 exact 对照和真实 HIL 三层证据支持工程可用性。证据同时暴露了边界：静态任务时间估计、弱 deadline 和同构通信假设仍决定方法是否可靠。

**1 句话：** 对这篇论文最准确的概括是：“先用快速分图找到通信—负载折中，再用实时 deadline 和 HIL 把图论解筛成工程可用解。”

## § 9 — 最脆弱的假设

最脆弱的假设是：用于映射的任务执行时间估计 \(t_i\) 足够代表运行期间，尤其是最坏瞬态期间的真实计算负载，使一个按估计值均衡的静态映射仍能守住 deadline。这个假设一旦失效，Scotch 的 LIR 又只是弱约束，算法可能先接受一个看似均衡的候选，实际运行时却由少数任务的瞬态膨胀把某个处理器推过步长；增加处理器并重跑也未必找到本来存在的可行映射。[pdf:E06]（PDF 物理页 4，§3.1.2）

论文提供的正面证据是：在一个 85-task HVDC HIL 中，Balance 对估计误差比 Quality 更稳健，瞬态执行时间守住 30 μs。[pdf:E13]（PDF 物理页 7，§4.2）；[pdf:E14]（PDF 物理页 7，Fig. 8）但它没有系统扫描估计误差的幅值、相关性、工况变化或长时尾部，也没有给出 deadline-miss probability。更重要的是，作者自己指出通信在该案例中近乎可忽略，异构架构上结论可能改变。[pdf:E14]（PDF 物理页 7，Fig. 9 后正文）因此，“Balance 对不确定执行时间普遍稳健”只能算基于单案例的候选判断，不是论文已证明的一般结论。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重建整套 HVDC HIL，而是复现“Balance 对任务时间误差更不容易 miss deadline”这一机制。

- **数据：** 构造一个固定的 85-vertex SG，顶点分成换流站、控制、线路和 I/O/FPGA 接口四类，边权保持固定；处理器数设为 6，预算设为 30 μs。任务类别和规模来自论文 HIL，但由于论文未公开原始任务图，这只是机制复现，不是结果复刻。[pdf:E13]（PDF 物理页 7，§4.2）
- **实现：** 用 Scotch 或等价 multilevel partitioner生成 Quality 与 Balance 两组映射；为每个任务给出预测执行时间 \(\hat t_i\)，再用对数正态扰动和少数相关 burst 生成实际时间 \(t_i\)。
- **测量：** 扫描 0%–40% 的估计误差，统计每种映射的 deadline-miss probability、最重处理器的 99.9% 分位执行时间、处理器数和通信代价。
- **支持条件：** 在相同处理器数下，Balance 在中高误差区显著降低 miss probability，并仍把 99.9% 分位压在 30 μs 内，即支持论文的稳健性解释。
- **反驳条件：** 两策略 miss probability 无显著差异，或 Quality 在相同通信模型下更稳健，就说明论文 HIL 结果可能来自该案例特定任务结构，而非 Balance 的一般机制。

## § 11 — 最强反例设计

最强反例应把论文 HIL 中“通信近乎可忽略”的条件反转：使用四 chassis、多 socket 的异构 target，使跨 chassis 通信远贵于核内通信；同时让两个通信最重的任务在故障瞬态中发生相关计算 burst。然后让 Balance、Quality 和一个显式 deadline-constrained baseline 在相同处理器数、相同 30 或 40 μs 步长下运行。

如果 Balance 为追求静态负载均衡而把重通信任务拆到昂贵链路两侧，通信等待与相关 burst 会叠加在关键路径上；此时它可能比 Quality 更频繁超时，甚至出现“估计负载更均匀、实际 deadline 更差”的反转。该反例直接攻击核心机制，而不是泛泛地说“换个网络再测”：论文的大网络测试确实涉及异构 UV100，但后续深入分析限定为同构架构，HIL 也明确观察到通信时间很小。[pdf:E04]（PDF 物理页 3，架构与 Table 1 上下文）；[pdf:E14]（PDF 物理页 7，Fig. 9 及异构架构 caveat）

若 Balance 在这一条件下仍保持更低 deadline-miss probability，且通信代价没有主导关键路径，那么这个反例就失败，论文机制会得到更强支持。

## § 12 — Follow-up Research Idea

在实时 EMT 与 HIL 领域，高影响工作通常不仅要求平均加速，还要求可复现的 deadline 保证、跨工况数值可信度、真实硬件验证和对失败边界的量化。基于第 9 节，候选研究方向是把静态 TAP 改写成**面向尾部风险的 robust real-time mapping**：不再用单个估计值 \(t_i\) 和弱 LIR 代表任务负载，而是学习或在线更新每类任务在不同 EMT 事件下的执行时间分布及相关性，把目标改为在拓扑相关通信延迟下最小化 deadline-miss 的高分位风险。

（a）驱动需求是：一次罕见但相关的计算 burst 就足以破坏 HIL 的确定性，平均负载均衡不能给出可信保证。（b）研究价值在于把“映射看起来均衡”提升为“在给定风险水平下可说明为什么不会超时”，并可直接连接保护测试的可审计性。（c）可借鉴 robust optimization、chance-constrained scheduling 和 real-time systems 的 worst-case/measurement-based execution-time 工具。（d）第一个证伪实验就是在同构与异构 target 上注入可控的独立/相关执行时间误差，对比原始 Balance、Quality 与 robust mapping 的 99.9% 执行时间和 deadline-miss probability；若 robust 方法在相同核数下没有稳定降低尾部超时，它的核心价值即被否定。（e）它与本文的实质区别不是再加一种 Scotch 参数组合，而是把问题目标从“静态估计上的 LIR–CC 折中”改为“事件条件下的概率 deadline 保证”。

这是基于本文局限形成的候选想法；本次没有对外部相关工作做充分检索，因此不声称 novelty。
