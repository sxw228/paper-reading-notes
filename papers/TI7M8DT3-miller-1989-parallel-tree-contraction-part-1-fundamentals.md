# Parallel Tree Contraction Part I: Fundamentals

作者：Gary L. Miller；John H. Reif  
出处：*Advances in Computing Research*，Volume 5，pp. 47–72，JAI Press Inc. [pdf:E01]（PDF 物理页 1，印刷页 47，标题页与 Abstract）  
年份：1989 [pdf:E01]（PDF 物理页 1，印刷页 47，版权信息）  
DOI：未报告  
Zotero key：TI7M8DT3  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：这篇论文真正解决的不是某一种表达式，而是“怎样把树上的全局依赖，改写成只靠局部动作推进、又能在对数并行深度内完成的通用计算骨架”。** 传统 top-down divide-and-conquer 先找一个把树切成约 `1/3–2/3` 的 separator，再递归处理；作者指出，在没有预处理的 dynamic expression evaluation 中，寻找 separator 会使 Brent 路线看起来多出一个 `log n` 因子。CONTRACT 改成 bottom-up：所有结构修改都局部发生，控制简单，也更容易迁移到别的树问题。[pdf:E02]（PDF 物理页 2，印刷页 48，Section 1.1）

论文把两类互补的局部消元统一起来：RAKE 处理“树很宽、叶子很多”的部分，COMPRESS 处理“树很瘦、单子链很长”的部分；两者同步执行后，任意根树只需 `O(log n)` 轮便可缩到根。[pdf:E03]（PDF 物理页 5，印刷页 51，Section 2 与 Theorem 2.1）这使树上计算的并行深度不再受原始树高直接支配。表达式求值、全部子表达式求值和 list ranking 只是用来展示这套骨架的三个应用；论文报告 deterministic 版本为 `O(log n)` 时间、`O(n)` processors，0-sided randomized 版本把 processors 降到 `O(n/log n)`。[pdf:E04]（PDF 物理页 4，印刷页 50，Section 1.3–1.4）

对 EMT + FPGA 读者，最值得迁移的是**依赖结构**：叶端局部消元、单接口链的函数合成、冲突自由的并行匹配、活跃任务压缩，以及保存一条可反向展开的 contraction history。不能从本文直接迁移的是具体电网络数值代数或硬件排程；本文没有三相模型、Schur complement、固定宽度矩阵块、数值稳定分析，也没有 PE、memory bank 或 interconnect 的实体约束。

## § 2 — 前人工作与不足

论文把 Brent 的 parallel arithmetic-expression evaluation 作为最直接的 prior work。Brent 已能把大小为 `n` 的表达式预处理成深度 `O(log n)` 的 straight-line code；作者认为，若输入需要在线、动态地转换，沿 separator 路线似乎要付出 `Ω(log² n)` 的时间。[pdf:E04]（PDF 物理页 4，印刷页 50，Section 1.3）不足不在“表达式不能并行”，而在于**先构造全局分解本身就昂贵**，且控制结构与原树形状强耦合。

论文还把全部子表达式求值视为 parallel prefix 的推广，并指出 list ranking 是其特例；作者声称其 0-sided randomized 结果给出了首个 `O(log n)` 时间、`n/log n` processors 的 list-ranking 算法。[pdf:E04]（PDF 物理页 4，印刷页 50，Section 1.3）这里的推进是把“前缀”从线性链推广到一般树，并同时处理从根值到全部内部值的 backward expansion。

前人路线还留下一个更工程化的缺口：即使每轮能删掉常数比例的顶点，若仍给每个原始槽位常驻一个 processor，dead pointers 会造成大量空转。Section 4 因而不只证明树会缩小，还专门解决 active tasks 的重新排列与部分 compaction；作者用 prefix sums、random permutation 和 DISCARD ZEROS 将 processor 数降到 `O(n/log n)`。[pdf:E05]（PDF 物理页 14，印刷页 60，Section 4.1）换言之，论文的第二层贡献不是新的树操作，而是把“结构上有线性总有效工作”变成 PRAM 上真正接近线性 processor-time 的执行。

## § 3 — 重建作者的思考路径

可以从三个失败模式重建作者的推理。

第一，只有 RAKE 不够。一条高度不平衡的长链每轮只会去掉末端叶子，可能要线性轮数；于是必须增加能把 unary chain 折半的 COMPRESS。[pdf:E03]（PDF 物理页 5，印刷页 51，Section 2）

第二，RAKE 与 COMPRESS 不能任意同时做。抽象定义把 chain 限定为：每个链顶点只有一个孩子，链尾的那个孩子不是叶子；随后只配对奇数位置与其下一个顶点。这样，同一 maximal chain 内的配对互不重叠，且 COMPRESS 不会触碰本轮正被 RAKE 删除的叶边。[pdf:E03]（PDF 物理页 5，印刷页 51，chain、COMPRESS 与 CONTRACT 定义）这一步先解决“每轮是否合法”，再谈速度。

第三，树缩小不等于计算被保存。每个被压缩的子树必须对尚未求值的接口保留一个紧凑 summary。作者观察到，表达式节点在只剩一个未知孩子时可表示成 unary function；在 `{+,×}` 的 semiring 示例中是 `aX+b`，两个这样的函数可继续合成，且只需两个 scalar 保存。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）因此，结构 contraction 与应用语义之间的接口是“**闭合、可快速合成、表示大小受控的标签代数**”。

在此基础上，deterministic 版本用 pointer jumping 让 unary chain 并行跨过父节点；randomized 版本则给 unary vertices 独立标记 F/M，只收缩 F-child→M-parent 的边，从而自动得到不共享端点的 matching。[pdf:E07]（PDF 物理页 8，印刷页 54，Figure 1）[pdf:E08]（PDF 物理页 10，印刷页 56，Figure 3）最后，作者再意识到“每轮删常数比例”仍不足以得到 work-optimal PRAM：必须把活指针重新聚拢，让少量真实 processors 模拟不断减少的 virtual processors，于是出现 Section 4 的随机排列与 partial load balancing。

## § 4 — 核心 Intuition

一轮同时做两件事：把所有已完成的叶端贡献向父节点吸收，并把只剩一个未决输入的长链按互不冲突的边成对折叠。每次折叠不保存整棵被删子树，而保存它对剩余接口的紧凑 unary function；只要这种表示在 composition 下闭合，树就能在 `O(log n)` 轮内变成一个根值。[pdf:E03]（PDF 物理页 5，印刷页 51，Theorem 2.1）[pdf:E06]（PDF 物理页 6，印刷页 52，linear-function composition）随机版本再用局部 coin flips 产生 matching，并通过重排活任务把 processor-time 降到线性量级。

## § 5 — 具体方法与完整 Pipeline

**输入与状态。** 输入是根树 `T=(V,E)`。每个 internal vertex 被视为一个以孩子值为参数的函数；若 `v` 有 `k` 个孩子，common memory 中为其预留 `k` 个 argument slots。`Arg(v)` 是尚未被标记的参数数目，`P(v)` 指向 `v` 在父节点中的那个唯一 slot。[pdf:E07]（PDF 物理页 8，印刷页 54，Figure 1 前后正文）这套表示保留了孩子的参数位置，因此同一父节点有多个叶子同时完成时，不必靠“最后写入者”决定语义。

**抽象 CONTRACT 的一轮。**

1. **RAKE：** 同时删除所有 leaves。应用层必须把每个叶子的值写入其父节点对应的 argument slot；若一个父节点的全部参数已到齐，就可求值，若只剩一个参数，就把该节点改写为对该参数的 unary function。
2. **COMPRESS：** 对每条 maximal unary chain，按 `(v₁,v₂),(v₃,v₄),…` 合并。链尾的孩子必须不是 leaf，故不会与同轮 RAKE 重叠；同一链上的 pair 也不重叠。[pdf:E03]（PDF 物理页 5，印刷页 51，Section 2）
3. **标签更新：** 被合并的两个 unary functions 做 composition；结构指针跳过被吸收节点，summary 留在幸存顶点上。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）

**Deterministic Dynamic Tree Contraction。** Figure 1 的一轮对每个非根顶点并行执行：若 `Arg(v)=0`，就标记 `P(v)` 并删除 `v`；若 `Arg(v)=Arg(parent(v))=1`，则让 `v` 的 pointer 跳到 grandparent。[pdf:E07]（PDF 物理页 8，印刷页 54，Figure 1）这里的“合法”与抽象 COMPRESS 不完全相同：相邻顶点可以同时读取彼此并做 pointer jumping，因为 deterministic phase 并不立即删除被跨过的 parent。论文明确说它比保守的 CONTRACT 更激进，分析时把 out-of-phase、永远不会被求值的链丢掉，剩下的 essential chains 与 CONTRACT 对应。

**Randomized CONTRACT。** 先照常删除 `Arg(v)=0` 的顶点；对 `Arg(v)=1` 的顶点独立随机赋 F 或 M；仅当 `v=F` 且 `parent(v)=M` 时，保存旧 `P(v)`、把 `P(v)` 跳到 grandparent，并删除旧 parent。[pdf:E08]（PDF 物理页 10，印刷页 56，Figure 3）这些被选边天然形成 matching：一个顶点不可能同时作为 F-child 和 M-parent，因此两次删除不会争用同一顶点；且两个端点均有 `Arg=1`，不会与本轮 `Arg=0` 的 RAKE 重叠。

**表达式例子。** 假设一条未决路径依次表示 `f₁(X)=X+3`、`f₂(X)=5X`、`f₃(X)=X+7`。RAKE 把已知常数吸收入节点标签，COMPRESS 先把相邻函数合成，最终得到 `f₃∘f₂∘f₁(X)=5X+22`。这是本文机制的演算示意；论文给出的关键条件是 `aX+b` 在 composition 下闭合、且只用两个 scalars 表示，而不是这组示例常数。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）

**输出与 backward expansion。** 若只求 root value，收缩到根即可。若要全部 subexpressions，deterministic contraction 在每个 phase 开始时把旧 `P(v)` 压入 `Store_v`；expansion phase 逐轮 pop 旧 pointer，并在 `Arg(v)=0` 时把值向父 slot 回填。[pdf:E09]（PDF 物理页 9，印刷页 55，Figure 2 与 push-down store 正文）Theorem 3.2 说明 contraction 与 expansion 各自至多约 `log_{5/4}n` 轮即可 mark all vertices。[pdf:E08]（PDF 物理页 10，印刷页 56，Theorem 3.2）在低-processor randomized 版本中，作者不再依赖每个 processor 的 local stack，而是在 common memory 保存几何缩小的各级树，并用 back pointers 连接 `T_i` 与 `T_{i+1}`；总 storage 至多线性。[pdf:E10]（PDF 物理页 20，印刷页 66，Theorem 4.6 后正文）

**原文究竟有没有讨论“逆向恢复”？有，但范围有限。** Section 5.2 明说把 randomized tree evaluation “backward” 运行，可以在 Theorem 5.1 的同一时间与 processor bounds 下计算全部 subexpressions。[pdf:E11]（PDF 物理页 21，印刷页 67，Section 5.2 与 Theorem 5.2）它恢复的是每个原树顶点的函数值／子表达式值及所需依赖指针，不是一个对任意 application payload 都成立的全状态 inverse，也没有讨论浮点误差、被消元物理状态、隐变量、历史波形或不可逆压缩的恢复。

**可迁移的树收缩依赖结构：** rooted dependency tree；叶端消元；单接口链的 pairwise composition；matching 约束；活任务 compaction；contraction tape/back pointers；按局部延迟异步推进。

**论文没有给出的内容：** exact Schur elimination；三相 `3×3` block 的闭合、可逆、pivoting 或 conditioning 条件；EMT 的 switch/event、time stepping、multi-rate 或 state-space 离散；全状态恢复定理；fixed-point/bit width；固定数量 PE 的映射；BRAM bank/port conflict；NoC/interconnect；cycle-accurate schedule。PRAM processor count 不能直接等同于 FPGA PE 数。

## § 6 — 核心数学推导（无形式化数学则跳过）

**1. 为什么轮数是 `O(log n)`。** 作者把顶点分成 `Ra` 与 `Com` 两类。RAKE 后，`Ra` 的幸存量至多为原来的 `4/5`；COMPRESS 后，每条 maximal chain 中属于 `Com` 的顶点至少折半。因此全局可取最慢收缩因子 `4/5`，经过约 `log_{5/4}n` 轮就只剩根。[pdf:E03]（PDF 物理页 5，印刷页 51，Theorem 2.1）这里的对数深度是组合结构结论，本身不依赖 CRCW、随机数或具体 processor 数。

**2. 为什么压缩不会丢失表达式语义。** 对 `{+,×}` 的示例，部分求值后的节点写成

\[
f(x)=ax+b.
\]

若另一层是 `g(x)=cx+d`，则

\[
(g\circ f)(x)=c(ax+b)+d=(ca)x+(cb+d),
\]

仍由两个 scalars 表示。这就是 COMPRESS 能把一条 unary chain 折叠成一个同类型标签的原因。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）

加入 division 后，作者改用 scalar linear-fractional function

\[
f(u)=\frac{au+b}{cu+d},\qquad g(y)=\frac{a'y+b'}{c'y+d'}.
\]

composition 仍为

\[
(g\circ f)(u)=\frac{(a'a+b'c)u+(a'b+b'd)}{(c'a+d'c)u+(c'b+d'd)}.
\]

论文把这写成“ratio of linear functions 在 composition 下闭合”，并据此证明 dynamic arithmetic-expression evaluation。[pdf:E11]（PDF 物理页 21，印刷页 67，Section 5.1 公式）这只是 scalar Möbius transform；原文没有把它推广成 matrix Schur complement，更没有三相 `3×3` block 的数值条件。

**3. Randomized pointer jumping 为什么能删常数比例。** 对 unary chain 中每个顶点独立赋 F/M，某条相邻边成为 F→M 的概率为 `1/4`。论文把一条长度 `n+1` binary string 中出现 `01` 的次数定义为 `MATE_n`，证明

\[
\mathbb{E}[MATE_n]=n/4,\qquad \mathrm{Var}(MATE_n)=(n+2)/16.
\]

[pdf:E12]（PDF 物理页 24，印刷页 70，Lemma 7.1）进一步用 independent-set lower bound 与 Chernoff bound 得到：当 `n≥180` 时，一轮 RANDOMIZED CONTRACT 至少删除 `n/32` 个顶点的失败概率小于 `1/n`。[pdf:E13]（PDF 物理页 13，印刷页 59，Theorem 3.7）较早的全程界是：至多约 `12.5 log n + 150` 轮，树以失败概率至多 `1/n` 缩为单点。[pdf:E14]（PDF 物理页 12，印刷页 58，Theorem 3.6）

**4. Depth、processor count 与 work 要分开。** 论文报告的 deterministic dynamic evaluation 是 `T=O(log n)`、`P=O(n)`，若用 `W=P·T` 计 processor-time，则上界为 `O(n log n)`；0-sided randomized 版本是 `T=O(log n)`、`P=O(n/log n)`，因而 `W=O(n)`。[pdf:E15]（PDF 物理页 20，印刷页 66，Theorem 5.1）随机版本的 processor 优化不是由 matching 单独带来，而依赖 Figure 5 中的 random permutations、pointer permutation、DISCARD ZEROS 与最后的小树收尾。[pdf:E16]（PDF 物理页 19，印刷页 65，Figure 5）Theorem 4.6 汇总为：0-sided randomized 算法以 `O(log n)` 时间、`O(n/log n)` processors mark all vertices。[pdf:E10]（PDF 物理页 20，印刷页 66，Theorem 4.6）

**5. 这些复杂度分别依赖什么机器假设。**

- **纯结构轮数：** RAKE/COMPRESS 的 `O(log n)` 轮数不依赖 PRAM 并发读写。
- **Deterministic 每轮 `O(1)`：** 论文全局采用 CRCW PRAM；processor 可在 unit time concurrent read/write common memory，并对大小至多 `n^{O(1)}` 的整数做 unit-cost arithmetic。[pdf:E02]（PDF 物理页 2，印刷页 48，Section 1.2）对 unbounded degree，作者给每个 argument 一个 processor，并用 concurrent writes 测试 `Arg(v)=0/1`；这一步是 constant-time phase 的明确 CRCW 依赖。[pdf:E07]（PDF 物理页 8，印刷页 54，Figure 1 后正文）
- **Concurrent-write 语义：** 默认是 arbitrary-winner write，即多个 processor 写同一地址时任意一个成功，但算法结果不能依赖赢家；作者还说 detectable-noise 的 collision 模型可保持相同性能。论文没有给 EREW 或 CREW 版本及其额外代价。[pdf:E17]（PDF 物理页 3，印刷页 49，Section 1.2）
- **Randomized 收缩：** 每个 processor 每步可取得一个独立、大小 `<n` 的 random number；0-sided 意味着终止时总是正确，且终止概率至少 `1-1/n`。[pdf:E17]（PDF 物理页 3，印刷页 49，Section 1.2）
- **Work-optimal load balancing：** random permutation 在某个 processor 超过 trial budget 时用 concurrent write 全局 abort；DISCARD ZEROS 在任一 interval overflow 时也用 concurrent write abort。[pdf:E18]（PDF 物理页 16，印刷页 62，Lemma 4.3 前后）[pdf:E19]（PDF 物理页 17，印刷页 63，Theorem 4.4 proof）所以 `O(n/log n)` processor 结论依赖 CRCW、独立随机性、prefix computations、可重排 common-memory pointers，以及失败时可检测并重启的 0-sided 组织方式。
- **Unbounded degree：** 若 raking `k` 个孩子的 cost 至多 `O(log k)`，同步 barrier 可能叠成 `O(log² n)`；APTC 用 phantom leaves 表示尚未完成的局部工作，并在已完成区域继续下一轮，在“cost 只依赖该节点 leaf 数”的条件下仍得 `O(log n)` stages。[pdf:E20]（PDF 物理页 22，印刷页 68，Section 6 与 Theorem 6.1）其 proof 用 phantom weight 的几何衰减作为 potential。[pdf:E21]（PDF 物理页 23，印刷页 69，Theorem 6.1 proof）

## § 7 — 实验设计与结论

这是一篇理论算法论文，没有 wall-clock benchmark、硬件资源表、误差曲线、FPGA timing 或 numerical ablation。它的“验证”由定理、概率界和应用构造组成。

**问题 1：任意树是否都能在对数轮数内缩完？ → 验证：** 按顶点局部度数把树分成 `Ra/Com`，分别证明 RAKE 至少取得 `1/5` 进展、COMPRESS 至少折半 chain 部分。**答案：** 约 `log_{5/4}n` 轮足够。[pdf:E03]（PDF 物理页 5，印刷页 51，Theorem 2.1）

**问题 2：deterministic pointer jumping 是否会因“错相”链而变慢或算错？ → 验证：** 把每条 maximal chain 分成 essential chain 与不会被求值的 out-of-phase chain，并只在 proof 中丢弃后者。**答案：** dynamic contraction 的轮数不超过抽象 CONTRACT；加入 per-vertex pointer stack 后，再做同量级 expansion 可 mark all vertices。[pdf:E09]（PDF 物理页 9，印刷页 55，Theorem 3.1 后与 Figure 2）

**问题 3：随机 matching 每轮能否稳定删掉常数比例？ → 验证：** 以 MATE random variable、variance、Chernoff bound 和 forest independent set 给出 lower bound。**答案：** 大树中一轮至少删 `n/32` 的失败概率小于 `1/n`，全程为 `O(log n)` rounds with high probability。[pdf:E13]（PDF 物理页 13，印刷页 59，Theorem 3.7）

**问题 4：能否在不牺牲 `O(log n)` depth 的情况下把 processors 从 `n` 降到 `n/log n`？ → 验证：** 先预生成几何缩小的一系列 random permutations，每轮随机打散活／死 pointers，再用 DISCARD ZEROS 只压掉常数比例 dead slots，最后对 `n/log n` 规模的小树用一顶点一 processor 收尾。**答案：** Theorem 4.6 给出 0-sided randomized `O(log n)` time、`O(n/log n)` processors，并用线性总 back-pointer storage 支持 expansion。[pdf:E16]（PDF 物理页 19，印刷页 65，Figure 5）[pdf:E10]（PDF 物理页 20，印刷页 66，Theorem 4.6）

**问题 5：结构 contraction 是否真的能承载应用语义？ → 验证：** 对 arithmetic expressions 构造 linear／linear-fractional function algebra，并 backward 运行得到全部 subexpressions。**答案：** root evaluation、all-subexpression evaluation 与 list ranking 都达到相同 asymptotic bounds。[pdf:E15]（PDF 物理页 20，印刷页 66，Theorem 5.1）[pdf:E11]（PDF 物理页 21，印刷页 67，Theorem 5.2 与 Corollary 5.3）

不得外推的范围很明确：这些定理验证的是 abstract PRAM step、processor count、概率和 symbolic operation closure；它们没有验证真实 memory bandwidth、bank conflicts、routing、clock frequency、finite precision、roundoff、ill-conditioning、dynamic switch events 或 EMT real-time step。

## § 8 — Take-aways

**5 句话版**

1. CONTRACT 用 RAKE 解决宽树、用 COMPRESS 解决长链，使任意树的结构 depth 降到 `O(log n)`。[pdf:E03]（PDF 物理页 5，印刷页 51，Section 2）
2. 真正承载语义的是每个收缩节点保存的 bounded-size unary-function label，而不是“删除顶点”本身。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）
3. Deterministic 版本以 `O(n)` processors 换取简单的 constant-time pointer-jumping phases；randomized 版本用 matching 与 load balancing 把 processors 降到 `O(n/log n)`。[pdf:E04]（PDF 物理页 4，印刷页 50，Section 1.3–1.4）
4. 论文确实给出 backward expansion，并能恢复全部 subexpression values，但保存的是 pointer/function history，不是任意物理系统的全状态。[pdf:E09]（PDF 物理页 9，印刷页 55，Figure 2）
5. 对 FPGA，最可复用的是 contraction DAG 与 active-task compaction；CRCW 和 unit-cost labels 必须重新实现，不能把 PRAM processor count 直接当成 PE schedule。

**3 句话版**

1. 树收缩的本质是“叶端消元 + 单接口链合成”，其组合结构保证对数 rounds。
2. 随机匹配负责产生冲突自由的局部删除，random permutation/compaction 才负责把总 processor-time 做到 `O(n)`。[pdf:E05]（PDF 物理页 14，印刷页 60，Section 4.1）
3. Reverse expansion 是原文的一部分，但 Schur、三相 block、全状态恢复和 bank-aware hardware mapping 不是。

**1 句话版**

这篇论文给出了一套可逆向展开的树依赖压缩框架及其 CRCW-PRAM 复杂度，而不是一套现成的 EMT 数值消元或 FPGA 实现。

## § 9 — 最脆弱的假设

**最脆弱的不是“树能否缩小”，而是 application label 是否存在 bounded-size、快速、composition-closed 的表示。** 结构定理即使成立，若每次 COMPRESS 都让 summary 变大，`O(log n)` rounds 也不再等于 `O(log n)` computational depth，更不意味着 `O(n)` work。

论文在 expression case 中给出的正面证据很具体：`aX+b` 只需两个 scalars，且 pairwise composition 后仍是同型；加入 division 时改用四个系数的 linear-fractional form，仍然闭合。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）[pdf:E11]（PDF 物理页 21，印刷页 67，Section 5.1）但这只是特定 scalar algebra。论文没有证明 matrix-valued interface operator 的维数不增长，也没有讨论 fill-in、pivoting、condition number、bit width 或 quantization。

在实际 EMT／FPGA 场景中，这一假设可能因三个原因失效：多端口消元让接口维数增长；三相耦合把原本稀疏 block 变密；为保证数值稳定而引入的 pivoting 或重排序破坏原树依赖。如果发生其中任一项，树仍可在结构上 contraction，但每个节点携带的 payload、算术 latency 和 memory traffic 会增长，论文的 processor/depth 结论就不能直接迁移。原文给了“应当寻找一种可实现并存储 unary-function composition 的 general form”这一方法论提示，却没有给上述工程条件的证据。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）

## § 10 — 最小复现实验

一周内最有信息量的复现不是做完整 PRAM，也不是上 FPGA，而是写一个 **round-accurate tree-contraction simulator**，同时验证 structure、work 与 reverse expansion。

**数据。** 生成 `n=2^10…2^20` 的五类 rooted trees：path、balanced binary tree、star/bounded-degree replacement、broom、random bounded-degree tree。为每个 internal vertex 随机赋 `{+,-,×}`，叶值用小整数；另建一组安全 division case，保证 denominator 非零。递归 evaluator 作为 ground truth。

**实现。** 严格按 Figure 1 实现 deterministic phase，按 Figure 3 实现 randomized F/M phase；为每个顶点保存 `Arg`、argument slots、`P(v)`、compact function label 与 `Store_v`。再实现 Figure 2 expansion，以及 Figure 5 的一个软件化近似：每轮记录 live/dead pointer array，随机 permutation 后做 stable compaction。[pdf:E07]（PDF 物理页 8，印刷页 54，Figure 1）[pdf:E08]（PDF 物理页 10，印刷页 56，Figure 3）[pdf:E16]（PDF 物理页 19，印刷页 65，Figure 5）

**测量。** 记录 contraction rounds、每轮删除比例、active-vertex operations、`P·T` 估计、最大 live-pointer array、history bytes、root-value correctness、全部 subexpression correctness。对 randomized case 每个 `(tree,n)` 运行至少 1,000 个 seeds，画出一轮删除比例和总 rounds 的分布。

**支持 claim 的结果。** 所有 tree family 的 rounds 随 `log n` 线性；randomized 一轮在大 `n` 时极少低于 `n/32`；processor-limited simulation 的总有效任务接近 `O(n)`；backward expansion 对每个原顶点给出与递归 evaluator 相同的值。[pdf:E13]（PDF 物理页 13，印刷页 59，Theorem 3.7）[pdf:E11]（PDF 物理页 21，印刷页 67，Theorem 5.2）

**反驳 claim 的结果。** 任一合法 tree family 出现 superlogarithmic rounds；F/M selected edges 发生端点冲突；pointer history 不足以恢复全部顶点；或在 label size 固定的前提下，active-task work 仍系统性超线性。这个实验不会验证 CRCW 的真实硬件成本，但会把“结构算法错误”与“机器模型不现实”分开。

## § 11 — 最强反例设计

最强攻击是构造一个**结构上完全适合 COMPRESS、语义 summary 却指数膨胀**的应用。取一条长度为 `n` 的 unary chain，每个节点不是 `ax+b`，而是一个有两个单调分支的非单调 piecewise-linear map，例如适当缩放的 tent map。显式 composition 一次可把 breakpoints 数量近似翻倍；经过整条链，精确表示可能有 `2^n` 个 pieces。

在这个输入上，RAKE/COMPRESS 仍会按论文的结构证明在 `O(log n)` rounds 内把链折叠；random F/M matching 也完全合法。但每个幸存 label 的表示大小和 composition cost 爆炸，故 unit-cost function evaluation、bounded-size memory 与 `O(n)` work 同时失效。这个反例不推翻 Theorem 2.1 的结构结论，也不推翻论文对 arithmetic expressions 的定理；它直接攻击“只要是树问题就容易迁移”的泛化。

对应的 EMT 压力测试应选择会使 eliminated subtree 的 boundary operator 接口维数或 dense coupling 持续增长的 radial multiport family，观察 payload size 是否随 contraction level 扩张。不过，本文没有给出 exact Schur、三相 `3×3` block 或 pivoting 条件，因此这种 EMT 反例属于基于论文机制的外推设计，不能写成原文结论。

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty：建立“typed boundary-operator contraction”——让 tree contraction 同时成为多端口动态网络的数值代数与可综合空间执行图。** 由于本任务只允许使用输入包、未检索后续全文，下面只能与本文自身作实质比较，不能对最近工作作事实性 novelty 声明。

**新的研究问题。** 是否存在一类固定接口类型的 dynamic-network operators，使每个 subtree 都能被压成 bounded-size boundary response，RAKE 与 COMPRESS 在该类型系统中闭合；同时，contraction history 又携带足够的 reconstruction factors，以从 root/boundary solution 恢复全部内部 states？这会首次把本文的 scalar unary-function idea 扩展为“数值语义、reverse reconstruction 与 banked spatial execution”共同设计的对象，而不是先做抽象消元、再另写一个 hardware wrapper。

**核心机制与因果链。** 每个顶点不再只保存 `aX+b` 或 `(ax+b)/(cx+d)`，而保存带显式 interface signature 的小型 boundary operator；RAKE 消去 leaf-side internal variables，COMPRESS 只在两个 operator 的 interface types 可合成且输出 type 不增长时执行。每次合成同时写入 reconstruction factor 和 contraction edge；这些 edges 形成与 Figure 5 相似的 shrinking DAG，再被编译成有限 PE、有限 bank ports 下的空间数据流。若 operator closure 成立，结构常数比例缩小带来对数 dependency depth；若 reconstruction factors 完备，backward pass 可恢复内部 states；若 type 约束还能界定 payload size，才可能把 `O(n)` processor-time 转化为稳定的 memory traffic。本文的依据分别是 compact unary composition、back pointers/linear storage、processor-efficient shrinking algorithm。[pdf:E06]（PDF 物理页 6，印刷页 52，Section 2）[pdf:E16]（PDF 物理页 19，印刷页 65，Figure 5）[pdf:E10]（PDF 物理页 20，印刷页 66，Theorem 4.6 后正文）

**改变的基本设计变量。** 状态表示从 scalar unary function 改为 typed multiport operator；研究目标从 root expression value 改为 boundary response 加全部 internal-state reconstruction；时间模型从 unit-cost PRAM step 改为 operator-dependent pipeline latency；hardware mapping 从无限 common memory 的 abstract processors 改为显式 PE/bank/interconnect 图。是否能退化为 fixed `3×3` phase blocks、是否需要 Schur-like update、何时可逆和稳定，都是要被证明或否证的问题，不能从本文预设答案。

**最大收益与最大风险。** 成功后，可得到一条从数学 closure theorem 到 cycle-level dataflow 的完整链条：同一 contraction DAG 同时决定 elimination order、reverse tape 和硬件通信。最大科学风险是最脆弱假设再次失败：interface dimension、fill-in、conditioning 或 reconstruction storage 可能随层级增长，使 typed operator 不再 bounded-size；此时结构 contraction 仍快，但数值与硬件复杂度不快。

**首个可证伪实验。** 构造一组小型三相 radial RLC trees，使用高精度 reference solver；为每个 subtree 自动生成 boundary operator 与 reconstruction factor，逐层执行 RAKE/COMPRESS。测量 operator dimension、nonzero count、condition number、composition latency、reverse state error、bank-conflict count，并与“相同 levelization、但用 generic sparse elimination”的 baseline 比较。只有当 operator size 在深度上有统一上界、reverse pass 恢复全部 node states、且速度收益在控制相同 schedule 后仍存在，才支持核心机制；否则最强替代解释是收益仅来自普通 tree levelization，而不是新的 operator algebra。

**Wild-card alternative：** 把 APTC 的 phantom leaves 从 proof device 改造成 latency tokens，为 data-dependent arithmetic pipelines 建立异步 contraction calculus；其核心变量是局部操作延迟与 token decay，而不是 matrix operator representation。[pdf:E20]（PDF 物理页 22，印刷页 68，APTC 定义）论文还留下 MATE 总 moments 的 conjecture，提示另一条完全不同的路线：用更强的随机变量界或 derandomization 设计既保持 matching shrinkage、又直接均匀散列到 memory banks 的调度器。[pdf:E22]（PDF 物理页 25，印刷页 71，Section 7 conjecture）
