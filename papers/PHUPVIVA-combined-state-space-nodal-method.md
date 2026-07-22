# A Combined State-Space Nodal Method for the Simulation of Power System Transients

Christian Dufour、Jean Mahseredjian、Jean Bélanger；IEEE Transactions on Power Delivery，2011；DOI：10.1109/TPWRD.2010.2090364；Zotero key：PHUPVIVA

**来源说明。** 公式和报告数字已由 fidelity 核验；这不代表论文 prose 已逐句认证。下文把论文原文明确声称、相关文献已有结论、基于证据的推断和仍不确定的候选判断分开写，并用论文章节、图、表或 `fidelity item` 标注可核验位置。

## § 1 — 研究问题与重要性

**研究问题。** 论文要解决的是：能否把任意大小、以 state-space 描述的电气子系统分成若干组，分别保留其动态状态，再把每组在当前时间步的端口关系转换成 nodal 形式，与其余 nodal equations 同时求解（论文 §I 末段；§II 开头）。这里的“同时”不是先解一个系统、再把结果喂给另一个系统，而是让各组共享同一个当前时间点的节点电压/电流解。

物理上，state-space 方法擅长保存电容电压、 电感电流等内部能量状态，并且离散器可以在建模之后选择；但把整个网络一次性合成一个状态空间模型，会让开关组合、自动矩阵生成和大规模非线性耦合变得昂贵（论文 §I 第 1–3 段）。Nodal analysis 把器件离散成伴随支路，适合稀疏大网络、拓扑变化和 MANA（modified-augmented-nodal analysis），但单独使用时会把所有器件都放进节点方程，或受到拓扑/非线性处理方式的约束（论文 §I 第 1–2 段及文献 [3]–[6]、[17]）。

因此，论文的工程瓶颈不是“哪一种方程更正确”，而是如何在同一 EMT 时间步内取得两者的优势：局部状态空间减少自动合成和开关预计算，节点接口保留稀疏联立求解，并为并行计算和非线性迭代留下入口（论文 §I 倒数第 3–1 段；§V）。这对 real-time simulation 尤其重要，因为最坏时间步必须在时限内完成，且开关事件会放大缓存失效和矩阵更新的成本（论文 §III-D，Table I）。

## § 2 — 前人工作与不足

论文把已有路线分成两大类。以 SimPowerSystems、控制器设计和自动状态空间合成为代表的 state-space 路线（文献 [1]、[13]、[18]、[19]）可以在建模后选择数值积分器，也适合显式保留内部状态；但完整系统的自动矩阵合成耗时，多个开关需要为每种 permutation 预存矩阵，非线性和大状态数又会使每步求解变重（论文 §I 第 2–4 段）。以 Dommel 方法、MANA、MatEMTP 和 EMTP-RV 为代表的 nodal 路线（文献 [3]–[6]、[17]）利用稀疏矩阵处理大网络和拓扑变化，但若整个系统都用节点方程，状态空间在控制设计或局部复杂模型中的便利性就丢失；某些传统 nodal 变体还需要处理拓扑限制或附加补偿。

更接近本文的工作是分组、compensation 和接口缩减：OVNI/PC clusters 通过 group separation 减小节点或独立求解子电路（文献 [9]–[13]），测量拟合工作也曾把 state-space 方程嵌入 nodal equations（文献 [14]、[15]）。这些工作说明“分组”可行，却没有在本文所要求的范围内给出一个统一、任意拓扑、可把 state-space 组和 nodal 组直接混接的离散端口表达（论文 §I 第 5–7 段；§II）。

最关键的不足是开关组合的组合爆炸。论文指出，离散 state-space solver 对 switching events 不友好，靠预计算矩阵来满足 real-time 时限时，耦合开关数量一大，矩阵集合的存储需求就会失控（论文 §I 倒数第 4 段；相关讨论引用文献 [16]）。本文的切入点是让每个局部组只承担自己内部的 switch permutation，把跨组耦合压缩为当前步的 nodal interface；但这只是论文在其示例和分组方式下验证过的工程策略，并不是对所有网络的复杂度定理。

## § 3 — 重建作者的思考路径

以下是基于 §I–§II 背景的重建，不把论文的最终贡献倒灌成先验事实。

1. 先观察到两种求解器的优势互补：大网络需要 sparse nodal solve，而控制和局部动态模型需要 state variables 与可选积分器。若强迫整网只用一种表示，就必然放弃另一边的便利（论文 §I 第 1–3 段）。
2. 再把一个 state-space 子系统看成“内部状态 + 外部端口”。外部输入在当前步只通过端口电压或电流进入，因而可以尝试先消去内部状态，留下一个 history term 加一个当前端口的线性映射（论文 §II-A，eqs. (1)–(7)）。
3. 端口可能是电压驱动的 Norton 关系，也可能是电流驱动的 Thevenin 关系；现实网络还会同时出现两种端口。于是需要 mixed-type 表达，并把它重新整理成标准 nodal current-versus-voltage 关系（论文 §II-A，eqs. (8)、(9)）。
4. 一旦每个组都能输出这样的关系，就可以把各组的 admittance 映射到一个全局节点矩阵；开关未改变时矩阵保持不变，改变时只更新受影响的组。剩余的纯 nodal 组和非线性支路可直接放入 MANA，避免为全网重新合成 state-space（论文 §II-A，eqs. (10)–(12)）。
5. 最后，组内计算天然可并行，稳态 phasor 可给出初始状态，非线性可在缩小后的 MANA/Jacobian 上迭代。这样形成的不是“state-space 加一个接口模块”，而是一个按组分配计算负担的统一 solver（论文 §II-B、§III-D、§IV；这是基于这些步骤的推断）。

## § 4 — 核心 Intuition

把每个 state-space 组想成一个带记忆的多端口元件：内部电容和电感继续按 state-space 更新，但对外只交付“历史响应 + 当前端口矩阵”的伴随关系。跨组连接因此只需要一次当前步的 nodal 联立，Norton、Thevenin 和 mixed-type 端口都能接入同一网络。开关和局部非线性留在各自组或 MANA 区域内，若分组确实把变化局部化，就能减少全局矩阵集合、并行计算，并保留同时求解非线性的可能（论文 §II-A、§II-B；这是对机制的物理解释和证据推断）。

## § 5 — 具体方法与完整 Pipeline

以论文的 HVDC 测试为例，输入是整流侧的交流源/阻抗、可切换电容、固定滤波器、变压器—晶闸管整流器—平波电抗器，以及它们和逆变侧之间的端口连接（论文 §III-B，Fig. 5）。完整 pipeline 如下。

1. **分组和状态建模。** 每个 group 选择一组独立的电容电压、 电感电流作为 state vector，写成
   \[
   \dot{\mathbf{x}}=\mathbf{A}_k\mathbf{x}+\mathbf{B}_k\mathbf{u},\qquad
   \mathbf{y}=\mathbf{C}_k\mathbf{x}+\mathbf{D}_k\mathbf{u}
   \]
   （论文 §II-A，eq. (1)；`fidelity item：eq(1)，PDF p.2 左栏`）。下标 $k$ 表示开关位置或 piecewise-linear device segment 的 permutation。
2. **离散化并拆端口。** 对 state equation 使用 trapezoidal integration，先得到当前和下一步输入共同参与的离散更新（eq. (2)），再把输入分成内部注入 $\mathbf{u}_i$ 与外部 nodal 注入 $\mathbf{u}_n$，输出分成内部量和节点端口量（eqs. (3)、(4)；对应 `fidelity item：eq(2)`、`eq(3)`、`eq(4)，PDF p.2 左栏`）。这一步的物理意义是把组内状态推进与组间端口闭合分开。
3. **生成当前步端口伴随关系。** 将 eq. (3) 代入 eq. (4) 的 nodal-output 行，得到
   \[
   \mathbf{y}_{n,t+\Delta t}=\mathbf{y}_{k_{hist}}+\mathbf{W}_{k_n}\mathbf{u}_{n,t+\Delta t},\qquad
   \mathbf{W}_{k_n}=\mathbf{C}_{k_n}\hat{\mathbf B}_{k_n}+\mathbf{D}_{k_{nn}}
   \]
   （论文 §II-A，eqs. (5)–(7)；`fidelity item：eq(5)`、`eq(6)`、`eq(7)，PDF p.2 左栏`）。第一项由上一步已知状态和内部输入组成，第二项是当前端口的线性映射。
4. **统一 V/I/mixed-type 端口。** 若端口输入是电压、输出是电流，$\mathbf W$ 是 admittance，构成 V-type/Norton 组；若输入是电流、输出是电压，$\mathbf W$ 是 impedance，构成 I-type/Thevenin 组。两者同时存在时使用 mixed relation（eq. (8)），再将电流项移到左侧，得到由 history term 和 $\mathbf Y_{k_n}$ 驱动的 nodal form（eq. (9)；`fidelity item：eq(8)`、`eq(9)，PDF p.2 右栏`）。这避免把不同物理端口错误地压成单一方向。
5. **组装并求解全局网络。** 把各组的 $\mathbf Y_{k_n}$ 按节点映射插入
   \[
   \mathbf{i}_{\mathbf N,t+\Delta t}=\mathbf{Y}_{\mathbf N}\mathbf{v}_{\mathbf N,t+\Delta t}
   \]
   （论文 §II-A，eq. (10)；`fidelity item：eq(10)，PDF p.2 右栏`），用 sparse LU 等方法求当前节点电压，再回代各组 eqs. (3)、(4) 更新状态。开关位置或 piecewise-linear segment 未变时，$\mathbf Y_{\mathbf N}$ 不变；发生变化才更新受影响贡献（§II-A，eq. (10) 后说明）。若某一组直接用 nodal equations 或含 nonlinear device，则把它放入 MANA：
   \[
   \mathbf b_{\mathbf N,t+\Delta t}=\mathbf A_{\mathbf N}\mathbf x_{\mathbf N,t+\Delta t}
   \]
   （eq. (12)；`fidelity item：eq(12)，PDF p.2 右栏`），可在迭代中更新 Jacobian，而不必把该组重新写成全局 state-space。
6. **时间推进、事件与并行。** 每个时间点依次执行稳态初始化、推进、确定 switch permutation、更新 history 和全局矩阵、求 nodal system、回代状态，再进入下一点（论文 §II-B 的 Step 1–9）。步骤 3–6 与步骤 8 的组内工作可并行；论文没有给出 FPGA 映射、fixed-point 位宽或专用硬件实现，不能把 CPU 实时结果外推成 FPGA 结果。RLC discontinuity 点使用 halved-time-step Backward Euler，这是该验证案例的事件处理规则（§III-A，Figs. 3–4）。
7. **稳态初始化。** 令 $s=j\omega$，并以
   \[
   \tilde{\mathbf X}=(s\mathbf I-\mathbf A_k)^{-1}(\mathbf B_{k_i}\tilde{\mathbf U}_i+\mathbf B_{k_n}\tilde{\mathbf U}_n)
   \]
   求初始 phasor state（eq. (13)；`fidelity item：inline s=jω`、`eq(13)，PDF p.3 左栏`）；再用 $\mathbf H=(s\mathbf I-\mathbf A_k)^{-1}$ 的 eqs. (14)、(15) 得到内部和节点输出，取实部初始化 $t=0$ 的 history（`fidelity item：eq(14)`、`eq(15)`、`inline I 与 H 定义，PDF p.3 左栏`）。

在 HVDC 例中，整流侧被拆成四组：交流源和阻抗为 V-type，切换电容和固定滤波器为 I-type，变压器/晶闸管整流器/平波电抗器为 V-type；逆变侧仍用 state-space 方法（论文 §III-B，Fig. 5）。这说明接口可以跨越不同建模范式，但也说明分组边界和端口方向是建模者的责任，论文并未给出自动最优分组器。

## § 6 — 核心数学推导

### 6.1 从连续状态到离散端口

连续模型的状态 $\mathbf x$ 是储能元件的记忆，$\mathbf u$ 是输入，$\mathbf y$ 是输出（eq. (1)，`fidelity item：eq(1)`）。trapezoidal rule 把一个时间步两端的输入都纳入更新：

\[
\mathbf x_{t+\Delta t}=\hat{\mathbf A}_k\mathbf x_t+\hat{\mathbf B}_k\mathbf u_t+\hat{\mathbf B}_k\mathbf u_{t+\Delta t}
\]

（eq. (2)，`fidelity item：eq(2)，PDF p.2 左栏`）。这不是把动态系统变成无记忆电阻，而是把旧状态压缩到下一步可计算的 history 项，同时留下当前端口的代数未知量。

拆分内部输入和外部节点输入后，下一步状态由 eq. (3) 给出，输出由 eq. (4) 给出（`fidelity item：eq(3)`、`eq(4)，PDF p.2 左栏`）。取输出方程的 nodal 行并代入状态更新，论文得到 eq. (5)；其中所有已知的旧状态、旧输入和内部当前步注入合并成 $\mathbf y_{k_{hist}}$，所有当前步外部端口未知量的系数合并成

\[
\mathbf W_{k_n}=\mathbf C_{k_n}\hat{\mathbf B}_{k_n}+\mathbf D_{k_{nn}}
\]

于是有 eq. (6) 的 companion form（`fidelity item：eq(5)`、`eq(6)`、`eq(7)，PDF p.2 左栏`）。工程上，这一步把“内部动态”变成一次 history source 更新，把“跨组耦合”变成一个端口矩阵。

### 6.2 V-type、I-type 与全局 nodal 闭合

如果 $\mathbf u_n$ 是节点电压、$\mathbf y_n$ 是注入电流，$\mathbf W$ 就是 admittance，得到 V-type/Norton 关系；如果 $\mathbf u_n$ 是注入电流、$\mathbf y_n$ 是节点电压，$\mathbf W$ 就是 impedance，得到 I-type/Thevenin 关系（论文 §II-A，eq. (7) 后两段）。两种关系混合时，论文先写成

\[
\begin{bmatrix}\mathbf v_n^{\mathrm I}\\\mathbf i_n^{\mathrm V}\end{bmatrix}
=\begin{bmatrix}\mathbf v_{hist}\\\mathbf i_{hist}\end{bmatrix}
+\begin{bmatrix}\mathbf W_{II}&\mathbf W_{IV}\\\mathbf W_{VI}&\mathbf W_{VV}\end{bmatrix}
\begin{bmatrix}\mathbf i_n^{\mathrm I}\\\mathbf v_n^{\mathrm V}\end{bmatrix}
\]

（eq. (8)，`fidelity item：eq(8)，PDF p.2 右栏`），再把电流未知量移到左侧，得到

\[
\begin{bmatrix}\mathbf i_n^{\mathrm I}\\\mathbf i_n^{\mathrm V}\end{bmatrix}
=\mathbf{\Gamma}_{k_n}\begin{bmatrix}\mathbf v_{k_{hist}}\\\mathbf i_{k_{hist}}\end{bmatrix}
+\mathbf Y_{k_n}\begin{bmatrix}\mathbf v_n^{\mathrm I}\\\mathbf v_n^{\mathrm V}\end{bmatrix}
\]

（eq. (9)，`fidelity item：eq(9)，PDF p.2 右栏`）。把所有组的 $\mathbf Y_{k_n}$ 映射到共享节点，形成

\[
\mathbf i_{\mathbf N,t+\Delta t}=\mathbf Y_{\mathbf N}\mathbf v_{\mathbf N,t+\Delta t}
\]

（eq. (10)，`fidelity item：eq(10)，PDF p.2 右栏`）。因此当前步只需一次全局 nodal closure；组内状态可以在解出节点电压后并行回代。

论文还指出，若输出方程显式含 $\mathbf D_{1k}\dot{\mathbf u}$，可避免 I-type 组，但许多 state-space solver 并不直接提供该矩阵，所以保留 I-type 更通用（eq. (11)，`fidelity item：eq(11)，PDF p.2 右栏`）。使用 MANA 时，eq. (8) 的上半部分可以直接插入增广方程，避免矩阵求逆；其形式为

\[
\mathbf b_{\mathbf N,t+\Delta t}=\mathbf A_{\mathbf N}\mathbf x_{\mathbf N,t+\Delta t}
\]

（eq. (12)，`fidelity item：eq(12)，PDF p.2 右栏`）。这也是非线性支路可在较小 Jacobian 上迭代的数学入口。

### 6.3 稳态初值

稳态时把微分算子替换为 $s=j\omega$，其中 $j$ 是复算子、$\omega$ 是稳态角频率（`fidelity item：inline steady-state definition s=jω，PDF p.3 左栏`）。定义

\[
\mathbf H=(s\mathbf I-\mathbf A_k)^{-1}
\]

其中 $\mathbf I$ 是 identity matrix（`fidelity item：inline definition I identity matrix and H=(sI-A_k)^−1，PDF p.3 左栏`），则

\[
\tilde{\mathbf X}=\mathbf H(\mathbf B_{k_i}\tilde{\mathbf U}_i+\mathbf B_{k_n}\tilde{\mathbf U}_n)
\]

（eq. (13)，`fidelity item：eq(13)，PDF p.3 左栏`）。将该状态解代回输出方程，分别得到内部输出和节点输出的两项 phasor 关系（eqs. (14)、(15)，`fidelity item：eq(14)`、`eq(15)，PDF p.3 左栏`）。先用 eq. (15) 解节点 phasor，再解 eqs. (13)、(14)，最后取状态 phasor 实部作为时间域初始状态；所以启动瞬态不是人为清零，而是从电路稳态一致地初始化（论文 §II-B；后半句是由该流程作出的解释）。

### 6.4 非线性支路的局部线性化

对非线性磁化支路，在第 $j$ 次迭代用一段直线近似磁链—电流曲线：

\[
\phi_{L_t}=K^{(j)}i_{L_t}+\phi_0^{(j)}
\]

（eq. (16)，`fidelity item：eq(16)，PDF p.6 右栏`）。将其与 trapezoidal flux integration 结合，并改写成以电压为未知量的 branch current：

\[
i_{L_t}=\frac{\Delta t}{2K^{(j)}}v_{L_t}+\frac{1}{K^{(j)}}\left(\phi_{L_h}-\phi_0^{(j)}\right)
\]

（eq. (17)，`fidelity item：eq(17)，PDF p.6 右栏`）。因此每次迭代都要更新斜率项对应的 branch admittance 和 history 注入；eq. (12) 的矩阵就成为当前线性化点的 Jacobian，反复分解直到收敛（论文 §IV；公式和结构由上述两个 fidelity item 支持）。

## § 7 — 实验设计与结论

### RLC 开关案例

- **提出了什么问题：** 混合 I-type/V-type 组能否在没有拓扑限制的情况下处理开关瞬态。
- **设计了什么实验：** 使用等效 **500-kV** 交流系统切入以电容为主的 RLC 支路，开关在 **0.05 s** 闭合，并以 **5 μs**、**50 μs** 两个 $\Delta t$ 运行；SSN 与 MANA 在不连续点都采用 halved-time-step Backward Euler（论文 §III-A，Fig. 2；数值为 `fidelity item：RLC case reported values，PDF p.3–4`）。
- **问题的答案：** Fig. 3 的开关电流及 Fig. 4 的闭合瞬间放大图显示两种方法结果一致，支持端口混合和事件处理的数值等价性；它只覆盖简单 RLC，不足以证明大规模实时性能。

### HVDC 系统

- **提出了什么问题：** SSN 能否把 state-space 组与 nodal/不同端口类型组合起来，复现具有传播延迟、滤波器和晶闸管的复杂直流系统。
- **设计了什么实验：** 采用 **1000-MW** HVDC 链路，把 **500-kV、5000-MVA、60-Hz** 网络连接到 **345-kV、10000-MVA、50-Hz** 网络；整流器和逆变器为 12-pulse converters，中间是 **300-km** distributed-parameter line（含 propagation delay）和两个 **0.5-H** 平波电抗器，每侧滤波/电容总量 **600 Mvars**，整流侧 **300 Mvars** 电容拆分并在 **1.5 s** 切入（论文 §III-B，Fig. 5；`fidelity item：HVDC system values，PDF p.4 左栏`）。整流侧四组按 V/I 类型分开，逆变侧保留原 state-space 方法；以固定 **25 μs** 步长与 SPS 比较（`fidelity item：HVDC comparison integration and jitter time step，PDF p.4 右栏`）。
- **问题的答案：** Figs. 6–8 的波形匹配很近，支持 SSN 与 SPS 在该 HVDC 工况下的一致性。直流电流的小差异来自晶闸管 turn-on/turn-off 细节无法完全复现，低频 jitter 来自 **25 μs** 的开关采样步长（论文 §III-B；时间数值绑定同一 fidelity item）；因此结果不能被解释为所有 thyristor event compensation 都已解决。

### Breaker test setup

- **提出了什么问题：** 在需要多故障、多断路器重复研究的 state-space solver 中，分组是否能把不可实现的 switch-matrix 预计算变成可管理的规模。
- **设计了什么实验：** 测试系统为 **50-Hz、225-kV** 网络，源阻抗 **R=1.27 Ω、L=63.5 mH**，PI section 电容 **1×10^-14 F/km**，正序参数 **60 mΩ/km、1.27 mH/km**，零序参数为其三倍，负荷 **P=50 MW、Q=0**，故障位置 F1–F4、断路器 BR1–BR2（论文 §III-C，Fig. 9；`fidelity item：breaker setup values，PDF p.4 右栏`）。系统拆成五个 SSN groups、九个 nodal points；在 F3 于 **100 ms** 施加 phase-a-to-phase-b fault，**150 ms** 消失，以 **25 μs** 步长观察 CT1/BR2 电流（Fig. 10；`fidelity item：breaker simulation values，PDF p.4 右栏`）。若整网一次性预计算，需要 **2^22** 组 state-space matrix sets；论文的五组方案把最大组合数降为 **2^7**（`fidelity item：breaker state-space precalculation count` 与 `SSN breaker combination reduction，PDF p.4 下部右栏`）。
- **问题的答案：** Fig. 10 中 SSN 与 SPS 的 CT1 电流一致，且组合数显著下降，支持“局部开关 + 节点接口”对该重复故障测试的价值。这里的 **2^22 → 2^7** 是预计算集合数量，不等于所有运行时间、内存和矩阵分解成本都按同一比例下降。

### Hard real-time

- **提出了什么问题：** 分组与并行是否足以在实际硬实时平台上满足最坏时间步。
- **设计了什么实验：** 在单台 **3.2-GHz Xeon i7 Quad-core PC**、RedHat Linux kernel 上运行 SPS 实现；HVDC 使用三个 core（整流侧 SSN、逆变侧 state-space、控制），breaker setup 使用一个 core（论文 §III-D；`fidelity item：real-time platform values`）。测量不包含 I/O 设备；Table I 报告 HVDC 最坏步长 **10 μs/3 CPUs**，breaker test **21 μs/1 CPU**（`fidelity item：Table I hard real-time time step，PDF p.6 左上`）。
- **问题的答案：** 两个案例的最坏计算步长均被作者判断为适合 hard real-time，说明并行化和局部分组在目标平台上有效。但作者也明确提醒，不同 simulator 的硬件技术差异很大，仅凭 timing 数值不能公平排序求解器效率（论文 §III-D，Table I 后段）。

### 非线性模型

- **提出了什么问题：** 能否在 SSN 自身框架中，对非线性磁化支路做 simultaneous iterative solution，而不是使用带一步延迟、在较大步长下可能降低精度和稳定性的 current-injection 近似（论文 §IV 开头）。
- **设计了什么实验：** 在 **12.5-kV** 配电系统中选三段 state-space sections SS1–SS3，其余网络留在 MANA；变压器磁化支路用 piecewise-linear flux-current curve。场景为 XFMR 母线 **4 Ω** phase-a-to-ground fault，**20 ms** 发生、**133 ms** 清除，断路器同在 **133 ms** 打开并于 **203 ms** 重合；使用 **50 μs** 步长、两个磁化支路，并与 EMTP-RV simultaneous iterative solver 对比（论文 §IV，Figs. 11–14；`fidelity item：nonlinear test system values`、`eq(16)`、`eq(17)`、`nonlinear scenario values`、`nonlinear validation values`）。
- **问题的答案：** Fig. 13 的高压侧电流与 EMTP-RV 一致，Fig. 14 显示解点保持在对应非线性线段上，且每个时间点两个磁化支路都收敛；这支持局部 Jacobian 迭代的可行性，但论文没有给出迭代次数分布、失败回退策略或实时最坏界。

## § 8 — Take-aways

### 五句话

第一，SSN 把 state-space 组的内部动态和 nodal analysis 的当前步网络闭合放进同一个求解流程。第二，离散后每组都可以输出 history term 加端口矩阵，因此 Norton、Thevenin 和 mixed-type 组能够共同接入全局节点方程。第三，论文的 RLC、HVDC、breaker 和 nonlinear 案例都与相应参考求解器相符（§III–§IV，Figs. 3–4、6–8、10、13–14）。第四，分组把开关组合和非线性迭代局部化，并提供组内并行入口，但收益依赖分组质量。第五，实时结果证明了目标 CPU 案例的可行性，却没有证明任意拓扑、任意规模或 FPGA fixed-point 实现都满足同样的最坏时限。

### 三句话

SSN 的核心不是新的器件模型，而是把 state-space 子系统变成可组装的离散端口。这样做在示例中同时改善了开关矩阵预计算、组内并行和非线性求解的组织方式。其一般性仍受分组、接口规模、矩阵更新和事件处理的最坏情况约束。

### 一句话

把有记忆的局部动态保留在 state-space，把跨组耦合交给一次 nodal solve，是论文实现可扩展 EMT 仿真的关键折中。

## § 9 — 最脆弱的假设

**失败代价最大的假设是：可以选出一组固定、足够局部的边界，使开关和非线性变化主要留在组内，而跨组端口的维数和更新成本不会反过来主导计算。** 这不是“任意拓扑”四个字自动保证的性质，而是 SSN 获得矩阵集合缩减、并行和小 Jacobian 的前提（论文 §II-A、§II-B；基于机制的推断）。

它可能在以下情况失效：开关跨越多个边界、每个事件都改变多个组的端口矩阵，或强耦合的非线性支路恰好位于接口。此时全局 $\mathbf Y_{\mathbf N}$ 需要频繁重建和分解，组内并行的等待时间增加，甚至需要把大部分网络重新并入一个组；若 piecewise-linear 迭代在膝点反复切换，所谓“较小 Jacobian”也可能被迭代次数抵消。论文给出的证据是示例中预计算集合从 **2^22** 降至 **2^7**、HVDC/Breaker 最坏步长为 **10 μs/3 CPUs** 和 **21 μs/1 CPU**，以及两个磁化支路在 **50 μs** 步长下收敛（论文 §III-C、§III-D、§IV；分别对应 `fidelity item：2^22`、`2^7`、Table I 和 `nonlinear validation values`）。

缺少的证据同样关键：没有随组数、接口节点数、开关跨界程度增长的 scaling 曲线，没有全局矩阵重建/稀疏 LU 的分解占比，没有非线性不收敛时的最坏迭代上界，也没有带 I/O 的硬实时测量。因而最稳妥的结论是“固定分组在所示案例有效”，而不是“固定分组对所有网络都可扩展”。

## § 10 — 最小复现实验

一周内最值得做的是先复现 RLC，再用同一代码的计数器复核分组机制，而不是直接重建完整 HVDC。

1. **数据和模型。** 按 Fig. 2 建一个 500-kV 等效交流源切入以电容为主的 RLC 支路，设置 0.05 s 合闸；分别运行 SSN 的 I-type/V-type 两组和一个 MANA 参考，使用 5 μs、50 μs 步长（论文 §III-A；`fidelity item：RLC case reported values`）。
2. **实现对象。** 实现 eqs. (1)–(10) 的最小版本：组内状态用 trapezoidal companion update，输出 history term 与端口矩阵，组装一次全局 nodal matrix；在事件点实现论文所述的 halved-time-step Backward Euler（论文 §III-A，Figs. 3–4；公式对应 `fidelity item：eq(1)`–`eq(10)`）。
3. **测量。** 记录开关电流全波形、合闸瞬间放大图、节点方程残差、每步矩阵是否重建、分解时间和总步长；再将两个三相子网按 Fig. 1 的连接方式分组，记录 monolithic 与分组的 switch-matrix set 数量。
4. **支持或反驳标准。** 若两种实现的波形在同一事件规则和数值精度下只差舍入/求解容差量级，且分组的接口闭合不引入稳定的事件错位，同时确实只更新受影响组，则支持论文核心机制。若出现可重复的波形偏差、节点 KCL 残差在事件后不收敛，或接口矩阵重建和分解抵消了计数收益，则反驳“该分组在此类系统中同时更高效且等价”的具体 claim；不要把一次代码错误误判为论文机制失败。

这个实验不能验证论文的全部实时结论：HVDC 的 thyristor 细节、三核调度、非线性 EMTP-RV 对照以及硬实时最坏步长仍需独立复现。

## § 11 — 最强反例设计

构造一个**开关跨界且接口强耦合的三相网络**：六个开关分散在多个组的边界附近，使每个 permutation 都改变不止一个组的端口关系；在其中一个共享端口放入带陡峭膝点的变压器磁化支路，并在故障切换时让其与节点电压同时变化。这个场景直接攻击 SSN 的关键前提，而不是泛泛地增加网络规模。

实验上，用同一网络、同一时间步、同一事件检测和同一 CPU，比较静态 SSN、monolithic state-space 和 MANA：记录每步全局 $\mathbf Y_{\mathbf N}$/Jacobian 重建次数、稀疏 LU 分解时间、非线性迭代次数、节点 KCL 残差、波形误差和最坏时间步。作为对照，论文的三相示例只需 **2^6=64** 个整体矩阵集合，而其两组分解报告 **2×2^3=16** 个集合，breaker 示例报告 **2^22** 降到 **2^7**（论文 §II-C、§III-C；均为相应 `fidelity item`）。

最有力的失败模式是：静态 SSN 仍能给出与参考解相同的波形，但接口更新和反复分解使最坏步长不再优于 monolithic solver，或非线性在某些事件步不收敛。这样可以区分“数值等价”与“可扩展/可实时”的两个 claim；若只观察波形而不测最坏成本，就会漏掉真正的反例。由于论文没有提供这种跨界、强非线性压力测试，能否通过仍属未验证问题。

## § 12 — Follow-up Research Idea

电气与控制领域对高影响工作的通常要求是：方法边界清楚、与权威参考求解器逐波形核对、在多种故障/开关工况下给出数值稳定性和工程可实现性证据；若声称 real-time，还要报告最坏步长、资源和调度条件，而不是只报平均速度。基于 §9 的局限，下面提出一个**候选想法**，不声称已有 novelty。

**想法：带可证伪资源契约的事件感知分区 SSN。** 把“如何分组”从一次性的建模选择改成 solver 的受约束决策变量：根据开关事件传播、接口节点数、端口矩阵变化率和非线性 Jacobian churn，在线或离线地选择 state-space/nodal 分区；每个分区必须输出保持固定端口维数的 Norton/Thevenin/mixed companion，并同时给出接口 KCL/KVL 残差、收敛状态和预计计算预算。若某事件使分区违反预算或收敛条件，solver 触发可记录的重分区或退回 MANA/monolithic 解，而不是静默地超时。

- **(a) 未满足的需求。** 论文证明了人工选择的固定分组在若干案例有效，却没有回答分组在跨界开关、强非线性和硬实时最坏情况下何时失效；事件感知分区直接针对这个缺口。
- **(b) 研究价值。** 成功的话，研究目标从“某些示例的矩阵集合减少”提升为“在给定接口、残差和最坏时间预算下仍保持当前步网络闭合”的可验证 solver contract。它可能把数值等价、稳定性和 real-time deadline 放在同一评价框架中，而不是只比较波形或平均 timing（这是候选价值判断）。
- **(c) 可借鉴工具。** 可借鉴电力网络的 graph/hypergraph partitioning、事件驱动调度、robust optimization，以及 passivity/energy-residual 监测；这些工具用于约束分区和回退条件，不应被当成本文已经采用的方法。
- **(d) 第一个证伪实验。** 先做 §11 的六开关跨界三相网络，加入一个膝点磁化支路；在同一 CPU 上与静态 SSN、monolithic state-space、MANA 对比。若事件感知策略无法同时保持参考波形、KCL/KVL 残差收敛和最坏步长预算，或重分区开销超过其节省，则候选想法被证伪。
- **(e) 与已有工作的实质区别。** 本文把分组视为建模者给定的灵活结构；候选方法把分组、监测、重分区和安全回退纳入 solver 的正确性与资源契约，并要求对最坏事件给出失败可见性。它不是简单增加一个 nonlinear block、换一类应用或把 $\mathbf Y$ 换成随时间变化的黑箱，而是改变“什么算作可部署 SSN solver”的问题定义。

相关工作的充分检索不在本次认证输入内，因此上述方向只能作为证据约束的候选研究问题；不能据此宣称 novelty、稳定性定理或已达到 FPGA 实时实现。
