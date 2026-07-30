# Applications of Data-Driven Dynamic Modeling of Power Converters in Power Systems: An Overview

- 作者：Sunil Subedi、Yonghao Gui、Yaosuo Xue
- 出处：IEEE Transactions on Industry Applications, Vol. 61, No. 2
- 年份：2025
- DOI：10.1109/TIA.2025.3529797
- Zotero key：CEGDREBJ

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是“再设计一个更准的神经网络”，而是一个更上游的问题：当电力系统越来越由 power electronic converter（PEC）接口资源主导时，研究者应该如何理解、选择和部署 data-driven dynamic modeling，并把这些模型用于稳定性、保护、故障诊断、优化控制、监测和电能质量分析。作者指出，详细 switched/EMT 模型虽然能保留高频开关动态，却会随 PEC 数量增长变得计算昂贵，还依赖常常属于厂商机密的控制结构与参数；数据驱动方法试图用有限内部知识，从输入输出数据中学习动态响应。[pdf:E01]（PDF 物理页 1，Abstract）

重要性来自模型错误的系统级后果。PEC 控制决定了低惯量电网在故障、频率变化和电压扰动下的响应，而传统同步机主导系统中的许多简化假设不再稳妥。论文把工程矛盾概括为 accuracy、simulation time-step、可扩展性和内部知识之间的权衡：越接近开关细节，通常计算代价越高；越依赖简化或 learned behavior，越需要证明数据覆盖和模型可信度。作者因此把自己的目标定位为补齐既有综述在 PEC 控制结构、white/grey/black-box 比较、ML/AI 应用与挑战方面的断裂。[pdf:E02]（PDF 物理页 3，Fig. 2 及 Introduction 的综述缺口与三项贡献）

## § 2 — 前人工作与不足

论文之前已经存在三条相对成熟但彼此分离的路线。第一条是 white-box：已知拓扑、控制和参数，用微分/代数方程、state-space 或 transfer function 描述系统。第二条是 grey-box：保留部分物理结构，只从数据辨识未知参数或未建模部分。第三条是 black-box：不显式恢复内部结构，直接学习输入历史到输出的映射。作者还把 PEC 的应用控制分为 grid-following、grid-forming 和 grid-supporting；这些控制模式对同步方式、等效源特性和需学习的动态并不相同。[pdf:E03]（PDF 物理页 5，Figs. 3–5 与 Section III 开头）

white-box 的优势是物理解释和设计可控性，但它要求足够完整的结构、参数和控制知识。论文用状态方程与线性化 state-space 形式说明这种路线如何从已知动态出发；对大规模、闭源控制或参数不可靠的 PEC 集群，这一前提本身会成为成本与误差来源。[pdf:E04]（PDF 物理页 6，Fig. 6、Table I、Eqs. (1)–(4)）

grey-box 通过保留已知矩阵、再辨识不确定输入和参数来折中物理可信度与灵活性；black-box 则更适合内部机制未知、非线性和非理想效应难以显式建模的对象。它们的不足也正好相反：grey-box 仍可能被错误或不完整的物理结构限制，black-box 则容易失去解释性并依赖数据覆盖。[pdf:E05]（PDF 物理页 7，Fig. 7、Eqs. (6)–(7) 与 Section III-C）

作者随后把 black-box 候选整理为 supervised、unsupervised、reinforcement 和 ensemble learning，并给出从 data collection/preprocessing 到 model estimation/validation 再到 deployment 的通用流程。[pdf:E06]（PDF 物理页 8，Figs. 8–9）这一流程里的 system identification 仍需预先选择 model structure 和 order，再用预测误差估计参数；论文以 least-squares 目标说明了这一点。[pdf:E07]（PDF 物理页 9，Eqs. (9)–(11)）Table IV 最终把三类路线的适用性和代价并排呈现：black-box 擅长复杂非线性但需要大数据且解释性弱，grey-box 需要部分 domain knowledge，white-box 依赖详细系统知识且开发耗时。[pdf:E08]（PDF 物理页 10，Table IV）

既有综述分别覆盖过动态系统辨识、纯 power electronics 的 AI 应用、online learning 或 smart converter 架构，但没有同时回答“PEC 是什么控制对象”“三类动态模型如何选择”“模型能在哪些电力系统任务中使用”“安全、实时和数据约束如何限制使用”。本综述的价值因此主要是知识结构整合，而不是声称首次提出某一种模型。

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为四步。

第一，先从物理对象出发。PEC 不只是一个静态功率接口；grid-following 依赖同步和电流控制，grid-forming 建立电压与频率，grid-supporting 组合两类行为。因此，动态模型必须保留与目标应用相关的控制响应，而不能只拟合稳态功率点。

第二，承认两个传统极端都不够。详细 switched/EMT 模型可表达高频开关，却需要微秒量级时间步并在大系统中造成巨大计算负担；正序 phasor 模型计算快，却可能因 balanced、fundamental-frequency 等假设丢失 PEC 主导系统中的关键现象。作者把 dynamic phasor 和 data-driven model 看作填补两者之间空档的候选。[pdf:E09]（PDF 物理页 12，Section IV 末尾至 Section V 开头）

第三，把“缺多少内部知识”作为建模入口，而不是先按某个 ML 算法分类。结构和参数都已知时用 white-box；只知道部分时用 grey-box；内部信息不可得时才进入 black-box。这样能够先固定证据边界，再选择 regression、RNN、kernel method 或 deep learning。

第四，再从 power-system task 反推模型需要学什么。稳定性评估关注扰动后的轨迹与边界，保护和故障诊断关注事件识别，控制关注带记忆的闭环动态，监测关注持续观测。由此自然得到“采集与预处理数据—构造输入输出—辨识并验证—部署到具体任务”的通用流程，而不是把某个网络结构当作普遍答案。[pdf:E06]（PDF 物理页 8，Figs. 8–9）

## § 4 — 核心 Intuition

核心 intuition 是：当 PEC 的内部结构无法可靠取得时，不必先完整复刻厂商控制器，仍可利用具有足够激励和覆盖度的输入输出数据，学习目标应用真正需要的动态行为。物理知识不是非黑即白；已知多少就保留多少，剩余部分再由数据补齐。模型选择的本质不是追求单一最高 accuracy，而是在 dynamics fidelity、interpretability、data requirement、computational cost 和 deployment constraint 之间做应用相关的取舍。

这一 intuition 的成败取决于“数据是否真的包含待部署场景中的动态信息”。论文的 black-box 辨识写法最终仍是用观测误差选择结构、阶次和参数，而不是从有限数据自动恢复全部物理。[pdf:E07]（PDF 物理页 9，Eqs. (9)–(11) 及其后模型选择讨论）

## § 5 — 具体方法与完整 Pipeline

这是一篇 overview，没有提出单一可复现算法。它给出的更像一条面向 PEC 的建模决策 pipeline：

1. **定义对象与任务。** 明确 converter topology、grid-following/grid-forming/grid-supporting 控制模式，以及目标是 stability、fault diagnosis、protection、optimization/control 还是 prediction/monitoring。不同任务要求保留的时间尺度和输出不同。
2. **确定知识边界。** 若拓扑、控制和参数充分已知，优先 white-box；若只知道部分方程或结构，用 grey-box 辨识未知部分；若内部知识受 proprietary 限制或难以表达非理想动态，再用 black-box。
3. **采集与整理数据。** 数据可以来自 simulation、real-time measurement 或 historical records；随后进行 filtering、missing-data estimation、transformation、quality assurance、feature engineering 和 feature extraction。[pdf:E06]（PDF 物理页 8，Fig. 9）
4. **建立动态映射。** 依据数据与任务选择 time-series/transfer-function、Hammerstein/Wiener/NARX、kernel、ANN/RNN/LSTM、ensemble 或 hybrid/physics-informed 结构。不能只按模型名选择：论文的横向比较指出，black-box 适合复杂非线性但可解释性弱且可能过拟合，grey-box 平衡物理与数据但需要领域知识，white-box 便于精确设计却依赖完整系统知识且开发耗时。[pdf:E08]（PDF 物理页 10，Table IV）
5. **估计、验证和部署。** 用 system-identification algorithm 估计模型，评价预测与动态复现性能，必要时迭代模型学习，再部署到具体应用。论文列举的应用谱系从 stability assessment 延伸到 fault detection/diagnosis/protection、optimization/control 和 prediction/monitoring。[pdf:E10]（PDF 物理页 13，Fig. 10、Fig. 11 与 Sections V-A/V-B）
6. **闭环使用时保留记忆与实时约束。** 静态 supervised mapping 不能替代动态控制；作者用 RNN/LSTM 说明控制模型需要利用历史信息，并列举 data-driven controller、predictive control、DRL 和 decentralized control 等路线，但并未给出统一控制器实现或统一实时 benchmark。[pdf:E11]（PDF 物理页 14，Sections V-C/V-D）
7. **检查落地条件。** 数据质量、隐私、interpretability、uncertainty、computational load、latency、synchronization、持续更新和 cyber-security 都会决定模型能否进入 safety-critical PEC。作者特别指出，实时系统需要 simplification、parallel processing 或 hardware acceleration，但这些只是方向，并非本文完成的硬件实现。[pdf:E12]（PDF 物理页 15，Section VI-A 至 VI-C）

举一个具体例子：若要为闭源 grid-tied inverter 构建故障期间的动态 surrogate，先记录 PCC 电压、频率、参考值和输出电流/功率的扰动轨迹；用事件类型与工作点划分训练、验证和真正未见测试集；再分别训练一个有物理状态约束的 grey-box 模型和一个带历史窗口的 NARX/LSTM black-box；评价多步 rollout、故障切除后的恢复轨迹、跨工作点误差和 inference latency；只有在未见事件上仍稳定且满足目标控制周期，才进入在线监测或控制辅助。这个例子是基于论文框架的复现设计，不是作者报告的统一实验。

对 EMT + FPGA 读者还要保留一个重要边界：本文没有规定统一的开关/事件处理、离散时间推进、多速率调度、dependency graph、定点数格式、FPGA 映射、资源占用、时钟频率或确定性 WCET，也没有提供自己的 FPGA/HIL 执行平台。它只说明 detailed switching EMT 需要很小时间步、数据驱动模型可能降低在线评估成本，以及 hardware acceleration 可能帮助满足实时约束；不能把这些方向性论述外推为已证明的 FPGA 实时能力。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文是综述，没有一条由作者提出并验证的统一核心数学推导，也没有可归因于本文的新 theorem、收敛证明或统一 converter surrogate。因而本节不编造“综述的统一数学”。论文中的公式只是用同一语言解释三类建模边界。

white-box 从状态与输出方程开始：

\[
\dot{x}=f(x,u), \qquad y=g(x,u),
\]

线性化后写为 \(\dot{x}(k)=Ax_k+Bu_k,\ y(k)=Cx_k+Du_k\)。这里 \(x\) 是状态、\(u\) 是控制输入、\(y\) 是输出，\(A,B,C,D\) 承载已知系统动态；工程上可以由工作点 Jacobian、器件参数和控制环参数建立。[pdf:E04]（PDF 物理页 6，Eqs. (1)–(4)）

grey-box 在已知 state-space 部分外增加未知项：

\[
\dot{x}(k)=Ax_k+Bu_k+B_{uc}u_{uc},\qquad
y(k)=Cx_k+Du_k+D_{uc}u_{uc}.
\]

\(A,B,C,D\) 表示物理上已知的部分，\(B_{uc},D_{uc}\) 与 \(u_{uc}\) 表示需要通过实验数据估计的不确定参数或输入。直觉是保留可信机理，只让数据解释残差或未知环节。[pdf:E05]（PDF 物理页 7，Eqs. (6)–(7)）

black-box 将观测写成 \(y(k)=g(x_k,\theta)+e_k\)，其中 \(e_k\) 是测量噪声，\(g\) 的结构与参数 \(\theta\) 都要从数据确定。[pdf:E06]（PDF 物理页 8，Eq. (8)）随后以预测 \(\hat y(k|\theta)\) 与观测的均方误差构造 least-squares 目标：

\[
\hat{\theta}_N=\arg\min_\theta V_N(\theta,Z^N),\qquad
V_N=\frac{1}{N}\sum_{t=1}^{N}\|y(t)-\hat y(t|\theta)\|^2.
\]

它说明“data-driven”仍需先选 model class、order 和 validation criterion；仅让训练误差最小并不自动保证跨事件、跨工作点或闭环稳定。[pdf:E07]（PDF 物理页 9，Eqs. (9)–(11)）

## § 7 — 实验设计与结论

本文没有作者自建 benchmark、统一数据集、控制实验、ablation 或统计 meta-analysis。它的“验证”是对文献案例和比较表的叙述性综合，因此不能像方法论文那样把综述结论理解为同一测试条件下的性能排名。

- **问题：如何按内部知识程度组织 PEC 动态模型？** → **综述设计：** 用 Fig. 6、Tables I–V 对 white/grey/black-box 的结构、方法、应用验证方式、优缺点进行归类。→ **答案：** 三类模型形成连续的知识—数据谱系，不存在对所有任务最优的一类；Table IV 明确显示 interpretability、domain knowledge、data volume 和 nonlinear capability 的交换关系。[pdf:E08]（PDF 物理页 10，Table IV）
- **问题：为什么大规模 PEC 系统需要 learned surrogate？** → **综述设计：** 对照 switching EMT、phasor、dynamic phasor 和 data-driven 的时间步、保真度与知识要求。→ **答案：** detailed EMT 和基础 phasor 各有不可忽略的尺度缺口，数据驱动方法可作为中间层，但其有效性仍受训练数据覆盖约束。[pdf:E09]（PDF 物理页 12，Section IV 末尾）
- **问题：数据驱动模型能服务哪些 power-system task？** → **综述设计：** 按 stability、fault/protection、optimization/control、prediction/monitoring 整理既有研究与典型 schematic。→ **答案：** 文献已覆盖从参数辨识、稳定区域估计到故障分类、islanding detection、frequency control 和 power-quality monitoring 的广泛任务，但这些是不同论文在不同设备、数据与验证平台上的结果，不能相互直接比较。[pdf:E10]（PDF 物理页 13，Fig. 10、Fig. 11 与 Sections V-A/V-B）[pdf:E11]（PDF 物理页 14，Sections V-C/V-D）
- **问题：为什么应用很多，工业落地仍有限？** → **综述设计：** 汇总 data requirement、interpretability/accuracy、real-time implementation、digital twin、practical deployment、expert knowledge、open dataset 与 cyber-security。→ **答案：** 作者的结论不是“ML/AI 已取代传统模型”，而是数据质量、model clarity 和 real-time requirement 仍是显著障碍；实际研究还需证明在哪些 PEC 场景中 data-driven 方法确实优于传统方法。[pdf:E12]（PDF 物理页 15，Section VI）[pdf:E13]（PDF 物理页 17，Future Directions 与 Conclusion）

因此，这篇综述能够证明“方法与应用版图已经广泛存在、关键工程约束尚未解决”，但不能证明某一 ML/AI 架构在相同条件下全面优于 physics-based model，也不能证明任一 reviewed model 已满足通用 safety-critical 实时部署要求。

## § 8 — Take-aways

**5 句话：**

1. PEC 动态建模的第一选择变量是内部物理知识与目标任务，而不是 neural-network 名称。
2. white-box、grey-box、black-box 构成从机理到数据的连续谱，各自交换 interpretability、开发成本、data requirement 和 nonlinear capability。
3. 数据驱动模型已被用于稳定性、故障/保护、优化控制和预测监测，但文献结果来自异构设备、工况和验证平台。
4. detailed EMT 的尺度成本为 learned surrogate 提供了动机，却不自动赋予 surrogate 跨事件可靠性或实时确定性。
5. 数据覆盖、透明度、latency/synchronization、实际部署和 cyber-security 是比单一平均误差更关键的未闭合问题。

**3 句话：**

PEC data-driven modeling 的价值，是在闭源控制和大规模计算之间学习任务相关的动态行为。最合理的路线通常不是纯黑盒，而是按已知物理多少选择 white/grey/black-box，并在未见扰动上验证动态 rollout。论文给出了完整研究地图，却没有统一 benchmark 或硬件实时证据，因此适合作为问题分类入口，不适合作为某个模型胜出的性能证明。

**1 句话：**

这篇综述最重要的提醒是：能拟合 PEC 数据不等于已经获得可解释、可迁移、可实时部署且安全的动态模型。

## § 9 — 最脆弱的假设

最脆弱的假设是：训练与验证数据对部署中真正重要的 PEC 动态具有足够 excitation 和 coverage。作者在定义 data-driven model 时就假设数据包含足以描述被建模系统 physics 的信息；如果故障保护、限幅、control-mode transition、弱电网耦合或厂商隐藏逻辑没有被触发，模型即使在常规数据上误差很小，也可能根本没有学到决定稳定性的状态转移。[pdf:E02]（PDF 物理页 3，Introduction 对 data-driven model 的前提）

该假设在实际中容易失效：严重故障稀少，安全限制不允许随意激励商业设备，现场传感器存在噪声、丢包和时间同步误差，converter firmware 还可能更新；random train/test split 又会把同一工作点附近的片段同时放入训练和测试，制造虚假的泛化感。论文为“应用已经广泛”提供了大量文献案例，却没有建立共同的数据覆盖标准、跨设备外推测试或统一 uncertainty calibration。作者自己把 comprehensive dataset、open repository、small-data learning、interpretability、real-time constraint 和 cyber-security 列为未来重点，并承认 academic/industrial practical implementation 仍有限。[pdf:E13]（PDF 物理页 17，Future Directions）

因此，一旦 coverage 假设不成立，综述中最有吸引力的承诺——用有限内部知识获得可用于 stability/control/protection 的动态行为——就会直接失效；模型可能只是在已见轨迹附近插值。

## § 10 — 最小复现实验

一周内最值得复现的不是全部应用，而是验证“一个 black-box dynamic surrogate 是否真的学到未见扰动下的 PEC 动态”。论文指出已有 commercial single-phase 和 three-phase PEC 的 real hardware-in-the-loop 数据可公开取得，可把该数据作为起点。[pdf:E13]（PDF 物理页 17，对公开 real-HIL data 的说明）

可执行方案如下：

1. 从同一台 converter 的数据中选取电压/频率或功率参考扰动，输入包含参考值、PCC 电压及历史输出，输出选择电流或有功/无功功率。
2. 实现一个线性 ARX baseline 和一个小型 NARX 或 GRU surrogate；不做大规模 hyperparameter search。
3. 按“完整事件”分割数据，而不是随机切样本：训练集保留常规阶跃，测试集整段留出不同幅值、不同初始功率或不同 grid condition。
4. 同时测 one-step error、多步 free-run rollout error、峰值与settling behavior、是否出现发散，以及单次 inference latency。若可取得故障或 mode-transition 数据，把它作为完全未见测试，不混入训练。
5. 支持核心 claim 的最低结果是：非线性 surrogate 在整段未见事件上持续优于 ARX，能够保持有界 rollout 并复现关键暂态方向，同时 inference latency 有进入目标仿真步长的余量。反驳结果是：优势只存在于随机切分或 one-step prediction，一旦 free-run 或跨工作点就发散/退化到不优于 ARX。

这个实验只能验证“有限范围内的数据驱动动态拟合是否有用”，不能证明通用 grid stability、保护正确性、FPGA 可实现性或确定性 WCET。

## § 11 — 最强反例设计

最强反例是构造一个训练数据中看起来连续、但会触发隐藏控制逻辑切换的 deployment set。训练数据只覆盖 grid-following 正常运行与小扰动；测试时同时改变弱电网阻抗、初始功率和 voltage sag 深度，使 converter 进入 current limiting、fault ride-through、PLL 失锁边缘或 grid-supporting mode transition。再加入可控的 sensor delay、timestamp skew、少量 missing samples 和幅度受限的对抗性测量偏差。

攻击的判据不是平均 RMSE 略升，而是比较：

- learned model 是否错误预测稳定，而真实 HIL 轨迹出现 sustained oscillation、保护动作或恢复时间显著改变；
- one-step error 仍小的时候，free-run trajectory 是否积累相位误差并越过安全边界；
- uncertainty 或 confidence 是否在失效前给出警报；
- grey-box 物理约束模型是否比更高容量 black-box 更晚失效。

若 black-box 在 IID 数据上显著优于 baseline，却在这个集合上静默给出高置信度错误，就出现了对综述核心应用叙事的具体替代解释：报告的性能可能主要来自 operating-region interpolation，而不是获得了可跨事件使用的 converter dynamics。论文关于 latency/synchronization、数据偏差与 cyber-security 的讨论说明这种反例不是人为刁难，而是 safety-critical deployment 的真实风险前提。[pdf:E12]（PDF 物理页 15，Sections VI-A 至 VI-C）[pdf:E13]（PDF 物理页 17，cyber-security 与 reliability future directions）

## § 12 — Follow-up Research Idea

**候选想法：coverage-aware、可拒答的 hybrid dynamic surrogate。** 这里不声称 novelty，因为本卡没有对 conformal prediction、safe learning、hybrid system identification 和 converter validity monitoring 做充分的相邻文献检索。

（a）未满足的需求不是再降低一点平均 RMSE，而是让模型在 safety-critical stability/control/protection 中知道“当前轨迹是否超出了可验证范围”，并在超界前拒答或切换到保守 physics-based fallback。

（b）电力电子与电力系统领域通常用跨工况严谨验证、闭环安全、实时工程可实现性和真实硬件价值评价高影响工作。若能把动态 surrogate 的适用域、实时监测和失败处置统一成可测试 contract，就比单纯更换 NN architecture 更接近这些评价标准，也直接回应论文识别的数据、透明度、实时和可靠性缺口。

（c）可以借鉴四个相邻方向：hybrid automata 用于表示 control-mode transition；active system identification 用最少安全激励扩展覆盖；conformal/ensemble uncertainty 用于在线校准“像不像训练域”；reachability 或 barrier certificate 用于约束 fallback 触发前的安全边界。模型输出不只是一条预测轨迹，还包括 coverage certificate、当前有效 mode 和是否必须 abstain。

（d）第一个证伪实验：在 real-HIL converter 上按工作点、grid impedance、fault severity 和 mode transition 做 leave-one-region-out 测试。如果 coverage score 不能在 rollout 明显偏离真实轨迹之前稳定升高，或拒答机制虽然安全却在大多数正常工况中频繁触发，使系统失去实用性，这个想法就被证伪。

（e）它与本文整理的大多数工作之实质区别，是把研究目标从“离线学一个更准的输入输出映射”改成“在线维护一个可审计的动态模型有效性边界，并把未知状态作为一等输出”。digital twin、open dataset 和 hardware acceleration 仍可作为实现手段，但不再是目标本身。这个方向直接对准作者在结论中确认的数据质量、model clarity、real-time requirement、practical implementation 和 cyber-security 障碍。[pdf:E13]（PDF 物理页 17，Future Directions 与 Conclusion）
