# Real-Time Surrogate Modeling for Fast Transient Prediction in Inverter-Based Microgrids Using CNN and LightGBM

- **作者**：Osasumwen Cedric Ogiesoba-Eguakun、Kaveh Ashenayi、Suman Rath
- **出处**：arXiv:2603.29255v1（eess.SY）
- **年份**：2026
- **DOI**：10.48550/arXiv.2603.29255
- **Zotero key**：IZFCMVP8

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的速度瓶颈：inverter-based microgrid 的开关、控制环和故障暂态发生得很快，EMT（electromagnetic transient，电磁暂态）模型能保留这些动态，却常常无法在现场监视和决策所需的时间内算完。作者因此不是要替换离线 EMT 真值，而是训练一个数据驱动 surrogate，让它从最近一段多通道测量中迅速给出电压幅值、频率、总有功功率和电压跌落的估计。论文把应用价值落在稳定性监视、故障分析和运行决策上，并报告 LightGBM 对 1 s 仿真段的推理快于实时、CNN 则仍慢于实时。[pdf:E01]

这里的工程意义有两层。第一，10 个 inverter-based DG（distributed generator，分布式电源）组成的系统具有控制耦合；如果每次告警判断都重新跑全细节 EMT，计算延迟会压过告警窗口。第二，不同输出并不具有相同的统计结构：频率可能平滑，电压跌落却由离散事件驱动，因此“一个模型包打天下”未必成立。论文将这一点作为比较 CNN、LightGBM 和二者组合的理由，而不是只报告一个总体误差。[pdf:E02]

必须先限定“实时”的含义。本文的证据是**离线生成数据之后，在通用 CPU/GPU 上对既定测试集做软件推理的 wall-clock benchmark**；它没有展示在线数据采集、闭环控制、硬件在环、确定性 deadline，也没有 FPGA 实现。因此，本卡把它视为“软件推理速度证据”，不把它外推成实时控制系统或 FPGA 可部署性证据。

## § 2 — 前人工作与不足

论文把已有路线分成三类。降阶或线性 surrogate 速度快，但难以覆盖电力电子控制带来的非线性与快暂态；LightGBM、random forest 等树模型擅长结构化特征，却依赖 feature engineering，未必能直接利用时间序列；CNN、RNN/LSTM 等深度模型能学习时间模式，但数据、调参和算力成本更高。作者还指出，既有稳定性研究多为分类、小信号评估或稳态 OPF surrogate，较少同时具备 EMT 高频数据、多类扰动、OOD（out-of-distribution，分布外）测试和 runtime benchmark。[pdf:E02]

更具体地说，论文自己的 Table I 将相关 CNN 工作描述为 transient-stability classification 或 vulnerability assessment，将相关 LightGBM 工作描述为 small-signal prediction/correction；作者之前的工作 [13] 则提供 10-DG EMT digital-twin dataset，但不训练 surrogate predictor。Table I 据此把本文定位为 EMT 数据上的多目标回归和运行时间比较。[pdf:E03] 这是**论文原文对相关工作的归纳**，本卡没有独立重查每篇引文，因而不能据此宣称本文具有 novelty。

论文确实补上了“同一数据框架下比较时间序列模型与特征模型”的实验，但它没有充分补上另一个更基础的缺口：预测时刻与输入时刻是否严格因果分离。后文公式把 \(X_t\) 写成包含 \(x_t\) 的窗口，又用它估计 \(y_t\)。这使结果可能主要证明同一时刻的重建或 feature transformation，而不是提前预测未来暂态。[pdf:E04]

## § 3 — 重建作者的思考路径

在不预设本文方案的前提下，一个研究者可能沿下面的路径走到这个设计。

首先，10-DG microgrid 的详细模型包含 DC link、PWM voltage-source inverter、LCL filter、coupling transformer，以及本地 voltage/frequency/power controller；系统用 MATLAB/Simulink EMT 仿真，并以微秒级时间分辨率捕捉开关和控制交互。[pdf:E02] [pdf:E03] 这说明“直接删掉快动态”会损伤要监视的对象。

其次，如果 EMT 仍作为离线数据生成器，就可以把昂贵求解转成 supervised regression：让高保真仿真负责覆盖工况，让轻量模型负责重复查询。数据中有 11 类工况与扰动，包括 normal operation、load step、voltage sag、ramp、frequency ramp、generator trip、tie-line disconnection、reactive-power disturbance、single-line-to-ground fault、measurement noise 和 communication delay；每个样本包含 38 个同步测量特征。[pdf:E03]

再次，不同目标的结构提示不同归纳偏置：CNN 直接读取窗口波形，适合局部时间模式；LightGBM 读取窗口的 mean、standard deviation、minimum、maximum 和 last value，适合结构化、低维统计关系。于是自然会得到“并行训练两类模型，再按目标比较，必要时组合”的实验框架。[pdf:E05]

最后，研究者会用 noise 和 communication delay 场景作为 OOD test，再把 surrogate 的 wall-clock time 与同一 1 s EMT 段比较，以回答“误差是否可接受”和“软件推理是否足够快”两个问题。[pdf:E06] [pdf:E07] 这条思路合理，但要成为真正的 transient prediction，还必须额外证明输入与目标之间存在正预测 horizon，而不是同刻量的重建。

## § 4 — 核心 Intuition

核心 intuition 是：保留 EMT 作为离线教师，把最近一段高维测量压成两种互补表示——CNN 看原始时间窗口，LightGBM 看统计特征——再用便宜得多的回归近似目标量。[pdf:E05] 平滑、低方差或显式派生的目标更容易被树模型捕捉，具有局部时间形状的信号更可能受益于 CNN；因此模型选择应跟着目标的物理与统计结构走，而不是固定使用一种网络。[pdf:E08] [pdf:E09]

## § 5 — 具体方法与完整 Pipeline

以“在一次扰动后估计 \(V_{\mathrm{mag}}\)、\(f_{\mathrm{DG1}}\)、\(P_{\mathrm{total}}\) 和 \(V_{\mathrm{dip}}\)”为例，完整 pipeline 如下。

1. **EMT 数据源**：作者在 MATLAB/Simulink 中建立 grid-connected、10-DG 的 inverter-based microgrid。代表性 DG 由 energy source、DC-link capacitor、PWM VSI、LCL filter、coupling transformer 和本地 V/f/P/Q 控制构成；相同结构用于全部 DG。[pdf:E04]
2. **工况与采样**：数字孪生运行 11 类正常、物理扰动和 cyber-physical 扰动场景，采集 38 个同步通道/特征。论文给出的代表性参数包括 \(f_{sw}=10\text{ kHz}\)、单 DG 额定容量 \(10\text{ kVA}\)、DC-link \(1000\text{ V}\)、额定频率 \(60\text{ Hz}\)，仿真使用微秒级时间分辨率。[pdf:E03]
3. **派生量**：由三相电压形成 \(V_{\mathrm{mag}}\)，由 10 个 DG 的输出求和形成 \(P_{\mathrm{total}}\) 与 \(Q_{\mathrm{total}}\)。作者明确没有显式加入 phase angle，理由是其信息被其他变量隐含反映；这是作者的建模判断，不是本文证明的物理等价。[pdf:E03]
4. **窗口化**：对多变量序列构造长度为 \(W\)、步长为 \(S\) 的 \(X_t\in\mathbb{R}^{W\times d}\)。CNN 直接读取 raw sequence；LightGBM 则读取每个窗口的 mean、standard deviation、minimum、maximum 和 last value。[pdf:E04] [pdf:E07]
5. **目标与训练**：目标集合为 \(V_{\mathrm{mag}}, f_{\mathrm{DG1}}, P_{\mathrm{total}}, V_{\mathrm{dip}}\)。尽管正文称其为 multi-output regression，实际训练策略是“每个输出单独训练一个模型”；LightGBM 采用 gbdt、learning rate 0.05、300 estimators、max depth 6、31 leaves，CNN 由三层 Conv1D、pooling、global-average pooling 和 dense layer 构成。[pdf:E06]
6. **数据划分和 OOD**：training set 学习正常及扰动数据，validation set 用于调参与监控，noise 和 communication-delay cases 放入 test set 检验 robustness；模型使用 early stopping 与 hyperparameter tuning。[pdf:E06] 论文没有报告各集合样本数、按哪些 scenario/file 切分、noise 幅值、delay 长度或随机种子以外的重复实验设置，因此无法判断 OOD 与训练分布的距离。
7. **预测与组合**：CNN 和 LightGBM 分别产生四类目标的估计，论文还报告 “Hybrid CNN+LightGBM”。但是，正文、Algorithm 1 和图 3 均未给出 hybrid 的融合公式、权重、训练方式或逐目标选择规则；正式复现时不能从 PDF 唯一重建这一环节。[pdf:E05] [pdf:E07]
8. **评价**：准确性用 RMSE、MAE 和 \(R^2\)，鲁棒性看 noise/delay OOD，速度用 surrogate inference wall-clock 与 EMT runtime 之比。实际执行平台是 Python 软件栈、Intel Xeon 8-core 2.0 GHz、50 GB RAM 和 NVIDIA Tesla T4 16 GB；deep-learning framework 的名称与版本未报告。[pdf:E06]

论文也没有报告 EMT 求解器模式、固定/变步长设置、window 的实际 \(W,S\)、输入采样间隔、数值精度、batch size、预处理是否计时、模型序列化/加载时间、事件同步机制或 FPGA mapping。这些项目均应保持“未报告”，不能靠常见实现补齐。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有形式化定义，但没有证明误差界、稳定性或闭环性质；数学主要用于定义 feature 和 supervised regression。

总有功、无功由各 DG 求和：

\[
P_{\mathrm{total}}=\sum_{k=1}^{N_{\mathrm{DG}}}P_{\mathrm{DG}k},\qquad
Q_{\mathrm{total}}=\sum_{k=1}^{N_{\mathrm{DG}}}Q_{\mathrm{DG}k}.
\]

工程上，这把各局部出力压成系统级 power-balance 指标；本文系统为 10 DG，所以 Algorithm 1 实际把求和上限写成 10。[pdf:E03] [pdf:E07]

时间窗口定义为

\[
X_t=\{x_{t-W+1},x_{t-W+2},\ldots,x_t\}\in\mathbb{R}^{W\times d},
\qquad y_t=f_\theta(X_t).
\]

训练目标是

\[
\mathcal{L}(\theta)=\frac{1}{N}\sum_{t=1}^{N}\|y_t-\hat y_t\|_2^2.
\]

直观上，模型用最近 \(W\) 个多通道样本解释一个 \(m\) 维目标。[pdf:E04] 但公式的目标是 \(y_t\)，输入又包含 \(x_t\)；论文没有定义 \(y_{t+\Delta}\) 或 \(\Delta>0\)。因此“future state”只出现在文字叙述中，形式化对象仍更接近同刻估计。

电压幅值按

\[
V_{\mathrm{mag}}=\sqrt{V_a^2+V_b^2+V_c^2}
\]

从三相电压计算。[pdf:E05] 这意味着如果当前 \(V_a,V_b,V_c\) 出现在窗口末端，预测当前 \(V_{\mathrm{mag}}\) 可以由确定性公式直接完成；必须用 analytic baseline 才能判断 CNN 是否真的学到 transient dynamics。

LightGBM 被写成加性树模型

\[
F_M(x)=\sum_{m=1}^{M}\gamma_mh_m(x),
\]

并通过 prediction loss 加树复杂度正则项；CNN 的一维卷积写成

\[
z_i^{(l)}=\sigma\left(\sum_{k=0}^{K-1}w_k^{(l)}x_{i+k}^{(l-1)}+b^{(l)}\right),
\qquad
\hat y=W_fz+b_f.
\]

前者表示逐棵树修正残差，后者表示卷积提取局部时间 pattern 后由 dense layer 回归输出。[pdf:E05] [pdf:E06] 这些是标准模型定义，不构成对 EMT 物理守恒、数值稳定或跨拓扑泛化的保证。

## § 7 — 实验设计与结论

- **问题：不同目标是否需要不同模型？ → 实验：** 在相同训练、验证和 OOD test 上比较 LightGBM、CNN 和 hybrid 对四个目标的 \(R^2\)。**答案：** Fig. 7 报告 LightGBM/CNN/hybrid 的 \(V_{\mathrm{mag}}\) 分别为 0.671/0.837/0.820，\(f_{\mathrm{DG1}}\) 为 0.999/0.997/0.999，\(P_{\mathrm{total}}\) 为 0.993/0.995/0.993，\(V_{\mathrm{dip}}\) 为 0.753/0.267/0.753。结果支持“目标依赖的模型选择”，但 hybrid 的融合方法未闭合。[pdf:E10]
- **问题：noise 和 communication delay 下是否仍能工作？ → 实验：** 将这两类 scenario 作为 OOD test，检查学习曲线、预测轨迹和 residual distribution。**答案：** 作者称两模型在 OOD 下保持较稳定；Fig. 5/6 显示 \(f_{\mathrm{DG1}}\) 与 \(P_{\mathrm{total}}\) 的拟合和 residual 更紧，\(V_{\mathrm{dip}}\) 的 spread 明显更大。[pdf:E08] [pdf:E09] 由于 PDF 未给 OOD 的 noise/delay 强度、样本量、置信区间和逐场景指标，这只能支持特定未充分刻画测试集上的表现，不能支持广义抗扰鲁棒性。
- **问题：surrogate 是否比 EMT 快并达到实时？ → 实验：** 对 1.00 s simulated time 比较 wall-clock。**答案：** Table IV 报告 Simulink 941.16 s；LightGBM 0.89 s、speedup 1053.58、RT ratio 1.12；CNN 5.09 s、speedup 185.04、RT ratio 0.20；hybrid 1.80 s、speedup 522.65、RT ratio 0.56。[pdf:E07] 因此只有 LightGBM 在该软件平台和这一定义下满足 RT ratio \(>1\)；hybrid 是“接近实时”，CNN 明确未达到实时。Fig. 7 将这些时间近似画成 1000/0.9/5/1.8 s，属于可视化取整。[pdf:E10]
- **问题：这些结果是否证明 fast transient prediction？ → 实验缺口：** 没有正预测 horizon、严格 causal ablation、persistence/analytic baseline、跨拓扑测试、闭环控制或 HIL。**答案：** 现有实验尚不能排除同刻 target leakage 和派生量重建这一替代解释，也不能证明在未见的 DG 数量、线路参数、controller 或 switching regime 上成立。

## § 8 — Take-aways

**5 句话：**（1）论文用 10-DG EMT digital twin 的 11 类场景训练 CNN 与 LightGBM surrogate，以估计电压幅值、频率、总有功和电压跌落。[pdf:E01]（2）CNN 读取原始窗口，LightGBM 读取窗口统计量，两者的相对优势随目标结构变化。[pdf:E05]（3）在报告的 OOD test 中，频率和总有功容易拟合，电压跌落最难，CNN 对后者的 \(R^2\) 只有 0.267。[pdf:E09] [pdf:E10]（4）只有 LightGBM 在所报 Xeon/Tesla 软件环境中对 1 s 段实现 0.89 s 推理；CNN 与 hybrid 都没有达到 RT ratio 1。[pdf:E06] [pdf:E07]（5）最大的不确定性不是模型分数，而是 \(X_t\to y_t\) 的同刻定义和输入/目标重叠，使“预测未来暂态”的解释尚未被证实。

**3 句话：** 这项工作证明了在一个 10-DG EMT 数据集上，CNN 与 LightGBM 可以用远少于 Simulink 的 wall-clock 重建若干关键量。它也显示不同目标需要不同 representation，但没有完整定义 hybrid。最关键的是，现有实验更像同刻 surrogate estimation，尚不能证明因果、多步、跨系统的 transient forecasting。

**1 句话：** 这是一个有价值的软件 surrogate benchmark，但不是已经闭合的实时预测器，更不是 FPGA 或闭环控制实现。

## § 9 — 最脆弱的假设

最脆弱的假设是：**窗口输入与目标之间没有会把“预测动态”退化成“读取或重算当前量”的信息泄漏。**

这个假设很可能不成立。论文形式化写的是 \(X_t=\{x_{t-W+1},\ldots,x_t\}\) 和 \(y_t=f_\theta(X_t)\)，没有正 horizon；Algorithm 1 又把 \(f_{\mathrm{DG}k}\) 放在同步输入里，同时把 \(f_{\mathrm{DG1}}\) 放在 target set 中，并用同刻三相电压/各 DG 功率形成 \(V_{\mathrm{mag}}\) 与 \(P_{\mathrm{total}}\)。[pdf:E04] [pdf:E07] 于是 \(f_{\mathrm{DG1}}\) 可能直接存在于输入，另外两个目标可由显式公式得到。若这一点成立，极高 \(R^2\) 主要说明模型能复现当前测量或 deterministic feature，而不是能在扰动发生前/后提前一个控制周期预测未观测状态。

论文给出的支持证据是 noise/delay OOD 下仍有较高分数和紧 residual；但它没有做 remove-current-target-channel、strictly-causal window、positive-horizon forecast 或 analytic-baseline 对比。[pdf:E08] [pdf:E09] 因此，这个关键假设缺少直接证据。其失败代价最大，因为它会同时削弱“fast transient prediction”“robustness”和“real-time decision support”三项解释，即使 runtime 数字本身仍然成立。

## § 10 — 最小复现实验

一周内最值得做的不是重建完整 10-DG EMT，而是对作者同一数据做一个 **leakage-controlled horizon test**。

1. 取得论文使用的 11-scenario dataset，保留按 scenario file 的分组；选 \(f_{\mathrm{DG1}}\)、\(V_{\mathrm{mag}}\) 和 \(P_{\mathrm{total}}\) 三个目标。
2. 做三种任务：A 为论文式 \(X_t\to y_t\)；B 从输入删除目标通道及其显式代数代理，但仍做 \(y_t\)；C 使用只到 \(t\) 的输入预测 \(y_{t+\Delta}\)，至少取一个控制/监测相关的正 horizon，并保证 train/test 按 scenario file 隔离。
3. 实现四个 baseline：last-value persistence、线性/AR、\(V_{\mathrm{mag}}\) 与 \(P_{\mathrm{total}}\) 的 analytic calculator，以及论文的 LightGBM；CNN 只需复现一个目标即可。
4. 测量逐 scenario 的 RMSE/MAE/\(R^2\)、最坏工况误差、event onset 前后误差和单样本 p50/p99 latency；预处理和数据搬运必须计时。
5. 若 B/C 仍显著优于 persistence/AR，且误差不会在 fault、trip、delay onset 附近崩溃，就支持 surrogate 学到了可预测动态；若 A 很高而 B/C 接近 baseline 或失效，就反驳论文对 “prediction” 的强解释。

这个实验不需要先完成 FPGA 映射，却能先判断是否值得投入硬件化。

## § 11 — 最强反例设计

最强反例是构造一个**相同当前观测、不同紧接未来**的成对场景。具体做法是让两条 EMT 轨迹在 \(t\) 前具有几乎相同的 \(V/I/P/Q/f\) 窗口，但在 \(t+\Delta\) 分别发生不同的 controller saturation、fault clearing、tie-line action 或 delayed command；这些未来事件不包含在输入中。模型若只是同刻重建，会在 \(t\) 得到漂亮分数，却不可能区分两条未来。

测试时再同时改变一个训练未见的结构变量，例如 DG 数量、线路阻抗或 controller gains，并与 persistence、解析派生量、简单状态估计器比较。若 CNN/LightGBM 在原始随机切分上保持高 \(R^2\)，但在成对未来与结构外推上误差陡增，就得到一个具体替代解释：模型学到的是当前 measurement manifold 与场景指纹，而不是可组合的 EMT dynamics。论文自己承认模型仅在一个 microgrid 上训练、可能需要更多数据才能迁移，而且当前方法是 single-step，未反映长期行为。[pdf:E08] [pdf:E09] 这使该反例既对准核心 claim，也符合作者已暴露的边界。

## § 12 — Follow-up Research Idea

**候选方向，不声称 novelty：面向大规模 VSC 场站的因果、端口可组合、定点可综合 surrogate。**

（a）**未满足需求。** 当前模型把一个固定 10-DG 系统整体视为数据映射，输入/目标存在同刻重叠，hybrid 未定义，且软件 latency 不能直接转成 FPGA deadline。大规模 VSC 场站更需要在拓扑和单元数量变化时仍可组合、在正预测 horizon 上可验证、并能给出确定的 worst-case latency。

（b）**可能的研究价值。** 把目标从“在固定数据集上提高平均 \(R^2\)”改成“学习每个 VSC/feeder 的因果端口状态更新，并在网络耦合后保持误差、守恒残差和 deadline 约束”。这同时回应数据驱动建模的可解释边界、EMT surrogate 的跨规模复用，以及工程领域看重的 HIL/闭环实证。依据本文，现有方案只在单一 microgrid、single-step 和通用 Xeon/Tesla 平台上验证。[pdf:E06] [pdf:E08]

（c）**可借鉴工具。** 可以借鉴 graph/message-passing 表示网络连接，借鉴 model predictive control 的 strict causal horizon，借鉴 physics-informed residual 约束端口功率/电流关系，并用 quantization-aware training、fixed-point range analysis 与 HLS/RTL pipeline 把推理核映射到 FPGA。这些是**基于工程需求的候选组合**，不是本文已经验证的方法。

（d）**第一个证伪实验。** 在 10-DG 训练后，冻结模型，直接测试未见的 DG 数量、线路参数和控制器参数；同时要求预测 \(t+\Delta\)，输入删除当前目标及解析代理。在同一数据与 bit-accurate FPGA emulation 上比较 float model、8/12/16-bit fixed-point model、persistence 和简化物理 baseline。若跨规模最坏误差、KCL/功率残差或 p99 deadline 任一超限，候选方向即被证伪；不能用平均 \(R^2\) 掩盖。

（e）**与本文的实质区别。** 本文是固定系统上的全局、同刻/单步软件 surrogate，Figure 7 比较的是模型分数和通用平台 wall-clock。[pdf:E10] 候选方向把研究对象改成可组合端口更新，把验证对象改成正 horizon、拓扑外推、物理残差、fixed-point 误差和确定性硬件时序。只有完成相关工作检索、公开跨系统 benchmark、真实 FPGA/HIL 闭环验证后，才有资格讨论 novelty 或 FPGA 可部署性；当前证据不足以作此声明。
