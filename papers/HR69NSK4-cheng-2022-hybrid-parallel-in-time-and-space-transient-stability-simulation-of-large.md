# Hybrid Parallel-in-Time-and-Space Transient Stability Simulation of Large-Scale AC/DC Grids

作者：Tianshi Cheng；Ning Lin；Venkata Dinavahi  
出处：IEEE Transactions on Power Systems, Vol. 37, No. 6, pp. 4709–4719  
年份：2022  
DOI：10.1109/TPWRS.2022.3153450  
Zotero key：HR69NSK4  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是大型 AC/DC 电网暂态仿真同时面临的两个尺度矛盾：transient stability（TS）用毫秒级步长观察电网级机电动态，却无法给出电力电子器件的微秒级 electromagnetic transient（EMT）细节；把两者联合起来又会显著增加计算量。作者因此追问：能否不仅在空间上并行求解设备和子网，还沿时间轴并行推进多个时间子区间，并让 CPU 与 GPU 各自承担更适合的任务，从而在保留 TS–EMT 联合分析能力的同时缩短大规模仿真的墙钟时间？论文首页的摘要与 Introduction 明确给出了这一工程瓶颈以及 CPU–GPU PiT+PiS 的回答。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

其价值不只是“把代码跑快”。AC/DC 混联系统既有同步机、电网频率和转角等系统级动态，也有 MMC 开关与电容能量等设备级动态；若只能选择 TS 或 EMT 其中之一，分析者就必须牺牲系统规模或局部细节。论文的目标是在同一次联合仿真中保留这两种观察尺度，并把新增的时间并行性叠加到已有空间并行性上。

## § 2 — 前人工作与不足

论文将前人路线分成三类。第一类是面向多核 CPU 或 GPU 的 TS 空间并行，包括 Gauss–Jacobi–Block–Newton、SIMD GPU 和多 GPU TS；第二类是异构 CPU–GPU 的 AC/DC TS–EMT 联合仿真；第三类是 Jacobi decomposition 或 Parareal 形式的时间并行。作者指出，前两类的线程并发主要来自 parallel-in-space（PiS），而既有 Parareal TS 工作主要研究 parallel-in-time（PiT）本身，尚未系统叠加 PiS。[pdf:E02]（PDF 物理页 2，Section I）

论文给出的直接对比是：已有 Parareal TS 工作在 IEEE 39-bus 系统上使用 470 个核仅取得约 4 倍加速；另一项大系统实验即使用了大量核，并行效率仍低于 20%。作者据此判断，单独增加时间区间并不能消除串行 coarse-grid 预测、迭代收敛与同步开销，纯 PiT 的效率仍不如成熟 PiS。[pdf:E02]（PDF 物理页 2，Section I）

## § 3 — 重建作者的思考路径

下面是基于论文背景与机制的重建，不是作者逐字陈述。第一步，研究者会从已有模型中看到丰富但有上限的空间独立性：同步机由分区迭代从主网络中拆出，MMC 子模块也能独立求解。[pdf:E03]（PDF 物理页 3，Figs. 3–4）[pdf:E04]（PDF 物理页 4，Section II-B）第二步，PiS 的并发度仍受可独立设备或子网数量限制：空间分区饱和后，再增加 GPU 线程收益很小。第三步，Parareal 能把一个时间窗切成多个子区间，但每轮仍要做串行 coarse-grid 传播，且迭代次数随分区和扰动难度增长，因此纯 PiT 的效率上限偏低；论文的理论式还给出当迭代数 \(I\ge 2\) 时其最大并行效率低于 50%。[pdf:E05]（PDF 物理页 5，Fig. 5 与 Eqs. (18)–(22)）

第四步，如果每个 fine-grid 时间子区间内部仍用 GPU 做 PiS，就可以在“时间区间数 × 空间线程数”两个维度同时扩展并发度。第五步，Parareal 调度、分支判断和流同步不适合放在纯 GPU dynamic parallelism 中，而 CPU 恰好可在 GPU 求 TS 时异步执行 EMT；于是形成“CPU 调度与 EMT、GPU 执行 TS、unified memory 交换波形、multi-stream 叠加 coarse/fine kernel”的异构结构。[pdf:E06]（PDF 物理页 6，Figs. 7–8 与 Section III-A）这一思路的关键不是把所有工作迁到 GPU，而是把不同依赖结构映射到不同处理器。

## § 4 — 核心 Intuition

Parareal 把一个时间窗拆成串行但便宜的 coarse 预测和可并行但昂贵的 fine 校正，而 PiS 又能让每个时间步内部的设备计算并行。作者把两种并行相乘，并让 CPU 在 GPU 执行 TS 的同时计算 EMT，从而尝试把原本暴露在关键路径上的空间饱和、调度和通信时间隐藏起来。能否奏效最终取决于 coarse 预测能否让 Parareal 少迭代，以及 CPU EMT 是否真的能被 GPU TS 的执行时间覆盖。

## § 5 — 具体方法与完整 Pipeline

以论文的合成 AC/DC 系统为例，输入包括若干 IEEE 118-bus AC 网、同步机动态模型、CIGRÉ DCS2 型 MTDC 网络、详细 MMC 等值模型、初值与故障或功率阶跃事件；输出是同步机转角、频率和端电压，以及 MMC 功率、DC 电压等时域波形。

1. **建立 AC 侧 TS DAE。** 每台发电机由同步机、电气控制与四质量块机械轴系组成 17 阶模型；网络代数方程与机组微分方程构成 DAE。作者以隐式 Trapezoidal rule 离散，并用主电路电压迭代与机组 Newton–Raphson 迭代解耦求解。[pdf:E02]（PDF 物理页 2，Section II-A 与 Eqs. (1)–(2)）[pdf:E03]（PDF 物理页 3，Fig. 3 与 Eqs. (3)–(8)）
2. **建立 DC 侧 MMC EMT 模型。** 每个 HBSM 用开关导纳和电容 companion model 表示，子模块独立求解 \(2\times2\) 方程；已知开关状态的逆导纳矩阵被缓存。所有子模块随后合并成臂电压源和 Norton 等值，主回路用 KLU 求解；NLM 与排序策略生成插入子模块和门极信号。这里用子模块—主电路间的一个 artificial delay 换取解耦与节点数缩减。[pdf:E03]（PDF 物理页 3，Fig. 4 与 Section II-B）[pdf:E04]（PDF 物理页 4，Eqs. (9)–(11)）
3. **沿时间轴做 Parareal。** 一个时间窗被切成 \(N\) 个子区间。串行 coarse operator \(G\) 先传播初值；各 fine operator \(F\) 从这些初值并行积分；随后用“新 coarse + fine − 旧 coarse”校正区间端点，直到误差低于 tolerance。本文的 \(F\) 与 \(G\) 都使用 Trapezoidal rule，区别是 \(h_F<h_G\)。[pdf:E04]（PDF 物理页 4，Section II-C 与 Eqs. (12)–(17)）[pdf:E05]（PDF 物理页 5，Fig. 5 与 Eq. (18)）
4. **在 GPU 内叠加 PiS，并由 CPU 发射 multi-stream。** CPU 预建一个 coarse-grid stream 和多个 fine-grid streams；第 \(x\) 个 coarse kernel 与可用的 fine kernels 重叠执行，端点校正也嵌入循环。coarse 依赖只在必要位置同步，而 fine streams 彼此并发；同一流结构还可映射到多个 GPU。[pdf:E06]（PDF 物理页 6，Section III-A）[pdf:E07]（PDF 物理页 7，Fig. 9(a)–(b)）
5. **CPU 异步执行 EMT PiS。** EMT 并行粒度是 HVDC 系统级，一个 CPU 线程负责一个或多个 HVDC 子系统；不同 EMT 子系统通过带传播时延的 Bergeron TLM 解耦，并以 ZeroMQ req/rep 消息总线交换端口量。[pdf:E07]（PDF 物理页 7，Section III-B）
6. **按时间窗交换 AC/DC 接口波形。** EMT 在 TS 侧等值为功率源；TS 的 RMS 母线电压被变换成 EMT 侧瞬时三相电压源。接口交换 \(P,Q\) 与 \(V\angle\theta\) 的采样波形，而非每个 EMT 步都同步；数据驻留在 CUDA unified memory，使 CPU 和 GPU 可共享并预取。[pdf:E07]（PDF 物理页 7，Fig. 9(c) 与 Section III-C）[pdf:E08]（PDF 物理页 8，Section III-C）

论文对多速率给了两层描述：方法部分称 EMT 步长约 \(50\,\mu s\)，TS 步长约 \(100\,\mu s\)–\(10\,ms\)；具体 case 的 TS fine/coarse 步长分别为 \(100\,\mu s\) 与 \(10\,ms\)，EMT 步长为 \(10\,\mu s\)。[pdf:E07]（PDF 物理页 7，Section III-C）[pdf:E08]（PDF 物理页 8，Section IV）开关状态由二值门极信号改变高低导纳，但论文未报告通用的零交叉检测、事件定位或可变步长机制。数值精度类型、GPU kernel 的具体线性代数布局、源码与可复现实验脚本均未报告。本文也未做 FPGA 映射；实际平台是 CUDA GPU 加多核 CPU，不能把其并行结构直接当作 FPGA 实现结论。

## § 6 — 核心数学推导（无形式化数学则跳过）

先看单步 TS 求解。连续 DAE 写成

\[
\dot{x}=f(x,u),\qquad g(x,u)=0,
\]

其中 \(x\) 是同步机、轴系和控制器状态，\(u\) 是由网络代数方程确定的电流、电压等接口量。隐式梯形离散为

\[
x_{n+1}=x_n+\frac{h}{2}\left[f(x_{n+1},u_{n+1})+f(x_n,u_n)\right].
\]

若 \(f(x,u)=Ax+Bu\)，则待解方程可整理为

\[
\left(E-\frac{h}{2}A\right)x_{n+1}
-\left(E+\frac{h}{2}A\right)x_n
+\frac{h}{2}Bu_{n+1}=0.
\]

工程直觉是：梯形法把新旧时刻的动态平均起来以获得稳定的隐式步进，但每一步要解耦合 DAE；若 \(A\) 随状态变化，还要做 Newton–Raphson。[pdf:E03]（PDF 物理页 3，Eqs. (5)–(8)）

Parareal 把昂贵的细步长算子 \(F\) 与便宜的粗步长算子 \(G\) 组合。本文二者采用相同梯形积分、仅步长不同：

\[
\begin{aligned}
F^k &= x_n^k+\frac{h_F}{2}\left[f(x_{n+1}^k,u_{n+1}^k)+f(x_n^k,u_n^k)\right],\\
G^k &= x_n^k+\frac{h_G}{2}\left[f(x_{n+1}^k,u_{n+1}^k)+f(x_n^k,u_n^k)\right],\qquad h_F<h_G .
\end{aligned}
\]

区间端点的核心校正式是

\[
U_j^{(k)}
=F(T_j,T_{j-1},U_{j-1}^{(k-1)})
+G(T_j,T_{j-1},U_{j-1}^{(k)})
-G(T_j,T_{j-1},U_{j-1}^{(k-1)}).
\]

第一项给出上一轮的高精度 fine 结果，后两项用本轮与上一轮 coarse 传播的差补偿它；作者把这一过程联系到 Quasi-Newton 近似。[pdf:E04]（PDF 物理页 4，Eqs. (12)–(17)）[pdf:E05]（PDF 物理页 5，Eq. (18) 与 Fig. 5）

对 \(n=mp\) 个 fine steps、单步代价 \(w\)、PiT 处理器数 \(p\) 和迭代数 \(I\)，论文给出的理想化加速比为

\[
S_{\mathrm{pit}}(p)
=\frac{n w}{(I+1)p w+I m w}
=\frac{1}{(I+1)/m+I/p}.
\]

相应效率满足 \(E_{\mathrm{pit}}(p)<1/I\)；论文取 \(I\ge2\)，所以纯 Parareal 最大效率低于 50%。叠加空间并行后，

\[
S_{\mathrm{pit+pis}}(p_1,p_2)
=S_{\mathrm{pis}}(p_1)S_{\mathrm{pit}}(p_2).
\]

这说明“两个维度的加速相乘”只在其代价模型成立时成立：同步、通信、负载不均衡和随分区增长的迭代次数都会破坏这个理想关系。论文随后用一个 8 空间分区、\(m=100\)、\(p=10\) 的假设例子画理论曲线，因此 Fig. 6 不是实测硬件定律。[pdf:E05]（PDF 物理页 5，Eqs. (19)–(22)）[pdf:E06]（PDF 物理页 6，Fig. 6 与 Eq. (23)）

## § 7 — 实验设计与结论

- **问题：PiT 的数值结果能否接近商业 TS 工具？→ 实验：** Scale x1 由 4 个 IEEE 118-bus 网与修改后的 CIGRÉ DCS2 MTDC 系统组成，共 472 个 TS 节点、216 台发电机和 4 个 201-level 三相 EMT MMC；在 Bus 23 施加持续 \(200\,ms\)、故障电阻 \(1\,\Omega\) 的短路，以 Generator 10 为转角参考，并与 DSATools TSAT 比较。**→ 答案：** 作者正文报告相对误差小于 1%，Fig. 11 局部放大图标注误差小于 0.1%；故障清除后约 2 秒的暂态在 10–12 秒回归稳定。[pdf:E08]（PDF 物理页 8，Fig. 10、Fig. 11 与 Section IV-A）这一结果只验证了该合成系统与单一短路工况，不能外推为所有强非线性事件都快速收敛。
- **问题：TS–EMT 联合接口能否表现跨网功率支援？→ 实验：** Case 2 在 Net-1 的 Bus 118 于 \(4\,s\) 增加 \(600\,MW\) 负荷；\(10\,s\) 时 Cm-E1 从 HVDC 母线抽取 \(600\,MW\)，Cm-B2 为维持 DC 电压提供 \(648\,MW\) 并从 Net-2 取能；\(10.5\,s\) 再向 Net-2 Bus 118 注入 \(620\,MW\)。**→ 答案：** Fig. 12 中 Net-1 的频率与电压在 MMC 支援后恢复，Net-2 先因供能下降、再因本地注入恢复，DC 端电压亦保持受控。[pdf:E09]（PDF 物理页 9，Fig. 12 与 Case 2 正文）这验证的是预设控制序列的动态一致性，不等于证明控制策略最优或在换流器闭锁等工况下仍稳定。
- **问题：PiT+PiS 是否比单 GPU PiS 更快？→ 实验：** 在 1–12 倍扩展系统上比较 CPU 串行、单 NVIDIA Tesla V100 的 GPU PiS 与 CPU–GPU PiT+PiS。**→ 答案：** 12x 时 PiS 为 98.7x，PiT+PiS 为 165.6x，后者相对前者为 1.67x；论文称执行时间与系统规模近似线性增长。[pdf:E09]（PDF 物理页 9，Fig. 13）[pdf:E10]（PDF 物理页 10，Section IV-B）附录给出的 CPU 环境为两颗 16-core Intel Xeon Silver 4216，系统为 CentOS 7.7、CUDA 11.0、GCC/G++ 9.3、OpenMP 4.5。[pdf:E10]（PDF 物理页 10，Appendix A）
- **问题：两张 V100 能否继续线性扩展？→ 实验：** 把 coarse-grid 放在 GPU-1、fine-grid 放在 GPU-2，比较单/双 GPU。**→ 答案：** 2x 系统的双 GPU 并行效率接近 100%，但系统继续增大时加速退化到约 1.0x；作者将原因归于大 kernel 使 fine-grid 负载集中在 GPU-2、coarse-grid GPU-1 空闲，形成负载不均衡。[pdf:E09]（PDF 物理页 9，Fig. 14）[pdf:E10]（PDF 物理页 10，Section IV-B）

论文未报告多次重复运行、误差条、能耗、显存峰值、CPU EMT 占用比例、每窗 Parareal 迭代数分布，也未给出与其他现代异构 TS–EMT 实现的端到端对比；因此不能把 165.6x 外推到不同硬件、模型刚性、事件密度或网络通信条件。

## § 8 — Take-aways

**5 句话：**

1. 论文把时间并行 Parareal 与空间并行 PiS 组合，使每个时间子区间内部仍能利用 GPU 的大量 CUDA cores。
2. CPU 负责 Parareal 调度与 EMT，GPU 负责 TS，multi-stream 和 unified memory 用来重叠 coarse/fine kernel、数据迁移与异构计算。[pdf:E07]（PDF 物理页 7，Fig. 9）
3. AC 侧使用同步机 DAE 与梯形积分，DC 侧保留 201-level MMC 子模块等值，因此实验同时观察系统级与设备级动态。
4. 合成 12x 系统上，作者报告 PiT+PiS 为 165.6x、PiS 为 98.7x，但该收益是特定 V100 与负载结构下的结果。[pdf:E10]（PDF 物理页 10，Section IV-B）
5. 双 GPU 在更大规模下几乎不再加速，揭示静态 coarse/fine 设备分工会把负载不均衡变成新的关键路径。

**3 句话：**

1. 这项工作的真正贡献是把时间依赖、空间独立性和 CPU/GPU 异构性放进同一个 TS–EMT 调度结构。
2. 数值正确性由 Parareal 最终可回退到串行传播保障，但性能取决于少迭代和成功重叠，而不是由算法形式自动保证。
3. 单 GPU 的 12x 结果令人鼓舞，双 GPU 的退化则说明可扩展性仍未解决。

**1 句话：**

作者证明了 PiT+PiS 在一个大型合成 AC/DC 基准上可以显著快于 PiS-only，但尚未证明这种优势对密集事件、负载不均衡和更多 GPU 稳健成立。

## § 9 — 最脆弱的假设

失败代价最大的假设是：每个时间窗的 coarse 解足够接近 fine 解，使 Parareal 在很少迭代内收敛，同时 CPU 上的 EMT 计算与重算成本能被 GPU TS 隐藏。若这个假设不成立，算法虽然可通过增加迭代并最终退回串行传播来保持精度，但时间并行收益会消失，甚至因 EMT 重启、同步和波形交换而慢于 PiS-only。

论文自己给出了这一风险的机制证据：小到 \(1\,ms\) 或 \(10\,ms\) 的时间窗可不经 AC/DC 接口迭代交换数据，较大时间窗却需要在每轮 PiT 迭代重启 EMT；作者还承认短路等突变会在若干时间窗降低性能，只是“最终回退串行”可保证精度。[pdf:E07]（PDF 物理页 7，Section III-C）[pdf:E08]（PDF 物理页 8，Section III-C）现有证据只有一个短路和一个分阶段功率阶跃，没有报告故障恰跨窗、换流器闭锁、控制饱和、连续开关事件或每窗迭代数。因此，论文证明了所选工况下的可行性，却没有充分证明这个关键假设在最需要 EMT 细节的强不连续场景中仍成立。双 GPU 的静态任务分配退化又表明，即使收敛不恶化，“EMT 被免费隐藏”和“增加 GPU 即扩展”也会受到真实关键路径限制。[pdf:E10]（PDF 物理页 10，Section IV-B）

## § 10 — 最小复现实验

一周内最值得验证的不是复现 12x 峰值，而是检验“在同一误差约束下，PiT+PiS 是否稳定快于 PiS-only”。前提是已有可运行的 TS DAE 与 EMT 求解器；论文未提供源码可用性说明，若从零实现完整 201-level MMC，单周目标不现实。

- **数据与模型：** 使用标准 IEEE 118-bus TS 数据，连接一个按论文等值方法实现的两端 MMC–HVDC 子系统；保留同步机 DAE、\(h_F=100\,\mu s\)、\(h_G=10\,ms\)、EMT \(10\,\mu s\)。选一个 \(200\,ms\)、\(1\,\Omega\) 的三相短路，并让故障开始或清除时刻分别对齐与错开 Parareal 窗边界。[pdf:E08]（PDF 物理页 8，Section IV-A）
- **实现：** 在同一台 CPU–GPU 机器上运行三条路径：串行 fine-step 作为数值参考、GPU PiS-only、CPU–GPU PiT+PiS。固定模型、编译选项和输出采样；只改变时间窗边界与并行调度。
- **测量：** 对转角、频率、AC 电压、DC 电压和 MMC 功率测最大相对/绝对误差；记录每窗迭代数、EMT 重启次数、CPU/GPU 活跃时间、同步等待与墙钟时间。每个工况预热后重复至少 5 次，报告中位数和离散范围。
- **支持或反驳：** 若 PiT+PiS 在全部窗对齐条件下均保持相对误差不超过作者正文使用的 1% 口径，并且墙钟时间稳定低于 PiS-only，便支持其核心机制；若错窗故障使迭代或 EMT 重启激增，导致 PiT+PiS 不再更快，或为保速度而误差超过 1%，则反驳“优势对强事件稳健”的外推。

## § 11 — 最强反例设计

最强反例是一个“跨窗密集不连续事件”实验：在相邻 Parareal 时间窗边界附近依次安排三相故障投入、故障清除、MMC blocking/deblocking 与功率控制饱和，使 AC 与 DC 两侧的状态在一个 coarse step 内都发生陡变；同时让不同 AC 子网的机组数和 MMC 开关负载高度不均衡。对每个事件时刻做亚步扫描，比较串行 fine、PiS-only 与 PiT+PiS 的误差、每窗迭代、EMT 重启、CPU/GPU idle 和总时间。

这个反例直接攻击两层机制：coarse operator 无法预测细步长不连续会破坏时间并行收敛；静态把 coarse 与 fine kernel 分到不同 GPU 会放大负载不均衡。论文已经观察到 sharp changes 会使若干窗口退化，也观察到双 GPU 在大规模下因 GPU-1 空闲、GPU-2 承担 fine-grid 而接近 1.0x 加速。[pdf:E08]（PDF 物理页 8，Section III-C）[pdf:E10]（PDF 物理页 10，Section IV-B）若在保持串行 fine 参考精度的前提下，PiT+PiS 在大部分事件相位都慢于 PiS-only，那么“混合两个并行维度即可获得稳健额外加速”这一核心机制就被实质推翻，而不能用最终串行回退仍然准确来回避。

## § 12 — Follow-up Research Idea

在电力系统计算领域，高影响研究通常不仅看峰值 speedup，还看数值可信度、复杂故障覆盖、跨规模与跨硬件可扩展性，以及实现是否能服务真实工程分析。基于本卡未做外部全文检索，下面仅是**候选研究方向，不声称 novelty**。

候选方向是把固定时间窗的 PiT+PiS 重新定义为“事件条件化的异构时空调度问题”：目标不再是预先切出相等时间窗并静态指定 coarse/fine GPU，而是在误差预算约束下，在线联合决定窗边界、coarse fidelity、Parareal 并发度以及 CPU/GPU 任务放置。驱动它的未满足需求是：最需要 EMT 的故障和开关不连续恰好会让固定 coarse predictor 失真，而多 GPU 又会因静态角色分工形成空闲资源。

这一方向可能有研究价值，因为它把“平均工况的峰值加速”转为“在给定事件密度和硬件资源下，对精度与最坏墙钟时间负责”。可借鉴相邻领域的 adaptive time stepping、task-graph scheduling、online load balancing 与 event-triggered control，但其服务对象是带 DAE、开关不连续和 TS–EMT 波形接口的联合仿真，不是给现有代码简单增加一个负载均衡模块。论文自己的文献谱系已经包含 Parareal 收敛分析、adaptive coarse solver、hybrid deferred correction、Thrust 与 CUDA unified memory，但没有在本 PDF 中建立上述联合在线调度问题；由于本卡未继续读取这些参考文献全文，这一差异仍是候选判断。[pdf:E11]（PDF 物理页 11，References [18]、[28]–[34]）

首个可证伪实验就是第 11 节的事件相位扫描：若在线策略不能在同一误差阈值下同时降低 Parareal 迭代数和 GPU idle，或其决策开销使其仍慢于静态 PiS-only，那么研究假设失败。它与本文的实质区别在于，本文固定 coarse/fine 步长、时间窗结构和 GPU 角色，并在失败时依赖串行回退；候选方法把事件可预测性和实时资源占用纳入问题定义，试图直接控制导致回退和负载不均衡的原因。
