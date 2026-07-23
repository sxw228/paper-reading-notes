# On Modeling Depths of Power Electronic Circuits for Real-Time Simulation - A Comparative Analysis for Power Systems

- corpus order：39
- Zotero key：DWXFPT5X
- canonical slug：`carne-modeling-depths-power2022`
- 作者：Giovanni De Carne, Georg Lauss, Mazheruddin H. Syed, Antonello Monti, Andrea Benigni, Shahab Karrari, Panos Kotsampopoulos, Md. Omar Faruque
- 年份 / 出处：2022 / *IEEE Open Access Journal of Power and Energy*
- DOI：`10.1109/OAJPE.2022.3148777`
- 唯一内容真相：`_source.pdf`
- PDF SHA-256：`8e4aa52577e517cbea0d9e77cfaec6ae15989e92d6bc5f3b23afa85dec1d30c7`
- 证据约定：`[pdf:E..]` 对应 `_evidence/` 下同 ID 开头的 PNG；物理页从 PDF 首页按 1 开始。

## § 1 — 研究问题与重要性

这篇论文处理的不是“怎样把电力电子模型做得越细越好”，而是更实际的决策问题：面向具体电力系统研究，应保留变流器的哪些物理与控制层级，才能在结果可信的同时满足数字实时仿真的固定时间预算。作者把这个矛盾明确为模型准确度、计算时间和执行硬件之间的 trade-off，并用 CPU 与 FPGA 两类执行路径讨论其工程后果。[pdf:E01]

这个问题重要，是因为新能源并网使电网从机电主导转向电力电子主导；与此同时，实时仿真要求每个时间步都必须在墙钟时间内完成。过深模型可能 overrun，无法实时运行；过浅模型则可能删掉恰好决定暂态稳定性的状态。论文最有价值的地方，是把“研究现象的时间尺度”放到选模入口：频率调节只涉及少数慢控制环，而低电压穿越、器件故障和寄生参数驱动的现象会要求 DC-link、开关状态或更小时间步。[pdf:E02][pdf:E09]

## § 2 — 前人工作与不足

按论文自己的 literature framing，已有工作已经分别覆盖三类知识：通用电力系统实时仿真综述、功率电子实时求解方法，以及针对 frequency regulation 或 fault ride through（FRT）的具体模型。频率调节研究往往使用静态或简化动态模型，因为主要动态低于数 Hz；FRT 文献则从线性化 DFIG 模型一直延伸到 MMC 或通用 VSC 的全开关模型，所需深度随研究对象而变。[pdf:E03]

不足不在于“没有模型”，而在于缺少把应用、模型深度、误差和实时计算代价放在同一决策框架中的比较。桌面离线仿真可以用更长计算时间换细节，实时仿真却必须预先判断哪些状态可以删；同时，CPU 与 FPGA 的并行方式和延迟特性不同，导致同一模型结构在两种平台上的可行性并不相同。[pdf:E02][pdf:E05] 论文因此不是再发明一个 converter model，而是建立一套面向选模的比较基准。不过，这套比较仍以更高复杂度模型而非实测波形作为主要准确度参照，这是后文最需要警惕的边界。[pdf:E03]

## § 3 — 重建作者的思考路径

可以把作者的出发过程重建为四步。第一，实时求解器的硬约束是每个步长内算完，因此系统规模与单个模型复杂度都会消耗预算；在大系统里，限制往往来自 converter 数量，而不只是单个 converter 的细节。[pdf:E02] 第二，变流器由功率级、DC-link、滤波器、PLL、内外控制环和能量源组成，不同现象只“看见”其中部分时间尺度，所以模型深度应按观测现象而不是按元件清单决定。[pdf:E02][pdf:E04] 第三，需要一个可重复的误差尺度，把浅层模型的波形与更高层模型比较，同时记录运行时间。[pdf:E03] 第四，选两个刻意拉开时间尺度的场景：慢的 primary frequency regulation 与快的 FRT，再增加 converter 数量观察 scaling，由此把“够不够准”和“跑不跑得动”同时落到数据上。[pdf:E02][pdf:E06][pdf:E08]

这条路径不依赖论文最后给出的推荐表：即使不知道作者的结论，一个研究者也会先按控制带宽和储能状态判断必要模型，再用任务相关波形误差与 worst-case execution time 检查选择。论文的贡献，是把这一直觉做成五级模型与实验对照。

## § 4 — 核心 Intuition

核心 intuition 是：模型深度不是模型本身的固定品质，而是“这个研究问题需要看见哪些动态”的函数。慢现象只需保留慢控制与功率交换，快速大扰动则必须保留 DC-link 能量和开关行为；任何被删掉的状态都可能让仿真表现得更稳定，却只是因为它失去了真实的失稳通道。[pdf:E04][pdf:E07][pdf:E08] 在此基础上，CPU/FPGA 不是简单的快慢之分，而是决定多细的模型能否在实时步长内执行。[pdf:E05]

## § 5 — 具体方法与完整 Pipeline

作者把同一个 grid-following converter 逐层简化为五类模型，并保持从浅到深的明确关系。[pdf:E04]

1. **Model (a)**：用一阶等效电流源表示 converter，时间常数为 \(T_{eq}\)；无 PLL，需要仿真器提供全局角度。
2. **Model (b)**：加入 PLL 与 current controller，功率参考被转换为电流参考；外层 power controller 在所观察的快速时间窗内被视为近似静态。
3. **Model (c)**：再加入 power controller，但忽略 DC-link 动态；它隐含的前提是 DC capacitor 足够大，或扰动足够小，使 AC/DC 两侧可解耦。
4. **Model (d)**：加入 DC voltage controller 与 DC-link 储能，但以一个 switching period 内的平均电压源代替开关器件，PWM block 被省略。
5. **Model (e)**：保留 switching elements、filter、DC-link 与全部控制环，是本文比较中的最高深度模型。[pdf:E04][pdf:E05]

以 0.3 p.u. 的三相电压跌落为例，完整 pipeline 是：给定 400 V、50 Hz 理想三相网和相同控制参考；故障前 converter 稳态运行；在 0.3 s 附近施加 100 ms 的深度电压跌落；模型根据各自保留的状态推进 current/power/DC-link 控制；输出 active power、reactive power 与 DC voltage；最后比较波形与稳定性。[pdf:E06][pdf:E07] Model (e) 会显式产生 switching ripple，Model (d) 仍能看到 DC capacitor 被抽空，二者都在深度跌落下越出 linear control region 并失稳；Model (c) 因为没有 DC-link 状态，看不到能量耗尽，反而“尝试恢复”初始功率。[pdf:E07][pdf:E08] 这个例子说明 pipeline 的关键输出不是一条更平滑的曲线，而是模型是否保留了研究所需的失稳机制。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文用相对 two-norm error 衡量模型 \(J\) 与更高深度模型 \(J+K\) 的整段波形差异：

\[
E^J =
\frac{\left\|x_i^J-x_i^{J+K}\right\|_2}
{\left\|x_i^{J+K}\right\|_2}
=
\frac{\sqrt{\sum_{i=1}^{N_s}\left(x_i^J-x_i^{J+K}\right)^2}}
{\sqrt{\sum_{i=1}^{N_s}\left(x_i^{J+K}\right)^2}} .
\]

这里 \(x_i\) 是第 \(i\) 个时间点的电气量，\(N_s\) 是样本数。分子把两个波形逐点差值的能量累加，分母用高深度波形的能量归一化，因此 \(E^J\) 可以跨信号幅值比较；作者用“小于 1%”举例说明何时继续加深模型可能只增加计算成本，但 1% 是示例阈值，不是经实验建立的通用安全界限。[pdf:E03]

Model (d) 的第二个关键公式，是在一个 switching period \(T_s\) 上对开关函数求平均：

\[
\bar v(t)=\frac{1}{T_s}
\int_{t-T_s/2}^{t+T_s/2}S_{1,\ldots,n}(\tau)V_{dc}\,\mathrm d\tau .
\]

\(S_i\in\{0,1\}\) 表示各 semiconductor 的开关信号，\(V_{dc}\) 是 DC-link voltage。直观上，积分把一个周期内高频的开/关电压替换成平均输出，因此保留了慢尺度的功率与 DC-link 能量交换，却主动删除 switching ripple 和器件级事件。[pdf:E04] 这也解释了为何 Model (d) 在 FRT 中可能与 switching Model (e) 的平均趋势接近，却不能用于 converter fault current：平均化已经去掉了器件 blocking 与瞬时开关路径。[pdf:E10]

## § 7 — 实验设计与结论

- **问题：慢的 primary frequency regulation 是否需要深模型？** 实验把各模型接到 400 V、50 Hz 理想三相网，比较 frequency 与 active power。结果是 Model (a)–(d) 的动态几乎重合，Table 2 中 Model (d) 与 Model (c) 的相对 two-norm error 为 0.10%；对这类慢现象，简化模型能保留主要行为。[pdf:E06]
- **问题：FRT 是否要求 DC-link 与 switching 细节？** 实验先施加 0.7 p.u.、100 ms 的电压跌落，再施加 0.3 p.u.、100 ms 的更深跌落。0.7 p.u. 时 Model (d)/(e) 的平均动态相近，Model (c) 的暂态更过阻尼且幅值偏低；0.3 p.u. 时 Model (d)/(e) 因 DC voltage 下降而失稳，Model (c) 却因删除该状态而给出表面恢复。[pdf:E06][pdf:E07][pdf:E08] 答案不是“越深越稳定”，而是深模型暴露了浅模型隐藏的失稳。
- **问题：模型深度如何随系统规模影响实时计算？** 实验在 OP4510/RT-LAB 上对每次仿真抽取 100 个连续时间步，统计 execution time，并把最多 15 个 converter 通过 0.1 Ω 支路并联；单个 Model (e) 的归一化基准执行时间是 2.61 μs。[pdf:E08] Model (a) 最省计算，Model (b)–(d) 随数量增长的差异很小，Model (e) 在少数并联 converter 后已呈显著非线性增长；因此全开关 CPU 模型的可扩展性最差。[pdf:E08][pdf:E09]

论文据此给出的应用表是：frequency regulation 可用 A–C；reactive power provision 用 B–C；grid forming 与 islanding 用 C–D；FRT 用 D–E；converter faults 只推荐 E。[pdf:E10] 这是基于本文场景的 guideline，不是对所有拓扑、控制器和电网强度的普适定理。

## § 8 — Take-aways

**5 句话：** 模型深度应由待研究动态决定，而不是由“可实现的最高细节”决定。频率调节这类慢现象可以用浅模型节省大量计算。FRT 会让 DC-link 能量状态成为决定稳定性的变量。删除 DC-link 可能产生“看似恢复、实际漏掉失稳”的假正确结果。[pdf:E07][pdf:E08] CPU 适合灵活的系统级研究，FPGA 则在亚微秒步长、高 switching frequency 或高度并行求解中更有优势，但开发成本与资源边界更高。[pdf:E05][pdf:E09]

**3 句话：** 先确定研究现象的最快关键动态，再决定必须保留的 converter 状态。随后同时验证波形误差与 worst-case execution time，而不能只看仿真能否启动。最后把“稳定得更好”视为待解释现象，因为它可能来自删掉了真实失稳机制。

**1 句话：** 最好的实时模型不是最细或最快的模型，而是在时间预算内仍保留目标现象因果链的最浅模型。

## § 9 — 最脆弱的假设

最脆弱的假设是：**模型深度的单调增加能提供足够可靠的“真值代理”，从而可用更高深度模型评估更浅模型。** 论文的 \(E^J\) 直接把 \(J+K\) 当作参照，但没有用硬件波形或独立实验真值为全部模型排序闭环；更高细节只意味着包含更多状态，不自动意味着参数、控制器 tuning、离散步长与器件模型更接近真实系统。[pdf:E03]

这个假设在多 converter、弱电网或控制交互显著时尤其可能失效。论文为了隔离 scaling，明确把第二个 test case 设计为避免 resonance 与 converter-controller interaction；因此它没有验证模型层级在最容易出现小信号/中频耦合的场景中仍保持同样排序。[pdf:E02] 基于证据的判断是：本文足以证明“在给定两个场景中，删掉 DC-link 会改变 FRT 结论”，但不足以证明五级 taxonomy 在所有电网阻抗、PLL bandwidth 和 controller tuning 下都能给出相同的应用推荐。

## § 10 — 最小复现实验

一周内最值得复现的不是整张 Table 4，而是“忽略 DC-link 会在深度 FRT 中隐藏失稳”这一条因果 claim。

1. 在同一求解环境实现 Model (c)、(d)、(e)；优先复用同一 current/power/DC-voltage controller，避免 tuning 差异成为替代解释。按 Appendix 使用 10 kW、230 V converter，750 V DC-link，\(L_c=0.85\) mH、\(R_c=0.1\,\Omega\)、\(L_g=0.5\) mH、\(R_g=0.1\,\Omega\)、\(C_f=5.5\,\mu\text{F}\)、\(R_f=2\,\Omega\)、\(C_c=5\) mF 与 \(T_{eq}=20\) ms。[pdf:E10]
2. 接到 400 V、50 Hz 理想网，设 active power 为 0.5 p.u.、reactive power 为 0 p.u.，依次施加 0.7 p.u. 与 0.3 p.u.、持续 100 ms 的三相电压跌落。[pdf:E06]
3. 记录 DC voltage、active/reactive power、是否越出 linear modulation region，以及每步 execution time。论文未在参数表中报告 switching frequency 与完整 solver time-step，因此复现时必须公开所选值并做至少三档步长敏感性检查，不能把单一数值误当成逐字复现。
4. **支持 claim 的结果：** 0.7 p.u. 下 Model (d)/(e) 平均趋势接近而 Model (c) 暂态偏差明显；0.3 p.u. 下 Model (d)/(e) 随 DC-link depletion 失稳，Model (c) 仍给出虚假的功率恢复。[pdf:E07][pdf:E08]
5. **反驳 claim 的结果：** 在相同参数、控制器和数值收敛检查下，Model (d)/(e) 的 DC voltage 不下降到失控区，或 Model (c) 与独立硬件/高保真参照同样准确。若只有 offline solver，这个实验只能复现动态机理，不能验证论文的 real-time execution-time claim。

## § 11 — 最强反例设计

最强反例是把论文刻意排除的 converter-controller interaction 放回来：在弱电网中并联多台参数略有偏差的 grid-following converter，系统扫描 short-circuit ratio、线路 \(R/X\)、PLL bandwidth、power-loop bandwidth 与 converter 数量，同时施加频率扰动和 FRT。[pdf:E02] 对每个工况并行运行 Model (a)–(e)，再用 switching reference 与 CHIL/PHIL 测量检查稳定边界、阻抗峰值、环流和 protection trigger。

攻击成立的判据是：论文推荐用于 frequency regulation 的 A–C 在慢功率波形上仍然接近，却把由 PLL/网阻抗耦合产生的振荡判成稳定；或者 Model (d) 在 FRT 上与 Model (e) 的平均功率相近，却错过器件 blocking 或保护动作。这会说明“按应用名称选深度”不够，真正决定深度的是应用内部最危险的交互机制。相反，如果跨上述扫描后，推荐表仍能预测最浅可信模型且硬件误差受控，论文的 guideline 才获得比现有两个理想化场景更强的外部有效性。

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty：从静态 model-depth taxonomy 转向“带在线可信度证书的自适应多保真实时仿真”。** 电力电子实时仿真的高影响工作通常不仅看算法新颖性，还看暂态保真、实时 deadline、硬件可实现性、跨工况稳定性与可复现实验；本文已经表明固定浅模型会在深 FRT 中隐藏 DC-link 失稳，也表明固定深模型会迅速吃掉 CPU scaling 预算。[pdf:E08][pdf:E09]

- **(a) 未满足需求：** 工程师在仿真前往往不知道某个扰动会不会激活被删掉的状态；固定选 A–E 只能在“总是太浅”和“总是太贵”之间押注。
- **(b) 研究价值：** 目标改为在每个时段维持一个可检验的误差/稳定性证书：平稳时运行浅模型，检测到 DC-link energy margin、PLL interaction indicator 或 residual 超界时，只提升相关 converter 的深度，并在风险解除后降级。这样研究问题从“哪一个模型最好”变成“怎样在实时预算内保证关键因果状态不会被静默删除”。
- **(c) 相邻领域工具：** 可借鉴 adaptive mesh refinement 的局部加密思想、hybrid systems 的 mode guard，以及 reduced-order modeling 的 residual-based error estimator；这里借用的是验证机制，不是把它们直接视为已有电力电子解法。
- **(d) 第一个证伪实验：** 在第 11 节的弱电网多 converter 场景下设定固定 CPU deadline；若 risk indicator 不能在 switching/硬件参照偏离前触发升阶，或升阶造成 deadline miss，核心想法即被证伪。
- **(e) 实质区别：** 本文为一个 study 预先选择固定 A–E；候选方向让模型深度成为受运行时证据驱动的局部状态，并把“误差不越界且不 overrun”作为共同验收。相关工作未在本任务中检索，因此这里只能作为由本文局限导出的研究候选，不能宣称尚无人完成。
