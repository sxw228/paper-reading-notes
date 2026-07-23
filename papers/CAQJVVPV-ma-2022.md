# Real-Time Simulation of Power System Electromagnetic Transients on FPGA Using Adaptive Mixed-Precision Calculations

- 作者：Xin Ma, Conghuan Yang, Xiao-Ping Zhang, Ying Xue, Jianing Li
- 出处：IEEE Transactions on Power Systems, Vol. 38, No. 4
- 年份：2022（在线发表；卷期版本为 2023）
- DOI：10.1109/TPWRS.2022.3199181
- Zotero key：CAQJVVPV

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文问的不是“FPGA 能否做 EMT 实时仿真”，而是更窄也更实际的问题：当仿真持续几十秒、模型里又有同步机这类旋转与反馈耦合部件时，传统全 Single-Precision 是否还足够；若不够，怎样以有限 FPGA 资源获得接近全 Double-Precision 的长期数值可信度。作者把矛盾放在三个同时成立的工程约束上：每个 EMT 步长必须按时完成，浮点误差不能随时间积累成相位漂移，FPGA 的 LUT、DSP、寄存器和布线资源又不能被全双精度迅速吃满。[pdf:E01](_evidence/E01-p001-abstract-introduction.png)

这个问题重要的物理原因是：EMT 仿真逐步推进电气状态和机电状态。同步机电角度一旦因舍入误差逐步偏移，Park transform 中的三角函数就会在错误相位上把 `abc` 与 `dq0` 量互相变换；错误随后进入电磁转矩、转速、控制器和下一步历史量，因而不再只是末位数字的微小差异。论文的价值在于把“精度”从全系统统一数据格式，改写成按子系统数值敏感性分配的硬件设计变量，并把这种分配落实到 pipeline、RAM 地址访问和时序控制上。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png) [pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png)

## § 2 — 前人工作与不足

论文列出的直接基线包括 Dommel 的 EMT 离散模型、Chen 与 Dinavahi 的 FPGA-based real-time EMTP、以及后续 FPGA 上的 MMC、输电线故障分类和变步长硬件仿真。作者概括的既有实现倾向于全 Single-Precision：它计算快、资源成本低，也足以让简单非旋转网络在短时间内与离线模型接近；离线 PSCAD、EMTP 和 MATLAB 则通常使用 Double-Precision。[pdf:E01](_evidence/E01-p001-abstract-introduction.png) [pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png)

不足不只是“Single-Precision 位数少”。IEEE 754 单精度的 fraction 为 23 bit，双精度为 52 bit；重复加法需要对阶、尾数相加、规格化和舍入，较小的增量可能不断丢失。作者用固定角增量 `Δδ = 0.0157` 的正弦迭代展示：初期误差很小，但 0.5 s 后开始明显失配，5 s 时正弦结果的绝对差约为 `0.04197`，文中概括为接近 4%。这说明仅看一个步长的局部误差，会漏掉长期相位状态的累积位移。[pdf:E03](_evidence/E03-p003-roundoff-tableI-eq14-eq15.png)

另一方面，全 Double-Precision 虽能保留更多耦合状态信息，却增加计算单元、存储和布线压力。已有 mixed-precision 数值算法说明“关键部分用高精度、其余部分用低精度”可能有效，但论文指出，在它所考察的 FPGA 同步机 EMT 场景中，Scheme 1B、2、3A、3B 这些具体硬件方案此前未见公开报告。这里的不足因此是一个跨层缺口：既缺少对“哪里真的需要双精度”的部件级证据，也缺少能在固定步长内运行的系统级硬件映射。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png)

## § 3 — 重建作者的思考路径

可以从作者之前已经掌握的模型与失败模式反推这条路径。

1. EMT 的 RLC 支路和输电线都可写成“本步端口量 + 上一步历史源”的递推；简单非旋转网络主要由加、减、乘和延时历史量构成。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png)
2. 同步机不同：电气方程、摆动方程、角度积分、Park transform、励磁、调速器、PSS 和 limiter 形成闭环。角度是持续累加的，三角变换又把角度误差转成坐标系误差。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png)
3. 因此，合理的第一步不是把整个网络都换成双精度，而是先做敏感性拆分：没有旋转耦合的网络是否仍可用单精度？只把角度更新换成双精度是否够？增加 Single-Precision iteration 能否补偿？[pdf:E03](_evidence/E03-p003-roundoff-tableI-eq14-eq15.png) [pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png)
4. 部件级比较若表明“只提高角度精度”仍会丢失转子、定子和控制器之间的完整耦合信息，那么精度边界就应扩大到整个 SG 子系统，而外部网络继续用单精度。这正对应 Scheme 3B。[pdf:E07](_evidence/E07-p007-sg-case-tableV-fig08-fig09.png) [pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png)
5. 最后，数值划分必须转成能综合的硬件：精度转换接口解决位宽边界，unit-level 与 module-level pipeline 处理不同数据通路，ordered/disordered address controller 处理不同内存访问规律，两个 FSM 保证每步的网络与同步机求解顺序。[pdf:E05](_evidence/E05-p005-pipeline-address-fig03-fig04.png) [pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png)

这条路径的关键不是先假定 mixed precision 一定好，而是用“简单网络 → 单机闭环 → 11-bus 系统 → 22-bus 系统”逐级寻找最小的高精度边界。

## § 4 — 核心 Intuition

核心 intuition 是：数值精度应跟随误差传播机制，而不是跟随“所有数据统一一种格式”的习惯。外部非旋转网络的单精度误差在本文工况中保持小，而同步机的角度积分、Park transform 和闭环控制会把舍入误差变成可累积的相位偏移，所以把整个 SG 子系统放在 Double-Precision、网络留在 Single-Precision，能保住关键状态又节省资源。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png) [pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png)

换成物理语言：真正需要保护的不是每个电压电流的最后几位，而是决定电气坐标系与机械转子位置关系的“相位记忆”。一旦这段记忆漂移，后面再做更多单精度迭代也无法把系统拉回正确轨道。

## § 5 — 具体方法与完整 Pipeline

作者比较五种实现：

- Scheme 1A：全 Single-Precision，无 iteration。
- Scheme 1B：全 Single-Precision，有 iteration。
- Scheme 2：全 Double-Precision。
- Scheme 3A：只有同步机角度相关计算用 Double-Precision，其余用 Single-Precision。
- Scheme 3B：整个 SG 与控制子系统用 Double-Precision，非旋转网络用 Single-Precision，并在边界双向转换。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png)

以 Kundur 4-machine 11-bus 系统中一次 `1.0–1.1 s` 的 bus 7 单相故障为例，Scheme 3B 的一个 EMT 步长可以按下面理解：

1. **输入与历史量**：读取输电线、变压器、RLC 支路、断路器和故障状态，以及上一时刻的历史电流源、同步机电气/机械状态和控制器状态。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png)
2. **Stage 1，Single-Precision**：计算不含 SG 响应的 open-circuit node voltage。相似的线性运算采用 unit-level pipeline；ordered RAM 直接用计数器访问，变长输电线等 disordered 数据则查预先生成的地址表。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png) [pdf:E05](_evidence/E05-p005-pipeline-address-fig03-fig04.png)
3. **精度边界**：把 `abc` 端口电压经 Floating-Point-to-Floating-Point IP 转为 Double-Precision，送入各台 SG。[pdf:E05](_evidence/E05-p005-pipeline-address-fig03-fig04.png)
4. **Stage 2，Double-Precision**：依次更新同步机预测量、governor 与 prime mover、电气与机械状态、PSS、excitation system，再经 Park transform 形成端口响应。反馈或复用计算单元较多的模块采用 module-level pipeline。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png) [pdf:E05](_evidence/E05-p005-pipeline-address-fig03-fig04.png)
5. **返回网络**：SG 输出转换回 Single-Precision，与外部网络组合，求解含 SG 响应的 node voltage，再更新输电线、变压器和 RLC 支路电流。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png)
6. **时序闭合**：FSM1 控制外部网络的 9 个状态，FSM2 控制 SG 的 9 个状态；`open_done` 和 `SG_done` 形成两者的握手。每个新步长全局计数器加一、局部时钟计数器归零，避免步骤间状态串扰。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png)
7. **输出**：在本步截止时间前得到节点电压、支路电流、同步机电磁/机械量和下一步历史状态。Kundur 案例中，Fig. 18 给出的 Scheme 3B 总执行时间为 `25.4 μs`，仿真步长为 `50 μs`。[pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png) [pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png)

论文没有报告运行时根据误差自动切换精度的机制。“Adaptive”在这里更接近依据部件敏感性预先划分精度，而不是在线自适应控制；这是基于 Fig. 2 和 Table II 的解释，不是作者单独定义的术语。

## § 6 — 核心数学推导

论文的数学核心不是一个新的求解定理，而是说明“历史递推 + 旋转坐标变换”为何会让局部舍入误差变成长期相位误差。

对 RLC 支路，梯形法离散后可写成 Norton companion 形式：

`i_RLC(t) = k1[v1(t)-v2(t)] + k2 I_RLC(t-Δt)`

`I_RLC(t-Δt) = k3[v1(t-Δt)-v2(t-Δt)] + k4 i_RLC(t-Δt)`。

也就是说，本步电流由本步端电压与历史源共同决定。输电线采用含传播时延 `τ` 的 history current source，物理上是在本端把对端较早时刻的行波影响作为等效注入。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png)

同步机的敏感环节是 Eq. (10) 的 Park matrix `P(θ)` 与 Eq. (11) 的角度更新：

`θ(t) = θ(t-Δt) + ω(t)Δt`。

角度每步累加，而 `P(θ)` 中包含相隔 `2π/3` 的 `sin`、`cos`。单精度若不断丢掉 `ωΔt` 的低位，`θ` 的误差不是独立噪声，而是会在后续所有坐标变换里保留。Eq. (5)–(9) 又把 `dq0` 电压、电流、磁链、机械转矩、电磁转矩、转速和上一时刻 history term 串成闭环，因此角度误差会进入下一步动力学。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png)

作者用 Eq. (15) 表示单精度累加：

`S_n = single(S_{n-1}+x_n) = (S_{n-1}+x_n)(1+ε_n)`，

其中 `ε_n` 由求和次序和舍入决定。这个式子本身没有给出全系统误差上界；它的作用是解释每一步都可能引入乘性扰动。Table I 再用固定角增量的数值实验表明，随着累计角度变大，单精度角度与正弦值逐渐偏离双精度参考。[pdf:E03](_evidence/E03-p003-roundoff-tableI-eq14-eq15.png)

Scheme 3A 只把 `θ` 相关块升为双精度，却仍让转子、定子和控制器的大部分闭环状态在单精度中传播；实验显示它可减小故障期间某些量的误差，但不能消除 start-up 后的相位问题。Scheme 3B 因而把高精度边界扩到完整 SG 子系统。这里是实验驱动的精度划分，不是由 Eq. (15) 严格推出的最优分区。[pdf:E07](_evidence/E07-p007-sg-case-tableV-fig08-fig09.png) [pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png)

## § 7 — 实验设计与结论

**问题 1：非旋转网络真的需要全双精度吗？** 作者在 5-bus RLC/变压器/输电线网络上，于 `11.5–12.5 s` 对 bus 4 施加单相故障，比较 Scheme 1A、Scheme 2 与 MATLAB。20 s 仿真中，两者电流绝对误差分别低于 `0.03%` 和 `0.01%`；全双精度额外使用 7 个百分点 LUT 和 10 个百分点寄存器，并引入 DSP 使用。答案是：在这一个主要由线性非旋转部件组成的案例里，Single-Precision 足够且更省资源。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png) [pdf:E07](_evidence/E07-p007-sg-case-tableV-fig08-fig09.png)

**问题 2：iteration 或局部双精度能否修复同步机相位漂移？** 单机模型包含 SG、励磁、PSS、governor 与外部负载，从 0 s 启动、10 s 达稳态，并在 `12–13 s` 对 bus 2 施加单相故障。作者比较 1A、1B、2、3A；Figs. 9–14 显示只有全 Double-Precision Scheme 2 避免了明显相位偏移。Scheme 1B 的额外 iteration 只能降低部分预测误差，Scheme 3A 只提高角度相关计算也不能保存整个机电闭环的信息。[pdf:E07](_evidence/E07-p007-sg-case-tableV-fig08-fig09.png) [pdf:E08](_evidence/E08-p008-sg-waveforms-fig10-fig13.png) [pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png)

**问题 3：完整 SG 双精度、外部网络单精度的 Scheme 3B 是否接近全双精度且节省资源？** 作者在单块 Virtex-6 ML605 上实现 Kundur 4-machine 11-bus 系统，100 MHz 主时钟、50 μs EMT 步长，bus 7 在 `1.0–1.1 s` 发生单相故障。Figs. 16–17 显示 Scheme 3B 与 Scheme 2 的波形接近；Table VI 中 LUT 从全双精度的 `87%` 降到 `60%`，DSP 从 `93%` 降到 `78%`，寄存器从 `35%` 降到 `29%`，memory 从 `9%` 降到 `6%`。答案是：在该模型和故障工况下，3B 保留了接近 Scheme 2 的动态结果，并显著释放资源。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png) [pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png)

**问题 4：能否扩到更大系统？** 作者把两个 11-bus 网络经输电线连接成 22-bus 系统，在同一 FPGA 上比较 Scheme 2 与 3B。Fig. 20 展示两种方案与 MATLAB 的同步机电流/转矩波形接近；论文还报告 3B 相对全双精度多留出 `15%` LUT 和 `13%` DSP 资源。答案只能限定为：这一特定 22-bus、8-machine 构造案例能够放入单板并运行；它没有证明任意更大网络或不同部件组合都能保持相同误差和时序裕量。[pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png) [pdf:E11](_evidence/E11-p011-conclusion-resources.png)

两个报告口径需要谨慎。Section IV 说“average error”按最大绝对误差除以最大幅值计算，这其实更接近 normalized peak error；Section C 与 Conclusion 对误差的 `2%/5%/3%` 概括也并非同一变量、同一统计口径。因而不能把“平均误差低于 3%”外推成所有信号、所有时间段的统一保证。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png) [pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png) [pdf:E11](_evidence/E11-p011-conclusion-resources.png)

## § 8 — Take-aways

**5 句话。**  
1. 长时 FPGA EMT 仿真中的关键风险不是单步舍入本身，而是角度积分与 Park transform 把误差积累成相位漂移。[pdf:E03](_evidence/E03-p003-roundoff-tableI-eq14-eq15.png)  
2. 论文案例中的简单非旋转网络对 Single-Precision 不敏感，没有必要为全部支路支付双精度成本。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png)  
3. 只增加单精度 iteration 或只把角度块改为双精度，都不足以保护同步机完整机电控制闭环。[pdf:E07](_evidence/E07-p007-sg-case-tableV-fig08-fig09.png) [pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png)  
4. Scheme 3B 以 SG/网络为精度边界，在 Kundur 案例中把 LUT 占用从 87% 降到 60%，同时保持与全双精度相近的波形。[pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png)  
5. 真正让算法成为实时硬件的是 pipeline、动态地址访问和双 FSM 时序，而不只是把变量类型改成 `float` 或 `double`。[pdf:E05](_evidence/E05-p005-pipeline-address-fig03-fig04.png) [pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png)

**3 句话。**  
精度应该放在会保存并放大相位记忆的子系统。Scheme 3B 证明这种静态分区在本文三类系统上能交换准确度与 FPGA 资源。它仍是一套案例驱动的工程规则，不是对任意 EMT 网络成立的误差保证。

**1 句话。**  
把双精度留给“会把末位误差变成物理相位错误”的闭环，把其余资源留给实时规模。

## § 9 — 最脆弱的假设

最脆弱的假设是：**高精度需求可以稳定地按“旋转 SG / 非旋转网络”这条部件边界局部化。** Scheme 3B 的成立依赖外部网络只把 `abc` 端口电压送入双精度 SG，而且网络侧的单精度误差不会显著改变零交越、开关事件、网络条件数或回馈到转子状态的扰动。[pdf:E04](_evidence/E04-p004-schemes-tableII-hardware-fig02.png) [pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png)

论文为该假设提供的证据是：5-bus 非旋转网络在 20 s 内的误差很小；Kundur 与扩展 22-bus 案例中，外部网络单精度、SG 双精度仍与全双精度接近。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png) [pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png) 但证据覆盖很窄：网络侧主要是 RLC、变压器和输电线，事件是单相故障；没有展示电力电子开关、大量 limiter/zero-crossing 位于网络侧、病态节点导纳矩阵、极端时间常数差异或更长于 20 s 的系统级运行。只要其中一种非旋转部件也会积累或放大舍入误差，3B 就会把它错误地留在 Single-Precision，核心资源-精度结论可能失效。这一段后半部分是基于论文覆盖范围的推断，不是作者已验证的失败。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 22-bus 平台，而是“精度边界必须覆盖整个 SG，而不只是角度块”这一核心 claim。

1. 按 Eq. (5)–(14) 实现一台带 governor、PSS、excitation 与 limiter 的同步机，采用论文 Fig. 8 的启动与 `12–13 s` 单相故障流程；同时实现 Scheme 1A、1B、2、3A、3B。参数若论文未完整给出，就使用一个公开标准同步机参数集，并明确这只能复现机制、不能复现原数值。[pdf:E02](_evidence/E02-p002-component-models-eq01-eq13.png) [pdf:E07](_evidence/E07-p007-sg-case-tableV-fig08-fig09.png)
2. 软件端强制使用 IEEE 754 `float32`/`float64`，同一步长、同一 lookup-table 或三角函数实现；记录 `θ`、`i_d`、`T_e`、`T_m`，以全 `float64` 为内部参考。
3. FPGA 端只综合 Park transform、摆动方程和一个代表性控制回路，测 LUT、DSP、寄存器、最大频率和单步 latency；不必先复现完整网络。
4. 支持 claim 的结果是：1A/1B/3A 在启动后出现持续可测的相位漂移，2 与 3B 不出现；同时 3B 的资源显著低于全双精度网络+SG 方案，并能在 50 μs 截止前完成。
5. 反驳 claim 的结果是：统一三角函数实现后 3A 已与 2/3B 等价，或相位差主要来自 lookup-table/实现不一致而不是闭环精度边界，或 3B 的转换与调度开销使它无法满足实时步长。

这个实验把“数值机制”和“硬件代价”分开测量，避免只凭重叠波形宣称成功。

## § 11 — 最强反例设计

最强反例不是再加更多同步机，而是构造一个**没有旋转部件、却具有强数值敏感性的网络**。例如建立一个含长延时输电线、相近大电流相消、极端参数比和带 zero-crossing/limiter 的电力电子等效支路；让节点导纳矩阵接近病态，并运行足够长时间。按 Scheme 3B 的分类，这个系统全部留在 Single-Precision，因为它没有 SG。

攻击步骤是：以全 Double-Precision 和高精度离线解为参考，逐步扫网络条件数、延时、故障清除角和阈值距离；观测节点电压、支路电流、事件时刻以及误差是否跨过 limiter 或开关阈值。若 Single-Precision 在一个网络侧事件上提前/延后触发，随后产生不可恢复的拓扑分叉，而 Double-Precision 没有，那么“非旋转网络可以安全使用单精度”就被直接推翻，Scheme 3B 的固定部件分类也不再是充分规则。论文的 5-bus 结果只证明一个线性、单相故障案例中误差很小，不能排除这个反例。[pdf:E06](_evidence/E06-p006-fsm-platform-5bus-tableIV.png)

另一个替代解释也应同时检查：论文把全双精度更好的结果归因于 mantissa 保留，但 Fig. 9–14 中残余差异也可能部分来自三角函数 lookup-table、精度转换或不同 pipeline 实现。让所有方案共享同一个高精度角度源、同一三角近似，再只改变闭环状态格式，可以判断相位漂移到底来自哪里。[pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png)

## § 12 — Follow-up Research Idea

**候选想法：从“按部件类型静态分精度”转向“按在线误差预算和事件风险动态分精度”。** 这不是声称已有 novelty 的结论；本任务没有做外部相关工作检索，因此只能作为证据约束的研究方向。

**(a) 未满足需求。** 论文的固定规则把 SG 视为高敏感、网络视为低敏感，但真实 EMT 系统中的敏感性可能随故障、控制饱和、网络条件数和开关事件迁移。需要一种能在错误变成相位漂移或事件分叉之前，识别“当前哪条计算链必须升精度”的机制。

**(b) 研究价值。** 在电力系统与实时仿真领域，高影响结果通常不仅要给出平均误差更小，还要同时证明：关键暂态不漏、固定 deadline 可满足、资源可扩展、不同网络与工况可复现。若能给出从局部浮点残差到端口状态/事件时刻误差的可计算界，并在 FPGA 上按界切换精度，就把经验分类提升为可审计的实时安全契约。

**(c) 可借鉴工具。** 可借鉴 mixed-precision iterative refinement、floating-point error analysis、interval/affine arithmetic，以及实时系统的 deadline-aware scheduling。具体实现可在每个子模块输出旁维护低成本 residual 或 shadow state；当残差、条件数代理或 zero-crossing 距离触发阈值时，把该计算链在未来若干步提升为 Double-Precision，再在风险消失后降回 Single-Precision。

**(d) 第一个证伪实验。** 同时运行论文的同步机案例和第 11 节的非旋转病态网络。若在线指标不能在输出误差或事件时刻分叉之前稳定预警，或者精度转换、双路径存储和调度开销让 50 μs deadline 失守，那么该想法即被证伪。论文现有 Scheme 3B 的 `25.4 μs / 50 μs` 时序可作为最初的开销预算基线。[pdf:E09](_evidence/E09-p009-phase-error-kundur-schedule-fig14-fig18.png) [pdf:E10](_evidence/E10-p010-kundur-22bus-tableVI-fig19-fig20.png)

**(e) 与本文的实质区别。** 本文先做离线部件敏感性判断，再固定为“SG 双精度、网络单精度”；候选方案把精度边界变成随数值状态和事件风险移动的受约束控制问题。它优化的也不再只是平均资源与波形误差，而是“在实时 deadline 内不发生未预警的数值事件分叉”。
