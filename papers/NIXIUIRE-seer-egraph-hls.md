# SEER: Super-Optimization Explorer for HLS using E-graph Rewriting with MLIR

**作者**：Jianyi Cheng、Samuel Coward、Lorenzo Chelini、Rafael Barbalho、Theo Drane  
**出处**：arXiv:2308.07654v1  
**年份**：2023  
**DOI**：10.1145/3620665.3640392  
**Zotero key**：NIXIUIRE  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是传统 HLS 的“给定一段已经写得像硬件的程序，怎样做 scheduling 和 binding”，而是更靠前的一步：面对普通 C/C++/SystemC 程序，怎样自动决定 source transformation 的顺序，使下游 HLS 真正得到高效硬件。作者指出，现有工具通常对所有输入采用固定 pass sequence；不同 pass 会互相破坏或创造机会，因此同一组 pass 仅仅改变顺序，就可能走到完全不同的硬件实现。这就是 HLS 中的 phase-ordering problem。论文把固定流水线与 SEER 的并行探索画在 Figure 1，并声称在所测 benchmark 上最高可达到原程序 38 倍的性能、面积不超过 1.4 倍。[pdf:E01]（PDF 物理页 1，Abstract、Figure 1 与 Introduction）

这个问题重要，是因为当前 HLS 的易用性与结果质量之间仍有断层：工具接受高级语言，不等于它能从任意软件写法自动找到好的微架构。设计者仍需按硬件原则手工改写源程序；如果这个步骤能够自动化，HLS 才更接近“软件输入直接得到有竞争力的硬件”，而不是把硬件专家的知识转移到 coding style 手册里。这里的价值既是减少人工，也是在比单一路径更大的等价程序空间中发现专家未必会尝试的组合。

## § 2 — 前人工作与不足

论文把既有工作分成几层。传统 HLS 已能自动完成 scheduling、binding 和 retiming；parameterized HLS 的 DSE 也能搜索 unrolling、tiling、array partition 等显式参数，但最前面的 source rewriting 仍主要依赖人工。软件编译器中的 phase-ordering 方法包括 machine learning 预测 pass sequence，以及 heuristic 或 iterative search；作者认为前者常依赖特定 domain，后者不能高效保留迭代中出现的中间表示，而且两类工作主要以软件指标为目标。MLIR/CIRCT、ScaleHLS、POLSCA 等提供端到端编译基础设施，但仍使用固定 pass order。[pdf:E02]（PDF 物理页 3，Figure 3、Problem Formalization 与 Section 3.1）

最接近的硬件工作是 ROVER：它已经用 e-graph 对 combinational datapath 做 area-oriented rewriting，但不处理 loop 等 control path。SEER 的定位不是替代这些工具，而是把 MLIR 的高层 control transformations、ROVER 的 datapath/gate rewrites 和 HLS scheduling 信息编排到同一个等价表示空间中。[pdf:E03]（PDF 物理页 4，Section 3.2–3.3 与 Figure 5）因此，作者所针对的缺口很具体：已有各层 optimizer，但缺少一种能够保留多条等价路径、让不同粒度优化相互创造机会，并用硬件代价而非软件代价选出结果的统一探索机制。

## § 3 — 重建作者的思考路径

可以从论文的 loop fusion 例子逆向重建思路。三个顺序 loop 中，`loop_1` 与 `loop_3` 因数组 `x` 的 dependence 不能融合，`loop_2` 却能与其中任意一个融合。传统 destructive compiler 必须先选一条路；一旦融合了 `loop_1+loop_2`，另一条 `loop_2+loop_3` 就不再可达。更麻烦的是，选择哪条路取决于后续综合得到的 operation latency：Table 1 的 Case 1 中 Listing 2 最好（1196 cycles），Case 2 中却是 Listing 3 最好（701 cycles）。[pdf:E04]（PDF 物理页 2，Figure 2、Table 1 与 Section 2）

已有 e-graph 提供了第一条线索：constructive rewriting 不删除旧表达式，而把等价表达式放进同一 e-class，共享公共子结构。已有 MLIR pass 又提供了第二条线索：无需在 egg 中重写成熟的 loop dependence analysis。最后，HLS scheduler 提供第三条线索：可以先从原始表示取得少量 scheduling constraints，再在搜索中近似传播，而不必对每个候选重新综合。于是作者的路线自然变成：用一个可在 MLIR 与 egg 之间往返的语言保存等价程序；让内部 e-graph rules 与外部 MLIR passes 共同扩张空间；最后用 hardware-aware cost extraction 选出 HLS source。

## § 4 — 核心 Intuition

SEER 的核心不是“猜一条更好的 pass sequence”，而是暂时不做单选：把许多等价程序及其共同子表达式同时留在 e-graph 中，让 control、datapath 和 gate-level rewrite 彼此创造后续机会。需要做静态分析时，可以临时抽取 analysis-friendly 表示；需要生成硬件时，再从同一等价类抽取 hardware-friendly 表示。这样，某个中间表示可以为另一等价表示提供分析事实，而不要求最终硬件使用那个分析友好的写法。[pdf:E05]（PDF 物理页 7，Figure 7–9 与 Section 4.4–4.5）

## § 5 — 具体方法与完整 Pipeline

以一段包含 loop 和 memory access 的 C 程序为例，完整 pipeline 如下：

1. Polygeist 把 C/C++/SystemC 转成 MLIR 的 `affine` 或 `scf` dialect；SEER front end 再把 MLIR 转成作者定义的 S-expression 语言 SeerLang。SeerLang 保留 operation、type、operand，并以 `seq` 把可能有 memory dependence 的操作串起来。论文当前为简化分析，假设任意两个 memory operations 之间都存在 dependence。[pdf:E06]（PDF 物理页 5，Figure 6、Listing 4–6 与 Section 4.1–4.2）
2. 由 SeerLang 建立初始 e-graph。内部 rules 直接在 egg 中 rewrite；外部 rules 则从匹配到的 SeerLang 子表达式抽取 MLIR，调用现有 MLIR pass，确认结果有效且发生变化后，再翻译回 SeerLang 并 union 到原 e-class。
3. rewrite 同时覆盖 control path、datapath 和 gate level。论文列出 10 个 loop/if 相关 MLIR passes，并继承 ROVER 的 106 个 bitwidth/signage-aware datapath 与 gate rewrites；具体包括 loop fusion/interchange/flatten/perfection、if conversion、memory forwarding、if correlation、memory reuse、control-flow mux、constant folding、strength reduction 等。[pdf:E07]（PDF 物理页 6，Table 2 与 Section 4.3）
4. SEER 交替运行 control-flow 与 datapath rewrite set，直到没有新表示或达到用户限制。Figure 7 展示了 `seq` associativity 这种内部 unconditional rewrite，以及 loop fusion 这种经 MLIR validation 的 conditional rewrite；原来的两种 fusion 路径都保留在图中。[pdf:E05]（PDF 物理页 7，Figure 7 与 Section 4.4）
5. extraction 分两阶段：先固定最低估计 latency 的 control flow，再在这一子空间内以 ROVER 的 bitwidth-dependent gate count 最小化 datapath area。抽出的 SeerLang 经 MLIR、emitC 回到 HLS C/SystemC。
6. 最后，SEER 利用 egg 的 proof production 回溯 transformation steps，为每一步生成 SystemC，并用 Synopsys VC Formal 建立从原程序到结果程序的 equivalence-check chain。[pdf:E08]（PDF 物理页 9，Section 4.6–4.7）

一个最能体现方法差异的实例是 Figure 8：`(i<<1)+i` 在 ASIC 中只需 shift 和 adder，却不容易被 polyhedral analysis 识别；同一 e-class 中的 `3*i` 适合 affine analysis，却可能需要 multiplier。SEER 先抽取 `3*i` 促成 loop fusion，再为最终硬件抽回 `(i<<1)+i`。[pdf:E09]（PDF 物理页 8，Figure 8、Section 4.5 与 Constraint 1）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学核心是把 HLS loop schedule 压缩为四元组 `(P,l,N,A)`：`P` 是 initiation interval，即相邻 iteration 启动间隔；`l` 是单次 iteration latency；`N` 是 trip count；`A` 是 memory-access 集合。对 pipelined loop，总 latency 为

\[
L=(N-1)P+l.
\]

直觉是第一个 iteration 花 `l` 个周期完成，后续 `N-1` 个 iteration 每隔 `P` 周期启动，因此只再增加 `(N-1)P`。[pdf:E09]（PDF 物理页 8，Figure 10 与 Constraint 1）

搜索中新 loop 不逐个调用 HLS scheduler，而是从原 loop 的 constraint 近似传播。以 fusion 为例，作者令融合后 `l'=max(l_0,l_1)`、`N'=max(N_0,N_1)`、`A'=A_0∪A_1`，并在假设 BRAM 单端口时用 `P'=max(P_1,P_2,M(A'))` 计入同一数组的最大访问数。然后对每个 e-node 定义

\[
L(n)=\begin{cases}(N_n-1)P_n+l_n,&n\text{ 是 loop}\\0,&\text{其他}
\end{cases}
\]

并在全部表示 `E` 中最小化 loop latency 之和。得到共享同一 control flow 的子空间 `E'` 后，再以 ROVER 的 node area `A(n)` 最小化 datapath gate count：

\[
\min_{e\in E}\sum_{n\in e}L(n),\qquad
\min_{e\in E'}\sum_{n\in e}A(n).
\]

control-flow extraction 是 greedy；datapath extraction 是用 Coin-Or CBC 求解的 ILP。[pdf:E08]（PDF 物理页 9，Equations 2–4 与 Section 4.6）工程上，这相当于先决定“循环怎样组织、吞吐怎样最大”，再在该控制结构内决定“算术表达式怎样实现、面积怎样最小”。这不是统一的 Pareto optimization，power 也没有进入目标。

## § 7 — 实验设计与结论

**问题一：不同粒度的 rewrite 是否真的需要联合探索？** 作者用 Intel production snippet `byte_enable_calc` 做 case study，并分别运行只含 datapath 的 SEER(D)、只含 control 的 SEER(C)、完整 SEER、专家手工版本和“手工版本再交给 SEER”。ROVER-only 与 baseline 相同；SEER(C) 将 cycles 从 119 降到 81；完整 SEER 进一步降到 29 cycles、execution time 24.1 ns、area 1.36 µm²，优于手工版本的 42 cycles/34.9 ns，但面积略高于手工版本的 1.33 µm²。这支持“control rewrite 把区域暴露给 datapath rewrite，两者组合优于单独使用”的 claim。[pdf:E10]（PDF 物理页 10，Figure 11–12、Table 3 与 Section 5.2）

**问题二：收益能否跨应用出现？** 作者在人工 `seq_loops`、Intel case 和 MachSuite 的 `kmp`、两种 `gemm`、两种 `md`、两种 `sort` 上比较 baseline Stratus、ROVER 和 SEER。工具链为 Stratus HLS 22.02、内置 45 nm technology library；cycles 来自 co-simulation，area/power 来自 Post & Route。Table 4 显示 SEER 在八个总体 benchmark 上的 normalized geometric mean 为 0.34× cycles、1.06× area、0.95× critical path、2.54× power；也就是说平均约 2.9× speedup、面积约增加 6%，但 power 明显恶化。[pdf:E11]（PDF 物理页 11，Table 4、Figure 13）

**问题三：探索是否具有可用的规模？** Table 5 报告 e-graph 从 114 到 44,328 nodes、搜索时间从 0.3 s 到 161 s；这说明小 kernel 上可以运行，但不是大型程序可扩展性的证明。[pdf:E11]（PDF 物理页 11，Table 5）作者也明确把 multithread exploration、subgraph partition 和更大 benchmark 留作 future work。[pdf:E12]（PDF 物理页 11，Section 5.3、Conclusion）

不得外推的边界同样重要：实验目标是 ASIC，不是 FPGA；benchmark 是低层 kernel；比较没有覆盖论文提到的 FPGA-oriented HLS work；所有 loop 默认 pipeline，cost 不含 power；等价验证依赖商业 VC Formal。因此，“对任意软件程序都能得到优于专家的硬件”并没有被这些实验验证。

## § 8 — Take-aways

**5 句话。** 第一，HLS 的 source rewrite phase ordering 本身就是一个需要 hardware-aware 评价的设计空间。第二，e-graph 的价值不只在压缩等价表达式，还在于保留会相互创造机会的多条 transformation path。第三，SeerLang 让 egg 可以复用 MLIR pass，而无需复制整个 MLIR optimizer。第四，analysis-friendly 与 hardware-friendly 表示可以来自同一 e-class，前者提供分析事实，后者成为最终实现。第五，实验支持明显的 cycle reduction 和适度 area 代价，但也暴露 power、scale、schedule approximation 和 ASIC-only evaluation 的边界。

**3 句话。** SEER 用 e-graph 把固定 pass pipeline 改造成可保留多条等价路径的探索。它以近似 loop schedule 先选 control flow，再用 ROVER area model 选 datapath。最有说服力的结果是 control 与 datapath rewrite 的协同，最需要警惕的是评价模型没有 power 且对新 loop schedule 只做近似。

**1 句话。** 这篇论文证明了：对 HLS 而言，保存并跨用多个等价程序表示，可能比更聪明地猜一条固定优化顺序更有价值。

## § 9 — 最脆弱的假设

最脆弱的假设是：**从原始 loop schedule 推导出的 `(P,l,N,A)` 近似，足以正确排序 rewrite 后的 control-flow 候选。** 这不是一个局部误差问题，因为 extraction 先以该模型固定 control flow，之后的 area ILP 只能在 `E'` 中选择 datapath；如果第一阶段排错，真正更快的控制结构会被整体排除。[pdf:E08]（PDF 物理页 9，Equations 2–4）

这个假设可能在真实 HLS 中失效：fusion、unrolling、memory forwarding 和 if conversion 会改变 recurrence、resource sharing、memory banking、mux depth 与 critical path，实际 `P` 和 `l` 未必能由 `max` 规则组合；论文还默认所有 loop pipeline，并在 fusion 公式中假设 single-port BRAM。[pdf:E09]（PDF 物理页 8，Section 4.6 与 Constraint 1）论文给出的间接证据是最终综合结果总体改善，但没有报告预测 latency 与实际 post-synthesis latency 的 rank correlation，也没有比较“近似模型选中的候选”与“小空间中逐个真实综合的 oracle”。因此，这一核心 ranking assumption 仍未被直接验证。

## § 10 — 最小复现实验

一周内最有价值的复现，不是重建全部 SEER，而是验证上述 ranking assumption。选论文公开的 `seq_loops` 和一个小型 `gemm` kernel，只实现 3–4 种会互相作用的 rewrite：loop fusion、complete unroll、strength reduction、memory forwarding。枚举得到几十个合法候选，用论文的 `(P,l,N,A)` 传播公式预测 cycles；同时用同一套可用 HLS 配置逐个综合，记录实际 cycles、critical path、area，并检查功能等价。

测量三项：预测与实测 cycles 的 Spearman rank correlation；预测最优候选在实测排序中的名次；两阶段策略相对真实 Pareto front 的 regret。若两个 kernel 上相关性高、预测最优稳定落在实测前 10%，就支持论文最关键的快速 extraction 机制；若存在合法候选被预测为最好、实测却落入后半区，且误差可追溯到 banking、resource conflict 或 changed recurrence，就直接反驳其普适性。这个实验不需要实现完整 MLIR↔egg↔SystemC toolflow，却能证伪核心 hardware-aware ranking claim。

## § 11 — 最强反例设计

最强反例是一类“rewrite 会改变 memory architecture 与 recurrence”的 kernel：两个 loop 表面上可 fusion，按公式得到较小 `N'` 和可接受 `P'`；但融合后多个访问落到同一 bank，或更长 recurrence 迫使实际 II 上升，导致真实 execution time 比未融合版本更差。进一步加入一个等价的非 affine index，使 analysis-friendly 版本能够通过 dependence check，但最终抽回的 hardware-friendly index 改变 banking inference。这样可以同时攻击论文的跨表示推理与 schedule propagation，而不是只证明某个 rule 实现有 bug。

实验上，在小尺寸 stencil、histogram 或 irregular gather kernel 中系统枚举 layout、fusion 与 unroll 组合，对每个表示都做真实 HLS/P&R；然后比较 SEER 模型排序、真实排序以及下游工具实际推断出的 port/bank conflict。如果模型持续偏爱会产生 memory serialization 的表示，而一个仅逐候选真实综合的 oracle 稳定选择另一表示，那么结果的替代解释就是：论文的收益主要来自默认 pipelining 和 benchmark 中温和的 memory behavior，而不是 cost model 已经抓住了跨粒度 phase ordering 的一般规律。

## § 12 — Follow-up Research Bet

**研究押注：让 e-graph 同时综合“等价算法表示”和“等价 memory architecture”，从 source-to-source optimizer 升级为 representation-carrying memory-system synthesis。** 新问题不是怎样给 SEER 增加一个 power term，而是：能否让每个 e-class 同时携带 computation、index map、layout、banking/replication 与 port protocol 的等价实现，使编译器在分析时选择 affine、规则的视图，在硬件生成时选择无 bank conflict、低通信的物理布局？如果成功，首次可能做到的是：loop transformation 不再被固定数组布局约束，memory architecture 也不再是程序 extraction 之后才附加的 pragma/DSE 参数，而成为与 control/datapath rewrite 同步演化的语义对象。

核心因果链是：e-graph 保留多种等价 index 表达与 program invariant → layout-isomorphism rules 把 index rewrite 与 bank mapping、padding、replication 联结 → MLIR analysis 可从 affine 视图证明 legality，hardware extraction 可从物理视图计算 port conflict 和 on-chip traffic → 联合 extraction 选择 computation-layout pair，而不是先选程序再被动映射 memory。论文已展示同一 e-class 中 `3*i` 可服务 polyhedral analysis、`(i<<1)+i` 可服务 ASIC 实现，这是“同一语义、不同消费者使用不同表示”的直接机制依据。[pdf:E09]（PDF 物理页 8，Figure 8 与 Section 4.5）其现有 cost state 已包含 memory-access set `A` 与 `M(A')`，说明 memory pressure 已进入 control model，但仍只把 memory 当约束，而没有把 layout/banking 作为可重写设计变量。[pdf:E08]（PDF 物理页 9，fusion constraints 与 Equations 2–4）实验中 `md`/`gemm` 的 speedup 伴随显著 area/power 增长，且 normalized power geometric mean 为 2.54×，提示仅优化 control latency 与 datapath gate area 会把代价推向 memory/physical implementation；这是扩展评价对象而非简单加惩罚项的实验动机。[pdf:E11]（PDF 物理页 11，Table 4、Figure 13）

相对论文及其列出的最近工作，这个方向至少改变了三件事：problem 从 pass ordering 变为 computation-memory co-synthesis；representation 从仅表示程序 operation 扩展为带 layout isomorphism 的 memory object；hardware mapping 从 extraction 后交给 HLS 工具，变成 e-graph 内部可探索变量。这里的 novelty 只作候选判断，因为本任务未联网检索 2023 年之后的 e-graph memory-synthesis 工作。

最大收益是把 memory-bound kernel 中“分析能证明”和“硬件能并行访问”统一起来，可能打开传统 source rewrite 到不了的架构；最大科学风险是 layout equivalence 会引入全局状态、alias 和容量约束，使 e-class 爆炸，并且 layout conversion 的成本可能抵消收益。首个区分性实验应在 `seq_loops`、blocked GEMM 与一个 irregular gather 上比较三组：固定 layout 的原 SEER、先抽程序再做独立 banking DSE、联合 computation-layout e-graph。若联合方法只等于两阶段 DSE，说明收益来自更大的普通搜索预算；只有当它发现一个依赖“分析视图与物理视图分离”才合法且更优的 design，并在真实 HLS/P&R 上降低 cycles 与 bank conflicts，才支持核心机制。

**Wild-card alternative**：把 e-graph 反过来用作 HLS compiler 的主动测试生成器，从同一等价类抽取结构差异最大的程序对，自动寻找“语义相同但综合 QoR 剧烈分叉”的输入，以建立专门测量 phase-ordering blind spot 的 benchmark，而不是继续优化单个输入。
