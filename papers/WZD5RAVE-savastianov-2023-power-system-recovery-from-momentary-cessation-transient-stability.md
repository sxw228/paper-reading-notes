# Power System Recovery from Momentary Cessation with Transient Stability Improvement

- 作者：Mikhail Savastianov、Keyue Smedley、Junyi Cao
- 出处：IEEE Transactions on Power Systems, Vol. 39, No. 4, pp. 6014-6025
- 年份：2023（2023 年 12 月在线发表；期刊卷期为 2024 年 7 月）
- DOI：10.1109/TPWRS.2023.3341725 [pdf:E01]（PDF 物理页 1，论文首页题名、作者、卷期、在线发表日期与 DOI）
- Zotero key：WZD5RAVE
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的不是“IBR 是否应尽快从 momentary cessation（MC，暂时停止向电网注入有功和无功、但仍保持电气连接）中恢复”这一笼统问题，而是更具体的一问：**故障清除后，位于不同电气位置的 inverter-based resources（IBRs）是否应该采用相同的有功恢复动作，还是应按它们对暂态失稳模式的作用方向分别控制？** 作者的核心判断是，统一的快速恢复规则可能帮助一部分 IBR，却同时伤害另一部分 IBR；真正决定动作方向的是该 IBR 在当前故障与网络状态下属于 critical 还是 noncritical 一侧。

这个问题有直接的系统安全意义。论文列举的美国南加州事件中，Blue Cut Fire 扰动导致约 1200 MW 光伏损失，Canyon 2 Fire 扰动导致约 900 MW 光伏损失；部分资源恢复过程长达 15 min。文中引用的 NERC 调查还显示，在 13 543 MW 光伏中约 71% 使用 MC，约 33% 无法消除 MC。这说明 MC 不是小容量、短时、可忽略的控制细节，而可能把局部低电压事件转化为大规模有功骤降及失步风险。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

论文的工程价值因此有两层。第一层是解释层：把“恢复越快越好”拆成带位置条件的命题，指出 critical 与 noncritical IBR 对等值功角动态的作用符号相反。第二层是控制层：把这种差异落实成可执行的故障位置/拓扑 lookup table 与逐台 IBR 恢复流程。作者明确研究 bulk-power-system-connected IBR，但认为物理结论也与 distributed resources 有关；实际实施方案只为前者展开，这一适用范围不能被外推为已验证的配电侧方案。

## § 2 — 前人工作与不足

论文梳理出三个已经存在、但彼此没有统一起来的线索。Shin 等的工作 [6] 用 single-machine equivalent（SIME）分析把全部 IBR 放在 noncritical generator group，得到 MC 会恶化故障后暂态稳定，并定义 critical MC threshold；Kang 等 [7] 在同一类布置下研究恢复 ramp rate，得到过慢恢复可能恶化稳定性，并主张比标准更快恢复。另一项工作 [8] 则把全部 IBR 放在 critical group，发现 MC 的效果类似切除 critical generator，反而有利于稳定。这些结果并非简单矛盾，而是各自只覆盖了“所有 IBR 恰好位于同一组”的特殊情形。[pdf:E02]（PDF 物理页 2，Section I）

既有 SIME [9] 能用转子角的 largest gap criterion 区分 critical/noncritical generators，却不能直接给不与同步机同母线的 IBR 分组；基于耦合强度或预测转子角的其他方法 [10]、[15] 同样以 generator identification 为目标。multimachine-multiconverter 的耦合微分方程分析 [14] 不做 critical/noncritical 分组，因此也不能给出按 IBR 所在位置改变恢复动作的规则。缺口的实质不是“以前忘了考虑位置”，而是既有稳定性等值模型的分类对象是同步机，实际 IBR 却分散接在网络母线上；若没有 bus-level classification，就无法把已有理论转成逐台 IBR 指令。[pdf:E03]（PDF 物理页 3，Section II 至 Section III；MC 定义、标准区间与 controlled-current-source 建模前提）

当时的工程建议也放大了这个缺口。论文转述的 NERC 建议包括缩短恢复延时并把有功 ramp rate 提高到至少 100%/s，但这是面向全部 IBR 的同向建议。作者要修正的正是这种“恢复动作不随失稳群组变化”的默认假设，而不是否定快速恢复本身。[pdf:E03]（PDF 物理页 3，Section II 的 NERC recommendations）

## § 3 — 重建作者的思考路径

以下是基于论文背景和失败模式的逆向重建，不是作者逐字陈述的研究过程。

首先，真实扰动说明大量 IBR 会同时进入 MC，而且统一 ride-through 或统一恢复并不总能实现。其次，已有研究在“全部 IBR 属于 noncritical group”时得到恢复更快更好，在“全部属于 critical group”时却得到停止注入更好；最自然的解释不是某一组实验必然错误，而是 IBR 对暂态稳定的作用取决于它与失步机群的相对电气位置。再次，IBR 在故障时间尺度上可近似为快速 controlled current source，因此它改变的是同步机看到的电气功率项；这个项的符号受电压相角关系影响，可以先在 OMIB 的相量几何中看清。[pdf:E04]（PDF 物理页 4，Table I、Fig. 4、Fig. 5、Eq. (3)-(6)）

沿着这条线索，一个合理的研究路径是：先在 OMIB 中求 IBR 注入如何移动 power-angle curve，并确认 crossing angle 的有效范围；再把多机系统压缩成 critical 与 noncritical 两台等值机；然后把 generator largest-gap classification 扩展到 bus voltage angle，使每台 IBR 能被分到一侧；最后根据其对等值电气功率是增益还是减益，选择 inject 或 cease。这里真正的转折是把问题从“选择统一的 ramp rate”改写成“先判断动作符号，再谈恢复速度”。

## § 4 — 核心 Intuition

IBR 的有功注入不是天然有利或有害：当它跟随 critical group 的相角时，恢复注入会降低两群等值系统的有效电气功率并压缩减速能力；当它跟随 noncritical group 时，恢复注入则提高有效电气功率并增加减速能力。因而故障后应让 critical-bus IBR 暂停有功、让 noncritical-bus IBR 尽快恢复或维持有功，而不是给所有 IBR 同一个 ramp 命令。[pdf:E05]（PDF 物理页 5，Eq. (7)-(10)、Fig. 6 与 Section III 末）

## § 5 — 具体方法与完整 Pipeline

方法可以分成离线分类准备与在线恢复控制两部分。

1. **按网络状态建立 bus lookup table。** 对每个关心的网络开关/保护状态、故障类型和故障位置，取得各母线电压相角；每个时间步把相角降序排列，寻找相邻母线之间出现的第一个 largest gap。gap 上方的母线标为 critical，下方标为 noncritical。这个规则由 generator rotor-angle largest gap criterion 扩展而来。Fig. 7 展示了 IEEE 39-bus 的分组，Section IV-A 给出三步算法。[pdf:E06]（PDF 物理页 6，Fig. 7、Fig. 8、Eq. (11) 与 Section IV-A）
2. **在线识别工况。** central processor unit（CPU）根据故障位置、generator dispatch、breaker state 等信息选择对应 lookup table；measurement units（MUs）提供同步机与 IBR 母线的电压数据。论文认为纯在线预测可能来不及，因此把预计算表作为快速主路径。Table II 也表明，同一母线会随故障位置改变分组；实际表需要细化到同一线路上的不同故障位置。[pdf:E07]（PDF 物理页 7，Table II、Fig. 9、Eq. (12)-(13) 与 Section V）
3. **按电气距离逐台动作。** 先把 IBR 按到故障点的 electrical distance 排序，从最近者开始。若 lookup table 判为 critical，则 fault clearing 后不注入有功；若判为 noncritical，则注入有功。对没有进入 MC 的 IBR，含义分别是 critical 侧主动 cease、noncritical 侧保持注入。
4. **每次动作后做暂态稳定判定。** 论文建议调用 real-time transient stability assessment，例如 emergency SIME。若等值转子角 \(\delta<\delta_{\mathrm{uep}}\)，系统判稳并停止逐台动作；否则处理下一台 IBR。文中称该估计可在约 350 ms 时间框架内完成，但该时间主要受采样率、通信与控制动作速度影响，不是本文对整套闭环控制器的实测 worst-case latency。[pdf:E08]（PDF 物理页 8，Fig. 10、Fig. 11、Table III 与 Section VI 开头）
5. **稳定后恢复功率平衡。** 一旦系统稳定，先前被 idled 的 IBR 再逐渐回到扰动前输出，避免把暂态稳定动作误当成永久弃电策略。

以 IEEE 9-bus 的 line 5-7 near B7 三相接地故障为例，作者识别 G2、G3 及 B2、B3、B7、B8、B9 为 critical，G1 及 B1、B4、B5、B6 为 noncritical；B2、B5、B7、B8、B9 的电压跌破 0.5 pu MC threshold。于是位于 B5 的 IBR 应在清故障后 step restore，而位于 B2/B7/B8/B9 的 IBR 应保持 no injection。[pdf:E08]（PDF 物理页 8，Fig. 10、Fig. 11 与 Case 1）

从 EMT + FPGA 实现视角看，论文报告的是 MATLAB Simulink 10.6（R2022b）的 **phasor simulation**，不是开关级 EMT。同步机使用带 IEEE DC1A excitation 的高阶 state-space model，IBR 被简化为 unity-power-factor controlled current source；MPPT 动态和 IBR current transient 被忽略。论文未报告离散积分公式、solver step、多速率调度、开关事件处理、并行依赖图、fixed-point/浮点数值格式、FPGA 映射、片上资源、时序收敛、实时步长、HIL 平台或硬件实测。因此，这篇工作的贡献是故障恢复决策逻辑与暂态稳定机理，不是 EMT 求解器或 FPGA 实现。[pdf:E03]（PDF 物理页 3，Section III 的 IBR 建模假设）[pdf:E08]（PDF 物理页 8，Section VI 的仿真平台与模型）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，核心是追踪 IBR 注入如何改变等值同步机的电气功率。

在 OMIB 中，不注入 IBR 电流时，同步机电气功率为

\[
P_{e0}=\frac{E_gV_0}{x_g+x_{L1}}\sin\delta .
\tag{1}
\]

IBR 以 unity power factor 注入幅值 \(I_{\mathrm{IBR}}\)、相角跟随接入点电压角 \(\gamma\) 的电流后，

\[
P_e=P_{e0}
-\frac{x_{L1}}{x_g+x_{L1}}E_gI_{\mathrm{IBR}}\cos(\delta-\gamma).
\tag{2}
\]

Eq. (2) 的工程含义比公式外观更重要：若 \(\delta-\gamma<90^\circ\)，余弦为正，IBR 项被减去，\(P_e\) 降低；若 \(\delta-\gamma>90^\circ\)，该项转为增加 \(P_e\)。作者用 Fig. 4 的相量几何推导接入点电压角

\[
\gamma=
\tan^{-1}\!\left(
\frac{\sin\delta}{V_0x_g/(E_gx_{L1})+\cos\delta}
\right)
+\sin^{-1}\!\left(
\frac{I_{\mathrm{IBR}}}
{\sqrt{(E_g/x_g)^2+(V_0/x_{L1})^2+
2E_gV_0\cos\delta/(x_gx_{L1})}}
\right).
\tag{3}
\]

直角三角形存在条件进一步给出 Eq. (4)-(6) 的最大允许转子角 \(\delta_{\max}\)：它可能为 \(180^\circ\)、被限制为 \(\delta_m\)，或在给定 \(I_{\mathrm{IBR}}\) 下根本不存在。该条件提醒读者，理想 current command 也受网络相量可行域约束。[pdf:E04]（PDF 物理页 4，Eq. (1)-(6)、Fig. 4、Fig. 5 与 Table I）

令有 IBR 与无 IBR 的 power-angle curve 相交，作者得到

\[
\delta_{\mathrm{cp,min}}
=90^\circ+\sin^{-1}\!\left(\frac{E_gx_{L1}}{V_0x_g}\right)>90^\circ ,
\tag{7}
\]

\[
\delta_{\mathrm{cp}}
=90^\circ+\sin^{-1}\!\left(
\frac{E_gx_{L1}}{V_0x_g}+\frac{x_{L1}}{V_0}I_{\mathrm{IBR}}
\right),
\quad
I_{\mathrm{IBR}}<\frac{V_0}{x_{L1}}-\frac{E_g}{x_g}.
\tag{8)-(9}
\]

这修正了文献 [11] 把 crossing point 可能范围写成 \(0^\circ\) 到 \(180^\circ\) 的结论：本文证明其下界严格大于 \(90^\circ\)，而且取决于网络参数。由于大部分运行角区间位于 crossing point 之前，critical-side IBR 注入通常把 power-angle curve 向下移。论文用 equal-area criterion 的稳定裕度

\[
\eta=\frac{A_d-A_a}{A_a}
\tag{10}
\]

量化 accelerating area \(A_a\) 与可用 decelerating area \(A_d\) 的差；\(\eta>0\) 表示稳定，曲线越高、减速面积越大，裕度越好。[pdf:E05]（PDF 物理页 5，Eq. (7)-(10) 与 Fig. 6）

多机系统通过 SIME 压缩为 critical 与 noncritical 两台等值机：

\[
M_{\mathrm{CN}}\ddot{\delta}_{\mathrm{CN}}
=P_{\mathrm{CN,m}}-P_{\mathrm{CN,e}},
\qquad
\delta_{\mathrm{CN}}=\delta_C-\delta_N,
\tag{11}
\]

其中 \(M_{\mathrm{CN}}=M_CM_N/(M_C+M_N)\)，而
\(P_{\mathrm{CN,e}}=(M_{\mathrm{CN}}/M_C)P_{C,e}
-(M_{\mathrm{CN}}/M_N)P_{N,e}\)。这是把“多台机是否分裂”为“两群之间的相对加速”来观察。[pdf:E06]（PDF 物理页 6，Eq. (11) 与 Fig. 8）

含一台 IBR 时，两侧电气功率为

\[
P_{C,e}=g_1E_C^2+
\frac{E_CE_N\sin(\delta_C-\delta_N)}{x_{13}+x_{23}}
-\frac{x_{23}E_CI_{\mathrm{IBR}}\cos(\delta_C-\gamma)}
{x_{13}+x_{23}},
\tag{12}
\]

\[
P_{N,e}=g_2E_N^2-
\frac{E_CE_N\sin(\delta_C-\delta_N)}{x_{13}+x_{23}}
-\frac{x_{13}E_NI_{\mathrm{IBR}}\cos(\delta_N-\gamma)}
{x_{13}+x_{23}}.
\tag{13}
\]

若 IBR 属于 critical group，\(\gamma\) 跟随 \(\delta_C\)，最终使 \(P_{\mathrm{CN,e}}\) 下降；若它属于 noncritical group，\(\gamma\) 跟随 \(\delta_N\)，最终使 \(P_{\mathrm{CN,e}}\) 上升。于是“critical cease、noncritical inject”不是经验规则，而是 Eq. (12)-(13) 中 IBR 项对两群等值电气功率产生相反符号的控制结论。[pdf:E07]（PDF 物理页 7，Eq. (12)-(13)）

## § 7 — 实验设计与结论

**问题 1：在最简单的 critical-side OMIB 中，恢复越快是否越稳定？** 作者把一个 0.2 pu controlled current source 接在同步机端，fault clearing 后等待三个 fundamental cycles，再比较 no injection、ramp injection、step injection。equal-area 稳定裕度依次为 2.52、2.10、1.72；在这个 critical-side 情形，恢复越快反而越差。这个实验验证的是数学符号，不是通用电网规模上的性能。[pdf:E05]（PDF 物理页 5，Fig. 6）

**问题 2：critical/noncritical 位置会不会在同一 9-bus 系统中反转最优动作？** 两个 IEEE 9-bus fault case 均使用三相接地故障并在清故障后切线。系统在 MATLAB Simulink R2022b 中用 phasor method 建模；IBR MC threshold 为 0.5 pu，ramp 为 100%/s，reactive power injection 固定为 0，以 critical clearing time（CCT）作为指标。Case 1 加入一台 32 MW IBR，占总发电 10%；CCT 通过改变清故障时间搜索到 0.1 ms 精度，但论文没有把该精度说明为 solver time step。[pdf:E08]（PDF 物理页 8，Section VI、Fig. 10、Fig. 11 与 Table III）

结果具有清楚的次序反转。Case 1 中，noncritical B5 的 no/ramp/step CCT 分别为 123.3/127.1/137.8 ms，step 最好；critical B2 的对应结果为 129.8/121.4/80.5 ms，no injection 最好。对没有触发 MC 的资源，noncritical B1 保持/停止注入为 147.1/133.0 ms，而 critical B3 为 98.4/121.0 ms，仍是相反动作更优。以 Fig. 12 的固定 clearing time 比较，B5 在 128 ms 时 proposed step 稳定而 NERC ramp 不稳定；B2 在 128 ms 时 proposed no injection 稳定而 NERC ramp 不稳定；B3 未进入 MC 时，在 110 ms 下 proposed cease 稳定而 keep injection 不稳定。[pdf:E09]（PDF 物理页 9，Table IV、Table V、Table VI 与 Fig. 12）

**问题 3：同一母线的标签是否真的随故障位置变化？** Case 1 的 line 5-7 near B7 与 Case 2 的 line 8-9 near B8 产生不同 critical sets；例如 B3 在 Case 1 为 critical，在 Case 2 为 noncritical。Case 2 中，B3 的 no/ramp/step CCT 为 260.9/261.7/264.4 ms，而 critical B7 为 259.6/258.3/247.1 ms，再次出现同一动作速度的相反排序。[pdf:E09]（PDF 物理页 9，Section VI-A 至 VI-B 与 Table V）

**问题 4：结论能否扩展到更大系统与多 IBR 协同？** IEEE 39-bus case 含十台同步机和十台 IBR，IBR 正常运行于 unity power factor，并提供总发电的 20%；作者测试 line 21-22 near B21 与 line 11-6 near B11 两个三相接地故障。第一场景同时控制 noncritical B16 与 critical B22 时，“B16 step + B22 no injection”的 CCT 为 330.2 ms，而相反的“B16 no injection + B22 step”为 294.2 ms。第二场景中四台 noncritical IBR 全部 step 的 CCT 为 348.8 ms，高于全部 no injection 的 337.0 ms。作者据此认为方法对更大系统和多 IBR 可扩展，但这里只有一个 39-bus benchmark、两种 fault locations，不能外推为任意规模或任意控制器动态下的 scalability proof。[pdf:E10]（PDF 物理页 10，Table VII、Table VIII、Fig. 13 与 Section VI-C/D）

**问题 5：相对统一 NERC 恢复建议，收益多大、边界在哪里？** 作者汇总的 CCT 提升平均为 5.6%，最小 0.4%，最大 23%；结论是 critical IBR 不注入、noncritical IBR 尽快回到扰动前有功。论文也明确承认：若 fault duration 超过 proposed strategy 自身的 CCT，该策略不能稳定系统。[pdf:E11]（PDF 物理页 11，Fig. 14-Fig. 16、Section VI-D 与 Section VII）

没有被实验覆盖的内容同样重要：没有 EMT switching model、converter current limit/reactive-priority dynamics、测量噪声或延迟 sweep、拓扑识别错误、负荷模型敏感性、保护误动、真实控制器、实时仿真、HIL、FPGA 或现场试验；也没有报告 lookup table 的存储规模、离线生成成本与在线 worst-case execution time。因此实验支持“在给定 phasor benchmarks 和理想 current-source 假设下，动作方向随分组反转”，而不是支持“实际大电网中该闭环已可直接部署”。论文的参考文献表共列出 17 项，包含 NERC reports、SIME/E-SIME、IBR 暂态稳定、multimachine-multiconverter 分析与标准系统参数来源；本卡未对这些外部文献做独立全文核验。[pdf:E12]（PDF 物理页 12，References [1]-[17]）

## § 8 — Take-aways

**5 句话：**

1. MC 恢复的正确动作取决于 IBR 在当前故障下属于 critical 还是 noncritical group。
2. critical-side IBR 恢复有功会降低等值电气功率和暂态稳定裕度，noncritical-side IBR 恢复有功则相反。
3. 作者用 bus voltage-angle largest gap 把 SIME 的 generator classification 扩展到 IBR 所在母线。
4. 控制策略是 noncritical IBR 尽快注入、critical IBR 暂停注入，并用在线稳定评估决定是否继续处理下一台。
5. IEEE 9-bus 与 39-bus phasor simulation 支持这个方向性结论，但不构成 EMT、实时硬件或现场部署验证。[pdf:E11]（PDF 物理页 11，Section VII）

**3 句话：**

1. 统一恢复规则掩盖了 IBR 位置对 power-angle dynamics 的相反作用。
2. 论文把这个差异转成 lookup-table classification 与逐台恢复动作，并在两个标准系统上观察到更高 CCT。
3. 最需要进一步验证的是分类在模型不确定性、测量延迟与真实 converter constraints 下是否仍可靠。[pdf:E11]（PDF 物理页 11，Section VII；作者结论与本卡基于未覆盖范围的判断）

**1 句话：**

先判断一台 IBR 的注入是在给失步群加速还是减速，再决定它应立即恢复还是暂时停机。[pdf:E07]（PDF 物理页 7，Eq. (12)-(13)）

## § 9 — 最脆弱的假设

失败代价最大的一条假设是：**预计算 lookup table 在实际动作时能正确判断每台 IBR 对当前失稳模式的作用符号，即 critical/noncritical 标签不会因故障位置误差、拓扑/dispatch 漂移、测量延迟或 largest-gap 不确定性而错置。**

这条假设之所以最脆弱，是因为控制律是二值且方向相反：同一个 step injection 对 noncritical IBR 是论文推荐动作，对 critical IBR 却是最差动作。错分不是“少一点收益”，而可能把本应 cease 的资源推向最快恢复，直接降低 CCT。论文自己展示 B3 会随 fault location 从 critical 变为 noncritical，Table II 还说明实用 lookup table 必须细化到同一线路上的不同故障位置；这证明分类对工况敏感，而不是固定母线属性。[pdf:E07]（PDF 物理页 7，Table II 与 Section V）

论文给出的支持证据是 IEEE 9-bus 两个 fault locations、IEEE 39-bus 两个 fault locations 下，largest-gap 分组与 CCT 次序一致，并且较大系统场景中多 IBR 的联合动作保持相同方向。[pdf:E10]（PDF 物理页 10，Table VII、Table VIII 与 Section VI-C/D）但缺少的证据更直接对应部署风险：没有 near-tie angle gaps、PMU/MU 噪声与时标、通信延迟、错误 breaker state、fault-location uncertainty、dispatch/负荷变化、模型参数偏差或分类更新滞后的敏感性试验。基于证据的判断是，当前结果证明了“标签正确时控制方向有效”，尚未证明“真实系统能持续给出正确标签”。

## § 10 — 最小复现实验

一周内最有信息量的最小复现，是只复现 IEEE 9-bus Case 1 中一个 noncritical 与一个 critical 接入点的 **CCT 次序反转**，而不复现完整 lookup-table 系统。

1. 使用标准 IEEE 9-bus phasor model，按论文给出的结构配置高阶同步机、DC1A excitation 和一个 32 MW controlled-current-source IBR；若无法取得文献 [12]、[16] 的完全相同参数，应把目标标为“机制复现”而非“逐数值复现”。
2. 在 line 5-7 near B7 施加三相接地故障并清故障切线，设置 MC threshold 0.5 pu、\(Q=0\)、ramp 100%/s。先把 IBR 放在 noncritical B5，再放在 critical B2。
3. 分别实现 no injection、three-cycle-delay ramp injection、three-cycle-delay step injection。通过二分或细扫 fault clearing time 求 CCT，搜索分辨率取 0.1 ms；同时记录 bus voltage angles、largest gap、group label 与失步判据。
4. 论文给出的目标次序是：B5 为 \(137.8>127.1>123.3\) ms（step > ramp > no），B2 为 \(129.8>121.4>80.5\) ms（no > ramp > step）。数值可因未报告的完整模型细节而偏移，但排序必须反转。[pdf:E08]（PDF 物理页 8，Table III）
5. 若两个接入点稳定地出现相反排序，并且 bus label 与排序方向一致，则核心 mechanism 得到最低限度支持；若在合理参数扰动和足够细 clearing-time search 下排序不反转，或 label 与最优动作无稳定关系，就应视为对核心 claim 的反驳，而不是调参直到吻合。

这个复现不需要实现 39-bus、多 IBR 次序控制、E-SIME online loop 或通信网络，因此一周内可完成；它也不能验证 scalability 与部署 latency。

## § 11 — 最强反例设计

最强反例不是再换一个标准系统，而是专门制造 **largest-gap 标签接近翻转、lookup table 却来不及更新** 的工况。可选一个论文已显示会换组的边界母线 B3，在同一线路上连续移动 fault location，同时改变 dispatch、负荷与一条线路/断路器状态；加入 MU 相角噪声、一个到两个采样周期延迟和 fault-location error，寻找最大与第二大 angle gap 几乎相等的场景。对每个场景比较三种控制：

1. 使用无误差在线轨迹得到的 oracle group label；
2. 使用预计算、离散化 fault location 的 proposed lookup table；
3. 统一 NERC ramp/keep-injection baseline。

攻击成功的判据应很具体：lookup table 把真实 critical IBR 标成 noncritical 并执行 step injection，使系统在相同 clearing time 下从稳定变不稳定，或使 CCT 低于 NERC baseline；同时 oracle label 的 cease action 仍能稳定。这样可以排除“工况本身太严重”的替代解释，直接证明失败来自分类错误。论文 Fig. 9 的流程会在每次动作后再做稳定评估，但如果第一条错误动作已经消耗关键 decelerating margin，后验检测未必能撤销损失；这正是应测试的机制性风险。[pdf:E07]（PDF 物理页 7，Fig. 9 与 Table II）

若 lookup table 在上述边界、延迟和拓扑扰动下仍保持正确动作符号，并始终不劣于 baseline，这个反例就失败，反而会显著增强论文的工程可信度。

## § 12 — Follow-up Research Idea

在电力系统暂态稳定与 emergency control 领域，高影响工作通常需要同时满足可解释机理、严格稳定性边界、跨工况大规模验证与可实施的时延/通信约束。基于第 9 节，候选方向是：**不再把每台 IBR 强制归为一个离散 group，而是实时认证“该动作对 \(P_{\mathrm{CN,e}}\) 和稳定裕度的作用符号在不确定性集合内是否确定”，只对符号可认证的 IBR 执行 inject/cease。** 这是候选研究想法；本卡只阅读了论文及其参考文献表，没有检索后续工作，因此不声称 novelty。

**（a）未满足的需求。** 现有 lookup table 随 fault location、topology 和 dispatch 组合增长，而且一位 classification error 就可能把控制方向完全翻转。系统需要的不是更多表项，而是一个在 measurement noise、latency、topology ambiguity、current limit 与模型偏差下仍能说明“这个动作不会比基线更差”的决策边界。

**（b）潜在研究价值。** 若能从 Eq. (11)-(13) 推导 \(P_{\mathrm{CN,e}}\) 变化的区间界，并把它与 finite-time rotor-angle safety margin 连接，就能把论文的物理 intuition 提升为带 uncertainty certificate 的 emergency control。其价值不只是多提高几个百分点 CCT，而是给出何时允许动作、何时必须 abstain 的可审计安全保证。

**（c）可借鉴的相邻工具。** 可借鉴 set-membership state estimation 形成相角/参数可行集，用 reachability analysis 或 control barrier functions 给出短时失步边界，再用 robust optimization 选择一组 IBR 动作；若作用符号跨越零，则回退到 hold/限幅动作，而不是硬分类。这里的“回退”是研究对象的一部分，必须与 NERC baseline 一起验证，不能预设安全。

**（d）第一个证伪实验。** 在 IEEE 9-bus 与 39-bus 上系统扫 fault location、dispatch、拓扑、measurement delay/noise 和 converter current limits。若认证方法在大多数可稳定场景都只能 abstain，或存在声称已认证但动作仍使 CCT 低于 baseline 的反例，则核心想法被证伪；若它能在不确定工况中保持零违规并保留显著的 CCT 改善，再进入 EMT 与 real-time HIL 验证。

**（e）与本文的实质区别。** 本文先给母线一个 critical/noncritical 标签，再按标签选择动作；新问题是“在当前不确定信息下，能否证明某个动作方向不会恶化稳定裕度”。它改变了控制目标与输出语义，从 hard classification 变成 action-sign certification，而不是在现有 lookup table 旁边再加一个预测模块。本文 references [1]-[17] 覆盖事件报告、SIME/E-SIME、IBR 暂态稳定与标准测试系统来源，但仅凭该列表不足以判断这一方向是否已有同构工作。[pdf:E12]（PDF 物理页 12，References）
