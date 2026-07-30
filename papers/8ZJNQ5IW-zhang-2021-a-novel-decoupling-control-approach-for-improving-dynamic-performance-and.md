# A Novel Decoupling Control Approach for Improving Dynamic Performance and Stability of Multiple Grid-Connected Converters

作者：Yonglei Zhang、Xibo Yuan、Xiaojie Wu [pdf:E01]

出处：IEEE Transactions on Industrial Electronics，Vol. 69，No. 9，pp. 8613–8624 [pdf:E01]

年份：2021 [pdf:E01]

DOI：10.1109/TIE.2021.3116556 [pdf:E01]

Zotero key：8ZJNQ5IW

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是：多台并联 grid-connected converters 经公共 grid impedance 接入电网时，如何同时提高各电流环的动态带宽与稳定性。作者指出，并联系统的 plant 不是若干互不相干的 SISO 对象，而是非对角的 MIMO 耦合系统；并联台数为 \(n\) 时，各机所见的等效 grid impedance 效应会随 \(n\) 放大。弱电网、并联台数增加或滤波电感减小时，耦合既会压低电流环带宽，也可能在增大 regulator gain 后触发高频交互振荡。[pdf:E01]（PDF 物理页 p001，Abstract 与 Section I）

工程上的矛盾很具体：保守地按单机滤波电感整定，公共电流的响应变慢、低频谐波增加；按包含放大后 grid impedance 的对象整定，又可能使 converter 间的 difference-current mode 失稳。论文因此不把“系统不振荡”当作唯一目标，而是要求在不改滤波器或电网硬件的前提下，同时得到较快的 grid-current response 和受控的机间差流。[pdf:E02][pdf:E05]（p002，Table I 后的比较与贡献说明；p005，Eq. (11)–(12) 和 Fig. 3）

这一问题对大型风电、光伏 string inverter 和储能的模块化并联系统重要，因为这些系统通过并联模块扩展功率并共享升压变压器或公共接入点。论文讨论的价值不是减少 EMT 仿真成本，而是给真实控制器一个可以按单变量理论整定的结构；论文没有报告 EMT 求解加速、FPGA 实时仿真步长或硬件在环加速结果。[pdf:E02][pdf:E07]（p002，Fig. 1 与 Section II 开头；p007，Section IV-C）

## § 2 — 前人工作与不足

论文把相关工作分成几条路线。MIMO/state-space 与 frequency-domain modal analysis 能显式描述非对角耦合，reduced-order aggregate model 能降低多变换器仿真的复杂度，但作者认为它们难以给出直观、直接的 current-regulator design guideline。Impedance/admittance 方法能判断稳定性或 reshape 阻抗，却不能同时给出保证 current-control bandwidth 的简单精确整定。把电流分成 internal/parallel/series resonance、low/high-frequency interaction 或 common/interactive current 的分类方法有清楚的物理解释，但若要从 multivariable control 角度真正消除机间耦合，还需要额外设计 feedforward compensation。Active damper 与 notch filter 主要面向稳定性；convex-optimization control 给出另一条 MIMO 设计路线，但论文认为其实验性能仍需进一步评价。[pdf:E01][pdf:E02]（p001–p002，Section I 与 Table I）

最接近的先前工作是作者自己的文献 [23]：它已用 summation-difference coordinate 把多机模型变成多个单变量模型，用于分析 interactive oscillation；但它停在 modeling/analysis。本文声称的增量是把实际 current control 也放进这个坐标系，为 summation-current loop 和 difference-current loops 分别配置 regulator。[pdf:E02]（p002，贡献说明）

需要收紧作者的比较口径。论文的实验只直接比较了三组 conventional PI gains 与所提方法，没有在同一原型上实现 impedance reshaping、active damping、notch filter 或 convex-optimization control。因此，“优于 conventional method”有直接实验支持；“优于表中所有既有路线”只是作者基于能力边界的论述，不能由本文实验单独推出。[pdf:E02][pdf:E08][pdf:E09]（p002，Table I；p008–p009，Fig. 7–10）

## § 3 — 重建作者的思考路径

下面是基于论文证据的合理重建，而不是作者逐字给出的研究日志。

第一步，从公共 PCC 写出 superposition 关系。每台 converter 的输出电压不仅驱动自己的滤波支路，还通过 \(Z_g\) 改变公共点电压，所以得到的 transfer-function matrix 具有相同的 diagonal term \(Y_1\) 和相同的 off-diagonal term \(Y_2\)。只要 \(Z_g\neq 0\)，各机电流就互相受其他 regulator 影响。[pdf:E03]（p003，Eq. (1)–(2)）

第二步，观察这个矩阵的置换对称性。公共方向 \([1,\ldots,1]\) 描述流入电网的 summation current；与公共方向正交的 \(n-1\) 个方向描述 converter 之间的 difference currents。用这组方向作为坐标，原非对角 plant 可以被对角化为一个含 \(Z_L+nZ_g\) 的 summation plant 与 \(n-1\) 个只含 \(Z_L\) 的 difference plants。[pdf:E03][pdf:E04]（p003，Eq. (3)–(4)；p004，Eq. (5)–(7)）

第三步，重新解释 conventional control 的失败。传统做法给每台 converter 同一个 regulator；换到 SD 坐标后，虽可看见 sum/difference modes 已分开，但同一个 regulator 同时面对两个截然不同的 plant。按 \(Z_L\) 整定会牺牲 sum mode 带宽，按 \(Z_L+nZ_g\) 整定又会把 difference mode 推向不稳定。[pdf:E04][pdf:E05]（p004，Eq. (8)–(10) 与 Fig. 2；p005，Eq. (11)–(12) 与 Fig. 3）

第四步才自然得到控制 idea：既然 plant 的自然 modes 不同，就不要在物理 converter 坐标里复用一个 regulator，而应在 modal coordinate 中分别闭环，再做 inverse transform 把控制电压分配回各机。这一路径与 motor vector control 的相似处不是公式相同，而是都先寻找能解耦物理作用的坐标，再分别调节各 mode。[pdf:E06][pdf:E07]（p006，Fig. 4 与 Eq. (13)–(14)；p007，Section IV-B）

## § 4 — 核心 Intuition

多台并联 converter 的耦合，本质上可分成“所有电流一起变化”的 sum mode 与“converter 之间相对变化”的 difference modes；这两类 mode 看到的阻抗不同。[pdf:E03][pdf:E04] 不应让同一组 PI gains 同时迁就两类对象，而应先把测量和 reference 变换到 SD 坐标，各自闭环，再把 voltage commands 逆变换回每台 converter。[pdf:E06] 这样做的收益来自对称 plant 的 modal decoupling，而不是增加 damping hardware 或提高单个 regulator gain。

## § 5 — 具体方法与完整 Pipeline

以四台并联 converter 为例，完整信号路径如下。

1. 输入是每台 converter 的 current reference \(i_k^*\)、采样电流 \(i_k\) 和 PLL 给出的电网相角 \(\theta\)。用 \(T_{\mathrm{SD}}\) 把四个 reference 与四个采样量分别变为一个 \(i_{\mathrm{sum}}\) 和三个 difference currents \(i_{1m2},i_{1m3},i_{1m4}\)。sum mode 表示总注网电流，difference modes 表示第一台与其余各台之间的相对电流。[pdf:E03][pdf:E06]（p003，Eq. (3)–(4)；p006，Fig. 4）
2. 每个 mode 再做 \(abc/dq\) 变换。summation-current loop 使用针对 \(L+nL_g\) 整定的 \(PI_{\mathrm{sum}}\)，每个 difference-current loop 使用针对 \(L\) 整定的 \(PI_{\mathrm{dif}}\)；Fig. 4 还画出了相应的 \(dq\) cross-coupling compensation。[pdf:E06]（p006，Fig. 4 与 Eq. (14)）
3. 各 mode 输出形成 \(u_{\mathrm{sum}},u_{1m2},u_{1m3},u_{1m4}\)，再经 \(T_{\mathrm{ISD}}=T_{\mathrm{SD}}^{-1}\) 得到每台 converter 的 \(u_1,\ldots,u_4\)。每台 converter 最后独立执行 SVPWM 并输出 gate signals。[pdf:E06]（p006，Fig. 4 与 Eq. (13)）
4. 同址且台数不大时，作者建议在一个 DSP/FPGA-based controller 上完成全部变换和控制；异地时可用一个 master 控制 sum loop、多个 slaves 控制 difference loops，并通过 EtherCAT 或高速光纤交换信息。作者要求所有控制器同步，且通信与算法必须在一个 control period 内结束，否则额外 delay 会同时降低 bandwidth 和 stability。[pdf:E07]（p007，Section IV-C）

实际实验没有使用 FPGA，而是用一颗 TMS320F28377D DSP 控制四台 converter；FPGA 仅被作者列为可扩展 I/O 的实现选项。论文未报告 fixed-point/浮点数值表示、FPGA pipeline、资源占用、时钟频率、worst-case execution time、时序收敛或 bit-accurate 验证。[pdf:E07][pdf:E08]（p007，Section IV-C 与 Fig. 6；p008，Table III 前的 prototype 描述）

从 EMT + FPGA 资产视角看，论文也未报告开关事件处理、network time stepping、多速率调度、实时步长或 FPGA 上的电磁暂态 plant mapping。它控制的是实物 converter，不是把电网/变换器模型映射成 FPGA 实时仿真器；因此不能从本文外推其方法能提高 EMT 仿真吞吐量。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的形式化推导。先在 Laplace domain 中写成

\[
\mathbf I(s)=\mathbf Y(s)\bigl(\mathbf U(s)-u_g(s)\mathbf E\bigr),
\]

其中 \(\mathbf Y\) 的 diagonal elements 为

\[
Y_1=\frac{Z_L+(n-1)Z_g}{Z_L(Z_L+nZ_g)},
\]

off-diagonal elements 为

\[
Y_2=\frac{-Z_g}{Z_L(Z_L+nZ_g)}.
\]

这里 \(\mathbf I=[i_1,\ldots,i_n]^T\) 是各机输出电流，\(\mathbf U=[u_1,\ldots,u_n]^T\) 是各机控制电压，\(u_g\) 是 grid voltage，\(\mathbf E\) 是 unit column vector，\(Z_L\) 与 \(Z_g\) 分别表示单机 filter branch impedance 与公共 grid impedance。这表明 \(Z_g=0\) 时矩阵退化为 diagonal；而 \(Z_g\neq0\) 时，每台 converter voltage 都会经 \(Y_2\) 影响其他机电流。[pdf:E03]（p003，Eq. (2)）

SD transformation 取

\[
T_{\mathrm{SD}}=
\begin{bmatrix}
1&1&\cdots&1\\
1&-1&\cdots&0\\
\vdots&\vdots&\ddots&\vdots\\
1&0&\cdots&-1
\end{bmatrix},
\qquad
\mathbf I_{\mathrm{SD}}=T_{\mathrm{SD}}\mathbf I
=
\begin{bmatrix}
i_{\mathrm{sum}}&i_{1m2}&\cdots&i_{1mn}
\end{bmatrix}^{T}.
\]

第一行提取公共 sum mode，后续各行提取相对 difference modes。[pdf:E03]（p003，Eq. (3)–(4)）其 inverse transform 为

\[
T_{\mathrm{ISD}}=\frac{1}{n}
\begin{bmatrix}
1&1&\cdots&1\\
1&1-n&\cdots&1\\
\vdots&\vdots&\ddots&\vdots\\
1&1&\cdots&1-n
\end{bmatrix}.
\]

[pdf:E04]（p004，Eq. (5)）

左乘 \(T_{\mathrm{SD}}\) 后，plant 被对角化，且只有两种 distinct admittances：

\[
Y_{\mathrm{sum}}(s)=\frac{1}{Z_L(s)+nZ_g(s)},\qquad
Y_{\mathrm{dif}}(s)=\frac{1}{Z_L(s)}.
\]

所以 sum loop 必须推动“filter + \(n\) 倍 grid impedance”，difference loops 却只看到 filter branch。这就是一个 regulator 无法兼顾两类 mode 的数学原因。[pdf:E04]（p004，Eq. (6)–(7)）

conventional design 的两种极端整定为

\[
k_{pI}=\frac{L}{3T_s},\quad k_{iI}=\frac{R_L}{3T_s},
\]

\[
k_{pII}=\frac{L+nL_g}{3T_s},\quad
k_{iII}=\frac{R_L+nR_g}{3T_s}.
\]

其中 \(L,R_L\) 是 filter inductor 的 inductance 与 resistance，\(L_g,R_g\) 是 grid impedance 的 inductive 与 resistive parts，\(T_s\) 是 PWM/control period；作者按每个 PWM period 执行一次控制，并在分析中采用 \(1.5T_s\) control delay。前者适合 difference plant，却让 sum loop 太慢；后者适合 sum plant，却可能使 difference loop 失稳。文中算例的 conventional sum-loop bandwidth 只有 \(591.7\ \mathrm{rad/s}\)，另一种整定则使 difference loop 不稳定。[pdf:E05]（p005，Eq. (11)–(12) 与 Fig. 3）

所提方法把两组比例增益直接分开：

\[
k_{p,\mathrm{sum}}=\frac{L+nL_g}{3T_s},\qquad
k_{p,\mathrm{dif}}=\frac{L}{3T_s}.
\]

逆变换再按 Eq. (13) 把 modal voltages 分配到各物理 converter。作者的 Bode analysis 报告两类 loop 在所提设计下达到相同控制特性，bandwidth 为 \(14951\ \mathrm{rad/s}\)，phase margin 为 \(61.4^\circ\)。[pdf:E06]（p006，Eq. (13)–(14) 与 Fig. 5 的正文说明）

上述推导成立的关键并不是 \(T_{\mathrm{SD}}\) 本身“总能解耦”，而是 \(\mathbf Y\) 具有相同 diagonal/off-diagonal elements 的对称结构；一旦各 branch 的 \(L\)、delay 或 controller dynamics 不同，固定 \(T_{\mathrm{SD}}\) 一般不再是精确 eigenbasis。这一点是基于 Eq. (2)–(7) 与作者限制说明作出的推断。[pdf:E03][pdf:E04][pdf:E11]

## § 7 — 实验设计与结论

**问题 1：常规方法是否真的存在 bandwidth–stability trade-off？** 作者搭建四台 \(2\ \mathrm{kW}\) 三相 two-level converters：grid voltage \(190\ \mathrm{V}\)，dc voltage \(320\ \mathrm{V}\)，实测 filter inductance \(1.8\ \mathrm{mH}\)，grid inductance \(5\ \mathrm{mH}\)，并联系统所对应的放大值为 \(20\ \mathrm{mH}\)；switching 与 control frequency 都是 \(20\ \mathrm{kHz}\)。四机由 TMS320F28377D 控制。[pdf:E07][pdf:E08]（p007，Section V-A；p008，Table III 及相邻正文）conventional PI 取 \(k_p=12,20,28\) 三组。\(k_p=12\) 时低频谐波明显，\(k_p=20\) 时 THD 从 \(5.34\%\) 降到 \(4.50\%\) 但仍有低频谐波，\(k_p=28\) 时出现约 \(3.3\ \mathrm{kHz}\) 的交互振荡，THD 为 \(7.17\%\)。答案是：在该弱网四机工作点，单纯提高共同 gain 不能同时解决慢响应与高频失稳。[pdf:E08][pdf:E09]（p008，Fig. 7 与正文；p009，Fig. 8）

**问题 2：分开的 sum/difference regulators 能否改善稳态电流质量？** 所提方法把 sum-loop 与 difference-loop 的 proportional gains 分别设为 \(130\) 和 \(20\)。四机 Phase-A currents 与单机三相电流保持稳定，#1 converter 的 Phase-A current THD 为 \(2.87\%\)；作者还指出除 switching frequency \(20\ \mathrm{kHz}\) 附近外，\(1\)–\(10\ \mathrm{kHz}\) 内没有其他高频谐波。答案是：在这一个原型工作点，所提控制得到比三组 conventional gains 更低的 THD，且未复现 conventional 高增益下的交互峰。[pdf:E08][pdf:E09]（p008–p009，Fig. 9 与相邻正文）

**问题 3：动态响应是否改善？** 作者把 #4 converter 的 q-axis reactive-current reference 从 \(0\) 阶跃到 \(-10\ \mathrm{A}\)。conventional 方法的 response time 接近 \(10\ \mathrm{ms}\)，所提方法不超过 \(3\ \mathrm{ms}\)。答案是：在相同硬件上，modal control 的该次阶跃响应明显更快。[pdf:E09]（p009，Fig. 10 与相邻正文）

**问题 4：各机输出功率不同时是否仍工作？** 四机 dc-link references 被设为 \(310,320,340,360\ \mathrm{V}\)，且 dc load 都为 \(50\ \Omega\)，由此形成不同功率。Fig. 12 展示了稳定的四机 Phase-A currents。答案是：相同/相似 branch hardware 并不要求各机功率相同。[pdf:E09][pdf:E10]（p009–p010，Fig. 11–12 与正文）

**问题 5：grid impedance 与 phase jump 变化时怎样？** 仿真把 \(L_g\) 从 \(1\) 扫到 \(6\ \mathrm{mH}\)；所提方法的响应随 \(L_g\) 增大而变慢，但作者仍判断整体响应足够快。另一个仿真令 grid-voltage phase 跳变 \(30^\circ\)，四机电流出现 overshoot 后在 \(20\ \mathrm{ms}\) 内恢复。[pdf:E10]（p010，Fig. 13–14）这两项是 simulation，不是实验；论文也未给 grid-impedance estimation error、通信 delay sweep、filter mismatch sweep 或更大并联台数的验证，不能外推为任意弱网与任意异构系统下都稳定。

## § 8 — Take-aways

**5 句话。** 第一，多并联 converter 的公共 grid impedance 把物理机坐标下的独立电流环变成 MIMO coupling。[pdf:E03] 第二，对称系统可分解为一个 sum mode 与 \(n-1\) 个 difference modes，它们分别看到 \(Z_L+nZ_g\) 与 \(Z_L\)。[pdf:E04] 第三，conventional common regulator 的根本矛盾是同一组 gains 同时面对这两个不同 plant。[pdf:E05] 第四，在 SD 坐标分别整定并逆变换回各机后，四机原型的 THD、动态响应和高频交互表现均优于文中测试的 conventional PI gains。[pdf:E08][pdf:E09] 第五，收益依赖 branch filters 相同或很相似、控制同步且 delay 近似一致，这个边界决定了结果不能直接推广到异构 converter fleet。[pdf:E07][pdf:E11]

**3 句话。** 论文的关键不是发明更强的 PI，而是把控制对象换到正确的 modal coordinates。其四机实验支持“同构、同步、弱网并联”条件下可同时改善 bandwidth 与 stability，但对 heterogeneous filters 与 distributed delay 没有闭合验证。[pdf:E08][pdf:E11] 对 FPGA/EMT 而言，本文提供的是可并行的控制结构启发，不是已验证的 FPGA 实现或实时仿真方案。

**1 句话。** 先把多机耦合分成 sum/difference modes 再分别闭环，能化解共同 PI 的 bandwidth–stability trade-off，但精确 decoupling 的代价是强同构与同步假设。

## § 9 — 最脆弱的假设

最脆弱的假设是：所有并联 branch 具有相同或非常相似的 filter/control plant，并且控制执行同步、没有额外差异 delay。作者明确说，若多台 converter 的 filters 不同，当前方法不能完成 decoupling；论文只证明相同或很相似 filters 的情形。分布式实现也要求通信和计算在一个 control period 内完成，否则 stability 与 bandwidth 都会下降。[pdf:E07][pdf:E11]（p007，Section IV-C；p011，Section VI 第 4 点）

失败机制可以从推导直接看出。固定 \(T_{\mathrm{SD}}\) 能对角化的是“所有 diagonal terms 相同、所有 off-diagonal terms 相同”的 \(\mathbf Y\)；filter inductance tolerance、磁芯随电流的非一致 saturation、sensor/actuator delay 或异步 PWM 会破坏这个结构，使 sum/difference channels 重新出现 off-diagonal coupling。[pdf:E03][pdf:E04] 这不是边缘情况：原型正文已经报告名义 \(2\ \mathrm{mH}\) 的滤波电感在额定条件下实测降为 \(1.8\ \mathrm{mH}\)，说明 operating-point-dependent inductance 确实存在；但论文没有报告四个 branch 各自的偏差分布。[pdf:E08]（p008，prototype 参数说明）

论文提供了不同 dc-link references/不同功率下的实验，这说明“功率不相同”本身未破坏该原型；但它不能替代 filter mismatch 或 delay mismatch 验证。[pdf:E09][pdf:E10] 因而最关键的未决问题不是 nominal performance，而是 decoupling 对 plant heterogeneity 的容差有多小。

## § 10 — 最小复现实验

一周内最小可证伪复现可以用 MATLAB/Simulink 或任一可记录内部 modal signals 的 averaged \(dq\) model，不必先搭四套功率硬件。

1. 复现四 branch、公共 \(L_g\) 的模型，采用论文工作点：\(n=4\)、每 branch \(L=1.8\ \mathrm{mH}\)、\(L_g=5\ \mathrm{mH}\)、control period \(T_s=50\ \mu\mathrm{s}\)，并分别实现 common-PI control 与 \(T_{\mathrm{SD}}/T_{\mathrm{ISD}}\) control。[pdf:E08]（p008，Table III 与 prototype 正文）
2. 做论文同类的 \(0\rightarrow-10\ \mathrm{A}\) q-axis reference step，记录 settling/response time、四机差流峰值、Phase-A current THD，以及 \(1\)–\(10\ \mathrm{kHz}\) spectrum。论文基线是 conventional 接近 \(10\ \mathrm{ms}\)、所提方法不超过 \(3\ \mathrm{ms}\)，所提方法 THD \(2.87\%\)。[pdf:E09]（p009，Fig. 9–10）
3. 在 nominal case 通过后，只增加一个证伪变量：令四个 filters 分别偏离 nominal 的 \(0,\pm5\%,\pm10\%,\pm20\%\)，再重复阶跃，并计算从 sum reference 到 difference-current outputs 的 cross-transfer。这里的 mismatch levels 与 cross-transfer metric 是复现实验设计，不是论文报告数字。
4. 支持核心 claim 的最低结果是：在 zero-mismatch baseline 中复现更快的 sum response，且 difference currents 不出现 conventional high-gain case 的 \(3.3\ \mathrm{kHz}\) interaction peak。[pdf:E08][pdf:E09] 若轻微且现实的 branch mismatch 就使 difference-current peak、THD 或 stability margin 恶化到与 conventional method 同量级，则“该固定坐标能在实际模块化系统中稳健解耦”的扩展解释被反驳，即使 nominal case 仍能复现。

这个实验的价值在于同时验证作者已展示的 nominal mechanism 和论文没有回答的 tolerance boundary，而不需要复刻完整 \(2\ \mathrm{kW}\times4\) 硬件。

## § 11 — 最强反例设计

最强反例是构造“名义相同、运行中实际电感不同”的四机系统，而不是简单把 grid impedance 调得更大。可让四个 nominally identical inductors 具有不同 saturation curves，并给各机不同 dc-link reference，使电流工作点变化后各 branch 的 incremental inductance 分离；再叠加一个 slave controller 的一拍 communication delay。该场景同时针对论文最核心的 matrix symmetry 与 synchronous-delay 假设，而且与原型已经观察到的 inductance saturation 及作者提出的 master–slave 实现直接相关。[pdf:E07][pdf:E08][pdf:E11]

攻击判据是：先用 measured small-signal plant 计算 \(T_{\mathrm{SD}}\mathbf YT_{\mathrm{ISD}}\) 的 off-diagonal terms，再在同一工作点做 sum-reference step。如果 fixed SD control 产生持续 difference-current oscillation、某一 branch 过流，或其 stability margin 低于 conventional robustly tuned control，就出现了具体替代解释：nominal 实验的收益来自高度对称的 prototype，而不是固定 SD basis 对现实模块差异具有鲁棒性。

这个反例若失败，也就是在显著 plant/delay mismatch 下 off-diagonal coupling 仍小且动态优势保留，才会真正增强论文对工程可部署性的证据；原文目前没有这项结果。

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty：**把“固定 SD 坐标下的精确 decoupling”改写为“面向异构、时变 converter fleet 的在线 modal subspace control”。未满足需求来自 §9：实际 filters、delays 和 operating points 不会永久相同，而固定 \(T_{\mathrm{SD}}\) 只对特定对称矩阵精确。

研究目标不再是给 sum/difference loops 各放一组固定 PI，而是在线估计小信号 port-admittance matrix 的 dominant common mode 与 dangerous relative modes，用 generalized eigenvalue decomposition 或 graph/modal identification 生成随工况变化的低维 basis；控制器只对可可靠辨识的 modes 做 coordinated control，其余 uncertainty 交给 robust local loops。可借鉴的相邻工具包括 power-system modal identification、graph signal processing、robust MIMO control 与 distributed clock/delay estimation。

它可能产生本领域认可的价值，是因为评价对象会从“一个高度对称四机台架的性能提升”变成“heterogeneous modular fleet 在参数漂移、通信延迟与故障重构下仍有可证明的 stability margin”，同时要求实时计算与实验原型闭合。FPGA 可以在这里承担并行矩阵变换、在线 estimator 和多 loop scheduling，但必须报告 fixed-point error、resource、latency 和 timing closure；本文没有提供这些证据。

第一个证伪实验应使用 §11 的 saturation/delay mismatch 场景，对比 fixed SD、候选 adaptive modal control 与保守 conventional/robust baseline。若在线 basis 在参数跃迁后一到两个控制周期内不能压低 off-diagonal modal gain，或其估计噪声导致的 margin 损失大于 fixed SD 的收益，就否决该方向。它与本文的实质区别是：本文依赖已知、固定、对称的 branch model 来获得 exact decoupling；候选方向把 heterogeneity 与 basis uncertainty 本身设为研究对象。由于本任务严格 PDF-only、未检索本文之后的相关工作，这一方向只能标为候选，不能宣称新颖性。
