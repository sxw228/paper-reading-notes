# DASS: Combining Dynamic & Static Scheduling in High-Level Synthesis

作者：Jianyi Cheng、Lana Josipović、George A. Constantinides、Paolo Ienne、John Wickerson [pdf:E01]

出处：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems，Vol. 41，No. 3 [pdf:E01]

年份：2022 [pdf:E01]

DOI：10.1109/TCAD.2021.3065902 [pdf:E01]

Zotero key：9XPKVH4Z

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 这篇论文研究的是 High-Level Synthesis（高层次综合，HLS）中最核心的决策之一：怎样把程序操作分配到 clock cycle（时钟周期）。传统 Static Scheduling（静态调度，SS）在编译期确定所有开始时间，能做 resource sharing（资源共享）和关键路径优化，但遇到数据相关分支、变量延迟操作和运行时才知道的 memory dependence（存储依赖）时，只能按最坏情况保守排程；Dynamic Scheduling（动态调度，DS）让操作在输入有效时立即执行，能利用运行时信息，却要付出 handshaking（握手控制）、分布式控制、难以共享算术单元和 Load-Store Queue（装载-存储队列，LSQ）的面积与频率代价。论文的问题不是“SS 还是 DS 哪个更好”，而是能否只在运行时信息真正有价值的部分使用 DS，同时把固定或低波动 latency（延迟）的计算岛恢复成 SS，从而改变面积—性能 Pareto frontier（帕累托前沿）。PDF 物理页 1 的 Abstract、Introduction 与 Fig. 1 直接给出了这一矛盾和目标。[pdf:E01]

这个问题重要，因为 scheduling 同时决定三类互相耦合的量：执行周期数、可达到的 Fmax（最高时钟频率）以及 LUT/DSP/register 等资源。只减少周期但降低 Fmax，或只节省算术单元却让控制流按最坏情况等待，都可能使实际 wall-clock time（墙钟时间）变差。DASS 的工程价值在于，它试图把“运行时自适应”和“编译期全局优化”拆到不同代码区域，而不是要求整个 accelerator（加速器）服从同一种调度范式。作者在摘要中报告，DASS 获得了从纯 DS 切换到纯 SS 时可得面积节省的 74%，以及从纯 SS 切换到纯 DS 时可得性能收益的 135%；这两个数是作者定义下的总体权衡指标，不应解释成每个 benchmark 都固定节省 74% 面积或加速 135%。PDF 物理页 1，Abstract/Fig. 1。[pdf:E01]

## § 2 — 前人工作与不足

**论文回顾的已有路线。** 第一类是 SS：HLS 把程序转成 CDFG（Control/Data Flow Graph，控制/数据流图），再用 SDC（System of Difference Constraints，差分约束系统）或 modulo scheduling（模调度）决定操作时刻、资源分配和绑定。它的优势是知道哪些操作不会同时发生，因而能复用乘法器、加法器和存储端口；不足是对运行时分支、变量延迟和未知 alias（别名）只能保守预留时间槽，吞吐会被最坏路径锁死。第二类是 DS：以 Dynamatic 一类工具生成带握手的同步 dataflow circuit（数据流电路），必要时用 LSQ 在运行时处理任意 memory dependence；不足是每个操作趋向成为独立 component，握手网络拉长 critical path（关键路径），算术单元难以共享，LSQ 又会增加面积和访存延迟。PDF 物理页 4，Section III-A 至 III-C。[pdf:E02]

**论文对最相关混合方案的判断。** Alle、Liu 等工作在运行时选择预先生成的 schedule，ElasticFlow 针对不规则 loop nest（循环嵌套）做弹性流水，另一些方法使用 pipeline flushing（流水线冲刷）或动态 hazard detection（冒险检测）。作者认为这些方案仍以 SS 为主体，并受特定循环或 speculation（推测执行）条件限制，不能像通用 DS 那样处理更广泛的输入依赖行为。Carloni 的 latency-insensitive design（延迟不敏感设计）提供了把同步模块封装进弹性系统的理论基础，但论文指出其典型 wrapper 假设内部 II=1、不会自行产生 stall；DASS 则必须支持 II>1，才能保留资源共享。PDF 物理页 5，Section III-D 与 IV-A/IV-B。[pdf:E03]

**本文声称补上的缺口。** DASS 不再把“静态/动态”作为整个函数顶层的单选项，而是把一个 SS function 当作 DS graph 中的 macro-component（宏组件），并解决两个此前版本也没有闭合的问题：非 1 的 II 如何与握手及 backpressure（反压）兼容，以及 SS/DS 如何正确共享同一片 BRAM。作者还明确说明当前 partition（划分）由用户通过 pragma 指定，自动发现只是未来工作，因此本文完成的是“可组合机制与工具链”，不是自动最优分区。PDF 物理页 2，Introduction/Relationship to Prior Publications；物理页 8，Section V。[pdf:E04] [pdf:E05]

## § 3 — 重建作者的思考路径

**基于证据的重建，不是作者逐句自述。** 可以从 Fig. 2 的例子逆向得到这条思路。一个循环只在 `d >= 0` 时调用高阶多项式 `g(d)` 并累加；SS 不知道下一次分支结果，只能把 `g` 和加法的槽位留给每次 iteration（迭代），于是即使某次走短路径，也要保持 loop II=5，出现空槽。DS 能让下一次读取和分支尽早启动，消除这些空槽，但它把 `g` 展开成逐操作握手网络，面积明显膨胀。PDF 物理页 2，Fig. 2 与 Section II。[pdf:E04]

下一步观察是：不规则性位于 `g` 外部的条件控制，而 `g` 本身是 fixed-latency（固定延迟）计算。若运行时调度不能改变 `g` 内部的依赖顺序，那么为 `g` 的每个乘加都保留 DS 控制只是开销；把 `g` 重新压成 SS block，可由 binder 复用算术资源。作者的示例中，SS 实现把 6 个加法器和 5 个乘法器压到各 1 个，而外部仍保留 DS，所以 cycle-level throughput（按周期计的吞吐）与 DS 相同，且因静态块关键路径更短，wall-clock performance 还可能更好。PDF 物理页 3，Fig. 3 与 “DASS—Both Small Area and High Performance”。[pdf:E06]

到这里还不能形成系统：静态块必须像普通 dataflow actor 一样接收不规则到达的 token（令牌）、过滤 bubble（气泡）、传播 backpressure，并且不能把其内部 memory dependence 隐藏到错误的边界后面。因此作者继续引出三个工程问题：怎样描述适用区域，怎样把 SS interface 转换成 DS handshake，以及怎样用全程序 memory analysis 决定哪些访问必须作为同一 conflict set（冲突集合）一起静态化或动态化。PDF 物理页 5 至 8，Section IV。[pdf:E03] [pdf:E07] [pdf:E08] [pdf:E05]

## § 4 — 核心 Intuition

DASS 的核心 intuition 是：让动态控制只包围真正依赖运行时信息的部分，把固定/低波动 latency、且有资源共享机会的子计算压成一个静态 macro-actor。wrapper 负责把 macro-actor 的固定 pipeline 语义翻译成 dataflow 的 valid/ready 语义，memory analysis 与 arbiter 则保证静态块和动态环境共享 BRAM 时仍然正确。收益的根源不是“混合”本身，而是所选静态块的服务速率仍不低于周围 graph 对它的实际需求；一旦边界内存在不可隐藏的 recurrence（递归依赖）或 memory serialization（存储串行化），同一机制会反过来成为瓶颈。PDF 物理页 3，Fig. 3；物理页 6，Fig. 4；物理页 12，Fig. 10/Section VI-C。[pdf:E06] [pdf:E07] [pdf:E09]

## § 5 — 具体方法与完整 Pipeline

这不是 EMT 数值积分或物理建模论文，因此没有微分方程离散、开关事件求解或多速率仿真步长；它的“时间”是 clock cycle、latency、II 和 token rate。完整 pipeline 如下。

1. **输入与人工分区。** 输入是 C/C++。用户用 pragma 把适合 SS 的代码封装为 function；未标注部分默认交给 DS。适用启发式是：运行时信息能提升全局吞吐、至少有一个 constant/low-variability latency 区域、且该区域存在 resource sharing 机会。当前工具要求 SS region 是函数，并不自动搜索最优边界。PDF 物理页 5，Section IV-A；物理页 8，Section V/Fig. 7。[pdf:E03] [pdf:E05]

2. **分别综合。** SS function 交给 Vivado HLS；其余顶层程序交给 Dynamatic。若 SS function 没有 interiteration dependence（跨迭代依赖），使用用户给定 II 或 Vivado HLS 找到的最优 II；若存在这类依赖，则生成 sequential schedule（顺序排程）。之后，工具把 Vivado 报告的 latency/II 回填到 Dynamatic graph，使后端 buffer 与 timing constraint 认识这个 macro-component。PDF 物理页 8，Section V/Fig. 7。[pdf:E05]

3. **把 SS interface 变成 DS handshake。** DS component 使用 `pValid/valid/nReady/ready`；Vivado SS block 使用 `ap_ce/ap_ready/ap_vld`。DASS 在 SS block 外加 wrapper，使前驱只在 block 可接收时发送，后继未准备好时由 `ap_ce=0` 冻结 pipeline，从而保存只在一个周期有效的输出。PDF 物理页 6，Fig. 4 与 Section IV-B。[pdf:E07]

4. **处理 bubble。** 因输入到达时间不再可预测，作者选择让 SS pipeline 持续运行，而不是等待每个有效 token；无效周期被视为 bubble。一个随 `ap_ready` 推进的 shift register 标记每个进入 pipeline 的 token 是否有效，输出时只把最老标记为 1 的结果送给后继。这样减少不必要 stall，但代价是静态块会处理无效输入，论文明确承认有额外 power overhead。PDF 物理页 6，Section IV-B “Constructing the Valid Signal”。[pdf:E07]

5. **多输入、多输出。** 多输入通过 join component 等待所有对应 token 到齐；多输出各自生成 valid，并在任一有效输出遭遇 backpressure 时冻结整个 SS block。论文给出的输出有效式为 `valid_i = ap_vld_i ∧ sr(0)`。PDF 物理页 7，Section IV-B。[pdf:E08]

6. **共享 memory。** 工具先把 SS function inline 回顶层，借用 DS compiler 的 alias/memory analysis 构造访问 graph。可能冲突且连接同一 LSQ 的节点必须作为完整 conflict set 落在同一硬件区域；否则 LSQ 看不到 SS black box 内一次调用可能包含的多次访问，正确性和吞吐都会失真。能证明独立的访问可直接经 Memory Controller（MC，存储控制器）连接 BRAM，避免 LSQ。PDF 物理页 7，Fig. 5 与 Section IV-C。[pdf:E08]

7. **生成共享 BRAM interface。** SS 侧使用 block-memory interface，DS 侧经 MC 转成同一接口；DASS 添加 memory arbiter，每个周期只授权 DS 或某个 SS block，其他 component 通过 clock enable 被 stall。多个请求采用 round-robin，且论文实现中 SS 相对 DS 具有更高优先级。作者报告该 shared-memory interface 在其 Section VI benchmarks 中移除了全部 LSQ。PDF 物理页 8，Fig. 6 与 Section IV-C summary。[pdf:E05]

8. **输出。** 顶层 Dynamatic netlist 中，每个 SS function 表现为一个带明确 latency/II、握手端口和可选 BRAM 端口的 component；工具输出组合后的 RTL。以 Fig. 2 的 `g` 为例，外部 branch/merge/loop feedback 仍是 DS，`g` 的多项式 datapath 由 SS 做资源共享，得到 DASS circuit。PDF 物理页 2 至 3，Fig. 2/Fig. 3。[pdf:E04] [pdf:E06]

论文采用的示例数据类型包括 `double` 与若干整数 benchmark，但没有系统报告 fixed-point quantization（定点量化）、数值误差或功耗优化；这些维度不能从本文结果外推。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有复杂的正确性定理，但给出了 wrapper 状态长度和 rate analysis（速率分析），用来解释怎样选择 SS block 的 II。

**1. Bubble 标签长度。** 若 SS block latency 为 `L`、initiation interval 为 `II_g`，shift register 长度取

\[
L_{sr}=\left\lceil \frac{L}{II_g}\right\rceil .
\]

它不是数据 pipeline 的全部寄存器数，而是同时在途的“输入批次”数量：每次 `ap_ready` 接收新输入就右移一位，最老一位与 `ap_vld` 一起判断输出是否合法。PDF 物理页 6，Section IV-B，Fig. 4 后的无编号公式。[pdf:E07]

**2. 普通 component 的速率约束。** 对一个有 `N` 个前驱、`M` 个后继的非控制 component，握手会使各输入输出的实际 token rate 相等为 `r`，并满足

\[
r\le \min\!\left(\frac{1}{II_g},\frac{1}{II_{p1}},\ldots,\frac{1}{II_{pN}},\frac{1}{II_{s1}},\ldots,\frac{1}{II_{sM}}\right).
\]

直觉是：一个 component 的吞吐不可能高于自身，也不可能高于任何相邻瓶颈。PDF 物理页 11 至 12，Section VI-C，Fig. 10 前后的无编号公式。[pdf:E10] [pdf:E09]

**3. 控制 component 改变 rate。** merge 汇合两条互斥路径时，`r_out=r_in1+r_in2`；branch 把输入按概率/占比拆分。论文 Eq. (2)–(3) 写为

\[
r_{out1}=p_1r_{in},\qquad r_{out2}=(1-p_1)r_{in}.
\]

对于处在 loop-carried dependency 中的 branch，Eq. (1) 进一步约束平均输入间隔：

\[
\frac{1}{r_{branch,in1}}\ge
\max\!\left(II_{in},\;II_{out1}p_1+II_{out2}(1-p_1)\right).
\]

这相当于说，反馈环不仅受前驱能多快供数限制，也受两条后继路径的加权服务时间限制。PDF 物理页 12，Section VI-C，Eq. (1)–(3)/Fig. 10。[pdf:E09]

**4. motivating example 的 `II_opt`。** 令 `η` 为走长路径 `d>=0` 的 iteration 比例。短路径最低服务间隔为 1，长路径包含 5-cycle feedback，因此顶层平均间隔至少为

\[
II_0\ge (1-\eta)\cdot 1+\eta\cdot 5=1+4\eta,
\]

所以总输入 rate 为 `r_0=1/(1+4η)`，流入 `g` 的 rate 为 `r_g=ηr_0`。只要 `g` 的最大服务 rate `1/II_g` 不低于 `r_g`，它就不会成为新瓶颈；边界点满足

\[
II_{opt}=\frac{1}{r_g}=\frac{1+4\eta}{\eta}=\frac{1}{\eta}+4.
\]

当 `η=0.5` 时，`II_opt=6`；当 `η=1` 时退化为 5；当 `η→0` 时 `g` 几乎不用，允许的 II 趋于无穷。这个推导解释了为什么一味把 SS block 做成 II=1 通常只增加面积而不增加系统吞吐，也解释了为什么输入分布知识可以继续换取 resource sharing。PDF 物理页 11，Fig. 9；物理页 12，Fig. 10 与推导段落。[pdf:E10] [pdf:E09]

**推导边界。** 该分析使用 average rate，并在 case study 中假设 branch 决策在 iteration 间均匀分布、由 buffer 吸收不平衡；它不是对任意 bursty sequence（突发序列）、有限 buffer 和复杂 memory contention 的完备吞吐证明。论文也把一般图上的最优 II 搜索留给用户。PDF 物理页 11 至 12，Section VI-C。[pdf:E10] [pdf:E09]

## § 7 — 实验设计与结论

**问题 1：DASS 能否在保持 DS 低 latency 的同时减少面积？ → 实验。** 作者选择 11 个 benchmark，包括 sparse matrix、histogram、条件多项式、tanh approximation、BNN、bubble sort、Livermore kernel 和几何求交等；比较 Vivado HLS 的最佳 SS、Dynamatic 的最佳 DS 与 DASS。设计者被假定不知道输入分布，因此 DASS 默认使用由拓扑/loop dependence 决定的保守 II；每个含数据相关控制的 benchmark 再测试 best/average/worst 三类分布。total clock cycles 来自 ModelSim 10.6c，area 来自 Vivado 的 Post & Synthesis report；目标 FPGA 为 `xc7z020clg484`，Vivado 版本为 2018.3，所有设计用 test vectors 做功能验证。PDF 物理页 9，Section VI 与 Fig. 8。[pdf:E11]

**答案。** Fig. 8 中多数箭头从 DS 指向左下方的 DASS，表示相对 SS 归一化后，面积和 wall-clock time 同时下降；Table II 逐项列出 LUT、DSP、register、total cycles、Fmax 与 wall-clock time，说明收益来自“资源下降 + 周期不增或下降 + 部分设计 Fmax 改善”的组合，而不是只看 cycle。PDF 物理页 9，Fig. 8；物理页 10，Table II/Section VI-B。[pdf:E11] [pdf:E12] 作者最终对适合 DASS 的 benchmark 总结为：相对对应 DS 平均节省 45% 面积，相对对应 SS 获得 1.98× execution-time speedup；这是该 benchmark 集上的平均结果，不是普适保证。PDF 物理页 13，Conclusion。[pdf:E13]

**问题 2：SS block 的 II 是否可以独立调节面积—性能？ → 实验。** motivating example 中，作者扫描纯 SS loop II 与 DASS 中 `g` 的 II，并改变长路径比例 `η`。纯 SS 的 II 从 5 增至 7 时，LUT 减少 28%，但 latency 增加 39%；DASS 则存在“elbow”：低于周围需求的 II 不再提升全局吞吐，却继续消耗资源。`η=0.5` 时，实验与 rate analysis 都给出 `g` 的最佳 II=6。PDF 物理页 11，Fig. 9/Section VI-C；物理页 12，Fig. 10。[pdf:E10] [pdf:E09]

**答案。** DASS 不是简单地把静态块做得越快越好，而是要把 block rate 配到 graph rate；若知道 input distribution，能比 worst-case II 取得更好的面积—性能点。反过来，这也说明论文的主要收益依赖分区和 II 选择。

**问题 3：方法何时失败？ → 实验。** 作者把 `bubbleSort` 的交换过程做成 SS function。内部跨 iteration 的 load/store dependence 迫使它顺序执行，function boundary 又增加 1 cycle latency；循环吞吐直接受该 latency 限制，wrapper 开销无法被 pipeline 隐藏。结果 DASS 相对纯 SS 既更慢又更大，纯 DS 又受 LSQ 面积和访存 latency 影响。PDF 物理页 13，Fig. 11 与 Section VI-D。[pdf:E13]

**不得外推的范围。** benchmark 是作者主动选择的、以 DS 能改善 latency 且多数满足 DASS 条件的 11 个程序；硬件平台只有一个 Xilinx 7-series 器件和一套较早工具版本。论文未报告 board-level power、place-and-route 后拥塞、跨器件家族结果，也没有系统扫描大量自动分区。因此数据支持“在可识别的适用区域上存在显著 Pareto 改善”，不支持“任意 HLS 程序混合调度都会更好”。PDF 物理页 9，Section VI；物理页 13，Conclusion。[pdf:E11] [pdf:E13]

## § 8 — Take-aways

**5 句话：** ① SS 擅长资源共享和关键路径优化，DS 擅长利用运行时控制与 memory dependence，两者的优势位于不同代码区域。② DASS 用 function-level SS macro-component 替换 DS graph 中固定/低波动 latency 的子图，并用 wrapper 保持 valid/ready、bubble 和 backpressure 语义。③ shared-memory correctness 不是附属细节，而是靠全程序 conflict-set analysis 与 BRAM arbiter 才闭合。④ 性能取决于 block II 是否匹配周围 token rate，`II_opt=1/η+4` 的 case study 把这种匹配定量化。⑤ 在适用 benchmark 上作者报告相对 DS 平均节省 45% 面积、相对 SS 达到 1.98× execution-time speedup，但 bubbleSort 证明错误边界会让 DASS 同时丢失面积和性能。[pdf:E07] [pdf:E08] [pdf:E09] [pdf:E13]

**3 句话：** ① DASS 的真正贡献是让 II>1、可资源共享的静态 pipeline 成为动态 dataflow 中可正确 backpressure 的 actor。② 其收益来自把 runtime uncertainty 留在 DS、把 regular computation 留给 SS，并把二者的 rate 与 memory ownership 对齐。③ 这不是自动万能优化：人工分区、输入分布与隐藏 recurrence 决定它是否进入更好的 Pareto 区域。[pdf:E03] [pdf:E05] [pdf:E10]

**1 句话：** DASS 说明 HLS scheduling 的最佳粒度不是“整程序选 SS 或 DS”，而是按不规则性的真实位置组合两者，同时把接口、速率和存储依赖当作同一个 correctness/performance 问题。[pdf:E04] [pdf:E05]

## § 9 — 最脆弱的假设

**最关键假设：被静态化的 region 可以被一个稳定的 latency/II 与完整 memory conflict boundary 充分描述，并且这个 black box 的服务速率不会限制周围动态 graph。** 这是失败代价最大的假设，因为 DASS 的 wrapper 只能正确传递 token 和 stall，不能消除静态块内部的 loop-carried recurrence、数据相关 memory serialization 或高度可变 latency。论文自己的适用条件要求 region 具有 constant/low-variability latency 和 resource-sharing opportunity；memory 方法又要求一个可能冲突的 node set 必须整体属于同一硬件区域，并指出含不可预测 memory access 的顶层 SS function 不能任意 pipeline。PDF 物理页 5，Section IV-A；物理页 7，Section IV-C。[pdf:E03] [pdf:E08]

如果这一假设不成立，后果不是“收益小一点”，而是机制反转：function boundary 的额外 latency 和集中式 schedule 进入 feedback loop，DS 外围无法越过它；同时仍保留 wrapper、handshake 和 arbiter 开销。bubbleSort 正是论文内的实证反例，DASS 被纯 SS 在吞吐和面积上同时支配。PDF 物理页 13，Fig. 11/Section VI-D。[pdf:E13]

论文为该假设提供的证据是 10 个适用 benchmark、一个明确负例和 motivating example 的 rate analysis；缺少的是对边界选择误差的系统 sweep，例如静态块数量、共享 BRAM contention、burstiness、有限 buffer、输入分布漂移和组合后的 critical-path growth。因而最稳妥的解读是：DASS 证明了“好边界存在时机制有效”，尚未证明编译器能可靠找到好边界。PDF 物理页 9，Section VI-A；物理页 13，Section VI-D/Conclusion。[pdf:E11] [pdf:E13]

## § 10 — 最小复现实验

一周内最值得复现的不是完整 11-benchmark 工具链，而是 Fig. 2 的 `filterSum + g`，因为它同时覆盖 branch-dependent workload、固定 latency 子计算、loop-carried accumulation 和 II 选择。PDF 物理页 2，Fig. 2；物理页 11，Section VI-C。[pdf:E04] [pdf:E10]

- **数据。** 生成长度 `N=4096` 的 `double` 数组，令 `d>=0` 的比例 `η∈{0,0.25,0.5,0.75,1}`；每个比例同时使用均匀随机排列和成段 burst 排列。`N` 和 burst 设计是复现实验选择，不是论文报告参数。
- **实现。** 生成三种 RTL：纯 SS；纯 DS；DASS，其中 `g` 为 SS block，扫描 `II_g∈{1,5,6,7}`。wrapper 至少实现 Fig. 4 的 shift-register valid tracking 与 `ap_ce` backpressure；另在 testbench 中随机拉低 `nReady`，验证 valid input 不丢失、bubble output 不外泄。源程序和预期 schedule 来自 PDF 物理页 2，wrapper 机制来自物理页 6。[pdf:E04] [pdf:E07]
- **测量。** 比较功能输出、LUT/DSP/register、cycle count、estimated Fmax 和 `cycles/Fmax`；所有版本使用相同 target、clock constraint 和 operator latency。再记录不同 `η`/排列下的 buffer stall，检查 average-rate 假设对 burst 的敏感性。
- **支持核心 claim 的结果。** 在均匀 `η=0.5` 时，`II_g=6` 应位于 DASS 的面积—wall-time elbow：相对 `II_g=1` 面积下降且 wall time 基本不变；DASS 应比 DS 面积小、比 SS wall time 短。这个预期直接来自 Fig. 9 与 `II_opt=6` 推导。PDF 物理页 11 至 12。[pdf:E10] [pdf:E09]
- **反驳条件。** 在匹配 operator latency 和 buffer 的前提下，若 DASS 仍不能同时优于至少一个单一范式，或 `II_g=6` 在均匀 `η=0.5` 下没有形成 elbow，核心“rate-matched static island”解释就被削弱；若只在均匀排列成立、burst 排列显著崩溃，则说明论文的 average-rate 结论不能直接推广到真实突发控制流。

## § 11 — 最强反例设计

**基于证据的攻击设计。** 构造一个带 loop-carried recurrence 的动态循环，循环内串联 `k` 个很小的候选 SS function；每个 function 都执行条件 load/store，访问同一片 BRAM，但地址冲突率可调。让纯 SS 能在整个 loop 范围内统一排程，让纯 DS 的 memory analyzer 能把可证明独立的访问绕过 LSQ；DASS 则被迫在每个 function boundary 付出 wrapper latency，并通过同一 shared-memory arbiter 串行化。这个设计把论文已经出现的三种不利因素叠加：隐藏在 SS block 内的跨 iteration dependence、每个 function 至少一周期的边界代价、以及 SS/DS 对共享 memory 的互斥授权。PDF 物理页 7，Section IV-C；物理页 8，Fig. 6；物理页 13，bubbleSort case study。[pdf:E08] [pdf:E05] [pdf:E13]

实验扫描 `k`、alias probability、长短路径 burst length 和 successor backpressure，并保证三种实现使用相同算术资源预算。最有力的反例不是 DASS 偶尔输，而是出现一个稳定区域：纯 SS 因全局 schedule 获得最高吞吐，纯 DS 因跨边界 overlap 获得次高吞吐，而 DASS 同时因多重 wrapper 和 arbiter serialization 变慢、面积又高于纯 SS，因而被两者的 Pareto envelope（帕累托包络）支配。为排除“只是工具没有优化好”的替代解释，应再加入手写、合并寄存器且经过 retiming 的 DASS wrapper；若结果仍随 `k` 近似线性恶化，才真正攻击了 function-level black-box 机制，而不是某个 RTL 细节。

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty：用 scenario-aware rate polytope（场景感知速率多面体）替代“固定 II 的 function black box”，合成一个统一的 elastic HLS topology。** 新研究问题是：能否让编译器不再二元决定“这段是 SS、那段是 DS”，而是把控制场景、token rate、资源占用和 memory conflict 一起编码为可综合的 phase-indexed actor（分相 actor），在同一硬件拓扑中同时获得跨区域 resource sharing 与运行时控制流吞吐？它首次可能使“静态资源共享跨越动态 branch boundary”成为一等综合对象，而不是只在一个被 wrapper 包住的 function 内发生。

**核心机制与因果链。** 编译器先对 dataflow SCC（强连通分量）和 Fig. 5 式 memory conflict set 建模，再从 branch outcome、recurrence 和 memory epoch 中提取有限 scenario phase。每个候选子图不再只有一个 `(latency, II)`，而是携带一组 phase-indexed token consumption/production rate、算术单元占用区间、BRAM-port ownership 和状态转移；这些约束组成 rate polytope。全局 modulo scheduler、buffer placer 与 resource binder 在 polytope 上联合优化，生成一套共享 functional-unit fabric；运行时 scenario token 只是推进同一 actor 的相位，不是在“快路径/保守路径”之间阈值切换。这样，DASS 当前 shift register 长度 `ceil(latency/II)` 所表达的单一在途深度，被更一般的多相 token-state 取代；Fig. 5 的 conflict set 也从“必须整个落在 SS 或 DS”变成 phase-aware memory ownership。论文现有表示和边界见 PDF 物理页 6 至 8。[pdf:E07] [pdf:E08] [pdf:E05]

**为什么全文支持这个押注。** 第一，Fig. 9/10 证明同一个 `g` 的最佳 II 随 `η` 连续变化，`II_opt=1/η+4`，说明 scalar worst-case II 丢失了真实 workload state；rate 本身已经是论文解释收益的核心变量。第二，bubbleSort 的失败不是算术不足，而是 function boundary 把 recurrence 和额外 latency 固化进 feedback loop，说明需要改变 partition object，而不只是自动挑 pragma。第三，shared-memory 方法已经产生 conflict-set graph，但目前只用它做二元归属和 arbiter 生成，没有与 rate/resource binding 联合优化。PDF 物理页 11 至 13，Fig. 9、Fig. 10、Fig. 11。[pdf:E10] [pdf:E09] [pdf:E13]

**改变的基本设计变量。** 状态表示从单一 latency/II 变成 scenario phase 与 rate polytope；系统边界从 function 变成跨 branch 的 SCC/subgraph；硬件映射从“每个 SS function 内局部共享”变成多个 phase 间的全局算术/BRAM 端口共享；评价对象从一个固定 input distribution 下的 Pareto 点变成一族 distribution 与 burst process 下的 Pareto surface（帕累托曲面）。这至少同时改变了状态表示、可控变量、硬件映射和系统边界。

**与论文所列近期方向的实质区别。** 论文把 runtime schedule selection、ElasticFlow、pipeline flushing 和 hazard resolution 描述为仍以 SS 为主体、受特定循环条件限制的方案；它又把 buffer sizing、scenario-aware dataflow 与 synchronous-dataflow throughput analysis 只作为 II/rate 相关背景引用。候选方案不是给 DASS 加自动 pragma selector，也不是根据监测值切换多个实现，而是把 scenario-aware rate 直接提升为 HLS IR 和 resource-binding 语义，并把 memory conflict graph 纳入同一个综合问题。由于没有读取这些引用论文的全文，这一差异只能视为基于本论文的候选判断，不能作为 novelty 声明。PDF 物理页 5，Section III-D；物理页 11，Section VI-C。[pdf:E03] [pdf:E10]

**最大收益与最大风险。** 若成功，它可能在不复制多套 datapath 的前提下，跨动态边界共享乘加器和 BRAM port，并自动适配不同 `η`/burst pattern，消除 DASS 对人工 function boundary 与单一 worst-case II 的依赖。最大科学风险是 scenario space explosion：真实 control/memory history 可能不能被有限 phase 准确压缩，polytope 联合调度也可能把控制与共享 mux 做得过重，最终降低 Fmax，抵消面积收益。

**首个可证伪实验。** 选择 motivating `filterSum`、失败的 `bubbleSort`，再加一个论文中的 shared-memory sparse benchmark；分别实现纯 DS、纯 SS、固定-II DASS 和 rate-polytope actor。四者匹配 buffer 数量、算术单元数量、BRAM bank 与 clock target，并在相同 `η`、burst length 和 alias pattern 上测试。核心机制得到支持的判据是：新表示在 `filterSum` 上无需为每个 `η` 重新综合仍接近各自 DASS elbow，在 `bubbleSort` 上消除多 function-boundary 的吞吐损失，并在 shared-memory case 中不靠增加 buffer 或复制 datapath 获得更好的 Pareto surface；若优势在资源/缓冲匹配后消失，则最强替代解释是“收益只来自更多 hand tuning 或 storage”，该研究押注应被否决。

**Wild-card alternative：** 把 Fig. 5 的 memory conflict set 编译成 versioned multi-bank BRAM fabric（版本化多 bank BRAM 网络），用显式 epoch token 让 SS 与 DS 在不同 memory version 上并发并在确定的 commit graph 汇合，从物理 memory topology 和一致性对象上消除单一 arbiter，而不采用上述 rate-polytope 表示。[pdf:E08] [pdf:E05]
