# From C/C++ Code to High-Performance Dataflow Circuits

作者：Lana Josipović、Andrea Guerrieri、Paolo Ienne  
出处：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems，Vol. 41，No. 7  
年份：2022  
DOI：10.1109/TCAD.2021.3105574  
Zotero key：QFHAXC9H  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的问题是：**怎样从普通 C/C++ imperative code 自动生成高性能、同步、动态调度的 FPGA dataflow circuit，使操作何时执行由运行时真实的数据、控制和内存依赖决定，而不是在综合时被固定进一个最坏情况 schedule。**作者指出，主流 HLS 通常把每个操作绑定到预定 clock cycle；当控制条件、内存地址别名或单元延迟在编译时不可判定时，static scheduling 只能按最坏情况保守串行化。论文的直接主张是，这种做法在规则 kernel 上有很好的 performance-per-cost，但在 irregular、control-dominated 和 general-purpose code 上会丢失本可利用的并行性；动态调度改变的不是某一个局部优化，而是“何时决定依赖是否存在”这一根本假设。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

Fig. 1 给出了最小但很有代表性的例子：循环每次先算 `d=a[i]-b[i]`，仅在 `d>0` 时更新具有 loop-carried dependence 的累加变量 `s`。静态流水 schedule 为所有迭代都预留加法时间，顺序状态机则只在需要时做加法却放弃跨迭代重叠；动态 schedule 同时保留跨迭代的 load、subtraction、comparison 并行性，只在真实发生 `s=s+d` 依赖的迭代收缩并行度。[pdf:E02]（PDF 物理页 2，Fig. 1）这说明论文瞄准的并非“让已规则的流水线再快一点”，而是把编译时无法证明的独立性推迟到电路运行时判定。

重要性来自两个层面。工程上，若 HLS 只能高效处理容易静态分析的 loop，软件开发者仍需大量 pragma、code restructuring 和专用知识，FPGA 的可编程性边界不会真正扩大。体系结构上，ready/valid handshake 让电路能自然吸收 variable latency，并根据真实控制路径和地址关系展开 out-of-order execution；这为更一般的 speculation 留出了接口。这里必须保留作者给出的边界：动态调度不是无条件优于静态调度，而是用更多 control、buffer 和 memory-ordering hardware 换取运行时适应性。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

## § 2 — 前人工作与不足

**论文对相关工作的直接归纳**可以分成三类。第一类是 Vivado HLS、LegUp、PandA 等传统 static HLS，以及 modulo scheduling。它们在访问模式规则、依赖可静态消解时能形成高吞吐 pipeline；问题是遇到不可判定的 memory/control dependence，只能采用 pessimistic schedule。多 schedule 运行时选择、ElasticFlow、pipeline flushing、application-specific hazard detection、prefetch 和 access/execute decoupling 等工作确实加入了一定动态性，但仍以静态 schedule 为骨架，适用范围受特定 loop 形态、已知参数或专门 hazard logic 限制。[pdf:E03]（PDF 物理页 12，Section VIII Related Work）

第二类是 latency-insensitive、elastic、asynchronous 或 functional dataflow circuit。它们已经提供 handshake component、动态 pipeline 或 dataflow network 的关键构件，但论文认为其不足在于：缺少从一般 imperative C/C++ 到细粒度 circuit 的完整转换规则，尤其没有把 control-flow token、SSA phi 的顺序、deadlock-free buffer placement 和 out-of-order memory interface 作为一个闭合系统处理，也很少与现代 commercial HLS 做端到端对比。[pdf:E03]（PDF 物理页 12，Section VIII）

第三类是与本文最接近的方案。论文称 Huang 等人的 circuit 每个 basic block 只用一个 branch，因此会同步该 block 的全部输出并妨碍 pipelining，而且没有 LSQ，潜在冲突的 memory access 仍需保守串行化；Budiu 等人的 C-to-asynchronous-dataflow 转换思路相近，但方法细节未完整公开，其 LSQ allocation policy 更保守。商业 HLS 的 coarse-grained “dataflow optimization”主要在函数或 loop 级通过 FIFO 重叠任务，FIFO sizing 往往依赖用户，且对 bypass、feedback 和 conditionals 有限制；本文则把对象下沉到 instruction-level dataflow，并联合处理 cyclic control、buffer sizing、deadlock 和动态 memory dependence。[pdf:E04]（PDF 物理页 13，Section VIII 延续）

因此，论文的贡献不宜概括成“第一次使用 dataflow”或“第一次使用 handshake”。更准确的说法是：**它把已有 elastic/dataflow 组件组织成一套从 SSA/CFG 到同步 FPGA circuit 的完整编译方法，并补齐 determinism、buffer optimization 和 LSQ ordering 三个使通用 C/C++ 真正可执行的关键缺口。**这是对论文自身定位的重建，不是本文之外的 novelty 认证。

## § 3 — 重建作者的思考路径

可以把作者的思考路径逆向还原为一条逐步消除失败模式的链条。

第一步，从 Fig. 1 的反例出发：只要某个 dependence 是否存在要到运行时才知道，compile-time controller 就不可能同时做到保守正确与最大并行。自然的替代方案是取消中央 schedule，让每个 operation 在 operands 有效、successor 可接收且必要的 control decision 已确定时局部 firing。Fig. 2 展示了这种结果：iterator、load、comparison、conditional accumulation 被映射为 merge、buffer、fork、branch、select 和 functional unit 组成的 token network；加法路径形成 backpressure 时，只阻塞真正受影响的 token。[pdf:E05]（PDF 物理页 3，Fig. 2）

第二步，需要一套足以表达局部调度的同步组件。作者选择 latency-insensitive ready/valid channel，并定义 eager fork、lazy fork、join、branch、merge、mux、control merge、source、sink 及普通 arithmetic unit；多输入 operation 内含 join，确保 operands 齐备后才执行。[pdf:E06]（PDF 物理页 3，Fig. 3 与 Section III-A）此时已经能画出 datapath，但还不能直接把 compiler graph 原样接线。

第三步，发现 software value 与 dataflow token 的语义不等价。processor register 可以保存一个值供以后多次读取，token 却会被消费；若 live-in 跨过中间 basic block 直接连接目标，可能多送旧 token、少送循环复用 token，最终产生错误或永久 backpressure。Fig. 4 因而要求 data 与 control 严格耦合：每个 basic block 的 live-in 只能来自 immediate predecessors，每个 live-out 只能发给 immediate successors。[pdf:E07]（PDF 物理页 4，Fig. 4）对应规则是对每个 live-in 放置 merge、对每个 live-out 放置 branch，并用 liveness analysis 生成连接。[pdf:E08]（PDF 物理页 4，Section III-B）

第四步，把上述规则机械化。Algorithm 1 先做 CFG liveness analysis，再为各 basic block 建 merge/branch 并连接 successor；与此同时，作者注意到这一严格传播有可能过度保守：与某个 branch condition 无关的 throughput-critical token 仍可能被长延迟条件阻塞，系统化 data bypass 被明确留在本文范围之外。[pdf:E09]（PDF 物理页 5，Algorithm 1 与其后讨论）

第五步，解决 SSA phi 的 nondeterminism。普通 merge 接受先到 token；若一个长路径产生 `x1`、一个短路径产生 `x2`，后一次软件迭代的 `x2` 可能先到并被写回，违反原程序顺序。Fig. 5 把这个错误具体化，说明“各 operation 可 out-of-order”不等于“phi input 可任意重排”。[pdf:E10]（PDF 物理页 5，Fig. 5 与 Section III-C）作者因此为所有 basic block 建一条 data-less、严格按 program control flow 前进的 in-order control network：phi merge 改为 mux，cmerge 告诉 mux 应接受哪个 predecessor。由此得到 determinism、cyclic path 上 one token per loop，以及 acyclic path 上由 control order 派生的严格 token ordering。[pdf:E11]（PDF 物理页 6，Fig. 6 与三项性质）

第六步，认识到正确 network 还不等于高性能 hardware。buffer 有 transparency 与 capacity 两个独立属性：nontransparent buffer 切断 combinational path 并增加一个 cycle，transparent buffer 可组合透传但用 slots 吸收 backpressure；buffer placement 不改变 latency-insensitive network 的功能，却直接决定 timing 和 throughput。[pdf:E12]（PDF 物理页 7，Fig. 8 与 Section IV-A/B）对 cyclic graph，还必须同时满足“每个 combinational cycle 至少一个 nontransparent buffer”和“cycle 内同时容纳 token 与 bubble”；由于前述设计使每个 cycle 有一个 token，至少需要两个 buffer slots 才能避免 deadlock。[pdf:E13]（PDF 物理页 7，Fig. 9 与 Section IV-C）

第七步，把 buffer 从 correctness patch 变成可优化的 architecture variable。Fig. 10 表明，在慢路径放大容量的 transparent buffer 可隔离 backpressure，在关键路径放小容量 nontransparent buffer 可切断长 combinational delay；示例把 6 ns multiplier chain 切到 4 ns target CP，并达到 loop II=1。[pdf:E14]（PDF 物理页 8，Fig. 10 与相邻正文）Algorithm 2 进一步用 profiling 和 ILP 找 performance-relevant choice-free subgraph，再以基于 Petri net 的 MILP 联合选择 buffer capacity/transparency，使 throughput 最大且全图满足 target CP；同一模型还可据 token rate 判断 functional-unit sharing。[pdf:E15]（PDF 物理页 8，Algorithm 2）

第八步，处理 memory side effect。普通 load/store port 允许 request 任意到达，但正确的 LSQ 必须知道原程序中的 basic-block execution order，才能在地址真正出现后判断哪些访问可越序、哪些必须等待。作者从 in-order control network 为每个含 memory access 的 basic block 提供 allocation token；除这一 allocation strategy 外，LSQ 主体类似 processor LSQ。[pdf:E16]（PDF 物理页 9，Figs. 11–12 与 Section V）连接本身也有严格约束：发往 LSQ 的 fork 必须是 lazy fork，且该支路不能插入 sequential buffer，否则 successor basic block 可能先于 predecessor 完成 allocation，破坏队列顺序。[pdf:E17]（PDF 物理页 10，Fig. 13）

最后，作者把这些规则封装进 Dynamatic：C/C++ 经 analyze、elaborate、Clang/LLVM、标准优化与 custom dataflow pass 生成 DOT netlist；MILP optimizer 添加 buffer；`dot2vhdl` 与 component library 输出 VHDL，随后可封装为 AXI-connected FPGA IP。unit library 为目标 FPGA 记录 latency、II 和 critical path，优化器据此选择组件并约束 timing。[pdf:E18]（PDF 物理页 10，Fig. 14 与 Section VI）这条路径说明论文真正的系统洞察是：局部动态执行只有与一条最小的全局顺序骨架、可证明无死锁的 storage 配置和显式 memory-order protocol 同时存在，才会成为可综合的 HLS flow。

## § 4 — 核心 Intuition

把“每个 operation 在第几个 cycle 执行”从 compiler 的固定表格中拿掉，改成 token 在 ready/valid network 中满足真实依赖后自行前进；这样电路只为实际发生的 dependence 付出等待，而不是为所有可能性预留空槽。[pdf:E02]（PDF 物理页 2，Fig. 1）为了不让完全分布式执行破坏程序语义，系统保留一条很窄的 in-order control spine，专门约束 phi selection、constant activation 和 LSQ allocation，其余 datapath 尽可能 out-of-order。[pdf:E11]（PDF 物理页 6，Fig. 6）buffer 则把同一张功能图变成 timing/throughput 可调的物理实现：容量吸收 backpressure，非透明边界切断 critical path。[pdf:E12]（PDF 物理页 7，Fig. 8）

## § 5 — 具体方法与完整 Pipeline

以 Fig. 1 的条件累加 loop 为例，完整 pipeline 如下。

1. **输入与 compiler IR。**输入是普通 C/C++。Clang 产生 LLVM SSA IR，标准 LLVM passes 先做常规分析与优化；CFG 被分成 basic blocks，每个 block 内形成 instruction-level DFG。[pdf:E18]（PDF 物理页 10，Fig. 14）本文没有连续时间模型、物理开关模型或 multi-rate time stepping；它的“事件”是 token 到达与 ready/valid handshake，执行平台是同步 FPGA circuit。

2. **block 内 datapath 化。**`load a[i]`、`load b[i]`、subtraction、comparison 和 conditional addition 各变成对应 functional unit，多 fan-out 处插 fork，多输入 operator 用 join 语义等待 operands。loop iterator `i` 和 accumulator `s` 通过 merge、buffer 和 feedback edge 循环；当条件为假，旧 `s` 经 select 很快返回，当条件为真，select 等待 addition，backpressure 随之阻止受依赖的新迭代继续推进。[pdf:E05]（PDF 物理页 3，Fig. 2）

3. **block 间 data-control coupling。**对每个 basic block 做 liveness analysis；每个 live-in 对应 merge，每个 live-out 对应 branch，所有跨 block value 都逐跳经过 immediate predecessor/successor，而不是像软件 register 那样越过 block 直接引用。[pdf:E07]（PDF 物理页 4，Fig. 4）这保证 token 数量与实际使用次数一致。

4. **顺序语义与无输入 operation。**SSA phi 对应的普通 merge 被 mux 替换，cmerge 构成的 in-order control network给出 predecessor 顺序；没有 operand 的 constant/source 不能永远有效，而应至少由该 control token 激活一次，避免 inactive block 中的 store 或 branch 被不断执行。[pdf:E11]（PDF 物理页 6，Fig. 6 与 Fig. 7 所在 Section III-C/D）

5. **buffer correctness 与 performance synthesis。**先保证每个 combinational cycle 被 nontransparent buffer 打断，且 cycle 至少有一个 token 和一个 bubble；再针对 target CP，以 ILP/MILP 选择各 channel 的 transparency 和 slot count。对示例慢 multiplier path，较深 transparent FIFO 允许快 iterator path 继续接收 token，nontransparent buffer 切开 6 ns combinational chain，示例配置达到 4 ns CP 与 II=1。[pdf:E13]（PDF 物理页 7，Fig. 9）[pdf:E14]（PDF 物理页 8，Fig. 10）

6. **memory interface。**可由 compiler 证明互不冲突的 access 分到简单 memory port 或不同 LSQ；仍可能 alias 的 access 进入 LSQ。每次 basic-block execution 先通过 in-order control path完成 LSQ allocation，随后具体 address/data request 可 out-of-order 到达；LSQ 根据 address 与原始 allocation order 决定 bypass 或 stall。[pdf:E16]（PDF 物理页 9，Figs. 11–12）lazy fork 与无 buffer allocation branch 是保持顺序的必要连接条件。[pdf:E17]（PDF 物理页 10，Fig. 13）

7. **输出与平台映射。**优化后的 DOT graph 被转成 VHDL dataflow-unit netlist，与预定义 component library 一起综合、place-and-route，并可作为 AXI accelerator 接入含 soft/hard CPU 的 heterogeneous FPGA system；论文报告当时支持 Xilinx 与 Intel FPGA。[pdf:E18]（PDF 物理页 10，Fig. 14 与 Section VI）

这个 pipeline 的输出不是一条带中央 FSM 的传统 scheduled datapath，而是一张分布式、同步、可 backpressure 的 circuit graph。其计算依赖与并行性由 token 动态暴露；数值表示本身没有提出新格式，仍使用所选 FPGA unit library 的 integer/floating-point implementation，论文也未报告 mixed precision、fixed-point error analysis 或 numerical stability 研究。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇文章**没有给出可逐式复现的核心数学推导或编号方程**。它给出的是 compiler transformation、deadlock 条件和 optimization architecture；buffer-placement MILP 的完整变量、objective 与 constraints 没有在本 PDF 展开，而是指向作者此前的专门工作。因此不能从本论文单独重建一个完整形式化证明，强行补写方程会超出证据范围。

仍可解释其三层数学/工程结构。第一层是 latency-insensitive token semantics：consumer 只在对应 valid tokens 同时到达且下游 ready 时消费，因此沿 channel 增删 buffer 不改变 value sequence，只改变时间位置。[pdf:E12]（PDF 物理页 7，Section IV-A/B）第二层是 cyclic liveness 条件：combinational cycle 需要 sequential cut；同时 token 要能前进必须存在反向移动的 bubble，所以 one-token cycle 至少配置两个 slots。[pdf:E13]（PDF 物理页 7，Fig. 9）第三层是 constrained optimization：profiling 选出 choice-free subgraphs，ILP 抽取关键 cycles，MILP 在全图 target CP 约束下选择 buffer transparency/capacity 并最大化这些 subgraphs 的 throughput。[pdf:E15]（PDF 物理页 8，Algorithm 2）

实验中的 execution time 也不是由新理论公式预测，而是用 simulation 得到 average loop II，再结合 post-route CP 计算；资源由 place-and-route 后的 slices、LUTs、FFs 与 DSPs 统计。[pdf:E20]（PDF 物理页 11，Section VII-A）因此，第 6 节最重要的读法不是寻找不存在的 closed-form equation，而是认清论文把 correctness、deadlock 和 performance 分别交给 token semantics、cycle storage invariant 与 MILP synthesis 三种工具。

## § 7 — 实验设计与结论

**问题一：动态调度是否真的能把不可静态判定的 memory dependence 转化为运行时并行？**实验用 Histogram、Matrix power、Matching 三个 kernel 与开启 loop pipelining 的 Vivado HLS 对比，并在无法 disambiguate access 时加入 LSQ。Histogram 的 average II 从 13.0 降到 2.3，尽管 CP 从 3.5 ns 增至 4.9 ns，execution time 仍由 45.5 μs 降至 11.1 μs，即由表中时间相除得到约 4.10×；代价是 slices 从 129 增至 `220+1073=1293`，约 10.0×。Matrix power 的时间从 16.8 μs 降至 4.9 μs，约 3.43×；Matching 只从 21.1 μs 降至 18.4 μs，约 1.15×。[pdf:E19]（PDF 物理页 11，Table I）**答案：**机制有效，但收益高度依赖实际可越序比例，LSQ 可带来很大的 area/CP 成本。

**问题二：不可静态判定的 control dependence 是否也能受益？**If loop add 的 II 从 10.0 降至 1.1，execution time 从 32.0 μs 降至 5.5 μs，约 5.82×；If loop mul 的 II 从 7.0 降至 1.1，时间从 22.4 μs 降至 5.5 μs，约 4.07×。两者动态 CP 分别为 5.0 ns 与 5.2 ns，高于静态的 3.2 ns；If loop add 的 DSP 从 2 增至 4，是因为动态高吞吐实现不能像低吞吐静态设计那样把 add/sub time-multiplex 到同一 unit，而 If loop mul 使用不同 operator 后两边 DSP 都为 5。[pdf:E19]（PDF 物理页 11，Table I）[pdf:E21]（PDF 物理页 12，Section VII-C）**答案：**在真实依赖稀疏时，II 改善足以覆盖更慢时钟，但高吞吐需要更多并行 unit 与 control logic。

**问题三：当 static HLS 已能看清全部依赖时，动态机制的固定开销是多少？**FIR 与 Matvec 的 static/dynamic II 都是 1.0；动态 execution time 分别为 3.5 μs 和 3.6 μs，静态均为 2.9 μs。动态 slices 分别为 221 对 47、309 对 63，约为 4.70× 与 4.90×。[pdf:E19]（PDF 物理页 11，Table I）作者明确说这两个 regular kernel 是动态结果被静态结果 Pareto-dominated 的案例，因为动态设计没有额外并行可挖，只剩 CP 与 resource overhead。[pdf:E21]（PDF 物理页 12，Section VII-C）**答案：**动态调度不是免费抽象；规则代码仍应优先用静态 HLS。

**问题四：比较是否尽量公平且结果怎样取得？**作者不给动态方案使用 unrolling；两边使用相同 arithmetic units 与 RAM blocks，设计在 ModelSim 做 functional verification，average II 来自 simulation，CP 来自 post-routing timing，资源来自 Vivado place-and-route。benchmark 共七个，刻意覆盖五个 memory/control-irregular kernel 与两个 regular kernel。[pdf:E20]（PDF 物理页 11，Section VII-A/B 与 Fig. 15）**答案：**比较对 schedule paradigm 的主要变量做了控制，但 workload 是小型代表性 kernel，不是完整 application suite。

**总体结论与外推边界。**论文直接说明 dynamic II 是 data-dependent：无 dependence 时最好，所有相邻 iteration 都 dependent 时最坏，最坏 II 会回到 statically computed 值；LSQ critical path 对 queue entries 非常敏感，out-of-order memory interface 也是资源开销最大的一类组件。[pdf:E21]（PDF 物理页 12，Section VII-C）该 PDF 未报告 power/energy、compile time、large application、不同 LSQ depth、不同 dependence probability、不同 memory latency distribution 或跨 FPGA family 的 sensitivity sweep。因此可以接受“在所选 irregular kernels 上显著提速”的 claim，不能把它扩展成“任意 irregular C/C++ 都会更快”或“单位资源效率更高”。

## § 8 — Take-aways

**5句话：**

1. 论文把 HLS 的 schedule decision 从 compile time 移到 ready/valid dataflow circuit 的 runtime，使潜在依赖只在实际发生时限制并行。[pdf:E01]（PDF 物理页 1，Abstract）
2. 真正困难的部分不是把 arithmetic operator 画成 graph，而是让 token 数量、basic-block control、SSA phi order 和 memory side effect 与原程序严格一致。[pdf:E07]（PDF 物理页 4，Fig. 4）[pdf:E11]（PDF 物理页 6，Fig. 6）
3. in-order control spine 是全系统的语义锚点：它选择 phi input、激活无输入 operation，并向 LSQ 提供 program order，同时允许普通 datapath 尽可能 out-of-order。[pdf:E16]（PDF 物理页 9，Section V）
4. buffer 不只是 register，而是同时承担 cycle cut、bubble storage、backpressure isolation 与 throughput shaping，因而需要 ILP/MILP 联合决定 transparency 和 capacity。[pdf:E14]（PDF 物理页 8，Fig. 10）[pdf:E15]（PDF 物理页 8，Algorithm 2）
5. 实验表明 irregular kernel 可获得约 1.15×–5.82× execution-time 改善，但 regular kernel 更慢且 area 显著增加，所以正确结论是形成新的 performance–cost Pareto tradeoff，而不是全面替代 static HLS。[pdf:E19]（PDF 物理页 11，Table I）

**3句话：**动态 dataflow HLS 用分布式 handshake 释放 compile-time analysis 看不到的并行性。为了保持 C/C++ 语义，它必须增加 control-order network、deadlock-safe buffers 和 ordered LSQ allocation。收益取决于 runtime independence 是否足以覆盖更长 CP 与更大 area。[pdf:E21]（PDF 物理页 12，Section VII-C）

**1句话：**这篇论文的核心不是“dataflow 更快”，而是“把不确定依赖留到硬件看见真实输入后再决定，并用最小顺序骨架守住语义”。

## § 9 — 最脆弱的假设

最关键、失败代价最大的假设是：**目标 workload 在运行时具有足够高的真实 independence，因而 II 的下降能持续压过 handshake、buffer、额外 functional units 与 LSQ 带来的 CP/area 固定成本。**这不是 correctness 假设，而是支撑“高性能”这一核心价值的 workload assumption。

它可能在四种实际条件下失效。其一，potential alias 最终几乎都变成 real dependence，LSQ 大部分时间只能按程序顺序放行；其二，条件分支频繁选择带 loop-carried dependence 的路径，dynamic II 接近 static worst case；其三，LSQ depth、address comparison 或 fan-out 使 critical path 增长，较低频率吃掉 cycle-count 优势；其四，loop 很短或 kernel 很小，control/FIFO overhead 不能被足够多 iteration 摊薄。论文直接承认最坏 data pattern 下 dynamic II 等于静态 II，也承认 LSQ critical path 对 queue entries 高度敏感。[pdf:E21]（PDF 物理页 12，Section VII-C）Table I 进一步显示，即使 II 大幅改善，Histogram 仍付出约 10× slices；在 FIR/Matvec 上 II 无改善时，动态设计直接被静态设计 Pareto-dominate。[pdf:E19]（PDF 物理页 11，Table I）

论文为这一假设提供的正面证据是五个刻意选择的 irregular kernels，尤其 If loop add、Histogram 和 Matrix power；它们说明 runtime independence 确实可以转化为净 execution-time gain。缺失的证据是 dependence-density sweep、alias locality、branch burstiness、LSQ-depth scaling、long-memory-latency distribution 和 full-application amortization。**基于证据的推断：**论文证明了机制在“独立性足够多”的点上成立，却没有确定这一区域在真实 workload space 中有多大。

## § 10 — 最小复现实验

一周内最有信息量的复现不是重建全部 compiler，而是复现 Fig. 1 的 If loop add，并把**真实依赖频率**变成受控变量。

使用同一段 C loop 生成两套设计：Dynamatic dynamic dataflow 与 Vivado HLS static pipeline；遵循论文设置，不 unroll，使用同类 arithmetic unit/RAM。构造长度足够大的 `a[]`、`b[]`，让 `d>0` 的比例依次为 0%、10%、50%、90%、100%，并增加“均匀随机”和“长 burst”两种排列，使平均比例相同但依赖聚集程度不同。Fig. 1 已表明 `d>0` 决定是否执行 loop-carried accumulation。[pdf:E02]（PDF 物理页 2，Fig. 1）

对每个输入先做 bit-exact RTL simulation，再测 average II；随后 place-and-route，记录 CP、总 execution time、slices、LUTs、FFs 和 DSPs，完全沿用论文的 measurement chain。[pdf:E20]（PDF 物理页 11，Section VII-A）最关键的图是 dependence rate 对 II 和 execution time 的曲线，而不是只复现 Table I 的单点。

支持 claim 的结果应是：static II 基本不随输入改变；dynamic II 在 0% 附近接近 1，在 100% 附近逼近 static schedule，并在低到中等依赖率下即使 CP 较长仍有净时间优势；论文单点 If loop add 的参照是 static/dynamic II 为 10.0/1.1、时间为 32.0/5.5 μs。[pdf:E19]（PDF 物理页 11，Table I）反驳 claim 的结果是：dynamic II 对真实依赖率不敏感、burst pattern 导致远超平均比例所预测的 stall，或 CP/area overhead 使除极端稀疏依赖外都没有净收益。这个实验同时验证“runtime adaptation”与第 9 节的 workload assumption，而且不要求先复现 LSQ。

## § 11 — 最强反例设计

最有力的攻击不是再找一个 regular FIR，而是构造一个**控制路径很慢、但 throughput-critical value 与该控制决定语义独立**的 loop，检验 compiler 是否会制造 artificial dependence。作者自己指出，严格的逐 basic-block data/control coupling 可能过度保守：例如 loop iterator 之类的关键 token 即使与某个 basic-block condition 无关，仍会被该长延迟 condition 阻止继续传播；系统化 bypass analysis 被留在本文范围之外。[pdf:E09]（PDF 物理页 5，Algorithm 1 后的讨论）

具体反例可以令每次迭代同时执行一条无依赖的快速主路径 `y[i]=f(x[i])`，以及一条长延迟 predicate 路径 `q=g(meta[i])`；`q` 只决定是否写入一个与 `y`、iterator 和下一迭代地址均不 alias 的 side log。源程序语义允许后续 `f(x[i+1])` 在 `q` 尚未得到时先执行，只需保持 side log 的可见顺序；但当前 in-order control path 与逐 block branch propagation 可能让下一 iteration 的 control token等待 `g`。将三种实现对比：未经修改的 Dynamatic、手工把独立 live-out bypass 过该 condition 的 dataflow graph、以及显式 predication/static transformed baseline。

真正能推翻核心机制的观察是：随着 `g` latency 从 1 增至数十 cycles，原始 Dynamatic 的 II 近似线性恶化，而手工 bypass 版本仍保持接近 1，且二者资源差异不足以解释吞吐差距。那将表明 Table I 的成功可能依赖于 benchmark 中 control spine 恰好足够短，系统并未自动提取“所有运行时可用并行”，而只提取了不越过 CFG control barrier 的一部分。反之，若原始 compiler 已能让快速 path 持续前进，或性能与 bypass oracle 接近，则该反例失败。这个攻击针对的是“从未改写 imperative code 自动得到高性能 circuit”，而不是论文已经承认的 area overhead。

## § 12 — Follow-up Research Bet

**主 idea：多-epoch 版本化 dataflow，让循环跨越未决 control 与 memory alias 继续前进。**新的研究问题是：能否把本文“cyclic path 上一次只有一个 control token”的同步 dataflow 扩展为同时携带多个 speculative loop epoch，并在不暴露错误 side effect 的前提下，让 throughput 由预测正确率而非 branch/alias decision latency 决定？本文当前的 in-order network 明确导出 one token per loop 与 strict token ordering，[pdf:E11]（PDF 物理页 6，Section III-C）而 Introduction 又把 speculative execution 称为动态调度打开但本文未展开的方向。[pdf:E01]（PDF 物理页 1，Introduction）因此，这不是在原方法外包一层 selector，而是改变 token 的状态表示、循环中的并发基数、memory side-effect 语义和 LSQ topology。

核心机制是给 loop header 发出的 token 增加 `epoch id` 与 control-path lineage，并允许若干 epoch 同时存在于 cyclic/acyclic subgraph。merge、mux、fork、join 和 buffer 不再只处理 value，还传播 epoch；branch resolution 验证 lineage。store 与可能 alias 的 load 进入版本化 LSQ，外部可见的 memory update 只有在 epoch 按 program order retire 后生效，尚未确认或已失效 epoch 的结果在可见前丢弃。因果链是：多 epoch 增加 unresolved window 内的在途 iteration → 独立 arithmetic/memory address work 能提前完成 → in-order retirement 恢复 precise C/C++ semantics → 当 decision latency 很长而预测较准时，吞吐不再被单一 control token 的往返时间限制。本文已经证明 LSQ 需要显式 program order，[pdf:E16]（PDF 物理页 9，Figs. 11–12）并说明 lazy fork、无 buffer allocation branch 才能维持该顺序；[pdf:E17]（PDF 物理页 10，Fig. 13）这些现有结构正好提供“epoch allocation/retirement”可依附的语义骨架。

它首次可能使 instruction-level spatial accelerator 同时越过 unresolved branch 和 unresolved memory alias，而不必预先复制若干完整 static schedules。被改变的基本设计变量至少包括：每个 loop 的 in-flight token 数、token representation、control time horizon、LSQ entry semantics、buffer capacity 分配、side-effect 可见边界和 hardware mapping。论文的实验依据也足够具体：Fig. 1 表明实际 dependence 才应降低并行度，[pdf:E02]（PDF 物理页 2，Fig. 1）Table I 表明 irregular kernels 的 cycle gain 可以覆盖 CP 开销，但 LSQ-heavy design 的 area 很大；[pdf:E19]（PDF 物理页 11，Table I）这意味着研究收益与硬件风险都是真实且可测的。

最大收益是把当前“等待真实依赖是否存在”推进到“在结果可撤销地不可见时先做未来工作”，从而形成一种面向 FPGA 的 distributed speculative out-of-order engine。最大科学风险是 epoch tag、versioned side-effect storage 与 retirement network 重新制造类似 processor ROB/LSQ 的集中复杂度，导致 fan-out、critical path、buffer pressure 和 wasted work 抵消全部吞吐；尤其本文已观察到 LSQ queue 规模会恶化 timing。[pdf:E21]（PDF 物理页 12，Section VII-C）

首个区分性实验应同时使用 If loop add 与 Histogram：实现 baseline Dynamatic、总 storage capacity 相同但只加深 FIFO 的 baseline、以及 2-epoch/4-epoch 版本化实现；分别扫描 predicate latency、`d>0` 比例、address alias 比例和 decision accuracy。核心机制得到支持的条件不是“buffer 更多所以更快”，而是多-epoch 版本在相同 slot budget 下，仅当 unresolved decision window 成为瓶颈时显著超过深 FIFO baseline，同时保持 bit-exact result 与 in-order memory visibility；若提高 epoch 数只增加 CP/area，或收益能被普通 buffer capacity 完全解释，该 research bet 即被证伪。

与论文所述 multi-schedule selection、ElasticFlow 和 application-specific hazard logic 相比，这个候选改变的是 token/side-effect representation，并把 control 与 memory speculation 放进同一 dataflow semantics，而不是运行时选择一份预先生成的 static schedule。[pdf:E03]（PDF 物理页 12，Section VIII）包内只给出了 speculative dataflow 相关文献的引用而没有其全文，故这里是**候选判断，不声称 novelty**；与最近工作的实质差异仍需另行全文检索确认。

Wild-card alternative：把当前统一 target CP 的同步 graph 改成由 handshake buffer 连接的多时钟 polychronous islands，联合综合 clock-domain topology、unit latency/II 与 buffer capacity，使 variable-latency subgraph 在不同本地节拍运行，而不是让全设计服从最慢 global CP。[pdf:E18]（PDF 物理页 10，Fig. 14 与 unit characterization）
