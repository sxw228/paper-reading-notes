# The Impact of Time Delays for Power Hardware-in-the-Loop Investigations

**作者**：Jana Ihrens、Stefan Möws、Lennard Wilkening、Thorsten A. Kern、Christian Becker [pdf:E01]

**出处**：Energies，14，3154 [pdf:E01]

**年份**：2021 [pdf:E01]

**DOI**：10.3390/en14113154 [pdf:E01]

**Zotero key**：ZPWPBDZZ

**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样把 PHiL 做得越快越好”，而是一个更实用的问题：在 Power Hardware-in-the-Loop（功率硬件在环，PHiL）中，simulator、通信接口、A/D 与 D/A 转换、power amplifier（功率放大器）和反馈测量分别引入多少延迟，这些延迟何时会损害精度、诱发不稳定，工程人员又该怎样按被研究现象的动态尺度选择平台与接口。作者在 PDF 物理页 2、Section 1 明确指出，PHiL 使用 fixed-time-step solver（固定步长求解器），系统各部分都会增加延迟；延迟可能降低精度、引起不稳定，甚至损坏设备，因此 simulator 与 amplifier 的时间特性必须按具体 investigation 匹配，而不是按单一“最高性能”标准选择 [pdf:E02]。

问题重要，是因为 PHiL 位于 pure simulation（纯仿真）和 full field test（完整现场测试）之间：它保留真实 Hardware Under Test（被测硬件，HUT），同时用可重复的 Rest of System（其余系统，ROS）仿真替代昂贵、危险或尚不存在的电网条件。论文在 PDF 物理页 1 的 Abstract 与 Introduction 说明，现场动态测试可能因故障工况稀少、成本、空间和安全约束而不可行；纯仿真则依赖高精度模型，计算开销大，简化还可能遗漏关键动态 [pdf:E01]。PHiL 因而很有价值，但它额外插入了闭环接口，若延迟处理不当，测试台自身产生的行为可能被误认为 HUT 的真实行为。

论文的工程价值在于降低两类错误。第一类是低估平台：用 PLC 或 microcontroller（微控制器）去承载过快、过复杂的模型，导致采样、计算或通信赶不上系统动态。第二类是过度配置：对秒级频率控制或分钟级电流耐久序列仍强制使用昂贵 RTS（real-time simulator，实时仿真器）和高速光纤链路。作者的目标是展示，只要 investigation 的时间常数和模型复杂度与平台性能相匹配，RTS、PLC 乃至 M-DUINO 都可能成为合格 simulator；真正需要匹配的是端到端延迟链和研究对象的动态，而不是设备标签 [pdf:E01][pdf:E02]。

## § 2 — 前人工作与不足

论文把已有路线分成 pure simulation、Controller Hardware-in-the-Loop（控制器硬件在环，CHiL）和 PHiL。Pure simulation 的优势是安全与可重复，但模型精度和计算时间之间存在直接冲突；CHiL 只交换低功率信号，PHiL 则通过 amplifier 向真实 HUT 施加功率，因此更接近完整硬件系统 [pdf:E01][pdf:E02]。已有 PHiL 工作已经认识到，插入 ROS-HUT 接口后，本来稳定的真实系统也可能在试验台上变得不稳定；amplifier 的有限带宽、量化误差、ROS 与测量延迟都可能参与这一过程，interface algorithm（接口算法）需要处理这些非理想性。论文还归纳了 linear amplifier、switched-mode amplifier 和同步发电机方案在功率、精度和延迟上的取舍 [pdf:E03]。

不足不在于“前人完全没研究延迟”，而在于已有讨论多围绕专用 RTS、高性能 amplifier、稳定化接口或特定实验平台，工程人员仍缺少一个从 investigation 时间尺度出发、可跨高端和低端 simulator 做选型的直观示例集。作者在 PDF 物理页 2、Section 1 明确把“用低性能设备作为 simulator，展示它们在 PHiL 中的潜力”作为相对现有活动的区别 [pdf:E02]。因此这篇论文更像 engineering design guide（工程设计指南）加实验性 case study，而不是新的 interface algorithm、统一稳定性理论或 FPGA 求解器架构。

这一定位也决定了它的上限：论文能够回答“在这三类任务中，哪种平台和通信链足够”，但不能仅凭这些结果证明“任何 PHiL 只要总延迟小于某个时间常数就一定准确稳定”。作者自己在 Section 2.2 已承认稳定性还取决于 interface algorithm、amplifier 动态和量化等因素 [pdf:E03]，后文却没有把这些因素纳入统一的闭环模型。

## § 3 — 重建作者的思考路径

可以把作者的思考路径逆向重建为五步。

第一步，现实电网测试既昂贵又危险，而且未来电网状态可能尚不存在，因此必须用 HIL 保留可重复性；但只做 pure simulation 又可能因模型简化遗漏真实 hardware dynamics（硬件动态）[pdf:E01]。

第二步，既然要把真实 HUT 接回 simulator，就必须通过 amplifier 完成功率接口并把测量反馈给 ROS。这个基本闭环由 simulator、D/A 或 digital link、amplifier、HUT、measurement 和回传组成，PDF 物理页 2 的 Figure 1 清楚展示了能量流与信息流的双向结构 [pdf:E04]。

第三步，新增闭环意味着每个计算周期、转换器、通信协议和 amplifier 都贡献相位滞后与离散化误差。CPU-based RTS 可以承载更复杂模型，但常见时间步长受限；FPGA-based simulation 可以进一步降低步长，却受可实现模型规模限制。PLC 又以 cyclic operation（循环扫描）更新 image table（映像表），输入输出只能在周期边界生效。与此同时，真实 amplifier 并非零延迟、无限带宽的理想器件 [pdf:E03]。

第四步，延迟的严重性不是绝对量，而取决于研究现象。对秒级 frequency deviation（频率偏差），毫秒级链路可能完全足够；对电磁暂态、高频谐波或快速闭环，微秒级差异就可能主导结果 [pdf:E02]。由此自然得到一个假设：平台选择应该从“最小需要解析的时间尺度”和“模型在该步长内能否算完”倒推，而不是默认 RTS。

第五步，为验证这个假设，作者用同一实验室搭建三组跨度很大的 case：PLC-analog 与 RTS-optical 的快速输出和 CPU load 对比；PLC + SCPI 的秒级 FCR/BESS 场景；M-DUINO 的分钟级高电流序列。TU Hamburg 的 PHiLsLab 允许 PLC 或 OPAL-RT RTS 通过 analog、SCPI 或 Aurora 接入 APS 22500 amplifier，再连接 HUT，PDF 物理页 4 的 Figure 3 给出了这套可切换架构 [pdf:E05]。

## § 4 — 核心 Intuition

核心 Intuition 是：**PHiL 的平台和通信链不需要全局最快，只需要在闭环中比被研究的最小关键动态足够快，并且 simulator 能在对应 fixed time step 内完成模型计算。** 高动态任务应减少转换、采用高速 digital link；慢动态任务可以把正弦波生成等快环节交给 amplifier 内部 oscillator（振荡器），让 PLC 或 microcontroller 只更新慢变量。作者最终把这一点概括为：setup 产生的延迟必须低于 investigation 的动态尺度，具体使用 analog、SCPI 还是 optical communication 取决于被研究现象 [pdf:E06]。

## § 5 — 具体方法与完整 Pipeline

这篇论文没有提出单一算法，而是给出一个“按延迟链分解和按任务时间尺度选型”的 PHiL pipeline。

1. **定义 ROS 与 HUT 边界。** Simulator 实时计算 ROS，输出 voltage/current/frequency set point（电压、电流或频率设定值）；amplifier 把低功率信号转成真实功率；HUT 的 current、power 或 frequency measurement（电流、功率或频率测量）再反馈给 simulator。Figure 1 显示了 digital、analog 和 power 三类链路 [pdf:E04]。一个关键边界判断是：若通信属于 HUT 自身，它的延迟就是被测对象的一部分；若通信属于 test setup，例如 RTS-amplifier 链路，则必须计入试验误差和稳定性分析 [pdf:E03]。

2. **根据现象确定最小时间尺度和步长。** 作者建议先问 ROS 中最快需要保真的动态是什么，再选择 simulation time step。高频、谐波或快速交流波形要求更短步长；phasor-based 或慢速功率平衡模型可以使用更长步长。然后检查 simulator 能否在该步长内完成模型计算 [pdf:E06]。

3. **选择 simulator 与执行平台。** PHiLsLab 的 Bachmann MC210 PLC 以 fixed-step 方式执行由 MATLAB/Simulink 编译的 C code，标称可到 200 µs；OPAL-RT OP5600 的 CPU simulation 可到 10 µs。实验室使用的 linear amplifier 每相 7.5 kW、总计 22.5 kW，AC 最高 270 V\(_\mathrm{rms}\)、DC 最高 425 V，bandwidth 最高 30 kHz [pdf:E07]。这些数字说明平台能力，但作者并不把规格表当最终判断，后续还用端到端测试确认真实延迟。

4. **实现通信和闭环。** PLC-analog 路径中，CPU 计算结果经过 D/A、amplifier 内部 A/D 与 scaling，再驱动 HUT；反馈测量再次经 A/D 回到 PLC。Figure 4 标出的关键量包括 PLC simulation step \(T_s\ge100\,\mu s\)、20 µs 的输出转换链、amplifier 侧 3 µs read-in 和约 1 µs measurement，所有转换都必须计入 closed-loop delay [pdf:E08]。RTS-digital 路径则通过 Aurora 直接传输 set point 与 measurement，省去 A/D 和 D/A；Figure 5 给出 \(T_s\ge5\,\mu s\) 以及 amplifier 内约 1 µs 的数字处理量级 [pdf:E09]。

5. **按任务把快环节下沉。** 在 FCR/BESS case 中，PLC 同时运行 dynamic grid model（动态电网模型）和 BESS controller，SCPI 每 5 ms 更新 frequency/voltage set point，amplifier 的内部 oscillator 生成三相正弦，因此 5 ms simulation step 不会直接把电压波形离散成阶梯。该 BESS 由三个双向 inverter 和 20 kWh lithium-iron-phosphate accumulator 组成；计算使用 64 bit，作者认为秒级最小时间常数下 SCPI 延迟可忽略 [pdf:E10]。在高电流 case 中，M-DUINO 只负责慢速 current sequence 和 ROS simulation，amplifier 工作在 current-controlled mode，并可通过 sense wire 缩短反馈路径 [pdf:E11]。

6. **验证而不是只相信 datasheet。** 作者实际测 step response、CPU load 和 waveform discretization，再把观察到的延迟与任务时间尺度比较。最终 Table 1 把 simulator step、communication conversion 和 amplifier read-in 分开列出，形成选型表 [pdf:E12]。

从 EMT + FPGA 角度看，论文只在设备概述中说明 CPU simulation 支持更大模型、FPGA simulation 支持更小时间步但模型规模受限 [pdf:E03]，并在实验室架构中出现 OP4520 FPGA connection box [pdf:E05]。它**没有报告** EMT solver 的离散形式、switch/event handling、multi-rate scheduling、计算依赖图、并行 partition、fixed-point/float 数值表示、FPGA 资源占用、时序收敛或 bitstream 映射。实际对比主体是 PLC CPU 与 OPAL-RT CPU，不能把结果解读为 FPGA 实时仿真的性能证明。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，但数学服务于 FCR case 的 dynamic grid model，而不是用于推导 PHiL delay stability（延迟稳定性）。PDF 物理页 8、Figure 7 与 Eq. (1)-(3) 给出一个简化的 ENTSO-E interconnected grid frequency model [pdf:E13]。

首先，忽略机械损耗时，accelerating power \(P_a\) 引起频率变化：

\[
\frac{df}{dt}=\frac{P_a\,f_0^2}{T_G\,P_n\,f}.
\]

其中 \(f\) 是当前频率，\(f_0\) 是 nominal frequency（额定频率），\(P_n\) 是 system load（系统负荷），\(T_G\) 是 grid time constant（电网时间常数）。直观上，正的 accelerating power 使频率上升；更大的惯性时间常数使频率变化更慢。该式对应 PDF 物理页 8、Eq. (1) [pdf:E13]。

接着，作者用转动惯量 \(J\) 和额定角速度 \(\omega_0\) 定义电网时间常数：

\[
T_G=\frac{J\,\omega_0^2}{P_n}.
\]

它把 rotating mass 中储存的动能相对于系统负荷的大小压缩成一个时间尺度：惯量越大，频率对功率失衡的响应越慢。该式对应 PDF 物理页 8、Eq. (2) [pdf:E13]。

最后，Frequency Containment Reserve（频率遏制备用，FCR）按 frequency deviation \(\Delta f\) 比例激活，增益定义为：

\[
K_{FCR}=\frac{P_{FCR,max}}{0.2\,\mathrm{Hz}}.
\]

这里 \(P_{FCR,max}\) 是可用 FCR 上限；分母表示在 0.2 Hz 频差时全部 primary reserve 被激活。该式对应 PDF 物理页 8、Eq. (3) [pdf:E13]。

真正需要注意的是：这三条公式只描述 ROS 的 frequency dynamics。论文没有把 simulator sampling、通信延迟、amplifier bandwidth、measurement delay 和 HUT impedance 写成带 \(e^{-s\tau}\) 或离散延迟项的闭环 transfer function，也没有推导 phase margin、passivity 或 delay margin。因此“延迟应低于 investigation dynamics”是由 case study 归纳出的工程规则，不是由 Eq. (1)-(3) 证明的稳定性定理。

## § 7 — 实验设计与结论

**问题 1：analog PLC 和 digital RTS 的输出链，谁更适合高动态过程？** → 作者让 simulator 输出 0 V 到 100 V step，HUT 是每相 31 Ω 的三相电阻，并比较 simulator output 与 amplifier output。→ PLC analog output 从 10% 上升到 90% 约需 25 µs，amplifier 再约晚 5 µs 跟随，延迟主要被 PLC analog rise time 主导；RTS digital signal 近似瞬时跳变，amplifier 约 4 µs 后开始上升、约 8 µs 达到最大值。结论是高动态任务优先高速 digital connection；analog 路径若 unavoidable，应选低 rise-time output module。定位：PDF 物理页 7、Section 4.1.1、Figure 6 [pdf:E14]。

**问题 2：低成本 PLC 能否承担 PHiL simulator，何时必须用 RTS？** → 作者把同一简化 ENTSO-E grid model 部署到两种 simulator，逐步降低 simulation time step，测 mean CPU load。→ PLC 在 500 µs 时约 20% load、200 µs 时约 50%，100 µs 时达到 98.1%，再低会在编译阶段报错；OPAL-RT 在 100 µs 时约 5%，5 µs 时约 92%。相同 CPU load 下，作者估计 RTS 约比 PLC 快 20 倍；一个 14-node CIGRE middle-voltage model 在 RTS 上以 100 µs 运行时平均 CPU load 为 67%，PLC 无法在合适步长下运行。结论是 PLC 可用于小模型和较慢动态，但低步长或复杂网络需要专用 RTS。定位：PDF 物理页 9、Section 4.1.2、Figure 8 [pdf:E15]。

**问题 3：simulation step 对 50 Hz waveform fidelity 有什么影响？** → 作者把正弦波分别用 5 µs、100 µs、1 ms 和 5 ms 步长离散化。→ 5 µs 与理想正弦几乎无可见差异；100 µs 对应每周期 200 个 step，仍可用；1 ms 只剩每周期 20 个 step，作者把它视为包含交流量 investigation 的下限；5 ms 每周期只有 4 个 step，无法充分表示波形。定位：PDF 物理页 10、Figure 10 及相邻正文 [pdf:E16]。

**问题 4：慢速 grid-frequency/BESS investigation 是否仍需 RTS？** → 参考事件设定为 continental Europe grid 在 off-peak \(P_n=150\,\mathrm{GW}\) 时失去 3 GW generation，即 2% load jump；约束包括频率偏差不超过 ±800 mHz、quasi-stationary 偏差不超过 ±200 mHz。作者用 PLC 同时运行 grid model 和 BESS controller，通过 SCPI 每 5 ms 更新 amplifier set point，由 amplifier 内部 oscillator 生成三相电压。→ 因最小时间常数在秒级，5 ms step 与最大 5 ms Ethernet/SCPI transmission delay 足够小，且 waveform quality 不受 simulation step 直接限制。作者据此认为复杂的慢动态研究可以不用 RTS。定位：PDF 物理页 10、Section 4.2 [pdf:E17]；PDF 物理页 11、Figure 11 与相邻正文 [pdf:E10]。

**问题 5：极慢的高电流耐久序列能否由普通 microcontroller 驱动？** → 作者用 M-DUINO 运行 current sequence 和 ROS，amplifier 输出最高 800 A，并可用 transducer 或 sense wire 闭环。→ 总延迟约 148 ms，主要来自 M-DUINO 的至少 146 ms 延迟；但对于每个 step 最长可达 10 min 的 current sequence，这个速度仍符合任务需求。定位：PDF 物理页 12、Section 4.3、Figure 12 [pdf:E11]。

这些实验共同支持一个有限结论：平台性能必须相对于任务判断。它们没有证明任何 HUT 和 interface algorithm 下的普适稳定性，也没有提供统一 accuracy metric、confidence interval 或跨平台重复实验，因此不应把 case-specific sufficiency 外推成 formal guarantee。

## § 8 — Take-aways

**5 句话总结：**

1. PHiL 的核心风险不是某一个器件慢，而是 simulator、conversion、communication、amplifier 和 feedback 共同形成的闭环延迟链 [pdf:E04][pdf:E12]。
2. 高动态 investigation 中，PLC analog output 的 rise time 可能成为主导瓶颈，Aurora 等高速 digital link 能显著缩短端到端响应 [pdf:E08][pdf:E09][pdf:E14]。
3. PLC 不是天然不适合 PHiL；当模型简单、步长要求宽松时，它能以更低成本完成任务，但复杂模型或微秒级步长需要 RTS [pdf:E15]。
4. 对秒级 FCR 或分钟级 current sequence，可以把快速 waveform generation 下沉到 amplifier，允许使用 5 ms SCPI 甚至百毫秒级 microcontroller [pdf:E10][pdf:E11]。
5. 论文最有用的贡献是 Table 1 与三组 case 构成的选型直觉，而不是新的 delay stability theory [pdf:E12][pdf:E06]。

**3 句话总结：** PHiL 设计应先确定被研究现象的最小时间尺度，再选择能在相应步长内完成计算的 simulator，并让通信和 amplifier 延迟与该步长相称。高动态任务要减少 conversion、优先 digital path；慢动态任务可以使用 PLC 或 microcontroller，并把正弦生成交给 amplifier。该规则有实验证据，但缺少针对 active HUT、jitter 和 interface algorithm 的闭环稳定性认证。

**1 句话总结：** 不要问“哪台 PHiL 硬件最快”，要问“这条完整闭环是否比我要研究的动态足够快，而且稳定性证据是否覆盖我的 HUT” [pdf:E06]。

## § 9 — 最脆弱的假设

最脆弱的假设是：**只要把各组件的 nominal delay 相加，并保证总延迟低于 investigation 的特征时间尺度，就足以判断 PHiL 的精度和稳定性。** 这是全文选择规则的支点。作者的 Table 1 确实把 simulator step、communication conversion 和 amplifier read-in 分解成可比较数字 [pdf:E12]，结论又明确要求 setup delay 低于 investigation dynamics [pdf:E06]。

这个假设可能失效，因为闭环稳定性不只由 delay magnitude 决定，还取决于 loop gain、HUT impedance、amplifier bandwidth、interface algorithm、采样保持、quantization 以及 delay jitter。论文自己在 PDF 物理页 3、Section 2.2 承认，原本稳定的系统可能因额外 ROS-HUT loop 变得不稳定，且非理想行为需要 interface algorithm 处理 [pdf:E03]。但用于快速平台对比的 HUT 是 31 Ω/phase 的简单电阻，作者还说明采用 simple HUT 是为了避免 instability 风险 [pdf:E14][pdf:E15]；另外两个 case 的关键动态分别在秒级和分钟级 [pdf:E10][pdf:E11]。这些设置证明了“在宽裕时间尺度和温和 HUT 下可以工作”，却没有覆盖最危险的 active、nonlinear 或强耦合 HUT。

论文为该假设提供的证据是三个成功 case、Figure 6/8/10 的响应与负载观察，以及 Table 1 的 delay inventory。缺失的证据包括：同一 HUT 下对 delay/jitter 的稳定边界扫描；不同 interface algorithm 的对照；closed-loop error 或 passivity margin；多次实验的统计波动；以及可复核的 raw data。Data Availability Statement 明确说，除论文展示的数据外，数据未公开，因为并非所有相关方同意发布 [pdf:E18]。因此这里最合理的结论是：选型规则是经验性 heuristic（启发式），不是可移植的稳定性证书。

## § 10 — 最小复现实验

一周内最值得复现的是 Section 4.1 的“通信路径决定高动态输出延迟”这一点，因为它不需要完整电网模型，也能直接证伪核心 claim。

**数据与硬件。** 使用一个 fixed-step simulator（PLC 或 RTS）、一台可接受 analog 和 digital set point 的 linear amplifier、每相约 31 Ω 的三相电阻 HUT、示波器或同步采集卡。论文原始 raw data 不公开，因此目标应是复现实验结论和数量级，而不是逐点重现 Figure 6 [pdf:E18]。

**实现。** 建立两条尽量相同的 loop：A 路径为 simulator analog output → amplifier analog input → HUT → measurement feedback；B 路径为 simulator digital/optical output → amplifier digital input → HUT → digital feedback。让模型输出 0 V 到 100 V step，并分别记录 simulator command、amplifier voltage 和 feedback current。随后用同一简单模型 sweep simulation step，记录 deadline miss/overflow 和 CPU load。实验配置直接对应 PDF 物理页 6 的 Figure 4/5 与物理页 7 的 Figure 6 [pdf:E08][pdf:E09][pdf:E14]。

**测量。** 至少报告 command-to-output latency、10%-90% rise time、round-trip latency、steady-state error，以及每个 time step 下的 CPU load。再加一个 50 Hz sinus test，以 100 µs、1 ms、5 ms 步长观察 waveform discretization，核对 Figure 10 所示的趋势 [pdf:E16]。

**支持标准。** 若 analog path 的主要瓶颈确实来自 output rise/conversion，digital path 保持 single-digit-microsecond amplifier response，而且 simulation step 收紧时 PLC 比 RTS 更早接近 deadline，则支持论文的局部 claim [pdf:E14][pdf:E15]。

**反驳标准。** 若两条路径在相同端到端 latency 下出现明显不同的 closed-loop error 或 instability，或者 analog/digital 的性能差异主要由 amplifier/interface configuration 而非通信形式决定，则说明“按 nominal delay 选型”不足，需要更完整的闭环模型。

## § 11 — 最强反例设计

最强反例不是再找一个更慢的 PLC，而是构造一个 **nominal total delay 很小、却因闭环性质而不稳定** 的 PHiL；或者构造一个 total delay 较大、但经 interface compensation 后仍稳定准确的 PHiL。这样可以直接攻击论文从 delay magnitude 推导 suitability 的核心机制。

候选实验如下：选择一个带主动控制的 power-electronic HUT，让 ROS-HUT loop 对 phase lag 敏感；固定平均 round-trip delay，不改变 simulator step 和 amplifier nominal bandwidth，只改变两件事：一是把 constant delay 换成具有相同平均值的 jittered delay，二是切换不同 interface algorithm 或 damping setting。对每个设置扫描 HUT operating point 和 loop gain，记录稳定边界、oscillation amplitude、tracking error 与 energy exchange。论文已经承认 interface algorithm 和 amplifier nonideality 会决定稳定性 [pdf:E03]，但最终推荐主要依靠 component delay 与 investigation time constant 的比较 [pdf:E06]。

若相同平均 delay 下，jitter 或 interface algorithm 使系统从稳定变为不稳定，Table 1 式的 scalar delay budget 就不是充分判据。若较大的 constant delay 在补偿后反而比更小但抖动的 delay 更稳定，也会推翻“越小越安全”的隐含排序。这个反例比简单比较另一台设备更有力，因为它提供了一个具体替代解释：Figure 6/8/10 的成功可能来自 benign resistor HUT 和宽松动态，而不是 delay matching 本身已经捕捉了闭环稳定性的全部决定因素 [pdf:E14][pdf:E15]。

## § 12 — Follow-up Research Idea

在电气、控制和 power hardware 领域，高影响研究通常不能只给更快的实现，还需要把 stability/accuracy guarantee（稳定性与精度保证）、跨平台实验验证和可落地的工程选型结合起来。基于第 9 节的缺口，一个非增量的候选方向是：**从“按标称延迟挑硬件”改写为“面向 delay uncertainty 的 PHiL 闭环认证与自动平台映射”。** 由于本任务只允许使用源 PDF、未检索外部相关工作，下面明确是候选研究想法，不声称 novelty。

**（a）未满足需求。** 当前 Table 1 能告诉工程师 OPAL-RTS、PLC、M-DUINO、Aurora、analog 和 SCPI 的 nominal delay [pdf:E12]，却不能回答“在某个 HUT、某个 interface algorithm、某个 jitter distribution 下是否稳定，以及误差上界是多少”。工程上真正需要的是可认证的 operating envelope，而不只是单点延迟清单。

**（b）潜在研究价值。** 新目标是建立一个 end-to-end model，同时包含 simulator deadline、sample-and-hold、communication delay/jitter、amplifier bandwidth、measurement path 和 HUT impedance；模型输出 robust stability margin、允许的 delay envelope 和可接受误差。随后自动决定模型应放在 CPU、FPGA、PLC 还是 amplifier internal oscillator，并选择 analog、SCPI 或 optical link。它把经验性选型规则升级为可验证的 co-design problem。

**（c）相邻领域工具。** 可以借鉴 networked control（网络化控制）的 delay/jitter model、robust control（鲁棒控制）的 uncertainty analysis、passivity-based interface design（基于无源性的接口设计）、real-time scheduling 的 worst-case execution time，以及 FPGA timing analysis。原论文只给出 CPU/FPGA 的一般取舍，没有 solver partition、数值格式和资源时序映射 [pdf:E03][pdf:E07]，因此这里不是“给现有方案再加一个 FPGA 模块”，而是把计算映射本身纳入闭环稳定性目标。

**（d）第一个证伪实验。** 在同一 active HUT 上构造多组具有相同平均 delay、不同 jitter/burst pattern 的链路，再改变 interface algorithm。若模型不能正确预测 stable/unstable boundary，或预测误差上界与实测严重不符，这个方向应立即被否定。反之，若它能跨 PLC-analog、RTS-optical 和 SCPI/internal-oscillator 三类架构预测结果，才说明模型抓住了比 scalar delay 更本质的机制 [pdf:E08][pdf:E09][pdf:E10]。

**（e）与本文的实质区别。** 本文的问题是“给定 investigation，哪类现有 hardware 足够快”；候选工作的目标是“给定 HUT 与不确定 delay，怎样联合合成 interface、调度和平台映射，并给出可验证的稳定/精度证书”。前者依赖成功 case 和时间尺度匹配，后者要求在失败边界附近也能做出可证伪预测。
