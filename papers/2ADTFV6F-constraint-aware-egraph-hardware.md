# Constraint-Aware E-Graph Rewriting for Hardware Performance Optimization

- 作者：Samuel Coward、Theo Drane、George A. Constantinides
- 出处：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems，Vol. 44，No. 4
- 年份：2025
- DOI：10.1109/TCAD.2024.3483096
- Zotero key：2ADTFV6F
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是普通的代数化简，而是一个更贴近硬件设计现场的问题：当一段 RTL 只在某个输入条件成立时才会被使用，优化器能否利用这个条件，生成只需在该子域上正确、因而更快或更小的电路？例如，一个 mux 的 true branch 已经保证 `x > 0`，那么该分支里的 `abs(x)` 实际等于 `x`；传统 e-graph 却要求 rewrite 在整个输入域都成立，无法直接表达这种“只在分支条件下等价”。作者把这个问题概括为 domain refinement 加 subdomain equivalence，并把它落到 equality saturation 的数据结构中。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

它的重要性来自两个事实。第一，条件分支和输入约束在 RTL 中普遍存在，人工 datapath 设计会主动利用它们；第二，浮点加减器等高性能算术单元甚至会故意插入 case split，让不同输入区域走不同关键路径。若工具只能做全域等价 rewrite，就会漏掉这种架构级机会。论文的目标因此是让自动优化器像专家一样，在保持功能等价的前提下利用控制上下文，同时把 area–delay tradeoff 留给后续实现选择。[pdf:E01]（PDF 物理页 1，Section I）

论文的直接成果是扩展 ROVER：加入约束感知 e-graph rewriting、bit-accurate value range analysis、理论 delay model 与受 delay 约束的 ILP extraction。作者报告，在七个小型 combinational RTL benchmark 上，相比启用高级 datapath 优化的商用综合基线，完整系统平均把 critical-path delay 降低 30%，同时面积平均降低 1%。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E12]（PDF 物理页 13，Table III 与 Section V-C）

## § 2 — 前人工作与不足

e-graph 与 equality saturation 已能紧凑表示大量全域等价表达式，并通过 constructive rewrite 避免传统 compiler 的 phase-ordering 问题；egg 又提供 e-class analysis 和 proof production。ROVER 的前身已把这套机制用于 RTL area optimization，其他工作也把 e-graph 用于 multiplier、HLS 和数值稳定性优化。[pdf:E13]（PDF 物理页 2，Section II-A）

真正的缺口在“等价关系只有一个”。普通 e-class 表示全输入域上的 congruence，不能把 `x > 0 ⇒ abs(x) = x` 这种局部事实直接并入，否则会把不成立的全域 rewrite 当成真。Colored E-Graphs 通过在同一图上叠加多个有层级的 equivalence relation 处理 assumptions，但需要改变底层 equality-saturation algorithm，复杂度更高；作者的 ASSUME encoding 则保持现有 e-graph 引擎不变。[pdf:E02]（PDF 物理页 3，Section II-A，Eq. (1) 周边）

program analysis 侧已有 abstract interpretation、interval arithmetic，以及把 constraints 纳入 abstract domain 的方法，但关系域通常更昂贵；简单 interval 又会因 overapproximation 丢失精度。作者此前证明 e-class 中不同等价表达式可共同收紧 abstraction，本论文进一步把 branch constraint 变成 ASSUME node，使 rewrite 与 analysis refinement 相互促进。[pdf:E02]（PDF 物理页 3，Section II-B）

硬件侧，商用 datapath synthesis 擅长 arithmetic clustering、constant folding 与 common-subexpression sharing，却据作者所知并不会利用 mux 引入的数据相关约束来优化 area 或 delay；既有 PowerPro 会利用分支关闭冗余计算以省 power，但目标不同。Voss II、FPGA multiplier rewriting 和 carry-save dataflow transform 也没有覆盖本文这种跨分支、子域有效的深层 arithmetic transform。[pdf:E02]（PDF 物理页 3，Section II-C）

## § 3 — 重建作者的思考路径

可以把作者的路线重建为五步。

1. 专家手写浮点 datapath 时，会先把输入空间切成 near path 与 far path；每条路径只处理较小的输入区域，因此位宽、shift、LZC 和 normalization 都能专门化。
2. equality saturation 已经适合同时保存许多候选式，但它只认全域等价。若直接加入条件 rewrite，就会破坏 soundness；若另建多套 e-graph，又会牺牲现有 egg 的算法与工具链。
3. 因而需要把“在条件 `c` 下看表达式 `x`”编码成普通 expression，使子域等价转化为普通 congruence。ASSUME 的特殊 `⊥` 语义正好做到这一点：条件外的值统一变成“不关心”。
4. ASSUME 若能穿过任意 operator 向下传播，约束就能自动找到真正相关的 subexpression；若再把它接入 e-class analysis，条件还能收紧 signal range，触发 bitwidth reduction 等动态 rewrite。
5. e-graph 最终会保留许多速度与面积不同的实现，因此最后一步不能只选“最小节点数”，而要显式建模 combinational delay，并用 ILP 在 delay target 下最小化 area。

这条路径的关键不是先发明某一条浮点优化规则，而是先把“上下文”变成 e-graph 可承载、可传播、可分析、可抽取的对象，再让已有与新增 rewrite 在它上面工作。[pdf:E03]（PDF 物理页 4，Section III-A–B，Eq. (6)–(10)）[pdf:E07]（PDF 物理页 8，Section IV-B–C）

## § 4 — 核心 Intuition

核心 intuition 是：不要让 e-graph 本身理解多种等价关系，而是把“只在条件 `c` 成立时关心 `x`”包装成普通节点 `ASSUME(x,c)`。条件不成立时所有这类节点都取 `⊥`，于是“`x` 与 `y` 在子域 `c` 上等价”就等价于“两个 ASSUME 表达式在全域上等价”。[pdf:E03]（PDF 物理页 4，Eq. (7)–(10)）

一旦 ASSUME 能沿表达式树传播，branch condition 就会被送到真正受它影响的运算上；e-class analysis 随之收紧 signal range，新的 rewrite 又产生更利于分析的表达式。也就是说，rewrite 不只是改电路，analysis 也不只是给 rewrite 做静态检查，两者在同一个 e-graph 中互相放大。[pdf:E04]（PDF 物理页 5，Section III-B–C）

## § 5 — 具体方法与完整 Pipeline

以论文的 FP16 subtractor 为例，完整 pipeline 如下。

1. **输入与中间表示。** ROVER 用 Slang 解析 combinational SystemVerilog，把 RTL 转成 VeriLang，再交给 egg 构建 e-graph。后端把选中的 VeriLang expression 重新生成 SystemVerilog，并输出可供 commercial equivalence checker 验证的中间设计链。[pdf:E05]（PDF 物理页 6，Fig. 3 与 Section IV）
2. **建立约束。** 对 mux `c ? b : d`，Create rewrite 在 branch 上插入 `ASSUME(b,c)` 或相反条件；Propagate rewrite 把 ASSUME 穿过 operator 推向更深的 subexpression；Combine 累积 nested mux 的 constraints；Refine 消去冲突条件产生的 dead code。[pdf:E03]（PDF 物理页 4，Table I 与 Section III-B）
3. **限制无效膨胀。** 传播 ASSUME 会复制 sub-e-graph。ROVER 在每个 e-class 维护 reachable live e-classes；只有 condition 与待分析表达式的 live sets 相交时才创建或传播 ASSUME，以避免 reset 等与 datapath 无关的控制信号引起无收益复制。[pdf:E04]（PDF 物理页 5，Section III-B）
4. **bit-accurate value range analysis。** 每个 bitvector 对应有限个无符号整数 interval 的 union；输入默认覆盖其位宽允许的全部值。分析按 Verilog 的 signedness 与 truncation 语义，把 bitvector 转成整数区间、做 interval arithmetic，再转回无符号 bitvector range。示例中 6-bit `add` 并非 `[0,63]` 全覆盖，而是 `[0,22] ∪ [40,63]`。[pdf:E05]（PDF 物理页 6，Section IV-A）[pdf:E06]（PDF 物理页 7，signed example）
5. **动态硬件 rewrite。** range 证明 comparator 恒真时可折叠比较；range 较小时可缩减 operator bitwidth。论文示例中 `a[2:0]*b[2:0]+c[2:0]` 的输出上界为 56，因此 7-bit adder 可缩成 6 bit；论文的 cost model 估计面积小 19%，综合测得 combinational cell 少 17%。ROVER 共使用 179 条 rewrite，其中 122 条为本工作新增。[pdf:E06]（PDF 物理页 7，Section IV-B）[pdf:E07]（PDF 物理页 8，Section IV-B）
6. **搜索 FP16 双路径架构。** 作者在 baseline output 上手动插入语义冗余的 case split `ExpDiff > c ? Out : Out`。普通工具会删掉它；ROVER 则把条件传播进两条 branch。`c=1` 时，near path 证明 `ExpDiff≤1`，缩小 alignment shift；far path 证明 cancellation 有限，把 42-bit LZC 缩到只看最高位。最终一个 42-bit subtractor 被两个 12-bit subtractor 替代，形成论文 Fig. 5(b) 的 near/far dual path。[pdf:E09]（PDF 物理页 10，Fig. 5–6 与 Eq. (24)）[pdf:E10]（PDF 物理页 11，Eq. (25)–(27)）
7. **area–delay extraction。** ROVER 先用理论 gate-count 与 gate-delay cost 描述 operator。最小 delay 可用 egg 的 greedy extraction；考虑 common-subexpression reuse 的最小 area 则用 binary node-selection ILP。本文再为每个 e-class 加 delay variable 与 target constraints，对 `d_min` 到 `d_max` 的不同 target 求 minimum-area solution，得到一条 Pareto frontier。[pdf:E07]（PDF 物理页 8，Section IV-C）[pdf:E08]（PDF 物理页 9，Eq. (16)–(22)）
8. **验证与实现边界。** 实验把 baseline 与生成 RTL 都综合到 TSMC 5 nm cell library，并以商用 equivalence checker 验证功能等价。本文只研究 combinational RTL；作者称可扩展到不考虑 retiming 的 feed-forward pipelined design，但没有给出 FPGA mapping、板级时钟、throughput、I/O 或完整 HIL 数据。[pdf:E08]（PDF 物理页 9，Section IV 与 Section V setup）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有两组真正决定方法是否成立的形式化内容。

第一组是 subdomain congruence。设程序输入域为 `J`，表达式语义为 `⟦e⟧ρ`。普通 congruence 要求 `ea`、`eb` 在整个 `J` 上取值相同；给定子域 `J'⊆J`，subdomain congruence 只要求二者对所有 `ρ∈J'` 相同。不同子域形成 lattice：meet 对应子域交集，join 对应子域并集。对 Boolean condition `c`，论文把“`c` 为真时 `ea`、`eb` 等价”写成 `ea ≅_{⟦c⟧T} eb`。[pdf:E03]（PDF 物理页 4，Definition 1–2 与 Eq. (2)–(6)）

ASSUME 的关键语义是

`⟦ASSUME(x,c)⟧ρ = ⟦x⟧ρ`，若 `⟦c⟧ρ=True`；否则为 `⊥`，

且任意 operator 只要一个输入为 `⊥`，输出也为 `⊥`。于是得到

`x ≅_{⟦c⟧T} y ⇔ ASSUME(x,c) ≅ ASSUME(y,c)`。

直观地说，条件为假时两边都落到同一个“不关心”值，所以不会给全域等价增加错误要求；条件为真时又保留原表达式的真实值。这样就能用普通 e-class 保存多个条件下的局部等价，而无需改 equality-saturation kernel。[pdf:E03]（PDF 物理页 4，Eq. (7)–(10)）

ASSUME 还会细化 abstract interpretation。论文的 interval 例子中，`x,y∈[0,255]`，普通分析给 `x-y∈[-255,255]`；当 e-graph 已把 condition 改写到包含 `x-y>0` 的同一 e-class 时，`ASSUME(x-y,x>y)` 的 interval 可与 `(1,∞)` 取交，收紧为 `[1,255]`。Eq. (15) 按 `<、≤、>、≥、==、≠` 分别给出与常数 constraint 相交的 interval。[pdf:E04]（PDF 物理页 5，Eq. (13)–(15)）

第二组是 extraction ILP。binary variable `x_n` 表示 e-node 是否被最终 RTL 采用；objective `Σ area(n)x_n` 最小化面积。结构 constraints 保证被选 node 的 child e-class 至少选一个实现，并保证所有 output e-class 恰选一个实现；topological variable 排除 cyclic result。本文新增每个 e-class 的 delay variable `d_c`，让 operator delay 沿非 register edge 累积，同时用 `d_c≤d` 约束全图满足 target delay。对每个整数 delay target 求一次 minimum-area ILP，即可形成 Pareto frontier。[pdf:E08]（PDF 物理页 9，Eq. (16)–(22)）

## § 7 — 实验设计与结论

**问题 1：约束感知 rewrite 能否自动重建专家手写架构？** 作者以 FP16 subtractor 为 case study，给 baseline output 手动加上四种冗余 case split，`c∈{1,2,4,8}`，让 ROVER 自动优化每条 branch。结果由 cost model 选出的 `c=1` 与经典 floating-point literature 一致，生成的 dual path 把一个 42-bit subtraction 拆成两个 12-bit subtraction；实际综合的 area–delay curve 显示，相比商用综合后的 baseline，性能提高 20%，面积增加 3%。搜索少于 10 s，e-graph 从 100 nodes 增长到 400 多 nodes。[pdf:E09]（PDF 物理页 10，Fig. 5–6）[pdf:E10]（PDF 物理页 11，Fig. 7 与相邻正文）

**问题 2：一张 e-graph 能否支持多目标实现选择？** 在 4-input max-tree component 上，ROVER 操作 mux tree、增加 speculation，并暂时关闭 ASSUME 以避免大量 correlated mux 造成过度复制。202-node e-graph 被抽取为 18 个 delay-constrained ILP，8 s 解完，得到四种 Pareto implementations。logic synthesis 大体复现 cost model 的趋势，但最高性能点的面积惩罚被模型明显高估，说明模型漏掉了综合器实现的 sharing。[pdf:E11]（PDF 物理页 12，Fig. 8–9 与 Section V-B）

**问题 3：value range、constraint awareness 各自贡献多少？** 作者用七个 combinational benchmark 做 ablation，对比 baseline、旧 ROVER、ROVER+VRA、constraint-aware ROVER+VRA。完整系统相对 baseline 的平均 delay 降低 30%，平均 area 降低 1%；相对旧 ROVER，VRA 单独平均再降 delay 3%，加入 constraint-aware optimization 后平均再降 20%。但收益差异很大：FP16-to-Unorm11 是 `54.3 ps → 31.5 ps` 且 `12.8 μm² → 3.0 μm²`；Max Tree 是 `173.7 ps → 78.1 ps`，却把面积从 `33.9 μm²` 增到 `56.4 μm²`；Normalization 的 delay 降 22.0%，面积却增 43.5%。因此“平均更快且不增面积”不能外推到单个设计。[pdf:E11]（PDF 物理页 12，Section V-C）[pdf:E12]（PDF 物理页 13，Table III）

**问题 4：控制 e-graph 膨胀是否有效、整体成本是否可接受？** live-class gate 在 FP16-to-Unorm11 上让 saturation 时新增 nodes 减少 48%。但全套 benchmark 的 final e-graph 平均仍是 initial 的 11 倍，ROVER 平均运行 69 s，若干 extraction 达到 120 s ILP timeout；输入 RTL 平均只有 65 行。结果证明方法对小 combinational kernel 有用，同时也把 scalability 明确暴露为未解决问题。[pdf:E12]（PDF 物理页 13，Section V-C）

**证据边界。** 工艺只有 TSMC 5 nm，baseline 只有一个商用综合流程，综合使用 zero-delay constraint；论文没有公开 power measurement，只说面积通常与 power 相关且此处平均 power 增加约 1%。实验没有 sequential retiming、FPGA implementation、板级验证或大规模 SoC 数据，因此不能把这些结果解释为通用 FPGA throughput 或 end-to-end latency 证明。[pdf:E08]（PDF 物理页 9，Section V setup）[pdf:E12]（PDF 物理页 13，Table III 与 Section V-C）

## § 8 — Take-aways

**5 句话：**

1. ASSUME 把“条件下等价”编码成普通 e-graph congruence，让现有 equality-saturation engine 不改内核也能承载多种子域等价。[pdf:E03]（PDF 物理页 4，Eq. (7)–(10)）
2. 约束传播与 e-class value range analysis 形成正反馈：branch context 收紧 range，range 又解锁位宽缩减、shift/LZC 简化等 rewrite。[pdf:E04]（PDF 物理页 5，Section III-C）[pdf:E06]（PDF 物理页 7，Section IV-A–B）
3. FP16 subtractor 证明该机制能自动重建有实际算术意义的 dual-path 架构，而不只是做局部 Boolean simplification。[pdf:E09]（PDF 物理页 10，Fig. 5–6）
4. delay-aware ILP 让同一 e-graph 同时产出多种 area–delay 实现，但理论 cost 与 ILP scalability 仍是工程瓶颈。[pdf:E08]（PDF 物理页 9，Eq. (16)–(22)）[pdf:E11]（PDF 物理页 12，Fig. 9）
5. 平均 30% delay 改善是真实综合结果，但它来自小型、combinational、规则丰富且部分手动提供 case split 的 benchmark，不能直接外推到任意 RTL。[pdf:E12]（PDF 物理页 13，Table III 与结论）

**3 句话：** ASSUME 的价值在于把 context 变成普通 expression，因此 rewrite、analysis 与 extraction 可在同一 e-graph 中协同。ROVER 由此发现了商用综合未找到的 dual-path arithmetic architecture，并能产生 area–delay Pareto frontier。当前证据同时表明，case split 仍需人工暴露、e-graph/ILP 会迅速膨胀、面积与 power 代价因 benchmark 而异。

**1 句话：** 这篇论文展示了“把控制条件当成可传播的等价上下文”如何把 e-graph 从全域代数改写器推进成能探索条件化算术架构的 RTL optimizer。

## § 9 — 最脆弱的假设

最脆弱的假设是：**有价值的 input-space partition 已经以 mux/case split 出现在 RTL 中，或设计者愿意手动把它插进去。** ASSUME 只能利用已有 condition；它不会从 branchless datapath 中发明 near/far path。论文最有说服力的 FP16 subtractor 结果恰恰是在作者手动加入 `ExpDiff>c ? Out : Out` 后得到的，随后 ROVER 才把 condition 向下传播并发现两个 12-bit paths。[pdf:E09]（PDF 物理页 10，Fig. 5–6 与相邻正文）

如果实际 RTL 没有暴露有利 partition，constraint-aware machinery 可能完全没有额外收益。论文自己的 FP16-to-Unorm11 benchmark 就因为缺少 data-dependent mux 而未从 constraint awareness 得到进一步改善；结论也明确把“自动合成 profitable case split”列为 future work。[pdf:E11]（PDF 物理页 12，Section V-C）[pdf:E12]（PDF 物理页 13，Conclusion）

这不是小缺陷，因为它决定了系统究竟是“自动 architecture discovery”还是“在专家已经指出正确切分变量后自动完成 branch specialization”。论文提供了后半段能力的强证据，却尚未证明前半段。即便未来枚举 case split，也还要解决 predicate search、额外 mux/parallel activity 的 area-power 成本，以及 e-graph duplication。

## § 10 — 最小复现实验

一周内最有价值的复现，不是跑完整七项 benchmark，而是只检验“ASSUME + VRA 是否真的能从冗余切分发现 dual path”。

- **数据与设计：** 使用论文 Fig. 5(a) 的 FP16 mantissa subtract core，构造三个 RTL：无 case split 的 baseline；带 `c=1` 冗余 mux 但禁用 ASSUME/VRA；带相同 mux并启用 ASSUME/VRA。输入 sorting 与 exponent-difference block 按论文一样排除在 core 之外。[pdf:E09]（PDF 物理页 10，Fig. 5 caption）
- **实现：** 只启用完成 near/far transform 必需的 Create/Propagate/Combine/Refine、interval refinement、shift/LZC/bitwidth rewrites；保存生成 RTL 与 formal-equivalence result，不需要复现完整 179 条规则。
- **测量：** 记录是否生成两个 12-bit subtractor、e-graph node growth、rewrite runtime；用同一 synthesis flow 比较 mapped critical path 与 area，并用 equivalence checking 覆盖全输入域。若没有 TSMC 5 nm library，可用同一开源 standard-cell library做相对机制复现，但不得把绝对数与论文直接比较。
- **支持标准：** 启用 ASSUME/VRA 的版本必须在全输入域等价，并独有地生成 Fig. 5(b) 的结构特征；其 mapped delay 至少相对“同 mux、禁用约束感知”稳定改善约 15%，同时 area penalty 不超过 5%。该阈值围绕论文的 20%/3% 结果留出工具链差异。[pdf:E10]（PDF 物理页 11，Fig. 7 与相邻正文）
- **反驳标准：** 禁用约束感知的版本也得到同等 dual path，或启用后未出现结构变化/没有稳定 delay gain，或 equivalence 失败。前两种结果会说明论文收益可能主要来自综合器、手工 rewrite 或 benchmark coding，而非 ASSUME mechanism。

## § 11 — 最强反例设计

最强反例应同时攻击“泛化性”与“可扩展性”：构造一族具有真实有利条件、但条件是关系型而非单变量 interval 的 nested-mux datapath。例如每条 branch 保证 `x+y=k`、parity 相同或两个 operands 互斥非零；这些条件足以让人工设计大幅共享或删减算术，但对有限 interval union 几乎不收紧任何单个 signal range。随着 branch depth 从 1 增到 8，固定相同的算术规模和最优电路，比较三件事：ROVER 是否发现人工已知优化、e-graph nodes 是否指数式增长、ILP 是否在 timeout 内抽出结果。

这个反例有两个可能的致命结果。第一，ASSUME 被正确传播却因 non-relational VRA 看不见 `x+y=k` 而没有触发有价值 rewrite，说明“局部化 constraint reasoning”不等于“能理解实际 constraint”。第二，加入足够多的 relational rewrites 后才找到优化，但 sub-e-graph duplication 与 extraction timeout 先失控，说明该 encoding 在 control-heavy RTL 上不能兑现一般性。论文已经给出相关预警：Max Tree 的 correlated mux 迫使作者关闭 ASSUME、改成两遍运行；全套 benchmark 的 e-graph 平均扩大 11 倍，并有 ILP 达到 120 s timeout。[pdf:E11]（PDF 物理页 12，Section V-B）[pdf:E12]（PDF 物理页 13，Section V-C）

为了排除“缺少某条手工 rewrite”的替代解释，反例应把人工最优 transform 作为一条可用 rewrite 加入，但只允许它在 relational condition 被证明后触发。如果 ROVER仍无法在合理资源内证明并应用它，失败就落在约束表示与搜索机制本身，而不是 rewrite library 不全。

## § 12 — Follow-up Research Bet

**研究押注：让 e-graph 从“利用已有分支”升级为“联合发明输入空间分区与算术架构”。** 新问题不是如何更安全地使用 ASSUME，而是：给定完全 branchless 的 RTL，能否从候选表达式的 critical-path activation pattern 中自动发现一组 input predicates，并让每个区域采用不同的 arithmetic representation？一旦成功，优化器就首次能从朴素单路径 RTL 直接合成 near/far path、多段 normalization 或其他互斥 datapath，而不需要专家先插入 mux。

核心机制可以是 **critical-path witness partition**。对 e-graph 中候选 operator path，符号化记录“哪些输入让该 path 真正成为 critical path”；把相互补充的 witness regions 聚类成少量 predicate partitions；将 partition 作为一等 e-graph object 物化成 case split；随后用 ASSUME 在各 region 内收紧 range，并让 branch-specific rewrite 产生不同位宽、shift/LZC 和 operator topology；最后由扩展 ILP 联合选择 predicate、branch implementation、跨 branch sharing 与 mux cost。因果链是“路径激活区域不同 → 自动产生 domain partition → 每区 range 与等价关系不同 → 每区可选架构不同 → 组合后出现单一路径 RTL 不具有的新关键路径结构”。它至少改变了问题定义（固定控制结构优化变为控制拓扑合成）、可控变量（predicate 与 partition 数量）和硬件映射（每区 arithmetic architecture 与跨区 sharing）。

这个押注直接由全文两类具体证据支撑。方法侧，ASSUME 的 Eq. (7)–(10) 已证明子域等价可被普通 e-graph soundly 表示，delay-constrained ILP 也已能在一张图里选择 area–delay implementation。[pdf:E03]（PDF 物理页 4，Eq. (7)–(10)）[pdf:E08]（PDF 物理页 9，Eq. (16)–(22)）实验侧，作者手动枚举 `c∈{1,2,4,8}` 后，ROVER 的模型选出文献一致的 `c=1`，并自动把 42-bit subtractor 变成两条 12-bit paths；同时，单路径版本性能几乎与商用 baseline 重合，说明真正的新能力来自 partition，而不是同一路径内再做一轮 rewrite。[pdf:E09]（PDF 物理页 10，Fig. 5–6）[pdf:E10]（PDF 物理页 11，Fig. 7）论文结论也承认 case split 仍由人工插入，并把 automatic profitable case-split synthesis 列为下一步。[pdf:E12]（PDF 物理页 13，Conclusion）

最大收益是把 arithmetic expert 的“看出哪一段输入不会走满关键路径”变成可搜索的 architecture variable，从而自动产生原 RTL 中不存在的控制与数据通路。最大科学风险是 critical-path witness 对 gate mapping 不稳定：理论 component model 可能把综合器能共享的逻辑误判为互斥瓶颈，导致 predicate search 找到只在模型里更优、实际却被 mux、fanout 和 parallel switching 抵消的 partition；Fig. 9 已显示最高性能点的 area penalty 被模型高估。[pdf:E11]（PDF 物理页 12，Fig. 9）

首个判别实验应从**没有冗余 mux**的 Fig. 5(a) baseline 开始，禁止硬编码 `ExpDiff` 与阈值集合，只给 optimizer bitvector semantics 和 operator cost。训练/开发只使用 FP8 subtract，测试用 FP16 subtract；看系统是否独立生成 `ExpDiff≤1`、两个 12-bit subtractors，并达到接近手工 `c=1` 版本的综合 Pareto curve。最强替代解释是“系统只是枚举了常数比较，碰巧复现作者已知模板”；因此再加入一个结构相同但最佳 split 由 operand width 与 normalization rule 改变的合成 benchmark。若 predicate 能随结构改变而移动，并且 ablation 掉 witness-region representation 后失败，才支持“路径激活机制”而非模板枚举。

与论文最近讨论的 Colored E-Graphs、relational contextual equality saturation、普通 RTL e-graph rewriting 的实质区别在于：这些工作主要改变**如何表示已有 context 或等价关系**，本押注改变的是**优化对象本身**，把 input partition 与控制拓扑加入待合成 design space。由于本文没有系统检索 2025 年后的相关工作，这只是候选判断，不声称 novelty。

**Wild-card alternative：** 构建带显式 clock-cycle 与 pipeline-boundary 的 temporal e-graph，让 rewrite 同时移动 arithmetic expression、register 与 handshake boundary，从而从 feed-forward RTL 联合合成 retiming、stage-local ASSUME domain 和 throughput-optimal pipeline；这条路线改变时间表示与 sequential hardware mapping，机制上不同于 input-space partition。
