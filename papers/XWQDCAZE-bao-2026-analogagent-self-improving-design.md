# AnalogAgent: Self-Improving Analog Circuit Design Automation with LLM Agents

- **作者**：Zhixuan Bao, Zhuoyi Lin, Jiageng Wang, Jinhai Hu, Yuan Gao, Yaoxin Wu, Xiaoli Li, Xun Xu
- **出处**：Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD ’26)
- **年份**：2026
- **DOI**：10.1145/3770855.3818993
- **Zotero key**：XWQDCAZE

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。

## § 1 — 研究问题与重要性

本文致力于解决一个紧迫的电子设计自动化（EDA）核心问题：在**无需模型参数训练（training-free）且不依赖任何预建外部电路拓扑库或领域知识库（library-free）**的前提下，如何利用大语言模型（LLM）将自然语言电路规格指令端到端地转化为可执行、满足直流工作点与电气功能断言的模拟电路设计脚本（SPICE/PySpice）及整定参数（物理页 1–3，Abstract、Section 1 与 Section 3.1）[pdf:E01][pdf:E04]。模拟集成电路是生物医学传感、环境监测与大型科学仪器中连接连续物理世界与数字计算的咽喉环节，其噪声、线性度与稳定性直接决定信号链上限；然而与拥有布尔代数标准抽象和成熟逻辑综合工具链的数字电路不同，模拟电路设计强耦合了拓扑结构选择、管子工作区偏置（如饱和区不等式）与多轮仿真调参，长期高度依赖资深工程师的启发式试错（物理页 1，Section 1）[pdf:E01]。

此前基于 LLM 的模拟电路自动化之所以在复杂任务与工业部署上卡壳，根源在于三重结构性矛盾。第一是**单模型全包范式（Single LLM paradigm）**，主流方法让单一智能体在同一对话循环内同时承担网表编码、SPICE 报错诊断与多轮迭代修正，导致异构认知任务相互干扰（物理页 2，Section 1）[pdf:E02]。第二是**上下文磨损（Context attrition）**，随着调试轮次累加，LLM 在重写和摘要历史对话时会不断压缩原始指标与技术细节，冲刷掉引脚顺序、衬底电位连接与偏置边界等硬约束——例如在 Hard Task 25（运放比较器）中，基线 AnalogCoder-Pro 的提示词在迭代中从 3.8K tokens 萎缩至 1.4K tokens，耗费约 7 分钟才碰出首个合规电路（物理页 2，Section 1 与 Fig. 1）[pdf:E02]。第三是**对人工拓扑库与云端超大闭源模型的双重依赖**：一方面，外挂子电路库在未见结构或专有场景下难以获取；另一方面，商业芯片设计中的工艺设计套件（PDK）与历史电路受严格保密协议（NDA）约束，严禁上传云端 API，而可本地私有化部署的紧凑开源模型（1.7B–14B）在单循环框架下首轮生成极不可靠（物理页 2，Section 1；物理页 8–9，Section 4.6 与 Section 5）[pdf:E02][pdf:E14][pdf:E15]。解决这一问题不仅能把旗舰模型在 30 任务基准上的首轮通过率（Pass@1）推高至 97.4%（GPT-5）和 92.0%（Gemini-2.5-Flash）、将硬任务首次收敛时间压缩至秒级（Task 25 仅 17.13 秒），更重要的是让本地部署的 Qwen3-8B 获得 +48.8 个百分点的平均 Pass@1 跃升（达 72.1%），打通了受 NDA 保护的本地化智能模拟 EDA 落地路径（物理页 1–2，Abstract 与 Fig. 1；物理页 8，Section 4.6 与 Fig. 5）[pdf:E01][pdf:E02][pdf:E14]。

## § 2 — 前人工作与不足

前人工作主要沿“传统数值/图优化 EDA 工具”与“LLM 驱动的电路生成系统”两条路线演进，但在开放拓扑适应性、外部先验依赖与长程上下文保真度上各有硬伤。

在传统模拟电路自动化路线中，一类是以 AutoCkt、GCN-RL、DNN-Opt、APOSTLE、基于 $g_m/I_D$ 的强化学习优化器以及神经仿真器加速框架 CRONuS、INSIGHT 为代表的**器件尺寸整定（device sizing）方法**（物理页 2，Section 2.1）[pdf:E03]。这些工作显著提升了固定架构下的样本效率，但其搜索空间被锁死在人工预先给定的电路模板内；一旦目标规格需要更改偏置支路、调整有源负载形式或引入级间补偿结构，固定参数向量优化便无能为力。另一类是以多拓扑联合寻优、整数规划单元选型及数据驱动拓扑综合器为代表的**拓扑探索系统**（物理页 2，Section 2.1）[pdf:E03]。此类系统的瓶颈在于候选可行性筛查开销极高：随机或组合拼接出的大量拓扑因缺失直流通路、偏置不可行或牛顿迭代不收敛而在 SPICE 仿真中直接失败，同时强依赖专家手写解析方程与预定义宏模块接口范围，跨电路族或跨工艺迁移的工程配置门槛极高。

在 LLM 驱动的电路生成路线中，早期代表作如 **SPICEPilot**、**Artisan** 与 **ADO-LLM** 依赖精心编写的静态提示词与上下文示例（in-context exemplars）直接生成网表或配合贝叶斯优化（物理页 2，Section 2.2）[pdf:E03]。由于缺少结构化的跨轮错误归因与持久记忆，这类方法重度依赖暴力采样——如 SPICEPilot 在 30 任务基准上 Pass@1 仅为 50.1%，需靠 30 次采样才能将 Pass@5 堆到 96.5%，平均首次成功耗费高达 251.5K tokens（物理页 5–6，Section 4.2、Table I 与 Table II）[pdf:E09][pdf:E10]。第二类训练式方法如 **AnalogGenie**、**LaMAGIC** 与 **CktGNN** 通过监督微调、强化学习或图神经网络学习拓扑分布（物理页 2–3，Section 2.2）[pdf:E03][pdf:E04]，但受限于稀缺的标注网表数据，面对新电路类别面临重训练成本。第三类近期强基线引入外部结构化资源与闭环反馈，包括知识图谱/专家库增强的 **AnalogXpert**、**AMSnet-KG**、**LADAC**、**LayoutCopilot**，以及本文最直接的对比标杆 **AnalogCoder**（引入人工整理的 Circuit Tool Library 可复用子电路库）和 **AnalogCoder-Pro**（进一步融合多模态波形视觉反馈与尺寸寻优）（物理页 2–3，Section 1 与 Section 2.2；物理页 5，Section 4.1）[pdf:E02][pdf:E04][pdf:E09]。然而，AnalogCoder 与 AnalogCoder-Pro 一方面预设了外部电路工具库的存在，另一方面仍把代码生成与多轮纠错耦合在单一智能体对话流中，受制于上下文磨损，不仅在复杂模块（如 GPT-5 下 AnalogCoder 的 Hard 任务 Pass@1 仅 36.5%，AnalogCoder-Pro 在 Task 16、24、25 上仅得 16.7%、36.7%、40.0%）上频繁卡壳，切换到小参数模型 Qwen3-14B 时甚至因长多模态提示词过载使 Pass@1 从裸基座的 35.3% 倒退至 29.6%（物理页 5–6，Section 4.2 与 Table I；物理页 8，Section 4.6 与 Fig. 5）[pdf:E09][pdf:E10][pdf:E14]。

## § 3 — 重建作者的思考路径

如果回到本文之前的技术节点，不预设多智能体与自进化记忆架构，一个直面模拟电路代码生成痛点的研究者会观察到两组尖锐的实验反常。第一组反常来自失败轨迹追踪：在完全去掉预建子电路库后，让单 LLM 根据 PySpice/SPICE 报错反复修改比较器或两级放大器脚本，模型在第 1 轮修好了子电路注册接口，到第 13 轮调拓扑时又写出了重复的晶体管实例名 `M3`，第 20 轮甚至再次把字符串误传给期待对象实例的 `subcircuit()` 接口（物理页 6–7，Section 4.4 与 Fig. 3）[pdf:E11][pdf:E12]。第二组反常来自上下文长度监控：直觉上多轮追加报错会让上下文越来越长，但在单智能体自总结机制下，随着轮次增加，智能体倾向于把长篇规格书和历史排查记录改写成简短概括，导致提示词反而从 3.8K tokens 缩水到 1.4K tokens，原本明确的节点命名、电源轨和管子连接细节在自我重写中不断蒸发（物理页 2，Fig. 1）[pdf:E02]。

顺着这两条线索逆向推演，第一步必然走向**认知职责的物理解耦**。写可执行网表代码（需要聚焦全局接口规范与完整模板）、做物理仿真排障（需要联合比对直流工作点 `.op`、扫描曲线 `.dc` 与波形斜率定位哪只管子脱离饱和区或卡死电源轨）、以及提炼通用避坑准则（需要剥离当前试探参数、抽取跨轮不变量）是三种截然不同的信息处理操作。把它们拆成各司其职的三个角色——**Code Generator**、**Design Optimizer** 和 **Knowledge Curator**——就能阻止纠错过程去篡改原始设计规范（物理页 3–4，Section 3.2–3.3 与 Fig. 2）[pdf:E05][pdf:E06][pdf:E07]。

但仅拆分角色还不够：如果 Curator 总结出的经验只是不断往长文本提示词里硬塞，跨迭代与跨任务积累的文本很快会重新淹没指令显著性，甚至混入试错期产生的错误经验。受测试时自适应记忆工作（如 Dynamic Cheatsheet 与 Agentic Context Engineering）启发，第二步自然推导出**结构化外置剧本（Adaptive Design Playbook）**：将经验按电路类型分桶存储，写入前强制经过硬接口约束冲突筛查与去重算子，读取时按任务类型精确匹配或子串回退，把提取出的紧凑规则每次直接拼接在**未经任何摘要损耗的原始任务指令**之后（物理页 3–4，Section 3.3–3.4，Eq. (2) 与 Eq. (7)–(8)）[pdf:E05][pdf:E07]。

最后一步来自模拟电路特有的“离散结构—连续参数”耦合痛点：一个拓扑完全正确、仅仅因为初始栅极直流偏置点选偏或宽长比 $W/L$ 未对齐而导致增益不足的候选电路，若直接判死重写拓扑会造成巨大浪费；反过来，指望 LLM 用离散文本生成去精调连续实数尺寸也极其低效。于是作者在诊断环内加入基于直流扫描曲线的自动可行偏置点重注入以挽救好拓扑，并在前端多智能体闭环锁定“功能可行电路”后，级联一段由 LLM 划定可调变量区间、交由 Optuna TPE 贝叶斯优化器执行连续数值寻优的后端流程，最终成型为完整的 AnalogAgent 框架（物理页 3–5，Eq. (5)、Fig. 2 与 Section 3.5）[pdf:E05][pdf:E06][pdf:E08]。

## § 4 — 核心 Intuition

单智能体闭环之所以在复杂模拟电路上越改越乱，是因为它用“有损的滚动对话摘要”同时充当短期排错草稿本与长期约束说明书，导致修好新仿真错误时冲掉了旧接口约定和偏置条件。AnalogAgent 的核心支点是**“原始指令零损耗常驻 + 执行证据结构化沉淀”**：将网表生成、五级物理仿真诊断与跨轮规则蒸馏彻底分权，把每一次成功模板与失败报错实时压缩成按电路类型键控、经接口冲突校验去重的紧凑设计手册（Adaptive Design Playbook），每一轮都用“干净的原始指标 + 精准命中的硬规则”重新驱动生成。这一机制既从根源上切断了多轮改写的上下文磨损，又把原本一次性的试错代价转化为跨任务可复用、连本地小参数开源模型也能直接照章执行的显式电路装配语法与工作区判据。

## § 5 — 具体方法与完整 Pipeline

### 针对本次阅读重点（Focus 1–3）的正面解答

1. **双环组织架构（拓扑构建 + 参数整定）与跨任务自进化经验机制（回答 Focus 1）**：KDD 2026 将电路设计组织为**“前端 MAS 离散拓扑/功能闭环 + 后端 LLM-Optuna 连续参数整定闭环”的两阶段双环级联架构**，外加一条横跨任务序列的**自进化记忆（SEM）长程经验环**（物理页 4–5，Fig. 2 与 Section 3.5；物理页 10，Algorithm 1）[pdf:E06][pdf:E08][pdf:E16]。前端内环由 Code Generator、Design Optimizer、Knowledge Curator 三个智能体在单任务尝试预算内（如 Fig. 2 所示单轮子循环 `Max Attempts = 3`，通用推理过程见 Algorithm 1 的预算 $K$）围绕可执行 PySpice 工件迭代，专门解决语法合规、拓扑连通、直流工作点与传输特性可行性（产出 Functional Circuit），其中 Design Optimizer 还内嵌了直流扫描偏置重注入子步骤（物理页 3–4，Section 3.3、Eq. (5) 与 Fig. 2）[pdf:E05][pdf:E06]；一旦前端环产出功能可行电路，系统切入后端参数整定环，由 LLM 根据任务要求与仿真输出识别关键可调器件参数（如 $W/L$ 或阻容值）及搜索边界，交由 Optuna 中的树结构 Parzen 估计器（TPE）做贝叶斯数值仿真寻优，产出最终达标电路（Functional & Optimized Circuit）（物理页 4–5，Fig. 2 与 Section 3.5）[pdf:E06][pdf:E08]。跨任务层面，SEM 不依赖任何预置电路库，而是在任务流推进中将基础任务（如 Task 1 共源放大器）沉淀的网表语法、衬底电位与偏置规则持久化至 Adaptive Design Playbook，供后续同族或更高阶任务（如 Task 9/10 多管放大器及基准外未见 cascode/OTA 电路）首轮检索复用，把搜索重心从低级语法试错直接推向高层拓扑构造（物理页 4，Section 3.4；物理页 7–8，Section 4.5 与 Fig. 4；物理页 10，Appendix C）[pdf:E07][pdf:E12][pdf:E13][pdf:E16]。
2. **仿真失败归因与设计规则提炼的数据结构与检索方式（回答 Focus 2）**：为防止经验库退化成冗长杂乱的历史对话堆砌，SEM Playbook 采用**两级键值 JSON 结构 + 五槽位原子规则模板 + 写入去重冲突过滤 + 确定性分层检索**（物理页 4，Section 3.4；物理页 10–11，Appendix B 与 Fig. 6）[pdf:E07][pdf:E16][pdf:E17]。如图 6 所示，Playbook 顶层以粗粒度电路类别（如 `"Amplifier"`）为键，下挂细分 `"circuit_type"`（如 `"CommonSourceAmpDiodeLoad"`）对象列表，每个对象的 `"knowledge"` 数组严格收敛为五类高密度短条目：`Template`（标准器件拓扑与四端连接）、`Req`（必选端口名、器件组合与衬底接法）、`Fix`（“故障现象 $\to$ 修正动作”因果对，如输出卡死电源轨时调 `Vin` 偏置或 $W/L$，工作区失效时满足饱和区不等式）、`Evidence`（关联产物索引 `netlist.sp, op.txt, dc.txt, dc.png, messages.txt`）与 `MM-reflect`（多模态图像判据，如基于 `dc.png` 识别平坦卡轨区与有效斜率区）（物理页 11，Fig. 6）[pdf:E17]。写入时，Curator 只提取紧凑规则增量 $\Delta_t$，并强制执行 `Filter(M_t || \Delta_t; \Omega)` 剔除违背硬接口约束 $\Omega$ 的幻觉经验，再用 `Dedup` 消除重复条目；读取时，检索器先按任务类型 $\tau$ 精确查键，未命中则按子串包含关系回退匹配相近电路族，最后浓缩为简短指令 $\Delta$ 直接拼接到**未经摘要改写的原始任务描述**之后（$P_t = P_{\text{task}}(x) \oplus r_t$），彻底规避了全量历史重写的长文本膨胀（物理页 3–4，Eq. (2) 与 Eq. (6)–(8)；物理页 10，Algorithm 1）[pdf:E05][pdf:E07][pdf:E16]。
3. **基准覆盖类别、多模型对比与消融实验概览（回答 Focus 3）**：评测采用统一封装的 30 题模拟电路基准（Easy 1–8、Medium 9–13、Hard 14–30），覆盖放大器、反相器、电流镜、运放、振荡器、积分/微分/加减法器、施密特触发器、VCO、PLL、比较器、四类无源滤波器与 Gilbert 混频器共 14 种电路类型，并在附录 C 扩展了 5 类未见复杂 cascode/OTA 拓扑（物理页 5，Section 4.1；物理页 10–11，Appendix C 与 Table IV）[pdf:E09][pdf:E16][pdf:E17]。跨 8 个基座模型（DeepSeek-V2-Lite、Llama-3-8B、Gemini-2.5-Flash、GPT-5 及 Qwen3 1.7B/4B/8B/14B）与 3 个专用基线（SPICEPilot、AnalogCoder、AnalogCoder-Pro）对比显示，AnalogAgent 在 GPT-5（97.4% Pass@1）、Gemini-2.5-Flash（92.0% Pass@1）及全部四个 Qwen3 尺度上均取得最高成功率；在 Gemini-2.5-Flash 上的 $2 \times 2$ 模块消融（Table III）与附录 C 的三变体跨问题迁移消融共同证实了 MAS 短期诊断与 SEM 长期记忆的互补必要性（物理页 5–8，Section 4.2–4.6、Table I–III 与 Fig. 5；物理页 10，Appendix C）[pdf:E09][pdf:E10][pdf:E12][pdf:E14][pdf:E16]。

### 结合真实电路任务实例（Task 10 与 Task 25）的完整 Pipeline 剖析

将整个闭环放在图 6 展示的 **Medium Task 10（二极管连接 PMOS 负载的单级共源放大器）** 与图 3 的 **Hard Task 25（运放比较器）** 上走查，可以清晰看清输入表示、LLM 离散推理与确定性数值/符号验证器的职责边界：

- **输入表示与检索规划**：系统接收四元组 $\mathcal{I} = (x, \tau, \Omega, \Phi_{\text{task}})$（物理页 3，Section 3.1）[pdf:E04]。以 Task 10 为例，$x$ 描述“设计以栅漏短接 PMOS 为负载的单级共源放大器”，$\tau$ 标识放大器任务，硬接口约束 $\Omega$ 锁定输入输出节点名 `Vin`、`Vout` 与 PySpice 执行规范，$\Phi_{\text{task}}$ 包含有效偏置区增益阈值与非卡轨断言（物理页 11，Fig. 6）[pdf:E17]。若此前已跑过 Task 1，检索算子 $\mathcal{R}(M_t, \tau)$ 从 `"Amplifier"` 桶中取出已验证的五条基础规则 R1–R5（显式定义 5V `Vdd`、保持 `Vin/Vout` 端口、NMOS 衬底接 `0` 且 PMOS 衬底接 `Vdd` 并遵守 `D, G, S, B` 顺序、消除浮空节点、显式声明 Level-1 MOS 模型 `kp/vto/lambda`）及二极管负载模板，组装成增强提示词 $P_t$（物理页 3，Eq. (2)；物理页 8，Fig. 4；物理页 11，Fig. 6）[pdf:E05][pdf:E13][pdf:E17]。
- **LLM 离散代码生成（Code Generator）**：Code Generator 负责离散结构决策与 API 实例化，输出完整可执行 PySpice 脚本 $c_t$——在 Task 10 中定义 `nmos`/`pmos` 模型、5V 电源 `Vdd`、2.5V 输入源 `Vin`、共源输入管 `M1`（漏接 `Vout`、栅接 `Vin`、源衬接地）、栅漏短接至 `Vout` 的负载管 `M2` 以及防浮空保护电阻 `R_safe`（物理页 3，Eq. (3)；物理页 11，Fig. 6）[pdf:E05][pdf:E17]。
- **确定性五级验证例程与 LLM 诊断修补的边界（Design Optimizer）**：候选脚本 $c_t$ 先交由外部确定性 Python/SPICE 执行评估例程 $\mathcal{E}(c_t)$ 顺序跑完五道检查，严格将符号/数值真值判定留在验证器侧，将语义归因交给智能体侧（物理页 3，Section 3.3 与 Eq. (4)–(5)；物理页 11，Fig. 6）[pdf:E05][pdf:E17]：
  1. **需求与拓扑静态检查（`Netlist_check.py`）**：解析生成的网表，核验 `Vin, Vout` 节点存在性及拓扑特征（如 PMOS 栅漏是否确实短接在 `Vout`）；
  2. **SPICE 静态工作点检查（`task_simulation.py` $\to$ `_operation_point_.txt`）**：调用底层 SPICE 求解器计算直流工作点，逐管核对饱和区物理不等式（NMOS 要求 $V_{gs} > V_{th}$ 且 $V_{ds} > V_{gs} - V_{th}$；PMOS 要求 $V_{sg} > |V_{th}|$ 且 $V_{sd} > V_{sg} - |V_{th}|$）；
  3. **直流扫描检查与自动偏置重注入（`_dc_sweep.py` $\to$ `Task_dc_result.txt, Task_dc.png`）**：在 `0.50–4.50 V` 等区间扫描 `Vin` 观察 $V_{\text{out}}(V_{\text{in}})$ 响应；对于需要传输曲线验证的电路，执行算子 $v_t = \mathcal{B}(\mathcal{D}(c_t))$ 从扫描结果中自动挑选高增益可行偏置点并注入原脚本生成辅助候选 $\tilde{c}_t = \mathcal{T}(c_t, v_t)$ 重评，若全区间卡在电源轨（如 `Vout ~5.00`）则生成“增强 NMOS 或削弱 PMOS 负载”的诊断提示；
  4. **电气功能断言检查（`Function_check.py` $\to$ `Function_messages.txt`）**：定量检验有效工作区斜率 $|dV_{\text{out}}/dV_{\text{in}}|$ 是否超过增益门限，或在 Task 25 中检验 `Vin < Vref` 输出低电平、`Vin > Vref` 输出高电平及 `Vin == Vref` 附近的陡峭翻转（物理页 7，Fig. 3；物理页 11，Fig. 6）[pdf:E12][pdf:E17]；
  5. **多模态波形合理性检查（`Task_Waveform.png / _dc.png`）**：结合渲染出的传输曲线/波形图排查平坦死区或轨锁定伪影。
  若任一环节未过，Design Optimizer 汇总错误标志、日志与波形信号 $(e_t, s_t, \ell_t, z_t)$ 生成局部修复指令 $\delta$ 送入下一轮生成（物理页 3，Eq. (4)；物理页 10，Algorithm 1）[pdf:E05][pdf:E16]。
- **规则蒸馏入库与后端连续尺寸整定（Knowledge Curator + Optuna TPE）**：Knowledge Curator 将每一轮的执行证据包 $f_t$（例如 Task 25 中捕获的 PySpice 子电路参数个数报错或器件重名报错，以及 Task 10 中捕获的卡轨修复规律）蒸馏为紧凑规则 $\Delta_t$，经接口冲突筛查与去重后写入 SEM Playbook（物理页 4，Eq. (6)–(7)；物理页 7，Fig. 3）[pdf:E07][pdf:E12]。一旦候选满足全部断言拿到 `PASS(c_t) = 1`，流程转入后端参数优化：LLM 从指令与当前仿真结果提取可调器件尺寸及搜索上下界，启动 Optuna 的 TPE 贝叶斯优化器迭代调用 SPICE 寻优，输出最终满足规格的可执行脚本与验证波形（物理页 5，Section 3.5；物理页 10，Algorithm 1）[pdf:E08][pdf:E16]。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文用 Eq. (1)–(9) 对“无训练模拟电路代码合成 + 闭环记忆演化”给出了清晰的形式化定义，并用超几何分布公式定义了无偏 Pass@$k$ 指标。逐条拆解其工程物理含义与防病态设计如下：

1. **硬约束与电气断言合取验收准则 Eq. (1)**：给定任务实例 $\mathcal{I} = (x, \tau, \Omega, \Phi_{\text{task}})$ 与满足接口规范空间 $\mathcal{P}$ 中的候选脚本 $c$，执行评估算子输出 $(e, s, z) = \mathcal{E}(c)$，有效解定义为：
   $$\text{PASS}(c) = 1 \iff (e = 0) \land (s = 0) \land \left(\bigwedge_{k=1}^K \varphi_k(z) = 1\right)$$
   （物理页 3，Section 3.1，Eq. (1)）[pdf:E04]。其中 $e \in \{0,1\}$ 指示 Python/评估层运行时错误或硬接口约束 $\Omega$（规定节点名、子电路引脚、仿真器设置）违例，$s \in \{0,1\}$ 指示底层 SPICE 仿真器故障（语法解析错误、奇异矩阵或直流工作点不收敛），$z$ 为仿真产出的工作点与波形数据，$\varphi_k(z) \in \{0,1\}$ 为第 $k$ 个任务专属电气功能断言。这种三级逻辑与形式化严密堵死了代码生成评测中最常见的**“语法可跑但电路假活”病态解**——例如靠接地大电阻消除浮空节点报错可令 $e=0 \land s=0$，但无法混过 $\varphi_k(z)$ 对饱和区工作点与小信号增益的检验。
2. **锚定原始指令的生成与扫描偏置解耦 Eq. (2)–(5)**：在第 $t$ 轮迭代中，生成提示词构造、代码采样、多维执行评估与传输曲线偏置修正分别为：
   $$P_t = P_{\text{task}}(x) \oplus r_t, \quad r_t = \mathcal{R}(M_t, \tau), \quad c_t = \mathcal{G}(P_t)$$
   $$(e_t, s_t, \ell_t, z_t) = \mathcal{E}(c_t), \quad v_t = \mathcal{B}(\mathcal{D}(c_t)), \quad \tilde{c}_t = \mathcal{T}(c_t, v_t)$$
   （物理页 3，Section 3.3，Eq. (2)–(5)）[pdf:E05]。这里有两个精妙的结构设计：其一，$P_t$ **不把 $t-1$ 轮的长对话重写结果作为递推状态**，而是将不可变的原始任务需求 $P_{\text{task}}(x)$ 作为常驻基座，仅通过拼接算子 $\oplus$ 挂载从记忆态 $M_t$ 检索出的任务相关知识 $r_t$，从状态转移结构上根除了多轮自摘要引发的信息熵衰减；其二，Eq. (5) 通过直流扫描算子 $\mathcal{D}(c_t)$ 获取全范围输入-输出曲线，再用偏置选择算子 $\mathcal{B}(\cdot)$ 定位有效放大区偏置电压 $v_t$ 并由代码变换算子 $\mathcal{T}(c_t, v_t)$ 回填重测，避免了因 LLM 瞎猜的静态偏置电压偏离高增益区几十毫伏就把原本正确的电路拓扑误判为结构错误。
3. **双向反馈蒸馏、带约束去重更新与分层回退检索 Eq. (6)–(9)**：Knowledge Curator 的蒸馏与 SEM 的状态更新、检索及闭环推进形式化为：
   $$f_t = \big(x, c_t, e_t, s_t, \ell_t, z_t, \text{PASS}(c_t)\big), \quad \Delta_t = \phi(f_t)$$
   $$M_{t+1} = \mathcal{U}(M_t, \Delta_t) = \text{Dedup}\big(\text{Filter}(M_t \parallel \Delta_t; \Omega)\big)$$
   $$r(\tau) = \begin{cases} \mathcal{R}[\tau], & \tau \in \text{keys}(r), \\ \mathcal{R}[k^*], & k^* = \min\{k \in \text{keys}(r) : k \prec \text{str}(\tau)\}, \\ \emptyset, & \text{otherwise} \end{cases}$$
   $$r_{t+1} = \mathcal{R}(M_{t+1}, \tau), \quad P_{t+1} = P_{\text{task}}(x) \oplus r_{t+1}, \quad c_{t+1} = \mathcal{G}(P_{t+1})$$
   （物理页 4，Section 3.3–3.4，Eq. (6)–(9)）[pdf:E07]。
   - Eq. (6) 将布尔通过标签 $\text{PASS}(c_t)$ 与诊断日志 $\ell_t$ 一并纳入反馈元组 $f_t$，使蒸馏函数 $\phi(\cdot)$ 同时捕获失败样本的“排错规则（Fix）”与成功样本的“标准拓扑模板（Template）”。
   - Eq. (7) 解决了持续学习记忆库最致命的**幻觉污染与冗余爆炸**问题：若直接追加 $M_t \parallel \Delta_t$，试错轮次中违反端口命名或 API 签名的错误归因会永久污染后续生成，同义规则也会重复堆积；引入受硬约束 $\Omega$ 监督的 `Filter` 与去重算子 `Dedup`，确保 Playbook 只保留合法且正交的原子条目。
   - Eq. (8) 用精确键匹配优先、子串包含匹配 $k \prec \text{str}(\tau)$ 兜底的分段函数实现了跨拓扑泛化（例如新任务含 `"Amplifier"` 或 `"Opamp"` 子串即可继承基础偏置与衬底规则）。需要严谨指出的是，原文 Eq. (8) 存在两处明显的符号书写瑕疵：作者把记忆库字典 $M_t$ 的键集合与检索算子混写成了 $\text{keys}(r)$ 与 $\mathcal{R}[\tau]$，紧接正文中又给静态任务类型加了冗余时间下标 $\tau_t$，且对字符串集合取 $\min$ 未说明是按字典序还是最短前缀定界——对照附录 B 的确定性检索说明与图 6 的 JSON 结构，其真实工程语义是在当前记忆字典 $M_t$ 的键空间上执行确定性精确查表与有序子串回退（物理页 4，Eq. (8)；物理页 10–11，Appendix B 与 Fig. 6）[pdf:E07][pdf:E16][pdf:E17]。

## § 7 — 实验设计与结论

本文围绕四个递进研究问题设计了系统实验：(1) 在零训练、零外部电路库条件下，AnalogAgent 在标准多难度基准上的首轮与多样本成功率、Token 消耗及耗时能否全面击败带库与多模态反馈强基线？(2) MAS 与 SEM 两个核心模块各自贡献几何、是否存在非加性协同？(3) 从基础电路自发沉淀的 Playbook 能否跨任务加速收敛，甚至零样本迁移到未见过的复杂高阶拓扑？(4) 该架构能否大幅拉升本地私有化部署的小参数开源权重模型？

在实验设置上，主基准采用整合自 AnalogCoder / AnalogCoder-Pro 的 **30 道标准化模拟电路任务**，按器件规模与拓扑复杂度分为三级：**Easy（Tasks 1–8，共 8 题：5 类单/多级放大器、2 类反相器、1 类电流源）**、**Medium（Tasks 9–13，共 5 题：米勒补偿两级放大器、二极管连接 PMOS 负载共源放大器、2 类差分运放、共源共栅电流镜）** 与 **Hard（Tasks 14–30，共 17 题：有源负载两级差分运放、套筒式共源共栅运放、RC 相移与文氏电桥振荡器、运放积分/微分/加法/减法器、非反相施密特触发器、VCO、PLL、运放比较器、低通/高通/带通/带阻四类无源滤波器、Gilbert 混频器）**（物理页 5，Section 4.1；物理页 11，Table IV）[pdf:E09][pdf:E17]。此外，附录 C 从 AnalogGenie 数据集中额外引入 **5 类基准外未见复杂拓扑**（增益自举共源共栅放大器、折叠共源共栅结构、高摆幅 OTA、套筒式增益自举放大器、高增益共源共栅运放）（物理页 10，Appendix C）[pdf:E16]。参评对象涵盖 **3 个专用系统基线**（SPICEPilot、AnalogCoder、AnalogCoder-Pro）与 **8 个 LLM 基座**（主实验的 DeepSeek-V2-Lite、Llama-3-8B、Gemini-2.5-Flash、GPT-5，以及小模型专项的 Qwen3-1.7B、Qwen3-4B-Instruct、Qwen3-8B、Qwen3-14B），在双卡 NVIDIA RTX A6000（Ubuntu 20.04, Python 3.10, vLLM 本地推理与官方 API）环境下，每题固定采样 $n = 30$ 个候选计算无偏指标 $\text{Pass@}k = 1 - \binom{n-c}{k}/\binom{n}{k}$（汇报 Pass@1 与 Pass@5），并统计 5 次随机试验的均值标准差、首次成功平均 Token 与运行时间（物理页 5–6，Section 4.1–4.2、Table I–II；物理页 8，Section 4.6；物理页 10，Appendix A）[pdf:E09][pdf:E10][pdf:E14][pdf:E16]。

实验给出了四组明确的定量答案：

1. **主基准成功率与收敛效率双优**：在 Table I 的 9 列模型/方法对比中，裸开源小基座 DeepSeek-V2-Lite 与 Llama-3-8B 平均 Pass@1/Pass@5 仅为 6.7%/11.4% 与 8.6%/27.0%；SPICEPilot（Gemini-2.5-Flash）Pass@1 低至 50.1%（Pass@5 为 96.5%）；依赖预设电路工具库的 AnalogCoder 在 Gemini-2.5-Flash 与 GPT-5 上分别为 47.6%/66.4% 与 60.8%/71.5%（GPT-5 下 Hard 任务平均 Pass@1 仅 36.5%）；引入多模态反馈的 AnalogCoder-Pro 在双基座上达到 81.7%/93.0% 与 88.6%/98.2%，但在高难任务上短板明显（如 GPT-5 下 Task 16 仅 16.7%、Task 24 仅 36.7%、Task 25 仅 40.0%，Gemini-2.5-Flash 下 Task 25 与 Task 30 均跌至 3.3%）。相比之下，无外部库的 AnalogAgent 在 Gemini-2.5-Flash 上达到 **92.0%/99.9%**，在 GPT-5 上斩获 **97.4%/100.0%**（全部 30 题 Pass@5 达 100.0%，25 题 Pass@1 满分，Hard 任务 Pass@1 较 AnalogCoder-Pro 提升约 16.7%）（物理页 5–6，Section 4.2 与 Table I）[pdf:E09][pdf:E10]。Table II（统一采用 Gemini-2.5-Flash 跑 5 次随机试验）进一步显示 AnalogAgent 在 Easy/Medium/Hard 上取得 **98.3±1.6% / 87.1±2.9% / 88.7±0.9%**（总均 **92.3±0.6%**），方差全场最小，同时将全基准平均首次成功耗时压缩至 **1.3 分钟**（优于 SPICEPilot 的 2.6 分钟和 AnalogCoder-Pro 的 2.1 分钟），首次成功平均消耗降至 **32.0K tokens**（低于 AnalogCoder-Pro 的 40.2K 与 SPICEPilot 的 251.5K），证明性能增益源自知识复用而非暴力堆砌采样预算（物理页 5–6，Section 4.2 与 Table II）[pdf:E09][pdf:E10]。
2. **正交消融与单模型记忆负迁移现象**：Table III 在 Gemini-2.5-Flash 上对比了五组配置——裸模型（Avg Pass@1/Pass@5 为 50.4%/56.0%）、`w/o MAS, w/o SEM`（63.8%/76.8%，Hard Pass@1 仅 43.7%）、`w/ MAS, w/o SEM`（79.4%/87.8%，Medium/Hard Pass@1 升至 75.3%/68.8%）、`w/o MAS, w/ SEM`（58.6%/68.1%）以及完整 `AnalogAgent`（92.0%/99.9%，Easy/Medium/Hard Pass@1 达 100.0%/86.7%/89.8%）（物理页 5，Section 4.3；物理页 7，Table III）[pdf:E09][pdf:E12]。除了验证完整模型最强外，Table III 数据还揭示了一个正文中未展开但极其关键的现象：单独启用 SEM 而不配 MAS（`w/o MAS, w/ SEM`）虽使 Easy 任务 Pass@1 从 82.9% 升至 88.8%，却令 Medium 任务从 64.7% **倒退至 56.0%**（甚至低于裸基座的 60.0%），拖累总平均从 63.8% 跌至 58.6%；反之在具备 MAS 专业化诊断后再开启 SEM，总平均却从 79.4% 跃升至 92.0%（Hard 任务暴涨 21.0 个百分点）。这说明缺乏独立诊断与精炼把关的单智能体记忆会把粗糙或误导性的局部经验带入中等复杂任务，MAS 的精准归因是 SEM 正向运转的前提。
3. **任务内自修复与跨任务/跨问题零样本迁移**：在单任务长程演化案例 Hard Task 25 上，AnalogAgent 通过固化子电路实例化接口与器件唯一命名规则，在 30 轮内将 Pass@1 从 0.0% 稳步推高至 86.7%（物理页 6–7，Section 4.4 与 Fig. 3）[pdf:E11][pdf:E12]。在跨任务迁移案例（Fig. 4）中，从基础 Task 1 蒸馏出的五条供电、端口、衬底与模型规则 R1–R5 直接复用于 Medium Task 9 与 Task 10，使 Task 9 的 Pass@5 从 40.0% 提升至 99.8%（首次成功耗时从 28.6s 缩短至 19.3s，总 Token 削减 53.9 万），Task 10 的 Pass@1 从 83.3% 升至 100.0%（耗时从 18.4s 缩短至 13.3s，总 Token 削减 5.9 万）（物理页 7–8，Section 4.5 与 Fig. 4）[pdf:E12][pdf:E13]。在附录 C 的 5 类未见高阶拓扑上，预载原基准所学 Playbook 的 AnalogAgent 取得 **92.4%** 平均最终 Pass@1（五个拓扑分别为 100.0%、80.0%、88.7%、100.0%、93.3%），显著超越空 Playbook 冷启动的 `AnalogAgent (Task i)`（平均 **70.7%**）与无 SEM 变体（平均 **44.7%**）（物理页 10，Appendix C）[pdf:E16]。
4. **显著放大紧凑开源权重模型能力**：如图 5 所示，在 Qwen3-1.7B、4B-Instruct、8B、14B 四个本地可部署尺度上，裸模型 Pass@1 分别为 2.4%、28.2%、23.3%、35.3%（解出题数 5、15、15、18 题）；AnalogCoder-Pro 分别为 6.1%、30.4%、34.9%、29.6%（解出 7、22、19、16 题，在 14B 尺度上出现负增益）；而 AnalogAgent 全面跃升至 **22.2%、62.3%、72.1%、76.7%**（解出 **17、25、27、27** 题），证明结构化多智能体与外置剧本能有效弥补小模型参数容量短板（物理页 8，Section 4.6 与 Fig. 5）[pdf:E14]。

## § 8 — Take-aways

- **5 句话版**：现有基于单 LLM 的模拟电路自动生成方法将网表编写、报错诊断与历史摘要耦合在同一对话循环中，极易因上下文磨损丢失硬性接口与偏置细节，且重度依赖预建外部电路库。AnalogAgent 提出了一种零训练、零外部库的智能体框架，通过前端三智能体（Code Generator、Design Optimizer、Knowledge Curator）与自进化记忆（SEM）完成离散拓扑合成与排错，再级联后端 LLM 引导的 Optuna TPE 贝叶斯参数整定。为了防止记忆库退化为冗长脏文本，系统将成功与失败的五级仿真反馈蒸馏为按电路族键控的五槽位 JSON 剧本（Adaptive Design Playbook），配合硬约束冲突过滤、去重与“干净原始指令 + 确定性检索片段”拼接机制切断多轮遗忘。在涵盖 14 类电路的 30 题基准及 5 类未见复杂共源共栅/OTA 拓扑上，AnalogAgent 在 GPT-5 上取得 97.4% Pass@1，并以 1.3 分钟平均首次成功耗时和 32.0K tokens 跑赢 AnalogCoder-Pro 等强基线。尤为关键的是，该架构在 Qwen3-1.7B 至 14B 等小参数开源模型上实现大幅跃升（其中 Qwen3-8B Pass@1 提升 48.8 个百分点至 72.1%），为受商业 PDK 保密协议约束的本地化模拟 EDA 部署提供了现实路径。
- **3 句话版**：AnalogAgent 通过解耦代码生成、五级物理仿真诊断与知识蒸馏三个智能体，配合后端 Optuna TPE 尺寸优化，解决了单 LLM 模拟电路设计中的上下文磨损与外部拓扑库依赖难题。系统将仿真试错轨迹提炼为经过接口冲突校验与去重的结构化 JSON 设计剧本（SEM），每轮直接挂载于未受损的原始任务指令之后，实现同任务快速自修复与跨任务零样本经验迁移。实验表明该方法不仅在 GPT-5（97.4% Pass@1）和 Gemini-2.5-Flash（92.0% Pass@1）上兼顾最高精度与最低收敛开销，还能将本地开源模型 Qwen3-8B 的 Pass@1 拉升至 72.1%。
- **1 句话版**：AnalogAgent 用“多智能体职责解耦 + 经冲突过滤的结构化自进化设计剧本 + 后端贝叶斯尺寸整定”替代单模型滚动长对话，在不训练权重且不依赖外部电路库的前提下，大幅提升了大、小语言模型生成合规模拟电路的首轮成功率与跨任务迁移效率。

## § 9 — 最脆弱的假设

全文最脆弱、一旦崩塌便会使核心贡献直接失效的单一假设是**“白盒中间层诊断神谕存在性假设（White-box Diagnostic Oracle Assumption）”——即默认每个目标设计任务都预先配备了人工针对该特定电路结构编写的白盒拓扑核查脚本（`Netlist_check.py`）、显式逐管工作区不等式清单与归因提示模板，从而能把复杂的模拟电路失效直接翻译为无歧义的局部修改方向**。

在真实工业级模拟模块设计或新拓扑探索中，工程师给出的输入往往只有**顶层黑盒性能规格书**（例如在特定负载电容与工艺角下要求开环增益 $> 70\text{ dB}$、单位增益带宽 $> 100\text{ MHz}$、相位裕度 $> 60^\circ$、功耗 $< 1\text{ mW}$），根本不可能在合成前就预先写好一个知道“PMOS 负载必须栅漏短接”的 `Netlist_check.py` 或预先指定每只未知晶体管应当处于哪个工作区的检查表（物理页 3，Section 3.1；物理页 11，Fig. 6）[pdf:E04][pdf:E17]。一旦撤掉这层人工预设的白盒拐杖、仅保留黑盒 SPICE 终端波形与标量指标成败信号，整个 MAS–SEM 闭环会遭遇双重断裂：第一，面对多级反馈与频率补偿等强耦合退化（如增益够了但右半平面零点拉垮相位裕度），缺少逐管中间断言的 `Design Optimizer` 无法区分失效究竟源于拓扑缺陷、偏置错位还是管子尺寸失配；第二，正如 Table III 中缺乏精细多智能体诊断的 `w/o MAS, w/ SEM` 变体在 Medium 任务上使 Pass@1 从 64.7% 倒退至 56.0% 所暴露的那样（物理页 7，Table III）[pdf:E12]，一旦上游归因失准，`Knowledge Curator` 就会把巧合生效或归因错位的伪规则提炼进 Playbook，而 Eq. (7) 的 `Filter` 算子只能核查端口名与 API 语法约束 $\Omega$，无法校验深层电路物理因果性（物理页 4，Eq. (7)）[pdf:E07]，进而导致跨轮次与跨任务的连锁记忆污染。

论文为该假设能运转提供的正面证据仅限于理想简化环境：所有 30 道基准题与 5 道迁移题均运行在显式手设 `kp=100e-6, vto=0.5` 的简化 Level-1 MOS 模型与全套五步白盒检验脚本之上（物理页 8，Fig. 4；物理页 10–11，Appendix A、Appendix C 与 Fig. 6）[pdf:E13][pdf:E16][pdf:E17]。与此同时，论文完全回避了两项最关键的压力测试证据：一是**剥离白盒拓扑/工作点提示、仅保留终端电气规格断言时的消融实验**；二是**真实工业 Foundry PDK（如 BSIM4 / FinFET 多工艺角模型及版图前寄生效应）下的验证**——尽管作者在 Section 4.6 与 Section 5 反复以商业 PDK 的 NDA 保密要求作为主推小模型本地部署的核心动机，全文却没有任何一例实验真正接上开源或商用 PDK 器件模型（物理页 8–9，Section 4.6 与 Section 5）[pdf:E14][pdf:E15]。

## § 10 — 最小复现实验

无需搭建完整的 30 题基准、多模态视觉波形反射及双卡 A6000 环境，可在 **1 周内用单张消费级 GPU（本地运行 vLLM + Qwen3-8B + 开源 Ngspice/PySpice，约 250 行 Python 代码）** 完成直击论文核心声称的最小验证/证伪实验。

- **待检核心命题**：(1) AnalogAgent 对小参数模型的巨大增益是否确实来自“常驻干净指令 + 经冲突过滤的结构化 JSON 剧本”，而非单纯因为避免了滚动重写原始提示词？(2) 当剥离白盒拓扑/逐管诊断脚本、退回真实黑盒终端指标反馈时，SEM 自进化机制是否仍然成立？
- **最小数据集切片（6 道跨难度链条电路）**：直接从公开的 AnalogCoder 仓库抽取 6 道构成拓扑递进关系的任务——Task 1（电阻负载共源放大器，作基础语法与偏置种子）、Task 9（两级米勒补偿放大器）、Task 10（二极管连接 PMOS 负载共源放大器）、Task 12（共源共栅电流镜）、Task 15（套筒式共源共栅运放）与 Task 25（运放比较器）（物理页 11，Table IV）[pdf:E17]。跳过后端 Optuna TPE 阶段与多模态截图模块，仅在纯文本 `.op` / `.dc` 仿真输出上运行最多 3 轮内部修正、每题独立采样 $n = 10$ 次测算 Pass@1。
- **四组受控对比变体**：
  1. **Rolling-Summary 单循环**：复现传统单智能体对话，每轮让模型结合报错重写上下文摘要；
  2. **Clean-Prompt 无记忆重试**：每轮保持原始指令 $P_{\text{task}}(x)$ 原文不动，仅附加上一轮原始报错日志，不建跨轮/跨题 Playbook；
  3. **Minimal AnalogAgent（白盒诊断 + JSON Playbook）**：复现三角色提示词、JSON 五槽位规则库、接口名冲突过滤与精确/子串检索，按 Task 1 $\to$ Task 9 $\to$ Task 10 $\to$ Task 12 $\to$ Task 15 $\to$ Task 25 顺序串行推进；
  4. **Black-Box Oracle 对照组**：与变体 3 代码完全一致，但屏蔽 `Netlist_check.py` 拓扑结构提示与逐管饱和区不等式报错，仅向 Design Optimizer 提供语法异常或终端黑盒指标未达标数值（如实际增益 vs 目标增益、输出摆幅区间）。
- **观测指标与判定阈值**：统计 6 题平均 Pass@1、首轮 SPICE 可仿真率（$e=0 \land s=0$ 比例）及跨题累计 Token。若**变体 3 平均 Pass@1 高于变体 1 达 30 个百分点以上，且比变体 2 高出至少 12 个百分点**，则强力支持论文“结构化外置剧本兼具防上下文磨损与跨任务迁移双重收益”的核心结论；反之，若变体 3 与变体 2 差距不足 5 个百分点，说明原论文增益主要来自“不篡改原始提示词”这一简单工程技巧；若**变体 4 相比变体 3 平均 Pass@1 暴跌超过 25 个百分点且 Playbook 中出现跨题误导规则**，则直接证实在无白盒 checker 的真实黑盒规格下该自进化机制不成立。

## § 11 — 最强反例设计

站在审稿反方立场，可以从**“粗粒度检索与静态单调规则引发的物理政体碰撞”**以及**“PySpice API 方言纠错混杂因子”**两个维度构造最具杀伤力的反例攻击：

第一，**可精确构造的病态失效场景——低压亚阈值设计与双稳态/动态闭环电路上的规则碰撞**。审视 Eq. (8) 的检索算子与图 4、图 6 展示的真实 Playbook 内容：SEM 仅靠粗粒度任务类型字符串（如 `"Amplifier"` 或子串包含）无条件检索规则，且把早期简单任务学到的经验写死为普适指令——例如图 4 中的 **`R1: Define Vdd explicitly (typically 5 V)`**、**`R5: Use robust MOS models: explicitly set key params (vto=0.5, kp=100e-6, lambda=0.01)`**，图 6 中的**强反型饱和区不等式检查（$V_{gs} > V_{th}$）与单调非平坦直流曲线判据**，以及 Eq. (5) 的单变量静态 DC 扫描选偏置机制（物理页 3–4，Eq. (5) 与 Eq. (8)；物理页 8，Fig. 4；物理页 11，Fig. 6）[pdf:E05][pdf:E07][pdf:E13][pdf:E17]。只需构造两类完全标准但跨物理政体的测试题即可令其可预测地崩溃：(1) **超低压（$V_{dd} = 0.6\text{ V}$）亚阈值生物电前置放大器**：由于任务类型同样命中 `"Amplifier"`，Eq. (8) 会把 5V 供电习惯与 Level-1 参数注入上下文，而 Eq. (7) 的 `Filter` 只检查端口名集合 $\Omega$、无法识别供电电压与沟道反型政体冲突；更致命的是，Design Optimizer 写死的 $V_{gs} > V_{th}$ 判据会把合法工作在弱反型区（$V_{gs} < V_{th}$）的放大管全部判为偏置错误，强行抬高栅压导致管子彻底挤入线性区丧失增益。(2) **强正反馈迟滞电路与无静态直流工作点意义的动态闭环系统（如电荷泵 PLL、多谐振荡器）**：Eq. (5) 的 $v_t = \mathcal{B}(\mathcal{D}(c_t))$ 隐含了电路具有单值无记忆静态传输曲线的前提；对存在回滞窗口的施密特/迟滞比较器（双向扫描跳变阈值不同）或必须靠瞬态周期稳态锁相的 PLL，单向直流扫描根本找不到动态工作点——这也直接印证了为何在 Table I（Gemini-2.5-Flash）中，AnalogAgent 在静态放大器（Tasks 1–8）上全数 100.0%，一到振荡器 Task 16（70.0%）、VCO Task 23（73.3%）、比较器 Task 25（53.3%）与混频器 Task 30（60.0%）首轮通过率便大幅滑坡（物理页 6，Table I）[pdf:E10]。

第二，**未被剥离的混杂因素替代解释——SEM 学到的主要是“冷门 PySpice Python 封装语法补丁”而非“模拟电路拓扑设计知识”**。仔细核对图 3（Hard Task 25 的 30 轮演进细节）与 Section 4.4–4.5 的规则案例，Curator 立下头功的高频规则高度集中在 **PySpice 特有的面向对象 API 陷阱**：例如“`Netlist.subcircuit()` 只接受 2 个位置参数而非 5 个”“必须向 `circuit.subcircuit()` 传入 `SubCircuit` 对象实例而非字符串名称（规避 `'str' object has no attribute 'name'`）”“禁止重复注册同名元件 `M3`”（物理页 6–7，Section 4.4 与 Fig. 3）[pdf:E11][pdf:E12]。由于 PySpice 在预训练语料中的占比远低于原生标准 SPICE 文本网表（`.subckt ... .ends`），去掉 AnalogCoder 预置的 Python 辅助工具库后，基座模型（尤其是 1.7B–8B 小模型）大量折戟在 Python 包装器 API 签名猜测上。论文缺少一组最关键的消融对照：**如果直接在所有基线的系统提示词里附上一页 15 行的官方 PySpice API 语法签名速查卡，或者统一改为直接生成标准原生 Ngspice `.sp` 文本网表**，AnalogAgent 依靠跨任务 SEM 取得的 +48.8% 小模型增益与 +21.7% 跨问题迁移增益中，究竟还有多少比例属于真正的电路物理与拓扑构造增益，目前在实验设计上并未被干净剥离。

## § 12 — Follow-up Research Bet

基于全文已暴露但未被开发的两个关键切口——一是 Table III 揭示无精细诊断门控的文本记忆（`w/o MAS, w/ SEM`）会在中等复杂度电路上产生 -8.7 个百分点的跨任务负迁移（物理页 7，Table III）[pdf:E12]，二是前端离散拓扑生成与后端连续参数寻优（Section 3.5 Optuna TPE）处于**单向开环割裂状态**（只有靠拍脑袋初值先碰过 `PASS(c_t)=1` 的电路才能进入 Optuna，而连续寻优卡壳时暴露的物理瓶颈梯度从未回流指导拓扑修改）（物理页 4–5，Fig. 2 与 Section 3.5）[pdf:E06][pdf:E08]——提出如下主研究押注：

### 主研究押注：灵敏度冲突签名驱动与物理政体门控的拓扑-尺寸双向协同演化（Sensitivity-Guided Regime-Gated Co-Evolution）

- **改变的基本设计变量（同时改变三项底层变量）**：
  1. **状态与记忆表示（State Representation）**：废除按粗粒度电路名字符串键控的无条件文本列表（Eq. (8) 与 Fig. 6），改为**以“物理工作政体谓词（供电轨区间 $V_{dd}$、反型区 $g_m/I_D$ 范围、信号域 DC/AC/Transient）+ 连续优化帕累托冲突雅可比签名（Jacobian Conflict Signature）”联合索引的可验证结构化变换算子库**；
  2. **系统边界与控制闭环（System Boundary & Control Loop）**：打破“先过前端布尔 `PASS` 再进后端 Optuna”的单向串行边界，将快速确定性 sizing/工作点投影嵌入每一次拓扑候选评估内部，用连续数值优化器收敛在不可行边界时的**拉格朗日乘子与目标梯度冲突信号**反向触发离散拓扑编辑（如仅当连续调节 $W/L$ 证明增益与带宽梯度恒负内积 $\nabla_w A_v \cdot \nabla_w \text{GBW} < 0$ 且输出阻抗受限于沟道长度调制极限时，才精确触发插入 cascode 管或增益自举支路）；
  3. **评价与验证对象（Evaluation Target）**：从理想 Level-1 模型与人工白盒拓扑脚本下的布尔 `PASS(c)`，转向真实开源工业 PDK（SkyWater SKY130 / IHP SG13G2）多工艺角（PVT corners）黑盒规格下的连续性能品质因数（FoM）帕累托前沿达成率。
- **新研究问题**：在完全没有预设白盒拓扑核查脚本、且黑盒多目标规格超越简单单级拓扑物理极限的真实 Foundry PDK 环境下，如何利用内层连续尺寸优化的局部收敛残差与灵敏度几何结构，自动区分“连续参数未调优”与“离散拓扑容量触顶”，并将拓扑升级操作沉淀为带严格物理适用域边界的可迁移经验？
- **首次使什么成为可能**：首次让无训练电路智能体在仅有终端黑盒性能指标与真实纳米工艺 PDK 模型时，依靠可计算的物理瓶颈证据**自主推演拓扑阶跃**（例如从基本五管差分对平滑演化出套筒式/折叠共源共栅或米勒调零电阻结构），同时彻底阻断高压强反型规则向低压亚阈值或射频动态电路的跨政体误迁移。
- **核心因果机制**：一个拓扑能否满足一组多目标规格，本质上是其可调参数流形在性能空间中的可达集覆盖问题；内层快速数值寻优停留在不可行局部极小点时，活跃约束上的非零对偶乘子与小信号灵敏度矩阵精确指出了哪两个物理指标在哪只器件上锁死，将这一数值不变量编码为记忆检索键与拓扑重写前置条件，就把脆弱的自然语言症状猜测升级为可验证的电路物理因果推理。
- **论文内的具体依据**：(1) Table III 中 `w/o MAS, w/ SEM` 在 Medium 任务上从 64.7% 跌至 56.0% 证实无适用域前提门控的规则检索会引发负迁移（物理页 7，Table III）[pdf:E12]；(2) Eq. (5) 的单变量直流扫描偏置回填已初步印证“在否决拓扑前先做确定性数值对齐”能挽救伪失败结构，但受限于单维静态直流偏置，未能扩展到多维管子尺寸与频域极零点（物理页 3，Eq. (5)）[pdf:E05]；(3) Table I 中多参数耦合的振荡器（Task 16）、PLL（Task 24）、比较器（Task 25）及附录 C 中折叠共源共栅（80.0%）与高摆幅 OTA（88.7%）明显低于单级放大器（100.0%），直接暴露了前端盲猜连续参数与粗粒度字符串检索在复杂耦合拓扑上的上限（物理页 6，Table I；物理页 10，Appendix C）[pdf:E10][pdf:E16]。
- **最大收益与最大科学风险**：最大收益是将 LLM 的离散符号结构组合能力与经典连续优化的对偶几何信息闭环咬合，使本地小模型在真实工业 PDK 黑盒规格下具备零样本拓扑演进能力；最大科学风险是在强非线性瞬态电路（如锁相环或自激振荡器）中，未起振或未锁定状态下的目标函数呈分段平坦或非光滑跳变，导致有限差分/伴随灵敏度失效，且内层快速 sizing 可能放大单步拓扑评估的仿真耗时。
- **区分替代解释的最小实验**：在 SKY130 PDK 上构造 8 档梯度递进的黑盒放大器规格（从单级共源可解递增至必须采用增益自举折叠共源共栅 + 调零补偿才可解，全程屏蔽 `Netlist_check.py` 且不提示拓扑名），在同等总 SPICE 仿真次数预算下对比三组系统：(A) 原版 AnalogAgent（文本过关后才调 Optuna + 字符串键检索）；(B) 给原版前端每个候选配同等预算的内层 Optuna 寻优，但只向 Curator 返回标量成败、不提取梯度冲突签名且无物理政体门控；(C) 灵敏度冲突驱动 + 政体谓词门控协同系统。若 (C) 在高难黑盒规格档位的达标率以及从 `1.8V` 强反型规格切换到 `0.8V` 弱反型规格时的首轮成功率均显著超越 (B) 和 (A)，则确证收益来自“灵敏度几何归因与政体门控”而非额外仿真采样预算。
- **与最近工作的实质差异**：与 AnalogCoder-Pro 及本文 AnalogAgent 把贝叶斯 sizing 孤立放在拓扑验证通过之后的单向后处理不同，也与 AnalogGenie / LaMAGIC 依赖离线网表语料训练拓扑生成网络不同，本方案保持完全零训练，首次将连续优化器的局部对偶冲突几何变成离散多智能体拓扑演进与长程记忆索引的一等公民。

### Wild-card Alternative（一句话不同机制替代路线）

彻底抛弃自然语言规则手册与过程式 PySpice 代码生成，改为在通过验证的 SPICE 网表图上运行**符号子图反统一与程序库学习（DreamCoder 式 Library Learning）**，将反复验证成功的电流镜、偏置支路与级间补偿网络自动抽象为带形式化小信号端口阻抗契约的可组合硬件原语，用静态电气类型检查器替代 LLM 文本规则检索来根除拓扑拼装与连接错误。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Abstract & Section 1 — Motivation, MAS+SEM framework summary, and headline Pass@1 metrics (Gemini 92%, GPT-5 97.4%, Qwen-8B +48.8% to 72.1%)"
[pdf:E02]: <_evidence/E02-p002-page.png> "PDF 物理页 2，Figure 1 & Section 1 — Context attrition on Hard Task 25 (3.8K to 1.4K prompt tokens, ~7 min vs 17.13 s) and three LLM circuit design challenges"
[pdf:E03]: <_evidence/E03-p002-page.png> "PDF 物理页 2，Section 2.1 & Section 2.2 — Fixed-architecture sizing limits, topology search overhead, and prior prompt-driven/trained LLM circuit synthesis"
[pdf:E04]: <_evidence/E04-p003-page.png> "PDF 物理页 3，Section 2.2 & Section 3.1, Eq. (1) — Training-free/library-free positioning and formal task verification criterion PASS(c)"
[pdf:E05]: <_evidence/E05-p003-page.png> "PDF 物理页 3，Section 3.2 & Section 3.3, Eq. (2)–(5) — Code Generator prompt augmentation, Design Optimizer five-stage checks, and DC-sweep bias injection"
[pdf:E06]: <_evidence/E06-p004-page.png> "PDF 物理页 4，Figure 2 — AnalogAgent dual-loop architecture: MAS+SEM functional synthesis loop (Max Attempts = 3) coupled with LLM+Optuna parameter sizing"
[pdf:E07]: <_evidence/E07-p004-page.png> "PDF 物理页 4，Section 3.3 & Section 3.4, Eq. (6)–(9) — Knowledge Curator distillation, conflict-checked Filter/Dedup playbook update, and exact/substring retrieval"
[pdf:E08]: <_evidence/E08-p005-page.png> "PDF 物理页 5，Section 3.5 — LLM-guided tunable parameter extraction and Optuna TPE Bayesian device sizing"
[pdf:E09]: <_evidence/E09-p005-page.png> "PDF 物理页 5，Section 4.1–4.3 — 30-task benchmark setup, Pass@k estimator (n = 30), main comparative findings, and ablation discussion"
[pdf:E10]: <_evidence/E10-p006-page.png> "PDF 物理页 6，Table I & Table II — Per-task Pass@1/Pass@5 across 30 tasks, 5-trial difficulty statistics, ~32.0K tokens, and 1.3 min Time-to-First-Success"
[pdf:E11]: <_evidence/E11-p006-page.png> "PDF 物理页 6，Section 4.4 & Section 4.5 — Hard Task 25 iterative subcircuit/naming error correction and Task 1 netlist grammar acquisition"
[pdf:E12]: <_evidence/E12-p007-page.png> "PDF 物理页 7，Table III & Figure 3 — MAS/SEM orthogonal ablation matrix on Gemini-2.5-Flash and 30-iteration self-improving trajectory on Hard Task 25"
[pdf:E13]: <_evidence/E13-p008-page.png> "PDF 物理页 8，Section 4.5 & Figure 4 — Cross-task transfer of rules R1–R5 from Task 1 to Amplifier Tasks 9 and 10 with token and runtime savings"
[pdf:E14]: <_evidence/E14-p008-page.png> "PDF 物理页 8，Section 4.6 & Figure 5 — Compact open-weight Qwen3 (1.7B/4B-Instruct/8B/14B) Pass@1 and solved-task scaling vs AnalogCoder-Pro"
[pdf:E15]: <_evidence/E15-p009-page.png> "PDF 物理页 9，Section 5 — Conclusion, commercial IC PDK/NDA confidentiality motivation, and future directions on AI assurance"
[pdf:E16]: <_evidence/E16-p010-page.png> "PDF 物理页 10，Appendix A, Appendix B (Algorithm 1), & Appendix C — Experimental hardware setup, MAS-SEM inference pseudocode, and 5 unseen cascode/OTA transfer results"
[pdf:E17]: <_evidence/E17-p011-page.png> "PDF 物理页 11，Table IV & Figure 6 — Full 30-task Easy/Medium/Hard circuit catalog, 5-stage Python/SPICE checker scripts, and JSON Playbook schema in SEM"
