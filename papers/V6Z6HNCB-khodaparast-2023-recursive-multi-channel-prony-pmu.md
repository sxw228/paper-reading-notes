# Recursive Multi-Channel Prony for PMU

作者：Jalal Khodaparast；Olav Bjarte Fosso；Marta Molinas  
出处：IEEE Transactions on Power Delivery, Vol. 39, No. 2, April 2024（online publication：2023）  
年份：2023  
DOI：10.1109/TPWRD.2023.3335999  
Zotero key：V6Z6HNCB  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“Prony 能否估计相量”，而是一个更具体的工程冲突：单通道 Prony 能跟随频率变化，却会因测量噪声而显著失准；多通道 Prony（Multi-Channel Prony, MCP）能汇集多个测量通道提高精度，但广义 MCP 需要处理随通道数和数据窗扩大的矩阵，计算代价妨碍实时 PMU 应用。作者因此研究：能否把 MCP 改写成逐样本递推算法，在保留多通道抗噪能力的同时避免每帧求解大矩阵，并进一步改善阶跃暂态和调制带宽。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，是因为 PMU 的相量估计位于 wide-area monitoring, protection and control（WAMPAC）的测量入口。幅值、相角、频率和 ROCOF 的偏差会直接进入监视、控制或保护逻辑；与此同时，新能源和电力电子接口增多使动态现象更复杂，估计器既要适应非标称频率，又要在噪声和动态条件下满足 IEEE C37.118.1 的误差与响应要求。论文把价值落在两个可检验指标上：Total Vector Error（TVE，复相量估计误差）和 FLOPs（浮点运算次数），并以合成信号、IEEE 39-bus、离线实测数据及在线 NI/LabVIEW 实验覆盖“准确性—计算量—实时性”三条证据链。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E09]（PDF 物理页 9，Section V-G，Figs. 12–14）[pdf:E12]（PDF 物理页 12，Table IV 与 Section VI）

## § 2 — 前人工作与不足

论文的相关工作脉络可分成三层。第一层是常规相量估计器：DFT、FIR/flat-top filter、matrix pencil、nonlinear least squares 以及 Kalman 类方法分别处理谐波、带外干扰、衰减直流或动态相量；Prony 的特殊优势是把频率作为待估参数，因此对时变或非标称频率更自然。第二层是 MCP：data fusion、ADMM、consensus/sub-gradient 等方法用多通道抵抗噪声，但广义 MCP 的大矩阵和若干方案的迭代求解带来较高计算负担。第三层是 recursive Prony：已有递推方案用于模态、趋势或振荡辨识，但只递推单个信号，没有把多通道融合与递推计算统一起来。[pdf:E01]（PDF 物理页 1，Section I）

作者据此指出的缺口是：先前工作通常只解决“频率自适应”“多通道抗噪”或“递推降计算量”中的一部分，缺少同时满足三者并面向 PMU 标准测试的方案。本刊版本相对其 2018 年会议工作还增加 FLOPs 分析、adaptive forgetting factor、adaptive root placement、六类方法比较、IEEE 39-bus 测试和两组实测数据。[pdf:E02]（PDF 物理页 2，Section I 的 contributions）

这里需要区分证据强度：上述 prior-work 能力和不足是论文作者对文献的归纳，本次 PDF-only 阅读没有独立打开被引论文复核，因此不能把“所有既有 MCP 都不够实时”提升为经独立系统综述确认的结论。

## § 3 — 重建作者的思考路径

以下是基于论文背景和失败模式的合理重建，不是作者逐字陈述。第一步，研究者会保留 Prony 的指数模型，因为根的位置同时编码阻尼与频率，天然适合 off-nominal frequency；但噪声会扰动多项式系数和根，使单通道估计越过 TVE 限值。第二步，会想到对同一电压或电流取得多个同步观测，并按各通道噪声方差加权，从而让高质量通道贡献更大、受污染通道贡献更小。第三步，若直接在每个数据窗上重做 generalized MCP，矩阵运算随通道数快速增加，故应把“整窗重算”改成“上一估计 + 当前新样本”的递推最小二乘更新。[pdf:E01]（PDF 物理页 1，Section I）[pdf:E03]（PDF 物理页 3，Eq. (10)–(14) 与 Algorithm 1）

递推又引入新的矛盾：较小 forgetting factor 能更快忘记旧状态、缩短阶跃后的 settling time，却会增加 TVE 或 overshoot；在幅相调制时，估计根还会偏离理想单位圆。由此自然得到两种按工况切换的修正：暂态时调节 forgetting factor，功率摆动/调制时根据 ROCOF 判断并把根约束回单位圆。这个思考路径把方法理解为“带工况检测的两级递推估计”，而不是单纯把一个 batch least-squares 公式换成 RLS。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Adaptive Forgetting Factor）[pdf:E04]（PDF 物理页 4，Figs. 2–4）

## § 4 — 核心 Intuition

同一个物理相量由多个通道重复观测时，噪声更小的通道应有更大权重，而每到一个新样本只需修正上一时刻的多项式系数和相量，无须重算整个数据窗。递推带来的“记忆”既是速度来源，也是暂态迟缓和误差传播来源，所以作者再用自适应 forgetting factor 控制记忆长度，并在调制状态下约束 Prony 根的位置。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14)）[pdf:E04]（PDF 物理页 4，Fig. 4）

## § 5 — 具体方法与完整 Pipeline

以四个 PMU 通道同时测量同一 50 Hz 电压为例，完整 pipeline 如下。

1. **输入与权重。** 在采样时刻 \(n\)，输入四个同步样本 \(y_1(n),\ldots,y_4(n)\)。论文用对角噪声矩阵 \(R=\mathrm{diag}(\delta_1^2,\ldots,\delta_M^2)\) 表示各通道噪声方差；方差小的通道在增益计算中权重更高。论文的四通道合成例设 \(M_1=1\)、阻尼 \(\alpha=0.05\)、\(f_1=50\) Hz、相角为 0，四个噪声方差依次为 \(10^{-4},10^{-5},10^{-6},10^{-7}\)，采样率 1 kHz、报告率 100 fps。[pdf:E03]（PDF 物理页 3，Eq. (10)）[pdf:E06]（PDF 物理页 6，Eq. (16)）
2. **第一级递推：更新特征多项式。** 用当前回归向量 \(u(n)\)、上一协方差 \(P_1(n-1)\)、forgetting factor \(\lambda_1\) 和 \(R\) 计算增益，再由预测残差更新系数向量 \(A\) 和 \(P_1\)。这一级代替整窗求解 \(A=(Q^TQ)^{-1}Q^TY\)。[pdf:E02]（PDF 物理页 2，Eq. (7)–(9)）[pdf:E03]（PDF 物理页 3，Algorithm 1）
3. **根求解。** 用更新后的 \(A=[a_1,a_2]^T\) 形成二阶特征多项式 \(F(z)=z^2+a_1z+a_2\)，求共轭根 \(Z_1,Z_1^*\)；根的相角给出频率信息，模长关联阻尼。[pdf:E02]（PDF 物理页 2，Eq. (7)–(9)）
4. **工况修正。** 流程图用 ROCOF 识别功率摆动/调制状态，并在该状态把根固定到单位圆；同时依据第二级估计误差调节 \(\lambda_2\)，以在稳态误差与暂态速度之间切换。论文给出的扫参范围为 \(\lambda\in\{0.2,0.3,\ldots,0.9,0.98\}\)，并显示调制频率越高、\(\lambda\) 越大时误差越高。[pdf:E03]（PDF 物理页 3，Fig. 1）[pdf:E04]（PDF 物理页 4，Figs. 2–4）
5. **第二级递推：更新相量。** 在根确定后，以同一组 RLS 关系递推相量参数 \(H\)，最后输出幅值与相角；由根同时得到频率、ROCOF 和阻尼。每个 PPS 对齐的报告帧包含 UTC、相量、频率和 ROCOF。[pdf:E03]（PDF 物理页 3，Algorithm 1）[pdf:E06]（PDF 物理页 6，Fig. 7）
6. **实际执行平台。** 在线实验由 NI-9239 与 NI-9225 采集两个电压通道，经 cRIO-9076 和 Ethernet 传到 Dell Latitude E5470 笔记本，在 LabVIEW 中运行估计；基频 50 Hz，每周期 100 个样本。[pdf:E11]（PDF 物理页 11，Fig. 17 与 Section V-H.3）

从 EMT + FPGA 视角看，本文给出了逐样本递推的数据依赖和 FLOPs，但没有报告开关事件处理、多速率 EMT 时间推进、FPGA 映射、定点位宽、DSP/BRAM/LUT 资源、pipeline initiation interval、板上 worst-case latency 或 timing closure。在线实验的计算核心明确是笔记本 CPU + LabVIEW，而不是 FPGA；因此不能把“实时 PMU 算法”外推为“已验证的 FPGA 实现”。[pdf:E11]（PDF 物理页 11，在线实验平台）

## § 6 — 核心数学推导（无形式化数学则跳过）

Prony 的起点是把实信号写成阻尼复指数之和：

\[
y(t)=\sum_{k=1}^{L}0.5M_k e^{(\alpha_k+j\omega_k)nT+j\phi_k}.
\]

对单一基波取一对共轭分量，令 \(Z_1=e^{(\alpha_1+j\omega_1)T}\)、\(h=M_1e^{j\phi_1}\)，则

\[
y(nT)=0.5hZ_1^n+0.5h^*Z_1^{*n}.
\]

直观上，\(Z_1\) 每乘一次就把信号推进一个采样点：\(\arg Z_1/T\) 对应角频率，\(\ln|Z_1|/T\) 对应阻尼；\(h\) 则承载幅值与初相角。把 \(N\) 个样本堆成矩阵后得到 \(Y=JH\)，已知根时可用 \(H=(J^TJ)^{-1}J^TY\) 求相量。[pdf:E02]（PDF 物理页 2，Eq. (1)–(6)）

根并非预先已知。共轭根满足

\[
F(z)=(z-Z_1)(z-Z_1^*)=z^2+a_1z+a_2,
\]

而移位样本满足 \(Y=QA\)，故 batch Prony 先由

\[
A=(Q^TQ)^{-1}Q^TY
\]

估计多项式系数，再求根，最后回到 \(Y=JH\) 求相量。这个“系数 \(\rightarrow\) 根 \(\rightarrow\) 相量”的顺序解释了为何 R-MCP 要做两级递推，中间保留一次求根。[pdf:E02]（PDF 物理页 2，Eq. (7)–(9)）

论文用加权 RLS 把两个 least-squares 步骤递推化。每个新样本执行

\[
k(n)=\frac{\lambda^{-1}P(n-1)u(n)}
{R+\lambda^{-1}u(n)^TP(n-1)u(n)},
\]
\[
\alpha(n)=d(n)-u(n)^Tw(n-1),
\]
\[
w(n)=w(n-1)+k(n)\alpha(n),
\]
\[
P(n)=\lambda^{-1}P(n-1)-\lambda^{-1}k(n)u(n)^TP(n-1).
\]

其中 \(R\) 是多通道噪声方差矩阵，\(\alpha(n)\) 是当前创新/预测残差，\(P(n)\) 表示参数不确定性的递推量，\(\lambda\) 决定旧信息衰减速度。第一级令 \(w=A\)，第二级令 \(w=H\)。较小 \(\lambda\) 更快忘记旧状态，因此阶跃响应更快，但论文的 Fig. 1 同时显示 TVE 增大；这就是自适应 \(\lambda\) 的数学动机。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14)、Algorithm 1、Fig. 1）

## § 7 — 实验设计与结论

- **问题：单通道 Prony 是否真的受噪声限制？** 实验把 50 Hz 阻尼正弦分别加到 50 dB 和 30 dB 白噪声中，采样率 1 kHz、窗长 20 ms、报告率 100 fps。答案是 30 dB 情形的单通道 TVE 越过 1% 稳态限值，支持引入多通道信息的必要性。[pdf:E05]（PDF 物理页 5，Eq. (15) 与 Fig. 6）
- **问题：递推化是否同时降低计算量并保持多通道精度？** 实验比较 1–4 通道 G-MCP 与 R-MCP。四通道时，G-MCP 为 4,202,708 FLOPs/estimate、TVE 0.0063%，R-MCP 为 887 FLOPs/estimate、TVE 0.0388%；递推方案精度略低于 batch 方案，但仍远低于 1% 限值，且计算量降低约三个数量级以上。[pdf:E06]（PDF 物理页 6，Table I）
- **问题：能否满足 P-class 动态测试？** 作者做 10% 幅值阶跃、10° 相角阶跃、1 Hz/s 频率 ramp 和幅相调制。幅值阶跃的 response time、delay、overshoot、frequency response time、ROCOF response time 分别为 0.00235 s、0.0005 s、4%、0.009 s、0.009 s；相角阶跃对应为 0.00195 s、0.0016 s、0%、0.008 s、0.008 s，均在论文列出的标准限值内。汇总表还报告 ramp 的 FE 为 0.0075 Hz（限值 0.01 Hz），bandwidth test 的 TVE 为 0.02%（限值 3%）。[pdf:E07]（PDF 物理页 7，Eq. (17)、Table II）[pdf:E12]（PDF 物理页 12，Table IV）
- **问题：非标称频率下是否优于 DFT/Kalman？** 四通道信号设实际频率 49.5 Hz、标称 50 Hz、噪声方差 \(10^{-4}\) 到 \(10^{-7}\)。图示中 R-MCP 的幅值和 TVE 更接近参考，论文归因于 Prony 在估计内部预测频率；Table IV 报告 off-nominal TVE 0.02%，标准限值 1%。这个结论只覆盖该单一频偏与所设噪声条件。[pdf:E08]（PDF 物理页 8，Eq. (20) 与 Fig. 11）[pdf:E12]（PDF 物理页 12，Table IV）
- **问题：在电网仿真和不同 SNR 下是否仍有效？** IEEE 39-bus 在 PSCAD 中仿真，Bus 14 配四通道 PMU，采样率 46 kHz、报告率 100 fps，四通道 SNR 为 20/30/40/50 dB。R-MCP 的 TVE 远低于 1%；SNR 从 10 dB 扫到 70 dB 时，所有方法随 SNR 降低而变差，低 SNR 区间 Kalman 和 data fusion 比 R-MCP 更准，而 R-MCP 在 off-nominal frequency 对比中优于 Kalman。说明论文没有证明 R-MCP 在所有噪声条件下精度最优，而是展示了计算量与频率自适应的折中。[pdf:E09]（PDF 物理页 9，Figs. 12–14）
- **问题：真实数据上是否可用？** 墨西哥电网离线数据含约 0.085–0.165 s 故障、60 Hz 基波和 300 Hz 五次谐波；加入两个不同方差的白噪声通道后，R-MCP 的 reconstruction Error Index（EI）为 0.0151，单通道 classical Prony 为 0.0309。Table III 中 Fourier-Kalman-Taylor 的 EI 0.0137 略优于 R-MCP，但仿真时间为 2.1978 s；R-MCP 为 0.701 s。这里没有真实相量 ground truth，EI 是“实测波形与重构波形的平均绝对差”，不能等同于 TVE。[pdf:E10]（PDF 物理页 10，Eq. (21)、Figs. 15–16、Table III）
- **问题：在线处理能否运行？** 两个 NI 模块的数据在线送入笔记本 LabVIEW；作者报告估计频率随真实系统在 50 Hz 附近变化，最大 EI 为 0.01。由 0.701 s/2,880 samples 得到每相量 0.000243 s，并与 P-class 0.033 s、M-class 0.0833 s 报告延迟限值比较。[pdf:E11]（PDF 物理页 11，Figs. 17–20）[pdf:E12]（PDF 物理页 12，Fig. 21 与 Table IV）这个 0.000243 s 是指定旧 CPU 上平均仿真时间的除法结果，不是带 I/O、调度和 worst-case jitter 的端到端硬实时测量。

Table IV 还列出 harmonic 及 sub-/inter-harmonic 的 TVE 均为 0.001%（限值 1%），但正文没有给出与这些汇总数字相匹配的完整激励、频率范围和独立小节，因此本卡只记录其“汇总表报告值”，不把它当成可复现实验已充分闭合。[pdf:E12]（PDF 物理页 12，Table IV）

## § 8 — Take-aways

**5 句话：**

1. R-MCP 用多个同步通道降低 Prony 的噪声敏感性，再用递推更新避免 generalized MCP 的大矩阵重算。[pdf:E01]（PDF 物理页 1，Abstract）
2. 方法实质是两级加权 RLS：先估计特征多项式系数并求根，再估计相量，通道噪声方差通过对角矩阵 \(R\) 进入增益。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14) 与 Algorithm 1）
3. 四通道例中，R-MCP 以 TVE 从 G-MCP 的 0.0063% 放宽到 0.0388% 为代价，把 FLOPs 从 4,202,708 降到 887。[pdf:E06]（PDF 物理页 6，Table I）
4. 合成动态测试、IEEE 39-bus、墨西哥实测数据和 NI/LabVIEW 在线实验共同支持“可用且更省计算”，但没有证明所有低 SNR 条件下精度最优。[pdf:E09]（PDF 物理页 9，Fig. 14）[pdf:E10]（PDF 物理页 10，Table III）
5. 论文没有 FPGA、定点数或端到端硬实时证据，且核心融合依赖多个同步、同量测、噪声统计可用的通道。[pdf:E02]（PDF 物理页 2，通道数量假设）[pdf:E11]（PDF 物理页 11，在线平台）

**3 句话：**

1. 这篇论文把 multi-channel Prony 从 batch 矩阵估计改成逐样本递推，并用 adaptive forgetting factor 与 root placement 修补暂态和调制性能。[pdf:E04]（PDF 物理页 4，Fig. 4）
2. 其最有力证据是四通道 FLOPs/TVE 对比和覆盖多种 PMU 工况的实验，但实时数字仍是 CPU 平均计算时间而非嵌入式 worst-case latency。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E11]（PDF 物理页 11，latency 说明）
3. 因而它适合作为低计算量 PMU estimator 的算法起点，不足以直接证明 FPGA 或现场保护级确定性实现。

**1 句话：**

R-MCP 的核心贡献是在“多通道抗噪”与“逐样本低计算量”之间建立可工作的折中，但这项折中仍建立在通道一致性和已知噪声权重之上。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14)）

## § 9 — 最脆弱的假设

失败代价最大的假设是：多个通道确实在同步测量同一个物理相量，而且它们的误差可以由已知、对角的方差矩阵 \(R\) 充分描述。若噪声主要来自共同电磁干扰、共享时钟、同一变送链路，或通道之间存在增益/相角偏差和时间偏移，那么“多一个通道”并不等于“多一份独立信息”；错误的 \(R\) 还可能让受污染通道获得过高权重，直接破坏论文最核心的抗噪增益。[pdf:E03]（PDF 物理页 3，Eq. (10)–(11)）

论文为这个假设提供的证据主要是人为设定不同方差的独立白噪声，以及两个不同 NI 模块的在线电压测量；没有报告完整协方差、时间同步误差、通道校准误差或 common-mode noise 扫描。作者还明确承认 recursive 方法会传播前一估计的误差、长期运行可能丢失相角估计，并且多个通道用于同一信号会挤占 PMU 对其他参数的测量灵活性。[pdf:E05]（PDF 物理页 5，Section IV limitations）[pdf:E11]（PDF 物理页 11，在线双通道配置）因此，现有证据说明方法在所测条件下可行，却不足以证明通道相关误差下仍稳健。

## § 10 — 最小复现实验

一周内最值得复现的是“递推化是否以很小精度代价换来数量级计算量下降”，同时顺手检验第 9 节的通道假设。

1. 依照 Eq. (16) 生成 2 s、50 Hz、1 kHz 采样的四通道阻尼正弦，噪声方差设为 \(10^{-4},10^{-5},10^{-6},10^{-7}\)；再生成一组总方差相同、但含可调 common-mode 分量的相关噪声数据。[pdf:E06]（PDF 物理页 6，Eq. (16)）
2. 实现 Eq. (10)–(14) 的两级 R-MCP，并实现同阶的 batch G-MCP 或至少 one-channel Prony 作为基线；先固定 \(\lambda\)，再加入论文 Fig. 4 的 adaptive forgetting/root-placement 逻辑。[pdf:E03]（PDF 物理页 3，Algorithm 1）[pdf:E04]（PDF 物理页 4，Fig. 4）
3. 测量每帧 TVE、settling time、每估计 FLOPs 和 wall-clock latency。独立白噪声组若能重现“四通道 R-MCP 明显优于单通道、TVE 低于 1%，且计算量远低于 G-MCP”的排序，就支持核心 claim；若做不到，则反驳论文的可复现性。论文 Table I 的 0.0388% TVE 与 887 FLOPs 可作为量级参考，但 FLOPs 会受具体实现计数规则影响，不应要求逐位相等。[pdf:E06]（PDF 物理页 6，Table I）
4. 把 common-mode noise 占比从 0 扫到 100%，并故意用对角 \(R\) 估计。若多通道增益随相关性迅速消失或 TVE 越过 1%，即可直接量化论文未覆盖的适用边界。

这个实验不需要墨西哥原始数据或 NI 硬件；论文未提供源码、随机种子和完整初始化值，复现报告应把这些实现选择显式记录为“复现者设定”，而非论文参数。

## § 11 — 最强反例设计

最强反例不是继续降低独立白噪声 SNR，而是制造“看似四个通道、实际只有一份错误信息”的条件：四通道共享一个占主导的 common-mode 扰动，其中两个通道再加入小的时间偏移，另一个通道加入稳定相角校准偏差；估计器仍使用论文的对角 \(R\)，并把这些观测当作同一个同步相量。随后施加 off-nominal frequency 与 10% 幅值阶跃，让 adaptive root placement 和 forgetting factor 同时动作。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14)）[pdf:E04]（PDF 物理页 4，Fig. 4）

这个反例直接攻击机制：对角 \(R\) 无法表达跨通道相关性和系统性偏差；单位圆约束只能限制根的模长，不能消除通道间的相角不一致；递推又会把一次错误融合带入后续估计。若此时 R-MCP 的 TVE 持续超过 one-channel 最佳通道，或者在阶跃后产生稳定偏置而仍给出表面平滑的频率轨迹，就能推翻“利用更多可用通道通常提高准确性”的宽泛表述，并把论文结论收窄到“通道同步、校准且误差近似独立”的条件。论文自己报告的长期相角丢失和误差传播使这一攻击更具针对性。[pdf:E05]（PDF 物理页 5，limitations）

## § 12 — Follow-up Research Idea

**候选研究方向：从“固定权重的多通道相量估计”改写为“带可辨识性判据的联合相量—通道误差估计”。** 这是基于本篇证据提出的候选想法；由于本次协议不联网、也未完整检索相关工作，不声称 novelty。

（a）未满足需求是：现场 PMU 的多通道可能共享时钟、变送器和电磁环境，真实误差既相关又会漂移；估计器必须知道“这些通道是否真的提供了独立信息”，而不只是无条件把所有通道纳入递推。论文当前的对角 \(R\) 和固定同量测前提没有覆盖这一点。[pdf:E03]（PDF 物理页 3，Eq. (10)）  
（b）潜在研究价值在于把输出从单一 phasor 扩展为“phasor + 通道可信度 + 当前可辨识性”，在证据不足时允许降权、隔离或拒绝给出高置信估计；这比单纯再调一个 \(\lambda\) 更接近保护与控制所需的可解释可靠性。  
（c）可借鉴 robust sensor fusion、full-covariance adaptive filtering、factor graph 和 change-point detection：联合估计相量、跨通道协方差、时间偏移与校准漂移，并用创新序列检查模型是否仍成立。  
（d）第一个证伪实验是硬件在环双源采集：分别注入独立噪声、common-mode noise、可控时间偏移和相角漂移，与原 R-MCP、最佳单通道和 full-covariance 基线比较 TVE、误报/拒绝率及 worst-case latency。若联合模型不能在相关误差下显著降低 TVE，或代价使实时预算失效，这个方向就被早期否证。  
（e）它与本文的实质区别是改变问题定义：本文假定通道可融合并追求更快的融合计算；新问题先判断通道信息是否独立且相容，再决定能否融合。它还要求端到端硬实时与定点实现证据，补上本文只在笔记本 LabVIEW 上给出平均处理时间、没有 FPGA 资源和 timing closure 的空白。[pdf:E11]（PDF 物理页 11，在线平台与 latency）[pdf:E12]（PDF 物理页 12，Table IV）
