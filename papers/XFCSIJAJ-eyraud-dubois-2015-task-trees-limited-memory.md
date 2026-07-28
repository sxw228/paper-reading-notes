# Parallel Scheduling of Task Trees with Limited Memory

- 作者：Lionel Eyraud-Dubois、Loris Marchal、Oliver Sinnen、Frédéric Vivien
- 出处：Inria Research Report No. 8606（本卡唯一源 PDF 所载版本）
- 年份：2015（正式出版年份；源 PDF 标注 October 2014）
- DOI：10.1145/2779052
- Zotero key：XFCSIJAJ

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究一个很具体、也很容易被“只追求并行度”掩盖的问题：给定一棵有根 in-tree，节点是任务，边上的数据必须从子任务完成后一直保留到父任务完成；在多个共享同一内存的相同处理器上，怎样安排节点的开始时间，才能同时压低总完成时间 makespan 和整个执行期间的 peak memory？作者把任务的运行时间记为 \(w_i\)，执行期间的程序或临时数据量记为 \(n_i\)，输出文件大小记为 \(f_i\)。一个父节点开始时，所有子节点输出、自己的执行数据和自己的输出必须同时在内存里，结束后才释放输入和执行数据，只留下输出供父节点使用。[pdf:E04]（PDF 物理页 7，§3.1）

这不是单纯“多核越多越快”的问题。更积极地并行展开多个子树，会更早地产生并同时保留许多尚未被父节点消费的输出，因而可能缩短 makespan，却抬高 memory；更保守地一次收完一个子树，则常常节省 memory，却让处理器空闲。作者把 makespan 定义为第一片叶开始到根任务结束的时间，把 memory 定义为任一时刻正在驻留和正在计算的数据之和的最大值。[pdf:E05]（PDF 物理页 8，§3.2）

论文的直接工程动机是稀疏矩阵的 multifrontal factorization：其 assembly tree 或 elimination tree 同时表达计算依赖和中间数据存储，矩阵足够大时，坏的遍历次序可能迫使程序使用 swap 或 out-of-core 路径，而这类较慢存储会显著拖累执行。[pdf:E02]（PDF 物理页 5，§1）论文也指出，类似的大文件 task graph 出现在 image processing、genomics、geophysical simulation 等 scientific workflow 中。[pdf:E03]（PDF 物理页 6，§2.2）

因此，论文真正要解决的不是“找一个唯一最优调度”，而是建立一个可解释的双目标边界：哪些 memory/makespan 组合在理论上不可能同时保证，实际又应该为不同内存预算选择哪一种 heuristic。摘要明确把工作概括为复杂度与不可近似性分析、覆盖不同折中的实用 heuristics，以及使用 realistic elimination trees 的实验评价。[pdf:E01]（PDF 物理页 3，Abstract）

## § 2 — 前人工作与不足

在单处理器情形，问题已有成熟基础。Liu 的早期工作先求受 postorder 限制的 memory-minimizing traversal，后续工作给出不受 postorder 限制的一般问题的最优算法。论文同时提醒：postorder 在构造反例上可以任意差于真正的 memory optimum；但它能一次完整处理一棵子树，结构自然，已被 MUMPS 等稀疏矩阵软件采用，并且在真实 elimination tree 上往往接近最优。[pdf:E02]（PDF 物理页 5，§1）

在并行 multifrontal solver 中，已有工作会针对 dynamic pivoting 改变节点/边权的情况做 memory-aware dynamic scheduling，也会把 task parallelism 与 tree parallelism 一起纳入；但这些工作主要改善具体 solver 的内存管理。本文刻意退回一个更简单的共享内存模型，试图提炼“并行树调度为什么会产生 memory/makespan 冲突”这一基础问题。[pdf:E03]（PDF 物理页 6，§2.1）

理论上，sequential pebble game 已解释寄存器或内存最少需要多少“pebble”：一般 DAG 在禁止 recomputation 时是 NP-hard，允许 recomputation 的一般问题是 PSPACE-complete，而树形图的 sequential 版本可多项式求解。作者声称，之前没有工作在 parallel machine 上同时最小化 memory 和 total execution time；这正是本文要补的空白。[pdf:E03]（PDF 物理页 6，§2.3）这里应严格区分来源：这些复杂度陈述是论文对相关文献的概述，不是本文重新证明的全部结果；本文自己的新增结果从 §4 开始。

## § 3 — 重建作者的思考路径

下面是基于论文背景与问题设置重建的合理推断，不是作者逐句陈述的研究日志。

第一步，一个研究者会从 sequential elimination-tree traversal 出发：如果只有一个处理器，完整收完一个子树再去下一个子树，通常能控制同时驻留的中间结果；因此 postorder 是很自然的 memory 基线。[pdf:E02]（PDF 物理页 5，§1）

第二步，一旦加入多个处理器，最直接的加速方式是并发处理多棵子树。但每棵已部分或全部完成的子树都会留下等待父节点的输出，所以“增加活跃子树数”同时增加可利用并行度和驻留数据。这提示 memory 与 makespan 可能不是两个可以各自优化后简单拼接的目标，而是同一调度次序上的结构性冲突。[pdf:E05]（PDF 物理页 8，§3.2）

第三步，先把所有文件和处理时间都设为单位权重，得到 parallel pebble game。若在这个最简单模型里加入 memory bound 就已让问题 NP-complete，并且不存在两个目标的常数比 simultaneous approximation，那么复杂度并非来自稀疏矩阵权重估算或某个 solver 的工程细节。[pdf:E06]（PDF 物理页 9，Theorem 1）[pdf:E07]（PDF 物理页 10，Lemma 1 与 Theorem 2）

第四步，既然统一最优保证不可得，算法设计就不应再追求一个“包打天下”的 heuristic，而应沿着折中轴布局：一端尽量继承 sequential memory-optimal traversal，另一端尽量遵循 critical path，再补上能接受显式 memory limit 的安全版本。论文 §5 正是按 ParSubtrees、两种 list scheduling、两种带限制的 pseudo-list scheduling 和 MemBookingInnerFirst 逐步展开。[pdf:E09]（PDF 物理页 16，§5）

## § 4 — 核心 Intuition

核心 intuition 是：并行调度的速度来自同时打开多条依赖分支，但这些分支越晚汇合，越多中间输出会同时滞留在共享内存；因此 memory 与 makespan 的冲突是树的汇合结构造成的，而不是实现偶然。理论部分先证明不存在对两个目标都给常数近似比的统一算法，实践部分再用不同优先级和“预留内存”把可用并行度控制在一个可接受的 memory budget 内。[pdf:E07]（PDF 物理页 10，§4.2）[pdf:E15]（PDF 物理页 26，§5.3.3）

## § 5 — 具体方法与完整 Pipeline

可以用一棵“多个叶任务产生数据、逐层 reduction、最终根任务汇总”的树来走完整 pipeline：

1. **建模输入。** 对每个节点 \(i\) 给出运行时间 \(w_i\)、执行数据 \(n_i\)、输出 \(f_i\) 和子节点集合。节点只有在所有子节点完成后才 ready；执行时必须同时放入全部子输出、\(n_i\) 和 \(f_i\)，完成后释放子输出和 \(n_i\)，保留 \(f_i\)。[pdf:E04]（PDF 物理页 7，§3.1）
2. **确定目标与预算。** 平台是 \(p\) 个 identical processors 共享一个 memory pool。调度器既记录最后一个节点结束的 \(C_{\max}\)，也记录全程最大驻留量 \(M\)；带预算版本还接收 memory limit \(B\) 或 \(M\)。[pdf:E05]（PDF 物理页 8，§3.2）
3. **偏 memory 的 ParSubtrees。** 先用 SplitSubtrees 反复拆当前工作量最大的子树，选择能让“并行子树阶段 + 剩余节点顺序阶段”预测 makespan 最小的切分；每棵选中子树内部再用 sequential memory-minimizing traversal。它对 peak memory 是 \(p\)-approximation，对 makespan 也是紧的 \(p\)-approximation。ParSubtreesOptim 把所有切出的子树按重量分配到负载最低的处理器，通常改善 makespan，但可能增加 memory。[pdf:E10]（PDF 物理页 19，§5.1）
4. **偏 makespan 的 list scheduling。** 通用 Algorithm 3 在每个完成事件把新 ready 节点放进 priority queue，并把队首任务发给空闲处理器。[pdf:E11]（PDF 物理页 20，Algorithm 3）ParInnerFirst 让 inner node 优先，叶节点遵循 sequential postorder，试图及时消费已就绪的中间文件；ParDeepestFirst 则按节点到根的 weighted depth 排序，优先推进 critical path。两者都是 \(O(n\log n)\)，但对 peak memory 都没有有限近似比。[pdf:E11]（PDF 物理页 20，§5.2.1）[pdf:E12]（PDF 物理页 21，§5.2.2）
5. **把一般树变成 memory-bound 算法可处理的 reduction tree。** 论文先用零运行时间的新叶子表示原来的 execution file，再为不满足 reduction property 的节点补虚拟叶子，使每个 inner node 的输出不大于输入之和，即 \(f_i\leq\sum_{j\in Children(i)}f_j\)。这个变换不改变 makespan，但可能提高变换后树的 memory requirement；把结果调度映射回原树时，原树的 peak memory 不会更高。[pdf:E13]（PDF 物理页 22，§5.3.1）
6. **两种 pseudo-list memory-limit 版本。** ParInnerFirstMemLimit 与 ParDeepestFirstMemLimit 只在当前占用加叶输出不超过 \(M\) 时启动叶节点；inner node ready 后仍立即启动。对没有 execution file 的 reduction tree，只要 \(M\) 不小于相同节点顺序的 sequential peak，它们就能处理完整棵树，且真实 peak 不超过 \(2M\)。代价是可能故意让处理器空闲，makespan 最坏退化为 \(p\)-approximation。[pdf:E25]（PDF 物理页 23，Theorem 5）[pdf:E14]（PDF 物理页 24，Algorithm 4 与证明）
7. **严格预算的 MemBookingInnerFirst。** 它从一个 sequential postorder \(PO\) 出发，为尚未 ready 的祖先节点提前预留将来生成输出所需的 `Contrib`。较晚执行的子节点先贡献可以由其输入释放后接续使用的空间；叶节点没有输入可转交，因此其预留量会进入启动条件。只有 `used + current leaf output + relevant booked memory ≤ M` 时才放行新叶子。[pdf:E15]（PDF 物理页 26，Contrib 递推）Algorithm 5 在任务完成事件上释放输入、更新父节点 booking，并在 inner/leaf 两类节点上应用不同的 admission test。[pdf:E16]（PDF 物理页 27，Algorithm 5）若 \(M\) 不小于该 \(PO\) 的 sequential peak，Theorem 6 保证整棵树完成且不超过 \(M\)；这是一条“预算可达且严格守住”的保证，而不是 makespan 最优保证。[pdf:E24]（PDF 物理页 28，Theorem 6）

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 单个节点为什么会制造内存峰值

节点 \(i\) 执行期间需要

\[
m_i=\left(\sum_{j\in Children(i)}f_j\right)+n_i+f_i.
\]

前一项是尚未释放的所有子输出，\(n_i\) 是执行文件或临时数据，\(f_i\) 是执行时已经要为输出留出的空间。节点完成后，前两类释放，\(f_i\) 留到父节点完成。[pdf:E04]（PDF 物理页 7，§3.1）直觉上，memory peak 不只由“当前运行多少任务”决定，也由已经完成但尚未被父节点消费的输出决定。

### 6.2 任意调度都逃不掉的面积下界

对 \(p\) 个处理器上的任意调度，论文给出

\[
C_{\max}\geq \frac{1}{p}\sum_{i=1}^{n}w_i,
\]

\[
M C_{\max}\geq
\sum_{i=1}^{n}
\left(n_i+f_i+\sum_{j\in Children(i)}f_j\right)w_i.
\]

第一式是总工作量下界；第二式把“内存占用 × 持续时间”看作面积：所有任务实际需要的总 memory-time 面积，不能超过高度为 peak \(M\)、宽度为 \(C_{\max}\) 的矩形。在 unit-weight pebble game 中，它简化为 \(C_{\max}\geq n/p\) 和 \(MC_{\max}\geq 2n-1\)。[pdf:E07]（PDF 物理页 10，Lemma 1）

### 6.3 复杂度与双目标边界

Theorem 1 从强 NP-complete 的 3-Partition 归约：即使 \(f_i=w_i=1,n_i=0\)，判断是否存在同时满足 makespan bound 和 memory bound 的树调度仍是 NP-complete。[pdf:E06]（PDF 物理页 9，Theorem 1 proof）因此，难点在最简 parallel pebble game 中已经存在。

Theorem 2 构造一棵根有 \(m\) 个子节点、每个子节点又有 \(m\) 个叶子的三层树。用 \(m^2\) 个处理器可以在 3 步完成，而最小 memory 是 \(2m\)；结合 \(MC_{\max}\geq2n-1\)，当 \(m\) 足够大时，任何固定 \(\alpha,\beta\) 都无法让同一算法同时成为 makespan 的 \(\alpha\)-approximation 和 memory 的 \(\beta\)-approximation。[pdf:E07]（PDF 物理页 10，Theorem 2）[pdf:E08]（PDF 物理页 11，Theorem 2 proof）这不是说某个具体实例不存在好折中，而是说不存在对所有树都维持两个固定常数保证的统一算法。

固定处理器数后，Theorem 3 把边界细化为

\[
\alpha(p)\beta(p)\geq
\frac{2p}{\lceil \log p\rceil+2}
\]

的不可突破区域。[pdf:E08]（PDF 物理页 11，Theorem 3）当要求 makespan 完全最优时，Theorem 4 给出更强结论：不存在同时达到 \((p-1-\varepsilon)\)-approximation peak memory 的算法。[pdf:E23]（PDF 物理页 13，Theorem 4）这些是 worst-case lower bound，不能直接读成真实矩阵上一定损失相同倍数。

### 6.4 heuristic 保证如何对应上述边界

ParSubtrees 用“每个并行子树的 memory 不超过整树 sequential optimum”得到并行阶段至多 \(pM_{seq}\)，并证明顺序汇合阶段也不超过同一界，因此是 peak memory 的 \(p\)-approximation。[pdf:E26]（PDF 物理页 18，Lemma 4）其 makespan 最坏同样是紧的 \(p\)-approximation。[pdf:E10]（PDF 物理页 19，makespan bound）

对 reduction tree，inner node 的输出不大于它将释放的输入。Algorithm 4 只把启动叶节点前的受控量限制在 \(M\)，inner node 启动时可能短暂同时保留输入和输出，所以证明使用 \(M_{new}\leq2M\)，得到两种 MemLimit heuristic 的 \(2M\) peak 保证。[pdf:E25]（PDF 物理页 23，Theorem 5）[pdf:E14]（PDF 物理页 24，证明中的 \(M_{new}\leq2M\)）MemBookingInnerFirst 则进一步把未来 inner output 的空间提前记入 booking；只要给定 \(M\) 至少等于所选 postorder 的 sequential peak，Theorem 6 保证最终完成且实际不超过 \(M\)。[pdf:E15]（PDF 物理页 26，booking 机制）[pdf:E24]（PDF 物理页 28，Theorem 6）

## § 7 — 实验设计与结论

### 问题一：六类策略是否真的形成 memory/makespan 梯度？

**实验。** 作者从 University of Florida Sparse Matrix Collection 选择 76 个中大型、方形、对称 pattern、非图矩阵，分别用 MeTiS 与 amd 排序，经 Matlab `symbfact` 生成 elimination tree，再做 1、2、4、16 种 relaxed node amalgamation，得到 608 棵 assembly tree。树规模为 2,000 到 1,000,000 个节点，深度 12 到 70,000，最大度 2 到 175,000；每个 heuristic 在 \(p=2,4,8,16,32\) 上用模拟并行执行评估。[pdf:E17]（PDF 物理页 29，§6.2）

节点权重来自 Cholesky factorization 的计算模型：若 \(\eta\) 是 amalgamated nodes 数，\(\mu\) 是相关 Cholesky 列的 nonzero 数，则

\[
n_i=\eta^2+2\eta(\mu-1),
\quad
w_i=\frac{2}{3}\eta^3+\eta^2(\mu-1)+\eta(\mu-1)^2,
\quad
f_i=(\mu-1)^2.
\]

这些权重用于模拟 factorization 的 memory 和 processing time，不是硬件实测。[pdf:E17]（PDF 物理页 29，§6.2）

**答案。** Table 1 显示清楚的梯度。ParSubtrees 与 ParSubtreesOptim 的平均 normalized memory 分别为 2.34、2.46，但 normalized makespan 为 1.40、1.33；ParInnerFirst 与 ParDeepestFirst 的平均 normalized memory 为 3.79、4.13，而 normalized makespan 降到 1.07、1.04。ParDeepestFirst 在 95.7% 场景拿到四种无约束 heuristic 中的 best makespan，却只在 3.0% 场景拿到 best memory；ParSubtrees 正好相反，best memory 占 81.1%，best makespan 仅 0.2%。[pdf:E18]（PDF 物理页 30，Table 1）这里的 makespan normalization 是对“总工作量/处理器数与 weighted critical path 二者最大值”的 lower bound，而不是已知最优值。

### 问题二：平均值是否掩盖灾难性 memory case？

**实验。** 作者把 76 个行为极端的树从 Figure 10 的总体平均中单列，在 Figure 11 展示四类 outlier。[pdf:E19]（PDF 物理页 32，§6.3）

**答案。** 相对排序仍大体相同，但 ParInnerFirst 与 ParDeepestFirst 在这些真实来源树上的 memory 可达到 sequential optimal memory 的约 100 倍，实证呼应了它们没有 peak-memory approximation ratio 的理论结论。[pdf:E19]（PDF 物理页 32，§6.3）这说明“通常很快”不能替代 memory safety guarantee。

### 问题三：给定显式 memory budget 时应选谁？

**实验。** 作者把原树按 §5.3.1 变成无 execution file 的 reduction tree，先求原树 postorder 的 sequential memory \(M_{seq}\)，再用 \(B=xM_{seq}\) 的多种 \(x\) 测试 memory-bounded heuristics；Figure 12 只画成功率超过 95% 的点。[pdf:E19]（PDF 物理页 32，§6.4）[pdf:E20]（PDF 物理页 33，Figure 12）

**答案。** 当 \(B<2M_{seq}\) 时，MemBookingInnerFirst 是唯一能运行且仍给出合理 makespan 的候选；当 \(2M_{seq}\leq B<5M_{seq}\) 或约 \(10M_{seq}\)（阈值随处理器数变化）时，ParInnerFirstMemLimit 开始可用且 makespan 更好；memory 充足时，ParDeepestFirstMemLimit 最快。[pdf:E19]（PDF 物理页 32，§6.4）Figure 13 进一步显示：在同一 budget 下，能真正利用更多可用 memory 的 heuristic 往往有更好的 makespan；optimized MemLimit 版本在紧预算下比非 optimized 版本利用更多空间。[pdf:E21]（PDF 物理页 34，Figure 13 与相邻正文）

### 不得外推的范围

实验全部是根据静态权重模拟的 shared-memory parallel execution，数据来源是 sparse-matrix assembly trees。论文没有 FPGA synthesis、BRAM/DSP utilization、板上 memory bandwidth、EMT numerical error、real-time step deadline 或多场站工况实验。作者自己在结论中把“顶层大任务内部并行”“distributed memory”以及 shared/distributed 混合平台列为仍需扩展的方向。[pdf:E22]（PDF 物理页 35，§7）因此，本节结果只能证明这些 heuristics 在论文模型和矩阵树数据上的 trade-off，不能直接当成 FPGA EMT 已验证结果。

## § 8 — Take-aways

### 用 5 句话总结

1. 树调度中的 memory 与 makespan 不是两个独立旋钮：并行展开分支会同时制造速度和驻留数据。[pdf:E05]（PDF 物理页 8，§3.2）
2. 即使所有任务和文件都是单位权重，带双约束的 parallel tree scheduling 仍是 NP-complete。[pdf:E06]（PDF 物理页 9，Theorem 1）
3. 不存在对任意树同时给 memory 与 makespan 固定常数近似比的统一算法，因此必须显式选择折中。[pdf:E07]（PDF 物理页 10，Theorem 2）
4. ParSubtrees 偏 memory，ParDeepestFirst 偏 makespan，而 MemBookingInnerFirst 能在可达前提下严格守住给定 memory limit。[pdf:E26]（PDF 物理页 18，ParSubtrees memory bound）[pdf:E24]（PDF 物理页 28，Theorem 6）
5. 608 棵 sparse-matrix assembly tree 的模拟支持这条梯度，但没有把结论验证到 FPGA、EMT 或 distributed-memory 平台。[pdf:E17]（PDF 物理页 29，§6.2）[pdf:E22]（PDF 物理页 35，§7）

### 用 3 句话总结

并行树调度的核心资源冲突是：越早并行产生子树结果，越可能缩短 makespan，也越可能抬高 peak memory。理论证明没有统一常数近似，实验则表明不同 heuristic 确实分布在从 memory-friendly 到 makespan-friendly 的不同位置。[pdf:E07]（PDF 物理页 10，Theorem 2）[pdf:E18]（PDF 物理页 30，Table 1）需要硬 memory cap 时，booking 比仅凭优先级排序更接近真正的 admission control。

### 用 1 句话总结

这篇论文把“树上并行度”从越多越好的直觉，改写成一个必须在 memory budget 下选择和证明的调度决策。

## § 9 — 最脆弱的假设

失败代价最大的假设不是 reduction property，因为论文给出了把一般树变换后再映射回来的办法；更脆弱的是：**真实执行可被一棵静态 in-tree、单一共享 memory pool、相同处理器和已知 \(w_i,n_i,f_i\) 充分描述。**

这个假设一旦不成立，理论中的关键动作“一个 inner node 完成就释放所有输入，只留下一个输出”便可能失真。真实系统可能有通信复制、bank conflict、cache 或 DMA buffer、数据跨步复用、任务内部并行、运行时间抖动，甚至 DAG 而不是 tree；此时 scalar peak memory 既未必代表真正资源瓶颈，weighted depth 也未必代表真正 critical path。作者的模型明确是 identical processors sharing a single memory，[pdf:E05]（PDF 物理页 8，§3.2）结论又明确提出未来需处理 large task 的内部并行与 distributed/shared memory 混合。[pdf:E22]（PDF 物理页 35，§7）

论文为这一假设提供的证据，是在 sparse Cholesky/assembly tree 上根据结构计算 \(n_i,w_i,f_i\)，再对 608 棵真实来源树模拟调度。[pdf:E17]（PDF 物理页 29，§6.2）它缺少的是实际 solver runtime trace 和硬件实测，尤其没有检验权重估计误差、memory bandwidth 或 communication 对 heuristic 排序的影响。因而，理论结论对抽象模型成立；heuristic 的工程优劣若离开该模型，仍需重新验证。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 multifrontal solver，而是“heuristic 梯度与硬预算保证”：

1. 从公开 sparse-matrix collection 选 3 个结构差异明显的矩阵，或直接准备 3 棵可公开复核的 assembly tree：一棵深链占主导、一棵宽汇合、一棵混合树。若一周内无法稳定重建 Matlab/MeTiS 数据链，就把“复现论文原数据”与“验证算法机制”分开，先用显式记录的合成树验证机制。
2. 实现统一的 event-based simulator：按 \(w_i\) 推进完成事件，严格执行子输出生命周期，逐事件记录 \(C_{\max}\) 与 \(M\)。先实现 sequential postorder、ParSubtrees、ParInnerFirst、ParDeepestFirst、MemBookingInnerFirst；Algorithm 3 与 Algorithm 5 已给出足够直接的伪代码。[pdf:E11]（PDF 物理页 20，Algorithm 3）[pdf:E16]（PDF 物理页 27，Algorithm 5）
3. 对 \(p=2,4,8\) 运行无约束三种 parallel heuristic，复查是否出现“ParSubtrees 更省 memory、ParDeepestFirst 更短 makespan”的方向性结果，而不是强求复现 Table 1 的跨 608 树精确均值。[pdf:E18]（PDF 物理页 30，Table 1）
4. 令 \(M\) 等于所选 postorder 的 sequential peak，再运行 MemBookingInnerFirst。每个事件后断言 `used ≤ M`，并确认根最终完成。若存在任何合法 reduction tree 使其超过 \(M\) 或停滞，便直接反驳对实现而言最关键的 Theorem 6 机制；若始终完成且不超限，则支持实现忠实，但不构成普遍数学证明。
5. 再给 \(w_i\) 加入 ±20% 的可重复扰动，只改变真实完成事件、不改变调度器预估值，观察 heuristic 排序是否稳定。此项是基于论文静态权重假设的扩展压力测试，不是原文实验。

最低验收结果应包含每个事件的 ready queue、running set、resident outputs、booked memory、peak 与 final makespan，使任何超限都能定位到一个具体节点，而不是只比较最终两列数字。

## § 11 — 最强反例设计

最强攻击应针对“这些 heuristic 在实际 parallel sparse/工程系统里仍给出有意义的折中”，而不是去挑战已经证明的抽象定理。

构造一棵宽度很大的 reduction tree，叶任务输出较小但都从同一个带宽受限的外部 memory channel 读取；上层 inner task 的 \(f_i\) 满足论文的 reduction property，却需要同一组不可并发的 compute units 或同一 memory bank。给所有节点的标称 \(w_i\) 使用论文式静态计算量，但在真实执行中让同时启动的叶越多，每个叶的运行时间和 buffer 占用越大。这样，ParDeepestFirst 或 aggressive MemLimit 会因为标称 critical path 而打开大量叶，纸面上 makespan 下降、scalar memory 未超限，真实系统却因 contention 变慢并占用额外 DMA/bank buffer。

判定标准很硬：在相同任务依赖和 scalar \(f_i,n_i\) 下，若加入可测的 bank/bandwidth 约束后，论文预测更快的 heuristic 在真实 makespan 上系统性更慢，或者 booking 报告 `used ≤ M` 时物理 buffer 已溢出，那么“单一共享 memory + 静态任务时间足以指导工程调度”就被否定。这个反例不否定 Theorem 1–6；它证明的是模型到系统的映射不足。

对 FPGA EMT 更直接的版本，是让多个场站子模型在同一时间步同时触发开关事件，导致原本近似固定的任务时长、DSP 占用和中间状态量一起突增。如果依赖实际为跨步 DAG 或有反馈，无法无损表示为本文 in-tree，那么论文 heuristic 甚至没有合法输入。这个场景目前是候选反例，论文没有提供 EMT 数据或板上证据，不能写成已观察事实。

## § 12 — Follow-up Research Idea

### 候选判断：面向单卡多场站 EMT 的多资源、硬 deadline 调度

这篇论文所属的 parallel scheduling/theory 方向看重可证明的复杂度或近似边界，以及能覆盖真实实例的算法评价；而 FPGA EMT 更看重固定实时步长内必达的 deadline、数值正确性、BRAM/DSP/带宽可实现性和板上测量。两类评价标准不能互相替代。

**(a) 未满足需求。** 单张 FPGA 卡同时承载多个场站模型时，真正约束通常不是一个 scalar memory：BRAM 容量与 bank/port、DSP 数、外部 memory bandwidth、pipeline initiation interval 和单步 deadline 都可能同时卡住。本文已经证明，在一个 scalar memory 与 makespan 之间都不存在普适的双常数近似；[pdf:E07]（PDF 物理页 10，Theorem 2）这提示更真实的多资源问题不能靠“先最大化并行度，再看是否装得下”处理。但论文没有验证任何 EMT 或 FPGA 场景。

**(b) 可能的研究价值。** 候选目标不是把 MemBookingInnerFirst 原样搬到 FPGA，而是把问题重新定义为：给定一个可验证的场站 EMT task graph、每类任务的 BRAM/DSP/bandwidth reservation 和 worst-case execution time，在每个仿真步的硬 deadline 内，求可组合、可审计的 admission/schedule certificate。价值在于把“平均更快”改成“资源不超限且 deadline 可证明”，并能明确拒绝无法在单卡上安全组合的场站集合。

**(c) 可借鉴的方法。** 可以借鉴本文的 booking 思想，把未来父任务所需资源在启动子任务时提前计入；再结合 multi-resource RCPSP、synchronous dataflow、network calculus 或 real-time worst-case response analysis。这里列的是候选工具方向，不是本文相关文献的结论，也不表示这些组合尚无人研究。

**(d) 第一个可证伪实验。** 先取 3 个规模与事件密度不同的场站模型，把一个 EMT step 内的计算依赖显式导出。第一道 kill gate 是检查它们能否在不丢失反馈、跨步状态和多父依赖的前提下化为 tree；不能，就应放弃直接套用本文 tree scheduler。若能，再在一张目标 FPGA 上比较：现有静态 schedule、只按 critical path 的 schedule、以及多资源 booking schedule。对正常步和同步开关事件步分别测量 worst-case step latency、BRAM/DSP/带宽峰值与数值误差；只要 booking 方案仍有资源超限、deadline miss，或为了守界造成不可接受的吞吐损失，该想法就被首轮否定。

**(e) 与本文的实质区别。** 本文优化的是 identical processors + shared scalar memory 上 tree-shaped sequential tasks 的 makespan/peak-memory 折中，并用稀疏矩阵树做模拟。[pdf:E17]（PDF 物理页 29，§6.2）候选研究改成异质、并发占用的多种 FPGA 资源，加上硬实时 deadline、事件诱发的 worst-case 变化和数值正确性约束；它首先验证“场站 EMT 是否真能形成本文所需的树”，而不是预设可以迁移。作者本人也把 task 内部并行和 distributed/shared memory 扩展列为未解决方向。[pdf:E22]（PDF 物理页 35，§7）

这是一个证据约束下的候选研究方向，不声称 novelty。完成针对 FPGA real-time scheduling、HLS resource-constrained scheduling、EMT task-graph partitioning 和 multi-station composition 的系统检索之前，不能把它写成“首个”或“尚无人解决”。
