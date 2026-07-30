# Hierarchical Control of DC Coupled Fast EV Charging Station

- 作者：Ali Sharida；Abdullah Berkay Bayindir；Sertac Bayhan；Haitham Abu-Rub
- 出处：IEEE Transactions on Power Electronics，Vol. 40，No. 8，pp. 11690–11700
- 年份：2025
- DOI：10.1109/TPEL.2025.3560343
- Zotero key：BF67SD5X

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个站级控制问题：在共直流母线的 fast EV charging station 中，多个可双向充放电的 EV、PV、外部储能和并联 AC–DC converter 会同时改变功率方向与大小，怎样让它们协同工作，在保持直流母线稳定的同时优先利用可再生能源、减少从交流电网取电，并在需要时提供 grid ancillary services。这里的工程难点不是单个 charger 能否控制电流，而是 EV 会随时接入或退出、PV 会波动、储能受 SoC 约束，AC–DC converter 还必须在 rectifier 与 inverter 两种方向之间切换。论文将目标具体化为三层 hierarchical control，并以 low-voltage ride through（LVRT）和 voltage support（VS）作为 ancillary service 的实验实例；摘要还列出高/低电压和高/低频率穿越，但正文只展开 LVRT 与 VS。[pdf:E01]（PDF 物理页 1，Abstract、Fig. 1）

共直流母线架构的价值在于：多个 bidirectional AC–DC converter 共享一条 DC link，EV、PV 和储能可通过单级 DC–DC converter 接入，因而有机会减少多级变换及其损耗，并提高扩展灵活性。但同一结构也把所有端口的瞬时功率失配集中到 DC-link capacitor 上；若站级控制跟不上，母线电压就会直接反映能量不平衡。因此，这篇工作的实质价值是把“充电站能源协调”与“交流电网支撑”放进同一条快速功率平衡链，而不是只增加一个上层充电调度器。[pdf:E01]（PDF 物理页 1，Introduction、Fig. 1）

## § 2 — 前人工作与不足

论文对相关工作的归纳可以分成三类。第一类已研究 PV、fuel cell 或 battery storage 与 bidirectional EV charger 的集成；第二类研究 DC microgrid 的电压支撑或 AC grid 稳定性；第三类研究 hierarchical power distribution。作者认为这些工作分别覆盖了“接入某类资源”或“提供某类服务”，却没有同时处理多 EV、可再生能源、外部储能、双向功率流和完整三层控制。[pdf:E02]（PDF 物理页 2，Introduction 前半）

更具体地，论文指出：已有 DC microgrid secondary control 常把母线调压任务分摊给可用 converter，但在 EV station 中，储能 SoC 不一定允许继续调压，EV 数量也不固定，车主还可能拒绝 V2G；因此“谁来承担 DC-link regulation”本身会变化。作者点名文献 [16] 的 ultrafast charging station hierarchical control 只覆盖 primary 与 secondary 层，没有说明 tertiary ancillary service，也没有处理 renewable intermittency。这里的不足不是“此前完全没有 hierarchical control”，而是控制边界没有闭合到动态端口可用性和 grid-service power allocation。[pdf:E02]（PDF 物理页 2，Introduction 中后段）

需要保留证据边界：以上 prior-work 判断是本文作者对文献 [9]–[16] 的陈述，本卡没有独立复核那些论文，因此不能据此断言本文具有全局 novelty。

## § 3 — 重建作者的思考路径

从本文之前已经存在的工程事实出发，可以重建出如下路径。第一，共直流母线已经能减少端口间不必要的级联能量变换，并让多个资源共享 AC interface。第二，一旦 EV、PV 和储能共用母线，任何端口的功率变化都会先进入 DC capacitor；传统“固定一个储能端口调压”会在储能 SoC 到界或车辆连接状态变化时失效。第三，converter 自身的快速电压/电流跟踪、站内总功率平衡、以及电网故障时的有功/无功分配具有不同的时间尺度与职责，因而适合分层处理。第四，与其让某个不稳定可用的 DC 端口始终担任 slack，不如把所有 DC 端口的电流折算为交流侧所需电流，并让并联 AC–DC converter 在整流和逆变两种方向上都承担母线平衡。[pdf:E02]（PDF 物理页 2，Fig. 2、System Description）

最后一步自然引出本文的核心设计线索：primary 层让每个端口跟踪局部电流/电压目标；secondary 层根据全站 DC 端口功率直接计算 grid-current reference；tertiary 层再依据 LVRT/VS 等服务，把总电流容量分配给 active 与 reactive 分量。这个思路来自端口功率守恒与职责分解，而不需要先假设本文方案已经成立。

## § 4 — 核心 Intuition

核心 intuition 是把 DC-link regulation 变成一个带符号的全站功率对账问题：先算清 EV、储能和 PV 此刻在 DC link 上合计“缺多少或多多少电流”，再命令 AC–DC converter 恰好从电网补足或向电网送出。这样 AC–DC converter 无论处于 rectifier 还是 inverter 方向，都仍是母线的平衡端；tertiary 层只需在这个总电流预算内决定有功与无功如何分配。[pdf:E05]（PDF 物理页 5，Eq. (20)–(24) 及其后说明）

## § 5 — 具体方法与完整 Pipeline

以“三辆 EV 接在同一 400 V DC link 上，PV 功率突然下降”为例，完整 pipeline 如下。

1. **物理端口。** 三个 bidirectional active-front-end AC–DC converter 并联在同一交流输入和同一 DC link；五个 bidirectional buck–boost DC–DC converter 分别连接三辆 EV、一个 PV 和一个 storage。论文用连续时间平均动态方程描述 AC–DC 与 DC–DC 端口，并给出端口电压、电流及 DC capacitor 的关系。[pdf:E02]（PDF 物理页 2，Fig. 3、Eq. (1)–(2)）[pdf:E03]（PDF 物理页 3，Fig. 4、Eq. (3)–(4)）

2. **Primary control。** EV 充电先采用 constant-current（CC），SoC 达到 80% 后转入 constant-voltage（CV）。作者用 current error 作为 sliding surface；CV 段不用 PI voltage controller 的积分项，而是在切换点记录电压并由 Eq. (7)–(10) 选择 proportional gain，以避免长充电过程中积分误差累积并使 CC→CV 的电流参考连续。PV 端使用 incremental-conductance MPPT 产生 current reference，再用同类 sliding-mode current control 跟踪；AC–DC converter 也按分配比例跟踪三相电流参考。[pdf:E03]（PDF 物理页 3，Primary Control 开头）[pdf:E04]（PDF 物理页 4，Eq. (5)–(16)）

3. **Secondary control。** 中央层采集各 EV、storage、PV 端口的电流/电压，按方向求和，计算维持 DC-link reference 所需的 grid RMS current。理想功率守恒给出 feedforward 项，实际 converter loss 则由 DC-voltage error 的积分反馈补偿，形成 Eq. (24)。若 DC 侧净功率不足，参考电流指向从 grid 取电；若净功率有余，参考反向使 AC–DC converter 向 grid 送电；恰好平衡时 grid-current reference 为零。[pdf:E05]（PDF 物理页 5，Eq. (17)–(24) 及四点说明）

4. **并联 AC–DC 分配。** Fig. 7 中，secondary 层先计算 power-sharing ratio，再把 \(I_{dq}^{*}\) 分给三个 AC–DC primary controller；各 converter 的局部 current controller 执行这一参考。该结构把站级功率平衡与 converter 局部跟踪分开。[pdf:E07]（PDF 物理页 7，Fig. 7）

5. **Tertiary ancillary service。** 正常工况下，电流预算主要用于有功交换；发生 voltage sag 时，tertiary 层按采用的 LVRT 曲线产生 \(I_q^{*}\)，再用总 apparent-current budget 计算剩余的 \(I_d^{*}\)。如果电压在 LVRT window 内恢复，系统返回正常充电；若未恢复，则切到 islanded operation，由 PV 与 storage 给 EV 分配可用功率。[pdf:E06]（PDF 物理页 6，Fig. 6、Eq. (25)–(27)）[pdf:E09]（PDF 物理页 9，Fig. 14 与相邻正文）

6. **论文未报告的实现层。** 本文没有给出开关级事件处理、离散控制方程、sampling period、实时仿真 time step、多速率调度、通信拓扑/时延、计算依赖图、并行算法、fixed-point 位宽或数值量化误差；也没有报告 FPGA mapping、FPGA 资源/时序、HIL/real-time simulator，甚至没有说明实际运行控制算法的 controller hardware。实验是物理 power-stage/emulator testbed，但不能据此推断其控制已具备 FPGA 或确定性 real-time 实现。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有形式化数学，关键不是复杂控制理论，而是把端口功率守恒变成可执行的 grid-current reference。

首先，对每个 EV、storage 和 PV DC–DC port，作者在近似 100% conversion efficiency 下令输入功率等于输出功率。把端口电压、电流折算到 DC link，可得总母线电流

\[
I_{dc}
=\sum_{x=1}^{E}\frac{v_{evx}i_{evx}}{V_{dc}}
+\sum_{x=1}^{S}\frac{v_{sx}i_{sx}}{V_{dc}}
+\sum_{x=1}^{P}\frac{v_{pvx}i_{pvx}}{V_{dc}} .
\]

这里 \(E,S,P\) 分别是 EV、storage 和 PV 的数量；带符号的端口电流决定该端口是在给母线供能还是从母线取能。[pdf:E05]（PDF 物理页 5，Eq. (17)–(20)）

其次，作者把 AC 侧 apparent power \(S_g=\sqrt{3}V_{g,\mathrm{rms}}I_{g,\mathrm{rms}}\) 与 DC 侧 \(V_{dc}I_{dc}\) 相等，得到理想 grid-current reference。为了补偿实际 converter loss 和建模误差，再加入 DC-voltage error 的积分项：

\[
I_{g,\mathrm{rms}}^{*}
=\frac{V_{dc}^{*}}{\sqrt{3}V_{g,\mathrm{rms}}}
\left(
\sum I_{EVx}+\sum I_{Sx}+\sum I_{PVx}
\right)
+K_i\int\left(V_{dc}^{*}-V_{dc}\right)\,dt .
\]

feedforward 部分回答“按当前端口功率，grid 应交换多少电流”，积分部分只清除 loss、参数误差和残余 DC-voltage error。正负号直接切换整流/逆变方向；这正是作者声称 AC–DC converter 能跨功率方向调压的数学核心。[pdf:E05]（PDF 物理页 5，Eq. (21)–(24)）

再次，tertiary LVRT 把 voltage sag 映射为 reactive-current reference：

\[
I_q^{*}=
\begin{cases}
0, & 0.9<v_{\mathrm{p.u.}}\le 1.0,\\
2(1-v_{\mathrm{p.u.}})I_n, & 0.5<v_{\mathrm{p.u.}}\le 0.9,\\
I_n, & 0<v_{\mathrm{p.u.}}\le 0.5 .
\end{cases}
\]

这表示电压每下降 1%，按采用的 German grid-code 曲线增加 2% rated current 的 reactive injection；下降超过 50% 时，全部额定电流用于 reactive support，最长 1 s。作者随后由三相 apparent-power 几何关系计算剩余 \(I_d^{*}\)，以避免 active 与 reactive 分量合成后超过总 current budget。[pdf:E06]（PDF 物理页 6，Fig. 6、Eq. (25)–(27)）

最后，EV 的 CC→CV 切换用 Eq. (7) 要求切换前后的 current reference 相等，并据切换瞬间的 voltage error 选取 \(K_p\)，从而让 \(I_{Bx}^{*}=K_p(V_{Bx}^{*}-V_{Bx})\) 在边界处连续。它解决的是 reference continuity，不等于给出了 battery electrochemical dynamics 或全局 stability proof。[pdf:E04]（PDF 物理页 4，Eq. (7)–(10)）

需要注意两个数学边界。第一，Eq. (24) 的积分项补偿平均 loss，却没有显式纳入 converter current limit、measurement delay、通信丢包和端口饱和。第二，论文没有给出完整 closed-loop stability proof；Eq. (5)、(6)、(13)–(15) 主要把 tracking error 选作 sliding surface/control law，未展示 reaching condition、boundary layer 或 chattering 处理。[pdf:E04]（PDF 物理页 4，Eq. (5)–(16)）

## § 7 — 实验设计与结论

实验平台包含三个由 Cinergia bidirectional AC/DC grid emulator 模拟的独立 EV battery、Chroma 62000D storage emulator、RE-005 PV emulator 和 California Instruments MX-30 regenerative grid emulator。Table I 给出的主要参数是：DC link 400 V、EV nominal voltage 400 V、initial battery voltage 360 V、initial SoC 20%、storage nominal voltage 400 V、AC grid 110 \(V_{\mathrm{rms}}\)、battery nominal capacity 1 Ah、每个 converter rated power 4 kW。作者明确说明 1 Ah 是为了在一幅图中缩短并展示完整充电过程，因此这些 charge-profile 时间常数不能直接外推到量产 EV battery。[pdf:E07]（PDF 物理页 7，Fig. 8、Table I）

**问题 1：AC–DC converter 在逆变方向还能否稳住 DC link？ → 实验：** 让第一、第二、第三辆 EV 依次向 grid 送出 real power，观察 grid voltage/current、三路 EV current、DC-link voltage 和 error。**答案：** 作者报告在该工况中 transient DC-link ripple 不超过 2%，grid current 为正弦且与 voltage 相差 180°，对应从 DC link 向 AC grid 送能；这里的 unity power factor 是该有功送电实验的结果，不代表 LVRT 的 reactive-injection 工况。[pdf:E07]（PDF 物理页 7，Fig. 9 及其上下正文）

**问题 2：从 grid 给不同数量 EV 充电时是否仍能调压？ → 实验：** 依次接入一、二、三辆 EV，让 AC–DC converter 作为 rectifier。**答案：** Fig. 10 显示 grid current 随 EV 接入增加，而 DC-link trace 保持在参考附近；论文给出定性“well-regulated”，但未报告这一工况的最大误差、settling time 或统计区间。[pdf:E08]（PDF 物理页 8，Fig. 10）

**问题 3：PV、storage 和 grid 能否按可用功率自动接力？ → 实验：** 起始无 EV、storage SoC 为 75%，PV 先给 storage 充电；随后逐台接入 EV。**答案：** 第一辆 EV 可由 PV 单独供电，第二辆接入后 storage 开始补能并使 grid net power 接近零，第三辆接入后 PV+storage 不足的部分由 grid 提供。该实验直接支持“先利用本地可用功率、grid 补差额”的机制，但没有 energy-cost baseline 或长期 SoC trajectory。[pdf:E07]（PDF 物理页 7，Integration With PV and Storage 开头）[pdf:E08]（PDF 物理页 8，Fig. 11 及相邻正文）

**问题 4：PV intermittency 是否会打断 EV charging？ → 实验：** 在三辆 EV 接入后把 PV maximum-power point 分别突然降低 50% 和 100%，再解除 shading。**答案：** grid current 补上缺失功率，图中 EV charging power 与 DC-link voltage 保持；作者称补偿过程无 ripple 或 overshoot，但正文没有给出放大尺度下的数值误差，因此应视为波形级、定性证据。[pdf:E08]（PDF 物理页 8，Fig. 12 及相邻正文）

**问题 5：不同 charging/discharging combination 能否共享本地功率？ → 实验：** 从 battery emulator 导出三组完整 profile，分别覆盖三车均充电、两车充电一车放电、三车均放电。**答案：** mixed mode 下放电 EV 与 renewable power 先供给充电 EV；全放电时多余功率给 storage 或 grid。图展示了 voltage/current/power/SoC trajectory，但未与其他 station-level controller 做定量 baseline comparison。[pdf:E09]（PDF 物理页 9，Fig. 13 与 Charging Profiles）

**问题 6：能否执行 LVRT/VS 并在故障持续时孤岛？ → 实验：** grid voltage 人为下跌约 20%，EV 从 charging 转为 discharging 支撑 grid；一组在 LVRT window 内恢复，一组不恢复。**答案：** 恢复时回到正常运行；不恢复时 seamless transition 到 islanded operation，并由 PV+storage 合计 8 kW 向三辆 EV 等分为每辆 2.67 kW。论文波形支持模式切换，但没有报告 grid-code compliance test、保护动作、islanding detection latency 或大功率实车验证。[pdf:E09]（PDF 物理页 9，Fig. 14 与相邻正文）[pdf:E10]（PDF 物理页 10，LVRT 段结尾）

总体上，实验支持“方向可反转、资源可接力、模式可切换”这三个机制 claim；它没有证明任意规模下的 stability/scalability，也没有 FPGA、HIL、real-time step、controller latency、计算资源或 fixed-point 结果。

## § 8 — Take-aways

**5 句话：**

1. 本文把共 DC-link charging station 拆成 primary 端口跟踪、secondary 母线功率平衡和 tertiary grid-service 分配三层。
2. 最关键的控制量不是某个 storage 的 voltage command，而是由所有 DC 端口带符号功率汇总得到的 grid RMS current reference。
3. 同一 AC–DC interface 因而能够在 EV charging 时整流、在本地功率过剩时逆变，并持续承担 DC-link regulation。[pdf:E05]
4. 三 EV lab-scale testbed 展示了 grid injection、grid charging、PV/storage 接力、50%/100% shading、混合 charging profile 和约 20% sag 下的 LVRT/islanding。[pdf:E07][pdf:E08][pdf:E09]
5. 证据仍停留在小容量 emulator 与波形级验证，未覆盖 delay、saturation、长期 SoC、硬件控制平台或 FPGA/real-time implementation。

**3 句话：** 本文的主要贡献是把 DC-side power balance 直接变成双向 grid-current reference，并用分层结构叠加 ancillary-service current allocation。实验说明这条链在三端口规模和若干突变工况下可工作。它尚未给出让 scalability 与 robustness 成为可证明工程保证所需的延迟、饱和和数字实现边界。

**1 句话：** 这是一套由“全站功率对账”驱动的双向充电站分层控制，但不是一份已经闭合到 real-time/FPGA 与大规模稳定性保证的实现方案。

## § 9 — 最脆弱的假设

失败代价最大的假设是：中央 secondary controller 能够及时、同步且足够准确地获得所有 EV、storage 和 PV 端口的带符号电流/功率，并且 AC–DC inner loops 有足够余量立即实现 Eq. (24) 与 tertiary 给出的 \(I_{dq}^{*}\)。如果测量过时、端口突然掉线、通信延迟或 converter saturation 使参考无法兑现，feedforward 项会把“旧的功率账本”送给 AC–DC converter；此时只剩 DC-voltage integral feedback 吸收失配，DC capacitor 可能在其恢复之前出现过压或欠压。该风险直接击中“无论功率方向、端口数量和资源可用性都能调压”的核心贡献。[pdf:E05]（PDF 物理页 5，Eq. (24) 及其四点说明）[pdf:E07]（PDF 物理页 7，Fig. 7）

论文提供的支持是三 EV emulator 在逐台接入、PV shading 和 grid sag 下的平滑波形，并在送电实验中报告 transient ripple 不超过 2%。但它没有报告 sensor bandwidth、通信周期/latency、同步方式、current saturation、anti-windup、DC capacitance margin、故障丢包或端口同时切换，也没有在实际 EV battery 容量和额定 charging-station power 上验证。因此，“集中功率账本近似瞬时且可执行”仍是核心但未被充分压力测试的假设。[pdf:E07]（PDF 物理页 7，Table I、Fig. 9）[pdf:E08]（PDF 物理页 8，Fig. 11–12）

## § 10 — 最小复现实验

一周内最值得复现的不是整套 testbed，而是验证 Eq. (24) 是否真的让 DC-link regulation 对功率方向与资源突变不敏感。

- **数据/工况：** 建一个 400 V DC-link averaged model，包含一个可双向 AC–DC grid port、三个脚本化 EV current port、一个 PV port 和一个 storage port；使用 Table I 的 110 \(V_{\mathrm{rms}}\)、每 converter 4 kW 作为尺度。依次执行三 EV 接入、EV 从 charging 反转为 discharging、PV 降低 50%/100% 和 20% grid sag。[pdf:E07][pdf:E08][pdf:E09]
- **实现：** 实现带 current limit 的 inner current loop、Eq. (24) feedforward+integral secondary controller，以及 Eq. (25)–(27) 的 LVRT \(d/q\) allocation；baseline 使用只有 DC-voltage PI、没有端口功率 feedforward 的控制。
- **测量：** 记录最大 \(|V_{dc}-V_{dc}^{*}|/V_{dc}^{*}\)、settling time、grid-current RMS/THD、current saturation 时间、本地 renewable utilization 和功率反向时 integral state。对论文最接近的逐车送电工况，\(\le 2\%\) transient deviation 才算复现其已报告结果；其他工况应在实验前另设安全阈值，不能把论文的定性“smooth”擅自变成同一数值标准。[pdf:E07]
- **支持/反驳：** 若 feedforward 方案在相同 current limit 下显著降低方向反转和 shading 时的最大 DC-voltage deviation，且 LVRT 时不越过 current budget，则支持核心机制；若优势只在无延迟、无饱和的理想模型成立，或功率符号反转造成 integral windup/母线越界，就反驳其强 robustness 解读。

这个实验不复现真实 battery chemistry、长期 SoC scheduling 或完整 hardware efficiency；它只检验最核心、最容易被证伪的站级功率平衡 claim。

## § 11 — 最强反例设计

最强反例是制造“可用总能量看似足够，但功率账本和执行器同时失真”的组合工况：storage 已到 SoC 上限，三辆 EV 中一辆突然掉线、一辆拒绝 V2G、另一辆从 4 kW charging 切到 discharging；同时 PV 从满功率变为 100% shading，grid 出现约 20% sag。给各 DC-port measurement 注入可扫描的异步 delay/jitter，并让 AC–DC converter 受额定 current limit 约束。这个工况不是单纯把负载变大，而是同时攻击 Eq. (24) 的观测及时性与 Eq. (25)–(27) 的执行余量。

如果在物理上仍有可行 power allocation 的区域内，central feedforward 因 stale data 反复改变符号、DC-link voltage 越过安全界限或 LVRT reactive current 使 active balance 崩溃，那么实验就给出一个具体替代解释：论文波形之所以平滑，可能主要因为 emulator event 被顺序安排、通信/执行延迟很小且 converter 未进入 saturation，而不是 hierarchical mechanism 对一般动态端口天然 robust。反之，若在明确的 delay、jitter 和 saturation 边界内仍能保持母线与 grid-current 约束，这个反例也会转化为更强的 robustness 证据。论文现有实验没有覆盖这些变量。[pdf:E07]（PDF 物理页 7，Fig. 7–9）[pdf:E08]（PDF 物理页 8，Fig. 11–12）[pdf:E09]（PDF 物理页 9，Fig. 14）

## § 12 — Follow-up Research Idea

**领域判断：** 对 power electronics/control 方向，高影响结果通常不仅要展示可行波形，还需要明确的 stability/constraint analysis、真实 converter 或高保真 HIL 验证、与强 baseline 的量化比较，以及数字控制实现边界。基于这些标准，一个非增量候选方向是：把“中央控制器精确汇总瞬时功率”改写为“部分可观测、带通信延迟和执行器饱和时，DC charging station 仍有可认证的安全功率域”。

**(a) 未满足需求。** 大规模站点无法保证所有 EV、PV 和 storage measurement 同步到达，也无法保证 LVRT 时仍有足够 current headroom；需要知道在什么 delay、dropout、SoC 和 current-limit 组合下，DC voltage 与 grid-code obligation 仍可同时满足。

**(b) 研究价值。** 这个方向把本文的“实验上看起来 scalable”推进为可计算的 admissible operating envelope。若该边界能指导 converter sizing、DC capacitance、通信周期和服务承诺，它会直接改变 charging-station 设计与 grid-service bidding，而不只是给现有 controller 多加一个 compensation block。

**(c) 相邻领域工具。** 可以借鉴 networked control 的 input-to-state stability、set-invariance/control barrier function，以及 distributed optimization 的 local power contract：每个端口只承诺一个带置信区间和时效戳的可用功率集合，站级控制不再依赖单个精确瞬时值。

**(d) 首个证伪实验。** 在 controller-HIL 或 power-HIL 中系统扫描 measurement delay、jitter、packet loss、EV simultaneous event、PV ramp 和 grid sag，并让算法事先预测 safe/unsafe boundary。只要实验在预测为 safe 的区域内出现 DC-voltage 或 current-limit violation，这个研究想法的核心“可认证边界”就被证伪。

**(e) 与本文的实质区别。** 本文优化的是已知端口功率下的 grid-current reference，并用实验展示若干切换；候选工作改变问题定义，目标不再是精确功率对账，而是在信息不完整和 actuator constrained 时证明安全可行性。由于本卡没有对 2025 年后的相关工作做系统检索，这只是由本文证据约束出来的候选研究方向，不声称 novelty。
