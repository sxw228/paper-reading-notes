# Closed-Loop Interconnected Model of Multi-Inverter-Paralleled System and Its Application to Impact Assessment of Interactions on Damping Characteristics

作者：Shuhan Liao, Yandong Chen, Wenhua Wu, Lei Wang, Qianming Xu  
出处：IEEE Transactions on Smart Grid, Vol. 14, No. 1, pp. 41–53  
年份：2022（online publication；卷期标注为 January 2023）  
DOI：10.1109/TSG.2022.3194148  
Zotero key：M3DQ26J6  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个很具体的容量扩展问题：当风电场或其他 inverter-based distributed generation 在非理想电网中新增一台或一组并网逆变器时，新旧逆变器通过 PCC 电压相互影响，新增集电线长度如何改变整个并联系统的中频阻尼？作者要解决的并非“某组参数下系统是否稳定”这一单次判定，而是如何量化原系统与新增逆变器的 interaction degree，并从大量不同参数的并联系统中提取可复用的阻尼规律。论文直接声称，新增线长接近任一既有线长时，中频阻尼会变差；规避办法是拉开线长，或重新整定逆变器控制参数。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，因为在非零电网阻抗下，一台逆变器的电流扰动会改变总并网电流和 PCC 电压，而 PCC 电压又反馈到其他逆变器。于是，多机系统不再是若干单机模型的简单叠加；单机稳定也不保证并联后的 interaction mode 有足够阻尼。论文把这一工程风险放在风电场扩容背景下：集电线路长度通常受能量损耗、基础设施成本和场站布局支配，但传统布局优化并未把并联系统小信号稳定性作为主要约束。[pdf:E09]（PDF 物理页 9，Section III-D）

本文的价值有两层。第一层是分析价值：把“原系统”和“新增逆变器”写成两个闭环互联系统，通过开环子系统与闭环整体的 eigenvalue 位移度量相互作用。第二层是设计价值：把模态变化进一步压缩为一条可操作的扩容规则，并给出调整 current controller 比例系数 \(k_{pi}\) 的补救路径。这里的“开环子系统”是论文自己的分区术语，子系统内部仍含 dc-voltage loop、current loop 和 PLL，并不是把控制器本身开环。[pdf:E04]（PDF 物理页 4，Fig. 4–Fig. 8 与 Section II-B）

## § 2 — 前人工作与不足

论文对前人工作的划分如下。对于参数完全相同的并联逆变器，state-space model 与 impedance-based model 已得到一致结论：系统可分为互相解耦的 internal stability 和 external stability；内部稳定性只受逆变器参数影响，外部稳定性还受到逆变器数量的 multiplication effect 影响。对称性允许把系统化成等效电路，因此可以提取一般规律。已有 closed-loop interconnected modeling 也曾用于风机与含同步机外部电网的强动态交互，以及单机中 PLL 与交流电流控制的耦合分析。[pdf:E02]（PDF 物理页 2，Table I 与 Introduction）

不足出现在 differently parameterized inverters。实际风场的集电线长度不完全相同，系统失去对称性后，详细 state-space root locus 或 impedance Bode diagram 仍能判断某一个具体系统，但难以直接给出“参数怎样变化会普遍把阻尼推向何处”的机制性结论。作者因此认为，既有方法要么依赖 trial-and-error，要么能显示稳定性变化却不能量化两个子系统的 interaction degree。论文将“用闭环互联模型同时量化交互强度并提取阻尼一般规律”列为自己的贡献；这是论文原文的 novelty claim，本卡未做外部检索，不能把它提升为独立验证过的首创结论。[pdf:E02]（PDF 物理页 2，Table I 与 Introduction）

还要限定“前人不足”的边界：论文并未证明 state-space 或 impedance 方法在异构多机系统中原则上不能产生一般结论；它证明的是作者所构造的闭环互联分区能把关注对象映射为开环—闭环 eigenvalue 对，从而更直接地解释容量扩展场景。因而合理的说法是“原有详细模型不便于提取本文所需规律”，而不是“原有方法无法分析该系统”。

## § 3 — 重建作者的思考路径

以下是基于论文背景与方法组织方式的合理重建，不是作者逐字陈述。

1. 对称的同参数并联系统之所以容易分析，是因为可以识别 internal mode 和 external mode；真正棘手的是线路、控制器或运行点不同后，这种对称分解不再直接可用。
2. 容量扩展天然提供了一个有物理含义的切口：把已有风场连同电网视为 subsystem A，把新装逆变器视为 subsystem B。二者交换的恰好是 PCC voltage 与新增逆变器 line current，而不是人为挑选的抽象状态。[pdf:E03]（PDF 物理页 3，Fig. 1–Fig. 3）
3. 若强制令新增逆变器电流扰动为零，A 看见的是 constant current source；若强制令 PCC 电压扰动为零，B 看见的是 constant voltage source。这样就能得到两个“无相互作用”的参照系统，再把它们闭环连接，观察 eigenvalue 从 \(\lambda_A,\lambda_B\) 移到 \(\hat{\lambda}_A,\hat{\lambda}_B\) 的距离。[pdf:E05]（PDF 物理页 5，Section II-C）
4. 先在两逆变器系统中扫描新增线长，找出闭环模态轨迹的转向点；再利用交换两条线路后闭环 eigenvalue 不变这一对称关系做 sensitivity analysis；最后把同线长逆变器间的 internal pole 关系推广到多逆变器系统。
5. 若中频模态的 participation factor 主要落在 current controller 状态上，那么除改变集电线路外，还能通过 \(k_{pi}\) 把模态左移，形成第二条工程补救路径。[pdf:E09]（PDF 物理页 9，Fig. 13–Fig. 14）

这一路径的关键不是发明新的逆变器控制器，而是改变“如何观察交互”的坐标系：从整个高阶系统的一组无来源区分的极点，转到“原系统极点、新增设备极点以及闭环后各自移动了多少”。

## § 4 — 核心 Intuition

把扩容前系统与新增逆变器暂时断开动态反馈，可以得到各自的基准 eigenvalue；重新闭环后，极点位移就是 interaction 对阻尼的影响。若新旧逆变器除线长外相同，线长相等会形成最强的内部模态匹配，使中频闭环极点最容易靠近甚至越过虚轴；拉开线长或增大 current controller 的 \(k_{pi}\) 可以把这一模态向左推。这个 intuition 的物理链条是“电流扰动 → PCC 电压扰动 → 另一子系统电流响应 → 原扰动”，而不是线长本身直接产生不稳定。

## § 5 — 具体方法与完整 Pipeline

以“已有 #1 inverter，新增 #2 inverter”为例，作者的方法可以还原为以下 pipeline。

1. **输入与边界。** 每台装置是 L-filtered two-level inverter，经升压变压器和集电线接到 PCC；电网外部用 Thevenin 电压源 \(v_g\) 与阻抗 \(Z_g\) 表示。作者假设关注的逆变器动态快于风速、光照和环境温度变化，因此把 dc-link 输入功率视为常数，并采用 VOC：dc-link voltage loop、current loop、PLL 与 PWM 构成控制链。[pdf:E03]（PDF 物理页 3，Fig. 1–Fig. 3 与 Section II-A）
2. **系统分区。** subsystem A 包含原有逆变器与非理想电网，subsystem B 包含新增逆变器。B 的输出/ A 的输入是新增逆变器 line-current perturbation \(\Delta\mathbf i_{xy2}\)；A 的输出/ B 的输入是 PCC-voltage perturbation \(\Delta\mathbf v_{pxy}\)。二者在 PCC 形成闭环。[pdf:E04]（PDF 物理页 4，Fig. 4–Fig. 5）
3. **建立传递函数。** 总电流满足 \(\Delta\mathbf i_{gxy}=\Delta\mathbf i_{xy1}+\Delta\mathbf i_{xy2}\)（Eq. 1）；无 grid-voltage perturbation 时，\(\Delta\mathbf v_{pxy}=\mathbf Z_g(s)\Delta\mathbf i_{gxy}\)（Eq. 3）；第 \(i\) 台逆变器由 \(\mathbf Y_i(s)=\Delta\mathbf i_{xyi}/\Delta\mathbf v_{pxy}\) 表示（Eq. 4）。由此得到 \(\mathbf G_A(s)=[\mathbf I-\mathbf Z_g\mathbf Y_1]^{-1}\mathbf Z_g\)、\(\mathbf G_B(s)=\mathbf Y_2(s)\)，以及整体 \(\mathbf G(s)=\mathbf Y_2(s)[\mathbf I-\mathbf Z_g\mathbf Y_1-\mathbf Z_g\mathbf Y_2]^{-1}\)（Eq. 5–7）。[pdf:E04]（PDF 物理页 4，Eq. 1–Eq. 7）
4. **构造无交互基准。** 令 \(\Delta\mathbf i_{xy2}=0\)，用 steady-state constant current source 替换 B，得到 open-loop subsystem A；令 \(\Delta\mathbf v_{pxy}=0\)，用 steady-state constant voltage source 替换 A，得到 open-loop subsystem B。这里“open-loop”只表示两个分区之间的动态通路被切断。
5. **匹配模态并量化交互。** 将闭环 eigenvalue 与 A、B 的开环 eigenvalue 配对，用 \(\Delta\lambda_{Ai}=\hat{\lambda}_{Ai}-\lambda_{Ai}\) 和 \(\Delta\lambda_{Bi}=\hat{\lambda}_{Bi}-\lambda_{Bi}\) 分别表示 B 对 A、A 对 B 的交互影响，再比较开环与闭环极点的实部或 damping。[pdf:E05]（PDF 物理页 5，Eq. 8–Eq. 9 与 application Step 1–Step 6）
6. **扫参与推广。** 固定既有线长 \(l_A\)，扫描新增线长 \(l_B\)，观察中频模态；在二机结果上做 sensitivity analysis，再推广到 \(n+1\) 台并联系统。
7. **输出。** 输出不是一个新的实时控制信号，而是 interaction degree、最危险的线长关系，以及“改变线长/增大 \(k_{pi}\)”两类规划和整定建议。

EMT 与 FPGA 边界必须说清：论文报告的是 continuous-time small-signal transfer-function/eigenvalue analysis 与 nonlinear time-domain simulation。虽然系统图含 two-level inverter 和 PWM，但正文没有报告开关级还是 averaged switching model、离散化方法、事件处理、数值求解器、仿真步长、多速率调度、计算依赖、并行方案、定点数值表示、FPGA 映射、逻辑资源、时序收敛、实时步长或实际硬件平台。因此本论文不能作为 EMT 实时仿真精度或 FPGA 可实现性的证据。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从物理互联到闭环传递函数

最基础的三步是 KCL、网侧阻抗和逆变器 admittance。KCL 给出 Eq. (1)；网侧 impedance matrix \(\mathbf Z_g(s)\) 把总电流扰动变成 PCC 电压扰动；每台逆变器的 \(\mathbf Y_i(s)\) 又把 PCC 电压扰动变成其电流扰动。把三者首尾相接，就得到 Eq. (7) 的闭环传递函数。直观上，\([\mathbf I-\mathbf Z_g\mathbf Y_1-\mathbf Z_g\mathbf Y_2]^{-1}\) 正是对“电流改变 PCC、电压再改变电流”这一反馈回路的累积放大。[pdf:E04]（PDF 物理页 4，Eq. 1–Eq. 7）

Appendix 进一步从 dc-voltage loop、current loop 与 PLL 的线性化方程构造单机 \(\mathbf Y_i(s)\)。电流环闭环关系为 \(\Delta\mathbf i_{dq}=\mathbf G_{ir}(\mathbf I-\mathbf G_{ir}\mathbf G_i)^{-1}\mathbf G_{iv}\Delta\mathbf v_{fdq}\)（Eq. A.5）；通过 \(dq\to xy\) 变换和 PLL 动态得到 inverter-output voltage 对 line current 的 \(\mathbf H_i(s)\)，再与变压器/集电线阻抗组合，形成 Eq. (A.12) 的 \(\mathbf Y_i(s)\)。[pdf:E12]（PDF 物理页 12，Eq. A.3–Eq. A.12）工程含义是：控制器决定“逆变器端口如何响应 PCC 扰动”，线路和变压器决定“该响应如何传到 PCC”。需要注意，Eq. (A.11) 刚定义了 \(\mathbf Z_{lTi}\)，但 Eq. (A.12) 印作 \([\mathbf H_i-\mathbf Z_{\text{line}i}]^{-1}\)；本卡不擅自替作者修正这一记号差异。

### 6.2 从极点匹配到“同线长最危险”

设新增线长为 \(l_B\)，闭环中与 subsystem B 对应的中频 eigenvalue 为 \(\hat{\lambda}_B(l_A,l_B)\)，B 独立时的 eigenvalue 为 \(\lambda_B(l_B)\)。当 \(l_A=l_B=l_0\) 时，论文利用 identical-inverter system 的内部模态关系得到 \(\hat{\lambda}_B(l_0,l_0)=\lambda_B(l_0)\)（Eq. 13）；交换两条线不改变闭环系统，因此 \(\hat{\lambda}_B(l_0+\Delta l_B,l_0)=\hat{\lambda}_B(l_0,l_0+\Delta l_B)\)（Eq. 15）。把这两个对称关系代入差分极限，得到

\[
\left.\frac{\partial\lambda_B}{\partial l_B}\right|_{l_B=l_0}
=2\left.\frac{\partial\hat{\lambda}_B}{\partial l_B}\right|_{l_B=l_0},
\]

即 Eq. (19)。[pdf:E07]（PDF 物理页 7，Eq. 10–Eq. 20）

论文再从 Fig. 10 观察到 open-loop subsystem B 的极点轨迹近似平行虚轴，即 \(\arg(\partial\lambda_B/\partial l_B)\approx\pi/2\)（Eq. 23），因而同线长点处闭环轨迹的切线也近似平行虚轴（Eq. 24）。结合两种分区下开环极点实部近似相等，作者推到

\[
[\hat{x}_B(l_1,l_2)-x_B(l_1)]
[\hat{x}_B(l_1,l_2)-x_B(l_2)]\ge 0
\]

（Eq. 29），再结合数值轨迹取其物理解支，写成 \(\hat{x}_B(l_1,l_2)\le\max\{x_B(l_1),x_B(l_2)\}\)（Eq. 30）。等号在 \(l_1=l_2\) 处取得，所以匹配线长对应最靠右、阻尼最差的中频闭环极点。[pdf:E08]（PDF 物理页 8，Eq. 29–Eq. 30）

### 6.3 推广到多逆变器

对 \(n+1\) 台系统，如果新增线长 \(l_{n+1}\) 等于任一既有 \(l_i\)，作者借助 identical pair 的 internal pole 不受其外部系统动态影响这一已有结论，把多机内部极点等同于对应二机系统极点，再等同于 open-loop subsystem B 的极点（Eq. 31–Eq. 33）。在同样的“开环轨迹近似竖直”条件下，得到 Eq. (35)：\(\hat{x}_B(l_1,\ldots,l_n,l_{n+1})\le x_B(l_i)\)，等号在 \(l_{n+1}=l_i\) 时取得。[pdf:E08]（PDF 物理页 8，Eq. 31–Eq. 35）

这部分确有形式化数学，但结论并非无条件定理。Eq. (23) 是从算例轨迹得到的近似条件；从 Eq. (29) 到 Eq. (30) 还结合了 Fig. 10 所示的分支方向；多机推广又依赖 identical-inverter internal pole 关系。更准确的理解是“在论文列出的模态匹配与轨迹方向条件下的一般规律”，而不是对任意控制器、任意运行点和任意异构逆变器的普遍定理。

## § 7 — 实验设计与结论

**问题 1：线长主要影响哪一段动态？ → 实验：** 固定 \(l_A=10\) km，将 \(l_B\) 从 0 km 扫到 34 km，步长 2 km，并比较 ideal grid、SCR=9、SCR=5 下开环与闭环 eigenvalue trajectories。**答案：** 集电线参数主要移动中频 eigenvalues，对低频 eigenvalues 影响较小；ideal grid 的 \(Z_g=0\)，A/B 动态解耦，而非理想电网下闭环与开环极点通常不同。[pdf:E06]（PDF 物理页 6，Fig. 9–Fig. 11）

**问题 2：新增线长接近既有线长是否会降低阻尼？ → 实验：** 二机系统采用三组线长：System I 为 \(10/1\) km，System II 为 \(10/34\) km，System III 为 \(10/10\) km；每台 inverter 额定 1.5 MW，变压器比 690 V/10.5 kV、等效阻抗 0.045 p.u.，电缆阻抗 \(0.46+j0.4\ \Omega/\text{km}\)，grid \(X_g/R_g=10\)。控制参数包括 \(L_f=0.2\) mH、\(C=11.75\times10^3\ \mu\text F\)、\(k_{pv}=3\)、\(k_{iv}=20\)、\(k_{pi}=0.026\)、\(k_{ii}=20\)、\(k_{pt}=0.05\)、\(k_{it}=0.9\)。[pdf:E05]（PDF 物理页 5，Table II 与 Section III-A）在 6.0 s 将 #1 dc-link input power 降低 5%。**答案：** SCR=5 时三者都稳定但 System III settling time 最长；SCR=9 时 System I 约 1 s、System II 约 3 s、System III 约 35 s 才回到稳态，匹配线长的 System III 阻尼最弱。[pdf:E09]（PDF 物理页 9，Table III 与 Section IV-A）

**问题 3：两机规律能否在五机系统出现？ → 实验：** System IV 的线长为 \(1,3,5,10,10\) km，System V 为 \(1,3,5,10,34\) km；比较 SCR=5 和 SCR=9 下 #4 inverter 的 active-power response。[pdf:E10]（PDF 物理页 10，Table IV、Fig. 18 与 Section IV-B）**答案：** SCR=5 时两系统均稳定但 System IV settling 更慢；SCR=9 时带两个 10 km 线长的 System IV 不稳定，线长全不同的 System V 稳定。作者用 Eq. (36)–Eq. (37) 将这一差异解释为 System IV 的 internal pole 等于 10 km 下的 open-loop B 极点，而 System V 的对应闭环实部更靠左。[pdf:E11]（PDF 物理页 11，Fig. 19、Eq. 36–Eq. 37）

五机实验的扰动幅值存在 PDF 内部不一致：Section IV-B 的总述写 #4 dc-link input power 在 6.0 s 降低 5%，但 Fig. 18 caption 写降低 10%，后续 Fig. 19/Section III-D 的表述也采用 10%。源 PDF 未提供足够信息消除此冲突，因此本卡不把五机扰动幅值认证为唯一确定值。[pdf:E10]（PDF 物理页 10，Section IV-B 与 Fig. 18 caption）[pdf:E11]（PDF 物理页 11，Fig. 19–Fig. 20）

**问题 4：增大 current-controller \(k_{pi}\) 能否补救匹配线长导致的不稳定？ → 实验：** participation factor 表明中频模态主要由 \(I_d^*\)、\(I_d\) 与其导数状态参与，随后作者把 \(k_{pi}\) 从 0.026 扫到 0.054，步长 0.002；在 System IV、SCR=9 中把 #4/#5 的 \(k_{pi}\) 增大到 0.035。**答案：** eigenvalue 向更稳定方向移动，原本不稳定的 System IV 在 nonlinear simulation 中恢复稳定。[pdf:E09]（PDF 物理页 9，Fig. 13–Fig. 14）[pdf:E11]（PDF 物理页 11，Fig. 20）

不得外推的范围包括：论文只验证二机和五机、VOC、给定 L-filter/控制结构、给定参数与 SCR 工况；没有硬件实验、field data、controller delay/quantization、强异构控制器或 EMT/FPGA 实时执行证据。图中波形支持“这些算例与小信号分析一致”，不能单独证明所有风场布局都遵循同一排序。

## § 8 — Take-aways

**5 句话：**

1. 论文把容量扩展后的多逆变器系统分成“原系统”和“新增逆变器”，用 PCC voltage 与新增 line current 构造闭环互联。
2. 开环子系统与闭环整体的 eigenvalue 位移提供了 interaction degree 的可解释量。
3. 在本文的 identical-inverter、非理想电网和中频模态条件下，新增集电线长度越接近任一既有线长，系统阻尼越差。
4. 二机与五机 nonlinear simulations 支持该排序，并显示更高 SCR 的算例反而更易出现严重振荡或不稳定。
5. 规划上可拉开线长，控制上可增大 current-controller \(k_{pi}\)，但论文未验证硬件、强异构设备或实时 EMT/FPGA 场景。

**3 句话：**

1. 这篇论文的核心贡献是把多机交互从“整体极点发生了什么”改写为“闭环后各子系统极点移动了多少”。
2. 在其假设范围内，同线长会产生最危险的中频 internal mode，而线路差异和更大的 \(k_{pi}\) 可增加稳定裕度。
3. “普遍规律”仍受 identical-device symmetry、近似竖直的开环极点轨迹以及有限仿真工况约束。

**1 句话：** 对采用相同 VOC 参数的扩容型并联系统，集电线“过度匹配”可能比线路更长本身更危险，但这一规则必须先用目标场站的实际 admittance 和模态验证。

## § 9 — 最脆弱的假设

最脆弱的假设是：**新增逆变器与某台既有逆变器除集电线长度外具有足够相同的动态参数，使“线长相等 → identical pair internal pole 与 open-loop subsystem B 极点重合”的模态匹配成立。**

这是核心假设，因为二机的 Eq. (13)、多机的 Eq. (31)–Eq. (33)，以及最终“等长最危险”的等号条件都依赖它。论文给出的证据是同参数 VOC 逆变器的 eigenvalue sweep、二机/五机仿真，以及对既有 identical-inverter internal pole 结论的引用；在其五机 System IV 中，两个 10 km 分支确实对应 SCR=9 下的不稳定，增大两台 \(k_{pi}\) 后又恢复稳定。[pdf:E08]（PDF 物理页 8，Eq. 31–Eq. 35）[pdf:E11]（PDF 物理页 11，Fig. 19–Fig. 20）

实际扩容时，这个假设可能因厂家差异、current/PLL 参数差异、滤波器与变压器容差、数字控制 delay、运行功率和 dc-link operating point 不同而失效。只要这些差异让 internal pole 不再与 \(\lambda_B(l_i)\) 重合，线长相等未必仍是轨迹最靠右的点。论文没有做这些异构维度的 robustness sweep，也没有用硬件或现场阻抗辨识证明“看似同型号”的设备足以满足模态同一性。因此它证明了一个结构清晰、但条件性很强的机制；尚未证明线长匹配是异构风场扩容的普遍风险指标。

## § 10 — 最小复现实验

一周内最值得复现的是“同线长处中频模态最靠右，并可被 \(k_{pi}\) 拉回”的最小闭环验证，不必先搭五机或 FPGA。

1. 在 MATLAB/Simulink 或等价工具中建立两台同参数 VOC inverter 的连续时间 averaged model：L-filter、dc-link constant-power input、dc-voltage PI、current PI、PLL、变压器/集电线和 Thevenin grid。使用 Table II 与 Section III-A 的参数；论文未报告的 solver、PWM/average 细节必须在实验记录中自行固定，并作为复现偏差源。
2. 固定 \(l_A=10\) km，令 \(l_B=1,2,\ldots,34\) km；分别设置 SCR=5 与 SCR=9。线性化后保存全部 eigenvalues，并以 modal assurance/eigenvector continuity 跟踪与 subsystem B 对应的中频模态，不能只按“最近的极点”手工配对。
3. 对每个 \(l_B\) 记录该模态 real part、damping ratio，以及 \(|\hat{\lambda}_B-\lambda_B|\)。重点检验 \(l_B=10\) km 是否为 real part 的局部最大值，且轨迹切线是否近似平行虚轴。
4. 在 \(l_B=1,10,34\) km 三点施加 #1 dc-link input power 5% step，测 active-power settling time 与增长/衰减包络。最后在 \(l_B=10\) km、SCR=9 下把 \(k_{pi}\) 从 0.026 增至 0.035，检查 unstable/weakly damped 模态是否左移且时域响应恢复衰减。

支持核心 claim 的最低结果是：同一参数集下 \(l_B=10\) km 的目标模态 real part 不小于邻近线长，时域 settling 最慢，并且增大 \(k_{pi}\) 后该模态和波形同时改善。反驳结果是：经过可靠的同一模态跟踪后，最差点稳定地偏离 10 km，或 \(k_{pi}\) 左移预测与 nonlinear response 相反。这个复现只检验论文的二机机制，不足以验证多机推广。

## § 11 — 最强反例设计

最强反例不是随便加入噪声，而是专门破坏第 9 节的模态同一性，同时保持设备参数落在工程可信范围内。

构造一个五机容量扩展系统，既有线长固定为 \(1,3,5,10\) km，新增线长在 8–12 km 连续扫动。让新增逆变器与 10 km 既有机组在额定功率和拓扑上相同，但对 \(k_{pi}\)、PLL bandwidth、\(L_f\)、变压器 leakage 和 digital delay 做联合容差扫描；运行功率也从低载扫到额定。每个工况同时计算 full-system eigenvalues、open/closed eigenvalue pairing、participation factor 和 nonlinear step response，并与“所有控制参数完全相同”的基准比较。

真正推翻核心机制的结果是：在一大片而非孤立的可信参数区域内，最差阻尼点系统性地离开 10 km；或者 10 km 处不再出现 internal-pole/open-loop-pole 重合，而某个不同线长因 control-delay/PLL interaction 更不稳定。这样就提供了具体替代解释：决定风险的不是“线路长度相等”，而是总端口 admittance 的某个 modal coincidence；线长仅在 identical-controller 切片上充当代理变量。相反，如果在多维异构扫描中最差点仍稳定锁定于 matched length，才会显著增强论文规则的工程可信度。

## § 12 — Follow-up Research Idea

**候选研究方向：从“按线长避配”转向“基于实测端口 admittance 不确定集的鲁棒扩容共设计”。** 这是基于本文证据和局限提出的候选判断，未做外部相关工作检索，不声称 novelty。

**(a) 未满足需求。** 风场扩容时，业主通常知道电缆长度，却未必掌握每台在役逆变器的真实 closed-loop admittance、控制器版本、delay 和运行点；而论文最关键的 identical-dynamics 假设恰恰无法由线长保证。需要一种直接回答“接入这台新设备后，在参数漂移和运行点变化下最坏阻尼是多少”的方法。

**(b) 可能的研究价值。** 电力电子与电网领域更看重可验证的稳定边界、工程可实现性和硬件证据。若能把本文的开环—闭环 eigenvalue attribution 保留下来，同时给出对测量误差和设备异构都成立的 worst-case damping certificate，价值会高于再增加一个线长算例。

**(c) 可借鉴工具。** 可以借鉴 robust control 的 structured singular value / parameter-dependent stability analysis，以及 system identification 的 frequency-response uncertainty set。先对原系统在多个 operating points 注入小扰动，辨识 PCC seen-admittance 及其不确定包络；再把候选新增 inverter admittance 接入，求交互模态的 worst-case real part，并联合优化线路、\(k_{pi}\) 与 PLL bandwidth。

**(d) 第一个证伪实验。** 在 controller-HIL 或功率硬件平台上选两种不同固件/延时的并网逆变器，分别测试 matched line 与 deliberately mismatched line。若辨识得到的不确定集无法覆盖实测端口响应，或预测的 worst-case 模态排序与硬件时域振荡排序不一致，这个方向应立即被否定或重构。论文未报告 FPGA/HIL，因此这里的硬件平台是后续研究要求，不是对原文实验的描述。

**(e) 与本文的实质区别。** 本文把 line length 当作主要变化量，在 identical inverter dynamics 下推导 matched length 的风险；候选方向把“未知且随运行点变化的 closed-loop port dynamics”改成问题本身，目标从一条线长启发式变为带不确定性证书的扩容决策。它保留本文最有解释力的 subsystem interaction attribution，但不再要求“相同线长意味着相同内部模态”。
