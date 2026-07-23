# FPGA-Based Device-Level Electro-Thermal Modeling of Floating Interleaved Boost Converter for Fuel Cell Hardware-in-the-Loop Applications

**作者：** Hao Bai; Chen Liu; Shengrong Zhuo; Rui Ma; Damien Paire; Fei Gao  
**出处：** IEEE Transactions on Industry Applications, Vol. 55, No. 5, 2019  
**DOI：** 10.1109/TIA.2019.2918048  
**Zotero key：** Y9DDITL4

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是一个很具体的实时仿真矛盾：燃料电池汽车中的四相 floating interleaved boost converter（FIBC）既需要在控制器 HIL 中实时运行，又需要看见 IGBT 开通、关断和二极管反向恢复期间的纳秒级波形，才能计算开关损耗和结温。普通 system-level 模型用导通压降和电阻表示开关，能算电感电流和母线电压，却把决定损耗与热应力的瞬态细节抹掉；完整器件等效电路又有非线性电容和受控源，通常依赖迭代求解，难以塞进严格的实时预算。论文给出的目标是：FIBC 网络以 500 ns 步长推进，同时以 5 ns 分辨率重建 IGBT 瞬态，再由瞬时损耗在线推算结温。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

器件级电热耦合的物理意义不是“多输出一条温度曲线”，而是闭合一条因果链：开关端口的 \(v_{ce}\) 与 \(i_c\) 在换流期间重叠，形成瞬时功率损耗 \(P_L\)；损耗经芯片、封装、导热脂和散热器的热阻热容网络积累成结温 \(T_j\)；\(T_j\) 又改变 IGBT 的静态特性和 transfer characteristics。这样，HIL 控制器看到的不只是理想电路响应，还能看到控制动作、开关损耗和热应力之间的反馈。[pdf:E03]（PDF 物理页 3，Section II-A）[pdf:E05]（PDF 物理页 5，Fig. 8 与 Eqs. (21)-(22)）[pdf:E06]（PDF 物理页 6，Eq. (23)）

重要性来自控制验证的风险口径。FIBC 用于燃料电池到高压直流母线的接口，具有高升压比和低输入电流纹波，但其非线性和 non-minimum-phase 特性增加了控制设计难度。HIL 可以在不损坏真实功率台架的情况下测试极端工况和故障；如果实时模型漏掉损耗与结温，控制策略即使在电压、电流层面“通过”，也可能在器件热安全上失败。[pdf:E01]（PDF 物理页 1，Introduction）

## § 2 — 前人工作与不足

**论文原文明确声称：** 当时已有 FPGA system-level 实时仿真可利用并行结构把步长压到几十纳秒，但 device-level 模型仍受两类负担夹击：开关瞬态要求极短步长，非线性器件模型又提高了每步计算量。[pdf:E01]（PDF 物理页 1，Introduction）

作者把最接近的方法分成四类。其一，直接从 datasheet 取动态参数并用线性变化近似，会丢失 tail current 与寄生参数效应；其二，对特定拓扑的 Saber 结果做 curve fitting，泛化性不足；其三，基于 gate-charge curve 的模型报告了 100 ns 瞬态步长，仍不足以描述快速开关过程；其四，作者此前基于等效电路线性化的 IGBT behavioral model 使用了严格假设，而且没有加入 diode 与 thermal model。作者更早的 FIBC system-level 工作则只用 two-value resistance 表示 IGBT 和二极管，无法给出开关瞬态。[pdf:E02]（PDF 物理页 2，Introduction）

这篇工作的改变不是把整个非线性器件电路硬塞进网络迭代，而是接受一项受控近似：网络求解只使用静态 Thevenin 等效，器件瞬态由另一个更快的 behavioral model 根据网络状态和器件参数生成；损耗再驱动热网络并反馈温度敏感的电气特性。[pdf:E02]（PDF 物理页 2，Section II-A 与 Fig. 2）

**边界说明：** 上述“前人不足”是本文作者对文献 [13]-[17] 的归纳，本卡没有额外取得这些论文的全文做独立复核，因此不把它升级为跨文献的最终结论，也不据此声称本文具有未经检索确认的 novelty。

## § 3 — 重建作者的思考路径

下面是**基于证据的合理推断**，不是作者逐字叙述的研发过程。

第一步，研究者先保留已经能实时运行的 FIBC 网络模型，因为控制器首先需要可信的电感电流、电容电压和开关状态。显式积分的关键优势是：下一时刻的状态只依赖上一时刻，因此电感、电容可以在当前步解耦为源，把四个结构相同的相支路并行求解。[pdf:E03]（PDF 物理页 3，Figs. 3-5 与 Eqs. (1)-(6)）

第二步，他们意识到把纳秒级开关过程直接反馈进 500 ns 网络方程会破坏实时预算，于是把“影响网络的慢尺度状态”和“决定开关损耗的快尺度波形”分开。网络层每步提供负载电流、导通压降、PWM 与温度相关参数；器件层只在检测到 switching event 后，根据预计算的阶段时长、斜率和时间常数生成 \(v_{ce}\)、\(i_c\) 与 \(P_L\)。[pdf:E02]（PDF 物理页 2，Fig. 2）[pdf:E04]（PDF 物理页 4，Figs. 6-7）

第三步，为避免完整 IGBT 等效电路的迭代，他们把 \(v_{ce}\) 与 \(i_c\) 分别建模，把 \(C_{ge}\) 视为常量、把 \(C_{cg}\) 分段为两个值，并把 turn-on/turn-off 拆成五个可用线性或指数关系推进的阶段。二极管 reverse recovery 和 IGBT tail current 被保留，因为两者直接影响峰值电流和开关能量。[pdf:E04]（PDF 物理页 4，Section II-C 与 Eqs. (7)-(14)）[pdf:E05]（PDF 物理页 5，Eqs. (15)-(20)）

第四步，他们把 datasheet 的 transient thermal impedance 拟合为四项 Foster 网络，以 Backward Euler 离散，从在线损耗得到结温；再在 datasheet 给出的两个温度边界之间线性插值电气特性，实现电到热再回到电的闭环。[pdf:E05]（PDF 物理页 5，Figs. 8-9 与 Eqs. (21)-(22)）[pdf:E06]（PDF 物理页 6，Eq. (23)）

最后，算法结构被翻译成 FPGA 结构：可并行的网络子电路、流水化 transient parameter computation（TPC）、每个 IGBT 独占的动态与热模型，以及用 LUT 代替 \(\exp\)、\(\ln\) 和部分除法。[pdf:E06]（PDF 物理页 6，Figs. 10-11）[pdf:E07]（PDF 物理页 7，Fig. 12）

## § 4 — 核心 Intuition

核心 intuition 是：不必用同一个时间步、同一个求解器同时承担网络动态和器件换流细节。让 500 ns 的静态网络解负责“这一开关事件发生在什么电流、电压和温度条件下”，再让 5 ns 的事件驱动 behavioral model 负责“这次事件的波形与损耗长什么样”，即可在实时预算内保留热计算真正需要的瞬态信息。[pdf:E02]（PDF 物理页 2，Fig. 2）[pdf:E07]（PDF 物理页 7，Table I 与 Fig. 12）

电热闭环的直观含义是：每次开关事件都向热网络注入一小份能量，热网络把许多事件积累成结温；温度再修正下一批开关事件的电气参数。这个分层不是把热过程事后离线计算，而是让热状态成为实时模型的一部分。[pdf:E05]（PDF 物理页 5，Eqs. (21)-(22)）[pdf:E06]（PDF 物理页 6，Eq. (23)）

## § 5 — 具体方法与完整 Pipeline

以四相 FIBC 的一次 IGBT 开通事件为例，完整 pipeline 如下。

1. **网络离散与并行分区。** 四个电感电流与两个电容电压用 Forward Euler 更新。由于更新只依赖上一时间步，电抗元件被替换为注入源，FIBC 被拆成四个相支路与一个输出子电路并行求解。作者报告 500 ns 网络步长，并以离散系统极点位于单位圆内作为数值稳定条件；本文工况下该步长被验证为稳定。[pdf:E03]（PDF 物理页 3，Figs. 3-4 与 Eqs. (1)-(6)）[pdf:E04]（PDF 物理页 4，Section II-B-4）
2. **开关状态识别。** PWM 为高时 IGBT 导通、对应 diode 截止；PWM 为低且电感电流大于零时 diode 导通；若电感电流降为零进入 DCM，则 IGBT 与 diode 都截止。[pdf:E03]（PDF 物理页 3，Fig. 5）
3. **静态网络解与参数准备。** 静态 IGBT 用由输出特性分段线性化得到的 \(V_{\mathrm{ON}}\) 与 \(R_{\mathrm{ON}}\) 构成 Thevenin 等效。网络层给出支路电流、节点电压，并计算动态模型所需的阶段时长、斜率、时间常数与温度相关特性。[pdf:E02]（PDF 物理页 2，Section II-A）
4. **纳秒级开关波形生成。** 开通与关断各分五个阶段。模型使用 gate RC、Miller plateau、二极管 reverse recovery、线性电流变化、分段 \(C_{cg}\) 与指数 tail current，生成 \(v_{ge}\)、\(v_{ce}\)、\(i_c\)。它不是在每个 5 ns 点重新求非线性电路，而是比较 counter 与预计算的阶段区间，选择相应的线性或指数更新模块。[pdf:E04]（PDF 物理页 4，Figs. 6-7 与 Eqs. (7)-(14)）[pdf:E05]（PDF 物理页 5，Eqs. (15)-(20)）[pdf:E07]（PDF 物理页 7，Fig. 12）
5. **损耗与热状态。** 器件层以 \(P_L=v_{ce}i_c\) 计算瞬时损耗。IGBT、diode、thermal grease 与 heat sink 构成热网络；datasheet 的 transient thermal impedance 由四项 Foster 模型拟合，以 Backward Euler 推进结温。[pdf:E05]（PDF 物理页 5，Fig. 8、Fig. 9 与 Eqs. (21)-(22)）[pdf:E07]（PDF 物理页 7，Section III-B）
6. **温度反馈。** IGBT 静态模型和 transfer characteristics 随结温变化；两个 datasheet 温度边界之间采用线性插值。论文没有报告超出这两个边界时采用何种外推或钳位策略。[pdf:E06]（PDF 物理页 6，Eq. (23)）
7. **FPGA 映射。** 实现在 NI LabView FPGA 环境、NI-7975R FlexRio 的 Kintex-7 XC7K410T 上，采用 fixed-point。system-level 以 40 MHz 运行，device-level 以 200 MHz 运行；复杂的 \(\exp\)、\(\ln\)、部分除法、transfer curve 和 reverse-recovery curve 用 LUT。[pdf:E06]（PDF 物理页 6，Section III 与 Fig. 11）
8. **实时输出。** 200 MHz 流水线的一次 initiation interval 是 1 cycle，相邻动态模型输出间隔为 5 ns；每个 IGBT 有独立的动态与热模型，网络求解器、control unit 与 TPC 在 system-level 共享。[pdf:E07]（PDF 物理页 7，Table I、Fig. 12 与 Section III-C）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有明确的形式化模型，但重点是把物理过程改写成 FPGA 可流水化的差分和分段函数，而不是提出新的连续系统理论。

**网络层。** 对电感与电容使用 Forward Euler：

\[
i_L^{n+1}=i_L^n+\frac{h}{L}v_L^n,\qquad
v_C^{n+1}=v_C^n+\frac{h}{C}i_C^n.
\]

这里 \(h\) 是 system-level 步长。工程直觉是把“当前步相互耦合的未知量”换成“上一时刻已知状态注入当前电路”，从而允许各子电路并行；代价是显式积分的稳定域受限，因此 500 ns 不能被当作对所有参数都自动稳定。[pdf:E03]（PDF 物理页 3，Eqs. (1)-(6) 与 Section II-B-4）

**器件瞬态层。** gate 方程

\[
C_{ge}\frac{dv_{ge}}{dt}
=C_{cg}\frac{d(v_{ce}-v_{ge})}{dt}
+\frac{V_g-v_{ge}}{R_g}
\]

把 gate resistance、电容充放电与 collector-gate 耦合联系起来。作者把 \(C_{cg}\) 分成 small/large 两段，使 Miller plateau 前后可分别得到 stage duration 与 \(dv_{ce}/dt\)；turn-on 的电流上升还叠加 diode reverse-recovery 峰值 \(I_{rr}\)。[pdf:E04]（PDF 物理页 4，Eq. (7) 及 Eqs. (8)-(14)）

关断末段的关键不是让 \(i_c\) 突然归零，而是保留 excess carriers 造成的 tail：

\[
i_c=i_0 e^{-t/\tau_{\mathrm{tail}}}.
\]

这项指数尾流与前一阶段的线性电流下降共同决定 turn-off loss。作者还在附录用 diode reverse-recovery 等效模型离线求峰值时刻 \(t_s\) 与 \(I_{rr}\)，再将不同 \(di_d/dt\) 和负载电流组合制成可查参数。[pdf:E05]（PDF 物理页 5，Eqs. (15)-(20)）[pdf:E09]（PDF 物理页 9，Eq. (24) 与 Appendix A）

**热层。** 四项 Foster 网络的 transient thermal impedance 为

\[
Z_{\mathrm{th}}(t)=\sum_{i=1}^{4}R_i\left(1-e^{-t/\tau_i}\right),
\qquad \tau_i=R_iC_i.
\]

Backward Euler 离散后，每个 RC 支路保存一个热状态，结温等于 case temperature 加上四个支路对当前损耗与历史热状态的贡献。物理上，快支路描述芯片附近快速升温，慢支路描述封装与散热路径的长期积热；论文用 datasheet 曲线拟合这些时间常数。[pdf:E05]（PDF 物理页 5，Fig. 8、Fig. 9 与 Eqs. (21)-(22)）

**电热反馈。** 温度敏感特性 \(X\) 在 \(T_{\min}\) 与 \(T_{\max}\) 之间线性插值：

\[
X(T_j)=\frac{X(T_{\max})-X(T_{\min})}{T_{\max}-T_{\min}}
\,\left(T_j-T_{\min}\right)+X(T_{\min}).
\]

这一式把结温送回静态压降和 transfer characteristics。它计算简单、适合 FPGA，但隐含“两个温度点之间近似线性”的建模假设。[pdf:E06]（PDF 物理页 6，Eq. (23)）

模型以 CM100DY-12H 为器件来源。作者报告的部分关键参数包括 \(C_{ge}=5\) nF、\(C_{cg(s)}=0.5\) nF、\(C_{cg(l)}=10\) nF、\(\tau_{\mathrm{tail}}=100\) ns、\(\tau_{rr}=50\) ns；完整 IGBT、diode、导热脂和散热器热参数列于 Appendix B。[pdf:E10]（PDF 物理页 10，Appendix B）

## § 7 — 实验设计与结论

**问题 1：system-level 网络解是否准确？** 作者在 \(V_{\mathrm{in}}=72\) V、\(R_L=10\,\Omega\)、四个电感各 \(400\,\mu\mathrm{H}\)、两个电容各 \(200\,\mu\mathrm{F}\)、\(f_s=10\) kHz 的开环工况下，把 FPGA 模型与 Simulink SimPowerSystem（SPS）比较。六个状态量的平均相对误差为 0.019%-0.118%，最大值小于 0.12%。这支持了该工况下 500 ns 网络解的精度，但不能证明所有参数和 DCM 边界都稳定。[pdf:E07]（PDF 物理页 7，Fig. 13）[pdf:E08]（PDF 物理页 8，Table III）

**问题 2：简化动态模型是否保留关键 switching transient？** 作者把 FPGA 的 turn-on/turn-off 波形与使用完整 behavioral circuit 的 Saber 离线模型比较。Table IV 报告：turn-on delay 为 143 ns 对 163 ns、rise time 为 92 ns 对 82 ns、turn-off delay 为 1441 ns 对 1430 ns、fall time 为 419 ns 对 391 ns；reverse-recovery peak 为 18.3 A 对 20.1 A，最大 turn-on loss 为 23.5 kW 对 24.1 kW，最大 turn-off loss 为 18.0 kW 对 17.7 kW。作者也明确承认，由于分段线性和指数近似，波形仍存在差异。[pdf:E08]（PDF 物理页 8，Fig. 14 与 Table IV）

**问题 3：热模型是否跟随 switching frequency 的损耗变化？** 在 0.5 s 仿真中，作者比较 5、10、20 kHz 三种频率下 FPGA 与 Saber 的 IGBT junction temperature。两者给出一致的趋势：频率越高，switching loss 越大，结温越高。本卡只采用论文明确给出的趋势，不从 Fig. 15 曲线估读未报告的精确温度。[pdf:E08]（PDF 物理页 8，Fig. 15 与 Section IV-B）

**问题 4：模型能否接入实时闭环控制与故障场景？** 作者把 embedded PI controller 与 FIBC 模型都放入 NI-7975R FPGA，在 PXIe 台架上通过 NI 5741 输出模拟信号到示波器。四组实验分别是电感电流 15-30 A 阶跃、输出电压 150-300 V 阶跃、负载 10-20 \(\Omega\) 扰动，以及在 \(300\) V/\(10\,\Omega\) 下令第 1、3 相 IGBT 开路；该组 FIBC 参数为 \(V_{\mathrm{in}}=72\) V、\(L=800\,\mu\mathrm{H}\)、\(C=1\) mF、\(f_s=10\) kHz。[pdf:E08]（PDF 物理页 8，Fig. 16 与 Section V）

故障实验中，论文报告第 2、4 相 IGBT 电流应力加倍，结温约在故障后 5.5 s 到达新的稳态且超过 200 °C，高于器件最大工作范围 150 °C；作者据此认为应降低额定输出并优化 gate drive 与 cooling strategy。[pdf:E09]（PDF 物理页 9，Fig. 17 与 Section V）

**不得外推的范围：** 这些结果验证的是指定 CM100DY-12H 参数、指定 FIBC 和所列工况，并以 SPS/Saber 为主要数值参考。示波器展示的是实时模型的模拟输出，不是实物功率级的 \(v_{ce}\)、\(i_c\) 或实测结温；论文没有报告与 double-pulse hardware、热电偶/红外测温或 calorimetry 的直接对照。[pdf:E08]（PDF 物理页 8，Figs. 14-16）这意味着实验支持“模型实时可执行且与离线参考一致”，尚不足以单独证明“对真实器件在广泛工况下同样准确”。

## § 8 — Take-aways

**5 句话：**

1. 论文把 FIBC 的 500 ns 网络求解与 IGBT 的 5 ns switching transient 生成解耦，用多时间尺度换取实时性。[pdf:E01]（PDF 物理页 1，Abstract）
2. 网络层采用显式离散与电路分区，器件层采用五阶段 behavioral model，热层采用 datasheet 拟合的四项 Foster 网络。[pdf:E03]（PDF 物理页 3）[pdf:E04]（PDF 物理页 4）[pdf:E05]（PDF 物理页 5）
3. FPGA 实现通过 fixed-point、LUT、pipeline 和 per-IGBT 并行动态模型，把相邻瞬态输出压到 5 ns。[pdf:E06]（PDF 物理页 6）[pdf:E07]（PDF 物理页 7）
4. 在论文指定工况中，system-level 六状态平均相对误差最大为 0.118%，switching 与 thermal waveforms 与离线参考总体一致，但局部瞬态差异仍然存在。[pdf:E08]（PDF 物理页 8，Tables III-IV 与 Figs. 14-15）
5. 实时故障演示说明热状态能改变控制与保护判断，但这仍是 model-versus-model 和模型输出验证，不是实物器件级精度的最终闭环。[pdf:E09]（PDF 物理页 9，Fig. 17）

**3 句话：** 这篇论文的贡献重点是计算结构：慢网络决定工况，快 behavioral model 重建开关，热网络积累损耗并反馈温度。FPGA 的并行与流水线让该结构同时满足 500 ns 网络步长和 5 ns 瞬态分辨率。[pdf:E07]（PDF 物理页 7，Table I 与 Fig. 12）其证据强项是完整的网络、器件、热和闭环故障演示，弱项是主要以 SPS/Saber 而非实物开关和实测结温作为准确性参考。[pdf:E08]（PDF 物理页 8）[pdf:E09]（PDF 物理页 9）

**1 句话：** 论文证明了一条工程上可行的实时路线：用分层、事件驱动的近似模型保留控制安全真正关心的开关损耗与结温，但其真实器件外推能力仍需硬件测量验证。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**由静态网络状态驱动的简化五阶段 behavioral model，在控制器可能到达的工作区间内，能足够准确地给出每次 switching energy；因此累计热状态也可信。**

这项假设一旦失效，错误会沿电热链放大。某个工况下的 \(I_{rr}\)、Miller plateau、\(C_{cg}\)、tail current 或温度依赖若偏差较大，\(v_{ce}i_c\) 的重叠面积就会错；误差再逐次注入 Foster 网络，最终让 protection threshold、derating 和 cooling decision 建立在错误的 \(T_j\) 上。论文自己的 Fig. 14 与 Table IV 已显示简化波形和 Saber 存在可见差异，例如 rise/fall time 与 reverse-recovery peak 并非完全一致。[pdf:E08]（PDF 物理页 8，Fig. 14 与 Table IV）

论文提供的支持包括：指定工况下与 Saber 的 transient 对比、三种 switching frequency 下 0.5 s 热趋势对比，以及闭环故障场景中的热响应。[pdf:E08]（PDF 物理页 8，Figs. 14-15）[pdf:E09]（PDF 物理页 9，Fig. 17）仍缺少的关键证据是：跨 \(V_{dc}\)、load current、gate resistance、junction temperature 与器件批次的实物 double-pulse switching energy，以及独立的结温测量。线性温度插值只用 datasheet 的两个温度边界，论文也未给出超界策略。[pdf:E06]（PDF 物理页 6，Eq. (23)）因此，把“与 Saber 一致”直接等同于“对真实 IGBT 全工作区准确”仍然是**未经该论文闭合的不确定性**。

## § 10 — 最小复现实验

一周内最有价值的复现不是先重建四相闭环台架，而是复现“一个 IGBT 事件是否能以固定计算预算给出可信 switching loss 和短时 thermal response”。

1. **数据与参数。** 使用 Appendix B 的 CM100DY-12H 参数，包括 \(C_{ge}\)、两段 \(C_{cg}\)、\(\tau_{\mathrm{tail}}\)、\(\tau_{rr}\) 和四项 IGBT thermal RC；以论文 Table IV 的 Saber 结果作为第一阶段数字基准。[pdf:E10]（PDF 物理页 10，Appendix B）[pdf:E08]（PDF 物理页 8，Table IV）
2. **实现。** 在可综合 fixed-point 代码或 HLS 中实现 Eqs. (7)-(23)：turn-on/turn-off 五阶段、reverse-recovery lookup、\(P_L=v_{ce}i_c\)、四项 Foster 离散与温度插值。用 200 MHz 等价时钟驱动，记录 initiation interval 与 latency；不必先实现完整 FIBC network。
3. **测量。** 对与论文 Fig. 14 相同的器件参数设置，比较 \(t_d(on)\)、\(t_r\)、\(t_d(off)\)、\(t_f\)、\(I_{rr}\)、\(P^{on}_{L(max)}\)、\(P^{off}_{L(max)}\)，并在 5、10、20 kHz 重复事件序列下比较 0.5 s 结温趋势。不得从图上反推更细的精确温度，只检验频率排序和自身高精度浮点参考。[pdf:E08]（PDF 物理页 8，Table IV 与 Fig. 15）
4. **实时性判据。** 支持 claim 的最低条件是 200 MHz 下动态模型达到 1-cycle initiation interval，输出间隔 5 ns，且报告的七项瞬态量至少不劣于论文 FPGA 与 Saber 之间的偏差量级；论文实现的动态模型 latency 为 19 cycles，thermal model initiation interval 为 5 cycles、latency 为 4 cycles。[pdf:E07]（PDF 物理页 7，Table I）
5. **反驳判据。** 如果 fixed-point/LUT 实现为达到时序而显著扩大 switching-energy 误差，或热状态随事件累计后与浮点参考的偏差持续漂移，就足以反驳“该近似在给定实时预算下仍保留电热可信度”的核心工程 claim。

该复现不能证明实物准确性，但能在一周内把论文最关键的“模型误差 - 数字实现 - 实时吞吐量”三者关系暴露出来。

## § 11 — 最强反例设计

最强反例应攻击 loss-to-temperature 因果链，而不是只找一个电压波形的小差异。设计一个真实 CM100DY-12H double-pulse test matrix：跨低/高直流电压、低/额定电流、\(R_g=30/50\,\Omega\)、冷态/热态，并加入 diode reverse-recovery 明显的工况；同步测量 \(v_{ce}\)、\(i_c\)，积分得到每次 \(E_{on}\)、\(E_{off}\)，再用独立温度敏感电参数或校准热测量取得短时 \(T_j\)。论文模型的器件参数与这两个 \(R_g\) 设置来自 Appendix B。[pdf:E10]（PDF 物理页 10，Appendix B）

真正有杀伤力的结果是：模型在论文展示点附近仍与 Saber 一致，但在高温、高 \(di/dt\) 或 reverse-recovery 强烈的组合下系统性低估 switching energy，随后在重复脉冲中低估结温并错过 150 °C 保护阈值。这样可以排除“只是曲线形状不同但能量仍对”的解释，并直接推翻该模型作为热保护证据的充分性。论文现有证据只有单组 transient 表、三种频率的 model-versus-model 热趋势和模型闭环故障输出，没有这类实物跨工况矩阵。[pdf:E08]（PDF 物理页 8，Table IV 与 Figs. 15-16）[pdf:E09]（PDF 物理页 9，Fig. 17）

如果实测 switching energy 在全矩阵内都保持小误差，而且结温预测在 fault transient 中也能覆盖实测，那么这个反例反而会显著加强论文最薄弱的一环。

## § 12 — Follow-up Research Idea

**候选方向，不声称 novelty：** 把“给出一个实时结温点估计”改成“给出带可校准不确定性边界的实时热安全证据”。目标不是继续增加 IGBT 等效电路复杂度，而是在 HIL 中同时输出 \(\hat T_j\) 与可信区间，并在当前 \(V_{dc}\)、电流、\(R_g\)、温度或 fault 状态离开已校准区域时明确降低模型可信度。

**(a) 未满足需求。** 论文已经说明结温会影响 derating、gate drive 与 cooling decision，并在开路故障中给出超过 200 °C 的模型结果。[pdf:E09]（PDF 物理页 9，Fig. 17 与 Section V）但一个没有误差边界的点估计无法告诉控制器：超过阈值是真实热风险，还是 behavioral/LUT/Foster 参数误差。

**(b) 研究价值。** 电力电子 HIL 的高影响结果通常同时要求实时性、器件物理可信度、硬件资源可实现性和真实实验验证。把安全决策从“相信单一模型”改为“只有在误差界内才允许通过”，会直接改变 HIL 的验收对象，而不是只多加一个模块。

**(c) 可借鉴工具。** 可借鉴 interval observer、set-membership identification 与在线 residual monitoring：离线用少量 double-pulse 与 thermal transient 校准参数集合；在线让 FPGA 传播上、下界或低阶 sensitivity bound，并用测得的 controller-side 电压、电流残差更新可信区间。

**(d) 首个证伪实验。** 用训练矩阵之外的高温、高 \(di/dt\) 与开路故障序列测试。如果真实 switching energy 或 \(T_j\) 落在预测区间之外，或者区间宽到无法支持 150 °C 阈值决策，候选方法立即失败。

**(e) 与本文的实质区别。** 本文的目标是让一个确定性的 behavioral electro-thermal model 在 500 ns/5 ns 多速率预算内运行，并以 Saber/SPS 一致性支撑准确性。[pdf:E07]（PDF 物理页 7，Table I）候选方向把问题重新定义为“在实时预算内证明何时可以信、何时不能信”，并要求用实物测量闭合模型外推风险。由于本卡没有对 uncertainty-aware electro-thermal HIL 做充分相关工作检索，这里只把它作为可证伪的研究假设，不宣称新颖性。
