# An Efficient Half-Bridge MMC Model for EMTP-Type Simulation Based on Hybrid Numerical Integration

- Zotero key：`6I9KI3B7`
- slug：`gao-efficient-half-bridge-mmc2023`
- 作者：Shilin Gao, Ying Chen, Yankan Song, Zhitong Yu, Yenan Wang
- 发表信息：IEEE Transactions on Power Systems，在线发表 2023-03-28，卷期页面为 Vol. 39, No. 1, January 2024
- DOI：`10.1109/TPWRS.2023.3262584`
- 内容真相：`_source.pdf`

## § 1 - 研究问题与重要性

这篇论文处理的不是“如何把 MMC 简化掉”，而是一个更具体的计算瓶颈：在 EMTP-type 电磁暂态仿真中，既保留半桥子模块（HBSM）的电容动态和开关状态，又避免 MMC 的大量电气节点与随开关变化的等效电导矩阵反复触发大规模 LU 分解。作者指出，前者使系统节点方程维数急剧增长，后者使已经很大的矩阵频繁重分解；对含多个 MMC 的离线 EMT 仿真，计算时间可能不可接受。[pdf:E01]

这件事重要，因为 MMC-HVDC 的启动、闭锁、故障和控制暂态都依赖子模块内部动态，单纯的 averaged-value model（AVM）虽然快，却不能在不同运行条件下可靠重现这些内部动态。作者的目标因此是保留 EMTP 现有“网络节点方程 + 元件 Norton 等值”的工作方式，同时让每个 MMC 桥臂在主网络看来只有两个端点，并在正常运行时保持固定等效电导。[pdf:E01][pdf:E02]

论文的核心技术 claim 是：把桥臂电感与子模块电容分别用 trapezoidal rule 和 midpoint rule 组织成相差半步的 leapfrog 更新，可以把每个桥臂写成固定电导的 Norton 等值；在多种正常与异常开关状态、网络切换及多尺度系统上，它与传统 TE-based model 给出近似一致的结果，同时显著减少大网络的计算时间。[pdf:E02][pdf:E06][pdf:E11]

## § 2 - 前人工作与不足

以下是作者在本文中的 related-work framing，不是本卡独立完成的文献核验。

AVM 把每个 MMC 桥臂简化为受控电流源，能压低节点规模，但它依赖运行条件，不能准确模拟 MMC 内部动态。TE-based model 保留子模块动态，并把 MMC 化成六个 Thévenin 端口；问题是端口等效电导仍随开关状态变化，所以没有消除频繁 LU 分解这个第二瓶颈。[pdf:E01][pdf:E02][pdf:E13]

另一条路线是 latency insertion method（LIM）。作者认为 LIM 具有高度并行性，已有 FPGA 实现可做到几十纳秒量级步长；但分布式 LIM 的求解框架与工业和学术界广泛使用的 EMTP-type 工具差异很大，并且难以覆盖某些电力系统元件。已有 LIM-EMTP 混合方案又没有处理 critical damping adjustment（CDA），因此面对 EMTP 网络中的开关和故障时容易出现数值振荡。[pdf:E02]

本文真正改变的不是 MMC 的物理拓扑，而是数值积分和求解时序：传统 trapezoidal 离散会把当前时刻的电容状态耦合进桥臂等效电导，使电导随插入子模块状态变化；作者改用半步电容状态，把这部分移入 history current，从而让正常状态的端口电导不再跟着 `K_1` 频繁改变。[pdf:E04]

## § 3 - 重建作者的思考路径

下面是基于论文证据的逆向重建，不是作者明说的研发日志。

第一步，研究者会把计算慢拆成两个相互独立的问题：节点太多，以及主网络电导矩阵随 MMC 开关变化。已有 TE-based model 已经大幅减少节点，所以继续压缩拓扑不是最有价值的方向；剩下的关键是找出“为何端口电导仍随开关变化”。[pdf:E01][pdf:E02]

第二步，从 trapezoidal 离散式回看端口 stamp。桥臂方程中当前时刻的子模块电容电压依赖当前桥臂电流，因此把电容方程代回去后，Norton 电阻中出现由 `k_{1i}`、`k_{2i}` 决定的项；只要插入状态变化，主网络就看到新的电导。[pdf:E04]

第三步，借鉴 LIM 的 latency 思想但不搬走 EMTP 框架：让电容状态落在 `t-Δt/2`，桥臂电流落在 `t`，再用该电流推进到 `t+Δt/2`。这样桥臂电感和所有子模块电容可以交错显式更新，端口仍然保持标准 Norton 形式。[pdf:E04][pdf:E05]

第四步，检查这项数值重排最容易失效的地方：HBSM 可能出现一条腿导通、两条腿同时导通或两条腿同时关断；网络开关还会触发 trapezoidal ringing。于是作者为异常导通状态分别建立统一桥臂方程，并把 CDA 的两个 backward-Euler 半步嵌入同一接口。[pdf:E03][pdf:E05][pdf:E06]

## § 4 - 核心 Intuition

不要让“本步刚算出的电容电压”反过来改变“本步主网络要用的电导”；把电容电压错开半个时间步，它对主网络就表现为已知 history source。于是 MMC 桥臂仍保留内部动态，但主网络在绝大多数正常运行步只看到一个固定电导的两端口 Norton 元件。发生真正改变导通腿数量或网络拓扑的事件时，再通过状态判断与 CDA 处理，而不是每次 PWM 切换都重做大矩阵分解。[pdf:E04][pdf:E05][pdf:E06]

## § 5 - 具体方法与完整 Pipeline

以一个含 N 个 HBSM 的桥臂为例，输入是上一步桥臂电流、位于半步时刻的各子模块电容电压、当前控制器门极信号、器件电压电流和外部网络端口电压；输出是本步桥臂电流、下一半步的电容电压以及供主网络使用的 Norton 电流源。

1. **判定开关与 HBSM 状态。** 正常时只有上腿或下腿导通；作者还显式处理两腿同时导通和两腿同时关断。上腿导通时子模块输出电容电压，下腿导通时电容被旁路；异常状态会改变桥臂的等效电阻项和电容更新式。[pdf:E03]
2. **形成统一桥臂模型。** 所有子模块状态被压缩进 `R_eq`、选择向量 `K_1`、`K_2` 以及电容电压向量。桥臂在主网络中不再展开为 N 个电气节点，而是一个两节点 Norton 元件。[pdf:E03][pdf:E04]
3. **计算端口 stamp 与 history current。** midpoint/trapezoidal 混合离散给出 `i_arm(t)=Gv_arm(t)+i_hist(t)`。正常运行且 IGBT 与 diode 的导通电阻取相同时，`R_eq` 不随哪个子模块插入而变，因而 `G` 固定；变化被放入 `i_hist`。[pdf:E04]
4. **必要时执行 CDA。** 控制系统与开关状态更新后，仿真器检查元件等效电导是否真的改变。若改变，则对主网络执行两个 `Δt/2` 的 backward-Euler 子步；否则直接进入常规 history current 更新。[pdf:E05][pdf:E06]
5. **求主网络。** 计算 MMC 与其他元件的 history currents，求解节点方程，再恢复包括 `i_arm` 在内的支路电流。[pdf:E05]
6. **推进所有电容。** 用刚得到的 `i_arm(t)`，根据一腿、两腿或零腿导通的对应式，把每个 `v_ci(t-Δt/2)` 推进到 `v_ci(t+Δt/2)`。各子模块电容彼此独立，适合并行计算。[pdf:E05]
7. **进入下一步。** 更新 `t←t+Δt`，重复上述过程。论文实现位于 C++ 编写的 CloudPSS EMTP-type 仿真程序中；本文没有报告 FPGA 上的本方法实现。[pdf:E07]

## § 6 - 核心数学推导

桥臂连续模型被统一写成

`L_0 di_arm(t)/dt = v_arm(t) - R_eq i_arm(t) - K_1 v_c(t) - K_2 v_ceq(t)`，

其中 `K_1` 标识上腿导通的子模块，`K_2` 标识两腿同时导通或同时关断的异常子模块，`R_eq` 根据这些状态取不同形式。[pdf:E03][pdf:E04]

若直接对整个方程使用 trapezoidal rule，当前时刻的 `v_c(t)` 仍依赖 `i_arm(t)`。把电容方程代回桥臂方程后，Norton 电阻会出现含 `k_{1i}` 和 `k_{2i}` 的求和项，因此 PWM 状态变化会让等效电导 `G_tr` 变化。论文的关键代换是用半步已知量近似积分项：

`(Δt/2L_0)[K_1v_c(t)+K_1v_c(t-Δt)] → (Δt/L_0)K_1v_c(t-Δt/2)`，

`K_2v_ceq` 项同理。这样桥臂离散式可整理为标准 Norton 形式

`i_arm(t)=Gv_arm(t)+i_hist(t)`，

`G=Δt/(2L_0+R_eqΔt)`。

`i_hist` 只含上一整步的端口电压和桥臂电流，以及上一半步的电容状态，所以在求解本步节点方程前已知。[pdf:E04]

电容则用 midpoint rule 在半步网格上推进。一条上腿导通时，

`v_ci(t+Δt/2)=v_ci(t-Δt/2)+(Δt/C_smi)i_arm(t)`；

下腿导通或零腿导通时电容电压保持不变；两腿同时导通时先用上一半步电压近似当前电压，得到上腿电流

`i_1i(t)=1/2[v_ci(t-Δt/2)/R_on-i_arm(t)]`，

再用

`v_ci(t+Δt/2)=v_ci(t-Δt/2)-(Δt/C_smi)i_1i(t)`

推进。这里的物理含义是：主网络先用旧半步电压算桥臂电流，电容再吸收这个本步电流；二者相差半步但不互相隐式求解。[pdf:E05]

当网络开关使电导矩阵改变时，CDA 把一个常规步拆成两个 `Δt/2` backward-Euler 子步，分别从 `t-Δt` 推到 `t-Δt/2`、再推到 `t`。论文的式 (32)-(37) 保持同样的 Norton 结构，只改变 `G` 和 history current 的系数；两半步后恢复常规 leapfrog 流程。[pdf:E06]

这套推导的成立边界也很清楚：正常状态下 `G` 固定依赖于把 IGBT 与 diode 的 ON-resistance 视为相同；若两者不同，或同时导通腿数量改变，`R_eq` 与 `G` 就不再固定。[pdf:E03][pdf:E04]

## § 7 - 实验设计与结论

**问题 1：异常 HBSM 状态和网络开关是否会破坏准确性？** 作者先用单 HBSM 和十 HBSM 系统，在 `Δt=10 μs` 下与 TE-based model 比较。单 HBSM 在 `t=0.05 s` 闭锁；不建模零腿导通时，`[0.0827, 0.0846] s` 区间出现明显误差。十 HBSM 测试又覆盖两腿同时导通；忽略该状态后从 `t=0.017 s` 起失真。网络开关在 `t=0.11 s` 动作时，不执行 CDA 会出现明显数值振荡，而执行 CDA 后与基线重合。[pdf:E07][pdf:E08]

**问题 2：半步 latency 是否在启动、稳态和功率阶跃中引入可见能量偏差？** 两端 MMC-HVDC 从零启动，`t<0.08 s` 时 IGBT 与控制器闭锁、子模块由反并联二极管充电，之后触发控制；两模型在 `10 μs` 步长下的启动和稳态波形近似重合。该启动过程中 `G` 在 200000 个仿真步里改变 159 次，即 99.9205% 的步保持常值。[pdf:E09]

在 `t=1 s` 将 MMC2 有功参考从 `-900 MW` 阶跃到 `0 MW` 时，AC 与 DC 侧功率趋势近似一致。作者由图计算的 MMC2 有功效率分别为 TE-based model 的 98.988% 和本文模型的 98.999%，据此判断半步延迟没有造成可见的能量损失或生成。[pdf:E09][pdf:E10]

**问题 3：较大时间步和更复杂网络中是否仍准确？** 两端系统在 `50 μs` 与 `100 μs` 下的结果与 `1 μs` TE-based reference 接近；CIGRE 四端五节点系统在有功阶跃下也与 TE-based model 近似重合。[pdf:E10]

**问题 4：固定电导能否真正缩短 CPU 时间？** 在 Intel i7、32 GB RAM、`10 μs` 步长、3 s 仿真时长下，Table IV 报告两端系统 `44.29 s → 29.12 s`（1.52 倍）、四端系统 `184.41 s → 158.62 s`（1.16 倍）、大规模 AC/DC 系统 `2688.23 s → 274.65 s`（9.79 倍）。大系统包含 10594 个单相节点、134 台发电机、1442 条线路、1124 台变压器、1676 个负荷和一套 MMC-HVDC；接收端在 `t=1.5 s` 发生单相接地故障并在 `t=1.55 s` 切除，本文模型与 TE-based model 的波形近似一致。[pdf:E10][pdf:E11]

**问题 5：子模块数增加后收益如何变化？** Table V 从每桥臂 30 个子模块扫到 120 个；30 个时 CPU 时间为 `30.64 s → 17.08 s`，120 个时为 `61.03 s → 45.46 s`。模型始终更快，但加速比随子模块数增加而下降，因为控制系统计算增长，而本文主要加速的是电气网络求解。[pdf:E12]

论文的实验结论足以支持“在作者测试范围内保持相近波形并减少 CPU 时间”，但没有给出统一的波形误差范数、统计置信区间、内存占用、并行扩展曲线或公开复现代码。因此“与 TE-based model 一样准确”主要来自图形重合和若干功率指标，而不是严格误差预算。

## § 8 - Take-aways

**5 句话：** 1）本文把 MMC 桥臂内部大量子模块压缩为主网络中的两节点 Norton 等值。2）关键不是忽略电容动态，而是让电容状态和桥臂电流错开半步，使正常运行的端口电导固定。3）零腿、两腿导通与网络切换必须单独处理，否则误差或数值振荡会直接出现。4）固定电导的收益取决于网络矩阵分解在总计算中的占比，大系统获得 9.79 倍，小型且控制计算占主导的系统只有 1.16-1.52 倍。5）论文证明的是 CloudPSS 中 CPU EMT 仿真的高效接口，不是已经实现的 FPGA 实时模型。[pdf:E05][pdf:E08][pdf:E11][pdf:E12]

**3 句话：** 混合积分把 MMC 的“内部动态保真”和“外部固定 stamp”从二选一变成可组合的数值结构。异常开关与 CDA 是方法成立的一部分，不是实现细节。它最适合 LU 分解占主要成本的大型 EMTP 网络，而不保证对控制器主导的小系统有同等加速。[pdf:E06][pdf:E11][pdf:E12]

**1 句话：** 用半步 leapfrog 把电容动态移入 history source，换来正常运行时固定端口电导，是这篇论文的全部技术主线。[pdf:E04][pdf:E05]

## § 9 - 最脆弱的假设

最脆弱的假设是：**正常运行的大多数时间里，桥臂等效电阻可以视为固定，因而 `G` 真正长期不变。** 这同时依赖两个条件：IGBT 与 diode 的 ON-resistance 被取成相同值，且异常的零腿或两腿导通只偶发。论文明确写道，若两类器件导通电阻不相等，`R_eq` 就不再保持常数；导通腿数量改变时 `G` 也会改变。[pdf:E03][pdf:E04]

实际器件的导通压降和等效电阻会随器件类型、结温、电流方向与老化状态不同。若为了更真实地模拟损耗、热过程、故障闭锁或保护动作而保留这些差异，本文最重要的固定 stamp 可能退化为事件密集的可变 stamp。作者只说明 IGBT/diode 的 ON-resistance 都很小，取等或不等时 EMT 波形“nearly the same”，但没有给出电阻比、温度范围、误差度量或对 LU 次数和速度的影响扫描。[pdf:E03]

性能结果也侧面显示这一风险：大网络矩阵分解昂贵时加速 9.79 倍，而控制节点超过 15000、仅 193 个电气节点的四端系统只有 1.16 倍。也就是说，即使数学假设成立，若 LU 本就不是主要成本，核心工程价值也会显著缩水。[pdf:E11][pdf:E12]

## § 10 - 最小复现实验

一周内不必复现整个 MMC-HVDC。最小实验可以只搭建论文 Fig. 8 的单 HBSM 电路，同时实现两个可交换元件模型：传统 TE-based model 与本文的 half-step leapfrog Norton model。使用 Table II 的参数、`Δt=10 μs`，执行三段测试：正常 PWM；`t=0.05 s` 闭锁以制造零腿导通；`t=0.11 s` 断开网络开关以触发 CDA。[pdf:E07]

需要记录四类量：

1. `i_arm` 和 `v_ci` 的全时域波形，以及相对一个更小步长 TE-based reference 的最大误差和 RMS 误差；
2. 每步 `G` 是否改变、主网络矩阵实际分解次数；
3. 开启/关闭零腿状态模型时，`[0.0827, 0.0846] s` 的误差变化；
4. 开启/关闭 CDA 时，开关动作后的振荡峰值和衰减。

支持核心 claim 的结果应当同时满足：本文模型在相同步长下与 TE-based model 收敛到同一参考波形；正常 PWM 段 `G` 不随插入状态改变；零腿模型消除闭锁区间的系统性偏差；CDA 消除网络开关后的数值振荡。只要出现以下任一结果，就应反驳或收缩 claim：在正常段仍频繁改变 `G`，半步模型相对小步长参考出现持续能量漂移，或 CDA 只能靠额外人工阻尼才稳定。

## § 11 - 最强反例设计

最强反例不是再找一个更大的理想 MMC，而是构造一个**导通电阻非对称且异常状态事件密集**的 HBSM 群。令 `R_on,D/R_on,T`、结温和电流方向共同变化，在启动、闭锁、直流故障清除及保护重触发期间制造大量零腿与两腿状态；同一网络上比较三种实现：本文固定电阻近似、按真实器件电阻更新的本文结构、完整 TE-based model。

攻击指标应同时覆盖物理误差和计算收益：电容能量漂移、臂电流峰值、故障恢复时间、`G` 变化比例、稀疏矩阵分解次数和端到端 CPU 时间。若固定电阻版本虽然快但低估故障峰值，而真实电阻版本为了准确而频繁更新 `G`、速度接近 TE-based model，就说明本文性能不是混合积分普遍带来的，而是由“器件电阻可同值化、异常事件稀少”这个特定简化带来的。

第二个控制变量是保持 MMC 数量相同，只改变外部网络矩阵规模和控制器计算占比。Table IV/V 已显示加速随 LU 成本占比变化；若固定电导在控制主导系统中没有端到端收益，就不能把“大网络上的 9.79 倍”外推为一般 MMC 仿真加速。[pdf:E11][pdf:E12]

## § 12 - Follow-up Research Idea

在电力系统 EMT 与电力电子建模领域，高影响工作通常不只看一个更快的元件公式，还看数值稳定性和误差边界、故障与极端工况、可集成性、规模化实测以及可复现性。基于第 9 节的限制，本卡提出一个**候选想法**，未做相关工作检索，因此不声称 novelty。

候选方向是“允许物理真实的可变端口 stamp，但把变化限制为可增量更新的低秩事件”。不是强制所有器件共享同一个 `R_on`，而是让每个 MMC 桥臂在少量局部 stamp 模板之间切换；主网络保留稀疏因子分解，并用 low-rank factorization update 处理少数桥臂事件。电容仍采用本文半步 leapfrog 更新，但接口契约从“`G` 必须恒定”改为“`G` 的变化必须局部、可审计、可增量更新”。

- **未满足需求：** 在考虑温度、损耗、器件差异和异常导通时保留物理准确性，同时避免每次事件都全量 LU。
- **潜在研究价值：** 它把本文仅在固定电阻假设下成立的效率优势扩展到损耗、热和保护暂态，并仍可嵌入现有 EMTP-type 求解器。
- **可借鉴工具：** 稀疏矩阵 low-rank update、hybrid-system event scheduling 与 passivity-preserving integration。
- **第一个证伪实验：** 在同一 100+ MMC 网络上注入温度相关 `R_on` 和成簇异常事件；若增量更新的端到端时间不优于全量重分解，或相对完整 TE-based reference 的能量/峰值误差不可接受，则该方向失败。
- **与本文的实质区别：** 本文通过数值错步把正常桥臂强制成固定电导；候选方向承认电导会物理变化，研究对象从“新的 MMC 等值模型”转为“可变元件与全局稀疏求解器之间的更新协议”。

### 证据索引

PDF 物理页从文件首页按 1 开始。证据图保留整页上下文，便于同时核对段落、公式、图题、坐标、表头和单位。

| ID | PDF 物理页 | 主要定位 | 文件 |
|---|---:|---|---|
| E01 | 1 | 摘要、研究瓶颈、AVM/TE 背景 | [`E01-p001-abstract-problem.png`](_evidence/E01-p001-abstract-problem.png) |
| E02 | 2 | LIM/EMTP 背景、三项贡献 | [`E02-p002-contributions-hybrid-integration.png`](_evidence/E02-p002-contributions-hybrid-integration.png) |
| E03 | 3 | HBSM 状态、Fig. 1-3、式 (1)-(4) | [`E03-p003-hbsm-states-arm-equation.png`](_evidence/E03-p003-hbsm-states-arm-equation.png) |
| E04 | 5 | 统一桥臂式、trapezoidal 问题、式 (16)-(25) | [`E04-p005-unified-arm-midpoint-norton.png`](_evidence/E04-p005-unified-arm-midpoint-norton.png) |
| E05 | 6 | 电容式 (26)-(31)、leapfrog 与 Fig. 6 | [`E05-p006-capacitor-leapfrog-flow.png`](_evidence/E05-p006-capacitor-leapfrog-flow.png) |
| E06 | 7 | CDA 式 (32)-(37)、Fig. 7、方法特征 | [`E06-p007-cda-features.png`](_evidence/E06-p007-cda-features.png) |
| E07 | 8 | 单 HBSM 设置、Table II、Fig. 8-10 | [`E07-p008-single-hbsm-validation.png`](_evidence/E07-p008-single-hbsm-validation.png) |
| E08 | 9 | 零腿/两腿误差、无 CDA 振荡、稳定性讨论 | [`E08-p009-abnormal-modes-stability.png`](_evidence/E08-p009-abnormal-modes-stability.png) |
| E09 | 10 | 两端系统启动、159 次 G 变化、99.9205% | [`E09-p010-two-terminal-startup-constant-g.png`](_evidence/E09-p010-two-terminal-startup-constant-g.png) |
| E10 | 11 | 功率效率、50/100 μs、大步长与多端测试 | [`E10-p011-efficiency-large-step-multiterminal.png`](_evidence/E10-p011-efficiency-large-step-multiterminal.png) |
| E11 | 12 | 大系统故障、Table IV 计算时间 | [`E11-p012-large-grid-table-iv.png`](_evidence/E11-p012-large-grid-table-iv.png) |
| E12 | 13 | Table V、适用规模边界、结论 | [`E12-p013-table-v-limit-conclusion.png`](_evidence/E12-p013-table-v-limit-conclusion.png) |
| E13 | 14 | Appendix A 推导、TE-based model、Table VI | [`E13-p014-appendix-te-table-vi.png`](_evidence/E13-p014-appendix-te-table-vi.png) |
