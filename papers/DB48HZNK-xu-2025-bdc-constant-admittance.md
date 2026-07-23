# Electromagnetic Transient Equivalent Modeling and Real-Time Simulation Method for Bidirectional DC/DC Converters

**作者：** Mingwang Xu；Wei Gu；Yang Cao；Shuaixian Chen；Fei Zhang；Wei Liu  
**出处：** IEEE Transactions on Industry Applications, Vol. 62, No. 1, Jan./Feb. 2026  
**年份：** 2025（online publication；卷期出版于 2026）  
**DOI：** 10.1109/TIA.2025.3574123  
**Zotero key：** DB48HZNK  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“双向 DC/DC converter（BDC）能否被仿真”，而是一个更具体的工程矛盾：详细开关模型能保留高频暂态和器件内部量，却让每次开关动作都可能改变节点导纳矩阵；多模块级联后，节点数、矩阵维数和频繁重分解的成本一起增长。BDC 又是 power electronic transformer（PET）的基本模块，常见于高压侧串联、低压侧并联等结构，因此模型一旦随模块数失去可扩展性，离线 EMT 仿真和 HIL 实时测试都会很快碰到计算上限。论文据此提出“恒定导纳 + 无接口时延”的 EMT 等效模型，目标是在不退化为平均模型的前提下，使多模块网络仍能用固定网络 stamp 和并行子系统求解。[pdf:E01]（PDF 物理页 1，Abstract、Introduction A）

这里的“恒定导纳”是指对外网络看到的等效电导/电阻系数在开关过程中不变，因而全局节点矩阵不必随每个门极事件反复求逆；开关状态的变化被搬到历史源和预测校正项中。其价值有三层：一是降低大规模 BDC 阵列的求解成本；二是避免传统端口解耦用上一时刻接口量而引入的一个或半个步长时延；三是保留电容电压、变压器电流和桥臂开关量等 EMT 内部状态，而不是只保留低频平均行为。作者明确把准确度、效率和 RT-LAB 上的实时可执行性作为验证对象。[pdf:E02]（PDF 物理页 2，Introduction C）

## § 2 — 前人工作与不足

论文自己的文献综述把既有方法分成四类。第一类是 node-dimension reduction/NEM：能把复杂电力电子拓扑化成低阶网络，但作者认为其求解串行性仍高，而且模型并非恒定导纳。第二类是 generalized state-space averaging、frequency-dependent averaged model 和大小信号模型：它们适合稳态或稳定性分析，却可能丢掉高次谐波、器件级问题及快速 EMT 细节。第三类是 port modeling 和 hierarchical parallel simulation：已有工作能在 FPGA 上以 250 ns 步长运行串并联 DC/DC 系统，也能让级联 PET 并行求解，但端口方程把内部变压器与桥臂动态藏在黑盒后面。第四类是 decoupling：以慢动态电容为接口、topology-aware partition、semi-implicit leapfrog 或 predictive correction 换取并行性；代价分别是接口时延、半步错位，或显式预测带来的精度与稳定性问题。[pdf:E01]（PDF 物理页 1，Introduction B）[pdf:E02]（PDF 物理页 2，Introduction B）

因此，论文声称的缺口不是泛泛的“以前不够快”，而是三个约束尚未同时满足：导纳矩阵在开关事件下保持恒定；不同子系统在同一个全局步内解耦而不借用旧接口量；模型仍能回算 converter 内部电压、电流。需要强调的是，这些 prior-work 判断来自本文的综述，本卡没有跨论文独立核验，不能据此把作者的 novelty 表述升级成已验证的文献结论。

## § 3 — 重建作者的思考路径

以下是基于论文所列失败模式重建的合理推断，不是作者逐字叙述。

1. 先把瓶颈定位在“开关改变网络 stamp”而不是普通的微分方程积分。若每个 BDC 的每个桥臂都直接进入全局节点矩阵，模块数和开关频率会共同放大矩阵重构成本。
2. 不采用平均模型，因为目标仍包括高频变压器波形、桥臂电压电流、短路暂态和双向功率流。于是自然选择电容电压与变压器电流为能量状态，并用二值电阻表示开关状态。
3. 观察状态矩阵可拆成不随开关变化的对角部分与随开关变化的交叉耦合部分。若前者用隐式梯形积分形成固定 companion stamp，后者不直接进入全局矩阵，恒定导纳就有了代数入口。[pdf:E03]（PDF 物理页 3，Eq. (5)–(7)）
4. 传统解耦之所以有时延，是因为一侧在当前步只能拿到另一侧的历史量。若先在同一步内预测一个 \(t+\varphi\Delta t\) 的交叉状态，再把它放进隐式校正式，V-subsystem 与 I-subsystem 就能并行求当前步，而不必真的延后一拍。[pdf:E03]（PDF 物理页 3，Eq. (8)–(14)）
5. 最后把这一代数结构还原成端口 companion circuit：固定导纳留在网络里，开关影响进入历史源；外部网络解出状态后，再回算桥臂内部量。这样，计算结构与原物理电路之间仍有明确映射，而不是只得到不可解释的端口拟合。

## § 4 — 核心 Intuition

把“不会随开关变的储能元件自项”和“会随开关变的电压—电流交叉耦合”分开处理：前者隐式积分并永久盖进节点矩阵，后者用 \(\varphi\)-step 预测后写进历史源。这样，开关仍改变瞬时注入，却不再改变全局导纳 stamp。预测量只承担同一步内的解耦，随后参与校正，因此 V/I 两个子系统可以并行而无需使用上一时刻接口量。[pdf:E03]（PDF 物理页 3，Section II-B/C）

## § 5 — 具体方法与完整 Pipeline

以论文的双 H-bridge、高频隔离 transformer BDC 为例，输入是本步两侧 DC port current、AC/transformer port voltage、开关状态和上一步的电容电压/变压器电流，输出是本步端口解、内部状态及下一步历史源。

1. **建立开关级状态模型。** 选择 \(u_C=[u_{C1},u_{C2}]^T\) 与 \(i_T=[i_{T1},i_{T2}]^T\) 为状态；桥臂开关用上、下管状态及其二值电阻关系形成 \(k_i\) 与 \(k_u\)。于是电容电流由 DC 端电流与 transformer 电流决定，漏感电压由 DC-link 电压、桥状态和 transformer 端电压决定。[pdf:E04]（PDF 物理页 4，Eq. (15)–(17)，Fig. 3）
2. **矩阵拆分与预计算。** 将 \(A=A_\alpha+A_\beta\)：论文把对角、恒定部分记为 \(A_\alpha\)，把由开关导通状态决定的非对角、变化部分记为 \(A_\beta\)。仿真开始时预计算并存储 \(M_i,N_{ij},Q_i\) 等恒定矩阵以及 \(A_{\beta,j}\) 的候选元素，避免步内重复构造大矩阵。[pdf:E03]（PDF 物理页 3，Eq. (6)–(9)）[pdf:E07]（PDF 物理页 7，Fig. 12、Section V）
3. **做 \(\varphi\)-step 预测。** 用本步已知状态和输入显式预测 \(x^p(t+\varphi\Delta t)\)。预测值不是最终状态，而是对 V/I 交叉耦合在本步内位置的估计。
4. **形成两个无时延子系统。** 将预测式代回包含梯形积分的校正式，得到 V-subsystem 与 I-subsystem 的当前步方程。两者各自和关联的外部网络同时求节点电压，不等待对方上一时刻的结果。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14)）
5. **使用固定 companion circuit。** 等效电路把 DC capacitor 端和 transformer current 端写成 \(I=GU+I_{\mathrm{his}}\) 的形式；\(G\) 或 \(R\) 只由 \(C,L,\Delta t\) 决定，开关状态进入 \(u_{C\mathrm{his}}\)、\(i_{T\mathrm{his}}\)。论文保留平台已有的高频 transformer 模块，不另行拟合 transformer port equation。[pdf:E04]（PDF 物理页 4，Fig. 3、Eq. (18)–(21)）
6. **更新状态并回算内部量。** 节点解给出本步输入与状态，随后更新等效历史电流源；桥臂开关的电压、电流可由 \(u_{C1}\)、\(i_{T1}\) 与开关状态反算，而不只得到端口量。[pdf:E05]（PDF 物理页 5，Eq. (22)）
7. **合并多模块端口。** 串联端口按等效电导的倒数求和，公共电流下合成端口电压；并联端口直接相加电导和历史电流源。ISOP/ISOS/IPOP/IPOS 都因此可形成低维端口等效，模块内部的 V/I 子系统仍可并行。[pdf:E06]（PDF 物理页 6，Fig. 9–11、Eq. (26)–(27)）

论文使用固定步长；没有报告多速率调度。论文也没有给出 floating-point/fixed-point 位宽、量化误差、Kintex-7 上的具体模块划分、LUT/DSP/BRAM 用量、时序闭合或 host–FPGA 通信延迟，所以不能从“平台包含 FPGA”外推出算法已完成可复用的 FPGA datapath 映射。[pdf:E09]（PDF 物理页 9，Section VI-C、Fig. 18）

## § 6 — 核心数学推导（无形式化数学则跳过）

基础出发点是线性分段状态方程

\[
\dot{x}(t)=Ax(t)+Bu(t), \qquad A=A_\alpha+A_\beta .
\]

\(A_\alpha\) 是可隐式积分的恒定自项，\(A_\beta\) 是开关决定的变化耦合。作者把一步积分写成

\[
x(t+\Delta t)=x(t)+\int_t^{t+\Delta t}\!\left(A_\alpha x(t)+Bu(t)\right)\,dt
+\Delta t\,A_\beta x^p(t+\varphi\Delta t),
\]

即对恒定部分采用隐式形式，对变化耦合用预测状态数值积分。[pdf:E03]（PDF 物理页 3，Eq. (5)–(7)）

预测器为

\[
x^p(t+\varphi\Delta t)=(E+\varphi\Delta t A)x(t)+\varphi\Delta t Bu(t),\quad 0<\varphi<1 .
\]

把系统按 voltage states 与 current states 拆开并将预测器代入校正式后，可写成

\[
\begin{bmatrix}x_V(t+\Delta t)\\x_I(t+\Delta t)\end{bmatrix}
=
\begin{bmatrix}\alpha_1x_V(t)\\\alpha_2x_I(t)\end{bmatrix}
+
\begin{bmatrix}\beta_1u_I(t)\\\beta_2u_V(t)\end{bmatrix}
+
\begin{bmatrix}Q_1u_I(t+\Delta t)\\Q_2u_V(t+\Delta t)\end{bmatrix},
\]

其中 \(\alpha_1=M_1+N_{12}P_1,\alpha_2=M_2+N_{21}P_2\)，\(\beta_1=Q_1+N_{12}R_1,\beta_2=Q_2+N_{21}R_2\)。物理含义是：对方子系统的“未来影响”已压入本地系数，当前步只剩本子系统和其外部网络的未知量，因此可以并行求解。[pdf:E03]（PDF 物理页 3，Eq. (10)–(14)）

对 BDC，状态方程写成

\[
\begin{bmatrix}\dot u_C\\\dot i_T\end{bmatrix}
=
\begin{bmatrix}0&k_i\\k_u&0\end{bmatrix}
\begin{bmatrix}u_C\\i_T\end{bmatrix}
+
\begin{bmatrix}C^{-1}&0\\0&L^{-1}\end{bmatrix}
\begin{bmatrix}i_d\\u_s\end{bmatrix}.
\]

对角块为零，开关信息集中在 \(k_i,k_u\) 的交叉块，这正是“恒定自项、变化互项”拆分能成立的电路结构原因。[pdf:E04]（PDF 物理页 4，Eq. (17)）

离散后端口 companion equation 是

\[
\begin{bmatrix}u_C(t+\Delta t)\\i_T(t+\Delta t)\end{bmatrix}
=
\begin{bmatrix}u_{C\mathrm{his}}(t)\\i_{T\mathrm{his}}(t)\end{bmatrix}
+
\begin{bmatrix}R_C\,i_d(t+\Delta t)\\G_T\,u_s(t+\Delta t)\end{bmatrix},
\]

且

\[
\begin{bmatrix}R_C\\G_T\end{bmatrix}
=\frac{\Delta t}{2}
\begin{bmatrix}C^{-1}&0\\0&L^{-1}\end{bmatrix},\qquad
\begin{bmatrix}G_C\\R_T\end{bmatrix}
=\frac{2}{\Delta t}
\begin{bmatrix}C&0\\0&L\end{bmatrix}.
\]

因此 \(G_C=2C/\Delta t\)、\(R_T=2L/\Delta t\) 在开关过程中固定；\(u_{C\mathrm{his}},i_{T\mathrm{his}}\) 吸收旧状态、\(\varphi\)-step 校正、开关矩阵和端口输入。这就是“恒定导纳”在电路层的精确定义。[pdf:E04]（PDF 物理页 4，Eq. (18)–(21)）

稳定性分析把一阶测试方程的特征根记为 \(\lambda\)、步长记为 \(h\)，得到放大因子条件

\[
\left|\frac{x_{n+1}}{x_n}\right|
=
\left|
\frac{1+\lambda h/2+\lambda h(1+\varphi\lambda h)}
{1-\lambda h/2}
\right|<1.
\]

作者据此绘出不同 \(\varphi\) 的稳定域，推荐 \(\varphi=0.125\)，并称其稳定域相对直接 modified Euler 扩大 64 倍；对文中 converter 特征根集合，作者报告可允许的最大仿真步长达 \(400\,\mu s\)。这是线性化/测试方程层面的数值结论，不等同于任意开关序列下的全局 hybrid-system 稳定性证明。[pdf:E05]（PDF 物理页 5，Eq. (23)–(25)、Fig. 4–7）

## § 7 — 实验设计与结论

**问题 1：无接口时延是否真的提高 EMT 精度？** 作者搭建五个高频隔离 BDC submodule 连接 MVDC 与 LVDC 的测试系统，以 PSCAD/EMTDC v46 detailed model（DM）为 benchmark，同时比较 traditional time-delay model（TTM）与 proposed model（PM）。参数包括 10 kV DC、10 kHz、五模块、DC-side capacitor 100/20 \(\mu F\)、30 \(\mu H\) AC-side inductor、20 \(\Omega\) load impedance、10 MVA transformer、1:1 ratio 和 0.1 p.u. leakage reactance；工况是在 0.3 s 施加 0.05 s 的 LVDC 负载短路，并在 0.6 s 将 MVDC 从 10 kV 升至 15 kV。[pdf:E07]（PDF 物理页 7，Table I、Section VI-A）答案是：在 0.25–0.8 s 区间，load voltage 的 MRE 从 TTM 的 8.06% 降到 PM 的 0.26%；transformer primary/secondary voltage 从 2.7%/5.86% 降到 0.10%/0.09%；primary current 从 13.6% 降到 0.12%。这些数字支持“同一测试系统中 PM 更接近 DM”，但不是对真实硬件误差的测量。[pdf:E08]（PDF 物理页 8，Fig. 14–16 及相邻 error analysis）

**问题 2：稳定域是否比显式预测或时延解耦更好？** 作者先比较 forward Euler、modified Euler 与所提算法的放大因子稳定域，再对一个桥臂在不同步长下做 discrete characteristic-root analysis。论文报告 \(\varphi=0.125\) 给出最大的连续稳定域；TTM 随步长增加出现成对复根和更强振荡，而 PM 的示例根保持在实轴，并据此判断步长增加不会触发观察到的那类振荡。[pdf:E05]（PDF 物理页 5，Fig. 4–7）[pdf:E06]（PDF 物理页 6，Fig. 8）答案支持“该线性化示例中的数值稳定性改善”，但没有覆盖所有开关组合、控制器状态、非线性器件和异步事件。

**问题 3：模块数增加时是否更快？** 作者分别构造 1、5、10、20、30、50、80、100 个 submodule，输入 10 kV、load 20 \(\Omega\)、10 kHz、步长 1 \(\mu s\)、仿真时长 0.5 s，在 i5-12600K 3.70 GHz/16 GB RAM 上比较 DM、TTM、PM。Fig. 17 显示 DM 用时显著更长；TTM 与 PM 用时接近，PM 略多；相对 DM 的 speedup 随模块数增长。论文未给出这些柱/线对应的完整数表，因此本卡不从曲线估读精确 speedup。[pdf:E08]（PDF 物理页 8，Section VI-B）[pdf:E09]（PDF 物理页 9，Fig. 17 及相邻结论）

**问题 4：模型能否在实时平台覆盖控制、故障与双向功率流？** 作者在含 AMD Ryzen processing cores 与 AMD-Xilinx Kintex-7 410T FPGA 的 RT-LAB 平台上以 1 \(\mu s\) 步长运行 PM，并用 B-Box 3.0 RCP 实现 single-phase-shift control。HIL 参数是输入 1000 V、DC capacitor 100 \(\mu F\)、10 kHz、load 10 \(\Omega\)、两侧 leakage inductor 各 5 \(\mu H\)、auxiliary inductor 30 \(\mu H\)、magnetization inductor 1 H。[pdf:E09]（PDF 物理页 9，Section VI-C、Fig. 18–19）实验包括负载电压参考从 800 V 改到 600 V/400 V、负载短路，以及输入从 1 kV 降到 600 V 触发正反向功率流；作者观察到 HIL 波形与 offline simulation 一致。[pdf:E10]（PDF 物理页 10，Fig. 20–22、Section VI-C）[pdf:E11]（PDF 物理页 11，Fig. 23、Conclusion）这里的 HIL 是 controller 与实时 simulator 的闭环结果，不是实体功率级测量；论文也没有报告 deadline miss、最坏步耗时、FPGA 资源或 fixed-point 误差，所以“可实时运行”得到支持，“硬件映射效率已充分量化”则没有。

## § 8 — Take-aways

**5 句话：**  
1. 论文通过把固定储能自项与开关相关交叉项分开，令 BDC 的外部 companion admittance 在开关过程中保持不变。  
2. \(\varphi\)-step predictor 估计同一步内的交叉耦合，再由隐式校正式得到最终状态，从而使 V/I 子系统并行而不使用上一拍接口量。  
3. 五模块故障与电压阶跃算例中，PM 相对 detailed model 的 MRE 明显低于 traditional time-delay model。  
4. 模块规模越大，固定 stamp、低维端口合并与并行子系统带来的相对加速越明显。  
5. RT-LAB 的 1 \(\mu s\) HIL 结果说明该模型能覆盖参考变化、短路和双向功率流，但论文没有交付可核验的 FPGA 资源/时序数据。

**3 句话：**  
1. 核心创新是把“开关变化”从全局导纳矩阵移入同一步预测校正的历史源。  
2. 这样既保留开关级 EMT 内部状态，又避免传统解耦的接口时延，并让多模块端口可以低维合并。  
3. 证据在作者选定的 10 kHz、1 \(\mu s\) 与对齐开关事件工况下很强，但对异步事件、器件非线性和真实硬件误差仍缺覆盖。

**1 句话：** 这是一种用同一步预测换取固定网络 stamp 与无时延并行求解的 BDC EMT 模型，其优势成立的关键是预测必须在每次开关事件附近仍足够准确。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**一个固定步内的开关模式及其交叉耦合可以由 \(x^p(t+\varphi\Delta t)\) 准确代表，因而把 \(A_\beta\) 移出隐式全局矩阵不会漏掉决定性事件。** 如果 PWM edge、dead time、二极管换流或保护动作落在步内，\(A_\beta\) 实际上可能在 \(t\) 与 \(t+\Delta t\) 之间跳变；此时预测器使用的可能是错误拓扑，历史源即使不引入“上一拍接口时延”，仍会引入事件定位误差。该假设一旦失效，论文的三项核心收益会同时受损：端口误差增加，所谓稳定域不再描述真实 hybrid dynamics，固定导纳模型也可能必须缩步或额外迭代才能可信。

论文给出的有利证据是：在 10 kHz、1 \(\mu s\) 步长、负载短路、电压阶跃和正反向功率流下，PM 与 DM/offline 波形高度一致；线性测试方程和单桥臂特征根也显示更大的稳定域。[pdf:E05]（PDF 物理页 5，Section III）[pdf:E08]（PDF 物理页 8，Fig. 14–16）缺失的证据是：开关 edge 相对仿真网格的相位扫描、dead time/diode commutation、参数突变或磁饱和下的误差上界，以及跨步拓扑变化时的 hybrid stability 证明。HIL 与 offline simulation 的一致性无法排除“两者共享相同事件对齐或器件简化”这一替代解释。

## § 10 — 最小复现实验

一周内最有信息量的复现不是重建五模块 RT-LAB，而是做一个 **single-module event-phase sweep**：

1. 按论文 HIL 参数实现一个双 H-bridge BDC：1000 V 输入、\(C=100\,\mu F\)、10 kHz、10 \(\Omega\) load、两侧 leakage \(5\,\mu H\)、auxiliary \(30\,\mu H\)、magnetization \(1\,H\)，使用 single-phase-shift control。[pdf:E09]（PDF 物理页 9，Section VI-C）
2. 实现三个 solver：事件精确定位且步长足够小的 detailed reference、上一拍接口量的 TTM、\(\varphi=0.125\) 的 PM。三者使用相同开关序列和器件参数。
3. 先在 \(\Delta t=1\,\mu s\) 复现稳态、800→600 V 参考变化和负载短路；测量 \(u_C,i_T\)、端口功率、开关边沿附近峰值误差、整段 MRE，以及每步 wall-clock time。
4. 再把所有 PWM edge 相对步网格的 offset 从 0 扫到一个完整 \(\Delta t\)，并扫 \(\Delta t=0.5,1,5,10,20\,\mu s\)。这是对最脆弱假设的直接检验，而不是只重画论文波形。

作为预先写明的复现判据：在对齐的 1 \(\mu s\) 工况，若 PM 的主要状态 MRE 低于 0.5%、且至少比同设置的 TTM 低一个数量级，同时没有新增的数值振荡，则支持论文核心 accuracy claim；若边沿 offset 改变后该优势消失、PM 在 reference 稳定时出现振荡，或为保持误差必须退回与 detailed model 相同的事件处理成本，则反驳“无时延固定导纳足以普遍保持精度”的更强解释。0.5% 和“一数量级”是本复现实验的判据，不是论文新增报告数字。

## § 11 — 最强反例设计

最强反例是构造一个**步内拓扑必然变化但平均功率仍与论文工况相同**的 adversarial switching test。保持 10 kHz、相同电压与负载，把两桥 PWM edge 随机放到 10–20 \(\mu s\) macro-step 内不同位置，加入真实 dead time，并令二极管在 transformer current 过零附近自然换流；随后叠加一次使 magnetization inductance 进入明显非线性区的 DC bias。用事件分辨的 reference 作为真值，对比固定 \(\varphi=0.125\) PM、TTM 与允许一次事件回退/迭代的版本。

这个反例的攻击点不是“极端参数会更难”，而是给出一个具体替代解释：论文观察到的高精度可能主要来自 \(1\,\mu s\) 步长相对 100 \(\mu s\) switching period 足够小、且门极事件与仿真网格规则对齐，而不是 \(\varphi\)-step 在一般开关事件下消除了耦合误差。若 PM 的节点解仍数值稳定，却在 edge 附近累积能量偏差、产生错误反向功率或漏掉峰值电流，那么 Eq. (25) 的大稳定域只能说明“不发散”，不能说明 EMT 波形正确。若 PM 在随机 edge、dead time 和非线性磁化下仍保持显著低于 TTM 的误差，并满足实时 deadline，这个反例才算被击败。

## § 12 — Follow-up Research Idea

本领域高影响工作的评价重点通常是：清楚的物理/数值机制、可证明或可解释的稳定性与误差边界、严格的 EMT 对照、真实实时 deadline，以及在代表性功率硬件或 HIL 系统上的工程可实现性。基于第 9 节，候选方向是 **event-aware constant-stamp hybrid EMT**：问题不再定义为“固定步长下选一个更好的 \(\varphi\)”，而是“在任意步内开关事件、dead time 与自然换流存在时，如何仍保持全局网络 stamp 恒定，同时对事件前后状态跳变给出可验证的误差界”。

**（a）需求。** 未来 PET/BDC 阵列的控制器、保护与通信事件不会都与 EMT 网格对齐；若每次异步事件都强制全网缩步，恒定导纳带来的规模优势会被最坏事件吞掉。

**（b）研究价值。** 若能把精确事件时刻局部化为端口 history-source jump，而全局导纳与多数模块步长不变，就可能同时得到可组合的大规模实时性和开关边沿可信度；这比简单调 \(\varphi\) 或再加一个 predictor 改变了研究目标。

**（c）可借鉴工具。** 可借鉴 hybrid systems 的 saltation matrix（描述离散事件使连续状态敏感度发生的跳变）、asynchronous discrete-event integration，以及局部 Schur-complement/low-rank source update。它们应只修正发生事件的模块端口源，不重构全网矩阵。

**（d）首个证伪实验。** 用第 11 节的随机 edge/dead-time 测试，在 10–20 \(\mu s\) macro-step 下与亚微秒事件分辨 reference 比较。若方法不能同时做到：误差不随 edge offset 系统性恶化、无全网矩阵重构、且每步最坏执行时间满足 deadline，那么核心想法即被证伪。

**（e）实质区别。** 本文用固定 \(\varphi\) 的连续预测值近似步内变化；候选方法把 switching event 当作有精确时刻的离散状态转换，并要求给出跨事件的误差/稳定性契约。由于本任务没有联网或跨论文检索，这只是由本文证据约束的候选研究方向，不声称 novelty，也不声称相邻领域尚无同类方法。
