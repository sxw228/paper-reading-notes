# MTOF: A Novel FPGA-Based EMT Toolbox in MATLAB

作者：Xin Ma；Xiao-Ping Zhang  
出处：IEEE Transactions on Power Systems, Vol. 40, No. 5, September 2025, pp. 3736–3749  
年份：2025  
DOI：10.1109/TPWRS.2025.3535841  
Zotero key：WK32GRFH  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。论文首页、作者与摘要见 PDF 物理页 1。[pdf:E01]

## § 1 — 研究问题与重要性

**论文直接陈述。** 这篇论文要解决的不是“如何再写一个 EMT 模型”，而是“如何把用户在 MATLAB 中给出的电网拓扑、元件参数和仿真参数，自动翻译成能在 FPGA 上执行的透明 VHDL/COE 文件，同时完成计算顺序、资源分配、初始化和数据格式处理”。作者将这个 MATLAB-to-FPGA EMT toolbox 称为 MTOF，并把目标用户明确指向缺乏底层 FPGA 编程经验的研究生和初学者。摘要还强调采用 IEEE-754 Floating-Point（浮点）计算，而不是把用户直接暴露在二进制参数、地址和时序细节中。PDF 物理页 1，Abstract。[pdf:E01]

这个问题重要，是因为 FPGA 实时 EMT 同时受两套约束支配：上层必须正确表达电磁暂态方程、历史变量和网络求解；下层又必须处理并行逻辑、固定存储、资源上限、端口映射、流水延迟和每个时间步的硬截止时间。论文称传统逐行 VHDL 开发会让初学者花至少 6 个月，而商业实时仿真器虽然提供高层模型，却不向终端用户开放可自动生成的透明底层代码；一般 High-Level Synthesis（高层综合）工具仍需要反复优化和较强的硬件背景。PDF 物理页 1，Section I 的问题陈述与贡献列表。[pdf:E02]

它的工程价值有三层。第一，作为教学工具，让学习者看到 EMT 数学如何落到硬件对象；第二，作为领域专用 synthesis tool（综合工具），把高层数据结构转换为低层 VHDL；第三，作为编程工具，把网络规模变化尽量收敛为输入数据变化，而不是手工改动大量硬件代码。这里的“任意拓扑”应理解为：在论文已支持的元件模型和固定执行架构范围内改变网络连接，而不是自动支持任意新物理模型或任意数据依赖。PDF 物理页 1，Section I，贡献 1–3。[pdf:E02]

## § 2 — 前人工作与不足

论文所用的 EMT 数学基础并不新。RLC 支路采用梯形积分后的伴随模型，节点网络仍是导纳矩阵方程；这些公式在文中明确追溯到已有 EMTP/EMT 文献。PDF 物理页 2，Section II-B，Eq. (1)；PDF 物理页 3，Eq. (12)。[pdf:E03][pdf:E04] 因此，MTOF 的主要贡献不是提出新的电磁暂态方程，而是把已有方程组织成可自动生成、可定时、可综合的 FPGA 数据流。

论文把既有方案分成三类。传统 ISE/VHDL 路线要求开发者逐位处理参数、地址、端口和时序；商业实时 EMT 平台向用户暴露高层模型，但不开放足够透明的底层实现；HDL Coder 或一般 HLS 可以从受限的 MATLAB/C 表达生成 HDL，却不能保证复杂 EMT 模型生成后无需手工优化即可满足资源和时序。作者进一步列出 MATLAB 与 FPGA 的结构性差异：二进制输入难检查、存储深度固定、元件并行执行、算术单元数量有限、`sin` 等高层函数不可直接使用、所有模型必须在约 5000 个时钟周期内结束、每个新端口都会改变实际电路连接。PDF 物理页 4，Fig. 3 与相邻正文。[pdf:E05]

真正未被解决的缺口，是缺少一个 **EMT-aware（理解 EMT 结构的）领域编译层**：它既知道哪些量可离线预计算、哪些状态必须逐步更新，也知道怎样把运算图映射成 memory unit、arithmetic sub-module 和 FSM controller。一般 HLS 只看到程序语句，不一定知道“历史电流源”“故障前后导纳矩阵”“传播延迟地址”这些领域语义。论文在这一点上的动机是成立的；但它没有给出与 HDL Coder、HLS 或专家手写 RTL 的直接、同平台对照实验，所以“现有工具不够”在本文中主要是作者的工程判断，而不是被严格 benchmark（基准测试）证实的比较结论。PDF 物理页 1，Section I；PDF 物理页 4，Fig. 3。[pdf:E02][pdf:E05]

## § 3 — 重建作者的思考路径

下面是**基于证据的重建**，不是作者逐字给出的研发日志。

1. 先从成熟 EMT 模型出发。RLC、变压器、分布参数线路、同步机和控制器在离散时间下都可写成“当前输入 + 历史状态 + 常数系数”的组合；网络层再通过节点方程把元件耦合起来。Fig. 1 把这一步概括为从 EMT component layer 到 FPGA-readable formats，再到 configurable logic。PDF 物理页 2，Fig. 1 与 Section II-A。[pdf:E06]
2. 再把硬件困难归纳成三种信息：参数和状态放在哪里，运算由什么电路完成，运算按什么顺序启动和结束。于是每个模型被拆成 memory unit、sub-module 和 main controller；这比把 MATLAB 逐句翻译成 VHDL 更接近一个领域 compiler intermediate representation（编译器中间表示）。PDF 物理页 4，Fig. 4–5。[pdf:E07]
3. 把不随当前时间步变化的工作尽量移到 MATLAB 离线侧，例如常数、地址、可枚举故障状态下的矩阵逆、固定子矩阵和初始化数据；实时侧只保留历史变量、必要乘加和小规模变量矩阵运算。分布参数线路的历史数据被放进固定深度存储，并在时间步结束时移位释放空间。PDF 物理页 5，Fig. 6 与 Eq. (31)–(33)。[pdf:E08]
4. 对高频、重复、结构简单的运算使用 pipelined design（流水设计）；对调用次数少、结构复杂的运算使用 non-pipelined design（非流水复用），以牺牲吞吐换资源。矩阵分解进一步把同步机的实时变量求逆从 7×7 压到 3×3，并声称至少节省 42 个 divider（除法器）。PDF 物理页 5，Fig. 8 与相邻正文。[pdf:E09]
5. 最后用 FSM 把这些模块拼成有确定延迟的时间表。论文给出的示例中，10 台同步机在单机 10-state FSM、最大 latency 100 clocks 的假设下需要 2000 个时钟周期；简单线路计算则可逐时钟送入流水线。PDF 物理页 6，Fig. 12 与相邻正文。[pdf:E10]
6. 当上述模式稳定后，再把它封装为 MATLAB 中的 Input processor、Organizer、Setting.m、Initial.m、Parameter.m、Address.m 和 Model.m，输出主控制器、存储文件与子模块，交给 Xilinx ISE 完成综合、布局布线和 bitstream 生成。PDF 物理页 7，Fig. 15 与 Section III-B。[pdf:E11]

这条思路的关键转折是：作者没有试图让通用 MATLAB 语义完整地落到 FPGA，而是先限制问题，使 EMT 模型变成可静态分析的领域数据流，再对这个受限表示自动生成硬件。

## § 4 — 核心 Intuition

MTOF 的核心 intuition 是把 EMT 仿真看成一个**静态数据流编译问题**，而不是普通脚本到 HDL 的逐句翻译。凡是与当前时间步无关的常数、地址和矩阵块都在 MATLAB 侧预计算，实时 FPGA 只执行历史状态更新、必要的变量运算和固定 FSM 调度。数据、算术和控制被分别落为 memory unit、sub-module 与 main controller，因此同一套硬件架构可以随输入拓扑扩展。它能奏效的前提，是模型尺寸、事件集合和最坏延迟能够提前确定。PDF 物理页 4–7，Fig. 4、Fig. 8、Fig. 15。[pdf:E07][pdf:E09][pdf:E11]

## § 5 — 具体方法与完整 Pipeline

以论文的 10-machine 39-bus 案例为例，完整流程如下。

1. **输入与模型选择。** 用户在 MATLAB 中给出 bus、load、synchronous generator、transformer、transmission line 等数组。MTOF 所展示的模型包括 RLC 支路、不同接线变压器、带传播延迟的分布参数线路、节点网络、同步机与控制系统，以及 grid-forming converter（构网型变流器）。模型先被改写成适合逐时间步计算的历史源形式。PDF 物理页 2–3，Section II-B，Eq. (1)、Eq. (7)–(12)、Eq. (22)–(30) 与 Fig. 2。[pdf:E03][pdf:E12][pdf:E04][pdf:E13][pdf:E14]
2. **固定步长时间推进。** 论文使用统一的电磁暂态步长 \(\Delta t\)。支路历史量在下一步被读取，分布参数线路把传播延迟 \(\tau\) 映射到整数地址和插值系数；历史电流存储采用固定深度并在每个时间步结束时移位。论文没有报告 adaptive time step（自适应步长）或 multi-rate（多速率）调度。PDF 物理页 2，Eq. (7)–(11)；PDF 物理页 5，Fig. 6 与 Eq. (31)–(33)。[pdf:E12][pdf:E08]
3. **离线预处理。** `Parameter.m` 计算线路常数等固定参数，`Address.m` 为每个变量和参数分配硬件地址，`Initial.m` 生成 zero-start 或 steady-state start 的初始化存储，`Setting.m` 计算 latency 和 FSM 排程，`Model.m` 根据方程字符串与可用 IP Core 组织端口和运算。总架构由 Input processor 和 Organizer 驱动。PDF 物理页 7，Fig. 15 与 M-file 列表。[pdf:E11]
4. **开关与矩阵处理。** 对可枚举的 switching-variable matrix，MTOF 在离线侧预先存储稳态矩阵和故障矩阵的逆，实时侧只用 1-bit `Fault_en` 选择；对随状态连续变化的同步机矩阵，MTOF预计算常数块，只在 FPGA 上求较小的变量子矩阵。论文示例把 7×7 的 \(R(t)\) 求逆缩减为 3×3，并报告至少节省 42 个除法器。PDF 物理页 5，Fig. 8。[pdf:E09]
5. **计算依赖与并行。** 重复次数高的线路乘加进入流水线，复杂而低频的同步机求解复用同一运算单元；主控制器用 FSM 错开 read、calculate、write 和 reset。论文示例称 10 台同步机可在 2000 clocks 内完成，而线路计算可逐时钟送入流水。PDF 物理页 6，Fig. 12。[pdf:E10]
6. **数值表示与 FPGA 映射。** 参数、地址和初值被写成 `.COE` 或 `.VHD`；算术子模块和 main controller 写成 `.VHD`。实验在单块 ML605 FPGA 上运行，板上资源为 768 DSP、416 RAM、301440 registers 和 150720 LUTs，系统时钟 100 MHz，并使用 IEEE-754 Floating-Point 与 distributed memory IP Core。PDF 物理页 10，Fig. 22 与硬件说明。[pdf:E15]
7. **生成、编译与执行。** Fig. 23 把流程分为 9 步：输入数据、计算参数、预分配地址、可选初始化、可选新模型子模块、计算 latency/安排主模块、写出 VHD/COE、加入 ISE 编译、下载 FPGA 并采集数据。这里必须区分：MTOF 生成源文件，Xilinx ISE 负责后续 compile 和 `.bit` 文件；论文没有把二者合并成一个“300 秒端到端 bitstream”指标。PDF 物理页 10，Fig. 23。[pdf:E16]
8. **输出。** 对 10-machine 39-bus，最终输出是可由 ISE 编译的 VHDL/COE 文件、bitstream 和 FPGA 波形；实验通过 bus 6 的单相故障检查 q-axis voltage、d-axis current 与 electric torque 是否跟 MATLAB/Simulink 参考结果一致。具体数字在第 7 节讨论。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有大量公式，但没有提出新的收敛定理、误差上界或数值稳定性证明。数学上的核心，是把标准 EMT 离散方程逐层“lowering（降级）”为可存储、可流水和可调度的硬件运算。

**1. RLC 伴随模型。** 梯形积分把动态支路改写成当前端电压差与历史电流源的线性组合：

\[
i_{\mathrm{RLC}}(t)=k_1\bigl(v_a(t)-v_b(t)\bigr)+k_2 I_{\mathrm{RLC}}(t-\Delta t).
\]

其中 \(k_1,k_2\) 由元件类型和仿真步长决定，\(I_{\mathrm{RLC}}(t-\Delta t)\) 把过去状态压缩为一个可在 BRAM 中保存的历史量。工程 intuition 是：FPGA 不需要保存完整波形，只需要保存下一步计算必需的状态。PDF 物理页 2，Eq. (1) 与相邻说明。[pdf:E03]

**2. 分布参数线路。** 发送端电流由当前端电压和延迟历史源构成：

\[
i_s(t)=\frac{1}{Z}v_s(t)-I_s(t-\tau),
\]

\[
I_s(t-\tau)=A v_r(t-\tau)+B i_r(t-\tau)+C v_s(t-\tau)+D i_s(t-\tau),
\]

并定义 \(\tau=d\sqrt{lc}\)、\(k_5=\tau/\Delta t\)、\(k_6=\lfloor \tau/\Delta t\rfloor\)、\(\Delta k=k_5-k_6\)，再由 Eq. (10)–(11) 对非整数步延迟做插值。物理上的传播延迟因此被转换成“地址偏移 + 一次线性插值”，这正是后续固定深度 memory unit 的基础。PDF 物理页 2，Eq. (7)–(11) 与变量定义。[pdf:E12]

**3. 网络耦合。** 每个时间步的节点方程写成

\[
Y(t)V(t)=I(t)-I(t-\Delta t),
\]

其中当前注入与历史电流源汇总后求解节点电压。这个公式把元件并行更新与全网耦合分开：各元件先形成注入，网络层再解线性方程。PDF 物理页 3，Eq. (12)。[pdf:E04]

**4. 同步机变量矩阵。** 同步机电流写成

\[
i_{dq0}(t)=R(t)^{-1}\bigl(v^{out}_{dq0}(t)-v_{hist}(t-\Delta t)\bigr),
\]

\[
R(t)=-R^{out}_{dq0}(t)+\frac{2}{\Delta t}L_{dq0}+\omega^M_{pre}(t)L_{dq0}+R_{dq0}.
\]

难点是 \(R(t)\) 随转速和外部网络状态变化，不能完全离线求逆。MTOF 的做法不是消除变量性，而是把常数子块先算好，只保留 3×3 变量子矩阵实时求逆；Fig. 8 的资源表把原 7×7 方案的 42 multipliers、42 adders、42 dividers 降为各 6 个。PDF 物理页 3，Eq. (22)–(23)；PDF 物理页 5，Fig. 8。[pdf:E13][pdf:E09]

**5. 历史存储的地址化。** 论文把分支、模态和传播时间索引合成地址 \(g(t)\)，令最大深度满足 \(g_{max}=a b c\)，并在时间步边界执行 \(I_{TL}(g(t))=I(g(t)+ab)\)，相当于丢弃最旧的 \(ab\) 个历史元素并整体移位。这样仿真时间增加时，存储深度不再线性增长。PDF 物理页 5，Fig. 6 与 Eq. (31)–(33)。[pdf:E08]

因此，这篇论文的数学创新应谨慎表述为“面向 FPGA 的结构化改写与部分求值”，而不是新的 EMT 数值方法。它没有给出浮点位宽敏感性、长时稳定性、adaptive stepping 或多事件情况下的误差理论。

## § 7 — 实验设计与结论

论文用 Eq. (34) 定义平均相对误差：

\[
\epsilon=
\frac{\sum_{t=0}^{n}\frac{|V_{FPGA}(t)-V_{MATLAB}(t)|}{|V_{MATLAB}(t)|}\times100\%}{n/\Delta t}.
\]

但 Eq. (34) 前的文字把指标描述为“全时段最大绝对误差除以最大参考幅值”，而公式实际呈现的是逐点相对误差的平均；两者不是同一个指标。若参考信号接近零，逐点相对误差还可能放大。PDF 物理页 10，Section V-D 与 Eq. (34)。[pdf:E17]

**问题 1：生成模型能否复现同步机暂态波形？ → 实验。** 4-machine 11-bus 在 bus 7 施加 1.0–1.1 s 单相故障，比较 FPGA、MATLAB 和 Simulink 的 q-axis voltage、d-axis current 与 electric torque。Fig. 27 的三组曲线基本重合，图内标注 q-axis voltage 最大绝对差 0.0224；正文报告平均误差 0.30%。PDF 物理页 11，Fig. 27 与 Section V-D.1。[pdf:E18][pdf:E19] **答案。** 在这个工况和作者参考模型下，MTOF 生成的实现与软件模型高度接近。不过正文说观察 SG1，Fig. 27 caption 写的是 G2，实验对象标注存在轻微不一致。PDF 物理页 10–11。[pdf:E17][pdf:E18]

**问题 2：网络扩大到 10-machine 39-bus 后是否仍准确？ → 实验。** bus 6 在 1.0–1.1 s 发生单相故障，比较 FPGA 与 MATLAB/Simulink。正文报告 q-axis voltage 最大绝对误差 0.0589、平均相对误差 1.49%。PDF 物理页 11，Section V-D.2。[pdf:E19] 但 Fig. 28(b) 图内实际标注 `max(|vq(FPGA)-vq(MATLAB)|)=0.0229`，与正文的 0.0589 不一致。PDF 物理页 12，Fig. 28(b)。[pdf:E20] **答案。** 平均误差仍低于作者采用的 2% 结论线，但最大误差的具体数值不能在论文内部唯一闭合，应以“正文 0.0589、图内 0.0229”并列保留，而不能替作者消解。

**问题 3：能否处理 IBR/GFM 模型？ → 实验。** modified 39-bus 在 bus 1 接入 1 个 IBR，bus 6 于 0.8–0.9 s 施加单相故障，比较电流、有功和频率。正文称 per-unit active power 的绝对误差低于 2%，frequency 的绝对误差低于 1%；Fig. 29 显示 FPGA、MATLAB 与 Simulink 的趋势接近。PDF 物理页 11–12，Section V-D.3 与 Fig. 29。[pdf:E19][pdf:E21] **答案。** 论文证明了一个预定义构网型变流器模型可以嵌入同一工具链，但没有证明更复杂限流、饱和或大量开关事件也能保持同等误差。

**问题 4：是否满足实时 deadline？ → 实验。** 正文报告 4-machine 11-bus 为 25.4 μs、10-machine 39-bus 为 47.0 μs、1-IBR 39-bus 为 17.0 μs；前两者的仿真步长是 50 μs。PDF 物理页 11–12，相邻正文。[pdf:E19][pdf:E22] Fig. 30(a) 的 4-machine 时间轴终点实际标为 24.9 μs，与正文 25.4 μs 相差 0.5 μs；另外两例图内终点分别为 47.0 μs 和 17.0 μs。PDF 物理页 12，Fig. 30。[pdf:E23] **答案。** 三个给定案例均在各自时间步内完成，但 10-machine 39-bus 只剩约 3 μs 余量，论文没有测试更高事件密度、更多模型或跨板通信后的 worst-case execution time（最坏执行时间）。

**问题 5：单板资源是否足够？ → 实验。** Table I 报告：4-machine 11-bus 使用 34% registers、78% LUTs、12% RAM、91% DSP；10-machine 39-bus 使用 34%、87%、12%、92%；1-IBR 39-bus 使用 23%、94%、11%、14%。PDF 物理页 12，Table I。[pdf:E22] **答案。** 三个 bitstream 都能放入单块 ML605，但 10-machine 案例已接近 DSP 上限，1-IBR 案例已到 94% LUT；“可继续扩展”取决于新模型消耗哪一类资源，不能仅由总资源未到 100% 推出。

**问题 6：自动生成是否显著减少人工代码？ → 实验。** Table II 报告 MTOF 生成 FPGA 文件分别需要 50 s、300 s、30 s，而“without MTOF”统一写为至少 6 个月。PDF 物理页 13，Table II。[pdf:E24] Table III 报告 4-machine 11-bus、10-machine 39-bus、1-IBR 39-bus 分别用 2280、2431、4591 行 MTOF M-file 生成 94572、97352、72427 行 FPGA code，code ratio 为 2.4%、2.5%、6.3%。PDF 物理页 13，Table III。[pdf:E25] **答案。** 论文有力证明了大量低层 boilerplate（样板代码）可以自动展开；但“至少 6 个月”没有用户研究、开发日志或专家基线，代码行数比也不是可移植性、可维护性或端到端开发成本的充分指标。并且 Table II 统计的是“files generation time”，ISE compile、place-and-route、bitstream 和下载在 Fig. 23 中是后续步骤，不能把 300 s 解读成完整硬件部署时间。PDF 物理页 10 与 13。[pdf:E16][pdf:E24]

总体上，实验支持一个较窄但有价值的结论：对论文已实现的模型库、三个测试系统、固定步长和单块 ML605，MTOF 能生成可综合代码，并在作者参考模型下满足精度与实时约束。实验不足以支持无条件的“任意 EMT 模型、任意事件、任意规模、任意 FPGA 平台”。

## § 8 — Take-aways

**5 句话。**  
1. MTOF 是一个 EMT-specific code generator（领域专用代码生成器），不是新的通用 EMT 求解器。[pdf:E06][pdf:E11]  
2. 它通过离线预计算、固定历史存储、矩阵分解、流水与 FSM 调度，把模型压缩成 memory、sub-module、controller 三类硬件对象。[pdf:E07][pdf:E08][pdf:E09][pdf:E10]  
3. 在单块 ML605 上，论文报告三个案例均满足实时 deadline，10-machine 39-bus 的执行时间为 47 μs、LUT 为 87%、DSP 为 92%。[pdf:E23][pdf:E22]  
4. 代码生成的量级压缩很明显：2431 行 MTOF M-file 对应 97352 行 FPGA code，文件生成时间报告为 300 s。[pdf:E24][pdf:E25]  
5. 最需要保留的谨慎是：实验模型和事件很有限，误差定义与个别数字存在内部不一致，也没有与 HLS 或专家手写 RTL 的直接公平对照。[pdf:E17][pdf:E20]

**3 句话。**  
1. 论文最有价值的贡献，是把 EMT 领域语义显式编码进 FPGA 生成流程，而不是依赖通用 HLS 猜测硬件结构。[pdf:E05][pdf:E11]  
2. 它证明了“静态可分析的 EMT 模型”可以在单板上自动生成并实时运行，但没有证明动态、非线性、事件密集模型同样成立。[pdf:E19][pdf:E23]  
3. 因而 MTOF 更像一个有说服力的 domain-specific compiler prototype（领域编译器原型），而不是已经覆盖所有实时 EMT 工作负载的成熟平台。

**1 句话。**  
把可预计算的 EMT 工作移出实时路径、把剩余运算编译成固定数据流，是 MTOF 成功的原因，也是它面对动态事件和不可预知迭代时最可能失效的地方。[pdf:E09][pdf:E10]

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标 EMT 系统能够被编译成尺寸固定、地址可预分配、事件状态可枚举、最坏 latency 可提前确定的数据流。** MTOF 的 memory standardization 要求固定深度和固定地址，matrix decomposition 要求常数块可离线计算或故障状态可由少量 enable 信号选择，main controller 又要求每个模块的 latency 已知，才能排出不违反 deadline 的 FSM。PDF 物理页 4–6，Fig. 5、Fig. 6、Fig. 8、Fig. 12。[pdf:E07][pdf:E08][pdf:E09][pdf:E10]

**基于证据的推断。** 这个假设在以下场景可能失效：拓扑在运行中以大量组合方式变化；磁饱和、限流器、保护逻辑或电力电子开关引入数据依赖迭代；事件时间需要 zero-crossing 定位；某些时间步需要更多 Newton iterations；或者 adaptive/multi-rate integration 改变历史地址与模块调用次数。此时“预存两套矩阵 + 固定 FSM”会面临状态爆炸、最坏时间膨胀或数值精度下降。

论文给出的证据是三个预定义案例、少量单相故障和固定 100 MHz schedule，其中 10-machine 39-bus 已用 47 μs/50 μs，资源上达到 87% LUT、92% DSP；这说明静态设计在给定案例成立，但余量并不宽。PDF 物理页 11–12，Fig. 30 与 Table I。[pdf:E23][pdf:E22] 论文没有测试运行时结构变化、密集并发事件、数据依赖迭代或不同 FPGA 平台。若静态可分析性不成立，MTOF 的核心承诺会同时受损：生成代码可能需要手工改写、硬实时 deadline 可能被打破，“任意拓扑”也只能退化为有限模板内的拓扑变化。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 39-bus，而是验证核心 claim：**从高层 EMT 数据自动生成的 memory/sub-module/FSM，是否无需手工修改就能编译，并在固定 deadline 内复现软件参考。**

**数据。** 构造一个 3-bus 小系统：一个电压源、一条含传播延迟的分布参数线路、一个 RLC 负载，并在中间节点施加持续 0.1 s 的单相故障。令线路延迟不是 \(\Delta t\) 的整数倍，以强制使用 Eq. (7)–(11) 的地址与插值；网络节点用 Eq. (12)，支路用 Eq. (1)。PDF 物理页 2–3。[pdf:E03][pdf:E12][pdf:E04]

**实现。** 第 1–2 天写 MATLAB 参考模型和一个最小 generator：读取 bus/line/RLC 数组，生成参数 `.COE`、地址 `.COE`、一个流水线路子模块、一个 RLC 子模块和一个 FSM main controller。第 3 天加入 Fig. 6 所示固定深度历史存储与移位；第 4 天用 vendor Floating-Point IP 或等价可综合算术完成 RTL simulation；第 5 天在 100 MHz 目标下综合并读取 latency/resource report；第 6–7 天执行故障波形对比和重复生成测试。方法依据见 PDF 物理页 5–6，Fig. 6、Fig. 12。[pdf:E08][pdf:E10]

**测量。** 记录四项：生成后人工修改的 VHDL 行数；从输入到写出 VHDL/COE 的时间；综合后的每步 clock cycles 与 timing slack；FPGA/RTL 波形相对 MATLAB 的 Eq. (34) 误差及最大绝对误差。误差指标必须同时报告，避免复用论文中模糊的单一描述。PDF 物理页 10，Eq. (34)。[pdf:E17]

**支持条件。** 生成文件无需人工逻辑修改即可编译；每步小于 5000 clocks，即 100 MHz 下小于 50 μs；平均相对误差低于论文采用的 2% 结论线；重复改变线路长度和 RLC 参数时，只修改输入数据，不修改 RTL 结构。

**反驳条件。** 只要出现任一情况，核心 claim 就被削弱：非整数延迟必须手工改地址；故障状态需要人工改 FSM；生成 RTL 不能过 timing；误差超过 2%；或者改变元件参数就必须重写模块。这个实验不验证大系统 scalability，但能直接验证 MTOF 最关键的“领域数据 → 可执行硬件数据流”机制。

## § 11 — 最强反例设计

最强反例不是再找一个更大的静态网络，而是构造一个**规模相近、但运行时计算图不再静态**的系统。

具体设计：以 39-bus 为基底，同时加入多台带 current limiting（限流）、mode switching（模式切换）和 anti-windup 的 grid-forming converters，加入一个饱和变压器，并在 2–3 个相邻时间步内触发多断路器动作、故障清除和控制模式切换。让某些状态需要数据依赖迭代才能收敛，且可能出现不同数量的 Newton steps；再把这些事件对齐到 50 μs deadline 附近。参考解使用更小步长和严格事件定位，MTOF 侧则保持论文的固定地址、预计算矩阵和静态 FSM。

攻击目标有三个。第一，预计算矩阵状态数是否随开关组合爆炸；第二，固定 schedule 是否在最坏事件步超过 50 μs；第三，即使仍能准时，浮点与插值误差是否在限流/饱和边界处显著放大。MTOF 的现有机制依赖少量可选矩阵、固定内存和已知 latency，证据分别见 Fig. 8、Fig. 6 和 Fig. 12。[pdf:E09][pdf:E08][pdf:E10]

一个真正能推翻核心机制的结果是：静态 MTOF 方案在普通稳态步中正常，但在事件密集步必然超时或选择错误矩阵，而一个允许 runtime event queue（运行时事件队列）和有界迭代的实现能在相近资源下保持 deadline 与误差。这样就排除了“只是工程优化不够”的替代解释，直接说明静态可分析性不是一般 EMT 工作负载的可靠前提。当前论文只展示少量单相故障和预定义 IBR，尚未覆盖这个反例空间。PDF 物理页 11–12，实验工况、Fig. 29–30。[pdf:E19][pdf:E21][pdf:E23]

## § 12 — Follow-up Research Idea

在 EMT + FPGA 领域，高影响工作通常需要同时证明：物理模型 fidelity（保真度）、hard real-time deadline、资源可实现性、跨平台或跨规模泛化、与强基线的公平比较，以及可复现的端到端工具链。论文已经覆盖其中的模型、单板 timing 和资源，但其最脆弱处仍是静态事件假设。

**候选研究方向：带 deadline-and-error contract（时限与误差契约）的事件自适应 EMT 编译器。** 这是候选想法，不声称 novelty，因为本任务没有检索附件外相关工作。

**(a) 未满足的需求。** 当前 MTOF 能编译固定、可预分析的数据流，却不能说明在动态拓扑、限流、饱和和数据依赖迭代下是否仍能准时且准确。10-machine 案例 47 μs/50 μs 的余量和高 DSP/LUT 使用率表明，简单继续堆模块不是稳健答案。PDF 物理页 12，Fig. 30 与 Table I。[pdf:E23][pdf:E22]

**(b) 可能产生的研究价值。** 新目标不是“自动生成更多模型”，而是让编译器对每个模型生成可机器检查的 contract：允许哪些事件、最坏执行时间是多少、数值误差在什么范围、资源超限时如何降级。这样评价标准从“能生成代码”提升为“能证明在给定事件包络内准时并满足误差界”。

**(c) 可借鉴的相邻方法。** 可以组合 synchronous dataflow（同步数据流）与 worst-case execution time analysis（最坏执行时间分析）建立静态骨架，用 partial evaluation（部分求值）保留 MTOF 的离线优势；对少量运行时分支使用 bounded event queue 和 mixed-criticality scheduling（混合关键性调度）；用 interval arithmetic（区间算术）或 shadow simulation（影子仿真）在线监控误差余量。这里的关键不是加入一个模块，而是让编译器同时优化数值误差、deadline 和资源。

**(d) 第一个可证伪实验。** 在同一个 39-bus 基底上构造三组事件密度：单故障、并发多故障、限流与拓扑切换叠加。要求编译器在两种不同资源配置上自动生成实现，逐步报告 worst-case clocks、实际 clocks、误差和资源；若它无法在不手工改 RTL 的情况下覆盖最高事件密度，或为了保证 deadline 需要不可接受的资源复制，这个方向立即被证伪。

**(e) 与本文工作的实质区别。** MTOF 的目标是把预定义 EMT 模型翻译成固定硬件架构；该候选方向把问题重新定义为“在动态事件不确定性下，自动合成带可验证 timing/accuracy contract 的硬实时 EMT 系统”。前者主要做静态模板化与离线预计算，后者把运行时适应性和可证明边界纳入编译目标，因此不是简单增加模型库或更换应用场景。
