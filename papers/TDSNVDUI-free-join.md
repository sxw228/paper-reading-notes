# Free Join: Unifying Worst-Case Optimal and Traditional Joins

- 作者：Yisu Remy Wang、Max Willsey、Dan Suciu
- 出处：arXiv:2301.10841v2（源 PDF）；正式 DOI 见下
- 年份：2023
- DOI：10.1145/3589295
- Zotero key：TDSNVDUI
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“再造一个更快的 join”，而是一个长期被二分法卡住的系统问题：传统 binary join 擅长常见的 acyclic query，能够直接复用成熟的 cost-based optimizer、column-oriented layout 和 vectorized execution；worst-case optimal join（WCOJ）在某些 cyclic query 或强 skew 场景中能避免巨大的中间结果，却往往需要另一套 trie、计划表示和优化基础设施。工程上若让两套执行器并存，数据库必须复制或改造 optimizer 与执行路径，WCOJ 因此很难被平滑采用。论文把这个设计空间画成“每一步可同时处理多少个 relation、多少个 attribute”的二维空间，而 binary join 与 Generic Join 只是两个端点。[pdf:E01]（PDF 物理页 1，Abstract、Introduction 与 Fig. 1）

Free Join 的目标是把二选一改成一个统一框架：同一个 plan、同一套 Generalized Hash Trie（GHT）接口和同一个执行算法，可以精确表达 binary join、Generic Join 以及两者之间的混合形态；再用 COLT 和 vectorization 把 WCOJ 过去缺少的工程优化带进来。作者在 Rust 原型上报告：acyclic query 中，相对 binary join 与 Generic Join 的最大加速分别为 19.36× 和 31.6×；cyclic query 中分别为 15.45× 和 4.08×。[pdf:E02]（PDF 物理页 2，Introduction 左栏）

它的重要性因此有两层。算法层面，它把“join 几个 relation、join 几个 attribute”从算法类别提升为 plan 内每个节点都可独立选择的自由度。系统层面，它让已有 binary optimizer 的结果成为起点，而不是要求数据库为 WCOJ 重建完整优化栈。本文不涉及 EMT、实时仿真或 FPGA 映射；其价值在数据库 query processing 与执行系统设计。

## § 2 — 前人工作与不足

传统 binary hash join 一次处理两个 relation，并在两者之间所有共享 attribute 上连接。它的数据结构简单、hash table 构建便宜，几十年的 optimizer、column store 和 vectorized execution 也带来了显著常数优势。弱点是 plan 对 join order 很敏感：错误顺序可能先产生巨大的中间关系，再被后续 join 丢弃。

Generic Join 是论文采用的 WCOJ 代表。它一次选择一个 variable，遍历所有含该 variable 的 relation 的投影交集，然后递归处理 residual query；plan 是 variable 的全序。Fig. 2 的 triangle query 清楚显示了两种执行语义：binary join 遍历 tuple、逐 relation probe；Generic Join 遍历 value、同时在多个 trie 中求交。[pdf:E03]（PDF 物理页 2，optimizer 敏感性与贡献列表）[pdf:E04]（PDF 物理页 3，Sec. 2.2–2.3 与 Fig. 2）

Generic Join 的理论优势是：对任意 variable order 都满足 worst-case optimal 的 AGM-bound 复杂度。例如当 triangle query 的三个 relation 均为大小 \(n\) 时，Generic Join 的 join 阶段为

\[
O\!\left(\sqrt{|R||S||T|}\right)=O(n^{3/2}),
\]

而 binary plan 可达到 \(\Omega(n^2)\)。但这个界不包含构建 trie 的 preprocessing；若某个 relation 很大，即使 join 阶段的 bound 远小于它，Generic Join 仍要先扫描并建完整 trie。于是此前系统常采取“cyclic 部分用 WCOJ、其余用 binary join”的 hybrid approach，代价是两套算法和基础设施。论文认为真正不足不是端点算法不存在，而是缺少能够在两者之间连续取点的统一 plan 与数据结构。[pdf:E05]（PDF 物理页 4，Sec. 2.4、Fig. 3 及复杂度讨论）

## § 3 — 重建作者的思考路径

可以从三个在本文之前已存在的观察倒推这项工作。

第一，push-based left-deep binary plan 与 Generic Join 最终都表现为 nested loops。差别主要不是“有没有循环”，而是每层迭代什么、probe 什么：前者通常迭代一个 relation 的 tuple 并 probe 另一个 hash table，后者迭代一个 trie 的 key 并同时 probe 多个 trie。

第二，hash table 与 hash trie 也不是互斥对象。二层结构“key → tuple vector”已经很接近 trie；如果允许每层 key 是一个 tuple、leaf 是 tuple vector，就能得到同时覆盖两者的 GHT。

第三，binary plan 已由成熟 optimizer 选好 relation order。与其抛弃这个结果重新搜索 Generic Join 的 variable order，不如把 binary plan 翻译成更细粒度的 subatom plan，再只做语义安全的局部 factorization：把已经具备 key 的 lookup 提前到更外层，尽早剪掉注定失败的组合。clover query 给出了最小反例：naive binary-style 执行会产生 \(n^2\) 个 \((x_2,a_i,b_j)\) 组合，随后才发现 relation \(T\) 没有 \(x_2\)；若把对 \(T(x)\) 的 probe 提到对 \(b\) 的循环之外，执行降为 \(O(n)\)。[pdf:E05]（PDF 物理页 4，clover instance 与 binary/GJ 对比）

沿这条路径，作者无需先假设 Free Join 已成立：共同的 iteration/probe 原语导向统一数据结构；成熟 binary plan 导向可复用的初始顺序；skew 造成的中间结果爆炸导向 lookup factorization；完整 trie 的前置成本导向 lazy materialization；nested recursion 的 locality 问题导向 batch probes。

## § 4 — 核心 Intuition

Free Join 的核心直觉是：binary join 与 Generic Join 不是两种不可调和的算法，而是同一 iteration/probe 机器在不同粒度下的两个端点。把每个 relation 拆成 subatom，并允许一个 plan node 同时处理任意数量的 relation 与 attribute，就能在保留 binary optimizer 顺序的同时，把选择性强的 probe 提前，避免中间结果爆炸。一个合法 Free Join plan 必须保证每个 node 有一个 cover，能够一次绑定该 node 尚未可用的全部 variable；其余 subatom 才能用已绑定值 probe。[pdf:E06]（PDF 物理页 5，Definitions 3.4–3.7 与 Eqs. (2)–(3)）

## § 5 — 具体方法与完整 Pipeline

以 clover query \(Q_{\clubsuit}(x,a,b,c) :- R(x,a),S(x,b),T(x,c)\) 为例，完整 pipeline 如下。其统一执行骨架是：迭代当前 node 的 cover，依次 probe 其余 trie，成功后携带 subtrie 递归进入下一 node。[pdf:E07]（PDF 物理页 6，Fig. 7 与 Sec. 3.3）

1. **取得 binary plan。** 系统让 DuckDB 的 cost-based optimizer 先给出 left-deep 或 bushy binary plan。bushy plan 被分解为若干 left-deep subplan；需要的中间结果先 materialize。

2. **翻译为 Free Join plan。** `binary2fj` 从最左 relation 的完整 atom 开始。对后续每个 relation，把当前已可用 variable 与其 schema 的交集放入当前 node 作为 probe subatom，剩余 variable 放入下一 node。对 \([R,S,T]\)，初始结果是

   \[
   [[R(x,a),S(x)],[S(b),T(x)],[T(c)]].
   \]

3. **factor lookup。** `factor` 逆序扫描 node；只有当 subatom 的 variable 全已可用、前一 node 没有同 relation subatom，并且同 node 中此前 lookup 也能一起移动时，才把它提前。clover plan 因而变为

   \[
   [[R(x,a),S(x),T(x)],[S(b)],[T(c)]].
   \]

   这一步把 \(T[x]\) probe 移出 \(b\) 循环，在论文构造实例上把 \(n^2\) 次无效展开压到 \(O(n)\)，同时不为 \(R\) 新建额外 hash table。[pdf:E08]（PDF 物理页 7，Figs. 8–10 与 Sec. 4.1）

4. **按 plan 构造 GHT/COLT。** GHT 的 internal node 是 `tuple → child` 的 hash map，leaf 是 tuple vector。实际实现使用 Column-Oriented Lazy Trie（COLT）：初始 leaf 只保存 base relation 的 row offset；只有 `get` 或非 suffix 的 `iter` 真正需要 key 时，才把当前 offset vector `force` 成 hash map。若最左 relation 只被遍历、不被 lookup，系统可直接扫描 columnar base table，完全不构建辅助结构。[pdf:E09]（PDF 物理页 8，Fig. 11 与 Definition 4.2）[pdf:E10]（PDF 物理页 8，Fig. 12 与 `new/iter/get/force`）

5. **执行 Free Join node。** 对当前 node，算法在 cover 的 GHT 上 `iter`；每得到一个 tuple，就从当前 tuple 与先前 binding 中抽取其他 trie 所需的 key，并逐个 `get`。任一 probe 失败就跳到 cover 的下一项；全部成功则用得到的 subtrie 替换原 trie，递归执行下一个 node；plan 为空时输出 tuple。[pdf:E07]（PDF 物理页 6，Fig. 7 与 Sec. 3.3）

6. **vectorized execution。** `iter_batch(batch_size)` 一次产生一批 tuple。系统对同一个 trie 连续 probe 整批 tuple，删除失败项，收集每项的 subtrie 后再递归，从而减少逐 tuple 递归打断 probe locality。cover 仍按 Generic Join 原则选择估计 key 数最少者；当 COLT 尚是 offset vector 时，只能用 vector 长度估计 key 数。论文同时指出一个未解矛盾：Generic Join 为 join 阶段最优倾向遍历最小 relation，传统 hash join 为减少 build cost 倾向遍历最大 relation。[pdf:E11]（PDF 物理页 9，Fig. 13、Example 4.3 与 Sec. 4.3）

实现边界是单机、single-threaded、main-memory Rust library；没有分布式执行、磁盘路径、并发调度、数值离散、固定步长或 FPGA 映射。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出新的复杂度定理证明，但有三条决定设计的形式化关系。

**第一，Free Join plan 是 atom 的 partition。** 对 query 中每个 atom \(R_i(\mathbf{x}_i)\)，其所有 subatom \(R_i(\mathbf{y}_1),R_i(\mathbf{y}_2),\ldots\) 必须对 \(\mathbf{x}_i\) 构成不重不漏的 partition。node \(\phi_k\) 可使用的 variable 为先前 node 已绑定 variable 的并集：

\[
avs(\phi_k)=\bigcup_{j<k}vs(\phi_j).
\]

若 node 中某个 subatom 覆盖 \(vs(\phi_k)-avs(\phi_k)\) 的全部新 variable，它就是 cover。这个条件保证：先迭代 cover 后，其他 subatom 的 lookup key 必然已经绑定；同一 node 不允许两个 subatom 来自同一 relation，避免一次递归层对同 relation 产生含糊状态。[pdf:E06]（PDF 物理页 5，Definitions 3.4–3.7）

**第二，build schema 由 subatom 顺序直接决定。** 若 relation 被 partition 为 \(R_i(\mathbf{y}_0),\ldots,R_i(\mathbf{y}_{\ell-1})\)，GHT schema 是 \([\mathbf{y}_0,\ldots,\mathbf{y}_{\ell-1},[]]\)。如果最后一个 subatom 是其 node 的 cover，就删除末尾空层，使它成为 vector 而不是多建一层 hash map。这是 Free Join 能精确退化到 binary hash table 布局的关键。[pdf:E07]（PDF 物理页 6，Build Phase）

**第三，factorization 改变工作量而不改变结果。** clover instance 中，\(R\Join S\) 在 \(x_2\) 上先展开会产生 \(n^2\) 个组合，但 \(T\) 不含 \(x_2\)。将 \(T[x]\) probe 提前后，只有共同 key \(x_0\) 进入后续 Cartesian product，因此由 \(O(n^2)\) 降为 \(O(n)\)。这不是一般情况下的全局复杂度保证，却说明“先求共享 key 的交，再展开 payload”为什么能消除 skew 放大的中间结果。[pdf:E08]（PDF 物理页 7，Fig. 8 与 factorization 例）

## § 7 — 实验设计与结论

**问题 1：Free Join 相对 binary join 与 Generic Join，在 acyclic/cyclic query 上是否更快？** → 作者在 JOB 与 LSQB 上比较 Rust Free Join、自己的 Rust Generic Join、DuckDB binary hash join，并补充 Kùzu。JOB 有 113 个 acyclic query、平均每个 8 个 join；作者排除 5 个空结果 query。LSQB 只取前 5 个 query，其余 4 个需要未支持的 anti-join 或 outer join；scale factor 为 0.1、0.3、1、3。运行平台为 Apple M1 MacBook Air、16 GB memory，所有系统 single-threaded、main-memory，并共享 DuckDB 产生的 binary plan。[pdf:E12]（PDF 物理页 10，Sec. 5.1–5.2） → 在 JOB 上，Free Join 对 binary join 的 geometric-mean speedup 为 2.94×，对 Generic Join 为 9.61×；最大分别为 19.36× 与 31.6×，但最差相对 binary join 为 0.85×，即慢 17%。Q13a 中 binary join 前三步在四张大表上产生超过一亿个中间 tuple；Free Join 先在共同 attribute 上求交，把运行时间从 DuckDB 的 10 秒以上降到略高于 1 秒。LSQB 结果说明 cyclicity 不是充分判据：q2 虽 cyclic，在大输入上 Free Join 反而略慢；作者将差异归因于该 plan 没有 skew join。[pdf:E12]（PDF 物理页 10，runtime comparison）[pdf:E13]（PDF 物理页 11，Figs. 14–16）

**问题 2：COLT 与 vectorization 各自贡献多少？** → COLT 与 simple lazy trie（SLT）、预先完全展开的 simple trie 比较；vectorization 用 batch size 1、10、100、1000 比较。[pdf:E13]（PDF 物理页 11，Figs. 17–18） → COLT 相对 SLT 与 simple trie 的 geometric-mean speedup 分别为 1.91× 与 8.47×，最大分别为 11.01× 与 26.29×。默认 batch size 1000 相对无 vectorization 的平均 speedup 为 2.12×，最大 5.33×；10/100/1000 之间差别不显著，作者的解释是小 batch 降低短 query overhead，大 batch 提升大 join throughput。[pdf:E14]（PDF 物理页 12，Sec. 5.3）

**问题 3：Free Join 是否像 WCOJ 一样对差 optimizer 更不敏感？** → 作者把 DuckDB cardinality estimator 改为恒定返回 1，迫使它产生差 plan，再比较 good/bad estimate 下的三种算法。[pdf:E12]（PDF 物理页 10，Setup） → Fig. 15 中三者相对排序仍是 Free Join、binary join、Generic Join；但 Fig. 20 显示 Free Join 与 binary join 一样会因差 plan 明显变慢，而 Generic Join 的变化较小。作者认为后者不是因为绝对性能更好，而是其 trie-building overhead 已主导 runtime。Free Join 的额外弱点是 poor estimate 常产生 bushy plan，而原型只用简单 vector materialize 全部 base-table attribute。[pdf:E13]（PDF 物理页 11，Figs. 15 与 20）[pdf:E14]（PDF 物理页 12，Sec. 5.4）

不得外推的范围包括：这些结果不证明 multi-thread、disk-resident、distributed 或 production optimizer 下仍有同样 speedup；也不能从少量 LSQB query 推出“所有 cyclic query 都适合 WCOJ”。

## § 8 — Take-aways

**5 句话。** Free Join 把 binary join 与 Generic Join 表示为同一个 plan/data-structure/execution 框架的两个端点。它从成熟的 binary plan 出发，通过 subatom partition 和 lookup factorization 把选择性 probe 提前。COLT 用 columnar base table 上的 row offset 延迟构造 trie，使不需要 lookup 的 relation 可以零辅助结构扫描。batch probe 给这个统一执行器补上 vectorized locality。实验支持“skew 与中间结果形状比 cyclic/acyclic 标签更能解释收益”，但也表明 Free Join 仍明显依赖 optimizer 与 materialization 质量。

**3 句话。** 这篇论文最重要的贡献是把 join algorithm 类别改写为 plan node 的粒度选择。真正的性能来源不是单一技巧，而是提前 probe、lazy trie 与 batch execution 的组合。统一框架带来了更大的设计空间，也把优化问题从“选 binary 还是 WCOJ”升级为“在连续空间里如何找 plan”。

**1 句话。** Free Join 证明 binary join 与 WCOJ 可以共享一台 iteration/probe 机器，性能关键在于每层何时绑定、何时 probe、何时展开 payload。

## § 9 — 最脆弱的假设

最脆弱的假设是：**一个已优化的 binary plan 是足够好的起点，后续保守 factorization 能在不重新做全局搜索的情况下找到高质量 Free Join plan。** 这不是实现细节；Free Join 的 relation order、lookup order、bushy materialization 边界都继承自 DuckDB。若 cardinality estimate 失真，系统可能先产生需要 materialize 的大中间关系，而 local factorization 无法跨越这些已固定边界。

论文给出的直接证据并不完全支持这一假设。bad-estimate 实验中，Free Join 的 slowdown 与 binary join 接近；作者明确把一部分问题归因于简单 materialization，但这也意味着当前实验无法区分“plan 起点错误”与“materialization 实现太弱”两种解释。[pdf:E14]（PDF 物理页 12，Sec. 5.4）此外，作者列出的三项限制是 main-memory only、binary cost-based optimization 与 Free Join heuristic factorization 分裂、optimizer 不利用 existing indices；磁盘上 COLT 的 repeated random access 甚至可能非常低效。[pdf:E15]（PDF 物理页 12，Sec. 6）

缺少的关键证据是：在控制 materialization implementation 相同后，对同一 query 穷举或近似搜索较大的 Free Join plan 空间，比较“从 binary plan 局部变换”与“全局联合优化”的 regret。没有这组实验，就不能知道当前 heuristic 离该空间中的最优点多远。

## § 10 — 最小复现实验

一周内最值得复现的是 **clover skew 机制 + 三项优化的最小拆解**，不必复现完整 JOB。

数据使用合成 clover query \(R(x,a),S(x,b),T(x,c)\)。令 \(R,S\) 在同一个 key \(x_2\) 上各有 \(n\) 个 payload，但 \(T\) 不含 \(x_2\)；另保留一个三表共有 key \(x_0\) 产生正确输出。让 \(n\) 从 \(10^2\) 扩到 \(10^5\)，另做一个无 skew、key 均匀的对照组。

实现四个版本：binary-style plan；只把 \(T[x]\) 提前的 factorized plan；factorized + eager trie；factorized + COLT + batch probe。所有版本使用相同语言、hash implementation、单线程和输出语义。测量 wall-clock、构建时间、join 时间、hash entry 数、展开的中间 tuple 数、peak memory，以及 batch size 1/10/100/1000。

若 factorized plan 在 skew 组把中间展开从约 \(n^2\) 降到近线性、且无 skew 组没有同量级收益，便支持“收益来自提前 probe 消除 skew amplification”这一核心 claim。若 eager 与 COLT 的差异主要出现在大量 subtrie 从未访问时，支持 lazy-build 机制。若 factorization 后仍是二次增长，或收益在无 skew 组同样巨大，则论文对机制的解释被反驳，应该检查 hash layout、cache 与输出 materialization 是否才是主因。

## § 11 — 最强反例设计

最强反例不是找一个 Free Join 慢一点的 query，而是构造一类使其三项机制同时失去优势、并让继承的 binary plan 变成负担的工作负载：disk-resident、existing index 可用、低 skew、高选择性在 optimizer 未识别的晚层、且 bushy plan 需要 materialize 大量 payload。

具体实验可用相同 logical query 制作两组 physical layout。A 组全在 memory、无 index；B 组数据大于 memory、关键 relation 有 covering index。对 binary join、Generic Join、当前 Free Join，以及一个允许 index-aware global plan search 的 oracle，统一测量 I/O page、random read、materialized bytes 与 end-to-end latency。然后把 cardinality estimate 系统性偏置 10×、100×、1000×。

若 Free Join 在 B 组因 COLT random access 与错误 bushy boundary 同时恶化，并且即使使用同样高效的 materialization 仍显著落后 oracle，则“从 binary plan 出发再 factor 就足够”被真正挑战。这个反例还能排除作者当前解释中的替代因素：若换成高效 materialization 后差距仍在，根因就更可能是 plan representation/optimizer split，而不是原型代码简单。

## § 12 — Follow-up Research Bet

### 主押注：把 Free Join 的离散 plan 改造成可联合求解的“join geometry compiler”

**新研究问题。** 能否不再从一个 binary plan 做局部修补，而是把每个 subatom 的 node 归属、cover、lookup order、factorized materialization boundary 与 batch granularity 编码成同一个可优化对象，直接为给定 query hypergraph 与数据分布综合出 binary–WCOJ 连续空间中的内部点？

**首次带来的能力。** 现有系统能选 binary endpoint、Generic Join endpoint，或按规则把前者推向中间；新 compiler 则能自动生成过去没有名称、也不属于任何固定算法家族的 join geometry，并给出其预期 build/probe/materialization 代价。删除这一编译表示后，系统会退回 endpoint selection 或 local factorization，因而新能力不是给 Free Join 外挂一个 predictor。

**核心机制与因果链。** 把 Free Join plan 表示为 query hypergraph 上的受约束 assignment：subatom 到 node 的位置保证 partition，cover assignment 保证 validity；COLT 的 offset-vector/hash-map 状态提供 build-work 与 probe-work 的可测成本；factorized intermediate 把“何时展开 payload”作为显式决策；vectorized execution 把 batch locality 作为执行成本。compiler 在小 query 上枚举可行 assignment 取得真实性能标签，再训练结构化 cost surrogate；对较大 query 使用 constrained search，直接最小化实测近似的 build + probe + materialization cost。这样，表示变化 → 可以搜索内部 plan → 内部 plan 同时协调 early intersection 与 lazy expansion → skew、output size 和 cache locality 不再由一个 binary 起点间接决定。

**改变的基本设计变量。** 它至少改变四项：plan 的状态表示（binary tree/variable order → subatom assignment graph）、优化目标（endpoint cost → build/probe/materialization 联合代价）、可控变量（cover、node boundary、展开边界、batch granularity）和数据生成方式（从 query execution 采集 counterfactual plan labels）。

**论文特异依据。** 方法侧，Free Join 已证明 subatom partition 与 cover validity 足以表达 binary、Generic 及其内部 plan，Figs. 9–10 还给出 binary-to-Free-Join 与 factorization 的可执行变换。[pdf:E06]（PDF 物理页 5，Free Join plan 定义）[pdf:E08]（PDF 物理页 7，Figs. 9–10）实验侧，Q13a 表明内部 plan 可通过提前共同 attribute 的交集消除超过一亿个中间 tuple；另一方面 bad-estimate 实验显示 local factorization 仍继承 binary optimizer 的脆弱性。[pdf:E12]（PDF 物理页 10，Q13a 与 LSQB 讨论）[pdf:E14]（PDF 物理页 12，Sec. 5.4）limitations 还直接指出 two-phase optimizer、factorized materialization 与 smallest-versus-largest cover 是尚未统一的自由度。[pdf:E15]（PDF 物理页 12，Sec. 6）

**与最近工作的实质区别。** 在本文引用并讨论的最近路线中，Freitag et al. [7] 依据 estimated cardinality 在 Generic Join 与 binary join 之间切换；本文 Free Join 从 binary plan 出发做 heuristic factorization。该押注不做 endpoint switch，也不只增加 cardinality predictor，而是改变 plan representation 和 experimental object：研究对象从“两类算法谁更快”变为“一个受约束的 join geometry space 是否可被可靠综合”。由于本卡按 source-closed 规则未联网检索 2023 年后的工作，这只是候选差异判断，不声称 novelty。

**最大收益与最大风险。** 成功后，数据库可以把 skew、build cost、factorized output 与 locality 放进一次 plan synthesis，Free Join 才真正从统一执行器升级为统一 optimizer。最大科学风险是 cost landscape 不平滑：small-query 标签训练出的 surrogate 可能无法外推到不同 cardinality、cache 或 disk hierarchy，离散 assignment 的 rounding 也可能抹掉 relaxed search 的优势。

**首个证伪实验。** 在可穷举的小型 4–7 relation query 上，完整枚举合法 Free Join plan，建立真实最优值；训练 compiler 后在未见过的 cardinality/skew 上比较四组：DuckDB binary、Generic Join、论文 heuristic、compiler。关键机制对照不是换模型，而是把 compiler 的 plan representation 限制为两个 endpoint 或只允许论文 factor move。若 unrestricted representation 不能稳定缩小相对真实最优值的 regret，或收益完全可由更好的 cardinality estimate 解释，则“内部 geometry 可综合”这一机制被否证。

**Wild-card alternative。** 用不同机制把“未展开 COLT”提升为跨 join、aggregation 与 materialization 的一等 factorized intermediate，使 bushy pipeline 在最终消费前都不枚举 payload tuple；这改变的是中间结果对象与算子接口，而不是 plan 搜索变量。
