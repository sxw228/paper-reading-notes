# A Model Review for Controller-Hardware-in-the-Loop Simulation in EV Powertrain Application

作者：Wenming Gong、Chen Liu、Xiaobin Zhao、Shukai Xu  
出处：IEEE Transactions on Transportation Electrification, Vol. 10, No. 1  
年份：2024  
DOI：10.1109/TTE.2023.3290999  
Zotero key：XPWVTPC2  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文不是提出一个新的 CHIL 算法，而是回答一个工程选型问题：在 EV powertrain 的 controller-hardware-in-the-loop simulation（CHIL）中，怎样同时处理控制器与 digital real-time simulator（DRTS）之间的接口时序，以及 power converter、energy storage system（ESS）和 electrical machine 的实时模型选择。作者把综述分成 interfaced model 与 powertrain model 两条主线，并进一步讨论 FPGA 在缩短步长和并行求解中的作用。[pdf:E01]（PDF 物理页 1，Abstract、Section I）

这个问题重要，是因为 CHIL 用真实控制器闭环连接虚拟动力总成，可以在没有原型机或不冒损坏高功率原型风险时提前测试控制器。论文原文把它定位为连接纯软件仿真与功率实验之间的低成本、安全、节省开发时间的验证手段；难点则来自 EV 动力总成的多物理域、高功率与高频控制，以及商业实时仿真器对厂商模型库的依赖。[pdf:E01]（PDF 物理页 1，Introduction）

其实际价值不是“某个模型精度更高”这么单一，而是帮助工程师回答：某种控制频率下需要多小的闭环响应时间，哪些开关事件必须重建，哪些子系统可以用慢速等效模型，哪些必须放到 FPGA 上，以及为更细模型付出的计算和资源代价是否值得。

## § 2 — 前人工作与不足

论文梳理的已有接口方案包括 interpolation、extrapolation 及其与 state-space equation 的结合，用来补偿控制器 PWM 边沿落在 DRTS 两个离散步之间造成的 internal switching event。它们可用于 CPU/DSP-based DRTS，但论文指出这类平台的采样和仿真步长很难低于 \(1\,\mu s\)，且补偿算法会增加计算负担；相对地，文献中的 FPGA-based DRTS 可实现超过 \(50\,MHz\) 的 I/O sampling rate 和低于 \(500\,ns\) 的计算时间。[pdf:E02]（PDF 物理页 2，Section II-B、Fig. 3）[pdf:E03]（PDF 物理页 3，Section II-B）

对 power converter，已有 system-level 方法主要分为“预存全部开关拓扑对应矩阵”和“在线求逆/迭代求解”。前者避开在线矩阵求逆，却随耦合开关数增加产生存储瓶颈；后者节省矩阵存储，却把压力转移到 DSP48 等运算资源和除法、迭代延迟。Associated Discrete Circuit（ADC）可让导纳矩阵不随开关状态变化，但参数依赖外部电路，并可能引入虚拟功率损耗和拓扑切换振荡。[pdf:E03]（PDF 物理页 3，Section III-A-1）

对 device-level IGBT、PEMFC 和 machine，已有工作面对同一类矛盾：加入开关瞬态、寄生参数、多物理场、磁饱和或故障后，模型更接近物理系统，却更难满足实时 deadline。论文汇总的 IGBT 方案横跨数值物理模型、datasheet/curve-fitting、lookup table 和简化分段模型，各自在 calculation time、accuracy、complexity 与是否需要实验数据之间交换代价。[pdf:E04]（PDF 物理页 4，Table I、Section III-A-2）[pdf:E05]（PDF 物理页 5，Table II、Section III-B）

最关键的不足不是“前人没建模”，而是现有成果往往针对不同硬件、不同规模和不同精度目标，工程师仍缺少一个可直接把应用时间尺度、模型保真度、数值稳定性和硬件资源连起来的选择依据。本文试图用分类、对比表和案例汇总填这个知识组织缺口，但它本身没有建立统一 benchmark。

## § 3 — 重建作者的思考路径

以下是基于论文所引文献与结构重建的思考路径，不是作者明示的发明过程。

第一步，从 CHIL 的闭环事实出发：控制器送出 PWM，DRTS 采样控制信号、推进模型，再把状态量送回控制器。一次闭环响应必须容纳 input、calculation 和 output；若采样错过步内开关边沿，误差会直接进入下一次控制决策。[pdf:E02]（PDF 物理页 2，Figs. 1–3、Section II-A/B）

第二步，把“实时”从模糊标签改写为 deadline：模型不是离线算得越细越好，而是必须在下一次 I/O 交换前完成。于是接口重建、模型求解和输出延迟共享同一个时间预算。

第三步，按动力总成物理时间尺度拆分模型。ESS 的慢动态、machine 的电磁动态、converter 的开关动态和 semiconductor 的器件瞬态并不需要同一步长；如果强迫全系统采用最小步长，计算量会被最快子过程绑架。[pdf:E06]（PDF 物理页 6，Battery ECM 与 machine model）[pdf:E07]（PDF 物理页 7，Table IV）论文据此把模型族、solver 和平台放到同一张时间尺度图中。[pdf:E08]（PDF 物理页 8，Fig. 8）

第四步，再问硬件结构是否匹配计算依赖。CPU 适合复杂但相对慢的多物理模型，FPGA 适合固定数据流、细粒度并行和高采样；CPU/FPGA hybrid 由此成为 multirate co-simulation 的自然结果。这个推理最终导向本文的核心组织方式：接口时序约束先行，再按 converter、ESS、machine 分层选择模型与求解资源。

## § 4 — 核心 Intuition

CHIL 的核心不是单独追求最高 model fidelity，而是在闭环 deadline 内保留对控制器决策真正重要的动态。不同子系统应按自身时间尺度选模型、solver 和硬件；FPGA 的价值在于把高频采样与可并行的快速求解前移，而不是自动让任何复杂模型都实时。综述真正想提供的是一张“物理细节—数值方法—计算平台—可达步长”的工程地图。

## § 5 — 具体方法与完整 Pipeline

由于本文是 model review，下面的 pipeline 是作者所归纳 CHIL 架构的重组，不是论文交付的一套新代码。

1. **控制输入与接口采样。** 真实 controller 通过 ADC/DAC/I/O 与 DRTS 交换信号：controller 输出 PWM/gate signal，DRTS 返回电压、电流、转速等模拟状态。[pdf:E02]（PDF 物理页 2，Figs. 1–2）
2. **步内事件重建。** DRTS 检查 controller clock 与 simulator sample clock 之间是否出现 internal switching event；低采样率会形成 Fig. 3 所示 error area。可用 interpolation/extrapolation 估计开关时刻，或用 FPGA 提高采样分辨率，减少需要补偿的事件。[pdf:E02]（PDF 物理页 2，Fig. 3、Section II-B）
3. **更新 converter 拓扑。** FPGA solver 的典型数据流由 update unit、保存网络方程的 keeper unit、matrix-vector multiplier 组成。System-level 模型把器件视为 ideal/quasi-ideal switch，采用预存矩阵、ADC/SSN 或在线矩阵求解；device-level 模型则加入开关瞬态和 electrothermal 等非线性。[pdf:E03]（PDF 物理页 3，Fig. 4、Section III-A）
4. **推进 ESS。** Lithium battery 常用 RC-branch ECM，以 load current 与 core temperature 为输入，通过 SOC/temperature lookup table 更新电阻、电容和 open-circuit voltage，输出 terminal voltage 与 SOC。PEMFC 可从仅描述端口特性的 ECM，逐步升级到 0-D、1-D、2-D、3-D 多物理模型；维数越高，内部状态越丰富，stiffness 与实时 overrun 风险也越大。[pdf:E05]（PDF 物理页 5，Fig. 5、Section III-B）[pdf:E06]（PDF 物理页 6，Fig. 6、Eqs. (3)–(9)）
5. **推进 machine。** Induction machine 和 PMSM 可用 rotating \(dq\) frame；要覆盖 saturation、spatial harmonics、iron loss 或 fault，可改用 phase-domain、FEA-derived lookup table 或 nonlinear flux map。SRM 通常用 rotor position、exciting current 与 flux 的 lookup table，或计算更重的 magnetic equivalent circuit/hybrid analytical model。[pdf:E07]（PDF 物理页 7，Eqs. (10)–(12)、Table IV）
6. **multirate 与硬件映射。** 论文给出的实例是把 fuel-cell model 放在 CPU、把 dc-ac converter 放在 FPGA，以避免慢速多物理过程和快速开关过程互相绑死；FPGA 通过 customized parallel architecture 缩短 converter/machine 的时间步。[pdf:E03]（PDF 物理页 3，Section II-B）
7. **输出与闭环。** 在 deadline 内算出 simulated state，经 DRTS output port 返回 controller，进入下一控制周期。若 input/output latency、event reconstruction 和 model calculation 的总和超过预算，就会出现 overrun、延迟或稳定性风险。

论文未报告作者自己实现的 HDL、fixed-/floating-point word length、pipeline depth、FPGA resource utilization、clock frequency、综合目标板、I/O calibration、统一软件包或可下载数据；Table V 汇总的是不同文献中的 Typhoon、dSPACE、NI PXIe、Opal-RT 等案例，而不是本文运行的一套平台。[pdf:E08]（PDF 物理页 8，Table V）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文是综述，没有一个从假设到定理或算法收敛性的统一推导。它给出三组用于解释模型和实时约束的代表性公式；下面说明其工程含义，不把它们误写成作者的新理论。

**1. 闭环时间预算。** 论文按经验要求把 CHIL 响应时间限制为开关控制周期的百分之一：

\[
T_{\mathrm{CHIL}}\le 0.01T_{\mathrm{s\_control}},
\]

\[
T_{\mathrm{Cal}}
=T_{\mathrm{CHIL}}-T_{\mathrm{Input}}-T_{\mathrm{Output}}
\le 0.01T_{\mathrm{s\_control}}-T_{\mathrm{Input}}-T_{\mathrm{Output}}.
\]

其中 \(T_{\mathrm{Input}}\) 与 \(T_{\mathrm{Output}}\) 分别是 DRTS input sampling period 和 output period，\(T_{\mathrm{Cal}}\) 是留给模型计算的时间。这不是稳定性定理，而是论文引用实践经验形成的 sizing rule：I/O 越慢，可用于求解的预算越少。[pdf:E02]（PDF 物理页 2，Eqs. (1)–(2)）

**2. Battery ECM。** 论文先用 lookup function 表示参数依赖：\(R_0=f(SOC,T)\)、\(E_m=f(SOC,T)\)、\(C_{\mathrm{batt}}=f(T)\)、\(R_n=f(SOC,T)\)、\(C_n=f(SOC,T)\)。随后用

\[
V_T=E_m-I_{\mathrm{batt}}R_0-\sum_{n}V_n,\qquad
V_n=\int_0^t\left(\frac{I_{\mathrm{batt}}}{C_n}-\frac{V_n}{R_nC_n}\right)dt,
\]

\[
V_{\mathrm{out}}=N_SV_T,\qquad
SOC=-\frac{1}{C_{\mathrm{batt}}}\int_0^t I_{\mathrm{batt}}dt
\]

推进端口电压与 SOC。其 intuition 是：\(R_0\) 描述瞬时压降，每个 \(R_nC_n\) 支路描述一个极化时间常数，SOC 是电流随时间的电量积分。论文在 Eq. (8) 后把 \(N_S\) 解释为 series RC-pair 数；这一符号说明与 \(V_{\mathrm{out}}=N_SV_T\) 的电芯串联含义存在表述歧义，本文未进一步澄清。[pdf:E06]（PDF 物理页 6，Fig. 6、Eqs. (3)–(9)）

**3. Machine flux map。** PMSM 的 2-D data model 用 \(i_d=f(\psi_d,\psi_q,\theta_r)\)、\(i_q=g(\psi_d,\psi_q,\theta_r)\) 把 FEA 或测量得到的 flux-current relationship 压缩成 lookup table，并以 \(T_e=1.5P(\psi_di_q-\psi_qi_d)\) 求 electromagnetic torque；\(P\) 是 pole-pair 数。[pdf:E07]（PDF 物理页 7，Eqs. (11)–(12)）论文 Eq. (10) 给出 phase-domain voltage balance，但 PDF 将磁链导数印为 \(d\psi_{abc}/dx\) 且未定义 \(x\)；因此这里不擅自改写为常见的时间导数。

## § 7 — 实验设计与结论

本文未报告作者新搭建的 controller、DRTS 或 EV powertrain 实验，也没有统一硬件上的复现实验。它采用叙述性 review 与跨文献表格汇总来回答问题；检索式、纳入排除标准、study quality scoring、统一误差指标和统计分析均未报告。因此以下“问题 → 验证 → 答案”是文献证据综合，不是本文自有实验。

- **问题：接口能否捕获 controller 的 PWM 事件？→ 验证：** 汇总 interpolation/extrapolation 和 CPU/DSP、FPGA 实时实现，并比较采样/计算能力。**答案：** 低采样会漏掉 interstep switching event；FPGA 文献报告了超过 \(50\,MHz\) 的 I/O sampling 与低于 \(500\,ns\) 的计算时间，但这不等于在所有 converter 规模下都达到相同精度。[pdf:E02]（PDF 物理页 2，Fig. 3）[pdf:E03]（PDF 物理页 3，Section II-B）
- **问题：converter 模型怎样交换精度、资源与步长？→ 验证：** Table I 比较 system-level solver，Table II 比较 device-level IGBT model 的 calculation time、accuracy、complexity 和是否需要测试数据。**答案：** 预存拓扑受 memory 限制，在线求解受 arithmetic resource/latency 限制；详细 IGBT 更能表达瞬态，却通常需要更复杂计算或更小步长，简化模型则牺牲工作范围或精度。[pdf:E04]（PDF 物理页 4，Table I、Section III-A）[pdf:E05]（PDF 物理页 5，Table II）
- **问题：不同动力总成部件需要什么时间尺度？→ 验证：** Table V 汇总 CHIL cases，Fig. 8 将应用映射到典型时间步。**答案：** 作者总结 ESS 慢动态通常为 \(300\,\mu s\) 到 \(10\,ms\)，考虑至 \(1\,kHz\) transient 的 power system/machine 可能需 \(200\) 到 \(50\,\mu s\)，soft-switching transient 通常需小于 \(750\,ns\)，高功率 detailed IGBT 常在 \(500\,ns\) 到 \(1\,\mu s\)，而 WBG megahertz switching 被推断需要低于 \(100\,ns\) 的响应时间。[pdf:E08]（PDF 物理页 8，Fig. 8 及相邻正文）
- **问题：现有 EV CHIL 是否已采用最高保真模型？→ 验证：** 对 Table V 的案例做横向观察。**答案：** 作者指出接真实 controller 的 CHIL 更偏 system-level converter；FCEV 案例仍以 PEMFC ECM 为主，多物理 PEMFC 尚未进入所汇总的 CHIL 应用，device transient 与外部 controller 结合的 HIL 表现仍待评价。[pdf:E08]（PDF 物理页 8，Table V 前后正文）

这些结论只能外推为“所汇总文献中的工程范围”。由于硬件代际、模型规模、数值表示、误差定义与测试工况没有统一，不能把某篇文献的最小 time-step 直接当成另一系统的保证值。

## § 8 — Take-aways

**5 句话：**  
1. EV CHIL 的第一约束是 controller—DRTS 闭环 deadline，而不是模型离线精度。  
2. PWM interstep event 把采样分辨率直接变成准确性与稳定性问题。  
3. Converter、ESS 和 machine 跨越多个时间尺度，适合 multirate 与 CPU/FPGA hybrid mapping。  
4. 更细模型会把代价转化为计算、存储、solver stiffness、实验数据或 FPGA resource。  
5. 论文提供了有用的模型地图，但没有统一 benchmark，表中步长不能脱离具体平台和工况比较。

**3 句话：**  
1. 先用闭环时间预算约束模型，再决定 fidelity，而不是反过来。  
2. FPGA 适合高速采样和并行数据流，CPU 适合较慢且复杂的子模型。  
3. 综述最有价值的是揭示 trade-off，最缺的是可复现的跨平台等价比较。

**1 句话：**  
高可信 CHIL 是接口时序、模型保真度、数值稳定性与硬件资源的共同设计问题。

## § 9 — 最脆弱的假设

最脆弱的假设是：不同论文在不同电路规模、硬件代际、数值精度、solver、I/O 配置和 accuracy 定义下报告的 time-step 与 calculation time，仍足够可比，可以支持本文的模型选型图。

一旦这个假设不成立，Table I–V 和 Fig. 8 仍能作为文献目录，却不能证明某类模型或平台在公平条件下更优，也不能把“达到几十纳秒”外推为真实闭环中同时满足 I/O、稳定性和保真的能力。论文确实把 model type、solver、time-step、platform 与定性 accuracy/complexity 并列汇总，[pdf:E04]（PDF 物理页 4，Table I）[pdf:E05]（PDF 物理页 5，Table II）[pdf:E08]（PDF 物理页 8，Table V、Fig. 8）但未报告标准 workload、统一误差阈值、相同 word length、相同 circuit size 或独立重跑。因而，支持这个假设的是“跨文献趋势一致性”，缺少的是“同条件可复现实验”；这是失败代价最大的一点。

## § 10 — 最小复现实验

一周内最值得复现的不是整台 EV，而是“采样分辨率是否真的决定 PWM event reconstruction 误差”。

- **数据与对象：** 建一个 two-level inverter 驱动简化 PMSM 的固定模型，接一块真实 digital controller；同时保存一个离线极小步长参考轨迹。控制频率、负载阶跃和 dead time 由实验者固定并公开，这些是复现实验设定，不是论文报告值。
- **实现：** 在同一 DRTS 上实现三种接口：粗步长直接采样、粗步长加 interpolation/event compensation、高采样 FPGA event capture。converter 与 machine 方程、数值精度、I/O scaling 和 controller code 保持不变。
- **测量：** 记录 PWM edge-time error、相电流/转矩相对参考轨迹的误差、closed-loop delay、overrun 次数、稳定性，以及 FPGA clock、LUT/BRAM/DSP 使用量。
- **支持标准：** 若高采样或补偿在不增加闭环 overrun 的前提下，跨多个开关相位与负载工况稳定降低 event-time 和 state error，并满足论文的 \(T_{\mathrm{CHIL}}\le0.01T_{\mathrm{s\_control}}\) 预算，则支持“接口时序是关键瓶颈”。[pdf:E02]（PDF 物理页 2，Eqs. (1)–(2)、Fig. 3）
- **反驳标准：** 若控制结果主要由模型误差或 I/O latency 决定，提高采样或补偿后误差不降，或者所需 FPGA 资源使 deadline 失守，则反驳把高采样率视为最直接解决路径的泛化。

## § 11 — 最强反例设计

最强攻击不是找一个更复杂模型，而是做同条件 cross-platform counterexample：在 CPU/DSP 与 FPGA 上实现位宽、模型方程、开关数、I/O latency 和 error metric 全部等价的 converter—machine CHIL workload，再逐步增加异步 PWM edge 密度、耦合开关数、参数 stiffness、fault/unbalanced condition 和 WBG-level switching demand。

离线 device-level 仿真与示波器测量共同作为参考，比较的不是“能否跑完”，而是闭环误差、事件遗漏、numerical instability、deadline miss 和资源增长曲线。如果 FPGA 在论文强调的高事件密度下因 memory/DSP routing、I/O latency 或模型分区造成误差突增，而 CPU 加 event compensation 在相同闭环预算下反而更稳，那么“FPGA 高分辨率是最直接、最有效路径”的解释就存在替代原因：优势可能来自被比较文献采用了更简单模型、更小系统或不同精度，而不是硬件结构本身。[pdf:E03]（PDF 物理页 3，FPGA 与 converter solver 讨论）[pdf:E04]（PDF 物理页 4，Table I）

这个反例也会直接检验 §9 的可比性假设：若在统一 workload 后原有方法排序显著改变，综述的时间步地图只能用于发现候选方案，不能作为选型结论。

## § 12 — Follow-up Research Idea

**候选想法：建立“可校准的跨平台 CHIL model-selection benchmark”，不声称 novelty。** 本文没有做完整系统检索之外的相关工作核对，因此这里只提出可证伪方向。

论文原文把 model refinement、PHM fault injection 和 digital twin 列为长期展望，但这些方向仍共同受实时计算能力与模型复杂度 trade-off 约束。[pdf:E09]（PDF 物理页 9，Future Outlooks、Figs. 9–10）

**（a）未满足需求。** 现在的工程师看到的是不同论文的最小 time-step，却不知道在自己的 controller period、I/O latency、circuit size、word length 和允许误差下，哪种模型真正能闭环运行。本文也承认系统级 CHIL、multiphysical model 与 WBG 小步长之间仍有明显缺口。[pdf:E08]（PDF 物理页 8，Table V、Fig. 8）[pdf:E10]（PDF 物理页 10，Conclusion）

**（b）研究价值。** 电气、控制与电力电子领域的高影响工作通常要求可解释的工程指标、真实控制器闭环、跨工况验证和可实现硬件。这个 benchmark 不再按“模型类别”静态排表，而是学习或辨识一个带 uncertainty 的可行域：给定 workload 与 hardware constraints，输出 accuracy–latency–resource–stability 的 Pareto frontier，并允许新平台通过少量 calibration run 接入。

**（c）可借鉴方法。** 可借鉴计算机体系结构的 performance portability benchmark、real-time systems 的 schedulability analysis，以及 uncertainty quantification / surrogate modeling；物理模型仍由 EMT、converter 和 machine 领域约束，不能用纯数据拟合替代守恒和稳定性检查。

**（d）首个证伪实验。** 选择两个独立实验室、两种 FPGA/CPU 平台和三类公开 workload，在不共享拟合参数的情况下预测它们的 deadline miss、闭环误差和资源占用。如果校准后的可行域不能跨平台预测，或方法排名对轻微测试设置极端敏感，这个研究方向的核心主张即被证伪。

**（e）实质区别。** 与本文汇总“某文献用了什么模型、达到什么步长”不同，新问题是“如何从标准化、可复现的闭环任务预测一个未见平台上的可行模型边界”。它把综述中的定性 trade-off 变成可验证的决策模型，也能为论文展望的 multiphysics、PHM 与 digital twin 提供统一实时性验收，而不是只给这些方向再增加一个模型模块。[pdf:E09]（PDF 物理页 9，Future Outlooks、Figs. 9–10）[pdf:E10]（PDF 物理页 10，Fig. 11、Conclusion）
