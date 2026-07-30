# Fast Simulation Model of Voltage Source Converters With Arbitrary Topology Using Switch-State Prediction

作者：Shilin Gao；Yankan Song；Ying Chen；Zhitong Yu；Rui Zhang  
出处：IEEE Transactions on Power Electronics, Vol. 37, No. 10, pp. 12167-12181  
年份：2022  
DOI：10.1109/TPEL.2022.3176687  
Zotero key：ZJ8B7MGM  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的是一个很具体的 EMT 仿真瓶颈：在保留 VSC 详细开关行为的前提下，怎样避免传统 EMTP-type 仿真器为了找到可行开关组合而在每个时间步反复求解整个电网。作者把问题放在高比例电力电子系统的背景下：VSC 已广泛进入新能源并网、交直流微网和 HVdc，详细 EMT 仿真又是分析振荡、电压冲击、控制保护和 hardware-in-the-loop 行为的基础；但 VSC 数量增大后，微秒级步长、高维导纳矩阵、频繁 LU 分解和开关状态迭代共同推高计算成本。论文的直接目标不是用平均模型换速度，而是在详细开关模型层面去掉其中的全局状态迭代。[pdf:E01]（PDF 物理页 1，Abstract 与 §I）

工程价值在于把“先解网络、再判断开关、状态不一致就重解”的离散非线性闭环，改造成“先局部预测开关、再一次求解网络”的线性时间步。若这一转换可靠，多 VSC 系统可以继续保留故障、自由续流和开关暂态，同时获得更高吞吐量；这比单纯放大步长更适合需要器件级细节的系统级研究。[pdf:E03]（PDF 物理页 3，§II-B 与 Fig. 1）

## § 2 — 前人工作与不足

论文把既有路线分成几类。state-space/DSED 方法和 DSIM 在电力电子器件级仿真中很高效，但作者指出其系统级使用受限，例如分布参数输电线不易纳入；EMTP-type nodal analysis 更适合系统级 EMT，却承担开关网络反复求解的成本。[pdf:E01]（PDF 物理页 1，§I）

对 EMTP-type 的提速，已有方法各自只消掉部分成本。论文回顾称，averaged-value model 可以用大步长并降低方程维数，但丢失高频开关暂态；switching-function model 能保留部分纹波，却仍需要较小步长，而且这两类模型都不能完整表达 VSC 内部故障与损耗。Thevenin 等值通过消去内部节点降低 MMC 或电力电子变压器的方程规模；associated discrete circuit 让等效导纳保持不变，但参数难选且可能引入不可接受的虚拟损耗。更接近本文的启发式非迭代开关判断已经出现，但论文认为其理论分析不足，难以覆盖复杂拓扑和多变工况。[pdf:E02]（PDF 物理页 2，§I）

因此，本文瞄准的不足不是“以前没人做快速模型”，而是已有快速模型通常牺牲开关细节，或仍未把“全系统迭代求可行开关组合”变成一个可解释、可嵌入、按局部拓扑执行的预测过程。作者的差异化主张是：将常见 VSC 分解成若干 HBC，以 HBC 为判断单元，用状态机做 preliminary prediction，再用导通路径 decision tree 修正 simultaneous switching。[pdf:E02]（PDF 物理页 2，§I Contributions）

## § 3 — 重建作者的思考路径

下面是基于论文问题描述重建的推理链，属于基于证据的合理推断，不是作者逐字给出的研究日志。

1. 详细 EMT 不能轻易退回 AVM，因为故障、自由续流和开关瞬态正是许多分析需要保留的对象；因此应保留开关级等效电路。[pdf:E02]（PDF 物理页 2，§I）
2. 传统流程的关键循环来自相互依赖：导纳矩阵 \(Y(t)\) 取决于开关向量 \(X(t)\)，开关向量又受求解后的节点电压约束；状态改变还会重算电流源，于是必须迭代到 \(X^k(t)=X^{k-1}(t)\)。[pdf:E03]（PDF 物理页 3，Eqs. (2)-(6) 与 Fig. 1）
3. 若把整个 VSC 直接视为一个组合开关问题，状态数会随器件数急剧增长；但常见 VSC 可以按串并联关系拆成两电平 HBC、三电平 T-type HBC 和三电平 NPC HBC，而一个 HBC 的状态主要由本地电容电压、支路电流和 gate signal 决定。[pdf:E04]（PDF 物理页 4，§III-A 与 Fig. 2）
4. 仅逐个器件预测仍可能得到物理上不可行的组合，因为 IGBT 改变会迫使续流二极管同时换相；所以需要先做器件状态机预测，再按正负电流下的主动/被动导通路径执行 simultaneous-switching 修正。[pdf:E05]（PDF 物理页 5，Figs. 4-5 与 §III-C）
5. 一旦每个 HBC 在网络求解前都给出可行状态，就能先组装等效电路和导纳矩阵，再只求解一次节点方程，从源头移除全局开关状态迭代。[pdf:E07]（PDF 物理页 7，§IV-A 与 Fig. 8）

这条路径的核心转折是把“全网离散非线性求解”重写成“局部有限状态预测 + 一次全网线性求解”。它没有减少节点方程本身的物理内容，而是改变了开关状态被确定的时机和空间范围。

## § 4 — 核心 Intuition

一个 VSC 虽然拓扑看起来复杂，但其开关判断可以被拆成若干局部 HBC；在足够小的时间步内，上一时刻的本地电压、电流与当前 gate signal 已经携带了下一状态所需的大部分信息。先用器件状态机得到候选状态，再用 HBC 导通路径的 decision tree 修正 simultaneous switching，就能在求解全网节点电压之前给出可行开关组合。[pdf:E04]（PDF 物理页 4，§III-A-B）[pdf:E06]（PDF 物理页 6，Fig. 6 与 §III-D）于是传统的“求解后检查并反复重算”被替换为“预测后一次求解”。

## § 5 — 具体方法与完整 Pipeline

以三相两电平 VSC 为例，每个桥臂被当成一个 HBC。A、B 相若主动导通，就执行 preliminary prediction 和 simultaneous-switching prediction；C 相若只作无源整流，则只需 preliminary prediction。三个 HBC 分别给出状态后，再形成整个 VSC 的等效电路。[pdf:E06]（PDF 物理页 6，§III-D 与 Fig. 7）

完整 pipeline 如下：

1. **初始化与控制求解。** 设置固定时间步 \(\Delta t\)、仿真终止时间和系统数据，然后在每一步先解控制系统，得到各 IGBT 的 gate signal。[pdf:E07]（PDF 物理页 7，§IV-A，Steps 1-2）
2. **局部 preliminary prediction。** IGBT/diode switch group 用三态表示：state 0 为两者均 OFF，state 1 为 IGBT OFF 且 diode ON，state 2 为 IGBT ON 且 diode OFF。预测函数读取上一时间步的 group state、\(v_{ce}\)、\(i_{ce}\) 和当前 \(G(t)\)；单独二极管则用两态转移。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Eqs. (7)-(8)）[pdf:E05]（PDF 物理页 5，Fig. 4 与 Eqs. (9)-(10)）
3. **simultaneous-switching correction。** 把不同 HBC 统一解释为正向主动路径 PA1/PA2、正向被动路径 PP、负向主动路径 NA1/NA2 和负向被动路径 NP。根据注入电流符号、哪个主动路径刚接通或关断，以及 gate 的互补约束，用三棵 decision tree 把受反压或续流影响的二极管同步改到可行状态。[pdf:E05]（PDF 物理页 5，Fig. 5 与 §III-C）[pdf:E06]（PDF 物理页 6，Fig. 6）
4. **组装网络。** 根据全部 HBC 的最终状态形成 VSC 等效电路，建立 VSC 与其余网络的 nodal admittance matrix，计算 external/history current sources，再求解 \(Y(t)v(t)=i_s(t)+i_h(t)\)。[pdf:E07]（PDF 物理页 7，Fig. 8，Steps 4-7）
5. **更新时间。** 计算支路与 VSC 内部变量以准备下一步的历史源；若未到终止时间，则令 \(t\leftarrow t+\Delta t\) 并回到控制求解。[pdf:E07]（PDF 物理页 7，Steps 8-9）

实现边界必须说清。论文用 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 两值电阻表达开关，示例中 OFF 电阻可取 \(10^8\,\Omega\)；电感、电容在实验中采用线性模型。[pdf:E03]（PDF 物理页 3，Eq. (4) 后正文）[pdf:E08]（PDF 物理页 8，§V）程序以 PSCAD/EMTDC user-defined component 实现，每个 VSC component 内含主电路和预测模块；对象化封装使各 VSC 的预测彼此独立。[pdf:E07]（PDF 物理页 7，§IV-B）

论文**未报告**多速率时间推进、并行调度、浮点位宽或定点量化，也**未报告** FPGA 映射、片上资源、流水线时序、HIL I/O 延迟或真实实时执行。实验平台是桌面 CPU 上的 PSCAD/EMTDC，不是 FPGA；论文只在结论中把 ADC switch model 与 variable-step solver 列为未来方向。[pdf:E12]（PDF 物理页 12，§V-B）[pdf:E13]（PDF 物理页 13，§VI）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文不是收敛定理型工作，数学的作用是暴露传统迭代闭环，并把开关器件规则写成可执行状态转移。

首先，EMTP-type 每步需要解

\[
Y(t)v(t)=i_s(t)+i_h(t),
\]

其中 \(v(t)\) 为节点电压向量，\(Y(t)\) 为等效节点导纳矩阵，\(i_s(t)\) 和 \(i_h(t)\) 分别为 external 与 history current source 向量。[pdf:E02]（PDF 物理页 2，Eq. (1)）有开关时，

\[
Y(t)=f_Y(X(t)),\qquad
X(t)=[x_1(t),x_2(t),\ldots,x_n(t)],\qquad
x_i(t)\in\{0,1\},
\]

并且论文写出 \(X(t)=f_X(v(t))\)、\(i_s(t)=f_I(Y(t))\)。直觉上，网络解依赖开关，开关又依赖网络解；这四个映射组成离散非线性代数闭环，所以传统方法只能迭代到开关向量不再变化。[pdf:E03]（PDF 物理页 3，Eqs. (2)-(6) 与 §II-B）

对 IGBT/diode group，论文用 \(s_i(t)\in\{0,1,2\}\) 表示三种物理状态。Eq. (7) 把 \(s_i(t-\Delta t)\)、\(v_{ce}(t-\Delta t)\)、\(i_{ce}(t-\Delta t)\)、当前 gate \(G(t)\) 和 forward drop \(v_{\mathrm{fvd}}\) 编成分段转移条件；若没有条件触发，状态保持。随后将 group state 映射回网络开关变量：

\[
x_i(t)=
\begin{cases}
1, & s_i(t)=1\ \lor\ s_i(t)=2,\\
0, & s_i(t)=0.
\end{cases}
\]

这里 \(x_i=1\) 表示这个 IGBT/diode 并联支路导通，不要求一定是 IGBT 本身导通。[pdf:E04]（PDF 物理页 4，Eq. (7)-(8) 与 Fig. 3）

单独二极管的转移更简单：

\[
s_i(t)=
\begin{cases}
1, & s_i(t-\Delta t)=0\ \land\ v_{ce}(t-\Delta t)<-v_{\mathrm{fvd}},\\
0, & s_i(t-\Delta t)=1\ \land\ i_{ce}(t-\Delta t)>0,
\end{cases}
\qquad x_i=s_i,
\]

其余情况保持原状态。preliminary prediction 之后再由导通路径 decision tree 处理“一个 IGBT 动作迫使若干 diode 同时动作”的组合约束；这一步不是连续方程推导，而是有限枚举后的规则化修正。[pdf:E05]（PDF 物理页 5，Eqs. (9)-(10) 与 §III-C）

实验误差采用 2-norm cumulative relative error：

\[
\varepsilon(y)=\frac{\lVert y_{\mathrm{ref}}-y\rVert_2}{\lVert y_{\mathrm{ref}}\rVert_2}\times 100\%,
\]

其中 \(y\) 是预测模型解，\(y_{\mathrm{ref}}\) 是 reference solution。[pdf:E09]（PDF 物理页 9，Eq. (11)）这衡量整段波形的总体偏差，但可能掩盖只发生在单个开关瞬间的尖峰，因此还需要看局部波形和逐步状态是否一致。

## § 7 — 实验设计与结论

论文的实验均在 PSCAD/EMTDC 中进行，reference 是用详细 IGBT/diode components 构造并以 \(1\,\mu s\) 步长运行的模型。[pdf:E08]（PDF 物理页 8，§V）

- **问题：三类基础 HBC 在正常、短路、闭锁和纯续流时是否准确？** 实验：两电平、T-type 三电平和 NPC 三电平 HBC 分别经历 healthy、node-to-ground fault 与 IGBT blocking，比较输出电流；Fig. 10 的典型故障/闭锁发生在 \(t=0.02\,s\)。答案：论文报告 proposed 与 reference 波形重合，Table I 的全部 2-norm relative errors 位于 0.00494%-0.0763% 之间，包含接近零电流的纯续流状态。[pdf:E08]（PDF 物理页 8，Figs. 9-10）[pdf:E09]（PDF 物理页 9，Table I）
- **问题：逐 HBC 判断能否覆盖主动桥臂与被动整流桥臂并存？** 实验：三相两电平 VSC 中 A、B 相主动运行，C 相被动运行，比较 \(i_a\)、\(i_c\) 与 \(v_{dc}\)。答案：Fig. 12 中两种方法的电流和电压重合，支持“按三个 HBC 分别判断”的实现路径。[pdf:E09]（PDF 物理页 9，Figs. 11-12）
- **问题：模块化 SST 在正常与故障时是否准确？** 实验：10-module SST 在 \(1\,\mu s\) 下先跑正常工况，再于 \(t=0.1\,s\) 施加 AC-side ground short，并在 \(t=0.12\,s\) 清除，比较 AC current 与 DC voltage。答案：作者称没有 visible error；波形图显示 proposed 与 reference 在正常和故障段基本重合。[pdf:E09]（PDF 物理页 9，Fig. 13 与故障设置）[pdf:E10]（PDF 物理页 10，Figs. 14-17）
- **问题：步长增大后，非迭代预测是否比有限次传统迭代更稳？** 实验：10-module SST 用 \(10\,\mu s\) 步长，在同一故障下比较 proposed、traditional 与 \(1\,\mu s\) reference。答案：故障瞬间 traditional 出现虚拟负电流，论文将其归因于有限迭代未得到可行状态；全段 2-norm errors 分别为 traditional 5.15%、proposed 3.84%。[pdf:E10]（PDF 物理页 10，Fig. 18）[pdf:E11]（PDF 物理页 11，Fig. 19 前后正文）
- **问题：结论能否延伸到更多 converter topology？** 实验：对 Boost、Buck、MMC、10-module SST、dual-active-bridge、单相/三相两电平、T-type 与 NPC converter 统计 capacitor voltage 和 arm current error。答案：Table II 的报告值从 0.00154% 到 0.451%，但这些仍是仿真对仿真，不是硬件测量。[pdf:E11]（PDF 物理页 11，Table II）
- **问题：多 VSC 系统在稳态、负载突变和较大步长下是否工作？** 实验：六 VSC dc microgrid 包含 SST、Buck、Boost、三相两电平、三相 T-type 和三相 NPC converter，各 converter switching frequency 为 10 kHz，并在 \(t=0.5\,s\) 改变 Bus 3 DC load。答案：常规步长下 proposed 与 reference 基本重合；在 \(5\,\mu s\) 下 proposed 仍大体正确但有轻微差异，traditional 因 iteration/interpolation 给出错误结果。[pdf:E11]（PDF 物理页 11，Fig. 20-21 与 dc microgrid 设置）[pdf:E12]（PDF 物理页 12，Figs. 22-23）
- **问题：是否真正节省计算时间？** 实验：在 Intel Core i7-7700K 4.2 GHz、32 GB RAM 桌面机上比较不同模块数和步长。答案：\(1\,\mu s\) 下，80-module SST speedup 约为 2，traditional 每步迭代 1-3 次；\(10\,\mu s\) 下 speedup 超过 6。dc microgrid 在 \(2\,\mu s\) 下由 115.36 s 降至 53.16 s，即 2.17 倍；\(5\,\mu s\) 时 traditional 报 fatal error，proposed 用时 32.98 s。[pdf:E12]（PDF 物理页 12，Fig. 24 与 §V-B）[pdf:E13]（PDF 物理页 13，Fig. 25 与 Table III）

不得外推的范围是：实验没有 FPGA、实时处理器或物理 converter；没有给出多线程/并行 scaling；“arbitrary topology”只通过有限 converter 集合和三种基本 HBC decision tree 支持，并非对所有开关器件和任意耦合拓扑的形式化证明。

## § 8 — Take-aways

**5 句话：**

1. 论文把传统详细 EMT 中最昂贵的全局开关状态迭代，改成求解节点方程之前的局部 switch-state prediction。
2. 它以两电平、T-type 三电平和 NPC 三电平 HBC 为基本单元，先做器件状态机预测，再修正 simultaneous switching。
3. 这一设计保留详细开关模型和故障/续流行为，而不是通过 averaged model 隐去开关。
4. PSCAD/EMTDC 仿真表明，在论文测试的 HBC、VSC、SST 与六 VSC dc microgrid 上，误差较小且速度随模块数和步长增加而更有优势。
5. 最重要的边界是局部历史量必须足以预测下一状态，而且现有 decision tree 只被明确构造和验证于 IGBT-based 的三类 HBC。

**3 句话：**

1. 贡献本质是把一个全网离散非线性迭代问题分解为局部、可枚举的开关状态问题。
2. 速度提升来自消除迭代，不来自并行或 FPGA。
3. 实验支持“这些测试拓扑与工况有效”，但不足以证明标题中的任意拓扑。

**1 句话：**

这是一种用局部开关因果规则换掉全网反复求解的详细 EMT 加速方法，其价值和风险都集中在预测规则能否覆盖真实换相。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在每个时间步开始时，一个 HBC 的上一时刻本地电容电压、支路电流、器件状态与当前 gate signal，足以唯一决定本步的可行开关组合，外部网络不会在该步内引入必须联合求解的状态变化。** 作者给出的物理理由是电感电流与电容电压在小步长内不会突变，且不同 HBC 的开关状态“hardly affected”彼此；这正是从 \(t-\Delta t\) 预测 \(t\) 的基础。[pdf:E04]（PDF 物理页 4，§III-A）

若这个假设失效，预测器会在节点方程求解前锁定错误状态。此时要么得到不可行导通路径和电流尖峰，要么不得不恢复迭代，核心速度贡献随之消失。论文确实用短路、闭锁、被动整流和 \(5/10\,\mu s\) 大步长做了压力测试，但没有给出覆盖所有耦合、所有换相边界和所有器件物理的证明；它还明确说 MOSFET-based converter 需要修改 decision tree。[pdf:E05]（PDF 物理页 5，§III-C3）

因此，“arbitrary topology”应读成受约束的工程扩展性：作者实际构造的是三种 IGBT HBC，并在结论中把外推范围表述为可由 switch group 描述的新 HBC。没有报告 reverse-recovery、寄生参数、dead-time 非理想、饱和器件、跨 HBC 强耦合或硬件测量证据。[pdf:E13]（PDF 物理页 13，§VI）这不是否定方法，而是指出其最关键的适用前提还主要由有限仿真覆盖来支撑。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 dc microgrid，而是“一个 HBC 能否不用全局迭代仍给出与详细模型一致的状态和波形”。

**数据与模型。** 采用 Appendix Table A1 的 single-phase two-level HBC：DC source 1 kV、\(R_{dc}=10\,\Omega\)、\(C=1000\,\mu F\)、IGBT/diode \(R_{\mathrm{on}}=0.005\,\Omega\)、\(R_{\mathrm{off}}=10^8\,\Omega\)、\(L_a=0.02\,H\)、\(R_a=2\,\Omega\)、\(L_s=0.08\,H\)、\(R_s=8\,\Omega\)。[pdf:E13]（PDF 物理页 13，Table A1）

**实现。** 在同一 EMT 求解器中做两份模型：A 使用 Eqs. (7)-(10) 和两电平 HBC decision tree，在网络求解前决定状态；B 使用传统“求解-检查-重组-重解”直到开关向量稳定。两份模型必须共享 gate waveform、初值、器件电阻和线性 L/C companion model，避免把实现差异误当算法差异。

**工况。** 以 \(1\,\mu s\) 为主步长，依次运行 healthy、在 \(t=0.02\,s\) 施加 node-3-to-ground fault、在 \(t=0.02\,s\) block IGBTs 三种场景，并额外扫 \(5\,\mu s\) 与 \(10\,\mu s\) 观察步长敏感性。[pdf:E08]（PDF 物理页 8，Fig. 10 caption 与 §V-A1）

**测量。** 逐时间步记录两种方法的 group state、开关向量、全局迭代次数、输出电流和 wall-clock time；对输出电流计算 Eq. (11)，并单独检查 fault edge 与 current-zero crossing 附近的最大瞬时误差。

**支持/反驳判据。** 若 \(1\,\mu s\) 下三种工况的状态序列除同值事件排序外一致，预测模型不做全局迭代，且累计相对误差不高于论文 Table I 量级的 0.08%，则核心 claim 获得最小支持。若预测模型出现持续一个以上时间步的不可行状态、故障边沿电流方向错误，或为了恢复正确性仍需全局迭代，则核心机制被反驳。这个实验不验证“arbitrary topology”，只验证最小基本单元。

## § 11 — 最强反例设计

最强反例应直接破坏“本地历史量足以先验决定状态”，而不是只换一台更大的 converter。可构造两个共享低阻抗 DC-link/neutral path 的 NPC HBC，使它们在一个电流过零附近同时收到 gate edge；再在同一时间步施加低阻抗 AC fault，使一个 HBC 的换相电压取决于另一个 HBC 在本步内实际选择的续流路径。扫 \(\Delta t\)、dead-time、故障相角和初始电容不平衡，让上一时刻的 \(v_{ce}\) 与 \(i_{ce}\) 对两个候选路径都接近阈值。

ground truth 使用带子步事件定位的 transistor-level 或 complementarity solver，直到所有 diode/IGBT 状态与 KCL/KVL 同时满足；被测方法保持论文的单次 local prediction。攻击指标不是平均波形“看起来接近”，而是：

1. 是否出现 prediction state 与 ground-truth state 不同；
2. 是否存在同一时刻多个 HBC 必须联合决定才能满足 KCL/KVL；
3. 错误是否产生不可行导通组合、虚拟负电流或能量跳变；
4. 恢复正确性是否迫使算法重新引入全局迭代。

论文的 Fig. 18 已显示传统有限迭代在大步长故障瞬间会产生虚拟负电流，这说明换相边界是有辨识力的压力点；反例把同一压力放到 proposed predictor 的局部充分性上。[pdf:E10]（PDF 物理页 10，Fig. 18 与对应正文）如果被测方法在上述联合换相中稳定给出错误状态，而缩小步长或恢复联合求解后错误消失，就能排除“只是连续积分误差”的替代解释，并直接挑战核心机制。

## § 12 — Follow-up Research Idea

在电力电子与 EMT 仿真领域，高影响工作通常需要同时展示数值正确性、故障与边界工况鲁棒性、跨拓扑可实现性，以及可重复的计算或实时收益。基于第 9 节的局限，一个非增量候选方向是：**把“为每种 HBC 手写确定性 decision tree”改写为“带可行性证书的混合事件求解”**。这是候选研究想法；本卡没有联网检索紧密相关工作，因此不声称 novelty。

**(a) 未满足需求。** 现有 predictor 在确定状态时没有同时输出“这个局部决定在当前网络条件下仍然唯一且可行”的证书。需要一种机制在大多数普通步中保留局部单次预测的速度，在电流过零、故障突变或跨 HBC 强耦合时又能识别不确定性，而不是静默给出错误状态。

**(b) 研究价值。** 问题目标从“预测一个状态”变为“证明本步可安全跳过全局迭代，或精确定位必须联合求解的最小子网”。若成功，它可把标题中的 arbitrary topology 从经验外推推进到可检查的适用条件，并为 CPU、GPU 或 FPGA 实现提供明确的 fast path 与 fallback path。

**(c) 相邻领域工具。** 可借鉴 hybrid systems 的 guard/event localization、complementarity formulation、interval arithmetic，以及 SAT/SMT 中的局部冲突证书。每个 converter component 输出候选状态和一个关于端口电压/电流的有效区间；网络层先检查区间与 KCL/KVL 是否相容，仅对证书失败的局部耦合簇做子步或联合离散求解。

**(d) 首个证伪实验。** 使用第 11 节的双 NPC HBC 联合换相 stress suite，与论文 predictor、全局迭代 EMTP 和事件定位 ground truth 比较。若证书漏掉任何错误状态，或在常规工况中频繁失败到使速度退化为全局迭代，则该想法首先被证伪。

**(e) 实质区别。** 论文方法的主要知识载体是三类 HBC 的确定性状态机和 decision tree；候选方法的主要知识载体是“局部状态决定何时有效”的可验证条件。它不是再加一种拓扑规则，而是改变求解器与 converter model 的接口：converter 不只返回 state，还返回该 state 的可信域和失败原因。
