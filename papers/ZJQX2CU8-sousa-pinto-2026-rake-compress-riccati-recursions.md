# Rake–Compress Riccati Recursions for Parallel Scenario-Tree Model Predictive Control

作者：João Sousa-Pinto [pdf:E01]（PDF 物理页 1，标题与作者）  
出处：arXiv:2608.01332v1 [math.OC] [pdf:E01]（PDF 物理页 1，页边版本标识）  
年份：2026 [pdf:E01]（PDF 物理页 1，版本日期）  
DOI：未报告  
Zotero key：ZJQX2CU8  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的核心问题不是进一步减少 scenario-tree MPC（场景树模型预测控制）的总算术量，而是缩短其关键依赖链：标准 tree Riccati recursion（树 Riccati 递推）已经能以节点数线性量级完成一次 branched LQR（分支线性二次调节器）求解，但 backward/forward pass（反向/正向遍历）的 span（最长依赖链）仍与根到叶的最大高度成正比；长而不平衡的主干无法靠同层并行消除。论文提出的目标是，在保持代数精确、总工作量线性和完整 primal–dual（原始—对偶）恢复的同时，把依赖深度降为与节点数对数相关，并且不要求树平衡、树高较小或最大出度有界。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

论文直接陈述的答案是：先把每个局部控制独立消元，再用 rake（摘叶）处理分支、用 compress（压链）处理一元链段，反向展开恢复全部 Riccati 系数、状态、控制和乘子；给定可复用的 topology plan（拓扑计划），固定局部维度时，每次 factorization/solve（分解/求解）具有线性 work（工作量）、线性 storage（存储）和对数 span。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E15]（PDF 物理页 13，Theorem 4 与 Corollary 1）

重要性在于，scenario tree 同时编码“哪些决策必须共享”和“何时信息才分叉”。现实树常因不同分支的观测时刻、剪枝和终止深度而高度不规则；非预见性要求在信息尚未分开时共享控制，不能简单把各条 trajectory（轨迹）拆开独立求解。基于证据的工程推断是：若 Newton/KKT 线性代数仍按树高串行，增加 GPU/FPGA 并不会自动把长主干变成低延迟数据流；论文的价值正是把并行对象从“同一层的节点”改成“整棵树上的消元依赖图”。

## § 2 — 前人工作与不足

以下 prior work（前人工作）定位均是论文自己的 Related Work 归纳，不是本卡联网复核后的独立文献结论。

标准 tree-sparse KKT/Riccati 方法和 TREEQP 一类直接稀疏求解器已经做到总工作量随节点数线性增长，但依赖仍沿树高传播。链式时间并行方法则分别采用 recursive master problem（递归主问题）、endpoint-explicit decomposition（端点显式分解）或 associative conditional-value composition（可结合的条件价值复合）；它们能压缩单链，却没有给出如何在任意分支树上同时组织叶消元、链段复合和反向恢复。scenario decomposition（场景分解）通过对偶化 nonanticipativity（非预见性）或 dynamics（动力学）暴露独立轨迹，但改变了直接耦合求解的结构，可能引入协调或稠密系统。论文也区分了经典 Miller–Reif rake–compress、EREW PRAM 调度和本文面向重复数值求解的静态 CREW 式计划：操作原语相同，但调度规则和依赖图不同，因此既有复杂度定理不能直接套用。[pdf:E02]（PDF 物理页 2，Contributions 与 Related Work）

论文重点比较的最近方法 Zhang et al. 把 backward pass 在最后一次分支时刻切开：后缀路径可并行 scan（扫描），前缀要么继续普通 tree Riccati，要么把路径压平、协调共享控制并求一个稠密 control-space system（控制空间系统）。本文认为这仍依赖一个特殊“最后分支时刻”或预设拓扑模式；其目标则是直接分解原始稀疏任意树，让 rake 在任意分支处聚合兄弟子树、让 compress 在任意一元段上复合，不把整树展平成路径，也不形成全局稠密系统。[pdf:E03]（PDF 物理页 3，Related Work 末段）

因此，真正缺口不是“前人没有并行”，而是三件事尚未同时闭合：一是任意树拓扑上的 logarithmic dependency depth（对数依赖深度）；二是 exact direct solve（代数精确直接求解）而非迭代协调；三是从压缩结果完整恢复每个节点的状态、控制和乘子。

## § 3 — 重建作者的思考路径

可以从既有知识逆向重建出一条自然路线，而不先假定本文答案成立。

第一，branched LQR 已经有线性工作量的顺序递推，因此优化目标应从“少做运算”转为“重排依赖”，否则任何新算法都容易以额外工作换并行。第二，链式 LQR 已知存在可结合的 conditional value（条件价值）复合，这说明一段时间区间可以被压成只依赖端点状态的固定维对象。第三，经典 tree contraction（树收缩）告诉我们，任意树可以通过删除叶子和压缩一元节点在对数轮数内缩到根；它提供的是拓扑骨架，而不是 LQR 数值代数。[pdf:E02]（PDF 物理页 2，chain parallelism 与 tree contraction 相关工作）

接下来会遇到三个障碍。其一，需要找到一种数值表示，对“叶子连同父边被消去”和“中间一元节点连同两条边被复合”都闭合；其二，表示不能依赖显式求逆一个可能奇异的 dynamics regularization（动力学正则化），因为未正则化的精确约束也必须覆盖；其三，压缩时不能丢失反向恢复完整 primal–dual 解所需的信息。图 1 和图 2 展示的 rake/compress 结构正好把“跨分支”和“沿主干”两类并行性分开。[pdf:E06]（PDF 物理页 5，Fig. 1–2）

最后，标准 scenario MPC 在一个 information node（信息节点）上只有一个共享控制，而边式局部代数更希望每条边拥有局部控制。自然的桥接办法是把每个非叶节点拆成 predecision/decision（决策前/决策）两个节点，让控制在分支发生前成为一条唯一 decision edge（决策边）变量，从结构上保住非预见性，再把统一的边式代数交给 tree contraction。[pdf:E04]（PDF 物理页 3，Eq. (5) 与 nonanticipative node controls）[pdf:E05]（PDF 物理页 4，Eq. (8)–(10) 与 Proposition 2）

## § 4 — 核心 Intuition

把任意已消去子树压缩成“只描述边界状态之间代价与约束关系”的固定维 conditional quadratic（条件二次函数），而不是保留子树内部所有变量。[pdf:E08]（PDF 物理页 6，Eq. (14)–(20)）rake 把一个叶子子树的约化代价加回父节点，compress 用可结合复合把一元链段替换成一条等价边；两者交替即可同时挖掘分支和时间方向的并行性。[pdf:E06]（PDF 物理页 5，Fig. 1–2）保存少量 residual tape（残余带）后逆序展开，就能恢复每个子树价值 Hessian、状态、控制与乘子，而不牺牲 exact KKT equivalence（精确 KKT 等价性）。[pdf:E09]（PDF 物理页 7，Eq. (23)–(30) 与 Theorem 1）

## § 5 — 具体方法与完整 Pipeline

以论文的 irregular autonomous-driving scenario tree（不规则自动驾驶场景树）为例，完整流程如下。

1. **建立局部问题。** 每个节点保存状态、局部代价和进入该节点的对偶变量，每条边保存 dynamics 与一个局部控制；总体问题写成 dual-regularized branched LQR saddle problem（对偶正则化分支 LQR 鞍点问题），其 KKT 方程覆盖节点 stationarity（驻点条件）、控制 stationarity、根约束和边 dynamics。[pdf:E04]（PDF 物理页 3，Eq. (1)–(5)）

2. **把共享 node control 线性规模地提升为 edge control。** 对非叶信息节点建立状态为 \([x_i;0]\) 的 predecision 节点和状态为 \([x_i;v_i]\) 的 decision 节点；decision edge 唯一携带共享控制 \(v_i\)，后续 uncertainty edges（不确定性边）不再各复制一份控制。提升后节点数不超过 \(2|V|-1\)，最大分支度不增加，投影回原变量得到同一 KKT 解。[pdf:E05]（PDF 物理页 4，Eq. (8)–(10) 与 Proposition 2）

3. **一次性构造 topology-only plan。** 每个 structural round（结构轮）先 rake 全部非根叶节点，再从剩余一元节点选 maximal nonadjacent set（极大非相邻集合）并行 compress；同一父节点的多个 rake contribution（摘叶贡献）用预计算、保序的二叉归约合并，所有操作依赖被记录供 reverse expansion（反向展开）。[pdf:E06]（PDF 物理页 5，Fig. 1–2）[pdf:E12]（PDF 物理页 10，Algorithm 1 与 Section VII-A）

4. **做 homogeneous factorization（齐次分解）。** 先独立消去每条原始边上的控制，得到 edge triple（边三元组）；随后在条件二次数据上执行 rake/compress，收缩到根，再反向展开得到每个原始节点的 subtree value Hessian（子树价值 Hessian）\(P_i\)。最后每个节点/边独立构造 \(F_i,W_i,G_e,K_e,T_e\) 等局部可复用因子。[pdf:E07]（PDF 物理页 5，Eq. (11)–(13)）[pdf:E08]（PDF 物理页 6，Eq. (14)–(22)）[pdf:E10]（PDF 物理页 8，Eq. (31)–(38)）

5. **对每个新 right-hand side（右端项）求解。** 固定 KKT matrix 时，新的 \((q,r,c)\) 只改变子树价值的一次项。算法把 affine edge map（仿射边映射）向根收缩并反向展开，得到所有 \(p_i\)；根节点局部解出 \(x_\rho\)，随后把 parent-to-child state map（父到子状态映射）按同一 topology plan 复合、再从根向外反向展开。所有 \(u_e\) 和 \(y_i\) 最后由节点/边局部公式独立恢复。[pdf:E11]（PDF 物理页 9，Eq. (39)–(46) 与 Theorem 2）[pdf:E12]（PDF 物理页 10，Algorithm 1）

6. **事件与时间语义。** 自动驾驶例子用树分支显式表示信息事件，而不是在积分器里做 event root finding（事件根查找）：第 4 个信息阶段揭示相邻车让行/并线或前车制动，后续分支再揭示驾驶反应、湿滑路面和骑行者进入；根到叶轨迹在信息历史相同前重合，信息分开后才分离。[pdf:E19]（PDF 物理页 14，Fig. 4 与相邻正文）[pdf:E20]（PDF 物理页 15，Fig. 3）基础案例采用 4 s horizon（时域）和 0.25 s 步长，叶节点在第 13–16 阶段结束；论文没有报告多速率 time stepping（时间推进），后续 refinement（细化）仍是改变统一离散网格。[pdf:E18]（PDF 物理页 14，Section X 与 Eq. (57)）

7. **数值与执行平台。** 实现使用 JAX/XLA、静态整数计划、按 operation kind（操作类型）分组的批处理和 `jax.vmap`；同一拓扑下计划、编译结果和 factorization 可复用。论文明确提醒 PRAM 式 span 是算法依赖上界，不等于每层只有一次设备 kernel dispatch（内核发射），实际速度还受 occupancy（占用率）、memory traffic（存储流量）、fusion（融合）和编译缓存影响。[pdf:E15]（PDF 物理页 13，Section VIII）实际测试平台是 CPU 与 NVIDIA Tesla P100 GPU；FPGA 映射、RTL/HLS、定点位宽、片上存储和时序收敛均未报告。[pdf:E19]（PDF 物理页 14，Section XI-A 平台说明）[pdf:E21]（PDF 物理页 15，Table II）

## § 6 — 核心数学推导（无形式化数学则跳过）

Riccati recursion 的本质是 variable elimination（变量消元）：把一个子树内部状态、控制和乘子消去后，只留下根状态的二次 value function（价值函数）。本文的关键不是重新证明顺序 Riccati，而是找到一种在 rake 与 compress 下都闭合、且允许精确约束的边界表示。

**1. 良定性。** 论文采用的充分条件是

\[
R_e\succ0,\qquad \Delta_i\succeq0,\qquad
Q_i-\sum_{e\in\mathrm{out}(i)}M_eR_e^{-1}M_e^\top\succeq0.
\]

在这些条件下，primal Hessian（原始 Hessian）在 dynamics nullspace（动力学零空间）上正定，KKT matrix 非奇异，鞍点唯一。[pdf:E04]（PDF 物理页 3，Definition 1、Proposition 1、Eq. (3)–(4)）

**2. 每条边先局部消去控制。** 对原始边 \(e=(i,j)\)，齐次控制消元得到

\[
\bar A_e=A_e-B_eR_e^{-1}M_e^\top,\qquad
\bar C_e=\Delta_j+B_eR_e^{-1}B_e^\top,\qquad
\bar P_e=-M_eR_e^{-1}M_e^\top.
\]

这一步完全 edge-local（边局部），也是 contraction 期间唯一一次控制消元。[pdf:E07]（PDF 物理页 5，Eq. (11)–(13)）

**3. 用 extended-real conditional quadratic 表示一条已压缩边。** 当前 edge triple \(\alpha_e=(A_e,C_e,P_e)\) 表示

\[
\Phi_e(x_i,x_j)=\frac12x_i^\top P_ex_i+
\sup_\lambda\left\{\lambda^\top(A_ex_i-x_j)-\frac12\lambda^\top C_e\lambda\right\}.
\]

当 \(C_e\) 奇异时，若 \(A_ex_i-x_j\notin\mathrm{range}(C_e)\)，函数值就是 \(+\infty\)；因此它把 exact dynamics（精确动力学约束）作为扩展实值凸函数编码，不需要使用 \(C_e^{-1}\)。[pdf:E08]（PDF 物理页 6，Eq. (14) 与后续说明）

**4. rake 是把叶子价值折回父节点。** 若 \(j\) 是叶子、\(U_j\) 是其节点二次项，则

\[
\tau(\alpha_e,U_j)
=P_e+A_e^\top U_j(I+C_eU_j)^{-1}A_e.
\]

这正是对 \(x_j\) 做最小化后留给父状态 \(x_i\) 的新二次系数；同一父节点的多个叶贡献可相加。[pdf:E08]（PDF 物理页 6，Eq. (15)、(18)、(20)）

**5. compress 是条件价值的可结合复合。** 对连续边 \(e_\ell=(i,j)\)、\(e_r=(j,k)\)，令

\[
\widetilde P_{e_r}=P_{e_r}+U_j,\qquad
S=I+C_{e_\ell}\widetilde P_{e_r},
\]

\[
A_{e_{\ell r}}=A_{e_r}S^{-1}A_{e_\ell},
\]

\[
C_{e_{\ell r}}=C_{e_r}+A_{e_r}S^{-1}C_{e_\ell}A_{e_r}^\top,
\]

\[
P_{e_{\ell r}}=P_{e_\ell}+A_{e_\ell}^\top\widetilde P_{e_r}S^{-1}A_{e_\ell}.
\]

这些公式等价于消去共享中间状态 \(x_j\)。不变量

\[
U_i+\sum_{e\in\mathrm{out}(i)}P_e\succeq0,\qquad C_e\succeq0
\]

保证 \(I+C_eU\) 和 \(S\) 可逆；而三段链的任意 parenthesization（括号化）消去的是同一组内部状态，所以复合满足 associativity（结合律）。[pdf:E08]（PDF 物理页 6，Eq. (16)–(22) 与 Lemma 1、Proposition 3）[pdf:E09]（PDF 物理页 7，Eq. (23)）

**6. 反向展开恢复 Riccati Hessian，再构造局部反馈因子。** 收缩到根后，逆序用保存的 rake/compress 数据恢复每个 \(P_i\)，并证明

\[
V_i^0(x_i)=\frac12x_i^\top P_ix_i,
\]

即 \(P_i\) 是原始子树齐次价值函数的 Hessian。[pdf:E09]（PDF 物理页 7，Eq. (26)–(30) 与 Theorem 1）随后定义

\[
F_i=I+\Delta_iP_i,\qquad
W_i=P_iF_i^{-1}=(I+P_i\Delta_i)^{-1}P_i,
\]

\[
G_e=R_e+B_e^\top W_jB_e,\quad
H_e=B_e^\top W_jA_e+M_e^\top,
\]

\[
K_e=-G_e^{-1}H_e,\quad
A_e^{\mathrm{cl}}=A_e+B_eK_e,\quad
T_e=F_j^{-1}A_e^{\mathrm{cl}}.
\]

这些因子只由 KKT matrix 决定，可供多个 right-hand side 复用。[pdf:E10]（PDF 物理页 8，Eq. (34)–(35) 与 Local factor construction）

**7. 非齐次求解仍是两次可结合传播。** 子树价值一次项满足

\[
p_i=q_i+\sum_{e=(i,j)\in\mathrm{out}(i)}(Z_ep_j+z_e),
\quad Z_e=T_e^\top,
\quad z_e=K_e^\top r_e+(A_e^{\mathrm{cl}})^\top W_jc_j.
\]

这是一条向根的 affine recursion，可用同一 rake/compress plan 收缩和展开。[pdf:E10]（PDF 物理页 8，Eq. (36)–(38)）状态传播则使用 affine map \(\psi_e(x)=T_ex+b_e\)，两段映射按

\[
(T_r,b_r)\circ(T_\ell,b_\ell)=(T_rT_\ell,\,T_rb_\ell+b_r)
\]

复合。根状态和最终变量为

\[
x_\rho=-F_\rho^{-1}f_\rho,\qquad
x_j=T_ex_i+b_e,\qquad
u_e=K_ex_i+k_e,\qquad
y_i=P_ix_i+p_i.
\]

因此 backward value propagation（反向价值传播）和 forward state broadcast（正向状态广播）都被改写为相同拓扑上的 contraction/expansion。[pdf:E11]（PDF 物理页 9，Eq. (39)–(46)）

**8. 对数 span 的证明不只依赖“每轮删很多节点”。** 每个非平凡结构轮至少删除初始节点的三分之一，所以轮数不超过 \(\lceil\log_{3/2}N\rceil\)。[pdf:E12]（PDF 物理页 10，Lemma 3）高出度父节点还需要归约许多 sibling contributions；论文用 producer level（生产层级）定义 readiness weight \(w_j=2^{\ell_j}\)，再用保序 Shannon–Fano–Elias 型二叉树让较晚到达的输入走更短路径，避免额外乘上一个出度对数因子。[pdf:E13]（PDF 物理页 11，Eq. (47)–(49) 与 readiness-weighted reduction）由此得到任意出度下前向和反向依赖深度均为 \(O(\log N)\)。[pdf:E14]（PDF 物理页 12，Eq. (50)–(54) 与 Lemma 5）最终，对一次局部 dense LQR 操作的 work/span 分别记为 \(\chi(n,m)\)、\(\delta(n,m)\)，总复杂度为 \(O(N\chi(n,m))\) work、线性 storage 和 \(O(\delta(n,m)\log N)\) span；固定块维度时即为 \(O(N)\)、\(O(N)\)、\(O(\log N)\)。[pdf:E15]（PDF 物理页 13，Eq. (55)–(56) 与 Theorem 4）

## § 7 — 实验设计与结论

**问题一：算法是否真的解了同一个 KKT 系统？** 实验独立用 NumPy 组装 dense KKT matrix，并与 Algorithm 1 输出的 \((x,u,y)\) 比较；测试含 26 个 binary64 实例，覆盖 chain、star、不规则树、\(\Delta=0\)、\(\Delta\succeq0\) 和打乱节点拓扑顺序的随机树。答案是最大绝对 KKT residual 为 \(3.89\times10^{-15}\)，与独立稠密解的最大绝对差为 \(1.25\times10^{-14}\)，支持代数实现正确性，但样本规模和维度都较小。[pdf:E16]（PDF 物理页 13，Section IX-A）[pdf:E17]（PDF 物理页 14，Section IX-A 续）

**问题二：依赖深度是否真的不随树高或出度线性增长？** 实验统计四类拓扑的 primitive operation levels（原语操作层数）。当 \(N\) 从 16 增至 4096，chain 从 5 增至 13 层，star 从 6 增至 14 层，balanced tree 从 10 增至 34 层，comb 从 11 增至 35 层；chain/comb 的树高可线性增长，star 的出度可线性增长，而测得层数仍呈对数增长。[pdf:E17]（PDF 物理页 14，Table I）

**问题三：对数依赖能否转化为 accelerator speedup（加速器加速）？** 合成 benchmark 固定 \(n=8,m=2\)，在两核 Intel Xeon CPU 与 Tesla P100 GPU 上比较 sequential CPU tree Riccati 和 parallel GPU rake–compress；计时排除数据生成、计划、初始化、传输与 JIT compilation，并报告五次同步执行中位数。\(N=8192\) 时，chain/balanced/star 的 factorization 相对 sequential CPU 分别加速 11.08×、12.26×、15.14×，复用 factorization 的 solve 分别加速 19.06×、20.16×、24.33×。[pdf:E21]（PDF 物理页 15，Table II 与相邻正文）答案是“足够大且重复执行时可以”，而不是“一次调用必然更快”；comb 的 CPU baseline 因当前 JAX 编译问题未报告，也限制了比较完整性。

**问题四：完整 nonlinear scenario-tree MPC stack（非线性场景树 MPC 全栈）是否可运行？** 基础自动驾驶树有 \(N=102\)、13 个叶、树高 16、最大出度 3；primal–dual interior-point method 在 53 次迭代后，独立重算的最大 residual 分量为 \(9.44\times10^{-8}\)，计划包含 101 次 rake/compress，恰好对应每个非根节点一次消元。[pdf:E18]（PDF 物理页 14，Section X 与 Eq. (57)）[pdf:E19]（PDF 物理页 14，Fig. 4 与相邻正文）Fig. 3 中共享信息历史的策略轨迹先重合、后分离，直观检查了 nonanticipativity。[pdf:E20]（PDF 物理页 15，Fig. 3）

**问题五：时间网格细化后，kernel scaling（内核扩展性）和端到端时间如何变化？** 在 \(N=8185\) 的细化实例上，同一 parallel workload 从 CPU 移到 GPU，Newton factorization 加速 10.72×、复用因子 solve 加速 7.81×；完整 nonlinear solve 加速 14.74×。[pdf:E22]（PDF 物理页 15，Table III–IV）但 \(N=2044\) 需要 181 次 outer iteration 和 1101 次 logical line-search iteration，而 \(N=8185\) 只需 35 次且每次首个试探即接受，所以端到端时间不单由线性代数规模决定；论文据此把 Table IV 视为更受控的 kernel 比较。[pdf:E23]（PDF 物理页 15，refinement 分析）在 \(N=129\) 时 GPU 的独立 factorization/solve 反而略慢，说明发射与调度开销存在明确 crossover（交叉点）。[pdf:E24]（PDF 物理页 16，benchmark 结尾）

总体结论是：实验较强地支持“精确性、拓扑依赖深度和大规模稳态 GPU 加速”三项 claim；它没有证明一次性求解延迟、频繁变拓扑下的计划/编译成本、FPGA 性能，也没有覆盖不满足凸性条件的 KKT 系统。

## § 8 — Take-aways

**5 句话**

1. 论文把 scenario-tree Riccati 的主要并行瓶颈从树高依赖改写成 rake–compress contraction 的对数依赖图，同时保持线性总工作量。[pdf:E01]（PDF 物理页 1，Abstract）
2. 真正的代数核心是可处理奇异 \(C_e\) 的 extended-real conditional quadratic，它让精确 dynamics、叶消元和链段复合处在同一个闭合表示里。[pdf:E08]（PDF 物理页 6，Eq. (14)–(22)）
3. 反向展开不是附属步骤，而是保证每个 subtree Hessian、状态、控制和乘子都能从压缩带中精确恢复的组成部分。[pdf:E09]（PDF 物理页 7，Theorem 1）
4. 任意出度下的 \(O(\log N)\) span 还依赖 readiness-weighted sibling reduction，而不只是“每轮删掉三分之一节点”。[pdf:E13]（PDF 物理页 11，Eq. (47)–(49)）[pdf:E14]（PDF 物理页 12，Lemma 5）
5. 实验显示大树上 GPU speedup 会扩大，但结果是 post-compilation、可复用计划下的稳态性能，小实例仍可能因设备开销更慢。[pdf:E21]（PDF 物理页 15，Table II）[pdf:E24]（PDF 物理页 16，benchmark 结尾）

**3 句话**

1. 这是一种把 tree LQR 的 branch parallelism（分支并行）和 temporal parallelism（时间并行）统一进同一直接消元框架的方法。
2. 理论贡献的关键条件是固定局部维度、满足良定性假设并已获得可复用 topology plan；在这些条件下，factorization 和每个 right-hand-side solve 都是线性 work、对数 span。[pdf:E15]（PDF 物理页 13，Theorem 4）
3. 工程上最可信的结论是“大规模重复执行值得并行化”，而不是“任意规模、任意拓扑变化和任意硬件都能低延迟”。

**1 句话**

论文用一个对 rake 与 compress 都闭合的条件二次代数，把任意场景树的精确 Riccati 求解从树高串行改造成可反向恢复的对数深度数据流。

## § 9 — 最脆弱的假设

最脆弱的假设是 **Definition 1 的凸性与局部正定条件始终成立**，尤其是 \(R_e\succ0\) 和 \(Q_i-\sum M_eR_e^{-1}M_e^\top\succeq0\)。这不是普通技术条件，而是整套闭合代数的承重墙：它用于证明 KKT matrix 非奇异、rake/compress 中的 \(I+C_eU_j\) 与 \(S\) 可逆、恢复出的 \(P_i\) 半正定，以及局部 \(G_e\) 正定。[pdf:E04]（PDF 物理页 3，Definition 1 与 Proposition 1）[pdf:E08]（PDF 物理页 6，Lemma 1 与 Proposition 3）[pdf:E10]（PDF 物理页 8，Local factor construction）

基于证据的推断是：在一般 nonlinear MPC（非线性 MPC）中，碰撞代价、非线性 dynamics 的 exact Hessian 或不充分的 convexification（凸化）都可能产生 indefinite primal curvature（不定原始曲率）；正半定 dual regularization 本身不保证修复这部分曲率。若该假设失效，论文的“代数精确”不再有已证明的良定性基础，某个局部系统可能奇异或不定，核心 factorization/solve 可能直接中断，而不是仅仅精度稍差。

论文给出的证据是完整的充分条件证明、在这些条件下的 dense-KKT 对照，以及一个可收敛的非线性自动驾驶实例。[pdf:E16]（PDF 物理页 13，KKT accuracy）[pdf:E18]（PDF 物理页 14，自动驾驶模型与约束）但论文没有报告该案例各 Newton 步的最小特征值、离假设边界的 margin（裕度）、对 indefinite KKT 的压力测试，或失败时采用何种 primal regularization/convexification；因此它证明了“假设下正确”，尚未证明“常见非凸 MPC 子问题自然满足假设”。

## § 10 — 最小复现实验

一周内最值得复现的是“**代数精确性 + 拓扑依赖深度**”，不必先复现完整 interior-point solver。

数据上，生成 chain、star、balanced binary tree 和 comb 四类 parent array，取 \(N\in\{16,64,256,1024,4096\}\)，局部维度先用 \(n=4,m=2\)。构造 \(R_e\succ0\)、\(\Delta_i=0\) 与 \(0.02I\) 两组，并把 \(Q_i\) 设成足以满足 Definition 1 的正半定矩阵；再随机打乱节点编号，避免实现偷偷依赖拓扑顺序。这个设计直接对应论文的 KKT accuracy 与 Table I 测试范围。[pdf:E16]（PDF 物理页 13，Section IX-A）[pdf:E17]（PDF 物理页 14，Table I）

实现上只需四部分：小规模 dense KKT reference；顺序 postorder tree Riccati；rake/compress topology planner；按 Eq. (13)–(46) 完成 factorization、affine solve 和 state recovery。先在 \(N\le128\) 上逐项比较 \((x,u,y)\)，再只统计大树的 rake/compress 数量和 dependency levels；最后在同一 CPU 或同一 GPU backend 上做 warm-up 后计时，同时另报包含 plan 构造的总时间。

测量四个量：KKT infinity residual、相对 dense-solution error、rake+compress 总数是否为 \(N-1\)、依赖层数对 \(\log N\) 的增长斜率。支持核心 claim 的标准可以设为 binary64 下小规模残差与相对误差均低于 \(10^{-10}\)，所有拓扑操作数线性、chain/star/comb 的层数明显远低于树高或最大出度，并随 \(\log N\) 增长；若误差随拓扑系统性放大、某类树依赖层数恢复为 \(\Theta(N)\)，或 reverse expansion 不能恢复 dense KKT 解，就直接反驳核心机制。论文的报告值可作为上限参考，而不应被当作必须逐位复现的硬阈值。[pdf:E15]（PDF 物理页 13，Theorem 4）[pdf:E16]（PDF 物理页 13，报告残差）

## § 11 — 最强反例设计

最有力的工程反例不是再造一个小型数值误差，而是检验论文观察到的 speedup 是否主要来自 **跨硬件比较和可摊销 setup**，而不是 rake–compress 本身。

构造一系列每个 MPC 周期都会重新剪枝、重新排序或改变终止深度的 irregular trees，使 parent array 每次都变化；规模覆盖 \(N=512\) 到 \(8192\)，局部矩阵保持相同统计分布，并加入 comb 与“长主干 + 突发高出度”拓扑。对每个周期计入 planner、dependency-level 构造、JAX tracing/JIT、host–device transfer 和第一次执行，比较三种同硬件基线：同一 GPU 上的 level-synchronous sequential/tree Riccati、同一 GPU 上的 rake–compress，以及 CPU 上的优化顺序版本。所有方法用同一 dense/reference residual 检查正确性。

这项反例针对一个具体替代解释：论文 Table II 的主比较是 two-core CPU sequential 对 P100 GPU parallel，而且明确排除了 planning、初始化、传输和 JIT；当前 host planner 还有 \(O(N\log N)\) 最坏预处理工作，并假定 topology plan 可跨 MPC 迭代复用。[pdf:E15]（PDF 物理页 13，planner 与 JAX implementation）[pdf:E21]（PDF 物理页 15，Table II 计时边界）若动态拓扑下 inclusive latency（全包延迟）长期差于同 GPU 基线，或同 GPU 上优势消失，那么“观察到的实时收益来自 contraction 的对数依赖”这一解释就被显著削弱；若大规模下仍稳定占优，才说明代数重排而非硬件切换是主因。

论文自己的 refinement 已显示端到端时间会被 nonlinear convergence 强烈扰动，且小规模时 GPU kernel 反而更慢。[pdf:E23]（PDF 物理页 15，refinement 分析）[pdf:E24]（PDF 物理页 16，crossover 说明）因此，这个反例可能推翻的是“实际 scenario-tree MPC 的普遍低延迟价值”，而不是 Definition 1 下的 exactness theorem 或 \(O(\log N)\) 抽象 span 证明；两类 claim 必须分开判断。

## § 12 — Follow-up Research Bet

**主押注：把 rooted scenario tree（有根场景树）升级为允许分支重新汇合的 scenario DAG（场景有向无环图）。这是证据约束下的候选判断，不声称已完成最近工作检索或具有 novelty。**

新的研究问题是：能否把本文只依赖边界状态的 conditional-value algebra，从“一条边只有一个父边界、整张图无汇合”的树推广到“不同信息历史可共享同一未来物理模式或同一后缀”的 recombining DAG（可重合 DAG），并仍然 exact 地恢复每条历史上的 primal–dual 量？一旦成立，它首次使 exact parallel MPC 的成本按“不同的未来物理状态/模式数”而不是按“完整历史路径复制数”增长；对于 Markov mode lattice（马尔可夫模式格）、故障恢复后重新进入同一运行模式、或多代理意图在若干阶段后不再影响未来 dynamics 的问题，这会改变可处理的场景规模。

核心机制的因果链是：Eq. (14)–(17) 已证明一个已消去组件可由固定维 boundary conditional quadratic 表示，并可通过局部消元复合，而表示尺寸与被压缩子树内部节点数无关。[pdf:E08]（PDF 物理页 6，Eq. (14)–(17)）下一步不是给原算法加一个外部缓存，而是引入新的 **merge primitive（汇合原语）**：两个或多个历史边进入一个共享后缀时，用包含多个入边界与一个共享状态的 separator conditional quadratic（分隔集条件二次函数）表示该组件，通过 saddle Schur complement（鞍点 Schur 补）消去共享内部变量，并在 reverse pass 中恢复各历史特有乘子。若每个 merge 的 separator width（分隔宽度）有界，rake、compress、merge 三类原语可能让 work 随 DAG 中独特节点数线性增长、span 随其 contraction depth 对数增长；若宽度随历史数膨胀，方案就失败。

它至少改变四个基本设计变量：问题拓扑从 tree 变为 recombining DAG；状态表示从单边界 edge triple 变为多边界 separator object；复杂度自变量从树节点数 \(N\) 变为独特 DAG 节点数加 separator width；实验对象从 tree height/out-degree 变为 history duplication ratio（历史重复率）与 graph width（图宽）。论文的自动驾驶信息树展示了延迟揭示和多阶段分支，细化实验又表明节点数扩大直接决定线性代数负担；这些细节说明“避免重复表示相同未来后缀”若可实现，会有实质收益，但 Figure 4 本身并未证明其分支实际可汇合。[pdf:E19]（PDF 物理页 14，Fig. 4）[pdf:E22]（PDF 物理页 15，Table III–IV）

最大研究收益是把 exact direct scenario optimization 从纯树扩展到含 reconvergence（重新汇合）的不确定性过程，同时仍保留完整 primal–dual 恢复和硬件并行；最大科学风险是 merge 会引入不断增长的 separator，破坏“边界维度与组件规模无关”的核心闭合性，使复杂度退化为 graph treewidth（图树宽）的指数函数。与论文所述最近工作相比，Miller–Reif 类 tree contraction、tree-coupled saddle systems 以及 branch MPC GPU 方法的基本对象仍是树或路径分解；这个押注改变的是数学对象和消元代数，而不是给既有树调度换一个 scheduler。[pdf:E02]（PDF 物理页 2，Related Work）[pdf:E03]（PDF 物理页 3，最近 branch MPC 对比）

首个证伪实验应使用可精确组装 dense KKT 的“diamond chain（菱形链）”：每个单元先分成两条拥有不同局部代价的历史，再进入完全共享的后缀状态，连续串接多个单元。实现一个最小 merge rule，比较三种表示：复制后缀的普通树、去重后的 DAG、独立 dense KKT；逐步增加 diamond 数和 separator width，测量解误差、残差、记录尺寸与局部运算数。核心机制得到支持的条件是 DAG 解与 dense KKT 一致、所有 branch-specific multipliers 可逆向恢复，而且记录和 work 随独特 DAG 节点数增长；若 separator 尺寸随历史数增长、反向乘子不唯一或结果只能靠简单 memoization（记忆化）复用同一数值后缀，则应否决该方向。要求保留分支前不同代价并输出所有乘子，可以把真正的 coupled merge algebra 与“只是缓存重复计算”这一最强替代解释区分开。

**Wild-card alternative：**把静态 dependency levels、局部 dense kernels 和 expansion tape 共同映射为流式 FPGA dataflow fabric（FPGA 数据流架构），让 factorization、affine solve 与 state broadcast 作为三条可复用片上流水线运行；它改变的是硬件通信与存储拓扑，而不是场景图的数学结构。
