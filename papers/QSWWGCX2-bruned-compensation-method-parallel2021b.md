# Compensation method for parallel real-time EMT studies

- 作者：B. Bruned；S. Dennetière；J. Michel；M. Schudel；J. Mahseredjian；N. Bracikowski
- 出处：*Electric Power Systems Research*
- 年份：2021
- DOI：10.1016/j.epsr.2021.107341
- Zotero key：QSWWGCX2

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

### § 1 — 研究问题与重要性

这篇论文要解决的不是“如何再写一个并行求解器”，而是一个很具体的实时 EMT 瓶颈：传统并行 EMT 常把传输线的传播时延当作天然任务边界，只要传播时延大于仿真步长，两个时刻之间就有足够的因果间隔让子网分开计算；但配电网中的短线路、用集中参数表示的 R-L 线路，以及大型电力电子换流站内部，往往没有足够的天然时延。此时即使机器有多个核，网络方程仍被耦合在同一个时间步里，减小步长所需的计算量无法直接摊开。论文在 Introduction 中把“更小积分步长带来更高 EMT 精度”与“多核并行加速”联系起来，并明确指出 line-delay decoupling 的适用条件和缺口。[pdf:E01](_evidence/E01-p001-sec1-line-delay-decoupling.png)

工程上，这个问题重要在于实时仿真每一步都有硬截止时间：某一步算不完就是 overrun，而不是稍晚得到结果。新能源与 HVDC 控制交互把快速开关过程带进输电系统，配电网规模又持续增长；如果只能靠增加虚构传输线或放大步长来换取实时性，模型的物理结构或时间分辨率就会被计算平台反向决定。作者因此研究 compensation method（CM，补偿法）能否在没有天然传播时延的地方人为“撕开”网络，同时保持 EMT 波形可信，并在 offline、SIL 与接入实际控制保护 replica 的 HIL 环境中获得真实的计算收益。[pdf:E02](_evidence/E02-p001-sec1-bbd-cm-gap.png)

### § 2 — 前人工作与不足

按论文对相关工作的梳理，已有路线可分三类。第一类直接利用传输线时延，在拓扑分析后以线路为边界创建任务；它的优点是因果分离自然，缺点是短线路、集中参数线路和换流器内部没有可用时延。第二类把网络矩阵重排为 Bordered Block Diagonal（BBD，带边界块的分块对角）形式，再用 domain decomposition 或 Schur-complement 类方法并行；作者指出，得到的 BBD 结构未必对应最优计算负载，而且已有应用常假设线性网络，遇到非线性和开关拓扑时需要重新组织或分解矩阵，性能会明显下降。第三类是历史更早的 compensation、diakoptics 和 hybrid-analysis 路线：CM 原本就用于电磁暂态中的非线性、时变元件求解，理论上比单纯的线路时延切分更一般。[pdf:E02](_evidence/E02-p001-sec1-bbd-cm-gap.png)

因此，论文真正补的缺口是“实用边界”而不是补偿理论本身：作者没有声称发明 CM，而是声称此前缺少对 CM 在 practical switching systems 与 real-time simulation 中的性能、精度和失败模式的系统记录。这个定位也限定了本文证据强度：它能说明所给配电网与 IFA2000 案例上的工程可用性，不能单凭这些案例证明任意拓扑、任意切点都可稳定并行。

### § 3 — 重建作者的思考路径

可以从三个先验事实重建这条路线。第一，EMT 每个时间步本来就要解离散后的节点导纳方程；如果把连接支路切开，各子网在该步内就能独立求解。第二，切开会丢掉端口之间本应满足的电压、电流约束，但 Norton/Thévenin 等效与叠加定理恰好提供了一种“先独立、后纠偏”的办法：子网先告诉协调者自己从切口看出去的等效电压与阻抗，协调者再算出真正应该流过切口的电流。第三，实时并行不仅需要代数等价，还需要明确的同步点；因此协调计算必须压缩为一个小规模连接问题，子网的大矩阵工作留在并行区间。

沿着这三点，一个自然方案是：把网络切成若干独立子网；每个子网在切口电流置零时求自身状态和端口等效；集中求解切口电流；再把这组电流作为补偿源回注各子网。这里的关键取舍也在方案形成前就出现了：切口越多，并行潜力越大，但连接矩阵可能更难求、同步更重，且数值条件可能变坏。后文实验实际上验证了这个取舍，而不是证明“切得越多越好”。

### § 4 — 核心 Intuition

CM 的直觉是：先把原网络暂时切开，让每个子网独立回答“如果切口不流电，我这里会是什么电压，以及从端口看进去有多硬”；再由一个小的协调问题算出把这些端口重新接回去时应流的电流，最后把该电流的影响叠加回各子网。物理上它像把一条真实连接暂时替换成一对方向相反的理想电流源：大块内部计算可并行，只有恢复连接约束的端口问题必须串行。[pdf:E03](_evidence/E03-p002-sec2-eq01-eq03.png)

### § 5 — 具体方法与完整 Pipeline

以两个由 \(n_C\) 条连接支路相连的子网 \(N_1,N_2\) 为例，完整时间步如下。

1. **人工选切点。** 本文的 compensation cuts 由用户手工选择；切开后，各子网必须在该时间步内相互独立。[pdf:E03](_evidence/E03-p002-sec2-eq01-eq03.png)
2. **并行求无切口电流的子网状态。** 令连接电流 \(i_C=0\)，每个子网用离散元件模型和节点法求电压；同一任务还计算 history currents。随后对每个切口节点施加单位电流，得到端口 Thévenin 阻抗矩阵。只要子网拓扑不变，这些阻抗矩阵可跨时间步复用。[pdf:E03](_evidence/E03-p002-sec2-eq01-eq03.png)
3. **集中恢复连接约束。** 协调任务把两侧 Thévenin 等效和连接元件阻抗相加，解出连接支路电流 \(i_C\)。这是每个时间步中不可并行的核心小系统。[pdf:E04](_evidence/E04-p002-sec2-eq04-eq05.png)
4. **并行回注补偿。** 各子网把 \(i_C\) 当作理想电流源，在独立源置零时求其电压贡献，再与第一步的无切口电流解叠加，恢复最终节点电压。开关导致 Thévenin 阻抗变化时，补偿阻抗矩阵必须更新并重新 factorize。[pdf:E04](_evidence/E04-p002-sec2-eq04-eq05.png)
5. **用两道 barrier 实现线程同步。** 第一条 barrier 等待所有子网交付 Thévenin 等效；协调任务解出 \(i_C\) 后，第二条 barrier 把结果广播给子网。论文的三任务示例是两个子网线程加一个 compensation 线程，也允许把协调计算并入某个子网任务以减少到两任务。[pdf:E05](_evidence/E05-p002-sec2-fig03-barriers.png)

作者认为熟悉网络的人可以按性能收益选择切口，本文配电网案例就是 feeder-cluster oriented 的手工 tearing；超大网络才考虑用 BBD 方法自动化。[pdf:E06](_evidence/E06-p003-sec3-dist-setup-eq06.png)

在 IFA2000 示例里，模型包含 LCC bipole、详细 6-pulse bridge 和 frequency-dependent DC cable。[pdf:E07](_evidence/E07-p003-table01-dist-results-hvdc-setup.png) 长 DC cable 仍用天然传播时延把两个换流站分开，CM 只在每个换流站内部增加切口，把原本不可由线路时延拆分的 converter station 再分成两个子任务；这说明 CM 与 line-delay decoupling 是叠加关系，不是二选一。[pdf:E08](_evidence/E08-p004-fig08-fig09-hvdc-sil.png)

论文实际实现采用经典 nodal formulation 与 sparse LU，任务映射到 CPU thread，每个 thread 占一个 simulation core。它报告的是 Intel i7、Xeon/OP5031 Linux 实时平台以及 HIL I/O，未报告 FPGA 映射、定点字长、流水线、片上存储、资源占用或多速率 FPGA 调度，因此不能把本文的 CPU 并行结果直接解释成 FPGA 实现结果。[pdf:E04](_evidence/E04-p002-sec2-eq04-eq05.png)

### § 6 — 核心数学推导（无形式化数学则跳过）

先看物理含义。切口两侧各自可等效为一个 Thévenin 电压源和端口阻抗；重新连接时，支路电流就是“两侧开路电压差”除以“从一侧走到另一侧所见的总阻抗”。CM 的数学工作，是在节点方程中系统地构造这些多端口等效，再用叠加把连接电流的影响加回去。

**子网独立解。** 在 \(i_C=0\) 时，

\[
Y_1v_{n1}=i_1,\qquad Y_2v_{n2}=i_2. \tag{1}
\]

\(Y_1,Y_2\) 是两个子网各自的导纳矩阵，\(v_{n1},v_{n2}\) 是未知节点电压，\(i_1,i_2\) 包含独立源与离散元件的 history current injection。切口节点集合为 \(n_{C1},n_{C2}\)，每侧大小都是 \(n_C\)；由这一无切口电流解可直接读取两侧开路 Thévenin 电压 \(v_{\mathrm{th}1},v_{\mathrm{th}2}\)。[pdf:E03](_evidence/E03-p002-sec2-eq01-eq03.png)

**构造多端口阻抗。** 对每个切口节点 \(k\) 注入单位电流并杀死独立源：

\[
Y_1v_1=i_1^{(k)},\qquad Y_2v_2=i_2^{(k)}. \tag{2}
\]

把各次求解在切口节点的电压响应排成列，得到

\[
Z_{\mathrm{th}1}=
\left[v_{1n_{C1}}^{(1)}\ \cdots\ v_{1n_{C1}}^{(n_C)}\right],\qquad
Z_{\mathrm{th}2}=
\left[v_{2n_{C2}}^{(1)}\ \cdots\ v_{2n_{C2}}^{(n_C)}\right]. \tag{3}
\]

每一列的物理意义是“某个切口注入 1 A 时，全部切口电压如何响应”；因此矩阵包含端口自阻抗和互阻抗。拓扑不变时，这个响应不变，可避免每步重建。[pdf:E03](_evidence/E03-p002-sec2-eq01-eq03.png)

**解连接电流。** 连接支路阻抗矩阵记为 \(Z_B\)，若切开的只是理想导线则 \(Z_B=0\)。总连接阻抗为

\[
Z_C=Z_{\mathrm{th}1}+Z_{\mathrm{th}2}+Z_B,
\]

连接电流由

\[
Z_Ci_C=v_{\mathrm{th}2}-v_{\mathrm{th}1} \tag{4}
\]

给出。这里 \(Z_C\) 是否良态直接决定补偿电流对数值误差的放大程度；这也是后文“某些切点会不稳定”的数学根源。[pdf:E04](_evidence/E04-p002-sec2-eq04-eq05.png)

**叠加回子网。** 用求得的 \(i_C\) 作为补偿源，得到其在两侧造成的电压贡献 \(v_{1C},v_{2C}\)，最终

\[
v_{n1}^{\mathrm{final}}=v_{n1}+v_{1C},\qquad
v_{n2}^{\mathrm{final}}=v_{n2}+v_{2C}. \tag{5}
\]

式 (1)、(2) 和回注部分可在不同子网上并行，式 (4) 对全部切口有共同依赖，必须在 barrier 之间串行完成。[pdf:E04](_evidence/E04-p002-sec2-eq04-eq05.png)

实验中的相对误差定义为

\[
\frac{\left|e_{\mathrm{compensation}}-e_{\mathrm{normal}}\right|}
{\max\left(\left|e_{\mathrm{normal}}\right|\right)}, \tag{6}
\]

其中 normal 是不使用 CM 的参考解。分母用参考波形绝对值的全局最大值，因此这个量衡量的是相对于参考峰值的点对点偏差，而不是在过零点会发散的瞬时相对误差。[pdf:E06](_evidence/E06-p003-sec3-dist-setup-eq06.png)

### § 7 — 实验设计与结论

**问题一：在线性大配电网中，CM 能否在不牺牲波形的情况下缩短实时步长？** 作者用 600 节点、20 kV 配电网接 63 kV 电源，线路用 R-L 阻抗、负荷用受控电压源动态模型；以 feeder cluster 手工切分。工况是 1 s 仿真、50 μs 步长，在 63/20 kV 变压器 20 kV 侧于 \(t=0.2\) s 加入持续 100 ms 的 1 mΩ 单相接地故障。该案例只在故障投入时重分解一次导纳矩阵，作者把它视为线性案例。[pdf:E06](_evidence/E06-p003-sec3-dist-setup-eq06.png) 结果是：OP5031 Arch2 上 normal 的无 overrun 实时步长为 145 μs；一次切割、2 核的 comp2 为 73 μs，报告 speed-up 1.99；三次切割、4 核的 comp4 为 40 μs，报告 speed-up 3.63。对应 feeder-root 电流几乎重合，Fig. 7 的误差处于数值噪声量级。[pdf:E07](_evidence/E07-p003-table01-dist-results-hvdc-setup.png)

**问题二：含频繁开关的 HVDC converter 能否保持实时性与精度？** IFA2000 模型包含两个 1000 MW LCC bipole、±272 kV 运行电压、每个 DC pole 两个详细 6-pulse bridge、73 km frequency-dependent cable、详细滤波器与 Simulink 控制；AC 侧用短路容量等效源与阻抗。[pdf:E07](_evidence/E07-p003-table01-dist-results-hvdc-setup.png) SIL 测试在 OP5031 上用 30 μs 步长、200 MW 法国到英国功率传输；不用 CM 时 4 核，用 CM 时 6 核。作者报告 CM 降低了最重任务的执行时间，并在 6.3 s converter deblocking、需要多次 admittance refactorization 时避免了 normal case 的 overrun；Fig. 10 显示 DC voltage 基本重合，但 Fig. 11 的相对误差明显高于线性配电网。[pdf:E08](_evidence/E08-p004-fig08-fig09-hvdc-sil.png) [pdf:E09](_evidence/E09-p004-fig10-fig12-hvdc-hil-limit.png)

**问题三：接入真实控制保护 replica 后，CM 是否仍有收益？** AC-fault HIL 工况用 40 ms 法侧单相接地故障、1000 MW 法国到英国功率、40 μs 步长；CM 用 4 核，normal 用 3 核。作者报告相对经典切分的计算速度提升 40%，Fig. 14 中 normal 与 compensation 的 DC-voltage 响应基本重合，Fig. 15 中最重 processor 的执行时间带整体下移。[pdf:E09](_evidence/E09-p004-fig10-fig12-hvdc-hil-limit.png) [pdf:E10](_evidence/E10-p005-fig13-fig15-hil-fault.png)

**问题四：更强的开关暂态下结论是否维持？** Transformer-energization HIL 工况把法国侧网络建得更细，用 FDNE 表示其余网络，功率设为 1000 MW 英国到法国，40 μs 步长；论文正文给出的 phase switching times 为 \(t_A=128\) ms、\(t_B=129\) ms、\(t_C=119\) ms，并报告最终 HVDC 永久 trip。normal 用 5 核，CM 用 8 核；在整站 trip 前，作者报告性能改善 30%。但两次实验的 energization event 与 replica state 不同步，波形存在平移，作者还承认 refactorization 数值误差可能参与其中，因此这个案例只能支持“响应相似且更快”，不能作严格逐点精度证明。[pdf:E11](_evidence/E11-p005-sec33-transformer-conclusion.png) Fig. 16–19 保留了拓扑切口、AC current、DC voltage 和最重 processor 执行时间的视觉证据。[pdf:E12](_evidence/E12-p005-fig16-fig19-transformer.png)

**不得外推的边界。** 作者进一步把 6-pulse bridge 内部也切开时，仿真变得不稳定；其解释是 \(Z_C\) 可能病态，固定 pivot 下的反复重分解会放大数值误差。因此实验结论不是“CM 可在任何位置无损切割”，而是“选择合适切口时可在这些 CPU 实时案例中换取明显速度收益”。[pdf:E08](_evidence/E08-p004-fig08-fig09-hvdc-sil.png)

### § 8 — Take-aways

**5 句话**

1. CM 用端口 Thévenin 等效把一个强耦合网络改写成“子网并行 + 小连接系统串行 + 电流补偿回注”。  
2. 它能填补 line-delay decoupling 在短线路、集中参数配电网和 converter station 内部没有天然时延的缺口。  
3. 600 节点线性配电网给出了最干净的结果：实时无 overrun 步长从 145 μs 降至 40 μs，报告 speed-up 3.63，误差仍是数值噪声量级。[pdf:E07](_evidence/E07-p003-table01-dist-results-hvdc-setup.png)  
4. 在 HVDC SIL 与 HIL 中也观察到 30%–40% 的报告性能收益和相近波形，但多次 refactorization 让误差明显高于线性案例。[pdf:E09](_evidence/E09-p004-fig10-fig12-hvdc-hil-limit.png) [pdf:E11](_evidence/E11-p005-sec33-transformer-conclusion.png)  
5. 决定方法成败的不是公式等价性，而是切点、\(Z_C\) 的条件性、串行补偿开销和同步负担能否同时受控。

**3 句话**

CM 把缺少传播时延的 EMT 网络切开，通过等效端口电流重新闭合物理约束。论文在配电网、HVDC switching、SIL 和实际控制保护 replica HIL 上证明了它能降低关键任务执行时间。它最危险的失败模式是病态补偿矩阵：继续加切口可能由加速转为误差放大和失稳。

**1 句话**

这篇论文的核心结论是：补偿法能把“没有天然时延所以不能并行”的 EMT 网络变成可实时并行的任务，但可用切口必须受数值条件约束。

### § 9 — 最脆弱的假设

最脆弱的假设是：**人工选择的切口会产生数值条件足够好的 \(Z_C\)，使补偿电流可稳定求解，而且这一条件在开关引起的反复矩阵更新中仍成立。** 如果该假设失效，端口电压中的微小舍入误差会经 \(Z_C^{-1}\) 放大成错误的补偿电流，再被回注所有子网；此时方法不只是“少一点加速”，而是直接破坏波形甚至使仿真发散。

论文对这个风险给出了非常关键但不充分的证据：IFA2000 中多次使用固定 pivot 重分解时，相对误差高于线性案例；进一步把 6-pulse bridge 切开则仿真不稳定，作者明确把病态矩阵列为原因，并提出未来研究 pivoting 与 scaling。[pdf:E08](_evidence/E08-p004-fig08-fig09-hvdc-sil.png) 结论也再次承认并非所有位置都能切，反复 refactorization 会增加数值误差。[pdf:E13](_evidence/E13-p005-sec4-conclusion-limit.png) 缺少的证据是：论文没有报告 \(Z_C\) condition number、pivot growth、误差随切点或切口数的系统曲线，也没有给出一个在运行前即可判定“安全切点”的阈值。

### § 10 — 最小复现实验

一周内最值得复现的是“线性场景中代数等价与加速是否同时出现”，而不是先复刻完整 IFA2000 HIL。

- **数据与模型：** 构造或取得一个约 600 节点的三相 20 kV feeder，线路用 R-L 集中参数，接到 63/20 kV 变压器；设置论文同型的 1 s、50 μs 仿真，并在 \(t=0.2\) s 施加 100 ms、1 mΩ 单相接地故障。若原 benchmark 不可得，应明确使用拓扑规模与元件类型匹配的替代模型，而不声称逐模型复现。[pdf:E06](_evidence/E06-p003-sec3-dist-setup-eq06.png)
- **实现：** 做 normal 单任务、一次 feeder-cluster cut 的 2-task CM，以及三次 cut 的 4-task CM；保持同一离散模型、solver tolerance 与 CPU affinity。实现两道 barrier，并单独记录子网解、补偿解和等待时间。
- **测量：** 比较 feeder-root 三相电流；按式 (6) 算点对点相对误差；统计平均、99.9 分位和最大 realized step time，以及 overrun 次数。再记录 \(Z_C\) condition number，作为论文未给但可解释失败的诊断量。
- **支持标准：** 以下门槛是本复现实验预先设定的判据，不是作者原文阈值：三种切分的峰值归一化误差不超过 \(10^{-8}\)，且 4-task CM 的 99.9 分位执行时间至少比 normal 低 30%，同时不增加 overrun。
- **反驳标准：** 在模型、步长和 solver 设置一致时，只要 CM 产生可重复的非数值噪声波形偏差、最大步长反而上升，或收益主要来自改变了模型/容差而不是并行本身，就反驳“线性网络可无精度代价加速”的核心 claim。

### § 11 — 最强反例设计

最强反例不是再找一个收益小的网络，而是主动构造作者已经暴露出的失稳边界：在 IFA2000 单个 6-pulse bridge 内部逐步增加 compensation cuts，让切口跨过会随 thyristor 状态变化的强耦合支路；在 deblocking、换相失败边缘与 transformer energization 期间同时记录 \(Z_C\) condition number、LU pivot growth、补偿电流幅值、相对误差、overrun 与是否失稳。

实验应比较三组 solver 策略：论文所述固定 pivot、带动态 pivoting 的 sparse LU、以及经端口 scaling 的求解。若在 normal 模型稳定时，CM 的 condition number 峰值先于补偿电流尖峰和波形发散出现，并且仅换 solver 策略就能移动失稳边界，那么“性能问题来自任务切分”这一替代解释就被削弱，而“病态连接系统导致失败”得到支持。反过来，如果 \(Z_C\) 一直良态但 barrier jitter 或最重子网负载决定 overrun，则论文把不稳定主要归因于 conditioning 的解释就不完整。这个反例直接攻击“理论上可任意切割”的工程可实现性，依据是作者已观察到 bridge 内进一步切分会不稳定。[pdf:E08](_evidence/E08-p004-fig08-fig09-hvdc-sil.png)

### § 12 — Follow-up Research Idea

**候选方向：把 EMT 并行切分重新定义为“带数值安全证书的实时网络 tearing”，而不是最大化任务数。** 未满足需求是：现有手工切分能产生明显加速，却没有办法在运行前或开关事件到来时判断某个切口会不会把 \(Z_C\) 推向病态；作者的实际失败已经说明“更多并行”与“可信实时结果”不是同一个目标。[pdf:E13](_evidence/E13-p005-sec4-conclusion-limit.png)

研究目标应联合优化三件事：最坏步长执行时间、barrier 后的串行补偿预算、以及可在线验证的误差放大上界。可借鉴 sparse numerical linear algebra 的 condition estimation 与 pivot-growth monitoring、graph partitioning 的动态边界选择，以及安全关键实时系统的 runtime assurance：每个候选切分不仅给出预计负载，还给出端口缩放后的 conditioning 证书；开关事件使证书失效时，运行时切回更保守的 tearing 或合并子网，而不是继续用已知危险的切口。

第一个可证伪实验是在同一组配电网、LCC deblocking 与 transformer-energization 工况上，比较“仅按负载均衡切分”和“带 conditioning 证书切分”。如果证书分数不能比简单的切口数或历史误差更早预测数值尖峰，或者安全重构的同步代价使最坏步长不降反升，那么这个方向失败。若成功，它改变的是问题定义：从“CM 能否加速”变成“能否在每个拓扑状态下证明当前并行分解仍满足实时性与数值可信性”。本文未做充分的跨论文检索，因此这里只把它标为证据约束的候选研究方向，不声称 novelty。
