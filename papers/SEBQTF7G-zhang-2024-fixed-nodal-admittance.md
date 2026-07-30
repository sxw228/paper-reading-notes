# General Linearized Model of Voltage Source Converter With Fixed Nodal Admittance Matrix

作者：Fei Zhang、Wei Gu、Yuanshi Zhang、Liwei Wang、Wei Li  
出处：IEEE Transactions on Power Electronics，Vol. 39，No. 10，pp. 12143–12148  
年份：2024  
DOI：10.1109/TPEL.2024.3409537  
Zotero key：SEBQTF7G  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的是一个实时 electromagnetic transient（EMT）仿真中的结构性矛盾：VSC 的开关状态不断变化，详细开关模型因此会改变网络的 nodal admittance matrix（NAM，节点导纳矩阵）；每次开关事件后重新组装、分解或求逆 NAM，会在 VSC 数量增加时迅速吞噬实时步长预算。作者把目标定为：保留开关级动态和 pulse-blocked 行为，同时让送入全局网络求解器的 NAM 固定，并避免为了电路解耦而引入一个仿真步的延迟。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这项工作的工程价值不只在“算得更快”。固定 NAM 让全局网络矩阵可以预先处理，开关非线性不再触发全局矩阵结构变化；若同一模型还能在 pulse-enabled 与 pulse-blocked 两类工况下工作，就可减少模型切换和额外二极管支路。论文直接声称其 companion circuit（伴随电路）把 AC、DC 端口解耦，不引入虚拟 L/C，也不在局部模型与全局网络解之间插入一步延迟。[pdf:E02]（PDF 物理页 2，Fig. 2 与贡献列表）这里的“解耦”是计算接口上的解耦，不是说 VSC 的 AC/DC 物理能量交换消失；耦合仍通过 history source 在相邻时间步之间传递。

## § 2 — 前人工作与不足

论文把既有路线分成三类。第一类是 PSCAD/EMTDC 一类详细开关模型：用 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 两值电阻表示开关通断，物理意义直观，但任何开关状态改变都可能导致 NAM 重新生成，矩阵计算成为实时仿真的瓶颈。[pdf:E01]（PDF 物理页 1，Section I）

第二类是 Hui–Christopoulos、Pejovic–Maksimovic 一脉的 associated discrete circuit（ADC）模型：ON 用电感、OFF 用电容，只要恰当选择 L/C，使两者离散后的等效电阻相同，NAM 就可固定。代价是这些元件是为数值建模引入的“虚拟”储能元件；论文指出，为压低虚拟功率损耗、振荡和模型误差，尤其在高开关频率场景中，离散步长通常必须进入 sub-microsecond 范围。[pdf:E01]（PDF 物理页 1，Fig. 1 与 Section I；相关文献条目见 [pdf:E06]，PDF 物理页 6，Refs. [4]–[6]）

第三类是 switching function 模型。显式积分可以用上一步电流计算电容电压，从而解耦等效电路，但这相当于引入时序滞后；若改用 backward Euler 或 trapezoidal 等隐式积分，switching function 又会进入当前步导纳关系，使 NAM 随开关变化。现有 pulse-blocked 仿真还可能要求添加额外二极管或修改等效电路。[pdf:E01]（PDF 物理页 1，Section I；相关文献条目见 [pdf:E06]，PDF 物理页 6，Refs. [7]–[11]）

因此，作者面对的不是“有没有固定 NAM 模型”，而是现有固定 NAM 方法分别以虚拟元件、小步长、一步延迟或 blocked-mode 特殊结构为代价。论文的实质目标是同时取消这些代价。

## § 3 — 重建作者的思考路径

可以从已有 EMT companion-circuit 思想逆向重建这条路径。网络求解器真正需要的不是 VSC 内部每只开关的完整拓扑，而是端口在当前步满足的“导纳项 + history source”关系。若能把所有随开关状态改变的量移入 history source，把当前步连接全局网络的导纳项保持常数，那么非线性仍被计算，但不会传播为全局 NAM 的结构变化。这是基于论文背景与推导的合理重建，不是作者逐字描述的研究过程。[pdf:E01]（PDF 物理页 1，Section I）[pdf:E03]（PDF 物理页 3，Eqs. (13)–(18)）

接下来需要一个离散方法满足两点：一方面达到接近 trapezoidal 的局部截断误差，另一方面不能形成需要迭代求解的当前步 switching-dependent 隐式项。modified Euler 先用当前步斜率预测 \(k+1\) 状态，再用预测状态修正，因此可以把 \(k+1\) 输入前的系数整理成只由物理 L/C 和步长决定的对角矩阵，而把 switching-dependent 的 \(A\) 矩阵留在 history 更新中。[pdf:E02]（PDF 物理页 2，Eqs. (9)–(11)）[pdf:E03]（PDF 物理页 3，Eqs. (12)–(14)）

最后还剩两个工程缺口。pulse-blocked 时不能继续把 IGBT gate 当作导通状态，故作者用反并联二极管的电流、电压和前一状态更新 switching state；粗步长内的开关时刻也不能只量化到步边界，故作者用参考波与载波的交点估计步内 \(T_{\mathrm{on}}\)，以 duty ratio 进入模型。[pdf:E03]（PDF 物理页 3，Sections II-D、II-E 与 Fig. 3）这两步把“固定端口导纳”扩展到正常 PWM、阻断和步内开关事件。

## § 4 — 核心 Intuition

核心 intuition 是：不要让开关非线性改变当前步的端口导纳，而要让它只改变 companion source 的历史值。modified Euler 恰好能把 VSC 离散关系整理成“固定、对角的端口系数 \(G\) + switching-dependent history source”，所以全局 NAM 固定，AC/DC 端口也可在当前步分别接入网络求解。[pdf:E03]（PDF 物理页 3，Eqs. (13)–(18)）步内开关时刻则通过 duty ratio 注入 history 更新，以减轻粗步长造成的事件量化误差。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Eq. (21)）

## § 5 — 具体方法与完整 Pipeline

以论文验证的 two-level VSC 为例，一次仿真步的输入、处理和输出如下。

1. **建立端口状态。** AC 侧每相满足
   \[
   v_{sj}(t)=v_{\mathrm{con}j}(t)+L\frac{\mathrm d i_{sj}(t)}{\mathrm dt},
   \]
   而换流器相电压由上下桥臂开关状态与上下 DC 电容电压给出：
   \[
   v_{\mathrm{con}j}(t)=SW_{\mathrm{up}j}(t)v_{\mathrm{cap\_p}}(t)-SW_{\mathrm{low}j}(t)v_{\mathrm{cap\_n}}(t).
   \]
   DC 电容电流由三相电流、开关状态和 DC 端口电流共同决定。作者选择上下 DC 电容电压和三相 AC 电感电流作为五个状态量。[pdf:E02]（PDF 物理页 2，Fig. 2 与 Eqs. (1)–(6)）

2. **形成 switching-dependent 的局部状态方程。** 写成 \(\dot x=A(SW)x+Bu\)，其中 \(x=[v_{\mathrm{cap\_p}},v_{\mathrm{cap\_n}},i_{sa},i_{sb},i_{sc}]^\mathsf T\)，\(u=[i_{\mathrm{dc\_p}},i_{\mathrm{dc\_n}},v_{sa},v_{sb},v_{sc}]^\mathsf T\)。\(A\) 含开关状态以及 \(1/L,1/C\)，而 \(B=\mathrm{diag}(1/C,1/C,1/L,1/L,1/L)\) 与开关状态无关。[pdf:E02]（PDF 物理页 2，Eqs. (6)–(8)）

3. **用 modified Euler 时间推进。** 先由 \(x(k),u(k)\) 预测 \(\tilde x(k+1)\)，再用当前与预测斜率修正 \(x(k+1)\)。整理后，当前步网络输入 \(u(k+1)\) 前的系数是 \((T_s/2)B\)，其余项只需用已知的 \(x(k),u(k)\) 和当步 switching state 计算，不需要全局迭代。[pdf:E02]（PDF 物理页 2，Eqs. (9)–(12)）

4. **拆成固定端口导纳与 history source。** 定义 \(G=(T_s/2)B\)，把其余项记为 \(x_{\mathrm{his}}(k)\)，得到
   \[
   \begin{bmatrix}x_V(k+1)\\x_I(k+1)\end{bmatrix}
   =
   G\begin{bmatrix}u_I(k+1)\\u_V(k+1)\end{bmatrix}
   +
   \begin{bmatrix}x_{V,\mathrm{his}}(k)\\x_{I,\mathrm{his}}(k)\end{bmatrix}.
   \]
   因 \(G\) 是对角常数，DC 电容电压只显式依赖当前步 DC 电流，AC 电感电流只显式依赖当前步 AC 电压；二者的跨端耦合和开关非线性进入 history source。[pdf:E03]（PDF 物理页 3，Eqs. (13)–(16)）

5. **把端口关系接入全局网络。** companion circuit 的等效参数为
   \[
   R_{L,\mathrm{equ}}=\frac{2L}{T_s},\qquad
   R_{C,\mathrm{equ}}=\frac{T_s}{2C}.
   \]
   只要 \(L,C,T_s\) 不变，这些端口参数不随开关状态改变，故全局 NAM 可固定；每步只更新 companion source。[pdf:E03]（PDF 物理页 3，Eqs. (17)、(18)）

6. **处理 pulse-blocked。** gate 全置零后，以反并联二极管状态代替 IGBT switching state：前一步已导通且二极管电流为正，或前一步关断且二极管两端正向电压为正时，当前步置为导通；上下二极管都关断时，相支路高阻，作者用
   \[
   i_{j,\mathrm{his}}=-\frac{v_j(k)}{R_{L,\mathrm{equ}}}
   \]
   令相电流在 companion relation 中为零。[pdf:E03]（PDF 物理页 3，Eqs. (19)、(20)）

7. **处理步内 switching event。** 由 \(k-1,k\) 时刻的 \(v_{\mathrm{ref}}\)、\(v_{\mathrm{car}}\) 及其斜率外推交点，得到一个步内的总导通时间；单次或多次开关都压缩为
   \[
   d=\frac{T_{\mathrm{on}}}{T_s},\qquad
   v_{\mathrm{con}j}=d_{\mathrm{up}j}v_{\mathrm{dc\_p}}-d_{\mathrm{low}j}v_{\mathrm{dc\_n}}.
   \]
   多次开关时 \(T_{\mathrm{on}}\) 是各导通区间之和。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Eq. (21)）[pdf:E04]（PDF 物理页 4，Eq. (22)）

论文未报告多速率调度、CPU/FPGA 任务划分、FPGA 流水线或并行映射、定点/浮点格式、字长、时钟频率、LUT/DSP/BRAM 资源、综合时序、单步最坏执行时间或实时 deadline margin。文中只报告模型运行于含 AMD Ryzen 3.8 GHz CPU 和 Xilinx Kintex-7 FPGA 的 OP4610XG；因此不能从本文判断核心方程究竟执行在 CPU、FPGA，还是两者协同。[pdf:E04]（PDF 物理页 4，Section III）

## § 6 — 核心数学推导（无形式化数学则跳过）

modified Euler 是全文的关键。论文从
\[
\tilde x(k+1)=x(k)+T_s\big(Ax(k)+Bu(k)\big)
\]
开始，把预测值代入修正式
\[
x(k+1)=x(k)+\frac{T_s}{2}\big(Ax(k)+Bu(k)\big)
+\frac{T_s}{2}\big(A\tilde x(k+1)+Bu(k+1)\big),
\]
得到
\[
x(k+1)=Mx(k)+Nu(k)+\frac{T_s}{2}Bu(k+1),
\]
其中
\[
M=I+T_sA\left(I+\frac{T_s}{2}A\right),\qquad
N=\frac{T_s}{2}(I+T_sA)B.
\]
[pdf:E02]（PDF 物理页 2，Eqs. (9)–(11)）

工程上最重要的不是 \(M,N\) 的外观，而是它们所处的时间位置。\(A\) 含 switching state，因此 \(M,N\) 也随开关变化；但它们只乘已知的 \(x(k),u(k)\)，可以在局部形成 history source。唯一乘未知当前步网络量 \(u(k+1)\) 的是 \(G=(T_s/2)B\)，而 \(B\) 是由物理 \(L,C\) 决定的对角常数。于是 switching-dependent 非线性被限制在右端 history source，送入全局网络左端的 NAM 不变。[pdf:E02]（PDF 物理页 2，Eqs. (6)–(12)）[pdf:E03]（PDF 物理页 3，Eqs. (13)–(18)）

对数学基础较弱的读者，可以把这看成“把难变的部分和快变的部分换了位置”：传统详细模型让开关改变方程左边的矩阵，必须重做全局求解；这里让开关只改变方程右边的等效源，左边矩阵可以复用。作者还直接指出 modified Euler 具有与 trapezoidal method 相同的 local truncation error，同时不需要迭代过程。[pdf:E03]（PDF 物理页 3，Section II-B）论文没有给出稳定域、全局误差界、passivity 或刚性系统下的收敛证明；因此“同局部截断误差”不能自动外推为任意拓扑和任意粗步长下与详细模型等精度。

## § 7 — 实验设计与结论

**问题 1：固定 NAM 模型能否同时覆盖充电、正常 PWM 和 pulse-blocked，并优于 switching function 基线？**  
实验采用 two-level VSC，参数为 \(T_s=20~\mu s\)、额定功率 300 kW、DC 电压 3 kV、AC 线电压 rms 1.5 kV、AC 电感 15 mH、DC 电容 3.3 mF、载波频率 5 kHz；详细 IGBT/diode 模型作 reference，另设带 blocked-mode 二极管的 switching function 模型。开环 gate 对所有模型完全相同：0–0.5 s 为二极管充电，0.5–1 s 开启 PWM，1 s 阻断。[pdf:E04]（PDF 物理页 4，Table I、Fig. 5 与 Section III）答案是：Fig. 5 中 proposed model 在 AC 电流、DC 电压和 DC 电流上比 switching function model 更贴近 detail model，且一个模型跨越了 enabled/blocked 两种状态。论文没有为 Fig. 5 各瞬态分别报告数值误差或置信区间，故这里仅能采用作者的相对比较结论，不能从曲线估读更精确数字。[pdf:E04]（PDF 物理页 4，Fig. 5）

**问题 2：步内插值能否使较粗步长仍接近细步长 reference？**  
作者比较 proposed model with interpolation 在 \(50~\mu s\) 下的结果，与 detail model 在 \(1~\mu s\) 和 \(50~\mu s\) 下的结果；工况仍覆盖充电、PWM 与 1 s 阻断。答案是 proposed \(50~\mu s\) 接近 detail \(1~\mu s\)，而 detail \(50~\mu s\) 出现较大误差。[pdf:E04]（PDF 物理页 4，Section III 的 Fig. 6 引导文字）[pdf:E05]（PDF 物理页 5，Fig. 6）作者总结 proposed model 与 detail model 的稳态 relative two-norm error 小于 0.6%。[pdf:E04]（PDF 物理页 4，Section III）论文未给出该指标的完整公式、统计窗口、各信号分别的误差或最坏瞬态误差，所以 0.6% 不能理解成全时域、全变量的统一上界。

**问题 3：模型放进闭环 HIL 后是否仍跟得上 detailed reference？**  
模型运行于 OP4610XG real-time simulator（AMD Ryzen 3.8 GHz CPU、Xilinx Kintex-7 FPGA），controller 为 imperix B-Box 3.0，通过 I/O 连接；闭环采用 classic PQ control，controller 接收 AC 电压、电流和 DC 电压并输出 gate。在 5 s 时有功指令从 \(-1\) 跳至 \(-0.5\) p.u.。[pdf:E04]（PDF 物理页 4，Fig. 4 与 Section III）Fig. 7 显示 proposed 与 detail model 的 AC 电流、DC 电压、DC 电流和有功响应基本重合；作者把轻微差异归因于 controller–simulator communication delay。[pdf:E04]（PDF 物理页 4，Section III）[pdf:E05]（PDF 物理页 5，Fig. 7）但论文未报告 HIL I/O 延迟数值、jitter、丢帧、闭环实时步长的独立说明或 deadline miss 统计。

**问题 4：VSC 数量增加时是否有计算收益？**  
作者以 detail model 的执行时间为基准，比较 5、10、20、30、40 个 VSC 的 simulation acceleration。40 个 VSC 时，proposed model 约比 switching function model 快 8 倍、比 detail model 快 100 倍；Fig. 8 还显示收益随 VSC 数量上升。[pdf:E04]（PDF 物理页 4，Section III）[pdf:E05]（PDF 物理页 5，Fig. 8）Table II 只做定性比较：L/C ADC 固定 NAM 且可做 blocked mode，但未消除 virtual loss；switching function 带一步 delay 且 blocked mode 需额外二极管；proposed method 三项均满足，并被赋予最高效率等级。[pdf:E05]（PDF 物理页 5，Table II）论文未报告绝对执行时间、每步负载分布、矩阵规模、线程数、FPGA 资源或功耗，因此不能把“100 倍”外推到其他硬件、网络结构或实现。

验证边界也很明确：正文展示的是一个 two-level VSC 测试系统及其多实例扩展，而不是 multilevel converter、不同开关器件、弱网、多端 DC 网或大规模真实电网。论文虽声称矩阵维数对不同拓扑保持固定并在 multilevel converter 中尤其可显著缩减，但没有给出 multilevel 实验。[pdf:E03]（PDF 物理页 3，Section II-C）FPGA 的板卡型号被报告，但 FPGA mapping、资源和时序未报告；因此这是一篇 real-time/HIL 模型论文，不是一篇可据此复现 FPGA 实现细节的论文。

## § 8 — Take-aways

**5 句话：**  
1. 论文把 VSC 开关非线性从全局 NAM 移到局部 history source，使当前步端口导纳保持固定。[pdf:E03]（PDF 物理页 3，Eqs. (13)–(18)）  
2. modified Euler 让 AC 电感电流和 DC 电容电压通过对角 \(G\) 接入当前步全局解，同时避免 switching function 模型常见的一步解耦延迟。[pdf:E02]（PDF 物理页 2，Eqs. (9)–(12)）  
3. pulse-blocked 通过二极管状态更新，步内 switching event 通过 duty interpolation 处理，无需更换等效电路。[pdf:E03]（PDF 物理页 3，Eqs. (19)–(21)）  
4. two-level VSC 实验显示 \(50~\mu s\) 插值模型接近 \(1~\mu s\) detail reference，稳态 relative two-norm error 小于 0.6%，40 个 VSC 时报告约 100 倍于 detail model、8 倍于 switching function model 的速度。[pdf:E04]（PDF 物理页 4，Section III）[pdf:E05]（PDF 物理页 5，Figs. 6、8）  
5. “general” 的证据仍有限：multilevel 拓扑、非理想开关、FPGA 实现细节、绝对实时预算和多工况误差界均未报告。

**3 句话：**  
1. 真正的贡献是把 switching-dependent 项限制在 history source，而不是发明另一种固定电阻近似。  
2. 这让固定 NAM、无虚拟 L/C、无一步延迟、enabled/blocked 共用模型可以同时成立，并得到 real-time 与 HIL 的初步支持。[pdf:E05]（PDF 物理页 5，Table II 与 Conclusion）  
3. 最需要后续验证的是：同一端口分解在更复杂拓扑和步内事件次序不可忽略时是否仍准确。

**1 句话：**  
这篇论文用 modified Euler 把 VSC 的“会变开关”封装进 history source，让全局网络看到“不会变的端口导纳”，但其广泛拓扑适用性仍主要是方法主张而非充分实验结论。

## § 9 — 最脆弱的假设

最脆弱的假设是：**对目标 VSC 及所用步长，所有会显著影响当前步端口行为的 switching-dependent 动态，都可以安全地压入 history source 或一个步内总 duty，而不必改变当前步的固定对角端口系数 \(G\)。**

这个假设一旦失效，核心贡献会同时受损：若内部浮动电容、箝位支路、dead time、非理想导通、commutation overlap 或多个步内事件的先后次序必须出现在当前步端口 Jacobian 中，那么要么 NAM 不再固定，要么固定 NAM 仍在但误差和数值不稳定性上升。论文给出的支持是 two-level VSC 在 20 与 \(50~\mu s\) 工况中的开环比较，以及 PQ 闭环 HIL；其中 \(50~\mu s\) interpolation 结果接近 \(1~\mu s\) detail reference。[pdf:E04]（PDF 物理页 4，Section III）[pdf:E05]（PDF 物理页 5，Figs. 6、7）

缺失证据是决定性的：没有 multilevel 或 floating-capacitor 拓扑，没有对同一 duty 但不同事件顺序的检验，没有稳定性/passivity 证明，也没有参数扫描说明粗步长、载波比、blocked transition 和 diode 零交越的安全范围。因此，“对不同 VSC 拓扑 general”目前应读作方法结构的主张，而不是经广泛反例检验后的结论。[pdf:E03]（PDF 物理页 3，Section II-C）

## § 10 — 最小复现实验

一周内最值得复现的是“固定 NAM + \(50~\mu s\) 插值仍接近 \(1~\mu s\) detail reference”，不必复刻完整 HIL。

1. 在同一 EMT 软件中搭建论文的 two-level VSC：300 kW、3 kV DC、1.5 kV AC line rms、15 mH、3.3 mF、5 kHz；使用完全相同的 open-loop gate 序列。[pdf:E04]（PDF 物理页 4，Table I）
2. 建三个模型：\(1~\mu s\) detail IGBT/diode reference、\(50~\mu s\) proposed fixed-NAM with interpolation、\(50~\mu s\) detail control；只实现 Eqs. (9)–(22) 所需的状态更新、blocked diode logic 和 gate interpolation。[pdf:E02]（PDF 物理页 2，Eqs. (9)–(12)）[pdf:E03]（PDF 物理页 3，Eqs. (13)–(21)）[pdf:E04]（PDF 物理页 4，Eq. (22)）
3. 运行 0–0.5 s diode charging、0.5–1 s pulse-enabled、1 s pulse-blocked 的相同序列；逐步记录 AC current、DC voltage/current，并在每个 switching event 后计算并 hash 全局 NAM，验证其字节不变。[pdf:E04]（PDF 物理页 4，Fig. 5 工况）
4. 用与论文一致的 relative two-norm 指标时，必须自行明确窗口；至少分别报告 steady state、enable transition、blocked transition 三个窗口，而不是只给一个全局平均。再以互相关检查 proposed 与 reference 是否存在一个 \(T_s\) 的系统性相位滞后。
5. 支持核心 claim 的最低结果是：全程 NAM 不变、没有一步系统性滞后、steady-state two-norm error 不超过论文报告的 0.6%，且 \(50~\mu s\) proposed 明显优于 \(50~\mu s\) detail control。[pdf:E04]（PDF 物理页 4，Section III）若任一 switching event 改变 NAM，或插值模型在 blocked transition 出现比粗步长 detail 更大的能量/电流偏差，就反驳相应 claim。

这个复现不需要 OP4610XG 或 B-Box，因此不能复现论文的 HIL communication delay 和真实 deadline；它只检验算法机理。若时间允许，再把 5、10、20、30、40 个并联但电气隔离的 VSC 实例加入，报告绝对 step execution time，而不只报告加速比。

## § 11 — 最强反例设计

最强反例不是简单加噪声，而是构造**同一仿真步内总 duty 完全相同、开关事件次序不同**的两条 gate 序列。Eq. (21) 把多次 switching action 压缩为总 \(T_{\mathrm{on}}\)，Eq. (22) 再只使用 \(d_{\mathrm{up}},d_{\mathrm{low}}\) 计算相电压；因此在相同步初状态和相同总 duty 下，proposed interpolation 会给两条序列相同或近似相同的步级输入。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Eq. (21)）[pdf:E04]（PDF 物理页 4，Eq. (22)）

反例应让“先导通后关断”和“先关断后导通”在详细电路中产生不同能量轨迹：使用明显 DC-link ripple、较小电感、相电流零交越，并在该步末立即进入 pulse-blocked；再扩展到有 floating capacitor 或 neutral-point balance 状态的 multilevel VSC。以 \(0.1\) 或 \(1~\mu s\) event-resolved detail model 为参考，比较两种事件次序在步末的电感能量、电容能量、diode state 和端口电流。

若 detail model 显示两序列的步末状态显著不同，而 proposed model 因总 duty 相同给出相同状态，这就不是“调小一点步长即可”的普通精度损失，而是模型输入表示丢失了决定状态的 event ordering。它会直接挑战第 9 节的核心假设，并说明“固定 NAM + 单一 duty history source”不是所有拓扑和所有粗步长下的充分状态描述。论文目前没有做这一检验。

## § 12 — Follow-up Research Idea

在电力电子与实时 EMT 仿真领域，高影响工作通常不仅要给出更快的算法，还要证明数值可信性、复杂拓扑适用性、实时硬件可实现性，以及在故障/阻断/控制闭环中的工程价值。因此，一个非增量的候选方向是：**event-order-aware、energy-consistent 的固定端口导纳 hybrid model**。它不再把一个步内的 switching waveform 仅表示为总 duty，而是把有序 commutation event 和少量能量不变量纳入局部 history state；全局网络仍只看到固定 \(G\)，局部模型则按事件顺序做解析或短子步更新。

（a）未满足的需求是：在 coarse real-time step 下，同时保住固定 NAM 和事件次序对内部储能、二极管换流、neutral-point/floating-capacitor 状态的影响。  
（b）研究价值在于把“经验上接近 detail model”提升为有可检验适用域的模型：给出哪些事件可被 duty 合并、哪些必须保留次序，以及 energy/passivity error 的界。  
（c）可借鉴相邻领域的 hybrid-system event localization、operator splitting、passivity-preserving model reduction 与 conservative integration；这些工具用来设计局部事件更新，不要求全局 NAM 随事件变化。  
（d）第一个证伪实验就是第 11 节的 paired-gate 测试：两条序列具有相同 duty、不同事件次序，跨 two-level 与一个含内部浮动状态的 multilevel 拓扑；若新模型仍不能区分两者，或为了区分而必须改变全局 NAM，它就失败。  
（e）与本文的实质区别是研究目标从“用总 duty 改善固定-NAM 模型的平均精度”改成“定义 fixed-NAM history state 对有序 switching events 的最小充分表示”，并要求能量一致性和明确的适用域。

这是基于本文薄弱环节提出的候选研究方向；本卡只使用了指定 PDF，没有进行外部相关工作检索，因此不声称 novelty。
