# Fast and Optimal Extraction for Sparse Equality Graphs

- 作者：Amir Kafshdar Goharshady、Chun Kit Lam、Lionel Parreaux
- 出处：Proceedings of the ACM on Programming Languages, Vol. 8, OOPSLA2, Article 361
- 年份：2024
- DOI：10.1145/3689801
- Zotero key：NBCEH6H6
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文处理的是 equality saturation 的最后一步：一个 e-graph 通过大量局部 rewrite 累积了许多彼此等价的表达式以后，怎样从中选出总成本最低、依赖闭合的一组 e-node，得到真正要编译或执行的 term。这个阶段叫 extraction。它不是在图里找一条最短路径，因为不同候选表达式可能共享子项；选中一个 e-node 还会强制选中它的全部 child e-class，而每个被选中的 e-class 又至少要选一个成员 e-node。局部便宜的选择可能破坏全局共享，因此目标是一个带闭包约束的组合优化问题。[pdf:E02]（PDF 物理页 4，Fig. 1 与 Example 1）[pdf:E03]（PDF 物理页 5，Valid Extractions 与 Monotone Cost Functions）

这件事重要有两个直接原因。第一，saturation 阶段探索到的优化机会，只有 extraction 真正选出来才会变成输出程序；如果最后用一个无最优保证的 heuristic，前面花成本构建的大型等价空间可能仍被糟糕地落地。第二，一般 e-graph 的 Optimal Extraction 不只是 NP-hard；作者进一步证明，除非 P=NP，不存在对任意实例保证任意固定常数近似比的多项式算法。因此，不能期待某个通用快速 heuristic 在所有输入上都“离最优不太远”。现有选择于是落在两个不舒服的端点：ILP 能给最优解但可能慢，heuristic 快但最坏情况可任意差。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E05]（PDF 物理页 9，Section 3 与 Fig. 4）

论文改变问题的方式不是再发明一个更好的通用 heuristic，而是问：实际 e-graph 是否具有可利用的结构参数？作者把 treewidth/pathwidth 当作实例难度。若 e-graph 能被切成由小 bag 连接而成的树或路径，那么 bag 就是连接已处理区域与未处理区域的小边界；全局最优提取可由这些边界上的有限状态拼起来。对固定宽度 $k$，算法对图规模 $n$ 呈线性 FPT（fixed-parameter tractable）时间，而实验中的 Cranelift e-graph 大多确实落在低 treewidth 区域。[pdf:E04]（PDF 物理页 7，Tree Decompositions、Treewidth 与 Pathwidth）[pdf:E09]（PDF 物理页 17，Theorems 4.1–4.2）[pdf:E11]（PDF 物理页 19，Tables 1–4）

这不是 EMT 或 FPGA 论文。它报告的是 Rust/CPU 实现和编译器 benchmark；没有电磁暂态模型、离散积分、开关事件、实时步长、定点位宽、FPGA 资源或板级时序。本文对 ResearchStudio 的价值只在“稀疏依赖结构如何把全局最优组合问题变成小边界动态规划”这一算法思想，不能把其实验直接外推成 FPGA 可实现性或实时仿真性能。

## § 2 — 前人工作与不足

论文把已有路线分成四类。

第一类是 equality saturation 系统中的 greedy 或其他 heuristic extraction。它们快，但不保证共享子表达式下的全局最优；论文的 Set Cover 归约又说明不存在一个通用多项式 heuristic 能对所有输入保证固定常数近似比。因此，“工程上通常够好”与“有可证明质量界”是两件事。

第二类是 ILP-based optimal extraction。它能编码选择变量与依赖约束并返回最优解，是作者实验中唯一直接可比的既有最优路线；不足是把结构信息交给通用求解器后，在大量 extraction call 上付出较高开销。作者分别用开源 CBC 和商业 Gurobi 作为基线，而不是只挑一个弱 solver。[pdf:E10]（PDF 物理页 18，Implementation、Machine 与 baselines）

第三类是 ZDD（Zero-Suppressed Binary Decision Diagram）或 MAX-SAT 等表示。Rosenthal 的 ZDD 可以紧凑表示候选 extraction，但构造本身最坏可指数；牺牲最优性可换速度。He 等人针对 acyclic extraction 中 ILP 不擅长的拓扑排序约束，显式识别 cycle 并转成 Weighted Partial MAX-SAT。它们解决的是候选集合表示或无环约束求解，并没有利用 e-graph 的 treewidth 来给出本文这种低宽度 FPT 算法。[pdf:E15]（PDF 物理页 23，Section 6 Further Related Works）

第四类是与本文几乎同时出现的 Sun、Zhang、Ni 2024：其也对 treewidth 参数化，通过把 e-graph reduction 成 cyclic monotone Boolean circuit，再调用已有 FPT 算法，并提出降低 e-graph treewidth 的办法。论文明确说这是 independently devised。因此，本文不能被准确概括为“唯一发现 treewidth 能做 optimal extraction”；更精确的贡献是直接构造了以 e-class/e-node 局部合法性为状态语义的 tree/path-decomposition DP，并给出高性能 Rust 实现与 Cranelift 大规模测量。[pdf:E15]（PDF 物理页 23，Section 6）

前人工作真正缺的不是“没有任何最优方法”，而是没有把实际实例的结构稀疏性转化为一条同时满足三点的路线：最优性不降级、复杂度对 $n$ 线性、在真实 compiler e-graph 上明显快过通用 ILP。本文正是针对这三个缺口。

## § 3 — 重建作者的思考路径

不使用本文贡献作前提，可以从以下已知线索走到这个 idea。

首先，Optimal Extraction 的困难来自共享和闭包，而不是单个 operator 的 cost。一般实例 NP-hard，继续寻找“所有图都快”的精确算法不现实。Set Cover 还暗示 approximation 也不能提供稳定兜底：选择一个集合能同时满足多个元素，正对应选择一个共享 e-node/subterm 能同时服务多个依赖。[pdf:E05]（PDF 物理页 9，Set Cover reduction）[pdf:E06]（PDF 物理页 10，Correctness 与 Section 4 起始）

其次，在 graph algorithms 中，许多一般 NP-hard 问题在低 treewidth 上可解。tree decomposition 的关键不只是“图看起来像树”，而是每个 bag 同时覆盖边，并且一个 vertex 出现的 bags 构成连通子树。于是 bag 是 separator：处理 bag 下方子图时，外界只可能通过 bag 中至多 $k+1$ 个 vertex 与它交互。[pdf:E04]（PDF 物理页 7，tree decomposition 定义与 cut property 的前置定义）

第三，把 extraction 的两条合法性约束放到 separator 上审视：被选中的 e-node 必须带上所有 child e-class；被选中的 e-class 必须在某处选中至少一个 member e-node。第一条可在边的两个端点共同出现的 bag 中局部检查；第二条不能只靠“当前是否已满足”一个 bit，因为满足者可能在 separator 的另一侧。因此需要记住哪些边界 e-class 已经被外部/另一子树豁免。这个思路自然导向两个集合：$M$ 表示当前 bag 中哪些 vertex 进入 partial extraction，$S\subseteq M\cap C$ 表示当前子图里暂时不用证明已有 successor 的 e-class。[pdf:E07]（PDF 物理页 11，Dynamic Programming Subproblems）

最后，把任意 decomposition 标准化成 nice decomposition，只需处理 leaf、introduce、forget、join 四类 bag。每种图结构变化只涉及一个 vertex，或合并两个共享同一边界的子树；于是可以写出有限个局部 recurrence。这个路径没有假定新 solver，也没有把最优性换成 heuristic，而是把“全图指数”收缩成“边界宽度指数”。[pdf:E06]（PDF 物理页 10，Nice Decompositions）[pdf:E08]（PDF 物理页 13，Pseudocode 2）

## § 4 — 核心 Intuition

低 treewidth e-graph 可以被很多小 separator 切开。处理一个 separator 下方的子图时，不必记住内部选了什么，只需记住边界中哪些 vertex 被选，以及哪些边界 e-class 的 member 义务要留给另一侧满足。对每个 bag 穷举这个小接口的有限状态并自底向上合并，就能得到全局最优 extraction；指数成本落在宽度 $k$ 上，而不是图规模 $n$ 上。

最关键的不是“在树上跑 DP”这句泛话，而是作者找到了足够且接近最小的接口状态 $(M,S)$：$M$ 传递选择，$S$ 传递尚未在当前子图内闭合的 e-class 义务。没有 $S$，两棵子树在 join 时无法判断一个 e-class 是否已经由另一侧选中的 member 满足；保留整个 partial solution 又会失去低宽度带来的压缩。[pdf:E07]（PDF 物理页 11，$\mathrm{Ans}[b,M,S]$ 语义）

## § 5 — 具体方法与完整 Pipeline

以论文的 $(a\times2)/2$ e-graph 为小例子：同一个 e-class 中可选乘法或左移，左移路径还要带上常数 1。给定 target e-class 和每个 vertex 的 cost，目标是选择闭合的 vertex 集；在论文给定 cost 下，左移构成的 valid extraction 更便宜，因此最优输出是 $(a\ll1)/2$。[pdf:E02]（PDF 物理页 4，Fig. 1 与 Example 1）[pdf:E03]（PDF 物理页 5，formal extraction/cost definition）

完整 pipeline 如下。

1. **形式化输入。** 把 e-graph 写成有向二部图 $G=(C,N,E)$：e-class 到其 member e-node 有边，e-node 到其 child e-class 有边。输入还包括必须选择的 target 集 $\tau$、monotone cost oracle，以及底层无向图的一棵 tree/path decomposition。
2. **得到 nice decomposition。** 将 decomposition 线性时间转换成空 root、空 leaf，以及 introduce/forget/join bag 构成的 rooted tree。作者把最优 decomposition 当作算法输入；理论上低 $k$ 时可以 FPT 地求得，工程实现则用 htd 库计算。[pdf:E06]（PDF 物理页 10，Nice Decompositions）[pdf:E10]（PDF 物理页 18，Implementation）
3. **定义边界状态。** 对每个 bag $b$、$M\subseteq V_b$、$S\subseteq M\cap C$，计算 $\mathrm{Ans}[b,M,S]$。它是在子图 $G_b$ 内、与当前 bag 的交集恰为 $M$ 的最小成本 partial solution；所有已选 e-node 的当前子图 successor 必须被选，而所有已选且不在 $S$ 的 e-class 必须在当前子图找到至少一个已选 successor。[pdf:E07]（PDF 物理页 11，DP subproblem definition）
4. **先做局部 sanity checks。** 若 $M$ 选了 e-node $u$ 却漏掉 bag 内 successor $v$，该状态为 $+\infty$；若 bag 中出现 target 却不在 $M$，也为 $+\infty$。[pdf:E08]（PDF 物理页 13，Pseudocode 2 lines 2–7）
5. **按 bag 类型转移。** leaf 返回 $\mathrm{Cost}(\varnothing)$；introduce 决定新 vertex 是否进入 $M$，并在引入 e-node 时把它满足的 predecessor e-class 加入 child 的 exemption；forget 在“child 选 $u$ / 不选 $u$”之间取最小；join 合并两棵子树，要求两个 child exemption 集 $S_1,S_2$ 的交集正好是 parent 的 $S$，并减去重复计算的 $\mathrm{Cost}(M)$。[pdf:E08]（PDF 物理页 13，Pseudocode 2 lines 8–23）
6. **读出全局解。** root bag 为空，所以 $\mathrm{Ans}[r,\varnothing,\varnothing]$ 已没有向外欠下的义务，等于全局 Optimal Extraction 的 cost。保存每次取 min 的 argmin，反向追踪即可恢复 vertex 集，而不只是 cost。[pdf:E09]（PDF 物理页 17，Final Solution 与 Theorems 4.1–4.2）
7. **工程化。** Rust 实现把 nice decomposition 按 preorder flatten 成 enum 列表，从尾到头迭代，避免递归；利用 treewidth-$k$ 图的 $(k+1)$ coloring，把 bag subset 编成 32-bit bitset（实现假设 treewidth 不超过 31）；partial solution 用共享节点 linked list 与 reference counting，使 union/添加元素保持常数时间。实际平台是 14-core/20-thread Intel Core i9-12900HK、32 GB RAM、NixOS；论文没有报告 GPU、FPGA 或分布式执行。[pdf:E10]（PDF 物理页 18，Machine 与 Optimizations）[pdf:E11]（PDF 物理页 19，优化列表的最后一项）

论文没有 appendix；正文后只有 Data Availability、致谢与参考文献。代码与实验数据 artifact 的 DOI 是 `10.5281/zenodo.13624896`。[pdf:E16]（PDF 物理页 24，Data Availability Statement）

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 合法 extraction 与成本

令 $X\subseteq C\cup N$ 是被选 vertex 集。它合法当且仅当：

$$
\forall c\in X\cap C,\ \exists \nu\in X\cap N:(c,\nu)\in E,
$$

$$
\forall \nu\in X\cap N,\ \forall c\in C:\ (\nu,c)\in E\Rightarrow c\in X.
$$

第一式说每个选中的等价类必须落实成至少一个 member；第二式说选一个算子就必须把其全部输入依赖带上。target constraint 是 $\tau\subseteq X$，目标是最小化 $\mathrm{Cost}(X)$。论文形式上允许 monotone cost：给两个集合加同一个新 vertex 不会颠倒原有成本顺序；为便于展示 recurrence，正文主要按 additive cost 写。[pdf:E03]（PDF 物理页 5，Valid Extractions、Monotone Cost Functions、Optimal Extractions）

### 6.2 为什么一般情形不可近似

给 Set Cover 实例 $U=\{1,\ldots,n\}$、$\mathcal S=\{S_1,\ldots,S_m\}$，作者为每个集合建一个 cost 为 1 的 e-node $S_i$；为每个 universe element $j$ 建 e-class $c_j$，其中每个候选 member $v_{i,j}$ 都依赖相应的 $S_i$；root e-node 又依赖所有 $c_j$。任何包含 root target 的 extraction 都必须为每个 $c_j$ 选一个 $v_{i,j}$，于是被迫选择覆盖 $j$ 的某个 $S_i$。反过来，一个 set cover 也直接构造出同成本 extraction。因此最优成本保持，Set Cover 的 $c\ln n$ inapproximability 被带到 extraction；特别地，不存在任何固定常数近似比，除非 P=NP。[pdf:E05]（PDF 物理页 9，Fig. 4 与 reduction construction）[pdf:E06]（PDF 物理页 10，Correctness）

### 6.3 DP 状态为何足够

对 bag $b$ 的子图 $G_b$，状态写作

$$
\mathrm{Ans}[b,M,S]=\min \mathrm{Cost}(A),
$$

其中 $A\cap V_b=M$，$A$ 在 $G_b$ 内满足所有 e-node successor 约束，且 $A\setminus S$ 中每个 e-class 已在 $G_b$ 内找到 member。$S$ 是 exception set：这些边界 e-class 的满足证据允许在 bag 外/另一子树出现。tree decomposition 的 connectedness 和 edge coverage 保证，子图内部对外的全部影响都经过 $V_b$；所以 $(M,S)$ 足以概括内部，无需记住 $A$ 的全部结构。[pdf:E07]（PDF 物理页 11，Ans definition 与解释）

四类 recurrence 中最有信息量的是 join：

$$
\mathrm{Ans}[b,M,S]
=\min_{S_1\cap S_2=S}
\left(\mathrm{Ans}[c_1,M,S_1]+\mathrm{Ans}[c_2,M,S_2]-\mathrm{Cost}(M)\right).
$$

减去 $\mathrm{Cost}(M)$ 是因为 separator vertex 在两个 child 都算了一次。条件 $S_1\cap S_2=S$ 的直觉是：一个 parent 中仍被豁免的 e-class，必须在两个 child 中都没有完成；只要任一 child 完成，它就不该继续出现在 parent exemption 中。[pdf:E08]（PDF 物理页 13，Pseudocode 2 line 23）

### 6.4 复杂度

path decomposition 没有 join。每个 bag vertex 对 $(M,S)$ 有三种身份：不在 $M$、在 $M$ 但不在 $S$、同时在 $M$ 与 $S$，所以每个 bag 至多指数级 $3^{k+1}$ 个状态；每个状态的 sanity check 至多 $O(k^2)$。作者给出的总时间是

$$
O(n\cdot 3^k\cdot k^2).
$$

tree decomposition 的 join 要同时枚举 $M,S,S_1,S_2$。满足包含关系与 $S_1\cap S_2=S$ 时，每个 bag vertex 有五种身份，得到

$$
O(n\cdot 5^k\cdot k).
$$

当 $k$ 为常数，两式对 $n$ 都是线性时间。这是 parameterized guarantee，不是说对任意 treewidth 的图都近似线性；$3^k/5^k$ 会迅速增长。[pdf:E09]（PDF 物理页 17，Theorems 4.1–4.2）[pdf:E10]（PDF 物理页 18，Corollary 4.3）

## § 7 — 实验设计与结论

### 问题一：真实 compiler e-graph 是否足够稀疏？

**实验。** 作者修改 Cranelift，在 sightglass WebAssembly benchmarks 的 function data-flow graphs 上记录每次 extraction call，并用 htd 计算 tree/path decomposition。Table 1 共列出 281,459 个 graph/extraction instances；Table 2–4 按 size、treewidth、pathwidth 分桶。[pdf:E10]（PDF 物理页 18，Cranelift 与 Benchmarks）[pdf:E11]（PDF 物理页 19，Tables 1–4）

**答案。** 按 Table 2，treewidth $\le10$ 的实例为 280,924/281,459，约 99.81%。正文另称，超过 100 vertices 的实例中“almost 94%”的 treewidth 不超过 10；但 Table 3 各桶合计为 8,704，与 Table 1 的 `>100 vertices` 总数 8,245 不一致，因此不能从两表可靠复算更精确比例。按 Table 4，pathwidth $\le10$ 为 196,682/281,459，约 69.88%，另有约 30.12% 落在 `>10` 或 htd 未成功产生 decomposition 的合并桶。因此 treewidth variant 覆盖更广，pathwidth variant 覆盖约七成。[pdf:E11]（PDF 物理页 19，Tables 1–4 与 Statistics）

这里有一处必须保留的论文内在不一致：物理页 19 的 Statistics 说“about 30% ... pathwidth more than 10”，与 Table 4 一致；物理页 22 的 Discussion 却写“only about 23% ... pathwidth at most 10”，与同表无法同时成立。本卡采用可复算的 Table 4 数字，不把 23% 当作已核实结论。[pdf:E11]（PDF 物理页 19，Table 4 与 Statistics）[pdf:E14]（PDF 物理页 22，Discussion）

### 问题二：在适用的低宽度实例上，是否比 ILP 快？

**实验。** 比较 treewidth/pathwidth DP 与 CBC ILP；treewidth 另与 Gurobi 比较。图中每个点是一条 Cranelift extraction call，横纵轴为微秒且均取对数。作者同时报告端到端时间（含 htd decomposition）和只算 DP 的时间，从而把 structural preprocessing 与核心求解分开。[pdf:E12]（PDF 物理页 20，Fig. 14）[pdf:E13]（PDF 物理页 21，Figs. 15–16）

**答案。** treewidth route 含 decomposition 时胜 CBC 的实例占 95.9%，80.2% 至少快 2 倍；只算 DP 时胜 99.9%，97% 至少快 10 倍。含 decomposition 时胜 Gurobi 92.8%，去掉 decomposition 则胜 99.3%。pathwidth route 在适用实例上全部胜 CBC；含 decomposition 时 99.8% 至少快 2 倍，只算 DP 时 88.7% 至少快 10 倍。作者同时指出端到端时间主要由 htd 主导，因此“DP 极快”与“获得 decomposition 也同样快”不能混为一谈。[pdf:E12]（PDF 物理页 20，Fig. 14 相邻正文）[pdf:E13]（PDF 物理页 21，Figs. 15–16；相关数字在物理页 20 相邻正文）

### 问题三：treewidth 与 pathwidth variant 谁更实用？

**实验。** 在两者都适用、即 pathwidth $\le10$ 的实例上直接比较，仍分别给出含/不含 decomposition 的时间。[pdf:E14]（PDF 物理页 22，Fig. 17）

**答案。** 含 decomposition 时 pathwidth route 通常更快；只看 DP 时 treewidth route 反而常更快。原因不是理论 bound 失效，而是同一图的 pathwidth 往往显著大于 treewidth，指数参数差异盖过 $3^k$ 与 $5^k$ 形式上的优势；同时 htd 求 tree decomposition 比求 path decomposition 更慢。实际选择取决于“宽度大小 × decomposition 成本”，不能只看渐近式。

### 问题四：全局最优 extraction 是否直接减小最终 code size？

**实验。** 在 108 个程序上，用 Cranelift `-Osize`、每条 instruction cost 为 1，比较接入 optimal extraction 后的 code size。[pdf:E14]（PDF 物理页 22，Code Size Improvement）[pdf:E15]（PDF 物理页 23，Fig. 18）

**答案。** 大多数程序不变；排除不变项后，论文报告平均 size reduction 约 `-2.4%`，但有两个程序反而增大。作者给出的原因是 Cranelift 并不请求一个 overall global optimum，而是组合许多 locally optimal solutions；这种系统级组合忽略 node sharing，局部最优 solver 不能修复上层目标分解。这个结果非常重要：本文证明并加速的是单次 formal extraction problem 的最优性，不等价于整个 compiler pipeline 的全局代码最优。

### 不得外推的范围

实验只覆盖 Cranelift/sightglass 与 tree/pathwidth $\le10$ 的主要比较区间；`>10` 桶还混入 htd 未能产生 decomposition 的实例，不能据此区分“真实宽度大”和“工具失败”。Egg 常需要 acyclic extraction，本文算法未直接覆盖；扩展为追踪 bag 内局部 reachability 会把 bound 推高到论文所写的 $O(c^{k^2}\cdot k\cdot n)$，作者认为即便小 treewidth 也不实用，而且 extraction-gym benchmarks 往往 treewidth 大。[pdf:E14]（PDF 物理页 22，Usage with Egg）此外，论文没有报告能耗、内存峰值、编译总时延占比、硬件实现或实时 deadline。

## § 8 — Take-aways

### 5 句话

1. 一般 e-graph Optimal Extraction 不仅 NP-hard，而且除非 P=NP，无法在多项式时间内保证任何固定常数近似比。
2. 低 treewidth/pathwidth 把全局依赖图变成由小 separator 连接的结构，使 $(M,S)$ 边界状态足以做精确 DP。
3. 算法对 path decomposition 是 $O(n3^k k^2)$，对 tree decomposition 是 $O(n5^k k)$，所以固定 $k$ 时对图规模线性。[pdf:E09]
4. Cranelift 数据中约 99.81% 的实例 treewidth 不超过 10，适用实例上的端到端实现通常明显快过 CBC/Gurobi ILP。[pdf:E11][pdf:E12][pdf:E13]
5. 这不意味着所有 e-graph、acyclic Egg extraction 或整个 compiler pipeline 都被解决：decomposition 成本、宽度爆炸和上层局部目标分解仍是硬边界。[pdf:E14]

### 3 句话

论文的实质是把 extraction 的全局组合爆炸压缩到 tree-decomposition separator 上的有限接口状态。它在低宽度 Cranelift e-graph 上同时保住最优性和速度，并用大规模测量说明“低宽度”不是纯理论假设。最危险的误读是把“固定宽度线性、单次 extraction 最优”说成“任意 e-graph 都快、最终程序全局最优”。

### 1 句话

当 e-graph 的复杂依赖只通过小边界相连时，可以对边界穷举而不对整张图穷举，从而快速得到严格最优 extraction。

## § 9 — 最脆弱的假设

失败代价最大的假设是：目标 workload 的 **有效 treewidth 足够小，而且 decomposition 能以可接受成本得到**。这不是一般“benchmark 代表性”问题，而是算法复杂度的指数参数本身；若 $k$ 从 10 增长到 20，$5^k$ 状态因子理论上增加约 $5^{10}$ 倍，$n$ 再小也救不了。若 decomposition 工具无法及时产出，端到端优势也会消失，因为实验已显示总时间主要由 htd 主导。[pdf:E09]（PDF 物理页 17，treewidth runtime）[pdf:E12]（PDF 物理页 20，端到端与 DP-only 对比）

论文给出的支持证据相当强但范围有限：281,459 个 Cranelift extraction instances 中约 99.81% 落在 treewidth $\le10$，正文还称超过 100 vertices 的实例中“almost 94%”落在该范围，但其 Table 1 与 Table 3 的总数矛盾使后一比例无法独立复算。[pdf:E11] 它还缺少三个关键压力测试：没有展示 width 超过 10 后 runtime/memory 如何实际崩溃；`>10` 与 htd failure 被合并，无法知道失败来自结构还是工具；Egg extraction-gym 则被作者直接报告为常有大 treewidth，说明该假设跨系统并不稳定。[pdf:E14]

因此，本文最可信的结论是“对 Cranelift 这类实测稀疏 e-graph，方法有效”，而不是“e-graph 在实践中普遍低 treewidth”。此外，Table 4 与 Discussion 的 70%/23% pathwidth 覆盖冲突降低了 pathwidth 适用性陈述的可信度，但它不是核心 treewidth 结论的直接反证。[pdf:E11][pdf:E14]

## § 10 — 最小复现实验

一周内最值得复现的不是整个 Cranelift compiler，而是“低 treewidth DP 是否在包含 preprocessing 的真实时间上仍胜 ILP”这个核心 claim。

**数据。** 从作者公开 artifact 中选择约 300 个 extraction instances，按 treewidth 分成 $k=2$、$4$、$6$、$8$、$10$ 五档；每档同时包含 50–100 vertices 与超过 100 vertices 的图。若 artifact 提供的原始分桶不足，按 graph size 与 htd 返回宽度分层抽样，但不修改 graph。artifact 与实验数据的位置由论文 Data Availability 给出。[pdf:E16]

**实现。** 编译论文 Rust DP 与 CBC ILP baseline。对每个实例固定 target、cost 和随机种子，分别记录：(1) decomposition 时间；(2) DP-only 时间；(3) ILP solve 时间；(4) end-to-end 时间；(5) peak memory；(6) 输出 extraction cost。用一个独立 checker 验证两边输出满足 e-node/e-class closure，并要求 cost 完全相同，而不是只比较 runtime。

**测量。** 每个实例预热后重复 20 次取中位数；画出 speedup 随 $k$ 和 $n$ 的二维分布，并单独统计 htd failure。最关键的是把 end-to-end 与 DP-only 分开，这直接复现 Fig. 14 的两种口径。[pdf:E12]

**支持标准。** 在 $k\le10$ 的抽样中，全部可解实例与 ILP cost 一致；至少 90% 的实例端到端快于 CBC，且 DP-only speedup 随 $n$ 不恶化，则核心工程 claim 得到支持。这个阈值比论文的 95.9% 略宽，允许机器与版本差异。

**反驳标准。** 任一 cost mismatch 直接反驳正确性实现；或 htd 时间使超过一半实例端到端不再胜 CBC；或 memory 随 $k$ 在 8–10 已普遍不可承受，都足以反驳“低宽度下实用”的泛化。该实验不验证 Gurobi、Egg、code size 或 FPGA 映射，避免一周任务被扩大。

## § 11 — 最强反例设计

最强攻击不是构造一个明显 dense 的 clique，因为论文已经限定 sparse e-graph；更有力的是构造一族 **边数仍线性、size 与 operator distribution 接近 Cranelift，但 treewidth 可控增长** 的 e-graph，并保持 ILP formulation 容易。

具体做法是从真实低宽度 Cranelift graph 出发，复制多个局部 motif，再用稀疏 expander-like cross-links 连接 e-class 与 e-node，使总边数仍为 $O(n)$，同时 separator size 随 $n$ 增长。保持每个 e-class 的 member 数、每个 e-node 的 child 数和 cost distribution 与真实样本相近，避免“完全不真实”的反驳。对 $k=6,8,10,12,14,16$ 逐级生成，比较 treewidth DP、CBC/Gurobi 与一个可验证 optimum 的小规模 exhaustive solver。

这个反例会同时检验两种替代解释。若 DP 优势主要来自 benchmark 的低 width，它应随 $k$ 呈清晰指数恶化并很快输给 ILP；若优势主要来自 Rust 的 bitset/cache engineering，则在相同 $n$、不同 $k$ 下恶化可能远小于理论预期。再加入“同 $k$、不同 decomposition quality”的配对：一个用近最优 decomposition，一个故意宽 20%–40%。若小幅 decomposition 变差就使端到端性能崩溃，说明实际能力更依赖 decomposition tool，而不是 extraction DP 本身。[pdf:E10]（PDF 物理页 18，implementation optimizations）[pdf:E12]（PDF 物理页 20，decomposition 主导总时间）

判定上，只要存在结构仍稀疏、局部统计贴近真实 workload 的一段 $k$ 区间，使 ILP 稳定更快或 DP 内存先失控，就能推翻“sparse 即足够”的宽泛说法，并把正确适用条件收紧为“small-treewidth 且可快速分解”。这不会推翻定理，却会实质挑战论文标题与实践叙事中容易混淆的 sparsity/treewidth 等同。

## § 12 — Follow-up Research Bet

### 主押注：无需物化全局 e-graph 的流式全局最优 extraction

**新能力。** 把 extraction 从“saturation 结束后，拿到一张静态完整 e-graph 再求最优解”改成“e-graph 片段持续产生、分布在不同 worker 或存储层时，仍可随时得到当前全局最优 extraction”。成功后，大型 equality saturation 系统不必先把完整图集中物化，也不必在每次局部 rewrite 后从头求解；它可以把每个 fragment 压成可组合的边界语义，再沿 decomposition tree 合并成 exact optimum。这里改变了问题定义（static batch → evolving/streaming）、状态表示（bag 的标量 DP 表 → 可组合 boundary transfer summary）和系统边界（集中式全图 → 分片通信）。

**核心机制与因果链。** 本文已经证明，子图对外影响可由 $(M,S)$ 完整概括，join recurrence 只通过共享 bag 合并两个 child table。[pdf:E07]（PDF 物理页 11，boundary state）[pdf:E08]（PDF 物理页 13，join recurrence）这意味着每个 e-graph fragment 可以输出一个“从边界选择/欠账到最小内部成本与 witness”的 transfer operator，而不是输出内部全部 vertex。rewrite 只改变一个 fragment 时，只重新生成该 fragment 的 operator，再沿 decomposition ancestor chain 做代数合成：小边界形成有限消息 → fragment 内部被信息隐藏 → 多 worker 只交换 $O(f(k))$ summary → root 始终保有 exact global optimum。它不是给原算法加监视器或遇险回退；删除 summary composition 后，“不集中物化全图仍能全局最优”这项能力就不存在。

**为什么论文细节支持它。** 方法侧，$(M,S)$ 的语义正是一种充分边界接口，join 的 $S_1\cap S_2=S$ 与减去 $\mathrm{Cost}(M)$ 已给出组合律的雏形；共享 linked-list witness 也说明最优解证据可在不复制整个 partial solution 的情况下组合。[pdf:E08][pdf:E11]（PDF 物理页 19，node-sharing linked lists）实验侧，DP-only 在 99.9% 的适用实例上胜 CBC，而端到端主要被 decomposition 主导，说明下一步最大收益不是继续微调 DP inner loop，而是改变 decomposition/求解的生命周期：让结构和 summary 随图演化被复用。[pdf:E12] 同时，Cranelift 组合多个局部 optimum 后 code size 仍可能增加，恰好表明“各片段各自最优再拼接”不够；新机制必须交换带共享语义的 boundary summary，才能保持全局最优，而不是独立求局部最优。[pdf:E14]

**基本设计变量。** 需要设计：(1) fragment boundary 如何与 e-class congruence merge 对齐；(2) transfer summary 是完整 $(M,S)$ table、压缩 decision diagram，还是 min-plus tensor；(3) rewrite、e-class merge、target/cost change 分别触发哪些 summary 代数更新；(4) decomposition tree 是否与 worker placement 共设计；(5) witness 如何跨 fragment 以 persistent DAG 表示。评价对象也从一次 solve latency 扩展为每次 edit 的 amortized update cost、跨 worker bytes、未物化 vertex 数与持续 exactness。

**最大收益与最大风险。** 最大收益是把 exact extraction 变成 equality saturation 的在线组成语义：搜索、分区、存储和 extraction 可以共享同一套小边界接口，允许超出单机内存的 e-graph 仍保有全局最优输出。最大科学风险是动态 rewrite/merge 会破坏既有 decomposition；若一次常见 merge 引起全树大范围重构，summary 复用率就接近零，而论文已经表明 decomposition 是端到端瓶颈。[pdf:E12] Egg 的高 treewidth 与 acyclic requirement 也是明确负证据：该能力可能只对结构保持低宽度的 saturation regime 成立。[pdf:E14]

**首个可证伪实验。** 从 Cranelift artifact 取 100 个原始 e-graph，保留真实 build/rewrite 顺序，比较三种系统：(A) 每次 edit 后重新计算 decomposition 与本文 DP；(B) 固定 decomposition、只 memoize 未变 bag 的普通 DP；(C) fragment transfer summaries 加 ancestor-only composition。三者每一步必须与 ILP optimum 完全一致。核心机制的预测是：在 edit 只影响一个局部 fragment 且宽度不增时，C 的 update cost 与受影响 decomposition path 和 summary size 相关，而不是与全图 $n$ 相关；通信量远小于发送全部变化子图。最强替代解释是“普通 memoization 已经足够”。若 C 相对 B 没有稳定的 update-time/communication 优势，或真实 merge 使超过 25% 的 edits 需要全局 decomposition 重建，主机制即被反驳。

**与最近工作的实质区别。** 仅按本文 related-work 记载，Sun 等人的相邻工作也是 static e-graph optimal extraction 的 treewidth FPT，并额外降低 treewidth；Rosenthal 用 ZDD 表示 static candidate set；本文自己处理 static batch DP。[pdf:E15] 本押注把研究对象改为 evolving/distributed e-graph，把表示改为可跨 fragment 合成的 boundary operator，把实验对象改为真实 edit trace 和跨 worker communication。由于本任务禁止联网，尚未对这些论文全文及 2024 年后的工作做系统检索；因此这是论文特异、证据约束的候选判断，不声称 novelty。

**Wild-card alternative：** 将 $(M,S)$ table 解释为可训练但必须 exact decode 的 workload-specific elimination algebra，让 saturation 直接学习“生成低宽度 e-graph 的 rewrite schedule”，研究目标从事后提取转为共同塑造搜索空间拓扑与最优提取复杂度；该方向改变的是数据生成/搜索动力学，而不是流式分片机制。
