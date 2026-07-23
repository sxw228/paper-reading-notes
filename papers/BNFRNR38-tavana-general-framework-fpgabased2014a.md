# A General Framework for FPGA-Based Real-Time Emulation of Electrical Machines for HIL Applications

- 作者：Nariman Roshandel Tavana；Venkata Dinavahi
- 出处：IEEE Transactions on Industrial Electronics, Vol. 62, No. 4
- 年份：2015（在线发表时间为 2014 年）
- DOI：10.1109/TIE.2014.2361314
- Zotero key：BNFRNR38

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“能否在 FPGA 上算一个电机模型”，而是更实际的工程问题：怎样用一套统一的数字硬件框架，把多类电机模型做成能够按真实时间推进、可以接入 HIL（hardware-in-the-loop，硬件在环）测试的 FPGA emulator，并弄清固定点/浮点、并行/流水、图形化/文本化实现之间真正的代价。作者针对 induction motor、synchronous generator、line-start permanent-magnet synchronous motor（LSPMSM）和 dc motor 给出实现，并把比较轴落到步长、准确性和资源占用，而不只报告“能跑”。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

它重要，是因为 HIL 的模型必须在每个仿真步长截止前交付结果；离线仿真慢一些只是等待更久，HIL 超时则意味着被测控制器收到的电压、电流或转矩已不再对应物理时间。论文指出，电机瞬态需要小步长，而模型复杂度、计算精度与实时 deadline 之间存在直接冲突；FPGA 的硬连线并行、DSP、片上存储和纳秒级时钟为打破这个冲突提供了可能。[pdf:E01]（PDF 物理页 1，Introduction）因此，这项工作的价值不是替代电机本体，而是在不破坏真实设备的条件下，让 controller、drive 和 protection 在启动、负载突变和故障等危险工况中接受可重复测试。

需要先限定“general”的含义：论文统一的是可写成 state-space equations 的模型到 FPGA 的实现骨架，不是证明任意电机物理现象都已被高保真覆盖。作者采用对称绕组、参数恒定的 lumped \(dq\) 模型，并在结论中把 spatial 与 nonlinear phenomena 留给未来工作。[pdf:E02]（PDF 物理页 2，Section III 开头）[pdf:E11]（PDF 物理页 11，Conclusion）

## § 2 — 前人工作与不足

论文之前已有三条路线。第一，MATLAB/Simulink、JMAG、ANSYS 等离线工具已经能模拟电机，但不承担与外部硬件同步的硬实时 deadline。第二，已有 FPGA 电机实时仿真多数采用 fixed-point；第三，已有工作也做过 32-bit floating-point synchronous generator，但面向 nodal analysis 的单类模型。[pdf:E01]（PDF 物理页 1，Introduction）相关代表包括 Matar 与 Iravani 的 AC machine massively parallel implementation，以及 Chen 与 Dinavahi 的 universal machine/line floating-point hardware emulation；论文的参考文献给出了这两项工作的完整出处。[pdf:E13]（PDF 物理页 13，References [20]–[21]）

不足不在于这些方法“没有 FPGA”，而在于比较边界没有闭合：当 fixed-point 更快、floating-point 数值范围更宽时，最终 HIL 准确性同时受一个步长内所需 clock cycles、可达到时钟、离散化截断误差、量化误差和资源复用方式影响。仅在离线条件比较数值格式，会漏掉“更精确的单次运算迫使实时步长变长，反而累计更大时间推进误差”的机制。作者据此把 32-bit fixed-point 与 schematic/highly-parallel 实现配对，把 IEEE-754 single-precision floating-point 与 VHDL/deeply-pipelined 实现配对，再在同一 state-space 框架下比较。[pdf:E02]（PDF 物理页 2，Section II 末）

还要看到一个后文会成为批评重点的缺口：论文同时改变了 number representation、programming method 和 spatial architecture。于是它能比较两套完整工程方案，却不能仅凭这些结果把差异因果地归到“fixed versus floating”某一个因素。

## § 3 — 重建作者的思考路径

以下是基于论文背景与结构的合理重建，不是作者逐字陈述。

第一步，研究者从 HIL 的硬约束出发：每个 \(T_s\) 内必须完成输入生成、开关事件处理、状态更新和输出计算，否则实时性直接失败。第二步，把不同电机都整理为 \(\dot{x}=Ax+Bu,\ y=Cx+Du\)，让“换电机”主要变成换矩阵、状态和参数，而不是重写整个控制时序。[pdf:E03]（PDF 物理页 3，Eq. (3) 与相邻变量定义）

第三步，选 explicit integration。隐式法每步要求 root finding，不利于确定延迟；forward Euler 只依赖上一步历史量，适合寄存器和 RAM 驱动的数据流。FPGA 的小 clock period 又允许把 \(T_s\) 压到远小于电气、机械 time constants，以换取显式法的稳定性余量。[pdf:E03]（PDF 物理页 3，Eq. (6) 前后的离散化讨论）

第四步，不再问“fixed 还是 floating 谁理论精度高”，而是问“在 deadline 和芯片资源约束下，哪套 datapath 给出的端到端波形更接近参考”。资源便宜的 fixed-point 可以复制算子形成并行网络；昂贵的 floating-point 更适合流水复用。最后，用离线参考、真实 induction motor 和多类故障/负载波形逐层检验：先证明数字实现没写错，再证明至少一类真实机器能对上，最后展示框架可迁移到不同 machine equations。

## § 4 — 核心 Intuition

核心 intuition 是：先把不同电机压缩成同一种 state-space 时间推进问题，再让 FPGA 的 architecture 与数值格式共同决定“每个物理步长内怎样把计算排完”。固定点单算子便宜，适合大规模并行以缩短 \(T_s\)；浮点单算子昂贵，适合深流水提高 throughput、减少复制，但 latency 会推高可用 \(T_s\)。因此，HIL 中的准确性不是 bit precision 的单调函数，而是量化误差与时间离散误差在硬实时约束下的合成结果。[pdf:E02]（PDF 物理页 2，Section II）[pdf:E07]（PDF 物理页 7，Table I 与 Section V-A）

## § 5 — 具体方法与完整 Pipeline

以三相 induction motor 从静止启动为例，完整 pipeline 如下。

1. **建模与统一接口。** 将 phase-domain 电压、电流和 flux linkage 变换到旋转 \(dq0\) frame，以降低随 rotor position 变化的 inductance matrix 复杂度；选择 flux linkages 为状态、供电电压为输入、电流为输出，再把 electrical 与 mechanical equations 放进统一 state-space 形式。[pdf:E02]（PDF 物理页 2，Eq. (1)–(2)）[pdf:E03]（PDF 物理页 3，Eq. (3)–(5)）
2. **离散时间推进。** 用 first-order Adams–Bashforth，也就是 forward Euler，把下一步状态写成上一时刻状态、输入和矩阵的显式函数。每步历史状态放在寄存器或 dual-port RAM 中；论文没有采用隐式迭代，也没有报告多速率积分。[pdf:E03]（PDF 物理页 3，Eq. (6)）[pdf:E06]（PDF 物理页 6，Eq. (7) 与 RAM 说明）
3. **输入与事件。** Source Module 生成三相正弦电压。浮点实现把半周期 \(4096=2^{12}\) 个 cosine samples 放入 LUT，对应 \(\Delta\theta=\pi/4096\)；Timer & Switch Module 用 RAM 中的预定开关时刻翻转 switch bits，并用 `dtOver` 判断整步计算是否在 \(T_s\) 前完成。[pdf:E04]（PDF 物理页 4，Fig. 2–3 与相邻正文）这里的“事件处理”是按预存时刻切换，不是自适应零交叉定位。
4. **主控制顺序。** Main Control 先命令 Source Module 并检查开关状态，随后启动 Electrical Machine Module；收到 `EMdone` 后输出实时信号，再检查 `dtOver`。若本步超过 \(T_s\)，系统输出 error 并终止实时 emulation。[pdf:E04]（PDF 物理页 4，Main Control 与 Timer & Switch 正文）
5. **floating-point/VHDL 路线。** FSM 在 S0 更新 \(A\)、并行计算 \(K,K^{-1}\)，S1 做 \(abc\to qd0\)，S2 更新 flux states，S3 并行求 currents 与 torque，S4 变回 \(abc\)，S5 求 speed 与 position。[pdf:E03]（PDF 物理页 3，Fig. 1）核心 datapath 用 sparse matrix-vector multiplication（SprMxMul）和 FLPMAS。稀疏条目保存 32-bit value、4-bit column index 与 1-bit row label；累加器采用 `40.100` fixed-point 中间格式，并用两个交替 accumulator 消除相邻 row 的 stall。FLPMAS 最长路径为 19 clock cycles。[pdf:E05]（PDF 物理页 5，Fig. 4–5 与相邻正文）
6. **fixed-point/schematic 路线。** 在 MATLAB/Simulink 与 Xilinx System Generator 中搭建定点数据流，自动生成 HDL；Fig. 6 展示 source、frame transformation、state-variable calculator、output calculator 和 mechanical unit。并行支路用寄存器对齐 latency，dual-port RAM 保存 \(n-1\) 步历史量，place-and-route 后再依据 area/time 调整。[pdf:E06]（PDF 物理页 6，Fig. 6 与 Section IV-B）
7. **FPGA 与 I/O。** 资源统计以 Xilinx Virtex-7 XC7VX485T 为目标，实时波形由 VC707 board 的采集卡输出到 oscilloscope；低电平数字/模拟 I/O 可通过功率 amplifier 与真实 HIL 设备连接。[pdf:E08]（PDF 物理页 8，Section V-C）[pdf:E09]（PDF 物理页 9，Section VI 开头）

这套方法的“通用性”来自矩阵化接口、可重复的 step scheduler 和可替换 datapath，而不是自动从任意 machine description 生成最优架构。论文也没有报告自动 word-length optimization、运行时 adaptive step、multi-FPGA partition 或闭环 controller-under-test 的实验。

## § 6 — 核心数学推导（无形式化数学则跳过）

物理上，state-space 的作用是把“磁链如何积累”与“电流、转矩如何由当前磁链得到”分开。论文用

\[
\dot{\mathbf{x}}(t)=\mathbf{A}\mathbf{x}(t)+\mathbf{B}\mathbf{u}(t),\qquad
\mathbf{y}(t)=\mathbf{C}\mathbf{x}(t)+\mathbf{D}\mathbf{u}(t)
\]

统一描述不同电机，其中 \(\mathbf{x}\in\mathbb{R}^h\) 是 state vector，\(\mathbf{u}\in\mathbb{R}^p\) 是 input，\(\mathbf{y}\in\mathbb{R}^q\) 是 output；文中选择 \(\lambda_{qdo}\)、\(V_{qdo}\)、\(I_{qdo}\) 分别作为状态、输入和输出。[pdf:E03]（PDF 物理页 3，Eq. (3)）

电磁与机械耦合由

\[
T_e=\frac{3}{2}\frac{P}{2}\left(\lambda_{ds}i_{qs}-\lambda_{qs}i_{ds}\right),
\qquad
\dot{\omega}_r=\frac{P}{2J}\left(T_e-T_{\mathrm{mech}}-T_{\mathrm{damp}}\right)
\]

连接起来。第一式表示 \(d/q\) 轴磁链与正交电流的交叉作用产生 electromagnetic torque；第二式是净转矩经 inertia \(J\) 转换为 rotor electrical speed 的变化率。[pdf:E03]（PDF 物理页 3，Eq. (4)–(5)）

关键离散化是

\[
\begin{aligned}
\mathbf{x}(t)&=\mathbf{x}(t-T_s)+T_s\big[\mathbf{A}(t-T_s)\mathbf{x}(t-T_s)
+\mathbf{B}(t-T_s)\mathbf{u}(t-T_s)\big],\\
\mathbf{y}(t)&=\mathbf{C}(t)\mathbf{x}(t)+\mathbf{D}(t)\mathbf{u}(t).
\end{aligned}
\]

它把 derivative 近似为一个步长内的常斜率：先用上一时刻的信息算增量，再写回新状态。工程优势是无 root finding、dependency 固定、容易形成确定 latency；代价是 truncation error 与稳定性强烈依赖 \(T_s\)。[pdf:E03]（PDF 物理页 3，Eq. (6) 及前后文）

论文进一步把 induction motor 第一行状态更新展开为

\[
\lambda_{qs}(nT_s)=\lambda_{qs}((n-1)T_s)+T_s\left[
A_{11}\lambda_{qs}((n-1)T_s)+A_{14}\lambda_{qr}((n-1)T_s)
+V_{qs}((n-1)T_s)\right],
\]

直接对应 Fig. 6 中的乘法器、加法器、寄存器与 history RAM。这一展开说明“公式到 FPGA”不是象征性映射：每一项都成为一条可调度的数据路径，寄存器负责让并行支路同拍到达。[pdf:E06]（PDF 物理页 6，Eq. (7) 与 Fig. 6）

## § 7 — 实验设计与结论

**问题 1：两套实现能否满足实时步长，并且谁更快？ → 实验：** 对四类电机分别综合 fixed-point/highly-parallel 与 floating-point/deeply-pipelined 架构，报告 latency 和最小 time-step。**答案：** induction motor 为 \(46\) cycles / \(230\,\mathrm{ns}\) 对 \(234\) cycles / \(1.755\,\mu\mathrm{s}\)；synchronous generator 为 \(55/275\,\mathrm{ns}\) 对 \(256/1.920\,\mu\mathrm{s}\)；LSPMSM 为 \(52/260\,\mathrm{ns}\) 对 \(240/1.800\,\mu\mathrm{s}\)；dc motor 为 \(29/145\,\mathrm{ns}\) 对 \(126/0.945\,\mu\mathrm{s}\)。fixed 与 floating implementation 的 clock periods 分别是 \(5\) 与 \(7.5\,\mathrm{ns}\)。[pdf:E07]（PDF 物理页 7，Table I 与 Section V-A）

**问题 2：更高 arithmetic precision 是否自动带来更准的 HIL 波形？ → 实验：** induction motor 从静止启动，以 SimPowerSystems 的 double-precision RK4、\(100\,\mathrm{ns}\) 步长为 reference；比较 VHDL/SP floating \(1.755\,\mu\mathrm{s}\)、M-file/DP 同步长、XSG/32-bit fixed \(230\,\mathrm{ns}\)、M-file/DP \(230\,\mathrm{ns}\)。**答案：** 所有方法在大尺度图上接近 reference，但局部放大后，SP floating hardware 的偏差最大；\(230\,\mathrm{ns}\) fixed hardware 更接近 reference，却出现定点范围/小数位不足造成的 staircase。这个实验支持“deadline 下步长误差可以压过单次浮点精度优势”，不支持“fixed-point 数学上比 floating-point 更精确”。[pdf:E07]（PDF 物理页 7，验证设置与解释）[pdf:E08]（PDF 物理页 8，Fig. 8 caption）

**问题 3：虚拟电机是否接近真实电机？ → 实验：** 一台 3-hp Baldor induction motor 与 dc generator 机械耦合，直接接三相电源启动；FPGA 输出由 ChipScope 采集，与 current probe 和 shaft encoder 的测量叠加。**答案：** 电流约 \(0.4\,\mathrm{s}\) 后进入稳态，模拟 speed 紧随实测；偏差在低速/瞬态更明显，作者归因于 shaft backlash 放大 torque pulsation，以及 lumped \(qd\) 模型不能表达真实机器的 distributed/spatial effects。[pdf:E08]（PDF 物理页 8，Fig. 9–10 与相邻正文）

**问题 4：资源结论是什么？ → 实验：** 在 XC7VX485T 上统计 registers、LUTs、DSPs。**答案：** 以 induction motor 为例，fixed 方案使用 \(25{,}127\) registers、\(36{,}567\) LUTs、\(26\) DSPs；floating 方案使用 \(6{,}689\) registers、\(29{,}115\) LUTs、\(38\) DSPs。四类模型中，massively parallel fixed 方案都花更多 LUTs，而 deeply pipelined floating 方案都花更多 DSPs；register 数在 dc motor 上反转为 floating 更多，说明资源结论依赖模型结构。[pdf:E09]（PDF 物理页 9，Table II）

**问题 5：框架能否覆盖不同机器与扰动？ → 实验：** 用连接 VC707 的 500-MHz four-channel oscilloscope 观察 induction motor、synchronous generator、LSPMSM 与 shunt dc motor。同步机端口三相故障在 \(t=0.25\,\mathrm{s}\) 发生、\(t=0.5\,\mathrm{s}\) 清除；LSPMSM 在 \(t=1\,\mathrm{s}\) 加到 \(80\%\) nominal torque，\(t=1.5\,\mathrm{s}\) 后故障并在 \(1.65\,\mathrm{s}\) 清除；dc motor 约 \(t=2\,\mathrm{s}\) 进入稳态，\(t=2.7\,\mathrm{s}\) 加 rated load。[pdf:E09]（PDF 物理页 9，Fig. 11 与 cases）[pdf:E10]（PDF 物理页 10，Fig. 12–14 与正文）**答案：** 波形呈现了预期的 acceleration、loss/recovery of synchronism 和 load-induced current/speed changes，但论文只为 induction motor 展示了离线叠加与真实机器实验；其他三类的离线验证被作者称已完成，却未逐图给出。因此，证据支持“同一框架能生成多类实时 transient”，不能外推为“四类机器均有同等强度的物理实验 fidelity”。

## § 8 — Take-aways

**5 句话：**  
1. 论文用 state-space 接口把四类电机纳入同一个 FPGA step scheduler。[pdf:E01]（PDF 物理页 1，Abstract）  
2. fixed/highly-parallel 方案以更多并行算子换来更短步长，floating/deeply-pipelined 方案以流水复用降低部分 LUT/register 占用，但增加 DSP 与 latency。[pdf:E07]（PDF 物理页 7，Table I）[pdf:E09]（PDF 物理页 9，Table II）  
3. HIL 准确性取决于 arithmetic error 与 time-discretization error 的共同作用，浮点并不自动获胜。[pdf:E08]（PDF 物理页 8，Fig. 8）  
4. induction motor 的实测比较给出了真实世界锚点，同时也暴露 lumped \(qd\) 模型与 shaft dynamics 的偏差来源。[pdf:E08]（PDF 物理页 8，Fig. 9–10）  
5. 多机器 case studies 证明框架可迁移，但物理实验强度不均衡，不能把一个电机的验证强度复制到其余机器。[pdf:E09]（PDF 物理页 9，Section VI）

**3 句话：** 这是一篇“模型统一 + 架构比较 + HIL 波形验证”的工程论文。它最有价值的结论是：实时 deadline 会改变数值精度的排序，短步长可能比更高单次 precision 更重要。它最需要谨慎解读之处是 fixed/float、parallel/pipeline、schematic/VHDL 被成组改变，比较结果是方案级而不是单因素因果结论。

**1 句话：** 在 FPGA HIL 中，正确的问题不是“哪种数值格式更精确”，而是“在同一真实时间与资源预算下，哪套模型—离散化—datapath 组合最忠实”。

## § 9 — 最脆弱的假设

失败代价最大的假设是：论文比较的两套完整实现足以代表并区分 fixed-point 与 floating-point 的本质优劣。实际上，fixed-point 同时采用 schematic method 和 massively parallel architecture，floating-point 同时采用 VHDL/TPL 和 deeply pipelined architecture；Table I 与 Table II 观察到的是三个因素共同变化后的结果。[pdf:E02]（PDF 物理页 2，Section II 末）[pdf:E07]（PDF 物理页 7，Table I）[pdf:E09]（PDF 物理页 9，Table II）

这个假设在实际中很可能不成立，因为同一种数值格式也可以做不同程度的并行、流水与资源共享；同一种 architecture 也可以采用 mixed precision。综合工具版本、DSP primitive、timing constraint 和 sparsity 都会改变 Pareto frontier。若 32-bit fixed 也做深流水，或 SP floating 也复制更多 datapath，在相同步长或相同资源预算下结论可能改变。

论文确实证明两套被实现方案都能运行，并给出 latency、time-step 与资源数字；它没有提供 \(2\times2\) factorized design，也没有在 equal-\(T_s\)、equal-area 或 equal-throughput 条件下隔离 number format。故“这两套工程方案的实测差异”是论文直接证据；“差异主要由 fixed/float 本身导致”仍是不确定的因果解释。

## § 10 — 最小复现实验

一周内最值得复现的是 induction motor 启动瞬态，因为它同时有 Appendix B 参数、离线 reference、FPGA 两套步长和真实实验锚点。采用论文的 3-hp、230-V 参数 \(r_s=0.5\,\Omega,\ r_r=0.51\,\Omega,\ l_{ls}=l_{lr}=4\,\mathrm{mH},\ l_m=89.4\,\mathrm{mH}\)。[pdf:E12]（PDF 物理页 12，Appendix B-i）

最小方案：

1. 实现同一 \(dq\) state-space 与 forward Euler 更新，先用 double-precision RK4、\(100\,\mathrm{ns}\) 生成 reference。
2. 做两个 bit-accurate datapath：32-bit fixed 与 IEEE-754 single precision；先复现论文的 \(230\,\mathrm{ns}\) 和 \(1.755\,\mu\mathrm{s}\)，再增加一个 equal-\(T_s\) 组，把 representation 与 step-size 分开。
3. 输入为从静止直接启动的三相电源，至少测前两个 stator-current oscillations；记录 deadline miss、NRMSE、peak error、稳态 amplitude error、LUT/register/DSP 和 achieved clock。
4. 若论文步长配置下 fixed 的 NRMSE 低于 floating，而 equal-\(T_s\) 后 floating 反超或相当，则支持论文的核心机制“步长压过单次 precision”；若在论文配置下 floating 仍更准，或 fixed 无法在报告资源/时序数量级内达到 \(230\,\mathrm{ns}\)，则反驳核心 claim。

论文没有给出数值化 error threshold，因此复现前应预注册，例如“前 \(30\,\mathrm{ms}\) 电流 NRMSE 差异超过 10% 才判定排序具有工程意义”，避免只靠 Fig. 8 的视觉放大作结论。报告的比较设置与波形定位见 PDF 物理页 7–8。[pdf:E07][pdf:E08]

## § 11 — 最强反例设计

最强反例不是再找一条“对不上”的波形，而是拆掉 comparison confound：做完整的 \(2\times2\) 实验，number format 取 fixed/floating，architecture 取 massively-parallel/deeply-pipelined；四组使用同一 state equations、forward Euler、FPGA family、toolchain、\(T_s\) 和 I/O deadline。随后在三种约束下分别画 accuracy–area–latency Pareto frontier：equal time-step、equal LUT+DSP budget、equal throughput。

压力工况选 induction motor 的低速启动与饱和附近电流，再加 synchronous generator terminal fault。前者会放大量化和 lumped-model error，后者会放大状态跃迁与动态范围需求；论文已有相应启动与故障场景，但没有 factorized architecture comparison。[pdf:E08]（PDF 物理页 8，induction motor validation）[pdf:E09]（PDF 物理页 9，synchronous generator fault）

如果 fixed/deep-pipeline 在 equal-\(T_s\) 下比论文的 fixed/parallel 大幅省资源，或 floating/parallel 在 equal-area 下也能缩短步长并反转准确性排序，就说明论文观察到的优势主要来自 architecture 和 tool flow，而非 number representation。这不会否定其两套实现“可以工作”，但会推翻把方案级结果泛化为 fixed-versus-floating 规律的最强解释。

## § 12 — Follow-up Research Idea

电气与 HIL 领域通常看重可重复的实时 deadline、误差边界、资源/功耗可实现性，以及在真实 controller 或 power interface 下的验证，而不是只看算法新颖性。基于第 9 节，候选研究方向是把问题从“选择 fixed 或 floating”改写为：**在给定 FPGA 资源、硬实时 deadline 和一组物理工况下，自动合成具有可验证 fidelity bound 的 mixed-precision、多架构电机 emulator。** 这是候选想法，尚未做充分相关工作检索，不声称 novelty。

（a）未满足需求是：当前方案把 precision、parallelism、pipeline depth 和 \(T_s\) 人工绑在一起，设计者不能知道某个波形误差究竟来自模型、离散化还是量化。  
（b）研究价值在于把“实时运行”升级成“在指定故障集合上，deadline 永不丢失且输出误差有可审计上界”，更接近 HIL 的安全使用条件。  
（c）可借鉴 compiler 的 scheduling/design-space exploration、mixed-precision error analysis，以及 robust control 的 uncertainty envelope；把每个 state update 的 sensitivity 转成 word length、pipeline 和 replication 的联合约束。  
（d）第一个证伪实验是：在 induction motor 启动与 synchronous generator fault 两个 workload 上，给自动方案与四种手工 baseline 相同 XC7VX485T 资源和 deadline；若自动方案不能同时改善 worst-case error 与资源，或其 bound 覆盖不了实测误差，这个研究命题就失败。论文提供了两类场景和报告资源作为初始 benchmark。[pdf:E09]（PDF 物理页 9，Table II 与 generator case）  
（e）它与本文的实质区别是：本文验证两条预先选择的 implementation paths；新方向把 architecture、precision 与 time-step 当成可独立搜索的变量，并要求从“观察到接近”提升为“在规定工况集合内可验证地不超时、误差不越界”。这样也能自然纳入论文明确未覆盖的 spatial/nonlinear machine phenomena，而不是把它们继续留作未量化的未来工作。[pdf:E11]（PDF 物理页 11，Conclusion）
