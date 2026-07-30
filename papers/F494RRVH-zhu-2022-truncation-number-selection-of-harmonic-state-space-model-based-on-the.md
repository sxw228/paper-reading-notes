# Truncation Number Selection of Harmonic State-Space Model Based on the Floquet Characteristic Exponent

作者：Jianhang Zhu；Zeren Guo；Jiabing Hu；Shicong Ma；Jianbo Guo  
出处：IEEE Transactions on Industrial Electronics  
年份：2022  
DOI：10.1109/TIE.2022.3172780  
Zotero key：F494RRVH  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体、却会直接改变稳定性判断的问题：Harmonic State-Space（HSS）模型在理论上是双无限维的，实际计算必须截断；截断数 \(M\) 决定最多保留到第几次谐波，也把一个含 \(n\) 个状态的系统变成 \((2M+1)n\) 阶模型。\(M\) 太小会漏掉决定稳定性的频率耦合，太大则增加特征值计算和模态分析成本。论文的核心 claim 是：应以原 Linear Time-Periodic（LTP）模型的 Floquet Characteristic Exponent（FCE）为物理参照，逐步增加 HSS 截断数，直到 HSS 的可信特征值同时复现目标 FCE 的阻尼与振荡频率，而不是凭频谱经验或凭特征值图上“显眼的竖线”选 \(M\)。PDF 物理页 1 的 Abstract、Introduction 与 Fig. 1 给出 HSS 的来源和双无限维问题；物理页 2 进一步给出 \(M\) 的含义和 \((2M+1)n\) 阶关系。[pdf:E01] [pdf:E02]

工程上，这个问题重要，是因为 MMC、非平衡电网下的新能源变流器等系统具有周期时变和跨频耦合；截断选择一旦错误，结果不只是“精度差一点”，还可能把不稳定模态漏掉，或者把一个没有正确物理频率的特征值当作稳定性依据。作者最后用 PLL、grid current control（GCC）和 circulating current suppressing control（CCSC）三种失稳机制展示：同一个 MMC 系统里，合适的 \(M\) 会随失稳机制从 2 变到 6。[pdf:E01] [pdf:E04] [pdf:E05] [pdf:E06]

## § 2 — 前人工作与不足

论文把前人路线分成三类。第一类根据截断 HSS 特征值在复平面形成的明显竖线来选阶，并通常把中心位置的 significant eigenvalues 当作系统模态；问题是竖线清楚不等于中心特征值就同时给对阻尼和振荡频率，而且这种做法可能保留过高阶模型。第二类根据状态变量频谱只保留主要频率分量，工程上直观，但高度依赖研究者经验，缺少统一理论判据。第三类用 \(L_1\)-norm 定义截断规则，具有形式化指标，却缺少直接的物理解释，并可能对特定振荡问题给出保守截断数。上述比较由 Introduction 明确陈述，分别对应文献 [8]、[9]、[10]。[pdf:E02]

更广的背景是，既有 HSS/LTP 工作已经能够描述单相并网变流器、非平衡工况、MMC 内部谐波与阻抗稳定性，因而这里不是重新发明 HSS，而是在“模型已经会建”的前提下解决“保留多少谐波才足以支持可信稳定性判断”。论文引用的相关建模和稳定性工作列于物理页 7 的 References [1]–[8]；但本文没有重新实现这些 baseline，也没有给出与 \(L_1\)-norm 方法的统一算力或误差对比。[pdf:E07]

## § 3 — 重建作者的思考路径

下面是基于论文背景与论证顺序的重建，不是作者逐字陈述。

第一步，从稳定性分析真正关心的量出发：特征值实部代表阻尼和稳定性，虚部代表振荡频率。第二步，观察到截断 HSS 会同时出现 credible、significant 与 spurious eigenvalues；几何上“像模态”的点不一定在物理上正确。第三步，回到 HSS 的母模型 LTP：HSS 是 LTP 经 Fourier series 与 harmonic balance 后的近似，而 LTP 本身没有 HSS 截断这一步。第四步，利用 Floquet-Lyapunov 理论把一个周期 LTP 系统在周期变换下关联到常系数矩阵 \(Q\)，其特征值 FCE 正好仍以实部和虚部表达阻尼与频率。于是，一个自然的判据出现了：把 FCE 当作参照，增加 \(M\)，直到截断 HSS 的可信特征值在阻尼和频率两维都与它一致。[pdf:E01] [pdf:E02] [pdf:E03]

这里还有一个必须处理的障碍：矩阵对数只给出 FCE 虚部的一个 Floquet branch，实际振荡频率与它相差整数倍基频 \(k f_0\)。作者因此没有只做纯特征值匹配，而是引入失稳条件下的 nonlinear time-domain simulation 来识别实际振荡频率、间接确定 \(k\)，再更新目标 FCE 的虚部。这一步把“数学上等价的频率支路”变成了“当前失稳现象对应的物理频率”。[pdf:E03]

## § 4 — 核心 Intuition

HSS 截断数不应由模型自身的谱形状自我证明，而应由未做 HSS 截断的 LTP/Floquet 描述来校准。FCE 给出目标模态的阻尼，time-domain oscillation 补上 Floquet 频率支路；当截断 HSS 首次同时复现这两者时，再加谐波只会增加模型规模，而不再改变当前目标模态的物理解释。[pdf:E03]

## § 5 — 具体方法与完整 Pipeline

论文方法的输入是同一周期运行点附近的 LTP 模型、由它构造的不同截断数 HSS 模型，以及能够在目标失稳参数下运行的 nonlinear time-domain model；输出是针对该失稳模态的最小合适截断数，以及随后可用于 participation factor analysis 的 HSS 模型。Fig. 3 将流程画成三步。[pdf:E03]

1. **从 LTP 得到 FCE。** 数值计算一个周期的 state transition matrix \(\Phi(T,0)\)，再由 \(Q=\ln(\Phi(T,0))/T\) 得到常系数矩阵，\(Q\) 的特征值就是 FCE。论文把 \(\Phi(T,0)\) 的具体数值计算过程指向文献 [12]，本文没有展开求解器、步长或误差控制。[pdf:E03]
2. **为不稳定 FCE 选择物理频率支路。** 将 nonlinear model 参数设为相同失稳工况，从时域响应提取实际振荡频率，利用它确定整数 \(k\)，从而更新 FCE 虚部。实部继续作为阻尼参照。[pdf:E03]
3. **逐阶增加 HSS 截断数。** 从较小 \(M\) 开始计算 \(\operatorname{eig}(A_{\mathrm{hss},M}-N_{\mathrm{hss},M})\)，寻找与更新后 FCE 对应的 credible eigenvalue；若实部和虚部的偏差都小于给定计算容差 \(\delta\)，论文示例取 \(\delta=10^{-3}\)，就停止增加 \(M\)。随后在这个 HSS 模型上做 modal participation factor analysis。[pdf:E02] [pdf:E03]

以 CCSC 失稳为例：LTP 在 \(f_i^\Sigma=200\ \mathrm{Hz}\) 时给出不稳定 FCE \(4.015604553\pm0i\)；RT-LAB 时域与 FFT 显示新的 \(150\ \mathrm{Hz}\) 振荡，所以 \(k=3\)，目标更新为 \(4.015604553\pm942.4777961i\)。\(M=3\) 时只有实部吻合，直到 \(M=6\) 才首次有一对可信特征值的实部和虚部都在 \(10^{-3}\) 内，因此选 \(M=6\)。[pdf:E06]

领域实现边界需要说清：论文给出了 MMC grid-tied system 的 GCC、CCSC、PLL 控制框图，并在 Case 1 报告 RT-LAB OP5600、2 个 Intel i7 6-Core 3.3 GHz CPU；但没有报告开关级事件处理、离散时间推进、multi-rate 调度、并行任务划分、实时步长、定点或浮点数值表示、FPGA 映射、逻辑资源、时序收敛或 FPGA 在环执行。因此，这是一篇截断判据与稳定性分析论文，不是 FPGA real-time implementation 论文。[pdf:E03] [pdf:E04]

## § 6 — 核心数学推导（无形式化数学则跳过）

一般 LTP 小信号模型写成

\[
\dot{x}(t)=A(t)x(t)+B(t)u(t),\qquad A(t)=A(t+T),
\]

其中 \(x(t)\in\mathbb{R}^n\)、\(u(t)\in\mathbb{R}^p\)，而 \(A(t)\)、\(B(t)\) 分别是周期性的 \(n\times n\)、\(n\times p\) 矩阵。其解由 state transition matrix \(\Phi\) 表示；论文在 Eq. (1)–(3) 给出模型、周期条件和受迫响应。[pdf:E02]

Floquet-Lyapunov 理论的关键是：同一个 homogeneous LTP system 的基础解在相隔一个周期后只差一个常矩阵指数，因此

\[
\Phi(t+T,t_0)=\Phi(t,t_0)e^{QT}.
\]

定义周期矩阵

\[
P(t,t_0)=\Phi(t,t_0)e^{-Q(t-t_0)},
\]

并作基变换 \(x(t)=P(t,t_0)\bar{x}(t)\)。对两边求导，再用

\[
\dot{P}(t,t_0)=A(t)P(t,t_0)-P(t,t_0)Q
\]

消去周期项，得到

\[
\dot{\bar{x}}(t)
=P^{-1}(t,t_0)\bigl(A(t)P(t,t_0)-\dot{P}(t,t_0)\bigr)\bar{x}(t)
=Q\bar{x}(t).
\]

也就是说，周期变换把 LTP homogeneous dynamics 映射成常系数 LTI dynamics；物理直觉是 \(P\) 承担“随周期摆动的坐标系”，\(Q\) 留下跨周期累积的增长、衰减与旋转。Eq. (4)–(8) 给出这一步完整推导。[pdf:E02] [pdf:E03]

常系数系统有 \(\bar{x}(t)=e^{Q(t-t_0)}\bar{x}(t_0)\)，代回原坐标可得

\[
\Phi(t,t_0)=P(t,t_0)e^{Q(t-t_0)}.
\]

取 \(t=T,t_0=0\)，利用 \(P(T,0)=P(0,0)=I\)，得到本文实际计算的关系

\[
Q=\frac{\ln\!\bigl(\Phi(T,0)\bigr)}{T}.
\]

\(Q\) 的 eigenvalues 即 FCE；实部是周期系统每单位时间的指数增长或衰减率，虚部是旋转频率的一个等价支路。论文指出，由 matrix logarithm 的 branch 性质，FCE 虚部被限制在 \([-\pi f_0,\pi f_0]\)，而实际振荡频率可能相差 \(k f_0\)，\(f_0=1/T\)，所以必须借助失稳时域响应确定整数 \(k\)。Eq. (9)–(12) 及其后正文给出这些关系。[pdf:E03]

截断 HSS 一侧，\(M\) 表示保留 \(0,\pm1,\ldots,\pm M\) 次谐波，系统阶数为 \((2M+1)n\)；其稳定性矩阵为 \(A_{\mathrm{hss},M}-N_{\mathrm{hss},M}\)，其中 \(N_{\mathrm{hss},M}\) 是按 \(-Mj\omega_0,\ldots,Mj\omega_0\) 排列的频移对角块。论文没有推导误差随 \(M\) 的上界，而是用与更新 FCE 的数值一致性作为停止规则。[pdf:E02] [pdf:E03]

## § 7 — 实验设计与结论

**问题 1：方法能否在 PLL 参数诱发的失稳中找到足够而不过量的 \(M\)？** 作者令 \(\zeta_{\mathrm{pll}}=0.707\)，扫描 \(f_{\mathrm{pll}}=1\)–\(30\ \mathrm{Hz}\)，报告稳定范围为 \(1\)–\(23.5\ \mathrm{Hz}\)。在 \(24.5\ \mathrm{Hz}\) 工况，FCE 为 \(3.92730877\pm25.54790924i\)，其初始频率为 \(4.066076041\ \mathrm{Hz}\)；RT-LAB 波形在 \(2.5\)–\(3\ \mathrm{s}\) 内约有 27 个周期，对应约 \(54\ \mathrm{Hz}\)，故取 \(k=1\)，更新为 \(3.92730877\pm339.7071746i\)。HSS 在 \(M<2\) 时没有对应可信特征值，\(M=2\) 时首次使实、虚部偏差均小于 \(10^{-3}\)，答案是 \(M=2\)。[pdf:E04]

**问题 2：同样规则能否迁移到 GCC 失稳？** 作者令 \(\zeta_i^\Delta=0.707\)，扫描 \(f_i^\Delta=50\)–\(250\ \mathrm{Hz}\)，报告稳定范围为 \(124\)–\(250\ \mathrm{Hz}\)。在 \(115\ \mathrm{Hz}\) 工况，FCE 为 \(4.080103156\pm153.6535296i\)；RT-LAB 波形在 \(3\)–\(3.4\ \mathrm{s}\) 内约有 29.75 个周期，即约 \(74.375\ \mathrm{Hz}\)，所以 \(k=1\)，更新为 \(4.080103156\pm467.812795i\)。HSS 仍在 \(M=2\) 首次出现匹配的可信特征值，答案也是 \(M=2\)。[pdf:E05]

**问题 3：方法能否识别需要显著更高阶谐波的失稳？** 作者令 CCSC damping 为 0.707，扫描 \(f_i^\Sigma=50\)–\(250\ \mathrm{Hz}\)，报告稳定范围为 \(50\)–\(142\ \mathrm{Hz}\)。在 \(200\ \mathrm{Hz}\) 工况，FCE 为 \(4.015604553\pm0i\)，时域 FFT 在失稳阶段新出现 \(150\ \mathrm{Hz}\) 分量，因此 \(k=3\)，更新虚部为 \(\pm942.4777961\)。\(M=3\) 时有一个可信特征值只匹配实部，\(M=6\) 才同时匹配实、虚部，答案是 \(M=6\)。这组结果还显示，稳态值仅 \(0.644\ \mathrm{A}\)、约为直流分量 \(0.02\%\) 的第四次 circulating-current harmonic，仍可能对动态稳定性有关键影响；因此按稳态幅值删掉“小谐波”并不可靠。[pdf:E05] [pdf:E06]

**问题 4：传统 significant-eigenvalue 规则会不会偶然正确、但并不普遍可靠？** Discussion 比较了 Case 1 的 \(M=3\) 与 Case 3 的 \(M=7\)：前者中心 significant eigenvalues 可以与更新 FCE 重合，后者却不重合。答案是这种旧规则在部分工况可用，但不能作为跨失稳机制的统一判据。[pdf:E06] [pdf:E07]

实验边界也很明确：三组验证都来自同一类 MMC grid-tied system，系统参数和详细 LTP/HSS 推导分别外引到 [14]、[12]、[7]；本文没有报告其他 converter topology、参数不确定性、measurement noise、stable-mode 全谱误差、实时步长、资源占用或 FPGA 结果。因此实验支持“在这三个不稳定 MMC 控制案例中，FCE 匹配能纠正过低截断和错误 significant mode”，不能外推成对所有 LTP 系统的完整误差保证。[pdf:E04] [pdf:E07]

## § 8 — Take-aways

**5 句话。**  
1. HSS 截断数是一个稳定性保真度选择，不只是矩阵规模选择。  
2. FCE 提供了独立于 HSS 截断的阻尼与频率参照。  
3. matrix logarithm 的频率 branch 必须用失稳时域响应确定 \(k\) 后才能与 HSS 比较。  
4. 同一 MMC 的 PLL/GCC 案例需要 \(M=2\)，CCSC 案例却需要 \(M=6\)，说明截断数依赖目标失稳机制。[pdf:E04] [pdf:E05] [pdf:E06]  
5. 小稳态谐波不等于小动态作用，单看频谱幅值或中心 significant eigenvalue 都可能误判。[pdf:E06] [pdf:E07]

**3 句话。**  
把 LTP/Floquet 结果当外部标尺，逐阶增加 HSS，直到可信特征值的实部和虚部都吻合。用 nonlinear time-domain oscillation 解决 FCE 虚部的整数倍基频歧义。该方法在三个 MMC 失稳案例中有效，但尚不是带误差上界、覆盖稳定模态与跨拓扑的通用模型降阶理论。[pdf:E03] [pdf:E04] [pdf:E05] [pdf:E06]

**1 句话。**  
不要问“HSS 的谱图看起来够不够完整”，而要问“它是否已经复现未截断 LTP 系统中目标模态的真实阻尼和频率”。[pdf:E02] [pdf:E03]

## § 9 — 最脆弱的假设

最脆弱的假设是：**存在一个可被 nonlinear time-domain response 清楚识别的目标不稳定振荡，而且它与待匹配 FCE/HSS credible eigenvalue 是同一个物理模态。** 这是 Step 2 能确定 \(k\)、Step 3 能定义“正确虚部”的前提。如果多个不稳定模态同时增长、非线性饱和改变主导频率、噪声或短观察窗让频率不可分，时域主峰可能对应另一个模态；此时即使 HSS 特征值与“更新后 FCE”数值吻合，也可能只是匹配了错误目标。

论文为该假设提供的证据，是 PLL、GCC、CCSC 三个案例里正实部 FCE 与 RT-LAB 发散响应一致，且能从周期计数或 FFT 得到 54、74.375、150 Hz 后完成匹配。[pdf:E04] [pdf:E05] [pdf:E06] 但它缺少多模态同时失稳、弱阻尼稳定模态、噪声与有限窗口敏感性、matrix-log branch 接近边界时的鲁棒性测试。作者自己也明确指出：对于 stable FCE，目前只能用实部选择截断数，仍需更深入研究；这说明完整的稳定模态频率判据尚未闭合。[pdf:E03]

## § 10 — 最小复现实验

一周内最值得做的不是复刻整套 MMC，因为本文把系统参数和 LTP/HSS 详细推导外引，源 PDF 本身不足以无歧义重建其模型。[pdf:E04] 可以做一个**可控的二状态 LTP 最小复现**，直接检验核心判据。

数据方面，构造周期 \(T=20\ \mathrm{ms}\) 的二状态 \(A(t)\)，让其包含可开关的二次与六次谐波耦合，并通过已知周期相似变换生成 ground-truth \(Q\)。实现三条链：数值积分一周期得到 \(\Phi(T,0)\) 并计算 FCE；独立时域仿真提取增长率和振荡频率；由同一 \(A(t)\) 构造 \(M=0\)–8 的 HSS 并计算 credible eigenvalues。测量四项：FCE 与 ground truth 的误差、时域识别出的 \(k\)、每个 \(M\) 的最近可信特征值复数距离、以及该 HSS 对扰动增长率和频率的预测误差。

支持核心 claim 的结果是：以 \(10^{-3}\) 为阈值时，FCE 规则选出的最小 \(M\) 恰好也是增长率与频率预测开始稳定的最小 \(M\)，并且打开六次谐波耦合后所需 \(M\) 明显提高。反驳结果是：某个 \(M\) 已与更新 FCE 数值吻合，但时域增长率或频率仍明显错误；或者“最小合适 \(M\)”随积分步长、观察变量或频率窗口大幅漂移。这个实验复现的是论文的判据逻辑，不复现论文报告的 MMC 数字。

## § 11 — 最强反例设计

最强反例是构造一个**两个 Floquet branch 同时接近失稳、且观测量对两者可见度不同的非正规 LTP 系统**。令两个模态的虚部相差整数倍 \(f_0\)，实部都略为正；再让短时响应由瞬态放大较强、但渐近增长率较小的模态主导。对不同状态变量或不同观察窗做 FFT，可能得到不同“实际振荡频率”，于是 Step 2 会为同一 FCE 选择不同 \(k\)，Step 3 也会输出不同 \(M\)。

攻击判据不是“方法在噪声下会变差”这一泛泛说法，而是同时检验三个可证伪后果：一是时域主峰与最大实部 FCE 的模态身份是否一致；二是按该主峰更新后，HSS 数值匹配是否真的预测长期增长率；三是换观察变量后截断数是否保持不变。如果这些条件中任一个系统性失败，就说明单一时域频率不足以把 Floquet branch、物理模态和 HSS credible eigenvalue 唯一对应。该反例直接瞄准论文仅用三个单主导失稳案例支持的核心假设。[pdf:E04] [pdf:E05] [pdf:E06]

## § 12 — Follow-up Research Idea

电力电子与控制领域的高影响工作通常不仅要求一个新判据，还要求严格的稳定性解释、跨拓扑和工况验证、数值鲁棒性，以及可在真实控制/实时仿真平台上执行的证据。基于第 9 节局限，一个非增量的候选方向是把问题从“为一个已知不稳定振荡选 \(M\)”改写为：**为指定频带和全部关键 Floquet modes 生成带后验误差证书的 HSS model reduction**。这不是给现有流程再加一个模块，而是把输出从单个整数 \(M\) 改成“哪些 harmonic blocks 必须保留，以及这些块对稳定裕度、频率和参与因子的误差上界”。

未满足的需求是：stable mode 没有可用的发散时域波形来确定 branch，多模态系统也没有唯一主频；工程上却仍需在真正失稳前保证模型可信。可借鉴相邻领域的 pseudospectrum、resolvent analysis、balanced truncation 和 a posteriori residual bound，把 monodromy operator 的谱、模态可观测性和 HSS 截断残差联合起来。首个证伪实验应使用一个含 branch ambiguity、非正规瞬态放大和弱稳模态的 LTP benchmark：在不调用失稳时域主峰的前提下，证书必须提前预测每个候选 HSS 对稳定裕度、频率响应和 participation factor 的真实误差；若证书频繁漏报，或者为了可靠只能保留近乎完整的高阶 HSS，这个方向就失败。

它与本文的实质区别是：本文用一个更新后的不稳定 FCE 做点匹配并以 \(10^{-3}\) 数值偏差停止，[pdf:E03] 而候选方法追求多模态、频带级、可验证的误差控制，并把稳定工况纳入同一规则。由于本任务严格 PDF-only，未额外检索 2022 年之后相关工作；因此这里明确是候选研究想法，不声称 novelty。
