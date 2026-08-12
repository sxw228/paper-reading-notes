# Fine-grained hardware resource optimization and design for FPGA-based real-time simulation of large-scale renewable energy generations

作者：Yanfei Li、Zhiying Wang、Xiaopeng Fu、Peng Li、Ligang Zhao、Xiaoshan Wu [pdf:E01]

出处：International Journal of Electrical Power & Energy Systems，169 (2025) 110754 [pdf:E01]

年份：2025 [pdf:E01]

DOI：10.1016/j.ijepes.2025.110754 [pdf:E01]

Zotero key：TNWTPJ4C

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：这篇论文解决的不是“怎样把 EMT（electromagnetic transient，电磁暂态）模型放上 FPGA”这一宽泛问题，而是更窄、更具体的编译问题：在控制系统的算术依赖和最低可行时延不变时，怎样以 operation（算术操作）为粒度减少 FPGA 上的 arithmetic unit、MUX 和 FIFO，并把优化结果自动变成可综合 HDL。** 作者把研究对象限定为大规模 renewable energy generation（REG，可再生能源发电）系统中的控制系统求解；电气网络求解模块沿用前作，并非本文优化模型的主体。[pdf:E03]（PDF 物理页 3，Section 2 与贡献概述）[pdf:E05]（物理页 5，Section 3.1）

这个问题重要，是因为 REG 实时 EMT 仿真同时面对两个方向相反的压力：一方面，高频电力电子要求几微秒到几十微秒的 time-step；另一方面，大量发电单元、变流器控制器和系统级控制器使控制侧 operation 数量和资源需求迅速增长。论文直接陈述，在其目标场景中，控制系统的规模和硬件消耗可能超过电气系统；现有 CPU/集群方案又主要按串行方式执行底层运算。[pdf:E01]（物理页 1，Abstract 与 Introduction）[pdf:E02]（物理页 2，Introduction）

论文报告的工程目标不是概念性加速：两套单 FPGA 实验分别包含 15 个 detailed PV units 和 15 台 detailed WTG，time-step 分别为 9 μs 和 10 μs；摘要还报告相对 PSCAD/EMTDC 的误差低于 0.5%，硬件资源利用率相对传统设计约下降 30%。这些数字说明作者瞄准的是“在硬实时步长内扩大可装入单片 FPGA 的模型规模”，而不是单纯缩短离线仿真时间。[pdf:E01]（物理页 1，Abstract）

## § 2 — 前人工作与不足

论文对前人工作的归纳分成两类。第一类是 CPU 或 PC-cluster 实时仿真：作者列举了 4-core CPU 上的 6-array PV、集群上的 30 台 averaged-value WTG、10 台 WTG 且 time-step 为 50 μs 的 detailed transient，以及含 25 台 averaged-value 与 5 台 detailed switching WTG 的 offshore wind farm。论文给出的不足是底层运算仍以串行为主，控制系统扩展时计算负担很快上升。[pdf:E02]（物理页 2，Introduction）这里是**论文对相关工作的直接概括**，本卡没有联网读取那些被引论文，因此不把这些比较当作独立复核后的结论。

第二类是 FPGA 实时仿真。FPGA 本身具有 spatial-temporal parallelism（空时并行）、分布式存储和深流水优势，但论文认为既有控制系统硬件通常按控制元件的输入输出关系手工搭块，parallel schedule 依赖研究者经验；operation 之间可挖掘的并行关系没有被系统利用，而且每换一个目标系统都要重新设计硬件。[pdf:E02]（物理页 2，Introduction）[pdf:E03]（物理页 3，Introduction 末段）

因此，论文真正补的缺口有两个。其一，把资源需求、critical-path lower bound（关键路径下界）和数据缓存写成 operation-level 优化模型，而不是只给经验性的并行结构；其二，把优化器输出的静态 schedule、unit 数量、MUX/FIFO 配置编码成输入文件，再由模板化 HDL generator 自动实例化硬件。[pdf:E03]（物理页 3，Section 2.1）[pdf:E07]（物理页 7，Section 3.3）

需要限定 novelty（新颖性）判断：论文没有与通用 HLS scheduler、resource-constrained scheduling、MILP/CP-SAT 高层综合工具做系统比较，也没有给出同类自动 HDL 工具的覆盖率或生成时间。因而，“第一次”或“优于所有现有编译器”不是本文证据能够支持的表述。

## § 3 — 重建作者的思考路径

下面是**基于论文结构的逆向重建**，不是作者逐字陈述。

第一步，作者先把控制系统从“控制框图”降到“typed floating-point operations（带类型的浮点操作）”。这样，加、乘、sin、cos 等 operation 都有确定的 pipeline latency 和已知 FPGA 资源单价，控制模型就能被处理成硬件调度问题。[pdf:E03]（物理页 3，Section 2.1）

第二步，控制图原本可能有 feedback loop。循环依赖会让一次 time-step 内需要多少次迭代、何时结束都不确定，因此无法先验得到固定 schedule。作者选择在反馈环上插入一个 **one-time-step delay**，用上一步数据切断本步内的环，从而把连接关系改写为 DAG（directed acyclic graph，有向无环图）。论文明确给出的理由是“消除迭代时间不确定性”。[pdf:E03]（物理页 3，Section 2.2）

第三步，在 DAG 上把每个 operation 当作节点，把源 operation 的 output latency 当作边长。无限资源时，任何可行 schedule 都不可能快于最长依赖路径；作者用 max-plus 形式的 Floyd–Warshall 计算全部节点对的最长路径，并取最大值作为 `Tmin`。[pdf:E04]（物理页 4，Eq. (7)–(12) 与 Section 2.2）

第四步，作者不再优化时间，而是把 `Tmin` 固定成 deadline。非关键路径上的 slack 被用来延迟 operation，使同类型 arithmetic unit 可以复用；若 producer 输出后不能立刻被 consumer 使用，就用 FIFO 暂存；多路输入由 MUX 送入共享 arithmetic unit。于是“时间余量”被转换成“资源复用机会”。[pdf:E05]（物理页 5，Eq. (13)–(19)）

第五步，优化结果被降成一个静态硬件配置：每种 arithmetic unit 的数量、每个 operation 的 start time、论文声称的 unit binding、需要的 MUX/FIFO 及其控制时刻。HDL generator 再把这些值填入 static/dynamic/nested templates，生成 global control、data integration、core computation、data storage/buffering 等模块。[pdf:E05]（物理页 5，Section 2.3.2 末段）[pdf:E07]（物理页 7，Section 3.3）

## § 4 — 核心 Intuition

核心 intuition 是：**先用 operation DAG 的关键路径锁死“不能再快”的 `Tmin`，再把所有非关键 operation 在 slack 内尽量错开，从而用更少的 arithmetic units 完成同一 deadline。** 被错开的 producer/consumer 之间用 FIFO 保数据，多个 operation 通过 MUX 轮流使用共享 unit；最后把这套静态 schedule 直接固化成 HDL。[pdf:E04]（物理页 4，Fig. 1 与 Eq. (7)–(12)）[pdf:E05]（物理页 5，Eq. (13)–(19)）

这不是一个动态 runtime scheduler，也不是求最小 `T_commit` 的算法。它是 compile-time（编译期）的“固定 `Tmin` 下最小加权资源”问题，实际 clock frequency 和整个 EMT time-step 的完成时刻要到综合实现及电气模块并行执行后才体现。[pdf:E03]（物理页 3，Section 2.2 首段）[pdf:E10]（物理页 10，Table 3）

## § 5 — 具体方法与完整 Pipeline

**1. 从控制模型得到 arithmetic operation graph。** 输入是目标 REG 控制系统的元件类型、连接关系和重复子系统数量。控制方程被拆成 floating-point add、multiply、divide、sin/cos 等 operation；每种 unit 有固定 output latency 和 ALM/BMB 资源参数。反馈边不是在本 time-step 内迭代求解，而是插入一个 time-step delay 后再建 DAG。[pdf:E03]（物理页 3，Section 2.1–2.2）

**2. 计算关键路径下界 `Tmin`。** 每个 operation 是节点，边长是 predecessor 的 output latency。Floyd–Warshall 的更新规则在 `-∞` 初始化的非连通条目上取更长路径；`D_FW` 的最大值被定义为控制系统的最短 solution time，即后续优化的固定 clock-cycle bound。[pdf:E04]（物理页 4，Eq. (7)–(12)）

**3. 建立粗粒度资源成本。** 总资源向量只保留 ALM 与 BMB 两类：arithmetic units 消耗 ALM/BMB，MUX 消耗 ALM，FIFO 消耗 ALM/BMB。FIFO 成本按“是否需要 buffer 的依赖边数 × 单个 FIFO 固定成本”计，MUX 成本按各类 operation 的输入数和 operation 数计。[pdf:E03]（物理页 3，Eq. (1)–(6)）

**4. 在 `Tmin` 内安排 start time 和资源复用。** 约束要求 predecessor 完成后 successor 才能开始，所有 operation 的 `start + latency` 不超过 `Tmin`，每个 clock cycle 同类 operation 的占用数不超过该类 unit 数；若 consumer start 晚于 producer 的 `start + latency`，则相应依赖边启用 FIFO。目标是最小化 `w_ALM R_ALM + w_BMB R_BMB`。[pdf:E05]（物理页 5，Eq. (13)–(19)）

**5. Park transformation 示例展示了 start time、binding、latency 与 FIFO 的关系。** 该例有 4 个 add、5 个 multiply、1 个 sin 和 1 个 cos；优化后只保留 1 个 adder、2 个 multiplier、1 个 sin unit、1 个 cos unit。unit latency 分别是 add 7、multiply 5、sin 36、cos 35 clock cycles。[pdf:E05]（物理页 5，Section 3.2 起始段）[pdf:E06]（物理页 6，Fig. 3 与 Table 1）

| Operation | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| start / cycle | 13 | 1 | 18 | 32 | 25 | 32 | 1 | 2 | 37 | 37 | 42 |
| end / cycle | 18 | 8 | 25 | 37 | 32 | 37 | 37 | 37 | 42 | 42 | 49 |
| binding | Mult 1 | Adder | Adder | Mult 1 | Adder | Mult 2 | Sin | Cos | Mult 1 | Mult 2 | Adder |

这些数值来自 PDF 物理页 6 的 Fig. 3 与 Table 1。[pdf:E06] operation #2 在 cycle 8 得到 `x2`，但 operation #4 到 cycle 32 才开始，因此中间结果要缓存 24 cycles；作者用这个例子解释 FIFO 的插入。Table 1 中每个 `end-start` 又恰好等于相应 unit 的 output latency。[pdf:E06]（物理页 6，Section 3.2 与 Table 1）

**6. 把优化结果写入六字段 input file。** 每个 operation 记录：operation type、被分配的 unit number、start time、提供输入的 predecessor type、predecessor unit number、predecessor start time；文件还记录每类 unit 的总数量。这是 schedule/binding 到 HDL 的显式接口。[pdf:E07]（物理页 7，Section 3.3.1）

**7. 用模板生成静态 HDL。** template file 中有 static objects（通用 timer、signal generator、MUX、FIFO、arithmetic units）、dynamic objects（随 case 改变的控制时刻等）和三层 nested objects。generator 根据 unit 数量实例化 core computation，根据 Items 1–3 生成 MUX 控制，根据 Items 4–6 配置 MUX 输入与 FIFO/read-write signal，并生成与 electrical system 的 data-exchange block。[pdf:E07]（物理页 7，Section 3.3.2–3.3.3）[pdf:E08]（物理页 8，Fig. 5）

**8. 运行时执行的是静态时序。** global control 的 timer/signal generator 按预定 cycle 产生 MUX、FIFO 和 exchange signals；data integration 选数据，core computation 执行，data storage/buffering 缓存并把结果送往 electrical system。Appendix A 的 HDL 片段展示了按固定 `t_mux`、`t_fifo_write`、`t_fifo_read` 和 `t_ex` 产生信号以及用 `generate` 实例化 MUX、multiplier、FIFO；Appendix B 展示了模块连线。[pdf:E06]（物理页 6，Fig. 2）[pdf:E12]（物理页 12，Appendix A）[pdf:E13]（物理页 13，Appendix B）

**必须严格限定论文实际生成的东西。** 本文支持的表述是：它生成控制侧的静态 operation schedule、资源数量、论文声称的 arithmetic-unit binding、MUX/FIFO 配置和模板化 HDL。全文没有给出以下内容，不能从本文外推：

- electrical network 的 elimination/partition/reordering 结构选择；电气系统模块明确来自前作且不是本文重点；[pdf:E05]（物理页 5，Section 3.1）
- Schur complement 的构造、exact full-state back-substitution 或全状态恢复；
- BMB 的 bank/address 分配、FIFO depth/word-width 推导、真实 dual-port RAM 的逐 cycle 端口冲突证明；
- 整个 EMT step 的 atomic commit 协议。Appendix A 只显示在固定 `t_ex` 拉起 `exchange_signal`，没有给出全部状态同时可见、跨模块提交或 read-during-write 语义的完整证明。[pdf:E12]（物理页 12，Appendix A）

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 资源模型：把硬件成本压成 ALM/BMB 两个标量

论文先定义

\[
R=[R_{\mathrm{ALM}},R_{\mathrm{BMB}}],
\]

\[
R_{\mathrm{ALM}}=\gamma^{\mathrm{MUX}}_{\mathrm{ALM}}+\gamma^{\mathrm{FIFO}}_{\mathrm{ALM}}+
\sum_{i=1}^{N_{\mathrm{AU}}}n_i^{\mathrm{AU}}\gamma^{\mathrm{AU}}_{i,\mathrm{ALM}},
\]

\[
R_{\mathrm{BMB}}=\gamma^{\mathrm{FIFO}}_{\mathrm{BMB}}+
\sum_{j=1}^{N_{\mathrm{AU}}}n_j^{\mathrm{AU}}\gamma^{\mathrm{AU}}_{j,\mathrm{BMB}}.
\]

FIFO 的 ALM/BMB 成本分别是固定单价乘所有 `δ_FIFO=1` 的 producer-consumer 边数；MUX 的 ALM 成本是固定单价乘各 operation type 的输入数与 operation 数之和。[pdf:E03]（物理页 3，Eq. (1)–(6)）直觉上，优化器能改变的主要变量是各类 unit 数和需要缓存的边数。

这个模型很“细”是因为落到了 arithmetic operation，但对 memory 又很“粗”：`d_{m,j,l,i}` 表示 producer 完成到 consumer 启动之间的等待长度，Eq. (19) 只把 `d=0` 与 `d≠0` 二分为不用/使用一个 FIFO；FIFO 的成本没有随 delay depth、data width、BMB packing 或端口数量变化。[pdf:E05]（物理页 5，Eq. (18)–(19)）因此，“BMB 最小”在论文中是其固定 FIFO 单价模型下的最小，不是物理 RAM banking 后的精确最小。

### 6.2 `Tmin`：无限资源时的 critical-path lower bound

论文定义 distance matrix `D_FW=[d_uv]` 和 routing matrix `R_FW=[r_uv]`。直连节点的 `d_uv` 取边长，非直连取 `-∞`；若

\[
d_{uw}+d_{wv}\ge d_{uv},
\]

则更新

\[
d_{uv}=d_{uw}+d_{wv},\qquad r_{uv}=r_{uw}.
\]

遍历所有中间节点后，`D_FW` 的最大元素被定义为最长 path 长度，也就是 `Tmin`。[pdf:E04]（物理页 4，Eq. (7)–(12)）这实际上是 DAG 上的 max-plus all-pairs longest path。它给出的是 operation dependency 与 unit latency 决定的 clock-cycle 下界；论文随后把它当约束，不再把它作为可优化目标。

反馈环插入 one-step delay 是这一步成立的前提：没有切环，正 latency cycle 会破坏最长路问题的有限性，且本步迭代次数不再固定。[pdf:E03]（物理页 3，Section 2.2）

### 6.3 固定 `Tmin` 下的资源最小化

目标函数是

\[
\min f=w_{\mathrm{ALM}}R_{\mathrm{ALM}}+w_{\mathrm{BMB}}R_{\mathrm{BMB}},
\]

权重由目标 FPGA 的可用 ALM/BMB 决定。[pdf:E05]（物理页 5，Eq. (13)）关键约束包括：

\[
\delta^{\mathrm{AU}}_{m,j,l,i}\bigl(t^{\mathrm{STA}}_{m,j}+t^{\mathrm{LAT}}_m\bigr)
\le t^{\mathrm{STA}}_{l,i},
\]

\[
t^{\mathrm{STA}}_{l,i}+t^{\mathrm{LAT}}_l\le T_{\min},
\]

\[
\max_t n^{\mathrm{PD}}_{t,l}\le n^{\mathrm{AU}}_l,
\]

以及

\[
d_{m,j,l,i}=\delta^{\mathrm{AU}}_{m,j,l,i}
\bigl(t^{\mathrm{STA}}_{l,i}-t^{\mathrm{STA}}_{m,j}-t^{\mathrm{LAT}}_m\bigr),
\]

`d=0` 时不用 FIFO，`d≠0` 时启用 FIFO。[pdf:E05]（物理页 5，Eq. (14)–(19)）第一式保证依赖，第二式把所有 operation 压进 critical-path deadline，第三式把每个 cycle 的同类型并发数转成所需 unit 数，第四式把 schedule slack 转成 buffer 需求。

所以论文的准确表述是：**在固定 `Tmin` 下最小化加权 ALM/BMB。** `T_commit` 这个变量在论文中不存在；真实 time-step 时间还等于 clock period 乘 cycle 数，并受综合后的 `fmax`、电气系统模块及同步时刻影响。[pdf:E03]（物理页 3，Section 2.2 首段）[pdf:E10]（物理页 10，Table 3）

### 6.4 latency 与 occupancy 不是同一个量

` t_l^{LAT}` 是 arithmetic unit 从输入到输出的 pipeline latency，用于 dependency 和 deadline；Park 例中 add/multiply/sin/cos 分别是 7/5/36/35 cycles，Table 1 的 `end-start` 与这些 latency 一致。[pdf:E06]（物理页 6，Section 3.2 与 Table 1）

为线性化 unit capacity，论文又引入 one-hot 的 `δ_STA`、`δ_END` 和逐 cycle 的 `δ_PD`：

\[
t^{\mathrm{STA}}_{l,i}=\sum_{t=1}^{T_{\min}}t\,\delta^{\mathrm{STA}}_{t,l,i},\qquad
\sum_t\delta^{\mathrm{STA}}_{t,l,i}=1,
\]

\[
t^{\mathrm{END}}_{l,i}=\sum_{t=1}^{T_{\min}}t\,\delta^{\mathrm{END}}_{t,l,i},\qquad
\sum_t\delta^{\mathrm{END}}_{t,l,i}=1,
\]

\[
\delta^{\mathrm{PD}}_{t,l,i}=\delta^{\mathrm{PD}}_{t-1,l,i}
+\delta^{\mathrm{STA}}_{t,l,i}-\delta^{\mathrm{END}}_{t,l,i},
\quad \delta^{\mathrm{PD}}_{0,l,i}=0,
\]

\[
\sum_{t=1}^{T_{\min}}\delta^{\mathrm{PD}}_{t,l,i}=n_{ss}.
\]

[pdf:E05]（物理页 5，Eq. (20)–(26)）结合 nomenclature，`δ_PD` 更像某个 operation 向流水 unit 连续输入 `n_ss` 个重复子系统数据时的**输入占用窗口**，不是 output latency；这是基于公式的解释。论文没有把这层语义讲透，而且 Eq. (23) 附近把 `t_END` 解释为输入结束，Table 1 又把 `end time` 用成 `start+latency` 的 operation 完成时刻，存在记号复用或表述歧义。[pdf:E02]（物理页 2，Nomenclature）[pdf:E06]（物理页 6，Table 1）

Eq. (19) 的二值关系再用 big-M 线性化：

\[
-\delta^{\mathrm{FIFO}}_{m,j,l,i}M\le d_{m,j,l,i}
\le \delta^{\mathrm{FIFO}}_{m,j,l,i}M.
\]

[pdf:E05]（物理页 5，Eq. (27)）

### 6.5 start time 有显式变量，binding 在数学模型中没有闭合

论文明确说，求解结果包含每个 operation 的 start time 和“指定在哪个 floating-point arithmetic unit 上执行”；HDL input file 的 Item 2 也确实需要 unit number。[pdf:E05]（物理页 5，Section 2.3.2 末段）[pdf:E07]（物理页 7，Section 3.3.1）

但就 PDF 给出的 Eq. (13)–(27) 而言，模型只有每类 unit 的总数和 aggregate occupancy，没有展示 `x_{operation,unit}` 一类 assignment variable、同一具体 unit 上 interval 不重叠的约束，也没有给出从 aggregate schedule 到 unit binding 的构造算法。Park 例提供了一个实际 binding，但一般情形的 binding 完备性是**论文未证明的缺口**，不能把“作者声称会输出 binding”改写成“公式已经逐 unit 证明可绑定”。[pdf:E05]（物理页 5，Eq. (13)–(27)）[pdf:E06]（物理页 6，Fig. 3）

## § 7 — 实验设计与结论

**问题 1：优化能否在不放宽 time-step 的情况下显著减少资源？ → 实验：15-PV 系统，和经验式手工 traditional design 对比。 → 答案：能减少 ALM，但 total step 没有缩短。** 该系统的 admittance matrix 维度约 400，control graph 有 2850 nodes，FPGA clock 为 160 MHz，time-step 为 9 μs。[pdf:E08]（物理页 8，Section 4.1）Table 2 中 proposed/traditional 的 total ALM 为 48.5%/77.8%，control-system ALM 为 14.0%/43.3%，作者据此报告 control ALM 降低 67.7%、total ALM 降低 37.0%；control BMB 从 0.2% 增到 0.3%。两者 total solution time 都是 8.91 μs，因为 control solution 仅约 2.02/2.03 μs，电气系统的 8.91 μs 成为主路径。[pdf:E08]（物理页 8，Section 4.1.1）[pdf:E09]（物理页 9，Table 2）这组结果恰好说明本文不是在最小化全步 `T_commit`。

**问题 2：资源下降能否让更大控制系统满足 10 μs 实时约束？ → 实验：15 台 1.5 MW WTG 系统，同样与 traditional design 对比。 → 答案：proposed design 满足，traditional design 不满足。** 该 case 的 electrical admittance matrix 维度为 601，control graph 有 6525 nodes。[pdf:E09]（物理页 9，Section 4.2.1）Table 3 中 proposed/traditional 的 total ALM 为 58.2%/88.1%，control ALM 为 21.4%/51.3%；较低 ALM 让综合时钟达到 155 MHz，而传统设计只有 125 MHz。两者所需 cycle 数相近，为 333/351，但 total solution time 是 9.81/12.16 μs，因此只有 proposed design 落在 10 μs 内。[pdf:E10]（物理页 10，Table 3）这里的 wall-clock 改善来自资源压力下降后 `fmax` 提高，不是优化器把 `Tmin` 作为目标继续压短。

**问题 3：静态调度、反馈 delay 和 switching-function model 是否还能保持数值一致？ → 实验：两套 FPGA waveform 与同 time-step 的 PSCAD/EMTDC 对比。 → 答案：所展示波形接近，摘要报告 relative error 小于 0.5%，但误差来源没有被完全消除。** PV case 展示 phase-A voltage/current、全部 PV 的 active/reactive power、DC-link voltage 及其 relative error；WTG case 展示对应电压、电流、功率、rotational speed 及其 relative error。[pdf:E09]（物理页 9，Fig. 8）[pdf:E10]（物理页 10，Fig. 10）作者明确说明两种结构性差异：FPGA 使用 switching-function model 而 PSCAD/EMTDC 使用 `Ron/Roff` model；FPGA 的 feedback loop 有 one-step delay，而 PSCAD/EMTDC simultaneous solve。[pdf:E08]（物理页 8，Section 4.1.2）因此这些曲线验证的是两个完整实现的接近程度，不是单独隔离 schedule 或 feedback delay 的误差。

**问题 4：自动 HDL 生成链是否落到真实 FPGA？ → 实验：在 Intel Stratix V EP5SGSMD5K2F40C2 上运行两套 case，并展示 generator 流程、HDL 片段和综合后模块示意。 → 答案：生成结果至少足以支撑这两套实现。**[pdf:E08]（物理页 8，Fig. 5、Fig. 6）[pdf:E12]（物理页 12，Appendix A）[pdf:E13]（物理页 13，Appendix B）但论文没有报告 code-generation time、solver time、综合成功率、模板覆盖率，或与 HLS/手写 RTL 在开发时间上的量化比较，所以“提高建模效率”主要还是作者的定性结论。

不得外推的范围包括：只有两个 REG case、一个 FPGA family、一个 traditional baseline；没有其他 scheduler/optimizer、跨芯片复现、不同反馈强度/步长的系统 sweep，也没有 end-to-end memory-port 或 atomic-step 正确性证明。作者在结论中把总体结果概括为资源消耗下降约 30%，并把 heterogeneous multi-FPGA 扩展列为未来工作；后者尚未被本文实验验证。[pdf:E11]（物理页 11，Conclusion）

## § 8 — Take-aways

**5 句话：**

1. 论文把 REG 控制求解编译成带 unit latency 的 operation DAG，并用最长路径定义固定 `Tmin`。[pdf:E03]（物理页 3，Section 2.2）[pdf:E04]（物理页 4，Eq. (7)–(12)）
2. 在这个固定 deadline 内，优化器通过移动非关键 operation、复用同类 arithmetic unit 和插入 FIFO，最小化加权 ALM/BMB，而不是最小化 `T_commit`。[pdf:E05]（物理页 5，Eq. (13)–(19)）
3. Park 示例把 start time、unit binding、pipeline latency 和 buffer delay 连成了可读的 cycle-level schedule，但一般 binding 的数学约束没有在文中闭合。[pdf:E06]（物理页 6，Fig. 3 与 Table 1）
4. HDL generator 把六字段 operation 描述和 static/dynamic/nested templates 变成 timer、MUX、arithmetic unit、FIFO 与 data-exchange 的静态 RTL 配置。[pdf:E07]（物理页 7，Section 3.3）[pdf:E08]（物理页 8，Fig. 5）
5. 两个单 FPGA case 证明了 ALM 下降和 9–10 μs 实时运行的可行性，但没有覆盖网络消元、精确 Schur 全状态恢复、bank/address 证明或完整 EMT-step atomic commit。[pdf:E09]（物理页 9，Table 2）[pdf:E10]（物理页 10，Table 3）[pdf:E12]（物理页 12，Appendix A）

**3 句话：** 这篇论文的关键不是发明新的 EMT 数值积分，而是把控制侧的 operation graph 变成一个 resource-constrained static schedule。`Tmin` 是关键路径下界和固定约束，真正被优化的是 ALM/BMB；较低资源还可能间接提高综合后 `fmax`。自动 HDL 链把 schedule 落地了，但从 aggregate occupancy 到一般 unit binding、从 FIFO 标志到真实 memory implementation 仍缺少完整证明。[pdf:E05]（物理页 5）[pdf:E10]（物理页 10）

**1 句话：** 这是一个“先锁定 critical-path `Tmin`，再以时间 slack 换 FPGA 资源，并把结果静态编译成 HDL”的控制侧硬件生成方法。[pdf:E04]（物理页 4，Fig. 1）

## § 9 — 最脆弱的假设

**最脆弱的假设是：把每个 feedback loop 替换成 one-time-step delay，既足以把控制图变成 DAG，又不会对目标 REG 动态造成不可接受的语义改变。** 这不是外围实现选择，而是整个 `Tmin` 计算和静态 schedule 存在的逻辑前提；若本 time-step 内必须 simultaneous solve 或迭代求解，图就不再是论文假定的 DAG，最长路径下界和后续 MILP 都不再对应原控制方程。[pdf:E03]（物理页 3，Section 2.2）

在高增益、强耦合、stiff 或近代数环的控制回路中，一个完整 time-step 的 delay 会改变离散闭环极点、相位裕度和故障瞬态。论文给出的支持证据是两套 9/10 μs case 与 PSCAD/EMTDC 的波形接近，且摘要报告 relative error 低于 0.5%；但作者也明确把“FPGA feedback 有 delay、PSCAD simultaneous solve”列为误差来源。[pdf:E01]（物理页 1，Abstract）[pdf:E08]（物理页 8，Section 4.1.2）缺失的证据是：对 feedback gain、loop bandwidth、time-step、fault severity 和 algebraic-loop stiffness 的系统 sweep，以及 delay 对稳定边界的理论分析。

只要存在一个实际重要的控制环在 simultaneous solve 下稳定、而插入 one-step delay 后失稳或产生不可接受误差，本文方法对该环的核心适用性就会直接失效。

## § 10 — 最小复现实验

一周内最有效的复现不是重做 15-PV 或 15-WTG，而是复现 PDF 物理页 6 的 Park transformation，并把论文未闭合的 unit binding 显式补上。[pdf:E06]（物理页 6，Fig. 3 与 Table 1）

具体做法：

1. 按 Fig. 3(a) 录入 11 个 operations、依赖边和 add/multiply/sin/cos 的 7/5/36/35-cycle latency；按论文的最长路径定义独立计算 `Tmin`。Table 1 的最大 endpoint 是 cycle 49，若实现使用 0-based indexing，应把可能的一拍差明确报告，而不是强行对齐。[pdf:E06]
2. 建一个小型 MILP 或 CP-SAT：保留论文的 start-time、dependency、deadline、aggregate occupancy 与 FIFO-gap 约束，同时新增 `x_{op,unit}` assignment 变量和每个具体 unit 的 no-overlap 约束。
3. 检查是否能得到论文给出的资源数与 binding：1 adder，2 multipliers，1 sin，1 cos；并核对 11 个 start/end times。计算 edge `2→4` 的等待是否为 24 cycles，进而触发 FIFO。[pdf:E06]
4. 生成最小 Verilog 或 cycle-accurate simulator：timer 驱动 MUX selection、unit input、FIFO write/read；用随机 `Ua,Ub,Uc,θ` 与软件 Park transform 比较输出。最后做一次综合，记录 ALM/BRAM、`fmax` 与 completion cycle。

支持核心 claim 的结果是：在不超过论文 critical-path bound 的情况下，显式 binding 可实现且 unit 数显著少于 one-operation-one-unit baseline，RTL 输出与软件结果一致。反驳结果包括：aggregate occupancy 满足但无法分配到具体 units、FIFO read/write 时刻导致读空/覆盖、或要保持功能正确必须超过论文的 completion bound。这个实验直接检查“DAG → schedule → binding → FIFO/MUX control → HDL”的最短闭环。

## § 11 — 最强反例设计

最强反例应专门攻击 feedback-delay-to-DAG 这一步，同时消除 switching model、网络规模和 FPGA 量化等混杂因素。

构造一个小型但高增益的控制 algebraic loop，使 simultaneous equation 在每个 time-step 内有唯一稳定解；然后实现两个完全相同的浮点版本：A 版本在本步内 simultaneous solve，B 版本按论文方法把反馈值替换成前一步状态并做静态 DAG schedule。扫描 loop gain、controller bandwidth 和 time-step，比较闭环 pole、故障阶跃响应、峰值误差与是否失稳。两边使用相同 arithmetic precision、相同 plant、相同 operation latency，避免把差异归因于 `Ron/Roff` 与 switching-function model。[pdf:E03]（物理页 3，Section 2.2）[pdf:E08]（物理页 8，Section 4.1.2）

如果能找到一个区域：A 稳定且误差很小，B 因一拍 delay 出现持续振荡、失稳或远超 0.5% 的状态偏差，那么论文两套 case 的好结果就有一个更强的替代解释——不是“one-step delay 普遍可接受”，而只是测试 case 的 loop 对该 delay 不敏感。这个反例会同时推翻 DAG 语义等价和由该 DAG 导出的 `Tmin` 对原系统的代表性。

## § 12 — Follow-up Research Bet

**主 idea：做一个“network elimination tree（网络消元树）—control operation DAG—memory layout”一体化的 EMT hardware compiler。** 这是候选研究判断；本任务只读了输入论文及其参考文献表，没有联网检索，因此不声称 novelty。

新的研究问题是：能否从 electrical network topology、control equations 和目标 FPGA 出发，联合选择 sparse elimination/reordering、boundary-state representation、exact back-substitution、operation schedule、unit binding 与 bank/address layout，直接最小化**完整 EMT step** 的 cycle×clock-period 和资源，而不是只在既定 electrical solver 之外最小化 control-side 资源？它首次可能让“从电网图到可执行整步 RTL”成为统一编译问题，而不是本文这种“电气模块既定、只自动生成控制模块”的分段流程。[pdf:E05]（物理页 5，Section 3.1）[pdf:E13]（物理页 13，Appendix B）

核心因果链是：选择 elimination tree 改变 fill-in、并行子树和边界状态规模；把 Schur boundary solve 与 exact full-state recovery 显式展开为 typed streaming DAG；再联合安排 arithmetic units、FIFO depth、bank/address 和 dual-port access，使 topology-level parallelism 与 operation-level slack 同时可用；最终用类似本文的 template generator 固化 timer、MUX、FIFO、compute kernels 和 step-boundary exchange。这里改变了至少五个基本设计变量：problem definition、state representation、hardware mapping、memory topology 和评价对象。

论文内有两条具体依据。第一，Eq. (13)–(27) 与 Fig. 1 已证明 operation-level schedule 可以被转成静态资源配置和 HDL 输入。[pdf:E04]（物理页 4，Fig. 1）[pdf:E05]（物理页 5，Eq. (13)–(27)）第二，PV case 中 control ALM 降低 67.7% 后 total solution time 仍是 8.91 μs，因为 electrical system 已经成为主路径；WTG case 又显示资源压力会通过 `fmax` 影响整个 step。[pdf:E09]（物理页 9，Table 2）[pdf:E10]（物理页 10，Table 3）这说明下一阶段的高收益空间不在继续微调 control-only objective，而在跨越 electrical/control 边界重新定义编译对象。

按本文对既有工作的 framing，这个押注与最近路径有四个实质区别：problem 从“固定 operation graph 上省控制资源”改成“联合选择网络求解结构与整步硬件”；mechanism 从单纯利用 schedule slack 改成 elimination-tree parallelism 与 operation slack 的耦合；representation 从扁平 control DAG 改成 elimination tree、boundary state 和 recovery DAG 的分层对象；experimental object 从 control module 的资源/波形扩展为 full-state whole-step execution。本文只说明既有 FPGA 控制硬件多为手工构建、并行关系依赖经验，因此这段比较仍是基于本文材料的候选判断，不是独立 novelty 认证。[pdf:E02]（物理页 2，Introduction）[pdf:E03]（物理页 3，Introduction 末段）

最大收益是把网络结构、算术调度和存储端口从彼此独立的人工决定变成可搜索的统一设计空间，可能同时扩大模型规模、缩短 whole-step latency，并生成可审计的 full-state dataflow。最大科学风险是 elimination fill-in 和 back-substitution memory traffic 抵消并行收益；开关拓扑变化还可能破坏静态消元结构，使联合搜索复杂度失控。

最小判别实验用论文的 15-PV case，固定数值精度和控制方程，比较三种实现：A 为本文式“固定 electrical solver + optimized control”；B 固定同一 elimination tree，但做 electrical/control 联合 schedule 与 bank mapping；C 同时优化 elimination tree、联合 schedule 和 exact state recovery。测量 total step time、ALM/BMB、`fmax`、每 cycle port conflict、以及全状态与软件 EMT 的逐步一致性。若 B 与 C 收益相同，真正机制只是跨模块 schedule；只有 C 显著优于 B，才能说明 topology/elimination co-design 是新增能力的因果来源。

**Wild-card alternative：** 不展开 15 个近同构 PV/WTG 子系统的完整 operation DAG，而把它们编译成 parameterized cyclo-static dataflow actor，以向量化 state stream 共享一套 schedule 和 broadcast MUX 网络，研究资源随子系统数量的尺度律；这改变的是 graph representation 与 data-generation方式，而不是网络消元机制。[pdf:E08]（物理页 8，15 个 PV subsystems 的 pipeline 描述）[pdf:E09]（物理页 9，15 个 WTG subsystems 的 pipeline 描述）
