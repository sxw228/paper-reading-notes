# ProGraML: A Graph-based Program Representation for Data Flow Analysis and Compiler Optimizations

- 作者：Chris Cummins、Zacharias V. Fisches、Tal Ben-Nun、Torsten Hoefler、Michael O’Boyle、Hugh Leather
- 出处：Proceedings of the 38th International Conference on Machine Learning，PMLR 139
- 年份：2021
- DOI：未报告
- Zotero key：BI74IUG2
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。源 PDF 共 10 个物理页；正文引用了 Appendix A-D 和 supplementary materials，但该文件没有收录这些附录页，因此附录中的训练与数据细节保持未报告。

## § 1 — 研究问题与重要性

论文追问的不是「机器学习能不能直接猜出一个编译优化决策」，而是更基础的问题：学习模型是否具备沿程序控制流和数据流传播信息的能力。作者把传统 data flow analysis 改写为节点级监督学习任务，并提出 ProGraML，希望让模型从 compiler IR 的结构中学习类似 transfer function 和 meet operator 的推理。摘要和 Figure 1 将这条路线概括为「输入程序 → IR → ProGraML graph → Message Passing Neural Network → optimization pass」[pdf:E01]（PDF 物理页 1，Abstract、Figure 1）。

这个问题重要，因为 reachability、dominance、data dependency、liveness 和 subexpression 等分析支撑 dead-code elimination、global code motion、instruction scheduling、register allocation 和 common-subexpression elimination。论文的工程判断是：如果模型连这些可由传统算法精确求解的基础传播问题都学不会，那么它对更复杂编译决策的成功很可能只是利用了表面相关性。作者据此贡献了语言无关的图表示、由 461k 个真实程序 IR 构成的 DeepDataFlow benchmark，以及面向下游优化任务的验证；论文还报告整个数据集包含 85 亿个节点分类标签，并在有界问题上获得高 F1 [pdf:E02]（PDF 物理页 2，Introduction 的 contributions）。

## § 2 — 前人工作与不足

论文把既有方法的不足分成「输入表示丢失语义关系」和「模型处理方式不适合程序级传播」两类。

- 手工特征或固定长度向量会被 dead code 等不改变行为、却改变特征计数的变换干扰；这类方法不能自行形成程序的 abstract interpretation [pdf:E01]（PDF 物理页 1，Introduction）。
- source code、token sequence 和 AST 容易把命名与书写风格当成语义。Figure 2a 展示了 code2vec 对同义改名敏感、却把不同算法的相似命名误判为语义相近 [pdf:E03]（PDF 物理页 3，Figure 2a）。
- IR 级方法虽然去掉了源代码噪声，但当时的 XFG 缺少 operand order、变量/常量节点和完整 control-flow；CDFG 只用 opcode 表示 statement，省略 operand、variable、data type 和 constant；IR2Vec 又依赖预先可用的数据流分析结果。Figure 2b-c 和 Section 3 说明这些缺口直接妨碍 non-commutative operation、变量级和跨过程推理 [pdf:E03]（PDF 物理页 3，Figure 2、Related Work、Section 3）。
- 学习 static analysis rule 的方法需要 program generator 或手工 DSL；使用运行时 trace/register snapshot 的方法依赖动态信息；token-level contextual embedding 又不适合 data-flow propagation。论文的目标是仅从静态 IR 构造可供多类分析共用的表示 [pdf:E02]（PDF 物理页 2，Section 2）。

因此，ProGraML 的主张不是「GNN 首次用于代码」，而是把 control、data、call 三类关系、operand position、instruction/variable/constant 和 data type 同时放进一个 IR 级 directed multigraph，再让消息传播直接沿这些关系工作。

## § 3 — 重建作者的思考路径

以下是基于论文背景与失败模式重建的思考路径，不是作者逐字陈述。

第一步，编译优化依赖 data flow analysis，而传统分析的共同形式是：信息沿图传播，局部 transfer function 改写状态，多个路径在 meet operator 汇合，直到 fixed point。第二步，如果学习系统缺少控制、数据、调用关系或 operand order，再强的分类器也没有足够的结构去模拟这种传播。第三步，与其直接比较下游优化准确率，不如先把五种已有精确算法的数据流分析变成节点级 benchmark，以判断表示是否真的支持程序推理 [pdf:E02]（PDF 物理页 2，Introduction 与 contributions）。第四步，compiler IR 本来就是结构化程序语义的载体，所以把 statement、variable、constant 作为节点，把 control/data/call 和 position 作为边，便可将传统 fixed-point iteration 映射为 learnable message passing。最后，再把通过基础分析测试的表示用于 heterogeneous device mapping 和 algorithm classification，验证这种结构是否能迁移到传统规则不能直接解出的任务。

这条路径的重要转折是：作者先把「程序表示是否足够」变成可测问题，再提出表示；不是先选 GNN，之后再寻找适合它的 compiler task。

## § 4 — 核心 Intuition

ProGraML 的核心 intuition 是：程序语义不是一串 token 的统计模式，而是 instruction、variable 和 constant 沿 control、data、call 关系相互约束的图。只要 graph 明确保留这些关系及 operand position，消息传播就可以像传统 data flow engine 一样，把局部状态逐步传到整个程序。Figure 3 的 Fibonacci 示例显示，同一份 LLVM-IR 依次增加 control-flow、use/def data-flow 和 call/return edges 后，才成为可跨函数传播的完整表示 [pdf:E04]（PDF 物理页 4，Figure 3）。

## § 5 — 具体方法与完整 Pipeline

以 Figure 3 的递归 Fibonacci 程序为例，完整 pipeline 如下。

1. **从 compiler IR 建图。** 前端先把源程序变成 LLVM-IR。ProGraML 构造 directed multigraph `G = (V, E)`，把每条 instruction 建成节点，并按 successor 顺序添加带 position 的 control-flow edge。随后把 variable 和 constant 建成节点，用有方向的 use/def edge 连接 operand、instruction 与结果；operand position 保留 `a - b` 与 `b - a` 的差异。最后，从 call site 连到 callee entry，再从每个 function exit 连回 call site；外部函数由专用 dummy vertex 表示。三类边可在一次 `O(|V| + |E|)` 遍历中构造 [pdf:E04]（PDF 物理页 4，Figure 3、Section 3）。
2. **形成跨过程语义上下文。** control edges 不跨函数，但 call/return edges 把调用者和被调用者连接起来；global constant 的 data edge 也可跨 function boundary。作者因此把 inter-procedural relation 显式交给图，而不是要求模型从 token 邻近关系猜测 [pdf:E05]（PDF 物理页 4，Call Flow、Section 4 开头）。
3. **编码节点。** 每个 instruction、constant 和 variable 节点通过可学习词表映射到初始向量 `h_v^0`。LLVM-IR 的 key 使用 instruction name 或 data type；训练中没见过的 key 映射到 unknown embedding。作者承认 composite type 使词表理论上无界，因此在语义分辨率和训练集覆盖率之间作取舍 [pdf:E06]（PDF 物理页 5，Input Encoding）。
4. **传播与更新。** 每一轮先按 edge type 和 edge position 生成 message，再对邻居 message 求均值，用 GRU 更新节点状态。每条正向边另加一种 backward edge type，以支持 liveness 等 backward analysis。该过程固定重复 `T` 轮 [pdf:E06]（PDF 物理页 5，Message Propagation）。
5. **节点级 readout。** readout head 同时读取最终状态 `h_v^T` 和初始状态 `h_v^0`，输出每个 instruction 或 variable 属于分析结果集的概率；初始状态在 gating function 中形成 skip connection [pdf:E07]（PDF 物理页 5，Result Readout）。

实验中的两个 graph model 都使用 32 维 embedding；ProGraML 在训练时固定 `T = 30`，并通过 vertex selector 指定每个分析的起始节点 [pdf:E08]（PDF 物理页 6，Graph Models 与 DDF-30 setup）。

这不是 EMT solver，也没有开关事件、数值时间推进、多速率离散、定点位宽、FPGA 映射、通信拓扑、资源占用或实时步长。源 PDF 也没有报告执行平台和训练耗时；这些内容不能从该论文外推。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有定理证明，核心数学是把 GGNN message passing 写成传统 data flow iteration 的可学习近似。

**初始状态。** 对每个节点 `v ∈ V`，词表查找给出：

$$
f: v \mapsto h_v^0, \qquad h_v^0 \in \mathbb{R}^d.
$$

直觉上，`h_v^0` 只描述节点自身是什么 instruction 或 data type，还没有包含邻域信息 [pdf:E06]（PDF 物理页 5，Input Encoding）。

**边相关消息。** 从邻居 `w` 传向 `v` 的消息为：

$$
M(h_w^{t-1}, e_{wv})
= W_{\mathrm{type}(e_{wv})}
\left(h_w^{t-1} \odot p(e_{wv})\right)
+ b_{\mathrm{type}(e_{wv})}.
$$

其中 `W`、`b` 随 control/data/call 及其反向 edge type 改变；`\odot` 是逐元素乘法。position gate 为：

$$
p(e_{wv}) = 2\sigma\!\left(W_p\,\mathrm{emb}(e_{wv}) + b_p\right).
$$

`emb(e)` 是固定 sinusoidal position embedding。这个 gate 让同一 edge type 的不同 operand position 产生不同传递效果，而不必为每个位置学习独立矩阵；这是 Figure 2c 中区分 non-commutative operation 所需的信息。邻居消息取均值后交给 GRU，反复 `T` 次，得到带 `T` 跳上下文的 `h_v^T` [pdf:E06]（PDF 物理页 5，Message Propagation）。

**读出。** 每个节点的二分类概率为：

$$
R_v(h_v^T,h_v^0)
= \sigma\!\left(f(h_v^T,h_v^0)\right)\cdot g(h_v^T),
$$

其中 `f(·)` 和 `g(·)` 是 linear layer，sigmoid gate 同时查看初始和最终状态。工程直觉是：传播后的上下文决定分析结论，但原始 opcode/type 仍可直接影响是否读出该结论 [pdf:E07]（PDF 物理页 5，Result Readout）。

这里有一个没有写进公式却决定结果的边界：传统 data flow analysis 运行到 fixed point，ProGraML 却只运行固定 `T` 轮。只要依赖路径长于 `T`，或持续传播导致隐藏状态失稳，方程形式本身不能保证得到正确 fixed point。

## § 7 — 实验设计与结论

**问题 1：表示能否覆盖未见程序的节点词汇？ → 实验：** 比较 inst2vec、CDFG 和 ProGraML 在测试图上的 vocabulary coverage。**答案：** ProGraML 的词表大小为 2,230，覆盖 98.3% 测试节点；inst2vec 为 8,565/34.0%，CDFG 为 75/47.5%。更小的结构化词表反而覆盖更多未见节点 [pdf:E09]（PDF 物理页 7，Table 1）。

**问题 2：在传播深度受控时，表示能否学习五种 data flow analysis？ → 实验：** DeepDataFlow 从 256M 行 LLVM-IR 生成 15.4M 个分析样本，任务覆盖 reachability、dominance、data dependency、liveness 和 subexpressions；每个样本选一个 root vertex，并为所有节点生成 binary label，按 3:1:1 分割训练、验证和测试。平均图有 581 个节点、1,051 条边；always-true baseline 的 F1 为 0.073 [pdf:E07]（PDF 物理页 5，Section 5.1）[pdf:E08]（PDF 物理页 6，Figure 4）。训练固定 `T = 30`，DDF-30 只保留传统算法在不超过 30 步内可解的图，并与 inst2vec、CDFG 比较。**答案：** ProGraML 在五项 DDF-30 上的 F1 为 0.998、1.000、0.997、0.937、0.996；前两项 CDFG 也接近满分，但 CDFG 和 inst2vec 不能做 variable-level 的 DataDep/Liveness [pdf:E09]（PDF 物理页 7，Table 2）。论文贡献段写「有界问题上所有任务 F1 ≥ 0.939」，但 Table 2 的 DDF-30 Liveness 为 0.937；源 PDF 无法消解这个 0.002 的表述差异。

**问题 3：把推理轮数从 30 加到 60，能否外推到更大图？ → 实验：** DDF-30 排除了 28.7% 的图；作者用同一模型把 inference `T` 增加到 60，在传统分析不超过 60 步的图上测试，此时仍排除 19.6%。**答案：** DDF-60 的五项 F1 为 0.997、0.991、0.993、0.939、0.967，说明在这一有限扩大范围内，近似 fixed-point behavior 可以延伸 [pdf:E10]（PDF 物理页 7，DDF-60）。

**问题 4：固定轮数 MPNN 能否覆盖完整尺度分布？ → 实验：** 对全量 DDF 使用 `T = 200`；其中 9.6% 的图仍需传统算法执行超过 200 步，单图最大需求为 28,727 步。**答案：** 不能。Dominance F1 从 DDF-30 的 1.000 降至 0.123，Liveness 从 0.937 降至 0.625；前者和 Liveness 主要出现 false positive，Reachability/DataDep 则因传播不到远端而掉 recall。作者同时指出，过多迭代也可能让原本正确的图失稳 [pdf:E10]（PDF 物理页 7，DDF scalability）[pdf:E11]（PDF 物理页 8，scalability discussion）。

**问题 5：表示能否改善下游任务？ → 实验：** 在 OpenCL device mapping 上比较 CPU/GPU 选择错误率；在 104 类、约 240k 样本的 algorithm classification 上比较 test error，并移除各类 edge/vocabulary 做 ablation。**答案：** device mapping 的 AMD/NVIDIA error 为 13.4%/20.0%，优于 inst2vec 的 19.7%/21.5%；algorithm classification error 为 3.38%，优于 XFG 的 4.29%。移除 data edges 后 error 升到 7.76%（相对增加 129.6%），是最大 ablation 损失；移除 backward edges 后为 4.16% [pdf:E11]（PDF 物理页 8，Tables 3-4）。论文据此把性能提升主要归因于 data-flow structure，其次是支持 backward analysis 的反向边 [pdf:E12]（PDF 物理页 9，Section 6.2 结尾与 Conclusion）。

不得外推的范围也很明确：五种基础分析本来可由非 ML 算法精确求解；主要结果来自 LLVM-IR，虽声称设计可用于 XLA，但源 PDF 没给出 XLA 实验；附录 A-D、训练实现细节、硬件资源、时序和耗时不在这份源 PDF 中。

## § 8 — Take-aways

**5 句话：**

1. ProGraML 把 instruction、variable、constant 与 control/data/call relation、operand position 一起编码为 compiler-IR multigraph。
2. GGNN 在这个图上反复传播消息，相当于学习传统 data flow analysis 的 transfer 与 meet 操作。
3. 在传播深度受控的 DDF-30 上，五项任务的 F1 都达到 0.937 以上 [pdf:E09]（PDF 物理页 7，Table 2）。
4. 一旦进入全量尺度，固定轮数 MPNN 会因传播不足或迭代失稳而显著退化，这不是一个小的工程尾项。
5. 下游实验和 ablation 表明，显式 data-flow edge 对程序分类与优化决策确有价值，但论文证明的是「表示有效且有界推理可学」，不是「神经网络已经能替代精确 data flow engine」。

**3 句话：**

1. ProGraML 的主要贡献是给学习模型一个接近 compiler analysis 数据结构的 IR graph。
2. 这个表示在有界图和两个下游任务上优于当时的 sequence/graph baseline。
3. 最大未解问题是如何让学习到的传播在任意图规模上高效达到正确 fixed point。

**1 句话：** ProGraML 证明「把程序关系表示对」能显著提升 learned program reasoning，也同时证明固定深度 MPNN 还不是可扩展的数据流分析器。

## § 9 — 最脆弱的假设

最脆弱的假设是：**训练分布内学到的局部 message/update operator，可以通过改变固定传播轮数 `T`，在更大、更深的程序图上继续近似同一个 fixed-point computation。**

这个假设一旦失效，论文最强的系统性 claim 就会从「表示支持程序级 data flow reasoning」收缩为「模型能在路径长度被筛选过的图上拟合节点标签」。论文给出的正面证据是 DDF-30 到 DDF-60 的性能大体保持；负面证据却更强：全量 DDF 中，部分图需要远超 200 步，Dominance 和 Liveness 的 F1 大幅下降，而且作者观察到传播太少与传播太多会导致不同方向的错误 [pdf:E10]（PDF 物理页 7，DDF-60/DDF）[pdf:E11]（PDF 物理页 8，scalability discussion）。

实际程序中，这个假设可能因长控制依赖链、递归/调用深度、循环结构、跨函数数据依赖和语义等价但图直径不同的 IR 变换失效。论文没有给出跨 compiler、跨 optimization level、跨语言或超大真实程序的系统压力测试；XLA 也只出现在表示实现声明中，没有实验闭环。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重跑 15.4M 个样本，而是验证「ProGraML 在有界图上学习传播、到长路径图上失效」这一双重 claim。

- **数据：** 从 DeepDataFlow 选 Reachability 和 Liveness 各一个小子集。按传统 solver 的迭代步数分为 `≤30`、`31-60`、`>60` 三组，并保留 node-level ground truth。
- **实现：** 使用同一套 32 维 embedding 和 GGNN 容量，分别输入 ProGraML graph 与 CDFG；训练仅使用 `≤30` 组，固定 `T = 30`。推理时分别用 `T = 30/60/200`。
- **测量：** 每组报告 precision、recall、F1，并按传统 solver 步数和 graph diameter 作曲线；同时记录每图 message update 数量，避免只看分类准确率。
- **支持条件：** ProGraML 在 `≤30` 上明显优于 CDFG，特别是 variable-level Liveness；把 `T` 增至 60 后，`31-60` 组性能恢复，但 `>60` 组出现与论文相同方向的 recall/precision 退化。
- **反驳条件：** CDFG 与 ProGraML 没有稳定差距，或 ProGraML 的结果与依赖长度无关、无法复现全量尺度退化。前者反驳表示贡献，后者反驳作者对固定轮数 MPNN 失效机制的解释。

这项实验直接复用论文的任务定义和限制条件 [pdf:E08]（PDF 物理页 6，model setup）[pdf:E09]（PDF 物理页 7，Table 2），但不依赖源 PDF 未收录的附录超参数。

## § 11 — 最强反例设计

最强反例是一组**语义保持、图直径可控增长的程序对**。从一个短函数开始，系统插入不会改变输出的 basic-block chain、等价 copy/phi chain、dead branch 和跨函数 wrapper，使传统 data flow solver 的最终 Reachability/Liveness 标签保持可预测，却把相关节点之间的最短传播距离从小于 30 增加到 60、200、500 以上。每个变体再用不同 optimization level 编译，避免攻击只依赖某一种手写 IR 形状。

攻击成立的判据不是「大图平均更难」，而是：在语义与 ground truth 保持不变时，ProGraML 的错误率随纯粹的传播距离单调增加；同一图在较小 `T` 下漏传、在较大 `T` 下又出现过传播 false positive。这样可以排除「长程序只是词汇更陌生」这一替代解释，直接把失败定位到 fixed-depth message passing。论文自己用 dead code 说明表面特征不应改变语义 [pdf:E01]（PDF 物理页 1，Introduction），而全量 DDF 已显示远距离漏传和过度迭代失稳 [pdf:E10]（PDF 物理页 7，DDF）[pdf:E11]（PDF 物理页 8，scalability discussion），所以这个反例是对核心机制的定向攻击，而不是泛泛的 OOD 测试。

若模型在这些语义保持变换下仍稳定正确，作者关于图关系比 token/feature 更接近语义的主张会得到更强支持；若失败，则 ProGraML graph 本身仍可能有价值，但「沿图学习 data flow」不能被视为 transformation-invariant program reasoning。

## § 12 — Follow-up Research Bet

**主 idea：从表示程序转向生成分析器——任务条件化的可执行数据流代数。**

新的研究问题是：给定一个新 data flow analysis 的声明式语义（状态域、局部 transfer、路径汇合规则和少量输入输出例子），能否让一个系统在不为该任务重新训练整套 GNN 的情况下，直接生成可执行的图上传播程序？它首次要实现的能力不是「同一个分析在更大图上更稳」，而是**对训练期间从未出现的分析任务进行组合式求解**。

核心因果链为：ProGraML 已把 instruction/variable/constant、control/data/call 和 operand position 显式化 [pdf:E04]（PDF 物理页 4，Figure 3）；任务描述再把每个节点的隐藏向量替换为具名的、任务相关状态对象，并生成局部 state transition 与 path-composition operator；这些 operator 沿图执行，形成一个针对该任务的新 analyzer；最终 readout 不再只是固定模型的 binary head，而是分析状态本身的解释。论文的 message equation 已证明 edge type 与 position 可以参数化局部传播 [pdf:E06]（PDF 物理页 5，Message Propagation），但原实验仍为每个任务训练一个模型 [pdf:E08]（PDF 物理页 6，model setup）。因此，这个方向同时改变了研究目标（从拟合五个固定任务到组合新任务）、状态表示（从无结构 latent vector 到任务相关代数对象）、可控变量（分析语义本身）和评价对象（held-out analysis，而非 held-out program）。

论文特异的实验依据是：五类分析共同使用同一图表示，说明 representation 具有跨任务共享性；data-edge ablation 将 algorithm-classification error 从 3.38% 推到 7.76%，说明显式关系不是可有可无的输入装饰 [pdf:E11]（PDF 物理页 8，Table 4）。同时，完整 DDF 的退化说明仅把固定 GGNN 运行更多轮不能得到通用 analyzer。这使「生成局部运算规则」比「继续扩大 `T`」更值得下注。

最大研究收益是把 learned compiler model 从「每个 task 一个预测器」推进为「从分析语义生成执行过程」，从而能测试 zero-shot reaching definitions、constant propagation 或 taint-style propagation。最大科学风险是：精确 compiler analysis 依赖离散、可组合的状态变换，神经模型可能只学到训练任务的表面模板，无法生成真正新颖且可执行的 operator。

首个区分性实验应把一种分析完整留出，例如训练时只见 Reachability、Dominance、DataDep、Liveness 和 Subexpressions，测试时仅给 held-out reaching-definitions 的状态域/少量例子。比较三种系统：原 ProGraML 从头训练、同参数量的 task-conditioned predictor、生成并执行局部 operator 的系统。若第三种在不更新主体参数时能解 held-out analysis，而增加参数量或预训练数据的 predictor 不能，就支持「可执行数据流代数」这一机制；若所有收益都来自更大模型或相似任务标签迁移，主 idea 被反驳。

与源 PDF 内最近工作相比，这个 bet 也改变了问题边界：ProGraML 是固定任务的 label learning；Bielik et al. 的 static analyzer synthesis 依赖 AST、program generator 和手工 DSL；这里把 typed IR multigraph 作为执行对象，把新分析的代数语义作为条件输入。由于本次没有联网补充 2021 年后的相关工作，这只是候选判断，不声称 novelty。

**Wild-card alternative：** 构造由 semantics-preserving compiler transformation 自动生成的 counterfactual graph-pair corpus，把「不同 IR 图是否代表同一优化响应」作为新评价对象，学习跨 optimization level 的程序等价类，而不是节点级 data flow label；这条路线改变的是数据生成方式与研究对象，机制不同于任务条件化 analyzer synthesis。
