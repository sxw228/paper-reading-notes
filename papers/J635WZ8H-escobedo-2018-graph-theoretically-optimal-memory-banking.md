# Graph-Theoretically Optimal Memory Banking for Stencil-Based Computing Kernels

作者：Juan Escobedo；Mingjie Lin  
出处：FPGA ’18: 2018 ACM/SIGDA International Symposium on Field-Programmable Gate Arrays  
年份：2018  
DOI：10.1145/3174243.3174251  
Zotero key：J635WZ8H  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的核心问题不是一般意义上的 memory scheduling，而是一个更窄、也更可形式化的问题：给定 stencil kernel 的 affine memory references，把数组元素静态分配到若干独立 memory banks，并为每个元素生成 intra-bank offset，使同一迭代中被并行访问的元素落在不同的 single-port banks，同时尽量减少 bank 数和存储开销。作者把这两个职责明确拆成 bank map `f(x)` 与 intra-bank offset `g(x)`；前者决定元素进入哪个 bank，后者保证同一 bank 内的不同元素仍有不同地址。PDF 物理页 4，Section 4，Problem 1、Problem 2 与 Eq. (1)–(2)。[pdf:E07] [pdf:E08]

这个问题重要，因为 HLS 即使能把 C-like code 转成 RTL，也不会自动给出最省 bank、又支持并行访问的存储组织。论文的关键转化是：把“同一迭代共同访问”写成无向冲突边，把 array element 写成顶点，把 bank index 写成颜色；于是静态 conflict-free banking 的最小 bank 数变成 memory-access conflict graph 的 chromatic number。作者的 abstract 将贡献概括为：对任意给定 stencil 计算最小 partition factor，并利用冲突图着色的可重复性降低地址映射硬件。PDF 物理页 1，Abstract。[pdf:E01]

必须先限定结论边界。论文的正式冲突模型是“同一迭代共访即冲突”且 bank 为 single-port；它没有把读写类型、物理端口、pipeline cycle、同址依赖或 BRAM read-during-write mode 纳入图模型。因此它首先回答的是静态 bank 候选是否无冲突，而不是任意固定 schedule 下逐周期物理双端口是否合法。PDF 物理页 4，Section 4 对 conflict graph 与 single-port 假设的定义。[pdf:E08]

## § 2 — 前人工作与不足

作者把既有路线分成三类。第一类是 skewing/hyper-plane family：Shapiro [7]、Wijshoff 等 [12,13] 以及 HLS 中的 AMP/GMP [2,9] 都用线性或模意义下的几何映射产生 bank index。它们的优点是映射简单、周期性强；论文指出的不足是搜索空间受单个或少数 hyper-plane families 约束，可能错过非线性形状的更小 partition factor，而且 GMP 仍没有对所有 stencil 给出最小 bank 数证明。论文的 12-point 例子中，直接按 [9] 得到 partition factor 14，而作者给出的 coloring 使用 12 banks；这说明“某个映射族中的最优”不等于“所有静态映射中的最优”。PDF 物理页 2，Section 2，Fig. 1 及其后正文；PDF 物理页 3，Section 3。[pdf:E03] [pdf:E05]

第二类是 lattice/tessellation/supertile。论文对 [1,3,4] 的总结是：lattice 能扩大可表示的映射族，supertile 能把 bank 与 address calculation 变成有限、重复的查表，但有的方法预先给定 bank 数，有的方法优化 conflict 或 memory reuse 而不是从零求最小 partition factor，还有的方法仍不给 partition factor 的普适上界。第三类是 trace-based address mining [14]：它把 masked addresses 建图后做 coloring，适用范围可超出 stencil，但需要遍历 mask 候选，且论文认为仍无最优 bank 数的上界保证。PDF 物理页 3–4，Section 3；这里都是本论文对相关工作的陈述，没有用外部全文独立复核。[pdf:E05] [pdf:E06]

真正的缺口因此不是“以前没人用图”，而是没有同时闭合三个目标：从完整冲突关系得到全局最小 bank 数；把解压缩成有限、周期、可综合的 bank map；再为每个 bank 生成低开销且无别名的 intra-bank offset。本文试图用 chromatic number 解决第一个目标，用 extended stencil 与 periodic stitching 解决第二个目标，再用 `MemO` 和 accumulators 解决第三个目标。

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为以下链条，而不先假设其证明已经成立。

1. 先从失败例子出发：12-point stencil 的理论下界至少是 12，因为单次迭代中的 12 个不同元素形成 clique；但一个具体 hyper-plane mapping 需要 14 banks，说明几何参数化可能限制了解空间。PDF 物理页 2，Section 2。[pdf:E03]
2. 抛开映射公式，直接定义共访关系。每次迭代的访问集合形成 clique，所有迭代的 cliques 叠加成完整 memory-access conflict graph；proper coloring 就是一个静态 conflict-free bank map。PDF 物理页 4–5，Section 4 与 Fig. 5。[pdf:E08] [pdf:E10]
3. 完整图随数组尺寸增长，既难以 optimal coloring，也无法把每个顶点的颜色直接存进硬件；但 stencil references 是 affine 的，且相对位移在迭代间不变，因此完整图具有 translation invariance。PDF 物理页 5，Section 4。[pdf:E09]
4. 选一个 pivot，把所有包含该 pivot 的 stencil translations 叠加，只保留这个有限邻域及其全部冲突边，得到 extended stencil graph（ESG）。它是完整图的一个 induced subgraph，也是作者希望足以代表全局的局部对象。PDF 物理页 6，Fig. 8 及其后正文。[pdf:E13]
5. 若局部 coloring 能周期性扩展，就只需保存一个有限 pattern。作者于是把问题从“一次性着色整个数组”改成“着色 ESG，再证明可以 stitching/stamping 到全域”；若直接重复失败，则向 stencil 内补点，寻找一个满足其周期构造条件的 augmented stencil。PDF 物理页 6–8，Fig. 7、Section 5.2 与 Algorithm 1。[pdf:E12] [pdf:E16] [pdf:E19] [pdf:E20]
6. 最后把颜色表实现为 `MemB`，把 bank 内地址表实现为 `MemO`，并用维度方向的 accumulators 跨 repeating regions 累加 offset，从而避免为完整数组保存巨大的映射表。PDF 物理页 9，Fig. 12 与 intra-bank offset 正文。[pdf:E21] [pdf:E24]

这条路线的洞察是正确地把“最小 bank 数”从某个 bank formula 的参数搜索中剥离出来；它的风险则集中在局部 ESG 是否真的决定全局 chromatic number，以及局部 coloring 是否必然存在有限周期 lift。

## § 4 — 核心 Intuition

把同一迭代会一起访问的元素连边后，bank assignment 就是 graph coloring，最少静态 banks 就应当由 chromatic number 决定。Stencil 的平移重复性让作者只着色 pivot 周围的有限 ESG，再尝试把这个着色周期性 stitching 到整个 memory domain。颜色只解决 bank map；实际地址还必须由独立的 intra-bank offset map 保证 `(bank, offset)` 对每个数组元素唯一。PDF 物理页 4、6–7、9。[pdf:E08] [pdf:E13] [pdf:E17] [pdf:E21]

## § 5 — 具体方法与完整 Pipeline

以论文的 12-point stencil 为例，完整 pipeline 如下。

1. **提取 stencil。** 从 loop body 取出同一迭代需要并行访问的 affine references。Fig. 1 的形状有 12 个点，分布在四行；论文报告 GMP [9] 在 block size 1 时使用 14 banks，而目标是判断 12 banks 是否不仅可行、而且最小。PDF 物理页 2，Fig. 1 与正文。[pdf:E03]
2. **建立静态冲突关系。** 把每个被访问的 array element 作为顶点；若两个元素在某一迭代共同出现，就连边。每个 stencil instance 因而诱导一个 clique。该图不区分 read、write，也不带 cycle 或 port 标签。PDF 物理页 4–5，Section 4。[pdf:E08] [pdf:E11]
3. **构造 extended stencil。** 固定 pivot，叠加所有包含该 pivot 的 stencil instances；取这些位置在完整冲突图中的 induced subgraph，得到 ESG。Fig. 8 展示了 3-point stencil、extended stencil、ESG 与其 coloring 的对应关系。PDF 物理页 6，Fig. 8。[pdf:E13]
4. **求 ESG 的 optimal coloring。** 论文用 Matlab Matgraph toolbox 做 coloring，得到 `χ(ESG)`。若 `χ(ESG)` 等于 stencil 点数，作者把这种情况称作 perfect，并直接进入 periodic coloring；若更大，则承认已有 coloring 尚不能保证形成可用的有限 mapping，转而给 stencil 加点。PDF 物理页 6，Fig. 7 及正文。[pdf:E12]
5. **处理不能直接重复的形状。** 在最小 circumscribing square 内，按补点数从小到大枚举 node subsets；每次为 augmented stencil 建 ESG，直到其 chromatic number 等于 augmented stencil 的点数。Algorithm 1 返回该 ESG 的 coloring。PDF 物理页 8，Fig. 11 与 Algorithm 1。[pdf:E19] [pdf:E20]
6. **生成 periodic bank map。** 对满足构造条件的 ESG，作者用 pivot/link node 把 `ESG–ESG′–ESG` 交替 glue，声称颜色在有限距离内重复。12-point 的最终 data-space coloring 用 A–L 表示 12 banks，黑线标出 repeating pattern；任意平移后的 stencil instance 都不出现同色冲突。PDF 物理页 2，Fig. 2；PDF 物理页 7，Fig. 9。[pdf:E04] [pdf:E17]
7. **生成 intra-bank offset。** bank map 以 `MemB[coordinate mod ST]` 查出；offset 以 `MemO[coordinate mod ST]` 加水平、垂直 accumulators 得出。`MemO` 的局部编号可以重新排列，以把较小 offsets 放到更常落在有效矩阵范围内的区域，降低 padding waste。PDF 物理页 9–10，Fig. 12、Eq. (3) 与 Fig. 13。[pdf:E21] [pdf:E24] [pdf:E25]
8. **综合。** Matlab 根据 bank/offset supertile 生成 transformed C，Vivado HLS 再生成 RTL；每个 bank 被实现成独立 memory，访问先查 bank，再计算对应 intra-bank address。PDF 物理页 9，Section 6。[pdf:E22]

这里必须把两个层次分开。上述步骤最多构成“静态 bank 候选无冲突”：在作者的 single-port、同一迭代全并发模型中，一个 iteration 的不同顶点不会映射到同一 bank。对固定 schedule 的逐周期 dual-port 合法性，还要知道读请求能否合并、写请求能否合并、每个 cycle 每个 bank 的真实操作数、两个物理端口如何指派、同址 RAW/WAR/WAW 的先后关系、read-during-write 采用 read-first/write-first/no-change 中哪一种、以及 pipeline 写回何时对后续迭代可见。论文没有报告这些语义，也没有给出逐周期 port assignment，因此不能把其静态 coloring 自动解释成 dual-port BRAM 的完整合法性证明。

## § 6 — 核心数学推导（无形式化数学则跳过）

**1. Bank map 与 coloring 的等价。** 设 `G_D=(V,E)` 是给定 iteration domain 上的完整 memory-access conflict graph：`V` 是 array elements，若存在一次迭代同时访问 `u,v`，则 `(u,v)∈E`。在论文的 single-port 静态模型中，任意 proper coloring `c:V→{0,…,N-1}` 都可作为 `f=c`；反过来，任意无冲突 bank map 都必须让每条边两端 bank 不同。因此概念上有

\[
N_{\text{static}}=\chi(G_D).
\]

每个含 `m` 个互异访问点的 stencil instance 形成 `K_m`，所以 `χ(G_D)≥m`。论文的 3-point 例子得到 3-coloring 与 chromatic number 3；它同时指出一般 `k≥3` 的 graph coloring 判定是 NP-complete。PDF 物理页 5，Fig. 5 与 chromatic number 定义。[pdf:E10] [pdf:E11]

论文 Eq. (1) 把 bank minimization 写成最小化 `N=max f(x_i)` 并要求同一迭代 references 的 bank labels 不同。若颜色按 `0,…,N-1` 编号，这个写法存在一个没有解释的 index/count convention：最大 label 与 bank 数相差 1；这属于记号问题，不改变“最小 proper coloring”这一核心含义。PDF 物理页 4，Problem 1 与 Eq. (1)。[pdf:E07]

`g` 不参与颜色冲突，却承担地址唯一性。论文要求

\[
x\neq y\Longrightarrow (f(x),g(x))\neq(f(y),g(y)),
\]

也就是不同元素要么 bank 不同，要么同 bank 但 offset 不同；Problem 2 再最小化各 bank 最大 offset 的总和。由此可见，`χ(G_D)` 只给出 bank-count optimum，不自动给出 storage optimum，也不自动证明 `g` 的实现没有 alias。PDF 物理页 4，Problem 2 与 Eq. (2)。[pdf:E08]

**2. Extended stencil 的局部化。** 把 pivot 平移到原点，作者的构造可等价重写为

\[
ES(S)=\bigcup_{s\in S}(S-s)=S-S,
\qquad ESG(S)=G_D[ES(S)],
\]

即收集所有“让 stencil 的某个点落在 pivot 上”的 translations，再取其 union 上的 induced conflict graph。这一等价式是对 Fig. 8 构造的重写，不是论文原式。因为 ESG 是完整图的 induced subgraph，必有 `χ(ESG)≤χ(G_D)`；真正需要证明的是反向不等式。PDF 物理页 6，Fig. 8 与其后正文。[pdf:E13]

作者为反向不等式使用 clique-sum 思路：若两个图沿完整图 `K_n` glue，则引用 [8] 的结论

\[
\chi(G_1\oplus_{K_n}G_2)=\max\{\chi(G_1),\chi(G_2)\}.
\]

由于每个 stencil instance 是 `K_n`，且相邻 ESG 被认为是 isomorphic，作者据此声称不断沿 stencil clique glue 不会增加 chromatic number，最终覆盖完整冲突图，于是 `χ(ESG)=χ(G_D)`。PDF 物理页 6–7，Section 5.1。[pdf:E14] [pdf:E15]

这个推导成立需要非常强的结构条件：完整冲突图必须能按某个顺序表示成 ESG copies 的 clique-sums；每次新 copy 与已有图的交集必须是适用定理的 complete subgraph；而且不能出现未包含在该 intersection 中的额外交叉边。仅有 translation invariance、每个 iteration 是 clique、ESG 是 induced subgraph，并不能自动推出这些条件。论文用“can be readily partitioned”和示意图说明这一步，但没有给出对任意 stencil、任意边界 domain 的完整分解定理。因此“ESG chromatic number 等于全图 chromatic number”是全文最需要单独验证的证明环节。

**3. Perfectness 与 periodic stitching。** 论文先给出标准定义：perfect graph 要求其每个 induced subgraph 都满足 `χ=ω`。随后算法却把 `χ(ESG)=|S|` 直接写成“即 ESG perfect”，并在 stitching 证明中使用“所有最大 cliques 都含全部颜色”、存在特定 pivot/link-compatible coloring、以及 glue 后仍 perfect 等性质。PDF 物理页 5 的 perfect graph 定义；PDF 物理页 6 的算法分支。[pdf:E11] [pdf:E12]

两者并不逻辑等价：一个图整体满足 `χ(G)=ω(G)`，不代表它的每个 induced subgraph 都满足该等式。作为证明条件，作者至少需要真正证明 ESG 属于 perfect graph class，或另证其特定 stitching construction 对 `χ(ESG)=|S|` 足够。Fig. 9–10 展示了 pivot/link 的构造直觉和 3-point 示例，但示例不能替代对所有 shapes 的存在性证明。PDF 物理页 7–8，Section 5.2 与 Fig. 9–10。[pdf:E16] [pdf:E17] [pdf:E18]

**4. Node addition 的最优性范围。** 当作者认定原 ESG 不 perfect 时，Algorithm 1 在最小 circumscribing square 内按 added-node cardinality 递增搜索，条件是 augmented ESG 的 chromatic number 等于 augmented stencil size。终止性论证依赖“填满 square 后可对应 rook graph/Latin square，因此会得到 perfect ESG”；全局最优性论证又依赖外部节点可借 vertex-transitive property 换入 square 内。PDF 物理页 8，Algorithm 1 及其后证明。[pdf:E19] [pdf:E20]

所以这里可严格区分三种结论：

- 若已证明 `χ(ESG)=χ(G_D)`，则 `χ(ESG)` 是该静态 single-port 冲突模型下的最小 bank 数。
- 若还证明 ESG coloring 可周期 lift，则得到有限可实现的 bank map；这是比“存在一个全图 coloring”更强的结论。
- node-addition 算法显然按补点数穷举了 square 内、且满足其 equality predicate 的候选，但要把它提升为“所有 periodic mappings 中的最小 partition factor”，还需证明任何更小周期 coloring 都能由这种补点并变 perfect 的形式表示，以及 outside-square 交换论证对任意 stencil 成立。正文没有把这两个表示完备性条件独立闭合。

**5. Multi-port/defective coloring 被证明到什么程度。** 论文在 Introduction 的贡献列表中说 multi-port banking 可由 defective coloring 解决，Section 4 又写“can be readily shown”；但全文没有定义 defect 参数如何对应 `p` 个 ports，没有给出 theorem、proof、algorithm、periodic lift、intra-bank address rule 或实验。PDF 物理页 1 的贡献列表与物理页 4 的唯一扩展陈述。[pdf:E02] [pdf:E08]

因此正文真正证明和实验处理的对象仍是 proper coloring 下的 single-port 静态冲突。对于 dual-port，单纯允许相邻顶点同色还不够：需要在每个 cycle 对访问 multiset 做 read/write merge，验证每个 bank 的有效操作数不超过端口容量，并给出具体 port assignment；同址 RAW/WAR/WAW、read-during-write mode 和写回可见性还会改变合法性。论文没有提供这些信息，不能替作者补成已证明结论。

## § 7 — 实验设计与结论

**问题 1：方法能否在实际 HLS flow 中生成可综合 bank/offset logic？** 作者把六个 kernel 的 access patterns 输入 Matlab，计算 bank assignment 与 supertile 内 relative offset，自动生成 transformed C，再用 Vivado HLS 2016.2 和 Vivado HLx 2016.2 综合、实现。目标器件是 XC7K160tffg676-3 Kintex-7；每个 bank 取 512 elements、32-bit data 加 4-bit parity，映射到 single-port RAMB18E1。所有实验开启 loop pipelining，目标 II=1，并要求同一 iteration 的 memory accesses 在一个 clock cycle 内完成。答案是这套静态映射与地址逻辑能进入完整 FPGA tool flow；但实验设置仍明确是 single-port，而不是 dual-port legality test。PDF 物理页 9，Section 6。[pdf:E22]

**问题 2：bank 数、clock period 与资源是否优于 GMP/Trace？** Table 1 比较 Denoise、Bicubic、Deconv、MotionH、Sobel 与 12-Point。最直接支持核心 bank-count claim 的数据是 12-Point：GMP 用 14 banks，本文用 12；clock period 从 2.8 ns 降到 2.4 ns，DSP 从 12 降到 0，FF 从 5108 降到 806，LUT 从 9116 降到 2159，但估算 power 从 1687 mW 增到 1895 mW。表中 summary row 报告的平均改善为 bank 2.38%、clock period 14.21%、DSP 66.67%、FF -8.77%、LUT -30.42%、power 7.1%、pipeline stages 53.3%；负值说明资源收益并非所有 benchmark 都一致。需要注意，六个逐项 FF improvement 的算术平均约为 +8.78%，与 summary row 的 -8.77% 符号相反，表内存在可直接复算出的不一致。PDF 物理页 9，Table 1。[pdf:E23]

**问题 3：intra-bank offset 的 regular layout 能否减少 padding waste？** 作者让 `MemO` 的低 offsets 优先占据更常位于有效矩阵边界内的区域，并用 Eq. (3) 估算多维 memory overhead。Fig. 13 展示 repeating offset rectangle 的安排；Table 2 比较不同图像尺寸。表中 average row 在 SD、HD、FHD、WQXGA、4K 上分别报告 20.8%、30.95%、33.33%、-34%、33.33%；12-Point 在 WQXGA 的 improvement 报告为 -2261.7%。但同一行原始 overhead 是 GMP 3180、Ours 8324，按表中其他行显然采用的 `(GMP-Ours)/GMP` 计算应约为 -161.8%，而不是 -2261.7%；average row 也无法由印出的逐项百分比直接得到。因此 Table 2 能支持“特定尺寸可能显著更差”，不能把其两个汇总百分比当作已自洽复核的统计量。PDF 物理页 9–10，Eq. (3)、Fig. 13、Table 2。[pdf:E24] [pdf:E25] [pdf:E26]

**问题 4：实验验证了哪些 claim，没验证哪些？** 结果支持“bank/offset mapping logic 可综合”“12-point case 可用更少 banks”“若干 benchmark 上 clock/DSP 有收益”。它没有报告 exact coloring 的运行时间或规模曲线，没有验证 Algorithm 1 对困难 shapes 的组合爆炸，没有对 `χ(ESG)=χ(G_D)` 做跨 domain-size 的独立检查，也没有提供 read/write schedule、port assignment、functional hazard trace 或 read-during-write configuration。因此 Table 1 不能被外推为逐周期 dual-port 正确性证明。结论段仍把贡献概括为任意 stencil 的 optimal partition factor 与 finite repeating mapping，这一普适表述强于实验覆盖。PDF 物理页 10，Section 7。[pdf:E27]

## § 8 — Take-aways

**5 句话。**

1. 论文最有价值的抽象是把 static memory banking 变成 graph coloring，使“最少 banks”有了 chromatic-number 语言。
2. Extended stencil 的目标是把无限或超大 translation-invariant conflict graph 压缩成一个有限 induced subgraph，再周期复用 coloring。
3. Bank map 与 intra-bank offset 是两个不同问题：颜色只决定 bank，`MemO` 与 accumulators 才决定 bank 内唯一地址。
4. 全局最优性的关键不在 coloring 本身，而在“完整图确实是适用 clique-sum theorem 的 ESG 拼接”以及“局部 coloring 确实能周期 lift”这两个结构条件。[pdf:E14] [pdf:E17]
5. multi-port/defective coloring 和固定 schedule 的物理双端口合法性没有在正文中被证明。[pdf:E08]

**3 句话。**

1. 这是一篇把 memory banking 从几何 mapping heuristic 提升到 graph-theoretic optimization 的论文。
2. 12-point 综合数据说明该抽象能产生有竞争力的 bank 数与硬件，但 theorem 的 universal quantifier 需要比现有示意证明更强的验证。[pdf:E23] [pdf:E27]
3. 阅读时必须把 static conflict-free coloring、periodic addressability、intra-bank injectivity 和 cycle/port semantics 分成四层，不能互相替代。

**1 句话。**

论文给出了一个很强的局部图着色框架，但“局部 ESG 最优”到“全域、周期、物理端口级最优”的每一次提升都需要额外条件。

## § 9 — 最脆弱的假设

最脆弱的假设是：**任意 stencil 的完整 conflict graph 都可以由 isomorphic ESG copies 沿完整 stencil cliques 逐次做 clique-sum，且不会出现 theorem 未覆盖的额外交叉边或非完全交叠。** 一旦这个假设不成立，`χ(ESG)` 只仍是全图 chromatic number 的下界，作者关于最小 partition factor 的核心结论就会直接失效。论文给出的证据是 extended stencil 包含所有“两个 stencil instances 如何相交”的局部情形、每个 stencil 是等大的 clique，以及 Fig. 9–10 的 glue construction；但这些内容没有形式化证明任意数量的 overlaps 都能按合法 clique-sum 顺序闭合。PDF 物理页 6–8，Section 5.1–5.2。[pdf:E13] [pdf:E14] [pdf:E15] [pdf:E17] [pdf:E18]

一个独立的警报是 perfectness predicate。论文自己把 perfect graph 定义为“每个 induced subgraph 都有 `χ=ω`”，却在算法中用整个 ESG 的 `χ=|S|` 代替该条件。[pdf:E11] [pdf:E12] 例如取 5-point cross `S={(0,0),(±1,0),(0,±1)}`，其 ESG 可用 `c(x,y)=x+2y mod 5` 五着色，且每个 stencil clique 给出 `χ≥5`，所以整体 `χ=5`；但相对位置 `(-1,-1),(-1,0),(0,1),(1,1),(1,-1)` 诱导一个 5-cycle，该子图有 `χ=3、ω=2`。所以整体 equality 并不使 ESG 成为 perfect graph。这个例子不必然说明周期 coloring 不存在，却说明正文 stitching proof 使用的 perfect-graph 前提不能由当前判据直接得到。

实际中这项假设尤其可能在 sparse、长距离或非凸 stencils 上失败：多个局部 ESG 的重叠可能通过不同 stencil instances 同时产生额外边，形成只在更大尺度出现的 odd-cycle 或 coloring consistency constraint。论文的六个综合 benchmark 没有针对这种“局部可着色、全局不可按同色数扩展”的情形做压力测试。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 HLS system，而是核心 theorem 的有限、可证伪版本。

1. **数据。** 手工录入论文的 3-point stencil、12-point stencil，再加入一个 sparse collinear stencil `S={0,1,4}`；把一维例子嵌入二维数组的一行即可，不需要外部 dataset。论文示例的 stencil extraction 与 12-point 形状见 Fig. 1、Fig. 5。[pdf:E03] [pdf:E10]
2. **实现。** 对每个 `S` 生成差分集合 `S-S`、ESG，以及逐渐增大的有限 domain conflict graphs；用 exact DSATUR、SAT 或 ILP 同时求 chromatic number 与 coloring certificate。另实现作者的 periodic stamping，并检查每条全图冲突边两端颜色不同。
3. **测量。** 记录 `|ESG|`、`χ(ESG)`、有限 domain 的 `χ(G_L)`、找到的 period、每个 iteration 的 bank conflicts，以及 Algorithm 1 的候选数和运行时间。对 bank/offset 层，再在一个小矩阵上实现 `MemB/MemO+accumulators`，穷举验证 `(f,g)` injective。论文的代码模板与 offset 结构见 Fig. 12、Eq. (3)。[pdf:E21] [pdf:E24]
4. **支持标准。** 若对所有测试 stencil，随着 domain 扩大始终有 `χ(G_L)=χ(ESG)`，且一个有限周期 coloring 可扩展到所有已检查边，同时 `(f,g)` 无 alias，则核心静态 claim 获得支持。
5. **反驳标准。** 任意一个有限 domain 出现 `χ(G_L)>χ(ESG)`，或重复 ESG coloring 在边界外产生同色 conflict，就足以反驳“任意 stencil 只需着色 ESG”的 universal claim；不需要进入 FPGA synthesis。
6. **schedule 审计分开做。** 若要测试 dual-port，把每个 cycle 的 read/write operations 保留下来，先做同址 read merge 与合法 write merge，再求 bank/port assignment，并显式设置 read-during-write mode。只有这一层通过，才能说固定 schedule 在物理双端口上合法；论文现有 single-port II=1 设置只能作为基线。[pdf:E22]

## § 11 — 最强反例设计

最强攻击是给出一个局部 ESG 只需 3 色、但完整 conflict graph 的有限 induced subgraph 已经需要 4 色的 stencil。考虑 sparse collinear 3-point stencil

\[
S=\{0,1,4\}.
\]

按论文 Fig. 8 的 pivot construction，extended-stencil 顶点是 `S-S={-4,-3,-1,0,1,3,4}`，冲突边对应距离 1、3、4。这个 ESG 有显式 3-coloring：`A={0}`，`B={-4,1,3}`，`C={-3,-1,4}`；又因为每个 stencil instance 是 `K_3`，所以 `χ(ESG)=3`。该构造直接针对论文声称的 `χ(ESG)=χ(full graph)` 与 clique-sum 推导。PDF 物理页 6–7，Section 5.1。[pdf:E13] [pdf:E14] [pdf:E15]

但在足够大的 iteration domain 中，完整 conflict graph 在顶点 `{0,1,2,3,4,5,6}` 上的 induced subgraph 不可 3-color；若数组下标要求非负，把全部位置整体平移即可。假设 triangle `{0,1,4}` 分别着 `A,B,C`；triangle `{0,3,4}` 强制 `3=B`；triangle `{1,4,5}` 强制 `5=A`；triangle `{1,2,5}` 强制 `2=C`；triangle `{2,3,6}` 强制 `6=A`。然而 `5` 与 `6` 的距离为 1，二者有冲突边，却都被强制为 `A`，矛盾。因此该有限子图至少需要 4 色；而四种颜色显然足够，例如依次给 `0…6` 赋 `C,A,B,A,B,C,D`。所以完整图的 chromatic number 至少是 4，而 ESG 的 chromatic number 是 3。

这个反例揭示 proof failure 的具体位置：相邻 ESG copies 的组合并不总是“只沿一个 complete clique glue，且无其他 cross-edges”；多次 stencil overlaps 会在更大尺度产生额外 coloring constraints，不能反复直接套用 clique-sum chromatic-number theorem。它攻击的是论文对“any stencil”的理论 claim，不否定 12-point benchmark 本身可能确实存在 12-bank periodic coloring。[pdf:E04] [pdf:E23]

## § 12 — Follow-up Research Bet

**主 idea：面向真实 BRAM 语义的 space-time access hypergraph co-design。** 新的研究问题是：能否把 schedule phase、bank、physical port、intra-bank address 与 read/write visibility 一起设计，在一个有限的 space-time quotient 上求出最少物理 BRAM banks，而不是先做静态 proper coloring、再把 schedule 与端口语义留给后端？这首次可能把“静态 bank 候选无冲突”提升为“给定 modulo schedule 下逐周期可执行且 bank 数可证明最小”，并允许利用 dual-port capacity 与时间错位把物理 bank 数降到静态 single-port `χ(G)` 以下。

核心机制是把顶点从 array element 改成带类型的 operation instance `(address, pipeline phase, R/W kind)`；用 hyperedge 表示同一 cycle 的共同容量约束，用有向 relation 表示同址 RAW/WAR/WAW 与 writeback visibility；color 不再只是 bank，而是 `(bank, port, phase)` 的联合标签，`g(x)` 与 BRAM read-during-write mode 也成为约束变量。Stencil 的 translation invariance 仍用于把无限 space-time graph quotient 成有限 supercell，延续本文 `MemB/MemO` 的硬件优势，但基本数学对象从静态 undirected graph 改成 typed temporal hypergraph，时间尺度从 iteration 变成 cycle，硬件映射从 bank-only 变成 bank/port/address/mode co-design。论文已经提供 finite periodic bank/offset tables 与 II=1 HLS flow，却只对 single-port proper coloring 建模；它还明确提到 multi-port/defective coloring，但没有展开，这正是新对象的论文特异入口。PDF 物理页 1、4、9。[pdf:E02] [pdf:E08] [pdf:E21] [pdf:E22]

最大的研究收益是得到可直接落到 FPGA primitive 的最小-memory theorem，并把 bank count、II、port utilization、clock period 与 energy 放到同一个可验证 Pareto frontier 中。Table 1 显示减少 bank/DSP 与改善 clock 可以同时发生，但 power 和 LUT/FF 并不单调；这说明联合优化的评价对象不能只剩 partition factor。PDF 物理页 9，Table 1。[pdf:E23]

最大的科学风险是：space-time quotient 的最优 coloring/packing 仍可能 NP-hard，周期 lift 也可能像本文 ESG claim 一样在大尺度失效；此外 vendor-specific read-during-write semantics 可能让统一抽象过于复杂。首个区分实验应选择一个同时含 reads、writes 与 loop-carried dependency 的小 stencil，固定一个 modulo schedule，对比三种模型：本文 single-port static coloring、简单的 per-cycle capacity coloring、完整 typed temporal hypergraph。若第三种模型在更少 banks 下给出可综合 port assignment，并通过 cycle-accurate simulation 与 formal hazard checks，而前两者失败，就支持“联合时空表示产生了新能力”；若最优解总退化成静态 coloring，核心机制便被反驳。

与论文内最近路线的实质区别是：GMP/tessellation 主要改变静态几何 mapping，[14] 从 trace 中选择 bank lookup，本文正文则只给 array-element conflict graph；新方向直接改变 problem、representation、time model 与 experimental object。由于本任务按协议未联网检索 2018 年后的工作，这一方向只标为候选判断，不声称 novelty。

Wild-card alternative：把 stencil conflict graph 直接视为 `Z^d` 上的 Cayley graph，搜索 finite-index subgroups 及其 coset coloring，用可倾斜、非矩形 fundamental domain 取代 circumscribing square 和 node addition，使 subgroup index 而不是“补多少点”成为周期 bank map 的基本设计变量。
