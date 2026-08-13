# Equality Saturation for Tensor Graph Superoptimization

**作者：** Yichen Yang；Phitchaya Mangpo Phothilimthana；Yisu Remy Wang；Max Willsey；Sudip Roy；Jacques Pienaar。[pdf:E01]（PDF 物理页 1，标题与作者）

**出处：** Proceedings of the 4th MLSys Conference，San Jose，CA，USA。[pdf:E01]（PDF 物理页 1，页脚出处）

**年份：** 2021。[pdf:E01]（PDF 物理页 1，页脚年份）

**DOI：** 未报告。

**Zotero key：** 9I789BDQ。

**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的是：给定一个 tensor computation graph（张量计算图）和一组保持语义不变的 graph rewrite（图重写）规则，怎样不依赖脆弱的规则顺序，找到运行代价更低的等价图。生产框架通常用人工 heuristic（启发式）决定何时、按什么顺序应用规则；已有 superoptimization（超级优化）研究虽然把它改成搜索 rewrite sequence（重写序列），但仍然一次只做一个替换，因此会遇到 phase-ordering（阶段排序）问题：早先看似合理的改写可能隐藏后续更大的优化机会，搜索也只覆盖指数级等价空间的一小部分。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

论文的核心主张是把 equality saturation（等式饱和）用于 tensor graph superoptimization：探索阶段把可达的等价写法并存于 e-graph（等价图）中，提取阶段再按代价模型一次性选择最优图；为适配 tensor graph，作者又补上 multi-pattern rewrite（多模式重写）和可扩展的 cycle filtering（环过滤）。论文直接报告，TENSAT 相比当时 state-of-the-art（SOTA，最佳已有方法）可得到最高 16% 的额外运行时提升，同时平均少花 48 倍优化时间。[pdf:E01]（PDF 物理页 1，Abstract）

重要性有两层。第一层是推理运行时间：同一组语义等价的算子组合，kernel 数量、共享子图和融合形态不同，会直接改变端到端 latency。第二层是编译成本：若 superoptimizer 需要几分钟到几十分钟，它只能做离线 autotuning；若能压到秒级，就可能进入普通 compilation flow（编译流程）。Table 1 的量级说明这不是小差异：NasNet-A 的搜索时间从 TASO 的 1226 秒降到 TENSAT 的 10.6 秒，优化后相对原图的 speedup 从 1.9% 提到 7.3%；NasRNN 则从 177.3 秒降到 0.5 秒，speedup 从 45.4% 提到 68.9%。[pdf:E02]（PDF 物理页 1，Table 1）

基于这些证据，论文的价值不只是“找到另一张更快的图”，而是改变搜索组织方式：把过去在时间维度上做出的不可逆选择，改成在共享表示中保留多个选择，再由全局提取器决策。这使更大搜索覆盖与较短优化时间首次在同一套 tensor graph optimizer 中同时出现；但“全局最优”严格地说是相对于已生成的 e-graph 和指定代价模型，而不是对所有可能程序及真实硬件运行时间的无条件保证。

## § 2 — 前人工作与不足

论文把最接近的工作分成几类。TASO 使用 backtracking search（回溯搜索），并以硬阈值限制暂时增加运行时间的 substitution（替换）；Fang 等人的方法用 sampling（采样）剪掉冗余替换，搜索更快，但论文称它并没有因此找到比 TASO 更优的程序；NeuRewriter 用 reinforcement learning（强化学习）逐步选择规则和图区域，本质上仍是顺序应用替换。[pdf:E03]（PDF 物理页 10，Section 7“Graph Rewrite Optimizations”）

这些方法的问题不是“完全不会搜索”，而是搜索动作具有破坏性和历史依赖。传统 term rewriting（项重写）一旦把旧项替换掉，就忘记了原表达；一个局部优化若在错误时机发生，会让后面的规则不再匹配。e-graph 的关键差别是把新表达加入原 e-class，而不是覆盖旧表达，因此保留所有已证明等价的选择。[pdf:E04]（PDF 物理页 3，Figure 1 及 caption）[pdf:E05]（PDF 物理页 3，Section 2.3）

已有 equality saturation 工具也不能直接解决 tensor graph 问题。第一，深度学习图里重要的优化经常同时匹配多个输出，例如把两个共享输入的 matmul 合并成一次较大的 matmul，再 split 成两个输出；论文指出主流 equality saturation toolkit 通常只为 single-pattern rule（单模式规则）提供高效匹配，因此需要新的 multi-pattern matching 算法。[pdf:E06]（PDF 物理页 4，Figure 2 与 Section 4 开头）第二，e-graph 可以合法地包含环，但最终 tensor graph 必须是可执行 DAG；把拓扑序约束直接塞进 ILP 会让求解器很快成为瓶颈，因此需要在探索阶段过滤环。[pdf:E07]（PDF 物理页 6，Figure 3 与 Section 5.2）

更远的相关工作也只覆盖了问题的一部分。Denali 同样使用 e-graph 和 constraint solver（约束求解器），但目标是低层指令 superoptimization；Wang 等人的 equality saturation 工作处理的是由少量 matrix multiplication、summation 等算子组成的 linear algebra kernel，而 TENSAT 的对象是完整 computation graph。论文据此把自身差异概括为 computation-graph-level 搜索、multi-pattern 扩展和高效 cycle filtering。[pdf:E08]（PDF 物理页 10，“Superoptimization”“Equality Saturation Applications”与 Conclusion）

这里只能根据源 PDF 复原作者的比较范围。由于本任务不引入包外文献，本文是否在更广泛文献中具有绝对 novelty（新颖性）不作外推；能确认的是，论文针对其列出的 tensor graph 搜索基线，明确解决了顺序替换、multi-output matching 和 cyclic e-graph extraction 三个缺口。

## § 3 — 重建作者的思考路径

下面是基于论文背景、失败模式和已有工具能力的思考路径重建，不是作者逐字陈述的研究日志。

1. 先接受已有结论：graph rewrite 能优化 tensor program，但规则本身并不足够，规则顺序会决定哪些机会还能被看见。传统重写对表达做 destructive replacement（破坏性替换），因此 phase-ordering 不是调参问题，而是表示方式的问题。[pdf:E04]（PDF 物理页 3，Figure 1）
2. 既然错误来自“过早丢弃替代项”，自然的下一步不是更聪明地猜下一个规则，而是暂时不做单选。e-graph 可以在一个 e-class 中并存多个等价 e-node，equality saturation 将优化拆成 exploration（探索）和 extraction（提取），把规则选择推迟到所有候选共同出现之后。[pdf:E05]（PDF 物理页 3，Section 2.3）
3. 直接套用通用 e-graph 还不够，因为 tensor graph 的高收益规则往往是 non-local、multi-output 的。共享输入的 matmul/conv 合并规则需要同时找到多个模式，并要求共享变量落到同一个 e-class；这迫使搜索算法从单模式匹配升级为 canonicalization（规范化）、匹配结果笛卡尔积和共享变量兼容性检查。[pdf:E06]（PDF 物理页 4，Figure 2）[pdf:E09]（PDF 物理页 5，Algorithm 1 与解释段落）
4. 搜索空间变大后，局部 greedy extraction（贪心提取）不能正确计入 shared subgraph（共享子图），而 ILP 虽可做全局选择，却会被环约束拖垮。于是需要把“语义等价搜索”和“DAG 合法性维护”重新分工：探索时用轻量预过滤和迭代后 DFS 清环，提取时只解无环候选上的核心选择问题。[pdf:E10]（PDF 物理页 6，Eq. (1)–(5) 与说明）[pdf:E11]（PDF 物理页 7，Algorithm 2 与后处理说明）
5. 最后再问工程可用性：如果更完整的搜索仍比 TASO 慢，就不能进入常规编译。因此实验必须同时检验最终图 runtime、optimizer time、multi-pattern 迭代增长和各组件消融，而不能只展示一个最好图。

这条路径的关键转折是：作者没有继续优化“下一步选哪条规则”的 policy，而是改变了搜索状态的表示，把顺序决策问题变成共享等价空间上的全局选择问题。

## § 4 — 核心 Intuition

不要在每次 rewrite 发生时押注一个唯一方向，而要把所有已证明等价的图形态同时留在 e-graph 中。[pdf:E05]（PDF 物理页 3，Section 2.3）探索阶段尽可能扩展等价空间，提取阶段再依据全局代价选择一个可执行 DAG，从而把 phase-ordering 从“搜索时不可逆的选择”改成“提取时可比较的选择”。tensor graph 的特殊难点是多输出共享与潜在环，因此 TENSAT 用 multi-pattern matching 保留非局部优化机会，并在 ILP 前把无效 cyclic subgraph（有环子图）排除。[pdf:E12]（PDF 物理页 2，Introduction 对两项扩展的概述）直观上，它不是更会走迷宫，而是先把多个可达路线压缩画在同一张地图上，再统一选总代价最低的一条。

## § 5 — 具体方法与完整 Pipeline

可以用论文的共享 matmul 规则作为贯穿例子。原图有两个输出 `matmul(x, w1)` 和 `matmul(x, w2)`；目标图先把 `w1`、`w2` concat，再只做一次较大的 `matmul(x, concat(w1,w2))`，最后 split 出两个原输出。Figure 2 给出规则的 S-expression（符号表达式）形式，Appendix 的 Figure 8 说明这一模式确实出现在 BERT 优化结果中，并可推广到两个以上共享输入的 matmul。[pdf:E06]（PDF 物理页 4，Figure 2）[pdf:E13]（PDF 物理页 13，Figures 8–9）

完整 pipeline 如下。

1. **输入与图表示。** 输入是原 tensor computation graph 和语义保持的 rewrite rule 集合。每个 operator 对应一个输出 tensor node，输入 tensor 是其 child；完整图是 DAG。为让 equality saturation 的公式只处理一个 root，多个最终输出会用没有实际算子的 `noop` 合成单根。TENSAT 的语言覆盖 element-wise、matmul、grouped convolution、activation、pooling、transpose、concat、split、reshape 等算子及 tensor/string/integer/tensor-tuple 类型。[pdf:E14]（PDF 物理页 4，Table 2）
2. **初始化与形状约束。** 原图被加入 e-graph。每轮对所有规则做匹配，并把 target pattern 及等价关系加入 e-graph；若达到 saturation，或触发时间、e-graph 大小、迭代次数限制，就结束探索。每个匹配在应用前还要做 shape checking，验证 target tensor shape 是否满足规则前置条件。[pdf:E06]（PDF 物理页 4，Section 4）
3. **multi-pattern 匹配。** 对规则 source 中的每个 S-expression 先做变量重命名规范化，只搜索唯一 canonical pattern；然后恢复原变量名，对各模式匹配结果取 Cartesian product（笛卡尔积），检查共享变量是否映射到同一 e-class，兼容时才应用规则。[pdf:E09]（PDF 物理页 5，Algorithm 1）这一步让“两个共享 `x` 的 matmul”能作为一个整体被发现，而不是分别重写后再碰运气。
4. **限制组合爆炸。** multi-pattern rule 的增长极快：若某共享输入下有 `N` 个 matmul，第一轮可新增 `O(N^2)` 个节点，第二轮可达到 `O(N^4)`；因此作者单独设置 `k_multi`，超过该轮数后只继续 single-pattern rewrite。[pdf:E15]（PDF 物理页 5，Section 4 末段）
5. **cycle filtering。** 每轮开始先计算 descendants map；对每个匹配做常数时间的预检查，明显会成环的匹配直接跳过。由于该预检查 sound but incomplete（可靠但不完备），每轮结束再用 DFS 找剩余环，对每个环把最后加入的节点放入 filter list，并在提取时强制这些节点不被选择。[pdf:E11]（PDF 物理页 7，Algorithm 2 与后处理段落）
6. **全局提取。** 每个 e-node 的成本是该具体 operator 在目标硬件、具体 shape 和参数下测得的运行时间，图成本取被选节点成本之和；在该模型下，ILP 从 root e-class 出发选择一组闭合的节点，得到最低成本的 DAG。[pdf:E16]（PDF 物理页 5，Section 5“Cost model”与 5.1）
7. **输出与执行。** 输出是与原图语义等价、满足 shape 和无环约束的优化图，再用后端执行。论文实现使用 Rust、egg e-graph library、SCIP ILP solver 和 Google OR-Tools；实际评测平台是 NVIDIA Tesla T4 GPU、16-core CPU 和 60 GB memory。[pdf:E17]（PDF 物理页 7，Section 6 与 6.1）

这不是连续时间、电磁暂态或 multi-rate simulation（多速率仿真）方法，因此开关事件、时间推进和数值积分不适用；论文也没有报告 FPGA mapping（FPGA 映射）、片上存储、pipeline initiation interval 或定点数值表示。硬件相关部分只落实到 GPU operator runtime cost 与 T4/cuDNN 执行平台，不能把文中的结果直接解释为 FPGA 性能结论。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出新的收敛定理，核心形式化内容是把 e-graph extraction 写成 ILP。设 e-node 编号为 `i=0,…,N-1`，e-class 编号为 `m=0,…,M-1`；`e_m` 是 e-class `m` 内的节点集合，`h_i` 是节点 `i` 的 child e-class 集合，`g(i)` 是节点 `i` 所属 e-class，`e_0` 是 root e-class，`c_i` 是节点的实测 operator cost。为每个 e-node 引入二元变量 `x_i`，选中时为 1：

\[
\min_x f(x)=\sum_i c_i x_i
\]

\[
x_i\in\{0,1\},\qquad
\sum_{i\in e_0}x_i=1,
\]

\[
\forall i,\forall m\in h_i:\quad
x_i\le \sum_{j\in e_m}x_j.
\]

这些分别对应论文 Eq. (1)–(3)：二元选择、root 必须选一个表示、若选中父节点则每个 child e-class 至少要选一个节点。[pdf:E10]（PDF 物理页 6，Eq. (1)–(3)）因为目标函数会惩罚额外节点，最优解不会无故在同一 e-class 选多个节点；这使约束不必显式写成“每个 e-class 恰好一个”。

若允许 e-graph 自身含环，还需引入每个 e-class 的拓扑序变量 `t_m`：

\[
\forall i,\forall m\in h_i:\quad
t_{g(i)}-t_m-\epsilon+A(1-x_i)\ge 0,
\]

\[
\forall m:\quad 0\le t_m\le 1,
\]

其中 `\epsilon<1/M`，`A>1+\epsilon`。当 `x_i=1` 时，大常数项消失，约束强制 parent 的拓扑序严格晚于 child；当 `x_i=0` 时，`A` 让该约束自动松弛。这就是 Eq. (4)–(5) 的工程含义。[pdf:E10]（PDF 物理页 6，Eq. (4)–(5) 与解释）

但 TENSAT 的最终方案并不让 ILP 承担 Eq. (4)–(5)。作者观察到 cycle constraint 是求解瓶颈，遂在 exploration 阶段清环，提取时保留 Eq. (1)–(3)，并对 filter list 中的节点增加 `x_i=0`。Figure 3 说明一个语义合法的 multi-pattern rewrite 仍可能在 e-graph 中形成环；这解释了为什么“rewrite soundness”与“extracted graph acyclicity”是两个不同条件。[pdf:E07]（PDF 物理页 6，Figure 3 与 Section 5.2）

复杂度上，vanilla cycle filtering 每次匹配都遍历 e-graph，一轮为 `O(n_m N)`；高效方案把 descendants 计算摊到每轮一次，预过滤每个匹配为常数时间，后处理保守上界为 `O(n_c N)`，其中实际通常有 `n_c \ll n_m`。[pdf:E11]（PDF 物理页 7，Algorithm 2 后的复杂度说明）multi-pattern 搜索自身仍可双指数增长，因此 `k_multi` 是必要的规模旋钮而不是纯超参数。[pdf:E15]（PDF 物理页 5，增长分析）

最需要限定的一点是：ILP 保证的是“在当前 e-graph、当前 additive cost model（加性代价模型）下的最低成本无环图”。它不保证搜索已经覆盖全部等价程序，也不保证 `\sum_i c_i` 的排序与真实 end-to-end runtime 完全一致；后者在 SqueezeNet 实验中已经出现反例迹象。[pdf:E18]（PDF 物理页 9，Figure 7 与其后 cost-model discrepancy 段落）

## § 7 — 实验设计与结论

**问题一：equality saturation 是否能找到比顺序 backtracking 更快的图？** → 作者固定使用与 TASO 相同的 rewrite rules，在 BERT、ResNeXt-50、NasNet-A、NasRNN、Inception-v3、VGG-19、SqueezeNet 七个 inference graph 上比较，并用 TASO 的 cuDNN backend 测完整图 runtime；每个 optimizer × benchmark 设置运行五次，Figure 4 报告均值与标准误。[pdf:E17]（PDF 物理页 7，Section 6.1）[pdf:E19]（PDF 物理页 8，Figure 4 caption）→ 答案是多数 benchmark 上 TENSAT 找到更优图，最大收益集中在 NasRNN 和 SqueezeNet；Table 1 给出的 headline result 是最高 16% 超过 SOTA，NasRNN 相对原图 speedup 达 68.9%，SqueezeNet 达 24.5%。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 1，Table 1）

**问题二：更大搜索空间是否以不可接受的 optimizer time 为代价？** → 作者同时记录 TASO 完整搜索时间 `T_total`、TASO 首次找到最终最好图的 oracle time `T_best`，以及 TENSAT exploration+extraction 时间；Figure 5 比较各模型，Figure 6 单独画 Inception-v3 的 speedup–time tradeoff。[pdf:E19]（PDF 物理页 8，Figures 5–6）→ TENSAT 相对 `T_total` 快 9.5–379 倍，相对不可实际知道的 `T_best` 仍快 1.8–260 倍；Abstract 汇总为平均少花 48 倍优化时间。[pdf:E19]（PDF 物理页 8，Figure 5 及正文）[pdf:E01]（PDF 物理页 1，Abstract）Table 3 还显示阶段耗时通常为秒级，例如 NasNet-A exploration 8.81 秒、extraction 1.79 秒，Inception-v3 分别为 4.38 秒和 0.75 秒。[pdf:E20]（PDF 物理页 8，Table 3）

**问题三：增加 multi-pattern 迭代是否持续有益？** → 作者改变 `k_multi`，同时测 speedup、optimizer time 和最终 e-node 数，并给 ILP 设置一小时 timeout。[pdf:E18]（PDF 物理页 9，Figure 7）→ 对 NasRNN、Inception-v3、BERT、NasNet-A、ResNeXt-50，更大的 `k_multi` 往往找到更快图，但 e-graph 节点数和求解时间急剧增加；BERT、NasNet-A、NasRNN、Inception-v3 在 `k_multi=3` 时 ILP 超时。SqueezeNet 的实际 speedup 反而随 `k_multi` 降低，作者明确归因于 operator-sum cost 与真实 graph runtime 的偏差。[pdf:E18]（PDF 物理页 9，Figure 7 caption 与后续两段）

**问题四：ILP 与 cycle filtering 是否真的是必要设计，而非实现偏好？** → Table 4 比较 greedy 与 ILP：BERT 的 runtime 从原始 1.88 ms 经 greedy 仍为 1.88 ms，而 ILP 为 1.73 ms；NasNet-A 的 greedy 甚至退化到 22.5 ms，ILP 则从原始 17.8 ms 降到 16.6 ms。作者解释，greedy 看不到两个输出共同选择 split 后才能共享 RHS subgraph 的依赖。[pdf:E21]（PDF 物理页 9，Table 4 与 Section 6.5）→ Table 5 显示保留 cycle constraint 时，`k_multi=2` 的 BERT、NasRNN、NasNet-A 都超过 3600 秒且尚未找到 feasible solution；去掉后分别为 510.3、356.7、75.1 秒。[pdf:E22]（PDF 物理页 10，Table 5）→ Table 6 显示 efficient cycle filtering 在 NasRNN、`k_multi=2` 时把 exploration 从 2932 秒降到 1.47 秒，NasNet-A 从超过 3600 秒降到 8.62 秒，正文概括最高约 2000 倍加速。[pdf:E23]（PDF 物理页 10，Table 6 与相邻结论）

这些实验支持“更广搜索覆盖、全局共享感知提取和提前清环共同构成收益”这一 claim，但外推边界很清楚：实验只在单个 Tesla T4、同一套 TASO rules、七个成功 benchmark 上完成；作者另测 ResNet-50，发现这些规则在 T4 上无法给原图带来任何 speedup。[pdf:E17]（PDF 物理页 7，Section 6.1）论文没有验证其他 GPU 架构、并发 kernel 调度、训练图、动态图、FPGA 或大于当前 `k_multi`/`N_max` 限制的规模，因此不能把“平均 48 倍”当作跨平台常数。

## § 8 — Take-aways

**5 句话：** ① tensor graph optimization 的瓶颈不仅是缺少 rewrite rule，更是顺序替换造成的 phase-ordering。② equality saturation 用 e-graph 保留多个等价选择，把“何时应用哪条规则”推迟到全局 extraction。[pdf:E05]（PDF 物理页 3，Section 2.3）③ 要让这一思想适用于深度学习图，必须处理 multi-output rule、共享子图代价和 cyclic e-graph，而 TENSAT 分别用 multi-pattern matching、ILP 和 efficient cycle filtering 解决。[pdf:E09]（PDF 物理页 5，Algorithm 1）[pdf:E11]（PDF 物理页 7，Algorithm 2）④ 在七个 T4 inference benchmark 上，论文报告最高 16% 超过 SOTA 且平均少花 48 倍优化时间。[pdf:E01]（PDF 物理页 1，Abstract）⑤ 这些收益受 additive operator cost 和 e-graph 规模约束，所以“全局最优”必须理解为模型内最优而非真实硬件上的绝对最优。

**3 句话：** ① TENSAT 的主要创新不是一条新算子规则，而是把 tensor graph rewrite search 从顺序决策改造成等价空间构造。② multi-pattern rule 让共享 matmul/conv 的非局部优化进入 e-graph，cycle filtering 又使 ILP 能在更大图上完成全局提取。[pdf:E13]（PDF 物理页 13，Figures 8–9）[pdf:E22]（PDF 物理页 10，Table 5）③ 实验说明这种重构同时改善结果和编译时间，但 SqueezeNet 与 `k_multi` 爆炸也暴露出 cost model 和 scalability 是下一步真正的瓶颈。[pdf:E18]（PDF 物理页 9，Figure 7 与正文）

**1 句话：** TENSAT 证明了“先共享地保存等价图、再全局选图”比“沿一条 rewrite sequence 猜到底”更适合 tensor graph superoptimization，但其成功仍取决于搜索空间能否承受以及代价模型能否正确排序真实执行计划。

## § 9 — 最脆弱的假设

最脆弱的假设是：**图的真实执行时间可以被各 operator 在固定 shape/参数下的独立实测时间之和充分排序。** 论文直接说明其 cost model 与 TASO 相同，每个 operator 有独立成本，图成本为所选节点成本之和；它之所以被认为适合 GPU，是因为论文假设 graph execution 通常一次运行一个 operator。脚注同时承认，更复杂硬件可能并行执行多个 kernel，准确 cost 会含有 non-local dependency（非局部依赖），届时可能需要不同 extraction 方法。[pdf:E16]（PDF 物理页 5，Cost model 与脚注 2）

如果这个假设失效，TENSAT 的核心机制不会在语义上出错，但会在优化目标上“精确地解错问题”：ILP 可以找到 `\sum_i c_i` 的全局最优图，却选中真实 runtime 更差的图。论文已经给出内部证据——SqueezeNet 随 `k_multi` 增大时，cost model 认为某些新 rewrite 降低成本，完整图实测却变慢。[pdf:E18]（PDF 物理页 9，Figure 7 后第一段）这不是边缘误差，因为搜索越充分，优化器越可能把模型偏差放大。

论文为该假设提供的证据是：在 T4 上，多数 benchmark 的预测方向与端到端结果一致，且最终图确实更快；但缺少三类关键验证。第一，没有报告 e-graph 候选图的 predicted-cost 与 measured-runtime 排名相关性或 selected-plan regret；第二，没有跨 GPU、并发 stream、fusion policy、memory pressure 的验证；第三，没有把“搜索空间不够”与“cost model 排错”通过候选穷举分离。基于证据的判断是：这项假设一旦不成立，论文最强的“global optimum”措辞会退化为“对一个代理目标的 global optimum”，实际性能贡献可能随硬件和 workload 反转。

## § 10 — 最小复现实验

一周内最值得复现的不是七个完整网络，而是“multi-pattern + ILP 能发现 greedy 看不到的共享子图收益”这一最小 claim。实验对象采用论文 Figure 2/8/9 的两类 motif：若干个共享输入 `x` 的 matmul，和若干个共享输入 `x` 的 conv；候选 rewrite 分别是 concat weights → 单个大算子 → split outputs。[pdf:E06]（PDF 物理页 4，Figure 2）[pdf:E13]（PDF 物理页 13，Figures 8–9）

可执行方案如下：

1. 实现一个只含 `input/weight/matmul/conv/concat/split/noop` 的小图语言，以及上述两条 multi-pattern rule；不复现完整 TENSAT operator set。
2. 构造约 30 组 shape，覆盖两个、三个、四个共享分支，并让权重 concat 可在 inference 前预计算；每组生成原图和所有规则可达候选。
3. 用同一硬件分别测 operator microbenchmark cost 和完整候选图 runtime；实现三种选择器：一步顺序重写、按 subtree cost 的 greedy、Eq. (1)–(3) 的 ILP。Table 4 的现象是这一设计的直接靶点。[pdf:E21]（PDF 物理页 9，Table 4）
4. 记录搜索时间、e-node 数、预测成本、真实 runtime、是否选中共享 RHS，以及选中图相对枚举最优图的 regret。
5. **支持 claim 的结果：** ILP 在存在共享收益的 shape 上稳定选择 concat–single-op–split，并且真实 runtime 不高于 greedy/顺序基线；**反驳 claim 的结果：** greedy 同样总能选到最好图，或 ILP 虽降低预测成本却经常提高真实 runtime，或极小 motif 已出现不可接受的搜索爆炸。

这项复现把 representation、matching、sharing-aware extraction 和 cost-model fidelity 四件事分开测量，不需要复现所有网络或完整 rewrite inventory。若时间只够做一类算子，优先 matmul：Figure 8 与 Table 4 同时给出了真实使用模式和 greedy 失败证据。

## § 11 — 最强反例设计

最强反例应直接攻击 additive cost model，而不是只找一个 TENSAT 没覆盖的 rule。论文自己指出，复杂硬件可并行执行多个 kernel，代价会出现非局部依赖；Appendix 又展示了把多个独立 matmul/conv 合并成共享大算子的模式，以及权重 concat 可预计算的四 conv→两 conv 变换。[pdf:E16]（PDF 物理页 5，脚注 2）[pdf:E24]（PDF 物理页 14，Figure 10）[pdf:E25]（PDF 物理页 14，Figure 11）

反例族可以这样构造：对每个共享分支图，同时生成“多个小算子可并发执行”和“一个大算子+split 串行执行”两类等价候选；系统性改变 branch shape、算子饱和度、stream concurrency、memory bandwidth pressure 和可融合后继。对每个 e-graph 不让 TENSAT 只给出一个答案，而是穷举所有可执行候选，分别计算 `\sum_i c_i` 与真实 end-to-end runtime，测 rank correlation 和 selected-plan regret。这样可排除“没搜到最好候选”的替代解释：如果真实最快图已经在 e-graph 内，但 ILP 持续选择预测成本更低、实际更慢的图，失败就能归因于 extraction objective，而非 rewrite coverage。

最有杀伤力的结果是：在一类可预测的并发或 memory-bound 条件下，TENSAT 的 selected graph 随搜索加深而系统性变慢，并重现 SqueezeNet 的方向反转；同时 exhaustive best-in-e-graph 明显更快。这会推翻“更充分 equality saturation 通常会带来更优实际图”的实践性结论，并把论文的保证缩小为语义等价与代理代价最优。相反，若在控制并发和内存压力后 additive ranking 仍高度稳定，这个反例就失败，也会显著增强论文最脆弱假设的可信度。

## § 12 — Follow-up Research Bet

**候选研究押注（仅基于本 PDF，不声称 novelty）：把优化对象从纯 tensor DAG 提升为带调度、layout、buffer 与 device mapping 语义的 tensor execution hypergraph（张量执行超图）。** 新的研究问题不是“在等价计算图中选哪一张”，而是“能否在同一 equality-saturation 空间里联合发现等价计算、数据布局、并发调度、临时存储和硬件映射，使优化器直接选择真实执行计划，而不是先选图再交给后端”。它首次可能让只有在特定 schedule 或 memory placement 下才有收益的 rewrite 被正确评价，例如共享 matmul 的 concat–single-op–split、Figure 10 中可预计算 weight concat 的四 conv→两 conv，以及多个小 kernel 并发与单个大 kernel 之间的硬件相关取舍。[pdf:E13]（PDF 物理页 13，Figures 8–9）[pdf:E24]（PDF 物理页 14，Figure 10）

核心机制是把 e-class 继续定义为“产生同一语义 tensor/tuple 的等价实现”，但让 e-node 不再只表示 operator，而表示带 `layout/tiling/buffer/schedule/device` 属性的 execution hyperedge；multi-pattern rewrite 同时改写计算结构和共享生产者，extraction 的目标从独立 operator cost 之和改为 critical path、memory traffic、buffer capacity、kernel overlap 与通信代价共同决定的执行成本。因果链是：更丰富的状态表示保留 graph-level 与 hardware-level 等价选择 → multi-output e-class 显式表达共享和通信 → schedule-aware extraction 看见并发、复用与预计算的非局部作用 → 最终避免“代理图成本更低、真实执行反而更慢”的排序错误。它至少改变了状态表示、可控变量、硬件映射、系统边界和评价对象，而不是在 TENSAT 外面加一个修补模块。

这一押注有明确的论文特异依据。方法侧，作者的现有 cost model 假设独立 operator 串行相加，脚注明确指出并行硬件需要 non-local cost 与不同 extraction；Table 4 又证明共享 RHS 需要全局选择才能被正确计价。[pdf:E16]（PDF 物理页 5，Cost model 与脚注）[pdf:E21]（PDF 物理页 9，Table 4）实验侧，SqueezeNet 已出现 cost ranking 与真实 runtime 不一致，`k_multi` 增大又造成 e-graph 爆炸和 ILP timeout，说明只扩大图级搜索既可能放大模型偏差，也会撞上规模墙。[pdf:E18]（PDF 物理页 9，Figure 7 与正文）最大收益是把 equality saturation 从“graph optimizer”变成跨 compiler–accelerator boundary（编译器—加速器边界）的 execution-plan synthesizer，可自然覆盖 GPU stream/fusion，也可在未来映射到 FPGA 的 pipeline、on-chip buffer 和并行实例选择；最大科学风险是状态空间比当前 multi-pattern e-graph 更快爆炸，且 schedule/layout 等价性的 canonical representation 可能难以定义，导致 extraction 再次不可解。

首个可证伪实验应只用 Figures 8–11 的四类 motif，建立一个小 execution e-graph，加入两种 layout、两种并发 schedule 和有限 buffer placement；在同一硬件上比较三组系统：原始 graph-only TENSAT、只把 scalar cost 换成更强 learned predictor 的 graph-only 版本、真正把 schedule/layout 作为 e-node 状态的 execution-hypergraph 版本。三者共享同一底层 runtime predictor，并对小空间穷举真实最优计划。若第三组在 held-out shape 上显著降低 selected-plan regret，而第二组不能，则支持“表示与联合搜索”而非“只需更准 cost model”这一核心机制；若第二组已完全消除差距，主 idea 的必要性就被否证。

按论文自身列出的最近工作，TASO、Fang 和 NeuRewriter 仍在 computation graph 上顺序选择 substitution，SPORES 聚焦较小 linear algebra kernel，Denali 聚焦低层指令；源 PDF 没有展示把完整 tensor graph equality saturation 与硬件 schedule/storage 共同建模的系统。[pdf:E08]（PDF 物理页 10，Related Work）因此它与这些工作的实质差别应落在 problem、representation 和 experimental object 三处，但在未检索包外全文前只能视为候选方向，不能宣称已建立文献 novelty。

**Wild-card alternative：** 把 multi-pattern equality saturation 的系统边界扩展到同时服务的多个模型或请求，在一个跨图 e-graph 中发现跨模型共享的 matmul/conv producer 与联合 batching，使优化目标从“单模型最短 latency”变为“多模型 workload 的吞吐—内存 Pareto 前沿”。
