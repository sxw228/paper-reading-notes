# Graph Neural Networks for High-Level Synthesis Design Space Exploration

**作者：** Lorenzo Ferretti；Andrea Cini；Georgios Zacharopoulos；Cesare Alippi；Laura Pozzi。[pdf:E01]（PDF 物理页 1，标题与作者栏）

**出处：** *ACM Transactions on Design Automation of Electronic Systems*，Vol. 28，No. 2，Article 25。[pdf:E01]（PDF 物理页 1，ACM Reference format）

**年份：** 2022。[pdf:E01]（PDF 物理页 1，出版信息）

**DOI：** 10.1145/3570925。[pdf:E01]（PDF 物理页 1，DOI）

**Zotero key：** CV2X2APN

**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是一般意义上的“预测一次 HLS 结果”，而是一个更具体的自动化问题：面对由多种 pragma 取值做笛卡尔积形成的巨大配置空间，怎样用尽可能少的真实综合，找到 latency 与 FPGA resource cost 之间的 Pareto-optimal configurations。作者指出，HLS 接收 C/C++/SystemC 行为描述、综合 directives、technology library 和 target frequency，输出 RTL、性能与资源报告；配置数量随 directives 增长而快速膨胀，而真正 Pareto-optimal 的点只占很小一部分，因此 exhaustive synthesis 在计算成本上不可行。[pdf:E02]（PDF 物理页 2，Section 1）[pdf:E03]（PDF 物理页 3，Fig. 1）

这个问题重要，原因在于 HLS 把硬件设计入口提升到了软件层，却没有自动消除架构选择成本：unrolling、array partitioning、resource binding、inlining 等 directives 会同时改变并行度、时延和资源占用，设计者仍需在一个昂贵的多目标空间里搜索。若能在不解析 HLS compiler 内部 analytical model 的前提下，从既有综合数据学习一个跨程序的 predictor，就可以先廉价估计全部候选，再只综合预测的 Pareto points，把综合预算集中在最有价值的区域。[pdf:E02]（PDF 物理页 2，Section 1，问题与贡献陈述）

论文的工程价值因此有两层。第一层是 surrogate modeling：同时预测 latency、FF、LUT、DSP 等结果，替代大批 HLS runs。第二层是 transfer：把在历史 designs 上学到的表示迁移到新 design，仅用少量目标域综合做 fine-tuning，再执行 DSE；作者把这一框架称为 **gnn4hls**。[pdf:E02]（PDF 物理页 2，Section 1）

## § 2 — 前人工作与不足

**论文对 model-based methods 的归纳。** HLScope+、MPSeeker、COMBA、Aladdin、FLASH 及其他 analytical/simulation approaches 通过显式建模 compiler、schedule 或 hardware template 来估计性能与资源。它们可以很准，但通常需要 reverse-engineer 特定 HLS tool 和 pragma semantics，往往只覆盖有限 directives、固定 application class 或受限 architecture template；tool version、directive set 或应用结构变化后，模型需要专家重新修订。[pdf:E24]（PDF 物理页 15，Section 5，model-based methodologies）[pdf:E25]（PDF 物理页 16，Section 5，model-based 与 black-box 对比）

**论文对 black-box/refinement methods 的归纳。** Genetic Algorithms、response-surface refinement、simulated annealing、random forest refinement 等方法更 tool-agnostic，但知识主要在当前 DSE 中通过真实 synthesis 逐步积累；要逼近完整 Pareto frontier，通常需要许多迭代和较多综合。它们避免了 compiler analytical model，却没有消除昂贵标签获取这一瓶颈。[pdf:E25]（PDF 物理页 16，Section 5）

**此前 learning/transfer approaches 的关键限制。** 作者认为，program 长度、拓扑、constructs 和 directives 都变化很大，固定长度 vector representation 难以保留这些结构；以 source-code similarity 或 multi-domain MLP 做 transfer 的方法，也常与目标 design space 绑定，或需要为每个 domain 设置独立输入/输出层。[pdf:E04]（PDF 物理页 4，Section 2.2）[pdf:E26]（PDF 物理页 17，Section 5，prior-knowledge 与 vector-based transfer）

**此前 GNN-for-HLS 工作仍不等价于本文任务。** 论文提到已有 GNN 用于 operation delay prediction 或受约束的 resource optimization，但通常针对单一 delay/资源目标、有限 pragma 类型，或为不同 regression targets 使用不同模型；它们没有把多种软件 construct 上的 pragmas、多个 FPGA resources 和整条 Pareto frontier 放进一个统一 DSE predictor。[pdf:E26]（PDF 物理页 17，Section 5，GNN related work 与本文差异）

因此，本文真正试图补的缺口是：**用能容纳任意程序拓扑的 graph representation，把程序结构与 pragma 配置共同编码，再用一个跨 design 的模型同时回归性能和资源，并通过少样本适配服务于多目标 Pareto DSE。** 这是论文的直接主张；是否能扩展到不同 compiler、technology library 和未见 pragma，则没有在本文中闭合验证。

## § 3 — 重建作者的思考路径

以下是基于全文证据的重建，不是作者逐句给出的历史叙述。

第一步，研究者先看到 HLS 的矛盾：行为级描述降低了 RTL 编写门槛，但每一组 directives 仍要经过昂贵综合才能知道 latency 与 area，配置空间又按 directives 的组合增长；因此 DSE 的核心不是生成更多候选，而是减少无价值 syntheses。[pdf:E02]（PDF 物理页 2，Section 1）[pdf:E03]（PDF 物理页 3，Fig. 1）

第二步，传统 vector encoding 很难跨程序复用。两个 functions 的 loop 数量、basic blocks、parameters、memory accesses 和 pragma targets 都不同，把它们压成同长度向量，要么丢结构，要么把 domain-specific slots 固化在输入中。Graph representation 则天然接受可变节点数与拓扑，并提供 permutation invariance 这样的 inductive bias。[pdf:E04]（PDF 物理页 4，Section 2.2）

第三步，HLS compiler 本身已经依赖 CFG/DFG 一类中间表示。于是合理的设计不是从 token sequence 直接学习，而是把 control flow、data dependencies、parameters 和 directives 放到与 HLS 决策相关的图上。作者进一步意识到，pragma 的作用对象是 loop、array、function 等具体 construct，所以 pragma values 应附着到对应 node，而不是作为与程序结构脱离的平面向量。[pdf:E05]（PDF 物理页 5，Fig. 2）[pdf:E06]（PDF 物理页 6，Section 3.1）

第四步，只做局部 message passing 仍可能把整个 program 压缩成信息瓶颈。作者因此保留 graph-level global attribute，并让它在每一层通过 attention 从 nodes 汇聚信息；这样模型既能处理局部 dependency，也能形成面向整个 configuration 的 latent representation。[pdf:E07]（PDF 物理页 7，Eq. (3) 与 Section 3.2）[pdf:E08]（PDF 物理页 8，Fig. 3）

第五步，有了跨 functions 的 predictor 后，最自然的 DSE 用法是先在历史 syntheses 上训练，再随机综合新 function 的一小部分配置做 fine-tuning，随后预测其余空间，只综合 estimated Pareto-optimal points。作者刻意采用简单 exploration policy，把实验重点放在“表示与 predictor 本身是否足够有用”，而不是把收益归因于复杂 search heuristic。[pdf:E10]（PDF 物理页 9，Fig. 4 与 Section 3.3）

## § 4 — 核心 Intuition

把一个 HLS implementation 看成“带 pragma 的 program graph”，而不是固定长度配置向量：相同的 message-passing rules 可以在不同节点数、不同拓扑的 programs 上复用。[pdf:E05]（PDF 物理页 5，Fig. 2）

Graph nodes/edges 表达 control、data 和 parameter dependencies，global state 表达当前配置在整个 design space 中的位置；GNN 通过局部传播和 global attention，把这些结构压成 latency/resource prediction。[pdf:E07]（PDF 物理页 7，Eq. (3)）[pdf:E08]（PDF 物理页 8，Fig. 3）

只要历史 designs 中学到的结构规律能迁移到目标 design，少量 target syntheses 就足以校正 predictor，随后可以在全空间中快速筛出接近真实 Pareto frontier 的候选。[pdf:E10]（PDF 物理页 9，Fig. 4）

## § 5 — 具体方法与完整 Pipeline

以论文贯穿全文的 `sum_scan` 为例，完整流程如下。

1. **定义 HLS design 与 configuration space。** 输入是 behavioral specification、pragma configuration，以及 HLS synthesis 所需的 technology library 和 target frequency；真实 HLS 输出是 RTL、latency 和 resource reports。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Section 2.1）在本文数据中，综合环境固定为 VivadoHLS 2018.2、ZynqMP UltraScale+ `xczu9eg`、target clock 10 ns。[pdf:E12]（PDF 物理页 10，Section 4）

2. **构建 Hybrid CDFG。** LLVM pass 先产生 CFG 并识别五类 coarse-grained blocks：loop、read、write、function、standard；Clang AST 与 source analysis 补回 LLVM IR 中丢失的类型、参数和 pragma 信息；Frama-C dependency analysis 提供 dataflow。作者再加入 parameter nodes，以及 control/data/param 三类 directed edges，形成 `G_hls`。[pdf:E05]（PDF 物理页 5，Fig. 2）[pdf:E06]（PDF 物理页 6，Section 3.1）

3. **编码 node、edge 与 configuration。** Node features 包括 block type、instruction/loop/function/parameter 特征和 pragma values；categorical values 用 one-hot，若干跨度大的数值用 logarithmic scale；edge type 也用 one-hot。论文称每个 node 有 27 个 attributes，但紧接着给出的分项是 node type 5、node attributes 14、pragma values 7，算术和为 26；源 PDF 未解释这一个维度差异，复现时必须以实际 feature schema 或代码为准。[pdf:E06]（PDF 物理页 6，Section 3.1）

4. **加入 graph-level configuration coordinate。** 论文统计配置空间中各 pragma type 的 mean/median，并与当前 configuration 的 mean/median 做差，再与 LLVM instruction count、input parameter count 串接成 global attribute `u`。直觉上，`u` 描述当前配置相对整个 design space 偏向哪一侧，而不是只描述某个局部 node。[pdf:E07]（PDF 物理页 7，Eq. (3)）

5. **运行 gnn4hls。** Encoder 用 MLP 分别映射 node、edge、global features；随后若干 propagation blocks 对 incoming messages 做 mean aggregation，并用 multi-head attention 更新 global representation；最终把 pooled node representation 与 global state 拼接，由 regression head 同时输出 latency 和 resource estimates。[pdf:E08]（PDF 物理页 8，Fig. 3）[pdf:E09]（PDF 物理页 8，Eq. (5)–(8)）实验实现使用四个 propagation blocks，node/global hidden sizes 分别为 128/256，每层两个 global attention heads；训练 target 取对数，Adam 训练 800 epochs，learning rate 0.001，batch size 128，gradient norm clip 为 3。[pdf:E13]（PDF 物理页 10，Section 4）

6. **从 predictor 转入 DSE。** Base model 先用其他已综合 designs 训练；对新 target function，随机综合约 5% 配置并 fine-tune，再预测剩余配置。论文把归一化 FF/LUT/DSP/BRAM utilization 的等权平均作为 aggregate cost，与 latency 一起寻找 estimated Pareto points；这些候选最终仍要真实综合，以取得可信结果。[pdf:E10]（PDF 物理页 9，Fig. 4）[pdf:E11]（PDF 物理页 9，Eq. (9)）

7. **执行平台与时间语义。** 这不是 time-stepping、switch/event 或 multi-rate numerical simulation 论文；所谓“时间”主要是 synthesized latency 与 target clock constraint。Model inference 在论文报告的平台上可用 Intel Xeon CPU 或 Nvidia Titan V GPU 执行，真实硬件映射则由上述 VivadoHLS/FPGA target 产生。[pdf:E12]（PDF 物理页 10，Section 4）[pdf:E16]（PDF 物理页 12，inference timing）

输出不是一份直接可用的 RTL 替代物，而是每个 configuration 的 latency/resource estimate、estimated Pareto set，以及对这些候选做真实 synthesis 后得到的实际 implementation reports。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有形式化公式，但不是 theorem/proof 型论文；数学主要定义 message passing、global attention、DSE cost 和评价指标，没有给出 predictor error 到 Pareto error 的理论界。

**1. 通用 MPNN。** 对 node `i`，第 `t` 层先收集邻居 `j` 经 message function 产生的信息，再用 permutation-invariant aggregation 和 update function 更新 node；global state 则从所有 nodes 聚合后更新：

\[
v_i^t=\tau_v^t\!\left(v_i^{t-1},\operatorname{AGGR}_v\{\psi_v^t(v_j^{t-1},v_i^{t-1},e_{j,i});(j,i)\in E\},u^{t-1}\right),
\]

\[
u^t=\tau_u^t\!\left(u^{t-1},\operatorname{AGGR}_u\{\psi_u^t(v_i^t,u^{t-1});i\in V\}\right).
\]

其工程意义是：同一套局部计算可作用于任意节点数与拓扑，aggregation 不依赖节点排列。[pdf:E04]（PDF 物理页 4，Eq. (1)–(2)）

**2. Configuration 的 global coordinate。** 论文定义

\[
u=l\parallel p\parallel(s-c)\parallel(s'-c'),
\]

其中 `l` 是 LLVM instruction count，`p` 是 input parameter count，`s/c` 分别是配置空间与当前 configuration 的 pragma-value mean，`s'/c'` 是对应 median，`\parallel` 表示 concatenation。差值经方差归一化后，给模型一个“当前点相对设计空间中心/中位位置”的坐标。[pdf:E07]（PDF 物理页 7，Eq. (3)）

**3. Node propagation 与 global attention。** 具体模型把邻居 node 与 encoded edge 拼接，经 MLP 后做 mean aggregation：

\[
v_i^t=\operatorname{MLP}_{\tau_v}^{t}\!\left(v_i^{t-1}\parallel\operatorname{MEAN}\{\operatorname{MLP}_{\psi_v}^{t}(v_j^{t-1}\parallel e_{j,i}^{enc});(j,i)\in E_{hls}\}\right).
\]

随后由 global state 和 node state 产生 attention logit，并在全图 nodes 上 softmax：

\[
r_i^t=\operatorname{MLP}_{\alpha}(u^{t-1},v_i^t),\qquad
\alpha_i^t=\frac{\exp(r_i^t)}{\sum_{j=1}^{N}\exp(r_j^t)}.
\]

最后把 attention-weighted node features 汇总到 global update：

\[
u^t=\operatorname{MLP}_{\tau_u}^{t}\!\left(u^{t-1}\parallel\operatorname{SUM}\{\alpha_i^t\odot\operatorname{MLP}_{\psi_u}^{t}(v_i^{t-1});i\in V_{hls}\}\right).
\]

核心 intuition 是让 global representation 在每层有选择地读取与当前 configuration 最相关的 blocks，避免一次性 global pooling 把所有节点压成单一平均值。[pdf:E09]（PDF 物理页 8，Eq. (5)–(8)）

**4. DSE 的 aggregate resource cost。** 候选筛选时，论文使用

\[
C=\frac{1}{4}\left(\frac{FF_{used}}{FF_{available}}+\frac{LUT_{used}}{LUT_{available}}+\frac{DSP_{used}}{DSP_{available}}+\frac{BRAM_{used}}{BRAM_{available}}\right).
\]

它把不同 resource types 先按器件容量归一化，再等权平均；因此 Pareto 搜索实际压缩了多种资源之间的差异，不能表达某一 resource 的硬约束或非等权业务价值。[pdf:E11]（PDF 物理页 9，Eq. (9)）

**5. Pareto approximation 的 ADRS。** 设 `P` 为 reference Pareto set，`\bar P` 为 estimated set，论文用

\[
\operatorname{ADRS}(\bar P,P)=\frac{1}{|P|}\sum_{p\in P}\min_{\bar p\in\bar P}d(\bar p,p),
\]

\[
d(\bar p,p)=\max\left\{0,\frac{A_{\bar p}-A_p}{A_p},\frac{L_{\bar p}-L_p}{L_p}\right\}.
\]

这里 `A` 与 `L` 分别表示 area/cost 和 latency；ADRS 越低越好，0 表示两条 Pareto frontiers 一致。[pdf:E18]（PDF 物理页 13，Eq. (10)–(11)）

**推导链的缺口。** Training objective 是 pointwise regression，而最终任务是 Pareto ranking。论文用实验说明低 prediction error 通常带来较低 ADRS，但没有证明 MAPE、局部排序错误与 ADRS 之间的必然关系；因此对 near-frontier small error 是否会放大，仍只能由 DSE experiments 判断。

## § 7 — 实验设计与结论

1. **问题：模型能否跨多个 functions 准确预测 latency/resources？ → 实验：** 作者从 MachSuite 的 23 个 functions 构建 103,093 个 configurations，固定 VivadoHLS 2018.2、ZynqMP `xczu9eg`、10 ns，按每个 function 的 70%/10%/20% 划分 train/validation/test；与参数量相近的 DeepSets/MLP baseline 比较，并运行五个随机 seeds。[pdf:E12]（PDF 物理页 10，Section 4）[pdf:E13]（PDF 物理页 10，training split 与 baseline）Table 1 给出每个 function 的 SLOC、pragma types、configuration-space size、最终 ADRS 与 relative speedup。[pdf:E14]（PDF 物理页 11，Table 1）**答案：** gnn4hls 的平均 MAPE 为 2.7%，baseline 为 15.4%，论文称提升超过 82%；latency MAPE 为 2.1%，与 HLScope+ 报告的 1.1% 做定性比较，FF/LUT/DSP errors 为 4.8%/2.6%/1.3%，低于 MPSeeker 论文报告的 14.7%/13.2%/12.7%。但 HLScope+ 与 MPSeeker 未开源，作者明确说明这不是同一实验条件下的直接 comparison。[pdf:E15]（PDF 物理页 11，Section 4，prediction results 与脚注）

2. **问题：surrogate 是否真的比综合/模拟快？ → 实验：** 在 Intel Xeon Silver 2.10 GHz CPU 上测单 configuration，在 Nvidia Titan V 上测完整 design space。[pdf:E16]（PDF 物理页 12，inference timing）**答案：** 论文报告约 10 ms/point；一个完整 design space 约 3.5 s，折合约 0.11 ms/design。这个数字只证明 network inference 很快，不包含 graph extraction、初始 target syntheses 或最终 Pareto candidates 的真实 HLS 时间。[pdf:E16]（PDF 物理页 12，inference timing）

3. **问题：Hybrid CDFG 的 edge types 是否必要？ → 实验：** 分别去掉 dataflow edges、parameter edges、以及两者同时去掉，保持 node types/attributes 不变。[pdf:E16]（PDF 物理页 12，Fig. 6 与 ablation text）**答案：** 完整 Hybrid CDFG 最好，去掉 parameter edges 的伤害明显；作者解释 parameter nodes 只通过 param edges 接入图，而部分 data dependencies 可以被 param/control paths 间接补偿。这支持了“parameter flow 是跨程序资源/性能预测的重要结构信号”。[pdf:E16]（PDF 物理页 12，Fig. 6 与 ablation text）

4. **问题：模型能否用少量 target syntheses 做 leave-one-function-out DSE？ → 实验：** Base model 用除 target 外的 functions 训练；target 随机综合 5%，上限 150 个 designs，fine-tuning 在所测场景少于 5 分钟。[pdf:E17]（PDF 物理页 12，DSE setting）用于 Fig. 7 的具体设置进一步把 target samples 限为最多 128 个、SGD updates 设为 150、batch size 32，并在 40 次独立 runs 上平均；候选 Pareto frontier 最多迭代估计五次。[pdf:E19]（PDF 物理页 13，Fig. 7–8）[pdf:E20]（PDF 物理页 13，DSE protocol/results）**答案：** fine-tuned model 的平均 ADRS 为 0.20，prior-knowledge baseline 为 0.45，论文报告改善 55%；平均 relative speedup 为 0.94×，1× 是可达上限。[pdf:E20]（PDF 物理页 13，DSE results）

5. **问题：prediction errors 能否通过多轮候选扩展缓解？ → 实验：** 每轮综合当前 estimated Pareto points，移除后重新计算下一层 Pareto neighborhood，最多五轮。[pdf:E19]（PDF 物理页 13，Fig. 8）**答案：** ADRS 随轮数下降，而 synthesis count 近似线性增加；相较 prior-knowledge 方法，gnn4hls 需要更多 syntheses，但能枚举整个 target space 的 estimates。作者把进一步降低 synthesis count 留给更先进的 exploration heuristic 或更大 dataset。[pdf:E21]（PDF 物理页 14，Fig. 8 discussion）

6. **问题：能否迁移到不同 clock conditions 与 application domains？ → 实验：** 对 `local_scan` 分别在 5/10/20/50 ns 下做 DSE；论文报告 ADRS 为 0.058/0.162/0.076/0.098，对应 94/89/92/91 次 syntheses。[pdf:E22]（PDF 物理页 14，Section 4.1）原文在同一段把 50 ns 写成等价 200 MHz，这与 period/frequency 的倒数关系不一致，复现应以明确的 clock period 字段为准。对 encryption domain，作者测试 `aes_addRoundKey` 与 `aes_addRoundKey_cpy`，ADRS 为 0.016/0.006，分别需要 37/29 次 syntheses，aggregate ADRS 为 0.011。[pdf:E23]（PDF 物理页 15，Fig. 9–10 与 domain-transfer results）**答案：** 这些结果支持有限的 clock/domain transfer，但外推范围受限：所有主要数据仍来自同一 HLS tool/FPGA；AES 也只选择 front-end 能处理且配置数足够的 functions，而作者脚注明确说当前 front-end 不支持 C `struct` 和 globally defined arrays。[pdf:E24]（PDF 物理页 15，footnote 4 与 Section 5 起始）

**总体结论。** 论文最有力的证据是：在统一 compiler/FPGA 环境和已知可综合配置集合中，Hybrid CDFG + GNN 的 prediction error、leave-one-out ADRS 与跨 domain adaptation 都优于所选 baselines。不能据此推出对任意 HLS tool、任意新 pragma、任意 C/C++ construct、post-place-and-route timing 或 energy 的同等有效性。

## § 8 — Take-aways

**5 句话：**

1. HLS DSE 的真正瓶颈是昂贵 synthesis 与指数级 configuration space，而不是缺少候选生成手段。[pdf:E02]（PDF 物理页 2，Section 1）
2. gnn4hls 用 Hybrid CDFG 把 control、data、parameter flows 和 pragma values 放进同一个可变拓扑表示。[pdf:E05]（PDF 物理页 5，Fig. 2）
3. Message passing 处理局部依赖，global attention 汇总与当前 configuration 最相关的 nodes，再回归 latency/resources。[pdf:E08]（PDF 物理页 8，Fig. 3）[pdf:E09]（PDF 物理页 8，Eq. (5)–(8)）
4. 在论文固定 tool/FPGA 的 23-function dataset 上，它显著优于 DeepSets baseline，并可用少量 target samples 做 Pareto DSE。[pdf:E15]（PDF 物理页 11，prediction results）[pdf:E20]（PDF 物理页 13，DSE results）
5. 最关键的未闭合问题不是 network capacity，而是表示中没有显式编码 compiler/technology/clock condition，却把可迁移性作为长期目标。

**3 句话：**

1. 本文把 HLS DSE 从“为每个 design 单独搜索”推进到“学习跨 program 的结构化 surrogate”。
2. Hybrid CDFG，尤其 parameter edges，是实验中最有证据支撑的结构贡献。[pdf:E16]（PDF 物理页 12，Fig. 6）
3. 结果很强，但 generality 目前只在受控数据、同一 compiler family 和少量可处理 domains 中成立。

**1 句话：** gnn4hls 证明了 program graph 可以成为 HLS DSE 的可迁移学习接口，但尚未证明这个接口足以唯一描述跨 compiler condition 的真实硬件结果。

## § 9 — 最脆弱的假设

最脆弱的假设是：**`G_hls`、node/edge pragma features 与 global vector `u` 已经包含了决定 latency/resources 的充分条件；在新 target 上，少量 fine-tuning 只需校准分布偏移，而不必补回缺失的因果变量。**

这个假设之所以是核心，是因为整个方法把 HLS outcome 写成一个从 graph/configuration 到数值结果的 deterministic regression problem。可是论文自己的 HLS flow 明确显示，结果还依赖 technology library 与 target frequency；`u` 只串接 instruction count、parameter count 和 configuration-space statistics，没有显式加入 tool version、device、library 或 clock。[pdf:E03]（PDF 物理页 3，Fig. 1）[pdf:E07]（PDF 物理页 7，Eq. (3)）主要实验又固定在 VivadoHLS 2018.2、同一 FPGA 和 10 ns 上。[pdf:E12]（PDF 物理页 10，Section 4）

论文为该假设提供的正面证据，是在不同 clock periods 和 AES domain 上分别 fine-tune 后仍得到较低 ADRS。[pdf:E22]（PDF 物理页 14，Section 4.1）[pdf:E23]（PDF 物理页 15，domain transfer）但这些实验本质上为每个 target condition 重新适配 weights，并没有证明一个 condition-aware model 能同时区分相同 program/configuration 在不同 clock、device 或 tool 下的多个 labels。当前 front-end 还不处理 `struct` 与 global arrays；作者也把 tool-version transfer、unseen pragmas 和跨 HLS tools adaptation 明确放在 future work。[pdf:E24]（PDF 物理页 15，footnote 4）[pdf:E27]（PDF 物理页 18，Section 6）

一旦这个假设不成立，prediction error 不只是“多一点 noise”，而会变成输入相同、标签不同的不可辨识问题；此时再强的 GNN 也只能把多个 compiler conditions 平均掉，Pareto ordering 会直接失真。

## § 10 — 最小复现实验

**要验证的最小 claim：** 在 unseen target function 上，Hybrid CDFG 的 parameter-flow structure 加上少量 fine-tuning，确实比结构更弱的模型更能恢复 Pareto ordering。

**数据。** 使用论文所述 db4hls synthesis records，不重做全部 HLS；从 Table 1 选择 `local_scan` 作为 target，其余 MachSuite functions 作为 source domains，保留每个 configuration 的 latency、FF、LUT、DSP ground truth。[pdf:E12]（PDF 物理页 10，dataset）[pdf:E14]（PDF 物理页 11，Table 1）

**实现。** 只做两个 graph variants：完整 Hybrid CDFG，以及去掉 parameter edges 的 ablation；两者使用相同 node features、相同四-block gnn4hls training recipe。若完整 front-end 成本过高，最小版本只需覆盖 target/source functions 实际出现的 loop/read/write/function/parameter nodes 和论文列出的 pragmas，不扩展到未报告 constructs。[pdf:E06]（PDF 物理页 6，representation）[pdf:E13]（PDF 物理页 10，model/training recipe）[pdf:E16]（PDF 物理页 12，ablation setup）

**协议。** 先 source-only train；再按论文 DSE setting 随机抽取 target 的 5%，并采用其细化实验中的最多 128 target points、150 次 SGD updates 进行 fine-tuning；用多个 random seeds 重复。[pdf:E17]（PDF 物理页 12，5% sampling）[pdf:E20]（PDF 物理页 13，fine-tuning details）

**测量。** 同时报告 pointwise MAPE、ADRS、estimated Pareto candidates 的 synthesis count，以及 best-latency relative speedup；ADRS 必须按 Eq. (10)–(11) 从完整 target ground truth 计算。[pdf:E18]（PDF 物理页 13，ADRS definition）[pdf:E20]（PDF 物理页 13，reported DSE metrics）

**支持结果。** 完整 Hybrid CDFG 在多数 seeds 上同时优于 zero-shot 和 no-parameter-edge variant，且低 ADRS 不是靠显著增加候选 syntheses 换来的；结果方向应与 Fig. 6、Fig. 7 一致。[pdf:E16]（PDF 物理页 12，Fig. 6）[pdf:E19]（PDF 物理页 13，Fig. 7）

**反驳结果。** 去掉 parameter edges 后 ADRS 没有稳定恶化，或 pointwise MAPE 变好但 Pareto ADRS 不改善，说明论文最重要的结构归因或“低回归误差足以指导 DSE”至少有一项不能复现。

## § 11 — 最强反例设计

最强反例不是再找一个更难 benchmark，而是构造一个**输入表示不可辨识**的场景。

论文的 HLS flow 表明，同一 behavioral specification 和同一 pragma configuration，在不同 technology library 或 target frequency 下可以产生不同 RTL、latency 和 cost。[pdf:E03]（PDF 物理页 3，Fig. 1）但 gnn4hls 的 graph/node features 和 global attribute 只编码 program、pragmas、instruction/parameter statistics 与 configuration-relative statistics，不编码 clock、device、library 或 tool identity。[pdf:E06]（PDF 物理页 6，Section 3.1）[pdf:E07]（PDF 物理页 7，Eq. (3)）

**反例实验：** 取论文已经重新综合过的 `local_scan` 配置，把 5/10/20/50 ns 四个 clock-period datasets 合并；对同一个 configuration，故意不给模型 clock condition。这样 `G_hls` 与 `u` 完全相同，却对应多组 latency/resource labels。训练一个单一 gnn4hls，并分别计算各 clock 下的 MAPE、ADRS 与 Pareto recall；再与“每个 clock 单独 fine-tune 一个模型”的论文设置比较。[pdf:E22]（PDF 物理页 14，clock-transfer experiment）

若单一模型出现不可消除的平均化误差，而分 clock fine-tuning 恢复性能，就说明成功来自“把 condition 吸收到一套独立 weights 中”，而不是表示本身捕捉了跨 condition 的 HLS mapping。这不会否定论文在单一环境内的结果，但会强力反驳任何把 gnn4hls 解读为“一个统一 predictor 可覆盖任意 configuration space”的主张，并把有效范围收缩为“每个 compiler condition 需要单独适配的 predictor”。

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty。** 本输入只包含该论文，未做外部相关全文检索；下面是由论文机制和实验约束推出的研究押注。

**主 idea：把静态 configuration regression 改写为可组合的 compiler graph-state dynamics。** 新问题不是“给定最终 pragma 组合，预测一个 latency/resource vector”，而是“每次 pragma intervention 和 compiler pass 如何把当前 IR/schedule/resource-binding graph 变成下一状态，多个转换能否组合到未见 directive combinations、未见 tool versions 和未见 target conditions”。这会首次使模型能够生成 counterfactual compilation trajectories：它不仅给出终点数值，还能指出某个 unroll、partition、inline 或 resource choice 通过哪一串 schedule/binding 变化形成最终 Pareto trade-off。

**核心机制与因果链。** 以论文 Hybrid CDFG 为初始 program state，加入 compiler pass 之后的 schedule、memory banking、operator binding 等中间 graph states；每个 pragma 或 compiler optimization 被视为作用于 graph 的 intervention。模型学习“前状态 + intervention → 后状态”，再从终态读取 latency/resources。若这种 transition operator 真能组合，未见 pragma 组合的结果应可由已见单步或短序列转换滚动得到，而不必把整个 configuration 当成一个不可分解的 black-box label。论文已经表明 control/data/parameter topology 有信息量，尤其 parameter edges 对 prediction 很关键；global attention 又提供了从局部结构汇聚到全局结果的计算骨架。[pdf:E05]（PDF 物理页 5，Fig. 2）[pdf:E08]（PDF 物理页 8，Fig. 3）[pdf:E09]（PDF 物理页 8，Eq. (5)–(8)）[pdf:E16]（PDF 物理页 12，Fig. 6）

**它改变的基本设计变量。** 状态表示从单个静态 Hybrid CDFG 变为跨 compiler passes 的 temporal multi-level graph；数据生成从只保存最终 synthesis outcome 变为保存受控 pragma interventions 的 pre/post states；研究目标从 pointwise metric regression 变为 transition composition 与 trajectory planning；系统边界从 source-level graph 扩展到 compiler schedule/binding internals。删除这些新增对象后，就退化回本文的一次性 endpoint predictor，基本能力会消失，而不是只少一个辅助模块。

**论文特异依据。** gnn4hls 在 5% target sampling 后可显著改善 ADRS，说明历史 designs 中确实存在可迁移结构；多轮 Pareto inference 又表明模型能提供全空间 estimates，而不仅是单个最优点。[pdf:E17]（PDF 物理页 12，target sampling）[pdf:E20]（PDF 物理页 13，DSE results）与此同时，所有主要训练都固定在一个 HLS tool/FPGA，front-end 仍遗漏部分 C constructs，作者也把 unseen pragmas、tool-version adaptation 和 model-based reinforcement-learning exploration 列为 future directions。[pdf:E12]（PDF 物理页 10，fixed synthesis environment）[pdf:E24]（PDF 物理页 15，front-end limitation）[pdf:E27]（PDF 物理页 18，future directions）这些细节共同指向：静态 endpoint representation 已显示潜力，但可组合的 compiler transformation mechanism 尚未被开发。

**最大收益与最大风险。** 最大收益是把 transfer 的对象从“某个训练好的 weight initialization”提升为“可复用的 compiler transformation primitives”，从而对未见 pragma combinations、tool releases 和 device conditions进行更少标签的规划，并能解释 Pareto change 是由 schedule、memory 或 operator binding 的哪一步造成。最大科学风险是 compiler state 可能不是 Markovian：隐藏 heuristics、global scheduling decisions 和不稳定 IR rewrites 会让相邻 passes 难以对齐，rollout error 也可能随序列迅速累积。

**首个证伪实验。** 在一个论文已有 kernel 上选 resource/partition/unroll/inline 中相互作用的 directives，记录若干 compiler-pass snapshots；训练 transition model，并把部分 compound combinations 完全留出。对照组是使用相同 terminal labels 的静态 gnn4hls。若 transition model 能在未见组合上同时预测中间 schedule/resource changes 和最终 Pareto ordering，而静态模型不能，才支持“转换可组合”这一机制；若优势只在加入更多中间监督后出现，或 rollout 在短序列中便崩溃，则最强替代解释是“额外标签提高了拟合”，而不是学到了可复用 dynamics。

**与论文所述最近路线的实质区别。** 本文与其引用的 learning-based/black-box methods 都把 synthesis outcome 作为终点标签；model-based methods 虽分析 compiler 行为，却依赖手工 analytical model；此前 GNN works 主要回归 delay 或受限资源。这里的 experimental object 是 compiler state transition，本体不是 scalar metric，也不是对静态 predictor 外接 search wrapper。[pdf:E25]（PDF 物理页 16，related-work categories）[pdf:E26]（PDF 物理页 17，GNN related work 与 gnn4hls difference）

**Wild-card alternative：** 把 experimental object 下沉到 post-place-and-route 的 timing/congestion/resource graph，学习以 technology library、device 和 clock 为条件的 Pareto design generator，使 HLS DSE 直接优化物理实现结果，而不是只优化综合阶段的 reports。
