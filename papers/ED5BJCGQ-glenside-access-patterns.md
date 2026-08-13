# Pure Tensor Program Rewriting via Access Patterns (Representation Pearl)

**作者**：Gus Henry Smith、Andrew Liu、Steven Lyubomirsky、Scott Davidson、Joseph McMahan、Michael Taylor、Luis Ceze、Zachary Tatlock（PDF 物理页 1，标题页）[pdf:E01]  
**出处**：Proceedings of the 5th ACM SIGPLAN International Symposium on Machine Programming（MAPS ’21），Virtual, Canada（PDF 物理页 1，ACM Reference Format）[pdf:E02]  
**年份**：2021（PDF 物理页 1，ACM Reference Format）[pdf:E02]  
**DOI**：10.1145/3460945.3464953（PDF 物理页 1，ACM Reference Format）[pdf:E02]  
**Zotero key**：ED5BJCGQ  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是一个 compiler IR（编译器中间表示）的结构性矛盾：term rewriting（项重写）和 equational reasoning（等式推理）偏好纯、无副作用的表达式；但把 tensor kernel（张量核）真正映射到 accelerator（加速器）时，又必须显式处理 shape、transpose、window、blocking 和实际数据布局。作者指出，既有 ML IR 往往要么“纯但过于高层”，无法表达面向硬件的低层 rewrite；要么“足够低层但不纯”，使等式重写本身变得困难。Glenside 的目标就是在同一个纯 IR 中保留硬件级 layout 信息，并让这些信息能够参与 rewrite search（重写搜索）（PDF 物理页 1，Abstract）[pdf:E03]。

重要性不只在于少写几个 pattern matcher（模式匹配器）。论文描述的现实流程需要 compiler 专家手工 canonicalize（规范化）IR、调整 layout、unroll loop，甚至要求应用作者改变数据类型或源程序，才能暴露 accelerator invocation（加速器调用）机会；作者希望把这类脆弱的、顺序敏感的工程工作改写为少量通用等式规则，再交给 equality saturation（等式饱和）组合搜索（PDF 物理页 2，Section 1 与贡献列表）[pdf:E04]。若成立，它的价值是把“某个 kernel 能否映射到某块硬件”从一次性的 compiler pass，提升为可组合、可复用、可自动探索的表示与推理问题。

论文直接展示的价值边界是 representation pearl（表示层设计范例），不是完成度很高的 accelerator compiler。作者用 matMul、conv2d、max pooling、im2col 和 blocking 的符号化 case study 说明表达力与 rewrite 可达性，并在结论中将贡献表述为“为进一步探索打基础”（PDF 物理页 8，Section 6）[pdf:E05]。因此，这篇论文最可信的结论是“这种表示能让若干经典变换由通用规则组合出来”，而不是“已经证明端到端性能更好”。

## § 2 — 前人工作与不足

论文把前人路线分成四组。第一组是 Halide、TVM、FireIron、LIFT、Accelerate 一类 specification/schedule（规格/调度）分离系统：它们已经能把同一高层程序映射到多种硬件，但高性能 schedule 通常仍需专家精心编排，并受 phase ordering（阶段顺序）影响；自动 scheduling 虽有进展，表示与搜索仍是分开的工程对象。第二组是 TACO、Keops、COMET 一类 index notation（索引记法）IR：它们能紧凑表达逐输出元素计算，也适合稀疏化和 kernel specialization，但索引变量本身引入 binder（绑定结构）与上下文分析。以上都是论文对相关工作的归纳，未在本任务中联网复核（PDF 物理页 2，Section 2.1–2.2）[pdf:E06]。

第三组是 polyhedral compiler（多面体编译器），如 Tensor Comprehensions 与 Tiramisu。它们擅长把规则 loop nest（循环嵌套）建模为 polyhedron（多面体）并做几何变换，但核心能力受 affine transformation（仿射变换）约束；论文将其视为与 term rewriting 互补，而不是被 Glenside 取代。第四组是经典 term rewriting 与 equality saturation：前者破坏性地逐步改写，容易因规则顺序而得到截然不同结果；后者利用 e-graph（等价图）同时保留多个等价程序，缓解 phase ordering，egg 则提供了论文所用的实现基础（PDF 物理页 3，Section 2.2–2.3）[pdf:E07][pdf:E08]。

Glenside 认为这些路线共同缺少一个中间层：既要像纯函数表达式一样可做无副作用等式推理，又要像低层 compiler IR 一样把“哪些维度在枚举、哪些维度交给一次局部计算”显式化。作者进一步声称 Glenside 是首个适合 equality saturation 的 tensor IR，并把原因归结为 access pattern（访问模式）提供了 rank-polymorphic（秩多态）、高阶且无 binder 的 kernel combinator（PDF 物理页 3，Section 2.3）[pdf:E08]。这是论文原文 claim；由于协议限定只读本包材料，这里不把“首个”当作经外部相关工作核验后的 novelty 结论。

## § 3 — 重建作者的思考路径

下面是基于全文证据的逆向重建，不是作者逐字陈述。

第一步，从最简单的纯 matMul 出发。若只用 `map`、`cartProd`、`dotProd` 和 `trans2`，`cartProd` 会把二维结果压成一维，导致输出从 `[[f64]]` 退化为 `[f64]`；把它特化成 `cartProd2D` 后，又需要 `mapAt2` 才能在第二维执行 dot product。维度一多，就必须为不同 rank 和不同目标维度复制 operator 与 rewrite（PDF 物理页 3，Section 3.1）[pdf:E09]。

第二步，考虑通常的抽象工具。lambda、currying、closure 或 index notation 可以消除 `mapAt2` 之类的组合爆炸，但它们引入 name binding；在 e-graph 中对 binder 下的表达式重写，需要跟踪 free variable、substitution 和每个子表达式的上下文。作者报告，这会显著扩大 rewrite search space，抵消采用 equality saturation 的优势（PDF 物理页 4，Section 3.2）[pdf:E10]。

第三步，把“在哪些维度枚举”和“每次拿哪一块做计算”从 operator 名称与 binder 中抽出来，放进 tensor 的扩展 shape。这样，`mapAt2` 不再是一个新 operator，而只是同一个 tensor 的另一种 access/compute 维度划分；transpose、windows、flatten、slice 等也成为改变访问视图的纯 transformer。核心转折不是再发明一个优化 pass，而是把低层 layout 决策改写成可等式推理的 shape algebra（形状代数）（PDF 物理页 4，Section 4.1）[pdf:E11]。

第四步，用 equality saturation 验证这个表示是否真的“可组合”。如果 matMul 与 conv2d 最终都暴露出 `(compute dotProd (cartProd ...))`，那么一个面向 systolic array（脉动阵列）的 rewrite 就能匹配二者；若 shape 暂时不匹配，再让 flatten/reshape 或 slice/concat 的通用等式把程序变成可匹配形态。由此，im2col 与 blocking 不再是两个专门 pass，而是通用 rewrite 的涌现组合。

## § 4 — 核心 Intuition

Access pattern 把一个 tensor 的 shape 分成 access dimensions（访问维度）与 compute dimensions（计算维度）：前者说明程序要枚举多少个局部对象，后者说明每个局部对象交给哪个 operator 处理（PDF 物理页 4，Section 4.1）[pdf:E11]。Transformer 只改变“怎么看数据”，operator 只改变“对局部块算什么”，所以 conv2d、matMul 和 max pooling 的复杂差异主要落在 access 侧，而计算侧常可收敛为少数共享模式（PDF 物理页 6，Figure 2）[pdf:E12]。一旦表示保持纯且无 binder，equality saturation 就能同时保留多条等价变换路径，让 im2col、blocking 与 accelerator mapping 从通用规则组合中出现，而不依赖手写规则顺序（PDF 物理页 7，Section 5.3）[pdf:E13]。

## § 5 — 具体方法与完整 Pipeline

Glenside 的语言核心分为两类构造。`access`、`transpose`、`cartProd`、`windows`、`slice`、`squeeze`、`flatten`、`reshape`、`pair` 是 access pattern transformer，它们改变 access/compute 维度的组织方式但不执行数值运算；Table 1 给出各自的输入与输出 shape 约束（PDF 物理页 5，Table 1）[pdf:E14]。`reduceSum`、`reduceMax`、`dotProd` 是 operator，只能出现在 `compute` 中；Table 2 显示它们把一个 compute block 归约为标量（PDF 物理页 5，Table 2）[pdf:E15]。

以“把 conv2d 映射到 weight-stationary systolic array（权重驻留脉动阵列）”为完整例子：

1. **输入**：activation tensor `A` 的逻辑 shape 为 `(N,C,H,W)`，weight tensor `W` 为 `(O,C,K_h,K_w)`，stride 为 `(S_h,S_w)`。论文先将 activation 视为 `N` 个 image，即 `(access activations 1)` 得到 `((N),(C,H,W))`。
2. **形成滑窗**：`windows` 在 activation 的 compute dimensions 上构造 `(C,K_h,K_w)` 窗口，得到 `((N,1,H',W'),(C,K_h,K_w))`；这里每个 access 位置对应一个待卷积 patch（PDF 物理页 5，Section 5.1 与 conv2d 定义）[pdf:E16]。
3. **访问权重**：`(access weights 1)` 把权重视为 `O` 个 filter，shape 为 `((O),(C,K_h,K_w))`。
4. **配对并计算**：`cartProd` 把每个 patch 与每个 filter 配对，形成 `((N,1,H',W',O),(2,C,K_h,K_w))`；`compute dotProd` 对每对局部块做逐元素乘加，随后 `squeeze` 与 `transpose` 恢复输出 layout `((N,O,H',W'),())`。Figure 2a 同时标注了每一步的 access pattern shape（PDF 物理页 6，Figure 2a）[pdf:E12]。
5. **暴露硬件模式**：matMul 与上述 conv2d 都包含 `(compute dotProd (cartProd ...))`。Figure 3 的 conditional rewrite 在两个输入满足二维 access/compute shape 条件时，把该子式替换为 `systolicArray` 调用，并把第二个输入转置后以 `access ... 0` 表示“整块读取权重”（PDF 物理页 6，Figure 3 与 Section 5.2）[pdf:E17]。
6. **自动得到 im2col**：conv2d 的 patch 与 filter 仍是高维 compute block，不能直接满足 Figure 3。Figure 4 先插入保持等价的 `reshape(flatten(a), originalShape)`，再用两条 composition-commutativity rewrite 把 `reshape` 穿过 `cartProd` 与 `compute dotProd` 向外“冒泡”（PDF 物理页 7，Figure 4）[pdf:E18]。中间项把 activation windows 展平为 `((N·H'·W'),(C·K_h·K_w))`，权重展平为 `((O),(C·K_h·K_w))`，这正是 im2col 后的矩阵乘结构（PDF 物理页 7，Figure 5）[pdf:E19]。
7. **保留 layout 意图**：映射后的 weight access 被显式写成“先 transpose，再一次性 access”，作者认为这比仅记录算术等价式包含更丰富的 layout 信息，可供后续 rewrite 或 code generation 使用；但这里仍是符号化 IR 节点，并非已经生成并执行的 RTL 或 machine code（PDF 物理页 7，Section 5.2）[pdf:E20]。

按 EMT + FPGA 视角核对，论文的模型是静态正整数 shape 上的纯 tensor expression；没有开关事件、离散事件调度、multirate time stepping（多速率时间推进）或状态更新语义。并行性只通过 access dimensions、Cartesian product、window 与 reduction 的依赖关系被符号化，未给出 task graph schedule、memory arbitration 或 pipeline initiation interval。matMul 动机示例使用 `f64`，但论文没有数值误差分析、fixed-point/quantization 规则、真实 FPGA board、HLS/RTL 工具链、BRAM/DSP/LUT 占用、时钟频率、latency、throughput 或实时步长报告；硬件端只出现抽象的 `systolicArray` construct（PDF 物理页 3，Section 3.1；PDF 物理页 6，Figure 3）[pdf:E09][pdf:E17]。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有 theorem/proof 意义上的形式化推导；核心数学是 shape typing（形状类型）与等式 rewrite。可以把它分成五层。

**第一层：matMul 的目标等式。** 对矩阵 `P` 与 `Q`，输出满足

\[
R_{ij}=\sum_k P_{ik}Q_{kj}=P_i\cdot Q_j^{\mathsf T}.
\]

这说明每个输出元素都是“一行与一列的 dot product”，自然诱导 `cartProd(rows(P), columns(Q))` 后再 `dotProd`；困难不在算术，而在如何保留二维输出 shape（PDF 物理页 3，Section 3.1，未编号公式）[pdf:E09]。

**第二层：access pattern 的语义。** 一个 access pattern 的 shape 是一对 tuple：

\[
(S_A,S_C),\qquad \operatorname{shape}(T)=S_A\mathbin{+\!+}S_C.
\]

`S_A` 是 access dimensions，`S_C` 是 compute dimensions；语义上，它把原 tensor 看成 shape 为 `S_A` 的外层 tensor，其中每个元素又是 shape 为 `S_C` 的局部 tensor。若二维 `T` 的 shape 为 `(m,n)`，则 `(access T 1)` 得到 `((m),(n))`，即枚举 `m` 行、每次计算一个长度为 `n` 的向量（PDF 物理页 4，Section 4.1）[pdf:E11]。

**第三层：`compute` 的保形规则。** 若输入 access pattern 为

\[
((s_0,\ldots,s_{m-1}),(s_m,\ldots,s_n))
\]

且 operator `f` 的局部类型为

\[
(s_m,\ldots,s_n)\rightarrow(s'_{m'},\ldots,s'_{n'}),
\]

则 `compute f` 的结果是

\[
((s_0,\ldots,s_{m-1}),(s'_{m'},\ldots,s'_{n'})).
\]

也就是 operator 只能改变 compute dimensions，不能改变 access dimensions（PDF 物理页 4，Section 4.3 起始；PDF 物理页 5，Section 4.3 续）[pdf:E21][pdf:E22]。因此，rows `P` 与 columns `Q` 的 `cartProd` 得到 `((M,O),(2,N))` 后，`compute dotProd` 应得到 `((M,O),())`。值得注意的是，Section 4.3 的一处正文写成 `((M,N),())`，而同页前文与 Figure 2b 都要求保留 access dimensions `(M,O)`；这应是一个局部 notation typo（PDF 物理页 5，Section 4.3；PDF 物理页 6，Figure 2b）[pdf:E22][pdf:E12]。

**第四层：conv2d 只是 access algebra 加一次 dot product。** 论文给出的逐元素定义为

\[
\operatorname{out}[n,o,x,y]=
\sum_{d_x,d_y,c}
A[n,c,S[0]x+d_x,S[1]y+d_y]\,W[o,c,d_x,d_y].
\]

`windows` 负责把每个 `(c,d_x,d_y)` patch 变成 compute block，`cartProd` 负责把 patch 与 filter 配对，`dotProd` 完成乘加。因而 conv2d 与 matMul 的算术核心相同，差异被压缩到 access pattern 的构造过程（PDF 物理页 5，Section 5.1，未编号公式）[pdf:E16]。

**第五层：通过等式把 shape 改造成硬件可匹配形式。** im2col 的探索式 rewrite 是

\[
a\;\rightsquigarrow\;\operatorname{reshape}(\operatorname{flatten}(a),\operatorname{shape}(a)),
\]

它先引入 flatten，再立即 reshape 回原 shape，因此在逻辑 tensor 语义上保持等价；另外两条规则把 `reshape` 分别移过 `cartProd` 与 `compute dotProd`。在 e-graph 中，原式与这些中间式同时存在，直到某个等价项满足 systolic rewrite 的二维 shape 条件（PDF 物理页 7，Figure 4 与 Section 5.3）[pdf:E18][pdf:E13]。blocking 的对应代数是：若 dot-product 的 compute dimension 被切成两段，则完整 dot product 可改写为两个子 dot product 后再 `pair` 与 `reduceSum`；若切的是 access dimension，则结果沿对应 access dimension `concat`（PDF 物理页 8，Figure 6）[pdf:E23]。

## § 7 — 实验设计与结论

这篇论文没有传统 benchmark，而是四组 constructive case study（构造性案例）。因此下面的“答案”是“目标项能否由表示与规则推导出来”，不是运行速度、能耗或 FPGA 实测结论。

**问题 1：同一套 IR 能否简洁表示不同 ML kernel？** 实验把 2D convolution、matrix multiplication、max pooling 写成 Glenside 程序，并逐行标注 access pattern shape。答案是三者都能表示，而且每个 kernel 的数值计算只需一个 operator；大部分程序长度用于建立数据访问方式。更关键的是，conv2d 与 matMul 共享 `(compute dotProd (cartProd ...))`，说明硬件匹配可以针对结构而非算子名称（PDF 物理页 6，Figure 2 与 Discussion）[pdf:E12]。

**问题 2：纯 rewrite 能否直接识别 accelerator invocation？** 实验用一个带 shape side condition 的规则，把符合条件的 dot-product Cartesian product 改写为 weight-stationary `systolicArray`。答案是在符号层面可以，同时还能把权重转置与整块读取的 layout 要求编码到 RHS；论文未执行该调用，也未验证 codegen、memory system 或 timing closure（PDF 物理页 6，Figure 3；PDF 物理页 7，Section 5.2）[pdf:E17][pdf:E20]。

**问题 3：通用 rewrite 能否自动重建 im2col？** 实验只添加 flatten/reshape 探索规则，以及 `reshape` 与 `cartProd`、`compute dotProd` 的组合交换规则。答案是 equality saturation 能找到一个展平后的 conv2d 等价项，使其满足 systolic rewrite，得到 Figure 5 的 im2col 结构；作者强调规则不是为单个 conv2d 实例硬编码，且 e-graph 的非破坏性搜索使叙述中的规则顺序仅用于说明（PDF 物理页 7，Figure 4、Figure 5 与 Section 5.3）[pdf:E18][pdf:E19][pdf:E13]。

**问题 4：同样机制能否发现 matMul blocking？** 实验用 slice-then-concat 探索规则，再把 `concat` 分配穿过 `cartProd` 与 `compute dotProd`。在输入为 `32×32` 的示例中，结果是八个 `16×16` matMul，随后通过求和与拼接恢复完整输出；Figure 7 只画出其中两个（PDF 物理页 8，Figure 7）[pdf:E24]。该案例明确假设对每个可用维度都尝试切分、每次恰好对半切、所有维度大小都是 2 的幂；作者还以 systolic array 常见规模约 `16×16` 到 `256×256` 说明 blocking 的动机（PDF 物理页 8，Section 5.4）[pdf:E25]。

**总体结论与不可外推范围。** 这些案例支持“access pattern 足以表达若干通用、可组合的 layout rewrite，并能在 e-graph 中到达经典变换”这一 claim。它们没有回答 rewrite soundness 是否被 mechanized checker 完整验证、e-graph 节点数与搜索时间如何随 rank/shape/rule set 增长、extractor 如何选择最低真实硬件成本项、im2col 的复制开销何时值得、生成代码是否正确，以及任何 latency、throughput、resource、energy 或 real-time 指标；这些都不能从本文结果外推。

## § 8 — Take-aways

**5 句话**

1. Access pattern 用 `(access dimensions, compute dimensions)` 取代大量按维度特化的 operator，把低层 layout 选择变成纯 shape 信息（PDF 物理页 4，Section 4.1）[pdf:E11]。
2. Transformer 负责重排、切片、开窗和展平数据视图，operator 只在 compute block 上做归约，因此表示保持可组合（PDF 物理页 5，Table 1–2）[pdf:E14][pdf:E15]。
3. Conv2d、matMul 与 max pooling 的差异主要在 access pattern，而共享的计算骨架可直接成为 accelerator rewrite 的匹配对象（PDF 物理页 6，Figure 2–3）[pdf:E12][pdf:E17]。
4. Equality saturation 让 im2col 与 blocking 从少量通用等式的组合中出现，避免把专家经验固化成顺序敏感的专用 pass（PDF 物理页 7–8，Figure 4–7）[pdf:E18][pdf:E23][pdf:E24]。
5. 论文证明的是表示与搜索的可行性，不是实际 accelerator performance；真实 codegen、cost model、搜索扩展性和硬件测量仍未闭合。

**3 句话**

1. 最核心的贡献不是一个新的 conv 或 matMul algorithm，而是一个让 layout 进入纯等式推理的 IR 边界。
2. 最有说服力的结果是 im2col 与 blocking 都能由通用 rewrite 涌现，而不是被单独编码。
3. 最大缺口是“逻辑等价且 shape 可匹配”尚未被证明等于“物理布局可实现且硬件成本更低”。

**1 句话**

Glenside 把低层 tensor mapping 重述为可由 e-graph 搜索的纯 shape algebra，但本文完成的是表达力论证，而不是加速效果论证（PDF 物理页 8，Section 6）[pdf:E05]。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**仅凭 access/compute shape 分解与这些逻辑 transformer，就足以充当从纯 tensor 等价到真实 accelerator layout 的契约。** 论文中的 access pattern 本质上是一对正整数 tuple，Table 1 描述的是 transpose、windows、slice、flatten 等逻辑 shape 变换；它没有把 physical stride、base offset、contiguity、aliasing、address space、bank mapping、buffer capacity 或 transfer cost 纳入同一语义对象（PDF 物理页 4，Section 4.1；PDF 物理页 5，Table 1）[pdf:E11][pdf:E14]。

这个假设在实际中可能失败，因为两个逻辑 shape 完全相同的 tensor view，可以具有截然不同的物理步长、对齐与 bank conflict。Figure 3 的 rewrite 只根据 access pattern shape 判断是否可调用 systolic array；RHS 虽然记录了“转置后整块读权重”，作者也只说这可能帮助未来 rewrite 或 code generation，并没有展示 memory legalization 或执行结果（PDF 物理页 6–7，Figure 3 与 Section 5.2）[pdf:E17][pdf:E20]。基于证据的推断是：若后端必须额外 materialize、repack 或跨地址空间复制，e-graph 找到的“硬件项”可能只是数学等价，却不是合法或有利的硬件实现；一旦如此，论文关于 hardware-level rewriting 的核心意义会从“自动映射”退化为“自动生成一个仍需大量后端修复的候选”。

论文为该假设提供的证据是四个 shape-closed 的符号案例，尤其是 im2col 与 blocking 的可达性；缺少的证据是至少一个真实后端对 non-contiguous layout、有限 on-chip memory 与数据搬运进行闭环验证。这个缺口比“规则库还不够多”更关键，因为增加规则无法弥补表示本身没有区分的物理状态。

## § 10 — 最小复现实验

一周内最值得复现的是：**验证 Figure 4 的三条通用 rewrite 是否真的能从 Figure 2a 的 conv2d 自动导出 Figure 5 的 im2col 形态，并进一步触发 Figure 3 的 systolic rewrite。** 这直接测试论文最有代表性的“复杂变换由通用规则组合涌现”claim（PDF 物理页 6–7，Figure 2–5）[pdf:E12][pdf:E17][pdf:E18][pdf:E19]。

实施方案如下：

1. 用 Rust + egg，或任意支持 e-graph 的最小实现，定义 `access/transpose/cartProd/windows/squeeze/flatten/reshape/compute/dotProd/systolicArray` AST，并实现 access pattern shape checker；不需要完整 compiler。
2. 按 Figure 2a 构造一个能产生多个滑窗位置的微型整型 conv2d；同时写一个直接解释器，能够执行原 conv2d term 与被抽取的 im2col/matMul term。
3. 只加入 Figure 3 和 Figure 4 的规则与 side condition，不写“conv2d → im2col”专用规则。记录每轮 e-class/e-node 数、达到 `systolicArray` 的轮次、总搜索时间、抽取项大小，以及 flatten 后逻辑元素数相对原 activation 的膨胀。
4. 对同一组输入分别执行原 term 与抽取 term，要求逐元素完全一致；若使用浮点，则改为明确容差并报告最大绝对误差。
5. **支持 claim 的结果**：在没有专用规则的情况下稳定出现 Figure 5 形态和 `systolicArray` 节点，且解释器输出一致，搜索规模在微型实例上可控。**反驳 claim 的结果**：规则因 shape condition 无法闭合、必须加入实例特定规则、抽取项与原式数值不等价，或 e-graph 在微型输入上即不可控膨胀。

这个实验不需要生成 RTL，也不会证明性能，但能把论文最关键的表示与 rewrite 可达性从“纸面推演”提升为可执行、可证伪的最小闭环。

## § 11 — 最强反例设计

最强攻击不是再找一个 Glenside 不能表达的 exotic operator，而是在它声称已经能映射的 conv2d 上构造**逻辑 shape 相同、物理可执行性相反**的两组输入。具体做法是让两份 weight/activation 具有完全相同的 access pattern shape：一份连续、对齐并适合阵列整块读取；另一份来自带大 stride 的非连续 view，且 im2col 的重叠窗口在有限 on-chip buffer 下必须大规模 materialize。因为 Figure 3 的匹配条件只看 shape，两者都会被改写成相同的 `systolicArray` 结构（PDF 物理页 6，Figure 3）[pdf:E17]。

然后在一个带有限 scratchpad、固定 bank 数和显式 DMA 的 cycle-level model 或小型 FPGA prototype 上比较三条路径：原始直接 convolution、最佳手工 tiled matMul、Glenside 推导的 im2col+systolic 路径。论文承认 im2col 会在内存中实例化 convolution windows、造成数据复制，但把“speedup 足以抵消开销”作为背景判断，并未在本文中测量（PDF 物理页 7，Section 5.3）[pdf:E26]。若连续输入上 rewrite 有利，而同 shape 的非连续输入上必须额外 repack、超出 buffer、或总数据移动使其系统性慢于直接 convolution，就得到一个针对核心机制的反例：access pattern 的逻辑 shape 不足以决定 accelerator legality 与收益。

这个反例比“搜索太慢”更强，因为即使给 e-graph 无限时间、即使所有等式都正确，它仍可能对两个物理上不同的程序做出同一 mapping 决策。替代解释也很明确：论文案例成功不是因为 access pattern 已经捕获了低层 layout，而是因为示例默认了规则、连续、静态且容易 materialize 的 tensor 存储。

## § 12 — Follow-up Research Bet

**候选判断：由 access pattern 反向合成 accelerator dataflow topology（加速器数据流拓扑）。** 由于本任务按协议不联网、没有额外检索相关全文，下面不声称 novelty；它是由本文机制与案例约束出来的研究押注。

新的研究问题是：**能否不再把程序匹配到预先给定的 `systolicArray`，而是从 access-pattern 等价类反向生成最适合一组 kernel 的 processing-element topology（处理单元拓扑）与 dataflow？** 这将首次把“硬件调用是否存在”的搜索提升为“硬件通信结构是什么”的搜索：`access dimensions` 决定并行实例与数据分发轴，`compute dimensions` 决定 PE-local reduction（处理单元局部归约），`windows` 表示邻域复用，`slice/concat` 表示空间分区与汇合，`transpose/flatten/reshape` 表示数据放置与通信重排；equality saturation 先产生 im2col、blocking 等等价因子分解，再把每个等价项翻译为候选 spatial/temporal dataflow graph，最后联合选择程序项与可综合拓扑。

这条因果链有两类论文特异依据。方法上，Glenside 已把访问、计算和 shape 变换拆成可组合的代数，并且 Figure 3 的硬件节点只要求一个明确的访问/计算模式（PDF 物理页 5–6，Table 1–2 与 Figure 3）[pdf:E14][pdf:E15][pdf:E17]。实验上，Figure 4–5 表明同一 conv2d 可被改写成矩阵式数据流，Figure 6–7 又表明同一 matMul 可分解为多个更小阵列任务；这说明 e-graph 中已经存在可用于改变通信拓扑与粒度的自由度，而论文只把它用于适配固定阵列（PDF 物理页 7–8，Figure 4–7）[pdf:E18][pdf:E19][pdf:E23][pdf:E24]。

它至少改变四个基本设计变量：研究目标从“匹配 accelerator”改为“生成 accelerator”；硬件 topology 从固定二维 systolic array 改为可搜索的 PE/NoC graph；系统边界从 compiler IR 扩展到 compiler–architecture co-synthesis；评价对象从单个等价 term 改为 program–topology pair 的通信量、buffer 复用与关键路径。最大的研究收益是让 access pattern 成为 algorithm–hardware co-design 的统一中间对象，可能为 conv、pool、reduction 或混合 kernel 生成非 systolic、工作负载特异的数据流。最大的科学风险是：逻辑 rewrite 暴露的 factorization 未必足以确定可布线、可定时的物理拓扑，且“程序等价 × 拓扑组合”可能使搜索空间爆炸。

首个证伪实验应在同一 PE 数、相同 arithmetic precision（算术精度）、相同外存带宽与 buffer 容量下，比较两种机制：基线是在固定 systolic array 上做最佳 tiling；候选方法允许从 Figure 2 的三类 kernel 及 Figure 4/6 的 rewrite 结果中共同生成 topology。若候选对 matMul 自动恢复近似 systolic 数据流，同时对 conv2d 或 max pooling 产生不同拓扑，并在 cycle-accurate simulation 或小型 RTL synthesis 中降低 on-chip movement 或 latency，且优势在基线充分优化 tiling 后仍存在，就支持“拓扑本身来自 access algebra”这一机制；若所有收益都能由固定阵列上的更好 blocking 解释，则最强替代解释成立，研究押注被否定。与本文最近的对照对象相比，实质差异是本文把 `systolicArray` 作为 rewrite RHS 的既定目标，而该候选把 RHS 的硬件结构本身变成被合成的科学对象。

**Wild-card alternative**：把二分的 `(access, compute)` shape 改成 `(space-access, compute, time)` 三分表示，使 `windows/slice/concat` 同时表达 streaming line buffer、跨周期复用与多速率 token 流，从而让 equality saturation 搜索时序数据流而非空间阵列拓扑。
