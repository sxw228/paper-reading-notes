# Embedding an Electrical System Real-Time Simulator with Floating-Point Arithmetic in a Field Programmable Gate Array

- 作者：Janailson Queiroz；Sarah Carvalho；Camila Barros；Luciano Barros；Daniel Barbosa
- 出处：*Energies*
- 年份：2021
- DOI：10.3390/en14248404
- Zotero key：Z2ZQDR9T

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

### § 1 — 研究问题与重要性

这篇论文要解决的工程问题不是“FPGA 能不能做实时仿真”，而是：能否用 HDL 直接把一套包含电机、功率变换器、滤波器和控制器的电气系统模型变成 FPGA 上的专用计算电路，并在不依赖商业实时仿真软件包的情况下，让每个仿真步都在真实时钟期限内完成。作者把 real-time 的必要条件说得很清楚：一个时间步的模型计算必须在同样长的现实时间过去之前结束；否则仿真时钟会落后于被模拟系统。[pdf:E01](_evidence/E01-p001-abstract-introduction.png)

物理上，这个问题的重要性来自“计算必须追上能量交换”的硬约束。离线仿真可以等求解器慢慢算完，实时仿真却要在下一次控制、开关或外部接口事件到来前给出新状态。FPGA 的价值并非单纯主频高，而是能够把彼此独立的乘、加、除运算变成同时工作的硬件通道；代价则是每一种并行通道都占用 DSP、寄存器和布线资源。论文因此同时面对三个相互牵制的目标：时间步要短、数值结果要可信、硬件面积与成本要可接受。

作者选择“直流电机调速”作为闭环样例很有代表性：控制器输出会改变 H 桥开关，开关平均电压又经过滤波器作用于电机，电枢电流和转速再反馈给控制器。若流水线延迟、离散步长或数值表示处理不当，错误会沿闭环反复放大，而不只是让一条离线曲线稍有偏差。

### § 2 — 前人工作与不足

论文把当时的商用路线分成几类：RTDS/NovaCor 使用定制多核处理平台，HYPERSIM 用处理器承担大模型并用 FPGA 支持快速开关环节，eMEGAsim 则使用 ARTEMiS/SSN 求解器以及处理器与 FPGA。作者引述的典型步长范围为 HYPERSIM 5–100 μs、eMEGAsim 10–100 μs，并认为这些平台的专有软硬件和规模能力带来了较高采购成本。论文自己的目标因此是“用户可自行设计、架构可选、无需依赖现成商业软硬件包”的低成本 fully digital RT simulator，而不是替代这些平台的全部网络规模与 HIL I/O 能力。[pdf:E02](_evidence/E02-p002-prior-work-method-scope.png)

相关工作已经证明 FPGA 可用于电力系统、驱动系统和同步机实时仿真，也有 DC motor FPGA emulator。作者认为仍缺少的是一条从物理方程、离散化、表达式依赖、浮点 IP、时序验证到板上数据采集的完整 HDL 实现流程。这里需要谨慎区分：这是作者对工程流程缺口的定位，不等于论文通过系统性文献比较证明了方法 novelty。论文对 prior work 的比较主要停留在平台构成、典型步长和成本动机，没有给出与最接近 FPGA 电机模拟器的同模型、同精度、同器件对照。

### § 3 — 重建作者的思考路径

可以从作者采用方法之前的约束重建出如下思考路径。

第一，实时仿真先是一项 deadline 任务：每步计算必须在下一个仿真时刻之前完成。第二，电机、PID、变换器和滤波器最终都能写成加、减、乘、除组成的离散递推式；它们天然存在“某些运算可并行、另一些必须等待前级结果”的依赖图。第三，固定点虽然省资源，但设计者要事先管理每个中间量的范围和小数位，闭环中不同数量级信号会使这项工作复杂；IEEE 754 single precision 可以把范围管理交给标准化浮点格式。第四，既然 FPGA 浮点 IP 的不同运算有确定的 cycle latency，就可以把离散方程画成 expression tree：同一层的独立节点并行执行，跨层节点依赖前一层，并在短路径上补 delay，使所有模块在最慢路径完成时同步更新。最后再用 testbench、timing analysis、板上 Signal Tap 和物理工况波形逐层验证。

这条路径真正改变的不是电机方程，而是计算的承载方式：把“CPU 顺序执行一串公式”改写为“电路空间中同时存在多条公式流水线”。作者的贡献因此更接近可复用的 FPGA 建模与调度方法论，而不是新的电机模型或新的数值积分方法。

### § 4 — 核心 Intuition

把每个离散方程拆成 expression tree，让无数据依赖的浮点运算占用独立 IP 并行推进，再按最长运算路径对齐所有输出，就能把一个仿真步的完成时间压缩到受关键路径而非总运算数支配。物理模型仍按固定步长更新，但硬件把“这一时刻所有状态一起向下一时刻推进”落实为同步寄存器更新。论文是否成立的关键，不只是流水线够快，还包括这个固定步长离散模型在目标工况下确实足够准确。

### § 5 — 具体方法与完整 Pipeline

论文的样例输入是一套 separately excited DC motor 调速系统。连续模型包括电枢与励磁电路、反电动势、电磁转矩和机械转动方程；Figure 1 与 Table 1 给出了拓扑、变量及单位，Eq. (1)–(5) 把电压、电流、转速和负载转矩连接起来。[pdf:E03](_evidence/E03-p003-fig01-table01-eq01-05.png)

完整 pipeline 可以按一次仿真步来理解：

1. **从连续物理模型到离散状态更新。** 作者用 forward Euler 将电机方程离散为 Eq. (7)–(9)，其中 \(h\) 是 sampling time。控制对象的物理意义是：励磁电流决定磁场，电枢电流与磁场共同产生电磁转矩，机械惯量把净转矩积分成转速。PID 用当前及前两步误差形成递推控制量，输出参考电枢电压 \(V_a^*\)。系统块图和 Eq. (6)–(11) 位于 PDF 物理页 4。[pdf:E04](_evidence/E04-p004-eq06-11-fig02.png)
2. **从控制电压到开关与滤波。** H 桥通过两对开关产生双极性电压，PWM duty ratio 由 \(V_a^*\) 映射为导通时刻 \(T_1\)；低通滤波器削弱开关纹波，再用 Euler 递推滤波器电流。Eq. (12)–(17) 与 Figure 3 给出了 PID 递推、H 桥和滤波关系。[pdf:E05](_evidence/E05-p005-eq12-17-fig03.png) Eq. (18) 完成滤波器电流离散更新；同页也列出所选 FPGA 的逻辑、DSP、寄存器、片上存储和 I/O 规模。[pdf:E06](_evidence/E06-p006-eq18-fpga-features.png)
3. **统一数值表示。** 作者采用 IEEE 754 32-bit single precision，并实例化 Intel Multi-Cycle Custom Instruction floating-point IP。输入操作数和 operation code 进入 IP，输出仍为同一浮点格式。选择浮点的工程动机是扩大动态范围、避免设计者逐节点手工追踪 fixed-point scaling；代价是运算 latency 与 DSP/寄存器资源更高。[pdf:E07](_evidence/E07-p007-ieee754-fp-ip.png)
4. **把方程变成硬件。** Table 2 给出的报告 latency 包括 division 16 cycles、add/subtraction 5 cycles、multiply 4 cycles；Quartus Prime Pro 19.4 中的流程依次为 specification、HDL development、functional simulation、synthesis/timing、floorplanning/place-and-route 与 re-synthesis。[pdf:E08](_evidence/E08-p008-table02-fig07-design-flow.png)
5. **按依赖图并行与同步。** 电机、PID、变换器与滤波器被拆成三个模块，经 datapath 在 top-level 连接。每个算术节点使用一个浮点 IP；expression tree 的同层独立运算并行，不同层按依赖顺序推进，较短路径插入 delay，直到最长路径完成后一起提交下一步状态。[pdf:E09](_evidence/E09-p009-fig08-09-expression-tree.png)
6. **验证、部署和取数。** 先对微架构 block 和完整系统分别做 HDL testbench，再用 RTL viewer 检查互连、TimeQuest 检查 arrival time 与 required time，最后 place-and-route 到 FPGA。板上 Signal Tap 按物理地址抓取 IEEE 754 数据，经 Python 转成十进制后绘图。Figure 10 的伪算法也表明，若 verification、timing 或 maximum frequency 不满足要求，就返回优化或修改阶段。[pdf:E10](_evidence/E10-p010-verification-fig10-algorithm.png)

论文没有报告多速率求解、迭代式开关事件定位、外部 ADC/DAC 延迟或 HIL 接口；因此这条 pipeline 应理解为 fully digital、单模型、固定步离散仿真流程，不能自动外推为完整 HIL 平台。

### § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学核心是“连续电机方程 → 显式离散递推 → expression tree”。以电枢回路为例，连续方程是

\[
V_a(t)=R_a I_a(t)+L_a\frac{dI_a(t)}{dt}+E_a(t),\qquad
E_a(t)=K_m I_f(t)\omega_r(t).
\]

第一式表示外加电压被电阻压降、电感储能变化和反电动势共同消耗；第二式表示转子转得越快、励磁越强，抵抗外加电压的 back-EMF 越大。机械侧为

\[
T_e(t)-T_m(t)=J_m\frac{d\omega_r(t)}{dt}+F_m\omega_r(t),\qquad
T_e(t)=K_m I_f(t)I_a(t).
\]

净电磁转矩先克服负载与摩擦，剩余部分改变转子角速度。这些连续关系及变量定位见 Eq. (1)–(5) 和 Table 1。[pdf:E03](_evidence/E03-p003-fig01-table01-eq01-05.png)

forward Euler 的共同形式是

\[
x_k=x_{k-1}+h\,f(x_{k-1},u_{k-1}),
\]

也就是用上一步斜率近似整个时间步的变化量。它无需迭代，特别适合固定 latency 的流水线，但 \(h\) 过大时会产生相位误差甚至数值不稳定。论文据此写出励磁电流、电枢电流和角速度的 Eq. (7)–(9)，再用 backward finite difference 整理 PID，形成

\[
V_a(k)=e_k\,PID+e_{k-1}\,PD+e_{k-2}\,D+V_a(k-1),
\]

其中

\[
PID=K_p+\frac{K_d}{h}+K_i h,\quad
PD=-K_p-2\frac{K_d}{h},\quad
D=\frac{K_d}{h}.
\]

这些式子把积分和微分都化成有限历史样本，因此硬件只需当前误差、两级延迟误差和前一控制输出。[pdf:E04](_evidence/E04-p004-eq06-11-fig02.png) [pdf:E05](_evidence/E05-p005-eq12-17-fig03.png)

这里有一个不能静默修正的原文风险：PDF 的 Eq. (8) 把电压项印为 \(\frac{1}{L_f}V_a(t-1)\)，但它从电枢连续方程 Eq. (2) 推导时应对应电枢电感 \(L_a\)，即按代数关系应出现 \(\frac{1}{L_a}V_a(t-1)\)。这是基于原文两式直接比较得到的推断；没有 HDL 源码，无法判断实际实现采用了哪一个下标。任何复现都必须把“按印刷公式”和“按连续方程一致性修正”作为两个独立版本测试，而不能替作者选择。

H 桥部分把期望平均电压转换为 PWM duty：

\[
\bar V_a=\frac{V_{cc}T_1-V_{cc}(T-T_1)}{T},\qquad
T_1(t)=\frac{V_a^*(t)}{2V_{cc}}+\frac{1}{2}.
\]

其直觉是把一个 PWM 周期内正、负母线电压的加权平均设为控制器所需电压。滤波器再按 Eq. (18) 更新电流。这里的 \(h\) 决定数值积分，而浮点 IP 的 cycle latency 决定硬件多久算完一次更新；二者是不同概念。论文报告了后者，却没有给出实际采用的前者，这是后续评价 real-time 与 fidelity 时最重要的边界。[pdf:E06](_evidence/E06-p006-eq18-fpga-features.png)

### § 7 — 实验设计与结论

**问题一：并行 HDL 是否能在 deadline 内完成一个 DC motor 仿真步？ → 实验：** 作者在 125 MHz FPGA 上实例化约 45 个运算节点，按 expression tree 并行并用 delay 对齐最长路径。**答案：** 作者报告一次 time-step calculation 约需 360 ns。这里验证的是计算 latency，不是数值误差；论文没有报告实际积分步长 \(h\)，也没有展示每步 deadline miss 统计。[pdf:E11](_evidence/E11-p011-performance-tests-table03.png)

**问题二：闭环波形是否具有预期的电机与控制行为？ → 实验：** 工况 A 让电机带额定机械负载启动，并在 2.3 s 卸载；额定参数报告为 \(\omega_r=125\ \mathrm{rad/s}\)、\(V_a=240\ \mathrm{V}\)、\(I_a=10\ \mathrm{A}\)、\(T_m=19\ \mathrm{N\,m}\)，PID 参数为 \(K_p=-0.2339\)、\(K_i=47.6164\)、\(K_d=0.0012\)。作者观察 PID、变换器、滤波器、电枢电流和转速波形。**答案：** 卸载后转速约到 126 rad/s，PID 输出峰值约 260 V，作者报告 settling time 0.15 s、overshoot 3.1%。Figure 11 给出了曲线与指标；这些精确值来自正文或标注，不是本卡从曲线估读。[pdf:E12](_evidence/E12-p012-fig11-transient-metrics.png)

**问题三：开关故障时闭环响应是否符合因果预期？ → 实验：** 工况 B 在 2.2–2.5 s 让 S2、S3 保持高电平，只让 S1、S4 切换。**答案：** 作者报告 PID 为压低速度误差而增大控制量，变换器过调制使滤波器输出与电枢电流下降，转速随之下跌，故障解除后出现软峰并恢复。这个结果证明模型能产生一种合理的故障响应，但没有与示波器、商用 RTDS 或高精度离线求解器做误差对照。[pdf:E13](_evidence/E13-p013-fault-resources-table04.png)

**问题四：资源和更复杂系统的可扩展性如何？ → 实验：** 作者报告当前 DC motor 模型占用少于 1% logic cells、2.8% slice registers、4.3% DSP；再按约 81 个并行运算估算 PMSG wind turbine 模型在 125 MHz 下可得到 648 ns time-step，并用 Table 4 对四块 FPGA 做价格、时钟和估计步长比较。**答案：** 当前样例资源占用低，但 PMSG 和跨器件结果只是按运算数/时钟做的估算，不是综合、place-and-route 后的实测。Table 4 中 500 MHz 对应 90 ps、450 MHz 对应 1 ns 等条目也没有给出推导，不能当作已验证 benchmark。[pdf:E13](_evidence/E13-p013-fault-resources-table04.png)

作者最终结论是：这套 HDL 方法、IEEE 754 浮点实现和 FPGA design flow 能支持低成本实时电气系统仿真，并在样例工况中得到符合电机与电力电子理论预期的结果；其“低成本”依据主要是架构选择自由与不依赖商业包，而不是严格的总拥有成本对照。[pdf:E14](_evidence/E14-p014-conclusion.png)

### § 8 — Take-aways

**5 句话：**

1. 论文展示了从电机连续方程到 Euler 离散、HDL 模块、expression tree、浮点 IP、timing closure 和板上取数的一条端到端路线。
2. 它最有价值的机制是按数据依赖并行算术节点，并让所有模块以最长路径为界同步提交状态。
3. 在作者的 Cyclone 10 GX 样例上，约 45 个运算节点的一次计算 latency 报告为 360 ns，当前模型资源占用较低。
4. 负载卸除和变换器开关故障波形在定性上符合闭环电机系统的因果关系。
5. 但论文没有报告积分步长 \(h\)、定量 reference error、长期数值稳定性或 HIL I/O deadline，因此“算得快”尚不能等同于“物理上足够准且系统级实时”。

**3 句话：** 这是一篇 FPGA 实现方法论文，核心是把离散电气方程的 expression tree 空间并行化。它用 DC motor 闭环波形和 360 ns 计算 latency 展示可行性，却没有把数值误差与实时 deadline 共同闭合。最值得复用的是硬件调度思路，最需要重新验证的是步长、公式一致性和与可信 reference 的误差。

**1 句话：** 论文证明“能把一套浮点电机仿真电路跑得很快”，但尚未充分证明“在明确步长与误差界下仍是可信实时仿真器”。

### § 9 — 最脆弱的假设

最脆弱的假设是：**只要 FPGA 在约 360 ns 内算完一次递推，采用 single precision 与 forward Euler 得到的状态就足以代表真实系统的下一时刻。** 这个假设一旦不成立，论文最核心的“real-time simulator”贡献会退化为“高速执行了一个数值可信度未闭合的离散模型”。

论文为 timing 部分提供了运算 latency、125 MHz 时钟、expression-tree 调度、TimeQuest 流程和资源占用，也用两个工况展示定性合理的波形。它缺少的证据更关键：实际 \(h\) 是多少；\(h\) 与 360 ns latency 的关系；相对于 double-precision、小步长离线 reference 的最大误差和相位误差；长时间能量漂移；开关边沿附近误差；不同负载、参数刚性和控制增益下是否稳定；Eq. (8) 下标歧义在真实 HDL 中如何处理。由于这些缺口，作者展示的是必要的 deadline 能力，而不是充分的数值真实性证明。

### § 10 — 最小复现实验

一周内最值得做的不是复刻整套 GUI 和 Signal Tap，而是复现“同一组离散方程的 FPGA latency 与数值 fidelity 能否同时成立”。

- **数据与模型：** 采用论文的 separately excited DC motor、PID、H 桥平均模型和滤波器；使用正文给出的额定量与 PID 参数。对未报告的电机/滤波参数，只从可获得的作者材料补齐；若仍缺失，就明确使用一组公开参数，验证机制而不声称复现原始曲线。
- **实现：** 写一个 CPU double-precision reference，使用足够小步长的高阶求解器；再写与论文 Eq. (7)–(18) 一致的 IEEE 754 single-precision fixed-step kernel。Eq. (8) 分成 \(V_a/L_f\) 与 \(V_a/L_a\) 两个版本。FPGA 端只实现这一 kernel 和 cycle counter，不必复刻完整采集界面。
- **工况：** 复现 2.3 s 卸载与 2.2–2.5 s S2/S3 故障，再增加一组较低电感或较高控制增益，使系统时间尺度更接近步长限制。
- **测量：** 扫描 \(h\)，记录 FPGA 每步 cycle、deadline miss、转速与电流的最大绝对/相对误差、故障边沿时间偏差、settling time/overshoot 偏差，以及 10 s 长时漂移。
- **支持条件：** 存在一个明确 \(h\) 区间，使 FPGA 对每步都满足 latency \(<h\)，且相对 reference 的误差与闭环指标误差保持在预先声明的容差内，并且公式两个版本中只有一个与 reference 和物理维度一致。
- **反驳条件：** 只有在 \(h\) 小于硬件 latency 时误差才可接受；或在作者声称的实时区间出现明显相位错误、不稳定、deadline miss；或两种 Eq. (8) 实现导致实质不同结果而论文无法判定真实实现。任何一种都足以反驳“现有证据已闭合实时仿真可信度”的强解读。

### § 11 — 最强反例设计

最强反例不是换一台更大的电机，而是构造一个**时间尺度跨越且开关事件密集**的闭环：减小电气电感以产生快速电流动态，提高 PID 带宽，并让 H 桥在负载突变附近发生短时开关故障。这个场景会同时攻击 forward Euler 稳定域、single-precision 舍入、PWM/平均模型的事件表示和 expression-tree 固定 latency。

实验应在相同物理参数下比较三条轨迹：高精度 event-aware reference、论文式 single-precision fixed-step kernel、以及同一步长的 double-precision kernel。若 single 与 double 都偏离 reference，主要问题是离散化或事件处理；若只有 single 偏离，主要问题是数值表示；若数值只有在 \(h\) 小于 360 ns 时才稳定，则硬件虽能高速执行，却无法在该 FPGA 上满足“可信误差下的实时”。再把 Eq. (8) 的两个下标版本纳入比较，可判断原文公式歧义是否会改变故障电流和闭环恢复。这一反例给出了可区分的替代解释，强于笼统地说“模型太简单”。

### § 12 — Follow-up Research Idea

**候选研究方向：面向 FPGA 电气实时仿真的“数值—时序联合证书编译器”。** 这只是由本文证据缺口驱动的候选方向；本卡没有充分检索相关工作，因此不声称 novelty。

（a）未满足的需求是：现有流程能证明 RTL timing closure，却不能证明所选 \(h\)、精度和事件处理在同一硬件 deadline 下仍保持物理误差界。研究目标应从“生成更快电路”改为“自动生成一对可审计证书”：一份是最坏情况 step latency，一份是给定工况包络内的稳定性与误差界。

（b）它可能产生本领域认可的价值，是因为电力电子和 HIL 更关心故障、保护和快速开关附近是否可信，而不仅是平均吞吐。若证书能把参数范围、步长、浮点误差、事件密度与 FPGA 资源联系起来，工程师就能知道一个模型何时允许接入真实控制器。

（c）可借鉴的相邻工具包括 synchronous dataflow scheduling、worst-case execution time analysis、interval/affine arithmetic、control-oriented numerical stability analysis，以及对浮点 RTL 的 formal equivalence。expression tree 不再只用来排并行度，还携带每个节点的误差传播和 latency。

（d）第一个能够证伪它的实验，是在本文 DC motor 模型上自动生成“安全 \(h\) 与参数包络”，然后用 §11 的刚性与开关故障工况寻找包络内反例。只要出现 deadline 已满足但误差越界，或工具给不出比暴力仿真更有用的边界，这个方向的核心主张就失败。

（e）它与本文方法的实质区别在于：本文从方程生成并行硬件，再用定性波形说明可行；候选方向把“硬件完成得多快”和“这个离散答案有多可信”作为同一个编译与验收问题。它不是再增加一个求解模块，而是改变实时仿真器的完成定义。
