# FPGA-Based Detailed Real-Time Simulation of Power Converters and Electric Machines for EV HIL Applications

Luis Herrera, Cong Li, Xiu Yao, Jin Wang  
*IEEE Transactions on Industry Applications*, 51(2), 2015  
DOI：10.1109/TIA.2014.2350074  
Zotero key：G7MWPVIS

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“能否在 FPGA 上跑一个电机模型”这一宽泛问题，而是一个更具体的工程矛盾：EV 的功率变换器开关越来越快，HIL 仿真步长必须显著小于开关周期；与此同时，若模型只保留理想开关和线性电机，又会漏掉器件导通压降、温升反馈以及磁饱和等真正影响控制器和保护逻辑的效应。作者指出，当时典型 CPU 实时平台的最小步长约为 \(10~\mu\text{s}\)，而 FPGA 的并行计算和低总线延迟适合把内部步长推进到亚微秒量级。[pdf:E01]（PDF 物理页 1，Introduction）

这里的“详细”有两层物理含义。对变换器，它意味着开关导通电阻 \(r_{\rm on}\) 和正向压降 \(v_f\) 随电流、结温变化，并让电损耗、热网络和结温构成闭环；对电机，它意味着互感不再是假定常数，而是随磁化状态改变，并出现 \(d\)-、\(q\)-轴之间的 cross-saturation（交叉饱和）。[pdf:E02]（PDF 物理页 2，Section II）[pdf:E04]（PDF 物理页 4，Section III-A）

这对 EV HIL 重要，因为被测控制器看到的不是离线平均值，而是与开关事件同步的电压、电流、转矩和速度。如果模拟器太慢，开关事件会被跨过；如果模型太理想，控制器可能在仿真中稳定，却在真实器件的压降、温升或电机饱和下偏离。论文因此把价值落在三个可检验目标上：更小的实时步长、比理想模型更接近器件与电机的物理行为、以及能与外部控制器闭环交互的 HIL 平台。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）[pdf:E08]（PDF 物理页 8，Fig. 18 与 Section V）

## § 2 — 前人工作与不足

论文把既有实时建模方法分为几条路线。功率电子侧已有 state-space、modified nodal approach（MNA，修正节点分析）以及器件状态机；电机侧已有 FPGA 上的交流电机模型；数值实现则以 fixed-point 为主，少数工作使用 single、double 或 custom floating-point。[pdf:E01]（PDF 物理页 1，Introduction）这些方法已经证明 FPGA 可以承担实时电磁暂态计算，但作者认为它们没有同时闭合“器件非线性—损耗—温度”和“电机磁饱和”两条链路。

具体而言，传统 MNA 若把 \(r_{\rm on}(i,T_j)\) 和 \(v_f(i,T_j)\) 直接放进网络参数，系统矩阵会随非线性状态变化，矩阵及其逆需要频繁重算；hybrid state-space 也可能因 \(N\) 个开关面对多达 \(2^N\) 个拓扑状态。作者的批评不是“这些方法不能算”，而是这种重算与拓扑切换不适合追求极短固定步长的 FPGA pipeline。[pdf:E02]（PDF 物理页 2，Eq. (2)–(5) 后正文）

热模型此前已有离线电热联合仿真，也有真实全桥的实时温度监视，但本文要把导通损耗、开关损耗、热 RC 网络和电气模型放进同一实时执行链。[pdf:E01]（PDF 物理页 1–2 交界处，相关工作）电机饱和方面，FEA 加 lookup table 能表达 PMSM 等机器的非线性，但表会同时依赖 \(i_d\)、\(i_q\) 和转子位置 \(\theta_r\)，为避免插值跳变必须足够稠密；表过大或不连续会直接伤害 FPGA 资源和暂态连续性。[pdf:E04]（PDF 物理页 4，Section III-A.1）

作者因此改变了两个假设：第一，不让器件非线性改变网络矩阵，而把它改写成输入源；第二，不把饱和当作大型多维表，而从一条磁化曲线推导动态电感、静态电感和交叉饱和项。需要注意，论文对“前人不足”的比较主要是方法论说明，并没有给出统一硬件、统一精度下的 MNA、state-space、FEA lookup table 与本文方法的资源/延迟 benchmark。[pdf:E02]（PDF 物理页 2，作者方法概述）[pdf:E05]（PDF 物理页 5，Eq. (14)–(24)）

## § 3 — 重建作者的思考路径

可以从当时已经知道的失败模式反推作者的路线。

第一步，实时求解最怕每步改变计算结构。既然一个固定拓扑网络可以写成 \(A x_{k+1}=u_k\)，让 \(A^{-1}\) 预先固定就能把每步计算变成规则的矩阵—向量运算，适合 FPGA 并行化。[pdf:E02]（PDF 物理页 2，Eq. (2)）问题是，真实开关的导通压降和导通电阻又确实随 \(i,T_j\) 变化；因此自然的出路是保留固定 \(A\)，把非线性塞进等效 Thevenin 电压源，而不是塞回矩阵。[pdf:E02]（PDF 物理页 2，Fig. 2 与 Eq. (3)–(5)）

第二步，一旦 \(v_f(i,T_j)\) 被显式计算，导通损耗就已经有了；再把 datasheet 给出的开关能量转成平均开关损耗，就能用热 RC 网络更新结温，并把新结温反馈给下一步的 \(v_f\)。这样电气和热模型不是先后跑两个松散程序，而是在同一细步长上交换损耗和温度。[pdf:E03]（PDF 物理页 3，Eq. (6)–(10) 与 Fig. 5）

第三步，电机侧先选择低阶、参数相对静态的 \(dq\) 模型，因为它比 phase-domain 更适合实时实现；再观察饱和主要改变互感而非大部分位于空气磁路中的漏感。[pdf:E04]（PDF 物理页 4，Section III）若磁化磁链和电流用极坐标表示，磁化曲线的斜率自然给出 dynamic inductance \(L_y=d|\lambda_m|/d|i_m|\)，而割线斜率给出 static inductance \(L_m=|\lambda_m|/|i_m|\)。把这两个量投影回 \(d\)、\(q\) 轴，就得到自轴饱和和 cross-saturation 项。[pdf:E05]（PDF 物理页 5，Eq. (14)–(19)）

第四步，饱和使电感矩阵 \(L\) 每步变化，矩阵求逆重新成为瓶颈。作者发现 \(\det(L)\) 与磁化角 \(\mu\) 无关，于是把 determinant 与 adjugate（伴随矩阵）并行计算，再用 \(L^{-1}=L^\*/\det(L)\) 关闭这条计算链。[pdf:E05]（PDF 物理页 5，Eq. (24)）[pdf:E06]（PDF 物理页 6，Fig. 9–10）这条思考路径的共同主题是：不删除物理非线性，而是把它改写成固定、规则、可并行的数据流。

## § 4 — 核心 Intuition

核心 intuition 是：把“会改变求解结构的非线性”改写为“每步更新的输入数据”，就能同时保留物理细节与 FPGA 的固定流水线。变换器侧用等效电压源承载 \(r_{\rm on}\) 和 \(v_f\)，电机侧用磁化曲线生成少量时变电感并并行求逆。[pdf:E02]（PDF 物理页 2，Eq. (5)）[pdf:E06]（PDF 物理页 6，Fig. 10）小步长不是精度的替代物，但它让简单的 forward Euler 也可能在给定电机参数下达到可接受误差，同时显著减少计算依赖。[pdf:E05]（PDF 物理页 5，Eq. (23) 前正文）

## § 5 — 具体方法与完整 Pipeline

以“boost converter 电热模型 + 饱和 induction machine EV drive”为例，完整 pipeline 可以分成两条实时数据流。

**A. 变换器电热数据流**

1. 输入电路参数、直流电压、负载、gate signal，以及器件 datasheet 给出的 \(v_f(i,T_j)\)、开关能量和热阻热容参数。实验模型采用 Powerex PS22A78-E IPM；Table II 报告 \(L=13~\text{mH}\)、\(C=1.1~\text{mF}\)、\(F_{\rm sw}=10.8~\text{kHz}\)、内部步长 \(T_s=200~\text{ns}\)，输入范围为 \(200\)–\(325~\text{V}\)。[pdf:E06]（PDF 物理页 6，Table II 与 Hardware Description）
2. 根据开关状态生成 MNA current source，或等价地生成 Thevenin source。导通时不修改网络矩阵，而用 \(r_{\rm on}i+v_f\) 修正等效源；关断时源由端口电压决定。[pdf:E02]（PDF 物理页 2，Fig. 2 与 Eq. (1)–(5)）
3. 用固定 \(A^{-1}\) 完成下一电气步，得到电感电流、输出电压和器件电流。每个器件并行累计 ON current 和开关次数；损耗窗口可取一个完整开关周期，也可更短以更新得更频繁。[pdf:E03]（PDF 物理页 3–4 交界处，Fig. 5–7 与算法正文）
4. 由 \(i\,v_f(i,T_j)\) 计算导通损耗，由 \(E_{\rm sw}F_{\rm sw}\) 计算平均开关损耗，再驱动 junction-to-case、case-to-fin、fin-to-ambient 的 RC thermal network。[pdf:E03]（PDF 物理页 3，Eq. (6)–(10) 与 Fig. 4）
5. 新的 \(T_j\) 反馈到下一步 \(v_f(i,T_j)\)。为保持输入、输出、导通损耗和开关损耗的 power balance，模型在输入端并联 \(I_{\rm sw}=P_{\rm sw}/V_{\rm in}\)。[pdf:E04]（PDF 物理页 4，Eq. (11)–(12)）
6. 实际平台为 Opal-RT 系统中的 Xilinx Virtex-6 FPGA；论文报告 ADC、DAC 和 digital I/O 的时间率分别为 \(2.5~\mu\text{s}\)、\(1~\mu\text{s}\) 和 \(0.2~\mu\text{s}\)。这意味着 \(200~\text{ns}\) 是内部模型步长，不能直接等同于所有模拟接口都以 \(200~\text{ns}\) 刷新。[pdf:E06]（PDF 物理页 6，Hardware Description）

**B. 饱和电机与 EV HIL 数据流**

1. 输入三相逆变器输出、转速 \(\omega_r\)、电机电阻漏感参数和一条 \(|\lambda_m|(|i_m|)\) 饱和曲线；外部 Wanda 3U Linux target 运行控制器，向 FPGA 注入 gating signals，并读取 \(\omega_r\)、定子电流和电压。[pdf:E07]（PDF 物理页 7，Fig. 17）[pdf:E08]（PDF 物理页 8，Section V）
2. 从 \(i_{md},i_{mq}\) 得到 \(|i_m|\) 与磁化角 \(\mu\)，由曲线同时计算 \(L_m\) 和 \(L_y\)，再形成 \(L_{dd},L_{qq},L_{dq}=L_{qd}\)。后者就是磁化方向变化在正交轴之间产生的 cross-saturation coupling。[pdf:E05]（PDF 物理页 5，Eq. (16)–(21)）
3. 并行计算 \(\det(L)\) 和伴随矩阵 \(L^\*\)，得到 \(L^{-1}\)，再以 forward Euler 更新电机状态；转矩与机械转速状态并行推进。[pdf:E05]（PDF 物理页 5，Eq. (22)–(24)）[pdf:E06]（PDF 物理页 6，Fig. 9–10）
4. 输出电磁转矩、转速和电气量给外部控制器。论文报告无饱和模型步长 \(200~\text{ns}\)，有饱和模型步长 \(650~\text{ns}\)，并在示例中把逆变器运行到 \(24~\text{kHz}\)。[pdf:E08]（PDF 物理页 8，Table IV 与 RT Results）

论文没有报告 FPGA 的 LUT、DSP、BRAM、clock frequency、pipeline latency 或 timing slack，也没有交代定点/浮点格式和量化误差。因此可以确认的是“某平台达到了所报步长”，不能从本文单独重建等资源、等时序的 bit-accurate FPGA 实现。

## § 6 — 核心数学推导

### 6.1 把器件非线性移到输入端

传统 Thevenin switch 在导通时的源为 \(-R_{\rm TH}i_k\)。作者把真实导通特性加入后写成

\[
E_{{\rm TH},k+1}=-R_{\rm TH}i_k+r_{\rm on}i_k+v_{f,k}.
\]

这样稳态端口压降成为 \(r_{\rm on}i+v_f\)，而 \(A^{-1}\) 保持常数。[pdf:E02]（PDF 物理页 2，Eq. (3)–(5)）物理上，\(-R_{\rm TH}i_k\) 是离散开关 companion model 的历史项，后两项才是器件真实导通损耗的来源。它不是忽略非线性，而是改变非线性进入求解器的位置。

### 6.2 电—热闭环与能量补偿

热模型利用电—热类比：

\[
T_{j-c}=Z_{\rm th,j-c}P_{\rm loss},\qquad
\dot x=A_{\rm th}x+B_{\rm th}u,\quad y=C_{\rm th}x+D_{\rm th}v.
\]

其中功率损耗对应热流，温差对应电压，RC 支路对应不同热时间常数。[pdf:E03]（PDF 物理页 3，Eq. (6)–(7) 与 Fig. 4）器件导通损耗和开关损耗分别为

\[
P_{\rm cond}^{\alpha}=i^\alpha v_f^\alpha(i^\alpha,T_j^\alpha),\qquad
P_{\rm sw}^{i}=E_{\rm sw}^{i}F_{\rm sw},
\]

其中 \(\alpha\in\{i,d\}\) 分别代表 IGBT 与 diode。[pdf:E03]（PDF 物理页 3，Eq. (8)–(10)）为了不让“只在热模型里记账的开关损耗”破坏电气侧功率守恒，作者补入

\[
P_{\rm in}=P_{\rm out}+P_{\rm cond}+P_{\rm sw},\qquad
I_{\rm sw}=\frac{P_{\rm sw}}{V_{\rm in}}.
\]

[pdf:E04]（PDF 物理页 4，Eq. (11)–(12)）工程含义是：平均开关能量通过一个输入电流源从电源侧被真实扣除，而不是仅用于显示温升。

### 6.3 从磁化曲线得到 cross-saturation

作者把磁化磁链和电流写成复数极坐标：

\[
\lambda_m=|\lambda_m|e^{j\mu},\qquad i_m=|i_m|e^{j\mu},
\]

并定义 dynamic inductance \(L_y=d|\lambda_m|/d|i_m|\)。对两式求时间导数并分解到 \(d,q\) 轴，可得

\[
\begin{aligned}
L_{dd}&=L_y\cos^2\mu+L_m\sin^2\mu,\\
L_{qq}&=L_m\cos^2\mu+L_y\sin^2\mu,\\
L_{dq}=L_{qd}&=\frac{L_y-L_m}{2}\sin(2\mu),
\end{aligned}
\]

其中 \(L_m=|\lambda_m|/|i_m|\)。[pdf:E05]（PDF 物理页 5，Eq. (14)–(18)）\(L_m\) 是从原点到当前点的割线斜率，代表当前磁化水平；\(L_y\) 是曲线在当前点的切线斜率，代表一个小扰动看到的增量电感。在线性区二者相等，于是 \(L_{dq}=0\)，模型退化为经典未饱和模型；进入饱和后 \(L_y\neq L_m\)，正交轴之间出现耦合。

饱和曲线被写为线性段与非线性插值段的分段函数，并要求 \(|\lambda_m|(|i_m|)\in C^1\)，也就是函数和一阶导数连续；转折点必须满足 \(L_m(|i_{mc}|)=L_y(|i_{mc}|)\)。[pdf:E05]（PDF 物理页 5，Fig. 8 与 Eq. (21)）这个约束的物理目的，是避免跨过饱和点时电感突然跳变，从而人为激发暂态。

### 6.4 离散推进与并行求逆

饱和 \(dq\) 模型写成

\[
\frac{di_{dq}^{sr}}{dt}
=L^{-1}(-R-\Omega L_r)i_{dq}^{sr}+L^{-1}v_{dq}^{sr},
\]

forward Euler 离散后为

\[
i_{k+1}=(I+T_sA)i_k+T_sBv_k,\qquad
A=L^{-1}(-R-\Omega L_r),\quad B=L^{-1}.
\]

[pdf:E05]（PDF 物理页 5，Eq. (22)–(23)）作者报告，在其考察的一组电机参数上，纳秒级步长的 forward Euler 与 Runge–Kutta 百分差异小于 \(1\%\)，但没有给出参数扫描范围、误差范数或完整曲线，因此这个 \(<1\%\) 不能外推到任意刚性电机模型。[pdf:E05]（PDF 物理页 5，Eq. (23) 前正文）

关键化简是

\[
\det(L)=d_1(L_m+L_y)+d_2L_mL_y+d_3,
\]

其结果与磁化角 \(\mu\) 无关；因此 determinant 和 adjugate 可并行求得，再组合成 \(L^{-1}=L^\*/\det(L)\)。[pdf:E05]（PDF 物理页 5，Eq. (24)）[pdf:E06]（PDF 物理页 6，Fig. 10）这降低了串行依赖，但论文没有提供与 Cholesky 或一般矩阵求逆的 cycle、资源和精度对比，故“更快”的程度仍未被量化。

## § 7 — 实验设计与结论

**问题 1：等效源方法是否重现带导通压降的电路？**  
实验：作者用 \(L=1~\text{mH}\)、\(C=1~\text{mF}\)、\(r_{\rm on}=10~\text{m}\Omega\)、\(v_f=1~\text{V}\)、\(F_{\rm sw}=1~\text{kHz}\)、\(T_s=1~\mu\text{s}\) 的 boost circuit，把本文模型与 MATLAB SimPower Systems 对比，并另画忽略 \(r_{\rm on},v_f\) 的理想曲线。[pdf:E03]（PDF 物理页 3，Table I 与 Fig. 3）  
答案：波形图显示本文模型与 SimPower Systems 接近，忽略导通特性的曲线则出现偏离。不过作者没有报告最大误差、RMS error 或能量误差，所以这里只能支持“视觉一致”，不能支持某个数值精度界。

**问题 2：损耗算法能否跟随真实 power converter？**  
实验：在 Virtex-6/Opal-RT 平台上运行 Powerex PS22A78-E boost converter 模型，用 Yokogawa WT3000 测量真实损耗；Table II 给出 \(600\)–\(4500~\text{W}\) 输入功率范围和 \(200~\text{ns}\) 步长，Fig. 13 比较多组输入电流下的 RT 与实验损耗。[pdf:E06]（PDF 物理页 6，Table II、Fig. 12–13）  
答案：实验点整体围绕 RT 曲线分布，作者称两者 closely match。图中可见仍有离散偏差，但论文没有给出误差条、重复次数或统计指标，因此不能从曲线估读成精确误差百分比。

**问题 3：电气暂态是否跟随硬件？**  
实验：把输入电压从 \(300\) 跃变到 \(325~\text{V}\)，并列显示实验与 RT 的开关电压、电感电流、输出电压和输入电压。[pdf:E07]（PDF 物理页 7，Fig. 14）  
答案：两组波形在振荡形状和衰减趋势上相似，支持电气模型能重现该 operating point 附近的暂态；但图的垂直刻度并不完全相同，且没有时间对齐误差或 waveform norm，故不能声称逐点相等。

**问题 4：损耗驱动的热响应是否正确？**  
实验：输入从 \(200~\text{V}\)、\(1.03~\text{kW}\) 变到 \(325~\text{V}\)、\(2.73~\text{kW}\)，比较约 \(1800~\text{s}\) 内实验与 RT 的 heatsink temperature；另以 duty-cycle step 展示 IGBT 与 diode junction temperature 的实时估计。[pdf:E07]（PDF 物理页 7，Fig. 15–16）  
答案：heatsink 曲线在稳态和整体上升趋势上接近，说明“损耗—热网络”链路在这一次功率阶跃上成立。Fig. 16 的结温没有同时给出 junction temperature 实测，因此它是模型输出展示，不是结温准确度验证。

**问题 5：饱和模型能否在 EV HIL 步长内运行并产生合理差异？**  
实验：作者用三相 induction machine 和外部 vector controller，对比饱和与未饱和模型；参数表报告 \(V_{dc}=800~\text{V}\)、\(F_{\rm sw}=2\)–\(24~\text{kHz}\)，步长分别为 \(650~\text{ns}\) 与 \(200~\text{ns}\)，CPU 对照步长列为 \(25~\mu\text{s}\)。[pdf:E08]（PDF 物理页 8，Table IV、Fig. 18–19）  
答案：在 \(30~\text{Hz}\) 输入基波下，饱和模型给出更低的起动电磁转矩幅值，而转矩频率和相位基本不变；作者把这一趋势解释为与既有饱和研究一致。[pdf:E09]（PDF 物理页 9，Fig. 20 与 Conclusion）但是这里没有真实电机或高保真 FEA 的同步对照，且作者明确把“饱和对 vector controller 的影响”留作 future study。[pdf:E08]（PDF 物理页 8，RT Results）因此它验证了实时执行和内部可解释差异，没有闭合 machine-model fidelity。

总体上，实验对 converter 电气与 heatsink thermal response 给出了硬件对照，对 machine saturation 只给出了 HIL 内部比较。论文也没有报告 FPGA resource utilization、worst-case execution time、timing closure、长时间 overrun 或多实例扩展结果，不能把单机样例直接外推为任意规模 EV drivetrain 的实时能力。

## § 8 — Take-aways

**5 句话**

1. 论文最有价值的思想，是把器件非线性从时变矩阵移入每步更新的等效源，从而保留固定求解结构。[pdf:E02]（PDF 物理页 2，Eq. (5)）
2. 导通损耗、开关损耗、热 RC 网络和结温反馈被连成一条可在 FPGA 中并行执行的电热链。[pdf:E03]（PDF 物理页 3，Fig. 5–6）
3. 电机侧用 \(L_m\)、\(L_y\) 和磁化角推导 self-saturation 与 cross-saturation，不依赖大型多维 FEA table。[pdf:E05]（PDF 物理页 5，Eq. (16)–(24)）
4. boost converter 的损耗、电气暂态和 heatsink temperature 有真实硬件对照，而饱和电机只有 HIL 内部对比。[pdf:E06]（PDF 物理页 6，Fig. 13）[pdf:E07]（PDF 物理页 7，Fig. 14–16）[pdf:E09]（PDF 物理页 9，Fig. 20）
5. \(200~\text{ns}\) 与 \(650~\text{ns}\) 是有吸引力的结果，但缺少资源、数值格式、误差界和 machine ground truth，使其更像可行性证明而不是可直接复制的完整规格。[pdf:E08]（PDF 物理页 8，Table IV）

**3 句话**

作者通过等效源和解析饱和矩阵，把两类非线性改写成规则 FPGA 数据流。[pdf:E02]（PDF 物理页 2）[pdf:E06]（PDF 物理页 6）变换器电热部分有较强的实验支撑，电机饱和部分主要证明“能实时运行并产生合理趋势”。[pdf:E07]（PDF 物理页 7）[pdf:E09]（PDF 物理页 9）真正复用该工作时，应继承其重构思路，而不能把所报步长自动等同于已验证的整车 HIL fidelity。

**1 句话**

这是一篇把“详细物理”重新组织成“固定、并行、可实时计算结构”的方法论文，其 converter 证据强于 machine saturation 证据。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**真实 induction machine 的饱和可由一条静态、单值、\(C^1\) 的 \(|\lambda_m|(|i_m|)\) 曲线充分描述，并且主要只需修改互感。** 论文明确说明模型只需要 Fig. 8/19 那样的 saturation curve，并假设大部分漏磁通经过空气，因此漏感通常不饱和。[pdf:E04]（PDF 物理页 4，Section III-A）[pdf:E05]（PDF 物理页 5，Eq. (21)）如果真实机器存在显著 hysteresis、频率相关铁耗、温度漂移、空间谐波、转子位置相关饱和或动态 cross-saturation，那么“同一个 \(|i_m|\) 对应唯一 \(|\lambda_m|\)”就不成立；此时快速求得的 \(L^{-1}\) 仍然只是快速求解了错误模型。

论文给出的支持证据是：饱和模型在 FPGA 上达到 \(650~\text{ns}\) 步长，所得起动转矩幅值下降且频率、相位趋势与既有文献一致。[pdf:E08]（PDF 物理页 8，RT Results）[pdf:E09]（PDF 物理页 9，Fig. 20）缺失的关键证据是同一台真实电机在动态工况下的磁链、转矩或电流对照。

复现上还有一个直接可见的警告：Table IV 把 \(\bar L_m\) 写为 \(0.598~\text{mH}\)，但同页 Fig. 19 的 inductance 纵轴单位为 H，线性区约为 \(0.6~\text{H}\)。[pdf:E08]（PDF 物理页 8，Table IV 与 Fig. 19）这是论文内部的单位不一致；在没有作者源代码或参数澄清时，不应悄悄任选一个值。该问题不推翻方法，但会阻断 bit-for-bit 或 parameter-for-parameter 的电机结果复现。

## § 10 — 最小复现实验

一周内最可执行、且能证伪核心机制的实验是复现 **boost converter 的固定矩阵电热闭环**，因为论文为这一支提供了真实硬件对照，而电机参数存在上述单位歧义。

1. **数据与参数**：采用 Table II/III 的 \(L=13~\text{mH}\)、\(r_l=0.463~\Omega\)、\(C=1.1~\text{mF}\)、\(F_{\rm sw}=10.8~\text{kHz}\)、\(T_s=200~\text{ns}\)、热 RC 参数，以及 Eq. (25) 的 IGBT/diode \(v_f(i,T_j)\) surface fit。[pdf:E06]（PDF 物理页 6，Table II–III）[pdf:E07]（PDF 物理页 7，Eq. (25)）
2. **实现**：做两个完全相同输入的 solver。A 是本文的固定 \(A^{-1}\)+Thevenin input-source 方法；B 是每步按当前 \(r_{\rm on},v_f\) 更新的 reference MNA，使用 double precision 和更小步长作为数值基准。两者都接同一热 RC 网络和 \(I_{\rm sw}\) power-balance current。
3. **工况**：先跑 \(300\rightarrow325~\text{V}\) 电压阶跃，再跑 \(200~\text{V}/1.03~\text{kW}\rightarrow325~\text{V}/2.73~\text{kW}\) 功率阶跃，覆盖 Fig. 14–15 的两个关键实验。[pdf:E07]（PDF 物理页 7，Fig. 14–15）
4. **测量**：记录 \(i_L,v_C,v_{\rm sw}\)、每周期导通/开关损耗、heatsink temperature、能量残差 \(P_{\rm in}-P_{\rm out}-P_{\rm cond}-P_{\rm sw}\)，以及每步 worst-case latency。若有 FPGA，则再报告 LUT/DSP/BRAM、clock、timing slack 和连续一小时 overrun；只有综合结果不能替代真实 I/O HIL。
5. **预注册判据**：本文没有给误差阈值，因此复现实验应自己预注册而不是倒推图线。一个合理起点是：相对 reference MNA 的稳态电流/电压误差不超过 \(1\%\)，平均损耗误差不超过 \(2\%\)，功率残差低于输入功率的 \(0.5\%\)，且 \(200~\text{ns}\) deadline 无 overrun。若固定矩阵法在相同器件函数下不能满足这些阈值，或误差主要来自 source reformulation 而非离散步长，就反驳其“细节与实时性兼得”的核心工程 claim。

这个实验不能复现论文的真实热硬件结果，除非拿到同型号 IPM、散热器和测量条件；没有硬件时只能验证方法等价性和计算预算，不能报告完成了实验验证。

## § 11 — 最强反例设计

最强反例不是把 \(T_s\) 调大让 forward Euler 发散，而是构造两个具有**相同瞬时 \(|i_m|\)、不同磁化历史**的真实电机轨迹。让 induction machine 在相同电流幅值处分别从增磁和退磁方向进入，并跨越正反转、低频大磁通与高频弱磁、冷机与热机条件；用 dynamometer 和高带宽电压电流测量重建磁链与转矩。本文的静态单值曲线在同一 \(|i_m|\) 上必须给出同一 \(L_m,L_y\)，因而对两条历史轨迹给出相同局部电感；若真实机器出现稳定、可重复且超过测量不确定度的 hysteresis 或频率/温度依赖差异，模型的核心饱和表示就被直接证伪。[pdf:E05]（PDF 物理页 5，Fig. 8 与 Eq. (16)–(21)）

反例的输出不应只看转矩峰值。应同时比较 \(d/q\) 增量电感、定子电流谐波、磁链相位、起动转矩包络和 controller tracking error，并以未饱和模型、本文静态饱和模型和 history-dependent 模型三方对照。论文目前只展示饱和模型起动转矩幅值下降、频率和相位大致不变；这恰好可能由多种模型产生，不能唯一归因于本文推导的 cross-saturation 机制。[pdf:E09]（PDF 物理页 9，Fig. 20）如果 history-dependent 模型显著改善真实测量而本文模型不能，替代解释就成立。

## § 12 — Follow-up Research Idea

在 power electronics 与 electric drives 领域，高影响工作通常不仅要求更小步长，还要求可信的物理误差、硬件时序闭合、可复现实验和控制/保护任务上的实际价值。基于第 9 节，候选方向是把 HIL 电机模型从“单条确定性饱和曲线”重定义为**带历史状态与在线不确定度边界的实时磁化 emulator**。这不是在本文模型后面再加一个 correction block，而是把 HIL 的研究目标从“生成一条最可能波形”改为“在 deadline 内生成可验证的状态相关波形集合，并告诉控制器测试者哪些差异来自模型不确定性”。

（a）未满足的需求是：同一 \(|i_m|\) 下，hysteresis、温度、频率和空间谐波可能让真实磁链并不唯一，而本文只有静态曲线且没有真实电机 ground truth。[pdf:E05]（PDF 物理页 5，Eq. (21)）[pdf:E08]（PDF 物理页 8，machine HIL evidence）

（b）潜在研究价值在于：它能把“跑得快”与“测试结论可信”连接起来。若保护、故障检测或 model-predictive controller 在整个不确定度包络内仍通过，HIL 结果比单一 nominal trajectory 更有工程意义。

（c）可借鉴的相邻工具包括磁性材料中的 Preisach/Jiles–Atherton history state、control 中的 set-membership identification，以及 real-time computing 中的 worst-case execution-time analysis。模型必须压缩为少量可并行状态，并给出每步确定的 latency，而不是把大模型直接塞入 FPGA。

（d）首个证伪实验就是第 11 节的双历史轨迹：用未参与辨识的温度、频率和反转工况测试。如果 history-aware emulator 不能在固定 \(650~\text{ns}\) 预算内显著降低磁链/转矩误差，或其不确定度包络仍频繁漏掉真实轨迹，这个方向就失败。

（e）它与本文的实质区别是：本文假定一条 \(C^1\) 磁化曲线足以确定 \(L_m,L_y\) 并追求快速求逆；候选方向把磁化历史和模型不确定性本身提升为状态与验收对象。[pdf:E05]（PDF 物理页 5，Eq. (16)–(24)）由于本卡未对 2015 年之后的相关工作做系统检索，这只是证据约束下的候选研究想法，不声称 novelty。
