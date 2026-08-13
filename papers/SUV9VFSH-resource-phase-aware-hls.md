# Resource and Phase Awareness for Dynamically Scheduled High-Level Synthesis

**作者：** Mathias Bouilloud；Lana Josipovic；Wayne Luk（PDF 物理页 2，标题与作者区）[pdf:E01]

**出处：** *The International Symposium on Highly Efficient Accelerators and Reconfigurable Technologies 2025 (HEART 2025)*，Kumamoto, Japan（PDF 物理页 2，ACM Reference Format）[pdf:E01]

**年份：** 2025（PDF 物理页 2，ACM Reference Format）[pdf:E01]

**DOI：** 10.1145/3728179.3728194（PDF 物理页 2，ACM Reference Format）[pdf:E01]

**Zotero key：** SUV9VFSH

**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

下文把“论文直接陈述”“论文所引相关文献的结论”“基于证据的推断”和“候选判断”明确分开。由于本任务只允许使用附件，本文不对论文之外的 novelty 做独立检索认证。

## § 1 — 研究问题与重要性

论文处理的是 dynamically scheduled HLS（动态调度高层次综合）里两个相互耦合的问题。第一，elastic/dataflow circuit（弹性数据流电路）依靠 buffer 缓解 backpressure、提高 throughput，并用 non-transparent buffer 截断长 combinational path；现有优化通常持续添加 buffer，直到吞吐达到最优，却没有把可用 buffer 数量当成硬约束。第二，程序在不同 runtime phase 中会呈现不同的 branch probability、memory access 和 cycle execution frequency；若编译器只根据全程平均频率生成一个静态 buffer placement，有限资源可能被投给当前 phase 根本不活跃的路径。论文因此分别提出 resource-aware optimization 和 phase-aware optimization，并把二者集成进 Dynamatic（PDF 物理页 2，Abstract、Introduction 与贡献列表）[pdf:E01]。

这个问题重要，是因为 buffer 既不是“免费寄存器”，也不只是一个局部时序修补手段。dataflow circuit 的功能具有 latency-insensitivity，允许在不改变功能的前提下调整通道上的存储；但 buffer 的数量、透明性和位置会同时影响 backpressure、cycle throughput、critical path 与 FPGA 面积。论文把这种“功能不变、性能与面积可变”的自由度变成显式优化变量（PDF 物理页 3，Sections 2.1–2.2）[pdf:E02]。

直接工程价值有两层。较扎实的一层是：在固定 FPGA 预算下，不再问“达到最高吞吐至少要多少 buffer”，而是问“给定最多 N 个 buffer，能得到多高吞吐”，从而显式生成 area–performance trade-off。更冒险的一层是：针对每个 phase 生成不同配置，让同一份有限资源在时间上复用。我的判断是，前者解决的是当下编译器可直接利用的资源建模缺口；后者只有在 phase 足够长、检测足够准且配置代价能被 amortize（摊销）时才成立，这一条件正是论文后半部分最薄弱之处。

## § 2 — 前人工作与不足

**论文对既有 buffer optimization 的重建。** dynamically scheduled HLS 把 Basic Block 连接成带 handshake 的 dataflow graph，运算单元在输入就绪、下游可接收时立即执行。transparent buffer 是可直通的 FIFO，用于吸收 backpressure；non-transparent buffer 类似断开 combinational path 的寄存器。既有 placement/sizing 方法建立在 Petri net/marked graph、retiming 和 latency-insensitive design 上，通常写成 MILP：变量是每条 channel 上的 buffer slot 数与透明性，约束包括 clock-period path constraints 与 cycle-throughput constraints，目标是按执行频率加权各 cycle 的 throughput（PDF 物理页 3，Sections 2.1–2.2）[pdf:E02]。

**不足一：资源模型缺位。** 既有目标会继续投入 buffer，直到性能不再提升；它给出的是达到最大 throughput 的最小 buffer 数，而不是在现实资源上限内的最优解。论文改变的不是 dataflow semantics，而是优化问题的可行域：加入总 buffer budget 后，编译器可以在资源不足时选择“退化得最少”的 placement，而不是默认资源无限（PDF 物理页 5，Section 3.1，Eq. (1)–(2)）[pdf:E05]。

**不足二：全程平均频率掩盖 phase。** 论文引用的 phase model 把执行看成若干 working set 近似稳定的 major phase，中间由不稳定状态分隔。Styles 等人的工作已经提出 phase-optimized reconfigurable system，但其 Basic Block 内部是 statically scheduled、各路径同周期产出，并通过每个 Basic Block 的 Initiation Interval 体现资源分配；本文要填补的具体空位，是把 phase specialization 用到 dynamically scheduled dataflow graph 的 buffer placement 上（PDF 物理页 4，Section 2.4）[pdf:E04]。

**不足三：物理实现与模型之间仍有落差。** 论文自己指出，现有 buffer MILP 对 frequency/Clock Period 的估计不稳定，mapping-aware 方法试图把技术映射与 buffer insertion 联合起来；本文没有解决这一问题，后续实验也确实出现目标 5 ns 与 place-and-route 结果不一致的情况（PDF 物理页 3，Section 2.2；PDF 物理页 8，Section 5.2）[pdf:E02][pdf:E15]。

**不足四：phase detection 被移出问题边界。** 论文引用已有 phase detection 方法，并假定编译器已经知道每个 phase 中每个 cycle 的 execution frequency；因此它评测的是“给定 oracle-like phase information 后怎样优化”，而不是完整的在线识别、状态保存与重配置系统（PDF 物理页 7，Section 4.2，Eq. (3) 前正文）[pdf:E11]。这使方法论边界很清楚，也使端到端结论必须更谨慎。

## § 3 — 重建作者的思考路径

下面是基于全文证据的逆向重建，不是作者逐字陈述。

1. latency-insensitivity 先提供了一个关键自由度：在 channel 上插入或移动 buffer 不改变程序功能，只改变何时产生 backpressure、何时切断 combinational path，以及最终 throughput/Clock Period（PDF 物理页 3，Sections 2.1–2.2）[pdf:E02]。
2. 既然 buffer 是性能旋钮，也占用 FPGA 资源，那么“无限加到最优”为错误的问题定义；更实际的目标应是固定总量下的最优配置。作者因此保留原 MILP 的 path/throughput constraints 与 weighted-throughput objective，只额外加入总 buffer 上限（PDF 物理页 5，Section 3.1，Eq. (1)–(2)）[pdf:E05]。
3. 资源充足时，phase awareness 没有必要，因为所有主要 cycle 都可同时获得足够 buffer；真正有信息价值的区域是 N 小于达到全局最优所需的阈值时，此时不同 cycle 必须竞争稀缺 slot（PDF 物理页 5，Section 3.1）[pdf:E05]。
4. 如果两个 loop 在时间上互斥执行，全程平均频率却相近，global objective 会把 buffer 分散给二者；在任一时刻，这等价于把一部分资源投给 inactive phase。Listing 2 的两个连续 loop 就把这种冲突压缩成最小例子（PDF 物理页 5，Section 4.1 与 Listing 2）[pdf:E07]。
5. 一个自然的下一步不是发明新约束，而是改变目标权重：把 phase 表示为一组 per-cycle execution-frequency weights，对每个 phase 分别求解同一个 budgeted MILP，使 active loop 获得大部分 transparent buffers（PDF 物理页 6，Fig. 2 与 Section 4.2；PDF 物理页 7，Eq. (3)）[pdf:E08][pdf:E11]。
6. 生成多个专用电路后，必须回答“省下的 cycles 能否覆盖配置代价”。因此作者引入 speed-benefit 比值 ζ，并把是否值得重配置归结为一个简单的 amortization inequality（PDF 物理页 7，Section 4.3，Eq. (4)–(5)）[pdf:E12]。

这条思路的优点是模块化：resource-aware 部分只改 MILP 可行域，phase-aware 部分只改 objective weights，runtime 部分再单独核算切换成本。缺点也来自同一模块化：phase detection、bitstream/state management、真实配置延迟与 mapping-aware timing 没有被联合进优化，因此各模块单独成立并不自动推出端到端成立。

## § 4 — 核心 Intuition

把 buffer 看成由各条 dataflow channel 竞争的有限预算，而不是可以一直添加的免费资源；当程序进入不同 phase 时，竞争优先级也应随 per-cycle execution frequency 改变（PDF 物理页 5，Eq. (1)–(2)；PDF 物理页 7，Eq. (3)）[pdf:E05][pdf:E11]。因此，同一个 budgeted MILP 针对每个 phase 求一次解，就能把 transparent buffer 集中到当前真正限制 throughput 的路径上（PDF 物理页 6，Fig. 2）[pdf:E08]。但这种 specialization 只有在省下的执行 cycles 大于全部 reconfiguration cycles 时才有系统级价值（PDF 物理页 9，Eq. (6)–(9)）[pdf:E18]。

## § 5 — 具体方法与完整 Pipeline

以论文的两个连续 loop 为例，完整 pipeline 如下。

1. **从 C/C++ 生成动态数据流图。** Dynamatic 把 Basic Block 内的运算连接为 handshake dataflow units，并用 Merge/Branch 表示控制流；channel 上的 transparent buffer 调节 backpressure，non-transparent buffer 截断长 combinational path。FIR 示例直观展示了默认 placement 与低 budget placement 的结构差异（PDF 物理页 4，Fig. 1）[pdf:E03]。
2. **保留原 buffer MILP。** 原目标最大化各 choice-free cycle throughput 的执行频率加权和，原有 path constraints 管 Clock Period，throughput constraints 管 marked-graph cycle 的可达吞吐（PDF 物理页 3，Section 2.2；PDF 物理页 5，Eq. (1)）[pdf:E02][pdf:E05]。
3. **加入 resource budget。** 对所有 channel 的 buffer slots 求和，并要求其低于输入 budget N；求解结果是在不超过 N 的前提下尽量提高 throughput，而不再保证达到 unconstrained optimum（PDF 物理页 5，Section 3.1，Eq. (2)）[pdf:E05]。在 FIR 例子中，默认优化放入 8 个 buffer；随着 N 从至少 8 降到 7、5、3，论文报告的单 loop throughput 依次落到 1、0.83、0.5、0，N=3 时电路因资源不足而不可用（PDF 物理页 5，Section 3.2）[pdf:E06]。
4. **先看 phase-unaware baseline。** Listing 2 有两个顺序执行、结构相近的 loop。默认 Dynamatic 用 16 个 buffer 可在 1000 cycles 完成；把全局优化限制为 12 个 buffer 后，两段 loop 无法同时充分优化，总执行增加到 1670 cycles（PDF 物理页 5，Section 4.1 与 Listing 2）[pdf:E07]。
5. **构造 phase representation。** 论文把一个 phase 写成向量 φ，其元素是该 phase 中各 program cycle 的 execution frequency。对两个 loop，φ₁=(1,0)，φ₂=(0,1)；模型假定这些向量已知，并对每个 φ 分别运行一次优化（PDF 物理页 7，Section 4.2，Eq. (3)）[pdf:E11]。
6. **生成 phase-specialized circuits。** 在同样 12-buffer budget 下，phase 0 的配置把 transparent buffers 投向第一段 loop，phase 1 的配置投向第二段 loop；为约束全电路 Clock Period，non-transparent buffers 仍分布在其他位置。忽略 reconfiguration overhead 时，两段各自都能充分优化，总执行回到 1000 cycles（PDF 物理页 6，Fig. 2 与 Sections 4.1–4.2）[pdf:E08][pdf:E09]。
7. **运行时应用。** 概念上，编译器输出 P 个 phase-optimized circuits；外部 phase detector 发现 transition 后，让 FPGA 采用对应配置。论文没有实现或评测 detector、真实 reconfiguration controller 与状态迁移，而是在 simulation 中把各 phase 的 cycle count 相加，再用性能模型单独加入假设的 Nᵣ（PDF 物理页 7，Section 4.3；PDF 物理页 8，Methodology）[pdf:E12][pdf:E13]。
8. **后端评测。** 作者在 Dynamatic 中实现优化，用 ModelSim 得到 cycle count，用 Vivado place-and-route 得到 LUT 与 Clock Period，目标器件是 Xilinx Virtex UltraScale+ xcvu19p-fsva3824-2-e，buffer optimization 的目标 Clock Period 为 5 ns（PDF 物理页 8，Section 5.1）[pdf:E13]。

最终输出不是一个自动适应的单电路，而是一个 global resource-aware design，或一组依赖外部 phase information 的 specialized designs。论文真正实现并验证的是“怎样产生这些 design 及其模拟 cycle behavior”；完整 runtime system 仍是概念链条中的未实现部分。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有复杂理论证明，核心是三个 MILP/objective 变体与一个 amortization 模型。

**1. 原始 throughput objective。**

\[
\max \sum_i w_i\,\theta_i
\]

其中 θᵢ 是 program cycle i 的 throughput，wᵢ 与该 cycle 的 execution frequency 成比例。直觉是：更常执行的 cycle 对全程性能贡献更大，应优先得到 buffer。论文沿用此前工作的 path constraints、throughput constraints 与此目标，但没有在本文中重新给出完整 MILP，因此严格复现还需要先前模型或实现细节（PDF 物理页 5，Section 3.1，Eq. (1)）[pdf:E05]。

**2. Resource-aware constraint。**

\[
\sum_c N_c < N
\]

这里 N_c 是 channel c 上的 buffer slot 数，N 是输入的总 budget；源 PDF 使用严格小于号。若 N★ 表示达到最大 throughput 所需的最小 buffer 数，则 N≥N★ 时仍可达到最优，真正形成 trade-off 的区域是 N<N★（PDF 物理页 5，Section 3.1，Eq. (2)）[pdf:E05]。工程上，这相当于在原性能优化外套一层整数 knapsack-like budget，但每个 slot 被按相同计数处理，并没有直接按 bit width、LUT/FF/BRAM 成本或 routing cost 加权。

**3. Phase-conditioned objective。**

\[
\forall \phi:\qquad \max \sum_{i=1}^{P}\phi_i\,\theta_i
\]

φᵢ 是当前 phase 中 cycle i 的 execution frequency；同一 budgeted MILP 对每个 phase 独立求解。两-loop 例子使用 φ₁=(1,0)、φ₂=(0,1)，所以每次优化只奖励当前 loop 的 throughput（PDF 物理页 7，Section 4.2，Eq. (3)）[pdf:E11]。需要注意，Eq. (3) 的求和上界写成 P，而附近正文又用 P 表示 phase 数，符号存在复用歧义；按文字含义，求和对象应是 program cycles，而求解次数才是 phase 数。

**4. Runtime benefit。**

\[
\zeta=\frac{N_c}{\sum_j\left(N_r+N_j\right)}
\]

在 Eq. (4) 中，N_c 改指不重配置的 default circuit 总 cycle count，N_j 是 phase j 在其专用电路上的 cycle count，N_r 是每次 reconfiguration 的 cycle cost；这与 Eq. (2) 中 N_c 表示 channel buffer count 是另一处符号复用。ζ>1 才说明 phase specialization 加 reconfiguration 更快（PDF 物理页 7，Section 4.3，Eq. (4)–(5)）[pdf:E12]。

若有 P 个 phase，并把每个 phase 都计一次 N_r，则：

\[
\frac{N_c}{P N_r+\sum_j N_j}>1
\quad\Longleftrightarrow\quad
N_r<\frac{N_c-\sum_j N_j}{P}.
\]

右式就是每次 reconfiguration 可承受的最大 cycle budget：phase-specialized execution 相对 default execution 省下的 cycles，必须足以覆盖 P 次配置（PDF 物理页 9，Section 5.4，Eq. (6)–(9)）[pdf:E18]。

论文的 worked example 用 1670/(100+500+100+500)=1.39 展示 ζ；算术本身闭合，但同一段写“25 buffers available”，而此前产生 1670/1000 对比的 Listing 2 与 Fig. 2 明确使用 12-buffer constraint，因此“25”更像未解释的编辑不一致，不宜当成已验证参数（PDF 物理页 5–7，Section 4.1、Fig. 2、Eq. (5)）[pdf:E07][pdf:E09][pdf:E12]。

## § 7 — 实验设计与结论

**问题一：加入 buffer budget 后，性能是否按资源量可控地退化？** 作者选取 4 个来自 Dynamatic buffer-optimization study、主要源于 PolyBench 的 benchmark，并把部分 kernel 顺序组合成人工 major phases；对每个 benchmark 从默认 buffer 数向下扫描，直到最差性能。cycle count 来自 ModelSim，LUT 与 Clock Period 来自 Vivado place-and-route（PDF 物理页 8，Section 5.1）[pdf:E13]。Fig. 3 显示，buffer availability 降低时，cycle count 大体呈阶梯式、可解释地上升，LUT 多数情况下也下降；这支持 resource-aware model 能产生连续的 trade-off，而不是随机失效（PDF 物理页 7，Fig. 3）[pdf:E10]。

**问题二：Dynamatic 默认 placement 是否 over-provision buffer？** Table 1 中，保持 cycle count 不变时，Comb1 可从默认 31 降到 27，Fdtd 从 102 降到 70，Gemver 从 118 降到 75，Comb2 从 202 降到 121；按默认值重算，分别是 4/31=12.9%、32/102=31.4%、43/118=36.4%、81/202=40.1% 的 buffer reduction（PDF 物理页 8，Table 1）[pdf:E14]。这与论文概括的 13%、31%、36%、40% 一致，支持“最高约 40%”的主结论；但 Section 5.3 的正文把同样的 savings 写成“4 out of 17、32 out of 126、43 out of 103、81 out of 216”，这些分母与 Table 1 及所列百分比都不一致，属于可见的数据编辑问题（PDF 物理页 9，Section 5.3）[pdf:E17]。

**问题三：cycle improvement 是否等价于真实 execution-time improvement？** 不等价。优化目标 Clock Period 是 5 ns，但 Table 1 的 place-and-route 结果从 2.6 ns 到 6.8 ns，既有超过目标的结果，也有 buffer 更少反而 Clock Period 更好的反常点；作者明确承认无法提取全局趋势，并因 execution time 不稳定而把后续分析集中在 cycle count（PDF 物理页 8，Table 1 与 Section 5.2）[pdf:E14][pdf:E15]。因此 resource-aware 部分证明得最好的是“buffer count 对 simulated cycles 的可控 trade-off”，不是稳定的 wall-clock speed/area Pareto frontier。

**问题四：phase optimization 在忽略配置代价时是否有收益？** 作者对每个 phase 生成专用 design，模拟完整程序后只取该 design 所针对 phase 的 cycles，并把各 phase 相加。Table 2 给出分 phase cycle count；Fig. 4 中 zero-overhead reconfiguration 的蓝线始终不高于无 reconfiguration 的绿线，因此在 oracle phase information 与 N_r=0 的条件下，phase specialization 一直更好或相同（PDF 物理页 9，Table 2；PDF 物理页 10，Fig. 4）[pdf:E16][pdf:E19]。这是一个有效的 optimizer-level 结果，但它是 optimistic upper bound，不是完整系统测量。

**问题五：真实 reconfiguration overhead 能否被覆盖？** 通过 Eq. (9)，论文得到各 benchmark 的最大可承受 N_r：Comb1 2623 cycles、Fdtd 653 cycles、Gemver 2280 cycles、Comb2 1416 cycles；Fig. 5 也显示 buffer 越紧，允许的 overhead 越高（PDF 物理页 10，Section 5.4；PDF 物理页 11，Fig. 5）[pdf:E20][pdf:E21]。但论文随后指出，Xilinx reconfiguration 通常从数毫秒到数分钟；若 Clock Period 约 5 ns，就是数百万到数十亿 cycles，远高于上述阈值，因此对实际评测的这些 benchmark，真实 runtime reconfiguration 并不 attractive。作者只提出一个尚未实证的外推：若 loop 足够大，例如大规模 DNN/matrix multiplication，使 buffer shortage 带来数百万 cycles 的损失，才可能覆盖真实配置代价（PDF 物理页 10，Section 5.4）[pdf:E20]。

**结论边界。** resource-aware claim 有直接表格支撑：在 4 个 benchmark 上可以显著减少 buffer，且 simulated cycle degradation 大体平滑。phase-aware claim 只证明了“专用 placement 可减少 cycles”和“在 negligible overhead 下更快”；论文结论中“realistic workloads”仍是一项基于大 loop 的合理猜想，而不是本文 FPGA 实测结果。作者也把 mapping-aware timing、其他资源类型、其他 HLS compiler 与 neural-network benchmark 列为 future work（PDF 物理页 11，Limitations/Future Work 与 Conclusions）[pdf:E22]。

## § 8 — Take-aways

**5 句话：**

1. 论文用一个总 buffer budget 约束，把 Dynamatic 的目标从“达到最大 throughput 需要多少 buffer”改成“最多 N 个 buffer 时 throughput 能有多高”（PDF 物理页 5，Eq. (1)–(2)）[pdf:E05]。
2. 它把 phase 表示为 per-cycle execution-frequency vector，并对每个 phase 独立求解同一个 MILP，使 buffer placement 随 phase 改变（PDF 物理页 7，Eq. (3)）[pdf:E11]。
3. 4 个 benchmark 的 Table 1 支持在不增加 cycle count 的情况下减少约 13%–40% 的默认 buffer，但正文中的若干分母存在内部不一致（PDF 物理页 8–9，Table 1 与 Section 5.3）[pdf:E14][pdf:E17]。
4. zero-overhead simulation 中，phase-optimized execution 始终不差于静态 execution（PDF 物理页 10，Fig. 4）[pdf:E19]。
5. 真正的瓶颈是配置成本：实验可覆盖的只有 653–2623 cycles，而论文自己估计常见 reconfiguration 是数百万到数十亿 cycles（PDF 物理页 10，Section 5.4）[pdf:E20]。

**3 句话：**

1. resource-aware optimization 是本文最可信的贡献，因为它只需在既有 MILP 中加入 budget，并得到可解释的 buffer–cycle trade-off（PDF 物理页 7，Fig. 3）[pdf:E10]。
2. phase-aware optimization 在算法层面成立，但端到端 speedup 依赖极长 phase、准确 phase information 与极低或可摊销的 reconfiguration cost（PDF 物理页 9，Eq. (6)–(9)）[pdf:E18]。
3. 在 timing estimation、真实配置与 phase detection 都未闭合前，不能把 simulated cycle advantage 直接等同于 FPGA execution-time advantage。

**1 句话：**

这是一篇“资源预算建模已经站住、phase specialization 机制有潜力、真实 runtime reconfiguration 仍未被实验闭合”的论文。

## § 9 — 最脆弱的假设

最脆弱的假设是：**每个 major phase 足够长，使每次 reconfiguration 的成本满足**

\[
N_r<\frac{N_c-\sum_j N_j}{P}.
\]

一旦不满足，P 个 phase-specialized circuits 即使各自 cycle count 更低，端到端执行仍会比单一 resource-aware circuit 更慢（PDF 物理页 9，Eq. (6)–(9)）[pdf:E18]。

论文给出的证据实际上对这一假设不利：4 个 benchmark 的最大可承受配置成本只有 653、1416、2280、2623 cycles，而作者估计通常的 Xilinx reconfiguration 在约 5 ns Clock Period 下是数百万到数十亿 cycles；也就是说，评测实例的 break-even margin 比现实配置代价小多个数量级（PDF 物理页 10，Section 5.4）[pdf:E20]。Fig. 5 只证明资源越紧时 break-even threshold 会升高，并没有把它提升到现实量级（PDF 物理页 11，Fig. 5）[pdf:E21]。

论文提出“大 loop 或 DNN workload 会扩大 cycle savings”作为可能的补救，但没有用这类 workload、真实 bitstream transfer、phase detector、state quiescence/restore 或实际 reconfiguration latency 验证。即使 phase detection 完全准确，这个成本不等式仍可能失败；因此它比“phase 能否被识别”更直接地决定 phase-aware 核心贡献是否成立。这个假设失效不会推翻 resource-aware budget constraint，但会使 runtime phase specialization 从主要贡献退化为离线 upper-bound 分析。

## § 10 — 最小复现实验

一周内最值得复现的是 **“相同 12-buffer budget 下，per-phase objective 是否真的把 1670-cycle global design 拉回约 1000 cycles”**，而不是尝试搭完整 reconfiguration system。

**数据与程序。** 直接实现 Listing 2 的两个连续 loop，使用论文相同的动态 dataflow 语义；把两个 loop 视为 phase 0 与 phase 1（PDF 物理页 5，Listing 2）[pdf:E07]。

**实现。** 在 Dynamatic 或等价 elastic-HLS flow 中保留原 path/throughput constraints，加入 Eq. (2) 的总 buffer budget，并生成三类 design：全局 frequency 的 12-buffer baseline；φ₁=(1,0) 的 phase-0 design；φ₂=(0,1) 的 phase-1 design。再用 16-buffer global design 作为“资源充足”sanity baseline（PDF 物理页 5–7，Eq. (2)–(3)）[pdf:E05][pdf:E11]。

**测量。** 用 simulation 记录每个 loop 与全程序 cycle count，导出每条 channel 的 transparent/non-transparent buffer slots；若能运行 Vivado，再记录 post-place-and-route Clock Period，避免只看 cycles。论文的预期参照是：16-buffer global design 约 1000 cycles，12-buffer global design 约 1670 cycles，两个 12-buffer phase design 的目标 phase 各约 500 cycles，合计约 1000 cycles，且 transparent buffers 分别集中到对应 loop（PDF 物理页 5–7，Section 4.1、Fig. 2 与 Eq. (5)）[pdf:E07][pdf:E08][pdf:E09][pdf:E12]。

**支持标准。** 在总 buffer slots 完全相同的前提下，两个 specialized design 的目标 phase cycle sum 明显低于 global 12-buffer design；buffer map 的变化与 active loop 一致；乘上各自 post-route Clock Period 后优势仍存在。

**反驳标准。** 只要出现以下任一情况，就足以反驳该最小 claim：specialized sum 与 global baseline 接近或更差；所谓收益来自不同的实际 buffer/LUT 预算；或 specialized design 的 Clock Period 恶化到抵消 cycle savings。

这个实验只验证 phase-conditioned optimization mechanism。它不能验证真实 runtime speedup；后者还必须加入 Eq. (9) 所要求的实际 N_r（PDF 物理页 9，Eq. (9)）[pdf:E18]。

## § 11 — 最强反例设计

最强反例不是再找一个“buffer saving 较小”的 benchmark，而是给 phase-aware 方案最有利的信息条件，再让真实 reconfiguration cost 击穿它。

构造一个由多个顺序 phase 组成的 dynamically scheduled workload，使各 phase 的最优 transparent-buffer placement 明显不同；phase label 直接由 oracle 提供，排除 detection error；所有方案使用相同总 buffer budget。比较三种实现：单一 resource-aware circuit、每个 phase 一个 specialized circuit、以及资源充足的静态 upper bound。对 specialized 方案必须计入真实 FPGA 配置传输、让 dataflow state 安全进入可重配置边界所需的停顿，以及每个配置的 post-route Clock Period。

实验不固定一个方便的 phase 长度，而是从低于 Eq. (9) break-even 所需的执行量逐步增加，直接画出“phase useful work 对 end-to-end time”的交叉点。论文已经报告当前 benchmark 只能容忍 653–2623 cycles 的 N_r，而现实估计是数百万到数十亿 cycles（PDF 物理页 10，Section 5.4）[pdf:E20]；因此这个反例很可能在很宽的实际区间内显示 specialized circuits 更慢。为避免把失败归咎于 timing noise，应使用真实 place-and-route Clock Period，而不是固定 5 ns 模型，因为论文自己的 Table 1 已显示 Clock Period 不稳定（PDF 物理页 8，Table 1 与 Section 5.2）[pdf:E14][pdf:E15]。

若 specialized 方案只有在极端长、极少 transition 的 phase 才越过单一 circuit，就说明方法本质上不是普遍的 runtime phase optimization，而是针对“可被 circuit-level reconfiguration 摊销的超长 epoch”的条件化技术。若即使在这种长 phase 下也因状态管理、routing 或 Clock Period 损失而不能获益，则核心机制被更强地反驳。

## § 12 — Follow-up Research Bet

由于没有进行附件之外的相关工作检索，以下是**候选判断，不声称 novelty**。

**主 idea：可迁移 token-storage fabric（可迁移令牌存储织构）。** 新问题不是“为每个 phase 生成哪一个完整 FPGA circuit”，而是：能否在一个固定 dynamically scheduled circuit 内，把物理 buffer slots 做成共享、可重新绑定到不同 channel 的 banked storage fabric，使 phase adaptation 变成片上 token-storage reallocation，而不是 circuit-level FPGA reconfiguration？

它首次可能让 phase-aware buffer allocation 在短得多的 phase 上工作。因果链是：latency-insensitivity 说明 buffer 的插入位置在保持 handshake/order 语义时不改变功能（PDF 物理页 3，Section 2.1）[pdf:E02]；Fig. 2 表明 phase specialization 的主要结构差异恰好是 transparent buffers 从一个 loop 转移到另一个 loop，而 non-transparent timing buffers仍需保留（PDF 物理页 6，Fig. 2 与正文）[pdf:E08][pdf:E09]；Table 1 又显示静态默认 design 中有约 13%–40% buffer 在保持 cycle count 时可以去掉（PDF 物理页 8，Table 1）[pdf:E14]。因此可以把一部分 transparent storage 从 channel-local FIFO 改成若干共享 bank，通过可编程 endpoint、credit/handshake routing 与 token migration protocol，把容量在 phase 之间重新分配；删除这一 fabric 后，系统将失去“同一电路内改变 channel storage topology”的基本能力，所以它不是在原方法外加 observer 或 wrapper。

这项研究至少改变五个基本设计变量：硬件拓扑从 channel-local buffers 变为 shared banks；可控变量从 bitstream 选择变为 channel–bank binding 与容量配额；状态表示加入 token occupancy 与 ownership；系统边界把 adaptation 从外部 FPGA configuration port 移入 dataflow fabric；评价对象从单个 steady phase 扩展到 phase transition 期间的 token conservation、stall 与 Clock Period。最大收益是把论文估计的数百万到数十亿 reconfiguration cycles 降为片上状态搬移/重新绑定成本，从而把目前只在 zero-overhead simulation 中成立的优势推向真实执行（PDF 物理页 10，Section 5.4）[pdf:E20]。最大科学风险是共享互连、arbitration 与 token migration 本身可能拉长 critical path、增加 backpressure，或者破坏 marked-graph 中维持吞吐所需的 token/buffer invariant，最终比静态 over-provision 更贵。

首个证伪实验应使用 Listing 2 或结构相似的两-phase graph，在**相同总 buffer slots**下比较：静态 global placement、两个理想 specialized placements、以及一个 shared-bank prototype。phase label 继续用 oracle，避免把结果混入 detection；测量每个 phase cycles、transition stall、LUT/FF/BRAM、post-route Clock Period 和端到端 execution time。最强替代解释是“收益只是因为 prototype 实际提供了更多或更灵活的存储”，所以必须严格等容量，并增加一个静态但同样 banked 的 control；只有动态 reallocation 在等容量下仍优于该 control，才支持核心机制。

与论文所述最近工作相比，Styles 的方案在 phase 间采用完整的 phase-optimized circuit，mapping-aware buffering 则改进静态 placement 与 frequency estimation；这个候选把科学对象改成“运行中的 token storage topology”，既不依赖 P 个完整 circuit，也不只是把静态 MILP 做得更准（PDF 物理页 4，Section 2.4；PDF 物理页 11，Future Work）[pdf:E04][pdf:E22]。

**Wild-card alternative（候选判断）：** 不改变硬件拓扑，而把 phase 从 branch-frequency vector 改写为 marked-graph token-occupancy 的低维时间轨迹，并由编译器主动注入短探测输入来辨识各 channel 的 throughput sensitivity，再合成可跨 phase 插值的 buffer modes；这改变的是状态表示、时间模型与数据生成方式，而不是共享存储机制（PDF 物理页 3，marked-graph/MILP 背景；PDF 物理页 7，phase vector）[pdf:E02][pdf:E11]。
