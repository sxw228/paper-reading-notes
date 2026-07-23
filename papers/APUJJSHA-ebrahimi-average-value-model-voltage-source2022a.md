# Average-Value Model for Voltage-Source Converters With Direct Interfacing in EMTP-Type Solution

- Zotero key：`APUJJSHA`
- corpus order：`36`
- 作者：Seyyedmilad Ebrahimi；Juri Jatskevich
- 出处：*IEEE Transactions on Energy Conversion*, vol. 38, no. 3, September 2023
- DOI：`10.1109/TEC.2022.3220085`
- 源 PDF：`_source.pdf`
- PDF SHA-256：`a8e7b65ffb5c98927e673551c5ad62231278348ee3e83b44ad96e7f6a4766db1`
- 证据说明：`[pdf:E..]` 指向本目录 `_evidence/` 中的 PDF 上下文截图；物理页从 PDF 首页按 1 开始。论文事实与基于证据的推断在正文中明确区分。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的 EMT 接口问题：VSC 的 average-value model（AVM）本来可以忽略高频开关，从而使用比详细开关模型更大的仿真步长；但在 PSCAD 一类 EMTP-type 程序里，传统做法用受控电压源和受控电流源把 AVM 接到外部网络。非迭代求解时，网络变量和受控源之间会多出一个人为的一步延迟，步长变大后就会引入误差，甚至数值不稳定。作者的目标不是再简化 VSC 本体，而是消除这个接口延迟，使 AVM 的“大步长优势”在系统级网络中真正可用。[pdf:E01] [pdf:E03]

这件事的重要性来自两个时间尺度的冲突。详细 VSC 模型必须解析开关动作，因而要求很小的步长；AVM 把开关纹波平均掉，只保留慢于开关频率的动态，本应适合大规模离线 EMT 和实时仿真。如果接口实现又迫使 AVM 回到小步长，平均化带来的主要计算收益就被抵消。论文因此把“模型是否快”重新定位为“模型能否以与网络方程一致的方式进入每一步求解”。[pdf:E01]

![标题、摘要、研究问题与通用 VSC 系统图](_evidence/E01-p001-title-abstract-introduction.png)

## § 2 — 前人工作与不足

论文区分了三类前置工作。第一类是 VSC 详细开关模型：它保留开关过程，但为了稳定性和精度必须使用很小的步长。第二类是 conventional analytical AVM：它把 VSC 的基波端口关系写成受控源，模型连续且与开关频率无关，但传统 indirect interfacing（IDI）在非迭代 EMTP 求解中使用上一步的端口量生成本步受控源，因此有额外一步延迟。第三类是作者此前为 line-commutated converter（LCC）提出的 direct interfacing；那项工作说明直接结点接口可行，但依赖数值提取的 lookup table，不能直接替代本文面向 VSC 的解析公式。[pdf:E01] [pdf:E02]

已有方法的不足不只是“精度略差”。IDI 的输出 \(v_{abc}^{1}(t)\) 和 \(\bar i_{dc}(t)\) 由 \(\bar v_{dc}(t-\Delta t)\) 与 \(i_{abc}^{1}(t-\Delta t)\) 计算，接口因果链被人为向后移了一步；\(\Delta t\) 越大，这个延迟代表的物理时间越长，可能形成明显的相位误差或不稳定。加 compensated snubber 可以提高 IDI 的数值稳定性，但会用瞬态误差换稳定范围，阻尼电阻的选择成为“可用步长与准确性”的折中。[pdf:E03] [pdf:E08]

![传统接口、LCC 前作与本文 VSC 直接接口定位](_evidence/E02-p001-prior-work-direct-interface-claim.png)

## § 3 — 重建作者的思考路径

下面是基于论文背景与公式结构重建的思考路径，不是作者逐字陈述。

1. 研究者先观察到：VSC 的 analytical AVM 本身已经消除了开关时间尺度，却仍在大步长时失稳；因此瓶颈可能不在平均模型，而在模型与 EMTP 网络的交换顺序。[pdf:E01]
2. 把传统实现逐项展开后可以看见，受控源在本步只能使用上一步网络解；这不是 VSC 的物理动态，而是模块化接口制造的额外延迟。[pdf:E03]
3. EMTP 网络本来就在每一步求解结点形式 \(G V=I\)。如果能把 AVM 也改写为端口阻抗或导纳矩阵加历史源，它就可与外部网络同时求解，而不必等待网络先给出本步变量。[pdf:E02] [pdf:E05]
4. VSC analytical AVM 已给出 \(qd\) 坐标下 ac/dc 端口关系；因此可先把电压写成电流的函数，得到包含 ac-ac、ac-dc、dc-ac、dc-dc 耦合项的阻抗矩阵，再变换回 \(abc\) 坐标并求逆为导纳 stamp。[pdf:E04] [pdf:E05]
5. 最后用同一系统、同一工况比较 IDI 与 DI，逐步扩大 \(\Delta t\)，才能把“接口延迟被消除”与“大步长下仍准确稳定”连成可检验的因果链。[pdf:E06] [pdf:E07]

## § 4 — 核心 Intuition

核心 intuition 是：不要把 VSC AVM 当作网络求解之后才更新的黑盒受控源，而要把它变成网络方程中的一个结点 stamp。这样，VSC 端口电压、电流与外部网络变量在同一次结点求解中闭合；模型仍可使用上一时刻的真实历史项，但不再额外推迟一个接口步长。[pdf:E02] [pdf:E05]

## § 5 — 具体方法与完整 Pipeline

以图 1 的三相 AC Thévenin 等值—两电平 VSC—DC RLC 系统为例，输入是电网同步角 \(\theta_s\)、功角 \(\delta\)、调制比 \(M\)、上一时刻的 \(\bar v_{dc}(t-\Delta t)\) 以及外部网络的本步未知结点电压；输出是本步 \(abc\) 侧基波端口量与 DC 侧平均端口量。[pdf:E01] [pdf:E06]

1. **建立 conventional AVM 关系。** 用 Park 变换把 \(abc\) 基波量转到旋转 \(qd\) 坐标。式 (1) 把 \(qd\) 侧平均电压写成 \(\frac12 M[\cos\delta,\sin\delta]^T\bar v_{dc}\)；式 (2) 把 DC 侧受控电流写成 \(\frac34 M\cos\varphi\lVert\bar i_{qd}\rVert\)，其中式 (3) 给出 \(\varphi=\tan^{-1}(\bar i_d/\bar i_q)-\delta\)。[pdf:E03]
2. **保留 DC 接口阻尼与补偿。** 式 (4) 用 snubber \(R_x\) 建立 DC 电压，式 (5) 的 \(i_{\mathrm{comp}}(t)=\bar v_{dc}(t-\Delta t)/R_x\) 补偿 snubber 的稳态作用。这里的 \(t-\Delta t\) 是 EMTP 离散系统本来就需要的历史状态，而不是 IDI 在模块边界额外引入的延迟。[pdf:E03] [pdf:E05]
3. **改写为四端口阻抗形式。** 作者把 \(qd\) 两轴和 DC 端口合并，写成式 (6) 的电压—电流关系。式 (9) 的块矩阵显式给出 \(Z_{qd}\)、\(Z_{qd,dc}\)、\(Z_{dc,qd}\)、\(Z_{dc,dc}\)，这些项由 \(M\)、\(\delta\) 和 \(R_x\) 决定；式 (10) 给出依赖上一时刻 DC 电压的历史电压源。[pdf:E04]
4. **变回网络使用的 \(abc,dc\) 坐标。** 式 (11)–(17) 把 \(qd,dc\) 阻抗矩阵和历史项变换为三相 AC 加 DC 的统一端口表达；交叉块保留 AC/DC 功率转换的耦合，不能把 AC 与 DC 两侧分别求解后再拼接。[pdf:E04] [pdf:E05]
5. **生成 EMTP stamp 并同时求解。** 对端口阻抗矩阵求逆得到式 (18)–(19) 的 \(G_{\mathrm{VSC}}^{abc,dc}\) 与历史电流向量 \(i_{h,\mathrm{VSC}}^{abc,dc}\)，把它们并入全网 \(G V=I\)。本步网络解同时给出 VSC 与外部网络的端口量，消除了传统受控源接口的额外一步等待。[pdf:E05]

![传统 IDI-AVM 的式 (1)–(5) 与一步延迟](_evidence/E03-p002-idi-avm-eq01-05-delay.png)

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学核心不是重新推导平均化理论，而是把已有 analytical AVM 改写成可直接压入结点矩阵的 Norton/结点形式。

首先，式 (6) 将三维端口量写为

\[
\begin{bmatrix}\bar v_q\\ \bar v_d\\ \bar v_{dc}\end{bmatrix}
=
Z_{\mathrm{VSC}}^{qd,dc}
\begin{bmatrix}\bar i_q\\ \bar i_d\\ \bar i_{dc}\end{bmatrix}
+e_{h,\mathrm{VSC}}^{qd,dc}.
\]

直观上，\(Z_{\mathrm{VSC}}^{qd,dc}\) 是当前步端口之间的瞬时线性耦合，\(e_h\) 则携带离散系统的合法历史。作者从式 (1)–(5) 消去功率因数角相关的非线性表达并用三角恒等式整理，得到式 (9) 的解析矩阵：对角/同侧项描述 AC 两轴和 DC 端口自身关系，非对角块描述 AC 与 DC 的双向耦合；历史项由式 (10) 给出。[pdf:E04]

其次，Park 逆变换把 \(qd\) 关系还原到三相端口，形成式 (11)–(17) 的 \(Z_{\mathrm{VSC}}^{abc,dc}\) 与 \(e_{h,\mathrm{VSC}}^{abc,dc}\)。其中历史向量显式含有 \(\bar v_{dc}(t-\Delta t)\)，说明“消除延迟”不是抛弃状态记忆，而是只消除接口顺序造成的额外延迟。[pdf:E04] [pdf:E05]

最后，对阻抗矩阵求逆：

\[
G_{\mathrm{VSC}}^{abc,dc}=\left[Z_{\mathrm{VSC}}^{abc,dc}\right]^{-1},\qquad
i_{h,\mathrm{VSC}}^{abc,dc}=G_{\mathrm{VSC}}^{abc,dc}e_{h,\mathrm{VSC}}^{abc,dc}.
\]

于是式 (18) 成为标准结点 stamp：

\[
G_{\mathrm{VSC}}^{abc,dc}
\begin{bmatrix}v_{abc}^{1}\\ \bar v_{dc}\end{bmatrix}
=
\begin{bmatrix}i_{abc}^{1}\\ \bar i_{dc}\end{bmatrix}
+i_{h,\mathrm{VSC}}^{abc,dc}.
\]

物理意义是：本步 AC 与 DC 端口量由同一个代数系统闭合；数值意义是：VSC 不再作为落后一步的外部信号源。论文还指出，如果去掉 \(i_{\mathrm{comp}}\)，历史项可为零，但这等价于不补偿 snubber，会给 DC 稳态量以及 AC 端口量带来误差，因此不是无代价简化。[pdf:E05]

![DI-AVM 的阻抗矩阵、历史项与坐标变换](_evidence/E04-p002-di-avm-eq06-16.png)

![DI-AVM 的式 (17)–(19)、结点 stamp 与历史源机制](_evidence/E05-p003-di-avm-eq17-19-mechanism.png)

## § 7 — 实验设计与结论

**问题 1：在小步长下，直接接口是否保持 conventional AVM 的行为？** 作者建立图 1 的 AC–DC 系统，并实现 detailed switching model、0.1 μs 的 IDI reference AVM、IDI-AVM 和 DI-AVM。VSC 是 1620 Hz、SPWM 的 conventional two-level topology；初始 \(\delta=-25^\circ,M=0.5\)，以整流模式从 AC 向 DC 传输 200 MW；50 ms 时改为 \(\delta=25^\circ,M=0.7\)，进入逆变模式并从 DC 向 AC 传输 240 MW。IDI 与 DI 都以 10 μs 运行时，它们的 AC 电流、DC 电压和 DC 线路电流与 reference AVM 基本重合，且 AVM 能跟随详细模型的平均/基波分量。[pdf:E06]

**问题 2：步长变大后，消除接口延迟是否改善稳定性和精度？** 图 5 将无 snubber 的 IDI 设为 400 μs，将 compensated-snubber IDI 与 DI 都设为 1000 μs。无 snubber 的 IDI 在中等步长已明显失真/不稳定；加 \(R_x=10\,\Omega\) 后虽更稳定，但瞬态偏差明显；DI 在 1000 μs 下仍贴近 0.1 μs reference。图 6 的 AC 电流 2-norm error 扫描也显示 DI 的误差随步长增长得慢得多，而两种 IDI 分别受不稳定或 snubber 误差限制。[pdf:E07] [pdf:E08]

**问题 3：收益相对于 switching model 有多大？** 表 I 报告的是“可用最大步长的数量级”，不是通用硬上限：VSC switching model 在无插值时需 \(\Delta t<0.01\,\mu s\)，有开关插值时约 20–50 μs；IDI-AVM 约 200–250 μs；VSC/LCC 的 DI-AVM 约 1000–2000 μs，且两类 AVM 都不需要开关插值。这个结果支持 DI-AVM 的大步长潜力，但它基于本文系统和引用 [4] 的系统，不能外推为所有 VSC 网络的保证。[pdf:E07] [pdf:E09]

![图 4：模型、工况与 10 μs 小步长对比](_evidence/E06-p003-fig04-experiment-setup.png)

![图 5、图 6 与表 I：大步长波形、误差和可用步长数量级](_evidence/E07-p004-fig05-06-table01.png)

![作者对大步长结果与 snubber 折中的解释](_evidence/E08-p004-results-analysis.png)

## § 8 — Take-aways

**5 句话。**  
1. 这篇论文真正改动的是 VSC AVM 与 EMTP 网络的接口，而不是平均模型的物理层级。  
2. 传统 IDI 把本步端口变量错开为上一步受控源输入，大步长会放大这一人为延迟。  
3. DI-AVM 把 AC/DC 耦合端口改写为 conductance matrix 加 history current source，并入全网同一次 \(GV=I\) 求解。[pdf:E05]  
4. 单一 AC–DC 算例中，DI 在 1000 μs 下仍接近 reference，而 IDI 要么失稳，要么依赖 snubber 并牺牲瞬态精度。[pdf:E07] [pdf:E08]  
5. 收益只覆盖 AVM 有效的慢动态与论文测试过的系统，不能解释开关纹波，也尚未证明对弱网、不平衡故障或多 VSC 大网络同样成立。[pdf:E01] [pdf:E09]

**3 句话。**  
1. 把平均模型直接压入结点矩阵，可以消除模块化受控源接口制造的一步延迟。  
2. 论文给出了从 \(qd\) analytical AVM 到 \(abc,dc\) 导纳 stamp 的完整解析路径，并在大步长下展示了稳定性和精度优势。[pdf:E04] [pdf:E07]  
3. 最关键的边界是平均化假设与验证覆盖面，而不是导纳矩阵本身。

**1 句话。**  
VSC AVM 能否真正“大步长”，取决于它是否作为网络方程的一部分同时闭合，而不只是它是否省略了开关。[pdf:E01] [pdf:E05]

## § 9 — 最脆弱的假设

最脆弱的假设是：研究者关心的 VSC—网络动态都显著慢于开关频率，因此 analytical AVM 丢弃开关过程后仍保留了决定系统结论的物理。论文在引言中明确限定 AVM 只对慢于开关频率的动态有效；超过该频率，平均化假设可能失效。[pdf:E01]

这个假设一旦不成立，DI-AVM 即使数值稳定，也可能只是“稳定地算错物理”。例如弱网 PLL 交互、控制饱和、限流切换、不平衡故障、DC 侧高频谐振或开关谐波驱动的滤波器共振，都可能使被平均掉的频率成分或离散事件决定结果。本文的直接证据只有一个 two-level、1620 Hz SPWM 系统，一次从整流到逆变的功角/调制比阶跃，以及所列 AC/DC 参数；没有故障、控制限幅、参数扫描、多换流器耦合或实时硬件实测。[pdf:E06] [pdf:E09]

因此，论文有力证明的是“同一 AVM 在直接接口下比间接接口更能承受大步长”，而不是“DI-AVM 在所有 VSC EMT 问题中都保持详细开关模型的物理保真度”。这是基于证据的边界判断，不是作者声称失败。

![表 I 的适用语境、结论与附录系统参数](_evidence/E09-p004-table-discussion-conclusion-appendix.png)

## § 10 — 最小复现实验

一周内可做一个不依赖完整商业 EMT 平台的最小复现。

1. **数据与系统。** 按附录建立图 1：线电压 RMS 100 kV、60 Hz、\(r_{ac}=1.5\,\Omega\)、\(L_{ac}=37.14\,mH\)、\(r_{dc}=5.99\,\Omega\)、\(L_{dc}=84\,mH\)、\(C_{dc}=74.25\,\mu F\)、\(E_{dc}=200\,kV\)。VSC 使用 1620 Hz SPWM 的 two-level detailed model作为物理参照，并实现同一 analytical AVM。[pdf:E06] [pdf:E09]
2. **两个接口。** IDI 按式 (1)–(5) 用上一步端口量更新受控源；DI 按式 (9)–(19) 每步生成 \(abc,dc\) 导纳 stamp 和历史电流源。外部 RLC 网络使用相同的梯形离散和线性求解器，避免把求解器差异混入接口比较。[pdf:E03] [pdf:E04] [pdf:E05]
3. **工况。** 复现 \(\delta=-25^\circ,M=0.5,200\,MW\) 整流初态，并在 50 ms 切换到 \(\delta=25^\circ,M=0.7,240\,MW\) 逆变；先用 0.1 μs reference AVM，再扫描 10、50、100、200、400、1000 μs。[pdf:E06]
4. **测量。** 保存 \(i_a\)、\(\bar v_{dc}\)、\(i_L\)，计算 30–150 ms 区间相对 reference 的 AC 电流 2-norm error，同时记录发散、矩阵条件数和每仿真毫秒的 wall-clock cost。
5. **判据。** 若 DI 在 400–1000 μs 仍有界，且其 \(i_a\) 误差显著低于无 snubber 和 \(R_x=10\,\Omega\) 的 IDI，同时小步长结果不劣化，就支持论文的接口 claim；若在相同离散、容差和计算预算下 IDI 同样稳定准确，或 DI 的优势只来自不同阻尼/初始化，就反驳该 claim。

## § 11 — 最强反例设计

最有力的反例不是再找一个普通阶跃让 DI 发散，而是构造一个“结点求解稳定、物理答案错误”的场景，直接攻击第 9 节的平均化假设。

可把图 1 改为低短路比弱网，并加入带限幅与 anti-windup 的 PLL/current controller；在 50 ms 施加单相接地故障，使控制器进入限流并产生负序和高频侧带。用详细 switching model 在 0.1 μs 下给出参照，DI-AVM 分别以 50、200、1000 μs 运行。比较故障期间的峰值电流、DC 过电压、PLL 失锁边界、故障后恢复时间及能量误差，而不只比较基波 \(i_a\) 的 2-norm。

如果 DI-AVM 在所有步长下都数值稳定，却系统性漏报过流、过压或失锁，说明 direct interfacing 解决了接口数值延迟，但“大步长下准确”只对平衡慢动态成立。若 DI 在这些离散事件下仍能保持与 detailed model 一致，则反例失败，反而为方法扩展到保护与故障研究提供更强证据。论文没有执行这类测试；这是基于其已声明适用边界提出的攻击性验证。[pdf:E01] [pdf:E06]

## § 12 — Follow-up Research Idea

在电力系统 EMT 与电力电子建模领域，高影响工作通常不只看算法误差，还看数值稳定性、跨工况保真度、实时可实现性、可扩展到多设备网络的能力，以及硬件或商用实时平台上的闭环验证。基于本文最脆弱的平均化假设，一个候选的非增量方向是：**建立“可认证切换的多保真直接接口 VSC stamp”**。它不是给 DI-AVM 再加一个补偿模块，而是把研究目标从“永远使用一个平均模型”改为“在保持全网一次结点求解的前提下，按可观测误差风险切换端口物理分辨率”。

**(a) 未满足需求。** 现有 DI-AVM 可以在慢动态下大步长稳定运行，但无法保证故障、限流、弱网振荡或高频谐振时平均模型仍可信；详细 switching model 又会让整个系统回到极小全局步长。[pdf:E01] [pdf:E07]

**(b) 研究价值。** 若一个端口模型能给出在线误差证书，并只在少数风险窗口局部提升为谐波状态、开关事件或小步长子模型，就可能同时保留 DI 的全网可组装性和关键事件的物理保真度。这会把“速度—精度折中”变为可验证的动态资源分配问题。

**(c) 可借鉴工具。** 可借鉴 adaptive model order、a posteriori error estimator、hybrid systems 的 guard/重置逻辑，以及 waveform relaxation 或局部多速率积分；关键约束是所有模式都输出与式 (18) 兼容的端口 stamp 和历史源，使外部网络接口不改变。

**(d) 第一个可证伪实验。** 在第 11 节的弱网单相故障场景中，先冻结一个不参与训练的工况集；要求该方法在详细模型峰值电流、DC 过压、PLL 状态和能量误差超过阈值之前触发高保真模式，同时总计算量显著低于全程 switching simulation。若漏检关键事件，或切换本身产生非物理能量/数值不稳定，这个方向立即被证伪。

**(e) 与已有工作的实质区别。** 本文是在固定 analytical AVM 内消除接口延迟；候选方向则把“模型何时仍可信”纳入求解器状态，并要求不同物理分辨率共享同一直接结点接口。本文没有检索或验证这种多保真切换方案，因此这里只把它标为候选研究想法，不声称 novelty。
