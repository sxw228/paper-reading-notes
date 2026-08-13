# A Large Language Model-Based Framework for Generating Simulation Models of Power Systems

作者：Duange Guo、Shanyu Li、Yushi Liu、Xingyu Shi、Shan Jiang、Ye Zhu、Georgios Konstantinou、Mengxuan Shi  
出处：2025 IEEE PES GTD Grand International Conference and Exposition Asia（GTD Asia）  
年份：2025  
DOI：10.1109/GTDAsia60461.2025.11313242  
Zotero key：5GC6TK97  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**结论：论文要解决的不是一般意义上的“让 LLM 写代码”，而是让 LLM 把自然语言电力系统需求闭环地变成可执行的动态仿真模型，并在执行反馈下自行修正。** 作者把研究问题明确写成：如何构造一个 closed-loop framework，使 LLM 能自主生成、验证并迭代纠正用于电力系统仿真的代码，并把这种持续改善视为 self-evolution 的起点；给出的方案是 dual-LLM-agent framework。[pdf:E04]（PDF 物理页 2，Introduction 末段与贡献列表）

这个问题重要，是因为电力系统动态仿真直接服务于规划、运行、稳定性、保护以及可再生能源接入研究，而当前建模通常要由专家把技术规格、数据表或概念描述手工翻译成 Simulink、PSCAD、PowerFactory 等平台中的模型。论文指出，这种流程慢、易受无意错误影响，而且难以随系统复杂度扩展。[pdf:E02]（PDF 物理页 1，Section I 左栏）若自动化链路可信，它的价值不只在节省建模时间，还在于把“需求解析—模型构造—运行—修正”变成可重复的计算流程，并为后续训练或模型改进产生仿真数据；摘要正是以双 agent、双反馈回路、函数数据库和 IEEE 9-bus MATLAB/Simulink 示例来界定这一愿景。[pdf:E01]（PDF 物理页 1，Abstract）

但必须先限定论文实际证明的范围：它展示的是一个 IEEE 9-bus 单案例，而不是已经证明可普遍替代专业建模人员的通用系统。后者是目标，前者才是本文证据覆盖到的结果。

## § 2 — 前人工作与不足

**相关文献中的已有结论，仅按本文回顾而未作独立核验：** PE-GPT [3] 用领域知识库的 RAG、reasoning agent、metaheuristic algorithms 与仿真工具弥补通用 LLM 的电力电子知识缺口；另一项工作 [4] 用 collaborative multi-agent workflow 做目标导向控制器设计；文献 [5] 研究 tool-augmented LLM 的电网模型生成；文献 [6] 把 GPT-agent 与 deep reinforcement learning 用于带语言约束的实时最优潮流；文献 [7]、[8] 则讨论带知识检索、通信和 error-feedback 的 multi-agent 电力系统任务。[pdf:E03]（PDF 物理页 1，Section I 右栏）这些工作的题名与出处可在本文参考文献 [3]–[8] 中定位。[pdf:E21]（PDF 物理页 5，References [3]–[8]）

作者认为缺口在于：已有框架虽能做模型设计、控制器设计、网络生成、潮流计算或反馈驱动任务，但其测试没有覆盖需要多步推理的 time-domain dynamic simulation；与此同时，通用 LLM 虽会生成通用代码，却不能以足够准确度在特定仿真平台中完成完整电力系统模型。[pdf:E03]（PDF 物理页 1，Section I 右栏至页末）本文因此把问题从“生成一段答案或代码”推进为“生成平台可执行模型，并让运行结果返回 agent 形成闭环”。

不足也很明确：本文没有把上述最相关系统作为实验 baseline，没有报告相同任务下的成功率、误差、token、响应时间或人工修复成本对比。因此，“相较前人更好”在本文中主要是问题设定与架构层面的主张；严格 novelty 和性能优势只能视为候选判断，不能由这篇 PDF 单独闭合。

## § 3 — 重建作者的思考路径

下面是**基于证据的合理推断**，用于重建 idea 如何从既有失败模式长出来，而不是把论文贡献倒过来当作前提。

第一步，手工建模的本质是一个跨表示转换问题：自然语言需求、设备参数和电网数据并不直接对应仿真器的 block、连接关系与参数接口；单纯要求 LLM 一次生成完整模型，会同时压上需求理解、任务排序、领域方程、平台 API 和调试五种负担。[pdf:E02]（PDF 物理页 1，Section I 左栏）

第二步，把大任务拆成“先规划、后执行”可以降低单个 agent 的认知负荷。Agent I 把需求转换成有顺序和依赖关系的子任务序列，Agent II 只负责把当前节点转成代码；论文的 Algorithm 1 也把 `PlanMaker`、`Performer`、`Validator` 和 `UpdateMemory` 分成独立角色。[pdf:E05]（PDF 物理页 2，Algorithm 1）Agent I 与 Agent II 的正文说明进一步表明，前者构造 task logic topology，后者按预定义规范生成可执行代码。[pdf:E06]（PDF 物理页 2，Section II-A–C）

第三步，仿真器本身可以充当比语言自检更具体的反馈来源：把代码放入隔离环境预执行，捕获错误和输出，再把信息交回 Agent II；失败时根据错误重写或重规划，成功时才部署并保存。[pdf:E07]（PDF 物理页 3，Section II-D）这使“LLM 觉得答案正确”变成“代码至少通过了执行链路”。

第四步，平台代码不应完全自由生成。动态方程可以先变成 operator、constant、variable 组成的 AST，再通过固定 API 递归编译为 Simulink block；参数、潮流初始化和可复用函数也各自进入结构化接口与数据库。[pdf:E08]（PDF 物理页 3，Fig. 1、Eq. (1)、Section III-A）[pdf:E09]（PDF 物理页 3，Section III-B、Eq. (2)）[pdf:E10]（PDF 物理页 3，Section III-B.3 与 III-C）

因此，作者可能的完整思路是：**用任务分解控制语言层的不确定性，用 AST 与固定 API 控制平台层的自由度，用执行反馈暴露错误，再把成功代码积累为 memory。**

## § 4 — 核心 Intuition

不要让一个 LLM 一次承担“理解需求、设计模型、写平台代码、判断正确性”全部职责，而是让 Agent I 规划、Agent II 编译，再由可执行环境把错误送回闭环。[pdf:E05]（PDF 物理页 2，Algorithm 1）方程不直接作为任意文本代码落地，而先进入 AST，再经固定 MATLAB/Simulink API 递归生成 block 与连接，从而把生成空间压缩为受控的结构化操作。[pdf:E08]（PDF 物理页 3，Fig. 1 与 Section III-A）成功函数进入数据库后，后续任务优先复用而不是重新调用 LLM，这构成作者所谓 self-evolution 的工程起点。[pdf:E10]（PDF 物理页 3，Section III-C）

## § 5 — 具体方法与完整 Pipeline

以论文给出的输入“Please generate an IEEE 9-Buses system with power flow calculated.”为例，完整 pipeline 可以重建为以下七步。[pdf:E13]（PDF 物理页 4，Section IV-B）

1. **准备输入与约束。** Algorithm 1 的输入包括自然语言需求 `U`、high-priority prompt `A`、软件 API 文档 `D`、验证规则 `R`、memory `M` 和最大修正次数 `iter_max`；输出是最终仿真代码 `C_final`。[pdf:E05]（PDF 物理页 2，Algorithm 1 Input/Output）论文实际 prompt 要求 Agent I 只给概念性方案且控制长度，Agent II 只输出代码，并限定只能使用 `BasicPerformer` 类提供的方法。[pdf:E14]（PDF 物理页 4，Listing 1、Listing 2）

2. **Agent I 生成计划。** `PlanMaker(U,A,C_current)` 把需求拆成有序子任务 `P=(p1,p2,…,pN)`，显式表达执行顺序与依赖。对 9-bus 任务，一个合理计划会依次包含读取网架与参数、潮流初始化、创建设备方程、连接网络、设置仿真与返回模型；这里的具体拆分是基于论文机制的重建，论文未逐项展示 Agent I 的实际输出。[pdf:E06]（PDF 物理页 2，Section II-B）

3. **Agent II 执行当前子任务。** `Performer(p_i,D,M,C_current)` 先检索 memory 中已有函数，再按 API 文档生成草稿代码。Agent II 的高优先级 prompt 把输出约束为代码，并要求只调用 `BasicPerformer` 暴露的方法，以减少任意 API 使用。[pdf:E05]（PDF 物理页 2，Algorithm 1 第 5–7 行）[pdf:E14]（PDF 物理页 4，Listing 2）

4. **Validator 预执行并反馈。** 草稿代码在隔离环境中执行，系统捕获执行状态和输出；满足规则则追加到 `C_current`，否则把详细 error feedback 交回 planner/performer，修正计数加一并重新规划。[pdf:E07]（PDF 物理页 3，Section II-D）这一步验证的是执行与预设要求是否通过，论文没有公开 `R` 的完整规则集。

5. **把方程编译为 Simulink 结构。** 作者先把设备动态写成状态方程和输出映射，再把运算分解为 ADD、SUB、MUL 等 operator node，以及 constant、parameter、input、output、state 等节点；递归遍历 AST 后，通过 `add_block`、`set_param` 等函数生成 equation layer，随后连接成 structure layer，再把各 apparatus 连接成系统。[pdf:E08]（PDF 物理页 3，Fig. 1、Eq. (1)、Section III-A）[pdf:E09]（PDF 物理页 3，Section III-B.1）9-bus 示例中的 `d_T_m` 方程最终确实被展开成一串 Simulink 运算块和连接。[pdf:E16]（PDF 物理页 5，Fig. 3）

6. **生成参数并完成潮流初始化。** 参数被分成 system、component、simulation 三层；潮流模块接收 Excel/JSON 形式的标准 IEEE 数据，使动态仿真从可行平衡点启动。[pdf:E09]（PDF 物理页 3，Eq. (2) 与 Section III-B.2）[pdf:E10]（PDF 物理页 3，Section III-B.3）论文给出 9 个母线的电压幅值和相角分布作为初始化结果。[pdf:E15]（PDF 物理页 5，Fig. 2）

7. **返回模型、参数与运行结果，并更新 memory。** 成功代码按函数名、说明、输入输出和数据结构存入数据库，供未来任务检索复用。[pdf:E10]（PDF 物理页 3，Section III-C）在案例中，系统返回模型及参数表，并对 SG1 在约 1 s 时施加持续 0.5 s 的端口电压扰动，得到三台同步机的转子速度与角度曲线。[pdf:E13]（PDF 物理页 4，Section IV-B）[pdf:E17]（PDF 物理页 5，Fig. 4）

实现平台方面，论文使用 MATLAB/Simulink；在线 agent 为 DeepSeek-V3.1-Terminus API，本地 agent 为 DeepSeek-r1:14b，硬件为 Intel Core i9-14900HX、96 GB RAM 和 Nvidia RTX 4060 8 GB Laptop GPU。[pdf:E11]（PDF 物理页 4，Section IV 开头）

**未报告边界：** 论文没有给出开关/离散事件语义、DAE index 处理、solver 类型与步长、多速率时间推进、数值精度、代数环求解、计算依赖调度、并行实现、FPGA 映射、通信接口时序或实时步长。它只说明 simulation 参数类别中可包含 solver settings 和 duration，并在结论把并行模型生成列为 future work。[pdf:E09]（PDF 物理页 3，Eq. (2) 后解释）[pdf:E20]（PDF 物理页 5，Conclusion）因此不能把它读成已经完成的 EMT 实时仿真或 FPGA 自动部署方案。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文**没有新的理论推导、收敛证明或误差界**；数学部分主要承担三种工程记号：设备方程表示、参数分类以及系统开销统计。

首先，作者把电力系统元件动态写为

\[
\dot{x}=f(x,u),\qquad y=g(x,u),
\]

其中 `x` 是状态，`u` 是输入，`y` 是输出，`f`、`g` 由基本运算组成；这些运算随后被拆成 AST node 并递归生成平台模型。[pdf:E08]（PDF 物理页 3，Eq. (1)、Fig. 1、Section III-A）直觉上，AST 把“方程是什么意思”转成“先算哪个子表达式、再把结果送到哪里”。但论文称其为 nonlinear differential-algebraic equations，而 Eq. (1) 没有显式写出一般 DAE 常见的代数残差约束，例如 `0=h(x,z,u)`；所以这条公式足以表达状态方程与输出映射，却不足以单独证明框架覆盖高 index DAE、代数环或离散事件。这是基于公式范围的推断。

其次，参数文件按

\[
\mathcal{P}=\{\mathcal{P}_{\mathrm{system}},\mathcal{P}_{\mathrm{component}},\mathcal{P}_{\mathrm{simulation}}\}
\]

组织：system 层放 base MVA、frequency 等系统量，component 层放设备参数，simulation 层放 solver settings 与仿真时长。[pdf:E09]（PDF 物理页 3，Eq. (2)）这不是物理推导，而是让 agent 和 API 对参数作用域形成稳定契约。

最后，作者定义三项平均指标：

\[
\bar{T}=\frac{1}{N}\sum_{i=1}^{N}\left(T_{\mathrm{input},i}+T_{\mathrm{output},i}\right),
\]

\[
\bar{R}=\frac{1}{N}\sum_{i=1}^{N}K_i,
\]

\[
\bar{t}=\frac{1}{N}\sum_{i=1}^{N}\left(t_{\mathrm{end},i}-t_{\mathrm{start},i}\right).
\]

它们分别表示每任务平均 token、平均修正次数和从任务开始到最终验证通过的平均响应时间。[pdf:E12]（PDF 物理页 4，Eq. (3)–(5)、Section IV-A）这些式子只能量化成本和流程迭代，不能评价生成模型的物理误差；论文也没有给出 AST 转换保持数学等价性的形式化证明。因此，本文的“核心数学”实际上是结构化编译接口，而非新数值算法。

## § 7 — 实验设计与结论

**问题 1：系统能否从一句需求生成可运行的 9-bus 仿真模型？ → 实验：** 在 MATLAB/Simulink 上用在线与本地 DeepSeek agent，输入生成 IEEE 9-bus 且先算潮流的需求，通过固定 API 生成方程、结构和参数。[pdf:E11]（PDF 物理页 4，实验平台）[pdf:E13]（PDF 物理页 4，Section IV-B）**答案：** 论文报告任务成功，给出了母线电压/相角图以及 `d_T_m` 的 Simulink AST block 结构。[pdf:E15]（PDF 物理页 5，Fig. 2）[pdf:E16]（PDF 物理页 5，Fig. 3）这证明了一个案例的端到端可执行性，但没有用标准潮流程序或手工模型给出数值误差。

**问题 2：生成模型是否产生合理的时域动态？ → 实验：** 在 SG1 端口约 1 s 时施加持续 0.5 s 的电压扰动，观察三台同步机转子速度与角度。[pdf:E13]（PDF 物理页 4，Section IV-B）**答案：** Fig. 4 显示扰动后各机出现幅度不同的速度跌落、过冲与角度暂态，并呈现恢复趋势；作者据此认为模型正确且可用。[pdf:E17]（PDF 物理页 5，Fig. 4）更谨慎的结论只能是“曲线具有定性上合理的暂态形态”，因为没有 reference trajectory、误差指标、稳定性判据或重复工况。

**问题 3：流程成本和自修正开销是多少？ → 实验：** 用 Eq. (3)–(5) 统计 token、修正次数和总响应时间。[pdf:E12]（PDF 物理页 4，Section IV-A）**答案：** Table I 对一个 single task 报告 2,169 tokens、1 次 rectification、240 s、Task Outcome 为 Success。[pdf:E18]（PDF 物理页 5，Table I）论文正文把这些量称为平均值，但表题明确是单任务，且没有报告 `N`、方差、重复次数或失败样本，因而不能据此估计稳定成功率或规模扩展规律。

**问题 4：memory 是否带来持续改进，双 agent 是否优于单 agent？ → 实验：** 未设计。作者在结论开头把单案例概括为框架能够可靠生成 executable code，[pdf:E19]（PDF 物理页 4，Conclusion 开头）随后把“规划/执行分解与 self-correction 可支持复杂精密任务”列为收益，并说成功函数可以继续加入数据库，把可调参数的 self-evolving LLM 与并行生成留作未来方向。[pdf:E22]（PDF 物理页 5，Conclusion 第 1 点）[pdf:E20]（PDF 物理页 5，Conclusion 第 2–3 点与 future work）但这些外推没有对应实验，因此 memory 的命中率、token 节省、跨任务迁移、遗忘或错误复用都没有被实证。

**不得外推的范围：** 当前证据只覆盖一个 9-bus、一个自然语言任务、一个扰动、一个平台和一组 LLM/硬件配置；没有 baseline、ablation、统计重复、不同拓扑、不同设备类型、故障/开关事件、实时约束或 FPGA 结果。

## § 8 — Take-aways

**5 句话：**

1. 论文把自然语言到电力系统动态仿真的过程拆成 planner、performer、validator 和 memory 四个可执行环节，而不是让单个 LLM 一次写完整模型。[pdf:E05]（PDF 物理页 2，Algorithm 1）
2. 真正降低生成自由度的是 AST 加固定 Simulink API：LLM 产出受控节点与调用，递归逻辑负责搭建 block 和连接。[pdf:E08]（PDF 物理页 3，Fig. 1 与 Eq. (1)）[pdf:E09]（PDF 物理页 3，Section III-B）
3. 9-bus 案例展示了潮流初始化、方程 block 生成和扰动后的时域曲线，说明端到端链路在一个案例上能跑通。[pdf:E15]（PDF 物理页 5，Fig. 2）[pdf:E16]（PDF 物理页 5，Fig. 3）[pdf:E17]（PDF 物理页 5，Fig. 4）
4. 报告结果是单任务 2,169 tokens、1 次修正和 240 s 成功，尚不能证明平均性能、泛化或相对优势。[pdf:E18]（PDF 物理页 5，Table I）
5. 论文最有价值的是“LLM 作为受约束的模型编译编排器”这一系统设计，而不是已被充分验证的自动建模正确性。

**3 句话：** 双 agent 分工负责需求规划与平台代码生成，执行环境负责把错误送回闭环。[pdf:E06]（PDF 物理页 2，Section II）AST、参数层级和函数 memory 把一次性代码生成改造成可复用的结构化模型构造流程。[pdf:E08]（PDF 物理页 3，Section III-A）但实验只证明一个 9-bus 任务成功运行，没有证明生成模型与可信参考在物理上等价。[pdf:E18]（PDF 物理页 5，Table I）

**1 句话：** 这是一个有吸引力的自动化模型生成原型，但当前证据更接近“能编译并运行”，还不是“已证明生成正确且可泛化的电力系统动态模型”。

## § 9 — 最脆弱的假设

**最脆弱的假设是：代码能执行、输出曲线看起来合理，就足以代表生成模型在物理上正确。** 如果这个假设不成立，论文的核心贡献会从“自动生成动态仿真模型”退化为“自动生成可运行的 Simulink 程序”。

论文的 validator 主要依据预设规则、代码执行状态和输出结果完成自修正；正文没有说明它会比较参考模型、检查单位与符号、验证功率平衡、检查参数来源或量化动态轨迹误差。[pdf:E07]（PDF 物理页 3，Section II-D）作者提供的正面证据是：9-bus 潮流图、一个方程的 AST block、一次电压扰动下的三机曲线，以及 Table I 的 Success。[pdf:E15]（PDF 物理页 5，Fig. 2）[pdf:E16]（PDF 物理页 5，Fig. 3）[pdf:E17]（PDF 物理页 5，Fig. 4）[pdf:E18]（PDF 物理页 5，Table I）

这些证据能排除“完全不能运行”，却排除不了更危险的错误：参数单位错一个数量级、反馈符号反了、初值只在单一工况巧合匹配、某个状态未连接、事件顺序错误，或者模型在展示的 0.5 s 扰动下看似正常但在另一工况迅速偏离。论文缺少的关键证据，是与手工可信模型或独立求解器的定量等价测试，以及跨工况、跨设备、跨随机生成的重复结果。

## § 10 — 最小复现实验

**一周内最值得复现的是：执行反馈和双 agent 分工，是否真的提高“物理正确的模型”生成成功率，而不只是提高代码可运行率。**

数据与参考物采用同一个 IEEE 9-bus 系统，并先手工建立一个可信 MATLAB/Simulink reference model；生成任务沿用论文的自然语言输入和 SG1 在约 1 s 时持续 0.5 s 的电压扰动。[pdf:E13]（PDF 物理页 4，Section IV-B）实现只保留最小 API 子集：创建常量、加减乘除 block，设置参数，连接 block，读取 Excel/JSON 潮流数据，运行仿真和返回错误。AST 只覆盖论文 Fig. 1 所示 operator/constant/variable 类型。[pdf:E08]（PDF 物理页 3，Fig. 1）

比较两种条件：A 是单 agent 一次性生成；B 是论文的 PlanMaker + Performer + sandbox feedback + re-plan。对同一任务做 10 次独立生成，并用不同表述重写需求，避免把一次固定 prompt 的偶然成功当成系统能力。每次测量四组量：代码是否可执行；9 个母线潮流与 reference 的最大误差；三台同步机转子速度和角度相对 reference 的 normalized RMSE；以及论文定义的 token、rectification、response time。[pdf:E12]（PDF 物理页 4，Eq. (3)–(5)）

预先规定判据，例如：B 至少 9/10 次可执行，且全部关键轨迹误差低于 1%，同时物理正确率显著高于 A，才支持“反馈闭环提高自动模型生成可靠性”。若 B 只是更常运行成功，但与 reference 的动态误差没有改善，或者一改变措辞就失败，则反驳核心 claim。这里的 9/10 和 1% 是复现实验应预注册的候选阈值，不是论文报告数字。

## § 11 — 最强反例设计

最强攻击不是让模型遇到语法错误，而是构造一个**错误模型也能稳定运行、也能给出貌似合理曲线**的任务。具体做法是在同一 9-bus 系统中，把 SG1 的一部分动态改成带饱和、滞回和离散 mode transition 的混合模型，并加入一个会产生代数约束的控制环；要求系统从自然语言和方程说明生成模型，再在电压跌落、线路切除和负荷阶跃三类未见工况上与手工 reference 对比。

这个反例直接打到方法表示层：论文公开的 AST 只有 operator、constant 和 variable，API 说明集中在 equation block、structure、apparatus、参数文件与潮流初始化，没有给出 event node、mode state、zero-crossing、代数环或 DAE index 的语义。[pdf:E08]（PDF 物理页 3，Fig. 1 与 Eq. (1)）[pdf:E09]（PDF 物理页 3，Section III-B）因此 agent 完全可能生成一个语法合法、仿真可结束、单次波形平滑，却在切换时刻、限幅恢复或隐式约束上物理错误的模型。

判定标准应同时看 event time、mode sequence、关键状态轨迹和守恒/约束残差，而不是只看 `Task Outcome = Success`。若论文流程在 sandbox 中判为成功，但生成模型在任一 held-out 工况中选错 mode 或产生大幅轨迹偏差，这将证明“执行反馈”不能替代“物理语义验证”，也会推翻从单一 9-bus 曲线外推到复杂动态模型的依据。[pdf:E17]（PDF 物理页 5，Fig. 4）[pdf:E18]（PDF 物理页 5，Table I）

## § 12 — Follow-up Research Bet

**候选判断，不声称 novelty：主动激励驱动的可执行混合 DAE 结构发现。** 协议限定只使用本文材料，未对相关全文做外部检索，因此以下是研究押注而不是新颖性认证。

新的研究问题是：**当设备方程或控制拓扑未知时，agent 能否一边选择最有辨识力的扰动，一边发现连续方程、代数约束和离散 mode 组成的模型结构，并把它直接编译成可执行仿真图？** 这首次把本文的能力从“翻译已知需求与方程”推进到“通过实验主动发现未知动态机制”，目标对象不再是代码是否成功，而是结构是否被恢复、held-out 工况是否可预测。

核心机制是一条因果链。第一，把本文的 operator/constant/variable AST 扩展成 typed hybrid DAE graph，显式加入 continuous state、algebraic constraint、event、mode 和 physical port；本文已经证明 AST 可以递归落到 Simulink block，并用 system/component/simulation 三层参数组织配置。[pdf:E08]（PDF 物理页 3，Fig. 1、Eq. (1)）[pdf:E09]（PDF 物理页 3，Eq. (2) 与 Section III-B）第二，planner 不再只拆代码任务，而是同时提出候选 graph 与下一次主动扰动；第三，仿真或实测轨迹用来淘汰不能解释观测的结构，并拟合保留结构的参数；第四，胜出的 graph 继续通过固定 API 编译为可执行模型，并把可复用子结构写入 memory。[pdf:E10]（PDF 物理页 3，Section III-C）

这项押注至少改变四个基本设计变量：问题定义从“已知结构的代码生成”改为“未知结构的机制发现”；状态表示从普通算术 AST 改为 hybrid DAE graph；数据生成从一次固定电压扰动改为 agent 选择的主动干预；评价对象从 sandbox success 改为结构恢复与跨扰动预测。本文的实验只用了 SG1 在约 1 s 开始、持续 0.5 s 的单一电压扰动，并以三机速度和角度曲线作为结果，这恰好说明动态轨迹已经进入闭环，却还没有被用来选择下一次实验或区分竞争模型。[pdf:E13]（PDF 物理页 4，Section IV-B）[pdf:E17]（PDF 物理页 5，Fig. 4）作者又把成功函数积累和 self-evolving LLM 作为未来愿景，为“从存代码升级为发现模型结构”提供了论文特异的出发点。[pdf:E20]（PDF 物理页 5，Conclusion）

按本文自己的 related-work 描述，最近工作主要围绕 RAG、控制器设计、网络/潮流任务、tool-augmented code generation 或反馈式 multi-agent 执行；本文本身也仍以生成已定义仿真模型为对象。[pdf:E03]（PDF 物理页 1，Section I 右栏）这个押注与它们的实质区别在于：problem 是未知机制发现，mechanism 是主动实验选择与结构竞争，representation 是 typed hybrid DAE graph，experimental object 是可区分候选物理机制的多次干预，而不是一次任务的代码输出。由于没有独立检索，这个差异只能视为相对本文所述工作成立的候选判断。

最大收益是把自动建模从工程转译工具变成可执行 scientific discovery 系统，能够为缺少完整文档的新型电力电子设备或聚合模型自动提出、试验并落地动态结构。最大科学风险是 structural identifiability：不同 graph 可能在有限扰动下产生几乎相同轨迹；其次是组合搜索规模和 simulator-to-real gap，使 agent 可能把参数拟合误认为结构发现。

最小证伪实验是在 9-bus 中隐藏 SG1 的真实模型，从两个稳态潮流相同、但在不同频段扰动下动态不同的候选结构中随机选一个作为 ground truth。给 agent 相同数量的仿真预算，比较三组：typed graph + 主动扰动、typed graph + 随机扰动、固定结构只拟合参数；测试 exact structure recovery 和未见扰动下的轨迹误差。只有第一组在数据量相同的条件下更常恢复真实结构，并显著降低 held-out error，才能说明收益来自“主动结构发现”而不是简单增加数据或提高参数拟合自由度；否则应放弃这一机制。

**Wild-card alternative：** 把 AST node 直接映射为可部分重配置 FPGA dataflow fabric，使 agent 的输出从 Simulink 代码变成可执行硬件 netlist，并把研究对象改为拓扑变化下的编译延迟、资源占用和实时吞吐；这一方向改变的是硬件映射与执行架构，而不是主动结构发现机制。[pdf:E16]（PDF 物理页 5，Fig. 3）
