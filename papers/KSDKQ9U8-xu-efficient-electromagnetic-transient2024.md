# An Efficient Electromagnetic Transient Modeling Method Based on Unit Division and Parallel Simulation Framework for Large-scale Photovoltaic Power Stations

- Zotero key：KSDKQ9U8
- canonical slug：`xu-efficient-electromagnetic-transient2024`
- 作者：Mingwang Xu；Wei Gu；Yang Cao；Shuaixian Chen
- 年份与出处：2024，2024 2nd Power Electronics and Power System Conference（PEPSC）
- DOI：10.1109/PEPSC63375.2024.10823475
- 源 PDF：`_source.pdf`
- PDF SHA-256：`3d7e931e611b4be5b1cf4b16bc2f767a3e92e5728e2cd291610f9a0655979666`

### 证据缓存

PDF 物理页从文件首页按 1 开始。下列 PNG 均为 300 dpi 整页渲染，保留双栏上下文、图题、公式编号、坐标轴和表格单位；精读中的 `[pdf:E..]` 均指向这里。

- [pdf:E01]：[物理页 1，标题、摘要、研究背景与 related work](_evidence/E01-p001-fullpage.png)
- [pdf:E02]：[物理页 2，PVPS 拓扑、PV cell 等效与式 (1)–(5)](_evidence/E02-p002-fullpage.png)
- [pdf:E03]：[物理页 3，离散伴随模型、NFSS 局限、UDM 分区与图 4–6](_evidence/E03-p003-fullpage.png)
- [pdf:E04]：[物理页 4，式 (8)–(14)、运算量比较与历史电流源并行更新](_evidence/E04-p004-fullpage.png)
- [pdf:E05]：[物理页 5，式 (15)–(18)、并行流程、实验模型与参数表](_evidence/E05-p005-fullpage.png)
- [pdf:E06]：[物理页 6，三类扰动、误差描述、效率与 speedup 图](_evidence/E06-p006-fullpage.png)
- [pdf:E07]：[物理页 7，效率结论、适用性主张与参考文献](_evidence/E07-p007-fullpage.png)

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的矛盾：大型光伏电站（PVPS）由几十到上百个光伏发电单元（PVPGU）构成，每个单元又包含 PV array、boost、converter、filter 和升压 transformer。若全部保留开关与内部节点，EMT 仿真必须在微秒级步长下反复求解高维、随开关状态变化的节点导纳矩阵，规模越大越难在可接受时间内完成；但若把大量单元粗略聚合，又可能丢失站内差异和故障暂态。[pdf:E01] [pdf:E02]

作者的目标不是再造一个只看 PCC 外部特性的黑箱，而是在保留单元内部动态可回算的前提下，同时压缩两类成本：一是建模阶段消元所需的矩阵规模，二是每个时间步中“外部网络求解 → 内部节点反解 → 历史电流源更新”的串行依赖。[pdf:E01] [pdf:E03] 对工程使用者而言，价值在于同一模型既能观察站级功率和并网点电压，也能回到 cluster/单元内部电流，同时在单机多线程环境中获得随 PVPGU 数量增加而扩大的加速收益。[pdf:E05] [pdf:E06]

论文原文把 EMT 用于分析高渗透光伏下的故障和振荡，并称其对安全稳定运行重要。[pdf:E01] 这里需要收紧理解：论文实际验证的是三个短时场景及运行时间，不等于已经证明该模型足以覆盖所有稳定性问题。

## § 2 — 前人工作与不足

论文把已有路径分成两类。第一类是 aggregation/equivalent modeling：按辐照度、温度、逆变器参数、控制策略、线路阻抗或扰动响应曲线对 PV 单元聚类，再用少量等效机组代表整站。作者认为这类方法本质上仍是聚合，只能代表固定场景，难以同时表达环境、控制和设备参数强耦合下的动态关系；PV array 的动态和控制参数影响也容易被压缩掉。[pdf:E01]

第二类是并行加速，包括 parareal 的 coarse operator 和时空混合并行。这些工作说明并行计算可以提高大系统 EMT 或暂态仿真效率，但没有直接解决本文关心的 PVPGU 内部节点保留与 NFSS（节点形成法的低阶等效/内部节点反解流程）串行链。[pdf:E01] 论文还以 NFSS 为最直接的比较对象：一个 17 节点 PVPGU 若直接做 nodal analysis，需要处理 16 维矩阵；NFSS 消去内部节点时仍需逆一个 13 维矩阵，随后还要串行地形成外部等效、反解内部节点、更新历史电流源。[pdf:E03]

论文真正要补的缺口因此不是“以前没有等效模型”，而是：已有聚合模型牺牲内部可见性，已有 NFSS 虽降阶却没有把矩阵进一步拆小，也没有打散跨步骤串行依赖。需要注意，论文只通过自身叙述和文末 16 篇参考文献建立这一边界，没有系统性 literature review；因此“相对所有前人工作都更优”并未被本 PDF 充分证明。[pdf:E07]

## § 3 — 重建作者的思考路径

可以从论文已经给出的旧知识和失败模式，逆向重建如下路径。

1. EMT 中的电感、电容和变压器经离散后都能写成“导纳 + 历史电流源”的 Norton 形式；开关则用 binary resistance 表示。因此每个时间步的困难可转化为节点方程和历史量更新，而不是必须在连续时间里整体求解。[pdf:E03]
2. 直接把整个 PVPGU 一次消元虽然能得到外部低阶端口，但 13 维逆矩阵仍然昂贵；更关键的是，外部解、内部回代和历史源更新构成顺序链。[pdf:E03]
3. 观察离散电路拓扑会发现，含 capacitor 的支路可作为边界，把 17 节点网络拆成三个较弱耦合的 sub-unit。若分别隐藏各 sub-unit 内部节点，单个大逆矩阵就能改写为多个小矩阵。[pdf:E03]
4. 进一步利用 capacitor port voltage 和 inductor branch current 在相邻时间步不突变的性质，可以用上一步信息建立各 sub-unit 内部节点的显式关系，使外部网络求解、内部节点反解和历史源更新在同一时间步中拥有更多并行机会。[pdf:E05]

最后一步才自然导出本文的组合方案：UDM 负责改变矩阵结构，parallel framework 负责改变时间步内的依赖图。这个重建解释了为何两部分缺一不可：只做 UDM 会减少运算但仍沿用串行 NFSS；只开多线程而不拆矩阵，则任务粒度和依赖仍不利于并行。

## § 4 — 核心 Intuition

核心 intuition 是：不要把一个 PVPGU 当成必须一次整体消元的 13 维内部网络，而是沿 capacitor branch 把它切成三个 sub-unit，把一次大矩阵求逆变成若干小矩阵求逆。[pdf:E03] 再把电容电压、电感电流的相邻步连续性当作“延迟一拍但可并行”的接口，让外部节点、内部节点和历史电流源不再全部首尾相接。[pdf:E05] 物理上保留了单元内部状态，计算上则把大而串行的任务改造成小而可并发的任务。

## § 5 — 具体方法与完整 Pipeline

以一个由 PV array、boost、VSC、filter 和 transformer 构成的 PVPGU 为例，输入是当前辐照度 \(G\)、温度 \(T\)、控制指令、开关状态，以及前一时间步的电压、电流和历史源；输出是该步的外部端口量、内部节点电压及更新后的历史电流源。

1. **把 PV array 化为环境驱动的一端口源。** 单二极管五参数模型原本是 \(i_{pv}\) 与 \(v_{pv}\) 的隐式超越关系。作者用前一时间步的端口电流、电压构造 \(v_d(t)\)，把右端未知量近似为已知历史量，从而得到随 \(G,T\) 变化的等效电流源，见式 (1)–(5)。[pdf:E02]
2. **离散电气元件。** 电感、电容转换为 Norton companion circuit，变压器用 trapezoidal integration 得到端口导纳矩阵和历史电流源，开关采用 0/1 状态控制的 binary resistance model。[pdf:E03]
3. **按物理边界做 unit division。** 选择 capacitor branch 为分界，把 17 节点 PVPGU 拆成三个 sub-unit；每个 sub-unit 独立隐藏内部节点，最后保留 6 节点等效电路。图 5 展示多个 PVPGU 的 sub-unit 等效后仍接入同一 bus/external grid。[pdf:E03]
4. **先解决站外/站内端口接口。** 每个 PVPGU 的端口关系写成 \(I=GV+J^{his}\)，与 AC system 的 nodal voltage equation 联立，求得各 PVPGU 外部节点电压。[pdf:E05]
5. **并行回算内部节点。** sub-unit 1 用式 (15)–(16) 由前一步边界量和等效矩阵回算 \(U_1,U_7\)；sub-unit 2 用式 (17) 结合三相开关函数 \(S_a,S_b,S_c\) 回算 \(U_9,U_{10},U_{11}\)；sub-unit 3 用式 (18) 根据相邻步电压及电感支路电流、历史源回算 \(U_{15},U_{16},U_{17}\)。[pdf:E05]
6. **并行更新历史电流源。** 作者把各支路更新统一写为 \(I_h(t+\Delta t)=\alpha Y_bU_b(t)+\beta I_b(t)\)，对 L/C 又化为 \(\beta I_h(t)+(\alpha+\beta)Y_bU_b(t)\)，让不同支路独立更新。[pdf:E04]
7. **进入下一时间步。** 图 10 把原 NFSS 的三段串行过程改为 parallel framework 下的并发块；新的历史源成为下一步输入。[pdf:E05]

论文没有给出程序、线程调度代码、同步屏障位置或硬件映射，因此这里能重建的是数学 pipeline，不是可直接编译的实现。

## § 6 — 核心数学推导

这篇论文的数学重点有三层。

第一层是离散元件的统一接口。以 transformer 为例，式 (6) 把两端口电流写成

\[
\begin{bmatrix}i_{T1}(t)\\i_{T2}(t)\end{bmatrix}
=G_T
\begin{bmatrix}v_{T1}(t)\\v_{T2}(t)\end{bmatrix}
+
\begin{bmatrix}j_{T1}(t-\Delta t)\\j_{T2}(t-\Delta t)\end{bmatrix}.
\]

这里 \(G_T\) 是由 leakage inductance、excitation inductance、变比和步长决定的固定/状态相关端口导纳，\(j_T\) 携带前一步记忆。[pdf:E03] intuition 是把“含微分的动态元件”变成每一步都可参与线性 nodal solve 的代数元件。

第二层是 UDM 的运算量比较。作者给出的 NFSS 运算次数为

\[
T_{\text{sum}}=\frac{2}{3}n^3+(2m+3)n^2+4nm^2+nm-\frac{2}{3}n\sim O(n^3),
\]

其中 \(m,n\) 分别是外部、内部节点数。对图 4 的 \(m=4,n=13\)，论文报告 \(T_{\text{NFSS}}=4199\)；拆成三个 sub-unit 后报告 \(T_{\text{proposed}}=1871\)，再按并行执行路径计为 \(T_{\text{proposed}}^{\text{parallel}}=669\)，并写出 \(669<1871<4199\)。[pdf:E04] 直觉不是改变矩阵求逆的基本代数，而是把一个 13 维问题换成多个 3 维左右的问题，并用并发路径而非总工作量衡量临界执行长度。

第三层是解除时间步内依赖。式 (15)–(18) 的共同形式可概括为

\[
U_{\text{internal}}(t+\Delta t)
=F\!\left(U_{\text{boundary}}(t),I_L(t),J_h(t),S(t),G\right),
\]

即不必等待本步所有外部/内部量顺序完成，便能借助相邻步连续量、当前开关状态和预先形成的小矩阵计算内部节点。[pdf:E05] 这正是速度来源，同时也是误差来源：EM2 比串行 EM1 多了一层基于前一步关系的并行化近似，论文也观察到 EM1 的精度略高于 EM2。[pdf:E06]

一个必须说明的数学问题是：论文正文称矩阵求逆负担随维数“exponentially”增加，但其自己的式 (8) 给的是 \(O(n^3)\)，属于三次多项式；而 \(O(3^3)\) 把常数矩阵规模写成渐近复杂度，也不能说明规模变化规律。[pdf:E03] [pdf:E04] 因此 4199、1871、669 可作为作者特定计数规则下的比较，不能直接当作普适复杂度证明。

## § 7 — 实验设计与结论

实验基准由 100 个 PVPGU 组成：10 个 cluster，每个 cluster 10 个单元，每个单元输出 1 MW，采用 P/Q controller；步长为 10 µs。DM 是 PSCAD/EMTDC 中的 detailed model，EM1 是直接用 NFSS 串行求解的 equivalent model，EM2 是 UDM 加 parallel framework 的 proposed model。[pdf:E05]

- **问题：故障暂态下等效模型是否跟得住详细模型？** 实验一在 0.4 s 施加持续 0.05 s、接地电阻 1 Ω 的三相接地故障；作者报告 EM1、EM2 对 DM 的 maximum relative error（MRE）均小于 0.5%，且 EM1 略准于 EM2。[pdf:E06] 实验二在 PCC 的 A 相于 0.6 s 施加同样持续时间和接地电阻的单相接地故障；作者报告 MRE 均小于 0.3%。[pdf:E06] 这回答了“所测短路场景是否保持主要波形”：在本文设置下是。
- **问题：环境输入突变是否仍能反映站内差异？** 实验三令 cluster 1–3 的 illumination intensity 在 0.8 s 附近降至接近零，整站 active power 因而下降 30 MW；作者展示 cluster 输出电流和站级功率、电压，并判断 EM1/EM2 与 DM 匹配。[pdf:E06] 本场景未报告明确 MRE，因此只能确认视觉波形一致性，不能给出精确误差上限。
- **问题：规模增大时是否更快？** 作者令仿真时长为 1 s、步长 10 µs，在 Intel i5-12600K 3.70 GHz、16 GB RAM 上改变 PVPGU 数量，比较 DM、EM1、EM2 的运行时间和 speedup。论文称 EM2 在 100 MW/100 PVPGU 时相对 DM 超过 150 倍，并且 SR2/SR1 随规模增大；单个 PVPGU 时多线程启动开销反而使 SR2/SR1 小于 1。[pdf:E06] [pdf:E07]

这些实验直接支持“在给定模型、步长、PC 和三类工况上更快且波形接近”。它们没有直接支持 real-time execution、跨平台可移植性、任意控制器/拓扑、长时数值稳定性或超过 100 MW 后仍保持同样误差；论文最后一句关于更大系统可直接扩展，是作者主张而非已展示实验。[pdf:E07]

## § 8 — Take-aways

### 5 句话

1. 论文把大型 PVPS EMT 的主要成本定位为单元内部大矩阵消元和 NFSS 时间步内的串行依赖。[pdf:E03]
2. UDM 沿 capacitor branch 将 17 节点 PVPGU 拆成三个 sub-unit，把一次 13 维逆矩阵替换为多次小矩阵求解。[pdf:E03]
3. parallel framework 借助电容电压、电感电流的相邻步连续性，并行求外部/内部节点和更新历史电流源。[pdf:E04] [pdf:E05]
4. 在 100 MW、100 PVPGU、10 µs 步长的三个测试场景中，作者报告关键故障 MRE 小于 0.5% 或 0.3%，并称 100 MW 时 speedup 超过 150。[pdf:E05] [pdf:E06] [pdf:E07]
5. 最重要的保留意见是：论文没有给实现代码、线程细节、长时稳定性或更广参数覆盖，其复杂度表述也混淆了运算计数与渐近复杂度。

### 3 句话

1. 这不是单纯“少建几个节点”，而是同时重构空间矩阵和时间步依赖。
2. 论文展示了很强的特定案例 speedup，并在三个短时工况上维持了与 DM 接近的波形。[pdf:E06]
3. 但能否稳定推广到更大系统和更强事件，仍取决于一步历史量近似的误差是否受控。

### 1 句话

本文用“按电容边界拆小矩阵 + 用相邻步连续性打散串行链”换取大型光伏 EMT 的显著加速，但其可推广性仍需要围绕误差累积和真实并行实现来验证。

## § 9 — 最脆弱的假设

最脆弱的假设是：**用相邻时间步的 capacitor port voltage、inductor branch current 和边界节点量，足以在并行回算内部节点时代表当前步耦合，而且这种一步滞后误差不会在强开关事件或长时间推进中累积成显著偏差。** 这是 parallel framework 能解除依赖的必要条件；若必须等待当前步精确外部量再回算内部节点，流程就退回高度串行的 NFSS，核心速度收益会直接缩水。[pdf:E05]

论文给出的正面证据是：在 10 µs 步长、2 kHz converter operation frequency、两类接地故障和一次辐照突变下，EM2 波形仍接近 DM，故障 MRE 分别小于 0.5% 和 0.3%。[pdf:E05] [pdf:E06] 反面信号是作者明确说 EM1 精度略高于 EM2，说明并行化并非零代价。[pdf:E06]

缺失证据包括：误差随步长、开关频率、弱阻尼参数和仿真时长的变化；切换瞬间的局部误差峰值；数值稳定性界；不同分区边界的敏感性；多线程同步和 floating-point reduction 顺序。另一个证据断点是摘要宣称 accuracy less than 1.8%，但正文明确写出的两个故障 MRE 是 0.5% 与 0.3%，辐照场景又没有给 MRE；PDF 没有解释 1.8% 对应哪个变量或统计范围。[pdf:E01] [pdf:E06]

## § 10 — 最小复现实验

一周内最值得复现的不是整座 100 MW 电站，而是“并行回算是否在扩大步长和增强开关扰动时仍受控”。

- **数据与模型：** 按图 4 重建一个 PVPGU 的 17 节点离散网络，使用 Table II 中公开的 converter、line、transformer 和 control parameters；生成与论文一致的 2 kHz 三相开关函数，并使用 10 µs 为基准步长。[pdf:E03] [pdf:E05]
- **实现：** 做两个求解器。基准求解器每步直接解完整 nodal equation；候选求解器按图 5 拆成三个 sub-unit，执行式 (14)–(18) 的历史源更新和内部节点回算。[pdf:E03] [pdf:E04] [pdf:E05] 不需要先复现 100 个单元，也不需要 PSCAD GUI。
- **工况：** 复现论文的三相接地故障时序，并额外扫描 \(\Delta t=5,10,20,40\ \mu s\) 与开关相位，使故障起点分别落在开关前、开关时刻和开关后。[pdf:E06]
- **测量：** 比较 PCC voltage、PVPGU active power、各 sub-unit 内部 node voltage 的 peak error、RMS error、MRE 和 1 s 仿真 wall-clock time；同时画出误差是否随时间累计。
- **支持标准：** 10 µs 下关键波形 MRE 不高于论文报告的 0.5% 量级，且候选求解器的临界路径时间显著低于完整求解；扩大到 20 µs 时不出现误差发散。
- **反驳标准：** 误差在开关/故障重合时出现持续偏置或随时间增长，或者去除线程启动开销后候选求解器没有稳定速度优势。

论文没有公开源码、完整控制逻辑和所有初始条件，因此这会是“机制复现”，不是声称逐点重现作者 Fig. 11–15。

## § 11 — 最强反例设计

最强反例应让“相邻步连续性可安全解除依赖”失效，而不只是换一台更慢的电脑。可以构造一个弱阻尼、强耦合的 PVPGU：在 converter switching edge 与 PCC fault inception 同一时间步发生时，同时施加 irradiance step，并把 \(\Delta t\) 从 10 µs 逐步放大；对每个设置运行 DM、串行 EM1 和 EM2，持续足够多的开关周期。[pdf:E05] [pdf:E06]

攻击判据不是某一瞬间有轻微尖峰，而是出现以下任一项：EM2 的内部 node voltage error 随时间积累而 EM1 不积累；EM2 改变 fault recovery damping/phase；或者为维持误差上限不得不把步长缩小到抵消并行 speedup。若出现这种结果，替代解释将是：论文的加速主要来自用历史量替代当前耦合，而非单纯来自“等价的并行重排”；速度和精度之间存在论文尚未量化的交换。

这个反例比“只测更多拓扑”更有力，因为它正面攻击核心依赖解除条件。相反，如果 EM2 在步长、开关相位、耦合强度和长时运行的系统扫描中都保持 bounded error，那么论文的主张会比现有三个短场景更可信。

## § 12 — Follow-up Research Idea

**领域评价判断：** 对 EMT 与 power electronics simulation，高影响结果通常不仅看单个 speedup 数字，还看误差可解释性、跨工况稳定性、可复现实现、规模扩展和与真实实时/HIL 计算约束的对应。本文在 speedup 和特定波形精度上给了初步证据，但没有给“何时可以安全并行”的判据。

**候选研究想法：误差预算驱动的动态因果分区。** 不再预先固定“capacitor branch 永远是边界”，而是在每个时间窗估计 sub-unit 间当前耦合强度与一步滞后误差上界：低风险区继续用 UDM parallel update，高风险开关/故障窗口临时合并分区或恢复局部同步。它改变的问题定义——从“如何把固定模型算得更快”变为“如何在给定误差预算下自动选择依赖图”。

- **(a) 未满足需求：** 当前方法没有告诉使用者，换步长、控制参数或事件强度后 EM2 何时失真；只能事后与 DM 比较。
- **(b) 潜在研究价值：** 若能给出在线、可验证的 error budget，使用者可在速度与可信度之间做显式选择，并把方法推广到论文未验证的更大站或更复杂事件，而不是依赖一次性经验分区。
- **(c) 可借鉴工具：** 候选上可借鉴 adaptive time stepping、graph partitioning 与 waveform relaxation 的误差/耦合监测思想；这里仅是方向性连接，未做相关工作检索，不声称 novelty。
- **(d) 第一个证伪实验：** 对 § 11 的开关-故障重合扫描，比较固定 UDM、全同步基准和动态分区。如果动态法不能在相同 MRE 上降低 wall-clock time，或其风险指标不能提前识别误差峰值，想法即被否证。
- **(e) 与本文的实质区别：** 本文固定选 capacitor branch 并用历史量持续并行；候选方法把“分不分、何时同步”本身变成受误差预算约束的在线决策。

这个想法建立在本文已经暴露的最脆弱假设上，而不是给 UDM 再叠一个应用模块。它是否已有等价工作，需要单独做文献检索后才能判断。
