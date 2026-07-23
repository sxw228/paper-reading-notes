# Real-Time Simulation of Power Electronic Systems Based on Predictive Behavior

- Zotero key：`YRXGNX4M`
- 固定语料顺序：`67`
- 作者：Chen Liu, Hao Bai, Shengrong Zhuo, Xinyue Zhang, Rui Ma, Fei Gao
- 出处：IEEE Transactions on Industrial Electronics, 67(9), 2020
- DOI：`10.1109/TIE.2019.2941135`
- 阅读边界：以源 PDF 全文为唯一事实源；下文的解释、批评、复现实验和研究方向均与“论文原文明确声称”分开标记。没有执行足以支持 novelty 判断的外部相关工作检索。

## § 1 — 研究问题与重要性

论文要解决的不是“FPGA 能否做实时仿真”，而是更具体的时序瓶颈：传统 FPGA power-electronics solver 通常要先更新开关状态和网络矩阵，再计算电感电流、电容电压等 circuit-element state。拓扑一变，上一时刻的节点电压和支路电流不能直接当作当前值，因此这条数据依赖链天然串行。作者试图在保留连续 IGBT 开关暂态和较高阶积分精度的同时，把 switch-network block 与 circuit-element block 改造成同一时步内可并行执行的两条路径。[pdf:E02]

这件事重要，是因为 HiL（hardware-in-the-loop）中的真实控制器必须等待实时模型给出反馈；模型计算时间就是闭环中的额外延迟。论文给出的应用背景是高功率电力电子系统常见开关频率约为 10–200 kHz，而 FPGA HiL 通常以低于 500 ns 的步长作为能力目标。作者最终报告在 NI FlexRIO 上达到 25 ns 固定步长，因此追求的不只是“仿得快”，而是把模型响应延迟压到足以观察开关暂态、并给高频控制器提供及时反馈的量级。[pdf:E01]

## § 2 — 前人工作与不足

论文把既有并行化分为两路。第一路是 CPU/FPGA 或 DSP/FPGA 的 multi-rate partition：不同子系统放到不同计算设备。第二路是在 FPGA 内拆分网络，例如 network tearing 配合 \(R_\mathrm{on}/R_\mathrm{off}\) 二值开关、ideal-switch latency insertion、带并联寄生电容的 binary-resistance model，或对矩阵求逆过程做并行化。文中列举的代表性结果包括 50 ns、75 ns 和 36 ns 最小步长；这些结果说明 FPGA 并行本身并非新命题，但共同的 solver 结构仍包含开关更新、网络方程和状态求解之间的顺序依赖。[pdf:E02]

对 IGBT 细节模型，论文指出 Hefer 或 Hammerstein 一类模型包含除法、开方等高延迟运算；固定开关时间区间的模型虽曾达到 12.5 ns，却只在特定电流、电压下准确；lookup table 方案也可达到 12.5 ns，但需要大量 double-pulse test 数据。作者因此没有追求完整器件物理，而是选择足以产生连续暂态并服务于“预测下一时步”的简化 piecewise IGBT model。[pdf:E02]

对 ODE 积分，forward Euler（FE）最快但精度较低，trapezoidal（TR）和 backward Euler（BE）精度、稳定性更好，却通常要以串行固定步迭代求解。论文的目标是得到一套具有 FE 级计算时延、但 corrector 精度更高、且适合 FPGA 组合并行的积分结构。[pdf:E03]

这里的“不足”应精确理解为：论文没有证明以前的方法不能继续缩短步长；它声称的是现有结构仍有一段可消除的跨模块串行依赖，而详细器件模型与高阶积分又会增加关键路径。

## § 3 — 重建作者的思考路径

以下是基于论文背景与方法组织重建的推断，不是作者逐字陈述。

第一步，研究者会发现真正卡住时钟的不是单个乘加，而是“先判断开关，再解电路状态”的依赖顺序。若只把矩阵乘法做得更快，整个 step 仍然要等前一模块完成。[pdf:E02]

第二步，他们需要一个能提前暴露接口量的模型。连续的 piecewise IGBT 暂态可由当前门极信号、支路电流、直流电压和若干线性斜率参数，直接外推 \(t+2h\) 的 \(I_c\) 与 \(V_{ce}\)；同样，predictor-corrector 积分也能在求 \(t+h\) corrector 时顺手算出 \(t+2h\) predictor。[pdf:E03] [pdf:E04]

第三步，如果下一时步开始时，switch network 已经拿到预测的电感电流/电容电压，circuit element block 也已经拿到预测的开关电压/电流，那么两块就不必在该时步互相等待。预测值在这里不是最终输出，而是一种“提前一拍准备好的解耦接口”；corrector 才承担当前时步的正式状态输出。[pdf:E02] [pdf:E06]

第四步，研究者还必须回答两个问题：预测误差是否会破坏 corrector 的阶数，以及增加 predictor 是否会吃掉过多 FPGA 资源。论文分别用 Lipschitz 条件下的截断误差论证和一套 Kintex-7 实现回答；前者给出局部数学条件，后者展示单个案例的资源与时序结果。[pdf:E05] [pdf:E07]

## § 4 — 核心 Intuition

核心 intuition 是：不要等当前时步的开关网络算完后才开始算电路元件；在上一个时步就把双方下一拍所需的接口量预测出来，使两块在当前时步并行。预测量只用于打断数据依赖，当前输出仍由 corrector 校正，因此速度来自调度重排，而不是简单牺牲所有积分精度。[pdf:E02] [pdf:E04]

## § 5 — 具体方法与完整 Pipeline

以论文的 traction-system ac-dc-ac case 为例，完整 pipeline 如下。

1. **输入与状态。** 外部输入包括门极信号和交流源；动态状态是各电感电流与电容电压。案例拓扑包含输入侧整流桥、直流电容和输出侧三相逆变桥。[pdf:E06]
2. **IGBT 暂态建模。** 每个 phase-leg 的 IGBT 用 active-region equivalent circuit 近似。模型忽略 diode reverse-recovery current 与内部互连寄生，把 turn-on/off 分成 delay、rise、fall 等区间，用 \(dI_c/dt\) 与 \(dV_{ce}/dt\) 构造连续 piecewise waveform。[pdf:E03]
3. **压缩硬件表达。** 原本由式 (4)–(5) 给出的 12 段表达，被重组为四个线性形式；FPGA 单腿结构只需一个乘法和三个加法。每步根据预测支路电流的符号、另一器件状态和 gate signal 判断电流走 IGBT 还是 antiparallel diode，并更新对应系数。[pdf:E04]
4. **双输出。** IGBT block 同时产生 \(t+h\) 的 current status 和 \(t+2h\) 的 predictor；circuit-element block 也同时产生 \(t+h\) corrector 与 \(t+2h\) predictor。[pdf:E04] [pdf:E06]
5. **预测值交换。** 下一拍开始时，switch-network block 使用上一拍保存的预测电感电流/电容电压；circuit-element block 使用上一拍保存的预测 \(V_{ce}\) 与 \(I_c\)。两块并行执行，结束后各自写回 current result 与 next predictor。[pdf:E06]
6. **案例映射。** 输入电感 \(L_{s1}\)、直流电容 \(C_d\) 和三相负载电感分别按式 (19)、(21)、(23) 形成 predictor/corrector；Fig. 8 显示这些算术单元和多个 IGBT leg 在 FPGA 上并排布置。[pdf:E06] [pdf:E07]
7. **定时执行。** 作者使用 LabVIEW FPGA 的 single-cycle timed loop，使循环内函数在一个 FPGA clock tick 内完成，最终约束到 25 ns。[pdf:E07]

物理上，这套设计相当于让每个子系统携带一张“下一拍接口量的预报单”。只要预报没有改变开关导通分支，当前拍就可以先各算各的，最后用 corrector 给出正式状态。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从开关物理量到 piecewise predictor

论文先用门极回路与寄生参数给出开通阶段电流斜率的一种表达：

\[
\frac{dI_c(\tau_1)}{dt}
=
\frac{g_m(V_g-V_{th})-I_0}{R_g C_{ge}+g_m L_\sigma},
\]

并用 \(R_g C_{cg}\)、门极电压、阈值电压和负载电流给出 \(dV_{ce}/dt\)；关断阶段有对应表达。这里 \(g_m\) 是 forward transconductance，\(R_g\) 是 gate resistance，\(L_\sigma\) 是 stray inductance，\(C_{ge},C_{cg},C_{ies}\) 是等效电容。它们的物理作用是把门极驱动与寄生网络转换成电流、集射极电压的有限变化率，而不是让理想开关瞬时跳变。[pdf:E03]

把这些斜率按 delay/rise/fall 区间积分，得到式 (4)–(5) 的 \(I_c(t)\)、\(V_{ce}(t)\) piecewise waveform。为了硬件实现，作者又把每一段统一写成

\[
I_c=I_{c0}+A_x+B_x h,\qquad
V_{ce}=V_{ce0}+C_x+D_x h,
\]

其中 \(A_x,B_x,C_x,D_x\) 随开关阶段查表更新。因为同一线性段可把 \(h\) 换成 \(2h\)，当前时刻即可同时算出 \(t+h\) current value 与 \(t+2h\) predictor。[pdf:E04]

### 6.2 把 predictor 与 corrector 排到同一拍

线性状态方程写成

\[
\frac{dy}{dt}=f(t_n,y_n).
\]

论文用下面的并行 FE/BE 形式说明基本机制：

\[
y^p_{t+2h}=y_t+2h\,f(t,y_t),\qquad
y_{t+h}=y_t+h\,f\!\left(t,y^p_{t+h}\right).
\]

传统顺序是先得到 predictor，再把它送进 corrector；论文把 \(t+2h\) predictor 提前到求 \(t+h\) corrector 的同一拍。到下一时步时，下一次 predictor 已在寄存器中，因此关键路径不再包含“重新预测后才校正”的串联。[pdf:E04]

式 (11)–(12)进一步给出 3 阶、4 阶 Adams 型系数组合；式 (13)–(14)把 \(s\) 个方程推广为矩阵线性组合。每一项依赖不同历史样本，适合分配给 FPGA 独立算术电路并行累加。[pdf:E04] [pdf:E05]

### 6.3 阶数论证及其边界

作者把 exact solution 与 corrector 的误差写成截断误差和 predictor 误差经 \(f\) 传播的和。若 \(f\) 满足 Lipschitz continuity，且 predictor 的 global error 为 \(O(h^p)\)，则传播项多乘一个 \(h\)，从而 corrector error 为 \(O(h^{p+1})\)。论文据此称：当 predictor 阶数不低于 \(p\) 时，corrector 可达到 \(p+1\) 阶；式 (10) 的阶数为 2。[pdf:E05]

这个结论有两个重要边界。第一，它依赖 \(f\) 在所考察区间满足 Lipschitz 条件；理想拓扑跳变附近并不自动满足平滑直觉。第二，论文明确说这种方法适用于步长足够小的场景，并假设 FPGA 有足够资源并行铺开算术单元。[pdf:E05]

### 6.4 案例中的状态方程

以直流电容为例，

\[
C_d\frac{dU_{cd}}{dt}=i_{dc}-i_{dc1},
\]

于是同一拍分别用 \(2h/C_d\) 与 \(h/C_d\) 计算下一拍 predictor 和当前拍 corrector。输入电感及三相负载电感采取同样结构，具体见式 (18)–(23)。这说明论文的“预测行为”不是额外训练出的模型，而是由同一状态方程在不同时间索引上显式外推。[pdf:E06]

## § 7 — 实验设计与结论

### 问题一：数值结果是否接近参考模型？

**实验。** 作者建立 traction-system ac-dc-ac topology，以 MATLAB/Simulink 作为参考，而不是进行高功率实物实验。输入源幅值 3600 V、频率 50 Hz；逆变器采用 open-loop PWM，carrier frequency 2000 Hz、modulation index 0.4、基波频率 50 Hz；converter 一侧不给控制信号，以减少控制器差异对 solver error 的干扰。关键器件参数包括 \(t_{d,on}=280\) ns、\(t_{d,off}=160\) ns、\(C_d=3.01\) mF 等。[pdf:E07]

**作者报告的答案。** 输入电感电流相对 Simulink 的 absolute error 小于 50 A，对应 relative error 2%；直流电容电压 maximum absolute error 为 6 V，对应 relative error 小于 0.5%。predictor 与 corrector 的差异方面，输入电感电流低于 \(2\times10^{-3}\) A，电容电压低于 \(5\times10^{-6}\) V，输出相电流低于 \(5\times10^{-8}\) A。Fig. 10 还展示 turn-on/off transient 与 phase voltage，但本文不从曲线估读未印出的精确数值。[pdf:E07] [pdf:E08]

**证据强度。** 这支持“在该固定案例和给定工况下与 Simulink 接近”，不等价于对真实高功率硬件的误差认证。作者自己说明高功率实验更适合模型验证，但成本过高，因此采用 established tool 作为中间方案。[pdf:E07]

### 问题二：能否在真实 FPGA 时序上达到 25 ns？

**实验。** 目标平台是 NI PXIe-7975R FlexRIO 中的 Kintex-7 XC7K410T，采用 fixed-point 与 LabVIEW FPGA single-cycle timed loop。[pdf:E07]

**作者报告的答案。** 单案例满足 25 ns time constraint。资源表报告：Total Slices 使用 20,329/63,550（32%），Slice Registers 使用 45,509/508,400（9%），Slice LUTs 使用 54,366/254,200（21.4%），Block RAMs 使用 91/795（11.4%），DSP48s 使用 210/1540（13.6%）。[pdf:E07]

**证据强度。** 这是板级实现与综合/映射后的时序结果，比离线运行时间更直接；但论文没有展示多规模拓扑下步长和资源的 scaling curve，也没有给出与同一平台上 sequential solver 的严格 ablation。作者明确承认 predictor 可能使 DSP48 utilization 约翻倍，并限制可模拟系统规模。[pdf:E06]

### 原文内部歧义

Section VI、Fig. 7 和全文前部都把案例称为 ac-dc-ac topology；Conclusion 却写成 ac-dc-dc。图示包含整流桥、直流链路和三相逆变桥，因此读者可以判断前者与图更一致，但这里保留为原文内部不一致，不把推断改写成论文事实。[pdf:E06] [pdf:E08]

## § 8 — Take-aways

### 5 句话

1. 论文把实时 solver 的关键瓶颈定位为 switch network 与 circuit element 之间的时步内串行依赖。[pdf:E02]
2. 它用连续 piecewise IGBT model 预测下一拍开关接口量，而不是只用理想二值电阻。[pdf:E03]
3. 它把 predictor 与 corrector 错开一个时间索引，使两类计算在同一拍并行，同时用 corrector 保留较高阶精度。[pdf:E04] [pdf:E05]
4. 单个 ac-dc-ac 案例在 Kintex-7 FlexRIO 上报告 25 ns 步长，并与 Simulink 结果接近。[pdf:E07] [pdf:E08]
5. 最主要代价是额外 predictor 算术和约两倍 DSP48 压力，而验证范围仍限于一个 open-loop 案例和 Simulink reference。[pdf:E06] [pdf:E07]

### 3 句话

1. 这项工作的实质贡献是用“提前一拍的预测接口”重排 FPGA solver，而不是单纯换一种积分公式。[pdf:E02] [pdf:E06]
2. 它在一个真实 FPGA 实现中展示了 25 ns timing 与较小 reference-model error，但没有用高功率实验或大规模拓扑证明普适性。[pdf:E07]
3. 因而最值得继承的是解耦思路，最需要重新验证的是预测值在开关边界附近能否始终给出正确离散状态。

### 1 句话

用 predictor 打断跨模块依赖、用 corrector 保住当前输出，是本文把详细一点的开关行为塞进 25 ns FPGA 时步的核心办法。[pdf:E03] [pdf:E04] [pdf:E07]

## § 9 — 最脆弱的假设

最脆弱的假设是：**提前一拍得到的接口预测不仅数值上接近，而且不会让开关状态判断走到错误分支。**

这是比“平均误差小”更强的条件。模型会根据预测支路电流的正负、gate signal 和互补器件状态判断电流流经 IGBT 还是 antiparallel diode；如果预测误差恰好出现在零电流、换相或门极边沿附近，即使误差绝对值很小，也可能改变离散导通状态。一旦分支选错，switch network 与 circuit element 的并行结果就不只是小的积分误差，而可能对应不同拓扑。[pdf:E04]

论文提供的支持是单案例中 predictor-corrector 差异很小，且 FPGA 波形与 Simulink 接近。[pdf:E07] [pdf:E08] 但它没有报告以下压力条件：零电流附近的状态误判次数、同一步内 multiple switching events、突变 gate command、短路/故障、参数失配、步长扫描，或包含 diode reverse recovery 的详细器件 reference。IGBT 推导还明确忽略 diode reverse-recovery current 和内部互连寄生，并假设 delay time 在不同 power range 下保持常数。[pdf:E03]

因此，基于证据的判断是：论文证明了预测误差在一个平稳 open-loop case 中足够小，却没有直接证明“所有关键开关事件上预测状态都正确”。这正是核心并行解耦最可能失效的位置。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 FlexRIO bitfile，而是“预测解耦是否在开关事件附近保持正确状态”这一核心数值 claim。

**数据与模型。** 复建 Fig. 7 的 ac-dc-ac state equations，使用 Table II 参数、3600 V/50 Hz 源与 2 kHz open-loop PWM；用一个足够小步长的 sequential reference（或论文使用的 Simulink model）作为基准。[pdf:E06] [pdf:E07]

**实现。** 分别实现传统顺序 solver 和式 (7)、(10)、(19)、(21)、(23) 的 parallel predictor-corrector。不要先做 HDL；在软件中显式模拟寄存器的“一拍延迟”，确保比较的是调度语义而不只是公式输出。

**测量。**

- 每个开关事件前后 \(I_c,V_{ce}\)、各电感电流和电容电压的误差；
- predictor 与 corrector 的差；
- predictor 导致的 IGBT/diode branch 与 reference branch 不一致次数；
- 计算 dependency depth 或按目标 FPGA 运算延迟估算的 critical path；
- 在 \(h=25\) ns 附近及更大步长下的误差/状态失配曲线。

**支持标准。** 25 ns 下所有离散开关状态与 reference 一致，状态误差保持在论文报告量级，并且并行 schedule 的关键依赖深度明显短于 sequential schedule，才同时支持“可解耦”和“数值可接受”。

**反驳标准。** 即使平均波形误差很小，只要在零电流或门极边沿出现可重复的错误导通分支，或者 25 ns 才能避免错误而没有实际关键路径收益，就足以削弱核心 claim。

## § 11 — 最强反例设计

最强反例是构造一个“数值误差很小但离散状态必错”的换相边界。

具体做法是让支路电流在一个时步内穿过零点，同时施加接近该时刻的 gate edge；再扫描负载电感、直流电压、\(t_{d,on/off}\)、步长和采样相位，使 predictor 的电流符号与高分辨率 reference 相反。reference 使用包含 diode reverse recovery 和寄生参数的 detailed switching model；被测模型保持论文的简化 piecewise IGBT 与一拍预测接口。[pdf:E03] [pdf:E04]

攻击指标不是整段波形 RMSE，而是：

1. IGBT/antiparallel-diode branch 是否选错；
2. 错误拓扑持续几个时步；
3. \(V_{ce}\)、\(I_c\) 或直流链路能量误差是否被后续 corrector 消除；
4. 多次事件后是否积累偏差或产生数值振荡。

如果能找到一组物理合理参数，使 predictor-corrector 数值差仍看似很小、但开关 branch 稳定误判，那么论文用“小预测差”支撑并行分区的解释就不充分。反之，如果边界扫描中离散状态始终一致，才是比当前 Fig. 10 更强的证据。

## § 12 — Follow-up Research Idea

电力电子实时仿真中的高影响工作通常同时看四件事：暂态/事件精度、确定性实时步长、真实硬件映射与资源可扩展性，以及面向 controller-HIL 或 power-HIL 的系统价值。本文已经给出真实 FPGA timing 和一个 reference-model comparison，但在开关事件可信度与规模扩展上留下空白。[pdf:E06] [pdf:E07]

**候选研究想法：带事件可信度证书的预测解耦 solver。** 这只是基于本文局限提出的候选方向；由于没有充分检索相关工作，不能声称 novelty。

**(a) 未满足需求。** 现有方法每一步都使用单点 predictor 作为跨模块接口，却没有判断这个预测在离散开关状态上是否可信。真正需要的不是让所有数值都更准，而是在不牺牲平均并行度的前提下，保证 predictor 不会跨过影响拓扑选择的边界。

**(b) 研究价值。** 把目标从“平均波形接近”改成“并行执行前可验证开关状态不变”，可直接回应 HIL 最危险的瞬态错误。如果在绝大多数平稳时步维持 25 ns 级并行，而只对无法认证的事件步采取额外处理，就可能同时改善可信度与实时性。

**(c) 相邻领域工具。** 可借鉴 hybrid-systems guard analysis、validated numerics/interval arithmetic 和 reachability 的思想：不只传播一个 \(y^p\)，还传播下一拍接口量的保守区间；只有当整个区间都落在同一个 IGBT/diode guard 区域时，才签发“可安全并行”的证书。

**(d) 第一个证伪实验。** 使用第 11 节的零电流/门极边沿 adversarial sweep。若区间证书仍放过任何 reference-state mismatch，或为了避免误判而在多数时步都拒绝并行，使有效步长/吞吐显著劣于本文方案，这个想法就被早期证伪。

**(e) 与本文的实质区别。** 本文预测一个下一拍数值，并默认它足够准确以交换模块接口；新问题改为预测“下一拍可能落在哪个状态集合”，并把能否并行变成一个可检查的事件安全条件。它改变的是 solver 的正确性目标和接口语义，而不是只增加一个更高阶公式。

[pdf:E01]: _evidence/E01-p001-title-abstract-introduction.png
[pdf:E02]: _evidence/E02-p002-fig01-02-prior-and-predictive-structure.png
[pdf:E03]: _evidence/E03-p003-fig03-eq01-05-igbt-model.png
[pdf:E04]: _evidence/E04-p004-fig04-05-eq06-11-predictor-corrector.png
[pdf:E05]: _evidence/E05-p005-eq12-17-general-form-error-order.png
[pdf:E06]: _evidence/E06-p006-fig06-07-eq18-23-case-model.png
[pdf:E07]: _evidence/E07-p007-fig08-09-table01-02-platform-parameters.png
[pdf:E08]: _evidence/E08-p008-fig10-results-conclusion.png
