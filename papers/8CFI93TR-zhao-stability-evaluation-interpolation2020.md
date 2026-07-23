# Stability Evaluation of Interpolation, Extrapolation, and Numerical Oscillation Damping Methods Applied in EMT Simulation of Power Networks With Switching Transients

- 作者：Huanfeng Zhao；Shengtao Fan；Aniruddha M. Gole
- 出处：IEEE Transactions on Power Delivery
- 年份：2020
- DOI：10.1109/TPWRD.2020.3018651
- Zotero key：8CFI93TR
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。PDF 物理页从文件首页按 1 开始。下文把“论文直接陈述”“相关文献结论”“基于证据的推断”和“候选判断”明确分开。

## § 1 — 研究问题与重要性

论文研究的不是“哪种插值更精确”这一单一问题，而是更基础的安全性问题：当 EMT 仿真器为了处理开关时刻、消除 trapezoidal chatter、重初始化历史项或回到原时间网格而临时改变数值推进规则时，原有稳定性保证是否仍然成立。作者的核心结论是，在 lumped strictly passive switched circuit（LSPSC，集总严格无源开关电路）模型中，只要每个物理开关状态都严格无源，linear interpolation、Critical Damping Adjustment（CDA）以及文中分析的 FIRST 步骤不会给离散仿真注入净能量，因而不会破坏 BIBO stability；相反，extrapolation 可能注入能量，不能获得同样的无条件保证。[pdf:E01](_evidence/E01-p001-title-abstract.png)

先说物理意义。真实电感和电容储存能量，电阻耗散能量；在没有外部激励的严格无源网络中，总储能应持续下降。数值算法若在开关事件附近凭空增加离散“能量”，就可能把本来稳定的电路算成幅值不断增长的波形。这里的数值稳定性并不等于波形准确：一个有 chatter 但幅值有界的结果仍可满足 BIBO stability，却可能严重失真；一个能量逐步增大的结果则会数值发散。开关时刻通常落在固定步长网格之间，强行把事件对齐到网格会造成 current chopping 或非特征谐波，因此实际 EMT 程序必须插值定位事件，并随后处理时间网格错位。[pdf:E02](_evidence/E02-p001-interpolation-problem.png)

这项工作的价值在于把工程程序里的“事件补丁”纳入同一稳定性证明。只证明 trapezoidal 或 Backward Euler 对单一 LTI 状态 A-stable/L-stable 并不够，因为插值、重初始化和阻尼步骤本身相当于新的离散开关状态；它们也必须满足共同能量下降条件。

## § 2 — 前人工作与不足

论文直接回顾了四类既有处理。第一，linear interpolation 定位网格之间的开关瞬间；第二，用半步 Backward Euler、2s-DIRK 或 instantaneous solution 重建开关后的历史项；第三，用人工 snubber、位置相关积分、两次半步 BE 的 CDA 或 L-stable 方法抑制 trapezoidal chatter；第四，再做一次插值回到原始时间网格。相关文献和商业程序已经广泛采用这些办法，但它们分别改变了事件处的积分矩阵、样本间隔或历史源。[pdf:E03](_evidence/E03-p002-switching-remedies.png)

相关文献中的已有结论是：对稳定 LTI 系统，A-stable 或 L-stable 方法可给出稳定数值解；作者团队先前工作进一步指出，对开关系统这仍不够，仿真的 BIBO stability 还要求每个开关状态严格无源，并已证明 trapezoidal 与 BE 对 LSPSC 的稳定性。本文指出的缺口是：interpolation 和 CDA 恰好在事件处改写了离散推进，所以先前针对原始物理开关状态的结论不能直接覆盖这些新步骤。[pdf:E04](_evidence/E04-p002-stability-gap.png)

因此，本文对 prior work 的批评不是“它们没考虑开关”，而是更精确的：它们没有把事件处理步骤本身当成 switched system 的额外 mode 来检查。工程上经常有效的算法，还缺少一个能逐步骤回答“这一操作是耗能、守能还是注能”的统一判据。

## § 3 — 重建作者的思考路径

可以从论文之前已有的线索重建如下路径。首先，把含 \(s\) 个二值开关的网络看成至多 \(2^s\) 个连续状态：

\[
\dot{x}(t)=A_i x(t)+B_i u(t),
\]

积分后成为

\[
x(n+1)=G_i x(n)+H_i u(n).
\]

这里 \(n\) 只标记离散样本次序，不保证相邻样本相隔同一个物理时长；事件插值后，间隔可以是 \(k\Delta t\)。对电感、电容状态，取广义储能 \(E=x^\mathsf{T}Vx\)；严格无源性意味着每个连续 mode 都使该储能下降。[pdf:E05](_evidence/E05-p003-state-energy-model.png)

其次，引入 Common Quadratic Lyapunov Function（CQLF，共同二次 Lyapun诺夫函数）：若同一个正定矩阵 \(P\) 对所有离散 mode 都满足

\[
G_i^\mathsf{T}PG_i-P\prec0,
\]

那么任意 mode 切换下都共享同一把“能量尺”。以真实储能矩阵 \(V\) 作为 \(P\)，单步能量变化就是

\[
\Delta E=x^\mathsf{T}(G_i^\mathsf{T}VG_i-V)x.
\]

若每一种可能步骤都令 \(\Delta E<0\)，零输入系统渐近稳定；论文引用既有 switched-system 结果，把它连接到有界输入下的 BIBO stability。[pdf:E06](_evidence/E06-p003-cqlf-energy-criterion.png)

最后，最自然的问题就变成：不要把 interpolation、CDA 和 re-initialization 当作代码特例，而要写出它们各自的 \(G_{\text{event}}\)，逐个检查 \(G_{\text{event}}^\mathsf{T}VG_{\text{event}}-V\) 的符号。这个视角是本文方法的真正起点。

## § 4 — 核心 Intuition

核心 intuition 是：一次事件插值也可以视为 switched system 新增的一个离散 mode；只要这个 mode 在共同的物理储能度量下不增能，它就不会成为数值发散源。线性插值位于旧状态与一次稳定推进之间，权重 \(0<k<1\)，因而保留耗能性；外推的权重达到或超过 1，越过了这条“耗能线段”，就可能把能量符号翻成正值。[pdf:E07](_evidence/E07-p004-interpolation-state.png)

作者对定位开关瞬间的线性插值给出完整不等式链：由原始 trapezoidal mode 的 \(G_{\mathrm{TR},i}^\mathsf{T}VG_{\mathrm{TR},i}-V\prec0\)，再利用 \(k(1-k)>0\) 和 \(V\succ0\)，推出新增 interpolation mode 的 \(\Delta E_{\mathrm{Int}}<0\)。这不是“插值通常比较平滑”的经验判断，而是同一储能函数下的负定性证明。[pdf:E08](_evidence/E08-p004-negative-energy-proof.png)

## § 5 — 具体方法与完整 Pipeline

以一个二极管电流在一个时间步内过零为例，论文的方法可重建为以下 pipeline：

1. **预测事件。** 在开关前状态 \(i\) 下，用 nominal trapezoidal step \(\Delta t_{\mathrm{TR}}\) 得到预测点 \(x_p(t+\Delta t_{\mathrm{TR}})\)。若开关量在步内越过阈值，就用 \(0<k<1\) 定位事件时刻 \(t+k\Delta t_{\mathrm{TR}}\)。
2. **把定位插值写成新 mode。** 线性插值的状态矩阵为
   \[
   G_{\mathrm{Int},iji}=I+k(G_{\mathrm{TR},i}-I).
   \]
   它不是原网络的物理拓扑，却是数值轨迹真实经历的一步。作者证明这一 mode 降低储能。[pdf:E07](_evidence/E07-p004-interpolation-state.png)
3. **切换并重同步时间网格。** 事件后用新物理状态 \(j\) 推进；为了回到原来的整数时间网格，再以权重 \(1-k\) 插值。因为 \(0<1-k<1\)，它与前一步具有相同结构，也满足 \(\Delta E<0\)。[pdf:E09](_evidence/E09-p005-grid-resync.png)
4. **抑制 chatter。** CDA 在开关后执行两次半步 BE。BE 对 LSPSC 的每一步都降低能量，而且半步 BE 的导纳矩阵与整步 trapezoidal 相同，因此不需要重新分解矩阵。用于 chatter suppression 的 \(k=0.5\) 线性插值也落在已证明的 \(0<k<1\) 范围内。[pdf:E10](_evidence/E10-p005-cda-chatter-reinit.png)
5. **处理导数不连续。** 开关时状态 \(x\) 连续，但 \(A_i\to A_j\) 会令 \(\dot{x}\) 跳变。若 companion circuit 继续使用开关前电感电压或电容电流构造历史源，就相当于混用了 \(A_i\) 与 \(A_j\)。半步 BE 通过只依赖连续状态变量避开错误导数；instantaneous solution 则更新开关后导纳并重解节点方程。[pdf:E11](_evidence/E11-p006-derivative-reinit.png)
6. **评价其他重同步方法。** 对 FIRST，先在 \((k-1+\delta)\Delta t\) 定位事件，再用可保持导纳矩阵不变的 generalized integration 一步到 \((k+1)\Delta t\)。作者仍把该步写成新 mode 并检查能量变化。[pdf:E12](_evidence/E12-p006-first-definition.png)
7. **比较 extrapolation。** FIRST 的能量表达式由连续无源项和额外非正项组成，因此 \(\Delta E_{\mathrm{FIRST}}<0\)。Extrapolation 则有
   \[
   G_{\mathrm{ext},i}=I+k_{\mathrm{ex}}(G_{\mathrm{TR},i}-I),\qquad
   k_{\mathrm{ex}}=2-\delta\in[1,2],
   \]
   超出了线性插值证明所需的 \(k<1\)，所以可能出现 \(\Delta E>0\)。[pdf:E13](_evidence/E13-p007-first-extrapolation.png)

输出不是一个新的仿真器，而是一套方法级稳定性判定：对任意事件处理算法，写出其零输入离散状态矩阵，在共同储能矩阵 \(V\) 下检查单步能量是否严格下降。

## § 6 — 核心数学推导（无形式化数学则跳过）

先抓住最小数学对象。对零输入离散 mode \(x^+=Gx\)，储能从 \(E=x^\mathsf{T}Vx\) 变为

\[
E^+=(Gx)^\mathsf{T}V(Gx),
\]

所以

\[
\Delta E=x^\mathsf{T}(G^\mathsf{T}VG-V)x.
\]

矩阵 \(G^\mathsf{T}VG-V\prec0\) 的物理含义是：无论当前状态向量朝哪个方向，只要不为零，这一步都会耗散储能，而不是只对某一条波形成立。[pdf:E06](_evidence/E06-p003-cqlf-energy-criterion.png)

对线性插值，令 \(G_k=I+k(G-I)\)，其中 \(0<k<1\)。代入上式并整理，作者把 \(\Delta E_k\) 约束为含 \(k(1-k)\) 的二次型。关键矩阵可进一步界为

\[
(G-I)^\mathsf{T}V(G-I)\succ0
\]

的负值，因此

\[
\Delta E_k<0.
\]

直观地说，\(G_k\) 沿着从“不推进” \(I\) 到“完整稳定推进” \(G\) 的线段移动；严格无源性保证这条线段内部仍朝储能下降方向。[pdf:E08](_evidence/E08-p004-negative-energy-proof.png)

CDA 的证明更直接：每个半步 BE 的

\[
\Delta E_{\mathrm{BE}}
=x^\mathsf{T}\!\left[(I-A_i^\mathsf{T}\Delta t_{\mathrm{BE}})^{-1}
V(I-A_i\Delta t_{\mathrm{BE}})^{-1}-V\right]x<0,
\]

两步负能量变化相加仍为负。FIRST 的长式虽然形式不同，但符号判断同样来自 \(VA_i+A_i^\mathsf{T}V\prec0\) 以及一个带非负系数的附加负半定项。[pdf:E10](_evidence/E10-p005-cda-chatter-reinit.png) [pdf:E13](_evidence/E13-p007-first-extrapolation.png)

Extrapolation 的危险恰在系数域改变。当 \(k_{\mathrm{ex}}\ge1\) 时，\(k(1-k)\) 不再为正，原证明中保证耗能的符号链断裂。这里必须精确区分：论文证明的是“不能保证稳定，且给出了一个实际不稳定例子”，不是“所有 extrapolation、所有步长都会不稳定”。

## § 7 — 实验设计与结论

**问题 1：FIRST 和 Extrapolation 的理论能量判据能否预测真实数值行为？** 作者搭建一个一阶 RC 开关电路。开关用二值电阻表示，关断电阻为 \(1\,\mathrm{M}\Omega\)，导通电阻为 \(10\,\mathrm{m}\Omega\)，直流源为 \(100\,\mathrm{V}\)；分别采用 \(0.1\,\mu\mathrm{s}\)、\(86\,\mu\mathrm{s}\) 和 \(87\,\mu\mathrm{s}\) 步长。开关周期被刻意设为关断 \(8.3\Delta t\)、导通 \(1.7\Delta t\)，使每次事件都落在网格之间；turn-on 时 \(\delta=0.3\)，故 \(k_{\mathrm{ex}}=1.7\)。为排除错误重初始化这一替代解释，作者在每次开关后重新计算电容电流。[pdf:E14](_evidence/E14-p007-experiment-setting.png)

**答案。** 在 \(0.1\,\mu\mathrm{s}\) 时，两种方法的波形基本重合并保持稳定。步长增至 \(86\,\mu\mathrm{s}\) 时，两者仍稳定，但 Extrapolation 的准确性已经很差；其报告能量变化为 \(-1.6326\times10^{-7}\)。再把步长只增加 \(1\,\mu\mathrm{s}\) 到 \(87\,\mu\mathrm{s}\)，报告能量变化变为 \(+1.2220\times10^{-7}\)，Extrapolation 波形幅值随时间增长，而 FIRST 仍保持有界。这里没有从曲线估读额外精确数值；上述数字均为正文直接报告值。[pdf:E15](_evidence/E15-p008-waveforms-energy.png)

**问题 2：单步能量判据与论文总 claim 是否一致？** 论文结论把理论和示例对应起来：linear interpolation、CDA 与 FIRST 在“每个开关状态严格无源”的条件下不引入导致 BIBO instability 的 mode；Extrapolation 因不能保证能量下降而可能不稳定。作者同时明确提醒，\(86\,\mu\mathrm{s}\) 的稳定不代表准确。[pdf:E16](_evidence/E16-p008-results-conclusion.png)

**问题 3：instantaneous solution re-initialization 是否也被覆盖？** 附录把多次开关间的矩阵乘积重新排列，说明事件边界只额外留下有限的首尾矩阵；原 LSPSC trapezoidal 轨迹的指数衰减仍可由有限常数放大后保持，因此有界输入下仍为 BIBO stable。这个证明依赖矩阵可逆、首尾因子有界以及原 switched trajectory 的指数稳定性。[pdf:E17](_evidence/E17-p009-instantaneous-proof.png)

实验的证据强度边界也很清楚：它是一个简单一阶电路的机制验证，不是对商业 EMT 程序、复杂换流器、大网络或有限精度实现的广泛 benchmark。论文最强证据来自解析证明，示例只验证判据能预测一个步长临界附近的稳定/不稳定转变。

## § 8 — Take-aways

**5 句话。**  
1. EMT 开关事件处理会新增数值 mode，不能只靠原积分法对 LTI 系统的 A-stability 判断整体稳定性。  
2. 对每个物理开关状态严格无源的 LSPSC，可用真实储能构造 CQLF，并逐步检查事件算法是否注能。  
3. linear interpolation、回网格插值、CDA 和 FIRST 在论文条件下都保持能量下降。[pdf:E16](_evidence/E16-p008-results-conclusion.png)  
4. Extrapolation 的系数越过 1 后失去该保证，示例中 \(86\,\mu\mathrm{s}\) 仍稳定而 \(87\,\mu\mathrm{s}\) 发散。[pdf:E15](_evidence/E15-p008-waveforms-energy.png)  
5. 稳定只说明解不无界，不说明 chatter、相位、幅值或开关瞬态足够准确。

**3 句话。**  
1. 把事件算法写成离散状态矩阵，再检查共同储能是否下降，是本文最可迁移的方法。  
2. 插值在 \(0<k<1\) 时是耗能线段，外推在 \(k\ge1\) 时可能跨入注能区。  
3. 所有保证都受“每个 mode 严格无源”和理想数学实现的约束。

**1 句话。**  
事件处理是否安全，关键不在名称叫 interpolation、damping 还是 re-initialization，而在它对应的离散一步是否向数值系统注入能量。

## § 9 — 最脆弱的假设

最脆弱的假设是：网络能被表示为 LSPSC，且**每一个**二值开关状态都对同一个物理储能矩阵 \(V\) 严格无源。论文的所有“always stable”结论都把这一点写成前提，而非从 interpolation 或 CDA 本身无条件推出。[pdf:E01](_evidence/E01-p001-title-abstract.png) [pdf:E16](_evidence/E16-p008-results-conclusion.png)

这一假设在实际系统中可能失败：受控电力电子变换器可呈现负增量阻抗，理想无损 LC 子网络只满足非严格无源，控制器、延迟、饱和和离散采样会引入不在二值电阻网络状态 \(x\) 内的动态，频率相关线路和拓扑奇异性也可能破坏共享 \(V\) 的建模。这里属于基于证据的推断，论文没有用复杂受控变换器逐项验证这些失效情形。

若某一个 mode 不严格无源，结论不是“仿真一定发散”，而是 CQLF 的这条充分条件不能再给保证。论文给出的 Extrapolation 示例恰好说明了这种逻辑边界：能量条件不满足时，有些步长仍稳定，但另一些非常接近的步长会发散。[pdf:E15](_evidence/E15-p008-waveforms-energy.png)

## § 10 — 最小复现实验

一周内最值得复现的是“能量符号能否预测 86/87 \(\mu\mathrm{s}\) 的分岔”，而不是重建完整 EMT 软件。

1. 用论文 Fig. 5 的一阶 RC 开关电路，实现 exact discrete-time reference、FIRST 和 Extrapolation 三条路径；采用 \(1\,\mathrm{M}\Omega/10\,\mathrm{m}\Omega\) 开关、\(100\,\mathrm{V}\) 直流源、关断 \(8.3\Delta t\)/导通 \(1.7\Delta t\)，并在开关后重新计算电容状态，避免把 re-initialization 错误混入比较。[pdf:E14](_evidence/E14-p007-experiment-setting.png)
2. 扫描 \(\Delta t=80\)–\(90\,\mu\mathrm{s}\)，对每个步长直接计算新增 mode 的标量 \(G^\mathsf{T}VG-V\)，同时记录 0.1 s 内的最大电容电流、末段包络斜率和是否超过预设幅值阈值。
3. 支持 claim 的结果是：FIRST 在扫描范围内始终 \(\Delta E<0\) 且波形有界；Extrapolation 在能量项过零附近由有界转为增长，至少复现 \(86\,\mu\mathrm{s}\) 为负、\(87\,\mu\mathrm{s}\) 为正的报告符号与对应趋势。[pdf:E15](_evidence/E15-p008-waveforms-energy.png)
4. 反驳核心机制的结果是：在状态更新、事件定位和重初始化均与论文一致时，出现持续 \(\Delta E<0\) 却幅值无界，或 FIRST 出现正能量 mode。只出现数值大小略有差异不能单独反驳，需先排除参数、单位和浮点实现差异。

## § 11 — 最强反例设计

最强反例不应只是换一个更复杂电路，而应直接攻击“新增 mode 的能量判据足以覆盖实际事件实现”这一桥梁。可以构造一个每个连续拓扑都能找到共同严格无源 \(V\) 的小型 RLC switched network，同时让两个开关在同一步内近乎同时动作，并在生产式事件循环中加入常见的有限精度行为：事件时间 clipping、阈值回跳导致的重复插值、状态依赖事件排序，以及一次步内多次 re-initialization。然后并行运行两个求解器：

- 参考求解器严格执行论文矩阵 \(G_{\text{event}}\)，每次事件后核对 \(x^\mathsf{T}Vx\)；
- 生产式求解器执行实际代码路径，并从真实更新反推出 \(\widehat G_{\text{event}}\)。

若参考求解器在所有论文假设成立且每步解析 \(\Delta E<0\) 时仍发散，才是真正反例，可直接推翻证明链。若只有生产式求解器发散，并发现 \(\widehat G_{\text{event}}\neq G_{\text{event}}\) 或一次宏步的组合矩阵注能，则它不反驳定理，但会有力证明论文结论不能直接外推到含 event iteration 和 finite precision 的商业实现。这个设计比单纯加入主动负阻更强，因为后者一开始就违反严格无源前提。

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty。** 本卡没有对 2020 年后的相关工作做充分检索，因此这里只提出可证伪方向：把“离线证明每个理想事件 mode 无源”改成“运行时约束实际事件更新的能量预算”。求解器在每次 interpolation、re-initialization 或多事件迭代后计算可观测的离散供给率；若候选更新使 \(E^+-E\) 超过输入提供的能量，就在保持事件时刻一致的前提下，求解一个最小修正，把该更新投影回 dissipative set，而不是固定选择 CDA 或 FIRST。

（a）未满足的需求是：真实 EMT 求解器包含主动控制、非严格无源 mode、有限精度和多事件循环，未必存在论文要求的单一 CQLF。  
（b）它可能产生本领域认可的价值，因为评价对象从理想方法名变成实际执行的每一步，并可同时给稳定性、误差和实时计算开销。  
（c）可借鉴 switched-system 的 multiple Lyapunov functions、dissipativity、passivity observer/controller，以及 constrained projection。  
（d）第一个证伪实验是：在严格无源 RLC、多开关近同时事件和主动负增量阻抗三个递增难度算例上，与 unmodified interpolation、CDA、FIRST 比较；若投影仍出现净注能或为了稳定而把开关时刻/波形误差放大到不可接受，就否定该方案。  
（e）它与本文的实质区别是：本文为预先给定的理想算法寻找充分稳定条件；候选方向直接约束运行时的实际复合更新，并把“不存在共同严格无源 \(V\)”当作目标问题，而不是排除在前提之外。
