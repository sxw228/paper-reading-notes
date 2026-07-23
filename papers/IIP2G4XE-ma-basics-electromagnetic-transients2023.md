# Basics of Electromagnetic Transients: Underlying mathematics

> 论文身份：Xin Ma、Xiao-Ping Zhang，IEEE Electrification Magazine，2023，DOI `10.1109/MELE.2023.3320485`。[pdf:E01]  
> Zotero key：`IIP2G4XE`  
> slug：`ma-basics-electromagnetic-transients2023`  
> 唯一内容真相：`_source.pdf`  
> PDF SHA-256：`168e0a7a0d8b877514e43709fa94e0bd28bf14f44f8b8805a107f04be5dbef54`

本文是一篇面向 EMT 学习者的教程与实现综述，不应误读成从零提出全新数值方法的 research paper。下文把“论文原文明确声称”与“基于证据的推断”分开；所有精确公式、平台参数、实验数字、图表趋势和作者结论均绑定源 PDF 的上下文截图。

## § 1 — 研究问题与重要性

论文处理的实际问题是：怎样从连续时间的电气与机电微分方程出发，得到一个每个离散步都能算完、数值上不轻易发散、又能组合成大网络并满足实时 deadline 的 EMT 解法。数字计算机只能在离散时刻给出状态；如果元件离散、网络装配或非线性处理不当，下一步可能出现矩阵奇异或不收敛。作者因此把“积分方法—元件 companion model—网络方程—实时执行”作为一条完整链来讲，而不是只展示商业软件里的拖拽模块。[pdf:E01][pdf:E02]

其重要性有两层。物理层面，EMT 关心故障、开关和快速电磁过程，连续波形中的高频与突变不能靠少数稳态相量点替代。数值层面，每个时间步都必须把储能元件的记忆、非线性设备和全网约束闭合；实时仿真还要求执行时间 \(T_e\) 小于所选步长 \(\Delta t\)，否则结果即使数学上正确，也会错过真实时钟。[pdf:E02][pdf:E10]

论文直接给出的目标不是刷新某一个 benchmark，而是提供一份“避免常见错误”的简洁建模指南：比较三种积分方法；逐步构造线性与非线性元件；解释节点电压法、补偿法、频移法以及 offline/real-time 的差异；最后用四机 11 节点系统展示 FPGA 实现。[pdf:E02]

## § 2 — 前人工作与不足

论文把技术谱系追溯到 Dommel：20 世纪 60 年代开始以节点矩阵求 EMT，随后为非线性与时变元件发展 compensation method，并以隐式梯形积分构造 EMTP 的 companion circuit；EMTP、PSCAD 和 RTDS 则把这些思想工程化，RTDS 以并行结构实现约 50–100 μs 的实时步长。[pdf:E01][pdf:E02]

这些既有系统已经“能算”，不足却在可理解性与可重建性。商业工具把大量细节封装在元件库后面，初学者容易知道如何连接 block，却不知道为何一个电感会变成“电导 + 历史电流源”、为什么非线性设备不能直接塞进同一线性节点矩阵、以及怎样判断实时执行是否真正满足 deadline。论文明确指出，设计不良的 EMT 解法会导致矩阵奇异和 nonconvergence；它要补的是从基本运算到完整求解链的教育缺口，而不是取代这些成熟工具。[pdf:E02]

相关方法各自承担不同角色：forward Euler 是显式、便宜但一阶误差会积累；backward Euler 是隐式并引入局部截断误差；trapezoidal rule 同时使用步首和步末信息，作者把它作为 EMT 中兼顾稳定性与精度的主方法。节点电压法适合全部元件都能线性 Norton 化的网络；compensation method 把非线性部分隔离成注入，从而在保留线性网络求解的同时闭合非线性端口；frequency-shift method 则把带通信号搬到较低的等效频带，以允许更大的步长。[pdf:E02][pdf:E03][pdf:E07][pdf:E08]

## § 3 — 重建作者的思考路径

可以从一个最小问题逆向重建这条路线。

第一步，连续电感满足“电压决定电流变化率”，但数字机不能连续积分，只能从 \(t-\Delta t\) 推进到 \(t\)。因此先要选一个离散积分规则。显式规则只看过去，计算方便却更容易把局部误差带到未来；完全看未来的隐式规则较稳但数值耗散更大；梯形规则把区间两端平均，给出一个适合网络闭合的折中。[pdf:E02][pdf:E03]

第二步，一旦用梯形规则离散，电感、电容和一般 RLC 支路在当前步的未知量都可以拆成两部分：一个乘当前节点电压的常量电导，以及一个只由上一时刻已知量组成的 history source。这样，微分元件在当前步看起来就像一个静态 Norton 支路；全网可以统一装配成 \(Y U=I\)。[pdf:E03][pdf:E04][pdf:E06]

第三步，传输线的传播延迟和同步机、励磁、调速器的非线性/耦合说明“所有设备直接 Norton 化”并不总成立。传输线需要 traveling-wave 与模态解耦；同步机需要先预测慢机械量，再做 Park 变换、更新电磁量和转矩，最后回代机械状态；非线性端口则先从线性网络中隔离，再用 compensation response 叠加回来。[pdf:E05][pdf:E06][pdf:E07][pdf:E10]

第四步，离散方程算得对还不等于实时。必须把每一步拆成有确定依赖的 schedule，并验证资源、数值一致性和 \(T_e<\Delta t\)。于是作者最后自然落到 FPGA 上的四机 11 节点案例：不是为了证明所有电网都能在该板上运行，而是把前面的数学链落到真实硬件约束。[pdf:E09][pdf:E11][pdf:E12]

## § 4 — 核心 Intuition

核心 intuition 是：把每个动态元件在“当前一步”重写成一个静态电导与一个携带过去状态的电流源，就能把微分方程问题转成重复求解同一种节点网络问题。线性部分保持统一矩阵结构，非线性部分通过预测、顺序更新或 compensation 接口闭合；实时性则变成“这条依赖链能否在一个固定步长内完成”的工程判据。[pdf:E03][pdf:E06][pdf:E10]

换句话说，EMT 求解不是把整个连续过程一次算出来，而是反复回答同一个局部问题：“已知过去的储能与传播记忆，什么当前节点电压能让所有支路电流同时守恒？”

## § 5 — 具体方法与完整 Pipeline

以“故障作用于含传输线和同步机的网络”为例，完整 pipeline 可以重建为：

1. **选择时间网格。** 设定固定 \(\Delta t\)，以梯形规则把每个连续积分改写为步首和步末导数的平均。forward/backward Euler 作为误差与稳定性的参照。[pdf:E02][pdf:E03]
2. **线性支路 companion 化。** 对 R、L、C 及组合支路，计算当前步固定的等效电导 \(G_{\mathrm{RLC}}\)，并从上一时刻电压、电流更新历史源。Table 1 给出多种支路对应的 \(G_{\mathrm{RLC}},H_{\mathrm{RLC}},J_{\mathrm{RLC}}\)。[pdf:E03][pdf:E04]
3. **处理线路传播。** lumped line 保留相域耦合；distributed traveling-wave line 则由 surge impedance 和 travel time 建模，并把三相量变换到零、正、负序模态域，以解除矩阵的互耦项，各模态独立推进。[pdf:E05][pdf:E06]
4. **顺序更新同步机与控制。** 先预测机械角速度和角度，再做 abc→dq0 的 Park transform，更新绕组电流与磁链、计算电磁转矩，最后回代机械状态。励磁器和调速器被拆成加减乘、limiter、PID/低通环节，并分别离散为当前项和 history term。[pdf:E07][pdf:E08][pdf:E09]
5. **装配线性网络。** 等效电导进入 admittance matrix \(Y\)，history source 进入注入向量 \(I\)，求 \(U=Y^{-1}I\) 后回算支路电流并更新下一步历史量。[pdf:E06]
6. **闭合非线性端口。** 先移除非线性元件得到 open-circuit linear network，算开路端电压与端口等效响应；再求非线性端口状态，把 closed-circuit response 叠加回节点解。[pdf:E07][pdf:E10]
7. **按真实时钟调度。** 把网络、同步机、控制器、机械与励磁等计算排进一个 step，确认执行结束早于下一时钟边界；同时检查 FPGA resource utilization 和与 MATLAB 参考波形的差异。[pdf:E09][pdf:E10][pdf:E11]
8. **输出并推进。** 本步节点电压、支路电流、机电状态和控制量成为下一步的历史输入，循环至终止时间。

## § 6 — 核心数学推导（先讲物理与数值直觉）

### 6.1 积分规则为何决定 EMT 的“记忆”

设 \(f\) 是状态，\(u=\mathrm{d}f/\mathrm{d}t\) 是它的变化率。物理上，\(\Delta t\) 内的状态增量就是变化率曲线下的面积。三种方法只是用不同形状估计这块面积：

\[
\begin{aligned}
\text{Forward Euler: }&f_n=f_{n-1}+\Delta t\,u_{n-1},\\
\text{Backward Euler: }&f_n=f_{n-1}+\Delta t\,u_n,\\
\text{Trapezoidal: }&f_n=f_{n-1}+\frac{\Delta t}{2}(u_{n-1}+u_n).
\end{aligned}
\]

第一式把整段斜率冻结为旧值；第二式冻结为新值；第三式取两端平均。论文将梯形法描述为二阶、隐式且“绝对稳定”，并强调历史误差不会随时间无限累积。[pdf:E02][pdf:E03] 这里需要谨慎：这是作者给出的教程性表述，并不等于任意含开关、刚性非线性或不连续事件的系统都不会出现数值振荡。

### 6.2 电感如何变成 Norton companion

电感的物理式是

\[
\frac{\mathrm{d}i_{km}}{\mathrm{d}t}=\frac{v_k-v_m}{L}.
\]

对一个步长应用梯形积分，有

\[
i_{km,n}
=\underbrace{\frac{\Delta t}{2L}}_{G_L}(v_{k,n}-v_{m,n})
+\underbrace{\left[i_{km,n-1}+\frac{\Delta t}{2L}(v_{k,n-1}-v_{m,n-1})\right]}_{I_{L,\mathrm{hist}}}.
\]

直觉上，\(G_L\) 是“当前电压立刻影响当前电流”的接口斜率；括号中的 history current 则封装电感先前已经存储的磁能。于是当前步的电感等价为电导 \(G_L=\Delta t/(2L)\) 与已知历史电流源并联，Figure 2 同时给出这一推导和等效电路。[pdf:E03]

同理，任意固定参数 RLC 支路可写成“当前端电压项 + history term”，而 \(G_{\mathrm{RLC}},H_{\mathrm{RLC}},J_{\mathrm{RLC}}\) 在计算期间保持常数。其数值价值是 admittance matrix 不必因储能状态变化而重新改变结构；每步主要更新的是右端历史源。[pdf:E04]

### 6.3 从支路到网络

将所有线性 companion 的电导 stamp 到 \(Y\)，将独立源与 history source 汇入 \(I\)，即可写成

\[
Y U=I,\qquad U=Y^{-1}I.
\]

这不是说实际实现必须显式求逆；论文用该式说明节点电压由 admittance matrix 和注入共同确定，并提到 Gaussian elimination。[pdf:E06] 数值上更关键的含义是：只要拓扑和等效电导固定，网络左端结构可复用，而状态记忆集中在右端。

### 6.4 非线性为何要补偿

非线性端口没有固定斜率，不能直接被一个恒定 Norton 电导完整表示。compensation method 先求移除该端口后的线性网络开路响应，再以端口单位注入得到等效 response，之后求非线性端口的闭合电压/电流，最后叠加回全网。物理上相当于“线性电网告诉设备端口环境，设备告诉电网它在该环境下实际吸收/注入多少电流”；数值上则避免把整张网都纳入非线性迭代。[pdf:E07][pdf:E10]

## § 7 — 实验设计与结论

**问题 1：这些离散模型能否在真实 FPGA 上组成一个电力系统？**  
实验：作者在单块 Virtex-6 ML605 上实现四机 11 节点系统，使用 100 MHz 全局时钟、floating-point IP cores 和 50 μs EMT 步长；板卡资源基线为 768 DSP、416 RAM、301,440 registers、150,720 LUTs。[pdf:E09]  
答案：bitstream 可以在资源与 timing 约束内实现；Table 4 报告 registers 35%、LUTs 87%、memory 9%、DSP 93%。这说明该具体实现可装入该器件，但 LUT 与 DSP 已接近上限，不能直接据此断言“同一块板还可轻松扩大很多”。[pdf:E12]

**问题 2：FPGA 波形是否与参考实现一致？**  
实验：MATLAB 2018b 64-bit Windows 作为 offline reference，MATLAB 与 FPGA 都取 50 μs；在 bus 7 分别施加 1.0–1.1 s 的单相接地故障和三相故障，比较 \(i_d\)、电磁转矩和机械转矩。[pdf:E09][pdf:E11][pdf:E12]  
答案：作者报告这些量的相对误差保持在 5% 以内，Figure 8 中两组波形总体重合。[pdf:E11][pdf:E12] 这验证的是 FPGA 与所选 MATLAB 离散模型的一致性，不是对真实物理装置的独立校准。

**问题 3：一个 step 是否满足实时 deadline？**  
实验：作者把 NET、同步机、governor、mechanical、excitation 等阶段画成依赖 schedule，并与 50 μs 的步长比较。[pdf:E11]  
答案：正文报告总计算时间 25.4 μs，小于 50 μs，因而留有时间余量。[pdf:E12] 但 Figure 8(b) 的时间轴末端标为 24.7 μs，而正文写 25.4 μs；这是源 PDF 内部的 0.7 μs 不一致，复现时必须先澄清计时边界，不能择一当作无条件真值。[pdf:E11][pdf:E12]

**问题 4：哪类故障更能激发高频暂态？**  
实验：对两类故障的电磁转矩计算标准差。[pdf:E12]  
答案：作者报告单相接地故障与三相故障的标准差分别为 0.3318 和 0.0892，据此认为前者对 EMT 验证更敏感。[pdf:E12]

## § 8 — Take-aways

### 5 句话

1. EMT 的核心工程化动作，是把连续动态元件变成“当前电导 + 历史源”的离散 companion。[pdf:E03][pdf:E04]
2. 梯形法的两端平均让这种 companion 既保留状态记忆，又能装入统一节点矩阵。[pdf:E02][pdf:E03]
3. 传输线、同步机和控制器不能只写一句“离散化”，还必须明确传播延迟、坐标变换与机电更新的顺序依赖。[pdf:E05][pdf:E06][pdf:E07][pdf:E08]
4. 非线性用 compensation 从线性网络中隔离，实时实现则把数学依赖进一步变成 deadline 内的 schedule。[pdf:E07][pdf:E10][pdf:E11]
5. 论文的 ML605 案例支持“该具体模型在 50 μs 步长内可运行”，但资源接近上限、参考真值不独立且 timing 数字有内部差异，不能外推为普遍的规模与精度保证。[pdf:E09][pdf:E11][pdf:E12]

### 3 句话

梯形离散把动态支路转为可 stamp 的 Norton companion，节点法负责线性全网，顺序更新与 compensation 负责非线性设备。作者把这条数学链映射到单块 ML605，并在四机 11 节点故障案例上报告小于 5% 的参考差异与小于 50 μs 的执行时间。[pdf:E03][pdf:E10][pdf:E12] 最值得保留的批评是：它证明了实现一致性，却尚未以独立物理真值、跨步长和更强事件压力测试证明模型误差的来源与上界。

### 1 句话

这篇文章最有价值的不是某个孤立公式，而是展示了如何把“连续物理—离散记忆—网络闭合—硬件 deadline”连成一条 EMT 实现链。

## § 9 — 最脆弱的假设

最脆弱的假设是：**同一步长、同一建模链上的 MATLAB 结果可以充当足够独立的 accuracy reference。**

作者明确说明 MATLAB 与 FPGA 都使用 50 μs 步长，并据两者波形相对误差小于 5% 来支持模型有效性。[pdf:E09][pdf:E12] 如果两端共享同样的梯形离散、同样的同步机简化、同样的事件落点与参数，那么二者可能高度一致，却一起偏离更细步长解、解析解或真实设备。此时“小于 5%”主要证明硬件映射没有明显改变参考算法，而不能分解以下误差：时间离散误差、元件模型误差、故障事件定位误差、floating-point/IP 实现误差。

这个假设一旦不成立，论文最强的实验结论会从“动态暂态被正确表示”收缩为“FPGA 复现了 MATLAB 版本”。论文没有报告跨步长 convergence、与更高精度 EMT 工具的交叉验证、板级 I/O 闭环或实物录波对照；这些是 PDF 中未报告的缺口，而不是本文已证明失败。[pdf:E09][pdf:E12]

此外，资源结论也很脆弱：DSP 已用 93%、LUT 已用 87%，正文却称同板仍允许更大系统。[pdf:E12] 这最多说明仍未达到 100%，不能说明增加哪些元件、增加多少以及 routing/timing closure 仍会成功。

## § 10 — 最小复现实验

一周内最值得做的不是重建完整四机系统，而是把“数值正确性”和“实时可执行性”拆开验证。

**数据与模型：** 构造一个有解析或高精度参考的两节点 RLC 网络，再加入一个可控的非线性电流端口；设置阶跃与不对齐时间网格的开关事件。参数做小范围扫描，覆盖欠阻尼、强刚性和端口非线性三类工况。

**实现：**

1. 按 Figure 2 用 forward Euler、backward Euler、trapezoidal 三种方式实现 RLC companion。[pdf:E02][pdf:E03]
2. 按 Figure 7 的 open-circuit/closed-circuit 步骤实现 compensation interface。[pdf:E10]
3. 在 CPU 或现有 FPGA 上使用固定 50 μs 主步长；另用 0.5–1 μs 的高精度求解作为独立 reference，而不是复用同一离散链。
4. 记录每个 step 的执行时间分布，而不只记录一次或平均值。

**测量：** 峰值误差、相位误差、能量/阻尼偏差、事件后第一个峰值、最大与 99.9 percentile 执行时间，以及是否出现 \(T_e\ge\Delta t\)。

**支持 claim 的结果：** trapezoidal companion 在主要参数区间内比两种 Euler 更稳定/准确；compensation 结果与直接高精度非线性求解一致；最坏执行时间仍小于 50 μs。

**反驳 claim 的结果：** MATLAB/FPGA 同步长结果彼此接近，但二者相对高精度 reference 同时出现显著偏差；或平均执行时间合格而尾部 step 超时。这个实验能直接检验第 9 节的共享误差假设，且不依赖复现论文未公开的完整四机参数。

## § 11 — 最强反例设计

最强反例是“**同算法一致、物理答案错误**”。

选一个轻阻尼 RLC 与饱和型非线性端口组成的小系统，把故障施加时刻放在两个 50 μs 采样点之间；再让系统固有振荡频率接近该步长可分辨范围。用论文式 MATLAB 与 FPGA 实现共享 50 μs 梯形离散，同时用事件精确定位、亚微秒步长的独立求解器生成 reference。预期攻击路径是：

\[
\text{共享时间网格与模型}
\rightarrow \text{MATLAB 和 FPGA 波形高度一致}
\rightarrow \text{两者都错过事件瞬间或高频峰值}
\rightarrow \text{“小于 5\% 的相互误差”无法证明物理保真度}.
\]

如果该工况下 MATLAB–FPGA 仍小于 5%，但相对独立 reference 的首峰、相位或能量误差显著更大，就给出了具体替代解释：论文图中的重合来自共同离散误差，而不一定来自准确的 EMT 表示。若 FPGA 在所有这些 event phase、刚性与非线性扫描中仍保持独立 reference 误差受限且无 deadline miss，则这个反例失败，反而会显著增强论文 claim。

另一个工程攻击点是以最坏情况而非 nominal schedule 测时。Figure 8 给出固定阶段排程，但正文 25.4 μs 与图中 24.7 μs 已不一致。[pdf:E11][pdf:E12] 应让非线性端口经历 limiter 切换或额外迭代，观察尾部执行时间是否跨过 50 μs。

## § 12 — Follow-up Research Idea

### 候选想法：deadline-aware、带独立误差凭证的 EMT companion network

本领域高影响工作通常不仅要求算法在离线波形上“看起来一致”，还要求数值稳定性、明确的误差边界、可实现的实时 schedule、资源代价以及硬件或 HIL 场景中的系统价值。基于本文最脆弱的共享 reference 假设，可以把研究目标从“在固定步长内复现同一个模型”改成：

> 在每个固定 real-time macro-step 内，同时输出状态和一个可审计的局部误差凭证；只对检测到事件、刚性或高频能量的局部元件启用预预算 substep，而对外仍保持固定 Norton 接口与确定 deadline。

**(a) 未满足的需求。** 论文已经把执行时间和资源列为实时验证条件，却没有把“这一步为什么足够准确”纳入同一闭环。[pdf:E09][pdf:E10] 实际需求是同时知道 deadline 是否满足、误差来自哪里、何时固定 50 μs 已失效。

**(b) 研究价值。** 这会把 EMT 实时仿真从单一波形对照推进到“可证明的 accuracy–deadline co-design”：每个元件不只给 current injection，还给误差估计；调度器在预分配预算内选择局部解析更新、subcycling 或保守 companion。

**(c) 可借鉴工具。** 可借鉴 embedded real-time systems 的 worst-case execution-time 分析，以及 numerical ODE 中 embedded error estimator 的思想；这里只把它们作为候选连接，不声称本文或现有 EMT 工作已经实现。

**(d) 第一个可证伪实验。** 使用第 11 节的异步故障与轻阻尼非线性 RLC 工况，给定 50 μs macro-step 和固定 FPGA 预算。如果误差凭证无法可靠预测独立 reference 的首峰误差，或局部 substep 导致最坏执行时间越过 deadline，该想法立即被反驳。

**(e) 与本文的实质区别。** 本文固定步长、用同一步长 MATLAB 波形做 accuracy reference，并事后检查 timing。[pdf:E09][pdf:E12] 候选方法则把独立误差估计与最坏执行预算直接放进每一步求解决策；研究对象从“一个能实时运行的离散模型”变为“一个能解释何时可信、何时应局部加密且仍守 deadline 的实时求解系统”。

由于本任务禁止扩展检索，这只是从本文证据推出的候选研究方向，不声称 novelty。

---

## 证据图索引

- `[pdf:E01]`：PDF 物理页 1，标题、作者、DOI、EMT 背景与 Dommel 技术脉络。
- `[pdf:E02]`：PDF 物理页 2，文章目标、贡献、三种积分方法与 Figure 1。
- `[pdf:E03]`：PDF 物理页 3，梯形法性质、companion circuit 概念与 Figure 2 电感推导。
- `[pdf:E04]`：PDF 物理页 4，一般 RLC companion、Table 1 与线路模型说明。
- `[pdf:E05]`：PDF 物理页 5，同步机顺序求解背景与 Table 2 线路模型比较。
- `[pdf:E06]`：PDF 物理页 6，Figure 3 traveling-wave 线路模型与节点电压法。
- `[pdf:E07]`：PDF 物理页 7，compensation method、frequency shift 开端与 Figure 4 同步机 pipeline。
- `[pdf:E08]`：PDF 物理页 8，frequency shift、real-time/offline 定义与 Figure 5 励磁系统。
- `[pdf:E09]`：PDF 物理页 9，ML605 平台参数、50 μs 步长与三类验证标准。
- `[pdf:E10]`：PDF 物理页 10，Figure 7 compensation 完整步骤与 Table 3 实时判据。
- `[pdf:E11]`：PDF 物理页 11，Figure 8 四机 11 节点拓扑、schedule 与 MATLAB/FPGA 波形。
- `[pdf:E12]`：PDF 物理页 12，Table 4 资源、故障设置、误差、时序、标准差与结论。
