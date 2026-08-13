# egg: Fast and Extensible Equality Saturation

作者：Max Willsey、Chandrakana Nandi、Yisu Remy Wang、Oliver Flatt、Zachary Tatlock、Pavel Panchekha（PDF 物理页 1，标题与作者栏）[pdf:E01]

出处：arXiv:2004.03082v3（源 PDF 版本，PDF 物理页 1）[pdf:E01]

年份：2020（源 PDF 版本日期，PDF 物理页 1）[pdf:E01]

DOI：10.1145/3434304

Zotero key：XTMQVVBV

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 这篇论文解决的不是“如何再发明一种 rewrite”，而是如何让 equality saturation（等式饱和）所依赖的 e-graph 真正适合优化与程序综合工作负载。作者指出两个阻塞点：其一，传统 e-graph 为自动定理证明器设计，几乎每次修改后都立即恢复 congruence invariant（同余不变量），在持续增长的等式饱和图中代价很高；其二，常量折叠、自由变量、tensor schema、代价等语义事实无法仅靠句法 rewrite 表达，过去只能靠每个项目各自修改 e-graph 内部实现。论文因此提出 rebuilding 与 e-class analysis 两条主线，并把它们实现为可复用库 egg（PDF 物理页 1–2，摘要、Section 1 与贡献列表）[pdf:E01][pdf:E02]

问题重要，是因为 equality saturation 的核心价值在于消除 phase ordering problem（阶段排序问题）：不是破坏性地选择某一次 rewrite，而是把多个等价表达式压缩在同一张图中，直到饱和或超时，再按 cost function 抽取最优项。Figure 2 展示了 rewrite 只增加 e-node、边和等价关系，甚至可用一个环紧凑表示无限多个表达式；Figure 3 则给出“初始化 e-graph → 反复应用 rewrites → extraction”的完整工作流（PDF 物理页 4，Fig. 2；物理页 6，Fig. 3）[pdf:E03][pdf:E04]

**基于证据的推断。** 如果 e-graph 维护成本随候选空间增长得比有效优化收益更快，或者每加入一个领域事实都要重新实现内部数据结构，那么 equality saturation 虽然在概念上解决了 rule ordering，却仍然难以成为通用工程工具。egg 的价值在于同时改变算法边界与扩展接口：前者减少重复的 invariant maintenance，后者把领域推理变成稳定的库级抽象；这使“写 grammar、rewrite 与 cost function”更接近一个可重复的优化器构建流程，而不是一次性的研究原型（PDF 物理页 2，贡献列表；物理页 20，Section 5.3）[pdf:E02][pdf:E05]

## § 2 — 前人工作与不足

**论文对相关文献的概括。** 经典 e-graph 与 congruence closure 来自自动定理证明和 SMT solver。那类系统会交错查询、合并、理论推理与 backtracking，因此必须让 hashcons 与 congruence 在每次操作后都可立即使用；传统 upward merging 正是为这个在线、可撤销的工作负载服务。等式饱和虽然复用了同一数据结构，却是单调增加信息、无需 backtracking、按轮次批量 search 与 apply 的另一类工作负载。作者认为，沿用“每次 merge 都修复”的策略会做大量重叠工作（PDF 物理页 2，Equality Saturation Workload；物理页 26，E-graphs and E-matching 与 Congruence Closure）[pdf:E02][pdf:E06]

已有 equality saturation 工作解决了 destructive term rewriting 的 phase ordering，但没有解决三个工程缺口。第一，各项目常自建 e-graph，难以共享性能优化；第二，常量折叠等 interpreted reasoning 往往是遍历并直接操作 e-graph 的 ad hoc pass；第三，通用 SMT solver 虽然能力更广，却可能为不需要的 disjunction、theory 与 backtracking 付费。论文用 TASO 的等式验证任务说明第三点：Z3 用时 24.65 秒，egg 用时 1.56 秒，开启 batch evaluation 后为 0.52 秒；这是特定任务上的比较，不代表 egg 取代 SMT（PDF 物理页 6，Section 2.3）[pdf:E07]

作者对 novelty 的定位也很克制：rebuilding 与 Downey 等人的离线 congruence closure 核心结构相近，创新重点是**何时**恢复 invariant，以及如何把它嵌入在线 equality saturation；论文同时明确没有给出 online setting 下 rebuilding 的理论复杂度分析，性能很可能依赖 workload。对 e-matching，egg 采用既有 pattern compilation，并未宣称覆盖所有 theorem prover 索引优化（PDF 物理页 26，Related Work）[pdf:E06]

## § 3 — 重建作者的思考路径

下面是**基于证据的逆向重建**，不是作者逐字给出的研究日记。

1. 从 destructive term rewriting 出发：一次替换会丢掉旧表达式，因此某条 rule 过早执行可能阻断以后更优的组合；e-graph 通过保留并合并等价表达式缓解这一问题（PDF 物理页 4，Fig. 2；物理页 6，Fig. 3）[pdf:E03][pdf:E04]
2. 再观察工作负载差异：ATP 必须随时查询和撤销，而 equality saturation 在一轮内可以先收集所有 match，再统一写入，且信息只增不减。于是，“任何时刻 invariant 都必须成立”不再是天然前提，而是可以重新选择的执行策略（PDF 物理页 2，Equality Saturation Workload）[pdf:E02]
3. 检查 eager repair 的具体浪费：多个 merge 会沿相同 parent path 反复 upward merge。若把待修复 e-class 放入 worklist，并在真正 repair 前 canonicalize 与去重，重叠路径就可合并处理（PDF 物理页 8，Fig. 4 与其后解释）[pdf:E08]
4. 用构造性例子验证方向：一组 hashcons 更新可从传统策略的二次量级降到线性量级；宽度为 `w`、深度为 `d` 的嵌套项族中，repair 调用可从 `O(wd)` 降为 `O(d)`。这说明收益不是单纯常数优化，而来自把重复工作跨 merge 摊销（PDF 物理页 8，Section 3.2.1；物理页 9，Section 3.2.1 续）[pdf:E09][pdf:E10]
5. 最后处理 extensibility：既然 e-class 已经代表一组等价项，领域事实也应挂在 e-class 上；如果这些事实只会通过 join 单调累积，就可以与 merge、rebuild 共用同一传播框架，而 conditional/dynamic rewrite 与 extraction 则直接消费这些事实（PDF 物理页 13，Section 4.1；物理页 15，Sections 4.2–4.3）[pdf:E11][pdf:E12]

这条路径的关键不是先决定“做一个 Rust 库”，而是先识别出 equality saturation 与 ATP 的时序约束不同，再把“延迟恢复”和“单调语义事实”统一成可复用的数据结构接口。

## § 4 — 核心 Intuition

把 equality saturation 的一轮看成一个 epoch：在只读阶段基于一致快照寻找全部 rewrite match，在只写阶段批量加入等价关系，最后只做一次 rebuild（PDF 物理页 10，Fig. 5）[pdf:E13]。rebuild 通过 worklist canonicalization 与去重，把多次 merge 产生的重叠 upward-merging 路径合并；e-class analysis 则让语义信息通过 join-semilattice 单调汇入每个 e-class（PDF 物理页 8，Fig. 4；物理页 13，analysis invariant）[pdf:E08][pdf:E11]。因此，速度来自“少做重复维护”，扩展性来自“让 rewrite、analysis 与 extraction 围绕同一 e-class 事实协作”。

## § 5 — 具体方法与完整 Pipeline

以论文 Figure 10 的 lambda calculus partial evaluator 为例，输入测试项包含一个内部函数应用与常量加法，目标结果等价于 `λx.8`。这个例子同时覆盖 rebuilding、constant folding、free-variable analysis、conditional rewrite 与 dynamic rewrite（PDF 物理页 17，Fig. 10）[pdf:E14]

1. **定义语言与 rewrite。** 用户用 `define_language!` 声明算术、条件、函数、binding 与 explicit substitution 等 e-node 形状，再提供 beta、let propagation、常量消除、变量相等性和 capture avoidance 等规则。纯句法 rule 的右侧是 pattern；需要语义判断时，右侧可变成 condition 或实现 `Applier` 的动态程序（PDF 物理页 17，Fig. 10）[pdf:E14]
2. **初始化 e-graph。** 输入 AST 被递归加入 e-graph；每个 e-class 保存若干等价 e-node，边指向 child e-class。rewrite 的结果不会删除原表达式，而是把新表达式加入并与匹配到的 e-class merge（PDF 物理页 4，Fig. 2）[pdf:E03]
3. **只读 search phase。** 一轮开始时 invariant 已成立。Runner 对每条 rewrite 做 e-matching，把 substitution 与目标 e-class 收集到 match 列表，而不立即修改图。这样所有 rule 看到同一个快照，rule list 的排列不会在未饱和时偏袒后面的规则（PDF 物理页 10，Fig. 5 与 Section 3.3）[pdf:E13]
4. **只写 apply phase。** 对收集到的 match 批量构造右侧 e-node，并调用 add/merge。此阶段允许 congruence 与 hashcons 暂时失效，因为不会再进行依赖这些 invariant 的搜索（PDF 物理页 10，Fig. 5）[pdf:E13]
5. **一次 rebuild。** merge 只把受影响的 e-class 放入 worklist。rebuild 分块取出、canonicalize 并去重，再由 repair 更新 parent e-node 的 hashcons；若发现新 congruent parent，就继续 merge 并压回 worklist，直到为空（PDF 物理页 8，Fig. 4）[pdf:E08]
6. **同步维护 e-class analysis。** 在 lambda 例子中，每个 e-class 的数据同时保存常量值与自由变量集合；`make` 从 child e-class 计算新事实，`merge` 做 semilattice join，`modify` 把可求值常量重新加入同一 e-class。capture-avoiding substitution 根据自由变量集合动态选择右侧，常量折叠则把内部应用最终化成常量结果（PDF 物理页 19，Fig. 11）[pdf:E15]
7. **停止与 extraction。** Runner 负责饱和、超时、e-graph 大小限制、rule scheduling 与每轮指标；Extractor 按用户 cost function 从目标 e-class 递归选出最低成本项。默认 backoff scheduler 会暂时抑制 associativity、distributivity 等呈爆炸式匹配的规则（PDF 物理页 18，Section 5.1–5.2）[pdf:E16]

实现层面，egg 约由 5000 行 Rust 代码、测试与文档组成，语言、analysis 与 cost function 都是泛型参数；内部偏向 flat buffer、低间接寻址和编译后的 pattern virtual machine。论文还指出 search 通常占主要运行时间，phase separation 使按 rule 或 e-class 并行搜索成为可能；batch simplification 可把多个相似表达式放进同一初始 e-graph，利用 structural sharing 去重工作（PDF 物理页 16，Section 5；物理页 20，Section 5.3）[pdf:E17][pdf:E05]

这不是 EMT 或 FPGA 实时仿真论文。源 PDF 未报告物理开关/事件模型、时间推进或多速率步长、数值位宽、FPGA 资源与时序闭合；这里的“epoch”是 equality saturation 的算法迭代边界，实际执行对象是 Rust 软件数据结构与程序优化任务（PDF 物理页 16，Section 5；物理页 20，Section 5.3）[pdf:E17][pdf:E05]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化定义与正确性论证，但不是以连续数学推导为主。核心可分为 e-graph invariant、rebuilding 的摊销结构与 e-class analysis invariant。

**第一层：e-graph 为什么需要 invariant。** e-class id 由 union-find canonicalize；congruence invariant 要求 child e-class 等价时，相同 function symbol 的 parent e-node 也必须落在同一 e-class。hashcons invariant 写为

`n ∈ M[a] ⇔ H[canonicalize(n)] = find(a)`，

它保证 lookup 能用 canonical e-node 找到唯一的 e-class。Figure 2 同时展示了 e-class、e-node、边与循环表示（PDF 物理页 4，Definitions 2.4–2.7 与 Fig. 2）[pdf:E03]

**第二层：为什么 deferred rebuilding 能少做工作。** merge 不再递归 upward merge，而只把新 e-class 放入 worklist；repair 负责更新受影响 parent 的 hashcons，并合并新出现的 congruent parent。关键操作是在每一批 repair 前，把 worklist 中的 id 经 `find` canonicalize 后去重，因此不同 merge 共享的 parent path 只需处理一次（PDF 物理页 8，Fig. 4）[pdf:E08]

论文给了两个摊销例子。对 `f₁(x), …, fₙ(x), y₁, …, yₙ` 并依次 merge `x` 与各 `yᵢ` 的工作负载，eager 策略可能产生 `O(n²)` 次 hashcons 更新，deferred rebuilding 不超过 `O(n)` 次（PDF 物理页 8，Section 3.2.1）[pdf:E09]。对宽度 `w`、深度 `d` 的嵌套项族，逐 merge rebuild 需要 `O(wd)` 次 repair，而集中 rebuild 只需 `O(d)` 次，省掉了宽度因子（PDF 物理页 9，Section 3.2.1）[pdf:E10]

**第三层：正确性与终止。** Theorem 3.1 定义尚未合并的 congruent e-node 对集合 `I`，以及待 repair 的 worklist `W`。每次 repair 要么合并至少一对 congruent parent，使 `|I|` 下降；要么没有新 merge，使 `|W|` 下降。因此二元组 `(|I|, |W|)` 按词典序严格下降，最终到达 `(0, 0)`，此时 worklist 为空且 congruence closure 已恢复（PDF 物理页 9，Theorem 3.1）[pdf:E18]。直觉上，这个证明只说明“延迟后仍会修好并停下来”，不直接给出任意在线 workload 的复杂度上界。

**第四层：e-class analysis 如何形式化。** 对每个 e-class `c`，analysis 关联 `d_c ∈ D`，并提供 `make(n)`、`join(d₁,d₂)` 与 `modify(c)`。`D` 与 join 必须构成 join-semilattice，且 invariant 为

`d_c = ⋁_{n∈c} make(n)`，并且 `modify(c) = c`。

前半句表示 e-class 数据汇总其中所有 e-node 的事实；后半句表示 modify 已达到固定点。因为 join 满足结合、交换与幂等，merge 顺序不会改变最终事实（PDF 物理页 13，Section 4.1，analysis invariant）[pdf:E11]。Figure 9 把这套维护嵌入 add、merge 与 repair；论文明确假设 domain 确实是 semilattice 且 modify 幂等，否则 rebuild 可能无法恢复 analysis invariant 或不终止（PDF 物理页 14，Fig. 9 与其后正文）[pdf:E19]

**第五层：analysis 与 extraction 的连接。** 若 local cost function 能从 operator 与 child cost 计算 parent cost，则 analysis data 可保存每个 e-class 的最低成本 e-node。若 `f(c₁,c₂,…)` 是 class `c` 的最佳 e-node，则

`extract(c) = f(extract(c₁), extract(c₂), …)`。

这说明 extraction 本身也可被视为一个固定点 analysis；conditional/dynamic rewrite 还可读取最低成本项或其他 analysis facts 来决定是否、以及如何生成右侧（PDF 物理页 15，Sections 4.2–4.3）[pdf:E12]

## § 7 — 实验设计与结论

**问题一：deferred rebuilding 是否在保持结果一致的同时降低 congruence maintenance 成本？** 作者把 egg 改成每次 merge 后立即 rebuild，与每轮只 rebuild 一次做一对一比较。测试集有 32 个 equality saturation 任务，其中 8 个达到 100 轮上限，其余饱和；两种策略最终 e-graph 完全相同。实验机为 2020 MacBook Pro、2 GHz 四核 Intel Core i5、16 GB 内存（PDF 物理页 12，Section 3.4）[pdf:E20]。答案是：几何平均意义下，congruence closure 加速 88 倍，完整 equality saturation 加速 21 倍；随 applied rewrites 增加，倍数继续上升。repair 调用次数与 congruence time 的 Spearman 相关系数为 0.98，p-value 为 3.6e-47（PDF 物理页 11，Figs. 6–8；物理页 12，结果说明）[pdf:E21][pdf:E20]

**问题二：对只需要等式推理的任务，专用 equality saturation 是否可比通用 SMT 更快？** 作者复现 TASO 的一部分等式验证，把公理作为 rewrites。Z3 为 24.65 秒，egg 为 1.56 秒，batch evaluation 为 0.52 秒，对应报告的 15 倍与 47 倍加速（PDF 物理页 6，Section 2.3）[pdf:E07]。答案只适用于不需要 SMT 完整能力的该类验证任务。

**问题三：egg 是否能改善已有真实系统，而不只是微基准？** Herbie 的 drop-in backend 在约 500 个标准 benchmark、关闭 timeout 的比较中，相对最初 Racket simplifier 超过 3000 倍。Figure 12 报告 simplification 时间从 5022.0 分钟降到 batching 后 49.4 分钟、再到 rebuilding 后 22.4 分钟，直接使用 egg 为 1.4 分钟；其占总运行时间的比例从 98.1% 降至 4.8%，单独 backport rebuilding 又带来 2.2 倍加速（PDF 物理页 21，Section 6.1；物理页 22，Fig. 12）[pdf:E22][pdf:E23]

**问题四：e-class analysis 与 dynamic rewrite 是否能支撑不同领域的语义优化？** Spores 把 linear algebra 转成 relational algebra，用 e-class analysis 保存 schema、保守 cost 与 constant folding；其 prototype 推导出全部 84 条手写规则与 heuristic，并发现带来 1.2 倍到 5 倍端到端加速的新 rewrite，greedy extraction 下编译均在一秒内完成（PDF 物理页 23，Fig. 13 与 Section 6.2.2）[pdf:E24]。这支持“analysis 不只适合常量折叠”的 claim。

**问题五：solver-backed rewrite 与结构发现能否在 CAD 任务中工作？** Szalinski 用 dynamic rewrite 调用 arithmetic solver，把 concrete list 变成 `Tabulate`，并借助 inverse transformation 处理需要重排或重组的列表；Figure 14 给出 mesh → Core Caddy → egg/Solvers & Rewrites → Caddy 的系统路径，Figure 15 给出五个 cube 被重建为重复结构的例子（PDF 物理页 24，Fig. 14；物理页 25，Fig. 15）[pdf:E25][pdf:E26]。作者报告从 OCaml 自建 e-graph 切换到 egg 后约快 1000 倍，并把评测扩展到超过 2000 个真实模型（PDF 物理页 25，Section 6.3.2）[pdf:E26]

**不能外推的范围。** rebuilding 主实验集中在 egg 自身测试集和一台笔记本；没有报告 peak memory、cache miss、能耗、多核 scaling、FPGA 资源或实时 deadline。三个 case study 同时更换了实现语言、数据结构、batching、scheduler 与 extensibility 机制，因此除 Herbie 的分阶段图外，不能把全部端到端收益严格归因于 rebuilding。论文也明确没有给出 online setting 的 rebuilding 理论分析，并承认性能高度 workload-dependent（PDF 物理页 26，Related Work）[pdf:E06]

## § 8 — Take-aways

**5 句话。**

1. equality saturation 的真正瓶颈不只在 rewrite 数量，也在 e-graph 是否按该工作负载维护 invariant（PDF 物理页 2，贡献概述）[pdf:E02]。
2. rebuilding 把每次 merge 的即时修复改为每轮边界上的集中修复，并靠 worklist 去重获得摊销收益（PDF 物理页 8–10，Figs. 4–5）[pdf:E08][pdf:E13]。
3. e-class analysis 用 semilattice facts 把常量、自由变量、schema 与 cost 等 interpreted reasoning 纳入统一接口（PDF 物理页 13–15，Section 4）[pdf:E11][pdf:E12]。
4. egg 的贡献不仅是算法，也是一套把 language、rewrite、analysis、scheduler 与 extractor 组合起来的 reusable library（PDF 物理页 16–20，Section 5）[pdf:E17][pdf:E16][pdf:E05]。
5. 实验说明它在作者测试集和三个既有系统中都能产生显著收益，但收益大小仍取决于 match 结构、批处理机会和领域分析是否适合该抽象（PDF 物理页 11–12 与 21–25）[pdf:E21][pdf:E20][pdf:E23][pdf:E24][pdf:E26]。

**3 句话。**

1. 这篇论文把 e-graph 从“必须始终一致的在线数据结构”重新解释成“可在安全边界集中恢复一致性的迭代数据结构”（PDF 物理页 10，Fig. 5）[pdf:E13]。
2. 它同时把领域语义从项目内 hack 提升为 e-class 上的单调 analysis，使 rewrite 与 extraction 能共享事实（PDF 物理页 13–15，Section 4）[pdf:E11][pdf:E12]。
3. 最强证据是相同最终 e-graph 下的 rebuilding 对照和多领域 case study，最弱处是对非单调 analysis 与 adversarial match explosion 的覆盖不足（PDF 物理页 12、14、26）[pdf:E20][pdf:E19][pdf:E06]。

**1 句话。** egg 的核心不是“更快地执行旧 e-graph”，而是利用 equality saturation 的单调、分阶段结构重新定义 invariant maintenance 与语义扩展的边界（PDF 物理页 2、10、13）[pdf:E02][pdf:E13][pdf:E11]。

## § 9 — 最脆弱的假设

最脆弱的假设是：**需要带入 e-graph 的领域语义，能够被压缩成每个 e-class 一个单调增长的 join-semilattice 值，而且 `modify` 在没有新外部变化时是幂等的。** 论文明确把这两点作为实现前提；若不满足，egg 可能无法恢复 analysis invariant，甚至无法终止（PDF 物理页 14，Fig. 9 后正文）[pdf:E19]

这个假设容易在三类实际 analysis 中失效。其一，context-sensitive 或 path-sensitive facts 可能需要保留“哪个表达式导致哪个事实”的相关性，把它们 join 到一个值会过度近似；其二，某些优化事实会随全局资源、候选选择或 solver 反馈被撤销，不是单调信息；其三，`modify` 自己会加入 e-node，新增 e-node 又可能改变 analysis data，若设计不慎就会形成振荡而非固定点。论文中的 constant、free-variable、schema 与 conservative cost 都能自然做 join，但这些成功例子并未覆盖非单调或强相关性的 analysis（PDF 物理页 19，Fig. 11；物理页 23，Spores analysis）[pdf:E15][pdf:E24]

论文还承认 e-graph 没有内建 binding 支持，示例的 explicit substitution 成本较高；这说明“把事实挂到 e-class”并不会自动解决所有语义表示问题（PDF 物理页 16，footnote 7 与 Section 5）[pdf:E17]。如果该假设不成立，rebuilding 的 congruence 部分仍可能有效，但“e-class analysis 是通用 interpreted reasoning 机制”这一核心贡献会显著收缩为只适合单调、可 join、固定点稳定的 analysis。论文提供了实现警告和若干正例，却没有给出可表达性边界或失败基准。

## § 10 — 最小复现实验

一周内最值得复现的是 rebuilding 的核心 claim：**在最终 congruence closure 相同的前提下，延迟并去重 repair 能把重复维护从依赖宽度的工作量变成主要依赖深度的工作量。** 论文已经给出合成项族与预期量级：hashcons 例子从 `O(n²)` 到 `O(n)`，嵌套项族从 `O(wd)` 次 repair 到 `O(d)` 次（PDF 物理页 8–9，Section 3.2.1）[pdf:E09][pdf:E10]

最小方案如下：

- **数据。** 程序化生成论文中的嵌套项族：许多项共享相同的 function-symbol 链，但底部是不同 `xᵢ`；逐步增加宽度与深度。
- **实现。** 按 Figure 4 写一个只支持 add、merge、find、parent list、hashcons、repair 与 rebuild 的小型 e-graph；同一份代码提供“每次 merge 后 rebuild”和“全部 merge 后 rebuild”两种策略（PDF 物理页 8，Fig. 4）[pdf:E08]。
- **测量。** 记录 repair 调用数、hashcons 更新数、wall-clock time、峰值 worklist，以及 rebuild 后每个 e-node 的 canonical e-class。
- **支持条件。** 两种策略的最终 partition 与 lookup 结果完全一致；随着宽度增加，eager 策略的 repair 调用按宽度增长，而 deferred 策略基本由深度决定，速度比随问题增大而上升。
- **反驳条件。** 最终 partition 不一致，说明实现或算法破坏 soundness；若 repair 次数没有出现论文预测的量级差异，或者 deferred 策略的 match/内存开销抵消并反转收益，则该核心性能解释在该实现上不成立。

这个复现不需要完整 Runner、lambda calculus 或三个 case study，却能同时检查正确性、摊销机制和 Figure 7 所声称的“问题越大，speedup 越大”趋势（PDF 物理页 11，Fig. 7）[pdf:E21]

## § 11 — 最强反例设计

最强攻击不是找一个“小图上没有加速”的普通负例，而是构造 **snapshot match explosion**：在一轮只读阶段，许多尚未 merge 的 e-class 让高 arity rewrite 产生大量组合 match；写阶段早期的若干 merge 本会把这些 class 合并成少数 canonical class，但因为所有 match 已在旧快照上物化，后续仍要保存和应用大批最终重复的 match。Figure 5 明确显示 egg 先收集整个 match 列表，再进入写阶段；论文又指出 e-matching search 通常是运行时间主体（PDF 物理页 10，Fig. 5；物理页 20，Section 5.3）[pdf:E13][pdf:E05]

具体做法是让第一组规则快速证明许多 child e-class 等价，同时让另一组 expansive rule 在这些 child 上形成高组合度匹配。比较三种执行：立即 rebuild 且后续 rule 看到 canonicalized graph、egg 的 snapshot read/write、以及仅对 match 结果做 canonical dedup 的增强版本。记录 match 数量、match-list 内存、write 次数、rebuild 时间、总时间和最终 e-graph。

若 snapshot 版本保持正确但总时间与内存显著劣于立即维护，而 match dedup 版本恢复性能，就给出一个具体替代解释：论文观察到的加速来自 congruence repair 占主导的 workload；当 match materialization 占主导时，phase separation 可能把 invariant maintenance 的节省换成更大的 stale-match 开销。这不会推翻 rebuilding 的 soundness theorem，却会直接限制“对 equality saturation 普遍更快”的工程外推。

## § 12 — Follow-up Research Bet

**候选判断：以下方向只依据本 PDF，未做外部相关工作检索，因此不声称 novelty。**

**主押注：快照—增量日志 e-graph，把 phase separation 升级为异构并行执行模型。** 新的研究问题是：能否不再把 read/write split 只当作“少调用 rebuild”的局部优化，而把每轮 e-graph 表示成不可变 snapshot，加上由多个 worker 产生的 append-only add/merge/analysis delta log，再由确定性的 reducer 完成 canonicalization、semilattice join 与 rebuild？这将首次使一个共享 e-graph 在不做细粒度锁同步的情况下，同时服务大批相似输入和大规模并行 e-matching，并把 CPU、GPU 或 FPGA 视为同一 epoch 数据流中的不同执行单元。

核心因果链是：只读阶段 invariant 固定，所以 snapshot 可安全复制或分片；worker 只输出 match 与变更日志，不竞争可变 union-find；轮末把 merge proposal 汇总，worklist 去重消除重叠 repair；e-class analysis 的 join 顺序无关，适合作为并行 reduce；batch simplification 再把跨输入的公共子表达式变成共享状态。论文已经给出这条链的关键部件：Figure 5 的 read/write epoch、analysis 的 join-semilattice invariant、search 可按 rule 或 e-class 并行，以及相似表达式批处理的 structural dedup（PDF 物理页 10，Fig. 5；物理页 13，Section 4.1；物理页 20，Section 5.3）[pdf:E13][pdf:E11][pdf:E05]

它改变的基本设计变量至少包括：从原地可变 e-graph 改为 snapshot 与 delta 的时间表示；从单表达式 latency 改为 workload-level throughput；从单机共享内存算法改为可映射到异构计算与通信层次的系统边界。论文特异的实验依据是 Herbie 中 batching 把 simplification 时间从 5022.0 分钟降到 49.4 分钟，说明跨相似输入共享工作可能比单次优化更有价值；但 rebuilding 后继续下降、直接 egg 仍更快，也说明日志 reduce 与内存布局必须共同设计（PDF 物理页 22，Fig. 12）[pdf:E23]

最大的研究收益，是把 equality saturation 从“单个优化任务的数据结构”变成可持续接收任务流的并行等价推理 substrate，并让 pattern VM、function-symbol index 与批量 semilattice reduce 获得明确的硬件接口。最大的科学风险是日志量和 stale match 数量可能远大于被去重的 repair，union-find 与 parent traversal 的不规则访问也可能让 accelerator 空转；这正与第 11 节的反例形成可证伪张力。

首个区分实验应比较：并行 search 加细粒度同步写、并行 search 加 snapshot/delta、以及单线程 egg 风格执行。必须同时测 match-log 体积、重复 merge 比例、rebuild 工作量、memory traffic 与端到端 throughput；再用“关闭跨输入共享”和“保留共享但改回原地写”两项消融，区分收益究竟来自普通并行、batch structural sharing，还是 snapshot/delta 机制本身。与 PDF 中最近的工作相比，传统 theorem-prover e-graph 面向交错查询与 backtracking，egg 只提出在单机算法中延迟维护并指出 search 可以并行；本押注把 epoch、状态表示、通信对象与评价目标同时改变，而不是给原库外包一层并行 wrapper（PDF 物理页 26，Related Work）[pdf:E06]

**Wild-card alternative：** 为 Spores 一类 associative/commutative relational algebra 构造原生 schema-typed hyper-e-graph，让 `⊕`、`⊗` 与 aggregate 直接成为无序多元 hyperedge，并把 extraction 对象改成可融合的 sparse-kernel plan，从表示层避免枚举大量二叉结合树；其机制与 snapshot/delta 完全不同，依据是 Figure 13 的 n-ary RA equality 与 schema-dependent rule（PDF 物理页 23，Fig. 13）[pdf:E24]。
