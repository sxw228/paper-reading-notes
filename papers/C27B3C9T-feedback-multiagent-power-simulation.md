# Enhancing LLMs for Power System Simulations: A Feedback-driven Multi-agent Framework

作者：Mengshuo Jia；Zeyu Cui；Gabriela Hug  
出处：未报告（源 PDF 为 2025 年 5 月稿件，未显示正式卷期）  
年份：2025  
DOI：10.1109/tsg.2025.3589114  
Zotero key：C27B3C9T  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是“让 LLM 直接求解某个 power-flow 方程”，而是更工程化的问题：**怎样让 Large Language Model（大语言模型，LLM）把自然语言 simulation request 转成语法正确、参数精确、可以真实执行的 power-system simulation code，并在出错后自行修正**。作者把现有 LLM 的失败归结为三类能力缺口：simulation-specific knowledge 不足、复杂任务的 reasoning 不足，以及 function、option 与依赖关系处理不精确；更细的诱因包括训练语料中的领域知识低频、缺少高质量带解释的代码、任务需要多步推理，以及参数与函数之间的精密逻辑容易发生 semantic drift。该问题定义与原因列表见 PDF 物理页 1 的 Abstract、Introduction 右栏。[pdf:E01] [pdf:E02]

论文直接陈述的工程价值有三层。第一，研究者可以把精力从重复的 simulation implementation 转向实验设计与科学判断；第二，自然语言可以作为异构 upstream/downstream tasks 的接口，把原本难以用普通代码粘合的多模态输入输出连起来；第三，它可能把 power-system programming 推向更接近 natural-language coding 的交互方式。作者在 69 个 DALINE 与 MATPOWER 任务上报告完整框架成功率分别为 93.13% 和 96.85%，并报告单任务约半分钟、token 成本约 0.014 USD；这些是论文声称该问题值得解决的直接量化依据，定位于 PDF 物理页 1 的 Abstract。[pdf:E01]

需要明确范围：本文研究的是**仿真工作流编排与代码生成层**，验证环境是 DALINE 和 MATPOWER。它没有提出新的 EMT 离散模型、开关事件处理、多速率时间推进、fixed-point 数值表示或 FPGA mapping。因此，它对 EMT/FPGA 的直接价值不是“更快求解”，而是可能作为自然语言到既有 simulation backend 的上层入口；硬实时性和硬件执行正确性都没有被本文验证。

## § 2 — 前人工作与不足

论文转述的相关工作主要分成两类。第一类把 LLM 用于 power systems 的外围或相邻任务，例如把语言规则翻译成 OPF constraints、解释 real-time market 中的 reinforcement-learning 决策、检索与总结文档、利用历史数据迭代求 OPF、收集 EV charging preference、做 carbon accounting、cybersecurity、forecasting、公众接受度分析和 energy-domain benchmark。第二类更接近本文，即讨论 LLM 执行 power-system simulations、展示当前能力，或让 LLM 生成通用研究代码。作者认为这些工作证明了潜力，但没有系统处理本文指出的 knowledge、reasoning、function/option precision 三个瓶颈；相关工作综述与作者的差距判断见 PDF 物理页 2，Section I 及 Fig. 1 邻近正文。[pdf:E03]

作者对 standard Retrieval-Augmented Generation（检索增强生成，RAG）的批评是具体的：把整个复杂 request 当作一个 retrieval query，会把“该调用什么 function”和“该设置什么 option”混在一起，无法保留多子请求及依赖关系。论文还说明本文是作者先前 DALINE 工作的 substantial extension，并扩展到熟悉与不熟悉的 simulation tools、更多策略组合和系统消融；case-study 设计及“870 coding files 将在接收后公开”的说明位于 PDF 物理页 7，Section V 开头。[pdf:E04]

论文直接声称这是首个 systematic approach，但本任务按输入协议不联网，无法独立核验这一 novelty。更稳妥的结论是：**从源 PDF 可确认的新增组合**是 adaptive query planning、function-option-dependency triple knowledge base、structured reasoning agent 与 execution feedback 的一体化设计，并在两个工具上做了较完整的 ablation；“是否最早”只能视为作者 claim，而不是本卡认证的文献结论。

## § 3 — 重建作者的思考路径

以下是基于全文证据的逆向重建，不把论文贡献预设为必然答案。

1. 先观察到：即使 MATPOWER 这类成熟工具可能出现在 pre-training data 中，LLM 仍会写错简单 power-flow/OPF code；因此问题不只是“模型没见过文档”，而是知识调用方式和参数级精度不够。作者在 PDF 物理页 1 把失败进一步分成 frequency、quality、complexity、precision 四个来源。[pdf:E02]
2. 再抽象 simulation code 的共同结构：无论具体 toolbox 如何变化，用户请求最终都要落到“调用哪些 functions、设置哪些 options、这些 options 依赖哪些 functions”。如果 retrieval 仍以整段 request 为单位，最容易丢失的正是这种结构。Section II-A 对 whole-request RAG 的批评及 function/option 分解见 PDF 物理页 4。[pdf:E05]
3. 仅把正确片段检索出来仍不够，因为 coding agent 还要按顺序完成 function identification、syntax learning、option extraction 与 code generation。于是需要把 role、task、reasoning path、basic knowledge 和 retrieved knowledge 都显式写入 structured prompt；该 reasoning path 位于 PDF 物理页 5，Section III-B。[pdf:E06]
4. 即使一次生成有误，simulation environment 仍能提供比语言模型自我反思更有约束力的信号：真实 interpreter/solver 的 error message、problematic code 和历史尝试。作者因此把执行错误重新包装成 retrieval 与 correction request，形成闭环；具体 error report 字段与模块联动见 PDF 物理页 6，Section IV-A 至 IV-C。[pdf:E07]
5. 最后得到一个系统性假说：高成功率不会由单一 prompt trick、单一 RAG 或单一 fine-tuning 带来，而来自“结构化检索 + 结构化推理 + 环境反馈”的协同。后续 Table I 的组合消融就是对这一假说的实验化表达。[pdf:E08]

## § 4 — 核心 Intuition

把复杂 simulation request 当成一段普通文本去检索，会把 function、option 和 dependency 混成一团；应先把请求解析成这些可执行语义单元，再分别检索精确知识，Fig. 2 展示了这一核心分解。[pdf:E09] Coding agent 随后用固定的 reasoning scaffold 把这些单元装配成代码，而不是仅依赖模型“记得”某个 toolbox。代码进入真实环境执行后，error report 被转成下一轮 retrieval/correction request，Fig. 5 展示了这个反馈闭环。[pdf:E10] 因而本文真正的 intuition 是：**把 LLM 的一次性代码生成，改造成由 simulator documentation 和 execution signal 共同约束的迭代程序合成过程。**

## § 5 — 具体方法与完整 Pipeline

完整系统包含 Retrieval Agent、Coding Agent 和 Environmental Acting Module 三类角色。Fig. 1 把它们组织成 enhanced RAG、enhanced reasoning 与 feedback-driven acting 三个模块；模块间传递 retrieval results、simulation code、simulation result 和 error signal，定位于 PDF 物理页 2。[pdf:E03]

**1. 预构建 knowledge base。** 普通 manual 先被 chunk、embedding 并写入 vector database。作者额外构建 triple-based structured option document：每条记录至少包含 option name 与 default value/format、该 option 对应的 function dependency，以及 option description 与候选值；初稿由 ChatGPT-4o 从 manual 中提取，再由 domain experts review。论文给出的具体步骤与 `runuopf` 例子位于 PDF 物理页 4，Section II-A/II-B：面对“IEEE 24-bus RTS 上做带昂贵机组 de-commitment 的 AC OPF”，agent 不停留在泛化短语，而映射到具体 MATPOWER function `runuopf`。[pdf:E11]

**2. Adaptive query planning。** Retrieval Agent 先做 semantic recognition，把请求分成 function-related query 与 option-related query；每类再拆成多个 sub-query。随后做 keyword mapping：function sub-query 映射到 function name，option sub-query 映射到 option description 和 value，最后并行检索。该过程与 few-shot Chain-of-Thought（思维链，CoT）prompt 见 PDF 物理页 3，Fig. 2；正文强调这种结构不只是 keyword extraction，而是把隐含描述映射为可执行 API 术语。[pdf:E09] [pdf:E05]

**3. Enhanced reasoning。** Coding Agent 的 prompt 明确四件事：它是谁、要做什么、怎样逐步做、需要知道什么。通用 reasoning actions 是 function identification、function syntax learning、option information extraction、code generation；tool-specific examples 只负责把这些动作落到特定 API。PDF 物理页 5 的 Section III-B 给出动作序列，[pdf:E06] 物理页 6 的 Fig. 4 给出完整 prompt layout 与 code-generation workflow。[pdf:E12]

**4. 静态与动态知识合并。** Static basic knowledge 提供基础 functions 和 syntax；dynamic retrieval knowledge 提供当前 request 所需的 option format、value 和 function dependency。运行时用 placeholder 把 retrieval results 填入 reasoning prompt，再交给 Coding Agent。该双层知识设计位于 PDF 物理页 5，Section III-C/III-D。[pdf:E13]

**5. 执行与反馈。** 生成代码通过 simulation environment API 执行。若出现 error，系统生成包含 problematic code、error message、general hints、correction request、reminders 和 chat history 的 report；该 report 既作为 Retrieval Agent 的新 query，也作为 Coding Agent 的修正输入。若 `err` 为空则直接输出，若不为空则循环到 maxAttempts；模块图见 PDF 物理页 7，Fig. 5，[pdf:E10] 完整 pseudocode 见 PDF 物理页 8，Algorithm 2。[pdf:E14]

**用论文中的复杂任务说明。** Fig. 6 的 MATPOWER Complex Task 8 同时要求：对 IEEE 57-bus case 做 AC OPF、指定 MIPS、设置多种 tolerance、coordinate representation、branch-flow limit、generator voltage setpoint、soft limits 与输出选项；又要求对 51-bus radial system 做另一项 AC power flow，并指定 Newton–Raphson 与 mismatch tolerance。这里 request 不是一个“AC OPF”关键词，而是两个 function-level sub-requests 加一长串彼此依赖的 options。按本文 pipeline，Retrieval Agent 应先分离两个 simulation calls，再为每个 call 检索相应 options；Coding Agent 按函数、语法、参数、代码顺序组装；执行错误再触发局部重检索。任务原文与其 option 密度见 PDF 物理页 10，Fig. 6。[pdf:E15]

**EMT + FPGA 视角的缺项。** 本文未报告 network differential equations、switching/event semantics、solver time step、multirate schedule、parallel dependency graph、fixed-/floating-point representation、resource utilization、timing closure 或 FPGA platform。它只在 API orchestration 层说明 parallel retrieval；因此不能从本文推出 real-time EMT 性能或 FPGA 可实现性。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有提出新的 power-flow、OPF 或 data-driven linearization 数学模型，核心方法是 software/agent architecture。唯一需要解释的正式数学是实验评分，它把“要求是否完成”和“用了多少次尝试”合成一个 success rate。对任务 \(t\) 的第 \(i\) 次尝试，作者定义：完全满足要求且无无关设置得 100 分；满足要求但含不影响完成的冗余设置得 50 分；任一要求未满足得 0 分，即

\[
P_{t,i}\in\{100,50,0\}.
\]

若任务 \(t\) 最多允许 \(N_{\max}^{(t)}\) 次尝试，则

\[
S_t=\sum_{i=1}^{N_{\max}^{(t)}}P_{t,i},
\qquad
R_{\mathrm{overall}}=
\frac{\sum_{t=1}^{T}S_t}
{\sum_{t=1}^{T}\left(100N_{\max}^{(t)}\right)}\times100\%.
\]

公式、100/50/0 定义、unused attempts 继承最后一次已执行得分的规则，以及 DALINE 取 3 次、MATPOWER 取 5 次，均见 PDF 物理页 9，Section V-A。[pdf:E16]

这个指标的 intuition 是：若第一次就得到 100，后续未用 attempts 都按 100 计，任务获得满分；若先失败再成功，前面的 0 会留下惩罚，因此它同时衡量最终 correctness 与 correction efficiency。一个重要副作用是：**只有 execution error 才触发下一次尝试，但“可执行却未满足需求”的代码可能由人工评分判为 0，却不会自动进入反馈循环。** 这使训练时的可用 signal 与最终评价对象并不完全一致，也是后文最关键的脆弱点。

## § 7 — 实验设计与结论

**问题 1：原始 LLM 能不能可靠执行 power-system simulations？ → 实验：**作者选择 34 个 DALINE tasks 与 35 个 MATPOWER tasks；DALINE 在所用 LLM 更新之后发布，被视为 unseen tool，MATPOWER 被视为 seen tool。MATPOWER 中有 8 个 complex tasks 和 27 个 standard tasks。RAG 的 text/PDF chunk size 分别为 30/50 words，return number 为 20；LLM temperature 为 0.1、max tokens 为 4096；DALINE 和 MATPOWER 的 max attempts 分别为 3 和 5。设置见 PDF 物理页 8，Table II 与 Section V-A。[pdf:E17] **答案：**环境执行与反馈本身远远不够。DALINE 上 GPT4o-Sole 在 complex/standard tasks 都为 0%；MATPOWER 上 GPT4o-Sole 与 o1-preview 在 complex tasks 都为 0%，GPT4o-Sole 在 standard tasks 也只有 27.77%。[pdf:E18] [pdf:E19]

**问题 2：standard RAG 是否足够？ → 实验：**在相同环境中比较 whole-request standard RAG、OpenAI built-in RAG 与 enhanced RAG。**答案：**DALINE 上 GPT4o-SR 和 CGPT4o-R 的 all-task success rate 分别只有 31.37% 与 33.82%；MATPOWER 上 GPT4o-SR 在 complex/standard tasks 分别为 13.75% 与 52.96%。这说明“检索到 manual 片段”不等于“正确解析 function-option dependency”。DALINE 的具体比较见 PDF 物理页 9，Section V-B，[pdf:E18] MATPOWER 的具体比较见 PDF 物理页 12，Section V-C。[pdf:E19]

**问题 3：完整框架的提升来自单一模块还是协同？ → 实验：**Table I 组合出 Full、去 query planning、去 triple document、去 reasoning、去 few-shot CoT、换 standard RAG、去高质量 error reporting 等 schemes；Table I 的策略矩阵位于 PDF 物理页 7。[pdf:E08] **答案：**DALINE 上 GPT4o-Full 为 93.13%；去 triple document 的 GPT4o-NP 降到 81.37%，去 few-shot CoT 的 GPT4o-NCS 降到 65.19%，去 query planning 时 complex-task success rate 降到 66.67%。MATPOWER 上 Full 为 96.85%，其中 complex/standard 为 93.75%/97.77%；去 enhanced reasoning 后 overall 为 89.71%、complex 为 70.00%，去 query planning 后 overall 为 63.42%、complex 为 37.50%。作者据此把主要结论表述为 cumulative/synergistic effect，而不是某个单项策略独占增益。[pdf:E18] [pdf:E19]

**问题 4：environmental feedback 是否真的完成了 error correction？ → 实验：**比较 first-attempt 与 final-attempt success rate，并统计成功任务需要的 attempts。DALINE 的 score、success-rate 与 attempt distributions 见 PDF 物理页 11，Fig. 7–9。[pdf:E20] **答案：**final attempt 通常高于 first attempt，Full 多数任务一到两次完成；但收益强烈依赖 simulation tool 是否给出清楚、code-specific 的 error message。去掉 well-developed error reporting 的 GPT4o-RSRNW 在 DALINE 上降到 78.43%，且 first/final 差别很小，相关分析位于 PDF 物理页 10，Section V-B-4/Remark 4。[pdf:E21]

**问题 5：Supervised Fine-Tuning（监督微调，SFT）能否替代 external retrieval？ → 实验：**MATPOWER 上用 50 个随机任务形成 24,249-token SFT dataset；DALINE 上甚至把全部 34 个 test tasks 加 16 个额外任务放进 training，形成 32,346 tokens，再比较 GPT4o-Sole-SFT、Sole 和 Full。**答案：**MATPOWER standard tasks 上 SFT 从 35.18% 提到 51.11%，但 Full 从第二次尝试起所有任务都得到 100 分；DALINE Table III 中 SFT overall 为 51.961%，Full 为 95.098%，complex tasks 分别为 28.571% 与 95.238%。这些设置和结果见 PDF 物理页 12，Section V-D 与 Table III。[pdf:E19] 作者把差距解释为 SFT 是 lossy compression，只能较好吸收 style、tone、format 等 coarse-grained pattern，难以保留 option-level 的高精度细节；该解释位于 PDF 物理页 13。[pdf:E22] 这是作者解释，不是本文单独证明的普遍理论。

**问题 6：给更多反馈次数，baseline 最终会不会追上？ → 实验：**把 attempt budget 扩到 50，并用 3、4、8、12、16 个 sub-queries 表征逐级复杂任务。Fig. 16 显示三种结束状态：满足全部 sub-queries、无 execution error 但仍不满足要求、达到最大 iterations；见 PDF 物理页 15。[pdf:E23] **答案：**baseline 会因 invalid option name、合法 option name 配错误 value、遗漏 critical option 等原因长期失败；有些错误代码可执行却语义错误。Full 在这些任务上全部完成，仅最难任务第一次误用 option name，第二次修正。具体 failure modes 与 50-loop 观察见 PDF 物理页 14，Section V-E。[pdf:E24]

**问题 7：代价是否足以支持研究工作流？ → 实验：**统计 retrieval、reasoning、code generation、execution、aggregation 和 correction 的端到端平均时间与 token cost。**答案：**Table IV 报告 DALINE 为 29.446 s、0.014 USD，MATPOWER 为 32.703 s、0.013 USD；作者强调这些只是受多环节波动影响的近似量。Table IV 与 conclusion 位于 PDF 物理页 15。[pdf:E25]

**不得外推的范围。** 第一，只有两个 software environments，且 task family、manual、knowledge base 与 error-reporting quality 都由作者控制。第二，最终 0/50/100 scoring 是 human experts 手工完成，不是框架内生的 semantic judge。[pdf:E16] 第三，论文没有报告独立复现、跨机构 users、真实研究项目的长期交互，也没有 EMT/FPGA workload。第四，model/API version 与 cost 会变化；本文数字只能描述论文当时的实验配置，不能视为稳定产品指标。

## § 8 — Take-aways

**5 句话：**① Power-system simulation code 的难点不只是缺知识，而是必须精确恢复 function、option 与 dependency。② Standard RAG 把整个 request 当单一 query，无法稳定处理复杂 sub-requests。③ Adaptive query planning、structured knowledge、structured reasoning 与 environment feedback 协同时，论文在 DALINE/MATPOWER 上报告 93.13%/96.85%。[pdf:E25] ④ Feedback 的价值取决于 simulator 能否暴露清晰的 execution error；可执行但语义错误的代码仍是盲区。⑤ 本文证明的是 agent orchestration 在两个 API-based tools 上有效，不是 EMT 数值求解或 FPGA real-time implementation 已经解决。

**3 句话：**① 先把 request 编译成 function-option 语义，再检索和生成代码，比对整段自然语言做 RAG 更有效。② 真实 environment 能把一部分 hallucination 转成可行动的 error signal，但无法自动发现所有 requirement failure。③ 最大贡献是系统组合及实证消融，最大风险是把“无 execution error”误当成“simulation 正确”。

**1 句话：**这篇论文把 LLM simulation 从一次性写代码改造成 documentation-grounded、environment-in-the-loop 的迭代合成系统，但其上限由错误是否可观测决定。

## § 9 — 最脆弱的假设

**最脆弱的假设是：所有会破坏任务正确性的关键错误，最终都会以可利用的 documentation 或 execution-time error signal 暴露出来。** 作者在 Remark 2 明确把框架建立在“simulation tool 能由人凭充分文档学会”的前提上；没有文档时，需要另行生成文档。该前提见 PDF 物理页 7。[pdf:E04] Algorithm 2 又规定：只有 `err != null` 才进入反馈循环，`err == null` 就输出结果；见 PDF 物理页 8。[pdf:E14]

如果 option name 合法、代码可运行、solver 也收敛，但 option value、default behavior、物理约束或某个 sub-request 被错误处理，simulation environment 可能不会报错。此时 Retrieval Agent 和 Coding Agent 都得不到新信号，系统会把一个 plausibly wrong result 当成完成。论文自己的实验已经显示 error-reporting quality 下降时 feedback 几乎失效，[pdf:E21] 并在 conclusion 明确承认框架有时无法发现 “non-execution-bug” failures，导致 unaware、inaccurate outputs 无法自动修正；见 PDF 物理页 16。[pdf:E26]

失败代价之所以最大，是因为它不是降低一点 success rate，而是破坏“自动 research assistant”的可信闭环：离线实验还有 human expert 手工评分能发现遗漏，但真实自动化流程没有这个外部裁判。论文尚缺的核心证据是：在 deliberately constructed、solver-convergent、numerically plausible yet semantically wrong tasks 上，框架能否自行发现错误；没有这项证据，93%–97% 的结果不能外推到 silent failure 占主导的工具或任务。

## § 10 — 最小复现实验

一周内最值得复现的不是全部 69 个 tasks，而是本文最核心的因果 claim：**function/option 分解与 dependency-aware retrieval，是否在相同模型、相同 context budget 下优于 whole-request RAG。**

- **数据：**从 MATPOWER 任务模式中手工构造 12 个 tasks：8 个 standard、4 个 complex；每个 complex task 含 4–10 个明确 sub-requests。覆盖 AC power flow、AC OPF、CPF、solver choice、tolerance、branch-flow limit、generator reactive limits 和 output suppression。Fig. 6 可直接提供任务粒度和 option 密度参考，见 PDF 物理页 10。[pdf:E15]
- **金标准：**为每个 task 建立三份人工 gold：required function list、required option/value/dependency list、可执行 benchmark code。评审时保留论文的 0/50/100 规则，同时增加“function recall”“option exact-match”“漏掉 sub-request 的比例”。
- **三种实现：**A 为 whole-request standard RAG；B 为 function/option sub-query planning + 同一 manual vector store；C 为 B 加 triple-based option document。三者使用同一个 LLM、同一 prompt token 上限、同一 retrieved-token 总量和同一 environmental feedback，避免把“检索更多文字”误当成结构优势。
- **配置：**可对齐论文的 temperature 0.1、max tokens 4096、return number 20、MATPOWER max attempts 5；这些值位于 PDF 物理页 8，Table II。[pdf:E17]
- **支持标准：**若 B/C 在 complex tasks 的 full-requirement success rate 上稳定高于 A，且主要增益来自 option exact-match 和 sub-request completeness，而不是更多 tokens 或更多 attempts，则支持作者机制。
- **反驳标准：**若在严格 equal-context、equal-call 条件下优势消失，或者 A 只要加入相同的 structured prompt 就追平 C，则说明收益主要来自 prompt scaffolding/context volume，而不是 triple dependency retrieval 本身。

这个复现实验不要求重建所有 agents，也不依赖作者尚未随 PDF 提供的 870 个 code files，却能直接检验最有辨识力的设计变量。

## § 11 — 最强反例设计

最强反例不是让 simulator 返回更模糊的 error message，而是构造一组 **converged-but-wrong** tasks：代码始终可执行、solver 始终返回数值结果，但其中一个 function/option 的语义悄悄偏离 request。

具体做法是建立 30 组成对任务，每对只改变一个会改变物理意义但通常不触发 syntax/runtime error 的设置，例如 AC 与 DC formulation、branch-flow limit 的定义、是否 enforce generator reactive-power limits、voltage coordinate representation、CPF target scaling、或正确 option name 搭配错误但合法的 value。论文的 representative tasks 已包含这些 option 类型，见 PDF 物理页 10，Fig. 6。[pdf:E15] 为了排除 retrieval failure，可直接把正确 manual chunk 与正确 triple record 放入 context；这样攻击的对象是 reasoning/feedback mechanism，而不是 knowledge availability。

评价不看“有没有报错”，而看 request compliance、关键物理 invariant 和与 gold benchmark 的结果一致性。若 Full 在 `err == null` 后停止，并在大量 pair 上输出 plausible but wrong code，那么 feedback loop 无论给 5 次还是 50 次预算都不会启动。论文在 50-attempt stress test 中已经观察到“正确 option name + 错误 parameter value”会产生 executable but incorrect code，也观察到遗漏 critical settings 后提前结束；见 PDF 物理页 14。[pdf:E24] Fig. 16 还把“无 execution error 但未满足全部 sub-queries”单列为一种终止状态，见 PDF 物理页 15。[pdf:E23]

这个反例若成立，会给出更强的替代解释：论文的高成功率可能部分来自所选 tasks 经常把错误转成显式 exceptions，加上 human expert 的事后评分，而不是系统已经具备一般性的 semantic self-correction。作者在 PDF 物理页 16 对 non-execution bugs 的承认，使该攻击不是臆测，而是对其已知失效模式的集中放大。[pdf:E26]

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty：自然语言到“可编译的 typed experiment graph（带类型实验图）”，而不是直接到某个 toolbox 的脚本。** 由于本任务不联网，下面只能与论文内所述工作比较，不能认证它相对全部最新研究的首创性。

**新的研究问题。** 能否让 agent 先生成一个独立于 DALINE、MATPOWER 或未来 EMT/FPGA backend 的 experiment intermediate representation（实验中间表示，IR），其中节点表示 physical/simulation operations，端口带 data type、unit、shape、time semantics，边表示 function-option dependency、数据流和执行顺序；随后再由 backend compiler 生成各工具代码与硬件执行计划？

**首次使什么成为可能。** 同一自然语言实验可以迁移到不同 simulators，而不是每换一个工具就重写 prompt、few-shot examples 和 tool-specific code；更进一步，experiment graph 可以成为可组合的研究对象，支持把 data generation、power flow、parameter sweep、model training、result comparison 以及未来 CPU/FPGA partition 放在同一个显式结构里。主要收益是**跨工具实验可移植性与算法—执行架构共同设计**，而不是仅仅多一层错误检查。

**核心机制与因果链。** 本文的 Retrieval Agent 已经把 request 拆成 function 与 option sub-queries，且 triple document 显式保存 option-function dependency，见 PDF 物理页 3–4 的 Fig. 2 与 Section II-B。[pdf:E09] [pdf:E11] 下一步不再把这些结构压回自由文本，而是：① 把每个 sub-query 变成 typed graph node；② 用 triple dependency 约束合法 edge；③ 让 reasoning agent 补齐 node parameters 与 dataflow；④ 由 tool compiler 生成 MATLAB/Python/API code，或把规则、稠密线性代数与 streaming kernels 分区到 CPU/FPGA；⑤ execution result 作为 graph state 返回，供后续节点消费。因果链是“显式语义对象 → 后端无关组合 → 后端编译 → 跨工具复用”，其基本能力在删除 experiment graph 后就不存在，因此不是给原框架加一个 wrapper。

**改变的基本设计变量。** 它至少改变四项：输出 representation 从 text code 变成 typed graph；研究目标从单工具 task completion 变成 cross-backend experiment portability；系统边界从 LLM + one simulator 扩展为 LLM + compiler + heterogeneous backends；评价对象从一次代码是否成功变成 graph semantics、backend compilation coverage 与跨工具结果一致性。若进入 FPGA，time scale、numeric representation 与 hardware mapping 也会成为一等设计变量，而不是论文当前未报告的外部细节。

**论文特异依据。** 方法侧，作者反复证明 function、option 和 dependency 是 simulation coding 的稳定骨架，并把 reasoning 固定为 function identification、syntax、option extraction、code generation；见 PDF 物理页 5–6。[pdf:E06] [pdf:E12] 实验侧，去 query planning 后 MATPOWER complex-task success rate 从 Full 的 93.75% 降到 37.50%，而增加 sub-queries 会系统性放大 baseline 失败；见 PDF 物理页 12 和 15。[pdf:E19] [pdf:E23] 这说明“显式可组合结构”是比单纯增加 model scale 更有希望的扩展轴。作者又承认 text code 会出现 silent non-execution bugs 和用户意图不充分的问题，见 PDF 物理页 16；experiment IR 至少提供了一个可以显式表达需求与依赖的对象。[pdf:E26]

**最大研究收益与最大科学风险。** 最大收益是把自然语言 simulation assistant 从“会写某个工具的脚本”提升为“会设计、迁移并映射完整实验”，从而让 unseen-tool adaptation 与 hardware co-design 共享同一语义层。最大风险是不存在足够统一的 graph ontology：DALINE 的 data/model workflow 与 MATPOWER 的 steady-state solver semantics 差异很大，EMT/FPGA 还会引入离散事件、时间步和资源约束；IR 可能退化为最低公分母，或被 tool-specific extensions 再次碎片化。

**首个能区分机制与最强替代解释的实验。** 构建 30 个含 3–16 个 sub-queries 的 held-out tasks，并选择两个独立 backend 表达同一小型 AC power-flow/OPF intent。比较四组：原论文 text-code pipeline、同样 structured prompt 但输出 JSON text、typed graph + 单 backend、typed graph + held-out backend compiler。所有组使用相同 LLM、retrieval corpus、token budget 和 calls。关键指标不是单一 execution success，而是 held-out backend 的 zero-/few-shot compilation rate、sub-query semantic completeness、graph reuse ratio 与人工修改量。若 typed graph 只在已见 backend 上更整齐，却不能提高 held-out backend transfer，就说明收益只是 serialization/prompt discipline；若它在相同 context 下显著提升迁移与组合，则支持“显式实验对象”这一核心机制。

**与论文内最近工作的实质区别。** 论文内 prior work 和本文都把最终 experimental object 视为某个工具的 code，区别主要在 RAG、prompting、SFT 和 feedback；本押注把 problem 改成 experiment compilation，把 mechanism 改成 typed IR + backend compiler，把 representation 改成 dependency/dataflow graph，把 experimental object 改成可跨 simulator 与 hardware target 复用的实验本身。

**Wild-card alternative：**让 agents 通过成对参数扰动与主动激励，从 simulator 的输出响应中学习 option-function 的因果语义，生成 behavioral knowledge base；这条路线改变的是数据生成与测量机制，而不是 experiment representation。
