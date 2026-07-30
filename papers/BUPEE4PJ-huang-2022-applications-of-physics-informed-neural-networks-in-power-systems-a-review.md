# Applications of Physics-Informed Neural Networks in Power Systems - A Review

作者：Bin Huang，Jianhui Wang  
出处：IEEE Transactions on Power Systems，Vol. 38，No. 1，pp. 572–588  
年份：2022（在线发表；卷期标注为 January 2023）  
DOI：10.1109/TPWRS.2022.3162473  
Zotero key：BUPEE4PJ  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是某一个 power flow 或 dynamic state estimation 算法问题，而是一个领域组织问题：**“physics-informed neural network（PINN）在电力系统中到底包含哪些技术范式，已经用于哪些任务，现有证据能支持什么结论，下一步真正的缺口在哪里？”** 作者把动机落在普通 deep neural network（DNN）的四个工程弱点上：高质量训练数据昂贵或稀缺、black-box 结果难以解释、输出可能违反物理规律、out-of-sample generalization 缺乏保证。相对地，PINN 试图把科学知识或物理定律写进 DNN 的优化、初始化、架构或模型组合过程，以提高物理一致性、sample efficiency、可解释性和泛化能力。这些是论文在 Abstract 与 Introduction 中直接陈述的研究问题和价值主张。[pdf:E01]（PDF 物理页 001，Abstract 与 Section I）

这件事对电力系统尤其重要，因为电网同时具备强非线性、跨时间尺度、拓扑约束和安全关键性：state estimation、transient dynamics、power flow、optimal power flow（OPF）、故障检测等任务都既希望利用 DNN 的快速 feed-forward，又不能接受“数值看似合理但违反 Kirchhoff 定律、swing equation 或运行约束”的结果。作者据此把综述范围覆盖到 state/parameter estimation、dynamic analysis、power flow calculation、OPF、anomaly detection and location、model/data synthesis 等应用，并希望建立从“物理知识放在哪里”到“它解决哪类电力问题”的对应关系。[pdf:E01]（PDF 物理页 001，Abstract、Section I）

但需要先限定论文能提供的证据强度。它是一篇 review，主要贡献是分类、汇总和研究议程，而不是在统一数据集、统一网络或统一硬件上重新复现所有算法。因此，本文能说明“截至其文献覆盖期有哪些路径和已报告结果”，不能单独证明 PINN 在任意电网、任意事件或任意部署平台上都优于纯数据驱动或纯物理模型。

## § 2 — 前人工作与不足

作者指出，本文之前已经存在三类相邻综述：一类讨论通用 physics-informed machine learning 框架，一类聚焦 chemistry 等具体科学领域，另一类面向 cyber-physical systems。它们能说明“科学知识如何与 machine learning 结合”，但没有围绕电力系统的运行规律、任务谱系和近年应用做相对完整的整理。因此，这篇论文的定位不是发明 PINN，而是把已有概念重新组织成适合 power systems 的范式—应用—效果—缺口链条。[pdf:E02]（PDF 物理页 002，Section I 中与既有综述 [3]、[10]、[11] 的比较）

在具体技术上，前人并非没有解决这些任务。state estimation 已有 WLS、Gauss–Newton、Kalman filter（KF）及其变体；dynamic analysis 已有 time-domain simulation、Lyapunov 方法与 Koopman/DMD；power flow 已有 Newton–Raphson、Gauss–Seidel、DCPF；OPF 已有成熟的 constrained optimization；控制问题也已有 MPC、rule-based control 与 reinforcement learning。问题在于，这些路线各自承担不同代价：数值物理模型往往需要迭代求解、完整模型或较高计算量，纯 DNN 又依赖大量数据且缺乏物理可行性与可验证性。PINN 的意义是探索两者之间的中间区域，而不是宣称抛弃任意一侧。[pdf:E05]（PDF 物理页 005，Section III-A 开头）[pdf:E08]（PDF 物理页 008，Section III-B）[pdf:E10]（PDF 物理页 010，Sections III-B/III-C）

论文也主动收紧了范围。它把 GNN 视为可能承载拓扑先验的工具，但明确说已有专门 GNN 综述，因此这里只选取“物理原则被更深地整合、而不只是使用图结构”的工作。这说明作者真正关心的判据不是网络名字，而是物理信息是否改变了 loss、initialization、architecture 或 physics–DL interaction。[pdf:E04]（PDF 物理页 004，Section II-C）

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为五步。

第一步，从工程矛盾出发：电力系统需要更快的近似器和控制器，而普通 DNN 的训练数据、可解释性、物理可行性与泛化保证不足；纯物理方法虽然可解释，却可能在非线性、大规模或实时场景中计算昂贵。[pdf:E01]（PDF 物理页 001，Section I）

第二步，不把“physics-informed”理解成一种固定网络，而是问：物理知识能进入学习系统的哪个位置？沿 DNN 生命周期观察，会自然得到四个入口：loss function、parameter initialization、architecture、以及显式并存的 hybrid physics–DL model。Fig. 1 把这四个位置画在同一网络流程上。[pdf:E02]（PDF 物理页 002，Fig. 1 与 Section II）

第三步，为这四类入口建立可解释的机制。约束可以作为 residual 进入 loss；仿真数据或 expert demonstration 可以用于预训练；拓扑、守恒关系或中间物理量可以决定连接和隐藏状态；不完整物理模型与 DNN 还可以串联、相互替换局部组件或做 ensemble。这样，PINN 的“物理”不再只是口号，而是可落到参数更新路径上的具体设计选择。[pdf:E03]（PDF 物理页 003，Sections II-A/II-B）[pdf:E04]（PDF 物理页 004，Sections II-C/II-D）

第四步，把应用按电力任务而不是按网络结构分类。作者逐类考察 state/parameter estimation、dynamic analysis、power flow、OPF、anomaly detection/location、synthesis 等问题，并在 Table I 中记录 specific application、integration mode、baseline/effect。为了避免把不同论文的数字直接当成同一 benchmark，作者还说明了表中 baseline 选择、case 选择和 efficiency 的含义：多 baseline 时通常只列每一大类中的较优者，多 case 时可能给区间，并优先报告更现实的噪声或真实电网场景。[pdf:E05]（PDF 物理页 005，Section III 与 Table I 说明）

第五步，从已有结果的边界反推研究议程：小系统、少量动态过程、离散事件、跨拓扑迁移、formal guarantee、复杂数值表示和 benchmark 都没有被充分解决。于是论文最后的“path forward”不是再列更多应用名词，而是把可扩展性、可迁移性、robustness certification、hybrid discrete/continuous 输出等问题提到领域层面。[pdf:E14]（PDF 物理页 014，Section IV）[pdf:E15]（PDF 物理页 015，Sections IV/V）

## § 4 — 核心 Intuition

PINN 的核心不是让 neural network “自己学会物理”，而是把已知物理结构放进训练和推理的关键接口，使不符合物理的函数在搜索空间中更难被选中。[pdf:E02]（PDF 物理页 002，Fig. 1 与 Eq. (1)）  
这种先验可以是 soft constraint（physics residual）、好的初始点、由拓扑决定的连接，或与 white-box model 显式交互的 grey-box system。[pdf:E03]（PDF 物理页 003，Sections II-A/II-B）[pdf:E04]（PDF 物理页 004，Sections II-C/II-D）  
在电力系统中，power-flow equations、swing equation、KKT conditions、admittance/topology、energy function 等恰好提供了这些结构，因此 PINN 有机会用更少数据得到更物理一致的快速近似。  
但这一机制只在先验适用、约束可计算且与实际事件一致时成立；错误或过时的物理约束同样会系统性地把模型推向错误答案。

## § 5 — 具体方法与完整 Pipeline

本文是综述，没有一个统一可部署的“本文 PINN”。它提供的是一个设计 pipeline，使用者可以把具体电力任务放入其中：

1. **定义任务与输出物理含义。** 先确定是在估计 state/parameter、推进 dynamics、求 PF/OPF、检测异常，还是生成电网模型；明确哪些输出对应 voltage、angle、frequency、power、dual variable 等物理量。
2. **选择可信的 prior。** 可以采用 governing equations、network topology、KKT/convexity、设备通信结构、energy or stability index、专家策略或仿真模型。prior 的可用程度决定后续能采用 soft residual、hard-coded connection 还是 hybrid model。
3. **选择注入位置。** 四个主范式是 physics-informed loss、physics-informed initialization、physics-informed architecture、hybrid physics–DL model。它们可以单独用，也可以组合。[pdf:E02]（PDF 物理页 002，Fig. 1）
4. **构造训练信号。** 有标签数据约束预测误差，collocation points 约束方程 residual；或用 simulation/expert demonstration 预训练，再用真实观测 fine-tune。architecture 路线则直接固定、裁剪或解释某些连接和中间变量。[pdf:E03]（PDF 物理页 003，Eqs. (7)–(10) 与 Section II-B）
5. **按真实 baseline 与故障条件评估。** 需要同时比较纯数据驱动方法和纯模型方法，并区分 nominal、noise/corruption、limited observability、topology change 与 out-of-distribution 条件。论文的 Table I 就是按 application—mode—baseline/effect 汇总这一步。[pdf:E05]（PDF 物理页 005，Table I 说明）[pdf:E06]（PDF 物理页 006，Table I）

用论文的 single-machine infinite-bus system（SMIBS）示例，可以把这个 pipeline 具体化。输入是时间 \(t\) 与机械功率 \(P\)，网络输出 rotor angle \(\delta(t,P)\)；frequency 由 \(\omega=\partial\delta/\partial t\) 得到。automatic differentiation 计算 \(\delta\) 对时间的导数，再代入 swing equation 形成 residual \(f(t,P)\)。初始/边界标签约束 \(\delta\)，不要求标签的 collocation points 约束 \(f\) 接近零，两个损失共同更新同一组网络参数。输出不是独立于物理的 angle 预测，而是同时被少量数据和动力学方程限制的连续近似轨迹。[pdf:E02]（PDF 物理页 002，Eqs. (2)–(4)）[pdf:E03]（PDF 物理页 003，Eqs. (5)–(10)）

领域模板要求的若干工程项，本文没有给出统一实现，必须保持“未报告”：

- **开关/事件处理：** 未报告可执行机制；论文反而指出 protection action、generator reactive-power limit 等离散事件会导致 non-differentiable formulation，是现有 PINN 的缺口。[pdf:E10]（PDF 物理页 010，Sections III-B/III-C）
- **时间推进与多速率：** 综述提到被引工作使用 implicit Runge–Kutta 逼近 dynamical evolution，也讨论不同控制设备 action frequency 不同，但没有给出统一 step size、multi-rate scheduler 或实时 deadline。[pdf:E08]（PDF 物理页 008，Section III-B）[pdf:E12]（PDF 物理页 012，Section III-D）
- **计算依赖与并行：** 只讨论 test phase 的 feed-forward 效率和若干 solver 替代关系；未报告 dependency graph、parallel schedule 或 memory bandwidth。
- **数值表示：** 未报告 fixed-point、floating-point precision、quantization 或误差预算；论文只把 complex-valued PINN 列为未来方向。[pdf:E14]（PDF 物理页 014，Section IV）
- **FPGA 映射与实际平台：** 未报告 RTL/HLS、DSP/BRAM 使用量、clock frequency、latency、throughput、host interface 或 FPGA-in-the-loop 验证。论文提到 edge computing 只是未来应用背景，不等同于硬件实现证据。[pdf:E14]（PDF 物理页 014，Section IV）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有推导一个新的统一定理；它用 SMIBS 展示 physics-informed loss 如何从 governing equation 构造出来。这个示例是理解全文技术语言的数学核心。

首先，普通监督损失、参数正则和物理正则被写成

\[
\mathcal{L}
=L(\hat{\mathbf y},\mathbf y)
+\lambda R(\mathbf W,\mathbf b)
+\gamma R_{\mathrm{Phy}}(\mathbf X,\hat{\mathbf y}).
\tag{1}
\]

其中 \(L\) 测量预测与标签的距离，\(R\) 是对权重 \(\mathbf W\) 和偏置 \(\mathbf b\) 的常规正则，\(R_{\mathrm{Phy}}\) 则测量输出对物理方程的违反程度；\(\lambda,\gamma\) 控制两类约束的相对权重。直觉上，第一项要求“像数据”，第三项要求“像一个可能存在的物理过程”。[pdf:E02]（PDF 物理页 002，Eq. (1) 及其变量定义）

SMIBS 的 swing equation 写为

\[
\xi\frac{\partial^2\delta}{\partial t^2}
+\kappa\omega
+B V_gV_e\sin(\delta)
-P=0,\qquad
\omega=\frac{\partial\delta}{\partial t},
\tag{2}
\]

其中 \(\xi\) 是 inertia constant，\(\kappa\) 是 damping coefficient，\(B\) 是 generator 与 infinite bus 之间的 susceptance，\(V_g,V_e\) 是两端 voltage magnitude，\(P\) 是 generator mechanical power。惯性项、阻尼项、电磁功率项与机械输入必须平衡；网络若输出一条不满足这个平衡的 \(\delta(t)\)，就会产生非零 residual。[pdf:E02]（PDF 物理页 002，Eq. (2) 与相邻变量定义）

作者先写出通用 PDE 形式

\[
\frac{\partial u(t,x)}{\partial t}+\mathcal N[u]=0,
\qquad x\in\Omega,\ t\in[0,T],
\tag{4}
\]

再定义由同一网络及 automatic differentiation 得到的 residual

\[
f(t,x)=\frac{\partial u(t,x)}{\partial t}+\mathcal N[u].
\tag{5}
\]

对 SMIBS，令 \(u(t,x):=\delta(t,P)\)，则

\[
f(t,P)
:=\xi\frac{\partial^2\delta}{\partial t^2}
+\kappa\omega
+BV_gV_e\sin(\delta)-P.
\tag{6}
\]

关键不是额外训练一个完全独立的 \(f\)，而是 \(u\) 与 \(f\) 共享网络参数；因此，使 residual 变小会直接改变输出函数 \(\delta(t,P)\)。[pdf:E02]（PDF 物理页 002，Eqs. (3)–(4)）[pdf:E03]（PDF 物理页 003，Eqs. (5)–(6)）

有标签的初始/边界数据给出

\[
\mathcal L_{\mathrm{MSE},u}
=\frac{1}{N_u}\sum_{i=1}^{N_u}
\left\lVert
u(t_u^i,x_u^i)-u^i
\right\rVert^2,
\tag{7}
\]

而不需要状态标签的 collocation points 给出

\[
\mathcal L_{\mathrm{MSE},f}
=\frac{1}{N_f}\sum_{j=1}^{N_f}
\left\lVert
f(t_f^j,x_f^j)
\right\rVert^2.
\tag{8}
\]

联合训练目标是

\[
\mathcal L_{\mathrm{MSE}}
=\mathcal L_{\mathrm{MSE},u}
+\mathcal L_{\mathrm{MSE},f}.
\tag{9}
\]

因此，collocation point 的价值不是增加新的 ground truth，而是在没有 \(\delta\) 标签的位置仍能问“这条轨迹是否满足方程”。这正是论文所说的缩小参数搜索空间、降低 labeled-data demand 的机制。不过，\(\mathcal L_{\mathrm{MSE},f}\) 的权重、collocation point 选择和物理模型误差都会影响训练；论文后文也把 loss-term balance 与 collocation selection 列为未决问题。[pdf:E03]（PDF 物理页 003，Eqs. (7)–(10)）[pdf:E08]（PDF 物理页 008，Section III-B 对 loss balance 的讨论）[pdf:E10]（PDF 物理页 010，Section III-B 对 collocation points 的研究缺口）

## § 7 — 实验设计与结论

**重要边界：本文没有进行统一原创实验。** 下列均是作者对被综述工作的归纳，Table I 的百分比与倍数来自不同论文、不同系统和不同 baseline，不能横向当作同一 benchmark 排名。作者自己还说明：表中可能只保留某一大类中表现较好的 baseline，多 case 可能合并为区间，efficiency 默认指 deployment/testing phase。[pdf:E05]（PDF 物理页 005，Table I 解释）

**问题 1：物理先验能否提高 state/parameter estimation 的效率或抗坏数据能力？ → 实验：** 被综述工作在 real-time SE、limited-observability distribution SE、parameter estimation、transmission SE 与 DSE 中，把 skip connection、PFE residual、topology pruning、automatic differentiation 或 hybrid decoder 与 Gauss–Newton、WLS、NN、GNN、UKF 等比较。Power-GNN、three-phase PFE transition 和 physics-based decoder 等实例说明这些先验如何进入具体 estimator。[pdf:E07]（PDF 物理页 007，Section III-A）**答案：** Table I 汇总的多数案例报告正收益，但并非无条件胜出；例如 DSE 相对 UKF 在 standard/fast systems 中报告约 \(10\times\) accuracy 提升，却在 slow systems 中报告约 \(80\times\) accuracy 下降，说明 slow dynamics 和 vanishing gradient 是明确失败区。[pdf:E06]（PDF 物理页 006，Table I 中 State/parameter estimation 与 DSE 行）

**问题 2：PINN 能否在低数据条件下学习 dynamics，并减少 time-domain simulation？ → 实验：** [13] 的 SMIBS 示例只使用 40 个 labeled training samples，报告训练时间 223 s；后续工作加入 implicit Runge–Kutta、额外 governing-equation residual，或把 differential/algebraic reconstruction 与 equation violation 一起优化。**答案：** 综述归纳这些方法可以近似动态响应、部分工作不需要 simulation data 或 exhaustive time-domain simulations；但最大误差出现在 algebraic-variable jumps，battery ESS 的 PINN 相对 NN 优势还会随 prediction horizon 增长由 75% 降到约 10%。[pdf:E08]（PDF 物理页 008，Section III-B）

**问题 3：physics-guided control 是否兼顾模型结构与学习控制器的灵活性？ → 实验：** 被综述工作用 Koopman/autoencoder 学习可用于 MPC 的线性嵌入，也把 strategic utility、imitation learning、Lyapunov-inspired value priority 或 surrogate environment 写进 RL/DRL。**答案：** 论文认为这些结果显示 PINN 可以辅助控制 synthesis，但同时强调 reward design、safe exploration、agent/environment interaction、multi-agent scalability 与 formal safety 仍未解决，不能由已有个案外推为闭环安全保证。[pdf:E09]（PDF 物理页 009，Section III-B）

**问题 4：PINN 能否替代或补充 PF/OPF solver？ → 实验：** power-flow 工作用 semi-supervised encoder–decoder、bilinear admittance imitation 和 topology mask；GNN PF solver 在 IEEE 9、14、30、118-bus systems 上与 DCPF 比较，并报告 learned weights 可跨 grid 使用。OPF 工作则把 Lagrangian constraint violation、KKT conditions、sensitivity Jacobian 或 convex structure 写入训练。[pdf:E10]（PDF 物理页 010，Section III-C）[pdf:E11]（PDF 物理页 011，Sections III-C/III-D） **答案：** 综述报告 sensitivity-informed DNN 用约 \(1/10\) 到 \(1/4\) 的训练数据即可达到 conventionally trained DNN 的同等 prediction performance；但 worst line-flow violation 在部分 ACOPF case 上因 MIQCQP 过于棘手而难以计算，且当实时训练不可忽略时，PINN 相对快速可靠的 DCPF 未必有显著优势。[pdf:E11]（PDF 物理页 011，Section III-C）[pdf:E12]（PDF 物理页 012，Section III-D）

**问题 5：物理结构能否缓解异常样本稀缺？ → 实验：** high-impedance fault（HIF）检测把 voltage/current 的近似椭圆轨迹作为 convolutional autoencoder regularization；fault location 用 graph topology 与 label propagation 处理低可观测性和低标签率。**答案：** 综述记录 PINN fault-location 方法在 label-rate 急降、负荷变化或拓扑变化时仍报告 95%–100% accuracy；但作者同时指出，这类先验高度 problem-dependent，HIF 的椭圆规律不能自然推广到所有 fault type。[pdf:E13]（PDF 物理页 013，Section III-E）

**问题 6：PINN 的覆盖面是否已经形成统一证据？ → 实验：** Table II 按 forward/inverse、steady-state/dynamic、operation/control 重新分类已有文献。**答案：** 文献已经覆盖多个象限，但这是“存在性地图”，不是均衡 benchmark；不同象限的系统规模、数据条件和评估协议并不统一。[pdf:E14]（PDF 物理页 014，Table II）

## § 8 — Take-aways

**5 句话：**

1. 本文最重要的贡献是把电力系统 PINN 统一为 physics-informed loss、initialization、architecture 与 hybrid physics–DL model 四个范式，而不是提出单一新网络。[pdf:E02]（PDF 物理页 002，Fig. 1）
2. 电力系统中的 PFE、swing equation、topology、KKT condition、energy/stability information 都可以成为先验，但它们进入训练的位置和强度不同。[pdf:E03]（PDF 物理页 003，Section II）[pdf:E04]（PDF 物理页 004，Sections II-C/II-D）
3. 被综述工作在 estimation、dynamics、PF/OPF、control、fault 与 synthesis 上报告了数据效率、推理效率、鲁棒性或物理一致性收益，但这些数字来自异构 case，不能直接横向比较。[pdf:E06]（PDF 物理页 006，Table I）
4. 现有证据最薄弱之处是 large-scale generalization、discrete events、long-horizon dynamics、formal guarantee、transferability 与统一 benchmark。[pdf:E10]（PDF 物理页 010，Section III-B/III-C）[pdf:E15]（PDF 物理页 015，Section IV）
5. 论文不包含 FPGA 实现、数值精度、资源时序或实时步长证据，所以它能指导“如何构造 physics-informed learning problem”，不能直接证明“可部署为 FPGA real-time solver”。

**3 句话：**

1. PINN 是把可信物理先验嵌入 learning pipeline 的一组设计方式，不是一种固定 architecture。  
2. 其优势来自减少可行函数空间，但同一个机制也意味着错误、失效或不可微的先验会造成系统性偏差。  
3. 因此评价 PINN 的关键不是只看 nominal accuracy，而是检查先验失配、事件切换、跨系统迁移与可验证性。

**1 句话：**

PINN 的价值在于用物理约束换取更少数据和更可信的输出，而它的成败取决于这些约束在真实电网、真实事件和目标部署条件下是否仍然成立。

## § 9 — 最脆弱的假设

最脆弱的假设是：**被注入的物理先验在训练、测试和实际运行域内都足够正确、可观测、可微，并且不会漏掉决定系统行为的离散事件。**

如果这个假设成立，physics residual、topology mask 或 KKT layer 会排除大量不可能解，PINN 才可能以更少标签得到更物理一致的输出。论文直接说明，实际应用中如何整合物理知识取决于可用信息量；以 PF 为例，作者列出从 data-driven decoupled MLP、利用 ACPF structure 的 bilinear NN，到依赖已知 topology 的 topology-aware bilinear NN 三个层级。[pdf:E14]（PDF 物理页 014，Section III-I）

如果这个假设不成立，核心机制会反转：错误 prior 不再是 regularizer，而会成为有方向的 bias。论文提供了几个危险信号：dynamic PINN 的最大误差出现在 algebraic-variable jumps；现有方法尚不能自然编码 protection action、reactive-power limit 等离散事件；slow dynamics 会引发 vanishing gradient；多数动态研究只在 SMIBS、Kundur two-area 等小系统或少量过程上验证。[pdf:E08]（PDF 物理页 008，Section III-B）[pdf:E10]（PDF 物理页 010，Section III-B/III-C）

论文缺少的关键证据是：没有统一实验把“正确 physics”“轻微失配 physics”“事件后错误 physics”和“无 physics”放在相同数据、网络容量和测试分布下比较；也没有跨 topology、设备模型和 operating regime 的 calibration/coverage guarantee。Section IV 呼吁 robustness certification、transfer learning 和 benchmark，正说明作者知道现有证据还不能封闭这个假设。[pdf:E14]（PDF 物理页 014，Section IV）[pdf:E15]（PDF 物理页 015，Section IV）

## § 10 — 最小复现实验

一周内最值得复现的不是 Table I 的全部任务，而是检验“physics residual 在少数据时究竟提供了有效归纳偏置，还是只在物理模型完全匹配时看起来有效”。

**数据：** 用一个公开可实现的 SMIBS swing-equation simulator 生成 \((t,P,\delta,\omega)\) 轨迹。训练集只保留 40 个 labeled points，以对应综述引用的低数据设置；另采样一批无标签 collocation points。测试集分四组：nominal、measurement noise、未见过的 \(P/\xi/\kappa\) 组合、以及一次机械功率阶跃或拓扑等效参数突变。[pdf:E02]（PDF 物理页 002，Eq. (2) 与变量）[pdf:E08]（PDF 物理页 008，40 samples 与 223 s 报告）

**实现：** 使用相同 MLP 容量和 optimizer，训练三组模型：（A）只用 \(\mathcal L_{\mathrm{MSE},u}\) 的 plain NN；（B）加入正确 swing-equation residual 的 PINN；（C）加入有控制偏差的 residual，例如把 \(\xi\) 或 \(B\) 设为真实值的 80%，模拟 prior mismatch。三者使用完全相同的 labeled data、初始化次数和训练预算。

**测量：** 报告 \(\delta/\omega\) trajectory RMSE、最大误差、equation-residual norm、跨随机种子方差、训练时间和 inference latency。对阶跃点单独统计事件前、事件邻域与事件后的误差，防止总体 RMSE 掩盖 jump failure。

**支持 claim 的结果：** 在 nominal、noise 和未见参数组合上，B 相对 A 以相同标签数稳定降低 trajectory error 与 residual，且收益跨随机种子存在；这只能支持“正确 prior 在这个连续动力学问题中提高 sample efficiency/generalization”。

**反驳或收紧 claim 的结果：** 若 B 与 A 无显著差异，或 C 在 prior 仅轻微失配时就持续劣于 A，或 B 在阶跃后产生更大的系统性误差，则应把综述的广义优势收紧为“仅在 governing equation 与运行机制匹配时成立”。这个实验不需要复现完整电网控制系统，也不需要 FPGA；它直接攻击第 9 节的核心假设。

## § 11 — 最强反例设计

最强反例是一个**事件驱动的 hybrid power-system trajectory**：系统在训练域内遵循平滑 swing/PFE dynamics，但测试时触发 protection trip、converter current limit、tap action 或 topology reconfiguration，使 governing equation、algebraic constraint 或参数集合瞬间改变。给 PINN 仍使用事件前 residual，而给对照组同样的历史数据但不施加错误 residual；再增加一个能显式识别 mode switch 的 hybrid-system baseline。

这个反例有三个攻击点。第一，论文自己报告 dynamic PINN 最大误差出现在 algebraic jumps，说明连续 automatic differentiation 并不天然处理 discontinuity。[pdf:E08]（PDF 物理页 008，Section III-B）第二，论文明确把 protection action 和 generator reactive-power limit 列为尚不能编码的 discrete events。[pdf:E10]（PDF 物理页 010，Sections III-B/III-C）第三，planning 的 discrete/continuous hybrid output 同样被列为当前 PINN 难题，表明问题不是单一应用偶然现象，而是 smooth differentiable formulation 的共同边界。[pdf:E14]（PDF 物理页 014，Section IV）

若错误 residual 使 PINN 在事件后继续输出低 residual 但高状态误差，或者为了满足旧方程而错过真实 mode transition，这将直接推翻“物理约束自然提高可靠性”的宽泛解释。更具体的替代解释会是：既有收益主要来自**matched simulator 下的结构正则化**，而不是对真实电网机制变化的普遍鲁棒性。只有 event-aware baseline 能恢复性能时，才说明未来方法必须显式建模 mode、guard 和 reset，而不能只增加更多 collocation points。

## § 12 — Follow-up Research Idea

**候选想法：面向混杂电力系统的 event-aware、可证伪 PINN。** 这不是对现有 PINN 再加一个 loss term，而是把问题定义从“在单一平滑 governing equation 下拟合连续轨迹”改成“同时识别运行 mode、定位 event，并在每个 mode 内满足对应方程与 reset/guard 条件”。由于本卡严格 PDF-only、没有额外检索 2022 年之后的相关工作，这里不声称 novelty。

**（a）未满足需求。** 真实电网含 protection、限流、tap change、拓扑切换和多时间尺度设备，而论文明确把 discrete events、small-system scalability 与 hybrid outputs 列为缺口；传统 smooth residual 在事件处可能既不可微又错误。[pdf:E10]（PDF 物理页 010，Sections III-B/III-C）[pdf:E14]（PDF 物理页 014，Section IV）

**（b）可能的研究价值。** 电力系统领域看重安全关键条件下的可解释失败边界、严格验证、工程可实现性和跨工况可靠性。若模型不仅输出 state trajectory，还输出当前 mode、event confidence、mode-specific residual 与可验证的 violation bound，它比只提高平均 RMSE 更接近调度、保护与实时仿真的使用要求。论文也把 performance guarantee、robustness certification 和 benchmark 视为进一步认可 PINN 的关键。[pdf:E14]（PDF 物理页 014，Section IV）[pdf:E15]（PDF 物理页 015，Section IV）

**（c）可借鉴的相邻方法。** 可以借鉴 hybrid automata 的 mode/guard/reset 表示、change-point detection 的事件定位、mixture-of-experts 的 mode-conditioned function approximation，以及 MILP/MIQCQP neural verification。论文已经讨论 ReLU-to-MILP verification、KKT-based worst-case violation 与 mixed-integer program 的相邻进展，但未把它们组合成 event-aware dynamic PINN。[pdf:E10]（PDF 物理页 010，Section III-B 的 verification 讨论）[pdf:E12]（PDF 物理页 012，Section III-D 的 worst-case guarantee）[pdf:E14]（PDF 物理页 014，Section IV）

**（d）第一个证伪实验。** 在同一 SMIBS 或 Kundur two-area 系统中随机化 fault clearing、line trip 与 parameter jump，训练 smooth PINN、event-aware candidate 和纯数据 baseline。预先冻结判据：若 candidate 不能同时降低 event-time error、post-event trajectory error 与 false mode-switch rate，或在未见 event 组合上 violation bound 无覆盖率，那么研究假设被证伪，不继续扩展到更大系统。

**（e）与已有工作的实质区别。** 综述中的主流 PINN 把 physics 当作单一 regime 内的 loss、initialization、architecture 或 white/black-box coupling；这个候选方向把“哪套 physics 当前有效”本身变成待估计且可验证的状态，并把 mode transition 作为一等对象。它改变的是学习目标和系统语义，不是简单换一个应用、加一层网络或增加训练样本。
