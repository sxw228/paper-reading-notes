# Scaling Program Synthesis Based Technology Mapping with Equality Saturation

- 作者：Gus Henry Smith、Colin Knizek、Daniel Petrisko、Zachary Tatlock、Jonathan Balkind、Gilbert Louis Bernstein、Haobin Ni、Chandrakana Nandi
- 出处：arXiv preprint arXiv:2411.11036v2 [cs.PL]
- 年份：2024
- DOI：未报告
- Zotero key：ARHCXPXV
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是 FPGA technology mapping 中一个很具体、也很顽固的落差：高层设计明明可以落进 DSP 这类复杂可编程原语，Vivado、Yosys 等常规综合器却可能只用到原语的一部分功能，例如把 multiply-add 拆成一个 DSP 加额外逻辑；Lakeroad 用 sketch-guided program synthesis 更彻底地搜索 DSP 配置，但又要求用户手写 sketch，而且底层开源 SMT solver 一遇到宽位乘法就难以扩展。作者把这两个问题合并为一个研究问题：能否让 synthesis 只处理局部、较小的映射任务，同时自动从全局等价表示中产生这些局部任务所需的结构？论文给出的系统是 Churchroad：用 equality saturation（eqsat）维护等价实现，再把 Lakeroad 当作局部高能力 subroutine 调用。[pdf:E01]（PDF 物理页 1，标题、Abstract）

重要性不只是“少写一个 sketch”。复杂 FPGA primitive 的价值来自内部乘法器、加法器、移位器和级联通路的组合使用；若 technology mapper 看不到这种组合结构，设计会损失面积、性能或两者。Churchroad 试图改变工具之间的分工：e-graph 负责暴露全局等价分解和候选映射位置，program synthesis 只负责把一个局部候选落实为具体 primitive 配置。论文直接陈述，这种 divide-and-conquer 能把宽乘法拆开、缩小交给 Lakeroad 的 SMT query，并从 e-graph 内的信息推断输出结构，从而去掉用户 sketch。[pdf:E02]（PDF 物理页 1，Introduction 与 Technical Contribution 开头）

## § 2 — 前人工作与不足

最直接的前人系统有三类。第一类是 Vivado、Yosys、ODIN/ODIN-II 一类基于既定 pattern 或 syntactic matching 的 mapper；它们工程成熟，但面对 DSP48E2 这种参数多、端口组合多的 primitive 时，局部 pattern 未必覆盖最优用法。第二类是 Lakeroad：它把目标 primitive 的参数当作 hole，让 Rosette/SMT 搜索满足语义等价的配置，比纯 pattern matching 更完整；代价是用户必须先给出输出拓扑的 sketch。第三类是针对乘法验证或 SMT bit-blasting 的专门改进，例如改变 multiplier encoding、PolySAT 的 word-level reasoning、算术电路专用验证，以及用 equality saturation 预处理 SMT 的 Haploid。论文列出了这些邻近工作，但没有展示它们已经能自动完成本文的多 DSP 映射任务。[pdf:E10]（PDF 物理页 4，Related Work）

Lakeroad 的不足在这个 running example 上很清楚：输入是无符号 16-bit 的 \(a\) 与 32-bit 的 \(b\)，输出只保留乘积低 32 bit；目标实现需要两个 Xilinx UltraScale+ DSP48E2，其中 DSP0 计算低半部分，DSP1 利用 DSP0 的 partial product 与内部 shift 计算高半部分。[pdf:E03]（PDF 物理页 2，Eq. (1) 与双 DSP 结构图）现有 Lakeroad 不只要用户提前知道这个两-DSP结构，还要一次证明整个宽乘法与该结构等价；也就是说，结构知识和困难的全局 arithmetic proof 被绑在同一个 query 里。[pdf:E04]（PDF 物理页 2，Fig. 1、Eq. (2)–(4)）

技术瓶颈并非一般意义上的“SMT 很慢”。作者把 Eq. (4) 直接写成 Rosette bit-vector query，改变 bitwidth 后观察多种 solver；正文报告，小位宽可以求解，但大约到 12 bit 后，多数 solver 很快撞上 10 s timeout。作者把原因指向 multiplication 经 bit-blasting 展开为低层逻辑后造成的组合复杂度。[pdf:E05]（PDF 物理页 3，Rosette query 与 Fig. 1 结果解释）因此，本文不是另造一个 multiplier solver，而是避免让 solver 看到那个难的整体乘法证明。

## § 3 — 重建作者的思考路径

以下是基于全文证据的逆向重建，不是作者逐字陈述。

第一步，从失败 query 入手。若 Eq. (3) 的整体 sketch query 难在宽乘法，而目标双 DSP 结构本来就是两个较窄的局部关系，那么最直接的研究问题不是“怎样加速同一条 query”，而是“能否把一条全局证明拆成两条局部证明”。作者给出的两个局部 synthesis query 分别对应 \(a\times b_0\) 和带 partial product shift 的 \(a\times b_1\)；具体参数一旦猜定，验证式可退化为几乎同形的恒等式。[pdf:E06]（PDF 物理页 3，query splitting 与 egglog rewrite rule）

第二步，需要一种不会过早丢掉候选结构的数据结构。如果只把 \(a\times b\) 破坏性地 rewrite 成某一种分解，后续很难同时保留原式、分解式以及不同映射结果；e-graph 则把 `Mul` 与分解后的 `Concat/Add/Mul/Shr/Extract` 放进同一 equivalence class，不必立即选边。接着，用 egglog rule 在符合位宽与算子形状的 e-class 中插入 `DSP?` proposal node，表示“这里可能有 DSP 实现”，而不是先断言一定可映射。[pdf:E07]（PDF 物理页 3，e-graph 扩展图与 DSP proposal rules）

第三步，把 proposal 变成可求解任务。一个 e-class 里，原算术 subexpression 可以自动充当 spec，`DSP?` 节点加上参数 hole 后可以自动充当 sketch；这让 Lakeroad 所需的两个用户输入都从 e-graph 中生成。若 Lakeroad 找到具体 DSP48E2 配置，就把该实现重新插回 e-graph，供最终 extraction 使用。[pdf:E08]（PDF 物理页 4，带 DSP? 的 e-graph、自动 spec/sketch 与两条局部 query）

第四步，最后只从每个 e-class 选择 structural Verilog 合法节点，例如 module instance、extension、extract 和 concat，而不选择 behavioral `Mul`；于是两次局部 Lakeroad 结果能重新拼成完整结构网表。论文报告该 example 从头到尾约用 4 s。[pdf:E09]（PDF 物理页 4，extraction 与 runtime）这条路径把“发现分解”“验证 primitive 配置”“选择最终结构”拆成三个角色，正是 Churchroad 的系统结构来源。

## § 4 — 核心 Intuition

不要让 program synthesis 同时猜整个硬件拓扑并证明一个宽算术恒等式。先用 e-graph 保留并扩展许多语义等价的分解，让规则标出可能映射到 DSP 的局部 e-class；再让 Lakeroad 只解决这些小而明确的 primitive configuration 问题，最后从同一 e-graph 抽取能拼回完整设计的结构实现。普通话概括就是：eqsat 负责“把大题拆对并找到可下手的位置”，program synthesis 负责“把每个小题彻底做完”。

## § 5 — 具体方法与完整 Pipeline

以论文的无符号 16×32 乘法、输出低 32 bit 为例，Churchroad 的完整 pipeline 是：

1. **输入 spec。** behavioral Verilog 中只有 `o = a * b`；内部表示把 32-bit 的 \(b\) 视为两个 16-bit 半字 \(b_1\) 和 \(b_0\)。论文没有报告一般 HDL frontend 覆盖范围。
2. **建立并扩展 e-graph。** Churchroad 把原始 `Mul` 放入 e-graph，并用预先编码的等式把它与由 `Concat`、`Extract`、`Add`、`Mul`、`Shr` 组成的两部分乘法分解 union 到同一 e-class。这里的数值对象是定宽无符号 bit-vector；论文没有讨论 floating-point、signed saturation、时序状态或多周期行为。
3. **产生 primitive proposal。** egglog rule 搜索位宽可装入 DSP48E2 的 `Mul` 或带 shift 输入的 multiply-add。例如一条 rule 要求结果位宽不超过 48、乘法输入不超过 17 bit；命中后插入 `DSP?` 节点。`DSP?` 只是候选，不是已经验证的映射。[pdf:E07]（PDF 物理页 3，DSP proposal rules）
4. **从 e-class 自动构造 synthesis task。** 对含 `DSP?` 的 e-class，算术表达式充当 spec，proposal 加参数 hole 后充当 sketch。对于低半部分，query 形如 \(\exists p.\forall a,b.\ a\times b_0=DSP(p,a,b_0)\)；高半部分则把 \(a\times b_1\) 与移位后的 partial product 一起映射。[pdf:E08]（PDF 物理页 4，局部 Lakeroad queries）
5. **调用 Lakeroad 并回填。** Lakeroad/Rosette 搜索 DSP 参数，再由 SMT solver 验证局部 spec 与具体 DSP 行为等价；成功配置被加入原 e-graph。论文只展示 Lakeroad 作为这一类 specialized subroutine，没有给出失败 proposal 的调度策略或并行执行细节。
6. **结构 extraction。** extractor 在每个 e-class 中选 structural Verilog 合法节点，避开 behavioral `Mul`，输出由两个 DSP48E2、extract、concat 及连线组成的 structural Verilog。[pdf:E09]（PDF 物理页 4，extraction）

从 EMT + FPGA 实现视角看，本文报告了 arithmetic decomposition、bit-vector 表示、DSP48E2 映射和 structural Verilog 输出；没有报告开关/事件处理、时间推进、多速率、fixed-point rounding policy、host CPU、FPGA 板卡实测、resource utilization、Fmax 或硬件在环执行。因此它是一篇 technology mapping 方法短文，不应外推为实时仿真或端到端 FPGA 性能论文。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有新的定理体系，核心数学是“把宽乘法恒等分解成可分别映射的 bit-vector 子式”，再把语义等价写成带量词的 synthesis query。

先把 \(b\) 拆成高、低两个 16-bit 半字 \(b_1,b_0\)，其中 `++` 表示 concatenation。原 spec 是

\[
\operatorname{SPEC}(a,b):=a\times b=a\times(b_1\mathbin{++}b_0). \tag{1}
\]

目标只取乘积低 32 bit。按十六进制“竖式乘法”的直觉，低 16 bit 由 \(a\times b_0\) 的低半产生，高 16 bit 则来自 \(a\times b_1\) 加上 \(a\times b_0\) 右移 16 bit 后的进位/高半。论文用双 DSP 结构表达这个分解。[pdf:E03]（PDF 物理页 2，Eq. (1) 与双 DSP 图）

用户原本必须给 Lakeroad 一个带 hole 的两-DSP sketch：DSP0 接 \(a,b_0\)，DSP1 接 \(a,b_1\) 和 DSP0 partial product，输出拼接两个 DSP 的低 16 bit。Lakeroad 要搜索 \(p_0,p_1\)，使

\[
\exists p_0,p_1.\ \forall a,b.\ \operatorname{SPEC}(a,b)
=\operatorname{SKETCH}(p_0,p_1,a,b). \tag{3}
\]

对某组参数猜测，验证会展开成

\[
\forall a,b.\ a\times b=
\left(a\times b_1+((a\times b_0)\gg16)\right)^{15}_{0}
\mathbin{++}(a\times b_0)^{15}_{0}. \tag{4}
\]

上标/下标 \((\cdot)^ {15}_{0}\) 表示取低 16 bit，\(\gg16\) 表示右移 16 bit。[pdf:E04]（PDF 物理页 2，Eq. (2)–(4)）整体 Eq. (4) 对 bit-blasting solver 很难；Churchroad 预先把这个恒等式编码成 e-graph rewrite，再分别求解低半 DSP 和高半 multiply-add DSP 的参数。关键并不是近似原式，而是把已知恒等关系变成 e-graph 中并存的表示，从而让局部 query 保持语义目标却降低 SMT arithmetic 复杂度。[pdf:E06]（PDF 物理页 3，拆分 query 与 rewrite）

这里有一个容易忽略的隐藏前提：rewrite 必须在精确的 bitwidth、extract、shift 和 concatenation 语义下成立。整数代数上看似等价的变形，若忽略 bit-vector 截断或 signedness，未必仍等价；论文的 example 明确限定为 unsigned，并通过固定宽度运算表达。

## § 7 — 实验设计与结论

论文的实验规模很小，作者自己也只称其为 early evidence。源 PDF 没有独立 appendix，也没有额外 benchmark table。

**问题 1：整体 synthesis query 是否真的被乘法位宽卡住？ → 实验：**作者在 Rosette 中直接实现 Eq. (4)，调节 `bw`，比较 bitwuzla、z3、cvc5、yices、stp，并把 timeout 设为 10 s。**答案：**正文报告小位宽可以求解，但大约 12 bit 后，多数 solver 突然撞墙；Fig. 1 的趋势支持“宽乘法 bit-blasting 是当前 query 的瓶颈”，但它不是对所有 solver、encoding 或硬件 mapping workload 的普遍尺度律。[pdf:E04]（PDF 物理页 2，Fig. 1 caption 与曲线）[pdf:E05]（PDF 物理页 3，结果解释）

**问题 2：eqsat 拆分后能否完成一个 Lakeroad 单独处理不了的多 DSP 映射？ → 实验：**将 unsigned 16×32 乘法低 32 bit 用等式扩展为两个局部乘法/乘加，自动生成两个 Lakeroad task，再抽取两个 DSP48E2 的 structural Verilog。**答案：**论文报告 Churchroad 成功编译该 example，并把 Lakeroad 产生的两个映射组合起来；完整过程约 4 s。[pdf:E09]（PDF 物理页 4，extraction 与 runtime）论文的总结同样把结果限定为这个 larger design 相对 Lakeroad 的成功案例，而不是广泛 benchmark 胜率。[pdf:E10]（PDF 物理页 4，成功流程总结）

**问题 3：能否去掉用户 sketch？ → 实验：**在含算术节点与 `DSP?` proposal 的 e-class 中，把前者当 spec、后者加 hole 后当 sketch。**答案：**在这个 example 上可以，两条局部 query 都由 Churchroad 生成；但论文没有用户研究、不同 DSP pattern 的覆盖率或 proposal false-positive 数据。

**不能外推的范围。** 没有与 Vivado/Yosys 的 QoR 对照，没有 LUT/DSP/FF 数、Fmax、power、place-and-route 或板上测量，没有大 corpus，也没有 e-graph size/scaling 数据。作者的结论用语是“equational reasoning using e-graphs can help scale”，并把多工具 orchestration 与自动生成正确 rewrite rule 放在 future work，而非已完成结果。[pdf:E11]（PDF 物理页 4，Conclusions and Future Work）

## § 8 — Take-aways

**5 句话：**

1. Lakeroad 的 program synthesis 能深挖 DSP48E2 功能，但用户 sketch 和宽乘法 SMT query 限制了它处理多 DSP 设计。
2. Churchroad 用 e-graph 同时保留原算术表达式与分解后的等价结构，而不是立即选定一种 rewrite 结果。
3. egglog rule 在合适的 e-class 中插入 `DSP?` proposal，e-class 内的算术节点与 proposal 分别自动成为 Lakeroad 的 spec 和 sketch。
4. 论文在一个 unsigned 16×32、输出低 32 bit 的 example 上生成两个 DSP48E2 结构，报告总编译时间约 4 s。
5. 这只是 early evidence；广泛的映射质量、系统 scaling、rewrite 生成和多工具协同仍未验证。

**3 句话：** Churchroad 把 program synthesis 从“全局拓扑猜测器”改成“局部 primitive 配置器”。eqsat 负责暴露等价分解和 proposal，Lakeroad 负责验证并实例化局部 DSP。单例结果有说服力地展示了机制，却不足以证明普遍 QoR 或规模优势。

**1 句话：** 用 e-graph 把大映射问题拆成自动生成的小 synthesis task，是本文真正的贡献。

## § 9 — 最脆弱的假设

最脆弱的假设是：**手工加入 Churchroad 的 rewrite rule 在精确 bit-vector 语义下既正确，又足以把真实设计暴露成可独立映射的局部 primitive 结构。** 这是失败代价最大的假设，因为 rewrite 在 e-graph 中被当作等价关系使用；一个 signedness、截断位、shift 或 carry 处理错误，不只是让搜索变慢，而会让后续自动 spec/sketch 和最终 structural Verilog建立在错误等价类上。另一方面，即使规则都正确，若规则库没有覆盖某个 arithmetic shape，Churchroad 也看不到可用的 `DSP?` 局部任务，核心 divide-and-conquer 就不会启动。

论文给出的支持是 Eq. (4) 这条具体无符号分解以及成功的两-DSP example；它没有报告 rewrite suite 的证明、随机/形式化验证覆盖、signed/overflow 变体或更大 design corpus。作者把“generate correct rewrite rules rather than writing them manually”明确列为 future work，[pdf:E11]（PDF 物理页 4，Future Work）反而说明当前证据尚未闭合这一假设。这里的判断是基于论文证据的批评，不是论文自称已经保证了错误映射。

## § 10 — 最小复现实验

一周内最有价值的复现不是重做整套 FPGA flow，而是复现“拆 query 会改变可解性，并能形成等价的双 DSP structural output”这一核心 claim。

1. 使用论文同一 Verilog：unsigned `a[15:0] * b[31:0]`，输出低 32 bit；固定目标为 UltraScale+ DSP48E2。
2. 先运行论文的 Rosette Eq. (4) microbenchmark，在相同 10 s timeout 下扫一组 `bw`，记录各 solver 的 solve/timeout 与 wall time；这验证困难 query 是否能在本机重现。
3. 分别运行 Lakeroad 的整体两-DSP sketch query与 Churchroad 的两条局部 query，记录 query size、solver time、是否找到 DSP 参数、Churchroad 总时间和最终 DSP instance 数。
4. 对输出 structural Verilog 做 exhaustive small-width 检查或 SMT equivalence check；对 16×32 版本至少做独立 formal equivalence，不能只看综合成功。
5. **支持 claim 的结果：**整体 query 在较宽位宽 timeout 或显著更慢，而两条局部 query均可解，最终网表含两个 DSP48E2、与原 spec 等价，数量级接近论文报告的约 4 s。**反驳 claim 的结果：**整体 query同样稳定可解，或局部 query/抽取不能产生等价网表，或拆分开销吞掉全部收益。

这个实验不会验证 Churchroad 对任意 arithmetic design 的 scaling；它只验证论文唯一完整展示的机制闭环。

## § 11 — 最强反例设计

最有力的攻击是构造一族**局部可识别、但跨分块语义强耦合**的 arithmetic design，检验成功是否只来自 Eq. (4) 这条手工、恰好适配双 DSP 的分解。可从 unsigned baseline 系统地加入 signed extension、round-to-nearest、saturation、跨半字 carry、共享 partial product 和多输出复用，再把位宽从两块扩展到四块或八块；每个 design 都有明确的 DSP/LUT 实现，但局部 subexpression 不再能在不携带全局截断/舍入上下文时独立映射。

比较三条路径：整体 Lakeroad、Churchroad 当前规则、以及人工给出已知可行结构的 oracle sketch。测量 e-graph node/e-class 增长、`DSP?` 数、Lakeroad call 数与 timeout、最终 DSP/LUT QoR、编译时间和 formal equivalence。若 oracle sketch 能稳定找到好实现，而 Churchroad 出现 e-graph explosion、proposal 大量无解或只能抽取差实现，最强替代解释就成立：当前成功主要来自一个人工编码、局部可分的乘法 identity，而不是 eqsat 已经普遍解决了 program-synthesis technology mapping 的 scaling。这个反例直接攻击论文的核心机制边界，不是泛泛要求“多做 benchmark”。

## § 12 — Follow-up Research Bet

**主 idea：用 latency-indexed e-graph 联合发明流水线结构与异构 primitive 映射。** 新研究问题是：能否把 e-class 从“同周期、纯组合语义相等”扩展为“相差 \(\Delta\) 个 cycle 但在时间对齐后等价”，从而让 mapper 在同一个搜索对象里联合选择 arithmetic decomposition、register placement、retiming，以及 DSP/LUT/carry-chain 实现？这首次使 Churchroad 跨越组合子表达式边界，在映射阶段直接发明吞吐率导向的多级 pipeline，而不必先固定 RTL 寄存器边界再逐块 technology map。

核心机制的因果链是：在 e-graph IR 中引入 `Delay(k,x)` 与带 cycle offset 的 equivalence relation → 用合法 retiming 与算术分解规则同时生成跨周期候选 → 让 Lakeroad、ABC/Yosys 类 subroutine 分别把局部候选变成带 latency/resource signature 的实现节点 → 在 extraction 时对齐各路径 cycle，并全局选择 throughput/area Pareto 结构。它改变了至少四个基本设计变量：状态表示从组合 e-class 变成时间索引 e-class，时间尺度从单周期扩展为多周期，可控变量加入 register placement/latency，硬件映射从单一 DSP proposal 扩展为异构 DSP-LUT-carry pipeline；评价对象也从“能否编译一个表达式”变成“能否生成新的吞吐率—面积结构族”。

论文特异依据有三点。方法上，Churchroad 已经让 `Mul` 与 `Concat/Add/Shr/Extract` 在同一 e-graph 中并存，并用 proposal node 把局部算术表达式自动转成 spec/sketch，[pdf:E07]（PDF 物理页 3，e-graph 与 DSP proposal）这说明表示与 specialized solver 之间已有可扩展接缝。实验上，16×32 乘法被拆成两个 DSP48E2 局部任务并约 4 s 完成，[pdf:E03]（PDF 物理页 2，双 DSP 分解）[pdf:E09]（PDF 物理页 4，runtime）说明“全局等价结构 + 局部高能力 mapper”至少闭合过一次。系统方向上，作者明确希望用 e-graph orchestration 接入 Yosys、Lakeroad、ABC，[pdf:E11]（PDF 物理页 4，Future Work）但本文仍只抽取纯 structural combinational Verilog，尚未开发时间维度。

最大研究收益是把 retiming、pipeline synthesis 和 technology mapping 从串行 pass 变成一个共享等价空间，可能发现人工 RTL 边界会遮蔽的 mixed-primitive pipeline。最大的科学风险是 cycle-indexed equivalence 使 e-graph 爆炸，且不同 subroutine 返回的 latency/resource signature 未必能组合成全局可行结构；如果只是工具 portfolio 更多，而不是时间表示本身带来新结构，这个 idea 就失败。

首个区分实验选两个需要跨级对齐的 kernel：一条多 tap FIR/dot-product 和一条宽 MAC reduction。所有条件调用完全相同的 Lakeroad、Yosys/ABC proposal；实验组允许 `Delay`/retiming equivalence，对照组保留普通组合 e-graph并在映射后流水化。比较自动发现的 pipeline 拓扑、initiation interval、Fmax、DSP/LUT/FF、compile time 与 e-graph size；再做一个关键 ablation：保留同样多的 subroutine，却禁用 cycle-offset equivalence。只有实验组在 formal sequential equivalence 成立的前提下产生对照组不存在的吞吐率—面积 Pareto 点，才能把收益归因于新的时间表示，而不是“多叫了几个工具”。

与论文中最近的工作相比，这不是 Lakeroad 的更大 sketch、ODIN 的新 pattern，也不是 Haploid 式 SMT preprocessing：problem 从局部 primitive 配置变成跨周期架构生成，mechanism 从普通 equivalence class 变成 cycle-offset equivalence，representation 显式包含 delay，experimental object 是多级 pipeline 的吞吐率—面积前沿。由于本文没有系统回顾 temporal e-graph、retiming synthesis 或 sequential technology mapping 的最新文献，这一方向只能标为**候选判断，不声称 novelty**。

**Wild-card alternative：**把 `DSP?` proposal 的覆盖空洞与 Rosette solver hardness 当作主动采样信号，生成一套会最大化不同 mapper 行为分歧的 arithmetic circuit benchmark；它改变的是研究任务和数据生成方式，用 adversarial benchmark discovery 检验 mapper 的真实能力边界，而不是扩展映射器本身。
