# Task Scheduling for Parallel Sparse Cholesky Factorization

- 作者：G. A. Geist；E. Ng
- 出处：*International Journal of Parallel Programming*, Vol. 18, No. 4
- 年份：1989
- DOI：10.1007/BF01407861
- Zotero key：U6HIF8TT

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个很具体的并行化问题：在稀疏、对称正定矩阵 \(A\) 的 Cholesky 分解 \(A=LL^T\) 中，已经选好稀疏排序以后，如何把 \(L\) 的列计算分配给多个处理器。作者把一列视为一个 task；调度既要让处理器承担近似相同的计算量，又要尽可能让互不依赖的列并发执行，还要减少由列依赖造成的处理器间通信或同步。论文明确把这三个目标同时写入问题定义，并强调 minimum degree 一类减 fill 排序往往产生不平衡的 elimination tree，因此“稀疏性较好”并不自动意味着“容易并行”。[pdf:E01]（PDF 物理页 1，摘要与 §1 开头）[pdf:E02]（PDF 物理页 2，§1）

这里的 task graph 不是另行构造的任意 DAG，而是 Cholesky 的 elimination tree：每个顶点对应一列，父子与祖先关系编码列间依赖。处在不同子树的列相互独立，叶节点可以同时开始；沿树向根推进时，父列要等待相关子树中的先行列完成。因此，树的宽度近似表示可同时暴露的任务数，树高则构成一条串行依赖路径。[pdf:E03]（PDF 物理页 3，journal p.293，Fig. 1–2 与 elimination tree 定义）[pdf:E04]（PDF 物理页 4，journal p.294，列依赖与并行解释）

论文的重要性在于，它把“排序得到的稀疏矩阵”与“真实并行执行”之间缺失的一层补上了。只优化 fill 和 operation count，可能得到很偏的树；只把任务均匀轮转给处理器，又可能让依赖数据跨处理器频繁流动。作者试图在不重新定义数值分解的前提下，从符号结构预先预测每列工作量，再完成静态 task scheduling。

## § 2 — 前人工作与不足

论文讨论了三条既有路线。

第一，dense Cholesky 常用 wrap mapping，把第 \(i\) 列分给处理器 \((i-1)\bmod p\)。sparse-wrap 进一步按 elimination tree 的叶层逐批取出可并行列，再轮转给处理器。它能把潜在并发任务分散到不同处理器，但已有实验只说明通信负载在链路间较均匀，并不保证通信总量低。[pdf:E05]（PDF 物理页 11，journal p.301，§3 与 Fig. 12 上方正文）

第二，George、Liu 和 Ng 的 subtree-to-subcube mapping 把一棵子树及其通信限制在一个处理器子立方体中；论文引用的相关工作已对 nested-dissection 排序的规则 \(k\times k\) 网格给出渐近通信量最优结果。它的问题是依赖较平衡的 elimination tree，而且通常以处理器数为 2 的幂为自然条件；若树很偏，一整个重子树落在少数处理器上，通信可能减少但负载会严重失衡。[pdf:E05]（PDF 物理页 11，Fig. 12 与正文）[pdf:E06]（PDF 物理页 12，journal p.302，subtree-to-subcube 的通信性质与限制）这里的“渐近最优”是论文转述的相关文献结论，不是本文重新证明的结果。

第三，可以先旋转 elimination tree，以降低树高且不增加 fill 或 operation count。作者指出，Liu 的 tree rotation 有时能显著降低高度，但通常不能把树变成足够平衡、可直接有效应用 subtree-to-subcube 的结构。更根本的矛盾是：nested dissection 较容易产生宽而短的树，但对一般问题可能带来更多 fill；minimum degree 往往 fill 更少，却容易产生不平衡树。L 形有限元问题的 Table I 就显示，在 \(n=6121\) 时，MMD 有 164,054 个 off-diagonal nonzeros、4,964,748 次 operations，而 8 处理器 ND 对应 173,906 和 6,006,244，16 处理器 ND 对应 175,902 和 6,210,709。[pdf:E07]（PDF 物理页 13，journal p.303，Table I）因此，本文不是再发明一种 fill-reducing ordering，而是接受 MMD 产生的不平衡树，再解决其调度问题。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，不是作者逐句陈述的研究日志。

先从已知事实出发：elimination tree 已经精确表达列依赖，互不相交的子树天然可并行；同时，矩阵的符号结构足以在数值分解之前预测每列的 nonzero count 和 operation count。[pdf:E03]（PDF 物理页 3，Fig. 1–2）[pdf:E08]（PDF 物理页 14，journal p.304，§4）

接着观察失败模式：若直接 wrap，独立任务虽然被分散，但依赖数据也容易跨处理器；若把整棵子树固定给一个处理器组，通信局部性改善，却要求树本身平衡。MMD 恰好经常给出低 fill、低 operation count 但不平衡的树，所以不能为了适配旧调度器就轻易放弃 MMD 的数值工作量优势。[pdf:E06]（PDF 物理页 12，subtree-to-subcube 限制）[pdf:E07]（PDF 物理页 13，Table I）

由此可以自然走到作者的 idea：不要强迫原树变平衡，而是把每个子树的预测 operation count 当作重量，从树顶逐步切出更多独立 branch，再把这些 branch 当作可装箱的物件分给 \(p\) 个处理器。只要装箱后的负载比达到阈值，就停止继续切树；尚未被切入独立 branch 的上部 separator 再用 wrap 处理。这样，“切得更深”换来更细粒度的负载平衡，但也扩大 separator、增加潜在通信；停止阈值正是这个权衡的控制量。[pdf:E08]（PDF 物理页 14，任务目标与 breadth-first pruning）[pdf:E12]（PDF 物理页 19，journal p.309，separator 与 balance/communication trade-off）

## § 4 — 核心 Intuition

核心直觉是：不平衡的 elimination tree 不必先被改造成平衡树，只要把独立子树按预计浮点工作量切成足够多的 branch，再把重 branch 优先放进当前最轻的处理器 bin，就能在保留子树局部性的同时逼近负载平衡。继续切树会改善装箱粒度，却把更多上层节点留进需要跨处理器处理的 separator，因此调度不是单目标“越平衡越好”，而是计算均衡与通信局部性之间的可控折中。[pdf:E08]（PDF 物理页 14，§4）[pdf:E11]（PDF 物理页 17，journal p.307，Fig. 16 后的 bin-packing 说明）

## § 5 — 具体方法与完整 Pipeline

以一个已经用 MMD 重排、且 elimination tree 明显偏斜的稀疏 SPD 矩阵为例，完整 pipeline 如下。

1. **固定数值问题与 task 粒度。** 输入是重排后的 \(A\)、处理器数 \(p\) 和用户给定的负载容差。输出不是新的矩阵排序，而是“每个 Cholesky 列 task 分给哪个处理器”的静态映射。论文采用列粒度，因为这与当时商用 multiprocessor 的粒度匹配。[pdf:E01]（PDF 物理页 1，§1）
2. **建立 task graph。** 由 \(A\) 的符号结构在计算 \(L\) 之前生成 elimination tree。树中每个节点是一列；不同子树的列可以并行，祖先路径决定必须等待的列依赖。[pdf:E03]（PDF 物理页 3，Fig. 1–2）[pdf:E04]（PDF 物理页 4，依赖解释）
3. **预测每列代价。** 利用 `parent`、每列 nonzero count `nz` 和访问标记 `marker`，Fig. 13 的符号算法生成 `fcnt(i)`，即第 \(i\) 列所需乘除操作数。它不必先完成数值 Cholesky。[pdf:E08]（PDF 物理页 14，Fig. 13 的输入说明）[pdf:E09]（PDF 物理页 15，journal p.305，Fig. 13）
4. **把列代价累积成子树代价。** 从节点到父节点累加，得到 `nodewt(i)`；它等于以 \(i\) 为根的整棵子树所需浮点操作总量。根节点的 weight 就是整个 factorization 的 operation count。[pdf:E10]（PDF 物理页 16，journal p.306，Fig. 14 与正文）
5. **逐步切 branch。** 从至少 \(p\) 个 branch 开始；若当前装箱不能满足负载比，就在最重 branch 中继续向下找分叉，用更小的 sibling branches 替换它。Fig. 16 给出这一 partition-tree 过程。[pdf:E11]（PDF 物理页 17，Fig. 16）
6. **用两个 heap 装箱。** branch weight 放入 max-heap，处理器 bin load 放入 min-heap。每次把当前最重 branch 加到当前最轻 bin，再更新两个 heap；单次 heap update 为 \(O(\log q)\)，其中 \(q\) 是 heap 条目数。全部 branch 分配后检查负载比，不满足就继续切树并重装箱。[pdf:E10]（PDF 物理页 16，Fig. 15）[pdf:E11]（PDF 物理页 17，heap 说明）
7. **分配 separator。** 已装箱的独立 branch 固定给相应处理器；树上剩余节点组成 separator set \(\mathcal S\)，默认按 wrap 分配。论文还试验了在 \(\mathcal S\) 上推广 subtree-to-subcube，但对不规则 MMD 问题，wrap 更好，因为树顶较稠密，而且 subtree 方案再次引入负载不平衡。[pdf:E12]（PDF 物理页 19，separator 策略）[pdf:E15]（PDF 物理页 23，journal p.313，作者解释）

论文没有报告动态 work stealing、运行时重新调度、异构处理器、GPU/FPGA 映射、片上存储分配、数值位宽、实时 deadline 或多速率时间推进。这些在本文中均为**未报告**，不能从历史 CPU 调度结果补写出来。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文形式化程度不高，核心是结构定义、代价递推和停止准则，而不是收敛定理。

首先，数值问题是

\[
A=LL^T,
\]

其中 \(A\) 稀疏、对称正定，\(L\) 为对角元为正的下三角矩阵。[pdf:E01]（PDF 物理页 1，§1）

对第 \(j\) 列，若存在对角线下方 nonzero，则 elimination-tree parent 定义为第一个 off-diagonal nonzero 的行号：

\[
\operatorname{parent}(j)=\gamma(j);
\]

若不存在则记为 0，根节点为 \(n\)。列 \(i\) 只会影响其祖先中的一部分，因此不相交子树之间没有直接列依赖。[pdf:E03]（PDF 物理页 3，journal p.293，定义与 Fig. 2）这里的工程含义是：树边不是“数据大小相似”，而是“先后依赖与潜在通信”的结构标记。

Fig. 13 先由符号结构预测每列代价 \(f_i=\texttt{fcnt}(i)\)；随后 Fig. 14 递推子树权重：

\[
w_i=f_i+\sum_{c\in\operatorname{children}(i)}w_c.
\]

所以 \(w_i\) 是以 \(i\) 为根的全部列任务的预测 operation count，而 \(w_{\text{root}}\) 是整个 factorization 的预测 operation count。[pdf:E09]（PDF 物理页 15，Fig. 13）[pdf:E10]（PDF 物理页 16，Fig. 14）

设装箱后最轻和最重处理器的预测负载分别为 \(B_{\min}\) 与 \(B_{\max}\)，算法检查

\[
r=\frac{B_{\min}}{B_{\max}}\ge \texttt{tol}.
\]

若不满足，就增加 branch 数、重新装箱；满足后把 bin 中节点分给处理器，separator 节点按 wrap 分配。[pdf:E10]（PDF 物理页 16，Fig. 15）实验中“maximum load variation 20%”对应最忙与最闲处理器 operation count 的差小于 20%；作者还比较了 25% 到 5% 的阈值。[pdf:E14]（PDF 物理页 22，journal p.312，Table IV）论文没有给出该 greedy bin packing 相对最优调度的 approximation ratio，也没有证明 operation count 与真实执行时间严格成比例；这两点都应保持为**未知**。

## § 7 — 实验设计与结论

实验平台是 Intel iPSC/2，测试数据是一组 L-shaped domain 上的 finite-element 问题；详细问题构造被指向参考文献 12，本文本身没有给出足以逐字节重建矩阵的全部信息。[pdf:E01]（PDF 物理页 1，摘要）[pdf:E12]（PDF 物理页 19，§5）

**问题一：MMD 是否以更不平衡的树换来了更少的符号/数值工作？**
实验比较 MMD 与 8、16 处理器 parallel nested dissection 的 off-diagonal nonzero count 和 operation count。Table I 的 9 个规模上，MMD 均给出更低计数；例如 \(n=6121\) 时，MMD 为 164,054 nonzeros 和 4,964,748 operations，而 ND(\(p=16\)) 为 175,902 和 6,210,709。[pdf:E07]（PDF 物理页 13，Table I）答案是：在这组 L 形有限元问题上，MMD 的工作量优势明确，但本文没有证明这一趋势适用于任意稀疏矩阵。

**问题二：新 MMD-subtree 调度是否降低实际 factorization time？**
实验在 8 和 16 处理器上比较 sparse-wrap、使用 ND 的 subtree-to-subcube，以及使用 MMD 的新方法。Table II 中新方法在全部列出的规模上最快；例如 \(n=6121\) 时，8 处理器分别为 25.12、23.50、21.35 秒，16 处理器分别为 16.64、15.16、14.33 秒。[pdf:E12]（PDF 物理页 19，Table II）答案是：在该平台与数据集上，新组合取得一致的 wall-clock 优势。但这是“ordering + mapping”的组合比较，MMD 与 subtree-to-subcube 使用了不同 ordering；因此不能把全部差值都归因于 scheduler，Table I 已经显示 MMD 本身减少了 operations。

**问题三：先做 tree rotation 是否能带来同等级收益？**
作者对 MMD tree 应用 Liu 的降高 heuristic，factorization time 改善小于 1%。[pdf:E14]（PDF 物理页 22，Table IV 下方正文）答案是：在这组问题上，单纯降低树高不是主要收益来源。

**问题四：separator 顶部用 wrap 还是 subtree mapping？**
8 处理器 Table III 显示 wrap 在 5 个规模上均不慢于 subtree；\(n=6121\) 时，subtree 为 25.61 秒，wrap 为 21.41 秒。作者解释为树顶较稠密，且对不平衡树再次做 subtree mapping 会造成更严重负载不均。[pdf:E13]（PDF 物理页 21，journal p.311，Fig. 20 与 Table III）[pdf:E15]（PDF 物理页 23，解释正文）答案是：对本文的不规则 MMD 树，separator 使用 wrap 更合适。

**问题五：更严格的负载阈值是否必然更快？**
Table IV 把 maximum load variation 从 25% 收紧到 5%。时间没有单调改善；例如 \(n=6121\) 从 21.335 秒变为 21.745 秒，反而略增。[pdf:E14]（PDF 物理页 22，Table IV）答案是：预测负载更均衡不等于运行时间更短，因为继续切树会扩大 separator 并增加通信。

**问题六：调度预处理是否足够便宜？**
Table V 的 mapping 时间为 0.100–0.260 秒；同一论文报告的 factorization 时间在数秒至二十余秒量级。[pdf:E14]（PDF 物理页 22，Table V）答案是：在当时这些规模和 iPSC/2 上，预处理开销较小。作者进一步将速度下降主要归因于通信减少，但论文没有给出 message count、bytes 或链路占用的直接测量，所以“通信减少是主因”是作者结论而非由独立通信计数闭合的因果证明。[pdf:E15]（PDF 物理页 23，结论段）

实验明确指出，这些问题太小，无法有效使用超过 16 个处理器。[pdf:E13]（PDF 物理页 21，Table III 上方正文）因此不得把结果外推到更大并行度，更不得直接外推到现代 GPU、FPGA 或分布式 accelerator。

## § 8 — Take-aways

**5 句话：**
1. elimination tree 把稀疏 Cholesky 的列 task、依赖路径和可并行子树放进同一个结构。[pdf:E04]（PDF 物理页 4）
2. 低 fill 的 MMD 可能产生不平衡树，因此 ordering quality 与 parallel schedulability 不是同一个目标。[pdf:E07]（PDF 物理页 13，Table I）
3. 本文用符号预测的 operation count 给子树加权，再通过逐步切 branch 与 greedy bin packing 达到指定负载比。[pdf:E09]（PDF 物理页 15，Fig. 13）[pdf:E10]（PDF 物理页 16，Fig. 14–15）
4. 独立 branch 固定到处理器，separator 用 wrap，体现了负载平衡与通信局部性的显式折中。[pdf:E11]（PDF 物理页 17）
5. iPSC/2 实验支持该组合方法在 8、16 处理器和 L 形有限元问题上的时间优势，但比较受 ordering 差异影响，且不覆盖现代 accelerator。[pdf:E12]（PDF 物理页 19，Table II）

**3 句话：**
1. 这篇论文的价值不在新的 Cholesky 数值公式，而在从 elimination tree 提取可静态调度的 task graph 与代价。
2. 它用“切多少 branch”控制并行负载粒度，用 separator 大小承担相应通信代价。[pdf:E12]（PDF 物理页 19，trade-off 正文）
3. 实验说明该思想在指定历史 CPU 平台上有效，但没有建立跨架构性能定律。

**1 句话：**
不要强迫稀疏排序先产生一棵漂亮的平衡树；应从真实依赖树中切出带权独立任务，再把计算均衡与数据移动一起调度。

## § 9 — 最脆弱的假设

最脆弱的假设是：**每列预测 floating-point operation count 的子树和，足以代表各处理器的真实执行负载。** 如果实际时间主要由不规则访存、message latency、通信量、同步等待或不同列的 kernel efficiency 决定，那么两个 bin 的 \(w_i\) 之和相等，也可能有完全不同的 wall-clock time；此时 algorithm 的核心停止准则会在错误的 cost model 上宣告“已经平衡”。[pdf:E09]（PDF 物理页 15，Fig. 13 的 `fcnt`）[pdf:E10]（PDF 物理页 16，Fig. 14–15 的 weight 与 ratio）

论文给出的支持是：在 Intel iPSC/2、8/16 处理器和一族 L 形 finite-element 问题上，MMD-subtree 的 factorization time 一致优于两个比较方案，且 mapping 本身只需 0.100–0.260 秒。[pdf:E12]（PDF 物理页 19，Table II）[pdf:E14]（PDF 物理页 22，Table V）但证据仍有两个缺口。第一，没有把每个处理器的预测 operation count、实际 busy time、等待时间和通信 bytes 对齐报告；第二，新方法与 subtree-to-subcube 的比较同时改变了 ordering，MMD 自身的 operation count 更低。[pdf:E07]（PDF 物理页 13，Table I）所以“flop-weight 准确刻画实际负载”在本文中得到的是间接经验支持，不是独立验证。

## § 10 — 最小复现实验

一周内最有价值的复现不是照搬 iPSC/2，而是在现代多核 CPU 或本机多进程模拟器上，固定数值 kernel 与 ordering，只验证“带权 elimination-tree partition 是否比现有映射更好地预测并改善真实执行”。

可执行方案如下：

1. 选 6–10 个可公开生成的 SPD sparse matrices，至少包含规则网格、L 形网格和人为构造的极不平衡 elimination tree；全部固定使用同一 MMD ordering。本文测试矩阵的精确生成细节不完整，因此复现应明确是 mechanism replication，而不是原表逐数字 reproduction。[pdf:E12]（PDF 物理页 19，测试问题说明）
2. 实现本文 Fig. 13–16：预测 `fcnt`、累积 `nodewt`、逐步切 branch、max/min heap 装箱、separator wrap。[pdf:E09]（PDF 物理页 15，Fig. 13）[pdf:E10]（PDF 物理页 16，Fig. 14–15）[pdf:E11]（PDF 物理页 17，Fig. 16）
3. 在 8 和 16 个 worker 上比较 sparse-wrap、本文 scheduler，以及一个只追求 predicted load balance、不保留子树局部性的 baseline。每个方案使用完全相同的数值代码、ordering 和数据布局。
4. 同时测量 predicted max/min load ratio、每个 worker 的实际 busy/idle time、factorization wall-clock、跨 worker message/bytes、separator 大小和 scheduler time；不要只报告总时间。
5. 若本文 scheduler 在不平衡树上稳定降低真实 makespan 或通信，同时 predicted load ratio 与实际 busy-time ratio相关，则支持核心机制；若预测负载更平衡但真实 makespan不降、等待或通信显著增加，则直接反驳最脆弱假设。

## § 11 — 最强反例设计

最强反例应让“flop weight 相同”与“真实代价相同”系统性脱钩，而不是仅换一个更大的矩阵。

可以构造两类子树，它们的 \(w_i\) 几乎相同，但结构不同：A 类由许多短而稀的列组成，任务启动和同步次数多；B 类由少数较稠密列组成，算术多集中在连续数据上。再让多个 A 类 branch 的更新在 separator 顶部汇合，造成同一批处理器间的高频小消息与同步热点。本文 greedy bin packing 只看 \(w_i\)，很可能把 A、B 判作等重；收紧 tolerance 还会继续切出更多 A 类 branch、扩大 separator，从而让预测平衡改善而真实执行恶化。论文自己的 Table IV 已显示阈值从 25% 收紧到 5% 并不带来单调加速，这为该攻击方向提供了迹象，但尚不是上述反例的直接证明。[pdf:E14]（PDF 物理页 22，Table IV）

反例实验应固定总 operation count、ordering、处理器数与数值 kernel，只系统改变 branch 内 nonzero 分布和跨 branch 更新扇出。若在相同 \(B_{\min}/B_{\max}\) 下，通信次数、idle time 与 makespan 可相差很大，并且 communication-aware cost model 能稳定击败本文 flop-only scheduler，就说明论文的核心代价模型不能普遍支撑其调度目标。

## § 12 — Follow-up Research Idea

**候选判断，不声称 novelty：**把 elimination-tree 的“依赖结构 + 静态代价”思想迁移为面向单卡 FPGA 的、同时感知片上存储与外存流量的 EMT sparse-solve scheduler，目标场景是大规模 VSC 场站网络在固定或缓慢变化拓扑下的重复网络求解。这里只迁移问题分解方式，不迁移本文的历史 CPU 性能结论。

（a）**未满足需求。** 大规模 VSC 场站 EMT 仿真要在固定步长 deadline 内重复求解稀疏网络方程；单卡 FPGA 的 DSP、BRAM/URAM、片外 DDR/HBM 带宽和路由资源都受限。仅按 flop count 分 task 可能让 processing elements 算术均衡，却让某个 memory channel 或 separator 更新成为瓶颈。这个需求是基于现代硬件约束的候选判断，不是本文原文 claim。

（b）**可能的研究价值。** 电气与实时仿真方向真正有说服力的结果应同时报告：数值误差与稳定性、最坏步长 latency、deadline miss、资源占用、外存流量、拓扑/工况覆盖，以及真实 FPGA 板卡上的可复现实验。若一个 scheduler 能在不牺牲数值正确性的前提下，给出跨多个 VSC 网络规模的确定性时延界或显著减少 worst-case latency，其价值高于只报告平均加速比。

（c）**可借鉴的相邻方法。** 从 sparse supernodal/multifrontal solver 借鉴 supernode 或 frontal task，从 DAG scheduling 借鉴 critical-path 与 heterogeneous cost，从 high-level synthesis 借鉴 resource-constrained modulo/dataflow scheduling；再把本文 elimination tree 的子树独立性作为 task graph 骨架。[pdf:E04]（PDF 物理页 4，子树独立性）[pdf:E10]（PDF 物理页 16，子树权重）与本文不同，新 cost 应至少包含计算周期、片上容量、跨 PE 边流量和 DDR/HBM burst，而不是只有 operation count。

（d）**第一个证伪实验。** 在同一块 FPGA、同一套定点或浮点 kernel、同一批冻结的 VSC 场站网络矩阵上，对比 flop-only elimination-tree scheduler 与 resource/communication-aware scheduler。逐步扩大网络规模并加入最坏 separator 扇出，测量每步 worst-case latency、外存 bytes、PE idle、BRAM/DSP 占用和数值误差。如果新 scheduler 在资源约束下不能降低 worst-case latency，或为了降低流量而导致频率、精度或可布线性恶化，则候选想法被证伪。

（e）**与本文的实质区别与外推边界。** 本文调度的是 Intel iPSC/2 上的 Cholesky 列，使用预测 flop 和处理器间 message/synchronization 语境，实验最多到 16 个处理器，并明确认为测试问题不足以有效扩到更高并行度。[pdf:E02]（PDF 物理页 2，平台语境）[pdf:E13]（PDF 物理页 21，规模边界）FPGA 方案调度的应是能映射到流水化 PE 与存储层级的 task，评价目标是确定性时延和资源/带宽可实现性。两者之间可迁移的是“从 elimination tree 提取依赖、按子树切 task、显式权衡 separator 通信”的抽象；不可迁移的是 Table II 的秒数、CPU 上的相对加速、wrap 在 iPSC/2 上的优越性，以及 flop weight 对 FPGA 周期的准确性。[pdf:E12]（PDF 物理页 19，Table II）[pdf:E15]（PDF 物理页 23，历史平台上的解释）在检索现代 FPGA EMT、稀疏 supernodal dataflow 和 resource-aware DAG scheduling 的相关工作之前，不能把该方向称为新颖。
