# A Direct Mapped Method for Accurate Modeling and Real-Time Simulation of High Switching Frequency Resonant Converters

- 作者：Hossein Chalangar；Tarek Ould-Bachir；Keyhan Sheshyekani；Jean Mahseredjian
- 出处：IEEE Transactions on Industrial Electronics
- 年份：2021
- DOI：10.1109/TIE.2020.2998746
- Zotero key：8BIZE27F

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

### § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样把 LLC 电路方程写出来”，而是一个实时性与物理可信度正面冲突的问题：高开关频率 resonant converter 的谐振周期短，FPGA 实时仿真必须采用很小的计算步长；但每个步长内，二极管状态又与网络解互相依赖，可靠的 Resistive Switch Model（RSM）通常要迭代求状态。迭代次数不可预先固定，就难以给 Hardware-in-the-Loop（HIL）一个确定的硬实时 deadline。作者把目标压缩成一句话：在保留 RSM 与隐式离散精度的前提下，消除在线二极管状态迭代。论文摘要报告其 FPGA LLC 实现覆盖至 500 kHz，并达到 25 ns 仿真步长。[pdf:E01](_evidence/E01-p001-abstract-introduction.png)

物理上的难点来自 LLC 的“阻断区”。在一个半谐振周期的末尾，谐振电流可能全部流入励磁支路，整流桥输入电流接近零；此时四个整流二极管都应关断。只按电流正负二选一地决定整流桥正、负导通状态，会把本应无功率送往负载的区间错误地解释成频繁换向。论文以完整 LLC 拓扑、增益曲线和两个谐振频率说明这一工作区间；它不是数值实现的小细节，而是谐振腔能量在励磁支路与负载之间怎样流动的物理模式。[pdf:E02](_evidence/E02-p002-fig01-02-eq01-02.png)

因此，这项工作的工程价值有两层。第一层是 fidelity：避免开关等效模型或显式近似制造虚假振荡、漏掉阻断/短路状态。第二层是 determinism：把每一步的工作量变成固定的 Matrix-Vector Multiplication（MVM）、符号判断与 lookup，使 FPGA 可以给出可综合、可流水化的最坏执行时间。这里的“准确”首先是“相对同一理想化 RSM/Backward Euler（BE）模型的离线迭代解准确”，并不等同于已经证明对真实器件寄生、反向恢复和控制 I/O 都准确。

### § 2 — 前人工作与不足

作者把既有开关建模分成两条主线。Associated Discrete Circuit（ADC）可以保持固定网络矩阵，适合实时计算，但在高频 power electronic converter 中会出现 fictitious oscillation；为 ADC 加补偿又会改变谐振腔行为。RSM 用 \(R_\mathrm{on}\simeq 0\)、\(R_\mathrm{off}\gg 0\) 的两值电阻表达开关，物理结果通常更好，却让导纳矩阵随开关状态改变，并把自然换流器件的状态判定带回在线迭代。[pdf:E01](_evidence/E01-p001-abstract-introduction.png)

围绕 RSM，论文列出的已知折中都没有同时满足高频、准确和固定计算量：

- 预存所有开关组合的逆矩阵会随开关数指数增长，受 FPGA memory 限制；在线用 Sherman-Morrison-Woodbury 更新逆矩阵仍太重，而且没有消除二极管状态迭代。
- 给开关并联非真实寄生元件会改变 resonant converter；network tearing 的步长偏大；predictor-corrector 为稳定性需要更短步长，并随电路规模增加硬件；已有 iterative RSM 工作主要面向较低频率。[pdf:E01](_evidence/E01-p001-abstract-introduction.png)
- 针对 LLC 的已有 FPGA 结果中，作者点名 20 kHz 的商业实时仿真、60 kHz 的模块拆分法及 160 kHz/15 ns 的 Forward Euler（FE）法。模块内延迟可能产生错误；FE 虽省掉迭代，却不是对参数稳健的通用解。[pdf:E02](_evidence/E02-p002-fig01-02-eq01-02.png)

论文最有说服力的 prior-method 失败证据不是文献评价，而是同一 LLC 上的直接比较：在 15 ns 步长下，FE 在两个参数组的阻断区都出现振荡；对 500 kHz 的 Parameter Set #2，FE 与迭代 BE 的整体波形也明显偏离。作者还报告 FE 在 \(\Delta t\ge 30\) ns 时失稳，并指出仅用正、负两种整流状态还漏掉全关断与四管全导通两种可行模式。[pdf:E03](_evidence/E03-p003-fig03-04-table01-eq03-04.png) [pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)

### § 3 — 重建作者的思考路径

下面是基于论文证据对作者思路的逆向重建，不是作者逐字给出的研究日志。

第一步，保留 BE + RSM，因为 BE 的 Norton equivalent 同时给出支路电导和由上一时刻储能形成的 history current；它不像把电感侧简化成纯电流源的 FE 那样天然抹掉一部分状态。第二步，把“二极管状态未知”改写成“给定一种候选状态时，它是否自洽”：对候选 \(\sigma_\mathrm{rec}\)，节点电压满足

\[
\mathbf Y^{\sigma_\mathrm{rec}}\mathbf v_n=\mathbf B\mathbf i^h,
\qquad
\mathbf v_d=\mathbf T(\mathbf Y^{\sigma_\mathrm{rec}})^{-1}\mathbf B\mathbf i^h .
\]

也就是说，二极管电压符号最终只是两个 history current \((i_1^h,i_2^h)\) 的线性不等式。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)

第三步，不在运行时反复猜 \(\sigma_\mathrm{rec}\)，而是在离线阶段对 16 种二极管组合做 feasibility 检查。Fourier-Motzkin elimination 显示只有四种组合可行：Blocked \((0,0,0,0)\)、Positive \((1,0,0,1)\)、Negative \((0,1,1,0)\) 和 Shorted \((1,1,1,1)\)。这四种模式在 \((i_1^h,i_2^h)\) 平面中是由四条过原点的半直线分开的四个区域，于是“迭代求开关状态”变成“判断当前点落在哪个区域”。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)

第四步，作者再追问为什么 FE 会漏掉阻断模式。区域边界的斜率满足

\[
m_1=\frac{g_\mathrm{off}+g_2}{g_\mathrm{off}+g_1}\simeq\frac{g_2}{g_1},
\qquad
m_2=\frac{g_\mathrm{on}+g_2}{g_\mathrm{on}+g_1}.
\]

显式法把 AC 侧 Norton equivalent 近似成纯电流源，相当于令 \(g_1=0\)，于是 \(m_1\to\infty\)，Blocked 区域在几何上被挤掉。这把 Fig. 3–4 的振荡从“某组参数不好用”解释成了可定位的结构性原因。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)

### § 4 — 核心 Intuition

DMM 的核心不是更快地迭代，而是证明在所建模的整流桥中，二极管模式已经被两个 BE history current 充分决定。作者把在线求解从“解网络—猜状态—再解网络”改成“对两个电流做四个符号判断—查表选状态—执行预计算 MVM”，把不可预测的迭代变成固定延迟的组合逻辑。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png) [pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)

从物理上看，这相当于提前画出整流桥在能量状态平面中的换流边界；运行时只需定位当前能量历史落在哪个区域，而不再用局部正负号粗暴猜测。

### § 5 — 具体方法与完整 Pipeline

以论文的全桥 LLC 为例，输入是直流母线电压 \(u(t)=v_\mathrm{DC}(t)\)、逆变器门极信号 \(c(t)\)、上一时刻 AC/DC history current，以及由电容、电感储能形成的离散状态；输出是 \(v_o(t),i_r(t),i_m(t)\) 和下一步 history current。

1. **BE 离散与 MANA 建模。** 对所有 \(L/C\) 元件采用 BE，把 AC 与 DC 两侧写成 Norton equivalent；用 Modified Augmented Nodal Analysis 得到每个总开关组合 \(\sigma\) 对应的矩阵 \(\mathbf A^\sigma\)。矩阵逆及由它导出的 \(\mathbf H^\sigma\) 系数均离线预计算，在线不做矩阵求逆。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)
2. **受控逆变桥状态。** 门极信号直接给出 \(\sigma_\mathrm{inv}(c)=6\)（\(c=0\)）或 \(9\)（\(c=1\)）。由输入与历史量计算整流桥两侧的 \(i_1^h,i_2^h\)。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)
3. **DMM 状态分类。** 运行时计算

   \[
   \begin{bmatrix}p_1\\p_2\\p_3\\p_4\end{bmatrix}
   =
   \operatorname{sgn}\!\left(
   \begin{bmatrix}
   -m_1&1\\
   +m_1&1\\
   -m_2&1\\
   +m_2&1
   \end{bmatrix}
   \begin{bmatrix}i_1^h\\i_2^h\end{bmatrix}
   \right).
   \]

   四种特定符号对分别查表得到 \(\sigma_\mathrm{rec}\in\{0,6,9,15\}\)，再拼成 \(\sigma=16\sigma_\mathrm{inv}+\sigma_\mathrm{rec}\)。这里的 0/6/9/15 是四位二极管状态字，不是连续物理量。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)
4. **状态推进。** 按所选 \(\mathbf H^\sigma\) 做第二个 MVM，同时更新 \(i_\mathrm{ac}^{hist}\)、\(i_\mathrm{dc}^{hist}\) 和输出 \(\mathbf y=[v_o,i_r,i_m]\)。原始 Two-Stage algorithm 因 \(\sigma(t)\) 的数据依赖而串行执行两个 MVM。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)
5. **Single-Stage 重写。** Eq. (31) 把本步 DMM 所需的 history current 改写为 \(u(t)\) 与上一时刻 \(u,\sigma,i_\mathrm{ac}^{hist},i_\mathrm{dc}^{hist}\) 的函数，切断两个 MVM 的同一步串行依赖。代价是输出要经过两个仿真步才出现；收益是 initiation interval 可以减半。Fig. 7–9 的硬件几乎一对一映射这一数据流：一个输出/历史更新 MVM，一个 DMM MVM，加一个 LUT 与无成本的位拼接。[pdf:E06](_evidence/E06-p006-fig07-09-eq31.png)
6. **FPGA 数值与并行。** 每个 \(n\times m\) MVM 由 \(N\times m\) 个 ROM 和 \(N\) 个 \(m\)-input dot-product 单元组成；\(N\) 决定完全并行还是 time-multiplexed hardware reuse。正文称采用 per-unit 缩放的 fixed-point，向量为 FXP 25.23、矩阵为 FXP 35.29；但 Table III 又列 FXP 32.29/25.22，论文内部没有解释这一差异，不能据此唯一重建最终 bit format。[pdf:E07](_evidence/E07-p007-table02-fig10-fpga-design.png) [pdf:E08](_evidence/E08-p008-fig11-table03-04-eq32.png)

论文没有报告 HDL 源码、ROM 系数生成脚本、定点溢出/舍入策略、接口协议或 host/FPGA 数据搬运时序。这些应视为未报告，而不是 DMM 自动解决的部分。

### § 6 — 核心数学推导（无形式化数学则跳过）

数学主线可以压缩成“网络解 → 二极管电压符号 → 可行区域 → 直接分类”。

首先，对给定整流状态 \(\sigma_\mathrm{rec}\)，BE-Norton 网络是线性的：

\[
\mathbf Y^{\sigma_\mathrm{rec}}\mathbf v_n=\mathbf i=\mathbf B\mathbf i^h,\qquad
\mathbf i^h=[i_1^h,i_2^h]^\mathsf T .
\]

连通矩阵 \(\mathbf T\) 把节点电压变成四个二极管电压，因此

\[
\mathbf v_d=\mathbf T(\mathbf Y^{\sigma_\mathrm{rec}})^{-1}\mathbf B\mathbf i^h .
\]

对理想两值 RSM，二极管 \(d_i\) 导通的判据是相应线性式 \(\vartheta_{d_i}>0\)。Eq. (14)–(17) 展开了四个 \(\vartheta\) 对 \(i_1^h,i_2^h\) 的系数；逐候选状态联立这些不等式并做 Fourier-Motzkin elimination，便能离线删除不自洽的 12 种状态，只留下四种模式。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)

其次，四个可行域的边界斜率由 AC/DC Norton 电导与 \(g_\mathrm{on/off}\) 决定。特别是 \(g_\mathrm{off}\simeq0\) 时，阻断边界 \(m_1\simeq g_2/g_1\)。它的工程意义是：阻断并非仅由整流电流“是不是零”决定，而由谐振侧和负载侧离散等效电导共同决定；丢掉 \(g_1\) 就丢掉区分阻断态所需的信息。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)

最后，Eq. (29) 把四条边界写成一个 \(4\times2\) 矩阵乘法与 sign，Eq. (30) 把 sign pair 映射成四位状态字。网络推进 Eq. (24) 仍然是由预计算 \(\mathbf H^\sigma\) 完成的线性状态更新。所谓“exact and noniterative”应严格理解为：在论文采用的 BE + 两值 RSM + 指定拓扑模型内，开关状态是同时且非迭代地确定；它不是对连续时间真实半导体器件的无模型误差精确解。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)

### § 7 — 实验设计与结论

**问题 1：FE 忽略整流桥阻断模式是否只是无害近似？ → 实验：** 对文献中的两个 LLC 参数组，都用 15 ns 步长比较 FE 与迭代 BE；Parameter Set #1 的 \(f_{r1}=160\) kHz，Parameter Set #2 的 \(f_{r1}=500\) kHz，后者还给出 \(V_\mathrm{in}=400\) V、\(V_\mathrm{out}=12\) V、\(L_r=4.5\,\mu\mathrm H\)、\(L_m=21.6\,\mu\mathrm H\)、\(C_r=22\) nF、\(R_L=0.144\,\Omega\)。**答案：** 两组 FE 都在阻断段振荡；Parameter Set #2 的 FE/BE 整体差异更强，作者另报告 FE 在 \(\Delta t\ge30\) ns 失稳。该实验支持“显式二态判定不具参数稳健性”，但没有穷举所有 LLC 参数。[pdf:E03](_evidence/E03-p003-fig03-04-table01-eq03-04.png) [pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)

**问题 2：Single-Stage DMM 的面积—步长折中怎样？ → 实验：** 在 Xilinx Kintex XC7K325T 上比较 Fully Parallel Implementation（FPI，\(N_1=7,N_2=4\)）与 Hardware Reuse Technique（HRT，\(N_1=N_2=1\)），目标时钟为 40、200、320 MHz。**答案：** Table II 报告 FPI 在三种时钟下均为 25 ns 步长、50 ns 输入输出 latency；HRT 分别为 100、40、34.375 ns，面积显著更小。以 200 MHz 为例，FPI 报告 1,095 LUT、1,697 registers、88 DSP、22 BRAM；HRT 报告 329 LUT、350 registers、22 DSP、5.5 BRAM。[pdf:E07](_evidence/E07-p007-table02-fig10-fpga-design.png)

**问题 3：FPGA DMM 是否贴合离线迭代解？ → 实验：** 作者选择 200 MHz FPI 与 Parameter Set #2，运行 0.6 s：0–0.1 s 为 312.5 kHz；0.1–0.13 s 负载短路；0.13–0.25 s 故障清除；0.25–0.48 s 把频率从 312.5 kHz 提至 500 kHz；0.48–0.6 s 保持 500 kHz。比较 \(v_o,i_r,i_m\) 的 FPGA 波形与 offline iterative reference，并用

\[
e=\frac{\lVert f_s-f_r\rVert_2}{\lVert f_r\rVert_2}
\]

计算 2-norm relative error。**答案：** 全序列误差分别为 \(v_o=0.018\%\)、\(i_r=0.336\%\)、\(i_m=0.124\%\)；所有分段值均低于 0.5%，最大报告值是 500 kHz 段的 \(i_r=0.499\%\)。作者还报告 500 kHz 时输出电压 dc offset 不超过 0.2%。这些数值来自正文和 Table IV，不是从曲线估读。[pdf:E08](_evidence/E08-p008-fig11-table03-04-eq32.png)

作者最终结论是：DMM 以很小硬件 footprint 实现了 25 ns 步长，对 500 kHz LLC 在正常、频率变化和短路故障工况下都与离线迭代解保持低于 0.5% 的 2-norm relative error。[pdf:E09](_evidence/E09-p009-conclusion.png)

需要限制外推范围。实验验证的是单一 LLC 拓扑、两个离线数值参数组、一个 FPGA 设计空间和一条 0.6 s 序列；没有真实功率级测量、controller-in-the-loop I/O、device switching transient 或多 converter 可扩展性实验。资源对比还存在内部口径冲突：正文称 Table III 复现 200 MHz 结果，但 Table III 的 FPI/HRT clock 栏写 320 MHz；其定点格式和 FPI DSP 百分比也与正文/Table II 不一致。[pdf:E07](_evidence/E07-p007-table02-fig10-fpga-design.png) [pdf:E08](_evidence/E08-p008-fig11-table03-04-eq32.png)

### § 8 — Take-aways

**5 句话。**

1. 高开关频率 LLC 实时仿真的核心瓶颈是：准确的隐式 RSM 需要同时确定自然换流二极管状态，而在线迭代破坏固定 deadline。[pdf:E01](_evidence/E01-p001-abstract-introduction.png)
2. DMM 证明在论文模型中，两个 BE history current 足以把整流桥状态划分成 Blocked、Positive、Negative、Shorted 四个可行区域。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)
3. 运行时因此只需 MVM、sign 与 lookup，不再反复解网络；Single-Stage 重写再以两步输出 latency 换取更短 initiation interval。[pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png) [pdf:E06](_evidence/E06-p006-fig07-09-eq31.png)
4. Kintex K325T 的 FPI 报告 25 ns 步长，200 MHz FPI 在 500 kHz LLC 的 0.6 s 测试中对离线迭代基准的三个信号误差均低于 0.5%。[pdf:E07](_evidence/E07-p007-table02-fig10-fpga-design.png) [pdf:E08](_evidence/E08-p008-fig11-table03-04-eq32.png)
5. 这个结果严格成立于论文的理想两值 RSM 与已验证拓扑/工况，不能自动推广到带器件记忆效应的真实半导体或任意 resonant topology。

**3 句话。** DMM 把二极管状态迭代替换为 history-current 平面中的静态区域分类。它在论文的 FPGA LLC 实现中同时给出小步长、小面积和相对离线迭代解的低误差。真正需要继续追问的不是“分类能不能快”，而是“当前状态变量是否足以让真实器件模式成为单值函数”。

**1 句话。** 这篇论文最重要的贡献，是把隐式开关网络的在线互补求解离线编译成一个可在 FPGA 上固定延迟执行的 mode map。

### § 9 — 最脆弱的假设

最脆弱的假设是：对需要仿真的整流器，\((i_1^h,i_2^h)\) 是决定二极管状态的充分状态，因此存在单值、静态且可预计算的 \(f(i_1^h,i_2^h)\to\sigma_\mathrm{rec}\)。在论文的单相全桥、线性 BE-Norton equivalent 和两值 RSM 中，这个假设由 Eq. (13)–(17) 的线性不等式与四个可行区域支撑；因此“exact”在该模型内是有数学依据的。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)

它在真实高频器件中可能失效，因为 diode reverse-recovery charge、junction capacitance、温度相关 \(R_\mathrm{on}\)、transformer saturation、dead time 或 synchronous rectifier gate history 都引入额外记忆。此时两个具有相同 \((i_1^h,i_2^h)\) 的时刻，可能因储存电荷或磁化历史不同而需要不同开关模式；单值 map 不再存在。论文只用理想开关/RSM 的 LLC 验证，虽声称可用于其他 resonant topology，却没有给出其他拓扑或含器件动态的实验。[pdf:E02](_evidence/E02-p002-fig01-02-eq01-02.png) [pdf:E08](_evidence/E08-p008-fig11-table03-04-eq32.png)

这是失败代价最大的假设，因为一旦“状态充分性”不成立，增加 FPGA 并行度或缩短步长都救不了分类正确性；需要改变状态表示和 mode-selection 机制，而不是调参。

### § 10 — 最小复现实验

一周内最值得复现的是“DMM 能否在不迭代的情况下复现同一 BE-RSM 的开关状态序列”，而不是先复刻整套 FPGA。

1. 用 double precision 写两个离线模型：一个逐步迭代二极管状态直至自洽的 BE + RSM reference；一个严格按 Eq. (20)–(30) 分类并按 Eq. (24) 推进的 DMM。采用 Table I 的 Parameter Set #2。[pdf:E03](_evidence/E03-p003-fig03-04-table01-eq03-04.png) [pdf:E05](_evidence/E05-p005-eq18-30-algorithm.png)
2. 两模型使用完全相同的初值、输入与步长，先跑论文的 312.5 kHz 稳态—短路—清故障—升频至 500 kHz 序列。论文未报告完整初值与 reference 步长，因此应公开选择，并额外用 5 ns reference 做 time-step convergence，而不是把自选细节冒充原设定。[pdf:E07](_evidence/E07-p007-table02-fig10-fpga-design.png) [pdf:E08](_evidence/E08-p008-fig11-table03-04-eq32.png)
3. 每一步记录四位 diode mode，首先测量 DMM 与 converged iterative reference 的 mode mismatch count，特别标记阻断和短路边界；其次计算 \(v_o,i_r,i_m\) 的 Eq. (32) 误差与最大瞬时误差。
4. 支持核心 claim 的最低结果是：除数学边界上的 tie-breaking 外，mode sequence 一致，DMM 无状态迭代，并在论文序列中保持三个信号 2-norm error 低于 0.5%。若在相同步长和同一两值 RSM 下持续出现非边界 mode mismatch，或误差集中在阻断/短路切换处且无法随 reference 步长收敛，就直接反驳“模型内 exact mapping”。

完成这一步后再做 fixed-point bit-true 与 HDL HLS/RTL 实现才有意义；由于论文的 bit-format 报告不一致，复现者必须自己冻结量化、舍入和溢出规则。

### § 11 — 最强反例设计

最强反例不是再换一组 \(L_r,C_r\)，而是构造“同一 DMM 输入、两个不同正确模式”的状态碰撞。选一个 500 kHz 以上、带可测 reverse-recovery charge 与 junction capacitance 的整流器模型，或者同步整流 MOSFET 模型；设计两条前置脉冲历史，使某时刻的 \(i_1^h,i_2^h,u,c\) 在数值容差内相同，但器件储存电荷 \(q_{rr}\) 不同。随后给相同输入，观察高保真 SPICE/器件模型是否产生不同的导通集合。

如果两个轨迹在 DMM 的可见状态上重合、下一时刻却需要不同 \(\sigma_\mathrm{rec}\)，就证明不存在论文形式的单值 \(f(i_1^h,i_2^h)\)。这不是说论文在其 RSM 内算错，而是精确指出其“模型内 exact”不能承担“真实器件 exact”的替代解释。反之，如果在覆盖温度、负载、dead time 和故障恢复的轨迹中始终找不到碰撞，才为该充分状态假设提供比本文更强的外部证据。

### § 12 — Follow-up Research Idea

**候选方向：可认证的充分状态自动合成（不声称 novelty）。** 目标不再是为一个理想整流桥手推一张 DMM map，而是给任意 converter 的 hybrid device model 自动判断：当前状态摘要是否足以唯一决定 mode；若不足，自动加入最少的 memory state，直到能生成带覆盖证明的 FPGA guard logic。

- **未满足需求。** 本文的手工推导对理想全桥很漂亮，但跨 topology、器件非理想和多 converter 后，最危险的问题是 silent state omission：生成器仍能输出高速 map，却不知道自己遗漏了决定 mode 的历史量。
- **潜在研究价值。** 在 power electronics/EMT 领域，价值来自可验证的工程实现：不仅给出更快仿真，还给出“哪些状态足够、在哪个 operating envelope 内 guard 完备、何时必须回退到迭代”的证书。这改变了研究目标，从单一电路加速转为可审计的 real-time model compilation。
- **可借鉴方法。** 可结合 hybrid automata 的 bisimulation/state abstraction、SMT 可满足性检查、reachability 与 decision-diagram synthesis；论文已用 Fourier-Motzkin elimination 做了一个二维线性特例。[pdf:E04](_evidence/E04-p004-fig05-06-eq05-17.png)
- **首个证伪实验。** 对含 reverse recovery 的整流器，自动搜索两条可达轨迹：候选摘要状态相同而合法下一 mode 不同。若加入任何有限、可实时实现的最小状态集合仍无法消除碰撞，或生成 guard 的 FPGA 代价超过 iterative baseline，这个方向的核心可行性就被否定。
- **与本文的实质区别。** 本文先假定一个已知二维状态并手工导出四区 map；候选方向把“状态是否充分”本身变成待证明、可失败的研究对象，并允许在证明失败时显式拒绝 direct mapping。

本卡没有为此方向补做完整相关工作检索，因此只能称为证据约束的候选研究方向，不能声称 novelty。
