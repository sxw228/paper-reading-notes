# An LLM-Powered Multi-Agent Framework for Automated Controller Tuning and Calibration

作者：Dihong Huang、Yong Chen、Jianbiao Li、Ningyi Dai（PDF 物理页 1，标题页）[pdf:E01]

出处：2025 IEEE 3rd International Power Electronics and Application Symposium（PEAS，电力电子与应用研讨会）（PDF 物理页 1，标题页）[pdf:E01]

年份：2025（PDF 物理页 1，标题页）[pdf:E01]

DOI：10.1109/PEAS66638.2025.11403728（PDF 物理页 1，标题页）[pdf:E01]

Zotero key：CNK47NVX

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 论文要解决的是 power electronics（电力电子）控制器参数从离线模型迁移到 Real-Time Digital Simulator（RTDS，实时数字仿真器）时发生的 sim-to-real gap（仿真到真实/高保真平台差距）：离线 surrogate model（代理模型）和优化器给出的参数很快，但在 RTDS 验证时可能失效；完全在线搜索又需要大量昂贵的 RTDS 运行，手工调参还依赖专家经验。作者把目标明确为：让工程师用高层自然语言给出性能目标，系统自动完成离线搜索、RTDS 验证、参数校准和结果汇报。摘要报告，在 108 个优化问题上，所提方法成功率为 79.6%，离线方法单独使用时为 13.0%，平均每题使用 4.56 次迭代/RTDS 运行、耗时 57.7 s（PDF 物理页 1，Abstract）[pdf:E01]

重要性不只在于“少调几个 PI 参数”。对高功率变换器而言，overshoot（超调）、rise time（上升时间）、Integral Absolute Error（IAE，绝对误差积分）和 steady-state error（SSE，稳态误差）互相耦合；离线模型若不能忠实反映延迟、离散化和高保真实现效应，得到的“最优参数”可能在实际验证平台上不满足约束。论文因此瞄准的是控制设计流程中的成本瓶颈：把便宜的离线计算用于大范围搜索，把昂贵的 RTDS 运行用于少量、信息密度高的校准，而不是把全部优化预算花在 RTDS 上。论文将这一工程矛盾概括为“离线快但不可靠、在线准但代价高”（PDF 物理页 1，Section I）[pdf:E02]

**边界。** 本文展示的验证链路是 RTDS 环境，而不是物理功率样机；因此“hardware-validated”在本卡中应理解为高保真实时仿真/HIL 链路验证，不能外推为真实器件老化、传感器噪声、通信抖动和功率硬件故障下的上机有效性（PDF 物理页 1，Abstract）[pdf:E01]。

## § 2 — 前人工作与不足

论文对 prior work（前人工作）的梳理可以分成四条路线。第一，线性化模型加人工迭代测试，解释性强，但耗时且依赖专家。第二，Particle Swarm Optimization（PSO，粒子群）等 meta-heuristic（元启发式）算法自动搜索参数，但仍以数值试探为主。第三，data-driven surrogate model 和 Offline Surrogate Model Parameter Tuning（OSMPT，离线代理模型参数整定）用神经网络替代昂贵仿真，能显著加快初始设计。第四，直接在在线平台上调参，包括 reinforcement learning（强化学习）路线，能利用真实反馈，但计算和实验预算仍高。上述分类及其局限均是论文在 Introduction 中对引用文献 [1]–[10] 的概括，不是本卡对这些外部论文的独立复核（PDF 物理页 1，Section I）[pdf:E02]

最接近本文主题的已有方向还包括一项“面向目标的 power electronics LLM multi-agent control design”工作 [11]；本文参考文献给出了该题名，但正文没有用同一任务、同一 RTDS 预算与它直接比较（PDF 物理页 6，Reference [11]）[pdf:E03]。因此，本文真正补的缺口不是首次把 LLM 放进控制设计，而是把“离线 surrogate+GA 初值—RTDS 验证—LLM 根据偏差继续调参”串成一个自动闭环，并声称以 control theory（控制理论）知识替代盲目随机搜索。

论文对已有方法“不够”的诊断是具体的：纯离线方法的关键假设是代理模型足够接近 RTDS，但实验显示该假设会破裂；纯在线 GA 则把每个候选都交给 RTDS，成本随 population 和 generation 急剧增长。问题在于，本文没有把 Bayesian optimization、trust-region derivative-free search、CMA-ES、规则化专家调参器或同预算局部搜索纳入实验。也就是说，它证明了“额外在线校准比一次离线验证好”，但尚未证明“LLM 是这部分收益不可替代的来源”。

## § 3 — 重建作者的思考路径

**基于证据的推断。** 可以把作者可能的思考路径重建为五步。

1. 先承认离线 surrogate model 的价值：它能在大参数空间内廉价评估大量候选，因此适合找到一个接近可行域的起点，而不是直接被丢弃。
2. 再观察 RTDS 返回的不只是“成功/失败”，而是一组有物理含义的症状：rise time 太慢、SSE 偏大、IAE 偏大、overshoot 过高。传统专家会把这些症状解释为 proportional gain（比例增益）或 integral gain（积分增益）不足、过强或耦合失衡。
3. 由此把每一次昂贵 RTDS 运行从“黑箱打分”改造成“诊断样本”：用当前参数、四个性能指标、约束违反项和历史调参轨迹，推断下一步应朝哪个方向跳。
4. LLM 适合承担这一层语义推理，因为它能接收自然语言目标、调用 surrogate/GA/RTDS 工具，并按固定机器可读格式输出下一组参数；orchestrator agent（编排代理）负责状态和流程，专用 agent 负责实际执行。四层架构和工具关系见 PDF 物理页 2，Section II-A / Fig. 1 [pdf:E04]
5. 最后采用“两阶段”而不是纯 LLM 搜索：Stage 1 用 NN surrogate+GA 提供较好初值，Stage 2 才让 LLM 在 RTDS 反馈上做少量迭代，以控制昂贵评估次数（PDF 物理页 2，Section II-B）[pdf:E05]

这条思路的关键转折是：作者不再把 controller tuning（控制器整定）只看作一个高维数值优化问题，而是把指标违反模式看作可被工程知识解释的因果线索。论文在 Section II-C 明确声称，LLM 应根据控制参数与性能指标之间的关系做“intentional jump（有意跳跃）”，而不是小幅随机扰动（PDF 物理页 2，Section II-C）[pdf:E06]

## § 4 — 核心 Intuition

先让便宜的 surrogate+GA 把参数带到“可能可用”的区域，再让 RTDS 暴露离线模型没有捕获的偏差。LLM 不把这次偏差仅当作一个 fitness score（适应度分数），而是按控制理论把“哪项指标坏了”翻译成“哪类增益应增减”，从而用少量、有方向的 RTDS 试验跨过 sim-to-real gap。它本质上不是学习一个新的低层控制律，而是在现有优化器、代理模型和 RTDS 之上充当流程编排器与知识驱动的参数决策器（PDF 物理页 2，Section II-B/II-C）[pdf:E05][pdf:E06]

## § 5 — 具体方法与完整 Pipeline

系统采用四层架构：User Layer 接收工程目标；Orchestration Layer 解析目标、维护状态并决定工作流转移；Execution Layer 包含 Offline Optimization Agent 和 LLM Calibration Agent；Tools & Platforms Layer 提供预训练 NN surrogate、GA 和 RTDS。Fig. 1 还显示，最终参数和报告会回传给用户（PDF 物理页 2，Section II-A / Fig. 1）[pdf:E04]

验证对象是并网 MMC 的 cascaded dual-loop（级联双环）控制。作者只优化 outer power loop（外功率环）的四个 PI 参数 KpP、KiP、KpQ、KiQ，inner current loop（内电流环）参数固定；控制结构与被优化位置见 PDF 物理页 2，Section III-A / Fig. 2 [pdf:E07]。Table I 报告的系统条件包括 25 mH 网侧电感、10 mH 桥臂电感、20 个子模块、10 mF 子模块电容、20 kV 直流侧电压、10 kV 网线电压、2 kHz 开关频率，以及内环 Kp=2、Ki=50（PDF 物理页 3，Table I）[pdf:E08]

完整 pipeline 如下。

1. **输入要求。** 用户给出要最小化的主指标、其余指标的约束和增益边界。四个性能量分别是 overshoot、rise time、IAE 和 SSE；其中 overshoot 定义为相对稳态值的最大峰值百分比，rise time 是从最终值 10% 到 90% 的时间（PDF 物理页 2，Section III-B）[pdf:E09]；IAE 是阶跃响应绝对误差的积分，SSE 是最终误差相对参考值的百分比（PDF 物理页 3，Section III-B）[pdf:E08]
2. **离线代理建模。** 作者用 Latin hypercube sampling（拉丁超立方采样）生成 2,000 组四维增益，在 RTDS 上施加 1 MW→2 MW 有功功率阶跃；清洗后保留 1,676 条记录。MLP 有两层隐藏层、每层 64 个神经元，数据按 7:1:2 划分，batch size 为 32，使用 Adam、学习率 0.0001，训练 patience 为 300 epochs（PDF 物理页 3，Section III-C / Fig. 3）[pdf:E10]
3. **离线搜索。** GA 在 NN surrogate 上评估 fitness，population 为 50、generation 为 100，采用 tournament selection、simulated binary crossover（p=0.8）和 polynomial mutation（p=0.1），输出一组初始 KpP、KiP、KpQ、KiQ（PDF 物理页 3，Section III-C）[pdf:E10]
4. **RTDS 验证。** 把初始参数送入高保真实时仿真，得到四个实际指标和违反的约束。
5. **LLM 校准。** 使用 Qwen-Flash，temperature=0.1，最多 10 次尝试；Table III 给出的边界是 Kp∈[0.01,99.9]、Ki∈[0.01,999.9]。prompt 由 Role、Task、Current state、Tools、Requirement、Output format 六部分组成，以便自动解析输出（PDF 物理页 3，Section III-E / Table III）[pdf:E11]
6. **循环与输出。** LLM 根据当前指标、约束违反和调参历史给出解释及下一组参数，RTDS 再验证；成功时返回最终增益和报告，达到 Table III 规定的最大尝试次数仍不可行则判为失败（PDF 物理页 3，Table III）[pdf:E11]。

Problem No. 39 展示了一个完整例子。目标是优化 overshoot，同时要求 rise time≤0.2 ms、SSE≤0.02%、IAE≤57。离线初值在第一次 RTDS 运行中得到 overshoot=1.29%、rise time=0.3 ms、IAE=61.08、SSE=0.016%，因此 rise time 和 IAE 违反约束。LLM 随后先降低 KiP/KiQ、提高 KpP/KpQ；第二次运行虽把 rise time 降到 0.2 ms，却把 SSE 推到 0.059%、IAE 到 61.53，于是第二次建议提高积分增益并略降比例增益。第三次运行得到 overshoot=1.22%、rise time=0.2 ms、IAE=56.87、SSE=0.014%，全部约束满足；总耗时 37.62 s、3 次迭代（PDF 物理页 5，Section IV-C / Fig. 7）[pdf:E12]

论文没有报告 RTDS 仿真步长、solver、开关事件处理、multi-rate scheduling（多速率调度）、I/O 延迟、并行执行、数值精度、随机种子、LLM 的精确版本/系统 prompt、API 重试策略，也没有 FPGA 映射或固定点实现。这些缺失不妨碍理解概念 pipeline，但会阻止严格的 bit-level 或 timing-level 复现。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文没有给出新的控制理论定理、收敛证明、梯度推导或显式优化方程，因此没有可逐式重建的“核心数学推导”。数学对象主要是一个四维黑箱约束优化：四个 PI 增益决定四个性能指标，每次选一个指标作为最小化目标，其余三个作为约束；LLM 负责依据指标模式提出下一组参数，而不是计算解析梯度。

实验组合采用 full-factorial design（全因子设计）：四个指标轮流作为目标，另外三个约束各取三个等级，因此按文字描述应为 4×3³=108 个问题。值得注意的是，论文正文实际印成“4 objectives×3×3 … =108”，少写了一个“×3”；Table II 的 rise time 等级也列为 strict=0.2、moderate=0.05、relaxed=0.1，若这些数字是上限，则严格程度并非单调。这两处都是报告层面的可复现性疑点，不改变作者意图，但要求复现者向作者确认（PDF 物理页 3，Section III-D / Table II）[pdf:E13]

工程上最重要的数学直觉是指标压缩造成的信息损失：同一个 overshoot、rise time、IAE、SSE 四元组，可能来自不同的波形形状、振荡模态或参数敏感度。论文的 LLM 只接收这些指标及历史，未展示对完整时域波形、局部 Jacobian 或不确定性结构的建模；这会在第 9 和第 11 节成为核心压力点。

## § 7 — 实验设计与结论

**问题 1：离线 surrogate 是否足够准确且足够快？** 实验用独立测试集报告四个指标的 RMSE、MAE 和 R²。R² 分别为 overshoot 0.987、rise time 0.969、IAE 0.958、SSE 0.975；正文称离线 GA-NN 平均 1.6 s 完成一个问题（PDF 物理页 4，Section IV-A / Table IV）[pdf:E14]。答案是：对离线数据分布的预测看起来很好，但高 R² 并不保证满足 RTDS 上的硬约束。

**问题 2：sim-to-real gap 是否真实且严重？** 作者把离线 GA-NN 给出的参数放到 RTDS 验证。Fig. 4 中，overshoot 约束的预测成功率为 85.2%，实际验证仅 18.5%；离线方法整体实际成功率只有 13.0%（PDF 物理页 4，Fig. 4 及相邻正文）[pdf:E15]。答案是：离线模型在平均预测误差上很好，但在“是否跨过约束边界”这个离散判据上不可靠。

**问题 3：加入 LLM-RTDS 校准后，整体成功率和成本如何？** 108 个问题中，所提方法成功 86 个，成功率 79.6%，平均 4.56 次 RTDS 运行、57.7 s；离线 GA+NN 成功 14/108，即 13.0%，表中成本为 13.6 s 和一次 RTDS 运行。作者还估计 online GA+RTDS 约需 3,000 次 RTDS 运行、约 8 h，但没有给出其实际成功率（PDF 物理页 4，Table V）[pdf:E16]。答案是：加入少量在线反馈后成功率大幅上升，但这个比较没有控制在线评估预算。另一个成本口径不清之处是：Section IV-A 报告离线 GA-NN 平均 1.6 s，而 Table V 把离线方案写成 13.6 s（含一次 RTDS 运行）；论文没有进一步分解这两部分时间（PDF 物理页 4，Section IV-A / Table V）[pdf:E14][pdf:E16]。

**问题 4：提升是否覆盖所有指标？** Fig. 5 报告所提方法在 overshoot、rise time、SSE、IAE 四类目标上的成功率分别为 88.9%、81.5%、81.5%、66.7%，对应离线基线为 18.5%、18.5%、11.1%、3.7%；整体为 79.6% 对 13.0%（PDF 物理页 4，Fig. 5）[pdf:E17]。答案是：四类都提升，但 IAE 最难，且 66.7% 明显低于其他三类。

**问题 5：成功通常需要多少次校准？** 86 个成功案例多数在 2–4 次内收敛，成功案例平均 3.16 次；22 个失败案例达到 10 次上限，作者将其归因于极严格或冲突的约束（PDF 物理页 4，Fig. 6 及相邻正文）[pdf:E18]。这解释了 Table V 的 4.56 次全体平均与 conclusion 中“约三次”的差异：前者把失败案例的 10 次也算入，后者更接近成功案例均值。

**不能外推的范围。** 实验只有一个 MMC topology、一个 1 MW→2 MW 阶跃场景、固定的内环、四个外环 PI 增益、一个 LLM、一个 prompt 结构和一套由同四指标重组出的 108 个问题。没有跨 topology、跨 operating point、跨 disturbance、跨模型版本、跨随机种子或真实 power hardware 的验证。Table V 也没有给出同样 10 次 RTDS 预算下的强黑箱优化 baseline。因此实验支持“这条自动 pipeline 在该测试床上有效”，但不足以支持“LLM 理论推理普遍优于数值优化”。

## § 8 — Take-aways

**5 句话。** ① 论文把控制器整定拆成“离线 surrogate+GA 找初值”和“LLM+RTDS 做少量校准”两阶段。② 在一个并网 MMC 的四个外环 PI 增益任务上，纯离线方案虽有较高 surrogate R²，却只有 13.0% 的 RTDS 验证成功率，说明约束边界附近的 sim-to-real gap 很关键（PDF 物理页 4，Table IV / Fig. 4）[pdf:E14][pdf:E15]。③ 加入 LLM 校准后，108 个问题中成功 86 个，整体 79.6%，平均 4.56 次 RTDS 运行和 57.7 s（PDF 物理页 4，Table V）[pdf:E16]。④ Fig. 7 表明 LLM 能生成表面上合理、可读的增益调整解释，并在一个案例中三次迭代满足全部约束（PDF 物理页 5，Fig. 7）[pdf:E12]。⑤ 但论文没有同预算、同反馈的非 LLM baseline，因此最大未决问题是收益来自“LLM 的控制知识”还是仅来自“多了几次在线反馈”。

**3 句话。** 这是一套实用的自动化 workflow：用廉价离线模型缩小搜索范围，再用少量 RTDS 反馈修正模型偏差。它在单一 MMC 测试床上把验证成功率从 13.0% 提高到 79.6%，但比较预算不对等（PDF 物理页 4，Table V）[pdf:E16]。论文证明了在线闭环校准有价值，尚未隔离出 LLM 推理本身的因果贡献。

**1 句话。** 最可信的结论是“surrogate 初值加少量高保真反馈远胜纯离线参数”，而不是“LLM 已被证明是最佳校准算法”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**79.6% 的成功主要来自 LLM 的 control-theory-guided reasoning，而不是来自比离线基线更多的 RTDS 评估、任何形式的自适应在线搜索，或手工编码的简单增益规则。** 如果这个假设不成立，论文仍然展示了一套可用的自动编排系统，但“把数值搜索改造成知识驱动推理”的核心技术贡献就会大幅缩水。

论文提供的支持包括：Section II-C 对“有意参数跳跃”的机制描述（PDF 物理页 2，Section II-C）[pdf:E06]；Fig. 7 中两次可读的增益调整理由和第三次成功（PDF 物理页 5，Fig. 7）[pdf:E12]；Discussion 进一步把优势归因于用 theory-guided reasoning 取代 stochastic search（PDF 物理页 5，Section V）[pdf:E19]。但这些证据只证明 LLM 产生了看似合理的文本和参数，不证明文本推理导致了成功。

缺失的证据更关键。离线基线只有一次 RTDS 验证，而所提方法平均 4.56 次、最多 10 次；online GA+RTDS 只是约 8 h 的成本估计，没有实际成功率；没有同样初值、同样 10 次 RTDS 预算的 coordinate search、Bayesian optimization、CMA-ES、finite-difference trust region 或专家规则 baseline（PDF 物理页 4，Table V）[pdf:E16]。此外，论文只报告 Qwen-Flash、temperature=0.1 和 prompt 结构，没有模型版本、完整 prompt、重复运行方差或“去掉控制理论提示”的 ablation（PDF 物理页 3，Table III）[pdf:E11]。所以最合理的判断是：论文证明了系统级效果，但机制归因尚未闭合。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 108 题，而是检验“LLM 是否在相同在线预算下优于简单校准器”。

**数据与模型。** 建一个可快速运行的四参数双环控制仿真，保留 KpP、KiP、KpQ、KiQ 和 overshoot、rise time、IAE、SSE；准备一个低保真模型和一个加入延迟、参数偏移或离散化差异的高保真模型。用约 500–1,000 个 Latin hypercube 样本训练与论文相同规模的两层 64-neuron MLP，并用 GA 找初值；论文原始设置可作为上限参考（PDF 物理页 3，Section III-C / Fig. 3）[pdf:E10]

**实现。** 从 Table II 中选 12 个覆盖宽松、冲突和 IAE 主导的约束组合。每题从同一 GA 初值开始，给每种方法最多 10 次高保真评估：A 为论文式 LLM prompt；B 为 10–20 条固定专家规则；C 为 budgeted coordinate/trust-region search；D 为随机方向搜索。所有方法看到相同四指标和历史，参数边界一致。

**测量。** 记录 constraint satisfaction rate、达到可行解所需高保真运行次数、总 wall time、跨 5 个随机种子的方差，以及每步参数移动后指标改善量。

**支持标准。** 在相同 10 次预算下，A 的成功率比最强非 LLM baseline 高至少 15 个百分点，且在多数种子上保持优势；同时去掉 control-theory 提示后性能显著下降，才支持“知识驱动 LLM 推理”这一核心 claim。

**反驳标准。** B 或 C 达到与 A 相当的成功率/评估次数，或者 A 的优势在换随机种子、改指标名称、改变低高保真偏差后消失，就说明论文的主要收益来自在线闭环与额外预算，而不是 LLM 特有能力。

## § 11 — 最强反例设计

最强反例不是再找一个“更难的约束”，而是构造一对 **metric-aliased plants（指标混叠对象）**：在同一初始四个 PI 增益下，两套高保真模型给出完全相同的 overshoot、rise time、IAE、SSE，却具有相反的局部参数敏感度。例如，Plant A 中提高 KpP 会缩短 rise time，而 Plant B 因额外延迟或非最小相位效应，提高 KpP 反而增加振荡并恶化 IAE。由于论文 agent 的状态主要是四个标量指标、约束和历史，在第一次调参前它无法区分这两个 plant；temperature=0.1 的同一 prompt 很可能给出相同方向的“理论合理”动作，于是至少对其中一个对象系统性走错。

实验上，先通过参数化延迟、零点位置和 cross-coupling 构造 20 对这样的 plant pair；对每对都让论文式 agent、主动 finite-difference Jacobian 方法和同预算 trust-region 方法从同一初值运行，最多 10 次。若 LLM 在成对对象上频繁出现“一边成功、另一边沿相同方向失败”，而先用两次小扰动估计局部敏感度的方法稳定成功，就得到一个直接反例：四个性能标量不足以支持论文声称的 cause-and-effect reasoning，语言模型调用的是通用控制先验，而不是当前 plant 的可识别因果结构。

这个反例也能排除“只是约束更严格”的替代解释，因为两对象初始指标和约束完全相同；差别只在未被 agent 观测的局部动力学。论文自己承认 IAE 这一累积指标成功率较低，并计划改进 prompt（PDF 物理页 5，Discussion limitations）[pdf:E20]，这与“标量状态不足以区分不同波形和敏感度”这一攻击方向一致，但论文尚未做该测试。

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty。主押注：主动激励驱动的 waveform-level sim-to-real operator learning（波形级仿真差异算子学习）。** 新研究问题是：能否不再对每个约束组合逐题猜增益，而让 agent 主动设计少量 RTDS 激励与参数扰动，学习一个可跨目标复用的、从低保真预测到 RTDS 时域响应的局部差异算子？一旦成功，一次校准 session 就能服务许多新的 overshoot/IAE/SSE 目标，甚至在目标改变时无需重新从头迭代。

核心机制的因果链是：本文目前固定使用 1 MW→2 MW 阶跃，并把整条响应压缩成四个标量；108 个任务也主要是同四个指标和阈值的重组（PDF 物理页 3，Section III-C/III-D）[pdf:E10][pdf:E13]。新方法让 agent 同时选择 excitation waveform（例如多级阶跃、chirp 或受限伪随机序列）和小幅增益探针，RTDS 返回完整时域波形；随后拟合一个带记忆的局部 state-space/operator model，描述“surrogate 波形—RTDS 波形”的动态差异及其对四个增益的敏感度。LLM 的角色从直接猜下一组增益，改为提出可辨识性假设、选择最有信息量的实验并解释所得算子；参数更新则由这个可检验的动态模型计算。

它至少改变四个基本设计变量：数据生成方式从固定阶跃变为 active excitation；状态表示从四个标量变为时域算子/latent state；研究目标从逐题可行性搜索变为跨目标 amortized calibration（摊销校准）；评价对象从单题成功率变为波形预测、参数敏感度识别和新约束零/少样本迁移。论文中特别支持这一押注的实验细节是：Fig. 7 的 LLM 需要在 rise time、SSE 和 IAE 之间来回修正，说明四个指标之间存在未显式建模的耦合（PDF 物理页 5，Fig. 7）[pdf:E12]；Fig. 5 和 Discussion 又显示 IAE 成功率最低，作者自己把它归因于累积性能标准更复杂（PDF 物理页 4，Fig. 5；物理页 5，Discussion）[pdf:E17][pdf:E20]。这提示真正缺失的可能不是更长 prompt，而是包含时间结构的观测。

最大研究收益是把 RTDS 校准从“每个新要求做几次黑箱试探”变成“少量主动实验后获得可复用的动态差异模型”，从而支持目标重设、operating point 迁移和后续 controller co-design。最大科学风险是：强非线性、饱和和 topology 变化可能使局部算子迅速失效；主动激励也可能无法在有限幅值内充分识别关键模态。

首个可证伪实验应在同一 MMC 上限定总共 3 次 RTDS 探针，比较三组方法：主动选择波形和参数扰动、固定 1→2 MW 阶跃的原 LLM 流程、随机探针。随后不给额外校准预算，要求三者预测 held-out 波形并解决 12 个新约束组合。只有主动方案同时降低波形预测误差、正确恢复参数敏感度，并在新目标上显著提高可行率，才支持“可辨识动态差异算子”这一机制；若优势仅来自看到更多样本或更长波形，则机制被否定。

与本文当前方法的实质区别是：本文把 surrogate 映射定义为“4 个增益→4 个指标”，采用固定阶跃并逐题调参；新押注学习“增益、激励、历史状态→完整 RTDS 响应差异”的时间对象，并把实验选择本身设为决策变量。与本文引用的 surrogate/OSMPT 路线和 objective-oriented LLM multi-agent work [11] 的比较只能依据本 PDF 的描述与题名：前者侧重静态离线映射，后者至少已涉及 LLM 多代理控制设计，但本 PDF 不足以核验它们是否已有相同 active operator 机制，因此这里明确不宣称新颖性（PDF 物理页 1，Section I；物理页 6，Reference [11]）[pdf:E02][pdf:E03]

**Wild-card alternative：** 让 LLM 不再只调四个 PI 增益，而是联合生成 controller graph（控制器拓扑）并搜索采样率、fixed-point 位宽、pipeline 深度和 FPGA 并行映射，再由 RTDS 评价闭环动态；这把研究对象从“参数校准”改为“控制结构—数值表示—硬件时序”共同设计，机制与主押注完全不同。
