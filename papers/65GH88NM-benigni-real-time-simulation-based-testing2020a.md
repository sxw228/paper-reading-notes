# Real-Time Simulation-Based Testing of Modern Energy Systems: A Review and Discussion

- Zotero key：`65GH88NM`
- 固定语料顺序：`68`
- 作者：Andrea Benigni；Thomas Strasser；Giovanni De Carne；Marco Liserre；Marco Cupelli；Antonello Monti
- 年份与出处：2020，*IEEE Industrial Electronics Magazine*，14(2)
- DOI：`10.1109/MIE.2019.2957996`
- 唯一内容真相：`_source.pdf`
- PDF SHA-256：`e9b6fe97f4532949f17fcda8bfd2a3c9d9961bb0314c1e193f18f038f7856222`
- 文献类型：叙述性综述与讨论，不是提出新求解器并用统一 benchmark 验证的研究论文
- 证据约定：PDF 物理页从文件首页按 1 计数。论文事实、论文转述的既有文献结论和本文采用的图表均绑定可打开的 `[pdf:E..]`；批评、复现与研究方向明确标为本卡推断或候选设计。

## § 1 — 研究问题与重要性

这篇综述处理的不是“怎样把某一个电路算得更快”，而是一个更上层的问题：当能源系统同时包含电、热、气、储能、分布式控制、通信网络、市场和人的参与时，怎样把单个部件测试升级为系统级、跨域、覆盖开发全生命周期的验证。作者认为，现代能源系统的连续动力学与离散事件耦合更强，控制功能更加分布式并依赖通信，因此会出现仅靠孤立部件测试难以暴露的系统涌现行为。[pdf:E01](_evidence/E01-p001-title-and-modern-energy-context.png)

论文的重要判断是：传统上电力域和通信域往往分开设计、分开验证，已有方法又多聚焦 component-level 问题，系统集成缺少 holistic testing 概念；因此，需要把正式分析、软件仿真、real-time simulation、实验室测试和现场试验放回同一条开发链中，而不是把 HIL 当成一台更快的离线仿真器。[pdf:E02](_evidence/E02-p002-validation-concepts-and-review-scope.png) Table 1 给出了这条链的核心分工：分析/软件仿真最适合需求和详细设计，实验室测试最适合实现与原型，real-time simulation/HIL 同时适合实现原型和 deployment/rollout，现场试验则主要服务最终部署。[pdf:E03](_evidence/E03-p003-table1-validation-lifecycle.png)

因此，本文的价值在于建立一张“测试问题 - 时间尺度 - 求解平台 - 硬件接口 - 生命周期阶段”的地图。它不承诺单一工具覆盖全部问题，而是说明：快开关器件需要 submicrosecond 级实时求解，跨地域系统需要处理通信延迟，慢动态大系统需要降阶表示，控制器与功率设备又分别需要 CHIL 和 PHIL。这个分类框架是本文真正的贡献形态。

## § 2 — 前人工作与不足

作者将已有工作分成两层。第一层是 validation concepts：IntelliGrid、smart grid architecture model、model-driven development、ERIGrid holistic test description 和 JRC interoperability testing 已开始形式化用例、架构与测试计划，但针对 system-level question 的结构化验证概念仍不足。[pdf:E02](_evidence/E02-p002-validation-concepts-and-review-scope.png) 第二层是 methods and tools：既有实时仿真综述已经覆盖产品、技术和应用，本文则把近期进展重新组织为 small time-step solver、laboratory remote connection、slow dynamics solver、CHIL、PHIL 及其系统集成关系，而不是再列一份厂商目录。

对 fast dynamics，论文把能够准确表示电力电子系统且步长小于 500 ns 的方法归为 small time-step solver。宽禁带器件带来的高开关频率、强非线性以及内存/总线延迟，使通用 CPU 很难进入小于 1 μs 的实时步长，因而研究转向 CPU/DSP 与 FPGA 混合或纯 FPGA 实现。[pdf:E04](_evidence/E04-p003-small-step-solvers.png) 被综述的 FPGA 文献已经覆盖电机、变换器、非线性变压器、MMC 和器件级非线性；纯 FPGA 方案有文献报告过 40 ns 步长，但资源占用、编程陡峭学习曲线和多 FPGA 接口仍是限制。[pdf:E05](_evidence/E05-p003-fpga-landscape-and-limits.png) 这里的 40 ns 是本文转述参考文献 [22] 的结果，不是作者在本文中重新实验得到的数字。

对 large-scale/distributed dynamics，本地 DRTS 的容量、设备的地域分散和数据保密需求驱动实验室互联；然而 Internet 延迟可能比商业 DRTS 步长大几个数量级，逐步交换不可行且会导致不稳定，需要延迟补偿或改变表示域。[pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png) Dynamic phasor 把窄带振荡信号搬移到接近 0 Hz，只计算慢变包络，再在后处理中移回原频带，因此可以用更长步长处理大系统；代价是它天然适合窄带现象，不能自动保留所有 EMT 高频细节。[pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png)

对 hardware testing，CHIL 用 DRTS 替代受控 plant/grid，让真实控制器通过 I/O 或网络接口闭环运行，优点是成本和风险低、搭建快，但被测对象仍是控制器而不是功率硬件。[pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png) PHIL 则把真实硬件、DRTS、功率放大器和测量系统闭环连接，以避免为每种网况重建物理电网；它解决了“只在一个物理接入点验证硬件、无法验证整体网络”的限制，却引入了放大器、采样、通信和 interface algorithm 的新误差源。[pdf:E08](_evidence/E08-p005-system-integration-and-phil-rationale.png) [pdf:E09](_evidence/E09-p006-phil-actors-and-voltage-interface.png)

## § 3 — 重建作者的思考路径

下面是基于全文结构重建的思考路径，不是作者逐字给出的推理记录。

1. 先从失败模式出发：能源系统已从单域、集中式设备变成 cyberphysical、multidomain system of systems；如果仍按域和部件分开验证，集成后的通信、控制与物理网络耦合就没有负责的测试层。[pdf:E01](_evidence/E01-p001-title-and-modern-energy-context.png) [pdf:E02](_evidence/E02-p002-validation-concepts-and-review-scope.png)
2. 再把验证放入生命周期：早期设计适合分析与软件仿真，真实设备和真实时间约束只能在原型与部署阶段逐步引入，所以 HIL 的角色应是连接 software-only 与 field test，而不是替代其中任一端。[pdf:E03](_evidence/E03-p003-table1-validation-lifecycle.png)
3. 接着按物理时间尺度拆问题：power-electronics switching 需要 small time-step/FPGA；跨地域耦合遇到网络延迟；慢变量大系统则可用 dynamic phasor 牺牲宽带细节来换取规模。[pdf:E04](_evidence/E04-p003-small-step-solvers.png) [pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png)
4. 再按“真实到什么程度”拆实验：真实 controller 加模拟 plant 是 CHIL；真实 power hardware 加模拟 grid 是 PHIL；多个实验室和多域设备组合后，目标才从 component validation 上升为 system integration testing。[pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png) [pdf:E08](_evidence/E08-p005-system-integration-and-phil-rationale.png)
5. 最后承认闭环接口不是透明导线：PHIL 的 voltage-type、ideal current-type 和 modified current-type 拓扑各有稳定性与可实现性约束；software interface、power amplifier、ADC/DAC 和控制带宽共同决定实验是否仍代表目标系统。[pdf:E10](_evidence/E10-p007-fig4-phil-interface-types.png) [pdf:E11](_evidence/E11-p007-current-type-phil-tradeoff.png)

这条路径把“实时”从一个单纯的计算性能指标改写为验证契约：模拟时间必须与墙钟时间同步，同时被测硬件看到的端口变量、延迟和带宽还必须足以代表目标物理系统。

## § 4 — 核心 Intuition

本文的核心 intuition 是：现代能源系统不能靠一次 field test 或一次 software simulation 被整体证明，而要沿开发链逐级替换虚拟部件为真实部件，并保持闭环时间与接口物理量可控。[pdf:E03](_evidence/E03-p003-table1-validation-lifecycle.png) 不同问题的关键瓶颈不同，因此求解器时间尺度、分布式耦合方式、CHIL/PHIL 选择和接口算法必须由测试问题反推。所谓“更真实”的 HIL 只有在模型、延迟、带宽和功率接口组成的误差仍处于可接受范围时才成立。[pdf:E12](_evidence/E12-p007-phil-nonidealities-and-interface-algorithms.png)

## § 5 — 具体方法与完整 Pipeline

这是一篇 review，没有提出一条可直接下载实现的新算法。下面的 pipeline 是对作者分类与比较框架的忠实重建。

1. **定义测试 claim 和生命周期位置。** 输入不是一个模型文件，而是要验证的行为：控制逻辑、保护动作、硬件网侧性能、系统互操作性或部署风险。需求/详细设计优先分析与 software simulation；实现/原型进入 real-time simulation、CHIL 或 PHIL；最终部署再由 demonstration/field test 承担。[pdf:E03](_evidence/E03-p003-table1-validation-lifecycle.png)
2. **选择模型频带与实时求解层。** 高频 switching/nonlinear transient 进入 small time-step/FPGA 路线；窄带慢动态和超大系统可用 dynamic phasor；地域分散的子系统通过网络交换接口量，并显式处理通信延迟，而不是假定每个 EMT 步都能交换。[pdf:E04](_evidence/E04-p003-small-step-solvers.png) [pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png)
3. **选择被测真实对象。** 如果 claim 针对 controller，使用 CHIL：DRTS 模拟 plant/grid，真实控制器交换测量与控制信号。[pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png) 如果 claim 针对 power hardware，使用 PHIL：DRTS 计算电网，power amplifier 把模拟端口量变为真实功率，measurement system 把硬件响应送回模拟器。[pdf:E09](_evidence/E09-p006-phil-actors-and-voltage-interface.png)
4. **选择 PHIL 接口拓扑。** Voltage-type 用放大器复现电压、把 HUT 电流反馈进软件；ideal current-type 用真实电流源复现软件电流；modified current-type 在缺少商用理想电流源时，以 voltage-source amplifier 加高速电流控制器近似电流源。[pdf:E10](_evidence/E10-p007-fig4-phil-interface-types.png)
5. **配置闭环非理想因素。** 显式记录 DRTS/HUT sampling、ADC/DAC、通信延迟、interface controller 带宽、software interface 和 power interface bandwidth/rating。论文比较了 ITM、TFA、TLA、PCD、DIM；它们在实现简单度、稳定性、精度、外部阻抗与拓扑变化能力之间取舍，没有一个无条件最优。[pdf:E12](_evidence/E12-p007-phil-nonidealities-and-interface-algorithms.png) [pdf:E14](_evidence/E14-p008-table2-software-interface-comparison.png)
6. **执行、比较并解释。** 输出至少应包含目标端口变量、时延、闭环稳定性和相对可信 reference 的误差，并把结论限定到已测试的模型频带、功率范围和接口配置。本文列举的设施说明 PHIL 已覆盖从 45 kW modified current-type facility 到 MW/MVA 级 voltage-type facilities，但这些是异构案例，不是统一条件下的横向 benchmark。[pdf:E16](_evidence/E16-p009-phil-applications-and-facilities.png)

以 grid-forming converter 为例：两个 voltage-controlled converters 串联可能形成不稳定闭环，所以作者讨论的路线是 current-type PHIL；若理想 current-source amplifier 不可得，则采用 modified current-type 接口，并在更高 current-controller bandwidth 带来的高频复现能力与潜在失稳之间找折中。[pdf:E11](_evidence/E11-p007-current-type-phil-tradeoff.png) 这个例子说明测试拓扑不是接线细节，而是决定 claim 是否有效的一部分。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有给出新的编号公式、定理或可复现的核心数学推导，因此不存在应当逐式复原的“作者方法公式”。它使用了三个基础关系来组织讨论。

第一，real-time simulation 要求模拟时间步与墙钟时间同步，使模拟一秒对应真实一秒，真实 I/O 才能参与闭环。[pdf:E02](_evidence/E02-p002-validation-concepts-and-review-scope.png) 第二，作者用 sampling theorem 解释跨实验室延迟：若要无混叠表示最高频率为 \(f_{\max}\) 的动态，采样频率至少应满足 \(f_s \ge 2f_{\max}\)；而 Internet 的 tens-of-milliseconds 级延迟相对典型实时步长过大，直接耦合会破坏稳定性。[pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png) 这只是论文中的定性论据，本文没有推导完整的网络化系统稳定边界。

第三，dynamic phasor 的物理直觉是 frequency shift：把以 50/60 Hz 附近为中心的窄带信号搬移到接近 0 Hz，求解其慢变 envelope，再移回原频带，从而允许更长步长。[pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png) 它的成立条件是关注频谱确实窄带；若目标 claim 依赖 switching harmonics、宽带谐振或快速故障沿，这个降阶不能被无条件采用。

PHIL 部分同样没有给出统一闭环传递函数。论文只明确指出，提高 current-controller bandwidth 可以改善高频电流复现，但 aggressive controller 可能使闭环失稳，因此 accuracy 和 stability 必须折中。[pdf:E11](_evidence/E11-p007-current-type-phil-tradeoff.png) 真正可复现的稳定性推导需要被测 HUT、放大器、延迟和 interface algorithm 的具体模型，本文没有提供。

## § 7 — 实验设计与结论

本文没有作者新建的统一实验、ablation 或统计 meta-analysis；其证据是分类框架、比较表和对所引参考文献及若干现有设施的叙述性综合。因而本节按“问题 → 综述如何回答 → 可成立的结论”重建，不能把文献案例数量误当成实验重复数。

- **什么验证工具适合哪个开发阶段？** → 作者用 Table 1 比较分析/软件仿真、实验室测试、real-time simulation/HIL 和 field test。→ 可成立的结论是这些工具互补，real-time simulation/HIL 的优势集中在 implementation/prototyping 与 deployment/rollout，而不是需求阶段的通用最优解。[pdf:E03](_evidence/E03-p003-table1-validation-lifecycle.png)
- **快动态能否实时求解？** → 作者汇总 FPGA/CPU、HLS、多 FPGA 和非线性模型文献。→ 已有文献显示纯 FPGA 曾达到 40 ns 时间步，并能处理器件级或系统级案例；但资源使用和工程门槛仍限制规模与可移植性。[pdf:E05](_evidence/E05-p003-fpga-landscape-and-limits.png)
- **慢动态和地域分布能否接入同一实时实验？** → 作者比较 EMT、static/dynamic phasor 与 laboratory remote connection。→ Dynamic phasor 可用较长步长处理窄带大系统，但网络延迟仍需补偿，且这种表示不证明宽带 EMT fidelity。[pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png) [pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png)
- **真实 power hardware 如何安全接入模拟电网？** → 作者给出三类 PHIL topology，比较 ITM/TFA/TLA/PCD/DIM，并比较 synchronous generator、switching-element amplifier 和 linear amplifier。→ 结论不是“某一接口最好”，而是 topology、software interface、bandwidth、delay、power rating 和 bidirectionality 共同决定 accuracy/stability envelope。[pdf:E10](_evidence/E10-p007-fig4-phil-interface-types.png) [pdf:E14](_evidence/E14-p008-table2-software-interface-comparison.png) [pdf:E15](_evidence/E15-p008-table3-power-interface-comparison.png)
- **这些方法是否已走出概念验证？** → 作者列举 KIT、Fraunhofer、Florida State、Kiel 和 AIT 等设施与应用。→ 可以确认 CHIL/PHIL 已用于 renewable integration、microgrid、drive、grid-forming converter、教学和认证等场景，但由于设备、功率等级、接口和指标不同，本文没有提供跨设施的同条件性能排名。[pdf:E16](_evidence/E16-p009-phil-applications-and-facilities.png) [pdf:E17](_evidence/E17-p010-ait-voltage-phil-facility.png)

证据边界很重要：论文没有报告系统化检索式、纳入/排除准则、publication bias 分析，也没有用统一 benchmark 重测所综述的方法。因此，它强于“给出领域地图和工程取舍”，弱于“证明某类架构在所有条件下优于另一类架构”。

## § 8 — Take-aways

**5 句话。** 现代能源系统验证的核心难题是跨域闭环集成，而不是单一求解器速度。[pdf:E02](_evidence/E02-p002-validation-concepts-and-review-scope.png) Real-time simulation/HIL 应被看作连接软件仿真、实验室原型和现场部署的生命周期工具。[pdf:E03](_evidence/E03-p003-table1-validation-lifecycle.png) FPGA small time-step solver、dynamic phasor 和 distributed laboratory 分别针对快动态、慢动态/大规模和地域分散问题，但彼此不能无损替代。[pdf:E04](_evidence/E04-p003-small-step-solvers.png) [pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png) CHIL 验证 controller，PHIL 验证真实 power hardware 与模拟电网的闭环交互，而 PHIL 的接口本身会改变被测系统。[pdf:E07](_evidence/E07-p005-dynamic-phasor-and-chil.png) [pdf:E12](_evidence/E12-p007-phil-nonidealities-and-interface-algorithms.png) 论文最有用的产物是取舍框架，最缺的是跨厂商、跨设施、可量化的统一 fidelity 与稳定性验收标准。[pdf:E18](_evidence/E18-p011-future-research-boundaries.png)

**3 句话。** 先定义要验证的系统行为和频带，再选 solver、CHIL/PHIL 与接口，而不是先选设备。任何 HIL 结论都必须连同模型、步长、延迟、带宽、功率接口和被测工况一起解释。[pdf:E13](_evidence/E13-p008-power-interface-dynamics.png) 这篇综述证明了方法与设施已经丰富，却没有证明不同方案在统一条件下的相对优越性。

**1 句话。** “实时”只保证时间对齐，只有被测动态在模型与接口的 validity envelope 内时，测试结果才代表目标能源系统。

## § 9 — 最脆弱的假设

最脆弱的假设是：**HIL 闭环中的模拟模型、sampling/ADC/DAC、通信、interface algorithm 和 power amplifier 共同形成的替代系统，仍保留了目标真实系统中与待验证 claim 相关的动力学。** 如果这个替代关系不成立，那么更昂贵、更接近硬件的 PHIL 反而可能提供“看起来真实但验证了错误 plant”的证据。

论文自己给出了这个风险的直接证据。DRTS 与 HUT 的典型 sampling、额外延迟和接口控制会影响 accuracy/stability；software interface 还在简洁性、噪声、外部阻抗、拓扑变化和建模误差之间取舍。[pdf:E12](_evidence/E12-p007-phil-nonidealities-and-interface-algorithms.png) Switching-element amplifier 可到高功率且支持 bidirectional operation，但 bandwidth 只有 few-kilohertz 且有 several-hundred-microseconds 级延迟；linear amplifier 可到 180 kHz 且延迟为 few microseconds，却受功率、反向能量和电压依赖限制。[pdf:E13](_evidence/E13-p008-power-interface-dynamics.png) [pdf:E15](_evidence/E15-p008-table3-power-interface-comparison.png)

作者提供的是 component-wise trade-off 和案例设施，没有给出一个由目标频带/故障场景自动推出“该 PHIL setup 可接受”的统一判据。基于证据的判断是：这不会否定 CHIL/PHIL 的工程价值，但会限制任何跨 setup 外推；只要 validity envelope 未被量化，“通过一次 HIL 测试”不能自动升级为“系统在现场一定安全”。

## § 10 — 最小复现实验

**候选复现实验，不是论文已做实验。** 一周内最值得复现的是第 9 节的闭环 accuracy-stability trade-off，而不是复制完整 multienergy laboratory。

使用一套已有 DRTS、一个 programmable power amplifier 和一个低功率 grid-forming converter HUT，搭建 modified current-type PHIL；同时保留同参数的离线高精度 EMT reference。论文给出了该 topology 的结构与“提高 current-controller bandwidth 有利于高频复现、过于 aggressive 会失稳”的目标 claim。[pdf:E10](_evidence/E10-p007-fig4-phil-interface-types.png) [pdf:E11](_evidence/E11-p007-current-type-phil-tradeoff.png)

实验只扫两个轴：人为插入的闭环 delay，以及 interface current-controller bandwidth。工况包含稳态功率阶跃和一个会激发目标频带的网压扰动；测量 HUT 端口电压/电流相对 EMT reference 的幅值误差、相位误差、settling time、最大振荡幅度及是否失稳。支持 claim 的结果是：存在可重复的中间带宽区间，带宽增加先降低高频误差，随后在 delay 增大时出现振荡或失稳边界；反驳 claim 的结果是：在设备有效范围内误差和稳定性对这两个轴不敏感，或观测变化主要由另一个未建模因素解释。

最小验收不是达到某个预设百分比，而是公开 setup 参数、reference、原始波形和 pass/fail 定义，并在至少两次独立重复中得到同一边界趋势。若没有 PHIL 设备，可先做 pure-software loop-delay emulation 作为预实验，但它只能筛选工况，不能替代功率接口的真实验收。

## § 11 — 最强反例设计

**候选反例。** 构造一个同时包含 wide-bandgap converter switching、弱电网高频谐振、grid-forming control 和远程 supervisory control 的多时间尺度系统。把快速电力电子部分放在 small-step EMT reference 中，把远程子系统通过 tens-of-milliseconds 网络连接；然后让待攻击的 HIL 方案使用 dynamic phasor 远程耦合和 switching-element power amplifier。

这个反例专门把各层的“合理局部近似”叠在一起：dynamic phasor 会滤去窄带包络之外的 switching/harmonic interaction，[pdf:E06](_evidence/E06-p004-remote-delay-and-dynamic-phasor.png) switching-element amplifier 的 few-kilohertz bandwidth 与 several-hundred-microseconds delay 又可能压低高频环路增益，[pdf:E13](_evidence/E13-p008-power-interface-dynamics.png) Internet delay 则改变远程控制相位裕度。若 HIL 中 converter 顺利通过扰动，而 full-band EMT 加经过辨识的 amplifier/network dynamics 后出现可重复的高频失稳，那么“通过”有一个更强的替代解释：不是 controller 鲁棒，而是测试链滤掉了失败机制。

最有力的判定方式是做 paired test：相同 controller、相同工况、相同初始条件，只改变表示域和经过校准的接口动态；提前规定关注频带与 instability criterion。若差异只发生在目标 claim 之外的频率，本反例失败；若差异直接改变 protection/control 的 pass/fail，它就击中了综述框架最脆弱的外推点。

## § 12 — Follow-up Research Idea

在电力电子与电力系统实验研究中，高影响工作通常需要明确的物理机制、可复现实验、跨工况边界、工程可实现性，以及能迁移到不同平台的评价标准。本文已经指出 standardization/harmonization、跨厂商 DRTS 耦合和厂商工具依赖仍未解决。[pdf:E18](_evidence/E18-p011-future-research-boundaries.png)

**候选研究想法：为 HIL 建立“claim-conditioned fidelity budget 与 validity envelope”。** 它不是再做一个更快 solver，而是把每个待验证 claim 先变成所需频带、允许相位/幅值误差、事件时间分辨率和能量交换范围，再把误差预算分配到 model reduction、solver step、ADC/DAC、network delay、interface algorithm 和 power amplifier。测试前由预算判断 setup 是否有资格验证该 claim；测试后只在已证明的 envelope 内出具结论。

（a）驱动需求是当前 setup 的“实时运行”与“物理代表性”之间缺少可审计桥梁，同一 pass/fail 很难跨实验室复用。（b）如果能让 CHIL/PHIL 结果跨厂商、跨功率等级、跨表示域比较，它会同时提高工程可信度和标准化价值。（c）可借鉴 robust control 的 structured uncertainty/IQC、networked control 的 delay margin，以及 measurement uncertainty 的 traceability；这些工具可把接口非理想性从经验调参变成显式 uncertainty set。（d）第一个证伪实验是在至少两种 DRTS 与两类 amplifier 上，用预注册的 envelope 预测同一组 grid-forming converter 工况 pass/fail；若预测边界不能区分可靠与失真结果，想法即失败。（e）它与本文的实质区别是：本文提供 taxonomy 和定性 trade-off，本想法要求生成 machine-checkable 的测试资格与结论边界。

相关工作在本任务中没有做超出本文参考文献的充分检索，因此这只是从论文证据推出的候选方向，不声称 novelty。
