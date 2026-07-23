# Design and Implementation of Real-Time Mpsoc-FPGA-Based Electromagnetic Transient Emulator of CIGRÉ DC Grid for HIL Application

作者：Zhuoxuan Shen、Tong Duan、Venkata Dinavahi [pdf:E01]（PDF 物理页 1，题名页）

出处：IEEE Power and Energy Technology Systems Journal [pdf:E01]（PDF 物理页 1，题名页）

年份：2018 [pdf:E01]（PDF 物理页 1，题名页）

DOI：10.1109/JPETS.2018.2866589 [pdf:E01]（PDF 物理页 1，题名页）

Zotero key：9PFHAKN7

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接解决的问题**是：怎样在严格实时约束下，对完整 CIGRÉ DC grid 做 EMT（electromagnetic transient，电磁暂态）仿真，同时保留局部 MMC（modular multilevel converter，模块化多电平换流器）的器件级开关、损耗与结温细节，又不丢掉全网功率流和故障传播。论文面对的对象不是一个小型换流器算例，而是包含 11 个 AC-DC converter、2 个 DC-DC converter，并覆盖两端 HVDC、非网状 MTDC 和网状 MTDC 三类结构的测试系统 [pdf:E02]（PDF 物理页 2，Section I）。作者把目标进一步限定为 HIL（hardware-in-the-loop，硬件在环）：模型必须按墙钟时间推进，才能让真实控制器或保护设备在闭环中看到可信的电压、电流和状态量 [pdf:E01]（PDF 物理页 1，Abstract）。

这个问题重要，首先因为 DC transmission line 的低阻抗在正常运行时有利于降低损耗，却会在故障时产生很大的短路电流；因此，控制与保护的动作时序不能只靠稳态或慢速离线模型评估 [pdf:E02]（PDF 物理页 2，Section I）。其次，MMC 的风险并不只体现在母线电压和功率上：器件开关损耗、热积累和结温决定阀级是否进入危险区。论文的 electrothermal loop 将电气参数、开关波形、损耗和六阶热网络闭合起来，意图让 HIL 同时观察“系统是否稳定”和“器件是否可能受损” [pdf:E07]（PDF 物理页 5，Fig. 5 与 Section III-C-1）。

真正的工程矛盾是**精度、规模和实时性不能同时用同一种模型硬顶**。作者明确指出，把所有换流器都做成 detailed model 会超过单板资源；反过来，全网采用 average value model（AVM，平均值模型）虽然便宜，却假定所有 sub-module capacitor voltage 始终平衡，无法验证 valve-level control，并可能在故障下带来数值后果 [pdf:E04]（PDF 物理页 4，Section III-C）；[pdf:E12]（PDF 物理页 7，Eq. 19 后正文）。因此，这篇论文的价值不只是“用 FPGA 加速”，而是提出一个有取舍的系统方案：把高保真计算集中在研究区，把低保真模型用于远端，再用硬件分工和网络分解把总延迟压进实时步长。

## § 2 — 前人工作与不足

论文对前人工作的归纳可以分成三层。第一层是实时仿真平台：FPGA 已被用于 EMT 和 MMC 实时仿真，HLS（high-level synthesis，高层综合）也能把 C/C++ 设计转换成流水化硬件；但单纯拥有并行硬件并不自动解决大系统的模型选择、网络分解、板间通信和任务映射。第二层是 MMC 模型：已有工作用 equivalent circuit model 仿真三端 MMC-HVDC，说明保持 sub-module capacitor state、又减少节点数是可行的。第三层是完整 CIGRÉ DC grid：论文称已有完整网实时仿真把全部 MMC 都处理为 AVM，因此不能验证阀级控制 [pdf:E02]（PDF 物理页 2，Section I 的 related-work 与 contributions 段）。

不足不是笼统的“前人精度不够”，而是两种能力没有闭合。小范围 detailed/equivalent model 能描述阀级或器件级行为，却没有证明可扩展到完整 DC grid；完整网 AVM 能满足规模和实时性，却主动舍弃 capacitor sorting、individual SM state 和开关热行为。论文试图补上的正是中间缺口：用 device-level electrothermal、equivalent circuit 和 AVM 形成分层 fidelity，再把 20 个子系统映射到 MPSoC-FPGA 平台 [pdf:E02]（PDF 物理页 2，Section I）。

作者还宣称三项工作在实时 EMT 领域“首次”出现：在复杂 DC grid 中应用器件级 electrothermal model、构建 MPSoC-FPGA 混合硬件平台、以及对大规模 DC grid 采用 hybrid modeling [pdf:E02]（PDF 物理页 2，contributions）。这属于**论文原文的 novelty claim**，不是本卡独立核验后的结论；输入包没有额外全文，且本任务禁止联网，因此不能据此断言其相对所有同期工作的绝对首创性。

## § 3 — 重建作者的思考路径

下面是基于论文证据的逆向重建，不是作者逐字陈述。

1. **先识别最贵的对象。** 高电平数 MMC 含大量 SM；若把每个 SM 都作为独立网络节点，传统 EMT matrix 会迅速膨胀，难以实时执行。于是先把 SM 压缩成等效电阻和历史电压源，再把整臂聚合成一个 interface，是保住 capacitor state、又削减节点数的第一步 [pdf:E10]（PDF 物理页 7，Section III-C-2，Eq. 13–15）。

2. **再确认“全详细”在资源上不可行。** XCVU9P FPGA 总计有 6,840 个 DSP slice 和 1,182,240 个 LUT [pdf:E03]（PDF 物理页 3，Table 1）；而 Fig. 7 报告一个 electrothermal MMC block 就使用 3,824 个 DSP、约 596K LUT、543K FF，latency 为 3.36 μs。按报告数字粗算，单个 detailed MMC 已占约 56% DSP 和 50% LUT；equivalent circuit MMC 降到 1,260 DSP、188K LUT、0.8 μs，AVM 则只有 64 DSP、12K LUT、0.13 μs [pdf:E16]（PDF 物理页 9，Fig. 7）。这组数量级差异自然导向“不能让 11 个 MMC 同档建模”。

3. **把模型精度当成空间预算。** 对真正要观察器件损耗和结温的 converter 使用 electrothermal model；对其邻近 converter 使用 equivalent circuit model，以保留 capacitor dynamics 和 valve-level control；对远端 converter 使用 AVM，只维持主要系统交互。这不是简单降阶，而是把不同模型的误差成本与研究问题的空间位置绑定 [pdf:E04]（PDF 物理页 4，Section III-C）。

4. **利用物理或数值延迟切开全网。** Distributed line model 的 traveling time，以及 AVM 的 one-time-step latency，可成为子系统边界。只要线路传播时间不短于 20 μs system step，且关键链路还长于板间通信 latency，各 sub-matrix 就能独立并行求解 [pdf:E14]（PDF 物理页 8，Section IV-A）。

5. **最后按计算形态分配硬件。** CPU/ARM 擅长复杂但顺序性强、经常改参数的 system-level control；FPGA/PL 擅长重复、规则、可流水化的 device model、capacitor sorting、gate generation 和 matrix solver。作者因此没有沿用“一个 CPU core 对应一个 subsystem”的常见划分，而改成按 function partition，板内直接 routing、板间用 Aurora 通信 [pdf:E15]（PDF 物理页 8，Section IV-B/C）；[pdf:E17]（PDF 物理页 9，Section IV-C）。

这条路径的关键并不是某一条公式，而是先承认资源约束，再把模型、分解边界和硬件架构一起设计。若只替换硬件、不改变 fidelity allocation 和 dependency graph，论文面对的规模仍然很难进入实时预算。

## § 4 — 核心 Intuition

把全网每个元件都算得同样细，是对实时预算最差的使用方式；更合理的做法是把 scarce FPGA parallelism 集中在故障或控制研究区，距离越远，模型越粗 [pdf:E04]（PDF 物理页 4，Section III-C）。再利用 transmission-line delay 和 AVM 的一步延迟把网络切成可并行 sub-matrix，并把顺序控制交给 ARM、重复数值计算交给 FPGA [pdf:E14]（PDF 物理页 8，Section IV-A）；[pdf:E16]（PDF 物理页 9，Fig. 7）。换句话说，这篇论文的核心机制是“按研究价值分配 fidelity，按数据依赖分配硬件”，而不是单纯提高 clock frequency。

## § 5 — 具体方法与完整 Pipeline

论文的实际配置围绕 Converter Cb-A1 建立 study zone。Fig. 3 把 Cb-A1 标成 electrothermal model，把邻近的 Cb-B1、Cb-C2、Cm-A1 标成 equivalent circuit model，其余 AC-DC converter 主要用 AVM；研究区连接线用 ULM（universal line model），远端或较简单线路用 BLM（Bergeron line model） [pdf:E05]（PDF 物理页 5，Fig. 3）；[pdf:E13]（PDF 物理页 7，Section III-C-4）。这四个较高保真 MMC 都是 65-level、共 384 个 SM；器件额定能力通过 10 个并联、7 个串联 IGBT module 组合实现 [pdf:E13]（PDF 物理页 7，Section III-C-4）。

控制侧是三层结构：outer loop 负责 active power 或 DC voltage，inner current loop 生成 dq current command，valve-level control 进行 capacitor sorting、决定插入 SM 数并生成 IGBT gate signal [pdf:E06]（PDF 物理页 5，Fig. 4）。Cm-A1、Cb-A1、Cm-B2 用于 DC-voltage regulation，其他 AC-DC converter 主要调 active power；所有 converter 可独立调 reactive power [pdf:E26]（PDF 物理页 4，Section III-B）。

以“在 Bb-A1 施加 DC fault 的一个 20 μs 时间步”为例，完整 pipeline 如下：

1. **同步与输入。** FPGA 和 MPSoC 初始化参数、同步时钟，读取上一时间步的 line history、MMC state、控制 reference 和 fault/protection condition。系统级 EMT 以 20 μs 更新，器件开关波形以 10 ns 更新；两块板的 PL 均运行在 100 MHz [pdf:E18]（PDF 物理页 10，Fig. 8）；[pdf:E19]（PDF 物理页 10，Section IV-D 与 Section V）。

2. **并行更新元件模型。** Power source、transformer、ULM/BLM、MMC 和 DC-DC model 同时计算。Cb-A1 的 electrothermal loop 先用当前 junction temperature 更新 electrical parameter，再根据 EMT 电压、电流和 gate signal 生成 device waveform、计算 conduction/switching loss，最后经 thermal network 得到下一步 junction temperature [pdf:E07]（PDF 物理页 5，Fig. 5）。系统电路与热网络使用 IEEE 32-bit floating point；10 ns device-waveform module 使用 fixed point，以便每个 100 MHz clock 都能更新 [pdf:E10]（PDF 物理页 7，Section III-C-1/2 交界）。

3. **形成 MMC arm interface。** Electrothermal model 和 equivalent model 都把各 SM 的等效电阻、历史源累加为 arm-level interface；AVM 则直接由 modulation signal 生成 upper/lower arm fundamental voltage source。这样 FPGA 不必对 384 个 SM 暴露 384 组网络节点。

4. **事件处理与 matrix solve。** 若本步 fault 或 protection 被触发，就修改对应 conductance；论文的示例把 Bb-A1 DC bus 相关 conductance 从极小值改为极大值来表示 short circuit。随后 20 个 sub-matrix 并行求解，矩阵尺寸从 2×2 到 13×13，由四类 solver 覆盖 [pdf:E15]（PDF 物理页 8，Section IV-C）；[pdf:E17]（PDF 物理页 9，Fig. 7 后正文）。

5. **控制计算与硬件映射。** 11 个 MMC 的 system-level control 放在 ZCU102 的四个 APU core；Cb-A1、Cb-B1、Cb-C2、Cm-A1 的 capacitor sorting 与 gate generation 放在 PL。VCU118 主要承担 electrical element、converter model 和 matrix solver；Aurora block 完成两板的数据交换 [pdf:E16]（PDF 物理页 9，Fig. 7）；[pdf:E17]（PDF 物理页 9，Section IV-C）。

6. **输出与下一步。** 两板交换 control I/O、line history、selected observation results，并等到精确的下一 time-step。输出包括 AC/DC voltage、power flow、SM capacitor voltage、device loss、junction temperature 和线性化 switching waveform；DAC 把选定量送到 oscilloscope，也可作为 HIL 接口 [pdf:E18]（PDF 物理页 10，Fig. 8）；[pdf:E19]（PDF 物理页 10，Section IV-D）。

这个 pipeline 的可扩展性来自两种独立旋钮：一是改变 detailed/equivalent/AVM 的覆盖范围，二是把更多 subsystem group 分配到更多 board。论文确实给出了多板扩展思路，但没有展示扩到第二组 VCU118/ZCU102 后的实测 scaling curve。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文没有提出新的数学定理；它的“核心数学”是把 device characteristic、network companion model、loss model 和 thermal RC network 离散成可在 FPGA 上流水执行的递推关系。

**1. 器件电气接口。** 对导通的 IGBT 或 diode，论文用多项式拟合 datasheet 的输出特性：

\[
v(i)=\sum_n \alpha_n i^n,\qquad
r_{\mathrm{on}}=\frac{\mathrm{d}v}{\mathrm{d}i}=\sum_n \beta_n i^n,\qquad
v_{\mathrm{on}}=v(i)-r_{\mathrm{on}}i.
\]

它的工程含义是把 nonlinear V-I curve 在当前电流点改写成“slope resistance + threshold voltage”的局部等效源。Datasheet 只给出 \(T_1=25\ ^\circ\mathrm{C}\) 与 \(T_2=125\ ^\circ\mathrm{C}\) 两组曲线，论文用线性插值得到任意 junction temperature 下的 \(r_{\mathrm{on}}\) 和 \(v_{\mathrm{on}}\)，例如

\[
r_{\mathrm{on}}(T_{vj})=
\frac{T_{vj}-T_2}{T_2-T_1}
\left(r_{\mathrm{on}}^{T_2}-r_{\mathrm{on}}^{T_1}\right)
+r_{\mathrm{on}}^{T_2}.
\]

关断时则把电阻设为很大、源电压设为 0。以上对应 Eq. 1–5 [pdf:E08]（PDF 物理页 6，Eq. 1–5 与 Fig. 6）。

**2. 网络求解。** 所有元件经 trapezoidal integration 形成 companion model，整网每步求

\[
\mathbf G\,\mathbf V(t)=\mathbf I,
\]

其中 \(\mathbf G\) 是 conductance matrix，\(\mathbf I\) 包含 source 与 history term。Eq. 6 本身普通，关键是作者借 line delay 和 model latency 把大矩阵拆成多个可并行小矩阵 [pdf:E08]（PDF 物理页 6，Eq. 6）。

**3. 损耗到结温的闭环。** 总损耗分为 conduction loss 和 switching loss：

\[
P_{\mathrm{loss}}(t)=P_{\mathrm{cond}}(t)+P_{\mathrm{switch}}(t),
\]
\[
P_{\mathrm{cond}}(t)=r_{\mathrm{on}}(T_{vj})i^2(t)+v_{\mathrm{on}}(T_{vj})i(t),
\]
\[
P_{\mathrm{switch}}(t)=
\left(\sum_{k=0}^{2}\alpha_k i^k\right)
\frac{v(t)}{v_{\mathrm{rated}}\Delta t}.
\]

最后一式只是把原 PDF 的求和索引改名为 \(k\)，避免与电流符号 \(i\) 混用；含义仍是由二次拟合的 switching energy 按实际电压和时间步换算为功率。Eq. 7–9 及其解释见 [pdf:E09]（PDF 物理页 6，Eq. 7–9）。

六阶 thermal network 用五个器件结到散热器的局部支路，加一个共享 heatsink 到 ambient 的支路。离散递推为

\[
\begin{aligned}
T_{vj}(t)=&\sum_{k=1}^{5}\Bigl[\alpha_k\bigl(P_{\mathrm{loss}}(t)+P_{\mathrm{loss}}(t-\Delta t)\bigr)
+\beta_k\Delta T_k(t-\Delta t)\Bigr]\\
&+\alpha_6\bigl(P_{\mathrm{sum}}(t)+P_{\mathrm{sum}}(t-\Delta t)\bigr)
+\beta_6\Delta T_6(t-\Delta t)+T_{\mathrm{amb}},
\end{aligned}
\]

\[
\alpha_k=\frac{R_k^t\Delta t}{2\tau_k^t+\Delta t},\qquad
\beta_k=\frac{2\tau_k^t-\Delta t}{2\tau_k^t+\Delta t}.
\]

作者设 \(T_{\mathrm{amb}}=30\ ^\circ\mathrm{C}\)。这里的 intuition 是：本步与上步损耗共同给 thermal capacitor 充能，历史温差通过 \(\beta_k\) 保留；新温度再返回电气参数，形成 electrothermal feedback。对应 Eq. 10–12 [pdf:E09]（PDF 物理页 6，Eq. 10–12）。

**4. Equivalent circuit 的节点压缩。** 每个 SM 被写成

\[
r_{\mathrm{SMeq}}=r_i+kR_{\mathrm{cap}},\qquad
v_{\mathrm{SMeq}}=v_i+k v_{\mathrm{cap}}^{\mathrm{Hist}}(t-\Delta t),
\]

其中 \(k\in\{0,1\}\) 由 gate signal 与 arm-current direction 决定。整臂再聚合为

\[
v_{\mathrm{arm}}(t)=\sum_{j=1}^{n}
\left[v_{\mathrm{SMeq}(j)}+r_{\mathrm{SMeq}(j)}i_{\mathrm{arm}}(t-\Delta t)\right].
\]

这使模型仍能更新 individual capacitor voltage、支持基础 valve-level control，却显著减少网络节点。对应 Eq. 13–15 [pdf:E10]（PDF 物理页 7，Eq. 13–15）。

**5. AVM 的压缩与信息损失。** 对 phase \(i\)，upper/lower arm voltage source 为

\[
v_{p,i}=\frac{1-m_i}{2}v_{dc},\qquad
v_{n,i}=\frac{1+m_i}{2}v_{dc},\qquad
C_{\mathrm{avm}}=\frac{6C_{\mathrm{sm}}}{n},
\]

而 DC-side equivalent current 通过功率守恒写成

\[
i_{\mathrm{avm}}=\frac{1}{2}(m_ai_a+m_bi_b+m_ci_c).
\]

对应 Eq. 16–19 [pdf:E11]（PDF 物理页 7，Eq. 16–18）；[pdf:E12]（PDF 物理页 7，Eq. 19）。它换来 matrix separation 和低资源，但代价是把 SM capacitor imbalance 与 valve switching 全部平均掉。论文没有给出 hybrid model 的 formal error bound、数值稳定性证明或模型切换误差分析；因此这些公式说明了“怎么算”，没有证明“在所有故障下误差一定多小”。

## § 7 — 实验设计与结论

**问题 1：平台是否真正进入实时预算？→ 实验：** 两板 PL 运行在 100 MHz，system-level step 为 20 μs，device waveform step 为 10 ns；Fig. 7 分别报告主要 block 的 resource 与 latency，例如 electrothermal MMC 3.36 μs、13×13 solver 4.53 μs、Aurora 4.0 μs、APU system-level control 4.9 μs [pdf:E16]（PDF 物理页 9，Fig. 7）；[pdf:E19]（PDF 物理页 10，Section V）。**答案：** 报告的单个关键 block latency 都低于 20 μs，硬件能按设定步长持续运行。作为速度参照，同一完整 DC grid 在 PSCAD/EMTDC 中模拟 3 s 需要 63 s，即离线约慢 21 倍 [pdf:E19]（PDF 物理页 10，Section V）。不过论文没有给出整条 worst-case critical path、timing slack、jitter 或长时间 deadline-miss 统计，因此“实时”主要由设计步长与模块 latency 表闭合，而不是由端到端时序分布证明。

**问题 2：系统级波形是否可信？→ 实验：** 稳态下把 Cb-A1 与 Cm-C1 的 AC voltage、Cb-A1 首个 upper-arm SM capacitor voltage 与 PSCAD/EMTDC 对比；DC fault 下再比较三个 DC system 的 converter voltage 和 power response [pdf:E20]（PDF 物理页 11，Fig. 10）；[pdf:E23]（PDF 物理页 12，Fig. 13）。**答案：** AC voltage 和 fault propagation 的形状总体一致，且拓扑影响符合预期：DC System 2 通过无 galvanic isolation 的 DC-DC link 与故障系统直连，受影响明显；DC System 1 因隔离和强 AC support，扰动较小 [pdf:E24]（PDF 物理页 12，Section V-C）。但 Fig. 10 的 SM capacitor voltage 已出现可见差异，作者归因于 PSCAD 的 two-state resistor IGBT 与实时模型的 temperature-dependent nonlinear IGBT 不同 [pdf:E20]（PDF 物理页 11，Fig. 10 后正文）。

**问题 3：器件级 electrothermal result 是否可信？→ 实验：** 用 SaberRD 的 dynamic thermal IGBT/diode model 验证一个 Cb-A1 SM。稳态末端，实时结果与 SaberRD 分别给出 S1 约 47.7 °C 对 48.2 °C、S2 约 34.0 °C 对 34.1 °C、D2 约 47.9 °C 对 47.7 °C、D1 约 34.6 °C 对 34.2 °C [pdf:E21]（PDF 物理页 11，Fig. 11(a)–(d)）。**答案：** 温度终值与趋势很接近；线性化 switching waveform 也捕捉到 turn-on overshoot。不过 turn-off current fall time 在图中约为 1.3 μs 对 3.1 μs，说明“good estimation”更适合解释为数量级和形态相符，而不是所有 switching detail 都高度一致 [pdf:E21]（PDF 物理页 11，Fig. 11(g)–(h)）。

**问题 4：控制命令变化能否传到系统和器件损耗？→ 实验：** Cb-C2 的 generation command 在 3.5–4.5 s 从 600 MW 降到 0 MW；图中有功符号表现为 −600 MW 到 0 MW，同时观察 Cb-A1 的 IGBT S1 loss [pdf:E22]（PDF 物理页 12，Fig. 12）。**答案：** Cb-C2 能跟踪 ramp，负责 DC voltage regulation 的 Cb-A1 改变功率来平衡系统，其 conduction/switching loss 随之上升。这验证了 system-level control → network power flow → device loss 的因果链，但没有报告 tracking RMSE、overshoot 或 settling-time 指标。

**问题 5：严重 DC fault 下能否给出保护有用的 thermal timing？→ 实验：** 在 1.0 s 对 Bb-A1 施加双极 DC fault，比较实时模型与 SaberRD 中 S1、D2 从故障开始到 150 °C 的时间。实时结果约为 D2 3.50 ms、S1 4.98 ms；SaberRD 约为 3.42 ms、4.94 ms，相差约 0.08 ms 和 0.04 ms [pdf:E23]（PDF 物理页 12，Fig. 13(k)–(l)）。**答案：** 在该算例中，热危险到达时序非常接近，足以支持毫秒级 protection study。作者同时明确警告：超过 150 °C 后器件可能已不安全，模型参数又是由正常区数据外推，器件损伤会改变物理特性，因此极端高温结果只能作 rough estimation [pdf:E24]（PDF 物理页 12，Section V-C）。

**不能外推的范围：** PSCAD 的完整网对照使用了与实时平台相同的 hybrid modeling，且不含 electrothermal model；SaberRD 因完整 DC grid 的 convergence/stability 问题，只验证了由外部 system waveform 驱动的 detailed sub-module [pdf:E19]（PDF 物理页 10，Section V）。所以实验充分支持“该实现能实时运行并在展示工况下给出相近波形”，但没有独立证明“hybrid approximation 对所有故障、所有 study-zone 位置和所有控制器都保持同等精度”。

## § 8 — Take-aways

**5 句话：** ① 这篇论文把完整 CIGRÉ DC grid 的实时 EMT 问题重新表述为 fidelity allocation、network decomposition 和 hardware mapping 的联合设计问题。② 它用一个 electrothermal MMC、三个 equivalent-circuit MMC 和远端 AVM/BLM 构成静态 multi-fidelity grid [pdf:E05]（PDF 物理页 5，Fig. 3）；[pdf:E13]（PDF 物理页 7，Section III-C-4）。③ 20 μs system step 与 10 ns device step 让系统交互和器件开关波形在两个时间尺度上共存 [pdf:E19]（PDF 物理页 10，Section V）。④ MPSoC 的 ARM core 负责顺序控制，FPGA/PL 负责高并行模型、sorting 和 solver，资源差异解释了这种分工 [pdf:E16]（PDF 物理页 9，Fig. 7）。⑤ 实验展示了稳态、功率命令变化和 DC fault 的可行性，但最关键的 model-form error 仍未由独立全详细基准闭合。

**3 句话：** ① 论文最强的贡献是系统工程整合，而不是某个单独公式。② 它证明“局部精细、全局近似”可以把一个大 DC grid 放进实时硬件预算，并输出有保护意义的 junction-temperature timing。③ 它没有证明静态 study zone 在未知故障位置下仍然可靠。

**1 句话：** 用有限硬件做大规模实时 EMT，核心不是把所有东西算得更快，而是明确哪些状态必须精确、哪些依赖可以延迟、哪些计算应放到哪类处理单元。

## § 9 — 最脆弱的假设

最脆弱的假设不是“FPGA 足够快”，而是：**远端 MMC/line 被 AVM/BLM 替代、并引入一步延迟后，仍能生成足够准确的全网电压电流轨迹，从而给局部 electrothermal model 提供正确激励。** 如果这个假设失效，Cb-A1 内部的损耗和结温即使数值计算完全正确，也是在“错误的 arm current 与 terminal voltage”上精确计算，核心贡献会从“局部高保真”退化为“局部精细地算错”。

论文为该假设提供的证据是：稳态和故障的实时波形与 PSCAD/EMTDC 大体一致 [pdf:E20]（PDF 物理页 11，Fig. 10）；[pdf:E23]（PDF 物理页 12，Fig. 13），且一个 sub-module 的 thermal result 与 SaberRD 接近 [pdf:E21]（PDF 物理页 11，Fig. 11）。但证据闭环仍弱：PSCAD 对照沿用了相同 hybrid scheme，因而双方共享 AVM/BLM 的 model-form bias；SaberRD 只接收外部 system waveform，不能检验“器件模型反过来影响全网”的 closed-loop coupling [pdf:E19]（PDF 物理页 10，Section V）。论文自己也承认 AVM 的 one-step latency 可能在 fault 中带来 numerical consequences [pdf:E12]（PDF 物理页 7，Eq. 19 后正文），并承认 extreme-temperature extrapolation 不可靠 [pdf:E24]（PDF 物理页 12，Section V-C）。

最缺的证据有四类：全 detailed 或至少更高 fidelity 的独立 offline reference；系统级 NRMSE、peak error、event-time error 等量化指标；把故障放在 AVM/equivalent boundary 两侧的 sensitivity test；以及真实 controller/protection hardware 闭环下的 trip-sequence 一致性。只要其中一类显示 model boundary 改变了 fault current peak、traveling-wave arrival 或保护动作顺序，这个假设就会被直接击穿。

## § 10 — 最小复现实验

一周内最值得复现的不是整套双板系统，而是**静态 hybrid partition 是否保留局部关键轨迹**。严格的数值复现有一个现实缺口：论文说明 CIGRÉ grid 参数来自参考文献 [4]，源 PDF 没有完整参数表 [pdf:E26]（PDF 物理页 4，Section III-A）；因此，开始前必须取得同一组 grid parameter 与 IGBT datasheet/fit coefficient，否则只能做机制复现，不能声称逐点复现论文。

最小方案如下：

1. 只实现 Cb-A1、Cb-B1、Cb-C2、Cm-A1 及其相连线路构成的 study-zone 子网，保留论文的 65-level/384-SM 配置和 20 μs system step；不必先实现 FPGA，用双精度离线代码建立可控 reference [pdf:E13]（PDF 物理页 7，Section III-C-4）；[pdf:E19]（PDF 物理页 10，Section V）。
2. 建两套模型。Reference 把四个 MMC 都设为 equivalent circuit，保留 individual capacitor state；Test 按论文设 Cb-A1 为 electrothermal、其余三台为 equivalent，再把边界外等效为 AVM/BLM。若算力允许，再增加“全四台 detailed/equivalent + ULM”的高 fidelity reference。
3. 运行三类工况：steady state、Cb-C2 在 3.5–4.5 s 从 600 MW 到 0 MW 的 command ramp、Bb-A1 在 1.0 s 的 DC fault [pdf:E22]（PDF 物理页 12，Fig. 12）；[pdf:E23]（PDF 物理页 12，Fig. 13）。再把 fault 依次移到 model boundary 内外，这是论文没有做而最能证伪的方法。
4. 测量 Cb-A1 terminal voltage、arm current、SM capacitor voltage、IGBT loss、junction temperature，以及 150 °C crossing time。预先定义支持标准，例如 steady/transient NRMSE 不高于 2%、peak error 不高于 5%、150 °C crossing error 不高于 0.1 ms；这些阈值是复现实验的工程判据，不是论文报告值。
5. 若 hybrid model 在原论文工况通过、但 fault 一跨过 AVM boundary 就出现显著 peak/event-time error，则论文的“固定局部高保真”只对预先知道 disturbance location 的场景成立；若边界移动仍稳定满足阈值，才真正支持其核心 claim。

这个实验一周内可完成，因为它绕开 bitstream、Aurora 和 DAC，把最关键的不确定性先压缩为 model-fidelity comparison。硬件复现应放在第二阶段；否则可能花完一周只解决工具链，却没有检验论文最关键的科学假设。

## § 11 — 最强反例设计

最强反例是在**被 AVM 表示的远端 converter 附近制造一个需要 individual SM state 才能正确传播的快速事件**，例如严重 DC fault 后紧接 converter blocking/deblocking 或 capacitor-imbalance-sensitive valve action，再观察 Cb-A1 的 fault current、DC voltage、protection input 和 junction temperature。AVM 明确假设所有 SM capacitor voltage 始终平衡，不能验证 valve-level control，并带有 one-step latency [pdf:E12]（PDF 物理页 7，Eq. 19 后正文）；因此，这类事件正好攻击它删除的信息，而不是泛泛增加噪声。

反例应设置三组：A 为论文的 static hybrid partition；B 把故障附近 AVM converter 升级为 equivalent circuit；C 为尽可能高 fidelity 的 reference。若 A 与论文的 PSCAD hybrid baseline 仍一致，而 B/C 显示不同的 traveling-wave arrival、fault-current peak 或 trip order，就出现一个具体替代解释：论文中的一致性来自“实时模型和对照模型共享同一简化”，而不是简化本身足够准确。只要这种差异进一步改变 Cb-A1 的 loss 或 150 °C crossing time，论文最核心的“全网交互足以驱动局部器件级分析”就被反驳。

这个反例比“换更大系统”更强，因为它不质疑工程规模，而是直接针对 hybrid mechanism 的信息删除边界；也比单纯测量 waveform RMSE 更强，因为 protection sequence 或 thermal threshold 是离散决策，一次错误 crossing 就可能改变 HIL 结论。

## § 12 — Follow-up Research Idea

**候选想法：建立带在线误差预算与状态一致切换的 adaptive-fidelity EMT emulator。** 本输入包没有完成相关工作检索，因此这里不声称 novelty；它是从论文静态 study-zone 局限推导出的候选方向。

（a）**未满足需求。** 实际 fault location 和保护动作往往事先未知，而论文把 Cb-A1 固定为唯一 electrothermal converter、把邻近三台固定为 equivalent，其余长期保持 AVM/BLM [pdf:E13]（PDF 物理页 7，Section III-C-4）。一旦 disturbance 出现在远端，最需要细节的位置恰好可能是最粗的模型。

（b）**潜在研究价值。** 在 EMT、power electronics 和 HIL 领域，高影响工作通常必须同时闭合 accuracy、real-time deadline、hardware resource 和真实控制/保护价值。新目标不再是“预先选一个 study zone 后实时运行”，而是“无论 disturbance 从哪里出现，都在给定 error budget 内自动把高 fidelity 迁移过去，同时不丢 20 μs deadline”。这改变了问题定义，不只是多加一个模块。

（c）**可借鉴的相邻工具。** 可以把 adaptive mesh refinement 的局部加密思想、multi-fidelity state estimation 的误差指示器、event-triggered scheduling，以及 FPGA dynamic partial reconfiguration 或预综合 model bank 结合起来。关键技术不是简单切换模型，而是设计 state projection：AVM 的 aggregate energy、equivalent model 的 capacitor states、electrothermal model 的 device temperature 必须在升级/降级时守恒，避免切换本身制造假 transient。

（d）**第一个可证伪实验。** 在远端 AVM converter 处随机注入 fault，要求系统在一到数个 20 μs step 内检测 error indicator、把该 converter 升级到 equivalent/electrothermal model，并与高 fidelity reference 比较 fault-current peak、traveling-wave arrival、protection trip 和 junction-temperature crossing；20 μs 是论文采用的 system-level step [pdf:E19]（PDF 物理页 10，Section V）。只要模型升级造成能量跳变、错过 deadline，或误差没有明显低于 static hybrid，就应否定该方案。

（e）**与本文的实质区别。** 本文的未来工作是加入更多 MMC topology、更详细 AC system、offshore renewable plant 和更多互联计算设备 [pdf:E25]（PDF 物理页 13，Section VI）；这些主要扩展 scope。候选方案则把“模型层级由人离线指定”改成“模型层级由在线误差和事件动态决定”，并把可验证的 error bound/state consistency 设为第一目标。它直接回应第 9 节的脆弱假设：不是相信远端粗模型始终足够，而是在它开始不够时检测、迁移并证明迁移后的误差与时序仍受控。
