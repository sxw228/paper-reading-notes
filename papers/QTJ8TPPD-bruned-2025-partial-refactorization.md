# Partial Refactorization Techniques for Electromagnetic Transient Simulations

作者：Boris Bruned、Anas Abusalah、Jean Mahseredjian、Sébastien Dennetière、Omar Saad  
出处：IEEE Transactions on Power Delivery，Vol. 40，No. 4，pp. 1795–1801  
年份：2025，期刊期次为 August 2025  
DOI：10.1109/TPWRD.2025.3574482  
Zotero key：QTJ8TPPD  
以上信息与 PDF 首页一致。[pdf:E01]

> 证据说明：`[pdf:E..]` 对应源 PDF 物理页与 Eq./Fig./Table 定位。论文事实据此标注；推导、批评、复现实验设计和研究押注由本卡明确区分。

## § 1 — 研究问题与重要性

**本文解决的是 EMT 仿真中的重复稀疏 LU 重算问题：网络矩阵只有部分数值改变时，怎样避免重新处理实际上未受影响的因子列？** 在电力电子设备密集的电网中，开关换相会改变网络矩阵；非线性元件的迭代线性化也会反复更新矩阵。即使网络拓扑和稀疏结构没有整体变化，求解器仍可能为这些局部变化付出大范围 refactorization 的代价。作者把这一问题定位为大规模 EMT 仿真的重要计算瓶颈，特别关联新能源与 inverter-based resources 的详细建模需求。定位：物理页 1，Abstract 与 Introduction。[pdf:E02]

这里需要区分两个动作。初次 factorization 要确定数值 LU 因子，并可能通过 partial pivoting 调整行次序；后续 refactorization 则尽量复用已有的排列和稀疏结构，只更新数值。传统 KLU 的 refactorization 仍处理所有列，已有 MKLU 方法则从最早改变的列一直处理到最后一列。后者已经利用了一部分局部性，但列号上的先后关系比真正的计算依赖更保守。定位：物理页 2，Section III-A、Algorithm 2、Eqs. (8)–(9)。[pdf:E04]

本文的价值是保持原有离散网络方程与详细设备模型，减少求解器内部的无效计算。作者研究两种粒度的局部性：一种沿 LU 因子的列依赖传播，另一种利用 BTF 将网络分成较小子矩阵，只更新发生变化的部分。论文的实测对象是 CPU 上的 EMTP/MKLU；实时仿真和并行执行是相关应用背景，本文没有提供 FPGA 或实时 deadline 的实现结果。定位：物理页 1，Introduction；物理页 4，Sections III-C、IV。[pdf:E02][pdf:E07][pdf:E11]

## § 2 — 前人工作与不足

**最直接的基线是 KLU 与已有 MKLU，而非重新发明一种 LU 分解。** 按本文对参考文献 [4]、[5] 的介绍，KLU 使用 left-looking Gilbert–Peierls 算法计算稀疏 LU，初次分解支持 partial pivoting，后续可以复用已有结构进行无 pivoting 的 refactorization。参考文献 [6] 在此基础上加入 pivot validity test，必要时重新做完整 factorization，并提出 RefactChg：从最早发生变化的列开始重算。它的工程优势是实现直接，能够复用已经正确的前缀；其剩余成本来自保守的后缀重算，即使某个后续列与变化列没有依赖关系，也会被处理。定位：物理页 1，Introduction；物理页 2，Section III-A。[pdf:E02][pdf:E04]

**路径思想已有明确前史，本文的增量在于适用于非对称 LU 因子的 left-looking 表述与实现。** 作者追溯到 Tinney、Brandwajn 与 Chan 的 sparse vector methods，参考文献 [9] 用路径减少稀疏右端项对应的代入工作；参考文献 [10] 将其用于无 pivoting 的 Crout 部分重分解；参考文献 [11] 根据依赖关系并行调度 refactorization；参考文献 [12] 将 factorization path 用于实时 EMT 的部分重分解。以上比较均来自本文的文献回顾，相关文献全文没有包含在本次资料中。定位：物理页 1，Introduction；物理页 7，References。[pdf:E02][pdf:E08]

本文指出，[12] 的路径计算依赖对称 LU 结构，可以从 CSC 格式的 L 读取关系；一般 left-looking 分解可能不保持这种结构对称性。当 L 的依赖图不等于 U 图的转置时，直接沿用该做法可能得到错误的依赖方向或依赖集合。因此，本文明确从 U 建图，并用适于按行访问的 CSR 支持搜索。这个差异是算法适用条件的变化，不能概括成给已有方法换了一个存储格式。定位：物理页 3，Section III-B 最后两段。[pdf:E06]

**BTF 也属于已有工具，但本文改变了它的使用目标。** 参考文献 [13] 提供 block triangular ordering，参考文献 [6] 已将其用于子系统解耦和并行计算。本文进一步在顺序执行中利用它：识别哪些对角子块发生变化，只在这些子块上执行 RefactChg。已有并行解耦并不会自动省去未变化子块的数值重算，需要求解器显式维护更新范围。定位：物理页 4，Section III-C；物理页 7，References。[pdf:E07][pdf:E08]

因此，本文最扎实的贡献边界是：在已有 KLU/MKLU 框架内，把“列号后缀”改为“真实依赖闭包”，并把已有 BTF 分块用于选择性 refactorization。作者关于通用性与首次表述的主张见首页；仅凭本文的相关工作讨论，还不足以独立判定所有 sparse direct solver 文献中的优先权。[pdf:E02]

## § 3 — 重建作者的思考路径

下面重建的是一个研究者从已有知识出发可能经历的推理过程，而非作者公开记录的研究历程。

首先，已有 RefactChg 已经说明：发生变化之前的列通常可以复用。接下来最自然的问题是，发生变化之后的列是否真的全部需要重算？left-looking 算法逐列向前寻找所需信息，因此“列位于变化之后”只是可能受影响的必要位置条件，并不能说明存在实际依赖。已有 sparse vector methods 与部分重分解工作又提示，稀疏计算的影响范围可以通过图上的可达性描述。这个问题由算法结构和已有方法直接提出。定位：物理页 1，Introduction；物理页 2，Algorithm 1、Eqs. (8)–(9)。[pdf:E02][pdf:E03][pdf:E04]

其次，要找到影响范围，应回到三角求解的算术操作，而不是根据电网物理邻接猜测。某列是否使用此前某列的 L 值，取决于相应 U 元素是否属于有效依赖。由此可以提出一个可检验的方向：从变化列出发，沿列依赖逐层传播，直到没有新的下游列。参考文献 [11] 已用类似依赖关系组织并行任务，因此把这种关系用于排除不必要任务，在当时已有技术背景下是合理的一步。定位：物理页 3，Algorithm 3 与 Section III-B。[pdf:E05]

第三，工程实现会立即遇到两个问题。一个是 pivoting 会改变 LU 结构，不能假定原始网络矩阵的对称稀疏模式会一直保留到因子；另一个是路径计算本身有成本，如果完整分解频繁发生，预先计算的路径可能尚未充分复用便失效。因而研究者需要分别追问“依赖到底应从哪个因子读取”和“路径应何时计算”。这些问题来自既有 pivoting 机制与图搜索成本，而不是依赖新方法已经成功的结果。定位：物理页 2，Section III-A；物理页 3，Section III-B 末段。[pdf:E04][pdf:E06]

最后，输电线路传播延迟本来就可能把同一时刻的网络计算分成独立子系统。既然已有 BTF 能识别这些子系统，就可以进一步追问：一次设备更新是否需要让所有子系统重新分解？这提供了与列依赖不同的第二层局部性，即物理模型带来的块级独立性。定位：物理页 4，Section III-C。[pdf:E07]

## § 4 — 核心 Intuition

一个设备发生变化，真正需要重算的是计算上依赖它的那些因子列，而不是排在它后面的所有列。本文沿 LU 分解中的依赖关系追踪变化，把不在传播范围内的列直接保留下来。若网络还能分成独立子系统，就进一步让没有变化的子系统完全避开重分解。定位：物理页 3，Section III-B；物理页 4，Section III-C。[pdf:E05][pdf:E07]

## § 5 — 具体方法与完整 Pipeline

以论文实际使用的 Celtic-grid 故障仿真为例，输入是详细电网模型、设备状态、控制量及离散后的历史项，输出是各时间点的网络状态及机器功率等波形。该案例的网络矩阵有 27,652 个未知量、173,296 个非零元；BTF 得到 428 个块，最大块为 1,261 阶。论文没有公开某一次设备换相对应的矩阵坐标，因此下面用真实案例说明系统流程，再在数学部分用作者的教学图说明单次列依赖。定位：物理页 5，Fig. 3、Table II。[pdf:E14]

1. **建立离散网络方程并初始化。** EMTP 使用 MANA 和 companion circuit models，把节点电压、附加支路未知量以及历史项写成每个时间点需求解的线性系统。非线性设备提供线性化 Norton 等效，迭代中的网络矩阵相当于 Jacobian。实验由 Load-Flow 解自动初始化，包括变流器组件和控制系统。论文没有说明采用哪一种具体积分公式。定位：物理页 2，Section II、Eqs. (1)–(2)；物理页 5，实验设置。[pdf:E03][pdf:E12]

2. **完成初次稀疏分析与数值分解。** 求解器通过行列重排减少 fill-in，文中介绍了 AMD ordering，并用带 partial pivoting 的 left-looking Gilbert–Peierls 算法得到初始 LU。最终行排列包含数值 pivoting 的影响。若采用 BTF，则先识别对角子块。定位：物理页 2，Eqs. (3)–(7)、Algorithm 1；物理页 4，Section III-C。[pdf:E03][pdf:E07]

3. **把设备更新映射到分解后的列。** 每次开关状态或非线性线性化发生变化，记录原始矩阵中被更新的位置。原矩阵列通过逆列排列映射到重排矩阵列；随后在 U 的依赖图中查找受影响范围。U 使用 CSR 组织邻接访问，使 DFS 能直接读取每个顶点的后继。定位：物理页 3，Section III-B 末两段。[pdf:E06]

4. **准备或复用 factorization paths。** RefactPathPre 提前为所有潜在可变列计算路径；RefactPath 则在某列第一次实际变化时才计算，并在后续使用中复用。每次更新把有关路径取并集，得到本轮需要处理的列集合。pivot 排列发生改变后，旧路径需要作废并重新建立。定位：物理页 3，Section III-B 末段；物理页 4，Algorithms 4–6。[pdf:E06][pdf:E10]

5. **只重算选中的列，再求解网络状态。** 选中的列按列序执行无 pivoting 的 left-looking refactorization；其余列保留已有数值。每列仍执行 pivot validity test，若原 pivot 不再有效，则重新进行完整 factorization。更新 LU 后，通过 forward substitution 和 backward substitution 解出本轮网络状态。本文的路径方法针对因子重算，没有同时提出一种新的部分三角代入方案。定位：物理页 2，Eqs. (4)–(5)、Algorithm 2；物理页 3，Section III-B。[pdf:E03][pdf:E04][pdf:E05]

6. **BTF 方案单独利用块级更新范围。** RefactChg+BTF 只访问发生变化的子块，并在块内从最早变化的列开始重算。Table I 把它与 RefactPath、RefactPathPre 列为不同测试方法；论文没有报告 RefactPath+BTF 组合的独立实验结果。定位：物理页 4，Section III-C、Table I。[pdf:E07][pdf:E10]

7. **沿原仿真时间轴继续推进。** 非线性迭代完成后更新状态、历史项和控制系统，再进入下一时间点。时间步长属于原 EMT 仿真设置，本文没有提出多速率推进或新的开关事件插值方法。实际运行平台是 AMD Ryzen Threadripper PRO 5995WX，标称 2.70 GHz；全文未报告 FPGA 映射、定点格式、浮点位宽、线程配置或硬件资源占用。定位：物理页 4，Section IV；物理页 5，时间步长设置；物理页 6，Table V 对 Total Time 的说明。[pdf:E11][pdf:E12][pdf:E17]

## § 6 — 核心数学推导（无形式化数学则跳过）

### 从电路方程到可以复用的 LU

论文从以下网络方程出发：

$$Ax=b. \tag{论文 Eq. 1}$$

MANA 的分块形式是：

$$
\begin{bmatrix}Y_n&A_c\\A_d&A_x\end{bmatrix}
\begin{bmatrix}v_n\\x_x\end{bmatrix}
=
\begin{bmatrix}i_n\\b_x\end{bmatrix}.
$$

其中，$Y_n$ 是节点导纳矩阵；$A_c,A_d,A_x$ 来自附加方程；$v_n$ 为节点电压，$x_x$ 包含支路电流、理想开关电流等附加未知量；$i_n$ 包含电流注入和离散历史项，$b_x$ 是附加方程的已知量。工程上，设备状态主要通过矩阵系数和右端项进入网络求解。仅改变右端项时可以复用已有 LU，改变矩阵系数时才需要考虑因子更新。定位：物理页 2，Eqs. (1)–(2) 及其解释。[pdf:E03]

论文先写出 $A=LU$，再给出 $Lx'=b$ 和 $Ux=x'$。L 是下三角因子，U 是上三角因子；把复杂线性系统拆成两次三角求解，能够在同一矩阵对应多个求解时复用分解结果。重排步骤为 $A'=PAQ$，数值 pivoting 后为 $A''=P_pA'$，其中 P、Q 是初始行列排列，$P_p$ 是 partial pivoting 造成的行排列。定位：物理页 2，Eqs. (3)–(7)。[pdf:E03]

为避免把原始未知量与重排未知量混淆，可将这些式子合并为以下等价写法，这是本卡的记号整理：

$$A''=P_pPAQ=LU,\qquad Ly=P_pPb,\qquad Uz=y,\qquad x=Qz.$$

这说明排列不改变原方程表达的物理问题，但会改变因子中的列序和依赖结构，因此路径必须建立在实际使用的 LU 上。[pdf:E03]

### 为什么依赖关系来自 U

left-looking 算法计算第 k 列时，先以 $A''(:,k)$ 为输入求解一个下三角系统。Algorithm 3 的核心更新是：

$$w(j+1:n)\leftarrow w(j+1:n)-L(j+1:n,j)w(j),$$

其中遍历 $j<k$ 且 $U(j,k)\ne0$ 的前驱列。随后把 w 的上部写入 U 的第 k 列，下部除以对角 pivot 后写入 L 的第 k 列。工程含义是：计算第 k 列会读取哪些旧 L 列，由 U 第 k 列中的依赖位置决定。定位：物理页 2，Algorithms 1–2；物理页 3，Algorithm 3。[pdf:E03][pdf:E04][pdf:E05]

因此，若 $U(j,k)\ne0$，就建立有向边 $j\to k$。忽略对角自环后，边总是从较小列号指向较大列号，形成可以按列序执行的依赖图。变化从一列传播到它的直接后继，再传播到后继的后继。论文用 $G_U$ 表示这个图，并给出：

$$C_k=\operatorname{Reach}_{G_U}(k),\qquad C_{\mathrm{RefactPath}}=\bigcup_{k\in C}C_k. \tag{论文 Eqs. 10–11}$$

这里的 C 是发生输入变化的列集合，$C_k$ 是对应路径，Reach 表示可达集合。定位：物理页 3，Section III-B、Eqs. (10)–(11)。[pdf:E05]

对实现而言，**必须把变化列自身也放进重算集合**。若 Reach 的约定不包含起点，可把完整集合明确写成：

$$\widehat C=\bigcup_{k\in C}\left(\{k\}\cup\operatorname{Reach}^{+}_{G_U}(k)\right).$$

这是对实现语义的显式化。其正确性可以按列序理解：闭包外的列既没有原始输入变化，也没有变化的前驱因子；闭包内的列则在所有必要前驱更新后重新计算。在 pivot 次序和既有因子稀疏结构保持有效的条件下，这足以传播矩阵变化。这个集合是基于结构依赖的列级闭包，特殊数值抵消还可能使部分元素实际不变，因此“最小”应理解为该结构依赖模型下的最小重算范围，而非对所有数值巧合都最小。论文没有给出更一般的误差界或完整形式化证明。[pdf:E04][pdf:E05][pdf:E06]

### 图例存在可定位的集合错误

物理页 3 的 Fig. 1 中，从列 1 出发可以到达列 4、8、10；从列 2 出发可以到达列 6、7、9。正文也分别列出了这两组后继。可是 Eq. (12) 给出的 RefactPath 集合为 $\{4,6,7,8,10\}$，其中遗漏了列 9，同时没有列出输入已变化的列 1、2。定位：物理页 3，Figs. 1–2、Eq. (12) 及相邻正文。[pdf:E09]

按图的闭包并包含种子列，本卡得到的完整重算集合是：

$$\widehat C=\{1,2,4,6,7,8,9,10\}.$$

因此，这个教学图应理解为处理 8 列而非全部 10 列，不能把印出的集合直接写进实现。该修正来自对图和集合运算的直接核对；论文没有说明实现是否使用了同样的集合表示。整体路径机制仍可由 Algorithm 3 和 Eqs. (10)–(11) 独立重建。[pdf:E05][pdf:E09]

### 三种重算范围与 BTF 的区别

传统 Refact 的列集合是 $\{1,\ldots,n\}$；RefactChg 的集合是 $\{n_{\mathrm{chg}},\ldots,n\}$，其中 $n_{\mathrm{chg}}$ 为最早变化的列号。RefactPath 用依赖闭包替换这个后缀。它真正省去的是“列号更晚，但不存在依赖路径”的列。定位：物理页 2，Eqs. (8)–(9)；物理页 3，Eqs. (10)–(11)。[pdf:E04][pdf:E05]

BTF 采用另一层结构。论文先给出一般的块上三角形式：

$$A_{\mathrm{BTF}}=P_{\mathrm{BTF}}AQ_{\mathrm{BTF}}=[A_{ij}],\qquad A_{ij}=0\quad(i>j).$$

一般块上三角矩阵的子系统仍可能通过非对角块耦合；只有进一步形成论文 Eq. (14) 的块对角结构，子系统才在同一时刻完全独立：

$$A_{\mathrm{BTF}}=\operatorname{diag}(A_{11},\ldots,A_{mm}).$$

这里 m 为块数，$P_{\mathrm{BTF}},Q_{\mathrm{BTF}}$ 为相应排列。论文将常见网络中的块对角结构联系到稀疏模式及输电线路传播延迟：跨线路的信息进入延迟历史项，使部分网络在当前时间点可以独立求解。RefactChg+BTF 就在发生变化的块内执行后缀重算。定位：物理页 4，Eqs. (13)–(14) 与 Section III-C。[pdf:E07]

## § 7 — 实验设计与结论

**总体设计。** 论文测试了 IEEE-39、WP-grid、400kV-Fr-grid、IEEE-118、HVDC-BM5、T0-grid-AVM、T0-grid-DM 和 Celtic-grid，共八个案例。矩阵规模从 499 阶到 27,652 阶，非零元从 1,711 个到 173,296 个。设备覆盖非线性电阻、变压器磁化非线性电感、ZnO 避雷器、受控理想开关、晶闸管及同步和异步机器；不同案例的这些设备组合并不相同。定位：物理页 4–5，案例说明；物理页 5，Tables II–III。[pdf:E11][pdf:E12][pdf:E13][pdf:E14]

统一工况写为在 1 s 时施加持续 100 ms 的三相接地故障。通常使用 50 μs 步长，IEEE-39 为 20 μs，T0-grid-DM 为 10 μs；除 T0-grid-DM 写为仿真 1 s 外，其余案例为 2 s。因 T0-grid-DM 的结束时间与统一故障开始时间重合，正文不足以确认该案例是否包含完整故障后时间窗，这限制了对其故障波形覆盖范围的判断。定位：物理页 4–5，案例时长与故障设置。[pdf:E11][pdf:E12]

- **问题：省去列重算是否改变解？ → 实验：与完整 Refact 输出比较。 → 答案：在所选输出上，RefactChg 和 RefactPath 的报告误差均为零。** 论文使用 $e\%=100\|\tilde f-f\|_2/\|f\|_2$，f 为 Refact 参考输出，$\tilde f$ 为待比较输出；通常检查故障附近机器功率，HVDC-BM5 检查 DC 电压。Table IV 中 RefactChg 与 RefactPath 的八个结果都是 0；RefactChg+BTF 的最大报告值为 HVDC-BM5 的 4.9×10⁻²%。这是选定输出的比较结果，不能扩展成所有内部状态逐位一致。定位：物理页 5，Eq. (15)、Table IV 及说明。[pdf:E15]

- **问题：BTF 改变排列后，主要暂态趋势是否保留？ → 实验：叠加关键波形。 → 答案：展示的两组曲线吻合良好。** Fig. 4 比较 HVDC-BM5 的 DC 电压，纵轴为 pu、横轴为秒；Fig. 5 比较 Celtic-grid 的机器功率，纵轴同样为 pu。作者据此支持 BTF 方案的精度判断，但没有用这些图单独量化尖峰时刻误差或事件时间偏差。定位：物理页 6，Figs. 4–5 及图注。[pdf:E16]

- **问题：新方法比已有 MKLU 的 RefactChg 快多少？ → 实验：以 RefactChg 的稀疏线性系统求解时间为基准。 → 答案：收益明显但具有案例依赖性。** Table VI 中，Celtic-grid 的 RefactPath speedup 为 3.01，RefactChg+BTF 为 2.80；IEEE-118 分别为 1.70 和 1.14。HVDC-BM5 分别为 1.15 和 1.14，差距很小；T0-grid-DM 则是 BTF 的 1.38 高于路径法的 1.33。因此，路径法在多数案例领先，但不构成逐案例支配。定位：物理页 6，Table VI。[pdf:E18]

- **问题：什么工况使路径法更有利？ → 实验：结合更新频率和重新 pivoting 频率分析案例。 → 答案：反复更新、路径能够长期复用的案例最有利。** Celtic-grid 的 Refact Freq 为 99.59%，Fact Freq 为 0.04%；HVDC-BM5 和 T0-grid-DM 的 Fact Freq 则分别为 19.90% 和 21.69%。作者把后两者较小的路径法优势联系到频繁完整分解后路径失效。表中频率沿用作者的统计口径，正文没有充分明确所有频率的分母，不能直接把它们解释为时间步比例。定位：物理页 6，Table V 与性能讨论。[pdf:E17][pdf:E20]

- **问题：提前计算所有路径是否更划算？ → 实验：比较 RefactPath 与 RefactPathPre。 → 答案：在展示的两个频繁重新 pivoting 案例中，按需计算更好。** Table VII 以 RefactPath 为 1，RefactPathPre 在 HVDC-BM5 和 T0-grid-DM 中的相对性能分别为 0.57 和 0.53。作者解释为完整预计算花费较大，且完整分解后需要丢弃。这个实验只覆盖表中两个案例，不能据此证明所有更新分布下按需计算始终优于预计算。定位：物理页 6，Table VII 及相邻正文。[pdf:E19]

**时序与资源结论应限制在 CPU 离线求解。** Table V 把 Solver Time 与包括历史项、控制系统等开销的 Total Time 分开；例如 Celtic-grid 的 2 s 仿真，RefactChg 基准下分别耗时 254.45 s 和 327.43 s。Table VI 的 speedup 对应稀疏线性求解部分，不能直接当成完整仿真的加速比。论文没有报告各新方法的完整端到端时间、重复实验方差、路径存储量、实时最坏步时延或 FPGA 资源结果。定位：物理页 6，Tables V–VI 及其解释。[pdf:E17][pdf:E18]

## § 8 — Take-aways

**五句话。** EMT 中设备局部更新造成的 LU 重算，可以通过因子依赖图而非列号后缀来限定范围。[pdf:E04][pdf:E05] 对一般非对称 LU，路径应依据 U 的实际依赖建立，不能无条件借用 L 的转置关系。[pdf:E06] BTF 提供块级独立性，路径法提供列级传播范围，两者利用的结构不同。[pdf:E05][pdf:E07] 八个案例中，路径法相对 RefactChg 的最高求解 speedup 为 3.01，而 BTF 方案最高为 2.80。[pdf:E18] 实际收益取决于受影响范围与路径复用成本，印刷图例中的集合还需要在复现时修正。[pdf:E09][pdf:E19][pdf:E20]

**三句话。** 本文的核心是让重新计算的范围匹配实际计算依赖。[pdf:E05] 结果支持它在所测网络中节省求解时间，并保持所选输出的数值精度。[pdf:E15][pdf:E18] 判断可迁移性时，应检查依赖闭包、pivot 变化和整机时间，而不仅是矩阵规模。[pdf:E17][pdf:E20]

**一句话。** 把矩阵局部变化转化为 LU 依赖图上的传播范围，是本文最值得复用的机制。[pdf:E05]

## § 9 — 最脆弱的假设

**最关键的假设是：输入矩阵的局部变化，在消元后的依赖图中仍保留足够的计算局部性。** 更精确地说，按实际算术代价计算，依赖闭包需要小到能够让省下的列重算超过路径搜索、集合合并和缓存维护成本。这个假设不成立时，算法仍可能正确求解，但本文最核心的加速贡献会消失。

物理邻接上的局部性不能保证消元后的局部性。一个设备可能只改变少量矩阵项，却位于许多后续列的共同前驱；消元产生的 fill-in 也可能把局部变化连接到很大的后继区域。AMD 以减少 fill-in 为主要目的，本文没有给出它同时最小化动态更新闭包的论证。即使 pivot 长期有效，缓存得再好，也无法把本来就覆盖几乎全部列的闭包变短。这个判断直接来自 left-looking 依赖传播机制。定位：物理页 2，ordering 说明；物理页 3，Algorithm 3、Eqs. (10)–(11)。[pdf:E03][pdf:E05]

论文的支持证据是间接的：Celtic-grid 和 IEEE-118 的加速表明，在这些实际模型与更新序列中，确实省去了有意义的工作。缺失的证据则是每次更新的闭包大小分布、闭包对应的算术量、图维护时间，以及固定网络上改变更新位置的受控实验。HVDC-BM5 的较小收益也无法单独用于判断闭包是否很大，因为它同时存在频繁重新 pivoting。定位：物理页 6，Tables V–VI 与性能解释。[pdf:E17][pdf:E18][pdf:E20]

因此，本文较强地证明了这些案例中的工程收益，却没有建立“稀疏设备更新通常意味着便宜的 LU 更新”这一更广泛命题。

## § 10 — 最小复现实验

**一周内最值得复现的是依赖闭包机制的正确性和工作量收益，而不是完整重建 EMTP 案例。** 以下是建议实验，不是论文已完成的实验。

首先，用物理页 3 的教学 U 图建立单元测试。构造一个单位下三角 L 和具有该图结构的 U，再生成对应矩阵；更新列 1、2 后，检查实现是否包含种子列与列 9。这一步可以直接捕获 Eq. (12) 的集合问题。[pdf:E09]

随后生成两组小型、固定稀疏结构的网络矩阵序列：一组具有明显分支依赖，另一组具有长链式传播。矩阵可以由带接地支路的线性网络与附加受控支路方程构造，使测试包含非对称情况。只改变已有矩阵位置的值，先保持同一 pivot 顺序，把问题限定在论文的 refactorization 机制。测试数据完全由实验生成，不把它们称为原论文八个案例的复现。

最小实现包含三条共用同一算术内核的路径：全部列重算的 Refact、最早变化列之后重算的 RefactChg、U 图闭包重算的 RefactPath。路径法需要 CSR 邻接、DFS、路径缓存、并集合并和升序执行；不需要设备模型、控制系统或完整时间积分器。前半周完成生成器、完整重算和图例单元测试，后半周完成三法对照与更新位置扫描。所实现机制对应物理页 2–4 的 Algorithms 2–6。[pdf:E04][pdf:E05][pdf:E10]

每次更新测量整个解向量相对差、因子重建误差、线性系统求解误差、处理列数、乘加次数、包含图维护的耗时，以及路径缓存大小。可把双精度、条件良好的小矩阵上相对解差和重建误差小于 10⁻¹⁰ 设为本实验验收标准；这是建议门槛，论文没有规定这一数值。计时必须把首次路径构建与后续复用分别报告，同时给出整段序列的累计时间。

**支持结果**应同时出现两件事：小闭包更新与完整重算一致，且减少算术量后能够降低包含缓存成本的累计耗时。**反驳结果**包括：固定 pivot、固定结构下出现闭包外因子变化，说明依赖实现或解释不成立；或在大量小闭包更新中，路径维护仍持续超过省下的计算，说明最小实现尚不能支持性能主张。长闭包上失去加速则用于划定适用条件，不要求合成矩阵复现论文的最高 speedup。

## § 11 — 最强反例设计

**最有力的反例是让 pivot 保持不变，却让一个局部设备更新传播到几乎所有后续列。** 这样可以排除作者已经解释过的“频繁重新 pivoting 导致路径失效”，直接攻击路径法省计算的核心前提。

具体做法是构造没有传播延迟解耦的集中参数网状网络，使用与论文一致的重排流程；在得到 U 后，寻找早序且具有大可达闭包的可变支路位置，再将其设置为重复改变的电导或受控支路。通过适当接地导纳和较小参数变化，取得整段测试中相同的 pivot 排列。网络应保持单一 BTF 块，使块级解耦也无法解释任何收益。作者已明确承认，没有输电线路时 BTF 可能退化为单块；U 图的传递可达性则直接规定了更新传播范围。定位：物理页 3，Section III-B；物理页 6，关于无输电线路的讨论。[pdf:E05][pdf:E20]

如果最早变化列接近矩阵起点，而其依赖闭包几乎覆盖全部后缀，那么 RefactPath 与 RefactChg 将执行近似相同的数值更新，前者还需支付集合处理与缓存成本。可预测的结果是路径法 speedup 接近 1，甚至低于 1；这会挑战其在此类网络中的普遍效率，而不会借助奇异矩阵或错误 pivot 人为制造失败。

最关键的对照是在同一个网络、相同矩阵规模、相同更新次数、相同 pivot 排列下，把可变位置从大闭包列换到小闭包列。若速度只随闭包加权工作量变化，就支持本文机制但收紧其适用范围；若二者速度都相近，则需要检查已报告收益是否主要来自其他实现差异。论文未给出这种固定网络的干预实验，其跨案例比较同时混合了拓扑、设备类型和迭代负担等变化。[pdf:E13][pdf:E14][pdf:E17]

## § 12 — Follow-up Research Bet

### 主押注：把单轨迹 LU 改写成跨工况共享的代数计算图

**新的研究问题是：对同一电网的一族不同开关时序或故障工况，能否让数值因子计算量主要随“独特的列计算”增长，而不是随工况数增长？** 若成功，就能在保持详细 EMT 模型的同时，把原本需要分别运行的大量工况变成一个共同求解对象，直接优化多工况吞吐量与内存成本。本文研究的是单条时间轨迹中哪些列可以不重算；这里改变的是求解对象和状态表示，让多条轨迹共同拥有一张代数图。

**核心机制是跨工况表达式共享。** 求解器的基本状态不再是每个工况各一份完整 LU，而是“以工况索引为自变量的因子列函数”。一个因子列节点由其输入列、实际排列、稀疏结构和有序前驱因子版本定义；多个工况只要具有相同的这些输入，就共享同一个数值节点。不同工况的局部设备更新使相关列及其后继表达式分开，其余表达式继续共同使用。这里依据完整输入与依赖关系确定共享，没有基于误差指标的阈值决策。

这条因果链直接利用了本文尚未开发的自由度：Algorithm 3 说明一列只读取特定先驱；Eqs. (10)–(11) 说明局部输入差异只沿相应闭包传播。因此，两份整体不同的网络矩阵，仍可能有大量列计算完全相同。把这些共同计算在工况维度上合并，得到的收益来源不同于在一条轨迹上跳过未变化列。前提定位：物理页 3，Algorithm 3、Eqs. (10)–(11)。[pdf:E05]

设计变量至少改变三项。第一，研究目标从单次仿真延迟变为工况族的总吞吐量。第二，状态表示从独立 LU 数组变为带工况分支的共享计算图。第三，数据生成方式从一个固定故障扩展到有共同前缀、不同局部事件的工况树，主动研究事件位置和共同历史长度怎样决定共享规模。各工况的右端项与物理状态仍分别推进；共享因子列不要求把不同的物理轨迹合并成同一条轨迹。

**论文提供了机会信号，也暴露了风险。** Celtic-grid 同时具有 428 个 BTF 块、频繁 refactorization 和很低的重新 pivoting 频率，路径法达到 3.01 的求解 speedup，这说明现实大网络确实含有可复用的依赖结构；这些结果尚不能证明跨工况会出现相同的数值输入。定位：物理页 5，Table II；物理页 6，Tables V–VI。[pdf:E14][pdf:E17][pdf:E18] 相反，HVDC-BM5 和 T0-grid-DM 的高重新 pivoting 频率，以及预计算法在 Table VII 中落后，说明计算结构的持久性不能预设。定位：物理页 6，Tables V、VII。[pdf:E17][pdf:E19]

最大研究收益是让详细 EMT 的大规模工况探索具有新的计算复杂度来源：成本由独特代数表达式的数量控制，而不只是靠增加处理器并行运行更多副本。最大的科学风险是，非线性状态反馈很快使各工况 Jacobian 的数值分化，导致几乎所有表达式都变成独特节点；即使早期有共享，图存储与节点管理也可能吃掉收益。论文在讨论部分明确指出，扩展部分 factorization 时 LU 存储的部分重分配管理并不简单；共享计算图会把这一实现难点进一步放大。定位：物理页 7 顶部，Section IV 延续段。[pdf:E22]

**最小区分实验应排除“只是批处理更快”这一替代解释。** 使用一个没有线路延迟、BTF 只有单块、消元图具有多条分支汇入公共后继的小型网络。生成数十个工况，每个工况改变不同支路，使每份完整矩阵都不同，但部分分支列输入保持相同。比较三种执行：各工况独立 RefactPath；具有相同数据布局的普通多工况批处理；共享列表达式的计算图。记录数值列计算次数、共享节点数、内存和总时间，并验证每个工况的完整状态解。再把工况差异移到能影响多数后继的位置，观察独特节点数是否按依赖传播规律增长。若共享方案在所有完整矩阵都不同、只有一个 BTF 块时仍显著减少数值列计算，就能把核心机制与整矩阵缓存、BTF 复用及单纯向量化区分开。

**与最近工作的实质差异需要分四层说明。** 在 problem 上，本文及其介绍的 [12] 面向单轨迹重分解效率，本押注面向工况族求解。在 mechanism 上，[11] 利用依赖调度并行任务，本文利用依赖排除任务，本押注则将不同工况中的相同任务合并。在 representation 上，本文维护特定 pivot 下的 U 图及路径缓存，本押注维护工况索引上的因子表达式图。在 experimental object 上，本文是多个电网各自的故障仿真，本押注要求同一电网中整体矩阵不同、局部代数计算相同的一族事件序列。以上相关工作比较依据仅限本文的介绍；判定跨工况共享的文献新颖性，还需补读参考文献 [11]、[12]、[21] 全文，并补查本文未覆盖的跨工况 sparse direct solver 工作。定位：物理页 1，Introduction；物理页 6，后续工作讨论；物理页 7，References。[pdf:E02][pdf:E08][pdf:E20]

**Wild-card alternative：** 以换流器群的载波相位和换相时间分布为物理设计变量，使具有重叠消元依赖的事件在时间上成组，研究能否共同设计调制波形与整段仿真的累计路径并集工作量，从输入物理过程而非求解器内部改写计算负担；这一候选的依据是本文按更新路径取并集的机制，其电气可行性尚无本文实验支持。[pdf:E05]

[pdf:E01]: <_evidence/E01-p001-page.png> "PDF 物理页 1，Title, author list, journal header, publication dates and DOI"
[pdf:E02]: <_evidence/E02-p001-page.png> "PDF 物理页 1，Abstract and Section I: EMT bottleneck, prior path methods, claimed contributions and MKLU implementation"
[pdf:E03]: <_evidence/E03-p002-page.png> "PDF 物理页 2，Section II, Eqs. (1)–(7) and Algorithm 1"
[pdf:E04]: <_evidence/E04-p002-page.png> "PDF 物理页 2，Section III-A, Algorithm 2 and Eqs. (8)–(9)"
[pdf:E05]: <_evidence/E05-p003-page.png> "PDF 物理页 3，Algorithm 3 and Section III-B: U dependency graph, Eqs. (10)–(11)"
[pdf:E06]: <_evidence/E06-p003-page.png> "PDF 物理页 3，Section III-B, final two paragraphs: CSR versus CSC, inverse column permutation and pivot-dependent path validity"
[pdf:E07]: <_evidence/E07-p004-page.png> "PDF 物理页 4，Section III-C, Eqs. (13)–(14), transmission-line decoupling and selective block refactorization"
[pdf:E08]: <_evidence/E08-p007-page.png> "PDF 物理页 7，References [4]–[16] and [21]"
[pdf:E09]: <_evidence/E09-p003-page.png> "PDF 物理页 3，Figs. 1–2, captions, worked path example and Eq. (12)"
[pdf:E10]: <_evidence/E10-p004-page.png> "PDF 物理页 4，Algorithms 4–6 and Table I"
[pdf:E11]: <_evidence/E11-p004-page.png> "PDF 物理页 4，Section IV opening: execution platform and IEEE-39, WP-grid, 400kV-Fr-grid descriptions"
[pdf:E12]: <_evidence/E12-p005-page.png> "PDF 物理页 5，Section IV case descriptions, simulation intervals, fault, time steps and Load-Flow initialization"
[pdf:E13]: <_evidence/E13-p005-page.png> "PDF 物理页 5，Table III and adjacent descriptions of time-varying and nonlinear components"
[pdf:E14]: <_evidence/E14-p005-page.png> "PDF 物理页 5，Table II: test-case dimensions, nonzeros, BTF block counts and maximum block sizes"
[pdf:E15]: <_evidence/E15-p005-page.png> "PDF 物理页 5，Eq. (15), Table IV and paragraphs defining selected accuracy outputs"
[pdf:E16]: <_evidence/E16-p006-page.png> "PDF 物理页 6，Figs. 4–5, axes, legends, captions and waveform accuracy discussion"
[pdf:E17]: <_evidence/E17-p006-page.png> "PDF 物理页 6，Table V and definitions of Solver Time, Total Time, Nb Iter, Refact Freq, Fact Nb and Fact Freq"
[pdf:E18]: <_evidence/E18-p006-page.png> "PDF 物理页 6，Table VI: solver speedups relative to RefactChg"
[pdf:E19]: <_evidence/E19-p006-page.png> "PDF 物理页 6，Table VII and discussion comparing incremental and full precomputation of factorization paths"
[pdf:E20]: <_evidence/E20-p006-page.png> "PDF 物理页 6，Section IV discussion: pivot-frequency effects, no-transmission-line limit and proposed partial full factorization"
[pdf:E22]: <_evidence/E22-p007-page.png> "PDF 物理页 7，Opening continuation of Section IV: additional dependencies and partial LU storage reallocation difficulty"
