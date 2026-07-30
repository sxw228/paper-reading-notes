# Artificial Intelligence Aided Black-Box Modeling of Three-Phase Single-Stage Photovoltaic Inverter Systems

- 作者：Yuxi Men、Junhui Zhang、Xiaonan Lu、Tianqi Hong
- 出处：*IEEE Transactions on Industry Applications*, 61(2), March/April 2025, pp. 3317–3328
- 年份：2025
- DOI：10.1109/TIA.2025.3532415
- Zotero key：3PR5MK85
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很现实的建模困境：电网运营者需要知道 photovoltaic（PV）逆变器在扰动下会怎样响应，但厂家通常不会公开拓扑、无源器件参数和控制参数。传统 white-box model 只有在内部细节已知时才能逐元件建立方程；对多厂家、大规模 inverter-based resources（IBRs），这个前提经常不成立。作者因此提出只从可测输入、输出及其历史序列识别动态，用 nonlinear autoregressive exogenous neural network（NARX NN）建立离线 black-box model，而不要求知道内部拓扑和参数。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）[pdf:E02]（PDF 物理页 2，Introduction 的问题陈述与贡献）

重要性不只是“省去建模工作”。当 PV 渗透率升高时，系统影响分析、扰动研究和并网规划都依赖模型；模型若过于粗糙，会漏掉控制耦合和瞬态，模型若过于详细，又会受到保密信息和计算成本限制。论文将目标放在二者之间：学习一个能复现端口动态的 surrogate，供离线系统分析迁移使用，而不是把 NN 部署到逆变器控制板上。[pdf:E05]（PDF 物理页 5，Section IV 开头对离线用途的界定）

需要先收紧论文的真实 claim：它证明的是“在本文覆盖的仿真与硬件数据上，经过逐场景调参的 NARX 能高精度拟合所选输出”，不是“仅凭任意少量端口数据即可恢复任意未知逆变器的内部物理”，也不是稳定性保证或可跨设备直接复用的 universal model。作者自己的必要条件是数据集足够大且包含足够多样的系统动态。[pdf:E02]（PDF 物理页 2，black-box model 的数据充分性假设）

## § 2 — 前人工作与不足

论文把已有 PEC black-box modeling 分成几类。LTI model 适合单一工作点，但工作点变化后表达力不足；composite local linear state-space 和 polytopic model 用多个局部线性模型及权重覆盖非线性工况，却需要显式组织局部区域；Hammerstein–Wiener（HW）model 把静态非线性块与线性动态块串联，结构简单，但当系统中线性与非线性无法清楚分开、控制通道强耦合时，其固定结构限制了灵活性。[pdf:E03]（PDF 物理页 3，Section II）

NARX 相对这些方法的优势不是一个新的电力电子定律，而是“记忆”：它把过去的输入和过去的输出反馈给非线性函数，因此能表达电压、电流时序以及控制输出之间的非线性耦合。普通 NARX 本身仍可能被复杂非线性难住，作者用 ANN 作为函数逼近器来增强它。[pdf:E03]（PDF 物理页 3，NARX 与 ANN 的比较）

这项工作也不是从零出现。作者明确引用其 2023 年 ECCE 论文作为同一基本框架的 preliminary work，并说明本刊版本增加深入分析与进一步测试；所以更准确的贡献定位是：把既有 NARX black-box framework 扩展成完整的建模、数据处理和验证案例，并用 switching/average model、单机数据及多逆变器硬件 testbed 扩大证据面。作者还强调，参数细调、数据多样化、归一化、坐标变换和 cross-validation 等工程环节，可能比修改 NN 数学形式更影响效果。[pdf:E02]（PDF 物理页 2，三项贡献）

## § 3 — 重建作者的思考路径

以下是基于论文背景与方法组织所作的逆向重建，不是作者逐字陈述。

1. 首先接受一个工程事实：拿不到厂家内部参数时，不应再把“恢复完整 white-box model”当作前提，而应把可观测端口序列视为唯一可用信息。[pdf:E02]（PDF 物理页 2，white-box 与 black-box 的取舍）
2. 其次观察到单工作点线性模型无法覆盖多工况，HW 等固定分块结构也难以表达强非线性控制耦合，于是需要一个既有时间记忆、又有非线性逼近能力的输入输出映射。[pdf:E03]（PDF 物理页 3，Section II）
3. NARX 提供延迟输入/输出形成的有限历史，ANN 提供非线性函数逼近，因此可以把“内部状态看不见”转写成“从有限历史估计当前输出”。这一步改变的是状态的表达方式：不再显式命名每个电感电流、PI 积分状态，而让历史窗口充当可观测的隐状态代理。[pdf:E05]（PDF 物理页 5，Eq. (12) 及变量说明）
4. 只在一条平滑波形上拟合不足以证明动态建模，所以作者构造带 primary、secondary、tertiary control 的三相单级 PV 系统，并建立 switching 与 25 阶 nonlinear average model；这样可以主动制造分层控制切换和功率参考变化，并让 NARX 同时对照仿真测量与物理平均模型。[pdf:E04]（PDF 物理页 4，Fig. 1 与 Eq. (1)–(6)）[pdf:E05]（PDF 物理页 5，Eq. (7)–(11)）
5. 最后再用厂家工业逆变器数据和多逆变器 testbed 检查方法是否只会拟合自建 Simulink 模型。这个路径形成“可控仿真解释机制—单机硬件—系统级硬件”的递进验证，但仍没有消除训练覆盖域之外的外推风险。[pdf:E07]（PDF 物理页 7，Section V 的实验层次）[pdf:E09]（PDF 物理页 9，Fig. 7 与系统级试验说明）

## § 4 — 核心 Intuition

核心 intuition 是：未知逆变器的内部状态虽然不可见，但最近若干步的端口输入和输出携带了足以预测下一步输出的动态记忆。NARX 把这段历史送入非线性 NN，离线学出“历史窗口到当前输出”的映射；只要训练数据覆盖了目标工况，它就能在不恢复内部拓扑的情况下复现端口响应。[pdf:E05]（PDF 物理页 5，Eq. (12)）这是一种 behavioral identification，而不是物理参数辨识。

## § 5 — 具体方法与完整 Pipeline

以论文的单 PV inverter voltage-step test 为例，完整 pipeline 如下。

1. **固定端口变量。** 在逆变器输出端测量电流和电压，把 d-axis output current \(i_d\) 作为输入 \(u\)，把 d-axis output voltage \(v_d\) 作为目标输出 \(y\)。论文其他案例在 PCC 选择 \(i_{\mathrm{pcc}}\) 与 \(v_{\mathrm{pcc}}\)，但基本映射相同。[pdf:E07]（PDF 物理页 7，仿真案例的输入输出）[pdf:E09]（PDF 物理页 9，单机硬件案例）
2. **收集并整理序列。** 单机数据先从三相 \(abc\) 变换到同步旋转 \(dq\) frame，以直流量形式降低训练负担；输入与输出都归一化到 \([-1,1]\)。论文还建议按计算量与噪声之间的权衡调节 down-sampling rate，但没有报告所有案例的实际采样率。[pdf:E06]（PDF 物理页 6，数据处理说明）[pdf:E08]（PDF 物理页 8，Fig. 4–5 与 \(abc\!\to dq\) 说明）
3. **构造有限历史。** 在时刻 \(t\)，网络输入包含 \(u_t,u_{t-1},\ldots,u_{t-d_u}\) 和 \(y_{t-1},\ldots,y_{t-d_y}\)。这些 delays 决定模型能看到多长的输入激励和输出记忆。[pdf:E05]（PDF 物理页 5，Eq. (12)）
4. **离线训练。** 隐藏层用 `tansig` activation，输出层为线性映射，权重和 bias 用 Levenberg–Marquardt（LM）algorithm 迭代更新。作者从少量层、神经元和一步 delay 开始，再按拟合反馈 trial and error；复杂网络不一定更好，因为小数据配大网络会过拟合且增加计算量。[pdf:E06]（PDF 物理页 6，Fig. 2、Eq. (13)–(15) 与调参说明）
5. **逐案例选 architecture。** PV 单机案例使用 2 个 hidden layers、每层 10 个 neurons、two-step delay；battery inverter 使用两层、每层 6 个 neurons；系统级不同扰动又使用不同层数、神经元和 delay。这说明论文演示的是 scenario-specific model selection，而不是一套固定 architecture 横跨所有设备和扰动。[pdf:E09]（PDF 物理页 9，单机与 testbed 参数）[pdf:E10]（PDF 物理页 10，幅值/频率扰动参数）[pdf:E11]（PDF 物理页 11，相位扰动参数）
6. **验证并反归一化。** 用 validation sequence 计算 MSE、NMSE 与 fitting degree（FD），并把 NARX 输出与 switching model、25 阶 average model 或 hardware measurement 对齐比较。[pdf:E07]（PDF 物理页 7，Eq. (16)–(18) 与 simulation validation）

这条 pipeline 的执行边界很明确：NARX 在离线数据上训练，用于迁移到系统影响分析等离线应用；论文不要求也没有展示把它部署到 inverter controller、real-time simulator 或 FPGA。固定点位宽、逻辑资源、pipeline latency、实时步长、多速率调度和开关事件的显式处理均未报告。[pdf:E05]（PDF 物理页 5，Section IV 的用途界定）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文包含形式化数学，但它不是一个带误差上界或稳定性证明的 learning theory；数学分为“用于构造验证对象的物理 average model”和“用于拟合端口序列的 NARX regression”两层。

**第一层：物理验证对象。** Fig. 1 把 PV panels、DC–AC inverter、LCL filter、load/PCC/grid 与三级控制连在一起。Eq. (1) 用 LPF 得到 \(P,Q\)，Eq. (2) 是 \(P\!-\!f\) 与 \(Q\!-\!V\) droop，Eq. (4)–(5) 分别描述 primary 内环和 secondary restoration，Eq. (6)–(8) 描述 PCC 功率、tertiary control 和 PLL。[pdf:E04]（PDF 物理页 4，Fig. 1 与 Eq. (1)–(6)）主电路的 LCL filter、负载和 PCC 电流电压动态由 Eq. (9)–(10) 给出；合并全部方程后得到

\[
\dot{\mathbf{x}}=\mathbf{g}(\mathbf{x}),
\]

其中 \(\mathbf{x}\) 含 \(P,Q,\delta\)、各 PI 积分状态、PCC 功率、PLL 状态及 \(dq\) 轴电流电压等共 25 个 state variables，所以这是一个 nonlinear 25th-order large-signal model。[pdf:E05]（PDF 物理页 5，Eq. (7)–(11)）它在论文中是额外的 ground truth/check，不是部署 NARX 时必须知道的内部模型。

**第二层：NARX 映射。** 核心式为

\[
y_t=f\!\left(u_t,u_{t-1},\ldots,u_{t-d_u},
y_{t-1},\ldots,y_{t-d_y}\right).
\]

这里 \(d_u,d_y\) 是输入和输出 delay。直观上，\(f\) 不直接观察内部 state，而用有限历史近似“足以预测当前输出的状态摘要”。[pdf:E05]（PDF 物理页 5，Eq. (12)）

第 \(n\) 个 hidden layer 先做 affine transform，再做 `tansig`：

\[
\mathbf{z}^{n}=\mathbf{W}^{n}\mathbf{a}^{n-1}+\mathbf{b}^{n},\qquad
\mathbf{a}^{n}=\operatorname{tansig}(\mathbf{z}^{n}),
\]

最后通过线性输出层得到

\[
\hat{\mathbf{y}}=\mathbf{W}^{n+1}\mathbf{a}^{n}+\mathbf{b}^{n+1}.
\]

归一化到 \([-1,1]\) 与 `tansig` 的值域匹配；LM 负责拟合 \(\mathbf W,\mathbf b\)。这三式说明所谓 AI aided black-box model 的数学本体就是带 input/output feedback delays 的 supervised nonlinear regression。[pdf:E06]（PDF 物理页 6，Eq. (13)–(15)）

误差指标为

\[
\mathrm{MSE}=\frac{1}{N}\lVert \mathbf Y-\widetilde{\mathbf Y}\rVert^2,\qquad
\mathrm{NMSE}=\frac{\lVert \mathbf Y-\widetilde{\mathbf Y}\rVert^2}
{\lVert \mathbf Y-\overline{\mathbf Y}\rVert^2},
\]

\[
\mathrm{FD}=\left(1-\sqrt{\mathrm{NMSE}}\right)\times100\%.
\]

FD 把误差相对“只用样本均值预测”的基线归一化，越高越好。作者把一般 error margin 小于 5% 作为经验门槛，但也提醒这些指标依赖所选时间窗口，因此一个很高的整体 FD 不等于每个 transient peak 都同样准确。[pdf:E07]（PDF 物理页 7，Eq. (16)–(18) 与指标解释）

## § 7 — 实验设计与结论

**问题一：NARX 能否复现带完整 hierarchical control 的自建 PV system dynamics？**  
实验：在 MATLAB/Simulink 中建立 switching model，同时用 25 阶 average model 作第二参照；输入 \(i_{\mathrm{pcc}}\)、输出 \(v_{\mathrm{pcc}}\)，使用三层 \(10\!-\!15\!-\!10\) neurons 与 two-step delay。系统先在 islanded mode 下运行 primary control，随后启用 secondary control 把频率和电压恢复到 1 p.u.；grid-connected mode 中再把有功、无功参考升到 0.05 p.u. 后降回 0。[pdf:E07]（PDF 物理页 7，Section V-A）  
答案：三类曲线在 Fig. 3 中总体重合；作者报告 MSE \(=3.7\times10^{-9}\)、NMSE \(=5.5\times10^{-5}\)、FD \(=99.3\%\)。这支持模型能插值本文构造的分层控制 transient，但不能单独证明对未知 controller 或未见 fault 泛化。[pdf:E07]（PDF 物理页 7，报告数字）[pdf:E08]（PDF 物理页 8，Fig. 3）

**问题二：方法能否拟合真实单机 inverter voltage-step data？**  
实验：20-kW off-the-shelf GFL PV inverter 在 25%、50%、75% irradiance 下运行，30-kW battery inverter 在 25%、50%、75%、100% active-power setpoints 下运行；voltage 从 0.875 p.u. 到 1.1 p.u.、步长 0.025 p.u.，frequency 保持 60 Hz。两类数据都把 \(i_d\) 作为输入、\(v_d\) 作为输出。[pdf:E07]（PDF 物理页 7，单机实验设置）[pdf:E08]（PDF 物理页 8，Fig. 4–5）  
答案：PV model 使用两层、每层 10 neurons、two-step delay，报告 MSE \(=1.1146\)、NMSE \(=0.0018\)、FD \(=95.8\%\)；battery model 使用两层、每层 6 neurons、two-step delay，报告 MSE \(=1.5425\)、NMSE \(=0.0022\)、FD \(=95.4\%\)。Fig. 6 的阶跃平台整体吻合，但局部 zoom 仍能看到瞬态边缘和平台上的小偏差。[pdf:E09]（PDF 物理页 9，Fig. 6 与报告数字）

**问题三：在多设备 hardware testbed 和不同 grid disturbances 下是否仍能拟合？**  
实验：Fig. 7 的系统含 GFM1 250 kVA、GFM2 125 kVA、GFL battery inverter 125 kVA、diesel genset、540 kVA grid simulator 与 750 kVA load bank；作者在贡献陈述中将其称为 1-MW test system。模型以 GFM1 的 \(i_d\) 为输入、\(v_d\) 为输出，每种 disturbance 单独选 architecture。[pdf:E02]（PDF 物理页 2，1-MW test system 的作者陈述）[pdf:E09]（PDF 物理页 9，Fig. 7 与测量配置）  
答案分三组：

- Voltage magnitude 从 1.0 p.u. 分别增加 0.01–0.05 p.u.；三层、每层 20 neurons、five-step delays，MSE \(=1.6\times10^{-8}\)、NMSE \(=1.9\times10^{-3}\)、FD \(=95.6\%\)。[pdf:E09]（PDF 物理页 9，扰动与网络参数）[pdf:E10]（PDF 物理页 10，Fig. 8 与指标）
- Frequency 从 60 Hz 分别增加 0.1、0.2、0.3、0.4 Hz；0.4 Hz 时系统不稳定并触发 protection/disconnection。该场景用一层 5 neurons、two-step delays，MSE \(=8.3\times10^{-6}\)、NMSE \(=6.4\times10^{-5}\)、FD \(=99.2\%\)，表明在该已纳入数据的断开事件上仍能拟合波形。[pdf:E10]（PDF 物理页 10，Fig. 9、故障行为与指标）
- Phase 分别跳变 5°、10°；三层、每层 20 neurons、three-step delays，MSE \(=4.6\times10^{-7}\)、NMSE \(=5.4\times10^{-4}\)、FD \(=97.7\%\)。[pdf:E11]（PDF 物理页 11，Fig. 10 与指标）

这些实验支持“经逐场景训练和调参后，NARX 能以超过 95% 的 FD 拟合本文的硬件 voltage output”。不能从中外推的部分包括：一个 architecture 跨设备/跨事件复用、未见 disturbance 的 extrapolation、长期 free-running stability、端口交互的 multi-input/multi-output closure，以及实时或 FPGA implementation。论文也没有给出每个数据集的样本数、采样率、训练/验证切分边界、cross-validation 结果、随机种子、训练成本或代码，因此报告数字的独立复现性弱于其波形覆盖面。

## § 8 — Take-aways

**5 句话**

1. 论文把未知 PV inverter 的内部状态问题改写为“从有限输入输出历史预测当前端口输出”的 NARX regression。[pdf:E05]（PDF 物理页 5，Eq. (12)）
2. 它用完整 hierarchical-control switching/average model 提供可控 transient，再用真实单机和多逆变器硬件数据增加外部有效性。[pdf:E04]（PDF 物理页 4，Fig. 1）[pdf:E09]（PDF 物理页 9，Fig. 6–7）
3. 在本文各自调参的案例中，报告 FD 为 95.4%–99.3%，说明端口波形可以被高精度拟合。[pdf:E07]（PDF 物理页 7，仿真结果）[pdf:E09]（PDF 物理页 9，单机结果）[pdf:E10]（PDF 物理页 10，幅值/频率结果）[pdf:E11]（PDF 物理页 11，相位结果）
4. 成功的关键更像数据覆盖、归一化、坐标变换和 architecture tuning，而不是一个新的 NN 理论。[pdf:E02]（PDF 物理页 2，贡献二）[pdf:E06]（PDF 物理页 6，训练流程）
5. 最大未决问题是：高 FD 是否会在未见工况、free-running rollout 和 multi-inverter composition 中保持，而论文没有提供足够证据回答。

**3 句话**

1. 这是一个无需厂家拓扑参数、用端口历史进行离线 dynamic system identification 的实证方案。
2. 证据覆盖仿真、单机硬件和多逆变器扰动，但每种场景都单独调 architecture，且关键 data split 与复现细节未报告。
3. 因而应把结果理解成强有力的 in-distribution fitting evidence，而不是对任意未知 IBR 的可迁移稳定模型。

**1 句话**

NARX 证明了“端口历史可以很好地拟合已覆盖逆变器动态”，但尚未证明“这种拟合在覆盖域外仍是可信的系统模型”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**训练/验证数据已经覆盖模型未来会遇到的全部关键动态，使有限历史窗口成为当前状态的充分代理。** 一旦该假设失败，Eq. (12) 学到的只是训练轨迹附近的 interpolation；对未见控制模式、保护逻辑、饱和、拓扑变化或组合扰动，过去几步的相似波形可能对应不同内部状态，模型便会给出错误但看似平滑的输出。

论文对这一假设给出的正面证据是有意识地增加数据多样性：分层控制 transient、不同 irradiance/power setpoints、voltage/frequency/phase disturbances，以及工业多厂家设备。更重要的是，作者自己明确承认：若 training dataset 缺少多样 transient 或未覆盖 load change/fault，black-box model 的预测会受损；他们建议 data diversification 与 k-fold cross-validation。[pdf:E07]（PDF 物理页 7，Section IV 末的限制与建议）

缺失的证据同样关键。论文没有按“事件类型或 operating region 整块留出”的方式展示 out-of-distribution test，也没有比较 teacher-forced one-step prediction 与把自身输出反馈回去的 multi-step free run；不同实验还使用不同网络结构和 delays。[pdf:E09]（PDF 物理页 9，逐案例参数）[pdf:E10]（PDF 物理页 10，逐场景参数）因此，它证明了多种已覆盖场景可以分别拟合，却没有证明覆盖域边界可被识别，更没有证明越界时模型会拒绝而不是自信地产生错误轨迹。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重建整套 hierarchical control，而是复现单 PV inverter voltage-step mapping，并把 data leakage 排除掉。

- **数据：**取得论文参考文献 [33] 所指的 PV Inverter Experimental Data；论文说明其 hardware case 覆盖 voltage 0.875–1.1 p.u.、step 0.025 p.u. 以及 25%、50%、75% irradiance。[pdf:E07]（PDF 物理页 7，数据与工况）
- **实现：**从 \(abc\) 变换到 \(dq\)，以 \(i_d\) 为输入、\(v_d\) 为输出，按论文归一化到 \([-1,1]\)，实现 Eq. (12) 的 two-step input/output delays、两个 hidden layers、每层 10 neurons、`tansig` 与 LM training。[pdf:E06]（PDF 物理页 6，训练定义）[pdf:E09]（PDF 物理页 9，PV case architecture）
- **切分：**不要随机打散相邻时间点。按完整 voltage-step event 切分，留出若干整段 step 和一个完整 irradiance level 作 test，训练过程不得看到这些段。
- **测量：**按 Eq. (16)–(18) 报告 MSE、NMSE、FD，同时单独报告 step onset 后前若干采样点的 peak error、settling error，并画出 Fig. 6 同类 overlay。[pdf:E07]（PDF 物理页 7，指标）[pdf:E09]（PDF 物理页 9，Fig. 6）
- **支持标准：**若整事件留出的 test FD 仍接近论文报告的 95.8%，且 transient peak 没有系统性错位，则支持“历史 \(i_d,v_d\) 足以插值未参与训练的同类 voltage steps”。
- **反驳标准：**若随机点切分能得到高 FD，而整事件/整 irradiance 留出后 FD 显著下降，或 transient peak 与 settling time 明显错误，则说明论文式高拟合可能依赖强时间相关性或覆盖泄漏，不能当作泛化证据。

这个复现不需要 FPGA，也不需要知道 inverter topology；它直接检验论文最核心、又最容易被 data split 混淆的 claim。

## § 11 — 最强反例设计

最强反例是一个“**事件类型留出 + free-running rollout**”实验，它能区分真正的动态模型与只会 one-step curve fitting 的模型。

训练时只给模型 0.01–0.05 p.u. voltage-magnitude steps、5° phase step 和 0.1–0.3 Hz frequency steps；完全留出 0.4 Hz 事件，因为论文显示该事件触发 instability、protection 和 disconnection。[pdf:E10]（PDF 物理页 10，Fig. 9 与 0.4 Hz 事件）测试时再施加一个未见的组合扰动，例如 voltage magnitude step 与 0.4 Hz frequency step 同时发生。模型只在起始时获得真实 \(y\)，随后把自己的 \(\hat y\) 反馈为历史输出，连续 rollout，而不是每一步都喂入真实过去输出。

判据不是只看全窗口 FD，而是检查三件事：是否预测出保护发生，保护时刻是否正确，断开后的电压轨迹是否保持物理一致。若 teacher-forced one-step FD 仍高，但 free-running prediction 在保护前后漂移、漏掉断开或给出不可能的平滑轨迹，就出现一个具体替代解释：论文中的高 FD 主要来自真实历史输出和已覆盖事件提供的轨迹锚点，而不是模型已经获得可自主 rollout 的系统 dynamics。这个反例一旦成立，会直接削弱其作为 system-impact surrogate 的核心用途。

## § 12 — Follow-up Research Idea

本领域的高影响工作通常不只看一个平均拟合分数，还看多厂家实验、关键保护/控制事件、工程可实现性、可复现性，以及模型是否能安全进入系统级分析。本文已经提供较宽的 hardware scenario coverage，但适用域边界、越界检测和 multi-step closure 仍是空白。

为避免把目的、记录、数值和事件混成一个抽象标签，先固定候选方向中的对象：

| 来源 | 目的 | 具体对象 | 角色 | 成立条件或未知项 | 前后关系 | 候选词 | 首次定义 |
|---|---|---|---|---|---|---|---|
| 本文的数据覆盖假设 | 描述模型见过什么 | 训练事件的扰动类型、幅值范围、controller/保护状态与端口轨迹 | 记录 | [约束] 必须由真实 training set 计算；[未知] 本文未报告完整 split | 训练后形成，推理前查询 | 适用域记录 | 适用域记录是指由真实训练事件形成、可查询的覆盖范围描述 |
| 当前推理事件 | 判断是否越界 | 当前历史窗口到适用域记录的距离及校准误差上界 | 值 | [指标] held-out event 上的 coverage 与 error calibration；失准则推翻可信度 | 先计算，再决定是否预测 | 适用域置信度 | 适用域置信度是指当前事件与已验证覆盖范围的一致程度，不等同于 NN 输出概率 |
| 系统级使用者 | 阻止无证据外推 | 超出适用域时输出“拒绝/需物理模型接管” | 事件 | [指标] 越界事件漏报率与误拒率；不能只优化平均 FD | 置信度不足后触发 | 越界拒绝 | 越界拒绝是指模型不生成未经验证的轨迹并显式交回上游模型 |
| NARX 与 physics-based fallback | 检验能否成为动态 surrogate | 不喂真实历史输出的 multi-step closed-loop trajectory | 值 | [指标] event-wise FD、peak error、保护时刻、长期有界性 | 未拒绝时 rollout，失败时回退 | 多步闭合轨迹 | 多步闭合轨迹是指仅依赖外生输入和模型自身历史输出生成的连续响应 |

**候选研究方向：带适用域记录与越界拒绝的多步 black-box surrogate。** 它不是在 NARX 后面再加一个普通 uncertainty head，而是改变问题定义：模型不再被要求“对每个输入都给波形”，而是同时回答“这个事件是否在已验证适用域内”；域内才生成 multi-step closed-loop trajectory，域外立即拒绝并切换到 physics-based model、online identification 或新增试验。

（a）**未满足需求。** 系统影响分析真正需要的是可自主 rollout 且知道自己何时不可信的 surrogate；本文只给出逐场景高 FD，没有可审计覆盖边界。[pdf:E07]（PDF 物理页 7，作者对数据缺失 transient 的警告）

（b）**潜在研究价值。** 如果能在多厂家 IBR testbed 上同时减少未见保护事件的错误预测、保持域内计算效率，并给出可校准的拒绝率，这比再提高一个 in-distribution FD 小数点更接近电力电子与电力系统领域重视的工程安全性和系统价值。

（c）**可借鉴工具。** 可借鉴 system identification 的 set-membership/validation-domain 思想、machine learning 的 conformal calibration 或 out-of-distribution detection，以及 hybrid modeling 的 physics-based fallback；这些只是候选工具，当前未做充分相关工作检索。

（d）**第一个证伪实验。** 按第 11 节事件类型留出，让模型面对未见 0.4 Hz protection/disconnection 与组合扰动；如果它既不拒绝、又不能在 free run 中给出正确保护时刻，或校准误差上界不能覆盖真实误差，这个方向的核心机制就被证伪。

（e）**与本文的实质区别。** 本文优化的是给定数据与逐场景 architecture 下的输出拟合；候选方向优化的是“覆盖域识别—拒绝决策—多步闭合—物理回退”这一系统级可靠性契约。它改变了模型必须回答的问题，而不是只换一类 NN 或增加一个应用场景。

由于这里没有对 2025 年之后的相关工作做系统检索，上述内容只作为 evidence-constrained candidate idea，不声称 novelty。
