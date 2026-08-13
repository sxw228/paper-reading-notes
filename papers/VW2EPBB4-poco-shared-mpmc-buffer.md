# PoCo: Extending Task-Parallel HLS Programming with Shared Multi-Producer Multi-Consumer Buffer Support

作者：Akhil Raj Baranwal；Zhenman Fang  
出处：ACM Transactions on Reconfigurable Technology and Systems, Vol. 18, No. 4, Article 53  
年份：2025  
DOI：10.1145/3771938  
Zotero key：VW2EPBB4  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的不是“怎样再做一个 FIFO”，而是怎样让多个独立 HLS task 共享同一片片上存储，同时不把它们重新焊成一个大 FSM。TAPA、PASTA 一类 task-parallel system（TPS）已经能把 task 放进不同 FPGA slot，并在点到点通道上插入寄存器；但其 buffer 通道是 Single-Producer-Single-Consumer（SPSC）。一旦多个 task 要读写同一资源，设计者就要自行包装任务、铺设 request/response FIFO、写仲裁、重新 profile，最终还可能在 place-and-route 阶段遇到拥塞或跨 SLR 长路径。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 4，Section 2.1）

PoCo 的研究问题可以准确表述为：能否把共享片上内存做成 HLS task 可调用的 Multi-Producer-Multi-Consumer（MPMC）服务，并同时处理连接、page 所有权、动态请求、双端口利用率和 floorplan？其价值有两层：对程序员，它让新 task 只增加自己的 MPMC port，而不必重写所有既有连接；对硬件，它试图把不可放置的大组合逻辑拆成 latency-insensitive 的流水模块。作者报告，在 SPSC lane-switching 子实验中 BRAM 平均降低 22%、最高降低 50%，并在三个 MPMC case study 中观察到最高 1.5× frequency improvement；这些是特定 FPGA、设计和 baseline 上的结果，不是任意共享存储的普遍保证。[pdf:E03]（PDF 物理页 32，Conclusion）

## § 2 — 前人工作与不足

最直接的基线是 PASTA。其 buffer channel 用双端口 BRAM/URAM、Free Sections（FS）FIFO 和 Occupied Sections（OS）FIFO 在单个 producer 与 consumer 间传递 section token；producer 从 FS 取 token、写完送入 OS，consumer 从 OS 取 token、读完归还 FS。这套机制已经解决了 SPSC ping-pong 和跨 slot 的 latency-insensitive 通信，但共享资源仍没有多个独立 FSM 的仲裁入口。[pdf:E02]（PDF 物理页 4，Section 2.1）

论文用 shuffle 说明两种不足。朴素 HLS 会把多个 consumer 的选择逻辑连回共同 FSM，并以静态 time-division multiplexing（TDM）分配相同带宽；访问率不均时会把周期分给已经 idle 的 task。高级 PASTA 写法则要为每个 buffer 加 intermediary consumer，再在 4 buffer × 2 T2 的示例中建立 16 条 request/response FIFO，性能取决于程序员手写的动态仲裁。[pdf:E04]（PDF 物理页 7，Section 2.2.1）

相关路线各自覆盖了局部问题：CoRAM 和 LEAP 提供统一 memory view，但论文认为其 off-chip access 或集中式 scratchpad controller 带来延迟；HiDMM 支持 malloc/free 风格的 dynamic memory management，却通过 compile-time profiling 假定静态 pointer access schedule；AutoBridge、FADO 等处理 multi-die floorplanning，却不了解 PoCo 内部哪些组合单元不可拆、哪些通道可任意流水；HeteroCL 解耦计算、访存和数据表示，但没有显式 TPS MPMC buffer 与该论文的 coarse-grained placement。[pdf:E05]（PDF 物理页 31，Section 7）

这里必须克制：作者写了“据其所知”PoCo 是首个面向现代 HLS programming model、以片上内存支持 MPMC 的工作，但本卡遵守封闭来源，不联网复核，因此不把该 novelty claim 当成已独立证实的事实。[pdf:E05]（PDF 物理页 31，Section 7）

## § 3 — 重建作者的思考路径

从既有知识出发，第一步是承认 SPSC token buffer 已经有两个重要资产：每个 page 可以有明确的 producer/consumer ownership，而且连接可流水、可跨 slot。第二步是看到，MPMC 真正缺的不是一块更大的 RAM，而是把“谁请求哪个资源、响应回给谁、何时释放 ownership”从用户 task 中拿出来。第三步是避免把共享重新实现为一个巨型 crossbar/FSM：让每个 transactor 只面对成对 TX/RX FIFO，在内部用分层解析、switch fabric 和 accessor-pair 路由。第四步是注意到资源复用与读写互斥是两个不同层次的问题：前者分配静态池中的 page index，后者用 page token 控制一次生产或消费阶段。论文也明确说动态分配实际只是对静态已分配 memory pool 的 index 做运行时分配。[pdf:E06]（PDF 物理页 8，Section 2.2.2）[pdf:E07]（PDF 物理页 13，Sections 3.2.2–3.2.3）

再往硬件落地，SPSC 的一个端口固定给 producer、另一个固定给 consumer，会在单边活跃时浪费一半端口，因此作者把“两个物理端口”从“一个生产口加一个消费口”改成“当前 owner 的双 lane”。最后，既然 PoCo 自己生成内部架构，它也知道 LBB–IHD 是必须共置关注的组合连接，而大部分其余通道可插 pipeline，于是把 architecture knowledge 送入 floorplanner，而不只依赖黑盒 netlist。[pdf:E08]（PDF 物理页 20，Figure 14 与 Section 4.4）[pdf:E09]（PDF 物理页 21，Sections 4.4–4.5.1）

## § 4 — 核心 Intuition

PoCo 的核心不是让 RAM 同时接受任意数量的物理访问，而是把多个用户 task 的访问请求变成带地址、类型和回程身份的消息，再由流水化共享服务把它们路由到有限数量的 accessor。每个 page 仍遵守一个写阶段或一个读阶段的 token ownership，真正的并发度由 block/accessor 数量、partition、双端口和仲裁冲突共同决定。换句话说，它用“消息化访问 + page 级 ownership + 可布局的服务网络”替代“用户手写的点到点 buffer 图”。[pdf:E07]（PDF 物理页 13，Figure 7 与 Section 3.2.2）[pdf:E10]（PDF 物理页 16，Figure 8）

## § 5 — 具体方法与完整 Pipeline

以论文的 shuffle 为例，四个 T1 mapper 写 key–value page，两个 T2 sorter 读取它们：

1. **声明与连接。** 用户用 C++ template 指定数据类型、partition 数与 block/cyclic/complete scheme、BRAM/URAM、block 数和 block depth；每个 task 连接若干 MPMC port。一个 port 是 request/response 两个 FIFO，控制字段至多 24 bit，由 `xcxr`、`page` 和 `opcode/status` 构成，word address 与 payload 另放在 `addr/data`。[pdf:E11]（PDF 物理页 12，Sections 3.1–3.2.1）
2. **分配。** T1 调用 `allocate()` 得到 page index；Page Manager（PGM）在静态池的 allocation bitmap 中找空 page。Control Request Parser（CRP）把所有 transactor 的 alloc/free 轮询汇聚，并优先处理 deallocation。任何 task 都可以 free，未规定只能由原 allocator 释放。[pdf:E08]（PDF 物理页 20，Section 4.3.2 与 Eq. 2）
3. **共享引用。** T1 通过应用自己的点到点 FIFO 把 page index 交给 T2。PoCo 没有自动推导应用级“谁应接收哪个引用”；它只让 index 在全局 shared-buffer view 中有意义。[pdf:E12]（PDF 物理页 15，Listings 2–3）
4. **请求分流与路由。** Request Router（RQR）把 alloc/free 送 CRP、read/write 送 Data Request Parser（DRP）；DRP 依据 target accessor 添加 Ω-MIN routing tag，并写入 transactor identity。四个 Ω-MIN 分别承载读写请求和返回，网络每级由 2×2 switch 组成。[pdf:E10]（PDF 物理页 16，Figures 8–9）[pdf:E13]（PDF 物理页 18，Figure 12 与 Section 4.1.4）
5. **访问与互斥。** Output Handler（OHD）处理写，Input Handler（IHD）处理读。每个 block 包含多个 page，每个 page 只有一个 section/token；OHD 从 FS 取得写 token 并按请求中的 release bit 决定何时送 OS，IHD 从 OS 取得读 token并最终归还 FS。同一 block 可以同时读写不同 page，但同一 page 在一个时刻只能处于读或写 ownership。[pdf:E07]（PDF 物理页 13，Section 3.2.2）[pdf:E13]（PDF 物理页 18，Section 4.1.4）
6. **响应顺序。** Response Generator（RSG）按每种 request type 的接收顺序闭合 transaction，但跨类型默认优先级是 read > write > free > alloc；若设计要求 read/write 严格合序，可在 compile time 合并两种 tracking FIFO。因此论文保证的是配置下的队列顺序，不是所有 memory operation 的全局 sequential consistency。[pdf:E14]（PDF 物理页 17，Section 4.1.3）
7. **吞吐隐藏。** frontend source-to-source transform 把逐次 `do_read` 改为独立 TX loop 与 RX loop，使多个请求在 DP pipeline 中并行在途；RX backpressure 最终经 FIFO full 反压 TX。它隐藏首包 latency，但不消除争用、mutex wait 或 placement pipeline latency。[pdf:E15]（PDF 物理页 23，Section 5.2）[pdf:E16]（PDF 物理页 24，Listings 5–6 与 Figure 17）
8. **内存端口与布局。** Lane-Switch（LS）观察 FS/OS FIFO 活动，将 dual-port memory 的两个端口在下一次访问前一起切给 producer lane 或 consumer lane；各 partition 的 LS 同周期切换。backend 再根据综合资源与板卡 BRAM/URAM column，把 IHD/OHD 与 LBB 组合单元分配到 Pblock，其他 latency-insensitive 边插 pipeline，最后 stitch RTL 并完成 PNR。page depth 也参与 timing 设计：论文的 128-bit、2-partition、4-block 示例把 2 个深 page 改成 8 个浅 page 后，频率从 237 MHz 升至 305 MHz，代价是 LUT 增加 1.7%。[pdf:E09]（PDF 物理页 21，Section 4.4）[pdf:E17]（PDF 物理页 22，Figure 15 与 Section 4.5.2）[pdf:E15]（PDF 物理页 23，Figure 16）

论文不涉及 EMT 的离散模型、开关事件、数值积分、多速率或定点误差；其“时间”是请求 latency、pipeline II、仲裁与 FPGA clock。它也没有给出 cache coherence、跨 page transaction、multi-word atomic commit 或一般内存一致性协议。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有算法正确性定理，只有架构延迟和资源维度关系。设 transactor 数为 (T)，block/accessor-pair 数为 (N)。单个 Ω-MIN 的 stage 数取决于端点规模；一次 data transaction 要经过请求侧和响应侧网络，再加 RQR、DRP、RSG 各一拍，因此最小 datapath latency 为

\[
DP\_LATENCY = 3 + 2\left\lceil \log_2(\max(T,N)) \right\rceil .
\]

该 latency 只作用于第一个响应；pipeline 填满后可以 back-to-back 返回。但真实实现还会增加 floorplanning pipeline、mutex wait 与 contention，所以这个式子是结构下界，不是最坏情况。[pdf:E13]（PDF 物理页 18，Eq. 1）

若静态池共有 (P) 个 page，PGM 用深度为 \(\lceil P/32\rceil\) 的 32-bit vector array 保存 allocation 状态，通过 4-bit comparator、priority encoder 和 256-entry lookup 找最低空位。论文给出的无排队 worst-case allocation latency 是 \(\lceil P/32\rceil+2\) cycles；包含 RQR、CRP、PGM、CRP、RSG 的 control path 为

\[
CP\_LATENCY = 5 + \left\lceil P/32 \right\rceil .
\]

若所有 page 已占用，PGM 会一直等 free；若 RSG 前面还有 data response，control response 还会被延后，因此此式同样不是饱和系统的有限最坏时延保证。[pdf:E08]（PDF 物理页 20，Section 4.3.2 与 Eq. 2）

## § 7 — 实验设计与结论

- **问题：Lane-Switch 是否能回收单边活跃时浪费的 dual-port bandwidth？** 实验：在 Alveo U280 上用 Vitis/Vitis HLS 2023.2、XRT 2023.2 和 PASTA 0.0.20240104.2，对 KMeans、Minimap、8-PE HiSpMV 比较 PASTA buffer 与 LB。答案：BRAM 分别减少 3%、13%、50%，frequency 相近；一个 8 partition、每 partition 64-bit dual-port（读写总宽 1024 bit）的 LB，LS 逻辑为 98 LUT、33 FF。[pdf:E18]（PDF 物理页 25，Figure 18(a) 与 Section 6.1）
- **问题：MPMC buffer 随 pages、partitions、blocks、depth 怎样扩展？** 实验：U50 post-route，128-bit element，分别 sweep 四个维度。答案：page/partition 主要带来近线性 BRAM/LUT 增长；block 与 partition 增大后，瓶颈变成有限 LAGUNA die-crossing。文中 (N=64,P=4) 的每 port 宽 1216 bit，跨 SLR 资源不足；4096-depth 例中把 8 BRAM cascade 改为 4 page × 2 cascade，frequency 约提高 1.3×。[pdf:E19]（PDF 物理页 26，Figure 19 与 Sections 6.2.2–6.2.4）
- **问题：动态 Ω-MIN 仲裁在重负载下比 static schedule 好多少？** 实验：每个 transactor 发 1024 个随机地址请求，page 预分配；sweep accessor 数与 activity factor (A)。答案：在 (A=1) 的最坏密集流量下，effective bandwidth 仍约比同 transactor 数的 static scheduling 高 20%；降低 activity 会减少 conflict。作者明确指出单 transactor–accessor 热点只有一条 Ω-MIN path，密集固定通信更适合 dedicated SPSC channel。[pdf:E20]（PDF 物理页 27，Section 6.3.2）[pdf:E21]（PDF 物理页 28，Figure 21 与 Section 6.3.2）
- **问题：完整工具在真实应用上是否改善实现？** 实验：U50 Shuffle、U280 GraphTraversal、U280 PageRank，全为真实板卡、post-route，并保持对比中的静态 memory allocation 规模相近。答案：Shuffle 为 218 MHz，对 TAPA 52 MHz、PASTA 144 MHz；GraphTraversal 为 232 MHz，对 AutoBridge 168 MHz；但 PageRank 为 191 MHz，低于专用 ReGraph 的 214 MHz。论文正文另有 169/193 MHz 的四舍五入或不同 run 表述，本卡以 Table 3 的逐项值为主，并保留该文本不一致。[pdf:E22]（PDF 物理页 29，Table 3 与 Section 6.4）
- **问题：编程连接是否真的减少？** 实验：比较 LOC 与 interface count。答案：Bandwidth Testing 从 1097 LOC/12 interfaces 降到 160/2，Shuffle 从 1571/22 降到 649/14，GraphTraversal 从 1364/47 降到 454/15；作者也承认 LOC 对原代码写法敏感，interface count 更稳定。[pdf:E23]（PDF 物理页 30，Table 4 与 Section 6.5）

这些实验支持“PoCo 能在所测 task-parallel accelerator 中降低连接复杂度并改善若干实现”的 claim，但不支持把它外推为任意 workload 都更快：PageRank 反例已显示 generic framework 会输给 domain-specific pipeline，且 high-contention traffic、满池 allocation、adversarial ordering 没有给出 tail latency 或 fairness 上界。

## § 8 — Take-aways

**5 句话。** PoCo 把 task 对共享片上内存的读、写、分配和释放变成 request/response message。它用 block/accessor 组织并发，用 page token 组织读写阶段，而非允许同一 page 的任意同步访问。动态 allocation 只是静态 memory pool 的 page index 分配，不是物理 RAM 动态增减。Ω-MIN、Lane-Switch、source transform 和 placement-aware constraint 分别解决连接、端口利用、首包 latency 隐藏和 PNR。实测证明它在若干 FPGA case 上有效，但 hot route、mutex 切换、die crossing 与专用架构仍可成为瓶颈。[pdf:E10]（PDF 物理页 16，Figure 8）[pdf:E22]（PDF 物理页 29，Table 3）

**3 句话。** 它提供的是“共享 memory service”，不是无限端口 RAM。其 correctness 边界依赖用户正确释放 page mutex，ordering 也只在各请求类型或可选 read/write 合序范围内。对 ResearchStudio 最有价值的是把静态调度图与物理互连共同设计的思路，而不是直接照搬 MPMC runtime arbitration。

**1 句话。** PoCo 用消息路由、page ownership 与布局感知后端，把 HLS 的 SPSC buffer 扩展成可编程 MPMC 服务，但没有提供通用 atomic commit 或逐周期 bank 冲突合法性。

## § 9 — 最脆弱的假设

失败代价最大的假设是：应用能遵守“持有一个 page 时不等待另一个 page，并在最后一次同类访问上准确发出 release”的协议。PoCo 的 deadlock prevention 不是硬件自动发现 wait-for cycle，而是要求 programmer 在访问下一 page 前立即释放当前 page，以破坏 Coffman 的 hold-and-wait 与 circular-wait；`do_read()` / `do_write()` 的参数承担这个语义。[pdf:E24]（PDF 物理页 19，Section 4.2）

这个假设在真实 task graph 中容易失效：join、scatter-gather、双缓冲交换、需要同时观察两页后再决定写回的算法，都自然地产生多资源持有；异常控制流也可能漏掉最后一次 release。论文说明了规则，却没有展示静态 checker、runtime timeout、cycle detector，亦没有 deadlock stress test。更细的 ordering 风险也被留给配置：RSG 默认跨类型重排 read/write/free/alloc，read/write 全序需要另行合并 tracking FIFO。[pdf:E14]（PDF 物理页 17，Section 4.1.3）因此核心贡献成立的条件不是“任意 C++ task 可安全共享”，而是“task 服从受限 page-ownership protocol”。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 compiler，而是验证“动态 MPMC 仲裁是否在 burst imbalance 下优于静态 TDM，同时保持 page ownership 正确”。

实现一个 4-transactor、4-block、每 block 4-page、128-bit data 的 cycle-accurate RTL 或 HLS harness：保留 RQR/DRP、简化 Ω-MIN、IHD/OHD token 与 RSG；page 全部预分配，从而隔离 PGM。生成三类 trace：均匀随机、单 hot accessor、两阶段 burst（部分 transactor 提前 idle）。与 per-transactor static round-robin/TDM 比较 accepted requests/cycle、p50/p99 response latency、每 accessor fairness、mutex wait、data mismatch。再用 reference model 逐 transaction 检查：release 前同 page 不得从 write owner 转 read owner，response 必须满足所配置的 per-type ordering。

支持 claim 的门槛应预先固定为：在 burst imbalance 中 dynamic fabric 的有效吞吐显著超过 static TDM，并且无 ownership/response mismatch；反驳信号是 hot route 下吞吐不优于 dedicated SPSC，或任一合法 API trace 导致 starvation/错序。论文的随机请求、activity factor 和“热点更适合 SPSC”结论直接给出了这组最小变量。[pdf:E20]（PDF 物理页 27，Section 6.3.2）[pdf:E21]（PDF 物理页 28，Figure 21）

## § 11 — 最强反例设计

最强反例是构造“合法释放但极端集中”的 many-to-one 流量，而不是故意违反 deadlock 规则。令 32 个 transactor 每周期都向同一 accessor 的两个 page 交替发 128-bit read，持锁只覆盖单次 burst，另一组访问分散到其余 accessor；所有 page 预分配，排除 control path。比较 PoCo Ω-MIN、理想 output-queued crossbar 和该热点的 dedicated SPSC。测量热点与非热点的 p99/p999 latency、吞吐、starvation、head-of-line blocking，以及 RSG 的 read priority 是否让 write/free 长期推迟。

如果 PoCo 不仅热点退化，而且非热点流也被唯一 Ω-MIN path 的内部冲突显著拖慢，那么“适合 dynamic and uncharacterizable traffic”的解释就不足：观测到的平均 20% 优势可能主要来自论文使用的独立随机地址，而不是 MPMC fabric 对不规则应用的稳健性。论文已承认端点对之间只有一条 path、(A=1) 是最坏情况、密集 pair 更适合 dedicated SPSC，但没有报告 tail latency 或 adversarial correlation；这正是可证伪的缺口。[pdf:E21]（PDF 物理页 28，Figure 21 与相邻正文）

## § 12 — Follow-up Research Bet

**主 idea：把离线已知的确定性访问轨迹编译成“时空端口图”，而不是在运行时把它们当作一般 MPMC packet 仲裁。** 新研究问题是：对于固定有根三相 VSC 集电树，能否从精确 Schur elimination—full-state recovery 的依赖图直接构造一个跨周期、跨 bank、跨 PE 的 schedule，使每次 RAM port 占用、producer/consumer handoff 和状态版本在编译期就是图中的一等对象？它首次要实现的不是“更多 task 能访问同一 buffer”，而是把数值依赖正确性与真实双端口 bank 的逐周期合法性合成同一张可执行图。

因果链是：固定拓扑与固定 EMT step 给出静态读写集合 → Rake/Compress 决定消元与恢复的并行前沿 → 每个数据版本被映射到具体 bank/port/cycle → producer 完成事件产生下一版本，consumer edge 只读取匹配版本 → 编译器联合选择 PE、bank placement 与 interconnect pipeline → 硬件无需 Ω-MIN 的运行时竞争即可执行确定性完整 step。它改变至少四个设计变量：从运行时 arbitration 改为编译期 schedule；从 page ownership 改为 versioned state token；从通用 MPMC service 改为固定树的完整 EMT step；从平均 effective bandwidth 改为每周期 bank legality 与 step WCET。

论文特异依据有两类。结构上，PoCo 明确把 read/write request、accessor、响应 identity 和可流水 interconnect 分开，并表明大多数 task 间边 latency-insensitive，而 LBB–IHD 是必须关注的组合 union；这说明“访问语义、路由与布局共同编译”是可行的系统分层。[pdf:E10]（PDF 物理页 16，Figure 8）[pdf:E15]（PDF 物理页 23，Figure 16 与 Section 5.3）实验上，PoCo 的 scaling 已显示 concurrency 不是免费资源：(N=64,P=4) 时 1216-bit port 与有限 LAGUNA crossing 成为物理瓶颈；PageRank 又因每次 mutex switch 最长约 12 cycles 的 ownership transfer 而输给专用 ReGraph。[pdf:E19]（PDF 物理页 26，Section 6.2.3）[pdf:E22]（PDF 物理页 29，Table 3 与 Section 6.4.3）这共同支持一个候选判断：固定工作负载应把可预测的共享访问提前消解，而非保留通用仲裁自由度。

最大收益是得到从方程依赖到真实 bank port 的端到端可检查 schedule，并可能用专用静态网络换掉通用 Ω-MIN/RSG 的面积、冲突和 tail latency。最大科学风险是 schedule 可能被 event、数值迭代或非固定控制流破坏；此外，当前 ResearchStudio 只有 (N=7) trunk 的软件证据，尚不能声称硬件可行，更不能由 PoCo 的 generic buffer 结果推导出真实双端口逐周期合法性或 atomic commit。

首个判别实验应只取 (N=7) trunk：同一组 Schur elimination 与 recovery trace，分别映射到（a）静态时空端口图，（b）PoCo 风格 request/response shared service 的 cycle model。两者使用相同 PE 数、相同真实 dual-port bank 数与相同 pipeline latency；测 complete-step cycles、bank conflict、interconnect width、buffer/register footprint，并注入一类受控 event 观察是否必须重编排。若静态图只在忽略 event 或放宽 bank 约束时获胜，则核心机制被反驳；若在封闭约束下无 conflict 且 WCET/资源明显改善，才值得进入 RTL。与论文最近机制的实质区别是：PoCo 的 problem 是通用 task MPMC 编程，mechanism 是 runtime routing/page mutex，representation 是 request packet，experimental object 是 Shuffle/graph accelerator；这里的 problem 是固定树完整 EMT step，mechanism 是 compile-time dependency-to-port scheduling，representation 是 versioned state/port-time edge，experimental object 是可逐周期核验的 Schur—recovery 硬件图。因未做全文外部检索，这只是候选研究判断，不声称 novelty。

**Wild-card alternative：** 让每个 VSC 子树在边界上产生一种可合并的“消元消息”，由树形 reduction/broadcast 网络直接完成 Schur contribution 汇聚与全状态恢复，把物理拓扑本身变成通信拓扑；其设计变量是消息代数与树上 collective，而不是共享 bank 的访问 schedule，首测是比较同一 (N=7) trunk 上树网与集中式 bank 方案的跨层 wire volume 和 complete-step latency。
