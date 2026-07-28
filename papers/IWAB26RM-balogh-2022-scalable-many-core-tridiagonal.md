# Scalable Many-Core Algorithms for Tridiagonal Solvers

- 作者：Gábor D. Balogh, Tobias S. Flynn, Sylvain Laizet, Gihan R. Mudalige, István Z. Reguly
- 出处：*Computing in Science & Engineering*, 24(1), 2022
- DOI：10.1109/MCSE.2021.3130544
- Zotero key：IWAB26RM

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** 论文研究的是：当一批独立三对角线性系统的长度或总数据量已经超过单个 CPU/GPU 时，怎样把求解分布到多节点、多 GPU 上，同时控制 reduced system 的通信、同步和内存开销。三对角系统常由多维 PDE 的隐式离散产生，应用包括 CFD、计算电磁学、计算金融和图像处理。作者以 Xcompact3d 为例：一个时间步可能需要最多 150 批三对角求解；对 \(1024^3\) 网格，一次 batched solve 就包含 \(1024^2\) 个长度为 1024 的系统，估算需 80 多块 GPU 承载，因而单设备算法再快也不够。[pdf:E01]（PDF 物理页 1，摘要与引言）

这里的工程瓶颈有两层。第一层是设备内：Thomas 工作量小，却沿每条链串行；PCR/CR 能暴露行级并行，却增加运算和访存。第二层是设备间：把一条链切给多个 MPI process 后，局部消元会留下连接各 partition 的小型 reduced system；它的求解若依赖 AllGather、Gather-Scatter 或频繁全局收敛检查，节点越多越可能由通信而不是算术主导。论文的价值因此不是单纯缩短一次线性代数 kernel，而是给出 exact 与 approximate 两条路径，并显示它们何时从“算得快”转为“通信得慢”。[pdf:E04]（物理页 4，Distributed Memory Algorithms）

**基于证据的合理推断。** 这对 EMT/VSC 研究有条件的重要性：若某个 EMT 子问题确实形成大量彼此独立的标量或小块三对角链，例如规则传输线、方向分裂离散或某类一维支路模型，那么论文的 partition/reduced-system 思想有直接价值；一般 VSC 网络的节点导纳矩阵则是由拓扑决定的稀疏图，并不天然是独立三对角链，因此不能从本文结果直接推出“多卡 EMT 网络求解也会同样缩放”。

## § 2 — 前人工作与不足

Thomas 是三对角矩阵的专用 Gaussian elimination：前扫消去下对角，再回代，约需 \(2N\) 个有依赖的顺序步骤。CR 和 PCR 通过消去间隔不断翻倍的行来换取并行性；CR 运算较少但有 forward/backward 两遍，PCR 的每级行更新互不依赖、更适合 many-core。此前还有把 Thomas 与 PCR 组合的 GPU hybrid 方法。[pdf:E02]（物理页 2，Algorithms 1–2 及相邻正文）László 等人的单节点实现进一步把一个 subsystem 放进一个 32-thread CUDA warp 的 registers；但 subsystem 太大放不下时，优化访存的 Thomas 反而更好，说明算法选择受寄存器容量和内存带宽共同约束。[pdf:E03]（物理页 3，Hybrid Algorithms）

分布式方面，TridiagLU 已能按 MPI decomposition 切分系统并形成 reduced system。它可用 Jacobi 迭代该系统，也可把 reduced system gather 到某个 process 求解后 scatter；前者若要严格检查收敛，需要 global norm，后者天然需要 global collectives。本文认为这两类路径在大规模下都可能因通信扩展不良而失去优势。[pdf:E04]（物理页 4，Distributed Memory Algorithms）

**论文原文明确声称。** 本文相对这些工作补上的不是新的线性方程理论，而是三个系统缺口：

1. 把单节点 hybrid Thomas-PCR 扩到 distributed memory，并比较 GS、AG、PCR、Jacobi 四种 reduced-system 策略；
2. 用改进 forward sweep 把每个 MPI process 的 reduced system 从两行缩成一行；
3. 原生支持 3-D 应用沿不同方向的 contiguous/strided 布局，避免像 TridiagLU 那样必须先把 X/Y 方向数据转置成它能处理的布局。[pdf:E05]（物理页 5，Algorithm 6 与 Tridiagonal Systems in 3-D Applications）

论文引用的相关脉络还包括 ADI、Xcompact3d、GPU batch tridiagonal solver、BabelStream 和 OPS/OpenSBLI；这些引用表明评测目标是高阶结构网格与方向分裂工作流，而不是任意稀疏线性系统。[pdf:E09]（物理页 9，结论及参考文献 1–7）[pdf:E10]（物理页 10，参考文献 8–12）

## § 3 — 重建作者的思考路径

可以从已有事实重建出如下路径，而不预设本文贡献：

1. 一条三对角链上，Thomas 的工作量接近最小，但递推依赖阻止同一条链内部并行；当批量足够大时，可以让不同线程处理不同系统，但当单条链跨设备时仍需解决边界耦合。
2. PCR/CR 用额外工作换并行深度。PCR 每一级把有效耦合距离加倍，适合 SIMD/SIMT；但三对角求解本质上往往受 memory bandwidth 限制，因此多做运算和搬数据未必值得。[pdf:E02]（物理页 2）[pdf:E03]（物理页 3）
3. 把长链按 MPI partition 切开后，最自然的做法是每个 process 先消去内部未知量，只留下边界。这把大问题变为“无通信的局部前扫 + 很小但跨 process 的 reduced system + 无通信的局部回代”。
4. 真正的 scale killer 因而是中间的接口问题：AG/GS 的通信量随 process 数增长；Jacobi 只和邻居交换，但收敛检查会引入 collective；PCR 不需要 collective 且给 exact solution，但每一级要和更远的 process 点对点通信。[pdf:E04]（物理页 4）
5. 既然每个 partition 留两行会放大接口系统，就应问能否用不同的局部消元表达只留一行。Algorithm 6 给出的 forward sweep 正是把 reduced-system 尺寸减半，再让 Jacobi 或 PCR 处理接口。[pdf:E05]（物理页 5）
6. 最后，真实 3-D 应用沿 X/Y/Z 的数据布局不同；若 solver 只接受一种 batch layout，转置成本可能盖过算法收益。因此库必须把 layout 作为算法的一部分，而不是调用前的“数据整理细节”。[pdf:E05]（物理页 5）

## § 4 — 核心 Intuition

先在每个 device/process 内用接近 Thomas 的局部扫掠，把长三对角链压缩成每个 partition 只贡献一行或两行的接口系统；再只为这个小系统选择 exact PCR 或 approximate Jacobi；最后把接口解回代到各 partition。这样将大部分工作变成无通信、带宽友好的局部阶段，并把全局代价集中到一个可显式权衡“精度、通信轮数、通信距离和同步”的 reduced solve。[pdf:E04]（物理页 4）[pdf:E05]（物理页 5）

## § 5 — 具体方法与完整 Pipeline

设一批系统均为 \(A u=d\)，其中 \(A\) 只有下对角 \(a\)、主对角 \(b\) 和上对角 \(c\)。以一条长度为 \(N\) 且横跨多个 MPI process 的链为例，Tridsolver 的 pipeline 是：

1. **组织 batch 与 layout。** 3-D ADI 会沿某一坐标轴反复解许多独立一维系统。column-major 情况下 X 链的同一系统系数连续，Y/Z 链是 strided；row-major 则 Z 连续、X/Y strided。这里的 batch 是“一次共同执行的多条独立三对角链”，strided 表示同一条链相邻行的系数在内存中隔着固定步长。[pdf:E05]（物理页 5，Tridiagonal Systems in 3-D Applications）
2. **设备内局部消元。** 每个 MPI process 持有长度 \(M\) 的 subsystem。原 hybrid forward pass 把内部未知量写成两个端点未知量的函数，因而每个 process 向 reduced system 提交两行；改进的 Algorithm 6 只留一行，减小本地工作和接口系统尺寸。局部 forward/backward 阶段不需要 process 间通信。[pdf:E03]（物理页 3，Figure 1 与 Algorithms 3–4）[pdf:E05]（物理页 5，Algorithm 6）
3. **选择 reduced-system solver。**
   - GS：gather 到一个 process，解完 scatter；精确，但集中通信和集中内存成为瓶颈。
   - AG：allgather 到所有 process，各自求解；省去 scatter，却复制更多数据。
   - PCR：每级与距离逐次加倍的 process 点对点交换，避免 collective，给 exact solution。
   - Jacobi：每次只与相邻 process 交换，通信体积小，给 approximate solution；若每次或每 \(n\) 次检查收敛，需要 global collective。[pdf:E04]（物理页 4）
4. **接口求解后回代。** 每个 process 接收属于自己的接口未知量，用 hybrid backward pass 恢复 subsystem 内的全部 \(u_i\)。[pdf:E03]（物理页 3，Algorithm 4）
5. **映射到 many-core。** CPU 对 Y/Z batches 做 strip 化并加 `omp simd`；GPU 对不合并的访问用 warp 协作读取 \(32\times16\)（single precision）或 \(32\times8\)（double precision）的 YZ block，再用 `__shfl_xor()` 在 lanes 之间完成局部转置。该优化改变线程持有数据的方式，不改变数学系统。[pdf:E05]（物理页 5）
6. **执行与通信。** GPU 版本既可经 host copy 再做 CPU 间 MPI，也可用 GPU-direct MPI 直接在 GPUs 间传输；论文实测后者更好。[pdf:E07]（物理页 7，Figure 2 后相邻正文）

**可迁移到多卡 EMT/VSC 的机制。** 可以迁移的是“局部消元形成接口 Schur complement（消去内部变量后只保留跨分区边界耦合）→ 通信拓扑感知地解接口 → 本地回代”的三级结构；还可迁移 layout-aware batching、GPU-direct、把 global collective 换成小消息点对点、以及同时报告计算与通信占比的评测方式。

**不能直接迁移的机制。** 一般 EMT/VSC 节点方程不是独立标量三对角链，而是拓扑稀疏矩阵、block system 或含代数约束的系统；开关事件还会改变 sparsity/factorization。此时 Thomas 的相邻递推、PCR 的距离翻倍消元以及一行/两行 reduced system 都不再原样成立。论文也没有处理开关事件、时间推进、多速率、电力电子器件模型、定点数/FPGA 映射或实时步长；这些均是“未报告”，不能由 CPU/GPU batch solver 结果补推出来。

## § 6 — 核心数学推导

三对角系统的第 \(i\) 行为

\[
a_i u_{i-1}+b_i u_i+c_i u_{i+1}=d_i,\qquad i=0,\ldots,N-1,
\]

且 \(a_0=c_{N-1}=0\)。这等价于只有三条非零对角线的 \(A u=d\)。[pdf:E02]（物理页 2，Eqs. 1–2）

**Thomas。** 前扫令

\[
r_i=\frac{1}{b_i-a_i c^*_{i-1}},\qquad
d_i^*=r_i(d_i-a_i d^*_{i-1}),\qquad
c_i^*=r_i c_i,
\]

随后从 \(i=N-2\) 到 0 回代 \(d_i=d_i^*-c_i^*d_{i+1}\)。直觉是每一步用上一行消掉当前行的 \(a_i\)，所以工作量是 \(O(N)\)，但依赖深度也是 \(O(N)\)；论文将两遍合计描述为约 \(2N\) 个依赖步骤。[pdf:E02]（物理页 2，Algorithm 1）

**PCR。** 先把主对角归一化为 1。第 \(p\) 级取 \(s=2^{p-1}\)，用第 \(i-s\) 与 \(i+s\) 行消去当前行两侧间隔为 \(s\) 的耦合；最小 \(P\) 满足 \(2^P\ge N\)。经过 \(P\) 级后，更新后的 \(a^{(P)}\) 与 \(c^{(P)}\) 为零，\(d^{(P)}\) 就是解。[pdf:E02]（物理页 2，Algorithm 2）因此，**基于算法结构的复杂度推断**是：PCR 约有 \(O(\log N)\) 个同步级、每级 \(O(N)\) 行更新，总工作 \(O(N\log N)\)；它用更多算术和访存换取比 Thomas 更短的并行 critical path。论文明确给出级数和行独立性，但未把这组三个大 O 记号写成定理。

CR 的 forward 部分与 PCR 类似，另有 reverse pass；作者只做定性比较：CR 总操作更少，但并行性较低且需要两倍 passes。[pdf:E02]（物理页 2 到物理页 3 页首）

**Hybrid 与 reduced system。** 原 hybrid 方法在一个长度 \(M\) 的 partition 内把内部点表示成

\[
a_i^*u_0+u_i+c_i^*u_{M-1}=d_i^*,\qquad i=1,\ldots,M-2,
\]

所以只要先求出两端点就能本地回代。[pdf:E03]（物理页 3，Figure 1 前后）改进 forward sweep 改写为

\[
a_i^*u_0+u_i+c_i^*u_{i+1}=d_i^*,\qquad i=1,\ldots,M-1,
\]

最终每个 partition 只给 reduced system 一行。它在 partition 内引入依赖，却把接口维数从每 process 两行降为一行，且回代仍是一次 sweep、无额外内存移动。[pdf:E05]（物理页 5，Algorithm 6 前正文）

**通信与同步复杂度。** 论文明确说明分布式 PCR 的通信对象随级数逐次变远，通信 volume 随 solve direction 上 process 数量呈 logarithmic 增长；据此可写成每个 process 约 \(O(\log P_{\text{mpi}})\) 个点对点通信级，但消息距离增加。Jacobi 若做 \(K\) 次迭代，则有 \(K\) 轮邻居交换；收敛检查会再引入 global collective。AG/GS 不靠多级邻居传播，但单次 collective 的参与范围和数据复制随 process 数增长，实测最早失去扩展性。[pdf:E04]（物理页 4）[pdf:E06]（物理页 6，ARCHER2 weak-scaling 讨论）

## § 7 — 实验设计与结论

**平台与比较对象。** CPU 平台 ARCHER2 每节点有 \(2\times64\) AMD Rome cores 和 256 GB RAM；GPU 平台 Cirrus 有 36 个节点，每节点 \(4\times\) NVIDIA V100 16 GB，节点内 NVLink、节点间 FDR InfiniBand。CPU baseline 是 TridiagLU；Tridsolver 比较 AG、GS、PCR 和 Jacobi，Jacobi 为避免规模变化带来的迭代数差异固定为 10 次。[pdf:E06]（物理页 6，Evaluation and Performance）

**问题 1：内存布局是否决定设备内性能？ → 实验：** 比较 X/Y/Z solve 的带宽，并和 cuSPARSE 两种 batch layout 比较。**答案：** 单 V100 上 Tridsolver 的 X/Y/Z 分别为 458/731/739 GB/s；BabelStream Triad 为 821 GB/s。cuSPARSE 的 `gtsv2StridedBatch`（类似 X layout）为 525.5 GB/s，`gtsvInterleacedBatch`（类似 Z layout）为 725.6 GB/s。结论不是某一算法普遍更快，而是 contiguous/interleaved 的 coalescing 能造成接近 1.6 倍的方向差异。[pdf:E07]（物理页 7，Figure 2 后正文）

**问题 2：CPU weak scaling 能否保持每节点工作量不变时的 runtime？ → 实验：** 每个 ARCHER2 node 固定 \(512^3\) grid points，按 solve direction 扩展到 128 nodes。weak scaling 指每增加资源就同比增加总问题，理想结果是 runtime 近似不变。**答案：** Jacobi 整体 scaling efficiency 为 90%–98%；PCR reduced solve 为 70%–74%，但整体表现接近 Jacobi，仅在较大 node count 落后；AG/GS 受 global communication 限制。[pdf:E06]（物理页 6，Weak Scaling—ARCHER2）Figure 2(a)(b) 给出 runtime 对节点数的完整曲线。[pdf:E07]（物理页 7，Figure 2）

**问题 3：固定大问题能否 strong scale？ → 实验：** ARCHER2 固定 solve direction 为 8192 点、另两维各 512，从 1 增至 128 nodes。strong scaling 指全局问题固定，理想 runtime 随资源数反比下降。**答案：** 1–8 nodes 出现 102%–108% superlinear scaling，作者归因于 TLB/LLC misses 减少；32 nodes 后通信占优。128 nodes 的 Z solve 中，reduced solve 占总时间 60%（Jacobi）和 85%（PCR），AG/GS 还会因 reduced-system 过大而耗尽内存。[pdf:E06]（物理页 6，Strong Scaling—ARCHER2）[pdf:E07]（物理页 7，Figure 2 及其下方正文）

**问题 4：GPU 集群跨越节点边界后会怎样？ → 实验：** weak scaling 每 GPU 固定 \(512^3\) 点；strong scaling 固定 solve direction 2048 点、另两维各 512，从 1 到 32 GPUs，并比较 host copy 与 GPU direct。**答案：** 4 GPUs 以内在同一 NVLink node，效率超过 93%；跨节点后降为 Jacobi 55%–66%、PCR 39%–57%。32 GPUs 时通信占总时间 72%（Jacobi）与 86%（PCR）；GPU direct 在 strong scaling 中最高快 3.25 倍。[pdf:E08]（物理页 8，Figure 3 与相邻正文）Figure 3 的四个 panel 同时显示 weak/strong scaling 和 HC/GD 差异。[pdf:E08]

**问题 5：改进 forward pass 是否只是在通信之外做微调？ → 实验与答案：** 单 GPU 上 PCR/Jacobi variants 比 AG 快 1.8 倍；此时没有 reduced-system 跨节点求解，因此作者把增益归因于新的 Thomas forward/backward pass，而不是通信。结论总结同样报告该优化带来 1.8 倍 speedup。[pdf:E08]（物理页 8，Figure 3(b) 下正文）[pdf:E09]（物理页 9，Conclusion）

**不得外推的范围。** 这些实验使用规则 3-D batch、固定硬件互连和最多 128 CPU nodes/32 GPUs；Jacobi 规模实验固定 10 次迭代，论文没有同时报告每类矩阵的 residual/error。因此 90%–98% scaling 证明的是固定工作量的并行效率，不证明任意条件数下 10 次 Jacobi 都达到相同精度，也不证明 irregular EMT sparse network 的性能。

## § 8 — Take-aways

**5 句话。**

1. 分布式三对角求解的主矛盾会从本地消元转移到 partition 边界形成的 reduced system。
2. Thomas 工作少但串行，PCR 工作多却能以 logarithmic stages 暴露 many-core 并行，CR 位于两者之间。
3. hybrid 方法把局部链压缩后再求接口，而 Algorithm 6 把接口从每 process 两行减为一行。
4. Jacobi 的邻居通信 weak-scale 较好但只给 approximate solution，PCR 给 exact solution且无 collective，却因远距离多级通信在大规模更早受限。
5. batch 的 contiguous/strided layout、warp local transpose 和 GPU-direct 不是外围实现细节，而是决定带宽与跨节点效率的核心机制。[pdf:E04]（物理页 4）[pdf:E05]（物理页 5）[pdf:E08]（物理页 8）

**3 句话。** 最有效的结构是局部无通信消元、最小接口系统、局部回代。接口求解器必须按准确度要求和互连层级选择，而不是固定选“理论上并行”的算法。对 EMT/VSC 可迁移的是这种分层分区思想，不是三对角递推本身。

**1 句话。** 论文说明，在 many-core 上，求解器的可扩展性最终由“接口有多小、数据是否连续、通信要走多远”共同决定。

## § 9 — 最脆弱的假设

最脆弱的假设是：**真实工作负载能够表示为数量足够多、彼此独立、布局规则的标量三对角链，并且每条链的 partition 接口始终只有常数个未知量。** 这个假设一旦失效，本文的核心结构会同时失去三个优势：Thomas/PCR 的固定相邻耦合不再适用，每 process 一行的 reduced system 不再成立，规则 batch 也无法保证 coalesced/vectorized 访问。论文在算法定义中明确聚焦 scalar tridiagonal systems，在 3-D 应用中也依赖沿坐标轴形成独立一维 systems。[pdf:E02]（物理页 2，算法范围）[pdf:E05]（物理页 5，3-D Applications）

论文为该假设在结构网格 ADI/Xcompact3d 类型 workload 上提供了 CPU/GPU scaling 证据，但没有给出非规则稀疏图、动态拓扑或强 block coupling 的实验。对一般多卡 EMT/VSC 网络，这个缺口是决定性的：网络分区可能产生很多 separator variables，开关事件会改变接口结构，VSC 控制与电磁状态还可能形成 block Jacobian。把这些系统强行排成三对角通常会产生 fill-in，足以抵消本文的一行接口和规则访存优势。后半段是**基于证据的合理推断**，不是论文原文结论。

## § 10 — 最小复现实验

一周内可复现最关键的 claim：“reduced-system 策略与 layout，而非本地浮点运算，决定跨设备 scaling 转折点。”

1. **数据：** 生成 \(a_i=c_i=-1,\ b_i=2+\epsilon\) 的 Poisson-like tridiagonal batches；设置 X-like strided 与 Z-like interleaved 两种 layout。再加一组 \(b_i\) 接近 \(|a_i|+|c_i|\) 边界的难收敛样本，用于检验 Jacobi 准确度。
2. **实现：** 使用公开 Tridsolver，运行改进 forward/backward；reduced system 分别用 PCR 与固定 10 次 Jacobi。若只有 1 个多 GPU node，至少测试 1/2/4 GPUs；能访问两节点时加入 8 GPUs，正好跨越 NVLink 到 InfiniBand 的层级。
3. **测量：** 总 runtime、本地 kernel GB/s、MPI time fraction、每轮消息数/bytes、\(\|Au-d\|_2/\|d\|_2\)，以及 strong/weak scaling efficiency。每种配置同时记录 HC 与 GPU-direct。
4. **支持条件：** interleaved layout 显著高于 strided；4 GPUs 内效率接近恒定，跨节点后通信占比突升；PCR residual 接近 direct baseline，而 Jacobi 的 residual 随 conditioning 明显恶化；GPU-direct 降低通信时间。
5. **反驳条件：** 控制同等数据量后 layout 差异消失，或跨节点效率下降完全由本地 kernel 而非 MPI time 解释；又或者固定 10 次 Jacobi 在困难样本上仍与 PCR 同精度，都会削弱论文给出的机制解释。

论文公开的评测规模、Figure 3 的互连转折和固定 10 次 Jacobi 设置可作为复现实验的具体锚点。[pdf:E06]（物理页 6）[pdf:E08]（物理页 8）

## § 11 — 最强反例设计

最强攻击应保持“标量三对角 batch”不变，避免用超出论文范围的任意稀疏矩阵偷换问题。构造一族仍为三对角、但接近非对角占优且条件数跨多个数量级的系统；同时逐渐缩短每条链、减少 batch 数量，并让同一全局问题切到越来越多 MPI processes。这样会同时压低每设备可用并行工作，使接口系统相对本地系统变大，并让 Jacobi 需要远多于 10 次迭代。

攻击的判据是 accuracy-normalized time-to-solution：所有算法必须达到同一 residual，而不是固定工作量后只比 runtime。如果 Jacobi 为达到目标残差必须增加迭代和 global convergence checks，PCR 又因 \(O(\log P_{\text{mpi}})\) 级远距离通信而在高 process count 被通信吞没，那么论文展示的“Jacobi 高效率/PCR 竞争性 exact alternative”会同时失去实际优势。Figure 2/3 已显示这种趋势的前半段：128-node Z solve 的 reduced phase 占 60%/85%，32-GPU 时通信占 72%/86%。[pdf:E07]（物理页 7）[pdf:E08]（物理页 8）

这个反例不会否定局部消元的正确性，也不会否定 PCR 的 exactness；它真正挑战的是论文性能结论对 batch width、conditioning 和 partition granularity 的稳健性。论文没有报告 accuracy-matched 的 conditioning sweep，因此这个替代解释仍未被排除。

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty：面向事件驱动多卡 EMT 的“可验证接口求解器”。**

高影响的 HPC/电力电子交叉工作通常需要同时证明数值正确性、跨设备扩展性、工程可实现性和真实系统价值；只把 Thomas 换成另一种 GPU kernel 不足以形成强贡献。

**(a) 未满足需求。** 多卡 EMT/VSC 既需要微秒级或更小的稳定时间步，又面对一般稀疏/分块网络、开关事件和精度约束。本文的 regular tridiagonal batch 假设不成立，但其“局部消元—接口求解—局部回代”结构仍有价值。

**(b) 可能的研究价值。** 改变问题定义：不再问“怎样把 PCR 用到 EMT”，而问“怎样让每个网络 partition 在拓扑不变期间复用局部 factorization，只把小型 separator/port interface 暴露给多卡通信；拓扑事件发生时，又怎样以 residual certificate 决定局部更新、接口重构或全局回退”。这里的 certificate 是可核验的残差/守恒误差门槛，用来防止 approximate interface solve 静默污染 EMT 波形。

**(c) 相邻领域工具。** 借鉴 sparse multifrontal/domain decomposition 的 Schur complement、graph separator、communication-avoiding Krylov/preconditioner，以及本文的 layout-aware batching、GPU-direct 和 exact/approximate 双路径。对重复的 VSC/线路子结构，可以把小块接口按 block batch 组织；对不规则主网络则保留图结构，绝不伪装成三对角链。

**(d) 第一个可证伪实验。** 选择一个含多 VSC、传输线和频繁开关事件的 EMT benchmark，与单卡 sparse direct baseline 对齐每个时间步的节点电压/支路电流误差和 KCL residual。比较 1/2/4/8 GPUs 的固定拓扑时段与事件时段；若接口方法在达到相同误差门槛后不能降低跨卡 bytes/syncs，或事件重构使 deadline miss rate 高于 baseline，就否定该方向的核心机制。

**(e) 与本文的实质区别。** 本文的接口维数由三对角链保证为每 partition 一行或两行，PCR/Jacobi 作用于规则 reduced tridiagonal system；候选方法的接口由网络 separator 决定，可能是动态 block sparse system，并把误差证书和事件触发重构纳入算法目标。它迁移的是体系结构思想，不是假设 EMT 矩阵拥有本文的三对角结构。相关工作尚未在本任务中充分检索，因此这里只能作为候选研究方向，不能声称 novelty。
