# Hyper-optimized tensor network contraction

**作者：** Johnnie Gray；Stefanos Kourtis  
**出处：** Quantum  
**年份：** 2021  
**DOI：** 10.22331/q-2021-03-15-410  
**Zotero key：** KM5UI4TW  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的是一个很朴素、但代价呈指数放大的问题：给定任意几何结构的 tensor network，应该按什么顺序两两收缩，才能把总运算量和最大中间 tensor 控制到最低？同一个网络换一条 contraction path，数学结果不变，但中间 tensor 的 rank 会完全不同；一次不合适的合并可能让后续计算量和内存成指数增长。作者把这一问题直接表述为 contraction tree 的搜索，并分别用 contraction width $W$ 描述峰值空间、用 contraction cost $C$ 描述所有收缩的总计算量，而不是只看最昂贵的一步 [pdf:E03]（PDF 物理页 3，Eq. 1–5）[pdf:E04]（PDF 物理页 4，Eq. 6–7）。

它重要的原因不只在量子电路。论文列出的对象包括量子多体系统、统计物理、weighted model counting、图模型推断、QAOA 和随机量子电路；一般结构的精确 tensor network contraction 至少是 #P-hard，因此可行性常常取决于能否找到足够好的路径 [pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）。在 Google Sycamore 场景中，作者进一步把路径质量换算为对经典模拟成本的数量级改变，报告相对原始估算超过 $10{,}000\times$ 的加速 [pdf:E18]（PDF 物理页 19，Eq. 23 与 Summary）。这说明 contraction-path optimizer 不是一个可忽略的预处理器，而可能改变“某个问题是否算得动”的结论。

## § 2 — 前人工作与不足

论文之前已经有几条成熟路线。Optimal 通过 dynamic programming 搜索连通子图，能得到最优总 cost 或 width，但组合爆炸，只适合小网络。QuickBB 和 FlowCutter 先求 tensor network 的 line graph 的 tree decomposition，再把 edge ordering 转成 contraction tree；它们是 anytime 算法，却不考虑 edge weight，而且主要约束 leading cost，不保证总 cost 最优。此前也已有基于 community detection 的 contraction 思路；针对二维规则结构，TEBD-style boundary contraction、qFlex/PEPs 等手工或几何专用路径也很有效 [pdf:E04]（PDF 物理页 4，Table 1）[pdf:E10]（PDF 物理页 11，Fig. 5–6 与 Sec. 4.3）。

不足并非“前人没想到优化路径”，而是三种结构性错配。第一，任意网络没有单一几何先验：random regular graph、planar graph、grid 和量子电路偏好的 heuristic 不同。第二，treewidth 或最大一步只近似真实目标；总 FLOPs 是整棵 tree 上各节点 cost 的和。第三，bond dimension、hyperedge、COPY tensor 和可利用的 sparsity 会改变有效拓扑，而部分 line-graph 方法看不见这些信息。论文的 Table 1 清楚区分了各方法能否处理 edge weight、hyperedge，以及优化 total cost 还是 leading cost [pdf:E04]（PDF 物理页 4，Table 1）。因此作者要解决的不是发明一个永远最好的 heuristic，而是让搜索过程自动选择适合当前网络的 tree generator 和参数。

## § 3 — 重建作者的思考路径

可以从论文之前已有的事实逆向走到这个方案。首先，pairwise contraction 天然形成 rooted binary tree；于是 path search 可以统一成“找一棵低 congestion 的 tree”，不同传统算法只是用不同方式生成候选 tree。其次，图划分、community detection、greedy merge 和 tree decomposition 分别擅长看全局 separator、局部合并代价或 line-graph width，它们的归纳偏置互补，不必强行押注一个算法。再次，$W$ 与 $C$ 对 path 极敏感，因此同一 heuristic 只要加入随机扰动并重复采样，就可能从偶然的低成本 basin 中获益。最后，若 heuristic 参数确实决定 tree 形状，就可以把“选方法、调参数、选随机种子”统一成一个黑盒优化问题，以整棵 tree 的 $W$ 或 $C$ 作为反馈。

这条路径导出论文的两层设计：下层用 agglomerative、divisive、community 和 line-graph 方法生成 contraction tree；上层用 stochastic Bayesian optimization 选择算法参数并持续建议更有希望的候选。作者还在进入全局搜索前反复执行结构简化，因为若 diagonal、rank、column 或 exact split 能先消掉指数因素，后面的 optimizer 就是在一个真正更小的问题上工作 [pdf:E02]（PDF 物理页 2，Introduction 的两项核心思路）[pdf:E07]（PDF 物理页 8，Sec. 3.7 与 Eq. 11–13）。

## § 4 — 核心 Intuition

核心 intuition 是：不要试图为所有 tensor network 找一个固定的“最佳规则”，而要把多种有不同偏好的 contraction-tree 生成器当成候选族，再直接用最终整棵 tree 的总成本反馈来选择方法和参数。随机化负责探索不同 tree 形状，Bayesian optimization 负责把有限搜索预算集中到有希望的区域。结构简化则在搜索前改变有效网络，使 optimizer 面对的是同一 contraction 结果的更低复杂度表示。

## § 5 — 具体方法与完整 Pipeline

以计算一个 Sycamore 随机量子电路的单个输出 amplitude $c_x$ 为例，完整 pipeline 如下。

1. **构造网络。** 把输入/输出 basis state、单量子比特 gate 和双量子比特 gate 分别变成 rank-1、rank-2 和 rank-4 tensors，tensor leg 表示量子线路上的 index。目标 scalar 是 $c_x=\langle x|U_d\cdots U_1|0^{\otimes N}\rangle$ [pdf:E12]（PDF 物理页 13，Eq. 19 与 Sec. 4.6）。
2. **选择 exact gate representation。** 双比特 gate 可保持 rank-4，也可通过 SVD 做 spatial decomposition；若允许交换两个 qubit 的 index，还可做 swapped decomposition。论文默认只在 exact bond dimension $\chi<4$ 时分解；主 Sycamore-53 结果不近似分解 fSim gate，以保持 perfect fidelity [pdf:E13]（PDF 物理页 14，Eq. 20–21 与 Sec. 4.6.1）。
3. **迭代简化。** 按 antidiagonal-gauging、diagonal-reduction、column-reduction、rank-simplification、split-simplification 的顺序循环，直到没有操作可做；涉及“等于零”的判断使用相对精度 $10^{-12}$。这些步骤可以把相等 index 合成 hyperedge、吸收不增 rank 的 tensor，或做 exact low-rank split [pdf:E07]（PDF 物理页 8，Sec. 3.7）[pdf:E08]（PDF 物理页 9，Sec. 3.7 结尾）。
4. **生成候选 contraction trees。** Hyper-Greedy 从叶到根选择局部 contraction；Hyper-GN 从 community hierarchy 反向得到路径；Hyper-Par 从整图开始做 recursive hypergraph partition，再用 Optimal 或 Hyper-Greedy 填补小 subtree。Hyper-Par 的关键自由度包括 partition 数 $k$、imbalance $\epsilon$ 和停止划分的 cutoff，并且能直接利用 hyperedge 与 edge weight [pdf:E05]（PDF 物理页 6，Eq. 9–10 与 Sec. 3.4–3.5）[pdf:E06]（PDF 物理页 7，Sec. 3.5–3.6）。
5. **hyper-optimize。** 对 edge weights 加噪声，或在 Hyper-Greedy 中按 Boltzmann probability 随机采样；用 Gaussian-process Bayesian optimization 建模参数到目标 $W$ 或 $C$ 的关系，建议下一批参数。每次都实际构造完整 tree、计算整棵 tree 的目标，再保留当前最佳路径 [pdf:E06]（PDF 物理页 7，Sec. 3.6）。
6. **按内存预算 slicing 并执行。** 若最佳 tree 的 width 仍超内存，则选择一组 indices 放到最外层求和；每个固定 index assignment 形成独立 contraction，可并行执行。作者还把 sliced cost 放回 Bayesian optimization，使搜索直接针对目标 width $W_s$ 找适合 slicing 的 tree，而不是把 slicing 仅作为事后补丁 [pdf:E15]（PDF 物理页 16，Sec. 4.7.1）[pdf:E16]（PDF 物理页 17，Fig. 10）。
7. **输出结果。** 按找到的 tree 和 slices 收缩 tensors，再对各 slice 求和，得到 amplitude；只要网络结构不变，这条 path 可以复用于不同 tensor entries，例如不同输出 bitstring。

论文不是 FPGA 论文，也没有报告固定点数值表示、RTL、片上存储布局、流水线时序或 FPGA 实时步长。实际执行平台是 quimb + JAX 编译后在 NVIDIA Quadro P2000 GPU 上运行；因此这里能提取的是算法依赖图、并行粒度与内存—FLOPs 权衡，不能外推成 FPGA 资源或时序结论 [pdf:E17]（PDF 物理页 18，Table 2）。

## § 6 — 核心数学推导（无形式化数学则跳过）

先从 tree 表示开始。每个原始 tensor 是一片叶子；内部节点 $v$ 表示把左右子树的有效 tensors 收缩。若 $s_v$ 表示该有效 tensor 仍暴露在外的 indices，则内部节点满足

$$
s_v=s_{l(v)}\oplus s_{r(v)},
$$

其中 symmetric difference 会删掉左右两边共有、因收缩而消失的 indices [pdf:E03]（PDF 物理页 3，Eq. 1）。这条式子的工程含义是：tree 中每条边携带的有效 tensor 大小，只由跨过该子树边界的 indices 决定。

峰值空间用 contraction width 表示：

$$
W=\max_{v\in V_B}\sum_{e\in s_v}\log_2 w(e),
$$

所以最大中间 tensor 的元素数量近似为 $2^W$；对 qubit 或 Boolean index，$w(e)=2$，于是 $W$ 就是最大暴露 index 数 [pdf:E03]（PDF 物理页 3，Eq. 2–4）。时间目标则把所有内部节点的计算量相加：

$$
C(B,S)=\sum_{v\in V_B}2^{\operatorname{vc}(B,S,v)},\qquad
\operatorname{vc}(B,S,v)=\sum_{e\in s_{l(v)}\cup s_{r(v)}}\log_2 w(e).
$$

这里 vertex congestion 统计一次 pairwise contraction 实际碰到的全部 indices。实数 tensor 的 FLOPs 是 $2C$，复数 tensor 是 $8C$；因此最小 $W$ 的 tree 与最小 $C$ 的 tree 不必相同 [pdf:E04]（PDF 物理页 4，Eq. 5–7 附近说明）。

Hyper-Greedy 用局部 score

$$
\operatorname{cost}(T_i,T_j)=\operatorname{size}(T_k)-\alpha[\operatorname{size}(T_i)+\operatorname{size}(T_j)]
$$

评价把 $T_i,T_j$ 收缩成 $T_k$ 的动作，再按

$$
p(T_i,T_j)\propto \exp[-\operatorname{cost}(T_i,T_j)/\tau]
$$

采样。$\alpha=1$ 偏向立即减少内存，$\alpha=0$ 偏向较低输出 rank；温度 $\tau$ 决定是否愿意探索暂时看起来较差的动作 [pdf:E05]（PDF 物理页 6，Eq. 9–10）。重要的是，局部 score 只负责生成 tree，最终优劣仍由全局 $W$ 或 $C$ 判断。

Hyper-Par 则把内部节点生成改写成 subgraph bipartition。由于一次 contraction 的 cost 包含 subgraph 外部 indices 和跨 partition 的 indices，而前者不随 partition 改变，减少 cut weight 就能降低当前 contraction cost；imbalance $\epsilon$ 控制两边规模，避免一味追求 min-cut 导致后续 tree 变差 [pdf:E06]（PDF 物理页 7，Sec. 3.5）。最后，slicing 把选定 indices 移到最外层求和，产生 $d_{\text{sliced}}=\prod_{e\in s_{\text{sliced}}}w(e)$ 个独立子任务；它降低每个任务的 $W_s$，但会因重复计算使总 sliced cost $C_s$ 上升 [pdf:E15]（PDF 物理页 16，Sec. 4.7.1）。

## § 7 — 实验设计与结论

**问题 1：不同 topology 是否真的需要不同 optimizer？** 作者对 random $k$-regular graphs（$k=3,4,5$）每个规模生成 100 个实例，每个 heuristic 搜索 5 分钟，并与最长运行 24 小时的 Optimal 比较。随着规模增加，Hyper-Par 在这些非平面随机图上最好，且对 total cost 的优势比对 width 更明显 [pdf:E08]（PDF 物理页 9，Sec. 4.1 设置）[pdf:E09]（PDF 物理页 10，Fig. 4）。但在 35,162 个 random planar graph 实例上，方法差距较小，Hyper-Greedy 反而最好；这支持“没有单一固定 heuristic 适合所有 geometry”，也限制了“Hyper-Par 总是最好”的外推 [pdf:E10]（PDF 物理页 11，Fig. 5 与 Sec. 4.2）。

**问题 2：方法能否处理真实非规则应用？** 在 100 个 Model Counting 2020 的 private weighted model counting 实例上，结构简化直接把 63 个实例化成 scalar；余下 37 个用 greedy 与 KaHyPar 的 hyper-optimizer 搜索 64 次。99 个实例最终求解，论文对比的竞赛最佳成绩为 69；其中与竞赛 solver 重合的 69 个结果还用 ADDMC 复核 [pdf:E11]（PDF 物理页 12，Eq. 14 与 Sec. 4.4）。这组结果同时验证了 simplification 与 hypergraph-native contraction，但不能把 99/100 全部归功于 path optimizer。

**问题 3：规模增加时 QAOA energy contraction 是否仍可控？** 作者在 random 3-regular graph 上计算 $p$-layer QAOA 的所有局部 energy terms，并在每个 $N,p$ 上平均 10 个实例。到 $p=4$，整个测试范围内 $W_{\max}\lesssim28$、$C_{\text{total}}\lesssim10^{10}$；例如 4-core CPU 上 $N=54,p=4$ 为秒级。$p=5$ 在 $N=40$–120 出现显著峰值，作者把它归因于长度不超过 $p$ 的 cycle 增加 tensor network 复杂度 [pdf:E12]（PDF 物理页 13，Fig. 8 与 Sec. 4.5）。这说明效果受 problem geometry 的非单调结构支配，并非只随 $N$ 平滑增长。

**问题 4：对随机量子电路，改进是否落实到真实执行？** 在 Rectangular-7×7、Bristlecone-70、Sycamore-53 上，各 optimizer 每个深度搜索 1 小时；Fig. 9 中 Hyper-Par 总体最好，尤其在 Sycamore 上可在相近 width 下找到更低 total cost [pdf:E14]（PDF 物理页 15，Sec. 4.6.4）[pdf:E15]（PDF 物理页 16，Fig. 9）。随后作者固定 $W_s=27$，用 quimb/JAX 在 5 GB Quadro P2000 上执行：例如 Bristlecone-70 $(1+40+1)$ 单 amplitude 报告 $277$ s、$C_s=3.14\times10^{13}$、slicing overhead $1.65\times$；Sycamore-53 $(m=20)$ 的时间为外推值 $9.74\times10^{10}$ s、$C_s=3.10\times10^{22}$、overhead $6410\times$ [pdf:E17]（PDF 物理页 18，Table 2）。所以 path 的低理论 cost 能转成高 GPU FLOPs efficiency，但极深 Sycamore 仍被 memory-driven slicing overhead 主导。

**问题 5：$10{,}000\times$ 结论如何得到？** 对 Sycamore-53*，作者取 $W_s=32$、$N_f=6$、$C_s=10^{20.17}$；为在 wavefunction fidelity $g\sim0.5$ 下生成 $M=10^6$、目标 fidelity $f=0.002$ 的样本，需要 $Mf/g=4000$ 次 contraction。按 Summit 的 281 petaFLOPs 上界估算为 195 天，按 Table 2 的 55% efficiency 为 241 天，两者相对文献 [45] 的原始经典估算都超过 $10{,}000\times$ 加速 [pdf:E18]（PDF 物理页 19，Eq. 23）。这是跨系统的估算，不是论文实际跑完的 195/241 天 wall-clock 实验。

## § 8 — Take-aways

**5 句话：**

1. 任意 tensor network 的 contraction path 可以统一表示为 rooted binary tree，并用峰值 width $W$ 和总 cost $C$ 分别衡量空间与时间。
2. Hyper-Greedy、Hyper-GN、Hyper-Par 等方法的价值不在某个固定 heuristic，而在随机采样后用 Bayesian optimization 直接按完整 tree 的目标反馈调参。
3. exact 结构简化会改变有效 topology，因此与 path search 同等重要，model counting 的 100 个实例中有 63 个被直接简化为 scalar [pdf:E11]（PDF 物理页 12，Sec. 4.4）。
4. Hyper-Par 在 random regular graphs 和随机量子电路上通常最好，但 planar graphs 更偏好 Hyper-Greedy，证明 geometry-specific bias 仍然存在 [pdf:E09]（PDF 物理页 10，Fig. 4）[pdf:E10]（PDF 物理页 11，Fig. 5）。
5. 理论 contraction cost 只有在内存允许时才有意义；深 Sycamore 的 slicing overhead 暴露出下一步真正的瓶颈是 tree、slicing 与执行平台之间的共同设计 [pdf:E16]（PDF 物理页 17，Fig. 10）[pdf:E17]（PDF 物理页 18，Table 2）。

**3 句话：** 多种 contraction-tree 生成器加上 stochastic Bayesian hyper-optimization，能比固定 heuristic 更稳健地适应不同网络 topology。结构简化、total cost 目标与可复用的随机搜索共同带来了大幅性能提升。真正的系统上限最终由 memory、slicing 重算和硬件执行效率共同决定，而不是 $C$ 一项。

**1 句话：** 这篇论文把“手工选 contraction rule”改造成“让完整执行成本反馈自动选择 tree family、参数和 slicing 形状”的搜索问题。

## § 9 — 最脆弱的假设

最脆弱的假设是：由静态 tensor-network 结构计算出的 $C$ 与 $W$ 足以可靠排序真实硬件上的 contraction plans。若这个排序失效，hyper-optimizer 即使把数学 cost 降得很好，也可能把搜索预算集中到 wall-clock 更慢的路径，论文“路径质量带来实际加速”的核心工程价值就会削弱。

论文提供了部分支持：Sycamore-53 没有 hyperedge，Table 2 的实测/外推 FLOPs efficiency 达到 72.8%–85.2%；这说明在 contraction 能高效映射为 dense matrix operations 时，$8C_s/\text{time}$ 与 GPU 峰值之间关系较稳定 [pdf:E17]（PDF 物理页 18，Table 2）。但同一表也暴露反例信号：带 hyperedge 的 Sycamore-53* 在 $m=12$ 时 efficiency 只有 8.16%，Rectangular/Bristlecone 多在约 22%–45%，作者明确归因于某些 pairwise contractions 不能 dispatch 为 matrix-matrix multiplication。论文只在一块 Quadro P2000、一个 JAX/quimb stack 上做 execution benchmark，没有验证跨 GPU、CPU、分布式通信或不同 kernel library 后 $C/W$ 排序是否保持。因此，核心算法指标与真实 runtime 的单调性仍是未经充分覆盖的假设。

## § 10 — 最小复现实验

一周内不必复现全部 benchmark，可以验证最核心、也最容易证伪的 claim：“在相同搜索预算下，hyper-optimized sampling 比固定参数的单次 heuristic 找到更低 total contraction cost。”

- **数据：** 生成 30 个 bond dimension 为 2 的 random 3-regular tensor-network graphs，每个取 $|V|=60$；固定随机种子并保存 graph edge list。
- **实现：** 用论文公开算法对应的 cotengra/quimb 接口，比较三组：固定参数 Greedy、随机参数/随机 seed 的 best-of-$n$ Greedy、Bayesian-tuned Hyper-Greedy。三组使用相同 wall-clock（例如每实例 60 s）和相同并发数；不需要真正构造 tensor values，因为 $W,C$ 可由 graph 与 tree 计算。
- **测量：** 每实例记录最优 $\log_{10}C$、$W$、到达当前最优值的时间，以及 30 个实例上的 paired difference；另对 $|V|=20$ 的小图用 Optimal 做 sanity check。
- **支持条件：** Hyper-Greedy 在多数实例上以相同预算稳定降低 $C$，且差异超过随机 seed 方差；同时小图结果接近 Optimal。
- **反驳条件：** best-of-$n$ 随机搜索与 Bayesian 版本无可重复差异，或 Bayesian overhead 使等 wall-clock 下更差。那将说明收益主要来自“多试几条路径”，而不是参数模型带来的智能分配。

这个实验只检验 path-finding claim，不验证论文的 Sycamore sampling runtime 估算，也不把 graph-only cost 当成 GPU wall-clock。

## § 11 — 最强反例设计

最强反例不是再找一个 Hyper-Par 输给 Hyper-Greedy 的 planar graph，因为论文已经承认 optimizer ranking 随 topology 变化；真正的攻击应让“按 $C/W$ hyper-optimize”系统性选错真实最快路径。

构造一组 contraction trees，使它们的 $C_s$ 和 $W_s$ 很接近，但 contraction 的矩阵形状分布不同：A 类由少量接近方阵的大 GEMM 主导，B 类由大量细长 contraction、transpose 和 hyperedge broadcast 主导。让 hyper-optimizer只能看到论文的 $C_s,W_s$，在同一 GPU 上执行所有候选并测 wall-clock、kernel launch 数、实际 memory traffic 与 GEMM 占比。若低 $C_s$ 的 B 类在多个规模上持续比略高 $C_s$ 的 A 类慢，且差异随 hyperedge 数增加而放大，就得到一个可预测的失败条件：标量运算计数遗漏了 contraction shape 与数据移动，导致 optimizer 的目标函数排序错误。

论文 Table 2 已给出这一替代解释的线索：Sycamore-53 的 FLOPs efficiency 可到 84.1%，而近似分解后引入 hyperedge 的 Sycamore-53* 在 $m=12$ 只有 8.16% [pdf:E17]（PDF 物理页 18，Table 2）。若上述控制实验成立，则论文展示的部分实际优势应重解释为“其 benchmark 恰好产生硬件友好的 kernels”，而不能完全归因于更低的 abstract contraction cost。

## § 12 — Follow-up Research Bet

**主押注：把 contraction tree 从“算术顺序”升级成可生成分布式数据布局和通信程序的 separator hierarchy。** 新研究问题是：能否让 hypergraph partition 的每个 separator 同时决定代数 contraction、tensor sharding、slice 归属与设备间传输，从而自动生成一份面向异构多加速器的 distributed tensor-network program？它首次要实现的能力不是在固定内存约束下少算一点，而是从同一个 tensor expression 直接合成“在哪个设备形成哪个中间 tensor、边界 index 如何分片、哪些 subtree 并行、何时通信”的完整执行结构。

核心机制的因果链是：Hyper-Par 本来就递归产生 subgraph separator hierarchy；separator 上的 indices 正是两个 subtree 必须交换或枚举的边界；把这些 indices 变成显式 sharding object 后，每个 subtree 可在设备内融合 contraction，跨 separator 只传递边界 tensor；再把设备内 FLOPs、峰值显存、跨设备 bytes 和可并行 slice 数联合反馈给 hyper-optimizer，tree shape 会随硬件拓扑改变。这样改变了至少四个基本设计变量：优化对象从标量 $C/W$ 变成带 placement 的 execution graph，状态表示从无设备信息的 binary tree 变成 annotated separator tree，可控变量新增 sharding/replication 与 subtree-to-device mapping，系统边界从单 GPU contraction 扩展到多设备互连。

这一押注有两条论文特异依据。方法侧，Hyper-Par 已把内部节点解释为 subgraph bipartition，并原生处理 weighted hyperedge；slicing 又把选定 index 变成独立 contraction tasks，说明 separator 与并行数据划分共享同一组结构变量 [pdf:E06]（PDF 物理页 7，Sec. 3.5）[pdf:E15]（PDF 物理页 16，Sec. 4.7.1）。实验侧，Fig. 10 表明最低 unsliced cost 的 tree 并不适合 heavy slicing，必须针对目标 $W_s$ 搜索不同 tree；Table 2 则显示 Sycamore-53 $m=20$ 在 $W_s=27$ 时 slicing overhead 达 $6410\times$，同时不同 hyperedge 结构的 GPU efficiency 差异可达近一个数量级 [pdf:E16]（PDF 物理页 17，Fig. 10）[pdf:E17]（PDF 物理页 18，Table 2）。这意味着算术 tree、内存切片和硬件执行并非可独立顺序优化。

它与论文中最近的两类方案有实质区别：现有 slicing 是从一棵 tree 中移出 indices，再以 $C_s$ 评价；qFlex/PEPs 是先把 circuit 压成平面网络，再优化该网络的 contraction。这里的 problem 是生成分布式程序，mechanism 是 separator-driven placement/communication co-design，representation 是带设备与边界数据语义的 tree，experimental object 是端到端多设备 schedule，而不只是 contraction path。由于本卡未联网检索 2021 年后的 distributed tensor compiler 工作，这一方向只标为候选判断，不声称 novelty。

最大收益是：让原本因单卡显存而产生巨大 slicing overhead 的网络，利用高速互连和 subtree locality 进入新的可计算规模，同时自动适配 GPU、FPGA cluster 或混合节点。最大科学风险是：真实 communication、kernel fusion 和 memory allocator 行为过于离散，separator cut weight 无法形成可迁移的 cost model，联合搜索空间还可能比路径搜索本身更难。

最小区分实验可用 2 块互联 GPU：固定同一组 Sycamore-like networks 和相同搜索预算，比较“按 $C_s/W_s$ 找 tree 后做最佳 post-hoc placement”与“搜索时就用 annotated separator tree 联合优化 placement”的端到端 runtime、跨卡 bytes 和峰值显存；两组必须共享相同 kernel library 与候选评估次数。最强替代解释是收益仅来自更多候选或更好的普通 contraction path。若联合方法在控制候选数后仍找到不同 separator shape，并同时降低跨卡 bytes 与 wall-clock，而把它的 tree 交给 post-hoc placement 仍保留优势，才支持“separator—placement 因果机制”；若只降低 abstract cost 或优势在相同 tree 下消失，则该机制被反驳。

**Wild-card alternative：** 把 exact gate decomposition、COPY/hyperedge rewrites 与 contraction tree 统一成可搜索的 tensor-expression grammar，让 optimizer 不只选路径，而是生成代数等价但 topology 不同的网络表示，以“表示变换产生新可收缩几何”为核心机制。
