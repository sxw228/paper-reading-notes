# A Survey of Power System State Estimation Using Multiple Data Sources: PMUs, SCADA, AMI, and Beyond

作者：Gang Cheng；Yuzhang Lin；Ali Abur；Antonio Gómez-Expósito；Wenchuan Wu  
出处：IEEE Transactions on Smart Grid  
年份：2023  
DOI：10.1109/TSG.2023.3286401  
Zotero key：44RJP3FJ  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是“再发明一种 state estimation（SE）算法”，而是一个更上层的工程问题：当电力系统同时拥有 SCADA、PMU、AMI、IED、MU、micro-PMU、伪量测、虚拟量测以及其他非传统数据时，怎样理解这些数据的互补关系、怎样分类已有融合方法，以及哪些接口问题仍没有被解决。作者把 SE 的任务界定为：利用不完美的测量和系统模型，恢复表征实时运行状态的一组状态变量；在输电 EMS 中它是基础功能，在分布式能源持续增长的配电系统中也正在从“可选”变为“必要”。论文摘要把多源融合的主要矛盾概括为多类型传感器协同布点、多报告速率与不同步、测量量类型不同、测量相关性、在线与历史数据结合，以及系统和测量不确定性。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

问题的重要性来自时间尺度和观测能力的巨大错位。论文给出的典型量级是：SCADA 通常每 2–5 s 报告一次，PMU 最快可达每秒 60 个样本，而 AMI 常见更新周期为 15 min 或 1 h；这些设备不仅采样快慢不同，报告时刻也不协调，因此在一次 SE 执行时刻往往不存在真正完整的“同一时刻快照”。同时，SCADA 主要给出电压幅值和有功/无功功率，PMU 给出电压、电流相量；把它们简单拼接会遇到非线性与线性模型混合、量纲和数量级不同、初始化困难、精度等级与权重悬殊等问题。[pdf:E02]（PDF 物理页 2，Fig. 1 下方的 challenges 2–6）

作者因此把全文按“数据源 → 输电 SSE → 输电 DSE/FASE → DSSE → 计算与数据要求 → 未来方向”展开，并用同一 taxonomy 连接测量、问题、方法和挑战。[pdf:E03]（PDF 物理页 3，Section I 的 scope、contributions 与全文结构）配电侧的工程价值更直接：实时量测稀疏时，历史 smart meter 数据、典型负荷曲线或学习模型可生成伪量测以恢复可观测性；零注入等物理约束形成虚拟量测，可在不增加传感器投资的情况下提高冗余度。代价是伪量测不确定性更大、权重更小，而把极高精度的虚拟量测与低精度伪量测放进同一正规方程又可能造成病态。[pdf:E04]（PDF 物理页 4，Sections II-C 与 II-D）因此，多源 SE 的价值不是“数据越多越好”，而是让不同时间尺度、物理含义和可信度的数据在同一个状态推断中真正可比较、可校准和可追责。

## § 2 — 前人工作与不足

在这篇综述之前，SE 本身已有成熟传统：输电系统已有 static state estimation（SSE）、dynamic state estimation（DSE）和 forecasting-aided state estimation（FASE）的算法综述；配电侧已有 DSSE、smart meter 数据分析、meter placement、WAMS/SCADA 融合与 corrupted measurement 处理等专项综述。作者认为缺口不在“没人讨论过这些方法”，而在已有综述多按单一算法族、单一设备或单一问题组织，尚未同时覆盖已有与新兴测量类型、抽象多源融合的共同挑战，并用同一分类框架比较输电 SSE、输电 DSE/FASE 和 DSSE 的解决路径。[pdf:E03]（PDF 物理页 3，Section I 的 prior surveys、scope 与 contributions）

论文据此刻意收窄范围：单一测量类型的 SE 通常不纳入，除非它能解释多源融合或使用了高度新颖的数据类型。它的三个直接贡献是：总结测量源与多源融合引入的独特挑战；按 SE 问题类型和所处理挑战建立 taxonomy；讨论 power-electronics-dominated system、integrated energy system、cyber-physical system 与 IoT 背景下的研究空白。[pdf:E03]（PDF 物理页 3，contribution items 1–3）这是“重新组织和比较证据”的贡献，不是新 estimator、新数据集或新的统一定理。

已有具体路线各自能解决一部分问题，但存在结构性不足。例如输电 SSE 中，PMU buffering 能用一段高频样本的均值和方差抑制噪声，却会在 buffer 过长时把真实状态变化混入平均值；estimator switching 能在 SCADA 到达时运行非线性 WLS、仅 PMU 到达时运行线性估计，但必须依赖上一时刻产生的 pseudo-SCADA 来恢复可观测性。[pdf:E05]（PDF 物理页 5，Section III-B）直接、并行和顺序三类 hybrid state estimation（HSE）能够组合 SCADA 与 PMU，却分别承受重新构造 Jacobian、PMU 子问题不可观、坐标变换误差、估计器间相关性以及两级误差传播等代价。[pdf:E06]（PDF 物理页 6，Fig. 2 与 Section III-C）

配电侧已有伪量测、compressive sensing、matrix/tensor completion、sparse tracking、Bayesian inference、ANN 和 smart-inverter grid probing 等路线；taxonomy 显示它们都在借助历史信息、低维结构、学习或主动 probing 缓解实时观测稀疏。[pdf:E02]（PDF 物理页 2，Fig. 1 的 DSSE method families）因此，前人工作不是“没有考虑多源数据”，而是大量解决方案仍针对特定设备对和特定时标，缺少任意传感器类型都能复用的通用理论。

## § 3 — 重建作者的思考路径

可以从论文出现前已经存在的工程事实，逆向重建作者的思考路径。

第一步，先把 SE 看成“状态、观测和模型的契约”，而不是一个固定的 WLS 程序。SCADA、PMU、MU、AMI、FTU、micro-PMU 和 behind-the-meter 数据分别提供不同变量、精度和时标；其中 MU 的采样值可用于电磁暂态和本地保护，而 AMI 往往只能提供慢速或历史信息。[pdf:E03]（PDF 物理页 3，Section II-A）[pdf:E04]（PDF 物理页 4，Section II-B）相关性的处理以及温度、热网、气网和 AC/DC 侧量测的尝试进一步说明，“数据源”可以跨越传统电气量和单一能源网络。[pdf:E07]（PDF 物理页 7，Fig. 3 与 Section III-E）

第二步，意识到新增传感器同时带来冗余和不一致。冗余有利于滤噪、坏数据识别和可观测性，不一致则体现在时钟、报告率、坐标表达、误差统计和网络模型上。于是分类的第一轴不应是某个具体算法名，而应是“它在解决哪一种融合失败”：布点、异步、多测量量、相关性、实时稀疏，还是不确定/缺失/延迟/坏数据。Fig. 1 正是把测量源、SE 问题、方法族和挑战放在四列中建立对应关系。[pdf:E02]（PDF 物理页 2，Fig. 1）

第三步，再按运行目标区分问题。输电 SSE 假设准稳态，可以接受 buffering；输电 DSE/FASE 要在接近 PMU 报告率的频率下追踪状态，不能简单缓存高频数据，只能预测慢速数据或慢速状态。[pdf:E08]（PDF 物理页 8，Section IV 与 Fig. 4）一旦传感器故障、通信拥塞或带宽限制带来 missing/delayed data，还必须把缺失过程或恢复模型纳入 estimator。[pdf:E09]（PDF 物理页 9，Section IV-B 与 Eq. (8)）DSSE 则首先面对实时观测不足，因而伪量测、稀疏恢复和学习方法更居核心。[pdf:E10]（PDF 物理页 10，Section V）这些方法进一步分成 pseudo-measurement、sparsity-based、learning-based 与 grid probing，并分别依赖历史分布、低维结构、训练数据或主动激励。[pdf:E11]（PDF 物理页 11，Section V-B）面对 DSSE 的多报告率，又可选择 down-sampling、slow measurement fill-in、state filtering 与 estimator switching。[pdf:E12]（PDF 物理页 12，Section V-C）

第四步，把算法选择理解为一组代价交换：直接融合减少后融合步骤，却增加统一 measurement function 的难度；并行融合模块化，但要处理两个估计结果的交叉相关；顺序融合易复用既有估计器，却可能放大前一级误差。对不确定、missing/delayed/bad data，可选 prediction、robust estimator 或 interval estimation，但它们分别引入模型偏差、计算成本或区间可信度问题。[pdf:E13]（PDF 物理页 13，Section V-D）decentralized SE 可并行加速，却在分区边界因冗余降低而更脆弱。[pdf:E14]（PDF 物理页 14，Section VI.4）

最后，作者从这些反复出现的接口问题推出未来方向：从离散齐次“扫描”走向连续时间异步事件；从朴素外推走向可验证的状态/量测预测；显式处理未知且时变的误差统计、模型错误和多解；联合规划传感器与通信；并建立可接入任意测量类型的通用融合理论。[pdf:E15]（PDF 物理页 15，future directions 1–9）在电力电子主导系统中，这条路线进一步延伸到基于 RMS 模型的相量数据与基于 EMT 模型的 sampled-value 数据融合。[pdf:E16]（PDF 物理页 16，future direction 10）这条思路并不以本文的贡献为前提，而是从设备演进、失败模式和已有方法的重复结构自然推出来的。

## § 4 — 核心 Intuition

这篇综述的核心 intuition 是：多源 SE 的难点不在把更多数字送进 estimator，而在先统一“这些数字代表哪个状态、对应哪个时刻、依赖哪个物理模型、误差之间怎样相关”。只要时间、物理量和可信度没有对齐，更多数据会制造过度自信、病态甚至发散；只有把不同融合失败按共同挑战组织起来，才能看清哪些方法是可迁移机制，哪些只是某一设备对的 ad-hoc 修补。[pdf:E02]（PDF 物理页 2，Fig. 1 与 challenges）[pdf:E15]（PDF 物理页 15，future direction 7）

## § 5 — 具体方法与完整 Pipeline

本文给出的不是一个可直接运行的软件 pipeline，而是一套用于选择和审查多源 SE 方案的完整分析 pipeline。以“配电网同时收到 SCADA、micro-PMU 和 AMI，且希望在较快节拍上估计三相电压状态”为例，可以按以下顺序使用这套框架。

1. **登记测量源及其物理含义。** SCADA/FTU 提供电压幅值、电流幅值和有功/无功；micro-PMU 提供同步电压、电流相量；AMI/SM 可提供用户电量、相别、电压、电流、功率和功率因数，但报告率通常受通信和存储约束；历史 AMI 还可生成伪量测。零注入、开关两端零压降等物理约束则作为虚拟量测，而不是普通带噪传感器。[pdf:E04]（PDF 物理页 4，Sections II-B–II-D）

2. **确定估计问题和目标时标。** 若只估计一个准稳态快照，属于 SSE；若需要通过状态转移模型追踪暂态，是 DSE；若用前一时刻提高准稳态精度，是 FASE；配电系统绝大多数既有工作仍属于 SSE。DSE 的 prediction step 先由上一状态预测，filtering step 再用最新量测校正；FASE 数学形式相近，但目标不是解析机器内部暂态，而是改善准稳态跟踪。[pdf:E08]（PDF 物理页 8，Section IV）

3. **先处理时间，不伪造“同时性”。** SSE 可缓存多个 PMU scan，取统计量后与最近 SCADA scan 结合；如果 SE 执行频率接近 PMU，则应在量测类型到达时切换 estimator。DSE/FASE 可采用 multi-step state prediction：分别运行 SCADA 与 PMU estimator，再融合状态；也可采用 multi-step measurement prediction：先把缺失的慢速 SCADA 预测到 PMU 时标，再在单一 hybrid estimator 中融合。[pdf:E05]（PDF 物理页 5，Section III-B）[pdf:E08]（PDF 物理页 8，Fig. 4）

4. **选择融合层级。** Direct measurement fusion 把不同测量直接送入一个 hybrid estimator；parallel state fusion 分别估计 SCADA state 与 PMU state，再融合；sequential measurement-state fusion 先运行一个 estimator，把结果作为第二个 estimator 的输入。Fig. 2 同时展示了这三类结构；选择时要显式检查 PMU 子问题是否可观、坐标变换是否放大误差，以及第一阶段的不确定度是否完整传到第二阶段。[pdf:E06]（PDF 物理页 6，Fig. 2 与 Section III-C）

5. **保留相关性而非默认对角协方差。** PMU 与 SCADA 可能来自同一组 VT/CT，buffer 内的 PMU 还具有时间和空间相关性。论文总结的做法包括 VAR、unscented transformation 和 point estimation，并用稠密或非对角 covariance matrix 表达相关误差。Fig. 3 展示了先预测 PMU 与协方差、再把 SCADA 和 PMU 组成 block-diagonal covariance 的一类框架。[pdf:E07]（PDF 物理页 7，Fig. 3 与 Section III-D）

6. **对不可观测部分选择信息来源。** DSSE 可以生成伪量测，也可以利用 compressive sensing、matrix/tensor completion、sparse tracking、Bayesian inference、ANN 或 smart-inverter grid probing。前三者必须验证 sparsity/low-rank；学习方法必须接受大量历史数据和训练成本；grid probing 则把不可观测负荷识别改成有约束的主动系统辨识问题。[pdf:E11]（PDF 物理页 11，Section V-B）[pdf:E12]（PDF 物理页 12，P2L 与 Section V-C）

7. **处理缺失、延迟、坏数据与模型不确定性。** 缺失/延迟可用预测、Kalman smoothing、EM 或低秩恢复；坏数据可用 SHGM、IR-WLS、MNMR 等 robust estimator；若目标是给出状态边界，可使用 interval state estimation。这里的输出不应只是一点估计，还应包含与误差模型相符的不确定度。[pdf:E09]（PDF 物理页 9，Section IV-B）[pdf:E13]（PDF 物理页 13，Section V-D）

8. **最后检查计算和数据约束。** Kalman-filter DSE 需要显式处理稠密协方差且执行频率高，通常比 WLS SSE 更重；robust estimator 往往以更高计算复杂度换取抗 gross error；线性 measurement model 可免迭代，而 nonlinear model 通常需逐次线性化；decentralized SE 可并行，但边界更易受坏数据影响；data-driven SE 把成本移到离线训练，在线前向计算可能较轻。[pdf:E14]（PDF 物理页 14，Section VI）

对 EMT + FPGA 关切必须保持边界：论文没有提出统一离散格式、开关事件处理算法、FPGA dataflow、定点字长、流水线、片上存储布局、时序收敛、资源占用、HIL 平台或实时步长，这些均为**未报告**。它只指出 MU 的 sampled-value 数据适合局部电磁暂态 DSE/保护，并在未来方向中明确提出应研究基于 RMS 模型的相量数据与基于 EMT 模型的采样值在 DSE 中的融合。[pdf:E10]（PDF 物理页 10，Section IV-D.2）[pdf:E16]（PDF 物理页 16，future direction 10）因此，不能从本文推出任何 FPGA 可实现性或实时性能结论。

## § 6 — 核心数学推导（无形式化数学则跳过）

**本文是综述，没有一条由作者提出并统一推导的核心数学链。** Eq. (1)–(11) 是为解释被综述方法族而摘录的代表性形式，不是本文的新定理或新 estimator。下面只说明这些公式的工程含义，避免把“示例方程”误写成本文贡献。

在 parallel state fusion 中，Bar-Shalom-Campo（BSC）形式把两个状态估计线性加权：

\[
\hat{x}^{\mathrm{final}}
=W_1\hat{x}^{\mathrm{scada}}+W_2\hat{x}^{\mathrm{pmu}} .
\]

\(\hat{x}^{\mathrm{scada}}\) 与 \(\hat{x}^{\mathrm{pmu}}\) 分别是 SCADA 和 PMU estimator 的状态向量，\(W_1,W_2\) 是对应权重，输出为 \(\hat{x}^{\mathrm{final}}\)。直觉是“先各自理解测量，再在 state space 合并”，但权重只有在两个估计的不确定度和交叉相关被正确表达时才可靠。[pdf:E06]（PDF 物理页 6，Eq. (1) 及其变量定义）

输电 DSE/FASE 的 multi-step state fusion 使用相似形式：

\[
\hat{x}^{(k_p)}_p
=\alpha_s\hat{x}^{(k_p)}_{p|s}
+\alpha_p\hat{x}^{(k_p)}_{p|p},
\]

其中两个分量分别来自按 PMU 节拍推进的 SCADA estimator 和 PMU estimator，\(\alpha_s,\alpha_p\in\mathbb{R}^{N\times N}\)，\(N\) 为状态数。这里真正解决的是“慢速 SCADA 在中间时刻没有新量测”时如何保持一个可融合的 state prediction，而不是把旧 SCADA 当作当前值。[pdf:E08]（PDF 物理页 8，Eq. (2)；变量定义续见物理页 9）

论文还用一个 switched system 说明模型选择。Subsystem I 采用

\[
x_{k+1}=x_k+w_k,\qquad z_k=h(x_k)+v_k,
\]

即 identity transition 与零 control input；Subsystem II 采用

\[
x_{k+1}=x_k+J^{-1}(u_{k+1}-u_k)+w_k,\qquad z_k=h(x_k)+v_k,
\]

其中 \(x_k,z_k,u_k\) 分别为状态、量测和控制输入，\(w_k,v_k\) 为过程噪声和量测噪声，\(J\) 为潮流 Jacobian。切换判据选择使预测量测残差 \(\lVert h_\alpha(\hat{x}_{k-1})-z_k\rVert_2\) 最小的 subsystem。直觉是：系统变化很小时用廉价的 identity model，控制输入发生可解释变化时用线性化潮流模型；风险是切换判据本身会受 gross error 和模型错误影响。[pdf:E09]（PDF 物理页 9，Eqs. (3)–(7)）

缺失量测的一种形式写成

\[
z=C\,h(x)+v,\qquad
C=\operatorname{diag}\{\gamma_1,\gamma_2,\ldots,\gamma_m\},
\]

其中 \(\gamma_i\) 是 Bernoulli 随机变量。\(C\) 相当于逐通道“是否收到数据”的随机开关，随后可在 EKF 中处理；它表达的是缺失过程模型，而不是坏数据值本身。[pdf:E09]（PDF 物理页 9，Eq. (8) 及变量定义）

配电侧 slow measurement fill-in 的三种代表形式是 stepwise evolution、extrapolation 和 interpolation。设 \(T_p\) 为 SM 报告周期，\(z\) 和 \(t\) 分别索引量测与时刻：Eq. (9) 在下一次报告前保持 \(z_j\)；Eq. (10) 用前一段斜率外推；Eq. (11) 用当前与下一次报告之间的斜率插值。它们能让 estimator 在慢测量未刷新时继续执行，但不能凭公式本身保证 DER 剧烈变化时仍准确。[pdf:E12]（PDF 物理页 12，Eqs. (9)–(11) 与变量定义）

因此，本文数学层面的真正 take-away 不是某个闭式解，而是：同一个多源融合问题会同时涉及 state transition、measurement function、missingness mask、covariance 和 fusion weight；若只对齐其中一项，形式上可计算并不等于统计上可信。

## § 7 — 实验设计与结论

本文**没有统一实验部分，也没有提出新数据集、test system、baseline 实现、消融、统一误差指标、运行时间、硬件资源或实时步长**。作者在 Section VI 明确说明，不能严格比较不同论文的计算成本，因为各文使用的 test system、measurement configuration、data volume、termination tolerance 和 computing resource 不同。[pdf:E13]（PDF 物理页 13，Section VI 开头）因此本节只能按“综述问题 → 综述设计 → 综述答案”总结，不能把被引用论文的单项结果包装成本文实验结论。

- **问题：多源 SE 的共同挑战是什么？ → 综述设计：**把测量源、SE 类型、方法族和挑战放入同一 taxonomy。**答案：**主要挑战集中在协同布点、异步与多速率、测量量异构、相关性、配电实时量测稀疏、不确定与缺失/延迟/坏数据六类。[pdf:E02]（PDF 物理页 2，Fig. 1）
- **问题：输电 SSE 如何融合 SCADA 与 PMU？ → 综述设计：**比较 buffering、estimator switching，以及 direct/parallel/sequential HSE。**答案：**没有单一最优路线；低执行频率可用 buffering，高执行频率更适合 switching，融合层级则在统一建模、不可观测、误差传播和模块复用之间交换。[pdf:E05]（PDF 物理页 5，Sections III-B–III-C）[pdf:E06]（PDF 物理页 6，Fig. 2）
- **问题：DSE/FASE 如何处理低速 SCADA 与高速 PMU？ → 综述设计：**比较 multi-step state prediction/fusion 与 multi-step measurement prediction/fusion，并讨论 missing/delayed data。**答案：**DSE 不能像 SSE 那样简单缓存，因为它需要捕捉动态；必须在状态层或测量层补齐慢时标信息，同时显式处理预测误差、缺失过程和 estimator consistency。[pdf:E08]（PDF 物理页 8，Fig. 4）[pdf:E09]（PDF 物理页 9，Section IV-A–B）
- **问题：DSSE 在实时量测稀疏时怎样恢复状态？ → 综述设计：**比较 pseudo-measurement、sparsity-based、learning-based 与 grid probing。**答案：**这些路线都把“额外信息”从另一处带进来：历史分布、低维结构、训练数据或主动激励；成功与否取决于相应先验是否真实成立。[pdf:E11]（PDF 物理页 11，Section V-B）[pdf:E12]（PDF 物理页 12，P2L）
- **问题：如何应对不确定与坏数据？ → 综述设计：**归纳 prediction、robust estimator 与 interval estimation。**答案：**预测可补数据但可能引入模型偏差；robust estimator 可压制 gross error 但更耗计算；interval estimation 能给出状态边界，但求解与区间可信度仍依赖不确定性模型。[pdf:E13]（PDF 物理页 13，Section V-D）
- **问题：计算与数据需求怎样比较？ → 综述设计：**只做跨方法族的定性比较。**答案：**DSE 通常比 SSE 更重，robust 比 non-robust 更重，nonlinear 比 linear 更重；decentralization 提供并行性但削弱边界冗余；data-driven 方法需要大量离线数据，却可能降低在线计算量。[pdf:E14]（PDF 物理页 14，Section VI）

不得外推的范围是明确的：本文没有证明融合必然优于单源，没有给出统一 accuracy gain，没有验证 continuous-time asynchronous fusion，也没有演示 RMS/EMT measurement fusion。最后一项仅作为未来研究空白提出。[pdf:E16]（PDF 物理页 16，future direction 10）

## § 8 — Take-aways

**5 句话：**  
第一，多源 SE 的核心对象不是传感器清单，而是时间、状态语义、物理模型和误差统计之间的对齐。第二，输电 SSE、输电 DSE/FASE 与 DSSE 面对的主矛盾不同，不能复用同一种时间处理策略。第三，direct、parallel、sequential fusion 各有接口和误差传播代价，更多数据不自动等于更可靠。第四，伪量测、稀疏恢复和学习方法都依赖可被反驳的先验，必须验证历史分布、low-rank 或训练覆盖是否成立。第五，真正尚未解决的方向是连续时间异步融合、未知误差与模型错误、传感器—通信联合设计，以及 RMS/EMT 多物理模型数据融合。[pdf:E15]（PDF 物理页 15，future directions 1–10）[pdf:E16]（PDF 物理页 16，future direction 10）

**3 句话：**  
这篇综述把多源 SE 重写为六类融合失败与三类主要 SE 场景的组合问题。它最有价值的地方不是给出冠军算法，而是暴露每条路线依赖的时标、可观测性和误差假设。论文也清楚表明，现有工作仍以设备对的 ad-hoc 方案为主，统一理论和可比较验证尚缺。

**1 句话：**  
多源 state estimation 的本质，是在不同时钟、不同物理量和不同可信度之间建立可检验的共同状态语义。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**不同数据源可以被转换到同一个状态—时间—误差语义中，而且转换所需的网络模型、时间戳与误差统计足够可信。**几乎所有融合路线都依赖它：buffering 假设窗口内状态变化可接受，WLS/WLAV 假设误差分布和 variance 可用，parallel fusion 假设 covariance 足以给出权重，prediction 假设 transition model 可达，data-driven SE 假设历史数据覆盖在线状态。

现实中这组条件很容易同时失效。论文指出传感器可能在连续时间异步到达，真实误差分布可能未知且随工况变化，拓扑和线路参数可能错误，精度等级和量纲差异会造成数值发散，电流幅值还可能导致多解。[pdf:E15]（PDF 物理页 15，future directions 1–5）若这些问题未被识别，多源融合最危险的结果不是“误差稍大”，而是把共同偏差或过期数据重复计算为独立证据，得到看似方差更小、实际更错的状态，并进一步误导 bad-data detection、保护或控制。

论文给出的证据是跨文献的失败模式和未来议程，而不是统一实验。它没有提供一个在真实多源系统上同时注入 clock drift、correlated bias、topology error 和 communication loss 的 benchmark，也没有检验融合结果的不确定度 calibration。因此，这一假设虽被论文准确识别，却没有被本文实证消除。

## § 10 — 最小复现实验

一周内最值得做的不是复现整篇综述，而是验证一个可证伪的核心判断：**在多速率、异步且相关误差存在时，朴素时间对齐会产生虚假精度，而显式建模时间与相关性应更稳健。**以下参数是复现实验设计，不是论文报告值。

1. 选一个可运行 AC power flow 的小型输电或配电 test case，生成 10–30 min 的高分辨率“真状态”轨迹，并从同一组电压/电流真值合成 SCADA 功率、PMU 相量和慢速 SM/AMI 数据。
2. 构造三种 estimator：A 为 latest-sample/hold 的朴素融合；B 为论文 Eq. (9)–(11) 所代表的 slow-measurement fill-in；C 为 state/measurement prediction 加 non-diagonal covariance 的 correlation-aware fusion。实现规模只需覆盖电压幅值与相角，不必复现所有方法族。
3. 分阶段注入时钟抖动、连续时间到达、共同 VT/CT bias、随机丢包和一次轻微 topology error。每次只改变一个因素，再做组合故障。
4. 测量 voltage magnitude/angle RMSE、gross-error 场景下的最大偏差、标称置信区间覆盖率、每步运行时间和 divergence 次数。论文给出的异步、相关性与缺失处理机制可作为实现导航。[pdf:E07]（PDF 物理页 7，Fig. 3）[pdf:E09]（PDF 物理页 9，Eq. (8)）[pdf:E12]（PDF 物理页 12，Eqs. (9)–(11)）
5. 若 C 在相同延迟预算下，随抖动和共同 bias 增加仍保持更低误差且 uncertainty coverage 接近标称值，则支持“必须显式建模时间和相关性”；若 C 只给出更窄 covariance、实际误差不降甚至升高，则反驳该实现的关键 claim。只要这一反例出现，就不应继续扩展到更大系统或 FPGA。

## § 11 — 最强反例设计

最强反例不是单独删掉一台传感器，而是制造“**多源表面独立、实际共享偏差**”的场景：PMU 相量和 SCADA 功率来自同一组 VT/CT，因此共享幅值或相角 bias；通信路径再给两者施加不同且漂移的延迟；同时引入一个未被 estimator 知道的支路参数或 topology error。这样，两个数据源在数值上互相“印证”，但共同指向错误状态。

攻击实验应比较 single-source、假设 diagonal covariance 的 fusion、显式 cross-covariance 的 fusion，以及允许 model uncertainty 的方法。关键判据不是平均 RMSE 一项，而是：融合后是否比最好的单源更差、是否更容易越过保护/控制阈值、以及报告的 covariance 是否仍声称高置信。论文已经指出 SCADA 与 PMU 可能共享 VT/CT、相关性不应忽略，并指出未知误差统计、网络模型错误和多解会破坏 SE。[pdf:E02]（PDF 物理页 2，challenge 4）[pdf:E15]（PDF 物理页 15，future directions 3–5）

如果 diagonal-covariance fusion 在该场景下持续输出更小的 nominal uncertainty，却产生更大的真实误差，那么“增加异构数据自然提高 SE 性能”的宽泛解释就被推翻。更重要的是，这会证明失败来自共同的生成机制而不是简单噪声增大，因而不能靠增加权重调参或更多同源测量修复。

## § 12 — Follow-up Research Idea

电力系统领域的高影响工作通常不仅要求算法上有新意，还要求在可信网络模型、严格故障工况、可复现实验以及面向实际 EMS/保护/控制的时延和可靠性约束下成立。基于本文最脆弱的假设，一个非增量候选方向是：**把多源 SE 从“离散 scan 的设备对融合”重新定义为“连续时间、跨物理模型、可校准的不确定状态轨迹推断”**。由于本卡没有补充检索相关工作，这只是候选想法，**不声称 novelty**。

（a）未满足需求是：SCADA、PMU、AMI 与 MU 以事件流方式异步到达，既可能共享传感器偏差，又分别对应 RMS 与 EMT 物理模型；把它们强行压到离散 scan 会丢失时间信息并掩盖模型冲突。论文明确把 continuous-time asynchronous measurement 和 RMS/EMT measurement fusion 都列为研究空白。[pdf:E15]（PDF 物理页 15，future directions 1 与 10）[pdf:E16]（PDF 物理页 16，future direction 10）

（b）潜在研究价值在于改变问题定义：估计对象不再只是某个离散时刻的电压向量，而是一条带 uncertainty 的连续状态轨迹；每个传感器拥有独立 observation operator、clock model、error model 和物理模型标签。这样可以把 clock drift、correlated bias、missing event 和 model mismatch 作为一等变量，而不是预处理噪声。

（c）可借鉴相邻领域的工具包括 continuous-time factor graph、event-based estimation、hierarchical Bayesian calibration，以及用于跨时间尺度耦合的 multi-model filtering。这里的关键不是把 neural network 再接到 WLS 后面，而是用统一 latent trajectory 连接 RMS 相量和 EMT sampled values，并让模型不一致显式产生可诊断残差。

（d）第一个证伪实验应在实时数字仿真或 HIL 环境中生成同一电力电子系统的 RMS 与 EMT 真值，向 estimator 注入不同步 PMU/SCADA/MU 事件、共同传感器 bias、拓扑错误和 packet loss；与 scan-aligned WLS、multi-step prediction 和单模型 DSE 比较轨迹误差、uncertainty coverage、异常定位率、端到端 latency 与 worst-case deadline miss。若连续时间多模型方法不能在同等计算预算下同时改善 calibration 与暂态跟踪，或者只在已知模型下有效，就应被否证。

（e）它与本文所总结多数工作的实质区别是：不再为“SCADA+PMU”“SCADA+AMI”等设备对分别设计 ad-hoc fusion，也不预设所有测量来自同一物理模型；它以状态轨迹、时间不确定性和模型身份为统一接口。若后续考虑 FPGA，合理分工是先证明连续时间推断的可辨识性和鲁棒性，再把已确认的固定计算核映射到硬件；本文本身没有提供任何字长、资源或时序依据，不能跳过这一证伪顺序。
