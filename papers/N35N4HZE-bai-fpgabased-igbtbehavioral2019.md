# An FPGA-Based IGBT Behavioral Model With High Transient Resolution for Real-Time Simulation of Power Electronic Circuits

- 作者：Hao Bai；Chen Liu；Akshay Kumar Rathore；Damien Paire；Fei Gao
- 出处：*IEEE Transactions on Industrial Electronics*, 66(8), 6581–6591
- 年份：2019
- DOI：10.1109/TIE.2018.2870354
- Zotero key：N35N4HZE

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

IGBT 的一次开关并不是从“断”瞬间跳到“通”。栅极先给电容充电，集电极电流上升，栅极进入 Miller plateau 后集电极—发射极电压下降；关断时又会出现少数载流子造成的 tail current，续流二极管还可能带来 reverse recovery。于是 \(v_{ce}\) 与 \(i_{ce}\) 会在几十到几百纳秒内重叠，重叠面积就是开关能量损耗，并进一步影响结温、器件应力和控制器参数整定。论文的 Fig. 5 把导通分成六段、关断分成四段，明确画出了 Miller plateau、反向恢复和尾电流这些物理过程；Eq. (17) 又把尾电流写成一阶指数衰减。[pdf:E04](_evidence/E04-p004-turnon-stages-eq06-16.png) [pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png)

研究问题因此是：怎样在 FPGA 实时仿真中保留上述纳秒级器件瞬态，同时不让非线性器件模型的迭代求解拖垮系统级实时步长？作者指出，传统理想开关或两段线性开关只描述稳态 ON/OFF，不能给出真实的电压—电流重叠；而详细非线性模型需要迭代，瞬态本身又可能短于 100 ns，这形成“模型越真实越算不动、步长越大越看不见瞬态”的矛盾。[pdf:E01](_evidence/E01-p001-title-abstract-problem.png)

论文直接声称，其方法把静态与动态行为分离，在 FPGA 上以 5 ns 间隔生成开关瞬态，并用四相 FIBC 与三相五电平 MMC 两个算例对比 Saber 离线模型。[pdf:E01](_evidence/E01-p001-title-abstract-problem.png) 这里的价值不只是让波形更好看：如果瞬态的电压、电流和功率脉冲能够以实时速度输出，HiL 才可能同时服务控制验证、开关损耗估算和后续热模型。后两项是基于论文物理链条的合理推断，不等于论文已经用实物温升实验验证。

## § 2 — 前人工作与不足

论文把已有方法分成几类。理想开关、two-value conductance、Thevenin equivalent 和 associated discrete circuit (ADC) 模型计算快，但只有理想状态或 ON/OFF 两段，缺少器件真实切换过程。[pdf:E01](_evidence/E01-p001-title-abstract-problem.png) 测量波形后按工况缩放的方法速度快，却要做大量参数辨识，而且难以迁移到别的 IGBT 或驱动电路；Hefner 物理模型准确但计算复杂度高，限制实时步长与电路规模。datasheet-based electro-thermal 模型依赖额定电压、电流、最高结温和特定驱动条件下的数据，且可能缺少关键参数或 gate behavior；基于 gate-charge 曲线的 Wiener–Hammerstein 模型同样受特定测试条件约束，论文报告其动态步长为 100 ns，对短于 200 ns 的瞬态仍不够。[pdf:E02](_evidence/E02-p002-prior-model-contribution.png)

因此，作者不是简单地把一个更复杂的 IGBT 方程塞进 FPGA，而是改变计算分工：系统级只求稳态端点，器件级再显式生成端点之间的瞬态轨迹。作者把该方案称为 innovative，但本卡没有补充检索最邻近工作的完整全文，不能独立确认 novelty；能够确认的是论文自己给出的差异定位和其内部实验。

## § 3 — 重建作者的思考路径

可以把作者的思路重建为四步。第一，真实开关损耗来自纳秒级过渡，而系统电感、电容状态通常按微秒或亚微秒步长推进，两类状态的时间尺度并不相同。第二，若每个 5 ns 都把电压相关电容和受控电流源放回全网求解，迭代会成为实时瓶颈。第三，开关瞬态虽非线性，却具有明确的物理阶段：阈值充电、集电极电流建立、二极管反向恢复、Miller plateau、电压下降、稳态充电，以及关断尾电流。第四，若每段用线性或一阶指数形式表达，系统级每次开关只需计算阶段时长、斜率和时间常数，器件级就能用流水线逐点输出波形。[pdf:E03](_evidence/E03-p003-static-dynamic-eq01-05.png) [pdf:E04](_evidence/E04-p004-turnon-stages-eq06-16.png)

这条路径的关键不是“FPGA 很快”，而是先把需要反复迭代的连续非线性问题改写成一次参数计算加显式分段轨迹，再利用 FPGA 的并行和 pipeline。这个重建是基于论文方法结构的推断；作者没有把它以这四步原样表述。

## § 4 — 核心 Intuition

稳态网络只需要知道 IGBT 在系统步长端点的等效导纳和电流源；只有开关事件附近才需要纳秒级细节。作者让系统级硬件计算新稳态端点和一组 \(\Delta t_i\)、\(k_i\)、\(\tau_i\)，再让 200 MHz 的器件级流水线把这组参数展开成 \(v_{ce}\)、\(i_{ce}\)、\(v_{ge}\) 与 \(P_D\) 的 5 ns 间隔轨迹。[pdf:E03](_evidence/E03-p003-static-dynamic-eq01-05.png) [pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png)

普通语言说，就是不让整个电路跟着器件的每个纳秒小动作重算，而是在慢时间尺度求“从哪里到哪里”，在快时间尺度按物理阶段补出“中间怎么走”。论文 Fig. 6 的上下两条时间轴直接展示了 40 MHz system-level sequence 与 200 MHz device-level pipelined output 的这种配合。[pdf:E06](_evidence/E06-p005-fpga-overview-fig06.png)

## § 5 — 具体方法与完整 Pipeline

以四相 FIBC 中某一只 IGBT 的一次导通为例，完整 pipeline 如下。

1. **系统级静态模型。** IGBT 饱和区输出特性被分段线性化成 Norton 等效导纳 \(G_S\) 与电流源 \(I_S\)，进入 nodal network solver。系统级时间尺度是微秒或亚微秒，结温可反馈到静态参数。[pdf:E03](_evidence/E03-p003-static-dynamic-eq01-05.png)
2. **求新稳态端点。** 网络求解得到该系统步的新 \(V_{ce}\) 与 \(I_{ce}\)。论文示例采用 explicit-integration-based circuit partitioning，把子电路写成可并行的 matrix-vector multiplication；作者也明确说网络求解本身不是本文重点。[pdf:E07](_evidence/E07-p006-system-hardware-timing.png)
3. **Transient Parameters Computation (TPC)。** TPC 根据稳态端点、gate voltage/resistance、\(C_{ge}\)、分段 \(C_{cg}\)、transfer characteristics、二极管 reverse-recovery 曲线与结温，计算每个阶段的持续时间 \(\Delta t_i\)、线性斜率 \(k_i\) 和指数时间常数 \(\tau_i\)。transfer curve、reverse-recovery curve 以及 \(\ln(x)\)、\(e^x\) 均用 LUT 支持，模块按 one-cycle initiation interval 做 pipeline。[pdf:E07](_evidence/E07-p006-system-hardware-timing.png)
4. **六段导通过程。** 栅压先充到阈值；\(i_{ce}\) 线性升至负载电流；续流二极管产生反向恢复；随后 \(v_{ce}\) 先在小 \(C_{cg}\) 区快速下降，再在 Miller plateau 与较大 \(C_{cg}\) 区慢速下降；最后栅压到达稳态。关断按四段处理，前三段近似为导通后半段的逆过程，最后一段叠加指数 tail current。[pdf:E04](_evidence/E04-p004-turnon-stages-eq06-16.png) [pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png)
5. **器件级波形生成。** stage selector 根据计数器和 \(\Delta t_i\) 选取对应的线性或指数计算路径，逐个 200 MHz 时钟输出 \(i_{ce}\)、\(v_{ce}\)、\(v_{ge}\)，再计算 \(P_D\)。论文采用 40-bit fixed-point；200 MHz 对应 5 ns 输出间隔。[pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png) [pdf:E08](_evidence/E08-p007-device-hardware-validation.png)
6. **平台映射。** 系统级硬件以 40 MHz 运行，器件级以 200 MHz 运行，目标器件为 NI-7975R FlexRIO 中的 Kintex-7 XC7K410T；LabVIEW FPGA 的 IP Builder 用 Vivado HLS 合成模块并在 SCTL 内执行。[pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png) [pdf:E08](_evidence/E08-p007-device-hardware-validation.png)

这个 pipeline 的输出是可观察的详细瞬态，但系统网络并没有在每个 5 ns 点重新闭环求解。这个区别决定了它对强寄生耦合、谐振换流等工况的适用边界。

## § 6 — 核心数学推导

数学骨架是把非线性电容和器件过程改写成可在 FPGA 上执行的分段显式式子。

首先，\(C_{cg}\) 随 \(v_{ce}\) 变化：在 \(V_{ce(min)}\) 处取大电容 \(C_{cg(l)}\)，在 \(V_{ce(min)}<v_{ce}\le V_{tp}\) 区间用 \(k_Cv_{ce}+b_C\) 线性近似，超过 \(V_{tp}\) 后取小电容 \(C_{cg(s)}\)，这就是 Eq. (1)。对 gate 回路写 KCL 得到 Eq. (2)；当 \(C_{cg}\) 为常数时得到 Eq. (3)，在 Miller plateau 令 \(\dot v_{ge}=0\) 则得到 Eq. (5)。物理意义是：\(C_{cg}\) 决定 gate current 有多少被用于改变 \(v_{ce}\)，Miller plateau 把栅压暂时“钉住”，从而形成电压下降阶段。[pdf:E03](_evidence/E03-p003-static-dynamic-eq01-05.png)

其次，导通 stage 1 把 \(C_{ies(s)}=C_{ge}+C_{cg(s)}\) 看成由 \(R_g\) 充电的一阶网络，时间常数为 \(\tau_1=R_g(C_{ge}+C_{cg(s)})\)。Eq. (6) 给出 \(v_{ge}\) 的指数充电，Eq. (7) 通过令 \(v_{ge}=V_{th}\) 反解到阈值的时间；stage 2 再用 Eq. (8) 求到支撑负载电流所需栅压的时间，并以 Eq. (9) 的 \(k_{i1}^{on}=I_L/\Delta t_2^{on}\) 近似电流上升斜率。[pdf:E04](_evidence/E04-p004-turnon-stages-eq06-16.png)

再次，二极管 reverse-recovery 峰值 \(I_{rr}\) 由 datasheet 曲线按负载电流和电流下降率插值，Eq. (10) 用“峰值除以斜率”求 stage 3 时长。stage 4–5 分别在小 \(C_{cg}\) 与线性变化 \(C_{cg}\) 区间推导 \(v_{ce}\) 斜率和持续时间，Eq. (11)–(16) 本质上都是“给定阶段端点和 gate 方程，反解该段斜率/时长”。[pdf:E04](_evidence/E04-p004-turnon-stages-eq06-16.png) [pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png)

关断最后一段把快速下降后的 tail current 写成

\[
i_{ce}(t)=\alpha I_{ce(on)}e^{-t/\tau_{HL}},
\]

其中 \(\alpha\) 是快速下降前后电流比，\(\tau_{HL}\) 由 datasheet 的 current fall time 取得；论文对给定 IGBT 把二者视为常数。[pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png) 温度效应则用 Eq. (18) 在 \(25^\circ\mathrm{C}\) 与 \(150^\circ\mathrm{C}\) 的 datasheet 参数间做线性插值。最后所有阶段归一为硬件友好的 \(u(t)=kt+U_0\) 或 \(u(t)=(U_0-U_{in})e^{-t/\tau}+U_{in}\)，分别对应 Eq. (19)、(20)。[pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png) [pdf:E08](_evidence/E08-p007-device-hardware-validation.png)

这里最重要的数学代价是：显式可流水化来自分段线性、一阶指数、固定阶段次序和参数插值这些近似，而不是无损地化简了原始非线性器件方程。

## § 7 — 实验设计与结论

**问题 1：硬件能否按要求实时产出瞬态？** 作者把系统级 static model、network solution、TPC 和 device-level dynamic model映射到 XC7K410T。Table I 报告 static model 为 25 ns，FIBC/MMC network solution 分别为 25/100 ns；TPC 在多开关情形下，FIBC 为 450 ns（40 MHz）或 520 ns（200 MHz），MMC 为 950 ns（40 MHz）或 620 ns（200 MHz）；dynamic model 在 200 MHz 下 latency 为 120 ns，但 initiation interval 为一周期，因此进入流水线后可每 5 ns 输出一点。[pdf:E07](_evidence/E07-p006-system-hardware-timing.png) 这支持“5 ns 输出分辨率”，但 5 ns 不是整个模型从输入到首个输出的端到端 latency。

**问题 2：资源是否容得下实际变换器？** 四相 FIBC 使用 4 个 dynamic models；五电平 MMC 有 48 个 IGBT/diode pairs，但同一 SM 内两只 IGBT 的瞬态不独立，因此只实现 24 个 dynamic models。Table III 报告 FIBC/MMC 分别使用 11.1%/18.2% slice registers、24.7%/41.1% slice LUTs、11.6%/11.6% block RAM 和 10.5%/25.2% DSP48s。[pdf:E08](_evidence/E08-p007-device-hardware-validation.png)

**问题 3：FIBC 波形是否接近参考模型？** FIBC 的系统级步长是 1 μs，器件级步长是 5 ns；作者把 FPGA 实时结果与 Saber 的 `igbt1_3` datasheet-driven electro-thermal model 对比。Fig. 11 显示系统量和开关瞬态的总体形状接近，本卡不从曲线估读精确值。[pdf:E08](_evidence/E08-p007-device-hardware-validation.png) [pdf:E09](_evidence/E09-p008-fibc-fig11.png) Table V 给出的平均误差为：\(V_{C1}\) 0.22%、\(V_{out}\) 0.23%、\(I_L\) 与 \(I_{in}\) 均 1.01%、\(E_{turn-on}\) 4.09%、\(E_{turn-off}\) 10.8%。作者把较大的关断能量误差归因于关断电流波形差异，且明确指出线性电流上升导致 \(t_r\) 差异、瞬时快速下降假设使 \(t_{d(off)}\) 偏大。[pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png)

**问题 4：复杂大规模拓扑是否仍可运行？** 三相五电平 MMC 采用 2 μs 系统步长、40 MHz 系统时钟和 24 个 dynamic models。Fig. 12 对比了三相输出、负载电流和器件开关瞬态，本卡只采用其“总体趋势一致”的定性信息，不估读曲线值。[pdf:E11](_evidence/E11-p009-mmc-fig12.png) Table VII 报告 \(V_{out}\) 0.87%、\(I_{load}\) 0.79%、\(E_{on}\) 5.76%、\(E_{off}\) 9.68%。[pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png)

**结论边界。** 论文直接结论是：所提模型以显著提高实时效率为代价，取得了作者认为可接受的误差，并能把理想或准理想 FPGA 开关模块升级为 detailed behavioral model。[pdf:E12](_evidence/E12-p009-conclusion-appendix.png) 更严格地说，实验支持的是“相对 Saber 参考模型、在同一 Infineon IGW40T120 datasheet 参数化和两个变换器案例下的一致性”；它没有展示与双脉冲实测波形的直接对照，也没有证明对任意器件、寄生参数或驱动条件都准确。

## § 8 — Take-aways

**5 句话：**

1. 论文把 IGBT 的慢稳态网络行为与快开关瞬态分开计算，从根本上避免全网 5 ns 迭代。
2. 动态模型把导通分成六段、关断分成四段，用线性和一阶指数近似 gate charging、Miller plateau、reverse recovery 与 tail current。
3. 系统级只计算稳态端点及 \(\Delta t_i\)、\(k_i\)、\(\tau_i\)，200 MHz 器件级 pipeline 每 5 ns 输出 \(v_{ce}\)、\(i_{ce}\)、\(v_{ge}\) 和 \(P_D\)。
4. 在四相 FIBC 和五电平 MMC 上，相对 Saber 参考模型的系统量误差低于 1.1%，但开关能量误差明显更大，尤其关断为 10.8% 和 9.68%。[pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png)
5. 方法的强项是确定时序和硬件可实现性，弱项是其准确性取决于分段轨迹和慢—快解耦是否覆盖真实器件与外部寄生耦合。

**3 句话：**

1. 作者用“慢网络求端点、快流水线补瞬态”换取器件级实时波形。
2. 5 ns 是稳态吞吐分辨率而不是整条计算链的 latency，准确性也只相对 Saber 得到验证。
3. 能量误差比系统电压电流误差更敏感，说明最值得继续检验的是开关瞬态形状而非稳态输出。

**1 句话：** 这是一种把 IGBT 开关瞬态改写成事件触发、分段显式、可流水化轨迹生成器的 FPGA 实时建模方法。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在一个微秒级系统步长内，外部网络只需提供开关前后的稳态端点，器件的 5 ns 瞬态可以离线式地在这两个端点之间展开，而无需把每个快时间点重新反馈进网络方程。** Fig. 2 与 Fig. 6 显示 network solver/TPC 先产生静态值和阶段参数，device-level 随后输出瞬态；这正是高吞吐的来源。[pdf:E03](_evidence/E03-p003-static-dynamic-eq01-05.png) [pdf:E05](_evidence/E05-p005-turnoff-temp-eq17-18.png)

如果换流回路存在显著 stray inductance、非线性寄生电容、振铃、soft switching 或强反向恢复耦合，器件瞬态会反过来改变端口电压、电流，预先确定的端点与阶段次序就可能失效。论文给出的支持证据是 FIBC 与 MMC 相对 Saber 的波形和平均误差；反面信号则是能量误差远大于系统量误差，且作者自己承认线性上升与瞬时快速下降会造成 \(t_r\)、\(t_{d(off)}\) 和关断能量偏差。[pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png) 论文没有给出寄生参数、驱动电阻、母线电压、负载电流和结温的系统扫参，也没有直接实测验证这个解耦假设，因此其跨工况稳健性仍不确定。

## § 10 — 最小复现实验

一周内最小可行复现应聚焦“分段显式模型是否能在不迭代的前提下重现关键开关量”，而不是重建整套 MMC。

- **数据：** 使用论文 Appendix 指定的 Infineon IGW40T120 datasheet 参数；参考工况先取论文 FIBC 的 72 V、10 kHz、\(R_g=30\,\Omega\)、0/15 V gate drive，并保留论文 Table IV/V 作为目标结果。[pdf:E08](_evidence/E08-p007-device-hardware-validation.png) [pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png) 若 datasheet 版本或所需曲线无法核实，则停止把结果称为严格复现。
- **实现：** 在 Python、MATLAB 或 C 中实现 Eq. (1)–(20) 的单 IGBT stage generator；输入一次网络求解给出的 \(V_{ce(off)}\)、\(V_{ce(on)}\)、\(I_L\)、温度与 gate 参数，输出 5 ns 栅压、电压、电流和功率序列。并行再用 Saber `igbt1_3` 或可核实的等价 reference model 运行同一 double-pulse 工况。
- **测量：** 计算 \(t_{d(on)}\)、\(t_r\)、\(t_{d(off)}\)、\(t_f\)、\(E_{on}\)、\(E_{off}\)，确认生成器没有迭代且连续样点间隔确为 5 ns；不从论文图上估读数值，直接与 Table IV/V 的报告值和复现实验的 reference trace 比较。
- **支持标准：** 预注册为“开关时间能复现 Table IV 的数量级与相对偏差方向，能量误差不劣于论文报告的 4.09%/10.8%，且每个样点计算路径无数据依赖迭代”。这是本卡提出的复现判据，不是作者原文标准。
- **反驳标准：** 同一参数下无法重现阶段顺序，或 \(E_{off}\) 明显超过 10.8%，或必须引入逐样点网络迭代才能保持波形稳定，就反驳最核心的工程 claim。

## § 11 — 最强反例设计

最强反例不是再换一个拓扑，而是做一组带可控寄生的硬件 double-pulse tests，专门制造“器件瞬态反过来改变网络端点”的情形。对同一 IGW40T120，同时扫描母线电压、负载电流、结温和 \(R_g\)，再插入三档 commutation-loop stray inductance；用高带宽探头实测 \(v_{ce}\)、\(i_{ce}\)、\(v_{ge}\)，并让论文模型只使用 datasheet 与系统步端点，不用实测波形重新拟合。

攻击的判据应是：随着 stray inductance 增大，若实测出现过冲、振铃、Miller plateau 变化或 reverse-recovery 耦合，而分段模型仍给出同一阶段次序和单调轨迹，则即使稳态 \(V_{out}\) 误差很小，模型对 peak stress 与 \(E_{off}\) 的用途也被推翻。论文 Fig. 11/12 的参考结果主要展示平滑的单调切换波形，Table V/VII 已显示关断能量是误差最大项，这使该反例直接针对其最弱环节，而不是泛泛要求更多案例。[pdf:E09](_evidence/E09-p008-fibc-fig11.png) [pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png) [pdf:E11](_evidence/E11-p009-mmc-fig12.png)

## § 12 — Follow-up Research Idea

在电力电子与实时仿真领域，高影响工作通常不仅要给出更小步长，还要同时证明物理可信度、确定的实时执行上界、跨工况泛化和硬件可复现性。基于第 9 节，候选方向是：**把研究目标从“生成一条看似准确的瞬态波形”改成“实时生成带可验证误差边界的器件端口轨迹”**。由于本卡没有充分检索 2019 年后的相邻工作，这只是候选研究方向，不声称 novelty。

（a）未满足需求是：控制 HiL 可以容忍少量形状误差，但器件应力和热设计需要知道 \(E_{on/off}\)、峰值电压和峰值电流的误差上界；现有论文只给两个算例的平均误差。[pdf:E10](_evidence/E10-p008-fibc-tables-mmc.png)

（b）研究价值在于把“5 ns 波形”升级为“5 ns 波形加可信区间”，让使用者知道何时可以相信模型、何时必须回退到更细的网络—器件联合求解。

（c）可借鉴 hybrid systems 的 reachability、interval arithmetic 与 uncertainty-aware surrogate modeling：保留论文的显式 stage generator 作为 nominal trajectory，同时用少量 double-pulse 数据建立参数区间，并实时传播到 \(v_{ce}\)、\(i_{ce}\)、\(P_D\) 的上/下界；当区间宽度越过阈值时，不继续伪装成精确模型，而触发局部耦合求解。

（d）第一个证伪实验就是 §11 的扫参 double-pulse grid：如果任何实测波形落在预测区间之外，或区间传播/局部回退使最坏计算时间超过实时步长，则研究假设失败。

（e）它与本文的实质区别不是多加一个校正模块，而是改变验收对象：本文优化的是确定吞吐下的一条 point estimate；候选工作优化的是在相同实时约束下仍能闭合的 worst-case error guarantee。只有后者在跨温度、驱动和寄生参数测试中成立，才足以支持把器件级实时波形用于保护与热可靠性决策。
