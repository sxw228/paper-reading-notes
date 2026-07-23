# Overview of Interface Algorithms, Interface Signals, Communication and Delay in Real-Time Co-Simulation of Distributed Power Systems

- corpus order：26
- Zotero key：V3X4JZ7M
- 作者：Elutunji Buraimoh, Gokhan Ozkan, Laxman Timilsina, Phani Kumar Chamarthi, Behnaz Papari, Christopher S. Edrington
- 出处：IEEE Access, 2023
- DOI：10.1109/ACCESS.2023.3317250
- 源 PDF：`_source.pdf`
- PDF SHA-256：`221fd9267813fd06bc1af2e42f1c3bf2e166f318fddc83dfbf6d37c6e086f769`
- 文献类型：综述。本文主要组织、比较既有方法与案例，并没有提出一个经过统一 benchmark 验证的新 interface algorithm。

证据图均为源 PDF 的完整物理页，便于同时核对正文、图题、表头和相邻上下文：

[E01：摘要与综述范围](_evidence/E01-p001-abstract-scope.png) ·
[E02：GDRTCS 的约束与固定步长](_evidence/E02-p003-gdrtcs-challenges-fixed-step.png) ·
[E03：ITM 与稳定性机制](_evidence/E03-p005-itm-loop-stability.png) ·
[E04：AITM、TFA、TLM](_evidence/E04-p006-aitm-tfa-tlm.png) ·
[E05：IA 总结与接口信号变换](_evidence/E05-p008-ia-summary-signal-transform.png) ·
[E06：dynamic phasor 数学表示](_evidence/E06-p010-dynamic-phasor-equations.png) ·
[E07：RMS、DP 与 SRF 比较](_evidence/E07-p011-rms-dp-srf-comparison.png) ·
[E08：wave variable 与端到端流程](_evidence/E08-p013-wave-variable-end-to-end-pipeline.png) ·
[E09：耦合方式与通信网络](_evidence/E09-p015-coupling-network.png) ·
[E10：TCP 与 UDP](_evidence/E10-p017-tcp-udp-mechanisms.png) ·
[E11：同步、传输率与框架](_evidence/E11-p018-sync-rate-frameworks.png) ·
[E12：VILLAS 与 HELICS](_evidence/E12-p019-villas-helics.png) ·
[E13：通信延时的定义与组成](_evidence/E13-p021-latency-definition-components.png) ·
[E14：延时误差与接口能量](_evidence/E14-p022-delay-error-energy.png) ·
[E15：DP 相位补偿](_evidence/E15-p024-dp-phase-delay-compensation.png) ·
[E16：SRF、model-based 与 model-free 补偿](_evidence/E16-p025-srf-model-delay-frameworks.png) ·
[E17：结论与未来工作](_evidence/E17-p026-conclusion-future-work.png) ·
[E18：已承认的边界与研究需求](_evidence/E18-p027-limitations-research-needs.png)。

## § 1 — 研究问题与重要性

这篇综述要回答的不是“怎样把两个仿真器用网线连起来”，而是一个闭环数值系统问题：当一个电力系统模型被拆到不同地点的实时仿真器上时，两个子系统每一步应交换什么量、怎样用这些量重建远端行为、网络协议如何输送它们、迟到或丢失的数据怎样处理，才能避免接口凭空注入能量、波形失真甚至数值失稳。作者把 interface algorithm（IA，规定子系统如何互相施加电压、电流或等效量的连接规则）、signal decomposition/reconstruction、通信协议和 delay compensation 放在同一条因果链中审视。[pdf:E01] [pdf:E05] [pdf:E14]

重要性来自实时仿真的硬约束。每个 simulator 必须在固定时间步结束前完成该步计算，而 WAN 延时可能比 EMT 的微秒至毫秒级时间步长大很多；因此远端返回的量天然属于“过去”，并非当前求解时刻的同步边界条件。若把旧量直接闭环反馈，误差会逐步传播；对于电力接口，错位的电压与电流还对应非物理的 residual energy。结果是一个物理上稳定的系统也可能在 co-simulation 中失稳，或只剩下看似平滑、实则丢失快速暂态的结果。[pdf:E02] [pdf:E13] [pdf:E14]

GDRTCS（Geographically Dispersed Real-Time Co-Simulation）的工程价值是把不同实验室已有的 RTDS、OPAL-RT、控制器、PHIL/CHIL 装置和专有模型组合成一个实验，而不必把设备集中到同一地点，也可保留各方模型与知识产权边界。它能扩大可模拟系统规模、共享稀缺硬件并支持跨机构验证；但这些价值只有在接口的稳定性、时间一致性和信息保真度可说明时才成立。[pdf:E01] [pdf:E02]

## § 2 — 前人工作与不足

论文归纳的第一类既有工作来自 PHIL。ITM 用受控电压源和受控电流源把一侧的端口行为施加到另一侧，结构简单、计算量低、精度通常较好，但 aggregate delay 会增加相位滞后，其稳定范围受两侧等效阻抗比约束。AITM 加入补偿阻抗扩大稳定区，却会改变被测系统；FCF 以低通或带通滤波抑制高频反馈，又可能牺牲信号准确度。PCD 复制耦合阻抗，DIM 则在 ITM 与 PCD 之间引入可调 damping impedance；它们以额外阻尼换稳定性，但准确的阻抗匹配本身可能需要已知远端模型。[pdf:E03] [pdf:E04] [pdf:E05]

第二类工作改变“传什么”。直接发送瞬时三相波形容易被 time-varying delay、packet loss 和 packet reordering 破坏，因此已有方法发送 RMS/频率/相角、dynamic phasor（DP）、synchronous reference frame（SRF）的 dq0 量，或 wave variables，再在接收端重建时域源。RMS 表示通信负担较小，但快速暂态保真度差；DP 能保留选定谐波并通过相位推进补偿延时，但系数越多计算与带宽成本越高；SRF 让稳态正序量近似为 DC，响应更直接，但准确补偿依赖频率和时钟；wave variable 用 passivity 思路提高大延时闭环的稳定性，却不保证高延时时仍有足够的暂态 fidelity。[pdf:E05] [pdf:E06] [pdf:E07] [pdf:E08]

第三类工作处理通信和调度。TCP 提供有序、可靠、错误恢复的字节流，但握手、确认和重传会增加 latency 与 jitter；UDP 不保证顺序、送达或去重，却允许按固定速率持续发送并丢弃过时包，更符合“最新状态比补回旧状态更重要”的实时语义。RTP/RTCP 可在 UDP 之上提供时间戳、流同步和 QoS 统计。PTP、NTP、IRIG-B 等解决的是各端“钟是否一致”，并不自动消除数据从发送到接收的网络延时。[pdf:E10] [pdf:E11]

第四类工作提供连接框架。VILLASnode 采用去中心化 gateway/adapter，把不同 simulator 与协议接起来，并可收集 link statistics、转换协议和暴露监控；HELICS 则以 federate、core 和 broker 组织数据交换与同步，更适合多域、多 simulator 的协调。论文的关键批评是：框架能搬运和调度数据，但不能替代电气接口设计；同样，稳定的 IA 也不能弥补错误的 coupling point、不可接受的信号压缩或未测量的网络延时。[pdf:E11] [pdf:E12] [pdf:E18]

## § 3 — 重建作者的思考路径

以下是基于论文材料重建的推断，不是作者逐字陈述。

第一步，从资源限制出发：单台实时仿真器受计算能力、专用 I/O 和设备所在地限制，而电力系统又需要固定步长、硬实时执行。把模型拆开并行是自然选择，但一旦拆开，原来同一求解器内部同时成立的代数连接就变成跨网络的数据交换。[pdf:E02]

第二步，把网络延时解释成数值边界条件错误，而不只是“画面卡顿”。子系统 2 在时刻 \(t_n\) 收到的是子系统 1 在更早时刻的输出；两侧闭环后，这个时间错位会累积，并使接口两边的电压和电流不再对应同一物理时刻。于是研究问题从“提高带宽”转为“让耦合在延时下仍满足稳定性与能量一致性”。[pdf:E13] [pdf:E14]

第三步，借用 PHIL 的 IA，因为 PHIL 也要在两个动态系统之间交换功率变量并承受接口延时；但 geographically dispersed 场景的延时更长、抖动和丢包更明显，所以不能照搬瞬时波形和本地放大器假设。必须把 IA 与信号表示联合设计。[pdf:E03] [pdf:E05]

第四步，把交流信号的“快速载波”和“慢变信息”分开。RMS/相角、DP、dq0 都是在不同程度上压缩波形：只发送远端真正需要的状态描述，再由远端自己的 simulation clock 重建波形。若数据携带发送时间戳，就可将已测 delay 转成相位推进或预测时域状态。[pdf:E06] [pdf:E07] [pdf:E15]

第五步，承认稳定性、fidelity、通信负担和模型依赖之间没有免费午餐。UDP 减少等待但允许丢包；DP/SRF 能补偿相位但依赖频率、时间戳和信号带宽；wave variable 可保 passivity 但可能钝化暂态；model-based predictor 精度高时有效，但模型错误会直接变成预测错误。因此正确问题应是“针对 coupling point、动态频带和网络统计，选择怎样的组合”，而非寻找对所有系统都最优的一种 IA。[pdf:E08] [pdf:E10] [pdf:E15] [pdf:E16]

## § 4 — 核心 Intuition

把 geographically distributed co-simulation 看成一个通过有延时网络闭合的功率端口，而不是两个独立仿真器交换日志。接口先把高频、难以逐点传送的电压电流压缩为慢变且可时间标记的等效量，网络持续传送最新状态，接收端再用本地时钟、测得的 delay 和物理一致的受控源重建当前边界条件。稳定性取决于端口能量与闭环阻抗，fidelity 取决于信号表示是否覆盖目标动态；两者必须与通信协议和补偿器一起设计。[pdf:E05] [pdf:E08] [pdf:E14] [pdf:E15]

## § 5 — 具体方法与完整 Pipeline

本文给出的不是唯一算法，而是一套组合式设计空间。用“两个实验室共同仿真 transmission-distribution 系统”的真实情境，可以把完整 pipeline 写成以下九步：

1. **定义研究动态。** 先确定要看的是稳态/慢速控制，还是 fault、converter switching 等快速 EMT 暂态。这个选择决定后续允许丢掉多少谐波与瞬时信息。[pdf:E07]
2. **选择 partition 与 coupling point。** 优先在单条 transmission line、transformer 或 HVDC link 等少量 series components 处切分；高度网状节点会产生多个强耦合端口，使数值闭环和通信都更复杂。[pdf:E14]
3. **决定耦合类型。** 只交换 setpoint/feedback 时是 control-signal coupling；要保持电力端口行为时是 electrical-signal coupling。后者又可按 AC 是否同频同相分为 asynchronous/synchronous coupling，或在 DC link 上耦合。[pdf:E09]
4. **选择 IA。** 例如 ITM：实验室 A 把接口电压变成实验室 B 的 controlled voltage source，B 把接口电流反馈为 A 的 controlled current source。若阻抗比和 delay 使 ITM 不稳，可考虑 AITM、DIM/MDIM、FCF、TLM 或 wave-variable 形式，但每种稳定化都可能引入模型依赖、额外阻抗或带宽损失。[pdf:E03] [pdf:E04] [pdf:E05]
5. **分解发送信号。** 慢动态可发送 \([V_{\mathrm{RMS}}, f, \theta]\)；需保留非平稳与谐波信息时发送若干 DP coefficients；平衡三相基波可发送 dq0；希望以 passivity 约束延时闭环时可发送 wave variables。不能把这些表示当成等价压缩，它们保留的频带不同。[pdf:E05] [pdf:E06] [pdf:E07] [pdf:E08]
6. **封包与定时。** 每个 packet 至少要携带 sequence/timestamp 和接口量。对硬实时交换，UDP 可按 predetermined rate 发送，无须等对端确认；接收端只采用最新时间戳，丢弃晚到的旧包。若应用更看重完整、有序送达，可用 TCP，但必须把重传引起的 delay/jitter 计入闭环设计。[pdf:E10] [pdf:E11]
7. **网关与时钟。** VILLASnode 之类的 gateway 可在 simulator 专用 I/O、UDP/RTP 等协议间转换、记录 packet loss/jitter 并调整 data rate；PTP/GPS/IRIG-B/NTP 让两端 timestamp 可比较。时钟同步只提供“延时测量尺”，不会自动补偿 delay。[pdf:E11] [pdf:E12]
8. **接收、补偿与重建。** 接收端用“当前同步时刻减发送 timestamp”估计 one-way delay。DP 方法把 delay 变成每个谐波的 phase advance；SRF 方法按 \(\phi=2\pi f_h\tau\) 推进相位，再 inverse Park 重建三相波形。丢包时可沿用上一组慢变 coefficients 并增加 phase advance，但这隐含“系数在丢包窗口内变化不快”的假设。[pdf:E15] [pdf:E16]
9. **闭环验收。** 将重建波形施加到 controlled source，检查 deadline miss、packet statistics、接口 residual energy、monolithic-reference waveform error、稳态与 fault transient 分段误差，并分别报告 stability 与 fidelity。系统不发散不代表快速暂态正确。[pdf:E08] [pdf:E14]

## § 6 — 核心数学推导

本文是综述，没有从统一模型推出一个新定理；其数学内容是解释不同接口为何受 delay、阻抗和信号表示影响。最有用的统一视角是“延时是频率相关的相位误差”。对于角频率 \(\omega\) 的分量，纯延时 \(\tau\) 等价于乘以 \(e^{-j\omega\tau}\)。频率越高，同一物理延时造成的相位误差越大；这解释了为什么 WAN delay 对快速 EMT 暂态特别危险，也解释了仅补基波相位无法恢复宽带 fault transient。[pdf:E13] [pdf:E15]

**ITM 的闭环。** 论文用两侧等效阻抗 \(Z_1(s)\)、\(Z_2(s)\) 与总接口延时构造 open-loop transfer function。直觉上，阻抗比决定反馈增益，delay 决定额外相位；Nyquist 轨迹若因两者组合绕过临界点，物理系统即使稳定，离散 co-simulation 也会失稳。AITM 在分母侧加入补偿阻抗，DIM 则调节 damping impedance，使 loop gain 更容易落入稳定区；代价是接口不再透明。[pdf:E03] [pdf:E04]

**Dynamic phasor。** 对周期 \(T\) 的波形 \(x(\tau)\)，论文以滑动时间窗 Fourier coefficient \(X_k(t)\) 表示它，并用有限的 \(k\in K\) 重建波形。物理意义是：不逐点发送高采样率波形，而发送幅值和相位缓慢变化的若干频率分量。保留的 \(K\) 越小，通信与计算越省，但任何不在该集合内的快速分量都无法由接收端恢复。[pdf:E06]

**DP delay compensation。** 发送端在离散时刻 \(n\) 给出 \(X_k(n)\)，接收端测到 delay \(d_n\) 后，在重建项中增加与 \(k d_n\) 成比例的 phase advance。这样可把“旧 coefficient”外推到当前 carrier phase；packet loss 时延用上一 coefficient 并继续推进相位。该方法对 carrier 相位是确定性的，却没有预测 coefficient 自身在故障期间的突变，所以不能由公式推出任意暂态都能无损恢复。[pdf:E15]

**SRF compensation。** 三相量经 Park transformation 变为 \(d\)、\(q\)、\(0\) 分量；平衡基波在同步旋转坐标中近似常数。若 one-way delay 为 \(\tau_d\)，对第 \(h\) 个待补偿 harmonic 使用 \(\phi_h=2\pi f_h\tau_d\)，在 inverse Park 时提前这一相位。论文指出，若固定用 nominal frequency 而实际瞬时频率在 transient 中变化，就会产生 steady-state/transition error，因此精确方案应 frequency-adaptive。[pdf:E07] [pdf:E16]

**接口能量。** 若发送电压 \(v(t-\tau_v)\) 与返回电流 \(i(t-\tau_i)\) 属于不同物理时刻，则接收端计算的瞬时功率不再等于原系统端口功率；时间累计后表现为 residual energy。passivity/wave-variable 方法的吸引力在于限制通信通道生成净能量，从稳定性上更保守，但 passivity 不等价于 waveform transparency，因此仍需单独测 fidelity。[pdf:E08] [pdf:E14]

## § 7 — 实验设计与结论

这篇文章没有运行统一的作者自建 benchmark，也没有给出可横向比较全部 IA、协议和补偿器的数据集。它通过梳理既有论文的案例、公式、架构与表格来支持结论，因此下面的“实验”是被综述工作的证据，不应误写成本文自己的实验结果。[pdf:E01] [pdf:E17]

- **问题：RMS 与 DP 哪个更适合 transient？→ 设计：** 既有 transmission-distribution co-simulation 在正常工况和 transient 下比较两类接口表示。**答案：** 两者在正常测试中可有较高 fidelity，但 transient 时 fidelity 明显恶化；phasor-based/DP 表示通常比 RMS 更准确、稳定，且可用 phase shift 补偿 delay，但仍不能据此声称快速暂态完全保真。[pdf:E07]
- **问题：直接 time-domain waveform 经 WAN 后会怎样？→ 设计：** 对比发送与接收的正弦波，并在 RTDS 与 OPAL-RT 之间观察时间偏移。**答案：** 网络 latency 造成明显 time shift；旧输入进入下一步后，误差会继续传播，且 delay 相对微秒到毫秒级 time step 不可忽略。[pdf:E13] [pdf:E14]
- **问题：DP 相位补偿能否去掉延时造成的载波偏移？→ 设计：** 对 reference signal 施加 constant 与 time-varying delay，比较有无 DP-based IA 的接收波形。**答案：** 基于 timestamp 的 phase compensation 显著减轻时间偏移和 delay variation 引入的伪动态；但该结果主要支持周期/慢变 coefficient 的重建，不等同于 fault transient 的宽带恢复。[pdf:E15]
- **问题：TCP 可靠性是否更适合 real-time？→ 设计：** 文献比较 TCP 的握手/确认/重传和 UDP 的无连接、固定速率发送，并报告 distributed HIL 中对晚到包按 timestamp 丢弃。**答案：** 对 hard real-time loop，UDP 的“允许丢、不要等”通常比 TCP 的“补齐旧包”更符合控制语义；可靠性责任转移到 application-level freshness、sequence handling 和 predictor。[pdf:E10]
- **问题：framework 是否决定数值正确性？→ 设计：** 对照 VILLAS 的 decentralized gateway 架构与 HELICS 的 broker/federate 同步架构及其应用。**答案：** framework 决定接入、协议适配、调度与可观测性，但接口稳定性、能量一致性和信号表示仍需应用层设计，不能由框架自动保证。[pdf:E11] [pdf:E12]

因此，论文真正支持的是一条工程结论：GDRTCS 的成功条件是 partition、IA、signal representation、transport/synchronization 和 delay compensation 的共同匹配。它没有支持“某一种 IA/协议在所有网络和工况下最好”，也没有建立跨文献统一量化排名。[pdf:E17] [pdf:E18]

## § 8 — Take-aways

**5 句话。**  
第一，geographically distributed real-time co-simulation 是一个跨网络闭合的数值功率系统，不是普通数据共享。[pdf:E13] [pdf:E14]  
第二，IA 决定端口如何互相施加电压、电流或等效量，其稳定性受阻抗比、delay 和额外滤波/阻尼共同影响。[pdf:E03] [pdf:E04]  
第三，RMS、DP、dq0 与 wave variable 保留不同信息，选错表示会在网络仍然畅通时就丢掉目标 transient。[pdf:E05] [pdf:E07] [pdf:E08]  
第四，UDP、timestamp、同步时钟和 gateway 共同提供“持续发送最新状态、测量数据年龄”的通信基础，但补偿仍要由接口重建或 predictor 完成。[pdf:E10] [pdf:E11]  
第五，稳定、低延时和高 fidelity 是不同验收维度，必须分别测量。[pdf:E14] [pdf:E18]

**3 句话。**  
先按研究动态选择切分点和信号表示，再按端口阻抗与网络 delay 选择 IA 和补偿器。[pdf:E05] [pdf:E14]  
把 timestamp 测得的数据年龄变成相位推进或状态预测，只能补偿模型覆盖的动态，不能重建被压缩掉或突变的频带。[pdf:E15] [pdf:E16]  
任何只报告“仿真没有发散”或“网络连通”的 GDRTCS，都还没有证明 transient fidelity。[pdf:E17] [pdf:E18]

**1 句话。**  
实时协同仿真的核心，是让“远端过去的有限信息”在本地被重建成既不注入非物理能量、又保留目标动态的当前边界条件。[pdf:E14] [pdf:E15]

## § 9 — 最脆弱的假设

最脆弱的假设是：**在一个通信更新窗口内，接口动态可以由所选的低维表示与补偿模型充分预测。** RMS 假定主要信息可由基波幅值、频率和相角表达；DP 假定有限 Fourier coefficients 在 delay/丢包期间变化足够慢；SRF 假定选定 harmonic 与瞬时频率可可靠估计；predictor 则假定 plant model 或数据规律在当前事件中仍有效。[pdf:E05] [pdf:E06] [pdf:E15] [pdf:E16]

它在 converter switching、fault inception、protection action、饱和或 topology change 时最可能失效，因为这些事件恰好让高频内容和 coefficients 在一个 WAN round trip 内突变。相位推进可以把旧的正弦量“转到现在”，却不能知道故障刚刚改变了幅值、序分量或网络拓扑。论文承认既有应用多集中在 small-scale circuits 和 slower dynamics，也明确提出需要提高 fault robustness、rapid dynamics reproduction 和大系统 scalability；这意味着核心假设尚未由大规模、宽带暂态证据充分闭合。[pdf:E15] [pdf:E17] [pdf:E18]

失败代价不是误差略增，而是接口两边功率变量不同步，residual energy 被注入闭环，导致虚假振荡、保护误动或数值失稳。现有证据显示 DP/SRF phase compensation 能改善延时波形、wave variables 能提高稳定性，但论文没有提供一个跨 IA、跨网络 profile、跨 fault type 的统一实验来界定“多快的动态仍可被可靠预测”。[pdf:E08] [pdf:E14] [pdf:E15]

## § 10 — 最小复现实验

一周内最值得复现的不是整套跨洲实验，而是“同一 bandwidth-limited 表示在稳态和突变下的边界”。

**数据与模型。** 在两台可固定步长运行的 simulator/process 上搭一个三相 Thevenin source 经线路供给 RL load 的小系统，并加入一次 line-to-ground fault。保留一个 monolithic EMT run 作为 reference。若没有两台实时机，可在同一主机的两个实时进程之间用 UDP 和可控 network emulator 建立真实 packet path；这验证接口逻辑，不冒充板级实时平台证据。

**实现。** 在相同 ITM 端口上实现两种 signal path：A 为直接使用上一包的 RMS/frequency/phase，B 为发送 0、±1 及至少一个更高次 DP coefficient，并用 timestamp 计算 delay 后按相位推进重建。固定发送周期，注入三组网络条件：恒定 20 ms delay、均值 20 ms 且带 jitter、再叠加 1% packet loss。接收端仅使用最新 sequence，记录 deadline miss 和 packet age。DP 重建机制与 packet-loss 时延用旧 coefficient 的规则可直接按论文描述实现。[pdf:E10] [pdf:E15]

**测量。** 分别计算 pre-fault steady-state、fault inception 前后两个周波、post-fault recovery 的 voltage/current normalized RMSE、相位误差、峰值误差；积分两侧瞬时功率差得到 residual energy；另记是否发散和每步执行时间。所有计算必须使用同一 timestamp 对齐，不能用事后任意 time shift 美化结果。

**支持 claim 的结果。** 若 B 在 steady-state 与 jitter 下显著优于 A，且执行时间仍小于 time step，则支持“DP phase compensation 能处理延时载波偏移”。若两者在 fault inception 都出现明显峰值误差，且误差随 packet age/未表示频带上升，则同时支持本文最重要的边界：phase compensation 不等于宽带 transient prediction。[pdf:E07] [pdf:E15]

**反驳条件。** 若在相同带宽、相同 delay profile 下，DP 对 steady-state 没有改善，或其计算使 real-time deadline miss 反而增加；又或者简单 RMS 在全部 fault 指标上不劣于 DP，则论文组织出的“更丰富 phasor 表示换取更高 fidelity”的工程判断需要重新限定。

## § 11 — 最强反例设计

最强反例是一个“网络看起来良好，但物理表示必然过时”的事件：两端时钟已 PTP/GPS 同步，UDP delay 低且稳定、无丢包；在两个 packet 之间，远端 converter 触发 current limit 并伴随 line-to-ground fault，使正负零序、幅值和 harmonic content 同时突变。发送端仍只发上一时刻的 RMS/DP/dq0 coefficients，接收端用精确的 \(\tau\) 做 phase advance。

若重建器只推进相位，它会非常准确地重建“旧运行状态在当前相角的位置”，却完全不知道 limiter 与 fault 已改变 coefficient 本身。受控源据此闭环后，电压和电流来自不同 topology/state，产生 residual energy；passivity filter 可能防止发散，却把突变钝化为一个不存在的慢响应。这个反例同时排除了“只是时钟没同步”“只是 TCP 重传”“只是网络太差”等替代解释，把失败归因到 signal representation/predictor 的信息边界。[pdf:E14] [pdf:E15] [pdf:E16]

实验上应扫描 event time 相对 packet boundary 的位置、fault impedance、converter current-limit slope 和 retained DP harmonics，比较 monolithic reference。最有杀伤力的结果是：网络指标保持优秀且闭环始终 stable，但 protection-relevant peak、fault inception angle 或 residual energy 明显错误。这会证明“稳定且通信正常”不能作为 high-fidelity GDRTCS 的充分条件，也直接挑战把 phase compensation 当成普适 delay solution 的做法。[pdf:E17] [pdf:E18]

## § 12 — Follow-up Research Idea

在电力系统实时仿真领域，高影响工作通常不仅要求新算法，还要求可解释的稳定性/误差边界、硬实时可实现性，以及在 fault、converter switching 和真实 HIL/多站网络下相对于 monolithic reference 的严格验证。本文自己也把大系统、快速动态、fault robustness、energy conservation 与 time-varying delay 列为未解决方向。[pdf:E17] [pdf:E18]

**候选研究想法：从“固定信号表示”改为“事件感知的可验证信息契约”。** 平时接口发送低带宽 DP/dq0 state；本地在线计算一个由未建模频带能量、coefficient innovation、packet age 和 port residual-energy bound 组成的可信度证书。一旦证书越界，系统不再盲目相位推进，而是切换到有限时长的 burst waveform/sequence-component packet，或进入双方约定的 passive safe interface；恢复后再退回低带宽模式。这里的改变不是给既有 IA 再加一个 predictor，而是把研究目标从“永远重建一个当前值”改成“实时证明当前重建是否足以支持目标物理结论，并在不足时显式改变信息量或实验状态”。

（a）**未满足需求。** 现有 phase compensation 可修正 carrier timing，却无法区分“只是包变旧”与“远端物理状态已突变”；用户需要的不只是输出波形，还需要知道该波形此刻是否仍可用于 protection/transient 结论。[pdf:E15] [pdf:E18]

（b）**潜在研究价值。** 它把 fidelity、stability、bandwidth 与 deadline 放进一个可在线验收的契约，可为跨实验室实验提供可审计的 validity window，并把“系统未发散”提升为“目标动态误差有界”。

（c）**可借鉴的相邻领域。** 可借鉴 networked control 的 event-triggered communication、set-membership/state-estimation 的 uncertainty bound，以及 passivity observer/controller 对 residual energy 的在线监测；但这些只作为方法来源，不能在未检索全文的情况下声称组合具有 novelty。

（d）**第一个可证伪实验。** 使用第 11 节的 packet-between fault/current-limit 场景。如果可信度证书在误差超限前不能触发，或触发后的 burst/safe mode 仍不能在硬实时 deadline 内把 protection-relevant peak error 压回预设界限，这个想法即被证伪。

（e）**与本文综述方法的实质区别。** 现有方法预先选择 RMS、DP、SRF、wave variable 或 predictor，然后在整个实验中沿用；候选方法让接口根据“当前信息是否足够”改变发送语义，并把可用性声明本身变成输出。由于本任务严格以单篇 PDF 为边界、未额外检索相关工作，这只是可证伪的候选方向，不作 novelty 声明。
