# Towards Higher Performance and Robust Compilation for CGRA Modulo Scheduling

- 作者：Zhongyuan Zhao、Weiguang Sheng、Qin Wang、Wenzhi Yin、Pengfei Ye、Jinchao Li、Zhigang Mao
- 出处：IEEE Transactions on Parallel and Distributed Systems，Vol. 31，No. 9，pp. 2201–2219
- 年份：2020
- DOI：10.1109/TPDS.2020.2989149
- Zotero key：8T74QJF5
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的是：怎样把循环的 data-flow graph（DFG）用 modulo scheduling 映射到 coarse-grained reconfigurable architecture（CGRA）上，同时得到较小的 initiation interval（II）和可接受、可预测的编译时间。II 是相邻两次循环迭代开始执行的间隔；在相同硬件与循环语义下，II 越小，稳态吞吐率越高。CGRA 映射同时决定“何时执行”和“在哪个 PE 上执行、怎样路由”，而该问题已被归为 NP-complete，因此大循环、扇出不规则的循环和缓冲资源紧张的 CGRA 很容易把编译器拖入巨大的搜索空间。[pdf:E01]（PDF 物理页 1，Abstract 与 Section 1）

作者把实际瓶颈概括为三个互相放大的问题：编译器没有组合利用 PE output register、local register buffer（LRB）、global register buffer（GRB）和 on-chip memory buffer（OMB）；进入 spatial mapping 前没有识别关键的互连与计算资源不可能条件；现有 decomposed 方法又常用 maximum-clique 等昂贵搜索来补救。结果是两种坏结局：要么较快但 II 偏大，要么性能尚可却可能几天都不结束。[pdf:E02]（PDF 物理页 2，Section 1 的五类挑战与贡献）

这个问题重要，不只因为“编译更快”。CGRA 的价值依赖软件把 loop-level parallelism 真正投射到有限的 PE、端口和寄存器上；如果编译器不能稳定地产生映射，硬件面积和能效优势就无法转化为可部署的应用性能。论文因此把目标写成一个工程性的双目标：在固定时间预算内提高编译成功率，并在成功映射的循环上降低 II。

## § 2 — 前人工作与不足

论文把既有工作分成 integrated 和 decomposed 两类。Integrated 方法把 timing、placement、routing 一起搜索：DRESC 使用 simulated annealing，PSOMap 使用 particle swarm optimization，AA-ILP 使用整数线性规划；这些方法较通用，但大而不规则的 DFG 会让收敛时间或求解时间不可预测。EMS、Resource-Aware 和 GraphMinor 采用更专门的启发式，速度更快，却只覆盖部分失败模式，因而会牺牲一般性或映射效率。[pdf:E02]（PDF 物理页 2，Section 1）

Decomposed 方法先做 temporal mapping，再做 spatial mapping。SPR 允许超出 slack window 的 rescheduling；EPIMap 通过 graph epimorphism 和 maximum clique 找映射；REGIMap 显式用 LRB；Memory-Aware 显式用 OMB；RAMP 扩展 REGIMap，在 temporal 阶段提供更多 rescheduling 与 OMB 选择。它们已经证明“先时间、后空间”可行，但论文指出两类结构性不足：第一，缓冲资源通常被单独使用，缺少同一路径跨 PE/LRB/GRB/OMB 的组合分配；第二，temporal 阶段没有充分判断随后的 spatial embedding 是否可能，导致 maximum-clique 搜索在不存在解时仍长时间运行。[pdf:E03]（PDF 物理页 3，Figs. 2–4 与 buffer hierarchy）

因此，作者并不是发明 modulo scheduling，也不是第一次分解 temporal/spatial mapping。其论文内可证实的新意是重新分配工作量：让 temporal mapping 承担 buffer allocation、interconnection constraints solving（ICS）和 computational constraints solving（CCS），把 spatial mapping降为有 backtracking 与 reordering 的轻量贪心搜索。关于相对于 2020 年之后工作的 novelty，本卡未联网检索，不作外推。

## § 3 — 重建作者的思考路径

下面是基于论文背景与失败模式的逆向重建，不是作者逐字陈述。

第一步，研究者会先注意到 II 不是只由算术 PE 数量决定。一个值从 producer 到晚到达的 consumer 之间必须“活着”，若只能占用 PE output register，路由节点会吞掉本可执行有效操作的 PE。LRB、GRB、OMB 都能延长 value lifetime，但访问范围、端口、延迟和附加约束不同：LRB 不占 PE 计算，却要求 producer 与 consumers 映到同一 PE；GRB 全局可访问但端口昂贵且容量小；OMB 容量较多，却引入 load/store、延迟和能耗。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Section 2）

第二步，如果 temporal scheduler 只给每个操作时间、不理解这些后果，那么它交给 spatial mapper 的图可能已经不可嵌入。此时再用更强的 clique search，只是在证明一个本应更早暴露的资源冲突。于是合理的设计转向是：先用 lifetime-sensitive scheduling、graph balancing 和 routing-path sharing 把 DFG 变成显式带 routing lifetime 的图，再在 temporal 阶段解决缓冲、互连和同周期 PE 容量问题。[pdf:E04]（PDF 物理页 6，Fig. 5、Fig. 7 与 Section 4 开头）

第三步，若 temporal 阶段已尽量消除了结构性不可能，spatial 阶段就不必再承担全局优化的全部压力。先用局部可达性优先级快速放置；失败时只回溯真正影响当前节点的前驱映射；仍失败则换 BFS topology order；所有 order 都失败才增加 II。这个推理把“稳定编译”从设置一个搜索时间上限，改成在进入昂贵搜索前重写问题本身。

## § 4 — 核心 Intuition

核心 intuition 是：不要让 spatial mapper 在一个先天不可嵌入的 DFG 上盲搜；先在 temporal mapping 中把值的 lifetime、buffer 类型、互连扇入/扇出和每个 modulo slot 的 PE 压力处理到位。只要 temporal 阶段产出的 modified DFG 已满足这些关键约束，spatial mapping 就可以用贪心、有限回溯和重排序完成，而不必依赖高阶 maximum-clique 搜索。[pdf:E04]（PDF 物理页 6，Fig. 7）

## § 5 — 具体方法与完整 Pipeline

输入是循环的原始 DFG、目标 CGRA 的 PE/互连拓扑，以及 LRB、GRB、OMB 容量；输出是每个 DFG 节点到“PE × modulo time”的 mapping pair，并包含路由与 buffer assignment。以 Fig. 5 的 A–G DFG 为例，完整 pipeline 如下。[pdf:E04]（PDF 物理页 6，Figs. 5–7）

1. **计算起始 II 并做 time assignment。** 从 minimal II（MII）开始，用 lifetime-sensitive scheduling 缩短 producer 到最后一个 consumer 的值寿命，同时保持依赖关系。
2. **Graph balancing。** 若依赖边两端的 schedule time 相差超过一周期，插入 routing node，使 consumer 的输入同时到达。这里的 routing node 表示值在某周期占用路由介质，而不是新的有效计算。
3. **Routing Paths Sharing（RPS）。** 同一 producer、同一时刻携带相同数据的 routing nodes 合并。Fig. 5 中 A 到 E/F/G 的三条路径共享为一条 lifetime path，减少了 6 个 routing nodes/edges。[pdf:E04]（PDF 物理页 6，Fig. 5）
4. **组合式 buffer allocation。** 对每条 routing path，先检查可否用 LRB，再按 shared level 分配稀缺 GRB，剩余长路径枚举 LRB+OMB、OMB+LRB 或两个不同 PE 的 LRB 组合。目标不是最大化某一种 buffer 使用率，而是最大化被删除的 routing nodes，从而释放 PE。LRB assignment 同时生成 same-PE table（SPT），记录必须落到同一物理 PE 的 operation 集合。[pdf:E05]（PDF 物理页 8，Eqs. 1–4 与 Algorithm 1）
5. **ICS。** 对每个时间点的单节点、双节点直至最多五节点组合，比较 DFG 的共同 predecessor/successor 需求与目标互连能够提供的共同邻接。失败时，对原始节点做 recomputation/rescheduling，或拆分 shared routing node、插入 routing operation，然后重新走 temporal flow。[pdf:E06]（PDF 物理页 10，Algorithm 5）
6. **CCS。** 对每个 modulo time $j$，检查该槽内节点数是否超过 $N_{pe}$。若超出，优先移动有 schedule mobility 的节点；无可移动节点时在 critical path 插入 routing node，让部分操作延后一周期，再重新计算 temporal mapping。[pdf:E07]（PDF 物理页 11，Section 4.4）
7. **Spatial mapping。** 构造 II 层 time-extended CGRA（TEC），按 topology order 逐节点放置。候选 PE 必须与已映射前驱/后继连通，并满足 SPT；候选按“还能接触多少未占用 PE”排序。失败时回溯影响当前失败节点的先前 mapping，耗尽候选后更换 BFS 起点生成新的 node order；所有 order 都失败才令 $II \leftarrow II+1$，重新开始 temporal 与 spatial mapping。[pdf:E08]（PDF 物理页 12，Eq. 7 与 Algorithm 6）

论文的硬件边界也很明确：方法面向 fixed-point arithmetic/logic PE、邻接互连与层级 buffer 的 CGRA 模板；没有讨论浮点数精度、RTL 位宽、FPGA 综合、时钟收敛或实际片上网络拥塞模型。这些内容应视为未报告，不能从 compiler-level mapping 结果外推。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出全局最优性证明，数学的作用是把“明显不可能”编码成可快速检查的必要约束。

对分配到 GRB 的 routing path $G_i$，其 lifetime 为 $LT(G_i)$，在 modulo schedule 中需要的 GRB 槽数为

\[
N^{i}_{req}=\left\lfloor\frac{LT(G_i)}{II}\right\rfloor+1,
\qquad
\sum_i N^{i}_{req}\le N_g.
\]

直觉是同一逻辑值跨越多个 II 时，会有多个迭代实例同时存活；因此需要按 lifetime/II 计算并发占用，而不能只把“一条 path”算作一个寄存器。只有 $LT(G_i)>2$ 才值得用 GRB，因为至少要消去一个 routing node。[pdf:E05]（PDF 物理页 8，Eqs. 1–2）

对分配到 LRB 的 path $L_i$，producer 与所有 consumers 构成集合 $S_{l_i}$。必要条件包括：

\[
|S_{l_i}|\le II,
\qquad
\forall j\in[0,II),\ |M_j(S_{l_i})|\le 1,
\]

即这些必须同 PE 的操作在一个 II 内不能占用同一个 modulo slot。还要满足外部邻接需求不超过目标 PE 的最大 successor 数，并满足

\[
\left\lfloor\frac{LT(L_i)}{II}\right\rfloor+1\le N_l.
\]

前一组约束防止同一 PE 同周期执行多个 operation，后一式保证 LRB 容量足以容纳重叠迭代的值。[pdf:E05]（PDF 物理页 8，Eqs. 3–4）

ICS 的 Eqs. 5–6 把一组同周期 DFG 节点的共同 predecessor/successor 数，与 TEC 中同样数量 PE 的最大共同邻接数比较。它比只检查单节点 fan-out 更强：两个节点各自的 fan-out 都合法，它们对三组共同消费者的联合需求仍可能在 2D torus 上不可实现。CCS 则检查

\[
\forall j\in[0,II),\quad |M_j(V_m)|\le N_{pe}.
\]

这些都是必要条件，不是 spatial embeddability 的充分证明。[pdf:E07]（PDF 物理页 11，Eqs. 5–6 与 Section 4.4）

Spatial mapping 的候选优先级为

\[
Priority(v_r)=
\begin{cases}
0,&N_r<N_d,\\
N_d/N_r,&N_r\ge N_d,
\end{cases}
\]

其中 $N_d$ 是当前 DFG 节点尚未放置的 predecessors/successors 数，$N_r$ 是候选 PE slot 仍可到达的空 PE 数。先排除邻接容量不足的候选，再偏向“刚好够用”的位置，以把连接度更高的资源留给后续节点。[pdf:E08]（PDF 物理页 12，Eq. 7）

## § 7 — 实验设计与结论

**问题一：方法是否在相同硬件上得到更小 II？** 作者把本方法、REGIMap 和 RAMP 移植到同一 LLVM compilation framework，使用 28 个来自 EEMBC、MediaBench、MiBench、MachSuite、PolyBench 及 DSP、graph、dynamic programming、computer vision 应用的 loop kernels。DFG 大小为 17–154 个 operations；目标是 4×4 PE、2D torus interconnect，GRB/LRB 配置变化；所有实验在 3.60 GHz Intel Core i5 上运行，单次编译上限为一周。[pdf:E09]（PDF 物理页 13，Section 6.1）实验以 (MII/II) 表示相对理论最佳性能。Table 4 显示，在 LRB=2、GRB=4 时，REGIMap 与 RAMP 的成功样本平均值分别为 0.84、0.93，本方法对应比较值为 0.96、0.99；LRB=4、GRB=4 时，本方法为 0.97–0.98，baseline 为 0.89–0.94。[pdf:E11]（PDF 物理页 15，Table 4）结论是，在这些成功编译的循环上，本方法确实更接近 MII；论文摘要汇总为相对 state-of-the-art 提升 5.4%–14.2%。[pdf:E01]（PDF 物理页 1，Abstract）

**问题二：增大 LRB 是否足以解决问题？** 作者把 LRB 从 2 增至 4、8，GRB 固定为 4。REGIMap 的平均性能从 0.84 增至 0.89，但对 dijstra3、fil1、Maxsubstring、unstructured2 等不规则 routing paths，单纯增大 LRB 没有解决问题；本方法通过组合 buffer assignment 保持更高的 (MII/II)。28 个 kernel 的 operation 数、routing path 数和高 degree 节点数在 Table 3 中逐项报告。[pdf:E10]（PDF 物理页 14，Table 3 与 Fig. 11）

**问题三：性能损失主要发生在哪个阶段？** Fig. 12 比较 temporal mapping 后与最终 spatial mapping 后的 (MII/II)。除 karatsuba2 外，多数 kernel 的 spatial 阶段没有进一步降低性能。作者据此支持“把约束处理前移到 temporal，spatial 用快速 heuristic”这一设计选择；这是对所测 kernel 的经验结果，不是充分性证明。[pdf:E11]（PDF 物理页 15，Fig. 12 与 Section 6.3）

**问题四：固定一周时间预算时，编译是否更稳定、更快？** 本方法在各配置下均为 100% 成功；REGIMap 在 LRB=2/4/8 时均为 89.3%，RAMP 在 LRB=2 时为 85.7%、LRB=4/8 时为 92.9%。[pdf:E11]（PDF 物理页 15，Table 4）在 LRB=2、GRB=4 的共同成功样本上，REGIMap 平均 3061 s、RAMP 平均 5536 s，本方法对应为 6.10 s 与 5.85 s；论文按另一组共同成功样本汇总为相对 REGIMap 和 RAMP 快 219×、595×。[pdf:E12]（PDF 物理页 16，Sections 6.4–6.5）论文同时承认，大而不规则的 loop，或 modified DFG 的节点数接近 time-extended CGRA 容量时，reordering 会让 spatial mapping 明显变慢。[pdf:E13]（PDF 物理页 17，Section 6.5）

不得外推的范围是：实验只覆盖一个 4×4 2D torus CGRA 模板、28 个 kernel、一个 CPU 主机和最多一周的 cutoff；没有报告更大阵列、mesh/异构互连、不同 PE 功能集合、实际 FPGA 频率/面积/能耗，也没有给出跨平台置信区间。

## § 8 — Take-aways

**5 句话：**

1. CGRA modulo scheduling 的难点不是只有 PE placement，而是 value lifetime、buffer hierarchy、互连和 modulo-time 容量共同决定可映射性。
2. 论文把 buffer allocation、ICS 和 CCS 前移到 temporal mapping，让不可能条件在昂贵 spatial search 之前暴露。
3. PE、LRB、GRB、OMB 的组合使用通过消除 routing nodes 释放计算 PE，同时把 LRB 的 same-PE 约束显式交给 spatial mapper。
4. 在 28 个 kernel、4×4 torus CGRA 的实验中，本方法得到更高 (MII/II)、100% 的一周内成功率和显著更短的平均编译时间。[pdf:E11]（PDF 物理页 15，Table 4）
5. 这些结果证明了该组织方式在所测环境有效，但没有证明 temporal constraints 对任意拓扑都是充分的。

**3 句话：** 先把 routing lifetime 和资源约束处理成“空间上有希望”的 modified DFG，再做 placement/routing，比在坏输入上扩大搜索更有效。混合 buffer allocation 负责释放 PE，ICS/CCS 负责提前消除互连和并行度不可能，backtracking/reordering 负责处理剩余离散选择。论文的强证据来自 4×4 torus 上的 28 个 kernel，跨架构泛化仍未验证。

**1 句话：** 这篇论文最重要的贡献，是把 CGRA 编译的主要智能从昂贵 spatial search 前移到可解释的 temporal resource shaping。

## § 9 — 最脆弱的假设

最脆弱的假设是：论文列出的 buffer、ICS 和 CCS 必要条件足以把绝大多数“真正困难的全局空间冲突”提前消掉，使剩余 spatial mapping 可以由有限 backtracking/reordering 快速解决。若存在大量 DFG 能通过所有局部与小组合检查，却因全局 graph embedding、共享链路争用或 SPT 集合之间的联合冲突而不可嵌入，那么方法仍会在多个 topology order 上反复搜索，最终增加 II；核心的编译时间优势便可能消失。

论文给出的支持证据是，Fig. 12 中除 karatsuba2 外，spatial 阶段几乎没有继续降低 28 个 kernel 的性能；并且同一批 4×4 torus 实验都在一周内完成。[pdf:E11]（PDF 物理页 15，Fig. 12 与 Table 4）但它缺少三项关键证据：ICS 检查的组合上限最多为 5 个节点；没有构造“所有局部条件成立、全局仍不可嵌入”的 adversarial DFG；也没有在更大或非 torus 拓扑上测量 backtracking/reordering 的增长率。论文自己报告容量逼近时重排序会变慢，正说明该假设不是无条件成立。[pdf:E13]（PDF 物理页 17，Section 6.5）

## § 10 — 最小复现实验

一周内最值得复现的不是完整 LLVM 工具链，而是“temporal constraint shaping 是否显著降低 spatial search”的 DFG-level 闭环。

1. **数据。** 手工重建 Fig. 5 的 A–G DFG、Fig. 9 的单/多节点互连冲突 DFG，再加入 20–50 个随机 DAG；控制 routing lifetime、fan-out、同周期共同 successors 和 SPT 组大小。目标硬件固定为论文的 4×4 torus、LRB=2、GRB=4。
2. **实现。** 做两个 mapper：A 只做 time assignment、balancing、RPS 后进入同一个 greedy+backtracking spatial mapper；B 在 A 上增加 Eqs. 1–6 的 buffer allocation、ICS、CCS。为避免把工程差异当作算法收益，两者共享同一 spatial code、node order 和 timeout。
3. **测量。** 记录最终 II、是否映射成功、尝试的 PE candidates 数、backtrack 次数、reorder 次数、wall-clock time，以及 temporal 后 routing node 数。
4. **支持条件。** 在相同 II 下，B 对 Fig. 9 类冲突应在 spatial search 前完成重写，并以显著更少的候选尝试/回溯得到映射；随机 DFG 上，中位搜索节点数和 timeout 率也应下降，而不是仅靠提高 II 成功。
5. **反驳条件。** 若 B 与 A 的搜索规模相近，或 B 主要通过更早增加 II 才减少时间，便不能支持“constraint shaping 本身带来更高性能且更稳定编译”的核心 claim。

复现时应先逐图核对 modified DFG，而不是只看最终运行时间；否则 temporal 重写错误也可能伪装成“更快”。所需算法与约束均可从 Algorithms 1、5、6 和 Eqs. 1–7 定位。[pdf:E05]（PDF 物理页 8，Algorithm 1）[pdf:E06]（PDF 物理页 10，Algorithm 5）[pdf:E08]（PDF 物理页 12，Algorithm 6）

## § 11 — 最强反例设计

最强反例是一族 **局部可行、全局不可嵌入** 的 DFG。构造多个同 modulo time 的 producer groups，使每个单节点到五节点组合都满足 Eqs. 5–6；每个 SPT 组单独也满足 LRB 容量与 modulo-time 冲突约束；总节点数满足 CCS。但把这些 groups 通过共享 consumers 和跨组 SPT 约束连接后，任何 4×4 torus embedding 都会在一个环切割上要求超过可用的独立邻接/路由通道。它相当于为 spatial embedding 制造一个论文局部约束没有表达的全局 Hall-type bottleneck。

攻击实验应把反例规模从 2 个 group 扩展到 8、16、32 个 group，保持 MII 和局部 degree 不变，分别测 temporal 检查时间、spatial candidate attempts、backtracking/reordering 数与最终 II。若 temporal 阶段持续判定“可进入 spatial mapping”，但 spatial 搜索随规模指数式增长或频繁提高 II，就说明论文的速度提升来自 benchmark 未覆盖全局冲突，而不是方法已经抓住一般的可映射性结构。若方法仍能在近线性搜索规模内通过重写找到相同 II，则反例失败，反而加强论文机制。

这个反例直接瞄准作者的关键因果链：论文用 ICS/CCS 预测 spatial 可行性，并把轻量 spatial mapper 的成功归因于约束已被提前找出。[pdf:E07]（PDF 物理页 11，Sections 4.3–4.4）它不是泛泛地要求“更多 benchmark”，而是在寻找必要条件与全局 embeddability 之间的明确缺口。

## § 12 — Follow-up Research Bet

**主 idea：让分布式 LRB 在每个 modulo phase 临时组成“虚拟 GRB”，由编译器同时生成数据流 schedule 与 buffer-access topology。** 新的研究问题不是怎样让现有 mapping 更稳，而是：在总存储位数和总互连端口预算不增加的前提下，CGRA 能否按 loop 的 value lifetime，在不同 modulo phase 动态改变一组 LRB 的可访问范围，使本地 bank 轮流承担 local storage、multicast rendezvous 和短时 global storage？成功后，固定层级 buffer 的 CGRA 将首次能够为每个 loop 合成不同的通信/缓冲拓扑，而不是只能把值塞进预先定义的 PE/LRB/GRB/OMB 层级。

机制链条如下：lifetime-sensitive scheduling 与 RPS 先暴露每个 value 的存活区间和共享级别；论文的 Eq. 1–4 已把“跨多少个 II 同时存活”转换为 bank 容量需求，而 Fig. 4 展示同一路径可以跨多类 buffer 分段保存。[pdf:E03]（PDF 物理页 3，Fig. 4）[pdf:E05]（PDF 物理页 8，Eqs. 1–4）在新架构中，编译器不再给 routing path 选择固定 buffer 类型，而是输出 phase-indexed lease：某些周期把相邻 LRB 通过预留链路组成只持续若干 modulo slots 的 virtual global bank，随后解除并恢复本地访问。这样，高 shared-level 值获得短时全局可见性，其他值仍保留局部性；PE 不再为长 lifetime 充当 routing register，有限的永久 GRB 端口也不必覆盖最坏情况。

它改变了至少四个基本设计变量：buffer 的状态表示从“固定类型”变为“随 modulo phase 变化的 access-scope lease”；硬件映射从选择既有 bank 变为共同合成 bank role 与链路；可控变量新增每相位的聚合范围、端口借用和 multicast tree；系统边界从纯 compiler mapping 扩展为 compiler–buffer-fabric co-design。论文特异依据不是一般性的“加速编译”：其 hybrid allocation 在无 GRB 时仍达到约 0.95 的平均 (MII/II)，有 4-entry GRB 时可升到 0.96–0.99，但缺少 GRB 会显著增加 backtracking/reordering；这说明少量“全局可访问时刻”可能比永久扩大 GRB 更有价值。[pdf:E11]（PDF 物理页 15，Table 4 与 Fig. 13）

最大研究收益是用相同 SRAM 位数得到 loop-specific communication fabric，可能让更小的物理 GRB 支撑高扇出、不规则 DFG，并把 compiler-visible lifetime 直接转化为硬件结构。最大科学风险是收益其实来自隐含增加的 crossbar/port bandwidth，而不是 phase leasing；若访问范围切换的配置、仲裁和长线延迟破坏时钟或能耗，所谓虚拟 GRB 只是在面积账本外重建一个真实 GRB。

首个可证伪实验应在相同 4×4 torus、相同总 SRAM bits、相同总长链路与端口数下比较三种 RTL/周期级模型：固定 LRB+4-entry GRB、无永久 GRB 的 phase-leased LRB fabric、以及仅增加等量静态端口的对照组。对 Table 3 中 routing paths/高 degree 较多的 kernel 和规则 kernel，联合测 II、可映射率、端口利用率、配置字节、综合后的 area/Fmax 与每迭代能量。只有 phase-leased 方案在不靠额外物理带宽的条件下优于两个对照，才支持“时间化 access scope”这一核心机制；否则应接受“只是多了互连资源”的替代解释。

与论文内最近方法的实质区别是：REGIMap 只利用 LRB，RAMP 对 LRB/OMB 做较独立的选择，本文方法对固定的 PE/LRB/GRB/OMB 做 hybrid path assignment；这个 research bet 则把 buffer 类型本身变成随 modulo phase 变化的硬件状态，并把研究对象从 mapping algorithm 改为编译器可合成的 buffer topology。[pdf:E02]（PDF 物理页 2，贡献 2）由于本卡未对 2020 年后的 compiler-directed reconfigurable memory fabric 做外部检索，这只是候选判断，不声称 novelty。

**Wild-card alternative：** 把“通过所有局部 ICS/CCS 检查但全局不可嵌入”的 DFG 当作新的数据生成目标，用可验证的 graph grammar 主动合成空间阻塞族，从经验 benchmark 评测转向发现 CGRA embeddability 的尺度律与缺失不变量。
