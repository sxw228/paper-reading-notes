# Pruner: A Draft-then-Verify Exploration Mechanism to Accelerate Tensor Program Tuning

**作者：** Liang Qiao，Jun Shi，Xiaoyu Hao，Xi Fang，Sen Zhang，Minfan Zhao，Ziqi Zhu，Junshi Chen，Hong An，Xulong Tang，Bing Li，Honghui Yuan，Xinyang Wang  
**出处：** ASPLOS ’25（Proceedings of the 30th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 2）  
**年份：** 2025  
**DOI：** 10.1145/3676641.3716269  
**Zotero key：** TUX7SRER  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

搜索式 tensor compiler 的实际瓶颈不只在“需要测很多 kernel”，也在“为了决定测哪些 kernel，先对海量候选做了一遍昂贵的 learned cost model 推理”。以 Ansor 在 Jetson Orin 上调优三个 DNN 为例，论文报告 space exploration 已占总时间的近 40%，而更复杂的 cost model 会进一步放大 feature extraction 和 GPU inference 的开销。[pdf:E02]（PDF 物理页 4，Table 1 与 §2.3）这使一个本来用于省测量时间的预测器，反过来成为调优过程的主要成本来源之一。

论文同时处理两个相连问题：第一，能否先用极便宜但有硬件含义的模型从大空间里“打草稿”，只让复杂模型验证一个小候选集；第二，learned cost model 在换 GPU 后能否利用源平台预训练知识，同时不被目标平台早期少量且有偏的数据带偏。作者提出 Pruner 与 MoA-Pruner，并在三类 NVIDIA GPU 平台上报告：在线场景相对 Ansor 的平均搜索时间 speedup 分别为 2.6× 和 4.82×，离线场景 Pruner 相对 TenSet 与 TLP 分别为 4.75× 和 4.05×，TensorCore 场景相对 MetaSchedule 为 4.08×。[pdf:E01]（PDF 物理页 1，Abstract）这些结果的重要性在于，它们针对的是“得到同等调优性能需要多久”，而不是只压低单个 cost-model batch 的延迟。

## § 2 — 前人工作与不足

Ansor、AutoTVM 与 MetaSchedule 已把 schedule 生成和搜索自动化；TenSetMLP、TLP、TIRAMISU 等则用 learned cost model 取代或增强传统经验模型。问题是 Ansor/TenSetMLP 的 statement-level 特征需要专家设计和较重的提取，TLP 虽用 schedule primitive 与 Transformer 表示时序关系，却依赖大规模离线数据，而且论文观察到其 one-hot 特征在一个 GEMM 中只有 1.387% 的值发生变化，目标平台小数据 fine-tuning 甚至可能无法找到可用解。[pdf:E02]（PDF 物理页 4，§2.3 Opportunity 2）

另一条路线是直接收紧空间或改变搜索器：Heron 用硬件约束，Felix 构造可微空间，Roller 用精细硬件模型和规则推导候选。这些方法或仍需让复杂模型评分每个候选，或对 operator、shape 和硬件模型有更强约束。跨平台方面，TenSet 训练一个额外模型预测源—目标性能差，Moses 做参数可迁移性蒸馏，TLP 使用 multi-task learning；作者认为这些方案仍引入额外 transfer effort，且没有解决在线早期数据少而偏的问题。[pdf:E13]（PDF 物理页 15，§7 Related Work）因此，Pruner 的直接对手不是单一模型，而是“所有候选都走昂贵评分”和“换平台后重新学”的联合工作方式。

## § 3 — 重建作者的思考路径

可以从三个既有事实反推这条路线。其一，GPU kernel 的性能与层次存储、并行粒度和 transaction 对齐强相关，很多 schedule 明显违背容量或并行资源约束；因此第一阶段未必需要一个能精确排序所有程序的神经网络，只要能高召回地排除明显不合硬件的 schedule。其二，真正区分好坏 schedule 的信息不只存在于孤立 statement，而存在于 global/shared/register 之间按时间发生的数据移动；把 tensor program 看成 temporal dataflow，可能比稀疏 one-hot primitive 更容易从小数据学习。其三，源平台模型虽不能直接当目标平台模型，却可能仍提供比随机初始化更好的表征起点；若源模型随目标梯度缓慢移动，而每轮目标模型都从这个平滑起点出发，早期有偏样本的破坏会减弱。

这条思考链没有先假设 Pruner 已经有效，而是从“粗筛只需高召回”“性能是层次数据流的结果”“跨平台初始化需要平滑演化”三个旧线索，分别得到 LSE、PaCM 和 MoA。论文的完整 Algorithm 1 正好把它们串成同一闭环：task scheduler 选 subgraph，LSE 生成 draft，PaCM 排序并测量，随后更新 tuning record 和 MoA 模型。[pdf:E03]（PDF 物理页 5，Algorithm 1）

## § 4 — 核心 Intuition

Pruner 不要求一个模型同时做到“便宜地扫全空间”和“精确地区分顶尖候选”。它让基于硬件符号的简易 analyzer 负责高召回粗筛，让 learned cost model 只在小候选集中做高精度排序；与此同时，PaCM 用跨层级内存的 temporal dataflow 表示真实程序行为，MoA 则让跨平台预训练权重以动量方式逐轮适应目标硬件。

真正改变工作方式的不是“再加一个 predictor”，而是把一次昂贵的全空间评分拆成信息需求不同的两级决策：draft 阶段只需要判断“值得进入决赛吗”，verify 阶段才需要判断“谁最好”。

## § 5 — 具体方法与完整 Pipeline

以一个 GEMM-ReLU fused subgraph 为例，完整流程如下。

1. **构造搜索空间。** TVM 根据 subgraph DAG 生成 split、reorder、cache read、compute-at 等 schedule primitives；Algorithm 2 随机初始化 schedule population，并用 GA 对 tiling factor 做 mutation。[pdf:E03]（PDF 物理页 5，Algorithm 2）
2. **抽取 hardware-aware symbols。** LSE 遍历低层 IR 的 buffer statement，在 L0/L1/L2 三个抽象存储层统计 allocation、computation、parallelism、memory footprint、transaction dimension 等八类符号。Figure 3 展示了 GEMM-ReLU 从原始循环、DAG、schedule template 到这些符号的对应关系。[pdf:E04]（PDF 物理页 6，Table 2 与 Figure 3）
3. **Draft。** Symbol-based Analyzer 把符号转换成容量、计算利用率和 memory transaction 对齐等 penalty，用一个解析延迟近似作为 GA fitness；每步把较优 schedule 放进候选集并继续 mutation。这里的目标不是精确预测真实 latency，而是保留高潜力 schedule。
4. **补入随机性。** Algorithm 1 将 LSE 产出的候选与随机初始 schedule 合并，避免经验公式完全封死探索方向。[pdf:E03]（PDF 物理页 5，Algorithm 1 lines 9–10）
5. **Verify。** PaCM 从程序中抽取跨 global/shared/register 的多层 tiling dataflow。每个 data-movement block 被编码为 23 维向量，包含 memory access、allocation、flow direction 和 compute density；该序列走 self-attention branch，Ansor statement features 走 linear branch，两者 concat 后输出 normalized performance rank。[pdf:E05]（PDF 物理页 7，Figure 4 与 §4.2）
6. **测量与迭代。** 排名靠前的 schedule 在目标 GPU 上真实测量，结果回写 tuning record。在线 MoA 模式下，每轮目标 PaCM 从 Siamese source model 权重初始化并用新数据 fine-tune；随后以目标梯度对 Siamese 权重做 momentum update，论文固定 momentum 为 0.99，且 Siamese branch 不做额外 forward/backward。[pdf:E06]（PDF 物理页 8，Figure 5 与 §4.3）
7. **输出。** 多轮 task scheduling 后，对每个 subgraph 选出最佳已测 schedule，生成面向目标 GPU 的 tensor program。论文是在 TVM 的 Ansor 与 MetaSchedule 搜索框架内实现，并针对 CUDA core 与 TensorCore 扩展相应 symbol/dataflow。[pdf:E10]（PDF 物理页 12，§6.4）

论文没有讨论 FPGA 映射、定点位宽、片上流水线、显式通信时序或真实硬件多速率执行；它的“硬件”对象是 GPU 层次存储和并行单元，不能把结果直接外推到 FPGA HLS 或 EMT real-time solver。

## § 6 — 核心数学推导（无形式化数学则跳过）

LSE 的数学角色是把“schedule 是否贴合硬件”变成一个便宜的 latency proxy。对计算型 statement，先把不同层级的计算 penalty 相乘，得到可用峰值计算能力

\[
U_p=T_p\prod_{l_i}P_{l_i,c};
\]

对 memory 侧，则用最低存储层的理论带宽与各层 memory penalty 得到

\[
U_m=T_m\prod_{l_i}P_{l_i,m}.
\]

最后对第 \(i\) 个 innermost statement，分别估计 \(L_c^i=S_8/U_p\) 与 \(L_m^i=S_5/U_m\)，再求和：

\[
L_{total}=\sum_i(L_c^i+L_m^i).
\]

其中 \(S_8\) 是 floating-point operation 数，\(S_5\) 是实际 memory access；这就是论文 Eq. (1)。[pdf:E05]（PDF 物理页 7，Eq. 1）直觉上，这是一个简化的 roofline-like 加和：先用对齐与容量 penalty 折损理论吞吐，再用“工作量/有效吞吐”算时间。它刻意忽略 compute-memory overlap、cache 细节和复杂 instruction behavior，因此只适合作为 draft ranking proxy。

具体 penalty 也体现了“对齐”的含义。例如 L0 memory penalty 使用 \(P_{l0,m}=\min(m_{l0}/S_1,1)\)，超过 L0 容量才受罚；L1 parallel penalty 用 schedule block 数相对可同时激活 block 数的整除关系估计利用率；L2 memory penalty用 transaction length 对齐估计浪费。[pdf:E04]（PDF 物理页 6，§4.1 Hardware-aware Penalty）这些式子没有声称是精确 GPU simulator，而是给 GA 一个成本低、方向大致正确的 fitness。

PaCM 的训练不是做绝对延迟回归，而是使用 normalized latency 与 LambdaRank loss 学习排序。[pdf:E06]（PDF 物理页 8，§4.2 Pattern-aware Transformer）数据集评测中的 Top-\(k\) 衡量 cost model 选出的前 \(k\) 个候选能多接近每个 subgraph 的最优 latency；Best-\(k\) 则衡量 LSE draft 集本身包含多好候选。论文在 Eq. (2)–(3) 中对 subgraph 出现频次 \(w_i\) 加权，以反映它们对整网 latency 的实际贡献。[pdf:E11]（PDF 物理页 13，Eq. 2–3）

## § 7 — 实验设计与结论

**问题一：同样 2,000 次真实 trials，能否更快找到同等或更好的 schedule？** 作者在 A100、Titan V、Jetson Orin-AGX 上，用 14 类视觉与语言模型覆盖 online/offline cost-model tuning；每轮测 10 个程序、最多 200 轮，LSE draft size 固定为 512。[pdf:E07]（PDF 物理页 9，§5 Tuning settings 与 Figure 6）答案是 Pruner 的 tuning curve 通常更早下降，且达到基线最终性能所需 search time 更短。MoA-Pruner 在 A100 上以 2,000 trials 对比更多 trials 的 Ansor时，Table 5 中四个模型的 tuning cost 为 84–98 分钟，而 Ansor 为 441–743 分钟；但 Inception-v3 上 MoA-Pruner 的 2.739 ms 略差于 Ansor 的 2.694 ms，说明“更快”并不保证每个 workload 最终 latency 都更优。[pdf:E08]（PDF 物理页 10，Table 5）

**问题二：加速是否真的来自 draft/verify，而非仅换了模型？** 编译成本实验显示，2,000 trials 时 Pruner 与 MoA-Pruner 的平均 compilation time 分别是 Ansor 的 84.1% 与 75.3%；机制上，LSE 把每轮需 learned-model 评分的候选从 8,000 缩到 512。PaCM 最大 GPU memory 为 1,694 MB，接近 TenSetMLP/Ansor 的 1,546 MB，明显低于论文报告的 TLP 4,812 MB。[pdf:E10]（PDF 物理页 12，§6.3 与 Table 7）离线 ablation 仍显示移除 LSE 后搜索成本和推理 latency 同时变差，说明 draft 并非只在弱在线模型下有用。[pdf:E13]（PDF 物理页 15，Table 13）

**问题三：LSE 会不会把最优 schedule 剪掉？** 在 TenSet T4 上，每个 subgraph 模拟 4,000 个 explored schedules，Best-1 随 draft size 增长；size 512 时完整 LSE 为 0.995，去掉 compute penalty 与 memory penalty 后分别降至 0.880 和 0.930。[pdf:E11]（PDF 物理页 13，Table 10 与 Figure 14）答案是在该静态数据集与这些 GPU 上，LSE 有很高的 top-candidate recall，但这不是对任意硬件或新 schedule template 的保证。

**问题四：temporal dataflow feature 是否比既有 feature 更易学？** 在 TenSet T4/K80 的 600 万训练样本设置下，PaCM 的 Top-1/Top-5 分数分别为 0.892/0.962 与 0.897/0.969，高于 TenSetMLP 和 TLP；不同数据规模曲线也显示 PaCM 更早收敛。[pdf:E12]（PDF 物理页 14，Figure 15 与 Table 11）ablation 中去掉 temporal dataflow feature 的损失总体大于去掉 statement feature，但个别 workload 并不单调，说明两支的互补性比“dataflow 永远更重要”更准确。

**问题五：能否覆盖 TensorCore 与现实 kernel library 的强项？** 作者为 16×16×16 WMMA 加入 TensorCore symbol 和 shared-to-fragment dataflow，在六个 Transformer 模型上相对 MetaSchedule 报告平均 4.08× search speedup。[pdf:E10]（PDF 物理页 12，Figure 12 与 Table 9）然而 specialized library 在 reduction axis 很大时可用 splitK 等 TVM 简单 tiling space 不含的算法；GPT-2 的一个 linear operator 中 Pruner 为 23.46 μs，而 cudaLib 为 18.96 μs。[pdf:E10]（PDF 物理页 12，Table 8）这划定了结论边界：Pruner加速的是给定 search space 内的探索，不能补回 search space 根本没有表达的算法。

## § 8 — Take-aways

**5 句话。** 第一，tensor tuning 的成本可被拆成便宜高召回 draft 与昂贵高精度 verify，而无需让 learned cost model 扫过全部候选。第二，LSE 用层次存储、并行度和 transaction 对齐构造符号化 hardware-fitness proxy，并在 TenSet ablation 中证明这些 penalty 对保留优质候选有贡献。第三，PaCM 把 tensor program 表示成跨存储层的 temporal dataflow 序列，再与 statement features 合并做 ranking。第四，MoA 用缓慢更新的 Siamese source model 为每轮 target model 提供跨平台初始化，改善在线早期小而偏数据的训练。第五，Pruner 在多个 NVIDIA GPU 与 CUDA/TensorCore 实验中显著减少搜索时间，但优势仍受 TVM schedule space 和论文覆盖硬件族限制。

**3 句话。** 论文最重要的系统洞见是：粗筛与精排需要不同模型，把二者解耦可以同时减少推理量和保持搜索质量。最有说服力的证据是 LSE 候选 recall、PaCM ranking 与端到端 search time 三层实验相互闭合，而不仅是单一模型 accuracy。最重要的边界是，搜索器无法发现 search space 未表达的 splitK、Winograd 等 specialized algorithm，且跨平台证据仍只覆盖三种 NVIDIA GPU。[pdf:E09]（PDF 物理页 11，§6.1–6.2）

**1 句话。** Pruner 的贡献是把 tensor schedule search 从“复杂模型全空间评分”改成“硬件符号先选潜力区、数据流模型再精排”，以较小候选集换取更快且通常不降质的调优。

## § 9 — 最脆弱的假设

最脆弱的假设是：**LSE 的简化 hardware-fitness ranking 在真正高性能 schedule 附近仍有足够高的召回率。** 如果架构性能主要由它没建模的机制决定，例如 instruction issue、cache conflict、asynchronous copy pipeline、bank conflict、tensor-core fragment layout，或 search space 引入全新算法模板，那么优秀 schedule 可能在 draft 阶段被系统性删除；后面的 PaCM 再准确也看不到它们，核心的“两级搜索不损质量”便失效。

论文为此提供的正面证据是 TenSet T4 上 size 512 的 Best-1 为 0.995，且移除 compute/memory penalty 会明显下降；端到端 ablation 里移除 LSE 也普遍增加 tuning latency 与 cost。[pdf:E11]（PDF 物理页 13，Table 10）但证据缺口同样明确：静态 recall 分析只覆盖 TenSet 的既有 schedule distribution，硬件验证只覆盖 NVIDIA GPU；论文没有在新 ISA、新 memory hierarchy、全新 schedule primitive 或 adversarial shape 下测“被剪掉的真正最优解比例”。因此这是经验支持较强、外推仍脆弱的假设，而不是可证明性质。

## § 10 — 最小复现实验

一周内不必复现整网和所有 baseline，只验证“draft 是否以很小评分预算保住优质候选”。选 TVM/Ansor 中 20 个 subgraph：GEMM、conv2d、reduction、fused elementwise 各若干，覆盖规则 shape 与一个容易触发 splitK/低并行度的极端 shape。对每个 subgraph 固定生成 4,000 个 schedule，全部在一块可用 NVIDIA GPU 上真实测量，得到 oracle latency 排名。

实现三种相同输出规模的 draft：随机抽样、只按简单 occupancy/memory capacity 过滤、论文 LSE penalty。每种方法输出 256 与 512 个候选，测 Best-1、oracle top-10 recall、draft CPU time，以及由同一个 cost model 在候选内选出的最终真实 latency。核心支持标准是：LSE 在大多数 subgraph 上的 top-10 recall 明显高于随机与简单过滤，同时 draft time 远小于对 4,000 个候选做完整 feature extraction 和 model inference；反驳标准是：在极端 shape 或某类 operator 上，LSE 反复漏掉 oracle top-10，导致最终 latency 显著变差。论文采用 Best-\(k\) 的原因和定义可直接作为复现指标。[pdf:E11]（PDF 物理页 13，Eq. 3 与 Figure 14）

这个实验应固定 search space、候选集合、真实测量次数和 verify model，避免把“生成了不同候选”误当成 LSE ranking 更好。至少重复真实测量并报告 variance；不要只复现 Table 10 的静态数字，因为目标是检验本机硬件上的关键因果环节。

## § 11 — 最强反例设计

最强反例是构造一组 **同等 LSE score、真实 latency 却由未建模硬件事件分成两个簇** 的 schedule。具体可针对 shared-memory bank conflict、global-memory coalescing 与 asynchronous copy pipeline，生成成对 schedule：保持 L0/L1/L2 allocation、parallel block 数、FLOP 和粗粒度 transaction dimension 几乎不变，只改变地址映射、padding、vector width 或 pipeline stage，使一半发生严重 conflict/stall，另一半避免这些事件。然后用 profiler counters 确认两个簇的差异确实来自目标事件，而不是工作量改变。

若 LSE 在多种 shape 上持续把“低分但快”的 schedule 排除，且把 draft size 从 256 增至 512 仍不能恢复 oracle top candidates，就说明其高 recall 来自现有 benchmark distribution，而非硬件符号足以刻画高性能区域。进一步让 PaCM 只在 LSE draft 内运行：如果 PaCM 在全集上能选对、在 draft 内必然失败，便可把责任精确归因于 draft bottleneck。论文自己的 specialized-kernel 结果已经提示这个方向：当 reduction axis 大时，splitK 等 search-space/机制差异可让 cudaLib 超过 Pruner。[pdf:E09]（PDF 物理页 11，Figure 9 附近讨论与 §6.2）

## § 12 — Follow-up Research Bet

**主押注：把 schedule tuning 改造成“主动生成反事实 schedule 对，以学习硬件响应算子”的实验科学。** 新问题不是“哪个 schedule 分数最高”，而是：能否自动合成只改变一个硬件相关设计变量的 schedule 对，并从真实测量中学习“某个 dataflow/tiling 改动通过哪类硬件瓶颈改变 latency”的可迁移响应表示？若成功，编译器将首次不仅能在现有候选中排序，还能回答“为了在这台未知设备上暴露并利用某类并行或数据移动能力，下一对最有信息量的程序应怎样构造”，从而主动建立目标硬件的可操作 performance map。

核心机制有一条明确因果链：LSE 已能把 schedule IR 映射为八类 hardware-aware symbols 和容量/并行 penalty；PaCM 已能把同一程序映射为按时间排列的跨层 dataflow blocks。[pdf:E04]（PDF 物理页 6，Table 2 与 Figure 3）在此基础上，生成器每次选择一个可控变量，例如 tile factor、memory level、vector width 或 dataflow order，合成结构尽量相同的成对 schedule；硬件测量给出 latency 与 counters 的差分；模型学习从“symbol/dataflow 差分”到“性能响应差分”的局部算子，再用最能区分候选瓶颈解释的 schedule 对作为下一次主动实验。这里改变了研究目标（从静态 ranking 到识别可干预响应）、数据生成方式（从搜索轨迹被动采样到反事实成对激励）和状态表示（从程序 embedding 到带干预语义的 response operator），删除新增机制后，系统会失去主动辨识硬件的基本能力。

全文中有两类特异依据。方法上，LSE 已提供可操纵的 hardware symbol 与 schedule mutation，PaCM 已证明 temporal dataflow 是可学习且比纯 statement feature 更关键的表示基础。[pdf:E05]（PDF 物理页 7，Figure 4）；[pdf:E12]（PDF 物理页 14，Table 12 与 Figure 16）实验上，LSE 在固定 TenSet distribution 中可高召回 draft，但 specialized splitK、Winograd 与 reduction-heavy kernel 暴露了现有搜索空间/表示未覆盖的机制边界。[pdf:E09]（PDF 物理页 11，§6.1–6.2）这正好说明“继续扩大同分布训练集”未必能发现真正缺失的硬件响应变量。

最大收益是获得一种面向未知 accelerator 的低样本 **mechanism discovery** 能力：它既可指导搜索，也可形成可解释的 device abstraction，并让跨平台迁移针对“响应规律”而非整模型权重。最大科学风险是所谓成对 schedule 无法只改变一个机制，compiler lowering 会引入隐含差异，counter 也可能不能唯一归因；最终学到的仍只是另一种相关性 ranking。首个证伪实验应在两块微架构不同的 GPU 上、用相同 20 个 subgraph 和相等测量预算比较三组数据：随机 schedule、普通 search trajectory、反事实 schedule pairs。除最终 best latency 外，要求模型预测未见 schedule pair 的 latency 差分符号与 profiler-counter 差分；若 pairs 只改善排序、不改善跨平台差分预测，或在控制 lowering 后优势消失，就否定“学到响应机制”而支持“只是更好的采样”这一最强替代解释。

与最近工作的实质区别是：Ansor/TenSet/TLP/PaCM 学的是 program-to-performance mapping，Felix 学的是可微搜索方向，Roller/Heron 用预设 hardware rule 收紧空间；本押注把 **干预本身** 作为实验对象，学习 schedule change-to-hardware response mapping。由于本卡按输入边界未联网补查 2025 年后的 active compiler autotuning 工作，这一差异属于基于本文 related work 的候选判断，不声称 novelty。

**Wild-card alternative：** 让编译器先合成一组覆盖 global/shared/register 与 TensorCore fragment 数据流的可执行 micro-probe，直接从测量反推出 device abstraction，再由该 abstraction 生成 schedule space；它以“先发现硬件对象、再定义搜索空间”为核心，机制和设计变量都不同于反事实 schedule-pair 响应学习。[pdf:E10]（PDF 物理页 12，§6.4 的 TensorCore symbol 与 shared-to-fragment dataflow 扩展）
