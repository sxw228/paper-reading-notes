# Data-Enabled Finite State Predictive Control for Power Converters via Adaline Neural Network

- 作者：Wenjie Wu，Lin Qiu，Xing Liu，Jien Ma，Jose Rodriguez，Youtong Fang
- 出处：*IEEE Transactions on Industrial Electronics*, 72(3), 2244–2253
- 年份：2025
- DOI：10.1109/TIE.2024.3413837
- Zotero key：39XCSPF6

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是 finite control-set model predictive control（FCS-MPC）的一个根本矛盾：它能直接枚举功率变换器的有限开关状态，动态响应快、约束处理自然，却要用准确的电阻、电感、电容和系统模型预测每个候选开关的后果。温度、制造偏差、老化、非线性和未建模动态会使真实对象偏离名义模型，预测排序一旦错误，控制器就会选错开关，严重时不仅电流跟踪变差，还可能失稳。作者因此要回答：能否保留 FCS-MPC 的有限开关枚举与滚动优化，却把下一拍预测改为只依赖在线测得的历史输入输出数据？这一问题及论文给出的三部分方案——dynamic-linearization（DL）数据模型、Adaline 在线估计和无电容参数的中点电压平衡——在摘要与引言中被明确提出。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

工程价值不只是“少填几个参数”。3L-NPC 逆变器有 27 个电压矢量，还必须同时压住两只直流电容的电压差；传统预测式既要知道负载 \(R_g,L_g\)，又要知道 \(C_{dc}\)，多目标 cost function 还要调 weighting factor。若仅凭当前装置自身的 I/O 数据就能完成电流预测和中点平衡，同一控制结构面对参数漂移时可能少做辨识、标定和模型维护。但论文验证对象仍是带 RL 负载的单台 3L-NPC 原型，不能直接外推到 FPGA、多变换器耦合、电机反电动势或电网阻抗突变。

## § 2 — 前人工作与不足

作者把既有路线分为两类。第一类仍以物理模型为中心：在线 parameter identification 用 RLS 或 model-reference adaptive control 估计 \(R,L\) 等参数；disturbance-observer 路线用 Luenberger observer、ESO 或历史预测误差补偿模型失配。它们能缓解参数扰动，但预测器骨架、输入增益或补偿假设仍来自先验模型，例如“同一控制动作造成的预测误差在短时间内近似不变”。[pdf:E02]（PDF 物理页 2，Section I 左栏）

第二类用数据模型替代物理模型。LUT 方法存储某开关动作上次造成的电流增量，简单但牺牲灵活性和可靠性；ultralocal model 把非输入项并入总扰动，再用 ESO、sliding-mode observer、RLS 或 neural network 估计，但仍可能需要输入增益、初值或额外估计环。已有 data-driven continuous-set MPC、面向 PMSM 的实时 RLS，以及作者前作中的 DL-based predictive control 已证明方向可行。[pdf:E02]（PDF 物理页 2，Section I）[pdf:E10]（PDF 物理页 10，References [15]–[24]）

本论文相对其直接前作 [21] 的变化不是首次引入 DL，而是三点组合：用同时含输出增量与输入增量的 full-form dynamic linearization（FFDL）增加历史窗口的可调性；用结构简单的 Adaline 估计时变 pseudo-gradient；给原先 capacitance-less CVB 增加可设上界，使中点电压越界时提高平衡优先级。作者声称由此不再需要 \(R_g,L_g,C_{dc}\) 等物理参数，也不再需要传统多目标 weighting factor。[pdf:E02]（PDF 物理页 2，作者贡献段）

## § 3 — 重建作者的思考路径

先从已知矛盾出发：FCS-MPC 的开关集合是离散且有限的，真正需要模型完成的任务只是回答“27 个候选里，下一拍哪个最好”，而不是永久得到一套可解释的全局物理模型。参数辨识和 observer 之所以仍脆弱，是因为它们先假定模型结构正确，再修补参数或误差；LUT 又把历史压得过短，无法表达较复杂动态。

下一步自然会想到 DL：在每个工作点附近，用最近若干拍的 \(\Delta i\) 与 \(\Delta u\) 构造局部线性增量关系，让时变 pseudo-gradient 吸收非线性、参数漂移和结构变化。FFDL 同时保留输入、输出历史，窗口长度 \(n_u,n_y\) 可调，理论上比只用输入历史的 CFDL/PFDL 更能描述局部动态。[pdf:E04]（PDF 物理页 4，Section III-A，Eqs. (9)–(11)）

然后出现两个实现问题。第一，pseudo-gradient 必须每拍在线更新，因此估计器要足够轻；Adaline 本质上是单层线性神经元，用 measured increment 当监督信号，以 normalized least-mean-square 更新权重，符合这一需求。第二，即便负载电流不再用 \(R,L\) 预测，中点电压的传统式仍含 \(C_{dc}\)；于是作者不再预测电压变化的数值，而用中点电压和中点电流的符号判断哪类开关会把电压拉回，并用上界决定何时提高这一目标的优先级。[pdf:E05]（PDF 物理页 5，Eqs. (13)–(16) 与 Section III-C）[pdf:E06]（PDF 物理页 6，Eqs. (17)–(19)）

## § 4 — 核心 Intuition

核心 intuition 是：FCS-MPC 不必知道装置“是什么参数”，只要最近的输入输出增量足以说明装置“此刻怎样响应”，就能为有限候选开关做下一拍排序。Adaline 每拍把这种局部响应压进 pseudo-gradient；中点平衡则不求精确电容动态，只利用电压偏差与候选中点电流的方向关系。换言之，作者把“预测一个参数正确的全局模型”改成“持续刷新一个够用的局部动作—响应映射”。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Section III）[pdf:E06]（PDF 物理页 6，Section III-C/D）

## § 5 — 具体方法与完整 Pipeline

以论文的三相 3L-NPC 逆变器为例，一拍控制过程可重建为：

1. **采样并形成增量历史。** 采样 \(\alpha\beta\) 坐标下的负载电流、已施加的电压矢量以及上下电容电压。数据栈 \(\Delta H_\alpha,\Delta H_\beta\) 分别保留最近 \(n_y\) 个电流增量和最近 \(n_u\) 个控制输入增量；论文最终选 \(n_y=1,n_u=3\)。[pdf:E04]（PDF 物理页 4，Eqs. (9)–(10)）[pdf:E09]（PDF 物理页 9，Fig. 9 分析）
2. **用 Adaline 更新局部模型。** 网络输入是 \(\Delta H\)，权重就是 pseudo-gradient \(\Xi\)，输出是预测的电流增量。用上一拍真实测得的 \(\Delta i_g\) 与 \(\Xi^\top\Delta H\) 的误差更新 \(\Xi\)，并让 learning rate 随误差大小自适应变化。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Eqs. (11)–(12)）[pdf:E05]（PDF 物理页 5，Eqs. (13)–(16)）
3. **枚举电流候选。** 对 3L-NPC 的 27 个开关状态，把相应候选电压矢量代入数据栈的当前输入位置，用 FFDL 计算 \(i_{g\alpha,\beta}(k+1)\)，再以参考电流与预测电流的二范数平方作为 tracking cost。[pdf:E03]（PDF 物理页 3，Fig. 2）[pdf:E06]（PDF 物理页 6，Eqs. (18)–(19)）
4. **处理 neutral-point voltage。** 若 \(|v_n(k)|\le \bar v_n\)，沿用前作 [21] 的 capacitance-less 两阶段选择；若越过上界，则对 27 个候选计算 \(\mathrm{sign}(v_n)\mathrm{sign}(i_n)\)，筛出能把中点电压推回的候选，再在其中最小化电流 tracking cost。该逻辑用方向而非 \(C_{dc}\) 的精确数值决定平衡动作。[pdf:E05]（PDF 物理页 5，Fig. 4 与 Section III-C）[pdf:E06]（PDF 物理页 6，Eqs. (17)–(18)）
5. **施加最优开关并滚动。** 把选中的 \(S_{\mathrm{opt}}\) 送给逆变器；新测量进入 data stack，下一采样周期重新估计并枚举。Fig. 5 显示的依赖链是 data stack → parameter estimation → prediction → optimization → converter。[pdf:E05]（PDF 物理页 5，Fig. 5）

这里的 “parameterless” 要按作者语境理解为“不使用被控对象的 \(R,L,C\) 物理参数和传统多目标 weighting factor”，不是完全没有调参。\(n_y,n_u\)、Adaline 的 \(k_1,k_2\) 以及中点电压上界 \(\bar v_n\) 仍是设计量。论文未报告 FPGA 映射、并行枚举结构、fixed-point 字长、资源占用、单拍执行时间或 timing margin；实际执行平台是 DSP，不应把“结构简单”改写成“已证明适合 FPGA”。

## § 6 — 核心数学推导（无形式化数学则跳过）

先看传统模型为何依赖参数。对 RL 负载，前向 Euler 离散后有

\[
\Delta \mathbf i_{\alpha\beta}(k+1)
=-\frac{R_gT_s}{L_g}\mathbf i_{\alpha\beta}(k)
+\frac{T_s}{L_g}\mathbf u_{\alpha\beta}(k).
\]

中点电压定义为 \(v_n=(u_l-u_p)/2\)，理想开关下中点电流为

\[
i_n=|S_a|i_a+|S_b|i_b+|S_c|i_c,
\qquad
\Delta v_n(k+1)=\frac{T_s}{2C_{dc}}i_n(k).
\]

因此传统 FCS-MPC 的电流预测显式需要 \(R_g,L_g\)，电压预测显式需要 \(C_{dc}\)；其 cost function 还用 \(\theta_n\) 权衡电流误差和中点电压。[pdf:E03]（PDF 物理页 3，Eqs. (2)–(8)）

作者用 FFDL 增量关系替换第一组物理方程：

\[
\Delta i_{g\alpha}(k+1)=\Xi_\alpha(k)^\top\Delta H_\alpha(k),\qquad
\Delta i_{g\beta}(k+1)=\Xi_\beta(k)^\top\Delta H_\beta(k).
\]

\(\Delta H\) 由过去的 \(\Delta i\) 和 \(\Delta u\) 拼成，\(\Xi\) 是有界的时变 pseudo-gradient。它不是 \(R,L\) 的物理辨识值，而是局部输入输出增量关系的系数；非线性、参数时变和结构变化都被压缩到它随时间的更新中。[pdf:E04]（PDF 物理页 4，Eqs. (9)–(11)）

Adaline 的线性输出与监督误差分别为

\[
O(\Xi,\Delta H)=\sum_{i=1}^{n_y+n_u}\Xi_i\Delta H_i,\qquad
e_z=\Delta i_g-\Xi^\top\Delta H.
\]

论文没有使用普通固定步长 gradient descent，而采用 normalized LMS：

\[
\Xi(k)=\Xi(k-1)+\frac{\mu e_z\Delta H}{\Delta H^\top\Delta H},
\qquad
\mu=k_1\left(1-e^{-k_2e_z^2}\right).
\]

误差大时 \(\mu\) 增大以加快跟踪，接近收敛时 \(\mu\) 变小以降低稳态波动。这一解释是由 Eq. (16) 的单调关系作出的基于证据推断；论文正文只明确说明“大初值利于收敛、小值利于降低 steady-state error”。[pdf:E05]（PDF 物理页 5，Eqs. (13)–(16)）

对候选 \(u_j\)，一步预测写成

\[
i_{g\alpha}(k+1)=i_{g\alpha}(k)+\Xi_\alpha^\top\Delta H_\alpha|_{u_{j\alpha}(k)},
\]

\[
i_{g\beta}(k+1)=i_{g\beta}(k)+\Xi_\beta^\top\Delta H_\beta|_{u_{j\beta}(k)}.
\]

越界时 CVB 不再算 \(\Delta v_n=T_si_n/(2C_{dc})\)，而以

\[
J(S_{abc})=\mathrm{sign}(v_n(k))\,\mathrm{sign}(i_n(k))
\]

筛选中点电流方向，再最小化

\[
\left\|\mathbf i_{\alpha\beta}^{*}(k+1)-\mathbf i_{\alpha\beta}(k+1)\right\|_2^2.
\]

这样移除了 \(C_{dc}\) 与 \(\theta_n\)，代价是中点电压只得到阈值意义下的方向性调节，而不是论文给出的一套精确闭环收敛界。[pdf:E06]（PDF 物理页 6，Eqs. (17)–(19)）

## § 7 — 实验设计与结论

**问题 1：正常参数下，数据模型会不会牺牲基本稳态质量？ →** 作者在 3L-NPC 仿真中比较 conventional FCS-MPC、ESO-based MPC、前作 data-driven MPC 与本文方法。仿真参数为 \(R_g=7.5\,\Omega\)、\(L_g=10\,\mathrm{mH}\)、\(C_{dc}=2700\,\mu\mathrm F\)、\(T_s=100\,\mu\mathrm s\)、\(V_{dc}=300\,\mathrm V\)、\(f=50\,\mathrm{Hz}\)；Fig. 6 标出的 phase-a current THD 依次为 2.41%、2.25%、2.44% 和 2.24%。→ **答案：** 本文方法在该工况下与三类基线相当，没有因数据预测明显损失稳态电流质量或中点平衡。[pdf:E05]（PDF 物理页 5，Table I）[pdf:E06]（PDF 物理页 6，Fig. 6）

**问题 2：参数失配时是否真的更稳健？ →** Fig. 7 把电感设为名义值的 50%；图中 conventional mismatch、conventional matched、ESO、前作 data-driven 与本文方法的 THD 标签分别为 6.45%、5.02%、4.77%、4.51% 和 4.09%。Fig. 8 又扫描电感偏差 \(-60\%\) 到 0%、电阻偏差 \(-60\%\) 到 \(+40\%\)。→ **答案：** 在作者扫描的 RL 参数范围内，本文方法的平均 THD 更低，支持“对 \(R,L\) 失配不敏感”这一有限范围 claim；这不是对任意未建模动态的鲁棒性证明。[pdf:E07]（PDF 物理页 7，Figs. 7–8）[pdf:E08]（PDF 物理页 8，Fig. 8 结果文字）

**问题 3：历史窗口怎么选？ →** 作者令 \(n_y,n_u\) 各自从 1 到 5，比较 average THD 与 tracking error。→ **答案：** \((1,1)\) 最差，任一窗口增加都会改善，超过 3 后收益趋于饱和；最终选 \(n_y=1,n_u=3\) 作为 tracking 与计算成本的折中。论文展示了 sensitivity map，但未给执行时间随窗口增长的实测值。[pdf:E07]（PDF 物理页 7，Fig. 9）[pdf:E09]（PDF 物理页 9，Fig. 9 结果文字）

**问题 4：无电容参数 CVB 能否限制中点波动？ →** 仿真让参考电流幅值从 12 A 阶跃到 20 A，比较传统 weighting-factor、前作 capacitance-less CVB 与本文有上界方法。→ **答案：** 前两者的电容电压波动随电流上升而增大，本文方法把波动限制在阈值附近；实验 Fig. 14 也显示本文方法相对前作具有更小 ripple。图给出波形和刻度，但正文没有报告统一的 RMS/peak-to-peak 数值统计。[pdf:E07]（PDF 物理页 7，Fig. 10）[pdf:E08]（PDF 物理页 8，Fig. 14）[pdf:E09]（PDF 物理页 9，CVB 分析）

**问题 5：真实硬件上是否保持稳态、失配与瞬态性能？ →** 原型采用 Vincotech 10-FZ07NIA050SM-P925F58 IGBT 模块，控制器运行于含 TMS320C28377D DSP 的 RTU-BOX 206；实验参数为 \(R_g=3\,\Omega\)、\(L_g=10\,\mathrm{mH}\)、\(C_{dc}=2700\,\mu\mathrm F\)、\(T_s=100\,\mu\mathrm s\)、\(V_{dc}=120\,\mathrm V\)、\(f=50\,\mathrm{Hz}\)。作者比较理想参数与电感降至 \(4.4\,\mathrm{mH}\) 的波形，并做参考频率、幅值阶跃。→ **答案：** 理想参数下本文方法与 ESO 方法相近；电感失配时 conventional FCS-MPC 明显劣化，本文方法仍保持较好电流波形；频率与幅值阶跃显示其保留了快速 transient response。[pdf:E05]（PDF 物理页 5，Table I）[pdf:E07]（PDF 物理页 7，Fig. 11）[pdf:E08]（PDF 物理页 8，Figs. 12–14）[pdf:E09]（PDF 物理页 9，实验分析与 Conclusion）

验证边界很重要：论文没有报告统计重复次数、置信区间、测量噪声 sweep、dead time/器件非理想的独立消融、计算耗时、CPU load、FPGA resource、fixed-point error 或超过单台 RL-load 3L-NPC 的硬件验证。因此“remarkable robustness”应收窄为“在给定原型和所测 \(R,L\) 失配下表现稳健”。

## § 8 — Take-aways

**5 句话：** ① 论文用 FFDL 把 3L-NPC 的下一拍电流预测改写为历史 I/O 增量与时变 pseudo-gradient 的内积。② Adaline 通过 normalized LMS 在线更新 pseudo-gradient，避免把 \(R_g,L_g\) 写入预测器。③ 中点电压越界时，控制器利用 \(v_n\) 与候选 \(i_n\) 的符号关系选方向，再最小化电流误差，从而不使用 \(C_{dc}\) 和传统 weighting factor。④ 在作者给定的仿真与 DSP 原型中，本文方法保持了稳态和瞬态性能，并在 \(R,L\) 失配下优于所比基线。⑤ 它证明的是特定 3L-NPC/RL 场景中的可行性，不是 FPGA 实现、任意未建模动态或严格稳定性的证明。

**3 句话：** 论文用可在线更新的局部数据模型取代固定物理预测模型。电流预测靠 Adaline 学到的增量映射，中点平衡靠符号和阈值逻辑。实验支持有限工况下的参数鲁棒性，但实现时序、数值格式与分布外运行仍未闭合。

**1 句话：** 这是把 FCS-MPC 从“依赖准确参数的候选预测”推进到“依赖近期 I/O 的候选排序”，但其成败仍取决于近期数据是否足以辨认当前动作—响应关系。

## § 9 — 最脆弱的假设

最脆弱的假设是：**固定长度的近期增量历史对当前工作点具有足够 excitation 与辨识信息，使一个有界、缓慢可跟踪的 pseudo-gradient 能同时正确预测所有候选开关的下一拍响应。** 这比“Adaline 能拟合线性函数”更关键，因为 FCS-MPC 需要的是 27 个反事实候选的正确排序；历史只记录实际施加过的动作，未必覆盖当前准备比较的候选。

该假设可能在稳态小增量、某些电压矢量长期不用、测量量化使 \(\Delta H\) 接近零、器件 dead time、磁饱和、反电动势突变或负载结构突然改变时失效。此时 normalized LMS 的分母 \(\Delta H^\top\Delta H\) 也会变得敏感，而同一段有限历史可能对应两个未来响应不同的真实对象。论文给出的正面证据是：增大 \(n_u,n_y\) 可改善 tracking，且参数扫描和电感骤降实验仍工作；缺失的证据是历史数据秩/condition number、候选级 one-step prediction error、噪声与低 excitation 测试，以及对 pseudo-gradient 有界性和闭环稳定性的实验或理论保证。[pdf:E04]（PDF 物理页 4，Eqs. (9)–(12)）[pdf:E05]（PDF 物理页 5，Eq. (15)）[pdf:E07]（PDF 物理页 7，Figs. 7–9）[pdf:E08]（PDF 物理页 8，参数失配实验）

## § 10 — 最小复现实验

一周内最值得复现的不是整套硬件，而是“只用 I/O 数据的一步候选排序在参数失配下是否比固定模型可靠”。

- **数据：** 在 Matlab/Simulink 或同等离散仿真中搭建论文的 3L-NPC + RL 对象，采用 Table I 的仿真参数与 \(T_s=100\,\mu s\)。记录每拍 \(i_{\alpha\beta}\)、实际施加的 \(u_{\alpha\beta}\)、27 个候选下的仿真真实下一拍电流和 \(v_n\)。控制器侧严格禁止读取真实 \(R,L,C\)。
- **实现：** 只实现 FFDL \(n_y=1,n_u=3\)、Adaline Eqs. (13)–(16)、Eq. (19) 的 27 候选预测，并以 conventional FCS-MPC 作为基线。CVB 可先保留理想平衡，把一周资源集中在核心数据预测 claim。
- **工况：** 先用名义 \(L=10\,\mathrm{mH}\) 跑到稳态，再无通知地切到 \(L=5\,\mathrm{mH}\)，并追加论文硬件所用 \(4.4\,\mathrm{mH}\)；每个工况至少用不同初相位重复若干次。
- **测量：** 记录 phase-current THD、RMS tracking error、所有 27 候选的 one-step prediction RMSE，以及“预测最优开关与仿真真实最优开关一致率”。后一指标能把最终波形改善与候选排序机制直接连接起来。
- **支持标准：** 参数突变后本文方法的 tracking/THD 劣化小于 conventional，且候选排序一致率短暂下降后恢复；**反驳标准：** 它与固定模型同样劣化、恢复慢于一个基波周期，或必须读取真实参数才能达到论文趋势。

所有目标参数与对照范围均来自论文；重复次数和判据阈值是复现实验设计者应在运行前预注册的新增约束，不是作者报告的事实。[pdf:E05]（PDF 物理页 5，Table I）[pdf:E06]（PDF 物理页 6，Eq. (19)）[pdf:E07]（PDF 物理页 7，Figs. 7–9）[pdf:E09]（PDF 物理页 9，硬件失配设置）

## § 11 — 最强反例设计

最强反例不是再把 \(L\) 改得更大，而是制造**历史上不可辨识、候选上必须外推**的情形。先把调制度和参考轨迹设成使控制器长期只使用少数小矢量的稳态工况，让 \(\Delta H\) 低秩；随后在不改变最近可观测历史的前提下切换到两种内部动态之一，例如“线性 RL”与“含饱和电感及 dead-time 电压误差”的对象。紧接着给一个大幅参考阶跃，迫使控制器在此前未充分激励的大/中矢量之间选择。

对每拍保存 27 个候选的真实下一拍结果。如果两种对象产生近似相同的 \(\Delta H\)，Adaline 因而给出近似相同的预测排序，但真实最优开关不同，就直接击中了方法的 information limit：不是 learning rate 没调好，而是有限历史根本不能决定反事实动作。若本文控制器在该条件下连续选错开关、THD 或中点偏差超过 conventional/ESO，而论文式窗口加长仍不能恢复，则“仅靠近期 I/O 即可规避模型误差”的广义解释被反驳；若它能检测低 excitation、主动恢复信息并保持排序，则反例失败。论文没有做这类候选级、低 excitation 或对象别名测试。[pdf:E04]（PDF 物理页 4，FFDL 历史结构）[pdf:E07]（PDF 物理页 7，现有参数扫描范围）[pdf:E08]（PDF 物理页 8，现有硬件波形范围）

## § 12 — Follow-up Research Idea

**候选想法：把 data-enabled FCS-MPC 从“点预测所有候选”重定义为“只在数据足以证明候选排序时决策”。** 这不是再接一个更大的 neural network，而是把研究目标从拟合系统动态改成验证 decision identifiability：对每个开关候选输出下一拍误差的可校准集合或上下界；只有当某候选在不确定区间下仍稳胜其他候选时才施加，否则触发受约束的主动激励或安全 fallback。

（a）驱动需求是第 9 节的不可辨识风险：当前 point pseudo-gradient 无法告诉控制器“我没有见过足够相似的动作”。（b）在电力电子领域，若能同时给出 \(100\,\mu s\) 级实时实现、硬件保护边界和跨参数/非线性验证，其价值在于把“经验鲁棒”变成可观测的决策可信度。（c）可借鉴 set-membership identification、online conformal prediction 与 safe exploration，但输出对象应是有限开关的 cost ranking，而不是通用回归置信区间。（d）第一个证伪实验就是第 11 节的双对象同历史测试：若区间仍错误地给出高置信唯一最优开关，或主动激励在一个采样周期预算内不可实现，想法即失败。（e）与本文的实质区别是，本文用单一 \(\Xi\) 始终给 27 个候选点预测并取最小值；候选方案允许“当前数据不足以排序”成为一等控制状态，并把获取可辨识信息纳入控制目标。

该方向是基于本论文脆弱假设的候选判断，尚未对所有相邻工作完成系统检索，因此不声称 novelty。论文自身只证明了 FFDL + Adaline 点估计和阈值 CVB 在给定 3L-NPC 原型上的效果。[pdf:E05]（PDF 物理页 5，Fig. 5）[pdf:E06]（PDF 物理页 6，Eq. (19)）[pdf:E09]（PDF 物理页 9，Conclusion）
