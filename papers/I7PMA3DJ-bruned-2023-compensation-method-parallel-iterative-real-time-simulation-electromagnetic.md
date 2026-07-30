# Compensation Method for Parallel and Iterative Real-Time Simulation of Electromagnetic Transients

- 作者：Boris Bruned，Jean Mahseredjian，Sebastien Dennetière，Julien Michel，Marco Schudel，Nicloas Bracikowski（按 PDF 作者行拼写）[pdf:E01]
- 出处：*IEEE Transactions on Power Delivery*，Vol. 38，No. 4，pp. 2302–2310
- 年份：2023
- DOI：10.1109/TPWRD.2023.3238422
- Zotero key：C5M2TBJ5
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的实时 EMT 瓶颈：网络方程必须在每个很小的 time-step 内完成，而电力电子器件、换流器和变压器饱和又会引入开关或非线性，使矩阵更新、重分解和迭代集中在最忙的 CPU core 上。传统的 line-delay 并行化只有在线路传播延迟大于仿真步长时，才能无精度损失地把网络拆成彼此独立的子网；短配电线路和 HVDC 换流站内部通常没有这样的自然延迟。插入人工延迟虽然能强制解耦，却会引入数值误差，甚至不稳定。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

论文的直接目标是：在没有可用 line-delay 的位置，用 Compensation Method（CM）切开零阻抗连接支路，把网络求解并行化；再把原本面向线性网络的 CM 扩展为 iterative CM，使二极管、IGBT 开关状态和变压器非线性分段能在同一个 time-point 内反复更新直至收敛。作者把这一 claim 放在配电网、LCC-HVDC、VSC-HVDC，以及带真实控制保护装置的 HIL 场景中验证。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

工程价值不只是“多用几个核”。真正有价值的是缩短最忙 core 的执行时间，使给定模型能在固定实时步长内不 overrun，同时避免人工延迟改变原网络。论文展示的是 CPU/shared-memory 实时仿真证据，不是 FPGA 证据；因此它可以为 EMT 求解器的并行分解和迭代调度提供方法依据，但不能直接支持 FPGA resource、pipeline latency 或确定性 WCET 结论。[pdf:E05][pdf:E06][pdf:E07]（PDF 物理页 5–7，平台与 HIL 设置）

## § 2 — 前人工作与不足

论文把既有路线分成四类。第一类是 natural line-delay：当线路或电缆传播延迟不小于 time-step 时，网络可以自然拆分，且不损失精度；但配电网短线路和换流站内部常常没有足够延迟。第二类是 artificial delay 或 stubline：它强行制造一个 time-step 的延迟，代价是附加虚拟电容等数值扰动，可能降低精度或稳定性。第三类是把矩阵变成 Bordered Block Diagonal（BBD）形式的分解方法；论文指出，涉及开关拓扑或非线性时，反复 matrix re-factorization 会削弱这类方案的适用性。第四类是经典 CM；Dommel、Tinney、Alsac 等工作奠定了补偿法，作者此前的工作 [15] 已把 CM 用于含开关的线性实时 EMT 网络，但还没有处理必须迭代更新的非线性状态。[pdf:E01][pdf:E09]（PDF 物理页 1，Introduction；物理页 9，Refs. [10]–[17]）

Appendix 还把 CM 放到更宽的 delay-free decomposition 谱系中：MATE 被解释为源自 CM 的线性网络方法，SSN 用于 state-space 方程或 solver 的并行化，CM/SBBD 则给出一个带物理端口含义的解释。[pdf:E08][pdf:E09]（PDF 物理页 8，Appendix；物理页 9，Refs. [27]–[30]）不过，本文没有报告与 MATE、SSN 或其他 nonlinear domain-decomposition solver 的同平台定量比较，也没有给自动 cut selection 的实验；这些不是“效果不好”，而是论文未报告的比较范围。

本文真正补上的缺口，是让 CM 的补偿电流求解进入 Newton/分段线性化迭代，并把子网任务、补偿任务和收敛标志组织成可在共享内存 CPU 上执行的 barrier protocol。它不是发明 CM、BBD、Thevenin 等值或 Newton 法，而是把这些机制组合成一个能跑实际 nonlinear EMT/HIL case 的实时并行执行方案。[pdf:E02][pdf:E03][pdf:E04]（PDF 物理页 2–4，Section II 与 Fig. 2）

## § 3 — 重建作者的思考路径

以下是基于论文证据重建的合理推断，不是作者逐字陈述。

第一步，研究者会先观察到 line-delay 的优点与硬边界：它解耦干净，但必须等待真实传播延迟；短线路和换流站内部不满足条件。第二步，会转向 CM：沿零阻抗 wire branch 切开网络，各子网独立形成 Thevenin 响应，再用一个小的补偿边界问题恢复切开前的同时解。这样可以把大矩阵重分解变成若干小矩阵重分解。[pdf:E01][pdf:E02]（PDF 物理页 1–2，Introduction、Fig. 1 与 Eqs. (1)–(7)）

第三步，线性 CM 遇到二极管、IGBT 或饱和电感时会失效，因为一次补偿后得到的新电压可能改变开关状态或分段线性区间；此时 Norton resistance、Norton current 以及 Jacobian 必须重新构造。作者据此把“补偿一次”改成“在同一 time-point 内补偿—更新状态—再补偿”，直到所有相关子网都不再改变 nonlinear segment。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Section II-A）

第四步，为了把数学迭代变成真实并行程序，需要明确同步协议。每个子网一个 task，另有一个 compensation task；前两个 barriers 用于收集 Thevenin 等值和广播补偿解，第三个 barrier 汇总 IterFlag，纯线性子网还可以在迭代期间挂起，避免重复计算。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Section II-B 与 Fig. 2）最后，研究者会挑选“重分解很多、最忙 core 容易超时”的场景来检验收益，因为小子网重分解越频繁，CM 相对单体或只用 LD 的潜在收益越大；论文在换流器 commutation 和 transformer saturation 实验中正是这样解释性能提升。[pdf:E06][pdf:E08]（PDF 物理页 6、8，Figs. 9、19 邻近正文）

## § 4 — 核心 Intuition

CM 的核心直觉是：先把连接子网的理想 wire 暂时“剪开”，并行求出各子网从接口看进去的 Thevenin 响应；随后只解一个小得多的接口补偿电流问题，再把这个电流造成的电压贡献叠加回各子网，就恢复原网络的同时解。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Eqs. (3)–(7)）

Iterative CM 只多加一个关键动作：若补偿后的电压改变了开关状态或非线性分段，就在同一仿真时刻更新 Norton 等值并重做补偿，直到所有相关 task 一致认为不再需要迭代；不含非线性的子网可以等待，从而把计算集中在真正变化的区域。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Case-1/Case-2 与 Fig. 2）

## § 5 — 具体方法与完整 Pipeline

论文的输入是一个经 EMT 离散后得到的 nodal network：每个候选子网有 admittance matrix \(Y_i\)、内部 current right-hand side \(i_i\)，切口由 connectivity matrix \(S_i\) 表示；非线性器件在当前 operating point 上表示为 Norton resistance 与 Norton current。对于开关器件，闭合和断开分别用小电阻 \(R_{\mathrm{on}}\) 与大电阻 \(R_{\mathrm{off}}\) 表示，检测到开关状态变化时触发迭代。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Section II-A）

完整 pipeline 如下：

1. **离线/建模阶段选切口。** 先用自然 line-delay 做第一层拆分，再在没有足够 line-delay 的子网中人工选择 CM cuts。本文的 cut identification 仍是人工完成；每个切分后的子网分配一个 task，另设一个 compensation task，每个 task 映射到一个 CPU thread/core，线程间通过 shared memory 通信。[pdf:E03]（PDF 物理页 3，Section II-B）
2. **进入一个 time-point。** 根据当前开关状态和非线性分段，更新 \(Y_i\) 与 \(i_i\)。如果可以，分段线性化可预先计算；否则在当前 operating point 更新 Norton 等值。[pdf:E02]（PDF 物理页 2，Eq. (2) 邻近正文）
3. **并行求子网自由响应。** 保持切口开路，各子网并行计算内部源产生的电压贡献 \(\hat b_i\)，并通过 unit-current injection 计算接口响应 \(C_i\)。补偿 task 汇总这些结果，形成接口 Thevenin voltage 与 impedance。[pdf:E02]（PDF 物理页 2，Eqs. (4)–(5)）
4. **解接口补偿。** compensation task 解 \(C_m i_m=\hat b_m\)，得到 compensation/interface current \(i_m\)，再广播给各子网；各子网并行做电压叠加 \(v_i=\hat b_i-C_i i_m\)。[pdf:E02]（PDF 物理页 2，Eqs. (6)–(7)）
5. **检查非线性一致性。** 用更新后的 \(v_i\) 重算开关状态或 nonlinear segment，并设置 IterFlag。任一参与迭代的子网发生 segment change，就更新矩阵和右端项并回到步骤 2；全部稳定后才推进到下一个 time-point。纯线性子网的 Thevenin 等值在一个 time-step 内不变，可以在迭代期间挂起。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Section II 与 Fig. 2）
6. **输出。** 得到本 time-point 的节点电压、支路电流和器件状态，再按固定步长前进。论文使用 LU sparse decomposition 求上述线性系统。[pdf:E03]（PDF 物理页 3，Section II-A 开头）

以 Eleclink VSC-HVDC 为真实例子：系统是 Siemens MMC 技术的 \(1000\ \mathrm{MW}\) symmetrical monopole，DC 电压为 \(\pm320\ \mathrm{kV}\)；长 DC cable 先用 LD 拆开两站，MMC 的 AC side 再用 CM 切分，IGBT 表示中的 nonlinear diode 触发迭代。离线启动实验设 \(500\ \mathrm{MW}\) 法国到英国功率流、\(10\ \mu s\) time-step，LD+CM 使用 7 cores、LD 使用 5 cores；HIL 中则由真实控制保护 replica 替代 Simulink 控制。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Section III-C、Figs. 10、13、14）

领域验收中的未报告项需要明确保留：论文没有报告 multirate time advancement；没有报告数值格式是 single/double/fixed-point、量化误差或 mixed precision；没有 FPGA、HLS/RTL、DSP/BRAM/LUT、pipeline、on-chip memory banking 或 device clock 数据；也没有给实时 scheduler 的形式化 WCET。实际平台是 OP5031 Linux target 上的 Intel Xeon 多核 CPU，算法依靠 shared-memory threads 与 barriers。[pdf:E03][pdf:E05][pdf:E06]（PDF 物理页 3、5、6，task mapping 与 Arch1/Arch2）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的形式化数学。基础是 nodal analysis：把所有节点电压和接口电流装入未知量 \(x\)，网络写成

\[
A x=b. \tag{1}
\]

切开 \(n\) 个子网后，矩阵成为 BBD 形式。用 \(S=[S_1,\ldots,S_n]\)、\(v=[v_1^\top,\ldots,v_n^\top]^\top\)、\(i=[i_1^\top,\ldots,i_n^\top]^\top\) 简写，论文 Eq. (2) 可读作

\[
\begin{bmatrix}
\operatorname{diag}(Y_1,\ldots,Y_n) & S^\top\\
S & 0
\end{bmatrix}
\begin{bmatrix}
v\\ i_m
\end{bmatrix}
=
\begin{bmatrix}
i\\ 0
\end{bmatrix}. \tag{2}
\]

\(Y_i\) 是第 \(i\) 个子网的 nodal admittance matrix，\(S_i\) 在切口两侧节点分别放 \(+1\) 与 \(-1\)，\(i_m\) 是理想 wire 中待恢复的 interface/compensation current。非线性情形下，\(A\) 是当前迭代点的 Jacobian；器件被线性化成写入 \(Y_i\) 的 Norton resistance 与写入 \(i_i\) 的 Norton current。[pdf:E02]（PDF 物理页 2，Eqs. (1)–(2) 与变量定义）

作者通过行变换把 Eq. (2) 写成 SBBD 形式。保持切口开路后，Eq. (4) 计算内部源产生的 \(\hat b_i\)，Eq. (5) 用 unit-current injection 计算边界列 \(C_i\)；最后一行分别聚合所有子网的 Thevenin voltage 和 impedance，形成 \(\hat b_m\) 与 \(C_m\)。接口问题和电压恢复是

\[
C_m i_m=\hat b_m, \tag{6}
\]

\[
v_i=\hat b_i-C_i i_m,\qquad i\in\{1,\ldots,n\}. \tag{7}
\]

第一式只解边界补偿电流；第二式是 superposition：\(\hat b_i\) 是内部源贡献，\(-C_i i_m\) 是补偿电流注入贡献。[pdf:E02]（PDF 物理页 2，Eqs. (3)–(7)）

对于两个子网、三相切口的例子，作者进一步把 SBBD 量还原为物理 Thevenin 等值：

\[
(S_1C_1,-S_1\hat b_1)=(Z_{\mathrm{th1}},v_{\mathrm{th1}}),\qquad
(S_2C_2,S_2\hat b_2)=(Z_{\mathrm{th2}},v_{\mathrm{th2}}), \tag{9}
\]

\[
\hat b_3=v_{\mathrm{th2}}-v_{\mathrm{th1}},\qquad
C_3=Z_{\mathrm{th1}}+Z_{\mathrm{th2}},\qquad
i_3=i_c. \tag{10}
\]

因此两侧电压分别由各自自由响应和 \(i_c\) 的注入响应叠加得到，即 Eq. (11) 的 \(\hat b_1-C_1i_3=v_{n1}+v_{1C}\) 与 \(\hat b_2-C_2i_3=v_{n2}+v_{2C}\)。这说明 CM 不是用延迟近似跨区耦合，而是在当前 time-point 解一个小的边界问题来恢复零阻抗连接条件。[pdf:E03]（PDF 物理页 3，Eqs. (8)–(11)）

实验误差使用 reference vector \(f\) 与 candidate vector \(\tilde f\) 的相对 2-norm：

\[
e_{\%}=100\frac{\lVert\tilde f-f\rVert_2}{\lVert f\rVert_2}. \tag{12}
\]

SEQ 或纯 LD 是 reference，DB 或含 CM 的解是 candidate。[pdf:E03]（PDF 物理页 3，Eq. (12)）

论文没有给出 \(C_m\) 可逆性、condition number 上界、Newton contraction 条件、最大 iteration count 或 barrier 后的 WCET 证明。作者明确说测试 case 没遇到 convergence problem，但 divergence detection、segment stepping、bisection 和 prediction correction 均不在本文范围内。[pdf:E02]（PDF 物理页 2，非线性迭代说明）

## § 7 — 实验设计与结论

**问题 1：在线性配电网里，CM 能否在不插人工延迟的情况下兼顾速度与精度？** 作者用 663-node、4-feeder 的 GHOST microgrid，运行 \(90\ \mathrm{s}\)、\(100\ \mu s\) time-step 场景，包含 PV 功率阶跃、三相接地故障、孤岛和负荷切除；比较 SEQ、DB 和 CM。[pdf:E04]（PDF 物理页 4，Section III-A 与 Fig. 3）Table I 报告：SEQ/DB/CM 分别使用 2/5/5 cores；offline average \(\Delta t\) 为 65/24/32 \(\mu s\)，实时 steady-state 最小无 overrun 步长为 68/29/38 \(\mu s\)，transient 时为 246/46/115 \(\mu s\)，DB 与 CM 的 transient speedup 分别为 5.35 和 2.14。[pdf:E05]（PDF 物理页 5，Table I）答案是：DB 更快，但 CM 更准确；Feeder 2 的 RMS voltage 相对误差为 \(e_{\%,CM}=5.44\times10^{-4}\)，DB 为 \(2.35\)，且 DB 的虚拟电容明显影响 reactive power。[pdf:E05]（PDF 物理页 5，Figs. 4–5 与邻近正文）

**问题 2：在线性但频繁换相的 LCC-HVDC 网络里，更细的 CM 切分能否减少重分解代价？** IFA2000 case 设 DC voltage 为 \(\pm272\ \mathrm{kV}\)、功率为法国到英国 \(200\ \mathrm{MW}\)、time-step 为 \(30\ \mu s\)。bridge-based LD+CM 的电压相对误差为 \(0.17\%\)；SIL 实时结果显示，它比 pole-based LD+CM 快 \(15\%\)，比只用 LD 快 \(47\%\)，并使原本 overrun 的 case 能实时运行。[pdf:E06]（PDF 物理页 6，Figs. 8–9 与 Section III-B）但答案有重要条件：CM 使子网矩阵 condition number 增大；Sellindge 的 bridge-based cut 发生数值不稳定，作者在两个切口附近各串联 \(10^{-10}\ \Omega\) 小电阻才处理该问题，而 pole-based cut 没有同类不稳定。[pdf:E05][pdf:E06]（PDF 物理页 5–6，Figs. 6–7 与 Section III-B）

**问题 3：iterative CM 能否处理 VSC 的二极管换相非线性，并在 SIL/HIL 中保住实时步长？** Eleclink 启动 case 中，未迭代的 LD+CM 在 diode commutation 处出现明显数值振荡；Iterative LD+CM 消除了振荡，相对误差为 \(0.013\%\)，性能相对 Iterative LD 提升 \(40\%\)，并能以 \(10\ \mu s\) time-step 实时运行，而 Iterative LD 连续 overrun。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Figs. 11–12）在接入真实 control/protection replica 的 HIL 中，作者又施加 \(150\ \mathrm{ms}\) 单相接地故障、\(1000\ \mathrm{MW}\) 最大功率传输，使用 \(30\ \mu s\) 步长；Fig. 15–16 显示 DC voltage 相近且最忙 core 性能提高 \(40\%\)。[pdf:E07]（PDF 物理页 7，Figs. 13–16）

**问题 4：复杂的 transformer saturation 分段非线性会不会破坏效果？** IFA2000 HIL case 使用 two-point saturation characteristic，功率为英国到法国 \(300\ \mathrm{MW}\)，在 \(1\ \mathrm{s}\) 内合闸，三相合闸时刻分别为 128、129、119 ms；Iterative LD+CM 用 8 cores，Iterative LD 用 5 cores，case 以 \(40\ \mu s\) time-step 无 overrun 运行。[pdf:E07]（PDF 物理页 7，Fig. 17 邻近正文）Iterative LD+CM 相对 Iterative LD 再提高 \(40\%\)，两者 DC voltage 相近；更关键的是，不让 transformer 参加迭代会因错误 segment selection 产生虚假过电压，Fig. 20–21 显示只有非迭代 LD 曲线出现巨大尖峰。[pdf:E08]（PDF 物理页 8，Figs. 18–21）

总体上，实验支持“在作者挑选的 cuts 和 CPU 平台上，iterative CM 可减少最忙 core 的执行时间，并保持与 reference 接近的波形”。实验不能外推为任意 cut、任意非线性均收敛，也不能外推到 FPGA。论文给的是若干波形、relative 2-norm error、最忙 core execution-time traces 和无 overrun 观察；未报告跨大量网络的统计、自动 cut baseline、tail-latency/WCET、FPGA resource/timing 或 bit-accurate error。

## § 8 — Take-aways

**5 句话。** 第一，CM 用当前 time-point 的边界补偿电流恢复被切开的零阻抗网络，因此避免了 artificial delay 的物理扰动。第二，iterative CM 把开关/分段状态更新放入补偿循环，使二极管、IGBT 和 transformer saturation 能参与并行 EMT 求解。第三，线性 GHOST case 表明 CM 没有 DB 快，但电压和无功精度明显更好。[pdf:E05]（PDF 物理页 5，Table I 与 Figs. 4–5）第四，VSC 与 LCC case 中，作者多次报告最忙 core 性能提高 \(40\%\)，并在真实控制 replica 的 HIL 中运行。[pdf:E07][pdf:E08]（PDF 物理页 7–8）第五，收益依赖人工 cut placement 和数值条件，且本文完全没有 FPGA 或形式化 WCET 证据。

**3 句话。** 这篇论文把经典 CM、SBBD/Thevenin 等值和 nonlinear iteration 组合成了一个可执行的 shared-memory 实时 EMT 并行方案。它在配电网和两个 HVDC 技术的 CPU/SIL/HIL case 中展示了精度—性能折中，但也暴露出 cut 导致高 condition number 和不稳定的风险。最应该继承的是“边界小系统加局部重分解”的结构，最不能继承为事实的是“任意网络都稳定、任何硬件都能达到相同实时收益”。

**1 句话。** Iterative CM 的贡献，是用小边界补偿问题协调并行子网的 nonlinear state convergence，从而在所测 CPU/HIL case 中缩短关键 core 时间，但其可扩展性与可靠性仍受人工切分和数值条件约束。[pdf:E03][pdf:E08]（PDF 物理页 3、8）

## § 9 — 最脆弱的假设

最脆弱的假设是：**用户能够选出既降低最忙 core 负载、又让所有子网与接口补偿矩阵保持良好数值条件的 CM cuts。** 这是方法能否成立的共同前提，而不是一个边缘实现细节。cut 太粗，子网仍然重、并行收益消失；cut 太细或落在不合适的网络位置，子网 admittance 或 \(C_m\) 会病态，补偿电流对舍入误差和很小的建模扰动高度敏感，迭代可能振荡、选错 segment 或直接失稳。

论文给出的正面证据，是所有正式测试 case 最终都运行并且作者称未遇到 convergence problem；同时，Case-2 可以把纯线性子网挂起，减少不必要迭代。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Section II）但论文也提供了直接反证信号：cut 仍由用户人工识别；IFA2000 bridge-based cut 把 Sellindge/Les Mandarins 子网 condition number 推高到 \(10^{23}\) 与 \(10^{10}\)，Sellindge 侧发生数值不稳定，必须在切口附近加入两个 \(10^{-10}\ \Omega\) 串联电阻；结论又明确限定为“presented test cases 中 cuts well-placed”。[pdf:E03][pdf:E05][pdf:E06][pdf:E08]（PDF 物理页 3、5、6、8）

缺失的关键证据是 automatic cut selection、condition-number/convergence bound、对同时多开关和多 nonlinear segment 的系统 stress test，以及引入小电阻后对物理 fidelity 的敏感性分析。若这个假设不成立，论文最核心的“无需人工延迟而同时保持精度和实时性”会一起失效：要么重新引入非物理扰动，要么迭代时间超过实时 deadline，要么波形本身不再可信。

## § 10 — 最小复现实验

一周内最值得做的不是重建完整 HVDC HIL，而是做一个能同时检验“同一时刻恢复耦合”和“nonlinear iteration 是否稳定”的两子网实验。

使用同一套 trapezoidal EMT discretization 建两个 RLC 子网，以三相零阻抗支路连接；一侧放 binary-resistance diode/IGBT leg，另一侧放 two-segment saturable inductance。实现两个 solver：单体 nodal Newton 作为 reference，以及按 Eqs. (4)–(7) 实现的 two-thread iterative CM；两者使用相同 time-step、相同开关事件、相同 convergence tolerance 和 double precision。CM 侧记录每步 iteration count、matrix re-factorization 次数、\(C_m\) condition estimate、最忙 thread execution time 和 Eq. (12) 波形误差。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eqs. (4)–(12)）

实验只扫三项：cut location、开关事件相对饱和分段 crossing 的时间间隔，以及切口附近串联电阻从 0 到 \(10^{-10}\ \Omega\) 的敏感性。预先规定支持标准：在所有事件后，iterative CM 与单体 reference 收敛到相同开关/分段状态，关键电压电流相对误差不高于论文 VSC case 的 \(0.013\%\)，且最忙 thread 的高分位执行时间低于单体 solver；反驳标准是任一 case 出现不同的离散状态、发散/循环、必须靠电阻扰动才能收敛，或执行时间不再有收益。这里的 \(0.013\%\) 只是取自论文的复现门槛，不是普适行业标准。[pdf:E06]（PDF 物理页 6，Fig. 11 邻近正文）

这个实验不证明真实 HIL，也不证明 FPGA；它只以最小成本验证 iterative CM 的核心机制和最脆弱的 cut-conditioning 依赖。若通过，再扩展到公开 microgrid 或 HVDC benchmark，而不是先复制整套控制 replica。

## § 11 — 最强反例设计

最强反例是构造一个**跨 CM cut 强耦合、接口近奇异、且多个 nonlinear state 在同一两个 time-step 内来回切换**的网络。具体可把弱阻尼 LC resonance 放在切口两侧，同时让多只 diode/IGBT 在零交越附近换相，并让 saturable transformers 的两个 segment 几乎同步跨越；逐步把接口等值阻抗调到使 \(C_m\) condition number 急剧升高。单体 Newton solver 与 iterative CM 使用完全相同的器件模型、步长和 tolerance，避免把模型差异误当成分解误差。

攻击成立的判据是：单体 solver 在同一事件序列下收敛且波形平滑，而 iterative CM 出现 IterFlag 循环、iteration count/重分解峰值使 deadline overrun、得到不同开关或饱和 segment，或只有加入 \(10^{-10}\ \Omega\) 级人工电阻后才稳定且波形显著改变。这个反例直接针对论文已暴露的 failure mode：bridge-based cut 曾数值不稳定，而作者未实现 divergence detection、segment stepping 或 bisection 等保护。[pdf:E02][pdf:E06]（PDF 物理页 2、6，非线性保护范围与 IFA2000 instability）

若 iterative CM 在广泛 condition-number 扫描下仍与单体解一致，并且 barrier/refactorization 峰值始终低于 deadline，这个反例就失败；那会比再增加一个普通 HIL waveform 更有力地支持方法的稳健性。

## § 12 — Follow-up Research Idea

在 EMT、电力系统和电力电子领域，高影响工作通常需要同时满足数值正确性、工程可实现性、对代表性复杂系统的验证，以及可解释的实时边界；只展示平均加速或单个漂亮 waveform 通常不够。基于本文的 cut-conditioning 缺口，一个非增量的候选方向是：**把“寻找最快的 CM cut”重定义为“编译并认证一个在指定事件集合内同时满足收敛、fidelity 与 deadline 的 decomposition contract”。** 这不是再加一个 heuristic module，而是把研究目标从平均性能改成可验证的数值—实时安全边界。

（a）未满足的需求是：人工 cut 可能把 condition number 推到 \(10^{23}\) 并触发失稳，但实时 HIL 又不能在运行后才发现；用户需要在部署前知道哪些 topology/event 组合安全。[pdf:E05][pdf:E06]（PDF 物理页 5–6）  
（b）研究价值来自把 parallel EMT 从经验调参推进到可审计的工程 contract：每个 cut 同时带有接口条件估计、允许的 nonlinear state region、最大 iteration/refactorization 预算和 deadline margin。  
（c）可借鉴相邻领域的 sparse graph partitioning、numerical linear algebra condition estimation、hybrid-system reachability，以及 real-time scheduling response-time analysis；MATE/SSN/CM 的共同边界结构可作为比较对象。[pdf:E08][pdf:E09]（PDF 物理页 8–9，Appendix 与 Refs. [27]–[30]）  
（d）第一个证伪实验是在一组含同时换相、饱和和 topology change 的公开 EMT 网络上，盲测 contract 对“不收敛、误差超限、deadline overrun”的预测；若它不能比简单 load-balanced cut 更早、更准地识别失败，或者安全保证吞掉全部并行收益，这个方向应被否决。  
（e）它与本文的实质区别是：本文由用户手工选 cut，再用若干 case 事后观察波形和执行时间；候选工作以可证伪的部署前安全声明为主要产物，并把数值稳定性和实时 deadline 作为同一个优化约束。

由于本卡按唯一 PDF 完成、没有额外检索相关工作，上述方向只能标为候选研究想法，不声称 novelty。论文也没有 FPGA 实现；若未来映射到 FPGA，必须另行建立 bit-accurate、resource、clock、memory conflict 与 WCET 证据，不能把本文的 Xeon CPU speedup 直接换算成 FPGA 收益。
