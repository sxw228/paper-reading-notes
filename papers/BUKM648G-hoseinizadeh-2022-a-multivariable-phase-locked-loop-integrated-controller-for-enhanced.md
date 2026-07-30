# A Multivariable Phase-Locked Loop-Integrated Controller for Enhanced Performance of Voltage Source Converters Under Weak Grid Conditions

- 作者：Seyed Milad Hoseinizadeh；Houshang Karimi；Masoud Karimi-Ghartemani；Saeed Ouni
- 出处：IEEE Transactions on Industrial Electronics, Vol. 69, No. 10, pp. 10079–10089 [pdf:E01]
- 年份：2022
- DOI：10.1109/TIE.2022.3146607 [pdf:E01]
- Zotero key：BUKM648G

> 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文处理的是 grid-following voltage source converter（VSC）在 weak grid 中的同步与电流控制问题。常规 vector current control（VCC）把 phase-locked loop（PLL）当成同步前端，再分别设计电流环；但电网短路比 SCR 降低时，PCC 电压越来越受变流器电流和电网阻抗影响，PLL 与电流环因此形成不能忽略的闭环耦合。作者指出，既有方案在相同工况下会在 SCR 低于 1.95 后逐渐振荡，并在 SCR=1.26 时失稳，而本文方案在 SCR=1 时仍保持平滑稳定；这使问题直接关系到高阻抗接入点上 DER 的可用功率范围和故障穿越能力 [pdf:E01]。

工程上的关键不是简单“调慢 PLL”，而是承认 PLL 状态已经属于 plant-controller 闭环的一部分。论文在 stationary \(\alpha\beta\) frame 中把三相 ePLL/UTSP 的内部状态与 VSC 电流状态联合建模，再用一个 multivariable controller 同时反馈电流、servo compensator 和 PLL 状态。作者的核心技术 claim 是：显式控制这些耦合状态，可以把弱电网导致的同步-电流相互作用纳入闭环极点整形，从而扩大稳定裕度 [pdf:E02]。

## § 2 — 前人工作与不足

论文给出的 prior-work 图景可以分成四类。第一，降低 PLL 增益可扩大功率容量，但 PLL 动态性能限制了能降低的程度；同步到“更强虚拟点”的 impedance conditioning 仍保留 PLL 非线性，在极弱电网下未必有效。第二，double-PLL impedance reshaping 把内电流环带宽假定为无穷，因此主要改善外环，不能解释有限带宽电流控制器与 PLL 的共同动态。第三，已有 frequency-coupling suppression 与 ePLL-integrated controller 面向单相系统，不能在不使用两个独立单相 PLL 的前提下直接推广到常规三相实现。第四，PLL-less VCC 以 band-pass filters 产生同步量，但论文引用的既有分析认为这些滤波器动态与 PLL 相近，仍可能遭遇同类弱网稳定问题 [pdf:E01] [pdf:E02]。

作者也承认 stationary-frame PR/VCC 相比 \(dq\)-frame 受到 PLL 的负阻尼影响较小，但 PCC voltage 等外环会同时恶化两者。因而缺口不是“没人研究弱网”，而是既有工作通常分开处理同步器、内电流环和功率参考生成器，或依赖单相、无限带宽等简化，缺少一个对三相 stationary-frame VSC 的联合状态模型和由该模型直接导出的 multivariable feedback [pdf:E01] [pdf:E02]。

## § 3 — 重建作者的思考路径

从论文给出的前置事实出发，可以重建出如下路径。首先，弱网使 \(v_{\mathrm{PCC}}\) 不再是近似刚性的外部输入，而会随 VSC 输出电流变化；所以 PLL 所观测的电压本身就是控制动作的结果。其次，如果继续把 PLL 当作独立测量器，电流环设计会漏掉由该反馈路径产生的交叉耦合。再次，三相 UTSP 已经提供正、负序电压估计以及可写成 LTI 方程的内部状态，那么这些状态就可以像电流状态一样进入 augmented plant。最后，一旦 plant、PLL 与 sinusoidal tracking servo 被放入同一状态向量，问题便可转化为完整状态反馈和 LQR 权重整定，而不再依赖逐环“补丁式”调参 [pdf:E02] [pdf:E03]。

这是基于论文证据的思路重建，不是作者逐字给出的发现史。它真正改变的假设是：同步器不是控制器之外的理想坐标生成器，而是需要被控制器直接看到的动态子系统。

## § 4 — 核心 Intuition

弱电网下，变流器电流会改变 PLL 正在跟踪的 PCC 电压，所以“PLL 先同步、电流环再控制”的串联直觉已经失效。本文把 PLL 状态并入 VSC 状态，让一个 multivariable controller 同时压制两个 \(\alpha\beta\) 通道中的同步耦合，而不是在耦合形成之后再靠降低 PLL 带宽缓解。LQR 只是求反馈增益的工具，真正起作用的机制是让反馈器显式获得同步器状态 [pdf:E03] [pdf:E04]。

## § 5 — 具体方法与完整 Pipeline

以给定 \(P^\*=4~\mathrm{kW}\)、\(Q^\*=2.9~\mathrm{kVAr}\) 的仿真工况为例，完整 pipeline 如下 [pdf:E07]。

1. 两电平三相 VSC 经 \(R_t+L_t\) 接入 PCC，电网由理想三相源和 \(R_g+j\omega L_g\) 表示；dc 侧被建模为固定 \(V_{dc}\) 的理想电压源，因此 dc-link 动态不在本文模型内。PCC 三相电压与输出电流经过 Clarke 变换进入 \(\alpha\beta\) frame [pdf:E02]。
2. UTSP 接收 \(v_{s,\alpha\beta}\)，估计正、负序分量以及内部状态 \(x_{1\mathrm{pll}},x_{2\mathrm{pll}}\)。Reference Generator 用平滑的 PLL 电压状态代替含开关噪声的瞬时 PCC 电压，将 \(P^\*,Q^\*\) 转成 \(i_\alpha^\*,i_\beta^\*\) [pdf:E03] [pdf:E04]。
3. 每个 \(\alpha\)、\(\beta\) 通道配置一个以电网频率 \(\omega\) 为内部模型的二阶 servo compensator，使 sinusoidal reference tracking 和同频扰动抑制转化为增广状态 \(x_c\) 的调节问题 [pdf:E04]。
4. 控制器以 \(x=[x_c^\mathsf{T},i_\alpha,i_\beta,x_{1\mathrm{pll}},x_{2\mathrm{pll}}]^\mathsf{T}\) 为状态，执行 \(u=-Kx\)。\(K=[K_c\ K_p]\) 中，\(K_c\) 反馈 servo 状态，\(K_p\) 同时反馈 converter current 与 PLL 状态；增益通过加权二次型代价和 MATLAB `lqr` 得到 [pdf:E04] [pdf:E05]。
5. \(u_{\alpha\beta}\) 变回 \(u_{abc}\)，再通过 SPWM 生成 VSC gate signals。论文报告仿真的 PWM switching frequency 为 5 kHz，实验也采用 5 kHz [pdf:E02] [pdf:E05] [pdf:E08]。

与 EMT + FPGA 实现直接相关但论文未报告的部分需要明确保留为空白：没有给出控制器的离散差分形式、采样周期与 PWM 更新相位、开关事件的时间推进、multi-rate 划分、任务依赖或并行调度、定点/浮点数值格式、量化与溢出策略、FPGA fabric 上的 HDL 映射、资源占用、流水线 latency 或 WCET。实验段只说明控制器运行于 OPAL-RT OP5700 FPGA-based real-time simulator，电压电流由 OP8660 采集；Fig. 19 的另一次实现则使用 eZdsp F28335 DSP。因而可以确认“在两个实时平台上运行过控制器”，不能据此推断已完成可移植 FPGA 核或确定性时序认证 [pdf:E08] [pdf:E10]。

## § 6 — 核心数学推导（无形式化数学则跳过）

第一步是把弱网反馈写进 PCC 电压。由变流器侧 KVL 与电网阻抗关系消去 \(\mathrm{d}i_{\alpha\beta}/\mathrm{d}t\)，论文的 Eq. (3) 可写成

\[
v_{s,\alpha\beta}
=\xi v_{g,\alpha\beta}+\sigma v_{t,\alpha\beta}+\tau i_{\alpha\beta},
\quad
\xi=\frac{L_t}{L_g+L_t},\ 
\sigma=\frac{L_g}{L_g+L_t},\ 
\tau=\frac{R_gL_t-L_gR_t}{L_g+L_t}.
\]

这说明 PCC 电压同时依赖理想电网电压、VSC 输出电压和 VSC 电流；\(L_g\) 增大时，控制动作到 PLL 输入的通道不能再忽略 [pdf:E03]。

第二步是把 UTSP 的正序提取器写成状态方程。Eq. (4) 使用

\[
\dot x_{1\mathrm{pll}}=\mu_1(u_\alpha-x_{1\mathrm{pll}})-\omega x_{2\mathrm{pll}},
\qquad
\dot x_{2\mathrm{pll}}=\mu_1(u_\beta-x_{2\mathrm{pll}})+\omega x_{1\mathrm{pll}},
\]

其中 \([x_{1\mathrm{pll}},x_{2\mathrm{pll}}]^\mathsf{T}
=V_p[\cos\phi_p,\sin\phi_p]^\mathsf{T}\)。将 Eq. (3) 代入后，PLL 状态直接含有 \(v_t\) 和 \(i\)；再与 VSC 方程组合为 Eq. (6)：

\[
\dot x_p=A_px_p+B_pu+F_pW,\qquad y=C_px_p,
\]

\(x_p=[i_\alpha,i_\beta,x_{1\mathrm{pll}},x_{2\mathrm{pll}}]^\mathsf{T}\)。作者声称该系统对所有系统参数可控、可观，并为 minimum phase；该结论是论文直接陈述，PDF 中没有展开证明 [pdf:E03]。

第三步是展示 reference generator 为什么也形成通道耦合。Eq. (7) 为

\[
\begin{bmatrix}i_\alpha^\*\\ i_\beta^\*\end{bmatrix}
=\frac{2}{3V_p^2}
\begin{bmatrix}
x_{1\mathrm{pll}} & x_{2\mathrm{pll}}\\
x_{2\mathrm{pll}} & -x_{1\mathrm{pll}}
\end{bmatrix}
\begin{bmatrix}P^\*\\Q^\*\end{bmatrix}.
\]

因此 PLL 方程与功率到电流的变换都混合 \(\alpha\)、\(\beta\) 通道；当 \(Q^\*=0\) 时 reference generator 的这部分耦合消失，但 PLL 耦合仍在 [pdf:E04]。

第四步是构造 sinusoidal internal model。论文取 \(p(D)=D^2+\omega^2\)，并以 Eq. (9)–(10) 的二阶 servo 状态实现同频跟踪，再把 \(x_c\) 与 \(x_p\) 合并。Full-state control law 为

\[
u=-Kx,\qquad K=[K_c\ K_p],
\]

并以 Eq. (14) 的代价

\[
J=\int_0^\infty\!\left[
q_1(e_\alpha^2+e_\beta^2)
+\frac{q_2}{\omega^2}(\dot e_\alpha^2+\dot e_\beta^2)
+q_5(z_\alpha^2+z_\beta^2)
+q_7z_{1\mathrm{pll}}^2+q_8z_{2\mathrm{pll}}^2
+v_\alpha^2+v_\beta^2
\right]\mathrm{d}t
\]

通过 LQR 权重调节闭环极点。论文给出的最终极点为 \(-297\pm j632\)、\(-281\pm j557\)、\(-683\pm j293\) 和 \(-505\pm j45\) [pdf:E04]。

第五步是推导极弱网下的 reactive-power 下界。忽略 \(R_g\)，由 \(j\omega L_gI=V_{\mathrm{PCC}}-V_g\) 与 \(S=1.5V_{\mathrm{PCC}}I^\*\)，令 \(V_{\mathrm{PCC}}=V_R+jV_I\)、\(K=\frac{2}{3}\omega L_g\)，论文得到

\[
Q\ge Q_{\min}
=\frac{K^2P^2-V_g^4/4}{V_g^2K}.
\]

作者进一步代入 SCR 定义，说明等号对应 SCR=1。物理意义是：电网越弱、给定 real power 越高，维持可行 PCC 电压所需的最低 reactive power 越大；这不是 controller 可以任意消除的 plant feasibility constraint [pdf:E06]。

一个影响复现的未决点是：物理页 3 的 Eq. (4)–(5) 与矩阵 \(A_p\) 对 PLL 旋转交叉项采用 \((-\omega x_2,+\omega x_1)\)，而物理页 4 的 Eq. (11) 与 Eq. (13) 版面上出现 \((+\omega x_2,-\omega x_1)\)。这是基于 PDF 的候选符号不一致，作者未作说明；正式实现前应以闭环模型、原始代码或作者确认消解，不能默认为两者等价 [pdf:E03] [pdf:E04]。

## § 7 — 实验设计与结论

**问题 1：显式反馈 PLL 状态是否扩大参数稳定范围？** 作者先令 \(L_g\) 从 10 mH 变化到 28 mH，对比包含与不包含 PLL-state feedback 的闭环极点；前者极点仍位于左半平面并保持更高阻尼，后者随弱网化逼近虚轴。随后将 \(P,Q\) 各自在 0–5 kW/kVAr 范围内变化，报告 proposed system 的极点保持在左半平面。这里验证的是给定连续模型和所扫参数范围内的 pole robustness，不是对任意电网阻抗的全局稳定证明 [pdf:E05]。

**问题 2：时域仿真是否重现稳定裕度差异？** 仿真先在 \(t=0.2~\mathrm{s}\) 将 \(Q^\*\) 从 0 提升到 2.9 kVAr，再在 \(t=0.3~\mathrm{s}\) 将 \(P^\*\) 从 0 提升到 4 kW，并重复 SCR=7、3.5、2、1 等工况。SCR 从 7 降到 1 时，proposed controller 的 settling time 从 15 ms 增至 50 ms且作者报告无 overshoot；conventional controller 越来越振荡并在 SCR=1.26 时失稳 [pdf:E06] [pdf:E07]。

**问题 3：不平衡电压下电流质量是否改善？** 在 \(P=3~\mathrm{kW}\)、\(Q=4~\mathrm{kVAr}\)、\(L_g=10~\mathrm{mH}\)、SCR=3.5 时，\(t=0.25~\mathrm{s}\) 施加 two-phase-to-ground fault，VUF=80%。proposed controller 的 current THD 保持低于 1%，conventional method 的 THD 高达 15% [pdf:E07]。但这项比较有一个重要归因限制：论文明确说明 conventional controller 使用不具 negative-sequence extraction 的 PLL，而 proposed controller 使用 UTSP；因此该结果同时混合了“PLL 状态反馈”和“序分量提取能力”两种变化，不能单独证明前者造成全部 THD 改善。

**问题 4：硬件实验能否在 stiff 与 extremely weak grid 上复现？** 实验平台包括 OP5700、OP8660、Semikron MiniSkiiP 三相 IGBT bridge（额定 40 kW）、150 V dc-link、52 V rms line-to-line grid simulator、60 Hz、5 mH L-filter，以及 \(L_g=5\) 或 20 mH。stiff-grid 工况为 SCR=5.1、\(S\approx280~\mathrm{VA}\)、\(Q=200~\mathrm{VAr}\)、\(P:0\to200~\mathrm{W}\)，两控制器表现几乎相同 [pdf:E08]。

在 \(L_g=20~\mathrm{mH}\)、SCR=1、\(S\approx350~\mathrm{VA}\) 的实验中，先以 \(P=0\) 将 \(Q:50\to100~\mathrm{VAr}\)：conventional controller 的 overshoot/settling time 为 82%/60 ms，proposed controller 为 25%/20 ms。再令 \(Q=165~\mathrm{VAr}\)、\(P:200\to300~\mathrm{W}\)：proposed controller 无明显 overshoot、settling time 25 ms，conventional controller 失稳；由 Eq. (18) 算得该点 \(Q_{\min}=161~\mathrm{VAr}\)，即接近 voltage-instability 边界 [pdf:E08] [pdf:E09]。Fig. 19 又在 F28335 DSP 上以 DSO 捕获同类 real-power step，proposed 波形受控而 conventional 发散 [pdf:E10]。

不得外推的范围同样清楚：实验功率约 280–350 VA，明显低于 40 kW bridge 额定值；论文没有报告高功率热应力、current limiting、dc-source dynamics、长期 grid-frequency drift、宽频阻抗不确定性、数字延迟或多变流器并联系统。

## § 8 — Take-aways

**5 句话：**

1. 论文把三相 PLL/UTSP 状态纳入 stationary-frame VSC 的 augmented LTI model，并用 multivariable full-state feedback 同时控制 current、servo 与 synchronization dynamics [pdf:E03] [pdf:E04]。
2. 核心机制不是“更强的 PLL”，而是显式关闭 PLL-state feedback 所遗漏的 \(\alpha\beta\) cross-coupling 通道。
3. 仿真中 proposed controller 在 SCR=1 保持稳定，而 matched-pole conventional controller 在 SCR=1.26 失稳；不平衡故障下报告的 current THD 为低于 1% 对最高 15% [pdf:E07]。
4. 低功率硬件实验在 SCR=1 且接近 reactive-power feasibility boundary 时复现了 proposed controller 的阻尼与稳定优势 [pdf:E08] [pdf:E09]。
5. 证据仍局限于连续模型、窄实验包络和未报告数字实现细节，且不平衡 THD 对比混合了控制反馈与 sequence-extraction 差异。

**3 句话：** 弱网使 PLL 变成闭环 plant 的一部分，忽略其状态会漏掉决定稳定性的耦合。把 PLL、VSC 与 sinusoidal servo 联合建模后做 MIMO state feedback，在论文的仿真和低功率实验范围内显著扩大了 SCR 稳定边界。要进入 EMT/FPGA 或工程部署，还必须补齐离散化、latency、数值格式、current limit 与等前端公平对比。

**1 句话：** 本文最值得保留的思想是“同步器状态必须进入控制设计”，而不是把 SCR=1 的单个平台结果直接视为普遍鲁棒性证明。

## § 9 — 最脆弱的假设

最脆弱的假设是：连续时间 augmented LTI model 中未建模的数字实现与功率级动态足够快、足够小，因此 LQR 所整形的极点仍能代表真实闭环。这个假设一旦不成立，PLL-state feedback 可能把 delayed/noisy synchronization state 直接注入高增益控制通道，纸面上的阻尼提升甚至可能反转为新的相位滞后和失稳。

论文提供的正面证据是：对 \(L_g=10\)–28 mH 和 \(P,Q\in[0,5]\) kW/kVAr 做了 pole sweep，并在 OP5700 与 F28335 上展示了稳定波形 [pdf:E05] [pdf:E08] [pdf:E10]。但它没有给出采样与计算 latency、离散闭环极点、PWM 同步方式、state-estimation noise、饱和/current limit、dc-link dynamics 或 fixed-point 误差；实验又只覆盖约 280–350 VA。基于这些证据，合理结论是“论文证明了所测平台和工况下可实现”，仍不能确认其 nominal continuous-time stability margin 能在高功率、不同硬件或延迟变化下保持。

前述 Eq. (5)/(11) 的 PLL 交叉项候选符号不一致进一步放大了这一风险：如果复现者选择了错误符号，连 nominal model 都无法唯一确定 [pdf:E03] [pdf:E04]。

## § 10 — 最小复现实验

一周内最有价值的最小复现不是搭建完整 40 kW 功率台，而是在 MATLAB/Simulink 或等价 state-space 工具中实现 Eq. (1)–(14) 的 averaged \(\alpha\beta\) model，并只验证“PLL-state feedback 是否在公平前端下扩大弱网稳定域”。

具体做法如下：

1. 使用 Table I 的 \(V_{dc}=600~\mathrm{V}\)、\(v_s=120~\mathrm{V_{rms}}\)、60 Hz、5 kHz PWM、\(R_t=0.1~\Omega\)、\(L_t=5~\mathrm{mH}\)、\(R_g=1~\mathrm{m}\Omega\)，令 \(L_g=4,10,17,28~\mathrm{mH}\)，对应论文给出的 SCR=7、3.5、2、1 [pdf:E05]。
2. 让两个 controller 共用完全相同的 UTSP、reference generator、servo、采样和限幅。proposed 分支使用完整 \(K_p\)，baseline 仅把 PLL-state feedback 的两列置零，再重新整定其余增益到接近的 stiff-grid poles，避免 sequence extractor 或 nominal bandwidth 成为混杂变量。
3. 重放 \(Q^\*:0\to2.9~\mathrm{kVAr}\)（0.2 s）和 \(P^\*:0\to4~\mathrm{kW}\)（0.3 s），记录闭环最大实部、\(P/Q\) overshoot、2% settling time，以及一次 \(Q\) step 在 \(P\) 通道诱发的峰值作为 cross-coupling 指标 [pdf:E07]。
4. 在连续模型通过后，仅增加 0、0.5、1、2 个采样周期的 measurement-to-actuation delay，并加入同幅值 PLL-state noise；不要同时改其他环节。

支持核心 claim 的结果是：同前端、同约束下，完整反馈在 SCR=1 仍稳定且 coupling metric 明显更低，而 baseline 接近论文报告的阈值时失去阻尼。反驳结果是：公平化 UTSP 后差距消失，或一个采样周期量级的合理延迟就使 proposed 分支不再优于 baseline。复现前必须先用 Eq. (4)–(6) 的状态矩阵自洽性解决 PLL 旋转项符号，不能直接复制 Eq. (11) [pdf:E03] [pdf:E04]。

## § 11 — 最强反例设计

最强反例应直接攻击“性能提升来自 PLL-integrated feedback”这一因果解释。构造两个除 PLL-state gain 外完全相同的控制器：二者使用同一 UTSP 正负序提取器、同一 reference generator、同一 nominal poles、同一 sampling/PWM latency 和同一 current limiter；然后在 SCR=1–2 范围内施加论文的 80% VUF two-phase-to-ground fault，同时叠加 grid-frequency ramp、PLL-state delay 和 measurement noise [pdf:E07]。

若 conventional controller 在获得同样的 negative-sequence extractor 后也把 THD 压到接近 1%，则原文 15% 对低于 1% 的差异主要来自 synchronizer capability，而不能归因于 PLL-state feedback。若 proposed controller 在 realistic delay 或 current saturation 下先于 baseline 失稳，则更直接否定“显式 PLL feedback 必然扩大真实系统稳定裕度”的机制外推。这个反例比简单换一个 SCR 更强，因为它同时去掉了原比较中的前端混杂，并把第 9 节最脆弱的 model-to-implementation 假设推到可观测的失败条件。

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty：** 把问题从“为 nominal augmented model 求一组最优增益”改写为“为 synchronization-state feedback 合成一个可验证的离散实现包络”。目标不再只是 SCR=1 时的漂亮 transient，而是同时给出允许的 grid-impedance 集合、sampling/latency 区间、state-noise 上界、current-limit 作用区间和 dc-link 变化范围；只要实现落在该包络内，就有可检查的稳定证书。

驱动需求是现有论文已经证明 PLL 状态值得反馈，却没有回答这些状态经过真实 ADC、计算、PWM 和饱和后还能延迟多久、误差多大。电力电子领域认可的价值将来自“控制律 + 可实现性证书 + 跨平台实验”三者同时成立，而非再增加一个补偿支路。可借鉴的相邻工具包括 sampled-data robust control、integral quadratic constraints、delay-dependent Lyapunov certificates 和 set-membership identification；它们可以把 delay、量化、阻抗不确定性和 limiter 作为有界算子进入同一个验证问题。

第一个能够证伪该想法的实验很简单：在同一 HIL plant 上自动扫 \(L_g\)、功率点、0–2 sampling-period delay 与 current limit，预先计算 certified safe envelope，再检查 envelope 内是否出现任何失稳。如果出现一次，证书或建模方法即被反驳。它与本文的实质区别在于：本文基于 nominal continuous-time model 用 LQR 整形性能，并以少数平台工况验证；候选方向把“实现不确定性下可证明的安全运行域”本身作为研究对象。由于本任务严格 PDF-only、未补充检索 2022 年后的相关工作，这里不主张该方向尚无人研究。
