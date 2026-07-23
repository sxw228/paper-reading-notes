# A Generalized Associated Discrete Circuit Model of Power Converters in Real-Time Simulation

- Zotero key：`WV2NL3DR`
- corpus order：`72`
- 作者：Keyou Wang, Jin Xu, Guojie Li, Nengling Tai, Anping Tong, Junxian Hou
- 年份 / 出处：2019，*IEEE Transactions on Power Electronics*, 34(3), 2220-2233
- DOI：[10.1109/TPEL.2018.2845658](https://doi.org/10.1109/TPEL.2018.2845658)
- 源 PDF：`_source.pdf`
- PDF SHA-256：`0967cf4dbb4a3341cdf0bd3d919136fc2c79216f9ad9947c4e53ce1d6741cad0`
- 阅读边界：以下“作者声称/报告”只复述本篇 PDF；解释、批评、反例与研究方向均显式标为基于证据的推断或候选判断。本文没有完成外部相关工作检索，因此不在本卡声称 novelty。

## § 1 — 研究问题与重要性

这篇论文处理的是实时电磁暂态仿真里的一个结构性矛盾：功率变换器的开关状态不断变化，但实时求解器不能在每次开关时都重新组装、分解节点导纳矩阵。associated discrete circuit（ADC，关联离散电路）把每个开关在离散时刻表示成一个固定等效导纳与一个历史电流源的并联。只要 ON 和 OFF 两种状态使用同一个导纳 \(Y_{\mathrm{sw}}\)，开关动作就只改变右端注入电流，不改变网络矩阵；节点矩阵可以预存，FPGA 每一步只需更新历史源并完成固定结构的节点求解。[pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png)

传统 L/C-ADC 的问题来自它对这个数值接口的物理实现：ON 用小电感，OFF 用小电容串联电阻。电感、电容的充放电是为模拟开关而人为引入的动态，不是被模拟变换器本身的储能过程。每次换相都可能激发这段虚拟暂态，形成虚拟功率损耗；其 RLC 参数又会受运行点和外部电路影响。论文要回答的核心问题因此是：能否保留“固定导纳、无需重构矩阵”的实时计算优势，同时让开关的离散暂态更快衰减，并让参数尽量不依赖外部系统？作者提出 G-ADC，以参数化历史电流源直接规定离散响应，再从稳定域和极点阻尼反推参数。[pdf:E01](_evidence/E01-p001-title-abstract-intro.png) [pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png)

其重要性不只是提高单个开关波形的观感。对于固定微秒级步长的 HIL，矩阵结构能否固定决定了计算是否可预测；虚拟损耗是否随开关频率显著增长，又决定了模型在高频 PWM 下是否仍可信。论文实际搭建了 NI-PXIe 平台，将 EMTP、PWM 和开关历史源计算放到 FPGA，并保留与外部控制器连接的 HIL 接口。[pdf:E08](_evidence/E08-p008-fpga-flow-hcri.png)

## § 2 — 前人工作与不足

按本文自己的文献回顾，PSCAD/EMTDC 常用 two-value-resistor model：开关 OFF 时用大电阻、ON 时用小电阻。它能逼近理想开关，但等效导纳随状态变化，因而需要重构导纳矩阵，实时计算负担较重。已有 ADC / small-time-step model 则用固定等效导纳避免这一问题，并已进入 RTDS、FPGA 平台和高性能服务器实现；本文列出的源头与相关实现包括 Hui、Christopoulos、Morrall、Matar、Dinavahi 等工作。[pdf:E01](_evidence/E01-p001-title-abstract-intro.png) [pdf:E14](_evidence/E14-p014-references.png)

本文认为 L/C-ADC 仍有两个具体缺口。第一，参数配置与运行工况、外部电路有关，不能为同一拓扑直接复用一组参数。第二，模拟开关用的小电感和小电容产生充放电暂态，特别在高开关频率下会形成不可接受的虚拟功率损耗。[pdf:E01](_evidence/E01-p001-title-abstract-intro.png) 作者还指出，已有 reinitialization 与 compensation-source 方法主要降低换相后的初始误差，但它们仍建立在 L/C-ADC 上；如果离散系统自身阻尼不足，减小后的初始误差仍会在后续步中慢慢衰减。[pdf:E08](_evidence/E08-p008-fpga-flow-hcri.png)

这里需要保留证据边界：这些 prior-work 判断来自本文的叙述和参考文献表，本卡没有逐篇重读被引论文。因此可以说“本文相对于自己选定的 L/C-ADC 基线扩大了可调离散参数空间”，但不能据此断言它在所有固定导纳开关模型中首次做到这一点。

## § 3 — 重建作者的思考路径

以下是基于论文结构的合理重建，不是作者逐字陈述。

第一步，实时计算真正需要保留的不是“小电感/小电容”这组物理元件，而是它们离散化后共同提供的接口：固定导纳加历史电流源。既然节点求解只看这个离散接口，就可以把模拟电路的 RLC 参数拿掉，直接参数化历史源。[pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png)

第二步，参数不能随意选。理想开关的稳态要求是：ON 时电压为零但电流可任意，OFF 时电流为零但电压可任意。把这两个要求代入历史源递推式，可以先消去两个自由度，得到 \(\alpha_{\mathrm{off}}=Y_{\mathrm{sw}}\) 与 \(\beta_{\mathrm{on}}=-1\)。[pdf:E03](_evidence/E03-p003-two-level-constraints.png) [pdf:E04](_evidence/E04-p004-poles-stability.png)

第三步，换相后的虚拟误差可被看作离散系统的 zero-input response。于是“损耗小”可以转化为“离散极点模尽量小”：先用 Jury criterion 划出稳定域，再最小化最大极点模 \(MMoP\)。这把经验式调 RLC 参数改写成了一个可分析的离散系统设计问题。[pdf:E04](_evidence/E04-p004-poles-stability.png) [pdf:E05](_evidence/E05-p005-best-damped-three-level.png)

第四步，为了让一组参数脱离外部网络，作者把半桥外部滤波电感视作近似恒流源、直流侧平滑电容视作近似恒压源，只分析一个拓扑基本单元。这个解耦不是无条件成立，而是依赖开关模型暂态远快于外部 L/C 动态。[pdf:E03](_evidence/E03-p003-two-level-constraints.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

第五步，即使极点阻尼很好，换相瞬间的初态也可能不理想。因此实现端再加入 HCRI（history current reinitialization）：状态不变时按递推式更新，状态改变时使用上一次同类开关动作结束时的历史电流，先压小初始误差，再让 best-damped 极点快速消除剩余误差。[pdf:E08](_evidence/E08-p008-fpga-flow-hcri.png) [pdf:E09](_evidence/E09-p009-case-setup-comparison.png)

## § 4 — 核心 Intuition

G-ADC 的核心不是给 L/C-ADC 换一组更好的电感、电容，而是承认实时节点求解器真正需要的只有“固定端口导纳 + 可更新历史源”。作者直接设计历史源的离散递推，使稳态像理想开关、换相误差的极点尽量靠近零；这样既不改变预存节点矩阵，又避免受虚拟 RLC 储能过程束缚。[pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png) [pdf:E04](_evidence/E04-p004-poles-stability.png)

物理上，它把“用一个小 L 或小 C 假装开关”改成“用一个固定端口导纳承接网络耦合，再用有记忆的电流源重建开关行为”。数值上，它把开关建模变成受稳定约束的离散状态响应整形；能否脱离外部系统，则取决于拓扑分解与时间尺度分离假设。[pdf:E03](_evidence/E03-p003-two-level-constraints.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

## § 5 — 具体方法与完整 Pipeline

以论文中的三相两电平 VSC 为例，完整流程如下。

1. **固定网络接口。** 对每个开关统一设置等效导纳 \(Y_{\mathrm{sw}}\)。ON/OFF 状态都保持这个导纳，节点导纳矩阵因此不随 PWM 状态改变。[pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png)
2. **定义参数化历史源。** ON 与 OFF 分别使用
   \(I_{h,\mathrm{on}}(t)=\alpha_{\mathrm{on}}U(t-\Delta t)+\beta_{\mathrm{on}}I(t-\Delta t)\) 和
   \(I_{h,\mathrm{off}}(t)=\alpha_{\mathrm{off}}U(t-\Delta t)+\beta_{\mathrm{off}}I(t-\Delta t)\)。五个待定量为 \(Y_{\mathrm{sw}},\alpha_{\mathrm{on}},\beta_{\mathrm{on}},\alpha_{\mathrm{off}},\beta_{\mathrm{off}}\)。[pdf:E03](_evidence/E03-p003-two-level-constraints.png)
3. **先满足理想开关稳态。** 用 ON 时 \(U=0\)、OFF 时 \(I=0\) 的条件得到 \(\alpha_{\mathrm{off}}=Y_{\mathrm{sw}}\)、\(\beta_{\mathrm{on}}=-1\)，剩下 \(\alpha_{\mathrm{on}}\) 和 \(\beta_{\mathrm{off}}\) 控制暂态。[pdf:E04](_evidence/E04-p004-poles-stability.png)
4. **按拓扑建立离散动态。** 两电平变换器分解成互补导通的半桥基本单元；三电平 NPC 则用可输出 \(U_d/2,0,-U_d/2\) 的 surrogate circuit。作者分别建立特征方程，并用 Jury criterion 求稳定参数域。[pdf:E03](_evidence/E03-p003-two-level-constraints.png) [pdf:E05](_evidence/E05-p005-best-damped-three-level.png) [pdf:E06](_evidence/E06-p006-feasible-space-relationships.png)
5. **选 best-damped 参数。** 两电平情形有两个 \(MMoP=0\) 的参数点，对应 Type I 和 Type II；三电平情形的三个极点无法同时为零，作者数值求得近似最优点 \(\alpha_{\mathrm{on}}=-5.04Y_{\mathrm{sw}},\beta_{\mathrm{off}}=-0.39\)。论文的表 II 还把这三组 G-ADC 参数与 backward Euler / trapezoidal L/C-ADC 放在同一参数空间中，显示 best-damped 点不落在 L/C-ADC 的可调线上。[pdf:E05](_evidence/E05-p005-best-damped-three-level.png) [pdf:E06](_evidence/E06-p006-feasible-space-relationships.png) [pdf:E07](_evidence/E07-p007-summary-platform.png)
6. **运行每个 1 μs 实时步。** FPGA 依次完成开关状态判断、历史电流、节点注入电流、节点电压、支路电压与电流计算；PWM 也在 FPGA 上。状态改变的第一步调用 HCRI，后续按普通历史源递推。[pdf:E08](_evidence/E08-p008-fpga-flow-hcri.png) [pdf:E09](_evidence/E09-p009-case-setup-comparison.png)
7. **输出与闭环。** 计算出的支路量成为下一步历史输入，也作为 measured signals 返回实时 CPU / 外部控制器；控制器产生调制信号再驱动下一轮 PWM 和开关状态。[pdf:E08](_evidence/E08-p008-fpga-flow-hcri.png)

这个 pipeline 的关键计算收益是：状态变化只触发历史源更新，不触发矩阵重构。它不是“没有状态”，而是把状态放进支路历史源；也不是“物理损耗模型”，而是以理想开关响应为目标的数值代理。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从固定导纳到历史源

任一开关支路在当前步满足

\[
I(t)=Y_{\mathrm{sw}}U(t)-I_h(t).
\]

G-ADC 不再要求 \(I_h\) 必须来自某个具体 L/C/R 电路，而写成一阶历史递推

\[
\begin{aligned}
I_{h,\mathrm{on}}(t)&=\alpha_{\mathrm{on}}U(t-\Delta t)+\beta_{\mathrm{on}}I(t-\Delta t),\\
I_{h,\mathrm{off}}(t)&=\alpha_{\mathrm{off}}U(t-\Delta t)+\beta_{\mathrm{off}}I(t-\Delta t).
\end{aligned}
\]

这里 \(Y_{\mathrm{sw}}\) 是网络在当前步“看到”的固定导纳，\(\alpha\) 与 \(\beta\) 决定上一步电压、电流如何折算成当前历史注入。固定 \(Y_{\mathrm{sw}}\) 保住矩阵结构，四个系数则提供独立整形暂态的自由度。[pdf:E03](_evidence/E03-p003-two-level-constraints.png)

### 6.2 稳态约束为什么只固定两个系数

ON 稳态要求 \(U(t)=U(t-\Delta t)=0\)，但电流可保持任意常值。代入支路式，要使任意电流都成立，必须有 \(\beta_{\mathrm{on}}=-1\)。OFF 稳态要求 \(I(t)=I(t-\Delta t)=0\)，但电压可为任意常值，因此必须有 \(\alpha_{\mathrm{off}}=Y_{\mathrm{sw}}\)。[pdf:E04](_evidence/E04-p004-poles-stability.png)

这两个条件保证最终落点像理想开关，却没有规定“多快到达”。暂态速度由 \(\alpha_{\mathrm{on}}\) 和 \(\beta_{\mathrm{off}}\) 控制。

### 6.3 用极点把“虚拟损耗”变成阻尼设计

对互补工作的半桥基本单元，作者得到二阶特征多项式

\[
P(z)=Y_{\mathrm{sw}}(z-1)^2+(z+\beta_{\mathrm{off}})(Y_{\mathrm{sw}}z-\alpha_{\mathrm{on}}).
\]

Jury criterion 给出极点位于单位圆内的参数不等式；作者用

\[
MMoP=\max(|p_1|,|p_2|)
\]

度量最慢衰减模态。直观上，每一步误差大致乘以相应极点；最大极点模越接近零，换相留下的虚拟电压、电流误差越快消失。[pdf:E04](_evidence/E04-p004-poles-stability.png)

两电平的两个最优点使两个极点都为零，对应

\[
\begin{aligned}
\text{Type I:}\quad
I_{h,\mathrm{on}}&=(-1-\sqrt 2)Y_{\mathrm{sw}}U_{k-1}-I_{k-1},\\
I_{h,\mathrm{off}}&=Y_{\mathrm{sw}}U_{k-1}+(1-\sqrt 2)I_{k-1};\\
\text{Type II:}\quad
I_{h,\mathrm{on}}&=(-1+\sqrt 2)Y_{\mathrm{sw}}U_{k-1}-I_{k-1},\\
I_{h,\mathrm{off}}&=Y_{\mathrm{sw}}U_{k-1}+(1+\sqrt 2)I_{k-1}.
\end{aligned}
\]

作者把它们称为 best-damped G-ADC。注意，“极点为零”描述的是所建零输入离散系统；真实换相仍受初态影响，因此实现中还使用 HCRI，实验文字报告剩余误差在两个步内衰减。[pdf:E05](_evidence/E05-p005-best-damped-three-level.png) [pdf:E09](_evidence/E09-p009-case-setup-comparison.png)

三电平 surrogate circuit 形成三阶系统，但只有 \(\alpha_{\mathrm{on}},\beta_{\mathrm{off}}\) 两个暂态自由度，不能令三个极点同时为零；论文据此数值寻找最小平均极点模，给出近似点 \(\alpha_{\mathrm{on}}=-5.04Y_{\mathrm{sw}},\beta_{\mathrm{off}}=-0.39\)。[pdf:E05](_evidence/E05-p005-best-damped-three-level.png) [pdf:E06](_evidence/E06-p006-feasible-space-relationships.png)

### 6.4 与外部系统解耦的真实条件

作者在附录中把外部等效电感和直流侧平滑电容的离散导纳近似为

\[
Y_{L_{\mathrm{eq}}}\approx\frac{\Delta t}{L_{\mathrm{eq}}},\qquad
Y_{C_{\mathrm{sm}}}=\frac{C_{\mathrm{sm}}}{\Delta t}.
\]

要把电感看作近似恒流源、把电容看作近似恒压源，需要

\[
\frac{\Delta t}{L_{\mathrm{eq}}}\ll Y_{\mathrm{sw}}\ll\frac{C_{\mathrm{sm}}}{\Delta t}.
\]

所以“参数独立于外部系统”不是无条件结论，而是一个尺度分离结果：必须存在足够宽的 \(Y_{\mathrm{sw}}\) 区间。论文明确说，如果所分析拓扑没有电感，本文推导的可行域和 best-damped 点将不再适用。[pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

## § 7 — 实验设计与结论

### 问题 1：best-damped 参数是否真的减少换相暂态？

作者在 NI-PXIe 平台上构建三相 VSC，比较 Type I G-ADC、按 RTDS 方法优化的 L/C-ADC，并以 PSCAD/EMTDC 的 two-value-resistor 模型作离线基准。测试系统报告的参数为：直流电压 750 V，交流电网 RMS 220 V，LC 滤波电感 1.5 mH、电容 50 μF，直流侧平滑电容 4000 μF，变压器与线路等效电感 2.3 mH，PWM 载波 10 kHz，\(P_{\mathrm{ref}}=40\) kW、\(Q_{\mathrm{ref}}=0\)。[pdf:E09](_evidence/E09-p009-case-setup-comparison.png)

论文报告：优化 L/C-ADC 在换相后仍有明显暂态误差，而 best-damped G-ADC 的初始误差较小并在两个步内衰减；其波形更接近 PSCAD 基准，虚拟能量损耗也更小。[pdf:E09](_evidence/E09-p009-case-setup-comparison.png) Fig. 12 直接显示三种模型的开关电压、电流、功率损耗和累计能量损耗趋势；本卡不从曲线估读未印出的精确数值。[pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png)

### 问题 2：高载波频率下优势是否保留？

作者比较了不同载波频率与 1 μs / 0.5 μs 步长下的 virtual power loss ratio，并展示 40 kHz、100 kHz 的开关电压波形。论文的文字结论是：L/C-ADC 的虚拟损耗在低频段近似随载波频率增长，缩小步长能缓解但加严实时约束；best-damped G-ADC 的损耗维持在很小的量级。[pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png) 这支持“降低虚拟损耗”的 claim，但 Fig. 14 不是统计试验，本卡不把曲线点估读为精确百分比。

### 问题 3：同一组参数对运行点和外部参数是否不敏感？

作者把有功参考从基准 40 kW 改为 20 kW 和 60 kW；又分别把外部电感 \(L_{\mathrm{ex}}\) 与平滑电容 \(C_{\mathrm{sm}}\) 改为原值的 0.1 倍和 10 倍。Fig. 15-16 显示 best-damped G-ADC 在这些测试下仍维持接近理想的开关波形，而 L/C-ADC 的虚拟损耗明显。[pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png) 这是对有限扫描范围的经验支持，不等于证明对任意外部系统均不敏感。

### 问题 4：方法能否扩展到三电平 NPC？

作者用 phase-disposition PWM 仿真三电平 NPC。Fig. 17 的输出电压与输入电流比较表明，best-damped G-ADC 的换相初始误差更小、衰减步数更少；作者据此认为该方法在三电平开关建模中也优于优化 L/C-ADC。[pdf:E11](_evidence/E11-p011-three-level-results.png)

### 问题 5：能否实时执行并进入 HIL？

论文给出两电平与三电平的初步 HIL 示波器截图，G-ADC 波形的换相振荡明显小于 L/C-ADC；但作者自己称这是 preliminary test，因此它证明的是平台连通性与趋势一致性，不是完整控制器认证。[pdf:E11](_evidence/E11-p011-three-level-results.png) [pdf:E12](_evidence/E12-p012-hil-waveforms.png)

在 1 μs 目标步长下，表 IV 报告 FPGA 平均执行时间：L/C-ADC 为 0.463 μs，G-ADC 为 0.475 μs，均满足实时要求；G-ADC 多 0.012 μs。表 V 报告 G-ADC 相比 L/C-ADC 使用 10.5% 对 10.2% 的 flip-flops、20.0% 对 19.0% 的 LUT、相同的 11.4% Block RAM，以及 13.7% 对 10.2% 的 DSP48 slices。作者据此称其计算代价“几乎相同”；更谨慎的表述是：在这块 FPGA 和该实现规模下，增加量没有破坏 1 μs deadline，但 DSP 占用的相对增幅并非为零。[pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

## § 8 — Take-aways

### 5 句话

1. G-ADC 把开关模型的本质接口识别为固定导纳与历史电流源，从而保留预存节点矩阵这一实时计算优势。[pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png)
2. 它直接设计历史源递推的稳态与极点，而不再受 L/C-ADC 虚拟电感、电容的充放电动态束缚。[pdf:E04](_evidence/E04-p004-poles-stability.png)
3. 两电平存在两个零极点的 best-damped 参数点，三电平则只有数值求得的近似最优点。[pdf:E05](_evidence/E05-p005-best-damped-three-level.png) [pdf:E06](_evidence/E06-p006-feasible-space-relationships.png)
4. 仿真与初步 HIL 表明，它在高载波频率、不同运行点和有限外部参数扫描中比优化 L/C-ADC 产生更小的换相误差与虚拟损耗。[pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png) [pdf:E12](_evidence/E12-p012-hil-waveforms.png)
5. 这些结论依赖拓扑可分解、互补开关和外部 L/C 与开关暂态时间尺度分离，不能外推到没有电感或复杂非线性器件行为的系统。[pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

### 3 句话

1. 论文把固定导纳开关模型从“挑 RLC 元件”提升为“在稳定域内设计历史源极点”。[pdf:E02](_evidence/E02-p002-lc-adc-g-adc.png) [pdf:E04](_evidence/E04-p004-poles-stability.png)
2. 在所测 VSC、NI-PXIe 和 1 μs 步长下，G-ADC 明显降低虚拟暂态，同时仍在 deadline 内完成计算。[pdf:E09](_evidence/E09-p009-case-setup-comparison.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)
3. 它最值得保留的思想是“固定网络接口、整形内部历史”，最需要警惕的边界是外部系统并不总能被当作慢变量。

### 1 句话

G-ADC 用稳定性约束下的历史电流源递推替代虚拟 L/C 储能，在不改变节点矩阵的前提下让开关误差更快衰减，但其通用性取决于明确的拓扑与时间尺度假设。[pdf:E04](_evidence/E04-p004-poles-stability.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

## § 9 — 最脆弱的假设

最脆弱的假设是：外部滤波电感和直流侧平滑电容在开关模型暂态期间足够“慢”，所以可分别近似为恒流源和恒压源，并让开关基本单元与外部系统解耦。数学上，这要求存在
\(\Delta t/L_{\mathrm{eq}}\ll Y_{\mathrm{sw}}\ll C_{\mathrm{sm}}/\Delta t\)
的宽可行区间；拓扑还必须能分解为论文分析的互补半桥或三电平 surrogate unit。[pdf:E03](_evidence/E03-p003-two-level-constraints.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

如果 \(L_{\mathrm{eq}}\) 太小、\(C_{\mathrm{sm}}\) 太小、步长太大，或者没有电感，这个区间会变窄甚至消失。此时外部网络动态进入作者原本消去的特征方程，同一组 \(\alpha_{\mathrm{on}},\beta_{\mathrm{off}}\) 不再保证原有极点位置，“参数与外部系统无关”这一核心收益随之失效。论文只扫描了 \(L_{\mathrm{ex}}\) 与 \(C_{\mathrm{sm}}\) 的 0.1 倍到 10 倍，并在附录明确承认无电感拓扑不适用；因此它给出了合理性与有限经验支持，但没有展示逼近可行区间边界时的失效曲线。[pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

## § 10 — 最小复现实验

一周内最值得复现的不是整套 NI-PXIe，而是“极点整形是否直接转化为更小虚拟损耗”。

1. 用固定 1 μs 步长实现 Fig. 3 的半桥离散基本单元，分别编码优化 L/C-ADC、Type I G-ADC，以及关闭/开启 HCRI 两种初态策略。网络求解可以先在 CPU 上完成，但 ON/OFF 必须共用同一个 \(Y_{\mathrm{sw}}\)。[pdf:E03](_evidence/E03-p003-two-level-constraints.png) [pdf:E09](_evidence/E09-p009-case-setup-comparison.png)
2. 采用论文三相 VSC 的核心参数，至少保留 750 V 直流侧、1.5 mH / 50 μF LC 滤波器、4000 μF 平滑电容与 10 kHz PWM；再增加 40 kHz 和 100 kHz 两个压力点。[pdf:E09](_evidence/E09-p009-case-setup-comparison.png) [pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png)
3. 每次换相记录开关电压、电流、误差衰减步数，并按论文定义计算六个开关总虚拟功率损耗除以变换器输入功率的比值。不要从论文图中抄数，而是对自己的时域数据积分。[pdf:E09](_evidence/E09-p009-case-setup-comparison.png) [pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png)
4. **支持 claim 的结果：** Type I 的换相误差在所有三个载波频率下均在约两个步内衰减，virtual loss ratio 对载波频率的增长显著弱于 L/C-ADC；关闭 HCRI 后初始峰值变大，但后续衰减速度仍由极点决定。
5. **反驳 claim 的结果：** 在相同固定导纳、步长和初态处理下，Type I 并未更快衰减，或其 virtual loss ratio 随载波频率增长与 L/C-ADC 同量级。这样的结果应先检查式 (17) 的符号、history-current 方向和换相第一步的重初始化，再判断理论或实现是否失败。

这个实验把“极点”“初态”和“累计虚拟损耗”三者分开，足以验证论文最核心的因果链，而不需要先复刻全部 FPGA 资源映射。

## § 11 — 最强反例设计

最强反例不是再换一个普通运行点，而是有意让时间尺度分离区间坍塌。构造一个两电平变换器族，保持开关基本单元与控制不变，连续减小串联/滤波电感 \(L_{\mathrm{eq}}\)、减小平滑电容 \(C_{\mathrm{sm}}\)，直到对任何可接受 \(Y_{\mathrm{sw}}\) 都无法同时满足
\(\Delta t/L_{\mathrm{eq}}\ll Y_{\mathrm{sw}}\ll C_{\mathrm{sm}}/\Delta t\)；再加入没有独立电感的拓扑端点。[pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

对每个点固定使用论文的 Type I 参数，测量完整网络离散系统的实际谱半径、换相误差衰减、virtual loss ratio 与节点解误差，并与“把外部网络一起纳入极点设计”的模型比较。如果论文的同一组 best-damped 参数在区间坍塌前就明显漂移，说明外部系统独立性比作者展示的 0.1-10 倍扫描更脆弱；如果到无电感端点仍表现良好，则反而会挑战附录给出的适用边界。[pdf:E10](_evidence/E10-p010-loss-ratio-external-parameters.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

还可以把互补开关假设作为第二层攻击：加入 dead time、二极管自然换相、同时关断区间和器件非线性损耗。论文结论只针对理想化开关代理，且作者明确把 actual switch power loss 与其他非线性列为未来工作；若在这些状态下 HCRI 选错历史分支，快速阻尼可能压低的是错误目标，而不是提高物理保真度。[pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

## § 12 — Follow-up Research Idea

**候选想法：固定端口契约下的自动离散开关模型综合。** 这只是从本文局限出发的候选研究方向；本卡没有充分检索相关工作，不声称 novelty。

**(a) 未满足需求。** 本文需要人为把拓扑化成半桥或三电平 surrogate，再手推低阶特征方程；复杂拓扑、无电感端口、dead time、自然换相和实际器件损耗仍不在模型内。[pdf:E06](_evidence/E06-p006-feasible-space-relationships.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

**(b) 可能的研究价值。** 把问题重新定义为：给定一个必须保持不变的网络端口导纳 \(Y_{\mathrm{port}}\)，自动综合一个有限阶 history-source state machine，使其在指定外部阻抗集合与全部合法开关事件上同时满足稳定性、被动性、误差和实时预算。这样评价对象不再是某个拓扑的一对经验系数，而是一个可验证的端口契约。

**(c) 可借鉴的方法。** 可以借鉴 robust control 的 polytopic uncertainty、passivity / dissipativity certificate，以及 model-order reduction 的受约束 realization。外部电路不再被完全消去，而被表示为一个有界导纳集合；综合器寻找在该集合内都稳定的历史源递推。如果还要拟合实际损耗，可把器件数据只用于拟合内部源项，同时以解析约束锁住固定导纳、稳定性和能量耗散方向，避免黑箱模型破坏实时求解结构。

**(d) 第一个可证伪实验。** 训练或综合时只使用普通半桥与论文的 \(0.1-10\) 倍 L/C 范围，测试时给出无独立电感、dead time 和自然换相的未见拓扑。只要出现端口不被动、节点系统不稳定、1 μs deadline 失守，或相对器件级离线基准的换相能量误差没有优于固定 Type I，核心想法就被否证。论文的 FPGA 流程与表 IV-V 可作为延迟、LUT、DSP 的第一组预算基线。[pdf:E08](_evidence/E08-p008-fpga-flow-hcri.png) [pdf:E13](_evidence/E13-p013-timing-resources-conclusion-appendix.png)

**(e) 与本文的实质区别。** 本文是在预先选定的低阶拓扑单元上求 best-damped 系数；候选方向则把“固定导纳接口”提升为可验证契约，在一组外部网络和事件上联合综合递推阶次、系数与能量约束。研究目标从“让某个理想开关代理的极点尽量小”变成“在实时预算内保证跨拓扑端口行为的稳定、耗散与保真”。
