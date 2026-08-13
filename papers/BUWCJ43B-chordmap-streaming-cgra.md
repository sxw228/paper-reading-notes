# ChordMap: Automated Mapping of Streaming Applications Onto CGRA

作者：Zhaoying Li、Dhananjaya Wijerathne、Xianzhang Chen、Anuj Pathania、Tulika Mitra  
出处：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems, 41(2): 306–319  
年份：2022  
DOI：10.1109/TCAD.2021.3058313  
Zotero key：BUWCJ43B  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的是一个系统级映射问题：给定由 synchronous data flow（SDF）描述的完整 streaming application，以及计算单元和片上存储均受限的 coarse-grained reconfigurable array（CGRA），如何在编译期同时安排 actor、actor instance、空间区域和执行时间，使稳态吞吐最大，同时不让 token buffer 溢出。作者指出，已有 CGRA compiler 已能把单个 loop kernel 映射为每周期静态配置，但“多个相互通信的 kernel 如何共享一块 CGRA”仍缺少完整解法；论文摘要报告 ChordMap 在八个应用上相对当时 state-of-the-art 平均获得 1.74× 吞吐提升。[pdf:E01]（PDF 物理页 1，Abstract、Fig. 1、Introduction）

重要性不只在于“多放几个 kernel”。SDF 的 producer–consumer 关系同时规定执行先后和 token 数量；若只追求并行，片上 scratchpad memory（SPM）可能装不下中间 token，若只压低 buffer，又会把可并行的 actor instance 串行化。CGRA 的每周期重配置能力允许不同 actor 在同一批 processing element（PE）上沿时间维复用，这比 FPGA 风格的纯 spatial mapping 多出一个关键自由度，但也把数据就绪时间、峰值 buffer 和 memory-bank conflict 一并带进映射问题。[pdf:E02]（PDF 物理页 2，Fig. 2、Introduction 末段、Section II 开头）

## § 2 — 前人工作与不足

论文把相关方法分成三类。第一类是 SDF scheduling：已有工作能在 CPU 或 multicore 上寻找 bounded-buffer 或 throughput-maximal schedule，但主要处理时间顺序，不需要决定 actor 在二维 PE 阵列中的形状、位置和路由。第二类是 FPGA SDF mapper，例如 CMOST 和 FPGAConvNet：它们能提取、调度并在空间上复制 SDF actor，但频繁 partial reconfiguration 对 FPGA 代价很高，因此 actor 通常长期占据固定区域，难以利用 CGRA 的 per-cycle temporal multiplexing。第三类是 CGRA streaming mapper，例如 PPA/本文实现的 PPAM、MP-C 以及面向单 kernel 的 CGRA compiler：PPAM 用 task graph 划分 pipeline stage，却让同一 stage 的 task 采用相同 CGRA 尺寸；MP-C 同一时刻只在 CGRA 上运行一个 kernel；单-kernel mapper则没有系统级 SDF schedule。[pdf:E09]（PDF 物理页 9，Section V）

因此，论文声称的缺口并非“前人完全没有 SDF 或 CGRA 映射”，而是此前没有把以下三件事闭合在同一个静态 mapper 中：跨 actor 与跨 instance 的并行、actor version 的空间—时间权衡、以及有限多 bank SPM 下的 buffer 与访问冲突。这个缺口之所以此前难处理，是因为加入时间复用后，一个 actor 不再固定占据一个 region，schedule、占用体积和随时间变化的 token 峰值相互耦合；单独优化其中任意一个，都可能让另一个约束失效。[pdf:E02]（PDF 物理页 2，Fig. 2 后正文与作者贡献段）

## § 3 — 重建作者的思考路径

可以从论文给出的三 actor 例子逆向重建这条思路。SDF 中 A、B、C 每个 steady-state 分别调用 1、2、4 次，最小 buffer schedule 是 `A(BC²)²`，展开为 precedence graph 后，实线边表示数据依赖，虚线边表示为了限制 buffer 而补上的次序；这说明“schedule”可以统一承载依赖和存储约束。另一方面，同一个 actor 可有多个 `(X,Y,Z)` version：更多 PE 通常缩短占用时间，更少 PE 则拉长时间，这又把单 actor compiler 的输出变成可供系统 mapper 选择的离散设计空间。[pdf:E03]（PDF 物理页 3，Fig. 4、Fig. 5、Section II）

接着看纯 spatial mapping 的失败模式。对同一 4×4 CGRA，空间独占让 A、B、C 的阶段不平衡；若让 A 和 B 在同一 PE 区域上时间复用，释放的空间可给 instance 更多、计算量更大的 C，pipeline interval 可从 240 cycles 降到 160 cycles。加入 100-token buffer 约束后，两种映射都变慢，但 ChordMap 仍是 240 cycles，Spatial 为 280 cycles；若 buffer 增至 120 tokens，ChordMap 相对最小-buffer schedule 的吞吐提升为 50%，Spatial 只有 17%。[pdf:E04]（PDF 物理页 4，Fig. 6、Table I、Table II）

由此自然得到作者的分治路线：不要一次性联合搜索整张 SDF、全部 actor instance、全部 version 和整块 CGRA，而是把 CGRA 切成 sub-CGRA，把 SDF 切成执行时间尽量均衡的 sub-SDF；每个 sub-SDF 内寻找符合 buffer 的 schedule 和 spatio-temporal mapping，再把各 sub-SDF 作为 pipeline stage 拼接。若吞吐仍受某个 stage 限制，就继续拆分该 bottleneck 对应的区域，直到新增 partition 不再改善吞吐。[pdf:E05]（PDF 物理页 5，Fig. 7、Section IV-A）

## § 4 — 核心 Intuition

ChordMap 的核心直觉是：CGRA 的每周期重配置让“同一块 PE 在不同时间服务不同 actor”成为廉价操作，因此系统级吞吐不应由静态空间切片决定。它通过把 actor version 的空间—时间形状、SDF 的 token schedule 和 sub-CGRA pipeline 一起安排，用时间复用释放空间，再把空间投入真正的 bottleneck actor；buffer 约束不是映射后的补丁，而是构造 precedence graph 和 schedule 时就进入搜索。最终目标不是让每个 actor 单独最快，而是让各 pipeline stage 的稳态完成间隔尽量接近。

## § 5 — 具体方法与完整 Pipeline

输入是一张静态 SDF、目标 CGRA 的 PE 阵列与 banked SPM 容量，以及单-actor compiler 在不同 sub-CGRA 尺寸上生成的 actor versions；输出是一个可重复执行的 mapped SDF schedule。完整 pipeline 如下。

1. **建立 actor version 库。** 对每个 actor 的 CDFG，在 1×2、2×2、2×4 等不同尺寸的 sub-CGRA 上做 loop pipelining，记录空间尺寸、占用周期和 resource utilization。论文的系统 mapper消费这些版本，但不重新发明单-kernel mapping。
2. **迭代划分 CGRA。** 从两个等尺寸 sub-CGRA 开始；下一轮继续切分上一轮最大且对应 sub-SDF 最慢的区域。sub-CGRA 的长宽限制为 2 的幂，以控制组合数量，并要求所有块能无重叠重构原 CGRA。
3. **划分并均衡 SDF。** 用 DFS 尽量把依赖 actor 留在同一 partition，以 Eq. (1) 的粗略执行时间把 actor 分入各 sub-SDF；随后在相邻 sub-SDF 之间移动边界 actor，反复降低估计执行时间不平衡。Algorithm 1 的核心不是最优图划分证明，而是一个能在数十 actor 规模上运行的启发式。[pdf:E06]（PDF 物理页 6，Algorithm 1、Eq. (1)、Section IV-B）
4. **按 buffer 预算构造 sub-SDF schedule。** 先按各 sub-SDF 的最小 buffer 需求分配 SPM。从 maximum-buffer schedule 出发，用 repetition vector 的公因数逐级 factoring，例如把 `A⁴⁰B²⁰C¹⁰` 变为 `(A²⁰B¹⁰C⁵)²`，直至 schedule fits memory；若整组 repetition 无法继续约分，就对 maximal actor chain factoring；仍失败时回到 minimum-buffer schedule。未用满的 buffer 会重新分配给 bottleneck sub-SDF。[pdf:E07]（PDF 物理页 7，Algorithm 2、Section IV-C）
5. **做 memory-conflict-aware spatio-temporal mapping。** 将 schedule 展开为 instance precedence graph；对于每组 actor-version combination，维护 fire-able 与 waiting node set，按 ASAP 排序放置 actor instance。论文假定每个 memory bank 有两个 port：不同 channel 优先放不同 bank，互不同时访问的 channel 可共享 bank；同一 actor 同时启动的 instance 不超过两个，actor 内的 load 通过 modulo schedule 错开。搜索只取 resource utilization 最高的 1000 组 version combination。[pdf:E08]（PDF 物理页 8，Algorithm 3、Fig. 9、memory-conflict-aware mapping）
6. **拼接并继续拆 bottleneck。** 各 sub-SDF 在对应 sub-CGRA 上并行构成 pipeline。示例中两 stage 用时 8000/6000 cycles，新增 partition 后变为 5000/5500/6000 cycles，pipeline interval 从 8000 降到 6000 cycles；算法继续增加 partition，直到吞吐不再提高。[pdf:E09]（PDF 物理页 9，Section IV-D）

数值表示、配置存储容量、互连能耗、片外 DMA 与 steady-state 之间的启动/排空代价均未报告。论文把 CGRA RTL 在 40 nm 工艺上综合，但实验主体是 compiler/mapping evaluation，不是 FPGA 原型、芯片实测或实时 HIL。[pdf:E10]（PDF 物理页 10，Fig. 10、Section VI-A）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出全局最优性的形式化推导；核心数学对象是用于启发式 partition 的执行时间代理，以及搜索复杂度。

对 actor `v`，估计执行时间为

\[
ET(v)=\frac{o(v)\times RV}{X\times Y},
\]

其中 `o(v)` 是 actor 的 operation 数，`RV` 是该 actor 在一个 SDF recurrent schedule 中的 repetition value，`X×Y` 是对应 sub-CGRA 的 PE 数。工程直觉是“总工作量除以并行资源”；sub-SDF 的 `ET` 是其 actor 的 `ET` 之和，再用相邻节点交换去压低 stage 间差异。它隐含所有 PE 理想利用、依赖不增加空洞的假设，因此只是 partition guide，不是最终 cycle count。[pdf:E06]（PDF 物理页 6，Eq. (1) 与相邻变量定义）

Algorithm 1 的复杂度写为 `O(pn³)`：`n` 是 SDF actor 数，`p` 是 partition 优化迭代数。包含 schedule mapping 的 Algorithm 2 写为 `O(pnfm³)`：`m` 是 schedule 中 actor instance 总数，`f` 是 actor-version combination 数；实际实现令 `f=1000`，buffer 重分配通常少于十轮，因此单轮 ChordMap 总复杂度为 `O(pn³)+O(pnfm³)`。[pdf:E08]（PDF 物理页 8，Algorithm 2 complexity）[pdf:E09]（PDF 物理页 9，Section IV-C 末段）

这套数学的作用是解释搜索为什么可做，而不是证明结果最优。论文后来明确指出 Eq. (1) 不含 data dependency，最终 mapping 才会体现依赖与真实 utilization；因此 estimated ET 与 final execution time 可能偏离，图划分也可能错过最佳 partition。[pdf:E13]（PDF 物理页 13，Fig. 15 后续分析）

## § 7 — 实验设计与结论

实验覆盖八个 streaming applications：CNN、CNN2、FFT-128、FFT-256、Filterbank、MatrixMultBlock、MPEG-2、TDE_PP；前两者按文中方法构造，其余来自 StreamIt。规模从 7 到 27 个 actor，minimum buffer 从 1.10 KB 到 22.75 KB，maximum buffer 从 1.34 KB 到 196.88 KB。作者排除了含 input-dependent while loop 或 actor feedback loop 的应用，因为其执行时间无法静态估计或不受当前 mapper 支持。[pdf:E10]（PDF 物理页 10，Table III、Section VI-A）

- **问题：有限 SPM 下，时间复用与 memory-aware scheduling 是否仍有收益？** 实验比较 8×8 CGRA/16 KB SPM 与 16×8 CGRA/32 KB SPM，并以 PPAM、MP-C、CMOST 为基线。8×8 上 ChordMap 相对三者平均提升 2.96×、3.29×、2.21×；16×8 上为 4.73×、7.89×、1.65×。但 TDE_PP 的 minimum buffer 已是 22.75 KB，在受限 SPM 下相对 PPAM 仅 1.11×；FFT-256 在 8×8 上也是例外。[pdf:E11]（PDF 物理页 11，Fig. 11、Section VI-B）
- **问题：收益是否只来自特定 buffer 容量？** 在假定无限片上 buffer 的 8×8、16×8、16×16 CGRA 上，ChordMap 同尺寸平均相对 PPAM、MP-C、CMOST 提升 4.4×、6.35×、1.62×；8×8 单独是 3.48×、4.41×、1.97×。把每个 benchmark 的 SPM 设为其 Min-Buffer 与 Max-Buffer 平均值时，提升仍为 2.73×、2.76×、1.70×。[pdf:E12]（PDF 物理页 12，Fig. 12、Fig. 13）
- **问题：分区是否真的改善 stage balance？** 16×8 上，actor execution time 的 relative standard deviation（RSD）从 CMOST 的 41.8% 降为 ChordMap 的 18.2%，支持“partition + temporal multiplexing 能降低不平衡”的解释。但 estimated ET 与 final ET 并非总一致；Filterbank 和 MMB 的最终 RSD 约为估计值一半，说明代理模型会高估不平衡。[pdf:E12]（PDF 物理页 12，Fig. 14、Fig. 15）
- **问题：编译代价是否可接受？** ChordMap 明显慢于三条基线；除 TDE_PP 外，多数映射在数百秒内，TDE_PP 接近图中更高数量级。作者据此判断静态编译开销可接受，并报告运行时不增加额外开销，但没有报告 mapper 能耗、配置存储开销或真实芯片端到端功耗。[pdf:E13]（PDF 物理页 13，Fig. 16、Conclusion）

论文结论中汇总的跨实验平均值为：相对 CMOST、MP-C、PPAM 分别 1.74×、5.49×、3.94×。这些数字支持“在所测静态、无反馈 SDF 与该 CGRA/SPM 模型下，联合时空映射优于三条实现基线”，不能外推为任意 streaming graph、任意互连规模或动态 workload 上都同样获益。[pdf:E13]（PDF 物理页 13，Conclusion）

## § 8 — Take-aways

**5 句话：** ChordMap 把完整 streaming application 而非单个 kernel 作为 CGRA mapping 对象。它利用 per-cycle reconfiguration，让不同 actor 沿时间复用同一 PE 区域，同时把释放的空间给真正的 bottleneck。它把 SDF 的 dependency、buffer-bound schedule、actor version 和 memory-bank conflict 放进同一编译期 pipeline。实验表明，收益主要来自更均衡的 stage 与多层并行，而不是单纯放大 CGRA。代价是启发式搜索更慢，且适用范围依赖静态可估计、无 actor feedback 的 SDF。

**3 句话：** 论文最重要的观念变化，是把 CGRA 从“单 kernel loop accelerator”看成可被多个 actor 在三维时空中共享的 pipeline fabric。SDF schedule 不只是执行顺序，也是控制 token buffer 与 instance parallelism 的设计变量。ChordMap 的证据显示该组合在八个 benchmark 上有效，但还没有证明对动态执行时间、超大互连和真实芯片资源同样成立。

**1 句话：** 用 buffer-aware 的 SDF schedule 驱动 CGRA 时空复用，可以把原本因静态空间切片浪费的 PE 重新转化为稳态吞吐。

## § 9 — 最脆弱的假设

最脆弱的假设是：每个 actor 的执行次数和执行成本能够在编译期稳定估计，从而一个静态 precedence graph、buffer schedule 与 spatio-temporal placement 可以在所有 steady-state iteration 中重复使用。它一旦失效，影响的不只是 partition 质量；actor 可能错过预定 slot，token 峰值不再等于编译期估计，原本可并行的 memory access 也可能同时发生，因而核心的“离线一次映射、运行时无额外调度”闭环会一起失效。

论文提供的支持是：选用的 SDF benchmark 有固定 repetition，单 actor loop 由 compiler 生成静态 modulo schedule，并在最终 mapping 中再处理 dependency 与 bank conflict。论文也直接暴露了证据缺口：input-dependent while loop 与 actor feedback loop 不受支持；Eq. (1) 只按 operation count、repetition 与 PE 数估时，不含 data dependency，最终 ET 可能偏离。[pdf:E10]（PDF 物理页 10，Section VI-A 的 benchmark 排除条件）[pdf:E13]（PDF 物理页 13，estimated/final ET 分析）因此，这是基于证据的批评，不是论文已证明会失败的结论；在当前实验覆盖外，执行时间抖动多大才会破坏 schedule，论文没有给边界。

## § 10 — 最小复现实验

一周内不复现完整 LLVM 与 CGRA compiler，而是复现 Fig. 6 的三 actor 闭环。输入直接采用论文的 A/B/C operation count、1/2/4 repetition、Table I actor versions，以及两类 SDF schedule；实现一个离散 event simulator，枚举 4×4 PE 上的 spatial-only 与允许 actor time multiplexing 的 placement，并显式统计 pipeline interval、各 edge token 峰值和最多双 port memory access。论文给出的目标点是：无 buffer 约束时 Spatial 为 240 cycles、ChordMap 为 160 cycles；100-token 约束时分别为 280 与 240 cycles。[pdf:E04]（PDF 物理页 4，Fig. 6、Table I、Table II）

支持核心 claim 的判据是：在同样的 4×4 PE、相同 actor version 与相同 token accounting 下，允许时间复用的最优解稳定复现上述两个 interval 改善，而且禁用 time multiplexing 后收益消失。反驳判据是：只有放宽 buffer、忽略 precedence 或额外增加 PE 才能得到 160/240 cycles，或严格 token accounting 后 ChordMap 的结果不优于 Spatial。这个实验只验证“时间复用 + buffer-aware schedule 能改善 toy SDF 的稳态 interval”，不声称复现八 benchmark 平均值。

## § 11 — 最强反例设计

最强反例应留在论文声称支持的静态、无反馈 SDF 内，而不是用被明确排除的 while loop。构造一组 acyclic multi-rate SDF：actor 的 operation count 与实际 critical-path latency 刻意反相关；多个可同时 fire 的 actor 都在相同周期访问少数两端口 bank；每个 actor 还拥有“高 utilization 但持续时间长”和“低 utilization 但能与邻居互补”的两类 version。这样同时攻击 Eq. (1) 的排序、top-1000 high-utilization combination 截断，以及“最多两个同 actor instance 并行”下的 memory-conflict placement。[pdf:E08]（PDF 物理页 8，Algorithm 3、bank-port 与 top-1000 规则）

在相同 PE、SPM、bank 和 compile-time budget 下，比较 ChordMap、完整 version oracle 与一个不做 partition 的联合 schedule。若 oracle 能找到显著更短的 pipeline interval，而 ChordMap 因估时错误反复拆错 bottleneck，或因 utilization 排序丢掉互补 version，最终不优于 CMOST-style spatial mapping，那么结果会直接推翻“当前启发式能够可靠地把时空自由度转化为高吞吐”这一机制性解释。若三者差距很小，则说明论文的收益并不依赖脆弱的代理排序，反例失败。

## § 12 — Follow-up Research Bet

**主 idea：相位标记的多图 SDF 合成，让一块 CGRA 同时执行多个独立 streaming application。** 新问题不再是“怎样把一张 SDF 映射得最快”，而是“能否把多张 SDF 合成为一个带 application phase tag 的 product graph，使不同应用的 actor version 在三维时空中互补占位，并给出确定性的联合稳态吞吐”。这首次可能让同一 CGRA 在不把应用永久切成固定 spatial slice、也不轮流整图 context switch 的前提下，形成可静态验证的 multi-tenant streaming fabric。

核心机制的因果链是：actor version 已经提供不同的 `(X,Y,Z)` 形状 → ChordMap 已证明不同 actor 可在同一区域时间复用，并通过 sub-SDF pipeline 平衡 stage → 将独立 SDF 的 repetition phase 显式编码进 product graph 后，mapper 可把一个应用的空间空洞与另一个应用的时间空洞配对 → bank address permutation 再把相位错开的 channel 分散到不同 port → 结果不只是提高单图的鲁棒性，而是新增“多个 streaming graph 确定性并发”的系统能力。论文中特异依据包括 Fig. 7 的 actor-version/partition/schedule 联合 pipeline，以及 Fig. 6 中 240→160 cycles 的时间复用收益；实验上，资源从 8×8 增至 16×8 时 ChordMap 吞吐接近翻倍，且 stage RSD 由 CMOST 的 41.8% 降至 18.2%，说明互补占位与均衡有可开发空间。[pdf:E05]（PDF 物理页 5，Fig. 7）[pdf:E04]（PDF 物理页 4，Fig. 6、Table II）[pdf:E12]（PDF 物理页 12，Fig. 12、Fig. 14）

这个方向改变了问题定义（单图最大吞吐变为多图联合吞吐与隔离）、状态表示（普通 SDF 变为 phase-tagged product SDF）、系统边界（单应用 CGRA 变为 multi-tenant CGRA）以及硬件映射变量（bank address phase 与跨图 actor-version packing）。最大收益是把目前依靠固定 partition 或粗粒度 context switch 的多应用执行变成细粒度、静态可重复的联合 pipeline；最大科学风险是跨图合成后的 repetition vector 与 buffer state 乘积爆炸，搜索复杂度增长可能吞噬所有互补收益。由于本卡没有联网检索，这一方向仅是候选判断，不声称 novelty。

首个证伪实验选择两张 actor-version shape 明显互补的 paper benchmark SDF，在相同总 PE、SPM、bank-port 与每应用输入率下，对比三种方案：固定 spatial slice、整图 round-robin、phase-tagged product mapping。只有当 product mapping 在不降低任何一个应用 token conservation 的前提下，提高 harmonic-mean throughput，且把应用标签随机打乱后收益显著消失，才能把收益归因于跨图相位互补，而不是更宽松的资源预算或 benchmark 偶然性。

**Wild-card alternative：** 把 banked SPM 改造成支持 token multicast/combining 的可编程 memory-centric dataflow fabric，使 multi-rate edge 不必逐 token 物化后再由 PE 搬运；这改变的是物理通信拓扑与 token 生成方式，而不是多图相位表示。
