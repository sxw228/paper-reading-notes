# A Discrete Small-Step Synthesis Real-Time Simulation Method for Power Converters

- 作者：Zirun Li, Jin Xu, Keyou Wang, Guojie Li, Pan Wu
- 出处：IEEE Transactions on Industrial Electronics, Vol. 69, No. 4
- 年份：2022
- DOI：10.1109/TIE.2021.3076702
- Zotero key：G8FRSHQ9

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的实时 EMT 仿真矛盾：L/C fixed-admittance switch model 用小电感表示 ON、用小电容表示 OFF，因此开关动作不会改变节点导纳矩阵，适合 FPGA 上避免每次开关都重组和求解矩阵；但这些人为加入的储能元件在切换后会经历并非真实理想开关所有的充放电暂态，从而产生 virtual power loss。已有做法可以把仿真步长压小来缩短这个假暂态，但硬件必须在同样短的时间内完成一次完整网络计算，实时期限又限制了步长。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

问题的物理意义不是“怎样把计算做得更快”这么泛，而是怎样把两个时间尺度拆开：内部模型需要纳秒级步长，才能让 L/C 假暂态迅速衰减；外部实时接口仍希望以微秒级步长推进，才能给 FPGA 足够的计算预算。作者的目标是在不缩短对外 simulation time-step 的前提下，把一个 normal step 内的多个 small-step 状态转移先合成为一次等价更新。[pdf:E03]（PDF 物理页 3，Section III-A/B，Eq. (10)–(14)）

如果成功，这个方法同时保留 fixed admittance 的硬件友好性和更接近理想开关的暂态行为，并减少为不同拓扑、载波频率或外部工况重新寻找 L/C 参数的工作。论文把这一价值限定在 power converter 的实时仿真，没有证明它已经解决任意电力电子网络、任意事件时序或器件级开关暂态问题。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

## § 2 — 前人工作与不足

论文给出的技术谱系分成三层。用于电网稳定性研究的 average model 和 dynamic phasor model 计算便宜，但不面向高频开关暂态；Ron/Roff model 在 PSCAD 等离线仿真中常用，也被少数平台用于特定拓扑的小步长实时仿真；L/C model 则已用于 RTDS Small_dt、OPAL-RT eHS、ADPSS 和多种 FPGA small-step simulator，因为它能保持节点导纳矩阵不随开关动作改变。[pdf:E01]（PDF 物理页 1，Introduction）

针对 L/C virtual power loss，论文归纳了三类既有修补：为 L/C 参数寻找最优值、设计具有 best-damping 特性的 generalized associated discrete circuit model、以及在开关动作后重置或优化初始状态。作者指出它们仍有两个共同难点：所谓最优参数依赖拓扑和外部运行状态，拓扑变化后可能要重算；而单纯缩短 time-step 虽能降低损耗，却把每步硬件计算期限一起压短。[pdf:E01]（PDF 物理页 1，Introduction 末段）[pdf:E02]（PDF 物理页 2，左栏开头）

因此，本文不是再换一组 L/C 参数，而是改变“建模步长必须等于实时推进步长”这个默认前提。需要注意的是，本节只重述论文自身的 related-work 定位；本任务没有做外部检索，不能据此声称 small-step synthesis 在所有相关工作中具有完整 novelty。

## § 3 — 重建作者的思考路径

下面是基于论文证据的合理重建，不是作者逐字陈述的研发日志。

第一步，研究者会观察到 L/C 模型的误差具有明确时间结构：开关后通常要经历约 10–20 个 modeling steps 才收敛；开关越多、频率越高，这些非物理暂态的损耗会累积。[pdf:E03]（PDF 物理页 3，Section III-A）

第二步，他们会把问题识别为 stiffness 与实时预算的冲突。小 L、小 C 引入最快动态，因此数值稳定和快速衰减要求纳秒级内部网格；但实时仿真只要求每个微秒级外部采样时刻交付新的电压、电流，不必把每个内部子步都逐一暴露给外部系统。[pdf:E02]（PDF 物理页 2，Introduction 延续）

第三步，要想“隐藏”内部子步，原始 EMTP 的串行 nodal-analysis 流程必须先改写成可合成的离散状态空间形式。论文选历史电流 \(I_h\) 为 state、Norton 注入电流 \(I_s\) 为 input，把节点电压 \(V_n\) 和支路电流 \(I_b\) 放入 output equation，于是每个小步都变成相同形状的线性仿射状态更新。[pdf:E02]（PDF 物理页 2，Section II，Eq. (1)–(9)）

第四步，既然 small-step 的 \(E,F\) 在一个 normal step 内被视为常矩阵，就可以像合成离散运动那样把 \(k\) 次递推折叠成 \(A'_k,B'_k\)。这样，复杂度从“运行时执行 \(k\) 次网络步进”转移为“使用预先合成的 normal-step operator 做一次状态更新”。这条思路受运载火箭姿态实时数字仿真的 small-step synthesis 启发，是论文明确给出的来源。[pdf:E02]（PDF 物理页 2，Introduction）[pdf:E04]（PDF 物理页 4，Eq. (15)–(19) 与 Fig. 3）

## § 4 — 核心 Intuition

核心 intuition 是：用纳秒级 \(h\) 构造开关模型的动力学，但把一个微秒级 \(\Delta t\) 内的 \(k\) 次小步状态转移提前合成为一个等价 operator，运行时仍只推进一次 \(\Delta t\)。这样，L/C 开关的非物理充放电暂态在“模型时间”里已经走完，而 FPGA 的对外实时 deadline 没有缩短。[pdf:E03]（PDF 物理页 3，Section III-B）[pdf:E04]（PDF 物理页 4，Fig. 3 与 Eq. (15)–(19)）

## § 5 — 具体方法与完整 Pipeline

以论文的 two-level converter 验证为例，完整 pipeline 如下。

1. **把网络写成 Norton/nodal 形式。** 节点导纳矩阵 \(Y_n\)、支路导纳矩阵 \(Y_b\) 和 incidence matrix \(K\) 把节点电压、支路电流、历史电流与外部注入联系起来。作者将 \(I_h\) 定义为 state、\(I_s\) 定义为 input，得到离散状态空间模型
   \[
   I_h(t+\Delta t)=AI_h(t)+BI_s(t),\qquad
   \begin{bmatrix}V_n(t)\\I_b(t)\end{bmatrix}=CI_h(t)+DI_s(t).
   \]
   [pdf:E02]（PDF 物理页 2，Eq. (1)–(9)）
2. **用 fixed-admittance L/C 表示开关。** ON 状态由小电感 \(L_s\) 表示，OFF 状态由小电容 \(C_s\) 表示；backward Euler 离散后令 \(Y_{\mathrm{on}}=\Delta t/L_s=Y_{\mathrm{off}}=C_s/\Delta t\)，从而开关动作不改变等效导纳，只改变历史源的更新关系。[pdf:E03]（PDF 物理页 3，Fig. 2，Eq. (10)–(11)）
3. **把 normal step 切成 \(k\) 个 modeling substeps。** 令 \(h=\Delta t/k\)，用 \(h\) 重新构造 small-step state/input matrices \(E,F\)，在 \([t,t+\Delta t]\) 内写出 \(I_h(t+(i+1)h)=EI_h(t+ih)+FI_s(t+ih)\)。[pdf:E03]（PDF 物理页 3，Eq. (12)–(14)）
4. **合成一次 normal-step operator。** 从 \(A'_0=I,B'_0=0\) 开始递推 \(A'_{i+1}=EA'_i,\ B'_{i+1}=EB'_i+F\)，最终得到 \(I_h(t+\Delta t)=A'_kI_{h0}+B'_kI_{s0}\)。运行时只执行这次 aggregate update，再由 \(C',D'\) 输出节点电压与支路电流。[pdf:E04]（PDF 物理页 4，Eq. (15)–(19) 与 Fig. 3）
5. **用统一参数在 FPGA 上执行。** two-level 和 three-level converter 在 Xilinx Kintex-7 XC7K410T 上使用 \(\Delta t=1\,\mu s\)、\(k=30\)、switch equivalent admittance \(0.3\,S\) 和 5 kHz PWM；Table I 还给出 800 V dc-link、220 V RMS/50 Hz grid、\(L_f=2\,mH\)、\(C_f=10\,\mu F\)、\(C_{dc}=1000\,\mu F\)、\(L_g=1\,mH\)。[pdf:E05]（PDF 物理页 5，Table I 与 Section V-A）
6. **输出并比较开关波形和 virtual power loss。** PSCAD 的 Ron/Roff model 被作为 benchmark，其中 \(R_{\mathrm{on}}=1\,m\Omega\)、\(R_{\mathrm{off}}=1\,M\Omega\)；同一 converter 还运行 traditional EMTP + L/C，以分离“模型仍为 L/C”与“是否 small-step synthesis”两个因素。[pdf:E05]（PDF 物理页 5，Section V-A）

开关/事件处理方面，论文给出 ON/OFF 的 L/C 历史源关系，但没有报告亚步事件定位、插值或同一 normal step 内多个异步开关沿的处理规则。数值表示方面，论文没有报告 fixed-point/float、位宽或量化误差。FPGA 方面只明确了器件和实时波形实验，没有给出 LUT、DSP、BRAM、clock、pipeline 深度、worst-case execution time 或资源随系统规模的增长关系；这些都不能从“在 FPGA 上运行”反推出来。

## § 6 — 核心数学推导

### 1. 从网络方程到可合成状态更新

EMTP nodal analysis 先由 \(V_n=Y_n^{-1}I_n\)、\(I_n=K(I_h+I_s)\) 和 \(V_b=K^\mathsf{T}V_n\) 得到节点/支路输出；历史电流再由离散电感、电容的 companion model 更新。把中间变量消去后，所有网络计算被压成 Eq. (9) 的 state/output 两部分。[pdf:E02]（PDF 物理页 2，Eq. (1)–(9)）

这一步的工程意义是把“求解电路”变成矩阵乘加图：state update 与 output calculation 的依赖关系显式，适合并行实现，也为后续 operator composition 提供统一接口。它并不消除矩阵运算，只是把每步需要的结构固定下来。

### 2. 合成 \(k\) 次 small-step

在 normal step \(\Delta t\) 内令 \(h=\Delta t/k\)，small-step recurrence 为
\[
I_{h,i+1}=EI_{h,i}+FI_{s,i}.
\]
论文用 holder 把这一 normal step 内的注入近似为 \(I_{s,i}=I_{s0}\)，于是
\[
A'_{i+1}=EA'_i,\qquad B'_{i+1}=EB'_i+F,
\]
\[
I_h(t+\Delta t)=A'_kI_{h0}+B'_kI_{s0}.
\]
[pdf:E03]（PDF 物理页 3，Eq. (12)–(14)）[pdf:E04]（PDF 物理页 4，Eq. (15)–(19)）

把递推展开可看出 \(A'_k=E^k\)，而 \(B'_k=\sum_{j=0}^{k-1}E^jF\)（这是由论文递推式直接推出的代数等价式）。物理上，\(E^k\) 描述旧历史电流经历 \(k\) 个纳秒级衰减后的剩余量，求和项描述同一持有输入在各小步注入后共同积累的结果；因此 runtime 不必真的逐个执行这些小步。

### 3. 用 spectral radius 选择 \(k\)

作者把 state matrix 的 spectral radius 当作开关假暂态收敛速度指标。单开关分析中，small-step synthesis 的参数扫描里超过 97% 的 eigenvalues 小于 \(10^{-4}\)，而 \(k=1\) 的 traditional EMTP 最小值仍大于 \(10^{-4}\)；对 two-/three-/five-level converter 的扫描显示，\(k\) 增大时 spectral radius 快速下降，论文据此给出“通常 \(k=30\) 足以把暂态压进一个 normal step”的经验选择。[pdf:E04]（PDF 物理页 4，Fig. 5 与正文）[pdf:E05]（PDF 物理页 5，Fig. 6，Eq. (21)–(22) 与正文）

### 4. 误差从哪里来

Appendix 把误差分成 small-step backward Euler truncation 与 holder error。执行 \(k\) 次一阶积分后，前者满足
\[
\lVert\varepsilon_t\rVert\le \frac{\mu}{k^p}\Delta t^{p+1},
\]
所以增大 \(k\) 会压低内部积分误差。[pdf:E08]（PDF 物理页 8，Eq. (A1)–(A2)）

但 \(I_s\) 在整个 \(\Delta t\) 内被 holder 近似，误差仍由 normal step 控制。论文在 \(A\) 稳定、\(\alpha=\lVert e^{A\Delta t}\rVert<1\) 且 \(k\) 足够大时，给出
\[
\lVert\varepsilon_m\rVert < \frac{1}{1-\alpha}\,\xi\,\Delta t^{q+1}.
\]
zero-order holder 对应整体误差 \(O(\Delta t^2)\)；作者还指出若改用 second-order holder，可达到 \(O(\Delta t^4)\)。[pdf:E09]（PDF 物理页 9，Eq. (A10)–(A13) 与其后正文）

因此，这个方法缩小的是 L/C 内部快暂态的积分误差，并没有让微秒级外部输入采样误差自动消失。这也是后面最关键的失效边界。

## § 7 — 实验设计与结论

**问题 1：small-step synthesis 是否真的加快 L/C 假暂态的收敛？** 作者扫描 single-switch 的 small-step count 与外部/开关导纳比，并进一步比较 two-/three-/five-level converter 的 spectral radius。结果是 spectral radius 随 \(k\) 快速下降，论文以 \(10^{-4}\) 为近似理想开关的收敛阈值，并据此选择一般性的 \(k=30\)。这是模型内的动态分析，不是独立硬件测量。[pdf:E04]（PDF 物理页 4，Fig. 5）[pdf:E05]（PDF 物理页 5，Fig. 6）

**问题 2：相同 \(1\,\mu s\) 实时步长下，波形是否比 traditional EMTP + L/C 更接近 benchmark？** 作者在 Kintex-7 FPGA 上运行 two-level 与 three-level converter，把 oscilloscope 波形与 PSCAD Ron/Roff benchmark、traditional EMTP + L/C 对比。Fig. 7/8 显示 traditional EMTP 的开关电压、电流存在跨多个 time-steps 的振荡和较大瞬时 power loss，而 small-step synthesis 波形在视觉上更接近 PSCAD。[pdf:E05]（PDF 物理页 5，Section V-A）[pdf:E06]（PDF 物理页 6，Fig. 7 与 Section V-B）[pdf:E07]（PDF 物理页 7，Fig. 8）

**问题 3：载波频率升高时，virtual power loss 是否仍受控？** virtual power loss 定义为 converter 全部开关损耗与输入功率之比。two-level traditional EMTP 在 5/10/20/50 kHz 下分别报告 18.36%/32.15%/53.58%/85.25%，small-step synthesis 分别为 0.34%/0.35%/0.36%/0.48%；three-level small-step synthesis 为 0.25%/0.25%/0.26%/0.31%，five-level 为 0.15%/0.24%/0.42%/0.96%。[pdf:E06]（PDF 物理页 6，Table II 与 Section VI-A）

**问题 4：收益是否只是把 real-time step 偷偷缩短？** 在 10 kHz two-level converter、同一 L/C 参数下，traditional EMTP 在 250 ns 和 \(1\,\mu s\) 的损耗分别为 9.69% 和 32.15%；small-step synthesis 分别为 0.08% 和 0.34%。这支持“内部 modeling step 与外部 simulation step 分离”本身贡献了主要改进。[pdf:E06]（PDF 物理页 6，Table III）[pdf:E08]（PDF 物理页 8，Section VI-C）

**问题 5：是否需要按拓扑和 switch admittance 调参？** 作者在相同参数下测试 two-/three-/five-level topology，并把 equivalent admittance 从 10 S 扫到 0.002 S。Fig. 11 显示 small-step synthesis 的曲线在该扫描内保持低损耗，而 traditional EMTP 只在局部最优值附近较低；作者据此声称对 topology、carrier frequency 和 L/C parameter 不敏感。[pdf:E07]（PDF 物理页 7，Section VI-B）[pdf:E08]（PDF 物理页 8，Fig. 11 与 Conclusion）

这些结果支持“在论文覆盖的 converter、参数与事件条件下，virtual power loss 显著降低”，但证据仍有边界：benchmark 是离线 PSCAD 模型而非实物功率回路；波形相似主要靠图示而非统一的 RMS/max error 表；没有 FPGA resource、clock、worst-case latency 或规模扩展数据；也没有报告多个异步开关事件落在同一 normal step 内时的误差。因此不能外推为任意拓扑上的无条件实时性、器件级 transient fidelity 或硬件资源可扩展性。

## § 8 — Take-aways

**5 句话：**

1. L/C fixed-admittance model 的核心优点是避免开关动作引起导纳矩阵重组，核心缺点是人为 L/C 暂态造成 virtual power loss。
2. 本文把纳秒级 modeling step 与微秒级 simulation step 分离，并将 \(k\) 次 small-step transition 合成为一次 normal-step update。[pdf:E03]（PDF 物理页 3，Section III）[pdf:E04]（PDF 物理页 4，Fig. 3）
3. spectral-radius 分析给出 \(k\) 的收敛解释，论文采用 \(k=30\) 做 \(1\,\mu s\) FPGA 实时验证。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Table I）
4. 在论文测试范围内，small-step synthesis 把 virtual power loss 从 traditional EMTP 的两位数乃至 85.25% 降到 1% 以下。[pdf:E06]（PDF 物理页 6，Table II–III）
5. 其最重要的未闭合边界是 normal step 内 input holding 与事件时序，而不是内部 L/C 暂态是否能被 \(k\) 个小步压缩。

**3 句话：**

1. 这是一种 operator synthesis：把很多纳秒级内部状态转移折叠成一次微秒级实时更新。
2. 它在 two-/three-/five-level converter、carrier frequency 和 admittance 扫描中显著降低了 L/C virtual power loss。[pdf:E06]（PDF 物理页 6，Table II–III）[pdf:E08]（PDF 物理页 8，Fig. 11）
3. 论文没有证明 intra-step 异步事件、FPGA 资源扩展和实物 transient fidelity。

**1 句话：**

本文的价值在于保留 fixed-admittance 的实时计算结构，同时用预合成的 small-step dynamics 消除大部分 L/C 假暂态，但其可信范围仍受 normal-step input/event 近似约束。

## § 9 — 最脆弱的假设

最脆弱的假设是：在一个 normal step \([t,t+\Delta t]\) 内，外部 Norton injection \(I_s\) 可以由 holder 足够准确地表示，且用于 operator synthesis 的状态动力学在这一段内保持可用。Eq. (16) 明确使用 \(I_{s0}\) 合成整个 step；单开关动态分析还假设外部电路中的其他开关不与被分析开关同时动作。[pdf:E04]（PDF 物理页 4，Eq. (16)、Section IV-A）

如果多个 PWM edge 异步落在同一个 \(1\,\mu s\) step 内，或外部网络在 step 内产生快速反馈，\(I_s\) 就不是“慢变量”。此时 \(k\) 再大也只会更精确地积分一个错误冻结的输入，内部 L/C 假暂态虽然收敛，真实事件驱动的电流变化却可能被错过。这是基于方程结构的推断，不是论文已经观测到的失败。

论文承认 holder 会带来 sampling error，并在 Appendix 给出稳定线性系统下的阶数上界；但它没有用异步事件密集、多开关同时切换或强 step 内耦合的实验直接验证这一假设。[pdf:E08]（PDF 物理页 8，Appendix Eq. (A3)–(A9)）[pdf:E09]（PDF 物理页 9，Eq. (A10)–(A13)）

## § 10 — 最小复现实验

一周内最值得复现的是“相同 normal step 下，operator synthesis 是否把 virtual power loss 降低至少一个数量级”，不必先复刻完整 FPGA。

1. 按 Table I 建立 two-level converter：800 V dc-link、220 V RMS/50 Hz grid、\(L_f=2\,mH\)、\(C_f=10\,\mu F\)、\(C_{dc}=1000\,\mu F\)、\(L_g=1\,mH\)、switch admittance 0.3 S、5 kHz PWM。[pdf:E05]（PDF 物理页 5，Table I）
2. 实现两条共享同一网络和开关序列的 L/C 求解路径：traditional EMTP \(k=1\)，以及 small-step synthesis \(k=30\)。再用足够细步长的 Ron/Roff solver 作为只读 reference。
3. 在 \(\Delta t=1\,\mu s\) 和 250 ns 两档下记录每次 edge 后的 settling steps、switch voltage/current 的 peak deviation、以及论文定义的 virtual power loss。
4. 预先规定支持标准：两档步长下 small-step synthesis 的 virtual power loss 都低于 1%，且至少比相同 \(\Delta t\) 的 traditional EMTP 低 10 倍；同时 reference 对齐后的开关后振铃显著缩短。这个 10 倍阈值是本复现实验的判据，不是论文原文阈值。
5. 反驳标准：任一档中 small-step synthesis 的损耗不低于 traditional EMTP，或虽然损耗下降却产生更大的 node-voltage/current 误差。

论文没有公开完整模型文件、PWM 初相位、控制器细节和误差计算脚本，因此复现应首先检验趋势与数量级，而不能把逐点波形不一致直接解释为方法失败。

## § 11 — 最强反例设计

最强反例不是再换一个静态 topology，而是专门破坏第 9 节的 holder 假设。构造两个或多个共享 dc-link/滤波网络的 converters，让各 bridge 的 PWM edges 随机错开，并使一部分 edge 落在同一 \(1\,\mu s\) normal step 的不同 substep；再加入一个使 injection current 在 step 内显著变化的低阻尼外部网络。用 10 ns event-resolved Ron/Roff 或直接逐 small-step 的 L/C 仿真作为 reference，对比原 small-step synthesis \(k=30\)。

攻击指标应同时包括 edge-time-dependent current error、dc-link 能量误差、virtual power loss 和最坏 step latency。若误差主要随“edge 在 normal step 中的位置”变化，而不是随 \(k\) 下降，并且在载波频率仍处于论文测试范围时就超过 traditional EMTP 或 reference 的可接受误差，那么“对 topology/carrier frequency 不敏感”的解释就必须收缩为“对同步到 normal-step 边界的测试工况不敏感”。该反例的证据起点是论文的 \(I_{s0}\) holding 和 non-simultaneous-switch assumption；反例本身是本卡提出的候选实验，不是论文结果。[pdf:E04]（PDF 物理页 4，Eq. (16)、Section IV-A）[pdf:E06]（PDF 物理页 6，Table II）

## § 12 — Follow-up Research Idea

在电力电子实时仿真领域，高影响工作通常不仅要给出更低误差，还要同时证明 deterministic latency、硬件资源可扩展性、跨工况稳定性以及与物理或高可信 reference 的一致性。基于第 9 节，候选方向是 **event-aware small-step operator composition**：不再把一个 normal step 内的 \(I_s\) 冻结成单一 \(I_{s0}\)，而是把 step 按实际开关事件时刻切成少量片段，为“无事件段”和“事件后段”预计算 transition operators，并在 FPGA 上按 event mask 与 substep offset 组合这些 operators。

- **(a) 未满足需求：** 多 converter、异步 PWM 和强耦合网络中，内部事件可能发生在 normal-step 边界之间；现有 \(A'_k,B'_k\) 合成没有显式保存事件时刻。
- **(b) 潜在研究价值：** 如果能在不恢复逐 10 ns runtime stepping 的前提下显著降低 intra-step event error，就同时推进 fidelity 与 deterministic real-time execution，而不是只做参数调优。
- **(c) 可借鉴工具：** 可借鉴 switched/hybrid systems 的 event segmentation、event-driven simulation，以及并行计算中的 prefix-scan/operator composition；这里仅提出方法连接，没有完成相关工作检索。
- **(d) 首个证伪实验：** 使用第 11 节的随机 edge-offset 双 converter 工况；若 event-aware 版本不能在固定 \(1\,\mu s\) deadline 内把最坏电流误差明显降到原 zero-order-hold 版本以下，或资源/组合延迟随事件数失控，则该方向被证伪。
- **(e) 与本文的实质区别：** 本文合成的是“固定输入下的 \(k\) 个均匀 small steps”；新方向合成的是“由 step 内事件分段定义的非均匀 operator sequence”，改变的是输入与事件的建模边界，而不是更换 converter 应用或附加一个后处理模块。

这是证据约束下的候选研究想法；由于本任务禁止联网和跨论文检索，不声称 novelty。
