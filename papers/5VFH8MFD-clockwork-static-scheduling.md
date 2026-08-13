# Clockwork: Resource-Efficient Static Scheduling for Multi-Rate Image Processing Applications on FPGAs

**作者**：Dillon Huff；Steve Dai；Pat Hanrahan  
**出处**：2021 IEEE 29th Annual International Symposium on Field-Programmable Custom Computing Machines (FCCM)  
**年份**：2021  
**DOI**：10.1109/FCCM51124.2021.00030  
**Zotero key**：5VFH8MFD  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

Clockwork 要解决的不是“怎样把一段图像算法综合成 FPGA”这个宽泛问题，而是更具体的编译断层：算法作者习惯把应用写成按阶段顺序执行的数组 loop nest；高效硬件却希望所有阶段形成一个并发、流式、固定节拍的流水线。传统 HLS 往往把每个 stage 单独调度，再用 inter-stage FIFO 连接。这样容易综合，却为 FIFO 付出 LUT、FF、BRAM 和能耗，还阻断跨 stage 优化。论文的核心技术 claim 是：把 polyhedral dependence/schedule 与 synchronous dataflow（SDF）的固定 rate 约束结合，可以把支持的多速率 loop nests 编译成单个 flat、statically scheduled module，从而获得 fixed latency、无 inter-stage FIFO 开销且不会因运行时 token 等待而 deadlock。[pdf:E01]（PDF 物理页 1，Abstract、Fig. 1）

这个问题重要，因为 multi-rate 不是边角模式：downsample、upsample 和 stencil 会使 stage 的生产/消费速率不同；如果编译器不能把这些速率放进同一个静态时间表，就只能保留整幅中间图像或依赖动态 FIFO。Clockwork 的价值因此是把“什么时候执行哪个 stage、需要复制多少计算、一个中间值活多久”前移到编译期，使 HLS 接收更规则的完美 loop nest，而不是让运行时队列承担协调。

对 ResearchStudio 而言，最可迁移的目标不是图像像素吞吐本身，而是类似的编译问题：把固定有根三相 VSC 集电树的完整 step DAG 变成确定性执行表，并把依赖延迟和暂存 lifetime 一并纳入 `T_commit`。但这只是问题结构上的类比；Clockwork 的证据来自周期性像素流，不能直接证明有限 EMT 步、固定 PE 和真实双端口 bank 上的完整无冲突调度。

## § 2 — 前人工作与不足

论文把 prior systems 分成三类。第一类是 Halide-HLS、Rigel、Polymage-FPGA、Hipacc-FPGA 和 SODA 等 stage-wise/dataflow 编译器：它们能够生成 line-buffered pipeline，但至少部分依赖 inter-stage FIFO。第二类是 Darkroom：能够 static schedule，却不支持 multi-rate 或 multi-pixel-per-cycle。第三类是 Aetherling：支持 multi-rate static scheduling，但论文报告其 scheduler 大约超过五个 stage 就不再扩展。作者据此把缺口界定为“现实规模、多 stage、多速率、全应用 flat static schedule”同时成立。[pdf:E02]（PDF 物理页 1，Introduction 右栏）

polyhedral 编译本身也不是空白。已有方法能表达 tiling、skewing、scaling、permutation 和 fusion，还被用于 re-use buffer、FIFO sizing 与 loop reordering；问题在于通用 polyhedral code generation 容易产生 imperfect loop nest 以及 division/modulus-heavy indexing，给硬件 HLS 带来低效或不稳定的 dependence analysis。SDF 则能通过固定 token rate 的 balance equation 判断是否存在 bounded-memory、deadlock-free 的周期 schedule，但其 actor/FIFO 编程模型不等同于图像作者的顺序数组 loop nest。Clockwork 的路线是保留前端的数组程序，用 dependence analysis 抽出与 SDF rate 等价的约束，再生成单一完美 loop nest。[pdf:E03]（PDF 物理页 2，Fig. 2 与 Section II）

这里应谨慎理解论文的比较强度。作者确实展示了 Clockwork 与 SODA 的同吞吐资源对照；但多速率部分没有一个同等级、自动化且可扩展的现成编译器作 baseline，因此改用朴素 HLS loop-nest 实现。由此可以支持“相对该参考实现，flat schedule 有巨大收益”，却不能把多速率结果解读为对所有可能的手工 FIFO sizing、定制 RTL 或其他 static scheduler 的全面胜出。

## § 3 — 重建作者的思考路径

可以从两个既有事实重建这条路线。其一，polyhedral schedule 已经能把 statement instance 映射到 lexicographic timestamp，所以“消费者必须晚于其最后一个生产者”本来就是线性时间约束。其二，SDF 已经知道：若 actor 每次 firing 的 token 生产/消费量固定，那么各 actor 的相对 firing rate 由 balance equation 决定；例如 producer `P` 每次产 1 个 token，consumer `C` 每次消耗 2 个 token，就有 `r_P = 2r_C`，一个合法周期是 `PPC`。[pdf:E04]（PDF 物理页 3，Fig. 3、Fig. 4、Synchronous Dataflow Scheduling）

由此自然得到四步推理。第一，不直接求任意 affine schedule，而只求能无限重复的高质量 schedule；这样结果不依赖图像边界。第二，把 producer/consumer dependence 对 timestamp 的不等式展开，要求随迭代索引增长的系数抵消，于是 polyhedral 的 slope 条件退化为 SDF balance rate。第三，在 rate 固定以后，仅优化各 stage 的 delay，使消费者尽早跟随生产者，从而缩短中间值 lifetime 和 buffer。第四，目标吞吐不足时，不重新搜索完全不同的 schedule，而根据 rate 推出各 stage 的 unroll factor，再让 HLS 对生成的完美 loop nest 做 cycle-level pipeline scheduling。

这条思路的关键不是“把 SDF 图翻译成 C++”，而是用 SDF 的周期平衡来限制 polyhedral schedule 的形状：牺牲通用 affine schedule 的自由度，换取可预测、可生成、可扩展的硬件结构。

## § 4 — 核心 Intuition

不同 stage 不必各自跑完一整幅图，也不必靠 FIFO 在运行时互相等待；只要每个 stage 的固定消费/生产速率能平衡，就可以在编译期把它们按一个重复节拍交错进同一 loop nest。rate 决定各 stage 多久执行一次，delay 决定消费者在依赖满足后多快执行，unrolling 决定每周期复制多少工作。于是“大中间图 + 动态队列”被缩成“工作集大小的 re-use buffer + 固定控制”。

## § 5 — 具体方法与完整 Pipeline

**输入与可行域。** Clockwork 接收一串原本顺序执行的 loop nests 和目标吞吐 `T`。每个 nest 必须属于 stencil、upsample 或 downsample，区别是输入访问 stride 分别等于 1、小于 1 或大于 1；访问与 loop index 之间保持线性。编译器若找不到它认为高效的 schedule，可以失败，而不是承诺覆盖任意 affine program。[pdf:E05]（PDF 物理页 3，Fig. 5、Section III 开头）

以 brighten 后 2× downsample 的例子看，原程序先生成完整 `64×64` 中间图，再执行 blur，需要 `4096` pixel 的暂存且吞吐低于每周期 1 pixel。目标设为每周期 2 pixel 后，完整 pipeline 是：

1. **dependence analysis**：识别 `C(i)` 读取 `P(2i)` 与 `P(2i+1)` 的结果，建立 consumer-after-producer 约束。
2. **rate 求解**：由固定访问 stride 得到 `q_C = 2q_P`；`q` 表示 statement instance 在新 fused loop 中的发射间隔。
3. **delay/lifetime 优化**：在依赖合法的前提下最小化 producer 与 consumer 的 delay 差，让消费尽早发生，减少中间数据活跃区间。
4. **unrolling**：brighten loop unroll 2 倍，对应分配两个 brighten PE；blur 每次本就消耗两个 pixel，因此此时不需要复制。
5. **fusion 与谓词化**：把两个 nest 合成一个完美 loop nest，用条件谓词只在 downsample 的数据依赖齐备时执行 blur。
6. **buffer lowering**：中间 `br` 从约 `64×64` pixel 的整图 buffer 缩为约 `64` pixel 的工作集，再降为 66-entry shift register。
7. **硬件生成**：输出 synthesizable HLS C++，交给 Vivado HLS 做内部 pipeline scheduling；示例生成模块以 `II=1` 执行，每周期读取两个输入 pixel。[pdf:E06]（PDF 物理页 4，Fig. 6）

多 nest、多维情况从 outermost 到 innermost 逐层 fusion，并把 dependence 投影到当前层；维数不匹配时插入 single-iteration loop；fractional upsampling stride 则先乘所有 upsample factor 的 least common multiple。存储侧，论文做的是根据静态依赖和滑窗模式生成 re-use buffer，并让同步访问模式暴露给 synthesis，以便合并 bank 或映射 shift register。论文没有给出“每个 cycle 的每次读写已经绑定到某个真实 dual-port bank/port，且不存在同址 read/write hazard”的证明，因此不能把 buffer lowering 自动视为 ResearchStudio 的真实双端口 bank 无冲突证据。

资源共享边界也很明确：该版本通过 unrolling 复制 compute unit 来提高吞吐，并未实现 cross-stage resource sharing；作者把它列为未来工作。Clockwork 的“资源高效”主要来自去掉 stage FIFO、缩短 buffer lifetime、暴露跨 stage 的存储合并机会，不是用一组 PE 在多个 stage 之间做时分复用。

## § 6 — 核心数学推导（无形式化数学则跳过）

令 `s_P(j)` 和 `s_C(i)` 表示原 producer/consumer 的某个 instance 被放到 fused loop 的哪个逻辑时刻。合法性首先要求 consumer 晚于它读取的每个 producer：

\[
s_C(i) \ge s_P(j),\qquad \forall i\in[0,2],\ \forall j\in[2i,2i+1].
\]

Clockwork 为得到可无限重复、与 loop bound 无关的 schedule，把 `i∈[0,2]` 强化为所有 `i`。再假设线性 schedule

\[
s_C(i)=q_C i+d_C,\qquad s_P(j)=q_Pj+d_P,
\]

并利用 raster-order 输入要求 `q_C,q_P≥1`，只需约束 consumer 晚于最后一个依赖 `P(2i+1)`。展开后得到

\[
(q_C-2q_P)i+(d_C-q_P-d_P)\ge0,\quad\forall i.
\]

为了让该式对所有 `i` 成立且不随边界漂移，斜率项必须抵消：

\[
q_C=2q_P.
\]

这正是 SDF balance equation。若 balance matrix 的 rank 等于 loop-nest 数量减一，则存在满足 rate 方程的正值；本例取 `q_P=1,q_C=2`。剩余常数约束是 `d_C≥1+d_P`，以 buffer size 代理目标最小化 `d_C-d_P`，得到 `d_P=0,d_C=1`，最终 schedule 为

\[
S_P(j)=[j,0],\qquad S_C(i)=[2i+1,1].
\]

第一维给出周期中的逻辑时刻，第二维在同一时刻内把 `P` 放在 `C` 之前；对应 fused loop 可以由 HLS pipeline 到 `II=1`。[pdf:E07]（PDF 物理页 4，Eq. (1)–(9)）

目标吞吐为 `T` 时，producer 要读满每周期 `T` 个 pixel，论文先取 `u_P=Tq_P`，再对 downstream consumer 取

\[
u_C=\left\lceil\frac{u_P}{q_C}\right\rceil.
\]

本例 `T=2` 时 `u_P=2,u_C=1`，说明 consumer 原本只有 50% utilization，无需随 producer 一同复制；到 `T=4` 才需要把 `C` unroll 2 倍。[pdf:E08]（PDF 物理页 5，Eq. (10)、Sections III-B–III-D）

工程上，`q` 是周期 rate/issue spacing，`d` 是 stage start delay，`u` 是空间复制因子。它们分别对应“多久做一次”“最早何时做”“一次并排做多少份”。对于 `T_commit`，可迁移的是 dependence-before-issue 和 lifetime-minimizing delay；不可直接照搬的是“去掉边界并无限重复”的推导，因为完整 EMT step DAG 是一个有明确起止和 commit 屏障的有限计算，而不是稳态 pixel stream。

## § 7 — 实验设计与结论

**问题 1：去掉 inter-stage FIFO 后，同吞吐 stencil pipeline 是否更省资源？** 作者用 Blur、Sobel、Camera Pipeline（10 stage）和 Jacobi（15 stage）对比 SODA，覆盖 `1/16/32 pix/clk`。Table I 给出 LUT、LUTAsMem、FF、BRAM、DSP 的逐项结果；Clockwork 与 SODA 的 DSP 数相同，而 Clockwork 的 LUTAsMem 普遍更低。[pdf:E09]（PDF 物理页 5，Table I）实验使用 `1080×1080`、16-bit pixel、250 MHz，资源和 timing 取 Vitis post-PnR report，两者均满足 timing，AWS 实际吞吐彼此在 5% 内。作者报告跨应用平均减少 55% LUT、30% FF、22% BRAM；在 1 pix/clk 时分别少 38%、19%、6%，在 32 pix/clk 时扩大到 65%、37%、42%。[pdf:E10]（PDF 物理页 6，Section IV-A）答案是：在这组同吞吐 stencil workload 上，flat static schedule 的资源优势成立，且 throughput 越高差距通常越大。不能忽略的是 Camera Pipeline 为适配 SODA，部分 SODA 不支持的 table lookup/coordinate compute 被简化。

**问题 2：多速率、深 pipeline 能否自动生成并扩展？** 因没有找到同时支持大规模 multi-rate 且可维护、可自动比较的系统，作者改用常规 HLS 参考：按 stage 写顺序 loop nests，只 unroll trip count 小于 10 的小 inner loop，并逐 nest 加 pipeline pragma。workload 是 Max Pooling（1 stage）、Gaussian Pyramid（8 stage）和同时含 stencil/upsample/downsample 的 Synthetic Exposure Fusion（53 stage）；GP/SEF 输入是 `1920×1080`，MP 是 `128×128×64`，均为 16-bit。[pdf:E11]（PDF 物理页 6，Section IV-B）这使实验能证明 Clockwork 相对该参考实现的收益，却不能闭合对最强手工多速率 RTL/FIFO baseline 的优越性。

Table II 显示：MP 的 HLS 参考为 `6.3 ms/1025 BRAM`，Clockwork 在 32 pix/clk 时为 `0.131 ms/37 BRAM`；GP 的参考需要 `2577 BRAM`、无法 PnR，Clockwork 32 pix/clk 为 `0.274 ms/8 BRAM`；SEF 参考需要 `22284 BRAM`、无法 PnR，Clockwork 32 pix/clk 为 `0.276 ms/55 BRAM`，但此点也消耗 `141419 LUT` 和 `300 DSP`。[pdf:E12]（PDF 物理页 7，Table II）GP/SEF 的 HLS 参考只使用 post-synthesis resource 与 HLS execution estimate，不能与 Clockwork post-PnR 点作完全对称的物理实现比较。

**问题 3：compiler 本身是否扩展？** Clockwork 前端 compile time 在全部应用中低于总 compile time 的 5%；真正的瓶颈转到 Vivado HLS dependence analysis。当 throughput target 与 stage 数乘积超过约 200，HLS 时间开始变得难以接受；SEF unroll 32 的 HLS dependence analysis 超过 7 小时，但所有应用最终仍推得 `II=1`。[pdf:E13]（PDF 物理页 7，Scalability）答案是：Clockwork 的 rate/schedule 求解可以扩展到 53 stage，end-to-end toolchain 的高吞吐深 pipeline 编译时间仍受 HLS 制约。

**问题 4：能效是否优于 CPU/GPU？** 作者把能效定义为输入 pixel throughput 除以功耗。PCIe Gen3×16 read bandwidth 取 16 GB/s、每 pixel 2 byte、F1 idle power 取 7 W，得到理论上限约 1.14 GPix/J；CPU 是 8-thread Xeon E5-2686 + Halide CPU auto-scheduler，GPU 是 K80/V100 + Halide GPU auto-scheduler。CPU/FPGA 使用 16-bit integer 运算，GPU 虽以 16-bit 存储却用 32-bit float 运算；CPU/FPGA 功耗不含额外 DRAM，GPU 数字包含板载 DRAM，比较口径并不完全同构。[pdf:E14]（PDF 物理页 8，Fig. 7 与 Energy Efficiency）Clockwork 达理论峰值的 46%–69%；在 SEF 上报告为 CPU 的 260 倍、K80 的 17 倍、V100 的 2.4 倍。

**问题 5：请求吞吐能否在真实 FPGA 上兑现？** SEF 的实测双向 bandwidth 随请求 throughput 增长，在高 throughput 约达到 ideal 的 80%；作者同时指出最大 SEF-32 设计受 PCIe bandwidth 限制。[pdf:E15]（PDF 物理页 8，Fig. 8、Conclusion）答案是：实测趋势支持 target-driven unrolling，但不是理想吞吐的 100%。

总的实验边界是：论文验证了 Xilinx VU9P、Vitis/AWS F1、16-bit image/tensor pipelines；没有验证 event-dependent workload、任意 affine access、跨 stage PE sharing、真实双端口同址 hazard、EMT 数值精度或完整 step commit semantics。

## § 8 — Take-aways

**5 句话：**

1. Clockwork 用 SDF balance rate 限制 polyhedral schedule，把支持的 multi-rate loop nests 融成一个可重复的 flat static schedule。
2. rate `q` 决定 stage 节拍，delay `d` 缩短 producer-consumer lifetime，unroll `u` 把吞吐目标转换为空间复制。
3. 它的主要资源收益来自消除 inter-stage FIFO、缩小中间工作集，并把同步访问模式暴露给 HLS 做存储合并。
4. 同吞吐 SODA 比较较强，但 multi-rate 比较采用朴素 HLS reference，且 GP/SEF reference 无法 PnR，因此结论应限定在给定 baseline 和平台。
5. 对 ResearchStudio 可借鉴 dependence-rate-delay-lifetime 的联合表述，但必须另行加入有限 step、PE assignment、真实 bank/port 与同址 hazard 约束。

**3 句话：** Clockwork 证明了周期固定 rate 可以把 stage-wise 图像程序压成单一确定性 loop nest。这样既减少 FIFO/整图 buffer，也让吞吐通过可推导的 unrolling 实现。它不是通用 DAG 或真实双端口 memory scheduler，迁移到 EMT 必须重建时间模型和物理资源约束。

**1 句话：** 用编译期的周期 rate、依赖 delay 和 unrolling 取代运行时 FIFO 协调，是 Clockwork 的核心贡献，也是它最值得迁移但不能原样照搬的部分。

## § 9 — 最脆弱的假设

失败代价最大的假设是：每个 stage 的生产/消费量与 affine stride 固定，因此存在一个不依赖 loop bound、可无限重复的正 rate schedule。这个假设一旦失效，`q` 的 balance equation 就不再描述真实执行，`u=Tq` 也不能保证吞吐，consumer predicate 和 buffer lifetime 会随数据或边界变化，flat schedule 的 fixed-latency/deadlock-free 结论随之失去适用基础。

论文对该假设的证据是方法上的显式输入限制（stencil/upsample/downsample、线性 stride）以及 MP/GP/SEF 的成功生成；它没有实验 event-triggered stage、data-dependent iteration count、动态拓扑或一帧内 mode-changing rate。对固定 VSC 集电树而言，拓扑和完整 step DAG 可以静态化，这是有利条件；但 `T_commit` 的有限起止、Rake/Compress 选择、Schur 消元后的全状态恢复、读写 phase 与 commit barrier 并非无限 pixel stream。必须先证明“每步结构固定且所有操作次数、依赖和 memory access 可在编译期枚举”，才能借用其静态 schedule 思想。

## § 10 — 最小复现实验

一周内最小复现不必重建 53-stage SEF。选择论文的 brighten→2×downsample 两 stage 例子，再增加一个带 reconvergence 的三 stage Sobel-like pipeline，分别生成三种版本：原始整图顺序 HLS、per-stage `dataflow` + FIFO、Clockwork 式 flat fused loop。对 `T=1/2/4` 固定 16-bit 输入和同一 250 MHz target，测量 post-synthesis 或 post-PnR 的 II、端到端 cycle、LUT/FF/BRAM/LUTAsMem，以及实际 buffer depth；同时用软件 reference 逐 pixel 比较输出。

支持核心 claim 的最低标准是：flat 版本对全部测试输入 bit-exact，达到目标 II，buffer 从整图降到 line/working-set 量级，并在同吞吐下相对 FIFO 版本显著降低 LUTAsMem/FF，且收益随 T 不消失。反驳标准是：在输出正确和同吞吐条件下，flat 版本因 predicate/address logic 或 HLS dependence analysis 不能达到 II，或者其总 LUT/FF/BRAM 不低于 FIFO 版本。该实验只复现“静态 fusion 减少 FIFO/working-set”的核心机制，不试图复现论文的 CPU/GPU 能效结论。

## § 11 — 最强反例设计

最强攻击应留在作者声称支持的 fixed-rate class 内，而不是简单换成动态算法。构造一组深度递增、含 reconvergence 的 multi-rate graph：多条分支使用互质 up/downsample factor，在末端汇合，并让边界 stencil 产生不同 phase 的有效区间；保证每个单独 stage 都是合法的 stencil/upsample/downsample。互质 rate 会放大 least-common-multiple period，reconvergence 会拉大 delay 差，边界 predicate 会增加地址和控制逻辑。

随后对同一 graph 比较三种实现：Clockwork 的 bound-independent flat perfect loop、允许利用有限 frame bound 的最优/近优 finite polyhedral schedule、以及经过认真 FIFO sizing 的 modular pipeline。测量 schedule period、最大 live set、buffer bank 数、predicate/address LUT、HLS compile time、II 与 post-PnR 资源。若 finite-bound 或 FIFO 版本在同吞吐下稳定使用更少资源，而 Clockwork 随 rate LCM 或分支深度出现超线性 schedule/control 膨胀，甚至在存在高效有限 schedule 时返回失败，就说明“强化为可无限重复 schedule”不是无害的可扩展性技巧，而是可能排除现实中更优实现的核心偏置。

## § 12 — Follow-up Research Bet

**主 idea：有限完整步的 phase-expanded compute–memory co-scheduling。** 候选研究问题是：能否把 Clockwork 的 rate/delay/lifetime 联合思想从无限重复的 pixel stream 改写为一个有明确开始、全状态恢复和 commit 终点的 finite EMT step，并在同一个编译问题里同时决定 operation issue time、固定 PE assignment、dual-port bank/port assignment 与 buffer slot？它首次使“精确 Schur 消元—全状态恢复的完整 step DAG”不仅有逻辑拓扑，还能生成一张对 `T_commit` 和每个真实 bank port 都可执行的确定性表。

核心因果链是：具体 VSC tree 决定 Rake/Compress 与完整 DAG → 把每个 operation 展开成有限 phase，而不是假设 ad-infinitum rate → 用 producer-consumer delay 决定最早 issue 与 value lifetime → 用 lifetime overlap 建立 slot reuse，用逐 cycle access 建立 bank/port 互斥与同址 read/write 次序 → 在全部计算和恢复完成后设置唯一 commit barrier → 联合最小化 `T_commit`、PE 数和 bank footprint。相较 Clockwork，它至少改变了时间模型（周期 steady state 变为有限 complete step）、表示对象（stage rate 变为 phase-expanded DAG）和硬件映射（buffer size 变为具体 bank/port schedule）。

论文特异依据有两类：方法上，Eq. (1)–(9) 已把 dependence、rate 与 delay 分开，Eq. (10) 又把 throughput 映射为空间复制；实验上，作者把 BRAM 降低归因于静态可见的同步读写/存储合并，并展示 FIFO 消除后资源显著下降。与此同时，论文明确没有 cross-stage resource sharing，且只证明 re-use buffer 生成，没有真实 dual-port 同址 hazard 的逐 cycle 证明；这正是新问题必须显式增加的设计变量，而不是从 Clockwork 结果中自动继承。

最大研究收益是把当前 N=7 trunk 的软件证据推进为可在真实 PE/bank 组织上执行的完整确定性 EMT step，得到可测的 `T_commit` 与 memory conflict 边界。最大科学风险是：finite DAG 的 PE、bank、port、slot 联合约束可能使求解规模失控，或者真实依赖几乎没有 lifetime reuse，最终不比现有分阶段编排更短也不更省。

首个区分实验只用现有 N=7 trunk：固定同一 Rake/Compress DAG，比较三种模型——仅 precedence 的最早开始表、加入 lifetime 但抽象无限端口的表、加入真实 dual-port bank/port 与同址顺序的表。若第二种看似满足 `T_commit` 而第三种必须插入 stall 或增加 bank，便直接证明存储可行性不是 Clockwork 式 buffer sizing 能替代的；再与一个“只增加 bank、不联合改 issue time”的替代解释比较，若联合调度以同样 bank 数得到更短 `T_commit`，才支持核心机制。

这是一项基于本文机制和 ResearchStudio 现状的候选判断。由于本任务没有检索相关工作的完整全文，不声称 novelty；与最近工作的实质差异也只能限定为：相对本文的周期图像 rate schedule，它研究 finite full-step、full-state recovery 与真实 bank-port execution object。

**Wild-card alternative：** 用 balance rate 的 residue class 把不同 EMT phase 折叠到少量可时分复用的固定 PE 上，在放宽 `T_commit` 的条件下研究跨 phase resource folding；它改变的是计算资源共享机制而非主 idea 的 bank-lifetime 联合机制，同样仅是候选判断。
