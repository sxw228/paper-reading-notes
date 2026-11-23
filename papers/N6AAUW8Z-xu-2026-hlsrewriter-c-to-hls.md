# HLSRewriter: Efficient Refactoring and Optimization of C/C++ Code with LLMs for High-Level Synthesis

- **作者**：Kangwei Xu, Grace Li Zhang, Xunzhao Yin, Cheng Zhuo, Ulf Schlichtmann, Bing Li
- **出处**：ACM Transactions on Design Automation of Electronic Systems (TODAES), Vol. 31, No. 4, Article 61
- **年份**：2026
- **DOI**：10.1145/3749986
- **Zotero key**：N6AAUW8Z

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

高级综合（High-Level Synthesis, HLS）能够将 C/C++ 自动编译为 Verilog 等硬件描述语言（HDL），降低专用加速器开发门槛 [pdf:E02]（物理页 2，Section 1）。但常规面向 CPU 编写的 C/C++ 软件代码与商业 HLS 可接受的高效硬件代码（HLS-C）之间存在两道硬性鸿沟：

第一是**可综合子集（Synthesizability）断裂**。CPU 程序依赖运行时调用栈与动态堆管理，广泛使用二级/动态指针（Catapult 报错 `CIN-243`）、动态内存分配与变长数组（`malloc()` / VLA，报错 `CIN-15`、`CIN-16`）、递归调用（报错 `CIN-15`）、C++ 虚函数（报错 `HIER-10`）、STL 容器（如 `std::queue`）、布尔自增或复合赋值（报错 `CRD-708`）、不完备分支（报错 `CRD-127`）以及异常栈展开与越界访问（报错 `CRD-175`）[pdf:E04][pdf:E17][pdf:E18]（物理页 4 Table 1；物理页 19 Fig. 13；物理页 20 Fig. 15）。硬件电路要求编译期确定静态存储拓扑与有限状态机边界，商业 HLS 对上述构造直接拒编，迫使兼具软硬件经验的工程师耗费大量精力手工重写 [pdf:E04][pdf:E05]（物理页 4–5，Section 2 & Fig. 1）。

第二是**执行模型与字长粒度的架构失配**。即便消除语法报错，CPU 串行代码常将访存与计算耦合在深层嵌套循环内，阻碍任务级流水线（pipelining）展开；若盲目做细粒度展开，又会导致专用集成电路（ASIC）寄存器与面积急剧膨胀 [pdf:E02][pdf:E09][pdf:E10]（物理页 2 Section 1；物理页 9–10 Section 3.4 & Fig. 5）。同时，CPU 默认采用 32/64 位标准 `int` 与 `float`，在定制硬件中维持过宽字长会显著推高算术单元面积、功耗与关键路径周期 [pdf:E02][pdf:E11]（物理页 2 Section 1；物理页 11 Section 3.5）。

本文（HLSRewriter）旨在以常规不可综合 C/C++ 源码及关联测试集为输入，协同大语言模型（LLM）与商业 HLS/ASIC 工具链，最小化人工干预地完成**可综合化去错、延迟-面积平衡的渐进循环分解、定点位宽自动裁剪以及综合指令（pragma/Tcl）与重定时 PPA 优化** [pdf:E01][pdf:E06]（物理页 1 Abstract；物理页 6 Fig. 2）。

## § 2 — 前人工作与不足

既有研究主要分为“传统静态分析/DSL/模板脚本”与“早期 LLM 辅助 HLS 重构”两类，各自受制于明确的技术瓶颈：

### 1. 传统分析与模板脚本方法
- **静态指针分析与定制容器/递归扩展**：Ramanathan 等 `[8]` 通过静态指针分析减少全局互连，但无法处理动态多级复杂指针；Thomas `[10]` 提供 C++ 之上支持递归的 DSL，但需手工添加控制语句；SynADT `[11]` 用数据结构模板替代动态内存，但支持结构有限且仍需大量人工改写 [pdf:E02]（物理页 2，Section 1）。
- **参数化位宽与剖析顾问**：Thomas `[12]` 提供模板化软浮点后端但需人工指定位宽；Sensei `[13]` 结合剖析缩减位宽，但输入越界时依赖易出错的回退函数（fallback）[pdf:E02]（物理页 2，Section 1）。串联这些局部脚本仍会遗留大量复杂结构与 FIFO 声明问题（Fig. 1）[pdf:E05]（物理页 5，Section 2）。

### 2. 早期 LLM 辅助 HLS 框架
- **C2HLSC**（Collini et al. `[40, 41]`）：通过层次化分解、单元测试与编译反馈闭环将 C 转为 HLS-C，但依赖人工编写特定提示词与潜在人工核查，缺乏系统化官方手册知识支撑，面对复合不兼容错误时泛化受限 [pdf:E03][pdf:E05]（物理页 3 & 5）。
- **HLSPilot**（Xiong et al. `[42]`）：面向 CPU-FPGA 异构加速，片面追求最大吞吐率而激进展开循环，忽视了 ASIC 设计必需的延迟-面积折中，导致面积与功耗成倍失控（Fig. 10）[pdf:E05][pdf:E14]（物理页 5 Section 2；物理页 14 Fig. 10）。
- **Auto-Repair**（作者前作 `[43]`）：引入 RAG 与手册修正模板修复 HLS 错误，但连同上述工作仍遗留五项短板 [pdf:E03][pdf:E05]（物理页 3 & 5）：(1) 缺乏完备前置错误推理，易受编译器单轮漏报误导；(2) 修复模板库依赖人工构建；(3) 未系统量化对比不同递归消除策略的硬件开销；(4) 忽略面向延迟-面积平衡的流水线循环重构；(5) 未考虑浮点变量小数位宽的自动精度裁剪。

## § 3 — 重建作者的思考路径

站在作者完成前作 `Auto-Repair [43]` 后的视角，可以从三个真实工程卡点逆向推演出本文的六阶段设计：

1. **为什么单靠编译器报错触发 RAG 仍修不通复合代码？** 在包含指针、`malloc` 与递归的程序（如附录 I 二叉树 BFS）上，商业 HLS 编译器遇到前序指针与动态数组错误（`CIN-16`、`CIN-243`）便直接中止，根本来不及报出后文的递归错误 [pdf:E16][pdf:E18]（物理页 18 & 20）。若只拿残缺报错去检索，LLM 会在多轮试错中陷入幻觉。因此必须在改写前增加脱离编译器单次视野的全局预诊——强制按 `What → Where → Why` 三步枚举潜在不兼容点 [pdf:E07]（物理页 7，Section 3.2）；同时用关键词脚本扫描官方手册半自动生成短小 `T_ref` 模板并分批限量注入上下文，兼顾建库效率与长上下文聚焦 [pdf:E07][pdf:E08]（物理页 7–8，Section 3.3）。
2. **修通语法后，如何在打开硬件流水并行的同时刹住 ASIC 面积膨胀？** 软件嵌套循环把读写与计算绑死，但像 `HLSPilot` 一样直接细粒度全拆又会让寄存器面积爆炸 [pdf:E05][pdf:E10]（物理页 5 & 10）。自然解法是模仿编译器优化等级，采用**粗粒度优先、不达标再逐级细化、出错则带负向约束回退**的渐进分解策略 [pdf:E09][pdf:E10]（物理页 9–10，Section 3.4）。
3. **控制流定型后，怎样低成本榨干数据通路与后端指令潜力？** 与其让不擅长二进制算术的 LLM 直接猜位宽，不如让 LLM 生成剖析脚本：用测试集最大绝对值 $\max|x|$ 闭式锁定整数位宽，再从 1 bit 起逐轮递增小数位宽直至精度达标 [pdf:E11]（物理页 11，Section 3.5）；最后结合 HLS 设计分析器瓶颈报告，复用手册 RAG 范式检索 pragma 与 Tcl 指令并叠加电路重定时（retiming）收尾 [pdf:E12][pdf:E19]（物理页 12 & 21）。

## § 4 — 核心 Intuition

HLSRewriter 奏效的核心支点，是**将高度耦合的“软件 C++ 到高效 RTL 重构”正交拆解为四个因果隔离的层级，并为每一层绑定确定性的外部物理或文档锚点**：用“分步错误预诊 + 官方手册小模板分批 RAG”锚定**语法可综合化**，用“由粗到细三级渐进循环切分”锚定**任务级流水并发与面积平衡**，用“LLM 生成极值剖析与逐位测误脚本”锚定**定点数据通路字长**，最后用“综合瓶颈分析器 + 手册指令检索”锚定**局部 pragma/Tcl 调优** [pdf:E06][pdf:E11][pdf:E12]（物理页 6, 11, 12）。前人方法之所以顾此失彼，正是因为试图靠单一提示词或纯吞吐率目标同时跨越语法合法性、并发微架构与算术字长三重鸿沟，要么触发长上下文幻觉，要么引发 ASIC 面积与功耗失控。

## § 5 — 具体方法与完整 Pipeline

### 本次阅读重点正面回答：四层因果分工与定量评测指标设计

1. **反硬件软件代码向硬件友好形式的转换边界**：常规 C/C++ 的反硬件构造包括动态指针/堆分配/递归/虚函数等不可静态定界语义（Table 1 [pdf:E04]，物理页 4）、读写与算术紧耦合的深层串行循环（Fig. 5 [pdf:E10]，物理页 10）以及冗余的 32 位标准 `int`/`float` 类型 [pdf:E02][pdf:E11]（物理页 2 & 11）。HLSRewriter 通过四层接力将其重塑为硬件友好形式：
   - **手册模板 RAG 修复库（配前置分步推理，Stage 1–3）——负责“语法与数据结构可综合化”**：`What-Where-Why` 分步推理先补齐编译器首错中断漏掉的隐藏错误 [pdf:E07]（物理页 7，Section 3.2）；随后基于关键词脚本扫描 Catapult 官方手册建立的 **74 个独立 `T_ref` 模板**（覆盖 7 类错误，每份约 **200 tokens**，含报错日志、违规示例、手册解释与修正代码四要素），由 Sentence Transformer 按报错检索并以**每批最多 3 份**注入 Prompt，将指针、动态分配与递归改写为静态数组池索引与迭代/模板/显式栈结构 [pdf:E07][pdf:E08][pdf:E09]（物理页 7–9，Section 3.3）。
   - **流水感知分解（Pipeline-Aware Decomposition，Stage 4）——负责“宏观控制流与任务级流水重构”**：在可综合代码 `C_Ref` 上按从粗到细三级策略（多层嵌套拆流式生产-消费函数 → 单层循环异构阶段拆独立子函数 → 单循环按 `[0, floor(n/2)-1]` 与 `[floor(n/2), n-1]` 对半切分加尾部残余循环）渐进打开并行流水，仅在粗粒度延迟不达标时才升级细粒度策略，以此控住 ASIC 寄存器面积开销 [pdf:E10]（物理页 10，Section 3.4 & Fig. 5）。
   - **位宽精度调节器（Floating-Point BWA，Stage 5）——负责“算术数据通路定点字长压缩”**：由 LLM 生成位宽调节脚本，先提取测试集仿真轨迹极值一步算出有符号整数位宽 `ac_int`/`ac_uint` 或 `ac_fixed` 整数部，再从 1 bit 小数位宽起步逐轮加宽直至满足任务精度要求 [pdf:E11]（物理页 11，Section 3.5 & Fig. 6）。
   - **指令调优与重定时（PPA Optimization，Stage 6）——负责“微观综合指令与时序收敛精调”**：在通过 C-RTL 协同仿真后，依据 HLS 设计分析器定位的面积/功耗/低频瓶颈代码段，从手册优化库检索 `#pragma hls_unroll`、`#pragma design_goal area`、双端口/缓存及 `run.tcl` 数组索引优化指令交由 LLM 注入，最后执行电路重定时缩短关键路径 [pdf:E12][pdf:E19]（物理页 12 Fig. 7；物理页 21 Fig. 17）。
2. **相对直接商业 HLS 与单一大模型的定量评测指标设计**：
   - **相对单一大模型（GPT-4 Turbo）及同类重构框架（GPT+Scripts、GPT+RAG、C2HLSC）**：主指标为**重构通过率（Refactoring / Simulation Pass Rate）** $\text{Pass Rate} = m/n$（每任务跑 $n = 15$ 个实例，每实例最多按 HLS 报错迭代查询 5 次；仅当生成代码**同时通过商业 Catapult HLS 综合 且 通过 C-RTL 功能仿真**时计入成功数 $m$ [pdf:E13]，物理页 13），辅以**分解迭代轮数缩减倍数**衡量渐进示例引导对盲目试错的收敛加速 [pdf:E14]（物理页 14）。
   - **相对直接商业 HLS 默认综合与 HLSPilot**：原始含动态指针/递归的软件代码在直接商业 HLS 下综合通过率为零；对已可综合的 `C_Ref`，以未施加对应优化前的 Catapult HLS + **Synopsys Design Compiler（Nangate 45nm 工艺库）** 门级综合结果为 `100%` 基准，对比归一化**延迟（Latency）、面积（Area, $\mu\text{m}^2$）与功耗（Power, mW）**，并在浮点任务上联测相对浮点输出的**精度损失百分比（Precision Loss）** [pdf:E13][pdf:E14][pdf:E15]（物理页 13–15）。

### 六阶段 Pipeline 与二叉树 BFS 贯穿实例

结合总框图 Fig. 2 [pdf:E06]（物理页 6）与附录 I–II 的广度优先搜索（`bfs.cpp` → `bfs_hls.cpp`）演化过程 [pdf:E16][pdf:E17][pdf:E18][pdf:E19]（物理页 18–21），在线流水线如下（离线预先建好 74 份修复模板库、通用提示词与 pragma 优化库 [pdf:E07]，物理页 7）：

- **Stage 1（分步推理诊断）**：70 行 `bfs.cpp`（含 `TreeNode*`、两处 `malloc`、`std::queue` 与递归建树 `bfs_build`，Fig. 13(a) [pdf:E17]）首轮送入 Catapult 仅报出动态指针（`CIN-243`）与 `malloc`（`CIN-16`）便中断 [pdf:E16][pdf:E18]。LLM 结合 7 类常见禁忌执行 `What-Where-Why` 推理，补抓出 `bfs_build` 内的递归不可综合问题（注：Fig. 14 真实输出虽将自调用函数名误写为 `insert` 并幻觉出内层 `for` 循环，但仍正确锁定了第 46–57 行 `bfs_build` 代码块 [pdf:E18]，物理页 20）。
- **Stage 2–3（手册 RAG 迭代重构）**：Sentence Transformer 根据错误日志与推理结论检索出指针、动态数组、递归 3 份 `T_Ref` 模板注入 Prompt（Fig. 15 [pdf:E18]）。文中归纳了三种递归消除图式（Fig. 4 [pdf:E09]，物理页 9）：循环迭代替换、Catapult C++ 模板编译期展开（`Templ_Func<Depth>`）与显式静态栈模拟。在生成的 `bfs_hls.cpp`（Fig. 13(b) [pdf:E17]，物理页 19）中，LLM 定义 `#define MAX 10` 与全局静态池 `TreeNode Pool[MAX]`，将指针改为整型下标，将 `std::queue` 改为定长数组 `int queue[MAX]`，并将 `bfs_build` 的二叉搜索树尾递归改写为 `while (1)` 索引下探循环（注：附录 I 第 18 页正文误称此处用了显式栈，核对第 19 页 Fig. 13(b) 第 22–45 行源码实为无栈 `curr` 游标迭代 [pdf:E16][pdf:E17]）。编译失败则反馈报错迭代修复（上限 5 轮）直至产出 `C_Ref` [pdf:E06][pdf:E13]。
- **Stage 4（流水感知渐进分解）**：按需依次尝试 Strategy 1（如边缘检测 `ED` 将像素读取嵌套循环与 3×3 卷积拆为经 `stream` 通信的两个函数，Fig. 5(a)）、Strategy 2（如 `DFS` 将节点插入与中序遍历拆为独立子函数，Fig. 5(b) & Fig. 16）与 Strategy 3（如 `SortAndProc` 对半切分索引区间并补尾部迭代，Fig. 5(c)）；若改写出错且重试无果，则回退至上一有效版本并附加负向约束 [pdf:E09][pdf:E10][pdf:E19]（物理页 9–10, 21）。
- **Stage 5（BWA 位宽调节）**：脚本分析测试集轨迹极值，在 `bfs_hls.cpp` 中将 32 位 `int` 接口收窄为 9 位有符号 `ac_int<9, true>` [pdf:E17]（物理页 19）；对 `DNN` 等浮点任务则固定整数位宽（如 11 bits）后从 `ac_fixed<12, 11>` 起逐轮递增小数位宽 `M`（`ac_fixed<12+M, 11>`）直至满足精度阈值（Fig. 6）[pdf:E11]（物理页 11）。
- **Stage 6（等价验证与 PPA 调优）**：通过 C-RTL 协同仿真验证后，针对 `bfs_hls.cpp` 的 `Large Area` 瓶颈，LLM 从优化库检索出 `Opt_A1` 与 `Opt_A2`，在源码第 15 行插入 `#pragma design_goal area` 并在 `run.tcl` 中设置 `directive set ARRAY_INDEX_OPTIMIZATION true`，最后辅以寄存器重定时完成优化 [pdf:E12][pdf:E17][pdf:E19]（物理页 12, 19, 21）。

## § 6 — 核心数学推导（无形式化数学则跳过）

全文以编译/综合闭环与提示工程为主，唯一显式给出的形式化算式是第 3.5 节（物理页 11）BWA 模块计算变量有符号整数部分位宽 $m$ 的分段公式 Eq. (1) [pdf:E11]（另在第 4 节物理页 13 给出通过率统计定义 $\text{Pass Rate} = m/n$ [pdf:E13]）；其余阶段依靠编译器检查、C-RTL 仿真与版本回退保障严谨性。

### 1. 有符号整数位宽公式 Eq. (1) 及其硬件补码边界审视
给定变量 $x$ 在测试集仿真轨迹上的最大绝对值 $\max|x|$，BWA 按下式确定有符号整数位宽 $m$ [pdf:E11]（物理页 11，Eq. (1)）：

$$m = \begin{cases} 1, & \text{if } \max|x| < 1, \\ \lceil \log_2(\max|x|) \rceil + 1, & \text{otherwise.} \end{cases}$$

- **工程含义与分段动机**：$m$ 对应 `ac_int<m, true>` 或 `ac_fixed<m+F, m, true>` 中含符号位在内的整数总位数，目标表征补码有符号整数区间 $[-2^{m-1}, 2^{m-1}-1]$（定点区间为 $[-2^{m-1}, 2^{m-1}-2^{-F}]$）[pdf:E11]（物理页 11，Fig. 6 & Eq. (1)）。引入 $\max|x| < 1$ 分支是为了防止纯小数信号（如 $\max|x|=0.25$ 或 $0$）代入对数后得出 $m \le 0$ 或 $\log_2(0) = -\infty$ 的病态结果，强制保留 1 位符号位以合法覆盖 $[-1, 1-2^{-F}]$。
- **隐藏的正二次幂边界溢出缺陷**：由于二进制补码正负表示范围不对称，当正半轴极值恰为二次幂 $x = +2^k$（$k \ge 0$）时，Eq. (1) 会少算 1 bit：例如 $x = +1.0$ 时落入第二分支得 $m = \lceil \log_2(1) \rceil + 1 = 1$，可表示上限仅 $1 - 2^{-F} < 1.0$；$x = +4$ 时得 $m = \lceil \log_2(4) \rceil + 1 = 3$，对应补码区间 $[-4, +3]$，$+4$ 直接越界并在默认无饱和模式下翻转为 $-4$。严格无溢出的正半轴位宽应为 $\lfloor \log_2(x_{\max}) \rfloor + 2$（$x_{\max} \ge 1$）。

### 2. 小数位宽的经验单调搜索
小数位宽未做解析误差传播建模，而是从 1 bit 起按 `ac_fixed<m+1+M, m>` 逐轮加一重跑仿真，依赖“面积/功耗随字长单调递增、任务精度损失大致单调递减”的经验规律搜索满足精度下限的最小 $M$ [pdf:E11][pdf:E15]（物理页 11 & 15）。

## § 7 — 实验设计与结论

实验在 Intel Xeon Silver 4314（2.40 GHz）上运行，通过 OpenAI API 调用 **GPT-4 Turbo**，前端采用 **Siemens Catapult HLS**，后端使用 **Synopsys Design Compiler** 与 **Nangate 45nm 开源标准单元库**综合门级面积、功耗与延迟 [pdf:E13]（物理页 13，Section 4）。基准集包含源自 `[10, 11, 13]` 与 LeetCode `[14]` 的 **24 个含不可综合错误的真实任务**（DP、HT、DNN、LP、BT、KNN、LL、DFS、BFS、ED、GA、BS、SVM、FT/FFT、CC、FS、CR、AES、DS、LIP、MPL、QRD、DF、TE）[pdf:E12]（物理页 12）。注：Fig. 8、Fig. 9(a)、Fig. 10 图例中的 `[38]`、`[36]`、`[37]` 系修回增补文献后图内硬编码标号未同步顺延，正文与图注明确对应 `Auto-Repair [43]`、`C2HLSC [41]` 与 `HLSPilot [42]` [pdf:E13][pdf:E14]（物理页 13–14）。

| 核心评测问题 | 基准规模与对比设置 | 定量结果与核心结论 |
| :--- | :--- | :--- |
| **Q1：分步推理与手册 RAG 对可综合通过率各自贡献几何？** | 全部 **24 个任务**（每任务 $n=15$ 实例 × 最多 5 轮查询）；对比裸调 `GPT-4 Turbo`、`GPT+Scripts`、`GPT+RAG` 与完整框架，并做 `10%/50%/80%` `T_ref` 抽样消融 [pdf:E13]（物理页 13，Fig. 8） | 通过率依次为：裸调基线 **55.83%** → 加脚本 **65.83%** → 加 RAG **79.73%**（较基线 **+23.90%**）→ 完整 HLSRewriter **86.67%**（较基线 **+30.84%**，较纯 RAG **+6.94%**）。模板抽样降至 `10%` 时通过率跌至 **60.54%**（降 **19.19%**），`50%` 与 `80%` 时回升至 **72.50%** 与 **76.38%**，印证手册模板覆盖度是抑幻觉关键 [pdf:E03][pdf:E13]（物理页 3 & 13）。 |
| **Q2：在外部同类基准上相对 C2HLSC 表现如何？** | 复用 **C2HLSC `[41]`** 的 9 个基准（Present、SHA256、CuSums、Monobit、Block、Overlap、Runs、Q.S.、AES），对齐工具与采样超参 [pdf:E14]（物理页 14，Fig. 9(a)） | 在绝大多数任务上优于或持平 C2HLSC（多项达 100%），平均仿真通过率提升 **14.81%** [pdf:E14]（物理页 14）。 |
| **Q3：三种递归消除方案的硬件代价孰优？** | **6 个含递归任务**（DP、HT、DNN、LL、DFS、BFS）对比显式栈、Catapult 递归模板展开与循环迭代替换 [pdf:E14]（物理页 14，Fig. 9(b)–(c)） | 相对显式栈模拟，模板展开平均省 **9.3%** 面积与 **6.84%** 功耗；**循环迭代替换**省去栈存储与控制开销，平均削减 **23.13%** 面积与 **16.92%** 功耗，效率最优 [pdf:E14]（物理页 14）。 |
| **Q4：渐进流水分解能否兼顾低延迟与省面积并击败 HLSPilot？** | **10 个可分解复杂任务**（DNN、DFS、BFS、ED、GA、SVM、FFT、CC、QRD、DF），对比分解前基线、直接提示词分解与 **HLSPilot `[42]`** [pdf:E14]（物理页 14，Fig. 10） | 相对分解前平均降低 **36.58%** 延迟而面积仅增 **7.38%**，比直接提示 `"decompose the task"` 减少 **2.61×** 迭代轮数；在可比延迟下较 HLSPilot 平均削减 **53.39%** 面积与 **41.46%** 功耗，克服了后者面积/功耗暴涨至 200%–280% 以上的弊病 [pdf:E03][pdf:E14]（物理页 3 & 14）。 |
| **Q5：浮点 BWA 与后端 pragma/重定时各自带来多少 PPA 收益？** | BWA 评测 **5 个浮点任务**（DNN、ED、GA、CC、Filter，`F1–F9`）；pragma+重定时评测全部 **24 个任务** [pdf:E15]（物理页 15，Fig. 11–12） | BWA 在保精度前提下平均降 **17.78%** 面积与 **7.52%** 功耗；pragma 调优配合重定时在 24 个任务上进一步平均削减 **24.99%** 面积、**12.69%** 功耗与 **18.34%** 延迟 [pdf:E03][pdf:E15]（物理页 3 & 15）。 |

## § 8 — Take-aways

- **5 句话版**：常规 C/C++ 难以直接综合为高效硬件，根源在于动态指针/递归/堆分配违反静态硬件约束，且串行深层循环与 32 位标准字长严重拖累 ASIC PPA [pdf:E02][pdf:E04]（物理页 2 & 4）。HLSRewriter 先用 `What-Where-Why` 分步推理补抓编译器首轮漏报错误，再靠脚本从官方手册抽取的 74 份小模板做每批最多 3 份的限量 RAG，把重构通过率推高至 86.67% [pdf:E07][pdf:E08][pdf:E13]（物理页 7, 8, 13）。在可综合代码上，框架按“粗粒度流式拆循环 → 单层拆阶段 → 半区拆索引”渐进重构流水线，以 7.38% 的微小面积增量换取 36.58% 的延迟下降 [pdf:E10][pdf:E14]（物理页 10 & 14）。随后通过让 LLM 生成基于测试集极值与逐位测误的定点化脚本，并检索手册 pragma/Tcl 指令配合重定时，进一步压减算术通路与时序开销 [pdf:E11][pdf:E12]（物理页 11–12）。这表明在 EDA 代码重构中，将 LLM 限制在局部等价重写与剖析脚本生成、由分阶段工具反馈把关物理指标，远比单次端到端生成稳健。
- **3 句话版**：HLSRewriter 把 C/C++ 到优化 HLS-C 的转换正交切分为“分步预诊 + 手册小模板 RAG 去错”、“由粗到细渐进循环分解”、“测试集驱动的定点位宽调节”与“手册检索式 pragma/Tcl 调优”四层流水线 [pdf:E06]（物理页 6，Fig. 2）。该架构既靠官方手册锚点压制了硬件语法幻觉，又靠粗粒度优先策略守住了 ASIC 的延迟-面积平衡 [pdf:E08][pdf:E10]（物理页 8 & 10）。在 24 个任务与 Nangate 45nm ASIC 评测中，它在通过率上击败 C2HLSC，并在同级延迟下较 HLSPilot 节省逾一半面积 [pdf:E13][pdf:E14]（物理页 13–14）。
- **1 句话版**：HLSRewriter 以“分步错误预诊 + 官方手册小模板分批 RAG”打通 C/C++ 可综合化，再串联渐进循环分解、测试集定点位宽调节与指令重定时优化，在不引起 ASIC 面积膨胀的前提下实现了软件代码到高质量 HLS 硬件的自动演进 [pdf:E01][pdf:E06]（物理页 1 & 6）。

## § 9 — 最脆弱的假设

全文一旦失效代价最大的唯一核心假设是：**“捆绑测试集（Dataset/Testbench）的容量与值域完备性假设”——即假定随源码附带的有限离线仿真向量足以穷尽真实部署中的最大动态内存分配规模、全部变量动态范围及边界控制流，从而既能直接据以硬编码静态数组池大小与定点位宽，又能作为 C-RTL 等价性验证的充分判据** [pdf:E06][pdf:E11][pdf:E13]（物理页 6, 11, 13）。

- **论文给出的证据**：24 个基准在各自测试集上取得了 86.67% 的综合与 C-RTL 仿真通过率 [pdf:E13]（物理页 13），且 5 个浮点任务在扫描小数位宽 `F1–F9` 时呈现出平滑可控的精度-面积功耗折中（Fig. 11）[pdf:E15]（物理页 15）。
- **论文回避与暴露出的致命缺口**：
  1. **静默删掉溢出回退接口且无静态池越界保护**：对比物理页 19 Fig. 13(a) 与 Fig. 13(b)，原始 `bfs.cpp` 含有第 4 个参数 `int *fallback` 处理动态分配失败，而重构后的 `bfs_hls.cpp` 直接删去 `fallback` 端口、硬编码 `#define MAX 10`，且在 `Pool[nextFree++]` 与 `queue[rear++]` 处没有任何 `nextFree < MAX` 检查 [pdf:E17]。一旦真实输入规模 $n > 10$，硬件即发生静默内存写穿与死循环，但在 $n \le 10$ 的捆绑测试集上却被判为“等价通过”。
  2. **极值紧贴测试集且正二次幂溢出**：Eq. (1) 不留任何保护位（guard bits），在 $+1, +4, +8$ 等正二次幂处直接发生补码符号翻转 [pdf:E11]（物理页 11），`bfs_hls.cpp` 也将 32 位 `int` 锁死为仅覆盖 $[-256, +255]$ 的 `ac_int<9, true>` [pdf:E17]（物理页 19）。
  3. **混用校准集与测试集**：全文未划分独立的分布外（OOD）模糊测试集，也未采用有界模型检验（如 CBMC）做符号等价验证，无法区分“针对固定测试向量过拟合裁剪”与“输入空间普遍等价”。

## § 10 — 最小复现实验

无需商业 Catapult HLS 与 Design Compiler 许可证，可在 **1 周内**利用免费工具链验证本文正向增益并检验其分布外脆弱性：

1. **测试输入（4 个微内核）**：(i) 物理页 19 Fig. 13(a) 原版 70 行 `bfs.cpp` [pdf:E17]；(ii) 真双分支递归归并排序（强制触发显式栈或非平凡迭代改写）；(iii) 物理页 10 Fig. 5(a) 四层嵌套边缘检测 `ED` 与 Fig. 5(c) 奇数长度（$n=15$）`SortAndProc` [pdf:E10]；(iv) 二阶浮点 IIR 滤波器，校准集幅值 $[-3.8, +4.0]$（含 $+4.0$），独立测试集外推 `10%` 至 $[-4.2, +4.4]$。
2. **最小实现（约 350 行 Python + Vitis HLS / Bambu HLS）**：采用开源 **Siemens `ac_types` 头文件**与 Vitis HLS（或开源 Bambu HLS）配合 `g++ -fsanitize=address,undefined`；从公开 HLS 手册整理 15 条 200-token `T_ref` 模板，用 `all-MiniLM-L6-v2` 实现 top-3 分批检索，对比 `裸调 LLM`、`LLM+RAG`、`LLM+三步推理+RAG`（每内核 $n=15$ 次 × 5 轮反馈）[pdf:E07][pdf:E08][pdf:E13]（物理页 7, 8, 13），并按物理页 11 Eq. (1) 实现 BWA 脚本 [pdf:E11]。
3. **观测指标与判据**：统计校准集通过率、独立 OOD 测试集（$n \in [11, 32]$ 及 $+1.0/+4.0$ 峰值）输出一致率及流水线 II/周期变化。若校准集上 `三步推理+RAG` 较裸调提升 **>15%** 且 `ED` 流式分解降低周期 **>25%**，则核心机制复现成立；若校准集通过样本中有 **>50%** 在 $n > 10$ 或 $+4.0$ 向量上触发 ASan 越界或补码翻转，则直接验证 § 9 的脆弱性诊断。

## § 11 — 最强反例设计

### 1. 可构造病态反例：动态边重连就地松弛 + 极点贴近单位圆的闭环滤波内核
构造一段 120 行 C++ 程序 `DynamicGraphRelax`：前半段用指针邻接表与 `malloc` 动态删改图边，并对节点执行带距离-1 循环携带依赖的高斯-赛德尔就地更新 `phi[u] = (1 - omega) * phi[u] + omega * sum_neighbors(phi)`；后半段对结果做极点半径 $r = 0.995$ 的二阶浮点谐振滤波，校准集峰值恰为 $+8.0$。在此程序上三层核心机制将确定性失效：
1. **单一静态池端口争用击穿 Stage 3 与 Strategy 1/2**：指针拍平为全局数组 `EdgePool[MAX]` 后（如 `bfs_hls.cpp` [pdf:E17]，物理页 19），链式跳转变为数据相关间接访存 `EdgePool[EdgePool[curr].next]`，单/双端口 SRAM 读写冲突使流水线 II 退化为多拍串行；若强拆为两个流水函数，要么复制整块静态池令面积翻倍，要么共享全局数组导致握手阻塞。
2. **跨半区数据依赖击穿 Strategy 3**：高斯-赛德尔与 IIR 递推在 `i = floor(n/2)` 处严格依赖前半区末尾状态 `y[floor(n/2)-1]`，按 Fig. 5(c) 对半切分循环 [pdf:E10]（物理页 10）要么破坏依赖导致仿真报错并退回原版，要么被迫串行等待而净增冗余控制多路器。
3. **正二次幂溢出与极限环击穿 BWA**：峰值 $+8.0$ 代入 Eq. (1) 得 $m = 4$（`ac_fixed<4+F, 4, true>`，上限 $8 - 2^{-F}$）[pdf:E11]（物理页 11），在 $+8.0$ 处翻转为 $-8.0$；且高 Q 闭环反馈会放大定点舍入噪声形成极限环振荡，使单调递增小数位宽卡在超高位宽。

### 2. 审稿反方替代解释
论文 24 个基准中包含大量 LeetCode 风格短小单函数题目（如 Bubble Sort、Fibonacci、Cyclic Rotation、Max Points on Line [pdf:E12][pdf:E13]，物理页 12 & 16），其 `malloc` 与指针多为小规模规则计算外的表层语法包装，74 个手册短模板近乎直接给出了标准改写范式；这尚不足以证明缺乏控制数据流图（CDFG）与存储分体调度的纯文本改写能扩展至多文件共享复杂结构体与片上带宽受限的工业级系统代码。

## § 12 — Follow-up Research Bet

### 主研究押注：将重构载体从源码字符串升级为“控制数据流存储分体图 + 区间仿射算术图”双层中间表示，联合求解片上存储拓扑与解析字长上界

- **切入的未开发自由度**：HLSRewriter 试图优化受物理结构强约束的硬件流水与定点位宽，却始终只在一维 C/C++ 文本表面做句法对半切分与单测试集经验试探，闲置了编译器前端精确的**控制数据流图（CDFG）访存依赖距离**与数值分析的**解析误差传播代数**。
- **同时改变的三项基本设计变量**：
  1. **状态表示**：不再直接在源码文本上盲拆循环和试探位宽，而是由 LLM 完成高层指针静态池化与尾递归消除后，经 LLVM/MLIR 前端提取**带依赖距离向量的 CDFG 存储冲突图**与**区间仿射算术（Affine Arithmetic）传播图**；
  2. **可控变量与物理拓扑**：打破单一全局数组 `Pool[MAX]` 的扁平结构，将**片上多 Bank 存储分体因子、读写端口分配、流式 FIFO 深度与多面体循环变换矩阵**作为整数线性规划（ILP）可控变量，在给定面积上限下精确消解端口争用并最小化启动间隔（II）；
  3. **评价对象与字长定界机制**：废弃单测试集经验公式 Eq. (1) 与逐轮重仿真，基于输入物理值域区间用**仿射算术解析推导中间变量严格上下界（根除 $+2^k$ 补码正边界溢出）与噪声增益**，并用位向量 SMT 求解器（Bitwuzla）对有界循环做位精确形式化等价证明与越界不可达证明。

### Wild-card 备选方向（不同机制一句话版）
- **Wild-card Alternative**：绕开“把动态软件 C++ 静态拍平以迁就传统静态调度 HLS”的路线，直接面向**弹性握手数据流动态调度高级综合（Dynamically Scheduled HLS）与片上硬件空闲链表分配器 IP**联合训练代码生成模型，在硬件微架构层原生支持可变延迟间接访存与有界动态内存分配。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title / Authors / Abstract"
[pdf:E02]: <_evidence/E02-p002-page.png> "PDF 物理页 2，Abstract (cont.) / Section 1 Introduction"
[pdf:E03]: <_evidence/E03-p003-page.png> "PDF 物理页 3，Section 1 Introduction — Limitations & Main Contributions"
[pdf:E04]: <_evidence/E04-p004-page.png> "PDF 物理页 4，Section 2 Background / Table 1 (HLS-incompatible Types)"
[pdf:E05]: <_evidence/E05-p005-page.png> "PDF 物理页 5，Section 2 Background / Fig. 1 & Prior LLM-HLS Critique"
[pdf:E06]: <_evidence/E06-p006-page.png> "PDF 物理页 6，Section 3.1 Overview / Fig. 2 (Six-Stage Framework)"
[pdf:E07]: <_evidence/E07-p007-page.png> "PDF 物理页 7，Section 3.1–3.3 — Offline Prep, Step-Wise Reasoning & 74 T_ref Templates"
[pdf:E08]: <_evidence/E08-p008-page.png> "PDF 物理页 8，Section 3.3 / Fig. 3 — RAG Template Structure & Batching (Max 3 Files)"
[pdf:E09]: <_evidence/E09-p009-page.png> "PDF 物理页 9，Section 3.3–3.4 / Fig. 4 — Three Recursion Schemes & Rollback Mechanism"
[pdf:E10]: <_evidence/E10-p010-page.png> "PDF 物理页 10，Section 3.4 / Fig. 5 — Three Pipeline-Aware Decomposition Strategies"
[pdf:E11]: <_evidence/E11-p011-page.png> "PDF 物理页 11，Section 3.5 / Fig. 6 / Eq. (1) — Floating-Point Bit Width Adjuster (BWA)"
[pdf:E12]: <_evidence/E12-p012-page.png> "PDF 物理页 12，Section 3.6 / Fig. 7 / Section 4 — PPA Optimization & 24 Benchmarks"
[pdf:E13]: <_evidence/E13-p013-page.png> "PDF 物理页 13，Section 4 / Fig. 8 — Experimental Setup, Pass Rate & Template Sampling Ablation"
[pdf:E14]: <_evidence/E14-p014-page.png> "PDF 物理页 14，Section 4 / Fig. 9 & Fig. 10 — C2HLSC, Recursion Schemes & HLSPilot Comparisons"
[pdf:E15]: <_evidence/E15-p015-page.png> "PDF 物理页 15，Section 4 / Fig. 11 & Fig. 12 — BWA Precision-PPA Trade-off & Directive/Retiming PPA"
[pdf:E16]: <_evidence/E16-p018-page.png> "PDF 物理页 18，Appendix I — End-to-End BFS Refactoring Walkthrough"
[pdf:E17]: <_evidence/E17-p019-page.png> "PDF 物理页 19，Appendix I / Fig. 13 — BFS Original C++ vs Refactored HLS-C Code"
[pdf:E18]: <_evidence/E18-p020-page.png> "PDF 物理页 20，Appendix II / Fig. 14 & Fig. 15 — Step-Wise Reasoning & RAG Prompts"
[pdf:E19]: <_evidence/E19-p021-page.png> "PDF 物理页 21，Appendix II / Fig. 16 & Fig. 17 — Pipeline Decomposition & Tcl/Pragma PPA Prompts"
