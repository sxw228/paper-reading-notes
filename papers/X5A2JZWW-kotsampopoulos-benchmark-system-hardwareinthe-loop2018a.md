# A Benchmark System for Hardware-in-the-Loop Testing of Distributed Energy Resources

**作者：** Panos Kotsampopoulos；Dimitris Lagos；Nikos Hatziargyriou；M. Omar Faruque；Georg Lauss；Onyi Nzimako；Paul Forsyth；Michael Steurer；F. Ponci；A. Monti；V. Dinavahi；Kai Strunz（IEEE PES Task Force on Real-Time Simulation of Power and Energy Systems）

**出处：** IEEE Power and Energy Technology Systems Journal，Vol. 5，No. 3，September 2018，pp. 94–103

**年份：** 2018

**DOI：** 10.1109/JPETS.2018.2861559

**Zotero key：** X5A2JZWW

**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是“如何再设计一个 DER controller”，而是更基础的工程问题：**不同实验室怎样用一套共同的低压配电网络、HIL 架构和实验步骤，对 distributed energy resources（分布式能源资源，DER）的控制器与功率设备开展可理解、可复用的实时测试。** 作者指出，HIL 已经被用于电力系统与 DER 的分析、验证和去风险，但当时尚缺少同时覆盖 reference system、CHIL、PHIL 和实验流程的共同方法；论文因此提出一个低压 benchmark system，并用集中式控制 CHIL 与本地控制 PHIL 两类案例展示其可用性（PDF 物理页 1，Abstract）[pdf:E01]。

这个问题重要，是因为离线数字仿真、controller hardware、power hardware 和真实接口各自会引入不同的模型误差、时间延迟和稳定性风险。若实验室只共享“网络拓扑”，却不共享模型粒度、接口边界和操作步骤，那么名义上相同的测试可能对应完全不同的物理问题。论文选择 CIGRE European LV network 为基础，在同一 feeder 中布置 PV、风机、microturbine、fuel cell 与 storage，意图让拓扑既保留真实低压网的主要技术特征，又能承载不同 DER 场景（PDF 物理页 2，Fig. 1 与 Section II）[pdf:E03]。

论文的直接价值是给研究者一条从“已有 benchmark network”走到“能在实验室安全闭环运行的 HIL test”的路径。更长期的价值则是为跨实验室比较、controller pre-deployment testing（部署前测试）和 DER ancillary services（辅助服务）验证建立共同语言。不过，本文真正完成的是**benchmark 框架与示例**，而不是已经被多实验室统计验证过的正式一致性标准。

## § 2 — 前人工作与不足

论文回顾表明，前人并非没有 benchmark：IEEE 已有多种 transmission/distribution test systems，CIGRE 也给出了北美和欧洲的 HV、MV、LV reference networks；CIGRE 网络已被用于高 PV 渗透、故障诊断和 microgrid operating modes 等研究。问题在于，这些工作主要解决“用什么网络做数字研究”，没有把网络如何映射到 digital real-time simulator（数字实时仿真器，DRTS）、如何连接 controller 或 power hardware、以及如何组织实验步骤统一起来。作者将缺口概括为 HIL 仍缺少 reference networks、test procedures 和 guidelines，并据此提出综合 benchmark network 与实时 HIL 指南（PDF 物理页 2，Introduction）[pdf:E02]。

已有实时仿真技术也能处理部分工程问题，但各有边界。DRTS 通常以离散 time step 推进；论文给出的典型尺度是约 50 μs 可覆盖从 DC 到约 3 kHz 的动态，而要捕捉 power-electronic switching transients，常需小于 5 μs。固定 deadline 会把网络规模、DER 模型数量和控制细节绑在同一计算预算内（PDF 物理页 2，Section II-A）[pdf:E04]。大系统可利用并行 rack 和 transmission-line propagation delay 解耦，但低压配电网线路短、耦合紧，人工加长线路会引入过大电容和异常高电压；缩短 time step 又会压缩可实时求解的系统规模。模型层面，P-Q source、average converter model、sub-cycle average model 和 full PWM model 之间也存在清晰的 accuracy–computation trade-off（PDF 物理页 3，Section II-A、II-B 与 Fig. 2）[pdf:E05]。

CHIL 与 PHIL 本身也早已存在。CHIL 的困难主要是 I/O、通信协议和 signal timing；PHIL 还必须加入 power amplifier、sensor、D/A、A/D 和闭环 feedback，因此 interface delay、filter 和 amplifier dynamics 可能直接决定实验是否稳定。本文之前已有 ITM、DIM 等 interface algorithms 以及稳定性、准确性分析方法，但它们更多是局部技术方案，尚未组成一套围绕共同 DER benchmark 的完整实验契约。论文的不足判断因此不是“前人没做 HIL”，而是“**网络、实时实现、接口和实验流程仍是分散的，结果难以在共同基准上解释**”。

## § 3 — 重建作者的思考路径

以下是基于论文证据的逆向重建，而不是作者逐字陈述。

第一步，研究者会先发现：重新发明 feeder 没有必要。CIGRE LV network 已经有较强的代表性和使用基础，因此更合理的起点是复用其 topology 与 DER composition，而不是设计一个只适合单个实验室的网络（PDF 物理页 2，Fig. 1）[pdf:E03]。

第二步，研究者会遇到“离线 benchmark 不能直接变成实时 benchmark”的障碍。实时系统每个 step 必须按 deadline 完成，网络分区、模型粒度和 switching detail 会竞争同一计算资源；因此 benchmark 必须允许研究目的驱动模型简化，同时要求明确写出简化边界（PDF 物理页 2–3，Section II-A、II-B）[pdf:E04][pdf:E05]。

第三步，研究者会意识到 controller testing 与 power-device testing 不能共用一张抽象框图。CHIL 只闭合信号回路，PHIL 则闭合能量回路；后一种系统多出 amplifier、sensor 与 power interface，稳定性风险发生了质变。于是 benchmark 至少需要两种标准 architecture，而不能只有一套通用“hardware in the loop”描述（PDF 物理页 4，Fig. 3）[pdf:E06]。

第四步，仅给 architecture 仍不足以复现。真正的实验会在 wiring、calibration、protection、stability assessment、loop closure 和 result acquisition 上失败。因此作者把 benchmark 从“模型”扩展成“模型 + 设备接口 + 顺序化 laboratory procedure”，分别为 CHIL 与 PHIL 给出 preparation 和 execution 步骤（PDF 物理页 5，Table 1、Table 2）[pdf:E08][pdf:E09]。

最后，为证明这套框架不是空泛 checklist，作者选择两种互补任务：CHIL 测 centralized optimization controller，PHIL 测实际 PV inverter 的 local droop behavior。前者展示 controller decision loop，后者展示真实 power hardware 与 simulated grid 的双向耦合。

## § 4 — 核心 Intuition

这篇论文的核心 intuition 是：**HIL benchmark 不是一个固定网络文件，而是一份把“被模拟的电网、被保留的动态、硬件边界、接口链路和实验步骤”同时固定下来的实验契约。** CHIL 把硬件放在控制决策侧，PHIL 把硬件放在功率交换侧；只有明确这条边界，结果才知道是在验证 algorithm、device，还是 interface artifact（PDF 物理页 4，Fig. 3、Fig. 4）[pdf:E06][pdf:E07]。

因此，方法奏效的关键不是某个新 solver，而是把已有 CIGRE network、实时模型选择、接口工程和安全流程组合成一个可执行 benchmark。它改变的假设是：benchmark 的可复用性不只来自 topology，也来自对实验闭环的共同约束。

## § 5 — 具体方法与完整 Pipeline

论文给出的完整 pipeline 可以重建为以下六步。

1. **选择共同电网。** 以 CIGRE European LV benchmark 为母体，保留典型 LV feeder、transformer、loads 和多类 DER 的连接关系（PDF 物理页 2，Fig. 1）[pdf:E03]。
2. **按研究频段选择实时模型。** 先确定需要保留的是慢速 power-flow/control dynamics，还是 converter switching transients，再据此选择 time step、network reduction、single-phase equivalent、P-Q source、average model 或更详细的 PWM/device model。论文强调，约 50 μs 与小于 5 μs 对应不同动态范围和计算代价（PDF 物理页 2–3，Section II-A、II-B）[pdf:E04][pdf:E05]。
3. **选择 hardware boundary。** 若被测对象是 microgrid controller、DSP 或 control board，采用 CHIL：DRTS 计算电网，硬件 controller 接收 measurements 并返回 set-points。若被测对象是 inverter 等 power component，采用 PHIL：DRTS 的低电平参考经 D/A 与 amplifier 变为实际电压或电流，HUT 响应经 sensor 与 A/D 反馈，闭合功率回路（PDF 物理页 4，Fig. 3、Fig. 4）[pdf:E06][pdf:E07]。
4. **建立接口与安全边界。** CHIL 要校准 signal paths、验证 I/O 与通信；PHIL 还要预先检查 Nyquist 或动态仿真意义下的 stability/accuracy，配置 protection 与 compensation，并分阶段启动 power interface、连接 HUT、发送 feedback、最后 closing the loop（PDF 物理页 5，Table 1、Table 2）[pdf:E08][pdf:E09]。
5. **执行 benchmark case。** 运行 controller-off/controller-on 或 grid-connected/islanded 等对照工况，记录 hardware measurements、DRTS signals 和 controller states。
6. **把结果解释回共同对象。** 不是只看一条曲线“是否变好”，还要说明用了何种模型简化、接口和 HUT operating point；否则无法判断变化来自控制策略还是实验链路。

**CHIL 示例。** 作者把 benchmark 简化为 single-phase equivalent，并把所有 DG 视作 PV P-Q sources；centralized controller 在独立硬件板上运行，以 load、PV 和 state-of-charge measurements 为输入，向 BESS 与 PV 返回 active/reactive set-points。Fig. 5 给出 DRTS 中的简化 feeder，Fig. 6 给出 DRTS、A/D-D/A、controller board 与 signals 的闭环关系（PDF 物理页 6，Fig. 5、Fig. 6）[pdf:E11]。实验比较有无 centralized control 时的 main-grid active-power exchange；论文报告 peak shaving 主要发生在 18:00–22:30，battery 在低负荷时吸收 active power、在峰时放电，同时用 reactive power 支撑电压（PDF 物理页 6，Fig. 7–Fig. 9 与相邻正文）[pdf:E12]。PV reactive-power dispatch 和 node voltages 的对照显示，controller 运行时最弱节点的电压下陷得到缓解（PDF 物理页 7，Fig. 10–Fig. 12）[pdf:E13]。

**PHIL 示例。** 作者在同一简化 feeder 中把一台额定 single-phase AC power 为 3 kVA、支持 ancillary services 的 commercial PV inverter 接到 load #4 bus，使用 linear amplifier 与 current sensor 构成功率接口（PDF 物理页 7，Section IV-B-1）[pdf:E15]。在 grid-connected case 中，simulated DG 与 hardware inverter 均采用 Q(U) 和 P(f) droop；Q(U) 激活后，节点电压向 nominal value 靠近，而 hardware inverter 因接近 apparent-power limit，会降低 active power 以留出 reactive-power absorption 能力（PDF 物理页 7–8，Fig. 13–Fig. 16）[pdf:E14][pdf:E16]。在 islanding transition 中，storage 使用 f(P)、V(Q)，DG 使用 P(f)、Q(U)；相应曲线显示 storage 吸收 active power、DG curtail active power 并提供 reactive support（PDF 物理页 8，Fig. 17–Fig. 22）[pdf:E16][pdf:E17]。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有提出新的形式化模型、定理或核心推导，因而不存在可逐式复现的数学证明。它采用的是工程上常见的 characteristic-map 表达，核心应理解为闭环物理意义，而不是公式创新。

- **Q(U)：** terminal voltage 偏高时，inverter 吸收 reactive power；偏低时则提供 reactive power。Fig. 14 画出带 deadband/limit 的典型分段特性。由于 inverter 受 apparent-power capability 约束，当需要更多 Q 而工作点已接近额定容量时，必须减少 P，论文的 hardware trace 正好展示了“active power reduction to absorb reactive power”（PDF 物理页 7–8，Fig. 14、Fig. 16）[pdf:E14][pdf:E16]。
- **P(f)：** frequency 超过设定阈值时，DG 通过 active-power curtailment 抑制过频。论文的 islanded case 写明，当 frequency 超过 50.2 Hz threshold，simulated DG 与 hardware DG 都降低生产；带 P(f) droop 的曲线比无 droop 时具有更低的最终频率（PDF 物理页 8–9，Fig. 18–Fig. 20 与相邻正文）[pdf:E16][pdf:E18]。
- **f(P)、V(Q)：** islanded storage 通过 active-power imbalance 调节 frequency、通过 reactive-power imbalance 调节 voltage，充当形成 microgrid reference 的设备；DER 的 P(f)、Q(U) 则在该 reference 周围分担功率与支撑电压（PDF 物理页 8，Section IV-B-2、Fig. 17–Fig. 22）[pdf:E16][pdf:E17]。

这里最需要警惕的是：这些 droop curves 只定义 controller law 的静态/低阶关系，PHIL 闭环的 stability 还取决于 DRTS step、amplifier bandwidth、sensor/filter 和 total loop delay。论文明确说大 time step 会增加总延迟，power-interface filter 也会影响 stability 与 accuracy（PDF 物理页 4，PHIL interface discussion）[pdf:E07]。

## § 7 — 实验设计与结论

**问题 1：共同 benchmark 能否承载硬件 centralized controller 的实时闭环测试？** 设计：作者在 DRTS 中实现简化 LV microgrid，把 optimization controller 放到 hardware board，比较 controller off/on 的 main-grid power exchange、BESS power/SoC、PV reactive power 与 node voltages（PDF 物理页 6–7，Fig. 5–Fig. 12）[pdf:E11][pdf:E12][pdf:E13]。答案：在所选 daily-load/irradiation case 中，controller 实现 peak shaving，并改善 node-voltage profile。这个实验支持“框架可运行并能观察控制效果”，但没有报告 optimization objective 的数值收敛、实时 deadline miss、cross-platform repeatability 或统计误差，因此不能外推为该 controller 已被全面验证。

**问题 2：PHIL 能否观察真实 PV inverter 的 grid-support 行为？** 设计：将 3 kVA commercial inverter 作为 HUT，连接到 benchmark bus，先关闭再激活 Q(U)，观察 HUT active/reactive power 与多节点 voltage（PDF 物理页 7–8，Fig. 13–Fig. 16）[pdf:E14][pdf:E15][pdf:E16]。答案：Q(U) 使节点电压更接近 nominal，硬件 inverter 同时出现 active-power curtailment 与 reactive-power absorption。实验说明 benchmark 能把设备 capability limit 与 grid response 放到同一闭环中观察；但它只覆盖一台 inverter、一个连接点和一个高 irradiation operating region。

**问题 3：local droop 能否改善从 grid-connected 到 islanded 的过渡？** 设计：storage 使用 f(P)、V(Q)，simulated/hardware DG 使用 P(f)、Q(U)，比较 frequency no-droop 与 frequency droop，并记录 storage、DG、HUT 和 node-voltage transients（PDF 物理页 8–9，Fig. 17–Fig. 23）[pdf:E16][pdf:E17][pdf:E18]。答案：P(f) 限制 over-frequency，DG 在 50.2 Hz 以上 curtail active power；Q(U) 提供 reactive support，缓解由 storage reactive demand 引起的 voltage reduction。它验证的是所选配置下的 qualitative mechanism，不是对 arbitrary interface delay、fault condition、unbalanced feeder 或 switching-level dynamics 的鲁棒性证明。

**问题 4：论文是否证明了 benchmark 的跨实验室标准化能力？** 设计上没有 round-robin、inter-laboratory comparison、统一 error metric 或 objective quality indicator。作者自己指出，不同 PHIL interface algorithm 各有 stability/accuracy 特性，并把“形式化不同 error/uncertainty 对 HIL accuracy 的影响、为结果配备 objective quality indicators”列为 future work（PDF 物理页 5，Section III-C）[pdf:E10]。因此答案是：论文证明了 benchmark concept 的工程可行性和示例价值，但尚未证明跨实验室的量值一致性。

## § 8 — Take-aways

**5 句话：**

1. 论文把 DER HIL benchmark 从“参考网络”扩展为“网络、实时模型、hardware boundary、interface 和 laboratory procedure”的组合。
2. CIGRE LV feeder 提供共同 topology，但 DRTS time step、network partition 和 DER model fidelity 决定它是否能真正实时运行。
3. CHIL 适合把 controller algorithm 放入闭环，PHIL 则能暴露真实 power hardware、capability limit 与 grid dynamics 的相互作用。
4. 两个案例表明 centralized control 可做 peak shaving/voltage support，local droop 可在 grid-connected 与 islanding transition 中提供 voltage/frequency support（PDF 物理页 9，Conclusion）[pdf:E19]。
5. 论文最大未完成项是缺少可量化的 HIL quality certificate 和跨实验室一致性验证。

**3 句话：** 这不是一篇新控制算法论文，而是一篇实验方法论与 benchmark 架构论文。它最有用的部分是把 model-fidelity trade-off、CHIL/PHIL interface 和顺序化 test procedure 放进同一套 DER 场景。它展示了“能做”，但还没有证明“不同实验室做出来会等价”。

**1 句话：** 一个可信的 HIL benchmark 必须同时规定电网问题、实时近似和硬件闭环，而不能只发布一张 feeder 图。

## § 9 — 最脆弱的假设

最脆弱的假设是：**只要实验室采用同一 nominal network 和大体相同的 CHIL/PHIL procedure，不同实时模型与接口实现仍会保留足够一致的闭环行为，从而让结果具有可比性。** 如果这个假设不成立，论文的核心贡献就会从“benchmark system”退化成“一个实验室可参考的示意 setup”。

这个假设在实际中很容易失效。DRTS step 与 computational partition 会改变 numerical delay；average model 与 full switching model 会改变高频动态；PHIL amplifier 的 bandwidth、slew rate、filter、sensor 和 A/D-D/A delay 会移动 stability margin；HUT 接近 apparent-power limit 时，P–Q coupling 又会改变控制响应。论文对这些机制都有直接承认（PDF 物理页 2–4，Section II 与 PHIL interface discussion）[pdf:E04][pdf:E05][pdf:E07]。

论文给出的支持证据是：两套架构确实能在一个 benchmark feeder 上运行，且实验曲线符合 peak shaving、Q(U)、P(f) 的预期物理方向。缺少的证据更关键：没有报告实际 real-time step、worst-case execution time、总 loop delay、amplifier/sensor transfer characteristics、interface algorithm 参数、数值误差、重复次数和跨平台结果。作者把 objective quality indicators 留给 future work，本身说明当前 procedure 尚不足以闭合 comparability（PDF 物理页 5，Section III-C）[pdf:E10]。

## § 10 — 最小复现实验

一周内最值得做的不是复制全部 PHIL laboratory，而是验证论文最核心、也最容易被证伪的 claim：**同一 benchmark + 明确 hardware boundary，能否在满足实时 deadline 的前提下稳定重现 controller-on/off 的系统级差异。**

数据与模型：依据 Fig. 5 重建 single-phase simplified feeder、四个 PV P-Q sources、五个 controllable loads 和一个 BESS；负荷与 PV 不追求逐点复制论文曲线，而使用公开声明的“daily load + sunny-day irradiation”形状构造归一化 24 h profile，并明确这是 mechanism reproduction，不是数值复刻（PDF 物理页 5–6，Section IV-A、Fig. 5）[pdf:E10][pdf:E11]。

实现：把 feeder 放在固定-step real-time process，把 centralized controller 放在独立进程或 controller board，通过与 Fig. 6 相同的 measurements/set-points 边界连接。运行两次完全相同 profile：controller off 与 controller on。控制器只实现三个目标：限制 transformer peak、约束 node voltage、保持 BESS SoC 可行。

测量：记录每个 step 的 execution time/deadline miss、main-grid peak power、最大 node-voltage deviation、BESS energy/SoC 和 active loss。预注册支持标准可以设为：全程无 deadline miss；controller-on 的 peak 至少降低 10%；最大 voltage deviation 不恶化，且 SoC 不越界。反驳标准是：控制效果只在放宽 deadline、改变 model step 或加入非论文所述的平滑后才出现，或者 controller-on 导致 voltage/SoC 约束破坏。

这个最小实验不证明 PHIL 标准化，但能验证论文的第一层贡献：benchmark topology、实时模型和 hardware controller interface 是否真的形成可重复的 CHIL test，而不是离线优化曲线的重新播放。论文中的参考趋势是 peak interval 内 BESS 放电、低负荷时充电，以及 controller-on 后 node voltages 改善（PDF 物理页 6–7，Fig. 7–Fig. 12）[pdf:E12][pdf:E13]。

## § 11 — 最强反例设计

最强攻击不是换一个更难的 feeder，而是做一次**接口等价性反例**：保持 benchmark network、HUT、droop curves 和 operating scenario 完全相同，只改变论文允许但未固定的 PHIL implementation details，然后检查论文的结论是否改变。

具体设计是使用同一 3 kVA inverter 和同一 Q(U)/P(f) case，构造两条功率接口：A 为低延迟、高带宽配置，B 在 datasheet 合法范围内增加 total loop delay、降低 bandwidth 或改变 feedback filter；若条件允许，再比较 ITM 与 DIM。两条接口都通过各自的稳定性预检查，然后执行相同的 grid-connected Q(U) 激活和 islanding transition。记录 oscillation margin、node-voltage improvement、HUT active curtailment、reactive support、frequency nadir/peak 和 settling time。

若配置 A 得到论文所示的 voltage support，而配置 B 出现振荡、反向电压效果或显著不同的 active curtailment，即使两者都声称遵循同一 benchmark procedure，核心 comparability 假设就被推翻。此时对论文结果的替代解释是：观察到的“controller/device benefit”部分来自特定 amplifier/filter/delay 的闭环塑形，而非 benchmark network 或 droop law 本身。这个攻击直接针对论文承认的非理想 power interface、loop delay 与 filter 对 stability/accuracy 的影响（PDF 物理页 4–5，PHIL discussion 与 Section III-C）[pdf:E07][pdf:E10]，也正好覆盖其示例中 hardware inverter 的 P–Q coupling 与 islanding response（PDF 物理页 7–9，Fig. 15–Fig. 23）[pdf:E14][pdf:E16][pdf:E17][pdf:E18]。

## § 12 — Follow-up Research Idea

**候选研究方向：建立“可执行的不确定性包络 benchmark”，而不是再增加一个 test case。** 由于本文未进行完整相关工作检索，这里不声称 novelty。

(a) **未满足需求。** 当前 benchmark 能规定 topology 和 procedure，却不能回答“两个实验室的结果在多大误差内算同一个结果”。论文自己提出需要形式化 error/uncertainty 对 HIL accuracy 的影响并给出 objective quality indicators（PDF 物理页 5，Section III-C）[pdf:E10]。

(b) **潜在研究价值。** 对电力电子与电力系统实验而言，高影响价值不只来自新 controller，也来自可验证的工程可实现性和可追溯 measurement。若 benchmark 输出的不再是一条理想曲线，而是“在给定 time step、model fidelity、loop delay、bandwidth、noise 和 HUT operating point 下允许的 response envelope”，它就能支持 inter-laboratory conformance testing、设备验收和标准制定。

(c) **可借鉴工具。** 可以结合 robust control 的 uncertainty set、system identification 的 interface model、metrology 的 traceability 与软件领域的 executable conformance test。论文参考的 online impedance identification 思路也提示，部分 interface uncertainty 可以在线估计，而不必只依赖静态 datasheet。

(d) **首个证伪实验。** 在两套不同 amplifier/simulator configuration 上运行同一 Q(U) 与 islanding case。先由各自测得的 delay/bandwidth/impedance 生成预测 envelope，再检查 hardware traces 是否落入包络。若大量观测越界，或 envelope 宽到无法区分 controller good/bad，该研究方向就失败。

(e) **与本文的实质区别。** 本文交付的是 reference network、CHIL/PHIL architecture、procedure 与示例结果；候选工作交付的是 machine-readable experiment contract、interface uncertainty model、quality score 和可被 round-robin 直接检验的 admissible response set。它改变的是 benchmark 的目标：从“指导如何搭实验”转为“量化何时两个实验结果可以被判定为等价”。
