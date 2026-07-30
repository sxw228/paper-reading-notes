# State-Space Driven Digital Twin for Condition Monitoring and Predictive Health Assessment in Grid-Integrated Power Converter System

作者：Arun Kumar；Nishant Kumar
出处：IEEE Transactions on Industrial Cyber-Physical Systems, Vol. 3
年份：2025
DOI：10.1109/TICPS.2025.3586823
Zotero key：B4XIDARI
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个具体的 cyber-physical monitoring 问题：对两级单相并网光伏变换器建立一个能够随物理系统（Physical System, PS）在线同步的 Digital Twin（DT），用状态空间模型描述内部动态，再通过在线参数估计识别电容、电感及其寄生参数的变化，从而把“波形是否正常”推进到“哪个元件的健康状态正在劣化”。作者把这一任务与变换器控制放在同一套系统中：boost 级由 PO-IMPC 执行 MPPT，逆变级由 αβCDSC-UVT-IMPC 生成并跟踪并网电流参考；摘要将核心结果概括为 FPGA-based OPAL-RT real-time validation 中 DT 与 PS 的 Percentage Similarity（PST）超过 98.55%。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，不是因为 DT 本身新奇，而是因为并网变换器的 DC-link 电容、滤波电感和寄生参数会随温度、老化和故障前兆变化；这些变化既影响能量传输，也会改变纹波、THD、损耗和控制稳定性。若模型能够从在线传感数据中可靠反推出这些参数，维护可以从定期检查转为 condition-based maintenance。不过，本文实际验证的是“在人工设置的健康/退化状态下进行参数辨识和波形跟踪”，尚未直接验证剩余寿命（RUL）、故障发生时间或提前预警时间。因此，“predictive health assessment”在本文中更准确地理解为**由参数退化趋势支持的健康评估潜力**，而不是已经闭合的寿命预测能力。

## § 2 — 前人工作与不足

论文将已有方法分成控制与 DT 两条线。控制侧，PI 的代价是稳态误差、慢瞬态和扰动敏感；distributed MPC 能改善动态与鲁棒性，但实时计算复杂；SMC 能应对参数变化，却会引入 chattering；FLC 具有非线性适应性，但结构复杂且依赖细致调参。[pdf:E01]（PDF 物理页 1，Introduction）这些不足解释了作者为何为 boost 和逆变器采用带积分项的 MPC，并额外用 αβCDSC 做基波正交分量构造和谐波抑制。

DT 侧，作者点名了面向 buck converter 的 model-based health-indicator estimation [10]、面向 multiphase boost converter 的 self-evolving DT [11]，以及 one-cycle multiparameter identification [8]。论文的判断是：已有 converter DT 往往偏向 emulation、离线参数估计或单一拓扑，欠缺与实时控制动态结合的故障识别和退化跟踪；Table III 进一步把 [6]、[8]、[10]、[11] 与本文按目标系统、参数估计方法和实时验证作了并列。[pdf:E02]（PDF 物理页 2，Introduction 与 Fig. 1–2）[pdf:E07]（PDF 物理页 7，Table III）

需要区分作者定位与严格比较证据：Table II–IV 给出了 PI、SMC、MPC、不同 DT 和 PSO/EFO/EDA/E2FD-HO 的汇总数值，但正文没有报告这些基线是否在同一硬件、同一采样、同一数据和同一调参预算下重新实现，也没有给出统计重复。因此，它们适合说明作者想解决的缺口，不能单独证明相对于全部 prior work 的公平 superiority。

## § 3 — 重建作者的思考路径

在不预设本文贡献的情况下，可以从已有工程事实重建这条路线。第一，两级并网 SPV 系统本来就有较清楚的开关拓扑、电感、电容、寄生电阻和可测端口量，因此状态空间模型比纯黑箱模型更容易解释“哪一个参数变了”。第二，现场可测的通常是 \(V_{pv}\)、\(I_{pv}\)、\(V_{dc}\)、\(v_g\)、\(i_g\) 等端口信号，而真正关心的电感、电容与寄生参数未必能在线直接测量；于是健康监测自然转化为 inverse problem：寻找一组内部参数，使模型输出与传感器记录最接近。第三，变换器的控制瞬态会污染健康残差，所以必须让 DT 与物理控制器共享明确的采样和开关状态逻辑，并用较快的同步/辨识维持模型贴合。第四，元件退化必须造成可观察的多量变化，例如 DC-link 纹波、THD、损耗和效率同时改变，否则“参数变化”可能只是优化器在补偿未建模动态。

由此会得到一个合理的研究程序：先从开关等效电路推导连续状态方程，再离散化供实时平台执行；从传感数据构造输出误差目标；在线搜索未知参数；最后用健康、分级电容退化和分级电感退化检查参数估计、内部波形与外部性能是否一致变化。这个路径在逻辑上成立，但能否成为“预测健康”仍取决于参数可辨识性、独立验证和跨工况泛化，而不只取决于拟合相似度。

## § 4 — 核心 Intuition

核心 intuition 是：健康变化会先表现为物理参数变化，而状态空间 DT 把这些不可直接观测的参数与可测电压、电流联系起来；只要持续寻找能让 DT 输出贴近 PS 的参数，就能把传感器波形转换成元件健康估计。E2FD-HO 负责做这个在线 inverse search，控制器与实时平台负责让比较发生在同一动态条件下。方法真正成立的关键不是“波形看起来像”，而是**不同元件退化在所测信号中必须具有足够独特且跨工况稳定的可辨识特征**。

## § 5 — 具体方法与完整 Pipeline

以论文的 3.95 kW 实验系统为例，完整 pipeline 如下。

1. **物理功率链。** Solar emulator/PV 端先经过 boost converter，把 DC-link 调至 350 V；随后单相全桥逆变器通过 \(L_f\) 与 RC filter 向 200 V rms、50 Hz 电网送电。论文报告实验标称元件为 \(L=5\ \mathrm{mH}\)、\(C_{dc}=9400\ \mu\mathrm{F}\)、\(L_f=6\ \mathrm{mH}\)、\(C_f=10\ \mu\mathrm{F}\)、\(R_f=5\ \Omega\)。[pdf:E05]（PDF 物理页 5，Fig. 4 与 Section VI）
2. **实时采样与控制。** Hall sensors 采集电压/电流并支持闭环控制及 PS–DT 通信。Boost 级先由 P&O 产生 \(I_{ref}\)，IMPC 对两个候选开关状态预测下一步 \(I_{pv}\)，选择积分误差 fitness 最小的状态；逆变级先用 T/8、T/16、T/32 的 αβCDSC 级联提取基波正交分量，再由 UVT 生成 \(i_{gref}\)，IMPC 对桥臂状态枚举并最小化并网电流误差。[pdf:E02]（PDF 物理页 2，Fig. 2 与 Eq. 1–2）[pdf:E03]（PDF 物理页 3，Eq. 3–16）
3. **构造物理 DT。** 作者按 boost switch ON/OFF 和 inverter 的两组导通状态画出包含 \(L,C_d,L_f,C_f\) 及寄生电阻的等效电路，分别形成一级与二级的连续状态空间方程。带横线的量表示 DT 内部状态或参数，而 \(V_{pv}\)、\(I_{pv}\)、\(V_{dc}\)、\(v_g\)、\(i_g\) 来自物理传感器或作为已知边界量。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Eq. 17–20）
4. **离散化并运行。** 连续模型用 Tustin method 转为 \(z\)-domain，得到 boost 级电流、DC-link 电容电压、滤波支路电流和并网电流等离散递推式（Eq. 21–28），在 OPAL-RT 上运行。论文只用符号 \(T_s\) 表示采样时间，没有报告其数值、solver、task schedule 或数值稳定性设置。[pdf:E04]（PDF 物理页 4，Eq. 21–28）
5. **在线参数估计。** E2FD-HO 以 \(I_{pv}\)、\(V_{dc}\)、\(i_g\) 的 PS–DT 绝对误差和为 objective。它先根据 objective 为粒子分配 charge，使用 electrostatic-discharge update 把候选拉向 global best，再用 electromagnetic-force update 调整速度和位置，直至相邻最优解变化小于容差 \(\Psi=0.01\)。估计结果包括电感、电容和多个等效串联/开关电阻。[pdf:E05]（PDF 物理页 5，Eq. 29–40）
6. **健康判读。** 把估计参数代回状态空间模型，比较 PS 与 DT 的 \(i_{inv},i_g,v_{cf},i_{cf},i_{dc},v_l,i_{db},v_{lf}\) 等波形，并计算 PST；同时观察 \(\Delta V_{dc}\)、THD、\(P_{grid}\)、\(P_{loss}\) 和效率随人工退化级别变化。[pdf:E06]（PDF 物理页 6，Table I、Fig. 5–7 与 Eq. 41）

硬件边界必须明确：论文报告控制使用 NI sbRIO-9636 FPGA microcontroller、DT 运行在 OPAL-RT，并在 Table III 声称 fully real-time synchronization latency \(<0.5\ \mathrm{ms}\)。但 FPGA 型号之外的 HDL/软件分区、时钟、pipeline、fixed-point、资源占用、WCET 和 I/O latency **未报告**；标准 HIL 拓扑与 host/target 边界 **未报告**；实时仿真的数值步长、overrun、jitter 和 solver **未报告**；EMT switching solver、网络离散化与电磁暂态精度 **未报告**。[pdf:E05]（PDF 物理页 5，Fig. 4 与实验平台说明）[pdf:E07]（PDF 物理页 7，Table III）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有形式化数学，但推导主干可以压缩成三层。

**第一层：从开关电路到状态空间。** 对 boost 的 ON/OFF 状态，状态取电感电流 \(\bar I_{pv}\) 与 DC-link 电容电压 \(\bar v_{cdc}\)；对 inverter，状态取逆变器电流 \(\bar i_{inv}\) 与滤波电容电压 \(\bar v_{cf}\)。作者分别写成

\[
\dot x=A(\theta,\mathrm{State})x+B(\theta,\mathrm{State})u,
\]

其中 \(\theta\) 包含待估的 \(L,C_d,L_f,C_f\) 和寄生电阻。Eq. 17–20 给出了各开关状态的具体 \(A,B\) 矩阵。直觉是：同一个输入电压在不同 \(L,C,R\) 下产生不同的斜率、纹波和相位，因此可通过波形反推参数。[pdf:E04]（PDF 物理页 4，Eq. 17–20）

**第二层：从连续时间到实时递推。** 作者用 Tustin bilinear transform 把 \(s\) 替换成 \(\frac{2}{T_s}\frac{z-1}{z+1}\)，由此得到 \(\bar I_{pv}(z)\)、\(\bar v_{cdc}(z)\)、\(\bar i_{dc}(z)\)、\(\bar V_{dc}(z)\)、\(\bar i_{cf}(z)\) 与 \(\bar i_g(z)\) 的 Eq. 21–28。相比 forward Euler，Tustin 通常更好地保留线性系统频率关系；但论文没有给出 \(T_s\) 的数值或离散化误差分析，所以无法判断最高 switching/harmonic 频率是否被充分解析。[pdf:E04]（PDF 物理页 4，Eq. 21–28）

**第三层：把系统辨识写成优化。** 核心 objective 为

\[
\bar O=\frac{1}{S_T}\sum_{k=1}^{S_T}
\left(
|I_{pv}-\bar I_{pv}|+
|V_{dc}-\bar V_{dc}|+
|i_g-\bar i_g|
\right),
\]

即让三组可测量量的平均绝对差最小。粒子 \(X_i\) 表示一组候选参数，charge 定义为 \(Q_i=e^{-\bar O(X_i)}\)；ED 更新为 \(X_i^{ED}=X_i+\alpha Q_i(G_b-X_i)\)，再按 Coulomb-like force 更新速度 \(V_i^{new}=\omega V_i+\eta F_i^{act}\) 与位置 \(X_i^{new}=X_i^{ED}+V_i^{new}\)。[pdf:E05]（PDF 物理页 5，Eq. 29、33、36–39）

结果相似度定义为

\[
PST=\left(1-\frac{|\gamma_{PS}-\gamma_{DT}|}{\gamma_{PS}}\right)\times 100.
\]

[pdf:E06]（PDF 物理页 6，Eq. 41）这个指标的直觉是用物理量作分母的相对误差，但正文没有说明它是逐样本、均值、峰值还是其他聚合，也没有说明 \(\gamma_{PS}\) 过零或接近零时如何处理。对交流电流而言，这一缺口很关键：分母接近零会使相似度病态，而选择峰值或特定窗口又可能掩盖相位与瞬态误差。

## § 7 — 实验设计与结论

**问题 1：健康状态下 DT 能否跟踪 PS？ →** 作者在 1000 W/m²、25 °C 下运行约 3.95 kW 系统，记录物理量和 DT 内部量，并用 E2FD-HO 估计元件参数。**→ 答案：** \(i_{inv},i_g,v_{cf},i_{cf}\) 的 PST 报告为 98.95%，另一组内部量的 PST 为 98.80%，整体高于 98.70%；并网电流 THD 为 3.3%。[pdf:E06]（PDF 物理页 6，Table I、Fig. 5–6）

**问题 2：DC-link 电容退化是否能被 DT 反映？ →** 作者用多个小电容串并联实现每 5% 一级、直到 H-40% 的容量退化，观察 DC-link 纹波、并网功率、损耗、效率与 THD，并比较 PS/DT 波形。**→ 答案：** H-40% 时 \(\Delta V_{dc}\) 从 4.5 V 增至 9.5 V，\(P_{grid}=3837\ \mathrm{W}\)，效率降至 96.79%，\(i_g\) THD 增至 4.95%；所展示内部量的 PST 为 98.85%，该 case 整体高于 98.70%。[pdf:E06]（PDF 物理页 6，Fig. 6–8 对应正文）

**问题 3：interfacing inductor 退化是否更严重且仍可跟踪？ →** 作者使用 variable inductor，每 5% 一级降到 H-40%。**→ 答案：** H-40% 时损耗报告为 695 W、效率 82.4%、THD 8.5%；Fig. 9 所示波形 PST 为 98.65%，正文同时称该工况 mean PST 始终高于 98.78%，而全参数、全退化级别总体超过 98.55%。[pdf:E07]（PDF 物理页 7，Fig. 9–10 与 Case 3）“98.65%”与“mean above 98.78%”面向的聚合对象并未被清楚区分，因此不应合并成一个无歧义的统计结论。

**问题 4：控制、DT 与优化算法是否优于基线？ →** Table II–IV 汇总比较 PI/SMC/MPC、既有 DT，以及 PSO/EFO/EDA。**→ 答案：** 作者报告 proposed control 的 harmonic suppression \(>90\%\)、response time 8–12 ms、steady-state error \(<0.5\%\)；E2FD-HO convergence \(<1.5\ \mathrm{s}\)、estimation error \(<1.5\%\)；DT synchronization latency \(<0.5\ \mathrm{ms}\)。[pdf:E07]（PDF 物理页 7，Table II–IV）但实验章节没有给出基线复现实验、重复次数、误差条、数据分割或计算平台控制，因此这些表更像汇总性对比，而不是可审计的 head-to-head benchmark。

总体而言，论文闭合了“在一套物理硬件上，状态空间 DT 能在健康和两类人工退化条件下保持很高的报告相似度，并呈现退化相关性能变化”。它没有闭合“提前多久发现故障”“能否预测 RUL”“能否区分复合故障”“在未见 irradiance/load/grid disturbance 下是否仍准确”。结论还提到 switches degradation，但实验 case 只详细报告了 DC-link capacitor 与 interfacing inductor，switch degradation 的独立实验结果 **未报告**。[pdf:E08]（PDF 物理页 8，Conclusion）

## § 8 — Take-aways

**5 句话：**

1. 论文把两级并网 SPV converter 的开关等效电路、状态空间 DT、在线参数估计和实时控制放进了一套 hardware validation。
2. E2FD-HO 用 \(I_{pv},V_{dc},i_g\) 的 PS–DT 误差搜索 \(L,C,R\) 参数，再用其他内部波形和性能量观察健康状态。
3. 健康、电容 H-40% 与电感 H-40% 下报告的 DT–PS PST 都很高，全退化范围最低汇总结论仍超过 98.55%。
4. 电感 H-40% 在论文实验中造成更高 THD、更低效率和更大损耗，因此比电容 H-40% 更具系统影响。
5. 但高 PST 仍是 fitting/monitoring 证据，不等于可泛化的 fault prognosis；采样、实时实现、可辨识性、独立测试和统计重复均不足。

**3 句话：** 这是一套 physics-model-driven DT：从状态空间方程在线反推元件参数，并在物理 converter 与 OPAL-RT DT 之间比较波形。实验说明人工电容/电感退化会在参数、THD、效率和损耗上留下可跟踪变化。论文最需要补强的是 blind generalization 和真正的 predictive endpoint，而不是继续增加 in-sample PST。

**1 句话：** 本文令人信服地展示了“能同步拟合并跟踪退化”，但尚未证明“能在未知工况下提前、唯一且可靠地诊断健康”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**使 \(I_{pv},V_{dc},i_g\) 拟合得很好的参数组合，就是物理上正确且可泛化的元件健康状态。** E2FD-HO 的 objective 只直接使用这三组量，而系统中同时存在多只电感、电容、寄生电阻、开关电阻和控制参数；不同参数组合可能对外部端口产生近似相同的响应，这就是 parameter non-identifiability。[pdf:E05]（PDF 物理页 5，Eq. 29 与参数搜索流程）

论文提供的支持是：Table I 的健康参数估值在数量级上接近实验标称值，且未直接进入 objective 的内部波形也呈现 98.8% 左右 PST；在单元件分级退化中，性能趋势与物理直觉一致。[pdf:E06]（PDF 物理页 6，Table I 与 Fig. 5–7）但它没有报告参数置信区间、observability/identifiability rank、不同随机种子是否收敛到同一参数、held-out 工况、复合退化，或先估参后冻结模型的 blind prediction。若这个假设不成立，DT 仍可能“波形很像”，却把电容 ESR 上升误判为电感变化，进而使维护决策错误；这会直接击中论文从相似度到健康诊断的核心贡献。

## § 10 — 最小复现实验

一周内最值得复现的不是完整控制器，而是“参数估计能否在未见数据上保持正确健康排序”。

- **数据：** 采集或从原平台导出健康、\(C_{dc}\) H-20%/H-40%、\(L_f\) H-20%/H-40% 五种状态下的 \(V_{pv},I_{pv},V_{dc},v_g,i_g\)，并保留元件实测值作为 ground truth。每种状态至少做三次独立启动；前两次用于估参，第三次完全留作 blind test。论文没有报告 \(T_s\) 数值，因此复现时必须记录真实采样间隔并检查 anti-aliasing，而不能猜用论文步长。
- **实现：** 只实现 Eq. 17–28 的离散状态空间模型与 Eq. 29 objective；E2FD-HO 可按 Eq. 30–40 实现，同时加入一个有界 nonlinear least-squares 或 PSO baseline。先在训练记录估计 \(\theta=(L,C_d,L_f,C_f,R\ldots)\)，随后冻结 \(\theta\)，不再用测试记录重新优化。
- **测量：** 在 blind test 上报告 MAE/NMSE、经零点保护定义的 PST、参数相对误差、健康等级排序正确率，以及从退化开始到越过检测阈值的 delay 与 healthy false-alarm rate。还要分别报告 objective 内三信号和未进入 objective 的内部/辅助信号，避免循环验证。
- **支持标准：** 如果冻结后的模型在独立运行与轻微 irradiance/load 变化下仍达到论文的 \(>98.55\%\) 波形阈值，并且 \(C_{dc}\) 与 \(L_f\) 的估值随真实退化单调且不会互相混淆，则核心 health-identification claim 获得支持。
- **反驳标准：** 如果只有重新拟合同一段数据才有高 PST，或不同随机种子给出不同元件参数但相同波形相似度，或工况变化被误报为元件退化，则证据支持的只是 adaptive curve fitting，而不是可信健康诊断。

## § 11 — 最强反例设计

最强反例是构造一个**端口波形近似等价、真实健康原因不同**的复合场景。令 \(C_{dc}\) 容量下降并伴随 ESR 上升，同时小幅改变 \(L_f\)、grid impedance 或 irradiance，使 \(I_{pv},V_{dc},i_g\) 在 Eq. 29 的训练窗口内仍可被另一组错误参数拟合；然后用拆机/离线 LCR measurement 给出真实元件值，并在新的负载或电网扰动下做 blind rollout。

若 E2FD-HO 在训练窗口仍得到 \(>98.55\%\) PST，却把退化归因给错误元件，或冻结后的 DT 在新扰动下迅速失配，那么高 PST 的替代解释就是“多参数补偿了同一外部波形”，不是正确的 predictive health assessment。这个反例尤其有力，因为 Fig. 10 显示各信号 PST 都聚集在很窄的高值区间，而论文没有展示 health-class separation、参数后验或复合故障识别。[pdf:E07]（PDF 物理页 7，Fig. 10）还应在交流过零点单独检查 Eq. 41：若改变零点处理规则就显著改变 PST，说明结论还受指标定义而非模型健康能力支配。

## § 12 — Follow-up Research Idea

在电力电子、控制与 industrial cyber-physical systems 领域，高影响工作通常不只追求拟合精度，还要求明确的物理可解释性、跨工况硬件验证、实时实现边界、可复现比较，以及错误诊断不会导致危险维护决策的证据。因此，候选研究方向不是再叠加一个 optimizer，而是把问题重新定义为：**可辨识性约束、风险校准的 health digital twin**。

**（a）未满足的需求。** 现有框架输出单一“最优参数 + 高 PST”，却不告诉维护者哪些元件在当前传感配置下其实不可区分、诊断置信度是多少、工况漂移是否超出模型适用域。真正需要的是“健康结论及其可证伪的不确定性”，而不只是最贴合波形。

**（b）潜在研究价值。** 若系统能在实时预算内输出参数 feasible set/posterior、故障类别置信区间和 unknown/abstain 状态，并在复合退化与 grid disturbance 下保持校准，它会把 DT 从可视化/拟合工具提升为可审计的 maintenance decision instrument。这比把 E2FD-HO 换成另一个 metaheuristic 更接近本领域认可的实质贡献。

**（c）可借鉴的相邻方法。** 可以结合 Bayesian system identification 或 set-membership identification 量化参数不确定性，用 nonlinear observability/Fisher information 主动选择传感器与激励，再用 conformal prediction 校准 residual-based alarm 的覆盖率。物理状态空间模型保留可解释性，学习部分只估计未建模残差或工况分布，不直接吞掉元件语义。

**（d）第一个可证伪实验。** 设计 blinded factorial test：分别和组合改变 \(C_{dc}\) 容量/ESR、\(L_f\)、grid impedance、irradiance 和 load，让训练集故意缺少若干组合。若系统不能在不可辨识组合上扩大不确定区间或 abstain，或者其 95% parameter interval 在 blind hardware run 中覆盖率显著不足 95%，该想法立即被证伪。

**（e）与本文的实质区别。** 本文优化一个点估计并以 PST 证明 DT 贴近 PS；候选方法的研究对象则是“哪些健康结论由当前传感与激励真正支持”，目标函数从 waveform similarity 改为 identifiability、uncertainty calibration 与决策风险。这个方向尚未做充分相关工作检索，因此只标为候选想法，不声称 novelty。
