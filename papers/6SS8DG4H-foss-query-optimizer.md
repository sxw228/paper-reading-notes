# FOSS: A Self-Learned Doctor for Query Optimizer

作者：Kai Zhong、Luming Sun、Tao Ji、Cuiping Li、Hong Chen（源 PDF 物理页 1，标题与作者区）[pdf:E01]

出处：IEEE International Conference on Data Engineering 2024（ICDE 2024，论文 accepted version；源 PDF 物理页 1，页脚）[pdf:E02]

年份：2024

DOI：10.1109/ICDE60146.2024.00330（源 PDF 物理页 1，页脚）[pdf:E02]

Zotero key：6SS8DG4H

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的核心问题是：**能否不从零构造查询计划，也不把搜索限制在少量粗粒度 hint 上，而是从传统 query optimizer 已经给出的计划出发，学习如何用少数细粒度动作把其中的坏节点“治好”**。FOSS 将这个范式称为 plan-doctor：planner 逐步修改原计划，asymmetric advantage model（AAM，非对称优势模型）比较候选计划，模拟环境再用廉价的计划生成和学习到的相对性能反馈扩充训练经验。摘要直接把低训练效率和受限搜索空间列为现有 learned query optimizer 的两类主要矛盾，并报告 FOSS 在 JOB、TPC-DS、Stack 上相对 PostgreSQL 的总延迟 speedup 为 1.15×–8.33×（源 PDF 物理页 1，Abstract）[pdf:E01]。

问题重要，是因为传统 optimizer 面对的是组合爆炸：即使只考虑 left-deep join order，搜索空间也按 $O(n!)$ 增长；再加入 bushy tree、join method 和 access path 后更大。与此同时，cardinality/cost estimator 的误差会把搜索导向差计划，而传统 optimizer 又不会从历史执行中学习，同类错误可能重复发生（源 PDF 物理页 1，Introduction）[pdf:E02]。因此，真正有价值的不是再训练一个完全替代 DBMS 的模型，而是找到一个工程折中点：保留传统 optimizer 的规则、可执行性和低成本 plan completion，把学习能力集中在“哪里错了、改哪一步、哪个候选更好”上。

论文的贡献边界也应先说清：当前 FOSS **只考虑 left-deep plans，并把可学习修改限制为 join order 与 join method**；bushy topology、scan/access-path 修改没有进入当前 action space（源 PDF 物理页 4，Section III）[pdf:E10]。所以它解决的是一个重要但受限的子问题，而不是一般意义上完整的 physical plan synthesis。

## § 2 — 前人工作与不足

以下归纳是论文对相关工作的直接分类，而不是本卡进行的包外文献复核。

作者把既有 learned query optimization 粗分成两类。第一类是 **plan-constructor**，代表性工作包括 Neo、Balsa、Loger 等：agent 从表或 partial plan 开始，逐步拼出完整计划。它的优势是搜索自由度高，但论文指出三个结构性成本：一是 learning from scratch，先要重新学会传统 optimizer 已掌握的基本规划能力；二是高质量 experience 难采，cost model 有偏、真实执行又昂贵；三是 intermediate partial plan 往往无法直接执行和评价，形成 sparse reward（源 PDF 物理页 1–2，Section I-A 的 C1–C3）[pdf:E03][pdf:E04]。

第二类是 **plan-steerer**，代表性工作包括 Bao、HybridQO 等：它们保留传统 optimizer，通过 hint 或候选 hint set 改变其行为，再用 learned model 选计划。论文认为这条路线更实用，但有三类不足：hint set 仍需要专家设计；hint 粗粒度会限制可达计划空间；增加 hint 虽可提高找到好计划的概率，却同步增加优化时间，形成 search quality 与 planning overhead 的权衡（源 PDF 物理页 2，Section I-A 的 S1–S3）[pdf:E04]。

FOSS 的定位是第三种 **whitebox-expertise / plan-doctor**：不丢弃传统 optimizer，也不只在其外部施加粗 hint，而是显式取出原计划的 join order 与 join method，用可解释的 Swap/Override 动作做局部手术。作者的直接论点是，传统计划虽然可能因估计误差而差，但“更好的计划常可由有限次修改找回”（源 PDF 物理页 2，Section I-B）[pdf:E05]。这个定位真正改变的不是是否使用 DRL，而是**学习对象从“生成整棵树”或“选一个 hint”变成“学习计划编辑序列”**。

需要保留一层批评：作者在结论中把 FOSS 称为首个通过细粒度修改原计划并借助模拟环境自举的 learned optimizer，这是论文的直接 novelty claim；本任务禁止包外检索，因此本卡不独立认证其首创性（源 PDF 物理页 12，Conclusion）[pdf:E28]。

## § 3 — 重建作者的思考路径

下面是**基于论文证据的思考路径重建**，不是作者逐句陈述。

第一步，从传统 optimizer 的失败方式出发：计划整体并非随机，通常已包含大量专家知识，但少数 cardinality/cost error 可能让一个关键 join order 或 join method 选择失误。论文给出的 JOB Query 1b 是最强直觉证据：PostgreSQL 原计划执行 100.67 ms，错误地在 `it` 与 `mi_idx` 之间采用 hash join；若先改成 nested-loop join，再调整两表位置，执行延迟降到 0.27 ms（源 PDF 物理页 2，Section I-B 示例）[pdf:E05][pdf:E06]。这说明至少在某些查询上，性能差距集中在少数离散决策，而不是整棵计划都要推倒重来。

第二步，把 plan-constructor 与 plan-steerer 的缺点并排看：从零构造浪费已有专家知识，粗 hint 又不能精确定位错误。自然的中间路线是：从 original plan 起步，定义一套足够细、但仍能被 DBMS 补全为合法 complete plan 的编辑操作。这样每一步之后都有可执行计划，reward 不必等到整棵树构造完成才出现。

第三步，意识到真实执行仍然太贵。既然给定 query 和不完整约束 ICP 后，传统 optimizer 可以低成本补全 complete plan，那么 state transition 不必学习；真正昂贵的是“这个新计划比旧计划好多少”。于是可以让 DBMS optimizer 充当 transition model，让一个 pairwise AAM 充当 learned reward model，组合成 simulated environment（源 PDF 物理页 8，Section V-A）[pdf:E17]。

第四步，绝对 latency prediction 在动态 workload 下难稳定，计划间的**粗粒度相对优势**可能更容易学习。论文先把相对延迟改善离散成 ordinal score，再让 AAM 输入有方向的计划对；这既服务于训练 reward，也服务于最终候选选择（源 PDF 物理页 5、7，Eq. (2) 与 Section IV-B）[pdf:E12][pdf:E15]。

最终形成的设计闭环是：原计划提供强起点，编辑动作提供可执行的 dense intermediate states，AAM 提供廉价相对反馈，少量真实执行不断纠正 AAM，模拟经验扩大 planner 的探索量。Fig. 1 把 planner、AAM、simulated experience pool、真实 DBMS executor 画成同一个自举循环（源 PDF 物理页 3，Fig. 1）[pdf:E07]。

## § 4 — 核心 Intuition

FOSS 的核心 intuition 是：**不要重新成为一个 query optimizer，而要成为传统 optimizer 的局部诊断与修复器**。原计划通常已在一个相对合理的区域，只需学习少数 table swap 和 join-method override，就可能把估计误差造成的性能瓶颈移除；Query 1b 从 100.67 ms 降至 0.27 ms 是作者用来说明这一点的实例（源 PDF 物理页 2，Section I-B）[pdf:E05][pdf:E06]。每次修改都交回 DBMS 补全成完整计划，因此 agent 始终在合法、可执行的计划之间移动。真实执行太慢时，则用 AAM 学习“右计划相对左计划是否明显更好”，把这种相对判断当作模拟 reward，再以少量真实结果持续校正。

## § 5 — 具体方法与完整 Pipeline

以论文的 Query 1b 为例，输入是一条 SQL，输出是从一组逐步修改得到的 candidates 中选出的 execution plan。完整 pipeline 如下。

1. **取得专家起点。** PostgreSQL optimizer 先为 query $Q$ 生成 complete plan $CP$。FOSS 从中抽取只保留 join order 与 join method 的 incomplete plan $ICP$；scan operator 等其余节点仍由传统 optimizer 根据 ICP 补全。当前实现只处理 left-deep plan（源 PDF 物理页 4，Section III）[pdf:E10]。

2. **编码 state。** state 由 complete-plan encoding 和当前 step ratio 拼接。plan encoder 基于 QueryFormer 的 tree Transformer，节点特征包括 operator、predicate、join、table，并额外编码 node height 与四类结构位置（left、right、no-sibling、root）；attention mask 阻断计划树中不可达节点之间的注意力（源 PDF 物理页 6–7，Section IV-A）[pdf:E14][pdf:E15]。

3. **选择细粒度 action。** planner 有两类动作：`Swap(T_l,T_r)` 交换两个 table 的位置，`Override(O_i,Op_j)` 把某个 join node 改为指定 join method。action mask 排除 query graph 下的非法 swap；若刚执行 swap，下一步只允许修改相关父 join method，以剪枝 action space（源 PDF 物理页 5，Section III-Action）[pdf:E11]。Fig. 2 展示了从 ICP、state network、action selector 到 DBMS optimizer、reward 和 experience pool 的闭环（源 PDF 物理页 4，Fig. 2）[pdf:E09]。

4. **由 DBMS 完成状态转移。** action 先修改 ICP，再把 $(Q,ICP)$ 交给 DBMS optimizer $\Gamma_p$，得到新的合法 complete plan $CP_t$。在真实环境中执行该计划取得 latency；在模拟环境中不执行，由 AAM 估计相对优势。Algorithm 1 还维护本 episode 中估计的最佳计划，并收集 $(state,action,reward,state')$ 更新 agent（源 PDF 物理页 6，Algorithm 1 与 Environment）[pdf:E13]。

5. **用 reward 约束“有效且短”的编辑路径。** positive bounty 奖励新计划相对当前最佳候选的改善，并在 episode 结束时加大最终计划的权重；penalty 则惩罚用冗余动作绕路到达同一 ICP。论文固定 episode-bounty 权重 $\eta=12$、penalty 系数 $\gamma=2$（源 PDF 物理页 5–6，Reward 与 Agent）[pdf:E12][pdf:E13]。

6. **用 AAM 做有方向的候选比较。** 同一 state network 分别编码 left/right plan，再加入不同 position embedding，经两个 fully connected layers 输出三档优势 score。由于输入位置不同且中间做有方向的差分，模型学习的是“$CP_r$ 相对 $CP_l$ 的优势”，不是无方向相似度（源 PDF 物理页 7，Section IV-B）[pdf:E15]。

7. **真实执行与模拟学习并发。** planner training、plan execution、AAM training 和 validation/test 交错运行。真实执行结果进入 execution buffer，重组为 plan-pair supervision 更新 AAM；planner 大量与 $\hat E(\Gamma_p,\theta_{adv})$ 交互产生 simulated experiences；AAM 认为 promising 的计划会被送回真实环境验证，及时纠正估计误差（源 PDF 物理页 8，Fig. 3 与 Section V-B）[pdf:E17]。

8. **控制坏计划的采样成本。** 新计划执行超过 original-plan latency 的 1.5 倍即 timeout；构造 AAM 样本时，若一对计划都 timeout 则过滤。作者明确承认，这可能减少 AAM 样本并降低预测准确率，但能显著加快数据收集（源 PDF 物理页 8，dynamic timeout）[pdf:E18]。

9. **推理输出。** 对一个 query，planner 从 original plan 出发生成按时间排序的 candidate plans，AAM 逐对比较并选择估计最优者作为最终 execution plan。系统级数据流可见 Fig. 1，planner/AAM/real executor 的职责边界见源 PDF 物理页 3（Fig. 1 与 System Overview）[pdf:E07][pdf:E08]。

实际执行平台是 Ubuntu 18.04、Intel Xeon Gold 5118 2.30 GHz、256 GB memory、GeForce RTX 3090；FOSS 使用 PyTorch、Ray 和 PPO。数据库为 PostgreSQL 12.1，shared buffers 设为 32 GB，并因 `pg_hint_plan` 关闭 GEQO（源 PDF 物理页 8–9，Experiment Support 与 Expert Engine）[pdf:E18][pdf:E19]。这不是 EMT/FPGA 论文：未报告开关事件、多速率时间推进、数值定点表示、FPGA mapping、resource/timing 或 real-time step；这里的 “step” 是 plan-edit decision step，不能外推成实时仿真步长。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有复杂的收敛性定理，数学核心是把 plan editing 写成 MDP，并构造可学习的 ordinal reward。可以按“状态 → 动作 → 相对优势 → reward → AAM loss”理解。

**1. 状态。** 在第 $t$ 步，状态把 complete plan 的编码与归一化进度拼接：

$$
\operatorname{State}(CP_t)=\operatorname{PlanEncoding}(CP_t)\,\Vert\,\operatorname{Step}(t),
\qquad \operatorname{Step}(t)=\frac{t}{\text{maxsteps}}.
$$

这就是 Eq. (1)（源 PDF 物理页 4，Eq. (1)）[pdf:E10]。直觉上，两个结构相同的计划在 episode 早期和末期不应完全等价：剩余可编辑步数不同，策略也应不同。

**2. 动作空间。** 若 query 有 $n$ 张表，table-position swap 的候选数为

$$
I_s=\frac{n(n-1)}{2},
$$

join-method override 的候选数为

$$
I_o=|Op|(n-1),
$$

其中 $Op$ 是 DBMS 可用 join methods 集合。整数 action $a\in[1,I_s+I_o]$ 被映射到 `Swap` 或 `Override`；action mask 再根据 query graph 和上一动作排除非法或无意义操作（源 PDF 物理页 4–5，Action 定义）[pdf:E10][pdf:E11]。这里的工程含义是：FOSS 没有连续控制量，优化能力完全由这套离散 plan-edit algebra 决定。

**3. 从 latency 变成 ordinal advantage。** 先定义右计划相对左计划的原始改善比例：

$$
\operatorname{Adv}_{init}(CP_l,CP_r)
=\frac{U(CP_l)-U(CP_r)}{U(CP_l)}\in(-\infty,1),
$$

其中 $U(CP)$ 表示计划性能，在真实环境中取 execution latency。正值表示 $CP_r$ 更快；例如 0.5 表示右计划 latency 比左计划降低一半（源 PDF 物理页 5，Bounty）[pdf:E11]。作者认为动态 workload 下精细回归值不稳定，因此把该比例落入有序区间 $D_k$，再用 Eq. (2) 输出离散 score：

$$
\operatorname{Adv}(CP_l,CP_r)=k-1
\quad\text{if}\quad
\operatorname{Adv}_{init}(CP_l,CP_r)\in D_k.
$$

（源 PDF 物理页 5，Eq. (2)）[pdf:E12]。实际 AAM 用分点 $\{0.05,0.50\}$ 将结果划成三档 $\{0,1,2\}$（源 PDF 物理页 7，Section IV-B）[pdf:E15]。这牺牲精确幅度，换取更稳定的 pairwise ordering。

**4. reward 同时奖励改善和短路径。** 每步 reward 是 bounty 与 penalty 之和。step-bounty 比较新计划与此前估计最佳计划；episode-bounty 用 original、已执行的 median-better plan 和 best-better plan 作为 reference anchors，并按以下式子只在 episode 末段提高最终输出的权重：

$$
\operatorname{Bounty}^{e}_{t}
=pb^{e}_{t}+\eta\left\lfloor\frac{t}{\text{maxsteps}}\right\rfloor eb^{e}.
$$

由 $t=1,\ldots,\text{maxsteps}$ 可见，floor 项在最后一步才变为 1，这是对公式的直接推断。冗余路径惩罚为 Eq. (3)：

$$
\operatorname{Penalty}^{e}_{t}
=\gamma\bigl(\operatorname{minsteps}(ICP^{e}_{t})-t\bigr).
$$

由于到达当前 ICP 的最短步数不大于实际步数，penalty 为 0 或负数；同一目标计划若能两步到达，策略就不应为了多拿中间 bounty 绕三步（源 PDF 物理页 5，Eq. (3) 及上下文）[pdf:E12]。论文设置 $\eta=12$、$\gamma=2$（源 PDF 物理页 6）[pdf:E13]。

**5. AAM 的非对称结构。** 设 $\phi$ 为共享 state network，AAM 写成：

$$
\theta_{adv}(CP_l,CP_r)
\rightarrow FC^2\!\left(
FC^1\!\left(\phi(\operatorname{State}(CP_l))\oplus pos_{left}\right)
-
FC^1\!\left(\phi(\operatorname{State}(CP_r))\oplus pos_{right}\right)
\right).
$$

（源 PDF 物理页 7，Section IV-B）[pdf:E15]。$pos_{left}$ 与 $pos_{right}$ 使交换输入次序成为不同问题，差分层则迫使模型聚焦两计划之间的相对证据。它最终不是预测 latency，而是预测 Eq. (2) 的 ordinal score。

**6. 针对类别不平衡的 asymmetric loss。** 从合理 original plan 出发随机修改，差计划通常多于好计划，因此 score 0 样本占优。论文先定义样本难度：

$$
\hat p_{i,j}=\begin{cases}
p_{i,j}, & h_{i,j}=1,\\
1-p_{i,j}, & h_{i,j}=0,
\end{cases}
$$

即 Eq. (4)，再用 $(1-\hat p_{i,j})^{\gamma}$ 提高难样本权重，并让 positive/negative 使用不同 decay coefficients，满足 $\gamma_+<\gamma_-$。label smoothing 把真实类目标改为 $1-\epsilon$，其余 $K-1$ 类均分 $\epsilon$，最终

$$
LOSS=-\sum_{i=1}^{N}\sum_{j=1}^{K}\hat h_{i,j}L_{i,j}.
$$

FOSS 取 $K=3$、$\epsilon=0.1$（源 PDF 物理页 7，Section IV-C）[pdf:E16]。这部分的直觉不是“让好计划权重永远更高”，而是避免大量容易判定的差计划淹没少量难判定、真正影响 selector 的 plan pairs。

**7. 模拟环境的分解。** 常规 model-based RL 同时学习 transition 与 reward；FOSS 利用 DBMS 已有能力，把 transition 直接设为 optimizer $\Gamma_p$，只学习 reward-side AAM $\theta_{adv}$，得到 $\hat E(\Gamma_p,\theta_{adv})$（源 PDF 物理页 8，Section V-A）[pdf:E17]。这一步是其 sample efficiency 的关键：不花模型容量重学“如何把约束补成合法计划”，只近似昂贵的性能比较。

## § 7 — 实验设计与结论

**实验边界。** JOB 使用 3.6 GB IMDb、21 relations、33 templates、113 queries，按 Balsa 划分为 94 train / 19 test；TPC-DS 生成 10 GB 数据，但 99 个 templates 中最终只选 19 个，每个生成 6 条 query，5 train / 1 test；Stack 数据为 100 GB、约 1800 万问答，过滤后从 12 个 templates 各取 10 条，8 train / 2 test（源 PDF 物理页 8–9，Workloads）[pdf:E18][pdf:E19]。比较对象是 PostgreSQL、Bao、HybridQO、Balsa、Loger；默认 $\text{maxsteps}=3$、每次 agent update 用 900 episodes，各方法以三个随机种子运行，并在 convergence 后比较（源 PDF 物理页 9，Comparison 与 Section VI-B）[pdf:E19][pdf:E20]。指标 GMRL 衡量 query-level 相对 execution latency 的几何平均，WRL 衡量整个 workload 的 execution + optimization 总延迟；两者都以 PostgreSQL 为 1，越小越好（源 PDF 物理页 9，Metrics）[pdf:E19]。

**问题 1：FOSS 是否改善总体 latency？ → 实验：三个 workload 上比较 train/test 的 WRL、GMRL 与总 runtime → 答案：平均上是，但不是每个单项都压倒性领先。** Table I 中，FOSS 的 train WRL 为 JOB 0.16、TPC-DS 0.87、Stack 0.57，test WRL 为 0.12、0.87、0.80；对应作者报告的 PostgreSQL speedup 分别为 train 6.25×、1.15×、1.75×，test 8.33×、1.15×、1.25×（源 PDF 物理页 9–10，Performance Overview 与 Table I）[pdf:E20][pdf:E21]。FOSS 的 workload runtime 为 19.38 s、30.96 s、29.05 s，而 PostgreSQL 为 161.50 s、35.59 s、36.31 s（源 PDF 物理页 10，Table I）[pdf:E21]。不过 TPC-DS train WRL 上 Bao 为 0.86，略低于 FOSS 的 0.87；因此更准确的结论是 FOSS 在跨 workload 的综合与平均表现最好，尤其 JOB 优势明显，而非每个 cell 都第一。

**问题 2：它是否更快学到有效策略？ → 实验：画 test workload 相对 expert 的 speedup-training-time curve → 答案：原计划起点与模拟经验使早期学习明显更快。** Fig. 5 显示 JOB 上约 5 小时后 FOSS 已优于其它 SOTA，约 8 小时达到最佳平台；TPC-DS 与 Stack 约 1 小时收敛（源 PDF 物理页 10，Fig. 5 与 Training efficiency）[pdf:E22]。这里的证据支持“样本效率更高”，但训练仍是小时级，不能把 “high training efficiency” 理解成无需离线训练。

**问题 3：更复杂的 learned optimizer 会不会把 planning overhead 吃掉？ → 实验：在整个 JOB 上统计从 SQL 输入到 plan 生成的 optimization time → 答案：有额外开销，但总 runtime 仍获益。** Fig. 6 中 FOSS 的 25th/50th/75th percentile optimization time 小于 Bao、Balsa、HybridQO，高于 Loger；作者解释 FOSS 还要调用传统 optimizer 生成 original/candidate plans，而 Loger 不需要这一步。尽管如此，Table I 的 workload runtime 仍显示 FOSS 在 JOB 最低（源 PDF 物理页 10，Fig. 6 及相邻正文）[pdf:E23][pdf:E21]。

**问题 4：FOSS 的搜索空间是否真的能覆盖更多有价值计划？ → 实验：每种方法运行三次，为 JOB 每条 query 取已观察到的 known best plan，再按相对 original plan 的 time-saving ratio 排序 → 答案：FOSS 在更多 queries 上超过 expert。** Fig. 8 显示 FOSS 曲线在大部分 rank 上高于 Bao、Loger、HybridQO，并与更细粒度的 Balsa 接近（源 PDF 物理页 11，Fig. 8）[pdf:E24]。按正文统计，至少节省 25% 时间的 query 数量依次为 FOSS 62、Balsa 61、HybridQO 38、Loger 31、Bao 29；至少节省 75% 的数量为 29、29、23、20、14（源 PDF 物理页 11，Known Best Plan）[pdf:E26]。这支持局部编辑空间在 JOB 上并不狭窄，但“known best”只是三次运行中各方法实际找到的最好结果，不是全局最优证明。

**问题 5：为什么默认只走三步？ → 实验：比较 maxsteps=2/3/4/5，并统计 known-best plan 的 step 分布 → 答案：三步在该设置下给出最佳质量—成本折中。** Table II 中 GMRL 分别为 0.596、0.436、0.487、0.470；训练时间与 optimization time 随 maxsteps 增大。Fig. 7 还显示 maxsteps=5 时 step4/step5 的 known-best plans 占比很小，作者据此认为有效计划通常可在 1–3 步内得到（源 PDF 物理页 10–11，Fig. 7、Table II 与 Determination of Maxsteps）[pdf:E23][pdf:E25]。这是一项 workload-conditioned empirical finding，不是普遍定理。

**问题 6：simulated environment 是否真是训练效率来源？ → 实验：关闭模拟环境，只与真实 DBMS 交互 → 答案：关闭后即使训练更久，结果仍明显更差。** Off-Simulated 版本为使实验可行把每次 update 的 episode 数降到 200，训练 48.01 小时后 GMRL 为 0.691；完整 FOSS 训练 9.09 小时、GMRL 为 0.436（源 PDF 物理页 11，Table II 与 Effect of Simulated Environment）[pdf:E25]。这项 ablation 很强，因为它同时展示了 sample throughput 和最终 quality 的损失；但 episode budget 也发生变化，所以不能把差距完全解释成 reward source 本身，真实执行吞吐不足是机制的一部分。

**问题 7：reward penalty、promising-plan validation 与多 agent 是否有用？ → 实验：逐项关闭或增加 agent → 答案：三者都改变了质量—成本曲线。** Off-Penalty 的 GMRL 为 0.465，Off-Validation 为 0.653，说明 validation 对阻止 AAM error accumulation 尤其关键；2-Agents 的 GMRL 最好，为 0.420，但训练时间增至 12.45 小时、optimization time 增至 280.65 ms（源 PDF 物理页 11，Table II）[pdf:E25]。正文解释 promising-plan validation 会把 AAM 估计好的候选送去真实执行，移除后训练数据多样性下降且误差不能及时纠正；2-agent 增加经验和候选多样性，但当前串行配置更慢（源 PDF 物理页 12，design choices）[pdf:E27]。

**不得外推的范围。** 这些结果来自单一 PostgreSQL 12.1 配置、固定硬件、过滤后的 query templates、left-deep plans，以及 join order/join method 两类编辑；TPC-DS 中大量 template 因 SOTA 方法要求或 FOSS left-deep constraint 被排除（源 PDF 物理页 8，Workloads）[pdf:E18]。论文未报告跨 DBMS version/schema 的 zero-shot transfer、并发 workload、cache-state 干扰、bushy plans、access-path editing 或 production tail latency，因此不能据现有实验断言 FOSS 对这些条件同样有效。

## § 8 — Take-aways

**五句话：**

1. FOSS 把 learned query optimization 重写成“从 expert plan 出发的 plan editing”，而不是从零建树或只选粗 hint（源 PDF 物理页 2–3，Section I-B 与 Fig. 1）[pdf:E05][pdf:E07]。
2. 它的可学习 action 只有 table swap 与 join-method override，每一步都由 DBMS 补成合法 complete plan，因此能获得比 partial-plan construction 更密集的反馈（源 PDF 物理页 4–5，Section III）[pdf:E09][pdf:E11]。
3. AAM 用有方向的 plan-pair ordinal classification 同时承担 simulated reward 与 final selector，真实执行负责持续纠偏（源 PDF 物理页 7–8，Sections IV–V）[pdf:E15][pdf:E17]。
4. JOB 上的 Table I、known-best ranking 和 ablation 共同支持其 latency、搜索覆盖与 sample efficiency claim，其中关闭模拟环境或 validation 会显著退化（源 PDF 物理页 10–12）[pdf:E21][pdf:E25][pdf:E27]。
5. 最关键的适用条件是好计划位于 original left-deep plan 的浅层编辑邻域；论文在当前 benchmarks 上给出支持，但尚未覆盖 bushy、access path、跨系统或强分布漂移。

**三句话：**

1. 方法上，FOSS = traditional optimizer 负责合法 plan transition，planner 负责编辑，AAM 负责相对评价，真实 executor 负责校准。
2. 证据上，它在 JOB 的收益最强，在 TPC-DS/Stack 上更接近已有方法，并用 Table II 证明三步搜索、模拟经验和 validation 都不是装饰组件（源 PDF 物理页 9–11）[pdf:E20][pdf:E25]。
3. 风险上，一旦 original plan 附近没有好计划，或 AAM 在新 workload 上排序失真，整个自举循环会被错误局部信息锁住。

**一句话：** FOSS 的真正贡献是把传统 optimizer 的专家先验变成 learned optimizer 的起点和 transition model，再用可执行的局部编辑与相对性能学习换取更高训练效率。

## § 9 — 最脆弱的假设

**最脆弱假设：对目标 workload，足够好的计划通常位于 PostgreSQL original plan 的一个很浅的、left-deep 的编辑邻域内，且能用不超过三次 Swap/Override 到达。**

这是比“AAM 足够准”更底层的假设。AAM 排序错还可以靠 promising-plan validation 和真实执行修正；但如果好计划根本不在 action space 或三步半径内，再好的 planner、AAM 和 simulated learner 也看不见它。论文直接限制为 left-deep plan，仅编辑 join order 与 join method，并把 bushy plan 留作 future work（源 PDF 物理页 4，Section III）[pdf:E10]。默认 maxsteps=3；JOB 的 Fig. 7 与 Table II 表明三步配置 GMRL 最低，step4/step5 known-best plans 很少，这是作者为该假设提供的主要实证（源 PDF 物理页 10–11）[pdf:E23][pdf:E25]。

它在实际中可能不成立，原因至少有三种。第一，坏计划可能来自 access path、scan operator、materialization、parallelism 或 bushy topology，而非当前两类 action。第二，多个局部决定存在强相互作用，真正的好计划需要四步以上协调修改；中间任何 partial repair 都可能更差，形成 performance valley。第三，原计划可能在 workload shift、强相关/倾斜数据或大 join graph 下落入完全错误的 basin，此时“保留 expert plan”从优势变成 search anchor。

论文证据仍不闭合：TPC-DS 只保留 19 个 templates，原因包含 select-project-join 要求和 FOSS left-deep constraint；Stack 也经过模板过滤（源 PDF 物理页 8–9，Workloads）[pdf:E18][pdf:E19]。因此，现有结果更准确地证明“在过滤后的三个 benchmarks 上，很多改进可在浅层邻域找到”，尚未证明“真实 workload 普遍满足局部可修复性”。

## § 10 — 最小复现实验

一周内最值得做的不是复现完整 PPO+AAM，而是直接证伪或支持“浅层局部邻域包含好计划”这个核心前提。

**数据与系统。** 使用 PostgreSQL 12.1、`pg_hint_plan` 和 JOB；从 113 条 query 中按 join 数分层抽取约 30 条，覆盖论文所述的 3–16 joins。固定数据库参数，先 warm cache，再对每个 plan 重复执行三次取 median。原论文的动作定义、left-deep 限制和 Query 1b 示例分别见源 PDF 物理页 2、4–5 [pdf:E06][pdf:E10][pdf:E11]。

**实现。** 不训练 RL，写一个 deterministic neighborhood enumerator：从 original ICP 出发，按论文合法性规则枚举半径 $r=1,2,3,4,5$ 的 `Swap` 与 `Override` 序列，去重后交回 PostgreSQL 补全 complete plan。为控制成本，对每条 query 可先限制到所有 join methods 与结构合法的 swaps；执行时沿用论文 1.5× original-latency timeout（源 PDF 物理页 8）[pdf:E18]。对于 join 数不超过 8 的子集，尽量完整枚举；更大 query 用固定预算的 breadth-first sampling。

**测量。** 对每条 query 记录：best latency ratio $L^*_r/L_{orig}$、首次达到 best-within-5 的最小半径、半径增加带来的 marginal gain、候选数与总执行成本；另统计至少节省 25% 和 75% 的 query 覆盖率，以便与论文 Fig. 8 的口径对齐（源 PDF 物理页 11）[pdf:E24][pdf:E26]。加入两个简单对照：同预算 random edit sequences，以及只修改 join method、不换 join order 的受限搜索。

**什么结果支持 claim。** 若绝大多数可改善 query 的最佳收益在 $r\le3$ 已获得，并且从 $r=3$ 扩到 5 只带来很小的额外 geometric-mean gain，同时三步 neighborhood 显著优于同预算随机搜索，就支持 FOSS 的局部医生假设。

**什么结果反驳 claim。** 若有稳定的一批 query 在 $r\le3$ 完全无改善，但 $r=4/5$ 或完整枚举出现大幅更优计划；或好计划集中在当前 action space 外的 scan/access-path/bushy 变化，那么即使原论文端到端结果可复现，也说明性能来自 benchmark 中 original plan 恰好处于好 basin，而不是 plan-doctor 机制具有普遍性。

## § 11 — 最强反例设计

最强反例不是简单换一个 dataset，而是构造一个**需要跨越性能谷底的多步协调编辑族**，让 FOSS 的局部动作、短 horizon、penalty 与 timeout 同时成为可预测的失败机制。

具体做法是生成 8–10 表的 left-deep 可表达 query，使原计划把高选择性表放在末端，并在前三个 join 上采用会触发大中间结果或 spill 的 methods。设计数据相关性与内存阈值，使任何 1–3 次局部修改都仍保留至少一个主瓶颈，latency 不降反升；只有把选择性表前移并同步修改多个 join methods，也就是至少 4–5 次协调动作，才突然进入低延迟 basin。对 $n\le8$ 的实例完整枚举所有 left-deep order/method combinations，精确得到 global best 与其相对 original ICP 的最短 edit distance。

这个反例直接攻击三处机制。第一，默认 maxsteps=3 无法到达目标；第二，Eq. (3) 的 shortest-path penalty 鼓励短、近似单调的编辑路径，不利于先变差后变好的 valley crossing（源 PDF 物理页 5，Eq. (3)）[pdf:E12]；第三，真实执行超过 original 1.5× 即 timeout，会减少这些“必要但暂时很差”的 intermediate plans 对 AAM 的监督（源 PDF 物理页 8，timeout）[pdf:E18]。action mask 在 swap 后又限制下一步只能修改邻接 join method，进一步规定了可达路径形状（源 PDF 物理页 5，Action）[pdf:E11]。

实验应比较四组：原 FOSS；maxsteps 扩到 6；移除 penalty 但保持预算；一个能直接搜索完整 edit program 的 beam/exhaustive baseline。若完整搜索稳定找到远距离好计划，而原 FOSS 在所有随机种子上停留于 original 附近，且扩 horizon 后才恢复，这会给出一个具体替代解释：**FOSS 在 JOB 上成功，可能主要因为 PostgreSQL original plans 周围存在短而近似单调的改进路径，而不是 AAM 学会了一般性的 query optimization。** 这比“换硬件后可能变差”更有力，因为它在论文自己的 left-deep、join-order/join-method 范围内就能推翻核心机制的普适性。

## § 12 — Follow-up Research Bet

**候选判断：任务禁止包外文献检索，以下不声称具有 novelty。主押注是“可迁移的因果计划编辑图谱（Causal Plan-Edit Atlas）”。**

**新的研究问题。** 不再问“给定一条 query，哪条 action sequence 最快”，而问：**一个具名 plan edit 在什么结构、数据分布和系统状态下会因果性地改善或恶化 latency，这种 edit effect 能否跨 query template、schema 甚至硬件迁移？** 这把研究目标从单 workload policy learning 改为学习可组合、可解释、可迁移的 plan-edit mechanism。

**首次可能带来的能力。** 若成功，optimizer 可以在新 schema 上用少量真实执行识别几个 edit-effect parameters，随后直接组合已学到的 causal motifs，完成 zero/few-shot plan repair；它还能说明“把表 X 前移为何只有在 join Y 使用 hash 时有效”，而不只是给出一个黑箱 score。FOSS 已提供适合作为 intervention vocabulary 的 `Swap`/`Override` algebra，以及有方向的 plan-pair label（源 PDF 物理页 5、7，Action 与 AAM）[pdf:E11][pdf:E15]。

**核心机制与因果链。** 数据生成不再采样任意 trajectory，而是构造 matched plan pairs：两计划除一个受控 edit 外尽量相同，以真实 latency 作为 outcome，并把 query graph、estimated/actual cardinality、node height、operator context、cache/hardware state 编成 context。模型学习一个 typed causal hypergraph：`context × intervention → local/interaction effect`；多个 edit 的组合通过显式 interaction factors 合成，而不是由单一 policy 在短 horizon 内隐式试错。随后用 DBMS optimizer 保证每个 intervention 后的计划合法，利用 FOSS 的 simulated-environment 思路大规模生成可执行 counterfactual candidates，再只对能最大区分 competing causal explanations 的 pairs 做真实执行。因果链是：**受控编辑产生可辨识的对照 → 学到可迁移 edit effect → 组合 effect 预测多步结果 → 生成新计划 → 少量真实实验更新机制**。

**被改变的基本设计变量。** 至少四项发生变化：任务从 per-query plan selection 变为 cross-query mechanism identification；representation 从单个 plan state vector 变为 plan-context-intervention causal graph；数据生成从 policy rollout 变为 matched intervention；评价对象从同 workload latency 变为 held-out edit-context 的 counterfactual generalization。它不是给 FOSS 加一个 confidence wrapper，因为删除 causal representation 后，“跨 schema 预测某个编辑的作用”这一基本能力就不存在。

**论文特异依据。** 方法侧，FOSS 已把 plan changes 离散成可命名 actions，并把 DBMS optimizer 当作廉价 transition model；AAM 已展示 plan-pair ordinal supervision 可以同时服务 reward 与 selection（源 PDF 物理页 5、7–8）[pdf:E11][pdf:E15][pdf:E17]。实验侧，三步配置最好说明短 edit motifs 在当前 workload 中有结构；Off-Validation 明显退化、2-Agents 因数据与候选多样性提升到 GMRL 0.420，说明“采什么 pairs、是否覆盖多样机制”直接决定模型质量（源 PDF 物理页 11–12，Table II 与 multi-agent analysis）[pdf:E25][pdf:E27]。这些现象支持把重点从更多 rollout 转向更有辨识力的 interventions。

**最大收益与最大科学风险。** 最大收益是把 learned query optimization 从 benchmark-specific policy 推向可迁移的机制知识，显著降低每个新 workload 的真实执行成本，并提供可检验的 edit-level explanation。最大风险是 query-plan latency 高度非局部：cache、memory spill、parallelism 与 cardinality error 可能产生高阶交互，使单 edit effect 不稳定、无法组合；所谓“因果图谱”最后可能只是换名的高容量 predictor。

**首个区分机制的最小实验。** 在 JOB 与过滤后的 TPC-DS 上生成相同预算的 plan pairs，严格留出未见过的 `edit × structural context` 组合；比较三种模型：因果 typed-intervention model、使用同一 encoder/数据量的普通 AAM、打乱 intervention identity 的对照。测试两项：一是 held-out pair 的 improvement-sign/ordinal-score accuracy，二是把两个或三个 edits 组合后对最终 latency rank 的预测。若因果模型只在随机划分上更好，而在组合留出上不优于 AAM，收益只是更多结构参数；只有它在组合留出和跨 workload 少样本适配上持续领先，才能支持“学到了可迁移 edit mechanism”。

**与论文所列最近路线的实质区别。** Bao/HybridQO 的对象是 hint/candidate selection，Balsa/Loger 的对象是 plan construction，Leon/QPSeeker 的对象是 learned cost/planner；本押注的 problem 是 edit-effect identification，mechanism 是受控 intervention，representation 是 causal edit graph，experimental object 是跨 context counterfactual effect（源 PDF 物理页 2、9、12，prior work 与 related work）[pdf:E04][pdf:E19][pdf:E28]。由于未检索包外全文，这只能作为证据约束的研究候选。

**Wild-card alternative：** 把等价 execution plans 定义成一种 typed graph-rewrite language，训练离散 diffusion model 一次性生成结构多样的可执行计划，AAM 仅提供离线序关系监督；研究对象从“局部修补策略”改为“计划空间的生成规律与可达拓扑”。
