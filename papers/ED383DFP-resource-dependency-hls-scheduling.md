# Resource Dependency-Aware Scheduling for High-Level Synthesis with GNN and SDC

- 作者：Aoxiang Qin、Minghua Shen、Nong Xiao
- 出处：2024 International Conference on Field Programmable Technology（ICFPT）
- 年份：2024
- DOI：10.1109/ICFPT64416.2024.11113459
- Zotero key：ED383DFP
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是 HLS 调度里一个很具体的难题：给定 data flow graph（DFG）、function unit（FU）类型与数量、操作延迟和总 latency 约束，应该给哪些无数据依赖的操作额外加上 resource dependency，才能让硬件复用 FU，同时又不过度串行化。resource dependency 并不是数据语义要求，而是调度器为了避免同周期争用同一个 FU 而人为建立的先后关系；它直接决定操作并行度、FU 数量和总 clock latency（CLC）。作者指出，完整搜索最优依赖集合需要指数时间；ILP 能求全局最优但扩展性弱，手工 heuristic 很快却容易制造多余依赖。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

工程价值在于，调度不是 HLS 流程里一个无关紧要的前端步骤。它会改变控制步数与资源共享，因而改变最终 accelerator 的 latency 和资源需求。论文试图在“用更多 FU 换并行”和“复用 FU 但延长关键路径”之间找到更好的点。作者报告的方法相对 DeepRL 平均减少 38.7% FU 使用，相对 NeuroSchedule 和 basic SDC 分别平均减少 8.5% 与 17.1% latency；这些是调度级指标，不是板级面积、频率、功耗或端到端执行时间。[pdf:E01]（PDF 物理页 1，Abstract）

## § 2 — 前人工作与不足

论文把已有路线分成三类。第一类是 multi-objective ILP：它把操作开始时间与资源冲突显式纳入整数优化，能通过 branch-and-bound 找到最优 schedule，但搜索空间随 DFG 增长而迅速膨胀。第二类是 list scheduling 等 handcrafted heuristic：它们用固定优先级和局部冲突规则快速决定依赖，却把本应全局权衡的资源复用问题过度简化。第三类是学习方法：DeepRL 直接近似 resource-dependency decision，NeuroSchedule 用 GNN 预测 list scheduling 的优先级；前者对未见 DFG 结构的近似精度没有保证，后者仍保留 list scheduling 的 heuristic dependency policy，所以只改优先级不能消除错误依赖。[pdf:E02]（PDF 物理页 1，Section I，prior work 与 contributions）

basic SDC 方法是作者最直接的基线。SDC 把 data dependency、resource dependency 和 latency 约束写成 difference constraints，再用线性规划最小化 latency。它的优势是约束矩阵 totally unimodular，因此在这种结构下可以得到整数解；问题出在进入 SDC 之前的 dependency transformation：先按统一 topological order 扫描同类 FU 的子序列，一旦计数超过资源上限，就把冲突对变成依赖。这种局部规则会加入不必要的边，并且为了消掉 resource-related variables，固定资源上限后也失去了联合优化 FU 数量的能力。[pdf:E03]（PDF 物理页 2，Section II-B 与 Section III 开头）

## § 3 — 重建作者的思考路径

下面是基于论文背景与结构重建的思考路径，不是作者逐字陈述。

1. ILP 的主要价值是它掌握全局 schedule，主要代价是组合搜索；basic SDC 的主要价值是求解快，主要损失并不来自 LP 本身，而来自 LP 之前把 resource conflict 变成 dependency 的 heuristic transformation。[pdf:E02]（PDF 物理页 1，Section I）
2. 因而不必让神经网络直接输出最终 schedule。更稳妥的分工是保留 SDC/LP 作为满足硬约束和优化 latency 的后端，只让 GNN学习 transformation 中最依赖 DFG 结构的部分。
3. 单一输出不足以同时控制资源与 latency：资源上限决定何时出现冲突，priority 决定先检查哪些操作，validity 决定候选依赖是否值得保留。因此把学习问题拆成三个 assistant tasks，分别预测 normalized resource constraint、priority distribution 和 pairwise dependency validity。[pdf:E05]（PDF 物理页 4，Fig. 3 与 Section IV-A/B）
4. 学习输出仍可能违反数据依赖、产生 self-loop 或 cycle，所以再用领域规则 post-process；最后将得到的依赖写入 SDC，用 LP 负责合法性与 latency minimization，并通过随机 threshold resampling 探索多个 dependency 子集。[pdf:E04]（PDF 物理页 3，Fig. 2(c) 与 Section III）

这条路线的关键选择不是“GNN 替代优化器”，而是“GNN 改写优化器的候选约束，SDC 决定约束下的 schedule”。它保留了符号优化的可解释硬约束，同时把最容易造成 heuristic loss 的前处理交给关系模型。

## § 4 — 核心 Intuition

普通 SDC 调度器像是先用一条固定队列猜哪些操作会抢同一台机器，再把猜到的冲突永久写成先后关系；猜错一条边，就可能把后续整条链一起推迟。本文让 GNN 先看 DFG 的局部与全局结构，针对当前图同时给出“可用多少 FU”“先看谁”“哪条依赖可信”三种提示，再让 SDC 在清理后的依赖集合中做数学优化。[pdf:E04]（PDF 物理页 3，Fig. 2）

真正起作用的机制是：学习模型不承担 schedule 的全部组合决策，而是改变 SDC 的约束生成空间。这样既能用结构信息少加坏边，又能通过 learned resource constraint 主动促进资源复用；但最终质量仍受 GNN 生成的候选空间限制。

## § 5 — 具体方法与完整 Pipeline

以 Fig. 2 的 9-operation DFG 为例：`o1`、`o5` 用延迟为 2 CLC 的 MUL，其余操作用延迟为 1 CLC 的 ADD，默认各有 2 个 FU，总 latency constraint 为 5 CLC。basic SDC 得到 5 CLC、2 MUL、2 ADD；本文方法得到 4 CLC、1 MUL、2 ADD，与图中的 optimal schedule 相同。[pdf:E04]（PDF 物理页 3，Fig. 2）完整 pipeline 如下。

1. **输入与初始时间窗。** 输入是 DFG、操作/FU 类型、每种 FU 的 delay 与约束，以及 latency constraint。ASAP 与 ALAP 先给每个操作的最早、最晚 CLC，并计算 ASAP 下每种 FU 的最大同时使用量。[pdf:E05]（PDF 物理页 4，Fig. 3-4）
2. **GNN 编码。** 每个 node 使用 6 个属性：predecessor 数、successor 数、对应 FU delay、ASAP 下该 FU 的 maximum usage、ASAP CLC、ALAP CLC；edge 属性是 source/destination 的 CLC difference。计数与 FU usage 按 operation 数归一化，ASAP/ALAP/CLC difference 按 latency constraint 归一化。bi-directional message passing 分别聚合 predecessor 与 successor 信息，并把不同尺度的 node embedding 汇成 program graph embedding。[pdf:E05]（PDF 物理页 4，Fig. 4 与 Section IV-B）
3. **三个 assistant tasks。** resource-constraint head 把 graph embedding 经 MLP 和 Sigmoid 输出每种 FU 的 normalized constraint；priority head 把 node embedding 经 MLP 和 Softmax 输出 operation priority distribution；validity head 对有方向的 node-pair embedding 做变换、内积和 Sigmoid，输出 dependency-validity matrix。[pdf:E06]（PDF 物理页 5，Fig. 5 与 Section IV-C(1)）
4. **领域 post-processing。** normalized constraint 乘 ASAP maximum FU usage 后 round 成整数资源上限。priority probability 排序成 operation order，再把违反 data dependency 的 predecessor 按 ASAP 顺序插回正确位置。validity matrix 清除 self-loop；对原始 data dependency 以及由 `ALAP(source) < ASAP(destination)` 推得的 derivative dependency，强制正向概率为 1、反向为 0。[pdf:E07]（PDF 物理页 5，Fig. 6 与 Section IV-C(1)）
5. **operation relation-aware transformation。** 按 learned priority 扫描同 FU 子序列，以 learned resource constraint 检测冲突，把冲突转成 candidate resource dependency。然后三次清理：删掉与 data dependency 冲突的边；用 breadth-first search 找 cycle，并删除满足 `ASAP(source) >= ALAP(destination)` 的第一条候选边；再采样一个 baseline probability，删掉 validity probability 低于该 threshold 的边。[pdf:E08]（PDF 物理页 6，Section IV-C(2)-(3)）
6. **SDC 求解与迭代。** 剩余 resource dependency、data dependency 和 latency constraint 组成 SDC，Cbc solver 最小化总 latency。随后重新采样 threshold，重复 pruning、SDC construction 和求解，直到达到 maximum iteration 或连续若干轮没有 performance increase。[pdf:E04]（PDF 物理页 3，Fig. 2(c)）
7. **监督训练。** 对 synthetic DFG 同时求 ASAP schedule 与 ILP schedule。ILP CLC order 产生 priority label；同 FU node pair 按 ILP schedule 产生 validity label，并对每个起始 CLC 只保留最小 CLC difference 的依赖；ILP/ASAP 的 FU-usage ratio 产生 normalized resource-constraint label。三个 loss 相加后更新 GNN 与 MLP。[pdf:E09]（PDF 物理页 6，Fig. 7 与 Section IV-E）

论文未报告开关器件、事件定位、数值积分、多速率时间推进、定点位宽、BRAM/LUT 映射、RTL 生成结果或实际 FPGA 板卡。实际训练平台是 Titan V GPU 加 24-core Intel Xeon CPU；因此本文证明的是 HLS DFG 的调度质量，不是 FPGA 上的 runtime、area、Fmax、power 或 HIL 实时性。[pdf:E10]（PDF 物理页 7，Section V-A 与 Table I-II）

## § 6 — 核心数学推导（无形式化数学则跳过）

SDC 的基本对象是 operation start CLC。一般 difference constraint 写成

\[
a_i x_i-a_j x_j\le b_{ij},\qquad a_i,a_j\in\{0,1\},\ b_{ij}\in\mathbb Z^+ .
\]

论文指出其系数矩阵 totally unimodular；直观上，每条约束只比较少数时间变量的差，因此线性目标下的 LP 极点可以保持整数，不必再为每个 start time 做组合枚举。[pdf:E03]（PDF 物理页 2，Section II-B）

若 resource dependency 为 `o_i -> o_j`，`x_i` 是 `o_i` 的开始 CLC，`d_i` 是它占用 FU 的 CLC 数，则加入

\[
x_i-x_j\le -d_i,
\]

等价于 `x_j >= x_i+d_i`，即 `o_j` 只能在 `o_i` 完成后启动。若 `L` 是总 latency，操作 `o_i` 的完成边界写成

\[
x_i-L\le 1-d_i,
\]

即 `x_i+d_i-1 <= L`。data dependency 用同类约束表示，线性目标最小化 `L`。[pdf:E08]（PDF 物理页 6，Section IV-D）

三个 supervised heads 使用不同损失：resource ratio 用 mean L1 loss，priority distribution 用 KL-divergence，validity matrix 用 weighted binary cross-entropy；三者直接相加。论文给出的 validity loss 对有效边加权，因为正样本只占 5%-10%。[pdf:E09]（PDF 物理页 6，Section IV-E，loss equations）这体现了三个输出的语义不同，但论文没有报告三个 loss 的相对尺度、权重敏感性，也没有证明“直接相加”对应最终 latency/FU 的 Pareto objective。

还需澄清“exact”的边界。给定一组已经选定的 difference constraints，SDC/LP 可以精确求该约束集内的最优整数 schedule；GNN 预测、heuristic conflict transformation、cycle pruning、random threshold 与有限次 resampling 仍在近似候选依赖空间。因此它不是对原始 HLS multi-objective scheduling 的全局最优证明。

## § 7 — 实验设计与结论

**问题 1：相比直接用 ML 近似 schedule，GNN-assisted SDC 是否更好？** 训练使用 200,000 个 synthetic DFG，每个 100-300 nodes、任意 node pair 以 0.5 概率连接；测试是从 LegUp、HLS-bench、PolyBench/C 产生的 10 个 benchmark DFG，规模 111-454 nodes、critical path 5-34 CLC。模型为 6-layer bi-directional GAT，训练 100 epochs、batch size 16、learning rate `1e-3`。[pdf:E10]（PDF 物理页 7，Table I-II 与 Section V-A）在 latency constraint `L=10L_cp`、每项平均 10 trials 的设置下，相对 DeepRL，本文平均减少 6.8% latency 和 38.7% FU；相对 NeuroSchedule，平均减少 8.5% latency 和 0.7% FU。[pdf:E11]（PDF 物理页 7，Fig. 8 与 Section V-B）

**问题 2：相比 LP-based 基线，learned transformation 是否弥补 basic SDC 的 heuristic loss？** 相对 basic SDC，本文平均减少 17.1% latency 和 0.7% FU；相对 optimal ILP，本文平均少用 14.0% FU，但 latency 高 12.3%。作者据此把方法定位为 limited solution space 内的 sub-optimal search，以资源换取更好的 scalability。[pdf:E12]（PDF 物理页 8，Fig. 9 与 Section V-C）但论文没有报告求解时间、memory、超时率或随 DFG size 的 scaling curve，所以“更可扩展”只由 formulation 和既有理论间接支持，没有被本组实验直接测量。

**问题 3：三个 assistant tasks 是否比单一 GNN 输出更有效？** 去掉 customized resource constraint、再把 baseline 手工调到 `0.22N_f^max` 后，完整方法在相同 FU 下平均少 6.1% latency。只保留 validity head 并以 0.5 threshold 直接决定依赖时，完整方法平均少 15.4% latency、少 70.84% FU。[pdf:E12]（PDF 物理页 8，Section V-D）这支持“GNN 作为多头 assistant，而不是直接决策器”的设计；但 No_Res_Const 与 SDC、NeuroSchedule 的 resource constraint 都经过手工调节，公平性取决于调参预算是否一致。

**问题 4：GNN 配置是否重要？** 6-layer bi-directional GAT 相比 GCN 平均少 36.4% latency、但多 3.8% FU；相比 GINE 平均少 22.4% latency、少 45.8% FU。6 layers 相比 3 layers 和 9 layers，分别报告 37.6%/53.9% latency reduction 与 0.7%/32.9% resource reduction。[pdf:E13]（PDF 物理页 8，Fig. 10 后的 hyperparameter study）这说明结果对 architecture/depth 高度敏感，也提醒我们不能把“GNN”视作无条件稳健的结构感知器。

不得外推的结论包括：没有板级 FPGA 资源、时序、功耗或 compilation runtime；没有真实完整 application 的端到端 HLS QoR；没有证明对所有 DFG 结构都优于 basic SDC；没有证明 random resampling 能覆盖全局最优 dependency set。

## § 8 — Take-aways

**5 句话：**

1. resource dependency 是 HLS 调度里连接并行度与 FU 复用的关键人工约束，错加一条边就可能延长整条依赖链。[pdf:E03]（PDF 物理页 2，Fig. 1 与 Section III）
2. 本文最重要的设计不是用 GNN 端到端替代调度器，而是让 GNN 产生 resource constraint、priority 和 validity 三类提示，再由 SDC/LP 做合法优化。[pdf:E05]（PDF 物理页 4，Fig. 3）
3. Fig. 2 的例子直观展示了这种分工：删掉坏边并加入有利于 FU 复用的边，可从 basic SDC 的 5 CLC、2 MUL 改为 4 CLC、1 MUL。[pdf:E04]（PDF 物理页 3，Fig. 2）
4. 10 个 benchmark DFG 上的结果支持它优于论文选取的 RL、GNN 和 basic SDC 基线，但相对 ILP 仍以 12.3% latency increase 换 14.0% FU reduction。[pdf:E11] [pdf:E12]（PDF 物理页 7-8，Fig. 8-9）
5. 最大证据缺口是没有 runtime/scaling 与板级 QoR，也没有针对 synthetic-to-real structural shift 的系统压力测试。

**3 句话：** GNN 被放在 constraint generation 而不是 final solving 的位置，是本文最值得复用的架构思想。SDC 保证给定候选约束下的合法与最优，但不保证 GNN/heuristic 产生了全局正确的候选空间。实验显示了 latency/FU 改善，却没有闭合 scalability 和真实 FPGA 实现证据。

**1 句话：** 这是一种“学习候选依赖、符号优化 schedule”的混合 HLS 调度器，而不是一个已经证明全局最优或板级更快的 FPGA 工具。

## § 9 — 最脆弱的假设

最脆弱的假设是：**从 100-300-node、pair-link probability 为 0.5 的 synthetic DFG 学到的三个 assistant outputs，能在未见真实 DFG 结构和资源预算上仍把全局好 schedule 留在 SDC 的候选空间里。** 只要 learned resource constraint 过紧、priority 把关键并行 operation 排错，或 validity/pruning 删掉必要边、保留有害边，后面的 SDC 即使精确求解，也只能精确地优化一个错误或过窄的空间。[pdf:E10]（PDF 物理页 7，Section V-A）

论文给出的支持是：10 个由真实 benchmark program 生成的 DFG，node 数跨到 454；这些图上平均优于 DeepRL、NeuroSchedule 和 basic SDC。[pdf:E11]（PDF 物理页 7，Fig. 8）但证据仍不够，因为没有报告 synthetic 与 benchmark 的 degree、motif、critical-path width、FU-type distribution 的距离，没有按结构 OOD 分组，也没有把 random resampling 的成功率与 iteration budget 拆开。更关键的是，作者声称 SDC optimization 不依赖 DFG 特征，而实验改进来自进入 SDC 前的 learned candidate construction；两者不能混为同一个 guarantee。

## § 10 — 最小复现实验

一周内不复现整套 200,000-graph 训练，而做一个可证伪“multi-head assistant 比 direct validity 或 basic SDC 更能保留好依赖空间”的小实验。

- **数据：** 从论文 Table II 选 4 个规模梯度明显的 DFG，例如 B1、B6、B9、B10；另生成 5,000 个 100-300-node synthetic DAG，明确固定随机种子、FU type、delay 与 `p=0.5`。latency constraint 设为 `10L_cp`，每种 FU 的初始上限使用 ASAP maximum usage。[pdf:E10]（PDF 物理页 7，Table II 与 Section V-A）
- **实现：** 用同一 Cbc backend 实现 ILP labeler、basic SDC、6-layer bi-directional GAT 的三个 heads，以及 `Validity_only`。保留论文的 data-dependency fixing、cycle pruning 和 threshold resampling；把 resampling iteration 固定并公开。
- **测量：** 对每个 DFG 记录 CLC latency、每类与总 FU、与 ILP 的 latency/FU gap、产生/删除的 dependency 数、cycle 数、solver time 与 end-to-end scheduling time。baseline 的 resource constraint 用同一搜索预算调参，不能只替某一方手工调到匹配资源。
- **支持标准：** 在四个 held-out DFG 上，完整方法在相同或更少 FU 下均不差于 basic SDC，平均 latency gap 至少改善 5%，且相对 `Validity_only` 的优势在不同随机种子下方向一致。
- **反驳标准：** 只要优势依赖某个手工资源系数、换随机种子后消失，或加入 GNN/resampling 后 end-to-end runtime 反而超过小规模 ILP 却没有 QoR 优势，就不能支持论文的核心工程 claim。

## § 11 — 最强反例设计

最强攻击不是再随机生成同分布图，而是构造训练分布看不到、但 HLS 常见的结构族：极长单链、超宽 fork-join、规则 stencil pipeline、稀疏多层 reduction tree，以及 node 数大于 454、FU delay 高度异构的 DFG。训练仍只用论文的 100-300-node、`p=0.5` synthetic graph；测试时按结构族逐步增加 depth、width 与 critical-path/FU-pressure ratio。[pdf:E10]（PDF 物理页 7，training/test settings）

对每个图同时运行 ILP、basic SDC、本文方法，并固定相同 resource budget 与 solver timeout。攻击指标不是平均 latency，而是：GNN priority 是否把 critical-path operation 排到资源冲突之后；6-layer message passing 是否看不到超过 receptive field 的远程竞争；validity threshold 是否系统地保留 shortcut-like 坏边；resampling 是否在给定次数内仍找不到 ILP dependency skeleton。如果本文方法在某一结构族上持续比 basic SDC 更慢或使用更多 FU，而 ILP 仍能给出明显更好的 schedule，就说明结果可由 synthetic generator 与 benchmark selection 的结构相似性解释，而不是一般的 operation-relation awareness。论文现有实验没有排除这个替代解释。

## § 12 — Follow-up Research Bet

### 主押注：面向资源预算族的“参数化依赖基”调度

**新能力。** 不再为一个固定 resource constraint 只生成一份 schedule，而是从一个 DFG 一次性抽取一组可复用的 dependency basis，使编译器能在 latency budget 或可用 FU 数变化时，立即实例化整条 resource-latency Pareto family。新的研究问题是：能否学习一个小而完备的 resource-dependency basis，使 SDC 对一整个预算区间都能生成合法、接近 ILP 的 schedule，而无需为每个预算重新做随机 threshold search？这把研究目标从“单实例 QoR”改为“预算变化下的 schedule family”，也把表示从 pairwise validity probability 改为带 activation interval 的 dependency basis。

**因果机制。** 论文已经证明三个 assistant outputs 控制冲突出现、候选顺序和边保留，且 ILP schedule 可以为这些输出产生监督标签。[pdf:E05] [pdf:E09]（PDF 物理页 4、6，Fig. 3 与 Fig. 7）新的机制是对同一 DFG 在多个 FU budgets 上求一组 ILP/SDC counterfactual schedules，找出跨预算反复出现的 dependency chains 与只在特定 budget interval 激活的边；GNN 输出的不再是一张 validity matrix，而是若干 dependency basis elements 及其 budget activation intervals。SDC backend 根据当前 budget 激活对应 basis，直接求 schedule。因果链为：跨预算 counterfactual labels -> 学到稳定依赖骨架与边的激活区间 -> 候选空间随 budget 有结构地变化 -> 一次编译得到可重配置 schedule family。

**基本设计变量变化。** 第一，任务对象从单一 DFG+单一 resource constraint 变为 DFG+resource-budget interval；第二，状态表示从 node-pair probability 与随机 threshold 变为 dependency basis+activation interval；第三，数据生成从每图一份 ILP label 变为每图跨预算的 counterfactual ILP trajectories；第四，评价对象从单点 latency/FU 平均值变为整条 Pareto curve 的 coverage、regret 与切换成本。

**论文特异依据。** 方法侧，resource-constraint head 本来就把 graph embedding 映射成每类 FU 的 normalized constraint，Fig. 7 又显示 ILP/ASAP ratio 可作为资源标签；这说明“预算”已经隐含在标签生成中，只是被压成一个点。[pdf:E06] [pdf:E09]（PDF 物理页 5-6，Fig. 5 与 Fig. 7）实验侧，本文相对 ILP 的结果本身就是明显的 resource-latency trade-off：平均少 14.0% FU、代价是 12.3% latency increase；baseline 还需要把 resource constraint 手工调到 `0.24N_f^max` 或 `0.22N_f^max` 才能公平比较，暴露了单点预算调参这一未开发自由度。[pdf:E11] [pdf:E12]（PDF 物理页 7-8，Section V-B-D）

**收益与风险。** 最大收益是让 HLS 调度从“每个器件/负载重新搜索”变成“同一 accelerator family 可按可用 DSP/ALU 或 latency SLA 快速重配置”，并提供比单点平均值更完整的设计空间。最大科学风险是 dependency basis 的规模可能随 DFG 或 FU types 指数增长，所谓 activation interval 也可能不是连续的；若如此，这个表示不会比逐预算求解更紧凑。

**首个区分实验。** 对 Table II 的 10 个 DFG，把每类 FU budget 从 ASAP maximum 的 20%-100% 离散为 9 个点。比较三种方法：每个点独立运行本文 random-resampling 方法、从一个预算迁移 dependency set、学习 dependency basis。主要指标是相对 ILP Pareto front 的 hypervolume regret、跨预算复用的 dependency 比例、basis size、总编译时间。若小 basis 在未见 budget 上仍保持低 regret，说明“跨预算稳定依赖结构”是真机制；若性能只来自在所有预算上重复求解或 basis 大到接近所有 pairwise edges，则替代解释成立，押注失败。由于尚未检索相关全文，这里只把它标为候选研究方向，不声称 novelty。

**Wild-card alternative：** 把 associative/commutative operator rewrite 也作为可控变量，让模型先改变 DFG 的代数拓扑、再由 SDC 调度；这不是在原方法上加监测器，而是把 experimental object 从“固定 DFG 的依赖选择”改为“计算图重写与 FU 依赖的联合生成”。
