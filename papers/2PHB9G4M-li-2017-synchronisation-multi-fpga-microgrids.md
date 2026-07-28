# Synchronisation mechanism and interfaces design of multi-FPGA-based real-time simulator for microgrids

- 作者：Peng Li, Zhiying Wang, Chengshan Wang, Xiaopeng Fu, Hao Yu, Liwei Wang
- 出处：IET Generation, Transmission & Distribution, 2017, 11(12): 3088-3096
- DOI：10.1049/iet-gtd.2016.1552
- Zotero key：2PHB9G4M

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“单块 FPGA 上怎样把某个电路模型算得更快”，而是一个系统集成问题：当微电网的高频电力电子器件、分布式电源和储能使单块 FPGA 的逻辑、DSP 和存储资源不够时，怎样把计算拆到多块独立 FPGA 上，同时保证各卡按同一个仿真时间推进、正确交换边界数据，并能通过 AD/DA 接口连接真实设备。作者在摘要中把目标概括为多 FPGA 拓扑、时间步同步、精确通信以及外部模拟接口，并报告在 4 块 FPGA 上以 3 μs 步长运行一个含 PV 和电池的微电网案例。[pdf:E01]

这个问题重要，是因为“增加卡数”本身并不自动增加可用仿真规模。卡间通信会占用每个实时步长的预算；独立晶振会产生 clock skew；边界数据如果晚到、错步或跨时钟域失稳，即使每块卡局部计算正确，整体 EMT 时序也会错误。论文明确指出，通信延迟会增加执行时间并限制可选步长，而不同 FPGA 的独立时钟会造成数据交换混乱。[pdf:E03] [pdf:E04]

从实时系统角度，真正的验收条件是：每一个数值时间步都必须在同样长的墙钟时间内完成，这个上限就是实时 deadline。论文的 4-FPGA 案例给出 3 μs 步长及分项执行时间，因此证明了这个特定分区在该平台上有运行余量；但它没有证明增加卡数后，通信、同步和 I/O 的最坏延迟仍能落在 deadline 内。[pdf:E05] [pdf:E07]

## § 2 — 前人工作与不足

作者把 RTDS 和 RT-LAB 作为成熟实时仿真背景。论文特别描述了 RTDS 的 rack 结构：一个 rack 最多与六个其他 rack 通信，每个 rack 最多六张处理卡；GTWIF 卡生成步长与通信区间信号，多 rack 时由 global bus hub 协调，rack 间用标准 Ethernet、rack 内用背板通信。这说明多处理器同步和互联并非新问题，但该能力依赖 RTDS 的专用机架、接口卡和总线结构。[pdf:E02]

论文还引用了把多枚 FPGA 集成在同一商用板上的既有方案，并把它与本研究的目标区分开：作者希望使用各自带单枚 FPGA 的开发板，通过 SFP/QSFP 光纤链路组成可重配拓扑，以适配不同分区和 multi-rate 场景。论文列举 crossbar、hierarchical crossbar 和 mesh 等既有多 FPGA 拓扑，随后选择 mesh 与 linear array 的组合，使不同通道数的板卡可形成 loop、radial 或 chained 结构。[pdf:E02] [pdf:E03]

因此，论文补的是“由通用 FPGA 开发板构成一个完整实时仿真器”所缺的接口层：拓扑、步长同步、跨时钟域通信和外部 AD/DA。它没有与 RTDS 做吞吐、抖动、成本或可扩展性对照，也没有证明其拓扑优于既有拓扑；贡献是可实施的设计与一个 4 卡案例，而不是完整的多卡扩展定律。

## § 3 — 重建作者的思考路径

下面是基于论文背景与工程约束的重建，不是作者逐字陈述。

第一步，微电网详细 EMT 模型包含大量高频开关、PV、储能和控制器，单卡资源会成为硬约束；把问题分区到多块 FPGA，是比不断更换更大芯片更可持续的扩容方向。[pdf:E01] [pdf:E02]

第二步，分区之后，局部求解不再是唯一瓶颈。各板有独立时钟，跨卡数据又必须在正确的数值时间步被消费，所以需要一个共同的步长基准；如果还要支持 multi-rate，基准不能只是一种固定步长，而应允许各卡步长取最小间隔的整数倍。[pdf:E03] [pdf:E04]

第三步，接口必须同时处理位宽与时钟域。电气系统使用 64-bit double precision，控制系统使用 32-bit single precision，而 FPGA fabric 到 transceiver 的 datapath 是 16 bit；因此需要 serializer/deserializer。fabric clock 与收发器 clock、ADC/DAC clock 彼此不同，因此需要 dual-clock FIFO 隔离跨时钟域数据与控制。[pdf:E03] [pdf:E04] [pdf:E05]

第四步，把这些机制放入真实分区：用 Bergeron's line model 把网络、PV/电池单元和两个 PV 单元切成四个子系统，分别映射到四块 FPGA，再用实际光纤、AD 输入和 DA/示波器输出验证接口是否能支撑一个完整案例。[pdf:E05] [pdf:E06]

这条思路的关键转折是：可扩展实时仿真不只取决于“总计算资源”，而取决于分区边界上的数据能否在每步 deadline 前以正确 step identity 到达。论文实现了这个接口，但只在一个 4 卡分区上验证。

## § 4 — 核心 Intuition

把一块大 FPGA 换成多块 FPGA 后，必须把“仿真时间”也变成显式的共享协议：由 master 发出步长起始信号，slave 收到后才推进，并用光纤链路和 FIFO 在不同时钟域之间搬运边界数据。[pdf:E03] [pdf:E04] 对 multi-rate，所有卡的步长都取一个可配置最小间隔的整数倍；对外部设备，则用同样的跨时钟域缓冲思想接入 ADC 和 DAC。[pdf:E04] [pdf:E05] 真正的核心不是卡越多越快，而是同步与通信开销不能吃掉实时步长。

## § 5 — 具体方法与完整 Pipeline

以论文的 4-FPGA 微电网为例，完整 pipeline 如下。

1. **离线建模与分区。** 应用程序完成 topology identification、system partition、time-step determination 和参数生成，并把结果保存为 memory initial data files；Verilog 编写的 operation program 在 Quartus II 中编译后下载到 FPGA。在线框架采用 nodal analysis，并分成 global control、electrical system solution、control system solution、data interaction 和 interface 五类模块。[pdf:E02] [pdf:E03]

2. **数值与控制映射。** 电气系统包含 RLC、开关、断路器、耦合线路、受控源、供电源和 network solver，采用 64-bit double precision；控制模块按顺序执行 PI、PLL、Park 变换等功能，采用 32-bit single precision以降低资源占用。电气与控制模块通过 data interaction module 交换电压、电流、开关状态和控制命令。[pdf:E03]

3. **拓扑与分区边界。** 通用设计按板卡可用链路数把四通道板接成 mesh、双通道板接成 linear array、单通道板放在端点，并允许 loop、radial 和 chained 配置。实际案例使用 radial：FPGA1 是 network 与 master；FPGA2 是 PV/battery；FPGA3、FPGA4 分别是 PV unit 1、PV unit 2。Bergeron's line model 的两端分属不同子系统，成为分区边界。[pdf:E03] [pdf:E05] [pdf:E06]

4. **步长同步。** 相同步长时，master FPGA1 在每步发送 synchronisation pulse，slave 只有收到它才启动；为补偿传播延迟，master 的本地启动被相应推迟。不同步长时，master 以最小间隔 `Δt_min` 发同步信号，各卡步长独立设置为 `Δt_min` 的整数倍。若 master 不能直连某个 slave，中间 slave 转发同步信号，论文要求 master 启动再后移两倍传输延迟。[pdf:E03] [pdf:E04]

5. **内部通信。** 32/64-bit 仿真数据先按 2 或 4 的 factor 串并转换到 16-bit datapath，再由 channel selector 路由到各通道；dual-clock FIFO 连接 fabric 与 transceiver 时钟域；transceiver 把 16-bit 并行数据串化成 1-bit 高速流并经 SFP/QSFP 光纤发送。论文称采用的通信标准为 “GigE-2.5 Gbps”，同步信号与仿真数据共享 transceiver channel，并用 time-division multiplexing 避免混淆。[pdf:E04]

6. **外部接口。** AD 侧由 FPGA 产生 `clk_ad` 和 enable，ADC 连续采样；dual-clock FIFO 把 ADC 时钟域数据交给 `clk_sim` 域，并进行 16-bit 到 32/64-bit 的格式转换。DA 侧在每步末把仿真数据写入 FIFO，再由 `clk_da` 域读取并转换为模拟量。案例使用 AD7606 作为 8-channel、16-bit、200 kHz ADC，使用 DAC900 的 10-bit 选项，更新率超过 165 MSPS；真实波动 irradiance 经 AD 输入，仿真电压电流经 DA 输出到 oscilloscope。[pdf:E04] [pdf:E05] [pdf:E06]

7. **实时执行与输出。** FPGA1 总计向三个 slave 发送 18 个 64-bit 数据，报告通信时间 0.680 μs；每个 slave 向 FPGA1 发送 6 个 64-bit 数据，报告 0.488 μs。论文选择 3 μs 步长，并说明通信时间已包含在 electrical-system execution time 中；0.680 μs 占步长 22.67%。[pdf:E05] [pdf:E07]

这里的 “synchronisation” 更接近 master 广播的 step-opening gate，而不是论文已证明的全局 barrier。所谓全局 barrier，是所有参与者都报告到达后才统一释放下一步；论文没有描述全卡 completion acknowledgement、step sequence number 或 collect-and-release 过程。因此不能把图 2 外推为已经证明任意卡数下都不会有晚到边界数据。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出新的 EMT 数值算法推导、稳定性定理或通信复杂度模型。它的形式化内容主要是同步时序关系。

相同步长时，图 2a 把步长写成 `Δt = n·clk = n'·clk'`：两块 FPGA 可以有不同本地 clock period 与 cycle count，但每次仿真推进都对应同一个物理间隔 `Δt`。master 的同步脉冲定义 step boundary，slave 收到脉冲后启动；传播延迟通过推迟 master 的本地启动来补偿。[pdf:E03]

multi-rate 时可写成 `Δt_i = k_i·Δt_min`，其中 `k_i` 为正整数。图 2b 的示例是 `Δt_1 = 2Δt_min`、`Δt_2 = 3Δt_min`、`Δt_3 = 4Δt_min`；共同的 `Δt_min` 提供对齐网格，各 FPGA 只在属于自己的格点上推进。[pdf:E03] [pdf:E04]

这个关系说明“何时允许启动”，却没有证明“所需边界数据必然在启动前到达”。也没有给出卡数 `N`、hop 数 `h`、payload `B` 与最坏步长开销之间的函数，例如 `T_step ≥ max(T_compute) + T_sync(N,h) + T_comm(B,N,h)`。因此，规模增长与 deadline 的关系仍是论文外的待验证问题。

## § 7 — 实验设计与结论

**问题 1：四块 FPGA 能否承载这个分区？** 实验把 12 个三相节点、一个 PV/battery 单元和两个 PV 单元按 Bergeron 线路分成四个子系统。整个案例包含 3 个 supply source、7 个 controlled source、70 个 RLC、21 个 IGBT、22 个 diode、48 个 meter、15 条三相耦合线路和 3 个 Bergeron's line model；Table 1 给出每卡元素分布。[pdf:E05] [pdf:E06] 资源结果显示 FPGA1 的 logic/DSP/memory 为 73%/24%/57%，FPGA2 为 67%/10%/68%，FPGA3 与 FPGA4 均为 50%/6%/67%；这证明该 4 卡映射放得下，但不是随卡数扩展的资源模型。[pdf:E06]

**问题 2：每步能否在 3 μs 内完成？** Table 3 报告 FPGA1 electrical system 2.680 μs、communication 0.680 μs；FPGA2 为 2.032/2.112/0.488 μs（electrical/control/communication）；FPGA3、FPGA4 均为 2.224/1.792/0.488 μs。作者说明 communication 已含在 electrical time 中，并认为最大 communication time 占 3 μs 步长的 22.67% 可以接受。[pdf:E05] [pdf:E07] 这些数字支持该案例的 nominal timing closure；论文没有报告测量窗口、分位数、jitter、最坏执行时间、deadline miss count，也没有把 ADC→求解→DAC 的端到端 HIL latency 单独计入。

**问题 3：接口后的波形是否与离线参考相符？** 快动态实验共 4 s：2 s 时 PV/battery 单元有功负载从 3 kW 增至 5 kW；3 s 时 PV unit 1 的 PCC 发生 Phase-C ground fault，0.2 s 后切除。[pdf:E05] 第一事件中，作者报告 Phase-A current 从 15 A 上升到接近 25 A，PV 约输出 5.09 kW，电池从吸收 2 kW 过渡到接近 0 kW；FPGA 曲线与 PSCAD/EMTDC 曲线在图中接近。[pdf:E06] 第二事件中，故障期间 Phase-C voltage 降至 0 V，PV unit 2 的 DC voltage 波动，而 PV/battery 单元 DC voltage 保持稳定。[pdf:E07] [pdf:E08]

作者没有把两种工具的差异掩盖掉，而是列出四个来源：FPGA 控制系统的 32-bit single precision、FPGA 的 constant-impedance switch 与 PSCAD/EMTDC 的 small/large-resistance switch 不同、两侧 irradiance 处理不同，以及用于分区的 Bergeron's line model 自身引入误差。[pdf:E07] 但论文没有进一步把这四类误差分离或量化，所以波形接近只能支持该案例的一致性，不能给出接口误差上界。

**问题 4：较长时间的外部输入能否贯通？** 实验把晴天 6:00-20:00、每 10 min 一个采样点的 irradiance 输入系统，并把有功负载保持在 4 kW。PV 有功随 irradiance 变化，电池有功呈相反趋势，总有功大体保持；作者据此称两种工具结果基本一致并验证内外接口。[pdf:E07] [pdf:E08]

实验真正验证的是：在一个 4-Stratix-V、radial、3 μs、特定 payload 和 Bergeron 分区案例中，接口可以运行，若干瞬态与长时波形和 PSCAD/EMTDC 视觉接近。它没有验证 8/16 卡扩展、loop/chained 拓扑下的实时性、不同步长卡之间的数值误差、链路 BER/重传/拥塞/尾延迟，也没有给出误差范数、统计置信度或 hardware-controller closed-loop 结果。案例中的外部设备是 sensor 与 oscilloscope，不能等同于已经完成控制器闭环 HIL 验证。[pdf:E06] [pdf:E07]

## § 8 — Take-aways

**5 句话版本。**  
1. 论文把多 FPGA 微电网实时仿真的接口问题拆成可重配拓扑、步长同步、内部光纤通信和外部 AD/DA 四部分。  
2. master pulse 加 `Δt_min` 整数倍机制让相同与不同步长的 FPGA 共享时间基准。[pdf:E03] [pdf:E04]  
3. serializer/deserializer、channel selector、dual-clock FIFO 与 2.5 Gbps transceiver 形成内部数据通路，AD/DA 也用 dual-clock FIFO 处理跨时钟域。[pdf:E04] [pdf:E05]  
4. 4-FPGA radial 案例在 3 μs 步长下跑通，并与 PSCAD/EMTDC 展示了接近的瞬态与长时曲线。[pdf:E05] [pdf:E07] [pdf:E08]  
5. 但“4 卡案例可运行”不等于“增加 FPGA 后仍可实时扩展”，因为论文没有测卡数增长时的同步、通信与 deadline。

**3 句话版本。**  
1. 这是一篇完整接口实现论文，而不是新的 EMT 求解算法论文。  
2. 它最有价值的结果是把时间同步、光纤通信、跨时钟域和模拟 I/O 放进同一个 4 卡微电网案例。[pdf:E04] [pdf:E06]  
3. 它最重要的证据缺口是没有把 nominal execution time 升级为可扩展的 worst-case end-to-end deadline 保证。

**1 句话版本。**  
论文证明了一个 4-FPGA、3 μs 微电网实时仿真接口原型可以工作，但没有证明其全局同步与通信在规模增长时仍能守住实时 deadline。

## § 9 — 最脆弱的假设

最脆弱的假设是：每个 step-opening 同步脉冲到来时，所有需要的跨卡边界数据都已经以正确的步号到达，而且这个条件在增加 FPGA、hop 和 payload 后仍能在 deadline 内成立。

如果这个假设失败，slave 仍可能按脉冲启动，却读到旧步数据或等不到新数据；这不是普通性能下降，而是破坏分区 EMT 的因果顺序。论文给出的支持证据只有 4 卡 radial 案例中 0.680/0.488 μs 的通信时间和 3 μs 步长，以及视觉接近的 PSCAD 波形。[pdf:E05] [pdf:E07] 对间接连接，论文自己承认同步要经 slave 转发，并把 master 启动推迟两倍传输延迟，这说明 hop 会进入时间预算。[pdf:E04]

缺失的证据包括：同步脉冲与 payload 的先后约束、跨卡 step ID、全卡 ready/complete acknowledgement、最大而非平均或单次通信延迟、jitter、丢包与 bit error、FIFO backpressure、clock drift、不同拓扑和卡数下的 deadline miss。作者在结论中称设计 “fully extensible”，但现有实验只支持物理接口可扩展的工程可能性，不能支持实时性随规模自动保持。[pdf:E07]

## § 10 — 最小复现实验

一周内不必复现整个微电网，最小实验应直接验证论文最脆弱的接口 claim。

- 使用 2-4 块带 SFP/QSFP 的 FPGA，复现 master step pulse、shared-channel time-division multiplexing、dual-clock FIFO 和论文的 payload：master 每步总发 18 个 64-bit word，每个 slave 回 6 个 64-bit word；步长固定为 3 μs。[pdf:E04] [pdf:E05]
- 每个 payload 加实验用 step counter 与发送/接收 timestamp；注意这是复现测量仪器，不是论文已报告的协议字段。
- 分别测试 direct radial 与一跳 relay，改变本地 clock offset，并运行至少 `10^7` 步。记录 pulse arrival skew、payload complete time、FIFO occupancy、wrong-step read、deadline miss，以及从 ADC sample 到 DAC update 的端到端 latency。
- 支持核心 claim 的最低结果是：所有试验中 wrong-step read 与 deadline miss 均为 0，且最大端到端延迟小于 3 μs；若 relay 或 clock offset 下出现任何错步，或 tail latency 穿越 3 μs，即反驳“仅靠现有同步与接口即可稳定守住该实时步长”。

如果硬件时间允许，再接一个线性 RLC 或简化 PV 端口，比较单卡 golden trace 与多卡 trace 的逐步误差；这样可把协议正确性与数值正确性连接起来，而无需重建论文全部控制系统。

## § 11 — 最强反例设计

最强反例不是让链路彻底断掉，而是构造一种“同步脉冲按时、数据偶尔晚到”的合法压力场景。把 4 卡 radial 改成论文声称支持的 chained topology，让最远端同步经中间 FPGA 转发；同时令各 cut-set payload 在某些步骤发生 fan-out，并注入小幅 clock-frequency offset，使 FIFO 相位缓慢漂移。[pdf:E03] [pdf:E04]

攻击点是 master-pulse 机制没有被论文证明是 collect-and-release barrier：如果某个 slave 在收到 step pulse 时仍缺当前步边界数据，它可能消费旧值而不会立刻停机。实验应逐步增加 card/hop/payload，记录 step ID、数据年龄、deadline miss 和接口能量残差，并在负载跃变与 ground fault 时比较单卡或高精度 reference。[pdf:E05] [pdf:E08]

如果在链路平均吞吐仍低于 2.5 Gbps 的情况下，只因 tail latency 或相位漂移就出现错步、故障暂态偏差或不稳定，那么“带宽足够 + 周期同步”不足以保证多 FPGA EMT 正确性；这会直接击中论文从 4 卡案例外推到更大系统的核心薄弱处。反之，若所有规模与拓扑下都能用明确的最坏界证明数据先于 pulse-ready point 到达，这个反例才被否证。

## § 12 — Follow-up Research Idea

**候选方向：把“时钟同步”重新定义为“带 deadline 的跨分区因果闭合”。本方向未做充分相关工作检索，不声称 novelty。**

（a）未满足的需求是：现有接口只给每块 FPGA 一个共同 step boundary，却没有给每条分区边界一个可检查的 data-age 与 completion contract。随着卡数、hop 与 payload 增长，真正需要保证的是“第 `k` 步使用的所有端口量都来自允许的逻辑时间，并在第 `k` 步 deadline 前完成”。

（b）研究价值在于把“多加 FPGA 可以扩容”的工程判断变成可证伪的实时-数值合同：既约束通信最坏延迟，也约束延迟数据造成的物理残差。这样评价的不只是 raw link speed，而是 EMT step 是否因果闭合。

（c）可借鉴 synchronous-reactive systems、timed dataflow、network calculus 和 time-sensitive networking：离线为每个 cut edge 计算 payload、hop、release time 与 deadline；运行时携带 step index 与 data-age，并在合同被破坏时显式失败，而不是静默使用旧数据。这里的相邻方法只是工具候选，不代表已有工作中不存在同样设计。

（d）第一个证伪实验是复用 §11 的 radial/chained 压力矩阵：如果合同预测“可按 3 μs 运行”但硬件仍出现 wrong-step read 或 deadline miss，或者合同满足却数值能量残差显著增加，则该方向失败。

（e）它与论文的实质区别不是增加一种接口或更快协议，而是改变验收对象：论文同步“卡的开始时刻”，候选方向认证“跨卡端口数据在 deadline 内的逻辑时间与物理一致性”。只有当这一合同能随卡数给出可测的通过/失败边界，规模增长才从愿景变成证据。
