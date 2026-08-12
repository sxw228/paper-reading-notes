# Hierarchical Linking-Domain Extraction Decomposition Method for Fast and Parallel Power System Electromagnetic Transient Simulation

作者：Tong Duan；Venkata Dinavahi  
出处：IEEE Open Journal of Industry Applications，Vol. 2，pp. 194–203  
年份：2021  
DOI：10.1109/OJIA.2021.3096518  
Zotero key：E8QGIU3S  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文处理的不是笼统的“怎样并行做 EMT”，而是一个更具体的工程矛盾：原始 linking-domain extraction（LDE，链接域提取）能把非重叠子系统通过小型 linking-domain 重新耦合，但它以计算并保存整个导纳矩阵逆为中心；系统变大后，全逆通常变稠密，存储与 I/O 先失去可扩展性，而单层分解留下的大块矩阵求逆也仍然昂贵。作者因此把目标改写为两件事：第一，只求解每个时步所需的节点电压，不显式形成全系统逆；第二，把一级子块的求逆继续递归分解，形成 hierarchical LDE（H-LDE，层次化 LDE）。论文摘要把核心 claim 限定为：四层 H-LDE 在 IEEE 118-bus 上可顺序或并行执行，并在“一定系统规模内”优于经典 LU 与稀疏 KLU，而不是宣称对任意规模都占优。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 9，Section VI）

这个问题重要，是因为 EMT 仿真需要反复求解离散后的网络方程；当步长很小、时步很多时，单步 matrix solve 的延迟和中间矩阵的存储都会被放大。H-LDE 的潜在价值不是改变电磁暂态模型本身，而是保持同一线性方程的代数等价性，同时降低逆矩阵物化成本、暴露块级并行，并让分解深度与具体硬件开销共同决定。论文后续实验使用 20 μs 步长、累计 5000 个时步来放大这一求解器差异。[pdf:E03]（PDF 物理页 7，Section V-A）

## § 2 — 前人工作与不足

以下均是论文对相关文献的概括，本任务没有用这些参考文献全文做独立复核。论文给出的 prior-work 图谱有四类。第一类是 Schur complement 一类的 matrix-based non-overlapping decomposition；第二类是 transmission line modeling（TLM）和 latency insertion method（LIM）一类依靠连接延迟解耦的非重叠方法；第三类是作者此前提出的原始 LDE；第四类是 EMTDC/PSCAD 中的 LU，以及 SPICE 等仿真器常用的 KLU、NICSLU 稀疏直接法。[pdf:E04]（PDF 物理页 1，Section I）[pdf:E05]（PDF 物理页 2，Section I）

真正被本文直接修复的是原始 LDE 的两个缺陷。其一，LDE 先求整个导纳逆，而大规模稀疏导纳矩阵的逆通常是稠密的，因此存储远高于直接解方程；其二，原始 LDE 只分解一次，一级子块仍可能很大，子块求逆继续成为瓶颈。本文的改进分别对应“只应用逆、不保存全逆”和“对子块递归使用 LDE”。[pdf:E05]（PDF 物理页 2，Section I）

稀疏 LU 并没有被本文消除。论文自己的结果显示，KLU 在更大规模上重新占优，因此 H-LDE 的定位是低 separator、有限规模、可利用块并行的替代路线，而不是通用 sparse solver 的全面替代。[pdf:E06]（PDF 物理页 8，Table I）[pdf:E07]（PDF 物理页 9，Table II）[pdf:E08]（PDF 物理页 9，Section V-B）TLM/LIM 也没有在实验中被直接比较，源 PDF 只把它们列为另一种分解范式；因此不能据本文断言 H-LDE 已经优于这些 latency-based 方法。

## § 3 — 重建作者的思考路径

以下是基于全文证据的逆向重建，不是作者逐句陈述的研究日志。

1. 已知 LDE 的 Woodbury 型分解是精确的，问题不在数学等价性，而在“把精确逆完整物化”这个执行选择。既然每个 EMT 时步只需要 \(G^{-1}i_{eq}\)，首先应把 inverse formation 改写成 inverse application。[pdf:E09]（PDF 物理页 2，Section II-A，Eq. (1)–(3)）
2. 链接矩阵 \(C\) 每列只有一个 \(-1\) 和一个 \(+1\)，其余为零，说明全局耦合只通过低维边界变量发生。于是可以先在各 diagonal block 内独立求解，再解一个 \(k\)-维 linking-domain 方程，而不必做一般稠密乘法。[pdf:E09]（PDF 物理页 2，Section II-A）[pdf:E10]（PDF 物理页 3，Eq. (5)–(8)）
3. 即便不形成 \(G^{-1}\)，一级算法仍需要 \(G_d^{-1}\)。这提示“LDE 本身还可以用来算 LDE 所需的块逆”：对子块再分解、再求更小块逆，直到叶节点足够小，再自底向上组装。[pdf:E10]（PDF 物理页 3，Section III-A）
4. 递归不能无限加深，因为每层都新增 linking-domain 的 \(k_i^3\) 成本，GPU 还新增 child-kernel launch 与同步开销。于是需要把拓扑 separator 大小、块大小、分解层数和硬件并行能力放进同一个停止条件。[pdf:E11]（PDF 物理页 4，Eq. (9)–(14)）[pdf:E12]（PDF 物理页 5，Eq. (15)–(16)）
5. 最后再选择硬件映射：GPU 的 dynamic parallelism 对应树形父子 kernel，但只把前两层并行、后两层顺序执行，以免更深层的 launch overhead 吞掉收益。[pdf:E13]（PDF 物理页 5，Section IV-A）

这条路径的关键不是“多分几层”，而是先改变求解对象，再把递归深度变成一个由 separator 与硬件共同约束的设计变量。

## § 4 — 核心 Intuition

H-LDE 把一个大的全局逆矩阵，改写成许多局部块逆加一个低维边界耦合求解；第一层只把逆作用到当前右端项，避免保存全系统稠密逆。[pdf:E10]（PDF 物理页 3，Eq. (5)–(8)）局部块若仍太大，就继续用同一套链接域分解递归求逆，再从叶节点自底向上组装。[pdf:E14]（PDF 物理页 7，Fig. 5）这个机制只有在每层跨块链接数 \(k_i\) 足够小、且新增层的并行启动或顺序修正成本低于直接求逆时才成立。[pdf:E11]（PDF 物理页 4，Principle 1）[pdf:E12]（PDF 物理页 5，Principle 2）

## § 5 — 具体方法与完整 Pipeline

以论文的 IEEE 118-bus 例子为主线，完整 pipeline 如下。

1. **输入与离散方程。** 输入是当前 EMT 时步的网络导纳矩阵 \(G\) 和等效电流向量 \(i_{eq}\)，输出是节点电压 \(v\)，基本方程为 \(Gv=i_{eq}\)。论文直接从该 nodal equation 开始，没有给出各元件 companion model、积分公式或数值离散推导。[pdf:E10]（PDF 物理页 3，Eq. (5)）
2. **一级拓扑分区。** 118-bus 系统含 118 buses、54 generators、177 lines、9 transformers 和 91 loads。一级把系统分成大小为 30、30、28、30 的四个子系统，跨子系统链接数为 \(k_1=15\)。[pdf:E13]（PDF 物理页 5，Section IV-A/B）四层分区的实际拓扑、每层 cut 和链接数见 Fig. 4。[pdf:E15]（PDF 物理页 6，Fig. 4）
3. **继续递归分解。** 二级把典型 30-node 子系统分成两个 15-node 子系统；三级再把 15 分成 8 和 7；四级把叶块降到 4 或 3 个节点。实际计算顺序不是从上往下解，而是从第四层开始求小逆，再逐层向上组装。[pdf:E16]（PDF 物理页 6，Section IV-B）
4. **叶节点与自底向上组装。** 叶层直接求小矩阵逆；上一级用本层 linking-domain 的 \(Q\) 修正并组装父块逆。Fig. 5 展示了 \(4\times4/3\times3\) 叶块如何组装成 \(8\times8/7\times7\)、再到 \(15\times15\)、最终形成一级的 \(30\times30\) 或 \(28\times28\) 块逆。[pdf:E14]（PDF 物理页 7，Fig. 5）在该配置中，实际需要求逆的最大 block matrix 为 \(4\times4\)，最大 \(Q\) 为 \(6\times6\)；一级 \(15\times15\) linking-domain 在变化矩阵情形中是解线性方程，而不是显式求逆。[pdf:E16]（PDF 物理页 6，Section IV-B）[pdf:E17]（PDF 物理页 9，Changeable Conductance Matrix）
5. **每时步求解。** 先在一级各块内计算 \(v_{DBM}=G_d^{-1}i_{eq}\)，再形成 \(T=G_d^{-1}C\)，解 linking-domain 方程得到 \(v_{LDM}\)，最后输出 \(v=v_{DBM}-Tv_{LDM}\)。因为 \(C\) 是极稀疏的符号关联矩阵，相关乘法可以简化成选取、加减和少量累加。[pdf:E10]（PDF 物理页 3，Eq. (7)–(8) 及四步 procedure）
6. **常量矩阵与变化矩阵两条执行路径。** 若 \(G\) 恒定，\(G_d^{-1}\)、\(C\) 和 \(Q\) 可预先得到，每步只做矩阵乘法，使用 Eq. (17)；若矩阵数值变化，则执行 Eq. (6)–(8)，但在非零位置不变时可以复用同一层次分区和装配结构。[pdf:E18]（PDF 物理页 8，Eq. (17) 与 Constant Conductance Matrix）[pdf:E17]（PDF 物理页 9，Changeable Conductance Matrix）
7. **并行映射。** CPU 版本全顺序执行；GPU 版本使用 CUDA dynamic parallelism，把前两层作为嵌套并行，后两层顺序执行，论文记为总层数 \(r=4\)、并行层数边界 \(q=2\)。[pdf:E13]（PDF 物理页 5，Section IV-A）输出仍是每时步的节点电压向量。论文未报告 floating-point precision、kernel 内存布局、开关事件调度、完整 history-item 更新实现，也没有 FPGA 映射；正式平台只有 Intel i5-7300HQ CPU 与 NVIDIA Tesla V100 GPU。[pdf:E19]（PDF 物理页 7，Section V）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的形式化核心，而且它本质上是 Woodbury identity 在网络分区上的结构化应用。

先把导纳矩阵分成 block-diagonal 部分和跨域链接部分：

\[
G=G_d+L,\qquad L=C\Lambda C^\top .
\]

\(G_d\) 包含各非重叠子系统内部导纳；\(C\in\mathbb{R}^{N\times k}\) 是链接的有向关联矩阵，每列只含一个 \(-1\)、一个 \(+1\)；\(\Lambda\in\mathbb{R}^{k\times k}\) 为对角矩阵，\(k\) 是跨域链接数。[pdf:E09]（PDF 物理页 2，Eq. (1)–(2)）Woodbury identity 给出

\[
G^{-1}=G_d^{-1}-G_d^{-1}CQC^\top G_d^{-1},
\qquad
Q=(\Lambda^{-1}+C^\top G_d^{-1}C)^{-1}.
\]

[pdf:E09]（PDF 物理页 2，Eq. (3)）[pdf:E10]（PDF 物理页 3，Eq. (4)）直觉是：先忽略跨域链接，各块独立响应；再用一个只与边界链接数 \(k\) 有关的 correction，把跨域耦合补回来。

原始 LDE 会把上述 \(G^{-1}\) 整体算出并保存。本文把它直接作用到右端项：

\[
v_{DBM}=G_d^{-1}i_{eq},
\]
\[
(\Lambda^{-1}+C^\top G_d^{-1}C)v_{LDM}=C^\top v_{DBM},
\]
\[
v=v_{DBM}-G_d^{-1}Cv_{LDM}.
\]

[pdf:E10]（PDF 物理页 3，Eq. (5)–(8)）这里没有引入近似：只是把“形成逆矩阵”改成“解一个 \(k\)-维边界方程，再把修正作用回各块”。若一级被等分成 \(m\) 个子块，作者给出的存储量为

\[
O\!\left(m(N/m)^2+k^2\right)=O\!\left(N^2/m+k^2\right),
\]

相对原始 LDE 约减少 \(m\) 倍，但仍高于真正利用 sparsity 的 LU/KLU。[pdf:E10]（PDF 物理页 3，Section II-B）

层次化部分令第 \(i\) 层每个父块被分成 \(m_i\) 个大小约为 \(N_i\) 的子块，跨域链接数为 \(k_i\)，满足 \(N_{i-1}=m_iN_i\)。并行递推的主项是

\[
O[f_p(N_{i-1},k_{i-1})]
 =O[f(N_i,k_i)+k_i^3+t_{p(i)}],
\]

顺序递推的主项是

\[
O[f_s(N_{i-1},k_{i-1})]
 =O[m_i f_s(N_i,k_i)+k_i^3],
\]

叶层再落到 \(N_r^3\) 级的小矩阵求逆。[pdf:E11]（PDF 物理页 4，Eq. (9)–(14)）由此得到两个 heuristic：非末层尽量令 \(k_i<N_i\)，末层在 \(k_r\) 与 \(N_r\) 间取平衡；新增一层还必须满足“下一层计算、\(k_i^3\) 修正与并行启动开销之和小于直接求逆”的 Eq. (15)/(16)。[pdf:E11]（PDF 物理页 4，Principle 1）[pdf:E12]（PDF 物理页 5，Eq. (15)–(16)）

这不是严格的渐近最优性定理。作者明确假设同层子块大小和链接数近似均匀，并承认该假设不严谨；因此这些式子更适合作为 topology/hardware co-design 的成本模型，而不是对任意电网图的复杂度保证。[pdf:E11]（PDF 物理页 4，Section III-B）

## § 7 — 实验设计与结论

1. **问题：层次化和 GPU nested parallelism 是否真的比单层分解快？ → 实验：** 在 IEEE 118-bus 上，把 Gauss–Jordan（GJ）作为基线，比较 Schur complement、original LDE 和 1–4 层 H-LDE；步长为 20 μs，只累计 5000 步的 matrix-equation solution time。**答案：** H-LDE 在 4 层达到相对 GJ 的 36.1× speed-up，约为 original LDE 最佳结果的两倍；但 3 层到 4 层只从 35.4× 增到 36.1×，说明层数收益已明显饱和。[pdf:E03]（PDF 物理页 7，Section V-A）[pdf:E20]（PDF 物理页 8，Fig. 6）
2. **问题：恒定导纳矩阵时，顺序 H-LDE 能否胜过 LU/KLU？ → 实验：** 在 39、57、118、300-bus 标准系统以及生成的 400/500/600-bus 系统上比较 5000 步总时间。**答案：** 400-bus 时 H-LDE 为 237 ms、KLU 为 249 ms，H-LDE 仅领先 1.05×；到 500-bus 和 600-bus，H-LDE 分别为 396 ms、707 ms，而 KLU 为 298 ms、361 ms，speed-up over KLU 降为 0.75 和 0.51。[pdf:E06]（PDF 物理页 8，Table I）
3. **问题：矩阵数值随时间变化时，层次结构是否仍有收益？ → 实验：** 在同一组规模上令负载随时间变化，执行完整 Eq. (6)–(8)，并与 dense LU 和 KLU 比较。**答案：** 400-bus 时 H-LDE 为 2476 ms、KLU 为 3493 ms，对 KLU 为 1.41×；500-bus 和 600-bus 时该比值降为 0.80 和 0.39。相对没有 sparse technique 的 LU，H-LDE speed-up 随规模从 2.39 增至 16.68，说明它主要击败的是 dense/block-unaware 路线，而非大规模稀疏直接法。[pdf:E07]（PDF 物理页 9，Table II）
4. **问题：这些结果能外推到完整 EMT 实时仿真吗？ → 实验实际覆盖：** GPU 比较明确排除了各电力设备的 history-item 更新，只记录矩阵方程求解；CPU 表也说明是 pure matrix equation solution latency。生成的 400–600-bus 图使用 row density 4，变化矩阵案例主要改变负载数值并保持结构可复用。[pdf:E03]（PDF 物理页 7，Section V-A）[pdf:E18]（PDF 物理页 8，Table I 下方说明）[pdf:E21]（PDF 物理页 8，Section V-B）**答案（基于证据的判断）：** 论文充分支持“特定低密度拓扑和特定平台上的 solver kernel 加速”，但没有给出端到端实时步长、波形误差、残差、跨平台复现、自动分区质量或结构频繁变化时的证据，不能把 36.1× 直接外推成完整 EMT 仿真 speed-up；论文结尾也只把适用范围表述为一定规模内，并建议未来结合 sparse techniques。[pdf:E02]（PDF 物理页 9，Section VI）

## § 8 — Take-aways

**5 句话：** ① H-LDE 的首要贡献是把全逆矩阵物化改成 block solve 加低维 linking-domain solve，保持代数等价而显著降低存储。[pdf:E10]（PDF 物理页 3，Eq. (5)–(8)） ② 第二个贡献是递归计算一级块逆，让大块求逆变成小叶块求逆和自底向上修正。[pdf:E14]（PDF 物理页 7，Fig. 5） ③ 层次越深并不必然越快，收益由 separator \(k_i\)、叶块 \(N_i\) 和硬件启动/同步开销共同决定。[pdf:E11]（PDF 物理页 4）[pdf:E12]（PDF 物理页 5） ④ 118-bus GPU kernel 结果支持四层结构相对单层 LDE 的明显加速，但改进在第三到第四层已经接近饱和。[pdf:E20]（PDF 物理页 8，Fig. 6） ⑤ H-LDE 在约 400-bus 以内可与 KLU 竞争，规模继续增大时 sparse LU 的可扩展性重新占优。[pdf:E06]（PDF 物理页 8，Table I）[pdf:E07]（PDF 物理页 9，Table II）

**3 句话：** ① 这是一篇把 Woodbury 结构、图分区和硬件执行开销结合起来的 solver co-design 论文。 ② 它最可信的结论是“低 separator、有限规模、可复用层次结构下，H-LDE 可降低求解延迟”，而不是“层次分解普遍优于稀疏直接法”。 ③ 真正决定方法边界的是每层 linking-domain 的增长速度，而不是总节点数本身。

**1 句话：** H-LDE 用小边界问题和递归小块逆替代大规模全逆，但它的成功条件是电网图必须存在适合目标硬件的低 separator 层次。

## § 9 — 最脆弱的假设

以下是基于论文方法与实验边界的推断。最脆弱的假设是：**导纳图存在一个可复用的多层低 separator 分区，使每个非末层的 \(k_i\) 始终明显小于块规模 \(N_i\)，且新增层的修正与调度开销低于直接求逆。**这不是辅助假设，而是 H-LDE 能把 \(N_i^3\) 成本换成小块计算的必要条件；一旦 \(k_i\) 随块规模快速增长，\(k_i^3\) 会成为主项，递归反而增加工作量。[pdf:E11]（PDF 物理页 4，Principle 1）[pdf:E12]（PDF 物理页 5，Principle 2）

它在实际中可能失效于高度网状的 AC/DC 网络、跨区耦合密集的 converter-dominated grid，或者任何难以做平衡低 cut 的拓扑；即使原图稀疏，稀疏也不自动等于“每一层都具有小 separator”。论文给出的正面证据是手工构造的 118-bus 四层分区，以及 row density 为 4 的生成网络；自动多层分区被明确留作未来工作。[pdf:E22]（PDF 物理页 7，Section IV-C）[pdf:E21]（PDF 物理页 8，Section V-B）论文自己的反向信号是 H-LDE 在 500/600-bus 上已经落后 KLU，说明块逆的 storage/I/O 与 separator 修正会吞掉优势。[pdf:E06]（PDF 物理页 8，Table I）[pdf:E07]（PDF 物理页 9，Table II）

仍缺少的证据包括：对同一规模不同 graph separator profile 的系统性 sweep、自动分区算法与手工分区的差距、非零结构变化后能否快速重建 hierarchy，以及不同 memory hierarchy/parallel launch cost 下的 crossover。没有这些实验，方法的真正适用域应表述为“具有可复用低 separator hierarchy 的中小规模网络”。

## § 10 — 最小复现实验

一周内不必复现完整 PSCAD 模型，先验证最核心的代数与性能机制。

- **数据。** 构造一组严格对角占优、conductance-like 的稀疏矩阵。主数据按论文 118-bus 配置设 \(N=118\)，一级块大小 30/30/28/30、\(k_1=15\)，再按 15→8+7、叶块 4 或 3 的层次生成；另做一组保持 \(N\) 和行密度不变、只逐步增加跨块链接 \(k_i\) 的压力数据。[pdf:E13]（PDF 物理页 5，Section IV-B）[pdf:E16]（PDF 物理页 6，Section IV-B）
- **实现。** 用 double precision 实现四条路径：直接 dense solve、显式形成全逆的 original LDE、Eq. (7)–(8) 的 improved one-level LDE、以及 \(r=1\ldots5\) 的 recursive H-LDE。恒定矩阵测试 5000 个不同 RHS；变化矩阵测试固定 sparsity pattern、每步改变数值。
- **测量。** 同时记录相对残差 \(\|Gv-i\|_2/\|i\|_2\)、与直接解的相对差、预处理时间、5000 次求解总时间、peak resident memory，以及各层的 \(N_i\)、\(k_i\)、\(Q_i\) 大小和耗时。
- **预注册判据。** 正确性支持条件是 H-LDE 与直接解在 double precision 下达到预设的 \(10^{-10}\) 量级相对误差；机制支持条件是小 \(k_i\) 数据上存在有限最优层数、H-LDE 明显减少 original LDE 的内存并降低总时延，而且随着 \(k_i\) 增大出现由 \(k_i^3\) 主导的可预测 crossover。若在统一 BLAS、统一线程数和统一内存布局后仍无速度或内存优势，或者层数/\(k_i\) sweep 不符合成本模型，就应反驳论文最核心的工程 claim，而不是把失败归因于“实现还不够优化”。

## § 11 — 最强反例设计

最有力的反例不是把网络简单做成稠密矩阵，而是保持论文使用的典型行密度约为 4，同时构造 **expander-like 的随机正则导纳图**：节点数、非零数和数值条件与论文生成系统相近，但任何平衡多层切分都保留大量跨块边。这样可以隔离“稀疏性”与“低 separator hierarchy”这两个常被混淆的属性。[pdf:E21]（PDF 物理页 8，Section V-B）

实验对每个 \(N\in\{118,300,400,500,600\}\) 生成多组随机种子，用同一个 graph partitioner 搜索多层分区，并给 H-LDE 充分的调参机会；随后与 KLU、one-level LDE 比较 \(k_i\) 分布、\(Q_i\) 尺寸、内存流量和 5000 步总时间。反例的预测是：即使原矩阵保持稀疏，\(k_i\) 仍与块规模同阶增长，linking-domain solve 和 correction 迅速主导，增加层数不再降低延迟。若 H-LDE 在这种图族上仍稳定胜过 KLU，说明本文的 separator 假设比预期更宽；若其 speed-up 崩溃而 KLU 保持扩展性，就能把论文结果的替代解释锁定为“测试图具有有利的层次 separator”，而不是“层次化 LDE 对一般稀疏电网都更快”。

## § 12 — Follow-up Research Bet

**主押注（候选判断，不声称 novelty）：窗口化边界响应 H-LDE 的多 FPGA 空间数据流。**新的研究问题是：能否把 H-LDE 每个时步交换的 \(k_i\)-维边界电压向量，提升为一个长度为 \(W\) 的有限时域 boundary-response operator，使每个子树一次推进多个 EMT 时步，并在多 FPGA 之间只流动边界响应块，而不是每个时步都做全局同步？这首次瞄准的能力是：在不依赖 latency-based transmission-line link 解耦的前提下，把全局耦合 EMT 从“逐步同步的 matrix solver”改造成“跨芯片连续流动的时空数据流”。

核心因果链是：\(C\) 只编码少量带符号边界链接，一级求解已被压缩为 \(k\)-维方程；四层 118-bus 配置的实际小逆只有 \(4\times4\) block 和 \(6\times6\) \(Q\)，说明子树内部可以被编译成紧凑的局部线性响应。[pdf:E09]（PDF 物理页 2，Eq. (1)–(3)）[pdf:E16]（PDF 物理页 6，Section IV-B）把单步 \(v_{LDM}\) 改成窗口内“边界输入历史 → 边界输出历史”的 block-lower-triangular operator 后，H-LDE 树可在时间维上组合这些 operator；每个 FPGA 固定承载一棵子树，片上 pipeline 连续推进局部状态，芯片间通信只围绕 boundary dimension 展开。它同时改变了状态表示（向量变有限时域 operator）、时间尺度（单步变窗口）、硬件映射（nested kernel 变空间固定数据流）和评价对象（单次 matrix solve latency 变端到端 sustained EMT throughput）。

全文给出的直接动机有两处：更深 GPU 层次的收益被 child-kernel launch/synchronization 吞噬，3 层到 4 层 speed-up 几乎饱和；更大系统上 H-LDE 又因 block storage 与 I/O 输给 KLU。[pdf:E12]（PDF 物理页 5，Eq. (15)）[pdf:E20]（PDF 物理页 8，Fig. 6）[pdf:E18]（PDF 物理页 8，Table I 后讨论）窗口化 operator 加空间固定映射的目标不是再加一个调度模块，而是同时删除逐时步全局 barrier 和 GPU 动态启动这两个执行对象。

基本设计变量变为 \(W\)、各层 \(k_i\)、层数 \(r\)、operator 的存储基、子树到 FPGA 的放置、片间带宽和本地时钟/步长配比。最大研究收益是把 H-LDE 从中小规模单设备 solver 扩展成可横向扩展的实时 EMT fabric；最大科学风险是时间窗口内的 boundary operator 发生 fill-in，存储可能按 \(Wk_i^2\) 甚至更快增长，或者矩阵数值变化使 operator 重建成本抵消同步收益。

首个证伪实验应在相同精度、时钟、分区和内存接口下比较三种实现：\(W=1\) 的流式 H-LDE、\(W>1\) 的 boundary-response H-LDE、以及只做普通 batched RHS 的 H-LDE。测试 118/300/400/600-bus 的恒定矩阵与固定 sparsity-pattern 变化矩阵，并把设备/history 更新纳入端到端计时。若 \(W>1\) 的收益不超过普通 batching，或 off-chip bytes 与全局同步次数没有按预测下降，则“新表示带来能力”这一机制被否证；若在相同硬件流水线下只有 boundary operator 版本随 \(W\) 提升 sustained throughput，且误差仍与逐步求解一致，才支持该因果链。

与本文最近的内部对照相比，original LDE、H-LDE、Schur 和 KLU 都以单时步 nodal vector solve 为基本对象，TLM/LIM 则依赖连接延迟来解耦；该押注改的是 problem、mechanism、representation 和 experimental object，而不只是给原求解器换硬件。由于本任务禁止外部检索，这里只能依据源 PDF 做候选判断，不能声称它相对 2021 年后的工作具有 novelty。

**Wild-card alternative：** 把分区对象从 bus graph 改成电力电子变换器的有限导纳状态超图，预编译各局部状态共享的层次 Woodbury 子表达式，以“整组可达拓扑的联合吞吐量”而非单一轨迹 latency 作为新任务和评价对象。
