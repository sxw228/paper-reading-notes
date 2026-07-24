# Low Cost and Optimized FPGA-HIL Real Time Simulation of a Boost Converter Powered by a Photovoltaic Panel

作者：Rodolfo Orosco Guerrero、Elías Rodríguez Segura、Juan Martínez Nolasco、Fany Rodríguez García  
出处：*IEEE Latin America Transactions*, Vol. 22, No. 11, 2024, pp. 962–970  
年份：2024  
DOI：10.1109/TLA.2024.10738270  
Zotero key：8SJQSIC8

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是：如何把“光伏板的指数非线性 + boost converter 的开关动态”放进低成本 FPGA，在实时 HIL（hardware-in-the-loop）中以固定、很小的步进运行，同时避免每步 Newton–Raphson 迭代或指数函数计算带来的延迟。作者提出三状态离散模型，把两个只依赖状态 \(x_1\) 的非线性函数做成一维 LUT（lookup table），再通过状态缩放与算术依赖重排，把最长状态更新路径压到 4 个 40 MHz 时钟，即 100 ns（PDF 物理页 1、5，Abstract 与 Table I）[pdf:E01][pdf:E05]。

这个问题重要，因为 power-electronics HIL 的被控对象必须在控制器 deadline 内给出下一步电流、电压；若步长相对 PWM 周期过大，控制器看到的纹波、相位和暂态会失真。论文使用 50 kHz PWM，对应 20 μs 开关周期；100 ns 步进相当于每周期约 200 个状态更新点。它的价值不是提出新的 PV 单二极管模型，而是把已有连续模型重写成适合 FPGA 确定性执行的形式（PDF 物理页 5，Section VI 与 Tables II–IV）[pdf:E05]。

## § 2 — 前人工作与不足

论文回顾了三类工作。第一类使用 Xilinx System Generator 或 LabVIEW FPGA 加速 HIL 开发，但工具本身没有解决 PV 指数模型的低延迟计算。第二类针对光伏模型优化 Newton–Raphson、Taylor 展开或 SysML/Petri-net 实现，已有工作把计算从 19.2 μs 降到 0.96 μs，但没有把光伏板与变换器动态统一到同一个状态更新核。第三类已经实现 PV+boost HIL，其中一项 MyRIO 工作报告 10 μs，另一项使用 Newton–Raphson 却没有给出执行时间（PDF 物理页 1–2，Introduction）[pdf:E01][pdf:E02]。

因此，本文针对的真实缺口是“联合 PV 非线性与 boost 开关动态，并把一步延迟进一步降到 100 ns”。不过标题中的 low cost 与 optimized 需要收窄理解：源 PDF 没有报告 LUT/BRAM/DSP/LUT/FF 利用率、综合后的 fmax、采购成本或与商业 HIL 平台的成本对比；它证明的是 MyRIO 上的算术路径设计和软件参考一致性，不是完整的成本—资源最优性（PDF 物理页 1、5，Abstract 与 latency analysis）[pdf:E01][pdf:E05]。

## § 3 — 重建作者的思考路径

可以从已有约束重建出如下思路：

1. 单二极管 PV 模型包含指数函数；若在线求解二极管方程或反复迭代，FPGA 延迟难以固定。
2. boost 的主要动态可压缩为 PV 输入电容电压相关状态、电感电流和输出电容电压三个状态。
3. 选取缩放状态 \(x_1=N_sV_D/a\)，使两项昂贵非线性 \(f(x_1)\) 与 \(I_{dsh}(x_1)\) 都只依赖一个变量，因此可预计算成一维 LUT。
4. 让 \(x_1\) 的有效物理范围铺满 \(2^{14}\) 个地址，避免 LUT 大量地址没有被使用。
5. 用 forward Euler 离散，再把公共项、常数乘法和由开关量控制的乘法重排；\(x_2u\)、\(x_3u\) 用 AND mask 实现，不额外增加时钟。
6. 最后用三个占空比的开环 MyRIO HIL 与同参数 Simulink 浮点模型比较，检查平均值、纹波与暂态（PDF 物理页 3–6，Sections III–VI）[pdf:E03][pdf:E04][pdf:E05][pdf:E06]。

## § 4 — 核心 Intuition

核心 intuition 是：先改变模型表达，再谈硬件加速。只要把 PV 指数关系变成由一个缩放状态寻址的 LUT，把 boost 两种导通拓扑压进逻辑量 \(u\)，并按依赖关系重排 Euler 更新，最慢状态就能在固定 4 个时钟内完成，而不必每步求解非线性方程（PDF 物理页 4–5，Eq. (20)–(23) 与 Table I）[pdf:E04][pdf:E05]。

## § 5 — 具体方法与完整 Pipeline

以 500 W/m² 辐照度、50 kHz PWM 的实验为例，pipeline 如下：

1. **建立 PV 模型。** 单二极管等效电路包含光生电流 \(I_G\)、二极管电流 \(I_d\)、并联漏电 \(I_{sh}\)、串联电阻 \(R_s\) 与并联电阻 \(R_{sh}\)。温度影响被压成常数 \(K_t\)，辐照度 \(G\) 保留为外部输入（PDF 物理页 2，Eq. (1)–(6) 与 Fig. 1）[pdf:E02]。
2. **选三状态。** \(x_1=N_sV_D/a\)，\(x_2=I_L\)，\(x_3=V_{C2}\)。输入电容 \(C_1\) 将 PV 板与电感连接，boost 只建模主导动态，不包含晶体管和二极管的动态损耗（PDF 物理页 3，Figs. 2–4 与 Section III）[pdf:E03]。
3. **统一两种开关拓扑。** 定义 \(u=0\) 表示 Q 导通、D 截止，\(u=1\) 表示 Q 截止、D 导通。\(x_1\) 的动态不直接受开关影响，\(x_2,x_3\) 由 \(u\) 选择对应的电感和输出电容关系（PDF 物理页 3–4，Eq. (11)–(18)）[pdf:E03][pdf:E04]。
4. **forward Euler 离散。** 以步长 \(T\) 计算 \(x(k+1)\)。随后把 \(Tf(x_1)\) 记为 \(f_T(x_1)\)，预合并常数，并把 \(x_2u\)、\(x_3u\) 用组合逻辑 AND mask 实现（PDF 物理页 4，Eq. (20)–(21)）[pdf:E04]。
5. **LUT 映射。** \(f_T(x_1)\) 与 \(I_{dsh}(x_1)\) 分别放入一维 \(2^{14}\) 项、32-bit 输出 LUT，每张约 64 KB。用缩放因子 \(a\) 将 \(0\le x_1\le V_{oc}/a\) 映射到 IQ(14,9) 可用地址范围（PDF 物理页 4，Eq. (22)–(23)）[pdf:E04]。
6. **硬件调度。** MyRIO 1900 FPGA 为 40 MHz；作者按每级加法、乘法或 LUT lookup 占一个时钟分析依赖路径。\(x_1,x_2\) 各需 4 周期，\(x_3\) 需 2 周期，因此最慢延迟为 100 ns（PDF 物理页 5，Table I）[pdf:E05]。
7. **HIL 对比。** 使用 10 个串联 ReneSola Virtus II 250 W 模块、\(R_o=366\,\Omega\)、\(G=500\text{ W/m}^2\)、25 °C、50 kHz PWM；分别令逻辑量 \(u\) 的 duty 为 100%、75%、50%，与 Simulink 运行 100 ms 的状态波形比较（PDF 物理页 5，Section VI 与 Tables II–IV）[pdf:E05]。

## § 6 — 核心数学推导（无形式化数学则跳过）

PV 端把二极管与并联漏电合成：

\[
I_{dsh}(x_1)=I_0\left(e^{a x_1/V_t}-1\right)+\frac{a x_1}{R_{sh}},
\]

再把输入电容动态中的导数项整理成仅依赖 \(x_1\) 的系数 \(f(x_1)\)。三状态连续模型可概括为：

\[
\dot{x}_1=f(x_1)\left(\frac{I_{Gn}}{G_{nom}}G+K_t-I_{dsh}(x_1)-x_2\right),
\]

\[
\dot{x}_2=\frac{1}{L}\left(a x_1-(N_sR_s+R_t)\left[\frac{I_{Gn}}{G_{nom}}G+K_t-I_{dsh}(x_1)\right]-u x_3\right),
\]

\[
\dot{x}_3=\frac{1}{C_2}\left(u x_2-\frac{x_3}{R_o}\right).
\]

这些式子的工程意义是：PV 指数非线性被集中到两个单变量函数，boost 拓扑切换只进入 \(u x_2\) 与 \(u x_3\)，因此 LUT 与组合逻辑可以并行使用（PDF 物理页 3–4，Eq. (11)–(18)）[pdf:E03][pdf:E04]。

离散时采用 \(x(k+1)=x(k)+T\dot{x}(k)\)，随后改写成 Eq. (21) 的流水友好形式（PDF 物理页 4，Eq. (20)–(21)）[pdf:E04]。在理想实数算术中，代数重排不改变模型；在 fixed-point 中，它会改变量化、舍入与 overflow 发生的位置。源 PDF 没有给出每一级位宽、舍入与 saturation 策略，因此复现不能只照抄最终方程，还必须公开数值格式。

## § 7 — 实验设计与结论

**问题一：FPGA fixed-point 结果是否接近软件浮点参考？ → 实验：** MyRIO 与 Simulink 使用同一参数，测试 \(u\) duty 为 100%、75%、50%，比较 \(I_L,V_{C1},V_{C2}\) 的 100 ms 波形。**答案：** 电感电流稳态平均相对误差分别为 -0.011%、0.017%、0.026%；\(V_{C1}\) 分别为 0.013%、0.018%、0.042%；\(V_{C2}\) 的平均稳态误差也接近零。差异主要表现为纹波峰值相位与幅值，作者归因于 FPGA 定点精度（PDF 物理页 6–7，Figs. 5–13 与对应正文）[pdf:E06][pdf:E07]。

**问题二：是否达到 100 ns 实时步进？ → 实验：** 作者按 MyRIO 的运算级数规则分析 Eq. (21) 的依赖路径。**答案：** 最长路径 4 个 40 MHz 时钟，即 100 ns（PDF 物理页 5，Table I）[pdf:E05]。这是一项结构/时钟级 latency analysis，不是附有 post-route timing report 的实测；论文也没有明确给出 pipeline initiation interval，所以“每 100 ns 可接受一个新状态”与“输出 latency 为 100 ns”仍需综合实现确认。

**问题三：LUT 缩放是否在不增加延迟时提高分辨率？ → 实验事实：** Eq. (22)–(23) 把 \(x_1\) 有效范围铺到 \(2^{14}\) 地址，LUT access 仍计一个时钟。**答案：** 地址利用率改进有解析依据，但论文没有缩放前后误差消融，也没有 LUT 深度—资源—误差曲线（PDF 物理页 4，Section V-A）[pdf:E04]。

**问题四：是否比软件仿真快？ → 实验：** 100 ms HIL 实时完成；Simulink 在 AMD A6-7310 2 GHz PC 上需要 10–13 s。**答案：** 对该 PC 与设置，FPGA 明显更快，但不能外推到现代 CPU、优化求解器或其他商业 HIL 平台（PDF 物理页 5，Section VI）[pdf:E05]。

实验边界是：只做开环 duty 测试，温度固定，未加入器件动态损耗；没有实物 PV-boost 电路作为第三方真值，也没有辐照度、负载、电感、开关频率或工作模式扫参（PDF 物理页 1、3、5，Abstract、Section III、Section VI）[pdf:E01][pdf:E03][pdf:E05]。

## § 8 — Take-aways

**5 句话：**

1. 论文把 PV+boost 压缩成一个三状态非线性开关模型（PDF 物理页 3–4，Eq. (11)–(18)）[pdf:E03][pdf:E04]。
2. 两个指数相关函数只由 \(x_1\) 寻址，因此可以预计算到一维 LUT（PDF 物理页 4，Section V-A）[pdf:E04]。
3. 状态缩放让有效物理范围铺满 \(2^{14}\) 地址，而不增加一次 LUT 访问的时钟数（PDF 物理页 4，Eq. (22)–(23)）[pdf:E04]。
4. 重排后的 Euler 更新最长依赖路径为 4 个 40 MHz 时钟，即论文所称的 100 ns（PDF 物理页 5，Table I）[pdf:E05]。
5. FPGA 波形与 Simulink 参考接近，但资源、成本、实物准确性与 CCM/DCM 模式边界未闭合。

**3 句话：** 核心贡献是硬件映射，不是新的 PV 物理模型。LUT、状态归一化和算术路径重排共同产生低 latency。现有实验验证了与软件参考的一致性，却没有证明真实 PV boost 全工作区间内的有效性。

**1 句话：** 这是一个映射思路清楚、分析延迟很低，但工作模式与硬件资源证据仍不完整的 FPGA-HIL 内核。

## § 9 — 最脆弱的假设

最脆弱的假设是：实验所需范围始终可以只用“Q 导通/D 截止”和“Q 截止/D 导通”两个拓扑描述，即电感电流保持 CCM（continuous conduction mode）。Eq. (14)–(18) 只用一个逻辑量 \(u\) 选择两种状态方程；模型没有表示 Q 截止后电感电流降到零、二极管也截止的第三个 DCM 模式（PDF 物理页 3–4，Figs. 3–4 与 Eq. (14)–(18)）[pdf:E03][pdf:E04]。

在低辐照、轻载、小电感或某些 duty 下，\(I_L\) 可能在一个周期内到零。把负值 saturate 到零只能防止非物理负电流，不能恢复零电流区间的正确拓扑、持续时间与状态转移。论文只测试 \(L=16\text{ mH}\)、\(R_o=366\,\Omega\)、\(G=500\text{ W/m}^2\) 和三个开环 duty，没有扫描零电流边界（PDF 物理页 5，Tables III–IV 与 Section VI）[pdf:E05]。若 CCM 假设失效，失效的是核心电路模型，而不只是 fixed-point 误差。

## § 10 — 最小复现实验

一周内最小复现应验证“100 ns 硬件 deadline 与数值一致性是否同时成立”：

1. **数据与参数。** 采用 Tables II–IV：\(R_{sh}=200.32\,\Omega\)、\(R_s=0.3832\,\Omega\)、\(V_t=1.42\text{ V}\)、\(I_0=30.295\text{ pA}\)、\(N_s=60\)、\(I_{Gn}=9.06\text{ A}\)、\(R_t=0.22\,\Omega\)、\(C_1=82\,\mu\text{F}\)、\(C_2=150\,\mu\text{F}\)、\(L=16\text{ mH}\)、\(R_o=366\,\Omega\)、\(G=500\text{ W/m}^2\)、50 kHz PWM（PDF 物理页 5）[pdf:E05]。
2. **实现。** 先实现 double-precision Eq. (20) golden model，再实现 Eq. (21) fixed-point 版本和两个 \(2^{14}\) LUT；逐级记录位宽、rounding 与 saturation。
3. **测量。** 报告三个 duty 下三状态的平均、ripple 幅值与相位误差；读取 post-route fmax、critical path、BRAM/DSP/LUT/FF 利用率，并区分 latency 与 initiation interval。
4. **支持 claim。** 40 MHz 时序收敛，连续状态更新的真实间隔不超过 100 ns，三个状态平均相对误差保持在论文约 0.05% 范围内且无 overflow。
5. **反驳 claim。** 必须增加周期或降低时钟才能收敛；fixed-point/LUT 误差明显放大；或 100 ns 只是输出 latency，不能按该间隔推进闭环状态。

## § 11 — 最强反例设计

最强反例是在 CCM/DCM 边界附近测试。降低辐照度和负载电流，或减小电感，使 \(I_L\) 在 Q 关断阶段降到零；同时以包含二极管自然关断的高精度开关模型和真实 boost 原型作为参考。逐步扫过零电流边界，比较二极管导通时间、下一周期初始电流、输出电压、纹波相位及控制器观测到的 plant dynamics。

若论文模型在进入 DCM 后仍保持较小平均误差，却持续错误预测导通区间，说明当前 Simulink 对比中的“平均值吻合”掩盖了拓扑错误。若闭环控制器据此得到错误的稳定裕度或 MPPT 瞬态判断，就会直接挑战该内核作为通用 PV-boost HIL plant 的有效性（PDF 物理页 3–4 的两拓扑模型是该反例的直接攻击对象）[pdf:E03][pdf:E04]。

## § 12 — Follow-up Research Idea

**候选想法：面向工作模式有效性与 deadline 证明的自适应 FPGA-HIL 内核。**

（a）未满足需求是：真实 PV 控制器会经历启动、遮阴、轻载、限流和故障，固定 CCM 内核无法保证这些阶段的 HIL 结果可信。（b）电力电子实时仿真的高价值证据应同时包括跨工作区间的实机对照、确定性最坏执行时间、资源代价与误差界。（c）可借鉴 hybrid automaton 的 event detection、多速率实时仿真和 fixed-point interval error analysis：由零电流、二极管电压等事件触发拓扑切换，平滑区使用快速内核，事件邻域切换到局部高保真更新。（d）第一个证伪实验就是上一节 CCM→DCM 扫描；若模式感知内核不能在固定 deadline 内降低真实硬件的换流误差，想法即失败。（e）它与本文的实质区别是评价目标从“一个预设模型的最短算术路径”变为“模型何时有效、何时切换、误差与最坏时间是否可界定”。

在没有系统检索最新 mode-aware FPGA real-time simulation 文献前，这只能称为候选研究方向，不声称具有 novelty。
