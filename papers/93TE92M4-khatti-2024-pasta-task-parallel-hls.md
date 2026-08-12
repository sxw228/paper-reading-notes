# PASTA: Programming and Automation Support for Scalable Task-Parallel HLS Programs on Modern Multi-Die FPGAs

**作者：** Moazin Khatti, Xingyu Tian, Ahmad Sedigh Baroughi, Akhil Raj Baranwal, Yuze Chi, Licheng Guo, Jason Cong, Zhenman Fang  
**出处：** ACM Transactions on Reconfigurable Technology and Systems, Vol. 17, No. 3, Article 42  
**年份：** 2024  
**DOI：** 10.1145/3676849  
**Zotero key：** 93TE92M4  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

PASTA 处理的不是“怎样让 HLS 生成 RTL”这一基础问题，而是更靠后的规模化问题：一个由许多并发 task 组成的 HLS accelerator 放进现代 multi-die FPGA 后，跨 SLR 的长连线和拥塞会把全局关键路径拖慢；等 placement and routing 暴露真实 net delay 时，HLS 已经固定了 cycle-accurate semantics，后端不能随意补寄存器。论文指出，跨 die 信号延迟可达到同 die 中等长度连线的约八倍，而 HLS 的预表征延迟模型尤其难以准确预测 net delay。[pdf:E01]（PDF 物理页 3，Section 1）

已有 TAPA/AutoBridge 路线用 coarse-grained floorplanning 把 task 放进较小 slot，再给跨 slot 的 latency-insensitive FIFO 插 pipeline，已经能显著改善 stream-based task graph；问题是大量实际 accelerator 采用 load-compute-store、数组分块和 ping-pong buffer，而不是纯 FIFO stream。若工具只支持 FIFO，程序员必须重写通信结构，或者失去物理设计协同优化的收益。[pdf:E01]（PDF 物理页 3，Section 1）

因此论文的核心研究问题是：能否给 task-parallel HLS 增加一种同时满足 vendor HLS 接口、memory partition、ping-pong overlap 和任意链路 pipelining 的 buffer channel，并让前端编程抽象与后端 placement/pipelining 使用同一份 task graph 元数据？作者将它实现为端到端 PASTA toolflow，并报告在 AMD/Xilinx Alveo U280 上，相对相应 baseline 的平均频率提升为 25%，峰值为 89%。[pdf:E02]（PDF 物理页 4，Section 1）

## § 2 — 前人工作与不足

**论文直接陈述的最近工作。** PASTA 直接建立在 TAPA/AutoBridge 上。TAPA 提供显式 coarse-grained task-parallel/dataflow 编程模型，AutoBridge 从 task graph 提取资源与连接信息，用 ILP 做 slot mapping 和 channel routing，再对跨边界 FIFO 加 pipeline。这个组合的边界不是 floorplanning 不够强，而是通信语义只覆盖 latency-insensitive FIFO；ping-pong array buffer 涉及可随机访问的 memory ports、partition 后的多个 memory cores、section ownership 和 producer/consumer 两套 FSM，不能直接套 FIFO 边的处理方式。[pdf:E03]（PDF 物理页 5，Fig. 1 与贡献说明）

**论文所列相关文献。** 多 die placement 工作能够减少跨 die 信号数量，却未必缩短仍然必须跨 die 的关键路径；迭代 HLS 与 physical design 的方法需要反复运行昂贵的后端；routing-congestion prediction 可以指出问题区域，但通常把修复留给用户；fine-grained dynamic-HLS buffer insertion 针对的是电路级 path/throughput，而 PASTA 针对显式 task graph 的 coarse-grained channel。论文还比较了面向 Halide/CGRA 的 unified buffer 与从隐式并行程序生成动态 task graph 的 TAPAS：前者的输入与硬件目标不同，后者处理 fine-grained dynamic tasks；PASTA 处理显式、静态、粗粒度 task graph 的 multi-die frequency optimization。[pdf:E14]（PDF 物理页 28，Section 7）

这些比较是**论文对相关工作的归纳**，不是本卡独立完成的系统文献核验。特别是“PASTA 是否在所有 buffer-aware HLS physical co-optimization 中最早”仍未闭合；在本次来源封闭条件下，只能确认作者把相对 TAPA/AutoBridge 的增量明确定位为 buffer channel 的 abstraction、frontend API/compiler 与 backend placement/pipelining。

## § 3 — 重建作者的思考路径

可以把作者的路径重建为四步。第一，现代 multi-die FPGA 的主要 timing failure 往往来自跨 slot net，而不是局部组合逻辑；因此只在 HLS 层调 pragma 或只在后端移动 cell 都缺少另一侧信息。第二，TAPA/AutoBridge 已证明一条可行原则：把程序暴露为 task graph，并让跨 slot 通信具备 latency-insensitive handshake，后端就能安全地 floorplan 和 pipeline。第三，真实 HLS design 中的数组块不是 FIFO item 流；producer 与 consumer 需要在整段 memory section 上重叠工作，partition 又会把一个逻辑数组变成多个可并发访问的 memory cores。第四，若把“section 所有权”从 memory data path 中抽出来，用 token FIFO 同步 free/occupied section，data path 就能继续保持 ap_memory，控制 path 则获得 FIFO handshake，于是既兼容 Vitis HLS，又为跨 slot pipeline 留出结构化插入点。[pdf:E05]（PDF 物理页 9，Fig. 4 与 Section 3.1）

这一思路还解释了为什么作者没有把 buffer 塞进 producer 或 consumer task：channel 必须成为独立 RTL module，才能独立生成不同 partition 配置、计算资源、决定物理归属并在 task 之间插 pipeline。换句话说，PASTA 改变的关键假设是“buffer 只是 HLS function 内的数组”，把它提升为 task graph 中带 ownership protocol 的一等通信边。

## § 4 — 核心 Intuition

把一个 ping-pong buffer 拆成“可分区的 dual-port memory data plane”和“free/occupied token control plane”，producer 与 consumer 就能靠 token 交换 section 所有权，而不依赖固定周期延迟。[pdf:E05]（PDF 物理页 9，Fig. 4）前端用 RAII 风格的 `acquire()`/section 生命周期隐藏 token 操作，后端再把 memory、free FIFO 与 occupied FIFO 分别放到合适一侧并给长路径加 pipeline。于是同一个 buffer 同时保持数组式随机访问、任务间 overlap、vendor HLS compatibility 和跨 die timing closure 所需的 latency insensitivity。

## § 5 — 具体方法与完整 Pipeline

以论文的 vector-add task graph 为例，输入数组先经 `load` task 进入 channel，`add` task 消费两个输入并生成结果，`store` task 写回 off-chip memory。顶层 C++ 用 `task().invoke(...)` 实例化 task；`istream`/`ostream` 表示 FIFO 端点，`ibuffer`/`obuffer` 表示 buffer consumer/producer，`mmap` 表示 off-chip memory，scalar 则从 host 传入。[pdf:E04]（PDF 物理页 6，Fig. 2、Listing 1 与 Section 2.1）完整流程如下：

1. **写程序与建图。** 用户声明 buffer 的 element type、multi-dimensional shape、section 数、每一维的 `normal`/`complete`/`cyclic`/`block` partition 以及 BRAM/URAM 类型。一个 section 意味着不能 producer/consumer overlap，两个 section 即 double buffering，也允许更多 section。[pdf:E17]（PDF 物理页 12，Listing 2 与 Section 4.1）
2. **解析与变换。** 基于 Clang/LLVM 的 AST parser 找出 task、channel 配置与 connectivity，输出 task graph，并为各 task 生成变换后的 HLS C++。toolflow 随后并行调用 Vitis HLS，必要时再调用 Vivado RTL synthesis 获得更准确的资源报告。[pdf:E03]（PDF 物理页 5，Fig. 1）
3. **生成 buffer RTL。** 一个 buffer 由多个 dual-port memory cores、free-sections FIFO 和 occupied-sections FIFO 构成。初始时 free FIFO 含全部 section token；producer 取 free token，写对应 section，结束时把 token 放入 occupied FIFO；consumer 取 occupied token，读对应 section，再把 token 还给 free FIFO。这样不同 section 可 ping-pong，partition 后的多个 cores 可被 loop unrolling/pipelining 并行访问。[pdf:E05]（PDF 物理页 9，Fig. 4 与 Section 3.1）
4. **隐藏协议细节。** producer 或 consumer 调用 `acquire()` 后得到 section object；object 离开作用域时自动把 token 交给另一条 FIFO。software simulation 使用 thread-safe C++ 实现相同协议。[pdf:E02]（PDF 物理页 4，Section 1 的 frontend 实现说明）HLS 版本只暴露 vendor 支持的 `ap_fifo` 和 `ap_memory` ports；parser 自动插入 interface/partition pragmas，并用一个总被 memory access 写入的 `volatile` Boolean 建立 artificial dependency，防止 HLS 把 token release 排到 data access 之前。[pdf:E07]（PDF 物理页 18，Fig. 9 与 Section 4.4.4）
5. **选择 memory 实现。** 如果分析得到 producer 只写、consumer 只读，PASTA 选择 S2P BRAM；否则选择两端均可读写的 T2P BRAM，URAM 则使用 T2P。论文指出 S2P 在 36/72-bit 宽配置下可把 BRAM 消耗降至 T2P 的一半；memory generator 只为出现的 unique configuration 生成 parameterized RTL。[pdf:E06]（PDF 物理页 11，Section 3.2.2）
6. **floorplan 与 route。** high-level floorplanner 依据 task/channel 资源和 U280 slot model，用一个 ILP 将 task 映射到 slot、尽量减少跨 slot wires且满足资源限制，再用另一 ILP 为跨 slot channel 选择可实现的 route。[pdf:E16]（PDF 物理页 8，Section 2.2.4）RTL stitcher 根据结果实例化 task/channel、插 pipeline、发出 placement constraints，并生成最终 `xo`/XCLBIN 流程。[pdf:E03]（PDF 物理页 5，Fig. 1）
7. **buffer 专用 placement/pipelining。** occupied FIFO 和 memory cores 靠 consumer 放置，从 producer 一侧 pipeline；free FIFO 靠 producer 放置，从 consumer 一侧 pipeline。memory write 可只增加完成延迟，read response 则会往返经过寄存器：若插入 (l) 级，单次 read 额外等待为 (2l) cycles，producer 需要按新 latency 重新综合。[pdf:E08]（PDF 物理页 21，Fig. 11 与 Sections 5.2.2-5.2.3）Figure 12 的例子把 producer 放 slot 1、consumer 放 slot 4，channel route 为 (s_1\rightarrow s_2\rightarrow s_4)，并把三类子通道从各自合适一侧 pipeline。[pdf:E09]（PDF 物理页 22，Fig. 12 与 Section 5.2.4）
8. **保护有反馈读的 producer。** 若 producer 也读 buffer，且 read latency 会抬高 loop II 或未 pipelined loop 的 iteration latency，PASTA 默认约束 producer/consumer 同 slot，避免 channel pipeline；用户可以显式强制分开，此时 parser 修改 `ap_memory` latency pragma 并重新综合 producer。[pdf:E08]（PDF 物理页 21，Section 5.2.3）

最终输出不是一个抽象 schedule，而是经过 Vitis/Vivado placement and routing 的 accelerator bitstream；作者用实际 board execution 检查频率收益是否转化为执行时间收益。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有性能正确性的复杂证明，但给出了 buffer partition 到物理 memory 数量的核心资源模型。设 buffer 有 (n) 维，维长为 (D=\{d_1,\dots,d_n\})，section 数为 (s)，元素宽度为 (w)。对第 (i) 维，partition factor 定义为

\[
f(i)=\begin{cases}
1, & \text{normal},\\
d_i, & \text{complete},\\
\mathrm{cyclic}_f(i), & \text{cyclic},\\
\mathrm{block}_f(i), & \text{block}.
\end{cases}
\]

于是逻辑 memory core 数为 (c=\prod_i f(i))，总 entry 数为 (t=s\prod_i d_i)，每个 core 的深度为

\[
d_p=\frac{t}{c}=s\prod_i\frac{d_i}{f(i)}.
\]

直觉是：section 数 (s) 增加纵向容量，partition factor 增加横向 bank 数；partition 越强，并行端口越多，每个 bank 越浅。若一种物理 BRAM/URAM bank 的宽度和深度分别为 (W,D_p)，实现一个逻辑 core 需要

\[
\left\lceil\frac{d_p}{D_p}\right\rceil
\left\lceil\frac{w}{W}\right\rceil
\]

个物理 banks。[pdf:E06]（PDF 物理页 11，Eqs. (1)-(2) 与 Section 3.2.2）这组式子重要之处不在代数本身，而在它让 floorplanner 在运行后端综合之前，能从 HLS type/shape/partition 元数据估计每条 buffer edge 的 BRAM/URAM 占用。

memory-channel pipeline 的另一条简式关系是：若 data/address path 插入 (l) 级寄存器，write 延后 (l) cycles，而需要 response 的 read 增加 (2l) cycles。若 pipelined loop 的 II 不变，这通常只增加与 trip count 无关的 pipeline depth；若 read-after-write 令 II 依赖该 latency，或者 loop 未 pipeline，总 latency 会按 trip count 放大。[pdf:E08]（PDF 物理页 21，Section 5.2.3）

## § 7 — 实验设计与结论

**问题 1：PASTA 是否在设计规模增大时维持更高 post-route frequency？** 作者在 U280 的 3 个 SLR/HBM 平台上测试 6 个 benchmarks、共 32 个 design points：Rodinia HLS 的 KNN、k-means、Pathfinder、NW，以及 real-world HiSpMV、Minimap。前四者的 baseline 是标准 Vitis HLS flow；后两者 baseline 仍用 PASTA 编程，但关闭 frequency optimization，因此两组 baseline 定义并不完全相同。除 SpMV 以 235 MHz 为 target 外，其余 target 为 300 MHz；每一点都做了 on-board execution。[pdf:E11]（PDF 物理页 25，Table 2 与 Section 6.2）Figure 15 显示小设计两者接近，PE 增加后 baseline frequency 明显下滑，而 PASTA 较稳定。[pdf:E10]（PDF 物理页 24，Fig. 15）作者报告 32 点平均 frequency improvement 为 25%、峰值为 89%；仅看平均资源占用高于 25% 的大设计，平均提升为 46%。SpMV 160-PE baseline 无法 route，PASTA 达到 209 MHz。[pdf:E12]（PDF 物理页 26，Section 6.3）**答案：** 对该 U280 benchmark set，证据支持 PASTA 缓解随着规模增长而出现的 cross-slot net bottleneck；它不证明能修复高 logic-delay path，NW 的低频结果正是作者给出的反例边界。

**问题 2：频率提升是否转化为真实执行速度？** 作者比较 frequency gain、按 compute/memory-bound 性质计算的 expected gain 和 board-measured actual gain。compute-bound 四项的 actual 与 expected 平均相差 1%、最大 5%；memory-bound SpMV/Minimap 在单个 512-bit HBM port 约 225 MHz 后受 bandwidth 饱和限制，expected 与 actual 平均相差 6%、最大 9%。全 32 点的平均 frequency、expected performance、measured performance improvement 分别为 25%、24%、22%；大设计分别为 46%、45%、42%。[pdf:E12]（PDF 物理页 26，Section 6.4；大设计汇总延续到物理页 27）**答案：** 提频总体转化为加速，但 memory-bound design 的收益被 off-chip bandwidth 和 dynamic access pattern 削弱，不能把 MHz 比例直接外推成应用 speedup。

**问题 3：收益是否来自额外堆资源？** post-route 数据显示 baseline 与 PASTA 的平均资源差为 0.18%，极端点最大 2.65%；作者据此判断 frequency optimization 的资源 overhead 很小，提升不是来自显著降低 utilization。[pdf:E13]（PDF 物理页 27，Section 6.5）其 buffer resource model 先对 240 种 memory-core configuration 检查，平均误差为 0.35 BRAM banks，并在 6 个 benchmarks 上报告 100% accuracy。[pdf:E18]（PDF 物理页 20，Section 5.1.3）**答案：** 在这组实现中，主要变量确实是 placement/pipelining，而不是资源规模变化。

**问题 4：编译代价与 memory cascade 是否受控？** floorplanning 平均耗时 7 分钟，而大设计 placement and routing 可达 15-24 小时；最大相对 overhead 出现在 SpMV-64PE，为 30 分钟、约占总 place-and-route 时间的 9%。Minimap 的 cascade-height sweep 中，无 cascading 为 242.5 MHz，默认高度 16 为 234 MHz，但高度 2-5 的结果不单调，作者明确认为还需要更多 deep-buffer benchmarks，不能推出普遍尺度律。[pdf:E13]（PDF 物理页 27，Table 3 与 Sections 6.6-6.7）**答案：** floorplanner 本身不是主要编译成本；cascade height 的作用尚未形成稳定结论。

实验能支持的是：在一块 U280、这 6 个应用及其给定规模 sweep 上，buffer-aware physical co-optimization 改善 routing-dominated timing，并在板上得到相应但非总成比例的性能收益。它不能外推到其他 FPGA families、不同 NoC/interposer、动态 task graph、logic-dominated critical path，也没有把 PASTA 与所有可能的手写 RTL floorplan 作比较。论文结论再次给出 32 点平均 25%、最高 89%、大设计平均 46% 的 frequency improvement。[pdf:E15]（PDF 物理页 29，Section 8）

## § 8 — Take-aways

**5 句话。** 第一，PASTA 把 task-parallel HLS 的通信边从 FIFO 扩展到可 partition、可 ping-pong 的 buffer channel。第二，它用 memory cores 承载数据、用 free/occupied token FIFO 承载 section ownership，使 buffer 在任意 pipeline latency 下仍能同步。第三，frontend 的 type/API/parser、resource model、ILP floorplanner 和 RTL stitcher 是同一个闭环，而不是彼此脱节的优化脚本。第四，实验证据最强的地方是大设计：资源越重，baseline 越容易被 cross-slot net 拖慢，PASTA 的相对收益越明显。第五，频率不是性能的充分条件；HBM bandwidth、dynamic access、logic delay 和 producer read dependency 都会限制最终收益。

**3 句话。** 这篇论文真正增加的是一个可被 physical design 操作的 buffer communication primitive，而不只是新的 C++ API。它的有效性来自“显式 task graph + latency-insensitive ownership + layout-aware pipelining”三者同时成立。U280 结果支持该组合能改善 routing-dominated scalable HLS design，但没有证明跨平台普适性或全局 novelty。

**1 句话。** PASTA 让 ping-pong array buffer 也成为可以被编译器安全跨 die 放置和流水化的 task-graph edge。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**规模化设计的主导 timing bottleneck 位于可识别、可流水化的 task-channel 跨 slot net，而且 producer 对 buffer memory 的读取不会形成无法隐藏的 loop-carried latency。** 一旦关键路径主要是 task 内高 logic delay，增加 channel pipeline 不会改善频率；一旦 producer 存在 read-after-write dependency，跨 slot memory read 的 (2l) 额外延迟可能抬高 II，并按 trip count 放大执行时间。[pdf:E08]（PDF 物理页 21，Section 5.2.3）

论文给了两类支持。其一，六项 scale sweep 中，小设计收益有限而大设计收益增加，且作者把 baseline 降频归因于 cross-slot net；SpMV 160-PE 的 route failure 与 PASTA 209 MHz 形成强案例。[pdf:E12]（PDF 物理页 26，Section 6.3）其二，作者显式识别 producer-read 三种情况，并默认把可能受害的 producer/consumer 同 slot，避免引入 memory pipeline latency。[pdf:E08]（PDF 物理页 21，Section 5.2.3）

但这也暴露证据缺口：论文没有报告“多少 buffer edge 因 producer read 被迫同 slot”、这些 constraint 对 ILP feasibility 和全局 frequency 的代价，也没有专门构造 loop-carried read-after-write 的压力测试。NW 已显示即使 2 PE、约 20% resources 时也只有约 220 MHz，因为瓶颈是 high logic delay，作者明确说这不属于 PASTA 的目标范围。[pdf:E12]（PDF 物理页 26，Section 6.3）因此，当前证据证明的是一类 routing-dominated design 的可扩展性，不是任意大 HLS program 的 timing closure。

## § 10 — 最小复现实验

一周内不必复现六个完整应用，可以只验证最核心的“buffer edge 可安全流水化并改善跨 SLR timing”claim。

1. 在同一块 U280 上用 PASTA 写一个三 task `load -> transform -> store` design；`load` 与 `transform` 之间使用 2-section、cyclic-partition 的 BRAM buffer，producer 只写、consumer 只读。固定 data size、unroll factor、HLS directives 与 target 300 MHz。
2. 构造三个只差后端约束的版本：A 为无 coarse floorplan/pipeline baseline；B 强制 producer/consumer 跨 SLR 但关闭 buffer pipeline；C 使用 PASTA 的 memory/FIFO placement 与 pipeline。每个版本至少跑 3 个 implementation seeds，避免把单次 Vivado placement 偶然性当作机制效果。
3. 对每版记录 post-route WNS/achieved frequency、跨 SLR critical path 类型、LUT/FF/BRAM、cycle count 和 board execution time；对随机输入逐元素比较 output，确保 latency change 没有改变 token/data 顺序。
4. **支持条件：** C 在所有 seed 上保持 bit-exact output，资源增量小，同时相对 B 显著缩短跨 SLR critical path、提高 achieved frequency；A/B/C 的 cycle count 除固定 fill/drain latency 外不变。**反驳条件：** C 的关键路径没有改善、功能结果错位，或增加的 pipeline 使 steady-state II/board time 恶化到抵消频率收益。
5. 若时间允许，只加一个最小对照：让 producer 在 pipelined loop 中读取刚写的 buffer 值，观察重新综合后的 II 是否从 1 上升。该对照直接检验论文对 producer-read hazard 的边界，而不需要复现完整 benchmark。

这个实验采用论文的 buffer/token 与 placement 结构作为事实前提，[pdf:E09]（PDF 物理页 22，Fig. 12）但“3 个 seeds 足够判断稳定趋势”是本卡的**实验设计判断**，不是论文结论。

## § 11 — 最强反例设计

最强反例不是再找一个小设计说“没有提频”，而是构造一个**必须跨 slot、producer 又存在 loop-carried read-after-write 的大 task graph**。令 producer 在每次迭代先读同一 buffer section 的旧状态、更新后写回，下一次迭代依赖该值；consumer 同时读取完成的 section。再用资源和 HBM placement constraints 迫使 producer 与 consumer 分处不同 SLR，使“默认同 slot”不可行。

对比三种实现：PASTA 强制跨 slot 并按 `ap_memory latency` 重新综合、手写 local-state producer 加显式 bulk transfer、以及把状态通信改为 FIFO message 的版本。测量 loop II、trip-count 扩展曲线、fmax、end-to-end throughput 和 ILP 是否找到合法 placement。论文自身预测 memory channel 插 (l) 级寄存器时 read latency 增加 (2l)，在 read-after-write 情况下可能提高 II；它当前用同 slot constraint 规避，而不是消除这个因果链。[pdf:E08]（PDF 物理页 21，Sections 5.2.2-5.2.3）

若 PASTA 虽提高 fmax，却因 II 随跨 SLR latency 增长而使 throughput 低于两种对照，或者同 slot constraint 让大设计无法合法映射，就说明“latency-insensitive buffer”只保证 protocol correctness，不保证 performance insensitivity；这会直接削弱其可扩展性主张。若 PASTA 仍能保持 II、合法 placement 与正确结果，则该反例反而给核心机制提供比现有 benchmark sweep 更强的证据。

## § 12 — Follow-up Research Bet

### 主 idea：把 section ownership 变成可迁移的空间状态，而不是固定 memory 的访问许可

**候选研究问题。** 能否把 PASTA 的 token 从单纯的 section 编号扩展为 `section + epoch + physical residency`，让每次 producer/consumer ownership transfer 同时触发整段数据在 slot-local memories 之间迁移，从而把 buffer channel 变成一个随 task phase 改变位置的 distributed buffer fabric？这首次使编译器可以让 producer 与 consumer 都主要访问本地 memory，又用 coarse burst transfer 穿过 pipelined cross-SLR link；被优化的对象不再只是 static task placement，而是“数据 section 在时间中的物理驻留轨迹”。

**核心机制与因果链。** producer acquire 一个本地 free section并完成局部读写；release 时，token 携带 epoch 和目标 residency，DMA-like burst engine 将完整 partitioned section 通过预定 route 推送到 consumer-local banks；数据到达后 occupied token 才变为可见。consumer 在本地完成随机访问后，以相反方向或重新分配方式归还 residency。粗粒度迁移把多个细粒度 `ap_memory` read round trips 聚合成顺序 burst，因而可能用 bandwidth 换掉 loop 内 (2l) latency；同时 epoch 防止 ping-pong section 在跨 die 传输中被提前复用。基本设计变量至少改变了**状态表示**（token 变为 location/epoch-bearing ownership state）、**硬件映射**（memory residency 随 phase 变化）和**时间尺度**（每次 access 变为每个 section 的 bulk movement）。

**论文特异依据。** PASTA 已证明 free/occupied token 能把 section ownership 与 data plane 分离，且 partition factor 决定多个 memory cores 的并行结构。[pdf:E05]（PDF 物理页 9，Fig. 4）它同时表明 static 方案把 memory 固定在 consumer 一侧，producer read 需要 (2l) 额外 latency并可能抬高 II。[pdf:E08]（PDF 物理页 21，Fig. 11）实验端则显示 memory-bound SpMV/Minimap 的频率收益不能完全转化为性能，作者把差距部分归因于 bandwidth saturation 与 dynamic access pattern；这意味着新机制必须把 section-transfer bytes 和 HBM traffic 一起建模，而不能只优化 fmax。[pdf:E12]（PDF 物理页 26，Section 6.4）此外，cascade-height sweep 没有单调关系，提示“更深/更多级 memory structure 自动改善 fmax”不是可靠解释，首个实验必须隔离 residency migration 本身。[pdf:E13]（PDF 物理页 27，Table 3）

**与最近工作的实质区别。** 在本论文给出的来源范围内，TAPA/AutoBridge 把 FIFO item 作为静态 task edge，PASTA 把 partitioned buffer memory 静态放在 consumer 侧，unified buffer 工作则面向受限 Halide 到 CGRA 的 buffer mapping。[pdf:E14]（PDF 物理页 28，Section 7）这里的候选把“物理驻留位置”加入运行时 ownership state，并把一次 section handoff 定义为数据迁移事件；problem、representation、experimental object 均不同。但本次没有补充全文检索，**这只是候选判断，不声称 novelty 已闭合**。

**收益、风险与首个证伪实验。** 最大收益是让含 producer local reuse、consumer random access 和 cross-SLR separation 的 task graph 不再在“远程细粒度读”与“强制同 slot”之间二选一；最大科学风险是 section transfer volume 过大，复制时间、额外 banks 与 NoC/SLR bandwidth 反而超过省下的 read latency。最小实验选一个固定总数据量、可调 section size 与 producer reuse count 的双 task kernel，对比 static consumer-resident PASTA、local-state + hand-written bulk copy、token-routed migratory buffer；扫 1-4 个 SLR hops、partition factor 和 reuse count，测 II、transfer bytes、fmax、BRAM/URAM 与 end-to-end throughput。若迁移版只在 fmax 上升而 throughput 不升，或优势不能随 reuse count 呈现可预测的 crossover，它就不能支持上述因果机制；若在相同 link bandwidth 下，迁移版通过减少 fine-grained round trips 而跨过明确 crossover，则能排除“只是多加 pipeline registers”的最强替代解释。

**Wild-card alternative：** 不改 buffer microarchitecture，而把 cascade height、section depth、partition factor、SLR hop count 与 placement seed 做成主动设计实验，寻找可跨 benchmark 预测 post-route frequency 的经验尺度律；这是新的 measurement/data-generation 机制，与主 idea 的运行时 residency migration 不同，同样不声称 novelty 已闭合。
