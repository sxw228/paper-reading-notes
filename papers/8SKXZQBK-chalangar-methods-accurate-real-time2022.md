# Methods for the Accurate Real-Time Simulation of High-Frequency Power Converters

- 作者：Hossein Chalangar、Tarek Ould-Bachir、Keyhan Sheshyekani、Jean Mahseredjian
- 出处：IEEE Transactions on Industrial Electronics, 69(9), 2022, pp. 9613–9623
- DOI：10.1109/TIE.2021.3114706
- Zotero key：8SKXZQBK
- 阅读边界：以下论文事实均来自源 PDF；“基于证据的推断”“候选判断”是本文读者侧分析，不冒充作者结论。

## § 1 — 研究问题与重要性

这篇论文解决的是一个很具体的实时仿真矛盾：高开关频率（high-switching-frequency, HSF）变换器要求仿真步长缩短到几十纳秒，但二极管等自然换相器件的导通状态又不能仅由门极信号直接给出。传统电路求解器通常要在同一个时间点反复执行“解网络方程 → 检查二极管电压/电流 → 修改开关状态 → 重解”，迭代次数事先未知；而 real-time simulation（RTS）的每一步必须在固定预算内完成，否则硬件在环（HIL）接口就会错过物理时钟。[pdf:E01] [pdf:E02]

作者的目标不是单纯把某个矩阵乘得更快，而是同时保住四件事：使用能较真实表示导通与关断状态的 resistive switch model（RSM），准确处理自然换相，维持隐式积分的稳定性，并把运行期计算变成固定延迟、非迭代的数据通路。论文给出的主张是：direct mapped method（DMM）可以把当前输入和状态直接映射为可行二极管组合；对于由多个 HSF 子变换器构成的大电路，再把 DMM 与 single-delay decoupling（SDD）或 network tearing technique（NTT）结合，便可把局部和全局迭代从实时环中移除。[pdf:E02] [pdf:E03]

其工程价值在于让控制器能够在接近真实开关时间尺度的数字对象上闭环测试。论文的 EV battery charger（EVBC）算例同时包含单相整流、两相交错 boost 和三相 LLC，开关频率最高为 200 kHz；作者在 FPGA 上报告了 75–175 ns 的候选实现步长，并以一个 100 kHz resonant boost converter（RBC）补充实测。[pdf:E01] [pdf:E05] [pdf:E08] [pdf:E09] 需要严格区分的是：论文展示了 FPGA 实时执行和 DAC/示波器输出，但没有在本文实测部分展示外接真实控制器的闭环 HIL 稳定性试验；因此“可作为 HIL 平台”是应用动机，不等于本文已经验证了完整闭环 HIL。

## § 2 — 前人工作与不足

作者把既有路线分成几类，每一类都在“速度、准确性、确定延迟、可扩展性”中牺牲了至少一项。

首先，associated discrete circuit（ADC）模型计算便宜，早期 FPGA RTS 借它取得小步长，但作者指出 ADC 会恶化仿真精度，因此不适合作为 HSF 变换器的实用高保真模型。RSM 更能复现系统级暂态，却因拓扑随开关状态变化而需要更多存储与计算；尤其自然换相器件的状态取决于求解后的电压或电流，通常必须迭代。[pdf:E01]

其次，预计算并存储所有开关组合对应的矩阵可以避免运行期矩阵分解，但组合数随开关数量增长，受 FPGA 片上存储限制。Sherman–Morrison–Woodbury 一类逆矩阵更新方法避免全量预存，却被作者判断为不适合 HSF 场景。NTT 等 diakoptics 方法通过 tearing 把大网络拆成并行子电路，缓解规模和计算量问题，但标准 NTT 同时存在局部迭代与全局迭代，仍难保证很小且固定的实时步长。[pdf:E01] [pdf:E02] [pdf:E03]

再次，SDD 在接口处使用上一时间点的电压或电流，把子电路直接解耦，结构简单但会引入一个时间步的延迟，可能产生数值误差甚至不稳定。LIM 和显式积分也能隔离开关网络、取得 50–100 ns 量级步长，但论文指出显式法有稳定性问题，并且某些 switching-function 表示无法访问单个开关变量。既有 DMM 已在特定 resonant converter 上证明了小步长和非迭代求解，却缺少一般数学表述，也难直接扩展到多变换器网络。[pdf:E02] [pdf:E10]

Table VIII 把这种取舍压缩得很清楚：已有工作可报告 15–100 ns 步长，但分别带有不考虑二极管、步长不固定、依赖特定拓扑、无法监测单个开关或不能覆盖全部运行模态等限制；本文方法以更高 FPGA 资源占用为代价，在 200 kHz EVBC 上给出 75 ns 和 100 ns 的主实现步长。[pdf:E10] 这不是“本文在所有指标上都优于前人”，而是把目标函数改成：允许用更多硬件资源换取一般化的自然换相处理、可观测开关变量和确定运行路径。

## § 3 — 重建作者的思考路径

可以从实时约束本身逆向重建这项工作的思路。

第一步，观察真正破坏 fixed-step RTS 的不是线性网络方程本身，而是开关状态未知所造成的条件分支和反复重解。受控开关的状态来自门极，难点集中在二极管：它的导通条件最终是电压或电流符号约束。[pdf:E02]

第二步，如果对给定受控开关组合和固定离散步长，网络方程是线性的，那么二极管电压就可以写成“当前输入和上一状态”的线性函数。每一种可能的二极管组合都对应一组线性不等式；满足这些不等式的状态区域，就是该组合自洽的区域。于是运行期问题不必继续表述成“猜状态再迭代”，可以改成“判断当前向量落在哪个预先划分的区域”。[pdf:E03]

第三步，这个区域分类仍可能很贵。作者因此在离线阶段用 Fourier–Motzkin elimination（FME）删去不可行组合和冗余不等式，把各区域的边界收集成独立超平面；运行期只需计算这些超平面的符号模式，再通过 TCAM/RAM 查表得到二极管组合。[pdf:E03] [pdf:E04]

第四步，单个 DMM 的矩阵与查找规模仍会随着大型多变换器电路膨胀。自然的扩展不是继续做一个巨型 lookup，而是沿物理接口把网络拆成子电路：DMM 消除每个子电路内部的 local iteration，SDD 或 relaxed NTT 则切断同一时刻的跨子电路循环依赖。作者由此得到 DMM-SDD 与 DMM-NTT 两条路线，前者更省计算，后者用额外全局接口求解换取更高精度。[pdf:E03] [pdf:E05]

这条思考链的关键转折，是把“在线非线性/互补状态求解”前移为“离线可行域构造 + 在线确定性分类”。FPGA 并非最后才附加的加速器；TCAM、ROM 和固定尺寸 matrix-vector multiplication（MVM）从一开始就参与了算法形态的选择。

## § 4 — 核心 Intuition

DMM 的核心直觉是：自然换相器件看似要求在线试错，其实对固定拓扑、参数和离散步长而言，每个自洽二极管组合都占据状态空间中的一个可预先计算的多面锥区域；实时阶段只要识别当前点属于哪个区域，就能一次得到正确组合。[pdf:E03] 对大型网络，不再试图建立一个全局巨型映射，而是让各子电路用 DMM 消除局部迭代，再用带延迟的接口量或简化 NTT 解除跨子电路的代数闭环。[pdf:E03]

## § 5 — 具体方法与完整 Pipeline

以论文中的 EVBC 为例，输入是门极信号、独立电源以及上一时间步的电感电流和电容电压；输出是本步的二极管状态、更新后的电气状态和需要观测的电压/电流。完整流程分为一次性的离线生成和每个时间步重复的在线执行。

1. **建立开关网络。** 作者用 RSM 表示半导体器件，并以 backward Euler 形成固定步长的离散网络。EVBC 沿 dc bus 拆为两个子电路：Stage 1 是单相整流器与两相 interleaved boost，Stage 2 是 inverter、三相 LLC 谐振腔和三相整流器；SDD 在接口交换上一时刻的 \(v_{dc}\) 与 \(i_{dc}\)，NTT 则把两个子电路化成 Norton 等值并求公共 dc-link 电压。[pdf:E05]
2. **按受控开关组合生成候选方程。** 对每个 \(\sigma_c\)，写出二极管电压 \(\mathbf v_d=\mathbf Q^\sigma\mathbf z\)，其中 \(\mathbf z\) 汇集独立输入与状态；对每个候选 \(\sigma_d\)，用二极管 ON/OFF 对应的符号矩阵检查 \(\mathbf S(\sigma_d)\mathbf Q^\sigma\mathbf z<0\) 是否可行。[pdf:E03]
3. **离线删去不可行组合。** Algorithm 1 对每个候选组合运行 FME，剔除矛盾不等式与冗余行，收集线性独立边界形成 \(\mathbf W^{\sigma_c}\)，并把符号模式写入 TCAM、把对应的可行二极管组合写入 RAM。[pdf:E04]
4. **在线识别开关状态。** FPGA 计算 \(\mathbf p=\operatorname{sgn}(\mathbf W^{\sigma_c}\mathbf z)\)，以 \(\mathbf p\) 查询 TCAM，编码匹配地址，再从 RAM 读出唯一的 \(\sigma_d\)。这条路径用固定数量的乘加、比较和存储访问替代迭代。[pdf:E03] [pdf:E08]
5. **更新状态。** 选定开关组合后，用预计算的 \(\mathbf F_k^{\sigma_k}\) 执行一次 MVM，得到当前状态 \(\mathbf x_k(t)\) 和所需输出 \(\mathbf y_k(t)\)。在 DMM-NTT 中，额外的 NTT 数据通路先根据两个子电路的 Norton 电流和开关相关电导求 \(v_{dc}\)，再完成各子电路最后一级状态更新。[pdf:E04] [pdf:E08]
6. **在下一固定时刻重复。** 受控开关组合来自新门极信号，状态向量来自上一时间步；每步没有“直到收敛”为止的循环，因此硬件 latency 可以直接转成 RTS time step。

具体规模揭示了方法如何压缩组合爆炸：Stage 1 有 6 个二极管，理论上 64 种组合，实际只保留 16 种，由 32 个非冗余超平面区分；Stage 2 同样有 64 个候选，只保留 19 种，由 30 个超平面区分。在状态更新中，两级的 \(\mathbf F\) 矩阵分别为 \(4\times6\) 与 \(10\times11\)。[pdf:E06] 这说明 DMM 并不是保存所有 \(2^n\) 个状态矩阵，而是先利用电路约束删去大部分不可能区域，再用符号特征索引可行状态。

## § 6 — 核心数学推导（无形式化数学则跳过）

先从物理意义出发。一个理想二极管的状态与其端口变量必须自洽：假定 ON 后，电压/电流极性必须符合导通条件；假定 OFF 后，也必须符合截止条件。传统迭代器通过反复修改假定来寻找自洽点。DMM 证明，只要离散网络在给定开关组合下是线性的，这个自洽性可以等价写成状态空间中的线性不等式分类。

对固定受控开关组合 \(\sigma_c\)，作者定义

\[
f^{\sigma_c}:\mathbf z(t)\mapsto \sigma_d ,
\]

其中 \(\mathbf z(t)\) 是独立输入和状态变量，\(\sigma_d\) 是二极管组合。若某个完整开关组合 \(\sigma=(\sigma_c,\sigma_d)\) 下的二极管电压为

\[
\mathbf v_d(t)=\mathbf Q^\sigma \mathbf z(t),
\]

那么该组合自洽的条件写成

\[
\mathbf S(\sigma_d)\mathbf Q^\sigma\mathbf z(t)<0. \tag{3}
\]

\(\mathbf S\) 的对角元按每个二极管 ON/OFF 取 \(-1\) 或 \(+1\)，所以式 (3) 只是把不同器件的极性条件统一成同一个“小于零”形式。[pdf:E03]

对每个候选 \(\sigma_d\)，式 (3) 的解集

\[
\mathcal C^{\sigma_c}(\sigma_d)
=\{\mathbf z\in\mathbb R^n\mid
\mathbf S(\sigma_d)\mathbf Q^\sigma\mathbf z<0\}
\]

是由过原点超平面围成的 convex cone。FME 用来判断这个集合是否为空，并删除冗余不等式。把所有可行组合的独立边界行合并为 \(\mathbf W^{\sigma_c}\)，就得到符号向量

\[
\mathbf p^{\sigma_c}(\mathbf z)
=\operatorname{sgn}(\mathbf W^{\sigma_c}\mathbf z). \tag{6}
\]

作者的 generality argument 是：相同的符号向量对应同一个可行锥，因此存在一个满射 lookup \(\phi^{\sigma_c}\)，使

\[
f^{\sigma_c}(\mathbf z)
=\phi^{\sigma_c}(\mathbf p^{\sigma_c}(\mathbf z)). \tag{8}
\]

论文用单相整流器说明实现：四个可行组合 \(\{0,6,9,15\}\) 分别由四维符号向量中的部分位确定，“don't care” 位适合直接放进 TCAM，命中地址再索引 RAM 中的组合值。[pdf:E03] [pdf:E04]

网络更新的另一层数学是“先选模式，再做线性状态推进”。子电路的 MANA 方程写成

\[
\mathbf A_k^{\sigma_k}\mathbf q_k(t)
=\mathbf B_k
\begin{bmatrix}
\mathbf x_k(t-\Delta t),\mathbf u_k(t)
\end{bmatrix}^{T},
\]

预消元后只保留 FPGA 真正需要的状态和输出：

\[
\begin{bmatrix}
\mathbf x_k(t),\mathbf y_k(t)
\end{bmatrix}^{T}
=\mathbf F_k^{\sigma_k}\mathbf z_k(t). \tag{14}
\]

因此运行期的数值核心就是“DMM 选 \(\sigma_k\) + 对应 \(\mathbf F_k^{\sigma_k}\) 做 MVM”。[pdf:E04]

对于 NTT，每个子电路用多端口等值

\[
\mathbf w_k^{out}
=\mathbf w_k^h-\mathbf H_k^{\sigma_k}\mathbf w_k^{in},
\]

全局 tableau 经过 partial Gaussian elimination 后只需求接口量。EVBC 的两端口特例为

\[
v_{dc}(t)
=\left(g_1^{\sigma_1}+g_2^{\sigma_2}\right)^{-1}
\left(i_1^h(t)+i_2^h(t)\right). \tag{19}
\]

这里 \(g_k^{\sigma_k}\) 随子电路开关组合变化；FPGA 把统一组合 \(\{\sigma_1,\sigma_2\}\) 用作 ROM 地址，取出预计算的逆电导，再更新 \(v_{dc}\)。[pdf:E05] [pdf:E08]

一个重要限定是，论文所谓“exact”指在给定 RSM、离散规则、固定参数和固定 \(\Delta t\) 下，DMM-NTT 与该离散网络的自洽解一致；它不是对连续时间真实器件的零误差声明。

## § 7 — 实验设计与结论

**问题 1：DMM 相比廉价的 explicit status update（ESU）是否真的更准确？**  
作者以 50 ns 离线步长运行 EVBC，测试序列包括正常启动、输出短路、故障清除、LLC 谐振腔相间故障、再次清除，以及 LLC 开关频率由 200 kHz 降至 150 kHz。参考结果来自 EMTP，比较 ESU-SDD、ESU-NTT、DMM-SDD 和 DMM-NTT 的四个状态变量。[pdf:E06] 结果是 ESU 的 2-norm 相对误差约为 2%–8.9%；DMM-SDD 各项约 \(4.7\times10^{-3}\%\) 至 \(1.3\times10^{-2}\%\)；DMM-NTT 则在 \(10^{-9}\%\)–\(10^{-8}\%\) 量级，作者将其解释为仅剩数值伪差，波形在正常和故障区间均与 EMTP 重合。[pdf:E06] [pdf:E07]

**问题 2：这种准确性能否放进固定延迟 FPGA 数据通路？**  
作者在 Xilinx Kintex K325T 目标上实现 ESU-SDD、DMM-SDD 与 DMM-NTT，全部设计可运行在 320 MHz。EVBC 的 single-stage DMM-SDD 和 DMM-NTT 分别达到 75 ns 与 100 ns；对应 double-stage 版本为 125 ns 与 175 ns。代价是资源明显上升：例如 single-stage DMM-NTT 使用 6513 LUT、16835 registers、143.5 BRAM 和 480 DSP blocks，而 ESU-SDD 为 1787 LUT、5572 registers、36.5 BRAM 和 156 DSP blocks。[pdf:E08] 这支持“以面积换确定性与精度”，但不支持“DMM 更省硬件”。

**问题 3：固定点实现是否破坏数值结果？**  
实现采用 35-bit fixed-point，其中 32 位是小数位，并通过 per-unit normalization 缓解动态范围限制。[pdf:E06] EVBC FPGA 相对离线计算的四个 2-norm 误差分别为 \(2.04\times10^{-2}\%\)、\(9.63\times10^{-3}\%\)、\(8.51\times10^{-3}\%\) 和 \(8.65\times10^{-3}\%\)；DAC 示波器显示 LLC 谐振电流频率为 200 kHz。[pdf:E09] 这些结果说明 fixed-point datapath 没有显著吞掉离线 DMM 的精度。

**问题 4：方法是否只对 EVBC 有效？**  
作者又实现 100 kHz RBC。Algorithm 1 得到至多 10 个可行组合、\(14\times6\) 的 \(\mathbf W\) 和 \(5\times6\) 的 \(\mathbf F\)；100 ns 每步执行 209 个算术操作，其中 114 次乘法、95 次加法。该实现占 Kintex K325T 的 1.1% LUT、1.6% registers、6.5% BRAM、25.7% DSP，五个状态变量的 2-norm 误差均低于 0.06%，示波器读得谐振电流 99.935 kHz，接近设定的 100 kHz。[pdf:E09] [pdf:E10]

综合来看，证据充分支持“对两个指定电路和给定参数，DMM 可在 FPGA 上以固定小步长、高数值一致性执行”。证据较弱的部分是范围外泛化：论文没有展示参数漂移、器件非理想、测量噪声、变步长、不同 FPGA 系列或真实控制器闭环下的系统性压力测试。

## § 8 — Take-aways

**5 句话。**  
1. HSF 变换器 RTS 的关键瓶颈是自然换相状态带来的不定次迭代，而不仅是矩阵规模。[pdf:E01]  
2. DMM 把每种可行二极管组合表示成状态空间中的线性不等式区域，离线建图、在线查表。[pdf:E03]  
3. DMM-SDD 用较小的接口处理成本取得很高精度，DMM-NTT 增加计算和资源以取得接近离散参考解的结果。[pdf:E06] [pdf:E08]  
4. EVBC 的 75 ns/100 ns single-stage 实现和 RBC 的 100 ns 实测表明方法确实能映射为确定性 FPGA datapath。[pdf:E08] [pdf:E09]  
5. 这种收益依赖预先固定的拓扑、参数和时间步，并以 BRAM/DSP 占用显著增加为代价。

**3 句话。**  
DMM 的本质是把在线二极管互补求解编译成离线几何划分和在线 TCAM/RAM 分类。[pdf:E03] DMM 与 SDD/NTT 的组合让复杂 HSF 多变换器网络在 FPGA 上同时获得固定步长和高离散数值精度，但面积成本比 ESU 明显更高。[pdf:E08] 本文最可信的结论限于已实现的 EVBC 与 RBC、固定参数和开环/示波器测试，不能直接外推为任意 HIL 闭环都稳定。

**1 句话。**  
这篇论文证明了“先离线编译开关可行域、再在线一次查表和线性更新”是把自然换相 HSF 变换器送入纳秒级 FPGA RTS 的有效路线。[pdf:E03] [pdf:E09]

## § 9 — 最脆弱的假设

最脆弱的假设是：离线构造的可行域划分在运行期仍然完整、互斥并与真实离散网络一致。论文明确说明每个 cone 的形状由电路参数和仿真步长 \(\Delta t\) 决定，\(\mathbf W\)、TCAM 内容以及各模式的 \(\mathbf F^\sigma\) 也都由这些量预计算。[pdf:E03] 这意味着“无需迭代”并不是免费得到的，而是把拓扑、元件参数、积分规则和步长的确定性作为编译期契约。

在实际系统中，电感、电容、电阻会随温度和工作点漂移；半导体存在压降、死区、寄生参数与恢复过程；HIL 调度也可能产生步长 jitter。只要这些变化使开关边界移动，名义 \(\mathbf W\) 的符号模式就可能把靠近超平面的状态点分到错误 cone。错误并不一定表现为小的连续误差，而可能直接选错二极管组合，随后使用错误的 \(\mathbf F^\sigma\) 推进状态。TCAM 在边界上如何处理零值、fixed-point 量化如何改变符号，也没有被单独压力测试。

论文提供的支持是两个具体电路、包含短路和 LLC 相间故障的 EVBC 序列、以及固定点 FPGA 对离线结果的小误差。[pdf:E06] [pdf:E09] 这些证据说明名义配置内部的映射工作良好，却没有证明同一映射对参数漂移、步长变化和边界邻域仍保持唯一正确。因此，这一假设一旦失败，会直接击中“准确且非迭代”这一核心贡献，而不是只让性能稍微下降。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 EVBC 硬件，而是“DMM 查表能否在自然换相和故障切换时逐步复现迭代 RSM 的开关组合”。建议使用论文 RBC 或更小的整流-boost 子电路，固定 backward Euler 步长为 100 ns。

1. 用同一份 RSM 和参数实现一个高精度参考求解器：每步迭代二极管组合，直到端口电压/电流与状态自洽。
2. 枚举受控开关组合，用线性不等式可行性计算生成 \(\mathbf W\) 与组合表；先不做 FPGA，只在软件中实现符号分类和 lookup。
3. 运行启动、稳态、负载阶跃和短路清除序列。逐时间步记录两种求解器的 \(\sigma_d\)、状态向量、迭代次数，以及 DMM 到最近边界的 margin \(\min_i|(\mathbf W\mathbf z)_i|\)。
4. 主要指标不是平均 waveform error，而是：开关组合逐步一致率、状态 2-norm 误差、最坏单步误差、参考法运行时间的波动，以及 DMM 固定操作数。
5. 如果 DMM 在所有非边界时间点给出与收敛参考相同的 \(\sigma_d\)，状态误差接近浮点舍入且运行路径固定，就支持核心 claim；若在 margin 明显非零时仍选错组合，或故障切换后出现持续偏离，就直接反驳实现或一般性论证。

论文 RBC 给出的对照目标是 10 个以内可行组合、\(14\times6\) 的 \(\mathbf W\)、\(5\times6\) 的 \(\mathbf F\)，以及 100 ns FPGA 步长和低于 0.06% 的状态误差。[pdf:E09] 一周版不必复制资源利用率，但应保存所有 mismatch 的状态向量，使每个失败都能回到具体超平面与组合。

## § 11 — 最强反例设计

最强反例不是换一个更大的电路看它“会不会太慢”，而是让运行期网络轻微偏离编译期模型，同时把轨迹推到开关边界附近。具体做法是：用名义 \(L,C,R,\Delta t\) 生成一次 \(\mathbf W\)、TCAM/RAM 和 \(\mathbf F^\sigma\)，运行时保持这套映射冻结；随后对电感、电容和导通电阻施加独立的 \(\pm20\%\) 扰动，对步长加入小幅 jitter，并用负载阶跃或输入相位扫描寻找 \(\min_i|(\mathbf W\mathbf z)_i|\) 很小的状态。每一步用“实际扰动参数下的迭代 RSM”作参考。

攻击判据应是离散事件级的：统计 DMM 与参考求解器首次选择不同 \(\sigma_d\) 的参数、margin 和持续时间，再观察错误模式是否导致能量、峰值电流或故障恢复轨迹发生显著偏差。若很小的参数偏移便在高 margin 区域触发错误，说明“固定几何图”比论文的应用叙述脆弱；若错误只集中在数学边界且不会累积，则核心方法反而获得更强支持。

这个反例同时排除了一个常见替代解释：当前实验的极低误差可能主要来自 DMM 与 EMTP 使用同一组理想化参数和相同离散模型，而不是映射对物理不确定性天然稳健。论文没有声称已经解决参数不确定性，因此该反例不是说作者数据错误；它检验的是方法从“名义模型的精确编译”外推到“真实 HIL 对象”的边界。

## § 12 — Follow-up Research Idea

在 power electronics / EMT 实时仿真领域，高影响工作通常不仅看更小步长，还看数值稳定性、故障与换相保真度、确定 latency、资源可实现性，以及能否在硬件和闭环工况下复核。本文已经很好地覆盖名义模型下的速度、精度和 FPGA 实现，却把“模型与时间步固定”留作隐含契约。[pdf:E08] [pdf:E09]

**候选研究想法：把 DMM 从名义点 lookup 改写为带正确性证书的 robust switch-region compiler。** 目标不再是为一组参数生成唯一超平面图，而是为参数区间、fixed-point 量化误差和有限步长 jitter 生成三类区域：可证明只有一个二极管组合成立的 safe region；多个组合都可能成立的 boundary region；模型契约已失效的 out-of-envelope region。在线 datapath 在 safe region 保持原 DMM 的一次查表；进入 boundary region 时触发一个有严格最大次数的小型局部解析器，进入 out-of-envelope region 则显式报告模型失效，而不是静默输出某个组合。

未满足的需求是：真实 HIL 环境中的器件容差和数值量化不应把“精确映射”悄悄变成错误模式选择。它的研究价值在于把本文的确定 latency 从经验实现属性升级为“正常区固定延迟、边界区有界延迟、越界可检测”的可验证契约。可借鉴相邻领域的 multiparametric programming、interval arithmetic、robust explicit MPC 与 hybrid-system reachability，用集合而不是单个参数点构造开关区域。

第一个能证伪该想法的实验很直接：在 RBC 上对 \(L,C,R,\Delta t\) 给定小区间，用穷举/区间参考求解器扫描边界邻域；若编译器声称 safe 的任一点仍出现两个可行组合，或其硬件区域膨胀导致大多数正常轨迹都退化到边界解析器，那么方案失去核心价值。与本文的实质区别在于，研究对象从“固定模型下如何消除迭代”改成“模型不确定时如何证明何处可以安全消除迭代”。由于本次阅读按约束没有额外检索相关文献，这只是候选方向，不声称 novelty。

---

## 证据缓存索引

| ID | PDF 物理页 | 定位 | 文件 |
|---|---:|---|---|
| E01 | 1 | 标题、摘要、Introduction 与既有方法背景 | `_evidence/E01-p001-title-abstract-intro.png` |
| E02 | 2 | 贡献、iterative solver、SDD/NTT 与 DMM 组合 | `_evidence/E02-p002-contributions-iteration-decoupling.png` |
| E03 | 3 | DMM 一般表述、式 (1)–(9)、FME 与 TCAM/RAM | `_evidence/E03-p003-dmm-formulation.png` |
| E04 | 4 | Algorithm 1、NTT 全局方程、子电路状态更新式 (10)–(15) | `_evidence/E04-p004-algorithm-network-equations.png` |
| E05 | 5 | EVBC 拓扑、参数、SDD/NTT 接口与式 (16)–(19) | `_evidence/E05-p005-evbc-topology-parameters.png` |
| E06 | 6 | 可行组合规模、故障测试序列、Table III 精度结果 | `_evidence/E06-p006-accuracy-test-sequence.png` |
| E07 | 7 | EVBC 波形与三种 FPGA datapath | `_evidence/E07-p007-waveforms-datapaths.png` |
| E08 | 8 | Table IV/V 计算量、时步和 FPGA 资源，TCAM/RAM 实现 | `_evidence/E08-p008-fpga-burden-resources.png` |
| E09 | 9 | 实验装置、EVBC/RBC 实时测试与 Table VI/VII | `_evidence/E09-p009-realtime-hardware-tests.png` |
| E10 | 10 | Table VIII 与 Conclusion | `_evidence/E10-p010-comparison-conclusion.png` |
