# Deep Learning-Based Modeling for Power Converters via Physics-Enhanced Hierarchical Neural Network

**作者：** Qianyi Shang, Fei Xiao, Yaxiang Fan, Ruitian Wang, Tiewei Song  
**出处：** *IEEE Transactions on Power Electronics*, Vol. 41, No. 4, 2026-04  
**DOI：** 10.1109/TPEL.2025.3629881  
**Zotero key：** BDZJXT4T

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“能否用 neural network 拟合一段变换器波形”，而是一个更严格的问题：能否在训练数据很少、工况发生变化、又需要保持电路机理可解释性的条件下，对功率变换器的电感电流与输出电压做高精度时域建模。作者把现有路线分成 physical modeling、纯 data-driven modeling 和 physics-informed neural network（PINN）：物理模型便于稳定性分析与控制设计，但很难同时做到通用和高精度；纯数据模型能逼近复杂动态，却数据需求高且像黑箱；常见 PINN 又多把物理规律放进 loss，约束较松，且存在计算量、跨工况泛化和训练稳定性问题。论文在 0.8 kW DAB 硬件实验上报告误差低于 3%，所以它瞄准的是“小数据 + 跨工况 + 物理约束”三者同时成立，而不是单纯追求一个更低的拟合误差。[pdf:E01]

这个问题对 EMT 和数字实时仿真很重要。DAB 包含高频开关、隔离变压器、串联电感和直流侧电容，模型既要跟踪开关尺度的 \(i_L\)，又要跟踪慢得多的 \(v_o\)。如果只能用很小步长的详细数值积分，参数扫描、控制器测试和系统级联合仿真会很慢；如果换成黑箱模型，又可能在未见工况下漂移或违反电路规律。论文选择 TPS 控制的 DAB，是因为 SPS、DPS、EPS 可视为 TPS 的特殊情形，因而同一个试验对象覆盖了较丰富的调制自由度。[pdf:E02][pdf:E03]

需要先划清工程边界：Fig. 8 的实验台包含 DSP+FPGA，但论文明确报告的模型训练与评估平台是 NVIDIA RTX 3080Ti GPU 和 12 GB RAM；正文没有给出 TL-PEODE 的 FPGA 部署、fixed-point 字长、HLS/HDL、资源占用、pipeline initiation interval 或确定性单步延迟。因此，这篇论文验证了硬件采集波形上的建模效果，却没有验证“模型本身可在 FPGA 上实时运行”。[pdf:E07]

## § 2 — 前人工作与不足

论文点名了三组最相关的既有路线。第一组是 LSTM、wavelet CNN 和 attention 等纯 data-driven 时序模型，它们可以从历史数据学习状态依赖，也能处理内部参数未知的变换器，但缺少显式电路模型，外推可靠性和物理解释有限。第二组是用 loss 把微分方程残差加入训练的 PINN；这能减少数据量，却只形成 soft constraint，最终预测未必严格满足电路方程。第三组是针对变换器的 physics-informed architecture，例如 PA-RNN、两个解耦网络的 hybrid framework，以及融合实验与仿真数据的模型；作者认为它们仍有数值迭代负担、跨工况需要重新采数和训练、或 RNN/FNN 梯度消失/爆炸等问题。[pdf:E01][pdf:E02]

论文真正改变的是“物理知识放在哪里”。常见 PINN 把物理规律作为 loss 的一个惩罚项，数据项和物理项之间需要权衡；PEODE 则把 DAB 的 ODE 和隐式求解器放进前向计算图，让状态更新先经过物理方程，再由数据驱动层学习 ODE 求解所需的潜在 stage state。作者把这称为 hard constraint。随后，TL-PEODE 再把预训练的 PEODE 与 ResNet-LSTM residual branch 相加，以吸收开关纹波、寄生效应和元件退化等简化模型未描述的成分。[pdf:E03][pdf:E04][pdf:E05]

但“前人不足”与“本文已解决”不能等同。论文只在同一 TPS-DAB 拓扑的两个调制点上做 seen/unseen 比较，并没有展示跨 converter topology 的实验；“无需重新训练”的引言表述，也与方法部分“冻结 PEODE、fine-tune data-driven branch”的实际流程不完全一致。更准确的结论是：论文展示了同一硬件拓扑、一个未见调制工况下的 residual transfer，而不是已经证明任意拓扑或任意 domain shift 都可零训练迁移。[pdf:E02][pdf:E06][pdf:E07]

## § 3 — 重建作者的思考路径

下面是**基于论文证据的思路重建**，不是作者逐字陈述。

第一步，研究者会发现 DAB 的主导动态并非未知：Kirchhoff 定律已经给出 \(i_L\) 与 \(v_o\) 的耦合 ODE，开关函数也由 TPS 的 \(D_1,D_2,D_\phi\) 决定。完全丢掉这些知识、让 LSTM 从少量波形中重新学一遍，统计效率很低。[pdf:E03]

第二步，直接用显式 Euler 或细步长数值积分又不理想。开关变换器具有 stiff、nonlinear 和 time-varying 特征，显式积分为了稳定可能需要极小步长；因此可以让 MLP 预测隐式 Runge-Kutta 的潜在 stage state，再用 GLIRK 把这些状态与电路 ODE 连接起来。这样，network 不再直接自由地“画下一点波形”，而是在一个物理求解步骤内部提供待学习量。[pdf:E04][pdf:E05]

第三步，理想 ODE 不会自动包含死区、寄生参数漂移、开关纹波和测量链误差。只靠 PEODE 会在新工况留下结构化 residual；与其把整个模型推倒重训，不如冻结已学到的主导物理 backbone，让 ResNet 抽取局部波形特征、LSTM 汇总历史，再只学 PEODE prediction 与真实波形之间的残差。[pdf:E04][pdf:E05][pdf:E06]

第四步，多输出、多时间尺度带来优化困难。ResNet 的 skip connection 缓解深层特征提取的梯度问题，LSTM 保留历史，最后 additive fusion 同时输出下一步 \(i_L\) 和 \(v_o\)。这一路径自然形成论文所谓的 hierarchical ResNet-LSTM：先局部 convolution，再时序 memory，最后 fully connected residual，与 PEODE 输出相加。[pdf:E02][pdf:E06]

## § 4 — 核心 Intuition

核心 intuition 是：不要让神经网络从零发明 DAB 的状态更新，而要让它在 Kirchhoff ODE 和稳定的 implicit solver 内学习“怎样走完这一步”；这样少量数据也能把学习空间压缩到物理允许的主动态附近。理想物理仍解释不了的高频与非理想细节，则交给一个只学习 residual 的 ResNet-LSTM，并通过 transfer learning 把主物理 backbone 留住。[pdf:E03][pdf:E04][pdf:E05]

用一句更直白的话说：PEODE 负责“这台电路原则上应该怎样动”，ResNet-LSTM 负责“真实硬件相对理想电路还差了什么”。这个分工很有吸引力，但也埋下一个关键问题：后加的自由 residual 是否会把前面得到的物理一致性重新破坏，论文没有用方程残差或守恒误差直接回答。[pdf:E04][pdf:E06]

## § 5 — 具体方法与完整 Pipeline

以论文的 TPS-DAB 为例，完整 pipeline 如下。

1. **确定物理状态与输入。** 模型状态是当前 \(i_L(t_n)\) 和 \(v_o(t_n)\)，控制/激励包含交流端方波 \(v_{ab}(t),v_{cd}(t)\)、time step \(\Delta t\) 与电路参数 \(\theta=\{L_s,C_2,R_T,R_{\text{load}}\}\)；ResNet-LSTM 还读取长度为 \(L\) 的历史 \(i_L,v_o\)。输出是下一步 \(i_L(t_{n+1}),v_o(t_{n+1})\)。Table I 明确列出了这些输入输出，而没有把 FPGA 时序或离散定点格式列入模型接口。[pdf:E06]

2. **把开关波形写成物理方程。** TPS 的 \(D_1,D_2,D_\phi\) 生成 primary/secondary switching functions \(s_{\mathrm{pri}},s_{\mathrm{sec}}\)，进而得到 \(v_{ab},v_{cd}\)。Kirchhoff 方程定义 secondary capacitor voltage 与 series-inductor current 的导数；这两条方程是 PEODE 的物理 backbone。[pdf:E03]

3. **PEODE 预训练。** MLP 接收当前状态并输出 GLIRK 的潜在 stage trajectories；GLIRK 使用 Butcher tableau 把它们投影为满足 DAB ODE 的下一步状态。若电路参数已知，只训练 network weights \(\{w,b\}\)；若未知，则把 \(\theta\) 与 network 一起反向传播估计。训练 loss 同时比较 \(t_n\) 与 \(t_{n+1}\) 的 observable state。[pdf:E04][pdf:E05][pdf:E06]

4. **构造 transfer residual branch。** 预训练 PEODE 的核心参数被冻结。相同的当前输入加上历史窗口送入 1-D ResNet，抽取局部开关/纹波特征；flatten 后由 LSTM 捕获时间依赖，dropout 用于减轻过拟合，fully connected layer 输出 residual。[pdf:E05][pdf:E06]

5. **层级融合。** 最终预测等于 PEODE provisional state 加 ResNet-LSTM residual。只 fine-tune data-driven branch 以最小化总 prediction loss。注意，这一步是“少量目标域训练”而不是严格的 zero-shot inference；论文没有报告每个目标域究竟用了多少新标签。[pdf:E04][pdf:E06]

6. **验证。** 加载最佳 checkpoint，向模型输入新的控制和状态序列，递归产生时域轨迹。论文用 500 组 seen waveforms 按 7:2:1 划分，并用另一个 TPS modulation point 作为 unseen case；硬件原型参数为 \(V_i=100\ \mathrm{V}\)、期望 \(V_o=60\ \mathrm{V}\)、\(f_s=20\ \mathrm{kHz}\)、turns ratio \(1{:}1\)、\(L_s=35\ \mu\mathrm{H}\)、\(R_T=0.34\ \Omega\)、\(C_1=4400\ \mu\mathrm{F}\)、\(C_2=500\ \mu\mathrm{F}\)。[pdf:E07]

论文通过 Bayesian optimization 得到的具体网络配置为：GLIRK、1 个 hidden layer、256 hidden units、learning rate \(5\times10^{-3}\)、Conv1D kernel size 3、128 个 ResNet channels、window size 7、Adam optimizer。这些是本文实验配置，不应被外推为所有变换器的最优设置。[pdf:E07]

## § 6 — 核心数学推导

### 6.1 DAB 的物理骨架

对 secondary-side capacitor，论文 Eq. (4) 为

\[
C_2\frac{dv_o(t)}{dt}
=n\,s_{\mathrm{sec}}(t)i_L(t)-\frac{v_o(t)}{R_{\mathrm{load}}}.
\]

左边是电容电流；右边第一项是变压器 secondary-side switching function 调制后的电感电流，第二项是负载电流。它强迫输出电压的变化满足电荷守恒，而不是由 network 任意决定。[pdf:E03]

对 series inductor，Eq. (5) 为

\[
L_s\frac{di_L(t)}{dt}
=s_{\mathrm{pri}}(t)V_i-n\,s_{\mathrm{sec}}(t)v_o(t)-R_Ti_L(t).
\]

直觉上，这是加在 \(L_s\) 上的净电压：primary bridge 激励减去折算到 primary 的 secondary voltage，再减去 parasitic resistance 压降。两条方程共同把 fast current 与 slow capacitor voltage 耦合起来；\(s_{\mathrm{pri}},s_{\mathrm{sec}}\) 则由 TPS 的 piecewise switching rules 给出。[pdf:E03]

### 6.2 为什么引入 implicit Runge-Kutta

显式 Euler 的 Eq. (9) 只是

\[
x(t_n+\Delta t)=x(t_n)+\Delta t\,f(x(t_n);\theta),
\]

对 stiff system 容易因步长过大而不稳定。PEODE 改用 \(\nu\)-stage Gauss-Legendre implicit Runge-Kutta（GLIRK）。论文 Eq. (10) 的核心 stage relation 是

\[
h_j=x_j(t_n)+\Delta t\sum_{i=1}^{\nu}
a_{j,i}f(t_n+c_i\Delta t,h_i),
\]

其中 \(h_j\) 是 \(t_n\) 与 \(t_{n+1}\) 之间不可观测的 latent stage state，\(A,b,c\) 是 Butcher tableau 系数。因为每个 \(h_j\) 同时依赖其他 stage，solver 是 implicit 的；论文再由 Eq. (11) 更新 terminal state，并用 Eq. (12) 的 polynomial 构造 GLIRK tableau。[pdf:E04]

### 6.3 network 在 solver 中学什么

MLP 不直接输出自由的完整波形，而是按 Eq. (13) 输出一组 latent trajectories：

\[
f_{\mathrm{MLP}}
=\sigma[W_2(W_1x+b_1)+b_2]
\longrightarrow
\{\hat{x}(t_{n+c_1}),\ldots,\hat{x}(t_{n+c_\nu})\}.
\]

这些 latent stage 被 GLIRK 与 Eq. (4)–(5) 连接起来。训练时，network weights 与可选的 circuit parameters \(\theta=\{L_s,C_2,R_T,R_{\mathrm{load}}\}\) 一起通过 solver 反向传播；Eq. (14) 同时惩罚 \(t_n\) 和 \(t_{n+1}\) 的 state mismatch。它的工程意义是：数据层提供“中间轨迹猜测”，物理层负责判断这个猜测能否形成一致的状态推进。[pdf:E05]

### 6.4 residual fusion

总体结构由 Eq. (7) 概括：

\[
\mathcal{F}_{\mathrm{TL\text{-}PEODE}}
:=\mathcal{F}_{\mathrm{Add}}
\left(\mathcal{N}(\cdot),
\mathrm{concat}[\mathcal{R}_{\mathrm{ResNet}}(\cdot),
\mathcal{G}_{\mathrm{LSTM}}(\cdot)]\right).
\]

\(\mathcal{N}\) 表示包含 Eq. (4)–(5) 的 physics branch，ResNet-LSTM 表示 residual branch，最后做 additive fusion。训练目标 Eq. (8) 是多状态、多时间点的平均 squared error。这里要保持一个严格区分：PEODE branch 的推进经过 ODE hard constraint，但 Eq. (7) 对**最终相加后的输出**没有再施加 Eq. (4)–(5)；因此“整个 TL-PEODE 必然物理一致”不是由这组公式自动推出的。[pdf:E04]

## § 7 — 实验设计与结论

### 问题 1：小数据下能否更快、更准地训练？

**实验。** 作者用 500 组 seen waveforms，比较 LSTM、ResNet、ResNet-LSTM、PINN 与 TL-PEODE 的 training loss 和 test accuracy；训练曲线画到 125 epochs。[pdf:E07][pdf:E08]

**答案。** 论文报告 TL-PEODE 在约 40–50 epochs 收敛，并用 500 samples 达到低于 3% 的 average estimation error；相同 accuracy 下比 loss-based PINN 收敛更快。这个结论支持“data-light training”，但只覆盖一个 DAB 数据规模，没有 data-scaling curve，也没有把“500 组 waveform”换算成独立工况数、总采样点数或采集时间。[pdf:E08]

### 问题 2：PEODE 相比 detailed numerical model 是否更省计算？

**实验。** 对 0.1 s target duration，Table IV 比较 detailed numerical ode15s（IRK1–5）与 PEODE/GLIRK。表中 detailed model 使用 100,001 steps、平均 GPU computation 3.43 s；PEODE 使用 1,428 steps、平均 0.0175 s。[pdf:E07]

**答案。** 在作者的 GPU 实现与该任务设置下，PEODE 的报告运行时间约为 detailed model 的 \(3.43/0.0175\approx196\) 分之一。这个比值证明的是特定 GPU benchmark 的吞吐优势，不是 FPGA 实时步长，也不能推出 0.0175 s/step；论文未报告 batch size、I/O、warm-up、kernel timing protocol 或 deterministic worst-case latency。[pdf:E07]

### 问题 3：未见调制工况下是否仍能保持精度？

**实验。** Seen case 1 使用 \([D_1,D_2,D_\phi]=[0.115,0.116,0.32]\)，unseen case 2 使用 \([0.395,0.405,0.275]\)。Table V 汇总 test dataset 中 30 次硬件实验的平均预测结果，并与 Runge-Kutta、LSTM、ResNet、ResNet-LSTM、PINN、PA-RNN 比较。[pdf:E07][pdf:E09]

**答案。** Table V 报告 TL-PEODE 的 \(i_L\) MAE 在 case 1/2 分别为 0.13/0.31，\(v_o\) 为 0.74/3.75；纯 ResNet-LSTM 在 case 2 为 22.58/46.61，PINN 为 2.12/7.94。作者还报告最高 accuracy 为 99.87%，并在 Fig. 13 中展示 TL-PEODE 对 seen 与 unseen steady-state waveform 的拟合更贴近 measurement。[pdf:E09]

这个结论能支持“同一 DAB、一个未见 TPS 点”的 generalization，却不能支持任意 load transient、parameter aging、不同 switching frequency 或跨 topology。特别是 case 2 标为 \(60\ \mathrm{V},300\ \mathrm{W}\)，case 1 为 \(60\ \mathrm{V},800\ \mathrm{W}\)，但只有一个 unseen 点，无法把性能归因拆成 modulation shift、load shift 与 transfer training 的各自作用。[pdf:E09]

### 问题 4：预测是否与 measurement 相关，电路参数是否可识别？

**实验。** Fig. 15 给出 ground truth 与 estimation 的 scatter；Fig. 16 同时训练 \(L_s,C_2,R_T,R_{\mathrm{load}}\)；Fig. 17 把 precise parameters 人为偏移 5%、10%、15%、20%。[pdf:E10]

**答案。** \(i_L\) 与 \(v_o\) scatter 的 \(R^2\) 分别为 0.994 和 0.989。识别值收敛到 \(L_s=34.9\ \mu\mathrm{H}\)、\(C_2=5.12\times10^2\ \mu\mathrm{F}\)、\(R_T=0.33\ \Omega\)、\(R_{\mathrm{load}}=4.51\ \Omega\)，与 Table II 的 nominal/measured quantity 接近；作者指出 \(L_s\) 与 \(R_T\) 的误差对最终 modeling accuracy 影响最大。[pdf:E10]

这组实验说明 parameters 与 waveform 可以联合拟合，但不是参数 identifiability 的严格证明：论文没有给 confidence interval、不同初值下的多解分析，且 \(C_2\) 明显收敛较慢。[pdf:E10]

## § 8 — Take-aways

### 5 句话

1. TL-PEODE 把 DAB ODE 和 GLIRK 放进 network architecture，而不是只把物理残差塞进 loss。[pdf:E03][pdf:E04]
2. 预训练 PEODE 学主导物理，ResNet-LSTM 学硬件相对理想模型的时序 residual。[pdf:E05][pdf:E06]
3. 在 0.8 kW TPS-DAB 的 500-waveform 实验中，作者报告低于 3% average estimation error，并在一个 unseen operating point 上明显优于纯 data-driven baselines。[pdf:E01][pdf:E08][pdf:E09]
4. GPU benchmark 显示 PEODE 比 detailed numerical model 快很多，但这不是 FPGA deployment 或 hard real-time 的证据。[pdf:E07]
5. 最值得继续追问的是：additive residual 提高 accuracy 后，最终输出是否仍满足 Kirchhoff/energy constraints；论文没有直接测这个量。[pdf:E04][pdf:E10]

### 3 句话

1. 论文的主要贡献是把“物理 solver”变成可训练模型的 backbone，再用 transfer residual 修正未知动态。[pdf:E04][pdf:E05]
2. 它有力证明了同一 TPS-DAB 上的小数据拟合与单点跨工况效果，但没有证明跨拓扑、零训练迁移或 FPGA 实时执行。[pdf:E06][pdf:E07][pdf:E09]
3. 因而最可信的结论是“physics-enhanced residual learning 对该硬件数据有效”，而不是“最终模型已经具备普遍物理一致性和通用实时性”。

### 1 句话

TL-PEODE 用可微分的 DAB-ODE/GLIRK 管住主动态、用 ResNet-LSTM 补残差，在一个 0.8 kW DAB 上取得强 accuracy，但物理一致性是否穿过 residual fusion 仍是未闭合的核心问题。[pdf:E04][pdf:E09]

## § 9 — 最脆弱的假设

最脆弱的假设是：**ResNet-LSTM 输出的 additive residual 只修正未建模动态，不会破坏 PEODE branch 已满足的电路约束。**

这个假设一旦不成立，论文最有区分度的卖点就会塌缩。PEODE 的 provisional state 经过 Eq. (4)–(5) 与 GLIRK，因此可以说 physics is in the architecture；但 TL-PEODE 的最终 output 是 Eq. (7) 中 physics output 与一个自由 learned residual 的相加，后者并未被限制在 Kirchhoff-consistent、passive 或 energy-bounded 的子空间。[pdf:E04][pdf:E06]

实际中它很可能失效。switching edge、dead time、load step、saturation 或参数老化产生的 residual 不只是“平滑的小误差”，而可能改变能量流和 state derivative；一个以 MAE 为唯一目标的 residual network 可以在采样点上更准，却在采样点之间形成不守恒的 trajectory。论文提供的证据是 waveform MAE、\(R^2\)、parameter sensitivity 和 visual fit；没有报告最终 TL-PEODE 的 Eq. (4)–(5) residual、KCL/KVL error、passivity、long-rollout energy drift 或 stability margin。[pdf:E09][pdf:E10]

所以，基于证据的判断是：论文证明了“accuracy gain”，但还没有证明“fusion 后的 physical consistency”。这不是说模型一定不物理，而是核心机制的最关键一环尚未被直接测量。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重做全部网络，而是同时复现“unseen accuracy gain”和“最终物理残差”。

**数据。** 使用论文报告的 TPS-DAB 参数：\(V_i=100\ \mathrm{V}\)、\(V_o=60\ \mathrm{V}\)、\(f_s=20\ \mathrm{kHz}\)、\(L_s=35\ \mu\mathrm{H}\)、\(C_2=500\ \mu\mathrm{F}\)、\(R_T=0.34\ \Omega\)。按 case 1 的 \([0.115,0.116,0.32]\) 生成/整理约 500 组 waveform，按 7:2:1 划分；case 2 用 \([0.395,0.405,0.275]\) 只做 target test。若论文随附数据可用，优先使用原数据以减少 acquisition 差异。[pdf:E07]

**实现。** 只实现三个模型：PEODE、ResNet-LSTM、TL-PEODE。PEODE 使用 GLIRK 与 Eq. (4)–(5)；TL 阶段冻结 PEODE，仅训练 residual branch。用论文 Table III 的 hidden units 256、learning rate \(5\times10^{-3}\)、kernel 3、channels 128、window 7、Adam 作为起点，并跑至少 5 个 random seeds。[pdf:E07]

**测量。**

- case 1 与 case 2 的 \(i_L,v_o\) MAE/RMSE、\(R^2\)；
- 达到稳定 validation loss 的 epochs 和 wall-clock；
- 对每个预测点计算 Eq. (4)–(5) 的 normalized residual；
- 做至少 1000 个连续 step 的 recursive rollout，记录 waveform error、energy drift 和发散率；
- 分别记录 PEODE provisional state 与 additive fusion 后 state 的物理残差。

**支持核心 claim 的结果。** case 2 中 TL-PEODE 应接近论文报告的 \(i_L/v_o\) MAE 0.31/3.75，并显著优于纯 ResNet-LSTM 的 22.58/46.61；更重要的是，fusion 后的方程残差不能显著差于 PEODE，且 long rollout 不发散。[pdf:E09]

**反驳核心 claim 的结果。** 如果 accuracy gain 只在单一 seed 出现，或者 fusion 后 Eq. (4)–(5) residual/energy drift 明显放大，即使 MAE 下降，也应否定“最终模型同时准确且 physically consistent”这一强结论。这个复现不需要 FPGA；FPGA 是后续独立的 deployment 问题。

## § 11 — 最强反例设计

最强反例是制造一种“短窗口 MAE 变好、长时物理行为变坏”的 domain shift。

具体做法是：训练仍用 case 1，测试时在一个 waveform 内同时施加 load step、dead-time 偏移和 \(L_s/R_T\) 缓慢漂移，并让测试区间跨越 switching edge。比较 PEODE、TL-PEODE，以及一个与 TL-PEODE 参数量相当但不带 physics backbone 的 ResNet-LSTM。对所有模型同时评估 sample-wise MAE、Eq. (4)–(5) residual、累计输入/输出/损耗 energy mismatch 和 10,000-step rollout stability。

这个设计直接攻击论文机制，而不是泛泛增加噪声。论文自己承认 PEODE 不能完整描述 switching ripple、parasitic effect 和 component degradation，并把这些交给 residual branch；Fig. 17 又显示 \(L_s,R_T\) 偏差最敏感。[pdf:E05][pdf:E10]

若 TL-PEODE 在短窗口 MAE 上仍最好，但出现更大的 KCL/KVL residual、非物理能量产生或 rollout instability，就得到一个有力替代解释：优势来自 residual network 对测量分布的统计拟合，而不是在新工况下仍保持 physics-consistent dynamics。反过来，若它在该测试中同时保持低 MAE、低方程残差和 bounded energy drift，才真正补上论文当前缺失的证据。

## § 12 — Follow-up Research Idea

### 候选方向：从“输出残差补偿”改成“可容许缺失物理的辨识”

这是一个**候选研究方向，不声称 novelty**；本卡没有对相邻领域做完整检索。

**（a）未满足的需求。** 当前 TL-PEODE 把 residual 直接加到 state output，accuracy 可以提高，但最终输出是否满足 circuit law 没有保证；同时 GPU speed 也没有转化为 FPGA 上的 deterministic real-time budget。[pdf:E04][pdf:E07]

**（b）问题重定义。** 不再问“怎样用 network 把预测误差补小”，而问“怎样只学习允许进入 DAB state equation 的 missing physics”。例如让 network 输出 dead-time voltage、parasitic loss、unmodeled current injection 或 parameter drift，再把它们作为受约束项送回 ODE：

\[
\dot{x}=f_{\mathrm{known}}(x,u,\theta)
+G(x,u)\,r_\phi(\text{history}),
\]

其中 \(r_\phi\) 必须满足 dimensional consistency、bounded dissipation 或 passivity constraint。这样 residual 修正的是 differential equation，而不是绕过方程修改最终 state。

**（c）可借鉴工具。** 可以借鉴 port-Hamiltonian neural network、passivity-constrained system identification、differentiable circuit simulation 和 constrained neural ODE；部署侧再用 fixed-point-aware training 与 hardware-in-the-loop timing analysis，把“物理可容许”与“FPGA 可执行”放到同一个验收里。

**（d）第一个可证伪实验。** 直接使用 §11 的复合 domain shift，对比 output-additive TL-PEODE 与 equation-residual model。若后者不能在相近 MAE 下显著降低 Eq. (4)–(5) residual、energy drift 和 long-rollout failure，或者其 implicit solve 无法满足目标 FPGA step budget，就应淘汰这个方向。

**（e）与本文的实质区别。** 本文把已知物理做成 backbone、把未知部分做成 output residual；候选方向把未知部分也限制为“可进入物理方程的机制项”，研究目标从 waveform approximation 改成 admissible missing-physics identification，并把 real-time determinism 作为一等约束。这不是简单再加一层 network，而是改变 residual 的语义、约束位置和验收标准。
