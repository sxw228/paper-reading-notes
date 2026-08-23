# Modeling Method for DFIG-Based Wind Farm in High-Efficiency Real-Time Electromagnetic Transient (EMT) Simulations

- 作者：Yifan Liu, Jianzhong Xu, Yiyang Zhu, Zhaoxuan Tian, Chengyong Zhao, Gen Li
- 出处：IEEE Transactions on Power Electronics, Vol. 40, No. 9
- 年份：2025
- DOI：10.1109/TPEL.2025.3567136
- Zotero key：5WB6J2JA

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** 这篇论文要解决的不是“能否把一个 DFIG 风机算出来”，而是“能否在实时 EMT 仿真中保留风场内每台风机和集电线路的细节，同时把节点方程压缩到现有硬件能实时求解的规模”。传统 detailed model（DM）保留开关和内部节点，但大规模风场会遭遇节点数和矩阵维度共同造成的“dimensionality disaster”；单机或多机 aggregation 虽然能扩大规模，却会丢掉单机馈线、内部故障和振荡传播所需的信息。作者因此把目标定为：降低 DFIG 风机和风机串的外部节点数，并仍能恢复内部节点量。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个目标的重要性是工程性的。实时 EMT 仿真用于供应商设备选择、场站设计验证、并网稳定性研究和调度控制开发；这些任务既需要微秒级时间步，又常常需要知道“哪台风机、哪段集电线发生了什么”，仅有 PCC 聚合输出不够。[pdf:E01]（PDF 物理页 1，Introduction）

**基于证据的合理推断。** 论文真正试图守住的是“细节—实时性”这条 Pareto 前沿：它不追求替代器件级开关 DM，而是要在风场级问题上，把硬件预算从“每个内部节点都参与全局求解”转成“端口等值在线求解、内部量按需回代”。这也解释了为什么作者同时需要设备级 latency decoupling 和场站级 M-NFSS，而不是只做一种模型简化。

## § 2 — 前人工作与不足

**相关文献中的已有结论（按本文综述）。** 设备层面已有 DFIG 的 dq0 state-space、谐波模型、稳态非迭代求解和降阶同步稳定模型；但这些模型往往依赖状态空间积分，难以直接嵌入采用 nodal analysis 的 EMTP/RTDS 图形化元件网络。变流器层面，average-value model（AVM）允许较大步长，但忽略 switching 高频分量；switching-function model 保留 PWM 特征并有利于 AC/DC 解耦。场站层面，容量加权的单机 aggregation 和按特征聚类的多机 aggregation 能扩大风场规模，但会压掉单机与馈线细节。[pdf:E01]（PDF 物理页 1，Introduction）[pdf:E02]（PDF 物理页 2，Introduction）

网络加速也有三条既有路线。Transmission-line natural decoupling 受线路传播时间与长度约束；MATE 需要 node tearing 或 branch segmentation，并带来顺序网络求解；latency insertion method 会加入额外 L/C 和延迟，改变系统动态并限制步长。普通 NFSS 通过 Schur complement 消元减小外部网络，但当风机内部节点仍很多时，一次高阶矩阵求逆的收益受限。[pdf:E02]（PDF 物理页 2，Introduction）

**论文原文明确声称。** 本文的差异不是简单删掉更多状态，而是组合两层结构变化：先把 DFIG、变流器、滤波器和变压器的耦合改写为历史量驱动的受控源，使单台 WT 对外从 24 个节点降到 3 个；再对“风机 + π 型短线”串采用 M-NFSS，以“多次低阶消元”替代“一次高阶消元”，得到保留 3 相与地的四节点串等值。[pdf:E02]（PDF 物理页 2，贡献列表与 Section II 开头）

## § 3 — 重建作者的思考路径

下面是对作者思路的**基于证据的合理推断**，不是论文逐字给出的研究日志。

第一步，从工程失败模式出发：DM 的问题不只是每台风机计算复杂，而是所有设备节点被拼入同一个全局 nodal matrix，风机数量一增大，矩阵求解和硬件分区同时恶化。单纯 aggregation 虽快，却恰好删除了故障追踪和振荡传播最需要的单机信息。[pdf:E02]

第二步，观察 DFIG 风机内部存在“物理上强耦合、数值上相邻步变化较慢”的端口：大 DC 电容让 \(V_{\mathrm{dc}}\) 较平滑，AC smoothing reactor 让相电流 \(I_i\) 较平滑。若把当前步交叉耦合改用 \(t-\Delta t\) 的历史量，就能把 admittance coupling 变成受控电流源信号，从拓扑上切开定子/转子、变压器两侧和变流器子网络。[pdf:E02]（PDF 物理页 2，Section II 开头）

第三步，单机被压缩后，集电线路的收发端仍不能用同样办法完全解耦；若把整串一次做 NFSS，内部块 \(C\) 的阶数仍随 \(3m\) 增长。于是再利用风机串天然的链式拓扑：每次只把当前四端口等值与下一段线路/风机组成一个七节点小问题，消去 3 个内部节点，递归 \(m\) 次。[pdf:E04]（PDF 物理页 4，Eq. (18)–(20)）[pdf:E05]（PDF 物理页 5，Fig. 8 与 Eq. (21)–(22)）

第四步，为避免“等值快了但看不到内部”的代价，把每一级消元的参数预存，再从最终外端口电压反向回代各级内部节点。由此，作者把实时前向求解与内部量恢复拆成两个方向相反但共享参数的过程。[pdf:E05]

## § 4 — 核心 Intuition

把同一步内的强电气耦合改写成“上一时间步已经知道的端口注入”，就能让原本必须共同求解的风机子网络并行独立求解。再利用风机串的链式结构，逐段执行固定三阶 Schur complement，而不是一次求逆一个随风机数增长的大矩阵；最终只向全场网络暴露四节点端口，内部量则反向回代恢复。[pdf:E03]（PDF 物理页 3，Eq. (12)）[pdf:E05]（PDF 物理页 5，Fig. 8 与 Eq. (21)–(22)）

## § 5 — 具体方法与完整 Pipeline

以一条含 \(m\) 台 DFIG 风机、\(m\) 段短集电线的 35 kV string 为例，输入是设备参数、上一时步历史量、控制器输出和串首外部节点电压；输出是串的四节点 Norton 等值以及可回代的每台风机内部电压电流。

1. **DFIG 离散与端口化。** 从 abc 定转子电压、磁链和机械方程出发，经匝比折算与 Park 变换得到 dq0 矩阵式；以电流为状态，采用 implicit Euler 离散，并把 speed EMF \(e\) 当作历史量，形成 \(I=GU+J\) 的 Norton 形式。[pdf:E02]（PDF 物理页 2，Eq. (1)–(3)）[pdf:E03]（PDF 物理页 3，Eq. (4)–(10)）
2. **DFIG latency decoupling。** 将 \(G=G_1+G_2\) 取为 \(G_1=0,\ G_2=G\)，即全部 admittance coupling 改由 \(U(t-\Delta t)\) 驱动。定子和转子七个节点之间不再由 admittance 相连，只由受控电流源交换信号，耦合物理关系仍由历史源项携带。[pdf:E03]（PDF 物理页 3，Eq. (11)–(12) 与 Fig. 2）
3. **变压器与整机解耦。** 对含绕组电阻的 T 型变压器离散，把变压器 admittance 拆成保留两侧自项的 \(G_1\) 和延迟两侧互项的 \(G_2\)。整台 WT 随后被分成 machine-side、DC-side、grid-side 和 external circuit 四块；前三块分别用 \(U=Y^{-1}J\) 独立求解，对外只剩 3 个相节点。[pdf:E04]（PDF 物理页 4，Eq. (13)–(15) 与 Fig. 4）[pdf:E05]（PDF 物理页 5，Fig. 5）
4. **短线建模。** 每段短线使用考虑相间耦合的 π 型线路，\(R,L\) 为三相矩阵，参数由正序和零序量换算；离散后仍保留收、发两端。作者明确不对其套用 DFIG 式 latency decoupling，因为那只能拆开三相，不能拆开线路两端。[pdf:E04]（PDF 物理页 4，Eq. (16)–(18)）
5. **M-NFSS 递归端口消元。** 把外部/内部节点方程分块为 \(A,B,C\)。先将 \(WT_1+line_1\) 的 3 个内部节点消去得到 \(EM_1\)，再把 \(EM_1+line_2+WT_2\) 组成下一七节点小问题；重复 \(m\) 次得到四节点 \(EM_m\)。每级只做三阶计算，在线阶段不求逆 \(3m\) 阶内部块。[pdf:E04]（PDF 物理页 4，Eq. (19)–(20)）[pdf:E05]（PDF 物理页 5，Fig. 8 与 Eq. (21)）
6. **全场组装与内部量恢复。** 多条 \(EM_m\) 在 PCC 汇合；全局网络只见各串的四节点等值。求得外部电压后，按 \(U_{\mathrm{IN}}=Y_{22}^{-1}(J_{\mathrm{IN}}-Y_{21}U_{\mathrm{EX}})\) 逐级反向恢复内部节点，因此仍可观测各 WT 与线路。[pdf:E05]（PDF 物理页 5，Eq. (22)）
7. **实际执行平台。** 作者在 RTDS CBuilder 中实现 \(EM_1\) 与 \(EM_m\)，以 DM 和 AVM 为基线；另用 RCP 产生 grid-side converter 触发信号，通过 GTAI/GTAO 与 RTDS 连接做 HIL。论文没有报告 HDL、fixed-point word length、FPGA pipeline 或资源时序，因此不能把它解释成 FPGA 实现论文。[pdf:E06]（PDF 物理页 6，Fig. 9、Fig. 10 与 Validation 开头）

## § 6 — 核心数学推导

### 6.1 从 DFIG 微分方程到可解耦 Norton 端口

论文从

\[
U=RI+\frac{d\psi}{dt}+e,\qquad \psi=LI
\]

出发；\(U,I,\psi\) 包含定、转子 dq0 分量，\(L\) 的非对角块是定转子 mutual inductance，\(e\) 则含同步与滑差角速度引起的 speed EMF。[pdf:E03]（PDF 物理页 3，Eq. (5)–(7)）

采用 implicit Euler 后，

\[
L\bigl(I(t)-I(t-\Delta t)\bigr)
=\Delta t\bigl(U(t)-RI(t)-e(t)\bigr).
\]

作者把 \(e(t)\) 取为 \(e(t-\Delta t)\)，再做定、转子分块与反 Park 变换，得到

\[
\begin{bmatrix}I_s(t)\\I'_r(t)\end{bmatrix}
=
\begin{bmatrix}G_{11}&G_{12}\\G_{21}&G_{22}\end{bmatrix}
\begin{bmatrix}U_s(t)\\U'_r(t)\end{bmatrix}
+
\begin{bmatrix}J_s(t-\Delta t)\\J'_r(t-\Delta t)\end{bmatrix}.
\]

其中 \(G\) 可由 Park 矩阵和电感块逆矩阵构造。关键一步不是再近似 \(G\) 的数值，而是把其全部当前步电压乘积延迟一拍：

\[
\begin{bmatrix}I_s(t)\\I'_r(t)\end{bmatrix}
=G
\begin{bmatrix}U_s(t-\Delta t)\\U'_r(t-\Delta t)\end{bmatrix}
+
\begin{bmatrix}J_s(t-\Delta t)\\J'_r(t-\Delta t)\end{bmatrix}.
\]

于是当前步 nodal matrix 中不再有定转子 mutual admittance，原耦合变为已知历史电流注入。[pdf:E03]（PDF 物理页 3，Eq. (8)–(12)）

**工程直觉。** 这是用一拍相位滞后换取拓扑可分性。它不是删除电感耦合，而是把耦合从“同一步联立未知量”搬到“上一时步已知源项”。因此准确性依赖 \(\Delta t\) 相对端口动态足够小。

### 6.2 M-NFSS 的递归 Schur complement

对任一级七节点小网络，分块方程为

\[
\begin{bmatrix}A&B\\B^T&C\end{bmatrix}
\begin{bmatrix}U_{\mathrm{EX}}\\U_{\mathrm{IN}}\end{bmatrix}
=
\begin{bmatrix}J_{\mathrm{EX}}\\J_{\mathrm{IN}}\end{bmatrix}
+
\begin{bmatrix}I_{\mathrm{EX}}\\0\end{bmatrix}.
\]

消去内部节点得到 Schur complement：

\[
I_{\mathrm{EX}}=G_{\mathrm{EQ}}U_{\mathrm{EX}}+J_{\mathrm{EQ}},
\quad
G_{\mathrm{EQ}}=A-BC^{-1}B^T,
\quad
J_{\mathrm{EQ}}=BC^{-1}J_{\mathrm{IN}}-J_{\mathrm{EX}}.
\]

普通 NFSS 若一次处理整串，需要对随 \(m\) 增长的内部块 \(C\) 求逆；M-NFSS 每次只消去 3 个内部节点，因此执行 \(m\) 次固定三阶计算，最终得到含 abc 与 ground 的四节点等值。[pdf:E04]（PDF 物理页 4，Eq. (19)–(20)）[pdf:E05]（PDF 物理页 5，Eq. (21) 与正文）

消元并未不可逆地丢掉内部量。保存每级 \(Y_{22}^{-1}\) 与 \(Y_{21}\) 后，可用

\[
U_{\mathrm{IN}}=Y_{22}^{-1}
\left(J_{\mathrm{IN}}-Y_{21}U_{\mathrm{EX}}\right)
\]

反向恢复。[pdf:E05]（PDF 物理页 5，Eq. (22)）

**仍然不确定。** 论文没有给出 latency decoupling 的全局误差阶、稳定域或 passivity 证明，也没有给出递归回代在有限精度下的 condition number 传播。因此“固定三阶”说明了结构复杂度优势，但不等于已经证明任意参数、步长和风机数下都数值稳定。

## § 7 — 实验设计与结论

**问题 1：单台 \(EM_1\) 在正常动态下是否逼近 DM？** 作者在 NovaCor/RTDS 中令 \(n=m=k=1\) 且不含短线，风速在 \(t=3\) s 从 12 降到 6 m/s，随后在 \(t=15\) s 斜升到 16 m/s，最终回到 12 m/s；比较机械/电磁转矩、DC 电压和 P/Q。答案是 \(EM_1\) 对 DM 的平均误差低于 1%，HIL 有线路损耗与传输延迟造成的小误差；AVM 虽跟随趋势，却不能重现稳态附近的 switching ripple。[pdf:E06]（PDF 物理页 6，Fig. 11 的工况说明）[pdf:E07]（PDF 物理页 7，Fig. 11 结论）

**问题 2：故障下 latency-decoupled WT 是否仍准确？** 在 Fig. 10 的 Fault1 于 \(t=0.1\) s 触发单相接地短路，记录 P/Q、DC 电压、PCC 与 grid-side converter 出口 A 相电压。\(EM_1\) 与 HIL 的平均相对误差均低于 3%，小于 AVM；但 switching-function model 与 AVM 都不能完整反映变流器出口高频谐波，所以作者明确保留 DM 作为器件级仿真的必要模型。[pdf:E07]（PDF 物理页 7，Section IV-A-2）[pdf:E08]（PDF 物理页 8，Fig. 12）

**问题 3：递归 \(EM_3\) 能否保持整串故障响应？** 由于一个 RTDS core 最多容纳 3 个 detailed WT，作者令 \(k=n=1,m=3\)，在 Fault2 施加三相短路并比较全场 P/Q。答案是 \(EM_3\) 跟随 DM，平均相对误差低于 3.6%。[pdf:E07]（PDF 物理页 7，Section IV-A-2）[pdf:E08]（PDF 物理页 8，Fig. 13）

**问题 4：频域端口特性是否一致？** 作者扫描 1–100 Hz（1 Hz 间隔）和 1000–2000 Hz（2 Hz 间隔）。大多数频点 \(EM_3\) 与 DM 接近；25–27 Hz 的幅值相对误差达到 15%，26 Hz 相角分别为 3.047 与 -3.03 rad，作者把相角表观反号解释为接近 \(\pm180^\circ\) 跳变，且指出 1 Hz 最小扫描间隔限制了分辨率；总体波形平均相对误差低于 3%。[pdf:E07]（PDF 物理页 7，Section IV-A-3）[pdf:E08]（PDF 物理页 8，Fig. 14 与相邻正文）

**问题 5：实时硬件效率是否提高？** Table II 比较每个 NovaCor core 可容纳的 WT 数：在 2.17/3.33/4.17/5.56/10 μs 下，DM 分别为 1/2/2/3/3，AVM 为 1/2/3/3/3，\(EM_1\) 为 2/3/3/5/9。因而 10 μs 时 \(EM_1\) 以 DM 的 33.3% 资源实现三倍规模。作者同时承认该工况下瓶颈已转为模型计算，\(EM_m\) 没有表现出明显的额外资源节省；其价值主要是消除线路新增节点，为更大步长或更长 string 留出节点上限。[pdf:E08]（PDF 物理页 8，Table II）[pdf:E09]（PDF 物理页 9，Section IV-B）

**问题 6：能否运行保留单机信息的大场站？** 作者用 4 台 NovaCor、\(n=4,m=5\)、\(EM_5\)，单机 2.5 MW、总场站 250 MW，运行三相故障和振荡传播工况；把 \(WT_1\) 控制器 \(K_p\) 从 0.1 改为 100 后，振荡从 \(t=1\) s 起出现，并在 \(t=4\) s 后显著增强，其他 WT、group 和 station 随后也出现传播趋势。[pdf:E09]（PDF 物理页 9，Section IV-C 与 Fig. 15–16）由 \(250/2.5=100\) 可得模型容量对应 **100 台 WT**；这是依据论文报告容量作出的算术推断，论文正文原句只写 “hundreds of WTs”，并未逐字给出 “100 WT”。

测试参数包括：单机 2.5 MVA、0.69 kV、50 Hz，converter switching frequency 2000 Hz、DC-bus capacitance 20000 μF，grid-side/machine-side filter inductance 分别为 0.3/0.12 mH；各 WT 和线路取相同设置，控制为 RTDS 标准 vector control 与 PWM。[pdf:E06]（PDF 物理页 6，Table I 与相邻正文）

**不得外推的范围。** 实验支持的是给定参数、控制器、步长和 RTDS 平台上的波形/阻抗/容量表现；它没有证明异构风机、弱网多控制交互、更长时间运行、极端 fault switching、任意 \(\Delta t\) 或其他实时平台上的同等误差与稳定性。

作者在 Discussion 还明确给出一个工程 trade-off：模型集成度越高，效率越高，但用户修改内部拓扑的灵活性越低；因此 \(EM_m\) 相比 \(EM_1\) 的进一步集成并非无代价。[pdf:E10]（PDF 物理页 10，Section IV-D 与 Conclusion）

## § 8 — Take-aways

### 5 句话

1. 论文用 latency decoupling 把 DFIG、变压器和变流器子网络的当前步互耦改成历史受控源，使单台 WT 对外节点从 24 个降到 3 个。[pdf:E02]
2. M-NFSS 沿风机串递归做三阶 Schur complement，以多次低阶端口消元替代一次 \(3m\) 阶内部块求逆，并可反向恢复内部节点。[pdf:E05]
3. 在给定 RTDS 测试中，\(EM_1/EM_3\) 的正常、故障与阻抗结果总体接近 DM，但 25–27 Hz 出现局部幅值偏差，器件级高频谐波仍需 DM。[pdf:E07][pdf:E08]
4. 10 μs 时每核可放 9 个 \(EM_1\) 而 DM 只能放 3 个，即报告资源用量为 DM 的 33.3%。[pdf:E08][pdf:E09]
5. 250 MW、单机 2.5 MW 的场站容量对应 100 台 WT，论文展示了内部故障和人为激发振荡的传播可观测性，但尚未给出延迟模型的稳定性证书。[pdf:E09]

### 3 句话

作者的关键贡献是把设备耦合与场站消元都改造成适合预存参数和并行执行的端口问题。实验证明它在特定 RTDS 设置下能以约三分之一 DM 资源保留单机级信息，但不能替代器件级 switching DM。最需要补足的不是更多波形，而是一步延迟在弱阻尼、多控制器和不同步长下何时仍保持稳定与正确的可验证边界。

### 1 句话

这是一种用“一拍历史耦合 + 递归三阶端口消元”换取大规模实时 EMT 可解性的 refined wind-farm model，速度收益明确，稳定适用域仍未被形式化闭合。

## § 9 — 最脆弱的假设

最脆弱的假设是：**所有被延迟的交叉端口量在一个时间步内足够平滑，因此用 \(t-\Delta t\) 替代 \(t\) 不会改变研究关心的稳定性与阻抗结论。**

这个假设贯穿核心贡献。DFIG 的全部 mutual admittance 被移到上一时步，speed EMF 也作历史量处理；变流器解耦依赖大 DC capacitor 与 AC smoothing reactor 使 \(V_{\mathrm{dc}}\) 和 \(I_i\) 相邻步变化平滑。[pdf:E02]（PDF 物理页 2，Section II 开头）[pdf:E03]（PDF 物理页 3，Eq. (8)–(12)）一旦该条件在弱阻尼谐振、controller interaction、故障开断或步长增大时失效，新增的一拍相位滞后可能移动阻抗交点或离散极点。此时不仅波形误差变大，方法用来研究“振荡传播/小扰动稳定性”的核心用途也可能给出错误稳定性判断。

论文提供的支持是：给定步长下时域误差多为 1%–3.6%，两段频率扫描总体贴合，且 100 台容量工况能实时运行。[pdf:E07][pdf:E08][pdf:E09] 但它缺少三项决定性证据：没有随 \(\Delta t\) 的稳定域/误差收敛扫描，没有覆盖异构控制器与弱网高 Q 共振，也没有证明端口 passivity 或 recursive composition 后的稳定性保持。25–27 Hz 已出现 15% 幅值偏差，虽然作者给出了扫描分辨率和相角 wrap 的解释，这仍是该假设最值得压力测试的已见信号。[pdf:E07][pdf:E08]

## § 10 — 最小复现实验

一周内不必复现完整 100-WT RTDS 系统；最小实验应直接检验“延迟端口化与递归消元是否在目标步长下保持端口行为”。

1. **数据与模型。** 使用 Table I 的 DFIG、converter filter、transformer 与 line 参数，先实现一个线性化三相 Norton WT，再串联 3 台形成与论文 \(EM_3\) 对应的小系统。[pdf:E06]
2. **三个求解器。** A 为同一步 monolithic nodal solve；B 为 Eq. (12) 的一步 latency-decoupled \(EM_1\)；C 在 B 上增加 Eq. (21) 的三级 M-NFSS，并用 Eq. (22) 回代内部节点。[pdf:E03][pdf:E05]
3. **激励。** 做一个小幅 PCC voltage step、一个 0.1 s 单相接地故障，以及 1–100 Hz 的小信号扫频；把 \(\Delta t\) 依次设为 2.17、5.56、10 μs，与论文 Table II 的关键点对齐。[pdf:E07][pdf:E08]
4. **测量。** 比较 PCC current、DC voltage、每台 WT P/Q、端口 impedance 幅相、内部回代误差、每步最大矩阵阶数和 wall-clock time。所有误差以 A 为基准。
5. **支持标准。** 若 10 μs 下 B/C 的时域平均相对误差低于论文故障测试量级 3.6%，扫频除 \(\pm180^\circ\) wrap 邻域外没有新的大偏差，且 C 与 B 的外端口结果在数值容差内一致，同时 C 每级只需求解三阶内部块，则核心 mechanism 获得最小支持。[pdf:E05][pdf:E07]
6. **反驳标准。** 若减小 \(\Delta t\) 仍不收敛于 A、B/C 出现 A 没有的增长振荡、M-NFSS 回代误差沿级数系统性放大，或 25–27 Hz 一类偏差扩大并改变稳定结论，则核心 claim 被反驳或至少其适用域必须收缩。

这个实验不验证“NovaCor 资源占用 33.3%”，因为那需要同一 CBuilder 实现与真实硬件；它只验证论文最核心、也最容易证伪的数值 mechanism。

## § 11 — 最强反例设计

最强反例不是再加一种普通故障，而是专门构造一个 **DM 稳定、latency-decoupled model 不稳定，或二者对振荡源作出相反判断** 的弱阻尼端口网络。

具体做法是把 3–5 台控制参数略异构的 DFIG 连接到高线路电感、低 short-circuit ratio 的电网，并调节 grid-side current loop / PLL，使 DM 在 20–40 Hz 形成接近但尚未穿越 Nyquist 临界点的高 Q resonance。该频带刻意覆盖论文在 25–27 Hz 已观察到 15% 幅值差的位置。[pdf:E07][pdf:E08] 然后同时扫 \(\Delta t=2\)–20 μs、故障清除角和控制器 bandwidth，比较：

- monolithic DM 与 \(EM_m\) 的 impedance Nyquist encirclement、离散极点和 ring-down damping ratio；
- 相同扰动下振荡究竟衰减还是增长；
- 延迟引入的相位是否随 \(\Delta t\) 近似线性增加，并在临界点翻转稳定性结论；
- 回代到各 WT 的振荡源排序是否一致。

若 DM 在全部重复试验中衰减，而 \(EM_m\) 稳定地预测增长，或反之，这就排除了“只是曲线局部误差”的宽松解释，直接击中论文把模型用于 small-disturbance stability、fault traceability 和 oscillation propagation 的主张。反过来，若在接近临界稳定边界时两者仍保持相同 Nyquist 结论与源定位，才是比现有波形拟合更强的支持。

## § 12 — Follow-up Research Bet

这是一个**候选研究押注**：把 DFIG 风机串从“被动汇集功率的网络”改造成**可编程振荡传播介质**。本卡没有检索外部相关全文，因此下面只说明它如何从本文证据推出，不声称 literature novelty。

**新问题与首次新能力。** 新问题不是怎样再压缩几个节点，而是：能否把沿风机串有意布置的控制器异质性当作空间材料参数，使某一频带的集体振荡出现可设计的传播、驻波或局域模态？若成立，这条论文路线第一次新增的能力将是：在保持逐台风机 EMT 细节的实时实验里，先指定“振荡能量应在哪个频带、哪几台 WT 上形成何种空间模态”，再由控制参数的空间排列实现该模态，而不是只能在振荡发生后重放其传播过程。这里的“第一次”仅指相对本文当前的仿真任务，不代表对全部文献的首创判断。

**核心因果链与基本设计变量（基于证据的机制假设）。** 每台 WT 的 current loop、PLL 或文中用于激振的 \(K_p\) 改变局部端口阻抗；“WT + 三相耦合 π 型短线”构成一个空间 unit cell；将每一级 Eq. (21) 的端口关系在线性化频域改写为三相 cell transfer operator 后，不同 unit cell 的算子沿物理串联次序复合，使相邻 WT 响应发生频率相关的相长或相消叠加；周期排列由此形成传播带和禁带，故意引入的缺陷 cell 则在禁带内形成空间局域模态。基本设计变量至少包括：1）高/低 controller parameter 的取值、占比、排列次序与空间周期；2）unit cell 内集电线的 \(R/L/C\)、长度及 WT—line 配对方式；3）用于读取 band structure 的激励位置与频率。它改变了研究目标、可控变量、状态表示和实验对象：状态不再只是一组时域波形，而是“频率—WT 位置”上的复数模态形状与 unit-cell multiplier。

**论文特异依据。** 这个机制依赖本文的具体结构，而非给原方法加一个通用模块。Eq. (18) 给出保留相间耦合的 π 型短线，Eq. (21) 把整串写成逐级组合的低阶端口映射，Eq. (22) 又能恢复每一级内部节点，因此同一实时模型既能形成空间 cell，也能观察 cell 内模态。[pdf:E04][pdf:E05] 控制系统并未被平均化，CBuilder/RTDS 实现保留逐台 WT 控制与内部量。[pdf:E06] 更关键的是，作者把 \(WT_1\) 的 \(K_p\) 从 0.1 改为 100 后，振荡从该机扩展到其他 WT、group 和 station，Fig. 16 已展示“一个局部控制参数—全串传播”这条因果链的起点；Fig. 14 的 1–100 Hz impedance scan 则说明论文已有观察频率选择性端口行为的实验接口。[pdf:E08][pdf:E09] Table II 和 \(EM_5\) 大场站实验表明该问题可以进入多 WT 实时尺度，而不必先退回 aggregation。[pdf:E08][pdf:E09]

**最大研究收益与科学风险。** 最大收益不是得到一个更稳妥的等值模型，而是建立“converter control 作为空间材料”的可实验科学对象：研究者可以在 utility-scale refined EMT 平台上合成、移动和拆分集体模态，并检验空间周期、缺陷和线路耦合怎样共同决定传播。这会把风场振荡研究从单一源定位推进到可设计的 band structure。最大的科学风险是所谓禁带其实只来自平均阻尼增大、局部增益失配或一拍 latency 的数值色散；此外，controller saturation、PWM 谐波和风机参数散布可能破坏线性 unit-cell 假设。若同一现象不能在 monolithic DM 或 HIL 中重现，这个押注就只制造了 \(EM_m\) 的离散化现象。

**区分机制与替代解释的最小实验。** 构造 6 台 WT、3 个二机 unit cell 的短串，固定两组 controller parameter 的取值与数量，比较三种布置：均匀参数、周期交替 \(ABABAB\)、以及保留相同 \(A/B\) 数量但打乱空间次序的非周期布置；三者使用相同线路、工作点和总注入能量。由首台 WT 注入同一组小信号扫频，利用 Eq. (22) 记录各 WT 的内部电压、电流和 \(P/Q\)，同时在 \(EM_6\) 与 monolithic DM 中计算沿串传递衰减、相位推进和模态形状；随后把空间周期从 \(AB\) 改为 \(AABB\)。如果只有周期布置产生清晰频带缺口，缺口边缘随周期改变而按 unit-cell transfer operator 的特征值预测移动，并且 DM 与 \(EM_6\) 给出相同空间模态，那么“周期干涉形成 band structure”胜过“只是平均阻尼或参数离散”；若随机布置产生同等衰减，或现象只存在于 \(EM_6\)，核心机制即被反驳。

**与本文及其综述中最近工作的实质区别（候选判断）。** 本文的问题是以更少外部节点复现给定风场，机制是历史量解耦与 recursive Schur complement，representation 是四节点 Norton 等值加内部回代，experimental object 是同参数 WT 串、一个被大幅修改 \(K_p\) 的振荡源以及 accuracy/resource 对比。本文综述的 aggregation、AVM 和 impedance equivalent 也主要改变模型粒度或外部特性。这个 bet 的问题是反向设计内部传播，机制是空间周期阻抗造成的干涉，representation 是 unit-cell transfer operator、multiplier 与内部 mode shape，experimental object 是受控排列且保持参数多重集合相同的异质 WT 串。由于没有读取这些方向的外部全文，这一比较不能支持 novelty 声明。

**Wild-card alternative（一句话）：** 不改变 controller 的空间排列，改用多点相位编码的小信号主动激励与少量内部测量 tap，通过 Eq. (21)–(22) 的前向/反向端口映射做集电线与变压器参数层析，其独立设计变量是激励码的相位—频率结构和 tap 的位置—数量。[pdf:E05]
