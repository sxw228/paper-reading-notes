# A Combined State-Space Nodal Method for the Simulation of Power System Transients

- 作者：Christian Dufour、Jean Mahseredjian、Jean Bélanger
- 出处：IEEE Transactions on Power Delivery, 26(2)
- 年份：2011
- DOI：10.1109/TPWRD.2010.2090364
- Zotero key：PHUPVIVA

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是“怎样再发明一种 EMT 积分公式”，而是一个求解器架构问题：能否让状态空间法和节点分析法在同一个时间步内同时工作，使不同电气子系统各用更合适的表示，却仍然得到一个电气上联立的解。作者把矛盾说得很直接：节点分析适合大规模稀疏网络和开关网络；状态空间表示便于控制设计、数值积分器选择与子系统建模，但自动生成全系统矩阵较慢，耦合开关一多，预计算所有开关排列的矩阵集合会造成组合爆炸，非线性模型的同时求解也更困难。[pdf:E01]

工程价值在硬实时 EMT 中尤其明显。“硬实时”指每个仿真步都必须在固定截止时间前算完，平均速度快并不够。若一个含很多开关的完整状态空间模型需要为每种拓扑保存矩阵，内存和切换开销会先于算术量成为瓶颈。论文提出的 state-space nodal（SSN）方法把网络切成若干状态空间 group，再通过少量边界节点联立：组内保留状态空间的紧凑动力学，组间保留节点法对拓扑、开关和非线性的处理能力。[pdf:E01][pdf:E05]

对 EMT + FPGA 读者要特别划清边界：本文验证的是 CPU 上的实时求解器组织方式，而不是 FPGA 架构。论文没有报告 FPGA pipeline、定点格式、片上存储、资源占用或时序收敛；因此它能启发“如何分区”，但不能直接证明某个 FPGA 实现可行。

## § 2 — 前人工作与不足

论文把既有路线分成两类。Dommel 式节点法先把器件按梯形法等规则离散为 companion branch，再组装稀疏节点矩阵；它对大网络有效，也已用于实时仿真。状态空间路线则先形成 \(\dot{\mathbf x}=\mathbf A\mathbf x+\mathbf B\mathbf u\)，积分器可在建模后选择，并与 Simulink/控制器设计自然衔接。[pdf:E01][pdf:E02]

作者并非声称“分组”本身从未出现。文中点名了通过 group separation 减少节点数、通过 compensation method 分开线性电路、通过减少连接节点加速，以及把状态空间方程纳入节点方程用于由测量拟合模型综合等既有工作。真正未被满足的是一个更一般的接口：任意拓扑下，让多个自动生成的状态空间 group 以 Norton、Thevenin 或混合端口形式进入同一个节点联立，同时允许普通节点/MANA group 和非线性迭代共存。[pdf:E01][pdf:E03]

先前完整状态空间求解器的不足不是“状态空间不够准确”，而是拓扑变化的工程代价。一个开关排列对应一套 \(\mathbf A_k,\mathbf B_k,\mathbf C_k,\mathbf D_k\)；耦合开关多时，预计算集合按排列数增长。相反，纯节点法虽善于换拓扑，却失去某些已有状态空间模型、自动建模工具和控制设计接口的便利。SSN 的贡献是把两种表示的排他关系改成边界上的 algebraic coupling，而不是要求整网统一改写。[pdf:E01][pdf:E02]

## § 3 — 重建作者的思考路径

可以从论文之前已有的三个观察逆向走到 SSN。第一，离散后的任何线性动态子系统，从端口看都能写成“本步端口量 = 历史源 + 常系数 × 本步另一类端口量”；这正是节点法 companion branch 的抽象，而不只属于单个 \(RLC\) 元件。第二，若把一个大状态空间模型切开，组内状态仍可独立推进，真正必须全局同时决定的只剩边界节点电压或电流。第三，开关组合爆炸来自把远处、弱耦合的开关排列做笛卡尔积；若它们分属独立 group，各组只保存本地排列，组合数就从“乘在一起”变为“分别保存再由节点接口联立”。[pdf:E02][pdf:E05]

沿这条路径，研究者会自然提出两个问题：状态空间 group 能否在离散后导出稳定的 Norton/Thevenin 等效？不同端口类型能否统一装配进节点矩阵？论文的 Eq. (6)–(12) 正是在回答这两个问题。然后才轮到工程上的并行：各 group 的开关判定、历史项更新和状态回代可以并行，但边界节点方程仍需一次全局求解。[pdf:E03][pdf:E04]

这一路径也解释了为什么作者没有简单采用“延迟一个时间步的电流注入”来解耦：那会牺牲电气同时性，尤其在非线性和较大步长下可能损失精度与稳定性。SSN 保留本步联立，把解耦放在模型组织和矩阵规模上，而不是放在物理耦合的时间延迟上。[pdf:E10]

## § 4 — 核心 Intuition

核心 intuition 是：一个离散状态空间子系统对外不必暴露全部内部状态，只需暴露一个“历史源 + 端口导纳/阻抗”的 companion equivalent；把这些端口等效装配到全局节点方程，就能同时解出所有 group 的边界量。[pdf:E02][pdf:E03]

因此，开关和复杂动态主要留在局部 group 内，只有少量节点参与全局联立。方法奏效的关键不是取消耦合，而是把“必须同时求解的耦合”压缩到端口层，同时仍在同一时间点回代各组状态。[pdf:E04]

## § 5 — 具体方法与完整 Pipeline

以 Fig. 2 的开关 RLC 电路为例，输入是本步开关状态、上一步状态与历史项，以及两个 group 边界处的未知端口量；输出是本步节点电压、支路电流和所有 group 的内部状态。Fig. 2 把电源与左侧网络作为 Group 1，把开关后的 \(10\,\mathrm{mH}\)、\(1\,\mu\mathrm F\)、\(50\,\Omega\) 支路作为 Group 2；Group 1 为 I-type，Group 2 为 V-type。[pdf:E05]

完整时间步如下：

1. 先用相量稳态解初始化状态和 history terms。论文给出频域 Eq. (13)–(15)，先求边界节点，再求各 group 的状态和输出。[pdf:E04]
2. 进入下一时间点，按本步开关位置或 piecewise-linear segment 选择局部的第 \(k\) 套状态空间矩阵。[pdf:E02][pdf:E04]
3. 各 group 由上一步状态和内部激励计算历史源，并把离散端口关系改写成 V-type Norton、I-type Thevenin 或 mixed-type 形式。[pdf:E02][pdf:E03]
4. 把各 group 的端口导纳按节点映射到全局 \(\mathbf Y_N\)，把历史源贡献装入 \(\mathbf i_N\)。只有开关位置或分段发生变化时，相关矩阵项才需更新。[pdf:E03][pdf:E04]
5. 用 LU 或稀疏求解器解 \(\mathbf i_N=\mathbf Y_N\mathbf v_N\)，得到同一时间点的所有未知节点电压。[pdf:E03][pdf:E04]
6. 把边界解回代 Eq. (3)–(4)，推进每个 group 的状态和输出。Steps 3–6 以及回代可在不同 CPU core 上并行，节点联立仍是同步屏障。[pdf:E04]

对开关事件，论文的 RLC 验证在不连续点对 SSN 与 MANA 都采用 half-step Backward Euler，而普通步使用既定离散规则；这说明“group 接口”与“事件补偿/不连续点积分策略”是两层问题，SSN 本身并没有消除开关时刻的数值处理。[pdf:E06]

对多速率、数值位宽和 FPGA 映射，论文未给出实现。它使用固定步长实验和 CPU core 并行，没有论证异步 group、跨时钟域端口交换或定点量化后的稳定性。

## § 6 — 核心数学推导

先看组内连续模型。对第 \(k\) 个开关/分段排列，作者写成

\[
\dot{\mathbf x}=\mathbf A_k\mathbf x+\mathbf B_k\mathbf u,\qquad
\mathbf y=\mathbf C_k\mathbf x+\mathbf D_k\mathbf u ,
\]

其中状态是独立的电容电压和电感电流；\(k\) 同时编码开关位置与 piecewise-linear device segment。[pdf:E02]

梯形离散后，本步状态可写成

\[
\mathbf x_{t+\Delta t}
=\hat{\mathbf A}_k\mathbf x_t
+\hat{\mathbf B}_k\mathbf u_t
+\hat{\mathbf B}_k\mathbf u_{t+\Delta t}.
\]

把输入/输出拆成内部量 \(i\) 和外部节点端口量 \(n\)，再把状态式代入输出式，作者得到端口 companion relation

\[
\mathbf y_{n,t+\Delta t}
=\mathbf y_{k,\mathrm{hist}}
+\mathbf W_{kn}\mathbf u_{n,t+\Delta t},\qquad
\mathbf W_{kn}=\mathbf C_{kn}\hat{\mathbf B}_{kn}+\mathbf D_{knn}.
\]

物理上，\(\mathbf y_{k,\mathrm{hist}}\) 汇总了在求本步端口未知量之前已经知道的上一步状态和内部激励；\(\mathbf W_{kn}\) 则是本步从端口激励到端口响应的离散增益。[pdf:E02]

若 \(\mathbf y_n\) 是流入 group 的电流、\(\mathbf u_n\) 是节点电压，\(\mathbf y_{k,\mathrm{hist}}\) 就是 history current source，\(\mathbf W_{kn}\) 是导纳矩阵，即 V-type/Norton group。若 \(\mathbf y_n\) 是电压、\(\mathbf u_n\) 是流入电流，则得到 history voltage source 与阻抗矩阵，即 I-type/Thevenin group。Eq. (8) 允许两类端口混合；把所有未知电流移到左边后得到 Eq. (9) 的统一节点形式。[pdf:E03]

每个 group 的 \(\mathbf Y_{kn}\) 按连接节点 stamp 进全局矩阵，形成

\[
\mathbf i_{N,t+\Delta t}=\mathbf Y_N\mathbf v_{N,t+\Delta t}.
\]

这里 \(\mathbf i_N\) 是已知注入，\(\mathbf v_N\) 是全局未知节点电压。若采用 modified-augmented-nodal analysis（MANA，即把某些支路电流也保留为未知量的扩展节点法），mixed group 可直接进入

\[
\mathbf b_{N,t+\Delta t}=\mathbf A_N\mathbf x_{N,t+\Delta t},
\]

从而避免为 I-type 接口做额外矩阵求逆。[pdf:E03]

非线性磁化支路展示了同一框架如何变成 Newton 式同时迭代。每一迭代 \(j\) 用分段线性关系

\[
\phi_{L_t}=K^{(j)}i_{L_t}+\phi_0^{(j)}
\]

表示磁链-电流曲线；经梯形积分改写为

\[
i_{L_t}=
\frac{\Delta t}{2K^{(j)}}v_{L_t}
+\frac{1}{K^{(j)}}\left(\phi_{L_h}-\phi_0^{(j)}\right).
\]

第一项更新节点矩阵中的支路导纳，第二项更新右端历史注入；线性化后 \(\mathbf A_N\) 就是 Jacobian，重复因子分解与回代直到收敛。[pdf:E10]

## § 7 — 实验设计与结论

**问题 1：SSN 接口是否改变基本开关暂态解？** 作者用 Fig. 2 的 \(500\,\mathrm{kV}\) 等效电源和两组 RLC 网络，在 \(0.05\,\mathrm s\) 合闸，分别取 \(\Delta t=5\,\mu\mathrm s\) 与 \(50\,\mu\mathrm s\)，并与 MANA 比较。Fig. 3–4 中两种方法的开关电流曲线重合；这是对接口一致性的直接支持，但只是一个小型线性电路。[pdf:E05][pdf:E06]

**问题 2：复杂换流系统中能否保持结果接近参考实现？** 作者模拟 \(1000\,\mathrm{MW}\) 12-pulse HVDC，连接 \(500\,\mathrm{kV}/60\,\mathrm{Hz}\) 与 \(345\,\mathrm{kV}/50\,\mathrm{Hz}\) 两个交流系统，整流侧切成四个 SSN group，逆变侧仍用普通状态空间；固定步长为 \(25\,\mu\mathrm s\)。Fig. 6–8 与 SPS 很接近，但作者明确承认直流电流存在小差异，原因包括无法复现 SPS 的晶闸管开通/关断细节，以及 \(25\,\mu\mathrm s\) 采样引起的低频 jitter。[pdf:E06][pdf:E07][pdf:E08]

**问题 3：分组是否缓解开关排列爆炸？** 三相示例中，全系统保存 \(2^6=64\) 套矩阵；分成两个 group 后只需 \(2\times2^3=16\) 套，代价是边界三相电容成为额外状态并增加一个 \(3\times3\) 节点问题。断路器案例若整体预计算，文中给出 \(2^{22}\) 套矩阵这一不可实现规模；其五组结构把开关留在局部模型中。[pdf:E05][pdf:E07]

**问题 4：是否达到真实 CPU 硬实时？** 目标机是一台运行 RedHat Linux 的 \(3.2\,\mathrm{GHz}\) Xeon i7 quad-core PC。Table I 报告 HVDC 案例用 3 个 CPU core 达到最坏 \(10\,\mu\mathrm s\) 步长，断路器案例用 1 个 core 达到 \(21\,\mu\mathrm s\)；“最坏”取所有时间步中的最大计算时间，测试未包含 I/O 设备。结论只能外推到该软件/硬件组合，不能据此比较现代 CPU 或 FPGA。[pdf:E08][pdf:E09]

**问题 5：非线性器件能否在节点接口中同时迭代？** 作者用 \(12.5\,\mathrm{kV}\) 配电系统、两个非线性变压器磁化支路和分段线性磁链-电流曲线，加入 \(4\,\Omega\) 单相接地故障；Eq. (16)–(17) 在每次迭代更新 Jacobian 与右端项。与采用 simultaneous iterative solver 的 EMTP-RV 比较，在 \(50\,\mu\mathrm s\) 步长下结果相同，Fig. 14 显示轨迹落在给定非线性特性分段上，两个磁化支路在每个时间点收敛。[pdf:E09][pdf:E10][pdf:E11]

总的证据支持“统一接口可行、在给定案例中与参考求解器一致或接近、并能显著减少局部开关矩阵集合”。它没有给出跨网络规模的复杂度曲线、误差范数、长期能量漂移、最坏 Newton 迭代次数，也没有把 SSN 与优化后的纯 MANA 在同一现代硬件上做公平吞吐对比。

## § 8 — Take-aways

**5 句话。** 第一，SSN 把离散状态空间 group 变成带 history source 的端口 companion equivalent，再 stamp 到全局节点方程。[pdf:E02][pdf:E03] 第二，V-type、I-type 与 mixed-type 接口分别对应 Norton、Thevenin 与混合端口，所以网络不必统一成一种表示。[pdf:E03] 第三，分组的主要收益是把开关排列的全局笛卡尔积变成多个局部矩阵集合，并允许局部计算并行。[pdf:E04][pdf:E05] 第四，RLC、HVDC、断路器与非线性磁化案例表明这种接口在论文工况下与 MANA、SPS 或 EMTP-RV 相符，同时真实 CPU 案例达到 \(10\,\mu\mathrm s\) 和 \(21\,\mu\mathrm s\) 最坏步长。[pdf:E06][pdf:E08][pdf:E09][pdf:E11] 第五，论文没有证明自动分区、任意规模可扩展性、现代硬件性能或 FPGA 实现。

**3 句话。** SSN 的创新不是新的器件方程，而是一个保持本步同时性的状态空间-节点法接口。它把组内动力学、组间节点耦合、局部开关排列和节点非线性迭代分层，从而让计算量可以在两类表示之间调节。[pdf:E03][pdf:E11] 证据足以证明方法成立，但不足以证明任何分区都更快。

**1 句话。** 把复杂动态封装成离散端口等效、只在边界节点上同步，是 SSN 同时获得状态空间建模便利与节点法拓扑灵活性的根本机制。

## § 9 — 最脆弱的假设

最脆弱的假设是：网络存在一个“好分区”，使大部分状态、开关和非线性能够局部化，而全局边界节点矩阵足够小、变化不够频繁，因此局部矩阵集合减少与并行收益大于边界 stamp、全局因子分解和同步开销。

这个假设一旦不成立，论文的核心工程优势会直接消失。若大量理想开关跨越 group 边界，或非线性器件使 \(\mathbf A_N\) 几乎每次迭代都变化，全局矩阵就必须频繁重构和重复因子分解；若 group 尺寸严重不均衡，所谓局部并行会被最慢 group 和节点同步屏障限制。论文自己说明 \(\mathbf Y_N\) 只在开关位置或 piecewise-linear segment 改变时保持不变，并说明非线性迭代要反复更新 Jacobian；这正暴露了收益依赖“变化局部且边界小”的条件。[pdf:E03][pdf:E10][pdf:E11]

作者提供的是若干人工选择的成功分区：三相两组、HVDC 整流侧四组、断路器五组和非线性三组，并展示了组合数和实时步长改善。[pdf:E05][pdf:E08][pdf:E09] 缺少的是分区算法、边界规模扫描、负载均衡分析，以及“何时不该用 SSN”的 break-even curve。因此“存在好分区”在这些案例中被支持，却没有成为可迁移的设计准则。

## § 10 — 最小复现实验

一周内最有价值的复现不是重建整套 HVDC，而是完整复现 Fig. 2 的两组 RLC 合闸，因为它同时检验端口等效、I/V 两类 group、稳态初始化和不连续点处理。

- **数据**：按 Fig. 2 建立 \(500\,\mathrm{kV}/-60^\circ\) 电源、\(98.03\,\mathrm{mH}\)、\(26.07\,\Omega\)、\(48.86\,\mathrm{mH}\)、边界两侧 \(1\,\mu\mathrm F\)，以及 Group 2 的 \(10\,\mathrm{mH}\)、\(1\,\mu\mathrm F\)、\(50\,\Omega\)；在 \(0.05\,\mathrm s\) 合闸。[pdf:E05][pdf:E06]
- **实现**：写一个直接 MANA 参考求解器；另写一个 SSN 版本，把左侧设为 I-type、右侧设为 V-type，依 Eq. (3)–(10) 生成 history source 与端口矩阵。两者都在不连续点采用 two half-step Backward Euler，并分别跑 \(5\,\mu\mathrm s\) 和 \(50\,\mu\mathrm s\)。[pdf:E02][pdf:E03][pdf:E06]
- **测量**：记录合闸前后 \(49.9\)–\(50.5\,\mathrm{ms}\) 的开关电流、峰值、首个零点和两条轨迹的逐样本差；再记录各步矩阵重构次数。
- **支持标准**：双精度下 SSN 与直接 MANA 的相对 \(L_\infty\) 波形差小于 \(10^{-9}\)，且峰值与首零点在一个采样间隔内一致；这比“图上看起来重合”更可证伪。
- **反驳标准**：排除实现错误后，若差异随步长增大而系统增长，或只在 group 接口处出现额外能量/相位偏差，就反驳“接口不改变离散解”这一最基础 claim。

## § 11 — 最强反例设计

最强反例应攻击分区带来的计算优势，而不是挑一个普通误差案例。构造一个三相网状网络：多个强耦合 LC 子网由大量跨 group 理想开关连接，每个边界附近再放置工作点反复跨越 knee 的饱和磁化支路；设计开关序列，使每个时间步都有边界拓扑变化，并让 Newton 迭代中的分段斜率在相邻 segment 间来回切换。

对同一离散模型比较三种实现：单体优化 MANA、论文式固定 SSN 分区、以及把全部器件并回一个状态空间 group。逐步测量全局矩阵重构/因子分解次数、最坏 wall-clock、迭代次数、deadline miss、波形误差和能量残差。SSN 的可预测失败条件是：局部开关排列确实减少，但 \(\mathbf Y_N/\mathbf A_N\) 几乎每次迭代都变化，节点矩阵不再“小而稳定”，跨组同步和重复 refactor 吞掉全部收益。[pdf:E03][pdf:E10][pdf:E11]

若在相同容差下，固定 SSN 的最坏步时持续高于单体 MANA，或为了赶 deadline 必须减少迭代从而破坏同时非线性解，就推翻“分组通常有利于实时”的广泛解读。它不会推翻 Eq. (6)–(12) 的代数正确性，但会把论文贡献严格收缩为“存在某些有利分区”，这正是对核心工程价值最有力的限定。

## § 12 — Follow-up Research Idea

在电力系统 EMT 与实时仿真领域，高影响工作通常不仅需要新方程，还要有严格的数值稳定性、可复现实验、硬实时最坏时延和具有工程代表性的系统验证。基于第 9 节，候选研究方向是把 SSN 从“人工分组方法”改写为“带证书的硬实时分区编译问题”：输入网络拓扑、开关相关图、非线性器件位置、目标步长与硬件时延模型，输出 group 边界、V/I/mixed 端口类型、静态调度，以及对最坏矩阵集合、边界矩阵规模和 deadline 的可检查证书。

（a）驱动需求是目前没有办法在仿真前判断一个分区会加速还是减速；人工成功案例不能迁移到新网络。（b）研究价值在于把“可调计算负担”变成可预测、可比较、可部署的设计过程，并把精度与最坏时延放在同一个验收契约中。（c）可借鉴 graph partitioning 的 cut/weight 模型、实时系统的 worst-case execution-time analysis、稀疏矩阵 symbolic factorization，以及电路 passivity/conservation 约束；这些工具必须共同约束，而不是只优化 cut 数。（d）第一个证伪实验就是第 11 节的 adversarial switching 网络：若编译器预测满足 deadline，但实测在拓扑/非线性切换下频繁 miss，或为了满足时延破坏离散解等价性，则想法失败。（e）它与论文的实质区别是研究目标从“证明状态空间 group 可接入节点法”变为“自动决定何时、怎样分组，并给出失败边界”。

这是候选研究方向，不声称 novelty。要提出正式 novelty claim，仍需系统检索 2011 年之后的 SSN 自动分区、EMT heterogeneous solver、实时图划分和硬件映射工作。
