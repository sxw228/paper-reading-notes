# High-Order Generalized Averaging Method for Power Electronics Modeling From DC to Above Half the Switching Frequency

**作者：** Hongchang Li, Kangping Wang, Jingyang Fang, Wenjie Chen, Xu Yang  
**出处：** IEEE Transactions on Power Electronics, Vol. 40, No. 1, pp. 176–194  
**年份：** 2025  
**DOI：** 10.1109/TPEL.2024.3450712 [pdf:E01]（PDF 物理页 1，题名、作者、期刊与 DOI）  
**Zotero key：** QK8IUSV2  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** 这篇论文要解决的是一个很具体的建模断层：经典 state-space averaging 把一个开关周期内的分段状态方程平均掉，因而擅长描述低频包络，却在频率接近开关频率一半时开始丢失开关纹波及 sideband coupling；而快速控制、电流模控制、谐振变换器恰恰依赖这些高频信息。作者的目标不是只为某一种拓扑补一个高频修正项，而是建立一套从 dc 一直有效到高于 \(f_s/2\) 的统一方法，并使 PWM、phase-shift modulation（PSM）、pulse-frequency modulation（PFM）和由状态决定的二极管开关都能接入同一个 circuit model。摘要同时说明验证对象是 PWM boost、\(V^2\) constant-ON-time buck 和 PFM LLC 三类变换器。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题的重要性在于：如果模型在控制带宽、采样频率或谐振附近把 sideband 当成不存在，设计者可能看错增益峰谷、相位滚降甚至次谐波稳定性。论文在引言中将这一缺口具体化为 DCM、可变开关频率、多谐振以及 state-dependent switching 等工况仍难以统一建模；提出的方法把这些工况放进 moving Fourier coefficient 的同一坐标系，而不是为每个工况另写一套波形分段推导。[pdf:E02]（PDF 物理页 2，Introduction 的问题陈述与四项贡献）

对 EMT 与 FPGA 读者需要先划清边界：本文产物是分析模型及 transfer-function matrix，不是实时 EMT 求解器。作者在引言中说 analytical model 可服务于 controller design、stability analysis 和 hardware-in-the-loop simulation，但全文没有给出 FPGA 架构、并行流水、定点字长、资源占用、时序收敛或实时步长。因此，它对 FPGA 的直接价值是提供可进一步离散化和降阶的高频耦合模型，而不是已经证明可部署的 FPGA 实现。[pdf:E05]（PDF 物理页 5，Section III 开头）

## § 2 — 前人工作与不足

论文把既有路线分成几类。state-space averaging 连续、简单，却只在远低于 \(f_s/2\) 时可靠；discrete/sampled-data model 可以进入高频，但要计算开关时刻和矩阵指数，遇到由状态轨迹隐式决定的开关时刻会变得复杂。describing function 与 harmonic balance 在理论上可到高频，但要在开关周期与调制周期的公倍周期上推 Jacobian，并依赖分段波形和开关边界假设。EDF 与传统 generalized averaging 用短周期近似长公倍周期，通常只保留 dc 和基波，因而仍受“调制频率远低于开关频率”的条件约束。multifrequency model 与 harmonic state-space（HSS）能显式表示 sideband，但在 power converter 中，状态矩阵依赖开关信号、开关信号又依赖状态，常需把闭环控制一起揉进模型；论文回顾称其应用范围主要集中在 CCM PWM 场景。[pdf:E02]（PDF 物理页 2，Introduction；相关工作结论均来自本文的文献回顾）

Table I 的对比是作者对上述差异的集中归纳：moving average 只建 dc，generalized average/EDF 常建 dc 加基波，而 proposed high-order generalized average 将 harmonic set 扩展为“all”；表中还把适用频率、是否依赖 waveform analysis、对 variable frequency 与 state-dependent switching 的支持并列比较。[pdf:E03]（PDF 物理页 3，Table I）

作者改变的关键假设不是“高频效应可以忽略”，而是反过来承认：一个开关信号的 dc、各次 harmonic 及其 sideband 必须共同进入模型。其工程代价也随之显现：数学对象是无限维的，实际求解只能截断。论文把这一代价留到结论中讨论，却没有给出“保留多少阶才足够”的定量答案。[pdf:E18]（PDF 物理页 18，Conclusion 的 limitation）

## § 3 — 重建作者的思考路径

以下是**基于论文证据的合理推断**，不是作者逐字陈述的研究日志。

第一步，从“平均模型为何在 \(f_s/2\) 附近失效”回看，问题不只是参数不准，而是表示空间不够：只保留 dc，或只保留 dc 与基波，相当于在建模前主动删除了能够搬移能量的 harmonic channels。第二步，moving Fourier coefficient 已知可以把非周期、甚至有跳变的信号写成随时间缓慢或快速变化但连续的系数；若保留全体系数，开关波形本身并没有被平均掉。[pdf:E03]（PDF 物理页 3，Section II-A，Eq. (1)–(5) 与 Fig. 1）

第三步，功率电路里的乘法项可以转化成 Fourier coefficient 的离散卷积，即 Toeplitz matrix 乘法；时间导数会多出按 harmonic index 加权的 \(jN\omega\) 项。这样，原始的 piecewise-linear state equation 可以在 harmonic coordinates 中保持结构化，而不必先猜每一段时域波形。[pdf:E04]（PDF 物理页 4，Eq. (7)–(19)）

第四步，单有 circuit model 不够，因为 PWM comparator、二极管关断和 PFM 都把状态或控制量变成 switching instant。作者于是把 Boolean switching signal 统一表示成每周期的 rising/falling instants，再求这些时刻对 moving Fourier coefficients 的敏感度。这样，circuit 与 modulator/controller 可以先分别线性化，最后拼成同一个 LTI small-signal model。[pdf:E06]（PDF 物理页 6，Section IV-A，Eq. (36)–(38)）

最后，利用 moving Fourier coefficient 的 Laplace transform，原来在物理频域中位于 \(s+jn\omega\) 的不同 sidebands，被搬到同一个基带 \(s\) 下，transfer-function matrix 的第 \((m,n)\) 个元素就直接表示第 \(n\) 个输入 sideband 到第 \(m\) 个输出 sideband 的耦合。这给“为什么 \(f_s/2\) 以上仍能建模”提供了统一解释。[pdf:E05]（PDF 物理页 5，Eq. (20)–(23)）

## § 4 — 核心 Intuition

核心 intuition 是：不要把开关纹波当成需要平均掉的噪声，而要把每个 harmonic 看成一个相互耦合的状态通道。moving Fourier coefficients 把跳变的开关波形变成可连续演化的系数，卷积和 \(jN\omega\) 结构则把电路方程搬进这些通道。再把 PWM/PFM/二极管的 rising/falling instant 对状态的敏感度接上，就能在一个 LTI 框架里同时看到基带与 sidebands，而不必逐段重建时域波形。[pdf:E04]（PDF 物理页 4，Section II-C–F）[pdf:E06]（PDF 物理页 6，Section III-D 与 IV-A）

## § 5 — 具体方法与完整 Pipeline

以论文的 PWM boost 为具体例子，输入是拓扑的 piecewise-linear state equation、输入电压与元件参数、PWM duty/carrier，以及选择保留的 harmonic indices；输出是 steady-state harmonic coefficients、重建波形和 duty-to-output transfer-function matrix。

1. **建立 circuit equation。** 对 boost，状态为电感电流 \(i_L\) 与输出电压 \(v_o\)，开关 \(S\) 与二极管 \(D\) 分别由 \(s_1,s_2\) 表示。原方程写成 Eq. (56)，再用 moving Fourier convolution 得到 large-signal Eq. (57) 与 small-signal Eq. (58)。[pdf:E08]（PDF 物理页 8，Section V-A，Eq. (56)–(58)）
2. **展开 moving Fourier channels。** 对每个信号保留 \(-K,\ldots,0,\ldots,K\) 阶系数。乘法换成 Toeplitz convolution，导数加入 \(jN\omega\) 对角项；得到的不是逐开关步进，而是一组 coupled harmonic equations。[pdf:E04]（PDF 物理页 4，Eq. (7)–(16)）
3. **独立建 switching signal。** PWM 的 \(s_1\) 上升、下降时刻是 \(d-c=0\) 的零点；Eq. (59)–(62) 把 duty perturbation 传到 switching instants，再传到各阶 \(\langle s_1\rangle_n\)。CCM 中 \(s_2=-s_1\) 的小信号互补；DCM 中二极管关断由 \(i_L=0\) 决定，要把关断时刻对 \(\langle i_L\rangle\) 的敏感度接回 circuit model。[pdf:E09]（PDF 物理页 9，Eq. (59)–(67)）
4. **解 steady state。** 给定 \(\langle v_i\rangle,\langle s_1\rangle,\langle s_2\rangle\)，求解线性平衡 Eq. (70)；DCM 还迭代二极管关断处 \(i_L(t_{f2})\to0\)。论文三组案例都以 \(-49\) 到 \(49\) 阶系数重建 steady-state waveform。[pdf:E09]（PDF 物理页 9，Eq. (68)–(70)）[pdf:E10]（PDF 物理页 10，Section V-D）
5. **局部线性化并组合。** 通用 small-signal circuit Jacobian 是 Eq. (34)，将它与 switch-timing Jacobian 线性连接，求需要的 \(H_{mn}(s)\)。若输入只含基带分量，\(H_{m0}\) 给出基带输入到第 \(m\) 个输出 sideband，\(H_{00}\) 则是通常关心的基带 transfer function。[pdf:E06]（PDF 物理页 6，Eq. (34)–(35)）[pdf:E05]（PDF 物理页 5，Eq. (20)–(23)）
6. **扩展到其他 modulation。** PSM 的开关边沿由 phase-shifted carrier 的零点给出；PFM 则令 \(\omega_s(t)=\omega+\dot\alpha(t)\)，把 switching-frequency perturbation 先积分为 phase perturbation，因此从 \(\omega_s\) 到输出的 transfer function 比从 \(\alpha\) 到输出多一个 \(1/s\)。[pdf:E08]（PDF 物理页 8，Eq. (53)–(55)）LLC 的 primary switch 用 phase input \(\alpha\)，secondary diode 则由 \(i_r-i_m=0\) 决定，Eq. (90)–(98) 给出二者的组合。[pdf:E15]（PDF 物理页 15，Eq. (90)–(98)）

**论文未报告项。** 论文没有给出稀疏求解器、矩阵规模随 \(K\) 的计算复杂度、内存量、时间推进器、multi-rate scheduling、数值条件数、定点/浮点表示、FPGA block mapping、DSP/BRAM/LUT 资源、clock frequency、latency 或 real-time step。本文的“LTI framework”是分析表示，不应外推为已经实现的 FPGA 并行执行架构。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从波形到 moving Fourier state

对 fundamental period \(T\) 与 \(\omega=2\pi/T\)，第 \(n\) 个 moving Fourier coefficient 定义为

\[
\langle x\rangle_n(\tau)=\frac{1}{T}\int_{\tau-T/2}^{\tau+T/2}x(t)e^{-jn\omega t}\,dt .
\tag{1}
\]

它不是对整段信号做一次固定 Fourier transform，而是在中心时刻 \(\tau\) 滑动一个周期窗口。保留所有 \(n\) 时，time-varying Fourier series 可在连续点重建 \(x(t)\)；即使原信号跳变，系数本身仍连续且几乎处处可微。[pdf:E03]（PDF 物理页 3，Eq. (1)–(3) 与 Fig. 1）

### 6.2 非线性乘法和时间导数的结构化形式

两个信号相乘后，第 \(n\) 阶系数是

\[
\langle xy\rangle_n=\sum_{m=-\infty}^{+\infty}\langle x\rangle_{n-m}\langle y\rangle_m ,
\tag{7}
\]

即 coefficient vectors 的离散卷积，也可写成 Toeplitz matrix \([[\!x\!]]\langle y\rangle\)。这一步把开关函数与电压、电流的乘法保留下来，而不是先平均。对导数则有

\[
\frac{d\langle x\rangle}{d\tau}=\langle \dot x\rangle-jN\omega\langle x\rangle,\qquad
N=\operatorname{diag}(\ldots,-1,0,1,\ldots).
\tag{15–16}
\]

\(jN\omega\) 的物理意义是：第 \(n\) 个 harmonic channel 自带 \(jn\omega\) 的旋转速度。[pdf:E04]（PDF 物理页 4，Eq. (7)–(16)）

### 6.3 从 piecewise circuit 到 large- 与 small-signal model

通用电路写成

\[
E\dot{\boldsymbol x}=f(\boldsymbol x,\boldsymbol u,\boldsymbol s),\qquad
\boldsymbol y=g(\boldsymbol x,\boldsymbol u,\boldsymbol s).
\tag{24}
\]

搬到 coefficient space 后得到

\[
(E\otimes I)\frac{d\langle\boldsymbol x\rangle}{d\tau}
=\langle\boldsymbol f\rangle-(E\otimes jN\omega)\langle\boldsymbol x\rangle,\qquad
\langle\boldsymbol y\rangle=\langle\boldsymbol g\rangle .
\tag{32}
\]

steady state 令左侧为零，形成 Eq. (33) 的平衡方程；在该 operating point 对 coefficient vectors 局部线性化，得到 Eq. (34) 的 LTI small-signal system。关键点是 Jacobian 的每个块仍是由偏导的 Fourier coefficients 形成的 Toeplitz matrix，所以 harmonic coupling 没有在线性化时消失。[pdf:E05]（PDF 物理页 5，Eq. (24)–(30)）[pdf:E06]（PDF 物理页 6，Eq. (31)–(35)）

### 6.4 用边沿时刻统一 switching signal

若一个周期内 Boolean signal \(s(t)\) 只有一个 rising instant \(t_r\) 和一个 falling instant \(t_f\)，作者先由二者确定 duty 与 phase，再给出

\[
\langle s\rangle_n=
\begin{cases}
\langle s\rangle_0,&n=0,\\
\dfrac{1}{\pi n}e^{jn\angle\langle s\rangle_1}
\sin\!\bigl(\pi n\langle s\rangle_0\bigr),&n\ne0 .
\end{cases}
\tag{37}
\]

边沿变化对各阶 coefficient 的敏感度为

\[
\frac{\partial\langle s\rangle_n}{\partial t_r}
=-\frac1T e^{-jn\omega t_r},\qquad
\frac{\partial\langle s\rangle_n}{\partial t_f}
=\frac1T e^{-jn\omega t_f}.
\tag{38}
\]

因此 modulation 或状态只要能决定 \(t_r,t_f\)，就能接入统一 switch model。[pdf:E06]（PDF 物理页 6，Eq. (36)–(38)）

若边沿是 \(x(t_0)=0\) 的零点，full differential 给出一般关系

\[
\frac{\partial t_0}{\partial\langle x\rangle_m}
=\frac{-e^{jm\omega t_0}}
{\sum_{n=-\infty}^{+\infty}jn\omega\langle x\rangle_n e^{jn\omega t_0}},
\tag{44}
\]

而当 \(x\) 在零点可微时，分母可写成 \(\dot x(t_0)\)，得到 Eq. (47)。这解释了 PWM comparator、DCM 二极管电流归零等事件如何进入 linearized model，也暴露了一个后文反例会利用的脆弱点：零点处斜率趋近零时，switch-time sensitivity 会变得病态。[pdf:E07]（PDF 物理页 7，Eq. (42)–(48)）

### 6.5 sideband transfer matrix

moving coefficient 的 Laplace transform 把原信号频率平移到 \(s+jn\omega\)。若 coefficient-space transfer matrix 为 \(H(s)\)，则

\[
\mathcal L\{y\}(s+jm\omega)
=\sum_{n=-\infty}^{+\infty}H_{mn}(s)\,
\mathcal L\{x\}(s+jn\omega).
\tag{21}
\]

所以 \(H_{mn}\) 不是抽象矩阵元素，而是输入第 \(n\) 个 sideband 到输出第 \(m\) 个 sideband 的通道。该式是作者“用 LTI 框架表示跨频耦合”的数学核心。[pdf:E05]（PDF 物理页 5，Eq. (19)–(23)）

## § 7 — 实验设计与结论

### 问题一：PWM boost 在 CCM 与 DCM、特别是 \(f_s/2\) 以上是否仍能预测 duty-to-output response？

**实验。** 原型参数为 \(L=33\,\mu\text{H}\)、\(v_i=24\,\text{V}\)、\(f_s=100\,\text{kHz}\)、steady-state duty \(50\%\)。CCM 使用 \(R=25\,\Omega,C=0.9\,\mu\text{F}\)，输出约 \(48\,\text{V}\)；DCM 使用 \(R=100\,\Omega,C=0.7\,\mu\text{F}\)，输出约 \(60\,\text{V}\)。作者以 \(1\%\) duty modulation 从 \(1\) 扫到 \(180\,\text{kHz}\)，并用 \(-49\) 至 \(49\) 阶系数重建波形。[pdf:E09]（PDF 物理页 9，Table III 与 Section V-D）[pdf:E10]（PDF 物理页 10，Section V-D）

**答案。** Fig. 5 同时给出实测点、high-order generalized average 与 classical moving average。论文直接结论是：新模型在调制频率接近或超过 \(f_s/2=50\,\text{kHz}\) 时更准确；图中 CCM 与 DCM 的高频 peaks/notches 也确实由新模型跟随，而 moving average 明显偏离。[pdf:E11]（PDF 物理页 11，Fig. 5(g)–(h) 及 caption）论文没有报告全频段 RMSE、最大幅相误差或置信区间，因此不能把“更准确”外推成一个已量化的误差保证。

### 问题二：\(V^2\) constant-ON-time buck 能否在接近 switching frequency 时辨认传统 describing-function model 预测错的峰谷？

**实验。** 评估板参数为 \(L=15\,\mu\text{H},C=20\,\mu\text{F},r=0.39\,\Omega,v_i=12\,\text{V},v_c=2.5\,\text{V}\)，实测 ON-time \(554\,\text{ns}\)、logic/drive delay \(170\,\text{ns}\)。CCM 的 \(R=10\,\Omega\)、实测 \(f_s=813\,\text{kHz}\)；作者用 \(10\,\text{mV}\) control-voltage modulation 从 \(100\,\text{kHz}\) 扫到 \(1.4\,\text{MHz}\)。[pdf:E12]（PDF 物理页 12，Table IV 与 Section VI-D）

**答案。** Fig. 8(g) 中，两模型的 magnitude 多数频段接近，但在 switching frequency 附近，新模型预测 peak，Li–Lee describing-function model 预测 valley；虚线圈出的实验点支持 peak。phase 差异还与旧模型未纳入 logic/drive delay 有关。[pdf:E13]（PDF 物理页 13，Fig. 8）[pdf:E14]（PDF 物理页 14，Section VI-D 对结果的解释）

**不得外推的范围。** DCM 下寄生电容与 choke inductance 产生振荡，下一次导通受 valley 触发，开关上升还滞后约 \(170\,\text{ns}\)，实验电路无法进入 steady state。因此 Fig. 8(d)、(f)、(h) 的 DCM steady state 与频响来自模型计算和 circuit simulation，不是实验频响；Table IV 的 DCM \(371\,\text{kHz}\) 也标有“simulation result”。[pdf:E12]（PDF 物理页 12，Table IV 脚注）[pdf:E14]（PDF 物理页 14，Section VI-D）

### 问题三：PFM LLC 在低于与高于谐振频率时，是否能覆盖高于 \(f_s/2\) 的 switching-frequency-to-output response？

**实验。** LLC 参数为 \(L_r=4.7\,\mu\text{H},C_r=530\,\text{nF},f_r=101\,\text{kHz},L_m=25\,\mu\text{H}\)、turn ratio \(r=2,C_f=8\,\mu\text{F},R_L=2\,\Omega,v_i=48\,\text{V}\)。两 operating points 是 \(f_s=80\,\text{kHz}<f_r\) 与 \(f_s=120\,\text{kHz}>f_r\)。PFM depth 为 \(5\,\text{kHz}\)，modulation frequency 从 \(1\) 扫到 \(190\,\text{kHz}\)；示例波形分别在 80-kHz operating point 加 \(10\,\text{kHz}\) modulation，以及在 120-kHz operating point 加 \(150\,\text{kHz}\) modulation。[pdf:E17]（PDF 物理页 17，Table V 与 Section VII-D）

**答案。** Fig. 11 的实测频响点对比 high-order model 与只保留 fundamental harmonic 的模型；论文结论是新模型更准确，差异在 modulation frequency 高于 \(f_s/2\) 时尤其明显。[pdf:E16]（PDF 物理页 16，Fig. 11 全图与 caption）同样，论文没有给出统计误差指标、重复实验次数或器件/温度变化下的 robustness。

三组验证覆盖了 PWM/PFM、CCM/DCM、低于/高于 resonant frequency 以及 state-dependent diode switching；但没有覆盖 grid-connected converter、multi-converter interaction、非周期稳态、强大信号扰动、数字采样/量化、器件非线性、dead time 扫描或 FPGA 实时执行。

## § 8 — Take-aways

**5 句话。**  
1. 这篇论文通过保留一组 moving Fourier coefficients，把开关纹波和 sideband coupling 变成 LTI harmonic channels，而不是在建模开始时平均掉。  
2. circuit equation 与 switching-signal equation 分开建模，再通过 switching instant sensitivity 组合，这是它比逐段 waveform analysis 更通用的结构。  
3. boost、buck、LLC 的结果表明，保留 \(-49\) 到 \(49\) 阶时，模型能在接近或超过 \(f_s/2\) 的频段跟随实验或仿真，而低阶 averaging/fundamental model 会漏掉峰谷。[pdf:E11]（PDF 物理页 11，Fig. 5）[pdf:E13]（PDF 物理页 13，Fig. 8）[pdf:E16]（PDF 物理页 16，Fig. 11）  
4. 模型的理论对象无限维，实际截断多少阶才达到给定误差，论文没有定量关系。[pdf:E18]（PDF 物理页 18，Conclusion）  
5. 本文没有实现 FPGA/HIL，因此它提供的是高频模型基础，而非已经完成实时性与资源验收的硬件方案。

**3 句话。**  
moving Fourier coefficients 让 dc、harmonics 与 sidebands 在同一 LTI 框架中耦合，switching instant Jacobian 则统一 PWM、PFM 和 state-dependent switching。三类原型/仿真显示它在 \(f_s/2\) 附近及以上比经典低阶模型更忠实。真正未解的问题是有限 harmonic truncation 的误差、条件数与计算成本如何被可靠控制。

**1 句话。**  
这篇论文的实质，是用“保留并耦合开关谐波”替代“先平均再补高频”，以更统一地跨越 \(f_s/2\) 建模边界。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**用一个有限的、固定截断的 harmonic set，就足以近似论文理论上的无限维模型，而且不会在目标频带遗漏决定性 coupling。**

论文直接承认 executable calculation 必须使用有限个 moving Fourier coefficients，截断会扭曲 steady-state waveforms 并给 transfer functions 引入误差；实验显示“dozens”可以得到很准的结果，但 truncation 与 error 的定量关系仍是未来问题。[pdf:E18]（PDF 物理页 18，Conclusion 的 limitation）三组案例都用了 \(-49\) 到 \(49\) 阶并取得一致波形，但这只是三个 operating families 的经验支持，不是对任意 topology、switching edge、Q factor 或控制带宽的误差界。[pdf:E10]（PDF 物理页 10，boost 的 \(-49\) 至 \(49\) 阶）[pdf:E17]（PDF 物理页 17，LLC 的 \(-49\) 至 \(49\) 阶）

这个假设可能在以下情形失效：开关边沿很陡而 spectrum 衰减慢；窄脉冲、dead time 或 diode reverse recovery 产生高阶内容；高-Q resonance 把一个看似很小的被截 harmonic 放大；某个 sideband 恰与控制 pole/zero 对齐；或者接近 CCM/DCM 边界时事件时刻对微小系数高度敏感。此时“幅值小的 harmonic”不等于“对 transfer function 不重要”。论文没有 harmonic-order sweep、a posteriori residual、condition-number 报告或 error certificate，所以目前无法在求解前知道 \(K=49\) 是否足够，也无法判断更复杂系统为达到给定误差需要多少计算量。

## § 10 — 最小复现实验

一周内最有辨识力的复现不是重做三台硬件，而是对 boost case 做 **harmonic-order convergence test**。

**数据与模型。** 使用 Table III 的 \(24\,\text{V}\)、\(33\,\mu\text{H}\)、\(100\,\text{kHz}\)、\(50\%\) duty，并分别采用 CCM 的 \(25\,\Omega/0.9\,\mu\text{F}\) 与 DCM 的 \(100\,\Omega/0.7\,\mu\text{F}\)。以高精度 switching simulation 作为独立参考；同时从 Fig. 5(g)–(h) 数字化实验点作 sanity check。[pdf:E09]（PDF 物理页 9，Table III）[pdf:E11]（PDF 物理页 11，Fig. 5）

**实现。**

1. 实现 Eq. (57)–(70) 的 boost large-/small-signal model，并分别截断为 \(K=1,3,5,9,19,49\)。
2. 对每个 \(K\) 解 steady state；DCM 内层迭代 \(i_L(t_{f2})=0\)。
3. 从 \(1\) 到 \(180\,\text{kHz}\) 扫 duty-to-output response，在 \(f_s/2\) 与 \(f_s\) 附近加密。
4. 同时记录 waveform \(L_2\) error、transfer magnitude/phase error、矩阵 condition number、solve time 与 memory；这几项能把“精度—阶数—成本”连起来。

**支持标准。** 随 \(K\) 增大，steady-state 与 transfer errors 总体收敛；\(K=49\) 在 Fig. 5 的实验点附近复现作者的峰谷，并在 \(50\)–\(180\,\text{kHz}\) 显著优于 \(K=0\) moving-average model。  
**反驳标准。** 误差随 \(K\) 不收敛或非稳定地反弹；不同 \(K\) 在 \(f_s/2\) 以上给出互相矛盾的 pole/zero；或者即使 \(K=49\) 仍无法匹配 switching reference/实验点。该实验首先验证论文最重要、也最缺定量证据的 practical truncation claim，而不需要复制完整硬件链。

## § 11 — 最强反例设计

最强攻击应对准 switching-time linearization，而不是只换一种负载。构造一个工作在 CCM/DCM grazing boundary 的变换器，使二极管电流在理论关断点不是以明确负斜率穿过零，而是近似相切：\(i_D(t_0)=0\) 且 \(\dot i_D(t_0)\approx0\)。再通过寄生谐振制造同一 fundamental window 内的多个近零 crossing。

Eq. (44)/(47) 的 switch-time sensitivity 以 \(\dot x(t_0)\) 或其 harmonic sum 为分母；在 grazing point 分母趋近零，微小 state perturbation 会造成极大的 event-time perturbation，甚至让“唯一 rising/falling instant”失效。[pdf:E07]（PDF 物理页 7，Eq. (44)–(47)）buck DCM 实验已经给出一个接近该方向的警告：寄生 LC 振荡导致 valley-triggered conduction、约 \(170\,\text{ns}\) delay，并使电路无法进入稳态，作者因此没有给出 DCM 实验频响。[pdf:E14]（PDF 物理页 14，Section VI-D）

具体反例可扫 load 与 parasitic capacitance，使 \(i_D\) 的零点从横穿变为相切再变为多次 crossing；对每个点比较 event-driven switching simulation 与 high-order model 的 predicted pole/zero 和频响。如果模型在 grazing 前后产生不连续、无界或错误的 small-signal gain，而提高 harmonic order 仍不能修复，就说明问题不只是 truncation，而是局部线性 switch-time map 在这类真实工况不存在或不唯一。这会直接挑战论文对 state-dependent switching 与“几乎所有 power converters”的广泛适用表述，而不是泛泛地说器件不理想。

## § 12 — Follow-up Research Idea

**候选研究想法，不声称 novelty。** 将研究目标从“给定固定 harmonic order，求一个 high-order model”改成“给定频带与误差容限，自动生成带可核验误差证书的最小 harmonic realization”。输出不只是 \(H(s)\)，还包括：每个 retained/discarded sideband 对目标 transfer channel 的 sensitivity、steady-state residual、event-time conditioning，以及一个覆盖指定频带的 a posteriori error bound。若遇到 grazing/multiple-crossing，算法应返回“当前 LTI event map 不成立”的证书，而不是继续给出看似精确的 transfer curve。

**(a) 未满足需求。** 论文已经证明高阶通道有价值，却没有回答设计者最实际的问题：为达到 1% 幅值误差或若干度相位误差，要保留哪些 harmonic、付出多少矩阵和硬件成本。[pdf:E18]（PDF 物理页 18，truncation limitation）

**(b) 研究价值。** 在 power electronics 领域，影响力更依赖可验证的精度、工程可实现性和跨 operating point 的稳健性，而不是仅扩大一个算例。若能把 harmonic order 选择从经验常数变成可审计的 accuracy contract，它可同时服务 controller design、model-order reduction 与后续 HIL/FPGA sizing。

**(c) 相邻领域工具。** 可借鉴 adaptive spectral methods 的 residual-based refinement、model-order reduction 的 frequency-weighted balanced truncation，以及 hybrid systems 的 saltation/event-conditioning analysis；重点不是简单“多加几阶”，而是按目标 channel 的耦合敏感度选择非连续 harmonic set，并检测 event map 是否失去可微性。

**(d) 第一个证伪实验。** 在本文 boost、buck、LLC 三组参数上外加 §11 的 grazing sweep，要求算法给出的 error certificate 在所有频点都上界 event-driven simulation/实验误差。只要存在一个 operating point 的实际误差超过证书，或算法在接近 grazing 时仍错误宣称 map well-conditioned，这个方向的核心 claim 就被证伪。

**(e) 与本文的实质区别。** 本文提出统一的无限维表示并用固定 \(-49\) 到 \(49\) 阶展示准确性；候选方向把“表示能力”改造成“可证明的有限实现选择问题”，同时把 harmonic truncation 与 switching-event conditioning 纳入同一个失败可见的框架。由于本卡没有联网检索这一交叉方向的完整相关工作，以上只作为证据约束的研究候选，不主张它尚无人提出。
