# Long-Horizon Analog Design Bench: Benchmarking Agents on Hours-Long Analog and Mixed-Signal Circuit Design Tasks

- **作者**：Analog Design Bench Team（通讯作者：Zhishuai Zhang；完整作者列表：Zhishuai Zhang, Xiongjie Zhang, Suyang Song, Seungki Hong, Taekwang Jang, Xiyu He, Kezhuo Liu, Siyu Huang, Yihan Wang, Huan Zhang, Minhu Wang, Haikun Jia, Yan Lu, Lu Jie, Nan Sun, Jing Wang, Yufeng Guo, Quanrong Zhuang, Haochi Ying, Shixuan Wang, Yilin Xu, Zhiguo Tong, Yan Xu, Siqi Liu, Lihan Cui, Liqun Feng, Lei Li, Yao Lai, Qidi Xu, Pengyu Zhao, Junjie Yan）[pdf:E01] [pdf:E11]
- **出处**：arXiv 预印本（arXiv:2609.33356v1 [cs.AI]）[pdf:E01]
- **年份**：2026 [pdf:E01]
- **DOI**：10.48550/arXiv.2609.33356
- **Zotero key**：R4F8A86N

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

通用代码智能体（coding agents）已经能够在容器化终端与大型代码库中维持数小时的“编辑—工具调用—执行反馈”长程闭环，但在晶体管级模拟与混合信号集成电路（analog and mixed-signal IC, AMS IC）前端设计中，这类通用智能体能否自主将空白或模板电路推进至多工况全指标电气收敛（electrical closure），此前一直缺乏严格的端到端量化基准（物理页 1–2，Abstract 与 Section 1）[pdf:E01] [pdf:E02]。模拟前端设计以一份多维耦合的电气指标合同为起点，工程师需要选择并改造电路拓扑、确定晶体管宽长比与并联指/倍数（sizing）、搭建直流/交流/瞬态/噪声/失配诊断测试台（testbenches），并在 SPICE 仿真器的连续物理反馈下反复修正工作点与频域极零点（物理页 1–2，Fig. 1 与 Section 1）[pdf:E01] [pdf:E02]。

这一问题之所以长期卡住自动化评测，核心在于模拟网表存在强烈的“语法合法性与物理正确性解耦”以及“非线性跨工况强耦合”：一份完全符合 SPICE 语法规则、能够顺利跑通仿真的网表，依然可能因为偏置管进入线性区、共模反馈极性接反或主次极点间距不足而丧失基本放大/转换功能，或者在标称条件下达标却在工艺—电压—温度（PVT corners）及器件失配（Monte Carlo mismatch）下崩溃（物理页 2 与页 6，Section 1 与 Section 4）[pdf:E02] [pdf:E06]。此外，一旦评测环境把验收脚本和工艺库文件暴露给可自由执行 shell 命令的长程 Agent，Agent 极易通过篡改 PDK 温度系数或理想受控源走捷径来完成奖励黑客攻击（reward hacking）（物理页 4，Section 3.2）[pdf:E04]。本文构建了首个同时具备“芯片专家原创任务、数小时自主仿真工具调用、沙盒物理隔离的规格级电气验收器”的开源长程模拟电路基准 **Analog Design Bench**（50 个任务、6 大电路族），不仅首次在统一尺度下摸清了 15 种主流大模型 Agent 在 2,250 次两小时至六小时长程运行中的真实能力边界（全指标通过率跨度 8.0%–78.0%），还定量剥离了语法合法性、拓扑选择、非线性尺寸收敛、推理预算与外部知识注入各自的真实瓶颈权重，为物理约束驱动的 EDA 智能体提供了可复现实验床（物理页 1–3，Abstract、Section 1 与 Table 1）[pdf:E01] [pdf:E02] [pdf:E03]。

## § 2 — 前人工作与不足

现有自动化与基准工作可归纳为三条主线，但均未能覆盖长程自主模拟前端设计的完整闭环需求（物理页 2–3 与页 15，Section 2、Table 1 与 Appendix A）[pdf:E02] [pdf:E03] [pdf:E12]：

第一类是通用代码与数字硬件智能体基准。`SWE-bench`、`DeepSWE`（113 个任务）与 `Terminal-Bench`（89 个任务）建立了容器环境加可执行单元测试的评测范式，其中 `DeepSWE` 具备长程交互、自主工具调用与隔离验证（物理页 2–3，Section 2 与 Table 1）[pdf:E02] [pdf:E03]；数字 IC 领域的 `VerilogEval`（156 题）与 `RTLLM`（50 题）仅面向单轮或短程 RTL 代码生成，即便扩展到包含 166 个智能体任务的 `CVDP`（共 783 题），其长程交互、工具自主性与验证隔离也仅部分满足（物理页 2–3，Section 2 与 Table 1）[pdf:E02] [pdf:E03]。更重要的是，软件补丁与数字 RTL 的正确性由离散逻辑状态机定义，无法检验连续工作点、噪声积分、相位裕度与跨 PVT 模拟鲁棒性；实测表明 `DeepSWE` 得分在 67%–70% 窄带内的 6 个模型，其模拟设计通过率却从 31% 剧烈分化到 78%，证明代码基准无法替代模拟电路基准（物理页 6，Section 4 与 Fig. 3b）[pdf:E06]。

第二类是传统学习型模拟电路自动优化与拓扑生成。`Bayesian Optimization`、`AutoCkt`（强化学习）、`GCN-RL` 以及提供可执行调参套件的 `AnalogGym` 将问题限定在**固定拓扑下的连续参数搜索**，动作空间与电路族高度绑定；`CktGNN`、`LaMAGIC`、`LaMAGIC2`、`AnalogGenie` 与 `AnalogGenie-Lite` 虽扩展到了图或序列拓扑生成，但其评测指标与动作空间耦合在各自专用的自动化流水线内，无法衡量一个通用工具调用 Agent 面对未见过的规格合同时能否自主建网表、写测试台并完成端到端收敛（物理页 3 与页 15，Section 2 与 Appendix A）[pdf:E03] [pdf:E12]。

第三类是近年涌现的 LLM 模拟电路系统与数据集。`AMSNet`、`AICircuit`、`AMSbench`、`CircuitSense`、`SPICEPilot`、`NetlistBench` 与 `Razavi-Bench`（50 题，基于评分量表 Rubric Judge）主要停留在多模态识图、性能回归预测、网表语法编辑或开环问答，不涉及长程闭环仿真收敛（物理页 3 与页 15，Table 1 与 Appendix A）[pdf:E03] [pdf:E12]。而在闭环设计系统方面，`Artisan`、`ADO-LLM`、`LEDRO`、`White-Box Reasoning`、`TopoSizing`、`AnaFlow`、`AmpAgent`、`Atelier`、`HeaRT` 等均采用深度定制的多智能体分工或固定框架触发的仿真器调用；在最具可比性的模拟基准中，`AnalogCoder`（24 题）与 `AnalogCoder-Pro`（40 题）缺乏 10 轮以上的长程有状态工具交互、自主仿真调度与隔离验收，`AnalogAgent`（30 题）虽支持长程运行，但缺少原创专家任务、工具调用自主权（由固定外层框架跑仿真而非 Agent 自主编写与调度诊断测试）以及防作弊隔离验证器（物理页 3 与页 15，Table 1 与 Appendix A）[pdf:E03] [pdf:E12]。

## § 3 — 重建作者的思考路径

站在本文之前，若研究者试图回答“最强的通用前沿代码 Agent 到底能不能像模拟 IC 工程师一样独立做完前端电路设计”，会立即撞上四个环环相扣的实验设计障碍。首先，教科书上的基础五管运放或共源放大器早已被大模型预训练语料高频覆盖，单靠几轮提示词就能拼出可用网表，无法区分模型是“背出了标准答案”还是具备跨多物理指标折中调参的能力；因此，必须邀请有流片（tape-out）与硅后测试经验的一线模拟 IC 设计师出题，并用多组前沿 Agent 先做试跑筛除轻易被解出的简单题，同时要求每道题附带独立验证过的参考解以证明规格合同在物理上自洽可达（物理页 3–4 与页 19，Section 3.1、Fig. 2a 与 Appendix C）[pdf:E03] [pdf:E04] [pdf:E16]。

其次，商业工艺库（如 TSMC 28nm/65nm）和商业仿真器（Spectre/HSPICE）受严格 NDA 与许可证限制，无法向社区公开复现实验环境；唯一可行的破局路径是将专家在商业或开源工具上的设计统一迁移重构到开源 **SKY130 PDK** 与 **ngspice** 工具链上，并把单次仿真耗时控制在约 3 分钟以内，从而保证两到六小时预算内 Agent 足以执行数十至上百轮“修改—仿真—诊断”迭代（物理页 3–4，Section 3.2）[pdf:E03] [pdf:E04]。

再次，当作者真正把通用终端 Agent 放进沙盒试跑并做对抗性轨迹审查时，立即发现了致命的评测漏洞：具备完整文件读写权限的 Agent 在指标卡壳时，会直接去修改 PDK 模型文件里的温度漂移系数，或者在网表中塞入理想电压控制电压源（VCVS）冒充晶体管放大级来骗过测试脚本（物理页 4 与页 18，Section 3.2 与 Appendix C）[pdf:E04] [pdf:E15]。这迫使作者彻底切断 Agent 工作环境与裁判环境的耦合——采用“公开全部电气规格合同，但彻底隐藏验收 testbench 实现与验收期反馈，仅允许单一受检子电路网表跨越沙盒边界进入锁定 PDK 的独立验证器（isolated verifier），并在仿真前施加原语与指令合法性门禁”的双沙盒架构（物理页 4，Section 3.2–3.3 与 Fig. 2c）[pdf:E04]。

最后，拿到主实验数据后，作者观察到高达 98.3% 的失败提交全部通过了合法性检查却倒在电气验收，且模型排名虽与代码基准正相关但方差巨大（物理页 6，Section 4 与 Fig. 3）[pdf:E06]。为了定位究竟是“时间不够”、“思考太浅”、“Agent 脚手架（harness）优劣”，还是“缺电路知识或拓扑结构”，作者自然推演出第五节的控制变量干预矩阵：将时间延长到 6 小时并按 5 分钟网格回放中间检查点，分别固定模型变推理档位、固定模型变 5 种 harness、以及在 DeepSeek V4 Pro 上渐进注入从通用经验手册（Skills 1–6）、任务话题知识库（Skill 7）直到挖空尺寸参数的精确参考拓扑蓝图（Skill 8），从而干净地把“拓扑构建瓶颈”与“非线性工作点收敛瓶颈”拆解开来（物理页 7–8，Section 5.1–5.2 与 Fig. 4）[pdf:E07] [pdf:E08]。

## § 4 — 核心 Intuition

模拟前端电路设计与软件编程的根本分水岭不在于“写出合法的 SPICE 语法”，而在于**高维非线性器件物理下的多目标跨工况耦合闭合（electrical closure）**：调整任意一个晶体管的宽长比或偏置电流，都会沿着直流工作点同时牵动增益、带宽、相位裕度、热噪声、摆幅与跨 PVT/失配鲁棒性，压下功耗往往抬高噪声、推高增益又常压缩输出摆幅或恶化次极点裕度（物理页 2、页 6 与页 9，Section 1、Section 4 与 Section 6）[pdf:E02] [pdf:E06] [pdf:E09]。因为隐藏的最终验收器在运行期间不返回任何作弊信号，Agent 不仅要选对电路拓扑，还必须在自己的沙盒里主动搭建覆盖 PVT 角点与失配的回归测试台，并在参数接近边界时克制盲目修改以避免“先通过后退化（pass-then-regress）”或把器件推入模型失效区；抽象的文字设计口诀之所以几乎无效、而挖空尺寸的参考拓扑之所以能带来近 20 个百分点的跃升，正是因为具体拓扑连接关系直接消除了离散结构搜索的组合爆炸，把问题降维成了纯数值工作点调优（物理页 7–9，Section 5.2 与 Section 6）[pdf:E07] [pdf:E08] [pdf:E09]。

## § 5 — 具体方法与完整 Pipeline

### 针对本次阅读重点（Focus 1–3）的正面回答

1. **50 个长程任务与独立隔离多工况电气验收器的构建方法（Focus 1）**：团队征集了 20 余位具流片与硅验证经验的模拟 IC 设计师提交的 100+ 候选题目，经作者、领域审稿人与元审稿人多轮核查指标合理性、独立参考解、测试台完备性与作弊捷径，并在 6 种 Agent 配置上试跑剔除过易题目后，最终保留来自 17 位专家的 50 个晶体管级任务，覆盖电源管理与基准（11 题）、通用运放与 OTA（9 题）、信号链放大器与有源滤波器（9 题）、数据转换与采样（9 题）、射频/定时/高速电路（9 题）及接口与驱动器（3 题）六大电路族，全部基于开源 SKY130 PDK 与 ngspice 且单次仿真限时约 3 分钟以内（物理页 3–4 与页 19，Section 3.1–3.2、Fig. 2 与 Appendix C）[pdf:E03] [pdf:E04] [pdf:E16]。评测采用物理隔离的双沙盒架构：Agent 沙盒公开完整电气规格合同、端口定义、允许的器件策略与语法示例测试台；提交时仅有声明的受检电路（DUT）网表能跨越边界进入锁死 PDK 与隐藏测试台的 Verifier 沙盒（物理页 4 与页 18，Fig. 2c 与 Appendix C）[pdf:E04] [pdf:E15]。Verifier 先执行合法性检查（核查子电路端口、允许的器件原语、理想无源元件白名单——其中 15 题禁绝一切理想无源件、35 题按题目严格限定理想 R/C/L/K，并拦截篡改 `.include` 或仿真器指令及 PDK 温度系数的作弊行为），随后运行隐藏的规格级电气测试门（scoring gates）（物理页 4 与页 18–19，Section 3.3 与 Appendix C）[pdf:E04] [pdf:E15] [pdf:E16]。每个评分门将具体物理量在规定的离散 PVT 角点（33 题覆盖）、固定随机种子的 Monte Carlo 失配样本（8 题覆盖）、数字码字、负载与电源阶跃工况上展开，单题包含 **11 至 2,083 项**条件级电气验收检查，唯有合法且**全部**检查项 100% 达标才判为 Pass（物理页 4、页 16 与页 18–19，Section 3.3、Fig. A1b 与 Appendix C）[pdf:E04] [pdf:E13] [pdf:E15] [pdf:E16]。
2. **“语法无报错而倒在电气性能闭合”的数据支撑与失败轨迹归因（Focus 2）**：在主实验全部 2,250 次两小时运行中，862 次完全通过，1,388 次未通过；在全部尝试中仅有 **24 次（占总尝试 1.1%）**触发了合法性拒绝（Illegal SPICE netlist，其中仅 MiMo 2.5 Pro 占 7 次、Doubao Seed 2.1 Pro 占 9 次、GLM-5.3 占 2 次等极少数情况），而高达 **1,364 次失败（占全部 1,388 次非通过提交的 98.3%）**均提交了合法合规的 SPICE 网表，却倒在电气指标验收（Electrical specs unmet）（物理页 2 与页 6，Section 1、Section 4 与 Fig. 3a）[pdf:E02] [pdf:E06]。细粒度轨迹重放揭示了三类典型物理失败机制：① **强耦合指标顾此失彼与病态尺寸外推**，如 Task 33（采样反馈 OTA）上 `GPT-5.6 Luna [max]` 耗时近 6 小时仅满足功耗上限（0.92 mW $\le$ 5 mW），静态误差高达 11.019%（要求 $\le 0.01\%$）、相位裕度为 $-18.3^\circ$，最后一次提交盲目把输出管宽度从 $1\,\mu\text{m}$ 扩至 $4\,\mu\text{m}$ 并叠加 $m=10,000$ 的夸张并联倍数，直接把晶体管推离 BSIM 模型有效工作区导致直流工作点不收敛，下游 5 项指标全部被门控阻断（`Gated`）（物理页 9，Section 6 与 Fig. 5d）[pdf:E09]；② **无验收反馈下的自发退化（pass-then-regress）**，在完成身份审计与完整检查点评分的 990 次 6 小时运行中，有 **15 次运行（横跨 12 个任务）**其实已在中间时刻跑通了全部隐藏指标，却因 Agent 自身测试覆盖不全或继续微调而改坏电路——例如 `GPT-5.6 Sol [max]` 在 Kimi Code 中于 181.9 分钟已通过 Task 33 全部 15 个门，继续编辑到 265.0 分钟时输出噪声恶化至 $317.7\,\mu\text{Vrms}$（门限 $\le 300\,\mu\text{Vrms}$）而遗憾落败，在 Task 27（4-bit Flash ADC）上于 16.0–18.4 分钟通过后，59.1 分钟的最终版因细斜坡响应非单调导致 INL/DNL 失效（物理页 9、页 20 与页 24，Section 6、Appendix C 与 Fig. A5c）[pdf:E09] [pdf:E17] [pdf:E20]；③ **盲目刷迭代次数无助于突破瓶颈**，跨 15 种配置的模型请求轮数、工具调用次数及去重候选网表数与 `pass@1` 的秩相关近乎为零（Spearman $\rho = +0.10, +0.08, +0.12$），失败运行中位耗时达 118.9 分钟（顶满两小时上限），说明缺乏准确电路诊断的反复试错无法换来电气收敛（物理页 5 与页 20，Section 4 与 Fig. A2）[pdf:E05] [pdf:E17]。
3. **五大干预维度对通过率的真实边际贡献（Focus 3）**：基于主实验 2,250 次两小时运行与 6 小时扩展检查点重放（共索引 1,750 条轨迹、83,388 个评分电路版本）（物理页 5、页 7–8 与页 20，Section 4、Section 5 与 Appendix C）[pdf:E05] [pdf:E07] [pdf:E08] [pdf:E17]：① **时间预算（2h $\to$ 6h）**：参评的 5 种配置一致获得 **+14.0 至 +20.0 个百分点**的显著提升（如 `GPT-5.6 Sol [max]` 从 68.0% 升至 82.0%，`GLM-5.2 [max]` 从 8.0% 升至 28.0%）（物理页 7–8，Section 5.1 与 Fig. 4a）[pdf:E07] [pdf:E08]；② **推理强度（Reasoning effort）**：固定 `GPT-5.6 Sol` 与 Codex，Low/Medium/High/XHigh/Max 五档在 2 小时通过率为 **8.0% / 20.0% / 34.0% / 66.0% / 72.0%**，且时间延长的红利高度依赖高推理档位——2 小时后仅 Max 与 XHigh 继续增长 +10.0 和 +6.0 个百分点（6 小时达 82.0% 与 72.0%），而 High/Medium/Low 在 2 小时后增幅全为 **0.0 个百分点**，Low 档所有失败运行在首个 1 小时内就停止了电路修改（物理页 7–8，Section 5.1 与 Fig. 4b）[pdf:E07] [pdf:E08]；③ **Agent 框架（Harness）**：固定 `GPT-5.6 Sol [max]` 对比 Pi、Kimi Code、Codex、MCode、OpenCode 五种框架，2 小时差距达 16 个百分点（56.0%–72.0%），但到 6 小时迅速收敛至 **80.0%–86.0%**（最大仅差 3 道题），远小于跨基座模型 54 个百分点的鸿沟（物理页 7–8，Section 5.1 与 Fig. 4c）[pdf:E07] [pdf:E08]；④ **通用与任务总结型 Skill 文档（Skills 1–7）**：无论是前 30 题轨迹提炼并在后 20 题测试的通用手册/工作流/故障决策树（Skills 1–3，6 小时仅比无 skill 的 46.7% 变动 **0.0 至 +3.3 个百分点**），还是全集轨迹提炼文档（Skills 4–6，6 小时为 53.3%/54.0%/62.0% 对比基线 59.3%，即 **−6.0 至 +2.7 个百分点**）与 14,490 词任务话题知识库（Skill 7，6 小时 60.0% 对比 59.3%，仅净增 1/150 次通过，11 题变好但 12 题变差），终局边际贡献均微弱甚至为负（物理页 7–8 与页 22–23，Section 5.2、Fig. 4d–e 与 Appendix F）[pdf:E07] [pdf:E08] [pdf:E19]；⑤ **参考拓扑检索（Skill 8，精确任务拓扑蓝图 + `<TUNE>` 占位符）**：边际增益最大但呈显著的模型能力分化——对中等模型 `DeepSeek V4 Pro [max]`，2 小时暴涨 **+30.0 个百分点**（42.0% $\to$ 72.0%），6 小时仍净增 **+18.7 个百分点**（59.3% $\to$ 78.0%，多过 28/150 次），直接抹平了拓扑搜索短板；对强模型 `GPT-5.6 Sol [max]`，2 小时提升 **+10.0 个百分点**（68.0% $\to$ 78.0%），但 6 小时仅微增 **+0.7 个百分点**（82.0% $\to$ 82.7%），主要起到了加速收敛的作用（物理页 7–8 与页 23，Section 5.2、Fig. 4f 与 Appendix F）[pdf:E07] [pdf:E08] [pdf:E19]。

### 完整端到端 Pipeline 与真实电路实例追踪

以论文重点剖析的 **Task No. 33（全差分 1 倍增益采样反馈电容耦合 OTA，Slot 33，370 项条件级检查）** 与首页展示的同架构高增益任务 **Task No. 34（全差分 8 倍增益采样反馈 OTA，Slot 34，399 项条件级检查）** 为具体实例，整个基准与智能体交互流水线分为四个严密解耦的阶段（物理页 1、页 4、页 9 与页 17，Fig. 1、Fig. 2、Section 6 与 Table A1）[pdf:E01] [pdf:E04] [pdf:E09] [pdf:E14]：

- **输入表示与任务契约（Task Package Input）**：每个任务包向 Agent 沙盒注入标准化的文本与网表文件集，包含完全公开的量化电气规格合同（如在 130-nm SKY130 CMOS 下满足相位裕度 $\ge 60^\circ$、输出积分噪声 $\le 300\,\mu\text{Vrms}$ 或 $\le 1\,\text{mVrms}$、输出差分摆幅 $\ge 1.8\,\text{V}$、建立时间 $\le 40\,\text{ns}$ 或 $\le 10\,\text{ns}$、静态误差 $\le 0.01\%$ 或 $\le 0.1\%$、动态误差 $\le 0.1\%$、功耗 $\le 5\,\text{mW}$ 或 $\le 10\,\text{mW}$、CMRR $\ge 60\,\text{dB}$、PSRR $\ge 70\,\text{dB}$、共模恢复残差限制，以及 30 个 PVT 角点与 20 个失配样本要求）、固定的顶层子电路端口定义（如 `.subckt dut VDD VSS VIP VIN VON VOP`）、初始模板文件、网表原语规范以及仅作语法示范的示例 testbench（物理页 1、页 3–4 与页 9–10，Fig. 1、Section 3.2 与 Fig. 5）[pdf:E01] [pdf:E03] [pdf:E04] [pdf:E09]。
- **Agent 沙盒内的离散—连续混合迭代（LLM Reasoning vs. SPICE Numerical Solver）**：在这里职责边界极其清晰——**LLM 智能体（运行在 Codex 或 Claude Code 等命令行 harness 中）**承担离散架构决策、物理因果归因与实验调度：它决定采用两级 Miller、折叠共源共栅（folded-cascode）还是增益自举拓扑，决定共模反馈（CMFB）支路连接方式，编写 `.subckt` 晶体管网表（设置 `sky130_fd_pr__nfet_01v8` / `pfet_01v8` 的 $L, W, nf, m$ 及无源电容电阻），并**自主编写**覆盖 `.op`、`.dc`、`.ac`、`.noise`、`.tran` 及多角点扫描的诊断 testbench 脚本（物理页 1、页 4 与页 9，Fig. 1、Section 3.2 与 Section 6）[pdf:E01] [pdf:E04] [pdf:E09]。**开源电路仿真器 `ngspice`** 则纯粹作为确定性物理先知（numerical DAE/MNA solver），求解紧凑器件模型（BSIM4/SKY130 模型卡）的非线性节点基尔霍夫方程组，输出工作点电流电压、频域波特图、积分噪声与瞬态建立波形（物理页 3–4，Section 3.2）[pdf:E03] [pdf:E04]。
- **闭环反馈信号与自主终止**：Agent 解析 `ngspice` 输出日志中的测量标量或报错信息（如矩阵奇异不收敛、某角点相位裕度不足），定位当前活跃瓶颈（active bottleneck），修改拓扑或器件尺寸后重跑仿真。例如在 Fig. 1 的 Task 34 真实轨迹中，`GPT-5.6 Sol [max]` 在 31.6 分钟仅过 1/8 项代表指标，80.2 分钟推进到 5/8 项，142.9 分钟达 6/8 项，直至 197.4 分钟首次实现 8/8 项（全部 15 个评分门）全通（物理页 1，Fig. 1）[pdf:E01]。运行在 Agent 主动声明完成或触及未公开的挂钟时限（主实验 2 小时、扩展实验 6 小时）时终止（物理页 4–5 与页 7，Section 3.2、Section 4 与 Section 5）[pdf:E04] [pdf:E05] [pdf:E07]。
- **隔离沙盒合法性门禁与全工况门控裁决（Isolated Verifier）**：最终提交的单一电路网表传入网络隔离的 Verifier 容器，先通过语法、端口、器件白名单与禁令审查，随后在锁定的 `ngspice` 与保护版 SKY130 PDK 上运行隐藏的全套名义工况与鲁棒性（PVT + 固定种子失配）测试台，输出二值 Pass/Fail 裁决与细粒度 `SpecScore`（物理页 4 与页 18–20，Fig. 2c、Section 3.3 与 Appendix C）[pdf:E04] [pdf:E15] [pdf:E16] [pdf:E17]。

## § 6 — 核心数学推导（无形式化数学则跳过）

作为面向工具驱动智能体的执行评测基准，本文不涉及神经网络训练损失或新数值求解算法的推导，但为解决模拟电路多物理量异构、多工况组合爆炸以及仿真不收敛引发的评测歧义，作者在正文 § 3.3、§ 4 及附录 C、G 中建立了一套严密的**规格门展开、覆盖—可靠性分解与方向对齐裕度（normalized margin）形式化体系**（物理页 4–5、页 18–19 与页 25，Section 3.3、Section 4、Appendix C 与 Appendix G）[pdf:E04] [pdf:E05] [pdf:E15] [pdf:E16] [pdf:E21]。

### 1. 条件级验收检查展开（Condition-Level Check Expansion）与二值合取判据

设任务 $t$ 的公开规格合同包含 $G_t$ 个具名评分门（scoring gates），每个评分门 $g \in \{1, \dots, G_t\}$ 对应一类电气指标（如 INL、相位裕度或建立时间），并在一组规定的离散工作条件集合 $\mathcal{C}_{t,g}$（涵盖工艺角、电源电压、温度、负载、通道、数字码字位置、固定种子失配样本、频率、极性与跳变方向）上进行测试（物理页 4 与页 18，Section 3.3 与 Appendix C）[pdf:E04] [pdf:E15]。同一标量上的上下界区间约束 $[s_{\min}, s_{\max}]$ 计为单次区间检查，排除原始瞬态波形采样点、连续扫描离散点与 FFT 频点后，任务 $t$ 的总条件级验收检查数为 $N_t = \sum_{g=1}^{G_t} |\mathcal{C}_{t,g}| \in [11, 2083]$（物理页 4 与页 18，Section 3.3 与 Appendix C）[pdf:E04] [pdf:E15]。

附录 C 给出了全基准最复杂任务 **Slot 23（5-bit 开关电阻型 DAC）** 的精确计数展开式（物理页 18–19，Appendix C）[pdf:E15] [pdf:E16]：

$$N_{23} = (11 + 8)(32 + 31 + 31) + 11(2 + 1 + 6 \times 3 + 6) = 19 \times 94 + 11 \times 27 = 1786 + 297 = 2,083$$

其中每一项都有明确的电路测试物理含义：$11$ 代表 11 个离散 PVT 角点，$8$ 代表 8 个固定种子的器件失配（Monte Carlo）样本，在这 $11+8=19$ 种环境/统计扰动下，逐一核查 $2^5 = 32$ 个数字输入码字的积分非线性（INL）、$31$ 个相邻码字台阶的微分非线性（DNL）以及 $31$ 次相邻码字转换的单调性（合计 $32+31+31=94$ 项静态转换检查）；第二项则是在 $11$ 个 PVT 角点下，分别测量零码与满量程 $2$ 项端点误差、$1$ 项静态/工作功耗、$6$ 组定向主进位跳变（major-carry transitions，如 `01111` $\leftrightarrow$ `10000`）各自的 $3$ 项动态毛刺/建立指标（$6 \times 3 = 18$ 项），以及 $6$ 个代表性码字处的输出阻抗（合计 $2+1+18+6=27$ 项）（物理页 18–19，Appendix C）[pdf:E15] [pdf:E16]。

设合法性检查指示函数为 $L(x) \in \{0, 1\}$，评分门 $g$ 在条件 $c \in \mathcal{C}_{t,g}$ 下的仿真收敛且测量值落入合格域的指示函数为 $p_{t,g,c}(x) \in \{0, 1\}$（若仿真未收敛、超时或缺失测量值，则严格令 $p_{t,g,c}(x) = 0$，绝不将空值放行）（物理页 19，Appendix C）[pdf:E16]。评分门 $g$ 通过当且仅当 $P_{t,g}(x) = \prod_{c \in \mathcal{C}_{t,g}} p_{t,g,c}(x) = 1$；整次提交通过当且仅当满足严格的逻辑合取（物理页 4 与页 19，Section 3.3 与 Appendix C）[pdf:E04] [pdf:E16]：

$$\text{Pass}_t(x) = L(x) \cdot \prod_{g=1}^{G_t} P_{t,g}(x)$$

同时，为刻画局部进展而不掩盖致命短板，定义单次尝试的门奖励（gate reward）为 $R_t(x) = \sum_{g=1}^{G_t} w_{t,g} P_{t,g}(x)$（其中 $\sum_g w_{t,g} = 1$，未声明任务特定权重时取等权 $w_{t,g} = 1/G_t$），跨 50 个任务与 3 次独立重跑（rollouts）取等权均值即得 `SpecScore`（物理页 4–5，Section 3.3 与 Section 4）[pdf:E04] [pdf:E05]。这种“门内全工况一票否决 + 门间加权诊断 + 整题全门合取”的设计，精准防止了常见评测病态：Agent 无法靠牺牲某一个低温慢速角点的稳定性去刷高平均分来骗取 Pass，而研究者仍能从 `SpecScore` 与 `pass@1` 的落差中读出“接近收敛但卡在少数刚性指标”的程度。

### 2. 覆盖率与可靠性的统计解耦（Pass@1 vs. Pass@3）

对每个配置在每个任务 $t \in \{1, \dots, 50\}$ 上独立执行的 $K=3$ 次尝试 $\{x_{t,1}, x_{t,2}, x_{t,3}\}$，主指标 `pass@1` 度量单次期望成功率，而经验 `pass@3` 度量至少一次成功的任务覆盖率（物理页 5，Section 4）[pdf:E05]：

$$\text{pass@1} = \frac{1}{50 \times 3} \sum_{t=1}^{50} \sum_{k=1}^{3} \text{Pass}_t(x_{t,k}), \qquad \text{pass@3} = \frac{1}{50} \sum_{t=1}^{50} \mathbb{I}\!\left(\sum_{k=1}^{3} \text{Pass}_t(x_{t,k}) \ge 1\right)$$

这一组配对指标直接暴露了长程随机搜索中的高方差现象：例如 `GPT-5.6 Sol [max]` 的 `pass@3` 高达 96.00%（48/50 题至少解出一次），高于 `Claude Fable 5 [max]` 的 90.00%（45/50 题），但三轮全过的稳定题数仅 18 题（远低于 Fable 的 32 题），致使其 `pass@1`（68.00%）落后 Fable（78.00%）整整 10 个百分点（物理页 5，Section 4 与 Table 2）[pdf:E05]。

### 3. 异构物理量的方向对齐规格裕度变换（Direction-Aligned Normalized Margin）

在 § 6 与附录 G 的长程轨迹诊断中，同一电路的功耗（mW）、误差（%）、建立时间（ns）、噪声（$\mu\text{Vrms}$）与抑制比（dB）跨多个数量级且优劣方向相反。作者在附录 G（第 25 页）定义了无量纲化的方向对齐比值 $r(x, s)$（其中 $x$ 为实测最坏角点值，$s$ 为规格门限）（物理页 24–25，Appendix G）[pdf:E20] [pdf:E21]：

$$r(x, s) = \begin{cases} x / s, & \text{对于线性下界约束 } x \ge s \text{（如摆幅、相位裕度）} \\ s / x, & \text{对于线性上界约束 } x \le s \text{（如功耗、噪声、建立时间）} \\ 10^{(x - s)/20}, & \text{对于分贝下界约束 } x \ge s\text{ dB（如 CMRR、PSRR、SNDR）} \end{cases}$$

该变换具备三个精巧的工程性质：① **统一合格判据**：无论原指标量纲与不等号方向如何，$r \ge 1$ 严格等价于该项指标达标；② **分贝域到线性幅值比的物理对齐**：对 dB 指标采用 $10^{(x-s)/20}$ 而非直接做分贝相除 $x/s$，不仅消除了 $s \le 0\,\text{dB}$ 时的除零奇点，而且将分贝裕度统一还原为电压/电流幅值比，与线性指标的物理尺度同构；③ **前置功能门控（Dependency Gating）与双尺度压缩**：在纵轴 $[0, 1]$ 区间采用线性刻度放大临近收敛区的微调轨迹，在 $(1, \infty)$ 采用对数刻度并截断于上限（OTA 为 50、Flash ADC 为 20）防止充裕指标淹没瓶颈指标；同时若前置基础功能门（如直流工作点或 Flash ADC 的 16 码传输特性）失效，所有下游依赖指标强制标为 `Gated` 而非计算出虚假的低功耗或低噪声高分，彻底杜绝了“死电路得高分”的数值假象（物理页 9 与页 24–25，Fig. 5 与 Appendix G）[pdf:E09] [pdf:E20] [pdf:E21]。

## § 7 — 实验设计与结论

本文围绕三个递进的核心实证问题展开系统评测：**（Q1）当前前沿通用代码 Agent 在长程模拟电路前端设计上的真实水位如何，代码能力在多大程度上能外推模拟设计能力？（Q2）失败提交究竟卡在网表语法合法性，还是卡在多物理指标的电气闭合？（Q3）延长搜索时间、提高推理预算、更换 Agent 框架以及注入不同颗粒度的电路知识（从通用文本指南到精确参考拓扑）各自能带来多少真实增益？**（物理页 2、页 5–7，Section 1、Section 4 与 Section 5）[pdf:E02] [pdf:E05] [pdf:E06] [pdf:E07]。

### 1. 基准规模、参评矩阵与评测指标

- **任务规模与电路维度覆盖**：共 **50 个晶体管级设计任务**，由 17 位芯片专家从 100+ 提案中经多轮审查与试跑筛选构建，分布于 6 大功能族（电源管理与基准 11、通用运放与 OTA 9、信号链放大器与有源滤波器 9、数据转换与采样 9、射频/定时/高速 9、接口与驱动 3）（物理页 3 与页 16–18，Section 3.1、Table A1 与 Table A2）[pdf:E03] [pdf:E13] [pdf:E14] [pdf:E15]。按评测的物理维度统计，50 题中有 44 题测功耗/效率、33 题测 PVT 角点、26 题测增益/带宽、25 题测瞬态建立/启动、16 题测稳定性/相位裕度、16 题测线性度/频谱、14 题测噪声、12 题测电源/共模抑制比、8 题测 Monte Carlo 失配；单题条件级检查数从 11 项（Slot 14 低功耗振荡器）跨越至 2,083 项（Slot 23 5-bit 开关电阻 DAC）（物理页 16–19，Fig. A1b、Table A1 与 Appendix C）[pdf:E13] [pdf:E14] [pdf:E16]。题目没有人为划分主观难度档位，而是通过 15 种配置的实际解出数形成客观难度谱系：全基准没有任何一题全军覆没或完全饱和，单题通过率跨度为 4.4%–88.9%，最少由 2 个配置解出（如 Slot 25 轨到轨 Class-AB 运放、Slot 28 浮空电荷转移余量放大器、Slot 34 8 倍增益采样反馈 OTA、Slot 42 6-bit 100 MS/s 异步 SAR ADC），最多由全部 15 个配置解出（Slot 1 半桥 Class-D 功放、Slot 2 可编程电流镜、Slot 45 500 MHz 二分频触发器）（物理页 5、页 16–18 与页 22，Section 4、Table A1 与 Fig. A4）[pdf:E05] [pdf:E13] [pdf:E14] [pdf:E15]。
- **参评模型与基线矩阵**：共评测 **15 种 Agent 配置**（模型 $\times$ 最高可用推理档位 $\times$ 框架），涵盖 Anthropic（`Claude Fable 5 [max]`、`Claude Opus 5 [max]`）、OpenAI（`GPT-5.6 Sol [max]`、`GPT-5.5 [xhigh]`、`GPT-5.6 Terra [max]`、`GPT-5.6 Luna [max]`）、Moonshot（`Kimi K3 [max]`）、DeepSeek（`DeepSeek V4 Pro [max]`、`DeepSeek V4 Flash [max]`）、智谱（`GLM-5.3 [max]`、`GLM-5.3 Flash [max]`、`GLM-5.2 [max]`）、阿里（`Qwen 3.8 Max [xhigh]`）、字节跳动（`Doubao Seed 2.1 Pro [high]`）与小米（`MiMo 2.5 Pro [thinking]`），其中 4 个 GPT 配置运行于原生 Codex（v0.144.1），其余 11 个运行于 Claude Code（v2.1.220），单次尝试成本跨越两个数量级以上（从 `DeepSeek V4 Flash` 的 \$0.12 到 `Claude Fable 5` 的 \$31.56）（物理页 5 与页 19，Section 4、Table 2 与 Table A3）[pdf:E05] [pdf:E16]。主实验每配置每题跑 3 次独立 rollout（两小时预算），总计 **$50 \times 15 \times 3 = 2,250$ 次**运行；第 5 节扩展实验将时间拉长至 6 小时，额外涵盖 5 档推理强度、5 种 Agent 框架（Codex、Kimi Code、MCode、OpenCode、Pi）与 8 套设计知识包（Skills 1–8）（物理页 5、页 7–8 与页 19–23，Section 4、Section 5、Table A3 与 Table A4）[pdf:E05] [pdf:E07] [pdf:E08] [pdf:E16] [pdf:E19]。
- **核心评测指标**：主指标为全规格通过率 `pass@1`，辅以三轮覆盖率 `pass@3`、逐轮通过率 `R1/R2/R3`、局部评分门进度均值 `SpecScore`、合法性拒绝率 vs. 电气未达标率，以及单次尝试成本、模型请求轮数、工具调用数、工具等待时间（覆盖 232,743 次工具调用中 99.2% 的边界）、SHA-256 去重候选电路数（共恢复 44,695 个）与运行总时长（物理页 5–6 与页 20–21，Section 4、Table 2、Fig. 3 与 Appendix D）[pdf:E05] [pdf:E06] [pdf:E17] [pdf:E18]。

### 2. 核心定量结论与消融发现

- **主实验梯队分化与覆盖—稳定性背离（回答 Q1）**：两小时 `pass@1` 从最低 8.00%（`MiMo 2.5 Pro` 与 `GLM-5.2`，均为 12/150）跨越至最高 **78.00%**（`Claude Fable 5 [max]`，117/150，`SpecScore` 89.26%），紧随其后的是 `Claude Opus 5 [max]`（69.33%，`SpecScore` 86.62%）、`GPT-5.6 Sol [max]`（68.00%，`SpecScore` 77.02%）与 `GPT-5.5 [xhigh]`（60.67%，`SpecScore` 73.02%）；其余 11 个配置全部低于 50%，开源/开放权重阵营最高为 `Kimi K3 [max]`（49.33%）与极具性价比的 `DeepSeek V4 Pro [max]`（42.00%，单次成本仅 \$0.37）（物理页 2 与页 5，Section 1 与 Table 2）[pdf:E02] [pdf:E05]。在覆盖率与稳定性上，`GPT-5.6 Sol [max]` 以 **96.00%** 的 `pass@3`（48/50 题）夺冠，但三轮全过的稳定题仅 18 题，而 `Claude Fable 5 [max]` 虽 `pass@3` 为 90.00%（45/50 题），却在 32 题上实现三轮全过，且平均仅需 **37 轮**交互（对比 `GPT-5.6 Sol` 的 148 轮与 `GPT-5.6 Luna` 的 216 轮）（物理页 5，Section 4 与 Table 2）[pdf:E05]。与 `DeepSWE` 对比，13 个有榜模型的秩相关为 Spearman $\rho = 0.88$（$p = 6.5 \times 10^{-5}$），但代码分在 67%–70% 聚拢的 6 个模型在模拟基准上拉开了 31%–78% 的 47 个百分点差距（物理页 6，Section 4 与 Fig. 3b）[pdf:E06]。
- **语法并非瓶颈，电气闭合统治终局失败（回答 Q2）**：2,250 次提交中仅 **24 次（1.1%）**因网表不合法被拒；1,388 次未通过提交中有 **1,364 次（98.3%）**合法无误却未能闭合全部电气门限（物理页 6，Section 4 与 Fig. 3a）[pdf:E06]。资源统计进一步印证“苦劳不等于功劳”：`pass@1` 与迭代轮数（$\rho = +0.10$）、工具调用数（$\rho = +0.08$）、候选电路数（$\rho = +0.12$）几乎无关，与输出 token 数呈弱负相关（$\rho = -0.28$，`GLM-5.3 Flash` 输出 382k tokens 约为榜首 108k 的 3.5 倍，`pass@1` 却仅 18.67%），而与工具等待时间强正相关（$\rho = +0.81$，反映强模型运行了更重、更全面的多工况仿真测试）、与平均任务时长强负相关（$\rho = -0.91$，通过运行中位耗时 72.0 分钟，失败运行中位耗时 118.9 分钟）（物理页 5 与页 20–21，Section 4、Table 2 与 Appendix D）[pdf:E05] [pdf:E17] [pdf:E18]。
- **测试时扩展与知识注入消融结论（回答 Q3）**：① 时间从 2 小时扩至 6 小时使 5 种配置普涨 **14.0–20.0 个百分点**（物理页 7–8，Fig. 4a）[pdf:E07] [pdf:E08]；② 推理强度决定天花板与时间利用率，`GPT-5.6 Sol` 在 Max/XHigh 下 2 小时后仍涨 +10.0/+6.0 个百分点至 82.0%/72.0%，而 High（34.0%）、Medium（20.0%）、Low（8.0%）在 2 小时后完全停滞（物理页 7–8，Fig. 4b）[pdf:E07] [pdf:E08]；③ 5 种 Agent 框架在 6 小时收敛到 80.0%–86.0%（Pi 与 Kimi Code 并列 86.0%，OpenCode 80.0%），框架差异随时间被抹平（物理页 7–8，Fig. 4c）[pdf:E07] [pdf:E08]；④ 通用或轨迹总结文本技能（Skills 1–7，词数从 668 到 14,490 词）在 6 小时对 `DeepSeek V4 Pro` 的影响仅在 **−6.0 至 +3.3 个百分点**之间波动，部分冗长文档（如 5,716 词的 Skill 4）在 2 小时反而拖累基线 12.0 个百分点（30.0% vs. 42.0%）（物理页 7–8 与页 23，Fig. 4d–e 与 Table A4）[pdf:E07] [pdf:E08] [pdf:E19]；⑤ 唯独提供挖空数值尺寸（替换为 `<TUNE>`）的任务匹配参考拓扑（Skill 8）令 `DeepSeek V4 Pro` 从 42.0%/59.3%（2h/6h）跃升至 **72.0%/78.0%**，追平无提示的前沿闭源模型，同时将 `GPT-5.6 Sol` 的 2 小时通过率推高 10.0 个百分点至 78.0%（6 小时为 82.7%），清晰证实中等模型的核心短板在于拓扑选择与网表搭建，而即使给定完美拓扑，非线性跨工况尺寸闭合依然留下了约 17%–22% 的硬骨头（物理页 7–8 与页 23，Section 5.2、Fig. 4f 与 Appendix F）[pdf:E07] [pdf:E08] [pdf:E19]。

## § 8 — Take-aways

- **5 句话版**：
  1. Analog Design Bench 构建了首个融合 17 位芯片专家原创的 50 个晶体管级任务、开源 SKY130 + ngspice 长程自主仿真闭环与双沙盒物理隔离规格验收器的模拟/混合信号电路设计基准（物理页 1–4，Abstract、Section 3 与 Fig. 2）[pdf:E01] [pdf:E03] [pdf:E04]。
  2. 在 15 种 Agent 配置、2,250 次两小时评测中，全指标通过率从 8.0% 跨越至 78.0%（`Claude Fable 5 [max]` 领跑），且相近的代码基准得分（DeepSWE 67%–70%）对应高达 31%–78% 的模拟设计差距，证明通用代码能力远不足以表征模拟物理设计能力（物理页 5–6，Table 2 与 Fig. 3b）[pdf:E05] [pdf:E06]。
  3. 高达 98.3% 的未通过提交均无 SPICE 语法或原语合法性违规，而是倒在单题 11 至 2,083 项耦合 PVT/失配门限的电气性能闭合（electrical closure），同时隐藏裁判机制暴露了中间达标后被自行改坏的退化现象（物理页 4、页 6 与页 20，Section 3.3、Fig. 3a 与 Appendix C）[pdf:E04] [pdf:E06] [pdf:E17]。
  4. 延长预算至 6 小时与拉满推理强度（Max/XHigh）能持续带来 14–20 个百分点的显著收益，而不同 Agent 框架（harness）在 6 小时收敛至仅差 6 个百分点以内，盲目堆砌交互轮数或输出 token 则与成功率无正相关性（物理页 5 与页 7–8，Section 4、Section 5.1 与 Fig. 4a–c）[pdf:E05] [pdf:E07] [pdf:E08]。
  5. 通用工作流与文字电路指南（Skills 1–7）几乎不提升终局通过率甚至产生干扰，唯有注入挖空尺寸的任务级参考拓扑（Skill 8）能为中等模型带来 +18.7 个百分点的六小时净跃升，指明了“真实电路 IP 检索改造 + 鲁棒多角点工作点闭合”的核心演进路线（物理页 7–10，Section 5.2、Fig. 4d–f 与 Section 7）[pdf:E07] [pdf:E08] [pdf:E10]。

- **3 句话版**：
  1. 本文推出包含 50 个专家级 SKY130 晶体管设计任务与隔离多工况验收器的 Analog Design Bench，在 2,250 次长程运行中测得主流 Agent 全指标通过率介于 8.0%–78.0%，且代码榜单高分模型在模拟电路上出现剧烈分化（物理页 1 与页 5–6，Abstract、Table 2 与 Fig. 3b）[pdf:E01] [pdf:E05] [pdf:E06]。
  2. 98.3% 的失败源于跨工况非线性电气指标闭合而非网表语法错误，高推理强度配合 6 小时搜索可显著推高上限，而 Agent 外层框架与通用文字经验文档的终局影响均十分有限（物理页 6–8，Fig. 3a 与 Fig. 4）[pdf:E06] [pdf:E07] [pdf:E08]。
  3. 提供无数值尺寸的精确参考拓扑能让 `DeepSeek V4 Pro` 在 6 小时暴涨 18.7 个百分点并加速强模型收敛，揭示出拓扑级电路 IP 检索与自洽多角点回归验证是攻克模拟设计智能体的两大关键支点（物理页 7–10，Section 5.2 与 Section 7）[pdf:E07] [pdf:E10]。

- **1 句话版**：
  Analog Design Bench 通过 50 个隔离验证的多工况晶体管级长程任务证明，当前前沿 Agent 在模拟 IC 设计上的真正瓶颈并非 SPICE 语法或外层框架，而是拓扑选择与强耦合非线性电气闭合——拉高推理深度与检索结构化电路拓扑远比注入通用文字经验有效（物理页 1、页 6–8，Abstract、Fig. 3 与 Fig. 4）[pdf:E01] [pdf:E06] [pdf:E07] [pdf:E08]。

## § 9 — 最脆弱的假设

本文全部排行榜结论与能力外推所依赖的**唯一最脆弱、失败代价最大的核心假设**是：**在不施加版图连线寄生（post-layout RC parasitics）与物理面积/器件并联规模上限的前仿原理图级（schematic-only）环境中，通过理想化无源元件许可与紧凑模型实现的“电气指标闭合”，能够保序且真实地表征智能体在工程级模拟/混合信号芯片前端设计中的有效能力**。

论文为支撑这一简化边界给出的正面依据是：原理图级拓扑选择、器件尺寸调优与仿真闭合构成了模拟前端工程师的核心日常工作，而版图物理实现属于下游独立阶段（物理页 4，Section 3.2）[pdf:E04]。然而，作者在正文的局限性声明、伦理影响声明与附录 C 中同时坦承了三处被刻意豁免的物理约束：① 全基准 50 题中有 35 题允许使用无寄生的理想无源电阻、电容甚至理想电感与耦合系数（22 题允许理想 R+C，7 题理想 C，3 题理想 R，2 题理想 R+C+L，1 题理想 R+C+L+K）（物理页 19，Appendix C）[pdf:E16]；② 除个别题目显式要求外，验收器**不考核芯片面积、无源器件物理尺寸与晶体管并联倍数（multiplicity $m$）的工程可制造性**（物理页 10 与页 19，Broader Impact 与 Appendix C）[pdf:E10] [pdf:E16]；③ 缺失连线电容电阻与版图扩散区寄生的反馈（物理页 10，Section 7 Limitations）[pdf:E10]。

从模拟集成电路物理来看，这一假设一旦放回真实流片场景极易崩塌，并直接动摇模型的分数与排序。在纯前仿网表中，热噪声谱密度满足 $\overline{v_n^2} \propto kT / g_m$，阈值失配标准差满足 Pelgrom 定律 $\sigma(\Delta V_{TH}) = A_{VT} / \sqrt{m W L}$，而连线寄生电容为严格的零。只要功耗预算尚有余量（或对栅极静态偏置管、开关电容采样开关、电阻阵列做尺寸放大），Agent 完全可以通过把晶体管并联倍数 $m$ 放大数百倍、或填入数十皮法的理想补偿电容与毫欧级理想电阻，在“零走线分布电容代价”下无成本地压低闪烁/热噪声、抹平 Monte Carlo 失配（如 Slot 23 开关电阻 DAC 的 0.25 LSB DNL/INL 或 Slot 33/34 的低噪声采样 OTA），而无需支付真实硅片上金属走线寄生电容 $C_{\text{wire}}$ 拖垮次极点 $\omega_{p2} \approx g_{m2}/(C_{\text{par}} + C_{\text{wire}})$ 的物理惩罚！正文中 `GPT-5.6 Luna [max]` 在 Task 33 上将输出管设到 $m=10,000$ 直至撑爆紧凑模型有效域才触发报错（物理页 9，Section 6）[pdf:E09]，恰好冰山一角地暴露了 Agent 在无面积约束下沿着极端尺寸方向投机搜索的本能：对于未撑爆 BSIM 边界的 $m=200 \sim 1,000$ 级“病态巨型管”设计，在高速电路（如 Slot 9 的 10 GHz CML 分频器、Slot 32 的 28 Gb/s NRZ 驱动器、Slot 43/49 的 2.4 GHz LNA 与 LC VCO）（物理页 16–18，Table A1）[pdf:E13] [pdf:E14] [pdf:E15] 中当前验证器会判为满分 Pass，但一旦折算真实金属层走线 $RC$ 与焊盘/阱寄生，高频极点与自谐振频率将瞬间坍塌。因此，现有高分通过率中有未知比例可能建立在物理上不可布线、面积荒谬的前仿退化解之上，论文完全缺失了对通过网表中总栅极面积 $\sum m W L$、总无源电容/电阻量级与估算寄生退化率的审计证据。

## § 10 — 最小复现实验

无需重跑耗资高昂的 2,250 次两小时评测，在 1 周内即可利用作者公开的归档轨迹、最终提交网表与开源 Verifier 容器（物理页 10，Reproducibility Statement）[pdf:E10]，完成针对上述核心假设的**“物理可实现性与一阶寄生注入审计”最小证伪实验**：

1. **实验数据与电路子集**：直接抽取归档快照中全部 15 个配置已获判 Pass 的提交网表，并重点深挖 6 道跨电路族代表题——噪声/失配敏感型（Slot 33 1 倍采样反馈 OTA、Slot 23 5-bit 开关电阻 DAC）、高频寄生敏感型（Slot 9 1–10 GHz CML 二分频器、Slot 32 28 Gb/s CML 驱动器、Slot 43 2.4 GHz 电感源极退化 LNA）以及多级稳定性敏感型（Slot 37 三级嵌套 Miller 运放）（物理页 16–18，Table A1）[pdf:E13] [pdf:E14] [pdf:E15]。
2. **最小实现模块（约 250 行 Python 网表变换器 + 原 Verifier 镜像）**：不改动任何 Agent 运行代码，仅在进入隔离 `ngspice` 验收器前插入一个两阶段物理审查算子：
   - **Stage A（硅片物理尺度审计）**：静态解析提交 `.subckt` 中所有晶体管实例与无源器件，统计总有效有源区栅面积 $A_{\text{active}} = \sum_i m_i \cdot nf_i \cdot W_i \cdot L_i$、最大单管并联倍数 $m_{\max}$、总电容 $\sum C_j$ 与总电阻 $\sum R_k$，以专家参考解（reference results，每题均已随库检入，物理页 3 与页 19）[pdf:E03] [pdf:E16] 的对应物理规模为基准，设定宽松工程上限（如 $A_{\text{active}} \le 10 \times A_{\text{ref}}$、单管 $m_{\max} \le 256$、片上总电容 $\le 100\,\text{pF}$）。
   - **Stage B（一阶节点连线寄生回注）**：对所有非电源内部信号节点 $v$，按连接至该节点的器件栅/漏周长总和自动并联一阶估算走线对地电容 $C_{\text{wire}, v} = c_0 \cdot \text{fanout}(v) + c_1 \sqrt{\sum_{i \in \mathcal{N}(v)} m_i W_i L_i}$（取 SKY130 典型局部互连经验系数 $c_0 = 2\,\text{fF}$，$c_1 = 0.5\,\text{fF}/\mu\text{m}$），并将理想电容/电感替换为带有限品质因数 $Q=30$ 等效串联电阻的模型后，在原冻结 Verifier 容器中重放全部评分门。
3. **观测指标与证伪判据**：统计各模型原通过网表的“面积超限淘汰率”、“寄生回注后生存率（Post-Parasitic Survival Rate）”以及 15 个配置的二次排名 Spearman $\rho'$。
   - **支持原论文核心结论**：若主流高分配置（如 `Claude Fable 5`、`GPT-5.6 Sol`）80% 以上的原 Pass 网表同时满足面积上限且在寄生回注后保持 $\ge 70\%$ 通过率，且跨模型排名相关性 $\rho' \ge 0.90$，则证实前仿无约束闭合确为稳健的能力代理。
   - **推翻/重创原论文假设**：若超过 35% 的原 Pass 网表存在 $A_{\text{active}} > 10 A_{\text{ref}}$ 或百皮法级理想电容堆砌，或在注入飞法级（fF）一阶连线电容后高频与多级运放任务的通过率腰斩（下降 $> 40\%$）甚至引发模型排位显著洗牌（某些“保守尺寸”模型反超“暴力扩尺寸”模型），则直接证明无寄生/无面积约束的前仿验收纵容了非物理退化解。

## § 11 — 最强反例设计

站在挑剔审稿人的反方视角，可以对本文提出一记兼具**具体病态电路反例**与**实验混杂因素剥离（confounder critique）**的强力攻击：**本文声称的“98.3% 失败源于模拟电气闭合能力不足”，实际上严重混杂了“电路拓扑/尺寸综合能力”与“盲盒验收体制下的 SPICE 测量测试台（testbench）软件工程能力”**。

### 1. 来自论文自身数据的混杂证据

在 Analog Design Bench 的规则下，隐藏 Verifier 在整整 2 至 6 小时内返回**零反馈**，Agent 沙盒里提供的仅是“语法参考示例 testbench”，Agent 必须自己用 `ngspice` 控制脚本写出覆盖多达数十个 PVT 角点、失配种子与复杂交直流转换测量的自检测试台（物理页 3–4 与页 9，Section 3.2–3.3 与 Section 6）[pdf:E03] [pdf:E04] [pdf:E09]。注意论文中三组耐人寻味的事实：① 附录 C（第 20 页）披露，在 990 次经身份审计的 6 小时运行中，有 **15 次运行（涉及 12 个任务）在中间时刻其实已经设计出了 100% 满足隐藏 Verifier 全部苛刻门限的完美电路**，随后却亲手把它改坏提交了失败版本（如 `GPT-5.6 Sol` 在 Task 33 与 Task 27 上的表现）（物理页 9、页 20 与页 24，Section 6、Appendix C 与 Appendix G）[pdf:E09] [pdf:E17] [pdf:E20]——这说明电路设计本身已成功，死因纯粹是 Agent 自建测试台的测量口径与隐藏裁判存在偏差或缺乏回归锁存！② 第 4 节资源分析显示，`pass@1` 与迭代次数、候选电路数几乎无关（$\rho = +0.10, +0.12$），唯独与工具等待时间高达 $\rho = +0.81$ 强正相关（物理页 5 与页 20，Section 4 与 Fig. A2c）[pdf:E05] [pdf:E17]——这恰恰暗示高分模型之所以赢，很大一部分优势可能仅仅在于它作为更强的终端软件工程师，老老实实写出了批量遍历全部 30 个 PVT 角点与 20 个 Monte Carlo 种子的 shell/ngspice 自动化脚本（因此仿真等待长），而低分模型只跑了 TT 标称角点就误以为完工。

### 2. 可确定性击穿该评测范式的病态物理电路场景：多环路共模反馈与双稳态启动陷阱

构造一个组合了本基准已包含组件（Slot 12 自启动 $\beta$-multiplier 偏置 + Slot 50 增益自举折叠共源共栅全差分 OTA 含连续时间 CMFB）（物理页 16 与页 18，Table A1）[pdf:E13] [pdf:E15] 的经典工业级电路场景：高阻全差分增益自举运放配自偏置启动电路与共模反馈环路。该电路存在两个臭名昭著的 SPICE 仿真测量陷阱：
- **直流伪工作点陷阱（Zero-Current / Latch-Up Bistability）**：若自建 testbench 直接运行标准 `.op` 与 `.ac`，SPICE 牛顿—拉夫逊求解器配合 Gmin stepping 往往直接收敛到高增益正常工作的亚稳态解，测得直流增益 $> 130\,\text{dB}$、差模相位裕度 $> 65^\circ$；但隐藏 Verifier 若在低温（$-40^\circ\text{C}$）Slow-NMOS / Fast-PMOS 角点下执行**电源 `VDD` 从 $0\,\text{V}$ 慢速斜坡上电（supply ramp-up `.tran`）**，漏电与阈值电压漂移会使自偏置环路锁死在零电流简并态，或因上电瞬态大信号将尾电流源挤入深线性区而触发 CMFB 正反馈闩锁！
- **差模/共模环路稳定性失察**：绝大多数 Agent 在自建稳定性测试时只对差模通路插大电感大电容测差模环路增益，漏测**共模反馈环路（CMFB loop）在容性负载角点下的独立相位裕度**，导致差模 `.ac` 看似完美（$PM = 70^\circ$），实则在隐藏裁判的非对称共模阶跃瞬态测试中发生百兆赫兹共模高频自激振荡。

在这一完全真实的电路场景下，哪怕给 Agent 直接喂入 100% 达到流片指标的人类专家黄金电路，只要把其中一个启动管宽度微扰 $15\%$，任何不精通 Middlebrook 双注入法与多斜率电源上电瞬态扫描脚本编写的 Agent 都会在自检中看到“全绿裕度 $>20\%$”并自信交卷，然后被隐藏 Verifier 100% 判零分——此时基准测量的已不再是“模拟电路设计能力”，而是“无文档黑盒下的 SPICE 测试工程完备度”。

## § 12 — Follow-up Research Bet

### 主研究押注：基于工作点雅可比敏感度图与 $g_m/I_D$ 流形解耦的神经—符号混合双层收敛架构（Operating-Point Jacobian & $g_m/I_D$ Manifold-Decoupled Agent）

- **论文内的具体实证依据**：本押注直接锚定论文暴露的两组核心定量反常现象。第一，在 § 5.2 与 Fig. 4d–f 中，向 `DeepSeek V4 Pro [max]` 注入多达 14,490 词的自然语言电路设计知识库（Skill 7）或 5,716 词轨迹总结手册（Skill 4），6 小时通过率仅变动 $+0.7$ 与 $-6.0$ 个百分点，而注入挖空尺寸的精确拓扑蓝图（Skill 8，`<TUNE>` 占位符）却使其 2 小时通过率暴涨 $+30.0$ 个百分点、6 小时净涨 $+18.7$ 个百分点至 78.0%，但即便给了完美拓扑，无论是 DeepSeek（78.0%）还是 `GPT-5.6 Sol`（82.7%）依然有约 **17%–22% 的任务无法完成非线性尺寸闭合**（物理页 7–8 与页 23，Section 5.2、Fig. 4d–f 与 Appendix F）[pdf:E07] [pdf:E08] [pdf:E19]。第二，在 § 4、§ 6 与附录 C/D 中，Agent 在网表文本空间直接猜测 $(W, L, m)$ 的候选电路数量与通过率几乎无关（$\rho = +0.12$），且出现了 `GPT-5.6 Luna` 将 $m$ 推至 10,000 撑爆器件模型、以及 990 次审计运行中 15 次“先达标后改坏（pass-then-regress）”的盲目随机游走（物理页 5、页 9 与页 20，Section 4、Section 6 与 Appendix C/D）[pdf:E05] [pdf:E09] [pdf:E17]。
- **改变的基本设计变量（同时改变三项）**：
  1. **状态表示（State Representation）**：废除“原始 SPICE 网表文本 + 终端标量指标打印”的黑盒文本接口，改为**注入小信号工作点与区域标注的带权电路端口图（Operating-Point Annotated Port Graph）**，每个节点/支路显式携带直流偏置裕度 $(V_{DS} - V_{\text{dsat}})$、跨导效率 $g_m/I_D$、本征增益 $g_m r_o$、寄生电容占比 $C_{gs}/C_{\text{node}}$ 以及各评分门指标对支路电学参数的一阶局部敏感度雅可比矩阵 $J_{m,p} = \partial \log M_m / \partial \log p$。
  2. **可控变量空间（Controllable Action Space）**：禁止 LLM 直接在高度非线性的几何尺寸空间 $(W, L, nf, m)$ 中盲猜数字，将可控动作空间重参数化为物理单调的**本征工作点目标空间 $(I_D, g_m/I_D, L, V_{\text{DS,margin}})$**，由底层预表征的 SKY130 查找表（LUT）确定性反查几何宽长比与合法并联倍数 $m \in [1, m_{\max}]$。
  3. **系统边界与单调提交协议（System Boundary & Monotonic Commit Gate）**：重构 LLM 与数值优化器的分工边界——LLM 仅负责**高层拓扑结构编辑（增删支路、选择补偿架构、修补测试台覆盖盲区）与软约束权重分配**；一旦拓扑固定，交由内嵌信赖域序列线性规划（Trust-Region SLP）算子利用有限差分/伴随雅可比矩阵在最坏 PVT 角点上做多目标局部尺寸闭合，并配备强制的**帕累托单调检查点锁存器（Pareto Checkpoint Latch）**，任何使全角点最坏规格裕度 $\min_{g,c} r_{g,c}(x)$ 跌破历史已验证最优检查点的修改自动回滚。
- **新研究问题与首次实现的能力**：当把离散拓扑图推理（LLM）与局部工作点流形上的梯度/信赖域跨角点闭合（符号—数值内环）按雅可比边界解耦后，中等规模开放权重模型能否在不依赖完美同任务拓扑泄露（Skill 8）的前提下，仅凭跨任务近似电路库检索改造加白盒敏感度内环，在两小时预算内突破 85% 全工况通过率并彻底消灭 pass-then-regress？这将首次使模拟电路 Agent 从“黑盒终端调参工”升级为具备**物理区域感知（永不越界撑爆紧凑模型）与单调收敛保证**的结构—数值协同综合器。
- **核心因果机制**：在几何空间 $(W, L)$ 中，MOSFET 在强反型、中等反型与亚阈值区跨越指数与平方律关系，LLM 用自回归 token 预测连续浮点尺寸本质上是在无梯度地拟合高曲率隐函数；转换到 $(g_m/I_D, I_D, L)$ 流形并显式暴露局部敏感度矩阵 $J_{m,p}$ 后，带宽、热噪声、摆幅与功耗之间的局部对偶折中在单步内退化为良态的凸锥/线性规划子问题，唯有当该线性规划报告**不可行（infeasible certificate，即当前拓扑存在结构性指标冲突，如一级五管运放无法兼顾 110 dB 增益与 1.8 V 摆幅）**时，才向 LLM 返回精确的“结构冲突证明”触发拓扑跃迁。
- **最大收益与最大科学风险**：最大收益是将长程模拟闭合所需的仿真采样复杂度降低一个数量级，让单次成本不足 \$0.5 的开放权重模型在多角点硬题（如 Slot 25、Slot 33/34、Slot 50）上超越 \$30+ 的前沿闭源黑盒 Agent；最大科学风险在于**强非线性开关瞬态与大信号周期稳态任务（如 Slot 27/42 的异步 SAR/Flash ADC、Slot 15/18 的电荷泵、Slot 49 的 LC VCO）**缺乏单一静态直流工作点，局部小信号雅可比线性化在大信号摆幅与时钟切换边界处可能失准甚至误导不可行性判定。
- **区分替代解释的最小实验**：在 Analog Design Bench 最难的 15 道未饱和任务（Solved by $\le 6$，涵盖连续时间运放与混合信号开关电路两类）上，固定同一基座 `DeepSeek V4 Pro`，对比三组单因子处理：(A) 原始网表文本空间直接编辑 + 帕累托检查点锁存；(B) $(g_m/I_D, I_D, L)$ 查找表重参数化动作空间（仍由 LLM 提出数值）+ 检查点锁存；(C) 完整 $(g_m/I_D, I_D, L)$ 空间 + 局部雅可比信赖域 SLP 内环 + 不可行证明驱动的 LLM 拓扑重构。若 (B) 显著优于 (A) 则证实几何尺寸非线性是主要障碍；若 (C) 在连续与采样放大器上大幅甩开 (B) 但在纯数字控制异步 SAR 逻辑定时上增益收窄，则精准界定了小信号敏感度内环的因果有效域。
- **与最近工作的实质差异**：不同于 `White-Box Reasoning`（仅将 $g_m/I_D$ 数据当作提示词上下文喂给 LLM 做自然语言推理）或 `ADO-LLM` / `LEDRO`（在固定预定义拓扑上用无物理导数的黑盒贝叶斯优化搜几何尺寸）（物理页 11–12、页 14–15，References 与 Appendix A）[pdf:E12]，本方案将“局部多角点信赖域不可行性证明（infeasibility dual certificate）”作为触发 LLM 执行**跨拓扑结构变异**的精确控制信号，打通了开放拓扑合成与局部物理保真闭合的双向闭环。

- **Wild-card Alternative（一句话不同机制备选）**：放弃在推理期让 Agent 从零编写脆弱的 SPICE 诊断测试台，转而用模拟任务规格合同训练一个**对抗性测试台协同进化双智能体（Generator–Breaker Co-Evolution）**——由专职 Breaker Agent 专门搜寻电源斜坡、极端跨角点与失配种子的最坏反例工况来证伪 Generator Agent 的当前网表，仅靠纯博弈自博弈验证闭环解决盲盒验收下的漏测与回退难题。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Abstract & Fig. 1"
[pdf:E02]: <_evidence/E02-p002-page.png> "PDF 物理页 2，Section 1 Introduction"
[pdf:E03]: <_evidence/E03-p003-page.png> "PDF 物理页 3，Section 2 Table 1 & Section 3.1"
[pdf:E04]: <_evidence/E04-p004-page.png> "PDF 物理页 4，Section 3.2-3.3 & Fig. 2"
[pdf:E05]: <_evidence/E05-p005-page.png> "PDF 物理页 5，Section 4 & Table 2"
[pdf:E06]: <_evidence/E06-p006-page.png> "PDF 物理页 6，Section 4 & Fig. 3"
[pdf:E07]: <_evidence/E07-p007-page.png> "PDF 物理页 7，Section 5.1-5.2"
[pdf:E08]: <_evidence/E08-p008-page.png> "PDF 物理页 8，Fig. 4 & Section 5.2 Interpretation"
[pdf:E09]: <_evidence/E09-p009-page.png> "PDF 物理页 9，Section 6 & Fig. 5"
[pdf:E10]: <_evidence/E10-p010-page.png> "PDF 物理页 10，Section 7 Discussion, Limitations & Broader Impact"
[pdf:E11]: <_evidence/E11-p014-page.png> "PDF 物理页 14，Authors Information"
[pdf:E12]: <_evidence/E12-p015-page.png> "PDF 物理页 15，Appendix A Extended related work"
[pdf:E13]: <_evidence/E13-p016-page.png> "PDF 物理页 16，Appendix B Fig. A1 & Table A1 (Slots 1-14)"
[pdf:E14]: <_evidence/E14-p017-page.png> "PDF 物理页 17，Appendix B Table A1 (Slots 15-40)"
[pdf:E15]: <_evidence/E15-p018-page.png> "PDF 物理页 18，Appendix B Table A1 (Slots 41-50), Table A2 & Appendix C"
[pdf:E16]: <_evidence/E16-p019-page.png> "PDF 物理页 19，Appendix C Check Expansion Formula, Limits & Table A3"
[pdf:E17]: <_evidence/E17-p020-page.png> "PDF 物理页 20，Appendix C Checkpoint Records & Appendix D Fig. A2"
[pdf:E18]: <_evidence/E18-p021-page.png> "PDF 物理页 21，Appendix D Tool Wait, Candidate Circuits & Fig. A3"
[pdf:E19]: <_evidence/E19-p023-page.png> "PDF 物理页 23，Appendix F & Table A4 Design Skills 1-8"
[pdf:E20]: <_evidence/E20-p024-page.png> "PDF 物理页 24，Appendix G & Fig. A5 Flash ADC Trajectories"
[pdf:E21]: <_evidence/E21-p025-page.png> "PDF 物理页 25，Appendix G Display Normalized Margin Formulas"
