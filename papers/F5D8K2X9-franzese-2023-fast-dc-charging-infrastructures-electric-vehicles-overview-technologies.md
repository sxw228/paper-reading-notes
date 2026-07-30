# Fast DC Charging Infrastructures for Electric Vehicles: Overview of Technologies, Standards, and Challenges

作者：Pasquale Franzese；Dhruvi Dhairya Patel；Ahmed A. S. Mohamed；Diego Iannuzzi；Babak Fahimi；Massimo Risso；John M. Miller  
出处：IEEE Transactions on Transportation Electrification, Vol. 9, No. 3  
年份：2023  
DOI：10.1109/TTE.2023.3239224  
Zotero key：F5D8K2X9  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这不是一篇提出新型 converter 或新控制器的研究论文，而是一篇面向 fast DC charging infrastructure 的跨层综述。作者要回答的问题是：面对 ultrafast charging station（UFCS）这个同时牵涉配电网、microgrid、power converter、接口标准、可靠性和数据治理的系统，设计者应如何把供电条件、车辆需求和运营约束翻译成一条可实施的技术选择链。摘要明确说，文章比较四类 active-front-end AC-DC converter、三类隔离 DC-DC converter 和两种控制架构，并把这些选择与供电电压、smart-grid 类型和功率流方向关联起来；其目标是把充电站设计者的需求与商业市场偏好接上。[pdf:E01]（PDF 物理页 1，Abstract）

问题之所以重要，首先是“快”会把一个交通服务问题放大成电力系统问题。论文按当时标准把 Mode 4 视为功率超过 50 kW 的 DC charging；同时也提醒，产业实践在 2023 年已更倾向把高于约 120 kW 的充电视作 ultrafast，而且这个门槛会继续变化。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II-A）在相同充电功率下，较低电池电压意味着更高电流、线缆与 converter 损耗、导体尺寸和冷却需求；论文给出的当时典型量级是中小型车辆最高约 400 V、重型或大型车辆名义上约 800 V。[pdf:E03]（PDF 物理页 3，Section II-A，Fig. 3 左侧相邻正文）因此，车辆侧的一次电压选择会沿着电流、热、绝缘、变换级和配电接入一路传导。

其次，UFCS 不是普通可忽略负载。论文将其称为 microgrid 中的“energy-greedy load”，并指出不协调充电可能引起 transformer 或供电设备过载、损耗、power-quality 问题、frequency instability、harmonics injection 乃至 voltage collapse。[pdf:E03]（PDF 物理页 3，Section II-C）这使得“选哪种 converter”不能脱离“接在哪级电网、是否有 BESS/RES、能否协调功率、如何满足接口与安全标准”来回答。

## § 2 — 前人工作与不足

论文所处理的各个子问题在此前都有人研究：配电网文献分析了 EV penetration 对电压、损耗和负荷峰值的影响；microgrid 文献研究了 peak shaving、load shifting、V2G 与储能协调；power electronics 文献分别讨论了 AFE、NPC、SAB、LLC、DAB、SST 和 partial power processing；标准体系规定了 charging mode、连接器、通信、保护和互操作；reliability 文献则提供 RBS、FMEA、RCA、器件寿命与 BESS 故障诊断。论文在物理页 5 直接指出，真正仍开放的问题是：面对 RES、storage、EV charger 与 grid 组成的系统，什么 architecture 与 control method 能在 cost 和 performance 上最实用，而答案需要对备选方案的 cost、efficiency 与 reliability 做定量比较。[pdf:E04]（PDF 物理页 5，Section II-E 至 III-A）

此前工作的不足主要不是“没有某个元件”，而是知识被分散在不同层级和不同评价口径中。microgrid 比较侧重结构与能量流，converter 文献侧重器件数、THD、bidirectionality、power factor、ZVS、损耗或控制复杂度，标准关注安全与 interoperability，可靠性分析又依赖具体 use case。Table I 把 AC、DC 和 hybrid microgrid 的优缺点并列，但这些描述仍是类别级判断。[pdf:E07]（PDF 物理页 8，Table I 与 Section III-C）Table II 和 Fig. 10 进一步把 grid-connection topology 与 converter 选择相配，并以 radar diagram 汇总性能维度；作者同时明确警告 Fig. 10 不是最终排名，因为许多性能依赖工作条件，正确的 conversion chain 也取决于许多因素。[pdf:E10]（PDF 物理页 11，Table II 与 Fig. 10）所以这篇综述的价值是“建立共同地图”，不是证明某一结构普遍最优。

还要区分证据强度：文中大量句子是在转述被引论文的结果，本卡把它们视为“论文对相关文献的整理”，而不是对那些原始实验的独立复核。本文自身没有统一数据集、统一硬件平台或统一工况下的 head-to-head experiment；因此不能把文献汇总后的 radar 形状当作同一实验室、同一边界条件下的性能测量。

## § 3 — 重建作者的思考路径

以下是基于论文结构的合理重建，不是作者明说的逐步发明史。

第一步，从充电服务目标反推电气边界。充电时间缩短会提高功率；在车辆电压受限时，这意味着更高电流、热和导体成本；提高车辆电压又把问题转化为绝缘与 step-up/step-down converter 的选择。[pdf:E02]（PDF 物理页 2，Section II-A）[pdf:E03]（PDF 物理页 3，Section II-A）

第二步，把 UFCS 放回配电网。若 MV 接入能直接取得所需功率，就要承担 MV cabinet、transformer、保护与维护成本；若 LV 接入功率不足，就需要 BESS/RES 进行 local leveling。多 slot 又引入共享功率、排队、资源管理以及 slot 之间的 galvanic isolation。[pdf:E04]（PDF 物理页 5，Section II-E、II-F 与 III-A）

第三步，把系统拆成两个可组合的选择面：grid/microgrid architecture 与 conversion chain。前者在 MV/LV 接入和 AC/DC/hybrid bus 之间选，后者在 AC-DC front end 与 isolated DC-DC 之间选。Fig. 4 给出四类 grid connection，Fig. 5 给出三类 microgrid；这一步建立了系统级“骨架”。[pdf:E05]（PDF 物理页 6，Fig. 4）[pdf:E06]（PDF 物理页 7，Fig. 5）

第四步，再把控制、标准和可靠性作为不能事后附加的约束。AFE 的 voltage/current control、DAB 的 phase-shift power control、EVSE 与 BMS 的 CCC/CVC 请求、连接器与通信协议、每个 slot 的保护以及不同 operation mode 下的 reliability block 都会改变一个 topology 是否实际可用。[pdf:E08]（PDF 物理页 9，Fig. 7 与相邻正文）[pdf:E09]（PDF 物理页 10，Figs. 8–9 与相邻正文）因此作者最后不是给出单一“最佳 charger”，而是给出按条件筛选方案的 matching table 与多维 benchmark。

## § 4 — 核心 Intuition

UFCS 不是一个孤立的高功率 converter，而是一条从 grid boundary、microgrid、conversion chain、vehicle interface、safety 到 operation data 的约束传播链。任何局部更优的器件或拓扑，只有在电压等级、功率流、隔离、控制、标准和 reliability use case 同时成立时，才是系统层面的可用选择。本文的核心机制是把这些原本分散的判断放进同一个条件化设计框架，而不是宣称存在无条件最优解。[pdf:E10]（PDF 物理页 11，Table II、Fig. 10 与作者对“非最终比较”的说明）

## § 5 — 具体方法与完整 Pipeline

这篇综述给出的不是可直接运行的算法，而是一条设计审查 pipeline。用“建设一个多 slot、需要快速充电且可能接入 BESS 的站点”作为例子，可以按以下顺序走：

1. **固定外部边界。** 先确定 grid 是 LV 还是 MV、允许功率、车辆电压范围、slot 数量、是否需要 V2G、是否已有 MV/LV substation。论文自己的工作定义把三相 400 V 且小于 100 kW 作为 LV，把高于 1 kV 且高于 100 kW 作为 MV；这是本文用于分类的边界，不应外推成全球统一定义。[pdf:E04]（PDF 物理页 5，Section III-A）
2. **选择 grid-connection architecture。** Fig. 4 的四种骨架分别是：MV/LV LFT 后接 LV AC-DC 与 LV DC-DC；MV/MV AC-DC 后接 MV/LV DC-DC；MV/LV AC-DC 后接 LV DC-DC；以及 LV grid 配合 BESS/RES。前两类减少或重构笨重的 line-frequency transformer，最后一类用本地 storage/generation 补足 LV grid 供电缺口。[pdf:E05]（PDF 物理页 6，Fig. 4 与 Section III-A）
3. **选择 microgrid bus。** AC microgrid 标准成熟、易变压和远距离扩展，但 DC load 要重复 AC-DC conversion；DC microgrid 利于 PV、BESS 与 EV 的直接能量交换，减少 reactive-power 相关损耗，但 protection 更复杂；hybrid microgrid 用 interlinking converter 在 AC 与 DC 两侧交换功率，却增加层级控制与协议问题。[pdf:E06]（PDF 物理页 7，Fig. 5 与 Section III-B）Table I 将这些优缺点集中列出。[pdf:E07]（PDF 物理页 8，Table I）
4. **选择 AC-DC front end。** Passive diode bridge 成本低、无需控制，但输出调节与功率质量能力有限；buck-type unidirectional PWM 适合需要较低可调 DC voltage 的单向场景；AFE 能双向流动、调节 power factor 并产生低谐波输入电流；NPC 用更多器件换取较低器件 voltage rating 与 switching loss。[pdf:E07]（PDF 物理页 8，Fig. 6 与 Section III-C-1）
5. **选择 DC-DC stage 与隔离位置。** 多 slot 场景中，论文强调隔离 DC-DC 用于 charger 之间的 decoupling。SAB 适合单向流但存在 turn-off 与 diode loss；LLC 通过 frequency control 实现软开关，但宽输出电压范围不利；DAB 适合 bidirectional power flow，利用 transformer leakage inductance 与 primary/secondary voltage phase shift 调功。[pdf:E09]（PDF 物理页 10，Figs. 8–9 与 Section III-C-2）
6. **配置控制链。** AFE 的经典结构用 SVM 和 d/q-axis PI current control，并通过 \(V_{\mathrm{ref}}\) 或 \(I_{\mathrm{ref}}\) 切换 controlled-voltage/controlled-current mode。[pdf:E08]（PDF 物理页 9，Fig. 7）EV 侧则由 vehicle BMS/VCCF 请求 CCC 或 CVC，EVSE 跟随 current/voltage command；不同 connector family 使用 CAN 或 PLC 等不同高层通信方式，并受动态 tolerance、slew rate 与 ripple 限制。[pdf:E13]（PDF 物理页 14，Sections IV-C、IV-D）
7. **逐项过 standards gate。** SGAM 视角把 vehicle、EVSE、CPO、EMSP 和 grid information service 放进同一 interoperability architecture；IEC 61851 和 SAE J3072 等文献负责 Mode 4 的 protection、voltage/current、连接与运行要求。论文列出的 IEC 61851 条件包括 AC grid 侧不高于 1000 V、额定电流不高于 250 A，以及 vehicle DC 侧不高于 1500 V、名义电流不高于 400 A；这些是论文所引用标准版本的报告值，不代表本卡对 2026 年标准状态的更新确认。[pdf:E11]（PDF 物理页 12，Fig. 11 与 Section IV-B）
8. **按 operation mode 做 reliability，而不是只看物理原理图。** Fig. 12 的示例站通过开关重构两个 DC-DC 输出，可在低电压时服务两个 vehicle，也可串联服务高电压 vehicle。[pdf:E12]（PDF 物理页 13，Fig. 12）RBS 会因为“单车/双车、低压/高压、grid/BESS 是否可用”而改变串并联关系，所以同一个物理 topology 会有多个 reliability function。[pdf:E14]（PDF 物理页 15，Section V-B）[pdf:E15]（PDF 物理页 16，Fig. 13）
9. **把运行数据与 cyber risk 纳入 facility management。** 论文把 charging time、power 等数据送往 centralized cloud platform，用于 renewable activation、energy-flow 和 cost management，同时列出 man-in-the-middle、payment fraud、malware、DoS 以及 coordinated load attack 等风险。[pdf:E16]（PDF 物理页 17，Section VI）

对 EMT + FPGA 读者必须明确：本文没有给出统一的 converter state-space model、离散时间推进公式、switching/event 处理算法、multi-rate 调度、fixed-point 数值格式、FPGA pipeline、资源占用、时序收敛或实际执行平台；这些项目均为论文未报告。Fig. 7 和 Fig. 9 只是控制框图，不能据此宣称作者完成了 real-time EMT 或 FPGA implementation。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文是综述，没有一套贯穿全文的核心数学模型或统一推导，因此不存在可按“假设 → 方程 → 定理/算法 → 误差界”复原的方法。converter 部分给的是 topology 与 control schematic，未给出统一 plant equation、controller tuning 或 stability proof；Fig. 10 的 radar score 也未给出可重算的原始数据表与 normalization procedure。[pdf:E08]（PDF 物理页 9，Fig. 7）[pdf:E10]（PDF 物理页 11，Fig. 10）

唯一较完整的形式化片段是 reliability block scheme。论文把 reliability function \(R(t)\) 定义为系统在时刻 \(t\) 成功运行的概率，并说明它可来自 physics-of-failure、reliability testing、历史数据或 modeling，但真实值通常难以预测。[pdf:E14]（PDF 物理页 15，Section V-B）Fig. 13 随不同 use case 把 grid、AC-DC、两个 DC-DC、BESS 和两个 dispenser 的 component reliability 组合为多条乘积/互补概率表达式。[pdf:E15]（PDF 物理页 16，Fig. 13）其工程直觉是：串联的必要组件中任一失效都会使该 use case 失效；并联或可替代路径则用互补概率表示“至少一路可用”。这些公式只说明结构依赖关系，不提供 component failure distribution、参数估计或置信区间，所以不能从本文重算 station lifetime。

## § 7 — 实验设计与结论

本文没有新建 prototype experiment，也没有在统一工况下对所有 topology 做实验。因此更准确的说法是“综述问题 → 文献与标准整理 → 条件化答案”：

- **问题：grid 与 station 应如何连接？ → 证据设计：** 用 Fig. 4 枚举四类 grid connection，再用 Fig. 5 与 Table I 对 AC、DC、hybrid microgrid 做结构比较。**答案：** MV 适合直接取得高功率但接入成本和体积更高；弱 LV 场景更需要 BESS/RES 进行 local leveling，DC microgrid 对以 DC source/load 为主的 station 更自然，但 protection 与控制也更难。[pdf:E05]（PDF 物理页 6，Fig. 4）[pdf:E06]（PDF 物理页 7，Fig. 5）[pdf:E07]（PDF 物理页 8，Table I）
- **问题：哪条 conversion chain 与边界条件匹配？ → 证据设计：** Table II 把四类 grid architecture 与 diode bridge、buck PWM、AFE、NPC、SAB、LLC、DAB 做可选性匹配，Fig. 10 再按器件数、THD、bidirectionality、power-factor range、ZVS、loss 和 control complexity 做 radar comparison。**答案：** 选择必须受 voltage level、power-flow direction、isolation 与 BESS/RES 条件约束；作者拒绝给出无条件总排名。[pdf:E10]（PDF 物理页 11，Table II、Fig. 10）
- **问题：标准是否只管 connector？ → 证据设计：** 文章沿 SGAM、IEC/SAE connector、communication、protection、CCC/CVC 动态要求展开。**答案：** standards gate 同时约束设备、电气保护、通信、用户交互和 energy-transfer behavior，而不只是插头形状。[pdf:E11]（PDF 物理页 12，Fig. 11）[pdf:E13]（PDF 物理页 14，Sections IV-C、IV-D）
- **问题：一个物理 station 是否只有一个 reliability？ → 证据设计：** 对可重构的双 slot/BESS UFCS 建 RBS，并随 use case 改变逻辑连接。**答案：** 没有；低压双车、高压单车、grid/BESS availability 会改变 critical path 和系统可靠性。[pdf:E12]（PDF 物理页 13，Fig. 12）[pdf:E15]（PDF 物理页 16，Fig. 13）

不得外推之处是：radar score 聚合自不同来源，论文未报告统一 test protocol、误差条、统计显著性、硬件成本清单、全效率地图、thermal cycling、EMI、fault ride-through 或 long-term availability。作者在结论中提出，MV 场景可用 AC 或 DC architecture，弱 LV 场景可考虑带 storage 的 DC microgrid，并把 nonisolated partial-power converter 视为提高效率的潜在方向；这些是综述建议，不是本文新实验验证的胜出方案。[pdf:E17]（PDF 物理页 18，Conclusion 尾段）

## § 8 — Take-aways

**5 句话：**  
1. UFCS 的设计对象不是单个 converter，而是 grid、microgrid、conversion chain、vehicle、standard、reliability 和 data 的耦合系统。  
2. 充电功率与车辆电压共同决定电流、热、线缆、绝缘和 voltage-conversion 负担，不能只看“峰值 kW”。  
3. LV/MV、AC/DC/hybrid、单向/双向、单 slot/多 slot 和 BESS/RES 会逐层缩小可选 topology。  
4. Table II 与 Fig. 10 是条件化导航，不是 universal ranking；作者自己明确说工作条件会改变性能。[pdf:E10]（PDF 物理页 11，Table II、Fig. 10）  
5. standards、reliability 与 cybersecurity 必须在 architecture 形成时进入，而不能在 converter 定型后再补。[pdf:E11]（PDF 物理页 12，Fig. 11）[pdf:E16]（PDF 物理页 17，Sections VI–VII）

**3 句话：**  
1. 先固定 grid、vehicle、slot、power-flow 与 isolation requirements，再谈 converter。  
2. 论文最有用的产物是跨层 design map，最弱的地方是缺少统一 operating point 下的可复算 benchmark。  
3. 对 EMT/FPGA 工作而言，它提供需求与 topology vocabulary，却没有给出可直接部署的离散模型或 hardware mapping。

**1 句话：**  
UFCS 的真正难点不是找到“最高效 converter”，而是证明一整条条件化设计链在电网、车辆、标准、故障与运营数据约束下仍然成立。

## § 9 — 最脆弱的假设

最脆弱的假设是：来自不同论文、不同功率等级、不同器件代际和不同工作条件的定性/半定量结果，经过类别化与 normalization 后，仍足以形成可靠的 architecture-selection guide。这个假设一旦不成立，本文最核心的“把需求匹配到方案”贡献就会退化成术语目录；因为某 topology 在一个 operating point 上的 loss、THD 或 ZVS 优势，可能在宽电压、轻载、热限制或 fault condition 下反转。

论文对这个风险给了诚实但有限的证据。Fig. 10 汇总多个来源，作者明确说它“不提供 converters 的最终比较”，因为性能依赖 working conditions，conversion-stage 选择取决于许多因素。[pdf:E10]（PDF 物理页 11，Fig. 10 后正文）然而，论文没有报告跨来源 score 的原始测量、normalization formula、uncertainty、器件世代校正或统一 validation set。缺少的关键证据不是再多列几种 topology，而是在共同边界条件下证明 Table II 的推荐关系具有可重复的预测力。

## § 10 — 最小复现实验

一周内最值得复现的不是整座 station，而是检验“条件化选择是否比直觉选型更可靠”这一点。

1. **数据与工况：** 从论文的 Fig. 12 抽取一个双 slot、BESS-coupled DC microgrid 结构，并设置两个 operation mode：双路低压充电与 DC-DC 串联高压充电。论文示例把两车模式描述为最高 450 V，把串联单车模式描述为最高 900 V；这些数值只用于复现该 use-case switch，不代表通用产品边界。[pdf:E12]（PDF 物理页 13，Fig. 12）
2. **实现：** 用 averaged EMT model 实现两条最小 conversion chain，而不是铺开全部七种 converter。候选 A 采用可双向 AFE 加 DAB，候选 B 采用单向 front end 加 SAB 或 LLC；对两条链使用相同 grid impedance、vehicle power request、switching-frequency assumption、device loss model 和 cooling limit。论文未报告这些统一参数，因此实验者必须公开设定，不能称为重放作者实验。
3. **测量：** 在相同 charging profile 下记录 grid-current THD、DC-bus deviation、conversion efficiency、semiconductor peak current/voltage、isolation condition、mode-switch transient 与单点故障后的可服务 slot 数；同时记录每个结论对参数变化的 sensitivity。
4. **支持标准：** 若 Table II/文中机制预期的候选在两个 mode 和合理参数扰动下保持 Pareto-nondominated，并且其优势能由 bidirectionality、soft switching、isolation 或 stage count 解释，则支持“条件化 guide 有预测力”。
5. **反驳标准：** 若排名随小幅 grid impedance、vehicle voltage 或 partial load 改变就频繁反转，或推荐方案在同等 safety constraint 下被另一方案全面支配，则反驳核心 guide 的稳健性。

这个实验不需要复现 cloud、connector 或整套 station，但会直接暴露文章最关键的证据缺口：跨来源定性结论是否能在统一模型里存活。

## § 11 — 最强反例设计

最强反例不是找一个“更高效率的新 converter”，而是构造一个论文 matching logic 会稳定选错的 operating envelope。具体做法是让同一 station 在 400–900 V 车辆范围、单/双 slot 切换、BESS 高/低 SoC、weak-grid impedance 和双向功率请求之间连续变化；这些维度正是论文分开讨论却没有联合 benchmark 的条件。Fig. 12/13 已显示，同一物理结构在不同 slot 与电压 use case 下会改变必须工作的 DC-DC 数量和 reliability path。[pdf:E12]（PDF 物理页 13，Fig. 12）[pdf:E15]（PDF 物理页 16，Fig. 13）

攻击成立的判据是：Table II 标为合适、Fig. 10 看似占优的 conversion chain，在这个 envelope 中由于 thermal limit、loss-map reversal、control interaction 或 common-cause failure 无法满足充电服务；而一个表中未优先推荐的 chain 在相同 isolation、protection 与 cost boundary 下持续完成服务。如果观察到这种结果，替代解释就是：真正决定 architecture 的不是类别标签，而是随状态变化的联合可行域；静态 matching table 把关键 interaction 消掉了。这个反例会推翻文章的核心工具性主张，但不会否定其作为术语与标准综述的价值。

## § 12 — Follow-up Research Idea

本领域的高影响工作通常需要同时证明：power-electronics 机制正确、对 grid/vehicle boundary 有工程价值、满足 safety/interoperability，并通过可复现实验或硬件验证给出 efficiency、power quality、thermal、reliability 与 control performance。仅增加一种 topology 或再画一张对比表，通常不足以形成强贡献。

**候选想法：建立“可执行的 UFCS 设计证书”。** 它不是静态 topology catalog，而是一个 constraint-carrying digital specification：输入 grid strength 与 PoD、vehicle voltage/power envelope、slot/queue scenario、BESS/RES、bidirectionality、isolation 与标准条款；输出可行 architecture、每条 constraint 的证据、关键 failure path，以及在参数不确定性下仍成立的 robustness envelope。

- **（a）未满足需求：** 当前综述能告诉工程师“通常考虑什么”，但不能证明一个具体方案在 mode switch、weak grid、partial load、thermal aging 和 component failure 同时出现时仍可服务。
- **（b）研究价值：** 如果证书能把 topology selection、EMT dynamics、thermal/lifetime、RBS 与 standards traceability 放进同一可执行模型，它会把 review knowledge 变成可审计设计决策，并直接服务高功率 charger 的工程验证。
- **（c）相邻领域工具：** 可借鉴 robust optimization、hybrid-system reachability、assume-guarantee contract、fault-tree/RBS 与 digital-twin calibration；FPGA/HIL 可作为实时验证载体，但不是研究目标本身。
- **（d）首个证伪实验：** 选择若干具有明显不同边界的 station archetype，先由证书预测可行 topology 与 robustness margin，再在独立 EMT/thermal/fault co-simulation 或缩比硬件上盲测。若 certificate 的可行/不可行判断不优于静态 Table II，或 margin 不能预测首次 constraint violation，该想法即被证伪。
- **（e）实质区别：** 它改变的是问题定义——从“列举并比较 topology”变为“为具体需求生成可执行、可被反驳的 design assurance”；不是简单增加一个 converter、controller 或 application domain。

由于本次严格只使用指定 PDF，没有联网检索 2023 年之后的相关工作，这一方向只能标为候选研究想法，不声称 novelty。论文附录列出的量产车辆已经展示 400–900 V 级 vehicle architecture 和快速变化的 charge-power envelope，使“静态单点选型”变得更可疑，但这些产品数据只反映论文发表时的记录。[pdf:E17]（PDF 物理页 18，Appendix）
