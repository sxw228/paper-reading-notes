# Detailed Magnetic Equivalent Circuit Based Real-Time Nonlinear Power Transformer Model on FPGA for Electromagnetic Transient Studies

- 作者：Jiadai Liu；Venkata Dinavahi
- 出处：*IEEE Transactions on Industrial Electronics*, Vol. 63, No. 2, 2016
- DOI：10.1109/TIE.2015.2477487
- Zotero key：WANJHN6H

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“能否在实时仿真器里放一个变压器模型”，而是更苛刻的问题：能否把绕组与铁心几何所决定的主要磁通路径、饱和、磁滞和频率相关涡流同时保留下来，又把整套非线性磁网络与电力系统网络在足够小的步长内实时求完。作者指出，EMT 会给变压器部件施加严重应力；若忽略相间耦合、饱和、剩磁、磁滞和涡流，就可能错估暂态过电压，继而影响保护策略、控制器整定和补偿设备额定值。[pdf:E01]

这个问题的重要性来自一个直接的工程矛盾。BCTRAN 一类集总参数模型快，但不保留详细几何；3-D FEM 能看见局部磁通与饱和，却因计算量过大而不适合重复 EMT，更不用说闭环 HIL。作者的目标是把两者之间的空白填上：以接近有限元网格思路的高分辨率磁等效电路（high-resolution magnetic equivalent circuit, HR-MEC）保留主要物理路径，再用 FPGA 的确定性并行计算获得实时性。[pdf:E01][pdf:E02]

论文直接声称，最终模型以 32-bit floating point VHDL 实现，磁滞采用 Preisach theory，涡流采用 frequency-dependent network，并用 JMAG 3-D FEM 验证。[pdf:E01] 这使工作的价值不只在“跑得快”，还在于它试图把局部磁状态、系统级 EMT 和可接入保护/控制硬件的实时执行放进同一模型。

## § 2 — 前人工作与不足

论文把既有方案分成三层。第一层是 BCTRAN 等集总电路模型：它们为了 EMT 速度省略详细变压器几何，因此难以表达局部磁通路径和铁心内部非线性。第二层是 2-D/3-D FEM：几何与场分布最完整，但反复暂态计算的负担即使离线也很重。第三层是 topology-based MEC，包括 duality-based、geometry-based UMEC，以及结合两者的 XFMR；其中 UMEC 已进入 PSCAD/EMTDC，XFMR 进入 ATPDraw。[pdf:E02]

最接近本文目标的是 RTDS 上的实时 UMEC。论文指出，该实现使用预计算的分段线性“磁通—MMF”饱和曲线，会产生需要补偿电路抑制的数值振荡，并省略磁滞和涡流；验证对象还是离线 PSCAD/EMTDC UMEC，而不是更细的 3-D FEM。[pdf:E03] 因此，缺口不是一句泛泛的“前人没考虑非线性”，而是：一旦几何磁网络的 permeance 随时间变化，系统 admittance 就必须每步更新和求解；传统顺序处理器很难同时负担详细磁模型、矩阵重构与网络求解。[pdf:E02][pdf:E05]

本文相对这些工作的实质推进是把四件事合并：细分绕组与漏磁支路的 HR-MEC、Preisach 磁滞、四段 Cauer 涡流网络，以及为时变矩阵设计的 sparse matrix 与 LU 硬件流水线。作者还明确把“低延迟带来更小 EMT 步长”和“3-D FEM 多工况验证”列为贡献。[pdf:E03] 但论文没有给出与 RTDS-UMEC 或 BCTRAN 在相同硬件、相同工况下的端到端 accuracy/latency 对照，因此它证明的是方案可行与对 FEM 的局部一致性，而不是对全部既有实时模型的全面优越性。

## § 3 — 重建作者的思考路径

在不预设本文方案的情况下，可以把作者的路径重建为以下链条。

1. EMT 保护研究需要暂态电流、电压，也需要知道这些量为什么因局部饱和、漏磁和剩磁而变化；单一集总支路无法给出足够的局部磁状态。[pdf:E01][pdf:E02]
2. 直接反复跑 3-D FEM 太慢。论文的 FEM 基线后来显示，一个 4 s、步长 \(500\,\mu s\) 的仿真在 Intel i7、8 GB PC 上接近 13 h，这说明不能只做“更快的 FEM 求解器”。[pdf:E15]
3. MEC 已经提供了介于电路和场之间的语言：Ampere/Gauss law 对应电路中的 KVL/KCL，铁心与空气磁路分别用非线性、线性 permeance 表达。自然的下一步是沿主要磁通路径细分线圈，而不是把整个绕组压成单个磁支路。[pdf:E03][pdf:E04]
4. 细分后，数值负担集中成固定 sparsity pattern、但数值每步变化的矩阵运算。FPGA 适合把固定依赖图做成并行流水线；因此，先开发 sparse-dense multiplication 与 MAC，再把每步的磁网络更新、逆矩阵、网络 LU 分解排入 FSM，是从计算结构而非单纯算力出发的选择。[pdf:E06][pdf:E10][pdf:E11]
5. 只表达饱和仍不足以解释涌流与频率成分，于是把 Preisach minor-loop memory 和 Cauer \(R\!-\!L\) 网络嵌入同一磁模型；最后用 3-D FEM 与系统级故障工况分别检验物理精度和实时执行。[pdf:E07][pdf:E08][pdf:E15]

这是“先选中间物理抽象，再让硬件结构追随方程依赖”的路线，而不是先有 FPGA 再寻找可并行任务。

## § 4 — 核心 Intuition

核心直觉是：不必实时重算完整电磁场，只要把决定暂态的主要磁通通道离散成足够细的磁网络，就能保留比集总模型更多的局部非线性；再把该网络每步都要做的稀疏矩阵运算固化为 FPGA 流水线，就可能在实时预算内更新它。[pdf:E03][pdf:E04] Preisach 模型为磁状态增加路径记忆，Cauer 网络为涡流增加频率依赖，二者共同避免把铁心非线性压缩成一条无记忆的分段饱和曲线。[pdf:E07][pdf:E08]

## § 5 — 具体方法与完整 Pipeline

以三相三柱变压器从合闸到涌流为例，完整 pipeline 如下。

1. **输入与磁网络建模。** 输入包括三相一次、二次绕组电流、上一步磁通与 history terms，以及变压器几何和绕组匝数。每个绕组被分成若干 subcoils；每个 subcoil 对应 winding branch 上的 MMF 与非线性铁心 permeance，同时配置并联的线性 leakage permeance，yoke 与 zero-sequence 路径也显式进入 HR-MEC。论文示例每相一次、二次绕组各分成两组 subcoils。[pdf:E03][pdf:E04]
2. **更新铁心非线性。** Preisach hysteresis unit（PHU）根据 magnetization current、当前 major/minor loop 方向和 reversal point 更新每个非线性支路的磁通，再由 \(P_k=\phi_k^M/(i_{mk}N_k)\) 得到新的 permeance。[pdf:E07][pdf:E08]
3. **加入频率相关涡流。** 磁滞 HR-MEC 与四段 Cauer \(R\!-\!L\) ladder 耦合；离散后的 eddy-current Norton network 更新自己的 history current。论文称四段足以在最高 200 kHz 内把误差控制在 5% 以下，但这句话依赖文献 [18] 的参数确定方法。[pdf:E08][pdf:E09]
4. **形成变压器 Norton 等效。** HR-MEC 的磁通—MMF 关系与 Faraday law 经 trapezoidal rule 离散后，变成端口形式
   \[
   \mathbf i_T(t)=\mathbf Y_T(t)\mathbf v_T(t)+\mathbf I_{\mathrm{hist}T}(t).
   \]
   因为 nonlinear permeance 每步变化，\(\mathbf Y_T(t)\) 也必须每步重算。[pdf:E05]
5. **映射到 FPGA。** 固定 sparsity pattern 的矩阵通过 SMxDM 单元访问三组 RAM；MAC 用一个 floating-point multiplier、float-to-fixed/fixed-to-float 转换和交替复位的两个 fixed-point adders 维持流水线。作者解释，fixed-point adder 只用于单周期累加，结果再转回 floating point 参与后续计算。[pdf:E06][pdf:E07]
6. **系统网络推进。** Supervisor FSM 在 \(S_1\) 并行更新 flux/history terms，在 \(S_2\) 更新 \(\phi_{\mathrm{hist}}^M\) 与 nonlinear permeance，在 \(S_3\) 顺序计算 \(\mathbf P,\mathbf Z,\mathbf Z_{\mathrm{HR-MEC}}\)，在 \(S_4\) 求逆，在 \(S_5\) 形成 \(\mathbf I_{\mathrm{hist}T},\mathbf Y_T\)，在 \(S_6\) 组装全网 \(\mathbf Y,\mathbf I_{\mathrm{hist}}\)，最后在 \(S_7\) 用 LU、forward substitution 和 backward substitution 解节点电压。[pdf:E10][pdf:E11]
7. **输出。** 输出为当前 EMT 步的网络节点电压、变压器端口量、磁通与新的 history terms；电压既回送各子模型，也可经 DAC 在示波器显示。[pdf:E10]

论文展示了 source、switch、distributed-parameter line 与三个 HR-MEC transformers 的系统接口，但未报告开关事件插值、multi-rate 时间推进或自适应步长；因此不能把图中的 switch module 外推成已验证的 sub-step event handling。[pdf:E10][pdf:E13]

## § 6 — 核心数学推导

先补一个物理直觉。电路中电流受 KCL 约束、回路电压受 KVL 约束；对应到 MEC，磁通满足 Gauss law 的节点守恒，MMF 沿磁路满足 Ampere law。若 \(\boldsymbol\phi\) 是支路磁通，\(\mathbf P\) 是支路 permeance 对角阵，\(\mathbf N\mathbf i\) 是绕组电流产生的 MMF，则论文先写出 Eq. (1)
\[
\boldsymbol\phi=\mathbf P\left(\mathbf N\mathbf i-\boldsymbol{\mathcal F}'\right),
\]
再以 \(\mathbf A^T\boldsymbol\phi=0\) 施加磁通守恒。消去 node MMF 后得到 Eq. (5)–(6)
\[
\boldsymbol\phi=\mathbf{\mathbb P}\mathbf P\mathbf N\mathbf i,\qquad
\mathbf{\mathbb P}=\mathbf I-\mathbf P\mathbf A(\mathbf A^T\mathbf P\mathbf A)^{-1}\mathbf A^T .
\]
这里 \(\mathbf{\mathbb P}\) 可以理解为把任意支路激励投影到满足磁通守恒的子空间；其关键代价是每步都要处理含时变 \(\mathbf P\) 的逆矩阵。[pdf:E04]

把含 MMF source 的 12 个分支挑出来，作者得到 Eq. (8)
\[
\boldsymbol\phi^M=\mathbf{\mathbb P}^{MM}\mathbf P^M\mathbf N^M\mathbf i^M ,
\]
其中 \(\boldsymbol\phi^M,\mathbf i^M\) 是 \(12\times1\) vectors，\(\mathbf P^M,\mathbf N^M\) 是 \(12\times12\) diagonal matrices。Faraday law 将这些分支磁通的导数映射成六个端口电压：\(\mathbf v_T=\mathbf N_Z\,d\boldsymbol\phi^M/dt\)，\(\mathbf N_Z\) 为 \(6\times12\) winding-turn matrix。[pdf:E04]

对 Faraday law 用 trapezoidal rule，Eq. (12)–(13) 为
\[
\mathbf N_Z\boldsymbol\phi^M(t)=\frac{\Delta t}{2}\mathbf v_T(t)+
\boldsymbol\phi_{\mathrm{hist}}^M(t),
\]
\[
\boldsymbol\phi_{\mathrm{hist}}^M(t)=\frac{\Delta t}{2}\mathbf v_T(t-\Delta t)+
\mathbf N_Z\boldsymbol\phi^M(t-\Delta t).
\]
再定义 \(\mathbf Z=\mathbf N_Z\mathbf{\mathbb P}^{MM}\mathbf P^M\mathbf N^M\)，并把同一绕组的 subcoil 项合并为 \(6\times6\) 的 \(\mathbf Z_{\mathrm{HR-MEC}}\)，得到 Eq. (20)–(22)
\[
\mathbf i_T=\mathbf Y_T\mathbf v_T+\mathbf I_{\mathrm{hist}T},\quad
\mathbf I_{\mathrm{hist}T}=\mathbf Z_{\mathrm{HR-MEC}}^{-1}\boldsymbol\phi_{\mathrm{hist}}^M,\quad
\mathbf Y_T=\frac{\Delta t}{2}\mathbf Z_{\mathrm{HR-MEC}}^{-1}.
\]
物理上，这一步把“有内部磁记忆的非线性器件”压成了当前步可插入系统节点方程的 Norton source；数值上，它把全部风险集中到每步 \(\mathbf Z_{\mathrm{HR-MEC}}\) 的可逆性与条件数。[pdf:E05]

铁心磁滞由 Eq. (23) 的 hyperbolic major-loop template 表达：
\[
\phi_{p\_m}(i_m)=\frac12\sum_{u=1}^{3}a_u\left[\tanh(b_ui_m)+c_u\,\mathrm{sech}^2(b_ui_m)\right].
\]
minor loops 则以 reversal point \((i_r,\phi_r)\) 和函数 \(K\) 生成 upward/downward trajectories，最后用 Eq. (26) 把磁通与 magnetization current 还原成各支路 permeance。[pdf:E07][pdf:E08] 论文没有在正文或 Appendix 给出 \(a_u,b_u,c_u\) 的数值，也未给出四段 Cauer 的具体 \(R,L\) 值；这限制了独立的逐数值复现。

涡流网络离散后同样成为 Norton form：
\[
\mathbf i_E=\mathbf Y_E\mathbf v_E+\mathbf I_{\mathrm{hist}E},\qquad
\mathbf I_{\mathrm{hist}E}(t)=\mathbf G_E\mathbf v_E(t-\Delta t)+\mathbf I_{\mathrm{hist}E}(t-\Delta t),
\]
\[
\mathbf G_E=\mathrm{diag}\!\left\{\frac{\Delta t}{2L_1},\frac{\Delta t}{2L_2},
\frac{\Delta t}{2L_3},\frac{\Delta t}{2L_4}\right\}.
\]
这说明 Cauer branches 的动态通过 history currents 保留下来，而不是每步做频域变换。[pdf:E09]

全网最终满足 Eq. (30) \(\mathbf Y\mathbf v=\mathbf i-\mathbf I_{\mathrm{hist}}\)。作者不显式形成 \(\mathbf Y^{-1}\mathbf b\)，而是用 \(\mathbf Y=\mathbf L\mathbf U\) 和 Eq. (32)–(36) 的逐列、逐行更新完成 LU factorization；对 HR-MEC 内部所需的逆矩阵，则只对矩阵分解一次，再依次以 identity matrix 的各列为右端，通过 forward/backward substitutions 生成逆矩阵各列。[pdf:E11][pdf:E12][pdf:E13]

## § 7 — 实验设计与结论

**问题 1：HR-MEC 能否再现高饱和下的局部磁场与涌流？** 作者在 JMAG Designer 中建立 187.5 MVA 三相变压器的 3-D FEM；半模型网格尺寸为 0.15 m，共 37,750 elements、7,753 nodes，Newton–Raphson 每步最多 50 iterations，一次侧三相电压供电、二次侧开路。[pdf:E15] FEM 在 phase-c current peak 时给出局部磁通分布，phase-c limb 最饱和、最大 flux density 接近 2.6 T；这与 phase-c 涌流更高的方向性解释一致。[pdf:E13][pdf:E15] 但它证明的是一个指定变压器、一个网格与一组参数下的相符性。

**问题 2：方法是否满足实时预算，硬件代价是什么？** 系统在 Xilinx Virtex-7 VC707 XC7VX485T 上运行，最高 clock frequency 90 MHz；一次时间步为 3,000 cycles，即 34 \(\mu s\)，每步 5,816 floating-point operations，作者报告 0.17 GFLOPS。[pdf:E16] Table I 显示 HR-MEC module 本身占 79,160 slice registers（13%）、122,255 slice LUTs（40.3%）、85 BRAM/FIFO（2.8%）和 746 DSP48E1（26.6%），并实例化 147 adders、146 multipliers、34 dividers；network solver 另占 15,996 registers、26,221 LUTs 和 151 DSP48E1。[pdf:E14] 因而“实时”是由实际 FPGA latency 支撑的，但论文没有报告 place-and-route margin、多个不同规模 HR-MEC 的 scaling curve 或 closed-loop external controller 的实测延迟。

**问题 3：涌流与稳态波形是否接近 FEM？** 合闸前 \(SW_1,SW_2\) 均断开，\(SW_1\) 在 \(t=0.05\,s\) 合闸。Fig. 14 显示 real-time 与 JMAG 的三相 inrush shape 接近，电流约在 3.5 s 后进入稳态；暂态中 2nd、3rd harmonics 相对更突出，稳态由 fundamental 主导。[pdf:E17][pdf:E18] 作者报告 phase-c first-order component 的最大差异在暂态、稳态分别为 9% 和 11%。[pdf:E18] 这里不能把“波形接近”外推成全频带误差小：论文只给了特定窗口与 harmonic-order comparison，也承认幅值存在偏差。

**问题 4：系统级故障暂态能否实时推进？** 作者在 \(t_1=2\,s\) 对 \(T_2\) secondary winding 施加 three-phase ground fault，并在 \(T_3\) primary 捕获电压、电流。Fig. 15 显示两者强烈畸变；电压幅值最高为 steady-state voltage 的 121%，三相电流不平衡，并在 \(t_2=2.16\,s\) 后衰减回稳态。[pdf:E19] 这证明模型能在给定网络内连续跑过故障，但该工况没有同步给出 FEM 或实验硬件的 fault waveform baseline，故不能据此单独量化故障精度。

**问题 5：相对 3-D FEM 的速度差异有多大？** JMAG 在 Intel i7、8 GB PC 上跑 4 s、\(\Delta t=500\,\mu s\) 的仿真接近 13 h；FPGA HR-MEC 的步执行时间为 34 \(\mu s\)。[pdf:E15][pdf:E16] 这显示了强烈的执行时间差异，但两者模型分辨率与步长不同，因此不能把两数字直接相除后称为严格 speedup。

## § 8 — Take-aways

**5 句话。** 第一，论文用细分磁路而非完整场网格，在“集总 EMT 太粗、3-D FEM 太慢”之间建立了一个能保留局部磁通路径的中间模型。[pdf:E03][pdf:E04] 第二，trapezoidal discretization 把非线性 HR-MEC 变成每步更新 admittance 的 Norton equivalent，使它能嵌入标准节点分析。[pdf:E05] 第三，Preisach 与四段 Cauer network 分别保留磁滞记忆和频率相关涡流，而 sparse matrix、pipeline 与 LU solver 把这些计算落到 FPGA。[pdf:E08][pdf:E10][pdf:E12] 第四，Virtex-7 上 90 MHz、3,000 cycles 对应 34 \(\mu s\) 一步，涌流相对 FEM 的最大 phase-c fundamental differences 为 9% 和 11%。[pdf:E16][pdf:E18] 第五，成果很有工程启发性，但单一变压器验证、缺少关键磁滞/Cauer 参数和初始磁通的数值规避，使“可迁移的准确性”尚未被充分证明。

**3 句话。** 这篇论文的真正贡献是把详细磁物理、EMT Norton interface 与 FPGA matrix pipeline 共同设计，而不是单独提出某个磁滞公式。它用 FEM 与硬件时序证明了一个有吸引力的 accuracy–latency operating point，却没有证明该点在不同铁心、剩磁状态和规模下仍稳定。后续工作最值得追的是结构保持的初始化与求解，而非继续简单增加磁支路数量。

**1 句话。** HR-MEC 说明“足够细的物理网络 + 面向依赖图的 FPGA 并行”可以逼近 FEM 暂态并进入实时步长，但其可信边界取决于磁状态初始化、参数辨识和矩阵可逆性。

## § 9 — 最脆弱的假设

最脆弱的假设是：**HR-MEC 的磁状态可以被初始化为既物理可信、又使 \(\mathbf A^T\mathbf P\mathbf A\) 与 \(\mathbf Z_{\mathrm{HR-MEC}}\) 在每个时间步保持可逆的状态。** 这是 failure cost 最大的假设，因为一旦不成立，问题不是误差略增，而是 Eq. (6)、(21)、(22) 所需的 inverse 无法形成，整个 EMT 步不能推进。[pdf:E04][pdf:E05]

论文自己给出了这个风险的直接证据：在 HR-MEC 中若各 limb initial flux 全为零，则 \(\mathbf P\) entries 全为零，\(\mathbf A^T\mathbf P\mathbf A\) 不可逆；作者因此把 initial fluxes 设为接近零的很小值，而 FEM 从严格零磁通开始。作者把这列为涌流幅值偏差的一个原因，另一个原因是 HR-MEC mesh 远粗于 3-D FEM。[pdf:E18] 这不是普通的 implementation detail，而是数值可解性迫使物理初态被修改。

论文缺少三类证据：没有给“小值”的具体量级；没有给对该量级的 sensitivity sweep；也没有在有 residual flux、不同 reversal history 或深饱和下报告 condition number 与失败率。因此，“基于证据的推断”是：本文的 9%/11% difference 可能同时包含空间离散误差、参数误差与初始化偏置，现有实验无法把三者分开。这个推断不是作者的明确结论。

## § 10 — 最小复现实验

一周内最值得做的不是复刻全部 VHDL，而是复现并证伪“初始化后 HR-MEC 能稳定、准确地给出涌流”这一核心环节。

1. **数据。** 使用 Appendix 的三柱铁心几何：limb length 3.59 m、limb/yoke cross-sectional area 0.454 \(m^2\)、yoke length 2.66 m；energization source 130.6 kV，\(T_1=187.5\) MVA、65/450 kV。[pdf:E20] 从 Fig. 14 数字化三相 inrush envelope 与稳态区间，作为论文结果的可见比较对象。[pdf:E17]
2. **实现。** 在 MATLAB 或 Python 中实现 Fig. 2 的两组 subcoils HR-MEC、Eq. (5)–(22) 的 trapezoidal/Norton update，以及 Eq. (23)–(29) 的 Preisach/Cauer 结构。[pdf:E04][pdf:E05][pdf:E07][pdf:E09] 由于论文未给 \(a_u,b_u,c_u\) 与具体 \(R,L\)，必须用一组明确公开来源的 B–H/损耗数据自行拟合，并把这一步标为“结构复现”，不能冒充作者数值的 exact reproduction。
3. **变量扫描。** 对 initial flux epsilon 做 \(0,10^{-12},10^{-10},\ldots,10^{-3}\) p.u. 扫描，并加入三组满足磁通守恒的 residual-flux vectors；每步记录 \(\kappa(\mathbf A^T\mathbf P\mathbf A)\)、\(\kappa(\mathbf Z_{\mathrm{HR-MEC}})\)、是否求解失败、三相 inrush peak/decay time 与 harmonic spectrum。
4. **支持标准。** 若在跨至少六个数量级的非零 epsilon 和物理可行 residual flux 下都不失败，且选定参数后 Fig. 14 的三相波形形状、3.5 s 衰减与 harmonic ordering 稳定，才支持“核心结构不是由特定 epsilon 偶然撑住”。[pdf:E18]
5. **反驳标准。** 若零/小 epsilon 使 inverse 失败或 condition number 急剧放大，或仅极窄 epsilon 区间能得到接近 Fig. 14 的结果，则应反驳模型对初态不敏感这一隐含前提。若把步长降到论文 34 \(\mu s\) 仍不能改变该结论，问题更可能在状态表示而非时间离散。[pdf:E16]

这个实验不验证完整 FPGA latency，也不验证作者未公开参数的 absolute accuracy；它以最低成本隔离了论文最脆弱、且最可能决定 HIL 可信度的数值机制。

## § 11 — 最强反例设计

最强反例不是把频率推到论文承诺之外，而是构造**物理上合理的 residual-flux 与合闸角组合，使任一磁柱从有记忆的 minor loop 进入深饱和，同时逼近 HR-MEC 的奇异边界**。真实变压器在重合闸前不会普遍处于“各磁通几乎为零”的状态；Preisach 模型本来就用于保存 reversal history，因此剩磁恰好是方法必须处理、不能排除的输入。

实验可以这样设计：在满足 Gauss flux constraint 的 residual-flux manifold 上生成从 \(-0.8\) 到 \(+0.8\) p.u. 的成组初态，对每组扫描三相合闸角；以高分辨率 3-D FEM 或实测可编程电源/小型三柱变压器为基线，同时运行 HR-MEC。测量 solver failure、matrix condition number、first-cycle peak、各相 DC offset、2nd/3rd harmonics 和局部 peak flux density。Fig. 11 所示 phase-c 接近 2.6 T 的饱和状态与 Fig. 14 的强非对称 inrush 提供了这一攻击的目标区间。[pdf:E13][pdf:E17]

若 HR-MEC 只能通过人为夹紧 permeance 或把 residual flux 拉回 epsilon 才能求解，或者在 residual-flux 某一方向上相对 FEM 的 peak/current polarity 系统性错误，那么“能准确预测 transient- and steady-state transformer behavior”的核心结论就被实质挑战。[pdf:E20] 相反，若它在整个 manifold 上保持可解并保持误差界，才真正补上现有论文没有做的鲁棒性证据。

## § 12 — Follow-up Research Idea

**候选研究方向：以磁通守恒流形为状态空间的 passivity-preserving HR-MEC，而不是靠每步显式逆矩阵和 epsilon 初态维持可解性。** 这是基于本文证据提出的候选判断，尚未进行充分相关工作检索，因此不声称 novelty。

（a）未满足的需求是：闭环 HIL 不仅要求平均 34 \(\mu s\) latency，还要求所有物理可达 residual-flux/history 状态都可初始化、可求解，并且在多台 transformer 组合后不引入数值能量。[pdf:E16][pdf:E18] （b）这可能产生本领域认可的价值，因为它把评价目标从“一个工况下比 FEM 快”改成“在物理状态全集上给出可验证的 solvability、passivity 和 error bound”，直接服务保护测试的可信度。（c）可借鉴 descriptor systems/DAE 的 constraint-preserving integration、port-Hamiltonian modeling、passivity-preserving model reduction，以及稀疏图上的 null-space coordinates：先在 \(\mathbf A^T\boldsymbol\phi=0\) 的子空间选独立 flux states，再由 constitutive laws 计算电压电流，避免每步通过 \((\mathbf A^T\mathbf P\mathbf A)^{-1}\) 投影。[pdf:E04]

（d）第一个能证伪它的实验，就是第 11 节的 residual-flux × closing-angle sweep：在相同 HR-MEC 分辨率、相同 Preisach/Cauer 参数和相同 34 \(\mu s\) 步长下，把原方法与 constraint-state 方法对照；若新方法没有降低 failure rate/condition number，也没有保持或改善相对 FEM 的 peak/harmonic error，则这个研究方向的核心机制不成立。（e）它与本文工作的实质区别不是增加更多 subcoils 或换一块更快 FPGA，而是改变状态表示和成功标准：从“并行加速时变磁网络的逆与 LU”转向“先保证磁网络在所有物理初态下结构可解、无源且可组合，再做硬件并行”。本文 Fig. 8 的模块化接口和 Fig. 9 的 FSM 可继续复用，真正替换的是 HR-MEC 内部的状态推进与 matrix inversion boundary。[pdf:E10][pdf:E11]
