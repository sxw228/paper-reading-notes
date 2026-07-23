# A Fast and Stable Method for Modeling Generalized Nonlinearities in Power Electronic Circuit Simulation and Its Real-Time Implementation

**作者**：Zhen Huang；Venkata Dinavahi [pdf:E01]（PDF 物理页 1，标题与作者栏）

**出处**：*IEEE Transactions on Power Electronics*，Vol. 34，No. 4，April 2019 [pdf:E01]（PDF 物理页 1，页眉与出版信息）

**年份**：2019（期刊卷期年份；源 PDF 同页注明 online publication date 为 2018-06-28）[pdf:E01]（PDF 物理页 1，页眉与稿件信息）

**DOI**：10.1109/TPEL.2018.2851570 [pdf:E01]（PDF 物理页 1，Digital Object Identifier）

**Zotero key**：P2SAJ8VM

**证据说明**：

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样为某一种器件写一个更精细的 nonlinear model（非线性模型）”，而是更底层的问题：**能否让不同类型的非线性元件进入同一套固定步长 electromagnetic transient，EMT（电磁暂态）求解框架，使求解既快、可并行，又不因每次开关状态变化而重建整个系统矩阵。** 作者把非线性视为电力电子电路仿真的主要性能瓶颈，并指出 MMC（modular multilevel converter，模块化多电平换流器）一类系统含有大量开关与储能元件，传统 nonlinear solve（非线性求解）会迅速成为计算主耗时；摘要直接把目标概括为 fast、stable、generalized，并把 offline 与 FPGA real-time implementation（实时实现）作为同一个 claim 的两端验证 [pdf:E01]（PDF 物理页 1，Abstract 与 Section I）。

重要性来自三个工程约束同时存在。第一，EMT 仿真需要很小且确定的时间步长，实时硬件还要求每一步都在 deadline（截止时间）内完成，平均速度快但偶尔超时也不够。第二，功率器件在 ON、OFF、turn-on transient、turn-off transient 等状态之间切换，若等效电阻随状态改变，nodal admittance matrix（节点导纳矩阵）也随之改变，反复 factorization（分解）会压垮大规模模型。第三，设备级开关暂态、系统级控制与电机动态可能同时存在，单一的理想开关近似无法覆盖全部精度需求。论文所追求的价值因此很明确：把“拓扑／器件状态变化”从全局矩阵中移走，换成结构固定、计算时间可预测的更新过程，从而兼顾大系统 offline 加速和 FPGA real-time step（实时步长）。

论文直接给出的价值证据是：两类典型拓扑在 system level（系统级）与 device level（器件级）上都与成熟工具作比较，offline C 程序报告约十倍加速，并进一步在 Xilinx FPGA 上实现 500 ns 和 200 ns 的实时步长 [pdf:E02]（PDF 物理页 9，MMC runtime）；[pdf:E03]（PDF 物理页 11，NPC runtime 与 FPGA 平台说明）；[pdf:E04]（PDF 物理页 12，MMC FPGA 时序）；[pdf:E05]（PDF 物理页 14，NPC FPGA 时序）。这些结果说明研究问题不是抽象的矩阵技巧，而是“能否把复杂非线性 EMT 变成硬实时可执行的数据流”。

## § 2 — 前人工作与不足

论文把已有方法分为 iterative（迭代）和 noniterative（非迭代）两大类。迭代方法把网络方程与器件非线性特性联立，典型做法包括 Newton–Raphson；若收敛，它不需要为速度主动引入近似，但作者指出两项工程缺陷：收敛没有普遍保证，且达到指定精度所需迭代次数随工况变化，因此执行时间不可预测，通常更适合 offline、规模受限且不强调 deadline 的场景 [pdf:E01]（PDF 物理页 1，Section I 对 iterative methods 的讨论）。

非迭代方法主要有两条路线。其一是带一个时间步延迟的 current-source representation（电流源表示）：用上一时刻变量预测本时刻注入电流，速度快，但突变电压只能在下一步引起电流响应，可能让电机端子出现虚假尖峰；它依赖“步长足够小”才准确。其二是 piecewise-linear representation（分段线性表示）：例如 ON 时小电阻、OFF 时大电阻，形式直观，但参数切换会改变系统导纳矩阵，迫使程序重新 triangularization／inversion（消元分解／求逆）；当开关数量很大时，这一成本会变得不可接受 [pdf:E06]（PDF 物理页 2，Section I 前半）。

已有 constant-admittance switch model（恒定导纳开关模型）尝试让 ON／OFF 使用相同导纳，但论文指出它们可能引入错误损耗，或需要复杂修正，而且通常只覆盖开关，不能自然推广到电机、PV、battery 等连续变化的非线性。另一方面，latency insertion 与 transmission-line modeling（延迟插入与传输线建模）可人工解耦子系统，却会插入额外 L／C，参数不当时会扭曲原系统动态。最关键的不足不是某个方法“完全不可用”，而是这些方法的数学表示彼此不同：电机适合滞后一拍的电流源，导通开关更像零压电压源，二者不得不共存，最终让统一求解和并行映射都变复杂 [pdf:E06]（PDF 物理页 2，Section I 后半与 Section II 开头）。

因此，论文真正填补的空缺是：**用同一个外部端口形式容纳不同非线性，同时只让一个较小矩阵的对角项随状态变化。** 这比“再提出一种器件模型”更一般，也比“强行让所有开关具有同一电阻”更灵活。不过，论文对 prior work（前人工作）的判断主要来自其正文综述，本卡没有使用输入包之外的全文去独立核验各文献，因此关于 novelty（新颖性）的结论只能理解为作者定位，而不是外部文献检索后的认证。

## § 3 — 重建作者的思考路径

可以从论文给出的背景逆向重建出以下思考链，而不先假定其最终方案正确。

第一，固定步长 EMT 已经有一个成熟事实：线性电感和电容经过 trapezoidal rule（梯形积分）后，都能写成“恒定电阻并联历史电流源”的 Norton equivalent（诺顿等效），所以线性网络的导纳矩阵可以固定，真正麻烦的是非线性器件让等效参数或迭代过程随时间变化 [pdf:E06]（PDF 物理页 2，Fig. 1 与 Section II）。

第二，观察不同非线性器件的工作状态，会发现并非必须同时精确预测其端口电压和端口电流。开关在稳态 ON 时端压接近已知，在稳态 OFF 时电流接近已知；turn-on 时最终电压和初始电压可用于构造电压轨迹，turn-off 时初始电流和最终零电流可用于构造电流轨迹。电机、PV 或电池则可能因 inertia（惯性）使某个端口变量在一个很小的步长内可由历史状态预测。于是，一个合理的研究者会先问：是否可以每步只选择“更可预测的那一个端口变量”，而不是完整求解器件的非线性交点 [pdf:E07]（PDF 物理页 3，Table I、Fig. 3 与 Section III）；[pdf:E08]（PDF 物理页 4，Fig. 4 及互补开关解释）。

第三，若所有元件的外部表示都固定为恒定电阻并联电流源，那么节点电压就是全部 companion current sources（伴随电流源）的固定线性组合；此时非线性不再进入全局导纳矩阵，而是进入“本步应取什么伴随电流源”的辅助方程。接着再利用一个结构事实：电感串联路径对应很大的离散等效电阻，电容并联路径对应很小的离散等效电阻，它们在数学上会减弱非线性子系统间的交叉耦合；MMC 等拓扑因此可能自然分成许多小块，而无需人为插入延迟元件 [pdf:E08]（PDF 物理页 4，Eq. (2)、Eq. (5)–(7)）；[pdf:E09]（PDF 物理页 6，Fig. 6、Eq. (18)–(22) 与 Fig. 7）。

第四，剩下的问题变成一个结构化 linear algebra（线性代数）任务：辅助矩阵的 off-diagonal entries（非对角元）固定，只有对角元因“本步按电流源还是电压源处理”而变化。研究重点于是从通用非线性迭代，转为利用这一结构设计三种不同规模、不同硬件取向的求解器。这个路径解释了为什么论文的方法部分同时出现预计算、modified Gaussian elimination（改进高斯消元）和 Sherman–Morrison update（Sherman–Morrison 更新），而不是只给一个万能算法 [pdf:E10]（PDF 物理页 5，Eq. (13)–(17)）；[pdf:E11]（PDF 物理页 7，三类结构化求解思路）。

## § 4 — 核心 Intuition

把每个非线性元件对外都伪装成“一个恒定电阻并联一个可更新电流源”，就能让全局导纳矩阵永远不变；真正随器件状态变化的，只是伴随源的数值 [pdf:E07]（PDF 物理页 3，Fig. 2、Eq. (1)）。每个时间步不再同时求非线性器件的电压和电流，而是根据状态选择较可预测的一个：可预测电流时把它当电流源，可预测电压时把它当电压源，再由一个仅对角变化的线性系统补出伴随电流源 [pdf:E12]（PDF 物理页 5，Eq. (8)–(12)）；[pdf:E10]（PDF 物理页 5，Eq. (13)–(17)）。方法能快，靠的是固定全局矩阵、自然解耦和结构化求解；它能准到什么程度，则取决于“被选中的端口变量能否在一个步长内被准确预测”。

## § 5 — 具体方法与完整 Pipeline

下面用论文的 three-level NPC-fed PMSM（三级 NPC 驱动永磁同步电机）案例串起完整 pipeline。

1. **统一元件表示。** 线性 L／C 按固定步长积分变成 Norton equivalent；每个非线性元件也固定使用一个常数电阻 \(R_{\mathrm{eq}}\) 并联 companion current source。论文进一步把所有非线性元件的 \(R_{\mathrm{eq}}\) 取为 1，使电流型与电压型方程具有统一形式 [pdf:E07]（PDF 物理页 3，Eq. (1)）；[pdf:E12]（PDF 物理页 5，Eq. (10)–(12) 后的说明）。

2. **一次性建立全局线性映射。** 由固定 conductance matrix \(G\) 和 companion-source incidence matrix \(T\) 得到 \(A=G^{-1}T\)。以后每步只要知道全部独立伴随源向量 \(I\)，节点电压就由 \(V=AI\) 直接计算；FPGA 上也可以选择对 \(GV=I'\) 做 LU factorization，但论文更偏好直接式，因为各节点可并行计算 [pdf:E08]（PDF 物理页 4，Eq. (2)、Eq. (5)–(7)）；[pdf:E03]（PDF 物理页 11，real-time model module 说明）。

3. **先更新线性元件。** 根据上一时间步状态，用 trapezoidal rule、backward Euler 或其他积分规则得到线性元件的新 companion source。论文没有提出 multi-rate（多速率）时间推进；核心框架是 fixed time-step（固定步长），不同案例分别使用 500 ns 与 200 ns [pdf:E03]（PDF 物理页 11，FPGA signal flow 的线性元件更新）；[pdf:E13]（PDF 物理页 8，MMC 500 ns）；[pdf:E14]（PDF 物理页 10，NPC 200 ns）。

4. **给每个非线性元件选择本步 causal orientation（因果方向）。** 控制信号或系统状态决定它按 current-source-type 还是 voltage-source-type 处理。稳态 OFF 开关可设为零电流源，稳态 ON 开关可设为零电压源；turn-off 使用电流轨迹，turn-on 使用电压轨迹；电机、PV、battery 等则依赖历史状态与惯性预测一个步长后的电流或电压 [pdf:E07]（PDF 物理页 3，Table I 与 Section III）；[pdf:E08]（PDF 物理页 4，Fig. 4）。

5. **建立 companion-source 方程。** 对电流型元件，把预测的 \(i_{km}(t)\) 代入端口方程；对电压型元件，把预测的 \(v_{km}(t)\) 代入。因为 \(V=AI\) 的系数固定，所有未知非线性伴随源最终组成 \(MI=b\)。其中非对角项来自固定的 \(A\)，始终不变；电流型方程会在对应对角位置多出一个 1，电压型方程没有这个 1，所以只有对角项随类型切换 [pdf:E12]（PDF 物理页 5，Eq. (9)–(12)）；[pdf:E10]（PDF 物理页 5，Eq. (13)）。

6. **先解耦，再选求解器。** 若真实电感位于子系统串联路径，离散等效 \(R_L=2L/\Delta t\) 很大；若真实电容位于并联路径，离散等效 \(R_C=\Delta t/(2C)\) 很小，交叉耦合系数会随之减小。论文据此把“先找自然 decoupling，再选 solver”设为原则：小矩阵用 precomputed inversion／factorization，中等矩阵与 FPGA 并行场景用 Sherman–Morrison，大矩阵或 CPU sequential program（顺序程序）用 modified Gaussian elimination [pdf:E09]（PDF 物理页 6，Fig. 6、Eq. (18)–(22)）；[pdf:E15]（PDF 物理页 8，solver selection）。

7. **NPC 例子的结构化缩减。** 该案例有 12 个节点、3 个线性元件和 19 个非线性元件；考虑 PMSM 三相电流和为零后，\(A\) 为 \(12\times 23\)，初始 \(M\) 为 \(20\times 20\)。18 个会切换类型的 IGBT／diode 与始终按电流源处理的电机被分块后，Schur complement（舒尔补）把问题化为三个相同的 \(6\times6\) 相腿矩阵；offline 程序用 modified Gaussian elimination 求解 [pdf:E16]（PDF 物理页 9，Fig. 11 与系统规模）；[pdf:E14]（PDF 物理页 10，矩阵分块与三个 \(6\times6\) 子问题）。

8. **计算节点电压并推进状态。** 解出本步非线性 companion sources 后，把它们与线性 companion sources 合并，计算 \(V=AI\)，再更新电感、电容、电机、器件轨迹与控制器状态，进入下一步。论文的事件处理不是连续时间 root finding（根定位），而是每步根据 control signal／system state 判定模式；是否发生更细粒度的 event localization 未报告 [pdf:E17]（PDF 物理页 12，Fig. 14）。

9. **映射到 FPGA。** 项目分为并行的 control module 与 model module；model module 内部依次计算节点电压和伴随源。MMC 的 \(2\times2\) 模式矩阵直接预存；NPC real-time 版本把 Sherman–Morrison inverse update 放在主状态循环之外，与控制模块并行工作，新逆矩阵准备好后新模式才生效。论文报告该更新延迟小于 1 μs，并认为相对半个 carrier period 可忽略，但这实际上引入了一个有界的 mode-application delay（模式生效延迟）[pdf:E17]（PDF 物理页 12，Fig. 14）；[pdf:E05]（PDF 物理页 14，Sherman–Morrison 并行更新与延迟说明）。

数值表示方面，论文只明确报告 MMC FPGA 模型使用 59-bit fixed point（59 位定点数），并通过 multiplier reuse（乘法器复用）和 pipeline（流水线）降低资源；NPC 的具体数值位宽未在源 PDF 中报告 [pdf:E04]（PDF 物理页 12，MMC fixed-point 与 pipeline 说明）。

## § 6 — 核心数学推导（无形式化数学则跳过）

**第一步：用端口恒等式固定非线性元件的外观。** 对连接节点 \(k,m\) 的任意二端非线性元件，只要其真实端口解为 \(v_{km}(t),i_{km}(t)\)，就可以选一个常数 \(R_{\mathrm{eq}}\)，令

\[
I_{\mathrm{com}}(t)=i_{km}(t)-\frac{v_{km}(t)}{R_{\mathrm{eq}}}.
\]

这样，外部网络看到的“恒定电阻并联电流源”在该端口点上与原非线性元件完全一致 [pdf:E07]（PDF 物理页 3，Eq. (1) 与 Fig. 2）。这一步本身不是近似；近似发生在如何在不做迭代的情况下得到本步的 \(v_{km}\) 或 \(i_{km}\)。

**第二步：把全局网络压成固定线性映射。** 所有元件都采用恒定电阻后，nodal equation 为

\[
GV=I',\qquad I'=TI,
\]

因此

\[
V=G^{-1}TI=AI,
\]

并且任意端口电压都能写成

\[
v_{km}(t)=\sum_{j=1}^{N_2}\bigl(A_{k,j}-A_{m,j}\bigr)I_j(t).
\]

这里 \(G\)、\(T\)、\(A\) 都是常数；直观上，所有网络拓扑和线性耦合都被提前编译进 \(A\)，运行时只更新源向量 [pdf:E08]（PDF 物理页 4，Eq. (2)、Eq. (5)–(7)）。若直接乘 \(A\)，单步节点电压计算是矩阵-向量乘，作者将其复杂度归为 \(O(N^2)\)，而不是每次对时变矩阵做约 \(O(N^3/3)\) 的分解 [pdf:E07]（PDF 物理页 3，Eq. (1) 后的复杂度说明）。

**第三步：用“预测电流”或“预测电压”闭合每个非线性端口。** 端口支路电流为

\[
i_{km}(t)=\frac{v_{km}(t)}{R_{\mathrm{eq}}}+I_l(t).
\]

若 \(i_{km}(t)\) 可预测，把上式和 \(v_{km}=AI\) 代入后，对未知 \(I_l\) 的那一行会多出一个自身系数；若 \(v_{km}(t)\) 可预测，则对应行没有这个额外自身项。论文把所有非线性 \(R_{\mathrm{eq}}\) 取 1，于是两类方程只在对角位置相差 1，统一得到

\[
M_{N_3\times N_3}I_{N_3\times1}=b_{N_3\times1},
\]

其中 \(M\) 的 off-diagonal entries 恒定，只有 diagonal entries 随模式变化 [pdf:E12]（PDF 物理页 5，Eq. (8)–(12)）；[pdf:E10]（PDF 物理页 5，Eq. (13)）。这正是全文最重要的代数结构。

**第四步：把不切换类型的元件消掉。** 将会在电流型／电压型之间切换的元件记为块 1，始终保持一种类型的元件记为块 2：

\[
\begin{bmatrix}M_{11}&M_{12}\\M_{21}&M_{22}\end{bmatrix}
\begin{bmatrix}I_1\\I_2\end{bmatrix}
=
\begin{bmatrix}b_1\\b_2\end{bmatrix}.
\]

因为 \(M_{12},M_{21},M_{22}\) 固定，可先消去 \(I_2\)，得到

\[
\underbrace{\left(M_{11}-M_{12}M_{22}^{-1}M_{21}\right)}_{M}I_1
=
\underbrace{b_1-M_{12}M_{22}^{-1}b_2}_{b}.
\]

这一步把所有真正的时变性集中到更小的 diagonal time-varying matrix（对角时变矩阵）中 [pdf:E10]（PDF 物理页 5，Eq. (14)–(17)）。

**第五步：利用拓扑和矩阵更新结构求解。** 对自然解耦后的小矩阵，枚举全部可达模式并预存 inverse／factorization，运行时复杂度近似为常数。modified Gaussian elimination 从矩阵两端交替制造零块，约 \(\lceil(N+1)/2\rceil\) 步后只需对约半尺寸的 variable block \(P\) 做传统消元；在论文给定的节点数与非线性元件数近似条件下，计算量约为传统时变 \(G\) 消元的八分之一 [pdf:E11]（PDF 物理页 7，Fig. 8 与其后复杂度分析）。

对只改变少数对角元的模式切换，论文使用 Sherman–Morrison rank-1 update：

\[
(M+uv)^{-1}=M^{-1}-\sigma M^{-1}uvM^{-1},
\qquad
\sigma=\frac{1}{1+vM^{-1}u}.
\]

若有 \(m\) 个对角项相对基矩阵不同，更新复杂度为 \(O(mN^2)\)；在 FPGA 上，同一轮的 \(N^2\) 个中间量可并行，因此作者把 wall-clock complexity（墙钟复杂度）理解为约 \(O(m)\) [pdf:E11]（PDF 物理页 7，Eq. (26) 与复杂度）；[pdf:E15]（PDF 物理页 8，并行性说明）。

**数学上最需要谨慎的地方有两个。** 一是论文没有给出“历史预测端口变量”的 general error bound（通用误差界），因此 \(MI=b\) 的代数求解可以很精确，但右端 \(b\) 本身仍可能代表错误的物理近似。二是 Sherman–Morrison 在 \(1+vM^{-1}u\) 很小时会产生 numerical distortion（数值畸变）；作者给出基矩阵与更新顺序的经验性规避策略，但没有给出覆盖全部模式的条件数证明 [pdf:E15]（PDF 物理页 8，数值误差警告）。作者所谓“always numerically stable”主要依据每个元件外部都带有内部电阻、全局网络看起来像纯电阻网络；这支持 nodal solve 不易发散，却不能自动推出离散非线性模型的 physical fidelity（物理保真度）在所有工况下都稳定 [pdf:E15]（PDF 物理页 8，stability claim）。

## § 7 — 实验设计与结论

**问题 1：系统级 MMC 波形是否接近成熟 EMT 工具？ → 实验：** 构建三相 five-level MMC，采用上下桥臂相差 45° 的 phase-shift PWM，DC-link 在 50 ms 内 soft start，固定步长 500 ns；用 PSCAD/EMTDC 与基于本文方法的 C 程序比较线电压、负载电流和子模块电容电压。**答案：** 线电压 THD 为 9.82%（PSCAD/EMTDC）与 9.81%（本文程序），A 相负载电流 THD 均为 1.25%；两只电容电压的 mean-square error 分别为 \(9.8189\times10^{-7}\) 与 \(9.8398\times10^{-7}\) [pdf:E13]（PDF 物理页 8，Fig. 9 与参数／THD 正文）；[pdf:E02]（PDF 物理页 9，MSE 正文）。在该测试范围内，系统级波形差异很小。

**问题 2：固定全局矩阵能否带来 offline 加速？ → 实验：** 在 Intel i7-3770 上执行 100 ms MMC 仿真，步长 500 ns；PSCAD 关闭图形输出，C 程序只计执行时间且以 debug mode 计时。**答案：** PSCAD/EMTDC 约 34 s，本文程序 3.361 s，约十倍加速 [pdf:E02]（PDF 物理页 9，runtime protocol 与报告数字）。这个比较尽力减少了图形和编译开销，但仍是 general-purpose commercial tool 与专用 C 程序之间的 system-level comparison，不能单独分离“算法优势”和“软件栈优势”。

**问题 3：方法能否处理同时含 IGBT、diode 和 PMSM 的更复杂非线性？ → 实验：** 使用 three-level NPC-fed PMSM，系统含 12 个节点、3 个线性元件、19 个非线性元件；把 \(20\times20\) 问题缩成三个相同 \(6\times6\) 子问题，固定步长 200 ns。系统启动时半载，SVPWM 控制令 d-axis current 为 0、q-axis current 为 1 kA；与 PSCAD/EMTDC 比较启动电流和线电压，并与 SaberRD 比较器件开关暂态 [pdf:E16]（PDF 物理页 9，Fig. 11 与系统规模）；[pdf:E14]（PDF 物理页 10，Fig. 12、控制设定与矩阵缩减）。**答案：** 系统级波形大尺度上难以区分；细看时，本文程序因显式包含器件 switching trajectory 而出现 PSCAD 简单 \(R_{on}/R_{off}\) 模型没有的电压尖峰。器件级参数也接近 datasheet 与 SaberRD：例如 IGBT \(t_{d(on)}\) 为 0.50／0.52／0.54 μs，\(t_r\) 为 0.55／0.53／0.58 μs，\(t_{d(off)}\) 为 4.3／4.3／4.4 μs，\(t_f\) 为 0.40／0.38／0.42 μs，diode \(t_{rr}\) 三者均为 4.0 μs，顺序分别是 datasheet／SaberRD／本文程序 [pdf:E03]（PDF 物理页 11，Table II 与 Fig. 13）。

**问题 4：NPC 案例是否也有速度优势？ → 实验：** 在同一 i7-3770 上做 1 s、200 ns 步长的 NPC-fed PMSM 仿真。**答案：** PSCAD/EMTDC 约 143 s，本文程序 13.288 s，仍超过十倍；SaberRD 因 iterative algorithm 与 variable time step 需要数小时，论文明确没有把它纳入同口径 runtime 比较 [pdf:E03]（PDF 物理页 11，offline runtime）。

**问题 5：MMC 能否在 FPGA 上满足硬实时？ → 实验：** 在 Xilinx Virtex UltraScale+ VCU118-ES1 上实现。MMC 的模式矩阵是 \(2\times2\) 且只有两种变化，预存两种解；节点映射矩阵 \(A\) 为 \(53\times82\)。为了避免全并行所需的 4000 多个 multiplier，使用 59-bit fixed point，把每个节点的 82 次乘法和 81 次加法分成 19、20、21、22 次乘法的四组并流水复用 [pdf:E04]（PDF 物理页 12，MMC FPGA 实现）。**答案：** 在 100 MHz 时钟下实现 500 ns 步长，即每步 50 个系统时钟；资源为 LUT 582115（49.24%）、FF 211466（8.94%）、BRAM 37.5（1.74%）、DSP 2140（31.3%），实时波形与 offline 波形近似一致 [pdf:E04]（PDF 物理页 12，Table III 与时序）；[pdf:E18]（PDF 物理页 13，Fig. 15）。

**问题 6：NPC-fed PMSM 能否以更小步长实时运行？ → 实验：** 利用每个相腿只有四种可达 switching combination，选择两种 base inverse，用 Sherman–Morrison 在控制路径旁路更新；新 inverse 准备好后再让模式生效。**答案：** 100 MHz FPGA 上实现 200 ns 步长；更新延迟小于 1 μs。资源为 LUT 125418（10.61%）、FF 98601（4.17%）、BRAM 106（4.91%）、DSP 998（14.59%），并展示 PMSM 启动、NPC 线电压、IGBT turn-on／turn-off 与 diode reverse-recovery 的实时波形 [pdf:E18]（PDF 物理页 13，Fig. 16、Table IV、Fig. 17）；[pdf:E05]（PDF 物理页 14，更新策略、延迟与 200 ns 步长）。

**不得外推的范围。** 这些实验有力证明了两种代表性拓扑上的 feasibility（可行性），但没有覆盖广泛非线性类别、强耦合无惯性工况、步长／参数不确定性 sweep、不同 \(R_{\mathrm{eq}}\) 对 conditioning（条件数）的影响，也没有给出同一代码基、同一编译优化、同一器件模型下的 solver-only benchmark。作者关于“most if not all nonlinearities”与“always stable”的广泛表述，证据强度低于其对 MMC 与 NPC 两个案例的具体结论 [pdf:E03]（PDF 物理页 11，generality claim）；[pdf:E05]（PDF 物理页 14，Conclusion）。

## § 8 — Take-aways

**5 句话：** ① 论文把任意非线性元件统一表示为恒定电阻并联 companion current source，从而固定全局导纳矩阵 [pdf:E07]（PDF 物理页 3，Fig. 2、Eq. (1)）。② 它每步只预测较可信的端口电流或电压，并把剩余未知量变成一个仅对角变化的 \(MI=b\) [pdf:E12]（PDF 物理页 5，Eq. (8)–(12)）；[pdf:E10]（PDF 物理页 5，Eq. (13)–(17)）。③ 真实 L／C 带来的自然解耦，再加预计算、modified Gaussian 和 Sherman–Morrison，使方法能适配不同矩阵规模与 CPU／FPGA 执行方式 [pdf:E09]（PDF 物理页 6，decoupling）；[pdf:E15]（PDF 物理页 8，solver choice）。④ 两个 offline 案例在报告指标上接近 PSCAD／SaberRD，同时 C 程序约快十倍 [pdf:E02]（PDF 物理页 9，MMC）；[pdf:E03]（PDF 物理页 11，NPC）。⑤ FPGA 结果说明这种结构确实能变成确定时序的数据流，达到 500 ns MMC 和 200 ns NPC 实时步长，但 accuracy envelope（精度适用边界）仍只由有限案例支持 [pdf:E04]（PDF 物理页 12）；[pdf:E05]（PDF 物理页 14）。

**3 句话：** ① 这篇论文最有价值的贡献不是某个器件模型，而是把 nonlinear solve 重新组织成“固定网络映射 + 可切换因果方向 + 对角时变小矩阵”。② 它的速度优势有清楚的结构来源，也有 offline 与 FPGA 结果支撑；它的普适精度则依赖端口变量的一步预测质量。③ 因而，读者应把“矩阵求解稳定”和“物理模型在所有工况下准确”分开评价 [pdf:E15]（PDF 物理页 8，stability claim 与 Sherman–Morrison caveat）。

**1 句话：** 这是一种把非线性 EMT 从全局迭代问题改写为结构化源更新问题的强工程方法，其真正瓶颈从矩阵分解转移到了“本步应预测电流还是电压，以及预测能否可信”。

## § 9 — 最脆弱的假设

最脆弱、失效代价最大的假设是：**对每个非线性元件，在每个时间步都能选出一个端口变量，使其本步电流或电压可以由历史信息、控制状态或预定义 trajectory 足够准确地预测。** 论文自己明确把这一步称为为简化 companion source 求解而作的 approximation（近似）；current-source-type 与 voltage-source-type 的分类主要依据 empirical conventions（经验约定），而不是由可检验的误差条件自动决定 [pdf:E07]（PDF 物理页 3，Section III 与 Table I）；[pdf:E12]（PDF 物理页 5，Eq. (8) 后对 approximation 的说明）。

这个假设一旦不成立，损失不是局部的。预测值进入 \(b\) 或决定 \(M\) 的对角模式；即使 \(MI=b\) 被精确、稳定、快速地解出，得到的也只是“错误近似方程的精确解”。因此，恒定导纳矩阵和内部电阻能降低矩阵奇异／发散风险，却不能补偿 source prediction error（源预测误差）。这也是作者“always numerically stable”与“generalized accuracy”之间必须区分的地方 [pdf:E10]（PDF 物理页 5，\(MI=b\)）；[pdf:E15]（PDF 物理页 8，stability claim）。

该假设在低惯性、强耦合、同一步内电压和电流都剧烈变化的场景中可能失效。例如硬换流期间的电流转移、寄生 L／C 振荡、diode reverse recovery 与多个器件近同时切换，会使“下一步端口变量”主要由本步网络共同解决定，而不是由上一时刻单独决定。论文给出的正面证据是：开关轨迹可由实验曲线构造，电机／PV／battery 可借助系统惯性，且在 500 ns 与 200 ns 的两个案例中得到较好匹配 [pdf:E07]（PDF 物理页 3，Fig. 3 与 inertia 论述）；[pdf:E14]（PDF 物理页 10，200 ns NPC 结果）；[pdf:E03]（PDF 物理页 11，Table II）。缺少的证据则是统一的 predictability criterion（可预测性判据）、一步预测误差界、步长 sweep、参数扰动、强耦合 stress test，以及预测失效时的在线检测或 fallback（回退）。

所以，本卡对论文最核心的批评不是“速度比较不公平”，也不是“FPGA 位宽未完全报告”，而是：**论文把最困难的非线性闭合问题转移成了端口变量预测，却没有给出何时这种预测仍然可信的通用边界。**

## § 10 — 最小复现实验

一周内最值得复现的不是完整 MMC 或 PMSM，而是核心代数 claim 与最脆弱假设：**固定 \(G\) + current／voltage orientation 是否能在开关暂态中同时保持误差和速度优势。**

**数据与电路。** 实现论文 Fig. 4／Fig. 5 的 complementary half-bridge（互补半桥）与一个简单 R–L 负载。DC bus 取论文 NPC 参数中的 3 kV，carrier frequency 取 1800 Hz；turn-on／turn-off 时间常数采用 Table II 报告的量级，例如 \(t_{d(on)}=0.50\) μs、\(t_r=0.55\) μs、\(t_{d(off)}=4.3\) μs、\(t_f=0.40\) μs，并用平滑分段多项式生成可重复的 per-unit trajectory [pdf:E08]（PDF 物理页 4，Fig. 4／Fig. 5）；[pdf:E03]（PDF 物理页 11，Table II）；[pdf:E05]（PDF 物理页 14，Table VI）。论文没有公开完整器件 trajectory function，因此该实验复现的是方法机制，不声称逐点复现 Fig. 13。

**实现三套求解。** 第一套按论文方法：所有非线性 \(R_{\mathrm{eq}}=1\)，预计算 \(A=G^{-1}T\)，turn-on／ON 按 voltage source，turn-off／OFF 按 current source，解小型 \(MI=b\)。第二套是 piecewise \(R_{on}/R_{off}\) baseline，每次模式变化都重建并 factorize \(G\)。第三套是 reference：对同一平滑器件方程做 implicit Newton solve，步长取测试步长的十分之一，用作数值参考而不是速度基线。

**步长 sweep。** 分别测试 50、100、200、500 ns；每个步长运行至少若干 carrier periods，并加入一次 DC bus step 或负载突变，让 source prediction 遭遇真正的非平稳事件。记录每步 KCL residual、端口电压／电流 RMSE、峰值过冲、turn-on／turn-off timing error、累计 switching energy proxy、总执行时间、矩阵 factorization 次数和 deadline miss。

**支持条件。** 本复现预设：在 200 ns 及以下，论文方法相对 reference 的归一化波形 RMSE 小于 1%，开关时间参数误差小于 5%，KCL residual 与 baseline 同量级，同时全局矩阵 factorization 次数降为初始化时一次，wall-clock time 明显低于 piecewise baseline。这里的 1% 与 5% 是复现实验的证伪阈值，不是论文报告数字。

**反驳条件。** 若在 200 ns 或更小步长下，mode orientation 仍导致开关能量、峰值电压／电流或暂态时序出现系统性偏差；或为了压低误差必须把步长缩到使速度优势消失；或 \(R_{\mathrm{eq}}=1\) 引起明显 conditioning 问题，那么核心 claim 至少需要收窄。这个实验不需要复现完整 FPGA，却能直接回答“速度来自结构，还是来自把难以预测的物理过程提前写死”。

## § 11 — 最强反例设计

最强反例是构造一个**无明显惯性缓冲、强端口耦合、多个器件近同时换流**的网络，让本步电压和电流都不能由上一时刻单向预测。具体可用两个互相耦合的半桥，中间只保留很小的寄生电感和结电容，加入 diode reverse recovery，并让两桥在同一时间窗内改变模式；选择时间步与最快 parasitic resonance（寄生谐振）同量级，然后对 source orientation、步长和寄生参数做 sweep。

对照组使用同一物理模型的 fully implicit DAE／Newton reference，并把步长缩小 10–20 倍。攻击指标不是只看波形“像不像”，而是同时测量峰值 \(v_{CE}\)、峰值 \(i_C\)、reverse-recovery charge proxy、switching energy、KCL residual、mode timing 和 closed-loop state drift。若本文方法保持数值有界，却持续低估过冲或开关能量，便能证明“内部电阻带来的 numerical stability”不等于物理准确；若 current／voltage classification 在相邻步之间反复切换，还可检验是否出现 orientation chatter（因果方向抖动）。

这个反例还可以把可达模式选到使 Sherman–Morrison 的 \(1+vM^{-1}u\) 接近零，测试作者已承认的 numerical distortion 条件 [pdf:E15]（PDF 物理页 8，Sherman–Morrison caveat）。但反例的主攻击仍是 source predictability，而不是单纯制造病态矩阵：最有力的替代解释是，论文报告的高精度主要来自所选 MMC／NPC 案例具有足够 L／C decoupling、固定小步长和可预制器件轨迹，而不是该表示对 generalized nonlinearities 普遍成立 [pdf:E09]（PDF 物理页 6，natural decoupling）；[pdf:E14]（PDF 物理页 10，NPC 案例）；[pdf:E05]（PDF 物理页 14，generality conclusion）。

若该强耦合基准上，本文方法在合理步长仍能同时守住峰值、能量和状态误差，并保持固定计算预算，那么它对核心机制的支持力度会远高于原论文的“再增加一个常规拓扑”实验。

## § 12 — Follow-up Research Idea

基于本文展示的评价方式，EMT + FPGA 方向的高影响工作通常不能只给 algebraic speedup（代数加速）；它需要同时说明 system-level fidelity、device-level switching fidelity、real-time step、worst-case execution time、hardware utilization，以及跨拓扑的可迁移性。本文已经覆盖了其中多项，但没有给出“何时可以安全地把元件定向为电流源或电压源”的可证伪边界 [pdf:E14]（PDF 物理页 10，system／device comparison）；[pdf:E04]（PDF 物理页 12，FPGA time／resource）；[pdf:E18]（PDF 物理页 13，real-time waveforms 与 Table IV）。

**候选研究方向：Uncertainty-Certified Causal Orientation EMT（不确定性认证的因果定向 EMT）。** 它不再把元件预先归入 current-source-type 或 voltage-source-type，而是把每一步建模重新定义为一个 dynamic graph orientation（动态图因果定向）问题：对每个端口同时生成电流预测、 电压预测及其 local error estimate（局部误差估计）；只有当某一方向满足误差与 conditioning 证书时才用本文的显式 companion-source 更新。未通过认证且强耦合的元件自动合并为小型 nonlinear cluster，在 cluster 内做局部 implicit solve，而全局 \(G\) 仍保持固定。

**（a）未满足的需求。** 现有方法在可预测、自然解耦的案例上很强，但缺少对 abrupt event、寄生动态、模式同时切换和参数漂移的在线可信度判断。工程上需要的不是“永远不迭代”，而是“只在证据表明显式近似不可信的最小局部范围内迭代”，并给出每步 worst-case budget。

**（b）可能产生的研究价值。** 若能证明全局固定矩阵、局部有限迭代和在线误差证书可以同时成立，就会把论文当前的经验分类提升为可验证的 accuracy–latency contract（精度—时延契约）。这类结果既能形成理论边界，又能直接映射到 FPGA 上的 bounded fallback lanes（有界回退通道），符合本领域对实时性、资源和物理准确度同时验收的习惯。

**（c）可借鉴的相邻领域工具。** 可以借鉴 DAE tearing／index reduction（微分代数方程撕裂／指数约简）来识别最小强耦合 cluster，借鉴 domain decomposition（区域分解）组织并行局部求解，借鉴 residual-based error estimator（基于残差的误差估计）给 source prediction 做在线认证，并用 incremental passivity／port-Hamiltonian tools（增量无源性／端口哈密顿工具）约束局部模型不会向全局网络注入非物理能量。

**（d）第一个能证伪它的实验。** 直接使用第 11 节的强耦合换流基准，在相同 FPGA resource budget 和相同 deadline 下比较：固定经验分类的本文方法、全局 implicit Newton、以及候选 adaptive orientation + local cluster solver。若候选方法大多数时间都把元件判为“不确定”，导致 cluster 覆盖全网；或在相同资源下既没有更大的稳定步长，也没有更低的峰值／能量误差，那么该想法被证伪。

**（e）与本文的实质区别。** 它不是在三种 \(M\) 求解器之外再加第四种 solver，也不是简单增加一个误差模块；它改变了问题定义：从“依据经验给非线性元件选固定 source type”改为“每步认证 causal direction，并把未认证部分重新划分为局部隐式问题”。本文把 approximation 隐含在 source prediction 中，候选方案则把 approximation validity（近似有效性）本身变成显式状态与硬实时调度对象。

由于本任务按协议只使用输入包、未对 2018 年之后的相关工作做外部检索，这一方向只能标为**候选研究想法**，不声称 novelty。
