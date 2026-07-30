# High-Throughput FPGA Implementation of Matrix Inversion for Control Systems

作者：Xiao-Wei Zhang、Lei Zuo、Ming Li、Jian-Xin Guo  
出处：IEEE Transactions on Industrial Electronics, Vol. 68, No. 7, pp. 6205-6216  
年份：2021  
DOI：10.1109/TIE.2020.2994865  
Zotero key：C6M2RQVP  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个很具体的工程矛盾：控制与雷达系统有时无法绕开矩阵求逆，但高维矩阵求逆既消耗 FPGA 上稀缺的 DSP、RAM 和逻辑资源，又容易受舍入误差与病态条件影响；与此同时，在线控制要求结果在固定时限内持续产出。作者把“实时性”和“数值稳定性”并列为设计目标，并把应用范围指向 MPC、功率系统、网络、无线通信和相控阵雷达等需要在线求解优化或线性方程的场景。论文正式处理的数学对象是非奇异 Hermitian 矩阵，并在摘要中把 FPGA 上的 LDL 分解、上三角矩阵求逆和矩阵乘法作为完整求逆链路。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，不只是因为一次求逆很慢，而是因为它处在控制回路的关键路径上：延迟超限会使控制量过期，数值误差则会直接污染后续的权值、状态估计或优化结果。论文最终用一个 72 通道相控阵雷达的 LCMV 自适应波束形成链路做系统级验证；该链路规定数据延迟不超过 2 ms、器件延迟不超过 3.5 ms，因此算法、数值表示和硬件调度必须共同满足约束，而不能只在 MATLAB 中得到一个正确逆矩阵。[pdf:E10]（PDF 物理页 10，Table IV、Fig. 10 与 Table V）

需要限定的是：这不是一篇 EMT 实时仿真器论文，也没有建立开关电力电子系统的离散模型。它提供的是可被控制、雷达或仿真系统调用的矩阵求逆核；它对上层闭环稳定性、EMT 节点方程装配和控制采样策略的价值，属于潜在用途，而不是本文已经验证的结果。

## § 2 — 前人工作与不足

论文把既有求逆路线分为三类。按定义或伴随矩阵直接求逆适合 2×2、3×3 等小矩阵，但维度增大后运算量和舍入误差传播都变得不利；迭代方法需要初值和逐次误差更新，不容易给出适合实时硬件的固定计算流程；Cholesky、LDL、QR 等分解法通常更适合工程数值计算，但分解后的三角矩阵若仍用回代或逐方程求解，依赖链较长，难以充分并行。论文还指出，Gaussian-Jordan 类大规模实现计算负担重且数值稳定性不足，Neumann 展开只适合带状矩阵。[pdf:E01]（PDF 物理页 1，Section I）

作者特别针对两个接近的基线。其一是 Cholesky 求逆工作 [11]：它已利用三角矩阵与其逆的对角元素关系来省掉部分中间计算，但论文认为该工作没有给出推导，也没有继续利用第一条超对角线的结构。其二是面向 FPGA 预测控制的 SPMI [16]：它直接套用分块矩阵求逆，运行时间短，却没有通过矩阵分解建立稳定性基础，且原工作没有讨论高维、病态情况下的数值行为。论文还把 [17] 的 EMT 矩阵求逆技术描述为依赖应用中的常量中间矩阵，因而不适合一般矩阵。[pdf:E01]（PDF 物理页 1，Section I）

这些“前人不足”是论文原文的相关工作叙述，不等于独立完成的 novelty 检索。尤其是“LDL 的 condition number 更小”“整体资源最少”等措辞，需要结合后文实验定义和逐项资源表审慎理解，不能仅凭作者概括扩大为普遍结论。

## § 3 — 重建作者的思考路径

下面是基于论文证据重建的合理推断，不是作者逐句写出的研究日志。

第一步，研究者会先排除难以形成确定时序的路线。实时 FPGA 更偏好固定次数、规则访存和可流水化的计算，因此从分解法出发比从迭代收敛出发更自然。对 Hermitian 矩阵采用 \(A=R^{H}DR\) 后，外积形式的 LDL 更新把剩余子矩阵按行列递减，天然暴露了向量并行和 RAM 流式读写机会。[pdf:E02]（PDF 物理页 2，Section II-A，Eq. (1)-(4)）

第二步，研究者会寻找“数学上已知、硬件上却还在重复算”的量。LDL 产生的是单位对角上三角矩阵 \(R\)：其逆的对角元素仍为 1，而第一条超对角线只需改变符号，即 \(\hat r_{i,i+1}=-r_{i,i+1}\)。这意味着一部分乘除法可以被常量和符号翻转取代，剩余真正需要计算的非零元素数为 \(0.5(N^2-3N+2)\)。[pdf:E03]（PDF 物理页 3，Eq. (10)-(13) 与 Fig. 1）

第三步，为避免回代的长串行依赖，研究者把 \(R\) 沿对角线切成 2×2 起步的块，并递归使用
\[
R_B^{-1}=
\begin{bmatrix}
C^{-1} & -C^{-1}EG^{-1}\\
0 & G^{-1}
\end{bmatrix}.
\]
已经得到的 \(C^{-1}\) 被复用，单位对角与符号关系继续删减块乘法中的冗余项，最后再做 \(R^{-1}D^{-1}R^{-H}\)。这条路径保留了分解法的结构，同时把求逆改写为规则块运算。[pdf:E04]（PDF 物理页 4，Eq. (14)-(19)）

第四步，研究者把三个数学阶段变成三个可重叠的硬件阶段：LDL 分解、三角逆、三矩阵乘法分别由 RAM、地址/FSM 和计算单元驱动；当前矩阵的前几行分解结果一出现，就启动后级，而不是等整张矩阵完全分解后再开始。Fig. 4 所示的 tristage 架构解释了论文为何同时报告单次 device latency 和高于其倒数的流水 throughput。[pdf:E07]（PDF 物理页 7，Fig. 4 与 Section III-D）

## § 4 — 核心 Intuition

核心 intuition 是：不要把 FPGA 当作顺序处理器去照搬回代，而要先用 LDL 把问题变成单位对角上三角矩阵，再把已知的“对角恒为 1、第一超对角线只需反号”直接固化为硬件结构。随后用递归分块把剩余依赖改造成可流水的矩阵块运算，使数值结构、运算删减和硬件并行来自同一个分解。代价是该优势依赖矩阵确实适合无主元的 LDL 流程，并且输入分布与单精度动态范围足够温和。

## § 5 — 具体方法与完整 Pipeline

以论文的 72×72 complex Hermitian 矩阵为真实例子，完整 pipeline 如下。

1. **输入与问题变换。** 正式输入是非奇异 Hermitian 矩阵 \(A\)。若原问题给出一般方阵 \(B\)，论文建议先构造 \(A=BB^H\)，求得 \(A^{-1}\) 后再用 \(B^{-1}=B^HA^{-1}\) 恢复一般矩阵的逆。[pdf:E02]（PDF 物理页 2，Section I 末与 Section II 开头）这一扩展相当于 normal-equations 路线，会平方 2-norm condition number；论文没有实测这条一般矩阵路径，所以不能把 Hermitian 实验直接外推到任意 \(B\)。
2. **外积 LDL 分解。** 将 \(A\) 写成 \(R^HDR\)，其中 \(R\) 是单位对角上三角矩阵，\(D\) 是对角矩阵。每一步取当前 \(a_{ii}\) 为 \(d_{ii}\)，计算列向量比例 \(s=b/a_{ii}\)，再以 \(A_{\text{new}}=A_{\text{old}}-bs^H\) 更新余下子矩阵；若 \(a_{ii}\) 为 0 或在硬件精度下近似 0，则置 error flag 并退出。[pdf:E05]（PDF 物理页 5，Algorithm 1）
3. **递归三角求逆。** 沿单位对角线把 \(R\) 划分为小块，从 2×2 块开始递归组合。对角元素直接写 1，第一超对角元素用 LUT 完成 sign-bit inversion，其余块通过 \(-C^{-1}EG^{-1}\) 计算。论文实现只计算 \(0.5(N^2-3N+2)\) 个仍未知的非零元素。[pdf:E03]（PDF 物理页 3，Eq. (12)-(13)）
4. **恢复完整逆矩阵。** 先算 \(T=R^{-1}D^{-1}\)，再算 \(A^{-1}=TR^{-H}\)。这一步没有被论文进一步代数化简，仍是主要矩阵乘法负担。[pdf:E04]（PDF 物理页 4，Eq. (19)）
5. **FPGA 数据与控制映射。** LDL 路径使用 RAM0 接收输入，RAM1 保存对角中间量，RAM2 保存不含单位对角的上三角非零元素；内部 RAM 读写字宽可达 4608 bit，通过 parallel load 让一行向量在一个周期进入 Computation0。三角逆阶段从 RAM2 读、向 RAM3 写，Address/FSM 生成地址和阶段使能；Hermitian 对称性使 RAM1 只缓存半矩阵，符号反转用 LUT 而不是 DSP。[pdf:E06]（PDF 物理页 6，Fig. 2、Fig. 3 与 Section III-B/C）
6. **流水与存储。** 三矩阵乘法再使用 RAM4 等缓存；论文称全设计共用六个 dual-port RAM，并通过对称存储与 zero padding 节省空间。三阶段硬件允许分解、三角逆和乘法交叠，前两阶段推进到允许位置后即可接收下一矩阵，因此 throughput 不等同于单次 latency 的倒数。[pdf:E07]（PDF 物理页 7，Fig. 4 与 Remark）
7. **数值格式与平台。** 作者明确建议用 IEEE-754 single floating point 而非 fixed point；对 Eq. (20) 的近奇异 2×2 例子，24-bit fixed-point 给出明显错误结果，而 single floating-point 给出约 \(111.6672,-111.7780,111.8899\) 的逆元素。[pdf:E05]（PDF 物理页 5，Eq. (20)-(21)）硬件比较采用 Xilinx floating-point operator v7.1、Vivado 2016.02 和 XC7VX690T；板卡为 open VPX、含三片 XC7VX690T 和每片 2 GB DDR3，方法比较表针对 72×72 complex 矩阵。[pdf:E07]（PDF 物理页 7，Fig. 5）[pdf:E08]（PDF 物理页 8，Section IV-C）

论文未报告 EMT 的节点导纳装配、开关事件处理、time stepping、multi-rate 调度、控制离散化或与外部 plant 的同步机制；也没有给出 RTL 源码、完整逐周期时序表、片上/片外带宽上界和综合约束文件。这些内容不能从“用于 control systems”的题名中补写出来。

## § 6 — 核心数学推导（无形式化数学则跳过）

核心数学分成三层。

**第一层：LDL 的外积递减。** 对当前矩阵
\[
A_N=
\begin{bmatrix}
a_{11} & b^H\\
b & A_{N-1}
\end{bmatrix},
\]
令
\[
A_N=
\begin{bmatrix}
1&0\\
s&R_{N-1}
\end{bmatrix}
\begin{bmatrix}
d_{11}&0\\
0&D_{N-1}
\end{bmatrix}
\begin{bmatrix}
1&s^H\\
0&R_{N-1}
\end{bmatrix}.
\]
逐块相等得到 \(d_{11}=a_{11}\)、\(b=d_{11}s\) 和
\[
A_{N-1}=d_{11}ss^H+R_{N-1}^HD_{N-1}R_{N-1}.
\]
因此每一步只需计算
\[
s=b/a_{11},\qquad
A_{N-1,\mathrm{new}}=A_{N-1}-a_{11}ss^H=A_{N-1}-bs^H,
\]
然后对缩小一阶的 \(A_{N-1,\mathrm{new}}\) 重复。工程 intuition 是把一个 \(N\times N\) 分解变成连续的 rank-1 trailing-submatrix update；这些更新容易按向量并行，但 \(a_{11}\) 也是无主元流程的数值关口。[pdf:E02]（PDF 物理页 2，Eq. (1)-(4)）

**第二层：单位上三角矩阵的免费元素。** 一般上三角矩阵的逆仍是上三角矩阵，且 \(\hat r_{ii}=1/r_{ii}\)。LDL 中的 \(R\) 被归一为单位对角，所以 \(\hat r_{ii}=1\)；对第一超对角线，余子式展开给出
\[
\hat r_{i,i+1}=-r_{i,i+1}.
\]
因此硬件无需为这些元素调用除法器或乘法器，只需常量写入和符号位翻转；剩余未知上三角元素数为 \(0.5(N^2-3N+2)\)。[pdf:E03]（PDF 物理页 3，Eq. (9)-(13)）

**第三层：递归块合并。** 设
\[
R_B=
\begin{bmatrix}
C&E\\
0&G
\end{bmatrix},
\]
则
\[
R_B^{-1}=
\begin{bmatrix}
C^{-1}&-C^{-1}EG^{-1}\\
0&G^{-1}
\end{bmatrix}.
\]
递归中 \(C^{-1}\) 是已完成结果，\(G\) 从 2×2 单位上三角块开始，其逆由一次符号翻转得到。论文进一步利用 \(-C^{-1}\) 中的 0、-1 和已有元素，省去 Eq. (18b) 的第一列冗余计算；最终
\[
A^{-1}=(R^HDR)^{-1}=R^{-1}D^{-1}R^{-H}.
\]
[pdf:E04]（PDF 物理页 4，Eq. (15)-(19)）

从 operation count 看，论文给出的本方法 Add/Sub 为 \(0.5(N^3-3N)\)，Multiply 为 \(0.25(2N^3+N^2-2N)\)，Division 为 \(2N\)，Square Root 为 0。它相对 Cholesky 减少了部分加乘和全部平方根，但除法数从 \(N\) 增到 \(2N\)；相对 SPMI，除法也更多。因此“总运算最少”依赖不同操作在具体 FPGA 上的代价，不能只把四列符号式无权相加。[pdf:E05]（PDF 物理页 5，Table I）

## § 7 — 实验设计与结论

**问题一：算法结构是否减少运算时间？ → 实验：** 作者在 Intel Core i7-4600U 上用循环形式实现 Cholesky、SPMI、QR 和本方法，对 100,000 个随机非奇异 Hermitian 矩阵取平均时间，不做 multicore 优化。**答案：** 72×72 时四者分别为 34.991、5.102、7.369、5.093 ms；本方法仅比 SPMI 少 0.009 ms。作者据此主要把 CPU 结果解释为 operation count 的代理，而不是 FPGA 性能结论，并指出符号翻转在 FPGA 上可用单周期 NOR/LUT 实现。[pdf:E08]（PDF 物理页 8，Table II 与其下正文）

**问题二：数值稳定性是否优于基线？ → 实验：** 对 1,000 个 32×32 RANDN 随机矩阵，以及 IPIX sea clutter 数据，比较四种方法“处理后”的 condition number；随后在 FPGA 上处理 1,000 个 72×72 随机 Hermitian 矩阵和 IPIX 数据，用
\[
c=\lVert I-AA^{-1}\rVert_2
\]
作为逆矩阵残差指标。**答案：** 作者报告 LDL 路线在 Fig. 6、Fig. 7 中 condition number 最小，在 Fig. 8、Fig. 9 中 matrix two-norm error 最小，Cholesky 的误差表现与 LDL 接近，QR 的误差幅度最高。[pdf:E08]（PDF 物理页 8，Fig. 6、Fig. 7）[pdf:E09]（PDF 物理页 9，Fig. 8、Fig. 9 与 Eq. (23)）

这里有一个重要证据缺口：同一输入矩阵的数学 condition number 不应随求逆算法改变，论文没有清楚定义 Fig. 6、Fig. 7 究竟对哪个经过有限精度变换后的矩阵求 condition number。因此，这两图能复述为作者报告的现象，却不足以单独证明算法本身更稳定。相比之下，\( \lVert I-AA^{-1}\rVert_2 \) 是直接检查求逆结果的残差，但论文只给曲线，没有均值、最大值、分位数或统计区间。

**问题三：一片 FPGA 上的资源、频率、latency 和 throughput 是否更好？ → 实验：** 使用 Verilog、Xilinx floating-point operator v7.1、Vivado 2016.02，在 XC7VX690T 上实现四种 72×72 complex matrix inversion。**答案：** 本方法报告 250,681 LUT、5,924 LUTRAM、834 BRAM、1,839 DSP48、2,359.39 μs device latency、589.1 inversions/s throughput 和 250 MHz \(f_{\max}\)。作为对照，Cholesky 的 latency/throughput 为 4,703.95 μs/418.7 inversions/s，SPMI 为 3,074.82 μs/315.2 inversions/s，QR 为 3,947.05 μs/253.4 inversions/s。[pdf:E08]（PDF 物理页 8，Table III）

逐项看，本方法的 DSP48 和 LUTRAM 是表中最低，latency 最小、throughput 与 \(f_{\max}\) 最高；但 LUT 仍高于 QR 的 230,161，BRAM 仍高于 SPMI 的 636。因此更准确的结论是“在该实现与 72×72 负载下取得较好的资源-速度组合”，不是所有资源维度都最少。论文未报告 post-route timing margin、最坏输入相关 latency、功耗、DDR/SRIO 带宽占用或跨器件复现。

**问题四：能否满足真实雷达控制链的 deadline？ → 实验：** 在 microwave chamber 中设置 72 通道、512 snapshots、2 个干扰源，干扰角 \([-20^\circ,-15^\circ]\)、JNR \([40,65]\) dB，以 72×72 LCMV 协方差矩阵执行 diagonal loading 和求逆；系统要求 data latency ≤2 ms、device latency ≤3.5 ms。**答案：** 单片 XC7VX690T 上完整 LCMV 报告 data latency 1,668.98 μs、device latency 3,099.91 μs、200 MHz、32-bit word length，满足给定门限；资源占用达到 2,439 DSP48（78.86%）、1,034 BRAM（70.34%）和 301,183 LUT（69.53%）。MATLAB 与 FPGA 天线方向图在两个干扰角附近形成相近抑制，作者据此判断工程误差可接受。[pdf:E10]（PDF 物理页 10，Table IV、Fig. 10、Fig. 11 与 Table V）

**问题五：应用输出误差有多大？ → 实验：** 比较 MATLAB 与 FPGA 的方向图，并分解逆矩阵实部、虚部的 absolute/relative error。**答案：** 作者正文称 absolute error 幅值在 \(10^{-4}\) 量级，并据此宣布阵列天线控制问题得到解决。[pdf:E11]（PDF 物理页 11，Section V 与 Conclusion）但 Fig. 12 的子图 caption 顺序、图内 y-axis 标注和正文对 absolute/relative error 的叙述彼此不完全一致；因此不宜把 \(10^{-4}\) 当作无歧义的全局误差上界。[pdf:E10]（PDF 物理页 10，Fig. 12）

结论的可外推范围很窄：证据支持特定 FPGA、single precision、72×72 complex 矩阵和一个 LCMV 雷达工况下的实现；Conclusion 还称已做过 54×54、64×64、128×128 单片实现，以及理论上可跨 FPGA 扩展，但没有给这些尺寸的表格、误差、吞吐或通信开销，因而只能视为作者陈述，不能当作本文实验已闭合的 scalability 证据。[pdf:E11]（PDF 物理页 11，Section VI）

## § 8 — Take-aways

**5 句话。** 论文把 Hermitian matrix inversion 拆成外积 LDL、递归单位上三角求逆和三矩阵乘法。它的关键优化不是新型乘法器，而是把单位对角和第一超对角线的已知关系直接变成常量写入与符号位翻转。三阶段 RAM/FSM/PE 架构让计算发生重叠，在 XC7VX690T 的 72×72 实现中报告 2,359.39 μs device latency 和 589.1 inversions/s throughput。[pdf:E08] 真实 LCMV 雷达实验达到 1,668.98 μs data latency 和 3,099.91 μs device latency，满足论文给定门限。[pdf:E10] 最需要保留的疑问是无主元 LDL 的输入适用范围、condition-number 实验定义，以及未公开的最坏情况误差与时序证据。

**3 句话。** 数学结构删减、递归分块和硬件流水在本文中是同一个设计，而不是三个独立优化。给定 72×72 Hermitian、single precision 和 XC7VX690T，论文展示了有竞争力的 latency/throughput/资源组合及一个雷达闭环关键路径实例。它尚未证明对任意非奇异 Hermitian、一般非-Hermitian、跨 FPGA 扩展或 EMT 实时仿真都同样稳定有效。

**1 句话。** 这篇论文最有价值的结论是：先把单位上三角矩阵中“本来就知道”的逆元素从运算图里删掉，再围绕剩余块依赖设计流水，能把矩阵求逆做成高吞吐 FPGA 核，但适用矩阵和误差边界必须单独守住。

## § 9 — 最脆弱的假设

最脆弱的假设是：输入虽然被表述为“非奇异 Hermitian”，但其 leading pivots 必须在 single precision 下始终远离 0，使不带 pivoting 的标量 LDL 可以安全推进。Algorithm 1 遇到 \(a_{ii}=0\) 或近似 0 就置 error flag 并退出，没有 row/column pivoting、2×2 pivot、regularization 或 QR fallback。[pdf:E05]（PDF 物理页 5，Algorithm 1）

这个假设一旦不成立，核心贡献不是“精度稍差”，而是整条实时流水直接停止，或者在小 pivot 上放大误差。最小数学反例是
\[
A=
\begin{bmatrix}
0&1\\
1&0
\end{bmatrix},
\]
它是非奇异 Hermitian，特征值为 \(1,-1\)，但第一步 \(a_{11}=0\)，本文硬件会报错退出；这说明论文的实际可用域比题面“非奇异 Hermitian”更接近具有安全主元序列的 positive-definite/benign matrices。论文用 Hilbert、随机矩阵和 sea clutter 说明若干输入上的表现，却没有按最小 pivot、inertia 或 condition number 分层报告成功率，也没有证明 error flag 在控制 deadline 内如何被系统接管。

对于一般方阵 \(B\)，作者的 \(A=BB^H\) 路线还会把 2-norm condition number 从 \(\kappa(B)\) 放大到 \(\kappa(B)^2\)。这进一步削弱了“先转成 Hermitian 就容易解决一般矩阵”的稳定性直觉；论文没有对该路径做硬件误差实验。[pdf:E02]（PDF 物理页 2，Section I）

## § 10 — 最小复现实验

一周内最值得复现的不是完整雷达板卡，而是“结构删减是否在 deadline 不变的条件下保持残差”这一核心 claim。

数据可生成三组 72×72 single-precision 矩阵，每组至少 1,000 个：第一组为 \(A=XX^H+\alpha I\) 的 well-conditioned positive-definite 矩阵；第二组逐步减小 \(\alpha\)，覆盖 \(10^2\) 到 \(10^{10}\) 的 condition-number 区间；第三组通过随机正交变换构造 indefinite Hermitian，并刻意排列出很小或为 0 的 leading pivots。实现两个版本：论文的无主元 outer-product LDL + recursive triangular inverse，以及成熟库中的 pivoted LDL 或 QR 参考；若无同型号 FPGA，可先用 Vivado/RTL 仿真测 cycle count，再用 CPU double precision 只作为 truth oracle。

每个样本记录四项：是否触发 error flag、\(\lVert I-AA^{-1}\rVert_2\)、相对 forward error、从输入有效到结果有效的 cycle count。支持 claim 的最低标准是：在预先声明的 positive-definite condition-number 范围内，论文结构的残差不劣于参考实现一个数量级，且 cycle count 固定并显著低于非结构化版本；反驳 claim 的结果是 benign 范围内频繁退出、残差随 pivot 顺序而剧烈变化，或省掉的运算没有转化为 post-route latency/throughput 优势。这样无需复现天线、DDR3 和 SRIO，也能直接检验最关键机制。

## § 11 — 最强反例设计

最强反例不是换一个更大的矩阵，而是保持 72×72、相同特征值和相同 condition number，只改变 Hermitian 矩阵的基底或对称行列置换，使 leading pivot 从安全值变成接近 0。对每个谱固定的矩阵族生成数百个 \(PAP^T\) 或 \(QAQ^H\) 实例，送入同一 bitstream；如果数学问题的难度指标相同，仅因变量排列不同就出现 error flag、残差尖峰或 deadline 中断，就说明吞吐与稳定性来自未声明的 pivot-order 假设，而不是对“非奇异 Hermitian”类的稳健支持。

攻击还应加入作者声称的一般矩阵路径：构造 singular values 已知的 \(B\)，让 \(\kappa_2(B)\) 从 \(10^2\) 增至 \(10^6\)，比较直接 pivoted QR 求 \(B^{-1}\) 与 \(BB^H\) 路线。若后者的残差在 single precision 下按 \(\kappa(B)^2\) 快速恶化，即使硬件 throughput 仍高，也足以推翻“容易扩展到一般矩阵且保持 robust”的解释。最终评价必须同时报告失败率、最坏残差和 deadline miss，而不是只画平均曲线。

## § 12 — Follow-up Research Idea

**候选想法：面向控制 deadline 的自证式 matrix-solve service，而不是固定 matrix-inversion accelerator。** 这是基于本文证据与数值线性代数常识提出的候选方向，未做充分相关工作检索，不声称 novelty。

（a）驱动需求是控制器真正需要的并非一张显式逆矩阵，而是在 deadline 内得到可信的 \(Ax=b\)、增益或 beamforming weight；当前设计遇到小 pivot 只能退出，却没有告诉上层结果还能否安全使用。（b）研究价值在于把评价目标从“每秒多少次 inversion”改成“在输入 condition、pivot pattern 和 deadline 变化下，多少次请求能带可验证误差界按时完成”，把实时性和数值可靠性放进同一个接口契约。（c）可借鉴 mixed-precision iterative refinement、在线 condition estimation、Bunch-Kaufman 2×2 pivoting、QR fallback 和 control barrier/safety monitor；硬件前端先估计风险，正常输入走本文的高吞吐 fast path，高风险输入切到带 pivot 的 solve path，并返回 residual certificate，而不是无条件输出显式逆。

（d）第一个证伪实验就是第 11 节的等谱置换流：在相同 72×72 负载、相同平均资源预算和相同 deadline 下，如果自适应服务不能比固定 LDL 核显著降低 silent large-error 与 deadline miss 的联合概率，或 fallback 使正常工况 throughput 大幅下降，则该想法失败。（e）它与本文的实质区别不在于多加一个 QR 模块，而在于改变问题定义与输出：本文优化固定求逆数据通路并在小 pivot 时停止；候选系统优化的是带可验证 residual/状态的按时 linear solve，把矩阵性质变化、失败处置和上层控制决策纳入同一个研究对象。
