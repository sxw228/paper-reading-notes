# VeriOpt: PPA-Aware High-Quality Verilog Generation via Multi-Role LLMs

- **作者**：Kimia Tasnia, Alexander Garcia, Tasnuva Farheen, Sazadur Rahman
- **出处**：2025 IEEE/ACM International Conference On Computer Aided Design (ICCAD)（源 PDF 为 arXiv:2507.14776v1 预印本版）
- **年份**：2025
- **DOI**：10.1109/ICCAD66269.2025.11240771
- **Zotero key**：2ZWWBPPS

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

大语言模型（LLM）辅助寄存器传输级（RTL）Verilog 生成正面临从“能跑通仿真测试台（Testbench）”到“满足工业流片级功耗-性能-面积（PPA）指标”的跨越难题（PDF 物理页 1，Abstract 与 Section I `[pdf:E01]`）。本文围绕两个核心问题展开：**RQ1**——如何在不依赖昂贵领域预训练或监督微调（SFT）的前提下，生成透明、可读、易调试且功能正确的 Verilog 代码；**RQ2**——如何使大模型根据设计约束权衡并优化 PPA 指标，摆脱“功能正确但微架构次优（correct-but-suboptimal）”的局限（PDF 物理页 1，Section I `[pdf:E01]`）。

该问题长期受阻于两重断层：一是**训练语料极端稀缺**，GitHub 代码库中硬件描述语言占比远低于主流软件语言，削弱了基座模型对并发硬件原语、阻塞/非阻塞赋值与状态机边界的原生推理力（PDF 物理页 1–2，Section I、II-C 与 Fig. 2(a) `[pdf:E01]` `[pdf:E04]`）；二是**现有闭环仅锚定功能仿真**（PDF 物理页 1，Fig. 1 `[pdf:E02]`），忽略了空闲逻辑未门控、次优编码与深串行组合链等微架构缺陷。在片上系统（SoC）与 ASIC/FPGA 流程中，流水线切分等 RT 级架构决策无法由后续门级逻辑综合自动补救；若流片后才暴露漏电功耗失控或目标主频下时序违例，将引发百万美元级掩膜重制（Re-spin）或迫使产品降频延期（PDF 物理页 1–3，Section I、II-C 与 III-B2 `[pdf:E01]` `[pdf:E04]` `[pdf:E09]`）。

## § 2 — 前人工作与不足

Section II-A 与 Table I（PDF 物理页 2 `[pdf:E03]`）对比了 9 项代表性 LLM-for-RTL 工作，指出它们全部仅关注功能正确性（`Func. = ✓`），无一内建 PPA 优化（`PPA = ×`）：

1. **HDL 数据集监督微调（SFT）路线**：包括 VeriGen（Thakur et al.）、RTLCoder（Liu et al.）、BetterV（Pei et al.）与 RTLSquad（Wang et al.）（PDF 物理页 2，Table I 与 Section II-A1 `[pdf:E03]`）。微调虽提升了基础语法与功能通过率，但训练目标仅最小化词元交叉熵，缺乏物理综合代价约束；同时开源界极度缺乏带商用综合 PPA 标注的高质量多样化 RTL 语料，且端到端黑盒生成隐藏了从规范到硬件原语的推理过程，出错后极难定位根因（PDF 物理页 2–3，Section II-A1、II-C 与 III-A1 `[pdf:E03]` `[pdf:E04]` `[pdf:E05]`；物理页 8，Section V-C `[pdf:E16]`）。
2. **结构化与自然语言提示工程（PMT）路线**：包括 ChipGPT（Chang et al.）、RTLLM Self-Planning（Lu et al.）与模块化分层框架 HiVeGen（Tang et al.）（PDF 物理页 2，Table I 与 Section II-A2 `[pdf:E03]`）。此类方法免去了重训成本，但存在双重脱节：功能侧缺少独立的“规划落实核查员”与报错驱动的注释追踪闭环，长代码生成易偏离初始步骤；质量侧完全与综合器隔离，无法感知面积、功耗或关键路径裕量瓶颈（PDF 物理页 2–4，Section II-A2 与 III-A2 `[pdf:E03]` `[pdf:E06]` `[pdf:E07]`）。
3. **搜索引导与混合增强路线**：包括 DeLorenzo 等人的蒙特卡洛树搜索（MCTS）与 Zhang 等人的 SFT+ICL 混合框架 MG-Verilog，此外 Section I 还提及语法修复工具 RTLFixer、波形追踪代理 VerilogCoder 及重写框架 RTLRewriter（PDF 物理页 1–2，Section I、II-A3 与 Table I `[pdf:E01]` `[pdf:E03]`）。搜索方法通常仅把 PPA 当作生成后的事后筛选准则而非生成期微架构先验，且多轮树搜索显著推高了推理与外部验证开销（PDF 物理页 2，Section II-A3 `[pdf:E03]`）。

## § 3 — 重建作者的思考路径

面对“零微调条件下兼顾高功能通过率与 PPA 优化”的目标，首道硬约束是开源 HDL 语料占比极低且缺少成对的“RTL—综合报告”训练数据（PDF 物理页 2，Section II-C `[pdf:E04]`；物理页 8，Section V-C `[pdf:E16]`），解法自然聚焦于推理期提示架构与上下文学习（ICL）。

针对功能正确性（RQ1），单轮黑盒提示常在“自然语言规范 → 寄存器/状态机/边沿时序”的隐式映射中漏掉复位初值或边界保持拍数（PDF 物理页 3–4，Section III-A1 与 Fig. 4 `[pdf:E05]` `[pdf:E07]`）。参照人类芯片前端团队的分工——架构师拆解硬件原语步骤、RTL 工程师按章编码并留注释、审查员逐条勾稽设计步骤、验证工程师对照测试台报错日志开具修复单——将单一 LLM 拆分为 Planner、Programmer、Reviewer、Evaluator 四角色并强制行内 `[STEP k]` / `Fix k` 注释留痕，即可把黑盒采样转化为可逐步审计的白盒纠错环（PDF 物理页 3–4，Section III-A2 与 Fig. 4 `[pdf:E05]` `[pdf:E06]` `[pdf:E07]`）。

针对 PPA 优化（RQ2），作者梳理出五项障碍 `C1`–`C5`：纯文本模型无法单凭代码量化 PPA（`C1`）、难以脱离结构判断优化适用性（`C2`）、缺乏布局布线与单元库物理细节（`C3`）、需平衡多目标冲突（`C4`）并把高层约束映射为合法微架构变换（`C5`）（PDF 物理页 5，Section III-B1 `[pdf:E08]`）。若直接向提示词倾倒门级静态时序图（STA Graph）与工艺库 `.lib` 查找表，底层数据噪声反而令语言模型失效（`S1`）。但大模型擅长阅读两类高层信息：一是商用综合器对基线代码提炼的**标量指标摘要表**（`S3`），二是 VLSI 教材中的**一阶功耗/延迟解析方程与按目标归类的 RT 级变换范式**（`S1`–`S2`）（PDF 物理页 5，Section III-B2 与 Fig. 5 `[pdf:E09]`）。由此水到渠成地形成“先以四角色仿真闭环锁死功能基线，再注入基线综合报告与 VLSI 知识做上下文重构”的两阶段流水线（PDF 物理页 3，Fig. 3 `[pdf:E05]`）。

## § 4 — 核心 Intuition

传统大模型写 Verilog 之所以难以兼顾正确性与硬件质量，是因为它在既无中间原语审计、又无后端物理反馈的纯文本空间盲目采样，极易写出时序错拍或堆满串行进位链与无效翻转的低效代码（PDF 物理页 1–3，Fig. 1、Fig. 2 与 Section III-A1 `[pdf:E02]` `[pdf:E04]` `[pdf:E05]`）。VeriOpt 的核心支点是将任务拆成锚定不同外部真值的两步：先用强制代码注释留痕的“规划—编码—审查—仿真评估”四角色闭环拿到功能过关的基线 RTL（PDF 物理页 3–4，Fig. 3 与 Fig. 4 `[pdf:E05]` `[pdf:E07]`）。随后，它绕开大模型读不懂的底层工艺库时序图，改用基线代码的商用综合标量摘要搭配教科书级一阶功耗/延迟公式作为物理翻译器，让模型看清瓶颈究竟在逻辑级数还是开关翻转率，进而定向套用超前进位、操作数隔离或资源共享等 RT 级变换（PDF 物理页 5–6，Fig. 5 与 Fig. 6 `[pdf:E09]` `[pdf:E10]`）。

## § 5 — 具体方法与完整 Pipeline

### 聚焦问题正面拆解（Focus）

1. **四角色如何协同处理功能正确性与 PPA 收敛的冲突**：
   VeriOpt **并未在四角色内部同步博弈功能与 PPA，而是采用“两阶段串行解耦（先保功能闭环、后做开环 PPA 重构）”来隔离冲突**（PDF 物理页 3，Fig. 3 `[pdf:E05]`；物理页 6，Fig. 6(a) `[pdf:E10]`）。第一阶段（Fig. 3 绿色框）由 Planner、Programmer、Reviewer、Evaluator 围绕 Icarus Verilog 测试台迭代，唯一目标是产出功能正确的基线 RTL，全程不引入面积或时序约束；仅当 `Func Eval? = Yes` 后，才单向移交第二阶段（Fig. 3 紫色框）开展 PPA 上下文重构（PDF 物理页 3–4，Section III-A2 与 Fig. 3 `[pdf:E05]` `[pdf:E06]`）。尤需注意，Fig. 3 中紫色框输出 `PPA-optimized HDL Code` 后**无自动回接测试台或 Reviewer 的闭环箭头**，且 Section V-C 明确承认模型无法实时调用综合工具，优化验证依赖外部人工反馈环（PDF 物理页 3，Fig. 3 `[pdf:E05]`；物理页 8，Section V-C `[pdf:E16]`）。
2. **商用综合报告与时序反馈如何结构化回流**：
   摘要虽提及“multi-modal feedback (e.g., synthesis reports, timing diagrams)”（PDF 物理页 1 `[pdf:E01]`），但正文流水线并未采用视觉模型读取波形图，而是将第一阶段基线代码送入 **Synopsys Design Compiler** 后，抽取**三大类共 10 项标量指标**以结构化文本注入第二阶段提示词（PDF 物理页 5–6，Section III-B2 `S3`、Fig. 6(a) 与 Section IV-A3 `[pdf:E09]` `[pdf:E10]` `[pdf:E11]`）：功耗类（动态功耗、漏电功耗、单元内部功耗、线网翻转功耗）、面积类（单元面积、设计总面积、组合面积、时序面积）与时序类（关键路径长度、关键路径裕量 Slack、总负裕量 TNS、逻辑级数）。为弥补 LLM 无法解析标准单元库与门级 STA 图的缺陷（`S1`），上述标量报告与 CMOS VLSI 解析估算方程及 RT 级代码模板并列输入，引导模型将数值瓶颈映射至代码结构（PDF 物理页 5，Fig. 5 `[pdf:E09]`）。
3. **角色消融实验的对照方法**：
   全文实验（Section IV）**未设置同基座（GPT-4o）下逐一剔除 Planner / Reviewer / Evaluator 的单变量角色消融表**，亦未报告裸 `GPT-4o` 单次提示基线（PDF 物理页 6–8，Table II 与 Table III `[pdf:E11]` `[pdf:E12]` `[pdf:E14]`）。其实际对照分两层：功能评测（Table II）采用**跨方法阶梯对照**，将四角色 `VeriOpt`（`GPT-4o`）对比单轮模型（`GPT-3.5`/`GPT-4`/`StarCoder`）、SFT 模型（`Thakur et al.`/`RTLCoder`）及仅含“规划+生成”两步而无 Reviewer/Evaluator 闭环的 `RTLLM Self-Planning`（`GPT-3.5`/`GPT-4`）`[pdf:E12]`；PPA 评测（Table III）采用**阶段间前后自身对照**，在 25 个功能通过模块上将“仅跑第一阶段四角色、无 PPA 上下文”的基线代码与叠加第二阶段后的优化代码逐项对比 `[pdf:E11]` `[pdf:E14]`。

### 阶段一：四角色功能生成闭环（`signal_generator` 实例）

以 Fig. 4 的 5 位三角波发生器 `signal_generator`（输入 `clk`、低有效复位 `rst_n`，输出 `0..31` 往复递增递减波形 `wave`）为例，四角色职责如下（PDF 物理页 3–4，Section III-A2 与 Fig. 4 `[pdf:E06]` `[pdf:E07]`）：
- **LLM Planner**：将文本规范与端口定义拆解为底层原语步骤——`[Step 1]` 声明 `reg [4:0] wave` 与方向位 `reg dir_up`；`[Step 2]` `rst_n == 0` 时置 `wave <= 0`、`dir_up <= 1`；`[Step 3]` 随 `posedge clk` 按 `dir_up` 增至 `31` 或减至 `0` 时翻转方向；`[Step 4]` 直接由寄存器输出 `wave`。
- **LLM Programmer**：严格按规划编码并在源码内标注 `// [STEP 1..4]` 行内注释，确保实现流对人类与下游角色透明。
- **LLM Reviewer**：对照 Planner 清单逐条核查代码实现，生成带 `✅` 标记的核验报告；若有漏步则退回 Programmer 补全。
- **仿真反馈与 LLM Evaluator**：Icarus Verilog 运行 `tb_signal_generator`（`repeat (100)` 逐拍比对 `wave !== reference[i]`），首轮在 `20 ns`（输出 `1`、期望 `0`）至 `1010 ns`（输出 `24`、期望 `28`）报错。Evaluator 结合报错日志与测试台源码定位三项根因：`Fix 1` 复位后跳过初始 `0`；`Fix 2` 与 `Fix 3` 在峰值 `31` 和谷值 `0` 未额外保持一拍完整周期便提前转向。Programmer 写入带 `// Fix 1..3` 注释的补丁，经 Reviewer 复核勾选后在第二轮仿真通过 `[pdf:E07]`。

### 阶段二：PPA 上下文学习重构（`adder_16bit` 实例）

针对挑战 `C1`–`C5`，策略 `S1`–`S4` 从 VLSI 教材、`openMSP430` 开源核、Intel HLS 与 AMD Vivado UG901 综合指南及论文中提炼自然语言估算方程与 15 类 RT 级变换（功耗类：时钟门控、电源门控、操作数隔离、寄存器更新抑制、条件累加；性能类：流水线、重定时、循环展开、逻辑努力、数据前递旁路、路径重构；面积类：资源共享、FSM 编码、逻辑合并、寄存器优化、工艺映射）（PDF 物理页 5，Fig. 5 与 Section III-B2 `[pdf:E09]`）。在 Fig. 6 的 `full_adder_16bit` 算例中，阶段一生成了 16 位 `generate` 循环串行行波进位链（逻辑级数达 32 级）；阶段二结合其综合报告诊断出长进位链延迟与全位宽同时翻转缺陷，分别生成三类重构代码：两级超前进位加法器（`cla_4bit` + `cla_16bit`，逻辑级数降至 12 级）提速、`enable` 三元掩码操作数隔离降功耗，以及单行行为级 `assign {cout, sum} = a + b + cin;` 省面积（PDF 物理页 6，Section III-B3 与 Fig. 6 `[pdf:E10]`）。

## § 6 — 核心数学推导（无形式化数学则跳过）

正文未建立形式化优化目标或收敛性定理，但在 **Fig. 5（PDF 物理页 5 `[pdf:E09]`）** 嵌入了 6 条源自 CMOS VLSI 理论（Weste & Harris）的一阶解析方程，作为替代门级 STA 与功耗查找表的语言级物理因果模型：

1. **CMOS 功耗分解模型**（PDF 物理页 5，Fig. 5 左下 `[pdf:E09]`）：
   $$P_{\text{total}} = P_{\text{dynamic}} + P_{\text{static}}, \quad P_{\text{dynamic}} = \alpha C_L V_{DD}^2 f, \quad P_{\text{static}} = I_{\text{static}} V_{DD}$$
   其中 $\alpha$ 为节点开关活动因子，$C_L$ 为等效负载电容，$V_{DD}$ 为供电电压，$f$ 为时钟频率，$I_{\text{static}}$ 为静态漏电流。因 RTL 阶段 $V_{DD}$ 与 $f$ 固定，该式明确指示模型：降动态功耗须靠时钟门控、操作数隔离或更新抑制压低空闲态 $\alpha$；降漏电与面积则须靠资源共享、逻辑合并或电源门控削减冗余单元电容 $C_L$ 与漏电支路 $I_{\text{static}}$ `[pdf:E09]`。
2. **Elmore 延迟与逻辑努力（Logical Effort）模型**（PDF 物理页 5，Fig. 5 右下 `[pdf:E09]`）：
   $$t_{pd} = \sum R_{i\text{-to-source}} C_i, \quad d = f + p, \quad f = g h$$
   其中 Elmore 延迟 $t_{pd}$ 累加各节点电容 $C_i$ 与到源端共享路径电阻 $R_{i\text{-to-source}}$ 之积；单级门归一化延迟 $d$ 等于努力延迟 $f = g h$（逻辑努力系数 $g$ 乘电气扇出比 $h = C_{\text{out}}/C_{\text{in}}$）加本征寄生延迟 $p$。该组关系无需读取工艺库非线性延迟表，即可向模型解释为何 32 级行波进位串联链与高扇出节点会导致延迟激增，支撑超前进位扁平化、扇出缓冲与流水线切分策略 `[pdf:E09]` `[pdf:E10]`。
3. **严谨性支撑结构与形式化缺口**：方法严谨性依赖外部工具硬检（阶段一 Icarus Verilog 测试台与阶段二 Synopsys Design Compiler 报告）`[pdf:E05]` `[pdf:E11]`，但缺失两项关键形式化约束：一是无跨阶段顺序等价性（SEC）或端口不变性约束，无法阻止阶段二擅增端口或改变流水拍数；二是无多目标帕累托支配或带硬时序底线（如 $\text{Slack} \ge 0$）的标量化目标函数 `[pdf:E10]` `[pdf:E14]`。

## § 7 — 实验设计与结论

1. **实验平台与基准规模**：基于 **RTLLM** 全部 **29 个**涵盖算术单元、计数器、状态机、存储与 `asyn fifo` 的 Verilog 基准，统一采用 **OpenAI GPT-4o** 搭配 **Icarus Verilog**（功能验证）与 **Synopsys Design Compiler**（PPA 综合）（PDF 物理页 6–7，Section IV-A 与 Table II `[pdf:E11]` `[pdf:E12]`）。全文未披露具体工艺库名称、工作电压及目标时钟周期设定 `[pdf:E11]` `[pdf:E14]`。
2. **RQ1（功能正确性）定量结果**：Table II 对比 8 个基线——`Thakur et al.`（5/29）、`StarCoder`（5/29）、`GPT-3.5`（10/29）、`RTLCoder-Mistral-4bit`（12/29）、`RTLCoder-Mistral`（14/29）、`RTLLM GPT-3.5`（14/29）、`GPT-4`（15/29）与最强基线 `RTLLM GPT-4`（19/29，65.52%）。`VeriOpt` 达成 **25/29（86.21%，文中记 86%）** 功能通过率与 **100% 语法正确率**（无 `-` 项），独自攻克 `adder 64bit`、`FSM`、`asyn fifo` 等难题（PDF 物理页 1，Abstract `[pdf:E01]`；物理页 7，Table II 与 Section IV-B `[pdf:E12]` `[pdf:E13]`）。仅有的 4 个失败案例为 `div 8bit`、`parallel2serial`、`pulse detect` 与 `traffic light`——其中 `div 16bit` 通过而同结构的 `div 8bit` 失败，且 `traffic light` 在 `GPT-4`、`RTLCoder` 与 `RTLLM GPT-4` 上均通过而 `VeriOpt` 反倒失败；同时因缺少裸 `GPT-4o` 对照，6 个模块的净增混杂了基座代差与测试台反馈增益 `[pdf:E11]` `[pdf:E12]`。
3. **RQ2（PPA 综合质量）定量结果与异常核查**：
   - **局部算例**：Fig. 2 四状态 FSM 改用独热码与门控时钟后，动态功耗降 **85%**、漏电降 **25%**、面积降 **29%** `[pdf:E04]`；Fig. 6 `adder 16bit` 从基线（单元面积 **187.05 µm²**、设计面积 **202.13 µm²**、动态功耗 **19.62 µW** [内部 **16.33** + 翻转 **3.28**]、漏电 **236.33** [Table III 记 **0.23 µW**，对应 nW/µW 换算]、关键路径 **5.77 ns**）降至单元面积 **77.26 µm²**（改善 **58.70%**）、设计面积 **82.64 µm²**（**59.11%**）、动态功耗 **8.43 µW**（**57.03%**）、漏电 **91.67**（**61.21%**）、关键路径 **2.40 ns**（**58.40%**）`[pdf:E10]` `[pdf:E14]`。
   - **全量 25 模块前后对照（Table III）**：峰值增益出现在 `JC counter` 的单元面积缩减 **75.89%**（设计面积 **75.84%**，基准 `467.12/537.8 µm²`）、动态功耗缩减 **87.96%**（基准 `17.61 µW`）、漏电缩减 **76.87%**（另 `FSM` 动态功耗降 **85.51%**），`div 16bit` 关键路径长度缩减 **73.23%**（基准 `29.11 ns`），以及 `multi 16bit` 时序裕量改善 **39.44%**（基准 `-3.22 ns`）与 `multi pipe 4bit` 裕量改善 **90%**（基准 `-0.2 ns`），对应摘要 88%/76%/73% 峰值指标 `[pdf:E01]` `[pdf:E13]` `[pdf:E14]`。负向折中包括 `right shifter` 裕量因基数仅 `-0.02 ns` 恶化 **-50%**（面积/路径改善 `0%`），以及 `multi 8bit`（**-2.97%**）、`multi pipe 8bit`（**-5.84%**）、`signal generator`（**-3.36%**）、`PE`（**-0.16%**）的漏电微增 `[pdf:E13]` `[pdf:E14]`。Fig. 7 归一化曲线显示优化设计在三组二维折中图上整体优于基线 `[pdf:E15]`。
   - **两处报表异常**：其一，Table III 将 `JC counter`、`freq div`、`signal generator`、`calendar`、`asyn fifo` 等明确含时钟的时序模块标为 `CP Slack = N/A`（表注却称仅组合电路标 `N/A`），反映部分时序模块可能漏配时钟约束 `[pdf:E07]` `[pdf:E14]`；其二，其余 13 个有裕量模块均满足 `CP length + CP Slack ≈ 0.26–0.32 ns`，暗示施加了约 `0.3 ns`（超 `3 GHz`）激进时钟，导致所有基线裕量全负，所谓“73% 时序收敛提升”实为无裕量项 `div 16bit` 的路径长度缩减率 `[pdf:E01]` `[pdf:E14]`。

## § 8 — Take-aways

**5 句话版**：现有 LLM 生成 Verilog 多止步于通过仿真测试台的功能验证，忽视了决定流片成败的 PPA 综合质量 `[pdf:E01]` `[pdf:E03]`。VeriOpt 在零微调条件下提出两阶段流水线：先由 Planner、Programmer、Reviewer、Evaluator 四角色配合行内注释与 Icarus Verilog 报错闭环确保功能正确与可调试性 `[pdf:E05]` `[pdf:E07]`。再将基线 RTL 的 Synopsys Design Compiler 标量综合报告、CMOS VLSI 一阶估算方程及 15 类 RT 级变换模板注入上下文，驱动微架构重写 `[pdf:E09]` `[pdf:E10]`。在 RTLLM 29 个基准上，VeriOpt（GPT-4o）取得 25/29（86%）功能通过率与 100% 语法正确率，并实现最高 87.96% 动态功耗下降、75.89% 单元面积缩减与 73.23% 关键路径缩短 `[pdf:E12]` `[pdf:E14]`。但第二阶段仍依赖外部人工综合环且缺失优化后功能等价与时钟电学规约的自动闭环核验 `[pdf:E10]` `[pdf:E16]`。

**3 句话版**：VeriOpt 将零微调 RTL 生成解耦为“带注释追踪的四角色仿真纠错闭环”与“综合标量报告加 VLSI 解析公式引导的上下文 PPA 重写”两阶段 `[pdf:E05]` `[pdf:E09]`。它在 RTLLM 上实现 25/29 功能通过率，并大幅压降了阶段一基线代码的面积、功耗与关键路径延迟 `[pdf:E12]` `[pdf:E14]`。该方法证明标量综合摘要配一阶物理公式足以唤醒大模型的微架构改写能力，但开环重构潜藏端口篡改、组合门控毛刺与跨拍失配风险 `[pdf:E04]` `[pdf:E10]` `[pdf:E16]`。

**1 句话版**：VeriOpt 用“四角色白盒仿真闭环 + 综合标量报告与 VLSI 公式驱动的上下文重写”打通了零微调 RTL 功能生成与 PPA 优化，但也暴露出开环重构缺乏接口/周期等价及电学规约硬约束的核心短板 `[pdf:E05]` `[pdf:E10]` `[pdf:E16]`。

## § 9 — 最脆弱的假设

本文最脆弱且失效代价最大的唯一核心假设是：**对已通过功能仿真的基线 RTL 施加单轮开环的 PPA 上下文重写（Stage 2），能在不破坏顶层端口契约、周期精确功能等价性与时钟树电学规约的前提下，稳定兑现真实的微架构 PPA 净收益。**

作者给出的正面支撑是 25 个优化模块均能被 Design Compiler 综合并取得面积、功耗与路径缩减（PDF 物理页 7–8，Table III `[pdf:E13]` `[pdf:E14]`）。但源 PDF 内部直接暴露了三条反证：第一，Fig. 3 中阶段二输出后无回接测试台的回归验证环 `[pdf:E05]`，且 Fig. 6(d) 的 `full_adder_16bit_leakage_opt` 为实现操作数隔离擅自新增了原规范不存在的 `enable` 端口，若直接接回原测试台将因端口悬空输出全 `X` 态挂死，同理插入流水线必然改变响应拍数而击穿逐拍比对测试台 `[pdf:E07]` `[pdf:E10]`；第二，Fig. 2(c) 示范代码写出 `wire clk_en=(state==COMPUTE1||COMPUTE2); wire clk_gated = clk & clk_en;`，其中非零常量 `COMPUTE2 = 4'b0100` 使逻辑或恒为 `1'b1` 导致门控彻底失效，且无锁存器的组合与门时钟在 ASIC/FPGA 中会产生致命时钟毛刺（Clock Glitch）`[pdf:E04]`；第三，Fig. 6 列出三份不同优化代码却仅附唯一一张综合表，回避了单份合法 RTL 能否同时兼得各项收益的验证 `[pdf:E10]` `[pdf:E14]`。

## § 10 — 最小复现实验

无需商用 Synopsys 许可，可在 **1 周内**用全开源工具链完成最小验证/证伪实验：
- **输入子集**：从开源 RTLLM 抽取 **8 个模块**（算术类：`adder_16bit`、`adder_32bit`、`multi_8bit`、`ALU`；时序类：`signal_generator`、`FSM`、`JC_counter`、`multi_pipe_8bit`）及官方未改测试台。
- **实现与四组单变量对照**：固定 `GPT-4o`（`temperature = 0.2`，上限 `5` 轮），用 Python 脚本串联 **Icarus Verilog**、**Yosys**、**OpenSTA**（NanGate 45nm 库，统一对含 `clk` 模块配 `2.0 ns` 时钟约束）与 **Verilator lint**，对比：(G0) 裸 `GPT-4o` 单次生成；(G1) `GPT-4o` + 仅测试台报错闭环（无 Planner/Reviewer）；(G2) 完整阶段一四角色闭环；(G3) 阶段一 + 阶段二 PPA 重构，并强制不改原端口与原测试台重跑回归仿真。
- **核心指标与判据**：(1) 若 `G1` 与 `G2` 通过数差值 $\le 1$，则证明原表增益主因是 `GPT-4o` 基座与仿真反馈而非四角色拆解；(2) 若 `G3` 在原测试台下的回归通过率低于 `75%` 或出现裸 `clk & en` 毛刺告警，则证伪“开环 Stage 2 自动保持功能与电学合规”假设；(3) 若 `G2` 的面积-延迟积（ADP）比 `G0` 劣 `30%` 以上而 `G3` 仅回落至 `G0` 附近，则证实高优化率主要源于消除阶段一自身过度展开的冗余基线。

## § 11 — 最强反例设计

1. **可构造病态死锁场景：定拍协议下的跨状态机-宽算术耦合核**。构造一个要求严格在第 `4k` 拍输出精确饱和结果的 32 位迭代乘加滤波器核（或实时暂态仿真定步长历史电流源更新核），令“状态译码 + 32 位乘加 + 饱和比较”单拍关键路径超出目标时钟周期 `40%`。由于布尔算术深度下界限制，纯组合改写无法消除时序违例；而阶段二一旦采纳 Fig. 5 推荐的流水线切分（Pipelining）或资源复用插入哪怕 1 拍寄存器，输出延迟即变为 `4k+1` 拍，在缺少外部协议协商与测试台重对齐机制下必然 100% 触发功能判错，陷入“保定拍必违例、插流水必挂仿真”的死锁 `[pdf:E07]` `[pdf:E09]`。
2. **强替代解释（Planner 原语展开导致的基线膨胀假说）**。现代综合器面对单行行为级 `assign {cout, sum} = a + b + cin;` 会自动调用 DesignWare 树形算术库生成优质网表；但 VeriOpt 阶段一的 Planner 强令将设计拆成底层原语步骤 `[pdf:E06]`，诱导 Programmer 写出 16 级 `generate` 布尔门级行波进位链（Fig. 6(a)），人为阻断了综合器算子推断并制造出 32 级逻辑深度的膨胀基线，而阶段二的 Fig. 6(e) 仅将其删回单行 `a + b + cin` `[pdf:E10]`。因此部分超高百分比改善实质是“修复阶段一自身引入的反综合写法”，而非超越常规行为级编码。

## § 12 — Follow-up Research Bet

### 主研究押注：延迟弹性参数化硬件生成器与综合算子指令的双层联合合成

针对扁平无参 Verilog 既易遮蔽综合器算术推断又锁死固定拍数接口的症结（PDF 物理页 5–6，Fig. 5 与 Fig. 6 `[pdf:E09]` `[pdf:E10]`；物理页 8，Section V-C `[pdf:E16]`），提出主研究押注：**将大模型生成对象从扁平 Verilog 源码重构为“延迟弹性（Latency-Elastic）参数化硬件生成器（Chisel / 参数化 SystemVerilog）+ 综合器映射约束脚本（SDC 与数据通路算子属性）”的双层联合合成**，同时改变三项基本设计变量：

1. **改变状态表示与可控变量**：禁止手写门级展开链或裸组合门控时钟，改为输出显式暴露**流水级数 $L$、并行度 $U$、折叠因子 $M$ 与状态编码参数**的生成器代码及配套综合指令（集成时钟门控 ICG 综合属性、算术树结构选择指令与多频点时钟扫描脚本），将高层微架构决策与底层无毛刺单元映射彻底解耦。
2. **改变时间尺度与物理拓扑**：将模块边界升级为带 `ready/valid` 握手的**延迟弹性流式拓扑**，使调节内部流水深度 $L$ 与复用度 $M$ 仅平滑改变吞吐间隔与端到端拍数，不再破坏外部事务顺序。
3. **改变系统边界与评价对象**：构建直连综合器与形式化引擎的自动内环，将评价指标从未知单频点下的基线百分比差值改为**跨时钟周期网格扫描的后综合面积-延迟-能耗三维帕累托超体积（Pareto Hypervolume）**，并以**跨周期事务级形式等价验证（Transaction-Level Equivalence Checking）**替代脆弱的逐拍波形硬比对。

### Wild-Card Alternative（异构机制备选）

**基于 E-Graph 等价饱和（Equality Saturation）与标准单元库物理代价模型的确定性 RTL 代数重写**：剥离大模型直接改写源码的职责，仅令其生成局域布尔/算术等价重写规则库，在 E-Graph 上展开等价微架构空间并结合单元库真实面积、电容与延迟代价由整数规划直接提取严格等价的帕累托最优网表。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title / Abstract / Section I (RQ1, RQ2 & Core Contributions)"
[pdf:E02]: <_evidence/E02-p001-page.png> "PDF 物理页 1，Fig. 1 / Section I (Existing LLM-based HDL generation flow and its limitations)"
[pdf:E03]: <_evidence/E03-p002-page.png> "PDF 物理页 2，Table I / Section II-A (Comparison of recent works on RTL generation by LLMs)"
[pdf:E04]: <_evidence/E04-p002-page.png> "PDF 物理页 2，Fig. 2(a)-(c) / Section II-B & II-C (GitHub 0.3% HDL distribution & FSM one-hot/clock-gating example)"
[pdf:E05]: <_evidence/E05-p003-page.png> "PDF 物理页 3，Fig. 3 / Section III-A1 & III-A2 (Overview of VeriOpt multi-role and contextual PPA prompting flow)"
[pdf:E06]: <_evidence/E06-p003-page.png> "PDF 物理页 3，Section III-A2 (Role specifications of LLM Planner, LLM Programmer, and LLM Reviewer)"
[pdf:E07]: <_evidence/E07-p004-page.png> "PDF 物理页 4，Fig. 4 / Section III-A2 (Signal Generator 4-role execution flow, testbench error logs, and LLM Evaluator loop)"
[pdf:E08]: <_evidence/E08-p005-page.png> "PDF 物理页 5，Section III-B1 (Challenges C1-C5 in fusing PPA-awareness to LLMs)"
[pdf:E09]: <_evidence/E09-p005-page.png> "PDF 物理页 5，Fig. 5 / Section III-B2 (Contextual learning strategies S1-S4 & VLSI power/delay estimation equations)"
[pdf:E10]: <_evidence/E10-p006-page.png> "PDF 物理页 6，Fig. 6(a)-(f) / Section III-B3 (16-bit full adder PPA optimization case study and synthesis reports)"
[pdf:E11]: <_evidence/E11-p006-page.png> "PDF 物理页 6，Section IV-A1 to IV-A3 (Experimental setup: RTLLM 29 benchmarks, GPT-4o, Icarus Verilog, Synopsys Design Compiler)"
[pdf:E12]: <_evidence/E12-p007-page.png> "PDF 物理页 7，Table II / Section IV-B (Functional correctness comparison across 29 RTLLM benchmarks, 25/29 pass rate)"
[pdf:E13]: <_evidence/E13-p007-page.png> "PDF 物理页 7，Section IV-C (Quality evaluation analysis, peak PPA improvements, and negative trade-off cases)"
[pdf:E14]: <_evidence/E14-p008-page.png> "PDF 物理页 8，Table III (Baseline vs. VeriOpt PPA metrics across 25 functionally passing RTLLM designs)"
[pdf:E15]: <_evidence/E15-p008-page.png> "PDF 物理页 8，Fig. 7 / Section V-A & V-B (Normalized PPA trade-off plots, effectiveness, and future RAG/fine-tuning discussion)"
[pdf:E16]: <_evidence/E16-p008-page.png> "PDF 物理页 8，Section V-C & Section VI (Limitations regarding manual synthesis feedback loop, context window, and Conclusion)"
