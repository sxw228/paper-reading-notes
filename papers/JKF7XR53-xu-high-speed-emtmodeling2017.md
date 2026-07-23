# High-Speed EMT Modeling of MMCs With Arbitrary Multiport Submodule Structures Using Generalized Norton Equivalents

作者：Jianzhong Xu、Shengtao Fan、Chengyong Zhao、Aniruddha M. Gole [pdf:E01]（PDF 物理页 1，题名与署名）

出处：IEEE Transactions on Power Delivery，Vol. 33，No. 3 [pdf:E01]（PDF 物理页 1，页眉与题名）

年份：2018（论文在线发表日期为 2017 年 8 月 17 日）[pdf:E02]（PDF 物理页 1，卷期信息与 manuscript note）

DOI：10.1109/TPWRD.2017.2740857 [pdf:E02]（PDF 物理页 1，页脚 DOI）

Zotero key：JKF7XR53

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述的问题**是：如何对由任意 multiport submodule（多端口子模块，SM）构成的 modular multilevel converter（模块化多电平换流器，MMC）建立既快又准确的 electromagnetic transient（电磁暂态，EMT）模型。multiport SM 可用于增强直流故障电流阻断和电容电压均衡，但详细 EMT 模型会把每个开关、储能元件和内部节点都放进主网络求解器；当每臂含数百个 SM 时，节点数和开关状态变化引起的矩阵处理代价会非常高。作者的目标不是删掉内部状态，而是让主 EMT solver（求解器）只看到一个小型 multiport Norton equivalent（多端口诺顿等值），同时仍能恢复每个 SM 的电容电压和支路电流。[pdf:E01]（PDF 物理页 1，Abstract、Section I）[pdf:E02]（PDF 物理页 1，Section I）

**基于证据的工程推断：** 这个问题重要，是因为 MMC-HVdc 的控制、故障阻断和保护研究依赖开关级暂态，而仅用平均值模型会丢失作者关心的内部量。论文给出的规模例子很直观：对一个两端口、每臂 200 个 SM 的结构，直接表示需要 802 个臂内相关节点，而递归等值只向外部求解器暴露 4 个接口节点。[pdf:E03]（PDF 物理页 3，Section II-A，Fig. 5 邻近正文）这意味着瓶颈从“反复求解随 SM 数量增长的大网络”转为“在臂内部做规则的小矩阵递归，再解一个小得多的外部网络”。这是基于论文结构的工程解释，不是作者给出的独立复杂度定理。

作者最终声称，所提方法对测试的两端口 MMC 几乎不损失准确度，且相对直接详细模型可达到约两个到三个数量级的加速；大规模测试中甚至超过三个数量级。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E04]（PDF 物理页 8，Table I、Section IV-B）

## § 2 — 前人工作与不足

论文把已有路线分成三层。第一层是 nested solution（嵌套求解）与 diakoptics（网络分割）：Strunz 和 Carlson 的方法把网络分成嵌套子系统，以降低计算负担；这一路线与 Kron 等人的 diakoptics 思想相近。第二层是针对传统 single-port SM（单端口子模块）的 MMC 快速 EMT 模型：Gnanarathna、Gole 和 Jayasinghe 将每个桥臂缩减为两节点 Thévenin equivalent（戴维南等值），随后又有工作扩展到 blocking、快速电压均衡、更高仿真速度以及 real-time digital simulation（实时数字仿真）。[pdf:E02]（PDF 物理页 1，Section I）第三层是新出现的 multiport MMC 拓扑，它们通过额外端口实现故障穿越或电容自均衡。[pdf:E05]（PDF 物理页 2，Fig. 2、Fig. 3）[pdf:E06]（PDF 物理页 2，Section I–II）

此前方法真正不足的地方，不是笼统的“没有考虑多端口”，而是它依赖一个在 single-port 桥臂中成立、在 multiport 桥臂中失效的代数性质：传统桥臂内所有 SM 流过同一电流，因此各 SM 的 Thévenin 电阻和电压源可以直接串联相加；multiport SM 的不同端口电流并不满足这种同流关系，内部连接也不再是一条简单串联链。论文甚至说明这里的“port”是宽松叫法：两端口示例满足总流入与总流出守恒，但单个端口的进出电流不必相等。[pdf:E06]（PDF 物理页 2，Section I）因此，旧方法的简化基础被破坏，详细模型又太慢，必须找到一种不要求“同一桥臂电流”的一般网络消元方式。

论文没有通过外部相关工作比较证明“任意 multiport”是此前无人解决的严格 novelty；它只在本论文所引文献范围内说明旧的单端口聚合不能直接套用。因此，本卡把“将 generalized Norton equivalent 用于任意 multiport SM 结构”视为作者的贡献主张，而不是经完整文献检索认证的唯一首创。[pdf:E06]（PDF 物理页 2，贡献陈述）

## § 3 — 重建作者的思考路径

下面是基于论文证据的逆向重建，不是作者逐句给出的研发日志。

第一步，研究者已经知道：MMC 详细 EMT 的主要负担来自大量内部节点，而网络分割和嵌套求解能在不丢失子系统信息的前提下，把内部网络压缩成对外接口。[pdf:E02]（PDF 物理页 1，Section I）第二步，single-port MMC 的快速模型证明了“桥臂内部详细、桥臂外部等值”这条路线有效，但它靠的是全臂同流和串联相加；multiport 结构恰好打破这一条件。[pdf:E06]（PDF 物理页 2，Section I）第三步，如果不再把 SM 当成“一个串联电压源”，而把它当成任意线性 companion circuit（伴随电路）的多端口网络，那么每个离散时刻的开关网络都可以写成节点导纳方程，再用 Schur’s complement（舒尔补）消去内部节点。[pdf:E07]（PDF 物理页 4，Eq. (1)–(8)）

第四步，单个 SM 消元后仍然是同一种“左接口—右接口”块矩阵形式，于是两个相邻 SM 可以消去共享接口并合成一个更大的同型块；重复这一过程，就得到整条桥臂的等值。[pdf:E08]（PDF 物理页 5，Eq. (10)–(19)）第五步，外部求解器只计算桥臂端口电压；随后沿合并树反向展开，就能恢复内部节点、电容电压和下一时步需要的 history terms（历史项）。[pdf:E03]（PDF 物理页 3，Fig. 5、Section II-B–II-C）

这条思考路径的关键转变是：不再寻找 multiport 情况下的“串联相加公式”，而是寻找一种对任意节点网络都成立、并且合并后保持同一接口形式的消元算子。舒尔补正好满足这个要求。

## § 4 — 核心 Intuition

不要让主 EMT solver 看见随 SM 数量增长的内部节点，只让它看见每臂固定的 2m 个接口量。每个离散时刻先用 Schur’s complement 把 SM 内部和相邻 SM 的共享接口逐层消去，得到整臂 Norton equivalent；外部网络解完后，再按相反顺序恢复所有内部量。[pdf:E03]（PDF 物理页 3，Fig. 5）[pdf:E07]（PDF 物理页 4，Eq. (5)–(8)）[pdf:E08]（PDF 物理页 5，Eq. (9)）它的加速来自缩小主网络矩阵，而不是牺牲内部状态或改用低保真平均模型。

## § 5 — 具体方法与完整 Pipeline

以论文的两端口 SM 为例，输入是一条由 N 个 SM 级联的桥臂、当前 firing pulses（触发脉冲）、上一时步的电容 history current、外部网络及本时步边界条件；输出是外部网络节点电压、桥臂接口电流，以及需要时的每个 SM 内部电压和支路电流。

1. **建立单个 SM 的 companion circuit。** 两端口示例含 8 个开关电导和 1 个电容 Norton companion：开关电导按状态取 \(G_{\mathrm{ON}}\) 或 \(G_{\mathrm{OFF}}\)，电容由 \(G_C\) 与历史电流源 \(I_{\mathrm{CEQ}}\) 表示。开关状态由 firing pulses 以及上一时步的开关电压或电流共同决定；论文把积分方法、SM 电容和步长对 companion 参数的影响保留为一般形式，没有指定唯一积分公式。[pdf:E05]（PDF 物理页 2，Fig. 2）[pdf:E06]（PDF 物理页 2，Fig. 2(b) 邻近正文）

2. **在每个 SM 内部做局部消元。** 把 2m 个端口节点记为 interface nodes，其余 \(n-2m\) 个节点记为 internal nodes；对节点导纳矩阵分块，用 Schur’s complement 得到只含端口电压、电流和历史源的 \(2m\times2m\) Norton equivalent。[pdf:E07]（PDF 物理页 4，Eq. (1)–(8)）

3. **执行 outward flow（向外递归）。** 先把 SM1 与 SM2 的共享接口消去，形成 Block 2；再把 Block 2 与 SM3 合并，依次进行到 Block N。每次合并后的方程保持与单个 SM 相同的左右接口块结构，所以可以复用同一递归算子。[pdf:E03]（PDF 物理页 3，Section II-A、Fig. 5）[pdf:E08]（PDF 物理页 5，Eq. (14)–(19)）

4. **把整臂等值叠加进外部 EMT 网络。** 最终每臂只贡献一个 \(2m\times2m\) 的接口导纳块和接口历史电流项，不把 N 级内部节点加入主网络。对两端口、每个 SM 有 6 个节点、每臂 200 个 SM 的论文示例，直接表示为 802 个相关节点，而接口表示只有 4 个节点。[pdf:E03]（PDF 物理页 3，Section II-A）

5. **由主 solver 求外部网络。** 外部求解器计算系统节点电压和每臂 2m 个接口电压；整臂等值通过 Eq. (22)–(24) 与外部网络导纳矩阵和历史电流向量合并。[pdf:E09]（PDF 物理页 6，Eq. (20)–(24)）

6. **执行 inward flow（向内回代）。** 从 Block N 开始，用已知外部接口电压求出前一级共享接口，再依次回到 Block 1；每个块的内部电压只计算一次。得到的电容电压和支路电流既可作为输出，也用于生成下一时步的 history terms。[pdf:E03]（PDF 物理页 3，Section II-C）[pdf:E08]（PDF 物理页 5，Eq. (9)、Eq. (19)）

7. **处理 blocking 事件。** IGBT 脉冲撤除后，剩余二极管网络的导通状态取决于电流方向。论文沿用线性 interpolation（插值）定位二极管电流过零时刻，避免离散步长把二极管电流推进到负值并产生电压尖峰；随后再把解恢复到原时间网格。[pdf:E10]（PDF 物理页 6，Section III-D）

**实现边界。** 速度实验采用固定 20 μs 步长和 1 s 仿真时长；论文没有报告 multirate（多速率）时间推进、并行递归、矩阵存储格式、浮点精度、具体的 \(G_{\mathrm{ON}}/G_{\mathrm{OFF}}\) 数值、condition-number 监控或 FPGA 映射。其实际执行平台是 PSCAD/EMTDC Professional V4.6，运行于 Intel Core i7-6700 3.40 GHz、16 GB RAM、64-bit Windows 10 的 CPU 系统；递归模型在主 EMT solution 外处理，再以 Norton equivalent 接口接入。[pdf:E11]（PDF 物理页 7，Section IV 开头）[pdf:E04]（PDF 物理页 8，Section IV-B）

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文的数学本质是对每个离散时刻的线性 companion network 做 exact static condensation（精确静态凝聚）。它不是在时间域里拟合一个近似低阶模型，而是在给定开关状态和历史源后，精确消去本时步不必暴露给外部 solver 的节点。

单个 SM 的节点方程为

\[
Y_{\mathrm{SM}}V_{\mathrm{SM}}=J_{\mathrm{SM}}+I_{\mathrm{SM}}.
\]

这里 \(Y_{\mathrm{SM}}\) 是由开关电导和电容 companion conductance 盖章得到的 \(n\times n\) 导纳矩阵；\(J_{\mathrm{SM}}\) 主要承载储能元件的历史源，\(I_{\mathrm{SM}}\) 是外部网络只在接口节点注入的电流。[pdf:E07]（PDF 物理页 4，Eq. (1)–(4)）把接口节点和内部节点分块：

\[
\begin{bmatrix}Y_{11}&Y_{12}\\Y_{21}&Y_{22}\end{bmatrix}
\begin{bmatrix}V_{\mathrm{IF}}\\V_{\mathrm{IN}}\end{bmatrix}
=
\begin{bmatrix}0\\J_{\mathrm{IN}}\end{bmatrix}
+
\begin{bmatrix}I_{\mathrm{IF}}\\0\end{bmatrix}.
\]

消去 \(V_{\mathrm{IN}}\) 后得到

\[
Y_{\mathrm{IF}}V_{\mathrm{IF}}=J_{\mathrm{IF}}+I_{\mathrm{IF}},
\quad
Y_{\mathrm{IF}}=Y_{11}-Y_{12}Y_{22}^{-1}Y_{21},
\quad
J_{\mathrm{IF}}=-Y_{12}Y_{22}^{-1}J_{\mathrm{IN}}.
\]

这就是单个 SM 的 generalized Norton equivalent。[pdf:E07]（PDF 物理页 4，Eq. (5)–(8)）工程上，\(Y_{\mathrm{IF}}\) 描述“从端口看进去”的瞬时导纳，\(J_{\mathrm{IF}}\) 则把电容上一时步留下的记忆折算成端口历史电流源。

外部接口电压求出后，内部量由

\[
V_{\mathrm{IN}}=Y_{22}^{-1}\left(J_{\mathrm{IN}}-Y_{21}V_{\mathrm{IF}}\right)
\]

恢复。[pdf:E08]（PDF 物理页 5，Eq. (9)）这条式子解释了为什么“消元”不等于“丢失”：外部求解阶段暂时不计算内部节点，但只要保存分块矩阵和历史源，就能在回代阶段重建它们。

对相邻块 k 和 k+1，论文把各自的端口方程写成相同的左右分块形式，并施加共享接口约束

\[
X_{\mathrm{RL}}=X_R^k=X_L^{k+1}.
\]

随后消去 \(X_{\mathrm{RL}}\)，得到仍具有同一两端块结构的新方程 \(A^{k\rightarrow k+1}X=J^{k\rightarrow k+1}\)；Eq. (19) 保存了共享接口的回代关系。[pdf:E08]（PDF 物理页 5，Eq. (14)–(19)）“合并后形式不变”是递归能够重复 N−1 次的代数闭包条件。

当 N 个 SM 都被合并后，整臂满足

\[
Y_{\mathrm{IF}}^{1\rightarrow N}V_{\mathrm{IF}}^{1\rightarrow N}
=J_{\mathrm{IF}}^{1\rightarrow N}+I_{\mathrm{IF}}^{1\rightarrow N},
\]

再把这个小矩阵叠加到外部网络方程 \(Y_{\mathrm{EX}}V_{\mathrm{EX}}=J_{\mathrm{EX}}+I_{\mathrm{EX}}\)，得到最终系统方程 \(Y_NV_N=J_N\)。[pdf:E09]（PDF 物理页 6，Eq. (22)–(24)）因此，主 solver 的矩阵规模不再随臂内 SM 节点线性增加；代价是每个时步要执行 outward elimination 与 inward substitution 两遍递归。

**基于证据的推断：** 只要所需分块可逆、数值条件良好，并且详细模型与等值模型使用相同 companion discretization，这个消元在单个时步上应是代数等价的；论文的误差主要应来自数值实现、事件插值和 solver 细节，而不是舒尔补本身。论文没有给出这一点的形式化误差界。

## § 7 — 实验设计与结论

1. **问题：稳态下等值模型能否保留外部波形和单个 SM 内部量？** 实验：在 Fig. 6 的 point-to-point HVdc 系统中，对 proposed equivalent model（EM）与 fully detailed model（DM）做对比；每臂 8 个 SM，换流器额定 300 MW、±200 kV，每个 SM 电容 480 μF，并比较桥臂电压、第三个 SM 的电容电压和电容电流。答案：两组轨迹基本重合，电容电压峰值误差通常低于 0.2%，作者据此称准确度损失可忽略。[pdf:E11]（PDF 物理页 7，Fig. 6、Fig. 7、Section IV-A 设置）[pdf:E12]（PDF 物理页 7，Fig. 7 误差说明）

2. **问题：控制指令突变时，递归等值能否复现动态响应？** 实验：在 t=7.0 s 把有功参考从 300 MW 改为 260 MW，比较两种模型的交流侧有功。答案：Fig. 8 中结果几乎不可区分。[pdf:E12]（PDF 物理页 7，Fig. 8、Section IV-A.2）

3. **问题：blocking 这种强开关事件和直流故障清除能否被正确表示？** 实验：在 t=11.3 s 施加 pole-to-pole 直流短路，约 3 ms 后检测到故障，并在 t=11.303 s 阻断整流侧和逆变侧所有 IGBT；比较直流电压和交流线电流。答案：直流电压跌至零，阻断后交流侧电流也降至零，两种模型给出几乎相同结果。[pdf:E12]（PDF 物理页 7，Fig. 9、Section IV-A.3）

4. **问题：加速是否随 SM 数量扩大？** 实验：对 short-circuit ratio（短路比）为 3 的 MMC 端口及交流网络，测试每臂 48、72、144、288、576 个两端口 SM，步长 20 μs、时长 1 s。答案：DM/EM 的 CPU 时间分别从 456.9/7.9 s 增长到 110235.6/88.5 s；speedup factor 从 57.8 增至 1245.6。作者拟合 EM 的时间为 \(CT\approx0.15k+1.8\)，近似线性；DM 为 \(CT\approx0.053k^{2.3}+80\)。[pdf:E04]（PDF 物理页 8，Table I、Fig. 10、Section IV-B）

**不能外推的范围。** “arbitrary multiport”在数学表达上是一般的，但实验只展示一个两端口 SM 拓扑；准确性测试只有每臂 8 个 SM，规模测试主要报告 CPU 时间，没有给出大规模情况下的内部状态误差。所有结果来自一台 CPU 上的 PSCAD/EMTDC V4.6，没有 FPGA、real-time deadline、内存占用、不同稀疏 solver、不同 \(G_{\mathrm{ON}}/G_{\mathrm{OFF}}\) 比例、不同 m、不同积分法或数值条件的对照。[pdf:E11]（PDF 物理页 7，实验平台与准确性设置）[pdf:E04]（PDF 物理页 8，速度设置）因此，论文有力支持“该两端口案例在该软件与硬件上既准确又快”，但没有同等强度地支持“所有任意 multiport 结构和数值工况都同样稳定”。

## § 8 — Take-aways

**5 句话：**

1. 这篇论文把 multiport MMC 的快速 EMT 建模问题转化为逐时步的网络节点消元，而不是继续依赖 single-port 桥臂的同流串联性质。[pdf:E06]（PDF 物理页 2，Section I）
2. 每个 SM 先经 Schur’s complement 化为端口 Norton equivalent，相邻 SM 再按相同块结构递归合并。[pdf:E07]（PDF 物理页 4，Eq. (5)–(8)）[pdf:E08]（PDF 物理页 5，Eq. (14)–(19)）
3. 主 EMT solver 只处理每臂 2m 个接口量，内部电容电压和支路电流在外部求解后反向恢复。[pdf:E03]（PDF 物理页 3，Fig. 5）[pdf:E09]（PDF 物理页 6，Eq. (22)–(24)）
4. 在论文的两端口案例中，稳态、功率阶跃和直流故障 blocking 的 EM 与 DM 几乎一致，电容电压峰值误差通常低于 0.2%。[pdf:E11]（PDF 物理页 7，Fig. 7）[pdf:E12]（PDF 物理页 7，Fig. 8–9）
5. 速度测试显示 EM 时间近似随 SM 数线性增长，576 个 SM/臂时报告 1245.6 倍加速，但其一般性仍缺少多拓扑和数值条件验证。[pdf:E04]（PDF 物理页 8，Table I、Fig. 10）[pdf:E13]（PDF 物理页 8，Conclusion）

**3 句话：** 论文的核心不是近似掉 SM 动态，而是把内部节点从主网络矩阵中精确凝聚出去。递归的 outward flow 负责生成整臂端口等值，inward flow 负责恢复内部状态，从而同时保留速度和可观测性。[pdf:E03]（PDF 物理页 3，Fig. 5）[pdf:E09]（PDF 物理页 6，Eq. (22)–(24)）最强实验结果是大规模 CPU 时间近线性增长，但“任意 multiport”的数值稳健性仍未被系统验证。[pdf:E04]（PDF 物理页 8，Table I、Fig. 10）

**1 句话：** 这是一个用 generalized Norton equivalent 和双向递归，把“超大详细 MMC 网络”改写成“小外部求解加可逆内部回代”的高效 EMT 建模框架。[pdf:E13]（PDF 物理页 8，Conclusion）

## § 9 — 最脆弱的假设

最脆弱的假设是：**在所有相关开关状态和任意 multiport SM 拓扑下，被消去的内部块与相邻接口块始终可逆且数值条件足够好。** 论文的核心式直接使用 \(Y_{22}^{-1}\)、相邻块消元中的逆矩阵，以及整臂接口重排中的逆矩阵；一旦这些块奇异，Schur’s complement 无法定义，outward flow、Norton equivalent 和 inward recovery 会同时失效；若只是高度病态，则递归中的舍入误差和消元误差可能随 N 累积。[pdf:E07]（PDF 物理页 4，Eq. (7)–(8)）[pdf:E08]（PDF 物理页 5，Eq. (9)、Eq. (18)–(19)）[pdf:E09]（PDF 物理页 6，Eq. (21)–(22)）

这个假设在实际中可能失效，因为 multiport 开关网络可在某些 blocking 或重构状态下形成近浮置的内部共模、弱连接电容岛，或者产生极大的 \(G_{\mathrm{ON}}/G_{\mathrm{OFF}}\) 动态范围。有限的 \(G_{\mathrm{OFF}}\) 可能在论文示例中起到数值正则化作用，但拓扑更复杂、漏电更小或级联更长时，局部矩阵仍可能严重病态。这是基于电路与线性代数结构的推断。

论文为该假设提供的证据只有：一个具体两端口、单电容 SM 在所选开关模型和 PSCAD 设置下成功运行，并在三个动态场景中与详细模型吻合。[pdf:E06]（PDF 物理页 2，Fig. 2 及 companion circuit）[pdf:E11]（PDF 物理页 7，Fig. 6–7）[pdf:E12]（PDF 物理页 7，Fig. 8–9）它没有报告可逆性证明、condition number、pivoting 策略、全部开关状态枚举、不同 off-state conductance 或不同 multiport 拓扑的压力测试。因此，这一假设既是方法最核心的数学前提，也是论文证据最薄弱的部分。

## § 10 — 最小复现实验

一周内最有价值的复现，不是搭完整双端 MMC-HVdc 控制系统，而是验证“递归等值在动态开关下与详细节点模型代数一致，并且计算量随 N 近线性增长”。

- **数据与工况：** 按 Fig. 2(b) 建立同一个两端口 SM companion circuit，生成一组可重复的 firing-pulse 序列、端口电压轨迹和 blocking 事件；电容值可采用论文的 480 μF，固定步长采用 20 μs。先用 N=8 验证动态波形，再用 N=48、72、144、288 做扩展。由于论文未报告具体 \(G_{\mathrm{ON}}/G_{\mathrm{OFF}}\) 数值和唯一积分公式，复现必须明确声明这些选择，并保证两套模型完全一致。[pdf:E06]（PDF 物理页 2，Fig. 2）[pdf:E11]（PDF 物理页 7，参数）[pdf:E04]（PDF 物理页 8，规模与步长）
- **实现：** 在 Python/Julia/MATLAB 中写两套求解器：一套组装整臂完整稀疏 nodal matrix，另一套实现 Eq. (5)–(9) 与 Eq. (14)–(19) 的 outward/inward recursion。[pdf:E07]（PDF 物理页 4，Eq. (5)–(8)）[pdf:E08]（PDF 物理页 5，Eq. (9)、Eq. (14)–(19)）实现时用带 pivoting 的线性求解代替显式求逆，并记录每个局部块的 condition number。
- **测量：** 每个时步比较端口电流、全部电容电压、关键内部支路电流和方程残差；同时测量 wall-clock time、内存和时间随 N 的拟合斜率。再加入一次端口阶跃和一次 blocking 过零事件，检查误差是否在事件附近突增。
- **支持或反驳标准：** 若 N=8 的动态误差达到论文所示的 0.2% 以内，并且静态同状态残差接近浮点精度；同时递归时间对 N 近似线性、详细稀疏模型明显更快增长，则核心 claim 获得支持。[pdf:E12]（PDF 物理页 7，Fig. 7 误差说明）[pdf:E04]（PDF 物理页 8，Table I、Fig. 10）若误差随 N、开关状态或 condition number 系统性放大，或者递归实现并未相对公平的稀疏详细模型形成稳定优势，则应反驳或至少收缩论文的适用范围。

这个实验不复现完整控制器，但直接检验论文最核心的两个机制：Schur 消元是否保持电气等价，以及把 N 相关节点移出主 solver 是否真的改变复杂度。

## § 11 — 最强反例设计

最强反例应针对第 9 节的可逆性和数值稳定性，而不是再找一个普通波形。构造一个 m=3 的非对称 multiport SM，令某些 blocking/reconfiguration 状态下内部电容网络只通过极小的 off-state conductance 与端口相连；把 \(G_{\mathrm{ON}}/G_{\mathrm{OFF}}\) 从 \(10^6\) 扫到 \(10^{12}\)，并让相邻 SM 交替采用两种镜像连接，使递归合并时的局部 Schur 块逐渐接近奇异。论文的公式明确要求对这些内部与共享接口块求逆，因此这是对机制本身的直接攻击。[pdf:E07]（PDF 物理页 4，Eq. (7)–(8)）[pdf:E08]（PDF 物理页 5，Eq. (18)–(19)）[pdf:E10]（PDF 物理页 6，Section III-D）

实验同时运行两种模型：一边是带全局稀疏 pivoting、统一参考处理和严格残差检查的完整 MNA/nodal 模型；另一边是论文的固定顺序递归等值。逐个枚举关键开关状态并增加 N，记录局部与累计 condition number、端口功率误差、电容能量误差、回代残差及失败状态。为了排除“两个模型都在解一个物理上未定义的浮置网络”，每个测试都加入明确但极小的物理泄漏路径，并让完整模型保持可解。

如果完整模型残差仍小、能量行为平滑，而递归模型在某个可预测的导通比或 N 阈值后出现超过 1% 的端口/内部误差、非物理能量增长、NaN 或无法回代，那么“任意 multiport 结构可用同一递归稳定建模”的强表述就被实质推翻。反过来，如果递归模型在全部状态下保持误差与完整模型同阶，且 condition number 不随层数灾难性增长，这个反例就失败，并会显著增强论文最缺少的稳健性证据。

## § 12 — Follow-up Research Idea

**候选判断：** 本领域的高影响工作通常不仅要求仿真更快，还要求对故障与开关事件准确、覆盖实际拓扑、给出数值稳定性依据，并能在 real-time/HIL 或工程软件中复现。基于第 9 节，候选方向是：**面向任意 switching DAE（开关微分代数系统）的“可证明可解、保持无源、拓扑自适应”的 multiport EMT 等值框架。** 由于本任务只使用随包论文、没有检索论文之后的相关工作，下面明确是候选想法，不声称 novelty。

**(a) 未满足需求。** 现有论文把速度问题解决得很好，但把“所需局部逆矩阵一直可用”当作隐含前提；真正复杂的 multiport SM、blocking 状态和极端导通比可能产生浮置模态或病态块。[pdf:E07]（PDF 物理页 4，Eq. (7)–(8)）[pdf:E08]（PDF 物理页 5，Eq. (18)–(19)）[pdf:E10]（PDF 物理页 6，Section III-D）

**(b) 研究价值。** 把目标从“对规则拓扑做快速消元”改为“对每个开关状态自动认证可消元性、稳定性和无源性”，会同时影响 EMT 精度、故障保护可信度和 real-time 可实现性。若还能给出误差/残差界和固定时延上界，其价值会超过单纯再提高一个常数倍速度。

**(c) 可借鉴的相邻工具。** 可引入 circuit DAE 的结构秩分析、rank-revealing QR/SVD、descriptor-system null-space projection（描述系统零空间投影）、passivity-preserving Kron reduction（保持无源性的 Kron 约化）以及动态 graph partitioning（图划分）。对硬件实现，可把有限种“秩/拓扑类别”编译为固定尺寸的小矩阵 QR 或 LDLᵀ kernel，再映射到 FPGA；但 FPGA 只是执行载体，不是研究贡献本身。

**(d) 第一个可证伪实验。** 建立一个公开 multiport SM switching-state suite，包含正常、blocking、弱泄漏、浮置边缘和高导通比状态；同时比较完整 MNA、原论文递归法和新方法。在所有状态下检查端口等价、内部能量、无源性、condition number、实时步长 deadline 和失败检测率。只要新方法仍在某类可解完整网络上错误判定、破坏能量一致性，或为了稳定性付出不可接受的时延，它就被证伪。

**(e) 与本文的实质区别。** 本文固定接口、固定消元顺序，并用成功案例证明速度与准确性；候选方法把“能否安全消元”本身纳入模型状态，允许在秩变化时改变接口、保留约束模态或切换 descriptor representation。它改变的是问题定义——从快速求一个默认良态的 Norton equivalent，变为对任意开关拓扑生成带可解性证书的等值——而不是在现有递归上增加一个补丁。
