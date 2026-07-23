# Suppression of Chattering in the Real-Time Simulation of the Power Converter

- 作者：Chen Liu, Hao Bai, Rui Ma, Yaoqiang Wang, Fei Gao
- 出处：IEEE Transactions on Power Electronics
- 年份：2021
- DOI：10.1109/TPEL.2021.3069099
- Zotero key：E87DFKRD

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体、但会直接破坏实时仿真可信度的问题：轻载时，功率变换器会进入 discontinuous conduction mode（DCM，电感或支路电流在一个开关周期内真正降到零并保持一段时间）。二极管的自然换流由端口电流或电压的符号决定，而 FPGA 实时仿真必须使用固定步长；因此，计算电流越过零点后往往不会恰好落在零上，模型会在两个导通拓扑之间高速来回切换，形成 chattering。作者把 chattering 描述为零点附近的高频振荡，并指出亚 500 ns 步长对 10–200 kHz 开关频率的变换器很重要；论文的目标是在不牺牲硬实时固定步长的前提下处理这一轻载失真。[pdf:E01](_evidence/E01-p001-abstract-fig01.png)（PDF 物理页 1，Abstract、Section I、Fig. 1）

物理上，问题不只是“波形有一点毛刺”。错误的电流符号会让下一步选错二极管导通状态，错误拓扑又反过来把电流推向另一侧，因而形成自激式的数值切换。作者用轻载四象限变换器（4-QC）说明：Forward Euler（FE）在 100 ns 步长下，无论 ideal switch function（ISF）还是 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 模型，零点附近都出现明显振荡。[pdf:E02](_evidence/E02-p002-eq01-related-work.png)（PDF 物理页 2，Fig. 2、Eq. (1)）

工程价值在于：如果这个边界行为不能稳定处理，重载时看似正确的 FPGA 模型在轻载、续流结束或二极管阻断时可能突然失真；而 HiL 中控制器看到的是这个数值模型给出的反馈。论文因此把“在固定计算预算内正确处理 DCM”当成与求解速度同等重要的问题。

## § 2 — 前人工作与不足

论文列出两类直接相关方案。第一类是迭代法：在一个时间步内反复更新，直到开关端电流与电压的符号满足一致条件。它能减小 chattering 误差，但符号并不保证在单步内收敛到一致，硬实时系统必须设最大迭代次数以避免超时；迭代本身也拉长关键路径。第二类是 iteration-free 的高阻态方法：在 MMC blocked mode 的过零处强制子模块进入一次 high-impedance 状态。作者认为它的电流边界来自特定 MMC 子模块拓扑，阈值不够小且泛化性有限；高阻态还需要额外方程，不能保持全系统统一公式。[pdf:E02](_evidence/E02-p002-eq01-related-work.png)（PDF 物理页 2，Section I-B）

论文还把 Ron/Roff、associated discrete circuit（ADC）与 ISF 列为常用开关建模类型，但强调三者都绕不开自然换流器件的状态判定：门极可直接给出受控开关状态，二极管状态却必须依赖端口量的符号。[pdf:E01](_evidence/E01-p001-abstract-fig01.png)（PDF 物理页 1，Section I）因此，作者要改的不是某一种器件等效电路，而是固定步长下的过零判定与状态更新机制。

## § 3 — 重建作者的思考路径

下面是基于论文背景证据的逆向重建，不是作者逐句陈述的研究历史。

第一步，从 4-QC 的分段动力学出发：正电流、零电流、负电流分别对应两个导通模式与一个 blocked mode；不迭代时，\(t_{n+1}\) 的模式只能用上一时刻 \(i(t_n)\) 决定。固定步长跨过零点后，电流通常从正值直接变成负值，下一步便切到相反的导通方程，又把电流推回正侧，于是产生符号翻转环。[pdf:E02](_evidence/E02-p002-eq01-related-work.png)（PDF 物理页 2，Eq. (1) 及其后正文）

第二步，既然硬实时不允许像离线 variable-step solver 那样不断缩步，也不希望使用不定次数迭代，就需要在当前步预测“下一步是否会跨过过零带”。作者已有 predictor-corrector（PC）结构：预测支路与校正支路用历史状态分别计算，并且两条支路可以并行。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (7)）

第三步，用当前步可得的 guard function \(g\) 与预测 guard \(g^p\) 判断两者是否越过 \(\pm\alpha\) 且符号相反；这等价于在不求精确事件时刻的情况下识别 chattering 起点。最后，与其增加 blocked-mode 方程，不如把已经检测到的振荡状态限制到很小的 \(\pm\beta\)，并用一个短状态机保证退出 chattering 时回到正确一侧。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Definition 2.1、Eq. (8)–(11)、Table I）

## § 4 — 核心 Intuition

核心 intuition 是：不要等待离散电流“碰巧等于零”，而要同时看当前校正值和一步预测值；如果两者已经跨过零点带，就提前把它识别为 chattering。随后不显式求 blocked-mode，而是在两个原有 CCM 导通方程之间保持一致的更新，并把零点附近的数值振荡限制在足够小的 \(\pm\beta\)。[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Section II-B/C、Fig. 4）

这意味着论文所谓“suppression”主要是幅值抑制，而不是让开关状态完全停止来回切换；作者明确说 chattering 仍然存在，只是其数值影响被限制到可忽略范围。[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Section II-B）

## § 5 — 具体方法与完整 Pipeline

以论文的 series load resonant（SLR）converter 为例，完整 pipeline 如下。

1. **输入与历史状态。** 每个 100 ns FPGA tick 读取 PWM 与 dead-time 信号，以及上一步保存的谐振电流、电容电压等状态。论文的 SLR 使用 10 kHz 开环开关频率和 500 ns dead-time；开环控制用于把误差尽量限定在模型而不是控制器。[pdf:E05](_evidence/E05-p005-fig06-07-eq12-15.png)（PDF 物理页 5，Section III、Fig. 7）
2. **并行预测与校正。** prediction process 根据 \(x_{n-1}\) 预测 \(x^p_{n+1}\)，correction process 用预测状态计算 \(x_n\)。两条数据通路相互独立，可在 FPGA 上并行执行。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (7)）；[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Fig. 4）
3. **开关与网络求解。** 对 ISF 模型，预测电流与校正电流分别决定 prediction/correction 两套 switch function，再计算节点电压、支路电流和状态更新；对 Ron/Roff 模型，作者用 modified nodal analysis，并把所有可能的逆矩阵预计算后存入 FPGA look-up table，运行时按门极和电流符号选择。[pdf:E05](_evidence/E05-p005-fig06-07-eq12-15.png)（PDF 物理页 5，Eq. (12)–(15)）；[pdf:E07](_evidence/E07-p007-table02-03-eq16-18.png)（PDF 物理页 7，Tables II–III、Eq. (16)–(18)）
4. **过零检测。** zero-regulation unit 同时检查 \(g(t_{n+1},x)\) 与 \(g^p(t_{n+1},x)\)。若它们越过 \(\pm\alpha\) 且符号相反，设置 `flag=1`，认定当前点是 chattering 起点。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Definition 2.1、Eq. (11)）
5. **幅值规整与退出。** Table I 的状态规则把预测值与校正值赋成相反符号的 \(\pm\beta\)，用 `sgn` 记住连续 chattering 点；检测到离开区间时再赋为 \(\pm\alpha\)，直到后续点不再满足 chattering 条件。其目的不是求出连续系统的精确过零时刻，而是让离散拓扑选择不会把零点误差放大。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Table I）；[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Table I 后续解释）
6. **输出。** 当步状态写回寄存器，同时向外输出模拟量和数字量。论文在 NI PXIe 平台的 single-cycle time-loop（SCTL）中把上述过程限制在一个 FPGA clock tick 内。[pdf:E05](_evidence/E05-p005-fig06-07-eq12-15.png)（PDF 物理页 5，Fig. 7 与页末正文）；[pdf:E06](_evidence/E06-p006-fig08-11-results.png)（PDF 物理页 6，Fig. 8）

论文没有报告定点 word length、量化策略、流水线级数、时钟裕量或跨时钟域处理；这些不能从资源图反推。

## § 6 — 核心数学推导

先看物理对象。\(x\) 是状态向量，\(f_1\) 与 \(f_3\) 是零点两侧的 CCM 导通动力学，\(f_2\) 是 blocked-mode 动力学，\(g(t,x)\) 是决定开关边界的 guard function。连续系统在 \(g=0\) 处换模；固定步长实现把它放宽为 \(|g|\le\alpha\) 的邻域。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (4)）

PC 更新为

\[
x^p_{n+1}=x_{n-1}+2h\,f(t_{n-1},x_{n-1}),\qquad
x_n=x_{n-1}+h\,f(t_n,x^p_n).
\]

这里 \(h\) 是固定步长。第一式用跨两步的历史斜率预测下一点，第二式用预测状态修正当前点；工程意义是用两条可并行的计算支路换取一个“看见下一步符号”的能力。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (7)）

若 guard function 对状态呈线性形式 \(g(t_{n+1},x)=Cx_n+D\)，则

\[
g(t_{n+2},x)=Cx_{n+1}+D\approx Cx^p_{n+1}+D
=g^p(t_{n+1},x).
\]

因此，当前时刻即可同时得到真实校正分支的 \(g(t_{n+1},x)\) 与预测分支的 \(g^p(t_{n+1},x)\)。当 \(g^p>\alpha\) 且 \(g<-\alpha\)，或 \(g^p<-\alpha\) 且 \(g>\alpha\) 时，作者定义该点为 chattering 起点。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (8)、Definition 2.1）

在实际更新中，校正支路按 \(g^p\) 的符号选择 \(f_1\) 或 \(f_3\)，预测支路按 \(g\) 的符号选择 \(f_1\) 或 \(f_3\)；检测到 chattering 后，Table I 再把两支路的状态限制为相反符号的 \(\pm\beta\)。关键点是更新公式只保留 \(f_1,f_3\)，不再调用 \(f_2\)，从而用同一组 CCM 方程近似 blocked-mode。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (9)–(11)、Table I）；[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Section II-B）

这个推导依赖两项重要近似：\(x_{n+1}\approx x^p_{n+1}\)，以及用于预判的 guard function 在相关区间可由 \(Cx+D\) 表示。论文给出了算法构造与实验结果，但没有给出全局稳定性证明、误差上界或 \(\alpha,\beta,h\) 之间的形式化选取条件。

## § 7 — 实验设计与结论

**问题 1：ZR 是否真的缩小 4-QC 的零点误差？** 作者在 NI PXIe-7975R 上以 100 ns FE 模型先复现 ISF 与 Ron/Roff 两类模型的 chattering，再加入 ZR。4-QC 中取 \(\beta=10^{-4}\,\mathrm{A}\)、\(\alpha=10^{-3}\,\mathrm{A}\) 后，作者报告 chattering zone 只剩 \(\pm10^{-4}\,\mathrm{A}\)；以 MATLAB/Simulink 为参考，ISF 的 \(U_{cd}\) 误差由最高 5% 降到低于 0.2%，Ron/Roff 的误差由 20% 降到 0.3%。[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Fig. 5 及正文）；[pdf:E05](_evidence/E05-p005-fig06-07-eq12-15.png)（PDF 物理页 5，Fig. 6 及其后正文）

**问题 2：在更复杂的 SLR converter 上，ZR 是否保持实时速度？** 实验平台为 NI 7975R（Kintex-7 XC7K410T）与 NI 5741，SLR 以 10 kHz 开环控制、500 ns dead-time 运行；比较 FE、五次迭代的 Backward Euler（BE）和 ZR，并以 MATLAB/Simulink 为参考。[pdf:E05](_evidence/E05-p005-fig06-07-eq12-15.png)（PDF 物理页 5，Section III、Fig. 7）ISF 实现中，FE 与 ZR 均达到 100 ns，五次迭代为 500 ns；ZR 的 DSP48 占用为 2.6%，FE 为 1.3%。[pdf:E06](_evidence/E06-p006-fig08-11-results.png)（PDF 物理页 6，Fig. 9 及正文）

**问题 3：轻载加剧时，ZR 是否比 FE 与迭代法更接近参考模型？** 作者把负载设为 \(R_o=1,20,80\,\Omega\)。在 1 \(\Omega\) 时三种方法差异很小；20 \(\Omega\) 开始进入断续电流；80 \(\Omega\) 时 FE 与五次迭代在电流接近零处出现不可忽略振荡及电容电压偏差，而 ZR 波形仍与参考模型高度一致。[pdf:E06](_evidence/E06-p006-fig08-11-results.png)（PDF 物理页 6，Figs. 10–11 及正文）这是作者的图形与文字结论；论文没有给出这三组波形的统一 RMSE 或最大误差表，因此不应从曲线估读额外精确数值。

**问题 4：方法是否只适用于 ISF？** 作者又在 Ron/Roff 模型中用预计算逆矩阵的 modified nodal analysis 实现同一 ZR 规则。FE 与 ZR 均满足 100 ns，五次迭代为 500 ns；ZR 使用 4.8% DSP48，FE 为 2.4%。在 \(R_o=80\,\Omega\) 的轻载工况，作者同样报告 ZR 保持与参考模型的一致，而另两种方法误差明显。[pdf:E07](_evidence/E07-p007-table02-03-eq16-18.png)（PDF 物理页 7，Fig. 12–13 及正文）；[pdf:E08](_evidence/E08-p008-fig14-conclusion.png)（PDF 物理页 8，Fig. 14、Section III-C/IV）

证据边界也很清楚：这是两种变换器、两类开关模型、单一 FPGA 平台、主要在 100 ns 步长下的验证。论文没有报告 controller-HIL 闭环扰动、器件寄生参数扫描、定点位宽敏感性、长时间能量漂移或多器件同时换流压力测试，不能把“在所测案例有效”外推为所有功率电子拓扑的普遍保证。

## § 8 — Take-aways

**5 句话**

1. 固定步长跨过 DCM 零点时，上一时刻符号驱动的拓扑选择会把微小过零误差放大成来回换模。
2. ZR 用并行 predictor-corrector 同时获得当前 guard 与预测 guard，在不迭代求事件时刻的情况下识别 chattering 起点。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (7)–(11)）
3. 它保留两侧 CCM 方程、去掉显式 blocked-mode 方程，并把检测到的振荡状态规整到 \(\pm\beta\)。[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Section II-B/C）
4. 在论文的 ISF 与 Ron/Roff FPGA 实现中，ZR 保持 100 ns 步长，但 DSP48 约为 FE 的两倍。[pdf:E06](_evidence/E06-p006-fig08-11-results.png)（PDF 物理页 6，Fig. 9）；[pdf:E07](_evidence/E07-p007-table02-03-eq16-18.png)（PDF 物理页 7，Fig. 12）
5. 最重要的限定是：作者证明了若干案例中的幅值抑制与波形改善，没有证明任意拓扑、阈值和固定步长下的稳定性。

**3 句话**

1. 这项工作的真正贡献是把过零预判、幅值规整和 FPGA 并行执行组合成确定时延流程。
2. 实验显示它在轻载 DCM 下优于普通 FE 和固定五次迭代，同时仍满足 100 ns SCTL。[pdf:E08](_evidence/E08-p008-fig14-conclusion.png)（PDF 物理页 8，Section IV）
3. 代价是额外预测通路、约两倍 DSP48，以及对 \(\alpha,\beta\) 与 guard 结构的经验性依赖。

**1 句话**

ZR 用“一步预测发现跨零 + 小幅值规整”换取轻载固定步长仿真的可用精度与确定执行时间。

## § 9 — 最脆弱的假设

最脆弱的假设是：**当前 guard 与一步预测 guard 的异号关系足以可靠识别真正的 chattering，而且固定 \(\alpha,\beta\) 对被模拟电路始终足够小，不会改变有意义的物理动态。**

论文对这个假设的支持来自两个层面。方法层面，Eq. (8) 用 \(x_{n+1}\approx x^p_{n+1}\) 把下一步 guard 提前到当前步；实验层面，4-QC 取 \(\alpha=10^{-3}\,\mathrm{A}\)、\(\beta=10^{-4}\,\mathrm{A}\)，SLR 在三档负载和两类开关模型下都得到更接近参考模型的波形。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (8)、Definition 2.1）；[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，Fig. 5）

但论文没有给出阈值随步长、状态尺度、量化噪声或电路刚性变化的选取律。基于证据的推断是：若一个步长内发生多个耦合器件的近同时换流，或预测误差本身大于过零带，异号可能来自正常快速动态而非 chattering；此时强制 \(\pm\beta\) 可能删除真实的小电流区间、改变能量交换，甚至选错下一拓扑。这个失败会直接动摇“统一公式仍保持物理正确性”的核心贡献。

## § 10 — 最小复现实验

一周内最小复现应选论文的 4-QC，而不是完整 SLR FPGA 工程。用 Fig. 1 的电路与参数建立三个模型：高精度 variable-step 参考、100 ns FE 基线、100 ns FE 加 ZR；ISF 先做主实验，Ron/Roff 作为一天内可完成的交叉检查。[pdf:E01](_evidence/E01-p001-abstract-fig01.png)（PDF 物理页 1，Fig. 1）；[pdf:E02](_evidence/E02-p002-eq01-related-work.png)（PDF 物理页 2，Eq. (1)、Fig. 2）

实现只需保存 \(x_{n-1},x^p_n\)，按 Eq. (7)–(11) 计算两条支路，再实现 Table I 的 `flag/sgn` 规则。使用论文报告的 \(\alpha=10^{-3}\,\mathrm{A}\)、\(\beta=10^{-4}\,\mathrm{A}\)，扫描轻载程度与初始相位。[pdf:E03](_evidence/E03-p003-eq04-11-table01.png)（PDF 物理页 3，Eq. (7)–(11)、Table I）；[pdf:E04](_evidence/E04-p004-fig04-05-zr-rules.png)（PDF 物理页 4，参数说明）

测量三项：零点附近电流峰峰值、\(U_{cd}\) 相对参考的最大绝对误差、每步最坏执行时间。若 ZR 把零点振荡稳定限制到论文所述 \(\pm10^{-4}\,\mathrm{A}\) 量级、显著降低 \(U_{cd}\) 误差且不增加步长期限，就支持核心 claim；若需要频繁调阈值才能避免错误钳位，或误差下降来自把真实小电流直接截断，则反驳其稳健性。硬件不可用时，前两项仍可验证数值机制，但不能声称复现了 100 ns FPGA deadline。

## § 11 — 最强反例设计

最强反例不是简单换一种拓扑，而是构造**一个 100 ns 步长内有两个或更多耦合二极管近同时过零**的工况，并让其中一个小电流分量代表真实能量回流而非数值噪声。可在带寄生电容、漏感和轻载谐振的桥式变换器中扫描初相位，使两个 guard 在同一步内先后换号；再叠加与定点量化相当的小扰动。

用远小于 100 ns 的事件定位解作为参考，比较 ZR、FE 与有界迭代法的拓扑序列、每次换流时刻误差、单周期能量误差、长时间漂移和最坏执行时间。若 ZR 把真实回流电流误判为 chattering 并钳到 \(\pm\beta\)，即使输出波形肉眼更平滑，也说明它不是在恢复正确 blocked-mode，而是在以阈值重写物理过程。这个反例直接攻击第 9 节的核心假设，比单纯展示“某个负载下误差更大”更有解释力。

## § 12 — Follow-up Research Idea

**候选方向，不声称 novelty：把经验阈值规整改成可证明误差界的定时事件投影器。** 当前未对相关工作做充分检索，因此这里只给证据约束的研究问题，不宣称它尚未被提出。

未满足的需求是：ZR 给出了确定时延，却没有说明 \(\alpha,\beta\) 如何随步长、量化和拓扑耦合变化，也无法区分“真实的小电流能量交换”与“离散换模振荡”。候选方法可借鉴 hybrid systems 的 complementarity formulation：把二极管约束写成电流非负、阻断电压非负及二者互补，并在每步生成一个有界、固定迭代次数的局部投影；离线阶段针对拓扑与定点位宽求出可认证误差界，在线 FPGA 只执行预编译的小规模投影与分支。

它与本文的实质区别不是多加一个滤波模块，而是把研究目标从“把振荡幅值限制到人为 \(\beta\)”改为“在固定 deadline 下保持二极管互补约束，并给出状态误差上界”。对电力电子实时仿真而言，高影响证据应同时包括严格数值条件、真实 FPGA 最坏时延、跨拓扑验证与 controller-HIL 闭环结果，而不只是更平滑的离线波形。

第一个证伪实验就是第 11 节的多器件近同时换流压力测试：若投影器无法在 100 ns 内完成，或其能量/拓扑误差不优于 ZR，则该方向不成立。若能通过，再扩展到位宽、寄生参数与闭环控制器扫描；在完成系统性相关工作检索前，不判断其研究新颖性。
