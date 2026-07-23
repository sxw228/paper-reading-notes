# Real-Time Digital Hardware Simulation of Power Electronics and Drives

**作者：** Gustavo G. Parma；Venkata Dinavahi  
**出处：** *IEEE Transactions on Power Delivery*, 22(2), 1235–1246  
**年份：** 2007  
**DOI：** 10.1109/TPWRD.2007.893620  
**Zotero key：** X42DCC9J

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是一个很具体的工程矛盾：工业交流传动控制器需要在接入真实高功率变流器和电机之前做闭环测试，但传统实时数字仿真器既受计算带宽限制，又很难精确接住控制器发来的高频 gate signal。若开关事件落在仿真步长之间，模拟的施加电压与真实控制器意图就会错位；若把步长压得很小，通用处理器又未必能在每一步的截止时间内完成计算。作者因此把一套完整的 PWM VSC-fed induction machine drive 直接硬连线到 FPGA 上，并把最需要时间分辨率的 VSC 放在 12.5 ns 固定步长上运行。[pdf:E01]

重要性不只在“仿得更快”。HIL 的价值是让真实控制器看到按真实时间推进的被控对象，同时避免控制器故障损坏功率设备；这能减少高功率试验场地、motor-generator set、传感器和开关设备的占用。论文的核心工程主张是：FPGA 的并行硬件可以把变流器开关细节、电机动态、控制、SVPWM 和测量链放进同一个确定时序系统，从而在不依赖插值、外推或 variable-step correction algorithm 的情况下完成实时闭环仿真。[pdf:E01]

需要限定“精确”的含义：论文证明了这套模型能按设定的器件时序和多速率调度实时运行，并展示了合理波形；它没有证明这些波形在器件寄生参数、温度和开关能量层面等同于真实功率模块。

## § 2 — 前人工作与不足

论文把当时的 power-electronic device behavioral model 分成三类。ideal model 用开关态对应的双值电阻表示器件，开关改变会改变电路拓扑和系统矩阵；实时实现通常预存所有拓扑矩阵，用存储换计算。switching-function model 以受控源绕开矩阵重组，适合高频运行，但作者指出它不能准确表现 regenerative load 下的整流行为。averaged model 只保留低频开关函数，适合控制器设计，却会丢失 HIL 所需的高频真实感。[pdf:E01]

另一条路线是在线或离线的 interpolation、extrapolation 与 variable step-size correction，用来补偿一个大步长内发生的开关事件。作者的问题意识不是这些方法完全无效，而是它们增加算法复杂度，并且仍受通用实时平台计算带宽约束。相较之下，论文提出在 FPGA 上用极小固定步长直接解析 gate timing，并用器件 datasheet 提供的导通压降、延时、上升时间和下降时间构造 VSC 状态机。[pdf:E01][pdf:E02]

作者还声称这是首次用 FPGA 建模完整 ac drive，而此前 FPGA 在该领域主要用作控制算法或 PWM gating pattern generator。这个“首次”是论文在 2007 年给出的原文主张，不是本卡重新完成文献检索后的独立 novelty 结论。[pdf:E02]

## § 3 — 重建作者的思考路径

可以把作者到达方案的路径重建为五步。第一，HIL 真正难的不是慢速机械状态，而是控制器 gate edge 与变流器 switching transition；因此全系统没有必要统一使用纳秒级步长。第二，FPGA 天然适合把多个固定延迟、比较、计数和状态转移并行展开，而不是按软件指令顺序执行。第三，HIL 不需要 SPICE 级器件制造模型，但也不能退化成只保留基波的 averaged model；所以应保留最影响控制器接口的导通压降、dead-time、turn-on/turn-off delay、rise/fall time 和电流方向。第四，电机和控制器的自然时间尺度更慢，可以分别用 10 µs、250 µs 等步长运行，再通过寄存器和同步信号连接。第五，固定点位宽和硬件资源必须一起设计，否则算法正确也无法满足 FPGA 的时序与容量约束。[pdf:E02][pdf:E03][pdf:E09]

由此得到的不是“把 MATLAB 模型自动搬进 FPGA”这么简单，而是按物理时间尺度重新切分模型：开关器件是高速事件状态机，电机是离散状态空间，控制与 SVPWM 是周期任务，测量系统则在每个 PWM 周期内做同步积分。这个分解让每个部分只为自己真正需要的时间分辨率付费。

## § 4 — 核心 Intuition

核心 Intuition 是：不要用复杂校正算法猜测大步长内部发生了什么，而是把最敏感的 VSC 开关模型做成每 12.5 ns 前进一步的并行数字电路；其余慢动态按更大步长运行。器件模型不追求全部 semiconductor physics，只保留会改变 controller-visible voltage/current 的时序和导通特性。这样，FPGA 的空间并行性被转换成了实时仿真的时间分辨率。[pdf:E03][pdf:E09]

## § 5 — 具体方法与完整 Pipeline

以“转速给定变化并带负载扰动”为例，完整 pipeline 如下：

1. **输入与时钟。** 开发板接收 dc-link voltage \(V_{dc}\)、rotor-speed reference \(\omega_r^\*\)、rotor-flux magnitude reference \(|\lambda_r|^\*\) 和 load torque \(T_L\)。所有子频率来自板上的 80 MHz 公共时钟；开发板是 Altera Stratix EP1S80，论文报告其有 79,040 个 logic element、7,427,520 RAM bit、176 个 9-bit DSP block、12 个 PLL 和 679 个最大用户 I/O。[pdf:E08]
2. **控制。** direct field-oriented controller 读取电机模型直接给出的转速、定子电流、转子磁链幅值与角度，以 PI 回路产生 \(v_{\alpha s}^\*\) 和 \(v_{\beta s}^\*\)。PI 带 saturation 和 anti-windup；控制频率选为 4 kHz。论文没有实现实际系统通常需要的 flux observer，而是直接取用仿真电机内部的 rotor-flux state。[pdf:E06]
3. **SVPWM。** 8 kHz SVPWM 在每个 PWM 周期开始采样 \(\alpha\beta\) 电压指令，转成三相后排序，计算三条 bridge leg 的导通时间，再用同步比较器生成上管 gate signal；下管互补信号和 dead-time 在 VSC 模型内处理。[pdf:E07]
4. **VSC。** 每个 bridge leg 只接收一个上管 gate command，由 dead-time counter 产生上下管信号。四状态状态机结合输出电流的正、负或零，决定电流流过 IGBT 还是 antiparallel diode；多个计数器分别实现 turn-on delay、turn-off delay、rise time 和 fall time，输出桥臂电压和 dc-link current。三条相同 bridge leg 组成 2-level、6-pulse VSC。[pdf:E03][pdf:E04]
5. **电机。** fifth-order stationary-reference-frame squirrel-cage induction-machine model 以 stator/rotor flux 为电气状态，以 rotor electrical speed 为机械状态。作者利用机械时间常数较慢这一点，在一个电气步内把转速视为常量，先解电气部分再解机械部分；离散模型每 10 µs 更新。[pdf:E04][pdf:E05]
6. **测量与反馈。** 系统不通过一个会引入随基频变化相移的普通低通滤波器提取基波，而是在每个 PWM 周期同步积分 \(v_\alpha^{PWM}\) 与 \(v_\beta^{PWM}\)，并在周期边界输出积分值、复位 integrator，同时计算一个 PWM 周期内的 mean dc current。[pdf:E08]
7. **输出与观察。** VHDL bitstream 经 JTAG 下载到开发板；关键内部信号通过 AD5380 40-channel DAC 辅助板送往示波器。实际结果包括 IGBT switching transition、稳态 PWM/FFT、电机速度、转矩、电流和 speed reversal transient。[pdf:E08][pdf:E10][pdf:E11]

数值表示也是 pipeline 的一部分。外部电压、电流等 I/O 主要使用 24-bit fixed point（例如 19.5），内部变量最多 32 bit，并增加 fractional bit 以压低 round-off error。论文给出的 sin lookup table 输出是 2.11，分辨率为 0.00048828125；电流和转速等控制变量使用 19.13。[pdf:E09]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文不是提出新的电机理论，而是把器件、电机、控制和测量公式改造成可定时、可固定点实现的硬件计算图。最核心的数学有四层。

第一层是 IGBT 的导通近似。作者从

\[
V_{CEsat}(t)=V_{CE}(T_0)+r_{CE}i_c(t)
\]

出发，其中 \(r_{CE}\) 是 on-state resistance，\(V_{CE}(T_0)\) 是 threshold voltage。由于所用器件 datasheet 中 \(r_{CE}\) 约为 \(1\,\mathrm{m}\Omega\)，硬件模型进一步把 IGBT 导通压降近似为常数 \(V_{CEsat}=V_{CE}(T_0)\)，二极管压降也取常数。[pdf:E02][pdf:E04] 所选 Powerex CM100DU-24F 参数为：\(t_{d(on)}=100\) ns、\(t_r=50\) ns、\(t_{d(off)}=400\) ns、\(t_f=300\) ns、\(V_{CEsat}=1.8\) V、\(V_{dsat}=1.25\) V。[pdf:E03] 工程含义是：桥臂电压不再瞬间跳变，而由计数器在规定延迟和斜坡时间内推进。

第二层是 induction-machine state-space model。电气部分用 \(\lambda_{\alpha s},\lambda_{\beta s},\lambda_{\alpha r},\lambda_{\beta r}\) 作状态，并由这些 flux state 线性映射出 stator/rotor current；机械部分满足

\[
\dot{\omega}_r(t)=\frac{P}{2J}\left(T_e(t)-T_L(t)\right),
\]

而 \(T_e\) 由 stator 与 rotor current 的交叉项构成。[pdf:E04] 这组方程原本含有转速与状态量乘积；作者利用速度在一个电气步内近似不变，把电气和机械更新顺序化，从而避免一般 nonlinear solver。

第三层是离散化。作者对电机方程采用 trapezoidal rule，并用

\[
s=\frac{2}{\Delta t}\frac{z-1}{z+1},\qquad \Delta t=10\,\mu\mathrm{s}
\]

把连续模型变成寄存器、加法器和乘法器组成的递推计算。[pdf:E05] 梯形规则同时使用步首和步末信息，相比 forward Euler 对这类电磁状态通常有更好的数值稳定性；但论文没有给出离散误差界或步长收敛试验。

第四层是 PWM-synchronous measurement。对第 \(N\) 个 PWM 周期，

\[
\bar v_{\alpha(N)}=\frac{1}{T_{PWM}}\int_t^{t+T_{PWM}}v_\alpha^{PWM}(t)\,dt,\qquad
\bar v_{\beta(N)}=\frac{1}{T_{PWM}}\int_t^{t+T_{PWM}}v_\beta^{PWM}(t)\,dt.
\]

[pdf:E08] 物理意义是计算一个开关周期内真正施加的 volt-second，而不是用固定低通滤波器去猜基波；同步复位使测量相位与 PWM 周期锁定。

## § 7 — 实验设计与结论

**问题 1：器件状态机是否真的表现设定的 switching timing？**  
**实验：** 用示波器观察单桥臂 gate signal 与 \(V_{out}\)，分别设置 \(I_{out}>0\) 和 \(I_{out}=0\)，查看 turn-off、dead-time、fall/rise transition。  
**答案：** 波形按模型设定出现延迟和线性电压过渡；在一种工况下，上管允许的最短 on-time 小于 dead-time，因此器件甚至不会真正导通。[pdf:E09][pdf:E10] 这支持“状态机执行了设定规则”，但没有与物理 CM100DU-24F 开关波形做误差比较。

**问题 2：稳态 PWM、周期平均量与频谱是否合理？**  
**实验：** 在 \(\omega_r^\*=377\) rad/s 的稳态观察 60 Hz \(\alpha,\beta\) 电压、一个 PWM 周期的平均值以及 FFT。  
**答案：** 示波器显示典型 two-level phase voltage，主频为 60 Hz，并在 8 kHz PWM frequency 及 16 kHz 附近出现 sideband；作者称频谱与文献中的解析结果一致。[pdf:E10] 图中的 0 Hz 分量来自 0–5 V 单极性 DAC offset，不是模型生成的真实 dc component。

**问题 3：完整 drive 在动态工况下是否保持闭环行为？**  
**实验：** 依次执行 150 rad/s 启动、给定升到 377 rad/s、施加与移除 100 N·m 负载、再反转到 \(-377\) rad/s，记录速度、转矩、dc current 和 \(\alpha\beta\) current；并与 MATLAB/SIMULINK offline simulation 的相同工况作图形对照。  
**答案：** 实时与离线波形在趋势上相似；负载施加/移除时图中速度扰动不明显，speed reversal 时 current frequency 随转速变化，\(I_{dc}\) 在不同 transient 中可正可负，表现 inverter/rectifier operation。[pdf:E11][pdf:E12]

**问题 4：单片 FPGA 是否装得下且能按多速率 deadline 运行？**  
**实验：** 综合完整 VHDL 并报告资源与时序。  
**答案：** 总设计使用 38,072 个 LE（48.17%）、176 个 DSP（100%）和 1 个 PLL；其中电机模型使用 19,285 个 LE 与 136 个 DSP，是主要计算负担。VSC、measurement、machine、PWM、controller 分别以 12.5 ns、100 ns、10 µs、125 µs、250 µs 的节拍运行。[pdf:E09] 这里最重要的限制是 DSP 已用满，因此“还有一半 LE”不等于还能直接复制一个完整高复杂度 drive。

论文没有报告 RMS waveform error、switching-time error、THD error、latency jitter、timing slack、温度/电压/负载 sweep，也没有连接真实外部控制器完成 HIL 测试。因此实验支持的是“实现成功且波形合理”，不是经过独立计量的高保真上界。

## § 8 — Take-aways

**5 句话：**

1. 论文证明了 2007 年的单片 FPGA 已能把 VSC、电机、field-oriented control、SVPWM 和测量系统组合成实时 ac-drive simulator。[pdf:E01][pdf:E08]
2. 最关键的架构选择是让 VSC 以 12.5 ns 更新，而把电机、控制与 PWM 放在更慢的多速率时钟域。[pdf:E09]
3. VSC 用电流方向、dead-time 和 datasheet switching timing 驱动状态机，避免在大步长内额外做 switching-event correction。[pdf:E03][pdf:E04]
4. 完整设计占 48.17% LE，却已耗尽 176 个 DSP，说明硬件资源瓶颈并不只由逻辑门数量决定。[pdf:E09]
5. 实验给出了合理的 switching、稳态频谱和 drive transient，但定量 fidelity 和真实 HIL 闭环仍未被证明。[pdf:E10][pdf:E11][pdf:E12]

**3 句话：**

1. 这项工作的真正贡献是用空间并行换取纳秒级开关时间分辨率，并用多速率分解避免全系统都承担该成本。
2. 它展示了完整 FPGA drive simulator 的可实现性与资源代价。
3. 它最欠缺的是独立物理基准、误差指标和 controller-in-the-loop 证据。

**1 句话：**

把最硬的 switching deadline 固化成 FPGA 状态机，是这篇论文跨过实时性瓶颈的关键，但“能实时运行”与“已定量证明真实”仍是两件事。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**只要以 12.5 ns 固定步长执行一个由 datasheet 固定延迟、固定线性 transition 和固定导通压降构成的 IGBT 状态机，就足以精确表示控制器关心的 VSC switching behavior。** 这个假设直接支撑论文“不需要 correction algorithm 也能细致、精确接收 gate signal”的核心贡献。[pdf:E01][pdf:E03]

它可能在真实系统中失效，因为 \(t_{d(on)}\)、\(t_r\)、\(t_{d(off)}\)、\(t_f\) 与压降并不是跨 collector current、dc-link voltage、junction temperature 和 gate-driver impedance 恒定；commutation parasitic、diode reverse recovery、tail current、ringing 与同时开关也不会自然变成论文中的线性斜坡。作者还假设一个 12.5 ns 步内 current 不变，并以极小步长作为其合理性依据。[pdf:E04] 对 controller-level HIL，这种简化可能足够；但论文没有用 double-pulse hardware measurement、SPICE/SABER 高保真模型或误差界证明“足够”的有效范围。

论文提供的证据是状态机输出符合自身设定时序，以及完整系统波形与 offline simulation 趋势相似。[pdf:E10][pdf:E11][pdf:E12] 缺失的证据是模型对一个独立真实对象的交叉验证；因此现有对照存在“两个模型共享相同简化，所以彼此相似”的替代解释。

## § 10 — 最小复现实验

一周内不必重建完整电机 drive；最小实验只复现一个 VSC bridge leg。

1. 从论文 Table I 取六个器件参数，在 80 MHz 时钟上实现四状态状态机、dead-time counter 和四个 switching-timing counter；输入 \(V_{dc}\)、脚本化 \(I_{out}\) 与上管 gate signal。[pdf:E03][pdf:E04]
2. 设计覆盖 \(I_{out}>0\)、\(I_{out}<0\)、\(I_{out}=0\)、gate pulse 短于 dead-time、dead-time 内电流过零、连续窄脉冲六类序列。
3. 用独立的 event-driven 软件 reference 实现相同规则，但不复用 RTL 状态机代码；逐时钟比较 conduction path、\(V_{out}\)、transition start/end 和一个 PWM 周期的 volt-second。
4. 测量 missed-event count、switching-time error、每周期 volt-second error、RTL resource 和最高时钟频率。支持核心实现 claim 的最低标准应是：所有预期 gate event 均被确定性处理，transition timing 与规则的偏差不超过一个 12.5 ns clock，且不同 current-sign 路径无错误状态；任何漏脉冲、错误导通路径或不可接受的 volt-second 偏差都直接反驳该 claim。
5. 如果还能增加一天，再接一个简单 \(R\!-\!L\) load，在 8 kHz SVPWM 下比较 60 Hz fundamental 与 8/16 kHz sideband；这验证 bridge leg 是否能进入论文报告的系统级频谱，而不需要复现 field-oriented controller。[pdf:E07][pdf:E10]

这个实验只能复现“数字实现忠实于论文规则”，不能验证规则忠实于真实 IGBT；后者需要下一节的物理反例。

## § 11 — 最强反例设计

最强反例是一组跨 operating point 的 physical double-pulse test，而不是再做一次 MATLAB 波形对照。对 CM100DU-24F 或参数相近的 IGBT module，系统扫描 low/high dc-link voltage、low/rated collector current、cold/hot junction、不同 gate resistance，并特意加入 diode reverse-recovery commutation 与接近 current zero-crossing 的 dead-time。把测得的 \(V_{CE}\)、\(i_C\)、turn-on/off delay、tail current 和 bridge-leg volt-second 与论文固定参数模型在相同 gate command 下逐事件对齐。

攻击成立的条件应预先写清：如果某一实际工作区间内 switching boundary error 系统性大于若干个 12.5 ns tick，或模型给出的一个 PWM 周期 volt-second error 足以改变 current-controller 的饱和、zero crossing 或 regenerative/rectifying 判定，那么“固定极小步长本身足以保证精确开关建模”就被推翻。即便 FPGA 完全实时、RTL 也完全符合设计，这个反例仍然成立，因为它攻击的是 physical model validity，而不是 hardware scheduling。

更强的一步是把同一个真实 digital controller 分别闭环连接论文模型与物理功率 stage 的低压等比例平台，构造窄脉冲、过调制、快速 speed reversal 和 regenerative braking。若两边的 controller internal state、saturation event 或 protection decision 发生可重复分叉，就说明 offline-simulation 波形相似不足以证明 HIL 等价。

## § 12 — Follow-up Research Idea

在电力电子实时仿真领域，高影响工作通常不仅要展示更小步长，还要同时给出确定时序、可复现实机资源、与独立物理或高保真基准的定量误差，以及真实 controller/HIL 场景中的系统价值。基于第 9 节，候选研究方向是：**把“单一固定器件波形”改写成“带可验证误差契约的 switching-event emulator”**。这里不声称 novelty；在未系统检索 2007 年以后 FPGA EMT、device surrogate 和 uncertainty-aware HIL 文献前，它只是一个证据约束的候选想法。

**（a）驱动需求。** controller HIL 真正需要的不是看起来细腻的 \(V_{CE}\) 斜坡，而是知道模型在给定 operating envelope 内对 switching instant、commutation path 与 volt-second 的最坏误差，以及该误差会不会改变 controller decision。

**（b）研究价值。** 如果 FPGA 模型能在同一实时 deadline 下输出 nominal waveform 与一个经过校准的 error bound，使用者就能判断某次 controller test 是可信、边界性还是已越出模型适用域。这会把“步长越小越真实”的经验判断变成可审计的 HIL fidelity contract。

**（c）相邻工具。** 可以借鉴 robust control 的 uncertainty set、formal verification 的 reachability/interval arithmetic，以及 semiconductor double-pulse identification：离线从电压、电流、温度和 gate resistance sweep 拟合少量 piecewise-affine timing/voltage envelope，在线 FPGA 仍用并行状态机，但传播 nominal state 与紧凑 error interval。

**（d）首个证伪实验。** 在固定 FPGA resource 和 deadline 下，比较论文式固定参数模型与 error-contract model，对保留的 double-pulse operating point 和真实 controller transient 测试最坏 switching-time/volt-second coverage。若新增模型不能显著提高未见工况的误差覆盖率，或为保持覆盖导致实时 deadline/资源不可接受，那么研究设想即被证伪。

**（e）实质区别。** 论文优化的是“如何用纳秒级固定步长执行一个确定器件模型”；候选方向优化的是“如何在实时硬件中表达并约束器件模型与真实对象之间的不确定性”。它改变了成功标准：从波形合理、运行实时，变为 controller-relevant error 有界且适用域可判定。
