# Physics-Embedded Neural ODEs for Sim-to-Real Edge Digital Twins of Hybrid Power Electronics Systems

- 作者：Jialin Zheng，Haoyu Wang，Yangbin Zeng，Di Mou，Xin Zhang，Hong Li，Sergio Vazquez，Leopoldo G. Franquelo
- 出处：*IEEE Transactions on Industrial Electronics*
- 年份：2026
- DOI：10.1109/TIE.2025.3645414
- Zotero key：NVRUXU44

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是一般意义上的“用神经网络拟合变换器波形”，而是一个同时受物理结构、实时性和硬件资源约束的问题：怎样把离线仿真模型迁移成部署在变换器旁边的 edge digital twin（EDT），使它既能跟上高频开关产生的离散模式跳变，又能补偿寄生参数、死区、器件非线性、温度和老化造成的 Sim-to-Real 偏差。作者强调，EDT 一旦参与实时监测甚至控制，模型失真不再只是预测误差，而可能直接转化为控制失败和安全风险。[pdf:E01]

困难来自三个同时存在的矛盾。第一，功率电子系统是 hybrid system：每个开关拓扑内部由连续 ODE 演化，拓扑之间又在开关时刻离散跳转；一个网络若把所有模式混在一起学，会把不同 vector field 互相干扰。第二，纯物理模型在仿真中准确，却不自动包含真实硬件的未建模效应与参数漂移；纯数据模型又要用大量数据从零重建已经知道的电路规律。第三，云端可训练复杂模型，边缘 FPGA 却必须用有限的 DSP、BRAM、LUT 在严格时限内完成推理。论文把这三件事分别对应到 event automata、physics-embedded Neural ODE 和 cloud-to-edge 硬件协同部署。[pdf:E02]

其工程价值在于把“数字孪生”从离线可视化模型变成可嵌入控制回路的实时状态估计器。论文最终不只比较离线误差，还把模型部署到 Xilinx XCZU5EV，并把 PENODE-EDT 用于物理变换器的 PI 状态跟踪和 MPC 辅助；这使核心问题具有明确的实时控制落点，而不是只在仿真数据集上证明拟合能力。[pdf:E11]

## § 2 — 前人工作与不足

作者把既有路线分成四类。physics-based event-driven solver 能显式处理开关事件和 variable-step 时间推进，但依赖完整、理想化的电路模型，不能从数据中吸收寄生效应或漂移。RNN、LSTM、GRU 等离散时间模型学习固定步长的状态映射：步长太大时会漏掉短模式，步长太小时又在长模式中制造冗余计算，而且换步长往往需要重新训练。普通 Neural ODE 与连续物理过程更匹配，却没有显式管理多个不连续 vector field。PINN 把 KCL/KVL 作为 loss 中的 soft constraint；PRNN 则把离散化的物理模型与离散 residual network 分两阶段训练，物理项冻结后无法再与 residual 共同修正。[pdf:E02][pdf:E10]

这些不足不是简单的“前人没考虑物理”。问题在于物理知识被放在了不合适的位置：soft constraint 只能鼓励而不能结构性保证物理项存在；两阶段 residual learning 会让第二阶段替已经冻结的错误物理参数兜底；单一连续网络则仍要在同一参数空间内承载多个不连续模式。作者据此主张，模式边界、连续动力学和物理先验必须分别得到显式表示，同时又要在同一个可微 ODE 中联合训练物理参数与 neural residual。[pdf:E09][pdf:E11]

硬件侧也有单独缺口。ONNX、FINN、HLS4ML 等工具能帮助把神经网络搬到 FPGA，但复杂网络仍难满足 power electronics 的亚微秒级要求；若训练数据又只来自仿真，部署工具本身并不会缩小 Sim-to-Real gap。因此论文不是只提出一个网络层，而是把数据采集、云端训练、量化剪枝、HLS 转换、并行单元和边缘事件求解串成一条部署链。[pdf:E02][pdf:E07]

## § 3 — 重建作者的思考路径

下面是基于作者对失败模式和既有方法的陈述所做的逆向重建，不是作者按此顺序给出的自述。

1. 先从开关变换器本体出发：boost、DAB 或 buck 的控制信号决定拓扑，拓扑决定当下的 ODE；因此“先认出模式、再积分该模式的动力学”比让一个大网络隐式分辨所有模式更自然。[pdf:E03]
2. 既然 mode transition 可由 PWM carrier 与 reference 的交点预测，就可以把高频均匀采样改成显式事件时间，减少采样延迟和无效时间步；event automata 因而成为调度器，而不是另一个黑盒预测器。[pdf:E03]
3. 每个模式内部仍是连续时间系统。Neural ODE 直接参数化 vector field，并允许 ODE solver 按状态变化快慢调整步长，比固定步长 RNN 更贴近对象的数学结构。[pdf:E04]
4. 工业仿真器已经包含大部分电路 ODE，完全丢弃这些知识再训练黑盒网络是不经济的。更合理的分工是让 \(f_{\mathrm{phy}}\) 承担已知主导动力学，让较小的 \(f_{\mathrm{NN}}\) 只学习仿真与硬件之间的 residual。[pdf:E05]
5. residual 的含义只有在两部分共同优化时才稳定；所以不能先把物理模型拟合完并永久冻结，而应让物理参数和 NN 权重通过同一个轨迹 loss 与 ODE 反向传播共同调整。[pdf:E05]
6. 最后再反推边缘实现：保留结构简单的线性物理项，剪枝和量化 residual，分别用 MVM 与 MVTU 并行执行，并让 LUT event automata 直接把 PWM 映射到 mode index，才有机会把学习模型放进实时 FPGA 时限。[pdf:E07]

这条路径的关键不是“物理 + AI”这个宽泛口号，而是三次结构拆分：离散事件与连续演化分开，已知物理与未知 residual 分开，云端训练与边缘确定性推理分开；随后再通过可微训练和统一硬件流水把它们重新接起来。

## § 4 — 核心 Intuition

PENODE 的直觉是：不要让一个网络同时猜“现在是哪种拓扑”和“该拓扑里状态怎样连续变化”，而应先用 event automata 确定模式，再让对应的连续 ODE 模块积分。[pdf:E03][pdf:E04] 在每个模式里，已知电路方程负责大尺度、可解释的运动，神经网络只补仿真模型遗漏的小 residual，并让两者端到端共同校准。[pdf:E05] 这样得到的模型既比纯黑盒更省数据，也比冻结的物理模型更能贴近真实硬件，同时保留适合 variable-step/event-driven 求解和 FPGA 并行化的结构。

## § 5 — 具体方法与完整 Pipeline

以论文中的 600 W 两级 dc-dc 系统为例，完整流程如下。

1. **采集与切分。** 物理平台由 25 kHz DAB 和四路并联 200 kHz buck 构成，TI TMS320F28069 产生控制，电压、电流传感器与 ADC 向 EDT 提供状态和控制信号；边缘侧收集不同工况轨迹，再通过 LAN/TCP/IP 上传云端。论文报告的硬件是 XCZU5EV，训练平台是 NVIDIA GeForce GTX 4070 Super 与 Intel Core i7-12700。[pdf:E06]
2. **事件编码。** 训练时，event automata 对完整历史 PWM/control 序列做 one-hot mode mapping，得到模式序列 \(\{z_k\}\) 与切换时刻 \(\{t_k\}\)，再按模式切分和聚类电压、电流轨迹。推理时不预先拥有完整控制序列，而是根据 control generation mechanism 预测下一个 carrier-reference 交点，选择最早事件并输出下一 mode 与 dwell time。[pdf:E03]
3. **逐模式连续建模。** 每个区间 \([t_k,t_{k+1})\) 只调用当前模式的 dynamics module。普通 NODE 用 \(f_{\mathrm{NN}}\) 直接参数化该模式的 ODE；PENODE 则写成 \(f_{\mathrm{phy}}+f_{\mathrm{NN}}\)，其中前者由电路参数构造，后者学习寄生、漂移或结构遗漏产生的 residual。区间末状态直接作为下一模式的初值。[pdf:E04][pdf:E05]
4. **云端训练。** Algorithm 1 先对齐时间戳、去噪、按开关组合聚类，并拆分 train/validation/test；随后预训练物理项，用 Bayesian optimization 搜索学习率和 batch size 等超参数，再联合训练 \(f_{\mathrm{phy}}\) 与 \(f_{\mathrm{NN}}\)，迭代到 loss 改善小于容差或达到最大轮数后导出参数。轨迹由 differentiable ODE solver 前向积分，梯度通过 adjoint sensitivity 或 automatic differentiation 回传。[pdf:E05][pdf:E06]
5. **压缩与定点化。** residual network 先 magnitude pruning，再把输入 activation 与权重线性映射到 8-bit integer，输出层保留 FP16；正文称线性物理项的 \(A,B\) 从 64-bit floating point 映射为 32-bit fixed point。需要注意，Fig. 7 顶部流程图的物理矩阵标签看起来写成 INT16，与正文的 32-bit 说法不一致，因此本卡不把物理支路的最终位宽视为已闭合事实。[pdf:E07]
6. **FPGA 映射。** HLS4ML 将 PyTorch residual 转成 C/C++ accelerator，再由 Vivado HLS 综合为 RTL/IP。物理项使用并行 MVM，neural term 使用含 multithreshold activation 的 MVTU；LUT-based event automata 读取 PWM 并映射 mode index，IP 最终集成进 Vivado bitstream。[pdf:E07]
7. **实时推进。** 论文既评估固定 200 ns 的 Euler/ODE1，也评估只在 switching instants 计算状态的 event-driven solver。该案例本身包含 25 kHz 与 200 kHz 两种开关频率，但论文未给出可泛化到任意多速率网络的独立同步算法；目前可确认的是 event automata 按实际事件分段，PENODE-EDS 在一个控制周期内使用 variable 8 steps。[pdf:E06][pdf:E11]

白盒、灰盒、黑盒只是同一结构的三个端点：白盒中 \(f_{\mathrm{NN}}\) 可以很小甚至为零；灰盒中已知子电路进入 \(f_{\mathrm{phy}}\)，未知部分由 residual 学习；黑盒中 \(f_{\mathrm{phy}}\) 可设为零，模型退化为普通 NODE。论文的主要 Sim-to-Real 优势出现在灰盒情形，因为那里既有可利用的主导物理，又确实存在需要数据修正的结构误差。[pdf:E05][pdf:E09]

## § 6 — 核心数学推导

第一层是 hybrid automaton。状态与模式分别写成

\[
x(t)\in\mathcal X\subseteq\mathbb R^{n_x},\qquad
z(t)\in\mathcal Z:=\{1,\ldots,Z\},
\]

在模式 \(z\) 内，

\[
\dot x(t)=F_z(t,x(t)).
\]

guard \(g(t,x)=0\) 定义 jump set \(\mathcal E\)，到达 \(t_{k+1}\) 后由

\[
z_{k+1}=\Delta\!\left(z_k,t_{k+1},x(t_{k+1})\right)
\]

选择下一模式。作者明确假定 jump 时 \(x(t_{k+1})\) 保持不变，用作下一 vector field 的初值。[pdf:E03]

对 PWM，事件条件具体化为 \(g(t)=c(t)-r(t)=0\)，其中 sawtooth carrier 为

\[
c(t)=2A_c\,\mathrm{mod}(t/T_c,1)-A_c.
\]

对所有可能的下一模式计算 dwell time \(\tau^k_{z\to z'}\)，取最早者：

\[
t_{k+1}=t_k+\min_{z'\in\mathbb M}\tau^k_{z\to z'},\qquad
z_{k+1}=\arg\min_{z'\in\mathbb M}\tau^k_{z\to z'}.
\]

直观上，这一步把“每个极小采样点检查一次是否切换”改成“直接求下一次切换何时发生”。[pdf:E03]

第二层是 continuous neuralization。每个模式的真实动力学写成 \(\dot x=f_z(x,u)\)。普通 NODE 用

\[
\dot x(t)=f_{\mathrm{NN}}\!\left(x(t),u(t),\theta_{\mathrm{NN}}\right),
\qquad
x(t)=x(t_0)+\int_{t_0}^{t}f_{\mathrm{NN}}(x(\tau),u(\tau))\,d\tau,
\]

再交给 ODE solver 得到轨迹。模型学的是连续 vector field，不是某个固定 \(\Delta t\) 下的 one-step map，因此可以与 RK4、Dopri5 或 adaptive solver 组合。[pdf:E04]

第三层是 physics embedding。作者把已知局部线性物理写成 \(f_{\mathrm{phy}}=Ax+Bu\)，并构造

\[
\dot x
=f_{\mathrm{phy}}(x,u,\theta_{\mathrm{phy}})
+f_{\mathrm{NN}}(x,\theta_{\mathrm{NN}}),
\qquad t\in[t_k,t_{k+1}).
\]

\(A=\mathcal F_A(\theta_{\mathrm{phy}})\)、\(B=\mathcal F_B(\theta_{\mathrm{phy}})\) 由 \(L,C,R\) 等物理参数生成；zero-vector padding 允许物理项只约束部分状态，而 residual 作用于其余或补偿非线性。这是“hard structural embedding”的具体含义：物理 ODE 直接出现在状态方程中，而不是只作为 loss penalty。[pdf:E05]

训练目标是多步轨迹均方误差

\[
\mathcal L
=\frac1K\sum_{k=1}^{K}
\left\|x(t_k)-x_{\mathrm{obs}}(t_k)\right\|_2^2.
\]

参数集合 \(\Theta=\{\theta_{\mathrm{phy}},\theta_{\mathrm{NN}}\}\) 通过 ODE 的 adjoint sensitivity 或 AD 联合求梯度，再由 Adam 更新。因而“物理参数校准”和“神经 residual 学习”不是两条独立拟合链；同一个轨迹误差会同时决定两部分应如何分担未建模动态。[pdf:E05]

## § 7 — 实验设计与结论

**问题 1：显式 event automata 是否真的让 hybrid dynamics 更容易学？** 作者在 triple-phase-shift DAB 的 black-box setting 中比较 RNN、LSTM、NODE 各自有无 EA 的版本，训练使用完整数据的 50%，并考察 in-domain 与 out-of-domain 波形、loss 和 neuron count。结果是有 EA 的模型平均收敛更快、最终误差更低；PENODE 到达同等 loss 约早 40 epochs，EA 让 NODE 所需 neuron number 降低超过 75%。这支持“先拆模式再学连续动力学”能降低学习负担，但数字来自该 DAB 工况，不能直接外推到模式数呈组合爆炸的大系统。[pdf:E07][pdf:E08]

**问题 2：PENODE 是否比 physics-only、纯数据和其他 physics-embedded 方法更能跨越 Sim-to-Real？** 主实验使用 1200 条 time-series trajectory，由 12 个输出电压点（12–24 V）、20 个 10%–110%–10% 大信号负载 profile 和 5 类随机叠加扰动组合而成；数据随机分成 840/240/120 条 train/validation/test，并用不同训练比例做 10 次独立试验。Table III 把 \(V_\mathrm{in}=10\text{–}40\) V、\(V_{\mathrm{out},1}=16\) V 设为 in-domain，把 \(V_\mathrm{in}=40\text{–}50\) V、\(V_{\mathrm{out},1}=24\) V 设为 out-of-domain；PENODE 与 PINN、PRNN、LSTM、NODE、physics-only 比较。[pdf:E07][pdf:E08]

Table IV 的 ablation 给出最清楚的量化结果：PENODE 在 white-box/gray-box 下的 A-MSE 为 0.02/0.12，A-MAPE 为 0.13%/0.64%，A-RMSE 为 0.17/0.51，\(R^2\) 为 0.99/0.97；PRNN 的对应 \(R^2\) 是 0.95/0.9088，physics-only 在 gray-box 中降到 0.68。这个结果支持联合连续 residual 比冻结物理项的两阶段 PRNN 更稳健，尤其在物理模型不完整时；但论文没有在多个独立硬件平台、多个拓扑或长期漂移周期上重复验证。[pdf:E09]

**问题 3：这种精度能否在边缘硬件的时限和资源内实现？** 作者在 XCZU5EV 上比较 PRNN、PINN、固定步长 PENODE-ODE1 和 PENODE-EDS。Table VI 报告单控制周期 latency 分别为 43.6、59.4、32.7、12.6 \(\mu s\)；PENODE-EDS 使用 variable 8 steps，占用 19.2% DSP48、7.86% BRAM、6.79% LUT，而 PINN 分别为 59.1%、31.6%、47.3%。因此表内数据支持 PENODE-EDS 相对最慢的 PINN 有约 4.7 倍 latency 改善，并显著节省资源；这里比较的是同一块 FPGA 的综合结果，不是跨器件的普适性能上界。[pdf:E11]

**问题 4：高保真 EDT 是否能改善真实控制，而不只是离线拟合？** Fig. 13 先展示 PI 控制下 PENODE-EDT 波形与物理测量接近，再比较 MPC 中只用初始物理模型的 Sim2Sim EDT 与经过数据校准的 Sim2Real EDT。作者报告前者因参数 mismatch 出现明显 overshoot，后者动态跟踪更好。这是有价值的闭环演示，但图中没有给出跨重复试验的统计量、稳定裕度或正式 safety guarantee，因此它证明“在该装置与工况中有控制收益”，还不能证明任意闭环使用都安全。[pdf:E10][pdf:E11]

## § 8 — Take-aways

**5 句话版**

1. 功率电子 EDT 的首要结构问题是 hybrid mode，不是网络容量不够；显式 event automata 能把离散模式选择与连续 vector-field 学习分开。[pdf:E03]
2. PENODE 把已知 \(Ax+Bu\) 与 neural residual 放在同一 ODE 内联合训练，从而让物理参数和未建模效应共同解释真实轨迹。[pdf:E05]
3. 在论文的 DAB 与两级 dc-dc 实验中，EA 缩短训练并减少模型规模，PENODE 在 white/gray/black-box 及 OOD 测试中优于所列 baselines。[pdf:E08][pdf:E09]
4. 量化、剪枝、MVM/MVTU 并行和 event-driven solver 使该模型能落到 XCZU5EV，PENODE-EDS 的单控制周期 latency 为 12.6 \(\mu s\)。[pdf:E07][pdf:E11]
5. 论文最强的证据是“模型结构—FPGA 实现—物理控制演示”闭环，但复杂拓扑、未知事件和长期漂移仍未验证。[pdf:E11][pdf:E12]

**3 句话版**

1. 作者用 event automata 管离散开关，用 physics-embedded Neural ODE 管每个模式内的连续动力学。
2. 这种分工在给定实验中同时改善了数据效率、OOD 精度、FPGA latency 与资源占用。[pdf:E08][pdf:E09][pdf:E11]
3. 结论成立的边界是事件规则与模式集合基本正确；一旦真实硬件产生未建模 mode 或 event-time drift，现有证据还不能保证优势保持。

**1 句话版**

PENODE 的核心贡献是把 hybrid power converter 的“何时换方程”和“方程内部怎样补偿 Sim-to-Real residual”分别显式建模，再把结果压缩成可实时运行的 edge digital twin。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**真实硬件中的关键 mode transition 能由已知的控制生成机制可靠预测，且已枚举模式足以覆盖运行；jump 时状态可视为连续不变。** 论文的 event predictor 以 PWM carrier 与 reference 的零交点求下一事件，transition map 决定 mode，且 Eq. (5) 后明确说明 \(x(t_{k+1})\) 在 jump 中保持不变。[pdf:E03]

这个假设一旦失效，错误不会只落在一个局部参数上。event automata 会把样本送入错误的 dynamics module，并从错误的切换时刻开始积分错误 vector field；后面的 \(f_{\mathrm{NN}}\) 即使拟合能力很强，也是在错误 mode 标签和 dwell time 下补偿，可能把 event error 吸收到 residual 中，破坏解释性与 OOD generalization。

真实变换器中可能破坏该假设的机制包括可变 dead time、diode reverse recovery、零电流导致的 DCM、饱和、保护动作、通信抖动和异步故障。这些是基于功率电子机制的候选风险，不是论文已经验证的失败。论文给出的正面证据是受控 PWM 条件下的 DAB/buck 波形、EA ablation 和物理平台实时演示；缺失的证据是故意错置 event time、引入未见模式、改变 guard surface 或让 mode 数随拓扑规模增加后的鲁棒性测试。[pdf:E08][pdf:E11] 作者在结论中也把复杂拓扑扩展、模块化大系统和在线老化适应列为未来工作，说明这些边界尚未闭合。[pdf:E12]

## § 10 — 最小复现实验

一周内最值得复现的不是整套 FPGA 流程，而是核心 claim 的最小闭环：**显式 mode segmentation 加 physics residual，是否在少量真实数据和 OOD 工况下优于同规模 monolithic NODE 与 physics-only。**

- **数据：** 使用一台两模式 buck 或 boost 小功率平台，记录 gate/PWM、\(V_\mathrm{in}\)、\(i_L\)、\(v_C\)、负载和 reference。采集约 100 条启动、负载阶跃和输入电压变化轨迹，把最高输入电压区间与一个负载变化速率完全留作 OOD；若没有安全硬件，可用仿真预训练，但最终至少需要一组真实示波器/ADC 轨迹验证 Sim-to-Real。
- **实现：** 从名义 \(L,C,R\) 写出每个模式的 \(f_{\mathrm{phy}}\)，以 gate edge 作为 event label；实现 per-mode PENODE 与一个参数量相同的 global NODE，再保留 physics-only。三者使用同一训练轨迹、同一 ODE solver、相同状态归一化和五个随机种子，避免把 solver 或容量优势误算成架构优势。
- **测量：** 同时报告全轨迹 NRMSE、开关边界前后固定窗口的 edge error、OOD load-step overshoot、训练时间和参数量；另外画出 \(f_{\mathrm{phy}}\) 与 \(f_{\mathrm{NN}}\) 的幅值，检查 residual 是否真的“小而平滑”，而不是重新学了一遍主动力学。
- **支持标准：** PENODE 在五个种子中稳定降低 OOD edge error 和全轨迹误差，且在更少真实训练轨迹下达到 global NODE 的精度；learned physical parameters 保持可解释，residual 能量显著小于主物理项。
- **反驳标准：** 在容量、solver 和数据完全对齐后，PENODE 没有稳定优势，或优势只来自已知 gate label；又或者 residual 与物理项同量级、物理参数漂移到不合理值。这将直接削弱“结构嵌入带来数据效率与解释性”的 claim。

这一复现只验证方法核心，不验证论文报告的 12.6 \(\mu s\) FPGA latency；后者需要同类 XCZU5EV、HLS 工具链和精确 synthesis 配置，属于第二阶段工程复现。[pdf:E11]

## § 11 — 最强反例设计

最强反例不是换一个更复杂网络，而是制造**训练中未出现、控制信号又不能完全指示的 hidden mode 与 event-time drift**。在同一 boost/buck 平台上，让 dead time 随温度或负载变化，并加入 DCM、diode reverse-recovery 或偶发保护动作；保持 \(V_\mathrm{in}\)、reference 和平均负载仍落在训练包络内，使失败不能简单归因于普通数值 OOD。然后只让 PENODE 看到原来的 PWM carrier/reference，event automata 仍按原 guard 预测 mode。

比较对象应包括原 PENODE、允许从状态变化中识别 event 的 neural hybrid automaton，以及不使用硬 mode assignment 的 global NODE。主要指标不是平均 MSE，而是 event-time calibration error、错误模式持续时间、switch-window peak error、MPC overshoot 和闭环 constraint violation。若 PENODE 在平均波形上仍好看，却在隐藏事件附近产生系统性相位错位或危险控制动作，就说明论文所展示的高精度主要依赖正确事件先验，而非对任意 Sim-to-Real hybrid dynamics 都稳健。

这个反例直接攻击 Eq. (3)–(8) 的 guard/event 闭合和 jump 连续性假设，而不是泛泛说“数据不够”。论文现有实验没有报告这类 guard drift 或 missing-mode 测试，因此结果无论支持还是反驳，都能显著改变我们对方法适用边界的判断。[pdf:E03][pdf:E08][pdf:E11]

## § 12 — Follow-up Research Idea

在工业电子与 power electronics 领域，高影响工作通常不仅需要更低的离线误差，还要给出物理可解释性、真实硬件上的确定性实时性能、跨工况/拓扑证据，以及模型进入控制回路后的收益和安全边界。本文已经覆盖单一硬件案例的实时部署与控制演示，但复杂拓扑、在线老化和 fault prognosis 仍被作者列为未来方向。[pdf:E11][pdf:E12]

一个非增量的候选方向是：**把问题从“已知 event automata 下学习连续 residual”改写为“带不确定性的 guard、reset 与 vector field 联合数字孪生”**。它不再假定 mode 与 event time 已闭合，而是同时输出当前 mode posterior、下一事件时间分布、可能的 state reset，以及各模式的 physics-residual dynamics；当 event uncertainty 超过阈值时，EDT 不向 MPC 提供单一确定轨迹，而切换到可达集合或保守控制包络。

- **未满足需求：** 真实硬件的 dead time、DCM、保护动作、器件老化和异步故障会移动 guard 或产生新 mode；固定 LUT event automata 无法表达“我不知道现在是哪一种模式”。
- **潜在研究价值：** 这会把 Sim-to-Real 从参数校准扩展到 hybrid structure calibration，并把模型不确定性直接连接到闭环安全，而不是只追求平均 MSE。
- **可借鉴工具：** hybrid system identification、change-point detection、neural hybrid automata、Bayesian event-time inference，以及 reachability/conformal prediction 可分别用于 guard 学习、模式后验和安全包络。论文参考文献中已列出 neural hybrid automata，但本卡未做外部相关工作穷尽检索。[pdf:E12]
- **首个证伪实验：** 训练时只给标称 dead time 与 CCM，测试时系统性扫 dead time、温度和 DCM 边界；若联合模型不能比固定 EA-PENODE 更准确地校准 event time，也不能减少 MPC constraint violation，那么“学习 guard uncertainty 有工程价值”的核心假设即被反驳。
- **与本文的实质区别：** 本文把 event automata 作为已知调度骨架，主要学习每个模式内的 continuous residual；候选方向把 guard、reset、未知 mode 和安全决策本身变成研究对象，改变了问题定义，而不是给 PENODE 再叠一层网络。

由于没有对最新相关工作的系统检索，这里只把它称为证据约束的候选研究方向，不声称 novelty。
