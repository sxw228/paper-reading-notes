# Scalable and Real-Time Power System Simulation Based on Heterogeneous CPU-FPGA Co-operation

- 作者：Hangyu Yang, Jiyuan Liu, Mingwang Xu, Wei Gu, Yongming Tang, He Li
- 出处：2025 IEEE International Symposium on Circuits and Systems (ISCAS)
- DOI：10.1109/ISCAS56072.2025.11043656
- 阅读边界：本卡只使用源 PDF。`[pdf:E..]` 指向同目录 `_evidence/` 中按 PDF 物理页裁切的上下文图片。论文事实、基于证据的推断和本文的批评性判断在行文中明确区分。

## § 1 — 研究问题与重要性

这篇论文处理的不是“能不能把一个电力电子模型放到 FPGA 上”，而是一个更具体的系统问题：怎样让同一套实时仿真系统同时容纳规模不同、拓扑不同、时间尺度不同的电力系统模型。作者观察到，现有 FPGA accelerator 往往针对单一拓扑做深度优化，速度快，却很难在 boost、half-bridge、full-bridge、三相 VSC 之间复用；CPU 更灵活，但在很小的仿真步长下，计算与 I/O 延迟又可能使每一步越过 deadline。[pdf:E01][pdf:E02]

这里的“实时”有严格含义：一次数据接收、计算和发送的总延迟 \(T_l\) 必须不超过仿真步长 \(\Delta t\)。一旦 \(T_l>\Delta t\)，计算结果虽然可能数值正确，却已经错过它对应的物理时刻。论文把 GaN/SiC 高频开关的快速暂态作为需求背景，并称小步长仿真通常要比开关频率快 20–100 倍；因此，问题同时受数值稳定性、计算量和通信 deadline 约束。[pdf:E01][pdf:E02]

作者的目标是用异构分工把这组矛盾拆开：CPU 负责大规模、较大步长、对延迟不敏感的 system-level grid；FPGA 负责高频开关附近的小步长、低延迟细粒度计算；CPU 再汇总结果用于电路控制，多块 FPGA 通过 Ethernet 扩展。[pdf:E04][pdf:E06][pdf:E07] 这类系统如果成立，价值不只在单个 kernel 加速，而在于同一平台可以让慢的网络尺度与快的器件/变换器尺度共存。不过，论文真正展示的是两块 FPGA 与四种变换器拓扑，尚未展示随系统规模增长仍保持实时的完整证据，这一点不能由题名中的 “Scalable” 自动推出。[pdf:E06][pdf:E07]

## § 2 — 前人工作与不足

论文把既有 FPGA 实时仿真工作分成两条路线。第一条通过 prediction correction、non-iterative decoupling 等算法降低 latency，作者概述其中一些工作达到 25 ns；第二条通过简化模型降低资源消耗，例如面向特定多电平 full-bridge 的简化 state-space 方法。作者认为，两条路线都能在各自目标上取得很高速度或很低资源，但常把模型、数据通路和 bitstream 固定到一个拓扑，因此没有解决多拓扑复用。[pdf:E03]

Table II 给出的比较也体现了这个定位：对比项多半只支持 Boost、HB、FB 或 VSC 中的一类，而本文的四个实现列均标为支持 Boost/HB/FB/VSC；论文还明确声称切换这些 converter topology 不需要 bitstream regeneration。[pdf:E07][pdf:E08] 因而，本文要填补的不是绝对最低 latency 空白——表中已有 50 ns 乃至正文提到的 25 ns 工作——而是“一个硬件实现同时支持多种拓扑，并保持约百纳秒 accelerator latency”的组合空白。[pdf:E03][pdf:E07]

需要谨慎的是，论文对 prior work 的不足主要依据其支持的 model 类型和作者概述，未用统一 workload 重新实现所有 baseline。Table II 中平台、年份、频率、量化格式和模型并不相同，所以它能说明本文覆盖面较广，却不能单独证明所有性能差异都来自 flexible decomposition 或 DFP。[pdf:E07] 这是比较设计的边界，不应把异构平台的优势写成已被严格隔离的因果结论。

## § 3 — 重建作者的思考路径

可以从四个在本文方案出现之前就成立的约束重建其思考路径。

第一，实时 deadline 只关心一整步是否在 \(\Delta t\) 内结束，而不是所有子系统都用同一硬件、同一步长计算。于是，把大电网慢变量和高频开关快变量强行放进单一求解器并不是必要前提。[pdf:E01][pdf:E04]

第二，电容、电感、电压源、开关和二极管都可以经过 Norton 等值和 binary conductance 表示进入 nodal analysis。这样，不同 converter 的差异可主要落到 admittance/connectivity matrix，而不是每个拓扑重新发明一条求解算法。[pdf:E03][pdf:E04]

第三，nodal update 的主计算是若干 matrix-vector multiplication（MVM）。若矩阵中的零元、对角块和互为转置的块可被识别，就能用 domain decomposition、CSR 和流水 MVM 保留一条通用数据通路，只把 topology-dependent 数据换进去。[pdf:E04][pdf:E05]

第四，同一 nodal loop 的 current stage 与 voltage stage 需要的数值范围不同。与其给全链路统一留出最坏情况位宽，不如保持统一 48-bit 总宽度，却让 current MVM 使用更多整数位、voltage MVM 使用更多小数位，再在阶段间移位缩放。[pdf:E05][pdf:E06]

沿着这四步，异构架构自然出现：CPU 维护更灵活、更大尺度的系统状态并传送 switch-state/topology 数据；FPGA 保存可复用的 topology-aware MVM engine，以固定小步长推进快子系统；Ethernet/DPDK 负责把多块 FPGA 接回 CPU。[pdf:E03][pdf:E04][pdf:E07] 这是一条基于论文证据的重建，不是作者逐字陈述的研发历史。

## § 4 — 核心 Intuition

核心 intuition 是把“拓扑变化”从“重新设计硬件”改写为“向同一条稀疏矩阵数据通路送入不同的结构与参数”。CPU 吸收规模和控制层面的灵活性，FPGA 固定执行 deadline 最紧的 nodal MVM；这样，异构分工沿时间尺度而不是沿某个具体 converter 名称划分。[pdf:E03][pdf:E04][pdf:E05] DFP 再利用 current stage 和 voltage stage 的不同动态范围，让通用性不必靠统一的过宽数值格式支付全部资源代价。[pdf:E05][pdf:E06]

## § 5 — 具体方法与完整 Pipeline

以 CPU 上的大步长电网连接一个需要 \(0.5\,\mu s\) 小步长推进的三相 VSC 为例，论文的方法可还原为以下 pipeline。

1. **元件统一建模。** Switch/diode 用 \(G_{\mathrm{on}}\) 与 \(G_{\mathrm{off}}\) 两个 conductance state 表示；其余元件用 Norton equivalent current source 与等效导纳表示。不同 converter 因而共享 nodal analysis 形式。[pdf:E03]
2. **CPU/FPGA 按时间尺度分工。** CPU 处理大规模、较大步长、delay-insensitive 的 system-level grid；FPGA 在预定义固定步长内循环推进高频开关子系统。CPU 还向 FPGA 传送 switch-state admittance matrix \(G_{\text{nodal}}^i\)，并汇总 FPGA 返回结果用于 circuit control。[pdf:E03][pdf:E04][pdf:E06][pdf:E07]
3. **拓扑编码与压缩。** 拓扑被表示为 directed graph matrix \(M_{\text{nodal}}\)：零元素表示节点不连接，非零元素给出等效 conductance 及方向。FPGA 按 row-major 顺序用 Zero-CMP 扫描 \(G_{\text{nodal}}^i\)，非零元触发 counter/index generation；domain decomposition 把矩阵分成更低维块，CSR 保存非零值与索引，ping-pong buffer 用来降低 read-after-write latency。[pdf:E03][pdf:E04][pdf:E05]
4. **按依赖链执行四段 MVM。** MVM(A) 由上一时刻 branch voltage 和 injected current 得到 history current；加入 source current 后，MVM(B) 形成 injected current；MVM(C) 乘以 inverse admittance 得到 nodal voltage；MVM(D) 再映射回 component branch voltage。后一个阶段消费前一个阶段的结果，因此算法不是四个彼此独立的 MVM，而是一条跨 timestep 的有序数据依赖链。[pdf:E04][pdf:E05]
5. **在每个 MVM 内流水。** 矩阵元素按列流入 multiplier，行级并行完成乘法与累加，再由 serial-to-parallel 单元输出。论文称 \(M\) 维矩阵与向量在 \(M\) 个 clock cycle 后得到结果；这里的 parallelism 位于一段 MVM 的行之间，而 A→B→C→D 的数据依赖仍然保留。[pdf:E05][pdf:E06]
6. **分阶段量化。** current MVM(A/B) 使用 Q(48,20)，给较大的 current/等效导纳留更多整数位；voltage MVM(C/D) 使用 Q(48,30)，给 voltage update 留更多 fractional bits。阶段间通过 shift register array 调整 scale，48-bit 总宽度与 DSP48 architecture 对齐。[pdf:E05][pdf:E06]
7. **系统互连与扩展。** 实物系统由两颗 AMD EPYC 9554、256 GB DDR5 和两块 XCKU060 FPGA 组成；多 FPGA board 通过 Ethernet switch 接入，DPDK zero-copy 用于降低数据搬运。Figure 5 给出了 CPU server、FPGA accelerator、Ethernet 和 GUI 的实物连接，而不是只给出算法框图。[pdf:E06][pdf:E07]

论文没有说明两个关键实现细节：当 switch state 变化时，\(G_{\text{nodal}}^{-1}\) 由谁、何时重新形成；CPU 大步长域与 FPGA 小步长域之间如何做数值耦合、同步和误差控制。Figure 4 显示 MVM(C) 直接消费 \(G_{\text{nodal}}^{-1}\)，但正文只明确描述 CPU 传送 \(G_{\text{nodal}}^i\) 与 FPGA 更新等效导纳。[pdf:E03][pdf:E04][pdf:E05] 因而，不能从现有描述推断在线矩阵求逆的硬件实现，也不能推断该系统已经形成完整 PHIL/HIL 接口。

## § 6 — 核心数学推导

论文的数学主体是 discrete nodal update，而不是一个新收敛定理。Equation (1) 用一组 selector 把三类元件写成统一等效导纳：

\[
G_{\mathrm{eq}}^n=\alpha\frac{2C}{\Delta t}+\beta\frac{\Delta t}{2L}+\xi\frac{1}{R_s},
\]

其中 capacitor 取 \((\alpha,\beta,\xi)=(-1,0,0)\)，inductor 取 \((0,1,0)\)，voltage source 取 \((0,0,1)\)。直觉是：离散后的储能元件在当前 step 对外表现为一个等效 conductance 加一个携带过去状态的 history current；开关/二极管则用 on/off conductance 改变 nodal matrix。[pdf:E03][pdf:E04]

接下来 Eqs. (2)–(6) 给出一步更新：

\[
I_{\mathrm{his}}^{t_{n+1}}
=G_{\mathrm{nodal}}V_s^{t_n}+I_{\mathrm{inj}}^{t_n},
\]

\[
I_s^{t_{n+1}}=
\begin{cases}
0,&\text{otherwise},\\
U_s^{t_{n+1}}G_{R_s},&\text{AC/DC voltage source},
\end{cases}
\]

\[
I_{\mathrm{inj}}^{t_{n+1}}
=M_{\mathrm{nodal}}
\left(I_{\mathrm{his}}^{t_{n+1}}+I_s^{t_{n+1}}\right),
\]

\[
V_{\mathrm{nodal}}^{t_{n+1}}
=G_{\mathrm{nodal}}^{-1}I_{\mathrm{inj}}^{t_{n+1}},
\qquad
V_s^{t_{n+1}}
=M_{\mathrm{nodal}}V_{\mathrm{nodal}}^{t_{n+1}}.
\]

物理上，这条链先用旧 voltage/state 形成各支路向网络注入的 history/source current，再解 nodal voltage，最后把 nodal result 映射回各元件 branch voltage，供下一 step 与控制逻辑使用。[pdf:E04] 计算上，它说明 A→B→C→D 的 critical path 为何不能随意重排，也说明 MVM(C) 的 inverse admittance 是整个方法中复现信息最不足的一环。

DFP 不是“运行中任意改变位宽”，而是不同 MVM stage 使用不同 binary point。论文根据 10,000 组真实电力系统数据的 numerical oscillation analysis，称 99% 的变量落在 Table I 范围内：A/B 为 \([2^{-5},2^{16}]\) 并用 Q(48,20)，C/D 为 \([2^{-8},2^{12}]\) 并用 Q(48,30)。[pdf:E05][pdf:E06] 论文没有给出剩余 1% 的饱和、overflow 或异常处理，因此这些数据范围是经验校准，不是全输入域的误差保证。

## § 7 — 实验设计与结论

**问题 1：同一 accelerator 能否覆盖多种 topology？** 作者选择 boost、HB、FB、三相 VSC 四种 converter，以 PSCAD 输出作为 accuracy benchmark；每种 topology 在 \(0.5\,\mu s\)、\(1\,\mu s\)、\(5\,\mu s\) timestep 下运行，switching frequency 设为 100 kHz。[pdf:E06] Table II 的本文实现列均标为支持四种模型，正文还称 topology 切换无需 bitstream regeneration。[pdf:E07][pdf:E08] 这支持“同一设计覆盖四种已测拓扑”，但没有支持任意 topology，也没有给出 topology 切换耗时。

**问题 2：精度是否可接受？** Table III 报告，相对 PSCAD，在 \(0.5\,\mu s\) 下 Boost/HB/FB/VSC 的 relative error 分别为 1.28%、0.42%、0.32%、0.27%，平均 0.57%；在 \(1\,\mu s\) 与 \(5\,\mu s\) 下平均分别为 0.50% 与 0.47%。[pdf:E07] 论文因此声称 1 与 5 µs 的平均 error 低于 0.5%，但表中 1 µs 显示为 0.50%，按已报告精度只能说“不高于 0.50%”，不能确定严格小于。[pdf:E07][pdf:E08] 此外，贡献列表中的 0.41% 与 Table II 的 0.4148 fixed-point column 接近，而 DFP column 为 0.5746；Table III 的 \(0.5\,\mu s\) average 也为 0.57%。所以“0.41%”不能不加限定地当作 DFP 系统整体误差。[pdf:E02][pdf:E07]

**问题 3：是否满足实时 deadline？** 在两颗 EPYC 9554、256 GB DDR5 与两块 XCKU060 的实物平台上，论文报告 DPDK zero-copy 路径“包括 computational latency”的 data transmission latency 为 \(0.3\,\mu s\)，从而满足 \(0.5\,\mu s\) step deadline。[pdf:E06][pdf:E07] 另一个层级的证据是 XCKU060 accelerator 达到 200 MHz FMAX 与 100 ns latency。[pdf:E07][pdf:E08] 二者不能混为同一指标：100 ns 是 accelerator result，0.3 µs 是论文描述的端到端/传输路径数值；实时性应由后者与 0.5 µs 比较。

**问题 4：DFP 是否节省资源？** 正文报告 DFP 占用 5290 LUT、9743 FF、28 BRAM、108 DSP，并相对 64-bit fixed-point 降低 30.8%、26.8%、22.2%、43.8%。[pdf:E08] Table II 表明这组降幅更像 XC7K325T 的 fixed/DFP 对比：DSP 从 192 降到 108；在 XCKU060 两列中 DSP 都是 108，无法得到 43.8% 降幅。表中 XC7K325T DFP 的 FF 又写作 9742，正文写 9743；DFP LUT 为 5290 时相对 7566 的降幅约为 30.1%，与 30.8% 也不完全一致。[pdf:E07][pdf:E08] 因而，资源节省方向有表格支持，但百分比、器件与个别计数的对应关系需要复现者重新核算。

**问题 5：是否已经证明 scalability？** 系统照片和正文证明作者实际连接了 CPU server、Ethernet 与 FPGA accelerator，并明确使用两块 XCKU060。[pdf:E06][pdf:E07] 但没有 board 数从 1 增到 2、4、8 的 latency/throughput 曲线，没有网络规模、最大 node/matrix dimension、同步 jitter 或最坏时延。因此实验只证明“两板原型可工作”，没有闭合“随规模扩展仍实时”的完整 claim。

## § 8 — Take-aways

**5 句话。** 这篇论文把多拓扑电力系统实时仿真拆成 CPU 的大尺度慢步长域与 FPGA 的细粒度小步长域。[pdf:E04][pdf:E07] 它用 Norton/nodal 统一建模、topology-aware matrix decomposition、CSR 与通用流水 MVM，使同一 accelerator 覆盖 Boost/HB/FB/VSC。[pdf:E03][pdf:E05][pdf:E07] 它按 current/voltage stage 切换 Q(48,20) 与 Q(48,30)，在真实 XCKU060 上报告 200 MHz 和 100 ns accelerator latency。[pdf:E05][pdf:E07] 两块 FPGA、DPDK 与 CPU server 的实物系统报告 \(0.3\,\mu s\) 路径 latency，可在已测配置下满足 \(0.5\,\mu s\) deadline。[pdf:E06][pdf:E07] 但 scalability 没有规模曲线，量化范围没有 tail guarantee，资源与误差数字还存在正文/表格口径不一致。[pdf:E02][pdf:E06][pdf:E07][pdf:E08]

**3 句话。** 方法的真正贡献是让 topology 成为可更新的数据，而不是必须重生成 bitstream 的硬件结构。[pdf:E03][pdf:E05][pdf:E08] 真实硬件证据支持四种 converter、两块 FPGA、100 ns accelerator 与 0.5 µs deadline 下的原型运行，但不支持任意规模或任意 topology。[pdf:E06][pdf:E07] 最需要补的是随 board/matrix 规模增长的 worst-case end-to-end latency，以及 DFP 越界输入的误差与饱和行为。

**1 句话。** 这是一个有实物 FPGA 证据的多拓扑异构实时仿真原型，但“可扩展”仍是尚未被规模实验闭合的系统级 claim。[pdf:E06][pdf:E07]

## § 9 — 最脆弱的假设

最脆弱的假设是：**把更多细粒度子系统分散到更多 FPGA 后，CPU 聚合、Ethernet/DPDK 传输、跨域同步与 FPGA 计算的最坏总延迟仍会稳定小于最小 timestep。** 这个假设一旦失效，系统可以继续算，却不再是 realtime；而论文题名中的 “Scalable” 与异构分工的核心价值会同时失效。

论文为这个假设提供的证据只有一个已测工作点：两颗 EPYC 9554、两块 XCKU060、DPDK zero-copy、报告 \(0.3\,\mu s\) 路径 latency，满足 \(0.5\,\mu s\) timestep。[pdf:E06][pdf:E07] 它没有报告多 board 扩展曲线、packet contention、CPU aggregation cost、clock synchronization、99.9th-percentile/worst-case latency，也没有说明大步长 CPU domain 与小步长 FPGA domain 的耦合误差如何随规模积累。基于证据的判断是：论文证明了“一个两板配置在一个 deadline 下可行”，而不是“通信与同步成本可随规模受控”。

## § 10 — 最小复现实验

一周内最值得复现的不是完整大电网，而是“同一 bitstream 对两个结构差异明显的 topology 保持 deadline 与精度”的最小 claim。选择 Boost 与三相 VSC，使用论文的 100 kHz switching frequency、\(0.5\,\mu s\) timestep，并以 PSCAD 作为 reference。[pdf:E06]

实现范围只包括论文 Figure 4 的四段 nodal MVM、Zero-CMP/CSR topology data path、Q(48,20)/Q(48,30) stage scaling，以及 CPU 到单块 XCKU060 的 topology/state transfer；不重建 GUI 或多板系统。先固定同一 FPGA bitstream，依次加载 Boost 和 VSC matrix，记录：

- MVM A→B→C→D 的 cycle latency 与整步 wall-clock latency；
- 相对 PSCAD 的 waveform error，并明确 error 的数学定义；
- LUT/FF/BRAM/DSP 与 FMAX；
- topology 切换时是否需要 bitstream regeneration，以及切换后的第一步是否使用了正确 switch state；
- DFP 与统一 64-bit fixed-point 在相同 stimulus 下的误差和资源。

若同一 bitstream 在两种 topology 下都完成 \(T_l\le0.5\,\mu s\)，accelerator 接近 100 ns，误差落在论文表中 Boost 1.28%、VSC 0.27% 的量级，同时 DFP 资源方向与 Table II 一致，则支持本文最小 claim。[pdf:E07] 若必须重综合、任一 topology 频繁 deadline miss、DFP 出现未报告 overflow，或资源降幅只能在改变器件/频率后得到，则反驳对应 claim。这个复现仍不能验证 scalability；它只验证 topology reuse 与单板实时 kernel。

## § 11 — 最强反例设计

最强反例应直接攻击 scalability，而不是再测一个相似 converter。构造一个可控的多板 stress test：保持每个 FPGA 的局部 MVM workload 不变，把 board 数从 1、2 增到 4、8，同时让 CPU 每个 \(0.5\,\mu s\) step 聚合全部 board 结果；再叠加 worst-case burst，使多个 converter 在相邻 step 同时改变 switch state。测量从 CPU state dispatch 到所有 FPGA result 被 CPU 接收并用于 control 的 end-to-end latency distribution，尤其是 maximum 与 99.999th percentile，而不只测平均值。

若平均值仍低于 \(0.5\,\mu s\)，但 tail latency 随 board 数增长并越过 deadline，或某些 FPGA 因 ping-pong buffer/packet contention 使用了 stale topology state，那么“FPGA kernel 很快”就不能推出“异构系统可扩展且实时”。这是一个具体替代解释：论文的 0.3 µs 可能来自两板、低争用工作点，而不是 architecture 对规模的稳定性。[pdf:E07]

第二个攻击维度可嵌入同一实验：选择超出 Table I 99% calibration range 的 current/voltage transient，检查 Q(48,20)/Q(48,30) 是否 overflow、saturate 或发生大误差。论文没有给出剩余 1% 的处理机制。[pdf:E05][pdf:E06] 如果 topology burst 恰好同时制造通信 tail 与数值越界，就能测试系统在最需要小步长的极端暂态下是否反而最脆弱。

## § 12 — Follow-up Research Idea

在电力系统实时仿真与 FPGA 实现中，高影响结果通常不能只靠 average speedup；更重要的是可复现的实物平台、端到端 deadline、数值保真、resource/timing closure，以及在规模与极端工况下仍成立的工程证据。按这个标准，候选研究方向是：**面向 deadline 与数值误差双重契约的 compositional multi-rate EMT 平台**。它把研究目标从“用更多 FPGA 跑更多模型”改为“每个 CPU/FPGA partition 都携带可组合的 worst-case latency 与 numerical error contract，系统在运行前即可判断某个拓扑/规模是否可被安全调度”。

**(a) 未满足需求。** 本文已经有真实两板系统和 0.5 µs 工作点，却无法从该点判断加板、增加 matrix dimension、突发 topology change 后是否仍 realtime；DFP 的 99% range 也没有与 deadline/error violation 联动。[pdf:E06][pdf:E07]

**(b) 研究价值。** 如果能把 accelerator cycle bound、DPDK/network tail、CPU aggregation、multi-rate coupling error 和 DFP range 放进统一 contract，就可把“Scalable”从经验形容词变成可检验的 admission condition。对工程使用者而言，系统还能在开始仿真前拒绝一个无法守住 deadline 或 error bound 的 partition，而不是运行后才发现 overrun。

**(c) 可借鉴工具。** 可借鉴 real-time systems 的 worst-case response-time analysis 与 network calculus，结合 control/EMT 领域的 multi-rate error estimation；FPGA 侧增加 deadline/overflow monitor，CPU partitioner 则同时满足通信与数值约束。这是候选方法组合，不是本文已实现内容。

**(d) 第一个证伪实验。** 在 1/2/4/8 块 FPGA、不同 matrix dimension 与同步 switch burst 下，让 contract 预测每个配置的 worst-case latency 和最大 waveform error；只要实测出现 contract 判定可行却 deadline miss 或 error 超界，核心想法即被证伪。

**(e) 与本文的实质区别。** 本文优化的是一个 topology-aware MVM accelerator 与两板异构原型；候选方向优化的是“系统是否可被安全接纳”的可组合证据，并允许在资源不足时重分区、改变 local timestep 或拒绝运行。由于本任务禁止跨论文检索，这里只把它标为基于本文缺口的候选研究 idea，不声称 novelty。

## 证据索引

| ID | PDF 物理页 | 定位 | 支持的核心事实 | PNG |
|---|---:|---|---|---|
| E01 | 1 | title、abstract、Fig. 1 | 论文身份；多拓扑目标；100 ns、资源降幅摘要；\(T_l\le\Delta t\) 的实时定义 | `_evidence/E01-p001-title-abstract-realtime.png` |
| E02 | 1 | Introduction、contributions、Preliminary A | 20–100×时间尺度背景；CPU/FPGA动机；0.5 µs 与 0.41% 的作者贡献表述 | `_evidence/E02-p001-intro-contributions.png` |
| E03 | 2 | Fig. 2、Previous FPGA Simulators、Methodology A | prior work 限制；Norton/开关等值；CPU 传送矩阵；Zero-CMP 与 topology graph | `_evidence/E03-p002-prior-nodal-method.png` |
| E04 | 2 | Eqs. (1)–(6)、Flexible Matrix Decomposition、Computational Datapath | 完整 nodal dependency；CSR/domain decomposition；CPU/FPGA 时间尺度分工 | `_evidence/E04-p002-equations-topology-datapath.png` |
| E05 | 3 | Figs. 3–4、DFP 正文 | topology-aware decomposition；MVM pipeline；A/B 与 C/D 的不同数值需求及量化格式 | `_evidence/E05-p003-decomposition-mvm-pipeline.png` |
| E06 | 3 | Table I、Evaluation setup | DFP ranges；10,000 数据与 99% 描述；四拓扑/三步长/100 kHz；两 CPU、两 FPGA 平台 | `_evidence/E06-p003-dfp-table-system-setup.png` |
| E07 | 4 | Tables II–III、Fig. 5、system setup continuation | 实物 CPU-FPGA 系统；0.3 µs 路径；硬件型号、频率、latency、资源、相对误差 | `_evidence/E07-p004-hardware-comparison-system.png` |
| E08 | 4 | Precision、Overall Performance、Conclusion | 精度与资源的作者解释；XCKU060 200 MHz/100 ns；无 bitstream regeneration；未来通信工作 | `_evidence/E08-p004-errors-resources-conclusion.png` |
