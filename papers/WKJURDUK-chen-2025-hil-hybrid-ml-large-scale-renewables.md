# Hardware-in-the-Loop Real-Time Transient Emulation of Large-Scale Renewable Energy Installations Based on Hybrid Machine Learning Modeling

作者：Ruogu Chen, Tianshi Cheng, Ning Lin, Tian Liang, Venkata Dinavahi
出处：*IEEE Journal of Emerging and Selected Topics in Industrial Electronics*, Vol. 6, No. 2
年份：2025
DOI：10.1109/JESTIE.2024.3434364
Zotero key：WKJURDUK

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的工程矛盾：风电、光伏和电池储能等 inverter-based resources（IBR）需要足够细的 electromagnetic transient（EMT）模型来观察快速暂态，但当设备数量达到场站规模时，逐台求解非线性离散方程的计算量会迅速增大。作者希望用神经网络替代单个或成组 IBR 的传统计算模型，再把这些替代模型放到 FPGA 上，与较大步长的电网 transient stability（TS）模型组成多时间尺度实时系统。论文摘要把目标概括为：以 MLP 和 GRU 表示 IBR 暂态，把成批 ML 模块接入基于 IEEE 118-bus 的交流系统，并在 FPGA 上做实时硬件加速。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，不只是因为“神经网络更快”，而是因为规划和控制研究往往同时需要两种分辨率：IBR 侧要看到几十微秒尺度的电流和内部状态变化，电网侧又要容纳百节点网络。如果每个风机、面板或电池都保留完整计算模型，规模与实时性会冲突；如果只保留粗粒度 TS 模型，又可能丢掉 IBR 暂态。作者明确把传统 EMT 模型随设备数量扩展所遇到的计算约束作为研究动机，并用 EMT-TS 混合步长来分担不同时间尺度。[pdf:E02]（PDF 物理页 2，Introduction）

需要先限定论文所称的 “large-scale”。正式 HIL 测试系统不是一个同构光伏 VSC 场站，而是一个异构 IBR microgrid：180 台 DFIG 风机、320 块 PV panel、一个按 50 MW 缩放的 BESS，再接到 IEEE 118-bus 的 Bus 25。这里的规模来自固定小模块的批量复制和大网络接入，不等于论文训练或验证了任意拓扑、任意数量设备的统一模型。[pdf:E06]（PDF 物理页 6，Section III-A 与 Table I）

## § 2 — 前人工作与不足

论文给出的技术背景可以分为三条线。第一，传统 EMT 能解析到 sub-μs 级的快速暂态，但大规模非线性离散方程求解代价高；已有 GPU massive-thread 方法解决部分并行计算问题，却没有消除每个物理模型本身的求解负担。第二，ANN 已用于电力系统等值、长期稳态分析和其他 ML 任务，但作者认为这些工作不足以快速预测复杂、强非线性可再生能源设备的暂态。第三，EMT-TS 混合仿真早已存在，FPGA 也已用于神经网络 EMT 模型；论文指出此前相关 FPGA-ML EMT 工作集中在电机、变换器等较小系统，而不是本文这种多类 IBR 加 118-bus 的组合。[pdf:E02]（PDF 物理页 2，Introduction，文献 [6]–[21]）

因此，论文真正补的工程缺口不是发明 GRU、MLP、量化或多速率仿真，而是把这些已有手段串成一条可综合的系统路径：传统 IBR 模型生成数据，GRU/MLP 学习固定模块行为，量化后用 Vitis HLS 实现，再通过缓冲和全局时钟与 5 ms 的 TS 网络同步。作者把这称为 hybrid ML-based large-scale renewable installation 的 HIL emulation，并报告整个加速系统的等效 faster-than-real-time（FTRT）比为 3.33。[pdf:E02]（PDF 物理页 2，贡献列表）

论文没有提供与 topology-conditioned surrogate、跨拓扑 graph model 或静态调度编译器的比较；也没有系统检索“固定拓扑训练、未见拓扑测试”这一类工作。因此，本卡不据此声称论文或后续方向具有 novelty。

## § 3 — 重建作者的思考路径

从论文出现以前的知识出发，可以重建出如下思路。研究者首先会发现，风场中不同风速、PV 的辐照变化和电池的温度/SOC 让“一个稳态等值源”不足以复现暂态；但把每台设备的传统非线性模型都放进实时仿真，又会造成计算量随设备数量增加。已有经验同时给出两个线索：GRU 擅长带记忆的时序映射，MLP 擅长静态非线性映射；FPGA 则能把规则的矩阵运算、LUT 和流水线并行化。[pdf:E02]（PDF 物理页 2，Introduction）

下一步自然不是直接学习整个 118-bus 系统，而是先找可重复的局部边界：让风机和电池模块输出 Norton/电流源等接口量，让 PV 模块学习端口电压和辐照到输出电流的关系。对有显著内部状态的风机和电池保留递归特征，对主要体现静态 I-V 关系的 PV 使用前馈网络。这样，ML 模块可以继续通过端口量与传统网络求解器交换数据，而不必把整个网络方程塞进一个黑箱。[pdf:E03]（PDF 物理页 3，Fig. 1、Fig. 2 与 Eqs. (1)–(7)）

最后一步是把时间尺度拆开：IBR surrogate 每 50 μs 演化一次，118-bus TS 网络每 5 ms 更新一次；前者在一次网络交换间隔内运行 100 次。只要 FPGA 上 100 次 IBR 计算的墙钟延迟小于 5 ms，系统就能快于实时运行。这条推演能解释论文设计，但它是基于原文的重建，不是作者逐句陈述的历史过程。[pdf:E06][pdf:E08]（PDF 物理页 6、8，Section III-A、III-D）

## § 4 — 核心 Intuition

核心直觉是：不要实时求解每个 IBR 的完整非线性模型，而是学习“给定端口和环境输入，下一步端口输出与必要内部状态是什么”，再把这种固定小模块批量复制。对有记忆的风机和电池用 GRU，对近似静态 I-V 映射的 PV 用 MLP；在网络交换之间让这些模块以更小步长自行递推。FPGA 的量化、LUT 与流水线让成批推理的墙钟时间落在仿真步长预算内。[pdf:E04][pdf:E08]

## § 5 — 具体方法与完整 Pipeline

### 5.1 训练真值与三类 surrogate

作者先以既有传统模型生成训练真值：DFIG 风机来自 MATLAB Simulink 模型，电池采用 Thévenin/Norton 等值，PV 采用单二极管模型并由优化的 C++ 程序生成数据。论文称这些传统模型基于已被 PSCAD/EMTDC 等商业软件验证的研究工作，但没有给出本项目所用代码、数据文件或逐样本交叉验证记录。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Section II-A）

- **DFIG-GRU**：一个网络代表六台并联风机。图中当前输入包含风速 \(V_w\)、转矩 \(T_m\)、转速 \(\omega_r\)、三相端口电压 \(V_{abc}\)、有功 \(P\) 和无功 \(Q\)，输出包含三相电流 \(I_{abc}\) 以及下一步使用的内部/派生特征。正文明确点名 \(T_m\) 与 \(\omega_r\) 为递归特征，Fig. 3(a) 还用红框标出了被反馈的特征。最终结构是一层 GRU，hidden size 30，sequence length 5。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Fig. 3(a)、Section II-B3）
- **Battery-GRU**：电气特征包括端电压 \(V_t\)、输出电流 \(I_{out}\)、输入电流 \(I_i\) 和 SOC；热特征包括环境温度 \(T_a\)、\(dE/dT\) 与 \(dQ/dT\)。模型输出 \(I_{out}\)，并递推 \(I_i\) 与 SOC；一个网络代表 \(3\times4\) 电池阵列。最终结构是一层 GRU，hidden size 20，sequence length 3。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Fig. 3(b)、Section II-B4）
- **PV-MLP**：一个网络固定代表 \(4\times4\) panel array。输入是 16 个 panel 的辐照 \(I_{rr1}\ldots I_{rr16}\) 与端电压 \(V_t\)，输出阵列电流 \(I_{out}\)。网络有四个 hidden layers，每层 hidden size 64。作者选择 MLP 的理由是该 PV 模型主要表现静态非线性 I-V 关系，而非强时间依赖。[pdf:E04][pdf:E06]（PDF 物理页 4、6，Fig. 3(c)、Section II-B5）

### 5.2 数据、训练和验证边界

DFIG 训练序列保持一次 Monte Carlo run 内输入连续。风速按均值 10 m/s、标准差 3 m/s 的正态分布生成；训练集中加入并网点三相对称故障，短路电阻 0.01 Ω、持续 100 ms，故障样本占数据集 5%。DFIG 训练使用 dropout 0.2、1000 epochs、learning rate 0.001、batch size 1000 和 Adam。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Section II-B3）

PV 训练辐照按均值 1000 W/m²、标准差 300 W/m² 的正态分布生成，端口电压从 0 线性扫到最大工作电压，learning rate 从 0.00001 降到 0.000005。验证数据另行随机生成，未出现在训练数据中。[pdf:E06]（PDF 物理页 6，Section II-B5）

训练/测试划分需要特别澄清：论文没有报告总样本数、train/validation/test 百分比、随机种子或数据文件。它只说明若干验证工况未出现在训练集中，并报告 DFIG 训练集内故障占比 5%。因此不能把这些描述改写成标准的随机 train/test split，也无法独立排除相邻时间序列泄漏。

### 5.3 “Large-scale” 系统实际如何构成

正式 test bench 由固定模块复制而来：

1. 30 个 DFIG-GRU bundle，每个 bundle 表示 6 台并联风机，共 180 台；每个 bundle 额定 9 MW，30 个并联得到 270 MW。
2. 20 个 \(4\times4\) PV-MLP batch，共 320 块 panel；四个 batch 串联成一串、五串并联，总功率 62.5 kW。
3. 一个按 50 MW 缩放的 BESS station。
4. 上述 IBR microgrid 通过 25/138 kV 变压器接入 IEEE 118-bus 的 Bus 25。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Section III-A、Fig. 8）

这意味着论文有 **batched module**，但没有学习可变 series/parallel 拓扑。PV 训练和部署都是固定 \(4\times4\) 小阵列，再按固定“四串五并”组合；风场也是固定六机 bundle 的复制。论文没有 topology descriptor、可变邻接矩阵、跨拓扑 hold-out、模块插拔训练或拓扑规模泛化实验。所谓 individual characteristics 的证据主要是给不同风机组设置不同风速、给 PV 的特定 panel 设置不同辐照，而不是改变电气拓扑。[pdf:E07][pdf:E09]（PDF 物理页 7、9，Fig. 8、Scenarios 1–2）

### 5.4 FPGA 映射、数值表示与同步

硬件是 **Xilinx VCU118，器件 UltraScale+ XCVU9P**，不是 XCKU060。板上可用资源为 4320 BRAM、6840 DSP、2.364 M FF 和 1.182 M LUT。Table I 报告整个 test bench 使用 93.3% DSP、24.42% FF、61.3% LUT；BRAM 利用量在表中以 “–” 给出，不能从该表补推。[pdf:E06]（PDF 物理页 6，Section III-B 与 Table I）

PyTorch 训练模型原为 float32；作者对 GRU 使用 dynamic quantization，对 MLP 使用 static quantization，并在 HLS C++ 中用 `ap_int<8>` 容纳量化后的 int8 数据。sigmoid LUT 的输入范围是 \([-10,10]\)，tanh LUT 的范围是 \([-6,6]\)，步长均为 0.001；循环采用 fully pipelined 实现。[pdf:E07][pdf:E08]（PDF 物理页 7–8，Eqs. (10)–(11)、Section III-C2）

但论文只明确了量化数据的 int8 表示，没有完整报告累加器、bias、LUT 输出、缩放中间量和端口量的总位宽/小数位分配，也没有给出 overflow、saturation 或 rounding 的逐层策略。因此“系统全部采用 8 bit 定点”并不是可由原文支持的结论。

### 5.5 步长、推理延迟、系统预算与 HIL 边界

IBR 模型的仿真步长为 50 μs，118-bus TS 模型的仿真步长为 5 ms，所以一次网络数据交换之间，IBR 模块运行 100 步。Table I 基于 10 ns FPGA clock 报告 wind、battery、PV 和 118-bus 模块单次计算延迟分别为 15、10、6 和 30 μs；对应单模块 FTRT 比分别为 3.33、5、8.33 和 166.67。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Table I、Section III-B）

集成系统并不是用 30 μs 作为一个 5 ms 周期的总延迟。同步逻辑让三类 IBR 各做 100 次计算，最慢的 wind module 决定墙钟延迟 \(100\times15\,\mu s=1.5\,ms\)，之后才交换数据；因此集成系统相对于 5 ms 模拟时间的等效 FTRT 比是 3.33。[pdf:E08]（PDF 物理页 8，Fig. 10 与 Section III-D）Fig. 10 把 1.5 ms 标成 “System Equivalent Time-Step”，正文则把它解释为 equivalent system latency，而 Section III-A 又把最大仿真步长 5 ms 称作 entire-system equivalent time-step；术语存在内部不一致，但数值关系可以闭合。

这些数值是按综合后的 cycle latency 给出的。论文未报告负载抖动分布、板上长时间 deadline miss 统计、post-route 最差路径裕量或独立 WCET（worst-case execution time，最坏执行时间）分析，所以应称为“报告的确定周期延迟”，不应扩写成已经完成 WCET 认证。

硬件照片显示 host PC、VCU118、FMC DAC adapter、DAC board、SMA cable 和 oscilloscope。论文没有展示一个外部物理控制器、功率变换器或 protection device 与 FPGA 仿真器构成闭环，也没有给出外部 I/O 闭环时序。因此可确认的 HIL 边界是 FPGA 上运行模型并通过 DAC/示波器观察输出；更强的 controller-HIL 或 power-HIL 边界仍属未报告。[pdf:E07]（PDF 物理页 7，Fig. 8(c)）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有提出新的收敛定理或误差界；数学主体是传统等值模型、GRU/MLP 前向计算和量化映射。最关键的是理解这些式子如何保持可接入网络求解器的端口形式。

电池先由内部电压组成 Thévenin 源：

\[
V_{\mathrm{Bat}}=E_0+E_{\mathrm{pol}}+E_{\mathrm{exp}}+S_cE_{\mathrm{chg}}+(1-S_c)E_{\mathrm{dsc}},
\]

其中 \(S_c=1\) 表示充电。为了让节点电压求解器使用，作者将其变成 Norton 注入电流：

\[
\mathbf I_{\mathrm{B,eq}}=\mathbf V_{\mathrm{Bat}}\circ\mathbf G_{\mathrm B}.
\]

这里 \(\circ\) 是逐元素乘法，工程含义是“每个电池支路用一个并联电流源加电导接入网络”，从而让 surrogate 最终也以端口电流形式参与网络交换。PV 的光生电流写为

\[
I_{\mathrm{ph}}=
\frac{S_{\mathrm{irr}}}{S_{\mathrm{irr}}^*}
\cdot I_{\mathrm{ph}}^*
\cdot\bigl(1+\alpha_T(T_K-T_K^*)\bigr).
\]

\(S_{\mathrm{irr}}\) 是辐照，\(\alpha_T\) 是温度系数，\(T_K\) 是绝对温度，带星号的量是参考值；PV 最终也被转成两节点 Norton 等值。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(3)）

GRU 的状态更新为：

\[
\begin{aligned}
z_t &= \sigma(W^z_{ih}x_t+b^z_{ih}+W^z_{hh}h_{t-1}+b^z_{hh}),\\
r_t &= \sigma(W^r_{ih}x_t+b^r_{ih}+W^r_{hh}h_{t-1}+b^r_{hh}),\\
n_t &= \tanh(W^n_{ih}x_t+b^n_{ih}+r_t\circ(W^n_{hh}h_{t-1}+b^n_{hh})),\\
h_t &= (1-z_t)\circ n_t+z_t\circ h_{t-1}.
\end{aligned}
\]

\(r_t\) 决定旧状态中哪些信息先被“忘掉”，\(z_t\) 决定候选状态与旧状态如何混合。对风机和电池而言，这个递归状态承担了传统模型内部动态的压缩记忆；但论文没有证明该隐藏状态与物理状态一一对应，也没有给出长时滚动误差上界。[pdf:E03]（PDF 物理页 3，Eqs. (4)–(7)、Fig. 2）

MLP 的一层隐藏单元和输出为

\[
z_j=\sigma\!\left(\sum_{i=1}^{n}w_{ji}x_i+b_j\right),\qquad
y_k=\sigma\!\left(\sum_{j=1}^{m}v_{kj}z_j+c_k\right).
\]

它在本文中近似固定 \(4\times4\) PV 阵列的静态端口映射。训练误差使用

\[
\mathrm{MSELoss}=\frac1n\sum_{i=1}^n(\hat y_i-y_i)^2.
\]

MSE 很小只说明给定数据分布上的均方误差小，不自动保证拓扑变化、闭环稳定性或长时递归误差小。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Eqs. (8)–(9)）

量化采用仿射映射的一般形式：

\[
Q(x)=\operatorname{round}\!\left(\frac{x}{\Delta}\right)+Z,
\]

GRU 的 dynamic quantization 在运行时确定 activation 的 \(\Delta_{\mathrm{dynamic}}\) 与 \(Z_{\mathrm{dynamic}}\)，MLP 的 static quantization 则预先固定 \(\Delta_{\mathrm{static}}\) 与 \(Z_{\mathrm{static}}\)。论文给了公式和 int8 HLS 类型，但没有给出每层实际 \(\Delta,Z\) 或定点误差传播分析。[pdf:E07]（PDF 物理页 7，Eqs. (10)–(11)）

## § 7 — 实验设计与结论

**问题 1：GRU 是否能复现未在训练中出现的 DFIG 短时暂态？**  
实验用训练时 100 ms 的三相故障作为参照，验证 80 ms 与 200 ms 故障；还测试 8→13 m/s 和 10→5 m/s 的风速阶跃。曲线显示 GRU 与传统模型在这些工况下接近。作者据此认为模型能捕捉未见暂态，但没有报告统一 test-set 指标、置信区间或长时间闭环漂移。[pdf:E05]（PDF 物理页 5，Fig. 5）

**问题 2：成组风场在不同风速下是否仍贴近传统模型？**  
180 台风机被分为三组，分别施加 8→13、15→10、10→5 m/s 的阶跃；比较 rotor speed 与 active power。论文报告阶跃附近相对误差低于 1%。这验证的是固定六机 GRU bundle 复制后的三组输入变化，不是风机数量或连接拓扑的 out-of-distribution 泛化。[pdf:E09]（PDF 物理页 9，Fig. 11、Scenario 1）

**问题 3：PV MLP 能否处理 panel-level partial shading？**  
初始所有 panel 为 1000 W/m²，1 s 时将 S1 与 S16 改为 100 和 200 W/m²。固定串并联阵列的输出从 62.5 kW 降到 31.25 kW；论文报告标准辐照时相对误差 0.2%，partial shading 时为 4%。这支持模型在同一固定拓扑内处理未见辐照组合，但误差在分布边缘明显增大。[pdf:E09]（PDF 物理页 9，Fig. 12、Scenario 2）

**问题 4：量化是否节省资源而不明显损失精度？**  
在 DFIG 8→13 m/s 验证序列上，量化模型相对 float32 原模型的最大差异点小于 0.01%；Fig. 9 还显示 DFIG 模型量化后 DSP、FF、LUT 比例下降。battery 与 PV 只被文字概括为“similar performances”，没有分别展示完整量化误差曲线。[pdf:E07]（PDF 物理页 7，Fig. 9）

**问题 5：实现是否满足实时预算？**  
Table I 的最慢 IBR 单步延迟为 15 μs，小于 50 μs IBR 步长；集成后 100 次计算共 1.5 ms，小于 5 ms 网络步长，对应等效 FTRT 3.33。证据支持一次综合实现的周期预算闭合，但未形成独立 WCET 或 deadline-miss 统计。[pdf:E06][pdf:E08]（PDF 物理页 6、8，Table I、Fig. 10）

**问题 6：ML 模型是否比传统 FPGA 模型更可扩展？**  
Fig. 13 对相同 VCU118 上的传统与 ML 模型做资源/执行时间比较。论文报告在 10 000 台风机的 benchmark 上 speed-up 超过 8193 倍；图中传统模型约 456400 μs、ML 模型约 55.7 μs。这个点本身已略高于 50 μs 的单个 EMT 步长，而且 10 000 台不是 Fig. 8 的 180 台集成 HIL 系统，所以它证明的是相对执行时间趋势，不证明 10 000 台系统仍满足本文实时 deadline。[pdf:E10]（PDF 物理页 10，Fig. 13(d)、Section IV-C）

总体上，论文对“固定模块、给定输入范围、特定 FPGA 上能较快逼近传统模型”给出了直接证据。它没有验证跨设备参数、跨 VSC controller、跨串并联拓扑或跨节点接入位置的泛化，也没有真实电网测量对照；所有主要精度真值仍来自传统计算模型。

## § 8 — Take-aways

**5 句话：**

1. 论文用 GRU 表示有明显时间依赖的 DFIG 与电池，用 MLP 表示固定 \(4\times4\) PV 阵列的静态 I-V 映射。[pdf:E04]
2. “Large-scale” 来自 30 个六机 wind bundle、20 个 PV batch、50 MW BESS 和 IEEE 118-bus 的组合，不是可变拓扑统一模型。[pdf:E06][pdf:E07]
3. 硬件是 VCU118/XCVU9P，不是 XCKU060；明确报告的是 int8 量化数据类型，完整数值位宽链仍未披露。[pdf:E06][pdf:E08]
4. 50 μs IBR 步长与 5 ms grid 步长按 100:1 同步，集成墙钟延迟 1.5 ms，对应 FTRT 3.33，但没有独立 WCET 认证。[pdf:E08]
5. 最有价值的结果是固定模块复制后的实时预算与误差曲线；最重要的未证问题是参数、拓扑和长期递归误差的域外泛化。[pdf:E09][pdf:E10]

**3 句话：**

论文展示了一条“传统模型生成数据 → GRU/MLP surrogate → int8/HLS → 多时间尺度 FPGA test bench”的完整工程链。它确实有 batched IBR module 和 118-bus 规模，却没有 topology-parameterized training 或跨拓扑/跨规模泛化。应把结果理解为固定拓扑、有限输入域内的高效替代模型，而不是通用 IBR 场站数字孪生。

**1 句话：**

这是一项固定模块批量复制的 FPGA surrogate 工程验证，而不是任意拓扑 IBR 系统的已证泛化方案。

## § 9 — 最脆弱的假设

最脆弱的假设是：**由有限传统仿真数据学到的固定模块端口映射，在批量复制并与大网络闭环交换时，仍能在所需运行域内保持物理正确且误差不累积。**

这个假设一旦失效，论文的速度优势就没有意义，因为 surrogate 可以按时给出错误电流。风险来自三层：训练分布只覆盖给定均值/方差和少数故障；GRU 把不可测内部量递归反馈，误差可能沿时间累积；PV 与 wind 的部署拓扑固定，模型没有用于辨别拓扑或设备参数变化的输入。作者自己承认模型只针对额定值附近的指定输入范围优化，outlier 会导致不准确预测，并可能受到神经网络结构的 error accumulation 影响。[pdf:E10]（PDF 物理页 10，Conclusion）

论文提供的支持证据是：未见故障持续时间、风速阶跃、panel-level partial shading 和固定系统中三组不同风速下，曲线仍接近传统模型。[pdf:E05][pdf:E09] 缺失的关键证据包括长时间闭环漂移、设备参数随机化、不同 series/parallel 拓扑、VSC 控制器状态变化、接入点变化和跨规模 hold-out。因而这项假设在论文测试域内得到有限支持，在拓扑或参数域外仍属未知。

## § 10 — 最小复现实验

一周内最小、且能真正证伪核心 claim 的实验应聚焦 PV，因为它没有递归训练负担，却能同时检查 surrogate 精度、量化和拓扑边界。

1. **数据**：实现论文引用的单二极管 \(4\times4\) PV 阵列真值模型；按 1000 W/m² 均值、300 W/m² 标准差生成训练辐照，端口电压从 0 扫到最大工作电压。保留完整随机种子和按 scenario 隔离的 train/validation/test。
2. **模型**：复现四层、每层 64 hidden units 的 MLP，输入 16 个 irradiance 加 \(V_t\)，输出 \(I_{out}\)；再做 int8 static quantization。
3. **同拓扑测试**：复现 S1=100 W/m²、S16=200 W/m² 的 partial shading，并加入未见连续辐照轨迹。测 \(I\)-\(V\)、\(P\)-\(V\)、最大相对功率误差和波形相位/趋势。
4. **反事实测试**：在不重训的情况下，把同一批 panel 改成不同 series/parallel 连接，或改变 panel 参数离散度；测试固定模型是否仍有效。
5. **硬件**：在 XCKU060 上综合量化模型，报告 post-route 频率、DSP/BRAM/LUT/FF、单次 inference latency 和 50 μs deadline margin。这个器件测试是面向后续目标的迁移，不是对论文 VCU118/XCVU9P 数字的直接复现。

本卡建议的验收标准是：同拓扑 partial shading 误差不高于论文报告的 4%，且 XCKU060 上 inference latency 小于 50 μs，可视为支持“固定模块可实时替代”；若同拓扑测试已明显失败，或仅改变拓扑就出现超过 10% 的功率误差/错误曲线形状，而真值模型正常，则反驳其可迁移性。10% 是复现实验的预注册攻击阈值，不是论文原有阈值。[pdf:E06][pdf:E09]

## § 11 — 最强反例设计

最强反例不是再给一个更极端的辐照值，而是构造 **观测输入相同、正确输出却因未建模拓扑而不同** 的两套 PV 场站。让两套系统具有相同的 16 个 irradiance、相同端口电压 \(V_t\) 和相同 panel 参数，但采用不同 series/parallel wiring，或让相同 PV block 接入具有不同 DC-link/controller state 的 VSC。论文 MLP 只看到 irradiance 与 \(V_t\)，没有 topology descriptor 或 VSC 内部状态，因此必须对两套系统给出同一个 \(I_{out}\)；传统电路模型则一般会给出不同电流。这个反例从可辨识性上说明：固定输入向量无法表达拓扑引起的一对多映射。

对论文自身应公平限定：作者没有声称跨拓扑泛化，所以该反例不会推翻“同一 \(4\times4\) 拓扑内拟合有效”这一窄结论；它会推翻把本文 batched 模块外推成“任意同构 PV VSC 场站可复用模型”的解释。进一步的闭环攻击是在弱网、限流切换或保护动作下运行长时序，让 GRU/MLP 误差改变 VSC 控制状态，再观察错误是否被网络反馈放大。论文只展示短场景和传统模型曲线对照，没有覆盖这种 hybrid-event feedback。[pdf:E04][pdf:E09][pdf:E10]

## § 12 — Follow-up Research Idea

电力电子与实时仿真领域通常不会只凭平均预测误差评价高影响工作；更关键的是物理边界是否清楚、闭环是否稳定、实时 deadline 是否可证明、硬件资源是否可复现，以及方法能否处理真正决定工程复用成本的参数与拓扑变化。基于这一标准，一个与“同构光伏 VSC 场站 + XCKU060，拓扑参数化训练、拓扑冻结静态调度部署”直接相关的候选方向是：

**候选方向：拓扑条件化训练、部署期特化的同构 PV-VSC 场站 surrogate compiler。**

它不再把目标定义为“训练一个固定 \(4\times4\) 阵列并批量复制”，而是训练一个以组件参数、VSC controller 参数、线路阻抗和 topology descriptor 为条件的 family model。部署时给定某个实际场站拓扑，将 descriptor 冻结，做 constant folding、剪枝和静态 schedule 生成，再映射到 XCKU060；运行时不再支付通用拓扑分支的代价，并可为该冻结拓扑给出确定 latency/resource budget。

**(a) 未满足需求。** 同构设备并不意味着场站行为只由单机模型决定；series/parallel 连接、汇集线路、VSC 控制、停机单元和接入阻抗会改变端口映射。为每个拓扑从零采数和训练，无法支撑快速工程部署。

**(b) 潜在研究价值。** 如果一个 family model 能对未见拓扑保持 EMT 精度，并在冻结后得到比通用模型更低且可证明的 XCKU060 latency，它同时解决“模型复用”和“确定性部署”两个工程瓶颈。高价值证据必须包括 cross-topology hold-out、弱网/故障闭环、资源-精度前沿和长时间 deadline-miss=0 的板上测试，而不只是平均 MSE。

**(c) 可借鉴工具。** 可借鉴 graph neural operator 或 message passing 表示电气连接，用 differentiable simulator/domain randomization 覆盖组件参数，再借鉴 compiler partial evaluation 与 high-level synthesis 的 static scheduling，把训练时的通用图在部署时专化成固定数据流。这里是方法候选，不代表这些组合尚无已有工作。

**(d) 第一个证伪实验。** 在训练中保留多种 topology/parameter 组合，但完整 hold out 一种汇集拓扑；比较 topology-conditioned family model、本文式固定 block MLP 和每拓扑单独训练模型。若 family model 在 hold-out 拓扑上不能显著优于固定 block，或冻结后仍无法在 XCKU060 上满足 50 μs deadline/资源预算，方向即被首轮证伪。

**(e) 与本文的实质区别。** 本文把固定六机、\(3\times4\) 电池和 \(4\times4\) PV 模块复制后接入固定 test bench；候选方向把“跨拓扑可复用、部署时冻结并生成静态调度”本身设为学习与编译目标。它研究的是模型族到硬件实例的特化过程，而不是给固定模型再加一层网络。

这一方向与论文之间存在清楚的证据起点：论文已经证明 batched surrogate、int8 HLS 和多时间尺度同步可在 XCVU9P 上闭合，但没有 topology-parameterized training、XCKU060 实现或拓扑冻结调度证据。[pdf:E06][pdf:E08] 由于本卡没有完成该方向的系统相关工作检索，**不声称 novelty**。
