# A State Variables Elimination-Based EMTP-Type Constant Admittance Equivalent Modeling Method for Power Electronic Converters

- 作者：Mingwang Xu, Wei Gu, Yang Cao, Shuaixian Chen, Fei Zhang, Wei Liu
- 出处：IEEE Transactions on Power Delivery, Vol. 40, No. 2
- 年份：2025
- DOI：10.1109/TPWRD.2025.3539334
- Zotero key：X98GS3IY

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的 EMT 仿真矛盾：电力电子变换器必须保留开关动作和内部储能动态，才能看见故障、电压跌落、闭锁等快速现象；但若把每个开关、内部节点、电感和电容都放进全网节点方程，系统规模和每步求解代价会迅速膨胀。作者给出的动机例子是，在 PSCAD/EMTDC 中，以 10 μs 步长仿真一个 100 MW 光伏电站 1 s，耗时会超过 3 h。[pdf:E01](_evidence/E01-p001-abstract-motivation.png)（PDF 物理页 1，Introduction A）

作者希望得到一种 **EMTP-type constant admittance equivalent**。这里的含义不是把变换器简化成一个静态电阻，而是：对外仍呈现标准的“导纳矩阵 + 历史电流源”离散伴随模型，使它能直接并入外部电网节点方程；同时让导纳矩阵在开关状态变化时保持不变，把动态和开关影响放进每步更新的历史源。这样，全网导纳矩阵可以预先组装或分解，不必因为每次开关动作而重新求逆；内部电容电压、电感电流等状态仍被保留，因此模型仍能描述器件级暂态，而不只是平均外特性。[pdf:E01](_evidence/E01-p001-abstract-motivation.png)（PDF 物理页 1，Abstract）

论文的核心技术 claim 是：通过状态变量消元、矩阵拆分以及端口输出方程，可以生成低阶、恒定导纳的端口等效；与经典 node elimination method（NEM，节点消元法）相比，它减少串行回代和变化导纳矩阵求逆，并在物理实验、HIL、并联变换器、PET 和改造 IEEE 118 节点系统中保持较小误差和更高速度。[pdf:E02](_evidence/E02-p002-prior-work-contributions.png)（PDF 物理页 2，Contribution）

## § 2 — 前人工作与不足

论文把既有路线分成几类，问题并不只是“以前不够快”，而是不同路线分别丢掉了内部动态、恒定导纳或易接入性。

第一类是开关级离散等效和低维模型。response matching、compensation current source，以及面向 MMC/PET 的低维模型能够加速仿真，但作者指出已有低维模型并不具有恒定导纳矩阵。聚类等效把动态相近的光伏单元合并，适合电站级简化，却没有充分保留单台变换器内部动态。传统 average-value model（AVM）通过对开关周期取平均显著提速，但忽略真实开关动作，主要描述平均外特性；改进 AVM、event-driven 和 shifted-frequency 大步长方法改善了某些精度或效率问题，仍没有同时给出本文所需的恒定导纳。[pdf:E01](_evidence/E01-p001-abstract-motivation.png)（PDF 物理页 1，Literature Review）；[pdf:E02](_evidence/E02-p002-prior-work-contributions.png)（PDF 物理页 2，Literature Review）

第二类是 NEM。它从完整节点方程中消掉内部节点，能够形成低阶外部等效并保留内部节点信息，已用于 MMC、PET 和海上风场；代价是求解链仍高度串行：形成外部等效之后，还要回代内部节点，再求储能支路变量，才能更新历史电流源。更关键的是，内部子矩阵随开关变化时，NEM 需要反复处理变化导纳矩阵。[pdf:E02](_evidence/E02-p002-prior-work-contributions.png)（PDF 物理页 2，Literature Review）；[pdf:E05](_evidence/E05-p005-complexity-analysis.png)（PDF 物理页 5，Fig. 3、Eq. 15–18）

第三类是 NAM、SSM 和 SSN 三种求解视角。nodal analysis method（NAM）容易生成可接入电网的等效电路，但沿“网络—支路—历史源”逐层回算；state-space method（SSM）直接维护储能状态、更新历史量方便，却不容易生成低阶端口电路；state-space nodal（SSN）通过子系统状态方程和节点耦合减小全局节点矩阵。作者的改变不是再做一次普通节点消元，而是直接建立“端口节点电压—状态变量—端口注入电流”的关系，试图同时取得 NAM 的端口接口和 SSM 的状态更新能力。[pdf:E02](_evidence/E02-p002-prior-work-contributions.png)（PDF 物理页 2，Introduction C 与 Section II-A）

论文还比较了三种恒定导纳开关模型：L/C switch model 会引入虚拟功率损耗，高频时可能不可用；文献 [5] 的模型解决了虚拟损耗，但系统规模增大时节点矩阵仍大；基于 time-delay 的 switch-function 模型不能反映导通损耗，延迟还会带来接口误差和数值稳定问题。本文用 binary resistor 表示开关，目标是在不引入上述代价的同时把开关影响隔离到历史项。[pdf:E05](_evidence/E05-p005-complexity-analysis.png)（PDF 物理页 5，Section II-E）

## § 3 — 重建作者的思考路径

下面是基于论文问题陈述和推导顺序重建的思考路径，不是作者逐字说明。

1. 若最终模型要无缝接入 EMTP/PSCAD 外网，它对外最好仍是 Norton 形式：端口电流等于端口导纳乘端口电压，再加历史电流源。这样外网求解器不必理解变换器内部结构。
2. 若直接消内部节点，开关变化会进入被求逆的内部导纳子矩阵，且更新历史源还要回代内部节点和支路。真正需要保留的“记忆”其实是电容电压和电感电流，因此可以绕开内部节点，把储能状态 \(x\) 当作中间层。
3. 为了让被求逆的部分不随开关变化，把状态矩阵拆为恒定部分 \(A_\alpha\) 和开关相关部分 \(A_\beta\)。对 \(A_\alpha\) 用 trapezoidal integration，对 \(A_\beta\) 用 forward Euler，于是下一步状态前面的矩阵只含 \(M-\frac{\Delta t}{2}A_\alpha\)，可以预先求逆；开关状态留在显式历史项中。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 3、6）
4. 再补一条端口输出方程 \(i_s=Px\)，就能在离散方程中消去未来状态 \(x(t+\Delta t)\)，直接得到端口 Norton 等效。外网先求端口电压，随后用同一组常量矩阵反解状态，并用新状态更新下一步历史源。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 4、7）；[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 8、11、12）
5. 最后，把这种结构应用到可重复模块：PV generation unit（PVPGU）由 boost、VSC、filter、transformer 的状态块拼成；CHB-DAB/PET 由模块端口串并联。模块内部复杂度被状态维数吸收，外网只看少数端口，因此规模越大，避免重复内部节点求解的收益越明显。[pdf:E06](_evidence/E06-p006-pv-application.png)（PDF 物理页 6，Eq. 21–26）；[pdf:E07](_evidence/E07-p007-chb-application.png)（PDF 物理页 7，Fig. 6–8）

## § 4 — 核心 Intuition

变换器内部真正携带跨时间步记忆的是电感电流和电容电压，而不是每一个内部节点电压。本文把这些状态保留下来，却在端口处把“未来状态”消去：外网看到一副不随开关动作改变的导纳骨架，开关与内部动态只通过历史电流源注入。换句话说，作者不是消灭内部物理，而是把内部物理从“每步重建网络”改写成“每步推进状态”。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Fig. 1、Eq. 3–7）

## § 5 — 具体方法与完整 Pipeline

以二电平 VSC 接入外部交流网络为例，完整流程如下。

1. **选状态与端口。** 用电容电压 \(u_C\) 和电感电流 \(i_L\) 组成状态 \(x\)，外部端口节点电压组成 \(u_n\)，端口注入电流组成 \(i_s\)。若 DC 端口有电容，作者把 DC 端口注入电流 \(i_d\) 加进改写后的状态向量。开关用上下桥臂 binary resistors \(r_k\) 表示，二电平例子的状态包括三相电感电流和两个 DC 电容电压。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Fig. 2、Eq. 1–5）
2. **拆分状态矩阵。** 写成 \(M\dot x=(A_\alpha+A_\beta)x+Bu_n\)。\(A_\alpha\) 放置不会随开关改变的项，\(A_\beta\) 放置开关 on/off 相关项；另写端口输出 \(i_s=Px\)。\(B\) 和 \(P\) 是由端口连接关系形成的 0/1 系数矩阵。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 3–5）
3. **混合离散并消去未来状态。** 恒定部分采用 trapezoidal integration，开关相关部分采用 forward Euler。把离散状态方程与输出方程联立，消去 \(x(t+\Delta t)\)，得到 \(i_s(t+\Delta t)=Y_nu_n(t+\Delta t)+i_h(t)\)。\(Y_n\) 只由 \(M,A_\alpha,B,P,\Delta t\) 决定；开关状态通过 \(A_\beta\) 进入 \(R\) 和历史源 \(i_h\)。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 6–7）；[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 8）
4. **生成低阶端口电路并与外网联立。** \(Y_n\) 的互导纳变成端口之间的等效支路，每个端口再接相应历史电流源。这个端口组件可与外部电网共同进入同一个节点方程。作者的 PVPGU 示例把 boost、VSC、filter、transformer 的状态块合并，形成 5 端口等效；单个 PVPGU 的导纳矩阵维数比原电路减少 10，作者估计 100 MW PVPP 可减少 1000 维以上。[pdf:E06](_evidence/E06-p006-pv-application.png)（PDF 物理页 6，Fig. 5、Eq. 21–26）；[pdf:E07](_evidence/E07-p007-chb-application.png)（PDF 物理页 7，Fig. 6–7）
5. **求外部节点电压，再反解状态。** 外网求出 \(u_n(t+\Delta t)\) 后，用常量矩阵 \(K\) 和历史项反解 \(x(t+\Delta t)\)。新端口电压和新状态直接形成下一步历史电流源，不再回代所有内部节点和支路。需要内部量时，可从状态恢复开关臂或变压器端口电压、电流，因此“低阶端口”不等于丢弃所有内部可观测量。[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 11–12）；[pdf:E08](_evidence/E08-p008-flowchart-validation.png)（PDF 物理页 8，Eq. 33、Fig. 10）
6. **处理数值振荡和闭锁。** 作者把非状态量突变导致的历史源不合理跳变视为 trapezoidal numerical oscillation 的来源；检测到振荡后切换 backward Euler。闭锁时根据二极管上一时刻状态以及二极管电流/端电压判断导通状态，用它更新 binary-resistor 比值，不额外改变端口等效电路。[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Section II-C/D、Eq. 13–14）
7. **模块化复用。** 对 CHB-DAB，作者先把高频变压器离散为端口导纳与历史源，再把 H-bridge、DAB 状态拼成模块方程；多个模块可按输入串联、输出并联方式组成 PET 端口网络。[pdf:E07](_evidence/E07-p007-chb-application.png)（PDF 物理页 7，Eq. 27–30）；[pdf:E08](_evidence/E08-p008-flowchart-validation.png)（PDF 物理页 8，Fig. 9、Eq. 31–33）

论文实际报告的执行环境包括 PSCAD/EMTDC 离线仿真、低功率物理平台和 RT-LAB HIL 平台。它没有报告 FPGA 上的矩阵映射、流水线、定点/浮点格式、位宽、LUT/BRAM/DSP 资源或板级确定延迟；因此不能从“恒定导纳、可预计算”直接外推 FPGA 实现效果。[pdf:E09](_evidence/E09-p009-experiment-hil.png)（PDF 物理页 9，Fig. 11–14）

## § 6 — 核心数学推导

先从物理状态方程开始。\(M\) 的对角块保存电容和电感参数，\(x\) 保存相应电压、电流；端口电压是输入：

\[
M\dot x(t)=\left(A_\alpha+A_\beta\right)x(t)+Bu_n(t),\qquad i_s(t)=Px(t).
\]

这里 \(A_\alpha\) 是恒定部分，\(A_\beta\) 是开关状态相关部分。它们的拆分是整篇论文最关键的代数动作，因为它决定“哪一部分进入每步需要求逆的矩阵”。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 3–4）

作者对 \(A_\alpha\) 和端口输入使用梯形积分，对 \(A_\beta\) 使用前向 Euler：

\[
\begin{aligned}
\int_t^{t+\Delta t}M\dot x\,dt
\approx {}& \frac{\Delta t}{2}A_\alpha[x(t+\Delta t)+x(t)]\\
&+\Delta t A_\beta x(t)
+\frac{\Delta t}{2}B[u_n(t+\Delta t)+u_n(t)].
\end{aligned}
\]

因此未来状态前的系数为 \(M-\frac{\Delta t}{2}A_\alpha\)，不含 \(A_\beta\)。定义

\[
Q=\left(M-\frac{\Delta t}{2}A_\alpha\right)^{-1},\qquad
R=M+\frac{\Delta t}{2}A_\alpha+\Delta t A_\beta,
\]

联立 \(i_s=Px\) 并消去 \(x(t+\Delta t)\)，得到

\[
i_s(t+\Delta t)=Y_nu_n(t+\Delta t)+i_h(t),
\]

\[
Y_n=\frac{\Delta t}{2}PQB,\qquad
i_h(t)=PQRx(t)+\frac{\Delta t}{2}PQBu_n(t).
\]

物理上，\(Y_n\) 是外网每一步都看到的端口“静态骨架”；\(i_h\) 携带电感、电容的历史能量以及本步开关状态。只要 \(M,A_\alpha,B,P,\Delta t\) 固定，\(Q\) 和 \(Y_n\) 就固定；\(A_\beta\) 虽随开关变化，却只进入 \(R\) 和历史源。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 6–7）；[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 8 与 Constant Admittance Matrix）

外部节点电压求出后，状态更新为

\[
x(t+\Delta t)=Ku_n(t+\Delta t)+\varphi(t),
\]

\[
K=\frac{\Delta t}{2}QB,\qquad
\varphi(t)=QRx(t)+\frac{\Delta t}{2}QBu_n(t).
\]

这一步解释了“state variables elimination”并不是永久删除状态：状态只从全网联立方程中被消去，随后仍用端口解反算并推进。[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 11–12）

离散稳定性用状态转移矩阵 \(\Phi=QR\) 的谱半径判断，论文写出的充分必要条件是 \(\rho(\Phi)<1\)。参数扫描显示，在其指定范围内，电容对步长的约束比电感和负载更强；对表中 \(C=100\sim8000~\mu\text{F}\) 的扫描，作者给出不超过 112 μs 的稳定步长结论。这个数字只适用于表中参数范围，不能当作所有变换器的统一步长上限。[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Table I、Eq. 9–10）

复杂度分析中，NEM 对 \(n\) 个内部节点的作者计数为

\[
T_{\text{sum}}^{\text{NEM}}
=\frac{2}{3}n^3+(2m+3)n^2+4nm^2+nm-\frac{2}{3}n
\sim O(n^3),
\]

而本文方法对 \(q\) 个改写后状态、\(p\) 个 DC 端口电容的计数为

\[
T_{\text{sum}}^{\text{proposed}}=(2p+3)q^2+2pq\sim O(q^2).
\]

在作者用于说明的 CHB-DAB 电路中，NEM 按 \(m=4,n=6\) 计为 488 次操作，本文方法按 \(p=1,q=6\) 计为 195 次操作。这里比较的是作者定义的建模/求解操作计数和不同维度变量的渐近式，不应把 \(O(n^3)\) 对 \(O(q^2)\) 直接等同于任意平台上的固定倍数 wall-clock 加速。[pdf:E05](_evidence/E05-p005-complexity-analysis.png)（PDF 物理页 5，Eq. 15–18）；[pdf:E06](_evidence/E06-p006-pv-application.png)（PDF 物理页 6，Eq. 19–20、Fig. 4）

## § 7 — 实验设计与结论

**问题 1：端口等效能否跟随真实变换器的大信号变化和触发异常？**  
作者搭建低功率二电平 VSC 物理平台，参数为 50 V DC、1360 μF DC 电容、5 kHz 开关频率和 5 mH AC 电感；一组实验把负载电压参考从 20 V 改到 10 V，另一组丢失 A 相上桥臂触发脉冲。实验波形与 proposed model、detailed model 的仿真波形趋势一致。论文没有为这两组物理实验给出统一数值误差，因此能支持的是“关键波形形状和操作特性一致”，不是已量化到某个百分比的硬件精度。[pdf:E09](_evidence/E09-p009-experiment-hil.png)（PDF 物理页 9，Fig. 11–13）

**问题 2：方法能否用于高频实时仿真？**  
作者在 RT-LAB 上实现 DAB 模型，以 1 μs 步长实时运行；DAB 参数包括 1000 V DC、100 μF DC 电容、10 kHz 开关频率、10 Ω 负载、原副边各 5 μH 漏感和 1 H 励磁电感。HIL 波形与离线仿真对齐，支持“该算法可在所用实时平台和工况上运行”。论文没有给出 deadline miss、CPU 核占用或端到端 latency，因而不能外推更大系统仍满足 1 μs 实时约束。[pdf:E09](_evidence/E09-p009-experiment-hil.png)（PDF 物理页 9，Fig. 14、Section V-B）

**问题 3：多变换器故障暂态下，低阶等效是否仍接近详细模型？**  
三变换器并联系统采用 10 μs 步长、2 s 仿真，依次施加 AC 母线 A 相接地 0.01 s、converter 3 DC 短路 0.05 s、负载切除 0.1 s。与 detailed reference model（RM）相比，三组工况的作者汇总 MRE 分别小于 1.95%、1.41% 和 0.23%。五模块 PET 采用 1 μs 步长，在 1.5 s 发生 DC 接地并在 0.02 s 后清除，所示量的 MRE 小于 1.48%。这些实验回答的是已测试故障和控制设置下的波形精度，不能证明所有开关事件、控制器或故障阻抗下都保持同一误差界。[pdf:E10](_evidence/E10-p010-multimodule-accuracy.png)（PDF 物理页 10，Table III、Fig. 15–16）；[pdf:E11](_evidence/E11-p011-efficiency-results.png)（PDF 物理页 11，Fig. 17–19）

**问题 4：规模增大时是否真的提速？**  
作者在 Intel Core i5-12600K 3.70 GHz、16 GB RAM 的 PC 上改变并联变换器数量，分别测 RM、NEM 和本文 EM。50 台变换器时，论文给出的稳健结论是 EM 比 RM 快 7 倍以上，且比 NEM 快 2 倍以上，规模增大时 speed-up ratio 上升。[pdf:E11](_evidence/E11-p011-efficiency-results.png)（PDF 物理页 11，Fig. 20、Section V-C2）

这里存在一处必须保留的原文内部歧义：Section V-C2 的文字把 SR1 定义为 RM/EM、SR2 定义为 RM/NEM，并声称 50 台时 SR1>7、SR2≈3；但 Fig. 20 的图例位置以及 Table IV 的列标题却把 SR1 标为 RM/NEM、SR2 标为 RM/EM。Table IV 的原始时间可直接核算：2 kHz 时 RM/NEM/EM 分别为 5310.223/2095.589/801.221 s，对应 RM/NEM=2.534、RM/EM=6.628；5 kHz 时为 8762.267/2266.494/1058.855 s，对应 3.866 和 8.275。因此本卡不依赖 SR1/SR2 名称，只采用原始时间与“EM 对 RM、NEM 均更快”的结论。[pdf:E11](_evidence/E11-p011-efficiency-results.png)（PDF 物理页 11，Fig. 20 及其正文）；[pdf:E12](_evidence/E12-p012-ieee118-conclusion.png)（PDF 物理页 12，Table IV）

**问题 5：大网络与更高开关频率下是否仍保持精度和效率？**  
作者把 modified IEEE 118-node system 中若干发电机替换为 PVPP，节点 34 在 0.6 s 发生持续 0.02 s、接地电阻 1 Ω 的单相接地故障。节点 34 电压、节点 19 功率、节点 36 电压和节点 40 功率相对 RM 的 MRE 分别为 0.52%、0.81%、0.35% 和 1.0%。Table IV 还显示从 2 kHz 升到 5 kHz 时三种模型都变慢，但 EM 相对 RM 和 NEM 的速度优势变大。该结果支持论文已建模 PVPP 和该故障场景下的规模收益，不等于验证了任意 118 节点电力电子化配置。[pdf:E12](_evidence/E12-p012-ieee118-conclusion.png)（PDF 物理页 12，Fig. 21–22、Table IV）

## § 8 — Take-aways

**5 句话：**

1. 本文把变换器内部储能动态放进状态变量，把外网接口写成恒定导纳与历史电流源，从而避免每次开关动作都重构全网导纳。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)
2. 恒定导纳成立的关键不是普通代数消元，而是把恒定状态矩阵隐式离散、把开关相关矩阵显式处理，使被求逆的 \(Q\) 不含开关状态。[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)
3. 外网求完端口电压后，内部状态仍可反解并用于更新历史源，所以它在降低端口阶数的同时保留了主要内部动态。[pdf:E08](_evidence/E08-p008-flowchart-validation.png)
4. 论文在物理实验、1 μs HIL、多变换器故障和 modified IEEE 118-node system 中给出了精度证据，并在 50 台变换器实验中报告了相对 RM 超过 7 倍、相对 NEM 超过 2 倍的效率。[pdf:E09](_evidence/E09-p009-experiment-hil.png)；[pdf:E11](_evidence/E11-p011-efficiency-results.png)
5. 最关键的边界是：导纳恒定依赖线性/分段线性状态结构和特定矩阵拆分；论文没有验证磁饱和、器件强非线性、FPGA 实现资源或普适实时 deadline。

**3 句话：**

本文把“每步变化的内部网络”重写成“恒定端口导纳 + 每步推进的内部状态”。这种表示减少 NEM 的变化矩阵求逆和内部节点回代，并在论文测试的 PVPGU、CHB-DAB/PET 与多变换器系统中取得较小 MRE 和规模化加速。它最值得继续追问的不是还能否再快一点，而是当强非线性使恒定矩阵拆分失效时，能否仍保持固定外网因子分解和可证明的误差/稳定性。

**1 句话：**

用状态记住内部能量、用恒定导纳连接外网，是本文同时保留 EMT 暂态和降低全网重复求解成本的核心。

## § 9 — 最脆弱的假设

最脆弱的假设是：**所有会随时间、开关和工作点变化的因素，都能被隔离到 \(A_\beta\) 与历史源，而 \(M,A_\alpha,B,P\) 保持恒定。** 只要这个假设成立，\(Q=(M-\frac{\Delta t}{2}A_\alpha)^{-1}\) 和 \(Y_n=\frac{\Delta t}{2}PQB\) 就可以预计算；一旦电感、电容、端口映射或隐式部分随状态变化，恒定导纳这一核心贡献便直接失效，至少需要重新线性化、更新导纳或引入迭代。[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 8 与 Constant Admittance Matrix）

论文通过 binary-resistor switch model 把开关变化放进 \(A_\beta\)，并假定上下桥臂电阻和 \(r_{\text{sum}}\) 通常固定；闭锁二极管也用离散导通状态更新这个比值。它还在 PVPGU 和 CHB-DAB 模块上展示了同一结构，说明该假设对所建线性/分段线性模型可操作。[pdf:E03](_evidence/E03-p003-state-equations-port-equivalent.png)（PDF 物理页 3，Eq. 5）；[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Eq. 14）

证据缺口同样清楚：CHB-DAB 变压器推导明确忽略 copper loss、iron loss 和 core saturation；物理实验与 HIL 也没有系统扫过磁饱和、温度依赖导通电阻、结电容、二极管反向恢复或控制器导致的状态依赖参数。也就是说，论文证明了这套拆分在作者选定模型和工况中的有效性，却没有证明真实器件的强非线性仍可全部留在历史源而不污染恒定导纳。[pdf:E07](_evidence/E07-p007-chb-application.png)（PDF 物理页 7，Section IV-B、Eq. 27）

## § 10 — 最小复现实验

一周内最有价值的最小复现，不需要重建 118 节点系统；只需做一个二电平 VSC 的 detailed reference model 与本文 EM，并验证“导纳真的不随开关变，同时波形没有因显式开关项而失真”。

**数据和模型。** 使用论文物理实验的 50 V DC、1360 μF DC 电容、5 kHz 开关频率、5 mH AC 电感和 V/F 控制；保留 binary-resistor 六开关模型、两个 DC 电容状态和三相电感状态。设置两种事件：负载电压参考由 20 V 降到 10 V，以及 A 相上桥臂触发脉冲丢失。[pdf:E09](_evidence/E09-p009-experiment-hil.png)（PDF 物理页 9，Fig. 12–13）

**实现。**

1. 按 Eq. 3–8 构造 \(M,A_\alpha,A_\beta,B,P,Q,R,Y_n,i_h\)，每步先用 \(Y_n,i_h\) 与外部负载联立求端口电压，再按 Eq. 11–12 更新状态。
2. 用同样开关电阻、控制信号、步长和元件参数建立逐开关详细节点模型。两种模型必须共用事件时刻，避免把采样错位误认为模型误差。
3. 在所有 64 种二电平桥臂开关组合中记录 \(Y_n\) 的数值哈希或最大元素差；另记录 EM 与 RM 的 A 相电压、三相电感电流、DC 电容电压、MRE、单步计算时间，以及是否触发数值振荡/Backward Euler。
4. 可选地复制为 1、3、5、10 个并联单元，只测试端口矩阵规模和运行时间增长，不必复现完整控制系统。

**支持标准。** 如果所有开关状态下 \(Y_n\) 在机器精度内完全相同，两种事件的主要波形无相位错位，MRE 保持在论文多模块实验约 2% 的量级以内，并且模块数增加时 EM 相对详细模型的速度优势上升，则支持核心 claim。**反驳标准。** 若 \(Y_n\) 随开关状态变化、触发丢失时 EM 出现详细模型没有的能量增长/振荡、或在相同离散规则下误差显著超过论文所示量级，则应优先怀疑矩阵拆分或显式处理 \(A_\beta\) 的有效范围，而不是先扩大系统规模。

## § 11 — 最强反例设计

最强反例不是再找一个普通短路，而是让“恒定导纳所依赖的线性储能参数”主动失效。选择论文的 CHB-DAB/PET，因为其变压器推导明确忽略 core saturation；建立包含非线性励磁曲线、iron loss、温度依赖导通电阻和二极管反向恢复的详细参考模型，再让磁通从未饱和逐步进入深饱和，同时在电流过零附近交替施加移相变化、闭锁与恢复。[pdf:E07](_evidence/E07-p007-chb-application.png)（PDF 物理页 7，Section IV-B）；[pdf:E04](_evidence/E04-p004-stability-constant-admittance.png)（PDF 物理页 4，Blocking Mode Analysis）

攻击逻辑是：饱和使励磁电感随状态变化，温升和器件动态使等效电阻/电容随历史与电压变化，于是 \(M\) 或隐式状态矩阵不再恒定。若仍强制使用标称 \(Y_n\)，变化只能被塞进历史源，可能造成能量不守恒、相位误差或稳定性恶化；若为了恢复精度而更新 \(Q,Y_n\)，则“恒定导纳、预计算、不重求逆”的核心优势被破坏。

实验应同时报告三条曲线：与详细模型的 MRE/能量误差、最坏步长稳定边界、每次需要更新或重新分解导纳的次数。最有力的反驳结果是出现一个可重复阈值：饱和程度或温升超过该阈值后，固定 \(Y_n\) 的误差/振荡突然增大，而更新 \(Y_n\) 才能恢复；这会证明论文当前 claim 只适用于可被固定矩阵拆分覆盖的分段线性设备，而不是一般 power electronic converter。

## § 12 — Follow-up Research Idea

从本文选择的验证证据可以推断，这个领域认可的高影响工作至少要同时满足：端口模型可接入现有 EMT 求解器、故障暂态精度可量化、规模增长时有实际 wall-clock 收益，并最好在物理实验或 HIL 上证明工程可运行。只给出一个更小的矩阵，或只在离线单机波形上相似，都不足以支撑强工程价值。[pdf:E09](_evidence/E09-p009-experiment-hil.png)（PDF 物理页 9，物理/HIL 验证）；[pdf:E11](_evidence/E11-p011-efficiency-results.png)（PDF 物理页 11，Fig. 20）

**候选研究想法：从“恒定导纳等效”改写为“固定网络因子分解 + 有误差证书的非线性动态残差端口”。** 这不是声称已有 novelty 的结论；本卡未做外部相关工作检索，因此它只是由本文最脆弱假设推出的候选方向。

**（a）未满足的需求。** 真实高频变换器含磁饱和、温度依赖损耗、结电容与二极管恢复。希望外网仍只做一次主矩阵因子分解，但内部模型不必假装 \(M,A_\alpha\) 永远恒定，并且能给出“何时误差仍可接受、何时必须更新骨架”的在线判据。

**（b）潜在研究价值。** 目标从“对理想分段线性模型精确保持恒定导纳”转为“对强非线性模型保持固定全网求解骨架，同时给出稳定性和误差边界”。如果成立，它会扩大方法可用设备范围，并把效率—精度折中从经验波形比较提升为可验证契约。

**（c）可借鉴的相邻工具。** 可以把非线性部分表示为端口历史源中的低秩/稀疏动态残差，仅在残差超过能量或谱半径阈值时做局部更新；同时使用 energy-based passivity check 约束残差不能向外网无故注入能量。这里的工具是候选设计，不是本文已经采用的方法。

**（d）第一个证伪实验。** 使用 §11 的饱和 CHB-DAB，在 1 μs 步长下扫励磁曲线、移相角、闭锁时刻和模块数。若固定全网因子分解的残差模型不能在不迭代爆炸的情况下同时保持低于详细模型约 2% 的暂态误差、无虚假能量增长和实时 deadline，那么这个研究目标即被首轮证伪。

**（e）与本文的实质区别。** 本文通过矩阵拆分让 \(Y_n\) 在既定线性/分段线性模型中严格恒定；候选方向允许内部参数真正随状态变化，但要求全网求解骨架保持不变，并以残差界和能量/稳定性证书决定何时局部修正。改变的是问题定义和验收对象，不是给现有 pipeline 再附加一个补偿模块。
