# Hardware-in-the-Loop Simulation of Power Electronic Systems Using Adaptive Discretization

作者：M. Omar Faruque；Venkata Dinavahi（PDF 物理页 1，题名与作者信息）[pdf:E01]

出处：*IEEE Transactions on Industrial Electronics*, Vol. 57, No. 4, April 2010（PDF 物理页 1，刊头）[pdf:E01]

年份：2010（论文注明首次在线发表时间为 2009-11-24；PDF 物理页 1，稿件信息）[pdf:E01]

DOI：10.1109/TIE.2009.2036647（PDF 物理页 1，页脚）[pdf:E01]

Zotero key：4WXTWIBC

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述的研究问题**是：在 power-electronic hardware-in-the-loop（HIL，硬件在环）仿真中，怎样在严格实时步长内获得足够准确、稳定的离散模型，尤其是在系统输入从稳态平滑变化突然转为故障、开关或参考值突变时。C-HIL 把功率系统与变流器建成实时数字模型，把真实数字控制器接入闭环；控制器每一步读取仿真的电压、电流并返回开关信号，因此离散模型不只是离线计算工具，而是控制器看到的“被控对象”。论文指出，常用 trapezoidal rule（TR，梯形法）在某些条件下会产生伪数值振荡，较大步长还会发生 frequency warping（频率扭曲）；同时，实时仿真必须在每个指定步长内完成计算（PDF 物理页 1，Introduction）[pdf:E02]。

重要性来自两个同时存在、又相互冲突的要求。第一，HIL 被用来在真实控制器上重复测试危险工况，价值在于降低试验成本、提高可重复性，并允许控制器经历不宜直接施加到实物主回路的 contingency（事故工况）。第二，电力电子系统包含高频 PWM、异步开关事件和快速暂态，增大步长虽然减轻实时计算压力，却可能放大离散误差；缩小步长则可能使计算超出 deadline。论文将这一矛盾归结为：**离散器对采样间输入形状的假设是否与真实激励匹配**（PDF 物理页 1，Abstract 与 Introduction）[pdf:E01][pdf:E02]。

**基于证据的推断**：这项工作的工程价值不只是“让波形更像离线结果”，而是减少控制器验证中的错误归因。如果数值振荡被误认为真实硬件不稳定，控制器会被过度修正；如果离散模型掩盖了真实暂态，控制器又可能在现场失效。VSC-HVDC 被选作案例，正因为它同时包含三相交流网络、IGBT 开关、dc-link 动态、PWM 和有功/无功解耦控制，是对实时离散、事件同步和闭环接口的综合压力测试（PDF 物理页 6，Section IV 与 Fig. 8）[pdf:E03]。

## § 2 — 前人工作与不足

论文对既有工作的归纳分成三层。第一，早期 C-HIL 工作主要解决 fixed-time-step（固定步长）下来自控制器的离散开关信号如何计入仿真，也就是 switching-event accounting；模型离散仍普遍沿用离线 EMTP 中的 TR。作者认为这不足以解决较大步长下的伪振荡和频率扭曲（PDF 物理页 1，Introduction，对文献 [8]–[15] 的概括）[pdf:E02]。

第二，z-transform-based discretization（基于 z 变换的离散化）此前已经用于离线电磁暂态计算，SIT（step-invariant transformation，阶跃不变变换）、RIT（ramp-invariant transformation，斜坡不变变换）以及相关方法也见于数字控制和滤波器设计。但先前应用通常为整段仿真固定选择一个离散器，即使不同离散器的误差会随输入类型而变化（PDF 物理页 1–2，Introduction 延续）[pdf:E02][pdf:E04]。

第三，SIT、RIT、TR、forward Euler（FE，前向欧拉）等方法并不是在所有工况上统一排序。论文的基本数学判断是：SIT 假定步内输入保持常数，RIT 假定步内输入线性变化；只有真实输入与该假定匹配时，采样点响应才可能无误差。对其他输入，固定算法必然引入模型失配误差（PDF 物理页 2，Section II，Eq. (2)–(4)）[pdf:E05]。

因此，前人工作的关键不足不是“没有提出更多离散公式”，而是没有把 **input regime（输入形态）变化**作为实时求解器的 mode switch（模式切换）问题。另一个工程缺口是，z 域系数含矩阵指数，若在运行中重新计算会违反实时约束；作者据此把候选方法的系数矩阵预先计算，只在运行中切换（PDF 物理页 2，Introduction 延续）[pdf:E04]。

## § 3 — 重建作者的思考路径

以下是**基于论文背景和失败模式的重建**，不是作者逐句给出的研究日志。

1. 实时 C-HIL 首先要求每个计算步都准时结束；因此不能简单靠任意缩小步长或在线反复求矩阵指数来换精度（PDF 物理页 1–2，Introduction）[pdf:E02][pdf:E04]。
2. 连续系统被采样后，采样点之间的输入轨迹并没有自动消失。相同的端点采样值，可以对应“整步保持”“线性爬升”或“步内突然跳变”，而这些轨迹对状态积分的贡献不同（PDF 物理页 2，Section II，Eq. (1)–(4)）[pdf:E05]。
3. 既然离散误差主要来自输入轨迹假设失配，就不应追求一个在所有时刻固定使用的万能低阶积分器。稳态正弦在足够短的局部区间内更接近线性变化，故障和开关突变则更接近阶跃。
4. SIT 虽适合阶跃假设，却因严格真分式系统映射而带来一个或多个原点极点，对应时域延迟；增加 z 域原点零点可补偿延迟，形成 TSSIT。稳定连续系统经 SIT/RIT 映射后仍保持离散稳定，是采用这些方法的理论底座（PDF 物理页 3，Eq. (5) 与稳定性说明）[pdf:E06]。
5. 真正可部署的方案应只保留少数输入模式，为每种模式预计算系数矩阵；实时循环只做事件识别、矩阵选择和状态更新。这样，计算复杂度从“在线构造离散模型”变成“在有限模型库中切换”（PDF 物理页 2，adaptive 方法说明）[pdf:E04]。

这条思考路径把问题从“哪一个积分器最好”改写成“当前步的输入假设是哪一种，以及怎样在 deadline 内安全切换”。

## § 4 — 核心 Intuition

不要把离散化视为整段仿真固定不变的 numerical integrator，而要把它视为对采样间输入轨迹的模型选择。稳态、近似线性变化的输入使用 RIT，初始化、故障或参考突变等阶跃型输入使用无一步延迟的 TSSIT，并在输入机制改变时切换预计算矩阵。核心收益不是提高名义阶数，而是让离散器的局部输入假设与真实激励匹配，同时把昂贵的矩阵指数计算移出实时循环（PDF 物理页 2，adaptive 方法；PDF 物理页 4，Fig. 4 及解释）[pdf:E04][pdf:E07]。

## § 5 — 具体方法与完整 Pipeline

以论文中的“converter 2 交流电源中断后恢复”为例，完整 pipeline 如下。

1. **建立连续模型与控制目标。** VSC-HVDC 由两侧三相交流源、串联相电抗器、两个背靠背 IGBT VSC、dc-link 电容和数字 vector control（矢量控制）组成。变流器端电压由 modulation index、dc-link 电压和相角共同决定，论文写为 $V_{2i}=K m_a V_{dc}\sin(\omega t+\delta)$（PDF 物理页 6，Fig. 8、Eq. (9)、Section IV-A/B）[pdf:E03]。
2. **按输入形态选择离散模型。** 两侧交流系统在稳态正弦输入下采用 RIT；初始化和由突变引起的暂态采用 TSSIT。论文的交流支路状态更新见 Eq. (10)，VSC 用离散 switching function 表示，dc-link 电流与电压由 Eq. (13)–(15)更新（PDF 物理页 7，Fig. 9、Eq. (10)–(15)、Section IV-C）[pdf:E08]。
3. **预计算模式系数。** 对固定参数和固定步长，RIT、SIT/TSSIT 的系数矩阵只在仿真开始时计算；运行中只更换矩阵组。论文明确说明这些系数只有在系统参数或步长变化时才需重算（PDF 物理页 7，Eq. (10) 后的参数说明）[pdf:E08]。
4. **同步异步开关事件。** 控制器输出的门极信号可能发生在两个仿真采样点之间。Target 1 的 FPGA 在每个计算步内连续检测数字输入跳变，记录事件相对本步起点的时刻，并在下一计算步开始时上传；这给事件同步算法提供亚步时间戳（PDF 物理页 8，Fig. 11 后的 switching-event 说明）[pdf:E09]。
5. **执行多速率硬件分工。** Target 1 运行电气系统实时模型，Target 2 运行真实数字控制器；Target 2 的额外 FPGA 用 100 MHz 时钟生成 PWM 三角载波，时间分辨率为 10 ns。CPU 级 HIL 主仿真报告使用 10 μs 步长，形成“微秒级网络求解 + 纳秒级 PWM/事件时间戳”的多速率结构（PDF 物理页 8，Fig. 10–11 与硬件说明；PDF 物理页 10，结果总结中的 10 μs）[pdf:E09][pdf:E10]。
6. **闭环交换 I/O。** Target 2 接收 ±15 V 模拟反馈，输出 0–15 V 门极信号；六路门极信号通过标准 I/O 线送到 Target 1。电气模型由 C 程序封装为 Simulink S-function，并通过 RT-LAB 下装到 target nodes。论文没有报告浮点/定点格式、求解器的 worst-case execution time（最坏执行时间）分布或 FPGA 资源占用率（PDF 物理页 8，HIL Simulation）[pdf:E09]。
7. **在已知输入突变点切换。** 初始化时先用 TSSIT，再切到 RIT 达到稳态；converter 2 电源中断的计划时刻切回 TSSIT，电源恢复后再切回 RIT。该策略在 Fig. 12 中避免了 TR 出现的伪电流振荡（PDF 物理页 9，Section V、Fig. 12、Step 1–3）[pdf:E11]。
8. **用同一控制器做三级验证。** 论文先做 C 语言 offline simulation，采用 2 kHz carrier 和 20 μs 步长，并用 PSCAD/EMTDC、MATLAB/Simulink 交叉核对；随后做 PC-cluster HIL；最后把同一 Target 2 控制器接到 4 kW 实验 VSC-HVDC。实验两侧使用 2.5 mH、600 V、18 A 电抗器，门极板带 2 μs dead time（PDF 物理页 7，Offline Simulation；PDF 物理页 8，Experimental Setup）[pdf:E08][pdf:E09]。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线是：先明确步内输入的保持方式，再从连续系统得到与该输入模型相匹配的离散映射。

z 变换只保存采样序列：

$$
Y(z)=\sum_{k=0}^{\infty}y(k\Delta t)z^{-k}.
$$

这意味着 $z$ 域模型必须额外假定两个采样点之间的 $u(t)$ 怎样变化。对连续传递函数 $G(s)$，SIT 与 RIT 分别写为

$$
G_{\mathrm{SIT}}(z)=\frac{z-1}{z}\,\mathcal Z\!\left\{\frac{G(s)}{s}\right\},
$$

$$
G_{\mathrm{RIT}}(z)=\frac{(1-z^{-1})^2}{\Delta t\,z^{-1}}\,\mathcal Z\!\left\{\frac{G(s)}{s^2}\right\}.
$$

SIT 对应 zero-order hold，即步内输入常数；RIT 对应步内线性变化。论文强调，这两种映射只在真实输入与各自假设一致、且变化发生在采样时刻时给出精确采样响应（PDF 物理页 2，Eq. (1)–(4)）[pdf:E05]。

严格真分式系统经 SIT 映射会在原点引入极点，对应时域纯延迟。TSSIT 通过在 $z$ 域加入 $r$ 个原点零点补偿，输出写成

$$
y(k\Delta t)=\mathcal Z^{-1}\!\left[z^rG(z)U(z)\right],
$$

其中 $r$ 是补偿零点数。代价是算法由 explicit（显式）变成 implicit（隐式），但可消除 SIT 的一步延迟（PDF 物理页 3，Eq. (5) 与其后说明）[pdf:E06]。

附录从连续状态空间出发：

$$
\dot x(t)=A_cx(t)+B_cu(t),\qquad y(t)=C_cx(t)+D_cu(t).
$$

对 step-invariant 输入 $u(t)=u(k\Delta t)$，SIT 的离散式为

$$
x_{k+1}=A_dx_k+B_du_k,\qquad y_k=C_dx_k+D_du_k,
$$

$$
A_d=e^{A_c\Delta t},\qquad
B_d=\left(\int_0^{\Delta t}e^{A_c\tau}\,d\tau\right)B_c
=\left(e^{A_c\Delta t}-I\right)A_c^{-1}B_c.
$$

TSSIT 保留相同 $A_d,B_d$，但状态更新使用 $u_{k+1}$：

$$
x_{k+1}=A_dx_k+B_du_{k+1}.
$$

这正是“用当前区间末端输入补偿一步延迟”的状态空间版本（PDF 物理页 11–12，Appendix，Eq. (16)–(22)）[pdf:E12][pdf:E13]。

对 ramp-invariant 输入，论文假设

$$
u(t)=u_k+\frac{u_{k+1}-u_k}{\Delta t}(t-k\Delta t),
$$

并得到

$$
x_{k+1}=F_dx_k+G_du_k+H_du_{k+1},\qquad y_k=C_dx_k+D_du_k,
$$

其中

$$
F_d=e^{A_c\Delta t},
$$

$$
G_d=\left[e^{A_c\Delta t}(-I+A_c\Delta t)+I\right]
(A_c^2\Delta t^2)^{-1}B_c\Delta t,
$$

$$
H_d=\left[e^{A_c\Delta t}-I-A_c\Delta t\right]
(A_c^2\Delta t^2)^{-1}B_c\Delta t.
$$

工程 intuition 是：$G_d$ 和 $H_d$ 分别给步首、步末输入分配权重，因此能表达一段线性爬升，而不是把整步压成单个样值（PDF 物理页 12，Appendix，Eq. (23)–(29)）[pdf:E13]。

**关键限制**也直接来自这套推导：所谓“精确”是相对于所选 step/ramp 输入模型的采样点精确；一旦真实步内轨迹既非常数也非线性，误差不会因使用 z 变换自动消失。adaptive discretization 的本质，就是在不同局部输入模型之间切换，而不是消除所有离散误差。

## § 7 — 实验设计与结论

**问题 1：不同离散器在已知解析解的简单电路上是否按输入类型表现不同？** → 作者用 $R=1\ \Omega$、$L=0.05\ \mathrm{mH}$、时间常数 $\tau=50\ \mu s$ 的 RL 电路施加 100 V 阶跃，比较 FE、TR、SIT、TSSIT、RIT 和解析解；又把步长增至 $5\tau=250\ \mu s$。→ TSSIT 在 50 μs 和 250 μs 都与阶跃解析采样响应重合；SIT 有一步延迟；FE 在大步长不收敛，TR 出现衰减振荡，RIT 仍稳定但不如 TSSIT 准确（PDF 物理页 3–4，Fig. 2–3）[pdf:E06][pdf:E14]。

**问题 2：稳态正弦与突然变化是否需要不同方法？** → 同一 RL 网络以 2 kHz 正弦激励、步长 10 μs 仿真，并在波形中加入突然变化。→ 稳态正弦时 RIT 最接近解析解；突变发生后 TSSIT 更接近正确暂态。这直接支持“按输入 regime 切换”，而不是固定选一个方法（PDF 物理页 4，Fig. 4）[pdf:E07]。

**问题 3：结论能否从 nodal RL 扩展到 state-space RLC？** → 作者用 $R=1\ \Omega$、$L=10\ \mathrm{mH}$、$C=25\ \mu\mathrm F$、10 V 阶跃的 RLC 系统，在 50 μs 和 250 μs 下比较方法。→ 50 μs 时 TSSIT 与解析解匹配，SIT 有相位延迟；250 μs 时 TSSIT 仍匹配，TR 出现 frequency warping，RIT 和 SIT 产生不同程度误差（PDF 物理页 5，Fig. 5–7、Eq. (7)–(8)）[pdf:E15]。

**问题 4：adaptive 策略能否消除全系统中的 TR 伪振荡？** → 在 VSC-HVDC offline model 中中断 converter 2 三相电源，初始化用 TSSIT、稳态用 RIT、已知中断时刻切回 TSSIT。→ Fig. 12 中 TR 在电流归零附近产生明显伪振荡，adaptive 曲线没有；作者还指出实验电流在该时刻没有振荡（PDF 物理页 9，Fig. 12 与 Step 1–3）[pdf:E11]。

**问题 5：HIL 稳态结果是否接近真实装置？** → 设 $V_{dc}=500$ V、$P_2=3000$ W、$Q_1=Q_2=2000$ VAr，对比 HIL 和 4 kW 实验示波器波形。→ 实验 dc-link 电压用直流表测得 497–502 V；电流频率均为 60 Hz，HIL 与实验 rms 分别为 13.8 A 和 13.5 A。论文据此判断稳态结果接近，但也承认探头与 I/O 导致小偏差（PDF 物理页 9，Fig. 13–14、Case 1）[pdf:E16]。

**问题 6：闭环暂态是否既稳定又比 offline simulation 更真实？** → Case 2 保持 $P_2=3000$ W、$Q_1=Q_2=2000$ VAr，把 $V_{dc}$ reference 从 420 V 变到 560 V，再变到 440 V；Case 3 保持 dc-link reference，令三路功率 reference 多次变化并发生 power reversal。→ HIL 与实验的 dc-link 和功率耦合扰动相似，offline simulation 则没有出现部分尖峰；作者报告 HIL/实验中的 PI 增益需相对 offline 值轻微重调，幅度为 ±20%（PDF 物理页 10，Fig. 15–16、Case 2/3；PDF 物理页 11–12，Fig. 17–18）[pdf:E17][pdf:E10][pdf:E18][pdf:E19]。

论文没有给出统一的误差范数、统计重复次数、deadline miss 计数或完整的计算资源表。因此，实验有力证明了“波形级可行性”和“与单套 4 kW 装置的一致性”，但不能外推为对所有拓扑、所有输入分类误差和所有实时平台的普遍精度保证。

## § 8 — Take-aways

**5 句话：**

1. HIL 的离散误差不仅由步长决定，还由采样间输入轨迹的假设决定（PDF 物理页 2，Section II）[pdf:E05]。
2. TSSIT 适合阶跃和突变，能消除 SIT 的一步延迟；RIT 更适合稳态正弦的局部线性变化（PDF 物理页 3–4，Eq. (5)、Fig. 3–4）[pdf:E06][pdf:E14][pdf:E07]。
3. 把各方法的矩阵预计算后按输入 regime 切换，使这种选择可以进入严格实时循环（PDF 物理页 2，adaptive 方法说明）[pdf:E04]。
4. 在 4 kW VSC-HVDC 案例中，10 μs HIL 的稳态和暂态波形总体接近实验，并比理想化 offline simulation 呈现更多真实 I/O、传感器和参数效应（PDF 物理页 9–12，Fig. 13–18）[pdf:E16][pdf:E17][pdf:E10][pdf:E18][pdf:E19]。
5. 论文最强的工程启示是：实时求解器应把“输入形态和事件时刻”当作数值模型的一部分，而不是只把开关信号当作外部数据。

**3 句话：** z-transform 方法没有天然优于 TR；只有当输入模型与真实步内轨迹匹配时，它才更准确。论文用 RIT 处理稳态、TSSIT 处理突变，并通过预计算矩阵满足实时性。证据支持该机制在一套 VSC-HVDC HIL/实验系统上有效，但没有证明在线输入分类和参数漂移下仍然稳健。

**1 句话：** 这篇论文把固定离散器改造成了一个随输入机制切换的实时 hybrid solver（混合求解器）。

## § 9 — 最脆弱的假设

最脆弱的假设是：**系统能够在正确时刻被可靠地判定为 step-like 或 ramp-like，并立即切换到对应的预计算模型。** 如果这个假设不成立，论文的核心贡献会直接退化，因为 SIT/TSSIT/RIT 的“精确性”本来就只对各自的输入保持假设成立（PDF 物理页 2，Eq. (2)–(4)；PDF 物理页 12，Eq. (23)–(27)）[pdf:E05][pdf:E13]。

论文给出的正面证据是：简单 RL/RLC 输入类型由实验设计者明确指定；VSC-HVDC 案例中，稳态正弦使用 RIT，初始化和计划好的电源中断时刻使用 TSSIT，Fig. 12 的结果确实优于 TR（PDF 物理页 9，Step 1–3 与 Fig. 12）[pdf:E11]。但这更接近 **oracle policy（先验知道事件的策略）**，不是一个被验证的在线分类器。论文没有报告切换阈值、滞回规则、噪声下误分类率、混合输入时如何选择，也没有测试输入 regime 在相邻步频繁翻转时的稳定性。

这个假设在真实系统中可能失效的原因有三类。其一，PWM、控制器饱和、传感噪声和故障共同作用时，步内输入可能既不是常数也不是线性函数。其二，事件 FPGA 虽能记录步内跳变时间，但数据在下一计算步开始时上传，实际求解策略必须处理信息可用时刻与事件发生时刻之间的因果关系（PDF 物理页 8，event detector 说明）[pdf:E09]。其三，预计算矩阵依赖参数和步长，而论文承认实验与模型参数有差异、温度引起的参数变化未建模，控制器 PI 增益也需 ±20% 重调（PDF 物理页 7，系数说明；PDF 物理页 10，limitations）[pdf:E08][pdf:E10]。

因此，论文证明的是“在正确 mode 已知时，切换离散器有效”，尚未证明“在不确定、噪声和参数漂移下，系统能持续选对 mode”。

## § 10 — 最小复现实验

一周内不必复现整套 VSC-HVDC HIL。最小实验可只验证核心 claim：**输入匹配的离散器在相同步长下是否稳定、准确，并且 adaptive 切换是否对 mode/timing 误差敏感。**

数据与模型直接采用论文的两个可解析案例：RL 电路使用 $R=1\ \Omega$、$L=0.05\ \mathrm{mH}$、100 V 阶跃，测试 $\Delta t=50$ μs 和 250 μs；RLC 电路使用 $R=1\ \Omega$、$L=10\ \mathrm{mH}$、$C=25\ \mu\mathrm F$、10 V 阶跃；另加论文的 2 kHz 正弦、10 μs 步长（PDF 物理页 3–5，Fig. 2–7）[pdf:E06][pdf:E14][pdf:E07][pdf:E15]。

实现 FE、TR、SIT、TSSIT、RIT 和“稳态 RIT / 突变 TSSIT”的 adaptive policy。解析解或高精度连续 ODE 解作为 ground truth。除复现论文的理想 step/sine 外，再人为加入三种扰动：切换时刻偏移 $\{-\Delta t, -\Delta t/2, 0, \Delta t/2, \Delta t\}$；采样噪声；一段同时含正弦和步内斜率变化的混合输入。

测量四类指标：采样点最大绝对误差和 NRMSE、相位误差、伪振荡能量、每步运行时间及 deadline miss。支持论文 claim 的结果应当是：理想阶跃下 TSSIT 在采样点接近解析解，稳态正弦下 RIT 误差最低，正确切换的 adaptive policy 在大步长下显著减少 TR 的伪振荡。反驳或削弱 claim 的结果是：只要切换偏移半个到一个步长，adaptive 优势就消失，或者 mixed input 下固定方法/小幅 substepping 同样准确且更稳健。

这个实验的价值在于把“公式在理想输入下成立”和“实际 adaptive selector 可用”分开验证。

## § 11 — 最强反例设计

最强反例不是再找一个 TR 表现更好的平滑波形，而是取消论文策略中的事件先验，并保持其余硬件、控制器和步长完全相同。

具体做法是：在 VSC-HVDC HIL 中随机触发未预告的电源跌落、reference reversal、PWM 饱和和相邻步内多次开关事件；事件时刻相对 10 μs 网格均匀分布。对比四个同 deadline 方案：固定 RIT、固定 TSSIT、论文式 adaptive policy、以及按精确事件时刻做局部 substep 的 event-aware baseline。每个方案都必须使用同一 Target 1/Target 2、同一控制器和同一 I/O，避免把硬件真实性差异误归因于离散器（PDF 物理页 8，Fig. 10–11 的平台；PDF 物理页 9，Fig. 12 的 adaptive/TR 对比）[pdf:E09][pdf:E11]。

攻击点有两个。第一，论文在全系统中直接展示 adaptive 对 TR 的优势只来自 planned supply interruption 的 offline comparison；HIL 与实验的接近并没有同时给出固定 RIT、固定 TSSIT 或其他 event-aware solver 的 ablation。第二，HIL 比 offline 更像实验，可能部分来自真实 I/O 延迟、传感器偏置、供电畸变和参数不一致，而不是 adaptive discretization 本身；论文自己列出了这些差异（PDF 物理页 10，Case 3 与 limitations）[pdf:E10]。

若随机事件下论文式 selector 经常晚切、误切，或 event-aware substep 在相同计算预算下稳定胜出，那么更合理的解释将是：**论文证明了“正确选择输入模型”的价值，但没有证明其具体 adaptive 实现是一般可用的实时选择机制。** 这会直接击中核心机制，而不是只指出平台老旧或案例规模有限。

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty：构建“误差预算驱动、可证伪的实时离散器”，把输入类型选择改写为带 deadline 的在线 hybrid estimation 问题。** 本领域高影响工作通常不仅要求波形更准，还要给出实时可实现性、稳定性边界、误差指标和真实硬件验证；本文已经具备 HIL 与 4 kW 实验链条，但缺少对 mode 识别不确定性的处理（PDF 物理页 8–12，硬件与验证链）[pdf:E09][pdf:E18][pdf:E19]。

**（a）未满足需求。** 真实输入可能是阶跃、斜坡、PWM ripple、噪声和参数漂移的混合体，预先把工况标成 RIT 或 TSSIT 不够。论文的系数依赖参数，且实验参数与模型有偏差、温度变化未建模（PDF 物理页 7、10）[pdf:E08][pdf:E10]。

**（b）可能的研究价值。** 新系统不再问“当前输入叫什么类型”，而是在每一步估计各候选离散器的局部 residual 和误差上界，在满足 worst-case deadline 的候选中选择预测误差最小者；若所有候选都超过误差预算，则触发一次受限 substep。这样研究目标从“经验式 mode switching”变成“误差与实时性联合保证”。

**（c）可借鉴的相邻工具。** 候选方法可结合 hybrid-systems observer（混合系统观测器）、online change-point detection（在线变点检测）、embedded error estimation（嵌入式误差估计）和 verified worst-case execution-time analysis（可验证最坏执行时间分析）。这些是研究设计方向，不是本文已实现的组成。

**（d）第一个证伪实验。** 在论文的 RL/RLC 与 VSC-HVDC 工况上生成随机事件时刻、混合输入和参数漂移；比较 oracle selector、论文式 planned selector、误差预算 selector、固定 RIT/TSSIT 和 event-aware substep。在相同 10 μs deadline 下同时统计误差、mode 误判、切换抖动和 deadline miss。若新方法不能在非理想输入下稳定优于固定方法，或误差界经常失效，该方向立即被证伪。

**（e）与本文的实质区别。** 本文根据预定义的输入语义在预计算矩阵间切换；候选工作根据在线可观测的误差证据和计算预算决策，并允许“没有任何现有模式可信”这一状态。它改变了问题定义：从选择 step/ramp 近似，转向在事件与参数不确定性下维持可验证的实时精度。
