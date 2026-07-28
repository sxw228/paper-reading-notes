# Highly Parallel Sparse Cholesky Factorization

- 作者：John R. Gilbert；Robert Schreiber
- 出处：*SIAM Journal on Scientific and Statistical Computing*
- 年份：1992
- DOI：10.1137/0913067
- Zotero key：TUDTMNXF

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文问的是：面对非零结构任意的稀疏对称正定矩阵，能否在细粒度 data-parallel 机器上把 Cholesky factorization 做得既有足够并行度，又不被不规则通信和处理器空闲拖垮？作者在 Connection Machine CM-2 上比较两条路线：Router Cholesky 直接沿 elimination tree 暴露列依赖并行性；Grid Cholesky 则把稀疏问题分解成多个稠密主子矩阵，在二维 processor grid 上并行做 partial factorization。论文的核心主张不是“稀疏问题天然规则”，而是“填充图中 clique 的局部稠密性，可以成为规则并行 kernel 与任意稀疏结构之间的中介” [pdf:E01]（PDF 物理页 5，Abstract）。

这个问题重要，因为稀疏 factorization 的算术量不是唯一成本。CM-2 的通用 router 明显慢于 nearest-neighbor NEWS 与 scan；如果每层消元都做任意地址通信，理论并行度会被通信常数吞没。作者用实测参数说明，在该机器上无碰撞 `pset`、带碰撞 `pset` 和大量碰撞的 `pref` 成本差异很大，通用通信模式本身就是算法设计对象 [pdf:E05]（PDF 物理页 15，Table 1）。因此，论文真正处理的是“依赖图、数据布局、通信原语和 processor utilization 如何共同决定并行稀疏直接法的有效性能”，而不只是把串行 Cholesky 循环改写成并行循环。

对现代 FPGA EMT 而言，可迁移的联系只到这一层：网络矩阵的 elimination tree / supernode 结构可以帮助识别可并行前沿，规则的 dense或batched kernel可能比任意散射更新更适合硬件流水线。论文没有研究 EMT、FPGA、实时步长、开关事件、定点数、片上存储或现代稀疏格式，因此不能把 CM-2 的速度、复杂度常数或“任意结构都可高效”的实验判断直接外推到 FPGA EMT。

## § 2 — 前人工作与不足

论文把 prior work 分成几类。Gilbert 与 Hafsteinsson 的 PRAM 算法提供了理论上高效的 elimination-tree 并行路线，但其通信模式对 message-passing / data-parallel 实机过于不规则；George、Heath、Liu 与 Ng 以及 Zmijewski 代表了局部存储 MIMD multiprocessor 上的稀疏 Cholesky；Jess–Kees 研究如何重排以减少并行消元步数；O’Leary–Stewart 给出 dense matrix 的 wavefront/data-flow 思路；同时，vector supercomputer 与 workstation 上已经在使用 dense blocking / supernodal 技巧。以上是论文引用和概述的相关文献结论，不是本卡重新核验这些文献后的独立结论。

作者看到的不足有两层。第一层是算法模型与真实机器成本脱节：Router Cholesky 每个 elimination-tree level 都调用通用 router，虽有 \(O(h)\) 级并行步数，却把最昂贵的通信放进主导项。第二层是“有并行任务”不等于“处理器有效工作”：若一个操作只作用于少量非零元，其他与数据元素绑定的 virtual processors 会空闲。论文因此把目标从单纯减少依赖深度，改成同时减少昂贵通信、提高时间维度上的规则性，并让稀疏计算尽可能复用高效 dense kernel [pdf:E02]（PDF 物理页 8，§1.3）。

需要限定所谓“下界”。作者只证明或陈述：在其讨论的 left/right-looking 与 left/right-initiated 四种 Router Cholesky 亲缘变体中，所有版本至少需要 \(h\) 次 router operations，其中 \(h\) 是 elimination tree 高度 [pdf:E08]（PDF 物理页 22，§3.5）。这不是对所有稀疏 Cholesky、所有重排、所有并行机或所有 multifrontal 算法的普适通信下界。另一方面，Jess–Kees 的点式重排在 perfect elimination orderings 范围内最小化并行步数；本文的 block 版本以 simplicial clique 为单位，旨在保留同类步数优势并制造更大的稠密工作块 [pdf:E09]（PDF 物理页 23，§4.1.1）。

## § 3 — 重建作者的思考路径

可以从三个既有事实重建作者的路线。第一，Cholesky 的列依赖不是任意 DAG：filled graph 的 elimination tree 没有连接不同子树的 cross edges，因此一列只依赖其后代列；这允许同一高度的独立子树并行 [pdf:E04]（PDF 物理页 11，§2.2.1）。第二，若按“每个非零元一个 processor”直接执行列更新，所有跨列更新仍要经过通用 router，于是并行步数虽少，通信却处处位于 inner loop。第三，filled graph 是 chordal graph；当前可消元的 simplicial vertices 可以按相同 monotone neighborhood 聚成 clique，而 clique 与其邻域联合形成 dense frontal matrix。

于是一个自然推理链出现了：先用 elimination tree 找出依赖允许的并行层，再把同层、结构相同的 simplicial vertices 成组；对每组形成一个 maximal-clique principal submatrix；把多个这种 dense submatrices 同时放到二维 playing field；在 grid 内用 NEWS / copy-scan 完成大部分数值工作；只在 frontal matrix 搬入和 Schur complement 回写时使用通用 router。这样，昂贵通信从“每个消元步骤”退到“每个 clique-tree stage 的边界”，processor 也能在多个 frontal problems 之间重新分配，而不是永久绑定到整个 \(L\) 的某个非零元。

这条思考路径还带出 block Jess–Kees reordering：每一 major step 同时删除所有 simplicial vertices，并把 indistinguishable vertices 连续编号为 simplicial cliques；这些 cliques 再组成高度为 \(h\) 的 clique tree [pdf:E10]（PDF 物理页 24，Reorder procedure）。这里“block”并非为了改变数值答案，而是为了把图上的依赖等价类变成适合 dense partial factorization 的硬件友好工作单元。

## § 4 — 核心 Intuition

Grid Cholesky 的直觉是：不要让任意稀疏更新持续穿过慢速通用网络，而要借助 chordal filled graph 中天然形成的 cliques，把大部分工作变成规则的 dense frontal kernels。Elimination tree / clique tree 决定哪些 fronts 可以同时做，二维 playing field 负责高频局部通信，router 只负责 stage 边界的数据搬运。它成功的关键不是消除了稀疏性，而是把不规则性限制在较低频的调度与汇合层。

## § 5 — 具体方法与完整 Pipeline

**输入与前置条件。** 输入是实对称正定稀疏矩阵 \(A\)。作者假定已经完成减少 fill / operation count 的对称重排，并已通过 symbolic factorization 得到 \(L\) 的非零结构；这些前处理不计入本文数值 factorization 的时间 [pdf:E03]（PDF 物理页 9，§2.1）。论文的 pilot implementation 还依赖 CM-2 的 pvar、virtual processor ratio、NEWS、scan 和 router 原语；没有报告定点数、FPGA 资源或实时执行。

**Pipeline。**

1. 从 filled graph \(G^*(A)=G(L+L^T)\) 构造 elimination tree。若顶点 \(u\) 有编号更大的邻居，其 parent 是其中编号最小者；这一结构把列依赖压缩成树祖先关系 [pdf:E04]（PDF 物理页 11，§2.2.1）。
2. 反复找出当前图中的全部 simplicial vertices。同一 simplicial clique 内的顶点连续编号，同一轮被删除的 cliques 共享一个 stage；以最低 stage 的相邻 clique 为 parent 建 clique tree [pdf:E10]（PDF 物理页 24，§4.1.1）。
3. 对某个 simplicial clique \(C\)，令 \(K=C\cup\operatorname{adj}(C)\)。形成 principal frontal matrix \(A(K,K)\)，并按 \(C\) 与其邻域分成 \(X_C,E_C,Y_C\) 三块。
4. 对每个 stage，把该层所有 \(A(K,K)\) 搬到二维 playing field，彼此作为多个独立 dense subproblems。把 \(Y_C\) 清零，在没有 pivoting 的条件下做 \(\gamma_C=|C|\) 步并行 Gaussian elimination，得到 \(X_C\) 的 factor、更新后的 \(E_C\) 与 Schur complement；然后把已完成列和累积更新写回 sparse matrix storage [pdf:E11]（PDF 物理页 25，§4.1.2）。
5. dense partial factorization 的候选 kernel 有 systolic wavefront 和 rank-1 update。实际选择 rank-1：每一步取 pivot reciprocal、按列广播 pivot row、计算 multipliers、按行广播 multipliers，再并行 multiply-subtract；stage 末再把 LU 形式转换回 Cholesky 形式 [pdf:E12]（PDF 物理页 27，§4.2.2）。
6. 不同 frontal matrices 需要装入一个边长为二次幂的 rectangular playing field。作者承认这是二维 bin packing，最优解通常 NP-hard；实验只使用 sequential symbolic phase 中的 “first-fit by levels” heuristic [pdf:E14]（PDF 物理页 32，§4.3.2–§4.4）。

以论文的 \(63\times63\) 五点 Laplacian 为例，nested dissection 后得到 \(n=3969\) 的 SPD matrix。symbolic phase 形成 11 个 clique-tree stages；数值 phase 每个 stage 将相应 fronts 打包进固定 \(256\times512\) playing field，在 8192 个 processors 上按上述 rank-1 kernel 并行处理，再把 Schur updates 汇回 matrix storage [pdf:E15]（PDF 物理页 34，§4.5）[pdf:E16]（PDF 物理页 35，§4.5）。

## § 6 — 核心数学推导（无形式化数学则跳过）

Cholesky 的基础是：对实对称正定 \(A\)，存在对角线为正的唯一下三角矩阵 \(L\)，使

\[
A=LL^T.
\]

解 \(Ax=b\) 可化为 \(Ly=b\) 与 \(L^Tx=y\)。对称 permutation \(P\) 改变 elimination order，从而改变 fill 与工作量；本文假定这个 order 与 symbolic structure 已经给定 [pdf:E03]（PDF 物理页 9，§2.1）。

**Elimination tree 的并行含义。** 若 \(L_{vu}\neq0\) 且 \(u<v\)，则 \(v\) 位于 \(u\) 到 root 的唯一单调路径上。因此，不同子树之间没有 cross edge，一列只依赖其 descendants。令 tree height 为 \(h\)，Router Cholesky 逐高度执行，stage 数为 \(h+1\)。论文的机器模型把一次 stage 写成

\[
T_{\text{Router}}
=(c_1\rho+c_2\sigma+c_3)\,\phi\mu h,
\]

其中 \(\rho\) 是 route 相对 floating-point time，\(\sigma\) 是 scan 相对 floating-point time，\(\mu\) 随 virtual processor ratio \(v=\lceil\eta(L)/p\rceil\) 增长，\(p\) 是物理 processors 数；实作估计 \(c_1\approx5,c_2\approx2,c_3\approx4\)，因此 router 项主导 [pdf:E06]（PDF 物理页 20，§3.3）。对 nested-dissection 的 \(k\times k\) 五点网格，\(n=k^2\)、\(h=O(k)\)、\(\eta(L)=O(k^2\log k)\)、算术量 \(O(k^3)\)，Router Cholesky time 为 \(O(\rho k^3\log k/p)\)，按作者定义的 performance 为 \(O(p/\log k)\) [pdf:E07]（PDF 物理页 21，§3.3）。

**Frontal block 与 Schur complement。** 对 simplicial clique \(C\)，记 \(\gamma_C=|C|\)、\(\sigma_C=|\operatorname{adj}(C)|\)，则

\[
A(K,K)=
\begin{pmatrix}
X_C & E_C\\
E_C^T & Y_C
\end{pmatrix},
\qquad K=C\cup\operatorname{adj}(C).
\]

若 \(X_C=L_CL_C^T\)，partial elimination 得到

\[
E'_C=L_C^{-1}E_C,\qquad
Y'_C=-E_C^T X_C^{-1}E_C,
\]

再执行 \(A(\operatorname{adj}(C),\operatorname{adj}(C))\leftarrow A(\operatorname{adj}(C),\operatorname{adj}(C))+Y'_C\) [pdf:E11]（PDF 物理页 25，§4.1.2）。直观上，\(C\) 内部变量被消去，其对尚未消去邻域的影响被压缩为一个 dense Schur update。

**Grid 的复杂度。** 对同一二维网格模型，matrix storage 的 VP ratio 为 \(O(k^2\log k/p)\)，其 router 时间为 \(O(k^2\log^2k\,\rho/p)\)；playing field VP ratio 为 \(O(k^2/p)\)，各 stage 最大 clique size 之和为 \(O(k)\)，其 scan 主导时间为 \(O(k^3\sigma/p)\)。因此

\[
T_{\text{Grid}}
=O\!\left(
\frac{k^2\log^2k}{p}\rho
+\frac{k^3}{p}\sigma
\right).
\]

这使 \(\rho\) 只出现在低阶项，而作者定义的 performance 恢复为 \(O(p)\) [pdf:E15]（PDF 物理页 34，§4.4）。但这不是无条件的 work/span 最优性结论：它依赖二维有限元网格、nested dissection、给定的 CM communication model、足够可打包的 fronts，以及 \(p,k\) 的特定伸缩关系。

## § 7 — 实验设计与结论

**问题一：机器参数模型能否预测 Router Cholesky？** 作者先在 CM-2 上测量 memory、floating point、NEWS、scan 与多种 router pattern 的单位成本 [pdf:E05]（PDF 物理页 15，Table 1），再对 \(50\times50\) 五点网格做 Router Cholesky。该矩阵为 \(2500\times2500\)，原三角存储计 7400 个 nonzeros；factor 有 48608 个 nonzeros，elimination tree height 为 144，算术量为 1,734,724。8192-processor CM-2 上实测 53 s，其中约 41 s 来自 `pref` / `pset`；模型预测 router 39 s、其他 1.5 s。答案是：模型对 router 主导项拟合较好，但对剩余时间拟合差，作者怀疑 square root、pointer movement 与 I/O 影响了测量 [pdf:E07]（PDF 物理页 21，§3.4）[pdf:E08]（PDF 物理页 22，§3.5）。

**问题二：dense partial factorization 应选 systolic 还是 rank-1？** 作者分别测量 dense kernel 内各操作占比。rank-1 complete factorization 中 copy scans 占 79.7%，NEWS 5.5%，multiply 2.7%，divide 7.1%，multiply-subtract 4.8%；对二维模型，平均 Schur complement size 约为 clique size 的 4 倍，rank-1 在 step count 上有约 11:1 优势，足以抵消 scan 比 NEWS 慢 3–4 倍的劣势 [pdf:E13]（PDF 物理页 28，§4.2.2–§4.2.3）。答案是：在这台 CM-2 和 partial factorization workload 上选 rank-1，但这不是跨架构结论。

**问题三：Grid Cholesky 是否把昂贵 router 从主导项移走，并且模型是否仍准确？** \(63\times63\) 五点 Laplacian 经 nested dissection 后有 3969 columns、11781 original nonzeros、85416 factor nonzeros、11 stages 和 3,658,949 arithmetic operations [pdf:E15]（PDF 物理页 34，§4.5）。在 8192 processors、两个 VP sets 均为 VP ratio 16 时，总时间 6.13 s：playing field 4.09 s，其中 copy scans 3.12 s、token moves 0.15 s、local computation 0.82 s；matrix storage 2.04 s。模型预测 playing field 4.0 s，matrix storage 1.5–4.7 s；测得 move-in、factor-on-grid、update-back 分别占 12%、67%、21%。答案是：这个样例上代码不再 router-bound，模型足以支持架构选择 [pdf:E16]（PDF 物理页 35，§4.5–§4.6）。

**问题四：更快是否等于高效？** 不是。playing field 的“useful flop”效率估算仅 10.3%，损失来自计算 dense subproblem 两个对称半区、固定 playing-field size、二次幂 padding、稀疏发生的 divide/multiply 以及消元推进后的 processor idling；若逐 stage 改变 VP ratio，作者模型推算 playing-field useful flop rate 可达单个 dense factorization 的约 192%，但这是分析结果，不是实测 [pdf:E17]（PDF 物理页 36，§4.6）。整个小样例中 Grid 约比 Router 快 20 倍，却只有 0.597 MFLOPS（8K processors；线性折算 64K 为 4.77 MFLOPS），作者明确承认 pilot implementation 仍不具成本竞争力 [pdf:E18]（PDF 物理页 37，§5）。

实验边界同样明确：只有两个规则五点网格样例，均用 nested dissection；没有真实任意结构矩阵集合、数值稳定性扰动、pivoting、内存容量极限、能耗或端到端 symbolic preprocessing 时间。因此“任意结构稀疏问题可接近 dense kernel 效率”主要由结构论证、复杂度模型和一个小规模 pilot 支撑，不能理解为广泛 benchmark 已证实。

## § 8 — Take-aways

**5 句话。**
1. Elimination tree 揭示了稀疏 Cholesky 的依赖并行性，但只按 tree level 并行并不能自动得到好性能。
2. Router Cholesky 的失败说明，真实机器上昂贵通信原语进入主导项时，漂亮的 PRAM 复杂度不足以指导实现。
3. Grid Cholesky 通过 simplicial cliques / frontal matrices 把多数不规则稀疏工作变成多个规则 dense partial factorizations。
4. 在论文的 CM-2 小样例上，这一改写把 router 从主导瓶颈移开并取得约 20 倍相对加速，但绝对效率仍很低。
5. 可迁移的成果是“依赖树调度 + dense blocking + communication-aware cost model”，不是 1992 年硬件数字本身。

**3 句话。**
1. 稀疏并行直接法的关键不是最大化瞬时并行任务数，而是把高频通信变成规则、局部、可复用的 kernel。
2. Elimination/clique tree 给出合法并行与 front 汇合关系，playing field 承担 dense 计算，router 只处理 stage 边界。
3. 论文证明了这条设计路线值得做，却没有证明它能无条件跨矩阵、跨架构或跨数值问题高效。

**1 句话。**
把不规则性限制在低频调度层，把算术密集部分变成可批处理 dense fronts，是本文最持久的思想。

## § 9 — 最脆弱的假设

最脆弱、失败代价最大的假设是：待解矩阵适合无 pivoting 的 SPD Cholesky，即 \(A\) 始终实对称正定。论文从这一条件开始，并在 Grid kernel 中明确执行 Gaussian elimination without pivoting [pdf:E03]（PDF 物理页 9，§2.1）[pdf:E11]（PDF 物理页 25，§4.1.2）。若矩阵是非对称或不定的，唯一 \(A=LL^T\) 分解、filled chordal graph 上的依赖性质以及不带 pivot 的稳定执行都不再直接成立，核心 pipeline 必须换成 LU、\(LDL^T\) 或带 pivoting 的方法；pivoting 还可能动态改变结构和通信。

这对 EMT 迁移尤其致命。基于 modified nodal analysis 的网络方程可能因受控源、接口变量、约束和离散化而非 SPD；开关事件还可能改变结构。论文没有给出这类矩阵的证据。其次，作者把 ordering、symbolic factorization 与 clique-tree generation 放在数值计时之外，pilot 甚至顺序执行这些前处理 [pdf:E20]（PDF 物理页 39，§5）。因此，即使某个 EMT 子问题可化为 SPD，能否复用 symbolic structure 仍需另行验证。

## § 10 — 最小复现实验

一周内不必复刻 CM-2；应复现“clique batching 能否把不规则通信移出主导项”这一可迁移 claim。

1. 数据：生成 \(31\times31\)、\(63\times63\)、\(127\times127\) 五点 Laplacian SPD matrices，并增加一组同规模、front-size 分布高度不均匀的 SPD graph matrices。固定 nested dissection ordering，记录 \(L\) 的 fill、elimination tree、supernodes / simplicial cliques。
2. 实现：做两个数值 kernel。A 为 column-oriented left-looking Cholesky，用 scatter/gather 累积更新，代表 Router 风格；B 为 supernodal/multifrontal 版本，把同一 tree frontier 的 dense fronts batched 到 GPU 或多核 CPU，并显式记录 front packing、搬运和 Schur update。
3. 测量：总时间、算术时间、随机访问/搬运字节、每层 active fronts、batch occupancy、padding 比例，以及 numerical residual \(\|A-LL^T\|/\|A\|\)。不要用总 FLOPS 单独判定。
4. 支持条件：随网格增大，B 的 irregular-transfer 占比下降，dense-kernel 占比上升；同等 residual 下，B 对 A 的优势随 front size 增长，并能由参数化 cost model 预测数量级。
5. 反驳条件：packing / Schur 汇合一直主导，front heterogeneity 使 occupancy 持续很低，或模型必须逐矩阵重新拟合才能解释结果。这样的结果说明论文机制只适合规则 separator 结构，不能作为通用硬件映射原则。

这个实验只能验证结构与通信机制，不能复现论文的 CM-2 秒数，也不能证明 FPGA EMT 实时性。

## § 11 — 最强反例设计

最强反例不是简单换一个更大的矩阵，而是构造仍为 SPD、但系统性破坏 Grid Cholesky 摊销条件的 filled graphs：clique tree 每层包含大量尺寸互不相容的 fronts，边长恰好跨过二次幂边界；separator 较大而可消元 \(C\) 很小，使 \(\sigma_C\gg\gamma_C\)；同时让多个 fronts 的 Schur updates 高度重叠。这样每个 front 只有很少 rank-1 steps，却占用大块 playing field，padding、bin packing 和 update collisions 同时恶化。

用相同非零数、相近算术量但不同 front-size distribution 的矩阵成对测试 Router-style、Grid-style 与一个成熟 multifrontal baseline。若 Grid 的 router / transfer 占比重新成为主导，useful occupancy 随规模下降，且 fixed-size playing field 的速度低于直接 sparse schedule，那么“把任意稀疏问题系统地分成 dense submatrices 就能接近 dense efficiency”的广义解释被推翻。论文自己已经暴露了这个攻击面：二维 packing 使用 heuristic，fixed field 与 power-of-two dimensions 会造成浪费，消元推进还会让 processors fall idle [pdf:E14]（PDF 物理页 32，§4.3.2）[pdf:E17]（PDF 物理页 36，§4.6）。

对 FPGA EMT 的额外压力测试应把矩阵改为实际 MNA 形式并加入 topology event。若需要 pivoting 或 symbolic structure 频繁变化，直接应用本文 Cholesky pipeline 会在数值层先失效；这不是硬件优化能补救的问题。

## § 12 — Follow-up Research Idea

**候选判断，不声称 novelty：**面向大规模 VSC 场站网络与单卡片上资源有限的矛盾，研究“资源有界、事件感知的 elimination-tree streaming solver”。目标不是把 Grid Cholesky 原样搬到 FPGA，而是把它的依赖树与 dense-front 思想改写为一个可证伪的硬件调度问题：在固定 DSP/BRAM/URAM 和固定实时 deadline 下，联合选择 ordering、front 切分、片上驻留、跨 stage 流式传输与并发窗口；数值 kernel 根据实际 EMT 方程选择 Cholesky、\(LDL^T\) 或静态-pivot LU，而不是预设 SPD。

（a）**未满足需求。** 大型 VSC 场站使网络方程和 converter interface 数量增长，而单卡资源、外存带宽与每步时限固定；简单“每个非零元一个处理单元”会浪费资源，单个大 dense kernel 又装不下。论文已经指出 clique tree 可表达 partial factorizations 的 precedence，固定一层一调度并非唯一方案；也提出 varying VP ratio 与 out-of-main-memory scheduling 方向 [pdf:E19]（PDF 物理页 38，§5）[pdf:E20]（PDF 物理页 39，§5）。

（b）**潜在研究价值。** 若能在真实 EMT matrices 上证明：resource-bounded streaming schedule 在保持数值稳定和事件正确性的同时，减少 off-chip traffic 并稳定满足 deadline，它提供的是“结构、数值方法与硬件资源共同优化”的系统价值，而不是只换一个应用。电气与实时仿真领域会更看重真实工况、误差、最坏步时、资源和可复现实现，而不是 CM-2 式平均 MFLOPS。

（c）**可借鉴工具。** 可借鉴 modern multifrontal / supernodal symbolic analysis、tree-DAG list scheduling、bin packing、roofline / communication model，以及 FPGA HLS dataflow。本文可提供 clique-tree precedence 和 dense-front decomposition 的历史依据，但其 CM-2 cost parameters 不能直接使用。

（d）**第一个证伪实验。** 选一组可公开或可复现的多 VSC 场站 EMT matrices，至少包含固定拓扑与开关事件两类；在同一 FPGA resource cap 下比较 baseline sparse solver、静态 supernodal schedule 和候选 streaming schedule。预先规定 pass gate：最坏步时满足实时 deadline，残差与 EMT 波形误差不劣于 baseline，且 off-chip bytes/step 明显下降。只要 event 后的 symbolic / pivot overhead、front spill 或数值不稳定使最坏步时超限，候选方向即被证伪。

（e）**与本文的实质区别。** 本文在 CM-2 上假定 SPD、预先完成 symbolic structure，并用大量 virtual processors 并行摆放 fronts；候选问题则把单 FPGA 的有限片上资源、外存流、实时最坏时延、非 SPD 可能性与 topology event 纳入问题定义。它继承的是“tree-guided dense fronts”这一机制，不继承历史机器的性能结论。相关现代 FPGA sparse solver 与 EMT 文献尚未在本任务中充分检索，因此这里仅是研究候选，不构成 novelty 声明。
