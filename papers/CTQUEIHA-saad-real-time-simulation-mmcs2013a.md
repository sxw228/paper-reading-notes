# Real-Time Simulation of MMCs Using CPU and FPGA

- **作者**：Hani Saad；Tarek Ould-Bachir；Jean Mahseredjian；Christian Dufour；Sébastien Dennetière；Samuel Nguefeu
- **出处**：IEEE Transactions on Power Electronics, Vol. 30, No. 1, pp. 259–267
- **年份**：2015（论文在线出版于 2013 年）
- **DOI**：10.1109/TPEL.2013.2282600 [pdf:E01]（PDF 物理页 1，标题、作者与 DOI）
- **Zotero key**：CTQUEIHA
- **证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。下文把“论文直接陈述”“基于证据的推断”和“候选判断”明确分开。

## § 1 — 研究问题与重要性

论文要解决的不是“MMC 能不能被仿真”，而是一个更苛刻的工程问题：当每个桥臂有数百个子模块（submodule, SM）时，能否在每个真实时钟步长内算完电磁暂态，使仿真器可以直接接入真实控制器做 hardware-in-the-loop（HIL）测试。MMC 的每个 SM 都带开关和电容；规模扩大后，开关器件、内部节点和需要保存的电容状态一起增长。论文直接指出，详细开关模型的迭代求解在实时条件下不可行，因此必须在模型精度、时间步长、并行结构和硬件通信之间做联合设计 [pdf:E01]（PDF 物理页 1，Abstract 与 Section I）。

这个问题重要，是因为控制器看到的必须是按固定节拍推进的“在线电网”，而不是算得很准但偶尔超时的离线模型。作者研究的范围覆盖最高 400 个 SM/桥臂，即 401-level MMC，并比较 CPU 与 FPGA 两条实现路线；目标不是只报一次 benchmark，而是给出“给定 MMC 级数时，平台需要什么计算结构”的设计边界 [pdf:E01]（PDF 物理页 1，Abstract 与 Section I）。对 EMT + FPGA 研究而言，这篇论文的价值在于把电气模型、控制采样约束、数据搬运和硬件流水线放到了同一个实时性判据下。

## § 2 — 前人工作与不足

作者之前已有三类基础。第一，MMC 的详细/平均建模和控制方法已经存在，NLC（nearest level control）与电容电压 balancing control algorithm（BCA）也已有基础。第二，把 IGBT/diode 简化为可切换的 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 电阻后，可以消去桥臂内部节点，形成桥臂 Norton 等值，同时仍逐个保存 SM 电容电压 [pdf:E03]（PDF 物理页 3，Section IV、Fig. 6）。第三，这种桥臂等值已在 CPU 实时仿真中使用，但作者在当时文献中没有找到“数百个 SM/桥臂”的成功实时报告 [pdf:E01]（PDF 物理页 1，Section I）。

不足来自两条不同的瓶颈。CPU 便于用浮点实现复杂模型，但执行时间随 SM 数量上升，而且多 CPU 并行不能随意加入一个采样步延迟：桥臂模型和 Norton 等值必须在同一步内形成，所以只能在桥臂之间并行、在桥臂与网络等值之间保持串行依赖 [pdf:E04]（PDF 物理页 4，Section V-A、Fig. 9–10）。FPGA 可把计算压成微秒级，但传统 fixed-point 的动态范围与量化会限制步长；通用 floating-point 又带来面积和长 latency。论文因而采用定制、非标准 floating-point 运算器，同时直面 PCIe 数据搬运可能吃掉并行收益的问题 [pdf:E01]（PDF 物理页 1，Section I）。

## § 3 — 重建作者的思考路径

可以把作者的思考路径重建为四步。首先，先问控制采样本身允许多大的 \(\Delta t\)：如果 NLC 在一个步长内跨过了某个电平，再快的硬件也只是在更快地算错误的 staircase waveform。作者因此先从 NLC 正弦参考的最大斜率推导采样上限，并用不同步长的谐波结果检查这个边界 [pdf:E02]（PDF 物理页 2，Section III、Eq. (1)–(3)）[pdf:E03]（PDF 物理页 3，Fig. 4–5）。

其次，在模型侧保留“每个 SM 的电容状态”，但用桥臂 Norton 等值把大量内部电气节点从网络方程里消掉，使复杂度主要落在规则、可并行的桥臂状态更新上 [pdf:E03]（PDF 物理页 3，Section IV、Fig. 6）。再次，在 CPU 上测试“六桥臂分给六个核”能把边界推到哪里，同时承认网络等值与桥臂求解的串行依赖。最后，把最规则的桥臂运算映射成 FPGA 上的 application-specific processor（ASP），再比较两种分割：ASP1 只放桥臂模型，ASP2 连 BCA 一起放进去。这个对比让作者发现，真正决定系统性能的不是单个乘加器有多快，而是高维 \(v_C\) 与 SM commands 是否还要每步跨 PCIe [pdf:E06]（PDF 物理页 6，Section V-B、Fig. 14–17）。

## § 4 — 核心 Intuition

核心 intuition 是：先用桥臂等值把“数百个开关构成的大电路”改写为“六组规则的状态更新 + 一个小网络接口”，再让 FPGA 以固定节拍处理这些状态。若 BCA 也放进 FPGA，就不必每步把全部电容电压和全部 gate commands 跨总线搬运；系统时延于是主要由固定的桥臂流水线和少量接口数据决定，而不再由 SM 数量线性主导 [pdf:E06]（PDF 物理页 6，Fig. 14–17）。换句话说，论文真正改变的是计算边界，而不只是把同一段 CPU 代码换一块更快的硬件。

## § 5 — 具体方法与完整 Pipeline

以一个三相 MMC 的一次仿真步为例，完整 pipeline 如下。

1. **控制输入**：上层控制产生功率/电流参考，下层 control 运行 circulating-current suppression、NLC 和 BCA。NLC 给出每个桥臂应插入的 SM 数，BCA 决定具体选哪些 SM；每桥臂有 \(N\) 个 SM，线对中性点波形具有 \(N+1\) 个电平 [pdf:E02]（PDF 物理页 2，Fig. 1–3、Section II–III）。
2. **桥臂降阶**：每个开关用 \(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 表示，桥臂内部节点被消去。桥臂模型接收该桥臂端电压 \(v_{\mathrm{arm},j}\) 与 SM commands，更新各 \(v_{Cij}\)，并把 \(Y_{\mathrm{arm},j}\) 与历史电流源 \(i^h_{\mathrm{arm},j}\) 送给网络求解器 [pdf:E03]（PDF 物理页 3，Fig. 6–7、Section IV–V）。
3. **CPU 路线**：one-CPU 版本把整个 MMC station 放在一个 CPU；multi-CPU 版本把六个桥臂分到六个 CPU，但 Norton 等值仍与桥臂更新串行，以避免不物理的一个时间步人工延迟。桥臂之间则可并行 [pdf:E04]（PDF 物理页 4，Fig. 8–10）。
4. **FPGA 路线**：ASP1 在 FPGA 中实现六个桥臂模型，仍跨 PCIe 传全部 SM commands 与 \(v_C\)；ASP2 把六桥臂模型和 BCA 一起放到 FPGA，只与 CPU 交换六个桥臂电流和六个插入数，显著缩小通信量 [pdf:E06]（PDF 物理页 6，Fig. 14–15）。
5. **FPGA 内部执行**：sequencer 驱动 gate register file、\(v_C\) register file 与三个 processing elements；每次并行读写 5 个值，最多用 80 个 clock cycles 扫完一个 400-SM 桥臂。六桥臂顺序处理共 480 cycles，在 200 MHz 下为 2.4 μs；处理单元的 latency 与后续桥臂读写重叠 [pdf:E06]（PDF 物理页 6，Fig. 16–17）。
6. **数值表示**：变量使用 35-bit signed mantissa，常数使用 44-bit signed mantissa，加法与累加使用 80-bit extended mantissa；一次乘法占 3 个 cycles 与 4 个 DSP blocks。作者以此在动态范围、精度、资源和 latency 之间折中 [pdf:E07]（PDF 物理页 7，Table I 前正文）。
7. **输出与实时判据**：本步形成的 Norton 等值进入 CPU 网络求解，下一步继续。只有总执行时间不超过由 modulation 决定的采样上限，才算可实时运行；单纯“FPGA 内核很快”不等于整机实时。

论文未给出 HDL 源码、pipeline 的 cycle-accurate 状态机、\(R_{\mathrm{ON}}/R_{\mathrm{OFF}}\) 具体数值或完整定点/浮点误差传播分析；这些应保持为“未报告”，不能从框图补写。

## § 6 — 核心数学推导（无形式化数学则跳过）

NLC 先把正弦参考映射为每桥臂插入 SM 数：

\[
s_n=\frac{N}{2}\sin(2\pi f t_n)+\frac{N}{2}.
\]

这里 \(s_n\) 是插入数，\(N\) 是每桥臂 SM 数，\(f\) 是电网频率。相邻 staircase level 的最短间隔出现在正弦斜率最大处，因此要保证每个电平都被采到，控制步长需满足

\[
\Delta t\le \frac{1}{2\pi f}\arcsin\left(\frac{2}{N}\right).
\]

考虑频率上限 \(1.2\) pu 与幅值上限 \(1.4\) pu 后，作者采用更保守的

\[
\Delta t\le \frac{1}{1.2(2\pi f)}\arcsin\left(\frac{2}{1.4N}\right).
\]

这三个公式的物理含义很直接：级数越高，正弦参考在同一电角度内要穿过的台阶越多，因此允许的采样时间越短；它是 control fidelity 的上限，而不是由 FPGA 资源自动决定的上限 [pdf:E02]（PDF 物理页 2，Section III、Eq. (1)–(3)）。

FPGA processing elements 实现的桥臂状态关系为

\[
v^h_{\mathrm{arm},j}(t)=R_{\mathrm{arm},j}i_{\mathrm{arm},j}(t)+
\sum_{i=1}^{N}\alpha_{ij}v_{Cij}(t),
\]

\[
v_{Cij}(t+\Delta t)=R_{\mathrm{eq},ij}i_{\mathrm{arm},j}(t)+
\beta_{ij}v_{Cij}(t).
\]

\(\alpha_{ij}\)、\(R_{\mathrm{eq},ij}\) 与 \(\beta_{ij}\) 都由 gating state 决定；\(R_{\mathrm{arm},j}\) 则由 ON-state SM 数索引预计算表得到。第一式把本步所有 SM 状态折叠为桥臂 history voltage，第二式推进每个电容状态；二者共同解释了为什么计算规则、易流水化，也解释了为什么 \(v_C\) 是大规模数据 [pdf:E08]（PDF 物理页 8，Appendix、Eq. (4)–(5)）。

作者估算 \(v^h_{\mathrm{arm},j}\) 需要 5 次乘法和 5 次加法，\(v_{Cj}\) 需要 10 次乘法和 5 次加法；200 MHz 下对应 \( (15+10)\times0.2=5\) GFLOPS。这个数是作者对 ASP peak computing power 的运算计数，不是整个平台端到端吞吐率 [pdf:E08]（PDF 物理页 8，Appendix）。

## § 7 — 实验设计与结论

**问题一：NLC 步长约束是否真的影响波形？** 作者对 191-level MMC（\(N=190\)）分别使用 10、20、30 μs。10 与 20 μs 落在 Eq. (3) 的 admissible area 内，能够经过每个电平，谐波谱相近；30 μs 会跳级并显著改变谐波，因此 Eq. (3) 给出的不是抽象性能线，而是 modulation fidelity 的实际边界 [pdf:E03]（PDF 物理页 3，Fig. 4–5）。

**问题二：CPU 并行是否保持动态精度？** one-CPU 模型先前与 detailed IGBT/diode 模型比较，报告 relative error 小于 5%，因此本文把它作为 reference。multi-CPU 验证使用 101-level、30 μs，并在仿真 10 s 时施加持续 150 ms 的三相接地故障；外部与内部变量总体吻合，本文报告的 relative error 为 0.1%–2%。单个电容的 BCA 选择可能不同，但桥臂电容电压之和应一致 [pdf:E04]（PDF 物理页 4，Section V-A-3）[pdf:E05]（PDF 物理页 5，Fig. 11–12）。

**问题三：CPU 能扩展到多少 SM？** 作者把 \(N\) 从 60 扫到 400。100 SM/桥臂时，multi-CPU 平均执行时间约 12.3 μs，one-CPU 为 26.4 μs，提速比 2.15；multi-CPU 的实时上限约 230 SM/桥臂。加入估计为 9 μs 的 HIL communication/I/O latency 后，上限降至约 160 SM/桥臂 [pdf:E05]（PDF 物理页 5，Fig. 13 与相邻正文）。这说明 CPU 的主要限制仍是桥臂计算与端到端 latency，而不是核数本身。

**问题四：FPGA 资源与时序是否可实现？** 在 Virtex-6 LX240T 上，两种 ASP 都满足 200 MHz、5 ns timing constraint。ASP2 因包含 BCA，综合估计为 72,957 registers、39,702 LUTs、146 BRAM 与 84 DSP48E1，分别占器件的 24%、26%、35% 与 10% [pdf:E07]（PDF 物理页 7，Table I）。

**问题五：FPGA-ASP2 是否既快又准？** 作者用 401-level MMC、9 μs 步长复现同类三相接地故障；FPGA-ASP2 实时结果与离线 one-CPU reference 的外部/内部变量相近，报告 relative error 为 0.3%–3%。BCA 的电容电压 relative error 低于 0.1%，每周期开关次数平均值误差在 0.5% 内 [pdf:E07]（PDF 物理页 7，Fig. 18–19 与 Section V-B-2/3）[pdf:E08]（PDF 物理页 8，Fig. 20、Table II）。

**问题六：为什么 ASP2 胜过 ASP1？** 两个 ASP 的桥臂内核都以 2.4 μs 运行，但 ASP1 每步需通过 PCIe 交换 \(2\times6N+6\) 个值，端到端性能反而差；ASP2 把 BCA 放进 FPGA 后把总执行时间降到 9 μs，而且在论文测试范围内不随 MMC 级数增加。论文结论据此给出 CPU 约 231-level 的上限，以及考虑 HIL latency 后约 161-level 的上限，并把 ASP2 视为更现实的 HIL 结构 [pdf:E08]（PDF 物理页 8，Fig. 21、Conclusion）。

不得外推的范围是：作者验证的是该桥臂等值、该 NLC/BCA、最高 400 SM/桥臂、特定 OP5600 + Virtex-6 平台和所选故障/正常工况。论文没有证明任意 modulation、任意保护事件或超过该规模时仍保持相同精度与 9 μs 端到端时间。

## § 8 — Take-aways

**5 句话：**（1）实时 MMC 仿真必须同时满足 modulation 的采样上限和硬件的执行上限。（2）桥臂 Norton 等值保留逐 SM 电容状态，却避免把全部内部节点交给网络求解器。（3）multi-CPU 能扩展 CPU 上限，但同一步内的串行依赖与 HIL latency 阻止线性加速。（4）FPGA 的关键优势来自规则状态更新的定制流水线，更来自把 BCA 与桥臂模型放在同一数据域以消除 \(O(N)\) 的 PCIe 往返。（5）论文在 401-level、9 μs 条件下给出了可行性证据，但该证据不覆盖 blocked-state 与更广泛保护工况 [pdf:E05]（PDF 物理页 5，Fig. 13）[pdf:E06]（PDF 物理页 6，Fig. 14–17）[pdf:E08]（PDF 物理页 8，Conclusion 与 Appendix）。

**3 句话：** 把大 MMC 变成六个规则桥臂状态机，是这项工作的模型基础。把 BCA 搬入 FPGA、让高维状态留在本地，是它的系统基础。最终瓶颈从“算不完”转成了“通信边界是否设计正确”。

**1 句话：** 这篇论文证明的不是“FPGA 总比 CPU 快”，而是“当模型降阶、流水线和数据驻留共同设计时，数百级 MMC 才能进入微秒级实时仿真”。

## § 9 — 最脆弱的假设

最脆弱的假设是：用于目标 HIL 工况的每个 SM 在仿真步内都可视为受 gate command 决定的 ON/OFF 状态，而不需要 blocked-state 下由桥臂电流方向决定的 diode conduction。论文在拓扑说明中明确给出 blocked state 的物理行为，但 FPGA 实现省略了 blocked-state code；附录也再次说明本文只考虑 ON 或 OFF [pdf:E02]（PDF 物理页 2，Section II）[pdf:E06]（PDF 物理页 6，Section V-B-1）[pdf:E08]（PDF 物理页 8，Appendix）。

这项假设的失败代价最大，因为控制器保护、闭锁和故障恢复恰恰可能把 SM 推入 blocked state。**基于证据的推断**：一旦电流方向而非 gate bit 决定二极管导通，原来的 \(R_{\mathrm{arm}}\) 查表、\(\alpha/\beta\) 选择与 history source 更新就可能使用错误的拓扑，9 μs 的实时性仍可能成立，但物理轨迹不再可信。论文给出的三相交流侧故障和正常 BCA 验证支持已实现状态内的精度，却没有提供 converter blocking、直流故障或 protection sequence 的证据，因此不足以消除这一风险。

## § 10 — 最小复现实验

一周内最值得复现的是“ASP2 的收益究竟来自计算还是数据驻留”。不必先重做完整 OP5600：可用一台 CPU 与一块可用 FPGA/FPGA 仿真环境，实现单桥臂的 Eq. (4)–(5) 状态更新，把 \(N\) 扫过 60、100、200、400，并构造两种接口。

- **ASP1-like**：每步传 \(N\) 个 gate commands 与 \(N\) 个 \(v_C\)。
- **ASP2-like**：BCA 与状态留在 FPGA，每步只传 \(i_{\mathrm{arm}}\) 与插入数 \(s_{\mathrm{arm}}\)。
- **测量**：FPGA kernel latency、host–device transfer latency、端到端 step latency、deadline miss 数，以及与 double-precision CPU reference 的 \(v_C\) 与 \(v^h_{\mathrm{arm}}\) 误差。
- **支持 claim 的结果**：kernel latency 对 \(N\le400\) 保持固定预算，ASP2-like 的端到端 latency 明显低于 ASP1-like，并在目标 9 μs deadline 内无 miss，误差仍处于论文所展示的百分比量级 [pdf:E06]（PDF 物理页 6，Fig. 14–17）[pdf:E07]（PDF 物理页 7，accuracy verification）[pdf:E08]（PDF 物理页 8，Fig. 21）。
- **反驳 claim 的结果**：搬移 BCA 后端到端 latency 仍随 \(N\) 明显增长，或为了达到 deadline 必须牺牲状态精度，使误差显著超出 reference。

这个实验能单独验证论文最可迁移的系统机制，而无需先复现整套 HVDC 网络与控制器。

## § 11 — 最强反例设计

最强反例应直接攻击第 9 节的状态假设：在 401-level MMC 上施加会触发 converter blocking 的直流侧 pole-to-pole fault，随后执行 deblocking/restart；reference 使用含 antiparallel diode 与 blocked-state 的 detailed 或经验证 switching model，被测 FPGA 保持论文的 ON/OFF-only 实现。比较每桥臂电流、直流故障电流、总电容能量、单 SM 电容极值、阀端电压和保护时序，并同时记录 deadline miss。

**基于证据的推断**：若 FPGA 在闭锁期间继续按 gate bit 选择 \(R_{\mathrm{arm}}\)、\(\alpha\) 与 \(\beta\)，它可能给出“实时但错误”的故障电流和电容充电路径。若误差只在闭锁边沿短暂出现且不改变保护动作，可以把适用范围收窄为控制器正常运行与非闭锁扰动；若误差改变峰值、能量或 restart 结果，则论文结构不能直接支撑保护级 HIL。这个反例比再做一次交流侧故障更强，因为它让论文明确省略的物理状态成为主导机制 [pdf:E02]（PDF 物理页 2，blocked-state 定义）[pdf:E08]（PDF 物理页 8，Appendix 的 ON/OFF-only 条件）。

## § 12 — Follow-up Research Idea

电力电子实时仿真的高影响价值通常来自三者同时成立：模型在关键工况下物理可信、固定 deadline 可证明、并能在真实控制/保护闭环中复现。基于此，候选研究方向是建立一种 **protection-aware hybrid MMC FPGA solver**：不把 blocked state 当作后来补上的第三个 if-branch，而是把“由 gate 控制的导通”和“由电流方向决定的二极管导通”定义为两类有显式切换契约的混合状态，并让桥臂等值、事件检测和 deadline certificate 共同生成。

- **(a) 未满足需求**：现有结果能证明正常控制与选定交流故障下的微秒级性能，但无法证明闭锁、直流故障和恢复过程的物理可信性。
- **(b) 研究价值**：它把 HIL 的评价目标从平均误差和平均执行时间，改变为“保护关键事件的状态正确性 + 每步最坏执行时间”，更贴近 HVDC protection validation。
- **(c) 可借鉴工具**：可借鉴 hybrid systems 的 mode contract、worst-case execution time analysis，以及 FPGA 上的 event-triggered pipeline；这是方法借鉴，不是对已有 novelty 的声称。
- **(d) 首个证伪实验**：使用第 11 节的 blocking–deblocking 直流故障，把 peak fault current、capacitor energy 与 deadline miss 同时作为判据；如果加入混合状态后仍不能同时优于 ON/OFF-only 模型的物理误差且维持 deadline，研究设想即被早期证伪。
- **(e) 实质区别**：原论文优化的是给定 ON/OFF 桥臂算法的 CPU/FPGA 映射与通信边界；候选方向重新定义了实时仿真的正确性边界，使保护事件的 mode fidelity 成为一等验收量。

由于本卡未对 2013 年之后的相关工作做系统检索，这只是由论文证据约束出的候选方向，不声称 novelty。
