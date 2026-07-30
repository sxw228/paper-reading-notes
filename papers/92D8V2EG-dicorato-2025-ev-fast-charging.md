# Integration of EV Fast Charging Station into a DC-Based Microgrid

- 作者：M. Dicorato, G. Forte, Francesca Marasciuolo, M. C. Cavarretta, D. De Michino
- 出处：IEEE Transactions on Industry Applications, Vol. 61, No. 4
- 年份：2025
- DOI：10.1109/TIA.2025.3544567
- Zotero key：92D8V2EG

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个很具体的工程矛盾：一座快充站的瞬时功率可能高于微电网与配电网连接点允许取得的功率，但车辆仍需在短停留时间内获得足够能量。作者问：能否在一个含 photovoltaic（PV）、battery energy storage system（BESS）、普通双向充电车辆和一台 fast charger 的 600 V DC 微电网内，通过 day-ahead mixed-integer linear programming（MILP）协调各资产，使 EV fast charging（EVFC）的接入既不过度增加外部电网功率交换，也不造成过高的运行成本？论文把真实电价、充电电缆损耗、PV 与 EVFC 不确定性以及经济/技术目标的权衡一起纳入调度。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）[pdf:E02]（PDF 物理页 2，Section II-A）

这个问题重要，是因为 fast/ultra-fast charging 的高功率和脉冲式需求会改变配电负荷曲线、提高变压器负载，并可能带来电压和谐波问题；smart charging、储能与 DC 集成是已有缓解路线，但能否在受限并网容量下真实地“拼出”快充所需功率，取决于资产状态、车辆可用性和调度目标。[pdf:E01]（PDF 物理页 1，Introduction）本文案例中 EV6 的充电功率上限为 75 kW，而从外部电网购电被限制在 45 kW；这使内部储能和 V2G 资源不再只是优化成本的可选项，而成为部分工况下满足快充功率的必要来源。[pdf:E05]（PDF 物理页 5，Fig. 2、Table I）[pdf:E06]（PDF 物理页 6，场景定义与 Fig. 4）

## § 2 — 前人工作与不足

论文梳理的 prior work 已分别覆盖了几类能力：fast charger 对电压、变压器负载和谐波的影响；smart charging 对电压与峰值负荷的缓解；BESS 配合快充站进行 peak shaving；PV、储能与 EV 的 DC 联接和成本优化；以及 EV/V2G 为微电网提供内部 reserve 或参与 energy community。也就是说，“用储能或 smart charging 缓解快充冲击”本身不是本文的新命题。[pdf:E01]（PDF 物理页 1，Introduction 及 refs. [4]–[22]）

最接近的前作是作者自己的文献 [23]，它已经在 DC microgrid 中实现了 optimal V2G operation。本文相对于 [23] 的推进不是另造一套调度框架，而是把额外 EVFC、真实购售电价格和充电线损放入同一个模型，再增加面向 PV/EVFC 预测误差的 chance-constrained reserve，以及经济目标 OF1 与外部电网交换目标 OF2 的加权组合。[pdf:E02]（PDF 物理页 2，作者列出的四项 advancement）[pdf:E11]（PDF 物理页 11，ref. [23]）

原有工作之所以不够，不是因为完全没有优化、储能或 V2G，而是这些能力没有在本文这个压力条件下被同时验证：EVFC 需求高于并网可用功率，电缆损耗随功率平方增长，终端 SOC 约束会改变可用灵活性，而不确定性又要求预留上/下调容量。本文因此更像是对既有 DC 微电网优化框架的一次“高功率快充压力测试与扩展”，而不是对充电站电力电子本体的重新设计。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，不是作者逐句陈述的研究日志。

第一步，已有文献已经说明 fast charging 的风险来自高峰值与集中出现的负荷，而 BESS、smart charging、V2G 和 DC coupling 各自能提供缓解。于是自然的问题不是再证明这些部件有用，而是把它们放在同一个受限 DC bus 上，看它们能否在时间上互补。[pdf:E01]（PDF 物理页 1，Introduction）

第二步，真实站点的 EVFC 功率高于并网取电限制，因此单靠电网供电会在某些时段不可行。作者保留前作的 day-ahead MILP 骨架，把“最低运行成本”和“最低外部电网交换”分成两个目标，使调度器能够显式展示经济性与局部自给之间的冲突。[pdf:E02]（PDF 物理页 2，Eq. (1)–(2) 与方法说明）

第三步，快充功率较高，电缆的 \(I^2R\) 损耗不能再无条件忽略；但损耗在定电压下含功率平方项，会破坏 MILP 的线性结构。作者因此用分段线性变量近似 \(P^2\)，继续使用 MILP 求解，同时用事后真实平方损耗检查近似误差。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Eq. (6)–(18)）[pdf:E08]（PDF 物理页 8，Table VIII）

第四步，确定性日程仍可能被 PV 误差或 EVFC 到站 SOC 误差打破，所以作者用 chance constraints 要求 BESS 与 V2G EV 预留双向功率和能量裕量；最后再通过多目标权重 \(\beta\) 扫描，寻找成本与外网交换之间的折中。[pdf:E04]（PDF 物理页 4，Eq. (26)–(31)）

## § 4 — 核心 Intuition

核心 intuition 是：不要让受限的配电网连接点单独追随快充脉冲，而要让 PV、BESS 和暂时可用的 V2G 车辆在 DC bus 内部先完成能量搬移与功率拼接。MILP 决定“何时从谁取能、何时回充、允许留下多少终端 SOC”，而分段线性损耗和 reserve 约束分别防止调度器把电缆损耗与预测误差当作不存在。[pdf:E02]（PDF 物理页 2，Section II-A）[pdf:E04]（PDF 物理页 4，Section II-C/D）

## § 5 — 具体方法与完整 Pipeline

以论文的 EV6 快充为例，完整 pipeline 如下。

1. **输入系统和时间序列。** 模型接收 24 h 内的 PV 预测、购售电价格、车辆 plug-in/行程能量需求、初始与目标 SOC、设备功率/能量边界、转换效率和充电电缆参数。物理案例含 20 kW PV、25 kW/90 kWh Sodium-Nickel BESS、5 台 15 kW 双向普通 EV 充电器，以及一台最大 75 kW 的 EVFC；EV6 的单日行程能量需求合计为 102.11 kWh。[pdf:E05]（PDF 物理页 5，Fig. 2、Table I、Fig. 3 及正文）
2. **选择目标。** OF1 最小化购售电、BESS/EV 电池磨损、EV charging cost 与 V2G revenue 合成的 daily operating cost；OF2 最小化全天进口与出口能量之和。二者也可按归一化权重 \(\beta\) 组合为 OFcomb。[pdf:E02]（PDF 物理页 2，Eq. (1)–(2)）[pdf:E05]（PDF 物理页 5，Eq. (31)）
3. **建立功率与 SOC 约束。** 每个时间步在 DC bus 上平衡 grid、PV、BESS 和所有 EV 的功率，并施加设备功率、能量、方向和 SOC 更新约束。普通 EV 可充可放；EVFC 只允许 smart charging，不允许 V2G discharge。[pdf:E02]（PDF 物理页 2，Eq. (3)–(5)）
4. **把线损变成 MILP 可处理的形式。** 在定 DC 电压下，电缆损耗含 \(R_jP^2/V^2\)。作者按功率区间引入 binary 变量 \(\lambda_{m,j}\) 和 continuous 变量 \(\delta_{m,j}\)，用分段线性函数近似每个充/放电功率的平方，再把近似量代回 bus balance。[pdf:E03]（PDF 物理页 3，Fig. 1、Eq. (6)–(18)）
5. **求解三个 SOC 场景。** S1 把 BESS/EV 初末 SOC 均设为 90%，S2 均设为 28%，S3 则把 BESS 初始 SOC 设为 51%、EV 初始 SOC 设为 45%，但不约束最终 SOC。每个场景分别测试高/低 PV 和 OF1/OF2。[pdf:E06]（PDF 物理页 6，场景定义）
6. **可选的不确定性与多目标扩展。** chance-constrained 版本让 BESS 与 V2G EV 为 PV 输出误差和 EVFC 到站 SOC 误差提供上/下 reserve；multi-objective 版本扫描 \(\beta\in[0,1]\)，输出成本、外网交换和电池循环之间的 Pareto-like 权衡。[pdf:E04]（PDF 物理页 4，Eq. (26)–(31)）
7. **输出和校验。** 输出包括各资产功率日程、daily operating cost、进/出电网能量、线损、BESS/EV 等效放电循环和 reserve 分担；线性化线损再用原始平方功率回算，以量化近似偏差。[pdf:E04]（PDF 物理页 4，Eq. (19)–(25)）[pdf:E08]（PDF 物理页 8，Table VI–IX）

这不是开关级 EMT 仿真。论文没有报告 converter switching model、开关事件处理、数值积分器、multi-rate time stepping 或 EMT 仿真步长；\(\Delta t\) 只作为 day-ahead 调度时间间隔进入公式，本文未在系统参数部分给出其明确数值。模型是集中式 MILP，论文也未报告并行计算依赖、求解器运行时间、worst-case execution time 或实时 deadline。数值表示默认为优化变量的连续/整数表示；fixed-point、FPGA 映射、资源占用、时钟频率、HIL/实时仿真平台均未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有明确形式化数学，但关键不是复杂定理，而是把物理损耗和管理目标写成 MILP。

首先，技术目标把全天从外部电网进口和向外输出的能量都视为需要压低的交换量：

\[
OF2=\Delta t\sum_t\left(P_g^{in}(t)+P_g^{out}(t)\right).
\]

它不会区分“卖电有收益”还是“买电有成本”，所以与 OF1 的经济目标会产生结构性冲突。[pdf:E02]（PDF 物理页 2，Eq. (1)–(2)）

其次，定 DC bus 电压 \(V\) 时，第 \(j\) 条充电电缆的电阻与损耗核心分别是

\[
R_j=\rho_j\frac{2l_j}{S_j},\qquad
P_{\mathrm{loss},j}\propto \frac{R_j}{V^2}P_j^2 .
\]

其中 \(\rho_j,l_j,S_j\) 是电阻率、单程长度和截面积，系数 2 表示 DC 回路的两根导体。平方项意味着高功率快充会非线性放大损耗，也使原始 bus-balance constraint 不再是线性的。[pdf:E02]（PDF 物理页 2，Eq. (3)–(4)）

为保留 MILP，作者把 \(y_{EV,j}^c=(P_{EV,j}^c)^2\) 换成分段线性近似。对已激活区间，近似值写成

\[
y_{EV,j}^c(t)=\left[P_{EV,j}^{c,\min}(t)\right]^2+
\sum_m\left(P_m^2-P_{m-1}^2\right)\delta_{m,j}^c(t),
\]

并用一组单调 binary/continuous 辅助变量保证只有依次连接的线段被选中；放电功率采用对称构造，再以 \(y^c,y^d\) 替代 bus balance 中的平方项。[pdf:E03]（PDF 物理页 3，Fig. 1、Eq. (6)–(18)）工程上这相当于用折线弦逼近凸函数 \(P^2\)。论文的事后回算显示该近似在所测场景中始终高估而不是低估真实线损，因此给出的日程在损耗上偏保守，但这只是对所测区间的经验验证，不是全局误差定理。[pdf:E08]（PDF 物理页 8，Table VIII 及正文）

chance-constrained 扩展把 PV 和 EVFC 到站 SOC 的误差分位数变成 reserve 下界。上调方向的核心形式为

\[
\sum_{j\ne EVFC}R_{EV,j}^{+}(t)+R_B^{+}(t)
\ge q_{1-\alpha^+}^{PV,+}(t)
+\frac{q_{1-\alpha^+}^{S,j,+}(t)}{n_{\varepsilon,S,j}\Delta t}\Big|_{j=EVFC},
\]

随后再用 BESS/EV 的剩余能量和功率 headroom 限制可承诺的 reserve；下调方向采用对应约束。[pdf:E04]（PDF 物理页 4，Eq. (26)–(30)）

最后，多目标函数为

\[
OF^{comb}=\beta\frac{OF1}{C_{ref}}+(1-\beta)\frac{OF2}{E_{g,ref}},
\]

归一化避免“欧元”和“kWh”的量纲直接决定权重。这里的 \(\beta\) 仍是管理者主观选择，模型本身不会给出唯一正确的折中点。[pdf:E05]（PDF 物理页 5，Eq. (31)）

## § 7 — 实验设计与结论

论文做的是基于现实规模设施参数的 scenario optimization，不是实机控制实验。验证逻辑可以按“问题 → 实验 → 答案”概括。

1. **受限并网功率下，内部资产能否承担快充脉冲？** 作者在高/低 PV、S1/S2/S3 和 OF1/OF2 的组合上求解 24 h 日程，并把购电/售电上限设为 45/35 kW。结果显示 BESS 和普通 EV 会在 EV6 充电时放电或 V2V 供能；高 PV 的 OF2-S3 中，EV6 需求峰值可接近 80 kW（含效率和线损），但外部电网交换仍被日内内部资源抵消。[pdf:E06]（PDF 物理页 6，Fig. 4 及正文）
2. **“零外网交换”是否可能？** 在不约束最终 SOC 的 S3 中，OF2 在高、低 PV 两种情形都得到 \(E_g^{in}=E_g^{out}=0\)。这回答了单日调度上的“可能”，但不能外推为长期能量自给，因为 S3 允许日末储能低于日初状态。[pdf:E07]（PDF 物理页 7，S3 说明）[pdf:E08]（PDF 物理页 8，Table VI）
3. **经济目标对 SOC 条件有多敏感？** 高 PV 下，OF1 的 daily operating cost 从 S1 的 65.16 € 降到 S3 的 32.68 €，约减半；低 PV 下对应为 77.44 € 与 37.59 €。主要差别同时包含“终端 SOC 是否必须恢复”，所以这些数字不能解释成算法本身带来的纯收益。[pdf:E07]（PDF 物理页 7，Table V）
4. **线损近似是否足够准确？** 各场景线性化损耗与真实平方损耗的 mismatch 平均约 6%，但作者报告它只占总能量平衡的 0.006%，而且近似始终高估损耗。EVFC 占全部充电线损的 20%–60%，但全部 EV 充电电缆损耗仍低于微电网总能量平衡的 0.1%。[pdf:E08]（PDF 物理页 8，Table VII–VIII 及正文）
5. **为不确定性留 reserve 的代价多大？** 在 OF1-S3、高 PV 测试中，取 \(\alpha^+=\alpha^-=5\%\) 参数的 chance-constrained 版本把 DOC 从 32.68 € 增至 33.08 €，进口能量从 0 增至 0.99 kWh，出口从 54.44 增至 55.62 kWh，平均 EV 放电循环指标从 0.11 增至 0.15。作者据此报告成本增加约 1.2%、出口增加约 2.2%。[pdf:E09]（PDF 物理页 9，Table XI 及正文）
6. **经济与技术目标是否存在可用折中？** \(\beta\) 扫描显示，\(\beta=0.8\) 相对纯 OF1 的 DOC 偏差为 3.3%、总外网交换偏差为 6%；该点 BESS 等效放电循环为 0.29，并主要用其他 5 台 EV 的 V2V 支撑 EVFC。作者据此认为适当加权可避免过度使用储能，同时保留较好的成本与交换表现。[pdf:E09]（PDF 物理页 9，multi-objective 正文）[pdf:E10]（PDF 物理页 10，Fig. 10 与 Conclusion）

这些结论的有效范围是单个 DC microgrid 的优化算例。论文未报告与其他 optimizer 的 baseline 比较、MILP 求解时间、现场闭环运行、通信延迟、converter dynamics、EMT 精度、实时仿真或 FPGA/HIL 实验，因此不能从本论文推出控制器满足实时性、动态稳定性或硬件资源约束。

## § 8 — Take-aways

**5 句话。**  
第一，论文证明的是“通过日前调度协调内部灵活性，可以在受限并网接口下安排 75 kW 级 EVFC”，不是提出新的快充变换器。第二，真正改变结果的是 BESS/V2G 可用性和终端 SOC 条件；S3 的零外网交换建立在日末 SOC 可自由下降的前提上。[pdf:E06]（PDF 物理页 6，场景定义）[pdf:E08]（PDF 物理页 8，Table VI）第三，把 \(I^2R\) 线损显式放入 MILP 是必要的工程修正，分段线性化在所测场景中表现为小幅、保守的误差。[pdf:E08]（PDF 物理页 8，Table VIII）第四，chance-constrained reserve 能以约 1.2% 的日成本增量覆盖论文设定的 PV/EVFC 误差场景。[pdf:E09]（PDF 物理页 9，Table XI）第五，多目标权重能展示成本、外网交换与电池循环的冲突，但不能替代管理者对 SOC 债务和车辆参与意愿的约束。

**3 句话。**  
这是一套把 EVFC、V2G、BESS、PV、真实电价和电缆损耗统一进 day-ahead MILP 的调度方法。它的最好结果来自内部资产在时间上的能量搬移，而不是额外扩大并网容量。最需要警惕的是把“单日无外网交换”误读为“可持续自给”，因为最优场景放松了最终 SOC。

**1 句话。**  
论文说明 DC 微电网可以用储能与车辆灵活性吸收快充功率冲击，但收益大小主要由终端 SOC 与可用灵活性假设决定，而非由 MILP 本身保证。

## § 9 — 最脆弱的假设

最脆弱的假设是：在 EVFC 需要高功率时，BESS 和普通 EV 的可放电能量真实可用，而且调度器可以把这部分能量“借到日末”而不必在同一日恢复。该假设一旦不成立，论文最醒目的结果——OF2-S3 在高、低 PV 下都实现零外网交换——会直接失效。

论文给出的支持是：Fig. 4–5 的优化日程确实能让 BESS/V2G 在 EV6 到站时供能，chance-constrained 版本也为 PV 与 EVFC 到站 SOC 误差预留了 reserve。[pdf:E06]（PDF 物理页 6，Fig. 4）[pdf:E07]（PDF 物理页 7，Fig. 5）[pdf:E09]（PDF 物理页 9，Fig. 8–9）但缺失的证据更关键：没有用户拒绝 V2G、提前离站、通信失败、连续多日能量恢复、动态电池 degradation 或 reserve 分布失配的测试。S3 明确取消 final SOC constraint，所以零交换更准确地说是“在给定初始电量可以被消耗的单日窗口内可行”，而不是可循环重复的稳态运营结论。[pdf:E06]（PDF 物理页 6，S3 定义）这是基于证据的批评，不是作者显式承认的结论。

## § 10 — 最小复现实验

一周内最有价值的不是复刻全部 31 组方程，而是验证“零外网交换是否只是终端 SOC 松弛带来的能量借款”。

- **数据。** 从 PDF 录入 Fig. 2、Table I–IV 的设备参数：20 kW PV、25 kW/90 kWh BESS、5 台 15 kW 双向 EV 充电器、75 kW EVFC、45/35 kW 并网交换限制，以及 S3 初始 SOC。用论文报告的高/低 PV 总能量和 EV6 的 102.11 kWh 日需求构造可复核的 24 h profile；普通 EV 的完整参数若要逐点复现需继续取得 ref. [23]，因为本文未重复给全。[pdf:E05]（PDF 物理页 5，Fig. 2、Table I–IV）
- **实现。** 用 Pyomo、JuMP 或 PuLP 建一个最小 MILP，只保留 grid、PV、BESS、5 个可聚合的 V2G EV、EVFC、SOC 更新和分段线损。求解两组：A 为论文 S3，不约束 final SOC；B 增加 cyclic terminal constraint，使 BESS/EV 日末 SOC 等于日初。
- **测量。** 比较两组的 \(E_g^{in}+E_g^{out}\)、未满足 EVFC 能量、日末能量债务、DOC 和线损回算误差。
- **支持条件。** 若 A 能得到接近 Table VI 的零交换，而 B 需要显著外网能量或变为 infeasible，则支持本文算例、同时证实其零交换依赖终端 SOC 松弛。
- **反驳条件。** 若 A 在合理重建参数下也无法满足 EVFC 需求，或线性化误差改变可行性，说明公开论文参数不足以支持该核心算例；若 B 仍能连续日循环零交换，则第 9 节的批评被削弱。

这个实验不验证 EMT 稳定性或 FPGA 实时性，因为论文没有提供相应模型或硬件基线。

## § 11 — 最强反例设计

最强反例是把论文的单日 S3 扩展成连续 7 天，并禁止“免费重置”储能状态：每天保留相同 EVFC 服务需求，采用低 PV，要求第 7 天末 BESS/EV 聚合 SOC 回到第 1 天初，同时让 V2G 可用车辆在快充高峰时随机退出，并把 PV 低估与 EVFC 到站低 SOC 设为相关事件。并网购电仍限制为 45 kW，EVFC 未供能量不得被悄悄丢弃。

这个反例直接挑战机制而不是只调一个参数。如果模型频繁 infeasible，或必须显著增加外网交换才能还清能量债务，就说明“内部资源可缓解 EVFC 对配电网影响”只在有可消耗初始能量和可靠 V2G 参与时成立。chance constraint 只能覆盖作者选定分布和分位数下的 reserve，并不能自动处理长期能量恢复与相关极端事件。[pdf:E04]（PDF 物理页 4，Eq. (26)–(30)）[pdf:E09]（PDF 物理页 9，stochastic 结果）

另一种结果也有信息量：若在上述约束下仍能稳定满足服务并回到初始 SOC，且外网交换保持很低，那么本文机制会获得比原论文单日算例更强的支持。

## § 12 — Follow-up Research Idea

在 power systems、power electronics 和 transportation electrification 领域，高影响工作通常不只要求目标函数更优，还要求物理约束可信、在不确定性下可实现，并通过硬件、现场或至少高保真动态模型证明工程可执行性。本文发表在 IEEE Transactions on Industry Applications，已给出现实规模参数和多场景 MILP，但未给连续多日、闭环在线或 converter-level 动态证据。

**候选方向：从“单日最小外网交换”改写为“可偿还灵活性能量债务的多日可靠快充”。** 需求来自第 9 节：S3 可以消耗初始 SOC，却没有定量回答这些能量何时、以何种电网代价和用户代价恢复。新问题不再追求某一天的零交换，而是要求在滚动时域内，每一笔来自 BESS/V2G 的临时供能都有明确偿还期限、用户参与概率和 feeder risk budget。

可借鉴相邻领域的 distributionally robust model predictive control、inventory/energy debt accounting、chance-constrained service contracts 与 battery health-aware dispatch。第一项可证伪实验是：在 7–30 天真实 PV、车辆到离站和快充需求轨迹上，与本文单日 MILP 比较；同时施加 cyclic SOC、V2G dropout 和相关预测误差。如果新方法不能在相同 EVFC service level 下减少 95%/99% 分位的 feeder overload 或 unmet energy，或者成本/电池损耗显著恶化，这个方向就应被否定。

它与作者提出的“聚合多个 DC microgrids 进入 renewable energy community”不同：作者扩展的是系统空间范围，[pdf:E10]（PDF 物理页 10，Future works）这里改变的是成功标准——从单日调度表看起来局部自给，转为多日能量守恒、风险闭合和参与约束下仍可恢复。相关工作尚未做系统检索，因此这只是证据约束的候选研究想法，不声称 novelty；FPGA 与实时仿真也不是本方向已有证据，而应在后续若进入快速闭环控制时另行建立。
