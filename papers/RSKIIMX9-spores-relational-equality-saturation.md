# SPORES: Sum-Product Optimization via Relational Equality Saturation for Large Scale Linear Algebra

作者：Yisu Remy Wang、Shana Hutchison、Jonathan Leang、Bill Howe、Dan Suciu  
出处：arXiv:2002.07951v2（源 PDF 标注为 A PREPRINT）  
年份：2020  
DOI：10.14778/3407790.3407799  
Zotero key：RSKIIMX9  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“能否手工写出某个矩阵恒等式”，而是：**编译器怎样在 sparsity、common subexpression elimination（CSE，共同子表达式消除）、operator fusion（算子融合）和矩阵形状相互作用时，系统地枚举等价 linear algebra（LA，线性代数）程序，并选出执行代价最低的一个。** 作者指出，SystemML、OptiML、Cumulon 一类系统依靠局部 pattern rewrite（模式重写）和启发式条件；规则数量增长后，重写冲突、phase ordering（阶段排序）和输入依赖会同时出现，编译器容易错过需要多步组合才能显现的优化。[pdf:E01]（PDF 物理页 1，Abstract 与 Section 1）[pdf:E02]（PDF 物理页 2，Introduction）

论文用损失函数

\[
L=\operatorname{sum}\!\left((X-UV^{\top})^2\right)
\]

说明问题规模。源 PDF 设定稀疏矩阵 \(X\) 为 \(1\mathrm{M}\times 500\mathrm{k}\)，稠密向量 \(U,V\) 的长度分别为 \(1\mathrm{M}\) 与 \(500\mathrm{k}\)；直接形成 \(UV^{\top}\) 需要约 \(0.5\) trillion 次乘法和巨大的中间矩阵，而等价式

\[
\operatorname{sum}(X^2)-2U^{\top}XV+(U^{\top}U)(V^{\top}V)
\]

把主要工作变成对稀疏 \(X\) 的乘法和若干标量归约。[pdf:E01]（PDF 物理页 1，Section 1 开篇示例）这个例子的重要性在于：最优方向不是由“展开通常更贵”或“因式分解通常更省”这类单一经验决定，而取决于稀疏性、融合实现和是否存在可共享中间结果。

论文直接陈述的价值有两层。理论上，它把 LA sum-product 表达式翻译成 relational algebra（RA，关系代数），用少量 RA 等式构造一个完备的等价空间；系统上，它用 equality saturation（等式饱和）保存许多候选，再按全局成本抽取计划。作者报告该实现能导出 SystemML 已有的手写优化，并在部分任务上得到相对 SystemML 的 \(1.2\times\) 到 \(5\times\) 加速。[pdf:E02]（PDF 物理页 2，Introduction 与 contributions）

边界也很明确：这是一篇面向大型 LA sum-product 编译优化的论文，不是通用机器学习编译器，更不是 EMT、实时仿真或 FPGA 实现论文。其价值主要在“等价表示与搜索机制”，而不是提出新的数值算法、训练目标或硬件流水线。

## § 2 — 前人工作与不足

**论文对 prior work 的直接归纳。** SystemML、OptiML、Cumulon 主要使用 syntactic rewrite（语法重写）与启发式；传统数据库优化多集中于 join order；FAQ、AJAR 等 sum-product 工作能处理 join/product 与 aggregate，但本文认为它们不足以覆盖实际 LA 程序中普遍出现的 addition 与 CSE。SPOOF 已提出用关系视角优化 LA 的愿景，不过它要求中间关系表达式最多只有两个 free attributes（自由属性），以保证每一步都能写回 LA；SPORES 则允许搜索临时进入超过二维的关系表示，只要求最终结果能够回到 LA。[pdf:E03]（PDF 物理页 15，Section 5 与 5.1）

**工程上的不足不是“少考虑了几个规则”，而是规则体系的组织方式失效。** 源 PDF 列出四类具体失败模式：同一表达式可能同时匹配互斥重写；某些规则必须先于或晚于 constant folding；同一恒等变换是否有利取决于 sparsity 与 CSE；而有价值的优化往往由许多细粒度规则组合而成，示例损失函数大约需要十次 \(R_{EQ}\) 应用才能从原式走到高效式。[pdf:E04]（PDF 物理页 7，Section 3 开头）这解释了为什么简单增加 `if` 条件和规则优先级会让代码库越来越脆弱：它把“表达式是否等价”和“在当前数据上是否便宜”混在每条规则里处理。

SystemML 的现状也给出一个量化侧面。Figure 14 汇总了三十一个 rewrite method、共八十四个 sum-product pattern；每个方法还附带维度、空矩阵、标量、CSE 或转置等条件。[pdf:E05]（PDF 物理页 12，Figure 14）这些规则已经能完成大量实用优化，但它们是逐项编码的知识库，难以保证覆盖新的组合，也难以全局比较“展开”和“因式分解”这类方向相反的候选。

**本文相对前人的真正变化。** 它不是提出另一批更聪明的 LA 模式，而是改变 intermediate representation（IR，中间表示）与搜索语义：先把矩阵运算降到 K-relations 上的 join、union、aggregate，再用可逆等式形成等价类；选择哪一个形式则推迟到独立的 extraction 阶段。基于包内材料可以说这是对上述工程缺口的系统化回答；由于本任务不联网，也没有补充检索更晚近工作，因此关于更广泛 novelty 的判断只应视为候选判断。

## § 3 — 重建作者的思考路径

可以把通向 SPORES 的思考过程逆向重建为五步。

1. **先观察 LA 语法遮住了逐元素结构。** 对 \(\operatorname{sum}((UV^{\top})^2)\)，常见矩阵恒等式不容易直接把它变成 \((U^{\top}U)(V^{\top}V)\)；一旦写成索引求和，\(U_iV_jU_iV_j\) 就能按交换、结合和求和分离自然重组。[pdf:E06]（PDF 物理页 3，Figure 2 下方推导）这提示问题可能不是“缺恒等式”，而是当前语法层级不适合表达它们。

2. **寻找一个运算核心更小、等价律更统一的表示。** 把矩阵条目视作 K-relation tuple 的 multiplicity（重数），point-wise multiply 对应 natural join，矩阵加法对应 union，求和对应 aggregate，矩阵乘法对应 join 后按共享索引 aggregate。这样，大量看似不同的 LA 技巧被压缩为 bind/unbind 与三个 RA 核心算子。[pdf:E06]（PDF 物理页 3，Figure 1 与 Figure 2）[pdf:E07]（PDF 物理页 4，Table 1 与 Figure 3）

3. **先问“等价空间能否闭合”，再问“怎样找便宜计划”。** 如果每个 RA 表达式都能归约为“聚合后的单项式之和”，并且语义等价的 canonical form（规范形）仅相差索引同构，那么可逆 RA 等式就能连接原先在 LA 恒等式下分离的两个“岛”。Figure 4、Figure 5 与 Figure 6 展示了这条从 LA 到 RA 再到 canonical form 的桥。[pdf:E08]（PDF 物理页 4，Figure 4）[pdf:E09]（PDF 物理页 5，Figure 5、Figure 6 与 Section 2.3）

4. **意识到完备性会制造搜索爆炸。** 即使规则少，结合律、交换律、分配律和大量 aggregate 也会产生极多候选。传统“每次选一个重写”的策略重新落入 phase-ordering；E-Graph 则让等价表达式共享 E-Class 和共同子图，使表达式数量可以远大于图本身的节点数。[pdf:E04]（PDF 物理页 7，Section 3.1）[pdf:E10]（PDF 物理页 8，Figure 8、Figure 9 与 saturation 流程）

5. **把搜索与决策彻底分开。** saturation 负责扩大等价空间；extraction 使用 sparsity、schema、CSE 与 operator cost 选择计划。这样同一条等式不再预先承诺方向，展开和因式分解都可以留在图中，最终由全局代价决定。[pdf:E11]（PDF 物理页 9，sampling、CSE 与 ILP extraction）[pdf:E12]（PDF 物理页 10，Figure 11、Figure 12 与 class invariants）

这个路径的关键不是某个单独算法，而是连续改变三个问题的边界：先换语义表示，再压缩等价空间，最后才做成本选择。

## § 4 — 核心 Intuition

把矩阵程序先降到逐元素的 K-relation 语义，join、union、aggregate 的少量等式就能覆盖原本散落在许多 LA 特例中的变换。[pdf:E06]（PDF 物理页 3，Figure 1 与 Figure 2）不要在每次匹配时立刻决定重写方向，而把可达的等价式共享地压进 E-Graph。[pdf:E10]（PDF 物理页 8，Section 3.1）最后用全局成本从同一等价类中选出能利用 sparsity、fusion 和 CSE 的计划，再翻译回 LA。[pdf:E11]（PDF 物理页 9，optimal-plan extraction）核心变化是从“局部规则触发器”转成“语义等价空间加全局抽取器”。

## § 5 — 具体方法与完整 Pipeline

以输入 \(L=\operatorname{sum}((X-UV^{\top})^2)\) 为例，SPORES 的完整 pipeline 如下。

1. **接收 LA DAG 与数据属性。** SPORES 插入 SystemML 的 algebraic rewrite pass，输入是 LA operator DAG；矩阵维度与 sparsity estimate 由 SystemML 提供，只对程序内层的重要 LA 表达式调用该优化器。[pdf:E13]（PDF 物理页 11，Figure 13 与 Section 3.5）

2. **用 \(R_{LR}\) 把 LA 翻译为 RA。** `bind` 给矩阵维度命名，`unbind` 把关系结果重新解释成矩阵；例如
   \[
   AB\rightarrow[-i,-k]\sum_j([i,j]A*[j,k]B),\qquad A^{\top}\rightarrow[-j,-i][i,j]A.
   \]
   其中 LA 的 element-wise multiply 在 RA 中成为 natural join，LA 的 addition 成为 union。[pdf:E06]（PDF 物理页 3，Figure 2）连续的 unbind/bind 会被消去，并把属性 rename 向叶节点传播；最终得到叶端 bind、根端 unbind 的 RPlan。[pdf:E08]（PDF 物理页 4，Section 2.1 与 Figure 4）

3. **构造并扩展 E-Graph。** 输入 syntax tree 按 post-order 插入，以便一开始就共享已有 CSE；随后匹配 \(R_{LR}\) 与 \(R_{EQ}\) 的两侧，把匹配到的等价式加入同一 E-Class，并传播 congruence closure（同余闭包）。Figure 8、Figure 9 给出 `match → add → merge` 的伪代码。[pdf:E10]（PDF 物理页 8，Figure 8、Figure 9）

4. **控制 expansive rules，并维护 class invariants。** 结合律和交换律可能让图迅速膨胀，因此实现不是在每轮应用全部匹配，而是为每条规则采样有限匹配。每个 E-Class 同时携带 schema、常量与 sparsity 等不变量；schema 用于判断带 side condition 的 aggregate 规则，也用于剪掉不能翻译回二维 LA 的候选。[pdf:E11]（PDF 物理页 9，Dealing with Expansive Rules）[pdf:E12]（PDF 物理页 10，Section 3.2）

5. **按全局代价抽取。** 完整方案把每个 operator 与 E-Class 编成 ILP 变量：选中 operator 必须选中其子类，选中 E-Class 至少要选一个成员，根类必须被选；目标是最小化被选 operator 的总成本。由于共享 operator 只计一次，ILP 能显式处理 CSE，避免 Figure 10 中 greedy 局部选择造成的重复成本。[pdf:E11]（PDF 物理页 9，Figure 10 与 Constraint Solving）[pdf:E12]（PDF 物理页 10，Figure 11）论文也实验了更便宜的 bottom-up greedy extractor。

6. **翻译回 LA 并交给 SystemML 执行。** 选中的 RA plan 经 `translate` 返回最佳 LA DAG。自定义函数可以保留为 black box，也可以通过等式与基本算子关联；已有 fused operator 因而能与其它重写同时参与 saturation，而不是被固定在某个编译阶段之后。[pdf:E13]（PDF 物理页 11，Figure 13、Section 3.3 与 3.4）在示例中，canonical 路径包含 \(\operatorname{sum}(X^2)-2U^{\top}XV+(U^{\top}U)(V^{\top}V)\)，从而避免形成巨大的稠密 \(UV^{\top}\)。[pdf:E09]（PDF 物理页 5，Figure 6）

论文未报告物理系统模型、离散化、开关或事件处理、时间推进、多速率调度、定点数值表示、FPGA 资源映射或实时步长。实际平台是单节点 SystemML/Spark 软件栈，因而不能把其 pipeline 直接解释成硬件或实时仿真 pipeline。[pdf:E14]（PDF 物理页 12，Evaluation setup）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有明确的形式化数学，核心由“语义翻译的完备性”和“E-Graph 上的最小成本抽取”两部分组成。

### 从 LA 到 K-relations

矩阵 \(A\) 被解释为关系 \(A(i,j)\)，其 tuple multiplicity 是实数矩阵条目。于是：element-wise multiply 变为 natural join，addition 变为 union，sum 变为 aggregate，matrix multiply 变为共享索引上的 join 后 aggregate。[pdf:E06]（PDF 物理页 3，Figure 1）关键翻译规则包括：

\[
\begin{aligned}
A*B &\rightarrow [-i,-j]([i,j]A*[i,j]B),\\
A+B &\rightarrow [-i,-j]([i,j]A+[i,j]B),\\
AB &\rightarrow [-i,-k]\sum_j([i,j]A*[j,k]B),\\
A-B &\rightarrow A+(-1)*B.
\end{aligned}
\]

这些式子直接来自 Figure 2。[pdf:E06]（PDF 物理页 3，Figure 2）其直觉是把“矩阵算子名称”展开成“索引如何连接和消去”，从而让原本特殊的矩阵优化变成普通关系等式。

### 七条 RA 等式与 canonical form

\(R_{EQ}\) 包括分配律、aggregate 对 union 的线性、在索引不属于 \(A\) 时把 aggregate 穿过 join、aggregate 合并，以及 join/union 的结合交换律。代表性规则为

\[
A*(B+C)=A*B+A*C,
\]

\[
\sum_i(A+B)=\sum_iA+\sum_iB,
\]

\[
i\notin \operatorname{Attr}(A)\Rightarrow A*\sum_iB=\sum_i(A*B).
\]

完整七条规则见 Figure 3。[pdf:E07]（PDF 物理页 4，Figure 3）

作者把 canonical RPlan 定义为“若干 aggregated monomial 的和”，可压缩写成

\[
C(e)=\sum_r c_r\sum_{A_r}\prod_j x_{rj}^{k_{rj}},
\]

其中同一 monomial 内重复 factor 合并为幂，同构 monomial 合并系数，且不再保留两项同构 monomial。[pdf:E09]（PDF 物理页 5，Definition 2.1 与 normal-form 说明）Lemma 2.1 说明每个 RA 表达式都能用 \(R_{EQ}\) 归到某个 canonical form；Lemma 2.2 说明若两个 normal form 对任意维度输入语义相同，则二者同构。由此得到 Theorem 2.3：

\[
\forall e_1,e_2\in LA,\ \forall d,\ e_1(d)=e_2(d)
\iff
R_{LR}(e_1)\;R_{EQ}^{*}\;R_{LR}(e_2).
\]

也就是 LA 语义等价，当且仅当二者的 RA 翻译能通过 \(R_{EQ}\) 的传递闭包互相到达。[pdf:E15]（PDF 物理页 6，Lemma 2.1、Lemma 2.2 与 Theorem 2.3）这里“对任意维度”不是装饰条件：论文专门给出只在一维或低维上碰巧相等、但 canonical form 不同的例子，说明有限固定形状上的偶然等价不能推出该完备结论。[pdf:E15]（PDF 物理页 6，Lemma 2.2 后的维度讨论）

Appendix A 补上 uniqueness 证明。它先把 canonical expression 定义为不含同构 terms 的 polyterm，再证明 canonical expression 的 isomorphism 与 semantic equivalence 等价。[pdf:E16]（PDF 物理页 20，Definition A.5 至 Theorem A.3）困难方向使用逆否命题：若两个 canonical expression 不同构，就选取 homomorphism 偏序中的最小 term，构造稀疏 witness tensors，使该 term 产生一个其它 term 无法产生的 monomial，因此两个表达式在该输入上取值不同。[pdf:E17]（PDF 物理页 21，Lemma 2.2 的 witness proof）

### E-Graph 抽取的 ILP

对每个 operator 设布尔变量 \(B_{op}\)，对每个 E-Class 设 \(B_c\)，根类变量为 \(B_r\)。论文的约束为

\[
\mathrm{Constraints}\equiv B_r\land\bigwedge_{op}F(op)\land\bigwedge_cG(c),
\]

\[
F(op)\equiv B_{op}\Rightarrow\bigwedge_{c\in op.children}B_c,
\qquad
G(c)\equiv B_c\Rightarrow\bigvee_{op\in c.nodes}B_{op},
\]

并最小化

\[
\sum_{op}B_{op}C_{op}.
\]

这保证抽出的节点构成与输入同一根 E-Class 的合法表达式，并让共享子表达式只承担一次成本。[pdf:E12]（PDF 物理页 10，Figure 11）

成本 \(C_{op}\) 主要来自输出非零元估计。论文定义 sparsity \(S=nnz/size\)，并采用

\[
S[X*Y]=\min(S[X],S[Y]),\quad
S[X+Y]=\min(1,S[X]+S[Y]),\quad
S\!\left[\sum_iX\right]=\min(1,|i|S[X]).
\]

[pdf:E12]（PDF 物理页 10，Figure 12）这部分是工程 cost model，不是等价性定理；它决定“找到的等价表达式”是否真能转化为最快实现。

## § 7 — 实验设计与结论

论文围绕三个 research question 组织实验，并明确列出硬件与软件环境：单节点 Intel E7-4890 v2 @ 2.80GHz、1008 GB RAM、8 TB disk、Ubuntu 16.04.6，OpenJDK 1.8.0、Hadoop 2.7.3、Spark 2.4.4；Spark 本地运行六个 executor，每个八核，driver memory 为 50 GB，executor memory 为 100 GB。数据均由 SystemML benchmark generator 合成。[pdf:E14]（PDF 物理页 12，Evaluation questions 与 setup）

**问题一：关系等式能否覆盖手写 sum-product rules？** 设计是把每条 SystemML rule 的左侧输入 SPORES，执行 saturation，再检查右侧是否出现在 E-Graph 中。答案是：Figure 14 的三十一个方法、八十四个 pattern 全部能够由 \(R_{LR}\) 与 \(R_{EQ}\) 导出。[pdf:E05]（PDF 物理页 12，Figure 14）[pdf:E18]（PDF 物理页 13，Section 4.1 结论）这验证的是“已知规则是否落在搜索空间里”，不是证明所有实际程序都能在有限时间完成 saturation。

**问题二：是否找到比 SystemML 启发式更快的计划？** 设计是在 Generalized Linear Model（GLM）、Multinomial Logistic Regression（MLR）、Support Vector Machine（SVM）、Poisson Nonnegative Matrix Factorization（PNMF）、Alternating Least Squares（ALS）五个程序上比较 base、SystemML `opt2` 与 saturation；base 只做基本局部优化，`opt2` 包含 advanced rewrites、CSE、sum-product rules 和 fusion。[pdf:E18]（PDF 物理页 13，Section 4.2 与 Figure 15）答案是总体相对 SystemML 提升 \(1.2\times\) 到 \(5\times\)。ALS 的最高 \(5\times\) 来自把 \((UV^{\top}-X)V\) 展开为 \(U(V^{\top}V)-XV\)，使稀疏 \(X\) 不再被稠密中间量淹没；PNMF 最高约 \(3\times\)，关键是把 \(\operatorname{sum}(WH)\) 改成 column sums 与 row sums 的乘积，避免物化稠密 \(WH\)；MLR 则反过来通过提取公共因子并使用 `sprop` fused operator 获益。SVM 与 GLM 找到的主要是 SystemML 已有 fusion 优化。[pdf:E19]（PDF 物理页 14，Figure 17 与 ALS、PNMF、MLR、SVM、GLM 分析）

**问题三：搜索开销是否值得？** 设计比较 depth-first saturation 与 sampled saturation，以及 ILP extraction 与 greedy extraction。Figure 16 报告 depth-first 在 GLM、SVM 上触及 \(2.5\) s compile timeout；greedy extraction 显著缩短编译时间，在这些 benchmark 上没有损失运行时收益。[pdf:E18]（PDF 物理页 13，Figure 16 与 Section 4.3 开头）进一步分析显示 sampled saturation 在 ALS、MLR、PNMF 上收敛，因此在给定 cost model 下可谈最优性；GLM、SVM 在 iteration limit 前不收敛。论文观察实际被优化的 DAG 往往不超过十五个 operator，较大的程序会被 uninterpreted function 等 optimization barrier 切小。[pdf:E20]（PDF 物理页 15，Section 4.3）

**不得外推的范围。** 证据来自单节点、本地 Spark、合成数据、五个 SystemML benchmark 和 LA 内层表达式；没有跨硬件、真实生产数据分布、分布式集群、GPU/FPGA、数值误差或训练质量评测。[pdf:E13]（PDF 物理页 11，Section 3.5 的调用范围）[pdf:E14]（PDF 物理页 12，Evaluation setup）因此能稳妥支持的是“该表示和搜索方法在所测 sum-product workload 上可替代大量手写规则并发现若干有效重写”，不能直接推广为“所有 LA 程序都能高效饱和并获得全局最快执行”。

## § 8 — Take-aways

**五句话：**

1. SPORES 把 LA sum-product 表达式翻译成 K-relations 上的 join、union、aggregate，让许多矩阵特例共享同一组语义等式。[pdf:E06]（PDF 物理页 3，Figure 1 与 Figure 2）
2. 其理论核心是 canonical form 唯一性，从而把 LA 语义等价转成 \(R_{EQ}\) 可达性。[pdf:E15]（PDF 物理页 6，Theorem 2.3）
3. E-Graph 延迟所有重写方向选择，sampling 控制 expansive rules，ILP 或 greedy extractor 再按全局 cost 选计划。[pdf:E11]（PDF 物理页 9，Section 3.1）
4. 实验中它导出了 SystemML 的八十四个 hand-coded pattern，并在部分算法上取得 \(1.2\times\) 到 \(5\times\) 加速。[pdf:E18]（PDF 物理页 13，Section 4.1 与 Figure 15）[pdf:E19]（PDF 物理页 14，benchmark 分析）
5. 真正的瓶颈从“规则是否存在”转移到 saturation 是否覆盖关键区域，以及 cost model 能否正确预测真实执行代价。[pdf:E12]（PDF 物理页 10，Figure 12）[pdf:E20]（PDF 物理页 15，Section 4.3）

**三句话：**

1. 论文用关系语义把碎片化 LA 重写变成一个可证明完备的等价空间。[pdf:E09]（PDF 物理页 5，Section 2.3）
2. equality saturation 让相反方向的优化同时存在，因而能分别发现 ALS 的分配式优化和 MLR 的因式分解优化。[pdf:E19]（PDF 物理页 14，ALS 与 MLR 分析）
3. 系统成败最终取决于搜索规模和成本估计，而这两点仍主要由工程近似控制。[pdf:E12]（PDF 物理页 10，cost model）[pdf:E20]（PDF 物理页 15，convergence 与 overhead）

**一句话：** SPORES 的核心贡献是把“写更多聪明规则”改写为“建立共享的等价空间，再全局选执行计划”。

## § 9 — 最脆弱的假设

**最脆弱的假设是：以输出 \(nnz\) 和简单 sparsity propagation 为主的 cost model，能够正确排序真实机器上的候选计划。** 这不是次要实现细节；完备性只保证某个等价式可以出现在搜索空间中，真正执行哪一个完全由 extraction objective 决定。若成本排序错误，E-Graph 越完整，反而只是让错误选择面对更多候选。

论文的 estimator 把 operation cost 近似为输出非零元规模，并用 Figure 12 的 \(\min\) 与加和规则传播 sparsity。[pdf:E12]（PDF 物理页 10，Figure 12 与其后正文）这种模型没有直接表达 sparse pattern 的局部性、数据布局、kernel startup、cache/NUMA、物化与 streaming 的差别、fusion 实现质量或不同 operator 的常数因子。**这是基于证据的推断，不是作者原句。**

论文给出的支持证据是：该成本体系在 ALS、PNMF、MLR 上确实选中了带来显著加速的计划。[pdf:E19]（PDF 物理页 14，benchmark 分析）但同一页也给出警告：作者为 GLM 找到一个理论上应更快的手工优化，却因 SystemML 不能准确估计 sparsity 而没有实际效果。[pdf:E19]（PDF 物理页 14，SVM/GLM 段落）这说明“等价空间正确”与“最快计划被选中”之间仍有明显断层。论文缺少同一 \(nnz\) 下不同稀疏结构、不同硬件、不同 kernel library 和 cost-ranking accuracy 的系统评测；一旦这个假设失效，论文的实际性能贡献会直接失效，而理论完备性仍然成立却难以兑现。

## § 10 — 最小复现实验

一周内最值得复现的不是整个编译器，而是 **ALS 中那条反直觉分配式重写是否真的由 sparsity 决定，并且简单 cost ranking 能否预测正确方向。** 论文报告的核心变换是

\[
(UV^{\top}-X)V\quad\Longrightarrow\quad U(V^{\top}V)-XV,
\]

并把最高 \(5\times\) 加速归因于避免稠密中间量、利用稀疏 \(X\) 和 `mmchain`。[pdf:E19]（PDF 物理页 14，ALS 段落）

**数据。** 使用 SystemML benchmark generator 生成 ALS 输入，优先复用 Figure 17 中的 \(1\mathrm{M}\times 10\) 与 \(10\mathrm{M}\times 10\) 规模，并为 \(X\) 生成低、中、高三档 sparsity；\(U,V\) 保持稠密。[pdf:E19]（PDF 物理页 14，Figure 17）再增加“相同 \(nnz\)、不同非零分布”的版本，用于观察 cost model 看不见的结构效应。

**实现。** 在同一 SystemML 版本和相同执行设置下，手工固定两份 algebraically equivalent DAG：原始计划与分配后的计划；关闭其它会改变这段表达式的重写，只保留相同的后端 fusion 与 `mmchain` 能力。先用小输入验证输出一致，再运行正式输入。

**测量。** 记录 end-to-end runtime、该 DAG 的执行时间、peak memory、是否物化 \(UV^{\top}\)、各中间量的估计与实际 \(nnz\)，并记录 optimizer 对两计划的成本排序。实验环境尽量复用论文的 SystemML `opt2` 基线设置，以减少后端差异。[pdf:E14]（PDF 物理页 12，实验软件配置）

**支持与反驳标准。** 若在稀疏 \(X\) 上分配计划稳定减少物化和运行时间，且 cost model 在 sparsity 变化时正确翻转或维持排序，就支持论文关于该优化机制的解释；若同一 \(nnz\) 的不同 pattern 频繁导致实际排序反转，或原始计划因 fusion/CSE 更快而 estimator 仍选分配计划，就反驳“简单 sparsity cost 足以指导抽取”的实际 claim。这个实验不证明完整 SPORES，但能直接验证其最关键的“等价搜索加成本选择”闭环中的一条因果链。

## § 11 — 最强反例设计

最强攻击不是找一个 SPORES 不支持的 operator，而是构造 **语义等价候选都在 E-Graph 里、cost model 也给出确定选择，但真实运行时排序系统性翻转** 的程序族。这样可以把失败定位在论文最关键的“全局抽取”环节，而不是实现缺功能。

具体做法是围绕 ALS 变换构造三个 \(X\)：均匀随机稀疏、非零集中于少数行或列、与后端 block kernel 对齐的块稀疏；三者保持相同 shape 和 \(nnz\)。再让 \(UV^{\top}\) 被程序中的另一个 consumer 使用，使“保留稠密 CSE”与“分配后避免物化”形成真实竞争。E-Graph/ILP 理论上能够把共享 operator 只计一次，这是论文采用 ILP 的理由。[pdf:E11]（PDF 物理页 9，Figure 10 与 ILP 说明）然而 Figure 12 的 cost model 主要看 \(nnz\)，对这三种 pattern 会给出近似相同的信息。[pdf:E12]（PDF 物理页 10，Figure 12）

攻击实验应把所有候选计划手工导出，在同一执行引擎中逐个运行，再比较 SPORES 选择与真实最优。如果在块稀疏或强偏斜输入上，dense fused path 或共享 \(UV^{\top}\) 的计划明显更快，而 extractor 仍稳定选择分配计划；同时在均匀随机稀疏上论文计划又占优，那么就得到一个可预测的失败条件：**相同 cardinality 不代表相同 physical cost。** 这也挑战一种替代解释——论文中的收益可能主要来自 SystemML 当时已有 fused operator 与 kernel 组合，而不是 RA search 本身普遍具有更好的成本判断。ALS 与 MLR 分别偏好分配和因式分解、且 MLR 明确依赖 `sprop` fusion，正好说明 operator implementation 会改变最优代数方向。[pdf:E19]（PDF 物理页 14，ALS 与 MLR 段落）

若该反例成立，论文的等价性定理不受影响，但“完备搜索加简单全局成本即可得到高性能计划”的系统结论会被实质削弱。

## § 12 — Follow-up Research Bet

### 主押注：代数—布局—硬件联合 equality saturation

**新的研究问题。** 能否把 SPORES 的搜索对象从“等价 LA/RA 表达式”升级为“等价的 algebra、storage layout、materialization/streaming 方式、fused kernel 与硬件 dataflow”，让 extraction 直接输出可执行的 FPGA 流水线，而不是先选 LA DAG、再交给后端做独立映射？这是候选判断；本任务没有联网检索，因此不声称 novelty。

**首次成为可能的能力。** 同一个等价空间可以同时决定：ALS 应该展开以利用稀疏 \(X\)，MLR 应该因式分解以触发 `sprop` fusion，某个中间量应放在片上 buffer 复用还是从外存流式通过，以及代数变形是否值得改变矩阵 layout。论文已经展示“最优代数方向会随 kernel 与 sparsity 改变”：ALS 因分配律获益，MLR 因提取公共因子和 fused operator 获益。[pdf:E19]（PDF 物理页 14，ALS 与 MLR 分析）

**核心机制与因果链。** 现有 SPORES 已把 schema、常量和 sparsity 作为 E-Class invariant，并能用 invariant 剪掉不能回译 LA 的候选。[pdf:E12]（PDF 物理页 10，Section 3.2）它也允许 custom function 与基础算子通过等式共存，使已有 fused operator 参与 saturation。[pdf:E13]（PDF 物理页 11，Section 3.3）下一步不是在 SPORES 后面加一个普通 HLS wrapper，而是改变 E-node 的语义：节点同时携带 algebraic operator、layout、streaming/materialization、kernel implementation 与 buffer/reuse edge；rewrite rule 连接数学等价和物理 dataflow 等价；class invariant 扩展为 shape、sparsity、layout compatibility 与资源 signature；抽取器联合选择代数式和硬件 schedule。因果链是“保留相反代数候选 → 让物理实现成为同一等价图的一部分 → 在共享资源和数据移动约束下联合抽取 → 生成针对具体 workload 的不同硬件拓扑”。

**改变的基本设计变量。** 它至少改变状态表示、硬件映射、系统边界和评价对象：状态不再只是 LA/RA expression；输出不再只是 LA DAG；系统边界跨过 compiler IR 与 accelerator synthesis；评价从 operator cost 变成吞吐、外存流量、片上存储、资源占用和端到端 latency 的联合对象。

**论文特异依据。** 方法侧依据是 class invariants、custom functions 与 fusion 可在 E-Graph 中统一表示。[pdf:E12]（PDF 物理页 10，class invariants）[pdf:E13]（PDF 物理页 11，operator fusion）实验侧依据是相反代数方向在 ALS 与 MLR 上分别胜出，以及 PNMF 的收益来自避免 dense materialization。[pdf:E19]（PDF 物理页 14，benchmark 机制分析）相关工作部分还明确说 SPOOF 提出 compile-time fused-operator generation，SPORES 当前主要利用已有 fused operator，并把“sum-product rewrite 与 fusion generation 结合”列为未来方向。[pdf:E03]（PDF 物理页 15，Section 5.1）本押注比顺序式“先重写、再 fusion generation”更进一步：layout 与硬件 dataflow 是等价类中的一等对象，跨层选择在同一次 extraction 中完成。

**最大收益与最大风险。** 最大收益是把 algebraic superoptimization 直接变成 accelerator architecture synthesis，使“展开、因式分解、共享、融合、流式化”不再由不同编译阶段各自做局部决定。最大科学风险是物理选择加入后 E-Graph 组合爆炸，且硬件 cost 不再能由简单 \(nnz\) 估计；如果联合图不能压缩这些选择，或 HLS 编译反馈太慢，机制会失去可扩展性。论文已经显示仅代数 AC rules 就会爆图，sampling 也不能保证所有程序收敛，因此这个风险是由现有证据直接放大的。[pdf:E11]（PDF 物理页 9，Dealing with Expansive Rules）[pdf:E20]（PDF 物理页 15，convergence 结果）

**首个证伪实验。** 选择 ALS 与 MLR 两类 kernel，在同一 FPGA/HLS backend 和同一资源预算下比较三条路径：顺序式“先 SPORES 选代数、再硬件调度”、只搜索硬件 schedule 而固定代数、联合 co-saturation。测量端到端 latency、throughput、外存 traffic、片上 buffer、资源占用和 compile time；再分别冻结 algebra rule 与 layout/dataflow rule 做 ablation。若联合方法只是在 HLS autotuning 上更充分，而固定同一代数后也能得到全部收益，则核心机制被否证；若只有跨代数—布局的等式能分别为 ALS 找到稀疏 streaming 分配式、为 MLR 找到因式分解 fused pipeline，并在相同后端调参预算下仍占优，才支持该研究押注。

**与包内最近工作的实质区别。** SPOOF/Boehm 一线工作关注 fused operator generation 或 fusion plan，SPORES 关注关系语义下的代数等价搜索；这里把 physical layout、buffer reuse 和硬件 dataflow 纳入同一个可共享的等价表示，改变了 representation、experimental object 与 system boundary，而不是给原优化器增加一个 fusion 模块。[pdf:E03]（PDF 物理页 15，Section 5.1）

**Wild-card alternative：** 把 K-relation 的值域从固定实数推广为可选择 semiring，并让 equality saturation 同时搜索 provenance、概率推断或可微关系计算中的代数表示；这条路线改变的是数学对象与任务定义，而不是硬件机制。
