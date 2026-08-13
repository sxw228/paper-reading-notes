# HDagg: Hybrid Aggregation of Loop-carried Dependence Iterations in Sparse Matrix Computations

作者：Behrooz Zarebavani；Kazem Cheshmi；Bangtian Liu；Michelle Mills Strout；Maryam Mehri Dehnavi  
出处：IEEE International Parallel and Distributed Processing Symposium（IPDPS，IEEE 国际并行与分布式处理研讨会）  
年份：2022  
DOI：10.1109/IPDPS53621.2022.00121  
Zotero key：DTKJJEP8  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：这篇论文解决的不是稀疏算子本身怎么计算，而是带 loop-carried dependence 的稀疏迭代应当按什么顺序、以什么粒度映射到多核 CPU，才能同时保住 locality、load balance 与低 synchronization。** 作者把外层循环的每次迭代视为 DAG 顶点，把“后一次迭代读取前一次迭代写出的值”表示为有向边；对 SpTRSV 而言，一行是否依赖另一行可直接从 CSR 的列索引关系得到。[pdf:E05]（PDF 物理页 3，Listing 1 与其上方正文）

真正困难在于这些目标互相拉扯。按 wavefront 执行容易保证依赖正确，却会在每层产生 barrier，并把每行非零数不同造成的工作量差异暴露成负载不均；把依赖相近的迭代放到同一核可以复用数据，却可能把可并行顶点锁进同一分区。论文聚焦的 non-tree DAG 更棘手：SpIC0、SpILU0，以及预条件迭代求解器中的 SpTRSV，都可能不满足 elimination tree 一类方法依赖的树结构假设。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）[pdf:E04]（PDF 物理页 2，Introduction 末段）

它的重要性来自复用场景。稀疏三角求解和不完全分解常位于迭代求解器内，同一个 sparsity pattern 与调度会被反复使用；因此，一次 inspector 的成本可以由后续大量 executor 调用摊薄。论文用 NRE（Number of Required kernel Executions）专门衡量这一点，并报告 HDagg 对 SpIC0、SpILU0 的平均 NRE 小于一次 kernel execution。[pdf:E20]（PDF 物理页 10，Fig. 9、Eq. (2) 与 Inspection Overhead）这使调度质量不只是单次 kernel 的微优化，而可能直接改变整个线性求解流程的总时间。

## § 2 — 前人工作与不足

以下定位均是**论文对 prior work 的直接概括**，本卡没有联网独立复核相关文献。

DAGP 以减少 partition 间 edge cut 来改善 locality，但分区之间仍可能存在依赖，导致可同时运行的分区不足；论文把它概括为“locality 较好，但 average parallelism 受限”。Wavefront 方法按拓扑层推进，每个 wavefront 内并行、层间用全局 barrier；critical path 越长，barrier 越多，而且每行工作量不同会造成同层内负载不均。SpMP 用 point-to-point synchronization 让不同 wavefront 的工作重叠，改善 balance，却仍大体沿 wavefront 顺序执行，跨层数据复用未必转化为 cache locality。LBC 通过 wavefront coarsening 兼顾并行与同步，但其关键 cut 逻辑针对 tree DAG；面对 non-tree DAG 时需要 chordalization，新增依赖边会压低原有 parallelism。[pdf:E02]（PDF 物理页 1，Introduction 右栏）

Fig. 1 把差异压缩成同一个 13 顶点示例：Wavefront 使用多次全局同步；SpMP 以点到点依赖重叠层间执行；DAGP 的两个分区因分区间依赖无法并行；LBC 加边后形成长 serial region；HDagg 则形成三个 coarsened wavefront，并在每个 wavefront 内保留两路并行工作。[pdf:E03]（PDF 物理页 2，Fig. 1 与 caption）

因此，论文看到的缺口不是“再做一次 graph partitioning”，而是：**先识别值得放在同一核上的依赖密集迭代，再只在仍能形成足够独立 connected components 的范围内合并 wavefront。** 这个分解避开了 DAGP 只优化 edge cut、SpMP 只优化重叠、LBC 依赖树结构的单一目标局限。[pdf:E04]（PDF 物理页 2，Introduction 末段与 Motivating Example 开头）

## § 3 — 重建作者的思考路径

**基于论文证据的重建如下。**

第一步，先承认“合法并行度”和“数据复用位置”不是同一对象。拓扑层告诉系统哪些顶点此刻可执行，却不告诉系统哪些前后依赖顶点应当留在同一 cache；反过来，纯 graph partitioning 能把相连顶点放近，却不保证这些分区同时 ready。Fig. 1 中几种 schedule 的失败模式正好把这两个目标拆开了。[pdf:E03]（PDF 物理页 2，Fig. 1）

第二步，把 locality 问题局部化。若 transitive edge 被删去后，一批顶点形成单 sink 的 subtree，那么这些顶点之间存在紧密的直接依赖链，顺序执行在同一线程上有机会把生产者数据直接留给消费者。作者据此选择“近似 transitive reduction + modified BFS 找 subtree”，而不是一开始就对整个 DAG 做粗粒度 partition。[pdf:E08]（PDF 物理页 4，Section IV-A/IV-B）

第三步，再处理全局并行度。聚合后的顶点不能任意跨依赖执行，因此作者把连续 wavefront 暂时合并，计算其中的 connected components，并把 component 当作不可拆工作单元装进最多 `p` 个 bins。只要新的合并会让这些 bins 失衡，就在前一位置 cut；这等价于沿 wavefront 顺序做受 balance 约束的局部搜索。[pdf:E07]（PDF 物理页 4，Algorithm 1）[pdf:E10]（PDF 物理页 5，Section IV-C）

最后，作者需要一个无需实际运行 kernel 就能做 cut 的指标，于是引入 PGP，以静态成本估计“若完全均衡，最多还能减少多少执行时间”。这把一次 schedule 决策变成了可在 inspector 中完成的近似，而不是依赖在线 profiling。[pdf:E12]（PDF 物理页 6，Fig. 4、Eq. (1) 与 Section IV-D）

## § 4 — 核心 Intuition

先把**必须近距离串行、且可能共享数据**的迭代绑在一起，再把相邻 wavefront 合并到“不会失去足够可并行 connected components”的边界。第一步用结构性聚合换 locality，第二步用 PGP 与 bin packing 限制这种聚合对 load balance 的伤害。核心不是把 synchronization、locality 或 balance 中某一项做到极致，而是生成一个三者都不过度恶化的静态 schedule。[pdf:E09]（PDF 物理页 5，Fig. 2 与 caption）[pdf:E10]（PDF 物理页 5，Section IV-C）

## § 5 — 具体方法与完整 Pipeline

**输入与输出。** HDagg 输入依赖图 `G=(V,E)`、顶点成本函数 `C`、物理核数 `p` 和 load-balance threshold `ε`，输出 schedule `S`。`S` 由顺序执行的 coarsened wavefront 构成；每个 coarsened wavefront 又含若干可并行执行的 width-partitions。论文采用“每个顶点触达的 non-zero 数”作为默认静态成本。[pdf:E08]（PDF 物理页 4，Section IV-A）

**以论文的 SpTRSV/示意 DAG 为例，完整 pipeline 是：**

1. **从稀疏 kernel 建 DAG。** 在 CSR SpTRSV 中，顶点对应外层行迭代；若第 `c` 行读取由第 `k` 行写出的 `x[k]`，则建立 `k→c`。论文的 C++ driver 对 SpTRSV、SpIC0、SpILU0 从输入矩阵得到 DAG 与 cost；为降低 inspector 开销，实际实现不显式复制一份 DAG，而是复用矩阵结构。[pdf:E05]（PDF 物理页 3，Listing 1）[pdf:E06]（PDF 物理页 3，Listing 2 与 Framework Overview）

2. **近似 transitive reduction。** 若存在 `i→j→f`，两跳近似会删去可由该路径蕴含的 `i→f`。删边不改变合法依赖顺序，却让“直接依赖形成的 subtree”更容易暴露。[pdf:E07]（PDF 物理页 4，Algorithm 1 Lines 1–20）[pdf:E08]（PDF 物理页 4，Section IV-B）

3. **聚合依赖密集顶点。** 以 reduced DAG 的 sink 为起点做 modified BFS；当某顶点及其 parents 仍构成 tree 时，把 parents 加入同一组。Fig. 2 中红色 transitive edges 被移除后，若干顶点被合并成粉色 grouped vertices，得到 tree-grouped DAG `G''`。[pdf:E09]（PDF 物理页 5，Fig. 2）

4. **建立 wavefront 并尝试连续合并。** 对 `G''` 求 `W1…Wl`。论文示例先把 `W1` 与 `W2` 合并；继续纳入 `W3` 会把原本可分到不同核的工作连成更大的 connected component，于是在该处 cut，最终形成 `CW1=[W1,W2]`、`CW2=[W3]`、`CW3=[W4]`。Fig. 3 的高亮路径展示了这类“merge/not merge”选择。[pdf:E09]（PDF 物理页 5，Fig. 2(d)）[pdf:E11]（PDF 物理页 6，Fig. 3 与 caption）

5. **connected components + first-fit bin packing。** 每个候选 coarsened wavefront 先求 connected components，再把 component 作为整体装入最多 `p` 个 bins；first-fit 把 component 放入第一个尚未达到 balance 条件的 bin。bin 内按较小 vertex ID 优先排列，以争取 spatial locality。若 PGP 表明继续合并会失衡，就提交上一个 balanced partition 并开始新的 coarsened wavefront。[pdf:E10]（PDF 物理页 5，Section IV-C）

6. **执行。** Executor 依次推进 coarsened wavefront，并用 OpenMP 并行运行同一 wavefront 内的 width-partitions；所有 schedule 在输入 sparsity pattern 已知后静态生成。[pdf:E06]（PDF 物理页 3，Framework Overview）

**EMT + FPGA 维度的明确边界。** 本文没有 EMT 物理模型、开关/事件处理、time stepping 或 multi-rate 机制；它处理的是稀疏线性代数 kernel 的依赖调度。数值精度、浮点数据类型与误差传播未报告。实现平台是 C++/OpenMP 的 shared-memory CPU；没有 FPGA pipeline、BRAM/URAM、memory banking、DSP 映射、时钟频率或实时步长结果。[pdf:E06]（PDF 物理页 3，Framework Overview）[pdf:E14]（PDF 物理页 7，Experimental Results 的平台与编译设置）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有数值算法收敛性推导；其核心数学是**静态负载不均衡代理**与 inspector complexity。

对第 `i` 个 core，分配到的工作量定义为

\[
B_i=\sum_{j\in I_i} C_j,
\]

其中 `I_i` 是分到该 core 的顶点集合，`C_j` 是顶点成本。PGP 定义为

\[
PGP=1-\frac{\bar B}{\max_{1\le i\le p}(B_i)}. \tag{1}
\]

当所有核工作量相同，平均值等于最大值，`PGP=0`；最坏情况下全部工作落在一个核上，`PGP=1-1/p`。论文给出的直观例子是 `p=2` 且所有任务落到单核，此时 `PGP=50%`，意指若把负载完全均衡，理论上可把 runtime 再降低一半。[pdf:E12]（PDF 物理页 6，Eq. (1) 与其后解释）

这个公式本质上只看“最慢 core 相对平均 core 多出多少工作”。它适合 cut 判定，因为 coarsened wavefront 的完成时间由最慢 width-partition 决定；但它不是硬件执行时间模型，不含 cache miss、NUMA、分支、同步等待或 prefetch 行为。作者用 PAPI/Vtune 得到 measured potential gain，并在 SpTRSV 数据上报告 `PGP` 与实测 `PG` 的线性关系 `R²=0.83`，据此把它当作可用近似，而不是精确预测器。[pdf:E12]（PDF 物理页 6，Fig. 4 与 Section IV-D）

复杂度方面，论文采用两跳 transitive reduction 近似，其时间复杂度写为

\[
O\bigl(|E|\,E[D]+|V|\,Var[D]\bigr),
\]

其中 `D` 是每行 non-zero 数，`E[D]` 与 `Var[D]` 分别是其期望与方差；modified BFS 聚合阶段为 `O(|E|+|V|)`。[pdf:E13]（PDF 物理页 6，Section IV-E）对每次 wavefront 合并求 connected components 是第二阶段最贵部分：单核上总复杂度为 `O(l|E|\log|V|)`，有足够并行核时收敛到 `O(l\log|V|)`，其中 `l` 为 wavefront 数。[pdf:E14]（PDF 物理页 7，Section IV-E 续）

需要注意一个源文内部不一致：Algorithm 1 第 36 行写的是在 `PGP(S)<ε` 时关闭 bin packing，而随后正文解释为“累计不均衡高于 threshold”时关闭。两处条件方向相反，复现者不能仅凭论文自行确定最终实现语义。[pdf:E07]（PDF 物理页 4，Algorithm 1 Lines 36–38）[pdf:E10]（PDF 物理页 5，Section IV-C 末段）

## § 7 — 实验设计与结论

**实验范围。** 作者使用 34 个 SuiteSparse SPD matrices；选择 SPD 是为了让 SpIC0 数值稳定，矩阵规模覆盖约 `51×10³` 到 `59×10⁶` 个 non-zeros。平台为 20-core Intel Xeon Gold 6248 与 64-core AMD EPYC 7742；主要机制分析在 Intel 上进行。代码用 GCC 8.3.0、`-O3`、close thread binding 编译，每项取 10 次执行的 median；所有矩阵先经 Metis 重排。对比对象是 MKL、DAGP、LBC、Wavefront 与 SpMP。[pdf:E14]（PDF 物理页 7，Experimental Results）

**问题一：总体上是否更快？ → 实验：** 对 SpTRSV、SpIC0、SpILU0，在 Intel 与 AMD 上逐矩阵测 GFlops，并汇总 HDagg 相对各 baseline 的 speedup。**答案：** Intel 上跨三个 kernel，HDagg 相对 DAGP、LBC、Wavefront、SpMP 的平均 speedup 分别为 `3.87×、3.41×、1.95×、1.43×`；AMD 上分别为 `8.41×、7.01×、2.83×、1.10×`。对 MKL 只比较 SpTRSV，因为论文称 MKL 的 SpIC0/SpILU0 实现不是并行版本。[pdf:E16]（PDF 物理页 8，Table I 与 Executor Evaluation）

**问题二：收益是否覆盖多数矩阵？ → 实验：** Fig. 5 展示每个矩阵、每个 kernel 的 GFlops，并把 HDagg Step 1 与 Step 2 的增量画成 stacked bars。**答案：** SpTRSV 与 SpIC0 上，HDagg 在超过 `94%` 的矩阵中优于其他算法；SpILU0 上这一比例为 `73%`，说明最难 kernel 已出现明显失效区间。[pdf:E15]（PDF 物理页 7，Fig. 5）[pdf:E16]（PDF 物理页 8，Executor Evaluation）

**问题三：速度来自 locality、balance 还是 synchronization？ → 实验：** 在 Intel 的 SpILU0 上，用 average memory access latency 表示 locality，用 measured potential gain 表示 load balance，用 point-to-point synchronization 等价值表示同步成本。**答案：** 相对 DAGP，HDagg 的 locality improvement、load-balance improvement 与 synchronization reduction 分别为 `2.66×、2.60×、5.07×`；相对 SpMP，则分别为 `1.44×、0.34×、1.49×`。也就是说，HDagg 对 SpMP 并没有更好的 balance，却仍凭 locality 与较少同步取得总体优势；这支持论文“组合目标优于单项最优”的解释。[pdf:E17]（PDF 物理页 8，Table II、Fig. 6 与正文）

**问题四：何时会失败？ → 实验：** 作者按 matrix size 与 average parallelism 把矩阵分成三类，并把 HDagg 与 SpMP/Wavefront 中较优者比较。**答案：** 对 `nnz>10⁷` 的大矩阵，`93%` 的矩阵更快，平均 speedup `1.75×`；对较小但 average parallelism `>400` 的矩阵，`100%` 更快，平均 `1.26×`；对较小且 average parallelism `<400` 的矩阵，只有 `63%` 更快，平均 speedup 降到 `0.90×`。前两类中，HDagg 的 locality improvement 与 speedup 呈 `R²=0.95` 的相关性；第三类的低 non-zeros per wavefront 使可利用的数据复用不足，而 SpMP/Wavefront 的 balance 优势开始主导。[pdf:E18]（PDF 物理页 9，Table III、Fig. 7、Fig. 8）[pdf:E19]（PDF 物理页 9，分类分析正文）

**问题五：inspector 是否值得？ → 实验：** 用

\[
NRE=\frac{inspector\ time}{sequential\ time-parallel\ time} \tag{2}
\]

计算摊薄 inspector 所需的 kernel 次数。**答案：** SpTRSV 上，LBC、Wavefront、SpMP、HDagg 的平均 NRE 分别为 `24、9.4、21、16`；DAGP 为 `5305`，因此未画入图。HDagg 在 SpIC0 与 SpILU0 上的平均 NRE 分别为 `0.38` 与 `0.41`。[pdf:E20]（PDF 物理页 10，Fig. 9、Eq. (2) 与正文）

**不能外推的范围。** 这些结论来自经 Metis 重排的 SPD matrices、shared-memory CPU 与三个固定 sparsity pattern kernel；论文没有给出非 SPD、动态 sparsity、distributed memory、GPU/FPGA、能耗、数值误差或端到端 Krylov convergence 结果。因此，Table I 的 speedup 不能直接等价为完整求解器、其他架构或实时系统的收益。[pdf:E14]（PDF 物理页 7，实验设置）

## § 8 — Take-aways

**5 句话：**

1. HDagg 的主要贡献是把 locality-oriented vertex aggregation 与 load-balance-preserving wavefront coarsening 串成同一 inspector，而不是发明新的稀疏数值 kernel。[pdf:E07]（PDF 物理页 4，Algorithm 1）
2. 第一阶段利用 transitive reduction 后的 subtree 把可能有生产者—消费者复用的迭代固定到同一线程，第二阶段才决定这些组能跨多少个 wavefront 合并。[pdf:E08]（PDF 物理页 4，Section IV-B）[pdf:E09]（PDF 物理页 5，Fig. 2）
3. PGP 让 cut 可以静态完成，但它只是基于顶点成本的近似，论文自身的 SpTRSV 验证也不是完美相关。[pdf:E12]（PDF 物理页 6，Fig. 4 与 Eq. (1)）
4. 实验最有说服力的现象不是某个最高 speedup，而是 HDagg 在 balance 不如 SpMP 时仍能因 locality 获胜，说明稀疏 DAG 调度不能只优化并行度。[pdf:E17]（PDF 物理页 8，Table II 与 Fig. 6）
5. 方法的边界同样清楚：当每个 wavefront 的复用机会少且 average parallelism 低时，HDagg 的平均收益会跌破基线。[pdf:E18]（PDF 物理页 9，Table III）[pdf:E19]（PDF 物理页 9，分析正文）

**3 句话：** HDagg 先做依赖密集顶点聚合，再用 connected components、bin packing 与 PGP 决定 wavefront cut。[pdf:E10]（PDF 物理页 5，Section IV-C）它在两种 CPU、三个 sparse kernels 上总体优于论文选取的 baseline，但最困难的 SpILU0 已暴露出明显矩阵依赖性。[pdf:E15]（PDF 物理页 7，Fig. 5）真正可迁移的认识是：稀疏依赖调度的价值函数必须同时包含数据复用、最慢分区与同步边界。

**1 句话：** HDagg 证明了对 non-tree sparse DAG，“先聚合复用、再受约束地合并并行层”比单独追求最少 edge cut、最少 barrier 或最均匀 wavefront 更有效。[pdf:E03]（PDF 物理页 2，Fig. 1）

## § 9 — 最脆弱的假设

**最脆弱的假设是：DAG 上的结构接近性与“触达 non-zero 数”足以同时代理真实数据复用和真实执行成本。** 这个假设一旦失效，两阶段都会被误导：第一阶段会把“边很多但复用很弱”的顶点做成难以拆分的大组；第二阶段会把 `\sum C_j` 相等误判成 runtime 相等，从而在 PGP 看似很低时仍产生 straggler。[pdf:E08]（PDF 物理页 4，成本定义与 densely connected vertices）[pdf:E12]（PDF 物理页 6，Eq. (1)）

论文给了两类支持。其一，PGP 与 SpTRSV 的 measured PG 达到 `R²=0.83`；其二，在高复用的两类矩阵中，locality improvement 与 speedup 达到 `R²=0.95`。[pdf:E12]（PDF 物理页 6，Fig. 4）[pdf:E18]（PDF 物理页 9，Fig. 8）但这些证据也暴露了缺口：PGP 的直接相关性图只报告 SpTRSV；而低 non-zeros per wavefront、低 average parallelism 类别的平均 speedup 为 `0.90×`，说明结构代理无法在所有 sparsity pattern 上保证收益。[pdf:E18]（PDF 物理页 9，Table III）[pdf:E19]（PDF 物理页 9，分类分析）

实际中，同样的 row nnz 可以对应完全不同的 cache/TLB/NUMA 行为：一组行反复命中小工作集，另一组行随机触达超出 LLC 的 factor；PGP 会给出相同成本，但后者会慢得多。由于 HDagg 生成静态 width-partitions，慢分区会决定整个 coarsened wavefront 的完成时间。再加上 Algorithm 1 与正文对“何时 DisableBinPack”存在条件方向冲突，核心假设失效时系统是否真的退回细粒度任务也无法仅由论文确定。[pdf:E07]（PDF 物理页 4，Algorithm 1）[pdf:E10]（PDF 物理页 5，Section IV-C 末段）

## § 10 — 最小复现实验

**一周内最值得复现的是：PGP 是否真的能预测 SpTRSV 的实测 imbalance，以及 locality 收益是否足以抵消 balance 损失。** 不必复现全部三个 kernel，也不必重建所有 baseline。

数据上，从 SuiteSparse SPD matrices 中各选一组高 non-zeros per wavefront、高 average parallelism，以及一组两者都低的矩阵；保留论文的 Metis preprocessing。实现上只做 CSR SpTRSV、标准 Wavefront baseline、HDagg 的两阶段 inspector，并把 Algorithm 1 第 36 行的两种条件方向都作为独立 variant，避免把论文内部歧义悄悄“修正”。DAG 构造、cost 与 executor 接口可直接按 Listing 1/2 重建。[pdf:E05]（PDF 物理页 3，Listing 1）[pdf:E06]（PDF 物理页 3，Listing 2）[pdf:E07]（PDF 物理页 4，Algorithm 1）

测量四项即可：executor wall time；每线程 cycles 或完成时间；LLC miss/average memory access latency；静态 PGP 与由每线程实际时间计算的 measured PG。另记录 inspector time，并用 Eq. (2) 计算 NRE。[pdf:E12]（PDF 物理页 6，PGP）[pdf:E20]（PDF 物理页 10，NRE）

支持核心 claim 的结果应当是：高复用矩阵上，Step 1/2 带来一致的 locality 改善，PGP 与 measured PG 同方向变化，且总时间优于 Wavefront；低复用矩阵上允许收益减弱，但失败应能被 PGP 或 connected-component 数量提前解释。反驳核心 claim 的结果是：PGP 经常判断 balanced，而实际线程时间明显分叉；或者 locality 指标没有改善，速度差异主要由偶然的 thread placement、频率或 NUMA placement 解释。这个实验同时能判定论文中 `DisableBinPack` 条件的哪种实现更符合作者文字描述。

## § 11 — 最强反例设计

**最强反例应让 HDagg 的 `G` 与 `C` 看起来完全平衡，但让真实 memory cost 极不平衡。** 构造一族来自 SPD 系统 Cholesky/IC 因子的 block lower-triangular SpTRSV inputs：两个可并行 width-partitions 拥有相同顶点数、相同每行 nnz，因此 `\sum C_j` 相同；其中一组依赖反复命中一个能留在 cache 的紧凑 `x`/factor 工作集，另一组依赖分散到远大于 LLC 的地址范围，或被固定到远端 NUMA pages。两组在图上都形成相似的 subtree 与 connected components，因此第一阶段会同样聚合，第二阶段会给出接近 `PGP=0` 的“完美平衡”判断。[pdf:E08]（PDF 物理页 4，结构聚合与成本函数）[pdf:E12]（PDF 物理页 6，PGP 定义）

执行时，cold/remote 一侧成为稳定 straggler，coarsened wavefront 必须等待它；HDagg 既没有真实 runtime cost，也不能把已形成的 component 在本 wavefront 内重新拆分。用同一 DAG 比较 HDagg、Wavefront、SpMP 风格的更细粒度 schedule，并排除 inspector time。如果 HDagg 的 memory latency 没有改善、load imbalance 明显上升且 executor 仍更慢，就不是“某个矩阵偶然不适合”，而是直接证明 `nnz + graph proximity` 不能支撑论文的通用 balance/locality 机制。论文第三类矩阵中仅 `63%` 获胜、平均 `0.90×` 的结果已经给出这种反例可能存在的经验信号。[pdf:E18]（PDF 物理页 9，Table III）[pdf:E19]（PDF 物理页 9，分类分析）

最强替代解释是 NUMA page placement 而非算法本身。为排除它，应在 interleave、first-touch 和单 NUMA node 三种内存策略下重复；若只有远端放置时失败，则反例攻击的是实现环境，若单节点下同样因 working-set footprint 失衡而失败，才真正击中 PGP 与静态聚合假设。

## § 12 — Follow-up Research Bet

**候选判断，不声明 novelty：把单次 CPU schedule 提升为“跨调用驻留的时空 reuse-hypergraph FPGA dataflow”。** 新研究问题是：能否利用迭代求解器反复调用同一 sparsity pattern 的事实，把 non-tree SpTRSV，以及同一 sparsity pattern 下重复出现的 incomplete-factorization workloads，编译成长期驻留在 FPGA 上的 persistent dataflow，而不是每次调用都从 DRAM 重新读取因子并重新经历 wavefront 边界？论文已经证明 locality 在高复用矩阵上与 speedup 强相关，并表明 inspector 可由重复调用快速摊薄；但它只在单次 kernel 的顶点 DAG 上做 CPU 分区，没有把“数据值的生命周期”和“跨调用复用”变成一等对象。[pdf:E09]（PDF 物理页 5，Fig. 2 的两阶段聚合）[pdf:E18]（PDF 物理页 9，Fig. 8）[pdf:E20]（PDF 物理页 10，NRE 与迭代调用讨论）

**新能力与因果链。** Inspector 不再只输出 coarsened wavefront，而是把每个 matrix/factor element 及其消费者集合提升为 reuse hyperedge，并为 hyperedge 标注跨行、跨 kernel invocation 的 lifetime。随后联合切分顶点与 lifetime，生成 temporal tiles：每个 tile 把固定的 matrix/factor 数据长期保留在 BRAM/URAM 中，把 tile 映射到 persistent PE cluster；tile 间依赖用带 backpressure 的 token FIFO 传输，host 每次只注入新的 RHS 或边界值。因果链是“跨调用 lifetime 可见 → 因子数据驻留 → DRAM traffic 随调用次数摊薄 → tokenized dependency 取代全局 wavefront barrier → 多次 solve 形成稳定 pipeline throughput”。这首次使 non-tree sparse solve 成为可持续流式服务，而不只是一次性的并行 kernel。

它至少改变四个基本设计变量：状态表示从 vertex DAG 变为 vertex–data-lifetime hypergraph；时间尺度从单次 kernel 扩展到连续 solver iterations；硬件映射从 CPU thread partitions 变为 FPGA spatial PE/FIFO topology；评价对象从单次 GFlops 扩展为 warm-up 后 throughput、DRAM bytes per solve 与 energy per solve。与论文内的 DAGP、LBC、Wavefront、SpMP 相比，差异不在“换一个 partitioner”，而在于跨越调用边界并把数据驻留期纳入 correctness-preserving schedule；本文未提供完整的近期 FPGA/streaming sparse-solver 文献检索，因此这里只能作为候选研究押注。

**论文特异依据。** 方法侧，HDagg 的第一阶段已说明 producer–consumer 邻近可以转化为 locality，第二阶段已给出 non-tree DAG 上 connected-component-aware 的依赖分块。[pdf:E09]（PDF 物理页 5，Fig. 2）[pdf:E10]（PDF 物理页 5，Section IV-C）实验侧，前两类高复用矩阵的 locality improvement 与 speedup 达到 `R²=0.95`，而低复用类别平均只有 `0.90×`，正好提供“何种矩阵值得驻留、何种矩阵不值得”的可证伪边界。[pdf:E18]（PDF 物理页 9，Table III 与 Fig. 8）[pdf:E19]（PDF 物理页 9，分类分析）另外，NRE 结果说明结构分析适合被多次调用摊薄，这为更昂贵的 hardware mapping inspector 提供了系统级动机。[pdf:E20]（PDF 物理页 10，Fig. 9）

**最大收益与最大风险。** 最大收益是把当前受 memory latency 支配的稀疏三角/不完全分解调用变成 factor-resident pipeline，使 throughput 和 energy 不再随每次 solve 的完整 DRAM traffic 线性增长。最大科学风险是 non-tree hyperedge 的边界状态与路由规模膨胀，BRAM/URAM 容量不足会迫使频繁换入换出；若跨调用只有结构复用而没有足够的数据复用，persistent mapping 可能退化为昂贵的固定布线。论文第三类矩阵正提示这一风险不是边角问题。[pdf:E18]（PDF 物理页 9，Table III）

**首个证伪实验。** 选一类高 non-zeros per wavefront 矩阵和一类低复用矩阵，做一个保持 PE 数、on-chip memory 容量与 tile size 完全相同的 cycle-accurate/HLS 原型。对照组每次 invocation 都重新从外存装入 tile；实验组仅新增跨调用 lifetime hyperedges与 factor residency。测 DRAM bytes per solve、steady-state throughput、FIFO stall 与数值一致性。最强替代解释是收益仅来自更大的普通 blocking/cache：因此只有当两组 tile 大小和存储预算相同、收益随重复调用累积，并且人为打断 lifetime 后收益消失，才能把结果归因于“跨调用驻留”这一核心机制，而不是一般 cache tiling。

**Wild-card alternative：** 放弃固定 Metis preprocessing，把 matrix permutation、coarsened-wavefront 边界与 chiplet/NoC 拓扑联合表示为一个可优化的 communication hypergraph，目标是直接合成“稀疏结构—物理互连”共设计，而不是把既定 DAG 被动映射到现有硬件。
