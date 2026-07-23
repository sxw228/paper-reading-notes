# A fully automated reconfigurable calculation engine dedicated to the real-time simulation of high switching frequency power electronic circuits

**作者：** T. Ould Bachir、C. Dufour、J. Bélanger、J. Mahseredjian、J. P. David  
**出处：** *Mathematics and Computers in Simulation*, 91, 167–177  
**年份：** 2013  
**DOI：** 10.1016/j.matcom.2012.07.021  
**Zotero key：** Z4B8AE88  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“FPGA 能不能算电路”这一宽泛问题，而是一个受到硬实时约束的问题：能否把高开关频率电力电子电路的行为级模型，自动变成一个浮点 FPGA 计算引擎，使每个离散时间点都在下一拍输入到来前确定性算完，同时兼顾精度、面积和不同电路拓扑的复用。作者给出的现实矛盾是，PC-based HIL 对可模拟开关频率通常只能做到约 1–5 kHz，而论文面向的变换器以 10–200 kHz 开关；若按开关周期约二十分之一选步长，需要 0.25–5 μs，CPU 实时仿真的 5–10 μs 级步长很难覆盖这一范围。PDF 物理页 1 的摘要与物理页 2 的 Introduction 给出了这组问题边界。[pdf:E01] [pdf:E02]

它的重要性来自 HIL 的用途：真实控制器与被仿真的功率级闭环交互，可以在功率硬件尚未完成时开发控制器，也可以安全地触发极限工况。此时“平均意义上算得快”不够，最坏情况下每一步都必须按期交付。作者因此把研究目标落在 sub-microsecond 时间步、可预测的流水延迟和片上执行，而不是离线仿真的总吞吐率。[pdf:E01] [pdf:E02]

论文的核心技术 claim 是：把固定导纳开关模型的 MNA 方程预重写为固定矩阵—向量运算，再用自对齐浮点格式 SAF 与并行 dot-product（DP）算子执行，可以在高端 Virtex 5 和低成本 Spartan 3 上都得到小于 1 μs 的步长；同一类自动生成的引擎可覆盖 boost、两电平三相桥以及 boost 加三相桥三种拓扑。对应证据分别位于 PDF 物理页 4 的 Section 2.2 / Eq. (5)–(6)、物理页 5 的 Fig. 1 / Section 3.2，以及物理页 7 的 Table 3。[pdf:E04] [pdf:E06] [pdf:E09] 这里的价值不是得到一次漂亮波形，而是把“电路方程如何排布、浮点如何累加、硬件如何并行”共同设计成可按时完成的计算路径。

## § 2 — 前人工作与不足

作者把既有开关网络仿真分为 detailed-mode 与 behavioural-mode。SPICE、SABER 一类 detailed-mode 使用计算量大的非线性器件函数，适合器件细节分析，却难以直接进入实时 HIL。behavioural-mode 中又有 ideal switch、switching function 和 average model：switching function 可以表达故障，但高度依赖具体拓扑，必须事先辨识变换器的各种工作模式；ideal switch 或 Ron/Roff 二值电阻能逐开关处理，却会让网络方程随开关组合改变，需要反复重构。[pdf:E02]

固定导纳模型是论文采用的关键前人方案。PDF 物理页 3 的 Section 2.1 / Eq. (1)–(4) 显示，它把闭合开关表示成小电感、断开开关表示成小电容，并令两种状态的离散等效导纳相等，于是网络矩阵不随开关状态变化。[pdf:E03] 这个方案解决了“每种开关组合都重建矩阵”的问题，但还没有自动给出一个面积小、延迟短、浮点精度足够的 FPGA 求解器。

计算硬件方面，已有 FPGA 求解器常用并行 MAC；普通商业浮点加法器的多周期延迟会拉长 DP 的加法树，使更宽的列并行度难以转化为更短反馈环。作者此前的工作已经提出基于固定导纳与定制浮点 MAC 的求解器，本篇在此基础上增加四点：由脚本生成控制逻辑、用三种拓扑验证通用性、采用更节省的 SAF、以并行 DP 替换并行 MAC，并把网络表述换成 MNA。[pdf:E02] [pdf:E06] 因而这篇论文的增量不是发明固定导纳，也不是第一次提出 SAF，而是把模型重写、定制算术、DP 并行和自动控制生成组合成一条可实现链。

## § 3 — 重建作者的思考路径

以下是基于论文证据的逆向重建，不是作者逐句陈述。

第一步，研究者会先发现真正卡住 HIL 的是反馈依赖：本步求出的电压、电流和 history term 会成为下一步输入，不能仅靠把许多互不相关的样本吞吐量做高来隐藏延迟。FPGA 时钟约为 5–10 ns 时，sub-microsecond 步长只留下几十到约百个周期，因此矩阵求逆、拓扑判断和长浮点累加链都不能留在实时环内。[pdf:E02]

第二步，要让硬件反复执行同一数据流，就必须让开关切换不改变矩阵结构。固定导纳模型恰好把状态变化搬到 history source，而保持 MNA 矩阵 \(A\) 不变，因此 \(A^{-1}\) 可以离线只算一次；实时部分退化为固定系数的矩阵—向量乘法以及少量状态选择。[pdf:E03] 接着再把当前输入、动态元件 history、开关两种候选 history 和输出按依赖关系重排成 Eq. (6)，就能提前算出下一步所需量，并把每一行自然映射为 dot-product。[pdf:E04]

第三步，普通 IEEE-754 浮点的动态范围方便，但多周期对齐与规格化会把加法放进反馈关键路径；完全改成 fixed-point 又会把量程分析和缩放责任推给每个模型。PDF 物理页 4 的 Section 3.1 给出的 SAT/SAF 线索是：让各加数的尾数相对共同边界预对齐，把移位工作移出累加反馈环，使浮点累加可以单周期完成。[pdf:E05] 由此，PDF 物理页 5 的 Fig. 1 / Section 3.2 所示 DP 不再因为浮点加法树过长而失去优势，可以一次处理更多矩阵列。[pdf:E06]

最后，既然方程重排和控制时序具有规则性，就让 Matlab 脚本从原始 MNA/MANA 方程生成控制逻辑和矩阵装载，而不是手工为每个拓扑画一个求解器。论文所称 “fully automated” 到此为止：PDF 物理页 7 的 Section 4.2 说明它自动生成求解器控制逻辑，但原始方程仍需先给出，作者也把由 schematic/GUI 自动产生方程留作未来工作。[pdf:E08]

## § 4 — 核心 Intuition

把开关动作从“改写网络矩阵”改造成“在固定矩阵旁选择不同的 history source”，就能把每个实时步变成重复的固定系数 dot-product。[pdf:E03] 再把浮点尾数对齐移出累加反馈关键路径，多个乘积便可用并行 DP 快速汇总，而不必牺牲浮点动态范围。[pdf:E05] 所谓自动化，就是让脚本按方程依赖生成这台固定数据流机器的控制，而不是让 FPGA 在运行时理解任意电路图。[pdf:E08]

## § 5 — 具体方法与完整 Pipeline

以论文的 circuit #3（boost 驱动两电平三相桥，桥后连接 PMSM state-space core）为例，完整 pipeline 如下；拓扑和 SAF accuracy 分别见 PDF 物理页 8 的 Fig. 2 与 Fig. 3。[pdf:E10]

1. **离散器件。** 对电容、电感等二端器件采用 backward Euler method（BEM）形成 Norton companion：一个等效导纳加一个 history current。作者选择 BEM，是因为 trapezoidal integration method 在开关瞬间可能产生数值振荡；对电容有 \(g_C=C/h\)，对电感有 \(g_L=h/L\)。[pdf:E03]
2. **固定开关 stamp。** 每个开关在闭合时用小电感表示、断开时用小电容表示，并选参数使 \(g_C=g_L\)。这样开、关只改变注入向量中的 history term，不改变 MNA 矩阵 \(A\)。开关状态依据门极命令以及上一时刻的开关电压、电流符号更新；论文在 Eq. (3) 与 Eq. (4) 分别给出 IGBT-diode pair 和 diode 的布尔更新关系。[pdf:E03]
3. **离线预计算和重排。** 从 MNA/MANA 原始方程组装 \(A\)，离线计算 \(A^{-1}\)，再把当前独立源 \(u\)、非开关动态支路 history \(j^{(d)}\)、开关 history \(j^{(s)}\) 以及需要输出的电压、电流重排为 Eq. (6) 的若干固定 \(W\) 矩阵。[pdf:E04]
4. **生成硬件控制。** Matlab/Simulink System Generator 环境中的脚本读取这些原始方程，生成求解器控制逻辑，并以最小化步长为排程目标。矩阵系数、输入和状态向量进入寄存器/存储，四个 DP4 算子按行计算，控制单元安排数据送入、结果登记与下一步 feedback。[pdf:E06] [pdf:E08]
5. **定制数值路径。** 乘法输入/结果在标准浮点与 SAF 之间转换；SAF 用缩减指数和扩展尾数，把对齐移位放在累加回路外，使 MAC/DP 可以 single-cycle accumulation。论文的算子实验使用 SAF(48, 3, 160)，Virtex 5 目标 200 MHz，Spartan 3 目标 100 MHz。[pdf:E05] [pdf:E07]
6. **逐步执行。** 每个仿真时刻先依据门极与上一时刻符号选出实际开关 history，再由固定 \(W\) 乘以输入/history 向量，同时产生本步观测输出和下一步候选 history；寄存结果后进入下一时刻。[pdf:E04] 这是单一固定步长推进，论文没有报告局部自适应步长、事件时刻插值或多速率调度。
7. **输出与外部闭环。** circuit #3 中求解器输出 boost/DC-link 电压和电机侧电气量，并与外部 PMSM core 交换输入输出；离线时在 bit-accurate、cycle-accurate System Generator 模型中运行，实时版本则部署到 Opal-RT OP5600 的 ML605 FPGA 板，通过数字/模拟 I/O 与外界交互。[pdf:E10] [pdf:E11] [pdf:E12]

这条 pipeline 的“可重配置”主要是系数、状态维度与控制排程可由方程重新生成，不是运行中无停顿地接受任意新 schematic。论文也没有报告自动定点范围分析、自动选择 SAF 参数、部分重配置 bitstream 或多个不同步子系统的多速率执行。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线是把电路离散方程化成一个可以离线定矩阵、在线只做 dot-product 的递推。

对跨接节点 \(k,m\) 的二端元件，BEM companion 写成

\[
g_{\mathrm{eq}}\bigl(v_k^{n+1}-v_m^{n+1}\bigr)
=j_{km}^{n+1}+i_{km}^{n+1}.
\]

这里 \(g_{\mathrm{eq}}\) 是等效导纳，\(j_{km}^{n+1}\) 是由过去状态形成的 history current，\(i_{km}^{n+1}\) 是支路电流。电容取 \(g_C=C/h\)、\(j_C^{n+1}=g_C(v_k^n-v_m^n)\)；电感取 \(g_L=h/L\)、其 history 项为上一时刻电流与电压项的组合。把所有 companion stamp 组装后，MNA 得到

\[
A_t x_t=b_t,
\]

其中 \(x_t\) 同时含节点电压和某些支路电流，\(b_t\) 含独立源与 history source。[pdf:E03]

固定导纳开关模型的关键等式不是新的求解公式，而是约束 \(g_C=g_L\)。它让 \(A_t=A\) 与开关状态无关，于是

\[
x^{n+1}=A^{-1}b^{n+1}
\]

中的 \(A^{-1}\) 只需离线计算一次。[pdf:E03] 物理上，这相当于让开、关两种 companion 对网络呈现相同的瞬时导纳 stamp，把状态差异编码进注入电流；硬件因此反复使用同一系数矩阵。代价是这个人为选择的小电感/小电容必须既能代表开关行为，又不能引入不可接受的数值或能量误差。

随后作者把

\[
b^{n+1}=K_c
\begin{bmatrix}
u^{n+1}\\
j^{(d),n+1}\\
j^{(s),n+1}
\end{bmatrix}
\]

代入 \(A^{-1}b^{n+1}\)，并从所得线性映射中抽取 \(W^{(s0)}\)、\(W^{(s1)}\)、\(W^{(d)}\)、\(W^{(y)}\)。Eq. (6) 同时计算开关断开/闭合的下一步候选 history、非开关动态元件的下一步 history 和当前输出；实际 \(j^{(s)}\) 再由门极与符号逻辑选择。[pdf:E04] 这一步的工程意义是把“解网络”改写成若干共享输入向量的矩阵行内积，并显式暴露可并行性。

SAF 则处理内积中的浮点累加。一个数表示为

\[
x_{\mathrm{fp}}=m\cdot 2^{\,2^l e-b},\qquad -2^w\le m<2^w-1,
\]

其中 \(w\) 是扩展尾数宽度，\(l\) 表示从标准指数低位切出的位数，\(b\) 调整动态范围。[pdf:E05] 对两个 SAF 数，Eq. (7) 先令

\[
e_r=\max(e_a,e_b),\quad
k_a=e_r-e_a,\quad k_b=e_r-e_b,
\]

再计算

\[
m_r=(m_a\gg k_a2^l)+(m_b\gg k_b2^l).
\]

由于尾数相对公共边界移位，必要对齐可以在 feedback accumulation loop 之外完成；这使两输入、多输入加法和累加可共享同一思想。[pdf:E06] 论文没有给出 SAF 舍入误差上界、overflow 条件或固定导纳模型的稳定性证明，因此 Eq. (7) 是架构算法，不是端到端精度保证。

## § 7 — 实验设计与结论

**问题一：SAF 是否真的比商业浮点核更适合反馈求解器？** 作者在 Virtex 5 XC5VSX50T 与 Spartan 3 XC3S5000 上分别综合 commercial-core 与 SAF-based 的 MAC、DP2、DP4。PDF 物理页 6 的 Table 1 显示，Virtex 5 上 commercial DP4 与 SAF DP4 的 latency 分别为 16 与 10 cycle，slice 分别为 848 与 440；Spartan 3 上则为 30 与 12 cycle、2354 与 1526 slice。两者使用相同数量的乘法/DSP block。实验回答是：在这两个老一代器件和给定格式/工具链上，SAF 的优势会随 DP 宽度增大，尤其减少 DP4 的逻辑面积和累加延迟。[pdf:E07] 不能外推为 SAF 对所有现代 DSP 架构、IP 版本和时序目标都更优。

**问题二：完整自动求解器能否装入高端和低成本 FPGA？** PDF 物理页 7 的 Table 2 显示，四个 DP4 的求解器在 Spartan 3 上使用 10,776 slices（32%）、45 BRAM（43%）、64 MULT blocks（61%），达到 100.21 MHz；Virtex 5 上使用 2933 slices（35%）、63 BRAM（47%）、32 DSP blocks（11%），达到 200.96 MHz。作者据此认为芯片仍有空间容纳更复杂求解器或其他并行模型。[pdf:E08] 这个结论只说明资源与静态时序收敛，没有测量功耗、温度降频、I/O 延迟或与其他大型模型共同放置后的拥塞。

**问题三：同一生成框架能否处理不同电路规模？** PDF 物理页 7 的 Table 3 显示，作者测试 boost、三相桥、boost+三相桥，矩阵规模分别为 \(9\times6\)、\(18\times11\)、\(28\times17\)。Virtex 5 步长为 120、135、215 ns，Spartan 3 为 260、290、450 ns，三者都低于 1 μs。[pdf:E09] 这支持“在三种相近的 behavioural PEC 模型上具有可扩展性”，但不是对任意拓扑、强非线性器件或大电网规模的证明。

**问题四：定制格式是否保留足够数值精度？** PDF 物理页 8 的 Fig. 3 显示，boost 模型相对 double-precision 参考时，Virtex 5 的相对误差大致在 \(10^{-5}\)–\(10^{-4}\)，Spartan 3 在 \(10^{-6}\)–\(10^{-5}\)；作者解释后者更好，是因为 Spartan 3 对矩阵和向量都使用 42-bit 非标准浮点，而 Virtex 5 的矩阵条目使用 32-bit、向量使用 42-bit。[pdf:E10] 该图支持指定短时间窗和模型上的数值接近度，没有给出全状态 worst-case error、长期漂移或统计置信区间。

**问题五：组合电路的动态过程是否与软件参考一致？** PDF 物理页 9 的 Fig. 4 / Section 4.4 记录了 circuit #3 的 0.25 s bit/cycle-accurate 离线仿真：boost 与 inverter 的 PWM carrier 为 20 kHz，电机速度先设 400 Hz，在 0.15 s 突变到 100 Hz。与 SimPowerSystem 参考相比报告 0.1%–1% 的 accuracy/error level，作者认为瞬态稳定且满足 HIL 精度需要。[pdf:E11] 这里的误差同时混合了算术格式、开关模型和 motor side explicit forward Euler，实验没有把三类误差拆开。

**问题六：是否真的在实时设备上运行？** PDF 物理页 10 的 Fig. 5 / Section 4.5 显示，求解器部署到 Opal-RT OP5600 的 ML605 FPGA 板，VSC PWM 设为 40 kHz，PMSM 强制为 400 Hz；Fig. 5 是相 A 电压、电流的 oscilloscope capture。[pdf:E12] 这证明了实机实时执行和可观测 I/O，但“high fidelity”主要由波形展示支撑，未给出这一实时工况相对独立测量或离线参考的量化误差。

总体上，实验最强的部分是 implementation feasibility：综合资源、Fmax、步长和实机波形形成了硬件闭环。最弱的部分是模型有效域：只有三种相近拓扑、一个主要瞬态与一个示波器工况，没有故障、dead time、器件非线性、参数扫频或长期稳定性验证。

## § 8 — Take-aways

**5 句话：**

1. 固定导纳开关模型通过保持 MNA 矩阵不变，把在线求解压缩为预计算矩阵上的反复 dot-product。[pdf:E03] [pdf:E04]
2. SAF 把尾数对齐移出累加关键反馈路径，使浮点 DP 获得较短 latency 和较低逻辑面积。[pdf:E05] [pdf:E07]
3. Matlab 脚本自动生成控制逻辑，但尚未从 schematic 自动生成原始网络方程，因此“fully automated”有明确边界。[pdf:E08]
4. 三个测试电路在 Virtex 5 上达到 120–215 ns、在 Spartan 3 上达到 260–450 ns 的步长，证明 sub-microsecond 实现可行。[pdf:E09]
5. 离线参考和 OP5600 实机实验支持所测工况下的精度与实时性，但不足以证明固定导纳模型对故障、器件细节和所有开关事件都可靠。[pdf:E11] [pdf:E12]

**3 句话：** 论文真正的贡献是 model–arithmetic–architecture co-design：先用固定导纳把方程固定，再用 SAF/DP 把固定方程变成短反馈硬件流水。[pdf:E03] [pdf:E06] 自动生成与三拓扑实验说明这不是只为一个 boost 手工拼出的 datapath。[pdf:E08] 然而结果首先证明的是实现可行性，而不是开关模型在所有电力电子工况下的物理真实性。

**1 句话：** 这篇论文展示了如何用“固定矩阵 + history source + 自对齐浮点 DP”把高频 PEC behavioural model 压进 sub-microsecond FPGA 实时步长，但其最关键未决问题仍是固定导纳开关近似的有效域。[pdf:E03] [pdf:E09]

## § 9 — 最脆弱的假设

失败代价最大的假设是：用“小电感表示闭合、小电容表示断开、且令 \(g_C=g_L\)”得到的固定导纳开关，在目标工作区间内能够足够忠实地替代真实开关行为。[pdf:E03] 如果这个假设不成立，预计算矩阵、SAF 和并行 DP 仍可能按时且高精度地计算，却是在快速求解一个错误的网络模型；此时硬件性能不会挽救 HIL 结论。

这一假设可能在轻载 discontinuous conduction、二极管零交越、dead time、同时换相、反向恢复、寄生参数主导或故障状态下失效。论文的状态更新依赖上一时刻电压/电流符号，意味着真实事件发生在步内时可能被量化到下一时间点；而人为的小 \(L/C\) 还可能储存或释放并非真实器件对应的能量。这些是基于模型结构的推断，不是论文已实证的失败。

论文给出的支持是三种拓扑都达到 sub-microsecond 步长，circuit #3 的离线瞬态相对 SimPowerSystem 报告 0.1%–1%，实时板上也得到合理相电压/电流波形。[pdf:E09] [pdf:E11] [pdf:E12] 缺少的证据是：开关参数如何选择、误差对步长与 \(g_C=g_L\) 取值的敏感性、逐开关事件 timing error、故障/极轻载/寄生效应工况，以及与 detailed device model 或实物功率级的量化对照。

## § 10 — 最小复现实验

一周内最有价值的复现不是重建整套自动生成器，而是验证核心闭环：“固定导纳 + 预计算矩阵”在 20 kHz boost 上能否同时满足 sub-microsecond deadline 与可接受的开关事件误差。论文的最小 boost 案例矩阵为 \(9\times6\)，报告步长为 Virtex 5 的 120 ns 或 Spartan 3 的 260 ns，可作为量级参照而非对现代器件的硬性复刻目标。[pdf:E09]

具体做法如下：

1. 自行定义一个参数完整、可公开复算的 boost 电路，固定输入、电感、电容、负载和 20 kHz PWM；论文没有给出足以逐值复刻的完整模型参数，因此不声称重现其同一波形。
2. 建立两个 reference：一是 double-precision、极小步长的 ideal-switch/BEM 模型，二是带 dead time 和 diode 行为的细步长模型。测量输出电压、电感电流、每次导通/关断的零交越时刻与周期能量误差。
3. 按 Eq. (1)–(6) 实现固定导纳版本，离线生成 \(A^{-1}\) 和 \(W\) 矩阵；先用 double precision 验证方程重写与直接线性求解逐步一致，再把矩阵行映射到一个最小并行 DP datapath。[pdf:E03] [pdf:E04] [pdf:E06]
4. 在一块可用 FPGA 上综合，记录 worst negative slack、Fmax、每步 cycle 数与端到端 step latency；同时扫三组 \(g_C=g_L\) 参数和至少三组步长，避免只挑一个看起来好的点。
5. 支持 claim 的标准是：所有步骤无 deadline miss，step latency 小于 1 μs，稳态/瞬态主要量相对 double reference 的归一化误差不超过 1%，且减小步长时开关时刻与能量误差收敛。1% 阈值对应论文离线 circuit #3 报告范围的上界。[pdf:E11]
6. 反驳 claim 的标准是：即使算术和矩阵计算正确，固定导纳模型仍在某类正常开关事件上出现不收敛误差、虚假振荡或能量偏置；或者实现不能在最坏路径上维持 sub-microsecond deadline。

这个实验复现的是论文的核心机制与可证伪条件，不复现其 “fully automated” 脚本、精确 slice 数或 OP5600 I/O 系统。若要声称数值级复现原文，还必须取得作者的原始方程、元件参数、SAF 转换/舍入细节与生成脚本。

## § 11 — 最强反例设计

最强反例应把高吞吐算术与开关模型真实性分离。构造一个 boost+bridge 工况矩阵：从额定负载扫到极轻载 DCM，加入 dead time、二极管反向恢复和 DC-link 寄生，同时安排电流在 PWM 边沿附近过零；以细步长 detailed-switch reference 和功率硬件测量作为双重基线。然后在完全相同的输入下运行论文式固定导纳模型，并分别使用 double precision 与 SAF。固定导纳的状态由上一时刻符号与门极命令更新，这正是攻击步内换相与零交越误差的入口。[pdf:E03]

需要观察的不是一张看起来相似的稳态波形，而是逐事件 turn-on/turn-off timing、二极管导通区间、每周期能量守恒、DC-link ripple、峰值电流、故障触发前后的误判次数。若 double-precision 固定导纳与 SAF 固定导纳彼此高度一致，却都相对 detailed reference 和实物产生同方向、随步长减小仍不消失的偏差，就排除了“只是浮点精度不够”这一替代解释，并直接击中模型假设。论文的 Fig. 3 只说明给定 boost 工况下 SAF 接近 double arithmetic，不能排除两者共同精确求解了有偏的 behavioural model。[pdf:E10]

反例成立的判据可以设为：在不造成 deadline miss 的步长范围内，至少一类正常换相工况出现不可收敛的事件时序误差或能量偏置，并导致控制器作出与实物相反的保护/调制决策。这样的结果会推翻“该框架足以支撑 near-limit HIL”的广义解释，而不只是证明某个器件参数没调好。

## § 12 — Follow-up Research Idea

在电力电子实时仿真领域，高影响工作的评价通常同时看四件事：是否改善了真实而困难的模型有效域，是否有确定的 worst-case latency，是否在可复现硬件上给出资源/时序证据，以及是否用独立 EMT/detailed model 或实物验证而非只展示波形。论文在硬件时序与实机部署上较强，[pdf:E08] [pdf:E12] 但对固定导纳开关的误差边界较弱。

一个候选研究方向是：**passivity-constrained event-corrected history source**。它保留固定 \(A\) 和预 stamp 的硬件优势，却不再把开关状态差异完全压缩为一个静态规则；在每个开关端口增加一个只依赖局部电压、电流、门极和有限历史的校正 history source，并通过离线训练或在线小型查表逼近步内换相误差，同时施加 passivity/energy bound，防止校正源向网络注入非物理能量。这个想法基于论文“状态差异已在 history source 中表达”的结构事实，[pdf:E03] 但属于证据约束下的候选判断；本次没有做充分相关工作检索，不声称 novelty。

（a）驱动需求是：HIL 既要固定矩阵带来的确定延迟，也要在 DCM、dead time、故障和寄生主导区间保持可信开关事件。  
（b）它可能产生研究价值，因为它改变的是“固定矩阵必然绑定固定开关近似”这一问题定义，而不是仅增加更多 DP 或换一块 FPGA。  
（c）可借鉴相邻领域中的 passive model reduction、hybrid-system event localization 与 constrained system identification；学习器只修正端口 history，不直接替代网络求解器。  
（d）第一个证伪实验就是第 11 节的 DCM/换相 sweep：若校正后的模型不能在相同 sub-microsecond deadline 下显著降低逐事件和能量误差，或任一工况破坏 passivity，则放弃该方向。  
（e）它与本文的实质区别是：本文主要通过 MNA 重写、SAF 和 DP 并行加速既定固定导纳模型，[pdf:E04] [pdf:E06] 新方向则直接修改最脆弱的 switch-history 表达，同时把“矩阵保持不变”和“物理误差可控”设为共同约束。
