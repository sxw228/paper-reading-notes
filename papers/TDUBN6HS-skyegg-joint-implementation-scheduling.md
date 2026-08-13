# SkyEgg: Joint Implementation Selection and Scheduling for Hardware Synthesis using E-graphs

**作者**：Youwei Xiao；Yuyang Zou；Yun Liang  
**出处**：arXiv:2511.15323v1 [cs.PL]  
**年份**：2025  
**DOI**：未报告  
**Zotero key**：TDUBN6HS  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** SkyEgg 研究的不是“怎样再发明一个局部 HLS pass”，而是一个更基础的流程割裂：传统 HLS 先用 pattern matching 选 LUT、DSP 或 IP 的实现，再在已经固定的实现上排时序。可是实现决定 latency、端口 delay 和可启用的内部 pipeline，schedule 又反过来决定什么实现配置最有价值；先后分开做，会在第一阶段就不可逆地删掉好设计。论文将问题定义为：怎样在同一设计空间内联合选择等价代数表达式、硬件实现及其配置，并同时安排执行周期，使最终 latency 最小且满足目标时钟。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，是因为现代 FPGA 的异构资源不是“同一个算子换个面积数字”。以 DSP48E2 为例，pre-adder、multiplier、ALU 和可旁路的内部寄存器共同决定一个表达式能否被融合、需要几级 pipeline、最高频率是多少。若编译器只在单算子层面决定映射，后面的 scheduler 再聪明，也无法找回已经错过的多算子硬件模式。SkyEgg 的价值因此是把软件表达式的等价性与硬件时序的具体性放进同一个优化问题，而不是只改善某一阶段的启发式。

## § 2 — 前人工作与不足

**论文直接陈述。** Vitis HLS、LegUp、Bambu 等顺序式流程会先固定 implementation selection，再 scheduling；既有 HLS 与 physical design 协同工作主要处理 delay prediction、placement、pipelining 或 layout co-optimization，并没有把 implementation selection 本身纳入联合问题。另一方面，e-graph 已用于软件表达式选择、逻辑综合和 FPGA technology mapping，但论文认为此前没有把“实现候选 + 配置时序 + schedule”统一到 e-graph 上。[pdf:E02]（PDF 物理页 2，Section 2.1–2.2 与 contributions）

不足不是简单的“前人没有考虑 DSP”。顺序流程缺少一个共同的表示：实现选择器看得到局部 pattern，却看不到未来 schedule；scheduler 看得到固定候选的 delay，却不能重写表达式或更换内部 pipeline。论文的动机例子把后果具体化：16-bit 的 `-(a+b)*c` 在 xcku3p、450 MHz 下，Vitis HLS 给出 3-cycle 结果，只把乘法放进 DSP48E2；代数重写为 `-((a+b)*c)` 后，pre-adder、multiplier 和 ALU 可由一个 DSP48E2 覆盖，人工配置及 SkyEgg 都能得到 2-cycle 结果。作者还枚举 128 个 DSP48E2 pattern case，其中 31 个不能被 Vitis HLS 映射为单 DSP。[pdf:E03]（PDF 物理页 3，Figure 1 与 Section 2.3）

需要保留边界：源 PDF 的 related work 比较来自作者自己的分类，没有独立系统综述；“first”以及“complete design space”是论文 claim，不应在未补全文检索时升级为全领域事实。

## § 3 — 重建作者的思考路径

在不预设 SkyEgg 方案的情况下，可以从四个已知事实走到作者的 idea。

第一，异构 FPGA 上同一功能有多个 timing 完全不同的实现：LUT、DSP primitive、不同 latency 的 floating-point IP 都不是等价的固定成本节点。第二，表达式形状决定硬件 pattern 是否能匹配；一个合法的代数 rewrite 可能把三个离散操作变成一个 DSP 宏操作。第三，内部 pipeline 的开关会同时改变 latency 与每级 critical path，因此“最快的单元”不能脱离 schedule 定义。第四，e-graph 能紧凑保存大量等价 term，而不必过早挑出一个表达式。

由此自然得到一个研究问题：如果把代数 rewrite 与 hardware implementation 也都写成 equality saturation 的规则，能否先保留全部可选 term，再在同一个 e-graph 上选择实现并排 schedule？Figure 1 的 3-cycle 对 2-cycle 例子不是结论的替代品，而是把这条推理链压缩成一个可验证的最小案例。[pdf:E03]（PDF 物理页 3，Figure 1）

## § 4 — 核心 Intuition

SkyEgg 的核心 intuition 是：**不要在知道 schedule 之前冻结实现，也不要在冻结表达式之后才做 schedule。** 把代数等价形式和硬件实现配置都表示为 e-graph 中的候选节点，等到候选空间展开后，再用同一个目标函数选择“哪种表达式、哪种硬件、从第几拍开始”。

真正起作用的是表示方式的改变：一个 implementation e-node 不只是标注“这是 DSP”，还携带特定配置下的 latency 与端口 timing；于是 solver 可以比较“多一个组合链”“少一级 IP pipeline”“融合进一个 DSP”对全局结束时间的共同影响。

## § 5 — 具体方法与完整 Pipeline

**论文直接陈述。** SkyEgg 的完整流程如下：[pdf:E04]（PDF 物理页 4，Figure 2 与 Section 3–4.1）

1. **输入与建图。** 将 HECTOR 降低后的 MLIR SSA basic block 转成初始 e-graph；每个 SSA value 是 e-node，operand 指向对应 e-class。
2. **生成候选。** library 把每种硬件实现写成 `matcher → applier` 规则，并附 data type、bitwidth 等 condition。matcher 表示软件功能，applier 创建 `identifier(Vec(args...))` 形式的 implementation e-node；普通 algebraic rewrite 同时参与 saturation。
3. **枚举配置。** basic logic 没有配置变体；DSP48E2 等 primitive 枚举内部 register 的启用或旁路；parameterized IP 枚举整体 latency 与 resource preset。每个“实现—配置”组合对应固定电路结构。
4. **建 timing database。** 对每个实现配置单独跑 Vivado synthesis，抽取端口 incoming delay、最后一级 outgoing delay、内部 cycle delay 与 latency；论文明确把 post-synthesis timing 当作 wire-load model 下的近似。[pdf:E05]（PDF 物理页 5，Figure 3 与 Section 4.2）
5. **联合求解。** saturated e-graph 上只把 implementation e-node 纳入 MILP，约束 functional completeness、dependency、latency、selection 与 combinational chaining；目标先最小化 root e-class finish time，再用小系数惩罚实现数量。
6. **两条 solver 路线。** exact 路线由 OR-Tools 解简化后的 MILP；scalable 路线按 e-class topological order 做 ASAP，逐 class 选择 earliest-finish implementation。[pdf:E08]（PDF 物理页 8，Figure 5 与 Section 7.1）
7. **输出。** 选择结果带有 implementation、timing configuration 和 start cycle，转换为 SystemVerilog primitive/IP 实例，再交给 Vivado 综合。

用 `-(a+b)*c` 举例：代数规则产生 `-((a+b)*c)`；DSP rule 识别 `-((A+D)×B)`；该 configured DSP e-node 与传统 LUT-add/LUT-neg/DSP-mul 路径同时留在 e-graph 中。联合 solver 看到前者能用一个 DSP48E2 在 2 个 pipeline stage 完成，因而同时完成 expression extraction、implementation selection 和 scheduling。

论文未报告运行时可重配置、数据相关 dynamic scheduling、跨 basic-block 的 pipeline overlap、HBM/DDR memory scheduling、placement/routing co-optimization 或多 FPGA 通信；不能把 SkyEgg 外推为完整的端到端 accelerator compiler。

## § 6 — 核心数学推导（无形式化数学则跳过）

先理解 timing model。对实现 \(I\)，论文用 latency \(L\)、输入端口延迟 \(t_{incoming,p}\)、输出延迟 \(t_{outgoing}\) 与内部最坏 cycle delay \(t_{cycle}\) 描述它。对有寄存器的实现：

\[
t_{incoming,p}=t_{logic,0,p}+t_{su},\quad
t_{incoming}=\max_p t_{incoming,p}
\]

\[
t_{outgoing}=t_{clk\to Q}+t_{logic,L},\quad
t_{cycle}=\max_s(t_{clk\to Q}+t_{logic,s}+t_{su}).
\]

组合实现则令 \(L=0\)，端口 incoming delay 直接是组合路径，且 \(t_{outgoing}=t_{cycle}=0\)。这组量把“某 primitive 的内部 pipeline”翻译成 scheduler 能消费的接口。[pdf:E05]（PDF 物理页 5，Eq. 1a–1e）

连接 \(I_i\) 输出到 \(I_j\) 的端口 \(p\) 时，edge delay 为

\[
t_{edge}(e)=t^{I_i}_{outgoing}+t_{net}+t^{I_j}_{incoming,p}.
\]

对一条中间节点均为组合实现的 path \(\pi\)，\(t_{path}\) 累加 edge delay；若首节点本身是组合实现，还要补上它的 incoming delay。两个实现之间的 chain delay 是全部合法组合路径中最大的 \(t_{path}\)。插入 register 会增加一个 cycle，同时引入 setup、clock-to-Q 和额外 net delay；这正是“随便切一刀”并不免费。[pdf:E06]（PDF 物理页 6，Figure 4、Eq. 2–6 与 Table 1）

联合 MILP 的核心可压缩为：

\[
\min\; f_{cls_{root}}+\alpha\sum_i b_{I_i},
\]

其中 \(b_{I_i}\) 表示 implementation e-node 是否被选，\(s_{I_i},f_{I_i}\) 是 start/finish cycle，\(b_{cls_j}\) 与 \(f_{cls_j}\) 表示 e-class 是否需要及其完成时间。Eq. 7b–7d 保证从 root 出发选择了能完整计算 operand 的 implementation term；Eq. 7e–7g 保证依赖、实现 latency 与 e-class finish time 合法；Eq. 7h 用 Big-M 只在一条 path 上的 implementation 全被选中时施加 register-cut 约束。[pdf:E07]（PDF 物理页 7，Eq. 7a–7j）

若需要 \(q\) 个 register 把路径切成 \(q+1\) 个周期，则必须满足

\[
t_{path}(\pi)+q(t_{su}+t_{clk\to Q}+t_{net})\le(q+1)T_{clk}.
\]

论文据此计算最小 `cuts`。为避免枚举所有 path，exact 求解只保留 implementation pair 之间最长的 top-\(k\) 条 path，默认 \(k=3\)；作者报告该设置在全部实验中都得到满足 clock target 的解。ASAP 则在 topological traversal 中先算每个候选的依赖 earliest start，再补选中 path 的 cuts，最后选最早结束者。它在线性 e-graph scale 上运行，但局部最早结束不保证全局最优，因为这个候选可能给后续制造更长的 chaining constraint。[pdf:E07]（PDF 物理页 7，Eq. 8–10 与 Section 6）

## § 7 — 实验设计与结论

**问题 1：联合优化是否降低 latency？ → 实验。** 作者从 liquid-dsp、ggml、PolyBench 和 Vitis Library 取 float32 与 integer kernel，经 HECTOR 抽 basic block；Vitis HLS 2024.1 使用 `#pragma HLS PIPELINE`，SkyEgg 生成 Verilog并用 Vivado 2024.1 综合。两者都针对 xcku3p speed grade `-1`，测试 100、200、400 MHz；speedup 定义为 \((Latency_{Vitis}+1)/(Latency_{SkyEgg}+1)\)。→ **答案。** Section 7.2 报告全 benchmark/频率平均 speedup 为 3.10×，ASAP 为 3.08×，MILP 为 3.12×；float 平均 3.64×、范围 2.78×–5.22×，integer 平均 2.38×、最高 4.33×。[pdf:E09]（PDF 物理页 9，Table 2、Figure 6 与 Section 7.2）但 Abstract 与 Conclusion 写成 3.01×，[pdf:E01][pdf:E11] 源 PDF 对总体平均值存在 3.10×/3.01× 的内部不一致，本卡不替作者消解。

**问题 2：收益是否真的来自配置选择，而不只是代数 rewrite？ → 实验。** rmsnorm 的 float32 sqrt 在 400 MHz 下，Vitis HLS 选择 28-cycle/979 MHz 配置；profile 显示 10–13 cycle 配置都能达到 431 MHz，SkyEgg 选 10 cycle，将整体 latency 从 73 降到 25 cycles。randnf_pdf 的 exponential 中，Vitis 的 Full DSP Usage 是 30 cycles/699 MHz；SkyEgg 选择 Medium Usage 的 8 cycles/450 MHz，将整体 latency 从 154 降到 52 cycles。→ **答案。** 至少在这些案例里，频率呈 plateau，更多 pipeline 或更多 DSP 不等于更低应用 latency；显式枚举配置是关键机制。[pdf:E09]（PDF 物理页 9，Section 7.2，frequency plateau 案例）

**问题 3：latency 改善的资源与 timing 代价是什么？ → 实验。** Table 3 将三档频率平均后的 FF/LUT 用量除以 Vitis HLS，并检查每个 benchmark 是否都满足三档目标。→ **答案。** MILP/ASAP 的 FF 比值分别为 0.87/0.95，LUT 比值为 1.51/1.28；两种 SkyEgg solver 在表中全部 timing met，而 Vitis HLS 只有 0.52 的 benchmark 在全部频率均满足 timing，即 48% 失败。[pdf:E10]（PDF 物理页 10，Table 3 与 Resource and Timing Comparison）这说明论文用更高 LUT 换 latency，但不能把平均数解释成每个 kernel 都更省资源；例如 rmsnorm 的 LUT 比值达到 5.11。

**问题 4：求解是否可扩展？ → 实验。** 作者生成 integer/float 各 45 个、100–600 arithmetic operations 的 synthetic case，MILP timeout 为 3,600 s。→ **答案。** integer ASAP 均在 3 s 内，MILP 在超过 400 operations 后出现 timeout，45 例中 4 例超时；float ASAP 均小于 1 s，MILP 从约 150 operations 起超时，45 例中 37 例超时。在 MILP 与 ASAP 都解出的 41 个 integer case 中，ASAP 只有 1 例 latency 略差。[pdf:E11]（PDF 物理页 11，Section 7.3 与 Conclusion）

**不得外推的范围。** latency 来自 scheduling report，timing/resource 来自 synthesis report；论文没有 post-route congestion、板上频率、功耗、compile-time 全流程或跨 basic-block throughput 的结果。源 PDF 也没有 appendix；全文在 Section 8 后直接进入 References。因此实验支撑的是“这些 xcku3p kernel/basic block 上的联合 extraction + scheduling”，不是任意 FPGA、完整应用或 physical closure 的普遍保证。

## § 8 — Take-aways

**5 句话。** 传统 HLS 把 implementation selection 和 scheduling 分开，会过早删掉能改善全局 latency 的候选。SkyEgg 用 e-graph 同时保存代数等价式和 configured hardware implementation，再用 MILP 或 ASAP 联合 extraction 与 schedule。端口级 timing model 让 LUT、DSP48E2 和 parameterized IP 的内部 pipeline 差异进入同一个约束系统。实验显示主要收益既来自多算子 DSP pattern，也来自在频率 plateau 上选择更短的 IP latency。ASAP 在所测 synthetic workload 上接近 MILP 的 latency，却把大规模求解从 timeout 降到秒级。[pdf:E03][pdf:E05][pdf:E09][pdf:E11]

**3 句话。** SkyEgg 的贡献是把“表达式是什么、落在哪个硬件、何时执行”从三个顺序决定改成一个共同设计空间。它用一定 LUT 增长换来显著 latency 改善，并在 synthesis-report 级 timing 检查中全部达标。最关键的未决问题是孤立 primitive 的 post-synthesis timing profile 能否在真实拥塞与 placement 后仍可靠排序候选。[pdf:E10]

**1 句话。** 先保留代数与硬件配置的等价选择，再联合排时，比在固定 mapping 上做更聪明的 scheduler 更可能找到低 latency 设计。

## § 9 — 最脆弱的假设

最脆弱的假设是：**对孤立 implementation/configuration 做 Vivado synthesis 得到的 timing，在组合成较大设计后仍足以指导选择和 register cuts。** 这是核心假设，因为 SkyEgg 的 joint solver 用这些数字决定选哪个 IP latency、是否 operation chaining，以及一条 path 要插几级寄存器；若 placement、routing congestion、fanout 或跨区域连线改变了候选的相对时序，MILP 的“最优”目标与 top-3 path constraint 都会建立在错误顺序上。

论文提供的正面证据是 Table 3：所测设计在 synthesis report 中都满足 100/200/400 MHz 目标。[pdf:E10]（PDF 物理页 10，Table 3）但论文自己称 timing data 是 post-synthesis wire-load approximation，[pdf:E05]（PDF 物理页 5，Profile-based Timing Data Acquisition）且没有 post-route WNS/TNS、拥塞等级、跨 seed 波动或板级测量。因此当前证据能说明 model 在这组 synthesis 流程里可用，不能证明它在更大或更拥塞的物理设计上仍保持候选排序。

## § 10 — 最小复现实验

一周内最有价值的复现不是重建全部 benchmark，而是闭合“联合选择是否真的找回单 DSP 2-cycle 解”。

1. 用论文 Figure 1 的 16-bit `-(a+b)*c`，固定 xcku3p `-1` 与 450 MHz，建立三份 RTL/HLS 设计：Vitis 默认表达式、手工 `-((a+b)*c)` + 明确 DSP48E2 primitive、最小 SkyEgg 子集（仅该代数 rewrite、LUT rule、两个 DSP pattern 和 Eq. 7 的小 MILP）。
2. 测量 schedule latency、DSP/LUT/FF、synthesis WNS，并额外做 place-and-route 后 WNS；保留 primitive 配置与 start cycle。[pdf:E03]（PDF 物理页 3，Figure 1）
3. **支持核心 claim 的结果：** 最小 SkyEgg 自动选择与手工版本同构的单 DSP、2-cycle 解，且 route 后满足 450 MHz；默认 Vitis 仍是 3 cycles。
4. **反驳核心 claim 的结果：** SkyEgg 无法在规则给全时发现该解，或 2-cycle 解 route 后不满足时序，而 3-cycle baseline 满足；这会分别否定联合 extraction 的可实现性或 timing model 的可信度。

这项复现只验证论文最小机制，不验证 3.10× 平均 speedup、float IP plateau 或 600-operation scalability。

## § 11 — 最强反例设计

最强反例是一组 **timing-profile rank reversal** 设计：先从 library 中找两种功能等价候选 A/B，孤立 synthesis profile 预测 A latency 更小且满足时钟、B 更慢；然后在高 fanout、跨 SLR/拥塞通道、不同 placement seed 的完整 datapath 中重复实例化，使 A 的路由结构比 B 更不利。对每个设计同时跑 SkyEgg 的选择、post-route timing 与一个使用 B 的受控替代设计。

如果大量案例出现“SkyEgg 因 profile 选 A，但 A route 后违例或实际 latency/II 更差，而 B 达标”，就产生了比“某个 benchmark speedup 不高”更强的反例：它给出替代解释——论文表中的成功主要来自小 basic block 与 synthesis-level wire-load model 恰好一致，而不是 joint formulation 已经掌握可组合的物理 timing。Figure 8 所示的大 synthetic arithmetic count 只压力测试 solver runtime，并未增加 placement/routing 复杂度，不能排除这个解释。[pdf:E10][pdf:E11]

## § 12 — Follow-up Research Bet

### 主押注：RateEgg——让 e-graph 联合发明流式协议、跨迭代 schedule 与硬件实现

**候选判断，不声称 novelty。** 新研究问题是：能否把 SkyEgg 从“每个 basic block 选一个最短结束的 expression term”改造成“为持续 token stream 联合生成 rate-changing actor graph、跨迭代 pipeline schedule 和 heterogeneous hardware mapping”？这首次可能让 compiler 自动发现 polyphase、fold/unfold、fusion/fission 与 burst buffering 组合，而不是把应用 latency 简化为各 basic block latency 之和。[pdf:E08]（PDF 物理页 8，Section 7.1 的 basic-block 独立处理与 latency 求和）

核心机制是构造 **rate-aware temporal e-graph**：e-class 不只表示一个数值等价类，还表示一段带 token rate、phase 和 state transition 的 stream relation；implementation e-node 除了 \(L,t_{incoming},t_{outgoing},t_{cycle}\)，还声明 consume/produce rate、initiation interval、state footprint 和 buffer action。equality saturation 可把数学等价变换与时间变换放在同一空间，例如把一个逐 sample 表达式改写为两相 polyphase actor，再将各 phase 映射到不同 DSP/IP 配置；solver 优化 steady-state throughput、buffer bound 与资源，而不是 root finish time。这条因果链是：新的 stream 等价表示 → 可表达跨迭代重叠与 rate conversion → solver 能同时选择拓扑、时间相位与硬件配置 → 产生原 basic-block DAG 无法表示的持续吞吐能力。

它至少改变四项基本设计变量：状态表示从 value e-class 变为 stream-relation e-class；时间尺度从单次 DAG latency 变为周期稳态；可控变量新增 actor rate、phase、fold factor 和 buffer placement；系统边界从独立 basic block 扩到跨 block 的 producer–consumer pipeline。论文特异依据一方面是 implementation e-node 已能把硬件功能与配置绑定成 rewrite rule，[pdf:E04]（PDF 物理页 4，Section 4.1）另一方面是实验暴露出两个关键现象：IP latency 存在 frequency plateau，[pdf:E09]（PDF 物理页 9，rmsnorm/randnf_pdf 案例）而当前总体 latency 只是 basic-block latency 之和。[pdf:E08] 这说明设计空间中已经有“可改变时间结构而不降低频率”的自由度，但论文尚未把它提升为跨迭代数据流对象。

最大收益是自动发现以 throughput 为核心、包含多速率与状态的宏 pipeline，使 e-graph 从 expression optimizer 变成 stream architecture generator。最大科学风险是 stream equivalence 可能使 e-graph 爆炸，而且带 state 的 rewrite 很难保证 observational equivalence；此外收益也可能仅来自更丰富的手写 actor library，而非新的表示机制。

首个区分实验选一个同时含 decimation/interpolation 与 nonlinear arithmetic 的 streaming DSP kernel。比较三组：原 SkyEgg 逐 basic block 优化、固定 actor graph 上只做 mapping、RateEgg 同时 rewrite rate/phase/mapping。固定总 DSP/LUT/BRAM预算，测 steady-state II、端到端 latency、buffer peak、route 后频率。如果 RateEgg 只与“固定 actor graph + 同一 library”持平，说明收益来自 library；只有当它找到后者无法表达的 rate/phase topology，并在 route 后提高 throughput，才支持新机制。

与本文最近的工作边界是：SkyEgg 优化 expression、implementation 与单次 schedule；RateEgg 的 problem 是流式协议生成，mechanism 是有状态 rate rewrite，representation 是 temporal stream relation，experimental object 是持续 producer–consumer pipeline。由于没有在本任务中检索最新相关全文，这只是研究候选，不主张首创。

**Wild-card alternative：** 把 Vivado profile 从离线穷举数据库改成 e-graph 驱动的 active experiment design，让 compiler 选择最有信息量的少量 primitive/configuration 综合试验，学习 frequency plateau 的分段结构，再据此生成尚未测过的实现候选；它改变的是 timing-data 生成方式和 configuration-space 表示，而不是 stream topology。[pdf:E05][pdf:E09]
