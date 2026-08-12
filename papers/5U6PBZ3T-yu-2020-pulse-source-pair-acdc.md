# A Pulse-Source-Pair-Based AC/DC Interactive Simulation Approach for Multiple-VSC Grids

作者：Siqi Yu、Shuqing Zhang、Yingduo Han、Yingdong Wei、Sheng Zou  
出处：IEEE Transactions on Power Delivery，Vol. 36，No. 2，pp. 508–521  
年份：2020（online publication；卷期发表于 2021 年 4 月）  
DOI：10.1109/TPWRD.2020.2984275  
Zotero key：5U6PBZ3T  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是“怎样把单个 VSC 算出来”，而是“当同一电网里有许多频繁开关的 VSC 时，怎样仍以 EMT 细节运行仿真，又不让每个开关动作都触发昂贵的网络矩阵重构和 LU 分解”。传统 EMTP 把 IGBT/diode 组合近似成随开关状态改变阻值的二值电阻；一个三相两电平 VSC 对应 6 个开关支路，多个 VSC 会让某些仿真步的计算量突然上升，直接威胁 HIL 所需的确定步时。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

论文的核心 claim 是：把 VSC 的开关部分改写成 AC 侧受控脉冲电压源与 DC 侧受控脉冲电流源组成的 source pair，再按一个时间步内的单向 AC→DC 顺序求解，可以在保留详细开关事件的同时让电网系数矩阵保持不变。[pdf:E03]（PDF 物理页 2，Fig. 2 与 Eq. (1)–(3)）这项工作的价值因此很具体：若矩阵分解能预先完成并反复复用，多 VSC EMT 仿真的成本就从“开关一动便改矩阵”转成“更新右端源项并求解”，为更大的多变流器系统和实时仿真争取计算余量。[pdf:E09]（PDF 物理页 5，Eq. (18)–(22) 及相邻正文）

## § 2 — 前人工作与不足

论文把既有路线分成三类。第一类 Associated Discrete Circuit 让开关 ON/OFF 时的计算电阻相同，用注入电流表达状态改变，从而避免改矩阵；但本文所述的限制是需要“小于数微秒”的步长、参数设计受限，并可能引入高频振荡与人工功耗。[pdf:E01]（PDF 物理页 1，Introduction A）第二类 average-value model 省掉开关动作，计算便宜，却丢失 switching-frequency-dependent 的纹波；本文进一步概括，已有修正模型要么只适用于 DC-DC，要么只能用近似正弦纹波表达，要么结构复杂且误差仍明显，因此不足以支撑故障分析和高精度 HIL。[pdf:E02]（PDF 物理页 2，Introduction B 与本文贡献段）第三类依靠长传输线传播延时做 network partitioning，可让子网并行并支持 multi-rate；在中低压网或 microgrid 的短线路里，这个物理解耦条件往往迫使步长小到约 1 μs 以下，人工切分又会引入接口和数值稳定性风险。[pdf:E02]（PDF 物理页 2，Introduction C）

以上属于“相关文献事实（仅按本文的综述转述）”，并不是本卡对 [11]–[25] 原文的独立复核。本文改变的关键假设是：VSC 不必作为会改变网络拓扑的二值电阻支路进入系数矩阵；只要端口上的电压—电流瞬时约束能由 source pair 表达，开关状态就可以只改变源值。[pdf:E03]（PDF 物理页 2，Fig. 2 与 Eq. (2)–(3)）

## § 3 — 重建作者的思考路径

下面是基于证据的思考路径重建，而不是作者逐字陈述。

1. 先定位真正的时间开销：传统节点方程的形式本身并不慢，慢的是二值开关电阻改变后，节点电导矩阵必须修改并重新做 LU 分解。[pdf:E08]（PDF 物理页 5，Eq. (16)–(17) 及其后正文）
2. 再寻找不进入系数矩阵的等价物：由 superposition 可把 VSC 的 AC 端口写成受控电压源、DC 端口写成受控电流源，开关状态只改变源值，不改变被动网络拓扑。[pdf:E03]（PDF 物理页 2，Fig. 2 与 Eq. (2)–(3)）
3. 接着解决 AC/DC 代数环：数字控制本来就与网络分开求解，控制量进入网络存在一个仿真步延迟；本文据此使用上一时刻的 gate signal。[pdf:E04]（PDF 物理页 3，Section II.B 与 Eq. (4)–(5)）如果 DC 电容使端电压在一个小步长内变化很小，还可以用上一时刻 DC 电压先算 AC 电流，再回算当前 DC 电压。[pdf:E05]（PDF 物理页 3，Fig. 3 与 Eq. (7)–(13)）
4. 最后把单个最小回路推广为多 VSC 网络：预先求出 AC、DC 子网电导矩阵的逆或等价分解，按 AC 电压→AC 支路电流→VSC DC 注入→DC 电压的顺序推进；只有精度不足时才做可选迭代。[pdf:E10]（PDF 物理页 6，Fig. 6 与 Eq. (23)–(24)）

这条路径的要点不是“用一个更快的开关模型”，而是把开关引起的结构变化改写成端口源值变化，再用一个有明确误差来源的时间错位解除 AC/DC 同步耦合。

## § 4 — 核心 Intuition

论文事实：VSC 的开关网络可以在 AC 侧表现为由 DC 电压和 gate signal 决定的脉冲电压源，在 DC 侧表现为由 AC 电流和 gate signal 决定的脉冲电流源。[pdf:E03]（PDF 物理页 2，Eq. (2)–(3)）基于证据的直观解释是：把“开关改变电路结构”换成“开关改变端口注入”，便能让大网络的骨架固定下来。再把上一时刻 DC 电压用于当前 AC 求解，AC 与 DC 子网就能在一个时间步内单向传递而不是同时联立。[pdf:E07]（PDF 物理页 4，Eq. (15) 与 Section II.E）它奏效的前提是步长足够小，使这一个时间步的错位既不遗漏开关事件，也不让 DC 电压变化累积成显著误差。

## § 5 — 具体方法与完整 Pipeline

以包含 $k$ 个三相 VSC 的 AC/DC 网为例，单个时间步的输入包括上一时刻的 gate signal $S_{pj}(t-\Delta t)$、各储能元件的 history source、上一时刻 VSC DC 电压，以及当前外部激励；被动 AC、DC 网络的电导矩阵在开关仿真期间保持不变。[pdf:E08]（PDF 物理页 5，Table II 与 Eq. (16)–(17)）完整 pipeline 如下。

1. 对每个 VSC，用上一时刻的 gate signal 与 DC 电压形成三相受控电压源 $v^0_{pj}(t)$，把它们并入 AC 网络的已知电压边界。[pdf:E09]（PDF 物理页 5，Eq. (18)）
2. 复用预先分解的 $G_{AAac}$ 求当前 AC 未知节点电压，再由支路导纳和 history source 得到所有 AC 支路电流，包括各 VSC 的三相电流。[pdf:E09]（PDF 物理页 5，Eq. (19)–(21)）
3. 用 gate signal 对三相电流按上下桥臂导通状态加权，得到每个 VSC 注入 DC 网络的两个受控电流源 $I^0_{pdc1},I^0_{pdc2}$。[pdf:E09]（PDF 物理页 5，Eq. (22)）
4. 把这些电流源放入 DC 网络右端项，复用 $G_{AAdc}$ 的分解求 DC 节点电压与支路电流；新的 VSC DC 电压从该解中直接取出，作为下一时间步状态。[pdf:E10]（PDF 物理页 6，Fig. 6 与 Eq. (23)–(24)）
5. 若预设精度要求未满足，可把刚得到的 DC 电压重新送回 AC 侧，依次更新 AC 电压源、AC 节点电压、DC 电流源和 DC 节点电压，重复 Eq. (25)–(32)；论文将这一 correction 明确设为可选。[pdf:E11]（PDF 物理页 6，Section III.C 与 Eq. (25)–(32)）

开关/事件处理方面，方法保留离散 gate signal，但开关不再直接改变网络矩阵。时间推进方面，正文实验通常使用固定 10 μs 步长；论文只提出 decoupling 对 parallel solution 与 multi-rate hybrid simulation 有潜力，没有实现或评测真正的多速率调度。[pdf:E17]（PDF 物理页 10，Conclusion）Appendix B 给出 Droop、PQ 与 DC-voltage 三类控制框图和参数，但数值表示、FPGA 映射、片上存储、通信拓扑、WCET 和真实实时平台均未报告。[pdf:E19]（PDF 物理页 12，Fig. 19）验证在 Matlab/Simulink 中以自定义函数与模块完成，因此不能把本文的“适合 HIL”外推成已完成 FPGA 或实时硬件实现。[pdf:E12]（PDF 物理页 7，Section IV 开头与 Table III）Appendix A 只说明同一 source-pair 思路还能写成无 DC 中点的三相 VSC 和单相 VSC 形式。[pdf:E18]（PDF 物理页 11，Fig. 17–18 与 Eq. (33)–(36)）

## § 6 — 核心数学推导（无形式化数学则跳过）

先看 source pair 的物理含义。对有 DC 中点的两电平 VSC，$S_j\in\{0,1\}$，

\[
v_j(t)=S_j(t)u_{C1}(t)-\bar S_j(t)u_{C2}(t),
\]

\[
I_{dc1}(t)=\sum_{j=a,b,c}S_j(t)i_j(t),\qquad
I_{dc2}(t)=\sum_{j=a,b,c}\bar S_j(t)i_j(t).
\]

也就是说，AC 端电压由“哪只桥臂导通”和两侧 DC 电容电压决定；同一开关函数又把 AC 相电流分配为 DC 端注入。忽略 switching loss 后，这组瞬时约束就是 Fig. 2 中受控电压源—电流源等效的依据。[pdf:E03]（PDF 物理页 2，Eq. (1)–(3)）

控制与网络分步求解使 gate signal 带一个时间步延迟，故 $S_j(t)$ 被替换成 $S_j(t-\Delta t)$。论文引用既有 EMTP/TACS 文献并陈述：当步长小于 50 μs 时，该控制接口延迟可忽略；这是本文采用的背景条件，不是本文重新证明的普适界限。[pdf:E04]（PDF 物理页 3，Section II.B 与 Eq. (4)–(5)）

真正解除 AC/DC 代数环的是对 DC 电压再延迟一步。传统隐式梯形法会先联立求出当前 $u_C(t)$，再算 $i_L(t)$；本文改成

\[
i_L(t)=\frac{u_C(t-\Delta t)+\frac{2L}{\Delta t}i_{L,\mathrm{hist}}}{R+\frac{2L}{\Delta t}},
\]

然后把得到的 $i_L(t)$ 放进 DC 侧

\[
\left(\frac{1}{r}+\frac{2C}{\Delta t}\right)u_C(t)
=\frac{u_{dc}}{r}-i_{C,\mathrm{hist}}-i_L(t).
\]

前一式只读旧 DC 电压即可给出当前 AC 电流，后一式再用该电流更新当前 DC 电压，于是形成单向求解链。[pdf:E05]（PDF 物理页 3，Fig. 3、Eq. (11)–(13)）推广到 VSC 端口，就得到 Eq. (15)：当前 AC 脉冲电压完全由上一时刻 gate signal 与上一时刻两侧 DC 电压决定。[pdf:E07]（PDF 物理页 4，Eq. (15)）

论文用传统联立解 $u_C^*,i_L^*$ 作为基准，定义 $ERR_U=(u_C-u_C^*)/u_C^*$、$ERR_I=(i_L-i_L^*)/i_L^*$。在 Table I 给定的参数范围、10 μs 步长下，扫描到的最大绝对电压与电流相对误差分别为 $2.50\times10^{-5}$ 和 $2.38\times10^{-4}$；Fig. 5 显示最大电压误差和电流误差分别近似随步长三次方、二次方增长，若要求低于 $10^{-3}$，作者建议步长小于 20 μs。[pdf:E06]（PDF 物理页 4，Table I、Fig. 4 与 Eq. (14)）[pdf:E07]（PDF 物理页 4，Fig. 5）这只是最小 RL-C 回路的解析/数值误差估计，不自动等于完整多 VSC 系统的全局误差界。

网络层的数学收益来自固定矩阵。传统网络写成 $G_{AA}v_A=i_E-i_{hist}-G_{AB}v_B$，开关作为二值电阻时会改变 $G_{AA},G_{AB}$；source pair 则只进入边界电压和注入电流，使 $G^{-1}_{AAac}$、$G^{-1}_{AAdc}$ 或相应分解可以预先计算并复用。[pdf:E08]（PDF 物理页 5，Eq. (16)–(17)）[pdf:E09]（PDF 物理页 5，Eq. (18)–(22)）

## § 7 — 实验设计与结论

**问题一：一个时间步的单向解耦本身会引入多大误差？** 论文在最小 RL-C 回路上扫描 $R=0.01\sim100\ \Omega$、$L=0.1\sim10\ \mathrm{mH}$，并在 10 μs 步长下与传统联立解比较。答案是最坏扫描点的电压、电流相对误差绝对值分别达到 $2.50\times10^{-5}$、$2.38\times10^{-4}$，且误差随步长增大而快速上升。[pdf:E06]（PDF 物理页 4，Table I、Fig. 4、Eq. (14)）

**问题二：不同 AC/DC 连接关系、控制方式与故障下，波形能否跟随详细 switching reference？** Cases 1–5 覆盖两个 VSC 仅 AC 耦合、AC/DC 同时耦合、仅 DC 耦合三类结构，控制包括 Droop、PQ 与 DC-voltage control，故障包括三相、单相和 DC bipolar short circuit；这些 case 均以 10 μs 步长运行 proposed method，且不使用 iterative correction。[pdf:E12]（PDF 物理页 7，Fig. 7、Table III 与 Section IV.A）论文报告 proposed waveform 与 detailed EMTP reference 高度重合，并且在 1° carrier 不同步的 Case 4 中捕捉到 AC 电流 DC offset 与 subsynchronous oscillation，而 average model 只保留 sinusoidal component；Case 5 的 DC bipolar fault 下，average model 对 AC/DC 变量出现明显误差。[pdf:E13]（PDF 物理页 8，Fig. 9–11 及 Cases 4–5 正文）这些是作者基于波形的结论，论文没有为 Cases 1–5 给出统一的数值误差指标。

**问题三：规模扩大到配电网时是否仍准确？** Case 6 以 IEEE 123 Node Test Feeder 为基础，接入 5 台 CERTS Droop VSC，总负荷为 3490 kW + 1920 kVar；在节点 150 施加 $0.01\ \Omega$ 三相短路，$t=0$ 发生、$t=0.1\ \mathrm{s}$ 清除，仿真步长仍为 10 μs且不做 iteration。[pdf:E14]（PDF 物理页 9，Fig. 13 与 Case 6 设置）作者以 Fig. 14–15 的 AC 电压、电流和 DC 电压波形重合支持“多 VSC 大系统仍保持高精度”，但图中没有汇总误差统计。[pdf:E15]（PDF 物理页 9，Fig. 14–15）

**问题四：固定矩阵是否真的带来效率收益？** 对 1 s 仿真、10 μs 步长，Table IV 报告：2 kHz/5 VSC 时，EMTP 483 s、proposed 231 s，speed-up 2.09；5 kHz/5 VSC 时为 761 s 对 234 s，speed-up 3.25；5 kHz/10 VSC 时为 1603 s 对 327 s，speed-up 4.90。[pdf:E15]（PDF 物理页 9，Table IV 与 Section V.A）从 2 kHz 升到 5 kHz，proposed elapsed time 几乎不变，而 EMTP 增加 57.6%，作者把这一趋势归因于前者不再随开关事件更新矩阵。[pdf:E16]（PDF 物理页 10，Section V.A）论文未报告处理器、线程、内存、实时 target 或分步耗时，因此这些 elapsed time 不能外推为跨平台性能或硬实时 WCET。

**问题五：把步长放大后，iteration 能否补回丢失精度？** 作者把 Case 1 步长从 10 μs 改为 50 μs。答案分成两部分：一轮 iteration 可明显修正 AC 基波电流；但 50 μs 网格会遗漏两个约位于 $t=0.32082\ \mathrm{s}$ 与 $0.32098\ \mathrm{s}$ 的 DC 电压凹陷，也会损失 harmonic component，这些由步内开关事件缺失造成的问题不能靠 iteration 恢复。[pdf:E16]（PDF 物理页 10，Fig. 16 与 Section V.B）

## § 8 — Take-aways

**5 句话：**

1. 这篇论文把多 VSC EMT 的主要开销定位为开关状态变化触发的网络矩阵重构与 LU 分解。[pdf:E01]（PDF 物理页 1，Introduction）
2. Pulse voltage-current source pair 把开关影响移到端口源值，使 AC、DC 被动网络矩阵在仿真中保持不变。[pdf:E03]（PDF 物理页 2，Fig. 2 与 Eq. (2)–(3)）
3. 用上一时刻 gate signal 和 DC 电压先算 AC、再回算 DC，形成可选迭代的单向 loose coupling。[pdf:E07]（PDF 物理页 4，Eq. (15)）[pdf:E10]（PDF 物理页 6，Fig. 6）
4. 在论文的 10 μs Matlab/Simulink cases 中，proposed waveform 与 detailed EMTP reference 接近，并保留 average model 丢失的 switching-related 现象。[pdf:E12]（PDF 物理页 7，实验设置）[pdf:E13]（PDF 物理页 8，Cases 1–5）
5. 最大规模效率表给出 5 kHz、10 VSC 条件下 4.90 倍 speed-up，但 50 μs 实验也清楚显示：错过步内开关事件后，iteration 无法恢复全部纹波与谐波。[pdf:E15]（PDF 物理页 9，Table IV）[pdf:E16]（PDF 物理页 10，Fig. 16）

**3 句话：**

1. 方法的真正创新点不是删掉开关，而是把开关从矩阵结构中移到受控源的右端项。[pdf:E03]（PDF 物理页 2，Fig. 2）
2. 它以一个小时间错位换取 AC/DC 解耦，论文的 10 μs 结果支持这种交换在所测 cases 中有效。[pdf:E06]（PDF 物理页 4，error estimation）[pdf:E12]（PDF 物理页 7，cases 设置）
3. 它为 parallel/multi-rate 与硬件化提供了结构机会，但本文只验证 Matlab/Simulink 算法，未给出 FPGA 或实时平台证据。[pdf:E17]（PDF 物理页 10，Conclusion）

**1 句话：** 这是一种用“事件改变源、而不是改变矩阵”换取多 VSC EMT 加速的方法，其精度上限最终受时间网格能否看见开关事件约束。[pdf:E16]（PDF 物理页 10，Fig. 16 与讨论）

## § 9 — 最脆弱的假设

失败代价最大的假设是：仿真时间网格足够细，使 $S_j(t-\Delta t)$ 与 $u_C(t-\Delta t)$ 既能代表当前端口源，又不会漏掉一个步长内部的关键开关变化。论文对“DC 电压一个小步内变化慢”给了最小回路误差扫描，并建议若相对误差需低于 $10^{-3}$，步长应小于 20 μs；10 μs cases 也给出波形一致的正面证据。[pdf:E06]（PDF 物理页 4，Fig. 4 与 Eq. (14)）[pdf:E07]（PDF 物理页 4，Fig. 5 与 Eq. (15)）

但这不是对任意 PWM 频率、故障陡度、DC 电容、控制延迟或异步载波的统一保证。论文自己的 50 μs Case 1 已出现步内开关事件丢失：DC voltage ripple 的两个凹陷和部分 harmonic component 消失，且 iteration 只能改善已采样状态之间的耦合误差，不能重建从未进入时间网格的事件。[pdf:E16]（PDF 物理页 10，Fig. 16 与 Section V.B）因此，一旦开关边沿密度或 DC 电压变化速度让“一步延迟近似”失效，方法仍可保持矩阵固定，却可能失去其“无精度损失”的核心价值。

## § 10 — 最小复现实验

一周内最值得做的是“固定矩阵是否同时保留事件与加速”的缩小版复现，而不是重建全部 123 节点系统。

- **数据与模型：** 复用 Appendix B 的 4160 V 基准、0.5 MVA VSC、2000 Hz switching frequency、0.3 mH/0.1 mF AC filter、500 V DC source 与 1 mF DC capacitor 参数，搭建 Fig. 7(a) 的双 VSC 微网；控制只实现一种 Droop 配置，设置一次负荷跃变和一次三相短路。[pdf:E12]（PDF 物理页 7，Fig. 7 与 Table III）[pdf:E20]（PDF 物理页 13，Table V）
- **两条实现：** A 路用二值电阻开关并在状态改变时更新/分解矩阵；B 路实现 Eq. (18)–(24) 的 pulse-source-pair 单向求解，不做 iteration。[pdf:E09]（PDF 物理页 5，Eq. (18)–(22)）[pdf:E10]（PDF 物理页 6，Eq. (23)–(24)）
- **测量：** 在同一台机器、同一 solver 和 10 μs 步长下记录 AC 相电压/电流、DC 电压、每步耗时分布、矩阵分解次数；再把 switching frequency 从 2 kHz 改到 5 kHz，观察 B 路耗时是否基本不随开关频率增加。[pdf:E15]（PDF 物理页 9，Table IV）
- **预注册判据（候选复现标准，不是论文原有阈值）：** 若 B 路主要波形的归一化最大误差不超过 $10^{-3}$，且矩阵分解次数不随开关数增长、总耗时低于 A 路，则支持核心 claim；若 B 路在 10 μs 已系统性漏边沿、误差越过阈值，或其耗时仍随 switching frequency 近似线性增长，则反驳核心 claim。选 $10^{-3}$ 只是借用论文误差分析采用的数量级，复现报告必须同时给出原始波形和误差定义。[pdf:E06]（PDF 物理页 4，Fig. 5）

## § 11 — 最强反例设计

最强攻击不是再做一个普通故障，而是把论文分开测试的两种压力合并：使用不同步载波，使两台 VSC 的开关边沿在一个 20–50 μs 时间步内交错；同时减小 DC capacitance 或施加快速 DC fault，让 $u_C$ 在一个步内不再近似常量。Case 4 已表明 carrier phase 差会产生 average model 看不到的 DC offset 与 subsynchronous component，说明边沿相对时序确实会改变可观测波形。[pdf:E13]（PDF 物理页 8，Fig. 11 与 Case 4 正文）Fig. 16 又直接表明 50 μs 网格会遗漏 DC voltage ditch 与 harmonic component，而且 iteration 无法恢复缺失事件。[pdf:E16]（PDF 物理页 10，Fig. 16 与 Section V.B）

基于证据的反例设计是：以 1 μs detailed-switch EMTP 作为 reference，对同一组交错边沿分别运行 proposed 10、20、50 μs，并在每个步长下比较 0、1、多轮 iteration；扫描 carrier phase 与 DC capacitance，记录事件漏计数、AC harmonic spectrum、DC ripple 极值和时域误差。如果增加 iteration 只能改善基波，而误差主要由“边沿落在步内的相位”决定，便能排除“只是 AC/DC 耦合未收敛”这一替代解释，指出 fixed-matrix 机制并不等价于 event-faithful。若 proposed 10–20 μs 在全部交错边沿和快速 DC 变化下仍与 1 μs reference 一致，则这个反例失败，反而强化论文 claim。

## § 12 — Follow-up Research Bet

**主 idea（候选判断，不声称 novelty 已闭合）：把 pulse-source pair 从“每个固定步采一次的源值”改成“带精确时间戳的开关事件流”，构造 event-exact、异步 multi-rate 的 AC/DC EMT 求解与 FPGA 通信体系。** 新的研究问题是：能否让各 VSC controller 只发出压缩的 $S_j$ 边沿时间和对应 source-pair 更新，由 AC、DC 子网各自按合适步长积分，却在事件时刻精确更新端口源，从而第一次同时获得固定网络矩阵、步内 switching-event 保真和跨子网异步推进？

核心因果链是：controller 产生带时间戳的 gate transition → transition 只更新受控电压/电流源，不改变 $G_{AAac},G_{AAdc}$ → 每个 AC/DC solver 在相邻事件之间复用同一矩阵分解 → 事件队列把不同 VSC 的边沿按时间合并并向相关子网广播 → FPGA 上的矩阵求解流水线连续运行，通信只承载稀疏 source update，而不是拓扑或整矩阵。它同时改变了时间表示（固定采样值变为 event-time object）、数据生成方式（controller 输出边沿流）、可控变量（各子网步长与事件批处理粒度）、硬件映射和系统边界。

论文特异依据有两组。方法侧，Eq. (15) 已把当前 AC 源写成上一时刻 gate signal 与 DC 电压的代数函数，Fig. 6 又显示 AC/DC 子网只通过 source pair 交换量，说明固定矩阵与端口事件在结构上可分离。[pdf:E07]（PDF 物理页 4，Eq. (15)）[pdf:E10]（PDF 物理页 6，Fig. 6）实验侧，Fig. 16 明确暴露固定步长的失败不是 iteration 不够，而是步内 switching event 根本没有被采到；Conclusion 同时把 parallel solution 与 multi-rate hybrid simulation 列为尚待探索的方向。[pdf:E16]（PDF 物理页 10，Fig. 16）[pdf:E17]（PDF 物理页 10，Conclusion）

最大研究收益是把“高 switching frequency 必须缩小全网步长”改成“只有事件相关端口需要精确时刻更新”，使多 FPGA 分区的计算与通信都围绕稀疏事件组织。最大的科学风险是 source pair 的电压与电流互相依赖：异步事件到达后，若跨 AC/DC 子网的状态时间戳不一致，所谓 event-exact 可能只是 gate signal 精确，而端口能量交换仍有不可忽略的时序误差。首个区分实验应复用 §11 的交错载波 case，对比三条路线：1 μs detailed-switch reference、50 μs 固定步 proposed、50 μs base step 加精确边沿事件；若第三条在不缩小全网 base step 的情况下恢复两个 DC voltage ditch 与 harmonic spectrum，而仅增加 iteration 不能恢复，就支持“事件时间表示”而非“更多耦合迭代”是关键机制。[pdf:E16]（PDF 物理页 10，Fig. 16）

与本文归纳的 ADC、average model 和 transmission-line/manual partitioning 相比，这个 bet 不通过等值开关电阻、平均掉开关，也不要求用物理线路传播延时制造子网边界；与本文自身方法相比，它把固定步采样的 $S_j(t-\Delta t)$ 改成显式 event-time representation，并把评价对象从单机 elapsed time 改成“事件保真—异步步长—跨 FPGA 通信量”的联合尺度。由于本任务没有补做全文相关工作检索，这一比较只在本文给出的 prior-work 范围内成立，不能据此宣称全球 novelty。

**Wild-card alternative：** 采用不同机制，把两电平 VSC 的单一 source pair 推广为 MMC 臂内“电荷包 source tuple”，用子模块插入集合与臂电容电荷分布作为状态表示，研究能否在不逐个展开子模块开关的条件下仍生成可组合的 AC/DC 端口脉冲；Appendix A 展示的跨拓扑 source-pair 改写只提供起点，这一方向同样是未做相关工作闭合的候选判断。[pdf:E18]（PDF 物理页 11，Appendix A）
