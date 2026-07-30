# A Digital Twin Framework With Deep Feature Extraction and Gaussian Process for Multi-Objective Optimization in Semiconductor Manufacturing

- 作者：Chin-Yi Lin；Tzu-Liang (Bill) Tseng；Tsung-Han Tsai
- 出处：*IEEE Transactions on Automation Science and Engineering*，Vol. 23，pp. 1928–1949
- 年份：2026
- DOI：10.1109/TASE.2025.3650620
- Zotero key：4JETCWNK

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文实际属于**半导体制造、工业 AI 与 run-to-run 过程优化**，不是 EMT 仿真或 FPGA 实现论文。它处理的是 SiC 外延生长中的配方搜索：设备有数百个互相耦合的过程变量，而制造方希望用同一组配方同时把外延层厚度偏差和掺杂浓度推向给定目标。作者给出的具体目标是厚度偏差 0、掺杂浓度 20；论文把“厚度优化得很好、但掺杂失控”视为单目标方法在真实制造中的主要缺口。[pdf:E01]（PDF 物理页 1，摘要与 Note to Practitioners）[pdf:E15]（PDF 物理页 15，Section VI）

这个问题重要，不只是因为两个指标“同时存在”。SiC 外延层的厚度、掺杂及其均匀性直接牵涉击穿能力、漏电、导通损耗和可靠性；同一个温度、压力或气体流量动作会同时改变多个结果，因此分别寻找两个单目标最优配方，未必能合成一组可投产配方。论文还强调，传统 DOE 难以扩展到高维变量，物理模型成本高且面对新产品不易适配，而历史数据又可能稀少。[pdf:E03]（PDF 物理页 3，Section II-A）

作者把价值主张分成三层。第一层是**决策目标**：不求完整 Pareto front，而是直接追踪用户给出的 specification target。第二层是**样本效率**：用深层特征把高维输入压到较小 latent space，再让 Gaussian Process（GP）在少样本下提供均值和不确定度。第三层是**制造闭环**：以 wafer-to-wafer 的事件节拍吸收 APC/SPC 数据、更新 surrogate、给出下一片晶圆的配方，并用一个 target-attainment certificate 决定是否停止。[pdf:E01]（PDF 物理页 1，摘要）这些是论文的明确主张；是否已经被真实产线闭环实验充分证明，则要到第 7、9 节再判断。

## § 2 — 前人工作与不足

论文梳理的前人路线包括 DOE、physics-based modeling、传统 ML、deep learning、reinforcement learning、Digital Twin（DT）和多目标优化。作者认为：DOE 在变量多、交互强时试验成本迅速上升；physics-based model 的建模与计算代价高，且未必覆盖新产品和未建模非线性；许多 ML 工作只做单目标、离线回顾或依赖大量标注；deep model 虽表达能力强，却容易受数据量、正则化和训练稳定性影响；已有 DT 工作更多解决架构、监控或模拟问题，没有把带不确定度的多目标配方搜索作为闭环核心。[pdf:E02]（PDF 物理页 2，Introduction）[pdf:E05]（PDF 物理页 5，Section II-C）

最直接的 prior work 是同一作者 2025 年的 MRBORI。MRBORI 复用 XGBoost feature screening，再用单输出 deep-learning surrogate 与 multi-restart Bayesian optimization，一次只优化一个目标。本文保留 DT-to-legacy integration skeleton 和一次性 XGBoost screening，把优化核心换成 MOODFG：共享 deep feature、每个目标一个 GP、给定 target vector 的加权距离，以及基于不确定度的停止证书。论文在 Table I 中明确把“单目标、每次返回一个目标的配方”与“多目标、返回一组同时满足厚度与掺杂的配方”区分开来。[pdf:E04]（PDF 物理页 4，Table I）

这里需要收窄作者对 prior work 的表述。**论文直接陈述** conventional MO-BO 常以 hypervolume 或 scalarization 近似 Pareto front；**基于证据的判断**是，当制造方已经给出确定 target 时，求完整前沿确实可能多做无用搜索。但这并不说明 Pareto 方法本身不能做 target selection，也不说明 deep-feature GP 必然比精心设计的多输出 GP 或其他 representation 更好。本文的实验主要比较特定实现和同一 candidate pool，不能把结果外推成对整个 MO-BO 类别的否定。

## § 3 — 重建作者的思考路径

可以在不预设 MOODFG 的情况下重建这条思路。

第一步，制造工程师从已有 Epi-SiC 经验看到：APC 记录温度、压力、气流等 \(X\)，SPC 在晶圆完成后给出厚度、掺杂等 \(Y\)；一个 \(X\) 动作影响多个 \(Y\)，所以“先优化厚度、再优化掺杂”没有组合闭包。第二步，既有 MRBORI 已经证明同一数据链能做单目标 recipe tuning，但它每次只返回一个目标的解，这把问题暴露为**目标定义错误**，而不只是 optimizer 不够强。[pdf:E03]（PDF 物理页 3，Context and Link to Prior Work）

第三步，工程师会发现原始输入超过 500 个，直接在原空间训练小样本 GP 会遭遇维数灾难；因此先用 XGBoost 排除弱变量，再学习一个对多个输出共同有用的低维 representation。第四步，制造决策不只需要点预测，还需要知道“这组配方是否足够可信，可以发给 RMS/EPCS”，所以每个目标用 GP 输出均值与标准差。第五步，与其让 optimizer 恢复完整 Pareto front，不如把 fab specification 写成 target vector、容差权重和停止阈值，直接寻找一个 recipe。[pdf:E05]（PDF 物理页 5，Section III）

最后还要解决制造数据的节拍问题：APC 的 \(X\) 在运行结束时可得，SPC 的 \(Y\) 可能晚一片或多片才返回。作者因此把“实时”明确限定为 event-time 的 run-to-run 更新，而不是设备内部微秒级或毫秒级控制；迟到标签到达后只更新对应目标 GP，停止检查则要求 incumbent 的所有必要目标已观测。[pdf:E07]（PDF 物理页 7，Fig. 2 及 run-to-run handling）这条思考路径的合理核心是：先把实际决策对象定义成“一组可释放配方”，再让模型结构和数据节拍服务于这个对象。

## § 4 — 核心 Intuition

MOODFG 的 intuition 是：先把数百个工艺变量压到一个让响应更平滑、更容易估计的 latent space，再用每个目标各自的 GP 同时给出“离目标多远”和“对此有多不确定”。optimizer 不去画完整 Pareto front，而是直接寻找一组对厚度和掺杂都接近 specification target、且不确定度足够小的配方。[pdf:E06]（PDF 物理页 6，Fig. 1 与 Simulation Engine）

换成普通语言，它做的不是“找到所有可交换的好方案”，而是“围绕工厂已经指定的落点，找一张风险可接受、能直接下发的 recipe”。深层特征负责让高维问题变得可学，GP 负责把认知不足显式放进决策，target certificate 负责把模型输出变成停止条件。[pdf:E01]（PDF 物理页 1，摘要）

## § 5 — 具体方法与完整 Pipeline

以“一批历史 Epi-SiC 晶圆记录，目标为厚度偏差 0、掺杂 20”为例，完整 pipeline 如下。

1. **形成 wafer-level 数据。** APC 连续信号按晶圆处理窗口聚合为均值、最大值、最后值或 EWMA；SPC 提供厚度和掺杂标签。已知气路滞后或热惯性可加入 lagged features，慢漂移可通过 rolling window、exponential forgetting 或时间 covariate 表示。标签迟到时不做 imputation，只更新已经得到标签的目标 GP。[pdf:E07]（PDF 物理页 7，Fig. 2 与正文）
2. **一次性筛选可控变量。** XGBoost 为输入变量生成 importance \(I_j\)，选择累计 importance 达到阈值 \(\gamma\) 的最小关键子集。真实案例从超过 500 个输入降到 15 个；论文使用 \(\gamma=0.92\)。[pdf:E08]（PDF 物理页 8，Eq. (1) 与 Table II）[pdf:E19]（PDF 物理页 19，Table VII）
3. **学习共享 deep feature。** 两层 ReLU MLP 把筛选后的 \(x\) 映射为 \(z=\phi_\theta(x)\)。实现使用宽度 \([64,32]\)、latent dimension \(k=8\)，输入做 z-score normalization；feature 参数与 GP hyperparameters 通过 marginal likelihood 联合训练。[pdf:E10]（PDF 物理页 10，Eq. (3)）[pdf:E13]（PDF 物理页 13，implementation details）
4. **为每个目标拟合 GP。** 厚度和掺杂各用一个 exact GP，共享 \(z\)，但拥有各自的 ARD-RBF length-scales、signal variance 与 white-noise variance。这样允许两种物理响应有不同平滑尺度和噪声，同时把跨目标共享限制在 representation 层和最终加权距离中。[pdf:E09]（PDF 物理页 9，Eq. (2) 及 surrogate choice）
5. **对 candidate pool 打分。** 把各目标 posterior mean 组成 \(\mu_t(x)\)，posterior standard deviation 组成 \(\sigma_t(x)\)，计算到目标 \(y^\*\) 的加权距离，再加不确定度项形成 \(D_t^{\mathrm{UCB}}(x)\)。标准化输出时 \(W=I\)；若按工程容差设置权重，则 \(w_o=\kappa_o/\tau_o^2\)。选择 certificate 最小的 candidate。[pdf:E10]（PDF 物理页 10，Eq. (5)–(8)）
6. **限制配方步长并执行。** 为避免 run-to-run 大跳变，candidate 通过 \(2\%\)–\(5\%\) 工程范围的 \(\ell_\infty\) trust-region 做 step-limited update；若 certificate 没有改善，则加 proximity penalty 重求。随后 RMS/EPCS 下发配方，设备执行，APC/SPC 回收新数据。[pdf:E10]（PDF 物理页 10，Parameter update and deployment）
7. **增量更新与停止。** 每次加入新晶圆后，用 30 个 joint epochs 更新 feature 与各 GP，再冻结 feature 做 acquisition。若 incumbent 的所有必要实测标签已经到达，且 \(D_t^{\mathrm{UCB}}(x_t)\le\varepsilon\)，就返回一组 deployable recipe；预算耗尽则返回 best-so-far 和决策日志。[pdf:E11]（PDF 物理页 11，Iterative Refinement 与 workflow）

计算依赖是串行的“新标签 → feature/GP 更新 → 冻结模型 → candidate scoring → 下一配方”，不同目标 GP 的 Cholesky 可以并行，但论文未报告实际并行实现。数值上使用 exact GP、double precision、\(10^{-6}\) jitter、Adam 后接一次 L-BFGS；每步复杂度的主项是 \(O(Ot^3)\) 的 exact GP refit 和 candidate pool scoring。[pdf:E13]（PDF 物理页 13，Eq. (16)–(17) 与 complexity）

这不是 EMT 求解器：论文没有电磁暂态网络方程、开关事件、固定仿真步长、多速率电路积分或 HIL。它也没有 FPGA datapath、定点格式、资源占用、时序收敛、板卡型号或硬件部署结果。作者只报告“standard workstation”上的秒级 BO step；因此不能把本方法描述成 FPGA 加速或实时 EMT 技术。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从高维工艺变量到 latent GP

XGBoost 筛选写成

\[
x^\*=\arg\max_{x\subseteq\{x_1,\ldots,x_d\}}\sum_{x_j\in x} I_j,
\qquad
\text{s.t. }\sum_{x_j\in x}I_j\ge\gamma .
\]

直觉是用尽量少的变量覆盖指定比例的累计 importance；它是工程性筛选，不是证明未选变量无因果作用。[pdf:E08]（PDF 物理页 8，Eq. (1)）

筛选后用两层网络

\[
z=\phi_\theta(x)=\mathrm{ReLU}\!\left(W_2\,\mathrm{ReLU}(W_1x+b_1)+b_2\right)
\]

把 \(d\) 维输入压到 \(k\) 维 latent space。对目标 \(o\)，核函数为 ARD squared-exponential 加 white noise：

\[
k_o(z,z')
=\sigma_{o,f}^2
\exp\!\left[-\frac12\sum_{q=1}^{k}
\frac{(z_q-z'_q)^2}{\ell_{o,q}^2}\right]
+\sigma_{o,n}^2\delta_{z=z'} .
\]

每个 \(\ell_{o,q}\) 表示目标 \(o\) 对 latent direction \(q\) 的变化尺度；长度尺度大，说明该方向变化慢或影响小。white-noise 项吸收 metrology noise 和 run-to-run variation。[pdf:E09]（PDF 物理页 9，Eq. (2)）

feature 参数和 GP 参数通过所有目标 negative log marginal likelihood 之和联合训练：

\[
\mathcal L
=\sum_o\left[
\frac12y_o^\top K_o^{-1}y_o
+\frac12\log|K_o|
+\frac t2\log(2\pi)
\right]+\lambda_\theta\|\theta\|_2^2 .
\]

第一项奖励拟合，第二项自动惩罚过于复杂或不稳定的 covariance，第三项是高斯归一化常数，最后一项约束网络权重。[pdf:E13]（PDF 物理页 13，Eq. (17)）

### 6.2 从预测到 target certificate

论文的核心决策量是

\[
D_t^{\mathrm{UCB}}(x)
=\|\mu_t(x)-y^\*\|_{W,2}
+\sqrt{\beta_t}\,\|\sigma_t(x)\|_{W,2},
\]

并选

\[
x_{t+1}\in\arg\min_{x\in X_{\mathrm{pool}}}D_t^{\mathrm{UCB}}(x),
\qquad
D_t^{\mathrm{UCB}}(x_t)\le\varepsilon\ \text{时停止}.
\]

第一项是 posterior mean 到目标的距离，第二项把模型不确定度加成“最坏侧余量”。因此它更准确地说是**风险厌恶的上界证书**：同样接近目标时，模型更确定的 candidate 得分更低。[pdf:E10]（PDF 物理页 10，Eq. (5)–(6)）

这里有一个值得警惕的机制问题。论文多次把第二项称为 exploration bonus，但在“最小化正的不确定度项”时，高不确定 candidate 会被惩罚，而不是被奖励探索。除非还有外部 Sobol 初始化、candidate coverage 或其他探索机制，这个符号结构本身更接近保守 exploitation。这个判断直接来自 Eq. (5)–(6)，不是作者明示结论。

### 6.3 理论保证的真实边界

在每个目标 \(f_o\circ\phi_\theta\) 属于有界核的 RKHS、\(\phi_\theta\) Lipschitz 且参数处于 compact set、输入域 compact、噪声 sub-Gaussian 等假设下，论文给出高概率上界：

\[
\|f(x)-y^\*\|_{W,2}\le D_t^{\mathrm{UCB}}(x)
\]

以及

\[
\min_{1\le t\le T}D_t^{\mathrm{UCB}}(x_t)
=\widetilde O\!\left(\sqrt{\frac{\beta_T\gamma_T}{T}}\right),
\qquad
T_\varepsilon
=\widetilde O\!\left(\frac{\beta_T\gamma_T}{\varepsilon^2}\right).
\]

\(\gamma_T\) 是 information gain；latent space 越紧凑、核越容易学习，通常需要的样本越少。[pdf:E12]（PDF 物理页 12，Eq. (14)–(15) 与 assumptions）

但这个保证是**条件性 proof sketch**，不是对实际 rolling-window、adaptive feature retraining 和概念漂移的无条件保证。论文自己说明 frozen-feature analysis 只在更新之间适用；从一次冻结区间的 GP concentration 推到整个持续改变 representation 的闭环，还需要控制 feature update 所带来的 nonstationarity。把“在 A1–A3 成立时有 rate”写成“真实产线必然全局收敛”会越过证据。

## § 7 — 实验设计与结论

### 问题 1：算法能否在简单已知函数上朝指定 target 搜索？

**实验。** 作者用 \(f_1(x)=\sin x\)、\(f_2(x)=0.5+\cos 2x\)、\(x\in[0,10]\)，目标 \(y^\*=[0,0.5]\)，先均匀随机取 10 点，再做 30 次 incremental update。[pdf:E13]（PDF 物理页 13，Eq. (18) 与 setup）

**答案。** Fig. 4 显示后续红点集中到 target region，说明 pipeline 至少能在一维、光滑、可完全评估的 toy problem 上从探索转向局部搜索。[pdf:E14]（PDF 物理页 14，Fig. 4）它验证的是代码路径和基本 target tracking，不验证高维 feature learning、漂移或 delayed labels。

### 问题 2：真实 SiC 数据上能否从高维输入得到目标配方？

**实验。** 使用 Infineon WBG Epi 真实数据，原始过程参数超过 500 个；因保密，变量数值被变换为 de-identified ranges。XGBoost 选出 15 个参数，再以厚度偏差 0、掺杂 20 为目标运行优化。[pdf:E15]（PDF 物理页 15，Section VI-A）

**作者答案。** Fig. 5–8 被解释为参数范围收窄、厚度和掺杂预测接近目标、优化后参数分布更集中。[pdf:E15]（PDF 物理页 15，Fig. 5）[pdf:E17]（PDF 物理页 17，Fig. 7–8）

**证据约束。** Fig. 6 的掺杂序列视觉上稳定在约 16，而正文同页声称接近目标 20；Fig. 7 的 MOODFG 预测曲线也大多低于 20。论文没有解释这是 de-identification、归一化反变换还是图文不一致。[pdf:E16]（PDF 物理页 16，Fig. 6 与 Section VI-C）因此可以确认“模型输出更稳定、厚度接近 0”，但不能仅凭这些图确认“掺杂精确达到 20”。论文也没有报告公开数据、时间切分、独立产线测试或实际下发后的 wafer-level yield 改善值。

### 问题 3：多目标 formulation 是否修复 MRBORI 的单目标缺口？

**实验。** 在同一 candidate pool、相同 feature screening、seed 和预算下运行 thickness-only 与 doping-only MRBORI，并用 \(|\mathrm{thickness\ offset}|\le2\)、\(\mathrm{doping}\le40\) 检查单一 recipe 的 deployability。

**答案。** thickness-only MRBORI 对 doping drift 有持续偏差，单目标 recipe 的多规格 deployability 报告为 0%；这支持“分别做单目标不等于得到一组联合可用配方”。[pdf:E18]（PDF 物理页 18，Fig. 10 与 Section VI-G）

### 问题 4：MOODFG 是否优于替代 optimizer？

**实验。** 比较 MOODFG、ParEGO、NSGA-II、Random Search；所有方法 Sobol-10 初始化、20 seeds、总预算 \(T=50\)。ParEGO 和 NSGA-II 使用与 MOODFG 相同的 deep-feature GP surrogate，主要隔离 acquisition/selection 差异。

**答案。** MOODFG 的 median \(T_\varepsilon=4\)，ParEGO 为 4.5，NSGA-II 为 5.5，Random Search 为 20；前三者 final median Best Dist. 都是 0.889。MOODFG、ParEGO、NSGA-II 的 median \(T_{\mathrm{deploy}}=1\)、Deployable@T 都是 100%，Random Search 则为 2 和 85%。[pdf:E19]（PDF 物理页 19，Table VI）

这说明 MOODFG 在“进入 \(\varepsilon=2\) target tube 的速度”上略优于两个强基线，但 final accuracy 是并列，不支持“最终解质量显著更高”。更重要的是，三个多目标方法第一轮就已经 100% deployable，表明论文定义的 deployability tolerance 比 target-distance criterion 宽，不能单独证明 MOODFG 的搜索增益。

### 问题 5：计算成本与 feature selection 是否可控？

**实验与答案。** 论文报告每个 BO step 中，feature update 中位数 0.60 s、两个 exact GP refit 0.32 s、acquisition 0.18 s，端到端 1.10 s，峰值内存约 1.6 GB；一次性 XGBoost 为 4.8 min。阈值消融中，\(\gamma=0.92\) 选 15 个变量，per-step 1.10 s、\(T_\varepsilon=4\)、Best Dist. 0.889、Deployable@T 100%；更激进的 \(\gamma=0.95\) 只选 12 个变量，虽降到 1.00 s，却把 \(T_\varepsilon\) 推到 6、Deployable@T 降到 95%。[pdf:E19]（PDF 物理页 19，Table VII）[pdf:E20]（PDF 物理页 20，Table VIII）

论文还报告跳过 deep feature（\(\phi(x)=x\)）会更晚进入 tolerance tube，前半程距离更大、产生 deployable recipe 更慢；但该 ablation 没给出与 Table VI 同等完整的数字表，因此它支持“representation 有帮助”的定性结论，不能精确量化因果增益。[pdf:E20]（PDF 物理页 20，Section VI-J）

## § 8 — Take-aways

### 5 句话

1. 这篇论文把 SiC 外延 recipe tuning 从“每次优化一个输出”改写为“寻找一组同时满足厚度与掺杂目标的配方”。[pdf:E04]（PDF 物理页 4，Table I）
2. MOODFG 用 XGBoost 筛选、共享 deep feature 和 per-objective exact GP，把高维小样本问题转化为带不确定度的 target tracking。
3. 它的关键产品不是 Pareto front，而是一个 recipe、一个 target-distance certificate 和一个 run-to-run 停止规则。
4. 同一 candidate pool 上，MOODFG 达到 target tube 的中位迭代数略少于 ParEGO/NSGA-II，但三者 final distance 并列，deployability 指标也未区分三者。[pdf:E19]（PDF 物理页 19，Table VI）
5. 最有价值的贡献是问题 formulation 与制造闭环接口；最薄弱的部分是 certificate 假设、真实闭环证据、图文一致性和对 drift 下校准性的验证。

### 3 句话

MOODFG 把高维工艺输入压到 latent space，用 GP 均值和不确定度直接搜索指定的厚度/掺杂 target。它比单目标 MRBORI 更符合“一组配方同时过规格”的制造决策对象，并在离线 candidate-pool benchmark 上有较快 target attainment。现有证据尚不足以证明实际产线长期漂移下的 certificate 覆盖率、闭环 yield 改善和稳定 release。

### 1 句话

这是一套面向 wafer-to-wafer recipe release 的深特征 GP target-tracking 框架，formulation 有工程价值，但“可认证地投产”仍比论文现有实验走得更远。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在 rolling window、工艺漂移和稀疏迟到标签存在时，learned feature 后的每个目标仍由校准良好的 GP 覆盖，因此低 \(D_t^{\mathrm{UCB}}\) 真能上界实测 target error。**

它失败时，损失不是“性能下降一点”，而是整个核心交付物失效：模型可能对错误配方给出很小的 posterior variance，certificate 低于 \(\varepsilon\)，系统提前释放 recipe。理论上的 A1–A3 要求 RKHS 适配、compact feature parameter set、sub-Gaussian noise 和足够 coverage；实际算法却不断重训 feature、忘却旧数据并面对 reactor memory 与 drift。[pdf:E12]（PDF 物理页 12，assumptions 与 Eq. (14)–(15)）

论文提供的支持包括同一 candidate pool 上的 20-seed benchmark、no-feature ablation 和秒级 runtime；这些证明了离线搜索可运行，却没有直接检查 prediction interval coverage、false-release rate 或跨时间段 calibration。[pdf:E19]（PDF 物理页 19，Table VI–VII）此外，Fig. 6 中掺杂轨迹与名义目标 20 的可见差异，使“目标值、绘图尺度与 certificate 使用同一口径”本身也留下未决项。[pdf:E16]（PDF 物理页 16，Fig. 6）

因此，论文最需要的不是更多收敛曲线，而是一张随时间和工况分层的 coverage/release table：certificate 宣称可行时，真实下一片晶圆有多少比例同时过厚度和掺杂规格；发生 drift 后错误释放率如何变化。现有 PDF 未报告这项证据。

## § 10 — 最小复现实验

一周内最值得复现的是“deep feature 是否真的提高 target attainment，同时 certificate 是否校准”，不需要复刻完整 MES/APC/SPC 系统。

**数据。** 由于 Infineon 数据未公开，用可控的 semi-synthetic wafer stream：500 个输入，其中 15 个真实影响两个输出；加入非线性交互、两个目标不同噪声、一个缓慢 drift 和随机 1–3 run 标签延迟。目标和容差沿用论文逻辑，样本预算用 Sobol-10 加 40 次更新，总 \(T=50\)。论文真实实验的 500+→15、\(k=8\)、Sobol-10、\(T=50\) 可作为配置锚点。[pdf:E13]（PDF 物理页 13，implementation details）[pdf:E15]（PDF 物理页 15，真实数据设置）

**实现。** 做三个版本：MOODFG；\(\phi=I\) 的 raw-input GP；与 MOODFG 共用 surrogate 的 ParEGO。每个版本至少 20 seeds。严格按时间顺序更新，不让迟到标签穿越到过去；另记录 frozen-feature interval 内与跨 feature update 后的 posterior。

**测量。**

- \(T_\varepsilon\)、Best Dist.、单一 recipe 的真实 deployability；
- certificate 覆盖率：\(D_t^{\mathrm{UCB}}\le\varepsilon\) 时，真实双目标误差是否也 \(\le\varepsilon\)；
- false-release rate、标签延迟下的额外晶圆数；
- drift 前后分层的 calibration；
- 每步 wall-clock 和峰值内存，以论文 Table VII 的 1.10 s、约 1.6 GB 作为同量级参照，而不是必须复现的硬阈值。[pdf:E19]（PDF 物理页 19，Table VII）

**支持条件。** MOODFG 在多数 seeds 上比 \(\phi=I\) 明显降低 \(T_\varepsilon\)，且 nominal 90% certificate 在 drift 前后都接近覆盖目标，false release 不上升。

**反驳条件。** 只要出现以下任一项，就反驳核心强 claim：deep feature 没有稳定降低样本数；posterior 过度自信导致大量 false release；或 drift/延迟下 certificate 失去覆盖而算法仍停止。这个实验既能复现优化优势，也能直接证伪“uncertainty-aware certificate 可用于 deployment”。

## § 11 — 最强反例设计

最强反例不是再换一个 optimizer，而是构造**latent collision 加隐藏 reactor state**。

设两个外观看起来相同的 APC 配方 \(x_a,x_b\) 在历史窗口内映射到近似相同的 \(z=\phi_\theta(x)\)，但真实掺杂还受未进入输入的 chamber memory \(h_t\) 控制。训练期 \(h_t\) 稳定，GP 学到很小噪声和很低 posterior variance；测试期因清腔、前序 lot 或气路残留发生 regime switch。厚度仍接近 0，掺杂却从目标附近跳到超规格区。由于标签晚两片到达，系统在错误映射下连续下发 recipe。

这个反例直接攻击三件核心机制。第一，shared feature 可能丢掉对掺杂关键但对厚度不明显的方向；第二，最小化“距离 + 正不确定度”会回避新工况中的高不确定点，而不是主动探索；第三，stop rule 在 delayed labels 下可能用失配 posterior 做多次决策。[pdf:E07]（PDF 物理页 7，asynchronous labels 与 drift handling）[pdf:E10]（PDF 物理页 10，Eq. (5)–(6)）

实验上，把隐藏状态在第 25 个 run 突变，比较 nominal certificate、真实双目标误差和 false-release count。如果 \(D_t^{\mathrm{UCB}}\le\varepsilon\) 却连续出现实测超规格，Eq. (14) 的制造解释就被推翻；理论不会被逻辑反驳，因为 A1–A3 已失效，但这恰好证明这些假设不是可忽略的数学细节，而是 deployment 的前置条件。[pdf:E12]（PDF 物理页 12，Eq. (14) 与 assumptions）

## § 12 — Follow-up Research Idea

在 automation science and semiconductor manufacturing 领域，高影响工作通常不只看离线预测误差，还看实际闭环可执行性、跨时间和跨 tool 的稳定性、错误释放风险、可复现 benchmark，以及与既有 MES/APC/SPC 的集成成本。本文已经把未来工作指向 sequential objectives：后一个目标 \(Y_2\) 反过来改变前一个目标 \(Y_1\)，需要 conditional surrogate 与动态 target。[pdf:E21]（PDF 物理页 21，Section VIII）

基于第 9 节，我提出一个**候选研究方向**：把问题从“最小化 posterior target distance”改写成“在 drift 和 delayed labels 下，控制错误 recipe release 的长期风险”。核心不是再给 MOODFG 加一个网络模块，而是用 sequential conformal prediction、change-point detection 与 safe abstention 形成一个 distribution-aware release contract：只有当近期残差校准仍有效、双目标联合 prediction set 完全落入 specification set 时才释放；否则回退到已验证 safe recipe 并主动请求一次有信息量的实验。

具体地说：

- **未满足需求。** 现有 GP certificate 的可信度依赖核、feature 与噪声假设；产线真正关心的是“错误放行率是否受控”。
- **潜在研究价值。** 它把单次 target attainment 提升为可审计的 run-to-run safety guarantee，能直接对应质量、报废和设备风险。
- **可借鉴工具。** 从 online conformal prediction 借用有限样本 coverage，从 statistical process control 借用 drift alarm，从 safe Bayesian optimization 借用 verified safe set 与 abstention。
- **首个证伪实验。** 在多 tool、多时间段 replay 中注入 abrupt drift、慢漂移、heavy-tail metrology noise 和 1–3 run 标签延迟；若方法不能控制 false-release rate，或为保持覆盖而长期拒绝下发导致不可接受的 throughput loss，方向即被证伪。
- **与本文实质区别。** 本文优化的是 GP posterior 下的 target-distance upper bound；新方向优化的是真实 release error 的在线可校准风险，并允许“证据不足时不下发”成为一等决策。

论文 Table VIII 表明 feature 数和速度之间已有明确 trade-off，但这仍是 accuracy/cost 取舍，不是 release-risk 保证。[pdf:E20]（PDF 物理页 20，Table VIII）相关工作尚未做系统检索，因此上述方向只标为候选想法，不声称 novelty。
