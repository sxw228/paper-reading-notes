# Comparative Modeling and Analysis of EMT and Phasor RMS Grid-Forming Converters Under Different Power System Dynamics

- 作者：Salvatore Favuzza；Rossano Musca；Gaetano Zizzo；Jaser A. Sa’ed
- 出处：IEEE Transactions on Industry Applications，Vol. 60，No. 2
- 年份：2023（在线发表；卷期为 2024 年 3/4 月）
- DOI：10.1109/TIA.2023.3339108
- Zotero key：UXWRM3U7
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文问的是一个很具体的建模选择问题：研究 grid-forming converter（GFM）参与的电力系统动态时，什么时候 phasor RMS 模型已经足够，什么时候必须付出更高计算成本使用 electromagnetic transient（EMT）模型？作者没有把它处理成抽象的“精细模型一定更好”，而是在同一 MATLAB/Simulink Simscape Electrical 平台中，对三类 GFM 控制、两种控制层级、强弱电网和四类扰动逐项比较，试图把建模域的选择落实到“电网条件、控制结构、扰动时间尺度”这三个可操作维度上。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，是因为 GFM 的输出相角不是外部给定量，而是控制器主动形成的同步变量。传统 phasor RMS 仿真把基频载波和网络的快速电磁状态压缩掉；EMT 则保留瞬时波形和电感电流等动态。当 GFM 的快速功角控制、网络电磁时间常数和故障限流逻辑落到相邻时间尺度时，原来“机电动态用 RMS、快速电磁动态用 EMT”的边界会变模糊。[pdf:E02]（PDF 物理页 2，Eq. (3)–(11)）[pdf:E03]（PDF 物理页 3，Eq. (12)–(14) 后的分析）

工程价值在于避免两类相反错误。第一类是用 RMS 研究它没有能力表达的故障后振荡，得到过度乐观的 transient stability 结论；第二类是所有问题都使用 EMT，增加求解成本，却没有增加与研究问题相关的信息。论文最后强调，模型的好坏取决于适用范围，而不是细节越多越好。[pdf:E10]（PDF 物理页 11，Section VII）

## § 2 — 前人工作与不足

论文直接指出，已有文献已经讨论过 RMS 与 EMT 的比较、converter-interfaced generation 的短期电压稳定性，以及 GFM 在不同仿真平台中的实现；三种受测控制也都不是新提出的，分别是 power-synchronization control（PSC）、virtual synchronous machine（VSM）和 feedforward angle control。作者认为仍有三个缺口：已有比较常跨不同商业平台，缺少在 MATLAB/Simulink 同一工具链内的对应实现；比较条件不够完整，未同时覆盖强/弱电网、single-loop/multi-loop 和三种典型功角动态；缺少把结论放回标准 benchmark system 的应用验证。[pdf:E01]（PDF 物理页 1，Section I 末尾及续页贡献列表）

这些不足不是说 prior work “完全没有比较”，而是比较中的非研究变量没有被充分控制。若 RMS 与 EMT 分别来自不同软件、不同初始化或不同控制结构，曲线差异无法明确归因于建模域。本文的解决策略是让两种模型共享平台、控制律、solver 类型和工况，只保留时间域表示及相应步长等必要差异。[pdf:E05]（PDF 物理页 6，Section IV-A/B）[pdf:E07]（PDF 物理页 8，Table I）

需要保留边界：论文是在既有比较工作的基础上补充一组系统化仿真证据，并没有证明它给出的场景覆盖了所有 GFM 拓扑、所有不平衡故障或所有 converter hardware。

## § 3 — 重建作者的思考路径

可以把作者到达这个研究设计的路径重建为四步；这是基于论文背景与数学框架的合理推断，不是作者逐字陈述。

1. 先从物理差异出发。EMT 网络把线路电感写成微分状态，电流不会瞬时跳到新的稳态；phasor RMS 网络把同一支路压缩成工频复阻抗，等价于假定被删掉的快速网络动态已经完成。[pdf:E02]（PDF 物理页 2，Eq. (5)–(11)）[pdf:E03]（PDF 物理页 3，Eq. (13)–(14) 与随后段落）
2. 再观察 GFM 的特殊性。GFM 用功率误差直接产生同步角，PSC、VSM 和 feedforward angle control 的惯性与阻尼不同；因此，控制器可能在网络电磁状态尚未衰减时就改变相角。快功角控制比慢功角控制更可能“看到”RMS 被删掉的状态。[pdf:E04]（PDF 物理页 4，Fig. 5–8）
3. 接着引入结构性非线性。multi-loop 控制含 inner current controller、current limiter 和 fault 时的 freeze 逻辑；故障清除会同时释放网络储能与控制器冻结状态。即使 fault-on 段看似相同，post-fault 段也可能因被删掉的快速状态而分叉。[pdf:E03]（PDF 物理页 3，Fig. 2–4 及相邻正文）[pdf:E04]（PDF 物理页 4，freeze 说明）
4. 最后设计按时间尺度排序的扰动：功率参考阶跃和低频频率变化代表 smooth angle dynamics，phase jump 与短路代表 quick angle dynamics。若差异确实由时间尺度分离失效造成，前两类应匹配，后两类应在快控制、强网或限流条件下暴露差异。Section V 的实验正是按这个可证伪预期展开。[pdf:E07]（PDF 物理页 8，Section V 与 Fig. 23）[pdf:E08]（PDF 物理页 9，Fig. 24–25 与 Section V-B–D）

## § 4 — 核心 Intuition

phasor RMS 不是简单把 EMT 曲线画得粗一点，而是删除了网络的快速电磁状态，并用工频相量的代数关系替代它。只要系统相角平滑变化，被删除的状态足够快地衰减，RMS 与 EMT 就会给出相同的主动态；当 phase jump、短路清除、快功角控制和 current limiting 同时出现时，网络状态与控制状态会在同一时间窗口交换能量，RMS 就可能漏掉真正的 post-fault 振荡。[pdf:E03]（PDF 物理页 3，Section II 末段）[pdf:E09]（PDF 物理页 10，Table II 与 Section V-E）

## § 5 — 具体方法与完整 Pipeline

作者的 pipeline 可以按“一套控制、两种电气表示、同一组事件、逐条件比较”理解。

1. **搭建共同测试系统。** 一个 GFM controlled source 经 LC filter 和 interconnection impedance 接入中压网络，末端接本地负荷；电网等值为 fully controllable voltage source，以便直接注入功率参考变化、频率变化、相角跳变和三相短路。[pdf:E06]（PDF 物理页 7，Fig. 22 与 Section V 开头）
2. **配置三种同步环。** PSC 用积分型功角控制形成快速响应；VSM 用惯性常数与 droop 模拟同步机式功角动态；feedforward angle control 在 VSM 类结构上增加前馈。每种控制都分别放入 single-loop 与 multi-loop 结构；后者含 voltage loop、inner current loop、circular current limiter 和 fault freeze。[pdf:E03]（PDF 物理页 3，Fig. 2–4）[pdf:E04]（PDF 物理页 4，Fig. 6–9）
3. **构造 phasor RMS 分支。** Simscape 设为 “Frequency and time”，GFM 用复电压 controlled source；同步信号只保留相对角 \(\theta_{\mathrm{RMS}}=\Delta\theta\)，坐标变换是复数旋转。网络支路由工频复阻抗表示，不显式积分快速电感状态。[pdf:E05]（PDF 物理页 6，Fig. 14–16 与 Section IV-A）
4. **构造 EMT 分支。** Simscape 设为 “Time”，source 输入瞬时三相 modulation wave；同步角为 \(\theta_{\mathrm{EMT}}=\omega_n t+\Delta\theta\)，abc 与 converter dq frame 之间用 Park transform。论文说明控制输出还可接 average inverter 或 full switching inverter，但当前比较的核心是同一控制下的瞬时电气网络表示。EMT 模型不会像 RMS 一样自动从 loadflow steady state 启动，因此作者先用 twin model 计算初始节点电压，再求电流并写入各电感、电容的 Initial Targets。[pdf:E05]（PDF 物理页 6，Fig. 17–18 与 Section IV-B）[pdf:E06]（PDF 物理页 7，Fig. 19–21 与初始化说明）
5. **锁定比较参数。** 两个分支使用同一种 Backward Euler solver；RMS sample time 为 \(10^{-2}\,\mathrm{s}\)，EMT 为 \(10^{-4}\,\mathrm{s}\)。强网短路容量为 150 MVA、SCR = 15；弱网为 15 MVA、SCR = 1.5。converter 额定容量为 10 MVA，限流值为 1.3 pu，fault ride-through 检测电压阈值为 0.8 pu。[pdf:E07]（PDF 物理页 8，Table I）
6. **施加事件并比较。** 对每种控制、控制层级和电网强度，比较 active power、current、frequency 或 voltage 的 EMT 实线与 RMS 虚线；再把 VSM multi-loop 模型放入 modified two-area four-generator benchmark，检查发电损失与三相短路是否复现相同规律。[pdf:E07]（PDF 物理页 8，Fig. 23）[pdf:E09]（PDF 物理页 10，Fig. 27–28 与 Section VI）

论文没有报告 FPGA 实现、定点位宽、LUT/BRAM/DSP 资源、流水线、板级时序或 HIL/PHIL 实测。它只指出 MATLAB/Simulink 模型具有向 rapid control prototyping 和 hardware-in-the-loop 部署的潜在可迁移性；这不能外推为已经证明 FPGA 实时可行。[pdf:E05]（PDF 物理页 6，Section IV 引入段与两种实现）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文最重要的数学不是某个 GFM 控制律，而是解释 EMT 与 RMS 为什么会在快事件中分叉。

先看角度表示。EMT 的 converter 与 grid 瞬时相角分别写为

\[
\theta_c=\omega_n t+\delta_c,\qquad
\theta_g=\omega_n t+\delta_g ,
\]

其中 \(\omega_n=2\pi f_n\)，\(\delta_c,\delta_g\) 是相对相位偏移。EMT 使用含基频积分项的周期角 \(\theta\)，而 RMS 只使用 steady-state 中近似恒定的相对偏移 \(\Delta\theta=\delta\)。对 GFM 而言，\(\delta_c\) 正是功角控制器形成的有效控制信号。[pdf:E02]（PDF 物理页 2，Eq. (3)–(4) 与相邻定义）

在 EMT 中，两电压源之间的 RL 支路满足

\[
\mathbf v_c=R\mathbf i+L\frac{d\mathbf i}{dt}+\mathbf v_g .
\]

用以 \(\theta_c\) 定向的 Park transform 变到 converter dq frame 后，

\[
\mathbf v_c^{dq}=
\begin{bmatrix}
R&-\omega L\\
\omega L&R
\end{bmatrix}\mathbf i^{dq}
+L\frac{d\mathbf i^{dq}}{dt}
+\mathbf v_g^{dq}.
\]

Laplace 域的对角项因此包含 \(R+sL\)。这里的 \(sL\) 不是符号装饰，它表示电感电流是一个要随时间积分的真实状态；故障发生或清除后，电流与储能不能瞬时落到新的代数解。[pdf:E02]（PDF 物理页 2，Eq. (5)–(8)）

RMS 分支把 source 写成工频相量 \(\bar V_c=V_c e^{j\delta_c}\)、\(\bar V_g=V_g e^{j\delta_g}\)，支路关系为

\[
\bar V_c=(R+jX)\bar I+\bar V_g .
\]

再通过角度 \(\delta_c\) 的二维旋转变到 converter dq frame，得到

\[
\mathbf V_c^{dq}=
\begin{bmatrix}
R&-X\\
X&R
\end{bmatrix}\mathbf I^{dq}
+\mathbf V_g^{dq}.
\]

即使写到 Laplace 域，这个矩阵仍没有 \(sL\)；网络电流只由当前相量代数决定。[pdf:E02]（PDF 物理页 2，Eq. (9)–(11)）[pdf:E03]（PDF 物理页 3，Eq. (12)–(14)）

物理上，二者的误差条件由时间尺度比值决定：若扰动和控制功角变化远慢于网络 \(L/R\) 动态，EMT 中的 \(L\,d\mathbf i/dt\) 很快衰减，RMS 是合理的 quasi-steady approximation；若功角或故障边界变化与 \(L/R\) 同量级，被删掉的状态会参与控制反馈，RMS 与 EMT 就可能给出不同的峰值、阻尼甚至不同的 post-fault trajectory。论文的实验是对这一推论的数值检验。[pdf:E03]（PDF 物理页 3，Section II 末段）

## § 7 — 实验设计与结论

**问题 1：smooth power-angle dynamics 下，RMS 是否足够？**  
实验：active power reference 增加 0.3 pu，覆盖三种同步控制、single/multi-loop 和强/弱电网。答案：EMT 与 RMS 基本重合；multi-loop 会让慢同步控制的阶跃响应更振荡，但不破坏两种建模域之间的匹配，grid strength 也没有改变这个结论。[pdf:E07]（PDF 物理页 8，Fig. 23 与 Section V-A）

**问题 2：低频系统频率变化是否需要 EMT？**  
实验：电网频率叠加 \(-200\,\mathrm{mHz}\) steady-state deviation，以及幅值为总变化 0.1%、自然频率 1 Hz 的低频振荡。答案：三种控制在两种时域中基本给出相同响应；VSM 在强网下更容易呈现明显振荡，但这属于控制与 grid strength 的动态，不是 RMS/EMT 之间的主要失配。[pdf:E08]（PDF 物理页 9，Fig. 24 与 Section V-B）

**问题 3：突然相角变化会不会暴露 RMS 的边界？**  
实验：电网相角突然跳变 \(-1^\circ\)。答案：具有明显惯性效应的 VSM 与 feedforward angle control 仍较好匹配；fast power-angle dynamics 的 PSC 中，EMT 的响应更渐进，RMS 偏快，而且强网使差异更明显。论文据此把 failure 条件指向“快同步控制 + quick angle dynamics”，而不是笼统指向所有 GFM。[pdf:E08]（PDF 物理页 9，Fig. 25 与 Section V-C）

**问题 4：短路和 current limitation 会不会让 RMS 漏掉故障后动态？**  
实验：converter terminal 附近施加 100 ms 三相短路；强网的 voltage sag 约 0.2 pu，弱网约 0.5 pu。答案：single-loop 下没有显著差异；multi-loop 中，两种模型在 fault-on 段仍可接近，但 RMS 漏掉 fault clearance 后的 oscillation，强网和快 PSC 最明显。Table II 将强网 short-circuit 标为 multi-loop 下失败，弱网则写为“might be acceptable”。[pdf:E08]（PDF 物理页 9，Section V-D）[pdf:E09]（PDF 物理页 10，Fig. 26、Table II 与 Section V-E）

**问题 5：上述规律放进更完整系统后是否仍存在？**  
实验：在 two-area four-generator benchmark 的每个 area 增加两个 VSM multi-loop converter，保持原 loadflow operating point；Area 1 施加 200 MW generation loss 与 100 ms 三相短路。答案：generation loss 下两种模型的整体动态一致，RMS 只漏掉暂态开始时的快速电压分量；短路下 RMS 漏掉 fault-on 与 post-fault 的系统振荡。benchmark 因而支持“平滑事件可用 RMS、快速故障动态优先 EMT”的主结论。[pdf:E09]（PDF 物理页 10，Fig. 27–28 与 Section VI）[pdf:E10]（PDF 物理页 11，Fig. 29 与 Section VII）

不能从这些实验外推三件事：不能外推到不平衡 fault、harmonic interaction 或 switching-frequency phenomena；不能把理想/平均化 converter 的 EMT 结果视为 full switching hardware 的完整真相；不能由 simulation sample time 推出任何 FPGA 或 real-time execution guarantee。

## § 8 — Take-aways

**5 句话**

1. EMT 与 phasor RMS 的关键差别，是前者保留网络电磁状态和绝对瞬时角，后者用工频相量代数关系与相对角替代它们。[pdf:E02]（PDF 物理页 2，Eq. (3)–(11)）
2. 对 active-power reference step 和低频 frequency transient 这类 smooth angle dynamics，RMS 与 EMT 在本文测试范围内基本匹配。[pdf:E07]（PDF 物理页 8，Fig. 23）[pdf:E08]（PDF 物理页 9，Fig. 24）
3. 对 phase jump 与 short-circuit 这类 quick angle dynamics，快功角控制、强网和 multi-loop current limitation 会把被 RMS 删除的状态放大成可观察差异。[pdf:E08]（PDF 物理页 9，Fig. 25 与短路说明）[pdf:E09]（PDF 物理页 10，Fig. 26 与 Table II）
4. 最危险的失配不是 fault-on 波形略有误差，而是 RMS 可能完全漏掉 fault clearance 后的 oscillation，从而误判 transient stability。[pdf:E10]（PDF 物理页 11，Fig. 29 与 Section VII）
5. 这篇论文给出的是建模域选择的条件化证据，不是“EMT 总是好”或“RMS 总是坏”的二元结论，也没有提供 FPGA 实现证据。

**3 句话**

1. 当扰动比网络 \(L/R\) 动态慢很多时，phasor RMS 是有效的 quasi-steady approximation。
2. 当 quick angle event、fast GFM synchronization 与 current-limit state 同时出现时，应优先用 EMT 检查 post-fault trajectory。
3. 在选择模型前，先问研究对象的时间尺度、控制结构和 grid strength，而不是只问系统规模。

**1 句话**

GFM 让控制时间尺度贴近网络电磁时间尺度，因此 RMS 是否可信取决于具体事件和控制结构，而不是取决于它是否曾经适合传统同步机系统。

## § 9 — 最脆弱的假设

最脆弱的假设是：**本文的 EMT 分支可以作为判断 phasor RMS 缺失动态的充分参考真相，并且观察到的差异主要来自网络电磁状态，而不是 converter hardware、初始化或限流实现的其他细节。**

论文为这个假设提供了三类支持。第一，两种分支在同一 Simscape 平台上实现，共用控制律和 Backward Euler solver，减少跨软件差异。[pdf:E05]（PDF 物理页 6，Section IV）[pdf:E07]（PDF 物理页 8，Table I）第二，作者显式处理 EMT steady-state initialization，避免把启动漂移误当成域差异。[pdf:E06]（PDF 物理页 7，初始化段）第三，差异随事件速度、控制速度、grid strength 和 current-limit structure 有规律地出现，而不是在所有场景随机出现。[pdf:E09]（PDF 物理页 10，Table II）

但证据仍不充分。论文说明 EMT 控制输出可以接 ideal controlled source、average inverter 或 full switching inverter，却没有用 hardware measurement 或系统性的 switching-model sensitivity 来证明 fault clearance 后的振荡在这些实现层级之间保持不变。[pdf:E05]（PDF 物理页 6，Fig. 17–18）[pdf:E06]（PDF 物理页 7，Fig. 19）此外，所有核心事件都是平衡三相、参数固定的 simulation。若 post-fault 差异主要由特定 freeze/initialization 逻辑或平均化 converter 假设产生，而不是 RMS 删除网络状态这一机制产生，那么把结论推广为一般建模指南就会失效。这是基于证据的批评，不是论文已经证明的问题。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 benchmark，而是“reference step 能匹配、strong-grid short-circuit 的 multi-loop PSC 会分叉”这一对照，因为它在同一最小系统里同时给出正对照与反例。

- **数据与模型：**按 Table I 建立 Fig. 22 的 two-source system，只实现 PSC；保留 single-loop 和带 current limiter/freeze 的 multi-loop 两种结构。强网用 \(S_k=150\,\mathrm{MVA}\)、SCR = 15，弱网用 \(S_k=15\,\mathrm{MVA}\)、SCR = 1.5；converter 为 10 MVA，\(I_{\max}=1.3\) pu。[pdf:E06]（PDF 物理页 7，Fig. 22）[pdf:E07]（PDF 物理页 8，Table I）
- **两种数值模型：**EMT 支路显式积分 RL/LC 状态并使用 \(\theta=\omega_n t+\Delta\theta\)；RMS 支路使用工频复阻抗与 \(\Delta\theta\)。先严格对齐 steady-state、control state、fault timing 和 output sampling。
- **两个事件：**先施加 0.3 pu active-power reference step，再施加 terminal 附近 100 ms 三相短路；不要先扩展到三种控制或大 benchmark。
- **测量：**比较 current、active power、converter angle/frequency 的 waveform error、post-fault oscillation frequency、damping ratio 和 peak current；同时记录把 EMT 输出低通并降采样到 RMS bandwidth 后的误差，排除只由观测带宽造成的视觉差别。
- **支持条件：**reference step 的低频轨迹接近，而 strong-grid multi-loop fault 中 RMS 在 fault clearance 后显著低估振荡；weak-grid 或 single-loop 中差异减弱。
- **反驳条件：**在严格对齐初始化、solver convergence 和输出带宽后，RMS 也能恢复相同 post-fault mode，或所谓差异随 time-step 收敛而消失。出现这种结果应先怀疑数值或实现，而不是继续增加工况。

## § 11 — 最强反例设计

最强反例不是再找一个 RMS 与 EMT 不同的故障，而是证明论文归因错了：**post-fault 差异来自特定 average-source/current-freeze 实现，而不是 phasor RMS 删除网络状态的必然后果。**

具体做法是建立三层模型：原 phasor RMS、在 RMS 上只增加动态 RL 支路状态的 dynamic-phasor/reduced EMT、以及含 DC link、PWM 和 switching devices 的 full EMT。对 PSC multi-loop 做 \(L/R\)、SCR、current-limit threshold、freeze release timing 和 controller bandwidth 的联合 sweep，并让三层模型使用同一个经过验证的 initialization。若只增加一个动态网络状态的 reduced model 就能在所有 quick-angle 工况恢复 full EMT 的 post-fault pole，而原论文的 average EMT 又在 switching EMT 下改变了振荡模式，那么真正的结论应是“需要保留哪些状态”，而不是“必须切换到 EMT 域”。反过来，若 full EMT、average EMT 与 dynamic network model 都稳定地支持同一个额外振荡，而纯 algebraic RMS 始终漏掉它，论文的机制解释才被显著加强。

这个反例强在它同时攻击参考真相和因果归因，并且能给出可复用的模型阶次判据，而不只是报告另一组曲线。

## § 12 — Follow-up Research Idea

**候选研究方向：构建事件与控制状态感知的自适应 hybrid RMS–EMT 模型，不预先按元件固定分区，而是在仿真中检测时间尺度分离何时失效。**由于本任务没有联网检索相关工作，这里不声称 novelty。

（a）未满足的需求是：大系统 transient stability study 希望保留 RMS 的规模优势，但 GFM fault response 又可能在少数时间窗口需要 EMT 状态；全程 EMT 成本高，全程 RMS 可能漏掉决定稳定性的 mode。本文已经证明“所需细节随事件和控制结构变化”，却仍要求分析者在运行前二选一。[pdf:E09]（PDF 物理页 10，Table II）[pdf:E10]（PDF 物理页 11，Section VII）

（b）电力系统领域认可的价值不只是加速，而是给出可解释的 validity certificate：每个区域在何时满足 quasi-steady phasor assumption，何时因为 \(|d\Delta\theta/dt|\)、current-limit activation 或 estimated network-state residual 超阈值而切换到 EMT；切换后还要保持能量、相角和 controller state 连续。若能在标准 benchmark 与 hardware-in-the-loop 上同时证明稳定性判据不漏检且计算量显著低于全 EMT，它会比静态模型选择指南更具工程价值。

（c）可借鉴相邻领域的工具包括 hybrid systems 的 guard/reset map、adaptive model-order reduction、a posteriori error estimator，以及多速率积分中的 state projection。关键不是增加一个 heuristic switch，而是让切换判据直接估计被 RMS 删除的 \(L\,d\mathbf i/dt\) 项是否已经不可忽略。

（d）第一个证伪实验应使用本文 modified two-area benchmark 的 100 ms short-circuit：如果 hybrid 模型不能在 RMS 区域快速运行、在 fault 与 post-fault 窗口恢复 full EMT 的 oscillation frequency、damping 和 peak current，或者切换本身产生虚假能量与相角跳变，就应立即否定该方案。

（e）它与本文工作的实质区别是改变问题定义。本文问“一个场景应选 RMS 还是 EMT”；候选方向问“能否让模型自己给出局部、时变且可核验的适用范围，并只在必要处恢复被删除的状态”。这把离线经验指南变成可执行的误差控制机制。
