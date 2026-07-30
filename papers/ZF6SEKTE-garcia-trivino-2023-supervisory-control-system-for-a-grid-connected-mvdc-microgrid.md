# Supervisory Control System for a Grid-Connected MVDC Microgrid Based on Z-Source Converters With PV, Battery Storage, Green Hydrogen System and Charging Station of Electric Vehicles

- 作者：Pablo García-Triviño；Laís de Oliveira-Assís；Emanuel P. P. Soares-Ramos；Raúl Sarrias-Mena；Carlos Andrés García-Vázquez；Luis M. Fernández-Ramírez
- 出处：IEEE Transactions on Industry Applications，59(2)，2650–2659
- 年份：2023
- DOI：10.1109/TIA.2022.3233556
- Zotero key：ZF6SEKTE
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个同时包含 PV、铅酸电池、制氢/储氢/燃料电池系统、双路 EV 快充和公共电网接口的 MVDC 微电网：怎样用较少的功率变换级把不同电压等级的设备接到同一直流母线，并由 supervisory control system（SCS）在功率不平衡、储能边界和电价之间作实时调度。作者把目标分成两层：底层必须始终维持功率平衡；上层希望在允许的储能状态内利用电网买卖电获得经济收益。论文把 Z-source converter（ZSC）的单级 buck–boost 与 shoot-through 能力作为硬件结构基础，并把计及电价的 fuzzy SCS 作为控制层贡献。[pdf:E01]（PDF 物理页 p001，Abstract 与 Section I）

这个问题的重要性不只是“给 EV 充电”。PV 功率与充电需求天然不同步，电池适合快速功率缓冲，氢系统适合承接更大能量范围，电网则是最后的功率平衡端；若三者分别独立控制，系统很容易在局部看来合理、整体却出现储能越界或昂贵的电网交换。论文因此尝试把变换器拓扑、异构储能的统一能量状态和调度逻辑放进一条控制链。作者报告的工程规模是约 1800 V MVDC 母线、186 kW 峰值 PV、两台 50 kW 快充单元、36.9 kW 电池调度功率、77 kW fuel cell 和 144 kW electrolyzer 调度功率。[pdf:E03]（PDF 物理页 p003，Fig. 1 与 Section II）

## § 2 — 前人工作与不足

论文对 prior work 的归纳不是“以前没人做能量管理”，而是指出已有方案通常只覆盖问题的一部分。基于 model predictive control、PI、droop 或 rule-based 的充电站 SCS 已能削峰、稳定 DC bus、安排 ESS 充放电或满足 grid ramp-rate；也有工作把电网能量成本纳入决策。但作者指出，若研究采用很长采样周期或多年能量仿真，功率峰值和快速动态会被抹去；若只看数秒到数十秒动态，又难以说明经济性；只配置单一 ESS 时，也没有处理电池与氢系统之间的能量分配。典型结构还为各能源端配置传统 buck/boost DC/DC，再由 VSI 接网，变换级较多。[pdf:E02]（PDF 物理页 p002，Section I related work）

本文相对于这些工作的定位有三点。第一，用 qZSI 的阻抗网络同时形成 MVDC 接点并接入电池，PV 位于 DC 侧、电网位于 AC 侧，从而避免为电池再加一个独立 DC/DC。第二，用一个氢系统 ZSC 和两个快充 ZSC 接入其余端口。第三，SCS 同时使用净功率、统一的 State of Energy（SOE）和电网价格，并专门处理“低 SOE 仍有负荷”和“高 SOE 仍有功率富余”两类极端状态。[pdf:E02]（PDF 物理页 p002，本文贡献）；[pdf:E04]（PDF 物理页 p004，Section III）

需要收紧作者的 novelty 表述：论文证明了一个特定配置和控制组合可工作，但没有逐项给出相对于传统结构减少了多少器件、损耗、成本或故障点；因此“减少变换器”是有结构图支撑的作者主张，不是已完成器件级或寿命周期量化的结论。

## § 3 — 重建作者的思考路径

可以从论文列出的既有事实重建这条思路。第一步，EV 快充负荷和 PV 出力不匹配，所以至少需要 ESS 或电网补偿净功率。第二步，单一 ESS 很难同时兼顾快功率响应和较长能量搬移，于是引入电池与氢系统，但这又产生了“当前功率该分给谁”的新问题。第三步，传统多级变换器虽然能把各端口接到 DC bus，却付出更多变换级；ZSC 的单级升降压和 shoot-through 能力提供了减少接口级数的路径。[pdf:E01]（PDF 物理页 p001，Section I）；[pdf:E02]（PDF 物理页 p002，prior configurations）

接着需要一个能把两种储能放在同一尺度比较的量。直接比较电池 SOC 与氢罐百分比没有能量意义，因此作者把两者可放出的电能折算后合成为 SOE。再往前一步，如果调度只追踪 \(P_{net}\)，电网就只会被动补峰；加入 \(C_{grid}\) 后，可以有意改变交给 dispatch 的 \(P_{net,f}\)，在价格有利时买入或卖出。最后，普通状态用连续比例分配，接近储能边界时用 fuzzy 输出 \(S\) 反转调度方向，这就形成了“统一能量状态—价格修正—储能分配—底层功率环”的完整路径。[pdf:E04]（PDF 物理页 p004，Eq. (5)、Fig. 2 与 Section III.A）；[pdf:E05]（PDF 物理页 p005，Fig. 3、Table I 与 Section III.B）

这是基于论文证据的合理重建，不是作者明确记录的研发过程。

## § 4 — 核心 Intuition

核心 intuition 是：先把电池和氢罐当前还能提供或吸收的能量折算到同一尺度，再按这个尺度分配净功率；同时让电价只修改调度目标，而不直接接管底层变换器控制。普通状态下，价格输出 \(K\) 对净功率做幅值修正；储能接近上下边界时，输出 \(S\) 可以改变 \(P_{net,f}\) 的符号，让系统即使面对小幅功率需求也能补储能，或面对小幅功率富余也能主动释放储能。[pdf:E04]（PDF 物理页 p004，Fig. 2、Eq. (6) 与相邻正文）

物理上，ZSC 负责“能否在同一 MVDC 母线上调节这些端口”，SCS 负责“此刻由哪个端口吸收或发出多少功率”。这两层分工是本文真正可迁移的思想。

## § 5 — 具体方法与完整 Pipeline

以“PV 出力不足、两辆 EV 充电、电价允许售电且储能不在极端区”为例，pipeline 如下。

1. PV 端独立执行 MPPT；SCS 读取 EV 负荷与 PV 功率，计算 \(P_{net}=P_{EV}-P_{PV}\)。正值表示 BAT、氢系统或电网需要供能，负值表示它们需要吸收富余功率。[pdf:E04]（PDF 物理页 p004，Section III 与 Fig. 2）
2. 用电池 SOC、氢罐水平 \(L_{H2}\)、两种储能容量和 FC/LZ 效率计算可放/可充能量，再合成为 SOE。论文给出的边界为电池 SOC 30%–95%、氢罐 0%–100%。[pdf:E03]（PDF 物理页 p003，Eqs. (1)–(4) 与参数段）；[pdf:E04]（PDF 物理页 p004，Eq. (5)）
3. Mamdani fuzzy block 以 \(P_{net}\)、SOE、\(C_{grid}\) 为输入，用 27 条规则产生 \(K\) 和 \(S\)。普通状态由 \(K\) 令 \(P_{net,f}=P_{net}(1+K)\)；极端状态由 \(S\) 令 \(P_{net,f}=S|P_{net}|\)。该 block 每 10 s 更新一次并保持输出。[pdf:E04]（PDF 物理页 p004，Eq. (6)）；[pdf:E05]（PDF 物理页 p005，Fig. 3、Table I、Eq. (7) 与更新周期）
4. dispatch 按电池和氢系统的可用能量比例计算各自分配系数，再依次施加额定功率上/下限，得到 \(P_{BAT}\) 与 \(P_{H2}\)。作者特别强调 Eqs. (8)–(11) 或 Eqs. (12)–(15) 必须按顺序执行；剩余功率由 \(P_{grid}=P_{net}-P_{H2}-P_{BAT}\) 闭合。[pdf:E05]（PDF 物理页 p005，Eqs. (8)–(15)）；[pdf:E06]（PDF 物理页 p006，Eq. (16)）
5. 底层控制把功率参考映射到变换器动作：qZSI 的 shoot-through duty \(D_{st}\) 调节 BAT 功率；氢系统 ZSC duty 调节 FC/LZ 功率；qZSI modulation index \(M\) 及 dq 电流 PI 环控制 PV 有功与单位功率因数；EV ZSC duty 实现先 constant-current、后 constant-voltage 的快充过程。[pdf:E04]（PDF 物理页 p004，Fig. 2）；[pdf:E06]（PDF 物理页 p006，Section III.C、Eqs. (17)–(18)）

模型层面，论文采用 single-diode PV、Simscape Electrical 电池模型、含 activation/concentration/ohmic voltage drop 的 FC 等效电路、DC source 加串联电阻的 electrolyzer，以及理想气体氢罐模型。[pdf:E03]（PDF 物理页 p003，Section II）事件处理只明确报告了 EV 的 CCM→CVM 切换、充电电流低于设定值 5% 并持续 5 min 后结束，以及 fuzzy block 的 10 s 采样保持。功率电子开关的离散化方式、仿真求解步长、多速率同步机制、定点/浮点数值格式、任务并行性、资源占用和 FPGA 映射均未报告。执行平台仅报告 OPAL-RT OP4510 实时 plant emulator 与 dSPACE MicroLabBox 上的 SCS，不应把这项 HIL 验证外推成 FPGA 实现。[pdf:E08]（PDF 物理页 p008，Section IV.E）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有定理式推导，核心是能量记账、分段调度和控制映射。

首先把两类 ESS 的百分比状态变成电能。电池可放与可充能量分别为

\[
E^{dis}_{BAT}=E^{nom}_{BAT}(SOC-SOC_{min}),\qquad
E^{char}_{BAT}=E^{nom}_{BAT}(SOC_{max}-SOC).
\]

氢系统对应为

\[
E^{dis}_{H2}=L_{H2}Q_{tank}LCV_{H2}\eta_{FC},\qquad
E^{char}_{H2}=(100-L_{H2})Q_{tank}LCV_{H2}/\eta_{LZ}.
\]

前两式表达“离下限还有多少可放电能”和“离上限还有多少可充电能”；后两式把氢库存经 lower calorific value 与 FC/LZ 效率换算成电能。[pdf:E03]（PDF 物理页 p003，Eqs. (1)–(4) 与变量定义）

统一状态为

\[
SOE=
\frac{E^{dis}_{H2}+E^{dis}_{BAT}}
{Q_{tank}LCV_{H2}\eta_{FC}+E^{nom}_{BAT}}.
\]

它不是新的物理状态，而是“当前总可放电能/最大总可放电能”的归一化指标。[pdf:E04]（PDF 物理页 p004，Eq. (5)）

fuzzy 层只改变调度目标：

\[
P_{net,f}=S|P_{net}| \quad\text{或}\quad
P_{net,f}=P_{net}(1+K).
\]

\(S\) 用于极端 SOE 状态并可改变方向，\(K\) 用于普通状态下根据电价放大、缩小 \(P_{net}\)。[pdf:E04]（PDF 物理页 p004，Eq. (6)）；[pdf:E05]（PDF 物理页 p005，Eq. (7)）

放电时，作者先取

\[
K^{dis}_{BAT}=\frac{E^{dis}_{BAT}}{E^{dis}_{BAT}+E^{dis}_{H2}},
\qquad K^{dis}_{H2}=1-K^{dis}_{BAT},
\]

再按额定功率限制依次求 \(P_{BAT}\) 与 \(P_{H2}\)。充电分支采用同形的 \(K^{char}\) 和功率限幅，最后由 Eq. (16) 把剩余差额交给电网。[pdf:E05]（PDF 物理页 p005，Eqs. (8)–(15)）；[pdf:E06]（PDF 物理页 p006，Eq. (16)）

这里存在必须忠实保留的公式歧义。Section III.B 的文字说充电分配考虑 \(E^{char}_{BAT}\) 与 \(E^{char}_{H2}\)，但 Eq. (12) 的分母实际印成 \(E^{dis}_{BAT}+E^{dis}_{H2}\)；Eqs. (14)–(15) 又写 \(P_{net}\)，而不是该节声明的输入 \(P_{net,f}\)。[pdf:E05]（PDF 物理页 p005，Eq. (12)、Eqs. (14)–(15) 与相邻正文）基于证据的判断是：复现者不能自行“修正”后再声称完全按原文实现，必须分别测试 literal 版本和语义一致版本。

底层 qZSI 使用

\[
D_{st}=\Delta D+D_0,\qquad
D_0=\frac{V^{nom}_{BAT}}{2V^{nom}_{BAT}+V^{MPPT}_{PV}},
\]

其中 \(\Delta D\) 来自 BAT PI loop，\(D_0\) 提供随工作点变化的前馈基值。[pdf:E06]（PDF 物理页 p006，Eqs. (17)–(18)）

## § 7 — 实验设计与结论

**问题 1：完整系统在动态日照和 EV 接入下能否维持功率平衡？** 作者做了 1200 s simulation，电价每 10 s 变化，三辆 EV 先后接入两个 50 kW 快充单元，并将 F-SCS 与不使用 \(C_{grid}\) 的 Ref-SCS 对比。[pdf:E06]（PDF 物理页 p006，Fig. 4 与 Section IV.A）结果中 PV 与 EV 的差额由 BAT、氢系统和电网分担，主要电压、SOC、氢罐水平、SOE、\(M\) 与 \(D_{st}\) 保持在作者设定范围；这支持“在该仿真工况下闭合功率与状态”的 claim。[pdf:E07]（PDF 物理页 p007，Figs. 5–7）

**问题 2：SOE 接近边界时，SCS 能否主动逆转能量方向？** 作者分别构造约 40 s 的低 SOE/\(P_{net}>0\) 和高 SOE/\(P_{net}<0\) 工况。低 SOE 案例中，\(S\) 在 20 s 激活，使 \(P_{net,f}\) 从正变负并让 SOE 回升；高 SOE 案例中，\(S\) 在 10–30 s 激活，使 \(P_{net,f}\) 为正并让 SOE 下降。[pdf:E07]（PDF 物理页 p007，Section IV.B）；[pdf:E08]（PDF 物理页 p008，Figs. 8–9 与 Section IV.C）答案是：在规则表覆盖的“小幅”功率失衡和既定储能模型中可以。

**问题 3：计及电价是否比 Ref-SCS 更“经济”？** Table II 按“售电收入减购电支出”计算该工况收益，报告 F-SCS 为 166.10 €、Ref-SCS 为 -6.65 €；代价是 F-SCS 的 SOC、氢罐水平与 SOE 整体更低，例如 \(SOE_{min}\) 为 15.4% 对 21.6%。[pdf:E08]（PDF 物理页 p008，Table II 与 Section IV.D）答案只对该价格轨迹和这一定义成立，不能外推为包含储能退化、设备成本与效率损失的净利润。

**问题 4：控制器能否在实时 HIL 中运行？** plant 与 control 在 OPAL-RT OP4510 中实时执行，SCS 部署于 dSPACE MicroLabBox，Yokogawa DLM4038 捕获前 500 s 的主要功率与电压波形。作者观察到 HIL 波形与 simulation 趋势一致，电压受控且 SOE、\(M\)、\(D_{st}\) 位于适当范围。[pdf:E08]（PDF 物理页 p008，Fig. 10 前的 HIL setup）；[pdf:E09]（PDF 物理页 p009，Figs. 10–11 与 Section V）这验证了 controller-in-the-loop 的实时可执行性，但不是完整功率硬件实验，也没有报告实时步长、deadline miss、CPU load、量化误差、故障注入或统计重复。

## § 8 — Take-aways

**5 句话：**  
1. 论文把 qZSI/ZSC 的多端口 MVDC 结构与计及电价的 fuzzy supervisory control 合并成一套 PV–BAT–hydrogen–EV charging station 方案。[pdf:E03]  
2. SOE 把电池和氢罐的可放电能归一化，为异构储能的比例调度提供共同尺度。[pdf:E04]  
3. \(K\) 负责普通状态的经济性修正，\(S\) 负责接近储能边界时改变能量方向。[pdf:E04][pdf:E05]  
4. simulation、两个极端工况和 HIL 波形共同支持“该模型与该工况下可维持功率平衡并实时运行”。[pdf:E07][pdf:E08][pdf:E09]  
5. 166.10 € 的报告收益只是 grid cashflow，不足以单独证明真实生命周期利润。[pdf:E08]

**3 句话：**  
结构创新在于用 impedance network 兼作 MVDC 接点并减少独立接口，控制创新在于把 SOE、电价和净功率合成两层调度。[pdf:E02][pdf:E04] 证据表明该方案在 1200 s simulation、两个 40 s 边界案例和 dSPACE/OPAL-RT HIL 中按预期动作。[pdf:E06][pdf:E08][pdf:E09] 最大未闭合项是经济指标过窄、公式存在充电分支歧义，而且没有 converter-count、损耗、实时资源或物理硬件的定量对比。

**1 句话：**  
这是一篇“拓扑减级 + 异构储能统一调度 + 实时 HIL”组合型工程论文，但它证明的是特定模型与价格轨迹下的可行性，不是普适最优性。

## § 9 — 最脆弱的假设

最脆弱的假设是：**“售电收入减购电支出”足以代表 F-SCS 的经济收益，而且为了售电而加深 BAT/H₂ 循环不会产生足以抵消该收益的成本。** 这直接支撑 F-SCS 相对 Ref-SCS 的关键新增价值；如果电池退化、electrolyzer/FC 能量损失、氢设备启停代价、grid exchange 限额或结算规则改变，Table II 的 166.10 € 可能不再代表净收益。论文自己的结果已显示 F-SCS 通过更多利用 ESS 和电网换取收入，并把 \(SOC\)、\(L_{H2}\) 和 SOE 压到比 Ref-SCS 更低的水平。[pdf:E08]（PDF 物理页 p008，Table II 与 comparative analysis）

论文为“功率调度在模型中能执行”提供了 simulation 与 HIL 波形，但没有给出退化成本模型、氢往返能量成本、设备寿命消耗、grid exchange constraint、价格扰动敏感性或多日统计。因此，功率平衡 claim 并不会因该假设失效而消失，但“获得经济利益”这一相对于 Ref-SCS 的核心改进会直接失效。

## § 10 — 最小复现实验

一周内最值得复现的是“计及价格的 fuzzy 层是否真的在不破坏储能边界的情况下带来可重复收益”，而不是重建完整 switching converter。

1. 用 averaged power-flow model 表示 PV、EV、BAT、FC/LZ 和 grid，按 PDF 录入 Eqs. (1)–(18)、Table I 的 27 条规则、10 s SCS update，以及论文给出的功率/状态边界。[pdf:E03][pdf:E04][pdf:E05][pdf:E06]
2. 从 Fig. 4 近似数字化 1200 s 的 \(P_{PV}\)、\(P_{EV}\) 与 \(C_{grid}\)，同时单独重建 Figs. 8–9 的低/高 SOE 边界场景。[pdf:E06]（PDF 物理页 p006，Fig. 4）；[pdf:E08]（PDF 物理页 p008，Figs. 8–9）
3. 实现两个版本：A 严格照印刷公式执行 Eq. (12)、Eqs. (14)–(15)；B 把充电比例分母改为可充能量，并让充电功率使用 \(P_{net,f}\)。这样可以判断论文歧义是否改变结果，而不是静默选择一种解释。
4. 测量每个 update interval 的功率平衡残差、SOC/\(L_{H2}\)/SOE 越界、grid energy cashflow、BAT throughput 和 H₂ conversion energy。支持 claim 的最低标准是：两版中至少有一版复现极端工况的 \(P_{net,f}\) 符号翻转、无状态越界，并在同一输入下获得接近 Table II 方向与量级的 F-SCS/Ref-SCS 差异。若 literal 版无法复现、仅“修正版”可以，或加入最基本的 conversion/degradation proxy 后收益符号反转，就反驳“论文给出的 SCS 已足够明确且经济优势稳健”。

## § 11 — 最强反例设计

最强反例不是再加一个极端 irradiance，而是构造一个**价格套利看似有利、真实净成本却为负**的闭环场景。保持论文的 PV/EV 轨迹与储能容量不变，给出若干段对 F-SCS 有利的 \(C_{grid}\)，同时加入：非对称买卖价、grid import/export cap、BAT throughput cost、FC/LZ conversion loss cost，以及在价格变化附近的短时反转。然后比较 F-SCS、Ref-SCS 和一个只在计入这些成本后才交易的受约束基线。

攻击成立的条件是：F-SCS 仍显示正的 grid cashflow，却因额外储能循环或受限电网交换而出现更高的 total operating cost，或者触发 SOC/\(L_{H2}\) 边界与功率饱和。Table II 明确把 economic benefit 仅定义为售电收入减购电支出，并显示 F-SCS 的储能水平更低；这为替代解释提供了直接入口。[pdf:E08]（PDF 物理页 p008，Table II 与正文）

再叠加公式二义性作为机制攻击：literal Eq. (12)、(14)、(15) 与语义一致版本若在同一工况产生相反的交易方向或收益排序，就说明论文当前形式不足以唯一复现其核心控制器。[pdf:E05]（PDF 物理页 p005，Eqs. (12)–(15)）

## § 12 — Follow-up Research Idea

在电力电子与微电网控制中，基于本论文材料可以安全作出的候选判断是：高影响工作不仅需要“控制器在一个场景中跑通”，还应把 converter feasibility、实时可执行性、约束安全和经济指标闭合到同一个验证问题。本文已经提供了实时 HIL 起点，却没有把价格不确定性、储能退化和硬件资源纳入同一闭环。[pdf:E08][pdf:E09]

**候选研究方向：面向可证伪净收益的 safety-constrained supervisory control。** 它不再把目标定义为“按电价修正净功率”，而是要求控制器只在能够同时证明储能安全余量、converter power feasibility 与保守净收益下界时进行 grid arbitrage；否则退回仅维持功率平衡的安全模式。

- **未满足需求：** 当前 grid cashflow 可以为正，但无法回答额外 BAT/H₂ 循环是否真的赚钱，也无法回答 formula ambiguity、price disturbance 和 grid cap 下是否仍安全。
- **研究价值：** 把“经济收益”从单一场景的后验数字变成可被逐步证伪的闭环保证，同时保留 ZSC-based MVDC 的实时工程约束。
- **可借鉴工具：** 候选方法是 robust MPC 或 reachability-based safety filter，外接可在线更新的 BAT degradation 与 H₂ conversion cost model；这里仅是方法连接，不声称 novelty。
- **首个证伪实验：** 在 OP4510/MicroLabBox 同类 HIL 上，用相同 PV/EV 轨迹系统扫描价格误差、买卖价差、grid cap、状态估计偏差和设备成本；若所谓净收益下界仍频繁为负，或 safety filter 导致不可接受的未供电，则该方向失败。
- **与本文的实质区别：** 本文用 fixed fuzzy membership/rules 生成 \(K,S\)，并以 grid cashflow 后验比较 F-SCS 与 Ref-SCS；候选方向把“交易是否允许”本身变成带不确定性与硬件可行域的约束判定，并输出可审计的收益下界。本文的实时平台与波形验证说明这一问题可以进入 HIL，但并未完成这种保证。[pdf:E04]（PDF 物理页 p004，fuzzy SCS）；[pdf:E09]（PDF 物理页 p009，HIL results）

相关工作未在本次 PDF-only 阅读中另行检索，因此这个方向只标为候选，不声称具有 novelty。
