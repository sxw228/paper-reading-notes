# FPGA-Based Sub-Microsecond-Level Real-Time Simulation for Microgrids With a Network-Decoupled Algorithm

- 作者：Jin Xu, Keyou Wang, Pan Wu, Guojie Li
- 出处：IEEE Transactions on Power Delivery, 35(2), 2020, pp. 987–998
- DOI：10.1109/TPWRD.2019.2932993
- Zotero key：WNRAZ79Z

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个很具体的实时约束：能否只用一片 FPGA，在亚微秒步长内完成包含多个电力电子变换器和多条配电线路的微电网 electromagnetic transient（EMT）仿真。这里的“实时”不是仿真最终能跑完，而是每一个离散步的全部计算都必须在同样长的墙钟时间内完成，否则控制器硬件在环（HIL）闭环就会失去正确的时间关系。作者指出，20 kHz 开关频率通常要求小于 500 ns 的步长以准确反映开关时刻，而当时商用实时仿真器常见的步长范围是 0.5–2 μs；小步长与系统规模共同把计算量和 FPGA 资源推向瓶颈。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题的工程价值在于：微电网控制、保护和运行策略在进入真实系统前需要 HIL 验证，但变换器的快速离散开关会迫使 EMT 求解器同时满足“快”和“大”两个互相冲突的目标。[pdf:E01]（PDF 物理页 1，Introduction）物理上，步长决定仿真能否看见开关动作及其引起的电磁暂态；硬件资源决定同一时刻能容纳多少节点、支路和变换器。若只能二选一，仿真器要么漏掉开关细节，要么只能模拟一个器件而不是有网络耦合的微电网。

作者的核心 claim 是：把每个变换器局部网络交给 nodal analysis method（NAM，节点分析法），把连接它们的线路网络交给 latency insertion method（LIM，延迟插入法），可以切断各 DG 子系统之间的全局稠密计算依赖，使它们并行运行；在其案例中，一片 Xilinx Kintex-7 410T 最终容纳了三个三相变换器、三个 boost 电路和 21 条三相线路，最小实时步长为 380 ns。[pdf:E01]（PDF 物理页 1，Abstract）

## § 2 — 前人工作与不足

论文把既有路线分成三类。第一类通过插值改善开关时刻，但作者指出 multiple switching 仍是问题，因此小步长仍难避免。第二类是在 FPGA 上实现 EMTP、旋转电机或变换器实时仿真，并用 fixed-admittance、associated discrete circuit（ADC）或 small-time-step switch model 降低开关引起的矩阵重构成本。第三类用四片 FPGA 或 MPSoC-FPGA 扩大微电网、直流电网的规模。[pdf:E01]（PDF 物理页 1，Introduction）；[pdf:E12]（PDF 物理页 12，References [5]–[15]）

不足不是“以前没人用 FPGA”，而是求解结构仍随规模恶化。作者引用的传统集中式 NAM，其计算量被描述为随系统规模呈二次增长，执行时间和资源会很快上升；分布式 LIM 的计算量近似线性增长，却暂时不能直接容纳开关级变换器拓扑。[pdf:E02]（PDF 物理页 2，Section II）也就是说，NAM 会算变换器但难扩展，LIM 会扩展线路但不会算开关网络。论文真正针对的是这两个方法各自的“适用域”错位，而不是单纯换一片更大的 FPGA。

作者还援引了 LIM 的原始方法、不同积分格式下的稳定性分析、非均匀 GLC/RLC 网络稳定条件，以及 CIGRE 微电网与 HIL benchmark；这些是论文自身采用的相关工作脉络，而不是本卡独立复核后的领域全景。[pdf:E12]（PDF 物理页 12，References [17]–[25]）因此，本节只能确认“作者如何定位前人工作”，不能据此单独证明该方法在 2020 年具有唯一性。

## § 3 — 重建作者的思考路径

可以从三个此前已知的工程事实重建这条路线。第一，变换器内部开关多、耦合紧，但每一个 DG 子系统的局部规模不大；第二，配电线路网络规模大、结构稀疏，且天然由串联 R–L 支路和对地 G–C 节点组成，正好适合 LIM；第三，fixed-admittance switch model 能让开关状态改变时等效导纳保持不变，只更新历史源，从而避免每个 PWM 边沿重建节点导纳矩阵。[pdf:E02]（PDF 物理页 2，Figs. 1–2 与 Section III-A）；[pdf:E03]（PDF 物理页 3，Eqs. (9)–(14)）

下一步自然不是强迫一种算法吃掉全部网络，而是沿 LCL filter 把网络切开：局部变换器岛仍用经过压缩的 EMTP/NAM，外部线路用 LIM；接口的一侧看见等效电流源，另一侧看见等效电压源。[pdf:E04]（PDF 物理页 4，Fig. 4 与 Eqs. (23)–(30)）这样，每个 DG 岛只做自己的小型非对角矩阵乘法，线路网络只做大型对角矩阵乘法。由于 FPGA 擅长流水线和并行乘加，原来的一个全局大矩阵就被重写为多个可同时启动的局部任务。[pdf:E06]（PDF 物理页 6，Fig. 6 与 Table I）；[pdf:E07]（PDF 物理页 7，Figs. 7–8）

这条思路的代价也在推导中出现：NAM 与 LIM 交换的是上一步得到的接口量，因此接口引入一个 time-step delay。作者的判断是，亚微秒步长远快于微电网动态，只要组合系统数值稳定，这个延迟对精度的影响很小。[pdf:E04]（PDF 物理页 4，Section III-C 末段）这不是无代价解耦，而是用一个显式、可分析的延迟换取并行性。

## § 4 — 核心 Intuition

核心 intuition 是：不要让整张微电网共享一个越来越大的节点方程，而让“难并行但规模小”的变换器留在 NAM 岛内，让“规模大但结构规则”的线路进入 LIM，再只交换接口源。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II）物理上，每个 DG 岛像一个独立的快速电磁子系统，线路网络负责在下一步传播彼此影响；计算上，这把一个大而稠密的关键路径改成多个小而稠密的路径加一个可并行的对角路径。[pdf:E07]（PDF 物理页 7，Figs. 7–8）方法能扩展的关键不是 FPGA “更快”，而是全局耦合被改写成局部求解与延迟接口。

## § 5 — 具体方法与完整 Pipeline

以论文的离网 Microgrid 3 为例，输入是一套含电池、两个 PV 系统、六个变换器和 21 条三相线路的电路及其 PWM/控制信号；输出是每个实时步的节点电压、支路电流，并回送给实时 CPU 控制器。[pdf:E08]（PDF 物理页 8，Fig. 11 与 Section V–VI-A）

1. **网络分区。** 每个电池或 PV 的 boost、DC/AC converter 和 LCL filter 局部电路组成 NAM network；三相线路/电缆用 π-circuit model 组成 LIM network。LCL filter 被选作二者接口。[pdf:E02]（PDF 物理页 2，Fig. 1）；[pdf:E04]（PDF 物理页 4，Fig. 4）
2. **LIM 时间推进。** 每个 LIM node 写成对地电流源 \(H_i\)、电导 \(G_i\)、电容 \(C_i\) 的并联；每个 LIM branch 写成电压源 \(E_{ij}\)、电阻 \(R_{ij}\)、电感 \(L_{ij}\) 的串联。节点电压放在半步，支路电流放在整步，用二阶 leap-frog scheme 交错更新。[pdf:E02]（PDF 物理页 2，Fig. 2 与 Eqs. (1)–(2)）
3. **NAM 开关处理。** 所有支路先化为 Norton equivalent。开关导通时视为小电感 \(L_{\mathrm{sml}}\)，关断时视为小电容 \(C_{\mathrm{sml}}\)；令 \(\Delta t/L_{\mathrm{sml}}=C_{\mathrm{sml}}/\Delta t\)，即可使等效导纳 \(Y_{\mathrm{eq}}\) 不随开关状态改变，只让历史电流源系数 \(\alpha,\beta\) 随 PWM 更新。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Eqs. (9)–(14)）
4. **压缩 EMTP loop。** 作者把标准 NAM 的 Eqs. (14)–(18) 合并为 Eqs. (19)–(20)，预计算 \(K=-Y_{\mathrm{nodal}}^{-1}M_{\mathrm{NAM}}\) 和 \(L=-Y_{\mathrm{eq}}M_{\mathrm{NAM}}^{T}Y_{\mathrm{nodal}}^{-1}M_{\mathrm{NAM}}+I\)，减少串行计算链及误差扩散。[pdf:E04]（PDF 物理页 4，Eqs. (15)–(22)）
5. **接口交换。** NAM 把线路侧等效为注入节点的电流源，LIM 把变换器侧等效为支路上的电压源；互关联矩阵只负责把对应接口量搬到另一子网。完整循环先并行更新 LIM 节点量、NAM 节点/支路量和 NAM 历史源，再在接口数据就绪后更新 LIM 支路量。[pdf:E04]（PDF 物理页 4，Eqs. (23)–(30)）；[pdf:E05]（PDF 物理页 5，Fig. 5）
6. **稳定性门槛。** 先用 LIM 的步长条件 Eq. (31) 选择候选 \(\Delta t\)，再把组合 LIM–NAM 系统写成离散状态方程，检查整体状态矩阵的谱半径 \(\rho(A_{\mathrm{SYS}})<1\)。[pdf:E05]（PDF 物理页 5，Eqs. (31)–(40)）；[pdf:E06]（PDF 物理页 6，Eqs. (41)–(44)）
7. **FPGA 映射。** 常系数矩阵预计算并存储；只含 \(0,1,-1\) 的关联矩阵及 \(\alpha,\beta\) 相关乘法用 logic resource，实现时不占 multiplier。非对角矩阵按列串行输入并流水累加，对角矩阵则一次并行乘完。[pdf:E06]（PDF 物理页 6，Fig. 6 与 Section IV-A）
8. **平台闭环。** NI PXIe 平台中，FPGA module 运行电路 EMT 与 PWM generation，real-time CPU 运行 DG controls，host PC 负责 HMI 与记录，示波器可通过 FPGA I/O 直接观察信号。[pdf:E07]（PDF 物理页 7，Figs. 9–10）；[pdf:E08]（PDF 物理页 8，Section V）

## § 6 — 核心数学推导（无形式化数学则跳过）

第一层是 LIM 的交错积分。对一个 LIM 节点，KCL 离散后得到

\[
V_i^{n+1/2}
=
\left(\frac{C_i}{\Delta t}+G_i\right)^{-1}
\frac{C_i}{\Delta t}V_i^{n-1/2}
-
\left(\frac{C_i}{\Delta t}+G_i\right)^{-1}
\left(\sum_{k\in N_i} I_{ik}^{n}-H_i^n\right).
\]

对一条 LIM 支路，

\[
I_{ij}^{n+1}
=
\left(1-\frac{\Delta t}{L_{ij}}R_{ij}\right)I_{ij}^{n}
+
\frac{\Delta t}{L_{ij}}
\left(V_i^{n+1/2}-V_j^{n+1/2}+E_{ij}^{n+1/2}\right).
\]

节点电压和支路电流错开半个步长，意味着更新节点时用已知的整步电流，更新支路时又能立即使用新的半步电压；这正是消除同一步内全局联立求解的数学来源。[pdf:E02]（PDF 物理页 2，Eqs. (1)–(2)）；[pdf:E03]（PDF 物理页 3，Eqs. (3)–(8)）

第二层是 fixed-admittance switch model。统一历史源写成

\[
I_{\mathrm{history}}^{n+1}
=
\alpha Y_{\mathrm{eq}}V_{\mathrm{branch}}^{n}
+
\beta I_{\mathrm{branch}}^{n}.
\]

导通开关取 \(\alpha=0,\beta=1,Y_{\mathrm{eq}}=\Delta t/L_{\mathrm{sml}}\)，关断开关取 \(\alpha=-1,\beta=0,Y_{\mathrm{eq}}=C_{\mathrm{sml}}/\Delta t\)。通过

\[
Y_{\mathrm{eq}}=\frac{\Delta t}{L_{\mathrm{sml}}}
=\frac{C_{\mathrm{sml}}}{\Delta t},
\]

开关状态只改变历史源的组合，不改变节点导纳矩阵。物理上，导通与关断仍分别表现为很小的电感和很小的电容；计算上，它们被校准为同一个离散端口导纳。[pdf:E03]（PDF 物理页 3，Eqs. (9)–(14)）

第三层是把标准 EMTP loop 压成两个矩阵更新：

\[
\begin{bmatrix}
V_{\mathrm{nodal}}^n\\
I_{\mathrm{branch}}^n
\end{bmatrix}
=
\begin{bmatrix}
K\\
L
\end{bmatrix}
\left(I_{\mathrm{history}}^n+I_{\mathrm{source}}^n\right),
\]

\[
I_{\mathrm{history}}^{n+1}
=
(\alpha+\beta)L
\left(I_{\mathrm{history}}^n+I_{\mathrm{source}}^n\right)
-
\alpha
\left(I_{\mathrm{history}}^n+I_{\mathrm{source}}^n\right).
\]

附录通过把 injection current 代入 nodal equation，再把 branch voltage/current 消元，给出 Eqs. (19)–(20) 的推导。[pdf:E04]（PDF 物理页 4，Eqs. (19)–(22)）；[pdf:E11]（PDF 物理页 11，Appendix A1–A3）

最后，组合系统被写成 \(X_{\mathrm{SYS}}^{n+1}=A_{\mathrm{SYS}}X_{\mathrm{SYS}}^n+B_{\mathrm{SYS}}U_{\mathrm{SYS}}^n\)。作者采用的整体判据是

\[
\rho(A_{\mathrm{SYS}})<1,
\]

也就是所有离散特征值的模严格小于 1。它给出的是所选参数和步长下的渐近稳定条件，不等于对所有拓扑、开关序列和接口延迟都自动成立。[pdf:E05]（PDF 物理页 5，Eqs. (32)–(40)）；[pdf:E06]（PDF 物理页 6，Eqs. (41)–(44)）

## § 7 — 实验设计与结论

**问题一：解耦与一步接口延迟是否仍能保持 EMT 精度？** 作者选用并网 Microgrid 1，让实时 LIM–NAM 与离线 PSCAD/EMTDC 使用相同模型参数、相同控制和相同的 1 μs 步长。Scenario 1 在 0.1 s 把电池从 10 kW 放电切换为 10 kW 充电；Scenario 2 在 0.1 s 施加单相接地故障，0.05 s 后清除。[pdf:E08]（PDF 物理页 8，Section VI-B）图 12–13 中两组波形大体重合；作者报告大多数时间相对误差保持在 3% 以下，包括单相接地故障期间。[pdf:E09]（PDF 物理页 9，Figs. 12–13 与相邻正文）这支持“所测两种工况下精度可接受”，但没有覆盖所有开关状态或稳定边界。

**问题二：它能否承载真实控制闭环的功率平衡变化？** Microgrid 3 离网运行，电池 converter 用 V/f control 稳住微电网电压，两个 PV 用 MPPT。PV #1 辐照度在 75–90 s 从 1000 W/m² 降为 800 W/m²，PV #2 在 80–95 s 做同样扰动。[pdf:E09]（PDF 物理页 9，Scenario 3）作者观察到 PV 功率与电流随辐照度下降，电池补足不平衡功率且输出电压保持；这些波形来自 host-PC 与 oscilloscope。[pdf:E09]（PDF 物理页 9，Figs. 14–15）；[pdf:E10]（PDF 物理页 10，Section VI-C 末段）该实验验证的是闭环行为可运行，不是对 MPPT 或 V/f 控制器性能的全面认证。

**问题三：网络解耦是否真的减少资源并缩短关键路径？** 三个案例都在 Xilinx XC7K410T（1540 个 DSP slices）、100 MHz 时钟上实现；Table II 的比较步长均为 2 μs。Microgrid 1 的解耦/传统结果分别为 348 DSP（22.6%）与 628 DSP（40.8%），执行延迟为 38 ticks（380 ns）与 83 ticks（830 ns）；Microgrid 2 为 672 DSP（43.6%）与 1232 DSP（80.0%），延迟为 38 ticks（380 ns）与 143 ticks（1430 ns）；Microgrid 3 为 972 DSP（63.1%）与估计的 1776 DSP（超过 100%），解耦延迟仍为 38 ticks（380 ns），传统延迟估计为 197 ticks。[pdf:E10]（PDF 物理页 10，Table II）Microgrid 3 的解耦实现还使用了 248048 个 flip-flops（48.8%）、126034 个 LUTs（49.6%）和 97 个 RAM blocks（12.2%）。[pdf:E10]（PDF 物理页 10，Section VI-D）

**问题四：规模增加时，时间是否保持不变？** 作者又扫描了三相 converter 数和三相 line/cable 数。其结果显示，解耦方案的 DSP 使用近似随规模线性增加，而执行时间表面基本恒定；传统 NAM 的执行时间随两种数量增长。论文进一步报告，在没有 converter 时，一片 FPGA 约可模拟 64 条三相线路。[pdf:E10]（PDF 物理页 10，Fig. 16 与 Section VI-E）；[pdf:E11]（PDF 物理页 11，Fig. 17）但“时间不随规模增加”有明确适用条件：新增 DG 岛不能比现有最大 DG 岛更大，且资源仍要容纳所有并行单元。[pdf:E07]（PDF 物理页 7，Fig. 8 后正文）

## § 8 — Take-aways

**5 句话：**

1. 论文用 LIM 处理大而稀疏的线路网络，用 NAM 处理小而紧耦合的变换器岛，以一个步长的接口延迟换取网络级并行。[pdf:E02]（PDF 物理页 2，Fig. 1）；[pdf:E04]（PDF 物理页 4，Section III-C）
2. fixed-admittance switch model 让 PWM 状态改变时不必重构节点导纳矩阵，只更新历史源。[pdf:E03]（PDF 物理页 3，Eqs. (9)–(14)）
3. 对角 LIM 运算与多个局部 NAM 运算可以并行，关键路径由最大的局部岛而不是全网规模决定。[pdf:E07]（PDF 物理页 7，Figs. 7–8）
4. 在作者的 Kintex-7 案例中，含六个 converter、21 条三相线路的 Microgrid 3 使用 63.1% DSP，并以 380 ns 完成一步；传统 NAM 的 DSP 需求被估计为超过器件容量。[pdf:E08]（PDF 物理页 8，Fig. 11）；[pdf:E10]（PDF 物理页 10，Table II）
5. 精度证据来自两个 1 μs 的 PSCAD 对照工况和一个实时控制扰动工况，足以支持案例结果，但不足以证明所有参数与切换序列都对一步延迟稳健。[pdf:E08]（PDF 物理页 8，Section VI-B）；[pdf:E09]（PDF 物理页 9，Figs. 12–15）

**3 句话：**

1. 这项工作的主要贡献是改变计算依赖图，而不是单纯更换硬件：全局大矩阵被拆成可并行的小 NAM 矩阵和对角 LIM 运算。[pdf:E06]（PDF 物理页 6，Table I）；[pdf:E07]（PDF 物理页 7，Fig. 7）
2. 380 ns 与资源节省来自这种结构，但成立范围受最大局部岛、总资源以及接口延迟稳定性共同约束。[pdf:E07]（PDF 物理页 7，Fig. 8 后正文）；[pdf:E10]（PDF 物理页 10，Table II）
3. 论文证明了“这一组微电网和工况能工作”，还没有证明“任意规模与任意参数都能组合后工作”。[pdf:E11]（PDF 物理页 11，Conclusion）

**1 句话：** 把微电网按物理结构切成局部变换器岛和线路传播网，能把 FPGA EMT 的规模瓶颈从全局求解转成可检查的局部关键路径与接口稳定性问题。

## § 9 — 最脆弱的假设

最脆弱的假设是：LIM–NAM 接口引入的一个 time-step delay，在所有实际开关状态和网络参数下都足够小且不会破坏组合系统稳定性。作者明确承认该延迟，并以“亚微秒步长远快于微电网动态”解释其精度影响很小，同时给出 \(\rho(A_{\mathrm{SYS}})<1\) 的整体判据。[pdf:E04]（PDF 物理页 4，Section III-C）；[pdf:E06]（PDF 物理页 6，Eq. (44)）

它一旦不成立，损失不是误差略大，而是解耦接口可能注入非物理能量，使原本稳定的电路出现数值振荡；此时并行结构本身就不能作为可信实时仿真器。论文提供了 Microgrid 1 的充放电跃变与单相接地故障对照，报告多数时间误差低于 3%，这是支持该假设的直接案例证据。[pdf:E09]（PDF 物理页 9，Figs. 12–13）

仍缺的是对弱电网、低阻尼 LCL、不同线路 \(L/C\)、极端拓扑、不同步长及大量 PWM 状态的系统稳定裕度扫描。更值得警惕的是，论文在实现部分说明 \(\alpha,\beta\) 随 PWM 实时变化，却又把整个网络称为离散 linear time-invariant system；基于证据的推断是，单个开关状态下的谱半径判据未必自动给出任意切换序列下的统一稳定保证。[pdf:E06]（PDF 物理页 6，Section IV-A 与 Eqs. (39)–(44)）这不是说论文结果错误，而是其最关键的外推边界。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 Microgrid 3，而是“解耦延迟是否在增加线路段后仍保持精度和稳定”。可按 PDF 物理页 8 的 Microgrid 1 建一个最小电池 converter–LCL–π line–grid 模型：外网 380 V、60 Hz，源内阻 0.05 Ω 与 38.5 μH；每段线路取 0.05 Ω、38.5 μH、35 nF；LCL 取 0.75 mH、50 μF、0.75 mH。[pdf:E08]（PDF 物理页 8，Fig. 11 与参数段）

实现两条路径：一条是同一步联立的 monolithic NAM reference，另一条是论文的 leap-frog LIM、compact NAM 与一步延迟接口。先用 floating point 排除量化干扰，再加入论文报告的系数矩阵格式 `<±,36,16>` 和电压/电流格式 `<±,25,12>`，并为 1、4、8、16 段 π line 生成综合报告。[pdf:E06]（PDF 物理页 6，Section IV-A）

测量三类量：相对 reference 的电压/电流误差、所有仿真步是否有界以及综合后的 DSP/latency。复现支持条件可设为：充放电跃变和单相接地故障中大多数时间误差不超过论文报告的 3%，没有增长振荡，并且增加线路段不拉长 LIM 对角路径的综合延迟。[pdf:E09]（PDF 物理页 9，Figs. 12–13）；[pdf:E10]（PDF 物理页 10，Table II）若 monolithic NAM 稳定而 LIM–NAM 出现 \(\rho\ge 1\)、持续误差增长，或线路数增加使实际关键路径明显变长，就反驳了核心机制在该配置下的适用性。后两项判据属于本卡提出的可证伪设计，不是论文原文结论。

## § 11 — 最强反例设计

最强反例应主动寻找“物理系统稳定、同一步 NAM 也稳定，但一步延迟接口不稳定”的参数区，而不是只换一个更大案例。构造一个弱电网下的低阻尼 LCL converter 岛，把分区点固定在 LCL 与线路交界；扫描 grid strength、LCL damping、线路 \(L/C\)、\(\Delta t\) 和 PWM switching sequence。对每个点同时运行 monolithic NAM 与 LIM–NAM，并记录接口瞬时功率、能量残差、谱半径与时域误差。论文的接口正是在这里把 NAM network 等效为电压源、把 LIM network 等效为电流源，并明确引入一步延迟。[pdf:E04]（PDF 物理页 4，Fig. 4 与 Section III-C）

真正有杀伤力的结果是找到一片连通参数区域：monolithic NAM 波形收敛且能量有界，LIM–NAM 却出现持续振荡或误差随步数累积；这会把“误差来自模型”这一替代解释排除掉，并直接指向 delayed coupling。再加入一个规模显著大于其他岛的 DG network，可同时攻击“执行时间与规模无关”的说法，因为作者自己的条件是新增 DG 岛不能大于已有局部岛。[pdf:E07]（PDF 物理页 7，Fig. 8 后正文）如果大岛成为新的最长 NAM path，380 ns 常数就不再是网络解耦本身的无条件性质。

## § 12 — Follow-up Research Idea

在 EMT、实时仿真和电力电子领域，高影响工作通常需要同时满足数值可信性、硬件可实现性和对实际 HIL 场景的价值，而不是只给更漂亮的 software benchmark。基于第 9 节，候选方向是做一种**带能量/无源性证书的延迟接口**：不再假设一步延迟天然无害，而让每个 NAM 岛与 LIM 网络在交换等效源时携带局部 energy budget；当接口预测会注入非物理能量时，触发局部 predictor–corrector、wave-variable 变换或受限的子步同步。

- **未满足的需求：** 现有方案用案例误差和谱半径说明稳定，但缺少面对 time-varying switching、弱电网和异构局部岛时可组合的保证；论文自己承认一步接口延迟，并把多 FPGA 与更大系统留作后续计划。[pdf:E04]（PDF 物理页 4，Section III-C）；[pdf:E11]（PDF 物理页 11，Conclusion）
- **潜在研究价值：** 若每个新 DG 岛只需证明自己的端口能量约束，就可能把“整网重新求谱半径”改成 compositional certification，同时保留 FPGA 并行性。这改变的是扩展系统的验证方式，而不只是增加一个算法模块。
- **可借鉴工具：** 可借用实时 co-simulation 的 passivity observer/controller、wave-variable coupling，以及 domain decomposition 中的异步保守接口；这里是方法来源建议，不是声称这些工具尚未用于本问题。
- **首个证伪实验：** 使用第 11 节扫描得到的最坏稳定边界，在相同定点格式和 FPGA 时限下比较原始一步接口与能量约束接口。若新接口仍出现 monolithic NAM 没有的振荡，或 correction 使关键路径超过实时步长，这个想法就失败。
- **与本文的实质区别：** 本文把延迟看作在足够小步长下可忽略的代价，并事后检查整体稳定性；候选方向把接口稳定裕度本身变成运行时或可组合的设计契约。

本卡未为该方向额外检索紧密相关全文，因此它只是由论文证据约束出的候选研究想法，不声称具有 novelty。
