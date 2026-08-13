# Better Together: Unifying Datalog and Equality Saturation

- 作者：Yihong Zhang、Yisu Remy Wang、Oliver Flatt、David Cao、Philip Zucker、Eli Rosenthal、Zachary Tatlock、Max Willsey
- 出处：Proceedings of the ACM on Programming Languages（PLDI 2023，Article 125）
- 年份：2023
- DOI：10.1145/3591239
- Zotero key：UIAINUF3
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的是两套已经很成熟、却各缺一半能力的 fixpoint reasoning 工具为何不能协同。Datalog 擅长把事实存成关系，以 bottom-up rule evaluation、query optimization 和 semi-naive evaluation 高效完成程序分析，却很难让“两个值从此不可区分”自然地参与所有关系查询。Equality saturation（EqSat）擅长用 e-graph 保存海量等价 term、做 congruence closure 和非破坏式 rewrite，却难以组合多个会互相反馈的语义分析。作者提出 **egglog**：以函数式数据库为底座，把 equivalence、term construction、lattice value 与 Datalog rule 放进同一个 fixpoint 系统。[pdf:E01]（PDF 物理页 1，Abstract 与 Section 1）

问题之所以重要，不只是两种语言能否统一。现有真实系统已经为能力缺口付出代价：浮点表达式优化器 Herbie 因不能方便地证明 rewrite 的前置条件而使用 unsound rules，之后再丢弃错误结果；Datalog 指针分析 cclyzer++ 为绕过低效的 equivalence join，组合 choice domain、subsumptive rules 和自制等价表示，复杂到引入两个可导致 unsound result 的独立 bug。论文的核心工程 claim 是：若把 equality 变成数据库的内建身份关系、把 partial function 的冲突处理开放成 `:merge`，同一执行模型就能让这两类应用更短、更快且更可靠。[pdf:E02]（PDF 物理页 2，Section 1，egglog extensions 与 case-study claims）

## § 2 — 前人工作与不足

Datalog 的基础优势是清楚的：relation、conjunctive query 和 immediate consequence operator 组成单调的 bottom-up fixpoint；lattice Datalog 又把 relation 推广为从 tuple 到 lattice value 的函数，用 join 合并重复 key 的结果。它已被广泛用于 points-to analysis。但经典 relation 无法高效表达“等价元素在所有后续查询中都应不可区分”：显式等价闭包会占二次空间，即使用 Soufflé 的 union-find-backed `eqrel`，普通 relation 仍要与等价关系额外 join。[pdf:E03]（PDF 物理页 4，Sections 2.1–2.2，Datalog lattice 与 EqSat 背景）

EqSat 的优势则是解决 rewrite phase ordering：每轮同时应用规则并保留新旧 term，e-graph 用 e-class 紧凑表示相同语义的 e-node。它的问题是标准机制偏 syntactic。egg 的 e-class analysis 虽能给每个 e-class 附上 semilattice value，却只能有一个 analysis，信息主要从 child 向 parent 传播，还必须写 host-language Rust；复杂的 multi-pattern matching 也有专门且复杂的算法。relational e-matching 已证明 e-matching 可转成数据库 join，但需在 e-graph 与 relational database 两份表示间复制，收益会被同步成本抵消。[pdf:E04]（PDF 物理页 5，Section 2.2，e-class analysis、multi-pattern 与 dual representation）

因此，论文并不是简单把两种语法拼在一起。它接续了 Flix/lattice Datalog、Soufflé `eqrel`、egg e-class analysis 与 relational e-matching 的收敛趋势，但改变了事实源：**整个 EqSat 都从数据库视角执行**，不是只把 matching 临时翻译成 relation；同时 equality 又成为 Datalog 数据库的内建、可扩展语义，而不是一张需要反复 join 的辅助表。论文还把这一设计与 database chase 中的 tuple-generating/equality-generating dependencies 联系起来，但选择了更受限的语法与 union-find，以换取目标领域里的确定性和速度。

## § 3 — 重建作者的思考路径

可以把作者抵达 egglog 的路径重建成六步。

1. Datalog 与 EqSat 都是在不断增加已知事实，直到 fixpoint；差别主要在“事实长什么样”和“相等如何影响后续推理”，而不是迭代骨架。
2. 若把 relation 看成返回 `unit` 的 partial function，普通 Datalog fact 就能落进函数表；若函数返回非 `unit` 值，重复 key 必须有统一的冲突处理。
3. lattice Datalog 已说明一种冲突处理是 `join(old,new)`；e-graph congruence 又说明另一种冲突处理是把两个 output id `union`。于是 `:merge` 可以成为统一抽象。[pdf:E05]（PDF 物理页 6，Fig. 3 与 Section 3.2）
4. 若 user-defined sort 的值由 union-find id 表示、数据库始终 canonicalize，那么等价 id 在 rule matching 时天然不可区分；“join modulo equivalence”可退化成普通 equality join。
5. constructor 也只是带“缺失时生成新 id”默认行为的 function。这样 term creation、congruence closure 和 rewrite 都能表述为 function lookup、conflict repair 与 ordinary rule，不再需要独立 e-graph 表示。[pdf:E06]（PDF 物理页 7，Fig. 4 与 Section 3.3）
6. 一旦 e-matching 已是 database query，Datalog 的 semi-naive evaluation 便可直接增量化它；而多个分析又只是更多函数和规则，能够向任意方向传播并彼此合作。

这条路径的关键，是从两个领域的“数据结构名字”退回到共同约束：函数依赖、等价关系、增量事实和 fixpoint。统一由此不是 API wrapper，而是把 equality repair 与 lattice repair 都变成同一个可编程数据库动作。

## § 4 — 核心 Intuition

核心 intuition 可以压缩成三句话：把每个 relation 当成 partial function，把等价值当成同一个 canonical id，把同一 key 的多个 output 如何合并交给 `:merge`。当 `:merge` 取 lattice join 时，egglog 像 lattice Datalog；当 `:merge` union 两个 user-sort id 时，rebuilding 就是 congruence closure，egglog 像 EqSat。因为 rules、terms、analyses 与 equality 都生活在同一数据库中，Datalog 的增量 join 与 EqSat 的非破坏式 rewriting 可以直接共用。[pdf:E07]（PDF 物理页 8，Sections 3.3–3.4，rewrite desugaring）

## § 5 — 具体方法与完整 Pipeline

以“最短路 + 节点合并 + term rewrite”三个逐步扩展的例子来看，egglog 的完整 pipeline 如下。

1. **声明数据。** `relation edge (i64 i64)` 实际 desugar 成返回 `unit` 的 function；普通 rule 查询 function table，匹配到变量后执行 `set`，因此经典 transitive closure 可原样表达。
2. **让 fact 携带 lattice value。** 把 `path(x,y)` 改成返回 `i64` 的 function，并声明 `:merge (min old new)`。当直达路径给出 30、两跳路径给出 20 时，function dependency 不允许同一 `(1,3)` 有两个 output，merge 选 20；从 lattice 角度，这是以反向数值序为偏序的 supremum。[pdf:E05]（PDF 物理页 6，Fig. 3b 与 Section 3.2）
3. **引入可统一的对象。** user-defined sort 的值是 opaque id，union-find 保存 equivalence。`union (mk 3) (mk 5)` 后，数据库 canonicalization 让节点 3 与 5 对所有 query 不可区分，原本断开的 reachability 可以贯通。
4. **用 function constructor 造 term。** `datatype Math` 展开成一个 sort 与若干 constructor functions。缺失的 function call 通过 `:default` 创建 fresh id；嵌套 call 把 term 按需放入数据库。
5. **把 rewrite 变成 rule。** `(rewrite p1 p2)` desugar 为：匹配 `p1` 得到某 id，构造 `p2`，再 union 两者。所有 query 都在 canonical database 上执行，所以 matching 天然 modulo equality；rule 只增加事实，所以 rewrite 非破坏式。[pdf:E07]（PDF 物理页 8，Section 3.4，rewrite desugaring）
6. **修复 congruence。** 若输入 id 的 union 让两条 function entry 的 key canonicalize 成同一 key，rebuilding 调用 function 的 `:merge`。constructor 默认 union 冲突 output，于是父 term 也变等价，形成 congruence closure。[pdf:E08]（PDF 物理页 9，Sections 3.4–4 opening）
7. **执行 rules。** 每轮先用 immediate consequence operator 产生新 entries，再重复 rebuilding 直到数据库 canonical 且所有 function dependency 恢复；外层继续迭代到 fixpoint，或按用户给定的有限轮数停下。
8. **增量匹配。** semi-naive evaluator 保存本轮新增/更新的 `ΔDB`，把每条有多个 body atom 的 rule 展开为“至少一个 atom 来自 delta”的若干 delta rules，避免每轮重新发现旧 match。
9. **查询或 extraction。** verification 可直接检查两个 expression id 是否相同；optimization 则从目标 e-class 抽取 cost 最小的代表 term。

实现约 4,200 行 Rust。functional database 用 map 保证 dependency；rebuilding 源自 egg 与经典 congruence-closure algorithm；query engine 使用 relational e-matching 与 worst-case optimal Generic Join。论文没有报告分布式执行、持久化数据库、GPU/FPGA mapping 或并发伸缩结果，这些不应从“database-native”表述中外推。[pdf:E12]（PDF 物理页 13，Section 5.1–5.2）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文形式化的是一个“行为良好”的 core egglog 子集：对 uninterpreted ids，merge 固定为 union；对 interpreted constants，merge 固定为 complete lattice 的 join。完整语言允许任意 egglog expression 作 merge，因此形式语义没有覆盖所有实际程序。[pdf:E08]（PDF 物理页 9，Section 4 opening）

首先，schema instance 写成 `I=(DB,≡)`：`DB` 是 function entries `f(v1,…,vk) ↦ v` 的集合，`≡` 是 uninterpreted ids 上的 equivalence；interpreted constants 只能等于自己。任取全序后，canonicalization `λ≡(t)=min {t' | t'≡t}` 给每个等价类选代表。nested atom 不能直接入表，所以 `flatten_I` 递归把子 term 变成 flat entries；若缺失 function output，user sort 生成 fresh id，interpreted sort 使用 lattice bottom。[pdf:E09]（PDF 物理页 10，Fig. 5 与 Section 4.2）

rule application 使用 inflationary immediate consequence operator：

`T↑_P(I) = DB ∪ T_P(I)`，

其中 `T_P` 枚举所有令 body ground atoms 在 `I` 中成立的 substitution，并把代入后的 head 用 `flatten_I` 展开。之所以显式保留旧 `DB`，是因为完整 egglog 的 analysis value 可能变化，单条 rule 未必满足标准 Datalog 的单调性。[pdf:E10]（PDF 物理页 11，Section 4.2，ICO definition）

执行 `T↑_P` 后，同一 key 可能指向多个 output，只得到 pre-instance。rebuilding operator `R` 分两类修复：若 output 是 uninterpreted ids，把相同 canonical key 的 outputs 加入 equivalence closure；若 output 是 interpreted constants，对冲突集合取 `⊔K`。随后用新 equivalence 再 canonicalize 全库；canonicalization 又可能制造新冲突，因此定义 `R∞` 为反复 rebuild 到 fixpoint。一次程序迭代是

`F_P = R∞ ∘ T↑_P`。

作者用 expanded database 定义 information order `⊑I`：右侧至少知道左侧的所有 facts 与 equalities。即使 `F_P` 本身一般不单调，从空 instance `I⊥` 出发的迭代序列仍单调增加，因而 evaluation 定义为 inductive fixpoint `[[P]]=F∞_P(I⊥)`；实际可能发散，所以实现通常只计算有限轮 under-approximation。[pdf:E11]（PDF 物理页 12，Section 4.2 与 Algorithm 1）

semi-naive evaluator 把本轮变化记作 `ΔDB_i=DB_i−DB_{i−1}`。对 body 有 `m` 个 atoms 的 rule，它生成 `m` 个 delta variants，每个 variant 至少让一个位置查询 `ΔDB`。Appendix B 的 Theorem B.1 证明 semi-naive 与 naive evaluation 每轮产生相同 instance：关键是普通 `T_P` 对数据库集合包含关系单调、delta rules 覆盖所有本轮新 match，以及 `R∞(R∞(I)∪DB)=R∞(I∪DB)`，再用归纳把两边的 rule results 化为同一 rebuild input。[pdf:E28]（PDF 物理页 33，Appendix B，Theorem B.1 与 Eqs. (1)–(12)）

## § 7 — 实验设计与结论

**问题 1：database-native EqSat 与 semi-naive evaluation 是否真的更快？→ 实验：**作者取 egg 的 math test suite，删除需要 analysis 的 rules，使 egglogNI（关闭 semi-naive）与 egg 每轮生成同一 e-graph；三套系统均用 egg 默认 BackOff scheduler 跑 100 iterations，每个 iteration 各跑 7 次取中位数。所有实验运行在 Apple M2、16 GB MacBook Pro。**答案：**相同 e-graph 下，egglogNI 在第 100 轮比 egg 快 3.34×，说明 relational matching/query optimization 本身有收益；开启增量后 egglog 构造略大的 e-graph 仍快 9.27×，显示 semi-naive 避免重复 match。不过这不是 analysis-heavy workload，也没有拆分 compilation、rebuild 与 extraction 成本。[pdf:E13]（PDF 物理页 14，Fig. 7 与 Section 5.3）

**问题 2：内建 canonical equality 能否让 Steensgaard points-to analysis 更简单且更快？→ 机制与实验：**经典 Soufflé encoding 必须在 `vpt` 与 `eqrel` 间做 join modulo equivalence；egglog 把 equivalent allocation ids 主动 canonicalize，普通 equality join 即可。[pdf:E14]（PDF 物理页 15，Section 6.1，join-modulo-equivalence example）作者重写 cclyzer++ 的 context-/flow-/path-insensitive、field-sensitive 子集，对 postgresql-9.5.2 programs 设 20 s timeout，并比较 `eqrel`、原 cclyzer++、修复两处 soundness bug 的 `patched`、egglogNI 和 egglog。**答案：**除原 cclyzer++ 外，其余系统的 points-to relation size 一致；`eqrel` 除一个 case 均 timeout，patched 与 cclyzer++ 在最右三个 benchmark timeout。排除 timeout case 后，egglog 平均比最快 sound Soufflé encoding `patched` 快 4.96×，比原 cclyzer++ 快 1.94×，比 egglogNI 快 1.59×。[pdf:E15]（PDF 物理页 16，baseline definitions 与 discovered bugs）[pdf:E16]（PDF 物理页 17，Fig. 8 与结果段）

**问题 3：多个可组合 analysis 能否让 Herbie 在不使用 unsound rewrite 的情况下仍有用？→ 机制与实验：**作者在 egglog 中分别写 interval analysis 和 not-equals analysis；前者以 `max` 合并 lower bound、以 `min` 合并 upper bound，后者同时使用 interval facts 与 rewrite 新推导的 facts。两者共同证明 division/cancellation rules 的 side conditions。例如先证明 `v+1≠v`，再推导 cube roots 不等，才能 soundly 使用差立方分解 rewrite。[pdf:E17]（PDF 物理页 18，Figs. 9–10 与 Section 6.2）作者在 Herbie 的 289 个 floating-point programs 上比较原 unsound ruleset 与 egglog sound analysis。**答案：**sound 版本总耗时 73.91 min，对照为 81.91 min；104 cases 中 sound 版本找到更准确程序，但 135 cases 中 unsound ruleset 更准确。一个 extreme input 原方案无法解而 sound 方案可解；另一 outlier 因 egglog rational overflow。结果证明“sound 且整体更快”，却不证明当前 sound analyses 已覆盖原 ruleset 的优化能力。[pdf:E18]（PDF 物理页 19，Figs. 11–12；报告数字见物理页 18 相邻正文）

**外推边界。** microbenchmark 只覆盖无 analysis 的 math rules；points-to benchmark 是 PostgreSQL 9.5.2 的一类 analysis；Herbie 同时改变了 soundness 与搜索空间。论文没有给出置信区间、跨硬件复跑、内存峰值、超大规则库、并行 scaling 或 termination benchmark。速度数字支持这三个 workload 上的实现判断，不能直接推出 egglog 对所有 Datalog/EqSat 程序都更快。

## § 8 — Take-aways

**5 句话：**

1. egglog 的统一点不是共享前端，而是让 function dependency repair 同时承载 lattice join 与 equality union。
2. canonical ids 把 Datalog 中昂贵的 join modulo equivalence 变成普通 equality join，也让所有 rule matching 天然 modulo equality。
3. functional database、rebuilding 与 Generic Join 组成单一表示，消除了 relational e-matching 的 e-graph/database 双表示同步成本。[pdf:E19]（PDF 物理页 20，Related Work，relational e-matching）
4. semi-naive evaluation 因此第一次自然地成为增量 e-matching 方案，而 multiple functions/rules 又让 semantic analyses 可以分开定义、互相传播。
5. 三组实验展示了更快 EqSat、sound 且更直接的 unification-based points-to，以及 sound Herbie，但 termination、proof generation 和更广 workload 仍是开放问题。[pdf:E20]（PDF 物理页 21，Related Work，termination 与 logic-programming comparison）

**3 句话：** egglog 把 Datalog 的 relational fixpoint 与 EqSat 的 congruence fixpoint 压到同一个 canonical functional database 中。`:merge` 是最关键的接口：它决定冲突 output 是做 lattice join、union，还是完整语言中的其他组合。论文最有力的证据不是抽象“统一”，而是两个原应用的真实失败模式在同一机制下同时被简化并加速。

**1 句话：** egglog 证明了 equality saturation 可以是一种带内建 equality 的增量数据库计算，而 Datalog 也可以自然地操纵 term 与 congruence。[pdf:E21]（PDF 物理页 22，Conclusion）

## § 9 — 最脆弱的假设

最脆弱的假设是：**应用可以被组织成持续增加信息的 fixpoint，使 canonicalization 与 `:merge` 的重复执行最终在可承受时间和空间内停下来。** egglog 明确允许 divergence，因为几乎所有实用 EqSat rule set 都可能无限增长；core semantics 只保证从空 instance 出发的信息序列增加以及 fixpoint 存在，并不保证有限时达到它。完整语言甚至允许任意 merge expression，Appendix A 的 capture-avoiding substitution 例子同时依赖 set membership 的正、负条件，作者明确说该程序一般不是 monotonic。[pdf:E22]（PDF 物理页 26，Appendix A.1，bottom-up evaluation 与 demand）[pdf:E23]（PDF 物理页 27，Appendix A.2，non-monotonic free-variable analysis）

若这个假设失效，论文最核心的“统一执行模型”仍可能有表达力，却不能作为可靠 engine：rule 会不断生成 fresh ids/terms，分析值和 equivalence 反复触发 rebuilding，semi-naive 只能少做重复工作，不能阻止新事实无限出现。论文的三个 benchmark 都通过固定 100 iterations、20 s timeout 或应用自身的 search procedure 控制运行；它们没有系统评估 termination condition。作者也把借助 chase termination theory 理解 egglog termination 明列为 future work。因此，证据支持“这些案例有效”，尚不支持“语言中自然写出的组合 analysis 通常会收敛”。

## § 10 — 最小复现实验

一周内最有信息量的复现，是把论文的两个核心机制拆开验证，而不重做整个 Herbie 或 cclyzer++。

- **数据：**构造参数化 graph family：`n` 个 pointers，各自指向随后会被 union 的 `k` 个 allocation ids；再加一组 load/store rules，使查询反复需要判断两个 allocation 是否等价。取 `n∈{10^2,10^3,10^4}`、`k∈{2,4,8}`。
- **实现：**写三个等价程序：显式 equivalence relation；union-find eqrel 但 query 仍 join modulo equivalence；egglog function `vpt(pointer) -> Allocation` 且冲突 `:merge` 为 union。另对 egglog 分别打开/关闭 semi-naive。规则与输出语义保持一致。
- **测量：**检查最终 canonical points-to pairs 是否相同；记录 relation/table rows、rule matches、rebuild 次数、peak RSS 与 wall time。单独统计“加入一批新 union 后继续求 fixpoint”的增量成本。
- **支持标准：**若 egglog 输出与显式模型一致，且随 `k` 增大仍保持每 pointer 一个 canonical output、内存不随显式等价 pair 数二次增长，便支持 canonical equality 的核心 claim；若 egglog 只是把成本转移到 rebuild，导致时间或内存也近二次增长，则反驳其主要 scalability 解释。semi-naive on/off 的差异进一步区分“canonical representation”与“增量 rule evaluation”各自贡献。

这个实验直接对应论文 points-to 的关键机制，不依赖 PostgreSQL front-end，也不会把已有 benchmark timeout 当作证明；它能给出可证伪的 complexity curve。

## § 11 — 最强反例设计

最强反例应攻击 `:merge + rebuilding` 既表达丰富分析、又保持高效这一核心，而不是只找一个慢 benchmark。构造一个 **merge–canonicalize feedback ladder**：第 `i` 层有许多 function entries 的 keys 仅在本层 union 后碰撞；这些碰撞的 merge 又 union 下一层 outputs；下一轮 canonicalization 再制造更多 key collisions。同时加入两个 lattice analyses，让每次 equivalence 扩张都提高一个 bound，并由 bound 解锁新的 term-producing rule。控制最终可达数据库有限，避免把“它本来就发散”当作答案。

比较四个变体：egglog 完整执行、关闭 semi-naive、把 equality closure 与 analysis 分阶段批处理、以及手写专用 union-find worklist。测量每条最终 fact 被重写/canonicalize 的次数、每层 rebuild rounds、总 join work、peak memory，并验证结果相同。若 egglog 即使开启 semi-naive 仍对同一旧 entries 做层数乘表规模的反复 rebuild，而专用 worklist 近线性完成，就说明论文展示的速度主要来自案例中 equality/analysis feedback 较浅，而非统一表示的一般优势。该反例也能排除“仅仅 query optimizer 不好”的替代解释，因为瓶颈被刻意放在 merge-induced congruence repair。

## § 12 — Follow-up Research Bet

### 主押注：把 fresh-id hole 发展成“可抽取的双向规格执行”

**新能力先行。** 候选研究问题是：能否让同一份 egglog program 不再只从输入 term 向前分析或优化，而是把**部分输入、输出约束和未知中间结构同时放入数据库**，在一个共享 equality space 中增量合成满足约束的最小程序及其解释？成功后，egglog 会首次成为一种可双向运行的 specification engine：用户可以给出“已知 shape、未知 implementation、要求某些 type/equation 成立”，系统既传播 semantic constraints，也填充 structure holes，最后 extraction 直接返回候选实现。

这个押注来自 Appendix 中两项尚未合流的能力。第一，调用尚未定义的 user-sort function 会创建 fresh id 作为未知值，之后 rule 与 union 可以把这个 hole 填成 concrete term；tree-size 例子用它在 bottom-up engine 中模拟 demand-driven top-down evaluation。[pdf:E22]（PDF 物理页 26，Fig. 13 与 Appendix A.1）第二，type inference rules 能把 typing context 自顶向下传到 subexpression，再把 inferred type 自底向上汇合；simply typed lambda calculus 示例甚至让 matrix shapes 参与 cost-relevant type reasoning。[pdf:E24]（PDF 物理页 28，Fig. 15 与 Appendix A.2）Hindley–Milner 例子进一步表明，fresh type variables、function injectivity 和 occurs-check 可以分别写成 modular rules，而不需要手写可变 alias graph。[pdf:E25]（PDF 物理页 29，Appendix A.3，unification rule 与 HM explanation）

**因果链。** partial specification 调用未知 function → `:default` 生成稳定 fresh id，形成显式 hole → top-down demand rules 只实例化与目标相关的 subproblems → type/shape/equation analyses 约束 hole → constructor congruence 与 injectivity 把 equality 双向传播到结构及其 children → alternative constructors 仍在 e-class 中并存 → cost/proof extraction 返回最小实现及短 derivation。这里改变了至少四个基本变量：研究目标从“优化给定完整 term”变为“补全部分规格”；状态表示加入持久 hole 与 constraint-bearing e-class；数据生成方式由初始 AST 改为需求驱动的结构生成；评价对象从 rewrite throughput 变为 solution completeness、最小性与 explanation size。

论文的 equation-solving pearl 已证明 rules 可以改写整个 equation，并利用隐式 substitution 解简单多变量方程；proof datatype 又能让同一 fact 的不同 proofs 因 proof irrelevance 而压缩，并通过标准 extraction 取短 proof。[pdf:E26]（PDF 物理页 31，Fig. 17 与 Appendix A.4）[pdf:E27]（PDF 物理页 32，Figs. 18–19，proof extraction 与 guarded matrix rewriting）这些细节说明“hole + constraint + extraction”不是任意外接 synthesis wrapper，而是论文已有语义对象可能组成的新计算模式。

**与最近工作的实质区别。** 论文讨论的 EqSat 工作主要从完整 program 出发扩展 equivalent program space；Datalog±/chase 主要回答 ontology/query；Prolog 用 top-down search、backtracking 和 logic variables；SMT 求一个满足模型但不原生维护可抽取的最小 term universe。该候选把 egglog 的 bottom-up incremental database、non-destructive equivalence space、fresh ids 与 native extraction 组合成需求驱动的 partial-program completion。未做更广全文检索，因此这是基于本文证据的候选判断，不声称 novelty。

**最大收益与科学风险。** 最大收益是 analysis、synthesis 与 explanation 不再通过多个 IR/solver 往返：修改一条约束可用 semi-naive delta 增量更新可行实现空间。最大风险是 unrestricted constructor generation 与 equality rules 会爆炸或发散；更深的风险是 egglog 的 least/universal result 语义也许适合“包含所有推论”，却不等价于枚举所有有意义的程序选择，导致 completeness 或 extraction objective 无法定义。

**首个区分性实验。** 选择一个小型 typed matrix-expression completion benchmark：输入 matrix dimensions 与带 2–4 个 holes 的 partial expression，目标给定 output shape 和 algebraic equality；允许 `MMul`、`Kron`、transpose 与少量 guarded rules。比较三种系统：egglog 双向 hole propagation、只做 forward EqSat 后枚举填 hole、SMT/枚举器生成候选后再交 EqSat。固定同一深度与 operator set，测首次解时间、增量修改一个 dimension 后的更新时间、表示的候选数、最优 cost 与解的完备率。再删除 injectivity/top-down demand rules做 ablation：若完整 egglog 显著减少枚举且增量修改可复用数据库，同时仍找齐 bounded-depth solutions，才支持“共享 equality space 的双向传播”机制；若收益仅来自更好的枚举顺序，forward baseline 会在等量 candidate budget 下追平。

**Wild-card alternative：**用 proof irrelevance 与 equation-level rewriting 构造一个“proof-space optimizer”，把不同 Datalog derivations 合并为等价 proof class，并让 domain-specific proof transformations与短证明 extraction 在同一 fixpoint 中协同；它改变的是评价对象与表示，而不是 partial-program synthesis。
