# An Automated Semi–symbolic State Equation Generation Method for Simulation of Power Electronic Systems

作者：Zhujun Yu；Zhengming Zhao；Bochen Shi；Yicheng Zhu；Jiahe Ju  
出处：IEEE Transactions on Power Electronics, Vol. 36, No. 4, pp. 3946–3956  
年份：2021  
DOI：10.1109/TPEL.2020.3025785  
Zotero key：XU9MUVXF（attachment：RXP24QFD）  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的不是“怎样积分一个已经写好的状态方程”，而是更靠前、也更容易成为大规模仿真瓶颈的问题：当电力电子开关不断改变电路拓扑时，怎样由开关状态自动、准确且低成本地生成或更新状态空间矩阵。电力电子系统同时包含连续状态和离散开关事件；传统 state-space 自动建模需要识别拓扑、选择独立状态量，再求解 KCL、KVL 与元件伏安约束。拓扑一变，这一流程就可能从头再做。对于含 \(n\) 个开关的系统，候选拓扑最多可达 \(2^n\)，所以预先生成并存储全部矩阵、或者每次事件都重新推导，都很快失去可行性。[pdf:E01][pdf:E02]

这项工作服务于作者先前的 discrete-state event-driven（DSED）仿真框架。该框架用 flexible adaptive（FA）变步长、变阶算法推进连续状态，并用 event-driven 机制定位离散事件；先前测试相对商业软件已有十倍到百倍加速，但还不能像通用 GUI 仿真软件那样让用户任意搭电路后自动形成网络方程。本文的价值因此很具体：如果矩阵生成仍然昂贵，快速积分器的收益会被开关事件触发的建模工作吃掉；如果能把它变成稀疏、局部的数值更新，DSED 才可能由研究原型走向通用仿真软件。[pdf:E01]

本文是 CPU 离线仿真算法论文，而不是 FPGA 实现论文。它没有报告 RTL/HLS 映射、片上存储、流水线、并行 PE、定点格式、资源占用、时钟频率或实时 deadline；对 EMT+FPGA 研究而言，它提供的是“事件后哪些矩阵项必须改、怎样把改动局部化”的算法结构，而不是已经验证的硬件执行结果。

## § 2 — 前人工作与不足

论文把既有路线分成几类，并说明各自为什么没有直接解决这个问题。

第一类是理想开关的 variable-topology state-space 方法。开通器件被表示为小电阻、短路或零值电压源，关断器件被表示为开路或零值电流源；它准确、稳定，也适合通用电路，但一只开关变位都可能迫使拓扑识别和约束求解重做，因此事件频繁时生成矩阵的成本很高。[pdf:E02]

第二类是 two-value resistor 模型，把开关替换成大/小电阻，以固定拓扑换取变量参数。这省去了拓扑重识别，却把困难转移给电阻值选择：ON/OFF 比例不当会使系统变 stiff，并带来收敛问题。第三类是 constant-conductance 或 transmission-line 类离散时间开关模型，它可以保持系统矩阵不变，但步长被电路参数约束为固定值，开关点还可能出现不符合物理的电压、电流尖峰。[pdf:E02]

第四类把开关影响表示成可变输入，包括平均模型和每步更新的受控源模型。它们通常依赖上一时间步的测量量或 duty ratio，因而引入一步延迟与离散误差；精度依赖步长及接口电容、电感，还会扩大输入/输出维度，使即使没有事件的普通积分步也承担额外计算量。作者并不是否定 switching function 思想，而是指出若把这些源保留为真正的仿真输入，就会付出上述代价。[pdf:E02]

本文与这些方法的分界是：仍以 ideal switched model 的 KCL/KVL 数值结果为目标，但把常见 switching leg 当作最小换流单元，只让开关状态出现在一个对角系数矩阵中；受控源只用于初始化时的符号推导，随后被代数消元，不作为时间推进中的额外输入。[pdf:E03][pdf:E04]

## § 3 — 重建作者的思考路径

以下是基于论文证据的逆向重建，不是作者逐字陈述。

第一步，研究者已经知道 DSED 的 FA 积分与 event-driven 定位能加快连续状态推进，但观察到任意用户电路仍缺少自动网络方程生成；因此剩余瓶颈不在积分公式本身，而在事件后的模型重建。[pdf:E01]

第二步，研究者比较各种开关模型后会发现一个两难：理想开关保真，却改变拓扑；固定矩阵或等效源模型便于计算，却可能引入 stiff、固定步长、一步延迟或非物理尖峰。于是合理目标不再是“永远固定完整矩阵”，而是“保留理想开关的方程，同时把拓扑变化压缩成少数可更新系数”。[pdf:E02]

第三步，实际功率变换器的开关并非任意独立组合，常以 half-bridge、三电平 diode-clamped leg 等换流单元协同工作。H-bridge 的电感方程已经显示，多个开关的影响可以压缩成 \(s_1-s_3\) 这样的 switching function；这提示把 leg 而非单只器件设为建模原子。[pdf:E02][pdf:E03]

第四步，只要把 leg 表示成受控电压源、受控电流源与可选导通电阻的组合，并把源系数写成开关状态函数，就可先按固定扩展拓扑生成一次方程，再用代数消元把这些辅助源消掉。若常见端口连接还使 \(F_s=0\)，更新进一步退化成由一个列向量和一个行向量构成的局部 outer product；这正好把“重新建模”变成“更新少数矩阵项”。[pdf:E04][pdf:E05]

## § 4 — 核心 Intuition

不要把每次开关事件都看成一张全新的电路；把常见 switching leg 看成带离散系数的固定接口，先把拓扑结构算一次，再让开关状态只改这些系数。[pdf:E03] 受控源经过代数消元后，最终 \(A,B,C,D\) 仍与 ideal switched model 数值等价，而常见拓扑下单个事件只需对少数矩阵元素做乘加更新。[pdf:E05] 方法奏效的根本原因不是近似更粗，而是电力电子换流单元的合法开关组合和稀疏连接结构给了更小的变化自由度。

## § 5 — 具体方法与完整 Pipeline

以一个由 half-bridge 构成的变换器为例，完整 pipeline 如下。

1. **确定建模原子。** 软件库把 half-bridge、三电平 diode-clamped leg、flying-capacitor leg 等预建为基本元件。以 half-bridge 为例，用一对受控电流源 \(J\)、受控电压源 \(E\) 和可选导通电阻 \(R_{\mathrm{on}}\) 表示 dc/ac 两侧耦合；系数由合法开关状态查表得到。论文假设同类 IGBT 与 diode 的 \(R_{\mathrm{on}}\) 相同，以保持该电阻常数。[pdf:E03][pdf:E04]
2. **初始化扩展方程。** 只在初始化时，把所有 leg 换成 switching-function model，把等效受控源 \(u_s\) 当作辅助输入，使用既有自动拓扑分析生成常矩阵 \(A_0,B_0,C_0,D_0,B_s,D_s,E,F,F_s\)。这是传统拓扑识别与矩阵运算真正发生的一次。[pdf:E04][pdf:E05]
3. **把离散状态压缩到 \(K_k\)。** 当前开关向量 \(sw_k\) 经状态表映射为对角系数矩阵 \(K_k\)。受控源满足 \(u_s=K_k y_s\)，而控制量 \(y_s\) 又是状态、原始输入和辅助源的线性组合。[pdf:E05]
4. **消去辅助源。** 联立两式得到 \(u_s=(I-K_kF_s)^{-1}K_k(Ex+Fu)\)，再代回扩展方程，直接得到当前 \(A_k,B_k,C_k,D_k\)。因此时间推进仍只看原始状态与输入，受控源不会扩张积分器的输入/输出维度。[pdf:E05]
5. **利用结构做局部更新。** 当 leg 的 dc 端通常并联电容或独立电压源、ac 端通常串联电感时，论文认为多数情形可令 \(F_s=0\)。若一次事件只改变 \(K_k\) 的少数对角元，就不重算整个矩阵，而只把对应 column–row outer product 加到旧矩阵上。Fig. 7 的运行流程是：输入 \(sw_k\)；初始化时生成并存储基矩阵和拓扑信息；之后从 cache 取出它们，再按 Eq. (9) 或 Eq. (12) 更新。[pdf:E05][pdf:E06]
6. **检查适用模式并回退。** half-bridge 只接受 10 或 01，三电平 diode-clamped leg 只接受 1100、0110 或 0011。若出现 buck discontinuous-conduction mode 中两只器件同时 OFF 等非法组合，软件回退到传统 ideal switched model，并为该新拓扑生成一组矩阵。[pdf:E06]

时间推进与多速率方面，论文复用 DSED 的 FA 变步长、变阶积分和 event-driven 事件定位；案例只报告最大步长 \(10^{-3}\,\mathrm{s}\) 与相对误差容限 \(10^{-4}\)，没有报告多速率分区、事件定位容限或最小步长。[pdf:E01][pdf:E07] 计算依赖方面，Eq. (12) 暴露了可并行的稀疏乘加结构，但本文的实现只是 C++ 单 CPU core；线程级并行、SIMD、GPU 与 FPGA 映射均未报告。[pdf:E08] 数值表示是浮点还是定点、矩阵稀疏存储格式、cache 数据结构和代码生成方式也未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文先把每个开关组合 \(k\) 下的 piecewise-linear 系统写成

\[
\dot{x}=A_kx+B_ku,\qquad y=C_kx+D_ku ,
\]

其中 \(x\) 是独立电容电压和电感电流组成的 \(n\times1\) 状态向量，\(u\) 是 \(m\times1\) 原始输入，\(y\) 是 \(l\times1\) 输出；\(A_k,B_k,C_k,D_k\) 随开关组合和器件分段变化。工程上，这就是本文最终必须快速得到的四组矩阵。[pdf:E04]

直观起点可由 H-bridge 看出。论文 Eq. (1) 写成

\[
\frac{d i_{L_O}}{dt}
=-\frac{R_O}{L_O}i_{L_O}+\frac{s_1-s_3}{L_O}u_E,\qquad
A=\left[-\frac{R_O}{L_O}\right],\quad
B=\left[\frac{s_1-s_3}{L_O}\right].
\]

物理参数 \(R_O,L_O\) 不变，离散模式只通过 \(s_1-s_3\) 进入 \(B\)。这就是 semi-symbolic 的最小例子：不是对所有参数做符号运算，只把开关函数保留为符号。[pdf:E02]

对一般系统，引入辅助受控源向量

\[
u_s=\begin{bmatrix}v_{E_s}\\i_{J_s}\end{bmatrix},
\]

扩展状态方程为

\[
\dot{x}=A_0x+B_0u+B_su_s,\qquad
y=C_0x+D_0u+D_su_s .
\]

开关表给出对角矩阵 \(K_k=K(sw_k)\)，使辅助源与其控制量满足

\[
u_s=K_k y_s,\qquad y_s=Ex+Fu+F_su_s .
\]

这里 \(K_k\) 承载全部离散开关信息，其余矩阵在初始化后保持常数。[pdf:E05]

消去 \(u_s\)：

\[
u_s=(I-K_kF_s)^{-1}K_k(Ex+Fu).
\]

代回后得到

\[
\begin{aligned}
A_k&=A_0+B_s(I-K_kF_s)^{-1}K_kE,\\
B_k&=B_0+B_s(I-K_kF_s)^{-1}K_kF,\\
C_k&=C_0+D_s(I-K_kF_s)^{-1}K_kE,\\
D_k&=D_0+D_s(I-K_kF_s)^{-1}K_kF .
\end{aligned}
\]

所以任一系统矩阵都可写成 \(M_k=f_M(K_k)=g_M(sw_k)\)。论文的准确性论证是：没有估计或一步延迟，消元前后的 KCL/KVL 与原电路相同，因此所得数值矩阵与 ideal switched model 相同；这是一种代数等价变换，不是平均化近似。[pdf:E05]

主要成本在 \((I-K_kF_s)^{-1}\)。若常见端口结构使 \(F_s=0\)，则

\[
A_k=A_0+B_sK_kE.
\]

若只有 \(K_k\) 的第一项由 \(k_{11}\) 变为 \(k_{11}+\Delta k_{11}\)，则

\[
\Delta A_k
=B_s
\begin{bmatrix}
\Delta k_{11}&0\\
0&0_{(p-1)\times(p-1)}
\end{bmatrix}E
=\Delta k_{11}b_{s1}e_1^\mathsf{T}.
\]

\(b_{s1}\) 是 \(B_s\) 的第一列，\(e_1^\mathsf{T}\) 是 \(E\) 的第一行。也就是说，一个离散系数的改变只产生一个 rank-1 outer product；若 \(e_1^\mathsf{T}\) 本身稀疏，实际只需更新它非零位置对应的矩阵项。[pdf:E05] 论文没有给出该更新的渐近复杂度定理、数值条件数界或有限精度误差界。

实验误差用 Eq. (13)

\[
\mathrm{Error}_{\mathrm{rel}}
=\frac{\lVert y_{\mathrm{sim}}-y_{\mathrm{ref}}\rVert_2}
{\lVert y_{\mathrm{ref}}\rVert_2}
\]

衡量，是整段波形向量相对商业软件参考波形的二范数误差，而不是单点峰值误差。[pdf:E07]

## § 7 — 实验设计与结论

**问题一：在大规模、多开关系统中，semi-symbolic 更新是否保持与传统 ideal switched model 相同的结果？**  
实验：作者选择一个 2 MW、四端口 SST：10 kV HVAC、10 kV HVDC、380 V 三相 LVAC 和 \(\pm375\) V LVDC。单台 SST 含 576 个开关器件，其中 32 个 IGBT、544 个 SiC MOSFET；有 87 个 submodule、72 个 high-frequency transformer，最高调制频率 20 kHz。案例一模拟单台 SST 的 0.15 s 负载变化；案例二模拟两台 SST 的 0.1 s master/slave 功率交换。DSED 分别使用传统矩阵生成和本文方法，并与一个未具名的快速商业软件比较；三者最大步长均为 \(10^{-3}\,\mathrm{s}\)，相对容限均为 \(10^{-4}\)。[pdf:E07]  
答案：Fig. 10 与 Fig. 11 显示三种方法在毫秒级端口波形和微秒级 20 kHz HFT switching ripple 上重合。相对商业软件，Table IV 中单 SST 四个测量量的相对误差为 \(3.87\times10^{-5}\)、\(6.85\times10^{-4}\)、\(1.34\times10^{-5}\)、\(2.18\times10^{-5}\)；双 SST 四个测量量为 \(5.89\times10^{-4}\)、\(5.96\times10^{-5}\)、\(5.65\times10^{-4}\)、\(2.60\times10^{-4}\)。论文据此支持“没有因 semi-symbolic 建模额外牺牲精度”，但这些数字仍包含不同仿真器的积分与事件定位差异，不能单独当作矩阵逐元素相等的证明。[pdf:E08][pdf:E09]

**问题二：加速来自 DSED 积分器，还是本文的矩阵更新本身也有独立贡献？**  
实验：作者用 C++ 实现两个除矩阵生成/更新外完全相同的 DSED 版本；传统版本在事件后生成新矩阵或从 cache 取出旧矩阵，本文版本每次按 switching function 更新且不存全部模式。两 SST 案例扩大到 1152 个开关、576 个基本 switching leg、365 个独立状态和 256 个输出。全部测试运行于同一台机器的一个 3.00 GHz Intel “Xeno Gold 6316” CPU core、512 GB memory；这是论文原文的平台标注。[pdf:E08]  
答案：单 SST 的 0.15 s 仿真，本文 DSED 用 28 s，传统 DSED 用 23 min，商业软件用 5 h 24 min；归一化 CPU 时间为 1、49.2、694.3。双 SST 的 0.1 s 仿真分别用 1 min 50 s、3 h 28 min、38 h 22 min；归一化为 1、113.5、1255.6。论文因此把总加速概括为约 700 倍和 1200 倍，把本文矩阵方法相对传统 DSED 的独立贡献概括为约 50 倍和 110 倍。[pdf:E09][pdf:E10]

**问题三：结果能否外推到实时 EMT 或 FPGA？**  
实验：未做。论文只报告离线 CPU wall-clock time，没有实时步长逐步 deadline、最坏事件密度、延迟抖动、memory bandwidth、FPGA 资源或硬件在环结果。[pdf:E08][pdf:E09]  
答案：不能由本文证明实时性，也不能把 700/1200 倍直接外推到 FPGA。它证明的是特定正常模式 SST 案例中，矩阵更新算法在 CPU 上显著减少总仿真时间。

## § 8 — Take-aways

**5 句话。**  
1. 论文把频繁拓扑重建改写成 switching-state coefficient 更新，同时保持目标矩阵与 ideal switched model 数值等价。[pdf:E05]  
2. 核心抽象是把 basic switching leg 而非单只开关当作最小建模单元。[pdf:E03]  
3. 受控源只服务于初始化推导，代数消元后不会成为积分器的额外输入。[pdf:E04][pdf:E05]  
4. 在 \(F_s=0\) 且少数开关变化时，事件更新可以缩成稀疏 outer product，而不重做拓扑识别。[pdf:E05]  
5. 两个 2 MW SST CPU 案例给出很大加速，但没有覆盖异常开关模式、广泛任意拓扑、实时执行或 FPGA 映射。[pdf:E06][pdf:E09]

**3 句话。**  
它用换流单元结构把“组合爆炸的拓扑”压缩成“少数离散系数”。正常模式下，这种压缩不靠平均化或上一步测量，因此保留 ideal switched model 的方程。真正决定通用性的不是 Eq. (9) 能否计算，而是合法 switching-function model 能覆盖多少运行时间、回退传统建模有多频繁。[pdf:E05][pdf:E06]

**1 句话。**  
这篇论文最重要的贡献，是证明大规模电力电子事件后的状态矩阵可以在不引入建模近似的前提下做结构化局部更新，而不是每次重新“理解”整张电路。[pdf:E05]

## § 9 — 最脆弱的假设

最脆弱的假设是：**绝大多数实际运行事件都落在预建 switching leg 的合法组合内，因此昂贵的 traditional-model fallback 足够少。** 这是速度贡献能否成立的总开关。half-bridge 必须是 10/01，三电平 diode-clamped leg 必须是 1100/0110/0011；buck 的 DCM 两器件同时 OFF 已被作者明确列为不适用情形。遇到不适用状态时，算法要回退 ideal switched model 并生成新矩阵；如果这种状态在一个工况中频繁出现，核心计算优势会系统性消失。[pdf:E06]

这个假设在实际中可能因 DCM、dead time、换流重叠、保护动作、故障、器件非理想、用户用离散器件搭建自定义拓扑而失效。论文还限制为以 voltage-source converter 为主：具有 current-source behavior 的元件不能与等效电流源串联，具有 voltage-source behavior 的元件不能与等效电压源并联。[pdf:E06]

论文为该假设提供的证据是两种 SST 正常运行模式中的 576/1152 开关案例，且这些系统由大量规则 H-bridge 模块构成。[pdf:E07][pdf:E08] 它没有报告 fallback 次数、非法组合占比、dead-time/DCM/fault 工况、用户自定义离散开关电路，也没有比较“含回退的端到端时间”。因此“正常模块化 SST 上有效”有实验证据，“任意 power electronic system 普遍有效”则证据不足。

## § 10 — 最小复现实验

一周内最有价值的复现不是重做整台 2 MW SST，而是验证“代数等价 + 局部更新成本”这两个核心 claim。

1. 用 Python/NumPy 或 C++ 搭建参数化的 \(N\) 个 half-bridge 串并联 RLC 网络，取 \(N=2,8,32,64\)。为每个规模自动生成传统 ideal-switch nodal/state-space 方程，同时按论文 Eq. (3)–(12) 生成 semi-symbolic 方程。
2. 生成同一组合法 10/01 switching event trace；每个事件只改变一个 leg，另加一组多个 leg 同时变化的压力轨迹。用相同初值、输入和固定的小步长积分，以排除两个自适应求解器带来的混杂。
3. 每个事件后测量四项：\(A,B,C,D\) 的最大逐元素差；一步状态导数差；矩阵更新时间；随 \(N\) 和同时变位数增长的 scaling。另记录实际被改写的矩阵元素数。
4. 再注入 00 dead-time/DCM 状态，显式实现论文规定的 fallback，并扫描非法状态占全部事件的 0%、1%、10%、50%。测量含回退的端到端加速，而不是只测快路径。

若所有合法事件下矩阵差和状态导数差接近所用浮点精度，且单开关更新成本随被影响的稀疏项而非全矩阵规模增长，就支持核心 claim。若合法事件下出现稳定的矩阵不一致，或者很低的 fallback 比例就让端到端加速消失，就反驳其准确性或工程收益。复现不需要 FPGA；若后续做 FPGA，首先应把 Eq. (12) 的稀疏 outer-product kernel 与事件索引表单独综合，而不能拿本文 CPU 加速比当硬件基线。

## § 11 — 最强反例设计

最强反例应选择一个“异常组合不是偶发，而是正常工作机制”的系统：轻载 DCM buck/多相 converter，加入真实 dead time、diode 自然续流、换流重叠，并让负载在 CCM 与 DCM 间频繁跨越。再加入一个 current-source converter 支路，使部分端口违反作者对等效源串并联关系的要求。[pdf:E06]

对同一 switching trace 运行三种实现：全程 traditional ideal switched model；带论文所述合法性检查与全局回退的 semi-symbolic model；以及只对失效 leg 局部回退、其余 leg 继续 semi-symbolic 更新的增强对照。测量波形误差、每秒 fallback 次数、矩阵生成 CPU 时间、最坏单事件延迟和内存占用，并按 DCM 占空、dead time 和同时换流数做二维扫描。

如果原方法在物理上常见的 DCM/dead-time 区域必须高频回退，导致速度逼近传统方法，甚至因模式检查与 cache 管理更慢，那么“适合任意大规模 power electronic systems”的强解释就被推翻；剩下的贡献应收缩为“适合合法模式高度规则、主要由预建 voltage-source switching legs 组成的系统”。若即使 50% 事件触发非标准模式仍保持矩阵等价和显著加速，才说明最脆弱假设比论文证据暗示的更稳健。

## § 12 — Follow-up Research Idea

电力电子与控制领域通常不会只因算法新颖就认可高影响贡献；更看重严格的数值正确性、异常工况覆盖、可复现的大规模实验、实时/硬件可实现性，以及对真实设计与验证流程的价值。基于本文最脆弱假设，一个非增量候选方向是：**面向 hybrid converter 的约束认证式 switching-unit compiler**。它不要求用户先从库中选对 half-bridge/three-level leg，而是从任意电路图、器件方向和开关约束自动推断局部换流单元，为每个单元生成“合法模式语言、semi-symbolic update kernel、适用性证明条件和局部 fallback kernel”；运行时只让失效单元回退，而不是重建全系统。

（a）驱动需求是本文方法的速度依赖预建 leg 与正常模式，但实际 EMT 场景包含 DCM、dead time、故障和用户自定义拓扑。[pdf:E06]  
（b）它可能产生本领域认可的价值，因为研究目标从“已知拓扑的快矩阵更新”改变为“任意混合拓扑中可证明正确、可局部降级、可给出最坏事件成本的自动编译”，同时直接连接通用 GUI 仿真与实时执行。  
（c）可借鉴相邻领域的 program synthesis、static analysis、hybrid automata reachability，以及 sparse compiler 的 dependency graph 和 kernel scheduling；对 FPGA，可把每个已认证单元编译成有界延迟的稀疏乘加 kernel 和事件路由表。  
（d）第一个证伪实验是用含 CCM/DCM、dead time、故障和 voltage-/current-source converter 混合支路的公开拓扑集，比较传统全局重建、本文全局 fallback 与所提局部 compiler：若无法对每个模式保持矩阵/残差一致，或局部回退不能显著降低最坏事件延迟，该想法即失败。  
（e）与本文的实质区别在于：本文假定 switching leg 类型和状态表已经给定，且失败时回退生成整组矩阵；候选方法把“自动发现建模单元、证明适用模式、限制回退影响域和生成可调度 kernel”本身作为研究对象。

这个方向只由本文证据和相邻方法线索推导，未做外部相关工作检索，因此明确标为候选想法，不声称 novelty。
