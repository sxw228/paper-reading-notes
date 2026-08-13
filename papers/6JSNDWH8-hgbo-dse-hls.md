# HGBO-DSE: Hierarchical GNN and Bayesian Optimization based HLS Design Space Exploration

作者：Huizhen Kuang；Xianfeng Cao；Jingyuan Li；Lingli Wang  
出处：2023 International Conference on Field Programmable Technology（ICFPT）  
年份：2023  
DOI：10.1109/ICFPT59805.2023.00017  
Zotero key：6JSNDWH8  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。标题、作者和摘要见（PDF 物理页 1，标题页与 Abstract）[pdf:E01]

## § 1 — 研究问题与重要性

这篇论文解决的是一个很具体的工程问题：面对由 HLS directives（高层综合指令）形成的巨大、离散、带条件依赖的设计空间，怎样在不穷举所有配置、也不对每个候选都执行耗时的 FPGA implementation（实现）的前提下，尽快找出 power、latency、critical-path delay 和 area 之间的 Pareto-optimal（帕累托最优）解。作者把任务分成三部分：用 HGP 预测 post-implementation PPA，用 TDM 删除无效指令组合，再用 BOME 做多目标顺序搜索；摘要同时把支持范围限定到 function、loop、array 和 operator 四个层级。（PDF 物理页 1，标题页与 Abstract）[pdf:E01]

这个问题重要，不是因为 HLS 缺少可调旋钮，而是恰恰因为旋钮太多且相互作用复杂。论文指出，设计空间随指令数量指数增长，已有工作对 operator-level 的细粒度探索不足，而真实 PPA 往往只能在耗时的 implementation 之后获得；因此，人工调参、全空间搜索和“每点评估一次实现”的流程都会把设计周期拖长。更进一步，多目标之间相关且冲突，单一最优值并不存在，真正的输出应是一组可供工程师选取的 Pareto designs。（PDF 物理页 1，Section I Introduction）[pdf:E02]

论文直接报告的价值是：HGP 对 LUT、FF、critical path 和 power 的测试误差被压到 4.21%–7.72% 的区间，MOTPE-FL 相对 SA 和 NSGA-II 的 PLDA 改善分别为 72.00% 和 30.47%，以 HGP 替代 implementation 评价后，DSE 平均加速 14×、最高 24×。（PDF 物理页 1，标题页与 Abstract）[pdf:E01] 这些数字说明作者瞄准的不是单独提高 predictor accuracy（预测精度），而是缩短“提出配置—评估质量—更新搜索”的整个闭环。

## § 2 — 前人工作与不足

论文把 prior work 分成“QoR/PPA 预测”和“搜索算法”两条线。预测方面，Lin-analyzer、COMBA 等 analytical models（解析模型）可以估算性能和部分资源，但作者认为它们难以准确复现 HLS 工具内部启发式，也不适合 imperfect loops 等不规则逻辑；传统 ML predictor 要么依赖手工特征工程，要么只把 directives 当输入，容易丢失 program semantics。已有 GNN 方法如 IronMan-Pro、GNN-DSE、PowerGear 和 PNA-R 开始把 CDFG 用作输入，但论文认为这些方法采用 flat pooling（平坦池化），一次性压成图级向量，可能损失拓扑层级信息。（PDF 物理页 1，Section I Introduction）[pdf:E02]

搜索方面，SA、genetic algorithm 和 clustering 等 meta-heuristics 具有通用性，但收敛可能较慢；active learning 和 Gaussian-process BO 能减少采样，却会在高维、非规则、条件化空间中遇到建模困难；IronMan-Pro 使用 reinforcement learning，但需要额外训练。作者因此提出三项针对性改变：hierarchical pooling 代替 flat pooling，MOTPE 加 EnhancedLHS 代替普通随机初始化，以及 tree-structured design-space model 先消除冲突配置。（PDF 物理页 2，Section I contributions 与搜索方法讨论）[pdf:E03]

需要严格区分“论文声称”和“已被独立验证”。作者明确声称 HGP 是首个把 hierarchical pooling 用于 HLS QoR prediction 的 predictor，并用“flat pooling 可能丢失结构信息”解释其动机。（PDF 物理页 2，Section II-A hierarchical pooling 讨论）[pdf:E04] 由于本任务按协议只使用源 PDF、没有外部检索，这个“first”只能视为作者的 novelty claim，不能在本卡中升级成独立确认的事实。

MOTPE 的选择也有明确背景：它用两个密度模型处理 irregular search space，并借助 EHVI 偏向可能改善 Pareto front 的候选；这比把整个高维条件空间交给单个 Gaussian process 更贴合论文所描述的变量结构。（PDF 物理页 2，Section II-B 与 Eq. (2)）[pdf:E05] 但论文没有对“为什么一定是 MOTPE 而不是其他现代多目标 optimizer”做广泛、同预算的比较，因此搜索层的相对优势仍主要建立在 SA 和 NSGA-II 两个 baseline 上。

## § 3 — 重建作者的思考路径

下面是基于全文证据的逆向重建，不是作者逐字写出的推理过程。

第一步，先把任务认成 Pareto optimization，而不是把 power、latency、delay、area 随意加权成一个标量。只要不同指标互相冲突，输出就应是 nondominated set；同时，目标函数昂贵，不能完整枚举设计空间。论文的 dominance、Pareto set 和多目标形式化正是这个起点。（PDF 物理页 3，Eq. (3)、Section II-C 与 Eq. (4)）[pdf:E06]

第二步，观察到“配置”不是独立参数组成的普通向量。外层 loop pipeline 可能迫使内层 loop fully unroll，某些 flatten、unroll、pipeline 组合在语义上无效；因此，先把合法性和条件依赖显式编码，再搜索，比让 optimizer 在大量无效点上试错更合理。

第三步，观察到 PPA 不只由 directives 的名字决定，还与 CDFG 中的 operation、data dependency、bitwidth、局部资源和长程拓扑有关。于是自然会想到用 graph representation；而若一次 global pooling 把整张图压平，嵌套计算结构可能被抹掉，因此逐层 coarsen 的 hierarchical pooling 成为一个可检验的表示假设。

第四步，既然真实 implementation 很慢，就把它从每次 BO 迭代中拿掉，训练一个 surrogate predictor；而搜索空间又是离散、条件化、多目标的，所以使用能按参数建立非参数密度、以 hypervolume 为导向的 MOTPE，并用覆盖更均匀的初始样本稳定早期搜索。换言之，作者的 idea 不是“再做一个 GNN”，而是让空间约束、图表示和多目标采样三者对齐。

## § 4 — 核心 Intuition

HGBO-DSE 的核心 intuition 是：HLS DSE 同时具有三种结构——指令之间的条件树、程序的层级图、目标之间的 Pareto 几何——因此不应把它当成一个扁平黑盒。TDM 先保证 optimizer 只在合法分支上行动，HGP 用分层图压缩保留 CDFG 结构，BOME 再把昂贵评价集中到最可能推进 Pareto front 的候选。训练阶段仍需真实 implementation 生成监督信号，但部署阶段用 HGP inference 替代逐点 implementation，从而把主要时间花在少数高价值候选上。论文的总体框架明确区分 training、inference 和 design-space exploration 三种模式。（PDF 物理页 3，Section III 与 Fig. 1）[pdf:E07]

## § 5 — 具体方法与完整 Pipeline

论文的完整系统可拆成“离线数据与模型准备”和“在线 DSE”两条链。以下用 `gemm` 作为贯穿例子。

1. **定义输入与可调空间。** 输入是 application C/C++、`config.yaml` 和 `params.yaml`。可探索指令覆盖 function 的 inline/balance，loop 的 flatten/unroll/pipeline，array 的 partition/reshape/bind storage，以及 operator 的 bind op；每个 directive 还有开关、factor、type、implementation 等选项。（PDF 物理页 3，Section IV-A 与 Table I）[pdf:E08]

2. **TDM 构造合法的条件树。** `config.yaml` 指定要探索的 function、loop、array、operation，`params.yaml` 指定各自选项；TDM 把 nested loops 的依赖编码为树，并把其他参数保留为普通维度。在 `gemm` 示例中，factor 上限设为 4 时，原始组合由 1 个 function 参数、7 个 loop 参数、12 个 array 参数和 7 个 operator 参数形成，论文给出的总规模是约 `5.9×10^10`；当某条路径选择了外层 pipeline 后，受其约束的内层子空间会被跳过。（PDF 物理页 4，Section IV-B 与 Fig. 2）[pdf:E09] 论文随后报告，tree-structured modeling 将该空间缩到 `1.2×10^10`。（PDF 物理页 4，Section IV-B 跨栏续文）[pdf:E10]

3. **生成训练数据。** Random sampler 从 TDM 空间采样配置并写成 Tcl；Vitis HLS 生成 Adb/IR、RTL 和 HLS reports，Vivado implementation 生成真实 post-implementation reports；graph constructor 把 IR 解析成 CDFG，并把 CDFG 与真实 PPA 配对进入 standard dataset。（PDF 物理页 4，Section V-A 与 Fig. 3）[pdf:E11] 这一步是成本最高但只需离线完成的监督数据生产环节。

4. **构造 HGP 输入。** CDFG node features 包括 node type、opcode category、delay、latency、bitwidth、LUT、FF 和 DSP；categorical features 用 one-hot，numerical features 直接使用，edge features 记录 edge type 与是否为 back edge，最终保存 node feature matrix、edge feature matrix 和 adjacency matrix。（PDF 物理页 5，Section V-B 与 Table II）[pdf:E12] 此外，模型还拼接从 HLS reports 提取的 global features，论文列举的是 resource utilization 和 critical-path delay。（PDF 物理页 5，Section V-C 与 Fig. 4）[pdf:E13]

5. **HGP 做图级回归。** 主干由三个 `GraphSAGE → ReLU → SAGPool` block 组成，每层都有 readout；三个尺度的 readout 相加得到 graph representation，再与 global features 拼接，经三层 MLP 输出目标 PPA。（PDF 物理页 5，Section V-C 与 Fig. 4）[pdf:E13] 作者的机制主张是，SAGPool 逐层保留高分节点、丢弃低分节点，以避免一次性 flat pooling；模型实际预测的是 post-implementation power、delay 与资源，而不是仅复述 HLS estimate。（PDF 物理页 5，Section V-C HGP architecture 正文）[pdf:E14]

6. **BOME 编码并初始化搜索。** BOME 支持 floating encoding 和 discrete encoding。以 array partition type 为例，`block/cyclic/complete` 可映射到 `[0,1]` 中三个区段，也可编码为整数 `0/1/2`，采样后再解码成 Tcl directive；总体流程是 encode、initial sample、建立 surrogate、最大化 acquisition、decode、评价、更新样本集，直到停止后返回 Pareto solutions。（PDF 物理页 6，Section VI、Fig. 5 与 Fig. 6）[pdf:E15]

7. **EnhancedLHS 产生覆盖更均匀的初始点。** 算法把每一维 `[0,1]` 均分为 `N_s` 个区间，每个区间抽一个点并打乱，重复 5 次，保留“样本间最小距离”最大的候选矩阵。（PDF 物理页 6，Algorithm 1）[pdf:E16] 它改变的是初始覆盖，而不是后续 MOTPE 的基本更新规则。

8. **MOTPE-FL 顺序探索。** 初始配置由 HGP 评价并形成样本集 `D`；每轮按 nondominated sorting 和 hypervolume subset selection 把 `D` 分成 `D_l/D_g`，对每个 active parameter 拟合 `l(x_i)/g(x_i)`，采样候选并选择比值最大的组合，再用 HGP 得到新 PPA，更新 `D`，最终返回 `pareto(D)`。（PDF 物理页 6，Algorithm 2）[pdf:E17]

需要注意，HGP 不是仅凭 directive vector 做零成本预测。论文的 inference path 仍运行 HLS tool 取得 IR/CDFG，并由 graph constructor 与 HLS reports 生成模型输入；它主要省掉的是更慢的 Vivado implementation。（PDF 物理页 3，Section III 与 Fig. 1）[pdf:E07] （PDF 物理页 4，Section V-A 与 Fig. 3）[pdf:E11]

从 EMT + FPGA 的验收视角看，这篇论文不是 electromagnetic transient（电磁暂态）仿真论文，因此没有开关事件处理、数值时间推进或 multi-rate integration；文中的 latency 是 HLS scheduling 后的 clock-cycle count，而不是连续时间仿真的步长。它报告了 directives 如何改变并行度、存储端口和 operator mapping，但没有报告 host-side 搜索并行化、定点数值格式选择或板上在线执行；这些内容应保持“未报告”，不能从一般 FPGA 常识补写。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有证明型 theorem，但有一条清晰的“多目标定义 → MOTPE acquisition → 图表示 → robust regression”数学链。

**1. 多目标问题。** 论文把配置写成 `x=(x_1,…,x_n)∈X`，把昂贵目标写成 `f(x)=(f_1(x),…,f_m(x))`，目标是

\[
\operatorname*{arg\,min}_{x\in X} f(x):=(f_1(x),f_2(x),\ldots,f_m(x)).
\]

这里的 `arg min` 不是一个点，而是所有不能被其他配置同时改进的 Pareto set。这个形式避免预先给 power、latency、delay、area 规定人为权重。（PDF 物理页 3，Eq. (3)、Section II-C 与 Eq. (4)）[pdf:E06] 工程 intuition 是：先保留 trade-off，再让使用者按场景选点。

**2. MOTPE 的 good/bad 密度分解。** 对每个参数 `x_i`，MOTPE 按目标向量相对参考集合 `Y*` 的 dominance/incomparability，把历史样本拆成两组并拟合

\[
p(x_i\mid \mathbf y)=
\begin{cases}
 l(x_i), & (\mathbf y\prec Y^*)\lor(\mathbf y\parallel Y^*),\\
 g(x_i), & Y^*\preceq \mathbf y.
\end{cases}
\]

`l(x_i)` 由较好样本构造，权重与 hypervolume contribution 成比例；`g(x_i)` 由其余样本构造。（PDF 物理页 2，Section II-B 与 Eq. (2)）[pdf:E05] 结合 EHVI 后，论文给出

\[
\mathrm{EHVI}_{Y^*}\propto
\left(\gamma+(1-\gamma)\frac{g(x_i)}{l(x_i)}\right)^{-1},
\]

所以最大化 EHVI 可近似为最大化 `l(x_i)/g(x_i)`。（PDF 物理页 3，Eq. (3)、Section II-C 与 Eq. (4)）[pdf:E06] 直观地说，一个参数值若在“好样本”中常见、在“差样本”中少见，就优先被尝试。

**3. GraphSAGE message passing。** 对节点 `v`，第 `l` 层更新为

\[
h_v^l=\sigma\!\left(W^l\cdot\operatorname{concat}\!\left(h_v^{l-1},
\operatorname{mean}(h_u^{l-1},\forall u\in\mathcal N(v))\right)\right).
\]

即先平均邻居表示，再与节点自身表示拼接，经过线性变换和非线性得到新 embedding。（PDF 物理页 5，Eq. (5)）[pdf:E18] 这一步让 operation 节点吸收局部 data/control dependency，但单靠它还没有图级输出。

**4. SAGPool 与 multi-scale readout。** SAGPool 用归一化图卷积计算每个节点的 self-attention score：

\[
Z=\sigma\!\left(\tilde D^{-1/2}\tilde A\tilde D^{-1/2}X\Theta\right),
\]

再保留 `idx=top-rank(Z,⌈kN⌉)` 对应的节点，论文设 `k=0.5`。每层 readout 为

\[
r^l=\left(\frac{1}{N^l}\sum_{i=1}^{N^l}x_i^l\right)
\Vert\left(\max_{i=1}^{N^l}x_i^l\right),
\]

即 mean pooling 与 max pooling 的拼接，随后把不同层的 `r^l` 相加。（PDF 物理页 5，Eq. (6)–Eq. (8)）[pdf:E19] 这里有一个值得注意的内部细节：公式按 `k=0.5` 和 `⌈kN⌉` 选择节点，而 Fig. 4 的示意文字写的是 `14→10→7→4`；两者不能按同一个固定比例逐层严格推出，因此该节点数序列更适合视为机制示意，而非可直接复现的层尺寸配置。另一个小差异是正文称“summation and maximum”，但 Eq. (8) 实际含 `1/N^l`，数学上是 mean 与 max。

**5. Huber training loss。** 预测器以

\[
L_\delta(y,\hat y)=
\begin{cases}
\tfrac12(y-\hat y)^2,&|y-\hat y|\le\delta,\\
\delta|y-\hat y|-\tfrac12\delta^2,&|y-\hat y|>\delta
\end{cases}
\]

训练，论文取 `δ=1`。（PDF 物理页 7，Eq. (9)）[pdf:E20] 小残差区保持平方损失的平滑性，大残差区转为线性增长，目的是降低极端 PPA 样本对梯度的支配。

## § 7 — 实验设计与结论

**问题 1：HGP 能否准确预测 post-implementation PPA？** 论文在 10 个 MachSuite benchmarks 上每个随机采 1,000 个 directive configurations，共得到 10,000 个 CDFG；Vitis HLS 2022.1 与 Vivado 2022.1 面向 Xilinx Virtex-7 VC707 `xc7vx485tffg1761-2`、100 MHz 生成标签。数据覆盖 power `0.241–3.334 W`、critical path `1.481–11.875 ns`，LUT/FF/DSP/BRAM 从 `19/26/0/0` 到 `107717/87312/540/384`，随后将 standard dataset 按 80%/20% 划分训练与测试，论文没有说明是否按 benchmark 隔离；模型训练 500 epochs、batch size 32。（PDF 物理页 7，Section VII-A、Table III 与训练设置）[pdf:E21] 测试中，HGP+SAGE+GF 的 MAPE 为 LUT `7.72%`、FF `4.21%`、CP `5.39%`、power `7.39%`，DSP/BRAM 的 MAE 为 `0.57/0.09`；它在多数指标优于列出的 baseline，但 CP 仍不如 PNA-R 的 `3.97%`。（PDF 物理页 7，Table IV 与 Section VII-B）[pdf:E22] 因而最稳妥的答案是“在论文给定的 80/20 测试划分上，平均点预测较准”，而不是“已证明可迁移到未见 application、device 或 tool version”。

**问题 2：hierarchical GNN 是否是精度提升的原因？** 论文比较了 GraphSAGE 与 TransformerConv，也比较了有无 global features；HGP+SAGE 从无 GF 到有 GF 后，LUT/FF/CP/power 误差明显下降。（PDF 物理页 7，Table IV 与 Section VII-B）[pdf:E22] 但没有给出“同一 GraphSAGE、同一参数量、只把 SAGPool 换成 flat pooling”的直接 ablation，因此实验支持 HGP 整体有效和 GF 有用，却没有干净隔离 hierarchical pooling 本身的因果贡献。这是核心 novelty 证据链中最明显的缺口之一。

**问题 3：BOME 能否在相同 DSE 任务上找到更好的 Pareto front？** 论文比较 SA、NSGA-II、MOTPE-D、MOTPE-F 和 MOTPE-FL。评价一是 ADRS，即 learned front 到由所有方法最佳结果合并所得 reference front 的平均最近距离；评价二是 normalized PLDA，即 power、latency、delay、area 乘积相对 Vitis HLS 默认实现的归一化值。（PDF 物理页 8，Section VII-C 与 Eq. (10)）[pdf:E23] MOTPE-FL 的平均 ADRS 为 `0.0881`，相对 SA 与 NSGA-II 的改善为 `94.65%` 和 `61.81%`，并在 10 个 benchmark 的 ADRS 列中都取得最小值。（PDF 物理页 8，Table V）[pdf:E24] normalized PLDA 的平均值为 `0.4551`，论文据此报告相对 Vitis HLS、SA、NSGA-II 分别改善 `54.49%`、`72.00%`、`30.47%`。（PDF 物理页 8，Table VI）[pdf:E25] 因而在本文定义的 budget 和 reference set 下，MOTPE-FL 是最强的被测方法；但 reference front 不是已知真实 Pareto front，且实验没有报告 `N_i/N_t` 的具体数值、重复随机种子或置信区间，不能判断优势对预算和随机性的敏感程度。

**问题 4：用 HGP 替代 implementation 会不会只换来速度、却损失解质量？** 论文将 BOME+HGP 与 BOME+IMPL 对比：平均 normalized PLDA 为 `0.4551` 对 `0.4719`，平均运行时间为 `31` 对 `425` 分钟，平均加速 `14×`，最高在 `md_knn` 上达到 `24×`；作者还把 PLDA 差异表述为 HGP 方案平均改善 `1.68%`。（PDF 物理页 8，Section VII-D 与 Table VII）[pdf:E26] 这给出了同一平台上的正面证据，但只覆盖一个 FPGA family、一个工具版本和 10 个 benchmark；同时，表中个别 benchmark 的 HGP PLDA 更差，因此不能把“平均近似无损”外推为逐任务无损。

总体结论是：论文实验较有力地支持“这一整套 system 在给定工具链与数据集上能缩短 DSE，并找到比两个传统 baseline 更好的 front”，但对 cross-application generalization、hierarchical pooling 的独立贡献、随机稳定性和真实 Pareto gap 的支持不足。

## § 8 — Take-aways

**5 句话**

1. HGBO-DSE 的贡献不是单点 predictor，而是把合法空间建模、PPA surrogate 和多目标搜索接成一个闭环。（PDF 物理页 8，Section VIII Conclusion）[pdf:E27]
2. TDM 的关键价值是把 nested-loop directive dependencies 显式化，避免 optimizer 在无效组合上浪费预算。
3. HGP 把 CDFG 的局部 message passing、hierarchical pooling、multi-scale readout 和 HLS global features 合并，用于 post-implementation PPA regression。
4. MOTPE-FL 在本文 10 个 MachSuite benchmark 上取得最低平均 ADRS 和最低平均 normalized PLDA，并显著优于 SA、NSGA-II。（PDF 物理页 8，Table V）[pdf:E24] （PDF 物理页 8，Table VI）[pdf:E25]
5. 论文最需要补强的不是更多平均 MAPE，而是 Pareto ranking、跨 application/device/toolchain 的泛化，以及只改变 pooling 方式的受控 ablation。

**3 句话**

1. 这篇论文抓住了 HLS DSE 的三个真实结构：条件化 directives、层级程序图和多目标 Pareto front。
2. 它在单一 Vitis/Vivado/VC707 设置下展示了约 `14×` 平均加速，同时保持平均 PLDA 不劣于 implementation-driven search。（PDF 物理页 8，Section VII-D 与 Table VII）[pdf:E26]
3. 但“平均点预测准确”仍不能自动推出“自适应搜索过程中 Pareto 排序可靠”。

**1 句话**

HGBO-DSE 是一个工程上完整、结果上有说服力但机制隔离与分布外验证仍不充分的 HLS 多目标 DSE 框架。

## § 9 — 最脆弱的假设

最脆弱的假设是：**HGP 在 BOME 自适应访问的候选分布上，不仅有低平均回归误差，还能可靠保留真实 post-implementation Pareto 排序。** 这个假设一旦不成立，BOME 会把采样预算集中到 surrogate 制造的“假前沿”，最终得到的速度越快，偏离真实前沿反而可能越快。

论文提供了两类支持。第一，论文测试集上的 MAPE/MAE 较低。（PDF 物理页 7，Table IV 与 Section VII-B）[pdf:E22] 第二，在同一批 benchmark 上，BOME+HGP 的平均 PLDA 与 BOME+IMPL 接近甚至略好，同时获得 14× 平均加速。（PDF 物理页 8，Section VII-D 与 Table VII）[pdf:E26] 这说明假设在本文工作点上并非毫无依据。

但缺少的证据更关键。论文只报告 80/20 划分、未说明按 application 留出，因此不能把结果当作 unseen-program 检验；MAPE/MAE 衡量逐点数值误差，不衡量 pairwise order、Pareto recall、hypervolume regret 或 near-front calibration；BO 的候选是 adaptively selected，通常集中在训练分布中最难的边界区域；HGP 输入主要是 CDFG、节点/边特征和 HLS global features，并不显式包含 placement、routing congestion 或 device-specific physical context。（PDF 物理页 5，Section V-B 与 Table II）[pdf:E12] 所以，一个整体误差不大的模型仍可能在少数拥塞临界配置上发生 Pareto inversion。论文没有给出这类 inversion 的频率，也没有 cross-device、cross-version 或 leave-one-benchmark-out 结果。

这比“EnhancedLHS 是否最佳”更脆弱，因为初始化稍差只会降低 sample efficiency，而 Pareto 排序失真会直接破坏“surrogate 可以替代 implementation”这一核心加速前提。

## § 10 — 最小复现实验

一周内最值得做的不是重建整个系统，而是直接检验“hierarchical pooling 是否改善 Pareto ranking”这一关键链条。

- **数据。** 选择 `gemm_ncubed`，按论文的四层 directive space 生成约 300–500 个 TDM-valid configurations；对每个配置运行同版本 Vitis HLS/Vivado 和同一 VC707 target，保存 CDFG、HLS global features 与真实 PPA。`gemm` 的 loop dependency 和 `5.9×10^10 → 1.2×10^10` 空间缩减为采样合法性提供了明确复现对象。（PDF 物理页 4，Section IV-B 与 Fig. 2）[pdf:E09] （PDF 物理页 4，Section IV-B 跨栏续文）[pdf:E10]
- **实现。** 做两个参数量尽量匹配的 predictor：A 为三层 GraphSAGE 后直接 global mean+max pooling，B 为论文的三层 GraphSAGE+SAGPool、多尺度 readout；两者使用相同 node/edge/global features、MLP、Huber loss、训练/测试划分和随机种子。
- **测量。** 除 LUT/FF/CP/power 的 MAPE 与 DSP/BRAM 的 MAE 外，必须测 Kendall/Spearman ranking、真实 Pareto set 的 recall、predicted front 经 implementation 复核后的 hypervolume regret，并在 3–5 个 seeds 上报告分布。
- **判据。** 若 B 在多数 seeds 上同时降低 point error、提高 near-front ranking 和 Pareto recall，且固定 30 次真实评价预算时得到更高真实 hypervolume，则支持“hierarchical pooling 对 DSE 有实质作用”；若只改善 MAPE、却不改善 front ranking，或优势在参数量匹配后消失，就反驳论文最重要的机制解释之一。

这个实验不需要复现所有 10 个 benchmark，也不需要完整重写 BOME；一个简单的固定-budget candidate selection 已足以判断 predictor 的结构增益是否真正传递到 DSE 目标。

## § 11 — 最强反例设计

最强反例是构造一组 **representation collision（表示碰撞）**：在 HGP 可见的 CDFG、node/edge features 和 HLS global features 上非常接近，但在真实 placement-and-routing 后出现显著不同的 critical path、power 或可布通性。

具体做法是选择 `spmv_ellpack`、`stencil3d` 或 `gemm_ncubed`，再通过 directives 把候选逐步推向高资源占用，系统扫描 array partition、bind storage、unroll、pipeline 与 DSP/fabric binding 的组合，刻意把设计推向 BRAM port pressure、高 fanout、DSP column 和 routing congestion 的临界区。对每个配置，在 HGP 输入空间中找最近邻配对；若两点的输入距离很小、模型预测也接近，但真实 PPA 跨过 Pareto dominance 关系，就得到一次 Pareto inversion。HGP 的可见特征和 graph architecture 由论文给出，而真实标签是在 Vivado implementation 后获得，因此这个测试直接攻击“前端结构足以决定后端 PPA”的可识别性假设。（PDF 物理页 4，Section V-A 与 Fig. 3）[pdf:E11] （PDF 物理页 5，Section V-C 与 Fig. 4）[pdf:E13]

更强的版本不是只找个别误差点，而是估计同一局部表示邻域内真实 PPA 的条件方差。如果在拥塞临界区存在持续的大方差，那么任何只使用当前输入表示的 predictor 都无法稳定区分这些配置；此时改更多 GNN layers 也不能解决信息缺失。报告结果的一个替代解释就会变成：MachSuite 与 VC707 的被测区域里，HLS estimates 恰好与 physical effects 高度相关，所以平均误差好看；一旦换到更拥塞、不同 device 或不同 placement seed，排序优势可能消失。若该反例成立，HGBO-DSE 仍可作为 heuristic，但“准确 surrogate 替代 implementation”的普适解释会被推翻。

## § 12 — Follow-up Research Bet

**候选研究押注：把 HLS DSE 重定义为“directive-induced causal graph transformation planning（指令诱导的因果图变换规划）”。** 这是基于本文证据提出的候选判断；由于本任务没有检索外部全文，不声称它具备已确认的 novelty。

新的研究问题不是“给定完整配置，PPA 是多少”，而是：**一个特定 directive 在某个层级和程序状态上，会诱导怎样的 IR/CDFG 结构变化与 PPA 增量；这些作用能否跨 application 复用并按顺序组合？** 目标是让 DSE 输出可迁移的“变换机制”和 action sequence，而不只是每个程序独立训练一个静态 `configuration → PPA` surrogate。

核心因果链是：构造只相差一个 directive 的 paired interventions → 学习 `state graph + scoped action → graph delta + ΔPPA` 的 action-conditioned transition model → 在 function/loop/array/operator 的层级状态上组合若干 graph rewrites → 用 planning 选择能产生互补结构变化的 action sequence → 只对少量候选运行真实 HLS/implementation。TDM 已经揭示 directives 具有路径依赖和 active/inactive 参数，而 Algorithm 2 仍主要对当前 active `x_i` 建立静态 `l/g` 密度；这为把“参数值”升级为“有作用域、有顺序的 graph-transform action”提供了直接切口。（PDF 物理页 4，Section IV-B 与 Fig. 2）[pdf:E09] （PDF 物理页 6，Algorithm 2）[pdf:E17]

这个方向至少改变四个基本设计变量：问题从 point prediction 改为 intervention-effect prediction，状态表示从最终 CDFG 改为有层级作用域的 state-action graph，数据生成从独立随机配置改为 matched counterfactual pairs，评价对象从同分布 MAPE 改为跨程序 action-effect transfer 与 sequence composition。论文的数据生成器本来就能保留 Tcl、IR、RTL、HLS report 和 implementation report，因此可以观察一条 directive 前后的结构差；HGP 的 hierarchical pooling 提供了可复用的多尺度图表示机制；10,000 个配置和 14× surrogate speedup 又说明已有资产足以支撑更丰富的模型，但当前实验没有测试跨 application 的机制迁移。（PDF 物理页 4，Section V-A 与 Fig. 3）[pdf:E11] （PDF 物理页 5，Section V-C 与 Fig. 4）[pdf:E13] （PDF 物理页 7，Section VII-A、Table III 与训练设置）[pdf:E21] （PDF 物理页 8，Section VII-D 与 Table VII）[pdf:E26]

最大的研究收益是把 DSE 从“每个新程序重新黑盒优化”变成“复用已学到的 graph transformation motifs”，从而可能实现 few-shot cross-program optimization，并解释某个 directive 为什么改善或恶化某项 PPA。最大的科学风险是 directives 的作用可能强烈 non-local、non-commutative，两个单步 graph delta 无法组合；此外，后端 physical effects 可能不在 IR delta 中可观测，使 transition model 只学到相关性。

最小证伪实验选 3 个 benchmark。对每个 benchmark 生成成对样本，每对只改变一个合法 directive，并保留 action scope、前后 CDFG 与真实 ΔPPA；在两个 benchmark 上训练，在第三个上测试。比较三者：静态 HGP、使用同样 paired data 但忽略 action label 的强 predictor、以及 action-conditioned delta model；测单步 ΔPPA 符号/排序、两步 action composition error，以及固定真实实现预算下的真实 Pareto hypervolume。为排除“只是 paired data augmentation 更有效”的替代解释，还应打乱 action labels；只有在正确 action label 下跨程序 delta 和两步组合都显著更好，才能支持因果图变换机制。

仅依据本文 related-work 描述，最近的 GNN 方法研究的是 `CDFG → QoR` point regression，IronMan-Pro 的 reinforcement learning 研究 search policy，本文的 MOTPE 研究参数密度与 hypervolume；这里的实质区别在于 problem 是 transferable intervention effect，mechanism 是 action-conditioned graph transition，representation 是 ordered state-action graph，experimental object 是 matched counterfactual configuration pairs，而不是换一个 optimizer wrapper。

**Wild-card alternative：** 训练一个 program-conditioned set generator，直接从 TDM-valid directive tree 与 CDFG motifs 一次生成整组多样 Pareto candidates，把 sequential BO 改成 set-valued Pareto-front synthesis，并以跨 application 的 front coverage 而非单点误差作为主要目标。
