# Real-Time Simulation-Based Multisolver Decoupling Technique for Complex Power-Electronics Circuits

Luc-André Grégoire、Handy Fortin Blanchette、Jean Bélanger、Kamal Al-Haddad；*IEEE Transactions on Power Delivery*，Vol. 31, No. 5，2016；DOI：10.1109/TPWRD.2016.2565512；Zotero key：TWTFXPGE。

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是一般意义上的“把电路算快一点”，而是一个有硬截止时间的实时仿真问题：每个固定步长内必须完成输入采样、模型计算和输出更新，否则仿真就无法与外部控制器或功率硬件同步。作者以 50 μs 步长为例说明，三段工作必须全部塞进这 50 μs；如果单核算不完，只能增大步长而牺牲精度/稳定性，或把模型分给多个处理器，而后一条路又要求各分区在同一步内没有循环数据依赖。[pdf:E02]

困难在于，大型电力电子电路同时含有快慢悬殊的动态、开关不连续性和强耦合状态。经典网络撕裂往往依赖传输延时或人为增加状态；这对短线路和紧凑变换器并不自然，还可能引入数值振荡。本文试图找到一种“只改变少数接口状态的离散方式，就让两个子电路能并行前进”的方法，同时保留固定步长、单步求解和全系统稳定性分析能力。作者把贡献概括为：同一状态空间模型中的不同状态使用不同 ODE 离散器，以 implicit/explicit solver 的互补性解耦，不加人工延时或附加状态，并可嵌入商业仿真软件。[pdf:E01]

其工程价值在于把“实时性、稳定性、精度”从三选二变成可联合检查的问题。若方法成立，复杂模型可以沿少数接口分区，把每个分区交给不同计算核，同时仍用全局离散极点预判稳定性；这正是 controller-HIL、power-HIL 和大规模 EMT 实时仿真的关键能力。[pdf:E04][pdf:E08]

## § 2 — 前人工作与不足

作者在引言中给出的 prior-work 图景有四层。第一，Bergeron distributed-parameter line 用物理传播延时天然解耦远距离网络，但短线路传播时间小于仿真步长时不适用；强行凑成一个步长会给原本主要是感性的线路并联寄生电容，形成 stubline。[pdf:E01] 第二，在 DC bus 电容等慢状态上人为加一拍延时能撕裂网络，却可能导致数值不稳定。[pdf:E01]

第三，已有方法用 BE 求各子电路、FE 求接口状态，并在每一步迭代、必要时缩小步长直到收敛。这在离线计算中可接受，却与实时仿真的确定性执行时间冲突。[pdf:E01] 第四，latency-based multisolver 或 state-space/nodal tearing 已能按局部 solver 分区，并用受控源和等效阻抗连接，但前者需要中间时刻更新，使有效步长约减半；后者每一步还要先求局部子电路，再求全局 nodal solution，仍是两阶段计算。[pdf:E01]

因此本文瞄准的缺口很具体：不用额外物理/寄生状态、不做迭代、不插入中间半步，也能形成单步并行执行；而且稳定性检查不能只看各子系统，必须能重建整个离散闭环的极点。[pdf:E01][pdf:E04] 这里的“前人不足”是作者在本文引言中的归纳，并非本卡对所有相关工作的独立复核。

## § 3 — 重建作者的思考路径

可以从实时执行约束反推这条路线。第一，实时仿真的并行核之间只能稳定地交换上一拍结果：若 core 2 在当前拍需要 core 1 的当前拍输出，就形成顺序依赖，无法并行。[pdf:E02] 第二，传统加延时虽然把“当前值”变成“上一拍值”，却会改动物理模型；因此应寻找一种不添元件、只改离散依赖方向的办法。[pdf:E01]

第三，FE 本来就是 explicit：下一状态由上一拍状态与输入给出；BE 是 implicit：当前输入进入当前拍方程，但数值耗散更强。两者的 local truncation error（局部截断误差）同为二阶量级且符号相反，而 TR 为三阶量级、精度通常更高。[pdf:E02] 于是自然出现一个研究假设：让接口的一侧使用 FE，把跨分区依赖推迟到上一拍；让相邻的快状态使用 BE，以额外阻尼压住 FE 的欠阻尼倾向；其余状态继续用 TR 保精度。

第四，仅靠直觉配 solver 不够。可先由连续状态空间估算各状态的二阶导数，用它找最快状态；再优先选择依赖关系少、轻耦合的接口；最后把得到的离散递推式重新组装成全局矩阵，用极点而不是局部波形“看起来没炸”来检查稳定性和近似误差。[pdf:E03][pdf:E04] 这条路径不以本文最终结果为前提，而是由 hard real-time、explicit/implicit 数据依赖与已知数值耗散特性逐步推出。

## § 4 — 核心 Intuition

核心直觉是：解耦不一定要给电路增加一拍物理延时，也可以让接口两侧的状态采用不同离散器，从代数上把跨核依赖变成上一拍数据。[pdf:E03] 把 BE 放在变化最快的状态上提供阻尼，把 FE 放在相邻且较慢、轻耦合的状态上切断当前拍依赖，其余状态用 TR 保持精度。[pdf:E02][pdf:E03] 这样得到的两个子电路可在同一仿真步并行执行，再用完整离散矩阵的极点检查是否付出了不可接受的稳定性或精度代价。[pdf:E04]

## § 5 — 具体方法与完整 Pipeline

以论文的 grid-connected inverter + LCL filter 为例，输入是连续状态空间模型、固定步长和候选分区，输出是两个能并行执行的离散子模型及其接口 companion model。

1. **建立连续模型并找候选接口。** 把整体模型写成网络 1、接口/传输段、网络 2 三组状态；优先考察只在端点连接、对其他状态依赖少的轻耦合变量。论文指出传输线或类似局部连接元件通常适合作为切点。[pdf:E03][pdf:E04]
2. **按状态选择 solver。** 用连续模型的稳态状态和输入估算二阶导数。论文例子中，$v_{C2}$ 的二阶导数绝对值最大，因此给它用 BE；相邻的 $i_{L1}$ 用 FE；剩余的 $v_{C1}$、$i_{L2}$ 用 TR。[pdf:E05]
3. **对每条状态方程分别做 operational substitution。** 也就是不再对整个模型统一替换 $s$，而是按状态分别代入 FE、BE 或 TR 的 $z$ 域近似，然后把带 $z$ 的未来状态隔离出来。[pdf:E02][pdf:E03]
4. **把跨分区当前拍依赖消掉。** FE 侧只读取 $n-1$ 拍数据；BE/TR 侧可以读取本分区当前输入。论文将网络 1 与 $i_{L1}$ 放在一个 core，网络 2 与 $v_{C2}$ 放在另一个 core，两边只交换上一拍接口状态，因而能同拍并行。[pdf:E05][pdf:E06]
5. **用 companion model 接回商业仿真软件。** 电流接口用“受控电流源 + 等效电阻”，电压接口用“受控电压源 + 等效电阻”；等效阻抗/导纳直接来自离散矩阵。论文给出了两种模型及其 Eq. (22)、(23)。[pdf:E05]
6. **组装全局离散系统并预检极点。** 将各商业软件生成的子系统矩阵与接口矩阵组合，求完整离散状态矩阵；所有极点在单位圆内才算稳定，并与由连续极点映射得到的 reference poles 比较精度。[pdf:E04]
7. **固定步长执行并与基线比较。** 论文在 MATLAB/Simulink 与 SimPowerSystems 中，以未解耦模型为 reference，对 proposed method 和两种 stubline 撕裂进行稳态与短路故障比较。[pdf:E05][pdf:E06][pdf:E07]

论文没有报告 FPGA RTL、定点位宽、DSP/BRAM 使用量、pipeline latency、资源占用或板上时序；实际执行平台只落实到 multicore/商业实时仿真软件层面。HIL/PHIL 是作者提出的可应用方向，不是本文完成的硬件实验。[pdf:E08]

## § 6 — 核心数学推导

先看离散器的物理含义。精确采样关系为

$$
s=\frac{\ln z}{T},
$$

其中 $T$ 是 integration time-step，$z$ 表示向前一个离散步。论文用 operational substitution 将它近似为

$$
s_{\mathrm{FE}}=\frac{z-1}{T},\qquad
s_{\mathrm{TR}}=\frac{2}{T}\frac{z-1}{z+1},\qquad
s_{\mathrm{BE}}=\frac{1}{T}\frac{z-1}{z}.
$$

这些分别是 Eq. (1)–(4)。[pdf:E02] 对应 LTE 为

$$
\mathrm{LTE}_{\mathrm{FE}}=\frac{1}{2}T^2\ddot{x}_{\mathrm{FE}}+O(T^3),\quad
\mathrm{LTE}_{\mathrm{TR}}=\frac{1}{6}T^3\dddot{x}_{\mathrm{TR}}+O(T^4),\quad
\mathrm{LTE}_{\mathrm{BE}}=-\frac{1}{2}T^2\ddot{x}_{\mathrm{BE}}+O(T^3).
$$

FE 与 BE 的主误差同阶、符号相反，工程上分别表现为欠阻尼与过阻尼；TR 的主误差高一阶，所以通常更准。这不是说两种 Euler 误差会自动严格抵消，而是说明把 BE 放到最快状态可让主导误差偏向阻尼，而不是偏向放大振荡。[pdf:E02]

对二阶连续系统 $\dot X=A X+B U$，作者让 $x_1$ 用 FE、$x_2$ 用 BE。整理 Eq. (9)–(12) 后，$x_1[n]$ 的递推只含上一拍 $x_1,x_2,u$；$x_2[n]$ 可含当前拍输入 $u[n]$，但不需要另一 core 的当前拍状态。因此两条状态递推可以并行，条件是当前输入与 BE 状态留在同一 core。[pdf:E03] 这就是算法最关键的“代数撕裂”：并没有给连续电路新增延时元件，却改变了离散方程的跨分区数据依赖。

solver 选择来自

$$
\ddot X=A\dot X+B\dot U \approx A(AX+BU)=AAX+ABU,
$$

即 Eq. (14)。近似号隐含 $\dot U=0$，也就是输入相对状态动态变化较慢；用名义稳态 $X,U$ 算出的最大 $|\ddot x_i|$ 指示最快状态，给它 BE，再给相邻且较慢状态 FE。[pdf:E03] 在 LCL 例子中，Eq. (25) 得到的四个二阶导数量级为 $-3.76\times10^6$、$-12.16\times10^6$、$1.16\times10^9$、$55.56\times10^3$，所以 $v_{C2}$ 被判为最快状态。[pdf:E05]

对于大网络，作者将当前拍项写成

$$
X_n=A^{d1}X_{n-1}+A^{d2}X_n+B^{d1}U_{n-1}+B^{d2}U_n,
$$

移项后，真正决定离散极点的状态矩阵是

$$
A_d=(I-A^{d2})^{-1}A^{d1}.
$$

连续 reference pole $\lambda_s^{\mathrm{ref}}$ 则映射为 $\lambda_z^{\mathrm{ref}}=e^{\lambda_s^{\mathrm{ref}}T}$。因此 $| \lambda(A_d) |<1$ 检查稳定性，与 $\lambda_z^{\mathrm{ref}}$ 的距离检查离散精度；这分别对应 Eq. (20)、(21)。[pdf:E04] 该分析把被商业软件内部离散的子模型也纳入一个全局极点检查，但前提是能取得 Eq. (16)、(18) 所需的离散矩阵。

## § 7 — 实验设计与结论

**问题 1：解耦后是否仍全局稳定，而且不会像 stubline 那样引入寄生振荡模态？** → 作者构造 4 状态 grid-connected inverter + LCL filter，采样时间 10 μs、开关频率 5 kHz，参数包括 100 V、5 kVA、$C_1=2$ mF、$L_1=3.5$ mH、$C_2=15$ μF、$L_2=1.5$ mH；比较未解耦 reference、proposed method、以 $L_1$ 为 stubline、以 $C_2$ 为 stubline 四种模型，并先求极点。[pdf:E06] → proposed method 的两对极点为 $0.9956\pm j0.0795$、$0.9993\pm j0.0031$，均在单位圆内且接近 reference；两种 stubline 各多一个接近 $-1$ 的极点 $-0.9997$、$-0.9999$，预示高频数值振荡。[pdf:E06]

**问题 2：稳态波形是否保持准确？** → 作者采用 open-loop 控制，避免 controller 把离散误差补掉；对 $v_{C1}$、$i_{L1}$、$v_{C2}$、$i_{L2}$ 逐一计算相对 reference 的误差。[pdf:E06][pdf:E07] → $v_{C1}$ 与 $i_{L2}$ 在三种解耦方案中都小于 1%；$i_{L1}$ 峰值相对误差分别约为 proposed 1%、$L_1$ stubline 3%、$C_2$ stubline 0.1%。最显著区别出现在 $v_{C2}$：$C_2$ stubline 因数值振荡达到 35%，proposed 与另一 stubline 约为 5% 和 2%；作者据此认为 proposed method 在三种实现中总体误差最小。[pdf:E07]

**问题 3：故障瞬态下是否仍能工作？** → 在 $C_2$ 处施加持续半个周波的短路，比较 $i_{L1}$ 与 $v_{C2}$ 及其相对误差。[pdf:E07][pdf:E08] → proposed method 因 BE 更强的数值阻尼，在故障初期的相对误差看起来更大，但 $v_{C2}$ 约一个周波回到稳态，另外两种方法需数个周波；最终误差回到稳态水平，而且没有 stubline 的寄生状态与相应数值振荡。[pdf:E07][pdf:E08]

**问题 4：是否已证明大型模型的实时加速和硬件可实现性？** → 本文没有给出 wall-clock execution time、deadline miss、CPU utilization、core-to-core communication latency、数百状态规模测试，也没有 FPGA/HIL 实机资源和时序数据。→ 所以实验支持“该离散撕裂在一个 4 状态开关电路例子中稳定且精度可接受”，却没有直接支持摘要中“数百状态可轻松实时仿真”的性能幅度，也不能外推到 FPGA 映射、强耦合网络或 multirate 系统。[pdf:E01][pdf:E06][pdf:E08]

## § 8 — Take-aways

**5 句话。** 这篇论文把网络解耦重新表述为“每个状态如何离散”的问题，而不是“给物理网络哪里加延时”的问题。[pdf:E03] FE 负责把跨分区依赖推到上一拍，BE 负责给最快状态增加数值阻尼，TR 留给其余状态保精度。[pdf:E02][pdf:E03] 完整离散矩阵和连续极点映射使作者能在跑波形前检查全局稳定性与近似精度。[pdf:E04] 在 10 μs 的 LCL inverter 例子中，方法避免了 stubline 接近 $-1$ 的寄生极点，并在稳态和半周波短路下给出可接受结果。[pdf:E06][pdf:E07][pdf:E08] 但论文验证的是数值可行性，不是大规模实时加速、FPGA 实现或自动 solver/切点选择的完成证据。

**3 句话。** 作者用混合离散器制造单步并行所需的数据依赖方向，同时不添加寄生状态。[pdf:E03] 其可信之处是有全局极点分析和故障波形，局限是只有一个小型例子且缺少真实执行时间。[pdf:E06][pdf:E08] 对后续 EMT/FPGA 工作，最值得继承的是“分区决策必须同时带稳定性证书和 deadline 证据”，而不是只复刻 FE/BE 组合。

**1 句话。** 这是一种用离散器选择代替人工延时的网络撕裂方法，证明了小型开关电路中的数值潜力，但尚未证明其大规模实时和 FPGA 工程收益。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**用名义稳态值并令 $\dot U\approx0$ 算出的 $|\ddot x|$ 排序，足以在开关、故障和工况变化期间持续找对“BE 最快状态 + FE 相邻轻耦合状态”的接口。** 这是 Eq. (14) 到 solver 选择的关键桥梁；若排序在真实瞬态中翻转，FE 可能落到实际最快或强耦合的状态上，其欠阻尼误差就不再被 BE 安全压住，跨分区一拍数据依赖也可能显著改变主导模态。[pdf:E03]

论文给出的支持是：在一个 $d\in\{-1,0,1\}$ 的 inverter/LCL 模型中按名义 RMS 选择 $v_{C2}$ 用 BE、$i_{L1}$ 用 FE，并通过全局极点、稳态波形和 $C_2$ 半周波短路观察到稳定结果。[pdf:E05][pdf:E06][pdf:E07] 缺失的是 operating-point sweep、参数不确定性、grid impedance 变化、不同 switching sequence、强耦合切点和 multirate 情况；作者也明确承认切点与 solver 仍需人工选择，并把 multirate 留作 future work。[pdf:E08] 因此，基于证据的判断是：论文证明了一个选择结果可行，却没有证明这条选择规则在目标应用域内具有鲁棒性。

## § 10 — 最小复现实验

一周内最小复现不需要搭完整实时平台，可以直接重建论文 Eq. (24) 的 4 状态 LCL 模型。

1. 使用 Table I 的 100 V、5 kVA、5 kHz switching、10 μs step 及 RLC 参数，建立未解耦高精度 reference；用 open-loop modulation，避免控制器掩盖离散误差。[pdf:E05][pdf:E06]
2. 实现 proposed 离散：$v_{C2}$ 用 BE、$i_{L1}$ 用 FE、$v_{C1}$ 与 $i_{L2}$ 用 TR，并按 Eq. (26)–(29) 组装递推矩阵；只做这一种解耦和 reference，就足以验证核心 claim。[pdf:E05][pdf:E06]
3. 先测 $A_d$ 全部极点的模是否小于 1，并比较 $e^{\lambda_sT}$；再跑稳态和 $C_2$ 半周波短路，记录四个状态的 peak/RMS relative error、故障后 settling time 和每步最坏计算时间。[pdf:E04][pdf:E07][pdf:E08]
4. **支持标准：** 极点留在单位圆内；proposed 不出现接近 Nyquist 的持续数值振荡；稳态误差大致复现 $v_{C1},i_{L2}<1\%$、$i_{L1}$ 峰值约 1%、$v_{C2}$ 峰值约 5% 的量级；故障后 $v_{C2}$ 约一周波收敛；最坏计算时间低于 10 μs。[pdf:E07][pdf:E08]
5. **反驳标准：** 任一工况出现 $|\lambda|\ge1$、持续寄生振荡、误差显著超过论文以实时仿真为目标时援引的 5% 可接受范围，或计算 deadline 无法满足。[pdf:E08]

前四项复现论文的数值主张；加入“每步最坏计算时间”是本卡为验证真实实时性补上的验收，不是论文已经报告的结果。

## § 11 — 最强反例设计

最有力的攻击不是再换一个更大的电路，而是构造一个**每个冻结开关状态单独看都稳定，但开关序列组合后不稳定**的 LCL/grid-impedance 工况。具体做法是保留论文的接口和 10 μs 步长，对 $L_1,C_2$、grid impedance、开关占空序列和输入斜率做约束搜索；solver 仍只按名义 RMS 与 $\dot U=0$ 选一次，然后对每个开关状态形成离散矩阵，搜索其矩阵乘积（一个 switching period 的 monodromy matrix）是否出现谱半径大于 1。论文当前的选择依据和故障验证分别位于 Eq. (14)/(25) 与单个半周波短路场景。[pdf:E03][pdf:E05][pdf:E07]

若能找到这样的序列，就会给出一个直接替代解释：单工况 frozen-pole 稳定并不等于 hybrid switched system 稳定，论文例子的成功可能来自所选调制与参数，而非 FE/BE 配对的一般稳定性。随后在 double precision 离线模型和 real-time target 上复现同一发散/极限环，并与统一 TR reference 对照；若 reference 稳定而 multisolver 发散，就直接击中核心机制，而不是仅说明实现较慢。反过来，若在广泛参数域和 switching sequence 下都找不到此反例，才会显著增强方法的鲁棒性证据。

## § 12 — Follow-up Research Idea

**候选方向：面向 hybrid multirate EMT 的“可证伪稳定分区”——把 solver/切点选择从名义点启发式，改写为对开关序列、参数不确定性和 deadline 同时成立的 certificate synthesis 问题。** 这不是简单地把人工规则自动化，而是改变目标：输出不再只是一个分区，而是“分区 + 允许工况域 + switched-system 稳定性证书 + worst-case execution-time 证书”。论文自己指出当前选择仍需人工介入，并把不同状态采用不同步长的 multirate 系统留作后续挑战。[pdf:E08]

（a）未满足需求是：电力电子实时仿真不能只在一个名义点数值稳定，还要在拓扑切换、故障、参数漂移和多速率交互下不越过稳定与 deadline 边界。（b）在 power delivery/EMT 领域，高影响价值应来自可复现的大规模模型、严格稳定性论证、实际实时/HIL 平台上的精度与延迟，而不是仅增加一个求解器变体。（c）可借鉴 switched-system control 的 common/multiple Lyapunov function、joint spectral radius，上层再结合 graph partitioning 与 worst-case execution-time analysis；FPGA 场景还应把定点误差和 pipeline latency 纳入证书。（d）第一个证伪实验就是第 11 节的 switching-sequence 搜索：若证书判定安全的参数盒内仍出现 monodromy spectral radius 大于 1、HIL 波形发散或 deadline miss，方向即被反驳。（e）它与本文的实质区别是从“按二阶导数选择 FE/BE 后再算一个全局极点”升级为“对一族混杂、多速率、有限字长实现联合给出可检查的安全域”。

由于本卡没有对 2016 年后的相关工作做系统检索，这只是由本文证据约束出的候选研究想法，不声称 novelty。
