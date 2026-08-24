# Neural Controlled Differential Equations for EMT-Level Surrogate Modeling of Grid-Forming Inverters

作者：Jiagang Qu、Yong Tao、Dan Wang、Enyi Li、Jingjing Qi、Ding Wang
出处：arXiv:2607.16258v1，2026
DOI：10.48550/arXiv.2607.16258
Zotero key：PXQN7NA7

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“用神经网络拟合一条波形”这么窄的问题，而是：怎样把一个只从输入输出轨迹学习到的 grid-forming inverter 代理模型，放回连续时间 EMT 求解环路中，让它既能响应离散、多速率控制输入，又不在长时间滚动中无界漂移。作者希望以此缓解两类工程困难：详细 EMT 模型计算慢，且制造商往往不公开全部控制结构和参数。论文把目标定位为黑箱、连续时间、具有一定物理一致性的元件级 surrogate，而不是替代整个电网求解器。[pdf:E01]（物理页 1，Abstract 与 Introduction）

物理上，代理模型最重要的任务是学到“端口电压与控制命令怎样推动网侧电流变化”。论文对象是一个三电平 ANPC 储能变流器，经 LCL filter 接入电网；控制链包含 grid-forming 外环、voltage control、current control 和 PWM。模型实际观测的状态是 \(dq0\) 网侧电流，输入是电压幅值命令、相角命令以及 \(dq0\) 电容电压。[pdf:E03]（物理页 3，Fig. 1 与 §2.1）这使工作与 EMT 元件建模直接相关，但还没有证明它能处理不同控制器、不同拓扑或保护模式。

## § 2 — 前人工作与不足

论文把已有学习型动态模型分成两条主要路线：RNN 一类离散时间数据驱动模型直接学习输入输出序列；physics-informed 模型则把物理先验或约束写入训练。作者认为，前者通常依赖固定采样率和窗口，后者仍可能难以兼顾复杂、刚性的 converter dynamics。Neural ODE 提供了连续时间向量场，但把多速率控制量简单当作连续外生输入或 zero-order hold，不能显式表达“慢外环命令”和“快内环变化”对状态的不同作用；无约束向量场还可能产生伪振荡、能量漂移或长时发散。[pdf:E02]（物理页 2，Introduction）

Neural CDE 的已有优势是把离散观测插值成连续 control path，再让状态随这条路径演化，因此天然兼容不规则采样。本文在这个基础上加入 affine-control 分解、slow/fast 双路径、残差项和 Jacobian regularization。[pdf:E04]（物理页 4，§2.2，Eq. 4–6）需要注意，论文没有用外部 benchmark 证明这些设计优于所有现有 EMT surrogate，也没有报告与 FPGA、CPU 或实时仿真器的 wall-clock 对比；贡献证据主要来自同一数据集内的消融。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，不是作者逐字陈述。第一步，研究者会发现离散序列网络把采样周期写进了模型，而 EMT 求解器和控制器可能有不同步长。第二步，他们会把 inverter 看成受控微分系统：状态本身有自主漂移，控制命令又沿一条时间路径推动状态。第三步，grid-forming control 天然具有层级结构，外环参考变化慢，内环与调制相关量变化快，于是把同一个控制量拆成积分路径和增量路径。最后，为避免 learned vector field 在反复积分时放大误差，再用离散一步映射的 Jacobian spectral radius 作为局部稳定性代理。[pdf:E04]（物理页 4，Eq. 6）[pdf:E05]（物理页 5，Eq. 9–12）[pdf:E06]（物理页 6，§4.2，Eq. 13–15）

这条思路的关键转变，是不再只问“下一点预测准不准”，而是问“这个向量场被数值积分器反复调用时是否仍像受控电气系统”。不过，论文把 100 kHz EMT 波形低通并降到 1 kHz 后再学习，因此它真正约束的是采样后闭环包络，而不是开关级瞬态本身。[pdf:E07]（物理页 7，§4.3）

## § 4 — 核心 Intuition

Neural CDE 把离散控制序列变成一条连续路径，模型学习“状态沿控制路径怎样移动”，而不是把控制量仅仅拼到普通 ODE 的输入端。作者再把路径拆成慢变化 \(u(t)dt\) 和快变化 \(du(t)\)，分别对应外环趋势与突变信息，并对一步流映射的局部放大率施加惩罚。[pdf:E05]（物理页 5，Eq. 11–12）[pdf:E06]（物理页 6，Eq. 13–15）

直观地说，它试图同时回答三个问题：系统自己会往哪里走、控制命令把它推向哪里、控制命令突然变化时会发生什么。这个结构是否真的对应独立的物理 slow/fast mode，论文只给了消融支持，没有做 mode identification 或频域因果分解。

## § 5 — 具体方法与完整 Pipeline

以一次电压参考扰动为例，完整 pipeline 是：

1. 从 EMT 模型得到三相网侧电流与 terminal/capacitor voltage，并做 power-invariant Park transformation。模型状态为三维 \(i_{dq0}\)；控制输入是五维向量 \([A,\phi,v_{dq0}]\)。[pdf:E09]（物理页 9，§5.3）
2. 原始 EMT 波形以 100 kHz、即 10 μs 步长产生；低通后按 100 倍抽取到 1 kHz、即 1 ms，每条约 5.1 s、5101 个样本。全部通道再按 245 A 和 1000 V 基值做 per-unit normalization。[pdf:E08]（物理页 8，§5.1）[pdf:E09]（物理页 9，§5.3）
3. \(f_\theta(x)\) 表示不显式依赖控制的 intrinsic dynamics；两条 \(g_\theta^{(i)}(x)\) 分别接收 slow path \(dX_1=u(t)dt\) 和 fast path \(dX_2=du(t)\)；\(h_\theta(x,u)\) 补偿一阶 Taylor 截断留下的高阶残差。论文还使用 augmented latent dimensions 提高表示能力。[pdf:E05]（物理页 5，Eq. 10–12）
4. \(f_\theta\)、两个 \(g_\theta\) 共享 trunk 但使用独立 heads，baseline trunk 含两层、每层 256 neurons；\(h_\theta\) 是单个 linear layer。训练用 AdamW、learning rate \(10^{-3}\)、weight decay \(10^{-4}\)、26-sample windows，fixed-step RK4；推理用 DOPRI5，rtol \(10^{-4}\)、atol \(10^{-6}\)。[pdf:E08]（物理页 8，Table 1 与 §5.1）
5. 训练损失以短窗 \(dq0\) trajectory MSE 为主，并加入 Jacobian stability regularizer。推理时从初始状态连续积分，输出预测 \(i_{dq0}\)，再可变回 abc 电流用于波形对比。[pdf:E06]（物理页 6，Eq. 15）[pdf:E10]（物理页 10，Fig. 2 与 Eq. 18）

论文没有报告 FPGA mapping、fixed-point format、resource utilization、pipeline latency、实时步长闭合或多实例并行结果。这篇工作提供的是算法级 EMT surrogate，不是已实现的 FPGA real-time component。

## § 6 — 核心数学推导

先看物理意义。普通受控 ODE 写成
\[
\dot{x}=f_\theta(x,u,t),
\]
意思是当前状态和输入决定“每秒往哪个方向变化”。Neural CDE 改写为
\[
dx=f_\theta(x)\,dX,
\]
其中 \(X(t)\) 是由离散控制样本插值得到的路径；状态变化与控制路径的增量直接耦合。[pdf:E04]（物理页 4，Eq. 5–6）

作者从受控 ODE 对输入做一阶 Taylor expansion：
\[
f_\theta(x,u)\approx f_\theta(x)+g_\theta(x)u.
\]
若选 \(dU=u\,dt\)，就得到 affine-control CDE。最终模型进一步写为
\[
dx=f_\theta(x)dt+\sum_{i=1}^{2}g_\theta^{(i)}(x)dX_i+h_\theta(x,u)dt,
\]
其中 \(dX_1=u\,dt\) 保存控制命令的慢趋势，\(dX_2=du\) 强调突变，\(h_\theta\) 承担被一阶近似丢掉的残差。[pdf:E05]（物理页 5，Eq. 9–12）这里“slow/fast”是建模解释，不等于论文已经证明两个 branch 精确对应某两个可辨识物理模态。

稳定性正则从一步离散流映射开始。对 nominal step \(\Delta t\)，作者用
\[
A_\theta(x)\approx I+\Delta t J_\theta(x)
\]
近似一步 Jacobian，并惩罚 \(\rho(A_\theta)>1\)：
\[
\mathcal L_{\text{stab}}=\mathbb E[\max(0,\rho(A_\theta(x))-1)].
\]
[pdf:E06]（物理页 6，Eq. 13–15）这只是小步长下的一阶局部代理；它不能推出整个闭环、多元件网络或所有未见工况都稳定。

论文还定义两种评估量。damping score 比较 Hilbert envelope 拟合得到的 \(\sigma_{\mathrm{CDE}}\) 与 \(\sigma_{\mathrm{EMT}}\)；等于 1 表示衰减率一致。[pdf:E07]（物理页 7，Eq. 16–17）stability score 则积分预测误差的正向局部对数增长率；误差从不放大时得分为 1，持续放大时降低。[pdf:E10]（物理页 10，Eq. 18）二者都不是 Lyapunov stability certificate。

## § 7 — 实验设计与结论

**问题 1：CDE 结构是否比普通 controlled Neural ODE 更适合滚动预测？** 作者保持约 \(2.0\times10^5\) 的相近参数量做逐项消融。Neural ODE 到 standard Neural CDE 时，MSE 从 \(6.0726\times10^{-5}\) 降到 \(3.8649\times10^{-5}\)，stability 从 0.8220 升到 0.8374；dual control pathway 达到 0.8463，是单项消融中最高 stability；dual control + residual 的 MSE 最低，为 \(2.6853\times10^{-5}\)。[pdf:E12]（物理页 13，Table 3）

**问题 2：不同 branch 的容量加在哪里最有效？** Table 4 显示中等 trunk、较深 base 的配置取得 \(3.5407\times10^{-5}\) MSE；Table 5 中加一层 fast branch 得到全表最高 stability 0.8518，加一层 residual branch 得到最低 MSE \(2.5204\times10^{-5}\)。继续加深后收益低于 1%。[pdf:E12]（物理页 13，Table 4）[pdf:E13]（物理页 14，Table 5 与 §5.5）

**问题 3：模型是否保留有效阻尼并能有界滚动？** 六个 test case 的 \(dq\) 和 \(abc\) 电流波形总体贴合；作者报告 damping score 0.85，并展示约 6 s 的 extended rollout 保持有界。[pdf:E10]（物理页 10，Fig. 2）[pdf:E11]（物理页 12，Fig. 4）[pdf:E13]（物理页 14，§5.6）但论文没有给出每个 test trajectory 的误差分布、最大误差、置信区间或 divergence rate。

**最重要的边界：这不是 OOD 实验。** 90 条轨迹全部来自同一 ANPC three-level topology、同一对称运行配置，并随机分成 72 training、9 validation、9 test，也就是 80/10/10 random trajectory split。[pdf:E09]（物理页 9，Table 2 与 §5.3）论文没有 held-out GFL/GFM 控制类别、topology、current-limit/protection mode、fault switching mode，也没有在测试时保持这些模式完全不进入训练。因此不能把 0.85 damping score 或有界 rollout 写成控制/拓扑 OOD 泛化证据。

**时间尺度边界：** 参考 EMT 在 100 kHz 产生，但学习与主要物理指标在低通后的 1 kHz 数据上计算。作者明确承认高频 LC resonance 在这个采样率下被强烈抑制，保留下来的是 effective closed-loop dynamics。[pdf:E07]（物理页 7，§4.3）所以“EMT-level”在本文中更准确地表示数据来源和嵌入目标，不表示 surrogate 逐点重现了 switching waveform。

## § 8 — Take-aways

**5 句话：**
1. 论文把 grid-forming inverter surrogate 写成受 control path 驱动的连续时间 Neural CDE。[pdf:E05]
2. affine \(f/g\) 分解、slow/fast 双路径和残差项在同一数据集消融中均带来收益。[pdf:E12]
3. Jacobian penalty、damping score 和 error-growth score把“滚动是否健康”纳入了训练或评估。[pdf:E06][pdf:E07][pdf:E10]
4. 最强实证是同配置随机切分上的较低 MSE、约 0.85 damping score 与有界 extended rollout，而不是 OOD、硬件实时或全系统稳定性。[pdf:E09][pdf:E13]
5. 1 kHz 低通数据丢掉了大部分高频 LC/switching 信息，因此这更像 sampled closed-loop envelope surrogate。[pdf:E07]

**3 句话：** Neural CDE 的价值在于把多速率控制历史变成连续路径，并把慢趋势和快增量分开建模。论文在随机切分的同一 ANPC-GFM 数据上证明了精度与滚动指标的改善，但没有证明控制或拓扑 OOD。它为 EMT surrogate 提供了值得复现的结构与指标，却还不是可部署的 FPGA/real-time component。

**1 句话：** 这是一篇“结构和评估口径有启发、泛化与部署证据仍很窄”的 Neural CDE EMT surrogate 论文。

## § 9 — 最脆弱的假设

最脆弱的假设是：低通到 1 kHz 后的部分可观测轨迹，仍包含部署时判断 converter dynamics 所需的全部关键物理信息。论文只观察 \(i_{dq0}\) 与 \(v_{dq0}\)，并明确说 kilohertz-range LC resonance 被 controller、PWM、EMT discretization 及采样带宽强烈抑制。[pdf:E07]（物理页 7，§4.3）

如果未观测的 inductor current、switching ripple、current limiting 或保护切换决定了稳定边界，那么一个模型完全可能在 1 kHz 包络上低 MSE、damping score 很高且滚动有界，却在真实 EMT 联立时给出错误的瞬时端口响应。论文用随机 test trajectories、有效阻尼和长滚动给了同分布支持，但没有用 held-out mode、频带外扰动、网络耦合或硬件闭环测试这个假设。作者在结论中也建议增加完整 LC 电感电流和电容电压，并引入 energy-consistency constraint。[pdf:E14]（物理页 15，Conclusion）

## § 10 — 最小复现实验

一周内最有价值的目标不是复刻全部数字，而是检验“dual-path CDE 是否真的改善同分布滚动”。论文没有公开完整 controller gains、数据集或可直接运行代码，因此严格逐字复现目前不可闭合；应把实验标为机制复现。

1. 在现有 EMT 工具中搭建 Table 2 的 ANPC/LCL 配置，固定一个 GFM controller，生成至少 90 条约 5.1 s 轨迹；同时保存 100 kHz 原始数据和论文式 1 kHz 低通数据。[pdf:E09]
2. 固定 72/9/9 trajectory split、相同 state/input、相近参数量，训练 controlled Neural ODE、standard Neural CDE、dual-path Neural CDE 三个模型。
3. 复现 Table 3 的 MSE、Eq. 18 stability score、Eq. 17 damping score；报告每条 test trajectory 的 median、95th percentile、maximum 和是否发散，而不是只给平均值。[pdf:E07][pdf:E10][pdf:E12]
4. 支持核心 claim 的最低标准：dual-path 在至少三个 random seeds 上同时降低 test MSE 和 error-growth，并且 extended rollout 不增加发散数。若收益只出现在单一 split/seed，或 100 kHz 误差显著恶化，则反驳其稳健性。

## § 11 — 最强反例设计

最强反例是 leave-one-mode-out 的冻结模型测试。训练集中只放 normal symmetric GFM 轨迹，完全留出 current-limit/protection mode 或另一组控制结构；测试时让同一条轨迹跨越参考阶跃、限流进入、限流退出和故障恢复，禁止 fine-tuning。然后同时比较 1 kHz 包络误差、100 kHz 端口瞬态、最大电流约束违例、damping classification 和是否发散。

这个反例直接攻击论文最脆弱的外推：dual slow/fast path 可能只学会同一控制器下的输入平滑与差分，而没有学会离散模式改变后的新向量场。若模型仍保持有界但把限流峰值或恢复时间预测错，它将说明“bounded rollout”不等于“物理正确”；若 Jacobian penalty 在模式边界附近失效，则说明局部 spectral-radius proxy 不能承担 hybrid EMT stability 保证。论文现有 72/9/9 random split 没有排除这个替代解释。[pdf:E09]（物理页 9，§5.3）

## § 12 — Follow-up Research Bet

**主 bet：用闭合命令回路辨识 GFM 的非交换控制几何。** 新问题不是继续降低随机轨迹上的平均 MSE，而是问：当电压幅值命令 \(A\) 和相角命令 \(\phi\) 走过起点、终点、持续时间和一阶累计量都相同、只有先后顺序相反的路径时，ANPC-GFM 是否留下方向相反的 \(i_{dq0}\) 位移？若答案为是，这会使当前 surrogate 首次具备“控制顺序可辨识”能力：它不仅知道命令变化了多少，还能预测“先升压再超前相角”与“先超前相角再升压”在异步 control clock 下为何产生不同瞬态。

核心机制来自 control-affine CDE 的非交换 vector fields。论文的 Eq. 11–12 已把完整输入向量分别沿 \(dX_1=u(t)dt\) 与 \(dX_2=du(t)\) 驱动状态，但仍只把它们解释为 slow/fast 两路。[pdf:E05] 对命令平面中的小矩形回路 \(A\uparrow\!\to\!\phi\uparrow\!\to\!A\downarrow\!\to\!\phi\downarrow\)，若 \(A\) 与 \(\phi\) 对应的状态 vector fields 不可交换，回路结束后的领先项应随 signed area \(\mathbb A^{A\phi}\propto\delta A\,\delta\phi\) 和 Lie bracket \([g_A,g_\phi]\) 变化；反向走同一回路时该项反号。因果链是：层级 GFM controller 与 LCL closed-loop dynamics 使两个命令通过不同状态通道作用 → 两个作用次序改变 latent trajectory → 闭合路径仍留下方向相关的电流位移 → 把二阶 iterated integral 与 bracket field 直接写入 CDE 后，模型可外推未见的更新顺序。基本设计变量至少包括命令轴对 \((A,\phi)\)、回路 signed area（由 \(\delta A,\delta\phi\) 决定）和两次更新之间的 dwell time \(\tau\)；representation 变量则是保留到哪一阶 iterated integral 以及 bracket basis 的 rank。这不是在原模型后面追加 residual module，而是把 experimental object 从普通波形改成输入路径的方向效应。

论文证据支持“值得测这个效应”，但尚未证明它存在。方法上，模型状态只有 \(i_{dq0}\)，输入却同时含可操纵的 \(A,\phi\) 与内生的 terminal voltage \(v_{dq0}\)，并以共享 trunk、独立 heads 表示不同 control-driven effects。[pdf:E08][pdf:E09] 实验上，在约 \(2\times10^5\) 的相近参数预算下，standard Neural CDE 相比 controlled Neural ODE 把 MSE 从 \(6.0726\times10^{-5}\) 降到 \(3.8649\times10^{-5}\)，dual control pathway 又达到 \(2.7681\times10^{-5}\) 与 0.8463 stability score；这说明 path organization 的收益不能简单归因于参数量。[pdf:E12] 但继续加深 fast branch 虽把 stability 提到 0.8518，却使 MSE 回升到 \(2.8141\times10^{-5}\)，而进一步加深总体很快饱和，提示“更多容量”不是充分解释。[pdf:E13] Fig. 2 与 Fig. 4 展示了阶跃附近的尖峰和重复扰动下的有界 rollout，却没有构造顺序相反的 matched paths。[pdf:E10][pdf:E11] 更关键的是，90 条轨迹均来自同一对称 ANPC 配置并随机作 72/9/9 切分；100 kHz 原始波形低通到 1 kHz 后，kilohertz-range LC resonance 已被显著压低。[pdf:E07][pdf:E09] 源 PDF 没有 appendix；实现细节只闭合到 26-sample window、训练 RK4 和推理 DOPRI5，未给出可辨识 path geometry 的实验。

最大收益是把黑箱 EMT component 的研究对象从“某一批扰动波形拟合得准”推进为“少量可解释的 control algebra 能生成多种异步更新顺序”，从而用一个低维 bracket basis 组织多速率 controller 的组合效应，并可能反推出哪些 command channels 在物理上真正耦合。最大的科学风险也很尖锐：1 kHz 低通后的闭环包络可能近似交换，所谓方向效应低于数值与测量噪声；或者观察到的回路位移只是未观测 controller/LCL states 造成的 memory aliasing，而非 \([g_A,g_\phi]\) 的稳定结构。任一情况成立，这个 bet 都失去核心能力，而不是只损失一点精度。

最小区分实验是在 Table 2 的同一 ANPC EMT 模型中，从完全相同的完整内部状态出发，生成顺时针/逆时针成对的 \(A\)-\(\phi\) 小矩形命令回路；取三档 \(\delta A\)、三档 \(\delta\phi\) 与三档 \(\tau\)，同时保存 100 kHz 原始响应和论文式 1 kHz 低通响应。先检验成对差值 \(D=i_{dq0}^{\circlearrowright}-i_{dq0}^{\circlearrowleft}\) 是否随 orientation 反号、在小扰动区是否近似按 \(\delta A\delta\phi\) 缩放；再用相同参数量比较原 dual-path CDE、加宽但不含 path area 的 control model，以及显式输入 \(\mathbb A^{A\phi}\) 的 bracket-aware CDE，并把一种 orientation、部分 area 与 control-clock phase offset 完全留作测试。只有当 EMT 本身出现可重复的 orientation-odd、area-scaled 响应，且 bracket-aware 模型独占地预测留出顺序，同时该效应在完整状态严格重置后仍存在，才支持非交换机制；若效应不反号、不按 area 缩放，或加宽 baseline 同样恢复，则更强解释是 generic nonlinearity、带宽效应或额外容量。

与本文及近邻 Neural ODE/CDE surrogate 的实质区别可以逐项落地：problem 从同分布 trajectory rollout 变为 matched-path ordering identification；mechanism 从 slow/fast increment separation 变为 command vector fields 的 Lie bracket；representation 从 \(u(t)dt\)、\(du(t)\) 与普通 latent dimensions 变为 signed second-order iterated integrals 和低秩 bracket basis；experimental object 从 MSE、damping score 和有界波形变为闭合命令回路的 orientation-odd current displacement 及其 area scaling。它也不以 RTL 波前、event-flow、网络消元、carrier macro-operator 或 impedance kernel 为机制。由于未对这一具体组合做外部全文检索，这里是由论文 method 与 experiment 推出的候选判断，不声称 novelty。

**Wild-card alternative：** 把 \(\phi\) 从普通标量改成 dq reference frame 的 \(SO(2)\) gauge coordinate，以全局相位旋转角和 frequency ramp 为基本设计变量训练 rotation-equivariant Neural CDE，测试同一物理轨迹在未见参考系下能否只发生严格的坐标旋转；其机制是 symmetry-equivariant representation，而不是控制路径的非交换回路。
