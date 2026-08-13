# EagerlyElastic: Correct-by-Construction Eager Execution in Dynamically-Scheduled HLS

作者：Shun Katsumi、Emmet Murphy、Lana Josipović [pdf:E01]（PDF 物理页 2，标题页作者栏）

出处：Proceedings of the 2026 ACM/SIGDA International Symposium on Field Programmable Gate Arrays（FPGA ’26），Seaside, CA, USA [pdf:E01]（PDF 物理页 2，论文出处栏）

年份：2026 [pdf:E01]（PDF 物理页 2，论文出处栏）

DOI：10.1145/3748173.3779196 [pdf:E01]（PDF 物理页 2，论文出处栏）

Zotero key：VUIJ38A8

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 动态调度 HLS（dynamically-scheduled HLS）生成的 elastic circuit 能按运行时 control flow 与 memory dependency 自适应执行，但这类 token-driven 电路难以做激进优化，因为一旦控制 token 数量、顺序或提交位置处理错误，就可能出现 deadlock、错误提交或全局语义改变。论文要解决的问题是：能否把 eager execution 引入 elastic circuit，在 branch condition 尚未到达时先执行条件两侧，同时仍以 correct-by-construction 的方式保持电路正确性。[pdf:E02]（PDF 物理页 2，Abstract）

重要性来自两个相反事实。第一，branch condition 尤其会卡住 loop re-entry，使大量已经存在的 FPGA datapath 并行度闲置；若能延后这条控制依赖，就可能直接提高 initiation rate 与总吞吐。第二，传统 processor 上的 eager execution 往往需要复制 pipeline，并带来错误路径 side effect 与安全风险；因此单纯把处理器式 speculation 搬到 HLS 并不现实。[pdf:E03]（PDF 物理页 2，Section 1）Elastic circuit 的特殊机会在于，它本来就把软件操作映射成许多专用硬件单元，并用 suppressor 与 mux 实现 commit-based control flow，所以“先算、后决定是否提交”不必从零搭建一套计算资源。[pdf:E06]（PDF 物理页 4，Section 2.1）

**作者报告的价值。** 在其选定 kernels 上，摘要报告平均加速为 3.2×，平均 LUT 与 FF 分别增加到 1.2× 和 1.3×；作者同时强调，计算单元无需复制，主要变化发生在 control path。[pdf:E02]（PDF 物理页 2，Abstract）更深的价值不是一个固定优化 pass，而是打开了一个由 eager extent、loop re-entry 次数、mux 后路径选择和 buffering 共同定义的新设计空间；论文自己也把这视为尚未充分探索的 Pareto frontier。[pdf:E05]（PDF 物理页 3，Figure 1 后贡献总结）

## § 2 — 前人工作与不足

以下是**论文对相关工作的归纳**，不是本卡对外部文献的独立复核。

- **If-conversion（条件转换）**会把 control dependency 改写成 data dependency，并对有 side effect 的操作加 predicate。它实现简单、在编译器和 HLS 前端中常见，但通常局限于 acyclic control flow，不能打破 loop re-entry 的控制依赖；而且 select 之后的操作仍要等 condition，因此无法得到本文追求的跨 mux、跨迭代提前执行。[pdf:E09]（PDF 物理页 5，Section 3.1）
- **Value prediction（值预测）**能打破任意 data dependency，适用面比 eager execution 更广，但需要保存状态、misprediction rollback、额外 commit unit 与 tagged token。论文指出，既有 elastic value prediction 实现引入 custom units，导致 formal reasoning 困难、buffering 等既有动态 HLS 优化不兼容，并造成 LUT、critical path 和 clock frequency 开销。[pdf:E10]（PDF 物理页 5，Sections 3.2–3.3）
- **SpecHLS**在 static HLS 的源代码层加入 FSM、recovery logic 和 commit mechanism，目标主要是 branch prediction。论文将它视为与本文大体正交：HLS 范式不同、speculation 机制不同，并且不是本文所说的 correct-by-construction local circuit rewrite。[pdf:E10]（PDF 物理页 5，Section 3.4）[pdf:E12]（PDF 物理页 6，Section 3.4 续文）
- **ElasticMiter**已经提供了证明 elastic circuit 局部 rewrite 等价的框架：给出 initial circuit、输入到达约束组成的 context、以及 transformed circuit，用 symbolic model checker 一次性验证该 pattern，随后 synthesis 中可反复应用。此前随 ElasticMiter 展示的 rewrites 主要改变 token steering，而不改变 datapath 的执行行为；缺口在于，尚没有一组面向 eager execution、会真正改变哪些操作提前执行的 verified rewrites。[pdf:E12]（PDF 物理页 6，Section 3.5）[pdf:E13]（PDF 物理页 6，Section 4 前的对比说明）

因此，本文的相对定位不是“又一种 branch predictor”，而是利用 elastic circuit 已有的 commit-based control 与空间并行，把 eager execution 表达为一组可局部匹配、可组合、预先证明过的 control-path rewrites。其不足也随之埋下：只要某类 control-flow topology 没有对应 rewrite 或 context 无法匹配，优化就无法继续。

## § 3 — 重建作者的思考路径

下面是一条**基于论文背景证据的合理重建**，不是作者逐字给出的历史叙述。

1. 先观察动态 HLS 的控制实现：conditional branch 并不是一个必须先执行完再选择路径的传统 branch unit，而是 fork 复制 token、两个 mutually-exclusive suppressor 决定哪条路径真正提交，mux 再处理 reconvergence。也就是说，标准 elastic circuit 已经天然接近 commit-based execution。[pdf:E06]（PDF 物理页 4，Section 2.1）
2. 再观察性能失败模式：在 do-while loop 中，下一次迭代常被 branch condition 卡住；如果 condition 是 bottleneck，提前允许一次 loop re-entry 就可把示例吞吐从 0.25 提到 0.5，再提前一次则到 0.75。[pdf:E07]（PDF 物理页 4，Figure 2）
3. 传统 if-conversion 不能处理循环回边，value prediction 又要承担预测、rollback 和全电路 tagged-token 代价。因此真正需要的不是“猜 condition”，而是保留 condition 的最终裁决权，只把裁决点向后移。[pdf:E09]（PDF 物理页 5，Section 3.1）[pdf:E10]（PDF 物理页 5，Section 3.3）
4. 在 processor 中，执行两条路径意味着复制或争抢通用 pipeline；在 spatial elastic circuit 中，大量 branch-side 操作本来就各有硬件单元。于是可以推断，若只移动 suppressor，很多 eager work 可由现成 datapath 承担，成本主要落在 control logic 与额外 in-flight token 的 buffering 上，而不是复制算术单元。[pdf:E03]（PDF 物理页 2，Section 1）
5. 最后面对正确性问题：全局手工移动 suppressor 很难推理，随着 eager extent 增大，token imbalance、错误 commit 与 deadlock 风险迅速上升。既然 ElasticMiter 已能验证局部等价 pattern，最自然的研究路线就是把复杂全局变换拆成一组带 context 的、一次证明后反复应用的 local rewrites。[pdf:E08]（PDF 物理页 4，Section 2.2）[pdf:E12]（PDF 物理页 6，Section 3.5）

这条路径的关键转折是：把 speculation 从“预测一个值并准备回滚”改写成“让已有路径先执行，并把 discard/commit boundary 延后”。

## § 4 — 核心 Intuition

核心不是预测 branch condition，也不是复制 datapath，而是把 commit/discard point 沿现有 token graph 向下推：条件两侧先运行，直到 store 或其他必须受控的 side effect 前再由 suppressor 决定是否提交。[pdf:E06]（PDF 物理页 4，Section 2.1）由于 elastic circuit 已有专用运算单元，这一动作主要改 control path；每个局部变换先用 ElasticMiter 证明等价，再作为 rewrite 组合使用。[pdf:E11]（PDF 物理页 6，Figure 3）性能来自延后 condition dependency，尤其是重复提前 loop re-entry；代价则是更多 in-flight tokens、buffering 和共享单元竞争，而不是“免费并行”。[pdf:E14]（PDF 物理页 7，Figure 4）[pdf:E22]（PDF 物理页 10，Section 7.2）

## § 5 — 具体方法与完整 Pipeline

以论文 Figure 1/2 的 `do { i = i + 1; } while (i < a[i])` 为例，完整 pipeline 如下。

1. **从程序到标准 elastic circuit。** Dynamatic 把每个算术、逻辑、load/store 操作映射为 fine-grained elastic unit，以 latency-insensitive handshake channel 传 token；fork 复制输入，suppressor 实现 divergent control，mux 实现 convergent control。此处没有连续时间模型或数值积分，时间对象是 token arrival、clock cycle、loop throughput 与 initiation behavior。[pdf:E04]（PDF 物理页 3，Figure 1）[pdf:E06]（PDF 物理页 4，Section 2.1）
2. **定位 condition bottleneck 并选择 eager depth。** 在线 HLS flow 对“保留 branch dependency”和“移除该 dependency”的电路做 throughput analysis，两者差异用于选择 rewrite sequence 中的参数 `n`，也就是每个 loop 要提前 re-enter 多少次。[pdf:E18]（PDF 物理页 9，Section 5 的 rewrite sequence）[pdf:E19]（PDF 物理页 9，Sections 5–7.1）
3. **沿直线 datapath 下推 suppressor。** Rewrite A 把 suppressor 越过 side-effect-free unit，使 branch 两侧无需等待 condition 即可执行。它不越过 store，结果在 store 前才 commit/discard；论文还说明，某些 Dynamatic out-of-order load-store queue 暂不支持 eager load，因此该 memory interface 处会保守停止变换。[pdf:E11]（PDF 物理页 6，Figure 3 的 Rewrite A）[pdf:E13]（PDF 物理页 6，Section 4.1）[pdf:E27]（PDF 物理页 7，Section 4.1 续文）
4. **提前 loop re-entry。** Rewrite D 把 loop-header mux 前的控制依赖向后推，使一次新的迭代可在 condition 到达前进入。其关键性质是 infinitely re-applicable：每重复一次 D，再配合 A 或 G 把 suppressor 推过 loop body，就多允许一次 eager re-entry。Figure 2 中，标准 Circuit 2A 的吞吐为 0.25，应用一次后 Circuit 2B 为 0.5，再应用一次后 Circuit 2C 为 0.75。[pdf:E07]（PDF 物理页 4，Figure 2）[pdf:E14]（PDF 物理页 7，Figure 4）[pdf:E16]（PDF 物理页 8，Section 4.4）
5. **处理 reconvergence 与复杂 control flow。** Rewrite B 让 mux 两侧都继续 eager execution，但两股 execution 会顺序共享 mux 后的 datapath，可能互相阻塞；Rewrite C 只让一侧无条件越过 mux，相当于优先一条路径。Rewrite E/F 处理 multiple-exit loop，G/H 处理 loop 内 if 或嵌套 if；每一种新 topology 都必须满足对应 initial sub-circuit 与 context 才可应用。[pdf:E15]（PDF 物理页 7，Section 4.3）[pdf:E17]（PDF 物理页 8，Figure 5 与 Section 4.5）
6. **按 sequence 自动组合。** 默认 sequence 先让 straight paths eager，再预处理 multiple-exit loop，随后重复 D 与 A/G，最后用 B 配合 A/G/H 继续穿过 convergent control。sequence 非 confluent，D 又可无限重用，所以工具必须给出有限 `n`；论文当前策略仍是“假定 eager execution 总有利并尽量最大化”，而不是成熟的全局 design-space search。[pdf:E18]（PDF 物理页 9，Section 5）
7. **生成与映射。** Offline flow 只需一次性证明 rewrite pattern；online flow 是集成进 Dynamatic 的 MLIR compiler pass，输出 eager elastic circuit，再走常规 simulation、co-simulation、synthesis 与 place-and-route。[pdf:E19]（PDF 物理页 9，Section 6）主文没有报告各 benchmark 的具体 bit width、fixed/floating-point 格式或 memory bandwidth 配置；报告的平台信息集中在实验设置，而不是方法定义中。[pdf:E21]（PDF 物理页 10，Section 7.1）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有给出传统意义上的定理—引理—证明推导，也没有展开 ElasticMiter 的完整 model-checking proof。其形式化核心是 **rewrite contract、token-count context、rewrite sequence 和 throughput scaling**。

1. **Rewrite contract。** Figure 3 用 `#A == #B == #C` 一类条件表示相关输入端在给定执行前缀中到达的 token 数相等；Rewrite A 还要求 Unit X 无 side effect，并且每个 input 消耗一个 token、每个 output 产生一个 token。直觉上，这些 context 条件保证移动 suppressor 后不会改变 token 守恒、输出顺序或提交语义。[pdf:E11]（PDF 物理页 6，Figure 3）
2. **自动应用的核心式。** 论文给出的一个实用 sequence 是：

   \[
   A^{*}E^{*}F^{*}\left(D(A\mid G)^{*}\right)^{n}\left(B(A\mid G\mid H)^{*}\right)^{*}.
   \]

   其中 `*` 表示反复应用子序列直到不再 applicable，`|` 表示无优先级地选择一个可用 rewrite，`n` 是每个 loop 的 eager re-entry 次数。[pdf:E18]（PDF 物理页 9，Section 5 的公式及其四段解释）该式不是一个保证全局最优的优化目标，而是作者当前使用的有限化 heuristic；它不使用 Rewrite C，也不进入其他 loop 或处理 multiple-entry loop。[pdf:E19]（PDF 物理页 9，Section 5 limitations）
3. **吞吐直觉。** 论文报告：只要 branch condition 仍是 bottleneck，`n = 1` 使原始吞吐翻倍，`n = 2` 使其变为三倍，概括为原始吞吐乘以 `n + 1`；一旦 condition bottleneck 消失，继续增大 `n` 不再加速，nested loop 甚至会变慢。[pdf:E25]（PDF 物理页 11，Figure 7 及相邻正文）便于理解，可把作者描述压缩为一个**基于证据的近似重述**：`T(n) ≈ min((n+1)T₀, T_other-bottleneck)`；这不是论文正式给出的新公式，而是对其曲线与文字的抽象。
4. **证明方式与成本。** 每个 initial circuit、context、transformed circuit 被写成 SMV，由 symbolic model checker 做 equivalence checking；pattern 只证明一次，之后在 synthesis 中复用。A–H 八个 rewrite 的报告 proof time 为 2.7–60.0 秒，最长的是 H 的 60.0 秒。[pdf:E12]（PDF 物理页 6，Section 3.5）[pdf:E20]（PDF 物理页 10，Table 2）

因此，这篇论文的“数学”主要是有限状态等价与 token-balance 约束，而不是数值算法或解析性能模型。真正未展开的部分是：多个 local proof 在任意 rewrite overlap、buffer placement 和全局 backpressure 下如何形成完整的 compositional theorem，主文只给出框架性说明。

## § 7 — 实验设计与结论

实验比较 standard Dynamatic elastic circuit、既有 elastic value prediction、EagerlyElastic 的默认 “Eager” sequence，以及两个 if-statement benchmark 上以 Rewrite C 替换 Rewrite B 的 “Custom” sequence。Table 1 覆盖 13 类 benchmark，包括 single/nested loop、multiple exits、if、sparse inner product 和 KMP；Table 2 给出 rewrite proof time。[pdf:E20]（PDF 物理页 10，Tables 1–2）性能由 ModelSim 2020.1 simulation 获得，resource 与 frequency 使用 Vivado 2025.1 的 post-routing 结果，power 是 simulation-vector-driven post-synthesis estimation，目标器件为 Kintex-7、目标 clock period 为 7 ns；Benchmark 6 另在 AMD Zynq UltraScale+ ZU7EV MPSoC 上实际运行验证。[pdf:E21]（PDF 物理页 10，Section 7.1）

- **问题：rewrite 是否能以低验证成本反复安全使用？→ 实验：** 对 A–H 分别做一次 equivalence proof。**答案：** 报告时间从 2.7 秒到 60.0 秒，且这些 proof 不是每个设计重新执行。[pdf:E20]（PDF 物理页 10，Table 2）
- **问题：eager execution 是否真正提高端到端性能？→ 实验：** 在 Table 3 的 QoR 中比较 time、cycles、critical path、LUT、FF、DSP 和 dynamic power。**答案：** 摘要对选定 kernels 报告平均 3.2× speedup、1.2× LUT 和 1.3× FF；Table 3 的最高单项是 Subdiagonal 的 10.4× time speedup。除故意设置为 data-speculation case 的 Sparse 外，作者称 EagerlyElastic 在其余 benchmark 上取得最佳性能。[pdf:E02]（PDF 物理页 2，Abstract）[pdf:E22]（PDF 物理页 10，Section 7.2）[pdf:E23]（PDF 物理页 11，Table 3）
- **问题：与 value prediction 相比，控制路径 rewrite 是否更轻？→ 实验：** 在 value prediction 能运行的 kernel 上比较资源、critical path 与 power。**答案：** 论文报告 EagerlyElastic 在每个可比 kernel 上 LUT 更少，在 10 个可比 kernel 中有 7 个 FF 更少，并在所有 kernel 上 dynamic power 低于 value prediction；同时 value-prediction artifact 无法处理需要 multiple predictions 的 Benchmark 7、8、13 及并行化 Benchmark 1。[pdf:E22]（PDF 物理页 10，Section 7.2）[pdf:E23]（PDF 物理页 11，Table 3）
- **问题：area 增长究竟来自 rewrite logic 还是高吞吐所需 buffering？→ 实验：** 对多个 `n` 比较不加 performance-maximizing buffering 的 eager circuit，再与最终 buffered design 比较。**答案：** Figure 6 显示 rewrite 本身只带来小幅 LUT/FF 增长，主要成本来自更多 unresolved in-flight values 和为避免 throughput throttling 而加入的 buffers。[pdf:E22]（PDF 物理页 10，Auxiliary Experiment 1）[pdf:E24]（PDF 物理页 11，Figure 6）
- **问题：`n` 是否构成可调的性能—面积变量？→ 实验：** sweep eager loop re-entry count，记录 execution cycles 与 LUT。**答案：** condition 仍是瓶颈时，增加 `n` 按 `n+1` 提高吞吐；瓶颈消失后继续增加只增资源，nested loop 还可能变慢，形成清晰 Pareto frontier。[pdf:E25]（PDF 物理页 11，Figure 7）
- **问题：Rewrite B 与 C 是否需要按 workload 选择？→ 实验：** 在 Balanced/Unbalanced if benchmark 上比较默认 Eager 与 Custom。**答案：** Balanced 中默认 Eager 为 1.4×，Custom 为 1.2×；Unbalanced 中 Custom 为 1.8×，高于默认 Eager 的 1.6×，证明输入到达时间和 mux 后单元利用率会改变最佳 rewrite。[pdf:E19]（PDF 物理页 9，Section 5 对 Custom 的说明）[pdf:E23]（PDF 物理页 11，Table 3）

**不得外推的范围。** 多数对象是小 kernel，只有一个 benchmark 报告了板上运行；value-prediction baseline 的公开实现不支持多个 prediction，因此部分比较缺项；论文也因引用既有工作中“token prediction 比 Vivado HLS 快 2×–15×”而没有直接与 Vivado HLS 做本次 apples-to-apples 比较。[pdf:E21]（PDF 物理页 10，Section 7.1）因此，结果有力支持“branch-condition-bound elastic loops/ifs 可从该机制获益”，但不足以证明对 memory-bandwidth-bound、重度 functional-unit sharing、复杂 aliasing 或大规模真实应用同样普遍有效。

## § 8 — Take-aways

**5 句话：**

1. EagerlyElastic 把 eager execution 重新表述为 elastic control path 上 suppressor 的下推，而不是 branch prediction 或 datapath replication。[pdf:E04]（PDF 物理页 3，Figure 1）
2. Rewrite A 让 straight datapath 提前执行，B/C 处理 reconvergent mux，D 可重复地提前 loop re-entry，E–H 覆盖若干 multiple-exit 与 nested-control case。[pdf:E11]（PDF 物理页 6，Figure 3）[pdf:E17]（PDF 物理页 8，Figure 5）
3. 每个 pattern 先由 ElasticMiter 做一次局部等价证明，online compiler 再在 Dynamatic 的 MLIR pass 中匹配并应用这些 rewrites。[pdf:E12]（PDF 物理页 6，Section 3.5）[pdf:E19]（PDF 物理页 9，Section 6）
4. 论文在选定 kernels 上报告平均 3.2× speedup，并展示最高 10.4×，主要额外资源来自 buffering 而非 rewrite logic。[pdf:E02]（PDF 物理页 2，Abstract）[pdf:E23]（PDF 物理页 11，Table 3）[pdf:E24]（PDF 物理页 11，Figure 6）
5. 当前自动 sequence 仍假定 eager execution 总有利，最佳 `n` 与 B/C 选择高度依赖具体 bottleneck，因此真正困难的问题已从“能不能做”转为“怎样全局选择”。[pdf:E18]（PDF 物理页 9，Section 5）

**3 句话：**

1. 这篇论文证明了 elastic circuit 的 commit-based control 可以在不复制算术单元的情况下承载强力 eager execution。[pdf:E05]（PDF 物理页 3，贡献总结）
2. 它用 verified local rewrites 把 branch-condition latency 转化为可调的 loop re-entry 与 path-priority 设计变量，并得到显著但非普遍的加速。[pdf:E14]（PDF 物理页 7，Figure 4）[pdf:E25]（PDF 物理页 11，Figure 7）
3. 下一阶段的核心不是再证明 eager 有效，而是建立能处理任意 topology、共享资源和 buffering 的全局 synthesis/search 方法。[pdf:E26]（PDF 物理页 11，Conclusion）

**1 句话：** EagerlyElastic 的本质是“把分支裁决往后推、让现有空间 datapath 先跑”，并用局部等价 rewrite 把这种激进执行变成可自动组合的 HLS 优化。[pdf:E26]（PDF 物理页 11，Conclusion）

## § 9 — 最脆弱的假设

**最脆弱假设：branch condition 是主要瓶颈，而且新增 eager tokens 能利用闲置 datapath，而不会先把共享 mux、functional unit、memory port 或 FIFO 压满。** 如果该假设不成立，correctness 仍可能保持，但论文的性能核心会直接失效：不同路径在 mux 后顺序共享资源，错误路径或低价值路径可能挡住真正需要提交的路径。作者明确承认 Rewrite B/C 的优劣依赖各输入 token 到达时间和 mux 下方单元是否 under-utilized，并指出不同 executions 可以互相 block/delay。[pdf:E15]（PDF 物理页 7，Section 4.3）

论文为该假设提供了三类压力证据：Sparse 需要预测非 branch value，Eager 仅 1.0×；Balanced/Unbalanced if 对 B/C 的最优选择相反；`n` 超过 condition-bottleneck 消失点后不再加速，nested loop 还会变慢。[pdf:E23]（PDF 物理页 11，Table 3）[pdf:E25]（PDF 物理页 11，Figure 7）但证据仍不充分，因为默认 sequence 明确“假定 eager execution 总有利并最大化 eager extent”，缺少对 branch bias、memory contention、functional-unit sharing、finite FIFO 深度和大型 irregular control graph 的系统 sweep。[pdf:E18]（PDF 物理页 9，Section 5）真正需要验证的不是“某个 branch 能否提前”，而是“提前产生的 token 是否在全局资源网络中仍具有正的 marginal throughput”。

## § 10 — 最小复现实验

一周内最值得复现的是 **Rewrite D 的 `n+1` loop-throughput claim 与其饱和点**，不必重建完整 Dynamatic。

- **数据与电路：** 直接复刻 Figure 1/2 的 do-while loop，生成 100–10,000 次迭代的 synthetic input；把 loop body、branch-condition path 和 memory/read path 的 latency 做成可调参数。实现三个 cycle-accurate ready/valid 模型或小型 RTL：baseline Circuit 2A、`n=1` 的 Circuit 2B、`n=2` 的 Circuit 2C。[pdf:E07]（PDF 物理页 4，Figure 2）
- **实现内容：** 只实现 fork、mux、suppressor、1-cycle arithmetic unit 和有限深 FIFO；按 Figure 3/4 手工实现 Rewrite A 与 D，并保持 store/输出在 condition 到达后才 commit。[pdf:E11]（PDF 物理页 6，Figure 3）[pdf:E14]（PDF 物理页 7，Figure 4）
- **测量：** 总 cycles、steady-state loop throughput、各 FIFO 峰值 occupancy、discarded token 数、是否 deadlock，以及输出是否逐项等于软件 reference；再 sweep branch latency、buffer depth 和 `n`。
- **支持条件：** 当 branch condition 是唯一瓶颈时，`n=1` 接近 2× throughput、`n=2` 接近 3×，输出完全一致；当其他 datapath 成为瓶颈后，继续增大 `n` 不再缩短 cycles，并显著增加 occupancy。[pdf:E16]（PDF 物理页 8，Section 4.4）[pdf:E25]（PDF 物理页 11，Figure 7）
- **反驳条件：** 在 condition 明显为瓶颈且 FIFO 足够时仍看不到 `n+1` scaling，或出现 token mismatch、输出乱序、deadlock；这会直接否定最核心的机制，而不是只说明完整工具链没复现好。

若时间允许，最后把三个小电路用同一目标频率综合到任意 FPGA，检查 rewrite logic 本身是否确实只带来小幅 LUT/FF，而 buffering 才主导增长；这对应 Figure 6 的辅助结论。[pdf:E24]（PDF 物理页 11，Figure 6）

## § 11 — 最强反例设计

最强的反例不是简单选一个“branch 不慢”的程序，而是构造一个**baseline 中 branch condition 确实是瓶颈，但 eager execution 因共享资源自干扰而更慢**的电路。

具体做法：设计一个 nested do-while loop，内部 if 的两条路径在 mux 后汇合到同一个长 latency、低 initiation-rate 的 multiplier 或 single-port RAM；高概率热路径很短，低概率冷路径会产生一串可提前执行的 tokens。延迟 branch condition，使 baseline 看起来有明确控制瓶颈；然后分别生成 baseline、默认 Rewrite B、只优先热路径的 Rewrite C，以及多个 `n` 的 Rewrite D 版本。Rewrite B 会让两侧 execution 顺序通过共享区域，论文已明确指出它们可能互相 block/delay；默认 sequence 又假定 eager 总有利并优先最大化 extent。[pdf:E15]（PDF 物理页 7，Section 4.3）[pdf:E19]（PDF 物理页 9，Section 5 limitations）

实验 sweep branch bias、冷路径 burst 长度、共享单元 II、FIFO 深度和 `n`，测量 useful-token latency、总 cycles、buffer occupancy、discarded work、LUT/FF 和 clock period。最有力的结果是：即使 baseline 的 condition path 最长，默认 Eager 仍因冷路径 tokens 占据 mux 后单元而慢于 baseline，且增大 `n` 单调恶化；若 Rewrite C 能恢复性能，则说明本文的局部 rewrite 是有价值的，但“用去掉 condition 后的 throughput 差来选 `n`、并最大化 eager extent”的自动策略不足。若 B 与 C 都失败，则更直接说明 eager execution 在高共享度 elastic region 中缺乏普遍性。[pdf:E22]（PDF 物理页 10，Section 7.2）[pdf:E25]（PDF 物理页 11，Figure 7）

为排除替代解释，应固定算术单元数量、buffer 总容量和目标 clock，只改变 control rewrite；再加入一个 oracle schedule，仅允许最终正确路径的 token 进入共享单元。这样可以区分“硬件本身不够快”与“eager token ordering 造成了自干扰”。

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty：Branch-Provenance Control Plane（分支谱系控制平面）。** 由于本任务只使用该论文 PDF，下面与“最近工作”的比较仅限论文内部讨论的 ElasticMiter、elastic value prediction 和 SpecHLS。

**新的研究问题。** 能否不用不断新增 topology-specific Rewrite E/F/G/H，而是为 control token 建立一个有限的 branch-provenance/loop-epoch 表示，使编译器能在此前未见的 nested loop、multiple exits、irreducible reconvergence 上直接综合 eager control？论文一方面认为 eager execution 理论上应能遍历整个电路，另一方面承认每个新的 convergent-control case 都需要新的 initial pattern 与 context，rewrite applicability 将成为长期瓶颈。[pdf:E17]（PDF 物理页 8，Figure 5 与 Section 4.5）

**它首次使什么成为可能。** 目标能力不是“多加几个 rewrite”，而是让一个固定 primitive set 处理开放式 control-flow family：同一套 control semantics 可自动跨越任意数量的 branch reconvergence 与 loop back-edge，并把“选择 B 还是 C、每个 loop 的 `n`、不同 path 的服务顺序”统一成一个全局 synthesis object。Rewrite D 的无限可重复性表明 loop epoch 本身具有可代数化的时间结构，而 B/C 在相同拓扑上产生不同性能则说明 path ordering 是必须显式表示的设计变量。[pdf:E14]（PDF 物理页 7，Figure 4）[pdf:E15]（PDF 物理页 7，Section 4.3）

**核心机制与因果链。**

1. fork 不只复制 Boolean predicate，而是在 control token 上附加紧凑的 lineage state：branch symbol、taken-side 占位和 loop epoch；data payload 保持不带 speculation tag。
2. mux 不再依赖每一种 topology 的手写 alternating-token 小电路，而是根据 lineage compatibility 接纳可并行或可顺序化的 token；condition 到达时，suppressor/commit boundary 对 lineage 做 resolve 与 cancel。
3. loop back-edge 对 epoch 做有限状态更新，由此统一表达 Rewrite D 的多次 re-entry；path-service order 与 buffer allocation 联合综合，而不是先最大化 eager 再补 buffer。
4. 对 lineage automaton 做 finite quotient，再用 symbolic equivalence 检查 quotient 前后的 token traces；若 quotient 可控，就能把“无穷多执行前缀”压缩成有限 control state。

这条因果链改变了至少三个基本设计变量：**状态表示**从无 tag 的局部 token 计数变为 control-only provenance；**系统边界**从 pattern-by-pattern rewrite 扩大为全 control graph synthesis；**评价对象**从单个 `n` 或单个 rewrite 的 QoR 变为 unseen topology 上的可生成性、trace equivalence 与全局 throughput。论文的实验依据是：buffering 而非 rewrite logic 主导 area，[pdf:E24]（PDF 物理页 11，Figure 6）`n` 存在清晰但会饱和的性能—资源曲线，[pdf:E25]（PDF 物理页 11，Figure 7）并且 Custom Rewrite C 在 Unbalanced if 上优于默认 B，说明 control ordering 的选择确实有可观收益。[pdf:E23]（PDF 物理页 11，Table 3）

**最大收益与最大风险。** 最大收益是把 EagerlyElastic 从开放式 rewrite library 推进到对新 control-flow topology 的 push-button eager synthesis，并可能在共享 datapath 上比“最大化 eager extent”更有效。最大科学风险是 control tag 与新 mux logic 重现 value prediction 被论文批评的问题：custom units、state growth、buffering incompatibility 和 clock-frequency degradation；嵌套 branch 的 lineage state 还可能指数爆炸。[pdf:E10]（PDF 物理页 5，Section 3.3）

**首个能区分机制与最强替代解释的实验。** 自动生成一组训练/开发阶段从未出现的 CFG family：两层以上 nested loop、multiple exits、if-under-if、交叉 reconvergence，并固定一套 lineage primitives，不允许为测试 topology 新增 pattern。与两条 baseline 比较：一条是当前 A–H sequence，另一条是“继续扩充手写 rewrite library”。若固定 primitives 能对 unseen CFG 全部生成电路、通过 trace equivalence，并在相同 buffer/clock 约束下接近或超过手写 rewrites，才说明 provenance representation 提供了真正的新能力；若每遇到新 topology 仍需修改状态机结构，它只是把 rewrite library 隐藏进了更昂贵的编码。

**与论文中最近工作的实质区别。** EagerlyElastic 使用 untagged token 与 topology-specific local rewrites；既有 elastic value prediction 给 data token 加 speculation tag，并依赖 predicted value、state saving 与 rollback；本候选只编码精确的 control lineage，不预测数值、不回滚 data computation，研究对象是 arbitrary reconvergence 的 eager routing，而不是 prediction accuracy。[pdf:E10]（PDF 物理页 5，Section 3.3）这一差异有机制基础，但在未检索更多全文前不应宣称具有 novelty。

**Wild-card alternative：** 对每个 strongly connected component 做周期展开，联合综合 multi-loop modulo eager schedule、buffer placement 与 shared-unit reservation，把标量 `n` 改成跨多个 loop 的 phase-offset 向量；该方向不使用 provenance tag，而是改变时间模型和硬件映射对象。
