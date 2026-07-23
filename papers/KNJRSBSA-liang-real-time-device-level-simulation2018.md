# Real-Time Device-Level Simulation of MMC-Based MVDC Traction Power System on MPSoC

作者：Tian Liang；Venkata Dinavahi  
出处：IEEE Transactions on Transportation Electrification  
年份：2018  
DOI：10.1109/TTE.2018.2823059  
Zotero key：KNJRSBSA  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述的研究问题**是：怎样在同一套实时硬件中，同时保留 MMC（modular multilevel converter，模块化多电平换流器）牵引供电系统的系统级电磁暂态，以及 IGBT/diode 的开关、损耗和结温等器件级暂态。传统 HIL（hardware-in-the-loop，硬件在环）实现多把注意力放在电机和推进系统上，功率电子换流器通常只用简化的系统级开关模型；这会隐藏 turn-ON/turn-OFF delay、反向恢复、tail current、瞬时功率损耗和结温等直接决定器件应力的量。作者因此把“能否在实时 deadline 内算完”与“能否看到器件物理过程”放在同一个问题里处理。（PDF 物理页 1，Abstract 与 Section I）[pdf:E01][pdf:E02]

这个问题重要，不只是因为模型更细，而是因为牵引电源的控制、保护和热设计依赖峰值应力，而峰值往往出现在很短的换流过程里。论文给出的目标尺度相差 250 倍：全系统按 25 μs 步长推进，选定器件模型按 100 ns 步长解析，并要求二者在一颗 Xilinx Zynq MPSoC 上实时完成。（PDF 物理页 1，Abstract）[pdf:E01] 若成立，这种实现可以在不反复制造高成本原型的前提下，检查 dc-link 控制、故障过程、器件损耗和热累积之间的联动。

需要先限定“价值”的边界：本文证明得最直接的是**在给定模型和给定工况下，计算能够按时完成，并与两套离线软件的波形接近**；“对真实器件应力的预测同样准确”还依赖行为模型是否能跨工况泛化，这正是后文最需要审视的部分。

## § 2 — 前人工作与不足

**相关文献中的已有结论，仅按本文的综述来复述。**器件级模型大致有三条路线：analytical model（解析模型）、numerical model（数值模型）和 behavioral model（行为模型）。解析与数值模型把非线性物理方程直接带入网络求解，精细但迭代和计算负担较重；行为模型绕开部分内部物理求解，用可辨识的输入输出关系预测工作点，更适合实时计算。本文引用的代表包括 Hefner 的 IGBT 解析模型、finite-element 参数提取、3-D lumped thermal network，以及 Hsu–Ngo 的 Hammerstein IGBT 行为模型；作者此前也做过基于 Hammerstein configuration 的 SoC 实时电热模型。（PDF 物理页 1，Section I；PDF 物理页 16，References [35]–[50]）[pdf:E02][pdf:E27]

作者认为单一 Hammerstein model 的关键不足不是“完全没有动态”，而是它通常把一个 nonlinear static block 与一个 LTI（linear time-invariant，线性时不变）动态块串联，无法明确表达“门极载流子必须先充放电到阈值，主开关暂态才开始”的前置条件。论文采用的 Wiener–Hammerstein configuration 把静态块夹在前后两个 time-variant dynamic blocks 之间：前块处理 carrier charge/discharge，静态块给出温度依赖的 I–V/Norton 参数，后块重建 reverse recovery、tail current 和功率波形。（PDF 物理页 2，Section I；PDF 物理页 4，Table I、Fig. 3 与 Section III-A）[pdf:E04][pdf:E08]

此前实时系统还有两个工程缺口。第一，系统级模型常把换流器简化，不能直接给出器件应力；第二，把细器件模型、带饱和的变压器、MMC 网络和控制全部放进同一实时调度，会同时遇到矩阵求解、非线性迭代、跨核通信和多时间尺度问题。本文的回应不是让所有计算都在 FPGA 上展开，而是根据依赖结构把任务拆到 PL、Cortex-R5 和四个 Cortex-A53 核上。这里的“新颖性”只能按本文自身定位理解；由于本任务不做外部相关工作检索，不把它表述为经过独立检索确认的 novelty。

## § 3 — 重建作者的思考路径

下面是**基于证据的逆向重建**，不是作者逐字写出的推理过程。

第一步，先接受实时仿真的硬约束：每一步必须在 deadline 前结束。若直接采用完整半导体物理模型，网络方程的非线性和迭代成本会过高；因此需要把器件“压缩”为网络求解器容易 stamp 的形式。作者把每个 IGBT/diode 化为 conductance 与 VCCS（voltage-controlled current source，压控电流源）的 Norton equivalent，再把半桥或全桥 submodule 逐层约简成一个等效 conductance 加一个等效电流源。（PDF 物理页 3，Fig. 2 与 Eq. (1)–(11)）[pdf:E05][pdf:E06]

第二步，作者注意到普通静态 I–V 加一个事后动态块会把因果顺序弄错：开关命令到达后，门极电容先经历充电、Miller plateau 和阈值越过，之后 collector current 与 collector-emitter voltage 才进入主暂态。于是，最自然的结构不是“静态块后接动态”，而是“前动态状态机 → 静态网络参数 → 后动态波形”。Table I 和 Fig. 3 正好把这一想法组织成 carrier charge、static electrical characteristic、dynamic electrical characteristic、power/thermal 四个阶段。（PDF 物理页 4，Table I 与 Fig. 3）[pdf:E08]

第三步，为避免重新引入昂贵的内部物理方程，作者从 datasheet 曲线提取低阶关系：电容随电压变化、delay 随 gate resistance 近似线性、静态 I–V 按温度插值、reverse recovery 和 tail current 用线性段加 first-order decay 表示。（PDF 物理页 5，Fig. 4；PDF 物理页 6，Fig. 5–6）[pdf:E09][pdf:E11][pdf:E12]

第四步，再根据计算形态做异构映射：PL 负责适合并行的系统矩阵运算，Cortex-R5 负责控制，四个 Cortex-A53 分别计算选定 submodule 的器件级暂态。作者明确说明，小规模 submodule 计算高度串行，拆到多核反而会被 core-to-core communication latency 抵消。（PDF 物理页 9，Fig. 12 与 Section IV-B）[pdf:E18]

这条思路的核心不是单独发明某个公式，而是把**可实时的等效网络、因果正确的开关状态机、数据表驱动的低阶器件模型和异构调度**拼成一个闭环。

## § 4 — 核心 Intuition

把功率器件看成一个“有记忆的 Norton 元件”：开关命令先驱动门极载流子充放电，达到阈值后才切换温度相关的静态 conductance/VCCS，最后再生成 reverse recovery、overshoot、tail current、损耗与结温。（PDF 物理页 5–6，Fig. 4–6）[pdf:E09][pdf:E11][pdf:E12] 全系统不必都用 100 ns 推进，而是让 25 μs 的网络层与 100 ns 的选定器件层分工运行，再把并行矩阵、实时控制和串行器件状态机分别映射到 PL、R5 和 A53。（PDF 物理页 1，Abstract；PDF 物理页 9–10，Section IV 与 Tables II–IV）[pdf:E01][pdf:E18][pdf:E19] 方法能奏效的关键，是用低阶、可 stamp、可调度的行为近似保留作者认为最重要的物理因果顺序，而不是追求完整半导体内部物理。

## § 5 — 具体方法与完整 Pipeline

以 Fig. 1 的牵引系统为例，输入是 220 kV public grid、三相降压变压器、grid-side 三相 half-bridge MMC、25 kV traction feeder，以及 load-side 单相 full-bridge MMC。三相 MMC 用 dc-link voltage closed-loop control；单相 MMC 用 open-loop control 在额定工况运行。half-bridge 侧成本较低但缺少 dc-fault blocking，full-bridge 侧增加器件数量换取故障阻断能力。（PDF 物理页 2，Fig. 1 与 Section II）[pdf:E03][pdf:E04]

1. **网络建模。**每个 IGBT module 被写成 conductance 与 VCCS，半桥/全桥再做层次化 Norton reduction，得到可直接进入节点导纳矩阵的 submodule stamp。（PDF 物理页 3，Fig. 2 与 Eq. (1)–(11)）[pdf:E05][pdf:E06] 变压器采用 admittance-matrix 离散模型，以 trapezoidal rule 更新 history term；磁饱和通过 Newton–Raphson iteration 求解。（PDF 物理页 4，Eq. (12)–(18)）[pdf:E07]

2. **接收 gate command 并推进前置动态。**模型从 datasheet 的 gate-charge、low-signal capacitance 和 delay–resistance 曲线构造等效电容网络。turn-ON 被分成五个 carrier-charge 区间，turn-OFF 被分成四个 discharge 区间；只有当 gate-emitter capacitor 越过相应阈值后，主电气暂态才被触发。（PDF 物理页 5–6，Fig. 4–5、Eq. (19)–(23)）[pdf:E09][pdf:E10][pdf:E11][pdf:E12]

3. **更新静态器件 stamp。**作者把 IGBT/diode 的静态特性划分为 low-current 与 normal-current 两区，分界设为 rated current 的 60%；每一区用温度依赖 conductance 与并联 VCCS 表示，并在 25 °C 与 125 °C 数据之间线性插值。（PDF 物理页 6–7，Fig. 6 与 Eq. (24)–(29)）[pdf:E12][pdf:E13]

4. **重建后置动态。**diode turn-OFF 用“静态 → 线性反向恢复 → first-order decay”三段描述；IGBT turn-ON 用 first-order rise，turn-OFF 用线性下降加 first-order tail。作者再把归一化电流、电压和瞬时功率分成 linear、square 与 exponential 区段，以积分得到 switching loss。（PDF 物理页 7–8，Fig. 7–9 与 Eq. (30)–(34)）[pdf:E13][pdf:E14][pdf:E15][pdf:E16]

5. **热网络更新。**单器件损耗作为 thermal RC network 的受控源，经过 junction-to-case、case-to-heatsink、heatsink-to-ambient 阻抗得到结温；论文采用每个 IGBT module 配置 10 K/kW water-cooled heatsink，并用 Eq. (36) 的离散递推更新多层热节点。（PDF 物理页 8–9，Fig. 10、Eq. (35)–(36)）[pdf:E16][pdf:E17]

6. **多速率与硬件映射。**PL 运行 system-level circuit matrix；Cortex-R5 在 600 MHz 下计算 PD-PWM 与 dc-link control；四个 1.2 GHz Cortex-A53 分别计算各 leg 中选定的一个 submodule 器件暂态。控制信号从 R5 发往 PL/A53，PL 把 history term 送往 A53，A53 的结果在下一 system step 回写 PL。（PDF 物理页 9–10，Section IV-B）[pdf:E18][pdf:E19] 因而本文并不是把所有 submodule 的每个器件都以 100 ns 全量求解，而是把选定 submodule 作为器件级窗口。

7. **系统加速与输出。**作者还用 TLM（transmission line modeling，传输线建模）把 12×12 admittance matrix 拆成两个 6×6 矩阵，并报告 matrix calculation 的平均误差在 2% 内，以换取实时执行。数字结果经 DAC 送到 oscilloscope，系统级波形与 PSCAD/EMTDC 比较，器件级开关和热波形与 SaberRD 比较。（PDF 物理页 9，Fig. 11；PDF 物理页 12，Fig. 14 附近正文）[pdf:E17][pdf:E22]

输出包括 terminal/source voltage、arm current、FFT、submodule capacitor voltage、IGBT turn-ON/turn-OFF current、diode reverse recovery、device loss、junction temperature，以及 dc-link/load-side fault response。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有形式化数学，但重点是**可实时离散化与分段近似**，不是证明型理论。

**1. Norton reduction。**半桥 submodule 的等效 conductance 由串并联约简得到：

\[
 g_{\mathrm{HBSM}}=\frac{g_1 g_{C1}}{g_1+g_{C1}}+g_2,
 \qquad
 g_j=g_{Sj}+g_{Dj},\quad i_j=i_{Sj}+i_{Dj}.
\]

直觉是把每个开关器件及反并联 diode 都转换为“导纳 stamp + history/current injection”，网络求解器每一步只需更新参数，而不必重新展开器件内部方程。full-bridge 的 Eq. (5)–(11) 是同一思想的更大规模代数消元。（PDF 物理页 3，Eq. (1)–(11)）[pdf:E06]

**2. 变压器离散。**核心形式是

\[
 \mathbf i_T(t)=\mathbf G_T\mathbf v_T(t)+\mathbf{hist}_T(t-\Delta t),
\]

其中 \(\mathbf G_T\) 由 winding resistance、leakage inductance 与 trapezoidal step 构成，过去状态进入 \(\mathbf{hist}_T\)。磁化曲线的非线性再用

\[
 \mathbf J_T(\mathbf i_{j+1}-\mathbf i_j)=-\mathbf F_T(\mathbf i_j)
\]

做 Newton–Raphson correction。工程上，这把“线性网络 stamp”和“饱和非线性修正”分开，便于在固定步长中调度。（PDF 物理页 4，Eq. (12)–(18)）[pdf:E07]

**3. 门极载流子前置动态。**datasheet 的三种电容满足

\[
 C_{ies}=C_{GE}+C_{GC},\qquad C_{res}=C_{GC},\qquad C_{oes}=C_{GC}+C_{CE}.
\]

turn-ON delay 被近似为一阶 RC 时间：

\[
 t_{d,\mathrm{ON}}=K_{\mathrm{ON}}C_{GE}\bigl(R_{G(\mathrm{int})}+R_G\bigr).
\]

它解释了 Fig. 4(d) 中 delay 对 gate resistance 的近似线性关系，也把“开关命令”与“主电流暂态”之间插入了物理上必要的等待状态。（PDF 物理页 5，Eq. (19)–(22) 与 Fig. 4）[pdf:E09][pdf:E10] turn-OFF 的 Eq. (23) 在同一 RC 项后增加常量 \(t_{stage2}\)；值得注意的是，PDF 的左端仍印作 \(t_{d(on)}\)，但上下文和右端 \(K_{OFF}\) 明确在讨论 turn-OFF，这应在复现时作为符号/排版歧义核对。（PDF 物理页 6，Eq. (23)）[pdf:E12]

**4. 温度插值与静态 stamp。**Eq. (24)–(29) 可概括为：对 \(x\in\{g_{low},v_{low},g_{high},v_{high}\}\)，

\[
 x(T_j)=\frac{T_j-T_{25}}{T_{25}-T_{125}}\bigl(x^{T_{25}}-x^{T_{125}}\bigr)+x^{T_{25}},
 \qquad i(T_j)=v(T_j)g(T_j).
\]

这样只需两组温度曲线就能得到中间温度的 Norton 参数。代价是默认温度依赖在 25–125 °C 内近似线性，并且 60% rated-current 的两区拼接足够平滑。（PDF 物理页 6–7，Fig. 6 与 Eq. (24)–(29)）[pdf:E12][pdf:E13]

**5. 恢复与尾电流。**diode reverse-recovery time 采用

\[
 t_{rr}=\frac{2Q_{rr}}{I_{rr}},
\]

对应一个三角形电荷近似；之后的衰减用 first-order curve。IGBT tail current 则用线性段与指数衰减拼接。（PDF 物理页 7，Fig. 8 与 Eq. (30)）[pdf:E14] 数学审阅中有一个明确警报：PDF 的 Eq. (31) 印为

\[
 \frac{dI_c}{dt}=\frac{L_{stray}}{V_L}.
\]

正文把 \(V_L\) 定义为 overshoot voltage、\(L_{stray}\) 为 stray inductance；按通常量纲，右侧是 s/A，而左侧是 A/s，因此原式至少存在量纲或排版问题，不能不经核对直接写进复现代码。（PDF 物理页 7，Eq. (31)）[pdf:E14]

**6. 损耗与热。**Fig. 9 把 diode/IGBT 的瞬时功率波形拆为 \(x\)、\(x^2\) 和 \(e^{-x}\) 等区段，Eq. (32)–(34) 对各段积分得到 turn-ON/turn-OFF energy。（PDF 物理页 8，Fig. 9 与 Eq. (32)–(34)）[pdf:E15][pdf:E16] 热网络的紧凑关系写成

\[
 T_{vj}(t)=P_{loss}(t)\bigl(Z_{thjc}+Z_{thch}+Z_{thha}\bigr)+T_{amb},
\]

而实际离散执行由 Eq. (36) 的多支路递推完成；前者给物理意义，后者才是 fixed-step implementation。（PDF 物理页 8–9，Fig. 10 与 Eq. (35)–(36)）[pdf:E16][pdf:E17]

## § 7 — 实验设计与结论

**问题 1：平台是否真的满足实时 deadline？ → 实验：测资源与各计算/通信路径 latency。 → 答案：在本文规模下满足，但裕量很紧。**XCZU9EG 使用 56 个 BRAM（3%）、908 个 DSP（36%）、180895 个 flip-flop（33%）和 200167 个 LUT（73%）。四个 A53 器件模型核的报告 latency 均为 90 ns，R5 控制为 7290 ns；PL system calculation 为 22.24 μs，R5→A53 和 R5→PL 分别为 120 ns 与 1840 ns，最大/平均总 delay 为 24.6/24.2 μs，低于 25 μs system step；90 ns 也低于 100 ns device step。（PDF 物理页 10，Tables II–IV 与 Section V-A）[pdf:E19] 这证明“可运行”，同时也显示最大路径只剩 0.4 μs 余量，扩展模型规模前不能默认 timing closure 仍成立。

**问题 2：系统级电压、电流与频谱是否接近离线 EMT 参考？ → 实验：把 oscilloscope real-time traces 与 PSCAD/EMTDC 波形逐图对照。 → 答案：在展示的稳态窗口内形状和标注的 FFT/THD 接近。**Fig. 13 比较了三相 terminal/source voltage、单相 terminal voltage、三组 FFT 以及三相 arm current；图上还显示约 3 kHz carrier harmonic。（PDF 物理页 11，Fig. 13）[pdf:E20] 但论文主要给 visual overlay 和少量频谱读数，没有给覆盖全时间窗的 RMSE、最大误差或置信区间。

**问题 3：器件级开关细节与 capacitor balance 是否被保留？ → 实验：把 real-time IGBT/diode transient 与 SaberRD 比较，并观察四个 submodule capacitor voltage。 → 答案：展示波形能重现 overshoot、reverse recovery 和 tail current。**单相 MMC capacitor voltage 报告为 2758–2860 V，三相 MMC 为 2780–2849 V；对应 variation percentage 分别为 3.5% 与 2.4%。作者还说明 TLM 矩阵拆分的平均误差在 2% 内。（PDF 物理页 12，Fig. 14 与邻近正文）[pdf:E21][pdf:E22] 这些结果支持所选稳态窗口，但不能外推为所有 modulation、fault severity 或器件参数下的误差上界。

**问题 4：损耗模型是否能驱动合理的热响应？ → 实验：把 real-time junction temperature 与 per-thermal-step average loss 同 SaberRD 对照。 → 答案：展示的 IGBT/diode 温升排序和冷却区间一致。**正文报告 S1、D2、S2、D1 的每热步损耗峰值约为 32 kW、3.4 kW、90 kW、2.45 kW，并据此指出 IGBT loss 至少是 diode 的八倍；Fig. 15 中 real-time 与 off-line 曲线成对给出。（PDF 物理页 13–14，Fig. 15 与邻近正文）[pdf:E23][pdf:E25]

**问题 5：控制和故障过程是否能在实时模型中运行？ → 实验：启动、dc-link fault 与 load-side fault。 → 答案：三相 MMC closed loop 把 dc-link 稳定在 45 kV，图中实时与 PSCAD 曲线呈相同的故障和恢复形态；正文给出 dc-link fault 在 11 s 施加。**（PDF 物理页 14，Fig. 16 与邻近正文）[pdf:E24][pdf:E25]

综合来看，实验充分支持一个较窄但清楚的 claim：**在作者选定的 MMC 规模、参数、控制与测试窗口内，MPSoC 能按时产生与 PSCAD/SaberRD 接近的系统级和器件级波形。**作者在结论中也把验证对象明确写为 PSCAD/EMTDC 与 SaberRD。（PDF 物理页 15，Section VI）[pdf:E26] 源 PDF 未报告独立的 double-pulse hardware measurement、calorimetric loss measurement 或结温传感实验，所以不能把 simulation-to-simulation agreement 自动等同于真实器件精度。

## § 8 — Take-aways

**5 句话：**这篇论文要解决的是全系统 EMT 与器件 switching/thermal 两个时间尺度无法同时实时计算的问题。它用前动态—静态—后动态的 Wiener–Hammerstein configuration 保留 gate charge、静态 I–V、reverse recovery、tail current 和热累积的因果顺序。它把网络矩阵放到 PL、控制放到 R5、选定 submodule 的器件模型放到四个 A53，从而达到 25 μs system step 和 100 ns device step。资源、latency、稳态、器件暂态、热和故障图表共同表明该实现能在本文规模下实时运行并接近 PSCAD/SaberRD。最需要保留的警惕是：实时性证据很强，独立物理精度与跨工况泛化证据较弱。（PDF 物理页 4、9–15）[pdf:E08][pdf:E18][pdf:E19][pdf:E20][pdf:E21][pdf:E23][pdf:E24][pdf:E26]

**3 句话：**方法的本质是把器件物理压缩成可 stamp 的低阶状态机，再通过 heterogeneous MPSoC 做多速率协同。实验说明 nominal case 下 timing closure 和 software-reference agreement 都能成立。论文没有证明 datasheet 拟合在未见过的温度、寄生参数、老化和故障组合下仍能给出可靠应力。（PDF 物理页 5–10、12–15）[pdf:E09][pdf:E14][pdf:E19][pdf:E21][pdf:E26]

**1 句话：**这是一套工程上聪明的实时器件级近似框架，但它最有价值的下一步不是再多跑几张 nominal waveform，而是给器件应力精度建立独立物理验证和可量化边界。

## § 9 — 最脆弱的假设

最脆弱的假设是：**由少量 datasheet 曲线构造的、可分离的低阶行为模型，能够在真实 MMC 的多变量工作空间中继续准确预测 switching stress 与 thermal stress。**这个假设一旦不成立，系统即使每一步都在 100 ns/25 μs deadline 内完成，也只是在实时地产生错误的 peak current、overshoot、switching energy 或 junction temperature，论文最初强调的控制与保护价值就会失效。

论文为该假设提供了三类证据：gate delay 对 \(R_G\) 的线性拟合，25/125 °C 的静态/动态曲线，以及同 SaberRD 的器件波形和热波形对照。（PDF 物理页 5–8，Fig. 4、6–10；PDF 物理页 12–13，Fig. 14–15）[pdf:E09][pdf:E12][pdf:E13][pdf:E14][pdf:E15][pdf:E16][pdf:E21][pdf:E23] 这些证据说明模型可以重现其拟合依据和一个离线软件参考，但还没有回答多变量耦合：\(V_{dc}\)、\(I_c\)、\(R_G\)、\(T_j\)、stray inductance、diode temperature、aging 和器件离散性同时变化时，front/static/back blocks 是否仍可近似分离。

缺失的关键证据是独立物理测量与误差边界。源 PDF 没有报告真实 IGBT module 的 double-pulse waveform、实测 \(E_{on}/E_{off}\)、calorimetric loss 或结温对照；同时，60% rated-current 的分区、first-order tail/recovery、Eq. (23) 的符号歧义和 Eq. (31) 的量纲异常都提示复现不能只照抄公式。（PDF 物理页 6–7，Eq. (23)、Eq. (31)；PDF 物理页 15，Conclusion）[pdf:E12][pdf:E14][pdf:E26] 因而这不是“论文一定错”，而是当前证据尚不足以把 simulation fidelity 升格为 physical fidelity。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 220 kV–25 kV 牵引系统，而是**单个 half-bridge submodule 的器件暂态与实时执行成本**。

1. **数据。**从源 PDF 的 Fig. 4、6、7、8、9 数字化 gate-charge/delay、static I–V、\(I_{rr}/Q_{rr}\)、rise/fall time 和 normalized power curves；选 Fig. 14(c)/(f) 作为未参与拟合的波形检查点。（PDF 物理页 5–8、12）[pdf:E09][pdf:E12][pdf:E13][pdf:E14][pdf:E15][pdf:E21]
2. **实现。**用 C++ 或可验证的 Python reference 实现 carrier state machine、Eq. (22)/(23)、温度插值、reverse recovery、tail current、piecewise loss 和一阶 thermal network；固定 device step 为 100 ns。先做一个 IGBT+diode，再接成 half-bridge Norton stamp。
3. **工况。**扫描 \(R_G=0\)–10 Ω，至少取 25 °C 与 125 °C，并在 60% rated current 两侧各取点；再改变一组 \(I_c\) 以检查参数耦合。
4. **测量。**记录 turn-ON/OFF delay、peak current、reverse-recovery peak、tail duration、\(E_{on}/E_{off}\)、温升轨迹，以及每个 100 ns step 的 worst-case execution time。
5. **支持/反驳判据。**这是复现实验自定而非论文报告的阈值：delay 曲线和打印波形的归一化误差若能稳定控制在约 10%，peak loss 误差在约 15%，且目标处理器 worst-case step 不超过 100 ns，则支持“低阶模型可复现论文展示的单器件结果”；若误差在温度、current region 或 \(R_G\) 联合变化时系统性扩大，或 timing 只看平均值而 worst case 超时，则反驳该最小 claim。

这个复现的限制也要写清：PDF 只给曲线图而非原始 datasheet 点集和完整源代码，因此它能验证**模型结构与图形一致性**，不能宣称重现了作者的逐位数值实现。

## § 11 — 最强反例设计

最强的反例是一组**联合变量 double-pulse test**，专门攻击“各 block 可分离、datasheet 低阶拟合可跨工况泛化”的假设，而不是再比较一组 nominal terminal waveform。

实验先只用论文公开的曲线拟合模型参数，然后在独立硬件上同时改变 \(T_j\)、\(R_G\)、\(I_c\)、dc-link voltage、stray inductance 与 commutating diode temperature。关键不是单变量扫描，而是选择两组在论文一维 datasheet 曲线上看起来相近、但 Miller plateau 与 reverse recovery 强耦合程度不同的组合；例如保持 \(R_G\) 和 \(I_c\) 不变，只改变 stray inductance 和 diode temperature。对每组测 \(t_{on/off}\)、\(I_{rr}\)、\(V_{CE}\) overshoot、tail current、\(E_{on/off}\) 与短时温升，并与实时模型逐点比较。

反例成立的标准应预先注册：如果模型仍能匹配 delay，却持续低估 peak current/voltage 或 switching energy，或者同一套参数无法同时解释 turn-ON、turn-OFF 和 reverse recovery，那么 front dynamic、static block 与 back dynamic 的可分离结构就被直接挑战。进一步把该器件误差放回 MMC fault case；若 terminal voltage 仍与 PSCAD 接近、但预测的最坏器件应力明显错误，就证明本文现有的系统级波形验证不足以支撑“准确预测 device stress”的强解释。这个攻击直接利用论文把 delay、静态 I–V、reverse recovery 和 thermal loss 分段拟合的结构事实。（PDF 物理页 4–8，Table I、Fig. 4–10）[pdf:E08][pdf:E09][pdf:E11][pdf:E12][pdf:E13][pdf:E14][pdf:E15][pdf:E16]

## § 12 — Follow-up Research Idea

在 EMT、power electronics 与 FPGA real-time simulation 领域，高影响工作的评价通常同时看四件事：独立物理精度、确定性 deadline、可扩展资源效率，以及对控制/保护决策是否产生实际价值。基于第 9 节的限制，一个非增量的候选方向是：**面向最坏器件应力包络的自校准、多速率实时数字孪生**。这里明确标为候选想法；本任务未做外部相关工作检索，不声称 novelty。

**(a) 未满足需求。**现有实现输出的是 nominal point estimate；但保护设计真正需要知道的是，在器件离散性、寄生参数、温度和老化不确定时，\(I_c\)、\(V_{CE}\)、\(E_{on/off}\) 和 \(T_j\) 的可信上界。仅让一个选定 submodule 以 100 ns 运行，也难以保证未建模 submodule 中没有更热的器件。（PDF 物理页 9，Section IV-B；PDF 物理页 15，Conclusion）[pdf:E18][pdf:E26]

**(b) 研究价值。**把目标从“复现一条参考波形”改成“在实时 deadline 内给出经校准的 stress envelope”，会直接改变 HIL 对保护阈值、热降额和故障容限的用法。它也把 accuracy 与 timing 放在同一个可证伪指标里，而不是分别展示。

**(c) 可借鉴的相邻工具。**可把 set-membership identification、interval arithmetic/reachability、online Bayesian calibration 与 event-triggered adaptive time stepping 结合起来：正常区间用低阶模型和 25 μs system step，检测到 switching/fault event 后只对高风险 submodule 提升到 100 ns 或更细，并让 FPGA/MPSoC scheduler 根据预测误差而不是固定映射分配算力。

**(d) 第一个证伪实验。**在未参与标定的 double-pulse 与 MMC fault 数据上，检查预测包络是否覆盖实测 \(V_{CE}\)、\(I_c\)、\(E_{on/off}\) 和 \(T_j\)，同时记录 worst-case latency。若包络频繁漏掉真实峰值，或为了覆盖峰值而宽到失去保护意义，或自适应调度超过 25 μs/100 ns deadline，这个方向即被证伪。

**(e) 与本文的实质区别。**本文解决的是 nominal behavioral trace 如何映射到一颗 MPSoC；候选方向解决的是**不确定条件下的最坏应力是否能被实时、可校准地包住**。它改变了输出对象、验证标准和调度目标，不只是给现有 pipeline 增加一个模块。
