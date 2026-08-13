# Large-scale periodic scheduling in time-sensitive networks

- 作者：Marek Vlk、Kateřina Brejchová、Zdeněk Hanzálek、Siyu Tang
- 出处：*Computers & Operations Research*, 137 (2022), 105512
- 年份：2022（2021 年在线发表）
- DOI：10.1016/j.cor.2021.105512
- Zotero key：JHKPT5RD
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 论文解决的是 IEEE 802.1Qbv Time-Sensitive Networking（TSN）中的离线周期调度：给定网络拓扑、已确定的 flow 路径、每条 flow 的 period、release date、deadline、payload，以及交换机队列和链路参数，给每个 frame 的第一次周期出现分配发送起点和 egress queue，使其所有周期副本同时满足 release/deadline、链路互斥、逐跳 precedence、zero-jitter 和 frame isolation constraint（FIC）。IEEE 标准规定了 gate 和 queue 如何按时间表工作，却不规定怎样计算这个时间表；因此，调度器本身是把确定性 Ethernet 从规范变成可部署配置的关键环节。[pdf:E01]（PDF 物理页 1，Abstract 与 Section 1）

重要性不只是“快一点”。工业控制和航空网络要让消息延迟及其抖动可预期；网络规模增大后，如果设计阶段算不出一张可行表，IEEE 802.1Qbv 的实时能力就无法使用。作者给出的既有结果显示，精调的 SMT/ILP 方法在数十节点、数十至数百 flow 时就可能耗费数小时，而本文要把问题推进到 2000 个节点、超过 10,000 条 flow 和 90,000 余个 frame occurrence 的量级。[pdf:E01]（PDF 物理页 1，Introduction）

## § 2 — 前人工作与不足

**相关文献中的已有结论，按本文综述。** 早期 TSN scheduler 多把约束编码成 SMT、ILP 或 constraint programming，再交给通用 solver。论文列举的代表性规模包括：Craciunas 等的 SMT scheduler 在 5 个 switch、7 个 end-station、最多 100 条 flow（1490 个 occurrence）上用到 5 小时；Oliver 等在 10 个 switch、50 个 end-station、最多 50 条 flow（264 个 occurrence）上用到 40 小时；dos Santos 等的 10-switch、50-end-station、10-multicast-flow 实例用到 80 小时；Vlk 等的 ILP scheduler 在 4 个 switch、16 个 end-station、少于 250 条 flow（不超过 2000 个 occurrence）时接近 10 分钟。[pdf:E01]（PDF 物理页 1，Introduction）这些方法表达力强，但变量和析取约束随 flow、路径长度及周期副本迅速膨胀，通用 solver 的搜索并没有利用本问题特有的周期结构。

已有 heuristic 的另一条路线是 EDF、as-soon-as-possible、Tabu、GRASP 或 no-wait scheduling。其不足不是简单的“没有考虑某个约束”：no-wait 会禁止 frame 在交换机 queue 中等待，删掉一块真实的调度自由度；one-pass 方法一旦早期放置不合适，通常无法撤销并重排；一些方法还假设 release time 为 0、忽略 jitter，或只用一个 TT queue。本文进一步把 TSN scheduling 与 periodic job-shop、blocking operation、unit-capacity buffer 联系起来，并指出 TSN 特有的 queue/gate 语义使已有 job-shop 方法不能直接照搬。[pdf:E02]（PDF 物理页 2，Sections 2.2–2.4）

## § 3 — 重建作者的思考路径

在本文提出 EPIC 之前，可以沿以下线索走到它。第一，调度变量其实很少：zero-jitter 让一条 flow 在某链路上的所有 occurrence 都由第一个 occurrence 的 start time 决定；但每一次一致性检查仍要顾及整个 hyper-period。第二，release/deadline 和逐跳 precedence 可收缩成 start-time domain 的上下界，真正困难的是同链路 resource conflict 与 FIC。第三，periodic resource conflict 可用 period 的 greatest common divisor（gcd）和 Bézout identity 检查，不必逐一枚举全部时间点。第四，constraint satisfaction 领域已有 conflict-directed backjumping：失败时不用退回上一个变量，而可退到真正造成冲突的旧变量。[pdf:E02]（PDF 物理页 2，Section 2.4）

接着出现本文特有的困难：FIC 是涉及两条 flow 的两个 outgoing frame 及其两个 predecessor 的四-frame 关系，当前变量失败时，真正该移动的可能是任一 predecessor；局部 conflict set 可能在多次 backjump 后丢失因果链。于是，一个自然路线是：保留局部 conflict set，再补一个 global conflict set；用 domain 语义直接跳到“下一个可能解除当前冲突”的值；同时用冲突次数动态改变变量顺序，让搜索尽早处理最难的 frame。**基于证据的推断：** EPIC 可以理解为“把通用 CSP 的回溯骨架，改造成认识 TSN 约束语义的专用搜索器”，而不是换一个 solver。[pdf:E05]（PDF 物理页 5，FIC 与 alternative graph 解释）

## § 4 — 核心 Intuition

EPIC 的核心 intuition 是：不要盲目遍历完整 schedule，也不要一次贪心定死；先构造 partial schedule，每次只放一个 frame，一旦发生冲突，就记录“谁导致了失败”，直接跳回最相关的旧 frame，并把该冲突用于重排后续变量。zero-jitter、gcd 检查和上下界传播把每次判断压缩到本问题的结构上；restarts 则让累积的 conflict counts 把下一轮搜索重新聚焦到反复出问题的 frame。[pdf:E06]（PDF 物理页 6，Section 5 与 Fig. 3）

## § 5 — 具体方法与完整 Pipeline

以论文的三-flow 例子为线索，完整 pipeline 如下。

1. **预处理输入。** 网络是有向图；每个有向 link 是一个 unary scheduling resource，switch 本身可通过并行端口同时收发。flow 给出 talker、listener、payload、period、deadline、release date；路径预先用 breadth-first search 取 hop 数最少的路径。调度变量是每条 flow 在每条路径 link 上第一个 frame occurrence 的 start time `s` 和 queue ID `λ`；后续 occurrence 的 start time由 `s + kT` 推出。[pdf:E03]（PDF 物理页 3，Sections 3.1–3.3 与 Table 1）
2. **建立可行域。** 从 talker 向后传播 earliest start time，从 listener 向前传播 latest start time，把 release、deadline、link delay、switch delay、synchronization error 和相邻 hop 的 transmission duration 纳入上下界。若任何 frame 的 `est > lst`，立即判定 infeasible。[pdf:E07]（PDF 物理页 7，Section 5.1）
3. **动态选 frame。** 所有未赋值 frame 放在 priority queue。最初倾向选择 deadline 更早、slack 更小且 precedence order 更前的 frame；搜索中则用 conflict count 降低反复冲突 frame 的 criterion，使它们更早被处理。[pdf:E08]（PDF 物理页 8，Section 5.2.2 与 Eq. 20）
4. **尝试一个 `(start time, queue)`。** 先从当前下界和 queue 0 开始。release/deadline 与 precedence 已由 domain propagation 保证，在线只检查同一 link 上的 FIC 和 resource conflict。FIC 不满足时，先试下一 queue；resource conflict 不满足时，利用 gcd/Bézout 直接算出能越过重叠区间的下一个 start time，而不是逐微秒加一。[pdf:E09]（PDF 物理页 9，Section 5.2.4）
5. **成功则前进，失败则 backjump。** 若某 frame 的 domain 已耗尽，算法从 local conflict set 与 global conflict set 中选最近赋值的冲突 frame，退回该处，清掉其后的赋值，并合并 conflict 信息；若两类 conflict set 都为空，则返回 infeasible。[pdf:E07]（PDF 物理页 7，Fig. 4 与 Section 5.2.1）
6. **周期性 restart。** 初始允许 64 次 backjump；达到阈值后清空当前 partial schedule，但保留每个 frame 的 conflict count。下一轮因 variable order 已改变，不会机械重复原搜索；阈值每次乘 1.3，因此完整版本不会永远停留在浅层搜索。[pdf:E09]（PDF 物理页 9，Section 5.2.5）
7. **可选 heuristic acceleration。** EPIC_H 删除 global conflict set；EPIC_T 再把 start-time 增量改为 `T_i/100`；EPIC_C 则用 circular buffer 观察搜索是否困在少量 index 上，并自适应放大增量。这些版本跳过部分信息或 domain value，换取速度，因而不再 complete。[pdf:E10]（PDF 物理页 10，Section 5.3）
8. **输出。** 所有 frame 均赋值后，输出每个 link 的周期 start time 与 queue ID；它们可进一步转换成 IEEE 802.1Qbv 的 gate control schedule。论文未报告 FPGA 映射、RTL、固定点数值格式或在线硬件执行，因为研究对象是 CPU 上的离线组合调度器，而不是实时网络仿真器或硬件加速器。

附录把上述 pipeline 在三-flow 例子中逐步展开：global conflict set 让 exact EPIC 在局部 conflict set 已空时仍能追溯到最早的 `f_{0,5,3}`，把它从 `10|30|50` 移到 `11|31|51`，随后找到 Fig. 2 的可行解；不带 global set 的 heuristic 在同一状态会返回“solution not found”。[pdf:E14]（PDF 物理页 14，Appendix 起始）[pdf:E15]（PDF 物理页 15，Appendix 结尾）

## § 6 — 核心数学推导（无形式化数学则跳过）

先固定符号。`T_i` 是 flow `i` 的 period，`p_i` 是 payload，`c_{a,b}` 是 link speed，`L_{i,a,b}=8p_i/c_{a,b}` 是 transmission duration，`s_{i,a,b}` 是第一个 occurrence 的 start time，`λ_{i,a,b}` 是 queue ID。整个 schedule 的 hyper-period 为

\[
HP=\operatorname{lcm}\{T_i\mid i\in\mathcal F\},\qquad
s^{(k)}_{i,a,b}=s_{i,a,b}+kT_i.
\]

因此，算法只搜索首个 occurrence，却能表示严格周期的全部 occurrence。[pdf:E03]（PDF 物理页 3，Section 3.2）

release/deadline 约束把第一跳和最后一跳夹在时间窗内：

\[
s_{i,t_i,t'_i}\ge r_i,\qquad
s_{i,l'_i,l_i}\le \tilde d_i-L_{i,l'_i,l_i}-d_{l'_i,l_i}.
\]

逐跳 precedence 则是

\[
s_{i,a,b}\ge s_{i,x,a}+L_{i,x,a}+d_{x,a}+d_a+\delta,
\]

即 frame 完整到达前一 switch、经过 link delay、switching delay 和最大时钟偏差后，才可从下一 link 发出。[pdf:E04]（PDF 物理页 4，Eqs. 1–3）

resource constraint 的关键不是把 hyper-period 中每对 occurrence 都展开。对同一 link 上 flow `i,j`，令

\[
g=\gcd(T_i,T_j),\quad
d_1=(s_j-s_i)\bmod g,\quad
d_2=(s_i-s_j)\bmod g.
\]

只要同时满足 `d_1 ≥ L_i` 与 `d_2 ≥ L_j`，两个无限周期的 transmission 区间就不重叠；任一条件失败时，差额也直接给出下一个值得尝试的 start time。这是 Bézout identity 在本算法中产生加速的地方。[pdf:E09]（PDF 物理页 9，Section 5.2.4）

FIC 比 resource constraint 更难。对进入 switch `a` 的 predecessor link `(x,a)`、`(y,a)`，以及从同一 egress link `(a,b)` 发出的两条 flow，在 occurrence `α,β` 上必须满足

\[
\begin{aligned}
&(s_{i,a,b}+\alpha T_i\le s_{j,y,a}+\beta T_j+L_{j,y,a}+d_{y,a}-\delta)\\
\lor{}&(s_{j,a,b}+\beta T_j\le s_{i,x,a}+\alpha T_i+L_{i,x,a}+d_{x,a}-\delta)\\
\lor{}&(\lambda_{i,a,b}\ne\lambda_{j,a,b}).
\end{aligned}
\]

普通语言是：如果两帧进同一 egress queue，则必须有一帧已离队后另一帧才完全入队；否则就分配到不同 queue。FIC 让冲突原因跨越四个 frame，因此需要 global conflict set。[pdf:E05]（PDF 物理页 5，Eq. 4 与 Section 4）

动态 variable ordering 使用

\[
\operatorname{crit}(f_{i,a,b})=
\frac{\tilde d_i\,(lst_{i,a,b}-est_{i,a,b})+\operatorname{order}(f_{i,a,b})}
{\operatorname{conflicts}(f_{i,a,b})}.
\]

最小 criterion 优先：slack 小、deadline 早、precedence 靠前或历史冲突多的 frame 更早被选中。实现为每个 frame 保存 conflict set，因此空间复杂度为 frame 数的平方；最坏时间复杂度仍是 exponential，论文没有给出 polynomial guarantee。[pdf:E08]（PDF 物理页 8，Eq. 20）[pdf:E09]（PDF 物理页 9，Section 5.2.7）

## § 7 — 实验设计与结论

**问题 1：EPIC 是否比通用 solver 和常见 heuristic 更可扩展？** 实验比较 EDF、GRASP、Z3 4.8.8 的 SMT、Gurobi 9.0 的 ILP、exact EPIC，以及 EPIC_H/EPIC_T/EPIC_C。所有 solver 禁止并行，单实例时限 1 小时；机器为双路 Intel Xeon E5-2690 v4、每 CPU 14 核、2.6 GHz、256 GB DDR4 ECC。production-line 数据集含 9000 个实例，覆盖 100、250、500、1000、2000 节点，两种 ring-plus-tree/line 拓扑和三组 period；flow 上限随规模从 1500 增至 12,000。[pdf:E10]（PDF 物理页 10，Section 6 与 6.1）

答案是：在“1 小时内找到可行表”的指标上，Table 4 的总体平均成功率为 EDF 0.1%、GRASP 10.8%、ILP 32.2%、EPIC 41.5%、EPIC_H 43.3%、EPIC_T 57.6%、EPIC_C 56.1%；SMT 因 500 节点实例有时超过 14 小时，只报告到 250 节点，不能计算同口径总体均值。ILP 找到的最大实例为 5268 条 flow、45,564 个 occurrence；EPIC 系列达到 10,812 条 flow、93,814 个 occurrence，flow 数高 105% 以上。EPIC 找到而 EPIC_H 未找到的情况为 86/9000，低于 0.96%，说明删除 global set 在该数据分布上通常以少量 completeness 损失换来速度。[pdf:E11]（PDF 物理页 11，Table 4 与相邻正文）

**问题 2：优势只是“耗满 1 小时多碰运气”吗？** Fig. 6–8 分别按 flow 数展示 schedulability、所有实例平均求解时间、仅成功实例平均求解时间。EPIC_T/EPIC_C 的 schedulability 曲线延伸到更大 flow 数；成功实例上的平均时间通常明显低于 ILP。把时限延到 14,400 秒后，大部分可解实例仍集中在很短时间内完成，超过 3600 秒只带来很小的额外成功率；因此 heuristic 的主要收益是更早进入有希望的搜索区域，而不是单纯多等。[pdf:E12]（PDF 物理页 12，Figs. 6–8 与相邻正文）

**问题 3：conflict count 与 restart 真有作用吗？** 100-node 实验中，完整 criterion `SLK+EDF+Conf` 的 schedulability 从无 restart 的 42.5% 提高到有 restart 的 55.9%；不含 conflict count 的 criterion 在 restart 后变量顺序不变，只会重复相同搜索，因此没有报告收益。论文据此把“保留 conflict count、丢弃 partial schedule”而非 restart 本身视为有效机制。[pdf:E13]（PDF 物理页 13，Table 5）

**问题 4：负载结构和领域变化会怎样？** Fig. 9 显示 maximum link utilization 超过约 0.2 后成功率开始明显下降。20 个 avionic 实例覆盖 1267–2786 条 flow、两种 node delay 和原 period/缩短 100 倍的 period；原始设置下 EPIC_H/EPIC_T/EPIC_C 均解出 5/5，而 EDF、GRASP、SMT、ILP 为 0/5；最苛刻的 `node delay=10, period=P4/100` 下所有方法均为 0/5。它证明算法并非无条件扩展，deadline slack 与 period 结构仍决定可解性。[pdf:E13]（PDF 物理页 13，Fig. 9 与 Table 6）

**问题 5：允许 queue 中等待是否必要？** 把 no-wait 加回全部实例后，平均成功率从 41.5% 降到 18.7%（EPIC）、43.3% 降到 25.1%（EPIC_H）、57.6% 降到 28.3%（EPIC_T）、56.1% 降到 25.5%（EPIC_C）。这直接支持论文的一个重要工程判断：等待和多 queue 不是实现噪声，而是大规模可调度性的核心自由度。[pdf:E13]（PDF 物理页 13，Section 6.2 前正文）

## § 8 — Take-aways

**5 句话。**

1. 这篇论文把 TSN 周期调度从通用 SMT/ILP 建模转成利用 zero-jitter、gcd 和 queue/FIC 语义的专用搜索。
2. EPIC 用 local/global conflict sets、backjump、动态 frame ordering 和 restart 在 partial schedule 空间中导航。
3. exact 版本保持 completeness；三个 heuristic 通过删除 global 信息或跳过 start-time value 换取更高的一小时成功率。
4. 9000 个 production-line 实例和 20 个 avionic 实例显示它能处理到 2000 节点、10,812 条 flow、93,814 个 occurrence，但成功率会随利用率、period 与 delay 结构恶化。
5. 最有工程含义的结果不只是“更快”，还包括 no-wait 使成功率大幅下降，说明 queue 等待是需要被保留的设计变量。

**3 句话。** EPIC 是一个理解 TSN 周期约束的 conflict-directed scheduler。它在本文数据上把可处理规模推到上万 flow，并以少量 completeness 换取更高 heuristic 成功率。它的外推边界主要在 period/hyper-period 结构、负载与 deadline slack，而不只是节点数。

**1 句话。** 用冲突解释搜索，而不是把完整约束模型丢给通用 solver，是本文实现大规模 TSN 周期调度的关键。

## § 9 — 最脆弱的假设

最脆弱的假设是：**大规模实例的 period 集合仍具有较小、规则的 hyper-period，使 FIC 的周期副本检查不会压倒搜索。** Algorithm 2 对一对同 link frame 的 FIC 会遍历 `lcm(T_i,T_j)/T_i` 与 `lcm(T_i,T_j)/T_j` 个 occurrence 组合；resource conflict 虽可用 gcd 常数级判断，FIC 并未得到同样的数论压缩。[pdf:E08]（PDF 物理页 8，Algorithm 2）

论文的 production-line period 集只有 3–5 个值，hyper-period 分别为 2000、2000、4000 μs；avionic period 集也是高度整齐的 12,500–200,000 μs 倍数链。实验没有保持 flow 数、link utilization、deadline slack 不变而只把 period 换成近互质值，因此“2000 节点、上万 flow”不能自动外推到 hyper-period 极大的 traffic mix。[pdf:E11]（PDF 物理页 11，Table 3）

若该假设失效，每次 consistency check 的成本会因 occurrence pair 数增长，conflict count 可能反映的是“检查贵”而非“结构难”，restart 也无法消除单次检查成本。论文承认最坏时间是 exponential，但没有单独测量 hyper-period 对吞吐的尺度律；这是核心 scalability claim 最大的未闭合处，而不是一个外围实现细节。

## § 10 — 最小复现实验

一周内最有价值的最小复现不是重建完整 2000-node benchmark，而是验证“conflict-directed ordering + restart 是否真的贡献成功率”。

使用论文公开的 production-line instance 生成方式，固定 100-node HYBRID_TREE 和 HYBRID_LINE，各生成或抽取 50 个实例；period 使用 Table 3 的 `P1–P3`，保持每实例 1 小时、单线程。直接运行作者的 EPIC 代码或按 Algorithms 1–2 实现最小版本，只比较三项：`SLK+EDF+Conf` 无 restart、同 criterion 有 restart、删除 conflict count 后有 restart。记录 60 秒和 3600 秒内的 solved ratio、backjump 数、每次 restart 前最大 assigned-frame 数。

支持 claim 的结果是：有 conflict count 的 restart 版本在相同实例、相同时间预算下明显提高 solved ratio，并且 restart 后最大搜索深度呈上升趋势；反驳 claim 的结果是：优势在不同随机种子下消失，或只是由某个起始 variable order 偶然造成。将 Table 5 的 42.5% 对 55.9% 作为复现目标区间，但不要求逐点相同，因为随机实例和实现细节可能不同。[pdf:E13]（PDF 物理页 13，Table 5）

## § 11 — 最强反例设计

最强反例是构造一组**节点数、flow 数、路径长度、payload、maximum link utilization 和 deadline slack 分布都匹配原 benchmark，但 period 两两近互质**的实例。设置两组对照：A 组使用 `{500,1000,2000}` 这类 harmonic period，B 组使用邻近的 prime-like period，使单条 flow 的平均发送频率和总链路负载相近，却把 pairwise lcm 与全局 hyper-period 放大数个数量级。

分别测 EPIC_T、EPIC_C 和一个不显式枚举 FIC occurrence pair 的 alternative encoding，记录每次 `Check` 的 occurrence-pair 数、单位 backjump 时间、3600 秒 solved ratio。如果 B 组的 EPIC 成功率和每秒搜索步数崩塌，而对照方法下降显著更小，就能把性能来源从“conflict-directed search 普遍适合大规模 TSN”改写为“它适合 period 结构规整的大规模 TSN”。反之，若 EPIC 在 B 组仍保持接近的单位时间搜索深度，就能反驳 §9 的担忧。这个反例直接攻击核心 scalability mechanism，而不是泛泛增加网络负载。

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty：把“typed conflict hypergraph”变成可组合 TSN schedule 的生成表示。** 新研究问题是：能否不再逐 frame 构造一张全局 schedule，而是从 EPIC 运行中提取可复用的“相位—queue motif”，在重复的 ring/tree/line 网络模块之间组合它们，从而一次生成一族规模和 traffic matrix 可变化的 schedule？这首次会让 scheduler 的输出从“一次性完整时间表”变成“可迁移、可拼接的周期结构单元”。

核心机制是把两类冲突编码成不同 hyperedge：resource edge 由 `gcd(T_i,T_j)` 上的相位间隔定义，FIC edge 则连接两个 outgoing frame 及其两个 predecessor，并携带 queue-separation 或 temporal-order 选择；多次 backjump 和 conflict count 给出哪些 edge 构成稳定 conflict community。算法先在局部 community 内求一个 phase/queue motif，再只用少量 boundary phase variable 连接网络模块。它改变了至少四个基本设计变量：schedule representation（全局 frame 表变为 typed motif）、优化对象（单实例可行性变为 motif 可组合性）、系统边界（固定全局搜索变为模块内生成加模块间拼接）、评价对象（单次 solved ratio 增加跨规模/traffic-matrix 的复用率与组合成本）。论文的 gcd resource test、四-frame FIC、conflict-directed ordering 是表示层依据；HYBRID_TREE/HYBRID_LINE 的重复模块、EPIC_T/EPIC_C 在 2000-node 实例上的优势，以及 no-wait 导致成功率近乎减半，说明“相位与 queue 的联合局部结构”确实承载了可调度性，而不只是普通图分区。[pdf:E06]（PDF 物理页 6，Fig. 3 与 Section 5）[pdf:E11]（PDF 物理页 11，Fig. 5 与 Table 4）[pdf:E13]（PDF 物理页 13，no-wait 对比）

最大的研究收益是把大型离线 scheduling 从每个新 traffic set 都重搜一次，变成可解释的模块化生成，并可能让 topology expansion 与 traffic family 共享计算。最大的科学风险是：motif 只是重复拓扑带来的普通 decomposition 效果，typed conflict 表示并没有额外作用；而跨 ring 的 20% flow 可能制造足够多的长程 FIC edge，使任何局部组合都退化为全局搜索。

首个证伪实验应固定 500-node 与 2000-node HYBRID_TREE/HYBRID_LINE，分别比较三种同规模 partition：随机模块、仅按物理拓扑模块、按 typed conflict hypergraph 得到的 motif。训练或提取 motif 时只看一组 traffic matrix，测试时改变 20% 跨 ring flow 的端点与 period；测新实例生成时间、solved ratio、boundary variable 数和复用 motif 比例。若 conflict motif 只在原 traffic matrix 上有效，或不优于物理拓扑分区，就否定核心机制；若它在拓扑相同但 flow 重排后仍保持更少 boundary variable 与更高 solved ratio，才能把收益归因于 typed conflict representation，而不是普通 decomposition。本文只提到 hierarchical decomposition 与后续 joint routing/scheduling，没有系统检索过“可组合 conflict motif”最近工作，因此与最近工作的差异目前仅是候选判断。

**Wild-card alternative：** 把 application sampling period 本身变成可控变量，利用 gcd phase lattice 联合设计控制任务周期与 TSN queue phase，使网络第一次能主动塑造而非被动接受 hyper-period 结构；这改变的是时间模型和跨控制—网络系统边界，而不是增加一个 scheduler wrapper。
