# Deadline-Deterministic Sparse Matrix Updates with Versioned Factor Banks for Real-Time Distribution Network EMT Simulation

作者：Dehu Zou、Wei Gu、Wei Liu  
出处：Electronics，15，3934  
年份：2026  
DOI：10.3390/electronics15173934  
Zotero key：6DIE4586  
题名、作者、出处、年份及 DOI 均与 PDF 物理第 1 页题名区、出版信息及页脚一致。[pdf:E01]

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。对相关工作的描述限于本文明确引用和讨论的内容；思考路径、批评、复现实验及研究押注属于分析或建议。

## § 1 — 研究问题与重要性

**本文解决的问题是：配电网 EMT 仿真发生已注册的拓扑数值变化时，如何让变化立即影响当前步的网络解，同时不把矩阵重建与因子分解的长延迟塞进事件步。** EMT 每步都要更新历史源、控制量和设备注入，再求解稀疏节点方程。离线仿真可以容忍少数慢步骤，只要总运行时间较短；实时 HIL 则要求每个步骤都在下一次墙钟释放边界之前完成，少数故障施加或清除步骤的长尾就足以破坏实时执行。这个区别是论文的工程出发点，见物理第 1 页 Introduction。[pdf:E01]

作者把模型变化区分为三类：R update 只改右端项或历史状态；N update 改已注册矩阵位置的数值，但维数、排序和稀疏模式不变；S update 改维数、排序、分区或稀疏模式，需要受控停机、结构重建和重新评定。DDSE 处理的是 N update，因此题名中的拓扑变化实际限定为初始化时预留的 superset sparsity pattern 内的数值变化，不能理解为运行中任意增删节点和连接。物理第 4 页 §2.1、Eq. (1) 明确给出了这一边界。[pdf:E04]

这个问题对配电网保护、馈线重构、故障投入与切除尤其重要，因为这些事件往往只改变少数支路，但传统完整数值重分解仍可能触及大量因子。与此同时，变流器控制和历史源每步变化，并不意味着节点矩阵每步都变化。作者利用的物理工作负载特征是：积分步很快，真正改变矩阵的配电网动作相对稀疏。物理第 2 页 Introduction 将这两种时间尺度明确分开。[pdf:E02]

本文的价值在于建立一种可审计的矩阵状态交接方式：已接受的物理变化立即生效，昂贵的因子维护稍后完成，完整新因子只在安全边界替代旧表示。作者将 deadline-deterministic 限定为指定硬件、软件、矩阵、负载和容量范围内的预分配、有容量界的前台事务；整步截止能力依靠该部署范围内的实测评定，未给出跨平台 WCET 证明。这个限定贯穿物理第 3 页 Introduction 和物理第 6 页 §2.4。[pdf:E03][pdf:E06]

## § 2 — 前人工作与不足

**已有工作已经解决了稀疏求解、局部矩阵修改和并行 EMT 的许多数值问题；本文补上的主要缺口是事件生效、后台维护与版本交接之间的时间组织。** 以下比较均采用本文的归纳，未将被引文献当作已经独立阅读全文的来源。

Dommel 的 companion-circuit EMT 方法提供了逐步形成节点方程的基础；Tinney 与 Walker 的有序三角分解、Davis 的 sparse direct methods，以及 Davis 与 Palamadai Natarajan 的 KLU，提供了高效稀疏求解和数值重分解能力。这些工作分别列于物理第 28 页 References [1]、[3]–[5]。它们解决的是方程如何有效求解；若完整数值重分解仍在事件步执行，重分解延迟就仍在该步的截止路径上。本文 Table 1 将这个问题明确归于 complete fixed-pattern numerical refactorization。[pdf:E28][pdf:E02]

Alsac、Stott 与 Tinney 的 sparsity-oriented compensation，以及本文讨论的低秩补偿路线，已经能够利用旧矩阵的解构造修改后网络的解。它们的优势是立即可见，代价是未被吸收的修改会持续产生修正工作。本文不是指出低秩补偿不能处理开关，而是强调：**只有补偿、没有吸收机制时，长期累积的不同支路目标会耗尽有限容量，并拖慢后续每一步。** 这一比较见物理第 2 页 Table 1；对应文献包括 References [6]、[9]，见物理第 28 页。[pdf:E02][pdf:E28]

Karaagac 等的 partial refactorization、Dinkelbach 等的 factorisation-path refactorisation，以及 Bruned 等的 partial refactorization techniques，已经能够只更新受影响的列、路径或子树。它们的问题不是完全没有实时意识，而是事件步所需工作仍受图结构、排序和受影响因子区域影响，不能仅由本步提交了几个支路描述符来界定。本文承认这些方法可以缩短后台构建，但没有在完全相同的矩阵表示、排序、因子存储和平台上实现它们，因此没有给出对这些方法的实测速度排名。文献身份见物理第 28 页 References [10]–[12]，比较边界见物理第 16 页 §5.2。[pdf:E28][pdf:E16]

后台重建和 multiversion buffering 可以把因子化移出事件步，但若新状态必须等到新因子完成才可见，就引入了物理事件生效延迟；若前台还要复制完整 CSC、动态分配、加锁或清理可变长度列表，异步因子化也没有真正消除前台长尾。物理第 3 页 Fig. 1 专门展示了这个失败模式，图中的条带长度只是示意。[pdf:E03]

并行、multirate、network equivalent 和 ParaEMT 等系统主要处理分区关键路径、通信和大规模吞吐；同平台前作 Zou、Gu、Liu 的 Bergeron–π 线路模型主要处理线路精度和分区解耦。本文将这些路线定位为可组合的外围技术，而非同一问题上的直接替代品。ParaEMT、multirate 方法与前作的文献信息见物理第 28–29 页 References [16]、[19]、[21]；若要比较它们是否已经提供相似的事件版本协议，需要补读对应全文。作者自己将贡献定位为已知代数方法的时间组合，而非新的 SMW 恒等式或因子化内核，见物理第 23 页 §7.1。[pdf:E28][pdf:E29][pdf:E23]

## § 3 — 重建作者的思考路径

下面是从论文提供的背景逆向重建的研究路径，属于分析，不是作者研究过程的事实记录。

首先，一个研究者会观察到：仿真慢步主要出现在少数矩阵状态改变的时刻，普通历史源更新却不要求重新分解矩阵。因此，优化对象不应只是平均三角求解速度，还应包括事件步额外承担了什么工作。这个判断来自物理第 1–2 页对逐步实时约束和 R/N 更新频度的讨论。[pdf:E01][pdf:E02]

其次，支路导纳的改变具有局部 stamp。即使它对全网电压产生影响，其矩阵扰动的代数支撑仍然很小。既有 compensation 方法和低秩恒等式提示：可以先利用旧因子得到新网络的解，无须先得到新网络的完整因子。这里的线索来自已有 nodal stamp、compensation 和 SMW，而非预先假定本文的系统结构；相应基础见物理第 4–5 页 §2.2–2.3 及其引文。[pdf:E04][pdf:E05]

再往前推一步，只保留补偿也不理想：每个尚未吸收的不同支路都让后续求解多做工作。一个合理设计方向便是让补偿承担短期数值生效，让较慢的维护过程承担长期整理。此时需要回答的已不只是算式是否正确，而是维护过程中读者能看到什么、旧结果是否会覆盖新目标，以及新因子替换旧表示时是否改变正在求解的网络状态。物理第 2–3 页对补偿、异步重建与不完整发布的比较，提供了这些失败模式。[pdf:E02][pdf:E03]

最后，实时系统知识会迫使研究者把动态搜索、分配、等待和大对象复制从事件路径中逐项剥离，并把过载变成可观察的拒绝，而不是无界等待。由此自然得到的研究问题是：能否定义一种有限容量的状态事务，使即时数值表示与稍后完成的因子表示始终对应同一个已接受目标？这一推理把 sparse linear algebra、并发状态所有权和实时执行预算连接了起来。

## § 4 — 核心 Intuition

不要等新因子算好才让故障或支路动作生效，而是先用旧因子加一个小修正，立即解出新网络。昂贵的矩阵重建在旁边完成，只有它追上最新目标后，才在两次求解之间替换旧表示。这样既没有推迟已接受事件的数值生效，又能定期清掉不断累积的小修正，恢复便宜的常规求解路径。物理第 3 页 Fig. 1 与物理第 24 页 §7.2 概括了这一组织方式。[pdf:E03][pdf:E24]

## § 5 — 具体方法与完整 Pipeline

**先回答用户最关心的三个问题：本文没有预存所有开关组合的因子；事件在当前步通过 overlay 生效，完整因子 bank 在步与步之间更换；实际评测对象是双路 CPU 服务器上的稀疏执行路径，FPGA 是机架中的独立小步长引擎。** 下面按执行过程展开。

1. **输入与初始化：固定结构，注册允许变化的位置。** 每个子系统输入固定模式的对称节点矩阵、当前右端项，以及允许改变的标量支路目录。初始化建立不可变 symbolic LDLᵀ pattern，为每条可变支路记录固定 CSC stamp 位置和直接索引 slot，并预分配事件 ring、目标与 shadow 状态、overlay、小稠密工作区和三套 factor banks。运行期不重新排序；结构性 S update 进入独立重建流程。论文报告了 companion-circuit 节点形式，但没有展开各元件的具体积分离散公式。见物理第 4 页 §2.1、物理第 6 页 §3.1。[pdf:E04][pdf:E06]

2. **预存的是当前基准状态及支路响应，而非拓扑组合查找表。** 初始化时三套 bank 都装入同一个初始数值矩阵，各自完成因子分解，并为目录中的每条支路预计算该 bank 对支路 stamp 向量的 inverse action。每个 bank 包含数值 CSC、L、D、支路导纳、inverse actions 和求解工作向量；共享的只是不可变索引和 symbolic 信息。之后三个 bank 轮流承担 active、building 和 ready 角色。因而它是运行中不断生成版本的驻留缓冲结构，存储量不随所有开关组合数指数增长。见物理第 6–7 页 §3.1、Eq. (8)、Fig. 2。[pdf:E06][pdf:E07]

3. **普通步更新模型与右端项。** 历史源、控制量和延迟接口量沿既有 EMT 路径更新；只发生 R update 时，仍使用当前 active bank 求解。积分步长在启动前固定，本文没有让 DDSE 动态改变步长。A100、B50、C50 的步长是应用配置，而非算法参数，见物理第 13 页 §4.3。[pdf:E13]

4. **以 C50 单相接地故障为例，先接纳目标，再让它进入当前求解。** C50 的物理事件是仿真时间 8–18 s 的 A 相接地故障。故障施加和清除分别形成一个已注册接地支路的目标导纳；其具体导纳数值未报告。这两次变化在同一步比较中达到的最大 active rank 为一。前台收到的描述符只有支路 slot 和目标导纳，先检查 slot、有限值、批量与 overlay 容量，并无阻塞地预留一个后台队列入口，再在临时空间更新、合并和压缩目标。相同支路的新目标覆盖旧目标，回到 active-bank 导纳的目标从 overlay 删除。见物理第 16 页 §5.3、物理第 23 页 §6.5，以及物理第 7–8 页 Eq. (9)、§3.2。[pdf:E16][pdf:E23][pdf:E07][pdf:E08]

5. **事务提交与本步求解：旧因子加 SMW bridge。** 作者所有路径的单步描述符上限为四，应用 overlay 容量为十六；这些是部署配置。前台在预分配空间形成小 coupling system，并完成数值检查。任一检查或队列预留失败，整批拒绝，先前已接受状态保持不变；成功则一起提交目标、overlay、序号和服务入口。当前 solve 随即用 active bank 求基准解，再通过 SMW 修正得到最新已接受矩阵的解，无须等待后台新因子。前台不做完整 CSC 复制、稀疏因子化、目录扫描、堆分配或阻塞等待。见物理第 5 页 §2.2–2.3、物理第 8 页 §3.2。[pdf:E05][pdf:E08]

6. **后台吸收：重建一个不可见的完整版本。** matrix worker 轮询固定容量 ring，合并连续队列前缀到 shadow conductance 和 shadow matrix，选取既非 active、也非 ready 的 bank，复制数值矩阵、重新做数值 LDLᵀ、重新生成整个注册目录的 inverse actions，并记录它代表的目标序号。这里执行的正是前台移走的大工作：完整数值 staging、factorization 和全部 inverse-action regeneration。若构建期间又接纳了目标，本次构建仍完成，但其旧序号候选不会被前台启用；后续再吸收更新的队列前缀。见物理第 8–9 页 §3.3、Fig. 3。[pdf:E08][pdf:E09]

7. **完整 bank 的启用发生在 quiescent step boundary。** 后台完成数组和元数据后，以 release-store 发布 ready descriptor；实时 worker 在步边界 acquire-load。只有候选序号等于最新已接受目标序号、且 bank 自身序号也一致，才改 active-bank 索引、清空 overlay，并把原 active bank 交回 idle 角色。此时前一次 solve 和 bounded I/O 已结束，没有求解者持有旧 bank 引用。更换动作不复制因子数组，也不释放内存。这里有两个不同的时刻：物理变化在接纳它的当前 solve 中生效；表示同一矩阵的新完整因子在两次 solve 之间替代旧因子加 overlay。任意时刻到来的外部事件如何映射到某个接纳步，本文没有另给连续时间调度语义。见物理第 8 页 Eq. (10) 与 §3.3。[pdf:E08]

8. **平台与并行边界：服务器内多核执行，分区依靠物理延迟解耦。** 评测服务器有两颗 Intel Xeon Platinum 8358，共六十四个物理核心，SMT 关闭，使用 PREEMPT_RT Linux、固定核心、轮询、NUMA-local hugepages 和 DPDK rings。网络最多分成十六个 EMT 子系统，每个 NUMA 域有一个后台矩阵 worker，为本域多个子系统服务。核心数值路径按每浮点量八字节核算；base bank 使用固定模式、无 pivoting、无 scaling/equilibration 的稀疏 LDLᵀ，小 coupling system 才做 partial row pivoting。见物理第 12 页 Table 2、§4.2，物理第 6–7 页 §3.1、Eq. (8)。[pdf:E12][pdf:E06][pdf:E07]

跨 socket placement 实验只是把后台 worker 放到另一 socket，bank 仍属于子系统的内存域。分区间采用带物理传播延迟的 Bergeron–π 线路接口，本分区本步依赖的是前一步已确定的边界量，因此没有跨分区的同一步迭代联立求解。需要 same-step convergence 的 iterative compensation 接口被作者列为另一个集成任务，见物理第 24–25 页 §7.3。[pdf:E24][pdf:E25]

Fig. 9 所示 ADS-RTSim 还包含 FPGA small-step subsystem、controller-HIL 和 PHIL 接口，但本文测量的是 server-based sparse-execution path。计时范围可以包括 optional FPGA exchange，PDF 未给出 CPU–FPGA 在同一步内联立的算法、FPGA 型号与器件数量、逻辑资源、数值格式或跨速率同步细节。因此，本文可以确定是双路多核 CPU 服务器的 DDSE 评测，无法据此判定独立 FPGA 引擎是单片还是多片，更不能将其解释为多 FPGA 分布式矩阵求解。见物理第 17 页 §5.4，以及物理第 26 页 Fig. 9 和 §7.5。[pdf:E17][pdf:E26]

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有明确的形式化数学，核心由支路 stamp、SMW 求解和状态不变量组成。

**第一步：把支路动作写成低秩矩阵差。** 每个子系统在第 k 步满足

$$G_{s,k}v_{s,k}=i_{s,k}.$$

这里 G 是 companion-circuit 节点矩阵，v 是节点未知量，i 包含历史源、延迟接口量和设备注入。对连接节点 a、b 的标量支路，令 $u_j=e_a-e_b$；接地支路则令 $u_j=e_a$。若 active bank 中导纳是 $g_j^{(q)}$，最新已接受目标是 $\hat g_{j,k}$，则

$$\Delta G_{j,k}=\alpha_{j,k}u_ju_j^T,\qquad \alpha_{j,k}=\hat g_{j,k}-g_j^{(q)}.$$

支路动作虽然可能改变全网电压，其矩阵差仍是一个 rank-one stamp。把不同的未吸收支路收集为列矩阵 U、把导纳差放入对角矩阵 C，便得到

$$G_{s,k}=G_{s,q}+U_kC_kU_k^T,\qquad r_k=|J_k|\le r_{\max}.$$

这些是物理第 4 页 Eq. (1)–(3)。这里的 $r_k$ 是不同未解决支路差的数量，未必等于矩阵扰动的严格代数秩，也不是自上次发布以来收到的命令总数；重复目标会被压缩，零差会被移除。见物理第 5 页 §2.2。[pdf:E04][pdf:E05]

**第二步：通过旧因子把大问题压到小 coupling system。** active bank 保存

$$G_{s,q}=L_qD_qL_q^T,\qquad p_{j,q}=G_{s,q}^{-1}u_j.$$

这里预存的是每条注册支路的响应向量 $p_{j,q}$，没有显式形成完整的 $G^{-1}$。令 $P_{k,q}$ 收集本次 overlay 所需的响应列，并先求 $x_{0,k}=G_{s,q}^{-1}i_{s,k}$，SMW 给出

$$v_{s,k}=x_{0,k}-P_{k,q}\left(C_k^{-1}+U_k^TP_{k,q}\right)^{-1}U_k^Tx_{0,k}.$$

见物理第 5 页 Eq. (4)–(5)。[pdf:E05]

为解释这个式子，可以把 Eq. (5) 的代数过程拆开。由修改后的节点方程得到 $v=x_0-PCU^Tv$；定义 $y=CU^Tv$，就有

$$\left(C^{-1}+U^TP\right)y=U^Tx_0,\qquad v=x_0-Py.$$

这一步是对论文公式的直接展开：真正新增的联立求解只有 overlay 大小，最后再把小系统的解映射回全部节点。零差已在压缩时删除，所以保留的 C 对角元非零。由于 u 只有一个或两个非零端点，$u_i^Tp_j$ 只需读取一个端点或计算两个端点之差，不需要长度为节点数的内积；但最终的 $Py$ 仍然需要遍历响应向量。物理第 5 页 Eq. (5) 后的正文特意区分了这两类工作。[pdf:E05]

**第三步：区分事件控制有界与整步耗时有界。** 论文对前台事件事务给出的操作量界是

$$C_{\mathrm{ctl},k}\le c_0+c_1m_k+c_2m_k^2+c_3m_kr_k+c_4r_k^2+c_5r_k^3+c_{\mathrm{pub}}.$$

当描述符容量和 overlay 容量固定时，这些项不随子系统维数或矩阵非零元数增长。这里的三次项来自小稠密系统处理，publication 项只包括 ready descriptor 的读取和状态检查。见物理第 10–11 页 Eq. (11) 及说明。[pdf:E10][pdf:E11]

完整数值求解却仍满足

$$C_{\mathrm{solve},k}=O\!\left(\operatorname{nnz}(L_q)+n_s+n_sr_k+r_k^2\right),$$

后台吸收则包含

$$C_{\mathrm{bg}}=O\!\left(\operatorname{nnz}(G_s)\right)+C_{\mathrm{numfact}}(G_s)+B_sO\!\left(\operatorname{nnz}(L_q)+n_s\right).$$

其中 $n_s$ 是子系统维数，$B_s$ 是注册支路数。前式保留三角求解和全节点 rank correction，后式还要为整个目录重新生成 inverse actions。见物理第 11 页 Eq. (12)–(13)。所以，把事件控制界解释成任意规模系统的固定整步耗时，会漏掉这两组主要成本。[pdf:E11]

**第四步：空间和服务能力也是方法的一部分。** 每个 bank 的浮点存储近似为

$$S_{\mathrm{bank}}=8\left[\operatorname{nnz}(G)+\operatorname{nnz}(L)+n_s+n_sB_s+B_s+2n_s\right]\ \mathrm{bytes}.$$

物理第 7 页 Eq. (8) 中的 $n_sB_s$ 表示全部注册 inverse actions，可能比稀疏因子更重要；三 bank 的代价需要按此累加。[pdf:E07]

对每个独立服务域，作者给出的必要负载条件是

$$\rho_d=\lambda_d\mathbb{E}[S_{b,d}]<1.$$

其中 $\lambda_d$ 是拓扑批次长期到达率，$S_{b,d}$ 是后台服务时间。物理第 11 页 Eq. (14) 明确称它为必要条件，实际部署还要限定 burst、有限队列、overlay 容量和服务长尾。物理第 5 页的容量规则同样要求，容量能覆盖当前状态吸收并发布之前可能到达的不同支路目标及工程裕量。[pdf:E11][pdf:E05]

**第五步：证明状态表示正确，而不是证明全部浮点运算无误。** Proposition 1 的归纳对象是每次 solve 开始时的最新已接受导纳：接纳事务只增加准确的 desired-to-active 差，后台不修改 active 表示，成功发布则用代表同一目标序号的完整 bank 替换旧 bank 加 overlay。Proposition 2 再利用 release/acquire 和序号检查排除未完成、过时的 bank。只有 active factorization 和 coupling matrix 非奇异时，Corollary 1 才由 SMW 得到精确算术下的直接求解等价性。见物理第 9–10 页 §3.4。[pdf:E09][pdf:E10]

浮点实现另有工程检查：base LDLᵀ 不做动态 pivoting，小系统采用预分配 Gauss–Jordan inversion 和 partial row pivoting；非有限中间量或可用 pivot 小于 $10^{-12}$ 会导致拒绝。初始化还要求归一化代数误差不超过 $10^{-9}$、相对参考解差不超过 $10^{-8}$。这些是接受门槛，不能代替所有已接受状态的条件数分析。见物理第 6 页 §3.1。[pdf:E06]

最终整步预算仍是模型、sparse solve、overlay、event control 和 bounded I/O 之和不超过 h，即物理第 6 页 Eq. (7)。DDSE 通过移走重建成本改善这个预算，并没有从算法操作量界直接推出墙钟时间上界。[pdf:E06]

## § 7 — 实验设计与结论

**证据设计同时检验了时间放置、容量更新、应用整步截止和同一步数值等价性。** 物理第 14 页 Fig. 5 将这些 claim 分别映射到 invariant audit、受控 kernel、实际应用、物理事件、后台服务和波形比较；计时与精度检查使用不同执行，独立参考求解和报告输出不混入 deadline 测量。[pdf:E14]

先明确应用规模。物理第 13 页 Table 3 报告的是分区后的资源包络，而非一个大矩阵的维数：[pdf:E13]

| Profile | 子系统数 | 子系统维数之和 | 最大子系统维数 | 注册标量支路总数 | EMT 步长 | 全部三层 bank 内存 |
|---|---:|---:|---:|---:|---:|---:|
| A100 | 9 | 366 | 129 | 405 | 100 µs | 0.715 MiB |
| B50 | 16 | 480 | 39 | 1332 | 50 µs | 1.027 MiB |
| C50 | 16 | 1026 | 78 | 3444 | 50 µs | 5.374 MiB |

A100 是 grid-forming 光伏站，采用 average-value converter models，对接电站控制器；B50、C50 是面向保护、测量和控制 HIL 的馈线模型。A100、B50、C50 同时通过计时与同一步 backend fidelity；B100、C100 只有额外的计时结果。见物理第 12–13 页 §4.3。[pdf:E12][pdf:E13]

**问题一：前台接纳是否真正避开了大矩阵工作？→ 实验：分配审计、不同规模提交时延与管理开销遥测。→ 答案：在测试范围内符合所设计的操作路径。** K0–K3 的可变大小对象均在初始化时创建；K2 的矩阵复制、数值分解和 inverse-action regeneration 均在后台。K2 外部提交 p99 对非零元数的回归未分辨出显著的尺寸依赖，但完整 solve 仍随矩阵增长。物理第 18 页 §6.1 提供这一结果。[pdf:E18]

应用遥测进一步记录到，四描述符 admission 最大为 1.837 µs；每次 ready/version check 平均为 0.018 µs、最大为 4.660 µs。这些是不同观测口径下的统计，作者没有相加 component maxima 来构造虚假的整步最坏值。见物理第 17 页 Table 5。[pdf:E17]

**问题二：收益来自新的数值内核，还是来自把工作移出事件步？→ 实验：同平台 K0–K4 对照。→ 答案：时间放置是主要机制。** 受控矩阵由 Eq. (15) 定义，为固定带宽、严格对角占优的对称正定矩阵。维数取 256、1024、4096，统一 deadline 为 100 µs；每次四条相邻支路在初值与其 1.5 倍之间交替，每隔一千步提交。各 cell 有五次重复，每次一万步 warm-up、十万步测量。见物理第 14–15 页 §5.2、Eq. (15)、Table 4。[pdf:E14][pdf:E15]

五条路径分别是：K0 在步内做完整吸收；K1 在前台复制完整数值 CSC，后台吸收；K2 是 DDSE；K3 只有 overlay、没有吸收；K4 使用已完成 symbolic analysis 的 public KLU 数值重分解。维数 4096 的核心结果如下，数值均来自物理第 19 页 Table 6：[pdf:E19]

| 路径 | 完整步 p99 / µs | 最大完整步 / µs | Deadline misses |
|---|---:|---:|---:|
| K0：步内吸收 | 54.171 | 484.413 | 495 |
| K1：前台 snapshot | 54.743 | 77.640 | 0 |
| K2：DDSE | 54.275 | 68.094 | 0 |
| K3：overlay only | 63.968 | 68.062 | 0 |
| K4：KLU refactorization | 54.408 | 192.274 | 495 |

K0 和 K4 的普通步并不慢，但全部已安排事件批次都越过 deadline；K2 避开了这种事件尖峰。K1 也按时完成，说明完整 snapshot 在这个规模尚未击穿预算，但其矩阵尺寸相关成本仍能被直接描述符进一步消除。KLU 使用 full CSC，内部内核使用 symmetric lower CSC，论文公开了这种存储差异；K4 是可复现公共求解器基线，不是 storage-identical 的替换实验。见物理第 15 页 §5.2、物理第 19 页 §6.2。[pdf:E15][pdf:E19]

**问题三：为什么不能永久保留 overlay？→ 实验：让不同支路的永久目标累积。→ 答案：后台吸收真正更新了有限容量，并恢复便宜的普通步。** 第二个协议在维数 1024、4096 上每隔一千步给四条此前未改变的支路提交永久目标，使用相同的描述符上限和 rank-256 stress capacity。每次请求九十九批、共三百九十六条不同支路变化。K2 接受全部批次，active rank 不超过四并返回零；维数 4096 的最长 rank-zero recovery 为五百一十四步。K3 每次仅接受六十四批，随后三十五批被容量拒绝；该规模的 median p99 为 771.959 µs，K2 为 64.247 µs。见物理第 15 页协议、物理第 19 页 §6.2。[pdf:E15][pdf:E19]

物理第 20 页 Fig. 6(c)(d) 把这个机制直接画了出来：K2 持续恢复低 rank，K3 逐渐到达容量上限。两条路径、两种规模的最大归一化代数误差仍低于 $8\times10^{-16}$，所以 K3 的失败在这里是持续成本与容量问题，而非精度崩溃。[pdf:E20]

**问题四：放回完整 EMT 应用后，还能每步按时完成吗？→ 实验：持续执行、物理故障和加速服务工作负载。→ 答案：全部已评定配置通过。** 五十五次应用运行共保留 202,600,000 个未经筛选的 post-warm-up 步骤，deadline misses 和 dropped timing samples 均为零，见物理第 20 页 §6.3。[pdf:E20]

E0 A100、B50、C50 的最大完整步分别为 57.697、13.505、14.731 µs；物理事件 E3 的 C50 最大完整步为 21.360 µs，对应最小 margin 28.640 µs。三相接地故障和单相接地故障的投入、清除均保留在事件步记录里。见物理第 21 页 Table 7 与 §6.3。[pdf:E21]

完整步计时涵盖 pre-step I/O、子系统分发与完成、稀疏求解、overlay、分区交换、可选 FPGA exchange、bounded I/O、事件接纳和版本检查；计时记录发布、事后序列化和独立精度检测被排除。原始完成时刻与 run start 锚定的绝对期限比较，所有保留应用运行均无记录丢失。见物理第 16–17 页 §5.4。[pdf:E16][pdf:E17]

**问题五：后台会不会拖住前台，NUMA-local 是否必然更快？→ 实验：C50 每 10 ms 一个目标、每 100 ms 四个目标，以及 local/remote 配对。→ 答案：本工作负载有很大服务余量，但 locality 的实测效应并非单调。** E1 local 的最大构建时间为 248.415 µs，最大 event-to-publication latency 为 250.350 µs；六十四入口队列的 high-water mark 为一。E1 五次共 29,950 批、E2 local 五次共 2995 批均全部接受并发布，相关 failure counters 为零。见物理第 22 页 Table 8。[pdf:E22]

remote worker 增加了 event-step p99 和 publication maximum，而 background maximum 反而下降，all-step p99 的区间跨零。因此，论文支持本地所有权作为减少跨域依赖的架构默认值，没有证明它在每个统计量上都最快。物理第 21–22 页 §6.4、Fig. 7 保留了这一混合结果。[pdf:E21][pdf:E22]

**问题六：立即补偿与稍后换 bank 是否改变波形？→ 实验：相同积分步长下与独立 local refactorization 比较。→ 答案：全部预设 screen 通过。** 代数指标使用 Eq. (16) 的归一化方程误差，预设限值为 $10^{-9}$，相对参考解差限值为 $10^{-8}$，见物理第 17 页 §5.5。[pdf:E17]

波形在共同的 100 µs 输出网格上比较，保留全部共同非恒定通道。A100、B50、C50 分别有七十二、六、十二个通道；最差 NRMSE 分别为 $1.212\times10^{-6}$、$9.038\times10^{-15}$、$5.502\times10^{-12}$，最差 peak-normalized maximum-point error 分别为 $1.339\times10^{-5}$、$9.647\times10^{-13}$、$6.738\times10^{-10}$，报告的 event-time deviation 均为零。见物理第 18 页 Eq. (17) 与评定方法、物理第 22 页 Table 9。[pdf:E18][pdf:E22]

Fig. 8 把误差显示为预设容差的占比。这里验证的是同一离散模型下 sparse backend 的等价性；输出网格上的零事件偏差，也应按该采样分辨率理解。它没有检验更细步长下的物理真值，更没有验证 FPGA 开关级模型。见物理第 23 页 Fig. 8 和物理第 13 页对 integration-step qualification 的单独说明。[pdf:E23][pdf:E13]

最后，应用模型和集成 DDSE 实现是专有的。PDF 文末称外部补充材料提供受控输入、计时记录、绘图脚本和应用派生统计，但排除了专有模型与实现文件，因此应用实验不能从共享包独立重跑。这个复现边界见物理第 27–28 页 Data Availability Statement。[pdf:E27][pdf:E28]

## § 8 — Take-aways

**五句话。** 本文的创新单位是矩阵状态事务的时间组织，而非新的低秩恒等式。[pdf:E23] 已接受目标通过 overlay 影响当前 solve，完整新因子只在序号匹配的步边界启用。[pdf:E08] 后台吸收既移走事件步重建成本，也更新有限 overlay 容量并消除后续持续修正成本。[pdf:E19] 有界的是固定容量下的事件控制工作，完整求解、内存和后台服务仍随矩阵与目录规模增长。[pdf:E07][pdf:E11] 全部实时结论限定于已测 CPU 平台及负载范围，独立 FPGA 引擎的细节不在该评测之内。[pdf:E25][pdf:E26]

**三句话。** 事件的数值生效时间与完整因子的维护时间可以分开。[pdf:E08] 二者通过同一个最新目标状态和序号协议连接，而不是靠推迟物理变化来获得实时性。[pdf:E09][pdf:E10] 系统能长期运行，还取决于后台是否足以持续清空临时差异。[pdf:E11][pdf:E19]

**一句话。** 用小修正立即求新网络，用后台构建稍后替换表示，让事件生效与因子维护不再争抢同一个步内预算。[pdf:E03][pdf:E24]

## § 9 — 最脆弱的假设

**最关键的假设是：需要按时执行的拓扑事件工作负载足够稀疏，使后台能在前台可实时承受的未吸收目标数耗尽之前，产生一个追上最新序号的完整 bank。** 这里的容量不仅是数组还能放多少支路，还包括当前 rank 下整步是否仍能按时完成。Eq. (12) 的节点数乘 rank 修正和 Eq. (11) 的小系统成本，使存储容量上限不能自动成为实时可行上限。[pdf:E10][pdf:E11]

这个假设在集中保护动作、故障后的连续恢复操作，或某些把开关动作直接映射为矩阵修改的开关级模型中可能失效。多个动作若持续落在后台构建窗口内，候选 bank 就可能反复因序号过时而不能发布。新目标仍要靠 active bank 加 overlay 表示，于是 rank 增大、后续每步变慢，最终出现 deadline miss 或整批拒绝。论文规定拒绝保留旧目标；对于必须及时施加的物理故障，旧矩阵继续被求解就意味着所要求的物理事件未被执行，虽然事务自身保持了一致性。其机制前提见物理第 8–9 页 §3.2–3.3。[pdf:E08][pdf:E09]

论文提供的支持证据很强，但集中在低并发服务区：加速应用负载的队列 high-water mark 为一，最大 publication latency 为 250.350 µs，而最密集周期到达间隔是 10 ms；实际 A/B/C 物理事件每个 DDSE cell 只有施加、清除两批，最大 active rank 分别为三、三、一。见物理第 21–23 页 §6.4、Table 8、§6.5。[pdf:E21][pdf:E22][pdf:E23]

缺少的关键证据是接近服务和实时 rank 边界时的 burst 试验，尤其是持续制造 stale candidates 的工作负载。平均利用率小于一只限制长期工作量，不能限制短时间内积累了多少不同目标，也不能保证很快出现序号完全匹配的候选。论文自己将 Eq. (14) 称为必要条件；其零 stale counters 证明当前实验没遇到这类压力，状态不变量证明则只保证不会错误发布，不能单独推出吸收进展。[pdf:E11][pdf:E22]

## § 10 — 最小复现实验

**一周内最值得复现的是容量更新这一因果 claim：相同低秩 bridge 下，打开后台吸收能否避免持续目标导致的 rank 累积。** 不需要复制 ADS-RTSim、外部 HIL 或 FPGA。

- **数据。** 直接按物理第 14 页 Eq. (15) 生成维数 1024、4096 的固定带宽矩阵。PDF 没逐项列出受控实验的完整 branch catalog 和右端项，因此本实验明确自行选择全一右端项，并注册足够覆盖三百九十六次永久变化的已有相邻支路；这验证机制，不追求复刻 Table 6 的绝对时延。[pdf:E14][pdf:E15]
- **实现。** 写一个双线程稀疏 kernel：前台固定 pattern solve、目标压缩和 SMW；后台完整数值构建、全部注册 inverse actions、三 bank 和序号匹配。用预分配单生产者单消费者 ring 与 release/acquire，两个线程固定到不同 CPU 核。K2 与 K3 共享同一代码和数值内核，唯一实验变量是后台吸收是否启用。方法依据是物理第 6–9 页 §3.1–3.3。[pdf:E06][pdf:E07][pdf:E08][pdf:E09]
- **负载。** 按原累计协议，每隔一千步提交四条新的永久目标，共九十九批；描述符上限为四、overlay 容量为二百五十六。另加两个很小的正确性测试：同支路连续改目标，以及恢复 active-bank 原值后从 overlay 消失。累计协议和压缩规则分别见物理第 15 页 §5.2 与物理第 5 页 §2.2。[pdf:E15][pdf:E05]
- **测量。** 保留每一步时间、rank、目标与 bank 序号、接受/拒绝批数、发布记录和所有 failure counters；定时执行结束后再做独立直接求解，计算 Eq. (16) 指标和相对解差。时间指标看未筛选的 maximum、p99.99 和 miss count，而非只看平均值。见物理第 16–17 页 §5.4–5.5。[pdf:E16][pdf:E17]

支持机制的结果是：只要后台确实能在下个事件间隔前完成并发布，K2 就不断返回 rank zero、接受全部永久目标；K3 则在六十四批后用满 rank-256 容量并拒绝后续批次。前者同时应维持与独立求解的数值一致。这个判据对应物理第 19–20 页的原实验结论。[pdf:E19][pdf:E20]

若在后台已追上且通过完整性检查的情况下仍无法清空 overlay，或有已接受目标没有进入当前 solve，便直接挑战状态协议；若两路径数值相同、后台也能及时完成，K2 却没有降低持续 rank 成本，则需要重新检查容量更新的因果解释。新机器上能否满足 100 µs 要作为本地新增评定单独报告，不能要求其绝对时间复制原服务器。

## § 11 — 最强反例设计

**最有力的攻击是构造长期平均负载很低、但短 burst 内候选始终落后最新目标的工作负载，让 K2 暂时退化成论文中已经失败的高-rank K3。** 这比简单发送超过容量的命令更有针对性，因为它可以在没有队列溢出、没有 overlay 超限、没有数值失败时挑战整步实时性。

实验采用原受控正定矩阵和维数 4096，保留单批四描述符、rank-256 stress capacity。把六十四批不同支路的永久目标压缩到连续的事件步，而不是每隔一千步提交；随后留足够长的静默时间，让长期平均服务利用率仍小于一。目标全部采用增加正支路导纳的方式，避免把结果归因于病态或奇异矩阵。容量、原事件协议和矩阵性质见物理第 14–15 页；版本过时的处理见物理第 9 页 §3.3。[pdf:E14][pdf:E15][pdf:E09]

核心设计变量是批次相对后台构建完成的相位：让后续目标在候选发布之前被接纳。因为作者仅允许最新序号候选启用，过时构建的完成不会清除 overlay，累计不同支路数就可能不断上升。原文已经观察到维数 4096 时完整后台吸收远长于单个积分步，也观察到高-rank K3 的持续 p99 越过 deadline；这使该反例具有明确的机制依据。见物理第 19 页 §6.2。[pdf:E19]

同时设置两个对照：一是原来每隔一千步的 K2，二是对完全相同的最终矩阵使用已完成吸收的 rank-zero bank。记录第一次 miss 时的 active rank、候选和最新序号、后台构建次数、队列水位、数值误差及接受状态。若 burst 路径在尚未超容量、所有数值检查通过时已超时，而两个对照按时完成，就能把失败归因于临时表示的驻留成本与最新序号发布条件，而不是求解器精度或模型规模。

该实验的判决对象是将 DDSE 扩展到高 burst 工作负载时的适用性。它尤其能否定一种过强解释：只要事务有固定容量、长期平均后台利用率小于一，所有可接受事件序列就都能按时完成。本文的周期工作负载则作为阳性对照保留。

## § 12 — Follow-up Research Bet

**主 idea：用空间—时间端口算子重新组织异构 EMT，使电气上短连接的 CPU 配网与 FPGA 开关级变流器能够形成微步内的统一电路解。** 这是尚未由本文验证的研究押注。新的问题是：当分区间没有可利用的物理传播延迟时，能否把全节点网络计算留在 CPU 宏步尺度，同时让 FPGA 在每个微步看到网络的动态端口响应，而不是平均值源或延迟到下一步的边界量？成功后，本文机架中的服务器和小步长引擎将能共同表示同一个紧耦合电路，而不再依赖当前评测采用的延迟解耦条件。

核心机制是改变被驻留和传输的数学对象。对于宏步窗口内系数固定的线性 companion network，把窗口内所有微步方程一起消去内部节点和内部历史变量，得到作用在端口电压、端口电流时间序列上的因果算子，以及宏步末全状态重建映射。其时间块结构包含前面微步对后面微步的影响。论文 Eq. (4) 的 registered inverse actions 可作为空间消元的响应基础；新表示进一步把这些空间响应沿离散状态演化展开到时间维，而不只是保存一个时刻的节点矩阵因子。物理第 5 页 Eq. (4)–(5) 提供了这种响应表示的代数起点。[pdf:E05]

在硬件上，CPU bank 的驻留对象改成端口时间算子、历史贡献和重建映射，FPGA 常驻快变流器模型及当前端口算子。每个微步由 FPGA 结合过去端口历史和当前器件方程，求一个小的端口联立系统；宏步结束后，CPU 根据端口历史重建网络内部状态。跨引擎传输由逐微步等待全节点求解，改为宏步算子与历史块交换。这样改变了状态表示、时间尺度、硬件映射和系统边界；全节点单步求解被端口时间序列求解整体替代。

这条方向直接来自全文尚未展开的能力与边界。其一，当前分区之所以没有 same-step coupling，是 Bergeron–π 接口具有物理延迟，作者明确把需要同一步收敛的接口列为另外的集成任务，见物理第 24–25 页 §7.3。[pdf:E24][pdf:E25] 其二，Fig. 9 已有独立 FPGA 引擎，但没有交代两种步长如何形成一个紧耦合网络，见物理第 26 页。[pdf:E26] 其三，受控实验中 K2 把最大完整步从 K0 的 484.413 µs 降到 68.094 µs，并反复恢复 rank zero，证明维护大对象与前台数值可见性可以分处不同时间尺度；这支持尝试新的算子驻留方式，但没有直接证明端口时间表示足够紧凑，见物理第 19–20 页 §6.2、Fig. 6。[pdf:E19][pdf:E20] A100 目前使用 average-value converter，而小步长开关级模型仍在独立引擎中，这使新能力具有具体应用对象，见物理第 13 页 §4.3。[pdf:E13]

与当前 DDSE 相比，新 problem 从矩阵事件事务变成异构电路的微步联立；mechanism 从单时刻 SMW bridge 变成带内部动态记忆的端口消元；representation 从节点矩阵版本变成有限时间窗端口算子；experimental object 从服务器分区网络变成短电气连接的网络—开关级变流器组合。与本文前作 [21] 相比，新方案不依靠线路旅行时间消除同一步依赖；与本文 §7.3 提及的 iterative compensation [9] 相比，押注的是用小型因果端口系统吸收跨引擎耦合，而不是进行跨分区同一步反复通信。[pdf:E24][pdf:E25] 本文对 direct-mapped converter 方法 [15] 和 multirate 方法 [16] 的介绍不足以判断是否已有相似时间算子，正式确立新颖性前需要补读 [9]、[15]、[16]、[21] 的全文；文献条目见物理第 28–29 页。[pdf:E28][pdf:E29]

最大的研究收益是让开关级器件与较大配网在没有人为通信延迟的条件下共同求解，研究对象由平均值装置行为推进到快速开关动作如何传播进入配网。最大的科学风险是端口表示根本不紧凑：空间上低秩的支路变化在时间展开后可能占据许多时间块，内部非线性也可能让固定端口算子失效，最终重新需要接近全状态的在线工作。本文目前只验证标量对称 stamps，block、nonsymmetric 与异构跨速率协同都被列为未完成方向，这些边界必须进入新实验，而不能直接沿用现有 qualification，见物理第 25 页 §7.4 和物理第 27 页 Conclusions。[pdf:E25][pdf:E27]

最小区分实验可以使用自行构建的两端口 RLC 馈线连接一个开关桥，研究设定宏步为 50 µs、微步为 5 µs，先用已知 gate 序列排除控制器轨迹差异。比较同一个电路、同一个微步下的全节点 monolithic reference、完整端口时间算子、以及保留同样端口规模但删除跨微步动态记忆的静态端口模型。再在宏步边界加入一个预注册支路目标，检查时间算子的数值更新和内部状态重建。观测每微步端口电压、电流、CPU 全节点求解次数、端口算子存储量和快环执行时间。

最强替代解释是收益仅来自小端口维数或更细步长。所有路径保持相同微步，静态端口对照保持相同端口维数，就能单独识别时间记忆的作用：只有完整时间算子匹配 monolithic 轨迹、同时无需每微步全节点求解，才支持核心机制；若删除时间记忆也同样准确，应加强窗口内动态激励后再判断，而不能把尺寸缩减误认成新的时域表示能力。

**Wild-card alternative：** 把 registered inverse actions 组织成以候选保护动作组合为坐标的多世界 EMT 状态张量，在共享网络响应基础上生成互斥动作的反事实轨迹，将评价对象从单轨迹截止性能改为一个控制周期内可辨别的动作后果数量与因果差异。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title and author block; publication information; Abstract; Section 1 Introduction; DOI footer"
[pdf:E02]: <_evidence/E02-p002-page.png> "PDF 物理页 2，Section 1 Introduction; Table 1 and note: event-control implications of matrix-update strategies"
[pdf:E03]: <_evidence/E03-p003-page.png> "PDF 物理页 3，Section 1 qualification and contributions; Fig. 1 and caption"
[pdf:E04]: <_evidence/E04-p004-page.png> "PDF 物理页 4，Sections 2.1–2.2; Eqs. (1)–(3); R/N/S update definitions"
[pdf:E05]: <_evidence/E05-p005-page.png> "PDF 物理页 5，Sections 2.2–2.3; target compaction and capacity rules; Eqs. (4)–(5); coupling-system checks"
[pdf:E06]: <_evidence/E06-p006-page.png> "PDF 物理页 6，Section 2.4, Eqs. (6)–(7); Section 3.1 initialization and numerical acceptance checks"
[pdf:E07]: <_evidence/E07-p007-page.png> "PDF 物理页 7，Section 3.1, Eq. (8), bank contents and ownership; Fig. 2 and caption; Eq. (9)"
[pdf:E08]: <_evidence/E08-p008-page.png> "PDF 物理页 8，Section 3.2 validate–stage–commit admission; Section 3.3 background absorption and Eq. (10)"
[pdf:E09]: <_evidence/E09-p009-page.png> "PDF 物理页 9，Section 3.3 stale-candidate handling; Fig. 3 and caption; Section 3.4 Proposition 1"
[pdf:E10]: <_evidence/E10-p010-page.png> "PDF 物理页 10，Section 3.4 Proposition 1 continuation, Proposition 2 and Corollary 1; Fig. 4; Eq. (11)"
[pdf:E11]: <_evidence/E11-p011-page.png> "PDF 物理页 11，Section 3.5 complexity bounds, Eqs. (12)–(13); Section 3.6 service envelope, Eq. (14)"
[pdf:E12]: <_evidence/E12-p012-page.png> "PDF 物理页 12，Table 2 experimental platform; Sections 4.2–4.3 NUMA/lcore mapping and application cases"
[pdf:E13]: <_evidence/E13-p013-page.png> "PDF 物理页 13，Section 4.3; Table 3 structural/resource envelope and notes; A100/B50/C50 step and fidelity profiles"
[pdf:E14]: <_evidence/E14-p014-page.png> "PDF 物理页 14，Section 5.1 timing/fidelity separation; Fig. 5 and caption; Section 5.2, Eq. (15)"
[pdf:E15]: <_evidence/E15-p015-page.png> "PDF 物理页 15，Section 5.2 K0–K4 toggling and cumulative protocols; Table 4; CSC representation comparison"
[pdf:E16]: <_evidence/E16-p016-page.png> "PDF 物理页 16，Section 5.2 affected-path comparison boundary; Section 5.3 application timing/event matrix; Section 5.4 metrics"
[pdf:E17]: <_evidence/E17-p017-page.png> "PDF 物理页 17，Section 5.4 timing interval and absolute deadline semantics; Table 5; Section 5.5, Eq. (16)"
[pdf:E18]: <_evidence/E18-p018-page.png> "PDF 物理页 18，Section 5.5 waveform comparison, Eq. (17) and acceptance gates; Section 6.1 foreground audit and scaling"
[pdf:E19]: <_evidence/E19-p019-page.png> "PDF 物理页 19，Table 6 and note; Section 6.2 K0–K4 comparison, snapshot/background costs and cumulative capacity results"
[pdf:E20]: <_evidence/E20-p020-page.png> "PDF 物理页 20，Section 6.2 cumulative residual and capacity conclusions; Fig. 6 and caption; Section 6.3 aggregate application timing"
[pdf:E21]: <_evidence/E21-p021-page.png> "PDF 物理页 21，Table 7 and Section 6.3 physical-event timing; Section 6.4 service and paired NUMA-placement effects"
[pdf:E22]: <_evidence/E22-p022-page.png> "PDF 物理页 22，Table 8; Fig. 7 and caption; Section 6.5 and Table 9 waveform-equivalence results"
[pdf:E23]: <_evidence/E23-p023-page.png> "PDF 物理页 23，Fig. 8 and caption; Section 6.5 repeatability, physical-event batch/rank coverage and initialization accuracy; Section 7.1"
[pdf:E24]: <_evidence/E24-p024-page.png> "PDF 物理页 24，Sections 7.1–7.3 temporal composition, capacity renewal and physical-delay Bergeron–π partition interface"
[pdf:E25]: <_evidence/E25-p025-page.png> "PDF 物理页 25，Section 7.3 same-step iterative-interface boundary; Section 7.4 deployment envelope; Section 7.5 engineering integration"
[pdf:E26]: <_evidence/E26-p026-page.png> "PDF 物理页 26，Fig. 9 and caption; Section 7.5 distinction between evaluated server path, FPGA engine and external interfaces"
[pdf:E27]: <_evidence/E27-p027-page.png> "PDF 物理页 27，Section 8 Conclusions and future work; Supplementary Materials; Data Availability Statement"
[pdf:E28]: <_evidence/E28-p028-page.png> "PDF 物理页 28，Data Availability Statement continuation; References [1]–[16]"
[pdf:E29]: <_evidence/E29-p029-page.png> "PDF 物理页 29，References [17]–[32], especially [19] ParaEMT and [21] Bergeron–π line model"
