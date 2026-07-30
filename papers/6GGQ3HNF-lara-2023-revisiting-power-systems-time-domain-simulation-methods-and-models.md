# Revisiting Power Systems Time-Domain Simulation Methods and Models

作者：Jose Daniel Lara；Rodrigo Henriquez-Auba；Deepak Ramasubramanian；Sairaj Dhople；Duncan S. Callaway；Seth Sanders

出处：IEEE Transactions on Power Systems，Vol. 39，No. 2，pp. 2421–2437

年份：2023

DOI：10.1109/TPWRS.2023.3303291

Zotero key：6GGQ3HNF

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是“哪一种仿真器最快”，而是一个更靠前的问题：在 inverter-based resources（IBR）占比上升后，研究者口中的 EMT、QSP、RMS、dynamic phasor、dq0-model 等名称究竟隐含了哪些数学变换、物理简化和数值假设；面对特定稳定性问题，什么才算“有效解”。作者指出，同步机主导系统中的主要时间尺度往往由磁链、机电运动和机械控制等物理过程自然分开，而 IBR 的 modulation、PLL、电压环、电流环和功率环由控制设计人为耦合，较高频率的控制交互因而进入系统级稳定性分析。论文的核心任务是从第一性原理梳理 time-domain simulation 的模型与时间推进方法，建立按频率带宽、网络表示和软件成熟度组织的 taxonomy，并用一个 IBR 主导小系统说明不同简化会改变可见轨迹。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，是因为模型不是被动的“精度旋钮”。是否保留网络电磁状态、是否把三相量变换到旋转坐标系、是否将快状态代数化，会共同决定模型能否看到某类振荡、方程是否 stiff、允许的步长以及适用的求解器。选错模型可能不是得到稍大的数值误差，而是把控制交互、次同步现象或保护动作从问题定义中直接删掉。作者也明确收窄了贡献边界：本文不提供一种通用的 simulation-domain 选型指南，而是解释常用方法内嵌的假设，并讨论它们在 IBR 系统中的能力与限制。[pdf:E02]（PDF 物理页 2，Section I.A 与 Section II.A）

## § 2 — 前人工作与不足

论文把已有工作分成几条彼此相关、但尚未形成统一语言的链条。稳定性分类和 IEEE Std 1110-2019 已能为同步发电机模型复杂度提供经验依据；IBR 研究也分别讨论了网络电路动态的理论条件、实际大系统中的模型精度、复合网络—发电机—逆变器模型，以及 EMT 加速方法。问题在于，这些成果通常从某一设备、某一频段或某一软件环境出发，文献中的“slow/fast”“dynamic phasor”“RMS/EMT”等术语并不自动对应同一组假设。作者因此不把 QSP 与 EMT 当作两个足够精细的标签，而是把网络表示、频率带宽、平衡性、状态数、时间变性和软件可用性拆开讨论。[pdf:E02]（PDF 物理页 2，Section I 的 related-work 段落与贡献列表）

论文给出的直接不足是：传统两分法无法说明同属 EMT 的 waveform、dq0 和 dynamic-phasor model 为什么有完全不同的状态数、初始化要求和数值方法，也无法说明同属 QSP 的 positive-sequence、RMS unbalanced 与 algebraic-network dq0 各自丢弃了什么。Fig. 2 将 QSP 与 EMT 再按 positive sequence、RMS unbalanced、dq0、dynamic phasor、waveform 及是否显式开关细分；作者同时区分 transformation 与 simplification：前者是在适用条件下改变坐标或信号表示，后者则以近似真实动态为代价降低复杂度。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Section II.B–III）

本文自身也不是“新求解器论文”。它的新增价值主要是语义澄清、统一 taxonomy、假设推导和示例验证，而不是提出新的 FPGA 架构、实时仿真平台或大规模 benchmark。相关软件的成熟度只按 mature/research 做分类，未给出可复现的商业工具横向性能数据。[pdf:E10]（PDF 物理页 10，Table I）

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为四步。第一步，从传统仿真的代价来源出发：三相正弦量让模型显式随时间变化，完整网络与器件状态又把最快电磁时间尺度带入系统模型，因此固定步长可能被最小时间常数锁死。第二步，观察到工程上长期使用两类“删复杂度”的手段：用 averaging/dynamic phasor 或 Park transform 把载波上的快速正弦变化变成较慢的 envelope；用 singular perturbation theory（SPT）在快子系统稳定且根可分离时把快微分状态代数化。动态相量的 Fourier、线性算子和 shifted-frequency 三条定义虽然来源不同，却导向相同的导数性质，这为统一讨论“快/慢”提供了信号带宽意义上的语言。[pdf:E04]（PDF 物理页 4，Eqs. (2)–(9)，Section III.A.2）

第三步，作者追问这些手段何时是可逆变换、何时是有损近似。Dynamic phasor 要求信号在所选载频附近窄带；表示任意无零序三相信号通常需要正、负频率两个复相量，而平衡三相时负频率分量为零，单一正频率相量才足够。高频信号可能需要很多 harmonic states，新增状态数会抵消增大步长的收益；单载频也可能产生 demodulation error。[pdf:E05]（PDF 物理页 5，Section III.A.2–3，Eqs. (10)–(15)）

第四步，把这些条件带回电网与 IBR 控制。Park transform 本身对三相信号可逆，但只有恰当选取旋转角度才会把模型变成低带宽或 time-invariant 形式；同步机转子天然给出局部参考系，IBR 则依赖 PLL 或其他控制估计本地频率，网络简化会反过来改变频率测量与控制响应。[pdf:E06]（PDF 物理页 6，Section III.B，Eqs. (16)–(21)）随后，SPT 给出另一种“快/慢”：若快子系统由小参数缩放、代数根独立且 boundary-layer dynamics 稳定，就能令小参数趋零，把快状态替换为慢状态的代数函数，得到 quasi-steady-state model。[pdf:E07]（PDF 物理页 7，Section III.C，Eqs. (22)–(25)）由此自然得到论文的中心判断：模型类别不应先于研究现象而定，必须从“要保留哪种物理信息”反推允许的 transformation、simplification 和 integrator。

## § 4 — 核心 Intuition

核心 intuition 是：仿真成本主要由模型中最快、最难积分的动态和网络方程结构决定；若能在明确条件下把载波移到基带，或证明快状态迅速收敛到稳定流形，就能用更慢、更少或更规整的状态表示同一研究对象。反过来，若窄带、平衡、时间尺度分离或稳定根条件不成立，所谓“降阶”会删掉目标现象，模型名称再熟悉也不能保证答案有效。[pdf:E03][pdf:E07]（PDF 物理页 3，taxonomy 与 simplification/transformation 定义；物理页 7，SPT 条件）

## § 5 — 具体方法与完整 Pipeline

本文的方法是一套模型选择与解释 pipeline，而不是单一算法。以文中的三母线 line-trip 示例为线索，可以按以下顺序理解：

1. **定义问题和输出。** 输入是设备状态方程、网络电路方程、初值、扰动和待观察量；输出是扰动后的有界时间轨迹。论文把 time-domain simulation 明确拆成“system model”与“time-stepping algorithm”两层，后者不能脱离前者选择。[pdf:E02]（PDF 物理页 2，Eqs. (1a)–(1b) 与 Section II.A）
2. **确定网络表示。** Waveform EMT 保留 abc 波形和网络电磁动态；dq-EMT 用 Park transform 把平衡三相 π-line 变换成复数 dq ODE；QSP 再把网络导数项置零，得到 admittance matrix 形式的 algebraic network 与 index-1 DAE。对 50/60 Hz 系统，文中给出的 π-line 缩放项约为 \(10^{-3}\)；示例性说明是 2 Hz 转子动态对应约 3% 的网络约化误差，因此忽略网络动态的模型不宜研究大于 10 Hz 的控制交互或振荡。[pdf:E08]（PDF 物理页 8，Fig. 3，Eqs. (26)–(29)，Section IV.A）
3. **确定设备细节。** 同步机可通过 Park transform 去掉转动电感的显式时变项，再在 SPT 条件下忽略定子磁链的快速导数。IBR 则包含级联电压环、电流环、滤波器和系统级控制；若内环时间尺度确实足够快，可把其跟踪误差代数化，但这等价于假设系统级 reference 被无误差跟踪。滤波器约 \(10^{-3}\,\mathrm{s}\) 的时间常数也只有在研究范围允许时才能消去。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Figs. 4–5，Eqs. (30)–(32)，Section IV.B–C）
4. **选 simulation category。** Table I 把 positive-sequence/RMS balanced、RMS unbalanced、algebraic-network dq0、RMS dynamic phasor、waveform EMT、dq0-EMT 和 EMT dynamic phasor按多频/不平衡能力、网络表示和软件成熟度对齐。决定性维度不是名称，而是网络电路是否动态、信号是否窄带、是否允许非对称，以及现有软件能否求解该方程结构。[pdf:E10]（PDF 物理页 10，Table I 与 Section V.A）
5. **选 integrator。** Positive-sequence QSP 常用 partitioned explicit 方法；waveform EMT 常用 Dommel 路线的梯形积分和 numerical integration substitution；dq-EMT 的多时间尺度 ODE 可能很 stiff，需要 simultaneous implicit 方法。固定步长适合显式时变模型，time-invariant 模型可用 variable-step solver，但论文指出商业 EMT/QSP 软件仍多采用 fixed step。[pdf:E11][pdf:E12]（PDF 物理页 11–12，Section V.B–C，Eqs. (33)–(36)）
6. **检查接口与事件。** IBR 可用 Norton current-source 或 Thevenin voltage-source interface；两者电路等价，但前者可能让 admittance matrix 接近奇异并在弱网中造成逐步迭代不收敛。文中真实示例是三母线高压网络，G1 为 VSM grid-forming inverter，G2 为 droop-controlled inverter，扰动为母线 1–2 线路切除；waveform EMT 用 PSCAD，dq-EMT 与 QSP 用 PowerSimulationsDynamics.jl。[pdf:E13]（PDF 物理页 13，Figs. 6–8 与 Section V.D）

论文未报告以下实现细节：开关器件级 event scheduler 的具体数据结构；多速率分区与同步算法；GPU/FPGA kernel；定点数位宽、量化误差、流水线深度、片上存储、资源利用率、时钟频率或 real-time deadline。它只在一般层面提到并行线性代数可用于大规模 stiff system 的线性求解，没有给出本文示例的并行实现或加速数据。[pdf:E12]（PDF 物理页 12，Section V.C.2）因此不能从本文推导 FPGA 实现性能。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有一个单独的定理，而是用三条数学链解释模型如何从 waveform 走向 dq-EMT 或 QSP。

**第一条：从连续系统到 time stepping。** 设备与网络写成

\[
\dot{\mathbf{x}}=F(\mathbf{x},\mathbf{y},\boldsymbol{\eta},t),\qquad
\dot{\mathbf{y}}=G(\mathbf{x},\mathbf{y},\boldsymbol{\psi},t).
\]

\(\mathbf{x}\) 是设备状态，\(\mathbf{y}\) 是网络状态；仿真器在离散时间线上根据已有状态推进到下一步。这个定义先把“模型保留什么”与“如何积分”分开，再指出两者互相约束。[pdf:E02]（PDF 物理页 2，Eqs. (1a)–(1b)）

**第二条：把载波移到基带。** 对近周期信号，Fourier dynamic phasor 写成

\[
s(t)=\sum_{k=-\infty}^{\infty}\langle s\rangle_k(t)e^{jk\Omega t},\qquad
\left\langle\frac{ds}{dt}\right\rangle_k
=\frac{d\langle s\rangle_k}{dt}+jk\Omega\langle s\rangle_k .
\]

直觉是：\(e^{jk\Omega t}\) 承担快速载波，\(\langle s\rangle_k(t)\) 只描述 envelope。线性算子和 shifted-frequency 两种推导也得到同一导数性质，因此 transformation 后仍能正确表达导数，只要信号在载频附近窄带、反变换唯一。[pdf:E04]（PDF 物理页 4，Eqs. (2)–(9)）对三相量，平衡条件使负频率分量为零，单个正频率复相量即可无损表示；不平衡时一般必须同时保留正、负频率分量，否则不是可逆表示。[pdf:E05]（PDF 物理页 5，Eqs. (10)–(15)）Park transform 则把 abc 量映射到旋转 dq0 坐标；当参考角与系统频率恰当配合时，平衡正弦量在 dq 轴上成为慢变或常量，但 IBR 的本地频率来自控制估计，网络近似可能污染这个闭环。[pdf:E06]（PDF 物理页 6，Eqs. (16)–(21)）

**第三条：把快微分状态代数化。** SPT 将状态分成慢变量与乘小参数 \(\varepsilon\) 的快变量：

\[
\dot{\mathbf{x}}_s=F_s(\cdot,\varepsilon),\qquad
\varepsilon\dot{\mathbf{x}}_f=F_f(\cdot,\varepsilon).
\]

令 \(\varepsilon\to0\) 后，快方程变成 \(0=F_f\)。只有当相关代数根在研究域内独立，并且 boundary-layer Jacobian 的 eigenvalue 条件保证快动态不发散时，才能写成 \(\mathbf{x}_f=R_x(\mathbf{x}_s,\mathbf{y}_s,\boldsymbol{\eta})\)，再代回慢方程得到 quasi-steady-state model。[pdf:E07]（PDF 物理页 7，Eqs. (22)–(25)）π-line 的 dq ODE 就沿此路径把导数项置零，得到 \(Y\mathbf{v}=\mathbf{i}\) 的 algebraic network 与设备—网络 index-1 DAE；这是 QSP 计算便宜的数学来源，也是它看不到被删电磁动态的原因。[pdf:E08]（PDF 物理页 8，Eqs. (27)–(29)）

最后，Taylor expansion 表明步长 \(\Delta t\) 越小，截断高阶项带来的误差越低但迭代次数越多；stiffness ratio 则概括最快与最慢衰减尺度的跨度。Implicit method 每步要解 nonlinear system，通常归结为大规模线性方程；transformation/SPT 的计算价值在于降低带宽或 stiffness，使较大的步长或 explicit method 成为可能。[pdf:E12]（PDF 物理页 12，Eqs. (33)–(36)）

## § 7 — 实验设计与结论

**问题一：平衡三相条件下，dq-EMT 能否复现 waveform EMT 的关键轨迹？** 作者在三母线 IBR 主导系统切除母线 1–2 线路，网络采用 π-line，G1 使用 VSM control、G2 使用 droop control；用 PSCAD waveform EMT 与 PSID.jl dq-EMT 对比母线电压和控制器内部状态。[pdf:E13]（PDF 物理页 13，Figs. 7–8）答案是：在该平衡、理想源输出的例子中，dq-EMT 与 waveform EMT 的母线电压高频振荡和 PLL/VSM 内部状态轨迹贴合，支持“适用条件内的 dq transformation 可保留目标电磁动态”。[pdf:E14]（PDF 物理页 14，Fig. 9 与 Section V.D）

**问题二：QSP simplification 丢掉了什么？** 作者在同一扰动和控制设置下用 algebraic network 的 positive-sequence QSP 比较。答案是：QSP 不显示 waveform/dq-EMT 中的高频振荡，且控制状态轨迹略有偏移；这说明线路与滤波器的电磁动态可以进入 PLL 和 VSM frequency estimate，在更极端工况下可能影响稳定性。[pdf:E13][pdf:E14]（PDF 物理页 13–14，Figs. 8–9）

**问题三：保留电磁状态付出多少数值代价？** dq-EMT 与 QSP 均用 Rodas5 adaptive solver，absolute/relative tolerance 都设为 \(10^{-14}\)；waveform EMT 用 \(5\,\mu s\) fixed step。报告的 stiffness ratio 分别为 dq-EMT 的 2185 与 QSP 的 105。10 秒仿真中，waveform fixed-step 做 \(2\times10^6\) 次 evaluation，dq-EMT 做 31,736 次、步长范围 \(1.7\,\mu s\) 到 \(7\,ms\)，其中仅 18 次小于 \(1\,ms\)；QSP 做 567 次、步长范围 \(1\,\mu s\) 到 \(0.1\,s\)。这些结果支持“变换与简化能显著减少 evaluation 数”，但论文没有报告统一硬件上的 wall-clock time、memory、并行效率或端到端 speedup，不能把 evaluation count 直接等同于实际加速比。[pdf:E14]（PDF 物理页 14，Section V.D）

不得外推的范围包括：示例只有一个小型、平衡三相、line-trip 工况；waveform 实现采用与 PSID.jl 匹配的 custom PSCAD control blocks 和理想源输出；没有器件级 switching、current limiting、unbalanced fault、谐波扫频、大规模系统、参数不确定性或 FPGA/HIL 验证。

## § 8 — Take-aways

**5 句话。** 第一，QSP 与 EMT 只是顶层标签，真正决定可见物理与数值代价的是频率带宽、网络表示、平衡性、状态保留和软件实现。第二，dynamic phasor 与 Park transform 可以在窄带、参考系合适、平衡等条件下把快速 waveform 变成低带宽 envelope，而 SPT 只有在快子系统根与稳定性条件成立时才能删状态。第三，IBR 控制把网络电磁动态、PLL、内外环和接口数值条件耦合起来，使传统同步机时代的经验简化不再自动可靠。第四，文中平衡三母线示例显示 dq-EMT 贴合 waveform EMT，而 QSP 漏掉高频振荡并改变部分控制轨迹。[pdf:E14]（PDF 物理页 14，Figs. 8–9）第五，模型选择的正确问题是“对当前研究，什么构成有效解”，而不是“哪个仿真类别通常最好”。[pdf:E15]（PDF 物理页 15，Section VI）

**3 句话。** 模型简化同时改变 physics、equation structure 与 solver requirements。只有在条件被显式检查时，较大步长和较少状态才代表安全加速；否则它们可能意味着把目标现象删除。对 EMT+FPGA 研究者，本文提供的是建模边界与验证问题，不提供任何可直接复用的 FPGA mapping 或实时性能结论。

**1 句话。** 先定义必须保留的现象，再证明变换或降阶不会删掉它，最后才谈计算加速。

## § 9 — 最脆弱的假设

最脆弱的假设是：**被删或被移到基带的 dynamics 与研究目标之间存在足够稳定、可辨识的分离，且这种分离在扰动与控制非线性期间仍成立。** 这同时覆盖 dynamic phasor 的 narrow-band/平衡前提与 SPT 的 isolated stable root 前提。若 IBR current limiter、PLL、弱网接口或控制增益让快子系统在事件期间靠近不稳定、产生多根或把能量扩散到多个频带，QSP 或低阶 dynamic-phasor model 就可能把真实不稳定判成稳定；失败代价是研究结论的类别错误，而不是小幅误差。[pdf:E05][pdf:E07]（PDF 物理页 5，dynamic-phasor 带宽条件；物理页 7，SPT 根与 boundary-layer 条件）

论文提供的支持是一个平衡三母线 line-trip：dq-EMT 与 waveform 贴合，QSP 的缺失高频分量清楚可见。它同时明确承认，SPT 的适用性依赖 IBR control parameters 和系统其余部分的 time constants，建模需求必须先从 detailed model 确定；保护切换、变压器励磁等问题可能必须保留 waveform。[pdf:E14][pdf:E15]（PDF 物理页 14–15，Section V.D–VI）缺失的证据是对 unbalance、harmonic-rich disturbance、limiter/saturation、低短路比、参数扫描和多 IBR 交互的系统失效边界。因此，本文证明的是条件化可行性，不是通用安全降阶。

## § 10 — 最小复现实验

一周内最有价值的复现，不是重做全部 taxonomy，而是复现“dq-EMT 保留目标电磁动态、QSP 丢失高频信息”这一条核心 claim。

- **数据与模型：** 使用论文 PDF 指向的三母线公开示例结构，至少保留 π-line、一个 VSM grid-forming inverter、一个 droop-controlled inverter 和母线 1–2 line trip；若仓库中的参数无法取得，则建立同拓扑的标幺小系统并公开全部参数。waveform EMT 作为 reference，另实现 dq-EMT 与 algebraic-network QSP。[pdf:E13]（PDF 物理页 13，Fig. 7 与 Section V.D）
- **测量：** 对母线电压、PLL \(v_d/v_q\)、VSM frequency estimate 计算事件后时窗的 normalized RMS trajectory error、峰值误差、主振荡频率与 damping；另外记录 accepted/rejected steps 和 wall-clock time。Evaluation count 单独报告，不能替代实际运行时间。
- **预注册判据：** 在同一求解容差和同一硬件上，若 dq-EMT 相对 waveform 的电压与关键控制状态 NRMSE 小于 0.5%，主振荡频率误差小于 2%，同时 QSP 显著低估事件后高频频带能量，则支持该条件化 claim；任一关键状态超过阈值，或 dq-EMT 与 waveform 给出不同稳定/不稳定判断，则反驳。这里的 0.5% 与 2% 是复现实验预注册阈值，不是论文报告数字。
- **最小扩展：** 只增加一次 control-gain sweep，检查 dq-EMT/QSP 的误差是否随 time-scale separation 变差。这样能把单一轨迹复现升级为对论文核心条件的第一次可证伪检查，而无需复现商业软件全套模型。

论文已给出的 sanity check 是 dq-EMT 与 waveform 轨迹接近、QSP 不含高频振荡，以及 2185/105 的 stiffness ratio 与三种 evaluation count；复现应先对齐这些方向性结果，再测试预注册阈值。[pdf:E14]（PDF 物理页 14，Fig. 9 与报告数字）

## § 11 — 最强反例设计

最强反例不是简单加入不平衡故障，因为那只会违反论文已声明的适用条件；更有力的攻击是寻找一个**外部三相量仍近似平衡且主要谱能量仍在基频附近，但内部 IBR 非线性破坏快状态稳定根**的工况。可构造低短路比三母线系统，在 VSM 与 PLL 参数 sweep 中加入硬 current limit、anti-windup 和 voltage saturation，再施加同一 line trip。对每个点同时运行 switching/waveform EMT、dq-EMT 和 QSP，并直接计算快子系统 Jacobian 的最小实部、代数根分支及接口矩阵条件数。

如果外部波形看起来满足“平衡、窄带”，但 limiter 激活后快子系统根合并或越过虚轴，而 dq-EMT/QSP 的常见适用性检查未触发警报，并且 reduced model 把 waveform EMT 的失稳判成稳定，那么就出现了对论文方法边界的实质攻击：仅凭信号带宽与名义 time constants 不足以判定模型有效，必须监测 nonlinear operating-point-dependent separation。Fig. 6 已说明 Norton/current-source interface 在弱网中会令 admittance matrix 接近奇异、逐步迭代难以收敛；结论部分又承认控制参数与扰动会限制简化的可推广性。[pdf:E13][pdf:E15]（PDF 物理页 13，Fig. 6 与 interfacing；物理页 15，Section VI）

若反例只发生在显式三相不平衡、强谐波或器件 switching 占主导的工况，它不会推翻论文的条件化结论；它只会再次确认适用边界。真正的证伪点是：论文给出的条件看似满足，但 reduced model 仍发生稳定性类别错误。

## § 12 — Follow-up Research Idea

在电力系统仿真领域，高影响工作通常不仅要求新算法，还要求可验证的物理忠实度、对关键稳定性结论的保真、大系统或 real-time/HIL 可实现性，以及对现有工具链的可迁移价值。基于第 9 节的脆弱假设，一个非增量的候选方向是：**把“离线选择一种 simulation category”改写为“带运行时有效性证书的自适应多保真仿真”**。系统默认运行低成本 dq-EMT/QSP，同时在线监测 spectral leakage、SPT boundary-layer stability margin、接口矩阵 conditioning 和 residual；当证书失效时，只在受影响的设备—网络区域恢复被删电磁状态或切换到 waveform，恢复后再安全降阶。

（a）驱动需求是：未来多 IBR 系统的有效 time-scale separation 随控制模式、limiter 和扰动改变，静态选模无法同时保证速度与稳定性结论。论文明确指出高频信息在某些研究中无关、在另一些研究中却决定答案，而且当前 novel simulation technique 缺少成熟软件承载。[pdf:E15]（PDF 物理页 15，Section VI）

（b）研究价值不在“再快一点”，而在给出可审计的错误边界：系统能说明何时降阶仍保持目标 trajectory/stability classification，何时必须恢复细节。这直接服务 system-wide EMT、IBR control interaction 和 real-time HIL。

（c）可借鉴相邻领域的 hybrid systems、a posteriori error estimation、adaptive model-order reduction 与 contract-based runtime monitoring。对于 FPGA+CPU heterogeneous execution，可以预编译 reduced/full 两套固定数据流，让 FPGA 承担规则、可流水化的 network/device update，CPU 负责 certificate、event 与区域切换；但本文没有 FPGA 证据，这只是架构候选。

（d）第一个证伪实验就是第 11 节的 limiter/weak-grid sweep：若证书在 waveform 与 reduced model 分叉前不能可靠预警，或频繁切换使端到端运行时间不优于统一 waveform EMT，就否定该方向的核心价值。

（e）与本文的实质区别是：本文分类并解释静态模型类别和适用条件；候选工作把“模型有效性”变成仿真期间可计算、可触发状态恢复的控制变量。相关工作未在本任务中联网检索，因此这只是基于本文证据约束的候选研究想法，不声称 novelty。
