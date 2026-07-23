# Real-time simulation of large-scale HTS systems: multi-scale and homogeneous models using the T–A formulation

作者：Edgar Berrospe-Juarez；Víctor M. R. Zermeño；Frederic Trillaud；Francesco Grilli [pdf:E01]（PDF 物理页 2，题名页）

出处：*Superconductor Science and Technology*，32 (2019) 065003 [pdf:E01]（PDF 物理页 2，题名页）

年份：2019 [pdf:E01]（PDF 物理页 2，Published 30 April 2019）

DOI：10.1088/1361-6668/ab0d66 [pdf:E01]（PDF 物理页 2，页眉）

Zotero key：DESMS3TW

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述的研究问题**是：怎样在普通个人计算机上，对由大量第二代高温超导带材构成的系统，同时求出全局磁场、各带材内部的电流密度分布和超导层磁滞损耗，并把计算耗时压到慢速充放电过程的物理时长以内。作者把问题放在大型 HTS 磁体的设计语境中：全尺寸 H formulation（H 公式）有限元模型虽然能描述每一根带材，却会因内存和时间成本而难以扩展；因此论文把既有 multi-scale（多尺度）与 homogenization（均匀化）降阶思想改写到 T–A formulation（T–A 公式）中 [pdf:E01]（PDF 物理页 2，Abstract）。

重要性有两层。第一层是热设计：作者只计算超导层中的磁滞损耗，这一损耗决定低温系统需要带走多少热；对大量匝数的线圈，忽略带材间电磁耦合会使损耗评估失真。第二层是场质量：作者强调，同一模型还能给出整个系统的磁场和每根带材的电流密度，因此其价值不只在总损耗，也在 MRI、NMR 等需要高场精度的系统分析 [pdf:E02]（PDF 物理页 3，Introduction 左栏上部）。

这里的“real-time（实时）”不是硬件闭环或每个数值步都满足固定 deadline，而是**整段仿真的墙钟时间短于被仿真物理过程的持续时间**。论文选择的目标工况是一条 3 h 的慢速充放电曲线，因此 1 h 13 min 或 37 min 完成一次离线计算就被视为实时 [pdf:E13]（PDF 物理页 10，Section 5 与 Fig. 9）。所以它解决的是“慢过程可在过程结束前算完”，而不是快速开关 EMT、硬实时控制或 FPGA-in-the-loop。

## § 2 — 前人工作与不足

**相关文献结论，仅按本文的综述重述。**早期解析模型主要覆盖单根导体、无限阵列或特定堆叠边界条件，难以代表真实设备，也难以完整纳入带材间电磁相互作用；FEM 数值模型扩展了可建模规模，其中 H formulation 已被广泛采用并有实验验证，但在大量匝数、尤其慢动态工况下，计算时间和内存成为主要瓶颈。论文还列出 MMEV、minimum electromagnetic entropy production 等路线，但没有把它们作为本工作的直接基线 [pdf:E02]（PDF 物理页 3，Introduction 左栏）。

在降阶方面，homogenization 把一叠带材替换为各向异性 bulk（体域）；multi-scale 只精确求解少量“analyzed tapes（分析带材）”，再通过全局磁场把局部与整机耦合。此前基于 H formulation 的 multi-scale 往往需要“单带材子模型 + 线圈子模型”反复迭代，建模和求解链较重；另一方面，T–A formulation 已证明适合把很薄的超导层降成 1D 线元，但当时尚未与这两类大型系统降阶策略形成本文所用的单模型耦合 [pdf:E02]（PDF 物理页 3，Introduction 下部）[pdf:E03]（PDF 物理页 3，右栏上部）。

因此，本文真正填补的缺口不是发明 T–A、multi-scale 或 homogenization 本身，而是把三者组合成两种可在一个 T–A 模型内同时求解局部电流与全局磁场的实现，并用 2000 匝 racetrack coil（跑道线圈）验证其慢周期墙钟时间。作者声称内存也“substantially reduced”，但正文的定量结果只给出损耗、误差、R² 和计算时间，没有给出峰值内存或内存缩减比例；这一部分只得到定性支持 [pdf:E01]（PDF 物理页 2，Abstract）[pdf:E14]（PDF 物理页 11，Table 2）。

## § 3 — 重建作者的思考路径

下面是**基于论文证据的逆向重建**，不是作者逐字给出的研发日志。

1. 先保留不可牺牲的物理量：大型线圈的总损耗不够，必须同时保住全局 \(\mathbf B\) 与每根带材的局部 \(J\)，否则无法判断边缘带材、不同 pancake（饼式线圈）之间的损耗差异。H full model（H 全模型）能做到，但慢周期代价过高 [pdf:E02]（PDF 物理页 3，Introduction）[pdf:E10]（PDF 物理页 7，Fig. 4）。
2. 利用 2G HTS 层极薄、宽厚比很大的几何事实，把每层超导体压成 1D sheet（薄片线元）：只在线元上求 \(\mathbf T\)，在整个计算域求 \(\mathbf A\)，再把线元表面电流作为 \(\mathbf A\) 方程的边界源。这样先把“带材厚度方向的细网格”从问题中拿掉 [pdf:E04]（PDF 物理页 4，Fig. 1 与 Eq. (1)–(3)）。
3. 仅靠 T–A full 仍需为每根带材保留 \(T\) 自由度，于是继续沿“带材编号”方向降阶：一种方案只挑若干带材求 \(T\)，其余带材的 \(J\) 插值；另一种方案把整叠带材变成 bulk，只保留少量堆叠方向单元 [pdf:E11]（PDF 物理页 8，Fig. 5、Fig. 6 与 Section 4.1–4.3）。
4. 作者观察到线圈上部的损耗随带材编号变化更快，于是把分析带材和 bulk 单元向该区域加密。这一步实际上把“哪里需要高分辨率”的先验知识写进了降阶模型 [pdf:E11]（PDF 物理页 8，Section 4.3）[pdf:E12]（PDF 物理页 9，Fig. 7、Fig. 8）。
5. 最后处理数值稳定性：同阶 \(T/A\) 元会在亚临界电流区域产生伪振荡，试验后选择 \(T\) 一阶、\(A\) 二阶的混合有限元组合；作者明确说振荡起因仍未知，选择来自 trial and error（试错） [pdf:E15]（PDF 物理页 12，Appendix A）[pdf:E16]（PDF 物理页 13，Fig. A1 与 Table A1）。

这条路径的核心不是单一公式，而是连续做两次“只保留必要自由度”的决策：先在单根带材截面上做 thin-sheet reduction，再在数百根带材之间做 sparse sampling（稀疏采样）或 bulk averaging（体域平均）。

## § 4 — 核心 Intuition

T–A formulation 把“全局磁场”与“超导薄层内部电流重分布”拆开：\(\mathbf A\) 在整个域传播耦合，\(\mathbf T\) 只在真正承载超导电流的低维区域求解 [pdf:E04]（PDF 物理页 4，Fig. 1）。在此基础上，multi-scale 只精算少量代表带材并插值其余带材，homogeneous model 则把整叠带材压成少量 bulk 单元 [pdf:E11]（PDF 物理页 8，Fig. 5、Fig. 6）。只要带材间的电流与损耗变化足够平滑，这种稀疏表示就能保住主要物理分布，同时显著减少自由度。速度收益最终来自“少求很多局部状态”，而不是更快的硬件或新的时间积分器。

## § 5 — 具体方法与完整 Pipeline

以论文的 2000 匝 racetrack coil 为例，完整 pipeline 如下。

1. **输入几何与材料。**线圈有 10 个 pancakes，每个 200 匝；利用对称性只建四分之一模型，即 5 个 pancakes、每个 100 根带材，共 500 根。unit cell 宽 4.45 mm、厚 293 μm，HTS 层宽 4 mm、厚 1 μm，\(E_c=10^{-4}\,\mathrm{V\,m^{-1}}\)、\(N=38\)、\(B_0=0.04265\,\mathrm T\)、\(k=0.29515\)、\(\alpha=0.7\) [pdf:E06]（PDF 物理页 5，Fig. 2 与 Table 1）。Table 1 的 \(J_{c0}\) 行在源 PDF 中只可见“\(2.8\times10\,\mathrm{A\,m^{-2}}\)”，十次幂指数没有呈现；本卡不把推测值当作已认证参数。
2. **建立 T–A full reference。**每根带材都求 \(T\)，整个域求 \(A\)；\(T\) 用一阶元，\(A\) 用二阶元，每根带材宽度方向 60 个均匀单元。作者先用 H full model 作参照，再把已验证的 T–A full 用作后续慢周期实验的 reference [pdf:E08]（PDF 物理页 5，Section 3.2–3.3）[pdf:E09]（PDF 物理页 6，Fig. 3）。
3. **multi-scale 分支。**每个 pancake 只对带材编号 \(\{25,66,88,96,99,100\}\) 求 \(T\)，总计 30 根；非分析带材的 \(J\) 由邻近分析带材线性插值。分析带材及其最近邻的 \(A\) 使用二阶元、宽度方向 60 个单元，其余区域的 \(A\) 用一阶元、宽度方向 30 个单元；得到分析带材损耗后，再用 PCHIP 插值其余带材的损耗 [pdf:E11]（PDF 物理页 8，Fig. 5 与 Section 4.3）[pdf:E12]（PDF 物理页 9，Fig. 7 及下方正文）。
4. **homogeneous 分支。**每个 pancake 被替换成一个 bulk，共 5 个；bulk 在原堆叠方向仅用 6 个不等距单元，上部更密，带材宽度方向仍用 60 个单元。bulk 内只保留 \(T_y\)，将电流密度按超导层厚度与 unit-cell 厚度之比缩放成 \(J_s\)，作为 \(A_z\) 方程的体源；在 6 个单元中心计算损耗，再用 PCHIP 映射回各带材 [pdf:E11]（PDF 物理页 8，Fig. 6 与 Eq. (11)–(13)）[pdf:E12]（PDF 物理页 9，Fig. 8 与 Section 4.4）。
5. **施加工况。**输入 11 A 的 3 h 充放电：1 h 线性升流、0.5 h 平台、1 h 降流、0.5 h 平台；输出峰值时刻的 \(|\mathbf B|\)、归一化电流密度 \(J_n=J/J_c\)、全周期每根带材损耗和总损耗 [pdf:E13]（PDF 物理页 10，Fig. 9 与 Section 5）。
6. **比较与判定。**用损耗相对误差、全时空 \(J\) 分布的 \(R^2\) 以及墙钟时间比较 T–A full、multi-scale 和 homogeneous。论文的“实时”判据仅为计算时间小于 3 h [pdf:E09]（PDF 物理页 6，Eq. (9)、Eq. (10)）[pdf:E14]（PDF 物理页 11，Table 2）。

**实现边界。**全部模型运行于 COMSOL Multiphysics 5.3 和一台 MacBook Pro（3 GHz Intel Core i7-4578U、4 cores、16 GB RAM）[pdf:E08]（PDF 物理页 5，Section 3.3）。论文未报告时间步长、误差容限、线性/非线性 solver 配置、浮点精度、显式并行依赖图或内存峰值；没有开关器件、事件处理、多速率 EMT，也没有 FPGA mapping（FPGA 映射）或硬件在环实现。换言之，这是一套 CPU 上的连续时间有限元降阶模型，而不是 FPGA 实时仿真器。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出严格的误差界或收敛证明，但给出了完整的控制方程与耦合关系。下面按工程因果链重排。

**第一步：用 \(\mathbf A\) 求全局磁场。**磁矢势满足

\[
\nabla^2\mathbf A=-\mu\mathbf J,\qquad \mathbf B=\nabla\times\mathbf A.
\]

这里 \(\mathbf J\) 是带材产生的电流密度，\(\mathbf A\) 在整个 bounded universe（有界计算域）求解，因此不同带材通过同一个磁场问题相互耦合 [pdf:E04]（PDF 物理页 4，Eq. (1) 与 Fig. 1）。

**第二步：用 \(\mathbf T\) 描述超导薄层内的电流重分布。**论文写为

\[
\nabla\times\bigl(\rho\,\nabla\times\mathbf T\bigr)=-\frac{\partial\mathbf B}{\partial t},
\qquad \mathbf J=\nabla\times\mathbf T.
\]

在 2D tape 截面中，\(\mathbf T\) 只剩 \(T_y\)，于是

\[
J_z=\frac{\partial T_y}{\partial x},\qquad
\frac{\partial}{\partial x}\left(\rho_{\mathrm{HTS}}\frac{\partial T_y}{\partial x}\right)=\frac{\partial B_y}{\partial t}.
\]

直观上，\(T_y\) 沿带宽的斜率就是沿带长方向的电流密度；外部与自生磁场的时间变化推动这个斜率重新分布 [pdf:E04]（PDF 物理页 4，Eq. (2)、Eq. (3) 与 Fig. 1）。

**第三步：用边界值差直接施加 transport current（输运电流）。**由 Stokes 关系，

\[
I=\iint_S\mathbf J\,dS
 =\iint_S\nabla\times\mathbf T\,dS
 =\oint_{\partial S}\mathbf T\,d\mathbf r,
\qquad I=(T_1-T_2)\,\delta .
\]

\(\delta\) 是真实 HTS 层厚度，因此改变 1D 线两端的 \(T_1,T_2\) 就能固定每根带材的电流。随后把体电流压成 sheet current（面电流）

\[
\mathbf K=\delta J_z,\qquad
\mathbf n\times(\mathbf H_1-\mathbf H_2)=\mathbf K,
\]

并将其作为 \(\mathbf A\) 问题的磁场跳跃边界条件 [pdf:E05]（PDF 物理页 4，Eq. (4)–(6)）。

**第四步：加入超导非线性。**HTS 电阻率采用 E–J power law：

\[
\rho_{\mathrm{HTS}}
 =\frac{E_c}{J_c(\mathbf B)}
  \left|\frac{J}{J_c(\mathbf B)}\right|^{N-1},
\]

临界电流密度用各向异性的 modified Kim relation：

\[
J_c(\mathbf B)=
\frac{J_{c0}}
{\left(1+\dfrac{\sqrt{k^2B_{\parallel}^2+B_{\perp}^2}}{B_0}\right)^{\alpha}}.
\]

功率律让 \(|J|\) 接近或超过 \(J_c\) 时电阻率陡增；Kim 关系则让平行与垂直磁场分量以不同权重削弱 \(J_c\) [pdf:E07]（PDF 物理页 5，Eq. (7)、Eq. (8)）。

**第五步：在 homogeneous model 中守恒总电流而缩小源项。**bulk 上下边界使用

\[
\frac{\partial T_y}{\partial n}=0,
\]

并把 bulk 内的 \(J_z\) 缩放为

\[
J_s=\frac{\delta}{\Lambda}J_z,
\qquad
\nabla^2A_z=-\mu_0(\sigma_0E_z+J_s),\quad \sigma_0=0,
\]

其中 \(\Lambda\) 是 unit-cell 厚度。\(\delta/\Lambda\) 的作用是：bulk 占据了原本含绝缘与基底的较大截面，源电流必须按真实超导填充率缩小，才能保持每根带材对应的总安匝 [pdf:E11]（PDF 物理页 8，Eq. (11)–(13) 与 Fig. 6）。

**第六步：定义损耗与分布误差。**50 Hz 验证中，平均磁滞损耗取周期后半段：

\[
Q_{\mathrm{av}}=\frac{2}{P}\int_{P/2}^{P}\int_{\Omega}\mathbf E\cdot\mathbf J\,d\Omega\,dt.
\]

电流密度拟合质量用

\[
R^2=1-
\frac{\sum_{i=1}^{m}(J_H-J_{TA})^2}
{\sum_{i=1}^{m}(J_H-\overline J_H)^2},
\]

其中向量包含所有带材、所有采样位置和所有时间步。它比只看总损耗更严格，因为总损耗可能相近，而局部 \(J\) 形状仍然错误 [pdf:E09]（PDF 物理页 6，Eq. (9)、Eq. (10) 及相邻定义）。

数学上的关键代价也很清楚：1D T–A 假设使 \(J\) 只能沿带宽变化，不能解析平行磁场穿入带厚方向的过程；论文只在平行分量影响可忽略时宣称适用，并明确说 long solenoid（长螺线管）类情形不能用该 formulation [pdf:E05]（PDF 物理页 4，Eq. (6) 后正文）。

## § 7 — 实验设计与结论

**问题 1：T–A full 能否替代 H full 作为高精度 reference？**作者先在 11 A、50 Hz 的一个周期上把带宽单元数从 25 扫到 150，用损耗误差和全时空 \(J\) 的 \(R^2\) 比较 H full 与 T–A full。60 个单元时损耗误差低于 1%、\(R^2>0.99\)，作者据此固定后续网格 [pdf:E09]（PDF 物理页 6，Fig. 3）。场图、\(J_n\) 和逐带材损耗曲线在两种 full model 间接近重合 [pdf:E10]（PDF 物理页 7，Fig. 4）。Appendix A 的量化表进一步显示，\(T\) 一阶、\(A\) 二阶时平均损耗为 128.0560 W m⁻¹，相对 H full 的误差 0.64%，\(R^2=0.9922\)，耗时 3 h 14 min；H full 为 31 h 32 min [pdf:E16]（PDF 物理页 13，Table A1）。**答案：**在该 racetrack coil 与该激励下，T–A full 足以作 reduced models 的数值 reference。

**问题 2：为什么必须用混合阶数？**作者比较 \(T/A\) 的一阶/一阶、二阶/二阶和一阶/二阶组合；同阶组合在亚临界 \(J\) 区域出现伪振荡，只有一阶 \(T\)+二阶 \(A\) 的曲线消除明显振荡并取得最高 \(R^2\) [pdf:E15]（PDF 物理页 12，Appendix A 正文）[pdf:E16]（PDF 物理页 13，Fig. A1 与 Table A1）。**答案：**混合有限元对本文实现不是可选优化，而是避免假电流纹波的必要数值条件；但作者没有解释其理论稳定性，只报告试错结果。

**问题 3：multi-scale 与 homogeneous 是否保留慢周期结果并达到实时？**实验使用 11 A、3 h 充放电，以 T–A full 为 reference，比较峰值 \(|\mathbf B|\)、\(J_n\)、逐带材损耗、总损耗、\(R^2\) 和墙钟时间 [pdf:E13]（PDF 物理页 10，Fig. 9 与 Section 5）[pdf:E14]（PDF 物理页 11，Fig. 10 与 Table 2）。Table 2 报告：T–A full 为 0.8832 J m⁻¹、9 h 04 min；multi-scale 为 0.8807 J m⁻¹、0.28% 误差、\(R^2=0.9888\)、1 h 13 min；homogeneous 为 0.9025 J m⁻¹、2.18% 误差、\(R^2=0.9573\)、37 min [pdf:E14]（PDF 物理页 11，Table 2）。按表内时长换算，两个降阶模型相对 full 约加速 7.5 倍和 14.7 倍，且都短于 3 h。**答案：**论文的核心实时 claim 在这一台电脑、这一种对称线圈和这一条慢速电流曲线上成立；multi-scale 更准，homogeneous 更快。

**问题 4：T–A 对极慢周期的计算时间是否稳定？**Appendix B 使用 20-tape benchmark #3，电流幅值为 \(0.5I_c=150\,\mathrm A\)，频率从 \(5\times10^{-5}\) 到 50 Hz [pdf:E17]（PDF 物理页 13，Appendix B setup）[pdf:E18]（PDF 物理页 14，Table B1）。Fig. B2 显示 T–A full 在全频段约为 300 s，而 H full 随频率降低显著变慢，在 \(5\times10^{-5}\,\mathrm{Hz}\) 达 36.6 h；两者每周期损耗曲线仍接近 [pdf:E17]（PDF 物理页 13，Appendix B 右栏）[pdf:E18]（PDF 物理页 14，Fig. B1、Fig. B2）。**答案：**在作者的 COMSOL 配置中，T–A 对慢周期比 H 更有利，但这同时是 formulation 与 solver 实现的联合结果，不能自动外推到所有软件和求解器。

**不能外推的范围。**新 reduced models 没有与实验直接比较，只是链式地依赖“既有 H model 已有实验验证 → 本文 H full → T–A full → reduced models”；只测试了一种几何、一条 11 A 慢曲线和一台 CPU 电脑。正文没有 fast transient、不同电流幅值、材料离散性、局部缺陷、动态采样策略、内存、solver tolerance 或跨平台结果。作者自己也把适用范围限制在 1D approximation 有意义、平行磁场影响可忽略的场景 [pdf:E15]（PDF 物理页 12，Conclusions）。

**源 PDF 内部的两处数值/标注不一致。**Section 5 正文把 homogeneous 损耗误差写成 2.23%，Table 2 写 2.18%；由表中 0.9025 与 0.8832 直接计算得到约 2.185%，因此 2.18% 与表内数字自洽 [pdf:E13]（PDF 物理页 10，右栏上部）[pdf:E14]（PDF 物理页 11，Table 2）。另外，Fig. 10 顶部把中、右两列标成 “T–A Homogeneous / T–A Multi-scale”，但图例与 caption 把中、右两列解释为 multi-scale / homogeneous；解读定量结果时应以图例、caption 和 Table 2 为准 [pdf:E14]（PDF 物理页 11，Fig. 10）。

## § 8 — Take-aways

**5 句话。**

1. 论文把 T–A thin-sheet formulation 与 multi-scale、homogenization 结合，目标是在个人电脑上计算大型 2G HTS 系统的局部电流、全局磁场和磁滞损耗 [pdf:E01]（PDF 物理页 2，Abstract）。
2. multi-scale 只对 30 根代表带材求 \(T\) 并插值其余带材，homogeneous 则把 500 根对称模型带材压成 5 个 bulk、每个 bulk 仅 6 个堆叠方向单元 [pdf:E11]（PDF 物理页 8，Section 4.3）[pdf:E12]（PDF 物理页 9，Fig. 7、Fig. 8）。
3. 在 3 h、11 A 的慢充放电中，两种降阶模型分别以 0.28% 和 2.18% 的总损耗误差，把 9 h 04 min 的 full 计算降到 1 h 13 min 和 37 min [pdf:E14]（PDF 物理页 11，Table 2）。
4. 这一结果依赖一阶 \(T\)+二阶 \(A\) 的混合元、1D 薄层近似、可忽略的平行场穿透以及带材编号方向上可插值的平滑变化 [pdf:E11]（PDF 物理页 8，Fig. 5、Fig. 6）[pdf:E15]（PDF 物理页 12，Conclusions 与 Appendix A）。
5. 论文证明的是特定慢周期下的离线墙钟实时性，不是开关级 EMT、硬件闭环或 FPGA 实时执行 [pdf:E08]（PDF 物理页 5，计算平台）[pdf:E13]（PDF 物理页 10，real-time 定义）。

**3 句话。**

1. 方法先用 T–A 降低单根带材的维度，再用稀疏带材或 bulk 降低带材数量维度。
2. 在作者的 2000 匝 racetrack case 上，multi-scale 提供更好的精度，homogeneous 提供更大的速度收益 [pdf:E14]（PDF 物理页 11，Table 2）。
3. 最大风险不是总损耗误差，而是固定采样与均匀化可能漏掉未采样带材上的局部非平滑电流或损耗峰值。

**1 句话。**

这是一篇用两层物理降阶换取慢周期实时性的工程论文，其结果有说服力，但适用性取决于薄层假设与跨带材平滑性是否真的成立。

## § 9 — 最脆弱的假设

最脆弱的假设不是“COMSOL 是否够快”，而是：**沿带材编号方向，\(J\) 与损耗足够平滑，而且高梯度区域可以在仿真前被正确识别，因此固定的 30 根分析带材或 6 个 bulk 单元能够代表全部带材。**multi-scale 对未分析带材直接做线性 \(J\) 插值，再以 PCHIP 补损耗；homogeneous 把整段带材集合平均进 bulk [pdf:E11]（PDF 物理页 8，Fig. 5、Fig. 6）[pdf:E12]（PDF 物理页 9，Section 4.3–4.4）。更关键的是，作者选择上部更多分析带材的依据，正是 full model 已显示那里损耗变化更大 [pdf:E11]（PDF 物理页 8，Section 4.3）。

如果运行工况改变后高梯度区移动，或某一根未分析带材出现与邻带不连续的 \(J_c\)、局部场或几何偏差，插值模型会把真实尖峰平滑掉，bulk 模型则会把它平均掉。此时总损耗仍可能因局部异常占比小而保持“2% 以内” [pdf:E14]（PDF 物理页 11，Table 2 的全局损耗误差量级），但最大逐带材损耗、局部 \(J/J_c\) 和潜在热点位置会错；这会直接破坏作者强调的“individual tape（单根带材）高精度”和 digital twin（数字孪生）价值。这个失败代价比总损耗略有偏差更大，因为用户可能在最需要局部告警时得到一幅看似平滑、全局指标也正常的结果。

论文提供的证据是一种均匀参数、强对称 racetrack coil 上的一次固定采样验证，\(R^2=0.9888/0.9573\) 说明在该 case 上插值确实有效 [pdf:E14]（PDF 物理页 11，Table 2）。但论文没有 blind sampling（盲采样）、工况转移、单带材参数扰动、误差指示器或自适应增采样实验，因此没有证明这个平滑性假设在未知设备状态下仍成立。这里是**基于证据的批评**，不是论文直接承认的 limitation。

## § 10 — 最小复现实验

一周内最值得做的，不是完整重建所有 H full 结果，而是验证“固定稀疏采样是否能在可控精度下换来实时速度”。

**数据与工况。**使用 Table 1 的四分之一 racetrack geometry：5 个 pancakes、每个 100 根带材，带宽和 unit-cell 尺寸按论文；电流使用 Fig. 9 的 11 A、3 h 充放电。\(T\) 一阶、\(A\) 二阶，带宽 60 单元，且关闭后处理 smoothing，以免隐藏 Appendix A 所示的伪振荡 [pdf:E06]（PDF 物理页 5，Fig. 2、Table 1）[pdf:E13]（PDF 物理页 10，Fig. 9）[pdf:E16]（PDF 物理页 13，Fig. A1）。源 PDF 的 \(J_{c0}\) 指数缺失意味着严格数值复现存在材料参数缺口；可把同一 PDF 图 A1 显示的 \(10^{10}\,\mathrm{A/m^2}\) 量级作为**待检验假设**，但必须在报告中明确它不是表 1 的已认证转录。

**实现。**只建三套 T–A：full、论文固定 30-tape multi-scale、5-bulk homogeneous；不建耗时最大的 H full。先用一个短时段检查电流守恒、边界 \(T_1-T_2\)、\(J\) 是否无伪振荡，再跑完整 3 h 波形。模型结构、采样编号、60/30 单元分配和 PCHIP 按 Section 4 复现 [pdf:E11]（PDF 物理页 8，Section 4.1–4.3）[pdf:E12]（PDF 物理页 9，Fig. 7、Fig. 8）。

**测量。**记录三项：全周期总损耗相对 full 的误差；在统一空间和时间采样上的 \(J\) 分布 \(R^2\)；墙钟时间。另加一个论文没有重点报告但更关键的指标：逐带材损耗最大绝对误差与最大 \(|J/J_c|\) 误差。

**支持标准。**在相近 4-core CPU 上，multi-scale 若总损耗误差不超过 1%、\(R^2\ge 0.98\)、墙钟时间小于 3 h；homogeneous 若总损耗误差不超过 3%、\(R^2\ge 0.95\)、墙钟时间小于 3 h，就支持论文的核心工程 claim。具体数值门槛来自 Table 2 的 0.28%、0.9888、1 h 13 min 与 2.18%、0.9573、37 min [pdf:E14]（PDF 物理页 11，Table 2）。

**反驳标准。**若在正确混合元和相同波形下，任一 reduced model 不能同时达到上述精度与实时条件，或全局指标合格但最大逐带材误差很大，则论文关于“快速且保持单带材高精度”的 claim 至少不能由该实现复现。由于 solver tolerance、time stepping 与完整材料参数未闭合，这个一周实验只能判定功能性复现，不能要求与论文墙钟时间逐分钟一致。

## § 11 — 最强反例设计

最强反例是在**保持同一几何和同一 3 h 慢周期**的前提下，只给一根未分析带材制造局部不连续，从而隔离“固定插值”这一机制是否可靠。

具体做法是选每个 pancake 的分析集合 \(\{25,66,88,96,99,100\}\) 之外、且远离相邻分析点的一根带材，例如 tape 80，把其 \(J_c(\mathbf B)\) 整体降低 20%–30%，其余参数不变。先用 T–A full 得到 ground truth，再运行原始固定 multi-scale 与 homogeneous。比较总损耗、tape 80 的峰值 \(|J/J_c|\)、逐带材损耗曲线和异常位置识别率；还要把异常带材从 70 扫到 90，防止结果只对某个编号偶然成立。

替代解释很明确：若 reduced models 仍给出漂亮的总损耗和高 \(R^2\)，却漏掉 tape 80 的局部损耗峰值，那么论文的全局一致性不是因为方法真正恢复了每根带材，而是因为全局误差指标被大量正常带材稀释。multi-scale 的线性插值在数学结构上无法凭空产生未采样的单点突变，homogeneous 更会主动平均它；因此这是可预测、机制性的失败，而不是调参不足 [pdf:E11]（PDF 物理页 8，Fig. 5、Fig. 6）[pdf:E12]（PDF 物理页 9，PCHIP 与固定网格说明）。

这个反例若成功，不会否定 T–A full，也不会否定论文在均匀 racetrack case 上的 Table 2；它会否定更强的应用外推：固定采样 reduced model 可以充当未知状态下的单带材 digital twin。

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty：error-certified adaptive T–A digital twin（带误差认证的自适应 T–A 数字孪生）。**论文所在的工程数值建模领域，真正高影响的后续工作通常不仅要更快，还要证明在新几何、新工况和实际非均匀性下仍能给出可信局部量；本文自己也把快速 parametric simulation 与 digital twin 作为价值目标 [pdf:E15]（PDF 物理页 12，Conclusions）。

**(a) 未满足需求。**固定 30 根分析带材与 6 个 bulk 单元需要预先知道高梯度区，而且没有在线误差告警。数字孪生最需要处理的恰恰是状态变化、参数漂移和局部异常；只报告总损耗误差不足以保证热点不被漏掉。

**(b) 可能的研究价值。**把研究目标从“在一个已知 case 上尽量少算”改成“在给定实时预算内，对最大逐带材 \(J\)/损耗误差给出可验证上界”。若能同时做到小于物理时长、自动发现局部异常并在多工况下保持误差界，它比再固定增加几根分析带材更接近可部署的 digital twin。

**(c) 可借鉴的相邻工具。**可把 adaptive mesh refinement（自适应网格细化）、goal-oriented error estimation（目标导向误差估计）和 active sampling（主动采样）的思想移到“带材编号”维度：全局仍求 \(A\)，少量带材求 \(T\)；根据相邻带材插值残差、\(J/J_c\) 曲率或功率密度不确定度，动态把可疑带材 promote 为 analyzed tape，或把 bulk 局部拆分。这里是方法候选，不把这些工具在 HTS 场景中的新颖性当作既成事实。

**(d) 第一个可证伪实验。**随机隐藏一根 \(J_c\) 降低 20%–30% 的未分析带材，位置和幅度对算法不可见；比较 fixed multi-scale、adaptive model 与 T–A full。若 adaptive model 不能在第一次完整充放电内定位异常，并把最大逐带材损耗误差压到预设阈值，同时保持墙钟时间小于 3 h，这个想法就被首轮证伪。

**(e) 与本文的实质区别。**本文以 fixed sampling + interpolation/bulk averaging 换速度，采样位置来自对 full model 变化分布的先验观察 [pdf:E11]（PDF 物理页 8，Section 4.3）。候选方案把采样位置本身变成求解变量，并把“是否还可信”作为模型输出；它改变的是问题定义和验收目标，而不是仅增加更多带材或换一个应用几何。
