# A Multiport Power Electronic Transformer With MVDC Integration Interface for Multiple DC Units

**作者：** Xiaoquan Zhu, Jintao Hou, Bo Zhang  
**出处：** IEEE Transactions on Industrial Electronics, Vol. 71, No. 9, pp. 10704–10715  
**年份：** 2024  
**DOI：** 10.1109/TIE.2023.3331147  
**Zotero key：** QE8CSJG9  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** 这篇论文要解决的不是“再做一个 DAB”，而是把光伏、储能和直流负载等功率方向、额定功率和控制目标都不同的 dc units，直接接入 medium-voltage dc（MVDC）母线，同时保留电气隔离和单级功率变换。作者选择 input-independent output-series（IIOS）结构：每个 submodule（SM）有独立低压输入，各 SM 输出串联形成中压。它省去了传统“先汇到 LVDC 母线、再经 DCPET 升压”路径中每个 dc unit 前的额外低压 dc–dc converter，但不同端口功率不相等会立即转化为串联 SM 的输出电压不平衡，进而带来器件过压和母线失稳风险。论文把这个不平衡问题作为主矛盾，并提出带 multiwinding coupled-inductor（MWCI）的 isolated series-resonant dual-active-half-bridge（ISR-DAHB）来搬运 mismatch power；摘要同时声称全部 active switches 可实现 ZVS，并可在 on-grid 与 off-grid 条件下运行。[pdf:E01]（PDF 物理页 1，Abstract 与 Fig. 1）

这个问题重要，是因为串联输出结构只有在各 SM 电压可控时才能真正“模块化”。如果一个 4-SM 系统的总母线电压看起来正常，但单个 SM 因端口功率突变而过压，那么模块化并没有降低系统风险，只是把风险藏进了内部节点。反过来，如果能够用一个嵌入式磁耦合网络在不增加独立平衡变换器的前提下重分配 mismatch power，那么多种 dc units 可各自维持适合自身的本地控制目标，系统层只负责输出串联和能量平衡；这正是本文相对传统 LVDC 汇集架构的工程价值。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

## § 2 — 前人工作与不足

**论文原文明确声称。** 作者把相关路线分为三层。第一层是传统 DCPET/ISOP：它能连接 LVDC 与 MVDC、实现隔离和双向功率流，但每个 PV、storage 或 dc load 仍要通过额外 LVDC converter 接入；发生 dc unit 或 LVDC bus 故障时，系统还可能整体停机。第二层是已有 multiport DAB-based DCPET：它能接多个 dc units，但当 DCPET 与 MVDC 断开时，PV 和 battery 需要临时改变控制策略去维持母线电压，增加控制复杂度并使这些端口偏离各自最佳工作点。第三层是面向分布式 PV 的 IIOS converter：已有工作使用 bidirectional buck–boost balancer 或相邻 SM 之间的 LC power-balancing unit（PBU）传递 mismatch power，但其输入端主要都是 PV，尚未证明能让 PV、储能、负载和 LVDC bus 以不同控制目标共存。[pdf:E02]（PDF 物理页 2，Introduction）

本文的针对性改变有两个。其一，MWCI 的各绕组置于公共磁芯，使第一个 SM 与其余目标 SM 之间直接交换不平衡功率，避免 mismatch power 逐级经过相邻单元。其二，保留 SM#1 连接 LVDC bus：MVDC 离线时由 SM#1 接管全系统功率平衡，其余 SM 不必即时切换原有控制策略。作者据此把工作范围从“多路 PV 汇集”扩展到“异质 dc units 接入”。[pdf:E02]（PDF 物理页 2，Introduction 与 Fig. 2）

需要收紧的地方是：上述 prior-work 不足均来自本文自身的文献综述，本卡没有在 PDF 之外逐篇复核 [12]–[18] 的原始实验。因此这里可以确认“作者如何定位自己的贡献”，不能据此独立确认所有相关工作都没有等价方案，也不能声称本文在全领域具有已证实 novelty。

## § 3 — 重建作者的思考路径

下面是**基于论文背景与电路证据的合理重建**，不是作者逐字陈述。

第一步，研究者接受 IIOS 的基本收益：独立低压端口加串联高压输出，理论上能减少中间 LVDC conversion stage。第二步，他会发现串联只约束总电压，不会自动约束每个 SM 的分压；异质端口的输入功率一旦不同，各输出电容的充放电速度就不同。第三步，若用每个端口的主控制器去追逐内部电压平衡，PV 的 MPPT、battery 的充电电流和 load 的恒压目标就会互相干扰；若另加完整 bidirectional converter，又抵消了 IIOS 减器件、减级数的初衷。第四步，观察 DAB 各 SM 已经具有高频隔离端和输出半桥，于是把“不平衡功率通道”嵌入现有二次侧：用公共磁芯的多绕组把各 SM 输出电压差变成 resonant-tank 驱动力，让多余能量直接流向作为系统平衡端的 SM#1。[pdf:E02]（PDF 物理页 2，Fig. 2）[pdf:E03]（PDF 物理页 3，Section II-A/B 与 Fig. 3）

最后还要解决运行状态的责任分配：SM#1 用 constant output voltage（COV）约束串联分压基准，PV 继续 MPPT，battery 用 constant input current（CIC），load 用 constant load voltage（CLV）；MVDC、LVDC 或 battery 接入状态变化时，只切换功率平衡关系，不要求所有端口重写控制目标。论文的六种状态 A–F 正是把这一思路离散化。[pdf:E06]（PDF 物理页 6，Section II-D/E 与 Fig. 7）[pdf:E07]（PDF 物理页 7，Fig. 8）

## § 4 — 核心 Intuition

IIOS 把多个低压端口的输出电压串起来，却把端口功率彼此解耦，因此“谁多发、谁多吸”会表现为 SM 电压不齐。本文的核心 intuition 是：不要让每个主功率控制器都追着内部电压跑，而是让输出电压差通过共享磁芯和 series-resonant branches 自发形成 mismatch-power 通道，并用连接 LVDC 的 SM#1 充当全系统能量缓冲端。这样各端口可继续执行 MPPT、充电电流或负载恒压任务，而输出侧获得额外的电压均衡机制。[pdf:E02]（PDF 物理页 2，Fig. 2）[pdf:E06]（PDF 物理页 6，Section II-D/E）

## § 5 — 具体方法与完整 Pipeline

以论文的 4-SM 例子为主线，输入分别是 LVDC bus、PV array、storage device 和 dc load，输出是串联后的 MVDC bus。

1. **单个 SM 的功率级。** 每个 SM 使用两个 voltage-fed half-bridge terminal 和一个带漏感 \(L_{\mathrm{SM},k}\) 的高频隔离变压器；输出侧采用 voltage-doubling rectifier DAB 结构。输入电容 \(C_{1,k},C_{2,k}\) 各承受一半输入电压，输出电容 \(C_{3,k},C_{4,k}\) 各承受一半 SM 输出电压。MWCI 有 \(N\) 个绕组，除第一绕组外，各绕组串入 \(L_{r,k}\) 与 \(C_{r,k}\)，并接在二次侧开关与输出电容之间。[pdf:E03]（PDF 物理页 3，Section II-A/B、Fig. 3 与 Eq. (1)）
2. **SM 主功率控制。** 开关保持 50% duty cycle 并设置 dead time；一次侧与二次侧桥臂的 phase-shift ratio \(d_{\mathrm{SM},k}\) 决定该 SM 吸收还是发出功率。作者把一个周期拆成六个 mode，利用漏感和 resonant current 在换相前先让 body diode 导通，从而给出 ZVS 条件；Fig. 4 展示了六个等效电路，但图注最后一项误写为第二个 “Mode 5”，正文对应的是 Mode 6。[pdf:E03]（PDF 物理页 3，Fig. 3）[pdf:E04]（PDF 物理页 4，Fig. 4 与 Eq. (6)–(13)）
3. **mismatch-power 均衡。** 若 \(V_{o,k}\neq V_{o,1}\)，MWCI 两端的方波基波产生差模电压，驱动第 \(k\) 个 resonant tank。能量通过公共磁芯在 SM#k 与 SM#1 之间直接交换，而不是逐级穿过其余 SM。等效损耗 \(R_r\) 越小，同一 mismatch power 所需的输出电压偏差越小；因此低损耗磁件和 resonant branch 不是附属优化，而是电压平衡机制成立的条件。[pdf:E05]（PDF 物理页 5，Section II-C、Fig. 6 与 Eq. (18)–(23)）[pdf:E06]（PDF 物理页 6，Section II-D）
4. **端口本地目标。** SM#1 的 COV controller 以 \(V_{\text{bus}}/N\) 为参考调节 \(V_{o,1}\)；SM#2 的 MPPT 产生 PV power reference；SM#3 用 CIC 调节 battery current；SM#4 用 CLV 调节 load voltage。每个 controller 输出相应 phase shift 与逻辑信号，MWCI 在输出侧补偿端口功率差。[pdf:E06]（PDF 物理页 6，Fig. 7 与 Section II-D/E）
5. **系统状态与事件。** 状态 A–F 由 MVDC grid、LVDC grid 和 storage 的接入/断开以及 battery 是否充满触发。比如 on-grid 的 B→A 表示 battery 结束充电；off-grid 的 E→D 后，SM#1 用 COV 向负载补足功率；LVDC 断开时走 C→F，PV 的 surplus/deficit 由 MVDC grid 吸收或补给。论文给出了状态功率平衡式和拓扑关系，但**没有报告**故障检测阈值、debounce、状态机采样周期、切换优先级或保护时序。[pdf:E06]（PDF 物理页 6，Section II-E）[pdf:E07]（PDF 物理页 7，Fig. 8）
6. **输出与执行平台。** 各 SM 输出串联成为 MVDC bus。仿真在 MATLAB/Simulink 中完成；实验控制器是 TMS320F28335 DSP，而不是 FPGA。论文**未报告**离散化算法、定点/浮点格式、word length、流水线、并行依赖、FPGA resource、clock frequency、latency 或真实 hardware real-time step；文中的 100 ns 是仿真步长，不能当作控制器实时步长。[pdf:E08]（PDF 物理页 8，Table II 与 Section III-A）[pdf:E10]（PDF 物理页 10，Section III-B）

因此，这篇论文对 EMT/FPGA 的直接价值主要是可复现的拓扑、状态和控制对象，而不是已经给出的 FPGA implementation。若要做 FPGA-HIL，需要自行建立 switch/event model、离散 resonant tank、状态机保护和固定点误差预算，不能从本文补写这些未报告项。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化电路推导。先把关键变量讲清：\(V_{\mathrm{in},k}\) 与 \(V_{o,k}\) 是第 \(k\) 个 SM 的输入/输出电压，\(n_k\) 是隔离变压器变比，\(f_s\) 是 switching frequency，\(L_{\mathrm{SM},k}\) 是漏感，\(d_{\mathrm{SM},k}\) 是一次与二次开关信号的 phase-shift ratio。

**1. 电容分压与换相。** 稳态下作者先给出

\[
V_{c1,k}=V_{c2,k}=V_{\mathrm{in},k}/2,\qquad
V_{c3,k}=V_{c4,k}=V_{o,k}/2 .
\]

这说明两个 half-bridge 都以中点电压工作。六个 operation modes 中，漏感电流不能瞬变，使下一只开关的 body diode 在 gate 到来前先导通，进而把 drain–source voltage 拉到零；Eq. (2)–(15) 分别写出了二次侧 KCL、漏感斜率和 resonant current/capacitor voltage。[pdf:E03]（PDF 物理页 3，Eq. (1)–(5) 与 Fig. 3）[pdf:E04]（PDF 物理页 4，Eq. (6)–(13) 与 Fig. 4）

**2. phase shift 到 SM 功率。** 采用 state-space averaging，作者把 SM 传输功率写成 Eq. (17)：

\[
P_{\mathrm{SM},k}=
\begin{cases}
\dfrac{V_{\mathrm{in},k}^{2}d_{\mathrm{SM},k}}
{4n_k f_s L_{\mathrm{SM},k}}\left(1-d_{\mathrm{SM},k}\right),
& d_{\mathrm{SM},k}\ge 0,\\[6pt]
\dfrac{V_{\mathrm{in},k}^{2}d_{\mathrm{SM},k}}
{4n_k f_s L_{\mathrm{SM},k}}\left(1+d_{\mathrm{SM},k}\right),
& d_{\mathrm{SM},k}<0.
\end{cases}
\]

普通语言解释是：phase shift 的符号决定功率方向，幅值决定功率大小；\(|d|\) 过大时 backflow power 增加，所以作者建议把 \(d_{\mathrm{SM}}\) 限制在 \([-0.5,0.5]\) 以内。[pdf:E05]（PDF 物理页 5，Eq. (16)–(17) 与 Fig. 5）

**3. 输出电压差到均衡功率。** 对 MWCI port square wave 做 fundamental-wave approximation 后，差模基波为 Eq. (19)

\[
\Delta v_k(t)=\frac{2(V_{o,k}-V_{o,1})}{\pi}\sin \omega_s t ,
\]

于是 resonant current 近似为 \(i_{r,k}=\Delta v_k/R_r\)。作者进一步给出

\[
P_{\mathrm{SR},k}\approx
\frac{2V_{o,k}}{\pi^2R_r}(V_{o,1}-V_{o,k})
\]

以及 Eq. (23) 所示的 \(V_{o,k}\)、\(P_{\mathrm{SR},k}\)、\(R_r\) 关系。物理意义比公式形式更重要：要搬运的 mismatch power 越大、resonant path 损耗越大，所需的 SM 电压差就越大；理想“电压相等”只在 \(R_r\) 很小的近似下成立。[pdf:E05]（PDF 物理页 5，Eq. (18)–(23) 与 Fig. 6）

这里有一个必须保留的数学疑点：若逐字采用 Eq. (22) 的正负号，直接消元并不能无歧义得到 Eq. (23) 根号内所印的符号；原文对 \(P_{\mathrm{SR},k}\) “absorbed or emitted”的正方向也没有说明到足以消除该歧义。因而 Eq. (22)–(23) 可作为“损耗和 mismatch 决定电压偏差”的定性依据，但在复现中必须先统一功率正方向，再重新推导，不能照抄为无条件的定量模型。[pdf:E05]（PDF 物理页 5，Eq. (22)–(23)）

**4. loss/efficiency model。** 作者用 turn-off loss、\(C_{\mathrm{oss}}\) loss 和 conduction loss 建立开关损耗，再叠加 inductor、capacitor、transformer loss 计算效率；后面三类损耗的具体表达式沿用文献 [17]、[18]，本文没有重新给出。因此论文内的效率比较并非完整自包含的损耗模型。[pdf:E07]（PDF 物理页 7，Eq. (24)–(28)）[pdf:E08]（PDF 物理页 8，Eq. (29)–(33) 与 Fig. 9）

## § 7 — 实验设计与结论

**问题 1：六个换相 mode 与 ZVS 机理是否在真实波形中出现？ → 实验。** 4-SM downscaled prototype 给出 SM#1 的 \(v_{\mathrm{GS},S1}\)、\(v_{\mathrm{GS},S3}\)、漏感电压/电流，以及三个 resonant-tank currents；示波图的电压、电流换相和近似正弦 resonant currents 与理论波形相符。**答案。** 这支持“该工作点下换相方向与 resonant coupling 正确”，但论文没有逐开关、逐功率方向展示 \(v_{\mathrm{DS}}\) 在 gate 前归零，也没有给出 ZVS operating boundary，因此不足以证明“所有 active switches 在全工况都 ZVS”。[pdf:E09]（PDF 物理页 9，Fig. 12）

**问题 2：端口状态变化时，SM 电压能否保持平衡？ → 仿真。** MATLAB/Simulink 采用 4 SM、100 ns simulation step；输入额定电压 375 V，SM switching frequency 50 kHz。作者执行 B→A→A、E→D→A、C→F→A 三条状态序列，包含 battery 充满、负载变化、MVDC/LVDC reconnect。Fig. 10 中各 SM 输出在扰动后回到约 750 V，总 MVDC bus 保持约 3000 V，图上标注的单次 SM 波动约为 4.8–10 V，off-grid bus 建立过程标注约 40 V 波动。[pdf:E08]（PDF 物理页 8，Table II 与 Section III-A）[pdf:E09]（PDF 物理页 9，Fig. 10）[pdf:E10]（PDF 物理页 10，Fig. 10 说明） **答案。** 仿真支持所选参数与状态序列下的电压再平衡，但没有参数不确定性、通信/采样 delay、磁饱和、器件温升或 fault-current 仿真。

**问题 3：on-grid、off-grid 和 LVDC-disconnected 三类运行能否在硬件上完成？ → 实验。** prototype 使用 48 V dc source 代替 PV，MPPT 被简化为 constant-current control，384 V constant-voltage source 代替 MVDC grid；4 个 SM 的输入约 48 V、输出约 96 V 串联。控制器为 TMS320F28335，实验 switching frequency 20 kHz，主变压器变比 1:2，MWCI 变比 1:1:1:1。[pdf:E08]（PDF 物理页 8，Table II）[pdf:E10]（PDF 物理页 10，Section III-B） Fig. 13(a) 的 on-grid 状态 B 中，SM#1–#4 电流约为 4.5、5.5、−1.2、−4 A；按 48 V 计算 net grid power 为 230.4 W，理想 grid current 约 0.6 A，计入损耗后实测约 0.4 A。负载从 12 Ω 变到 8 Ω 后，grid current 由 0.6 A 降到 0.25 A。[pdf:E11]（PDF 物理页 11，Section III-B 与 Fig. 13） **答案。** 三条状态序列在缩比、受控 dc-source 环境中均能连续运行，证明基本功率路由可行；但它没有验证真实 PV MPPT、MVDC insulation、medium-voltage semiconductor、grid fault 或额定热稳态。

**问题 4：器件应力和效率是否优于已有 PBU？ → 分析比较。** Table I 比较 [17]、[18] 与 proposed topology 的 analytic voltage/current stress；作者指出 proposed primary-switch current stress 较高，但一次侧开关数是 [17]、[18] 的一半，二次侧 switching current stress 较低。8-SM、rated-load、\(P_r=24\) kW 的 loss calculation 在 Fig. 9 给出约 91%–95% 的效率区间。[pdf:E07]（PDF 物理页 7，Table I）[pdf:E08]（PDF 物理页 8，Fig. 9） **答案。** 这些结果只支持同器件、同 operating condition、所采用 loss model 下的相对趋势。Fig. 9 的多个柱值并不一致支持正文“large mismatch 时远高于 [17] 且接近 [18]”这一概括，例如最右组 proposed 约 94%、[17] 约 94.5%、[18] 约 95%；因此不能把该图外推成普遍效率优势。[pdf:E08]（PDF 物理页 8，Fig. 9）

还有两个报告质量问题值得复现者提前处理。第一，Table II 把实验 resonant capacitance \(C_r\) 的数值 “10” 后单位印成 \(\mu\text{H}\)，从量纲看很可能是排版错误，但 PDF 没有更正，不能擅自当作 \(10\,\mu\text{F}\)。第二，实验是 336 W 级 dc-source setup，而不是论文标题语境中的实际 MVDC 设备；它证明 topology/control concept，不证明中压绝缘、热设计或 full-scale efficiency。[pdf:E08]（PDF 物理页 8，Table II）[pdf:E10]（PDF 物理页 10，Section III-B）

## § 8 — Take-aways

**5 句话。**  
1. 本文把 IIOS 的“多低压独立输入、输出串联升到 MVDC”用于 PV、storage、load 和 LVDC bus 的异质组合，而不只是一组同类 PV 端口。[pdf:E02]（PDF 物理页 2，Fig. 2）  
2. 它用共享磁芯的 MWCI 加 series-resonant branch，把 mismatch power 在 SM#1 与目标 SM 之间直接交换，以输出电压差驱动均衡。[pdf:E05]（PDF 物理页 5，Eq. (18)–(23)）  
3. SM#1 负责 COV 和系统能量缓冲，其余端口维持 MPPT、CIC、CLV，从而把设备本地目标与系统平衡责任分开。[pdf:E06]（PDF 物理页 6，Fig. 7 与 Section II-E）  
4. 4-SM 仿真与 384 V 缩比实验支持三类状态序列和基本电压平衡，但没有验证实际 MVDC、真实 PV MPPT、全工况 ZVS 或 FPGA 实时实现。[pdf:E09]（PDF 物理页 9，Fig. 10–12）[pdf:E10]（PDF 物理页 10，Fig. 13 与 Section III-B）[pdf:E11]（PDF 物理页 11，Section III-B）  
5. 最值得带走的并不是“已经得到一个普遍高效方案”，而是一个可检验的机制：\(R_r\)、mismatch power 与 SM voltage error 构成同一条约束链。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Eq. (22)–(23)）

**3 句话。**  
1. IIOS 减少 conversion stages，却把端口功率不匹配变成内部串联电压风险。  
2. MWCI resonant path 负责快速重分配 mismatch power，SM#1 则提供系统级能量平衡。  
3. 现有证据证明缩比可行性，不证明 medium-voltage scale、全工况 ZVS、效率优势或 FPGA feasibility。

**1 句话。**  
本文展示了一种“主端口各做各的控制、共享磁耦合支路专门消化功率不匹配”的 multiport MVDC PET 架构，但其成立边界取决于低损耗耦合网络和一个始终可用的能量平衡端。

## § 9 — 最脆弱的假设

最脆弱的假设是：**MWCI 与 resonant branches 的等效损耗足够小，而且 SM#1/LVDC 端在需要时具有足够双向功率裕量，于是任意实际 mismatch 都能在器件电压和 ZVS 边界内被吸收。**

这是核心假设，因为 Eq. (22)–(23) 与 Fig. 6 已经说明 \(R_r\) 和 transferred power 会直接拉开 \(V_{o,1}/V_{o,k}\)；若 winding resistance、leakage、core loss、temperature drift 或 coupling mismatch 使 \(R_r\) 增大，均衡机制必须先产生更大的电压差才能传同样功率。与此同时，SM#1 是所有 resonant currents 的叠加点，Table I/后续电流公式也表明它的 current stress 与其他端口并不对称。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Eq. (22)–(23)）[pdf:E07]（PDF 物理页 7，Table I 与 Eq. (25)–(28)）

论文给出的正面证据是 4-SM nominal-parameter simulation、一个 336 W 缩比 prototype 和三条有限状态序列；它没有给出 \(R_r\) 实测、磁芯温升、coupling coefficient、component tolerance、饱和裕量、SM#1 power-limit sweep 或“可均衡 mismatch power vs. allowed voltage error”的 envelope。[pdf:E08]（PDF 物理页 8，Table II）[pdf:E10]（PDF 物理页 10，Fig. 13 与 Section III-B）[pdf:E11]（PDF 物理页 11，Section III-B） 因此，**基于证据的合理推断**是：论文证明了一个 nominal operating point family，而不是证明了规模扩展后仍存在足够宽的安全工作域。

## § 10 — 最小复现实验

一周内最有价值的复现不是复制完整 384 V prototype，而是做一个可证伪的 4-SM switched simulation，并把 \(R_r\) 与 SM#1 power limit 作为显式自变量。

1. **模型。** 按 Fig. 2(b) 建 4 个 voltage-doubling DAB SM、output-series bus、MWCI 的 1:1:1:1 coupling 和三个 \(L_r\)-\(C_r\) branch；先用 Table II 的 simulation 参数：375 V input、750 V/SM、50 kHz、\(L_{\mathrm{SM}}=2.7\,\mu\text{H}\)、\(L_r=2\,\mu\text{H}\)、\(C_r=5\,\mu\text{F}\)、100 ns solver step。[pdf:E02]（PDF 物理页 2，Fig. 2(b)）[pdf:E08]（PDF 物理页 8，Table II）
2. **控制。** 实现 SM#1 COV、SM#2 power reference（先不用真实 MPPT）、SM#3 CIC、SM#4 CLV；phase shift 用 Eq. (17) 的方向约定。先重放 B→A、E→D→A、C→F→A，再加一个 paper 未做的 \(R_r\) sweep 和 SM#1 current limit。[pdf:E05]（PDF 物理页 5，Eq. (17)）[pdf:E06]（PDF 物理页 6，Fig. 7 与 Section II-E）[pdf:E07]（PDF 物理页 7，Fig. 8）
3. **对照。** 对每个工况分别运行 MWCI enabled、MWCI disabled，以及 \(R_r\) 从 nominal 小值逐步增大的版本。保持端口功率和控制器不变，避免把 controller retuning 误当成 topology benefit。
4. **测量。** 记录 \(\max_k|V_{o,k}-V_{\mathrm{bus}}/4|\)、settling time、SM#1 peak/RMS current、resonant current、bus-voltage deviation，并检查每个开关在 gate-on 前的 \(v_{\mathrm{DS}}\) 与电流方向，而不是只看 gate 和 inductor current。
5. **支持/反驳条件。** 若三条状态序列下 MWCI enabled 相比 disabled 明显降低最大 SM voltage error，且 \(R_r\) 增大时误差按 Eq. (23)/Fig. 6 所预示的方向单调恶化，核心均衡机理得到支持；若低损耗 nominal case 仍需主端口控制器共同改目标、SM#1 先触及 current limit，或某些开关失去 ZVS，则核心 claim 被反驳或至少需要缩小适用范围。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Eq. (23)）[pdf:E09]（PDF 物理页 9，Fig. 10–12）

这个实验不需要 FPGA。若之后要转 FPGA-HIL，应另行定义 discrete companion model、fixed-point format、event ordering 和 latency budget，因为论文没有提供这些实现事实。

## § 11 — 最强反例设计

最强反例是构造一个**高 mismatch、热致高 \(R_r\)、SM#1 受限**的组合工况，而不是简单制造短路。具体做法是：让 SM#2 突然从低功率升到高功率，同时 SM#4 加载、SM#3 到达 charge cutoff；使系统从 E→D 或 C→F 过渡，并给 SM#1 施加真实 current/power limit。与此同时，通过升温、串入可控电阻或降低 coupling coefficient，把三个 resonant paths 做成不对称。

攻击逻辑如下：如果作者的核心机制足够强，MWCI 应在不改变 SM#2–#4 本地控制目标的情况下，把 mismatch 导向 SM#1，并让所有 \(V_{o,k}\) 留在安全窗口、bus 稳定、开关保持 ZVS。若观察到最弱耦合端的 voltage error 持续扩大、SM#1 current 叠加触发限流、总 bus 仍正常但单个 capacitor 过压，或换相电流方向改变导致 ZVS 丢失，那么“共享磁芯直接传功率”仍然成立，却不能推出“多端口系统可稳定均衡”。这个反例直接利用论文自己的 \(R_r\)-power-voltage 关系和 SM#1 current superposition，而不是引入无关故障。[pdf:E05]（PDF 物理页 5，Eq. (22)–(23)）[pdf:E07]（PDF 物理页 7，Eq. (25)–(28)）

还应增加一个 simultaneous loss-of-grid 场景：MVDC 与 LVDC 都不可用且 storage 到达限制。论文只分别覆盖 MVDC disconnected、LVDC disconnected 和二者共同存在，没有证明两个能量平衡端同时不可用时仍可维持系统；此时正确结果可能是受控停机，而不是继续运行。若论文的 claim 被理解成“任何 off-grid 情况都稳定”，这个场景会直接反驳它；若 claim 被收窄为“至少一个平衡端可用”，则它帮助明确必要前提。[pdf:E06]（PDF 物理页 6，Section II-E）[pdf:E07]（PDF 物理页 7，Fig. 8）

## § 12 — Follow-up Research Idea

**候选研究想法，不声称 novelty：** 把 multiport IIOS PET 的研究目标从“提出一种 nominally self-balancing topology”改写为“合成并在线认证一个可保证的 power-mismatch safe envelope”。这个 envelope 同时约束每个 SM capacitor voltage、SM#1 current、MWCI flux/temperature、ZVS margin 和可用 energy-buffer capacity；端口控制器只有在当前状态位于该 envelope 内时才保持原目标，越界前则由 supervisory allocator 决定限功率、重分配或受控停机。

（a）未满足需求是：现有论文没有回答在 \(R_r\)、coupling、temperature、component tolerance 和端口功率边界变化时，最大可承受 mismatch 到底是多少。  
（b）它可能产生本领域认可的价值，因为 medium-voltage PET 的关键不是 nominal waveform 漂亮，而是能否给出可审计的 insulation、thermal、semiconductor stress 和 transient safety margin，并在真实 hardware 上验证。  
（c）可借鉴相邻领域的 robust control invariant set、port-Hamiltonian/passivity analysis、reachability 与 online set-membership estimation，把 resonant network 从“经验性 balancer”变成带证书的功率路由约束。  
（d）第一个证伪实验是：在 4-SM HIL/缩比 bench 上联合 sweep \(R_r\)、coupling、temperature、SM#1 limit 与 mismatch step；预先计算 safe envelope，再检查所有越界是否都被提前预测。若出现 envelope 内的 capacitor overvoltage、ZVS loss 或 magnetic saturation，方法立即失败。  
（e）它与本文的实质区别不是再加一个 controller，而是改变研究问题：本文证明特定 topology 在少量 nominal transitions 下可工作；候选方向要求对不确定性下“何时可以继续工作、何时必须限功率或停机”给出可证伪边界。其事实出发点是本文已经显示 \(R_r\)、mismatch power 与 voltage ratio 相互耦合，但没有给出该边界。[pdf:E05]（PDF 物理页 5，Fig. 6）[pdf:E08]（PDF 物理页 8，Table II）[pdf:E11]（PDF 物理页 11，Section III-B）
