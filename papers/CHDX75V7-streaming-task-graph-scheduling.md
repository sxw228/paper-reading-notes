# Streaming Task Graph Scheduling for Dataflow Architectures

**作者：** Tiziano De Matteis、Lukas Gianinazzi、Johannes de Fine Licht、Torsten Hoefler [pdf:E01]（PDF 物理页 1，标题页）  
**出处：** ACM HPDC ’23；源 PDF 标注为即将发表于该会议的预印本版本 [pdf:E01]（PDF 物理页 1，标题页）  
**年份：** 2023 [pdf:E01]（PDF 物理页 1，标题页与预印本日期）  
**DOI：** 10.1145/3588195.3592999  
**Zotero key：** CHDX75V7  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：** 论文要解决的是“怎样把一个单次执行的 DAG 任务图，静态映射到有限数量的 dataflow Processing Elements（数据流处理单元）上，同时显式利用任务间的 token-level pipelining（元素级流水），并给出不会死锁的 FIFO 容量”。这比传统 DAG 调度多了三个互相耦合的决策：哪些任务同时驻留并空间执行、哪些任务分批时间复用、哪些依赖以 streaming 而不是写回全局内存的方式传递。作者把最多含有 \(P\) 个计算任务、可同时执行的一组任务称为 spatial block；不同 block 按时间顺序执行，block 内尽量流水，block 间只允许 buffered communication，目标是最小化 makespan（完工时间）并计算所需缓冲区。[pdf:E02]（PDF 物理页 2，Section 2）

这个问题重要，是因为 dataflow architecture（数据流架构）的性能来源并不只在“有很多 PE”，还在于相邻算子可经片上互连边生产边消费。若仍采用“父任务全部结束后子任务才启动”的 load-store 式语义，链式算子会被人为串行化，中间结果反复落到全局内存，快速 NoC 的价值没有兑现。论文因此把空间并行、时间复用和通信流水视为同一个调度问题，而不是三个后处理步骤。[pdf:E01]（PDF 物理页 1，Abstract、Section 1、Figure 1）

论文直接声称的价值有四项：建立 canonical task graph（规范任务图）来表达并分析流水执行；给出有限 PE 下的空间—时间调度算法；推导 streaming execution time（流式执行时间）的界；在有限 FIFO、blocking-after-service 语义下计算避免死锁的容量。[pdf:E01]（PDF 物理页 1，Section 1 贡献列表）这些能力对 CGRA、可重构 dataflow accelerator 和多 PE 芯片具有抽象层面的通用性，但论文没有完成 placement、routing、异构 PE 或真实存储层次的闭环；作者把异构、placement 和跨设备通信列为后续扩展。[pdf:E02]（PDF 物理页 2，Section 2）[pdf:E12]（PDF 物理页 12，Conclusion）

## § 2 — 前人工作与不足

**结论：** 最相关的两条前人路线分别是传统 static DAG scheduling（静态 DAG 调度）和 Synchronous/Cyclo-static DataFlow Graph，简称 SDFG/CSDFG（同步/周期静态数据流图）；它们并非没有解决“调度”，而是使用了与本文目标不匹配的启动语义、优化目标和可分析对象。以下相关工作判断均是作者在论文中的归纳，未做包外文献核验。

传统 list-based、cluster-based、critical-path 和 look-ahead 调度通常把每个任务的计算与通信代价作为输入，并规定任务只有在所有父任务完成后才能启动。它们适合以任务完成事件为边界的多处理器调度，却无法表达“父任务刚产生第一个元素，子任务就开始”的部分重叠；因此即便 PE 数量足够，长算子链仍可能被调成串行。作者也指出 Cong 等面向 FPGA streaming application 的工作考虑了 spatial scheduling，而本文试图同时处理 spatial 与 temporal scheduling。[pdf:E11]（PDF 物理页 11，Section 8）

SDFG/CSDFG 已能用 actor firing 和 token production/consumption rate 分析流式系统，相关工具还能求 optimal throughput（最优吞吐）。不足不在于它们“不懂 streaming”，而在于它们主要优化多个 graph iteration 之间的吞吐；本文优化单个 DAG iteration 内部的任务流水与 latency（延迟）。作者还强调，SDFG 难以直接表示本文的 buffer node 所代表的非流式子计算；复杂图若转换为较简单的 homogeneous dataflow graph，规模在最坏情况下可能指数膨胀。[pdf:E11]（PDF 物理页 11，Section 8，SDFG 对比条目）

计算成本也是差异之一。论文把无 buffer 的 canonical graph 转成等价 CSDFG 后，用 SDF3 和 Kiter 求最优吞吐；在一小时超时限制下，复杂图出现最多 30/100 和 32/100 个超时，而本文启发式的中位调度时间处在毫秒到几十毫秒量级。作者据此主张：在双方都适用的子集上，canonical graph 的 schedule quality 接近 CSDFG 最优结果，但分析成本低 2–3 个数量级。[pdf:E10]（PDF 物理页 10，Section 7.2、Figure 12）这里的关键取舍是“更快得到接近最优的单次执行调度”，而不是证明一般情形下全局最优。

## § 3 — 重建作者的思考路径

下面是**基于证据的思考路径重建**，不是论文逐句陈述，也不把最终贡献当作前提。

1. **先识别传统调度的错误粒度。** 在 dataflow device 上，依赖边携带的是一串元素；若只记录任务完成时刻，就丢掉了第一个元素到达、稳定生产速率和最后一个元素离开的信息。因而需要把任务依赖从“完成屏障”细化为“持续的数据流”。[pdf:E02]（PDF 物理页 2，Section 2）
2. **再寻找足够简单、又能表达算子速率的图模型。** 元素级算子、reduction、replication 可分别抽象为 \(R=1\)、\(R<1\)、\(R>1\) 的节点；需要随机重读、重排或重复使用数据的地方则显式插入 buffer node。矩阵乘、outer product、normalization 等复杂算子不是一个固定节点，而可按实现方式拆成不同 canonical subgraph。[pdf:E03]（PDF 物理页 3，Section 3.2、Figures 2–4）
3. **在做有限资源调度前，先求无限 PE 下的稳态。** 只要同一流式连通区域内的 producer/consumer 速率不平衡，局部节点就会被 backpressure 限速；因此先按 buffer 边界切开图，再在每个 weakly connected component 中解 steady-state streaming interval。[pdf:E04]（PDF 物理页 4，Section 4.1、Equations 1–2）[pdf:E05]（PDF 物理页 5，Theorem 4.1）
4. **把有限 PE 约束变成“流水岛分批执行”。** 一个 block 内的节点可共同驻留并形成流水；block 数量越多，重复的填充/排空与全量 buffering 越多。于是 partition 的代理目标自然变为：每个 block 尽量容纳 \(P\) 个节点，同时避免把输出体量更大的 upsampler 过早放入 block，抬高整个 block 的 streaming interval。[pdf:E06]（PDF 物理页 6，Section 5）[pdf:E07]（PDF 物理页 7，Section 5.2、Algorithm 1）
5. **最后处理“DAG 也会因有限 FIFO 死锁”的反直觉失败。** 多条不同延迟的路径在 join 节点重汇合时，短路径可能先塞满 FIFO，并反向阻塞长路径所需的生产者；因此必须用 first-out time 的路径偏斜来配置容量，而不能只检查有向环。[pdf:E08]（PDF 物理页 8，Section 6、Figure 9、Equation 5）

这条路径的逻辑是：先改变时间语义，再构造可分析表示；先求稳态不变量，再做有限资源 partition；最后用事件时序补上有限缓冲带来的系统级死锁条件。

## § 4 — 核心 Intuition

核心不是给每个任务估一个更准确的总运行时间，而是把每条依赖边看成一个有生产速率、消费速率和相位差的元素流。[pdf:E04]（PDF 物理页 4，Section 4.1）把不能穿透的 buffer 切成 streaming island 后，同一 island 的所有节点会被最大数据体量的节点统一限速，因此只看输出体量就能求稳态间隔。[pdf:E05]（PDF 物理页 5，Theorem 4.1）有限 PE 下，再把能共同维持该稳态的节点装进 spatial block，block 内空间并行、block 间时间复用。[pdf:E07]（PDF 物理页 7，Sections 5.1–5.2）最后用各路径首元素到达时间的偏斜配置 FIFO，保证理想流水不会被有限容量破坏。[pdf:E08]（PDF 物理页 8，Section 6）

## § 5 — 具体方法与完整 Pipeline

**结论：** 方法的输入不是普通的 operator DAG，而是一个已经携带数据体量、production rate 和显式 buffer boundary 的 canonical DAG；输出是 spatial block 序列、block 内任务时序/PE 占用，以及 streaming edge 的 FIFO 容量。它是编译与调度层方法，不是 RTL 生成器，也不是具体 FPGA placement 工具。

**抽象模型。** 设备含 \(P\) 个同构 PE、无限容量的 global memory 和无 contention 的 NoC；每个 PE 同时只执行一个不可抢占任务。计算节点从每条输入边接收相同数量 \(I(v)\) 的元素，并向每条输出边产生相同数量 \(O(v)=R(v)I(v)\) 的元素；buffer node 收齐输入后再输出，因而切断流水，且自身不占 PE。[pdf:E02]（PDF 物理页 2，Sections 2、3.1）

**以 numerically stable softmax 为例。** 对长度为 \(N\) 的向量 \(x\)，论文使用
\[
y_i=\frac{e^{x_i-\max(x)}}{\sum_{j=1}^{N}e^{x_j-\max(x)}}.
\]
它被拆成求最大值的 downsampler、减法与指数的 element-wise 节点、求和 downsampler、最终除法节点，以及保存 \(x\)、最大值、指数结果和分母的 buffer；其中 \(e^{x_i-\max(x)}\) 只计算一次并复用，使中间一部分可以流水。[pdf:E04]（PDF 物理页 4，Section 3.2.4、Figure 5）这说明“同一个数学算子如何 canonicalize”直接决定可流水区域，而不是纯语法转换。

**完整 pipeline：**

1. **Canonicalization。** 编译器或 synthesis pass 把应用 DAG 的每个算子映射为 canonical node，或展开成 canonical subgraph；实现选择会改变数据顺序、buffer 位置和可用并行度。论文明确把通用自动推导留在范围之外，直接假定该图已提供。[pdf:E03]（PDF 物理页 3，Section 3.2、Figures 2–4）
2. **速率与边界分析。** 标注每个节点的 \(I(v)\)、\(O(v)\)、\(R(v)\)，把每个 buffer node 分裂成前驱侧的 tail 和后继侧的 head，由此得到彼此独立的 streaming weakly connected components。[pdf:E04]（PDF 物理页 4，Section 4.1）
3. **稳态求解。** 对每个 component，用 Theorem 4.1 从最大输出体量直接得到所有节点的 input/output streaming interval；随后计算 work、level、first-out、last-out 和 streaming depth。[pdf:E05]（PDF 物理页 5，Theorem 4.1、Section 4.2）[pdf:E06]（PDF 物理页 6，Section 4.2.3、Equations 3–4）
4. **Spatial block partition。** 反复从当前 DAG 的 source nodes 中选候选，直到 block 满 \(P\) 个计算节点或没有合适候选。SB-LTS 优先加入不会让 block 源节点输出体量上升的节点；SB-RLX 在没有此类节点时放宽约束，选择输出最小的可用 source，从而更倾向填满 block。启发式复杂度为 \(O(N^2)\)。[pdf:E07]（PDF 物理页 7，Section 5.2、Algorithm 1）
5. **Block 内调度。** graph source 从时刻 0 开始；一个 block 的 source 等前序 block 的相关生产者完成，block 内其他节点在直接前驱产生首元素后即可启动。downsampler 要先积累足够输入才有 first output，upsampler 在收到输入后还要继续发出额外元素；由递归的 \(FO\)、\(ST\)、\(LO\) 公式生成时间表。[pdf:E07]（PDF 物理页 7，Section 5.1、Figure 8）
6. **跨 block 串行化。** block 按构造顺序依次执行；block 内计算边可 streaming，跨 block 边全部 buffered。最终 makespan 是出口节点最大的 last-out time。[pdf:E02]（PDF 物理页 2，Section 2）[pdf:E07]（PDF 物理页 7，Section 5.2）
7. **Deadlock-free FIFO sizing。** 对每个 block 的无向环区域，找 join 节点各输入路径的最大 first-out 偏斜，并按上游 streaming interval 换算成元素数；容量不超过该边总数据量。Figure 9 的两个例子分别需要 18 和 32 个元素的 FIFO 才能维持预期流水。[pdf:E08]（PDF 物理页 8，Section 6、Figure 9、Equation 5）

**EMT + FPGA 视角下的已报告与未报告。** 本文不是 electromagnetic transient，EMT（电磁暂态）数值求解论文：没有电路离散方程、开关事件、积分器、实时仿真步长或多速率时间积分；文中的“rate”是 token production rate，“time unit”是抽象元素处理时间。数值表示只假定边携带基本数据类型，并称方法可扩展到任意数据宽度；没有 fixed-point 位宽、量化误差、DSP/BRAM/LUT 使用量、时钟频率、placement、routing 或 bitstream。目标硬件仅抽象为同构 PE + NoC + global memory，placement 被明确排除，异构与 placement 被列作未来方向。[pdf:E02]（PDF 物理页 2，Sections 2、3.1）[pdf:E12]（PDF 物理页 12，Conclusion）实际实现是 Python proof-of-concept，实验机为 128 GB 内存、16C/32T AMD Ryzen 9 5950X；PDF 报告操作系统为 Ubuntu 20.20，并未在 FPGA/CGRA 实机上执行。[pdf:E08]（PDF 物理页 8，Section 7）

## § 6 — 核心数学推导（无形式化数学则跳过）

**结论：** 数学核心是一个速率守恒不变量：同一 streaming component 中，节点的“输出元素总数 × 输出间隔”相同。这个不变量把复杂的稳态求解压缩为“找到该 component 中最大的输出体量”，再由此推导无限 PE 深度、有限 PE 上界和 FIFO 容量。

**1. 节点速率与边间隔。** 对计算节点，论文定义
\[
O(v)=R(v)I(v),\qquad s(e)\ge 1,\qquad S^o(v)=\frac{S^i(v)}{R(v)}.
\]
这里 \(s(e)\) 是边上相邻元素的平均时间间隔；\(s(e)\ge1\) 表示抽象 PE 最快每单位时间处理一个元素。\(R=1\) 保持间隔，\(R<1\) 的 downsampler 输出更稀，\(R>1\) 的 upsampler 输出更密。[pdf:E02]（PDF 物理页 2，Section 3.1）[pdf:E04]（PDF 物理页 4，Section 4.1、Equations 1–2）

**2. Theorem 4.1：稳态间隔闭式解。** 把 buffer 拆开后，对节点 \(v\) 所在的 weakly connected component，记为 \(WCC(v)\)，论文给出
\[
S^o(v)=\frac{\max_{u\in WCC(v)}O(u)}{O(v)}.
\]
证明思路是：无 buffer 路径上的生产/消费比把 interval 按数据体量反向缩放；对能汇合到同一后继的节点，有 \(S^o(v)O(v)\) 为常数。取输出体量最大的节点 \(u\)，其 interval 不可能小于 1；若大于 1，则整个 component 的 interval 还能同比缩小，违背最快稳态。因此令 \(S^o(u)=1\)，常数就是 \(\max O\)。[pdf:E05]（PDF 物理页 5，Theorem 4.1、Lemmas 4.2–4.3）工程直觉是：最大流量节点充当全流水岛的吞吐基准，其他节点按自己的输出量被相应放慢。

**3. Work 与 streaming depth。** 单节点 work 定义为
\[
W(v)=\max\{I(v),O(v)\},\qquad T_1=\sum_{v\in V}W(v).
\]
在全 element-wise、每个任务处理 \(k\) 个元素的 DAG 中，无限 PE 下
\[
T_\infty^s=k+L(G)-1,
\]
而完全不流水时为 \(kL(G)\)。前一式等于“注入 \(k\) 个元素”加“最后一个元素穿过其余 \(L-1\) 层”，直接揭示深链为什么最受益。[pdf:E05]（PDF 物理页 5，Section 4.2.1）[pdf:E06]（PDF 物理页 6，Section 4.2.1）

**4. 一般 canonical DAG。** 为计入 upsampler 的额外输出，节点 level 被推广为
\[
L(v)=
\begin{cases}
1,&v\text{ 无父节点},\\
\max(R(v),1)+\max_{(u,v)\in E}L(u),&\text{否则}.
\end{cases}
\]
last-out time 则在最大前驱 \(LO\) 上，给 upsampler 增加约 \((R(v)-1)S^o(v)\) 的排空时间；element-wise 与 downsampler 收到最后输入后只需一个单位时间完成。由 Theorem 4.1，论文得到
\[
T_\infty^s\le L(G)+\max_{u\in G}O(u),
\]
并称当流式元素数趋于无穷时该界变紧。含 buffer 时，把每个 WCC 压成 supernode 构造 DAG \(H\)，再沿 \(H\) 的最深路径叠加各 island 的深度。[pdf:E06]（PDF 物理页 6，Section 4.2.3、Equations 3–4）

**5. 有限 PE 的 Brent-like 上界。** 对纯 element-wise 图，按 level 排序并每 \(P\) 个节点组成一个 block，可得
\[
T_\infty^s\le T_P\le \frac{T_1}{P}+T_\infty^s.
\]
这意味着在达到 streaming depth 下限前，增加 PE 可近似线性摊薄 work。对 element-wise + downsampler 图，Algorithm 2 按非增 work 选节点，论文给出
\[
T_P\le \frac{T_1}{P}+T_\infty^s+
\min\bigl(n-1,(x-1)(L(G)-1)\bigr),
\]
其中 \(x\) 是同一 level 中不同 work 值的最大数量；最后一项是 block 跨 level、跨 work 组造成的附加流水排空代价。[pdf:E13]（PDF 物理页 13，Appendix A、Theorems A.1–A.2）

**6. FIFO 容量。** 对 block \(B_i\) 内 join 节点 \(v\) 的输入边 \((u,v)\)，论文使用
\[
B(u,v)=\frac{\max_{(t,v)\in G[B_i]}FO(t)-FO(u)}{S^o(u)},
\]
若结果大于该边总数据量则取总数据量。分子是这条输入相对最慢输入“早到”了多少时间，分母把时间差换算成会提前积压的元素数；这正是短路径在等待长路径时需要吸收的相位差。[pdf:E08]（PDF 物理页 8，Section 6、Equation 5）

## § 7 — 实验设计与结论

**问题 1：streaming scheduling 是否真的比全 buffered 调度更快？** → **实验：** 作者对 Chain、FFT、Gaussian Elimination、Tiled Cholesky 四类拓扑生成随机边权 canonical DAG；除固定为 8 个任务的 Chain 外，示例规模分别是 FFT 223、Gaussian 135、Cholesky 120 个任务。每个配置使用 100 个随机图，改变 PE 数量，对比 STR-SCH-1（SB-LTS）、STR-SCH-2（SB-RLX）和 NSTR-SCH（所有通信 buffered 的 critical-path list scheduling）。合成图不含 buffer node，因此 block 内所有边都具备 streaming 可能。[pdf:E08]（PDF 物理页 8，Section 7）[pdf:E09]（PDF 物理页 9，Section 7.1、Figure 10）→ **答案：** Chain 的非流式版本因严格依赖链而 speedup 为 1，流式版本随 PE 增加继续加速；其余拓扑也表现为 NSTR-SCH 较早停止扩展，而 streaming schedule 保持更高 speedup 和 PE utilization。SB-RLX 在 PE 数接近任务数时通常更好，因为它用更少 block 换取可能变慢的局部 interval。[pdf:E09]（PDF 物理页 9，Section 7.1、Figure 10）Streaming SLR 也随 PE 增加而下降，SB-RLX 在 \(P\ge N\) 时可接近 1。[pdf:E10]（PDF 物理页 10，Figure 11）

**问题 2：启发式快多少，代价是多少？** → **实验：** 对无 buffer 图构造等价 CSDFG，把本文 PE 数设为节点数并采用 SB-RLX；SDF3 和 Kiter 各自求 optimal throughput，单图限时 1 小时。[pdf:E10]（PDF 物理页 10，Section 7.2）→ **答案：** Figure 12 报告本文中位调度时间约为 0.002–0.043 秒；SDF3 为 0.524–9.948 秒，Kiter 为 0.408–56.751 秒。SDF3 在最复杂拓扑上最多超时 30/100，Kiter 最多 32/100；本文无超时。本文 makespan 与 SDF3 最优 makespan 的中位比值在 Chain、Gaussian、FFT 上约 1.00，在 Cholesky 上约 1.02，但分布尾部可明显更高。[pdf:E10]（PDF 物理页 10，Figure 12）因此证据支持“快很多且中位质量接近”，不支持“所有实例都接近最优”。

**问题 3：大规模真实 operator graph 是否仍有收益？** → **实验：** 作者从 DaCeML/ONNX 图构造 ResNet-50 和 base Transformer encoder layer 的 canonical graph；卷积以 im2col + matrix multiplication 表示，并为每个 MatMul 按矩阵尺寸选择最大化并行度的实现。ResNet 图含 54,252 个节点、其中 246 个 buffer；Transformer 图含 4,748 个节点、其中 37 个 buffer。[pdf:E11]（PDF 物理页 11，Section 7.3）→ **答案：** 在 2,048 个 PE 上，ResNet 的 streaming speedup 为 135.0，non-streaming 为 90.2，增益 1.5 倍；在 1,024 个 PE 上，Transformer 分别为 305.0 和 153.0，增益 2.0 倍。作者把 Transformer 的更高增益归因于更长、易流水的 operator chains；两种启发式在这两个图上差异不明显，表中报告 SB-LTS。[pdf:E11]（PDF 物理页 11，Table 2、Section 7.3）

**问题 4：解析 makespan 与 FIFO 容量是否符合事件级执行？** → **实验：** Appendix 使用 SimPy discrete-event simulation，为每个任务建立独立 process，用有限 blocking FIFO 模拟 streaming edge，并按 Equation 5 配置容量。[pdf:E14]（PDF 物理页 14，Appendix B.1）→ **答案：** 所有测试都完成且没有死锁；相对误差中位数为 0 或接近 0，说明稳态分析对典型实例有效。但 Cholesky、128 PE 的 whisker 范围达到 \([-7\%,4\%]\)，并出现绝对值超过 50% 的 outlier，密集连接图是最困难情形。[pdf:E15]（PDF 物理页 15，Appendix B.1）

**不得外推的范围。** 全部证据来自解析模型、Python 调度器和同一抽象假设下的事件模拟，没有 FPGA/CGRA 实机、NoC contention、placement、memory-bank conflict、频率或资源结果。另一个应明确记录的文本问题是：物理页 14 说负误差表示“调度器报告的 makespan 大于模拟值”，物理页 15 又说负 outlier 意味着“分析可能低估实际执行时间”；这两种符号解释方向相反，不能同时成立。[pdf:E14]（PDF 物理页 14，Appendix B.1 误差定义）[pdf:E15]（PDF 物理页 15，Appendix B.1 结果解释）

## § 8 — Take-aways

**5 句话：**

1. 论文把单次 DAG latency 调度改写成元素流的速率、首元素和末元素时序问题，而不再只看任务完成屏障。[pdf:E02]（PDF 物理页 2，Section 2）
2. Canonical graph 用 element-wise、downsampler、upsampler 与 buffer node 统一表达可流水与不可流水的算子片段。[pdf:E02]（PDF 物理页 2，Section 3.1）[pdf:E03]（PDF 物理页 3，Section 3.2）
3. Theorem 4.1 表明一个 streaming island 的稳态由其中最大的输出体量决定，从而把 interval 计算降为线性时间。[pdf:E05]（PDF 物理页 5，Theorem 4.1）
4. 有限 PE 调度通过 spatial blocks 把空间并行和时间复用结合起来，FIFO 容量则由重汇合路径的 first-out 偏斜决定。[pdf:E07]（PDF 物理页 7，Section 5）[pdf:E08]（PDF 物理页 8，Section 6）
5. 模型内实验显示相对全 buffered 调度的明显加速和很快的分析速度，但真实硬件有效性尚未被验证，密集图的误差尾部也不可忽略。[pdf:E09]（PDF 物理页 9，Figure 10）[pdf:E10]（PDF 物理页 10，Figure 12）[pdf:E15]（PDF 物理页 15，Appendix B.1）

**3 句话：**

1. 先用 production rate 和 buffer boundary 找到能形成稳态流水的任务岛，再把岛内任务分装到有限 PE 的 spatial blocks。[pdf:E04]（PDF 物理页 4，Section 4.1）[pdf:E07]（PDF 物理页 7，Algorithm 1）
2. 速度来自 block 内 producer/consumer 的重叠，正确性依赖 first-out/last-out 模型和足够的 FIFO。[pdf:E07]（PDF 物理页 7，Section 5.1）[pdf:E08]（PDF 物理页 8，Equation 5）
3. 这是一个有用的编译级性能模型和启发式，不是已经在 FPGA 上闭环验证的实现方法。[pdf:E08]（PDF 物理页 8，Section 7）[pdf:E12]（PDF 物理页 12，Conclusion）

**1 句话：** 这篇论文最重要的贡献，是证明“单次任务图内部的 streaming”可以用一个足够简单的 rate-aware graph（速率感知图）同时驱动性能界、空间—时间 partition 和 deadlock-free buffer sizing。[pdf:E01]（PDF 物理页 1，贡献列表）[pdf:E05]（PDF 物理页 5，Theorem 4.1）[pdf:E08]（PDF 物理页 8，Section 6）

## § 9 — 最脆弱的假设

**结论：** 最脆弱的不是 SB-LTS/SB-RLX 是否接近最优，而是**rate-faithful canonicalization（速率忠实的规范化）假设**：一个真实算子必须能被拆成 canonical nodes，使得仅凭 \(I(v)\)、\(O(v)\)、\(R(v)\)、buffer boundary 和拓扑，就足以预测其执行速率与 backpressure。

论文为此叠加了强假设：计算对输入/输出元素是线性时间、常数空间；PE 能对每个输入/输出持续达到每单位时间一个元素；NoC 无 contention；PE 同构；global memory 容量无限。作者还明确承认，同一运算怎样表示取决于实际实现与 runtime behavior，若要自动捕捉数据访问模式就需要完整内部语义，因此本文直接假定 canonical graph 由 compiler/synthesis pass 提供。[pdf:E02]（PDF 物理页 2，Sections 2、3.1）[pdf:E03]（PDF 物理页 3，Section 3.2）

**基于证据的推断：** 一旦实际算子存在 data-dependent work、稀疏跳过、burst memory access、共享链路仲裁、bank conflict、可变启动延迟或不能维持声明 rate，Theorem 4.1 的统一稳态、\(FO/LO\) 递推和 Equation 5 的容量都会同时失真。这不是局部性能偏差，而是从 representation 到 schedule 再到 deadlock sizing 的整条因果链失效。

论文提供的正面证据是：outer product、MatMul、normalization、softmax 能手工构造出多个 canonical representation；在同一抽象语义的 discrete-event simulator 中，误差中位数接近 0 且计算出的 FIFO 没有死锁。[pdf:E03]（PDF 物理页 3，Section 3.2）[pdf:E04]（PDF 物理页 4，Sections 3.2.3–4.1）[pdf:E14]（PDF 物理页 14，Appendix B.1）缺口是：没有自动 canonicalization 的正确性验证，没有真实 PE/NoC/存储系统上的 rate 测量，也没有解释密集图超过 50% 的 outlier 与模型哪一项失配。[pdf:E15]（PDF 物理页 15，Appendix B.1）因此，这个假设一旦不成立，论文的核心贡献不是“效果变小”，而是失去可执行预测意义。

## § 10 — 最小复现实验

**一周内最值得复现的 claim：** 在论文自己的抽象模型内，Theorem 4.1 + spatial-block heuristic + Equation 5 能同时做到“预测 makespan、相对全 buffered 调度获得加速、有限 FIFO 下不死锁”。无需复现 50,000 节点网络，也无需 FPGA。

**数据。** 先实现三组小图：8 节点 Chain；Figure 9 风格的双路径 reconvergent DAG；以及每类 30 个、20–80 节点的随机 FFT/Gaussian/Cholesky 子图。性能组不放显式 buffer node，死锁组加入不同 reduction/upsampling rate 和无向环结构。图的节点只需存 \(I,O,R\) 与类型。[pdf:E08]（PDF 物理页 8，Figure 9、Section 7）[pdf:E09]（PDF 物理页 9，Section 7.1）

**实现。**

1. 按 buffer split 计算 WCC，并用 Theorem 4.1 求 \(S^i/S^o\)。
2. 实现 SB-LTS、SB-RLX 和一个全 buffered critical-path baseline。
3. 按论文递推式计算 \(FO/ST/LO\)，按 Equation 5 配置 FIFO。
4. 写一个独立 discrete-event simulator：任务逐元素 consume/produce，FIFO 满时阻塞写、空时阻塞读；同一 PE 不并发运行两个任务。
5. 对每张图同时记录解析 makespan、模拟 makespan、是否 deadlock、speedup、PE utilization 和总 FIFO 元素数。[pdf:E05]（PDF 物理页 5，Theorem 4.1）[pdf:E07]（PDF 物理页 7，Sections 5.1–5.2）[pdf:E08]（PDF 物理页 8，Equation 5）

**建议的一周安排。** 第 1 天完成图结构与 interval；第 2–3 天完成两种 block heuristic 和时序递推；第 4 天完成事件模拟；第 5 天加入 Figure 9 型死锁用例；第 6 天跑随机图并画 predicted-vs-simulated 散点；第 7 天检查失败实例和写结论。

**预先注册的支持判据。** 这是复现实验者自行设定、不是论文原判据：使用 Equation 5 后所有测试图均无 deadlock；解析与模拟 makespan 的中位绝对相对误差不超过 1%；8 节点 Chain 在 \(P=8\) 时 streaming schedule 明显快于 NSTR-SCH；随机图中 streaming 的中位 speedup 高于 baseline。**反驳判据：** 只要存在一张满足论文假设的图在按式配置 FIFO 后仍死锁，或误差在多类拓扑上持续超过 10%，就足以否定“分析完整刻画该抽象执行”的核心 claim。Appendix 的零/近零中位误差与无死锁结果提供了直接对照目标。[pdf:E14]（PDF 物理页 14，Appendix B.1）[pdf:E15]（PDF 物理页 15，Appendix B.1）

## § 11 — 最强反例设计

**结论：** 最强攻击不是换一个更难的 DAG，而是构造**两个 canonical graph 完全相同、但物理 placement/routing 不同的执行**，让论文模型给出同一 schedule 和 FIFO，真实系统却出现数量级不同的 makespan，甚至一个死锁、一个不死锁。这样可直接证明“图的 rate/volume 信息不足以决定执行”。

**反例。** 构造 32 条 producer 分支，每条标称每周期产生 1 个元素；它们经过不同长度的 element-wise/downsampler 路径，在一个多输入 join/reduction 处汇合，并增加一条很短的 bypass，使 Equation 5 必须处理显著 first-out skew。使用 64 个 PE，使所有任务可放入一个或少数 block。做两个映射：A 将各流分散到独立 NoC 路径和 SRAM bank；B 让大多数流穿过同一条带宽为 8 元素/周期的 bisection link 和同一 memory bank。论文抽象中两者的 \(P\)、\(I/O/R\)、拓扑、streaming interval 和 FIFO 完全相同，因为 NoC 被假定无 contention。[pdf:E02]（PDF 物理页 2，Section 2）

**攻击机制。** 在映射 B 中，aggregate injection rate 远高于共享链路能力，短路径 FIFO 会比理想 \(FO\) 预测更快积压，backpressure 又会延迟长路径；这些延迟不是固定的独立路径偏移，而是由所有流共同决定的耦合排队过程。SB-RLX 还可能为了减少 block 数把高输出节点装进同一 block，进一步提高瞬时拥塞；Equation 5 只用理想 first-out difference 和单边 interval，无法表示共享资源竞争。[pdf:E07]（PDF 物理页 7，Algorithm 1）[pdf:E08]（PDF 物理页 8，Section 6、Equation 5）

**实验判决。** 在 cycle-accurate NoC simulator 或小型 FPGA prototype 上运行同一任务图的两种 placement，测 makespan、每条 link occupancy、FIFO 峰值和是否发生全局停滞。若 A 与 B 的 makespan 相差超过 2 倍，或 B 在论文给定容量下死锁而 A 不死锁，则同一 canonical graph 不能唯一决定 schedule quality 与 deadlock freedom。对论文合成实验的最强替代解释也随之成立：其加速可能主要来自“每条通信都可独立达到一元素/周期”的理想互连，而不一定来自 block heuristic 本身。这个反例直接挑战核心机制，而不是泛泛指出缺少实机实验。

## § 12 — Follow-up Research Bet

**主 idea：可重写 canonical task graph 的算法—调度联合合成。** 这是**候选判断**；本任务未做包外相关工作检索，因此不声称 novelty。

**新的研究问题。** 不再把 canonical graph 当成编译器已经固定的输入，而是给定一个算子语义图和 \(P\) 个 PE，联合选择每个复杂算子的 canonical decomposition、row/column data order、tile size、task granularity、production rate、buffer boundary、spatial block 和 PE mapping，使单次 inference latency 最小。它首次使“改变算法的数据流表示本身来创造可调度流水”成为编译器的一等优化，而不是先选实现、后做 schedule。

**机制与因果链。** 论文已经展示同一个 outer product、MatMul、vector normalization 可有多个 canonical representation：不同实现会改变哪些输入可直接 stream、哪些数据必须 buffer、输出按行还是按列产生，以及并行任务数。[pdf:E03]（PDF 物理页 3，Section 3.2、Figures 2–4）Softmax 的分解也显示，复用中间指数结果与 buffer placement 会改变可流水的内部路径。[pdf:E04]（PDF 物理页 4，Section 3.2.4、Figure 5）联合合成器可把这些等价实现组织成“代数重写超图”，为每个候选组合符号计算 \(O(v)\)、\(R(v)\)、WCC 最大输出、level、streaming depth、block sum-of-max 代价和 FIFO；表示选择先改变数据体量与 buffer topology，继而改变 Theorem 4.1 的 interval，再改变 partition、pipeline fill/drain 和最终 latency。[pdf:E05]（PDF 物理页 5，Theorem 4.1）[pdf:E06]（PDF 物理页 6，Equation 4、Section 5）

**改变的基本设计变量。** 它同时改变问题定义（从固定图调度变成等价程序族联合搜索）、状态表示（从单一 DAG 变成带语义等价关系的候选图空间）、数据生成顺序（row/column/tile）、可控变量（rate、buffer boundary、task granularity）和硬件映射。删除这一步后，系统只能在固定 representation 上移动任务，无法产生新的流水拓扑，因此新能力不是原方法外接一个 wrapper。

**论文特异依据。** 方法侧，Section 3.2 明确说 representation 取决于 implementation/runtime，却把它假定为 compiler 输入；这留下了一个未开发的高杠杆自由度。[pdf:E03]（PDF 物理页 3，Section 3.2）实验侧，真实 workload 中作者已为每个 MatMul 按尺寸选择“最大化并行度”的实现，Transformer 在 1,024 PE 时由 153.0 提高到 305.0、达到 2.0 倍 streaming gain，说明 operator representation 与长流水链可能共同决定收益。[pdf:E11]（PDF 物理页 11，Section 7.3、Table 2）而 Figure 12 显示固定图上的启发式中位 makespan 已接近 CSDFG 最优，这反而提示下一步更大的增益可能来自改变图，而不是继续微调同一图的 partition。[pdf:E10]（PDF 物理页 10，Figure 12）

**最大收益与最大风险。** 成功后，编译器可以为不同 PE 数量、片上 SRAM 和数据布局自动生成 architecture-native streaming algorithm，而不是复用同一 operator lowering；这可能同时减少 block 数、全局内存 materialization 和 pipeline drain。最大科学风险是搜索空间组合爆炸，以及 canonical cost model 对真实实现不够忠实：若不同 representation 的代价误差大于它们之间的理论差异，联合搜索会稳定选错。

**首个可证伪实验。** 取一个 Transformer attention 子图 \(QK^T\rightarrow Softmax\rightarrow AV\)，为两个 MatMul 分别枚举论文 Figure 3 的三类实现，为 Softmax 枚举至少两种合法 buffer/streaming decomposition，再变化 row/column order 和少量 tile size；在 \(P=64\) 与 \(P=128\) 下，对每个 representation 都运行同一个最强 partition 搜索或小规模穷举，然后与“论文式固定 representation + SB-LTS/SB-RLX”比较。预先注册的机制判据是：即使每个固定图都得到其最优 partition，联合改变 representation 仍能把 latency 再降低至少 20%；若收益在给固定图最优 partition 后消失，则改进只是更好的调度搜索，不支持“表示改变创造新流水”的核心机制。另记录 WCC 最大输出、level、block 数和 FIFO，总结 latency 改善是否沿着预言的因果链发生。

**与最近对象的实质区别。** 就本文覆盖的相关工作而言，传统 DAG scheduler 和本文都固定任务图后优化 placement/order；SDFG/CSDFG 比较也固定 actor/rate graph 后求 throughput 或 schedule。[pdf:E11]（PDF 物理页 11，Section 8）本 idea 的 experimental object 是同一语义下的一族不同 canonical graphs，mechanism 是算法分解、数据顺序和 schedule 的联合选择，representation 不再固定，目标仍是单 iteration latency；因此它在 problem、mechanism、representation 和 experimental object 上都不同于本文直接评测的路线。由于没有外部检索，这只能作为高风险研究押注，不能据此宣称首次提出。

**Wild-card alternative：** 把“block 必须前后完全串行”改写成一个跨 block 的 self-timed phase lattice（自定时相位格），联合选择相邻 block 的启动相位、跨 block token window 与分布式 SRAM 位置，使有限 PE 上也能形成跨 block 的连续 wavefront；这改变的是时间模型和系统边界，而不是算子 representation。
