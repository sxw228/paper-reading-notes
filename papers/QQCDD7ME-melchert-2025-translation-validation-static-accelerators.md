# Automated Translation Validation of a Compiler for Statically Scheduled Accelerators

作者：Jackson Melchert；Caleb Terrill；Aron Ricardo Perez-Lopez；Clark Barrett；Priyanka Raina  
出处：Formal Methods in Computer-Aided Design 2025（FMCAD 2025）  
年份：2025  
DOI：10.34727/2025/isbn.978-3-85448-084-6_26  
Zotero key：QQCDD7ME  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是“某个 accelerator 算得快不快”，而是一个更基础的可信性问题：一段应用从 Halide 等高层描述出发，经过 compute mapping、memory mapping、place and route、pipelining 和 bitstream generation，最终落到已存在的可编程 accelerator 硬件上时，怎样自动证明每一次 lowering 都没有改变程序含义。传统办法把 CPU 的 golden output 与 RTL simulation 的 accelerator output 对比；它只能覆盖被测试输入走到的行为，而且一旦最终输出错了，还要穿过多级 compiler stage 才能定位根因。论文因此把目标设为逐阶段的 translation validation：不预先证明 compiler pass 永远正确，而是证明这一次具体编译的 pass 输入与输出等价。[pdf:E01]（PDF 物理页 1，Abstract、Introduction 与 contributions）

论文直接声称，其案例首次把 translation validation 用到同时包含软件 IR 与硬件 RTL 的复杂 accelerator application compiler，并让同一套验证框架同时覆盖 compiler 结果和配置后的 hardware。实际价值有两层：第一，若某一级产生不等价结果，counterexample 可把 bug 定位到该级；第二，验证对象不止是 compiler IR，还一直延伸到 bitstream-configured CGRA，因此不会在“compiler 输出正确、硬件解释错误”之间留下未经检查的断层。[pdf:E01]（PDF 物理页 1，Introduction）

## § 2 — 前人工作与不足

**相关文献中的已有结论。** Translation validation 已用于 software compiler，例如优化 compiler 与 Halide；也用于 hardware optimization pass，以及把 C 生成 Verilog 的 HLS。硬件/软件 co-verification 也能比较映射前后的功能，但论文指出其代表方案使用的是 simulation，并不提供形式保证；ILA 则着重证明 instruction-level specification 与 hardware implementation 一致，而不是逐个验证 application compiler stage。[pdf:E02]（PDF 物理页 2，Section II）

这些能力不能直接搬到本文问题上，原因不是笼统的“之前没有考虑 accelerator”，而是验证关系本身不同。HLS 把 C 变成新生成的 Verilog，本文的 application compiler 却把应用编译到既有 hardware；translation validation 又要求 pass 两侧进入同一 semantic framework，所以每一种本项目特有的 IR 都必须有可靠的 symbolic translation。更关键的是，本文中间表示主要是 dataflow graph，且同一值会因静态调度、memory、PE register 与 routing register 在不同 cycle 出现；以 control-flow graph 或别的自定义 IR 为对象的 equality definition 不能直接处理这种“功能相同但时序错位”的等价。[pdf:E02]（PDF 物理页 2，Section II 与 III-A）

## § 3 — 重建作者的思考路径

以下是**基于论文背景证据的重建**，不是作者逐字给出的发现史。

第一步，一个认真排查此类 compiler 的人会发现，仅在最终 RTL simulation 比较输出，把所有 compiler pass 压成了一个黑箱；若中间某级先引入错误、后级又掩盖它，end-to-end test 甚至可能看不到。既有 translation validation 提供了一个更合适的单位：比较每一次实际 pass 的输入与输出，而不是证明整个 compiler 的所有未来运行。[pdf:E02]（PDF 物理页 2，Section II）

第二步，逐级比较的障碍是表示异构：front end 有 loop nests 和 arithmetic dataflow，映射后出现 PE/MEM，PnR 后增加 SB、CB、RMUX、REG，最后变成配置后的 RTL。作者据此把“统一表示”作为先决条件，并选择 bit-vector SMT 与 symbolic transition system（STS），因为 arithmetic、state、memory 和 RTL transition 都能落到同一逻辑语言中；图 2 也把五个 compiler boundary 与相应验证检查一一对应起来。[pdf:E03]（PDF 物理页 3，Fig. 2、Section III-B 与 IV）

第三步，即便两侧都成了 SMT，直接比较同一 cycle 的 output 仍会误报：静态 accelerator 的 pipeline 与 memory 让相同结果在不同 cycle 出现。这里真正可利用的线索是 compiler 已经掌握 schedule、unrolling factor 和 latency offset；既然这些量决定了数据何时进入和离开，那么它们也可以自动生成输入约束和跨 cycle 的 output relation。最后，完整 frame 从 reset 展开需要数千 cycle，促使作者把“从任意执行点开始”变成 symbolic starting state，再用 compiler-derived schedule 恢复合法状态约束。[pdf:E05]（PDF 物理页 5，Section V-B 至 V-E）[pdf:E06]（PDF 物理页 6，Section VI）

## § 4 — 核心 Intuition

核心 intuition 是：不要把 compiler 和 accelerator 当成两个只能靠 sample 对拍的黑箱，而要把每个中间 stage 和最终 RTL 都翻译成同一种 SMT transition semantics，然后逐 stage 查找“不等价的输入”。静态 schedule 不是验证的麻烦，而是一个精确的时间坐标系：它告诉 validator 哪个 stream element 应在什么 cycle 与 untimed array element 对齐。symbolic starting state 再把“必须从 reset 展开完整应用”改成“从任意合法时刻检查一小段”，从而让长时序验证可并行化。[pdf:E01]（PDF 物理页 1，contributions）[pdf:E06]（PDF 物理页 6，Section VI）

## § 5 — 具体方法与完整 Pipeline

以 appendix 中最简单的 `conv1_2` 为具体例子，输入是三个 16-bit 数据项，compute kernel 表达式为 `(e3 + 5·e2) + 3·e1`。论文展示的各级 symbolic representation 从 compute kernel 的几行增长到 loop-nest 的 61 行、fully-mapped graph 的 1284 行，而最终 CGRA Verilog 对应表示达到 4598 行；这说明 pipeline 的难点不只是写一个算术等式，而是保持同一计算在逐渐增加的 state、routing 和 RTL 细节中仍可比较。[pdf:E09]（PDF 物理页 10，Appendix A-D）[pdf:E10]（PDF 物理页 11，Appendix E-F）

完整 pipeline 如下：

1. **Application specification → SMT。** Halide-to-Hardware compiler 产生 compute kernels 与 loop nests。CoreIR arithmetic node 的语义本来就以 SMT-LIB 为基础，因此 validator 遍历 dataflow graph，把 node 变成 SMT term、把 edge 变成 equality；loop nests 则通过新增 Halide code-generation target 生成调用 Pono API 的 Python formal representation。[pdf:E03]（PDF 物理页 3，Section IV-A）
2. **Compute mapping → PE STS。** Compute mapper 用配置好的 PE 替换 CoreIR operation。PE 由 PEak 描述，PEak 能直接给出 SMT-based STS；若 PE 内有 register，就在 STS 中加入 state variable。[pdf:E03]（PDF 物理页 3，Section IV-B）
3. **Memory mapping → PE/MEM STS。** Lake 描述的 streaming memory 没有直接 SMT 后端，因此先生成 Verilog，再由 Yosys 转成 STS；validator 按拓扑顺序把 PEak 与 Yosys 产生的 node semantics 代入 fully-mapped dataflow graph。[pdf:E04]（PDF 物理页 4，Section IV-C）
4. **PnR 与 pipelining → 带时延的 graph STS。** SB、CB、RMUX 在配置后本质上是选定的 wire，可写成端点 equality；REG 则把输入延迟一个 cycle。PnR graph 与 pipelined placement 都沿用 graph traversal 的 symbolic translation。[pdf:E04]（PDF 物理页 4，Section IV-D）
5. **Bitstream → configured RTL STS。** 未配置 CGRA interconnect 可能含 combinational loop，Yosys 无法直接转换。流程先 flatten/simplify RTL，再依据 bitstream 的 address-data pair 把 configuration register 替成 constant，重新进入 Yosys 做 constant propagation 与简化，最后输出 SMT-based STS。[pdf:E04]（PDF 物理页 4，Section IV-E）
6. **逐 stage 建立验证对。** 五个检查依次是 compute graph ↔ PE graph、loop nests ↔ PE/MEM graph、PE/MEM graph ↔ PnR result、PnR result ↔ pipelined PnR result、pipelined PnR result ↔ bitstream-configured CGRA。每次只跨一个 compiler boundary，因而 satisfiable 的 mismatch query 同时给出 bug 存在性与 stage localization。[pdf:E03]（PDF 物理页 3，Fig. 2）[pdf:E04]（PDF 物理页 4，Section V）
7. **用 schedule 对齐 untimed array 与 timed stream。** Memory-mapping check 按 Halide schedule 指定的发送顺序 flatten 多维 input array，并在 STS 内建立以 cycle 为 index 的 LUT；有 input/output unrolling 时，cycle `c` 同时对应 `u` 个输入和 `v` 个输出。valid output 在 `c+l` 出现，其中 `l` 来自 compiler scheduling；PnR、pipelining 与 bitstream checks 也用各 stage 的已知 offset 对齐。[pdf:E05]（PDF 物理页 5，Section V-B 至 V-E）
8. **从 symbolic starting state 分段验证。** validator 不把所有 register 任意化后就直接求解，而是让所有 memory-tile cycle counter 从同一个 symbolic value 开始，并依据该时刻的 static schedule 自动约束 address、schedule 和 dimension counter。这样排除 unreachable state，同时允许多个 BMC instance 从不同执行位置并行开始。[pdf:E06]（PDF 物理页 6，Section VI）

这个流程的输出不是一个新的 bitstream，而是一组逐 stage 的 SMT satisfiability 结果：找不到 mismatch 时支持本次 translation 等价；找到 mismatch 时返回 counterexample，并把问题限定在对应 pass。这里“支持”而非“无条件证明整个 toolchain 正确”，因为 trusted base 与 BMC bound 仍有明确前提。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的统一数学对象是 symbolic transition system：`S = ⟨X, I, T⟩`，其中 `X` 是有限 state-variable 集合，`I(X)` 描述 initial states，`T(X, X′)` 描述一步 transition；`X@n` 表示第 `n` 次展开的同构变量。对 bound `k` 的 invariant `P`，bounded model checking 查询为

`I(X@0) ∧ (∧_{i=0}^{k-1} T(X@i, X@(i+1))) ∧ ¬P(X@k)`。

若该式 satisfiable，solver 给出的 assignment 就是一条长度为 `k`、到达 violation 的 trace。[pdf:E03]（PDF 物理页 3，Section III-B，BMC formula）工程上，这个形式把“跑 k 个 clock cycle”变成把 transition relation 复制 k 次；本文主要使用 bit-vector theory，因此 16-bit arithmetic、counter、register 与 mux 都保持硬件位宽语义。

**Compute mapping relation。** 设 compute graph 的 input/output 为 `I_c`、`O_c`，mapped PE graph 的对应端口为 `i_m`、`o_m`。每次 unroll 加输入约束 `∀i∈I_c, i=i_m`，并搜索 output mismatch `∃o∈O_c, o≠o_m`；mapped graph 若含 pipeline register，bound 由 input 到 output 的 graph latency analysis 决定。[pdf:E04]（PDF 物理页 4，Section V-A）

**Memory mapping relation。** 设 loop nests 的 input/output array 集合为 `I_h`、`O_h`，input/output unrolling factor 分别为 `u`、`v`，当前 cycle 为 `c`。论文写出的 input constraint 是

`∀j∈[0,u), ∀i∈I_h, i[c·u+j] = i^c_{m,j}`，

即第 `c` 个 cycle 的第 `j` 条 stream lane 对应 flattened array 的第 `c·u+j` 项。output mismatch relation 写为

`∀j∈[0,v), ∃o∈O_h, o[c·v+j] ≠ o^{c+l}_{m,j}`，

其中 `l` 是 application scheduling 给出的 output cycle offset。[pdf:E05]（PDF 物理页 5，Section V-B，input constraint 与 output property）直觉上，validator 比较的不是“同一墙钟时刻的两个值”，而是“同一个逻辑 pixel 在两个表示中的位置”。

**PnR、pipelining 与 bitstream relation。** 对 mapped graph input `i` 与 PnR input `i_p`，输入条件为 `∀i∈I_m, i^c=i_p^c`；mismatch 为 `∃o∈O_m, o^c≠o_p^{c+l}`。pipelining 与 bitstream stage 沿用同一结构，只替换两侧变量与 compiler 给出的 latency offset。[pdf:E05]（PDF 物理页 5，Section V-C 至 V-E）

这些公式的有效性有一个明确边界。论文直接承认 trusted base 包括 Halide compiler、Yosys、SMT solver 和各 IR→SMT translation；同时，只有 BMC bound 足够覆盖全部 output，结论才覆盖完整 application execution。[pdf:E05]（PDF 物理页 5，Section V-E 末段）[pdf:E06]（PDF 物理页 6，页首续文）

## § 7 — 实验设计与结论

**问题 1：symbolic starting state 是否是规模化验证的必要条件？** 实验覆盖 20 个 application，其中 12 个 small test、8 个较大 workload；输入 tile 为 `64×64`、每项 16 bit，所有应用映射到 `16×32` tile 的固定 CGRA。求解使用 Pono 与 Boolector，硬件环境为 32 cores、2.5 GHz Intel CPU、252 GB memory。[pdf:E06]（PDF 物理页 6，Table I 与 Section VII）在不使用 symbolic starting state 时，memory mapping、PnR、pipelining 和 bitstream verification 连最简单应用也无法完成，内存超过 252 GB；加入自动 state constraints 并并行分段后，完整 application 可以验证。论文因此给出的答案是：对需要展开数千 cycle 的这些 stage，该优化不是小幅加速，而是可完成性的前提。[pdf:E06]（PDF 物理页 6，Section VII-A）

**问题 2：逐 stage 验证成本落在哪里？** 作者把 runtime 分成原 compiler、symbolic representation construction 和 SMT solving。Compute mapping 只需 1-20 秒；memory mapping 对 small application 增加 1-3 分钟，对 large application 增加 2-375 分钟；PnR verification 约为 small application 1 分钟、large application 1-108 分钟；pipelining verification 分别约 1 分钟与 1-61 分钟；bitstream verification 分别为 8-9 分钟与 9-159 分钟。[pdf:E07]（PDF 物理页 7，Fig. 3-6 与 Section VII-B）结论不是“SMT solving 永远最慢”：memory mapping 的时间性和 memory model 使其难解，而 bitstream stage 主要耗在 Yosys 生成与简化大规模 configured RTL symbolic representation。

**问题 3：能否发现不同 stage 的软件和硬件 bug？** 作者在 `fast corner` 上对五个 stage 分别注入 operator mapping、PE arithmetic、latency、memory schedule、address-counter width、routing register、connection-box routing、pipelining reschedule、bypass register、bitstream bit flip 与 configuration-register width 等不同错误，所有注入错误均被找到。报告时间从 PE hardware bug 的 35 秒到 bitstream flip 的 171 分钟不等。[pdf:E08]（PDF 物理页 8，Section VII-C.1）

**问题 4：是否只会抓人工构造错误？** 论文报告了此前未知的真实问题：16-bit multiply operation 在 specification 中 zero-extend、hardware 中应 sign-extend 的不一致，compute mapping check 用 1.5 分钟发现；ROM mode 下 memory tile 的 write-enable 临时绕法导致的 configuration bug，用 4 分 12 秒发现；此外，较小应用上还在 pipelining rescheduling 中于数秒内发现 5 个 schedule bug。[pdf:E08]（PDF 物理页 8，Section VII-C.2）这支持“逐 stage validator 能发现真实 compiler/hardware mismatch”，但不能外推成对所有 accelerator、所有 IR translation 或全部 bug 类别的完备保证；实验只覆盖这套 CGRA toolchain、给定 20 个 application 与论文明确列出的 trusted assumptions。

## § 8 — Take-aways

**5 句话。** 1. 这项工作把一个多级 accelerator compiler 的 application、IR 和 configured RTL 全部放进统一的 SMT transition semantics。2. 它不是只比较最终输出，而是在五个 compiler boundary 上逐级搜索 mismatch，因此能把 bug 定位到引入它的 stage。3. 静态 schedule 提供了 array element、stream lane 与 cycle offset 的精确对应，是异构表示间 equivalence relation 的关键输入。4. Symbolic starting state 配合自动生成的合法状态约束，把必须从 reset 展开数千 cycle 的单次 BMC 变成可并行的分段验证。5. 20 个 application、跨 stage 的注入 bug 和多个真实 bug 表明方法有工程价值，但 375 分钟级开销与 trusted IR→SMT translation 仍限定了结论范围。[pdf:E01]（PDF 物理页 1，contributions 与 evaluation summary）[pdf:E06]（PDF 物理页 6，Section VI-VII）[pdf:E07]（PDF 物理页 7，runtime）[pdf:E08]（PDF 物理页 8，bug coverage）

**3 句话。** 1. 论文真正的新组合是“全 compiler stage 的统一 formal semantics + schedule-aware equivalence + symbolic starting state”。2. 最重要的实证不是某一个 runtime 数字，而是没有 symbolic starting state 时相关 stage 超过 252 GB、加入后完整 application 可验证，并且能够发现真实软件和硬件问题。3. 这仍是一个特定 CGRA compiler 的 case study，验证结果依赖 symbolic encoding、schedule information、solver 与充分 BMC bound 的正确性。

**1 句话。** 把静态 schedule 当作跨 IR 和 RTL 的时间语义，而不是只当作 compiler metadata，就能把黑箱 simulation 对拍升级为逐 stage、可定位的 formal translation validation。

## § 9 — 最脆弱的假设

最脆弱的假设是：**validator 使用的每个 IR→SMT translation 都忠实表达原对象，而且其依赖的 Halide、Yosys 与 SMT solver 没有产生会改变语义的错误。** 这比“某个 benchmark 是否够大”更致命，因为 translation validation 证明的是 symbolic model 之间的关系；若同一个 encoding 漏掉了 overflow、sign extension、memory update 或 register enable，solver 完全可能严谨地证明两个错误模型等价，而真实 compiler/hardware 仍不等价。

论文为此提供的正面证据是 heterogeneous stage 都有自动 symbolic construction，appendix 展示了从 kernel 到 configured RTL 的 representation excerpt，且人工注入 bug 与若干真实 bug 确实能穿透这些模型被发现。[pdf:E04]（PDF 物理页 4，Section IV-C 至 IV-E）[pdf:E08]（PDF 物理页 8，Section VII-C）但论文自己也把 Halide、Yosys、SMT solver 和 IR translation 正确性列为 assumptions，没有报告独立 semantics oracle、proof-producing translation 或针对这些 encoders 的差分完整性测试。[pdf:E05]（PDF 物理页 5，Section V-E 末段）因此证据说明“这些 encoding 对已测错误有辨别力”，还不能说明 trusted base 已闭合。

## § 10 — 最小复现实验

这是一个**基于论文证据提出的复现实验方案**。一周内不必复现 20 个 application，也不必先处理最慢的 bitstream stage；选择 appendix 已完整说明的 `conv1_2`，保留 compute mapping 与 memory mapping 两个边界即可。该应用的 kernel 只有 `(e3+5·e2)+3·e1`，但 memory-mapped representation 已含 state 与 schedule，刚好同时覆盖 combinational equivalence 和 timed stream equivalence。[pdf:E09]（PDF 物理页 10，Appendix A-D）

具体执行：先对原始 compile run 生成两组 SMT query，记录 clean case 是否 UNSAT、求解时间与最大内存；再做两次单点 mutation。Mutation A 把一个 multiply weight `3` 改成 `5`，测试 compute mapping 是否返回 SAT counterexample；Mutation B 把 memory output offset `l` 改为 `l+1` 或把一个 address counter 提前一 cycle，测试 memory mapping 是否返回 SAT，并核对 counterexample 的第一个 mismatch cycle。数据不需要图像语料库，只需 arbitrary 16-bit symbolic inputs；测量对象是 SAT/UNSAT、stage localization、counterexample cycle、runtime 与 peak memory。

支持核心 claim 的最低结果是：clean case 在预定 bound 内均为 UNSAT，两个 mutation 各自在其引入 stage 首先变为 SAT，且输出的具体 input assignment 经独立 bit-vector evaluator 重放后确有 mismatch。反驳结果包括：clean case 出现无法由真实 execution 重放的 counterexample、mutation 仍为 UNSAT、错误被定位到错误 stage，或不同 schedule offset 让结果只取决于 validator 与 compiler 共享的 metadata 而非真实 stream semantics。最后一种结果会直接指向第 9 节的 trusted-semantics 问题，而不是简单归因于“solver 太慢”。

## § 11 — 最强反例设计

最强反例不是再放大 benchmark，而是制造一个 **compiler 与 validator 共享同一错误 schedule 解释** 的 correlated bug。本文的 memory、PnR 和 pipelining relations 都从 compiler schedule 取得 flatten order、unrolling 和 offset `l`；symbolic starting-state constraint 也用 compiler-derived schedule 决定 counter 在某个 timestep 的合法值。[pdf:E05]（PDF 物理页 5，Section V-B 至 V-D）[pdf:E06]（PDF 物理页 6，Section VI）若一个 schedule bug 同时改变生成的 hardware 行为和 validator 的“正确对齐方式”，两侧可能在同一个错误时间坐标下保持一致，形成 false negative。

实验上，可在 schedule metadata 产生点之前注入一个系统性 permutation：例如对两条 unrolled input lane 交换偶数/奇数 pixel 的逻辑索引，同时让 memory configuration 与 validator LUT 都读取这份被污染 metadata。然后用一个完全独立、直接按原 Halide array semantics 解释的 oracle 逐 cycle 重放 configured RTL。最有力的反例结果是：论文式逐 stage query 全部 UNSAT，但独立 oracle 找到确定 input 使最终 image element 错位；这会说明验证框架证明的是“compiler 与自身 schedule interpretation 自洽”，而不是“相对外部 application semantics 正确”。相反，若某一级仍产生 SAT counterexample，就说明 pipeline 中存在足够独立的语义锚点，能够打破 correlated error。

## § 12 — Follow-up Research Bet

**主 idea：把 fixed-run translation validation 改造成 schedule-parametric CGRA mapping synthesis。** 这不是在原 validator 外加一个检查器，而是把研究问题从“给定 compiler 产生的一个 schedule 是否等价”改为“满足 application semantics 的 schedule、unrolling、pipeline placement 与 tile mapping 的可行集合是什么，以及能否从中直接合成低 latency 或低 resource 的实现”。它首次可能让 formal semantics 本身成为 accelerator compiler 的搜索空间，而不只是编译后的判定器。

核心机制是把现有 relation 中原本由 compiler 常量提供的 `u`、`v`、offset `l`、lane-to-array index、register placement 和 memory-counter phase 提升为 symbolic design variables；application-side array semantics 提供固定锚点，PE/MEM/PnR/RTL 的 STS 提供实现约束，solver model 给出一个可执行 schedule 与 mapping。因果链是：symbolic schedule variables 扩大候选空间 → array/stream equivalence 排除功能错误组合 → transition constraints 排除时序和 state 不可达组合 → objective 在剩余 model 上选择 latency/resource Pareto point。它至少改变了研究目标、可控变量、硬件映射和数据生成方式，而不是只提高原验证流程的鲁棒性。

论文特异依据有两类。方法上，memory relation 已把 array index 写成 `c·u+j`，把 valid output 写成 `c+l`，而 symbolic starting state 已能从 schedule 自动生成 counter invariants，这说明 schedule 不只是注释，而是可进入约束系统的数学对象。[pdf:E05]（PDF 物理页 5，Section V-B）[pdf:E06]（PDF 物理页 6，Section VI）实验上，不同 stage 的求解成本高度不均：compute mapping 为秒级，memory mapping 最坏达 375 分钟，bitstream verification 最坏 159 分钟；因此首个研究版本应在 PE/MEM graph 层合成 schedule，再把少量候选下推，而不是把全 RTL 放进一次 synthesis query。[pdf:E07]（PDF 物理页 7，Fig. 3-6 与 runtime discussion）

成功后的最大收益是把“compiler heuristic 给一个点、formal tool 再判断”改为直接枚举有语义保证的 design region，从而可能发现 heuristic 不会产生的新 pipeline/memory schedule。最大科学风险是 variable schedule 会破坏本文依赖的固定时序结构，使 query 从可分段 BMC 变成难以收敛的 quantified 或 combinatorial synthesis；现有 375 分钟级 fixed-schedule 结果提示这一风险很实在。

首个证伪实验只用 `conv1_2` 与 2-3 个 small test：固定 PE/MEM topology，把 `u`、`v`、`l` 和一个 register placement 设为有限域变量，比较 solver 合成的 schedule 与原 compiler schedule 的 latency/resource Pareto set。用独立 cycle-accurate simulation 重放每个 synthesized model。若 solver 只能重现原 schedule，或出现更优 objective 但无法重放，核心机制分别被“没有新增可行 design freedom”或“symbolic relation 不足以构造实现”反驳；若得到至少一个不同且可重放的 Pareto-improving schedule，则支持该方向。

与本文列出的最近工作相比，这一候选在 **problem** 上从 translation validation 转为 semantics-constrained mapping synthesis，在 **mechanism** 上从代入已知 schedule 转为求解 schedule，在 **representation** 上把 timing metadata 提升为 symbolic variable，在 **experimental object** 上从单次 compiler run 变为 schedule/mapping 可行域。本文未做外部全文检索，因此这只是基于本论文与其 related-work 描述的候选判断，**不声称 novelty 已经闭合**。

**Wild-card alternative：** 构造 phase-quotiented STS，把静态 schedule 的长周期执行压缩为“phase × local state”的周期商系统，直接研究整帧数据流的尺度律，而不是搜索新的 schedule 或继续展开 4096 个 cycle。
