# Sketch-Guided Equality Saturation: Scaling Equality Saturation to Complex Optimizations of Functional Programs

作者：Thomas Kœhler、Phil Trinder、Michel Steuwer。[pdf:E01]（PDF 物理页 1，标题页）

出处：arXiv:2111.13040v2 [cs.PL]。[pdf:E01]（PDF 物理页 1，标题页侧栏）

年份：2022。[pdf:E01]（PDF 物理页 1，标题页侧栏日期）

DOI：未报告。

Zotero key：FTNRHE5S

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：这篇论文要解决的不是“equality saturation（等式饱和）能否做编译优化”，而是它能否在 functional program（函数式程序）上承受真正复杂、需要成千上万次 rewrite 的优化。** 作者识别出两个相互叠加的瓶颈：一是 unguided equality saturation 以广度优先、纯增量方式保留大量等价程序，遇到 associativity、commutativity、loop transformation 等规则组合时，e-graph 会在到达目标前耗尽时间和内存；二是函数式语言中的 λ-binding、substitution 与 polymorphic type 若采用朴素编码，会进一步制造大量 α-equivalent terms 和中间 substitution terms。论文把解决方案也分成两条轴：用 sketch-guided equality saturation 控制搜索跨度，用更高效的 λ-calculus encoding 控制单个状态空间的体积。[pdf:E02]（PDF 物理页 2，Section 1 与 Fig. 1）

这个问题重要，因为 term rewriting 的 phase-ordering problem（阶段排序问题）具有结构性：某条 rewrite 的局部收益取决于后续 rewrite，贪心策略容易卡在局部最优；手写 strategy 又把所有排序责任转移给编译器作者。论文的目标是找到一个中间点：仍由语义保持的 rewrite rules 保证正确性，但只让人指定少量“程序应当长成什么样”的粗粒度路标，而不指定几千到几万步的精确路径。摘要报告，在七个 matrix multiplication 优化上，unguided 方法即使给到一小时和 60 GB RAM 也只能找到最简单的两个，而使用不超过三个 sketch guides 后，七个目标都能在秒级、低于 1 GB RAM 的条件下找到。[pdf:E01]（PDF 物理页 1，摘要）

价值不只在 matrix multiplication。若这种分工成立，编译器可以把“探索等价实现”的机械工作交给 e-graph，把“优化过程的大方向”留给领域专家，从而降低高性能 DSL、array language 和 domain-extensible compiler 中优化策略的开发成本。论文直接证明的是 Rise 语言与一组矩阵乘优化；把结论外推到其他语言、任务和硬件仍需要额外证据。

## § 2 — 前人工作与不足

论文面对的前人路线主要有三类。

第一类是 Elevate rewriting strategies 或 schedule：程序员明确写出 rewrite 的组合与作用位置。它们能产生高性能代码，但控制粒度过细。论文以 Rise 的 blocking 为例：Fig. 2 展示了从高层 map/reduce 矩阵乘到包含分块循环结构的程序，Listing 1 则用 tile、fission、split 和 reorder 明确规定变换顺序。[pdf:E03]（PDF 物理页 4，Fig. 2 与 Listing 1）论文进一步报告，相关案例的 strategy 开发估计耗费 2–5 person-weeks；一个名为 reorder 的 strategy 有 43 行、组合了 8 个内部 strategies，却仍只适配该矩阵乘例子；完整案例需要 tens of thousands of rewrite steps。其不足不是“没有自动化”，而是自动化边界停留在执行 strategy，phase ordering 仍由人逐步承担，且细小程序差异可能迫使 strategy 重写。[pdf:E04]（PDF 物理页 5，Section 2.2 “Limitations of manual rewriting with strategies”）

第二类是传统 equality saturation。它通过把 rewrite 两侧的相等关系加入 e-graph，而不是立即替换原项，保留多条路径，从而绕开局部最优。论文的 transpose/map-fusion 例子说明：最优项需要先应用不会降低 term size 的 transpose 交换与 associativity，之后 map fusion 才能发生；只按局部 cost 贪心不会走出这条路径。[pdf:E05]（PDF 物理页 5，Section 2.3，式 (A)、(B) 与 rewrite rules (1)–(3)）Fig. 3 展示了 e-graph 如何逐轮加入新 e-nodes/e-classes，并以 congruence sharing 压缩大量等价项。[pdf:E06]（PDF 物理页 6，Fig. 3 与其后 equality-saturation 说明）不足在于 breadth-first、additive exploration：当目标依赖长 rewrite chain，搜索空间增长速度会先于目标出现速度，sharing 只能延缓而不能消除爆炸。

第三类是已有的扩展技术。论文对相关工作的概括是：automatic optimization、rewriting strategy/schedule、theorem-proving guidance 与 program synthesis sketch 各解决了部分控制问题；其中 proof sketch 与 program sketch 提供了“用不完整结构引导搜索”的先例，但此前 sketch 主要用于 proof 或 synthesis，而不是从等价程序集合中筛选优化结果。[pdf:E07]（PDF 物理页 22，Section 6 “Related Work”）针对 e-graph 扩展性，egg 的 BackoffScheduler 会抑制 explosive rules，但 Rise 的目标优化有时恰好依赖这些规则；external solver 又要求先识别可委托子任务；朴素 explicit substitution 对复杂 λ-term 也过于昂贵。[pdf:E08]（PDF 物理页 23，Section 6 “Other techniques for scaling equality saturation”）因此，已有方法不是完全无效，而是在“保留足够多的 rewrite 可能性”和“避免保留太多可能性”之间缺少可操作的中间控制层。

## § 3 — 重建作者的思考路径

可以从论文出现之前的事实与失败模式重建出下面的推理链。

1. **先承认手写 strategy 的能力。** Rise/Elevate 已经证明，复杂 loop blocking、reorder、vectorization 和 parallelization 可以通过语义保持 rewrite 获得高性能代码；真正的障碍不是缺少 rewrite rules，而是必须把规则按正确顺序施加到正确位置。[pdf:E03]（PDF 物理页 4，Fig. 2 与 Listing 1）
2. **再用 equality saturation 消除局部 phase ordering。** transpose/map-fusion 例子表明，e-graph 同时保留“暂时变差但以后有利”的路径，这比贪心或单一路径重写更符合全局优化需求。[pdf:E05]（PDF 物理页 5，Section 2.3，rewrite rules (1)–(3)）
3. **观察自动搜索的新失败点。** 长优化并不是单纯把短优化多跑几轮；每轮都会在已有 e-graph 上继续纯增量扩张，某些规则组合造成指数式候选增长。于是“完全不规定顺序”在复杂任务上反而不可计算。
4. **寻找比 rewrite sequence 更低带宽的人类输入。** 编译器作者通常能画出期望 loop nest 或程序片段，却很难写出从输入到该结构的全部 rewrite。论文中的 blocking 目标只需表达“先 split、再 reorder 后得到怎样的嵌套”，而不必写出每一步；Listing 2–4 显示，sketch 可以省略大量内部程序细节，仅保留 map/reduce 的维度与嵌套形状。[pdf:E09]（PDF 物理页 8，Listings 2–4 与 Section 3.1）
5. **同时处理函数式表示造成的额外冗余。** 即使搜索被分段，若每次 β-reduction 都把 substitution 的中间步骤塞进 e-graph，或每次引入 binder 都生成新名字，单段搜索仍会迅速膨胀。因而还需要一种主要牺牲搜索 completeness、但不把无关中间状态写入 e-graph 的 substitution 方法，以及能让 α-equivalent binders 结构相同的表示。[pdf:E10]（PDF 物理页 12，Table 1、Fig. 9 与 Section 4.1）[pdf:E11]（PDF 物理页 13，Fig. 10 与 Section 4.2）

由此自然得到论文的组合方案：把人类可表达的程序形状变成一串 coarse-grained checkpoints；每到一个 checkpoint 就抽取一个代表项并重启搜索；同时用 De Bruijn indices、extraction-based substitution、保守 freshness predicate 与显式 monotype 信息压缩每个阶段的 λ-term 搜索。

## § 4 — 核心 Intuition

核心 Intuition 是：不要让一个 e-graph 从原程序一直背负所有等价路径到最终优化目标，而是让程序员给出少量结构性路标，每到一个路标就抽取一个满足 sketch 的程序并用 fresh e-graph 继续。[pdf:E09]（PDF 物理页 8，Section 3.1 与 blocking sketches）Sketch 只描述目标形状，不描述 rewrite 路径，因此细节仍由 equality saturation 自动探索，人工控制从 fine-grained phase ordering 降为 coarse-grained phase ordering。[pdf:E12]（PDF 物理页 10，Section 3.3、Fig. 7、Listing 6 与 Fig. 8）与此同时，De Bruijn indices 消除大量 α-equivalent 表示，extraction-based substitution 避免把 substitution 的中间过程全部写进 e-graph。[pdf:E10]（PDF 物理页 12，Section 4.1）[pdf:E11]（PDF 物理页 13，Section 4.2）本质上，方法用少量人为结构信息换取对搜索峰值规模的控制，而不是用人为信息替代 rewrite 搜索。

## § 5 — 具体方法与完整 Pipeline

以论文的 matrix multiplication blocking 为例，完整 pipeline 如下。

1. **输入高层函数式程序。** 初始 Rise 程序用两层 map 遍历输出矩阵，并用 reduce 表达 dot product；它描述计算含义但不固定 loop blocking、执行顺序或具体低层实现。目标程序具有按 32、32、4 分块和重排后的 loop nest。论文用 Fig. 2 对照了输入、优化后 Rise term 与直观循环结构。[pdf:E03]（PDF 物理页 4，Fig. 2）
2. **建立适合 e-graph 的 λ-calculus 表示。** `λx.e`、application 与 variable 分别编码为 `lam x e`、`app e1 e2`、`var x` 一类 operator/child 结构；实际 Risegg 再把 bound variable 转为 De Bruijn index，并在 binder 数量变化时做 index shifting。[pdf:E10]（PDF 物理页 12，Table 1 与 Fig. 9）为避免 polymorphic expression 在不同实例化下发生类型混淆，Risegg 把 instantiated monotype 嵌入 e-graph，每个 e-class 关联一个精确类型，并对重复类型做 hash-consing。[pdf:E13]（PDF 物理页 15，Sections 4.3–4.4）用户仍可写 name-based、partially typed rewrite rules；编译器进行 type inference、检查两侧良类型性，再内部翻译为带 De Bruijn indices 和 shift 的规则。[pdf:E14]（PDF 物理页 16，Section 4.5）
3. **写最终 sketch 与中间 sketch guide。** blocking 的最终 sketch 只规定外层 `m/32`、`n/32`，内部 `k/4`、`4`、`32`、`32` 的 map/reduce 嵌套；中间 sketch 只要求 loops 已 split、尚未 reorder。两者都不枚举 split/join/transpose 等完整程序细节。[pdf:E09]（PDF 物理页 8，Listings 3–4）
4. **把 sketch 解释为 term set。** SketchBasic 只有四个构造：通配符 `?`、精确 operator 形状 `F(...)`、递归包含 `contains(...)` 和析取 `∨`；Rise 的 sketch abstractions 再叠加 type sketch，以数组长度和元素类型限制 map/reduce 的迭代域。[pdf:E15]（PDF 物理页 9，Fig. 6 与 Section 3.2）
5. **为每一阶段配置三件事。** 每个 checkpoint 绑定一个 sketch、一个 local monotonic cost model 和一组 rewrite rules。论文的实现通常用 weighted term size；不同阶段可复用配置，也可限制规则集以减少无关交互。[pdf:E12]（PDF 物理页 10，Section 3.3）
6. **执行 sketch-satisfying equality saturation。** 对当前 term 先做可配置 normalization；矩阵乘案例使用 βη normal form。随后创建 fresh e-graph，反复应用本阶段 rules，直到当前起始 e-class 中出现满足 sketch 的 term。论文把“找到 sketch”置于进一步优化 cost 之前，因此一旦满足就停止增长。[pdf:E12]（PDF 物理页 10，Listing 6 与 Fig. 8）[pdf:E16]（PDF 物理页 11，Section 3.4 前的停止条件说明）
7. **按 sketch 约束抽取并重启。** `extract` 不只是找全图最低 cost term，而是在满足当前 sketch 的候选中找最低 cost term；这个 term 成为下一阶段输入，上一阶段 e-graph 不再携带。对 `?`、`F(...)`、`contains(...)`、`∨` 四种 sketch，论文分别用 e-class analysis 与递归组合实现约束抽取。[pdf:E16]（PDF 物理页 11，Section 3.4 “Sketch-Satisfying Extraction”）
8. **在 rewrite 中处理 substitution 与 binder。** β-reduction 不采用 explicit substitution 的逐步 e-graph 展开，而是从相关 e-classes 各抽取一个具体 term，在普通 term 层完成 substitution，再把结果加回 e-graph。它更省空间，但只覆盖 e-class 所代表项的一个子集，是有意的近似。[pdf:E10]（PDF 物理页 12，Section 4.1）论文用 Fig. 10 展示了一个可能漏掉 `id y` 的案例；作者称在 Rise 实验中未观察到它阻碍优化，并认为跨 iteration 的不同抽取、congruence 与后续 rewrite 会恢复一部分遗漏等价项。[pdf:E11]（PDF 物理页 13，Fig. 10 与其后说明）
9. **输出与验证。** 当最后一个 sketch 满足后，Rise 程序继续 lower 到 C/OpenCL 一类 imperative code。实验并未重新给出完整性能基准，而是检查生成 C code 与此前手工优化、已证明可达到 TVM 级性能的版本在忽略变量名后相同。[pdf:E17]（PDF 物理页 19，Section 5.2 的验证方法）

论文未报告 FPGA mapping、实时步长、多速率仿真、通信拓扑或片上资源时序；实际搜索平台是 AMD Ryzen 5 PRO 2500U 与 Intel Xeon E5-2640 v2 上的 CPU/JVM 环境。[pdf:E17]（PDF 物理页 19，Section 5.2 “Experimental Setup”）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有复杂定理证明，但有一套清楚的集合语义与 dynamic programming 式抽取公式。理解它们的关键是：**sketch 是一个 term predicate，e-graph extraction 是在这个 predicate 下做最小化。**

**1. SketchBasic 的集合语义。** 语法为

\[
S ::= ? \mid F(S,\ldots,S) \mid contains(S) \mid S\lor S.
\]

令 \(T\) 为全部 terms，\(R(s)\subseteq T\) 为 sketch \(s\) 接受的 terms，则：

\[
R(?)=T,
\]

\[
R(F(s_1,\ldots,s_n))=\{F(t_1,\ldots,t_n)\mid t_i\in R(s_i)\},
\]

\[
R(contains(s))=R(s)\cup\{F(t_1,\ldots,t_n)\mid \exists t_i\in R(contains(s))\},
\]

\[
R(s_1\lor s_2)=R(s_1)\cup R(s_2).
\]

直觉上，`?` 不施加约束；`F` 约束根节点和每个 child；`contains` 把“根满足”扩展为“任意深度子树满足”；`∨` 合并两类结构。对 typed language，论文再定义 \(R(s::pt)=R(s)\cap R(pt)\)，即 term shape 与 type shape 同时满足。[pdf:E15]（PDF 物理页 9，Fig. 6 与 Section 3.2）

**2. 多阶段搜索可以写成受约束的函数复合。** Listing 6 的过程可等价概括为：从 \(t_0\) 出发，第 \(i\) 阶段在

\[
g_i=EqSat(normalize(t_{i-1}),rules_i)
\]

中增长到 `found(g_i, e_i, sketch_i)` 成立，然后计算

\[
t_i=\arg\min_{t\in e_i\cap R(sketch_i)} cost_i(t).
\]

这里第二个式子是对论文伪代码与抽取定义的等价重写，而非论文单独编号的公式。关键变化是每个 \(t_i\) 只把一个满足 checkpoint 的代表项传给下一阶段，不把 \(g_i\) 整体传递。[pdf:E12]（PDF 物理页 10，Fig. 7、Listing 6 与 Fig. 8）

**3. Sketch-satisfying extraction。** 论文定义 \(E(c,s,g)\)，返回从每个 e-class 到 `Option[(cost, term)]` 的映射。对 `?`，它就是普通 local-cost extraction；对 \(F(s_1,\ldots,s_n)\)，只有当每个 child e-class 都能抽出满足对应 \(s_i\) 的 term 时，父 e-node 才形成候选；对 `contains(s)`，先把直接满足 \(s\) 的结果作为 base case，再用 e-class analysis 向父节点传播；对 \(s_1\lor s_2\)，合并两侧结果并保留较低 cost。其成立条件是 cost function local 且 monotonic，这样 child 的局部最优才能安全组成 parent 的局部最优。[pdf:E16]（PDF 物理页 11，Section 3.4 的四个 cases 与公式）

**4. λ-calculus 的核心 rewrite 与近似。** β-reduction 是 \((\lambda x.b)e\rightarrow b[e/x]\)，η-reduction 是 \(\lambda x.f\,x\rightarrow f\)（条件为 \(x\) 在 \(f\) 中不自由）；map-fusion 与 map-fission 又会在右侧引入新的 λ-binding。[pdf:E10]（PDF 物理页 12，Fig. 9）Explicit substitution 会把诸如 \((ab)[e/v]\rightarrow a[e/v]\,b[e/v]\) 的中间项全部加入 e-graph；extraction-based substitution 则执行“抽取 \(b,e\) 的代表项 → 普通 substitution → 加回结果”三步，从而减少状态数。[pdf:E10]（PDF 物理页 12，Section 4.1）

**5. De Bruijn indices 与保守 predicate。** 内部规则用 `%0` 一类 index 替代 bound name；删除或新增 binder 时用 \(\varphi\) 做 index shifting。以 η-reduction 为例，name-based 的 \(\lambda x.f\,x\rightarrow f\) 会编译成含 `%0`、类型参数和向外 shift 的 index-based rule。[pdf:E14]（PDF 物理页 16，Section 4.5 “Example 1: η-reduction”）对 freshness，Risegg 只在“e-class 中所有 terms 都满足变量不自由”时应用 η-reduction，而不是只要存在一个满足项就应用；这会漏掉合法 rewrite，但避免把不合法 term 混入同一 e-class。[pdf:E13]（PDF 物理页 15，Fig. 11 与 Section 4.3）

基于这些定义可以得出一个重要工程判断：论文中的近似主要牺牲的是 **equivalence coverage/completeness**，不是主动加入语义不等价项。extraction-based substitution 可能漏掉某些代表项组合，universal freshness predicate 可能拒绝某些合法 rewrite；两者都让搜索更保守。这是基于算法结构的推断，论文并未给出一般性的 completeness 或 soundness 定理。

## § 7 — 实验设计与结论

**问题一：高效 λ-calculus encoding 是否真的必要？**

实验：作者在一个 untyped Rise subset 的早期 Risegg prototype 上，组合两种 substitution 方案（explicit / extraction-based）与两种 binder 表示（named / De Bruijn），形成四种 encoding；用 reduction、fission、binomial 三个逐步变难的 rewrite goals 测试，在 AMD Ryzen 5 PRO 2500U 笔记本上把 RAM 限制为 2 GB。[pdf:E18]（PDF 物理页 17，Section 5.1 “Experimental Setup” 与 Figs. 13–14）binomial 是二维卷积到两个一维卷积的真实优化，先前需编排 30 条 rewrite rules，其中 17 次为 η/β-reduction。[pdf:E19]（PDF 物理页 18，Fig. 15 与 Table 2 上方说明）

答案：只有 extraction-based substitution + De Bruijn indices 找到 binomial，报告为 0.1 s、8 MB、约 5K rules、3K e-nodes、1K e-classes；同一组合在 reduction 与 fission 上分别为 0.002 s 与 0.006 s，均约 3 MB。其余三种组合都无法找到 binomial并在 2 GB 限制下失败；explicit substitution + named variables 连 fission 也失败。[pdf:E19]（PDF 物理页 18，Table 2）这支持“二者是互补而非可任选”的 claim：只改 binder 或只改 substitution 都不足以跨过最复杂测试。

**问题二：sketch guidance 是否把复杂优化从不可行变为可行？**

实验：作者在 full Risegg（Scala）上重现七个 TVM manual / Elevate 中的 matrix multiplication goals：baseline、blocking、vectorization、loop permutation、array packing、cache blocks、parallel。guided 与 Elevate 跑在 AMD Ryzen 5 PRO 2500U、JVM 可用 4 GB；unguided 跑在更强的 Intel Xeon E5-2640 v2、JVM 可用 60 GB。两种 equality-saturation 方法都以同一个 goal sketch 作为停止条件；找到后检查生成 C code 与已有手工优化版本在忽略变量名后相同。[pdf:E17]（PDF 物理页 19，Section 5.2 与 “Experimental Setup”）

答案：unguided 只找到 baseline 与 blocking。blocking 需要超过 1 小时、约 35 GB、5M rules、4M e-nodes、2M e-classes；vectorization 与 loop-perm 超过 1 小时且超过 60 GB，array-packing、cache-blocks、parallel 在约 35 分钟时超过 60 GB。guided 则七个目标全部找到：除 baseline 外耗时 4–7 s、RAM 0.3–0.5 GB，使用 1–3 个 guides，最大约 11K rules、11K e-nodes、7K e-classes。[pdf:E20]（PDF 物理页 20，Tables 3–4）因此“能否找到目标”和 peak memory 的差异非常强；但由于两组运行平台不同，表中的绝对 runtime 不宜作为严格的同机 speedup。

**问题三：收益是否确实来自切断 e-graph 的累积增长？**

实验：Fig. 16 逐 iteration 画出 blocking 与 parallel 的 rules、e-nodes、e-classes。unguided 曲线达到百万量级并在 parallel 第 7 iteration 左右耗尽 60 GB；guided 在每个 purple sketch line 后以抽出的 term 启动 fresh e-graph，曲线回到小规模，再增长到下一个 checkpoint。[pdf:E21]（PDF 物理页 21，Fig. 16）

答案：案例中 guided 的最大图规模约 11K，相比 unguided 的百万量级小约三个数量级。论文还报告，Table 5 中六个非 baseline 目标都复用 `split` 作为第一个 guide；sketch 单体大小为 7–12，而完整 program size 为 90–124，约 90% 细节被省略；若 blocking 搜索在每阶段天真地启用全部 rules，runtime 会增加约 25×，说明 guide 之外，stage-specific rule set 也是机制的一部分。[pdf:E22]（PDF 物理页 21，Fig. 16 后的 “Sketches Guiding the Search” 与 “Choice of Rules and Cost Model”）[pdf:E23]（PDF 物理页 22，Table 5 与其后 cost-model 说明）

**不能外推的范围。** 证据集中在一个 functional array language、一个 λ-encoding 实现和一个 matrix multiplication 优化族。生成代码的“高性能”主要通过与既有手工版本的代码同构及既有工作的性能结论间接确认，本论文没有对七个生成 kernel 重新报告统一的端到端运行时间。实验也没有覆盖不规则控制流、递归、效应、动态 shape、大规模多程序 benchmark 或不同硬件 backend。

## § 8 — Take-aways

**5 句话：** ① Equality saturation 能缓解 phase ordering，却会因 additive breadth-first exploration 在长 rewrite chain 上先发生 e-graph explosion。② Sketch-guided equality saturation 让程序员只规定少量程序形状 checkpoint，并在每个 checkpoint 后抽取一个 term、重启 fresh e-graph。③ 这种分段在七个矩阵乘优化上把百万级图和 35–60 GB 级失败压到约 11K 节点、0.5 GB 以内，并让全部目标在秒级找到。[pdf:E20]（PDF 物理页 20，Tables 3–4）[pdf:E21]（PDF 物理页 21，Fig. 16）④ 对 functional language，extraction-based substitution 与 De Bruijn indices 同样关键，缺少任一项都无法完成最复杂的 binomial goal。[pdf:E19]（PDF 物理页 18，Table 2）⑤ 最强证据是“可行性跨越”，最弱环节是 guide、rule set 与 cost model 是否能在新领域中同样简洁地获得。

**3 句话：** 论文把优化控制从“逐条 rewrite”提升为“逐阶段程序形状”，保留自动搜索又限制峰值状态空间。它还表明，e-graph 上的 λ-calculus engineering 不是次要实现细节，而会决定真实优化是否可计算。结果对 Rise 矩阵乘很有说服力，但尚不足以证明所有复杂编译优化都存在短而有效的 sketch decomposition。

**1 句话：** 这篇论文的核心贡献，是用少量结构性 checkpoints 和更紧凑的 λ 表示，把 equality saturation 从“短优化自动化”推进到“部分复杂优化可实际搜索”。

## § 9 — 最脆弱的假设

**最脆弱的假设是：对目标优化存在一条短、可由人发现的 sketch decomposition，并且每个阶段选出的单个低 cost term 都是通向下一阶段的良好入口。** 这是方法能否扩展的支点；若任一 checkpoint 太模糊，阶段内仍会爆炸；太精确，则可能排除可行实现；若 cost model 从多个满足 sketch 的 terms 中选到错误代表，fresh restart 会丢掉上一 e-graph 中尚未显式保留的替代路径。

论文给出的正面证据是，六个复杂目标只需 1–3 个 guides，且这六个目标共享 `split`，sketch 大小 7–12 而 program 大小 90–124；这说明在该优化族中确有紧凑、可复用的结构词汇。[pdf:E23]（PDF 物理页 22，Table 5）但同一页之前的分析也表明，选择 rules 很敏感：把全部 rules 用于 blocking 会慢约 25×。[pdf:E22]（PDF 物理页 21，“Choice of Rules and Cost Model”）论文结论把“如何识别每阶段适当 rule sets”“如何为更多应用设计有效 sketches”“能否自动 synthesise sketch guides”列为 future work，本身即承认该假设尚无一般解法。[pdf:E24]（PDF 物理页 23，Section 7 末段）

实际中它可能失效的原因有三种。其一，某些优化的关键中间态是非局部代数性质、数据依赖或跨过程 invariant，无法用小型 tree-shape sketch 表达。其二，一个 sketch 可能接受大量结构相近但后续可达性完全不同的 terms，weighted term size 与“能否到下一目标”不一致。其三，新领域的 rewrite rules 交互可能没有清晰阶段边界，任何人为分段都会在边界处丢失必要组合。论文没有测试 adversarial checkpoints、跨应用 guide transfer，或对不同抽取 cost 的系统敏感性，因此这一假设目前只在高度相关的矩阵乘优化族中得到支持。

## § 10 — 最小复现实验

一周内最值得复现的是：**同一 rewrite system、同一硬件、同一最终 goal 下，加入一个结构性 checkpoint 是否显著降低 peak e-graph size。** 不必复现完整 Rise compiler 或 TVM 性能。

**数据与语言。** 从 Fig. 2 抽取一个简化的 symbolic loop-nest / array IR，至少包含 `map`、`reduce`、`split`、`join`、`transpose` 和 sequential/parallel lowering 记号；用 symbolic dimensions `m,n,k` 表达矩阵乘。最终目标选择 blocking，进阶目标可选 parallel。依据论文给出的结构，定义 `split` 中间 sketch 与 `reorder/lower` 最终 sketch。[pdf:E03]（PDF 物理页 4，Fig. 2）[pdf:E09]（PDF 物理页 8，Listings 3–4）

**实现。** 用一个支持 e-class analysis 的 e-graph library 实现两条完全相同的 rewrite rule 集合和 weighted term-size extraction。模式 A 从初始 term 直接跑到最终 sketch；模式 B 先跑到 `split` sketch，抽取最低 cost term，建立 fresh e-graph，再跑到最终 sketch。两种模式必须在同一机器、同一进程配置、同一 iteration/node/time caps 下运行。另做一个 ablation：模式 B 每阶段使用全部 rules，对比 stage-specific rules。

**测量。** 记录 `found?`、wall-clock time、peak RSS、每 iteration 的 e-nodes/e-classes、applied rules，以及最终 term 是否满足同一 goal sketch。论文 Tables 3–4 与 Fig. 16 给出了预期现象：unguided 在百万级增长，guided 在 checkpoint 后重置并保持约万级。[pdf:E20]（PDF 物理页 20，Tables 3–4）[pdf:E21]（PDF 物理页 21，Fig. 16）

**支持标准。** 在至少 5 次重复中，guided 稳定找到目标，且 peak e-nodes/e-classes 比 unguided 低至少 100×，或在相同资源 cap 下 guided 成功而 unguided 失败；stage-specific rules 还应明显优于 all-rules guided。**反驳标准。** unguided 在相同 cap 下稳定成功且 peak graph 与 guided 同量级，或 guided 经常在中间抽取后无法到达最终目标；后一结果会直接质疑 checkpoint 与单代表传递机制，而不是只说明实现慢。

## § 11 — 最强反例设计

最强反例应攻击“抽取一个 checkpoint representative 并丢弃旧 e-graph”这一核心机制，而不是简单换一个更大的 benchmark。

构造一个语义保持的 rewrite system，使初始项 \(t_0\) 在第一阶段产生两个 terms：\(u_{cheap}\) 与 \(u_{gateway}\)。二者都满足同一个中间 sketch \(s_1\)，但 weighted term-size 满足 \(cost(u_{cheap})<cost(u_{gateway})\)。第二阶段使用论文允许的 stage-specific rules：从 \(u_{gateway}\) 能短路径到最终 sketch \(s_2\)，从 \(u_{cheap}\) 则无法在该规则集内到达，或必须先恢复第一阶段中已丢弃的结构并引发巨大爆炸。因为 SGES 在当前 sketch 一旦找到后就停止，并抽取一个最小 cost term 作为下一阶段唯一输入，它会稳定选择 \(u_{cheap}\) 并失败；单次 unguided e-graph 则仍同时保留 \(u_{gateway}\)，可以找到 \(s_2\)。这一攻击直接利用 Listing 6 的 early stop、单 term extraction 与 fresh restart。[pdf:E12]（PDF 物理页 10，Listing 6 与 Fig. 8）[pdf:E16]（PDF 物理页 11，Section 3.4）

实验上可生成一族“diamond” rewrite graphs，系统改变两条分支的 cost gap、到达 \(s_1\) 的先后顺序和通往 \(s_2\) 的深度。所有 rewrite 都必须语义等价，确保失败不是 correctness 问题。攻击成立的判据是：在资源相近甚至更低时，unguided 能找到最终 goal，而论文原始 one-best SGES 因 checkpoint 抽取选择而系统性失败；改变 cost model 会改变成败，但不改变 sketch 本身。若出现这一结果，就说明 sketches 只约束局部结构，不能保证 checkpoint term 的 downstream reachability，方法的 coarse phase ordering 仍可能需要隐含的全局规划。

## § 12 — Follow-up Research Bet

**主押注：把 SketchBasic 从“单次优化的 checkpoint 语言”提升为“面向程序族的参数化 optimization state space”，构建可复用的 sketch-transition atlas。** 这是候选判断；由于任务限定只使用源 PDF、未检索更广泛全文，这里不声称 novelty。

新的研究问题是：能否学习或归纳一个由 typed sketches 构成的状态图，使编译器对一族程序、shape 与 target configuration 复用优化知识，而不是为每个输入重新手写 guide sequence？它首次可能实现的是 **amortized equality saturation**：一次积累的优化轨迹可以迁移到未见过的矩阵尺寸、相邻算子组合甚至新 backend，优化对象从“一个 concrete term”变为“满足某个 parameterized sketch 的 term family”。

核心机制是一条因果链。首先，把 Fig. 6 的 typed SketchBasic 扩展为带 symbolic dimensions、data-layout class 和 execution-space variables 的节点表示；节点不是某个程序，而是一片结构化 term region。[pdf:E15]（PDF 物理页 9，Fig. 6 与 typed sketch 说明）其次，把每次成功的 stage 记录成一条 transition edge，edge 的内容不是完整 rewrite script，而是 `rule subset + cost model + normalization + observed target sketch`。再次，从多个程序的成功 traces 中合并同构节点与 edges，形成 atlas；新程序先匹配起始 sketch，再组合 atlas 中的 transitions，按 symbolic parameters 实例化各阶段 equality saturation。这样，sketch 不再只是一次性 stop predicate，而成为编译器跨任务共享的 optimization IR。

论文提供了两项直接支撑。一项来自 method：sketch 本身有集合语义、type restriction 与可组合 constructs，天然比 concrete program 更适合作为抽象状态。[pdf:E15]（PDF 物理页 9，Section 3.2）另一项来自 experiment：Table 5 中六个非 baseline 目标共享 `split` guide，sketch 只有 7–12 个 operators、程序有 90–124 个 operators，rules 与 cost models 也被作者认为可打包复用；同时，错误地使用全部 rules 会让 blocking 慢约 25×，说明“某类 sketch transition 应绑定哪组 rules”蕴含可学习、可迁移的结构信息。[pdf:E22]（PDF 物理页 21，“Sketches Guiding the Search” 与 “Choice of Rules and Cost Model”）[pdf:E23]（PDF 物理页 22，Table 5）

它至少改变四个基本设计变量：问题定义从单程序搜索改为程序族知识迁移；状态表示从 concrete term/e-graph 改为 parameterized sketch region；数据生成方式从一次运行改为跨任务 transition traces；评价对象从单次 compile time 改为 held-out transfer、amortized search cost 与 atlas coverage。与论文中的 rewriting strategies/schedules 相比，它不存储逐步命令；与当前 SGES 相比，它不要求每次由人给出完整 sketch sequence；与论文结尾提到的“自动 synthesise sketch guides”相比，它的中心不是为单个输入生成一条 guide，而是学习一个可组合、可复用的 transition space。论文确实把 rule-set identification、guide synthesis 与 interactive optimization assistants 列为未来方向，但没有展开这种 family-level representation。[pdf:E24]（PDF 物理页 23，Section 7 末段）

最大研究收益是形成一种可迁移的优化词汇：新的 DSL 或硬件 backend 只需建立少量节点/edge 对齐，就可能继承已有优化阶段，而不从零开发 strategy。最大科学风险是 sketch region 内部异质性过高：两个 terms 结构上匹配同一 sketch，却具有不同 downstream reachability，导致 transition 在训练程序上有效、在新程序上失效；atlas 也可能随 type、shape 与 backend 组合发生另一种状态爆炸。

首个可证伪实验是用论文七个 matrix multiplication goals 做 leave-one-goal-out。用六个目标的成功 traces 构建 atlas，保留 symbolic `m,n,k` 和 tile sizes；对第七个目标与未见尺寸，只允许组合既有 sketch nodes/edges，不允许回放该目标的 concrete rewrite sequence。比较三种方法：atlas transfer、只记 rule frequency 的 generic scheduler、精确 script memoization。若 atlas 在 held-out goal/shape 上以更小 peak e-graph 找到目标，而且打乱 sketch-node identity 后优势消失，就支持“结构化 transition state”而非“只是规则先验或记忆脚本”的机制；若只能复现训练程序或性能等同 rule-frequency baseline，主押注被反驳。

**Wild-card alternative：** 构建同时重写 program、data layout 与 hardware communication topology 的联合 e-graph，让 sketch 直接描述 CPU/GPU/FPGA memory hierarchy 与并行拓扑，从“寻找等价程序”转向“联合合成算法—存储—通信实现”。
