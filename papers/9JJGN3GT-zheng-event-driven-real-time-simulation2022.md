# An Event-Driven Real-Time Simulation for Power Electronics Systems Based on Discrete Hybrid Time-Step Algorithm

- Zotero key：`9JJGN3GT`
- corpus order：`35`
- 作者：Jialin Zheng；Zhengming Zhao；Yangbin Zeng；Bochen Shi；Zhujun Yu
- 出处：IEEE Transactions on Industrial Electronics, 70(5), 4809–4819
- DOI：`10.1109/TIE.2022.3187594`
- canonical PDF：`_source.pdf`
- PDF SHA-256：`d70e2ba75ed952e8f588d7e5e0ae1a8262ef78a5ac361ecc84cc361344972128`
- 证据说明：`[pdf:E..]` 指向本目录 `_evidence/` 中的 PDF 页面上下文图；物理页从 PDF 首页按 1 开始。论文原文、本文推断与候选研究判断在正文中分开标注。

| 证据 ID | PDF 物理页 | 论文位置 | 上下文图 |
|---|---:|---|---|
| E01 | 1 | 摘要、Introduction 开头 | [`E01-p001-abstract-problem.png`](./_evidence/E01-p001-abstract-problem.png) |
| E02 | 2 | Introduction 后半、SCED 概念 | [`E02-p002-prior-work-framework.png`](./_evidence/E02-p002-prior-work-framework.png) |
| E03 | 3 | Fig. 1–2、SCED 事件调度 | [`E03-p003-sced-timing.png`](./_evidence/E03-p003-sced-timing.png) |
| E04 | 4 | Fig. 3、DHT/LFTS/EDVS | [`E04-p004-dht-concept.png`](./_evidence/E04-p004-dht-concept.png) |
| E05 | 5 | Eq. (1)–(6)、Fig. 4 | [`E05-p005-equations-flow.png`](./_evidence/E05-p005-equations-flow.png) |
| E06 | 6 | Fig. 5、Table I、平台与模型比较 | [`E06-p006-platform-params-methods.png`](./_evidence/E06-p006-platform-params-methods.png) |
| E07 | 7 | Fig. 6–8、Table II、实验平台 | [`E07-p007-topology-comparison-cost.png`](./_evidence/E07-p007-topology-comparison-cost.png) |
| E08 | 8 | Fig. 9–10、Table III、效率分析 | [`E08-p008-results-efficiency.png`](./_evidence/E08-p008-results-efficiency.png) |
| E09 | 9 | Fig. 11–13、Limitations | [`E09-p009-limitations-runtime.png`](./_evidence/E09-p009-limitations-runtime.png) |
| E10 | 10 | Fig. 14、Conclusion | [`E10-p010-promotion-conclusion.png`](./_evidence/E10-p010-promotion-conclusion.png) |

## § 1 — 研究问题与重要性

论文处理的是一个很具体的实时 HIL 矛盾：高开关频率 power electronics system 要准确复现开关时刻，传统方案通常把采样步长压到控制周期的 `1/10` 以下；例如 20 kHz 控制载波对应 50 μs 周期，文中据此给出小于 5 μs 的采样间隔要求。更小步长既增加计算量，又常迫使系统采用昂贵 FPGA 和简化开关模型。[pdf:E01]

这里真正稀缺的不是“更快的积分器”，而是每个控制周期内哪些时刻必须计算。作者提出 CPU-based event-driven real-time（EDRT）框架：先由 synchronous-cycle event detection（SCED）从控制器参考波与计算载波中预知本周期的开关事件，再由 discrete hybrid time-step（DHT）只在事件与误差控制真正需要的位置推进状态。作者的核心 claim 是：算法改变可以替代一部分硬件堆叠，同时保留 ideal switch model 的精度。[pdf:E01][pdf:E02][pdf:E10]

这个问题重要，因为 HIL 的目的不是单纯加速离线仿真，而是在确定的 wall-clock deadline 内让真实控制器“感觉”自己接在真实功率级上。若开关边沿晚一个采样点，误差会进入拓扑切换时刻、暂态波形乃至闭环稳定性；若为消除误差无条件提高采样率，又会把平台成本和开发门槛推向 FPGA。[pdf:E01][pdf:E03]

## § 2 — 前人工作与不足

论文把既有路线分成两类。第一类是高频采样加小固定步长：它把 PWM 边沿当成采样后才知道的被动事件，因此实际开关与仿真采用开关之间存在不可避免的量化延迟；提高采样率只能缩小、不能从机制上消除该延迟，而且在一个控制周期内还可能漏掉多次切换。[pdf:E02][pdf:E03]

第二类是为实时性而采用 L/C-associated discrete circuit（L/C-ADC）开关模型。它用附加 L/C 元件换取常系数系统矩阵，避免每步重构矩阵，但会在换相时产生虚拟电压/电流尖峰和虚拟损耗。已有工作通过更小步长、阻尼电阻、补偿电流源或 generalized small-step model 缓和问题；论文指出，这些方法仍需要额外计算或历史电流源修正，没有同时消除采样延迟、模型误差与硬件成本。[pdf:E01][pdf:E02]

作者不是在证明 FPGA 不必要，而是在提出另一条约束组合：当控制器采用规则采样 PWM、调制参考在周期开始可获得、开关事件可由参考与载波重建时，CPU 可以把控制周期作为外层交互步长，把少量真实事件作为内层求解边界。[pdf:E03][pdf:E04]

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为四步。第一，观察到真实数字控制器本来就在控制周期边界采样，并用该次采样计算下一周期的 modulation signal；HIL 若仍以独立高频时钟“碰运气”捕捉 PWM，会人为引入真实控制链中不存在的边沿量化。[pdf:E02][pdf:E03]

第二，PWM 并非任意模拟波形，而是参考波与载波比较的确定结果。只要在周期开始取得参考值，就可以重放 PWM generator 的规则，直接计算本周期所有边沿时刻和边沿后的开关状态。于是“采得更密”可被改写为“只算真正发生的事件”。[pdf:E03]

第三，控制器只在控制周期边界收发一次数据，因此实时性的硬 deadline 是外层周期，而不是要求内部积分器每一步都固定等长。作者据此把外层 large fixed time-step solver（LFTS）用于 I/O，同一周期内用 event-driven variable-step solver（EDVS）沿事件分段积分。[pdf:E04]

第四，为避免 variable-step solver 本身太慢，作者利用开关事件之间电路拓扑固定这一事实，将系统视作分段 linear time-invariant state-space model，以 Taylor 展开和递推导数同时调节阶数与步长。这样，事件调度解决“何时换拓扑”，局部误差估计解决“事件之间算多少点”。[pdf:E05]

## § 4 — 核心 Intuition

核心 intuition 是：高开关频率不等于每个微小时刻都包含新信息，真正改变动力学的是有限个开关事件。若能在控制周期开始就准确知道这些事件，就可把计算点放在事件和误差需要的位置，而不是用高频固定采样网格覆盖整个周期。[pdf:E03][pdf:E04]

因此，SCED 把“边沿检测”从事后采样变成事前调度，DHT 再把“实时步长”拆成对外固定、对内可变；二者缺一不可。[pdf:E04]

## § 5 — 具体方法与完整 Pipeline

以论文的 50 kVA power electronic transformer（PET）为例，它包含三电平三相整流器、dual active bridge（DAB）和单相逆变器，共 24 个开关；DAB 的开关频率为 20 kHz。EDRT 运行在 Intel i7-10700 PC 的 RT Linux 上，通过 PCIe 与 Zynq real controller 通信。[pdf:E05][pdf:E06][pdf:E07]

一个 50 μs DAB 控制周期的 pipeline 是：

1. 周期开始时，CPU-based simulator 从真实控制器取得本周期的 modulation reference，并取得当前仿真状态；控制器不需要在周期内反复传输高频 PWM 样本。[pdf:E03][pdf:E04]
2. SCED 用与真实 PWM generator 相同的 reference-carrier 比较逻辑，计算本周期内每个开关事件的时间与事件后的状态；这些事件成为 EDVS 的强制分段点。[pdf:E03]
3. LFTS 把整个控制周期作为一次对外 I/O deadline。其内部，EDVS 从当前时刻走向最近事件；在拓扑不变的区间内，根据状态导数的增量判断数值阶数和步长。[pdf:E04][pdf:E05]
4. 到达开关事件时，求解器切换对应的 state-space coefficient matrices，再对下一事件区间重复计算。ideal switch model 因而不必为固定系统矩阵而引入 L/C-ADC 的附加元件。[pdf:E05][pdf:E06]
5. 周期结束前输出新的电压、电流采样值给真实控制器，进入下一个控制周期。论文报告 SCED 约耗时 1–2 μs、DHT 约耗时 23–29 μs，合计 24–31 μs，可放入 50 μs 周期。[pdf:E09]

输入是控制器 reference、当前 state 和电路参数；中间产物是按时间排序的开关事件与自适应积分节点；输出是下个控制边界的 state/output 与反馈采样值。论文没有给出完整源码、误差容限、最高阶 `q_max` 或全部控制器参数，因此可以理解其机制，但不能仅凭 PDF 做 byte-for-byte 的实现复现。[pdf:E05][pdf:E06]

## § 6 — 核心数学推导（无形式化数学则跳过）

在相邻事件 \(t_k<t\le t_{k+1}\) 内拓扑不变，作者把 PES 写成

\[
\dot{x}(t)=A_kx(t)+B_ku(t),\qquad
y(t)=C_kx(t)+D_ku(t).
\]

\(x\) 是状态向量，\(u\) 是显式输入，\(y\) 是输出；\(A_k,B_k,C_k,D_k\) 由当前拓扑和元件参数决定。物理意义是：开关事件负责改变矩阵，事件之间则是一个可微的 LTI 区间。[pdf:E05]

对下一个时刻作 \(p\) 阶 Taylor 展开：

\[
x_{k+1}=x_k+\sum_{i=1}^{p}\frac{x_k^{(i)}}{i!}\Delta t_k^i+R_n.
\]

由于区间内矩阵固定，各阶导数可递推为

\[
x^{(i)}(t)=A_kx^{(i-1)}(t)+B_ku^{(i-1)}(t),\quad i\ge1.
\]

这一步的 intuition 是：不必每次调用通用 nonlinear solver；只需沿固定拓扑的线性递推生成 Taylor 系数。[pdf:E05]

下一阶项近似局部截断误差：

\[
\epsilon_k\approx \frac{x_k^{(p+1)}}{(p+1)!}\Delta t_k^{p+1},
\qquad
\Delta_i x_k=\frac{x_k^{(i)}}{i!}\Delta t_k^i.
\]

算法逐状态检查 \(\Delta_i x_k\)：若当前阶数不能满足 accuracy requirement，就提高阶数或缩短步长；若满足，则选取可接受的阶数/步长，但阶数不超过 \(q_{\max}\)。SCED 给出的最近事件又为 \(\Delta t_k\) 设置上界，防止一次积分跨过拓扑变化。[pdf:E05]

推导成立的关键条件是：事件间模型确实可视为 LTI、输入 \(u(t)\) 的所需导数可获得、事件时间已知，而且误差判据对所有状态都成立。论文给出公式和流程，但没有给出全局稳定性证明、误差容限数值或事件时间误差如何传播到闭环误差的界。[pdf:E05]

## § 7 — 实验设计与结论

**问题 1：ideal model 的 EDRT 是否比 L/C-ADC 实时模型更忠实？** 作者在同一 PET 上比较 PLECS offline 的 DOPRI+ideal model、commercial RT 的 1 μs fixed-step+L/C-ADC，以及 EDRT 的 DHT+ideal model。Fig. 7 中 commercial RT 波形在 DAB 换相处出现明显 transient 和虚拟功率损耗，而 EDRT 与 PLECS 曲线接近；这支持“避免 L/C-ADC 伪暂态”，但图中没有给出独立的定量波形误差统计。[pdf:E06][pdf:E07]

**问题 2：EDRT 能否逼近真实硬件暂态？** 作者让同一 PET controller 先接 EDRT，再部署到实体 50 kVA PET，比较 low-voltage ride-through 下的输入电压、电流、DAB 输出和整流器输出。Fig. 9–10 显示主要暂态趋势和波形接近；作者还发现模拟器未包含 controller sampling delay 会造成局部差异，补入该 delay 后更接近实验。[pdf:E07][pdf:E08][pdf:E09] 这证明了该案例的可用性，但不是跨拓扑、跨控制器或统计重复实验。

**问题 3：算法是否更高效？** Table III 报告 EDRT-CPU 的 relative error 为 \(3.49\times10^{-7}\)、计算点 \(1.32\times10^6\)、计算时间 2.36 s；PLECS-CPU 分别为 \(4.64\times10^{-7}\)、\(1.63\times10^6\)、24.83 s。commercial RT-CPU 和 FPGA 的 relative error 均为 \(5\times10^{-3}\)，计算点均为 \(1\times10^7\)，其中 FPGA 完成时间为 4.9 s。[pdf:E08]

这里必须保留论文内部不一致：Table III 的 2.36/24.83 约为 `1/10.5`，而不是摘要及正文声称的 `1/36`；\(1.32/1.63\) 表示计算点约减少 `19%`，而不是正文声称的 `33%`。[pdf:E01][pdf:E08] 因而“EDRT 在该表中比 PLECS 快且误差同量级”有直接证据，“快 36 倍、点数少 33%”则没有被同页表格数字闭合。

**问题 4：能否满足真正的 wall-clock deadline？** Fig. 13 给出 SCED 1–2 μs、DHT 23–29 μs、总计 24–31 μs，作者据此判断可满足 50 μs 控制周期。PCIe 通信延迟至少 10 μs，使通信步长约受限于 20 μs，因此作者给出的 CPU EDRT 最大开关频率为 50 kHz。[pdf:E09] 这是一次平台测时结果，不是 worst-case execution time 的形式化保证。

## § 8 — Take-aways

**5 句话。** 论文把高频 PWM 的边沿从“高频采样后发现”改成“由 reference 与 carrier 预先调度”。[pdf:E03] 它把实时交互周期与内部积分步长解耦，让外层固定 deadline 内部使用 event-driven variable-step/variable-order integration。[pdf:E04][pdf:E05] 这样可以在 CPU 上使用 ideal switch model，避免 L/C-ADC 的虚拟尖峰与损耗。[pdf:E06][pdf:E07] 单个 50 kVA、24-switch PET 案例显示 EDRT 波形接近实验，且平台测得 24–31 μs 的算法总耗时可容纳于 50 μs 周期。[pdf:E07][pdf:E09] 但事件可预测性、控制器采样链未被直接测试、50 kHz 通信上限以及效率数字内部不一致，限制了结论的外推。[pdf:E08][pdf:E09]

**3 句话。** EDRT 的贡献不是更快地扫过固定网格，而是只在真正改变拓扑的事件与误差要求处计算。[pdf:E03][pdf:E05] SCED+DHT 在一个 PET prototype 上把 CPU 实时性、ideal model 和真实 controller HIL 组合起来。[pdf:E06][pdf:E07] 其最强结果是“机制与原型可行”，不是“所有高频 PES 都能获得论文宣称的固定倍数加速”。[pdf:E08][pdf:E09]

**1 句话。** 如果 PWM 事件能够在周期开始被忠实重建，就可用事件时间换掉大量固定采样点；如果不能，整个精度优势会从源头失效。[pdf:E03][pdf:E09]

## § 9 — 最脆弱的假设

最脆弱的假设是：**真实功率级采用的全部有效开关事件，都能由周期开始获得的 controller reference 与 simulated carrier 唯一、准确地重建。** SCED 的时间优势完全来自这一点；DHT 又把这些事件当作拓扑切换的硬边界，所以事件漏报、错序或时间偏差会让求解器在错误的矩阵 \(A_k,B_k,C_k,D_k\) 上积分。[pdf:E03][pdf:E05]

这个假设在 dead-time、driver propagation delay、保护/封锁、异步故障、饱和、PWM update jitter、外设采样链与 control code 不一致时可能失效。论文自己承认 all-digital interface 不能直接测试 controller sampling 部分，必须在 simulator 中人为加入 sampling delay；同时 PCIe 通信带来至少 10 μs 延迟和约 50 kHz 的开关频率上限。[pdf:E09]

论文提供的正面证据是规则采样 PWM 的 event scheduler 图解，以及 Zynq controller+PET 案例中加入 delay 后的波形匹配。[pdf:E03][pdf:E09] 缺少的证据是：实际 gate edge 的 timestamp 与 SCED 预测值的逐边沿比较、含 dead-time/保护事件的验证、事件时间误差对状态误差与闭环稳定性的上界。因此这是“在所示控制结构中得到支持的工程假设”，不是已普遍证明的性质。

## § 10 — 最小复现实验

一周内可复现最小而关键的 claim：“事件调度加 DHT 能在相同 waveform error 下减少计算，而不是靠改变物理模型取得表面加速。”

- 数据与模型：按 Table I 取 DAB 的 350 V 输出、9.4 mF 输出电容、变比 2、34.04 μH 漏感、50 mH 励磁电感和 20 kHz 开关频率；只实现 DAB，而不是整套 PET。[pdf:E06]
- 实现：建立 ideal-switch state-space reference model；一条路线用 0.1 μs fixed step 作为数值参考，另一条路线实现 reference-carrier event scheduler，并用 Eq. (1)–(6) 的 Taylor variable-order integrator 在事件间推进。[pdf:E03][pdf:E05]
- 工况：稳态 20 个周期后对 phase-shift command 做一步变化；另加一组已知 dead-time 或 ±0.5 μs edge jitter，用于检验最脆弱假设。
- 测量：逐边沿 timestamp error、输出电压/电流的 normalized RMS error 与峰值误差、计算点数、每周期 wall-clock time、deadline miss 数；同一 CPU、同一 compiler 和同一模型执行至少 1000 个周期。
- 支持标准：无 jitter 时所有 event timestamp 与 reference 一致，EDRT 的 RMS error 不高于 \(10^{-5}\)，且 99.9% 周期在 50 μs 内完成，同时计算点显著少于 fixed-step。
- 反驳标准：即使事件时间正确也不能同时满足误差与 deadline，或加入现实 dead-time/jitter 后 SCED 的状态误差相对 fixed-step 明显放大。

该实验只复现算法机制，不声称复现论文完整结果；PDF 没有给出完整 control code、容差、\(q_{\max}\) 和源码，故无法把论文 Table III 的全部数字作为一周复现的严格验收值。[pdf:E05][pdf:E08]

## § 11 — 最强反例设计

最强反例不是换一台更慢的 CPU，而是构造“reference 合法、真实 gate event 却不等于 reference-carrier 交点”的闭环工况。具体做法是在同一 DAB 上加入 driver dead-time、随机 propagation jitter 和一次过流保护封锁，用逻辑分析仪记录真实 gate edges；SCED 仍只接收 controller reference，并将预测事件送入 DHT。[pdf:E03][pdf:E07]

然后比较三条轨迹：实际硬件、基于实际 gate timestamp 的 event-driven solver、基于 SCED 预测 timestamp 的论文方案。如果第二条持续贴近硬件而第三条在保护触发或 dead-time 累积后出现相位漂移、功率偏差或闭环振荡，就排除了“积分器不够准”这一替代解释，直接把失败定位到论文最关键的 event observability 假设。

若反例成立，它不会否定 DHT 作为已知事件求解器的价值，但会否定“通过 controller reference 就能消除采样延迟并普适覆盖高频 HIL”的强表述。论文对 sampling part 无法直接测试的承认，使该反例具有现实入口。[pdf:E09]

## § 12 — Follow-up Research Idea

在 power electronics real-time simulation 领域，高影响工作通常不仅需要算法平均更快，还要证明 deadline 确定性、暂态保真度、可实现 I/O 链和跨工况稳定性。基于第 9 节，候选方向是把问题从“由 reference 预测确定事件”改写为**带事件时间不确定性的可观测 hybrid HIL**：求解器接收低成本 gate-edge timestamp stream，并把测量迟延、dead-time 和漏事件表示成有界 uncertainty，而不是假定事件表在周期开始已完全确定。

（a）未满足需求：现方案不能直接测试 controller sampling/driver chain，也不能自然容纳异步保护事件。[pdf:E09]  
（b）研究价值：如果能在有界事件迟延下同时给出 state-error envelope 与 worst-case deadline，就把“某一 prototype 跑得过来”提升为可审计的实时保真保证。  
（c）相邻工具：可借鉴 hybrid systems reachability、networked control 的 timestamp/latency calculus，以及 digital-twin 中的 online state correction。  
（d）首个证伪实验：在 20 kHz DAB 上系统扫描 dead-time、jitter 和异步保护频率；若 uncertainty-aware solver 的误差包络不能覆盖实测轨迹，或 deadline miss 超过预设阈值，该方向即被否证。  
（e）实质区别：目标不再是“预先算准唯一事件序列”，而是“在事件观测不完整时仍给出可验证的轨迹集合与实时保证”，改变了问题定义，而非只给 SCED 增加一个补偿模块。

这是基于本文证据提出的候选研究想法；本任务没有检索相关全文，不能据此声称 novelty。
