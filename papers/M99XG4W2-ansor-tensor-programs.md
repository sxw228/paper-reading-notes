# Ansor: Generating High-Performance Tensor Programs for Deep Learning

- 作者：Lianmin Zheng；Chengfan Jia；Minmin Sun；Zhao Wu；Cody Hao Yu；Ameer Haj-Ali；Yida Wang；Jun Yang；Danyang Zhuo；Koushik Sen；Joseph E. Gonzalez；Ion Stoica
- 出处：14th USENIX Symposium on Operating Systems Design and Implementation（OSDI 20），pp. 863–879
- 年份：2020
- DOI：未报告
- Zotero key：M99XG4W2
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。本源 PDF 共 18 个物理页，正文后为参考文献，没有附录；正文提到的 extended version appendix 不在本源 PDF 内，因此其中的 feature list、shape configuration 和 task-scheduler derivation 均不补写为已核实事实。

## § 1 — 研究问题与重要性

论文要解决的不是“怎样把某一个 convolution 写快”，而是怎样从算子的数学定义出发，自动为不同硬件生成高性能的 tensor program。这里的 tensor program 是已经落实了 tile、loop order、parallel、vectorization、unroll、fusion 和 memory placement 等决定的底层实现。难点在于，这些决定组合成极大的离散空间；vendor library 需要专家逐算子、逐平台手调，而已有自动搜索又常因搜索空间太窄或探索方式不合适而错过好程序。论文在摘要中把 Ansor 概括为“hierarchical search space 采样完整程序，再用 evolutionary search、learned cost model 和 task scheduler 细化”，并报告相对当时最好替代方案，在 Intel CPU、ARM CPU、NVIDIA GPU 上的 DNN execution performance 最高分别提升 3.8×、2.6×、1.7×。[pdf:E01]（PDF 物理页 2，Abstract 与 Introduction）

这个问题重要，是因为新 operator 和新 accelerator 的增长速度高于手写 kernel/template 的增长速度。论文指出，当时 TVM 中仅模板代码就超过 15K 行，而且模板通常只能覆盖设计者预先想到的结构；Ansor 的价值主张因此不只是“把已知模板参数调得更好”，而是让只有数学定义的新算子也能进入自动优化流程。[pdf:E02]（PDF 物理页 3，Introduction contributions 与 §2 Template-guided search）

## § 2 — 前人工作与不足

论文把最接近的方法分成两类。第一类是 AutoTVM、FlexTensor 这样的 template-guided search：template 把高层 program structure 固定下来，搜索器只调 tile size、unroll factor 等参数。它对常见 operator 有效，但 template 编写成本高；FlexTensor 虽有较通用的 template，仍以单 operator 为粒度，难以表达 operator fusion 等跨节点结构。[pdf:E02]（PDF 物理页 3，§2）

第二类是 Halide auto-scheduler 一类 sequential construction：按固定顺序展开 computation graph，每一步用 cost model 对尚未完成的 program 排名并保留 top-k。问题不只是 beam width 不够，而是标签来自可编译、可测量的完整程序，拿这个模型比较 incomplete program 会发生系统性错判。论文用 20,000 个随机完整程序训练模型，再逐步遮掉 transformation 构成 partial program；Figure 3 显示在信息极少时 pairwise accuracy 从约 50% 起步、top-k recall 从 0% 起步，接近完整程序后才快速提高。固定 decision order 还难以容纳新增 cache node、rfactor 等会改变后续决策数的 transformation。[pdf:E03]（PDF 物理页 4，Figures 2–3 与 §2 Sequential construction based search）

论文原文还把 polyhedral compiler、graph-level optimization、general auto-tuning 列为相关路线。它们分别擅长 affine transformation、graph rewrite 或用户给定空间内的探索，但没有同时给出 Ansor 所追求的“从 computation definition 自动生成大空间，并对完整 tensor program 做高效测量驱动搜索”的组合。这个对比只依据本论文的 related work，不等价于对 2020 年后工作的完整 novelty 检索。

## § 3 — 重建作者的思考路径

下面是基于论文证据的推断，而不是作者逐字给出的发明史。

第一步，研究者已经知道 declarative tensor expression 能把“算什么”与“怎样执行”分开，所以自动生成 schedule 在原则上可行。第二步，手写 template 的经验说明好程序确实存在于 tile、fusion、cache、parallel 等组合中，但把 structure 固定后，搜索只能在一个人为切出的局部空间里移动。第三步，Halide 路线又暴露出相反问题：如果一边搭程序一边剪枝，cost model 必须评价尚不能真实运行的中间态，而 Figure 3 说明这种评价在最需要剪枝的时候最不可靠。[pdf:E03]（PDF 物理页 4，Figures 2–3）

于是一个自然转向是：不要对 incomplete program 做早期生死判断；先用少量规则枚举高层结构，再随机补全低层参数，使每个被比较的候选都成为可编译、可测量的完整程序。随机补全保证广覆盖，evolutionary search 负责把“广但粗”的样本推向高性能区域，真实硬件测量不断给 cost model 提供更贴近目标设备的标签。最后，当优化对象从一个 subgraph 扩展到整个 DNN，搜索预算本身也成为变量，于是再用 task scheduler 把测量机会投向最可能降低 end-to-end latency 的 subgraph。

## § 4 — 核心 Intuition

Ansor 的核心是把“程序长什么样”和“每个细节取什么值”分成两层：sketch 枚举高层 structure，annotation 补全 tile size、parallel、unroll 等低层细节。它只让 cost model 排完整程序，再用真实硬件测量和 evolutionary search 逐轮改进，避开 incomplete-program ranking 的结构性误差。对整网优化时，它不平均消耗预算，而是优先优化对 end-to-end performance 贡献最大的 subgraph。[pdf:E04]（PDF 物理页 5，Figure 4 与 §3 Design Overview）

## § 5 — 具体方法与完整 Pipeline

以一个包含 `matmul → ReLU` 的小图为例，完整 pipeline 如下。

1. **输入与切图。** 用户提供类似数学表达式的 computation definition；实际 DNN 先由 Relay 的 operator-fusion 逻辑切成多个小 subgraph。每个 subgraph 进入独立 tensor-program task，最终目标仍由整网 latency 连接起来。[pdf:E04]（PDF 物理页 5，Figure 4）
2. **生成 sketch。** Ansor 把当前状态记作由 program structure 与工作节点组成的状态，按反向 topological order 应用 derivation rules。Table 1 包括 Skip、Always Inline、Multi-level Tiling、Tiling with Fusion、Add Cache Stage、Reduction Factorization，也允许 user-defined rule；一条规则可以产生多个后继状态，因此系统用 queue 穷举高层分支。CPU 的 dense compute 节点采用 `SSRSRS` 多级 tile pattern，典型 subgraph 的 sketch 数少于 10。[pdf:E05]（PDF 物理页 6，Table 1 与 §4.1）
3. **补全 annotation。** 系统从 sketch 中随机选择一个，均匀采样合法 tile factor，并加入 outer-loop parallel、inner-loop vectorize/unroll、computation location 等决定；constant weight 的 layout 可在 compile time 重写以匹配多级 tile。GPU 把 tile pattern 改成 `SSSRRSRS`，前三个 space tile 分别绑定 BlockIdx、virtual thread、ThreadIdx，并增加 shared-memory cache 与 cross-thread reduction 规则。[pdf:E06]（PDF 物理页 7，§4.2–§4.3）
4. **得到完整程序。** Figure 5 展示同一个数学输入如何先变成不同 sketch，再因 tile factor、loop simplification、vectorization、rfactor 等 annotation 产生多个完整 program。这一步的关键不是随机样本本身就快，而是让大空间中的不同结构都有机会成为后续 fine-tuning 的起点。[pdf:E07]（PDF 物理页 8，Figure 5 与 §5 opening）
5. **evolutionary fine-tuning。** 初始 population 混合新随机程序和上轮高分程序；mutation 改 tile size、parallel granularity、pragma 和 computation location，node-based crossover 则按 DAG node 合并两位 parent 的 rewrite history。cost model 快速评估大量完整候选，少量高分候选才真正编译并在目标硬件测量，测量结果再训练模型。[pdf:E08]（PDF 物理页 9，§5.1–§5.2）
6. **跨 task 分配预算。** 对多个 subgraph，task scheduler 把一次“生成并测量一批候选”定义为一个 time unit。它以 end-to-end objective 的估计梯度为依据选择 task，同时用 ε-greedy 保留探索；如果一个高 latency subgraph 连续投入后不再下降，其估计边际收益会降低，预算就转向别处。[pdf:E09]（PDF 物理页 10，§6 与 Table 2）
7. **输出。** 每个 subgraph 得到面向特定 target 的 tensor program，随后组成 DNN inference executable。论文实现约 12K 行 C++，其中约 3K 为 search policy、9K 为其他 infrastructure；生成的自有 IR 最终 lowering 到 TVM IR，TVM 在这里被当作 deterministic code generator。[pdf:E10]（PDF 物理页 11，§7 opening）

## § 6 — 核心数学推导（无形式化数学则跳过）

第一组数学对象描述 sketch enumeration。论文令状态为 \(\sigma=(S,i)\)，其中 \(S\) 是当前部分生成的 program structure，\(i\) 是正在处理的 DAG node；规则把它变为 \(\sigma'=(S',i')\)，且 \(i'\le i\)。当 \(i=0\) 时得到 terminal state，所有 terminal state 的 \(S\) 构成 sketch list。这个形式的直觉是：高层 structure 可以分支枚举，但每个分支都必须最终走到完整可 annotation 的骨架。[pdf:E05]（PDF 物理页 6，Table 1 与 §4.1）

第二组数学对象是 learned cost model。对完整程序 \(P\)，模型分别预测每个 innermost non-loop statement \(s\in S(P)\) 的得分，再求和作为整程序预测。以真实 throughput \(y\) 同时作为标签和权重，loss 为：

\[
\operatorname{loss}(f,P,y)
=y\left(\sum_{s\in S(P)}f(s)-y\right)^2.
\]

因此快程序的排序错误受到更高惩罚，这和系统真正关心“从候选里找出顶部程序”一致。底层模型是 gradient boosting decision tree；同一模型使用来自所有 DAG 的样本，各 DAG 内 throughput 归一化到 \([0,1]\)。[pdf:E08]（PDF 物理页 9，§5.2）

第三组数学对象是 task allocation。令 \(t\in\mathbb{Z}^n\) 表示给 \(n\) 个 task 的 time-unit 分配，\(g_i(t)\) 表示 task \(i\) 当前得到的最小 subgraph latency，整网目标写成

\[
\min_t f\bigl(g_1(t),g_2(t),\ldots,g_n(t)\bigr).
\]

单个 DNN 的 latency 近似为 \(f=\sum_i w_i g_i\)，其中 \(w_i\) 是 subgraph 在网络中出现的次数；多 DNN 时，Table 2 还给出总 latency、latency requirement、相对 reference 的 geometric mean speedup 和带 early-stopping estimate 的目标。scheduler 用最近一个 backward window 的实际改善速度，加上依据相似 task FLOP/s 作出的 optimistic estimate，近似 \(\partial f/\partial t_i\)，选择绝对梯度最大的 task；这里“梯度”表达的是再给一次测量机会，预计能让最终目标下降多少，而不是对 tensor value 求导。[pdf:E09]（PDF 物理页 10，§6.1–§6.2 与 Table 2）

## § 7 — 实验设计与结论

**问题一：更大的搜索空间和完整程序 fine-tuning 是否真的带来收益？** → 论文在 10 类 operator、4 种 shape、2 个 batch size 上形成 80 个单算子 case；AutoTVM、FlexTensor、Halide auto-scheduler、Ansor 每 case 最多 1,000 次 measurement trial，并与 PyTorch/MKL-DNN 比较。正文报告 Ansor 对既有 search framework 提升 1.1–22.5×；Figure 7 再比较 full Ansor、Beam Search、No fine-tuning、Limited space，曲线是 5 次运行的 median。→ 答案是：限制空间或去掉 fine-tuning 都显著降低最终结果，beam search 还会因 partial-program 误判丢掉最终快的候选。[pdf:E10]（PDF 物理页 11，§7.1）[pdf:E11]（PDF 物理页 12，Figures 6–7）

**问题二：优势能否跨 operator boundary？** → ConvLayer（conv2d + batch norm + ReLU）和 TBS（transpose + batch matmul + softmax）在 Intel CPU 与 NVIDIA V100 上测试。→ Figure 8 报告 Ansor 相对 manual library 和 search framework 提升 1.1–14.2×；FlexTensor 在单 operator 上尚可，却因缺少 fusion 在 subgraph 上失去优势。[pdf:E11]（PDF 物理页 12，Figure 8 与 §7.2）

**问题三：局部程序改进能否转成 end-to-end DNN 改进？** → ResNet-50、MobileNet-V2、3D-ResNet-18、DCGAN、BERT 在 Intel CPU、V100、ARM Cortex-A53 上比较 PyTorch、TensorFlow、TensorRT、TensorFlow Lite、AutoTVM。→ 对 AutoTVM，Ansor 为 1.0–21.8×；对每个 case 的最好替代方案，Intel、ARM、NVIDIA 的最高提升分别为 3.8×、2.6×、1.7×。论文还报告，compile-time weight-layout rewrite 给 ResNet-50 带来约 40% 改进。[pdf:E12]（PDF 物理页 13，Figures 9–10 与 §7.3）

**问题四：高性能是否以更长搜索为代价？** → Table 3 测量 Ansor 在 Intel CPU、batch size 1 上追平 AutoTVM 所需的 measurement count 和 wall-clock time。→ 五个网络上，measurement 减少 2.7–16.5×，wall-clock time 减少 3.3–88.6×；作者据此称可用约一个数量级更少的 search time 追平 AutoTVM。cost-model test 使用 25,000 个程序，20,000 train、5,000 test，报告 0.079 RMSE、0.958 \(R^2\)、0.851 pairwise accuracy、0.624 recall@30。[pdf:E13]（PDF 物理页 14，Table 3、Figure 11 与 §7.4–§7.5）

这些结论不能外推到 dynamic shape、sparse operator 或低精度 special instruction。所有 evaluation 使用 float32；正文总体 platform 描述写的是 18-core Platinum 8124M，而 Figures 6 和 8 caption 写的是 20-core Platinum 8269CY，源 PDF 没有解释这处硬件型号差异，因此不应把两者视为同一机器配置。[pdf:E10]（PDF 物理页 11，§7 opening）[pdf:E11]（PDF 物理页 12，Figures 6、8）

## § 8 — Take-aways

**5 句话：** Ansor 把 tensor-program search space 分成高层 sketch 与低层 annotation，使自动规则能覆盖 template 没有写出的 structure。它只对完整程序做 cost-model ranking 和硬件测量，绕开 incomplete-program prediction 的核心误差。随机采样负责覆盖，evolutionary search 负责把候选推向高性能区域，二者缺一都会明显掉点。task scheduler 把有限 measurement budget 分给最可能降低 end-to-end objective 的 subgraph，使大空间并不必然带来更长搜索。论文在 float32、static-shape、dense workload 上给出强结果，但 dynamic shape、sparsity 和 special instruction 仍在系统边界之外。

**3 句话：** Ansor 的关键贡献不是更精细地调一个固定 template，而是自动构造更大的 program-structure space。它通过完整程序的 measurement-driven fine-tuning 和跨 subgraph 的预算调度，把这个大空间变成可搜索的工程系统。证据支持其在论文测试范围内的性能与搜索效率，但不支持把结果直接推广到动态、稀疏或低精度 workload。

**1 句话：** 先扩大“什么程序可能存在”的空间，再只用完整、可测程序学习“哪个值得继续”，是 Ansor 的主线。

## § 9 — 最脆弱的假设

最脆弱的假设是：operator shape 在 compilation 和 measurement 前静态已知，而且部署时不会跨出这个 shape-specific program 的有效范围。这个假设一旦不成立，Ansor 不只是“搜索慢一点”，而是无法按现有规则完成 static analysis、构造合法 tile space、编译候选并给 cost model 取得同一任务分布下的硬件标签。作者明确承认系统不能优化 dynamic-shape graph，也只支持 dense operator，并依赖 LLVM/NVCC 处理 instruction selection。[pdf:E14]（PDF 物理页 15，§9 Limitations and Future work）

论文为 static-shape 场景提供了 80 个单算子 case、多个 subgraph 和五类 DNN 的广泛证据，但这些 shape 仍在 tuning 前已知；没有实验测量同一个 program 面对 runtime shape distribution 的性能，也没有展示跨 shape 的 cost-model calibration。因此，当前证据支持“对已知静态 shape 自动生成好程序”，不支持“对动态 workload 自动生成一个持续有效的程序族”。

## § 10 — 最小复现实验

一周内最值得复现 Figure 7 的最小闭环，而不是整套五网络 benchmark。数据不需要训练集，只需取 ResNet-50 最后一个 convolution、batch size 16 的固定 tensor shape，在一台可稳定独占的 CPU 上运行四个 variant：full Ansor、Limited space、No fine-tuning、Beam Search。每个 variant 使用相同的 1,000 measurement trials，至少 5 个独立 seed；每隔固定 trial 数记录当前 best measured throughput，并统一归一化到所有 run 中的最好程序。[pdf:E10]（PDF 物理页 11，§7.1 settings）[pdf:E11]（PDF 物理页 12，Figure 7）

支持核心 claim 的结果是：full Ansor 的 median curve 在相同 budget 下稳定高于 Limited space 和 No fine-tuning，且 Beam Search 即使早期接近，最终仍停在更低平台；同时抽查 full Ansor 的最好 program，确认它至少使用了 limited template 不允许的 tile level、computation location 或其他 structure。反驳结果是：在相同 hardware、measurement protocol 和 seed 数下，Limited space 或 Beam Search 可重复达到同等最终 throughput，或 full Ansor 的优势完全来自更多有效 measurement/更少 timeout，而不是 search-space coverage 与 complete-program fine-tuning。

## § 11 — 最强反例设计

最强反例不是再找一个普通 float32 convolution，而是把同一组 DNN 改成 FP16/INT8，并选择性能主要由 Tensor Core、Intel VNNI 或 ARM Dot instruction 决定的 operator。保持 model accuracy、batch、latency measurement 和 tuning wall-clock budget 可比，分别运行原始 Ansor、能显式调用这些 intrinsic 的 vendor library/hand schedule，以及一个只改变 backend instruction selection、不改变高层 search policy 的对照。论文所有 evaluation 使用 float32，而 limitations 明确说 Ansor 的高层优化依赖外部 code generator，不能充分利用这些 special instruction。[pdf:E10]（PDF 物理页 11，§7 evaluation datatype）[pdf:E14]（PDF 物理页 15，§9）

如果 vendor/intrinsic 对照在主流低精度 shape 上持续大幅领先，而扩大 Ansor 的 sketch/annotation 搜索仍无法弥合差距，那么“大搜索空间 + 更好探索就能带来 portable high performance”的解释就不充分：真正的决定变量是搜索对象里根本不存在的 instruction-level mechanism。这个结果不会否定 Ansor 在论文所测 float32 dense static domain 内的贡献，但会直接限制其跨 workload 与跨 accelerator 的核心外推。

## § 12 — Follow-up Research Bet

**主 idea：把 graph boundary、interface layout 与 kernel schedule 合成一个可测的 graph-program sketch。** 新的研究问题不是“怎样给每个已切好的 subgraph 再调一个更快的 schedule”，而是：能否自动生成一种跨 subgraph 的程序，使 partition、fusion、intermediate-tensor layout 和局部 loop schedule 共同决定 end-to-end latency？它首次可能找到这样一类解：某个局部 kernel 单独看更慢，但因为消除了 layout conversion、扩大 fusion 或复用了 producer/consumer cache，整网反而更快。

机制上的因果链是：把 Ansor 当前“Relay 先切图、Ansor 后逐 task 搜索”的 system boundary 扩成两层 graph-program representation；上层 sketch 选择 partition/fusion 边界、intermediate layout 和跨边界 dataflow，下层 annotation 再选择每个 region 的 tiling、parallel、vectorization 与 memory placement；只有完成的跨边界 candidate 才编译并测量 end-to-end latency；evolutionary operator 同时改 boundary 与 local schedule，cost model 用 region feature 加 interface-traffic feature 评分，task scheduler 的资源单位也从单 subgraph 改成相互作用的 region group。这样改变了至少四个基本变量：搜索对象从 kernel 变成 graph-program，状态表示加入 boundary/layout，系统边界跨过原先固定 partition，评价对象从 subgraph latency 变成 end-to-end interaction。

这个押注由两类论文特异证据支撑。方法侧，Ansor 已能在 sketch 中加入 cache node、做 fusion、改 computation location，并在 compile time 重写 constant layout；系统侧却先用 Relay 固定 partition，再把 subgraph 当作独立 task。[pdf:E04]（PDF 物理页 5，Figure 4）[pdf:E05]（PDF 物理页 6，Table 1）[pdf:E06]（PDF 物理页 7，§4.2）实验侧，weight-layout rewrite 单独就给 ResNet-50 带来约 40% 改进，subgraph benchmark 又显示缺少 fusion 会显著削弱 FlexTensor；related work 最后明确把 Ansor 与更多 graph-level optimization 的 joint optimization 留作 future work。[pdf:E11]（PDF 物理页 12，Figure 8）[pdf:E12]（PDF 物理页 13，§7.3）[pdf:E14]（PDF 物理页 15，§8–§9）

最大研究收益是让 auto-scheduler 发现“局部最优无法组合成全局最优”的结构性机会，并把 layout/fusion 不再作为 compiler 前处理，而作为 tensor-program generation 的一部分。最大科学风险是组合空间与 credit assignment 同时爆炸：一次 end-to-end measurement 很难判断收益来自哪个 boundary、layout 还是 kernel schedule，现有 cost model 可能无法在可接受预算内学到这种交互。

最小判别实验可只选一个 ResNet stage，或论文中的 ConvLayer/TBS subgraph 相邻组合。固定硬件、总 measurement count 与 wall-clock budget，对比三组：固定 Relay boundary 的原 Ansor；只增加同等额外 trials 的原 Ansor；允许 joint boundary-layout-schedule mutation 的 graph-program sketch。若第三组在相同 budget 下找到可复现的 end-to-end speedup，且把其 boundary/layout 固定回 baseline 后收益消失，就支持“跨边界交互”而不是“只是多搜了几次”的机制；若额外 trials 即可追平，或收益只来自某个独立更快 kernel，则核心机制被反驳。

与本论文当时列出的最近路线相比，这个候选不是先做 graph-level rewrite 再独立调 kernel，也不是 AutoTVM 的固定 template 加 global layout search，而是把 graph boundary 与内部 tensor-program structure 放进同一个 hierarchical candidate 并用同一次 end-to-end measurement 标注。由于本任务没有联网检索 2020 年后的 graph compiler 与 auto-scheduler 工作，这只是证据约束的候选判断，不声称 novelty。

**Wild-card alternative：** 构造 shape-conditioned symbolic sketch，让 tile factor、fusion boundary 和 layout 成为 runtime shape 的分段函数，并以一组 shape distribution 而不是单一静态 shape 作为 measurement object，从而生成一个覆盖 dynamic-shape workload 的 program family。
