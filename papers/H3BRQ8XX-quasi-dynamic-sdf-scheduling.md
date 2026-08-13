# From Static to Quasi-Dynamic: Reconsidering Scheduling and Memory in SDF Compilers

作者：Pedro Ciambra、Anaëlle Cloarec、Hervé Yviquel、Mickaël Dardaillon、Maxime Pelcat（PDF 物理页 1，标题与作者区）[pdf:E01]

出处：2025 IEEE/SBC 37th International Symposium on Computer Architecture and High Performance Computing Workshops（SBAC-PADW）（PDF 物理页 1，页眉与题名页）[pdf:E01]

年份：2025（PDF 物理页 1，题名页）[pdf:E01]

DOI：10.1109/SBAC-PADW69789.2025.00012（PDF 物理页 1，题名页）[pdf:E01]

Zotero key：H3BRQ8XX

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

结论：这篇论文要解决的不是“动态调度能否普遍跑得更快”，而是一个更具体的编译器取舍问题：**能否保留 SDF（Synchronous Dataflow，同步数据流）的静态速率、delay 和拓扑信息，却不在编译期把 multi-rate graph（多速率图）完整展开成逐 firing 的 single-rate graph（单速率图）？** 作者希望把会导致编译时间和二进制膨胀的决策推迟到运行期，同时让运行期只重建当前真正需要的 firing、依赖和内存，而不是承担通用动态数据流 runtime 的全部不确定性。论文将这种折中称为 quasi-dynamic scheduling（准动态调度），核心载体是 virtual FIFO（虚拟 FIFO）和 keyed semaphore（键控信号量）（PDF 物理页 1，Abstract 与 Introduction）[pdf:E02][pdf:E03][pdf:E04]。

传统静态 SDF 编译的优势很明确：固定 port rate 让 actor firing 次序、处理器分配和内存偏移可以预先决定，运行时延迟与内存占用较容易预测；single-rate SDF 又进一步要求 edge 两端 rate 匹配（PDF 物理页 2，Section II-B）[pdf:E05]。其常见实现会按 token rate 的最小公倍数复制 actor、插入 fork/join，并把每次 firing 显式编码到调度中；Fig. 2 直接说明 single-rate 转换后的节点数随速率最小公倍数增长（PDF 物理页 3，Fig. 2）[pdf:E06]。更严重的是，论文指出这种展开在某些拓扑和速率组合下可呈指数增长；即使是规则的矩阵逐元素操作，静态 schedule 的大小和编译时间也会随矩阵元素数增长，并丢失原本可供后端利用的规则性与对称性（PDF 物理页 4，Section IV-A）[pdf:E07]。

这个问题重要，是因为编译成本本身会成为可部署性的边界。论文明确指出，大 token ratio 会让静态编译在并不缺资源的机器上也变得不可行，动态重编译场景尤其受限（PDF 物理页 4，Section IV-A）[pdf:E07]。在作者的 degridder（反网格化）实验中，quasi-dynamic 原型相对 Preesm 报告了平均 12.2 倍的调度编译加速、平均 4.4 倍更小的二进制，而平均执行变慢约 1.4 倍（PDF 物理页 1，Abstract）[pdf:E02]。因此，论文的价值不在于宣称运行期调度取代静态调度，而在于把“低运行时开销”与“可编译的大图”之间原本近似二选一的关系改造成可测量、可选择的 trade-off（权衡）。

## § 2 — 前人工作与不足

**论文对相关工作的直接概括如下。**

- **Preesm** 代表静态路线：把 piSDF/SDF 转成 single-rate graph，生成包含预计算 schedule 的 C 文件，再与 actor kernel 链接。它可以在编译期做 memory exclusion graph 等分析，预先存储内存偏移和处理器分配，因而运行时几乎不需要临时决策；代价是 schedule 和 binary 会跟展开图一起增长（PDF 物理页 3，Section III；物理页 4，Section IV-A）[pdf:E08][pdf:E07]。
- **Spider/piSDF** 使用静态已知参数支持偶发重配置，并在参数变化后生成新 schedule；它扩大了 SDF 的适用范围，但仍以图展开和重新调度为主要路径，没有取消 firing 级静态表示的根本成本（PDF 物理页 3，Background 与 Related Works）[pdf:E08]。
- **Orcc** 代表通用动态 runtime：它面向可数据依赖的 RVC-CAL，依靠运行期调度和 ring buffer，并要求程序员手工给定各 edge 的 buffer size。常规 ring buffer 只暴露 FIFO 头尾，通常只能让不同 actor 并行，难以让同一 actor 的多个 firing 同时“越过队首”执行（PDF 物理页 3，Section III；物理页 4，Section IV-B）[pdf:E08][pdf:E09]。
- **Taskgraph** 通过记录并重放有效 schedule 来降低 OpenMP 静态 task DAG 的同步开销，但论文指出它局限于 single-rate、acyclic graph（无环图），不能直接覆盖这里的 multi-rate、可能有环、完全 self-timed（自定时）的 SDF（PDF 物理页 3，Section III）[pdf:E08]。
- **IaRa** 是作者已有的 MLIR dataflow compiler；本论文的贡献被实现为 IaRa 的新 scheduling mode，而不是另建完整编译栈（PDF 物理页 3，Section III）[pdf:E08]。

已有方案“不够”的原因并非简单地“没有考虑动态性”。静态方案把可预测性换成逐 firing 展开，扩张的是**表示和代码生成成本**；通用动态方案则为了应对 Turing-complete 行为，不能假定 edge 中 token 数有静态上界，也很难利用固定 rate 与 delay。ring buffer 还把逻辑 FIFO 次序和连续循环地址绑定在一起：直接读 ring buffer 会让 actor 感知 modulo layout 并占住 buffer，复制到临时区又增加 copy、空间和带宽；self-growing ring buffer 虽能扩容，却不能自然把闲置内存归还给其他 edge（PDF 物理页 5，Section IV-B）[pdf:E10]。作者由此把 quasi-dynamic 明确定义为“具有编译期图专用优化的 runtime scheduler”，并把系统拆成 virtual FIFO 与 keyed semaphore 两部分（PDF 物理页 5，Section V）[pdf:E11]。

**基于证据的推断：**作者真正改变的假设是“FIFO 语义必须由一个连续、按时间顺序推进的循环数组实现”。一旦把逻辑 token 位置与物理地址分开，SDF 已知的 rate、delay 和拓扑就足以在编译期生成图专用规则，再由运行时只物化当前活跃的 block、slice 和依赖项。这正是现有静态与通用动态方案之间尚未覆盖的中间层。

## § 3 — 重建作者的思考路径

以下是基于全文证据逆向重建的思考链，不是作者逐字给出的研发日志。

1. **先区分语义与实现。** SDF 要求每个 port 的 token rate 固定，并不要求编译器一定把每个 firing 复制成独立节点；single-rate expansion 是便于静态排程的实现选择，而不是 FIFO 语义本身。Fig. 2 和 Section IV-A 暴露了这一实现选择在高 rate 与规则 tensor workload 上的尺度问题（PDF 物理页 3，Fig. 2；物理页 4，Section IV-A）[pdf:E06][pdf:E07]。
2. **再找运行期方案的真正阻塞点。** 通用 ring buffer 用 front/back pointer 保证 FIFO，但 wrap-around、连续内存占用和仅暴露队首队尾，会把“某个 firing 逻辑上是否就绪”与“它访问的物理区间是否可用”缠在一起（PDF 物理页 4，Fig. 3 与 Section IV-B）[pdf:E09]。
3. **利用 SDF 比通用动态图多出的信息。** producer/consumer rate、initial delay、in-place chain 和每个 consumer 所需的总输入量都在编译期已知。因此可以先解除 firing dependency 与具体内存区域的绑定，再保存 block、slice 与 virtual offset，而不必提前决定 block 的实际地址、firing 的执行线程和实际时间顺序（PDF 物理页 5，Virtual FIFO）[pdf:E12][pdf:E13]。
4. **把地址顺序改成逻辑顺序。** 给每个 slice 保存 pointer、size 和单调递增的 virtual offset；offset 表示它位于无限逻辑 FIFO 的哪个 token 区间，物理 block 则可独立分配，甚至按不同于 firing 序号的时间顺序出现（PDF 物理页 5，Section V-A）[pdf:E13]。
5. **把静态依赖表改成短生命周期的运行期状态。** producer 完成后，根据 offset 与 rate 计算下游 firing，把 slice 交给以 firing sequence number 为 key 的 semaphore entry；entry 的 resource counter 归零时才提交 actor task，随后立即销毁并复用同步资源（PDF 物理页 6，Fig. 4 与逐步说明）[pdf:E14][pdf:E15]。
6. **把通用执行机制留给成熟 runtime。** 图专用部分只负责 block/slice 和依赖重建，线程分配、heap allocation 与 task execution 交给 malloc、OpenMP Tasks 和并发 hash map。这样原型可以先验证表示和调度思想，再把 allocator、同步和 locality 优化留给后续工作（PDF 物理页 8，Section V-C）。

这条路径的关键不是“静态改动态”，而是把静态信息从**完整 schedule**压缩成**运行期重建规则**。

## § 4 — 核心 Intuition

核心不是把 SDF 变成不可预测的动态数据流，而是只把最容易导致图和代码爆炸的 firing 实例化、线程选择与物理地址选择推迟到运行期。virtual FIFO 用 block、slice 和 virtual offset 保留逻辑 FIFO 次序，却解除它与连续 ring buffer 地址及时间顺序的绑定；keyed semaphore 再用编译期已知的输入需求恢复 firing 依赖（PDF 物理页 5，Section V）[pdf:E11][pdf:E12]。因此，binary 可以更接近原始 multi-rate graph 的规模，而运行时只为当前活跃 firing 支付状态和同步成本。

## § 5 — 具体方法与完整 Pipeline

以论文 Fig. 4 的真实例子说明：actor `P` 每次产生 3 个 token，actor `Q` 每次消费 2 个 token；编译器选择能同时容纳 `P` 的 2 次 firing 和 `Q` 的 3 次 firing 的 6-token block（PDF 物理页 6，Fig. 4）[pdf:E14]。右栏的逐步说明给出了 slice 拆分、依赖累计和乱序执行如何保持正确（PDF 物理页 6，Fig. 4 walkthrough）[pdf:E15]。

1. **读取 SDF 与内存共享关系。** 编译器保留 multi-rate graph，不先展开成所有 firing。它识别 edge、rate、delay，以及哪些 input/output port 可 in-place 共用同一物理区间。论文中的数据对象仍是 actor 之间的 token；scheduler 只新增 block 与 slice 元数据，不改变 token 的数值格式。
2. **生成 block 大小与显式内存 actor。** 对简单无 delay edge，block size 可取相关 rate 的最小公倍数；对含 delay 或跨多个 in-place actor 的 read-write chain，则先按 Fig. 5 确定首块与后续块的边界语义，再求解 Eq. 1 的整数对齐约束；Fig. 6/7 分别展示可对齐与无解情形（PDF 物理页 6，Fig. 5；物理页 7，Eq. 1、Fig. 6/7）[pdf:E16][pdf:E17][pdf:E18]。编译器在图中插入 `Alloc` 和 `Free` 节点，使 allocation 与 deallocation 也成为依赖图的一部分。
3. **分配一个逻辑 FIFO 区间。** `Alloc0` 从共享 heap 得到 6-token block `B0[0:6]`，并给它 virtual offset `v=0`。每条 edge 不再拥有固定的大 ring buffer；所有 virtual FIFO 从同一空闲内存池按需取得 block，consumer 完成后再归还（PDF 物理页 5，Section V-A）[pdf:E13]。
4. **producer 产生 slice，而不是推进一个全局尾指针。** `P0` 处理 `B0[0:3]` 后，根据 rate 与 offset 算出这段数据分别属于 `Q0` 的 `[0:2]` 和 `Q1` 的 `[2:3]`。`Q0` 已拿到完整的 2-token 输入，可立即进入 ready 状态；`Q1` 只拿到所需输入的一部分，必须等待 `P1` 再交付剩余 token（PDF 物理页 6，Fig. 4 的逐步说明）[pdf:E15]。
5. **keyed semaphore 合并依赖。** 每个 actor 有一张并发 hash map，以 firing sequence number 为 key。某个依赖首次到达时创建 entry，并把 counter 初始化为 consumer 所有 input rate 的总和；后续 slice 到达时写入 slice list 并扣减 counter，归零后提交该 firing，随即删除 entry。并发 map 被分段加锁，以降低所有 firing 竞争单一 mutex 的概率（PDF 物理页 8，Section V-B）[pdf:E19]。
6. **允许 out-of-order execution。** `P1` 可以先于 `P0` 执行；正确性不依赖真实地址或提交时间，而依赖 virtual offset。后续 `Alloc1` 的 `v` 从 6 开始，再后续 block 依次对应更大的逻辑区间，所以 consumer 仍能重建正确的 firing 编号和 token 子区间（PDF 物理页 6，Fig. 4 说明）[pdf:E15]。
7. **回收整块内存。** slice 沿图传播到 `Free` 节点；当一个 block 的所有 slice 所有权都返回时，`Free` 重建原始 allocation pointer 并把整块交还 heap allocator。这类似 block 级 reference counting（引用计数），但计数关系由图和 slice 传播产生。

**时间推进与多速率。** 该系统是 self-timed：没有统一 timestep，也没有在编译期固定 firing 的绝对顺序；multi-rate 关系通过 rate、offset 和依赖 counter 在事件到达时恢复。论文没有报告 real-time deadline、jitter 或多时钟域模型。

**并行与执行平台。** 当前 proof-of-concept 使用 libc `malloc`、OpenMP Tasks 与 `gtl/phmap`，运行平台是共享内存 CPU（PDF 物理页 8，Section V-C 与实验目标）[pdf:E20]。论文在背景中指出 fixed-size ring buffer 常见于 FPGA、DSP 和 scratchpad，但没有实现或评测 FPGA mapping，也未报告 BRAM/URAM、片上互连、HLS、定点格式或时钟频率；这些内容应视为未报告，而不是从 CPU 结果外推。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的形式化核心不是吞吐率定理，而是**怎样选择 block 边界，使一条 in-place read-write chain 上每个 actor 的连续访问都不跨 allocation boundary**。对 chain 中每条 edge \(e_{ij}\)，作者给出：

\[
D_{ij}+R_i\alpha_i=R_j\alpha_j,\qquad
R_i\beta_i=R_j\beta_j,\qquad \forall e_{ij}\in E.
\]

其中，\(D_{ij}\) 是 edge 的 initial delay 大小，\(R_i\) 与 \(R_j\) 分别是 producer 和 consumer 的 rate；正整数 \(\alpha\) 表示首个、含 delay 的 block 中各 actor 可完整执行多少次，\(\beta\) 表示后续无 initial delay 的 block 中可完整执行多少次（PDF 物理页 7，Eq. 1 及变量定义）[pdf:E17]。

直观上，等式两侧是在要求相邻 actor 看到同一个物理 block boundary。首块需要先跨过 delay，所以有 \(D_{ij}\) 的偏移；后续 block 不再含初始 token，只需让累计生产量与累计消费量相等。无 delay 的简单 chain 因而退化为求各 rate 的最小公倍数。

Fig. 6 给出具体数值：\(D_{PQ}=7\)、\(D_{QR}=9\)、\(R_P=2\)、\(R_Q=3\)、\(R_R=5\)。首块取 \(\alpha_P=7\)、\(\alpha_Q=7\)、\(\alpha_R=6\) 时，第一条 edge 满足 \(7+2\times 7=3\times 7=21\)，第二条满足 \(9+3\times 7=5\times 6=30\)；后续 block 取 \(\beta_P=15\)、\(\beta_Q=10\)、\(\beta_R=6\)，得到 \(2\times15=3\times10=5\times6=30\)。因此这条 chain 的最小对齐 block size 是 30，含 delay 与不含 delay 的 block 都可用这一大小（PDF 物理页 7，Fig. 6）[pdf:E18]。

这些约束是 first-order Diophantine equations（一阶丢番图方程）。作者建议用简单 ILP 求正整数解，并指出 Hermite normal form（Hermite 标准形）理论上更高效，但没有给出复杂度分析、全局最优性证明或大规模 chain 的求解统计；论文只称 ILP 对现实应用中的 chain size 与 rate “似乎足够”（PDF 物理页 7，Eq. 1 后正文）[pdf:E17]。

并非所有组合都有解。Fig. 7 中 producer 与 consumer rate 都为 3、delay 为 4，对首块要求 \(4+3\alpha_A=3\alpha_B\)，左侧模 3 余 1、右侧模 3 余 0，所以不存在整数解；论文规定此时编译失败于该 zero-copy 对齐，必须插入 copy（PDF 物理页 7，Fig. 7）[pdf:E18]。这说明 virtual FIFO 不是无条件消除复制，而是把“能否无复制共享 block”转化成可判定的整数可满足性问题。

## § 7 — 实验设计与结论

**问题：quasi-dynamic 是否能处理静态调度编译过慢、binary 过大的实例？ → 实验：**作者把 Preesm 的 degridder piSDF graph 直接翻译到 IaRa，尽量复用相同 C/C++ actor kernel，并移除 Preesm 独有的 I/O actor affinity 约束以求公平。SKA 提供的三种数据规模为 3,924,480、7,848,960 和 31,395,840 个 visibility sample，实验只使用最大数据集，并改变 core count 与把图像拆成 actor chunk 的 granularity（PDF 物理页 8，Section VI-A/B）[pdf:E21]。Fig. 8 把各 core/chunk 组合的 compilation、binary、BSS、RSS 与 execution 结果放在同一张图中（PDF 物理页 9，Fig. 8）[pdf:E22]。测试机是 Intel Core Ultra 5 125H、64 GB RAM，实验限制在前 8 个 hardware thread，并测量 schedule compilation wall time、binary size、maximum RSS、execution wall time 以及 Preesm 展开图的 node/edge 数（PDF 物理页 9，实验参数）[pdf:E23]。**答案：**只统计到 128 chunks 的成功实例，IaRa 的调度编译平均快 12.2 倍；IaRa 编译不超过 1.5 秒，而 Preesm 在 256、512、1024 chunks 上无法在 5 分钟 timeout 内完成（PDF 物理页 9，Section VII-A）[pdf:E23]。

**问题：把调度移到 runtime 后，执行代价是否仍在可接受量级？ → 实验：**在相同 degridder kernel 和不同 core/chunk 组合上比较 execution wall time。**答案：**IaRa 全部实例平均 slowdown 为 1.43 倍；按 core count 分别为 1 core 1.03、2 cores 0.96、4 cores 1.63、6 cores 1.77、8 cores 1.61。作者认为 core 数增大与 runtime overhead 有明显相关性，并把 2-core 无 slowdown 暂时解释为两个 hardware thread 位于同一 physical core、降低 context switching 影响，但这只是作者提出的解释，没有独立实验隔离该机制（PDF 物理页 10，Table I 与邻近正文）[pdf:E24]。

**问题：动态 allocation 是否改善内存可用性与 binary scale？ → 实验：**Fig. 8 同时画出编译时间、binary、BSS、maximum RSS 和执行时间；红色柱表示 Preesm 因可用内存不足而无法启动，橙色柱表示 IaRa 在运行中被 OS 因 OOM 终止（PDF 物理页 9，Fig. 8 与 caption）[pdf:E22]。**答案：**从 256 chunks 起，Preesm 试图预留超过系统容量的 static memory，程序无法启动；IaRa 可以先启动、按需申请，直到真实使用耗尽内存才被终止。对成功实例，两者 maximum RSS 几乎相同，IaRa 仅报告 1.007 倍更小；作者把差异主要归因于 binary size，并明确承认高 granularity 下异常增长与两边都不充分的 copy elision、以及 scheduler 未考虑系统可用内存有关（PDF 物理页 10，Section VII-C）[pdf:E25]。IaRa 最终 binary 平均小 4.4 倍，且基本不随图参数变化；Preesm 的 scheduler object 则随展开图增长（PDF 物理页 10，Section VII-D）[pdf:E26]。

**实验结论的边界。**这些结果支持“在一个大规模、streaming、actor 较粗的 degridder workload 上，编译与 binary 的尺度收益可以用同量级的运行时间代价换取”，但不能直接外推到任意 SDF、hard real-time、FPGA、细粒度 actor 或 NUMA/多机系统。正文还说 IaRa 实现同时测 virtual FIFO 与 ring-buffer scheduler，但 Fig. 8 的 legend 只区分 Preesm 与 IaRa，没有给出 virtual FIFO、keyed semaphore、malloc、OpenMP 和 concurrent map 的独立 ablation；因此结果验证了**整个原型栈**，尚未单独量化每个新机制的贡献（PDF 物理页 8，IaRa implementation；物理页 9，Fig. 8）[pdf:E21][pdf:E22]。

## § 8 — Take-aways

**5 句话：**

1. static SDF 的低运行时开销来自提前物化 firing、处理器和内存决策，但这也会让编译产物随 single-rate expansion 增长（PDF 物理页 4，Section IV-A）[pdf:E07]。
2. quasi-dynamic 的本质是保留 rate、delay 与拓扑，把 firing 实例化、线程选择和物理地址选择推迟到 runtime（PDF 物理页 5，Section V）[pdf:E11]。
3. virtual FIFO 用 block、slice 和 virtual offset 把逻辑 FIFO 次序从连续 ring-buffer layout 中解耦，从而允许同一 actor 的 firing 乱序并行（PDF 物理页 5，Section V-A）[pdf:E12][pdf:E13]。
4. keyed semaphore 只保存当前活跃 firing 的依赖计数与 slice list，而不是把整个展开图的同步对象永久写进 binary（PDF 物理页 8，Section V-B）[pdf:E19]。
5. degridder 结果显示平均 12.2 倍编译加速和 4.4 倍更小 binary 的同时，执行平均慢 1.43 倍，但证据仍局限于单一应用和未优化 CPU runtime（PDF 物理页 9–10，Results）[pdf:E23][pdf:E24][pdf:E26]。

**3 句话：**

1. 论文证明了 SDF 的静态信息不必等同于完整静态 schedule，它也可以被压缩成运行期依赖与内存重建规则。
2. 这种表示把 compile-time scalability 明显改善，但代价是 malloc、hash-map synchronization、task scheduling 和较差 locality 进入执行路径。
3. 当前证据足以证明这条 trade-off 存在，不足以证明它已经优于所有 compact static scheduler 或适用于细粒度与实时场景。

**1 句话：**

这篇论文最重要的贡献，是把 SDF 编译器的讨论从“静态还是动态”改写成“哪些信息必须静态、哪些实例可以按需物化”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**单个 actor firing 的有效工作足够粗，能够摊薄每次 firing 的 heap allocation、slice bookkeeping、并发 hash lookup、锁竞争和非连续内存访问。**如果这一点不成立，quasi-dynamic 的编译与 binary 优势仍可能存在，但论文最关键的实践主张——“只付出有限 latency overhead 就能换取可扩展编译”——会直接失效。

作者其实明确给出了警告：virtual FIFO 通过牺牲 ring buffer 的 memory locality 获得更高调度自由；在 PE 数较少、图高度规则且 actor 很细时，连续的大 ring buffer 更有利于 prefetch，virtual FIFO 更适合 coarse-grained graph 或 memory-constrained application（PDF 物理页 5，Section V 开头）[pdf:E12]。当前实现又使用通用 `malloc`、OpenMP Tasks 和 off-the-shelf concurrent map，而非 SDF 专用 allocator 或 task runtime（PDF 物理页 8，Section V-C）。Table I 中 slowdown 从低 core count 的接近持平上升到 4–8 cores 的约 1.6–1.8 倍，也与同步和调度成本随并行度暴露的方向一致（PDF 物理页 10，Table I）[pdf:E24]。

论文缺少的关键证据是 actor granularity sweep：没有逐步缩短 kernel、固定图结构后测 crossover point，也没有 hardware counter、allocator time、hash contention、cache miss 或 memory bandwidth 分解。degridder 的 convolution/Fourier 类 kernel 天然较重，因而可能恰好处于最有利于摊薄 runtime 的区域。基于证据的判断是：只要 workload 转向大量亚任务式、内存访问规则且计算很少的 actor，virtual FIFO 的散布访问和 keyed semaphore 的逐 firing 状态就可能比被它替代的静态展开更昂贵。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 radio astronomy pipeline，而是论文的核心 trade-off：**编译与 binary 是否不再随 firing 展开增长，以及 runtime overhead 是否会随 actor granularity 被摊薄。**

使用论文 Fig. 4 的 `P:3 → Q:2` multi-rate graph 作为最小数据流骨架，并把同一结构按论文 Fig. 8 的 chunk 范围重复放大；core count 采用论文实际报告的 1、2、4、6、8 组（PDF 物理页 6，Fig. 4；物理页 9，Fig. 8；物理页 10，Table I）[pdf:E14][pdf:E22][pdf:E24]。actor 对固定输入数组执行可调工作量，从近似 pass-through 连续增加到足以主导运行时间的计算 kernel；每个版本都输出 checksum，以确认 static 与 quasi-dynamic 的 token 语义一致。

实现两条路径：一条把 firing 展开并生成静态 schedule，另一条使用 block/slice、virtual offset 和 keyed dependency counter；两条路径共用 actor kernel、编译器优化等级和输入。测量 schedule generation time、scheduler object size、execution wall time、maximum RSS，并额外记录 allocation 次数、同步时间与 cache miss，以解释 crossover，而不只报告总时间。

支持论文 claim 的结果应同时满足：随着 chunk 增大，静态路径的编译时间与 scheduler size 明显增长，quasi-dynamic 路径近似平坦；随着 actor 变粗，quasi-dynamic 的执行 slowdown 收敛到与静态路径同一量级。反驳 claim 的结果是：即使 actor 已足够粗，quasi-dynamic 仍被同步、allocation 或 locality 系统性拖慢，或者其 memory footprint 随 chunk 增长得与静态方案同样严重。这个实验比完整复现 degridder 更容易定位“表示尺度收益”和“逐 firing runtime 成本”各自来自哪里。

## § 11 — 最强反例设计

最强反例不是再找一个更细粒度 workload，而是构造一个**compact static scheduler（紧凑静态调度器）**，检验论文观察到的收益究竟来自“必须运行期调度”，还是仅来自“Preesm 把 single-rate firing 逐个展开并写进代码”的实现选择。

具体做法是继续使用论文相同的 degridder graph、kernel、core/chunk sweep 和内存上限，但新增一个静态基线：它在编译期求出周期 schedule 与 memory plan，却用 counted loop、层次化 actor cluster 或压缩的 repetition pattern 表示重复 firing，不为每个 firing 生成独立节点、代码和静态同步对象。论文自己承认 compact graph representation 与 actor clustering 是缓解静态调度复杂度的持续研究方向（PDF 物理页 4，Section IV-A）[pdf:E07]。

然后比较 Preesm、quasi-dynamic IaRa 和 compact static baseline 的 schedule compilation time、scheduler object size、execution time 与 RSS。若 compact static baseline 的编译和 binary 已接近 IaRa，同时保留 Preesm 式的连续内存与低 runtime overhead，那么最强替代解释成立：Fig. 8 主要暴露的是**unrolled static representation 的问题**，并不能证明 runtime dependency reconstruction 是获得尺度收益的必要机制。只有当 compact static 在同样不展开 firing 的前提下仍无法处理多速率依赖、动态 allocation 或 memory pressure，而 virtual FIFO 可以，论文的因果主张才真正站稳。

这个反例有杀伤力，因为它不否认论文数据，而是改变数据的解释：12.2 倍编译收益和 4.4 倍 binary 收益可能来自“压缩 schedule 表示”，而非“把 schedule 搬到 runtime”（PDF 物理页 9–10，Compilation 与 Binary results）[pdf:E23][pdf:E26]。

## § 12 — Follow-up Research Bet

**主押注：把 scalar virtual offset 扩展成 multi-dimensional rate lattice（多维速率格），让调度对象从单个 firing 变成可跨 actor 对齐的 tensor tile region。**这是候选判断；本任务未检索包外全文，因此不声称 novelty。

**新的研究问题。**能否用同一个多维整数坐标系同时表达 SDF 的 token rate/delay、tensor 的空间索引和 block 的物理 tile，使编译器既不做 firing 级 single-rate expansion，也不在 runtime 为每个细粒度 firing 单独建立 hash entry？论文已经指出静态展开会丢失规则 tensor computation 的对称性（PDF 物理页 4，Section IV-A）[pdf:E07]，而现有 virtual FIFO 只给 slice 一个一维 sequence offset（PDF 物理页 5，Section V-A）[pdf:E13]；这两点共同暴露了一个尚未开发的表示自由度。

**首次可能实现的能力。**编译器可以把一组具有 affine access（仿射访问）的 actor firing 合并成跨 actor 的 tile pipeline：同一个 tile 在 producer、in-place transform、consumer 之间保持可证明的边界对应，同时允许 tile 级 out-of-order、actor fusion、zero-copy reuse，以及面向 CPU cache、GPU memory 或 FPGA on-chip buffer 的联合映射。它不是给 keyed semaphore 再加一个优化模块，而是把系统的基本计算对象从“标量 firing 序号”改成“多维 token region”。

**核心机制与因果链。**首先，把论文 Eq. 1 的一维 rate/delay 对齐推广成多维整数格上的 region alignment；其次，block 不再只是长度固定的一维 token 段，而是带 shape、stride、port mapping 和逻辑坐标的 tile；再次，依赖状态按 tile region 聚合，只有 region 的所有输入覆盖完成时才提交 tile task；最后，后端联合选择 tile shape、actor grouping、memory placement 与 device mapping。论文已经证明 rate/delay 可转成整数可满足性约束，并提到 Hermite normal form 作为更高效的整数工具（PDF 物理页 7，Eq. 1 后正文）[pdf:E17]，因此这条路线有明确的数学起点。

**被改变的基本设计变量。**状态表示从一维 offset 变成多维 region；时间粒度从 firing 变成 tile wave；可控变量新增 tile shape、跨 actor fusion boundary 和 device placement；系统边界从 shared-memory CPU scheduler 扩展到 compiler–runtime–heterogeneous memory 的共同优化；评价对象也从单纯 wall time/binary size 扩展到跨 actor copy、memory traffic 和 on-chip reuse。

**全文中的具体依据。**方法侧，virtual FIFO 已经证明逻辑 token 次序可以脱离物理地址，Eq. 1 又把 zero-copy boundary 归结为整数对齐（PDF 物理页 6–7，Fig. 5、Eq. 1）[pdf:E16][pdf:E17]。实验侧，Fig. 8 同时显示了不展开 schedule 带来的编译/binary 优势，以及高 granularity 下 memory 问题和多核 runtime overhead；结论还明确把 problematic high-granularity case 与 polyhedral compilation 列为后续方向（PDF 物理页 9，Fig. 8；物理页 10，Conclusion）[pdf:E22][pdf:E25][pdf:E26]。多维 rate lattice 正好把“保留 dataflow 语义”和“恢复 affine regularity”变成同一个表示问题，而不只是把高 granularity case 外包给另一个工具。

**最大研究收益与最大科学风险。**最大收益是形成一种统一的 dataflow–polyhedral IR：同一套整数 region 关系可驱动编译规模、内存复用、并行粒度和 heterogeneous mapping，可能同时减少 static expansion 与 per-firing runtime 状态。最大风险是 SDF actor 常被视为 black box；若 actor 不公开 affine access、存在数据依赖索引或复杂 side effect，多维 region 关系就无法建立，格求解和 tile state 本身也可能比现有 scalar virtual FIFO 更复杂。

**首个证伪实验。**在 degridder 的 chunked kernel 上，为输入 chunk index 与 kernel 内部规则数组维度建立多维 region，比较 scalar virtual FIFO、rate-lattice tile scheduler 和保持相同 tile size 的 blind batching。三者使用相同 actor code、相同并行度和相同 block 容量，测编译时间、scheduler size、wall time、RSS、跨 actor copy 与 memory traffic。若 rate-lattice 只在 batch 变大时获益，而在控制 batch size 后不再减少 copy 或同步状态，则最强替代解释“收益只是普通 batching”成立；若它在相同 batching 下仍能利用跨 actor 对齐降低数据移动并保持编译尺度，则核心机制得到支持。

**与本文所列近邻工作的实质区别。**Preesm/Spider 主要在 actor graph 与 schedule 层展开、重排或重配置；Taskgraph 重放已知 static DAG；本文的 virtual FIFO 仍以 scalar firing sequence 为依赖 key（PDF 物理页 3，Related Works；物理页 8，Keyed semaphore）[pdf:E08][pdf:E19]。候选方案则把 problem、representation 和 experimental object 都移到多维 token region：它要求跨 actor 的 index relation 成为一等 IR，而不是更快地重放 firing、给现有 runtime 加缓存，或在危险时回退到另一条路径。

**Wild-card alternative：**把 ephemeral virtual-FIFO block 改成 content-addressed、不可变且带 lineage 的 token segment，用于 streaming graph 的增量重算与可重复分支执行；这改变的是任务目标和数据生命周期，而不是 tile 几何与硬件映射。
