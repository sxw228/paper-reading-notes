# Simulation of Switched-Mode Power Conversion Circuits With Extended Impedance Method

作者：Yichao Liu、Yiming Gao、Junrui Liang

出处：IEEE Transactions on Circuits and Systems I: Regular Papers, Vol. 69, No. 9

年份：2022

DOI：10.1109/TCSI.2022.3178447

Zotero key：M786E779

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的是 switched-mode power converter 的稳态仿真问题：能否既保留开关瞬间、寄生器件和 CCM/DCM 切换等细节，又避免时域长时间积分以及每轮计算 Jacobian 或梯度所带来的代价。作者提出 extended impedance method（EIM），把传统只适用于单频 LTI 元件的“阻抗”扩展为谐波耦合矩阵，让 MOSFET、二极管等 LTV 或非线性器件也能在频域中和 R、L、C 一样进入 KCL/KVL 网络方程。论文的核心 claim 是，EIM 能从元件层面构造一般 switched-mode converter 的频域稳态模型，在保留开关附近高频特征的同时，以与 PSpice、ADS/HB 和实测相近的波形取得更低的计算代价。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，是因为电力电子设计中的损耗、效率、器件应力和工作模式通常取决于稳态周期波形，而不是只取一个平均工作点。状态空间平均法计算快，却会抹去一个开关周期内的细节；暴力时域仿真能给出细节，但必须跨越可能很长的 transient 才能抵达稳态。EIM 试图占据二者之间的位置：直接求周期稳态，又让高次谐波、二极管自动关断和结电容谐振留在模型里。[pdf:E01]（PDF 物理页 1，Introduction）

对 EMT/FPGA 读者，需要明确论文的边界。它研究的是单个 buck converter 的离线 frequency-domain steady-state analysis，不是电力系统级 EMT 实时仿真；论文没有报告离散时间步长、multi-rate 调度、定点位宽、FPGA 数据通路、片上资源、时序收敛或硬件实时执行。因此，它对 EMT/FPGA 的价值主要是提供一种“预先形成谐波耦合矩阵、直接求周期稳态”的模型思想，而不是已经完成的 FPGA solver。

## § 2 — 前人工作与不足

论文把既有路线分为三组。

第一组是时域方法。状态空间平均法把一个周期内的状态取平均，适合描述低频动态，但 DCM 的零电感电流区间需要额外的区间分析与 duty-ratio 约束；shooting method、Galerkin shooting、piecewise-linear 和 Volterra 等方法可以直接寻找稳态，但通常仍要处理未知初值、敏感度矩阵、非线性代数方程或较高计算维度。作者的判断不是“时域方法做不到”，而是它们为了保留详细波形，需要长 transient 或在迭代中求导，稳态求解代价高。[pdf:E01]（PDF 物理页 1，Section I）

第二组是频域方法。harmonic balance（HB）把网络分为线性和非线性部分，通过 mismatch 与 Newton-Raphson、relaxation 或 GMRES 等算法迭代；harmonic domain method（HDM）和 harmonic state-space（HSS）从时域 state-space 方程变换到截断 Fourier 系数。论文指出，HB 对非线性部分仍需反复计算梯度或 Jacobian；HDM/HSS 面向线性系统，当 passively-driven switch 或寄生非线性进入模型时不够直接。EIM 与 HSS 在 LTV Toeplitz 矩阵处有共同数学基础，但 EIM 坚持先在频域完成元件级建模，再用 KCL/KVL 组网，而不是回到 system-level state-space constitutive equation。[pdf:E02]（PDF 物理页 2，Introduction 与 Fig. 1）

第三组是 wavelet/hybrid 方法。wavelet 能比无限长的 Fourier basis 更局部地描述尖峰，但论文引用的实现中，basis 维数会随 wavelet level 指数增长，精度提高时计算代价仍然突出。论文的参考文献表也明确列出 averaging、shooting、piecewise-linear、Volterra、HB、HSS、wavelet 和早期 EIM 工作；这些是作者用于定位本工作的文献记录，而不是本卡重新核验后的领域共识。[pdf:E10]（PDF 物理页 10，References [8]–[34]）

本论文相对早期 EIM 的增量是把它系统地推广到 switched-mode power conversion：主动开关作为 LTV resistance，passively-driven diode 与结电容通过状态映射进入每轮迭代，并用同一组方程覆盖 CCM 与 DCM。作者同时声称可从 SPICE 模型取得半导体参数、用 gradient-free fixed-point iteration 求稳态，并在相似准确度下提升效率。[pdf:E02]（PDF 物理页 2，贡献列表）这篇论文没有做跨拓扑、跨功率等级或跨器件技术的系统比较，因此“general switched-mode circuits”主要是模型结构上的可推广性 claim，实验证据仍限于一个 buck 拓扑。

## § 3 — 重建作者的思考路径

可以从已有知识重建出如下路径，而不预设 EIM 已经成立。

首先，周期稳态允许把电压、电流写成 Fourier 系数；微分在频域变成乘以 \(jk\omega_0\)，所以周期微分方程有机会转化成代数方程。其次，普通阻抗法之所以简单，是因为元件方程和 KCL/KVL 可以直接组网；如果 time-varying resistance 与电流在时域相乘，那么频域中就是谐波卷积，卷积又可以写成 Toeplitz 矩阵乘法。于是一个自然问题出现：能否把“标量阻抗”升级成“谐波到谐波的矩阵”，让 LTV 元件也保留阻抗法的组网方式。[pdf:E03]（PDF 物理页 3，Section II-A，Eq. (1)–(11)）

接着会遇到真正的障碍：二极管、结电容等非线性器件的参数依赖电压或电流状态，而状态在求解之前未知。一个可行的工程近似是先猜状态，把本轮状态依赖映射成一条随时间变化的参数轨迹，再对这条轨迹做 Fourier transform，形成当前轮的 extended impedance/admittance；求出新状态后重复，直到变化量低于容差。这就是论文称为 state-to-time mapping（S2TM）的桥梁。[pdf:E04]（PDF 物理页 4，Section II-C–D，Fig. 2 与 Eq. (17)–(18)）

最后，若这个过程确实可用，就应该选一个同时包含主动开关、被动换流、CCM/DCM 和寄生谐振的最小 converter 来验证。buck converter 正好满足这些条件：MOSFET 由 PWM 主动驱动，二极管的关断时刻由状态决定，DCM 还有两开关均关断的第三区间。这样既能检查统一工作模式 claim，也能用 PSpice、HB 和示波器波形交叉比较。[pdf:E05]（PDF 物理页 5，Fig. 3–5 与 Section III）

## § 4 — 核心 Intuition

EIM 的核心 intuition 是：周期电路中，一个元件不必只有“某个频率上的标量阻抗”，它也可以是描述各阶谐波如何互相耦合的矩阵阻抗。非线性器件虽然不能一次写成固定矩阵，但可以在每轮把当前状态映射成 time-varying 元件，再更新它的谐波矩阵。这样，复杂开关网络仍可用熟悉的 KCL/KVL 组装，并用 fixed-point iteration 直接逼近周期稳态，而不必预先划分 CCM/DCM。

## § 5 — 具体方法与完整 Pipeline

以论文的 buck converter 为例，输入是 \(v_i\)、PWM duty cycle \(\xi\)、switching frequency \(f_s\)、RLC 与寄生 ESR，以及从 SPICE level-3 模型提取的 IRF510 和 1N4148 参数；输出是稳态的电压、电流 Fourier 系数、时域波形及由它们计算的平均功率和转换比。[pdf:E05]（PDF 物理页 5，Fig. 3–5）

1. **选择谐波基与初值。** 截断到 \(-K,\ldots,K\)，因此每个周期量用 \(2K+1\) 个 Fourier 系数表示；初始化目标电压、电流为零。论文两个工况都取 \(K=100\)、终止容差 \(\delta=10^{-10}\)。[pdf:E06]（PDF 物理页 6，Table II）
2. **建立 LTI 元件。** R、L、C 的矩阵是 diagonal；不同谐波之间不耦合，电感和电容的对角元素分别带 \(jk\omega_0L\) 与 \(1/(jk\omega_0C)\)。直流源只在零次谐波位置非零。[pdf:E04]（PDF 物理页 4，Eq. (13)–(16)）
3. **建立主动开关。** MOSFET 的 PWM switching path 被写成在 \(R_{\mathrm{on}}\) 与 \(R_{\mathrm{off}}\) 之间切换的 LTV resistance \(r_{\mathrm{sw}}(t)\)，其 Fourier 系数填入 Toeplitz extended impedance；并联的 \(c_{DS}\) 保留结电容非线性。[pdf:E05]（PDF 物理页 5，Fig. 5 与 Eq. (20)–(22)）
4. **建立被动二极管与结电容。** 二极管的 Shockley \(i\)-\(v\) 关系被重写成 conductance：正向区用电流作为自变量、反向区用电压作为自变量，以减小指数关系导致的迭代发散；\(c_D(v_D)\) 用电压相关 junction-capacitance model。每轮把 \(g_D\)、\(c_D\)、\(c_{DS}\) 的当前状态映射为 time-varying waveforms，再转换成 extended admittance matrices。[pdf:E06]（PDF 物理页 6，Eq. (23)–(25)）
5. **组装网络。** MOSFET 和二极管的 admittance 分别由其并联支路相加，随后对 Fig. 6 的节点进行频域 nodal analysis，形成 \(V_s,V_o\) 的 block-matrix equation。这里的计算依赖是全局谐波矩阵求解；论文没有报告稀疏存储、并行分块或多速率调度。[pdf:E06]（PDF 物理页 6，Fig. 6 与 Eq. (26)）；[pdf:E07]（PDF 物理页 7，Eq. (27)）
6. **fixed-point update。** 逆 Fourier transform 得到本轮时域状态，用它重算非线性元件轨迹；若目标状态的相对二范数变化低于 \(\delta\)，输出稳态，否则更新并进入下一轮。[pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. (17)–(18)）；[pdf:E05]（PDF 物理页 5，Eq. (19)）
7. **后处理。** 用 Parseval theorem 从 Fourier vectors 直接求平均功率与器件损耗，并用 \(M=v_o/v_i\) 分析 duty cycle 与 CCM/DCM 边界。[pdf:E08]（PDF 物理页 8，Eq. (28)–(30)）

具体参数方面，CCM 工况为 \(v_i=10\ \mathrm{V}\)、\(\xi=40\%\)、\(f_s=100\ \mathrm{kHz}\)、\(L=1.0\ \mathrm{mH}\)、\(r=7.3\ \Omega\)、\(C=10\ \mu\mathrm{F}\)、\(R=198.8\ \Omega\)；DCM 工况为 \(10\ \mathrm{V}\)、\(20\%\)、\(100\ \mathrm{kHz}\)、\(97.7\ \mu\mathrm{H}\)、\(0.6\ \Omega\)、\(220\ \mu\mathrm{F}\)、\(130.0\ \Omega\)。IRF510 模型采用 \(R_{\mathrm{on}}=0.47\ \Omega\)、\(R_{\mathrm{off}}=444.4\ \mathrm{k}\Omega\)、\(C_{j0}=366.5\ \mathrm{pF}\) 等参数；1N4148 采用 \(I_s=2.682\ \mathrm{nA}\)、\(n=1.836\)、\(V_T=26\ \mathrm{mV}\)、\(C_{j0}=4\ \mathrm{pF}\) 等参数。[pdf:E06]（PDF 物理页 6，Table I–II）

论文未报告程序语言、线性代数库、矩阵条件数、内存占用、adaptive harmonic selection、误差控制、定点数值格式、FPGA 映射、资源利用率、最高时钟频率或真实实时步长。因而不能从“0.10–0.16 s 的 PC 离线计算”外推出 FPGA real-time capability。

## § 6 — 核心数学推导（无形式化数学则跳过）

EIM 的数学起点是时域乘法变成频域卷积。对 time-varying resistor，

\[
v(t)=r(t)i(t),
\]

其第 \(k\) 阶 Fourier 系数满足

\[
V_k=\sum_{n=-\infty}^{+\infty}R_{k-n}I_n.
\]

截断到 \(-K\le k\le K\) 后，把 \(V_k,I_k\) 排成 \(2K+1\) 维向量，卷积就变成

\[
\mathbf V=\mathbf Z_R\mathbf I,
\]

其中 \(\mathbf Z_R\) 是由 \(R_{k-n}\) 组成的 Toeplitz matrix。直观上，\(\mathbf Z_R\) 的非对角元素表示“一个谐波的电流经过时变元件后，被搬移到另一个谐波的电压”；LTI 元件没有这种频率搬移，所以矩阵退化为 diagonal。[pdf:E03]（PDF 物理页 3，Eq. (1)–(6)）

对 LTV inductor 和 capacitor，时间微分在第 \(k\) 阶谐波上变成 \(jk\omega_0\)。因此它们同样能写成 extended impedance matrix；\(k=0\) 的微分项本来为零，论文用很小的 \(\varepsilon\) 防止矩阵奇异。这是数值正则化，不是物理元件参数，论文没有报告 \(\varepsilon\) 的具体取值或敏感性。[pdf:E03]（PDF 物理页 3，Eq. (7)–(11)）；[pdf:E04]（PDF 物理页 4，Eq. (12)–(15)）

非线性器件的关键不是一次性矩阵化，而是迭代：

\[
r\!\left[v_x^{(n)}(t),i_y^{(n)}(t)\right]
\xrightarrow{\mathrm{S2TM}}r^{(n)}(t)
\xrightarrow{\mathcal F,\mathrm{EIM}}\mathbf Z_R^{(n)}.
\]

把本轮全部 extended impedance/admittance 放入频域网络关系 \(\mathcal H[\cdot]\)，由 KCL/KVL 解出 \(\mathbf V_x^{(n+1)},\mathbf I_y^{(n+1)}\)，再逆变换回时域。这相当于构造映射 \(x^{(n+1)}=F(x^{(n)})\)；论文使用 fixed-point iteration，却没有证明 \(F\) 在一般 converter 上是 contraction。[pdf:E04]（PDF 物理页 4，Eq. (17)–(18)）

停止条件是若干目标电压和电流相对变化的加权和：

\[
\sum_x a_x\frac{\lVert\mathbf V_x^{(n+1)}-\mathbf V_x^{(n)}\rVert_2}
{\lVert\mathbf V_x^{(n+1)}\rVert_2}
+
\sum_y b_y\frac{\lVert\mathbf I_y^{(n+1)}-\mathbf I_y^{(n)}\rVert_2}
{\lVert\mathbf I_y^{(n+1)}\rVert_2}<\delta.
\]

buck case 只选 \(V_o\) 且权重为 1。这意味着“\(V_o\) 收敛”被用作整个网络稳态收敛的代理；论文没有报告对所有内部状态同时检查的结果。[pdf:E05]（PDF 物理页 5，Eq. (19)）；[pdf:E06]（PDF 物理页 6，Section III-B）

主动开关的 \(r_{\mathrm{sw}}(t)\) 是 \(R_{\mathrm{on}}\)/\(R_{\mathrm{off}}\) 的周期分段函数；其第 \(k\) 阶系数由 duty cycle \(\xi\) 的 sinc-like 项给出，从而形成 \(\mathbf Z_{\mathrm{sw}}\)。二极管则用 Shockley equation 和分段 conductance 映射避免某一方向上的指数扰动导致发散，结电容由 \(C_{j0}[1+v_D/V_{bi}]^{-m}\) 描述。[pdf:E05]（PDF 物理页 5，Eq. (20)–(22)）；[pdf:E06]（PDF 物理页 6，Eq. (23)–(25)）

网络层把 MOSFET 与二极管并联支路分别相加为 \(\mathbf Y_Q^{(n)}\) 和 \(\mathbf Y_D^{(n)}\)，再用 nodal admittance block matrix 求 \(\mathbf V_s^{(n+1)},\mathbf V_o^{(n+1)}\)。求得 Fourier vectors 后，平均功率由 Parseval theorem 写成

\[
\bar P=\frac{1}{T}\int_0^T v(t)i(t)\,dt
=\operatorname{Re}\!\left(\mathbf V^{\mathsf T}\mathbf I\right).
\]

这使损耗计算停留在频域；代价是有限 \(K\) 不能准确表示 switch instant 的电流尖峰，相关器件损耗会出现偏差。[pdf:E07]（PDF 物理页 7，Eq. (27)）；[pdf:E08]（PDF 物理页 8，Eq. (28) 与 power-loss discussion）

## § 7 — 实验设计与结论

- **问题：EIM 能否用同一模型覆盖 CCM 与 DCM，并还原主要波形？ → 实验：** 对 Table II 两套 buck 参数分别运行 EIM、PSpice 和 ADS/HB；HB 与 EIM 都取 \(K=100\)，再与示波器上的 \(v_o\) 和 \(i_L\) 比较。**→ 答案：** 三种模拟与实测主要波形一致；CCM 实测平均 \(v_o=3.56\ \mathrm{V}\)，DCM 实测 \(v_o=3.75\ \mathrm{V}\)。DCM 第三区间的 MOSFET/diode 同时关断后，电感与结电容谐振形成高频 ripple，包含 junction capacitance 的 EIM 能复现这一趋势。[pdf:E07]（PDF 物理页 7，Fig. 7–8 与正文）
- **问题：EIM 的稳态电压准确度是否达到既有仿真器水平？ → 实验：** 以 PSpice 平均 \(v_o\) 为 benchmark，比较 EIM 与 HB。**→ 答案：** CCM 中 EIM/HB 相对误差分别为 \(0.12\%/0.56\%\)；DCM 中为 \(0.05\%/1.62\%\)。这支持“在这两个 buck 工况下 EIM 不劣于所用 HB 配置”，但不支持跨拓扑的普遍误差上界。[pdf:E07]（PDF 物理页 7，结果正文）；[pdf:E08]（PDF 物理页 8，Table III）
- **问题：EIM 是否更快？ → 实验：** 三种仿真在同一台 Intel Core i7-9700 @ 3.00 GHz PC 上运行；CCM 中 EIM/PSpice/HB 用时 \(0.16/5.84/22.18\ \mathrm{s}\)，DCM 中为 \(0.10/19.56/55.52\ \mathrm{s}\)。**→ 答案：** Table III 报告 EIM 相对 PSpice/HB 的 speedup 为 CCM \(36/138\)，DCM \(195/555\)，分别经过 15 和 18 轮达到 \(\delta=10^{-10}\)。PSpice 的 stop time 和 maximum step 被人为设为保证稳态的 \(50.02/150.02\ \mathrm{ms}\) 与 \(50\ \mathrm{ns}\)，所以 speedup 是该配置下的结果，不是 solver-independent 定律。[pdf:E07]（PDF 物理页 7，Fig. 9 与 runtime setup）；[pdf:E08]（PDF 物理页 8，Table III）
- **问题：有限谐波是否足以支持功率与器件应力分析？ → 实验：** 比较 diode voltage/current、输入输出功率、效率和 MOSFET/diode/ESR loss breakdown。**→ 答案：** 整体效率接近，例如 CCM EIM/PSpice 为 \(84.7\%/84.0\%\)，DCM 两者均为 \(86.8\%\)；但 diode loss 偏差明显，CCM 为 \(0.7/1.2\ \mathrm{mW}\)，DCM 为 \(1.9/1.0\ \mathrm{mW}\)。作者把原因归于有限谐波无法准确刻画 switching instant 的 diode current spike。因此论文支持总功率近似，不支持所有器件 switching-loss 分量都高精度。[pdf:E08]（PDF 物理页 8，Fig. 10 与 Table IV–V）
- **问题：模型能否自动反映工作模式与 duty-cycle 关系？ → 实验：** 通过改变负载 \(R\) 改变 \(B=2Lf_s/R\)，扫描 \(\xi\)，比较理想曲线、EIM 和实验的 \(M=v_o/v_i\)。**→ 答案：** EIM 与实测总体吻合，包含 ESR 与导通电阻后能解释相对理想 \(M=\xi\) 的偏离；被动二极管状态在迭代中自动决定，无需事先标注 CCM/DCM。[pdf:E08]（PDF 物理页 8，Eq. (29)–(30)）；[pdf:E09]（PDF 物理页 9，Fig. 11 与 Section III-E）

论文没有报告统计重复次数、误差条、硬件测量不确定度、参数辨识误差、内存占用、矩阵求解时间分解、不同 \(K\) 的 convergence/accuracy 曲线、跨拓扑 benchmark 或 FPGA 实验。PDF 无 appendix；物理页 10 是 references 与作者简介，没有额外实验条件。[pdf:E10]（PDF 物理页 10）

## § 8 — Take-aways

**5 句话。**  
1. EIM 把周期 LTV 元件的谐波卷积写成 extended impedance/admittance matrix，使它们能与 LTI 元件一起用 KCL/KVL 组网。  
2. 非线性器件通过 S2TM 在每轮变成 time-varying 元件，再由 gradient-free fixed-point iteration 更新。  
3. 一个包含 MOSFET、diode、junction capacitance 与 ESR 的 buck case 表明，同一模型可以覆盖 CCM 与 DCM，并保留 DCM 第三区间的寄生谐振。  
4. 在论文给定配置下，EIM 的平均输出电压误差低于所用 HB，并比 PSpice/HB 更快。[pdf:E07]（PDF 物理页 7，结果与 runtime）；[pdf:E08]（PDF 物理页 8，Table III）  
5. 但 finite harmonics、单一 fundamental-frequency grid 和未保证收敛的 fixed-point iteration，分别限制尖峰精度、多频率效率和复杂网络鲁棒性。[pdf:E08]（PDF 物理页 8，switching-spike discussion）；[pdf:E09]（PDF 物理页 9，Section IV）

**3 句话。**  
1. EIM 的真正贡献不是另一个 buck 平均模型，而是把“元件阻抗”提升为“谐波耦合矩阵”，并用状态映射接纳非线性器件。  
2. buck 的 CCM/DCM 波形、平均电压、效率与计算时间验证了这个构造在两个工况下有效，但没有证明对一般 converter 都收敛或都更快。  
3. 对 EMT/FPGA，最值得带走的是 component-level harmonic assembly 思路，而不是尚未报告的实时硬件实现。

**1 句话。**  
EIM 用谐波矩阵与 fixed-point state mapping 直接求开关电路周期稳态，在论文的 buck 案例中又快又准，但其普适性仍受频率网格、谐波截断与收敛性约束。

## § 9 — 最脆弱的假设

最脆弱的假设是：由 S2TM、频域网络求解和非线性器件更新组成的 fixed-point map，在目标 converter 与给定初值下会收敛到物理上正确且唯一的周期稳态。如果这个假设不成立，EIM 不只是误差稍大，而是根本无法输出其核心产品——稳态波形、功率和工作模式。

论文提供的正面证据只有两个 buck 工况：从零状态初始化后，CCM 用 15 轮、DCM 用 18 轮到达 \(\delta=10^{-10}\)，Fig. 9 的 relative error 最终下降到阈值。[pdf:E07]（PDF 物理页 7，Fig. 9）但作者在 Discussion 中明确承认收敛不总是保证；fixed-point 的方向在更复杂网络中可能失控，并建议未来采用更合适的 numerical solver。[pdf:E09]（PDF 物理页 9，Section IV）

缺失的证据包括：fixed-point map 的 contraction 条件、Jacobian spectral radius、basin of attraction、不同初值与参数 continuation、multiple periodic solutions、subharmonic/chaotic operating points，以及复杂拓扑上的失败率。还有一个较隐蔽的问题是停止条件只监视 \(V_o\)：即使输出电压变化很小，内部 diode current 或 junction state 仍可能没有等价收敛。因而“在两个 case 中数值残差达标”不能外推为“general circuit robust convergence”。

## § 10 — 最小复现实验

一周内最小复现应只验证最核心且可证伪的 claim：**在同一 buck 模型中，EIM 不预先判断 CCM/DCM，也能以有限谐波直接得到准确稳态，并比细步长 transient reference 更快。**

实施步骤如下：

1. 依据 Fig. 3、Fig. 5–6 与 Table I–II，实现 \(2K+1=201\) 维的 LTI diagonal matrices、PWM switch Toeplitz matrix、diode Shockley conductance、voltage-dependent junction capacitance、Eq. (27) nodal solve 和 Eq. (19) update；只实现论文的两个参数集，不扩展拓扑。[pdf:E05]（PDF 物理页 5，模型）；[pdf:E06]（PDF 物理页 6，参数与非线性器件）；[pdf:E07]（PDF 物理页 7，Eq. (27)）
2. 用高精度、足够长的 time-domain transient 作为 reference，稳态判据独立于 EIM；同时记录 EIM 的 \(V_o\)、\(i_L\)、diode current、迭代数、wall time 和 peak memory。
3. 预注册通过条件：两个工况都无需手动指定 CCM/DCM；平均 \(v_o\) 相对 reference 误差不超过 \(0.2\%\)；主要 \(i_L\) 波形在采样网格上的 normalized RMS error 不超过 \(1\%\)；EIM wall time 至少快 10 倍；从零初值在 30 轮内达到 \(\delta=10^{-10}\)。
4. 同时把 diode current spike 和 diode loss 作为已知薄弱项，不允许用总效率接近掩盖局部误差。若任何工况发散、落入不同周期解、平均 \(v_o\) 误差超过 \(1\%\)，或加密 reference step 后 EIM 的速度优势消失，就反驳该最小 claim；介于阈值之间则结论为部分复现，而不是成功。

这个实验不需要搭硬件，也不验证一般 converter。它能把“矩阵构造是否正确”“模式是否自动形成”“fixed-point 是否收敛”和“速度比较是否由不公平 transient stop time 造成”分开观察。

## § 11 — 最强反例设计

最强反例不是再换一个普通 buck 参数，而是构造一个**双时间尺度、非线性强、可能多稳态**的 converter：例如 100 kHz PWM buck 在输入或控制端叠加 997 Hz 小信号，同时加入强 voltage-dependent junction capacitance、轻载 DCM 与控制环。若所有源严格落在同一 Fourier grid，fundamental frequency 是它们的最大公约数；为表达 100 kHz switching，\(K\) 至少需要达到 \(10^5\) 量级。论文自己指出，多频率 small-signal/Bode analysis 会因极小 fundamental frequency 与高最高频率而产生不可接受的 harmonic count。[pdf:E09]（PDF 物理页 9，Section IV）

攻击实验应从多个初值与 duty/load continuation 路径运行 EIM，并与 adaptive-step time-domain shooting 交叉比较。预期的失败模式有三种：矩阵规模先使 EIM 失去速度优势；若仍强行用小 \(K\)，switching sidebands 和 diode spike aliasing 造成波形/损耗错误；强非线性还可能让 fixed-point oscillate 或收敛到与 time-domain attractor 不同的周期解。有限谐波已经在本文 Fig. 10 与 Table V 中造成 diode-current envelope 和 loss 偏差，这为该反例提供了直接的机制线索。[pdf:E08]（PDF 物理页 8，Fig. 10 与 Table V）

如果 EIM 在该工况下仍能用稀疏可承受的谐波集合稳定收敛，并在多个初值下得到与 time-domain 相同的 attractor 和损耗，那么这个反例失败，反而会显著加强方法的 generality claim。若它只在单一初值、手调 damping 或预知模式后成功，就不能算通过。

## § 12 — Follow-up Research Idea

在 circuits/power electronics 领域，高影响方法通常不仅要在一个拓扑上得到漂亮波形，还需要清晰的数值成立条件、跨拓扑和跨工作区验证、与强 baseline 的公平比较，以及对实际器件损耗或硬件设计有可重复的价值。本文给了实验波形与商业仿真器比较，这是强项；欠缺的是收敛保证、多频率可扩展性和可实现的并行数值结构。

**候选研究方向：从“单一均匀 Fourier grid 上的 fixed-point EIM”改写为“事件感知的稀疏多频谐波图 + 可认证的非线性求解器”。** 这不是简单增加一个 acceleration module，而是改变问题定义：不再要求所有频率共享一个极小 fundamental，也不把每个器件的全部谐波塞进同一个 dense Toeplitz matrix；每个 source、switching carrier 和 sideband cluster 形成局部频率 lattice，只有器件非线性实际产生的 coupling edge 才进入全局图。开关事件附近的局部高频残差可交给短窗 multi-resolution basis，稳态方程则用 damped Newton-Krylov 或 Anderson acceleration，并对残差、Jacobian spectral radius 与状态一致性给出可检查证书。

- **(a) 未满足需求：** multi-frequency small-signal analysis 不能因 frequency GCD 太小而让 \(K\) 爆炸；复杂网络也不能依赖运气让 fixed-point 收敛。作者在 Discussion 中明确列出这两个缺口。[pdf:E09]（PDF 物理页 9，Section IV）
- **(b) 研究价值：** 如果能把计算量从“最高频率/最小公约频率决定的 dense grid”降到“实际活跃 coupling 数量”，同时给出失败可检测的 convergence certificate，就可能把 EIM 从单拓扑稳态工具推进到可复用的 converter analysis framework。
- **(c) 相邻领域工具：** 可借鉴 sparse spectral methods、multi-tone harmonic balance、graph-based sparse linear algebra、wavelet/multi-resolution analysis 与 nonlinear fixed-point acceleration。论文只提出 MRA 作为未来可能方向，并未实现该组合。[pdf:E09]（PDF 物理页 9，Section IV）
- **(d) 第一个证伪实验：** 使用 §11 的 100 kHz/997 Hz 双频强非线性工况，在相同误差阈值下比较 dense EIM、提出的 sparse multi-lattice solver 和 time-domain reference。若 sparse solver 仍需接近 \(10^5\) 阶全局 grid、不能预测发散、或对 diode loss 的误差没有显著改善，研究想法即被证伪。
- **(e) 实质区别：** 本文的方法把非线性状态映射到一个统一 Fourier grid，再用未认证的 fixed-point iteration；候选方法把频率支撑本身变成稀疏、局部且可增长的计算对象，并把“能否收敛”从隐藏假设变成显式输出。

以上是基于本文限制推导的候选想法。由于本任务只使用输入 PDF，未对 2022 年之后的 multi-tone EIM、sparse HB、MRA converter simulation 或 convergence-certified circuit solvers 做外部检索，因此不声称 novelty。
