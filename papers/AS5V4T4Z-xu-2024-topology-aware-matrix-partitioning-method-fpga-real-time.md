# Topology-Aware Matrix Partitioning Method for FPGA Real-Time Simulation of Power Electronics Systems

作者：Han Xu；Jialin Zheng；Yangbin Zeng；Weicheng Liu；Fuhai Zhao；Chunhui Qu；Zhengming Zhao

出处：IEEE Transactions on Industrial Electronics, Vol. 71, No. 7

年份：2024

DOI：10.1109/TIE.2023.3308137

Zotero key：AS5V4T4Z

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个很具体的实时仿真矛盾：高开关频率 power electronics system（PES）要求很小的仿真步长，作者引用的工程经验是步长通常应为开关周期的 \(1/50\) 到 \(1/100\)；但 FPGA 虽适合低延迟并行计算，却不擅长在每一步在线做矩阵分解或求逆，而为每一种开关拓扑预存逆矩阵又会迅速耗尽片上存储。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

现有两条捷径各有明显代价。forward Euler（FE）一类显式方法主要做 matrix-vector multiplication（MVM），计算轻，但数值稳定性弱；associated discrete circuit（ADC）模型可保持方程不随拓扑变化，却会引入人工振荡以及开关参数与步长的耦合。更准确的 two-state switch model 与隐式积分则产生随开关状态变化的方程，需要昂贵的在线求解或大量预存逆矩阵。[pdf:E01]（PDF 物理页 1，Section I）[pdf:E02]（PDF 物理页 2，Section I）

作者的目标不是单纯再缩短一次步长，而是同时保住三件事：隐式积分的稳定性、FPGA 友好的固定时延 MVM 数据通路，以及不随开关数指数增长的矩阵存储。论文给出的直接工程价值是：在一块 Xilinx VC707 上，以 25 ns 步长仿真最高 200 kHz 的 n-port active bridge（NAB）案例，并在 DAB 对比中把作者所称的矩阵存储相关 memory resource 降到传统“为所有拓扑存逆矩阵”方法的约 \(1/15\)。[pdf:E01]（PDF 物理页 1，Abstract）

## § 2 — 前人工作与不足

论文把 prior work 分成四条路线。第一类是显式积分和 predictor-corrector：单步以 MVM 为主，适合 FPGA，但 FE 的稳定域较小，predictor-corrector 仍属于显式方法，不能获得纯隐式方法的稳定性。第二类是 implicit-explicit 与 latency insertion：通过一步或半步延迟把开关与其余网络解耦，已经能在 FPGA 上实现小步长，但稳定性仍弱于纯隐式方法，且精度依赖接口变量的性质。[pdf:E02]（PDF 物理页 2，Section I）

第三类是为各拓扑预存逆矩阵，或者只减少需要保存的逆矩阵数量。它把在线求解换成查表和 MVM，时延可预测，却受 FPGA 存储限制；论文还指出，已有 matrix-inversion technique 仍需保存足够多的逆矩阵才能维持精度。第四类是 network tearing / subsystem partition：把大系统拆成拓扑数较少的子系统；有的方法仍要为每个子系统保存各拓扑的 reduced inverse matrix，另一些方法虽然免存逆矩阵，却要在线做 Gauss-Jordan（GJ）过程，只有 reduced matrix 很小时才划算。[pdf:E02]（PDF 物理页 2，Section I）

TA-MP 与这些工作的差别不是“也做一次分块”，而是利用开关桥臂的拓扑语义选取分块边界，让完整方程的对角块与开关状态无关，再以这些常量块构造一个常量迭代矩阵。这样，在线开关变化只修改 interface variables，主要计算仍是 MVM；作者希望由此同时取消拓扑逆矩阵库和在线矩阵分解。[pdf:E02]（PDF 物理页 2，Section I 与 Section II-A）

需要谨慎的是，论文中的 Table III 汇集了不同电路、不同 FPGA 和不同 solver 的文献资源数据，这能说明方法在设计空间中的位置，却不是严格控制硬件与案例后的 apples-to-apples benchmark。[pdf:E10]（PDF 物理页 10，Table III）

## § 3 — 重建作者的思考路径

以下是基于论文背景与失败模式的重建，不是作者逐字陈述。

第一步，研究者会先排除“只靠显式积分”的路线：高频开关要小步长，而小步长本身并不能消除 FE 稳定域带来的参数限制；如果输入电阻等参数稍变，显式解仍可能振荡甚至发散。[pdf:E02]（PDF 物理页 2，Section I）[pdf:E07]（PDF 物理页 7，Section V-B 与 Fig. 7）

第二步，若坚持 trapezoidal 等隐式方法，真正不适合 FPGA 的不是所有运算，而是每个开关状态下重新分解或求逆一个变化矩阵。于是自然的问题变成：能否把“随拓扑变化的部分”隔离成低成本的变量修改，把昂贵的主体矩阵固定下来？

第三步，power converter 本来就由 half-bridge 等 switching leg 组成；用 switching-function approach 把每个桥臂替换为一对受控源，会在电路图中暴露 cut vertex。沿这些 cut vertex 把电路拆成子系统后，子系统内部动态不再随相邻桥臂状态改变，变化只通过 interface variables 跨边界传递。[pdf:E03]（PDF 物理页 3，Fig. 1、Section II-B、Eq. (2)-(4)）[pdf:E04]（PDF 物理页 4，Fig. 2）

第四步，既然完整矩阵的对角块固定，就可离线求它们的逆，并用 block Jacobi 代替每步直接求解。进一步把迭代式中含开关系数的项从矩阵列中提出，乘到 interface variables 上，便得到一个固定的 \(\widetilde B_G\)。若还能在离线阶段给出固定的最大迭代次数，在线数据通路就只剩“改接口变量、做 MVM、向量相加”，正好匹配 FPGA 的细粒度并行结构。[pdf:E04]（PDF 物理页 4，Eq. (14)-(17)）[pdf:E05]（PDF 物理页 5，Fig. 3 与 Fig. 4）

## § 4 — 核心 Intuition

核心 intuition 是：开关动作未必需要让整个隐式方程矩阵都变化；如果按 switching leg 的拓扑边界切开系统，变化可以被限制在子系统之间的 interface variables，而每个子系统对应的对角块保持常量。[pdf:E03]（PDF 物理页 3，Section II-B）于是作者把“为每个拓扑保存/求逆矩阵”改写成“保存一个常量迭代矩阵，并在每步先修改接口变量再做 MVM”。[pdf:E04]（PDF 物理页 4，Eq. (14)-(16)）只要 block Jacobi 在预定次数内收敛，隐式稳定性、固定时延和较低存储就能同时成立；真正决定方法是否可用的不是分块本身，而是这个固定迭代次数能否覆盖全部相关拓扑和工况。[pdf:E05]（PDF 物理页 5，Eq. (17) 后的讨论）

## § 5 — 具体方法与完整 Pipeline

以论文的 dual-active-bridge（DAB）为例，完整 pipeline 如下。

1. **把 switching leg 改写为受控源对。** half-bridge 的端口关系写为 \(v_E=k_1v_J,\ i_J=k_2i_E\)，其中 \(k_1,k_2\) 由开关状态决定；\(v_J,i_E\) 被选作 independent interface variables。[pdf:E02]（PDF 物理页 2，Eq. (1)）[pdf:E03]（PDF 物理页 3，Fig. 1 后正文）
2. **按 cut vertex 切分电路。** DAB 被两个 cut vertex 切成三个子系统。每个子系统都有状态 \(x_k\)、独立源 \(u_{s,k}\)、受控源 \(u_{c,k}\) 和接口输出 \(y_k\)；相邻子系统通过 \(K_jy_j\) 传递开关状态影响。[pdf:E03]（PDF 物理页 3，Section II-B、Eq. (2)-(4)）[pdf:E04]（PDF 物理页 4，Fig. 2）
3. **组装 topology-aware block matrix。** 对角块对应子系统自身，保持常量；off-diagonal blocks 表示相邻接口的影响，并包含开关系数 \(K_j\)。这一步把“拓扑变化”从整个矩阵缩小到子系统之间的连接。[pdf:E03]（PDF 物理页 3，Eq. (5)-(7) 周边正文）[pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. (5)）
4. **离线离散并预计算。** 论文采用 A-stable 的 trapezoidal method，把 DAE 离散为 \(Gz_{n+1}=b_n\)。随后离线构造由对角块组成的 \(D_G\)、其逆 \(D_G^{-1}\)、常量迭代矩阵 \(\widetilde B_G\)，并由收敛目标预定 \(i_{\max}\)。初始化在 PC 上执行，生成的矩阵再写入 FPGA。[pdf:E03]（PDF 物理页 3，Eq. (8)-(12)）[pdf:E04]（PDF 物理页 4，Eq. (13)-(17)）[pdf:E06]（PDF 物理页 6，Section IV-A）
5. **在线处理开关。** ADC / gate input 先决定当前实际开关状态，LUT 给出对应 \(K_k\)；这些系数只用于逐元素修改 interface variables。对于非主动控制的二极管，实际导通状态还依赖电流方向。[pdf:E06]（PDF 物理页 6，Fig. 6 与 Section III-D、IV-A）
6. **在线固定次数迭代。** FPGA 并行计算 \(\widetilde B_G\widetilde y_{n+1}^{(i)}\) 与 \(f_n\)，做向量相加，按 \(i_{\max}\) 重复。论文研究案例中 \(i_{\max}=1\)，因而没有额外的重复 MVM；这只是案例结果，不应外推为所有 PES 都只需一次迭代。[pdf:E06]（PDF 物理页 6，Fig. 6 与 Section IV-A）
7. **恢复状态并输出。** interface variables 确定后，各子系统状态可独立计算；实时结果经 16-bit DAC 输出到示波器，MAB 案例还通过 ADC/DAC 与真实控制器闭环形成 RT-HIL。[pdf:E04]（PDF 物理页 4，Eq. (15) 后正文）[pdf:E08]（PDF 物理页 8，Section V-C）[pdf:E09]（PDF 物理页 9，Fig. 10 与 Fig. 11）

从 EMT + FPGA 验收维度看，论文报告了 two-state switch model、trapezoidal 固定步长、开关状态处理、MVM 并行、FPX 24.24 定点表示、VC707 实板、DAB 实时输出以及三端口 MAB RT-HIL；没有把该实现表述为一个覆盖任意网络元件的通用 EMT 平台。多速率没有实现，只在结论中作为未来可组合方向；blocking state / discontinuous conduction mode 与 nonlinear element 也不能由当前 TA-MP 直接处理。[pdf:E06]（PDF 物理页 6，Section III-D、IV-B）[pdf:E10]（PDF 物理页 10，Section VI）

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从桥臂拓扑到子系统接口

switching leg 的受控源关系是

\[
v_E=k_1v_J,\qquad i_J=k_2i_E .
\]

\(k_1,k_2\) 是由开关状态确定的 switching coefficients。这一步的工程意义是把“开关拓扑改变”写成端口变量前的系数，而不是直接重建整个电路矩阵。[pdf:E02]（PDF 物理页 2，Eq. (1)）

第 \(k\) 个子系统写成

\[
\dot x_k=A_kx_k+B_ku_{s,k}+E_ku_{c,k},
\qquad
y_k=C_kx_k+D_ku_{s,k}+F_ku_{c,k},
\]

并把相邻子系统对它的受控源贡献写为

\[
u_{c,k}=\sum_{j\in N(k)}S_{k,j}K_jy_j .
\]

这里 \(x_k\) 是 state vector，\(u_{s,k}\) 是 independent sources，\(u_{c,k}\) 是 switching leg 引入的 controlled sources，\(y_k\) 是 independent interface variables；\(S_{k,j}\) 负责选择和扩展相邻变量，\(K_j\) 是包含开关系数的对角矩阵。[pdf:E03]（PDF 物理页 3，Eq. (2)-(4) 及变量定义）

代入后，完整矩阵的 diagonal blocks 只含子系统自身矩阵，而含 \(K_j\) 的项出现在 off-diagonal blocks。Fig. 2 给出的 DAB 例子清楚显示：绿色对角块是 constant part，橙色块是由 interface variables 连接的 varying part。[pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. (5)）

### 6.2 隐式离散

论文从 DAE

\[
\dot x=f(x,y,t),\qquad g(x,y,t)=0
\]

出发，用 trapezoidal method 离散：

\[
x_{n+1}=x_n+\frac h2\left[f(x_n,y_n,t_n)+f(x_{n+1},y_{n+1},t_{n+1})\right],
\qquad
0=g(x_{n+1},y_{n+1},t_{n+1}),
\]

最后整理成

\[
Gz_{n+1}=b_n .
\]

\(h=t_{n+1}-t_n\) 是步长。隐式性来自 \(n+1\) 时刻变量同时出现在方程右侧；这带来 A-stability，但也产生每步线性方程求解需求。[pdf:E03]（PDF 物理页 3，Eq. (8)-(12)）

### 6.3 从 block Jacobi 到常量迭代矩阵

令 \(D_G=\operatorname{diag}(G_1,\ldots,G_N)\)，标准 block Jacobi 迭代为

\[
z_{n+1}^{(i+1)}
=B_Gz_{n+1}^{(i)}+f_n,\qquad
B_G=D_G^{-1}(D_G-G),\qquad
f_n=D_G^{-1}b_n,
\]

初值取 \(z_{n+1}^{(0)}=z_n\)。因为 \(D_G\) 的块不随开关状态变化，\(D_G^{-1}\) 可以只在离线阶段计算一次。[pdf:E04]（PDF 物理页 4，Eq. (14)）

原始 \(B_G\) 仍含 \(K_j\)，所以还不是常量。作者观察到 \(D_G-G\) 中对应 state variables 的列为零，并把剩余列中的 \(K_j\) 提到 interface variables 上，得到

\[
z_{n+1}^{(i+1)}
=\widetilde B_G\widetilde y_{n+1}^{(i)}+f_n,
\]

\[
\widetilde y_{n+1}^{(i)}
=\left[
(K_1y_{1,n+1}^{(i)})^T\ 
(K_2y_{2,n+1}^{(i)})^T\ \cdots\
(K_Ny_{N,n+1}^{(i)})^T
\right]^T .
\]

于是 \(\widetilde B_G\) 不再含 switching coefficients；开关状态只改变 \(\widetilde y\)。同时，state variables 不参加迭代，接口收敛后各子系统状态可独立恢复。[pdf:E04]（PDF 物理页 4，Eq. (15)-(16) 及邻近正文）[pdf:E05]（PDF 物理页 5，Fig. 3）

### 6.4 固定迭代次数与收敛边界

论文用谱半径 \(\rho\) 和误差目标预估固定的最大迭代次数：

\[
i_{\max}
=
\left\lceil
\log_{\rho}\frac{e_n}{e_0}
\right\rceil
=
\left\lceil
\log_{\rho}
\frac{0.01\max\left((hv)^{q+1},\mathrm{tol}_{abs}\right)}{hv}
\right\rceil ,
\]

其中 \(q\) 是积分阶数（trapezoidal method 时 \(q=2\)），\(v\) 是 state variables 的变化率，\(\mathrm{tol}_{abs}\) 是设定的 absolute error。[pdf:E04]（PDF 物理页 4，Eq. (17)）这个公式把可变的“迭代到收敛”为固定硬件时延，但成立前提是离线误差界和谱半径能覆盖运行中的全部相关拓扑与工况。

作者援引的充分条件是：每个 \(G_k\) 非奇异，且完整 \(G\) strictly block diagonally dominant。论文认为 \(I-\frac h2A_k\) 在子系统特征值实部不大于零时非奇异，并指出 \(h\) 越小，\(G\) 越可能满足 block diagonal dominance；这是“小步长有利于收敛”的理论理由，而不是对所有网络与参数的无条件证明。[pdf:E06]（PDF 物理页 6，Section III-D-2）

## § 7 — 实验设计与结论

### 问题 1：在相同步长下，TA-MP 是否比 FE 更稳定、同时接近隐式参考？

**实验。** 作者在 Simulink S-Function 中实现 TA-MP 与 FE，并用 fixed-point toolbox 模拟定点格式；两者步长均为 25 ns，以 Simulink implicit ode23s 为 benchmark。DAB 参数为：两侧直流电压 600 V / 400 V，两侧直流母线电容 1 mF / 250 \(\mu\)F，变压器漏感 42 \(\mu\)H、励磁电感 2.49 mH，端口电阻 1 m\(\Omega\)，开关频率表列范围 20-200 kHz；该精度实验取 20 kHz，并在 0.0125 s 把副边 phase-shift ratio 从 0 改为 0.3。[pdf:E07]（PDF 物理页 7，Table I、Section V-B）

**答案。** DAB 被分为三个子系统，构造 13-D preconditioner matrix 与 8-D iterative matrix；当 absolute error 要求为 \(10^{-8}\) 时，作者报告 \(i_{\max}=1\)。Fig. 7 中 FE 出现 numerical oscillation，高频电流误差约 3 A，输入电阻略减时甚至发散；TA-MP 波形与 Simulink reference 良好一致，计算复杂度接近 FE。[pdf:E07]（PDF 物理页 7，Fig. 7 与 Section V-B）不过论文主要给出波形和 absolute-error 曲线，没有报告跨完整参数域的统一 RMSE / worst-case error 表，因此“comparable accuracy”不应外推到未测网络。

### 问题 2：DAB 能否在 FPGA 上满足 25 ns 的真实时间预算？

**实验。** solver 采用 48-bit、24-bit integer-width 的 FPX 24.24 定点格式，经 Vitis HLS 和 Vivado 部署到 Xilinx VC707（XC7VX485T-2FFG1761C）。平台还包括 14-bit ADS4449 ADC（最高 250 MSPS）与 16-bit DAC34H84（最高 1.25 GSPS）。[pdf:E06]（PDF 物理页 6，Section IV-B）[pdf:E08]（PDF 物理页 8，Fig. 8 与 Section V-C-1）

**答案。** Table II 报告 TA-MP calculation time 为 18.408 ns，小于 25 ns 步长；实时 DAB 实验把开关频率从 20 kHz 提高到 200 kHz，并捕获副边方波相对原边从领先 \(0^\circ\) 变为领先 \(90^\circ\) 的瞬态。作者据此声称 200 kHz 下仍可准确实时仿真。[pdf:E08]（PDF 物理页 8，Fig. 9、Table II、Section V-C-2）论文没有报告板级 clock frequency、timing slack 分布、温度/电压角落或长时间 overrun 统计。

### 问题 3：相对预存所有拓扑逆矩阵，资源与延迟是否下降？

**实验。** 对比方法同样使用 trapezoidal method，但把全部拓扑逆矩阵预存；两者都用 C++、相同 HLS optimization instructions 转成 HDL。[pdf:E08]（PDF 物理页 8，Section V-C-2）

**答案。** Table II 中 TA-MP 与对比法的 calculation time 分别为 18.408 ns 与 30.364 ns；total LUTs 为 8774（2.89%）与 46901（15.45%）；computation kernel LUTs 为 2540（0.84%）与 40877（13.46%）；slice registers 为 578（0.095%）与 437（0.072%）；DSP48 为 48（1.71%）与 104（3.71%）。作者把结果概括为 TA-MP 仅消耗约 \(1/15\) 的 memory resource，同时只需 MVM。[pdf:E08]（PDF 物理页 8，Table II 与其后正文）这里“memory resource”主要由 LUT 使用量体现；Table II 未给出 BRAM 数量，也未报告功耗。

### 问题 4：方法能否闭合到真实控制器的 RT-HIL，而不只是在板上输出波形？

**实验。** 作者在同一 FPGA 平台上实现三端口 multi-active bridge（MAB）RT-HIL，通过 ADC/DAC 接真实控制器，并与同一控制器驱动的 power experiment 波形比较；开关频率为 20 kHz。[pdf:E08]（PDF 物理页 8，Section V-C-3）[pdf:E09]（PDF 物理页 9，Fig. 10 与 Fig. 11）

**答案。** MAB solver 的 reported computational delay 为 21.912 ns，资源为 LUT 1.64%、register 0.11%、DSP48 3.26%。作者判断实验波形与 RT-HIL 波形良好一致，同时明确说明物理实验含 switching transient，而 RT-HIL 波形更理想化。[pdf:E08]（PDF 物理页 8，Section V-C-3）[pdf:E09]（PDF 物理页 9，Fig. 11 后正文）论文未给出这组 HIL 对比的数值误差指标、controller 型号/控制周期或接口总闭环延迟。

### 问题 5：资源扩展是否优于全逆矩阵方案？

**实验与答案。** Fig. 12 的 resource-utilization scaling 比较显示：全存逆矩阵方案最多支持 8 个 DAB，而 TA-MP 图示可到 28 个 DAB，此时瓶颈从 LUT memory 转为 DSP48；对 NAB port 数，前者最高 4 port，TA-MP 图示最高 16 port。[pdf:E09]（PDF 物理页 9，Fig. 12 与 Section V-D）这组证据说明综合资源增长趋势，但没有同时给出最大规模 28-DAB 或 16-port 案例的实时波形、误差和 HIL 闭环结果，不能把“资源可容纳”直接等同于“大规模动态精度已验证”。

## § 8 — Take-aways

**5 句话：**

1. TA-MP 用 switching-leg topology 把 PES 分成子系统，使对角块固定、开关变化只进入接口耦合项。[pdf:E03]（PDF 物理页 3，Section II-B）
2. 作者从 block Jacobi 中提出 switching coefficients，得到可预存的常量 \(\widetilde B_G\)，把在线计算压缩为接口变量修改与 MVM。[pdf:E04]（PDF 物理页 4，Eq. (14)-(16)）
3. 在研究案例里 \(i_{\max}=1\)，DAB 在 VC707 上以 25 ns 步长运行，reported calculation time 为 18.408 ns。[pdf:E07]（PDF 物理页 7，Section V-B）[pdf:E08]（PDF 物理页 8，Table II）
4. 与全存逆矩阵的 trapezoidal baseline 相比，TA-MP 显著降低 LUT 与 DSP48，并完成 20 kHz 三端口 MAB 的真实控制器 RT-HIL。[pdf:E08]（PDF 物理页 8，Table II 与 Section V-C-3）
5. 核心边界是固定次数 block Jacobi 的覆盖性：blocking state、nonlinear element、非 switching-leg topology 和未验证的大规模强耦合工况都可能破坏当前证据的外推。[pdf:E06]（PDF 物理页 6，Section III-D）[pdf:E09]（PDF 物理页 9，Section V-D）

**3 句话：**

1. 这篇论文真正的新机制是把 topology dependence 从隐式矩阵主体挪到 interface variables，因而只保存一套常量迭代数据。[pdf:E04]（PDF 物理页 4，Fig. 2、Eq. (15)-(16)）
2. DAB 与 MAB 证据表明该机制能在 25 ns 量级的 FPGA 数据通路上运行，并显著降低对比方案的 LUT 使用。[pdf:E08]（PDF 物理页 8，Table II 与 Section V-C）
3. 但“一次迭代即可”只在研究案例成立，论文没有给出覆盖所有相关拓扑、参数不确定性与强耦合网络的统一收敛证书。[pdf:E06]（PDF 物理页 6，Section III-D-2）

**1 句话：**

TA-MP 是一种以拓扑语义换取常量隐式迭代矩阵的 FPGA solver 设计，其价值已经由小步长实板与 RT-HIL 案例支持，但其可扩展性的决定性问题仍是固定迭代次数能否对所有目标工况可靠成立。[pdf:E08]（PDF 物理页 8，Section V-C）[pdf:E09]（PDF 物理页 9，Section V-D）

## § 9 — 最脆弱的假设

最脆弱的假设是：**按 switching leg 得到的分块，不仅让对角块固定，而且会让全部目标开关状态与参数工况下的 block Jacobi 都在同一个预定 \(i_{\max}\) 内达到足够精度。** 如果这个假设失效，TA-MP 就必须恢复到 topology-dependent iteration count、增加最坏情况迭代硬件预算，或重新引入在线求解；固定时延、低计算量和隐式精度这三项核心收益会同时受损。

论文为这个假设提供了两层证据。理论层面，作者给出每个 \(G_k\) 非奇异、完整 \(G\) strictly block diagonally dominant 的充分条件，并论证小步长使后者更可能成立。[pdf:E06]（PDF 物理页 6，Section III-D-2）案例层面，DAB 在 absolute error \(10^{-8}\) 时得到 \(i_{\max}=1\)，并由 25 ns 的仿真和实板波形支持该特定模型。[pdf:E07]（PDF 物理页 7，Section V-B）

缺失的证据是：没有对所有开关组合、元件容差、强耦合程度和大规模分区做谱半径 / residual 的最坏情况扫描；Fig. 12 只给资源可扩展性，没有给 28-DAB 或 16-port 极限规模的收敛与精度结果。[pdf:E09]（PDF 物理页 9，Fig. 12）作者还明确承认 blocking state 对应的 discontinuous conduction mode 不能直接支持、nonlinear elements 需要与其他方法结合、非 switching-leg topology 需要额外矩阵更新步骤。[pdf:E06]（PDF 物理页 6，Section III-D-3）这些已知边界进一步说明，当前证据不能把“常量矩阵”与“统一固定迭代次数”当成任意 PES 的普遍性质。

## § 10 — 最小复现实验

一周内最有价值的复现不是搭完整 RT-HIL，而是验证“常量迭代矩阵 + \(i_{\max}=1\)”是否真的闭合到 DAB 的全部开关状态和一小块参数邻域。

**数据与模型。** 使用 Table I 的 DAB 参数：600 V / 400 V、1 mF / 250 \(\mu\)F、42 \(\mu\)H 漏感、2.49 mH 励磁电感、1 m\(\Omega\) 端口电阻和 20-200 kHz 开关范围；实现论文 Fig. 2 的三子系统划分以及 Eq. (14)-(16) 的 TA-MP。[pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. (14)-(16)）[pdf:E07]（PDF 物理页 7，Table I）

**实现。** 在 double precision 中同时实现三个 solver：每步直接解 \(Gz_{n+1}=b_n\) 的 trapezoidal reference、固定一次迭代的 TA-MP、FE。再把 TA-MP 量化为论文的 FPX 24.24，检查定点误差是否改变收敛结论。[pdf:E06]（PDF 物理页 6，Section IV-B）

**扫描。** 枚举 DAB 的合法开关状态与论文的 phase-shift transition，并围绕端口电阻、漏感和步长做小范围 sweep；每一步记录 \(\rho\)、一次迭代后的 linear residual、与直接隐式解的最大状态误差，以及 FE 是否振荡。另记录 \(\widetilde B_G\) 是否在所有状态下字节相同，排除实现悄悄重建矩阵的可能。

**支持标准。** 若全部枚举状态中 \(\rho<1\)，一次迭代 residual 达到 \(10^{-8}\) 对应的误差目标，25 ns 下 TA-MP 与直接隐式解的误差稳定且没有随时间累积，同时 FE 在论文所述低阻条件附近更早失稳，则最小实验支持论文核心机制。[pdf:E07]（PDF 物理页 7，Fig. 7 与 Section V-B）

**反驳标准。** 若任一仍处于论文 piecewise-linear、two-state switch scope 内的合法状态出现 \(\rho\ge1\)、需要 topology-dependent iteration count 才能达到误差目标，或 FPX 24.24 让 residual / 状态误差超出预设阈值，则“固定一次迭代且维持隐式精度”的案例 claim 被反驳或至少需要收缩。

这项复现不验证论文的板级 18.408 ns 时延、ADC/DAC 链路和 HIL 闭环；这些必须有 VC707 或等效硬件才能独立复现，论文也未提供可直接复用的公开代码或完整 HDL 工程信息。

## § 11 — 最强反例设计

最强反例应留在作者声称的 piecewise-linear、two-state switching-leg scope 内，而不是简单加入作者已经排除的 nonlinear device。可以构造一个由多个 DAB 紧耦合而成的低阻网络：子系统内部保持论文同类元件与桥臂模型，但把接口耦合增强到 off-diagonal blocks 与 diagonal blocks 同量级，再在若干桥臂同步换相时触发最不利拓扑。

攻击步骤是：对全部同步开关组合计算 block Jacobi 的谱半径和一次迭代 residual；以直接 trapezoidal solve 为真值，在 25 ns 下比较长时波形、能量偏差和换相后的 peak error。若某些合法拓扑使 \(G\) 不再 strictly block diagonally dominant、\(\rho\ge1\)，或者虽然最终可收敛但所需次数随拓扑显著变化，那么同一个固定 \(i_{\max}\) 不能同时保证实时 deadline 和隐式精度。[pdf:E06]（PDF 物理页 6，Section III-D-2）

这个反例比测试已知不支持的 blocking state 更有力，因为它不改变元件线性和 switching-leg 基本单元，只改变耦合强度与同步事件；它直接攻击“topology-aware partition 足以产生可预定的固定迭代时延”这一核心机制。论文的 Fig. 12 证明资源模型可向多 DAB 扩展，却没有提供最大规模动态收敛证据，因此该反例目前未被实验排除。[pdf:E09]（PDF 物理页 9，Fig. 12 与 Section V-D）

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty：面向全拓扑参数集合的可认证 partition-and-preconditioner co-design。**

本领域的高影响工作通常不仅要给出更低的 FPGA 资源数字，还要同时闭合数值正确性、确定性实时 deadline、硬件可实现性和真实 HIL / power-stage 对比。当前未满足的需求是：设计者不知道一个按 switching leg 直觉选出的 partition，是否真的能在全部合法拓扑、元件容差和多转换器耦合下保持 \(\rho<1\) 及统一 \(i_{\max}\)。

研究问题应从“怎样把矩阵固定下来”改为“能否共同设计 partition、interface variables 与 preconditioner，使整个 admissible topology-parameter set 都具有可证明的收敛上界，并在 FPGA 预算内达到固定 deadline”。可借鉴相邻领域的 robust numerical linear algebra、graph partition optimization、interval / affine arithmetic 和 formal verification：离线搜索分区与缩放，输出一个覆盖全部 admissible states 的 spectral-radius / residual certificate；在线只运行已认证的数据通路，若输入越出证书范围则明确 fail closed，而不是静默继续。

第一个可证伪实验是在一个规模仍可穷举的多 DAB 网络上，枚举全部开关拓扑并对元件容差做区间包络。如果不存在任何满足给定 LUT/DSP/25 ns 预算且对全部状态保证 \(\rho<1\) 与目标 residual 的 partition / preconditioner，或者区间证书过度保守到无法容纳论文 DAB 基线，这个想法立即失败。若能通过，再把证书预测的最坏拓扑部署到 FPGA，以直接隐式解和物理控制器 HIL 双重对照。

它与本文的实质区别不是再增加一种 nonlinear module，也不是换一个 converter。本文先按 switching leg 分块，再在个别 DAB/MAB 案例中计算并验证 \(i_{\max}\)；候选方向则把“对所有目标状态的固定时延收敛保证”本身变成优化目标和交付物，从经验案例验证转向 solver 适用域的可机读证书。[pdf:E06]（PDF 物理页 6，Section III-D）[pdf:E09]（PDF 物理页 9，Fig. 12）
