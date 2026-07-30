# FPGA-Based Implicit–Explicit Real-Time Simulation Solver for Railway Wireless Power Transfer With Nonlinear Magnetic Coupling Components

**作者**：Han Xu，Yangbin Zeng，Jialin Zheng，Kainan Chen，Weicheng Liu，Zhengming Zhao  
**出处**：IEEE Transactions on Transportation Electrification，Vol. 10，No. 3，pp. 6549–6558  
**年份**：2024  
**DOI**：10.1109/TTE.2023.3332583  
**Zotero key**：7BZSU9CP  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是一般的“如何把 WPT 电路放进 FPGA”，而是一个更具体的实时仿真矛盾：列车运动时，接收线圈不断离开、进入分段发射线圈，磁耦合单元的自感和互感随位置连续、非线性变化；与此同时，功率变换器的高开关频率又要求很小的实时步长。原型控制器测试昂贵且有安全风险，RT-HIL 本来可以把控制器接到虚拟功率级上，但 FPGA 必须在每个固定 deadline 内同时处理刚性 PWL 电路和非线性磁耦合，不能依赖耗时且迭代次数不定的非线性求解。作者把这一冲突概括为“显式法快但稳定域小、全隐式法稳但非线性迭代慢、传统 latency-based 解耦虽免迭代却引入一步接口延迟”。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

工程对象是一套仿真的 350 kW 铁路 WPT 系统，由发射单元、磁耦合单元和接收单元组成。[pdf:E14]（PDF 物理页 2，Section II-A）该系统最高开关频率为 40 kHz；作者指出 250 ns 通常能在这一频率下给出相对准确的结果，但其目标是把实时步长进一步压到 75 ns。系统中的两个 62.34 nF 谐振电容会引入快速状态和刚性，而磁耦合参数又随列车位置变化。[pdf:E04]（PDF 物理页 3，Section II-B、Fig. 1–2）因此，价值不只是“更快仿真”：若能在固定 75 ns deadline 内稳定地重现移动耦合过程，就可能在不上真实 350 kW 功率平台的情况下测试控制器启动、通信和跨线圈切换行为。

需要限定这个价值的边界。论文展示的是一套特定铁路 WPT 模型和一块特定 FPGA 上的结果，不等于已经证明任意 EMT 网络、任意非线性磁器件或任意规模系统都能在 75 ns 下实时运行。论文也没有报告标准 EMT 节点分析框架、通用网络组装器或多装置并行案例；它更准确地是一种针对“可分成 NL 磁耦合块和 PWL 功率电路块”的实时积分器与 FPGA 映射方案。

## § 2 — 前人工作与不足

作者把既有路线分成三类。

第一类是显式法。它只依赖旧时刻状态，不必在每一步求非线性方程，因此计算时间短而且确定；代价是稳定域有限，面对小谐振电容所形成的刚性状态时可能发散。第二类是隐式迭代法。它有更好的数值稳定性，但每步都要迭代求解非线性方程，带来长且不均匀的计算延迟；即使引入补偿技术，作者仍认为很难达到所需的小步长。第三类是 latency-based 解耦：把 NL 与 PWL 部分拆开计算，或假设 NL 部分变化更慢，或让两块在同一步长下分别采用显式和隐式方法。它避免了非线性迭代，却把两块的接口量错开一个完整步长；作者认为这一步延迟会削弱稳定性，并指出传统方法在本文 WPT 案例中发散，而拟议方法在相同步长下收敛。[pdf:E01]（PDF 物理页 1，Section I）[pdf:E02]（PDF 物理页 2，Section I）

在本文后续的同平台比较中，forward Euler 和传统 latency-based 方法都能把单步计算时间压到 75 ns 内，但都在目标系统上发散；trapezoidal 全隐式法稳定且误差相近，却需要超过芯片可提供量的 DSP，单步计算时间也远超实时 deadline。[pdf:E12]（PDF 物理页 8，Table III）这组结果把“不足”说得更精确：瓶颈不是某一种方法完全算不动，而是无法同时满足稳定、固定小步长和有限 FPGA 资源这三个条件。

这里的相关工作结论均是论文自己的综述和实验口径，本卡未独立读取被引论文。特别是“传统 latency-based 方法在不同系统中普遍不稳定”不能由本文推出；本文只证明了作者实现的对照方法在其目标 WPT 工况和简化电路上失败。

## § 3 — 重建作者的思考路径

可以从论文出现之前已经明确的约束重建这条思路，而不先假设 IMEX 是答案。

1. 真实列车移动把磁耦合参数变成位置相关量。作者用有限元得到线圈错位下的自感、互感变化，共采样 26 个位置点；从 Fig. 1(c) 可见，一个接收线圈离开发射线圈时对应互感下降，进入下一段时另一互感上升。[pdf:E03]（PDF 物理页 2，Section II-A）这说明把磁耦合长期冻结为常量会漏掉恰好需要测试的动态过程。
2. 直接为每个连续变化的电感组合存完整系统方程不可行；每步迭代求非线性方程又破坏小步长和固定 deadline。于是自然要问：是否能把“持续变化但结构较小的磁耦合块”从“大部分拓扑切换但分段线性的功率电路块”中分离出来？
3. 分块后，传统方法已有一个有吸引力的方向：NL 块显式算、PWL 块隐式算。但如果两边只交换上一步接口量，接口延迟正是新的不稳定源。小电容导致的刚性使这个缺陷在目标电路里暴露得尤其明显。[pdf:E02]（PDF 物理页 2，Section I）
4. 因而下一步不是重新引入非线性迭代，而是在一个完整步内增加一个中点：先算到 \(t_{n+1/2}\)，立刻交换中点接口量，再由中点推进到 \(t_{n+1}\)。这样第二阶段可以消除整步接口延迟，同时仍让 NL 块保持显式。
5. FPGA 上真正的实现问题随后变成：如何让两个阶段不把计算时间翻倍？答案是让每个硬件计算节拍只执行一个阶段，Stage 1 和 Stage 2 交替；NL 与 PWL 块在各阶段内部并行，PWL 块进一步映射为并行 MVM，磁耦合参数通过 LUT 取得。[pdf:E09]（PDF 物理页 6，Fig. 5）

这条路径的关键不是“用了 FPGA”，而是把数值耦合延迟和硬件 deadline 当成同一个设计问题：新增中点阶段修复数值接口，新阶段再通过交替流水和块内并行消化。

## § 4 — 核心 Intuition

把难题拆成两个性质不同的块：磁耦合 NL 块用显式更新避免非线性迭代，刚性的 PWL 功率电路块用隐式更新获得稳定性。传统解耦失败在两块相隔一个旧步长交换信息；本文在每个完整步中插入中点，使第二阶段使用同一中点的接口量，从而消除整步延迟。硬件上并不要求在一个 75 ns 节拍里连续完成两阶段，而是让阶段交替执行，所以增加一个数值阶段不必直接把实时步长翻倍。[pdf:E06]（PDF 物理页 4，式 (6)–(9) 及其解释）[pdf:E12]（PDF 物理页 8，Table III 与 Section V-D）

## § 5 — 具体方法与完整 Pipeline

以列车从发射线圈 Tx1 向 Tx2 运动的一步为例，完整 pipeline 如下。

1. **建立分块状态模型。** 磁耦合单元被划为 NL 部分，其他变换器、整流器、buck 和谐振支路属于 PWL 部分。两块通过成对受控源连接：PWL 侧给出磁耦合端口电压 \(\boldsymbol y_\ell\)，NL 侧回送端口电流 \(\boldsymbol y_{\mathrm{nl}}\)。这对受控源等效于变比为 1 的 ideal transformer model，因此分块没有改变原电路端口关系。[pdf:E04]（PDF 物理页 3，Fig. 1–2 与 Section III-A）[pdf:E05]（PDF 物理页 4，式 (1)–(5)）
2. **更新磁耦合参数。** FPGA 根据预定义或外部输入的运行条件读取电感 LUT。论文说明 \(L_p,L_{s1},L_{s2},M_1,M_2\) 可视为相对位置和电流的函数，但实现部分只说依据位置、速度等运行条件查表；LUT 的维数、26 个有限元点之间如何插值、越界如何处理、是否在线考虑电流相关饱和均未报告。[pdf:E03]（PDF 物理页 2，26 个有限元位置点）[pdf:E05]（PDF 物理页 4，变量定义）[pdf:E08]（PDF 物理页 5，Section IV-A/B/C）
3. **确定开关状态。** FPGA 同时读取物理控制器的 gate signals，并执行 switching-signal detection、zero-crossing detection 和 voltage-amplitude detection，选择第 \(k\) 个 PWL 系统矩阵。论文给出了流程框图，但没有报告同一时刻多开关事件的优先级、事件时刻插值、死区模型或亚步长事件校正。[pdf:E09]（PDF 物理页 6，Fig. 5(b)）
4. **Stage 1：推进到中点。** 在 \(t_n\) 计算两块接口量；NL 块用显式半步推进到 \(t_{n+1/2}\)，PWL 块用隐式半步推进到同一中点。两块并行计算。
5. **Stage 2：用中点接口推进到下一整步。** 在 \(t_{n+1/2}\) 重新交换接口量；两块再由共同中点推进到 \(t_{n+1}\)。NL 与 PWL 此时都采用显式中点形式，从而去掉传统方法的一整步接口延迟。[pdf:E06]（PDF 物理页 4，式 (6)–(9)）
6. **映射到 FPGA。** PWL 单步主要是 matrix-vector multiplication，作者使用 TA-MP 方法并让不同行的 dot product 并行；Stage flag 在两套时间推进式之间切换。NL 和 PWL 块同阶段并行，两个阶段跨计算节拍交替。[pdf:E09]（PDF 物理页 6，Fig. 5(a)(c)）
7. **数值表示与平台。** 实现使用 64-bit fixed-point，其中整数位宽为 24 bit；C++ 经 Vitis HLS 转为 HDL，再由 Vivado 部署到 Xilinx VC707 的 XC7VX485T-2FFG1761C。芯片总量为 303,600 LUT 和 2,800 DSP，平台通过 SFP/SFP+ 光纤与物理控制器连接，文中给出的 Ethernet 通信速率上限为 1,000 Mb/s，并用 16-bit DAC34H84 显示波形。[pdf:E08]（PDF 物理页 5，Section IV-B/C）
8. **在目标系统中执行。** Table I 给出 \(U_{\mathrm{in}}=1.5\ \mathrm{kV}\)、\(L_{f1}=42.95\ \mu\mathrm H\)、\(C_p=442.8\ \mathrm{nF}\)、\(C_{s1}=C_{s2}=62.34\ \mathrm{nF}\)、\(C_{f1}=C_{f2}=400\ \mu\mathrm F\)、buck 电感均为 \(1.1\ \mathrm{mH}\)，发射侧和接收侧开关频率分别为 40 kHz 与 5 kHz。作者用 75 ns 固定步长运行 IMEX，并把输出送往 DAC/波形记录仪或物理控制器。[pdf:E09]（PDF 物理页 6，Table I、Fig. 6 与 Section V-A）

论文报告了 75 ns 实时步长和一个半步中点，但没有报告多速率时间推进。硬件文字只说明每个 computational step 计算一个 stage、两个 stage 交替，并没有把公式中的完整步长 \(h\)、半步 \(h/2\)、75 ns wall-clock deadline 和可观测输出更新时间逐项对齐；因此不能仅凭 Table III 断言两个 stage 在同一个 75 ns 窗口内串行完成。论文也没有报告 FPGA 时钟频率、initiation interval、BRAM/FF/URAM 用量、片上 LUT 存储字节数、内存带宽、定点饱和/舍入策略、实时 overrun 计数或长期 jitter。HIL 方面，论文展示了物理控制器和光纤连接，却未报告控制器型号、控制算法参数、I/O 帧格式、端到端闭环延迟及同步误差。上述细节不能从板卡照片或波形反推。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 分块状态方程

NL 磁耦合块先写成

\[
\dot{\boldsymbol x}_{\mathrm{nl}}
=f_{\mathrm{nl}}(\boldsymbol x_{\mathrm{nl}},\boldsymbol y_\ell),
\qquad
\boldsymbol y_{\mathrm{nl}}
=g_{\mathrm{nl}}(\boldsymbol x_{\mathrm{nl}})
=\boldsymbol x_{\mathrm{nl}} .
\tag{1–2}
\]

对本文三绕组磁耦合，作者令

\[
\boldsymbol x_{\mathrm{nl}}
=[\Psi_p,\Psi_{s1},\Psi_{s2}]^\mathsf T,\quad
\boldsymbol y_{\mathrm{nl}}
=[i_1,i_2,i_3]^\mathsf T,\quad
\boldsymbol y_\ell=[u_1,u_2,u_3]^\mathsf T ,
\]

\[
f_{\mathrm{nl}}(\boldsymbol x_{\mathrm{nl}},\boldsymbol y_\ell)
=\boldsymbol y_\ell,\qquad
g_{\mathrm{nl}}(\boldsymbol x_{\mathrm{nl}})
=\boldsymbol M^{-1}\boldsymbol x_{\mathrm{nl}},
\]

\[
\boldsymbol M^{-1}
=\frac{1}{L_{s2}M_1^2+L_{s1}M_2^2-L_pL_{s1}L_{s2}}
\begin{bmatrix}
-L_{s1}L_{s2} & L_{s2}M_1 & L_{s1}M_2\\
L_{s2}M_1 & M_2^2-L_pL_{s2} & -M_1M_2\\
L_{s1}M_2 & -M_1M_2 & M_1^2-L_pL_{s1}
\end{bmatrix}.
\tag{3}
\]

直观上，磁通是 NL 块的状态，端口电压给出磁通变化率，当前电感矩阵的逆把磁通换成回送 PWL 块的电流。PWL 块则写为

\[
\dot{\boldsymbol x}_\ell
=\boldsymbol A_k\boldsymbol x_\ell+
\begin{bmatrix}\boldsymbol B_k^1&\boldsymbol B_k^2\end{bmatrix}
\begin{bmatrix}\boldsymbol u_I\\\boldsymbol y_{\mathrm{nl}}\end{bmatrix},
\tag{4}
\]

\[
\boldsymbol y_\ell
=\boldsymbol C_k\boldsymbol x_\ell+
\begin{bmatrix}\boldsymbol D_k^1&\boldsymbol D_k^2\end{bmatrix}
\begin{bmatrix}\boldsymbol u_I\\\boldsymbol y_{\mathrm{nl}}\end{bmatrix}.
\tag{5}
\]

\(k\) 表示当前开关拓扑，\(\boldsymbol u_I\) 是独立源，\(\boldsymbol x_\ell\) 是独立电容电压和电感电流。完整公式、矩阵和变量定义见 [pdf:E05]（PDF 物理页 4，式 (1)–(5)）。

式 (3) 暗含一个重要条件：分母

\[
\Delta=L_{s2}M_1^2+L_{s1}M_2^2-L_pL_{s1}L_{s2}
\]

必须远离零，否则 \(\boldsymbol M^{-1}\) 会病态，定点误差也会被放大。论文没有给出运动轨迹中 \(\Delta\) 或 \(\kappa(\boldsymbol M)\) 的范围。

还有一个原文内部不一致需要保留：通用式 (2) 末尾写成 \(\boldsymbol y_{\mathrm{nl}}=\boldsymbol x_{\mathrm{nl}}\)，但紧接着的本文专用模型又写成 \(\boldsymbol y_{\mathrm{nl}}=\boldsymbol M^{-1}\boldsymbol x_{\mathrm{nl}}\)，而 \(\boldsymbol x_{\mathrm{nl}}\) 随后被定义为磁通、\(\boldsymbol y_{\mathrm{nl}}\) 被定义为电流。除非 \(\boldsymbol M=\boldsymbol I\)，两者不能同时成立；按变量物理意义和式 (3)，实际实现应使用后者，但论文未显式勘误。[pdf:E05]（PDF 物理页 4，式 (2)–(3)）

### 6.2 两阶段 IMEX 推进

Stage 1 使用旧时刻接口量推进到中点：

\[
\boldsymbol x_{\mathrm{nl}}(t_{n+1/2})
=\boldsymbol x_{\mathrm{nl}}(t_n)
+\frac h2 f_{\mathrm{nl}}\!\left(
\boldsymbol x_{\mathrm{nl}}(t_n),\boldsymbol y_\ell(t_n)\right),
\tag{6}
\]

\[
\boldsymbol x_\ell(t_{n+1/2})
=\left(\boldsymbol I-\frac h2\boldsymbol A_k\right)^{-1}
\left[
\boldsymbol x_\ell(t_n)+
\begin{bmatrix}\boldsymbol B_k^1&\boldsymbol B_k^2\end{bmatrix}
\begin{bmatrix}\boldsymbol u_I(t_{n+1/2})\\
\boldsymbol y_{\mathrm{nl}}(t_n)\end{bmatrix}
\right].
\tag{7}
\]

NL 块的式 (6) 是显式半步，避免非线性迭代；PWL 块的式 (7) 把 \(\boldsymbol A_k\) 放在隐式逆矩阵中，承担刚性稳定性。到达中点后重新计算两块接口量，再执行

\[
\boldsymbol x_{\mathrm{nl}}(t_{n+1})
=\boldsymbol x_{\mathrm{nl}}(t_n)
+h f_{\mathrm{nl}}\!\left(
\boldsymbol x_{\mathrm{nl}}(t_{n+1/2}),
\boldsymbol y_\ell(t_{n+1/2})\right),
\tag{8}
\]

\[
\boldsymbol x_\ell(t_{n+1})
=\boldsymbol x_\ell(t_n)+h\left[
\boldsymbol A_k\boldsymbol x_\ell(t_{n+1/2})+
\begin{bmatrix}\boldsymbol B_k^1&\boldsymbol B_k^2\end{bmatrix}
\begin{bmatrix}\boldsymbol u_I(t_{n+1/2})\\
\boldsymbol y_{\mathrm{nl}}(t_{n+1/2})\end{bmatrix}
\right].
\tag{9}
\]

式 (8)–(9) 的工程意义是“两块都看见同一个中点”，因此不再用整步前的旧接口量驱动另一块。PDF 正文在 Stage 2-2 的一句话中写成“from \(t_{n+1/2}\) to \(t_n\)”，但式 (8)、式 (9) 和前文定义都明确目标是 \(t_{n+1}\)；这应视为正文笔误，而不是算法回退。公式与上下文见 [pdf:E06]（PDF 物理页 4，式 (6)–(9)）。

### 6.3 稳定性与二阶精度

作者用分裂测试方程

\[
\dot x=\lambda_0x+\lambda_1x
\tag{10}
\]

分析，其中 \(\lambda_0\) 对应显式部分、\(\lambda_1\) 对应隐式部分。令 \(z_0=h\lambda_0,z_1=h\lambda_1\)，得到放大因子

\[
\frac{y_{n+1}}{y_n}
=\frac{(z_0+1)^2+1+z_1(z_0+1)}{2-z_1}.
\tag{11}
\]

作者据此称，当 \(|z_0+1|<1\) 时对隐式变量 \(z_1\) 满足 A-stable 条件。更准确的读法是：隐式方向的稳定域很大，但仍受显式 NL 部分 \(z_0\) 的条件约束；它并不是对任意 NL 动力学都无条件 A-stable。

对

\[
\dot x=f_{\mathrm{nl}}(x)+f_\ell(x)
\tag{12}
\]

展开一个完整步，论文给出

\[
\begin{aligned}
x_{n+1}
=&\,x_n+h\big(f_{\mathrm{nl}}(x_n)+f_\ell(x_n)\big)\\
&+\frac{h^2}{2}
\big(f_{\mathrm{nl}}^{(1)}(x_n)+f_\ell^{(1)}(x_n)\big)\dot x_n
+O(h^3),
\end{aligned}
\tag{13}
\]

因此局部截断结构对应二阶数值精度。[pdf:E07]（PDF 物理页 5，式 (10)–(13)）但论文没有给出开关事件处的阶数证明；当一个时间步跨越拓扑不连续点时，平滑系统上的 Taylor 展开不能自动保证仍为二阶。

## § 7 — 实验设计与结论

### 问题 1：在不移动线圈时，75 ns IMEX 是否接近高精度离线仿真？

**实验。** 作者在 Simulink S-function 中以 C++ 实现 IMEX，固定步长 75 ns；参考模型由 Simscape 组件搭建，使用隐式变步长 ode23s。启动过程中线圈固定、电感不变，发射侧在前 0.01 s 内移相，接收侧在 0.01 s 后启动 closed-loop 输出电流控制。[pdf:E10]（PDF 物理页 6，Section V-A）

**答案。** Fig. 7 的启动波形基本重合；Table II 在 0.048–0.049 s 的稳态窗口比较 RMS 与峰值，所列相对误差为 0.05%–1.88%。例如 \(I_{rx1}\) RMS 为 93.44 A 对 94.93 A（1.57%），\(I_{\mathrm{out}}\) RMS 为 200.0 A 对 199.9 A（0.05%）。[pdf:E11]（PDF 物理页 7，Fig. 7、Table II）这支持“该案例下 75 ns IMEX 接近 Simulink”，但不是对全动态轨迹的全局误差上界。

### 问题 2：中点第二阶段是否真的改善了传统 latency-based 方法的稳定性？

**实验。** 在恒定车速、两个接收线圈从 Tx1 向 Tx2 迁移的动态工况下，作者采用 open-loop 控制，以排除闭环控制对数值稳定性比较的干扰；比较 IMEX、只保留第一阶段的传统 latency-based 方法和 Simulink。又从 WPT 系统抽取一个简化电路，扫步长并比较离散矩阵谱半径。

**答案。** Fig. 8 中 IMEX 与 Simulink 波形接近，latency-based 波形出现显著偏离；Fig. 9 中 latency-based 离散矩阵在所扫步长内谱半径持续大于 1，而 IMEX 在步长小于 100 ns 时谱半径小于 1。[pdf:E11]（PDF 物理页 7，Section V-B）[pdf:E12]（PDF 物理页 8，Fig. 8–9）这支持“增加中点阶段修复了该案例的接口延迟不稳定性”，但论文没有给出扫参边界、完整离散矩阵或跨多种电路的统计。

### 问题 3：算法能否在目标 FPGA 上满足 75 ns deadline？

**实验。** 作者在 VC707/XC7VX485T 上用 fixed-point HLS 实现 IMEX，并与 trapezoidal、forward Euler 和 latency-based 方法比较资源、计算时间和结果。

**答案。** IMEX 使用 21,119 LUT（6.96%）和 439 DSP48（15.68%），计算时间 68.212 ns，小于 75 ns；Table III 列出的 relative error 为 0.021%。Forward Euler 和 latency-based 分别只需 64.527 ns 与 64.229 ns，但结果发散。Trapezoidal 的 relative error 为 0.022%，却需要超过 100% 的 DSP，计算时间为 22,418.877 ns。[pdf:E12]（PDF 物理页 8，Table III）这证明了作者实现的 deadline 闭合，而不是一般 FPGA 的可移植保证。Table III 未说明 relative error 的精确定义、参考量和统计窗口；FF、BRAM、布线后频率及 timing slack 也未报告。

### 问题 4：静态 HIL 波形是否接近实物原型？

**实验。** 在线圈静止条件下，把 FPGA HIL 的发射侧 \(I_{Lf},I_{TX}\) 与接收侧 \(I_{\mathrm{buck11}}\) 和原型实验波形对比。

**答案。** Fig. 10 中 40 kHz 发射侧电流和 5 kHz buck 电流的形状、幅值相近，作者同时画出逐点相对误差。[pdf:E13]（PDF 物理页 9，Fig. 10）图可支持“波形总体吻合”，但不能从曲线估读一个论文未明确报告的最大误差；原型额定工况、传感器精度、示波器处理及重复次数均未报告。

### 问题 5：动态 RT-HIL 能否重现跨线圈切换的物理趋势？

**实验。** 让 Rx1、Rx2 依次离开 Tx1 并进入 Tx2，观察输出电流、输出电压和输入电压。

**答案。** Fig. 11 显示接收线圈离开发射线圈时 \(I_{\mathrm{out}}\) 与 \(U_{\mathrm{out}}\) 下降，进入下一发射线圈后在控制器作用下恢复；放大图还展示约 40 kHz 的输入波形。[pdf:E13]（PDF 物理页 9，Fig. 11 与 Section VI）这是动态 HIL 的可行性展示，但没有同步的动态实物原型真值，因此不能把该图称为动态工况精度验证。

EMT/FPGA/HIL 结论应保持如下边界：论文报告了 75 ns 实时步长、28 个开关、LUT/DSP 和单步计算时间；未报告 EMT 大系统规模、节点/状态数量上限、开关事件误差界、长时间 real-time overrun、通信往返延迟、BRAM/FF、功耗、热状态、不同 FPGA 的可移植性以及动态工况的实物真值。[pdf:E13]（PDF 物理页 9，Conclusion）

## § 8 — Take-aways

**5 句话。**  
这篇论文把移动铁路 WPT 的非线性磁耦合块与刚性的 PWL 功率电路块分开处理。  
NL 块显式推进避免非线性迭代，PWL 块隐式推进承担刚性稳定性。  
一个完整步中的中点再交换消除了传统 latency-based 解耦的一整步接口延迟，并在平滑测试方程上给出二阶精度。  
在 XC7VX485T 上，作者实现的 IMEX 单步计算为 68.212 ns，能满足 75 ns deadline，同时目标案例中的显式法和传统 latency-based 法发散。[pdf:E12]（PDF 物理页 8，Fig. 9、Table III）  
最重要的未决问题是，这个稳定性和定点精度能否跨越更强磁饱和、病态电感矩阵、密集开关事件和更大 EMT 网络。

**3 句话。**  
作者用“两块异质积分 + 中点再耦合”在稳定性和 FPGA deadline 之间找到一个工程折中。  
证据覆盖离线 Simulink、静态原型波形、动态 HIL、谱半径和 FPGA 资源，但只围绕一套 WPT 系统。  
因此它是可信的特定案例 solver 实现，不是已经建立通用适用域的 EMT 平台。

**1 句话。**  
这篇论文的核心贡献是：用一个可在 FPGA 上交替执行的半步 IMEX 耦合，把传统解耦的整步延迟换成中点同步，从而在 75 ns 下同时保住目标 WPT 案例的稳定性和实时性。

## § 9 — 最脆弱的假设

最脆弱的假设是：**磁耦合 NL 块可以在 75 ns 下始终安全地显式推进，而且当前电感矩阵既可逆又足够良态，于是系统的主要刚性可以留给 PWL 隐式块承担。**

这个假设一旦失效，核心机制会直接失效，而不只是精度略降。式 (3) 需要对位置、电流相关的 \(\boldsymbol M\) 求逆；若线圈错位、饱和或某个组合使 \(\Delta\) 接近零，固定 64-bit/24-integer-bit 表示会放大误差。即使矩阵不奇异，若磁饱和、磁滞、涡流或多个切换事件让 NL 动力学在一个步内比论文轨迹快得多，\(|z_0+1|<1\) 的显式条件可能不成立；PWL 块的隐式稳定性救不了 NL 块。[pdf:E05]（PDF 物理页 4，式 (3)）[pdf:E07]（PDF 物理页 5，式 (10)–(11)）

论文给出的支持是：26 个有限元位置点描述了目标线圈错位轨迹；在该 350 kW 系统、给定参数和 75 ns 步长下，IMEX 对 Simulink、原型静态波形和动态 HIL 都表现良好。[pdf:E03]（PDF 物理页 2，Section II-A）[pdf:E11]（PDF 物理页 7，Fig. 7、Table II）缺失的证据则更关键：没有报告 \(\boldsymbol M\) 条件数、LUT 插值误差、current-dependent 饱和曲线、定点 word-length sweep、步长裕度在参数不确定性下的最坏值，也没有动态原型对照。因此论文证明了一个工作点族，而没有证明一个可审计的安全适用域。

## § 10 — 最小复现实验

一周内最值得复现的是“中点第二阶段是否在固定计算预算下真正扩大稳定域”，而不是复刻整套 350 kW HIL。

**数据。** 使用论文式 (6)–(9)、Fig. 9(a) 的 NL/PWL 简化分块和 Table I 中可取得的 \(C_{s1},C_{f1},L_{B11}\) 等参数；因 \(R_{\mathrm{on}},R_L\) 等简化电路参数未完整报告，明确记录所选代表值。再用一个可控的 \(L_{s1}(t)\) 或 \(M(t)\) 轨迹模拟线圈移动。不要从 Fig. 1(c) 曲线估读所谓“精确 26 点数据”。

**实现。** 在 double precision 中实现三种离散器：只保留 Stage 1 的 latency-based 方法、完整式 (6)–(9) IMEX、以及高精度 implicit reference。对固定拓扑先直接构造离散矩阵，再加入一次位置变化和一次开关事件。

**测量。**

- 步长从 20 ns 扫到 150 ns，计算每种方法离散矩阵谱半径；
- 对平滑段做 \(h, h/2, h/4\) 收敛率，检查 IMEX 是否接近二阶；
- 记录开关事件前后最大状态误差、能量残差与是否发散；
- 把 IMEX 运算量折算为论文的两阶段交替 schedule，确认没有把两个阶段误算成同一 75 ns 窗口内串行完成。

**支持标准。** 在一组不是只调出来的参数上，latency-based 谱半径大于 1 而 IMEX 在约 75 ns 附近小于 1；平滑段 IMEX 呈二阶收敛；事件处误差有界。**反驳标准。** IMEX 与 latency-based 在相同分块下稳定域没有实质差别，或 IMEX 在 75 ns 附近同样发散，或所谓二阶只在不含事件的理想段成立而事件误差主导全局结果。这个最小实验验证积分机制，不验证 FPGA 资源数字和完整 WPT 精度。

## § 11 — 最强反例设计

最强反例不是再换一个普通 WPT 参数，而是专门把论文留给显式块的风险推到极限：构造一条接收线圈运动与电流轨迹，使 \(\boldsymbol M\) 的最小特征值迅速下降、\(\kappa(\boldsymbol M)\) 急剧上升，同时让开关拓扑在同一个 75 ns 步内变化。可以在保留 PWL 部分原参数的情况下，加入 current-dependent saturation，使 \(L_p,L_{s1},L_{s2},M_1,M_2\) 不再只是平滑位置 LUT。

对照应包括高精度全隐式 DAE reference、double-precision IMEX 和论文 64-bit fixed-point IMEX。扫描错位、饱和深度、开关相位和步长，测量：

- \(\Delta\)、\(\kappa(\boldsymbol M)\) 与定点电流误差的关系；
- 是否出现饱和、溢出、符号翻转或非物理能量增长；
- 75 ns 下的谱半径/非线性扰动增益；
- 是否能在不增加非线性迭代的前提下恢复稳定。

如果 double-precision IMEX 仍稳而 fixed-point 版本失稳，论文的硬件数值表示缺乏鲁棒性；如果两者都失稳而全隐式 reference 稳定，则直接反驳“PWL 隐式块足以承载主要刚性”的核心假设。这个反例比“换一块 FPGA”更有力，因为它攻击的是 IMEX 分裂本身，而不是工程实现细节。

## § 12 — Follow-up Research Idea

在电力电子、实时仿真和控制领域，高影响工作通常不仅需要更小的名义步长，还要给出数值稳定性、真实硬件 deadline、参数与事件覆盖、可复现的误差边界，以及对实际控制器测试的增量价值。基于这一评价标准，一个非增量的候选方向是：**把固定 NL/PWL 分块求解改写为“带实时 deadline 的条件数与能量约束求解”——运行时监测磁耦合块的条件数、显式稳定裕度和端口能量残差，并在风险升高时切换分块或局部积分策略，同时保持可证明的最坏执行时间。**

**(a) 未满足的需求。** 现有论文只证明固定分块在一个目标系统上工作，不能告诉 HIL 使用者何时结果仍可信。真正需要的是一个在线可观测的 validity envelope：不仅保证每步按时完成，还能在接近病态耦合、磁饱和或密集事件时给出“仍可信/需降步长/需改用局部隐式”的判据。

**(b) 研究价值。** 这把目标从“在某案例跑到 75 ns”改成“在硬 deadline 下提供可审计的数值安全包络”。如果能同时给出稳定证明、WCET（worst-case execution time）和真实 HIL 故障注入验证，它对 EMT 实时仿真平台和控制器认证都比单纯再缩短步长更有价值。

**(c) 可借鉴工具。** 可以借鉴 passivity-based co-simulation 的端口能量监测、switched/DAE 系统的 multiple-Lyapunov 或 contractive-step 判据、mixed-precision error estimator，以及 real-time systems 的 WCET 调度分析。这里的关键不是增加一个“AI 模块”，而是把数值风险量变成硬件可计算的 runtime contract。

**(d) 第一个证伪实验。** 在论文 WPT 模型上系统扫描 \(\kappa(\boldsymbol M)\)、饱和深度、开关相位和速度，同时施加固定 75 ns deadline。若监测量不能在失稳或超差之前稳定预警，或 fallback 的最坏执行时间不能闭合 deadline，这个想法立即被证伪。

**(e) 与本文的实质区别。** 本文固定地把磁耦合设为显式 NL 块，把其余电路设为隐式 PWL 块，并用一个中点消除接口延迟；候选方法把“分块是否仍安全”本身变成实时状态，并要求数值有效性与执行时间共同可证明。由于本任务未检索输入 PDF 之外的完整相关工作，这只是证据约束下的候选研究方向，不声称 novelty。
