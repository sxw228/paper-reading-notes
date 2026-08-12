# Stardust: Compiling Sparse Tensor Algebra to a Reconfigurable Dataflow Architecture

**作者：** Olivia Hsu；Alexander Rucker；Tian Zhao；Varun Desai；Kunle Olukotun；Fredrik Kjolstad  
**出处：** Proceedings of the 23rd ACM/IEEE International Symposium on Code Generation and Optimization（CGO ’25）  
**年份：** 2025  
**DOI：** 10.1145/3696443.3708918  
**Zotero key：** 35GUSIX4  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** Stardust 要解决的是：怎样让熟悉稀疏张量算法、但不了解具体 reconfigurable dataflow architecture（RDA）微结构的 performance engineer，从 tensor index notation 出发，把稀疏张量代数端到端编译到 Capstan，而不用手写充斥 memory hierarchy、显式数据搬运和 scanner 控制的 Spatial 程序。论文把问题拆成两个彼此耦合的映射：数据从抽象 tensor format 落到物理 memory，计算从 CIN 子树落到 parallel pattern；用户保留高层 placement 与 schedule 决策，编译器补齐 architecture-specific binding。[pdf:E01]（PDF 物理页 1，Abstract 与 Section 1）[pdf:E02]（PDF 物理页 2，Introduction 的问题陈述与 contributions）

这件事重要，不只是因为“写代码麻烦”。CPU/GPU 常见的是 pull memory model：控制流在需要数据时发起访问；Capstan/Spatial 属于显式、解耦的 push memory model，数据必须按预先安排的时间与层级被推到消费它的 pattern。稀疏 tensor 又把不规则坐标流、union/intersection、随机访存和分层压缩格式叠加在一起，因此普通的“把 `forall` 翻译成 `for`”并不成立。[pdf:E02]（PDF 物理页 2，Introduction）[pdf:E03]（PDF 物理页 4，Figure 4 及其上方的 ⑤–⑧ 对照）

**基于证据的合理推断。** Stardust 的实际价值是把 RDA 的可编程性问题改写成编译器接口问题：让用户在熟悉的 tensor algebra、format 和 scheduling 层表达意图，同时让编译器承担容易出错、又高度依赖硬件的 memory lifetime、transfer 和 scanner 生成。若这层接口成立，稀疏 RDA 才可能从“架构设计者能写的少数 kernel”变成可扩展的 kernel 平台。

## § 2 — 前人工作与不足

**相关文献中的已有结论（仅按本文的 related-work 叙述）。** TACO 已经把 tensor index notation、per-level format 与 sparse scheduling 分离，并通过 concrete index notation（CIN）表达迭代、临时 tensor 和变换；它的既有 lowering 主要面向 CPU/GPU 等 von Neumann 目标。Custard/SAM 能把 tensor index notation 编译到 streaming dataflow IR，但 SAM 是抽象机器，不自动落到具体 sparse RDA。Spatial 及其编译链能落到 Capstan，却要求程序显式写出 parallel pattern、memory type 和数据搬运。SPU 用 C 中的 stream-join 组合稀疏索引，ExTensor 用层次化 intersector 的硬件配置；它们提供不同的 sparse DSA 编程模型，并不是 Stardust 当前 backend 的直接替代实现。[pdf:E02]（PDF 物理页 2，Background）[pdf:E12]（PDF 物理页 13，Section 10）

不足的根因不是这些工作“没有想到高层语言”，而是接口链断在不同位置：TACO 的 IR 与 schedule 不包含 RDA push-memory 所需的物理 placement；SAM 没有 concrete backend lowering；Spatial 暴露的又恰好是用户最不该手工承担的 architecture-specific memory 与 scanner 细节。Stardust 的位置就是补上 **CIN → Spatial → Capstan simulation** 这段，并扩展 format/schedule，使内存与计算映射在高层可表达、在低层可完成。[pdf:E04]（PDF 物理页 5，Figure 5）

**边界。** “第一套端到端编译栈”是作者的 claim，不是本卡独立做出的 novelty 结论；本任务没有联网检索，也没有读取所引相关论文全文，因此不能把 related-work 段落当成完整的 prior-art 排查。

## § 3 — 重建作者的思考路径

以下是**基于证据的合理推断**，不是作者逐字陈述的研究日志。

第一步，从 SDDMM 对照中会看到，imperative lowering 暗含四个并不适用于 Spatial 的前提：`forall` 可直接变成循环；tensor element 可在表达式出现处随取随用；计算集中在最内层；累加可以反复修改一个时间变量。Spatial 反而要求不同的 scanner pattern、批量搬运、数据到达即消费，以及把累加映射为空间化 Reduce。[pdf:E03]（PDF 物理页 4，Figure 3/4 与正文）

第二步，与其直接从 index notation 猜完整 Spatial 程序，不如保留 TACO 已经成熟的 CIN 作为中心 IR。CIN 已经能承载 loop tree、where producer-consumer、temporary tensor 和 schedule rewrite；只要给 tensor format 增加 on/off-chip location，再把跨 region assignment 解释为 transfer，就能在原 IR 中保留数据移动的语义，而不把 Spatial 代码提前塞进前端。[pdf:E04]（PDF 物理页 5，Figure 5 与 Section 5）[pdf:E05]（PDF 物理页 6，Table 1、Figure 7）

第三步，把“用户该决定什么”和“编译器可推断什么”切开。用户决定 tensor 是否在 accelerator、在哪个 CIN scope 发生 precompute/communication，以及哪个子计算映射到哪个 backend function；编译器再依据 access pattern、level format 和 lifetime，把每个 positions/coordinates/values sub-array 绑定到 DRAM、SRAM、FIFO 或 register，并插入 load/store。[pdf:E05]（PDF 物理页 6，Section 6 开头）[pdf:E06]（PDF 物理页 7，Section 6.2–6.3）

第四步，计算 mapping 也不硬编码为某个 loop 模板，而是先用 schedule 把目标 CIN 子树隔离，再用 `map`/`accelerate` 把它替换成 backend function；剩余 `forall` 交给基于 iterator-set algebra 的 rewrite system，降成 dense iteration、single compressed iteration 或 bitvector co-iteration。[pdf:E08]（PDF 物理页 9，Table 2 与 Figure 9）[pdf:E09]（PDF 物理页 10，Table 3）

这条路径的核心不是发明另一套低层 DSL，而是让现有高层 sparse compiler IR 同时成为 memory placement、computation binding 和 hardware lowering 的交汇点。

## § 4 — 核心 Intuition

把“tensor 放在哪”和“计算在哪执行”拆成两个可调度但可协同分析的问题：用户只标出抽象的 on/off-chip 边界与要加速的 CIN 子计算，编译器再把 tensor 的 positions、coordinates、values 分别绑定到合适的物理 memory，并把稀疏迭代改写成 Spatial scanner/parallel pattern。[pdf:E04]（PDF 物理页 5，Figure 5）

真正让它奏效的是 CIN 仍保留 loop、tensor access、temporary 和 producer-consumer scope，因而 memory lifetime 与 iterator contraction 都能从同一棵 IR 树推出，而不必从已经扁平化的低层代码反推。[pdf:E05]（PDF 物理页 6，Figure 7）[pdf:E13]（PDF 物理页 14，Algorithm 1）

## § 5 — 具体方法与完整 Pipeline

以论文贯穿全文的 SDDMM 为例，输入是

\[
A_{ij}=\sum_k B_{ij}C_{ik}D_{kj},
\]

其中 \(A,B\) 为 CSR sparse matrix。下面的 pipeline 同时说明 compiler、IR、memory placement 与 binding。[pdf:E03]（PDF 物理页 4，SDDMM 的 CIN/Spatial 对照）

1. **算法、format 与 schedule 输入。** 用户用 tensor index notation 写计算；用 per-level format 描述 dense/compressed level，并给 tensor 标注 `offChip` 或 `onChip`；用 schedule 设置 `innerPar`、`outerPar`、`precompute` 和 `accelerate`。Figure 6 的 SDDMM 输入把外部 tensor 声明为 off-chip、把 reduction 的 scalar workspace 放到 on-chip register，并把该 reduction 绑定到 Spatial `Reduction` pattern。[pdf:E04]（PDF 物理页 5，Figure 6）
2. **统一降到 CIN。** index notation 先变成 loop-based CIN；原有 sparse scheduling 继续以 rewrite 方式改变 CIN。Stardust 新增的 location、`map`、`accelerate` 与 `environment` metadata 也附着在 CIN/relations 上，因此 memory 与 computation mapping 仍可在同一 IR 中分析。[pdf:E04]（PDF 物理页 5，Figure 5 与正文）
3. **用 temporary 表达 host–accelerator 数据移动。** `precompute` 把子表达式改写为 `consumer where producer`。若 temporary 与源 tensor 位于不同 region，这个 assignment 就表示 transfer；Figure 7 还表明，把 temporary 放在不同 index scope 会得到“逐 row/column 部分装入”或“整块预装入”两种不同数据移动方案。[pdf:E05]（PDF 物理页 6，Table 1 与 Figure 7）
4. **拆 tensor 为 sub-array。** 编译器不把 CSR 看成一个不透明对象，而是拆成 positions、coordinates、values；dense level 只有 dimension scalar。Figure 8 展示了 CSR matrix \(B\) 的 `B2_pos`、`B2_crd`、`B_vals` 及其迭代位置。[pdf:E06]（PDF 物理页 7，Figure 8）
5. **memory pinning。** 初始类型由抽象 on/off-chip region 决定，随后按 access pattern 与能力，把 sub-array 向相邻 hierarchy level 传播。文中规则包括：off-chip array → dense DRAM；无法识别可搬入 working set 的 sparse data → read-only sparse DRAM；affine access → dense SRAM；小型、固定尺寸、复用但随机访问 → sparse SRAM；线性且严格 enqueue/dequeue 配对的 coordinate/value stream → FIFO；on-chip scalar → register；两个 compressed level 同时遍历时生成 bitvector。[pdf:E06]（PDF 物理页 7，Section 6.2）
6. **memory lifetime 与 transfer insertion。** values 在该 tensor 最内层 access index 的 pattern body 读取，coordinates 在对应 level 的 pattern body 读取，positions 再高一层读取。allocation 默认放在首次使用 pattern 的上一层，load/store 紧接 allocation；对 FIFO values，元素必须在其 tensor access 所在层 dequeue，再 hoist 成 temporary 供更深层计算使用。[pdf:E06]（PDF 物理页 7，Section 6.3 的三条 scope 规则）[pdf:E07]（PDF 物理页 8，allocation/transfer 与 hoisting）
7. **computation binding。** schedule 先通过 `precompute` 把参与子计算的 off-chip operands 搬入 on-chip tensor，再以 `map(S, backend, f, c)` 把隔离出的 CIN statement 替换成 backend function；`accelerate` 是这组变换的复合命令，`environment` 设置全局 hardware configuration 参数。[pdf:E08]（PDF 物理页 9，Table 2 与 accelerate 定义）
8. **co-iteration lowering。** 对未显式 map 的 `forall`，compiler 根据同一 index 上 tensor level 的 union/intersection 与格式，把 iterator contraction 拆为 dense、single compressed 或 compressed-compressed 二元 pattern。compressed co-iteration 先生成 bitvector，再用 `Scan(...or...)` 或 `Scan(...and...)`；每个 bitvector level 会产生 result-position scanner 与 value scanner，value computation 使用 sparse SRAM atomic access。[pdf:E09]（PDF 物理页 10，Table 3 与正文）
9. **生成并执行。** 输出 Spatial，经既有 SARA/Spatial compiler 降到 Capstan streaming on-chip dataflow graph 和 cycle-accurate simulator。Appendix B 的 `LowerWithMemInsert` 把 iterator lowering、pos/crd/val memory selection、load、value hoisting 和 sparse co-iteration 串进一次 recursive CIN traversal。[pdf:E04]（PDF 物理页 5，Figure 5）[pdf:E13]（PDF 物理页 14，Algorithm 1）

论文不是 EMT solver 论文，因此没有开关事件、时间步进、多速率积分或数值离散；它也没有报告 fixed-point 位宽、量化误差或 FPGA RTL 实现。实际执行平台是 Capstan 的 cycle-accurate architectural simulation，而不是 FPGA 板卡实测。[pdf:E01]（PDF 物理页 1，Abstract）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有误差界或性能定理；形式化核心是 **schedule rewrite 与 iterator-set rewrite**。它们回答“怎样保持 tensor expression 语义，同时改变数据位置与 backend 执行方式”。

首先，`precompute` 把子表达式 \(e\) 写入 temporary tensor \(T\)：

\[
\forall i^* A
\;\xrightarrow{\operatorname{precompute}(e,i^*,i_w^*,T)}\;
\forall i^* A[T(i^*)/e]\ \mathbf{where}\ 
\forall i_w^* T(i_w^*)=e[i_w^*/i^*].
\]

直觉是把原表达式中的 \(e\) 换成 workspace access，同时在 `where` 的 producer 侧明确何时、按哪些 indices 生产 workspace。若 \(T\) 的 memory region 与原 tensor 不同，这个等价改写也把 transfer 的 scope 固定下来。[pdf:E05]（PDF 物理页 6，Table 1）

其次，对于 \(S\equiv\forall i^* a=e\)，`accelerate(S', backend, f, c)` 被定义为三个阶段的复合：输出先 `precompute` 到 \(a^{on}\)，所有 \(t\in tensors(e)\) 再 `precompute` 到 \(t^{on}\)，最后把替换后的子语句映射为 \(f\)。换句话说，\(c'_1\) 固定输出 placement，\(c'_2\) 固定 operands placement，\(c'_3\) 完成 computation binding；这个定义保证 backend function 只接收 on-chip tensors。[pdf:E08]（PDF 物理页 9，accelerate 的公式组）

最后，对某个 `forall` 的 iterator contraction，论文写成

\[
I=T_1\circ T_2\circ\cdots\circ T_n,\qquad \circ\in\{\cup,\cap\},
\]

并令每个 level 的格式为 compressed \(C_n\)、bitvector \(B_n\) 或 dense universe \(U\)。规则利用集合恒等关系消去 universe，例如 \(C\cap U\Rightarrow C\)、\(U\cup X\Rightarrow U\)；两个 compressed operands 则先生成 \(B_1,B_2\)，再把 union/intersection 分别降成 OR/AND bitvector scanner。其工程含义是：代数中的“谁参与这一 index 的交/并”直接决定硬件 scanner 的输入和控制，而不是先生成通用循环再做 peephole optimization。[pdf:E09]（PDF 物理页 10，Table 3）

**不确定性。** 这些 rewrite 在论文中按规则与算法描述，但没有给出机器检查的完整语义保持证明；因此“对所有合法 CIN 均语义等价”应视为实现主张，而不是已形式证明的定理。

## § 7 — 实验设计与结论

**问题 1：能否覆盖不止 SpMV 的 sparse tensor algebra？ → 实验：** 论文用 10 个 kernel，包括 SpMV、Plus3、SDDMM、\(Mat^T Mul\)、Residual、TTV、TTM、MTTKRP、InnerProd、Plus2；Table 4 同时列出表达式与 input/Spatial LOC。**答案：** Stardust 生成了原 Capstan 工作没有的 9 个 kernel，使 kernel 数量相对原工作超过 2×；但除 SpMV 外没有 handwritten Capstan implementation 可作一一比较。[pdf:E09]（PDF 物理页 10，Table 4）[pdf:E11]（PDF 物理页 12，Section 9.4）

**问题 2：生成代码能否利用 Capstan 资源？ → 实验：** 对 user schedule 做 parallelization-factor sweep，并报告 PCU、PMU、memory controller 与 shuffle network 占用。Capstan 模型有 200 PCU、200 PMU、80 MC、16 shuffle network；除 Plus2 外，各 kernel 至少逼近一个资源维度上限。**答案：** compiler 能提取 inner-loop vectorization 与 outer-loop cross-PCU parallelism，但不同 kernel 受不同资源约束；Plus2 的默认 schedule 明显没有充分 outer-parallelize。[pdf:E10]（PDF 物理页 11，Table 5/6 与 Section 9.2）

**问题 3：相对 CPU/GPU 是否更快？ → 实验：** CPU baseline 是 128-thread、四路 Xeon E7-8890 v3，GPU baseline 是 NVIDIA V100；二者都由 TACO 生成。Capstan 使用与既有工作相同的 cycle-accurate simulator，并比较 ideal memory、4-channel DDR4-2133 与 HBM-2E（1800 GB/s）。GPU 的 host-device transfer 被排除，单次迭代采用 cold cache。[pdf:E10]（PDF 物理页 11，Section 9.1） **答案：** 以 compiled Capstan HBM-2E runtime 归一化为 1，Table 7 的 geomean 是 V100 41.31、CPU 138.07；作者概括为平均 41× 与 138×。但 GPU backend 不支持 sparse result，很多时间花在 host 端初始化巨大 dense result tensor，因此这个 41× 不能外推为对成熟 sparse GPU kernel 的普遍优势。[pdf:E11]（PDF 物理页 12，Table 7 与 Section 9.4）

**问题 4：自动生成与专家手写差多少、是否减少代码？ → 实验：** 唯一可比的 SpMV 中，compiled Capstan runtime 为 1.00，handwritten Capstan 为 0.65；作者解释手写版本复制 input vector，避开 shuffle contention，并突破 shuffle network 的 outer-parallelism 上限 16。输入 LOC 从手写 Spatial 的 52 降为 Stardust 的 10，即减少 76%。**答案：** 自动生成明显减少输入代码，但尚未达到专家手写性能；这也说明缺失的 layout/replication optimization 仍然重要。[pdf:E11]（PDF 物理页 12，Table 7 与 Section 9.3）

**问题 5：结果覆盖哪些 sparsity regime？ → 实验：** 多数 2D kernel 使用原 Capstan 采用的 SuiteSparse matrices；3D kernel 多用 Facebook tensor。因为原 Capstan bitvector 对密度低于约 5% 的 tensor 表现不好，Plus3、InnerProd、Plus2 改用密度 1%、10%、50% 的 uniform random data。[pdf:E10]（PDF 物理页 11，Section 9.1）[pdf:E12]（PDF 物理页 13，Table 8 与 Appendix A） **答案：** 论文证明的是这些 dataset、format、schedule 与模拟 memory system 下的可编译性和性能，不能外推到任意超稀疏 tensor、真实板级功耗、place-and-route 后频率或 production GPU library。

## § 8 — Take-aways

**5 句话：**

1. Stardust 把 sparse tensor index notation 经 CIN、Spatial 编译到 Capstan cycle-accurate simulation，补齐了 high-level sparse algebra 到 concrete sparse RDA 的关键 lowering 链。[pdf:E04]
2. 它把用户可控的抽象 on/off-chip placement 与编译器推断的 DRAM/SRAM/FIFO/register binding 分离，同时用同一 CIN scope 决定 allocation、transfer 和 lifetime。[pdf:E05][pdf:E06][pdf:E07]
3. `map`/`accelerate` 负责具名子计算的 backend binding，iterator-set rewrite 负责剩余 sparse union/intersection 到 scanner/parallel pattern 的系统化 lowering。[pdf:E08][pdf:E09]
4. 在论文设置中，10 个生成 kernel 的 geomean runtime 相对 V100 与 128-thread CPU 分别呈现 41.31× 与 138.07× 的归一化差距，但 GPU sparse-output 缺失显著影响比较解释。[pdf:E11]
5. 它展示了可编程性收益，却没有消除 schedule、tile-fit、memory bandwidth 与 representation choice 对可用性和性能的决定作用。[pdf:E06][pdf:E10][pdf:E12]

**3 句话：** Stardust 的关键抽象是“高层选择 placement，低层完成 binding”，并让 memory lowering 与 sparse iteration lowering 围绕同一 CIN 协同发生。它把 Capstan 的可生成 kernel 从单一手写对照扩展到 10 个表达式，但性能证据仍来自 cycle-accurate simulation 和受限 baseline。最值得继承的不是某个具体 scanner，而是把 tensor format、schedule、memory lifetime 与 backend function 组织成可组合 compiler contract。

**1 句话：** Stardust 证明了 sparse tensor compiler 可以自动生成复杂的 RDA memory/scanner 代码，但也暴露出 representation、schedule 与实际 memory system 仍是决定性能的第一等设计变量。

## § 9 — 最脆弱的假设

最脆弱的假设是：**用户给出的 tiling 与 schedule 已经保证每个 on-chip array chunk 能装入目标 memory，并暴露足够的 inner/outer parallelism；编译器只需按规则 binding，无需验证或搜索这一前提。** 论文明确说 memory pinning 不考虑 array size，而是为一个 memory unit 分配最大可能尺寸，并假定 scheduling language 的 tiling 能让 array fit。[pdf:E06]（PDF 物理页 7，Section 6.2 末段）Table 5 也显示 10 个 kernel 使用的是逐 kernel 手写 schedule；Plus2 默认 schedule 只用到很少资源，说明 schedule quality 会直接改变映射结果。[pdf:E10]（PDF 物理页 11，Table 5/6）

失败代价很大：若 tile 不 fit，mapping 不是“慢一点”，而是无法成为合法的 on-chip implementation；若 fit 但 parallelism 或 communication scope 选错，bulk transfer、PMU/MC/shuffle contention 会吞掉 RDA 优势。SpMV 的手写实现仅通过复制 input vector、避开 shuffle network，就把归一化 runtime 从 compiled 的 1.00 降到 0.65，这说明编译器当前没推断出的 memory/layout decision 足以主导性能。[pdf:E11]（PDF 物理页 12，Section 9.3）

论文给出的支持是：在作者提供的 schedules 下，多数 kernel 能逼近至少一个 Capstan 资源上限，并在模拟中执行。但缺少的是 schedule 搜索成本、非法或不 fit schedule 的拒绝率、不同工程师能否稳定写出好 schedule，以及编译器对 capacity constraint 的静态校验。**基于证据的合理推断：** 这使“用户不需要底层架构知识”的主张目前更接近“用户不写底层 Spatial”，还没有完全变成“用户不承担架构约束”。

## § 10 — 最小复现实验

一周内最小复现只验证一个 claim：**CIN 上的 memory/lifetime 规则能否为 CSR SpMV 自动生成正确、可执行且接近论文资源结构的 push-memory dataflow。** 不必复现全部 10 个 kernel，也不把 CPU/GPU speedup 当作首要目标。

- **数据：** 采用 Table 8 的 `bcsstk30`、`ckt11752_dc_1`、`Trefethen_20000` 三个 SuiteSparse matrix；输入 vector 用固定 seed 生成。[pdf:E12]（PDF 物理页 13，Table 8）
- **实现：** 在一个最小 CIN AST 上实现 CSR 的 `pos/crd/val` decomposition、Section 6.2 的 memory pinning 子集、Section 6.3 的三条 lifetime rule，以及 dense/single-compressed `lowerIter`；输出一个可执行的软件 dataflow simulator 或事件 trace。以 ordinary CSR SpMV 作为数值 oracle。[pdf:E06]（PDF 物理页 7，Figure 8 与规则）[pdf:E13]（PDF 物理页 14，Algorithm 1）
- **测量：** 数值结果是否逐元素一致；每个 `pos/crd/val` 是否先 load 后 use；FIFO enqueue/dequeue 是否守恒；每个 nonzero 的 scanner/value-compute 次数；生成 trace/代码量；在相同 memory latency 参数下的 simulated cycles。
- **支持条件：** 三个 matrix 全部数值正确且没有未初始化 read/FIFO imbalance；仅改变 high-level format/schedule 就能重建数据移动；compiled trace 在趋势上复现“bulk transfer + vectorized inner reduction”，并能解释 Table 7 中 compiled SpMV 仍慢于手写版本的 shuffle/replication 差异。[pdf:E11]
- **反驳条件：** 任一 matrix 需要在 compiler 外手写 tensor-specific memory movement 才能正确运行，或 lifetime rule 在合法 CSR traversal 下产生不可配平 FIFO/越界 memory，那么核心的自动 memory lowering claim 就被直接削弱。

这个实验不声称复现 138×/41×，因为那些数字还依赖完整 Capstan simulator、HBM model、全部 kernel schedule 和 baseline toolchain；把这些都塞进一周只会让“编译规则是否成立”的判据变模糊。

## § 11 — 最强反例设计

最强反例不是再找一个 Stardust 编译失败的冷门 operator，而是构造一个 **density-controlled、baseline-fair 的 co-iteration stress test**，检验论文优势究竟来自 compiler mechanism，还是来自 Capstan bitvector 与 baseline 选择恰好有利。

固定同一组 union-heavy（Plus3/Plus2）与 intersection-heavy（SDDMM/InnerProd）表达式，保持 dimension 和 nonzero value distribution 一致，只把 density 从 \(10^{-5}\) 扫到 \(5\times10^{-1}\)。对 Stardust 固定 memory bandwidth 与 resource budget，同时记录 bitvector 扫描的 dense coordinate blocks、有效 nonzero、scanner cycles、PMU/MC traffic 和总 cycles；对照端使用真正支持 sparse result 的 GPU kernel，避免论文 TACO GPU baseline 的 dense-result zero initialization。再加入与本文 related work 中 SPU stream-join 或 ExTensor hierarchical intersector 同类的 coordinate-driven co-iteration 作为机制对照，而不是只换平台名称。[pdf:E11]（PDF 物理页 12，GPU baseline 限制）[pdf:E12]（PDF 物理页 13，Related Work 与 Appendix A）

预测性的失败条件是：随着 density 降低，Stardust bitvector 仍按 dense coordinate space/bitvector width 扫描，cycles per nonzero 急剧上升；论文也明确承认原 Capstan 对低于约 5% density 的 tensor 表现不好，并为 Plus3、InnerProd、Plus2 改用更高密度的 synthetic data。[pdf:E10]（PDF 物理页 11，Section 9.1）[pdf:E12]（PDF 物理页 13，Appendix A）若在公平 sparse-output baseline 下，Stardust 的优势在超稀疏区间消失或反转，那么“对 sparse tensor algebra 的普遍 RDA 加速”应收缩为“对适合 bitvector representation 的 sparsity regime 有效”。

这个反例还可区分一个替代解释：如果提升主要来自 1800 GB/s HBM 与 bulk transfer，而不是 co-iteration lowering，那么固定 bandwidth 后不同 representation 的 scanner work 不应显著改变结论；反之，coordinate-driven 对照若在相同 bandwidth 下显著减少扫描工作，就表明 representation 才是主因。[pdf:E10]（PDF 物理页 11，Figure 10 与 methodology）

## § 12 — Follow-up Research Bet

**主 idea：把“稀疏 level format”从存储描述提升为可综合的 co-iteration protocol，并让 compiler 与 RDA 共同生成 representation-native operator network。**

新的研究问题是：能否从 tensor contraction 的 iterator algebra 出发，不预设 compressed level 最终都变成 bitvector scanner，而是为每个 level 静态综合 coordinate-stream join、bitvector scan、segmented run traversal 等不同 protocol 及其物理连接拓扑？这首次可能让同一套 tensor index notation 在极稀疏、局部成簇和中高密度区间分别生成不同的、结构上原生的 RDA，而不是把所有 sparse co-iteration 挤进 Capstan 的 `genBitvector → Scan(and/or)` 路径。

核心因果链是：扩展 CIN iterator 的表示集合与 rewrite algebra → rewrite 不再只输出 `Foreach/Reduce/bitvector Scan`，而输出带 backpressure、position semantics 和 memory-port contract 的 protocol graph → physical memory analysis 同时决定 coordinate/value stream 的 placement 与 operator adjacency → 硬件生成器据此实例化 stream-join/intersector/scanner 网络 → 极稀疏时工作量随实际 coordinates 而不是 dense bitvector blocks 增长。它至少改变了三类基本设计变量：**状态表示**（bitvector/coordinate/segment protocol）、**硬件拓扑**（固定 scanner 到 synthesized operator network）和 **compiler–hardware boundary**（backend function 不再是预存在的 pattern，而是由 iterator algebra 生成的 protocol graph）。

这个押注由两类论文特异证据支撑。方法上，Table 3 已把 iteration 明确建模成 \(U,C,B\) 上的 union/intersection rewrite，说明表示选择本来就在 compiler semantic core；当前 compressed-compressed 路径却固定先 `genBitvector` 再 scanner。[pdf:E09]（PDF 物理页 10，Table 3）实验与 limitation 上，论文承认 bitvector 对低于约 5% density 的 tensor 不利，并为三个 kernel 改用 1%、10%、50% synthetic data；与此同时，related work 中 SPU 的 stream-join 与 ExTensor 的 hierarchical intersector 表明不同物理组合机制真实存在。[pdf:E12]（PDF 物理页 13，Appendix A 与 Related Work）

最大收益不是“更鲁棒”，而是扩大可计算对象：一套高层 sparse tensor program 可以综合成适配不同 sparsity geometry 的数据流机器，并把 representation/hardware co-design 变成 compiler 可搜索的科学对象。最大风险是 protocol graph 的选择与 buffer sizing 可能形成组合爆炸，而且 cycle-accurate simulator 中的收益未必能在 routing、clock frequency 和 area 约束下保留。

首个证伪实验使用 §11 的 density-controlled kernel set，在完全相同的 memory bandwidth、PCU/PMU budget 与 arithmetic pipeline 下比较三种静态生成的 protocol：纯 bitvector、纯 coordinate-stream join、由扩展 rewrite algebra 生成的 per-level protocol graph。关键判据不是总 speedup，而是 `cycles/nonzero`、scanned empty coordinates、buffer occupancy、network hops 和 post-layout-estimated frequency；如果生成图的优势在固定 bandwidth 后消失，或主要来自额外 area/ports，那么“protocol synthesis 而非 memory bandwidth/资源堆叠导致能力提升”的核心机制就被反驳。

与本文最近工作在本文所述范围内的实质区别是：Stardust 固定以 Capstan parallel patterns 为 backend，并把 SPU/ExTensor 视为其他 target；这个 idea 把那些 co-iteration 机制抽象进同一个 iterator-protocol IR，并让 backend topology 成为编译结果。**候选判断：** 本任务没有补充全文检索，因此不声称这一方向具有 novelty。

**Wild-card alternative（一句话，不同机制）：** 把研究对象从单 kernel 改成 persistent multi-operator sparse tensor pipeline，让 compiler 在整段 tensor program 上保留 on-chip compressed intermediates并联合生成 producer-consumer temporal graph，以“消除 kernel 间 materialization”而非“改变单个 co-iteration representation”获得新能力；同样仅是候选判断，不声称 novelty。
