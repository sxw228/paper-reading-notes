# Multi-FPGA digital hardware design for detailed large-scale real-time electromagnetic transient simulation of power systems

**作者：** Yuan Chen；Venkata Dinavahi [pdf:E01]  
**出处：** IET Generation, Transmission & Distribution, Vol. 7, Iss. 5, pp. 451–463 [pdf:E01]  
**年份：** 2013 [pdf:E01]  
**DOI：** 10.1049/iet-gtd.2012.0374 [pdf:E01]  
**Zotero key：** JCK2ZZKM  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“FPGA 能不能算一个电力元件”，而是更困难的系统问题：**能否用多片 FPGA 在严格实时期限内，对大规模电力系统做保留详细元件模型的 electromagnetic transient（EMT）仿真，同时不靠人为添加有传播时延的线路来切开网络。** 作者把目标落实为 3-FPGA 的 42-bus 系统和 10-FPGA 的 420-bus 系统，两者都采用详细线路、同步机和非线性元件模型，并在 100 MHz 时钟上执行。[pdf:E01]（PDF 物理页 1，title/abstract）

这里的“实时”不是泛指运行得快，而是每一个离散时间步的全部计算必须在下一个物理时间步到来前完成。EMT 需要跟踪电压、电流的瞬时波形；高频暂态越重要，时间步就越小。与此同时，frequency-dependent transmission line、八阶 universal machine（UM）和需要迭代的非线性避雷器又比简化模型昂贵得多。[pdf:E04]（PDF 物理页 3，Section 2.2.1–2.2.2，Eq. 1–5）[pdf:E05]（PDF 物理页 3，Section 2.2.3，Eq. 6–7）[pdf:E06]（PDF 物理页 4，Section 2.2.4–2.3，Eq. 8–10）因此，规模、模型细节和实时步长形成三角矛盾：牺牲细节会损失波形真实性，放大步长会漏掉快速暂态，而单纯增加顺序处理器又会引入通信和负载不均衡。

论文的重要性在于它试图改变这个矛盾的组织方式。作者不再先把电网按地域切成子网，再让处理器各算一块；而是先识别“线路、机器、非线性元件、RLCG、网络求解器”等计算类型，再让 FPGA 的空间并行和深流水直接服务这些类型。[pdf:E03]（PDF 物理页 2，Section 2.1、Fig. 1）如果这一思路成立，硬件增加带来的不只是更多顺序算力，而是更多同时工作的专用计算管线，从而给详细大系统 EMT 提供可扩展的实时执行路径。

## § 2 — 前人工作与不足

论文所处的现实基线是 RTDS、ARENE、HYPERSIM、NETOMAC、RT-LAB 等实时仿真器。它们主要依靠 DSP、PowerPC 或通用多核 CPU，并通过增加机架或集群节点扩展。已有并行方法通常利用真实线路或电缆的传播时延，把网络分成可在多个顺序处理器上同时计算的子系统。[pdf:E01] 这种方案已经能支持相当规模的实时 EMT，但作者指出四个直接限制：

1. 两个区域之间没有合适的真实延时线路、或电气耦合很强时，必须插入虚构线路；它会改变暂态的频率响应。
2. 子系统每步结束后仍需交换数据，通信时延侵占实时步长预算。
3. 分区边界常依赖经验和具体算例，难以形成与拓扑无关的系统方法。
4. 最大的不可再分子系统会成为全局瓶颈，造成处理器负载不均。[pdf:E02]（PDF 物理页 2，Introduction 的四项限制）

另一条旧路线是 frequency-dependent network equivalent：只详细模拟研究区，把外部系统压缩成拟合端口频率响应的 RLCG 等值。它能降低成本，但它改变了“原系统全部保留详细模型”的问题定义。[pdf:E02] 本文所批评的并非这些方法完全无效，而是它们的扩展单位仍然是电气子网，扩展性受可用分割边界约束。

在 FPGA 方向，作者承认已有单片 FPGA 上的 EMTP、详细电力电子装置、universal line、universal machine 和非线性 EMT solver 工作；本文引用的直接技术前身也主要来自同一研究团队。作者声称，在其检索范围内，此前 FPGA 暂态实现局限于小规模单 FPGA，尚未报道以多 FPGA 做详细大规模实时 EMT。[pdf:E01] 这项 claim 应理解为论文在 2012 年投稿时的文献定位，而不是今天仍然成立的 novelty 判断。

## § 3 — 重建作者的思考路径

下面是基于论文背景证据的逆向重建，不是作者逐字给出的研发日志。

第一步，研究者会发现传统分区依赖一个电气事实：边界线路的传播时延可以让两侧在一个时间步内解耦。但这也意味着“哪里能并行”由电网拓扑决定，而不是由硬件能力决定；当不存在合适边界时，只能插入会扰动频率响应的人工线路。[pdf:E02]

第二步，把视角从电网的地理位置转向每步真正执行的算子。不同区域都在重复做少数几类工作：RLCG history-current 更新、ULM 卷积、UM 电气与机械状态更新、非线性 Newton–Raphson（NR）迭代、开关处理和节点方程求解。[pdf:E04] [pdf:E05] [pdf:E06] 同类算子的控制流和数据格式相似，因而适合做成固定硬件 pipeline；多个同类元件可以像流水线上的工件一样逐拍进入。

第三步，FPGA 的价值就不再只是“比 CPU 快”，而是它允许两级并行：不同功能模块同时工作；一个模块内部的多相、多端或多个算术单元也同时工作。若把一个函数分成 \(n\) 级流水并送入 \(m\) 组数据，作者给出的处理时间是 \(n+m\) 个时钟周期，而非非流水实现的 \(m\times n\) 个周期。[pdf:E08]（PDF 物理页 5，Fig. 3、Section 3）

第四步，单片 FPGA 的资源不足会自然把问题推向多 FPGA。以 Stratix III EP3SL340 为例，ULM 单模块约占 44,610 个 combinational ALUT、96 个 18-bit multiplier 和 707.27 kbit memory，是表中最重的功能模块；若要复制足够多条管线来承载大系统，必须扩展到多片器件。[pdf:E07]（PDF 物理页 4，Table 1）

因此，一个合理的思考终点是：**按功能复制硬件模块，用流水深度容纳元件数量，用模块数量增加吞吐，再用少量跨 FPGA 的节点电压、补偿电压和 history-current 数据把功能链闭合。** 这就是 functional decomposition。它不是从论文贡献倒推出来的口号，而是从“拓扑分区不稳定”和“同类算子高度重复”两个先验事实相交得到的设计选择。

## § 4 — 核心 Intuition

这篇论文的核心 intuition 是：大规模 EMT 的可并行对象不必是“电网的一块”，也可以是“全网中一种计算功能”。把所有线路交给 ULM pipelines、所有机器交给 UM pipelines、所有非线性元件交给 NR pipelines，网络原始拓扑就不必为了硬件并行而被人为改写。[pdf:E03]

物理上仍然是同一个电网通过节点电压和注入电流耦合；改变的只是每个时间步内计算这些物理量的空间布局。FPGA 复制的模块越多，同类元件并行吞吐越大；同一模块中流水的元件越多，面积越省但时间步越长。这一“面积—步长—规模”交换关系是整篇论文的轴心。[pdf:E08] [pdf:E13]（PDF 物理页 10，Fig. 9）

## § 5 — 具体方法与完整 Pipeline

以 Case study I 的 42-bus 系统为例，可以把一次仿真步重建为下面的完整 pipeline。

1. **把连续元件变成离散 Norton/补偿形式。** 线性 RLCG 用梯形积分写成等效 conductance \(G\) 加上一拍历史电流 \(i_{h\mathrm{RLCG}}\)；frequency-dependent phase-domain ULM 用特性导纳矩阵 \(Y_c\) 和传播函数矩阵 \(H\) 的有限阶有理拟合，产生两端 history-current 卷积。[pdf:E04] UM 采用八阶模型，在 \(dq0\) 坐标计算电气量和机械转速，再变回 \(abc\) 注入网络。[pdf:E05] 非线性避雷器则用补偿法把线性网络的 Thévenin 关系与 \(v=f(i)\) 交给 NR 迭代。[pdf:E06]
2. **按功能而不是按区域映射。** FPGA0 放 5 个 ULM modules；FPGA1 放 6 个 UM modules 和 2 个 NR modules；FPGA2 放 16 个 Network Solver、8 个 RLCG、1 个 Switch 和 1 个 Control module。[pdf:E08] 这种放置也有通信工程约束：同类模块尽量在同一 FPGA，紧密相关模块放相邻 FPGA，非相邻传输经相邻器件转发，避免引脚数和 I/O bandwidth 先于算术资源耗尽。[pdf:E08]
3. **把真实系统元件装入 pipelines。** 42-bus 算例含 35 条三相 ULM 线路、10 台三相 UM 发电机、19 个三相负载、11 个三相变压器、总计 99 个 RLCG 元件、3 个非线性避雷器和 126 个网络节点。[pdf:E10]（PDF 物理页 7，Table 2、Section 3.1）35 条线路平均装入 5 个 ULM pipelines，每个 7 条；10 台机器装入 UM modules，每个最多 2 台；99 个 RLCG 分给 8 个模块；126 个节点分给 16 个 Network Solver。[pdf:E10]
4. **Period I：先解线性网络。** Network Solver 由当前线路和 RLCG history currents 组装注入向量，用预计算的 \(Y^{-1}\) 做 sparse matrix–vector multiplication 得到尚未计入机器和非线性元件的节点电压 \(v_n\)。论文同时说明，资源足够时也可用实时 LU decomposition 加 forward/backward substitution，但算例采用预计算逆矩阵路线。[pdf:E06]
5. **Period II：做补偿与非线性迭代。** \(v_n\) 送到 UM 和 NR modules。机器电流从 \(dq0\) 计算后回到 \(abc\)，非线性电流通过 NR 求解，再叠加回网络得到 compensated voltage \(v_c\)；与此同时，ULM pipelines 已开始计算部分卷积。[pdf:E06] Fig. 4 的时空排程显示，本算例 Period I 为 0.64 μs，Period II 由平均三次 NR 迭代主导，为 6.21 μs。[pdf:E09]（PDF 物理页 6，Fig. 4b）
6. **Period III：更新历史项。** RLCG、UM 和 ULM 更新下一拍使用的历史量；该阶段由 ULM 路径主导，为 4.70 μs。三段合计形成 11.55 μs 的最小实时步长。[pdf:E09]
7. **扩大到 10 FPGA。** Case study II 保留 FPGA0–FPGA2 的角色，增加 FPGA3 承载另一组 UM/NR，并让 FPGA4–FPGA9 复制 ULM modules。最终映射为 35 个 ULM modules 处理 376 条线路、8 个 RLCG modules 处理 990 个 RLCG；FPGA1 与 FPGA3 各放 6 个 UM modules 和 2 个 NR modules，合计处理 100 台发电机和 30 个非线性元件；16 个 Network Solver 处理 1260 个节点。[pdf:E12]（PDF 物理页 9，Fig. 8）
8. **输出与对照。** 设计用 VHDL 在 Quartus II 中综合、布局布线并下载到 DN7020k10；各 FPGA 工作于 100 MHz，实时波形经 125 MSPS DAC 输出到示波器，离线基线为 EMTP-RV。[pdf:E08] [pdf:E11]（PDF 物理页 8，Section 3.1–3.2、Fig. 6）

论文采用 IEEE 32-bit floating-point 表示，而不是为节省资源改用未经说明的低精度定点数；但开关处理只报告理想 time-controlled switch，没有展示电力电子高频开关网络、插值开关时刻或 substep 事件处理。[pdf:E01] [pdf:E06] 多速率只被指出在功能分组下“自然可行”，两个案例实际都使用单一时间步。[pdf:E03] [pdf:E14]（PDF 物理页 11，Section 3.3、Eq. 11–13、Conclusions）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学不是为了提出新的积分公式，而是为了说明每类 EMT 算子如何变成可流水、可复制的硬件接口。

### 6.1 统一的“导纳 + 历史源”

对 R、L、C、G 及其组合使用梯形积分后，端口关系写成

\[
i(t)=Gv(t)+i_{h\mathrm{RLCG}}(t-\Delta t).
\]

这里 \(G\) 是本步的等效 conductance，\(i_h\) 把上一拍状态折叠成电流源。[pdf:E04] 工程意义是：无论元件内部是否含储能，它交给网络求解器的接口都变成“当前电压的线性项 + 已知 history current”。这正是按功能批量送入流水线的前提。

### 6.2 Frequency-dependent ULM

ULM 先在频域用有限阶有理函数拟合特性导纳矩阵和传播函数：

\[
Y_{c,(i,j)}(s)=\sum_{m=1}^{N_p}\frac{r_{Y_c,(i,j)}(m)}{s-p_{Y_c}(m)}+d_{(i,j)},
\]

\[
H_{(i,j)}(s)=\sum_{k=1}^{N_g}\left(\sum_{n=1}^{N_{p,k}}
\frac{r_{H,(i,j),k}(n)}{s-p_{H,k}(n)}\right)e^{-s\tau_k}.
\]

\(N_p\) 是极点数，\(r\)、\(p\)、\(d\) 分别为 residue、pole 和 proportional term；\(N_g\) 是传播模态数，\(\tau_k\) 是第 \(k\) 个模态的时延。[pdf:E04] 时域端口仍呈导纳加 history-current 的形式，两端历史源由 \(Y_c\) 卷积本端电压、并用 \(H\) 卷积另一端延时电流得到。[pdf:E04] 这使线路最昂贵的有理函数状态更新可以由专用 ULM pipeline 连续吞吐。

### 6.3 UM 与补偿迭代

八阶 UM 的电气侧在同步旋转 \(dq0\) 坐标中写为

\[
\mathbf v_{dq0}(t)=-\mathbf R\mathbf i_{dq0}(t)
-\frac{2}{\Delta t}\boldsymbol{\lambda}_{dq0}(t)
+\mathbf u(t)+\mathbf v_{\mathrm{hist}},
\]

机械侧满足

\[
T_m=J\frac{d\omega}{dt}+D\omega+T_e.
\]

其中 \(\mathbf v,\mathbf i,\boldsymbol{\lambda},\mathbf R,\mathbf u\) 分别为绕组电压、电流、磁链、电阻和 speed-voltage 向量；\(J,D,\omega,T_m,T_e\) 分别为转动惯量、阻尼、转速、负载转矩和 air-gap torque。[pdf:E05] 网络先给出不含机器补偿的 \(v_n\)，UM 再产生电流注入并迭代求 \(v_c\)。直观上，这是用“先解容易的线性骨架，再用端口补偿把复杂元件接回来”避免把整网一次性塞进一个巨大的非线性求解器。[pdf:E06]

对非线性端口，论文联立

\[
v=v_n-R_{\mathrm{thev}}i,\qquad v=f(i),
\]

并以

\[
J(i^{k+1}-i^k)=v_n-R_{\mathrm{thev}}i^k-f(i^k)
\]

执行 NR 更新，其中 \(R_{\mathrm{thev}}\) 是端口看到的 Thévenin resistance，\(J\) 是 Jacobian；线性子问题由 parallel Gauss–Jordan elimination 求解。[pdf:E06]

### 6.4 网络方程与时间预算

网络求解器每步求

\[
\mathbf Y\mathbf v_n=\mathbf i.
\]

算例通过预计算各 switching event 对应的 \(\mathbf Y^{-1}\)，再做 sparse matrix–vector multiplication。[pdf:E06] 整个仿真步的 deadline 模型是

\[
\Delta t=t_{p1}+t_{p2}+t_{p3},
\]

\[
t_{p1}=t_{\mathrm{NW}},\quad
t_{p2}=\max(t_{\mathrm{ULM}},t_{\mathrm{UM}},t_{\mathrm{NR}})_{p2},\quad
t_{p3}=\max(t_{\mathrm{ULM}},t_{\mathrm{UM}},t_{\mathrm{RLCG}})_{p3}.
\]

同一 period 内不是把各模块时间相加，而是取最长者，因为模块并行工作；三个 period 之间存在依赖，所以必须相加。[pdf:E14] 对 ULM，作者给出

\[
t_{\mathrm{ULM}}=(34+8N_{\mathrm{line}})T_f,
\]

其中 34 是 pipeline latency，\(N_{\mathrm{line}}\) 是每个模块流水处理的线路数，\(T_f=10\) ns 是 FPGA 时钟周期；系数 8 建立在线路拟合阶次假设上。[pdf:E14] 这条式子把核心 trade-off 定量化：增加 ULM module 会降低每个模块的 \(N_{\mathrm{line}}\)，因而缩短时间步，但消耗更多 FPGA 面积和跨片连接。

## § 7 — 实验设计与结论

### 问题一：详细模型在多 FPGA 上能否按 deadline 运行？

**实验。** 作者在 DN7020k10 上实现 3-FPGA 的 42-bus/126-node 算例，使用 35 条 ULM 线路、10 台 UM 发电机、99 个 RLCG 元件和 3 个非线性避雷器。[pdf:E10] 设计综合后的资源利用率显示 FPGA0/1 的 logic utilisation 分别为 96%/80%，DSP 利用率为 83%/97%；三片设计统一运行于 100 MHz。[pdf:E10]

**答案。** 最小步长为 11.55 μs，其中 Network Solver 为 0.64 μs，平均三次 NR 迭代所在 Period II 为 6.21 μs，history update 所在 Period III 为 4.70 μs。[pdf:E09] 论文还报告同一系统在 AMD Phenom II 955、3.2 GHz、4 cores、16 GB 的 PC 上用 EMTP-RV 以 12 μs 仿真步执行时，每步计算需 192 μs。[pdf:E11] 这支持“该特定 FPGA 映射满足实时 deadline”，但不能直接解释为与现代 CPU 的普遍性能比较。

### 问题二：实时波形是否保持离线 EMT 的主要行为？

**实验。** 在 \(t=0.05\) s 对 Bus 2 施加三相接地故障，通过 125 MSPS DAC 和示波器采集 Bus 1 三相电压，并与 EMTP-RV 波形并列。[pdf:E11]

**答案。** 两者都显示约两个周波的暂态，峰值由约 20 kV 降到约 15 kV，图示波形的主要形态相近。[pdf:E11] 但论文没有报告 sample-by-sample 误差、相位误差、NR residual、能量误差或统计指标；因此它验证的是定性波形一致性，而不是严格的数值等价。

### 问题三：增加 FPGA 能否承载更大系统？

**实验。** 作者把 Case study I 复制十次并用线路互连，形成 420-bus/1260-node 系统；映射到 10 FPGA 后，包含 376 条 ULM 线路、100 台 UM 发电机、990 个 RLCG 和 30 个非线性元件。[pdf:E11] [pdf:E12]

**答案。** 10-FPGA 设计在 100 MHz 下达到 36.12 μs 最小步长，EMTP-RV 离线每步为 2120 μs。[pdf:E14] 系统规模增大十倍而 FPGA 数从 3 增至 10，仍能实时，但时间步从 11.55 μs 增到 36.12 μs；这说明可扩展不等于线性 scaling。

### 问题四：规模、步长和 FPGA 数量怎样交换？

**实验。** 作者用各功能模块 latency 与每模块 pipeline 元件数的关系，外推 3-FPGA 和 10-FPGA 的 \(\Delta t_{\min}\)–node 曲线及三变量表面。[pdf:E13] [pdf:E14]

**答案。** 图与正文给出的例子是：若详细模型使用 50 μs 步长，3-FPGA 可承载约 850 nodes，10-FPGA 可承载约 1860 nodes；固定系统规模时增加 FPGA 会缩短步长，但边际收益递减。[pdf:E14] 这是由模块 timing model 推得的 capacity estimate，不是对图上每个规模点都做了真实硬件仿真。论文的真实硬件证据集中在两个端点案例。

## § 8 — Take-aways

### 5 句话

1. 论文把大规模 EMT 的并行单位从“电气子网”改成“计算功能”，因而不必为了分区插入虚构延时线路。[pdf:E02] [pdf:E03]
2. RLCG、ULM、UM、NR 和 Network Solver 被做成可复制、可深流水的硬件模块，模块间和模块内同时利用 FPGA parallelism。[pdf:E06] [pdf:E08]
3. 3-FPGA/126-node 案例在 100 MHz 下达到 11.55 μs，10-FPGA/1260-node 案例达到 36.12 μs。[pdf:E09] [pdf:E14]
4. 三相故障波形与 EMTP-RV 的主要形态相近，但论文只给定性对照，没有严格误差指标。[pdf:E11]
5. 论文证明了两套具体映射可实时运行；对任意拓扑、密集 switching event 和更大集群的“fully scalable”结论仍主要来自 timing model 外推。[pdf:E13] [pdf:E14]

### 3 句话

1. 最有价值的贡献是 functional decomposition：让硬件结构跟随算子类型，而不是迫使物理网络跟随处理器边界。[pdf:E03]
2. 最扎实的证据是可综合的资源表、明确的三段 deadline 和两套真实多 FPGA 案例。[pdf:E07] [pdf:E09] [pdf:E12]
3. 最需要谨慎的是 scalability：两个案例不足以覆盖任意网络拓扑、开关状态数量、NR 收敛次数和跨片通信压力。

### 1 句话

这篇论文说明多 FPGA 可以靠“功能专用流水 + 受控的数据交换”实时运行详细大系统 EMT，但它尚未给出对最坏事件工况的 deadline 保证。

## § 9 — 最脆弱的假设

最脆弱的假设是：**当系统继续扩大或拓扑变得更复杂时，跨 FPGA 数据搬运、全局 Network Solver 和非线性迭代仍不会取代功能 pipelines 成为不可控的最坏步长瓶颈。**

这个假设一旦失效，论文最核心的“通过复制功能模块实现可扩展详细实时 EMT”就会失效。原因有三层。第一，functional decomposition 把全网同类元件集中后，线路 history currents、\(v_n\) 和 \(v_c\) 必须跨片流动；算术流水可复制，板级引脚和拓扑却不同比例扩展。论文自己承认相邻 FPGA 最多共享 220 pins，并制定了同类同片、相关模块相邻、非相邻转发的规则，说明通信不是次要细节。[pdf:E08] 第二，算例的 Network Solver 使用预计算的 \(Y^{-1}\)；当 breaker 状态组合很多时，预存多个逆矩阵的容量和更新方式可能成为限制。[pdf:E06] 第三，3-FPGA deadline 中 NR 已在“平均三次迭代”下占 6.21 μs，是三段中最大的部分；强非线性或困难初值会直接延长最坏步长。[pdf:E09]

论文为这个假设提供的证据是：一块 10-FPGA 板上，两套具体映射在统一 100 MHz 时钟下达成实时，且模块 latency 与 pipeline 元件数呈可建模关系。[pdf:E12] [pdf:E13] 缺少的证据则更关键：没有最坏 NR 迭代次数分布，没有同步开关事件 burst，没有任意 meshed topology 与非复制系统的硬件案例，没有跨板 FPGA cluster 的实测，也没有 communication utilisation 或 deadline slack 的逐步记录。因而“fully scalable and extensible”应视为基于这两个案例的工程推断，而非已覆盖最坏工况的证明。[pdf:E14]

## § 10 — 最小复现实验

如果只有一周，我不会试图重做完整 420-bus 系统，而会复现论文最关键、也最容易证伪的局部 claim：**按功能流水后，一个时间步的实际硬件 latency 是否能由三段 max-plus 模型预测，并稳定小于设定 \(\Delta t\)。**

实验使用论文 Appendix 的线路、同步机、避雷器、负载和变压器参数作为一个 42-bus reference workload；其中 ULM 使用 \(Y_c\) 九阶、\(H\) 十三阶有理拟合，避雷器使用 \(q=6\)、\(V_{\mathrm{ref}}=8192\) V、\(p=600\) A，负载为 \(R=500\,\Omega,L=0.05\) H、\(C=1\,\mu\mathrm F\)。[pdf:E15]（PDF 物理页 13，Appendix、Table 3）不必一周内重建所有物理 I/O，只需做三个可综合 RTL microbench：16-lane sparse Network Solver、一个承载 7 条线路的 ULM pipeline、一个带可控迭代次数的 NR/UM compensation pipeline。离线 EMT 程序预生成每拍输入向量和期望输出，RTL 回放同一向量。

测量四组量：每个模块从 valid-in 到 valid-out 的 cycle count；三个 period 的真实最大 latency；浮点输出相对离线参考的误差与 NR residual；在 1、3、5、8 次 NR 迭代下是否 miss deadline。论文的原始目标点是 \(t_{p1}=0.64\) μs、\(t_{p2}=6.21\) μs、\(t_{p3}=4.70\) μs、总步长 11.55 μs（100 MHz）。[pdf:E09]

支持 claim 的标准是：综合后至少连续回放 \(10^6\) 个时间步无 deadline miss，实测 \(\Delta t\) 与公式预测误差不超过一个 pipeline flush/handshake 常数，并且浮点结果在预先约定的误差阈值内。反驳标准是：通信或仲裁使 latency 随模块并发显著偏离 max 模型；或 NR 次数稍增就频繁超过 11.55 μs；或输出误差无法用 IEEE 32-bit rounding 解释。这个复现不证明完整系统正确，却能直接检验论文扩展方法依赖的 timing contract。

## § 11 — 最强反例设计

最有力的反例不是再换一个更大的平稳网络，而是构造一个**计算规模相同、但全局耦合和事件并发远高于两个案例的 1260-node meshed system**。让大量 breaker 在相邻几个时间步内同步切换，同时让多组 surge arrester 进入强非线性区，并选择使 UM compensation 初值较差的故障清除序列。系统节点数、FPGA 数和 100 MHz 时钟保持不变，以排除“只是硬件更少”的解释。

这个攻击同时打击三处隐含余量：

- 大量 switching state 迫使 Network Solver 处理新的或频繁切换的 \(\mathbf Y\)/\(\mathbf Y^{-1}\)；
- 同步事件使 \(v_n\)、\(v_c\) 和 history-current 的跨片流量在同一步聚集；
- 避雷器强导通和机器暂态使 NR 超过 Case study I 的平均三次迭代。[pdf:E06] [pdf:E09]

记录每一步的 Network Solver、跨片传输、NR、ULM latency 和总 deadline，并用 EMTP-RV 或双精度离线实现给出节点波形与 residual 基线。若这个与原案例节点数相同的系统在 36.12 μs deadline 下出现不可消除的 miss，或必须插入额外延时/简化模型才能运行，那么“scalability 主要由 node count、FPGA count 和 nominal time-step 决定”的解释就被推翻；真正的决定变量还包括 event concurrency、迭代难度、拓扑变化熵和通信 cut。论文的 Fig. 9 三变量表面没有包含这些维度。[pdf:E13] [pdf:E14]

## § 12 — Follow-up Research Idea

在实时 EMT 与硬件仿真领域，高影响研究通常不只看单个算例速度，还看数值可信度、最坏 deadline、可实现资源、可重复性，以及在真实 protection/control HIL 场景中的价值。基于第 9 节，候选研究方向是：**从“按平均元件数规划吞吐”转向“事件感知、通信受约束、具有 worst-case deadline certificate 的分布式 EMT solver”。** 由于本卡没有做 2013 年之后的完整相关工作检索，下面只称候选想法，不声称 novelty。

**（a）未满足的需求。** 现有设计用 node count、FPGA count 和 time-step 描述容量，却不能回答“最坏故障、同步开关和 NR 难收敛时，这一步一定不会超时吗”。保护装置闭环测试需要的恰恰是异常事件下的确定性，而不是平均工况吞吐。

**（b）研究价值。** 新目标不是再把同一系统复制更多次，而是在给定硬件上最大化一组有明确事件集合的**可认证系统规模**：对允许的 breaker event、非线性区间和迭代上限，给出每步 latency 上界、数值 residual 上界和 deadline slack。它把性能 claim 从两个 benchmark 点提升为可审计的实时保证。

**（c）相邻领域工具。** 可以借鉴 real-time systems 的 worst-case execution time（WCET）与 network calculus，为跨 FPGA flow 分配时隙；借鉴 distributed sparse linear algebra 的 Schur complement 或 domain decomposition，把全局 Network Solver 拆成带显式接口规模的局部求解；再用 event-triggered incremental factorisation 只更新受开关变化影响的矩阵块。它保留 functional decomposition 的专用 pipelines，但不再假设数据移动和 \(\mathbf Y^{-1}\) 管理会自然缩放。

**（d）首个证伪实验。** 在相同 10 FPGA、相同 1260 nodes 下，同时运行原论文式映射与新 solver，施加 §11 的同步 breaker/arrester stress workload。若新方法不能在所有测试步内给出更小的真实 worst-case latency，或者为保证 deadline 导致离线波形误差超过预注册阈值，就立刻否定该方向；平均速度提升不算通过。

**（e）与本文的实质区别。** 本文的主要设计变量是每类功能模块的复制数与每 pipeline 的元件数，时间模型依赖各 period 内的最大模块 latency。[pdf:E14] 候选工作把“事件引起的矩阵变化、迭代次数和跨片拥塞”提升为一等建模对象，并把研究目标从 nominal scalability 改为 adversarial event 下的 deadline-certified fidelity。这不是给原设计附加一个监控模块，而是重新定义什么叫“能实时模拟这个系统”。
