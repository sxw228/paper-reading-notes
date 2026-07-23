# Real-Time Hardware-in-the-Loop Emulation of High-Speed Rail Power System With SiC-Based Energy Conversion

- 作者：Tian Liang；Qin Liu；Venkata R. Dinavahi
- 出处：IEEE Access，Vol. 8
- 年份：2020
- DOI：10.1109/ACCESS.2020.3006904
- Zotero key：9C62Z4RV

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是一般意义上的“把高铁系统跑进实时仿真器”，而是把两个相差三个数量级的时间尺度放进同一套 hardware-in-the-loop（HIL）执行链：一边是整条交流牵引网络的微秒级电磁暂态，另一边是 SiC 功率器件开通、关断、反向恢复和寄生振荡的纳秒级暂态。作者指出，商用 HIL 常用的 system-level 开关模型会忽略器件开关过程；但若直接采用 physics-based 或有限元模型，又会因为非线性迭代、器件几何和材料数据需求以及计算量而难以满足实时 deadline。论文因此把“器件细节是否足够可信”和“计算是否能在物理时间到来前完成”视为同一个问题。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 2，Introduction）

这个问题的工程价值在于：SiC 的低电阻、低电容、高开关频率和高温能力虽能降低损耗，却也会提高寄生振荡频率并削弱阻尼。若 HIL 只保留理想开关状态，控制器或保护逻辑就看不到这些快速过冲、振铃、尾电流和温升后果；若模型太慢，所谓实时闭环又不成立。论文的目标是在非破坏性环境中，既让控制器面对器件级瞬态，又让完整北京—上海高铁牵引系统持续实时推进。[pdf:E02]（PDF 物理页 2，Introduction）[pdf:E03]（PDF 物理页 3，Section II-A 与 Fig. 1）

## § 2 — 前人工作与不足

论文把已有器件模型分为三类。Behavioral model 直接拟合外部电气行为，计算最省；physics-based model 求解更细的非线性器件方程，通常需要 Newton 迭代；numerical model 通过有限元等方法提供空间细节，但依赖制造商通常不公开的几何与材料参数，计算也最重。作者的判断是：针对实时 device-level HIL，后两类模型的物理细节虽然更丰富，却与 deadline 和数据可得性冲突，因此 behavioral model 是当前工程约束下最可行的入口。[pdf:E02]（PDF 物理页 2，Introduction）

已有 thermal model 包括 lumped network、transfer function、finite difference、finite element 和 boundary element 等路线。论文选择由 datasheet 参数化的 Foster thermal network，并利用热过程显著慢于电气开关过程这一事实，让热模型只在 system-level 步长上与电气模型交换信息。[pdf:E02]（PDF 物理页 2，Introduction）论文还引用了此前用于系统辨识、迟滞、电力电子和电机的 Wiener-Hammerstein 结构；本文并未证明该结构在理论上优于所有 SiC 模型，而是利用其“前动态块—静态块—后动态块”的分解，把载流子充放电、温度相关静态导通和开关振荡分别映射到便于实时实现的局部计算。[pdf:E02]（PDF 物理页 2，Introduction）

因此，本文真正补的工程缺口是：既有 system-level HIL 看不到器件瞬态，细致物理模型又无法在完整牵引系统中实时运行；作者尝试以 datasheet 驱动的降阶模型，换取“可解释到关键器件现象、又能守住 deadline”的中间点。这里是对论文问题设置的重述，不是对其 novelty 的独立判定；本卡未做充分的外部相关工作检索。

## § 3 — 重建作者的思考路径

可以从三个先验事实重建这条路线。第一，SiC 模块的低寄生电阻与电容会让开关振铃更快、阻尼更差，所以仅用理想开关无法回答过冲、损耗和保护问题。[pdf:E03]（PDF 物理页 3，Section II-A）第二，器件静态伏安特性、开关延时、反向恢复电荷、热阻抗和开关能量都能从 datasheet 取得，而完整器件几何和材料参数通常取不到。[pdf:E02]（PDF 物理页 2，Introduction）第三，实时计算资源具有异构性：ARM 适合高顺序性的局部状态推进，FPGA 适合大规模并行的网络求解；如果把不同时间尺度和计算形态分开放置，未必需要让完整系统都以纳秒步长运行。[pdf:E06]（PDF 物理页 6，Section IV-A/B）

由此，一个合理的推导路径是：先把开关过程拆成载流子充放电、温度相关静态导通、动态振荡和热过程；再用一阶环节、线性/多项式片段、等效 RLC 和 Foster network 逐段替代昂贵的器件方程；最后只在开关瞬态窗口启用纳秒级计算，其余牵引网络仍以微秒级 system-level 模型推进。[pdf:E03]（PDF 物理页 3，Table 1 与 Fig. 1）[pdf:E04]（PDF 物理页 4，Figs. 2–4）[pdf:E05]（PDF 物理页 5，Fig. 5 与 Eqs. (12)–(17)）

最后一步是把“模型简化”变成“可验证的实时调度”：器件波形对 SaberRD，系统波形对 PSCAD/EMTDC；器件计算时间必须小于对应物理开关延时，板间通信和系统步长也必须有明确上界。[pdf:E07]（PDF 物理页 7，Section V）[pdf:E09]（PDF 物理页 9，Fig. 13 与结果正文）

## § 4 — 核心 Intuition

核心 intuition 是：不要在每个 10 ns 时刻重算完整半导体物理，而是把 SiC IGBT 的开关行为拆成几个物理含义明确、datasheet 可参数化的低阶片段。载流子充放电决定“何时开始切换”，温度相关 Norton 等效决定“静态导通到哪里”，一阶响应与预计算 RLC 振荡决定“切换过程中怎样过冲和衰减”；再利用系统其他部分较慢的事实，把纳秒计算限制在局部器件和短暂时间窗内。[pdf:E04]（PDF 物理页 4，Figs. 2–4）[pdf:E05]（PDF 物理页 5，Fig. 5）

换句话说，论文用受控的物理降阶换实时性，而不是把器件瞬态整体删除。它能成立的关键不只是 FPGA 并行度，还包括对开关事件的分段调度和对振荡历史量的预计算复用。[pdf:E07]（PDF 物理页 7，Section V）

## § 5 — 具体方法与完整 Pipeline

以一列车在北京—上海交流牵引网中运行、MMC 子模块的 S2 发生开通为例，完整 pipeline 如下。

1. **建立器件参数入口。** 从 hybrid SiC IGBT module 的 datasheet 取得开通/关断延时、静态 \(I_C\!-\!V_{CE}\) 与 \(I_F\!-\!V_F\) 曲线、反向恢复电荷 \(Q_{rr}\)、栅极电阻、寄生电感/电容、开关能量和 thermal impedance。论文的 Table 1 明确把这些数据分别送入 dynamic carrier charge、static electrical characteristic、dynamic electrical characteristic、power loss/thermal calculation 四部分。[pdf:E03]（PDF 物理页 3，Table 1）

2. **载流子充放电前动态块。** 门极信号到来后，\(C_{GE}\) 与 \(C_{GC}\) 的非线性充电被等效为一阶 RC。等效电容由 datasheet delay \(T_d\) 和等效栅阻 \(R_{Geq}\) 给出，直到门极达到阈值才触发后续静态与动态块；因此这一步的物理作用是生成器件真正导通/关断前的等待窗口，而不是直接改变主电路电流。[pdf:E03]（PDF 物理页 3，Eq. (5) 与 Section II-B）[pdf:E04]（PDF 物理页 4，Fig. 2）

3. **温度相关静态块。** IGBT 与 diode 均写成 conductance 与 voltage-controlled current source（VCCS）并联的 Norton 形式。导通电导 \(g_{ON}\) 和偏置电流 \(i_{ON}=v_{ON}g_{ON}\) 由 datasheet 的低温、高温曲线随结温线性插值；静态状态下，SiC diode 的电容效应被忽略。Foster thermal network 将 IGBT、diode、module case、thermal paste、heatsink 与 ambient 串接，器件损耗成为结温输入。[pdf:E04]（PDF 物理页 4，Figs. 3–4、Table 2、Eqs. (6)–(8)）

4. **开通动态后块。** 开通 Stage 1 用一阶近似提升 conductance；Stage 2 用三角形近似反向恢复峰值；Stage 3 用寄生 \(RLC\) 回路生成衰减振荡。Fig. 1 给出 MMC 子模块在正、负电流方向下的两种内部振荡回路；低电容提高固有频率，低电阻降低阻尼。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Eqs. (1)–(4)）[pdf:E05]（PDF 物理页 5，Fig. 5(a)）

5. **关断动态后块。** 关断 Stage 1 把电流线性下降与一阶近似并行推进，在两条近似曲线交点后进入 Stage 2；Stage 2 将一阶尾电流与 RLC 振荡叠加。静态期则关闭这些动态支路，退回 Norton 等效。[pdf:E04]（PDF 物理页 4，Section II-D）[pdf:E05]（PDF 物理页 5，Fig. 5(b)(c)）

6. **电压与损耗重构。** 作者由 datasheet 的 switching power loss 曲线拟合线性/多项式、一阶指数和振荡片段，再以 \(V=P/I\) 重构开通、关断 \(V_{CE}\)。用于 thermal calculation 的不是归一化拟合损耗，而是 datasheet 标准损耗，以避免拟合误差继续进入热模型。[pdf:E05]（PDF 物理页 5，Eqs. (16)–(17)）[pdf:E06]（PDF 物理页 6，Fig. 6）[pdf:E07]（PDF 物理页 7，结果讨论）

7. **嵌入完整牵引系统。** 研究对象是 1318 km 北京—上海 HSR 网络，包含 27 个 power station 和 26 个 section post；线路用 distributed travelling-wave transmission-line model。列车侧把接触网 27.5 kV 经单相变压器降至 3 kV，整流后连接五电平 MMC induction-machine drive。[pdf:E06]（PDF 物理页 6，Figs. 7–8 与 Section III）

8. **异构硬件分解。** 一块 ZCU102 MPSoC 负责一段含 power station、AT substation、section post 的 device-level SiC MMC train；两块 VCU118 FPGA 负责 system-level AC traction network。ZCU102 与 VCU118 通过 QSFP/Aurora 通信，论文报告 board-to-board latency 为 650 ns。[pdf:E06]（PDF 物理页 6，Section IV-A/B）

9. **多速率实时调度。** 静态与一阶片段按 100 ns 计算，混合振荡按 10 ns 输出；RLC 单节点的预存历史计算可在每点 6 ns 内完成。system-level 网络以 10 μs 推进。载流子充电窗口不激活主器件，作者把这段物理等待时间用于提前完成后续瞬态计算，即所谓“borrow time”。[pdf:E07]（PDF 物理页 7，Section V）[pdf:E11]（PDF 物理页 11，Table 6）

10. **输出与比较。** device-level 开通/关断电流、重构电压和结温与 SaberRD 离线结果比较；system-level 线路电压电流、整流器电压、MMC 电容电压、电机电压与 FFT 则与 PSCAD/EMTDC 比较。论文在 oscilloscope 上输出硬件结果，形成 HIL 可观察接口。[pdf:E08]（PDF 物理页 8，Figs. 10–12）[pdf:E09]（PDF 物理页 9，Fig. 13）[pdf:E10]（PDF 物理页 10，Fig. 14）

## § 6 — 核心数学推导

### 6.1 用寄生参数解释 SiC 振荡

在欠阻尼近似下，MMC 子模块寄生回路的固有角频率写成

\[
\omega \approx \frac{1}{\sqrt{L_s' C_{oes}(V_R)}}, \qquad
L_s'=L_{C1}+L_{E1}+L_S+L_{C2}.
\]

这里 \(C_{oes}(V_R)\) 是反向电压下的输出电容，\(L_{C1},L_{E1},L_{C2}\) 是模块寄生电感，\(L_S\) 是外部 stray inductance。物理上，SiC 的小电容让 \(\omega\) 上升；等效电阻约 \(R_{eq}\approx1.5\,\Omega\) 则决定振铃衰减速度。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(4)）

### 6.2 从 delay 得到载流子充电时间尺度

作者把门极充放电压缩为一阶 RC，并由 datasheet delay 反推

\[
C_{eq}=\frac{T_d}{2.2R_{Geq}}.
\]

\(T_d\) 是开通或关断 delay，\(R_{Geq}\) 是内、外栅阻的等效值。这个式子的工程意义是：不追踪每个非线性结电容的内部电荷分布，只保留门极达到阈值所需的主时间常数。[pdf:E03]（PDF 物理页 3，Eq. (5)）

### 6.3 温度相关 Norton 静态模型

对 conductance 和 threshold-like voltage 分别在 datasheet 低、高结温之间插值：

\[
g_{ON}(T_{vj})=
\frac{T_{vj}-T_{low}}{T_{low}-T_{high}}
\left(g_{ON}^{T_{low}}-g_{ON}^{T_{high}}\right)+g_{ON}^{T_{low}},
\]

\[
v_{ON}(T_{vj})=
\frac{T_{vj}-T_{low}}{T_{low}-T_{high}}
\left(v_{ON}^{T_{low}}-v_{ON}^{T_{high}}\right)+v_{ON}^{T_{low}},
\qquad
i_{ON}(T_{vj})=v_{ON}(T_{vj})g_{ON}(T_{vj}).
\]

这里 \(T_{vj}\) 是 junction temperature，\(T_{low},T_{high}\) 是 datasheet 两个实验温度。它把温度变化转成每一实时步都容易更新的 conductance 与 VCCS，而不是再次求解半导体方程。[pdf:E04]（PDF 物理页 4，Eqs. (6)–(8)）

### 6.4 用 RLC 解析形状替代逐步求解

寄生振荡满足 \(u_C+u_R+u_L=0\)，其二阶特征方程为

\[
LCp^2+RCp+1=0,\qquad
p=-\frac{R}{2L}\pm\sqrt{\left(\frac{R}{2L}\right)^2-\frac{1}{LC}}.
\]

在欠阻尼条件下，电流写成

\[
i(t)=I_0 e^{-\delta t}\cos(\omega t),\quad
I_0=I_{rr}=4Q_{rr}f_{osc},\quad
\delta=\frac{R}{2L},
\]

\[
\omega=\sqrt{\frac{1}{LC}-\left(\frac{R}{2L}\right)^2}
\approx\sqrt{\frac{1}{LC}}
\quad \text{当 }R\ll2\sqrt{L/C}.
\]

\(Q_{rr}\) 是 reverse-recovery charge，\(f_{osc}\) 是 oscillation frequency。这个解析形状使模型可以预先保存一段历史电流，而不必在开关瞬态内重复求解完整网络。[pdf:E04]（PDF 物理页 4，Eqs. (9)–(11)）[pdf:E05]（PDF 物理页 5，Eqs. (12)–(13)）

### 6.5 一阶环节的离散化

作者从 \(H(s)=1/(\tau s+1)\) 出发，用 bilinear transformation

\[
s=\frac{2}{\Delta t}\frac{1-z^{-1}}{1+z^{-1}}
\]

得到可逐步执行的一阶差分关系。这里 \(\Delta t\) 是 simulation timestep，\(\tau\) 由 datasheet rise/fall time 定义反推。其作用是以一个状态量逼近 conductance、VCCS 或尾电流的主导 delay，计算成本固定且适合实时实现。[pdf:E05]（PDF 物理页 5，Eqs. (14)–(15)）

### 6.6 电压与热损耗

开通、关断损耗被分段写成线性或二次多项式、一阶指数与振荡项的积分；\(t_1\) 至 \(t_6\) 划分不同动态区间，\(A_i\) 至 \(G_i\) 与 \(\tau_i\) 是拟合参数。随后用 \(V=P/I\) 重构 \(V_{CE}\)。这不是从半导体物理第一性原理推出的唯一模型，而是带有 datasheet 拟合边界的工程近似；它的可信度必须由未参与拟合的工作点验证。[pdf:E05]（PDF 物理页 5，Eqs. (16)–(17)）[pdf:E06]（PDF 物理页 6，Fig. 6）

## § 7 — 实验设计与结论

### 问题 1：降阶器件模型能否复现开关瞬态？

**实验。** 作者在 datasheet 标准条件下，用 SaberRD 离线波形对比实时模型的四组电流工况，观察 turn-on current、turn-off current、reconstructed turn-on voltage、reconstructed turn-off voltage；又比较 normalized switching loss 与 datasheet switching energy。[pdf:E08]（PDF 物理页 8，Figs. 10–11）

**答案。** 论文报告平均误差分别为 \(i_{on}=0.17\%\)、\(v_{on}=4.32\%\)、\(i_{off}=1.02\%\)、\(v_{off}=3.72\%\)，因此其“device-level average error 小于 4.32%”在所测 datasheet 条件下成立。[pdf:E11]（PDF 物理页 11，Table 5）不能外推为所有结温、栅阻、寄生参数和负载电流下都小于该误差。

### 问题 2：器件计算是否真正赶得上物理开关过程？

**实验。** 作者将静态/一阶段和 RLC 振荡段拆开计时。在 \(I_C=168\) A 时，计算量为一次 100 ns 一阶计算加 62 个每点 6 ns 的振荡点，总计 \(472\) ns，小于 500 ns turn-on delay；在 \(I_C=1206\) A 时，总计 \(2\times100+43\times6=458\) ns。[pdf:E07]（PDF 物理页 7，Section V）

**答案。** Table 6 汇总的实现步长是 device-level first-order 100 ns、device-level mixed oscillation 10 ns、system-level 10 μs。论文据此宣称实时可行；严格说，直接给出的 deadline 论证集中在少数电流工况与特定 ARM/FPGA 配置上。[pdf:E11]（PDF 物理页 11，Table 6）

### 问题 3：电热耦合是否给出合理趋势？

**实验。** 同一 heatsink、同一 gate signal 下，对比 Si module FD1000R171E4 与 SiC module CMH1200DC-34S 的 10 s 结温；同时将 device-level realtime waveform 与 SaberRD 的结温、开通和关断瞬态叠放。[pdf:E08]（PDF 物理页 8，Fig. 12）[pdf:E09]（PDF 物理页 9，Fig. 13）

**答案。** 论文报告 Si 器件在 40–43 °C 之间波动，温度变化幅度约为 SiC 的三倍；SiC 器件稳定运行时均未超过 41 °C。[pdf:E07]（PDF 物理页 7，结果讨论）[pdf:E08]（PDF 物理页 8，Fig. 12）这验证的是指定损耗模型、散热网络和 10 s 工况下的模型结果，不是实物功率模块 calorimetry。

### 问题 4：完整牵引系统的微秒级结果是否与离线 EMT 对齐？

**实验。** 完整 HSR 网络的线路电压电流、整流器 AC/DC 电压、MMC capacitor-forming voltage、电机电压、上下桥臂电容电压和 FFT 与 PSCAD/EMTDC 离线结果对比。Table 3 还比较列车处于不同位置时的线路电压和相对误差。[pdf:E09]（PDF 物理页 9，Table 3）[pdf:E10]（PDF 物理页 10，Fig. 14）

**答案。** 论文报告 system-level average error 为 0.217%；在所示工况中，上、下桥臂电容电压分别约为 727–742 V 和 726–741 V，变化率为 2.022% 与 2.024%；4000 Hz 与 8000 Hz 谐波与 2000 Hz carrier 有关且相对 50 Hz 主分量较小。[pdf:E09]（PDF 物理页 9，结果正文）这些结果支持指定列车数量、位置和控制设置下的系统级一致性，不能证明故障、再生制动、通信抖动或多列车高密度运行下仍有同样误差。

### 问题 5：硬件是否还有资源余量？

**实验。** 作者统计 ZCU102 与两块 VCU118 的 BRAM、DSP、FF、LUT 占用。[pdf:E11]（PDF 物理页 11，Table 4）

**答案。** LUT 是最紧资源：ZCU102 为 90.92%，VCU118-1 为 67.47%，VCU118-2 为 88.55%。因此当前实例能装下，但 device-level 板与第二块系统级板的扩展余量有限；这对增加更多列车、更细模型或在线参数更新形成直接约束。[pdf:E11]（PDF 物理页 11，Table 4）

## § 8 — Take-aways

### 5 句话

1. 论文证明了一个工程上有价值的折中：用 datasheet 驱动的 Wiener-Hammerstein 降阶模型，在不删除 SiC 开关振荡的前提下，把 device-level HIL 做到 10 ns 输出尺度。[pdf:E01]（PDF 物理页 1，Abstract）
2. 真正的加速来自“按物理阶段拆计算”：100 ns 一阶片段、10 ns 混合振荡、10 μs 系统网络，而不是让整条高铁网络统一跑 10 ns。[pdf:E11]（PDF 物理页 11，Table 6）
3. 器件级验证对 SaberRD 的最大平均误差为 4.32%，系统级对 PSCAD/EMTDC 的报告平均误差为 0.217%，但都只覆盖论文给定工况。[pdf:E09]（PDF 物理页 9，结果正文）[pdf:E11]（PDF 物理页 11，Table 5）
4. 物理意义上，低 \(R\)、低 \(C\) 同时带来 SiC 的效率优势与更高频、更难阻尼的振铃，等效 RLC 是模型保留这部分风险的核心。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Eqs. (1)–(4)）
5. 论文最重要的未闭合边界不是“能否运行”，而是固定 datasheet 参数与预存振荡历史在多温度、多电流、多寄生和控制扰动下是否仍同时满足精度与 deadline。

### 3 句话

作者把 SiC IGBT 拆成 carrier charge、温度相关 static characteristic、dynamic oscillation 与 thermal network，并把不同部分映射到 MPSoC-FPGA 的不同时间尺度。[pdf:E04]（PDF 物理页 4，Figs. 2–4）所示硬件在器件级和系统级均与商用离线软件取得接近结果，但验证范围受 datasheet 标准条件和少数牵引工况限制。[pdf:E08]（PDF 物理页 8，Figs. 10–12）下一步最值得验证的是模型参数和预计算策略跨工作区间的稳健性，而不是单纯增加更多 FPGA。

### 1 句话

这篇论文的核心贡献是把“看得到 SiC 开关细节”和“完整高铁系统仍能实时运行”通过物理分段、降阶建模与异构多速率调度连接起来。

## § 9 — 最脆弱的假设

最脆弱的假设是：在需要实时复用的工作区间内，collector current \(I_C\) 对 reverse-recovery charge \(Q_{rr}\) 的影响足够小，所以可以固定预存 RLC 历史电流，并借用 carrier-charge delay 提前完成后续振荡计算。作者直接把这条假设写成采用 fixed pre-restored historical current 的 prerequisite；在 \(168\) A 与 \(1206\) A 示例中，正是它让总计算时间分别压到 472 ns 与 458 ns。[pdf:E07]（PDF 物理页 7，Section V）

这条假设一旦失效，精度和实时性会同时受损。若 \(Q_{rr}\) 随 \(I_C\)、junction temperature、gate resistance、\(d i/dt\) 或寄生回路显著变化，固定的 \(I_0=4Q_{rr}f_{osc}\) 会直接给错振铃初值；若改成每次在线重算，又可能吃掉“borrowed”时间预算。[pdf:E05]（PDF 物理页 5，Eqs. (12)–(13)）论文用四组 datasheet 标准电流的波形对比和平均误差支持该近似，并承认固定 \(\alpha\) 会在低电流区引入更高误差，最终实现中把 \(\alpha\) 调整到交点百分比以改善拟合。[pdf:E07]（PDF 物理页 7，结果讨论）但它没有给出跨结温、栅阻、寄生参数与 reverse-recovery 条件的系统 envelope，也没有报告 deadline miss distribution。基于这些证据，我认为“固定历史在整个目标 operating envelope 内仍成立”仍是不确定的候选判断。

## § 10 — 最小复现实验

一周内不必复现 1318 km 牵引网；只复现一个 half-bridge MMC submodule 的单次开通/关断即可验证核心 claim。

1. 从 CMH1200DC-34S datasheet 建立论文的 carrier-charge RC、温度插值 Norton、RLC 振荡和 Foster thermal network；按 Table 7 使用 \(L_{E1}=L_{E2}=10\) nH、\(L_{C1}=L_{C2}=20\) nH、\(L_S=100\) nH、\(C_{oes}(V_R)=1.17\) nF、\(R_{eq}=1.5\,\Omega\)、\(Q_c=2.5\) μC、\(I_{rr}=100\) A。[pdf:E11]（PDF 物理页 11，Table 7）
2. 先在论文展示的四个 current rating 上重放 turn-on/turn-off，参考值使用 SaberRD 或可获得的 double-pulse measurement；不要从论文图中估读精确曲线值。
3. 同时实现两种版本：A 为论文的 fixed pre-restored RLC history；B 让 \(Q_{rr}\) 随电流和温度更新。每个版本记录 \(i_C\)、\(v_{CE}\)、switching energy、波形误差和 wall-clock latency。
4. 支持论文 claim 的最低结果是：A 在论文标准工况下复现其误差量级，尤其 \(v_{on}\) average error 不高于论文报告的 4.32%；并在 \(168\) A 与高电流工况下分别守住论文给出的 500 ns 左右开通等待窗口。[pdf:E07]（PDF 物理页 7，timing 计算）[pdf:E11]（PDF 物理页 11，Table 5）
5. 反驳该 claim 的结果是：即使在论文标准工况下，A 的关键波形或 switching energy 明显偏离参考，或计算在同一硬件时钟假设下越过物理 delay；若只有 B 能保持精度，则说明固定历史而非 Wiener-Hammerstein 分解本身是瓶颈。

这个实验把“模型能拟合”与“模型能按时完成”放在同一验收中，避免只比较波形却忽略实时 deadline。

## § 11 — 最强反例设计

最强反例不是再换一个牵引线路拓扑，而是构造一个让固定 \(Q_{rr}\) 与固定振荡模板同时失效的 double-pulse operating envelope。选择低、中、高 \(I_C\)，至少两个 junction temperature，改变 external gate resistance，并在合理范围内改变 stray inductance；每一点都用实测或高可信 device-level reference 得到 \(Q_{rr}\)、峰值、振铃频率、阻尼、switching energy 与 turn-on delay。论文自己的机理表明，\(I_0\) 由 \(Q_{rr}\) 决定，\(\omega\) 由 \(L\) 与 \(C\) 决定，\(\delta\) 由 \(R/L\) 决定，所以这个矩阵会同时攻击振铃初值、频率、衰减和可借用时间。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(4)）[pdf:E05]（PDF 物理页 5，Eqs. (12)–(13)）

攻击的判据应是联合失效：固定模板在某个未见工况下超过论文报告的 device-level error envelope，且为修正误差所需的在线更新使 10 ns mixed-oscillation 或物理开关 deadline 无法满足。[pdf:E11]（PDF 物理页 11，Tables 5–6）若这种工况存在，就能给出一个具体替代解释：论文的成功主要来自 datasheet 标准条件下的模板匹配和预计算，而不是该结构对 SiC 器件 operating envelope 的普适压缩。若所有工况仍守住误差与 deadline，反而会显著增强论文目前最缺少的外推证据。

## § 12 — Follow-up Research Idea

在电力电子实时仿真领域，高影响工作通常不仅要求更小 timestep，还要求模型误差有可解释边界、真实硬件 deadline 可验证、参数对器件和工况变化具有可迁移性，并能在 closed-loop 或 HIL 场景中展示系统价值。基于第 9 节，候选方向是：**面向 operating envelope 的 uncertainty-aware、deadline-certified SiC device emulator**。本卡未充分检索相关工作，因此只把它标为候选研究想法，不声称 novelty。

**(a) 未满足需求。** 当前固定 datasheet 模板在标准工况有效，但 HIL 真正危险的区域往往是高温、不同 gate resistance、寄生漂移、老化和故障边缘；这些条件恰好会同时改变 \(Q_{rr}\)、振铃和物理 delay。用户需要的不是单一 nominal waveform，而是“在当前条件下，这个 10 ns 结果是否仍可信且按时”的在线答案。

**(b) 研究价值。** 问题定义从“把 nominal device waveform 跑得更快”变为“对每个工作区间同时给出误差 certificate 与 deadline certificate”。这会把实时仿真的可信性从离线平均误差提升为可用于保护器测试的运行时保证，并直接回应当前 90.92%/88.55% LUT 占用下不能无限加复杂度的资源约束。[pdf:E11]（PDF 物理页 11，Table 4）

**(c) 可借鉴工具。** 可借鉴 robust model reduction、set-membership identification 与 runtime assurance：离线用少量 double-pulse 数据辨识 \(Q_{rr}\)、\(RLC\) 和一阶参数随 \(I_C,T_j,R_g\) 的可达集合；在线用 residual monitor 判断当前状态是否仍在已认证 envelope。区间内走快速预计算模板，越界时切换到局部参数更新或明确输出“结果未认证”，而不是静默给出 nominal 波形。

**(d) 第一个证伪实验。** 留出一组未参与辨识的高温、低电流、变栅阻与变 stray-inductance 组合，在同一 MPSoC 上运行。候选方法必须在用户事先设定的波形/能量误差阈值内、零 deadline miss，并且其 uncertainty bound 覆盖真实误差；任一条件失败就证伪“可认证 envelope”。

**(e) 与本文的实质区别。** 本文用固定 datasheet 拟合与预存历史证明 nominal case 可以实时运行；候选方向把参数变化、误差界和 deadline 共同作为模型状态与输出，并允许系统在超出认证范围时拒绝给出伪精确结果。它改变的是 HIL 模型的目标函数与可信性接口，不只是给现有 Wiener-Hammerstein pipeline 再加一个拟合模块。
