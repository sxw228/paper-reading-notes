# A General FPGA-Based Accelerated Solver for Electromagnetic Transient Simulations

作者：Tian Liang、Xiaoshan Wu、Ligang Zhao、Qinxiong Huang（PDF 物理页 1，题名页）[pdf:E01]

出处：*Electronics*，15，606（PDF 物理页 1，页眉与题名页）[pdf:E01]

年份：2026（PDF 物理页 1，出版信息）[pdf:E01]

DOI：10.3390/electronics15030606（PDF 物理页 1，页脚）[pdf:E01]

Zotero key：WGUS4P5R

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 新能源与 power electronics（电力电子）占比上升后，系统中出现微秒级开关动态，而传统 DSP/CPU EMT 平台通常支持约 10–100 μs 的步长；论文所概括的既有 FPGA 研究已能做到 1 μs 及以下。与此同时，新型电力系统的仿真规模持续扩大，时间尺度从微秒跨到分钟，运行场景也在增多，单一计算架构很难同时兼顾复杂控制逻辑、短步长电气网络和大规模并行计算（PDF 物理页 2，Introduction）[pdf:E02]。

论文要解决的核心问题是：**能否把通用 EMT 求解过程改写成适合 FPGA 流水并行的统一计算结构，再用 CPU–FPGA heterogeneous computing（异构计算）把控制与电气部分分工，从而在不明显牺牲数值一致性的前提下加速 offline EMT simulation（离线电磁暂态仿真）？** 作者把目标归纳为统一元件模型、降低累计计算时延、提高 FPGA 资源利用率，并通过 PCIe 连接 CPU 与 FPGA（PDF 物理页 1–2，Abstract 与 Introduction）[pdf:E01][pdf:E02]。

这个问题重要，不只是因为“仿真更快”。EMT 的小步长直接决定能否观察 converter switching（变流器开关）、故障穿越和控制环之间的快速耦合；而离线仿真总耗时又决定设计迭代、参数扫描和事故复盘能做多大。论文的工程价值在于尝试把“高层控制适合 CPU、规则密集算术适合 FPGA”变成一个可执行的求解器边界，而不是简单把整套模型硬搬到 FPGA。需要同时注意：本文只用一个并网光伏案例验证，因此它证明的是一个可工作的实现与加速样例，还不是对“任意复杂 EMT 模型都通用”的充分证明。

## § 2 — 前人工作与不足

论文采用的算法底座并不新：经典 nodal analysis（节点分析）先把离散元件改写成 Norton 等值，即“等值导纳并联历史电流源”，再依次做元件状态更新、节点注入电流汇总和节点电压求解（PDF 物理页 3，Section 2.1、Figure 1–2）[pdf:E03]。论文自己的参考文献链还包括 CloudPSS 云端 EMT 仿真、面向大规模新能源的 FPGA 资源优化、带频率相关网络等值的 FPGA 仿真、multi-solver co-simulation（多求解器协同仿真）和 SFA–EMT hybrid simulation（混合仿真）等方向（PDF 物理页 17，References 3、7–11；物理页 18，References 12–13）[pdf:E04][pdf:E05]。在开关建模层面，本文直接采用了 associated discrete circuit，ADC（关联离散电路）模型，并引用 switch-state prediction（开关状态预测）来减少不可达状态（PDF 物理页 18，References 17–18）[pdf:E05]。

**论文对既有方法不足的归纳。** DSP/CPU 以串行为主，强行并行会带来通信开销；已有 FPGA 工作能把步长压低，但常围绕特定模型或局部资源优化；单一架构也不容易按模型的计算特性分配资源。作者因此主张用 CPU 处理 topology analysis（拓扑分析）、初始化和复杂控制分支，用 FPGA 处理重复、规则、可深流水的电气计算（PDF 物理页 2，Introduction）[pdf:E02]。

**基于证据的批评。** 本文实验只把异构平台与 pure CPU CloudPSS 4.5 比较，未与已有 FPGA solver、GPU solver 或其他 heterogeneous solver 做同硬件条件对比（PDF 物理页 9，Section 3.1；物理页 15，Table 2）[pdf:E06][pdf:E07]。因此，论文能够支持“该实现相对所选 CPU 基线更快且波形高度一致”，却不能仅凭现有实验确认三件事：统一模型本身是否优于既有通用化方法、两级累计是否是主要 speedup 来源、以及整个平台相对最强 FPGA/异构 prior work 是否具有明确优势。由于本任务禁止包外检索，本文的 novelty 只能标为**候选判断**，不能据此宣布已被相关工作充分校准。

## § 3 — 重建作者的思考路径

以下是基于论文证据逆向重建的思路，不是作者逐字给出的研发日志。

1. 先从经典节点法出发：每个时间步都要重复“元件更新 → 电流汇总 → 线性方程求解”，其中大量运算结构固定，天然适合硬件流水（PDF 物理页 3，Figure 1–2）[pdf:E03]。
2. 如果为每种元件单独设计一套 FPGA 数据通路，模型一扩展就会带来大量定制逻辑；于是把元件差异压缩进参数矩阵和少数历史电流更新模板，让硬件面对的是统一接口（PDF 物理页 4–5，Figure 3、Figure 5、Equations 1–3）[pdf:E08][pdf:E09]。
3. 元件更新模块复杂度不同，若所有模块完成后才开始求和，快模块会空等；于是先在组内按完成顺序累计，再做组间向量累计，并用 atomic addition（原子加法）避免并行写冲突（PDF 物理页 7，Section 2.4、Figure 7）[pdf:E10]。
4. 节点电压求解最终是 impedance matrix（阻抗矩阵）与节点电流向量的乘加，适合并行 multiplier 加流水 accumulator；既然累计逻辑已经存在，就复用 atomic/accumulator 结构降低资源占用（PDF 物理页 8–9，Equation 6、Figure 9）[pdf:E11][pdf:E06]。
5. 开关变化会改变系统矩阵。为避免 FPGA 每步在线分解矩阵，作者让 CPU 预先求出可用状态对应的阻抗矩阵，FPGA 按开关状态选择；状态太多时，再用不可达状态预判、ADC 恒导纳模型和 DDR–BRAM 分层存储缓解（PDF 物理页 8，Figure 8 与其后正文）[pdf:E12]。
6. 最后把复杂初始化与控制留给 CPU，把规则电气求解放到 FPGA，并在每个相同步长末交换控制量、电气量和同步信号，于是形成完整 CPU–FPGA 闭环（PDF 物理页 10，Figure 11）[pdf:E13]。

这条路径的本质是：先找出 EMT 中最规则、最重复的算术核，再把不规则拓扑和控制逻辑移出 FPGA；所谓“通用”主要来自**参数化接口和任务分工**，而不是来自一个能自动覆盖所有元件物理的全新方程。

## § 4 — 核心 Intuition

不要让 FPGA 理解每一种电气元件的完整语义，而是让所有元件都以“等值导纳 + 历史电流”的统一 Norton 接口参与同一条流水线（PDF 物理页 3、5，Figure 2、Equations 1–3）[pdf:E03][pdf:E09]。把拓扑解析、参数生成和控制分支交给 CPU，把组件更新、电流归并和矩阵–向量乘法交给 FPGA，就能让两类处理器各做自己擅长的工作（PDF 物理页 4、10，Figure 4、Figure 11）[pdf:E08][pdf:E13]。方法奏效的关键不是单个公式更快，而是让整个时间步的数据依赖变得可流式调度，并尽量避免 FPGA 在线处理不规则矩阵构造。

## § 5 — 具体方法与完整 Pipeline

以论文的并网 PV system（光伏系统）为例，输入是电气拓扑、元件参数、控制参数、初始状态和仿真步长，输出是每个时间步的节点电压、电流、功率及控制波形。完整 pipeline 如下。

1. **CPU 初始化。** CPU 完成拓扑分析、节点编号、元件排序、参数映射，并预求 binary-resistor switch（二值电阻开关）可能状态对应的 full-state impedance matrices（全状态阻抗矩阵）；节点数、拓扑、步长、元件参数和矩阵通过 PCIe 送入 FPGA 初始化模块（PDF 物理页 4，Section 2.2、Figure 4）[pdf:E08]。
2. **元件统一与离散。** FPGA 把元件分为 basic RLC、two-branch RLC、three-branch RLC、source 和 switch 五类更新模块；变压器和输电线由两支路或三支路 RLC 组合表示。普通元件从上一步节点电压和历史电流出发，用参数化的 Equations 1–3 更新本步历史电流；PWM 模块在 FPGA 内生成高频开关信号（PDF 物理页 5，Section 2.3、Figure 5）[pdf:E09]。
3. **开关与事件处理。** 二值电阻模型用小电阻/大电阻表示 ON/OFF，状态变化时需要选择新的系统矩阵；ADC 模型让 ON/OFF 两态保持同一等值导纳，只切换历史电流公式，从而避免矩阵随开关变化。论文声称两种模型都兼容，但没有报告自动判断哪些路径可安全使用 ADC（PDF 物理页 6–7，Figure 6、Equations 4–5）[pdf:E14][pdf:E10]。
4. **节点电流归并。** 各元件模块并行工作，先完成的组先做 intra-group merging（组内归并）；所有组完成后，再用 floating-point accumulator（浮点累加器）做 inter-group vector accumulation（组间向量累计）。atomic operation 在读–改–写期间锁住节点电流位置，防止 data race（数据竞争）（PDF 物理页 7，Figure 7）[pdf:E10]。
5. **矩阵选择与节点电压求解。** 当前开关位序列充当地址，从预计算矩阵中选择本步阻抗矩阵；大量矩阵放在 off-chip DDR，每步所需矩阵读入 on-chip BRAM cache。随后 FPGA 用并行浮点乘法器和复用的累加结构计算 \(U_n=Y^{-1}I_n\)（PDF 物理页 8–9，Figure 8、Equation 6、Figure 9）[pdf:E12][pdf:E11][pdf:E06]。
6. **CPU–FPGA 同步推进。** FPGA 计算 electrical system，CPU 同时计算 control system；每步结束后 FPGA 向 CPU 发同步信号和电气量，CPU 返回本步控制结果供下一步使用。论文实验中两侧采用同一个 \(dT\)，即 1 μs；**多速率或异步时间推进机制未报告**（PDF 物理页 10、12，Figure 11 与 Section 3.3）[pdf:E13][pdf:E15]。
7. **PV 闭环实例。** FPGA 侧包含 three-level Boost、three-phase three-level NPC inverter、滤波器和变压器；CPU 侧运行 converter dual-loop control（双环控制）、MPPT 和 LVRT。FPGA 把 AC/DC 电压电流及 PV 输出送给 CPU，CPU 返回受控源和调制参考，FPGA 内置 PWM 再驱动开关，形成闭环（PDF 物理页 10–11，Figure 12–13 及相邻正文）[pdf:E13][pdf:E16]。

数值表示方面，实验所有内部计算采用 double-precision floating point（双精度浮点）；离散方法使用 backward Euler（后向欧拉）（PDF 物理页 12，Section 3.3）[pdf:E15]。执行平台是 AMD Ryzen 9 CPU 与 XCKU115 FPGA，经 PCIe 连接（PDF 物理页 9，Figure 10）[pdf:E06]。论文未报告 CPU 的具体型号、FPGA 时钟频率、PCIe 代际与带宽、RTL/HLS 代码结构、时序收敛结果或每个 kernel 的 cycle-level latency，这些缺口会限制精确复现与跨平台比较。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有新的数学定理或收敛性证明，核心数学是“元件离散后的 Norton 等值 + 节点方程 + 矩阵向量乘法”。它的贡献主要在如何把这些公式组织成 FPGA-friendly dataflow（适合 FPGA 的数据流）。

普通元件的统一更新式为：

\[
U_k(t)=U_{n,F_k}(t-dT)-U_{n,T_k}(t-dT), \tag{1}
\]

\[
I_k(t)=G_kU_k(t)-I_{h,k}(t-dT), \tag{2}
\]

\[
I_{h,k}(t)=P_kU_k(t)+Q_kI_k(t). \tag{3}
\]

这里 \(k\) 是元件索引，\(F_k\) 与 \(T_k\) 是支路两端节点，\(U_k\) 是支路电压，\(I_k\) 是支路电流，\(I_{h,k}\) 是把上一步动态状态折叠后的历史电流；\(G_k\)、\(P_k\)、\(Q_k\) 分别是等值导纳矩阵、支路电压项系数矩阵和支路电流项系数矩阵。CPU 在初始化时生成这些参数，因此同一硬件数据路可通过换参数兼容后向欧拉、梯形积分等离散方法（PDF 物理页 5–6，Equations 1–3 及变量定义）[pdf:E09][pdf:E14]。直观上，Equation 1 取出支路两端的旧节点电压差，Equation 2 计算当前支路电流，Equation 3 再把本步状态压回下一步要用的历史电流。

ADC 开关在导通时使用：

\[
I_{h,k}(t)=P_{1k}U_k(t)+Q_{1k}I_k(t),\qquad P_{1k}=0,\quad Q_{1k}=-1, \tag{4}
\]

关断时使用：

\[
I_{h,k}(t)=P_{2k}U_k(t)+Q_{2k}I_k(t),\qquad P_{2k}=Y_{sw},\quad Q_{2k}=-R_{sw}Y_{sw}. \tag{5}
\]

通过选取 \(L_{sw}\)、\(C_{sw}\) 和 \(R_{sw}\)，ADC 让两态的等值导纳 \(Y_{sw}\) 保持不变，变化被移到历史电流更新里；这就是它能免去每次开关事件重建节点矩阵的原因（PDF 物理页 6–7，Figure 6、Equations 4–5）[pdf:E14][pdf:E10]。

所有元件历史电流按节点汇总后得到节点注入电流向量 \(I_n\)。论文把节点电压求解直接写成：

\[
U_n=Y^{-1}I_n, \tag{6}
\]

其中 \(Y^{-1}\) 被视为系统阻抗矩阵。工程上的关键是 CPU 预先得到候选 \(Y^{-1}\)，FPGA 每步只做矩阵选择和 matrix–vector multiplication（矩阵–向量乘法），避开在线矩阵分解（PDF 物理页 8，Equation 6 与相邻正文）[pdf:E11]。

实验的 maximum relative error（最大相对误差）定义为：

\[
\max\!\left(\frac{|X_{\mathrm{cpu,fpga}}-X_{\mathrm{cpu}}|}{|X_{\mathrm{cpu}}|}\right), \tag{7}
\]

并在 1 s 窗口上计算，另报告 RMS error（PDF 物理页 12，Equation 7）[pdf:E15]。**基于证据的推断：** 对正弦电压或电流，\(X_{\mathrm{cpu}}\) 会接近或穿过零点，Equation 7 的分母可能使指标病态甚至未定义；论文没有说明零值阈值、剔除规则或正则化方式。因而极小的“最大相对误差”虽与叠合波形一致，但在严格复现时必须先澄清指标实现，不能只抄最终数字（PDF 物理页 13–14，Figure 14–16 显示过零波形）[pdf:E17][pdf:E18][pdf:E19]。

## § 7 — 实验设计与结论

- **问题：稳态数值结果能否与 CPU 基线一致？** 实验：并网 PV 系统在额定工况运行，比较 AC 侧 A 相电压、电压 RMS、A 相电流和电流 RMS。答案：波形几乎重合，作者报告最大相对误差 \(3.54\times10^{-10}\)，最大 RMS 误差 \(2.92\times10^{-12}\)（PDF 物理页 13，Section 3.3.1、Figure 14）[pdf:E17]。
- **问题：控制指令突变时能否保持一致？** 实验：\(t=2\) s 时有功参考从 1.0 p.u. 降至 0.5 p.u.，\(t=2.3\) s 升至 0.8 p.u.；无功参考在 \(t=2.5\) s 从 0 变为 0.2 p.u.，在 \(t=2.7\) s 变为 −0.2 p.u.。答案：两平台的电流、有功和无功响应重合，作者报告最大相对误差 \(8.65\times10^{-8}\)，最大 RMS 误差 \(3.58\times10^{-12}\)（PDF 物理页 13–14，Section 3.3.2、Figure 15）[pdf:E20][pdf:E18]。
- **问题：电网故障和 LVRT 动态下是否仍一致？** 实验：\(t=5\) s 施加 AC 侧三相短路，持续 180 ms，PCC 电压约跌至 0.4 p.u.；观察电压、电流、无功支撑与有功恢复。答案：异构平台与 CPU 基线的动态响应高度一致，作者报告最大相对误差 \(8.93\times10^{-8}\)，最大 RMS 误差 \(4.47\times10^{-12}\)（PDF 物理页 13–15，Figure 16 及相邻正文）[pdf:E20][pdf:E19][pdf:E21]。
- **问题：是否获得端到端加速？** 实验：仿真 10 s，比较初始化、控制、元件更新、节点电流归并、节点电压求解及通信等耗时。答案：Table 2 给出的异构平台总计算时间为 11.13（不含初始化）和 13.61（含初始化），CPU 平台为 28.98 和 29.91；作者据此报告不含初始化的计算效率提升 61.59%，含初始化的总耗时降低 54.5%（PDF 物理页 15，Table 2 与其后正文）[pdf:E07][pdf:E22]。表头未显式标出时间单位，因此这些值不应被进一步外推为严格的 real-time factor。
- **问题：FPGA 资源是否随节点规模可扩展？** 实验：在 XCKU115 上统计 16、32、64、128 节点配置的 LUT、FF、BRAM、DSP 利用率。答案：资源随节点数增加；128 节点时 LUT 76%、FF 52%、BRAM 36%、DSP 41%，作者据此认为仍有扩展余量（PDF 物理页 16，Table 3）[pdf:E23]。

实验还统一使用 1 μs 步长、backward Euler 和 double precision；PV 参数表给出 10 kV 网侧线电压、0.63 kV AC 基值、1.08 kV DC 基值和 16 kHz PWM 载波等设置（PDF 物理页 12，Table 1 与 Section 3.3）[pdf:E15]。这些设置使数值对齐更可信，但验证范围仍很窄：只有一个 PV 拓扑、一块 XCKU115、一个 CPU 基线、一个步长和一种主要积分法；没有多模型 benchmark、没有同类 FPGA baseline、没有 kernel ablation、没有 Fmax/周期级时延，也没有量化 PCIe 延迟随模型规模或控制复杂度的变化。

因此，实验最扎实地支持的是两条结论：**该实现能在所测 PV 案例中复现 CPU 波形；该硬件分工在所测平台上显著缩短总耗时。** 它没有单独证明“模型统一”“两级累计”“矩阵预选”各自贡献了多少，也没有充分证明 solver 的 generality（通用性）。

## § 8 — Take-aways

**5 句话：**

1. 论文把 EMT 元件统一成参数化 Norton/历史电流接口，使同一组 FPGA kernel 能处理多类元件（PDF 物理页 3–6）[pdf:E03][pdf:E09][pdf:E14]。
2. CPU 负责不规则的初始化和控制，FPGA 负责规则的元件更新、电流归并与矩阵–向量乘法，这是整套系统的主要架构思想（PDF 物理页 4、10）[pdf:E08][pdf:E13]。
3. 两级电流归并、atomic addition 和累加器复用旨在减少等待与资源重复，而预计算矩阵把在线拓扑求解改成状态选择（PDF 物理页 7–9）[pdf:E10][pdf:E12][pdf:E06]。
4. 在 1 μs、后向欧拉、双精度的并网 PV 案例中，异构波形与 CPU 基线高度一致，且论文报告不含初始化的效率提升 61.59%（PDF 物理页 12–15）[pdf:E15][pdf:E17][pdf:E21][pdf:E22]。
5. 最关键的未决问题是开关状态矩阵的组合爆炸与真实大模型下的通信、存储和时序，而不是单个浮点乘加是否能在 FPGA 上运行（PDF 物理页 8、16）[pdf:E12][pdf:E23]。

**3 句话：**

1. 这是一个把经典 EMT 节点法系统性映射到 CPU–FPGA dataflow 的工程方案，而非新的数值理论（PDF 物理页 3–10）[pdf:E03][pdf:E13]。
2. 单一 PV 案例证明了可行性、数值对齐和相对 CPU 的加速，但没有完成对“通用”与“可大规模扩展”的强验证（PDF 物理页 13–16）[pdf:E17][pdf:E07][pdf:E23]。
3. 是否能摆脱全状态矩阵枚举，决定了这条路线能否从一个成功 demo 变成真正通用的 EMT solver（PDF 物理页 8）[pdf:E12]。

**1 句话：** 论文最有价值的贡献是把 EMT 的规则算术核组织成可复用 FPGA 流水并与 CPU 控制闭环协同，但其 generality 最终受制于未被充分量化的开关状态空间与系统级开销（PDF 物理页 8、15–16）[pdf:E12][pdf:E22][pdf:E23]。

## § 9 — 最脆弱的假设

最脆弱的假设是：**对于一个“通用”复杂系统，所有会改变导纳矩阵的关键开关状态仍能被预计算、筛减、存储并在每个时间步内及时取出。** 二值开关数为 \(S\) 时，合法组合的理论上界随 \(2^S\) 增长；论文也明确承认 full-state impedance matrices 会随开关组合指数增长，并提出三种缓解手段：预判并剔除物理不可达状态、在非关键路径改用恒导纳 ADC、把大批矩阵放入 DDR 并将当步矩阵读入 BRAM（PDF 物理页 8，Figure 8 后正文）[pdf:E12]。

这个假设一旦失效，核心贡献会直接受损，因为 Equation 6 的高速求解依赖“矩阵已经存在且能准时到达”。在多电平变流器、模块化拓扑、故障重构或大量独立开关并存时，合法状态仍可能很多；关键换流路径又未必允许用 ADC 近似，否则速度问题会被转化成模型误差问题。DDR 容量、矩阵加载带宽、BRAM cache 命中和状态预测准确性中的任何一个成为瓶颈，FPGA 的乘加流水再快也无法维持每步吞吐。

论文为该假设提供的证据有限。它确实展示了一个含 three-level Boost 与 three-level NPC inverter 的 PV 案例能够运行（PDF 物理页 10–12，Figure 12–13）[pdf:E13][pdf:E16]，但没有报告该案例究竟存了多少矩阵、预判删除了多少状态、DDR 占用多少、每步矩阵搬运耗时多少，也没有按“开关数量/可达状态数”做 scaling study。Table 3 只按节点数展示资源利用率，不能替代对状态空间的验证（PDF 物理页 16，Table 3）[pdf:E23]。因此，本文最强的工程结果仍建立在一个尚未被压力测试的可管理状态空间上。

## § 10 — 最小复现实验

一周内不应追求复刻整套 PV 平台，因为论文没有公开完整 netlist、全部控制参数、HDL/RTL、FPGA 时钟和 PCIe 配置。更有效的最小复现，是只验证核心 claim：**参数化元件更新 + 两级归并 + 预选阻抗矩阵能否在包含真实开关事件的短步长电路上同时保持数值一致和端到端加速。**

- **数据与模型：** 自建一个 16 节点三相 RLC 网络，接一个六开关 converter；固定使用 1 μs、backward Euler、double precision，并采用 16 kHz PWM，使设置与论文的主要实验条件同量级（论文条件见 PDF 物理页 12，Table 1 与 Section 3.3）[pdf:E15]。
- **实现：** CPU 写一个逐步节点法 reference；FPGA/HLS 只实现 Equations 1–6 对应的 component update、两级 node-current merging 和 matrix–vector kernel。先用 binary-resistor switch，再切换 ADC，CPU 负责产生 gate signal；PCIe 传输和同步必须计入总耗时（方法依据见 PDF 物理页 5–10）[pdf:E09][pdf:E10][pdf:E12][pdf:E13]。
- **测量：** 记录开关瞬间与稳态的 waveform RMS error、归一化 \(L_2\) error、Equation 7 在 \(|X_{cpu}|>\epsilon\) 区间的相对误差、每步 kernel latency、端到端耗时、PCIe/同步占比、LUT/FF/BRAM/DSP 与矩阵存储量。
- **支持标准：** 在开关瞬态中无系统性偏差，RMS error 与论文报告的 \(10^{-12}\) 量级结果方向一致；同时 electrical kernel 至少比单线程 CPU 快 2 倍，计入通信后端到端仍有至少 1.5 倍加速，并且 binary 与 ADC 两种路径的误差–速度差异可解释。
- **反驳标准：** 只要在切换瞬间出现大于 \(10^{-5}\) 的持续归一化误差，或加入 PCIe/同步后 speedup 消失，或矩阵读取使每步时延不可预测，就足以反驳“核心机制天然带来通用加速”的强版本。论文的原始端到端对照值和资源量级可作为参考，而不是必须复现的硬阈值（PDF 物理页 15–16，Table 2–3）[pdf:E07][pdf:E23]。

这个实验小到一周可做，却能把论文目前混在一起的三件事拆开：数值模型是否一致、FPGA kernel 是否更快、系统级通信是否吃掉收益。

## § 11 — 最强反例设计

最强反例不是再换一个普通 PV 工况，而是构造一个**合法开关状态很多、且关键路径不能安全改用 ADC 的多电平系统**。我会选 64 或 128 节点的 cascaded H-bridge/MMC 类网络，设置至少二十个相位错开的独立开关单元，再叠加一个会改变导通路径的故障；所有关键换流支路先用 binary-resistor model，以高精度 CPU 在线矩阵更新作为参考。

实验同时记录四组量：实际访问过的 distinct topology states（不同拓扑状态数）、预计算矩阵总存储、DDR→BRAM 取数时延与 cache miss、端到端每步时延；然后逐步增加独立开关数，而不是只增加节点数。再做一组 ADC 替代实验，检查为了控制状态数而改成恒导纳后，故障电流峰值、换流瞬态和能量误差是否恶化。论文自己已承认矩阵数会指数增长，并依赖预判、ADC 与 DDR 缓解（PDF 物理页 8）[pdf:E12]。

如果状态数或矩阵搬运在中等开关规模就压垮 1 μs 步进，或者 ADC 替代必须牺牲关键瞬态准确性，那么最合理的替代解释将是：**本文的 speedup 主要来自所选 PV 拓扑具有可管理的状态集合和有利的 CPU/FPGA 分工，而不是 solver 对一般开关网络都同样有效。** 这会直接攻击论文标题中的“General”，也比泛泛指出“只测了一个案例”更有判别力。Table 3 的节点资源曲线不能化解这一反例，因为它没有测状态数量、外存带宽或 timing closure（PDF 物理页 16，Table 3）[pdf:E23]。

## § 12 — Follow-up Research Idea

在 EMT + FPGA 领域，高影响工作通常不仅要有正确波形和局部 speedup，还要同时证明数值稳定性、确定性时延、硬件可实现性、跨拓扑扩展和真实系统价值。基于第 9 节的核心限制，我提出一个**候选研究方向**：**Topology-on-Demand EMT（按需拓扑 EMT）——用事件驱动的增量稀疏更新替代全状态阻抗矩阵枚举。** 本任务没有做包外 related-work 检索，因此不声称该方向具有 novelty。

- **(a) 未满足需求。** 多电平、模块化和故障重构系统可能产生大量合法状态，预存全部 \(Y^{-1}\) 会在容量和带宽上失控；论文也把多电平、频率相关、磁饱和与多异构设备列为后续扩展方向（PDF 物理页 16，Conclusion）[pdf:E24]。
- **(b) 研究价值。** 把“状态枚举是否可管理”从前提变成被解决的问题，才能让 solver 的 generality 由单案例功能性上升为可量化的 topology scalability（拓扑可扩展性）；同时仍可保留 FPGA 对固定拓扑区间的高吞吐优势。
- **(c) 可借鉴的方法。** 从 incremental sparse linear algebra（增量稀疏线性代数）借用 low-rank update、Sherman–Morrison–Woodbury 或动态 \(LDL^T\) 因子更新；从 event-driven simulation（事件驱动仿真）借用“只有开关事件发生时才更新矩阵”；从 cache-aware scheduling（缓存感知调度）借用热点拓扑缓存。CPU/GPU 处理稀有的结构更新，FPGA 持续流式执行元件更新、归并和已就绪矩阵的乘加，但研究问题的核心不是简单“再加一块 GPU”，而是改变拓扑状态的表示方式。
- **(d) 第一个证伪实验。** 在同一 128 节点、二十个以上独立关键开关的故障工况下，对比本文式 lookup solver、在线稀疏重分解和增量更新；要求相同步长与误差标准，测每步最坏时延、平均时延、矩阵存储、外存流量和故障波形。如果增量方法在频繁事件下不能维持确定性时延，或数值误差/资源代价超过 lookup 方案，它就应被判定失败。
- **(e) 与本文的实质区别。** 本文把 topology change（拓扑变化）表示为“在预计算矩阵集合中选一个”；候选方案把它表示为“对当前稀疏系统做局部结构更新”。前者用空间换时间并假设状态可枚举，后者试图让成本与实际发生的开关事件和局部秩变化相关，因此改变了问题定义，而不是只在现有 pipeline 后面增加一个模块。

论文参考文献中已经出现 ADC、switch-state prediction、multi-solver 与 hybrid simulation 等邻近线索（PDF 物理页 18，References 12–18）[pdf:E05]，但仅凭本包不能判断上述组合是否已有同等方案；最诚实的定位是：这是由本文证据直接驱动、且可被上述首个实验快速否证的候选研究计划。
