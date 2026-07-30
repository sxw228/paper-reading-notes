# An Overview of Digital Twin Technology for Power Electronics: State-of-the-Art and Future Trends

- 作者：Chenhao Wu，Zhexin Cui，Qian Xia，Jiguang Yue，Feng Lyu
- 出处：IEEE Transactions on Power Electronics，Vol. 40，No. 9
- 年份：2025
- DOI：10.1109/TPEL.2025.3570638
- Zotero key：GYR82VTM

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文问的不是“某一种 digital twin（DT）算法能否改善某一个变换器”，而是一个更基础的工程问题：面对设计、控制、维护三个生命周期阶段，以及机制、仿真、多物理场、数据四类建模路线，研究人员究竟应该如何理解 power electronic system（PES）里的 DT、选择模型，并判断它是否真的比普通离线模型多提供了实时同步、准确映射、数据交互或高保真能力。作者以超过 170 篇文献为对象，给出的目标是建立一张从 DT 概念、模型到生命周期功能的全景图，而不是提出一个新的变换器或控制器。[pdf:E01]（PDF 物理页 1，Abstract 与 Fig. 1）

这个问题重要，是因为 PES 同时存在几类彼此拉扯的要求。开关与控制要求快速计算，热、磁、机械和老化过程又跨越完全不同的时间尺度；设计阶段需要快速试错，控制阶段需要低时延闭环，维护阶段则依赖长期、稀缺而且可能失衡的退化数据。论文因此把 DT 的价值概括为三类：提高设计效率、增强控制性能、促进 predictive maintenance，并希望最终支撑系统的高质量、可靠运行。[pdf:E16]（PDF 物理页 20，Section VIII 开头）[pdf:E17]（PDF 物理页 21，Section VIII 结尾）

对 EMT 与 FPGA 研究者，实际意义尤其具体：DT 不是“画一个虚拟模型”的新名字。它可能是可离散、可放到实时计算单元上的状态空间模型，也可能是 HIL 中的高保真仿真、跨物理场的 reduced-order model，或者由现场数据持续校正的 learned model。不同选择直接决定能否在 deadline 内执行、能否覆盖开关状态、能否解释故障，以及是否有资格闭环影响物理系统。

## § 2 — 前人工作与不足

论文把已有综述分成若干局部视角：有的讨论一般 DT 的 modeling、enabling technology、uncertainty quantification 与 optimization；有的只覆盖 power-system steady-state analysis、PV 能量预测与维护成本、power-electronics-based energy conversion、microgrid，或 electrical machine control 与 predictive maintenance。作者的判断是，这些综述要么停留在通用框架，要么集中于单一应用，缺少对 PES 中 DT 建模方法与典型生命周期应用的集中、细化比较。[pdf:E02]（PDF 物理页 2，Table I、相关综述讨论与三项贡献）

另一个更根本的前置问题是术语混用。论文按自动数据流方向区分 digital model（DM）、digital shadow（DS）与 DT：DM 没有自动数据交换；DS 是物理对象到数字对象的自动单向流；只有物理与数字对象之间完全整合的双向流才称为 DT。与此同时，作者采用包含 physical entity、virtual entity、service、data、connection 的 5-D 模型作为更完整的组织方式。[pdf:E03]（PDF 物理页 3，Figs. 2–3 与 Section II-B）

因此，这篇综述真正补的不是“又列一批应用”，而是两个坐标轴：横轴是 mechanism、simulation、multiphysics、data 四类模型；纵轴是 design、control、maintenance 三个阶段。它还把模型的优势、缺点、计算成本、scalability、integration 难度和适用场景放在同一表中比较，并讨论 edge-cloud 部署里的 latency、算力、数据安全与成本权衡。[pdf:E06]（PDF 物理页 8，Table III 与 Section III-E）

但这里有一个必须保留的限制：作者称调查“comprehensive but still not exhaustive”，正文没有给出可复现的检索数据库、检索式、纳入排除流程或文献质量评分。因此，“覆盖超过 170 篇”证明了广度，却不等同于 systematic review 意义上的无偏样本，也不能直接把各引用论文的局部实验结果合并成总体 effect size。

## § 3 — 重建作者的思考路径

可以把作者到达这套框架之前的推理重建为五步。

1. 先从概念混乱出发。如果一个离线 Simulink 模型、一个由传感器单向更新的 dashboard 和一个能反向控制硬件的闭环系统都被叫作 DT，文献之间就无法比较。因此先用数据流方向把 DM、DS、DT 分开。[pdf:E03]（PDF 物理页 3，Section II-B）
2. 再承认 PES 不可能只有一种“最佳 twin”。机制模型可解释但受建模假设约束；仿真模型易于接 HIL 但受算力制约；多物理场模型能表达热磁耦合却难实时；数据模型能拟合难建模关系，但依赖训练分布与数据质量。于是需要模型分类，而不是统一算法。[pdf:E06]（PDF 物理页 8，Table III）
3. 把模型选择放回任务。设计需要 virtual prototyping 和 digital verification；控制需要预测、优化和可控性；维护需要 condition monitoring、fault diagnosis、reliability evaluation 与 RUL prediction。相同模型在不同阶段的“够用”标准并不相同。
4. 把 fidelity 视为可迭代关系而非一次建模结果。论文建议先定义需求，再建模、接入实时数据、核对虚实一致性，最后依据物理实验继续修正。[pdf:E04]（PDF 物理页 4，Section II-D 的五步 guidance 与 Fig. 4）
5. 最后才讨论扩展：当单个 physical–digital pair 无法承担数据不平衡、局部控制与故障接管时，引入 parallel triplet，形成 digital triplet（DTri）。这一步是作者提出的未来视角，不是已经由整篇综述证明成熟的工业标准。[pdf:E16]（PDF 物理页 20，Fig. 16 与 Section VII-B）

## § 4 — 核心 Intuition

核心 intuition 是：PES 的 DT 不是一种固定模型，而是一条可验证的虚实闭环；先由任务决定需要什么 fidelity、更新频率和信息流，再选择或组合合适的模型。论文的主要价值来自“模型类型 × 生命周期功能”这张坐标图，而不来自一条统一数学公式。真正把 DT 与普通 digital model 区分开的关键，是数据能否按应用要求持续校正数字对象，并在需要时把可用的决策或控制作用反馈给物理对象。[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E04]（PDF 物理页 4，Section II-D）

## § 5 — 具体方法与完整 Pipeline

这是一篇综述，没有作者实现的单一端到端系统。它给出的“方法”应理解为一套搭建与审查 PES DT 的 pipeline。

1. **Requirement definition**：明确目标是设计优化、控制性能还是 predictive maintenance；同时列出可直接测量的 voltage/current 与难直接测量的 static/dynamic stress。需求决定后续模型的精度、更新频率和接口。
2. **Model development**：根据 mechanism complexity、simulation necessity、multiphysics coupling 与 data accessibility，在 mechanism、simulation、multiphysics、data 四类中选择或组合模型。
3. **Real-time simulation/data connection**：持续采集 voltage、current、temperature、stress 等运行数据，让数字模型随物理输入更新。作者同时明确，实时同步并不是所有 PES DT 的硬性条件；高保真 quasi-static simulation 在某些任务中也可以成立，关键是目标与资源约束匹配。
4. **Fidelity verification**：在相同工况下比较数字模型与物理对象的输出，至少分别检查 component level 与 system level。
5. **Model refinement**：依据物理实验反馈修正模型，并跨 operating scenario、environment 与 component configuration 检查适应性和 generalization。[pdf:E04]（PDF 物理页 4，Section II-D）

放到设计阶段，这条 pipeline 对应 objective formulation、constraint space、solution exploration、performance verification 四步；作者把此阶段的多数实现归入 DM，因为 design objective、parameter selection 与待验证方案主要通过人工方式在虚实系统间交换，输出是经迭代优化和 digital verification 的设计方案。[pdf:E07]（PDF 物理页 9，Section IV）

以一个 buck converter 的维护型 DT 为例，输入可以是可测的电感电流、输出电压与环境条件；数字侧用状态空间或等效机制模型产生预测，再用 incoming physical data 与 digital output 的误差反向搜索 capacitor、inductor、MOSFET 等关键参数；输出不是一幅“数字外观”，而是可用于 condition monitoring、fault diagnosis 或 controller switching 的参数与状态。维护框架进一步把流程分成 DT-informed learning、monitoring and predicting、maintenance decision making 三段：先融合历史退化、故障与机制知识，再在线选择或更新估计模型，最后把结果反馈到控制策略、功率分配、器件更换或冗余决策。[pdf:E11]（PDF 物理页 13，Fig. 9 与维护三段流程）

对 EMT/FPGA 实现，论文给出的边界如下：

- **模型与离散**：机制模型从电感、电容等储能元件建立状态空间；可用 FE、BE、Tustin 或 RK 离散，选择取决于 computation、stability 与 accuracy。论文列举了离散方程在 FPGA 上实现的工作，但没有给出一套通用 RTL architecture。[pdf:E05]（PDF 物理页 5，Section III-A，Eqs. (1)–(2)）
- **开关/事件处理**：正文说状态空间模型可通过组合 switching components 覆盖 CCM 与 DCM，但没有形成统一的开关事件定位、拓扑重构或代数环处理规范。因此不能把本综述外推为 EMT event semantics 的完整实现指南。[pdf:E05]（PDF 物理页 5，Section III-A）
- **时间推进与多速率**：控制应用可让 accelerator 以高于物理 sampling frequency 的频率运行，用频率比决定预测 horizon；另有 ML 模型在 FPGA 上实现 faster-than-real-time（FTRT）仿真的案例。[pdf:E09]（PDF 物理页 11，Fig. 7 与 Section V-B）
- **并行与平台**：论文覆盖 MATLAB/Simulink、HIL、RT-LAB、Opal-RT、Typhoon HIL、FPGA 等，但没有统一报告 task graph、memory bandwidth、fixed-point word length、资源占用或 worst-case execution time。Table III 的“computational cost”是定性比较，不是可直接下板的预算。[pdf:E06]（PDF 物理页 8，Table III）
- **edge-cloud 分工**：低时延、高优先级的 fault detection 或 predictive control 倾向在 edge 执行，长期 monitoring 与 large-scale simulation 倾向放到 cloud；这是一条任务划分原则，不是经过统一 benchmark 验证的最优解。[pdf:E06]（PDF 物理页 8，Section III-E）

## § 6 — 核心数学推导（无形式化数学则跳过）

这是一篇分类与应用综述，**没有单一核心数学推导，也没有一个把四类模型统一起来的理论**。因此不能把正文出现的公式拼接成所谓“DT 总方程”。下面两组公式只是作者用来说明代表性建模路线的局部工具。

第一组是机制模型的一般状态空间表达：

\[
\dot{x}=Ax+Bu,\qquad y=Cx+Du
\]

其中 \(x\) 是 state vector，\(u\) 是 input vector，\(A\) 是 state matrix，\(B\) 是 input matrix，\(C\) 是 output matrix，\(D\) 是 transfer matrix。论文随后给出离散输出形式 \(y_{n+1}=Cx_{n+1}\)，并讨论 FE、BE、Tustin 与 RK 的计算量、稳定性和精度取舍。[pdf:E05]（PDF 物理页 5，Eqs. (1)–(2)）

工程上，这组式子的意义是把电感电流、电容电压等内部状态变成可预测、可离散、可移植到实时计算单元的更新关系。它并没有回答所有 DT 问题：多物理场模型、data-driven model 与模型在线校正都需要各自的方程和误差定义。

第二组是维护阶段的 RUL 定义：

\[
l=\inf\{l:D(t+l)\ge \omega\mid D(t)<\omega,\ D_{1:j}\}.
\]

这里 \(D(t)\) 是监测到的 degradation process，\(\omega\) 是 failure threshold，\(D_{1:j}\) 是截至当前时刻的累积数据；RUL \(l\) 是退化轨迹首次越过阈值所需的剩余时间。因为 \(l\) 是随机变量，论文还强调需要 lower/upper confidence intervals，而不是只报单点寿命。[pdf:E13]（PDF 物理页 17，Fig. 14 与 Eq. (3)）

这两个例子共同说明 DT 的数学核心依任务而变：控制关心状态推进与 deadline，维护关心退化过程与不确定性。综述没有证明二者能由同一个统一状态或同一种估计器闭合。

## § 7 — 实验设计与结论

论文自身没有搭建统一实验平台，也没有做 meta-analysis；它用被综述论文的案例回答问题。因此下面的“实验”都是作者转述的既有研究结果，不能当作本文独立复现。

- **问题：DT/HIL 是否能缩短设计验证？** → **实验：**一项带 battery storage 和 grid coupling 的 power-plant case，把现实系统测试与 HIL DT 环境比较 → **答案：**综述报告测试周期由三天降到 4 h，说明 virtual commissioning 可能显著缩短局部项目的验证时间；但本文没有给出跨平台成本或 fidelity 误差的统一对比。[pdf:E08]（PDF 物理页 10，Section IV-B）
- **问题：DT 能否在 controller failure 后接管物理 converter？** → **实验：**buck converter 的 physical controller 与 RT-LAB 中 DT controller 通过 signal switch 连接，测试 reference tuning、model variation 与 physical-controller switching → **答案：**被引研究报告，检测到 \(u(t)=0\) 后 DT controller 可接管，切换约 500 ms，48 V 输出下 overshoot 小于 1.0 V。这个结果支持“可作为冗余控制”的局部 claim，不证明所有 converter 或更严格实时 deadline 下都成立。[pdf:E10]（PDF 物理页 12，Fig. 8 与 Section V-C）
- **问题：在线参数识别能否比通用 metaheuristic 更快？** → **实验：**thermal DT 用 dual extended Kalman filter 反复 prediction/correction，并与同步 PSO 执行比较 → **答案：**综述转述其 convergence speed 高 1000 倍；但没有在本文中统一重算 accuracy、compute resource 与噪声鲁棒性。[pdf:E12]（PDF 物理页 15，Section VI-A）
- **问题：DT 能否支持 RUL prediction？** → **实验：**一项 oil-immersed transformer case 把 multiphysics coupling 与 learning model 结合，在不同工况下预测 winding hot-spot temperature 与寿命 → **答案：**综述报告约 95% 的 RUL prediction accuracy；该数字属于单一被引案例，本文没有统一说明数据拆分、置信区间或跨设备迁移性能。[pdf:E14]（PDF 物理页 18，Section VI-D）
- **问题：FPGA 是否已经形成通用 DT 部署路径？** → **实验：**文献中有 FTRT ML model、controller-oriented PID flow、order-reduced converter DT 等 FPGA 案例 → **答案：**可行性案例存在，但本文没有把 LUT/DSP/BRAM、时钟、fixed-point error、I/O latency 与 end-to-end deadline 放进同一基准。因此可得结论是“已有 FPGA 入口”，不是“DT 已可在任意 PES 上实时落地”。[pdf:E09]（PDF 物理页 11，Section V-B）[pdf:E13]（PDF 物理页 17，FPGA order-reduced DT 案例）

论文最终把证据综合为三项定性结论：四类模型各有适用边界；DT 的作用贯穿 design、control、maintenance；未来瓶颈集中在 general modeling platform、跨生命周期连接、data/knowledge、real-time computation、privacy/security、emerging-technology integration 和 industrial integration。[pdf:E15]（PDF 物理页 19，Section VII-A）[pdf:E17]（PDF 物理页 21，Section VIII）

不得外推的范围也很清楚：这篇文章没有提供统一 benchmark、统计显著性、hardware resource 表、确定性 WCET 或独立复现实验。其结论适合做研究地图和需求清单，不适合直接充当某个实时控制或寿命预测方案的性能保证。

## § 8 — Take-aways

**5 句话：**

1. 论文用“4 类模型 × 3 个生命周期阶段”组织了 PES digital twin 的主要研究空间。[pdf:E02]（PDF 物理页 2，贡献列表）
2. DM、DS、DT 的关键差别是自动数据流方向，只有完整双向交互才是严格意义上的 DT。[pdf:E03]（PDF 物理页 3，Fig. 3）
3. DT 建模应从需求、模型、实时数据、fidelity verification 到 model refinement 闭环推进，而不是一次性建立数字模型。[pdf:E04]（PDF 物理页 4，Section II-D）
4. HIL、FPGA、edge-cloud 与 data-driven model 已有大量可行性案例，但各文献的 fidelity、latency、资源和验证口径尚不统一。
5. 这篇综述最适合作为设计研究问题的地图；它本身不提供可直接复用的统一算法、实时架构或统计性能保证。

**3 句话：**

1. PES 的 DT 价值来自与物理系统持续校正并服务具体生命周期任务，而不是“有一个虚拟模型”。
2. 四类模型必须按 interpretability、fidelity、compute、data 与 latency 约束取舍，混合模型很可能比单一分类更符合真实系统。[pdf:E06]（PDF 物理页 8，Table III）
3. 当前最缺的不是更多概念名称，而是可复现的 fidelity、实时性、跨工况和跨生命周期验证合同。

**1 句话：**

这篇论文把 PES digital twin 从口号整理成了一张有用的模型—任务地图，但地图还没有变成可审计、可比较、可部署的工程标准。

## § 9 — 最脆弱的假设

最脆弱的假设是：**来自不同对象、不同数据流方向、不同 fidelity 定义和不同实验口径的 170 余篇案例，仍足够可比，因而可以支撑统一的四模型分类与生命周期建议。**

这个假设一旦不成立，论文最重要的贡献会从“可指导模型选择的 taxonomy”退化成“方便阅读的主题目录”。风险来自三处。第一，论文自己承认 DM、DS、DT 在文献中经常混用，而它们的数据闭环能力根本不同。[pdf:E03]（PDF 物理页 3，Section II-B）第二，作者明确表示实时同步不是所有 DT 的严格要求，导致 quasi-static high-fidelity simulation 与 real-time closed-loop twin 可能被放在同一大类下比较。[pdf:E04]（PDF 物理页 4，Section II-D）第三，论文在 future work 中直接指出 fidelity 不足、技术成熟度和标准化程度低、PES 间 interoperability 差是 common pitfalls。[pdf:E16]（PDF 物理页 20，Section VII-B）

论文为 taxonomy 提供了广泛案例和定性比较，却没有提供 inter-rater labeling、统一 fidelity metric、study-quality weighting 或 sensitivity analysis。基于全文证据的判断是：分类的解释力是可信的，分类的完备性与可重复性仍未被验证。

## § 10 — 最小复现实验

如果只有一周，最值得复现的不是重新做一个复杂 DT，而是检验论文的核心 taxonomy 是否可重复使用。

**数据：**从论文参考文献中分层抽取 24 篇全文，覆盖 4 类模型与 3 个生命周期阶段，每个组合至少 2 篇；优先选择正文明确讨论过的 buck/boost converter、PMSM、microgrid、HIL 与 RUL 案例。

**实现：**制定一张不超过一页的 coding sheet，只记录 model class、lifecycle phase、DM/DS/DT directionality、real-time/FTRT、physical validation、fidelity metric、hardware platform、reported latency/resource。让两名评审者独立标注，先不互相讨论。

**测量：**

- model class、lifecycle、directionality 的 Cohen’s \(\kappa\)；
- 无法单标签归类、必须 hybrid/multi-label 的比例；
- 报告明确 fidelity metric、end-to-end latency、hardware resource 的文献比例；
- 论文 Table III 的优势/缺点能否从原文直接回溯。

**支持条件：**预先规定 \(\kappa\ge 0.8\)，至少 90% 样本能在不新增类别的情况下完成标注，并且 Table III 的主要比较项可由原文复核。**反驳条件：**大量论文因术语、混合模型或生命周期交叉而无法一致分类，或者同一标签下的 fidelity/real-time 含义互不相容。这个实验只检验综述框架的可用性，不冒充对所有 DT 性能 claim 的复现。

## § 11 — 最强反例设计

最强反例不是找一个“DT 预测不准”的普通失败案例，而是构造一个**分类看似成功、工程上却给出相反决策**的系统。

可以选一台宽工况双向 converter：设计阶段用 multiphysics/FEA 生成 thermal 与 parasitic data；控制阶段用 reduced-order mechanism model 在 FPGA 上 FTRT 预测；维护阶段用 learned residual 更新老化参数；物理到数字的数据流连续存在，但只有安全 supervisor 批准后才能反向修改 controller。这个系统天然跨四类模型、三个生命周期和多种数据流方向。如果按论文 taxonomy 强行指定一个“主要模型”和一个“主要阶段”，很可能丢失决定实时性和安全性的边界。

攻击实验是逐步加入四类扰动：未见过的 switching mode、sensor delay/dropout、thermal parameter drift、controller failure。然后比较三种方案：单一 taxonomy 标签指导的部署、明确 hybrid dependency graph 的部署、没有 DT 的传统 observer/controller。若单标签方案在 nominal fidelity 上表现很好，却在任一扰动下错过 deadline、错误接管或把 out-of-distribution 数据当作可信更新，而 hybrid contract 能提前拒绝或降级，那么就说明“模型类别”不是足够的工程决策单元。论文所指出的纳秒级开关、秒级控制到年级维护的跨时间尺度，以及 edge-cloud latency tradeoff，正是这个反例可能发生的物理基础。[pdf:E15]（PDF 物理页 19，Section VII-A）

## § 12 — Follow-up Research Idea

电力电子领域通常不会只凭概念新颖性评价高影响研究；更重要的是权威期刊中的严格实验、跨工况可复现性、实时硬件可实现性、可靠性收益和系统级工程价值。基于第 9 节的脆弱假设，一个非增量候选方向是：**建立面向 PES 的“可执行 DT 合同与失效边界 benchmark”**。它不再问“该系统属于哪一类 twin”，而是要求每个 DT 明确声明并在线检查其适用域。

**（a）未满足需求。** 当前文献能描述模型类别，却缺少统一、机器可检查的合同来连接 fidelity、data directionality、update rate、deadline、uncertainty、security 与允许的 physical action。论文列出的 real-time computational unit、data consistency、privacy/security 和 interoperability 挑战表明，这些缺口已经决定 DT 能否安全进入真实系统。[pdf:E15]（PDF 物理页 19，Section VII-A）

**（b）研究价值。** 如果一个合同能在模型失真尚未演变为控制或维护错误之前检测到越界，并在不同 converter、drive 与 HIL 平台上重复成立，它同时提供理论可证伪性、FPGA/real-time 可实现性和 system reliability 价值，比“再加一种 AI 模型”更符合本领域的高影响标准。

**（c）可借鉴工具。** 可结合 control barrier/safety monitor、assurance case、system identification 的 uncertainty set、multi-fidelity modeling、real-time scheduling/WCET analysis 与 data provenance。论文提出的 DTri 可以作为受控冗余结构的一个候选，但不能预设它优于较简单的 supervisor；parallel controller 的接管价值仍需独立验证。[pdf:E16]（PDF 物理页 20，Fig. 16）

**（d）第一个证伪实验。** 在同一 buck/boost HIL testbed 上预注册 voltage/current/temperature fidelity envelope、端到端 deadline、允许的 controller action 和 OOD 条件；随后施加参数漂移、模式切换、通信延迟与 controller failure。如果合同不能在物理输出越界前稳定报警，或者误报导致不必要接管，那么该方向立即失败。

**（e）与已有工作的实质区别。** 论文回顾的大多数工作优化“模型更准”或“功能更多”，而这个方向把研究对象改成“DT 在什么证据与时序条件下有权影响物理系统”。它把 taxonomy 从静态标签变成运行时可验证的责任边界。由于本卡没有对合同式 DT、assurance case 和 benchmark 相关文献做充分外部检索，这只是**候选研究想法，不声称 novelty**。
