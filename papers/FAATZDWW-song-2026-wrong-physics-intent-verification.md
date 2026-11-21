# Your Simulation Runs but Solves the Wrong Physics: PDE-Grounded Intent Verification for LLM-Generated Multiphysics Simulation Code

- **作者**：Zhenghan Song、Yulong Liu、Cheng Wan、Chenjun Li、Lingfu Liu、Yunyi Li、Congcong Yuan
- **出处**：arXiv 预印本
- **年份**：2026
- **DOI**：10.48550/arXiv.2605.09360
- **Zotero key**：FAATZDWW

> 证据说明：[pdf:E..] 对应源 PDF 物理页与 Eq./Fig./Table 定位。本文区分论文报告的结果、依据公式作出的分析，以及尚未执行的复现实验与研究设想。

## § 1 — 研究问题与重要性

**论文解决的是“生成代码有没有忠实实现所要求的物理模型”，核心贡献是把这种忠实程度变成可计算、可定位、能反馈给生成器的检查。** 作者将自然语言理解与代码实现之间的偏差称为 comprehension–generation gap，并以 MOOSE 多物理有限元平台为对象：脚本可被接受，甚至正常收敛，但漏掉时间导数、用错边界条件或忽略耦合后，求解的问题已经改变（物理页 1，Abstract；物理页 2，Introduction）[pdf:E01][pdf:E02]。

一个直观实例是带孔区域的扩散：孔壁本应无通量，生成器却把它设为吸收边界；两种模型都能生成平滑、看似合理的浓度云图，运行日志无法告诉使用者哪一个符合原始要求。Fig. 1 还展示遗漏源项、异质扩散率变为均质、瞬态变为稳态、初值错误这四种情形（物理页 2，Fig. 1；物理页 12，Appendix A）[pdf:E02][pdf:E10]。这说明真正需要核查的是方程、边界、初值及材料假设与需求的对应关系。

工程价值在于：把“输出像不像正确结果”之前的一道建模检查自动化。MOOSE 的 Kernel 是向弱形式残差贡献一项的对象，BC 对象负责边界约束；这种可组合语义使输入文件能够被还原为一份物理契约，即可逐项核对的数学要求（物理页 3，§3.1；物理页 4，Fig. 2）[pdf:E03][pdf:E04]。论文最有分量的成果是利用这一结构产生确定性诊断；它提供的直接证据集中在受支持表示内的结构一致性。

## § 2 — 前人工作与不足

作者把 MOOSEnger、MechAgents、MetaOpenFOAM 和 AutoFLUKA 作为科学仿真生成系统的代表：这些工作分别推进 MOOSE、多代理力学、CFD 和粒子输运任务，降低了从自然语言启动仿真的门槛。本文对它们的主要批评是验证信号偏重执行结果，不能区分“正确模型的程序”与“容易运行的错误模型”（物理页 3，§2）[pdf:E03]。这个瓶颈来自目标函数：一旦修复动作删除了引起报错但物理上必要的对象，执行指标可以变好，建模质量却下降。论文给出删除应力核、丢失边界和改变时间类别的具体修复案例（物理页 25，Appendix M）[pdf:E21]。主实验比较的是作者构建的 Direct、SpecGen 和修复变体，因此对上述完整系统的评价应理解为验证范式比较，不能写成逐系统复现后的性能排名。

意图验证方面，本文讨论了 VeriCode 式规范翻译、逐步意图 verifier，以及 Terraformer 的策略反馈：这些方法依赖证明义务、模型判断或学习到的策略。作者选择更窄的对象集合，借助已经知道数学语义的 Kernel/BC 映射，把判定转化为离散结构比较（物理页 3，§2）[pdf:E03]。关键取舍是用可审阅的领域映射换取可执行的检查，而非要求 LLM 每次重新判断一个任意程序是否正确。

Self-Refine、Self-Debugging 提供了迭代生成的框架，反馈则来自模型自评或执行信息；本文把反馈替换为“哪个变量缺哪个项、哪个边界类型不符”的机器报告。既有机器可读 PDE 表示主要服务于求解或学习，本工作让表示直接服务于代码审查（物理页 3，§2）[pdf:E03]。因此创新重心是**把领域语义变成生成器外部的检查依据**，而多代理编排、提示词自检和普通错误重试只是实现手段。

## § 3 — 重建作者的思考路径

下面是依据文中线索重建的研究逻辑。首先，一个仿真失败有两种不同来源：程序无法形成合法问题，或者合法地求解了另一个问题。运行日志适合发现前者；对平滑云图的直觉也不足以排除后者。带孔扩散的五组示例使这种区分具体化（物理页 2，Fig. 1）[pdf:E02]。

接着追问：有没有不求完整参考解，也能检查“问题本身是否写对”的入口？若目标平台把方程装配隐藏在任意代码里，这很难；MOOSE 恰好显式声明 Kernel 和边界对象，而每个对象对应已知残差贡献（物理页 3，§3.1；物理页 12，Eq. (6)）[pdf:E03][pdf:E10]。由此可以先枚举激活对象，再还原其数学含义，避开让模型凭语言判断模型自身代码的循环。

然后会遇到另一个问题：还原出来的代码物理与什么比较？自然语言不适合直接逐项匹配，于是先将需求抽成结构化契约，再让生成器按契约实现；相同契约也可供核验器使用。论文以此区分 LLM 抽取的部署参考与专家建立的离线评价参考（物理页 4，§4.1；物理页 5，Fig. 3）[pdf:E04][pdf:E05]。

最后，检测结果必须能指导修改。一个总分不能说明该补时间项还是该改右边界，因此检查器同时输出逐项违反信息；生成器据此局部修正，重新核验。这个推演顺序是“执行信号缺失语义 → 寻找可恢复的对象语义 → 建立共同表示 → 将差异变成编辑指令”，不需要先假定本文的方法一定有效。

## § 4 — 核心 Intuition

仿真器会认真求解你交给它的模型，即使那个模型已经偏离了你的需求。MOOSE 把物理模型拆成有明确数学含义的对象，因此可以从代码反向列出它实际包含的方程项和约束，再与需求契约逐项对照（物理页 4–5，Fig. 2–3）[pdf:E04][pdf:E05]。让 LLM 修改这份“具体差异清单”，就能把修复目标落到缺失的物理项，而不是仅仅消除报错。

## § 5 — 具体方法与完整 Pipeline

### 先回答本次阅读重点

**1）如何界定并量化“能运行但物理错误”？** 论文将执行状态与 Intent Fidelity Score（IFS，物理意图保真评分）分别计量。部署审计把通过 Exec 且 IFS≥0.85 的样本记作 GoodExec，把通过 Exec 且 IFS<0.85 的记作 FalseExec，比例分母均为全部 220 个任务。三种主模型经 execution-only repair 后的 FalseExec 为 40.0%、40.0%、39.1%（物理页 6，§6.2；物理页 7，Table 2）[pdf:E06][pdf:E07]。这里 Exec 的 InitExec2 判据是“正常退出、首次报错前开始求解、或两秒内未出现报错”满足其一，反映短时对象实现与启动状态；完整收敛而物理不同的独立证据来自另外 30 对扰动实验（物理页 22，Table 11；物理页 8–9，§7.1 / Fig. 5）[pdf:E18][pdf:E08][pdf:E09]。

**2）reference-free 实际去掉了什么参考？** 主闭环无需参考场解或参考波形：LLM 从自然语言提取 \(P_{\mathrm{llm}}\)，静态解析器从代码重建 \(P_{\mathrm{code}}\)，确定性比较器检查两份契约。它不从温度、浓度等数值场反演真实物理，也不通过场残差训练模型；场量仅用于独立的数值验证实验（物理页 5，Fig. 3；物理页 13，Algorithm 1；物理页 17，Appendix F）[pdf:E05][pdf:E11][pdf:E14]。部署仍然需要一份数学参考，来源是抽取契约；专家 \(P_{\mathrm{gt}}\) 在生成结束后的 benchmark 评分阶段使用。材料检查 MCS 则额外要求可比参考材料事实，详见 §6。

**3）220 任务如何构建与评价？** MooseBench 从 260 个候选中排除 40 个，保留七个物理家族、三个检查点复杂度层级的 220 个任务；专家先写参考输入，再确定性重建 \(P_{\mathrm{gt}}\)，联合审阅需求、参考输入和契约。三种主模型进行 Direct / SpecGen / PDE-Refine 比较，另外三种模型参与弱模型或跨模型诊断；统计按同任务配对，解析失败计零，错误分类覆盖方程项、BC、IC、系数和时间类别（物理页 6，§5.1 / §6.1；物理页 26，Appendix O / Table 17；物理页 28–29，Tables 20–23）[pdf:E06][pdf:E22][pdf:E24][pdf:E25]。完整统计口径与负结果在 §7 展开。

### 用真实案例走完闭环

Appendix L 的 framework_009 是一维耦合扩散–反应任务：域长 1 m，变量 \(v\) 初值为 10，以 \(0.5\,\mathrm{s}^{-1}\) 衰减，左右端值分别为 10 和 0；变量 \(u\) 初值为零，由局部 \(v\) 以系数 0.5 产生，左端固定为零、右端零通量；模拟 3 s，步长 0.05 s（物理页 24，Appendix L）[pdf:E20]。

1. **意图抽取。** LLM 输出 JSON 契约，列出变量、方程项、边界、初值和时间类别。该例要求 \(v\) 有扩散、时间导数与衰减项，\(u\) 有扩散、时间导数与来自 \(v\) 的耦合源项；两变量的边界不能混用（物理页 24，Appendices K–L）[pdf:E20]。

2. **按规范生成。** LLM 把契约条目实现为 MOOSE 输入对象。SpecGen 到此为止；PDE-Refine 继续接受核验反馈。直接生成在该例漏掉 CoupledForce，并把 \(u\) 右端的 Neumann 零通量边界写成 Dirichlet，报告 IFS 为 0.62（物理页 24，Appendix L）[pdf:E20]。

3. **静态重建。** 解析器读取抽象语法树 AST，枚举 Kernel、BC、IC 和材料块，经映射表转成规范化算子及属性；未知 Kernel 进入未解析集合 \(U\)。这一步由确定性程序完成，不需要 LLM 判断，也不启动数值求解（物理页 13，Algorithm 1；物理页 4，§4.2）[pdf:E11][pdf:E04]。

4. **比较并生成可操作报告。** 核验器先对齐变量，再报告“变量 \(u\) 缺耦合项”和“\(u\)/right 边界类型不符”。报告使用候选代码中的变量名，使修改能定位到具体代码；该例一次修复后补齐 CoupledForce 并改回 Neumann，IFS 升至 0.98，作者将剩余差异归于系数容差问题（物理页 5，§4.4；物理页 25，Appendix L）[pdf:E05][pdf:E21]。

5. **停止与输出。** 最多两轮 refinement，内部 IFS 达到 0.85 即停止；regression guard 保留内部得分更好的候选。到达轮数上限也会结束，因此“输出文件”与“通过阈值”须分别记录。最终产物是 MOOSE 输入及其契约差异；MOOSE 的实际求解与执行审计承担另外的验证职责（物理页 6，§6.1；物理页 13，Appendix C；物理页 22，Table 11）[pdf:E06][pdf:E11][pdf:E18]。

### 各模块的职责边界

| 模块 | 输入与输出 | 实际承担的判断 |
|---|---|---|
| LLM extractor | 自然语言 → \(P_{\mathrm{llm}}\) | 解释需求、选取物理项和参数 |
| LLM generator / refiner | 契约、代码、违反报告 → 新代码 | 选择对象并完成离散编辑 |
| 确定性 parser / verifier | AST、语义映射 → \(P_{\mathrm{code}}\)、IFS、差异 | 在覆盖范围内检查契约一致性 |
| object-realization registry | 对象块 → 可实例化对象配置 | 参数解析、材料连接、缺省块与最小类型修复 |
| MOOSE | 输入文件 → 执行状态或数值场 | 装配与求解实际写入的模型 |

表中分工来自系统描述与 registry 定义（物理页 13，Appendix C；物理页 21，Appendix H.1）[pdf:E11][pdf:E17]。尤其要分清：文中没有一个替 LLM 完成任意 PDE 等价证明的通用符号求解器；其数学知识主要固化在语义映射表中。registry 在两种部署审计方法之间冻结，用来控制对象实现基础设施的差异。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 为什么对象能还原为方程：从弱形式看装配

作者用无重力 Darcy 压力方程作例子：

\[
-\nabla\cdot\left(\frac{K}{\mu}\nabla p\right)=0.
\]

这里 \(p\) 是压力，\(K\) 是渗透率，\(\mu\) 是黏度。乘以测试函数 \(\psi\) 并在域内积分，分部积分得到

\[
\int_{\Omega}\nabla\psi\cdot\frac{K}{\mu}\nabla p\,\mathrm d\Omega
-\int_{\partial\Omega}\psi\left(\frac{K}{\mu}\nabla p\cdot n\right)\mathrm d\Gamma=0.
\]

体积分对应 Kernel 的残差贡献，边界部分由边界条件处理；这正是代码对象到物理项的可追踪接口（物理页 12，Appendix B / Eq. (6)；物理页 3，Eq. (1)）[pdf:E10][pdf:E03]。原文 Listing 1 用 DarcyFluxPressure，以及左右端定压 BC 和材料参数说明输入结构（物理页 12，Listing 1）[pdf:E10]。算法实际装配的是弱形式贡献，而不是根据代码注释猜测控制方程。

### 6.2 契约保留什么，比较器真正使用什么

论文定义

\[
P=(\mathcal T,\mathcal B,\mathcal I,\mathcal C,S,\Omega),
\]

分别表示方程项、边界条件、初值、系数/材料事实、时间类别与域（物理页 4，Eq. (3)）[pdf:E04]。一个绑定方程项写为

\[
t=(v,o,\alpha),
\]

其中 \(v\) 是被作用的变量，\(o\) 是规范化 PDE 算子类型，\(\alpha\) 是系数；原文用 \(\bot\) 表示未显式指定或恒为一的单位系数（物理页 19，Definition G.3 / Eq. (12)）[pdf:E15]。

映射表还记录弱式描述符 \(d(o)=(\tau,\phi,\gamma)\)：\(\tau\) 描述试探侧操作，\(\phi\) 描述测试函数侧操作，\(\gamma\) 描述两者怎样相乘或缩并。对应集合大小为 8、4、3，试探侧包括 identity、grad、div、curl、ddt、ddt2、stress、strain（物理页 19，Eqs. (8)–(11)）[pdf:E15]。**运行时匹配使用算子类型 \(o\)，描述符用于审阅映射表的结构依据。** 它没有在每次评分时比较任意弱式表达式的代数等价性（物理页 20，Remark G.2）[pdf:E16]。

映射表的弱式说明覆盖 benchmark 真值中 762/766 个 Kernel–term 实例，即 99.48%；BC 与 IC 映射分别含 16 与 21 项（物理页 15，Table 6 表注；物理页 19，Definition G.4）[pdf:E13][pdf:E15]。这是该基准上的实例覆盖率，不能换算为对 MOOSE 全部对象或未来自定义模型的覆盖率。未映射对象被记入 \(U\) 并从 IFS 计算中排除（物理页 4，§4.2；物理页 13，Algorithm 1）[pdf:E04][pdf:E11]。

时间信息也需要按实现读取：Algorithm 1 仅检查 Executioner.type 是否为 Transient，随后将 \(S\) 标为 TRANSIENT 或 STEADY（物理页 13，第 2 行）[pdf:E11]。因此本文已经展示的是瞬态/稳态类别核验，不能据此认定步长、积分公式阶数和多速率同步也已被核验。域 \(\Omega\) 虽进入契约，主要评分和定理列出的维度没有给出完整几何等价判据（物理页 4，Eq. (3)；物理页 21，Theorem G.2）[pdf:E04][pdf:E17]。

### 6.3 对齐、匹配与 IFS

不同代码可能把同一物理量命名为不同变量。作者先用每个变量的算子签名对齐：

\[
\sigma(v)=\operatorname{sort}\{o_i:t_i\text{ 作用于 }v\}.
\]

签名相同时，再用边界名称、值与系数消歧；在对齐后的名称上比较项（物理页 20，Variable alignment procedure）[pdf:E16]。这避免了单纯改名造成假错误，但对称多变量系统中的身份辨识仍依赖签名之外的信息。

直接系数的匹配条件为

\[
v_{\rm ref}=v_{\rm cand},\qquad
o_{\rm ref}=o_{\rm cand},\qquad
\frac{|\alpha_{\rm ref}-\alpha_{\rm cand}|}
{\max(|\alpha_{\rm ref}|,\epsilon_0)}
\le \delta_{\rm coef}.
\]

\(\epsilon_0\) 防止参考值为零时除零，默认 \(\delta_{\rm coef}=0.1\)，即以参考值为尺度的相对容差（物理页 20，Eq. (14)）[pdf:E16]。该谓词一般不对称、不传递；它是“候选是否落入参考允许范围”的判定，不能当作数学等价关系使用。

令 \(Q(P_{\rm ref})\) 为参考契约诱导的检查项集合，\(w_j>0\) 为重要性权重，则

\[
\Delta_{\rm phys}
=\frac{\sum_{j\in Q(P_{\rm ref})}
w_j\,\mathbf1[\operatorname{fail}_j(P_{\rm ref},P_{\rm cand})]}
{\sum_{j\in Q(P_{\rm ref})}w_j},
\qquad
\mathrm{IFS}=1-\Delta_{\rm phys}.
\]

这个分数回答“参考检查项中，有多少重要性权重通过了”，没有把解场误差转换成概率或精度（物理页 5，Eqs. (4)–(5)）[pdf:E05]。作者给时间/惯性项、主导算子、耦合或 BC/IC 类型、数值变化、缺源项和非物理元数据分别赋权 4、3、2、1、0.7、0.5（物理页 20，Table 10）[pdf:E16]。这是一套典型影响的工程先验：例如源项的权重较低，不代表源项主导场景中漏源一定只产生小误差。

三个定理的保证都相对于表示与映射成立：正确映射重建覆盖项；IFS=1 表示已定义的检查谓词全部通过；某个被表示的检查项不符会使 IFS 下降（物理页 20–21，Theorems G.1–G.3）[pdf:E16][pdf:E17]。因此有效性链条必须同时包含“参考契约正确”“映射与检查点充分”和“候选通过检查”，不能只读取最后一个分数。§11 进一步给出集合去重与 G.1 计数结论之间的具体矛盾。

### 6.4 材料诊断 MCS 与真正的场误差

IFS 能检查契约中直接表示的系数，但复杂材料链里的幅值与本构信息可能未进入结构检查。作者为可比较的系数/材料事实集合 \(F\) 定义 Material Consistency Score：

\[
\mathrm{MCS}(c_{\rm ref},c_{\rm cand})
=\frac{1}{|F_{\rm ref}|}
\sum_{f\in F_{\rm ref}}
\mathbf1\!\left[
\exists g\in F_{\rm cand}:
\operatorname{key}(g)=\operatorname{key}(f)
\land\operatorname{value}(g)\approx\operatorname{value}(f)
\right].
\]

标量按参考相对容差比较，材料模型签名按规范化后的类别比较；没有可比参考事实时，MCS 未定义（物理页 17，Definition F.1 / Eq. (7)）[pdf:E14]。它仍需要参考材料事实。文中公式以参考文件为输入，没有单独证明任意部署需求都能自动提供可信的参考材料链。

独立扰动试验才使用数值场：

\[
E_{L^2}
=\frac{\|u_{\rm pert}-u_{\rm gt}\|_2}
{\max(\|u_{\rm gt}\|_2,10^{-15})},
\]

其中两向量是相同输出网格上的最终场拼接值（物理页 17，Appendix F）[pdf:E14]。这解释了两个容易混淆的结论：主方法可以不求参考场而给出结构差异；证明结构差异确实会改变物理解的实验，仍借助参考仿真场。Fig. 5 中高 IFS 与大场误差并存，正好展示结构评分和数值影响之间的边界（物理页 9，Fig. 5）[pdf:E09]。

## § 7 — 实验设计与结论

### 7.1 基准从哪里来，难度如何定义

MooseBench 最终含 220 个任务，来自 260 个候选、排除 40 个后的 clean set。每条自然语言需求对应专家参考输入，再用同一重建器产生 \(P_{\mathrm{gt}}\)；审核同时查看需求、参考输入与契约，以检查算子覆盖、边界/初值、材料、时间和提示泄漏（物理页 6，§5.1；物理页 22，Table 11；物理页 26–27，Appendix O）[pdf:E06][pdf:E18][pdf:E22][pdf:E23]。PDF 没有逐项展示被排除任务及理由，因而仅凭正文不能审计筛选是否偏向现有映射可处理的任务。

| 物理家族 | 任务数 |
|---|---:|
| 瞬态热传导 | 66 |
| 稳态热传导 | 36 |
| 热–流 TH 多孔介质耦合 | 30 |
| 线弹性 | 28 |
| 热–流–力 THM 多孔介质耦合 | 20 |
| 塑性 | 20 |
| 相场 | 20 |
| 合计 | 220 |

家族数量来自物理页 26 的 Table 17 [pdf:E22]。Simple、Medium、Complex 分别按检查项数 ≤4、5–8、≥9 划分，而非按某模型失败率划分；依据 Fig. 9 标注的逐格样本数相加，本卡计算得到三层分别为 55、90、75 个任务（物理页 26，Appendix O；物理页 31，Fig. 9）[pdf:E22][pdf:E27]。热传导占据较大部分，因此家族结果比单一总平均更能揭示外推范围。

原文声明提示不直接泄漏 MOOSE 对象名，所有 220 个真值契约均通过自比较 IFS=1（物理页 27，Appendix O）[pdf:E23]。自比较检验重建表示的自洽性；参考模型是否忠于需求，仍要由前述联合人工审核承担。

### 7.2 模型、方法和统计协议

主标准 sweep 使用 Claude Sonnet 4.6、GPT-5.4、DeepSeek V4 Flash 三种模型，每种模型均比较 Direct、SpecGen、PDE-Refine。GPT-4.1-mini 是弱模型案例；附录另用 Claude Haiku 4.5 与 Gemini 3.1 Flash Lite，全文出现六种模型，但六者没有同时进入主结果表。温度设为 0，最多两轮修复，内部阈值 0.85，系数容差 0.1（物理页 6，§6.1；物理页 22，Table 11；物理页 29，Tables 22–23）[pdf:E06][pdf:E18][pdf:E25]。

标准比较回答两个问题：先写物理契约是否有帮助，增加确定性差异反馈是否进一步有帮助。部署审计另固定 registry，对比 Exec-Repair+Reg 与 PDE-Reg；官方文档检索是独立控制支线。不同设置下的数字需要在各自 sweep 内比较（物理页 6，§6.1；物理页 21–23，Appendix I）[pdf:E06][pdf:E17][pdf:E19]。

IFS 对全部任务取无条件均值，解析失败记为 0。均值区间使用 case ID bootstrap；方法差异按同任务配对，Wilcoxon signed-rank 检验剔除零差值，GoodExec/FalseExec 作为任务级比例统计（物理页 7，Table 1；物理页 22，Table 12；物理页 23，Appendix I）[pdf:E07][pdf:E18][pdf:E19]。论文未报告 pass@k，也未给完整 API 调用总数或多随机种子复跑次数；按主表设计可算出 3×3×220=1,980 个最终得分观测，但它们不是 1,980 次独立同成本采样。

### 7.3 契约与修复带来多大收益

下面主表保留原文均值及 95% bootstrap 半宽（物理页 7，Table 1）[pdf:E07]。

| 模型 | Direct | SpecGen | PDE-Refine |
|---|---:|---:|---:|
| Claude Sonnet 4.6 | 0.744±0.032 | 0.800±0.023 | 0.816±0.021 |
| GPT-5.4 | 0.756±0.033 | 0.769±0.028 | 0.802±0.025 |
| DeepSeek V4 Flash | 0.599±0.048 | 0.668±0.045 | 0.782±0.031 |

PDE-Refine 对 Direct 的配对平均增益分别为 +0.072、+0.046、+0.183，对应 \(p=0.002、0.003、6.4\times10^{-11}\)；GPT-5.4 的 SpecGen 单独比较 \(p=0.167\)（物理页 22，Table 12）[pdf:E18]。据主表印刷均值作差，确定性修复相对 SpecGen 的额外收益约为 0.016、0.033、0.114。由此看，Sonnet 的较大部分收益在契约生成阶段已经取得，DeepSeek 对后续差异反馈更敏感；不能把 Direct→PDE-Refine 的全部提升都归给 verifier。

“hard cases”另按各模型自身 Direct IFS<0.7 定义，与 Complex 层不是同一分组。Sonnet 为 84 例、增益 +0.273；GPT-5.4 为 67 例、+0.219；DeepSeek 为 108 例、+0.414。GPT-4.1-mini 的 197 例、+0.406 来自 registry 的 PDE-Reg 设置（物理页 22，Table 13）[pdf:E18]。摘要的约 +0.22 至 +0.41 是这些低基线子集的条件收益，不能替代全部任务上的平均增益。阈值换成 0.6 或 0.8 后，所列模型的增益仍为正，但样本组成与收益幅度一起变化（物理页 23，Table 14）[pdf:E19]。

### 7.4 “能运行但物理不符”到底占多少

在同一冻结 registry 下，主审计结果如下；每个百分比均以 220 个任务为分母，IFS 是全任务均值（物理页 7，Table 2；物理页 29，Fig. 8）[pdf:E07][pdf:E25]。

| 模型 | 方法 | IFS | Exec | GoodExec | FalseExec |
|---|---|---:|---:|---:|---:|
| Sonnet 4.6 | Exec-Repair+Reg | 0.753 | 83.2% | 43.2% | 40.0% |
| Sonnet 4.6 | PDE-Reg | 0.854 | 91.4% | 60.0% | 31.4% |
| GPT-5.4 | Exec-Repair+Reg | 0.757 | 82.3% | 42.3% | 40.0% |
| GPT-5.4 | PDE-Reg | 0.839 | 86.8% | 56.8% | 30.0% |
| DeepSeek V4 Flash | Exec-Repair+Reg | 0.626 | 74.1% | 35.0% | 39.1% |
| DeepSeek V4 Flash | PDE-Reg | 0.824 | 87.7% | 60.0% | 27.7% |

主模型的 GoodExec 均增加，FalseExec 均下降；PDE-Reg 后仍有 27.7%–31.4% 的全部任务落在 FalseExec。这个结论使用 §5 定义的短时启动状态和 IFS 阈值，不是对全部输出逐个进行物理场验真后的错误率。

独立的 30 对扰动实验覆盖结构项、边界值和系数错误，两版仿真均运行并收敛，再比较最终场 \(E_{L^2}\)。结果显示执行检查无法区分这些错误；系数错误尤其可能处于高 IFS、大场误差区域（物理页 8–9，§7.1 / Fig. 5）[pdf:E08][pdf:E09]。这组实验直接支持“收敛不等于意图正确”，但不能替部署审计中的每个样本提供收敛保证。

弱模型扩展也不支持“所有模型均降低 FalseExec”的笼统说法：Gemini 3.1 Flash Lite 的 GoodExec 从 23.6% 升到 55.9%，FalseExec 却从 28.2% 升到 29.1%（物理页 29，Table 22）[pdf:E25]。当更多原先不能启动的任务变为可启动任务时，错误可执行样本的绝对占比仍可能增加。

### 7.5 静默错误分类与材料盲点

Table 4 的分析对象是四个 Direct sweep 中 766 个“成功解析但不完美”的输出，不能与映射覆盖统计中的 766 个真值 Kernel–term 实例混淆。互斥分类及其均值如下（物理页 8，Table 4）[pdf:E08]。

| 错误组合 | 比例 | 平均 IFS |
|---|---:|---:|
| 仅结构项错误（term/time/IC） | 7.4% | 0.60 |
| 仅 BC 错误 | 14.4% | 0.74 |
| 结构与系数错误 | 32.8% | 0.64 |
| 混合结构错误 | 32.9% | 0.25 |
| 仅系数/材料错误 | 12.5% | 0.94 |

前四类合计 87.5%，包含结构检查可以发现的部分；最后一类平均 IFS 仍为 0.94，暴露了材料链与数值系数对结构评分的逃逸。这个 87.5% 是该 cohort 的分类覆盖，不能解释为对任意物理错误的通用检出率（物理页 7–8，§6.3 / Table 4）[pdf:E07][pdf:E08]。

Table 20 则用可重叠标签逐模型统计：Sonnet、GPT-5.4、GPT-mini、DeepSeek 的 BC 错误比例依次为 56%、60%、80%、66%，缺失/额外 Kernel 为 35%、25%、87%、40%；缺 IC 均为 1%。BC 错误 cohort 有 578 个输出，其中仅 19.0% 是孤立 BC 错误（物理页 28，Tables 20–21）[pdf:E24]。这解释了修一个边界未必就修好了整个模型，也说明这些标签不能简单相加当作总错误率。

最有启发的负结果藏在 Table 26：Sonnet 的 coefficient 子评分从 Direct 的 0.737 降到 PDE-Refine 的 0.485；DeepSeek 从 0.688 降到 0.537，同时各自的总 IFS 上升（物理页 30，Table 26）[pdf:E26]。因此总分改进主要反映结构项和 BC 的收益，不能据此推导材料参数也同步改进。

MCS 的独立调查使用 GPT-5.4 抽取、DeepSeek 生成的 220 个输出，其中 176 个具备可比事实，32 个表现为高 IFS/低 MCS；从中选取的 22 个代表性修复案例，平均 MCS 从 0.316 提高至 0.985，IFS 从 0.959 提高至 0.987，21/22 个达到 MCS=1（物理页 19，Table 8）[pdf:E15]。这支持“显式材料差异可以成为有效修复信号”，证据范围是可比事实和选定修复样本。

### 7.6 哪些消融支持机制，哪些混杂仍未排除

**权重敏感性。** 把结构检查点改成均匀权重后，PDE-Refine 相对 Direct 的增益仍为 Sonnet +0.058、GPT-5.4 +0.021、DeepSeek +0.107，95% bootstrap 区间分别为 [0.041,0.076]、[0.005,0.037]、[0.076,0.139]（物理页 27，Table 18）[pdf:E23]。这说明正向收益不完全由专家 severity 权重造成；该消融把系数/材料另交 MCS，因此没有证明所有物理维度都得到改善。

**文档控制。** DeepSeek 的 DocsDirect 达到 IFS=0.672；Docs+ExecRepair 的 Exec 为 74.1%、FalseExec 为 38.2%、IFS 为 0.660；Docs+PDE-Reg 的对应值为 87.3%、28.6%、0.816（物理页 7，Table 3）[pdf:E07]。检索限定官方对象文档，最多八片段、6000 字符，排除 benchmark 参考输入与答案记录（物理页 14，Appendix D）[pdf:E12]。这些结果削弱了“提升完全来自多看文档”的解释。

**反馈源与预算。** 同 registry 控制了对象实现基础设施，但两条生成路径仍不同：PDE-Reg 先抽契约再生成，execution repair 从 Direct 出发，提示也分别强调定向最小修改与一般性修复。文档支线明确只有一轮 runtime-log repair，而 PDE refinement 最多两轮；PDF 没有给出等调用或等 token 成本的完整对照（物理页 14，Appendix D；物理页 24–25，Appendices K–M；物理页 22，Table 11）[pdf:E12][pdf:E20][pdf:E21][pdf:E18]。所以实验支持这套物理反馈流程的总体效果，尚不能把全部增益唯一归因于反馈源这一项变量。

**契约能否跨模型。** 独立 mixed-model sweep 中，GPT-5.4 抽取→DeepSeek 生成达到 0.772，介于 DeepSeek 自用的 0.765 与 GPT 自用的 0.792；Gemini 抽取→DeepSeek 达到 0.784（物理页 29，Table 23）[pdf:E25]。可交换的契约接口有用，但强 extractor 没有使弱 generator 自动达到强模型全流程水平。这些数字来自单独诊断，不与主表混作同一次实验。

**跨 DSL。** UFL/FEniCS、FreeFEM、FiPy、Devito 的扩展是静态解析概念验证，没有执行这些生成程序。FreeFEM/FiPy/Devito 合计 27 个文档来源任务，Direct/PDE-Refine 均值为 0.815/0.899，其中八个 hard 样本平均增益为 +0.262（物理页 8，Table 5 / §6.4）[pdf:E08]。表中 Deploy 按 Direct IFS<0.7 选择流程，却未明确门控分数的参考来源，因此它不足以证明真实部署中已经能无真值地选择最优生成路径。

### 7.7 已核实的图表一致性问题

物理页 28 的 Fig. 7 中，蓝色 GT IFS 的印刷点标为 **0.705→0.766→0.771**，橙色内部 IFS 为 **0.666→0.766→0.786**；图注却把 GT IFS 写为 **0.715→0.782→0.786** [pdf:E24]。这是渲染页上可见的图文冲突。本卡只采用“一次修复贡献主要增益、第二次收益较小”的共同定性趋势，不从冲突数字推导精确收敛改善幅度。

另按 Table 24–25 的家族数量加权，本卡计算 GPT-mini 的 PDE-Reg 均值约为 0.6964、Exec-Repair+Reg 约为 0.3652，与 Table 22 的 0.703、0.346 不一致，差异超过三位小数舍入范围（物理页 30，Tables 24–25；物理页 29，Table 22）[pdf:E26][pdf:E25]。三种主模型的主表仍给出一致的总体改善方向；弱模型家族表和汇总表的差异需要原始任务级结果才能澄清。

综合这些证据，可靠结论是：明确契约与确定性差异反馈能提高所覆盖模型的结构保真度，并减少三种主模型的低保真可启动输出；完整物理解的正确率、系数改善程度和真实部署契约可靠性需要分别测量。

## § 8 — Take-aways

### 5 句话版

仿真程序成功启动或收敛，仍可能实现了错误的方程、边界或初值，论文用带孔扩散与收敛扰动实验展示了这种断层（物理页 2，Fig. 1；物理页 9，Fig. 5）[pdf:E02][pdf:E09]。本文利用 MOOSE 对象的可组合弱式语义，从代码静态重建契约并进行确定性比较（物理页 4–5，§4 / Fig. 3）[pdf:E04][pdf:E05]。在三种主模型的 220 任务比较中，PDE-Refine 均提高平均 IFS，低 Direct 分数任务的收益更大（物理页 7，Table 1；物理页 22，Table 13）[pdf:E07][pdf:E18]。高 IFS 仍可能伴随系数错误或大场误差，MCS 只能在有可比材料事实时补充诊断（物理页 9，Fig. 5；物理页 17，Eq. (7)）[pdf:E09][pdf:E14]。最应继承的是可审阅契约、确定性差异和定向修复之间的接口，同时独立检验契约来源与表示保留的信息。

### 3 句话版

把代码执行与物理意图匹配分开测量，才能看到普通运行检查遗漏的建模错误（物理页 7，Table 2；物理页 9，Fig. 5）[pdf:E07][pdf:E09]。由代码对象反向重建方程结构，可以为 LLM 提供具体修复指令，并提高基准上的平均结构评分（物理页 13，Algorithm 1；物理页 7，Table 1）[pdf:E11][pdf:E07]。它的工程可信度最终取决于参考契约是否正确，以及重要动力学差异是否进入比较表示。

### 1 句话版

这篇论文最值得带走的方法是：把“代码实现了哪些物理要求”做成独立、可定位的检查，再用具体差异驱动修复（物理页 5，Fig. 3）[pdf:E05]。

## § 9 — 最脆弱的假设

**唯一最关键的假设是：部署时抽出的 \(P_{\mathrm{llm}}\) 忠实表达了用户真正要求的物理问题。** 整个确定性闭环以它为参考；如果 extractor 把对流边界理解成定温，或者漏掉某个耦合场，后续程序可以越来越精确地实现错误契约。此时内部 IFS 的改善反映实现一致性，却无法修复被提前丢失的需求（物理页 4–5，§4.1 / Fig. 3）[pdf:E04][pdf:E05]。

论文提供的支持是 Fig. 4(a) 中抽取质量与最终代码质量的关联，以及跨模型传递契约仍能产生改进的实验；同时，两者关系也表明 extractor 错误会影响下游（物理页 9，Fig. 4；物理页 29，Table 23）[pdf:E09][pdf:E25]。benchmark 刻意使用良定、明确给出物理条件的提示，使这条假设处在较有利的环境中（物理页 26–27，Appendix O）[pdf:E22][pdf:E23]。

最欠缺的证据是：在自然语言出现省略、指代、多种合理边界解释或错误抽取时，系统怎样独立确认“参考契约本身正确”。最低成本的检验是固定同一正确代码与用户需求，只改变抽取契约的一个关键条件，看修复是否主动破坏原本正确的模型。它直接测量误导性参考造成的失败代价，而无需扩大模型或任务规模。

## § 10 — 最小复现实验

**一周目标：拆开验证“确定性差异反馈有效”与“只是在追随给定契约”这两件事。** 选用 Appendix L 的两变量扩散–反应案例作为唯一物理任务，保留其边界、初值与时间设置；不必复现全部七个家族和六种模型（物理页 24–25，Appendix L）[pdf:E20][pdf:E21]。以下步骤与阈值是本卡提出的实验设计，尚未执行。

1. **第 1–2 天：建立独立正确基线。** 人工确认数学模型与 MOOSE 输入，完成整个时间区间的求解，并用一维有限差分实现交叉检查。网格、步长及求解器配置固定；先确认两种实现的目标场误差低于 1%，将它作为本实验的数值容差。

2. **第 3 天：构造少量可控错误。** 做六份候选：漏耦合项、右端零通量改为定值、材料系数缩小十倍，以及对应的三份无物理变化的代码重排/对象重命名控制。另保留一份完全正确代码，用于“错误契约诱导破坏”的试验。只实现涉及这些对象的解析与检查。

3. **第 4–5 天：公平比较反馈。** 从同一损坏文件出发，用同一个 LLM、同一最多两次修改预算、相同“最小编辑”提示，分别提供完整运行日志、结构违反报告、结构加材料事实报告；抽取阶段先使用人工确认的同一契约，避免把额外抽取调用混入反馈效果。每份保留调用数、token 和墙钟时间；本实验不使用 best-of-k 挑选。

4. **第 6 天：攻击参考契约。** 将正确契约中的耦合项人为删去，输入原本正确代码，观察系统是否把正确项当成 extra term 删掉。再追加 §11 的重复扩散 Kernel，直接检查实际重建结果是否保留重数，区分论文形式化缺口与发布实现行为。

5. **第 7 天：同时报告语义和数值指标。** 列出解析成功、全时段运行收敛、term/BC/coeff 各项正确性、内部 IFS、专家契约 IFS 与最终场相对误差；人工基准和独立离散求解只用于实验评分，不传给 LLM。

支持核心机制的结果是：在正确契约条件下，结构报告能定位并修复缺项与错边界，恢复独立数值基线，且不破坏代码重排控制；材料诊断是否消除系数型误差单独统计。若结构反馈在相同起点和预算下不优于日志反馈，其独立机制收益就缺少支持。若内部 IFS 上升而专家契约评分或数值误差恶化，或者错误契约稳定诱导破坏正确代码，则证伪“内部高分足以保证用户物理意图正确”的扩大解释。

## § 11 — 最强反例设计

**攻击：把一个已覆盖的 Diffusion Kernel 复制一份，只改对象块名称，变量、参数、作用域全部保持相同。** 这不依赖未登记的自定义对象。Table 6 明确每个 Diffusion 贡献 \((\nabla\psi,\nabla u)\)，因此两份激活对象在实际装配中叠加（物理页 16，Table 6，Diffusion 行）[pdf:E28]。

论文 Algorithm 1 却写为集合操作

\[
\mathcal T\leftarrow\mathcal T\cup\{(v_\kappa,o_\kappa,\alpha_\kappa)\}.
\]

两个同样的三元组在集合中只留下一个；Definition G.7 也把 \(\mathcal T\) 定义为集合，而 Theorem G.1(c) 声称项数等于覆盖的激活 Kernel 数量（物理页 13，Algorithm 1 第 8 行；物理页 20，Definition G.7 / Theorem G.1）[pdf:E11][pdf:E16]。**按文中写出的集合表示，去重与该计数结论存在直接矛盾。**

把它落到一个可解析的无量纲例子。本卡构造

\[
\partial_tu-\partial_{xx}u=0,\quad x\in(0,1),\qquad
u(0,t)=u(1,t)=0,\qquad u(x,0)=\sin(\pi x).
\]

参考输入只有一个扩散 Kernel；重复后的真实方程为 \(\partial_tu-2\partial_{xx}u=0\)。两者解析解分别为

\[
u_{\rm ref}=e^{-\pi^2t}\sin(\pi x),\qquad
u_{\rm dup}=e^{-2\pi^2t}\sin(\pi x).
\]

在 \(t=1/\pi^2\) 时，本卡计算得到相对 \(L^2\) 误差

\[
\frac{\|u_{\rm dup}-u_{\rm ref}\|_2}{\|u_{\rm ref}\|_2}
=1-e^{-1}\approx63.2\%.
\]

两套问题均良定，差异来自真实扩散作用翻倍；按集合去重逻辑却会得到相同的项表示。这同时挑战“对象清单足够区分物理”和 G.1 的书面证明，而非泛泛抱怨某个模型太难。

**判定边界明确：以上是数学构造，尚未运行作者发布代码。** 若实现实际保留多重集、对象身份，或先按作用域聚合贡献系数，反例可以被检出，需修正的是论文形式化；若实现也去重且返回满分，则是覆盖范围内部的实际漏检。最小验证只需这两个输入、一次重建比较和一组短瞬态，不需要重新跑 220 例。

## § 12 — Follow-up Research Bet

### 主押注：用可控试探场核验实际装配的残差作用

**新研究问题是：不依赖参考收敛场，能否识别“同一算子清单、不同真实动力学”的生成错误，并接受“代码写法不同、实际算子等价”的实现？** 本文的自由度来自可组合的弱式残差：每个 Kernel 已有可解释的作用，而当前运行时比较主要停留在算子类型与属性（物理页 15–16，Table 6；物理页 19–20，Definitions G.2–G.8）[pdf:E13][pdf:E28][pdf:E15][pdf:E16]。

押注同时改变三项设计变量。**状态表示**从 \((变量,算子类型,系数)\) 集合改成保留项重数、源/目标变量、作用子域和材料依赖的残差图。**可控变量**从仅修改代码扩展为主动选择输入试探场与边界激励。**评价对象**从检查项加权通过率改成“实际程序对同一试探场装配出的残差是否符合可审阅的数学规范”。它将首次在这个研究设定中把等标签、异作用的错误纳入直接核查范围，避免以对象名相同代替算子作用相同。

因果机制如下：从人工确认的弱式规范独立构造参考残差算子 \(R_{\rm spec}\)，通过目标求解器的装配接口取得候选程序的 \(R_{\rm code}\)，在共同网格与积分规则下输入同一批试探场 \(z^{(k)}\)，比较 \(R_{\rm code}(z^{(k)})\) 与 \(R_{\rm spec}(z^{(k)})\)。试探场可包含常量、局部变化、单变量激励和不同幅值；重复项会改变响应幅度，错接耦合会改变被激励的残差分量，错绑子域会改变响应位置。这里需要可信数学规范，但无需先求一条参考时间轨迹。

论文给出两条实证动机。Fig. 5 显示高 IFS 仍可伴随较大场误差；Table 26 显示总分提高时 coefficient 子评分可能下降（物理页 9，Fig. 5；物理页 30，Table 26）[pdf:E09][pdf:E26]。加上 §11 的重数问题，这些线索共同指向一个缺口：对对象与事实的抽象比较，未必保留装配后对状态的实际作用。MCS 已证明更具体的材料事实能指导修复，但它依赖事实可提取；残差试探进一步针对那些不易静态展开的材料与耦合路径（物理页 17，Eq. (7)；物理页 19，Table 8）[pdf:E14][pdf:E15]。

**最大收益**是把核验推进到求解器实际组装的离散物理，既能发现重数、耦合和材料作用错误，又有机会接受不同对象组合实现的同一算子。**最大科学风险**是有限试探场对非线性、历史相关材料只提供局部信息，可能遗漏未激发的错误；同时若参考残差与候选使用同一条有缺陷的转换链，差分结果会共同出错。因此最小实验中的参考算子应采用独立实现，并明确测试状态范围。

最小区分实验使用同一两变量扩散–反应系统，构造重复 Kernel、耦合源变量交换、子域绑定交换三类等标签错误，再加入代数等价重写作为阴性控制。固定模型、代码起点、反馈轮数与预算，比较原 IFS、丰富残差图的静态比较、以及残差图加试探响应三个版本；报告错误检出、等价重写误报、修复后的独立场误差与装配开销。若静态丰富表示已解决全部错误，收益来自表示；只有试探响应进一步识别材料链或装配行为错误，才支持主动残差核验这条机制。试探模式逐步增加时若性能仍无法稳定，则应收缩可验证的状态范围，而不是靠提高总分掩盖漏检。

相对于本文及其讨论的近期系统，这项押注的实质变化清楚：MOOSEnger 等系统重在生成与执行，PDE-Refine 重在规范化对象结构比较，MCS 重在显式材料事实；本押注把可控输入下的实际残差作用作为判别对象（物理页 3，§2；物理页 17，Definition F.1；物理页 19–20，算子表示）[pdf:E03][pdf:E14][pdf:E15][pdf:E16]。对 EMT 实时仿真的迁移设想，是把相同思路用于节点方程与离散元件更新残差，验证耦合关系和更新作用；这属于下一项研究设计，不是本文已经给出的结果。

**Wild-card alternative：**转向生成之前的意图辨识，自动找出自然语言中会导向不同物理契约的最小歧义片段，用一次反事实提问确定用户究竟要哪一种模型。

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title, full author list, Abstract, arXiv version/date"
[pdf:E02]: <_evidence/E02-p002-page.png> "PDF 物理页 2，Figure 1 silent-failure gallery; Section 1 Introduction"
[pdf:E03]: <_evidence/E03-p003-page.png> "PDF 物理页 3，Section 2 Related Work; Section 3.1 and Eq. (1)"
[pdf:E04]: <_evidence/E04-p004-page.png> "PDF 物理页 4，Figure 2; Sections 4.1–4.2; Eqs. (2)–(3), reference contracts and unresolved kernels"
[pdf:E05]: <_evidence/E05-p005-page.png> "PDF 物理页 5，Figure 3 workflow; Sections 4.3–4.4; Eqs. (4)–(5) IFS"
[pdf:E06]: <_evidence/E06-p006-page.png> "PDF 物理页 6，Section 5.1 ground-truth audit; Sections 6.1–6.2 setup and InitExec2 definition"
[pdf:E07]: <_evidence/E07-p007-page.png> "PDF 物理页 7，Tables 1–3 standard sweeps, controlled registry audit and official-document control; Section 6.3"
[pdf:E08]: <_evidence/E08-p008-page.png> "PDF 物理页 8，Tables 4–5 error categories and cross-DSL diagnostics; Section 7.1 perturbation-pair design"
[pdf:E09]: <_evidence/E09-p009-page.png> "PDF 物理页 9，Figures 4–5 extraction/gain and IFS/MCS diagnostics; Sections 7.1–7.3"
[pdf:E10]: <_evidence/E10-p012-page.png> "PDF 物理页 12，Appendix A diffusion gallery specification; Appendix B Eq. (6), Darcy weak form and Listing 1"
[pdf:E11]: <_evidence/E11-p013-page.png> "PDF 物理页 13，Appendix C Algorithm 1; four pipeline stages; iteration guard and execution-repair description"
[pdf:E12]: <_evidence/E12-p014-page.png> "PDF 物理页 14，Appendix D official-document corpus, retrieval budget, variants and leakage controls"
[pdf:E13]: <_evidence/E13-p015-page.png> "PDF 物理页 15，Table 6 mapping scope and coverage; weak-form definitions and coupled-source entries"
[pdf:E14]: <_evidence/E14-p017-page.png> "PDF 物理页 17，Appendix F Definition F.1 and Eq. (7) MCS; final-field relative L2 error definition"
[pdf:E15]: <_evidence/E15-p019-page.png> "PDF 物理页 19，Tables 8–9 MCS diagnostics; Appendix G Definitions G.1–G.4, Eqs. (8)–(12)"
[pdf:E16]: <_evidence/E16-p020-page.png> "PDF 物理页 20，Appendix G Eq. (14), Table 10 weights, variable alignment, Definitions G.7–G.8 and Theorem G.1"
[pdf:E17]: <_evidence/E17-p021-page.png> "PDF 物理页 21，Theorems G.2–G.3 and Corollary G.1; Appendix H.1 registry; Appendix I paired tests"
[pdf:E18]: <_evidence/E18-p022-page.png> "PDF 物理页 22，Table 11 experiment parameters; Table 12 paired statistics; Table 13 hard-subset gains"
[pdf:E19]: <_evidence/E19-p023-page.png> "PDF 物理页 23，Table 14 hard-threshold sensitivity; Appendix I bootstrap/proportion protocol; Appendix J examples"
[pdf:E20]: <_evidence/E20-p024-page.png> "PDF 物理页 24，Appendix K verbatim prompts; Appendix L framework_009 task and Direct failure"
[pdf:E21]: <_evidence/E21-p025-page.png> "PDF 物理页 25，Appendix L correction to IFS 0.98; Appendix M execution-repair failures; Table 15"
[pdf:E22]: <_evidence/E22-p026-page.png> "PDF 物理页 26，Appendix O benchmark construction and complexity tiers; Table 17 family distribution"
[pdf:E23]: <_evidence/E23-p027-page.png> "PDF 物理页 27，Appendix O truth construction, self-validation and examples; Table 18 weight ablation"
[pdf:E24]: <_evidence/E24-p028-page.png> "PDF 物理页 28，Table 19 DSL requirements; Figure 7 printed points and caption inconsistency; Tables 20–21 error taxonomy"
[pdf:E25]: <_evidence/E25-p029-page.png> "PDF 物理页 29，Figure 8 execution/fidelity partitions; Tables 22–23 weak-model and mixed-model diagnostics"
[pdf:E26]: <_evidence/E26-p030-page.png> "PDF 物理页 30，Tables 24–25 family means and Table 26 sub-dimensional IFS, including coefficient regressions"
[pdf:E27]: <_evidence/E27-p031-page.png> "PDF 物理页 31，Figure 9 family-by-complexity counts; tier totals obtained by summing printed cell counts"
[pdf:E28]: <_evidence/E28-p016-page.png> "PDF 物理页 16，Table 6 continued: Diffusion weak-form contribution and other mapped kernel semantics"
