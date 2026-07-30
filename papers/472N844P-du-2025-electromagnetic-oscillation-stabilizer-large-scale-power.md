# Electromagnetic Oscillation Stabilizer for Large-Scale Power Electronics-Dominated Power Systems in LTP Framework–Part II: Generalized Periodic Stabilization Control and Design

**作者**：Buyang Du, Jianhang Zhu, Jiabing Hu, Zeren Guo, Yingbiao Li, Jianbo Guo  
**出处**：IEEE Transactions on Power Electronics, Vol. 40, No. 11, pp. 17186-17202  
**年份**：2025  
**DOI**：10.1109/TPEL.2025.3588607  
**Zotero key**：472N844P  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。证据标记中的页码是 PDF 物理页。论文报告了 RT-LAB 电磁暂态仿真和 DSP-in-the-loop HIL，但 FPGA 实现、FPGA 资源、定点格式、实时仿真步长和求解器配置均未报告。

## § 1 — 研究问题与重要性

这篇 Part II 处理的是 EOS（electromagnetic oscillation stabilizer，电磁振荡稳定器）设计中的第二步：在 Part I 已经选择安装位置之后，怎样为大规模、线性时周期（linear time-periodic, LTP）的电力电子主导电力系统设计控制结构和参数，使指定的弱阻尼或不稳定 Floquet exponents 被放到期望位置。作者要求这个方案同时适用于含大量异构设备的系统、能够处理频率耦合，并且在运行点改变后仍能抑制振荡。摘要把贡献概括为 generalized periodic stabilization control（PSC）以及据此构造的 PSC-based EOS，并声称它比对比的 virtual impedance（VI）方案有更大的稳定裕度和更好的跨工况表现。[pdf:E01]

这个问题重要，不只是因为“出现振荡就要加阻尼”。在这类系统中，换流器的开关、坐标变换、正负序和高低频耦合使小信号模型天然呈周期变化；若仍用线性时不变（LTI）模型和时不变控制器，控制器可能无法任意配置 LTP 系统的特征值。与此同时，大系统中存在多个可选 PCC 和大量状态，若控制设计依赖完整状态反馈、全阶周期 Riccati 方程或高维 Grammian 运算，理论上可行也可能无法计算或实施。作者因此把“LTP 下准确配置目标模态”与“只对少数危险模态做低维设计”结合起来。[pdf:E02]

## § 2 — 前人工作与不足

论文把已有抑振方法分为附加装置、参数优化、控制结构增强和 EOS 四类。附加滤波器或 STATCOM 成本高；参数优化受动态性能和功率平衡约束；PLL 对称化或嵌入滤波器通常只针对特定振荡，整体阻尼提升有限。EOS 的优势是尽量不扰动稳态运行而显著增加目标模态阻尼。[pdf:E01]

作者重点批评了 VI-based EOS 的四类不足。第一，LTI state-space、SISO impedance 和二阶阻抗矩阵不能完整表达高低频耦合；第二，大型网络有多个 PCC，不同 PCC 会把 EOS 放到不同设备，但缺少系统性的最优 PCC 选择理论；第三，阻抗稳定判据可能受零极点相消或非临界不稳定特征值影响；第四，时不变控制器理论上不能在一般 LTP 系统中任意配置特征值。因此，一个在某个接入点和工况有效的 VI 参数，不能自动推出在另一工况仍有稳定裕度。[pdf:E02]

已有 PSC 也并非直接可用。Floquet modal control 要求输入数等于状态数；SSPH（sampled state periodic hold）要访问全状态；已有 static output feedback 依赖额外假设；auxiliary-system 方法只给 least-squares 意义的结果；周期 Riccati、Grammian 和积分方程又会带来高维计算。论文由此把真正缺口定义为：只要求目标弱阻尼模态对所选输入/输出可控、可观，并把控制器计算限制在目标模态维数，而不是整个系统维数。[pdf:E02]

## § 3 — 重建作者的思考路径

可以从论文之前已有的三条线索重建这条路线。第一，Floquet-Lyapunov 变换把周期系统

$$
\dot{x}(t)=A(t)x(t)+B(t)u(t),\qquad y(t)=C(t)x(t)
$$

变成具有常矩阵 \(J\) 的坐标系；\(J\) 的对角块对应 Floquet exponents，因此“抑制哪个振荡模态”可以转成“移动 \(J\) 中哪一对指数”。第二，LTP controllability/observability 可以由 reachability/observability Grammian 或 Floquet 模态对输入/输出的耦合判断。第三，SSPH 已证明周期 full-state feedback 可以任意配置可控 LTP 系统的 monodromy eigenvalues，但其全状态和全维计算不适合大系统。[pdf:E03]

沿这三条线索，一个自然的研究推进是：先把 SSPH 从 full-state feedback 改造成 output feedback；再利用 Part I 的 modal controllability（MOC）和 modal observability（MOO）只保留危险模态、最佳控制位置和反馈信号；最后用窄带滤波把其他模态对反馈通道的污染压低。这样，原先“全系统必须可控可观”的要求就缩小为“关心的模态对所选通道可控可观”，控制器维数也从 \(n\) 降到危险模态数 \(n_{pd}\)。论文在 Theorem 5-7、extended SSPH 和 Fig. 1-2 中把 output-feedback 这一中间台阶形式化。[pdf:E04]

这里要区分论文事实与重建：上面的三条技术前提和定理是论文明确给出的；“先改 output feedback、再做模态截取、最后加窄带隔离”是根据章节组织重建的思考路径，不是作者自述的发现过程。

## § 4 — 核心 Intuition

核心 intuition 是：不要为 393 个状态设计一个 393 维周期控制器，只围绕真正危险的那一对 Floquet 模态构造一个可观测、可控制的低维 lifted system。周期输入核在每个周期内按目标模态的状态转移形状施加控制，周期输出积分从测量中提取该模态；bandpass filter 再尽量隔离其他模态，最终由低维 estimator-based state feedback 把目标 monodromy eigenvalues 放到期望位置。[pdf:E06]

与 VI 的差别不只是调参方式。VI 通过时不变阻抗整形间接改变系统动态，而 PSC 直接在 LTP/Floquet 框架中针对目标模态做周期 eigenvalue assignment；因此它有机会获得更大的名义稳定裕度，但代价是模型、周期同步、滤波和控制结构都更复杂。

## § 5 — 具体方法与完整 Pipeline

以论文的真实 PEPS 为例，完整 pipeline 如下。

1. 构建大规模 LTP-SSM，计算 state transition matrix（STM）、Floquet exponents 和 real Floquet-Lyapunov transformation。论文称该 LTP-SSM 同时包含 VSC、LCC 的 AC 侧与 DC 侧动态，但具体建模过程和主要参数转引 Part I，本 PDF 未完整给出。[pdf:E08]
2. 使用 Part I 的 MOC/MOO，从危险模态出发选择控制位置和反馈量。本例选择 PV plant T 的 VSC，以论文指定的 \(i_f\) 分量作反馈、以 \(U_t^c\) 通道作控制位置；PSC 不需要先人为切分 PCC。[pdf:E08]
3. 在 Floquet 坐标中只保留目标弱阻尼模态 \(z_1\)，把其他模态 \(z_2\) 当作衰减更快的扰动。简化系统的状态数等于目标弱阻尼特征值数 \(n_{pd}\)。[pdf:E06]
4. 设计 bandpass filter

   $$
   F(s)=\frac{k\omega_n s}{s^2+k\omega_n s+\omega_n^2},
   $$

   使反馈主要保留目标振荡。Case 1 的 PSC 取 \(\omega_n=38\times2\pi\ \text{rad/s}\)、\(k=0.1\)，目标 eigenvalues 取 \(-20\pm j70\)。论文解释实部 \(-20\) 用于获得较大稳定裕度，虚部 70 接近开环 \(0.43\pm j73.59\) 的虚部。[pdf:E06] [pdf:E08]
5. 用 Eqs. (24)-(25) 构造一个周期内的输入核和上一周期输出积分，再由 Eqs. (28)-(29) 得到低维离散 LTI system。对这个系统设计 state estimator 与 state feedback，最后映射回周期控制信号。Fig. 3 给出闭环结构，Fig. 4 给出从建模到 output-feedback synthesis 的完整流程。[pdf:E06]
6. 对比 VI-based EOS。为公平比较，作者先选 PCC1，使 VI 也装在 PV plant T；其 bandpass 取 \(88\times2\pi\ \text{rad/s}\)、\(k=0.1\)，virtual resistance \(R_{VI}\) 再通过 eigenvalue analysis 选取。作者另用 PCC2 说明 VI 对安装位置敏感。[pdf:E08]
7. 保持 Case 1 设计所得的控制结构和参数不变，在 Case 2 的更高 PV 出力、参数切换和单相接地瞬时故障下比较 PSC 与 VI，再用 RT-LAB/DSP HIL 复核。[pdf:E10] [pdf:E11]

论文给出的计算复杂度判断是：常规 SSPH 约为 \(O(n^4)\)，generalized PSC 在 \(n\gg n_{pd}\) 时约为 \(O(n^3)\)。在 \(n=393,n_{pd}=2\) 的算例中，作者估算 SSPH 为约 \(2.4\times10^{10}\) 次量级，PSC 为约 \(1.4\times10^8\) 次量级；这一数字是基于步骤复杂度和 \(10^{-4}\) 积分步长的运算量估算，不是 wall-clock benchmark。[pdf:E07]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有完整形式化推导。理解它可以分为四层。

**第一层：把 LTP 动态变成 Floquet 模态。** 对周期 \(T\) 的系统，取 \(x(t)=U(t)z(t)\)、\(V(t)=U^{-1}(t)\)，得到

$$
\dot z(t)=Jz(t)+V(t)B(t)u(t),\qquad y(t)=C(t)U(t)z(t),
$$

其中 \(J\) 的实数块和共轭复数块携带 Floquet exponents，\(U(t)\) 满足 \(\dot U=A(t)U-UJ\)。这一步把时变的状态矩阵转成“常数模态 + 周期输入/输出映射”。[pdf:E03]

**第二层：把 SSPH 从 full-state feedback 扩展成 output feedback。** 传统 SSPH 在每个周期使用

$$
u(t)=B^T(t)\Phi^T((i+1)T,t)\xi_i,
$$

从而得到离散系统 \(x_{i+1}=\Phi(T,0)x_i+W_r(T,0)\xi_i\)。作者再定义上一周期输出的加权积分

$$
\eta_i=\int_{(i-1)T}^{iT}\Phi^T(\tau,(i-1)T)C^T(\tau)y(\tau)\,d\tau,
$$

把 \(x_i\) 与 \(\eta_i\) 合成 extended discrete-time system。Theorem 5 建立 \((\Phi(T,0),W_o(T,0))\) 的可观性与原 LTP system 可观性的等价关系，Theorem 6 则说明 extended system 对非零 \(\Lambda(\Phi(T,0))\) 可控、可观。[pdf:E04]

**第三层：用 observer separation 配置闭环模态。** 对 extended system 设计

$$
\hat z_{i+1}=(A_e-LC_e)\hat z_i+B_e\xi_i+L\eta_i,\qquad
\xi_i=K\hat z_i.
$$

闭环一个周期的 STM 经非奇异变换后，其 eigenvalues 是 \(A_e-B_eK\) 与 \(A_e-LC_e\) 的并集。因此 Theorem 7 给出的 closed-loop Floquet exponents 属于

$$
\Lambda\!\left(\frac{\ln(A_e-B_eK)}{T}\right)
\cup
\Lambda\!\left(\frac{\ln(A_e-LC_e)}{T}\right).
$$

直观上，\(K\) 决定控制极点，\(L\) 决定估计器极点，二者在 lifted discrete-time domain 分开设计，再通过对数映射回连续时间 Floquet exponents。[pdf:E05]

**第四层：只对目标模态做上述设计。** 把 \(J\) 重排成目标块 \(J_1\) 与其余块 \(J_2\)，只保留

$$
\dot z_1=J_1z_1+\tilde B_{11}(t)u_1,\qquad
y_1=\tilde C_{11}(t)z_1+\tilde C_{12}(t)z_2.
$$

目标模态的周期输入与输出核变为

$$
u_1(t)=\tilde B_{11}^{T}(t)e^{J_1^T((i+1)T-t)}\xi_i,
$$

$$
\eta_i=\int_{(i-1)T}^{iT}e^{J_1^T(\tau-(i-1)T)}
\tilde C_{11}^{T}(\tau)y_1(\tau)\,d\tau.
$$

bandpass filter 的状态加入后形成 Eqs. (28)-(29) 的低维离散系统，再重复 observer/state-feedback 设计。其核心数学收益是矩阵维度随 \(n_{pd}\) 而不是 \(n\) 增长。[pdf:E06]

附录 B-C 给出了 Theorem 5 和 Theorem 6 的证明：从 Floquet 模态不可观推出 \(W_o(T,0)\) 对相应 eigenvector 为零，再用 PBH rank 条件证明 extended system 对非零 monodromy eigenvalues 的可控可观性。附录 D 给出 Eqs. (28)-(29) 中 \(E_1-E_3,W_1-W_3\) 的积分表达式。[pdf:E14] [pdf:E15]

需要保留一个理论边界：论文证明的是在所需 controllability/observability 条件成立且模型与周期结构正确时可配置目标模态；它没有给出模型误差、采样抖动、参数漂移和通信延迟下的鲁棒 eigenvalue-assignment 定理。

## § 7 — 实验设计与结论

**问题 1：能否把名义工况的不稳定模态放到目标位置？**  
实验：Case 1 中，TVC 增益从 \((1,100)\) 切换到 \((4.7,470)\)，比较无 EOS、PSC 和 VI 的 eigenvalue analysis；随后在 RT-LAB 中做 electromagnetic transient simulation。答案：无 EOS 的 dominant eigenvalues 为 \(0.43\pm j73.59\)；PSC 后为 \(-19.89\pm j72.26\)，接近期望 \(-20\pm j70\)，且原稳定 eigenvalues 基本不变；VI 在 \(R_{VI}=0.03\) p.u. 时只能达到 \(-7.62\pm j60.99\)。时域结果中，4 s 切换参数后出现 138 Hz 振荡，5.5 s 启用 PSC 后快速衰减；VI 也能稳定 Case 1，但衰减更慢。[pdf:E09]

**问题 2：同一组控制器参数能否跨运行点工作？**  
实验：保持按 Case 1 设计的 EOS 参数不变，提高多座 PV plant 的出力形成 Case 2。答案：无 EOS 时 dominant eigenvalues 为 \(8.51\pm j71.05\)；PSC 后移到 \(-6.87\pm j62.58\)，而 VI 后为 \(0.77\pm j64.08\)，仍不稳定。时域仿真中，5 s 参数切换激发约 140 Hz 振荡，5.6 s 启用 PSC 后衰减；VI 仅使发散变慢，没有恢复稳定。[pdf:E10]

**问题 3：短路扰动下能否保持稳定？**  
实验：在 PSC 已投入的 Case 1/2 中施加单相接地瞬时短路。答案：作者报告故障激发的振荡在 1 s 内得到抑制；图中给出 VSC 输出电流与端电压响应。论文没有报告故障持续时间、故障阻抗、保护逻辑、数值 solver 或实时步长，因此该结论只能解释为所给仿真设置下通过，不能外推为所有短路故障的稳定保证。[pdf:E10] [pdf:E11]

**问题 4：控制器在实时硬件闭环中是否仍有效？**  
实验：使用 RT-LAB OP5600（2 个 Intel i7 6-core、3.3 GHz CPU）模拟被控系统，把 PV plant T 的原控制与 PSC/VI EOS 放在 TMS320F28335 DSP 中，做 Case 1/2 参数切换和短路实验。答案：HIL 波形与 eigenvalue analysis、EMT simulation 的排序一致：PSC 在两工况稳定，VI 在 Case 1 收敛较慢、Case 2 不能抑制振荡；短路后 PSC 仍恢复稳定。[pdf:E11] [pdf:E12]

**实现证据边界。** 论文报告的是 MATLAB/Simulink 中的 electromagnetic transient simulation、RT-LAB 实时模拟器和 DSP controller HIL。FPGA、FPGA-HIL、RTL、高层综合、FPGA 资源、定点字长、控制代码执行时间、OP5600 分区、I/O 延迟、实时步长和 overrun 统计均未报告。HIL 平台的更详细描述被转引到 Part I，不能由本 PDF 补全。[pdf:E11]

## § 8 — Take-aways

**5 句话。**  
1. 论文把大规模 PEPS 的 EOS 设计放回 LTP/Floquet 框架，而不是用 LTI impedance shaping 间接处理周期系统。  
2. generalized PSC 用 periodic output feedback 取代 SSPH 的 full-state feedback，并把可控可观条件缩小到关心的弱阻尼模态。  
3. MOC/MOO 选择输入输出，Floquet modal truncation 降维，bandpass filter 隔离目标模态，observer/state feedback 完成 eigenvalue assignment。  
4. 在 393 状态、2 个目标特征值的算例中，论文估算设计复杂度从 \(O(n^4)\) 降到约 \(O(n^3)\)，并在 Case 1/2 中给出比 VI 更大的稳定裕度。  
5. RT-LAB + DSP HIL 支持控制效果的工程可行性，但完整系统参数、实时步长、延迟裕度、FPGA 实现和多 EOS 协调仍未闭合。

**3 句话。**  
generalized PSC 的价值在于把“大规模周期系统控制”变成“危险 Floquet 模态的低维周期 output-feedback 设计”。论文的 Case 1/2 与 HIL 结果支持它在给定系统上比单一 VI 参数更稳健，但没有形成不确定性、延迟或多控制器条件下的鲁棒保证。它是一条有理论闭环且有 HIL 支持的 EOS 设计路线，不是可直接移植到任意 PEPS 的即插即用控制器。

**1 句话。**  
用 LTP/Floquet 模态直接设计周期 EOS，能比时不变 VI 更准确地移动危险模态，但其优势依赖模型、模态隔离和实现时序均足够可靠。

## § 9 — 最脆弱的假设

最脆弱的假设是：经 MOC/MOO 选择和 modal truncation 后，所选输入/输出仍对目标模态充分可控、可观，而且未保留的 \(z_2(t)\) 比 \(z_1(t)\) 衰减更快，能被固定中心频率的 bandpass filter 当作次要扰动隔离。这个假设一旦失败，Eqs. (24)-(25) 提取的就不再是一个干净的目标模态，低维 estimator 可能把邻近模态、频率漂移或测量/通信延迟解释成目标状态；此时 Theorem 7 的名义 eigenvalue assignment 不能直接推出真实系统稳定。[pdf:E06]

它在实际中可能因三类情况失效：两个弱阻尼模态靠得很近并落入同一滤波带宽；运行点变化使目标频率偏离固定 \(\omega_n\) 或使 MOC/MOO 排序变化；最佳控制位置和反馈信号落在不同设备，WADC 通信延迟引入不可忽略相位。作者承认跨设备位置会带来通信延迟问题，并为本文选择了同一设备内的折中位置；还承认 PSC 结构复杂、硬件要求高。[pdf:E13]

论文的正面证据是 Case 1 到 Case 2 的运行点变化、短路扰动和 RT-LAB/DSP HIL 都没有破坏稳定；但覆盖仍有限。作者明确说没有全面评估运行条件变化对控制性能的影响，并指出多 EOS 之间可能冲突，需要协调参数设计。[pdf:E14] 因而“模态隔离在合理运行域内持续成立”目前是有两个工况支持、尚无鲁棒证书的工程假设。

## § 10 — 最小复现实验

一周内最可行的不是复刻论文的真实 PEPS，因为本 PDF 没有给出完整系统参数和 Part I 的建模细节；最小复现应验证 generalized PSC 的核心理论 claim。

1. 构造一个可重复的 continuous-time LTP benchmark：例如 20-40 个状态，其中只有一对 Floquet exponents 弱阻尼或轻微不稳定，其余模态稳定；保留一个输入和一个输出，使目标对可控、可观。
2. 数值计算 \(\Phi(T,0)\)、real Floquet-Lyapunov transformation、目标模态的 \(J_1,\tilde B_{11},\tilde C_{11}\)，实现 Eqs. (24)-(29) 的 periodic input/output kernel、bandpass filter、observer 和 state feedback。
3. 设定目标 pair，例如把 \(0.5\pm j70\) 移到 \(-20\pm j70\)。同时实现全阶 SSPH 作为理论对照；VI 不适合作为该抽象 benchmark 的唯一 baseline，可另加一个固定 LTI output feedback。
4. 测量三件事：闭环 monodromy eigenvalues 与目标的误差；非目标 eigenvalues 的漂移；随 \(n\) 增大而 \(n_{pd}=2\) 固定时，控制器离线构造时间和内存增长。
5. 支持 claim 的标准是：目标 pair 在数值容差内到达指定位置、非目标稳定模态不越过虚轴，并且 generalized PSC 的构造成本随全系统维数增长明显慢于全阶 SSPH。反驳标准是：在可控可观且数值条件良好的 benchmark 上仍无法稳定配置目标 pair，或降维后非目标模态系统性失稳。

若要复现论文的工程 claim，还必须取得 Part I、模型文件、设备参数、solver/步长、故障定义和 DSP 控制实现；这些内容在本 PDF 中未报告，不能自行补齐。

## § 11 — 最强反例设计

最强反例不是把参数随机扰乱到系统必然崩溃，而是专门攻击“危险模态可被单独提取”的桥梁。构造两个相距很近的弱阻尼共轭模态，使它们都落在 \(k=0.1\) 的 bandpass passband 内；让 Case 1 中 MOC/MOO 选出的输入输出对第一模态强、对第二模态弱，而在连续的运行点变化后两者排序交换。控制器仍按 Case 1 的单对 \(n_{pd}=2\) 模型和固定 \(\omega_n\) 工作，再加入同设备 DSP 延迟与跨设备通信延迟两个版本。

测试时连续扫描模态间距、频率漂移、测量噪声和延迟，逐点计算真实 full-order monodromy eigenvalues，并做故障后时域验证。如果 PSC 把设计目标 pair 移入左半平面，却把未建模的邻近 pair 推向不稳定，或在很小的频率漂移/延迟下稳定裕度比 VI 更快丧失，那么“低维 periodic output feedback 在多工况下更稳健”的解释就被实质性挑战。这个反例还可以排除一个替代解释：论文的优势可能主要来自 Case 1 中更大的名义实部裕度，而不一定来自 PSC 结构本身。

这是基于论文假设的反例设计，不是论文已经做过的实验。论文已有的 Case 2 和短路测试增加了可信度，但没有覆盖邻近弱阻尼模态、MOC/MOO 排序交换、显式延迟或多 EOS 相互作用。

## § 12 — Follow-up Research Idea

电力电子与电力系统控制中的高影响工作通常不仅要求一个新控制律，还要求可验证的稳定性边界、与高保真 EMT/HIL 的一致性、实现可行性，以及在多设备、多工况和故障下仍成立的系统价值。基于第 9 节，候选研究方向是把问题从“名义 LTP 模型上一对模态的精确配置”改写为“含频率漂移、通信延迟和多 EOS 耦合的不确定 LTP 网络中，危险模态集合的可组合鲁棒稳定”。

**(a) 未满足需求。** 真实 PEPS 的运行点、模态频率和 MOC/MOO 都会变化，多个 EOS 还可能互相抵消；固定 \(J_1\)、固定 bandpass 和单控制器设计没有给出整个运行域的保证。论文也明确把全面工况评估、多 EOS 冲突和硬件复杂度留给未来工作。[pdf:E13] [pdf:E14]

**(b) 研究价值。** 如果能给出“哪些运行域、延迟和模态间距下多个周期 EOS 仍保证全阶稳定”的可计算证书，就把单算例控制器推进为可部署的系统级方法；这比再增加一个滤波器或再调一个工况更接近本领域认可的工程与理论贡献。

**(c) 可借鉴工具。** 可以把 lifted LTP model 与 robust control 的 structured singular value、integral quadratic constraints 或 parameter-dependent Lyapunov functions 结合；再用 distributed/structured \(H_\infty\) synthesis 约束每个 EOS 只能使用本地信号或有界延迟的远端信号。关键不是堆叠工具，而是让不确定模态集合与实际通信/实现约束进入同一个稳定性证书。

**(d) 第一个证伪实验。** 在两个相邻弱阻尼模态、两个 EOS、可扫描延迟和 PV 出力的 EMT benchmark 上，先计算声称的鲁棒稳定域，再在域内做 full-order eigenvalue analysis 与 RT-LAB/DSP HIL。如果任一证书内点出现不稳定 eigenvalue、实时 overrun 或故障后不收敛，研究假设立即失败。

**(e) 与本文的实质区别。** 本文在名义 LTP-SSM 上选择目标模态和单个 EOS，再用两个工况验证；候选方向把研究对象改成一个不确定、多控制器、带实现约束的 LTP 网络，并把目标从精确 pole placement 改成全阶鲁棒稳定域与可组合性保证。由于本次没有在源 PDF 之外检索相关工作，这只是候选研究想法，不声称 novelty。
