# Parallel-in-Time Object-Oriented Electromagnetic Transient Simulation of Power Systems

**作者：** Tianshi Cheng, Tong Duan, Venkata Dinavahi  
**出处：** IEEE Open Access Journal of Power and Energy, Vol. 7  
**年份：** 2020  
**DOI：** 10.1109/OAJPE.2020.3012636  
**Zotero key：** GFMQBWWJ

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的不是通常的“把大电网按空间切开并行求解”，而是把同一段 EMT 仿真时间切成多个子区间，让多个 CPU worker 同时推进不同时间段。EMT 要以很小步长重现故障、浪涌和电磁暂态，传统求解器即使充分利用稀疏矩阵，时间推进仍有强顺序依赖；因此，如果能在时间轴上获得并行度，就可能突破仅靠矩阵并行或空间分解留下的瓶颈。论文的明确目标是：在保留传统节点分析与已有元件模型的前提下，让 Parareal 能处理系统级 EMT，尤其要处理行波传输线带来的 delay differential equation（DDE）历史依赖。[pdf:E01]（PDF 物理页 1，Abstract、Nomenclature 与 Introduction）

这项工作的工程价值在于，它把“能不能并行”从系统规模问题改写为时间尺度问题。空间并行通常希望矩阵足够大，才能摊薄线程启动、同步与分解开销；时间并行则可能让较小系统也获得加速，但前提是粗时间网格能预测细时间网格，而且时间窗口不能破坏传输线历史状态。论文最终在 IEEE-118 案例上报告 6 线程、相同精度下 2.30× 加速和 38.3% 并行效率；作者据此把传输线时延而非系统规模识别为主要性能边界。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E10]（PDF 物理页 10，Table 3 后正文）

需要明确边界：这是 CPU 上的离线 EMT 加速研究，不是 FPGA 实时仿真器实现。论文只在相关工作中提到 GPU、FPGA 和 MPSoC 的空间并行 EMT，并未给出 FPGA 映射、定点数设计、资源占用或实时 deadline 证据。[pdf:E02]（PDF 物理页 2，Introduction 左栏）[pdf:E07]（PDF 物理页 7，Section IV 开头）

## § 2 — 前人工作与不足

论文把 prior work 分为三类。第一类是空间域分解以及 CPU、GPU、FPGA、MPSoC 上的 EMT 并行实现；它们已经能把大系统切成子系统并行计算，但仍然没有利用时间轴上的并行度。第二类是电力系统动态仿真的 Parareal/MGRIT：已有工作处理过半显式 DAE、两机全隐式 DAE，以及涡流有限元问题。第三类是针对单一 EMT 元件的工作，例如基于平均模型的 MMC-HVDC Parareal。作者据此声称，当时缺少能整合传统异构元件模型的系统级 parallel-in-time EMT 方法。[pdf:E02]（PDF 物理页 2，Introduction 左栏及参考文献 [9]–[13]）

作者归纳了三个技术缺口。其一，节点分析产生的电路方程通常是 index 不低于 1 的 DAE，很多只适用于 ODE 的时间并行方法不能直接使用；改成 state-space 又会显著增大矩阵。其二，传统 EMT 元件常把固定步长写进状态更新，而 Parareal 同时需要 coarse step \(\Delta t\) 与 fine step \(\delta t\)。其三，Bergeron 等行波线模型依赖 \(t-\tau\) 的历史量，粗网格没有细网格需要的历史样本，传统插值会让 coarse prediction 偏离 fine solution。[pdf:E02]（PDF 物理页 2，Introduction 三项原因）[pdf:E04]（PDF 物理页 4，Section II-C）

这些不足不是一句“前人没考虑传输线”能够概括的。真正的障碍是 Parareal 的收敛条件要求 coarse operator \(G\) 在子区间端点给出接近 fine operator \(F\) 的状态；但传输线状态不是仅靠端点状态就能重启，它还需要覆盖传播时延的历史轨迹。论文的方案因此同时改元件接口、历史缓存和时间窗口，而不是只替换迭代器。[pdf:E03]（PDF 物理页 3，Eq. (4)–(5) 及其解释）[pdf:E05]（PDF 物理页 5，Fig. 4 与相邻正文）

关于 novelty，本卡只复述论文对当时工作的定位，没有执行论文之外的系统性文献检索，因此不声称该方法在 2020 年或当前仍具有唯一性。

## § 3 — 重建作者的思考路径

可以从一个已有工程事实出发：传统 EMT 的节点分析非常成熟，电感、电容、变压器、同步机和传输线都能被封装成“等效导纳加历史电流源”，系统级求解只需组装矩阵和右端项。若为了时间并行把全部模型重新推成统一 ODE 或 state-space，既会丢掉既有模型资产，也会增加矩阵与实现复杂度。因此，一个更保守的路线是保留节点分析，把每个元件真正需要跨时间窗口传递的局部状态显式化。[pdf:E03]（PDF 物理页 3，Eq. (6)–(9) 与 Components Models）[pdf:E04]（PDF 物理页 4，变压器、同步机状态定义）

接着引入 Parareal。它先用便宜的 coarse operator 串行预测子区间端点，再让多个 fine operator 并行计算各子区间，最后用 \(F-G\) 修正 coarse prediction。这个结构允许不同时间子区间同时跑，但要求每个 worker 能在任意端点由完整状态重启。因此作者把 Circuit 设计成包含系统矩阵、节点电压和系统历史状态向量的可复用 worker，并让异构元件通过统一接口 gather/scatter 自己的历史量。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Eq. (5)）[pdf:E05]（PDF 物理页 5，Fig. 5 与 Component-Based System Architecture）

最后遇到决定性失败模式：对普通 ODE/DAE，端点状态足够；对行波线，端点状态之外还需要 \(t-\tau\) 的历史样本。若 coarse grid 自己插值，它看到的是稀疏、与 fine grid 不一致的历史，下一窗口预测会失真。由此自然得到两项限制：窗口必须短于最小相关时延，使所需历史已由前一完成窗口产生；coarse 与 fine 传输线必须共享 fine-grid 历史缓存，coarse 查询时再做索引换算。[pdf:E04]（PDF 物理页 4，Eq. (17) 后正文）[pdf:E05]（PDF 物理页 5，Fig. 4 与 Eq. (18)）

这条思考路径的核心不是“面向对象更优雅”，而是把可重启的物理状态与计算 worker 绑定起来，让 Parareal 的数学端点状态在 EMT 软件里有可执行的载体；object-oriented C++ 是实现手段，不是单独的数值贡献。

## § 4 — 核心 Intuition

Parareal 用廉价粗步长先猜每个时间片的起点，再让细步长 worker 并行纠正；只要粗解足够接近细解，时间片就能逐轮收敛。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Eq. (5)）

对 EMT 来说，关键不是再造一套统一方程，而是让每个传统元件暴露可重启历史状态，并让粗、细传输线共享细网格历史。窗口短于传输线时延时，当前窗口所需的行波历史已经由前一窗口确定，跨时间片的隐藏依赖就被变成可控的已知输入。[pdf:E05]（PDF 物理页 5，Fig. 4 与正文）

## § 5 — 具体方法与完整 Pipeline

以 IEEE-118 系统发生母线 38 故障为例，完整 pipeline 如下：

1. **元件初始化与系统组装。** 每个 transient component 按当前步长初始化等效参数，通过 `assemble_mat()` 把支路贡献写入全局节点导纳矩阵；`update_i()` 形成右端历史电流，节点方程经 LU 分解和前后代入求解，再由 `update_hist()` 更新元件历史状态。[pdf:E05]（PDF 物理页 5，Fig. 5 与接口说明）[pdf:E06]（PDF 物理页 6，Fig. 6）
2. **建立可重启状态。** 全局状态不只含节点电压 \(v\)，还含各元件历史向量 \(x\)。电感/电容保留电流与电压相关状态，变压器选择 \(\{i,\lambda\}\)，同步机保留 \(\{v_{um},i_{um},\psi_{um},\omega\}\)；这使 coarse/fine worker 能从时间片端点恢复。[pdf:E03]（PDF 物理页 3，Eq. (6)–(11)）[pdf:E04]（PDF 物理页 4，Eq. (12)–(16)）
3. **初始化 coarse grid。** 一个 coarse worker 以较大步长 \(\Delta t\) 串行产生所有时间片端点的初猜 \(G^{(0)}\)。[pdf:E06]（PDF 物理页 6，Initialization）
4. **并行 fine solve。** 第 \(k\) 轮中，各 fine worker 载入对应 coarse 端点状态，用较小步长 \(\delta t\) 完成 \(m\) 步，满足 \(m\delta t=\Delta t\)，得到子区间末端 \(F^{(k+1)}\)。已保证收敛的最前方时间片不再重复启动，因此每轮只需 \(N-k\) 个线程。[pdf:E06]（PDF 物理页 6，Parallel Operation）
5. **传输线历史处理。** 行波线用 Eq. (17) 从 \(t-\tau\) 更新两端历史电流。coarse 与 fine 模型共享 fine-grid 历史缓存，且计算窗口限制为小于传输线传播时延；coarse 查询历史时按 Eq. (18) 换算到 fine-grid 索引。[pdf:E04]（PDF 物理页 4，Eq. (17)）[pdf:E05]（PDF 物理页 5，Fig. 4 与 Eq. (18)）
6. **串行修正与收敛。** worker 并行形成 \(F-G\)，coarse worker 再按时间顺序更新端点状态；Eq. (19) 用相邻两轮 coarse 状态的相对 Euclidean distance 之和判断整个窗口是否收敛。收敛后，fine worker 补齐窗口内所有细步长输出。[pdf:E06]（PDF 物理页 6，Eq. (19)）[pdf:E07]（PDF 物理页 7，Fig. 7）
7. **窗口推进。** 固定全时域版本内存和迭代成本过高，因此正式实现把仿真切成不重叠小窗口。当前窗口完成后，最后一个 subdivision 把状态交给下一窗口的第一个 worker，复用 worker 与 workspace，从而把内存限制在一个窗口。[pdf:E07]（PDF 物理页 7，Fig. 8 与 Windowed Algorithm）
8. **实验工况。** CPU 程序用 C++、Intel TBB 与 Intel MKL 实现，在 IEEE-9、IEEE-39、IEEE-118 上与 sequential EMT、MKL parallel LU 以及 PSCAD/EMTDC 波形比较。IEEE-118 的故障发生在 0.2 s、Bus 38；但论文没有报告开关事件定位、可变步长事件回退、数值精度类型或硬实时调度策略。[pdf:E07]（PDF 物理页 7，Section IV）[pdf:E09]（PDF 物理页 9，实验设置）

论文没有 FPGA 映射：没有 pipeline latency、定点位宽、BRAM/DSP/LUT 资源、片上历史缓存布局或 HIL I/O 时序。若把这项工作用于 FPGA，真正困难的部分会是 fine-history 的带宽与多 worker 状态复制，而不是把 C++ 类机械翻译成硬件；这是基于方法结构的推断，不是论文结论。

## § 6 — 核心数学推导（无形式化数学则跳过）

Parareal 先把 \([t_0,t_{end}]\) 分成 \(N\) 个子区间。若 fine operator 为 \(\mathcal F(T_j,T_{j-1},U_{j-1})\)，所有端点状态满足一组块下三角非线性方程 \(W(U)=0\)。作者从 Newton 更新出发，用便宜的 coarse operator \(\mathcal G\) 近似 \(\mathcal F\) 对状态的作用，得到本文真正执行的修正式：

\[
U_j^{(k)} =
\mathcal F(T_j,T_{j-1},U_{j-1}^{(k-1)})
+\mathcal G(T_j,T_{j-1},U_{j-1}^{(k)})
-\mathcal G(T_j,T_{j-1},U_{j-1}^{(k-1)}).
\]

它的工程含义是：新端点等于“上一轮 fine 结果”加上“本轮与上一轮 coarse prediction 的变化”；coarse 串行传播因果关系，fine 同时计算昂贵细节。[pdf:E02]（PDF 物理页 2，Eq. (1)–(2)）[pdf:E03]（PDF 物理页 3，Eq. (3)–(5) 与 Fig. 1）

节点分析层把线性电路写成

\[
Yv_{n+1}=s_{n+1}-i^{hist}_{n+1},\qquad
i^{hist}_{n+1}=g(x_n,v_n),\qquad
x_{n+1}=h(i^{hist}_{n+1},v_{n+1}).
\]

这里 \(Y\) 是节点导纳矩阵，\(v\) 是节点电压，\(s\) 是源注入，\(x\) 是元件历史量，因而 Parareal 的全局状态是 \(U=\{v,x\}\)。物理上，矩阵求解负责电网瞬时约束，历史向量负责储能元件和动态设备的时间记忆。[pdf:E03]（PDF 物理页 3，Eq. (6)–(8)）

对电感/电容，论文用 Trapezoidal Rule 写成 \(i_{n+1}=G_{eq}v_{n+1}+i^{hist}_{n+1}\)，并强调 Parareal 有两种步长，因此不能像固定步长 EMT 那样省略显式状态。[pdf:E03]（PDF 物理页 3，Eq. (9)–(11)）但必须保留一个 PDF 内部不一致：Eq. (10) 原文印为
\[
G_{eq}^{L}=\frac{2L}{\Delta t},\qquad
G_{eq}^{C}=\frac{\Delta t}{2C},
\]
同时正文称 \(G_{eq}\) 为“equivalent admittance”且 Eq. (9) 使用 \(i=G_{eq}v+\cdots\)。按量纲分析，原式两项均更像阻抗而非导纳。因此本卡忠实记录 PDF，不擅自改成常见 companion-model 形式；复现者应回到代码或作者勘误确认。这是本卡的技术批评，不是对原式的改写。[pdf:E03]（PDF 物理页 3，Eq. (9)–(10)）

传输线的关键 DDE 为
\[
i^{hist}_m(t)=-2Gv_k(t-\tau)-i^{hist}_k(t-\tau),\qquad
i^{hist}_k(t)=-2Gv_m(t-\tau)-i^{hist}_m(t-\tau),
\]
说明当前一端注入取决于另一端在传播时延 \(\tau\) 前的电压和历史电流。为让 coarse worker 读取 fine history，作者给出索引换算
\[
j_{fine}=\operatorname{floor}\!\left(
j_{coarse}\frac{\Delta t}{\delta t}
+\left(\frac{\Delta t}{\delta t}-1\right)\frac{\tau}{\Delta t}
\right).
\]
这不是提高插值阶数，而是明确 coarse 查询在共享细网格历史中的位置；其成立条件是当前窗口所需历史已在前一窗口准备好。[pdf:E04]（PDF 物理页 4，Eq. (17)）[pdf:E05]（PDF 物理页 5，Eq. (18) 与相邻正文）

另一个复现风险是符号不一致：Eq. (5) 与 Fig. 7 都表示把 \(F-G\) 加到新的 coarse state 上，而物理页 6 的一行 prose 在定义 \(P=F-G\) 后写成 \(U=G-P\)。Fig. 7 的加号与标准 Parareal 形式相符，因此实现时应以 Eq. (5) 和 Fig. 7 为准，并把该 prose 视为待作者确认的排版错误。[pdf:E03]（PDF 物理页 3，Eq. (5)）[pdf:E06]（PDF 物理页 6，Sequential Update prose）[pdf:E07]（PDF 物理页 7，Fig. 7）

## § 7 — 实验设计与结论

**问题 1：并行结果是否保持 EMT 波形正确？** 作者在 IEEE-9、IEEE-39、IEEE-118 分别设置三相接地故障，将 parallel-in-time 电压/电流与 sequential 程序叠加，并另与 PSCAD/EMTDC 比较。Fig. 9 的缩放图显示 parallel 与 sequential 曲线近乎重合，正文称结果通过 PSCAD/EMTDC 验证；但论文没有报告标准化的最大误差或 RMS error，所以证据支持“图示一致”，不能外推为所有状态和工况都达到某个未报告误差界。[pdf:E08]（PDF 物理页 8，Fig. 9）[pdf:E09]（PDF 物理页 9，Fig. 9 后正文）

**问题 2：时间并行能否优于 sequential 和 spatial parallel LU？** 在固定 \(T_{window}=200\,\mu s\)、\(\Delta t=40\,\mu s\)、\(\delta t=1\,\mu s\)、5 线程、500 ms 仿真条件下，Table 1 报告 IEEE-9/39/118 的 Parareal 加速分别为 1.12×、1.77×、2.09×；parallel LU 在较小的 IEEE-9 与 IEEE-39 上甚至慢于 sequential，而在 IEEE-118 上才明显受益。答案是：这些案例中 Parareal 的确都获得加速，但小系统仍被同步开销显著侵蚀。[pdf:E09]（PDF 物理页 9，Table 1）

**问题 3：窗口与 coarse step 怎样影响收益？** 对 IEEE-118、5 线程、\(\delta t=1\,\mu s\)、300 ms 仿真，Table 2 的最佳实测组合是 \(T_{window}=200\,\mu s,\Delta t=40\,\mu s\)，平均迭代 1.99 次、仿真时间 170.034 s、加速 2.08×、效率 42%。把窗口增至 400 \(\mu s\) 后，因超过约 200 \(\mu s\) 的最小线时延，平均迭代升至 2.98，加速降为 1.50×；把窗口降到 50 \(\mu s\) 虽可 1 次迭代收敛，但 coarse/fine 工作量比例限制了加速，只得到 1.62×。答案是：窗口并非越大或越小越好，而要同时匹配时延与 coarse/fine 工作量。[pdf:E09]（PDF 物理页 9，Table 2 与解释）

**问题 4：更多线程是否总是更快？** Table 3 固定 \(\Delta t=40\,\mu s,\delta t=1\,\mu s\)，改变线程数。IEEE-118 在 6 线程达到 2.30×，5 线程为 2.05×，16 线程反而只有 1.23×；作者指出测试 CPU 在 16 线程时不能把所有作业真正并行执行，而且较长窗口跨过时延边界会降低预测质量。答案是：线程数存在最优点，本文案例为 5–6 线程，对应 200–240 \(\mu s\) 窗口。[pdf:E10]（PDF 物理页 10，Table 3 与相邻正文）

**问题 5：结果能否直接代表未经修改的标准系统？** 不能。IEEE-39 的线路长度被放大到 60–100 km；IEEE-118 中低于 60 km 的线路被替换为 multiple-PI sections，仅余 61 条线用 Bergeron 模型。作者明确说不做该简化时虽然结果仍可得到，但 parallel-in-time 会退化回 sequential。因此报告的加速依赖经过时延友好化的测试模型，不能直接外推到短线路占主导的真实网络。[pdf:E09]（PDF 物理页 9，Table 1 下实验设置）

## § 8 — Take-aways

**5 句话：**

1. 论文证明了传统节点分析和异构 EMT 元件可以被组织成可重启的 Parareal worker，而不必把整个系统重写为统一 ODE。[pdf:E03]（PDF 物理页 3，Eq. (6)–(8)）[pdf:E05]（PDF 物理页 5，Fig. 5）
2. 真正的新困难来自行波线的历史依赖，不是 DAE 本身；共享 fine-grid 历史并限制窗口小于传播时延是关键机制。[pdf:E04]（PDF 物理页 4，Eq. (17)）[pdf:E05]（PDF 物理页 5，Fig. 4）
3. windowed Parareal 把长时域的内存与收敛问题压缩到单个小窗口，并复用 worker/workspace。[pdf:E07]（PDF 物理页 7，Fig. 8）
4. IEEE-118 在 6 线程上达到 2.30× 加速、38.3% 效率，但不是线程越多越快。[pdf:E10]（PDF 物理页 10，Table 3 后正文）
5. 最关键的限制是加速依赖传输线时延和经修改的网络参数；短线较多时算法可能退化为顺序执行。[pdf:E09]（PDF 物理页 9，实验设置）

**3 句话：** 这项工作把系统级 EMT 的传统元件状态显式化，使 coarse/fine solver 可以在任意时间片端点重启。[pdf:E05]（PDF 物理页 5，Fig. 5）它通过共享 fine-grid 传输线历史和时延约束窗口，恢复了 Parareal 所需的 coarse/fine 一致性。[pdf:E05]（PDF 物理页 5，Fig. 4）得到的 CPU 加速真实但强烈依赖时间尺度，不应当被理解成对任意电网规模都稳定的通用倍速器。[pdf:E09]（PDF 物理页 9，Tables 1–2）[pdf:E10]（PDF 物理页 10，Table 3）

**1 句话：** 这篇论文的核心贡献，是把传输线历史从 Parareal 的隐藏依赖变成共享、受窗口约束的显式状态，从而让传统 EMT 模型获得有限但可测的时间并行加速。[pdf:E05]（PDF 物理页 5，Fig. 4）

## § 9 — 最脆弱的假设

最脆弱的假设是：**存在足够大的、仍小于关键传输线传播时延的时间窗口，使 coarse prediction 既准确，又能装下足够多的并行工作。** 如果真实系统大量线路的 \(\tau\) 很短，窗口就必须缩小；窗口太小会使每个 fine worker 的计算量不足以摊薄 coarse solve、同步和误差评估，甚至没有可用的时间并行度。若强行增大窗口，当前窗口会需要尚未准备好的历史量，迭代次数和误差随之增加。[pdf:E05]（PDF 物理页 5，Fig. 4 与窗口小于 \(\tau\) 的条件）[pdf:E09]（PDF 物理页 9，Table 2 解释）

论文给出的正面证据是：设置约 200–240 \(\mu s\) 的最小时延后，5–6 线程恰好获得最佳加速；400 \(\mu s\) 窗口跨过最小时延后性能下降。[pdf:E09]（PDF 物理页 9，Table 2）[pdf:E10]（PDF 物理页 10，Table 3 后正文）但更强的负面证据也来自论文自身：IEEE-39 的线路被放大到 60–100 km，IEEE-118 的短于 60 km 线路被改成 multiple-PI；不简化时 parallel-in-time 退回 sequential。[pdf:E09]（PDF 物理页 9，实验设置）

因此，本文并没有证明这种方法能直接加速原始参数的典型输配电网络。它证明的是：当系统的最短显著时延与可用线程形成合适窗口时，方法可以工作。这是比“系统规模决定加速”更有价值也更窄的结论。

## § 10 — 最小复现实验

一周内最有信息量的复现不是重建全部 object-oriented EMT 元件库，而是实现一个包含 Bergeron 线历史缓存的最小三相网络，并验证“窗口/时延比决定收敛与加速”。

1. **数据与模型：** 构造一个等值三相源、RL 支路、单条 Bergeron 线和三相接地故障；固定 fine step \(\delta t=1\,\mu s\)，准备 sequential trapezoidal EMT 作为参考。
2. **实现：** 做一个 coarse step \(\Delta t=40\,\mu s\) 的 windowed Parareal；coarse/fine 共享 fine-history，并按 Eq. (18) 索引。只需实现 RL、线路和故障电阻，不复现变压器或同步机。[pdf:E05]（PDF 物理页 5，Eq. (18)）[pdf:E07]（PDF 物理页 7，Fig. 8）
3. **扫参：** 选择三种传播时延 \(\tau\)，对每种扫 \(T_{window}/\tau=\{0.5,1.0,2.0\}\)，并扫 2、4、6 个 worker；保持总仿真时长、容差和硬件不变。
4. **测量：** 报告每窗口平均迭代数、相对状态误差、wall-clock speed-up、parallel efficiency、历史缓存读写量；误差指标用 Eq. (19)，另加相对于 sequential 的最大归一化电压/电流误差，避免只看波形叠图。[pdf:E06]（PDF 物理页 6，Eq. (19)）
5. **支持条件：** 当 \(T_{window}<\tau\) 时，在误差不恶化的条件下迭代数和 wall time 显著优于 \(T_{window}>\tau\)，且 4–6 worker 至少出现一个实测加速区间。
6. **反驳条件：** 在共享 fine-history 正确实现后，窗口跨越 \(\tau\) 并不系统性增加迭代/误差，或窗口小于 \(\tau\) 仍无法在任何 worker 数下击败 sequential。前者会削弱作者对时延边界的机制解释，后者会说明加速主要来自案例或实现细节。

复现时必须先处理 §6 的两个记号冲突：LC companion 参数不能直接照抄 Eq. (10) 而不做量纲/代码核验；Parareal 修正符号应以 Eq. (5) 与 Fig. 7 为准。[pdf:E03]（PDF 物理页 3，Eq. (5)、(9)–(10)）[pdf:E07]（PDF 物理页 7，Fig. 7）

## § 11 — 最强反例设计

最强反例是选一个“拓扑规模很大但电气传播时延很短”的网络，例如短电缆密集的城市配电网或大规模电力电子园区，而不是再测试一个更大的 IEEE 输电网。保留所有原始线路长度，不允许把短线替换为 multiple-PI 或人为拉长；再加入频繁开关事件，使每个小窗口都可能跨越新的离散状态变化。

实验采用与论文相同的 \(\delta t\)、误差容差和 CPU，比较三种方法：sequential EMT、MKL parallel LU、本文 windowed Parareal。横轴不是母线数，而是最小时延 \(\tau_{min}\) 与同步/粗解开销的比值；同时报告不得简化线路时的加速。论文自身已经显示短线未经简化会使算法退回 sequential，因此这个反例直接攻击核心机制，而不是泛泛质疑 C++ 开销。[pdf:E09]（PDF 物理页 9，IEEE-39/118 线路处理与退化说明）

如果大网络在原始短线参数下仍能保持 \(>1\) 的稳定加速，且随着 \(\tau_{min}\) 缩短没有明显恶化，那么“传输线时延是主要性能边界”的解释会被削弱，可能真正起作用的是 coarse model、负载均衡或特定模型简化。反过来，若 worker 数增加却加速迅速降到 1 以下，就支持本文所揭示的脆弱性。该反例还应强制报告事件附近误差，因为 Fig. 9 只展示了三个故障案例的图形一致性，没有给出跨大量离散事件的统计误差界。[pdf:E08]（PDF 物理页 8，Fig. 9）[pdf:E10]（PDF 物理页 10，16 线程性能下降）

## § 12 — Follow-up Research Idea

**候选研究方向：把“固定按时间切片”改成“按因果可用历史自适应切片”的 event- and delay-aware temporal scheduler。** 相关工作尚未充分检索，本卡不声称该方向具有 novelty。

**（a）未满足需求。** 本文要求窗口小于最小传输线时延，最短的一条线就可能限制整个系统；而实际网络常同时存在长输电线、短电缆、电力电子快速控制和稀疏开关事件。用一个全局固定窗口会让局部最坏时间尺度绑架全部 worker。[pdf:E09]（PDF 物理页 9，短线简化与 Table 2 解释）

**（b）潜在研究价值。** 新目标不是“再提高一点 Parareal 加速”，而是让调度器显式维护每个元件历史数据的 causal availability：只要某个子图所需的延迟历史已经确定，它就可以跨更大的时间块；短时延或事件密集区则缩小时间块或暂时回退顺序求解。这样研究问题从统一时间窗口优化变成异构因果前沿上的任务调度，可能扩大方法对原始网络参数的适用范围。

**（c）可借鉴工具。** 可以借鉴 discrete-event simulation 的 conservative synchronization、task graph runtime 的 dependency tracking，以及 multirate integration 的局部步长控制。Circuit/TransientComponent 已经提供元件级历史 gather/scatter 接口，可把每个历史区间的可用性登记为任务依赖，而不是新增一套与模型分离的全局状态。[pdf:E05]（PDF 物理页 5，Fig. 5 与历史接口）[pdf:E07]（PDF 物理页 7，window state transfer）

**（d）首个证伪实验。** 在同时含 20 \(\mu s\)、200 \(\mu s\)、2 ms 三档传播时延的网络上，比较固定窗口 Parareal 与自适应因果调度器。保持 fine solve 次数预算和精度相同；若自适应方法不能在不增加误差的情况下减少串行等待或提高 wall-clock speed-up，或者依赖追踪开销吞掉收益，则该方向被第一轮实验否定。

**（e）与本文的实质区别。** 本文通过共享 fine-history 和全局 \(T_{window}<\tau_{min}\) 来消除依赖。[pdf:E05]（PDF 物理页 5，Fig. 4）候选方法不再把最小时延当作全局窗口上限，而是把每个元件的历史可用区间当作运行时依赖，允许网络不同部分拥有不同的 temporal frontier。它改变的是并行任务的定义和正确性条件，不只是增加一个预测器或更换测试系统。
