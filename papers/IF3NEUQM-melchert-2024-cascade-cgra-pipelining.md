# Cascade: An Application Pipelining Toolkit for Coarse-Grained Reconfigurable Arrays

- 作者：Jackson Melchert、Yuchen Mei、Kalhan Koul、Qiaoyi Liu、Mark Horowitz、Priyanka Raina
- 出处：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems，Vol. 43，No. 10，pp. 3055–3067
- 年份：2024
- DOI：10.1109/TCAD.2024.3390542
- Zotero key：IF3NEUQM
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“怎样给 CGRA 多塞一些寄存器”，而是一个编译闭环问题：在可编程互连延迟占比很高的 coarse-grained reconfigurable array（CGRA）上，怎样让编译器根据真实 placement and routing（PnR）后的路径延迟插入流水级，同时不让 scheduling、mapping、PnR 和 pipelining 彼此反复推翻。作者指出，现有流程要么没有 application pipelining，得到低频实现；要么在每个互连 hop 上穷举式流水化，付出高功耗和高资源成本；把所有决策耦合成一次优化又会扩大搜索空间、降低可扩展性。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，是因为本文目标 CGRA 的逻辑功能并不自动决定运行频率：同一颗芯片上，具体应用的已布线组合路径才决定 maximum frequency。本文面向大规模 tile array、任意 tile 到任意 tile 的 single-cycle multihop 静态互连，以及每个 switch box hop 上可配置的 pipeline register；在这类结构中，PE、MEM 和长互连共同构成关键路径。[pdf:E02]（PDF 物理页 2，Section II-A 与 Fig. 1）如果不能把真实 hop delay 纳入编译，CGRA 的可编程性就会以低频为代价；如果全部 hop 都流水化，又会以寄存器、FIFO 和功耗为代价。Cascade 的工程价值在于寻找“只在需要的位置增加时序边界”的中间路线。

论文直接声称的结果是：相对无流水编译器，dense workloads 的 critical-path delay 降低 8–34 倍、EDP 降低 7–190 倍；sparse workloads 的 critical-path delay 降低 3–5.2 倍、EDP 降低 2.5–5.2 倍。[pdf:E01]（PDF 物理页 1，Abstract）这些数字表明该问题不只是编译时间优化，而是同时影响吞吐、能耗和 CGRA 架构是否有竞争力。

## § 2 — 前人工作与不足

相关文献中的已有结论，以下均按本文的综述和复现实验陈述，而不是本卡独立检索后的判断。FPGA/ASIC 已有 register retiming、post-placement retiming 和 interconnect register 等技术；常见的分阶段 compiler 为了避免“插入寄存器→schedule 改变→PnR 改变→再次插入”的不收敛循环，通常不会在 PnR 后改变流水决策，只使用粗略 wire-load estimate。作者认为，这保住了编译可解性，却不能准确利用应用已经落位布线后的 hop delay。[pdf:E03]（PDF 物理页 3，Section III 开头）

CGRA 路线则分成几类。EPImap、DRESC 等面向 neighbor 或 row/column connection，并采用 exhaustive pipelining；Sara/Plasticine 支持 any-tile-to-any-tile，但依赖每 hop FIFO；HyCUBE 支持 single-cycle multihop 和 configurable register，却只在 16-tile 阵列上评估，通过限制单周期 hop 数控制路径。本文的 Table III 将 Cascade 放在 any-tile-to-any-tile、configurable registers、512 tiles、450–1000 MHz 的位置。[pdf:E11]（PDF 物理页 11，Table III 与 Section VII-C）论文给出的不足不是笼统的“旧方法没考虑互连”，而是：连接受限的架构难以容纳大规模高扇出图；exhaustive pipelining 使 branch delay matching 和功耗代价变大；小阵列上的 hop-limit 方案不能直接扩展到 32×16 阵列。

Cascade 直接继承 AHA 的 staged flow。该已有流程已经把应用编译成 primitive-operation dataflow graph，再依次完成 compute mapping、static scheduling/MEM mapping、PnR 和 bitstream generation；已有工作能做 wire-independent pipelining，但不能根据最终 route 的真实延迟选择寄存器位置。[pdf:E02]（PDF 物理页 2，Section II-B–C）因此本文真正补的空位是：在不改变 mapped topology 和 PnR result 的条件下，做 post-PnR timing analysis、selective register/FIFO insertion、branch delay matching 与 incremental rescheduling。

## § 3 — 重建作者的思考路径

下面是基于论文背景的合理重建，不是作者逐字陈述。第一步，先接受 staged compiler 的现实约束：mapping、schedule 和 PnR 一旦反复联动，搜索会变慢甚至不收敛，因此应保留已完成的 topology 与 route。第二步，从传统 static timing analysis（STA）出发，在最终 dataflow/PnR graph 上找出真正的 critical path；既然目标 switch box 的现有 route 上有可配置寄存器，就只打开路径中已有但未启用的 register，以避免重新 PnR。[pdf:E03]（PDF 物理页 3，Eq. (1)、Section III-A 与 Fig. 2）

第三步，插入一个流水级会把某一支的数据推迟一拍，功能正确性问题便从“几何布线”转化成“各输入到达周期是否一致”。于是作者用类似 STA 的遍历做 branch delay matching：这里累计的不是纳秒 delay，而是每个节点产生输出所需的 cycle 数；同一 functional element 若收到多个不同 arrival cycle，就在较快支路补寄存器。[pdf:E03]（PDF 物理页 3，Fig. 2 右侧正文）第四步，静态 schedule 的剩余变化尽量只落到 MEM tile 的 address/schedule enable generator 中，以更新 delay register 和 starting cycle，不改变 mapped graph；global flush 晚一拍时，相应 memory address generator 提前一拍启动。[pdf:E04]（PDF 物理页 4，Section III-B）

第五步，branch matching 会在非关键支路制造大量寄存器，因此再把这些“时间延迟”从互连物理寄存器搬进可调度的 MEM tile，或把长 register chain 折叠进 PE tile 的 register file 作为 variable-length shift register。作者还把 reduction kernel 偏向 unbalanced operation chain，使产生的寄存器链更容易吸收；实验采用的 chain 阈值为 N = 10。[pdf:E04]（PDF 物理页 4，Section IV 与 Figs. 3–4）最终，问题从一个巨大的联合优化被拆成：先得到可用 PnR，再通过 STA 定位、局部插入、周期平衡和端点重排，迭代缩短关键路径。

## § 4 — 核心 Intuition

Cascade 的核心 intuition 是：PnR 后才知道真实长线在哪里，但知道以后不必重做 PnR；只要保持 graph topology 与 route 不变，就可以把关键路径上的可配置互连寄存器打开，再把新增周期差异吸收到其他支路和 MEM schedule 中。[pdf:E03]（PDF 物理页 3，Section III-A）换句话说，它把“改变空间结构”与“修正时间对齐”分开：空间路径冻结，时间边界局部移动。register absorption 又把非关键支路上的物理 register cost 转换为 memory starting-cycle offset 或 register-file shift，从而保留频率收益、减少互连资源。[pdf:E04]（PDF 物理页 4，Section IV）

## § 5 — 具体方法与完整 Pipeline

以一个含 multiply-add kernel、多个 MEM source 和高扇出 flush 的 dense image pipeline 为例，完整流程如下。

1. **输入与初始表示。** 输入是 application specification 与 CGRA specification。前端把程序转成 primitive operations 的 dataflow graph；compute mapper 把 kernel 映射成 PE/register DAG，scheduler 与 MEM mapper 再生成包含 PE、MEM、IO 和 register 的完整 mapped graph。静态 schedule 为每个 statement 的 iteration-domain instance 分配一维 cycle timestamp，使数据搬运与计算重叠。[pdf:E02]（PDF 物理页 2，Sections II-B–C）
2. **硬件 timing model。** Canal interconnect specification 枚举 PE/MEM tile 内显著 data/clock path 的起止点；商业 ASIC STA 工具在带 parasitic delay 的 post-layout netlist 上提取 worst-case delay。模型显式区分 PE core、MEM core、不同方向与 tile 类型的 hop delay，并考虑 clock skew。[pdf:E05]（PDF 物理页 5，Section V-A 与 Fig. 5）
3. **compute 与 broadcast pipelining。** compute mapper 打开每个 PE input 的可用寄存器并做 branch delay matching。目标 PE 最大 delay 为 0.8 ns，switch box 单 hop 约 0.14 ns，因此 PE 全流水后，超过约五个 hop 的 route 会接管 critical path。对一源多目的 broadcast，Cascade 把蛇形长组合路径改成多级树状流水路径，并允许用 tree level、register budget 等参数权衡资源与路径长度。[pdf:E05]（PDF 物理页 5，Section V-C1）[pdf:E06]（PDF 物理页 6，Section V-C2 与 Fig. 7）
4. **timing-aware placement and routing。** global placement 先最小化 HPWL；detailed placement 用 simulated annealing，并把每条 net 的成本改成 `HPWL^α`，使长 route 受到更强惩罚。论文实验对 α = 1…30 逐值执行 PnR，选择最高频结果；routing 沿用基础流程。[pdf:E06]（PDF 物理页 6，Section V-C3 与 Eq. (2)）
5. **post-PnR selective pipelining。** application STA 在最终 PnR graph 上计算 arrival time 并回溯 critical path。编译器只在现有 route 上打开未启用的 switch-box register，切断当前最长组合路径；随后按 cycle arrival 做 branch delay matching。该过程迭代到没有可切断路径或达到 target frequency，不改变 mapped topology，也不重新 PnR。[pdf:E03]（PDF 物理页 3，Section III-A 与 Fig. 2）
6. **incremental rescheduling 与 register absorption。** 新的 compute latency 回传 scheduler，只改 MEM controller 的 address/schedule delay 与 global-flush 对齐。非关键支路上的 register 优先由 MEM output 延后吸收；长链则用 register file 的同地址错周期读写实现 variable-length shift register。[pdf:E04]（PDF 物理页 4，Section III-B、Section IV、Figs. 3–4）
7. **其他缩放机制与输出。** low-unrolling duplication 先在较小阵列区域对低 unrolling kernel 做 PnR，再把相同 tile/interconnect configuration 复制到全阵列；超大 flush broadcast 则可从 configurable interconnect 移出，做成逐列分发且在固定 row 插寄存器的 hardened signal。最终生成 CGRA bitstream；Fig. 6 标出了 Cascade 新增或修改的 stages。[pdf:E06]（PDF 物理页 6，Fig. 6、Sections V-C4–5）[pdf:E07]（PDF 物理页 7，Fig. 8）
8. **sparse application 分支。** data-dependent memory access 使用 ready-valid interface。若只给 data path 加 register，会破坏单周期 handshake；因此 data、ready、valid 三条相关路径不能独立处理，Cascade 用 interconnect FIFO 共同切断它们。除 placement-cost optimization 和 low-unrolling duplication 外，需要插寄存器的 passes 在 sparse 情形改为插 FIFO。[pdf:E07]（PDF 物理页 7，Section V-D）

这里的“hazard”不是处理器教材中的 RAW/WAR/WAW 分类。本文真正处理的时序 hazard 有两类：一是 reconvergent branches 因新流水级产生不同 arrival cycle，必须 delay-match；二是 sparse ready-valid 若只延迟 data 会破坏 handshake，必须以 FIFO 同时保存数据并传递 backpressure。论文没有报告精确的 buffer depth 分配算法；它只明确 optimized split-FIFO 可由两个相邻 switch-box registers 构成 size-two FIFO。[pdf:E10]（PDF 物理页 10，Fig. 18 前正文）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有复杂理论证明，核心数学只有两个直接服务于工程决策的式子。

第一，STA 对 DAG 中节点 `N` 的 arrival time 定义为

\[
\operatorname{arrival}[N] = \operatorname{delay}[N] + \max_{P\in\operatorname{pred}(N)} \operatorname{arrival}[P].
\]

其中 `delay[N]` 是通过节点 `N` 的延迟，`pred(N)` 是所有前驱；pipeline register 会切断组合路径，因此其 arrival time 重新置为 0。对 graph 做反向拓扑遍历即可得到所有节点的 arrival，最大值是 critical-path delay，再沿贡献最大者回溯出 critical path。[pdf:E03]（PDF 物理页 3，Eq. (1) 与紧邻正文）直觉上，这就是给每个节点记录“最晚到达的输入再加本节点延迟”；post-PnR register insertion 的作用是把一条过长累加链从插入点重新计时。

第二，detailed placement 对每条 net 使用

\[
\operatorname{Cost}_{net}=(\operatorname{HPWL}_{net})^{\alpha}.
\]

HPWL 是 net bounding box 的 half-perimeter wire length，α 控制对长 route 的非线性惩罚。α = 1 时接近总线长目标；α 增大后，一条极长 net 比若干短 net 更昂贵，因此 placement 更愿意压缩潜在 critical route。论文不是解析求 α，而是因单次 PnR 只需数秒，在 α = 1…30 上枚举并选最高频结果。[pdf:E06]（PDF 物理页 6，Eq. (2) 与相邻段落）

branch delay matching 没有给出独立公式，但算法对象从“纳秒 delay”换成“整数 cycle latency”：若同一节点存在多个不同 cycle-arrival 值，就给较短支路补 storage，直到输入同步。[pdf:E03]（PDF 物理页 3，Fig. 2 右侧正文）这一步是功能正确性的核心，而不是性能 heuristic。

## § 7 — 实验设计与结论

**问题 1：STA model 是否足以指导高频应用？** 作者在 GlobalFoundries 12 nm、32×16 array（384 PE tiles、128 MEM tiles）的 post-layout netlist 上，用 SDF-annotated gate-level simulation 搜索每个应用的最快 clock period，搜索粒度 0.05 ns。结果中 STA 预测通常更悲观；在关注的 500 MHz 以上区间，平均误差为 13%，因此作者把它视为实际 maximum frequency 的保守下界。[pdf:E07]（PDF 物理页 7，Section VI-A 与 Fig. 9）这验证的是 post-layout timing simulation 一致性，不是流片后 silicon measurement。

**问题 2：register absorption 是否真的释放互连资源？** 五个 dense image/ML 应用比较 pipelining 前、吸收前与吸收后的 register usage。按应用不同，减少比例从 0% 到 97%；Unsharp 与 ResNet convolution 因 chained multiply-add 较多而收益最大，部分 register 只需改 MEM address-generator configuration，不占额外 memory，register-file replacement 才会消耗相应 storage。[pdf:E07]（PDF 物理页 7，Fig. 10 与 Section VI-B）[pdf:E08]（PDF 物理页 8，Section VI-B 延续）结论是该优化高度依赖 kernel structure，不能把 97% 当作普遍值。

**问题 3：dense application 的速度与 EDP 是否改善？** 五个 benchmark 为 Gaussian、Unsharp、Camera、Harris 与 ResNet-18 的一个 conv5_x layer；图像 frame size 分别为 6400×4800、1536×2560、2560×1920、1530×2554。Fig. 11 做 compiler-pass 增量对比，Table I 则用 SDF gate-level simulation 验证最终数值：例如 Gaussian 从 103 MHz、22.6 ms/frame、156 mW 变为 610 MHz、3.66 ms/frame、841 mW；Harris 从 30 MHz、70.6 ms/frame、85 mW 变为 571 MHz、1.90 ms/frame、614 mW。[pdf:E08]（PDF 物理页 8，Table I 与 Section VI-C）总体上，all software pipelining 将 runtime 降低 84%–97%、EDP 降低 86%–99%；compute pipelining 单独贡献 35%–81% runtime reduction，PnR 中及 PnR 后技术再贡献 48%–85%。硬化 flush broadcast 在软件流水全部启用后另降 runtime 31%–56%。[pdf:E08]（PDF 物理页 8，Figs. 11–13 与相邻正文）

**问题 4：sparse ready-valid workload 是否仍受益？** 四个 70% sparsity benchmark 使用 compute-unit input FIFO，因此 compute pipelining 默认开启。placement optimization 与 post-PnR pipelining 将 runtime 相对 compute-only 降低 52%–71%，EDP 降低 60%–81%；Tensor TTV 从 0% 到 99% sparsity 时，绝对 runtime 随稀疏度下降，但流水技术的相对收益不依赖 sparsity。Table II 中 Tensor TTV 从 260 MHz、10.0 μs、170 mW 变为 833 MHz、3.87 μs、394 mW。[pdf:E09]（PDF 物理页 9，Figs. 14–16、Table II 与 Section VI-D）

**问题 5：与其他 interconnect/pipelining 选择相比怎样？** 在同一 hardware-generation platform、相同 technology、tile architecture 和 application 上，Cascade 相对放大到 32×16 的 HyCUBE-like 方案取得 47%–95% lower runtime 与 59%–85% better EDP。对 Plasticine-like sparse interconnect，exhaustive FIFO 的 runtime 与 Cascade 相差 10% 以内，但 Cascade power 低 21%–36%；用两个相邻 switch-box registers 组成 size-two split-FIFO 后，相对 Plasticine power 再低 13%–39%，代价是部分应用 runtime 增加。[pdf:E10]（PDF 物理页 10，Figs. 17–18 与 Section VI-E）这些是统一实现平台上的架构模拟比较，不是对原论文芯片或原 compiler binary 的直接测量。

不得外推的范围很明确：证据覆盖静态 configurable interconnect、特定 12 nm 32×16 CGRA、五个 dense 与四个小型 sparse benchmark；没有证明动态 NoC、任意 CGRA、任意 buffer pressure、任意图规模或真实芯片 PVT 条件下都保持同样倍数。compile time 通常增加，主要来自 α 枚举；Gaussian 因 low-unrolling duplication 反而降低总 compile time。[pdf:E08]（PDF 物理页 8，Table I 与 Section VI-C）

## § 8 — Take-aways

**5 句话：**

1. Cascade 先冻结 mapping 与 PnR，再利用 post-PnR STA 找到真实 interconnect critical path，只开启必要的 switch-box register。[pdf:E03]（PDF 物理页 3，Section III-A）
2. 新寄存器造成的 cycle mismatch 通过 branch delay matching 与 MEM-controller incremental rescheduling 修正，因此不必回到完整 schedule/PnR 循环。[pdf:E04]（PDF 物理页 4，Section III-B）
3. 非关键支路寄存器可被 MEM starting-cycle offset 或 register-file shift chain 吸收，实验中的 register reduction 为 0%–97%。[pdf:E07]（PDF 物理页 7，Fig. 10）
4. dense 与 sparse 需要不同 storage semantics：前者可用 register，后者必须用 FIFO 同时维护 data/ready/valid handshake。[pdf:E07]（PDF 物理页 7，Section V-D）
5. 论文最强的系统证据来自 post-layout STA/SDF 与同平台 architecture comparison，而不是流片实测。[pdf:E07]（PDF 物理页 7，Section VI-A）[pdf:E10]（PDF 物理页 10，Section VI-E）

**3 句话：**

1. Cascade 把 PnR 后的真实 wire delay 变成可局部修复的 timing problem，而不重新打开整个 mapping search。[pdf:E03]（PDF 物理页 3，Fig. 2）
2. 它靠 branch balancing、schedule offset 和 register absorption 维持功能并控制资源，靠 FIFO 语义扩展到 sparse flow。[pdf:E04]（PDF 物理页 4，Figs. 3–4）[pdf:E07]（PDF 物理页 7，Section V-D）
3. 在本文平台上，这套组合使 dense runtime 降低 84%–97%、sparse runtime 降低 52%–71%，但收益边界仍受目标 interconnect 与 benchmark 限制。[pdf:E08]（PDF 物理页 8，Section VI-C）[pdf:E09]（PDF 物理页 9，Section VI-D）

**1 句话：** Cascade 的本质是冻结空间映射、再精确重排时间边界，以 selective storage 换取高频而避免 exhaustive pipelining。[pdf:E03]（PDF 物理页 3，Section III-A）

## § 9 — 最脆弱的假设

最脆弱的假设是：**在 mapped topology 与 route 完全不变的前提下，关键路径上存在足够的可启用 storage，而且新增 latency 能靠 branch matching、MEM schedule offset 或 FIFO 被全图一致地吸收。**这是 Cascade 能“post-PnR 但不重新 PnR”的成立条件。算法明确只打开现有 route 上未启用的 switch-box register；插入后若 reconvergent input cycle 不同，就继续在其他支路补 register。[pdf:E03]（PDF 物理页 3，Section III-A）如果关键 route 没有可用切点，或一次切断诱发的 matching storage 扇出超过互连资源，核心迭代会在达到目标频率前停止；如果 endpoint schedule 无法只靠 cycle offset 修正，冻结 topology 的前提也会失败。

论文给出的支持包括：目标 array 在每条 16-bit 与 1-bit switch-box outgoing track 上都有 configurable pipeline register；MEM controller 的 delay register 可做 incremental schedule update；五个 dense benchmark 中 absorption 最高释放 97% 的 register；sparse 情形用 FIFO 保持 ready-valid semantics。[pdf:E03]（PDF 物理页 3，Section III-A）[pdf:E04]（PDF 物理页 4，Sections III-B–IV）[pdf:E07]（PDF 物理页 7，Fig. 10 与 Section V-D）但证据也暴露了边界：register reduction 最低为 0%，register-file absorption 依赖目标架构存在 register file，sparse flow 又要求 interconnect 中实际存在 FIFO。论文没有给出“任意 mapped graph 都能完成 delay matching”的资源上界或可行性证明，因此这一假设仍是基于 benchmark 的工程证据，而不是普遍定理。

## § 10 — 最小复现实验

一周内可复现的最小闭环，是固定一个小型 reconvergent dense kernel，例如两条长度不同的 multiply-add branches 在一个 PE 汇合，只比较 **同一份 PnR result** 上的 unpipelined 与 post-PnR-pipelined configuration。

1. 用 Cascade 已有 target CGRA timing model 生成一次 mapped/PnR graph，并保存 route、placement 和随机种子；不启用 α sweep、broadcast hardening 或 low-unrolling duplication，避免把其他 pass 的收益混进 post-PnR claim。
2. 对 baseline 运行 application STA，记录 critical-path delay、critical route 与 functional output；再启用一次或多次 critical-path register insertion、branch delay matching 和 MEM incremental rescheduling，确认前后 placement/route topology 完全相同。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Section III-A）[pdf:E04]（PDF 物理页 4，Section III-B）
3. 对两个版本跑同一输入的 cycle-accurate simulation，逐样本比较输出，并记录 inserted register 数、absorbed register 数、final cycle latency 与 STA critical-path delay。若条件允许，再用 SDF gate-level simulation 复核两个 clock period；论文采用的搜索粒度是 0.05 ns。[pdf:E07]（PDF 物理页 7，Section VI-A）

支持核心 claim 的结果是：输出逐样本一致、PnR graph 未变、critical-path delay 明显下降，并且 MEM start-cycle 的变化正好解释新增 pipeline cycles。反驳结果是：必须改变 route 才能找到切点、branch matching 无法在资源预算内完成、schedule offset 后输出错位，或 STA 预测的频率提升在 SDF simulation 中消失。这个实验不需要复现全套九个 benchmark，却能直接检验“冻结空间结构后能否只改时间边界”这一核心机制。

## § 11 — 最强反例设计

最强反例不是再找一个“收益较小”的图，而是构造一个 **高扇出、强 reconvergence、storage 饱和的混合静态/ready-valid graph**。让一条跨越多行 MEM tile 的长 data route 成为唯一 critical path，同时让它在多个下游 PE 与许多短支路汇合；占用沿途可配置 register/FIFO，并让反向 ready path 穿过同一组 switch boxes。这样，切断一条 data path 会要求大量匹配 register，切断 handshake path 又要求成组 FIFO，最坏情况下形成比原 critical path 更昂贵的 storage frontier。该攻击直接瞄准“只在现有 route 上启用 storage、不给 topology 第二次机会”的机制，而不是泛泛攻击 benchmark 数量。[pdf:E03]（PDF 物理页 3，Section III-A）[pdf:E07]（PDF 物理页 7，Section V-D）

实验上应固定相同 array 与频率目标，比较三种方案：Cascade post-PnR selective pipelining、exhaustive FIFO/register pipelining，以及允许 timing-driven remapping/PnR 的联合优化 baseline。测量最终可达 clock、为 branch/handshake matching 新增的 storage、是否 routable、功耗和编译时间；所有方案都必须通过相同 functional trace。如果 Cascade 在保持 topology 时无可用切点或资源爆炸，而联合优化通过移动 fanout/reconvergence 点获得更短路径和更低 storage，那么论文结果的替代解释就是：现有 benchmark 恰好具有可吸收的 branch structure，而不是冻结 PnR 普遍优于联合优化。论文自己的 0%–97% absorption 跨应用波动，以及 ADRES 上复杂 benchmark 无法 branch-match 的讨论，说明这个反例具有可预测的失败机制。[pdf:E07]（PDF 物理页 7，Fig. 10）[pdf:E09]（PDF 物理页 9，Section VI-E 开头）

## § 12 — Follow-up Research Bet

**主 idea：phase-tagged local wavefront CGRA，取消全阵列 global epoch。** 这是候选判断；本卡没有联网检索相关全文，不能声称 novelty 已闭合。新的研究问题是：能否把 dense static schedule 的 cycle timestamp 与 sparse ready-valid token 合成一种显式的 phase-tagged data token，让每个 MEM/PE tile 仅依据局部 token phase 推进，从而在大阵列上不再依赖全局 flush broadcast，也不再要求所有 reconvergent path 具有相同物理 cycle latency？

它首次要实现的能力，是让 route latency 本身成为合法的编译变量，而不是插完 register 后必须被 branch delay matching 消除的误差。因果链是：为每条 logical value 增加有限 phase → MEM controller 按 phase 选择 address/schedule state → switch-box FIFO/register 传递 value 与 phase → reconvergent PE 按 phase 配对输入 → 不同物理路径可拥有不同 latency，同时保持应用级 iteration 对齐 → 编译器可以围绕 throughput、storage 与 communication energy 联合选择 space-time route。它至少改变了状态表示（普通 dataflow edge 变为 value-plus-phase）、时间模型（全局 cycle equality 变为局部 phase matching）、硬件映射（固定 delay matching 变为 phase-aware storage）和系统边界（global flush tree 变为局部 wavefront）。

这个押注来自两条论文特异证据。方法侧，现有 MEM tile 已能通过 delay register 改 starting cycle，而 sparse path 已有能同时携带 data/ready/valid 语义的 FIFO；说明“把时间状态下沉到 tile 与 interconnect storage”已有硬件支点。[pdf:E04]（PDF 物理页 4，Section III-B）[pdf:E07]（PDF 物理页 7，Section V-D）实验侧，global flush hardening 单独降低 runtime 31%–56%，说明全局 epoch distribution 已是显著路径；同时 sparse pipelining 的相对收益在 0%–99% sparsity 间基本不变，提示 timing structure 可以与具体非零数据比例分离。[pdf:E08]（PDF 物理页 8，Fig. 13）[pdf:E09]（PDF 物理页 9，Fig. 15）

最大研究收益是把 dense 和 sparse 的两套 timing semantics 统一成可缩放的 local protocol，并使编译器能主动利用非均匀 route latency，而不是为全图等时到达支付 register/FIFO 扇出。最大科学风险是 phase metadata、matching buffer 和局部控制的面积/功耗可能超过取消 global flush 与减少 branch matching 得到的收益；另一个替代解释是，Fig. 13 的收益主要来自特定 flush placement，而非全局同步模型本身。首个可证伪实验应在同一 32×16 layout 上实现一个 2-bit 或 3-bit phase-tag 原型，只选择一个 dense Gaussian pipeline 与一个 sparse Tensor TTV：固定 functional graph 和 target throughput，对比原始 global-flush/branch-matched Cascade 与 local-phase wavefront，测 critical path、每条 edge 的 storage、token metadata power、deadlock-free trace 和 SDF runtime。若去掉 global flush 后 critical path 没有下降，或 phase buffer 的功耗/容量增长快于 array diameter 带来的收益，就否定核心机制，而不是再加补丁保住结论。

与本文最近方法的实质区别是：Cascade、HyCUBE-like 和 Plasticine-like 比较的核心变量仍是“在哪里插 register/FIFO、是否 exhaustive”，而该 idea 改变的是应用时间语义与 experimental object——从 cycle-balanced route graph 变为 phase-carrying local wavefront；它不是在原流程外加 monitor、threshold 或 fallback。[pdf:E10]（PDF 物理页 10，Figs. 17–18）

**Wild-card alternative：** 候选探索一种完全不同的机制——把 low-unrolling duplication 扩展成可拼接的 heterogenous timing chiplet，让 compiler 先在多个不同 PE/MEM 比例与 hop-delay 的小区域生成已闭合 micro-pipeline，再按应用 dataflow 的通信矩阵选择并拼接区域，以“区域类型与拼接拓扑”而非 register position 作为主要设计变量；其可行性依据是低 unrolling 在较小区域先 PnR 后复制的机制，但是否区别于已有 spatial accelerator partitioning 尚未检索，不能声称 novelty。[pdf:E06]（PDF 物理页 6，Section V-C4）
