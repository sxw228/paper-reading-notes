# On the Use of Real-Time Simulation Technology in Smart Grid Research and Development

- 作者：Christian Dufour；Jean Bélanger
- 出处：IEEE Transactions on Industry Applications，Vol. 50，No. 6，pp. 3963–3970
- 年份：2014
- DOI：10.1109/TIA.2014.2315507
- Zotero key：7AIG3J5M

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要回答的不是“哪一种 smart grid 算法最好”，而是一个更靠近工程落地的问题：当电网同时包含可再生能源、储能、电动汽车、通信网络、保护装置、分布式控制器和用户侧设备时，怎样在真正接入电网之前验证这些部件的协同行为。作者把 smart grid 的困难归因于系统复杂度和相互作用：信息采集与通信已经成为控制链的一部分，新的电源和负荷又具有更强的不确定性，因此只在离线软件里验证某个局部算法不够。[pdf:E01]（PDF 物理页 1，Abstract、Introduction 与 Fig. 1）

Real-time（RT）simulation 的物理意义，是让仿真时间与墙上时钟同步推进，使真实控制器、继电器、通信设备或功率装置能够像面对真实电网一样与模型闭环交互。这样做的价值不是让模型天然更准确，而是把“模型、计算时限、接口和硬件”放进同一个可重复、可施加故障且不危及真实电网的实验环境。论文因此把 RT simulator 定位为 smart grid 研发的实验基础设施，并列出分布式控制、IEC-61850/DNP3、PMU 状态估计、WAMPAC、有源滤波、可再生能源并网、PHIL 和相量仿真等应用范围。[pdf:E02]（PDF 物理页 1，Introduction 右栏的研究目标与八类应用）

重要性在于：smart grid 的失败往往不是单个控制律算错，而是跨层闭环在时延、模型误差、设备限制或异常工况下出现意外耦合。RT simulation 提供了在实验室里暴露这类耦合的机会。不过，本文主要是一篇应用综述和案例汇编，而不是一项统一方法的受控性能研究；后文所有“有效”判断都应保留这一证据边界。

## § 2 — 前人工作与不足

论文涉及的 prior work 已经覆盖了若干局部问题。IEC-61850 的 GOOSE 和 Sampled Values 能分别承载跳闸等数字量和电流、电压等模拟采样值，RT-LAB 也能通过 IEC-61850、DNP3 与保护或控制设备交互；不足是当时协议可靠性仍在通过 pilot project 与传统铜缆架构比较，互操作性并不等于现场可靠性已经闭合。[pdf:E03]（PDF 物理页 2，Section II 与 Fig. 2）

在配电网控制方面，集中式电压调节可以统一优化各分布式电源的设定值，但它依赖完整网络配置、大量采集与通信组件，而且接入或切除电源后要重新求解全局优化问题；随着分布式电源数量和网络事件增加，这条路线会触及规模与鲁棒性边界。作者综述的替代路线是 multi-agent system：每个电源主要依据本地信息求自己的优化问题，再用简单协调机制接入整体控制。[pdf:E05]（PDF 物理页 3，Section IV 前半）

在 EMT real-time simulation 方面，经典 Bergeron line 等基于传播时延的解耦方式适合长输电线，却不容易用于本质上较集中、线路较短的配电网。论文举出的 210-bus 配电网平均主线长度约 7.5 km，不足以提供自然传播时延；人为加入 compensated delay 可以满足潮流控制研究，却会破坏故障暂态精度，因此需要 SSN 这类无算法延时的分区求解器。[pdf:E06]（PDF 物理页 3，Section V 的配电网规模、delay 方法结果与适用边界）

PHIL 已经能把真实功率设备放进闭环，但 simulator、power amplifier 与被测硬件共同构成的闭环可能失稳；这说明“硬件接上了”不是验收终点，接口算法、带宽和未建模动态同样是被测系统的一部分。[pdf:E11]（PDF 物理页 6，Section VIII 与 Fig. 10）论文第 8 页的参考文献把 IEC-61850 HIL、配电网多核解耦、SSN、Hydro-Québec 大系统和并行 solver 等工作列为案例基础，而本文的贡献是把这些分散实例组织成一幅 RT technology 的应用版图，不是提出一个取代它们的新算法。[pdf:E15]（PDF 物理页 8，References [1]–[30]）

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为五步。

1. 风、光、储能和可控负荷使电网从少数同步电源主导的系统变成大量主动设备协同的系统；通信不再只是监视通道，而是控制闭环的一部分。[pdf:E04]（PDF 物理页 2，Sections II–III）
2. 只验证控制器代码不够，因为协议栈、继电器、PMU、功率放大器和真实设备会改变闭环行为。因此需要让实际硬件与数字电网模型按真实时间交换量测和控制量。
3. 一个 solver 不可能同时以相同代价覆盖所有时间尺度。快速开关和故障暂态要求 EMT 的微秒级时间步，而广域监控只关心较慢的机电动态，可以使用毫秒级相量模型。[pdf:E13]（PDF 物理页 7，Section XI 的 EMT 容量瓶颈与 ePHASORsim 定位）
4. EMT 模型要在 deadline 内完成，需要利用网络结构做分区、稀疏求解和多核并行；但人为延时虽然便于解耦，也可能改变暂态物理。[pdf:E07]（PDF 物理页 4，Figs. 5–6 的 SSN group/SuperGroup 结构）[pdf:E08]（PDF 物理页 4，Section V-B 的 SSN 求解与并行说明）
5. 因而合理路线不是追求一个“最高保真”的万能模型，而是按研究问题选择 EMT、phasor、HIL 或 PHIL，再用真实接口和异常场景检查端到端闭环。

这条路径是基于论文案例组织方式的重建，不是作者明示的一套设计理论。

## § 4 — 核心 Intuition

本文的核心 intuition 是：smart grid 的风险来自跨设备、跨通信和跨时间尺度的相互作用，所以验证环境必须让关键闭环在真实时间里真正闭合。与此同时，模型保真度要匹配被测问题：故障和电力电子暂态用 EMT，无需快速电磁现象的广域控制用 phasor，设备接口风险用 HIL/PHIL。RT simulation 的价值不在于“实时”二字本身，而在于它让算法、计算 deadline、通信和硬件共同接受实验。

## § 5 — 具体方法与完整 Pipeline

本文没有给出一个统一软件 pipeline，而是从多个实验室案例中隐含出一条可复用的工程流程：

1. **先定义待验证对象。** 保护与通信问题关注 IEC-61850 报文、跳闸逻辑和 relay；配电控制关注电压、功率与 THD；大电网控制关注 PMU、SCADA 和慢动态。被测 claim 决定需要保留的物理现象。
2. **选择时间尺度和模型。** 故障、开关和电力电子交互采用 EMT；不要求快速电磁现象的 WAMPAC/SCADA 可采用 phasor model。论文报告的 phasor 路线以 10 ms 时间步覆盖约 20 000 buses，而若干 EMT 案例使用 50–65 μs 量级时间步。[pdf:E13]（PDF 物理页 7，Section XI）[pdf:E06]（PDF 物理页 3，Section V）[pdf:E08]（PDF 物理页 4，Section V-B）
3. **让模型在 deadline 内可解。** 对集中式配电网络，SSN 把网络划成 virtual state-space partitions，在连接节点上用 nodal method 同时求解，并把各 partition 分配到不同 CPU core；OLTC 还可用 discrete external model 直接编码，避免每次变 tap 都重算全系统 state-space matrix。[pdf:E08]（PDF 物理页 4，Sections V-A/V-B）
4. **接入控制与通信。** Multi-agent 案例用 TCP/IP 连接三个独立 agent、JADE、SCADA 与 RT-LAB；状态估计案例则把 GPS 同步的量测经 IEC-61850 送往 OpenPDC。[pdf:E05]（PDF 物理页 3，Fig. 4 与实验平台）[pdf:E09]（PDF 物理页 5，Section VI 与 Fig. 7）
5. **按风险选择 HIL 或 PHIL。** HIL 把控制器、relay、PMU 等信号级硬件接入闭环；PHIL 再通过 power amplifier 交换真实功率，使真实 house、PV inverter 或风机 bench 直接面对仿真电网。[pdf:E11]（PDF 物理页 6，Section VIII）
6. **构造场景并采集端到端结果。** 例如 AIT 的 PV integration 案例改变 grid impedance 与 P/Q control 参数，观察 regular operation、持续振荡或 instability；整个软件电气系统运行于 RT-LAB，整体带宽设为 1 kHz。[pdf:E12]（PDF 物理页 6，Section IX 与 Fig. 12）
7. **用离线高精度模型或已知标准做参照。** 检查 deadline miss、波形误差、保护动作、稳定性、THD、状态估计质量和通信行为，而不能只看模型是否“跑起来”。

一个具体例子是 PV inverter 并网研究：输入是不同 grid impedance、多个 inverter 及其 reactive-power control 参数；RT simulator 计算配电网和未作为真实硬件存在的部件，power interface 把真实 inverter 接入闭环；输出是电压幅值、PQ 行为以及正常、持续振荡和不稳定状态的边界。[pdf:E12]（PDF 物理页 6，Section IX）[pdf:E14]（PDF 物理页 7，Section IX 后半）

从 EMT + FPGA 角度必须明确一个缺口：本文没有报告 HDL 架构、fixed-point word length、FPGA resource utilization、place-and-route timing 或 FPGA-in-the-loop 实验。参考文献提到 FPGA-based high-resolution solver，但正文案例的具体计算平台主要是 CPU、多核服务器和 SGI supercomputer；不能把本文当成 FPGA 实现证据。[pdf:E15]（PDF 物理页 8，Reference [24]）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有给出可复现的核心公式或完整数学推导，因此本节不虚构推导。它提供的是三类数值计算机制的工程描述。

第一，SSN 将网络形成若干 virtual state-space partition，在 partition connection point 上进行 nodal solution；组内方程可并行预计算，组间只通过较少节点耦合，从而降低全网矩阵求解规模，并避免为了并行而加入非物理延时。[pdf:E07]（PDF 物理页 4，Fig. 6）[pdf:E08]（PDF 物理页 4，Section V-B）

第二，OLTC 的常规开关模型约需每相 16 个 switches，tap 改变会触发 state-space system 重算；SSN external model 允许在离散域直接编码可变变比和漏感对应的 OLTC 方程，从而把结构变化限制在局部模型内。[pdf:E08]（PDF 物理页 4，Section V-A）其物理意义是减少一次拓扑事件引起的全局计算抖动，而不是改变 transformer 的电气行为。

第三，ePHASORsim 使用 explicit two-step Euler 离散 differential equation，并利用 sparse matrix factorization/solution 处理 network nodal equations。[pdf:E13]（PDF 物理页 7，Section XI）这牺牲快速电磁细节，换取大规模和较大时间步，适用边界是“无需模拟快速 electromagnetic phenomena”的控制与保护测试。[pdf:E14]（PDF 物理页 7，Section XI 后半）

因此，本文真正的“数学约束”是一个工程 deadline：每个仿真步必须在下一个真实时刻到来前完成。但作者没有给出 worst-case execution time、deadline jitter 或数值稳定性的统一证明，只给出若干案例性能。

## § 7 — 实验设计与结论

本文的证据是跨实验室案例，不是同一平台上的 controlled benchmark。按“问题 → 实验 → 答案”可归纳如下。

- **IEC-61850 是否能进入保护闭环？** → 在 KTH 用 RT HIL 让 ABB RED-670 differential protection 面对 RT 电网模型，并综述 SEL-487E relay 的 RT-LAB 测试 → 论文证明了协议与真实 relay 可被纳入实验闭环，但没有给出相对铜缆的系统可靠性统计。[pdf:E03]（PDF 物理页 2，Section II 与 Fig. 2）
- **更少的有源滤波器能否维持配电网谐波标准？** → 多个 APLC 依据 PCC 电压/电流与 THD，由中央 SCA 分配 reference current，并以 IEEE-519 的 THD 小于 5% 为目标 → 报告结论是，只要位置选择正确且协同工作，APLC 数量少于 power-electronic load 数量仍可满足该规范。[pdf:E04]（PDF 物理页 2，Section III）
- **分散电源能否不用全局集中优化而协调电压？** → RT-LAB 电网通过 TCP/IP 与三个独立 agent 交互，每个 agent 控制各自风机接入点的电压和功率 → 案例展示了 MAS、JADE、SCADA 与 RT simulator 的集成平台，但本综述没有报告控制误差、收敛时间或通信扰动下的统计结果。[pdf:E05]（PDF 物理页 3，Section IV 与 Fig. 4）
- **集中式配电网能否做多核 EMT real-time simulation？** → 对 210 buses、210 lines、121 loads 的网络采用 compensated delay，五个子网在 OLTC feeder 汇合 → 对潮流目标，50 μs 步长下 active/reactive power 相对无延时仿真的误差低于 0.002%；作者同时明确说该方法不适合 fault transient，故障研究要用 delay-free SSN。[pdf:E06]（PDF 物理页 3，Section V）
- **SSN 能否在不加算法延时的情况下扩大网络？** → 一个超过 700 nodes、含 980 L-C states 的 radial system 在四核 3.33-GHz Xeon 上并行运行 → 报告时间步低于 65 μs，无 algorithmic delay 或 stub line；网络被化简为六个 nodes 和六个 multiterminal branches。[pdf:E08]（PDF 物理页 4，Section V-B）
- **RT 量测链能否支持配电状态估计？** → eMEGAsim 运行含 unbalanced lines 和 dynamic loads 的 IEEE 13-bus feeder，按 GPS pulse-per-second 产生量测，经 IEC-61850 流入 OpenPDC，再用 Kalman-filter-based estimator 估计状态 → PQ 与 PMU 数据库每 20 ms 更新一次，说明完整的同步量测链可以在 RT 环境闭合；论文未报告估计误差分布。[pdf:E09]（PDF 物理页 5，Section VI）
- **WAMPAC 应用能否与真实 PMU/PDC 联调？** → 用 eMEGAsim、SEL PMU/PDC 验证 S3 DK，并实现 wide-area frequency monitoring 和 online electromechanical mode estimation → 平台能显示频率、电压等 phasor quantity、产生阈值告警并处理窗口化 RT measurements；正文没有统一 baseline 或 detection metric。[pdf:E10]（PDF 物理页 5，Section VII 与 Figs. 8–9）
- **真实用户侧设备能否进入 microgrid PHIL？** → 真实 house 通过 10-kW power amplifier 接入 eMEGAsim distribution network → 案例可研究并网/离网和 frequency control，但作者强调 simulator、amplifier、house 构成的 closed loop 可能失稳。[pdf:E11]（PDF 物理页 6，Section VIII 与 Fig. 10）
- **RT simulation 能否覆盖非常大的新能源电网？** → 在 Hypersim 中建立 Hydro-Québec 网络，包含 643 three-phase buses、34 hydro generators、1 steam generator、1 multiterminal dc link、25 DFIG wind plants、7 SVC、6 synchronous condensers、167 lines 和 150 saturation transformers → 72 个 SGI processors 以 50 μs 时间步运行该 EMT 网络。[pdf:E13]（PDF 物理页 7，Section X–XI 交界）
- **不需要快速 EMT 时能否进一步扩展规模？** → ePHASORsim 用 phasor solver、two-step Euler 与 sparse nodal solution → 报告约 20 000 buses、10 ms 时间步且快于 real time，并已用于 DNP3 接口下的 local/wide-area control software 测试。[pdf:E13]（PDF 物理页 7，Section XI）[pdf:E14]（PDF 物理页 7，Section XI 与 Conclusion）

这些案例支持“RT simulation 能作为多类 smart grid 研发的共同试验底座”，却不能支持“所有案例已经达到现场等价精度”或“某一 solver 在统一 benchmark 上优于其他方法”。

## § 8 — Take-aways

**5 句话：** Smart grid 的主要验证困难是控制、通信、计算和硬件形成了跨层闭环。RT simulation 让这个闭环在实验室中按真实时间运行，并允许安全重复故障与异常工况。不同问题需要不同 fidelity：EMT 保留快速暂态，phasor 换取大规模，HIL/PHIL 暴露真实接口与设备效应。SSN、稀疏求解和并行化解决的是 deadline 内可计算性，但任何人为解耦延时都可能改变故障物理。本文最有价值的是应用版图与工程边界，而不是统一算法或完整 benchmark。

**3 句话：** 真实时间只有与真实接口、异常场景和可核验参照结合，才形成有意义的验证。模型精度、时间步、计算结构和硬件闭环必须由待验证的物理现象共同决定。论文展示了 RT 技术的广泛可用性，但没有证明 lab-to-field 的普遍可迁移性。

**1 句话：** 用与问题匹配的实时模型把 smart grid 的关键闭环搬进实验室，再以 deadline 和物理误差同时验收。

## § 9 — 最脆弱的假设

最脆弱的假设是：**RT 实验中的模型、通信接口和功率接口保留了足以预测真实系统稳定性与保护行为的动态。** 如果这个假设不成立，实验可以完美实时、没有 deadline miss，却仍对真实电网给出错误结论。

论文自己提供了三处警示。第一，compensated delay 在潮流研究中能得到低于 0.002% 的功率误差，却不适用于 fault transient，因为延时会显著扭曲暂态。[pdf:E06]（PDF 物理页 3，Section V）第二，PHIL 中 simulator、amplifier 与 real house 是一个可能失稳的闭环。[pdf:E11]（PDF 物理页 6，Section VIII）第三，AIT 的 PV 案例并不知道 inverter filter 的完整 component values，因此用 ideal transformer model 或 multirating algorithm 实现 power interface，并把整体带宽设为 1 kHz 作为稳定性与精度的折中。[pdf:E12]（PDF 物理页 6，Section IX）

作者给出的证据说明研究者意识到了这一风险，并在不同案例里选择了接口算法和时间尺度；但论文缺少统一的 uncertainty budget、interface-delay sweep、amplifier saturation test 以及 lab-to-field 对照。因此“能在 RT 平台运行”不能自动升级为“能预测现场行为”。

## § 10 — 最小复现实验

一周内最值得复现的是“无算法延时的分区 EMT 能同时满足实时 deadline 和故障暂态精度”这一点，因为它直接检验本文连接数值计算与物理可信度的核心。

可选一个公开 radial distribution feeder，扩展为约 200 个节点并使用短 pi-line、一个 OLTC、分布式电源和可控负荷。实现两个版本：一个是单体离线 EMT reference，另一个按电气连接点分成 4–6 个 partition，在固定 50 μs 时间步下并行求解；如果现有工具不能实现 SSN，可把“无延时 nodal coupling”作为最小替代，但必须明确不是复现原始实现。测试 steady-state load step、OLTC tap change、三相短路和故障切除，记录每步 wall-clock execution time、deadline miss、关键母线电压/电流波形误差、保护动作时刻和故障后恢复轨迹。

支持结果应同时满足两点：绝大多数步骤在 50 μs deadline 内完成，且故障与开关事件的波形和动作时刻与离线 reference 一致到预先规定的容差。若只有平均计算时间合格、事件步频繁超时，或潮流误差很小但 fault transient 明显偏移，就反驳“可用于保护/暂态验证”的版本。论文的 210-bus、50 μs、低于 0.002% 潮流误差案例只是性能锚点，不应被当成本复现实验预设的成功答案。[pdf:E06]（PDF 物理页 3，Section V）

## § 11 — 最强反例设计

最强反例不是再扩大网络，而是构造一个**仿真判稳、真实闭环却失稳**的 PHIL 场景。选择带未知或温漂明显的 output filter 的真实 grid-connected inverter，通过可调 power amplifier 接入 RT feeder；系统性扫描 grid impedance、communication delay/jitter、amplifier saturation、measurement noise 和 reactive-power controller gain。对每个工况分别运行纯数字仿真、PHIL 和尽可能小功率的 physical hardware reference，比较振荡频率、阻尼、保护动作与失稳边界。

如果纯 RT/理想接口预测稳定，而 PHIL 或 physical reference 在同一 controller setting 下出现持续振荡、错误跳闸或保护漏动，就说明真正决定结果的是未建模接口动态，而不是论文强调的 grid/controller mechanism。这个攻击直接针对作者已经观察的 PHIL closed-loop stability 风险，以及 PV 案例用 1 kHz 带宽和近似 power interface 处理未知 filter 参数的做法。[pdf:E11]（PDF 物理页 6，Section VIII）[pdf:E12]（PDF 物理页 6，Section IX）它比“模型可能不准”更强，因为它给出可预测的失效条件和三层对照。

## § 12 — Follow-up Research Idea

候选方向是：**建立带在线可信度预算的跨时间尺度 RT 验证系统，使 EMT、phasor 与 PHIL 不是三个独立模式，而是在同一实验中依据事件与不确定性动态分配保真度。** 这是一项候选研究判断；本卡没有完成 2014 年之后相关工作的系统检索，因此不声称 novelty。

**（a）未满足需求。** 当前做法由研究者事先选定 solver 和 interface；一旦实验中出现 fault、converter interaction 或通信异常，原先适合慢动态的模型可能突然失效，却没有机制告诉使用者当前结论还能信到什么程度。

**（b）潜在研究价值。** 电气与控制领域认可的价值不只是更快，而是给保护动作、稳定边界和硬件安全提供可审计的 error/deadline guarantee。若系统能同时报告“这一步是否准时”和“这一步对当前决策是否足够准确”，RT simulator 才从演示平台变成证据生成平台。

**（c）可借鉴工具。** 可借鉴 hybrid systems 的 event-triggered model switching、runtime verification 的在线断言、uncertainty quantification 的误差界，以及 FPGA 的确定性并行 pipeline。FPGA 不只是加速器，而可承担高频局部 EMT island；CPU 处理大规模 phasor network，PHIL interface 监测实测残差并触发 fidelity 升级。

**（d）首个证伪实验。** 在含 inverter、OLTC 和保护 relay 的 feeder 上，让系统平时以 10 ms phasor 模型运行，检测到 switching/fault 前后切换局部 50 μs EMT/FPGA island，并与全程高精度 EMT + PHIL reference 比较。若切换边界产生不可接受的能量跳变、保护动作次序改变、deadline miss，或 residual 无法提前预警，研究假设即被证伪。这里的 10 ms phasor 与 50 μs EMT 量级来自论文案例，但动态切换方案是本卡提出的研究设计。[pdf:E13]（PDF 物理页 7，Sections X–XI）

**（e）与本文的实质区别。** 本文展示“按应用选择一种 RT 技术”；该方向把问题改为“运行中如何证明当前 fidelity 足够，并在不足时局部提升”。目标从扩大可实时仿真的系统规模，转向让每个实验结论携带动态的可信度边界。
