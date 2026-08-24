# A Generalized Fixed-Admittance ADC Model for Two-Level Converters in EMT Simulation

- 作者：Yang Cao, Wei Gu, Mingwang Xu, Hangyu Yang, Shuaixian Chen, Fei Zhang, Wei Liu
- 出处：IEEE Transactions on Power Electronics, Vol. 41, No. 4
- 年份：2026
- DOI：10.1109/TPEL.2025.3634392
- Zotero key：6EN6SEVB

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是“怎样把一个开关算得更精细”，而是一个系统级实时 EMT simulation 的结构性矛盾：变流器的开关事件发生在微秒甚至亚微秒尺度，网络又可能包含大量开关，因此模型既要保留高频开关行为和非互补状态，又不能在每次开关后重新分解整个网络矩阵。传统 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 模型能逼近理想开关，但开关改变电导矩阵，\(K\) 阶矩阵频繁求逆的复杂度为 \(O(K^3)\)；L/C-associated discrete circuit（ADC）把开关等效成固定电导与历史电流源，使网络求解降到 \(O(K^2)\)，却引入非物理尖峰、虚拟功率损耗和由尖峰触发的状态误判。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I-A）

物理上，L/C-ADC 的问题来自“数值储能元件被突然换接”：为保持固定导纳而引入的虚拟电感、虚拟电容，在开关状态改变时会释放或吸收并不存在于真实电路中的能量。这不仅让波形难看，还可能改变控制器看到的零交越、触发错误的续流或阻断判断，进而使误差在闭环中积累。论文因此追求一个更具体的目标：不改变全局导纳矩阵，同时让二电平变流器在互补导通、同时阻断、DCM、门极信号丢失和故障暂态中仍具有可信的状态与能量行为。作者把 generalized half-bridge（GHB）作为建模单元，并报告该方法兼顾多状态表达、开关误差抑制和实时计算效率。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题的重要性在于“实时”不是单纯跑得快，而是每个固定 wall-clock 周期都必须完成一次求解。若模型为了精度频繁改矩阵，硬件 deadline 会失守；若为了速度接受虚拟尖峰，控制器硬件在环（HIL）测试可能响应一个并不存在的故障或开关状态。固定导纳、高状态可信度和可映射到 FPGA 三者同时成立，才使大规模 inverter-based resource 的闭环 HIL 与系统级 EMT 分析有工程价值。

## § 2 — 前人工作与不足

论文把已有路线分成三类。第一类改进离散化或加补偿，例如 exponential integration、negative impedance compensation；它们能缓和部分数值误差，却没有消除单开关 L/C-ADC 在状态突变时内部变量失配的根因。第二类是参数化 ADC 加 reinitialization：G-ADC 通过参数拟合、cross-initialization（CI）与额外修正算法降低虚拟损耗，但论文指出这些方法主要建立在一对开关始终互补导通的假设上，无法正确覆盖同时阻断。第三类是 topology-specific state-space formulation：它可以为特定 VSC 或 blocked mode 构造固定矩阵，但换拓扑往往要重推模型，通用性来自“重新设计”，而不是可复用基本模块。[pdf:E02]（PDF 物理页 2，Section I-B）

更细地看，HCRI 用“同一状态上一次出现时的稳态值”初始化，忽略两次相同状态之间真实发生的动态；CI 与 IEM 能修正互补导通切换，却没有覆盖两管同时关断。L/C-ADC 自己虽然有快速状态预测，但其判断依赖单开关电压、电流，而这些变量恰好会被 L/C 数值尖峰污染，形成“误差导致误判，误判再制造误差”的反馈。[pdf:E07]（PDF 物理页 7，Section IV-A）[pdf:E08]（PDF 物理页 8，Section IV-B）

作者试图改变的关键不是再给单开关补一个经验项，而是改变可观察边界：把成对开关连同端口关系作为 GHB，看端口的电感电流、电容电压或电源电压等状态变量，再由 KCL/KVL 反推内部开关状态。这样做的理由是端口状态变量具有连续性或缓变性，比切换瞬间的内部非状态变量更可靠。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Eq. (4)-(5)）[pdf:E04]（PDF 物理页 4，Eq. (6)）

需要守住边界：以上“前人不足”均是本论文自己的文献组织与论证，本卡没有独立读取所引文献，不能把它升级为已独立验证的 novelty 结论。

## § 3 — 重建作者的思考路径

可以从一个仿真工程师会遇到的失败链条重建这项工作。

1. 首先保留 ADC 的核心优势：每个开关无论开或关，都用同一个 \(G_{\mathrm{eq}}\) 连接到网络，只改变历史电流源，因此全局矩阵可预先求逆。
2. 然后观察失败并不主要发生在某个状态的稳态，而发生在状态切换后的第一个或前几个离散步。虚拟 L/C 中保存的是旧状态内部变量，新状态却要求另一组电压、电流约束，二者不一致就产生能量脉冲。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Section II-A）
3. 单开关看不到误差该流向哪里，但同一半桥的两只开关、电感支路与直流/交流端口受 KCL/KVL 共同约束；因此把“一只开关”提升为“一个 GHB”后，端口量足以确定内部状态。Eq. (6) 表明，已知一项内部电压与两项内部电流即可闭合 GHB 状态。[pdf:E04]（PDF 物理页 4，Eq. (6)）
4. 有了 GHB 状态，就不必用一组 \(\alpha,\beta\) 勉强覆盖所有模式。对互补导通和同时阻断分别写状态递推矩阵，要求谱半径小于 1，并在稳定域内选择收敛最快、稳态误差较小的参数。
5. 但同时阻断的最小谱半径仍接近 1，仅靠“最终会收敛”不够。于是利用端口状态量不突变这一物理线索，在切换瞬间重置内部非状态变量，使新状态从接近正确流形的位置开始，而不是等待错误自然衰减。
6. 最后把状态判断、multistate parameter setting 和 initial switching error correction（ISEC）串进每步求解；网络矩阵始终不变，变化被限制在 GHB 内部参数与历史源更新中。

这条路径的真正工程洞见是：固定导纳并不等于内部变量也必须机械延续。只要不改端口状态和 KCL/KVL，就可以在切换瞬间修正“数值模型的记忆”，而不向外部网络凭空注入一个新的拓扑。

## § 4 — 核心 Intuition

不要让每只开关用自己的、已被尖峰污染的电压电流判断世界；把成对开关视为一个 GHB，用较平滑的端口状态量决定它处于上管导通、下管导通还是同时阻断。状态改变时不重建全局网络矩阵，而是在 GHB 内部选择该状态的收敛参数，并把旧状态留下的非物理“数值记忆”重置到满足新状态 KCL/KVL 的位置。这样，固定导纳负责速度，GHB 端口约束与 ISEC 负责切换精度。

## § 5 — 具体方法与完整 Pipeline

以论文的 boost chopper 为例，输入是电源、滤波 \(L/C\)、负载、门极信号和上一步的端口/内部变量，输出是本步节点电压、支路电流、器件状态与更新后的历史源。

1. **建模与预计算。** 每只开关写成固定 \(G_{\mathrm{sw}}\) 加历史电流源的 ADC；两只相向开关和接口电感组成 GHB。论文的参数化形式为 \(i_{\mathrm{sw}}^n=G_{\mathrm{sw}}(u_{\mathrm{sw}}^n-v_{\mathrm{fw}})+I_{\mathrm{his}}^n\)，历史源由上一步电压、电流及 \(\alpha,\beta\) 更新；外部网络只看到固定导纳。[pdf:E03]（PDF 物理页 3，Eq. (4)-(5)）
2. **状态判断。** 根据器件是否受控、半控、不可控或物理缺失，先得到 \(C_V,C_D\)；再结合上一步电感电流方向、端口电压与 forward drop，通过 Eq. (25) 判断两个开关组和同时阻断状态。boost chopper 中只有受控器件 \(V_2\) 与不受控器件 \(D_1\)，论文把通式化简为 Eq. (26)-(29)。[pdf:E07]（PDF 物理页 7，Eq. (25)-(29)）
3. **按状态选参数。** 互补导通时，导通开关保持 \(\beta_{\mathrm{on}}=1\)，关断开关保持 \(\alpha_{\mathrm{off}}=-1\)，其余参数由谱半径优化得到；同时阻断时取两管 \(\alpha=-1,\beta=0\)。这些参数只依赖 GHB 内部 \(G_{\mathrm{sw1}},G_{\mathrm{sw2}},G_L\)，不随外部网络工况重算。[pdf:E05]（PDF 物理页 5，Eq. (14)-(17)）[pdf:E06]（PDF 物理页 6，Eq. (24) 与 Table I）
4. **切换瞬间执行 ISEC。** 若状态发生变化，依据新状态和上一步接口量，把 \(u_{\mathrm{sw1}},u_{\mathrm{sw2}},u_L,i_{\mathrm{sw1}},i_{\mathrm{sw2}},i_L\) 的内部初值投影到新状态的理想关系。关键点是只改 GHB 内部非状态变量，不改端口状态变量，因此校正前后仍满足 KCL/KVL。[pdf:E08]（PDF 物理页 8，Eq. (31)、(34)-(35)）
5. **更新历史源并求解固定网络。** 用选定参数与校正后的内部变量生成历史电流源，用预先固定的逆导纳矩阵完成本步节点求解，再更新支路量进入下一步。论文的 Fig. 8 把这一闭环画成“状态判断 → ISEC → 参数/历史源更新 → 固定矩阵网络求解”。[pdf:E09]（PDF 物理页 9，Fig. 8）

时间推进是固定步长离散 EMT；论文测试覆盖 100 ns 至 10 μs，但没有给出自适应步长或 GHB 内外 multirate 的实现。并行方面，GHB 被论证为可独立处理的模块，FPGA 上使用专门 ADC solver；控制信号由 CPU 计算并经 Ethernet 发送到 FPGA。论文未报告定点/浮点格式、位宽、流水级、时钟域、端到端通信抖动或综合约束，因此不能从资源表反推出数值表示细节。[pdf:E13]（PDF 物理页 13，Section VI-B 与 Tables V-VI）[pdf:E14]（PDF 物理页 14，Section VI-B）

## § 6 — 核心数学推导

先解释符号。时间步长为 \(h\)；开关等效电导为 \(G_{\mathrm{sw}}\)；接口电感经 trapezoidal rule 离散后 \(G_L=h/(2L)\)；端口电容对应 \(G_C=2C/h\)。\(\alpha\) 和 \(\beta\) 决定历史源记住多少上一步电压与电流。Eq. (3) 给出理想稳态开/关特性所需的基本约束：导通态 \(\beta_{\mathrm{on}}=1,\alpha_{\mathrm{on}}\neq-1\)，关断态 \(\alpha_{\mathrm{off}}=-1,\beta_{\mathrm{off}}\neq1\)。[pdf:E02]（PDF 物理页 2，Eq. (1)-(3)）

### 6.1 互补导通：把“误差会不会消失”化成谱半径

当 \(S_1\) 导通、\(S_2\) 关断时，作者将 GHB 的内部误差状态写成

\[
x_1^n=A_1x_1^{n-1}+b_1^n,
\]

其中 \(x_1^n=[u_{\mathrm{sw1}}^n,\ i_{\mathrm{sw2}}^n/G_{\mathrm{sw2}}]^T\)。物理意义是：导通管应该压降接近 \(v_{\mathrm{fw}}\)，关断管应该电流接近零；偏离这两个目标的误差，每一步都被 \(A_1\) 再乘一次。若谱半径 \(\rho(A_1)<1\)，误差衰减；越接近 0，衰减越快；若大于 1，误差放大。[pdf:E04]（PDF 物理页 4，Eq. (7)-(11)）[pdf:E05]（PDF 物理页 5，Fig. 4）

L/C-ADC 用 backward Euler 时 \(\rho=\sqrt{k_2}<1\)，用 trapezoidal rule 时 \(\rho=1\)，说明后者的切换误差不会由这套递推主动衰减。作者在可行参数域找到 \(K_1=K_2=0\) 的点，使理论上的 \(\rho(A_1)=0\)，再根据稳态误差选择 Eq. (14) 而不是 Eq. (15) 的参数组；反向互补导通对应 Eq. (16)。[pdf:E05]（PDF 物理页 5，Eq. (12)-(16)）

### 6.2 导纳尺度：在电感与电容之间给虚拟开关留出“安全带”

作者将稳态误差概括为

\[
\lim_{n\to\infty}\varepsilon x_1^n
=O(G_L/G_{\mathrm{sw}})+O(G_{\mathrm{sw}}/G_C)
=O\!\left(\max\left\{\frac{h}{2L G_{\mathrm{sw}}},\frac{hG_{\mathrm{sw}}}{2C}\right\}\right).
\]

第一项表示开关电导若相对电感离散电导不够大，接口电感会显著扰动开关的理想约束；第二项表示开关电导若相对端口电容电导过大，一个步长内的电容电压变化又会被放大。于是要求

\[
G_L\ll G_{\mathrm{sw}}\ll G_C,
\qquad
\frac{G_L}{G_{\mathrm{sw}}}=\frac{G_{\mathrm{sw}}}{G_C},
\]

并得到推荐 \(G_{\mathrm{optimal}}=\sqrt{\sum C_{\mathrm{dc}}/L}\)。这不是“电导越大越好”，而是在两个相反误差源之间取几何平衡。[pdf:E05]（PDF 物理页 5，Eq. (17) 与其后说明）[pdf:E09]（PDF 物理页 9，Eq. (39)）

该推导还依赖一个时间尺度假设：单个 operating state 持续期间，滤波电容每步的电压增量 \(\Delta u_C\) 近似不变。作者在 Appendix A 论证这种“增量不变”带来的误差为 \(O(h^2)\)，优于直接假设电压不变时的 \(O(h)\)。[pdf:E04]（PDF 物理页 4，Section III 的 Assumption）[pdf:E14]（PDF 物理页 14，Eq. (A.1)-(A.4)）

### 6.3 同时阻断与 ISEC

两管同时关断时，状态扩展为 \([i_{\mathrm{sw1}}/G_{\mathrm{sw1}},i_{\mathrm{sw2}}/G_{\mathrm{sw2}},u_L]^T\)。作者求得当 \(\beta_{\mathrm{sw1}}=\beta_{\mathrm{sw2}}=k_1+k_2\) 时最小谱半径为 \(k_1+k_2\)，但综合稳态误差、复杂度与收敛性，实际选 \(\alpha_1=\alpha_2=-1,\beta_1=\beta_2=0\)。这一状态的谱半径仍较接近 1，所以不能只等它慢慢收敛，必须在进入状态时修正初值。[pdf:E06]（PDF 物理页 6，Eq. (20)-(24) 与 Fig. 5）

ISEC 的数学作用可以看成“保持端口不变的内部投影”。Eq. (34)-(35) 用新状态 \(S_1,S_2,S_3\) 和旧端口量构造校正后的内部电压、电流。未校正时，切换后第一步误差含有与直流电压和电感电流同量级的项；校正后 Eq. (38) 只剩

\[
\varepsilon=O(G_L/G_{\mathrm{sw}})+O(G_{\mathrm{sw}}/G_C),
\]

即回到前述可通过导纳尺度与步长压小的余项。[pdf:E08]（PDF 物理页 8，Eq. (32)-(38)）

## § 7 — 实验设计与结论

**问题 1：能否在 CCM 与 DCM 中同时保持准确？** 作者用非对称 boost chopper，步长 0.2 μs，总时长 2.5 ms，在 1.5 ms 施加 50% 电压跌落并于 2.0 ms 恢复；\(R_{\mathrm{on}}/R_{\mathrm{off}}\) 作为参考。GHB-ADC 在 Case A 的最大相对误差为：\(P_{\mathrm{load}}\) 0.50%、\(i_L\) 0.53%、\(u_{\mathrm{load}}\) 0.32%、\(i_D\) 0.48%，而 L/C-ADC 对应 10.7%、12.3%、4.50%、12.0%；虚拟功率损耗误差项为 0.001% 对 0.37%。G-ADC 与 CI-ADC 在 DCM 失效，因为它们假设互补模式。[pdf:E09]（PDF 物理页 9，Section V-A）[pdf:E10]（PDF 物理页 10，Table III 与 Fig. 10）

**问题 2：推荐导纳是否只是巧合？** 作者把 \(G_{\mathrm{sw}}\) 从推荐值的 0.01 倍扫到 100 倍。推荐值误差最低，0.1 倍和 10 倍出现中等偏差，0.01 倍和 100 倍误差显著，符合“两侧误差项平衡”的数学解释。[pdf:E10]（PDF 物理页 10，Fig. 11 说明；Fig. 11 位于物理页 11）[pdf:E11]（PDF 物理页 11，Fig. 11）

**问题 3：面对同时阻断与门极异常，状态判断是否仍可靠？** AC-DC-AC 案例包含 LCR 与 VSC，步长 0.1 μs、dead time 100 ns，在 0.048 s 丢失 \(S_1\) 控制信号、0.068 s 恢复。L/C-ADC 的尖峰导致错误状态判断和反复切换；GHB-ADC 在信号丢失期间仍与参考波形一致。[pdf:E10]（PDF 物理页 10，Section V-B）[pdf:E11]（PDF 物理页 11，Fig. 13）

**问题 4：能否扩展到多变流器闭环大系统？** 论文构造 20 个 PV 子系统，步长 10 μs；0.7-0.8 s 对 Subsystem 1 施加 A 相接地故障，1.2 s 将 irradiance 降到 800 W/m²，1.4 s 恢复到 1000 W/m²。GHB-ADC 与参考保持对齐，而 L/C-ADC 的尖峰和误判使闭环控制结果偏离。Case C 中 GHB 的最大相对误差仍为 1.18%-3.80%，明显小于 L/C 的 44.9%-198.8%，但这也表明闭环会放大很小的模型差异，不能把单变流器误差直接外推到系统级。[pdf:E11]（PDF 物理页 11，Section V-C/D）[pdf:E10]（PDF 物理页 10，Table III）

**问题 5：固定导纳是否真的带来规模效率？** PSCAD 一秒离线仿真中，Case C 在两组载波设置下，GHB-ADC 用时 231.62/232.73 s，L/C-ADC 为 214.57/215.13 s，\(R_{\mathrm{on}}/R_{\mathrm{off}}\) 为 841.06/1498.57 s。GHB 并不比 L/C 更快，但保持同一数量级；相对需要改矩阵的参考模型，规模变大或载波频率升高时优势显著。[pdf:E12]（PDF 物理页 12，Table IV）

**问题 6：与真实硬件是否一致，并能否在 FPGA deadline 内完成？** 三相 VSC 的物理实验与 HIL 使用 OP4610XG、AMD Ryzen 3.8 GHz CPU、Xilinx Kintex-7 FPGA 和 Imperix B-BOX RCP 3.0 controller；HIL 步长为 2 μs。实验相电压幅值为 39.4 V，仿真为 40 V；在参考电压由 40 V 降到 30 V 时，GHB 与 L/C 都完成 HIL，但 GHB 的尖峰和虚拟损耗更小。[pdf:E13]（PDF 物理页 13，Section VI-A 与 Fig. 18）

专用 solver 的 FPGA 实时测试步长为 1 μs。单 VSC 每步平均执行时间为：GHB-ADC 0.360 μs、L/C-ADC 0.340 μs、G-ADC 0.475 μs、CI-ADC 0.477 μs；XCKU060 上 GHB 使用 7173 FF、12401 LUT、4 BRAM、111 DSP，L/C 分别为 6565、11014、4、102。结论是 GHB 比基础 L/C 稍贵，但在 1 μs deadline 内仍有余量，且比论文列出的两种改进 ADC 更快。[pdf:E13]（PDF 物理页 13，Tables V-VI）

不得外推的范围包括：shoot-through 被明确排除；没有器件级 reverse recovery、寄生振荡或 thermal behavior；物理实验只覆盖一套低压三相 VSC；大规模 20 变流器案例是软件仿真而非同规模 FPGA HIL；论文没有报告 bit-accurate 数值格式、最坏执行时间、通信抖动或长期漂移。

## § 8 — Take-aways

**5 句话：** 1）固定导纳的真正价值是让全局网络矩阵保持不变，而不是让开关内部变量原封不动。2）GHB 把两只开关与端口约束放进同一个判断单元，使互补导通、同时阻断和 DCM 能在统一框架中表达。3）multistate 参数通过谱半径控制误差收敛，ISEC 则直接消除切换第一步的大误差，两者缺一不可。4）从 boost、LCR+VSC、20-PV、物理实验和 FPGA 数据看，GHB-ADC 的精度显著优于 L/C-ADC，而计算代价仅小幅增加。5）这些结果成立的物理前提是端口状态在步长内足够平滑，并存在 \(G_L\ll G_{\mathrm{sw}}\ll G_C\) 的尺度窗口。

**3 句话：** GHB-ADC 用“固定全局矩阵 + 可变内部历史源”保留 ADC 的实时性。它以端口状态判断 GHB 模式，并在切换瞬间把内部变量投影到新状态，从源头压低尖峰和虚拟损耗。论文给出的证据很强地支持二电平、GHB 可分解拓扑，但还没有覆盖 shoot-through、器件级非理想和 bit-accurate 最坏执行时间。

**1 句话：** 这篇论文最值得带走的思想是：不改变网络拓扑也能修正开关切换，只要把校正限制在满足端口 KCL/KVL 的内部数值状态中。

## § 9 — 最脆弱的假设

最脆弱的单一假设是 **GHB 端口存在可作为“慢变量锚点”的状态量，并且在所选步长与参数下形成 \(G_L\ll G_{\mathrm{sw}}\ll G_C\) 的时间尺度分离**。这是一个物理假设而不只是调参条件：状态判断假定电感电流、电容电压或电源端口量不会像开关内部电压、电流那样突变；ISEC 又假定用这些旧端口量重建新状态内部变量不会把真实的高频动态误删。[pdf:E07]（PDF 物理页 7，Section IV-A）[pdf:E08]（PDF 物理页 8，ISEC 原理）[pdf:E05]（PDF 物理页 5，Eq. (17)）

如果端口直接接入很小的寄生储能、强刚性开关源、频繁改变的拓扑，或者时间步长大到一个步内跨过多个换流事件，那么端口量本身也可能急变；此时状态判断可能选错模式，ISEC 可能把真实暂态当成“数值误差”重置掉。若 \(G_L\) 与 \(G_C\) 之间没有足够宽的窗口，任何 \(G_{\mathrm{sw}}\) 都会让 Eq. (17) 的至少一项较大，固定导纳模型便无法同时满足导通约束和电容电压精度。

论文提供的支持包括 Appendix A 的 \(O(h^2)\) 误差论证、\(G_{\mathrm{sw}}\Delta u_C=O(G_{\mathrm{sw}}/G_C)\) 的导纳界、0.01-100 倍导纳扫描、100 ns-10 μs 步长范围以及多种软件工况。[pdf:E14]（PDF 物理页 14，Eq. (A.1)-(A.5)）[pdf:E15]（PDF 物理页 15，Eq. (A.6)）[pdf:E11]（PDF 物理页 11，Fig. 11）但证据缺口同样明确：没有直接扫描“端口时间常数/开关周期”的比值，没有给出状态判断在噪声、量化、延迟与一个步内多事件下的误判率，也排除了最会破坏平滑性的 shoot-through。故论文证明的是若干典型 GHB 工况中的有效性，而不是该假设对所有二电平硬件都天然成立。

## § 10 — 最小复现实验

一周内最有信息量的复现是论文 Case A 的 boost chopper，因为一个小电路就同时包含 CCM、DCM、故障切换和状态判断，不必复现 20 个 PV 子系统或完整 FPGA solver。

- **数据与电路：** 按 Table II 使用 48 V 直流源、0.001 Ω 内阻、64 μF 滤波电容、16 μH 电感、10 Ω 负载、20 kHz carrier 和 0.5 duty；固定步长 0.2 μs，运行 2.5 ms，1.5 ms 将输入电压降低 50%，2.0 ms 恢复。[pdf:E10]（PDF 物理页 10，Table II）[pdf:E09]（PDF 物理页 9，Section V-A）
- **实现：** 在同一离散 nodal solver 中实现三种模型：可变导纳 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 参考、标准 L/C-ADC、GHB-ADC。GHB 只需 Eq. (29) 的 boost 状态判断、Table I 参数、Eq. (34)-(35) ISEC 和 Eq. (39) 推荐 \(G_{\mathrm{sw}}\)。
- **测量：** 逐步记录 \(P_{\mathrm{load}},i_L,u_{\mathrm{load}},i_D\)、全部开关虚拟功率 \(\sum u_{\mathrm{sw}}i_{\mathrm{sw}}\)、DCM 起止时刻、每个状态切换后的首步峰值，以及每步计算时间。误差应对完整故障区间取最大值，而非只看稳态均方误差。
- **支持标准：** GHB 在 CCM、DCM 与电压跌落期间都不出现持续误判，且五项最大相对误差接近论文 Table III 的 0.50%、0.53%、0.32%、0.48%、0.001%，并显著优于 L/C；每步计算量仍与 L/C 同阶。
- **反驳标准：** 若关掉 ISEC 后结果几乎不变、GHB 在 DCM 边界发生状态抖振、误差与 L/C 同量级，或只有通过缩小步长/重新调 \(G_{\mathrm{sw}}\) 才能得到结果，则论文把收益归因于 GHB+ISEC 的 claim 未被复现。

为了区分“参数选择”与“算法机制”，只增加两个低成本 ablation：GHB 关闭 ISEC；完整 GHB 把 \(G_{\mathrm{sw}}\) 改为推荐值的 0.1 与 10 倍。不要再扩展拓扑，这两项已经足以检验谱半径优化、ISEC 与导纳窗口是否共同必要。

## § 11 — 最强反例设计

最强反例不是随意换一个复杂拓扑，而是专门破坏第 9 节的慢变量锚点，同时仍保持“二电平 GHB”这一论文声称的适用范围。构造一个带极小直流链电容、显著母线/换流寄生电感、dead time、二极管 reverse recovery 和门极传播延迟的三相 VSC；令控制器在电流过零附近连续产生短脉冲，并选择一个步长，使同一步内可能经历“上管关断 → 两管阻断 → 二极管续流 → 下管导通”。加入与论文 FPGA 资源场景一致的定点量化和一拍接口延迟，但不加入 shoot-through，以免落入作者明确排除的范围。

攻击的可证伪点有三个：

1. 记录高带宽 reference model 的真实端口电压/电流，检查一个仿真步内它们是否仍可视为平滑；若不是，Eq. (25) 用上一步量只能看见事件序列的起点而非最终状态。
2. 对比启用/禁用 ISEC 的能量残差。如果 ISEC 降低“虚拟损耗”同时也抹掉 reference model 中由寄生与 reverse recovery 产生的真实高频能量，它就是把物理动态误判为数值误差。
3. 扫描 \(h\)、寄生 \(L\)、链路 \(C\) 与 \(G_{\mathrm{sw}}\)，寻找不存在 \(G_L\ll G_{\mathrm{sw}}\ll G_C\) 可行窗口的区域；在该区域测状态误判率、首步误差与闭环稳定裕度。

若 GHB-ADC 在这个实验中仍能以固定矩阵重现事件顺序、真实高频能量和闭环行为，论文的机制证据会显著增强；若它只能给出平滑但错误的平均波形，则现有“低尖峰”不能再单独解释为更高物理精度，而可能只是更强的数值投影。

## § 12 — Follow-up Research Bet

**主 bet（候选判断，尚未完整检索相关全文，不声称 novelty）：构造“事件序列提升的 GHB macro-operator”。** 它要使当前模型首次具备的能力是：外部网络一次跨过一个 PWM carrier period，只做一次宏步网络求解，却仍保留该周期内门极边沿的先后顺序、CCM/DCM/同时阻断路径、周期末状态与选定的 switching-ripple moments；这不是把波形平均掉，也不是在宏步里暗中重复原来的全局微步求解。

**核心机制。** Eq. (4) 把每只开关写成固定 \(G_{\mathrm{sw}}\) 与 history source，Eq. (8) 和 Eq. (19) 又把互补导通、同时阻断分别写成低维 affine recurrence；Table I 只随 GHB mode 改变局部参数，Eq. (34)-(35) 的 ISEC 则是 mode 边界上的代数状态重置。[pdf:E03]（PDF 物理页 3，Eq. (4)）[pdf:E04]（PDF 物理页 4，Eq. (8)）[pdf:E06]（PDF 物理页 6，Eq. (19)、Table I）[pdf:E08]（PDF 物理页 8，Eq. (34)-(35)）因此，给定一个 carrier period 内的有序 mode word 后，可以把各段 affine map 与 ISEC reset 依次相乘，形成一个从宏步起点端口状态到终点状态及端口电流 moments 的 lifted operator；再把中间微步变量作块消元，只把宏步端点和少数端口时间基函数留给网络。因果链是“固定 mode matrix → 有序事件图可组合 → 内部微步变量可消元 → 网络只处理宏步端口关系 → 仍可回代恢复 DCM/阻断次序与 ripple”。删除这一 lifted representation，系统就退回 Fig. 8 的“每步状态判断—ISEC—history source—网络求解”，基本能力随之消失。[pdf:E09]（PDF 物理页 9，Fig. 8）

两个最基本的设计变量是：宏窗口 \(H\)（覆盖多少个 gate event 或 carrier period）以及宏端口时间基的阶数 \(q\)（只保留端点，还是再保留斜率/低阶 ripple moments）；第三个变量是保留哪些端口 moments，而不是保留哪些内部微步节点。\(H\) 决定一次消元跨多长时间，\(q\) 决定网络与 GHB 在宏步内交换多少动态信息，两者共同决定“少做全局求解”与“保留 switching-order effect”之间的科学边界。

**论文特异依据。** Fig. 10 的 boost case 表明，同一电路会在 CCM、DCM 与电压跌落之间移动，mode 顺序会直接改变二极管电流和 virtual power；Fig. 13 的 control-signal loss 又显示，错误事件序列会产生 repetitive switching，而不只是稳态幅值偏差。[pdf:E10]（PDF 物理页 10，Fig. 10、Section V-B）[pdf:E11]（PDF 物理页 11，Fig. 13）但本文仍逐微步推进：20-PV Case C 在 \(10\,\mu\text{s}\) 步长下每仿真 1 s 需 231.62/232.73 s，单 VSC 的 FPGA 平均每步为 \(0.360\,\mu\text{s}\)。这说明固定导纳已经降低了单步成本，却没有消除“开关越快，网络步数越多”的时间离散负担。[pdf:E12]（PDF 物理页 12，Table IV）[pdf:E13]（PDF 物理页 13，Table V）Appendix A 只证明单个 operating state 内电容电压增量近似带来 \(O(h^2)\) 误差，并没有证明把该近似直接跨到一个 carrier period 仍成立；这正是 macro-operator 必须重新研究端口时间基的原因。[pdf:E14]（PDF 物理页 14，Eq. (A.1)-(A.5)）[pdf:E15]（PDF 物理页 15，Eq. (A.6)）

**最大收益与最大科学风险。** 若成立，最大收益不是再降低若干百分比误差，而是把 switching-level EMT 的主要规模变量从“全系统网络微步数”改成“宏步数 + 每个 GHB 的局部事件数”，从而可能在同一 FPGA deadline 内同时容纳更高 carrier frequency 和更多 converter，同时保留 averaged model 无法区分的 event ordering。最大风险是 GHB 并非在宏窗口内真正闭合：二极管换流和 DCM 边界取决于同时变化的网络端口电压，若 \(q\) 必须随微步数增长，或每个 event 都必须重新做全局网络求解，块消元就只是在搬运原计算量。实现证据也尚未闭合：Table V 只有 average execution time，正文称 BRAM-free，而 Table VI 对完整 GHB-ADC solver 报告 4 BRAM；因此 memory traffic、Ethernet control latency 与 worst-case event count 都必须作为实现结果实测，不能由现有资源表推定。[pdf:E13]（PDF 物理页 13，Tables V-VI）[pdf:E14]（PDF 物理页 14，Section VI-B）

**能区分机制的最小实验。** 复用 Case A 的 48 V boost、\(0.2\,\mu\text{s}\) reference step、20 kHz carrier 和 50% voltage sag，在相同 duty 与相同 carrier period 下制作两种 gate word：一个连续脉冲与两个分裂脉冲；两者平均占空比相同，但边沿顺序和 DCM 进入时刻不同。[pdf:E09]（PDF 物理页 9，Section V-A）[pdf:E10]（PDF 物理页 10，Table II）用原始微步 GHB-ADC 与 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 生成 reference，再在一次一 carrier-period 网络求解的预算下比较 lifted operator 和 duty-averaged model，测周期末 \(i_L,u_C\)、二极管导通区间、首个 DCM 周期及预先选定的 ripple moments。若 lifted operator 能区分两种 equal-duty gate word，并同时复现 reference 的事件次序和终点状态，而 averaged model 对二者给出近乎相同结果，就支持“有序 affine composition”这一核心机制；若只有把 \(q\) 或内部网络求解次数提高到接近原微步数才匹配，或两种 gate word 的差异仍被抹平，则主 bet 被反驳。

**与本文及最近边界的实质区别。** problem 从“怎样在每个 EMT 微步降低 GHB switching error”变为“怎样跨越整段有序 switching events 而不逐次求解全局网络”；mechanism 从逐步 state judgment + ISEC 变为 mode-conditioned affine maps 的时间提升与内部变量块消元；representation 从某一时刻的 GHB internal state 变为由 mode word、\(H\)、\(q\) 参数化的 carrier-scale operator；experimental object 从单一 gate schedule 下的点波形误差变为 equal-duty、different-order gate words 的可区分性及宏步网络求解次数。论文把 small-step synthesis 描述为 topology-specific，并仅在效率表中列出既有 FPGA 对比；这些相邻工作的全文未在本卡中独立核验，因此这里不能据此声称本方向具有 novelty。[pdf:E02]（PDF 物理页 2，Section I-B）[pdf:E13]（PDF 物理页 13，Table V）

**Wild-card alternative：** 改用空间机制，把独立 GHB 重写为共享 floating-capacitor charge state 的 multilevel cell graph，以 cell adjacency 与 retained charge coordinates 为设计变量，并用“同一端口电压、不同 redundant switching word”的三电平 flying-capacitor 实验检验固定端口导纳下能否重现内部电荷迁移。
