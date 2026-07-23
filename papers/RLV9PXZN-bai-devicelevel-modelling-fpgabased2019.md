# Device-level modelling and FPGA-based real-time simulation of the power electronic system in fuel cell electric vehicle

- 作者：Hao Bai；Chen Liu；Rui Ma；Damien Paire；Fei Gao
- 出处：IET Power Electronics，Vol. 12，Iss. 13，pp. 3479-3487
- 年份：2019
- DOI：10.1049/iet-pel.2019.0101
- Zotero key：RLV9PXZN
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是“能否在 FPGA 上跑一个整车模型”这一宽泛问题，而是一个时间尺度冲突：FCEV 的控制器需要看到燃料电池升压变换器、双向 DC-DC、牵引逆变器和 PMSM 共同作用下的整车动态；与此同时，器件的开关电压、电流、损耗和结温又发生在纳秒到微秒尺度。理想开关模型能支撑控制级 HIL，却看不到 IGBT/diode 的开关应力与损耗；完整非线性器件模型能看见暂态，却通常依赖迭代求解，难以满足硬实时截止时间。论文把目标明确为：在同一个 FPGA 实时平台中，同时保留系统级电气耦合与器件级开关暂态。[pdf:E01](_evidence/E01-p001-title-introduction.png)（PDF 物理页 1，Abstract 与 Introduction）

先从物理耦合看整篇论文。燃料电池侧四相交错 boost、蓄电池双向 boost-buck 和 PMSM 逆变器共享 DC link；变换器的开关状态改变电感电流、母线电压和电机电磁转矩，器件瞬态电压与电流又决定损耗，损耗经热阻热容网络改变结温，结温反过来影响器件特性。计算上，作者没有在一个统一的纳秒步长里求完整系统，而是把慢一些的网络状态、快开关波形和更慢的热状态拆到可并行或可流水的模块中，再用每个实时步的新旧状态把它们接回去。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Fig. 2、Fig. 3 与 Section 2）[pdf:E05](_evidence/E05-p005-fpga-pipeline.png)（物理页 5，Fig. 6）[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 3.2.4）

工程价值因此很具体：controller-HIL 不只检查控制闭环能否工作，还可能在线观察器件电应力、开关损耗和结温。论文报告网络实时步最小可到 685 ns，实际验证选择 1 μs，而 200 MHz 流水线每个时钟周期生成一个波形点，对应 5 ns 的器件暂态分辨率。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Section 1 末）[pdf:E05](_evidence/E05-p005-fpga-pipeline.png)（物理页 5，Section 3.1）[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 3.3）

## § 2 — 前人工作与不足

以下是论文对 2019 年以前相关工作的归纳，而不是本卡完成的独立系统综述。作者将既有工作分成三类。第一类是 MMC 等高功率场景的 FPGA/MPSoC 器件级实时仿真，这些应用的开关暂态通常在数微秒尺度；FCEV 变换器可到 100 kHz，暂态可短至几十纳秒，因而时间约束更苛刻。第二类 FCEV 实时仿真采用理想开关，能够验证整车和控制，但不能生成开关损耗。第三类已有 EV electro-thermal HIL 使用 associated discrete circuit 等效开关，没有表示开关暂态。[pdf:E01](_evidence/E01-p001-title-introduction.png)（物理页 1，Introduction，文献 [6]、[9]-[14]）

作者还指出，传统器件级模型通常是非线性的，并依赖迭代求解；真正的困难不是缺少 IGBT 模型，而是如何在纳秒级暂态所要求的短时限内完成求解。[pdf:E01](_evidence/E01-p001-title-introduction.png)（物理页 1，Introduction）论文随后采用的 Norton 静态模型、分段动态模型、拓扑 tearing 与流水线，本质上都在削减这一“器件精度导致的串行计算量”。但由于本任务没有额外检索 2-3 篇紧密相关全文，本卡不声称“双重分区”在更大文献范围内具有已验证的 novelty。

## § 3 — 重建作者的思考路径

下面是基于论文背景与方法结构的合理重建，不是作者逐字陈述。

第一步，若用 5 ns 作为整个 FCEV 电力电子系统的统一时间步，整车网络、PMSM、器件模型和热模型都会被迫以最快尺度运行，硬实时预算很可能失守。第二步，显式 Forward-Euler（FE）只依赖上一步历史状态，因此 DC-link 电容电压和 PMSM 电流可以先算，并以电压源或电流源的形式把共享网络切成三个变换器，再把重复的 half-bridge（HB）切成八个可并行子电路。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Section 2.1 与 Fig. 3）第三步，开关的稳态导通/关断不需要纳秒步；只有开通和关断沿需要高分辨率。因此可用 Norton 等效静态模型参与 1 μs 网络求解，再让动态模块稍后读取本步边界值，用分段线性或指数函数合成 5 ns 波形。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Section 2.2）[pdf:E04](_evidence/E04-p004-switch-dynamic-fpga.png)（物理页 4，Eq. (18)、Eq. (19)）

第四步，若每个 HB 都复制一套复杂 transient parameter computation（TPC），DSP48 消耗过高；所以作者保留八个波形生成器，却让八组 HB 状态按索引连续经过一套高度流水的 TPC。这样，参数计算被时间复用，波形生成仍保持每时钟一个点。[pdf:E05](_evidence/E05-p005-fpga-pipeline.png)（物理页 5，Fig. 6 与 Section 3.1）最后，既然器件电压、电流波形已经在线生成，就可计算损耗并驱动 Cauer 热网络，把系统级电磁动态与器件热行为放入同一实时闭环。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 3.2.4）

## § 4 — 核心 Intuition

核心 intuition 是：不要让整车网络为器件开关沿的最小时间尺度付出全局计算代价。作者用显式历史状态切开网络空间依赖，再把 IGBT 分成参与全局电路求解的静态 Norton 部分和只负责暂态形状的动态部分；FPGA 同时用并行处理多个 HB、用流水线在一个实时步内部生成纳秒波形。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Fig. 3）[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Section 2.2）这种方法以受控的模型简化和一个短延迟换取确定的实时吞吐，而不是实时求解完整非线性器件方程。

## § 5 — 具体方法与完整 Pipeline

以“PMSM 在额定转速附近遇到负载变化”为例，完整 pipeline 如下。

1. **系统输入与边界。** 模型包括四相交错 boost、三相两电平逆变器、双向 boost-buck 和 PMSM；燃料电池与蓄电池本体不在范围内，以两个理想电压源代替。作者认为未来可在 multi-rate 框架中接入其动态模型，但本文没有验证这一接口。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Fig. 2 与 Section 2）
2. **显式状态推进。** DC-link 电容按 Eq. (1) 用上一步电流更新电压；PMSM 的 \(d\)-\(q\) 电压、磁链、转矩和机械速度由 Eq. (2)-Eq. (8) 组成状态空间并用 FE 离散。由此，电容可作为已知电压源，PMSM 三相电流可作为注入逆变器的已知电流源。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Eq. (1)-Eq. (6)）[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Eq. (7)、Eq. (8)）
3. **拓扑分区与并行。** 三个变换器先按共享状态解耦，交错 boost 与逆变器再拆成重复 HB；最终八个子电路依据门极信号、电流方向和 Table 1 的器件状态，用 Eq. (9) 的 Norton 形式并行求支路电流与节点电压，再更新全局历史状态。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Fig. 4、Table 1、Eq. (9)）
4. **开关动态参数化。** 每个开关沿分成五个工作阶段。TPC 从 LUT 读取 IGBT transfer characteristics 和 diode reverse-recovery 曲线，并计算阶段区间、斜率、初值与时间常数；指数、对数和部分倒数也由 LUT 或预计算代替复杂运算。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Eq. (10)-Eq. (14)）[pdf:E04](_evidence/E04-p004-switch-dynamic-fpga.png)（物理页 4，Eq. (15)-Eq. (19)）[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 3.2.2）
5. **FPGA 调度。** NI-7975R 板上的 Kintex-7 XC7K410T 以 200 MHz 运行。网络 solver、控制单元、TPC、波形生成器和温度模块由 LabVIEW FPGA/IP Builder/HLS 生成 IP，放入 single-cycle timed loop；握手信号确定顺序。八组 HB 数据连续通过一套 TPC，八个 waveform generator 按 HB index 生成 \(v_{ce}\)、\(i_c\) 波形。[pdf:E04](_evidence/E04-p004-switch-dynamic-fpga.png)（物理页 4，Section 3）[pdf:E05](_evidence/E05-p005-fpga-pipeline.png)（物理页 5，Fig. 6）
6. **电-热回接。** 波形产生的 IGBT/diode 损耗 \(p_L\) 驱动十二个温度计算模块；Cauer 热阻热容网络用 FE 推进结温。器件特性只在 25°C 与 125°C 两个数据点之间做线性插值，再供后续步使用。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Fig. 7、Eq. (20)）
7. **输出。** 每个 1 μs 网络步输出整车电流、电压、转速和转矩，同时得到 5 ns 分辨率的开关波形、损耗及结温；这些量构成 controller-HIL 的物理 plant 响应。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 3.3）[pdf:E08](_evidence/E08-p008-hil-results-conclusion.png)（物理页 8，Fig. 12）

数值表示方面，论文报告使用 LUT、BRAM 和 DSP48 等资源，也报告了资源总量，但没有明确给出定点/浮点格式、各信号位宽、量化策略或溢出处理，因此这些内容保持“未报告”。[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Table 3）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有形式化数学，但真正的主线不是推导一个新积分器，而是把不同物理模块改写成可确定调度的显式形式。

**网络层。** 电容公式

\[
v_c(t)=v_c(t-\Delta t)+\frac{\Delta t}{C}i_c(t-\Delta t)
\]

表示本步电容电压只由历史电流决定；物理上是电荷守恒的显式积分，计算上则把共享 DC link 在当前步“冻结”为已知源。PMSM 先由 \(d\)-\(q\) 电压与磁链关系得到 \(i_d,i_q\) 的状态方程，再与电磁转矩 \(T_e\) 和机械速度 \(\omega_m\) 联立，统一写为 \(\dot{x}=Ax+Bu\)，最后用 Eq. (8) 的 FE 更新。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Eq. (1)-Eq. (6)）[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Eq. (7)、Eq. (8)）这里的关键计算意义是“只读历史值”，代价则是 FE 的步长稳定性与离散误差需要由足够小的实时步保证。

**HB 静态层。** Eq. (9) 写成

\[
I=mG_{HB}V+mK_{HB}J
\]

其中 \(G_{HB}\)、\(K_{HB}\) 由电流方向与上下管门极状态选择。物理上，导通器件被线性化为电导与等效电流源；计算上，每个 HB 变成小规模、状态可枚举的线性子问题。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Fig. 4、Table 1、Eq. (9)）

**器件动态层。** 作者把 IGBT 开通/关断分成五阶段：门极充放电与 tail current 用一阶指数，电流上升/下降和 Miller plateau 区段用线性斜率，diode reverse recovery 由特性曲线给定。最终所有波形片段都归约为

\[
x(t)=kt+x_0,\qquad y(t)=(y_0-u)e^{-t/\tau}+u .
\]

因此 TPC 只需给出 \(k,x_0,y_0,u,\tau\) 与阶段边界，waveform generator 就能每 5 ns 产生一个点，而不必每点迭代器件方程。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Eq. (10)-Eq. (14)）[pdf:E04](_evidence/E04-p004-switch-dynamic-fpga.png)（物理页 4，Eq. (15)-Eq. (19)、Fig. 5）

**热层。** Cauer 网络把结到壳的热传导表示为多级 \(R_{th}C_{th}\)，继续用 Eq. (8) 的 FE 推进。温度依赖特性 \(X(T_j)\) 则在 25°C 和 125°C 数据间线性插值：

\[
X(T_j)=\frac{X^{125^\circ C}-X^{25^\circ C}}{100}(T_j-25)+X^{25^\circ C}.
\]

这意味着模型包含损耗到结温、结温到器件特性的反馈，但只假定这一区间内近似线性。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Fig. 7、Eq. (20)）

## § 7 — 实验设计与结论

**问题 1：分区后的系统网络状态是否保持足够精度？** 作者把 FPGA 网络结果与 MATLAB/Simulink SimPowerSystems（SPS）比较，覆盖 PMSM 三相电流、四相 boost 电感电流、DC bus、电机转速和电磁转矩；误差按 0.4 s 仿真窗口求平均。Table 4 报告的十项误差从 \(v_{dc}\) 的 0.11% 到 \(i_{L1}\) 的 2.36%。论文据此认为电路级结果与参考模型一致。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 4.1）[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Fig. 8、Table 4）

**问题 2：简化动态模型能否保持器件开关暂态？** 作者以 CM100DY-12H IGBT 为例，用 SABER datasheet-driven IGBT 等效电路作参考。Table 5 分别报告 FPGA/SABER 的开通延迟 86/98 ns、上升时间 56/50 ns、关断延迟 1126/1135 ns、下降时间 183/175 ns，以及开通峰值损耗 40.8/42.5 kW、关断峰值损耗 30.2/29.6 kW；作者承认简化模型为计算效率牺牲了一些精度，但认为波形具有良好一致性。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Section 4.2）[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Fig. 9、Table 5）

**问题 3：电-热链是否产生合理响应？** 作者比较 10 kHz 与 20 kHz、相同 duty cycle 下的结温，观察到更高开关频率带来更大损耗与更高温升，且 20 kHz 相对 SABER 的局部误差更大。论文没有在表格中给出结温误差统计，本卡不从 Fig. 10 曲线估读精确温度差。[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Section 4.3）[pdf:E08](_evidence/E08-p008-hil-results-conclusion.png)（物理页 8，Fig. 10）

**问题 4：实现是否真正满足 FPGA 硬实时与资源约束？** 200 MHz 下，网络 solver initiation interval/latency 为 67/66 cycles，TPC 为 1/40 cycles，waveform generation 为 1/19 cycles；作者据调度得出实时步需大于 685 ns，实验选 1 μs。整机由 1 个网络 solver、1 个控制单元、1 个 TPC、8 个波形生成器和 12 个温度模块组成。Kintex-7 XC7K410T 使用 35,026/63,550 slices（55.1%）、91,698/254,200 slice LUTs（36.1%）、95/795 block RAMs（11.9%）和 704/1540 DSP48s（45.7%）。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Table 2 与 Section 3.3）[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Table 3）

**问题 5：模型能否作为 controller-HIL plant 响应控制命令？** 测试参数包括 10 kHz 开关频率、100 V 输入、500 V DC bus、3000 rpm 额定转速和 87 N·m 额定转矩。HIL 中，PMSM 先以 5000 rpm/s 从零升到 3000 rpm；随后负载以 300 N·m/s 从 0 增至 60 N·m；boost 还承受 0 与 60 N·m 间的负载阶跃。示波器波形显示转速、电流和 DC bus 对命令与扰动产生预期响应，作者据此判断模型可作为 HIL 物理 plant。[pdf:E08](_evidence/E08-p008-hil-results-conclusion.png)（物理页 8，Table 6、Fig. 12 与 Section 5）

**不得外推的范围。** 这些结果只覆盖论文给出的硬开关 IGBT 场景、单一 FPGA 板和所列工况；燃料电池与电池本体是理想源。论文没有验证软开关、显著寄生参数、更大开关规模、不同器件族、长时间数值稳定性或 plant 与真实功率硬件的一致性。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Section 2）[pdf:E09](_evidence/E09-p009-limitations-appendix.png)（物理页 9，Conclusion）

## § 8 — Take-aways

**5 句话。**  
1. 论文把 FCEV 变换器、PMSM 与器件热行为放进同一 FPGA controller-HIL plant，而不是只做理想开关的控制级模型。[pdf:E01](_evidence/E01-p001-title-introduction.png)（物理页 1，Abstract）  
2. 拓扑分区利用显式历史状态切断当前步依赖，使三个变换器及八个 HB 能并行求解。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2，Fig. 3）  
3. 开关模型分区把静态 Norton 网络与动态五阶段波形分开，以短延迟换掉实时迭代求解。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Section 2.2）  
4. 一套流水 TPC 被八个 HB 时间复用，而八个波形生成器保持 200 MHz、5 ns 的输出分辨率。[pdf:E05](_evidence/E05-p005-fpga-pipeline.png)（物理页 5，Fig. 6）  
5. SPS、SABER 与 controller-HIL 的三层验证支持“可实时且近似保真”，但不支持把结论扩展到软开关、强寄生或任意规模。[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Tables 3-5）[pdf:E09](_evidence/E09-p009-limitations-appendix.png)（物理页 9，Conclusion）

**3 句话。**  
1. 这项工作的关键不是单纯加快器件模型，而是按物理时间尺度与 FPGA 数据依赖重新安排模型。  
2. 1 μs 的整车网络步与 5 ns 的合成开关波形共存，使控制动态、开关损耗和结温能在一个实时平台上同时出现。[pdf:E06](_evidence/E06-p006-thermal-timing-validation.png)（物理页 6，Sections 3.2-3.3）  
3. 其有效性依赖于分段器件模型和被忽略寄生仍足以代表目标硬开关过程。

**1 句话。**  
作者用“空间上切网络、模型上切静态/动态、硬件上并行加流水”把 FCEV 的整车电气耦合压进 1 μs 实时步，同时保留 5 ns 器件波形导航。[pdf:E02](_evidence/E02-p002-topology-discretisation.png)（物理页 2）[pdf:E05](_evidence/E05-p005-fpga-pipeline.png)（物理页 5）

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标硬开关暂态可以忽略寄生电感，并用少量分段线性/指数片段从网络步边界值重建。** 作者在动态模型推导中明确以 \(L_s/R_g\) 很小为由忽略寄生电感，并在结论中再次承认，为计算效率未纳入 switching transient 的 parasitic inductance；模型也只面向 hard-switching。[pdf:E03](_evidence/E03-p003-switch-static-dynamic.png)（物理页 3，Stage 2）[pdf:E09](_evidence/E09-p009-limitations-appendix.png)（物理页 9，Conclusion）

这一假设失败时，受影响的不只是某个小误差指标。较大的封装/母排寄生会改变 \(dv/dt\)、\(di/dt\)、过冲、振铃、diode reverse recovery 与开关能量；软开关还会改变作者划分的五阶段顺序和边界。于是“5 ns 分辨率”可能只是高密度地采样了错误形状，电应力、损耗和结温三项器件级输出会同时失真。这是基于电路机制的推断，不是论文已完成的实验结论。论文提供了单一 CM100DY-12H 与 SABER 的波形对比，却没有给出寄生参数扫描、不同布局/器件的泛化或软开关工况；因此证据足以支持已测场景，不足以支持更广的器件级保真度。

## § 10 — 最小复现实验

一周内不必复现整车，只复现一个 inductive-load HB 的“静态网络 + TPC + waveform generator”链路。

- **数据与模型：** 使用 Appendix 给出的 IGBT/diode 参数，例如 \(R_g=30\,\Omega\)、\(C_{ge}=5\,\mathrm{nF}\)、\(C_{cg(s)}=0.5\,\mathrm{nF}\)、\(C_{cg(l)}=10\,\mathrm{nF}\)、\(\tau_{tail}=100\,\mathrm{ns}\) 和 \(\tau_{rr}=50\,\mathrm{ns}\)，并用论文 Fig. 5、Eq. (10)-Eq. (19) 实现五阶段动态模型。[pdf:E04](_evidence/E04-p004-switch-dynamic-fpga.png)（物理页 4，Fig. 5、Eq. (15)-Eq. (19)）[pdf:E09](_evidence/E09-p009-limitations-appendix.png)（物理页 9，Appendix 9.1）
- **实现：** 先在 CPU 上做 bit-accurate 或定步长参考，再在可用 FPGA 上以 200 MHz 实现一套 TPC 与一个波形生成器；每 1 μs 更新静态边界，每 5 ns 输出 \(v_{ce}\)、\(i_c\) 与瞬时损耗。
- **比较：** 用 SPICE/SABER 类详细器件模型产生同一开通/关断参考；只读模型明确输出的时间点和峰值，不从曲线手工估读。测量 \(t_{d(on)}\)、\(t_r\)、\(t_{d(off)}\)、\(t_f\)、开通/关断峰值损耗，以及硬件能否在实时步截止前完成。
- **支持标准：** 若复现实验能达到 1 μs 硬实时、5 ns 输出，并得到与论文 Table 5 同量级且方向一致的六项差异，就支持“分区动态模型能以小幅精度损失换实时吞吐”。[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Table 5）
- **反驳标准：** 若在复刻论文参数后仍不能守住截止时间，或关键时序/损耗偏差显著大到破坏器件应力判断，则核心 claim 在最小场景已不成立。资源数字不要求与 NI-7975R 完全一致，因为换板会改变综合结果。

## § 11 — 最强反例设计

最强反例不是再换一个负载阶跃，而是构造一个**寄生主导的双脉冲测试矩阵**。在相同 DC 电压、电流与门极电阻下，系统地增加 commutation-loop stray inductance，并加入可控 diode reverse-recovery；再增加一组接近 zero-voltage/zero-current switching 的工况。对每个点同时运行论文分段模型与包含封装、母排寄生的详细电路模型，比较峰值 \(v_{ce}\)、峰值 \(i_c\)、振铃频率、单次开关能量和由重复脉冲积累的结温。

如果论文模型在寄生增大后仍输出平滑五阶段波形，而详细模型出现足以改变安全裕度与损耗排序的过冲/振铃，且这种差异不能通过重新辨识 LUT 参数消除，就能排除“只是参数没调好”这一替代解释，直接击中静态/动态分割的结构性边界。若软开关下阶段顺序本身改变，则更进一步表明该方法不是通用 device-level solver，而是针对 hard-switching 的专用 surrogate。论文已明确未纳入寄生电感且只面向硬开关，因此这个反例是在已报告边界上施压，不是要求论文回答无关任务。[pdf:E09](_evidence/E09-p009-limitations-appendix.png)（物理页 9，Conclusion）

## § 12 — Follow-up Research Idea

**候选方向：事件条件化的多保真器件实时模型。** 由于没有做充分相关工作检索，这里不声称 novelty。

本领域高影响工作的评价通常不只看离线拟合误差，还看确定实时性、FPGA 资源、跨器件/工况的电应力与损耗保真度，以及真实 controller-HIL 的工程价值。本文未满足的需求是：固定五阶段 hard-switching surrogate 很高效，却无法知道“什么时候自己的简化已不可信”。[pdf:E07](_evidence/E07-p007-resources-errors-waveforms.png)（物理页 7，Tables 3-5）[pdf:E09](_evidence/E09-p009-limitations-appendix.png)（物理页 9，Conclusion）

可以把研究目标从“用一个简化模型覆盖所有开关事件”改为“在固定实时预算内，按事件风险选择最低但足够的保真度”。平稳、低寄生的硬开关事件仍走本文的线性/指数流水线；当在线指标预示 parasitic-sensitive commutation、reverse-recovery 异常或接近软开关边界时，只对受影响 HB 启用一个带局部 RLC 状态的短时 surrogate 或受限子步求解，其余 HB 不降速。可借鉴相邻领域的 adaptive multi-rate integration、runtime error estimator 和 selective refinement，但选择逻辑必须综合成有界延迟硬件，不能引入不可预测迭代。

第一个可证伪实验就是第 11 节的双脉冲矩阵：在相同 FPGA 资源上比较固定五阶段模型与事件条件化模型。如果后者不能在 1 μs 全局截止时间内显著降低峰值应力和开关能量误差，或频繁触发高保真路径导致吞吐崩溃，这个想法就失败。它与本文的实质区别不在于“多加一个寄生模块”，而在于把问题定义从固定器件模型的实时实现，改成带在线可信度判断的实时保真度分配。
