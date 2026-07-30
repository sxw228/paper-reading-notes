# Intelligent EV Charging for Urban Prosumer Communities: An Auction and Multi-Agent Deep Reinforcement Learning Approach

作者：Luyao Zou，Md. Shirajum Munir，Yan Kyaw Tun，Seokwon Kang，Choong Seon Hong  
出处：IEEE Transactions on Network and Service Management，Vol. 19，No. 4  
年份：2022  
DOI：10.1109/TNSM.2022.3160210  
Zotero key：W6P6QMUV  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个两层耦合的 EV charging 问题：城市里的多个 prosumer community 既有光伏和电池储能，也有自身负荷与 EVSE；多个 EV 会因距离、目的地和行驶能耗而对不同社区给出不同买价。系统不仅要决定谁和谁交易、单位电价是多少，还要在 renewable generation 与 demand 都波动时决定是否从电网补能，从而同时提高 social welfare 和 EV charging achieved rate。作者把后者定义为“获得充电的 EV 数量 / 请求充电的 EV 总数”（PDF 物理页 1–2，Abstract 与 Introduction）[pdf:E01][pdf:E02]。

这件事重要，不只是因为“EV 越来越多”。工程上的真正矛盾是：只做市场撮合时，经济上合适的 winner 可以成交，但 loser 仍然没有电；只做充电调度时，又可能没有 truthful pricing、budget balance 与用户位置偏好。论文试图把这两种目标接起来：先用 auction 关闭价格和 winner，再用 grid purchase 为 auction loser 补充服务。对运营者而言，价值是同时观察交易收益、服务覆盖率与可再生能源利用，而不是只优化其中一个指标。

需要明确边界：这是一篇网络与服务管理层面的离散调度研究，不是配电网潮流、EMT、充电器功率电子或电池电化学论文。它讨论“买不买电”和“谁获得服务”，但没有验证电网电压、线路拥塞、保护动作、变流器动态或硬件实时实现。

## § 2 — 前人工作与不足

论文把 prior work 分成三组。第一组是 EV scheduling：离散充电、hierarchical ADMM、simulated annealing、EST/EFT 和两阶段 charging-station sizing。这些工作分别能平滑负荷、降低成本、改善服务时序或满足 QoS，但在作者的分类里没有同时把 social welfare maximization 和 charging-rate maximization 当作目标。第二组是 EV energy trading 的 double auction：已有方法能做 truthful matching、multi-unit transaction、charger sharing 或带时间偏好的交易，但通常只给 auction winner 充电；即使允许一个 buyer 向多个 seller 出价，也没有继续处理 auction loser。第三组是 DQN/DDPG-based charging：它们能做 charging route、navigation、charging control 或 multiphysics-constrained fast charging，但作者认为 experience replay 会增加 memory/computation demand，并让更新依赖 old-policy data（PDF 物理页 2–4，Table I、Table II 与 Section II）[pdf:E02][pdf:E03]。

因此，论文声称的差异不是“第一次用 auction”或“第一次用 DRL”，而是把两条已有路线串成有顺序依赖的联合方案：BDA 先给出 winner、loser、统一价格和剩余能源状态，A3C-LSTM 再处理 loser 的 grid-energy purchase。作者还在原 BDA 上增加 EV allocation，使一个 EV 即使在多个社区中成为候选 winner，最终也只分配到效用最大的一个社区（PDF 物理页 3，contributions）[pdf:E03]。

批评性地看，论文的 related-work gap 是由作者自己的目标组合定义的，Table I/II 证明的是“所列文献没有同时勾选这两个目标”，不是对整个领域的穷尽式 novelty 证明。本卡按 PDF-only 协议没有联网补查 2022 年前后的相邻工作，因此不能进一步声称该组合在全球文献中唯一。

## § 3 — 重建作者的思考路径

一个不预先知道论文方案的研究者，可能会沿下面的路径走到这个设计。

第一步，先承认单一 charging scheduler 不够。城市 prosumer community 同时面对自有负荷、间歇性光伏、有限 ProBSS 和多个 EV 的竞争请求；不同距离还会改变 EV 到达社区前消耗的能量和愿意支付的价格。于是“给谁充电”既是资源分配问题，也是市场定价问题。

第二步，采用 double auction。它天然适合多个 buyer 与多个 seller，并能把 individual rationality、budget balance 和 truthfulness 作为机制设计目标。但正常 auction 只服务 winner，charging achieved rate 会在供给紧张时明显下降，这恰好暴露出第二个问题：loser 仍需要服务。

第三步，把 loser charging 从 auction 中拆出。winner 已由第一阶段确定，第二阶段只需处理剩余 renewable energy、ProBSS energy、未满足的 prosumer demand、loser demand 与 grid support。由于这些量跨时间变化且维度随社区增加，研究者会考虑不用 replay buffer 的 asynchronous actor-critic，并用 LSTM 保留时间依赖。

第四步，把两个阶段用明确的数据接口连接：auction 输出 loser、统一价格、剩余能源与未满足负荷；每个 community agent 再做 grid on/off。这个思路并不要求“DRL 比所有优化方法更优”，只要求先把经济匹配和服务补偿分开，再让第二阶段学习时序决策。这一重建与作者在 PDF 物理页 2–3 对 technical motivations 和 contributions 的叙述一致 [pdf:E02][pdf:E03]。

## § 4 — 核心 Intuition

先让 auction 做它最擅长的事：用可解释的规则决定价格和赢家，并保证基本经济性质。再把 auction 没服务到的 EV 视为单独的动态供能问题，让每个社区只根据本地剩余能源、负荷和 loser demand 决定 grid on/off。两阶段之间不是并行拼接，而是第二阶段严格消费第一阶段的 loser 与剩余状态（PDF 物理页 11、14，Fig. 2 与 Fig. 4）[pdf:E09][pdf:E12]。

## § 5 — 具体方法与完整 Pipeline

系统模型以 DSO 为中央 auctioneer 和调度者。每个社区拥有 prosumer building、renewable generation、ProBSS 与至少一个 EVSE，并把位置、reserve price、可拍卖 surplus energy、负荷、发电和储能状态发给 DSO。EV 通过 RSU 获得社区位置，按距离和自身目的地选择一个或多个 preferred communities，再提交 buy bid、期望充电量和行驶速度。论文把每个 time slot 设为 6 小时，并假设 EV 在 slot 内采用 constant-power charging；社区的 reserve price 已含 battery degradation 与基础运营成本，但其最优定价不在研究范围内（PDF 物理页 5–6，Table III、Fig. 1、footnotes 1–2 与 Section IV）[pdf:E04][pdf:E05]。

完整 pipeline 如下。

1. **计算 EV 的到达能量需求。** DSO 用车辆质量、加速度、滚阻、坡度和速度估计 traction force/power，再除以 motor efficiency 得到电功率消耗，并把行驶消耗加到 EV 原计划充入的能量上。论文固定 motor efficiency 为 90.3%，不是按 torque-speed map 在线变化（PDF 物理页 6–7，Eq. (1)–(6)）[pdf:E05][pdf:E06]。
2. **形成联合优化问题。** 决策变量分别表示 EV 是否选择社区、社区是否买 grid energy、以及某一 EV bid 是否获胜；目标为各时隙 social welfare 与 charging achieved rate 的乘积，并受 EV/ProBSS 容量、单 EV 至多一个社区、auction surplus 与 QoS 约束。作者把它归为 mixed-integer、NP-hard 问题，然后拆成 truthful double auction 与 loser charging 两个子问题（PDF 物理页 9–10，Eq. (24)–(27)）[pdf:E07][pdf:E08]。
3. **BDA 决定价格和 winner。** DSO 将 community ask 升序、EV buy bid 降序排列，用 median seller ask 与 breakeven index 截出候选 winner；seller winner 的单位收款为 \(\lambda_\beta(t)\)，EV winner 的单位付款为临界 buy bid。若同一 EV 在多个社区成为 winner，分配给能产生最大 EV utility 的社区。输出包括每个社区的 winner、全局 loser、统一价格、剩余 ProBSS/renewable energy 和未满足 prosumer demand（PDF 物理页 11–13，Fig. 2、Fig. 3、Algorithm 1）[pdf:E09][pdf:E10][pdf:E11]。
4. **为 loser 生成每个社区的状态。** loser 被安排到其原先 preferred communities 中最近的一个；community agent 的状态由剩余 renewable energy、剩余 ProBSS energy、未满足 prosumer demand、该社区 loser demand、所需 grid support 五项组成。每个 agent 只有 grid on 和 grid off 两个离散 action；全局网络保存 actor/critic 参数，各 community agent 异步与环境交互并回传梯度（PDF 物理页 14，Fig. 4 与 Algorithm 2）[pdf:E12]。
5. **A3C-LSTM 学习 grid purchase。** actor 输出 stochastic policy，critic 估计 state value，LSTM 保存时间依赖；agent 根据能否完全覆盖 loser demand 且满足约束获得 0/1 reward，再以 q-step return、advantage、entropy regularization 和 Adam 更新。Algorithm 3 给出每个 community agent 与 global network 同步、交互、反向累积梯度及异步更新的流程（PDF 物理页 15–16，Eq. (37)–(50) 与 Algorithm 3）[pdf:E13][pdf:E14]。

Appendix 给了一个可核对的单时隙例子：4 个 EV、4 个社区，社区 ask 为 0.015、0.034、0.033、0.04 美元，median threshold 为 0.0335 美元；最终社区 \(i_1,i_3\) 获胜，EV \(κ_1,κ_2,κ_4\) 获胜，\(κ_3\) 成为 loser 并被安排到最近的 \(i_2\)。这段 walkthrough 证明 pipeline 的数据依赖可以手工追踪，但不证明长期策略最优（PDF 物理页 21，Tables VI–VII 与 Appendix）[pdf:E19]。

**EMT/FPGA 边界：** 论文未报告开关模型、事件处理、EMT 离散化、multi-rate time stepping、网络矩阵求解、fixed-point/浮点位宽、FPGA mapping、片上资源、时序、延迟或实时步长。实际执行平台只报告 Python 3.6 与 TensorFlow API 的仿真；“异步”指 A3C agents 的参数更新，不是 FPGA 并行流水线或电力电子实时仿真（PDF 物理页 16，Section VII）[pdf:E14]。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，但它更接近“模型定义 + 机制性质 + actor-critic 更新”，不是从物理定律推出一个闭式最优控制器。

**能量模型。** EV 的 traction power 为

\[
\Phi_\kappa(t)=F_\kappa^{\mathrm{trac}}(t)v_\kappa(t),
\]

电池侧消耗功率为

\[
\Upsilon_\kappa^{\mathrm{con}}(t)=\frac{1}{\mu_m}\Phi_\kappa(t),
\]

总 charging demand 则是计划充电量与行驶消耗之和：

\[
E_\kappa^{\mathrm{dem}}(t)=\omega_\kappa+\int_0^t\Upsilon_\kappa^{\mathrm{con}}(\tau)\,d\tau.
\]

直觉是：社区越远或行驶工况越费能，EV 到达后需要补的总能量越高；同一 buy bid 因此不能脱离到达能耗理解。原文 Eq. (2)–(6) 与变量解释位于 PDF 物理页 7 [pdf:E06]。

**联合目标。** 作者先把 social welfare 定义为 seller 与 buyer utility 之和 \(U_s(t)\)，再优化

\[
\max_{\mathbf{x},\mathbf{y},\mathbf{z}}\sum_{t\in\mathcal{T}} U_s(t)\,\zeta(t),
\]

其中 \(\zeta(t)\) 是 charging achieved rate。乘积意味着只有“经济效用高且服务覆盖高”的时隙才得到高目标值，但也会产生尺度耦合：social welfare 的货币尺度变化会直接改变目标，没有给出多目标权衡或归一化分析。Eq. (23)–(24) 及约束位于 PDF 物理页 9 [pdf:E07]。

**两阶段价格与服务。** BDA 的关键价格是

\[
\delta(t)=\lambda_\beta(t),\qquad
\delta_\kappa^i(t)=b_{\kappa_h,i_h}(t),
\]

即 seller 收 median threshold，buyer 支付 critical winning bid。由 winner buyer 的付款不低于 seller 收款，作者推出 auctioneer 无 deficit；由 winner 的报价单调性与 critical payment，作者给出 truthfulness 论证（PDF 物理页 12–13，Eq. (35)–(36)、Lemmas 1–3）[pdf:E10][pdf:E11]。这套证明覆盖 BDA 机制本身，不覆盖第二阶段 grid purchase 后的整个联合系统是否仍具有相同机制性质。

**A3C-LSTM 目标。** 每个 community agent 的 q-step return 是

\[
R_i^t=\sum_{j=0}^{q-1}\gamma^j r_i^{t+j}+\gamma^q V(s_i^{t+q};\theta_i^\vartheta),
\]

而即时 reward 为一个二值条件：只有可用 renewable、storage 与 grid support 在扣除 prosumer 未满足负荷后足以完全覆盖 loser demand，且约束成立，才得 1，否则得 0。随后用 \(R_i^t-V(s_i^t)\) 作为 advantage 更新 actor，并用平方 TD error 更新 critic（PDF 物理页 15，Eq. (37)–(45)）[pdf:E13]。直觉上它学习的是“哪些状态下开 grid 才能把该社区的 loser 全部覆盖”，而不是连续优化购电量、成本或 partial charging quality。

## § 7 — 实验设计与结论

实验是纯仿真。作者使用 NREL 数据来源构造 prosumer building demand、private/public EV demand 与 Midwest solar generation；case study 有 4 个社区、200 栋 prosumer buildings、每个 time slot 最多 696 辆 EV、最多 2784 个 buy bids。每个 slot 为 6 小时，一年共 1460 个 slots；A3C-LSTM 使用 discount factor 0.99、actor/critic learning rate 0.001、100 episodes、2 个 actions 与 Adam。对比方法是 Only BDA、BDA + DQN 和 BDA + A2C，后两者使用所有 community agents 的联合 state information（PDF 物理页 16–17，Section VII 与 Table IV）[pdf:E14][pdf:E15]。

**问题 1：BDA 是否满足经济性质？ → 实验：** 比较每月 buyer payment 与 seller income，并画出 buyer/seller utility 对 bid/ask 的分布。**答案：** 论文报告一年内 EV buyer 向 auctioneer 支付 215,699.78 美元，community seller 收到 184,247.47 美元，因此该仿真中 auctioneer 没有 deficit；utility 曲线也符合 critical bid 两侧 winner/loser 的预期（PDF 物理页 17，Fig. 5–8）[pdf:E15]。这支持具体样本中的机制行为，但 truthfulness 的主要依据仍是 Lemma 3，而不是这几张图。

**问题 2：LSTM-based A3C 是否学得比 DQN/A2C 好？ → 实验：** 在 100 episodes 上比较 reward trajectory。**答案：** 作者报告 A3C-LSTM 约在第 30 episode 收敛，收敛 reward 高于 DQN/A2C，且波动较小（PDF 物理页 18，Fig. 10）[pdf:E16]。论文未报告随机种子、重复训练次数、置信区间或显著性检验，因此无法判断曲线差异是否稳定跨 seed。

**问题 3：联合方法是否改善收入与 charging achieved rate？ → 实验：** 在 1460 个 slots 上比较四种方法。**答案：** 年总收入分别为 Only BDA 215,699.78 美元、BDA+DQN 376,621.21 美元、BDA+A2C 376,814.37 美元、proposed 401,287.33 美元；proposed 相对后三者分别高 86.04%、6.54%、6.49%。总请求 EV 为 465,868 辆，Only BDA、BDA+DQN、BDA+A2C、proposed 分别服务 295,908、464,804、464,894、465,487 辆（PDF 物理页 19，Fig. 14–16）[pdf:E17]。相应 charging rate 为 63.53%、99.77%、99.79%、99.92%，proposed 相对三条 baseline 的增长被作者报告为 57.31%、0.15%、0.13%（PDF 物理页 20，Fig. 17–19 附近正文）[pdf:E18]。

这里存在一个必须保留的原文内部冲突：贡献段在 PDF 物理页 3 把 Only BDA 写成 66.53% [pdf:E03]，但 Fig. 16 的 295,908/465,868、物理页 19 的正文以及物理页 21 的 conclusion 都是 63.53% [pdf:E17][pdf:E19]。按图中计数计算约为 63.52%，因此本卡把 63.53% 视为实验主体报告值，同时不抹去 66.53% 的不一致。

**问题 4：是否更接近 renewable-energy ground truth？ → 实验：** 比较 renewable usage 分布、supported-EV demand 与 explained variance。**答案：** 作者报告 mean renewable usage 为 ground truth 15.16 MW、BDA+DQN 12.72 MW、BDA+A2C 12.73 MW、proposed 15.08 MW；supported-EV demand 分别为 10,804.55、10,774.53、10,774.92、10,794.93 kW，proposed 的 explained variance 为 0.99（PDF 物理页 20，Fig. 18–19 与 Table V）[pdf:E18]。

不得外推的范围包括：只有 4 个社区；数据来自 Midwest 年度数据的构造 case；没有 distribution-grid constraints、动态电价、通信故障、用户拒绝、真实充电器或现场部署；没有 wall-clock training/inference latency、memory、CPU/GPU、energy consumption 或 scalability benchmark。作者“scalable”的论证是增加社区时增加 community agent，并非在更大规模上给出运行时间或收敛证据。

## § 8 — Take-aways

**5 句话：**  
1. 论文把 EV charging 拆成“先 truthful auction，再给 auction loser 补服务”的两阶段问题（PDF 物理页 10，Section V）[pdf:E08]。  
2. BDA 负责 winner、critical price 和基本经济性质，A3C-LSTM 只负责每个社区的 grid on/off（PDF 物理页 11–15，Section VI）[pdf:E09][pdf:E13]。  
3. 在作者的 4-community 年度仿真中，联合方法报告 99.92% charging rate 和 401,287.33 美元总收入（PDF 物理页 19–20，Fig. 14–16）[pdf:E17][pdf:E18]。  
4. 它相对 DQN/A2C 的绝对 charging-rate 优势只有 0.15/0.13 个百分点，且没有多 seed 或置信区间（PDF 物理页 20，Fig. 16 后正文）[pdf:E18]。  
5. 最关键的未验证点是电网购能被抽象成近乎无限、无拥塞的二值动作，因而高服务率可能主要来自“允许买电”，不一定来自 A3C-LSTM 本身。

**3 句话：** BDA+A3C-LSTM 提供了一个结构清楚、接口明确的 auction-to-service pipeline（PDF 物理页 11，Fig. 2）[pdf:E09]。仿真结果支持它在给定数据和抽象下提高服务率与收入，但论文内部还存在 66.53%/63.53% 的 BDA 数字冲突（PDF 物理页 3、19、21）[pdf:E03][pdf:E17][pdf:E19]。没有 grid feasibility、价格风险、现场硬件与统计重复时，不能把 99.92% 外推为真实城市系统保证。

**1 句话：** 这篇论文最有价值的是把“经济上没赢的 EV”显式变成第二阶段服务对象，最需要警惕的是第二阶段把真实电网约束压缩成了 grid on/off（PDF 物理页 10、15，Eq. (27) 与 Eq. (38)）[pdf:E08][pdf:E13]。

## § 9 — 最脆弱的假设

最脆弱的假设是：auction loser 与 community loser 都愿意接受第一阶段给出的统一价格，而且社区只要选择 grid on，就能按需要购买足够的电来完整覆盖 loser demand。论文还把 loser 分配到最近的 preferred community，并把距离视为统一价格下影响其意愿的唯一因素（PDF 物理页 10，Section V-B）[pdf:E08]。

这个假设一旦失效，核心增益会直接失效。真实配电网可能有 feeder/transformer capacity、需量电费、峰谷价格、购电上限、排队、充电器占用、通信延迟和用户取消；社区也未必愿意用 auction price 为 loser 服务。更关键的是，Eq. (38) 的 reward 只问“是否完全覆盖 loser demand”，不惩罚 grid energy cost，也不允许 partial service 的连续价值（PDF 物理页 15）[pdf:E13]。因此，99.92% charging rate 可能主要由“可按需从电网补足”这个环境设定产生，而非 LSTM 或 asynchronous learning 的独特能力。

论文给出的支持证据是：仿真中不同社区确实呈现不同 renewable、storage 与 grid usage，并且 proposed 方法服务的 EV 最多（PDF 物理页 20，Fig. 17–19）[pdf:E18]。缺失的证据则是 grid capacity、动态 tariff、峰值功率、网络安全约束、购电预算、用户接受率和供能失败工况。作者没有做关闭或限制 grid support 的消融，也没有把 learned policy 与一个确定性的 shortage-threshold rule 比较。

## § 10 — 最小复现实验

一周内最值得复现的不是全部论文，而是验证“A3C-LSTM 的收益是否超出允许 grid purchase 本身”。

数据使用论文列出的 NREL building/EV demand 与 Midwest solar 数据；若原始预处理无法重建，就按 Table IV 的 4 communities、200 buildings、最多 696 EV、6-hour slot 和 1460 slots 生成公开且固定 seed 的替代数据，并明确这只能复现机制而非原数值。实现 Algorithm 1 的 BDA、Algorithm 2 的 state construction，以及三种 loser policy：A3C-LSTM、A2C、确定性 rule `if available energy < loser demand then grid on`。为避免训练偶然性，A3C-LSTM/A2C 至少各跑 10 个 seeds。

测量四项：charging achieved rate、总 income、grid energy purchased、renewable curtailment；同时记录 mean±standard deviation，并对 peak-demand days 单独统计。论文的原始规模和 hyperparameters 可由 PDF 物理页 16–17 的 Section VII/Table IV 直接复核 [pdf:E14][pdf:E15]。

支持核心 claim 的结果是：A3C-LSTM 在相同 grid-energy budget 下，跨 seed 稳定超过 A2C 和 deterministic rule，且不是靠购买更多电换来服务率。反驳结果是：deterministic rule 达到相同或更高的 charging rate/income，或 A3C-LSTM 的优势落入 seed 方差内；这将说明论文证明了“允许补购电有效”，但没有证明 LSTM-based asynchronous policy 是必要机制。

## § 11 — 最强反例设计

最强反例是在同一年度需求上构造“高需求、低光伏、grid-constrained”连续窗口：对每个社区设置 feeder power cap、动态购电价和日预算，并让高峰期的 loser demand 跨社区相关上升。仍使用论文的 two-action policy，但 grid on 只能得到受 feeder cap 限制的能量，且高价购电会降低 social welfare。对照方法使用一个带相同信息的短视 constrained optimizer 或简单 priority rule。

这个反例会直接攻击两件事。第一，如果 Eq. (38) 的二值 reward 让 agent 在无法完全覆盖 demand 时长期只得到 0，它可能无法区分“差一点满足”和“完全不可行”，credit assignment 会恶化。第二，如果统一 auction price 不能覆盖动态 grid cost，第二阶段越积极买电，整体 social welfare 反而可能越低，破坏“同时提高 welfare 和 service”的原始目标。

可预测的失败条件是：连续多个 slot 的 renewable deficit 超过 feeder cap，且 dynamic tariff 高于 loser 接受的 auction price。若此时 proposed policy 的 charging rate、income 或 constraint violation 显著劣于 constrained baseline，那么原结果的替代解释就是“无限制 grid support 和 binary reward 造成的近饱和”，而不是 A3C-LSTM 对时序不确定性的优越处理。

## § 12 — Follow-up Research Idea

在 power/energy 与 network/service-management 交叉领域，高影响研究通常不仅看平均 reward，还看机制可实现性、约束违例、服务保证、跨场景鲁棒性和真实系统价值。基于本卡第 9 节，候选方向是：把问题从“为 auction loser 决定 grid on/off”重新定义为“在配电网容量、动态 tariff 与用户接受约束下，联合给出可兑现的服务承诺和市场结算”。这是候选想法，未做充分相关工作检索，不声称 novelty。

**(a) 未满足的需求。** 现有两阶段方案先承诺 winner/price，再假设第二阶段能用 grid energy 补足 loser；真实系统需要在承诺前知道 feeder capacity、购电成本和服务失败风险，否则市场结果可能物理上不可兑现。

**(b) 研究价值。** 新目标不是把 A3C 换成另一个网络，而是要求 auction outcome、grid feasibility 和 service guarantee 同时成立。它能把“99.92% 平均服务率”升级为“在给定风险水平下可兑现多少服务、违约成本是多少”，更符合电力系统的安全约束与服务管理的 SLA 思维。

**(c) 可借鉴的方法。** 可以借鉴 distributionally robust optimization 处理 demand/renewable shift，用 constrained Markov game 或 primal-dual safe RL 处理多社区的长期约束，再让 mechanism design 保证报价激励与物理可行分配一致。学习器不直接替代安全层，而是预测不确定性或提出候选动作，由约束层投影到可执行集合。

**(d) 第一个证伪实验。** 在论文的 4-community 数据上加入 feeder cap、time-of-use tariff 和一个未见过的连续阴天周；比较原 A3C-LSTM、deterministic constrained optimizer 与候选方法。若候选方法不能在相同 charging-rate 下显著降低 constraint violation/违约成本，或不能在相同风险下提高 welfare，这个方向应被否定。

**(e) 与本文的实质区别。** 本文固定第一阶段 auction，再把第二阶段建成二值购电补偿（PDF 物理页 11、15，Fig. 2 与 Eq. (38)）[pdf:E09][pdf:E13]；候选方法把“能否兑现服务”前移为市场分配的一部分，并把平均 reward 改为受物理与经济风险约束的服务保证。问题定义和验收指标都发生了变化，不是简单增加一个 neural-network 模块。
