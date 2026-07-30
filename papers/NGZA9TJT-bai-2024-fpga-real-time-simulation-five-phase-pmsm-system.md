# FPGA-Based Real-Time Simulation of Five-Phase PMSM System for Fault Tolerant Controller-HIL Applications

作者：Hao Bai、Nan Wang、Tianxing Li、Ruiqing Ma、Fengming Ai、Gang Huang  
出处：IEEE Transactions on Industry Applications, Vol. 60, No. 6  
年份：2024  
DOI：10.1109/TIA.2024.3439490  
Zotero key：NGZA9TJT  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是一般意义上的电机离线仿真，而是一个受硬实时约束的问题：怎样把五相永磁同步电机（five-phase PMSM, FPMSM）、五相逆变器以及开相故障注入放到 FPGA 上，使真实控制器能够在 controller hardware-in-the-loop（CHIL）闭环中测试正常控制和容错控制。作者把目标同时表述为准确、低延迟和可插入故障，并报告 FPGA 模型的最小时步为 66.7 ns。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题的重要性来自两层工程矛盾。第一，实体样机实验能呈现真实工况，却在研发早期昂贵且有安全风险；纯离线仿真又不能让真实控制器与虚拟被控对象闭环交互。第二，五相系统比三相系统多出相变量、更大的坐标变换和更多功率器件，同时高次谐波与高开关频率要求更短时步，因此“模型更完整”与“每步算得更快”直接冲突。论文据此把需求收敛为：定制的 FPMSM 模型、纳秒级求解、逆变器开关细节和开相故障能力必须在同一个实时系统中成立。[pdf:E02]（PDF 物理页 2，Introduction 后半）

本文的工程价值因此不是替代最终样机，而是把控制器硬件、控制软件和 fault-tolerant strategy 的暴露时点前移。若模型在正常与故障工况下都能稳定跟随控制器命令，团队可以在电机样机尚未完成时先发现控制逻辑和接口问题；但这种价值成立的前提是 CHIL 的闭环误差、延迟和数值稳定性足够可信，不能只看“FPGA 上跑起来了”。

## § 2 — 前人工作与不足

论文把既有电机实时模型分成几条路线。FEA 与 magnetic equivalent circuit（MEC）能表达几何、材料和非线性，却与具体设计参数强绑定且实时计算成本高；线性 lumped-parameter dq 模型容易求解和提参，但对空间谐波与非线性表达有限；三维或四维 LUT 可以把电感、磁链、转矩、温升或故障电流映射进去，却可能付出过大的存储成本；neural network 可替代 LUT 以减小存储并改善泛化，但仍不是本文选择的确定性模型路线。[pdf:E01]（PDF 物理页 1，Introduction）[pdf:E02]（PDF 物理页 2，Introduction；相关工作编号 [12]–[19] 的完整书目信息见物理页 12）[pdf:E12]（PDF 物理页 12，References [12]–[35]）

对逆变器实时仿真，既有并行方法包括等效网络分区和 delay-insertion network decoupling。前者通过 Thévenin/Norton 多端口等效降低网络阶数并保持同步全局解，但逆变器与 PMSM 的等效表示成本高；后者通过在子电路边界插入一步延迟获得完全数值解耦，速度更有利，却要求专门设计来控制精度和数值稳定性。论文还指出当时商业实时仿真器的组件库没有专门的 FPMSM 模块；五相系统又必须处理 fundamental 与 third-harmonic space、更多开关器件和开相故障，因此不能直接复用普通三相 PMSM 组件。[pdf:E02]（PDF 物理页 2，Introduction）

作者声称的三个贡献是：同时建模基波与三次谐波的 FPMSM、带详细开关特性的逆变器；用 substitution theorem 加一步延迟把电机与逆变器并行化到 66.7 ns；把任意相开路故障注入 CHIL。[pdf:E02]（PDF 物理页 2，贡献列表）这里应把“作者声称填补空白”与“已完成独立 novelty 核验”区分开：本卡只基于该 PDF，未对引用文献做全文复核，因此不把 novelty 当作已独立证实的事实。

## § 3 — 重建作者的思考路径

可以从论文出现之前已知的工程线索重建出如下路径。

1. CHIL 需要真实控制器与虚拟电机驱动在固定时间内反复交换信号，因此求解延迟是硬约束；与此同时，五相电机不能把三次谐波空间删掉，否则模型会漏掉可实际流过绕组并产生 magnetomotive force 的分量。[pdf:E02]（PDF 物理页 2，FPMSM 挑战）[pdf:E04]（PDF 物理页 4，Section II-C）
2. 逆变器与电机真正跨边界耦合的是五相电压和五相电流。若把上一时步的电压交给电机、上一时步的电流交给逆变器，两个大模块可在当前时步并行求解；代价是人为引入一个采样延迟。[pdf:E03]（PDF 物理页 3，Eq. (1)–(3) 与 Fig. 1）[pdf:E04]（PDF 物理页 4，Eq. (4) 与 Fig. 2）
3. 电机内部也可以继续拆解：通过 Clark/Park 变换把 abcde 相域分成 fundamental 与 third-harmonic 两个旋转正交子空间，再用显式离散电流方程、转矩方程和机械运动方程构成固定执行路径；逆变器则拆成五个并行 half-bridge solver 与一个 DC-link capacitor 更新。[pdf:E05]（PDF 物理页 5，Eq. (8)–(14) 与 Section II-D）[pdf:E06]（PDF 物理页 6，Fig. 4 与 Fig. 6）
4. 开相故障的物理约束是故障相电流为零。于是可在逆变换得到五相电流后将故障相强制归零，再变回 dq 子空间更新转矩和历史状态，同时把对应半桥置为 blocking state。这样故障不只是输出端遮罩，而会进入下一时步的递归状态。[pdf:E07]（PDF 物理页 7，Section III-D 与 Fig. 8）

基于作者简介的合理推断是，团队的既有专长覆盖 real-time simulation、power converter、motor control 与 fault diagnosis/fault-tolerant control，这使“电机模型—逆变器—容错 CHIL”组合路线具有自然的知识来源；这不是论文对方法正确性的证据。[pdf:E12]（PDF 物理页 12，作者简介）[pdf:E13]（PDF 物理页 13，作者简介续）

## § 4 — 核心 Intuition

核心 intuition 是：不要在一个时步内顺序解完整的“逆变器 + 五相电机”耦合系统，而是把边界电压、电流各延迟一步，用 substitution theorem 把两边变成可以同时求解的独立子系统。电机侧再把五相量投影到 fundamental 与 third-harmonic 两个 dq 空间，逆变器侧再拆成五个并行半桥，从而用结构并行换取纳秒级时步。[pdf:E03]（PDF 物理页 3，Fig. 1）[pdf:E04]（PDF 物理页 4，Fig. 2）开相故障则通过“故障相电流归零并回写内部历史状态”进入递归模型，而不是只把示波输出改成零。[pdf:E07]（PDF 物理页 7，Fig. 8）

## § 5 — 具体方法与完整 Pipeline

以“真实控制器命令五相电机从正常运行进入 A 相开路”为例，完整 pipeline 如下。

1. **电机物理模型。** 目标对象是对称绕组、Y 接、非凸极 FPMSM。论文保留 fundamental 与 third-order harmonic，认为对称绕组使偶次谐波消失、五次谐波在五相系统中抵消，并忽略其余更高次谐波；相域模型由定子电压、磁链和电感矩阵组成。[pdf:E04]（PDF 物理页 4，Section II-C 与 Eq. (5)–(7)）
2. **电机—逆变器边界解耦。** 当前步的电机使用上一步逆变器五相电压，当前步的逆变器使用上一步电机五相电流。Eq. (4) 将原耦合系统拆成两个可并行更新的离散方程，Fig. 2 给出两条计算链在同一 simulation time-step 内重叠执行的时序。[pdf:E03]（PDF 物理页 3，Eq. (1)–(3)）[pdf:E04]（PDF 物理页 4，Eq. (4) 与 Fig. 2）
3. **坐标变换与电流推进。** abcde 电压先经 Clark 变换进入两个正交静止子空间，再经 Park 变换进入同步旋转的 \(d_1q_1\) 与三倍电角速度的 \(d_3q_3\) 子空间。四个电流状态用 Eq. (11) 的 forward Euler 离散式推进，之后经逆 Park/Clark 变换返回五相电流；Eq. (12) 计算电磁转矩，Eq. (14) 更新转速与转角。[pdf:E04]（PDF 物理页 4，Fig. 3）[pdf:E05]（PDF 物理页 5，Eq. (8)–(14)）
4. **逆变器推进。** MOSFET 与 diode 用 binary resistor model 表示导通小电阻和关断大电阻。直接七节点 nodal analysis 会面对 10 个开关对应的 \(2^{10}\) 种组合，因此作者把五个半桥拆开并行求解，开关状态由 PWM 与输入电流方向共同确定；DC-link capacitor 用显式积分在下一步更新，电流源旁增加 snubber resistance 以缓解过零附近数值振荡。[pdf:E05]（PDF 物理页 5，Section II-D）[pdf:E06]（PDF 物理页 6，Fig. 4）
5. **FPGA 映射。** 目标平台是 NI 7935 FlexRIO 上的 Kintex-7 XC7K410T。LabVIEW FPGA VI 自动生成 VHDL，再由 Xilinx 工具生成 bitfile。电机侧被拆成 frame transformation、current solver、inverse transformation、trigonometric LUT、torque solver 和 motion solver；作者使用 fixed-point 表示，并用 per-unit system 缩小不同电机参数范围带来的精度差异。[pdf:E06]（PDF 物理页 6，Section III-A/B 与 Fig. 5–6）
6. **开相故障。** 当 A 相故障触发，逆变换得到的 \(i_a\) 被置零，修正后的五相电流重新变换到 \(d_1q_1/d_3q_3\) 空间，用于转矩与下一步历史项；对应半桥进入 OFF/OFF blocking state。相同机制可选择一个或两个故障相。[pdf:E07]（PDF 物理页 7，Section III-C/D 与 Fig. 7–8）
7. **CHIL 闭环。** FPGA 模型输出模拟量给真实 cRIO 9038 控制器，控制器再回送门极信号；测试台还包括 NI-5741 模拟输出模块、YOKOGAWA DL850 示波器和监控电脑。论文报告 NI-5741 最大更新率 1 MS/s、16-bit，控制器采样率 50 kS/s；因此 66.7 ns 是 FPGA 内部模型时步，不等于端到端 CHIL I/O 或控制闭环采样周期。[pdf:E09]（PDF 物理页 9，Section IV-A/B 与 Fig. 10–11）

论文**未报告**：FPGA fixed-point 的具体 word length/Q-format、三角函数 LUT 深度与量化误差、各模块 pipeline stage/clock 约束、端到端 ADC/DAC 与数字接口延迟、I/O jitter 与同步机制、PWM 开关频率、DC-link 元件参数、snubber 参数，以及一步边界延迟在参数变化下的误差界。本文也不是面向电力网络的通用 EMT solver；节点导纳重构、开关事件插值、变步长、多速率 EMT 调度和大电网分区等细节均未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线可以分成“电机坐标解耦”和“系统时序解耦”两层。

首先，相域定子方程是

\[
\mathbf U_s=\mathbf R_s\mathbf i_s+\frac{d\boldsymbol\phi_s}{dt},\qquad
\boldsymbol\phi_s=\mathbf L_s\mathbf i_s+\boldsymbol\phi_m,
\]

其中 \(\mathbf U_s=[u_{as},u_{bs},u_{cs},u_{ds},u_{es}]^T\)，\(\mathbf i_s\) 和 \(\boldsymbol\phi_s\) 分别是五相电流与磁链，\(\mathbf R_s=R_s\mathbf I_{5\times5}\)。电感矩阵写成 leakage、fundamental mutual 与 third-harmonic mutual 三部分：\(\mathbf L_s=L_{ls}\mathbf I+\mathbf L_{m1}(\delta)+\mathbf L_{m3}(\delta)\)，且五相对称间隔 \(\delta=2\pi/5\)。[pdf:E04]（PDF 物理页 4，Eq. (5)–(7)）

其次，用 \(T_{\mathrm{Clark}}\) 把 abcde 量分到 \(\alpha_1\beta_1\)、\(\alpha_3\beta_3\) 与零序，再用 \(T_{\mathrm{Park}}\) 进入 \(d_1q_1\)、\(d_3q_3\)。文中 Eq. (10) 的旋转坐标电压方程为

\[
\begin{bmatrix}u_{d1}\\u_{q1}\\u_{d3}\\u_{q3}\end{bmatrix}
=R_s\begin{bmatrix}i_{d1}\\i_{q1}\\i_{d3}\\i_{q3}\end{bmatrix}
+\operatorname{diag}(L_{d1},L_{q1},L_{d3},L_{q3})
\frac{d}{dt}\begin{bmatrix}i_{d1}\\i_{q1}\\i_{d3}\\i_{q3}\end{bmatrix}
+\omega
\begin{bmatrix}
-L_{q1}i_{q1}\\
L_{d1}i_{d1}+\psi_{m1}\\
-3L_{q3}i_{q3}\\
L_{d3}i_{d3}+\psi_{m3}
\end{bmatrix}.
\]

它的工程意义是：原本五相互相耦合的微分方程变成四个可按固定矩阵计算的电流状态，三次谐波通道通过 \(d_3q_3\) 显式存在。作者用 forward Euler 把该式展开为 Eq. (11) 的 \(n\rightarrow n+1\) 更新；步长 \(h\) 同时决定离散误差和硬件每步必须完成的时间。[pdf:E05]（PDF 物理页 5，Eq. (8)–(11)）

电磁转矩与机械运动分别为

\[
T_e=\frac{5}{2}P\left(\psi_{m1}i_{q1}+3\psi_{m3}i_{q3}\right),
\]

\[
J\frac{d\omega_m}{dt}=T_e-T_L-B\omega_m,\qquad
\omega_m^{n+1}=\frac{h}{J}(T_e-T_L-B\omega_m^n)+\omega_m^n.
\]

这里 \(P\) 是 pole pairs，\(J\) 是 inertia，\(T_L\) 是负载转矩，\(B\) 是阻尼系数。第一式说明基波与三次谐波 \(q\)-axis current 都会进入转矩；第二式把电磁量推进为机械转速和转角。[pdf:E05]（PDF 物理页 5，Eq. (12)–(14)）

最后，系统级并行来自边界延迟。把逆变器状态记为 \(x_i\)、电机状态记为 \(x_m\)，文中 Eq. (4) 的结构可概括为

\[
x_i^{n+1}=f_i(x_i^n,u_i^{n+1},i_{abcde}^{n}),\qquad
x_m^{n+1}=f_m(x_m^n,u_m^{n+1},v_{abcde}^{n}).
\]

即电机和逆变器在第 \(n+1\) 步不再互相等待当前步结果，而只读取对方第 \(n\) 步边界量。这正是并行性来源，也是后文最脆弱假设的来源。[pdf:E03]（PDF 物理页 3，Eq. (1)–(3)）[pdf:E04]（PDF 物理页 4，Eq. (4)）

## § 7 — 实验设计与结论

- **问题：FPGA 数值模型是否接近商业离线模型？ → 实验：** 在 hysteresis current control 下把 \(i_{q1}\) 从 10 A 阶跃到 40 A，并令 \(i_{d1},i_{d3},i_{q3}=0\)，比较 FPGA 与 Simulink/Simscape Power Systems 的五相电流和电磁转矩。**→ 答案：** Table III 报告五相电流平均误差分别为 0.946%、0.948%、0.942%、0.941%、0.925%，转矩平均误差为 0.299%；Fig. 9 的波形也高度重合。[pdf:E08]（PDF 物理页 8，Fig. 9 与 Table III）
- **问题：能否在 FPGA 上按目标时步执行？ → 实验：** 在 Kintex-7 XC7K410T 完成综合、布局布线并检查 timing violation 与资源。**→ 答案：** 作者报告无 timing violation 的最小 execution cycle/time-step 为 66.7 ns。Table I 报告资源比例为 slices 21.6%、slice registers 4.8%、slice LUTs 15.6%、Block RAMs 1.0%、DSP48s 19.6%；但表中 “Total/Used” 两列的原始计数顺序与百分比明显不自洽，所以本卡不把那两列计数当作可靠事实。编译时间为 28 min 5 s，环境是 i7-1260P 2.10 GHz 与 NI LabVIEW 2019 SP1 32-bit。[pdf:E07]（PDF 物理页 7，Table I 与 Section III-E）
- **问题：正常闭环对负载与转速命令的响应是否合理？ → 实验：** 在 CHIL 中先保持 1000 r/min、把负载从 30 N·m 提到 50 N·m，再在 50 N·m 下把转速从 1000 r/min 提到 1700 r/min。**→ 答案：** 第一工况电流幅值从 25.65 A 增至 42.74 A；第二工况在加速瞬间增流，稳态回落，同时电流频率随转速上升。作者据此认为模型能在正常条件下正确响应控制器命令。[pdf:E09]（PDF 物理页 9，Fig. 12 与 Section IV-C）
- **问题：开相后 fault-tolerant controller 是否仍能闭环？ → 实验：** 单 A 相开路时重复负载与转速阶跃，再用相邻两相开路重复测试。**→ 答案：** 单相开路时 A 相电流为零，其余四相重构；负载阶跃下电流幅值从 35.89 A 到 59.88 A，转速阶跃后的稳态幅值相对正常工况从 42.10 A 增到 59.91 A。两相开路时仅余三相重构，论文展示其随负载和转速命令变化，并定性认为故障 CHIL 有效。[pdf:E09]（PDF 物理页 9，Section IV-D）[pdf:E10]（PDF 物理页 10，Fig. 13–14 与 Section IV-D/E）
- **问题：CHIL 能否复现真实原型趋势？ → 实验：** 另建 8-pole non-salient、650 W、96 V 的 FPMSM #2 原型，在 500 r/min、0.9 N·m 下比较正常与 A 相开路的实验波形和 CHIL 波形。**→ 答案：** Fig. 16–17 显示相电流的频率和幅值定性一致，故障时相电流幅值高于正常时；作者据此声称 CHIL 具有 effectiveness 与 fidelity。[pdf:E10]（PDF 物理页 10，Table IV、Fig. 15 与 Section IV-F）[pdf:E11]（PDF 物理页 11，Fig. 16–17、Section IV-G 与 Conclusion）

不能从这些实验外推的部分同样重要。论文没有报告 FPGA 对实体原型的逐样本误差、phase lag、THD、转矩误差或置信区间；原型对照主要依靠示波波形的幅值/频率一致性。它也没有给出 66.7 ns 内部模型步长到 1 MS/s 模拟输出和 50 kS/s 控制器之间的端到端闭环延迟、jitter 或 aliasing 分析，更没有展示 fixed-point word length、数值溢出边界、长时间稳定性、随机故障时刻或宽参数域 sweep。因此论文较强地支持“所示工况可运行且趋势吻合”，但不足以支持“任意 FPMSM、任意控制器与故障工况下均高保真”。

## § 8 — Take-aways

**5 句话：**  
1. 论文把五相 PMSM 的 fundamental 与 third-harmonic dq 模型、详细开关逆变器和开相故障注入组合成一个 FPGA CHIL 被控对象。  
2. 速度提升的核心不是删掉电机动态，而是用一步边界延迟把逆变器和电机并行，再把五个半桥继续并行。  
3. 作者在 Kintex-7 XC7K410T 上报告 66.7 ns 最小时步，并以 Simulink 对照得到不超过 0.948% 的五相电流平均误差和 0.299% 转矩平均误差。[pdf:E07]（PDF 物理页 7，Section III-E）[pdf:E08]（PDF 物理页 8，Table III）  
4. 正常、单相开路、相邻两相开路 CHIL 以及一个 650 W 实体原型对照共同说明该方法能在展示工况下驱动真实控制器并呈现合理重构电流。[pdf:E09]（PDF 物理页 9，Fig. 12–13）[pdf:E10]（PDF 物理页 10，Fig. 14–15）[pdf:E11]（PDF 物理页 11，Fig. 16–17）  
5. 论文最欠缺的是对一步延迟、fixed-point 量化和端到端 CHIL 延迟的误差/稳定性边界，而不是更多正常工况波形。

**3 句话：**  
1. 这是一套面向 fault-tolerant controller 测试的五相电机 FPGA 实时模型。  
2. 它用“边界延迟换并行”实现 66.7 ns 内部时步，并在离线模型、CHIL 和原型波形三个层次给出验证。  
3. 现有证据能闭合展示工况的可行性，不能闭合宽参数域与端到端闭环 fidelity 保证。

**1 句话：**  
论文证明了五相 PMSM 正常/开相 CHIL 可以做到很快且在选定工况下相当准确，但尚未证明其关键一步延迟在最坏工况下仍然无害。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**在电机—逆变器边界各插入一步延迟后，这个延迟对闭环精度和数值稳定性的影响可以忽略。** 该假设一旦不成立，66.7 ns 的并行性不再是“同一模型算得更快”，而会变成“用不同的离散闭环换速度”；那么正常波形吻合也不能保证高转速、快速开关、故障瞬间或参数偏差下仍高保真。

论文为它提供的证据是：Fig. 9 中 FPGA 与 Simulink 波形重合、Table III 的平均误差低于 1%，正常与开相 CHIL 能跟随命令，并且原型与 CHIL 在两个展示工况下具有相近电流幅值和频率。[pdf:E08]（PDF 物理页 8，Fig. 9 与 Table III）[pdf:E09]（PDF 物理页 9，Fig. 12–13）[pdf:E10]（PDF 物理页 10，Fig. 14–15）[pdf:E11]（PDF 物理页 11，Fig. 16–17）

缺失的证据是：没有对 \(h\)、电角速度、PWM 频率、DC-link 电压、负载、参数不确定性和故障发生相位做 sweep；没有与“无边界延迟但同样离散”的 monolithic reference 直接隔离比较；没有 eigenvalue、passivity、energy error 或 phase-margin 分析；也没有报告 CHIL I/O 与控制采样延迟如何叠加到这一步模型延迟上。作者在相关工作讨论中承认 delay-insertion 方法需要专门设计来保证 accuracy 与 numerical stability，但正文没有给出适用于本模型的充分条件。[pdf:E02]（PDF 物理页 2，网络解耦相关工作）因此，现有证据支持该假设在测试点成立，不支持它是普遍成立的。

## § 10 — 最小复现实验

一周内最值得复现的不是整个 CHIL 平台，而是“**一步延迟解耦是否在关键工况下仍接近未解耦参考模型**”。

1. 用 Table II 的 FPMSM #1 参数建立两份固定步长模型：A 为逆变器与电机同一步耦合求解的 monolithic reference；B 为论文 Fig. 1/2 的电压、电流各延迟一步的并行模型。两者都保留 \(d_1q_1/d_3q_3\)、binary-resistor inverter 和相同 forward Euler 步长。[pdf:E04]（PDF 物理页 4，电机模型）[pdf:E05]（PDF 物理页 5，离散式与逆变器）[pdf:E07]（PDF 物理页 7，Table II）
2. 先复现 \(i_{q1}:10\rightarrow40\) A、其余 dq 电流指令为零的工况，再加入 A 相开路；记录五相电流、转矩、一步相位差和每步能量误差。[pdf:E08]（PDF 物理页 8，Fig. 9 与 Table III）
3. 对步长至少测试 66.7 ns、其两倍和四倍，并对转速、负载及故障发生电角度做小型网格 sweep。若有目标 FPGA，再要求 B 在 XC7K410T 或等效器件上完成 66.7 ns timing closure；没有 FPGA 时只能验证数值 claim，不能声称复现了实时性能。
4. 支持论文 claim 的最低标准是：在原论文工况下，B 相对 A 的五相电流平均误差不高于论文最大报告值 0.948%，转矩平均误差不高于 0.299%，开相后无发散且故障相电流归零。若在 66.7 ns 已出现持续相位漂移、能量增长或 fault instant 敏感失稳，则直接反驳“延迟影响可忽略”的核心假设。

这个实验比复刻全部 LabVIEW UI 更有信息量，因为它把模型结构误差与 FPGA 工具链、I/O 和控制器实现误差分开。

## § 11 — 最强反例设计

最强反例是寻找一个**单体离散模型稳定、而一步延迟并行模型确定性失稳或产生不可接受闭环相位误差**的工况。具体做法是：保持同一控制器与同一 fixed-point 精度，在高电角速度、高 DC-link 电压、快速 PWM 边沿附近触发相邻两相同时开路，并在故障后立即施加速度或负载阶跃；对比 monolithic reference 与 delay-decoupled FPGA model 的 pole/zero、相电流、转矩、能量和 fault recovery。

该反例针对的替代解释是：论文展示的低误差可能主要来自测试工况相对温和、平均误差指标抹平了故障瞬间的相位误差，而不是一步延迟在机制上无害。若 monolithic model 与实体原型保持稳定，而论文结构在相同步长下出现振荡、过流、steady-state bias 或错误的 fault-tolerant current redistribution，就能把失败归因到边界延迟，而不是 motor equation 或 controller 本身。尤其应把 66.7 ns 内部时步、1 MS/s 模拟输出与 50 kS/s 控制采样的多速率链整体纳入，因为论文只报告了各自速率，没有给端到端同步与延迟预算。[pdf:E09]（PDF 物理页 9，CHIL setup）

若这一攻击在覆盖宽参数域后仍无法制造显著差异，才会比新增几张正常工况波形更有力地支持作者的并行机制。

## § 12 — Follow-up Research Idea

**候选想法：从“固定一步延迟的快速模型”改写为“带可验证闭环误差界的 delay-aware FPGA machine twin”。** 这不是宣称已具 novelty；本卡没有对相关工作全文做系统检索。

（a）未满足的需求是，控制器工程师真正需要知道的不只是模型能否在 66.7 ns 跑完，而是某个控制器、某个故障和某组多速率接口下，虚拟被控对象与实体对象的闭环偏差是否仍在可接受界内。  
（b）它可能产生本领域认可的价值，因为它把实时仿真的评价目标从“单点 waveform matching”提升为“速度—精度—稳定性可共同验收”，直接服务 fault-tolerant controller qualification。  
（c）可借鉴 sampled-data robust control、passivity-based co-simulation、wave-variable decoupling 和 fixed-point formal error analysis：在线根据边界能量残差或相位裕度选择保持并行、局部预测补偿，或在故障瞬间切换到更保守的同步更新，而不是固定假设一步延迟永远无害。  
（d）第一个证伪实验是预注册一组覆盖转速、负载、PWM 频率、参数扰动、单/双相开路时刻和 I/O latency 的随机测试；模型必须在所有测试点给出事前误差上界。只要实际电流或转矩误差反复突破上界，研究想法就被证伪。  
（e）它与本文的实质区别不是多加一个补偿模块，而是改变问题定义：本文优化“在所示工况下尽快完成每一步”，候选方向优化“在明确的闭环 fidelity certificate 下尽快完成每一步”。其起点正是本文已证明并行结构可行、却尚未闭合延迟误差边界这一缺口。[pdf:E02]（PDF 物理页 2，delay-insertion 的 accuracy/stability 风险）[pdf:E07]（PDF 物理页 7，66.7 ns 实现）[pdf:E11]（PDF 物理页 11，论文结论）
