# A Voltage-Behind-Reactance Synchronous Machine Model for the EMTP-Type Solution

**作者：** Liwei Wang；Juri Jatskevich  
**出处：** *IEEE Transactions on Power Systems*, Vol. 21, No. 4, pp. 1539-1549  
**年份：** 2006  
**DOI：** 10.1109/TPWRS.2006.883670  
**Zotero key：** WMSCF7WU

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是一般意义上的“同步机怎么建模”，而是一个很具体的数值接口问题：完整同步机模型怎样进入 EMTP 的节点分析，使机器内部电磁状态和外部网络在同一个时间步内非迭代、同时求解，同时又避免 phase-domain（PD）模型在每一步重算大量转子位置相关系数的代价。作者提出的 voltage-behind-reactance（VBR）模型把定子保留在物理 `abc` 相坐标、把转子放在 `qd` 坐标，并以转子磁链为独立变量；摘要直接声称，这一接口是 non-iterative 和 simultaneous，并在单机无穷大母线算例中比若干既有 EMTP 机器模型更准确、更高效。[pdf:E01](_evidence/E01-p001-title-abstract-introduction.png)（PDF 物理页 1，Abstract）

这个问题重要，是因为 EMT 仿真需要保留定子快速暂态，而经典 `qd` 模型与网络之间的预测、补偿或延迟接口会把“机器模型本身的物理误差”和“接口造成的数值误差”混在一起。论文指出，既有 `qd` 接口为了控制误差通常必须缩小时间步，较大时间步会迅速损失精度，已有研究还报告过数值不稳定；这些问题对必须按固定时间预算推进的实时仿真尤其不利。[pdf:E01](_evidence/E01-p001-title-abstract-introduction.png)（PDF 物理页 1，Introduction）物理上，作者要保留的是定子端口对外部网络的直接电气耦合；计算上，作者要压缩的是转子内部随角度变化的重复代数工作。

论文的价值边界也很清楚：它证明的是一种同步机数值表示和 EMTP 接口的优势，不是 FPGA 实现。文中没有报告固定点位宽、片上资源、流水线、时钟频率或硬实时最坏步时；只把该模型与 UBC 实时电力系统仿真器背景联系起来，并把 multirate 与 latency 技术列为未来可利用方向。[pdf:E02](_evidence/E02-p002-vbr-contributions-models.png)（PDF 物理页 2，Introduction，贡献 4）

## § 2 — 前人工作与不足

论文把当时常见的 EMTP 同步机接口归为三条路线。第一条把机器内部写成 `qd` 模型，再以相坐标 Thevenin 等效接入网络；机器电气、机械量采用 predictor-corrector，而网络不迭代，MicroTran Type-50 和 DCG/EPRI EMTP Type-59 属于此类。它的优点是 `qd` 电感矩阵为常数，且较方便加入磁饱和；不足是等效电压源包含预测量，转子凸极还要靠平均等效电阻处理，因此接口误差随步长增大而放大。[pdf:E01](_evidence/E01-p001-title-abstract-introduction.png)（PDF 物理页 1，Introduction）

第二条是 compensation method：把外部交流系统化成 Thevenin 等效、在 `qd` 轴中连接机器，并对电气、机械变量迭代。当分布参数线路把机器彼此隔开时它能工作，但没有这种天然隔离时常需人工加入 “stub lines”，这既复杂化网络又损害精度；ATP universal machine model 是论文给出的实例。第三条是 PSCAD/EMTDC 的 Norton 电流源加终端阻抗接口，电流源使用前一时间步的端口母线电压，因此固有地引入一步延迟。[pdf:E01](_evidence/E01-p001-title-abstract-introduction.png)（PDF 物理页 1，Introduction）

PD 模型走了另一条路：直接在物理相变量中保留耦合电路，定子电路可与外部网络直接合并，不必预测或迭代电气端口量，因而改善了接口稳定性，还能更自然地表示内部故障。但它的定、转子互感随转子位置变化，离散后需要持续更新更大的矩阵和转矩表达式；论文提到 ATP Type-58 的实现每一步都要重新 triangularization。[pdf:E01](_evidence/E01-p001-title-abstract-introduction.png)（PDF 物理页 1 至物理页 2，Introduction）[pdf:E02](_evidence/E02-p002-vbr-contributions-models.png)（PDF 物理页 2，Introduction）

VBR 并不是从零发明的新机器物理模型。作者明确说，VBR 已在更早文献中用于 state-variable approach，也有 hardware-in-the-loop 示例；本论文的新增工作是把它扩展为适合 EMTP 节点分析的离散接口，并与 PD 和传统 `qd` 接口做数值、计算比较。[pdf:E02](_evidence/E02-p002-vbr-contributions-models.png)（PDF 物理页 2，Introduction）因此，本卡把贡献表述为“EMTP 离散形式和接口重构”，不把 VBR 概念本身说成本文首创。

## § 3 — 重建作者的思考路径

以下是基于论文证据重建的推断，不是作者逐句陈述的历史。第一步，从 EMTP 的求解结构出发：节点法最擅长处理形如“等效阻抗加历史源”的支路，所以同步机若能在当前步直接贡献一个三相 Thevenin 端口，就能与其余网络同时求解。第二步，观察传统 `qd` 模型为什么接口差：它把网络可见的相量藏在旋转坐标内部，只好预测快速电气量或做跨接口迭代。第三步，观察 PD 为什么稳定但昂贵：它把相电流作为独立变量，接口正确，却让所有转子绕组都卷入位置相关的大矩阵。

自然的折中是只在网络真正需要看到的地方保留相坐标。定子三相电流继续作为节点方程的未知量，转子内部则回到 `qd` 坐标并使用磁链作为状态；这样，转子的大部分系数可在主时间循环外预计算，而定子端口仍然直接进入网络。[pdf:E02](_evidence/E02-p002-vbr-contributions-models.png)（PDF 物理页 2，作者列出的优势 1-3）最后再用同一个隐式梯形规则把 PD 和 VBR 都化为等价的 Thevenin 形式，才能把差异归因于状态选择和离散接口，而不是积分器不同。[pdf:E04](_evidence/E04-p004-discrete-time-equations.png)（PDF 物理页 4，Section III）

这条思路的关键不是“把坐标变换做得更快”，而是把坐标系按物理职责分区：`abc` 服务网络耦合，`qd` 服务转子内部状态压缩。论文后续的 flop 统计也支持这条重建：PD 每步合计 546 次 flop、10 次 trig，VBR 为 241 次 flop、9 次 trig；节省主要来自历史源、转子状态和转矩计算，而不是少算了网络本身。[pdf:E05](_evidence/E05-p005-thevenin-complexity-table.png)（PDF 物理页 5，Table I 与 Section III-C）

## § 4 — 核心 Intuition

把同步机看成“外部网络看到的三相端口”与“内部转子记忆”两部分：端口必须留在 `abc` 相坐标，才能在当前时间步直接并入 EMTP；内部转子则用 `qd` 磁链状态表示，让大量系数成为常数并可预计算。VBR 用一个随转子角度变化的等效电抗和一个 subtransient voltage 历史源把两部分重新接起来，于是获得 PD 的直接网络接口，却避免 PD 对完整位置相关耦合矩阵的重复计算。[pdf:E03](_evidence/E03-p003-vbr-continuous-equations.png)（PDF 物理页 3，Section II-C）

## § 5 — 具体方法与完整 Pipeline

连续时间模型先把定子写成

\[
\mathbf v_{abcs}=\mathbf R_s\mathbf i_{abcs}
+p\!\left[\mathbf L''_{abcs}(\theta_r)\mathbf i_{abcs}\right]
+\mathbf v''_{abcs},
\]

其中 \(\mathbf i_{abcs}\) 是外部节点求解直接使用的三相定子电流，\(\mathbf L''_{abcs}(\theta_r)\) 是随转子角度变化的次暂态电感矩阵，\(\mathbf v''_{abcs}\) 则由转子 `qd` 磁链、转速、励磁和阻尼绕组共同形成。[pdf:E03](_evidence/E03-p003-vbr-continuous-equations.png)（PDF 物理页 3，Eq. 16-32）这意味着网络端口不需要知道每个转子绕组，只需要看到一个三相电抗和背后的三相电压源。

离散后，一个时间步的完整 pipeline 如下。

1. **预测慢变量。** 用前两步对 \(\theta_r\) 和 \(\omega_r\) 线性外推，即 Eq. 56-57。作者的理由是机械变量相对电气变量变化较慢；若要求机械、电气完全同时且精确耦合，一般会需要迭代。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section IV，step 1）
2. **形成三相 Thevenin 端口。** 用 Eq. 54 的 \(\mathbf R^{vbr}_{eq}(t)\) 和 Eq. 55 的 \(\mathbf e^{vbr}_{h}(t)\) 组装 Fig. 1 中的三相等效源加等效电阻；示例假设 Y 接且中性点接地，但作者说明其他绕组连接也可处理。[pdf:E05](_evidence/E05-p005-thevenin-complexity-table.png)（PDF 物理页 5，Eq. 53-55 与 Section IV）[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Fig. 1）
3. **求网络当前步。** 将机器端口与外部元件共同写入 conductance matrix \(\mathbf G\)，完成 triangularization 并求得当前步网络电压和支路量。这一步不是用上一时刻母线电压驱动 Norton 源，而是在当前步节点方程里同时闭合。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section IV，step 3）
4. **回写电磁状态。** 由 Eq. 53 得到定子电流，由 Eq. 47-48 更新转子磁链，再用 Eq. 50、46、52 更新次暂态电压和历史源。[pdf:E04](_evidence/E04-p004-discrete-time-equations.png)（PDF 物理页 4，Eq. 45-48）[pdf:E05](_evidence/E05-p005-thevenin-complexity-table.png)（PDF 物理页 5，Eq. 49-55）
5. **回写机械状态。** 用 Eq. 33 从 `qd` 磁链和电流计算电磁转矩，再用隐式梯形离散的 Eq. 34-35 重新计算转子位置与转速。[pdf:E04](_evidence/E04-p004-discrete-time-equations.png)（PDF 物理页 4，Eq. 33-35）这次校正完成后，进入下一时间步。

对一个真实工况，论文以单机无穷大母线为例：机器初始空载稳态，\(T_m=0\)，额定励磁保持不变，\(t=0\) 时在机器端施加对称三相故障。输出是励磁电流 \(i_{fd}\)、a 相定子电流 \(i_{as}\) 和电磁转矩 \(T_e\) 的暂态轨迹。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section V 与 Fig. 2-3）

论文没有 FPGA 映射。对 FPGA 读者最值得带走的是计算依赖：一个步内仍有“机械预测 → 端口组装 → 网络求解 → 电磁状态更新 → 机械校正”的先后关系；可以预计算的常系数集中在转子状态更新中，但网络 conductance matrix 含时变机器项。数值表示、定点误差、片上存储、并行流水线和 deadline 均未报告，不能从 C 语言 CPU 结果直接外推。

## § 6 — 核心数学推导（无形式化数学则跳过）

**第一层：连续物理模型。** PD 模型把完整耦合电感矩阵写成 \(\mathbf L(\theta_r)\)，转矩由该矩阵对转角的偏导得到；这使定子能直接入网，但矩阵大且处处随角度变化。[pdf:E03](_evidence/E03-p003-vbr-continuous-equations.png)（PDF 物理页 3，Eq. 14-15）VBR 的重新参数化保留位置相关的三相次暂态电感 \(\mathbf L''_{abcs}(\theta_r)\)，却把转子阻尼与励磁绕组状态收进 `qd` 磁链。其物理意义是：外部网络只看见转子对定子端口造成的“次暂态电抗 + 背后电势”，而不是显式看见所有转子支路。

**第二层：转子状态与转矩。** q 轴、d 轴磁化磁链分别由阻尼/励磁磁链和定子 `qd` 电流组合，转子绕组磁链按一阶微分方程衰减并受励磁驱动；电磁转矩写成

\[
T_e=\frac{3P}{4}\left(\lambda_{md}i_{qs}-\lambda_{mq}i_{ds}\right).
\]

这里 \(P\) 是极数，\(\lambda_{md},\lambda_{mq}\) 是 d、q 轴磁化磁链，\(i_{ds},i_{qs}\) 是相应轴定子电流。直观上，它是两轴磁场与正交电流的交叉作用：一项产生正向电磁转矩，另一项抵消。[pdf:E03](_evidence/E03-p003-vbr-continuous-equations.png)（PDF 物理页 3，Eq. 29-32）[pdf:E04](_evidence/E04-p004-discrete-time-equations.png)（PDF 物理页 4，Eq. 33）

**第三层：隐式梯形离散。** 论文对机械方程、PD 电路和 VBR 电路都使用同一个隐式梯形规则。以 VBR 定子端口为例，当前步电压含 \((\mathbf R_s+2\mathbf L''_{abcs}(t)/\Delta t)\mathbf i_{abcs}(t)\)、当前步背后电势以及由前一步电压、电流和电感形成的历史源。[pdf:E04](_evidence/E04-p004-discrete-time-equations.png)（PDF 物理页 4，Eq. 45-46）把 Eq. 47-48 的转子磁链更新代回 Eq. 49-52 后，当前步转子输出可消元，最终得到标准 EMTP 端口：

\[
\mathbf v_{abcs}(t)=\mathbf R^{vbr}_{eq}(t)\mathbf i_{abcs}(t)+\mathbf e^{vbr}_h(t),
\]

\[
\mathbf R^{vbr}_{eq}(t)=\mathbf R_s+\frac{2}{\Delta t}\mathbf L''_{abcs}(t)+\mathbf K(t),\qquad
\mathbf e^{vbr}_h(t)=\mathbf e^{vbr}_r(t)+\mathbf e^{vbr}_{sh}(t).
\]

\(\mathbf K(t)\) 是把转子状态对当前定子电流的反馈折算到三相端口的矩阵；\(\mathbf e_r^{vbr}\) 包含励磁与转子历史，\(\mathbf e_{sh}^{vbr}\) 则是梯形积分产生的定子历史源。[pdf:E05](_evidence/E05-p005-thevenin-complexity-table.png)（PDF 物理页 5，Eq. 49-55）

**第四层：为什么离散后精度不同。** 三种连续时间模型在代数上等价，但在指定积分规则和接口下，误差传播矩阵不同。论文把一步更新统一写成

\[
\mathbf x_n=\boldsymbol\Phi(\Delta t,t,\mathbf x_{n-1})\mathbf x_{n-1}
+\mathbf f(\Delta t,t),
\]

并用 \(\boldsymbol\Phi\) 的离散特征值解释局部误差如何传到下一步。作者特别提醒：系统是时变的，因此特征值在单位圆外不能机械地等同于整体不稳定；这里的特征值只作为 numerical conditioning 与误差传播的线索。[pdf:E08](_evidence/E08-p008-cpu-eigenvalue-analysis.png)（PDF 物理页 8，Eq. 59、Table III 与 Section VI）

## § 7 — 实验设计与结论

**问题 1：VBR 是否与已有连续机器模型一致？** 作者用 MATLAB/Simulink 中的 `qd` state-variable 模型、四阶 Runge-Kutta 和 \(1\,\mu s\) 步长生成参考解，再让 MicroTran、ATP、PD 与 VBR 以 \(50\,\mu s\) 重演同一三相端故障。Fig. 2 中各模型的 \(i_{fd}\)、\(i_{as}\)、\(T_e\) 视觉上不可区分，作者据此验证 VBR 的基本实现等价性。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section V-A 与 Fig. 2）

**问题 2：步长放大时谁更准确、更稳定？** 在 \(\Delta t=1\,ms\) 时，MicroTran Type-50 出现明显误差，ATP Type-59 已不收敛；PD 与 VBR 仍稳定且接近参考解，Fig. 4 的电流峰值局部显示 VBR 点更靠近参考轨迹。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Fig. 3）[pdf:E07](_evidence/E07-p007-accuracy-error-figures.png)（PDF 物理页 7，Fig. 4 与 Section V-B）作者用 Eq. 58 的轨迹 2-norm 相对误差评价 \(i_{as}\)；当步长大于 \(0.2\,ms\) 时，MicroTran 的 `qd` 模型误差超过 4%，ATP 模型不再收敛。[pdf:E07](_evidence/E07-p007-accuracy-error-figures.png)（PDF 物理页 7，Eq. 58、Fig. 5-6）

**问题 3：相同误差容限下的总体效率如何？** 以 0.25% 相对误差为阈值，MicroTran 和 ATP 的 `qd` 模型需要 \(10\,\mu s\)，PD 需要 \(150\,\mu s\)，VBR 可用到 \(500\,\mu s\)。按允许步长看，VBR 是 PD 的约 3.3 倍、传统 `qd` 接口的约 50 倍；作者再结合单步 CPU 时间，报告相对 PD 有 660% 的总体改进。[pdf:E08](_evidence/E08-p008-cpu-eigenvalue-analysis.png)（PDF 物理页 8，Section V-C）

**问题 4：机器模型本身每步少算了多少？** Table I 的手工复杂度统计为 PD 546 flop、10 trig，VBR 241 flop、9 trig。两种模型又以标准 C 编译，在 Pentium 4 2.66 GHz、512 MB RAM 上运行 \(0.2\,s\) 算例，步长 \(50\,\mu s\)：PD 总用时 0.031 s、每步 \(7.75\,\mu s\)，VBR 为 0.015 s、每步 \(3.75\,\mu s\)。论文称这是约 200% 的 simulation speed improvement；更朴素地说，报告数据对应约 2.07 倍吞吐或约 52% 用时减少。[pdf:E05](_evidence/E05-p005-thevenin-complexity-table.png)（PDF 物理页 5，Table I）[pdf:E08](_evidence/E08-p008-cpu-eigenvalue-analysis.png)（PDF 物理页 8，Table II）

**问题 5：误差优势是否有数值结构上的解释？** 在 \(\Delta t=1\,ms\) 的离散模型中，作者报告 VBR 最大特征值幅值约 1.031，PD 为 2.498，并把前者更接近单位圆原点解释为较好的 numerical conditioning；这一解释与 Fig. 5-6 的误差排序一致，但不是独立的稳定性证明。[pdf:E08](_evidence/E08-p008-cpu-eigenvalue-analysis.png)（PDF 物理页 8，Table III 与 Section VI）

不得外推的范围同样重要。所有主要验证都来自一台 835 MVA、26 kV、2 极、3600 r/min 的同步机参数和一个单机无穷大母线对称三相端故障；不平衡工况被指向另一篇投稿，本文没有展示。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section V）[pdf:E10](_evidence/E10-p010-machine-parameters.png)（PDF 物理页 10，Appendix B）更大网络的 factorization 开销也没有纳入上述单机结论：作者明确指出 VBR 会给网络 conductance matrix 引入时变项，若整张矩阵每步重新分解，端到端执行时间可能上升；机器占比、网络规模和分解策略都会改变结论。[pdf:E09](_evidence/E09-p009-network-scaling-conclusion.png)（PDF 物理页 9，Section VII）

## § 8 — Take-aways

**5 句话：**

1. VBR 在网络侧保留 `abc` 相电流，在转子侧保留 `qd` 磁链，从变量选择上同时照顾直接节点接口和内部计算效率。[pdf:E02](_evidence/E02-p002-vbr-contributions-models.png)（PDF 物理页 2）
2. 隐式梯形离散后，机器可化成当前步三相 Thevenin 端口，与外部网络非迭代、同时闭合。[pdf:E05](_evidence/E05-p005-thevenin-complexity-table.png)（PDF 物理页 5，Eq. 53-55）
3. 单机故障算例中，VBR 在大步长下比传统 `qd` 接口更准确，也比 PD 更省单步计算。[pdf:E07](_evidence/E07-p007-accuracy-error-figures.png)（PDF 物理页 7）[pdf:E08](_evidence/E08-p008-cpu-eigenvalue-analysis.png)（PDF 物理页 8）
4. 连续模型等价并不意味着离散接口等价，状态选择和历史源构造会改变误差传播。
5. 论文还没有证明在多机大网络、快速机械事件或 FPGA 固定点实现中仍保持同样的端到端优势。

**3 句话：**

1. VBR 的核心是把同步机按端口耦合与内部记忆分区，而不是简单删减物理阶次。
2. 这种分区把 PD 的直接网络接口和 `qd` 转子表示的低计算量结合起来，并在作者的单机故障基准上扩大了可用时间步。
3. 真正未闭合的问题是，时变机器端口引起的网络分解成本和机械预测误差，会不会在大系统或更激烈工况中吃掉收益。[pdf:E09](_evidence/E09-p009-network-scaling-conclusion.png)（PDF 物理页 9）

**1 句话：**

VBR 证明了“选对网络可见变量”可以比单纯优化方程运算更有效，但其系统级实时价值仍需在多机网络的真实求解器成本下验证。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**一个时间步内机械变量足够慢，\(\theta_r\) 与 \(\omega_r\) 的两步线性外推足以代表当前步，因此不必把机械方程与电气网络一起迭代求解。** 作者明确承认，机械方程非线性，若要求机械、电气变量精确同时求解，一般会需要迭代；论文之所以仍能宣称 non-iterative，是因为采用了 Eq. 56-57 的慢变量假设。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section IV，step 1）

如果在高扭矩阶跃、轴系扭振、失步边缘或较大时间步下，转速和转角在相邻步之间不再近似线性，那么错误的角度会同时污染 \(\mathbf L''_{abcs}(\theta_r)\)、坐标变换、背后电势和电磁转矩。此时错误不是只留在机械侧，而会通过当前步 Thevenin 端口反馈到整个网络；要恢复精度可能必须缩步或迭代，核心的“非迭代且可用大步长”优势会一起失效。这是基于方程依赖关系的推断。

论文提供的证据只覆盖空载、恒励磁、机器端对称三相故障；这个工况虽然电气暂态强，却没有专门构造快速机械激励，也没有报告机械外推残差或与 fully coupled implicit solution 的差异。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section V）所以该假设在作者算例中没有显然失败，但也没有被单独验证。

## § 10 — 最小复现实验

一周内最值得复现的是“相同误差容限下，VBR 是否真的允许比 PD 更大时间步”，并顺便测出机械预测何时开始失效。

1. **数据与基线：** 使用 Appendix B 的同步机参数，搭建同一单机无穷大母线、空载 \(T_m=0\)、恒定额定励磁和 \(t=0\) 机器端对称三相故障。[pdf:E10](_evidence/E10-p010-machine-parameters.png)（PDF 物理页 10，Appendix B）用同一双精度代码实现 PD 与 VBR；参考解用完整 `qd` state-space 模型、四阶 Runge-Kutta、\(1\,\mu s\) 步长，复现论文的基线定义。[pdf:E06](_evidence/E06-p006-interface-study-figures.png)（PDF 物理页 6，Section V-A）
2. **实现范围：** 只实现论文 Eq. 34-55 的隐式梯形更新和 Fig. 1 的三相端口，不做 GUI、FPGA 或完整商用 EMTP。确保 PD 与 VBR 共用网络求解、编译器选项、计时边界和初值。
3. **扫参：** 对 \(\Delta t=10,50,100,150,200,500,1000\,\mu s\) 分别运行 0.2 s；除原始对称故障外，再加入一个可控机械转矩阶跃幅值扫描，以观察外推残差。
4. **测量：** 按 Eq. 58 计算 \(i_{as}\) 轨迹 2-norm 相对误差，同时记录 \(i_{fd}\)、\(T_e\)、是否收敛、每步 CPU 时间、整网 factorization 时间、\(\theta_r/\omega_r\) 预测值与校正值之差。[pdf:E07](_evidence/E07-p007-accuracy-error-figures.png)（PDF 物理页 7，Eq. 58）
5. **支持标准：** 在原论文工况中，VBR 于 \(500\,\mu s\) 仍不超过 0.25% 的 \(i_{as}\) 误差，PD 需要约 \(150\,\mu s\) 才满足相同阈值，并且 VBR 的同一步计时显著低于 PD，才算复现核心 claim。[pdf:E08](_evidence/E08-p008-cpu-eigenvalue-analysis.png)（PDF 物理页 8，Section V-C）
6. **反驳标准：** 若共享同一网络求解器后 VBR 的总步时优势消失，或轻微机械转矩阶跃就使其必须缩到与 PD 相同甚至更小步长，便反驳“接口结构带来总体效率优势”的广义解释，即使机器方程的 flop 数仍较少。

## § 11 — 最强反例设计

最强反例不是再画一条不同故障波形，而是构造一个**机器占比高、网络没有线路天然隔离、同时含快速机械事件的多机系统**。例如，把同一同步机参数复制到一个 30 至 100 机的稠密网络，所有机器端口都直接进入同一节点矩阵；在电气三相故障之外，对一部分机器施加快速扭矩阶跃或轴系扭振激励。比较 VBR、PD 和 fully coupled implicit reference，在统一 \(i_{as}\)、转矩、转角误差阈值下测量最大单步延迟、均值步时、全矩阵重分解次数以及机械预测校正量。

这个设计同时攻击两处机制。快速机械事件攻击 §9 的慢变量外推；高机器占比攻击 VBR 的时变 \(\mathbf R^{vbr}_{eq}(t)\) 是否迫使网络矩阵频繁重分解。论文自己指出，时变元件的代价依赖机器占比与系统规模，并建议至少比较一个机器占比小和一个机器很多的系统；它还引用 190-bus、3-generator 案例中重 triangularization 带来约 4.4 倍计算时间，并在另一 compensation 示例中观察到约 15% 每步开销。[pdf:E09](_evidence/E09-p009-network-scaling-conclusion.png)（PDF 物理页 9，Section VII）

若 VBR 的机器内部更新仍快，但端到端最坏步时不再优于 PD，或者为保持误差必须引入迭代，那么论文在单机算例中显示的“计算优势”就不能外推为多机实时 EMTP 的系统优势。反过来，若低秩更新或局部 factorization 能让 VBR 在该反例中仍保持 deadline 与误差优势，才真正强化其工程 claim。

## § 12 — Follow-up Research Idea

**候选方向：factorization-aware、误差受控的 VBR 端口契约。** 本卡未额外检索 2006 年后的紧密相关全文，因此不声称该方向具有已验证 novelty。

**(a) 未满足的需求。** 论文优化了机器内部 flop，却允许 \(\mathbf R^{vbr}_{eq}(t)\) 随转角变化；在多机网络中，真正决定实时 deadline 的可能是整网 factorization，而不是机器状态更新。同时，固定两步机械外推没有在线误差界。需要把“机器端口怎样变化”与“网络矩阵何时必须重分解”一起设计。

**(b) 研究价值。** 将目标从平均机器计算量改成“给定端口误差上界下的最坏单步延迟”，能直接对应 EMT real-time/HIL 的工程判据。若在多机强扰动下仍能证明或实验保证 deadline，这比在单机上再降低一部分 flop 更接近本领域重视的可实现性、数值可信度与系统规模。

**(c) 可借鉴的相邻工具。** 从 sparse linear algebra 借用 low-rank matrix update、Schur complement 和局部 refactorization；从 adaptive integration 借用 a posteriori error estimator。机器每步先提交“常量基准 stamp + 低秩角度修正 + 历史源”，只有当机械预测残差或端口电流误差估计超过阈值时，才升级为局部重分解、缩步或一次校正迭代。论文已提出把机器节点放在矩阵末端、只更新较小下部子矩阵的方向，但没有把它与端口误差控制合成一个契约。[pdf:E09](_evidence/E09-p009-network-scaling-conclusion.png)（PDF 物理页 9，Section VII）

**(d) 首个证伪实验。** 使用 §11 的高机器占比多机系统，在相同误差阈值下对比原始 VBR、PD、全矩阵每步重分解和候选方法。若候选方法在强机械事件下几乎每步都触发全重分解/迭代，或最大单步延迟不低于原始方案，便立即否定“端口契约能稳定节省系统成本”的假设。

**(e) 与本文的实质区别。** 本文的问题是“怎样把 VBR 离散并接入 EMTP，同时降低机器方程计算量”；候选研究把问题改写为“怎样让机器端口变化服从可验证的网络求解成本与误差预算”。它不再把网络 factorization 当作实现后的附属讨论，而把端到端矩阵更新策略、机械预测可信度和实时 deadline 作为同一个模型接口的组成部分。
