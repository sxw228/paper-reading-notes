# Comprehensive Mapping of Continuous/Switching Circuits in CCM and DCM to Machine Learning Domain Using Homogeneous Graph Neural Networks

- 作者：Ahmed K. Khamis；Mohammed Agamy [pdf:E01]（PDF 物理页 1，题名与作者栏）
- 出处：IEEE Open Journal of Circuits and Systems，Volume 4 [pdf:E01]（PDF 物理页 1，页眉与页脚）
- 年份：2023 [pdf:E01]（PDF 物理页 1，出版信息）
- DOI：10.1109/OJCAS.2023.3234244 [pdf:E01]（PDF 物理页 1，题名上方 DOI）
- Zotero key：SWBQS25Q
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“用哪一种 neural network 预测某个电路指标”，而是更前置的问题：怎样把元件数可变、连接次序可变、既可能连续又可能开关、还可能处在 CCM 或 DCM 的电路，统一变成机器学习可以接收的图输入。作者希望这种表示同时保留元件类型、元件值、串并联关系和运行模式，并且输入维度不随电路规模固定；摘要将其概括为一种不依赖连接形式或元件数量的 circuit-to-graph 映射，并在 7 类连续电路与 Buck、Boost、Buck-Boost 三类变换器上做 proof of concept [pdf:E01]（PDF 物理页 1，Abstract）。

这个问题重要，是因为普通 neural network 的固定尺寸输入与“电路节点数没有先验上界”直接冲突。论文把 permutation invariance 和 scalability 明确列为电路表示的要求：元件输入顺序变化不应改变电路含义，而新增元件也不应迫使模型重新定义输入层 [pdf:E02]（PDF 物理页 2，Section II-A）。从工程上看，如果表示层丢掉连接关系，后续做 design automation、condition monitoring 或性能预测时，模型可能把拓扑不同但数值向量相似的电路视为同一对象。

需要先划清结果边界。论文实证证明的是“给定作者构造的数据和类别，图分类器能够识别电路类别及 CCM/DCM 标签”，不是动态电磁暂态模型、控制器、实时数字孪生或可综合 FPGA 核。摘要报告 continuous circuits 的 97.37% 和 switching circuits 的 100% classification accuracy [pdf:E01]（PDF 物理页 1，Abstract）；这些数字不能直接解释为电压、电流或开关波形的预测精度。

## § 2 — 前人工作与不足

以下是论文对相关文献的归纳，未在本卡中对每篇被引论文做独立复核。作者比较了三条表示路线：一般 graph theory、Y-matrix 与 bond graph。论文认为一般图表示直观但可能丢失非线性、开关和连接物理；Y-matrix 计算紧凑，却会把并联支路合并成等效导纳，使“增加元件”和“改变元件值”难以区分；bond graph 则显式提供 0/1 junction、能量变量与跨物理域的结构表示 [pdf:E03]（PDF 物理页 5，Table 2 及其相邻正文）。

作者还梳理了已有 circuit-GNN：一些工作只拼接输入/输出节点 embedding，一些把元件与 pin/net 做成 heterogeneous multigraph，一些只面向固定拓扑的参数优化。论文批评这些方法通常没有统一的电路定律基础，容易遗漏串联共享电流、并联共享电压等连接语义，或用更多 node/edge types 和更深网络补偿表示缺口 [pdf:E04]（PDF 物理页 6，Table 3 前半与相邻正文）[pdf:E05]（PDF 物理页 7，Table 3 后半与 Section V 总结）。

这篇论文改变的关键假设是：不把 schematic 中的“元件直接相连”当作唯一图结构，而先把电路变成 bond graph，再把元件、0-junction、1-junction 和 switched junction 全部当作同一种图节点。所谓 homogeneous GNN，是指网络只处理统一 node/edge type；元件或连接角色的差异被编码进 node features，而不是为每类器件建立独立的异构消息传递规则。这个选择降低了图类型复杂度，但是否能保留所有动态与非线性信息，论文只通过分类任务做了有限验证。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，不是作者逐字陈述。

第一步，研究者会发现固定长度向量或图像输入难以同时容纳不同阶数、不同元件数的电路；即使 padding 到统一尺寸，也会引入额外计算，并且仍未天然表达电路同构不变性 [pdf:E02]（PDF 物理页 2，Section II）。第二步，直接把 netlist 画成“元件为节点、导线为边”的图虽然简单，却没有显式说明 series/parallel 的物理语义；用 heterogeneous graph 加 pin/net 节点可以补信息，但代价是图更大、类型更多，而且仍可能出现结构同构歧义 [pdf:E05]（PDF 物理页 7，Section V）。

第三步，bond graph 已经用 0-junction 和 1-junction表达共同 effort/flow 关系，并有 switched power junction 表达开关，所以它可以作为 circuit laws 与 GNN 之间的中间语言。作者于是把问题拆成三段：先用 bond graph 重写拓扑，再建立统一 node/edge feature schema，最后用 permutation-invariant GCN 做 graph-level prediction [pdf:E06]（PDF 物理页 8，Section VI 与 Fig. 2）。第四步，为避免一开始就把表示层和复杂任务纠缠，作者选择易观测的分类作为 proof of concept：若模型能区分相近拓扑以及 CCM/DCM，至少说明表示里包含了某些拓扑与运行模式信息。

这条思路合理，但“分类成功”与“表示足以支持任意建模、控制、综合任务”之间仍有很大距离。分类器可以利用与标签相关但与电路动态不等价的统计特征；论文没有通过 trajectory prediction、held-out topology 或闭环控制来排除这种替代解释。

## § 4 — 核心 Intuition

核心 intuition 是：先把电路翻译成一种遵守连接物理的 bond graph，再让 GCN 沿这些物理连接传递消息；这样，电路有多少元件、节点如何编号，都不需要改变 neural network 的输入定义。连续、开关、CCM、DCM 的区别不靠更换模型，而靠 switched junction、虚拟开关、duty cycle、frequency、phase shift 和元件值等图特征进入同一表示 [pdf:E07]（PDF 物理页 9，Fig. 3、Table 5 与 DCM 正文）。

## § 5 — 具体方法与完整 Pipeline

以 Buck 变换器为例，完整 pipeline 可以还原为以下五步。

1. **从电路到 bond graph。** 对连续电路，作者为电压连接点和元件建立 0/1 junction 结构；Fig. 2 展示了二至四阶、共 7 类 resonant circuits 的 circuit-to-bond-graph 转换 [pdf:E06]（PDF 物理页 8，Section VI-A1 与 Fig. 2）。对开关电路，SPST 被表示为 switched junction 与 zero-valued flow source；Buck、Boost、Buck-Boost 在 CCM 下的完整 bond graph 见 Fig. 5 [pdf:E08]（PDF 物理页 10，Fig. 5）。
2. **显式编码 CCM/DCM 与开关模式。** CCM 由正常互补开关状态表示；DCM 则加入 virtual switch：当电感电流先于周期结束降为零、两个主开关均关断时，第三个互斥状态 \(D_3\) 表示零电流区间。作者同时把 duty cycle 放在连接 switched nodes 的 edge features 中，把 switching frequency 与 phase shift 放在控制源相关 node features 中 [pdf:E07]（PDF 物理页 9，Section VI-A2、VI-B 与 Table 5）。这是对运行模式的结构化编码，不是对开关瞬态的数值积分器。
3. **从 bond graph 到 homogeneous graph。** 图节点统一包含 circuit elements、0/1 junction 与 switched junction，边表示连接。连续电路的 edge feature 设为 1；node feature 由元件类别的 one-hot Element ID 与 normalized values vector 拼接，形成 \(N\times d_{in}\) feature matrix [pdf:E09]（PDF 物理页 11，Fig. 7、Fig. 8、Table 6 与 Section VI-C1）。
4. **生成并保存数据。** 作者对不同元件值和 operating points 做 steady-state computer simulations，把节点电压、回路电流等结果归一化后写入 graph dataframe；随后转换为具体 graph-ML library 可读的格式。实现选择了 PyTorch-Geometric [pdf:E09]（PDF 物理页 11，Section VI-C2）。论文没有报告 simulator 名称、元件取值范围、随机种子、batch size、处理器/GPU、数据生成代码或公开数据集，因此不能据此精确重建原始数据。
5. **GCN 分类。** 三层 GCN 让每个节点聚合到三跳邻域，作者解释三层是 exploration depth 与计算成本之间的折中 [pdf:E10]（PDF 物理页 12，Section VI-E 与 Fig. 10）。训练前，作者先在 6000 个 continuous-circuit graphs 上安排 12 组 feature experiments [pdf:E11]（PDF 物理页 13，Section VI-G），再据结果确定 capacitor 用 \(1/C\)、edge weight 用 1 的表示 [pdf:E12]（PDF 物理页 14，Fig. 11–13）。定稿的 classifier 结构由 Fig. 15 概括 [pdf:E13]（PDF 物理页 15，Fig. 15）：global mean readout 得到 graph-level embedding，fully connected layer 加 Softmax 输出电路类别概率，完整映射见 Eq. 3–11 [pdf:E14]（PDF 物理页 16，Section VII-1）。

预测对象必须准确表述：continuous case 输出 7 类 resonant topology 的类别；switching case 输出 6 类，即 Buck/Boost/Buck-Boost 各自的 CCM 或 DCM 标签。模型没有输出连续时间波形、器件损耗、稳定裕度或控制量。

实际推理平台也必须准确表述：论文只说明用 PyTorch-Geometric 构建 GNN；没有报告 CPU/GPU 型号、embedded target、FPGA、定点位宽、内存、LUT/DSP/BRAM、功耗、吞吐或 latency。论文提到 GCN 的简单实现“可能有利于”microcontroller digital twin，只是设计动机而非部署实证 [pdf:E10]（PDF 物理页 12，Section VI-E）。因此不能把这份软件分类模型直接外推为 FPGA 可部署。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学不是电路状态方程推导，而是 GCN 更新、复杂度与 classifier readout 的形式化。

输入特征先经 embedding：

\[
X^{(0)}=E(X).
\]

第 \(l\) 层的更新为：

\[
X^{(l+1)}
=\sigma\!\left(\hat D^{-1/2}\hat A\hat D^{-1/2}X^l\Theta^l\right),
\qquad \hat A=A+I.
\]

其中 \(A\) 是 adjacency matrix，加入 \(I\) 后每个节点也接收自身消息；\(\hat D^{-1/2}\hat A\hat D^{-1/2}\) 做对称归一化，避免高度数节点的数值尺度支配更新；\(\Theta^l\) 是该层可学习权重，\(\sigma\) 是非线性激活。直觉上，每一层把“一跳邻居告诉我的信息”与自身状态混合，三层后节点看到三跳范围 [pdf:E11]（PDF 物理页 13，Eq. 1–2 与 Fig. 10）。

对 \(N\) 个节点、feature width \(F\)、\(E\) 条边和 \(L\) 层，作者给出 sparse message passing 的总时间复杂度：

\[
O(LNF^2+LEF).
\]

这里 \(LNF^2\) 来自 feature transformation，\(LEF\) 来自沿边聚合。参数量不直接绑定 \(N\)，所以同一个网络可以接收不同大小的图；但运行时间与内存仍会随节点、边和 feature width 增长。论文自己明确说理论上电路阶数无上限，实践限制来自计算时间与 RAM [pdf:E11]（PDF 物理页 13，Section VI-F）。

图级分类则可写成 \(Y=\mathrm{classifier}(X,A)\)，经过 GCN、global mean readout、fully connected layer 与 Softmax，再用 cross-entropy 训练 [pdf:E14]（PDF 物理页 16，Eq. 3–11）。这些式子说明模型尺寸如何与图尺寸解耦，却没有证明 bond-graph features 对所有电路任务都信息完备，也没有给出数值稳定性、误差界或动态系统一致性定理。

## § 7 — 实验设计与结论

**问题一：元件值与边特征怎样编码，分类才更容易？ → 实验：** 作者在 7 类 continuous circuits 的 6000 个图上做 12 组 feature experiments；70% 用于训练，数据先 shuffle，训练与测试不共享样本，loss 为 cross-entropy，optimizer 为 Adam，learning rate 为 0.02 [pdf:E11]（PDF 物理页 13，Section VI-G）。**答案：** edge weight 设为 1、capacitor 的数值特征改为 \(1/C\) 时表现最好；把 edge feature 当 scaling factor 或把 inductor 写成 \(1/L\) 会变差 [pdf:E12]（PDF 物理页 14，Fig. 11–13 与相邻正文）。这说明特征工程影响很大，也说明高准确率并非单由 topology representation 保证。

**问题二：同一表示能否区分不同阶数的连续电路？ → 实验：** 分类难度从 4 类、5 类增加到 7 类，最终数据包含 6000 个 graph/steady-state simulation；三层 GCN 预测 graph class [pdf:E13]（PDF 物理页 15，Fig. 14、Fig. 15 与 Section VII）。**答案：** 4 类训练 accuracy 为 92.3%，5 类为 95.92%，7 类训练与测试 accuracy 分别为 97.37% 和 97.10%，训练 1200 epochs [pdf:E13]（PDF 物理页 15，Fig. 14 相邻正文）[pdf:E14]（PDF 物理页 16，Fig. 16 与 Table 7）。主要错误集中在相近的 class 2 与 class 3：class 2 recall 0.77，52 个 class-2 graph 被判成 class 3 [pdf:E15]（PDF 物理页 17，Fig. 18 与相邻正文）。

**问题三：同一框架能否同时区分拓扑与 CCM/DCM？ → 实验：** Buck、Boost、Buck-Boost 各分 CCM/DCM，共 6 类，训练 200 epochs；混淆矩阵和 Table 8 对 6 类均给出 precision、recall、F1 为 1.00 [pdf:E15]（PDF 物理页 17，Fig. 19、Table 8 与 switching classifier 正文）。**答案：** 作者报告 training/testing accuracy 都为 100%，Fig. 20 的二维 embedding 也把三个变换器及两种模式分群 [pdf:E16]（PDF 物理页 18，Fig. 20）。

这里存在一个应保留的内部不一致：正文说 Fig. 20 展示 1800 个 switching test graphs [pdf:E15]（PDF 物理页 17，switching classifier 正文），但 Table 8 的 support 合计为 6075 [pdf:E15]（同页 Table 8）；continuous 数据声称 6000 个、70/30 split，而 Table 7 的 test support 合计为 1792，不是按比例推得的 1800 [pdf:E14]（PDF 物理页 16，Table 7）。原文没有解释差额、重复采样或两套 evaluation set 的关系。

泛化范围因此要收紧：这些结果支持的是“在作者枚举的 7 类连续电路和 3 种 DC-DC topology、同类数据分布的切分下可以高精度分类”。论文没有做 held-out topology、比四阶更大电路、未见过的开关单元、多变换器耦合、强参数外推、噪声、寄生参数、器件非理想、动态工况迁移或跨 simulator 验证。所谓“任意电路”和“可用于多种 ML tasks”是方法目标与外推性主张，不是被这些实验完整验证的结论。

资源和实时性方面，论文只给出渐近复杂度，没有 wall-clock training/inference time、峰值 RAM、模型参数量、功耗、硬件资源或 deadline 测试 [pdf:E11]（PDF 物理页 13，Section VI-F）。因此没有证据回答 FPGA resource、latency 或实时步长。

## § 8 — Take-aways

**5 句话：**

1. 论文提供了一条 circuit → bond graph → homogeneous graph → GCN 的统一表示路线。
2. continuous circuit 用元件与 0/1 junction 表示结构，switching circuit 进一步用 switched junction、duty cycle、frequency、phase shift 和 DCM virtual switch 表示运行模式。
3. 三层 GCN 在作者枚举的数据上达到 continuous 97.10% testing accuracy，并对 6 类 converter/mode 报告 100% [pdf:E14]（PDF 物理页 16，Fig. 16）[pdf:E15]（PDF 物理页 17，Table 8）。
4. 结果证明了分类可行性，却没有证明动态建模、控制、拓扑生成或任意规模泛化。
5. 论文使用 PyTorch-Geometric 软件实现且未报告 FPGA、资源或 latency，所以硬件可部署性仍是未知。

**3 句话：** 这项工作的价值主要在表示层：用 bond graph 把电路物理连接变成 GNN 可消费的结构。分类结果说明该表示含有足以区分所测 topology/mode 的信息，但数据切分、规模外推和数据集计数存在未闭合处。它是后续 data-driven circuit modeling 的候选前端，不是已经验证的实时仿真或 FPGA 方案。

**1 句话：** 论文证明“物理启发图表示可做电路类别识别”，尚未证明“同一图模型能准确、稳定、实时地预测未见电路动态”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**统一的 bond-graph topology 加归一化 node/edge features，不仅能在已枚举类别内区分标签，而且足以支撑对未见拓扑、未见规模和未见工况的电路任务泛化。** 如果这个假设不成立，“scalable、topology agnostic、可用于任意 ML task”的核心价值会退化成一套只对当前分类数据有效的手工 feature engineering。

论文给出的支持是：7 类连续电路和 3 类变换器的随机样本切分上，类间 embedding 大多分离；同时，class 2/3 的混淆显示表示确实对相似连接更敏感 [pdf:E15]（PDF 物理页 17，Fig. 18 与正文）。但缺失的证据更关键：没有按 topology、order、component range、control law 或 simulator 做 group-held-out split；没有动态 trajectory 预测；没有测试寄生、饱和、dead time、器件非线性、mode boundary 抖动；也没有验证 virtual switch 的 DCM 编码在边界导通模式下仍保持物理一致。

此外，作者的未来工作讨论本身承认 ML model 依赖 network depth、neurons、activation、pooling 等 hyperparameters，设计过程仍需要 fine-tuning [pdf:E16]（PDF 物理页 18，Section VIII）。这进一步说明“图表示统一”不等于“模型行为在新任务上自动统一”。

## § 10 — 最小复现实验

一周内最有价值的不是追求复刻 97.37%，而是验证“表示能否跨出训练分布仍保留 topology/mode 信息”。

可从 Fig. 2 中最容易混淆的两类二阶 continuous circuits，以及 Buck 的 CCM/DCM 两类开始。根据论文的 circuit-to-bond-graph 规则手工实现 4 类 graph converter，使用透明记录的元件范围与 operating points 生成 steady-state samples；node feature 采用 Element ID 加 normalized value，continuous edge feature 设 1，switching edges/nodes加入 duty cycle 与 virtual-switch state。然后实现三层 PyTorch-Geometric GCN、global mean readout、Softmax，与论文 pipeline 对齐 [pdf:E09]（PDF 物理页 11，Table 6 与 Section VI-C）[pdf:E14]（PDF 物理页 16，Section VII-1）。

数据必须按“元件参数区间与运行工况”分组，而不是把同一分布随机 shuffle 后拆开：训练只看中间参数区间，测试看两端外推区间，并额外留出接近 CCM/DCM 边界的样本。测量 macro-F1、每类 recall、calibration，以及在参数外推和 mode boundary 上的退化。若 held-out macro-F1 仍接近 in-distribution 结果、且 CCM/DCM 边界错误随物理距离单调增加，算支持核心机制；若随机切分接近 100% 而 group-held-out 显著坍塌，或模型主要利用 duty-cycle 阈值而非图结构，便反驳“表示带来可泛化物理信息”的强说法。

这个实验不能宣称精确 reproduction，因为论文没有给出 component range、simulator、seed、batch size 或代码；它是对核心机制的最小可证伪复现。

## § 11 — 最强反例设计

最强反例不是再加一种 converter，而是构造**标签不同、局部 feature 统计几乎相同、只有跨尺度动态与 mode transition 才能区分**的图对。

具体可选两组攻击。第一组是 topology attack：构造 bond-graph 局部邻域在三跳内高度相似、但因远端连接或端口定义不同而具有不同传递行为的高阶网络；三层 GCN 加 global mean readout 可能把它们压成近似 embedding。第二组是 operating-mode attack：在电感电流恰好触零附近加入 dead time、二极管压降、寄生电容和采样噪声，使 DCM 不再是干净的 mutually exclusive \(D_3\) 状态；如果标签仍由预先写入的 virtual-switch feature 决定，分类器实际上读取了答案，而不是从电路行为识别 mode。

实验应设置三条对照：只给 topology、只给 operating features、给完整 graph。若“只给 duty-cycle/virtual-switch features”的简单 MLP 与完整 GCN 同样达到 100%，则 switching 结果的替代解释是 label leakage；若三跳同构但全局行为不同的图对大量混淆，则反驳固定三层 message passing 足以表达可扩展电路结构。论文现有结果无法排除这两种情况。

## § 12 — Follow-up Research Idea

**候选方向，不声称 novelty：把“电路图分类器”改成“可组合、可编译的分层动态端口模型”。** 未满足的需求是：大规模 VSC 场站需要许多 converter model 在共同网络中交换端口电流/电压，并在 EMT 时间尺度内稳定、确定地推进；当前论文只输出 class probability，不能直接进入网络方程，也没有硬件时序保证。

这个方向统一三个层次。底层把单个 converter 的 bond graph 扩展成 hybrid dynamic graph，输出下一步端口电流、内部状态和 mode-transition confidence，而不是 topology label；可借鉴 port-Hamiltonian/energy-based learning、graph neural ODE 与 hybrid automata，使模型训练目标包含能量平衡、KCL/KVL residual 和 switching-event consistency。中层把多个 VSC 的端口图与场站母线/线路图组成 hierarchical graph，只在端口交换低维消息，从而把 converter 内部快动态与场站网络耦合分开。硬件层不直接“把 PyTorch 模型搬上 FPGA”，而是把有界 message-passing schedule 编译成 streaming dataflow，明确量化位宽、BRAM 中的 graph state、DSP 乘加预算和最坏情况 latency。

它可能产生本领域认可的研究价值，是因为评价对象从“类别分对没有”改变为三项更接近工程的指标：未见 topology/parameter 下的 trajectory error，长时闭环/网络耦合稳定性，以及 FPGA 上可证明的 deadline、resource 与功耗。第一个证伪实验应选择一个小型多 VSC 场站：至少包含两个 converter 拓扑、CCM/DCM 边界、参数外推与一次网络故障；与开关级 EMT reference 比较端口波形、能量残差和稳定性，再把同一模型量化部署到 FPGA，测最坏 latency、LUT/DSP/BRAM 与功耗。只要模型在 held-out converter 上失稳、误差在多实例耦合后不可控，或 FPGA latency 超过目标步长，这个方向就应被否定或收缩。

它与本文的实质区别不是多加一个 GCN layer，而是更换研究目标：从静态 graph classification 变成具有端口契约、动态状态、事件语义和硬件执行约束的 composable surrogate。论文把 condition monitoring、circuit generation、power-system fault detection 等列为潜在应用 [pdf:E16]（PDF 物理页 18，Section VIII–IX），但没有完成上述动态、系统级或 FPGA 验证；因此这里只能作为候选研究议程，不能据此宣称已有 novelty 或可部署性。
