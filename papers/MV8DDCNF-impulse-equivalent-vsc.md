# An Impulse Equivalent VSC Model for Large Power Grids Containing Multiple Converters

作者：Jiaqi Ma、Qihang Wang、Shuqing Zhang  
出处：2024 1st International Conference on Smart Grids and Power Systems；*Journal of Physics: Conference Series* 2774 (2024) 012037  
年份：2024  
DOI：10.1088/1742-6596/2774/1/012037  
Zotero key：MV8DDCNF  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样把每个开关沿算得更细”，而是相反的问题：当一个大电网接入多个高频开关 VSC 时，能否不跟踪全部开关瞬间，仍保留对系统级 EMT 暂态有用的变流器响应。作者给出的工程背景是，VSC 开关频率通常为 1–10 kHz；详细开关模型若要保住开关谐波，需要缩小步长或在步内迭代定位开关时刻，两者都会增加计算量，而大量开关器件使这一负担更突出。作者据此把目标放在忽略高频开关谐波、放大仿真步长的 averaged model 上。[pdf:E01]（PDF 物理页 2，Abstract 与 Section 1）

真正的难点是：平均化不能只保证稳态基波正确。拓扑突变后，电感电流不能突变，但节点电压会按网络约束瞬时重分配；作者认为普通 AC 电压源式 averaged model 通过类似插值的方式给出节点电压，不能保证重建这个第一阶段的真实电压重分配。[pdf:E02]（PDF 物理页 4，Eq. (6)–(11) 前后正文）因此论文试图用“脉冲面积等效 + Dommel 离散端口 + 跨周期修正”在效率与暂态保真之间取得折中，而不是恢复器件级开关波形。

## § 2 — 前人工作与不足

论文列出的第一类基线是二值电阻表示的 ideal switch 详细模型。它能显式反映开关状态和谐波，但准确定位开关时刻要求微秒级步长或步内插值迭代，面对大量器件时计算代价高。[pdf:E01]（PDF 物理页 2，Section 1）第二类是 converter averaged model：把开关函数的离散拓扑状态换成 duty cycle。论文先写出一般开关系统，再将开关向量中的各项用对应占空比替代；这降低了拓扑切换频率，却天然丢掉脉冲在窗口内部的时间分布。[pdf:E03]（PDF 物理页 5，Eq. (12)–(16)）

作者还点名 Energy Equivalence Averaged Model（EE-AVM）：它以短时间内两侧传递能量相同为出发点。论文给出的批评是，步长稍大时用滞后电路参数计算功率，会破坏 small-ripple assumption，使结果不可接受，因而大步长模型必须加入修正。[pdf:E04]（PDF 物理页 6，Section 3.2 起始段）论文参考文献中还列出 “Pulse-Source-Pair-Based AC/DC Interactive Simulation Approach for Multiple-VSC Grids”，但正文没有给出足够方法细节或同工况定量对比，不能据此判断本文相对它的精确增量。

## § 3 — 重建作者的思考路径

可以把作者的思路重建为四步。第一，详细开关模型的主要成本来自高频拓扑切换，而电网关注的频带通常低于器件开关瞬态，所以需要把一个载波周期内的许多开关动作压缩为较慢的端口行为。[pdf:E01]（PDF 物理页 2，Section 1）第二，简单连续 AC 源会漏掉拓扑突变时的节点电压重分配，因此压缩后的对象仍应以网络可求解的电压—电流端口进入 EMT 方程，而不只是给定一条理想波形。[pdf:E02]（PDF 物理页 4，Eq. (6)–(11) 前后正文）

第三，采样控制中的 equal-area criterion 提供压缩依据：若开关周期足够短，经过惯性环节的两个窄电压脉冲只要面积相同，其响应大体等效，即 \(v_1T_1=v_2T_2\)。[pdf:E03]（PDF 物理页 5，Eq. (15)）这不是 Dirac impulse，也不是对任意网络的精确等效；它是以“负载在开关周期内主要感受到脉冲面积”为前提的低频近似。第四，把该近似先写成 AC/DC 耦合的 VSC state-space，再用 trapezoidal integration 整理成 Dommel 端口形式；闭环下未来调制量未知，就从载波交点求 duty、由历史值外推窗口末调制量，再在同一步内修正。[pdf:E05][pdf:E04][pdf:E06][pdf:E07]（PDF 物理页 6，Eq. (20)–(28)；物理页 7，Eq. (29)–(33)）

## § 4 — 核心 Intuition

一个高频 PWM 周期内，不再逐个保留“开关何时开、何时关”，而只保留脉冲对慢电磁状态产生的总作用，并把它写成可接入 EMT 网络的电压—电流端口。为了避免大步长把闭环 duty cycle 错后一拍，模型用历史调制信号预测窗口末值，再利用本步网络解迭代修正。它换来的是真正的降维，而不是开关网络的精确 Schur 消元，也不是天然固定导纳或无迭代闭合。

## § 5 — 具体方法与完整 Pipeline

以论文的三相两电平 VSC 为例，完整 pipeline 是：

1. **从开关状态到调制函数。** 每相上桥臂导通记 \(s_k=1\)，下桥臂导通记 \(s_k=0\)；平衡三相条件下定义 \(m_k=s_k-\frac13\sum s_k\)，交流相电压由 \(U_{dc}m_k\) 进入支路方程，直流电流由三相 \(m_ki_k\) 汇总。[pdf:E03][pdf:E05]（PDF 物理页 5，Fig. 2 与 Eq. (16)–(19)；物理页 6，Eq. (20)–(21)）
2. **形成 dq 端口模型。** 作者把交流状态变换到 dq 坐标，定义 \(I_{br}=[i_d,i_q]^T\)、\(U_{br}=[E_{sd},E_{sq}]^T\)、\(b=[m_d,m_q]^T\)，并得到交流支路电流与直流电流的耦合 state equations。[pdf:E05]（PDF 物理页 6，Eq. (22)–(24)）也就是说，端口电压是 \([U_{br},U_{dc}]\)，网络返回的端口电流是 \([I_{br},i_{dc}]\)；“等效对象”是 AC/DC 多端口的平均电压—电流关系，不是一个只看 AC 侧的固定电压源。
3. **离散并盖章到 EMT 网络。** 用固定步长 implicit trapezoidal method 离散后，作者写成 \([I_{br},i_{dc}]^T=Y_{ne}[U_{br},U_{dc}]^T+\) history source 的 Dommel 形式。history term \(I_{ne}(t-\Delta t)\) 由上一步状态和端口电压组成。[pdf:E04]（PDF 物理页 6，Eq. (25)–(28)）
4. **从载波交点算 duty。** 对窗口 \(T=nT_s\)，假设调制波在载波尺度上线性变化，求每个 carrier 的上升、下降交点 \(t_{k,r},t_{k,f}\)，再以 \(m(t_0)=T^{-1}\sum|t_{k,f}-t_{k,r}|\) 汇总窗口 duty cycle。[pdf:E06]（PDF 物理页 7，Fig. 3 与 Eq. (29)–(31)）
5. **闭环跨周期修正。** 开环可以预知 \(v_c(t_0+T)\)；闭环不能，于是先用 \(v'_c(t_0+T)=2v_c(t_0)-v_c(t_0-T)\) 线性外推，求 duty 和网络解，再比较本步迭代值与预测值。若差值超过 \(\varepsilon\)，按 Eq. (33) 松弛并重算，直到满足误差要求。[pdf:E07]（PDF 物理页 7，Eq. (31)–(33)）所以时步内因果关系是“历史预测 → duty → 端口/网络求解 → 未来调制量 → 迭代修正”，不是一次显式更新，也不能据此声称无延迟闭合。

对于多个 VSC，论文没有展示整网组装式。由 Eq. (27) 可直接看出：\(Y_{11}\) 在 \(R,L,\omega,\Delta t\) 固定时可保持不变，但 \(Y_{12}=Y_{11}^Tb\)、\(Y_{22}=b^TY_{11}^Tb\) 随调制向量 \(b\) 变化。[pdf:E04]（PDF 物理页 6，Eq. (27)）因此，**基于证据的推断**是：若每台 VSC 按该式直接盖章，多个变流器接入时系统矩阵至少有调制相关块随步变化；论文没有给出固定导纳分裂、精确 Schur 消元、矩阵复用或无冲突硬件 schedule。ResearchStudio 的固定有根三相集电树、精确消元—恢复图与 PE/bank 映射属于另一条系统路线，不能由“多 VSC”或“等效”二字推出；现有 N=7 trunk 软件结果也不构成对本模型的硬件或数值验证。

## § 6 — 核心数学推导（无形式化数学则跳过）

第一层是**脉冲面积近似**。论文把惯性环节前两个窄脉冲的等效条件写成

\[
v_1T_1=v_2T_2,
\]

并要求 switching period \(T_s\) 足够小、脉宽 \(T_i\le T_s\)。[pdf:E03]（PDF 物理页 5，Eq. (15)）工程含义是：保留 zeroth moment（面积），丢弃脉冲在窗口内的位置和更高时间矩。若被驱动网络在载波附近仍有明显动态，这一近似就没有保证。

第二层是**VSC 连续端口状态**。在 dq 坐标中，论文写成

\[
\dot I_{br}=AI_{br}-\frac{b}{L}U_{dc}+\frac{1}{L}U_{br},\qquad
i_{dc}=b^TI_{br},
\]

其中 \(A\) 含 \(-R/L\) 与旋转耦合 \(\omega\)，\(b=[m_d,m_q]^T\)。[pdf:E05][pdf:E04]（PDF 物理页 6，Eq. (22)–(24)）这清楚表明 AC 与 DC 端口通过调制向量双线性耦合；它不是把 VSC 降成与控制无关的固定 Norton 元件。

第三层是**trapezoidal Dommel 离散**：

\[
\begin{bmatrix}I_{br}(t)\\ i_{dc}(t)\end{bmatrix}
=Y_{ne}
\begin{bmatrix}U_{br}(t)\\ U_{dc}(t)\end{bmatrix}
+
\begin{bmatrix}I_{ne}(t-\Delta t)\\ b^TI_{ne}(t-\Delta t)\end{bmatrix},
\]

其中 \(Y_{ne}\) 由 \(Y_{11},Y_{12},Y_{22}\) 组成，\(Y_{12}\) 和 \(Y_{22}\) 显式含 \(b\)，而 \(I_{ne}\) 保存历史状态与历史端口电压。[pdf:E04]（PDF 物理页 6，Eq. (25)–(28)）这一步把局部动态变成当步电压—电流代数关系，便于并入 EMT 网络，但“便于组网”不等于矩阵恒定。

第四层是**未来 duty 的预测—校正**。线性外推式 Eq. (32) 给出窗口末调制值，载波交点决定 duty，再用本步解修正。[pdf:E06][pdf:E07]（PDF 物理页 7，Eq. (29)–(33)）值得警惕的是，论文将 \(\delta\) 定义为绝对误差，却在 Eq. (33) 中直接写 \(v_{c,next}=a\delta+v_{c,this}\)。若没有另行保留带符号误差，该式只会向一个方向加量；正文没有伪代码、符号澄清或收敛证明。因此具体实现应视为存在符号歧义，不能从论文文字断言其迭代必然收敛。

## § 7 — 实验设计与结论

**问题 1：大步长 IE-AVM 能否跟随故障暂态？** 作者在 Matlab/Simulink 2022b 中搭建 DFIG 的 back-to-back 三相 VSC，详细模型、比较 averaged model 与 IE-AVM 都采用 fixed-step implicit trapezoidal solver。测试系统的开关频率为 3000 Hz，额定交流电压 690 V、直流电压 1150 V、active power reference 3 MW；其余电路与控制器参数列于 Table 1。[pdf:E08][pdf:E09]（PDF 物理页 8，Section 4、Fig. 4 与 Table 1）工况在 \(t=0.03\,\mathrm{s}\) 将交流电压降至 70%，在 \(t=0.13\,\mathrm{s}\) 清除故障；IE-AVM 步长为 100 μs，详细模型为 5 μs，比较 averaged model 为 50 μs。[pdf:E10]（PDF 物理页 9，Section 4）Fig. 5 的 rotor speed、grid-side voltage 与 current 曲线总体接近，说明在这个单一 LVRT 工况下，100 μs 的 IE-AVM 能复现所画出的系统级趋势；图中故障后的电压细节仍可见模型间差异。[pdf:E09]（PDF 物理页 8，Fig. 5）

**问题 2：是否证明了计算效率“大幅提升”？** 论文只报告了三个模型的仿真步长，没有报告 wall-clock time、迭代次数、矩阵重构/分解次数、硬件配置或加速比。[pdf:E10]（PDF 物理页 9，Section 4）因此支持的结论只是“该案例允许使用更大步长并得到相近曲线”，不能把它升级为已定量证明的计算加速。

**问题 3：是否验证了 large grid containing multiple converters？** 实验对象是一个 DFIG back-to-back VSC pair，而不是多站、多馈入或大规模 converter-rich grid；论文也没有报告 converter 数量扩展曲线、网络矩阵变化率、并行效率或实时执行结果。[pdf:E09][pdf:E10]（PDF 物理页 8，Fig. 4–5；物理页 9，Section 4）所以题目中的“大电网、多变流器、计算效率”在本文实验中没有形成尺度证据。作者结论声称模型适合 complex power electronic networks，但这是作者陈述，不是该案例已充分验证的外推。[pdf:E10]（PDF 物理页 9，Section 5）

## § 8 — Take-aways

**5 句话。** ① IE-AVM 用 equal-area impulse approximation 把高频开关序列压成 duty cycle，而不是保留每个开关事件。[pdf:E03]（PDF 物理页 5，Eq. (15)）② 它把 VSC 写成 AC dq 与 DC 端口耦合的 Dommel 离散模型，能直接参与 EMT 网络求解。[pdf:E05][pdf:E04]（PDF 物理页 6，Eq. (22)–(28)）③ 闭环 duty 依赖窗口末未来量，论文用历史外推和步内迭代修正，不是无延迟的一次求解。[pdf:E07]（PDF 物理页 7，Eq. (32)–(33)）④ 单个 DFIG LVRT 案例显示 100 μs IE-AVM 与 5 μs 详细模型的系统级曲线大体接近，但没有定量误差与运行时间。[pdf:E09][pdf:E10]（PDF 物理页 8，Fig. 5；物理页 9，Section 4）⑤ 论文没有证明多 VSC 大电网的矩阵固定性、规模扩展、FPGA 映射或确定性完整 EMT schedule。

**3 句话。** 这是一种“保留脉冲面积、舍弃开关细节”的 VSC 平均端口模型。它靠预测—校正处理大步长下的闭环跨周期依赖，但其导纳块随调制量变化，且校正式存在符号解释缺口。[pdf:E04][pdf:E07]（PDF 物理页 6–7，Eq. (27)、(33)）当前证据支持一个 DFIG 故障工况的可用性，不支持大规模多变流器、固定矩阵或实际加速比的强结论。

**1 句话。** 论文给出了一个可组网、可放大步长的 impulse-equivalent VSC 建模思路，但“等效”只在慢于载波的响应意义上成立，离精确、固定导纳、可直接硬件调度仍有实质距离。

## § 9 — 最脆弱的假设

最脆弱的单一假设是：**VSC 所驱动的网络状态与闭环调制信号，相对 carrier period 足够慢，以至于一个窗口只保留 pulse area，并对窗口末调制量做线性外推，仍能代表关键 EMT 响应。** 论文在 Eq. (15) 明确要求开关周期足够小，Section 3.2 又假定工频系统变化慢、调制波在载波尺度上线性变化。[pdf:E03][pdf:E06]（PDF 物理页 5，Eq. (15)；物理页 7，Fig. 3 前正文）

这一假设在弱阻尼 LC 模态落入 carrier sideband、控制器限幅/饱和、故障触发快速相位变化、非平衡工况或 converter interactions 产生载波尺度动态时可能失效。论文提供的证据只有 3000 Hz switching、100 μs IE-AVM 步长下的一次对称电压跌落曲线，而且作者自己限定 averaging period 不应超过三个 carrier cycles。[pdf:E08][pdf:E09][pdf:E10]（PDF 物理页 8，Section 3.2 末段、Table 1；物理页 9，Section 4）没有频率扫描、控制带宽扫描、谐振网络、非平衡故障或多 converter 相互作用证据，所以该假设一旦越界，核心的面积等效与线性预测会同时失去依据。

## § 10 — 最小复现实验

一周内可以只复现论文最核心且可证伪的一点：**在同一 DFIG back-to-back 系统中，IE-AVM 是否能以 100 μs 步长复现 5 μs detailed switching model 的 LVRT 端口响应。** 参数按 Table 1：3000 Hz switching、690 V AC、1150 V DC、3 MW active-power reference；工况按正文在 0.03 s 跌至 70%，0.13 s 清除。[pdf:E09][pdf:E10]（PDF 物理页 8，Table 1；物理页 9，Section 4）

实现时只需要三项：详细开关 VSC、按 Eq. (20)–(28) 构造的 IE-AVM、按 Eq. (29)–(33) 构造的 duty predictor/corrector。[pdf:E05][pdf:E04][pdf:E06][pdf:E07] 测量 grid-side voltage/current 和 rotor speed 的峰值误差、故障后 20 ms 内的 waveform RMSE、相位误差，以及每步 correction iteration count 和总 wall-clock time。若 IE-AVM 在作者工况下以 100 μs 稳定运行、误差显著小于不带 cross-period correction 的同模型，并且总时间低于 5 μs detailed model，则支持核心 claim；若修正式因符号解释无法稳定收敛，或 corrected model 不优于未修正模型，则直接反驳论文最关键的机制性主张，而不必先复现大电网。

## § 11 — 最强反例设计

最强反例不是再换一个普通故障，而是构造两组**脉冲面积完全相同、时间质心不同**的 PWM 序列，并让 VSC 端口接入一个弱阻尼共振频率靠近 carrier 或 sideband 的 LC 网络。Eq. (15) 预测两组脉冲经过“惯性环节”后大体等效；但如果网络能分辨脉冲时序，两组 detailed switching 响应会在峰值电流、直流母线波动或谐振能量上显著分离，而只保留 duty 的 IE-AVM 会给出相同或近似相同结果。[pdf:E03]（PDF 物理页 5，Eq. (15)）

再把闭环控制带宽逐步推近 carrier scale，并施加使 modulation command 快速转折的故障。这样同时攻击 equal-area 与线性外推两个环节，但替代解释仍可区分：若只在谐振网络中失败，问题来自被忽略的 pulse timing；若无谐振也随控制带宽上升而失败，问题主要来自 Eq. (32) 的 slow-variation assumption。[pdf:E06][pdf:E07]（PDF 物理页 7，Fig. 3、Eq. (32)）这个反例能真正推翻“在关注频带内可用大步长代表 converter 暂态”的适用范围，而不是只说明参数还需调优。

## § 12 — Follow-up Research Bet

**主 idea：把 zeroth-moment duty model 升级为“端口 impulse moment packet”，并由固定被动网络编译器消费。** 新研究问题是：能否在每个 macro-step 内，不只保存脉冲面积 \(M_0\)，还保存相对窗口起点的一阶时间矩 \(M_1\)（等价于 pulse centroid），把每台 VSC 的高速开关作用压缩成少量带时间结构的 AC/DC 端口 packet，再由固定拓扑网络的消元—恢复图统一推进？这将首次允许在不展开全部开关事件的前提下，区分“面积相同但时刻不同”的脉冲，并有机会把调制相关计算局部化，而让大部分被动电网矩阵和硬件 schedule 保持固定。

因果链是：Eq. (15) 只保留面积，所以网络若能感知 carrier-sideband 就会混淆不同 pulse timing；Eq. (30) 实际已经求出了每个上升/下降交点，却在 Eq. (31) 中只把它们压成总 duty。[pdf:E03][pdf:E06]（PDF 物理页 5，Eq. (15)；物理页 7，Eq. (30)–(31)）把这些交点进一步压成 \((M_0,M_1)\)，可在局部端口更新中保留第一个时间结构；全局网络则消费固定维度 packet，而不是逐事件改拓扑。Fig. 5 中 100 μs IE-AVM 已能贴近主要系统趋势、但故障后 grid-voltage 高频细节仍有模型差异，这为“低阶时间矩可能补回部分细节”提供实验动机，而不是证明。[pdf:E09]（PDF 物理页 8，Fig. 5）

这个 bet 改变了状态表示、时间对象、硬件映射和评价对象：从单一 duty 变成带时间矩的端口 packet，从步内反复预测未来 modulation 转向局部事件压缩与全局固定图协同；评价也从“曲线看起来接近”改成“同面积异质心脉冲能否被区分，以及矩阵/PE schedule 是否真正固定”。它与本文 IE-AVM 的实质区别是保留 first temporal moment；与正文所述 EE-AVM 的区别是目标不是匹配窗口总能量；与论文仅在参考文献中点名的 pulse-source-pair 方法无法做更细比较，因为本文未提供其方法细节。来源闭合条件下，这只是候选判断，不声称 novelty。

最大收益是把 converter switching 的关键时间结构与固定树网络求解真正拆开，使确定性 full-step EMT schedule 有可检验的物理输入；最大科学风险是 \(M_1\) 仍不足以表征非线性闭环与共振，最终需要接近逐事件的高阶矩，失去压缩价值。首个判别实验使用 §11 的 same-area/different-centroid 脉冲对，同时比较 detailed switching、zeroth-moment IE-AVM 与 \((M_0,M_1)\) model：若一阶矩模型在不改变被动网络矩阵的前提下恢复两组响应差异，且优势集中在 pulse timing 可辨识的共振工况，支持该机制；若它只靠更多迭代或重新盖章才能改善，则最强替代解释是“额外计算量”，而不是 moment representation。

**Wild-card alternative：** 把多 VSC 的 carrier phase 本身作为主动实验与控制变量，设计跨变流器的相位编码，使各端口 impulse 在共享网络模态上相消；这条路线改变的是激励生成与群体协同机制，而不是增加端口时间矩。
