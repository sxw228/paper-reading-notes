# Real-Time Multi-Stability Risk Assessment and Visualization of Power Systems: A Graph Neural Network-Based Method

- 作者：Qifan Chen, Siqi Bu, Huaiyuan Wang, Chao Lei
- 出处：IEEE Transactions on Power Systems, Vol. 40, No. 4
- 年份：2025
- DOI：10.1109/TPWRS.2024.3524406
- Zotero key：3Z3KVXUH

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“某一种稳定性会不会失稳”，而是：在风电出力、故障位置和机组跳闸等不确定性共同存在时，能否在运行时刻同时估计小信号、频率、短期电压、长期电压和暂态稳定风险，并把稳定/不稳定运行域（stable/unstable operation regions, SURs）直观地画出来。作者把小扰动转子角与 converter-driven stability 合并为小信号稳定，用五个稳定裕度等级再取最小值得到 overall stability；因此“multi-stability”在本文中是同一工况、同一组不确定性和同一套样本上的联合风险视图，不是五个彼此独立的单项报告。[pdf:E03]

这个问题重要有两层原因。第一，真实停电事件可能同时出现多种失稳：论文举例称 2016 年南澳停电同时观察到频率失稳和短期电压失稳，2006 年巴基斯坦停电同时记录到小扰动转子角失稳和短期电压失稳；只做 singular stability risk assessment 会漏掉风险之间的关系。[pdf:E02] 第二，传统 Monte Carlo simulation（MCS）结合 time-domain simulation（TDS）或特征值分析虽然能生成概率结果，但计算代价太高，更适合规划而不是实时运行；随着可再生能源和拓扑不确定性增强，运行人员需要在秒级反复更新风险，而不是等待数小时。[pdf:E02]

本文的直接价值是把大量候选场景的“昂贵物理仿真”前移到离线阶段，在线用 GNN 近似五类稳定标签，再统计各标签频率并生成 SURs。论文在三个不同规模系统上展示了秒级结果，但这个价值应理解为“离线监督学习后的快速风险筛查与可视化”，不是实时 EMT 仿真，也不是 FPGA 实现。[pdf:E01][pdf:E12]

## § 2 — 前人工作与不足

论文把既有路线分成三类。第一类是 conventional MSRA：文献 [15] 用 MCS 计算一天内小扰动转子角、暂态转子角和频率的复合稳定指标，文献 [16] 用 MCS 建立小扰动/暂态转子角、长期电压和频率的多稳定运行边界。它们的优点是多个稳定问题共享场景和假设，缺点是仍依赖 TDS 或特征值分析，难以承担实时运行中的大样本计算。[pdf:E02]

第二类是提高 probabilistic stability assessment 效率的解析法和改进采样法。点估计、cumulant 和 probabilistic collocation 的结果依赖准确的不确定性分布与灵敏度项；Quasi-MCS、Latin hypercube sampling 等更容易处理复杂不确定性，但仍没有消除大量确定性评估的计算成本。作者认为这使它们更适合提前准备充分的规划任务，而不适合分布和拓扑快速变化的运行任务。[pdf:E02]

第三类是面向 singular stability 的 deep learning。论文点名 stacked denoising auto-encoder 和 debiased neural network，它们可从无需潮流计算即可赋值的稳态变量预测暂态稳定概率。然而，这类非图特征很难同时表达拓扑和扰动；同一组功率/电压特征在不同网络连接或故障下可能对应不同稳定结果。本文真正补的不是“再换一个更深的分类器”，而是把 operating condition 与 disturbance 分别编码成两个带权图，让模型显式接收节点、边、拓扑变化和故障信息。[pdf:E02][pdf:E05]

需要谨慎看待作者“首次实现实时 MSRA”的贡献表述：这是论文自己的 claim，本文证据只验证了三个仿真测试系统上的离线训练、在线推理和可视化，没有给出控制中心部署、真实 PMU 数据闭环或现场运行试验。[pdf:E03][pdf:E08]

## § 3 — 重建作者的思考路径

以下是基于论文背景与失败模式的重建，不是作者逐字陈述。

研究者首先会发现，分别优化一种稳定性可能把系统推向另一种失稳，因此必须在同一不确定场景中同时标注多种稳定结果。接着会发现，直接把 MCS 的每个样本送进 TDS 和特征值分析虽然可信，却不能在每个运行时刻重复数千到数万个样本。自然的下一步是用 supervised learning 学习“场景 → 五类稳定标签”的替代映射。

但普通 ANN、CNN 或 RNN 所用的一维稳态向量丢失了两类决定性结构：电网连接关系，以及故障/跳机究竟发生在哪里。于是应把母线当作节点、线路当作边，把当前 operating condition 和 disturbance 各建一张图。两张图分别经过图卷积后再融合，既保留稳态信息，又让相同功率状态在不同拓扑或故障位置下得到不同表示。[pdf:E05][pdf:E06]

最后，即使模型能快速给每个样本分类，概率表仍不够支持调度。把采样点投到风电出力等不确定性坐标中，再用可表示非凸边界的 alpha shapes 包住稳定点和不稳定点，就能把“风险有多大”转换成“当前点离哪块不稳定域多远、应朝哪个方向移动”。多个故障的 naive SURs 再合并为 integrated SURs，便形成从风险估计到可操作空间提示的完整链路。[pdf:E07]

## § 4 — 核心 Intuition

核心直觉是：运行状态和扰动都天然是图，稳定性依赖的不只是节点数值，还依赖这些数值通过什么线路、以什么故障方式相互作用。离线用高成本物理分析给大量双图样本贴上五类稳定标签，在线就可以让 GNN 在无需逐样本潮流、TDS 和特征值计算的情况下快速近似这些标签；再把分类结果投回不确定性空间，形成可视的稳定/不稳定区域。[pdf:E05][pdf:E07][pdf:E08]

## § 5 — 具体方法与完整 Pipeline

以“当前 IEEE 39-bus 系统，三个风场出力有不确定性，并可能在线路 8–9 发生三相接地故障”为例，完整 pipeline 如下。

1. **定义统一标签。** 每个候选场景分别计算小信号、频率、短期电压、长期电压和暂态稳定裕度等级；等级 2 表示稳定，等级 1 表示不稳定。overall stability 取五项等级的最小值，所以只要任一项失稳，overall 就是不稳定。[pdf:E03][pdf:E04]
2. **建立 operating graph。** 母线是节点，线路/变压器是双向边。每个母线保留有功、无功、电压幅值和相角四个槽位；PV、PQ 和 slack bus 只给可直接指定的相应量，其余置零。带权邻接矩阵用线路或变压器的 admittance 表示连接，线路或母线退出则把相应邻接项置零。[pdf:E05]
3. **建立 disturbance graph。** 它复制 operating graph 的背景结构，再把故障、发电机跳闸或功率增减编码进去。三相接地故障后切线用 \(\alpha_F=0\) 令相应故障边权为零；单相接地和两相接地可用不同的 \(\alpha_F\)；机组跳闸则清零相应节点及其连接；功率扰动直接改变对应节点值。[pdf:E05]
4. **双通道 GNN 提取特征。** operating graph 与 disturbance graph 分别经过一个 fully-connected layer（FCL）和多层带 GraphNorm 的 graph convolutional layers（GCLs）。GCL 使用 initial residual identity mapping，目的是在堆叠图卷积时保留初始特征并减轻 over-smoothing。两个通道输出 flatten 后拼接，再经过 FCL。[pdf:E06]
5. **同时输出五类标签。** 最后一层接五个独立 SoftMax classifier，分别预测 \(R_{\mathrm{SSS}},R_{\mathrm{FS}},R_{\mathrm{SVS}},R_{\mathrm{LVS}},R_{\mathrm{TS}}\)，然后按最小规则得到 \(R_{\mathrm{OS}}\)。训练使用五个分类任务的平均 cross-entropy loss 和 Adam。[pdf:E06]
6. **离线训练。** 从运行计划、历史记录和不确定性范围生成大量场景；每个场景用 eigenvalue analysis 或 TDS 得到五个 ground-truth 标签，形成双图输入与标签数据集。这里的物理分析成本没有消失，只是从在线阶段移到了离线阶段。[pdf:E07]
7. **在线风险计算。** 当前时刻从 PMU 得到部分运行量，从超短期非参数概率预测和历史统计得到风电与故障分布。采样后把各候选场景的双图直接赋值给 GNN，不逐样本做 power flow；某一裕度等级的概率就是该等级样本数除以总样本数，即 Eq. (22)。[pdf:E08]
8. **SURs 可视化。** 对同一故障选出样本，把指定不确定性变量作为坐标，分别对稳定点和不稳定点构造 non-convex alpha shapes，得到 naive SURs；再按 Algorithm 2 合并多个故障的区域，删除落在不稳定域中的稳定点并重构 stable region，得到 integrated SURs。[pdf:E07]
9. **离线更新。** 若在线样本或其相似样本不在训练集覆盖内，例如拓扑显著变化或出现新 contingency，作者要求生成新物理标签并离线更新 GNN；具体更新策略不是本文研究重点。[pdf:E08]

这套 pipeline 没有开关级器件模型、固定 EMT 步长、多速率时间推进、定点数值格式、FPGA 映射、资源占用或硬件时序报告。它处理的是系统级稳定风险分类与区域可视化，不能外推为 EMT/FPGA 实现。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线不是提出新的稳定性定理，而是把已有稳定指标离散成监督标签，再定义图表示、图卷积和风险统计。

首先是五类标签。小信号稳定用阻尼比

\[
\zeta=\frac{-\alpha}{\sqrt{\alpha^2+\omega^2}}\times100\%
\]

其中 \(\alpha,\omega\) 是相关共轭特征值的实部和虚部；\(\zeta>0\) 为稳定。频率稳定用

\[
f_{\mathrm{MFD}}=\max(f_{\max}-f_s,\;f_s-f_{\min}),
\]

论文采用 \(0.5\ \mathrm{Hz}\) 阈值。短期电压稳定用

\[
V_R=\max(|V_{\max}-1|,\;|V_{\min}-1|),
\]

论文采用 \(0.2\ \mathrm{p.u.}\) 阈值，即恢复到 \(0.80\)–\(1.20\ \mathrm{p.u.}\) 范围。长期电压稳定对 reduced Jacobian \(J\) 做特征值分析，以最小特征值 \(\lambda_{J,\min}>0\) 为稳定。暂态稳定用

\[
\gamma=\frac{360-\delta_{\max}}{360+\delta_{\max}}\times100,
\]

其中 \(\delta_{\max}\) 是 TDS 中任意两台发电机的最大转子角差，\(\delta_{\max}\ge360^\circ\) 即 \(\gamma\le0\) 判为不稳定。overall 等级为

\[
R_{\mathrm{OS}}=\min(R_{\mathrm{SSS}},R_{\mathrm{FS}},R_{\mathrm{SVS}},R_{\mathrm{LVS}},R_{\mathrm{TS}}).
\]

这些定义与阈值位于 PDF 物理页 3–4 的 Table I 和 Eq. (1)–(6)。作者明确说这些指标和标准用于展示方法，实际 operator 可以按电网情况更换指标、阈值和等级数。[pdf:E03][pdf:E04]

其次是图输入。operating graph 的节点矩阵 \(V_{\mathrm{OP}}\in\mathbb{R}^{N_B\times4}\)，边列表 \(E_{\mathrm{OP}}\in\mathbb{R}^{2\times2N_L}\)，带权邻接矩阵 \(A_{\mathrm{OP}}\in\mathbb{R}^{N_B\times N_B}\)；连接的 \(i,j\) 节点权重取 \(|z_{i,j}|\)，否则为零。disturbance graph 通过 Eq. (12)–(14) 修改边权、节点和功率变化。这里 PDF 把 \(z_{i,j}\) 称为线路或变压器的 admittance；符号命名与工程中常用 \(z\) 表示 impedance 的习惯不一致，复现时应以作者定义而不是字母习惯为准。[pdf:E05]

GCL 的核心更新是 Eq. (16)：

\[
H^{(k)}=\mathrm{ReLU}\!\left[
f_{\mathrm{GN}}\!\left(
\big((1-\alpha^{(k)})\hat P H^{(k-1)}+\alpha^{(k)}H^{(0)}\big)
\cdot\big((1-\beta^{(k)})I+\beta^{(k)}W^{(k)}\big)
\right)\right],
\]

其中 \(\hat P=\hat D^{-1/2}\hat A\hat D^{-1/2}\)，\(\hat A=A+I\)。\(\alpha^{(k)}\) 控制初始特征残留，\(\beta^{(k)}\) 控制 identity mapping 与可学习变换之间的混合；GraphNorm 用可学习的 \(\rho_j\) 决定从列均值中保留多少信息，并以 \(\kappa_j,\eta_j\) 做 affine transform。两个通道 flatten、拼接后，五个 SoftMax 分别按 \(\arg\max\) 产生等级，联合 loss 是五项任务、全部训练样本和等级上的平均 cross-entropy。[pdf:E06]

最后，在线概率没有额外概率模型：

\[
P_{R,i}=\frac{N_{R,i}}{N_{\mathrm{test}}}\times100\%.
\]

也就是说，GNN 给出每个 sampled scenario 的硬标签，风险概率是这些硬标签的样本频率。因此概率质量同时受场景分布、采样覆盖和分类误差影响；它不是 classifier 自身经过 calibration 的 posterior probability。[pdf:E08]

## § 7 — 实验设计与结论

**问题 1：GNN 能否在未作为训练 loading point 的工况上逼近物理分析给出的多稳定概率？**  
**实验：** modified IEEE 39-bus 在 90%、95%、100%、105%、110% loading level 生成 9832 个训练样本；在线测试使用未作为训练点的 98% loading level 和 10000 个随机样本。模型为两个通道，每通道一个 FCL、两个带 GraphNorm 的 GCL，随后接 FCL；通道 FCL 和后续 FCL 的宽度分别为 8 和 128，\(\alpha=0.1,\beta=0.5\)，Adam learning rate 为 0.001，最多训练 500 epochs。[pdf:E09]  
**答案：** GNN 给出的 transient instability 为 1.68%，eigenvalue analysis/TDS 为 1.77%，绝对误差 0.09 个百分点；overall multi-instability 为 20.59%，物理基准为 21.24%，误差 0.65 个百分点。后一个概率显著高于任一 singular instability 的概率，支持作者“单项 SRA 会低估总风险”的案例结论。[pdf:E09]

**问题 2：图表示是否比常见非图模型更适合这项任务？**  
**实验：** 把双图 flatten 成一维特征，比较 decision tree、SVM、ANN、CNN 和 LSTM；以 eigenvalue analysis/TDS 为基准，比较六类概率的最大误差。  
**答案：** proposed GNN 在 IEEE 39-bus 的六项最大误差依次为 0.71%、0.05%、0.24%、0%、0.09%、0.65%，均为表中最低；CNN 和 LSTM 次之，传统 DT/SVM/ANN 更差。这个结果支持“利用 graph spatial correlation 有益”，但因为所有模型的结构、容量和调参预算是否等价未在该页展开，不能把差异全部归因于图结构。[pdf:E09]

**问题 3：SURs 能否揭示不同失稳类型的共同区与独有区？**  
**实验：** 对三个风场出力均匀采样 8000 个场景，在线路 8–9 三相接地故障下分别构造五类与 overall naive SURs，再按不稳定域体积顺序合并多个故障。  
**答案：** 频率、短期电压和暂态稳定存在大面积共同不稳定域；短期电压还有独有不稳定域；长期电压在该工况范围始终稳定。合并 14 类较轻故障时仍有较大稳定域，加入线路 39–1 和 8–9 后不稳定域显著扩大，再加入线路 16–17 和 16–24 后 integrated SUR 几乎全是不稳定域。作者据此区分可由运行控制规避的风险与需要专门 emergency control 的故障。[pdf:E10]

**问题 4：速度是否达到论文所谓 real-time？**  
**实验：** 在 Intel i7-10700 CPU 上分别测 feature generation、GNN probability assessment 和 naive SUR visualization，并与 eigenvalue analysis/TDS 比较。  
**答案：** IEEE 39-bus 的 10000 样本特征生成、GNN 评估和可视化分别在 0.030 s、0.22 s 和 0.21 s 内完成；50000 样本全流程 1.95 s，而物理分析分别耗时 3.88 h 和 19.43 h，论文报告至少节省 99.94% 时间。[pdf:E10][pdf:E11] 这证明的是该 CPU、该仿真模型和已训练网络上的 batch inference 速度，不等于含数据接入、异常检测、模型更新和控制决策的端到端控制中心时延。

**问题 5：规模扩大后结果是否仍成立？**  
**实验：** modified WECC 使用 179 buses、29 SGs、5 WFs，在 90%、100%、110% loading level 生成 27837 个训练样本；测试点为未作为训练点的 91% loading level、10000 个样本。modified GB 使用 2224 buses、3207 branches、384 generators、10 WFs，考虑 6 类 N-1、3 类 N-2 和 1 类 N-3 faults；在五个 loading level 上训练 30000 样本，测试点为 92%、5000 样本。[pdf:E11][pdf:E12]  
**答案：** WECC 的最大概率误差为 0.25 个百分点，低概率 transient instability 2.70% 的误差为 0.17 个百分点，overall multi-instability 为 30.75%，物理基准为 30.84%，各稳定类型 confusion matrix accuracy 至少 99.51%；10000 样本 MSRA 在 1.65 s 内完成，论文报告相对物理分析至少节省 99.99% 时间。[pdf:E11][pdf:E12] GB 的最大概率误差为 0.32 个百分点，表明在该组已建模复杂 contingencies 上仍能逼近基准。[pdf:E12]

实验没有验证的范围同样重要：没有真实电网 PMU 流、没有完整 hold-out topology family、没有恶意数据或通信丢包、没有跨仿真器或跨参数模型迁移，也没有硬件在环、EMT 或 FPGA 实验。

## § 8 — Take-aways

**5 句话：**  
1. 论文把五类稳定问题放在同一不确定性采样框架中，避免只看单项风险。  
2. operating graph 与 disturbance graph 分别表达当前状态和故障位置/类型，是方法相对普通向量模型的关键变化。  
3. GNN 只替代在线的大批量物理分析，ground-truth 仍由离线 eigenvalue analysis 和 TDS 生成。  
4. 三个测试系统中，作者报告了 0.09–0.65 个百分点量级的关键概率误差以及秒级 batch assessment/visualization。[pdf:E09][pdf:E10][pdf:E11][pdf:E12]  
5. 结果支持“实时风险筛查和区域可视化”，但不支持把模型外推为无需更新、可解释、抗攻击或适用于 EMT/FPGA 的通用稳定分析器。[pdf:E08][pdf:E13]

**3 句话：** GNN 学的是带拓扑和扰动位置的场景到五类稳定标签的替代映射。在线对大量候选场景快速分类并统计频率，再用 alpha shapes 画出 SURs。速度收益很大，但可靠性取决于离线物理标签和训练分布是否覆盖当前运行条件。

**1 句话：** 这是一种以双图 GNN 换取秒级多稳定风险筛查、以 SURs 换取可操作可视性的仿真验证方案，而不是对未见拓扑和真实运行环境给出保证的方法。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在线候选场景与其稳定判别关系仍被离线训练集充分覆盖，尤其是拓扑、故障类型、动态模型和不确定性分布没有发生足以改变 decision boundary 的 shift。**

这个假设一旦不成立，核心贡献会同时失效。五个 classifier 可能在未知区域给出高度一致但错误的硬标签，Eq. (22) 会把这些错误直接累计成风险概率，alpha shapes 又会把错误标签放大成看似清晰的稳定域。速度仍然很快，但“实时”只会更快地产生错误的风险地图。

论文给出的正面证据是：三个系统都在未作为训练 loading point 的插值工况上取得小误差；GB 还包括预先建模的 N-2 和 N-3 faults。[pdf:E09][pdf:E11][pdf:E12] 但它缺少更关键的证据：训练时完全 hold out 某一 topology/fault family、元件动态参数漂移、测量误差或不同仿真模型时，误差是否仍可控。作者自己规定“拓扑显著变化或出现新 contingency”时应重新生成物理标签并离线更新，同时承认具体 update strategy 不在本文范围内；结论还把 interpretability 和 cyberattack defense 留作未来工作。[pdf:E08][pdf:E13] 因而泛化能力是经局部插值验证的经验结果，不是可部署条件下的覆盖保证。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重做三个系统，而是验证“双图表示是否能在未见 loading point 上保持概率和边界准确”。

- **数据：** 用 ANDES 构建 modified IEEE 39-bus；选择三个风场出力和少量线路/机组故障，按论文五个 loading level 生成约 1 万个离线场景。对每个场景用 eigenvalue analysis/TDS 计算五类标签。论文给出工具和总体设置，但 PDF 没有给出可直接下载的数据集或完整参数仓库，因此这会是方法级复现，不保证逐字节复现论文表格。[pdf:E08][pdf:E09]
- **实现：** 建立 operating graph 与 disturbance graph；实现两通道、每通道两层 GCL + GraphNorm + initial residual identity mapping 的模型和一个 flatten-vector ANN baseline。只做五个二分类头和 Eq. (22) 概率统计；SUR 只选择两个风电轴与一个固定风电切片，避免复现完整可视化系统。
- **测试：** 完全留出 98% loading level，另外把线路 8–9 故障留作一个更严格的 fault-family hold-out。分别测五类及 overall instability probability 的绝对误差、balanced accuracy、false-stable rate，以及稳定/不稳定边界附近样本的错误率。
- **支持标准：** 若普通插值 hold-out 上 overall probability 误差不超过 1 个百分点，且双图模型的 false-stable rate 明显低于相同参数量的 flatten baseline，则支持论文最小核心 claim。
- **反驳标准：** 若双图模型只在随机切分上表现好，一旦整类故障 hold out 就出现超过 5 个百分点的 overall risk 低估，或边界附近 false-stable rate 与普通 ANN 无显著差异，则论文关于拓扑/扰动图带来可泛化实时 MSRA 的解释受到反驳。

时间测量应单独报告 feature construction、inference 与 SUR construction，并说明 CPU/GPU 和 batch size，不能只报神经网络 forward time。

## § 11 — 最强反例设计

最强反例是构造一个**训练分布内节点数不变、但拓扑/动态关系系统性改变**的测试集，使输入看起来“相似”，稳定边界却发生突变。

具体做法是：训练集中保留所有母线和常规 loading range，但完整 hold out 一组跨区联络线退出、低惯量机组组合以及相关 N-2 fault family；测试时再叠加风电 forecast distribution shift，把样本密集放在原 SUR 边界附近。ground truth 仍由 TDS/特征值分析得到。比较三件事：overall instability probability 的低估幅度、false-stable rate、alpha-shape stable region 被错误扩大的体积。

这个反例直接挑战论文机制，而不是泛泛说“神经网络会过拟合”。如果模型在未见 topology family 上把大量真实不稳定样本判成稳定，那么 operating/disturbance graph 虽然表达了结构，却没有学到可组合的物理规律；清晰的 SUR 反而会制造错误安全感。若错误主要集中在边界附近，还会说明论文报告的总体 accuracy 被大量易分类样本掩盖。反过来，如果在完全 hold-out 的拓扑族上仍保持低 false-stable rate 和保守风险边界，才是比当前插值 loading 测试更强的支持证据。[pdf:E08][pdf:E11]

## § 12 — Follow-up Research Idea

在电力系统稳定领域，高影响工作通常不仅要有更高平均 accuracy，还要说明失效边界、跨工况可信性、工程时延和对真实安全决策的价值。基于第 9 节，候选方向是把问题从“预测一个快速风险值”改成“在 topology/distribution shift 下给出可验证的保守多稳定风险上界和拒答区域”。这是候选想法，未做充分相关工作检索，不声称 novelty。

**（a）未满足的需求。** TSO 更需要知道“这个风险图在哪些区域可信、最坏会漏掉多少风险”，而不是只知道随机测试集平均误差很小。当前方法遇到新 topology/contingency 时只能触发离线补样本，触发规则和更新时限都没有闭合。[pdf:E08]

**（b）潜在研究价值。** 把输出从点估计改为带 coverage 的 upper risk bound、OOD score 和 abstention region，可以让模型在熟悉工况继续保持秒级，在陌生工况明确拒答并切回物理分析。研究目标由“平均更快”变成“在安全约束下尽可能快”，更贴近实际系统价值。

**（c）可借鉴工具。** 可结合 graph out-of-distribution detection、conformal prediction、distributionally robust optimization 与 active learning。GNN 负责结构表示，conformal/risk-control 层给出有限样本覆盖，active learning 只把最影响风险上界的陌生场景送回 TDS/特征值分析。

**（d）首个证伪实验。** 完整 hold out 若干 topology/fault families，要求所给 95% conservative upper bound 在每个 family 上都覆盖真实 multi-instability probability，同时统计拒答率和总时延。若 coverage 明显低于 95%，或为了覆盖而几乎全部拒答，则该想法失去实用性。

**（e）与本文的实质区别。** 本文输出五类硬标签的样本频率和确定性 SURs，陌生场景靠事后离线更新；候选方案把“是否知道自己不知道”纳入问题定义，输出带置信覆盖的风险上界与明确拒答域。它不是在原网络后再加一个模块追求更高 accuracy，而是改变安全评估的验收对象。
