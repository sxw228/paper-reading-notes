# Design and Implementation of a Reconfigurable Phase Shift Full-Bridge Converter for Wide Voltage Range EV Charging Application

作者：Dingsihao Lyu；Thiago Batista Soeiro；Pavol Bauer  
出处：IEEE Transactions on Transportation Electrification  
年份：2022  
DOI：10.1109/TTE.2022.3176826  
Zotero key：FU4FCKQE  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“做一个效率更高的 PSFB”这么宽泛的问题，而是：同一台隔离型 EV 充电 dc/dc 变换器怎样覆盖 400-V 与 800-V 两类电池，并且不让低输出电压区因为过大的 phase shift、环流和器件电流应力而成为效率洼地。作者指出，当时带样机验证的文献主要覆盖 400-V 级电池，没有一台隔离 dc/dc 样机同时覆盖两类电压；为此他们把目标明确为 640–840-V 输入、250–1000-V 输出和 11-kW 功率，并以传统 PSFB 作为同规格基准。论文摘要还给出最终样机的 SiC 版本峰值效率 98.3%，把“宽范围”与“高效率”放在同一个工程约束里，而不是分别证明。[pdf:E01]（PDF 物理第 1 页，Abstract、Introduction、Fig. 1）

这个问题的重要性来自充电基础设施的兼容性。若为不同电池电压分别配置充电模块，会增加设备类型、库存与站端复杂度；若用单一固定变比 PSFB 硬做宽范围降压，则低压端要付出更大的 phase shift 和电流应力。论文的价值在于把“电压覆盖范围”从单纯提高器件耐压，改写成二次侧连接关系的选择问题，使器件额定值、损耗、磁件设计和充电周期效率可以一起讨论。

## § 2 — 前人工作与不足

论文把已有路线分为三类。第一类是传统或改进型 PSFB：它们可以通过 ZVS/ZCS、附加箝位网络或二次侧有源器件减小环流和尖峰，但常以额外器件、无源件或控制复杂度为代价，而且固定变比下低输出电压仍要求更大的 phase shift。第二类是 LLC/CLLC 等谐振变换器：它们在接近谐振点时效率高，但宽电压调节会扩大频率范围或迫使系统增加 SEPIC、buck、二次侧延时控制等额外调节自由度。第三类是 Sun 等人的可重构 PSFB：已有工作证明二次侧串并联和更多重构级能够扩展电压范围，也研究过切换控制、稳定性、ZVS 和损耗，但没有把 EV 充电所需的 250–1000-V 范围、二次侧电压振铃、两种输出滤波结构、详细电流应力模型以及与同规格传统 PSFB 的样机级 benchmark 一起闭合。[pdf:E02]（PDF 物理第 2 页，Introduction）

因此，论文的增量不是“首次想到串并联二次侧”。作者明确继承了既有 reconfigurable structure，真正补的是面向宽电压 EV 充电的完整设计链：选结构、建稳态应力模型、定器件与磁件、设计 RCD snubber，再用同规格传统 PSFB 和实际样机验证。这个边界很重要，因为它避免把系统工程整合误写成全新拓扑。

## § 3 — 重建作者的思考路径

从论文之前已经存在的背景出发，可以重建出如下路径。首先，400-V 与 800-V 电池把充电器输出范围拉得很宽，而固定输入母线意味着不能靠上游 dc-link 跟随电池电压。其次，PSFB 在输出电压远低于变压器自然变比时需要较大 phase shift，电流应力和损耗随之恶化；仅更换为更昂贵的器件并没有改变这个几何关系。再次，如果变压器提供两组相同二次绕组，那么高压端把两路整流输出串联，低压大电流端把两路并联，就能在不改变主桥的情况下改变有效变比和电流分担。作者据此选择带独立 LC filter 与独立 RCD snubber 的结构：它虽然增加滤波与箝位元件数量，却让电容、二极管和辅助开关承受更低电压或电流，并改善二次侧均流与热分布。[pdf:E03]（PDF 物理第 3 页，Fig. 2 与贡献列表）

最后，因为论文假定两类电池的充电电压区间不重叠，配置可以在能量传输前根据充电请求决定，辅助开关便可以采用低导通损耗的机械 relay，而不必在带载期间换态。这一步把一个本来需要 hybrid switching control 的动态问题，缩成了每次充电只选一次拓扑的静态问题。后续建模也因此可以把两种配置分别化成等效传统 PSFB，而不是为换态瞬间建立统一动态模型。

## § 4 — 核心 Intuition

核心 intuition 是：不要用同一个固定变比覆盖四倍输出电压范围，而是在低压端把两路二次侧并联成 current doubler，在高压端把它们串联成 voltage doubler，让主桥在两个区间都靠近较有利的 phase-shift 工作区。串联时 `Saux,1=ON、Saux,2/3=OFF`，并联时状态相反；作者把阈值设在两类电池电压区间之间，并假定一次充电过程中无需改变配置。[pdf:E04]（PDF 物理第 4 页，Section II-B、Table I）这样获得的效率提升不是来自某个新的软开关脉冲，而是来自“在边界处重置等效变比”，从源头降低低压区所需 phase shift 与电流应力。

## § 5 — 具体方法与完整 Pipeline

以一辆向充电桩报告目标电压的 EV 为例，完整 pipeline 如下。

1. **会话前选配置。** 充电器先读取车辆请求的电压、电流，并与重构阈值 \(V_{\mathrm{re}}\) 比较。低于阈值选择二次侧并联，高于阈值选择二次侧串联；辅助 relay 在能量传输前定态，论文没有实施带载重构。[pdf:E04]（PDF 物理第 4 页，Section II-B）
2. **把两种物理拓扑映射为同一个等效 PSFB。** 在串联模式下，等效变比、输出电感和电容分别是 \(n_{\mathrm{eff}}=n/2\)、\(L_{\mathrm{out(eff)}}=2L_{\mathrm{out,sp}}\)、\(C_{\mathrm{out(eff)}}=C_{\mathrm{out,sp}}/2\)；并联模式下则是 \(n_{\mathrm{eff}}=n\)、\(L_{\mathrm{out(eff)}}=L_{\mathrm{out,sp}}/2\)、\(C_{\mathrm{out(eff)}}=2C_{\mathrm{out,sp}}\)。主桥仍以固定频率、每个桥臂 50% duty 的 phase-shift modulation 工作，并经历 active、reactive、commutation 和两个 dead-time transition 阶段。[pdf:E05]（PDF 物理第 5 页，Fig. 3、Fig. 4、Table II）
3. **离线计算稳态应力。** 作者先把输入电压和漏感反射到等效二次侧，再由初始电感电流判定 CCM/DCM，求 duty、commutation interval、各段电流，最后计算主桥 IGBT/MOSFET、反并联二极管、整流二极管和变压器绕组的 rms/average current。该模型是器件设计和损耗估算的离线解析模型，不是在线控制器中的离散状态更新。[pdf:E06]（PDF 物理第 6 页，Eq. (1)–(5)、Eq. (11)–(16)、Table III）
4. **固定设计包络。** 论文把样机约束设为输入 640–840 V、输出 250–1000 V、15-kHz switching、11 kW、最大输出电流 30 A，并在 500 V 处把 250–500 V 分配给并联模式、500–1000 V 分配给串联模式。解析模型与 LTspice 在给定工况下的电流应力曲线相符，但论文没有报告最大相对误差或置信区间。[pdf:E07]（PDF 物理第 7 页，Fig. 5、Table IV、Eq. (6)–(10)）
5. **按最坏工况选变压器、滤波器和半导体。** 阈值确定后，作者计算变压器变比、输出电感和输出电容；同一规格下，Table V 给出的最坏主桥 lagging-leg IGBT rms 电流从传统 PSFB 的 34.3 A 降至 r-PSFB 的 25.2 A，整流二极管最大电压从 1382 V 降至 690 V。这里的应力值来自解析模型，不是直接由全范围电流探头测得。[pdf:E08]（PDF 物理第 8 页，Eq. (17)–(20)、Table V）
6. **把磁件作为效率、功率密度与温升的联合设计。** 设计流程固定 Litz 线规和磁芯材料，搜索磁芯形状、叠片数、电流密度、磁通密度与并联导线数，再以最坏工况计算 core/winding loss 和温升，最后在 cost、efficiency 与 power density 之间选解。作者采用经验温升关系 \(\Delta T=(P_{\mathrm{mag}}/(10A_{\mathrm{mag}}))^{0.833}\)，并明确这是磁件热估算而不是热仿真或实测热阻网络。[pdf:E09]（PDF 物理第 9 页，Fig. 7、Eq. (21)）
7. **为二次侧振铃单独设计 RCD snubber。** 漏感与变压器/整流器寄生电容的谐振会把二极管尖峰推高；作者按最坏条件估算未箝位峰值，选择 \(C_{\mathrm{RCD}}\)、目标 \(V_{\mathrm{cp}}\) 与 \(R_{\mathrm{RCD}}\)，并计算电阻损耗。样机使用机械 relay 作为三个辅助开关，因为配置被假定为充电前决定且运行中不变。[pdf:E10]（PDF 物理第 10 页，Fig. 8、Eq. (22)–(24)、Tables VI–VII）
8. **样机测试。** 论文搭建 11-kW 原型，以 TI TMS320F283790 microcontroller 控制，使用可编程电源、电子负载、功率分析仪和示波器做 set-point open-loop tests；Fig. 9 给出的体积功率密度为 2.3 kW/L。[pdf:E11]（PDF 物理第 11 页，Fig. 9、Table VIII）

从 EMT + FPGA 视角看，论文没有报告用于电磁暂态仿真的离散状态方程、固定步长或多速率推进；没有给出事件队列、开关函数数值实现、定点格式、pipeline/data dependency、FPGA 架构、资源占用、时序或 HIL 实时步长。控制平台是 microcontroller，论文目标是物理变换器设计与样机效率，而不是 FPGA 映射。上述项目均应保持“未报告”，不能从 15-kHz 开关频率外推成仿真步长或硬件吞吐率。

## § 6 — 核心数学推导（无形式化数学则跳过）

数学主线分为“拓扑等效”“电流分段”“器件设计”三层。

第一层是拓扑等效。Table II 把两种连接都化为 Fig. 3 的传统 PSFB，差异只进入 \(n_{\mathrm{eff}}\)、\(L_{\mathrm{out(eff)}}\)、\(C_{\mathrm{out(eff)}}\) 和实际二次侧电流换算。[pdf:E05]（PDF 物理第 5 页，Table II）这一步的工程意义是：后续不用为两个拓扑各推一套模型，只需把同一个 PSFB 模型代入不同的等效参数。串联模式把两路电压相加，因此从主侧看有效变比减半；并联模式把两路电流相加，因此每个二次绕组和整流桥只承担一部分总电流。

第二层是稳态分段电流。作者先定义反射量

\[
V_{\mathrm{in(ref)}}=\frac{V_{\mathrm{in}}}{n_{\mathrm{eff}}},
\qquad
L_{\mathrm{total(ref)}}=\frac{L_\sigma}{n_{\mathrm{eff}}^2}+L_{\mathrm{out(eff)}} .
\]

随后用

\[
I_{s1}=I_{\mathrm{out}}-
\frac{V_{\mathrm{out}}\left(V_{\mathrm{in(ref)}}-V_{\mathrm{out}}\right)}
{4f_{\mathrm{sw}}L_{\mathrm{total(ref)}}V_{\mathrm{in(ref)}}}
\]

判断导通模式：\(I_{s1}\ge 0\) 为 CCM，否则为 DCM。导通段末电流为

\[
I_{s2}=I_{s1}+
\frac{D\left(V_{\mathrm{in(ref)}}-V_{\mathrm{out}}\right)}
{2f_{\mathrm{sw}}L_{\mathrm{total(ref)}}},
\]

CCM 中续流/换流后的电流则由

\[
I_{s3}=I_{s2}-
\frac{(1-D^{\mathrm{CCM}}-C)V_{\mathrm{out}}}
{2f_{\mathrm{sw}}L_{\mathrm{total(ref)}}}
\]

给出。[pdf:E06]（PDF 物理第 6 页，Eq. (1)–(5)）直观上，\(D\) 决定有功加电流的时间，\(C\) 表示漏感换流占去的时间；初始电流是否已经降到零决定要用 CCM 还是 DCM 的面积积分。Eq. (6)–(10) 给出 \(D^{\mathrm{CCM}}\)、\(C\)、\(D^{\mathrm{DCM}}\) 和过零时间的闭式表达，再把分段波形平方积分得到 Table III、Eq. (11)–(16) 的器件 rms/average current。[pdf:E07]（PDF 物理第 7 页，Eq. (6)–(10) 与 Fig. 5）论文的假设是 dead-time transition 只有数十到数百纳秒，相对其他区间很短，因此忽略其对总电流波形的影响；这对平均损耗建模合理，但不能据此证明换态尖峰或 EMI。[pdf:E06]（PDF 物理第 6 页，Section III、Table III 下方正文）

第三层把应力模型转成器件值。变压器变比按

\[
n=\frac{V_{\mathrm{in(min)}}}{V_{\mathrm{re}}}\times 95\%=1.216
\]

选取；电感 ripple 由 \(V_{\mathrm{in,ref}}(1-D)D/(2f_{\mathrm{sw}}L_{\mathrm{out}})\) 决定，考虑并联模式的等效电感减半后得到 \(L_{\mathrm{out(min)}}=1.3\ \mathrm{mH}\)；最低输出电容为 \(3.75\ \mu\mathrm{F}\)，样机实际采用 130-\(\mu\mathrm{F}\)、500-V 电容以稳定测试电压。[pdf:E08]（PDF 物理第 8 页，Eq. (17)–(20)）这些数值是该 11-kW 设计的具名参数，不应外推为 r-PSFB 的普适最优值。

二次侧 snubber 的起点是未箝位尖峰估算：

\[
V_{\mathrm{ringing}}=2\frac{V_{\mathrm{in,max}}}{n}
=2\frac{840}{1.2}=1400\ \mathrm{V},
\]

超过所选 1200-V 二极管。作者取 \(C_{\mathrm{RCD}}=200\ \mathrm{nF}\)、\(V_{\mathrm{cp}}=1000\ \mathrm{V}\)、估计 \(C_{\mathrm{sec}}\approx400\ \mathrm{pF}\)，由 Eq. (23) 选择 62-k\(\Omega\) 电阻，并用 \(P_{\mathrm{RCD}}=(V_{\mathrm{cp}}-V_{\mathrm{out,max}})^2/R_{\mathrm{RCD}}\) 计算耗散。[pdf:E10]（PDF 物理第 10 页，Eq. (22)–(24)）其 intuition 是允许寄生谐振先把能量送入箝位电容，再由电阻耗散，从而以可计算的损耗换取二极管耐压裕量。

论文还定义了 charging-cycle efficiency，但 PDF 中印刷的 Eq. (25) 是

\[
\eta_{\mathrm{cycle}}=\int_0^{T_c}\eta(t)\,dt .
\]

[pdf:E12]（PDF 物理第 12 页，Eq. (25)）按量纲分析，这个表达式带有时间量纲，不能直接对应 Table IX 的百分比；若意图是时间平均，应除以 \(T_c\)，若意图是能量效率，则应以输入/输出能量积分定义。这里很可能存在公式排版遗漏，但 PDF 未给出勘误，复现者必须查参考文献 [46] 或原始计算代码，不能直接照抄 Eq. (25)。

## § 7 — 实验设计与结论

**问题 1：解析应力模型是否能描述 r-PSFB？** 作者在 \(V_{\mathrm{in}}=640\ \mathrm{V}\)、\(I_{\mathrm{out}}=10\ \mathrm{A}\)、\(L_\sigma=10\ \mu\mathrm{H}\) 的条件下，把传统 PSFB 与 r-PSFB 的解析曲线和 LTspice 点进行比较。Fig. 5 显示趋势和采样点相符，支持模型用于器件选型；但没有给出最大误差、跨参数网格统计或实验电流应力的同类误差指标，所以证据是 simulation correspondence，不是模型精度认证。[pdf:E07]（PDF 物理第 7 页，Fig. 5）

**问题 2：串并联是否实现预期的均流、分压和箝位？** 在并联模式的多个 250/320/500-V、5/22/30-A set point 上，两路二次侧电流能分担负载；满电流时由于绕组、二极管、电感和 relay 接触阻抗不一致，论文观察到小于 2 A、约占最大输出电流 6.7% 的不平衡。在串联模式中，两路输出电压差小于 50 V。[pdf:E11]（PDF 物理第 11 页，Figs. 10–11 及相邻正文）RCD 测试则在 \(V_{\mathrm{in}}=840\ \mathrm{V}\) 的串联、并联两种模式下把二极管电压箝位到约 1000 V，支持 1200-V 二极管的样机级安全裕量。[pdf:E12]（PDF 物理第 12 页，Fig. 12）

**问题 3：重构是否在宽电压区提高效率？** Fig. 13 把解析损耗模型得到的曲线与样机测试点叠加。IGBT 版本在 1000 V/10 A 的串联模式达到 97.6% 峰值，在 490 V/20 A 的并联模式测得 97.4%；SiC 版本对应为 98.3% 和 98.2%。500 V 附近换成 current doubler 后，效率曲线出现“重置”，低压区明显高于同规格传统 PSFB 的估算曲线。[pdf:E11]（PDF 物理第 11 页，Fig. 13 前导正文）[pdf:E12]（PDF 物理第 12 页，Fig. 13）这支持“重构减小低压区应力”的核心机制，但传统 PSFB 对照在 Fig. 13 中是 estimated，而非同台实测曲线。

**问题 4：一次完整充电是否受益？** 作者用 LNCO Boston Power SWING 5300 的 impedance-based battery model 生成 400-V/50.35-kWh 与 800-V/79.2-kWh CCCV 充电轨迹，再把估算效率映射到轨迹上。Table IX 给出：传统 PSFB IGBT 对两种电池的估算 cycle efficiency 分别为 92.2% 和 96.0%；r-PSFB IGBT 均为 96.4%，r-PSFB SiC 均为 97.8%。[pdf:E12]（PDF 物理第 12 页，Table IX、Eq. (25)）这些是 charging-profile simulation 加效率模型的结果，不是把真实电池从低 SOC 充到高 SOC 的量热或电能积分实测。

**问题 5：相对文献样机是否有竞争力？** Table X 把本样机与既有 PSFB-type EV charger prototypes 比较；作者报告其覆盖 250–1000 V、11 kW、30 A、15 kHz、2.3 kW/L，IGBT 与 SiC 的峰值效率分别为 97.6% 和 98.3%，并把输出电压跨度视为主要优势。[pdf:E13]（PDF 物理第 13 页，Table X、Fig. 14）结论据此声称 11-kW 样机的估算与测试相符，证明该方案用于 EV charging 的 feasibility。[pdf:E14]（PDF 物理第 14 页，Conclusion）

不得外推的范围包括：论文没有测试带载 series/parallel transition，没有闭环充电控制动态，没有真实整车/BMS 通信，没有完整充电周期实测，没有 EMI、故障穿越、relay 寿命、绝缘协调或长期热循环，也没有 FPGA/HIL 实现。样机证据证明的是固定配置下若干 set point 的稳态波形、箝位和效率。

文本一致性还有三处需要复现者主动处理。其一，Section II-B 先正确写成“低电压并联、高电压串联”，随后一句却反写成“400-V 串联、800-V 并联”；Section IV/V、Table II 和实验图均支持前者，因此后一句应视为原文内部矛盾，而不是控制规则。[pdf:E04]（PDF 物理第 4 页，Section II-B）其二，Eq. (25) 缺少把积分变成无量纲效率所需的归一化。[pdf:E12]（PDF 物理第 12 页，Eq. (25)）其三，作者在解释 cycle efficiency 比 peak efficiency 更有代表性时写成“\(\eta_{\mathrm{peak}}\) is the best metric”，但前后逻辑和下一句实际支持“不是最佳指标”；这也只能标为基于上下文的疑似文字遗漏，不能静默改写原文。[pdf:E13]（PDF 物理第 13 页，Table X 上方正文）

## § 8 — Take-aways

**5 句话：**  
1. r-PSFB 用二次侧串联覆盖高压区、并联覆盖低压大电流区，从等效变比而不是单纯器件升级入手解决宽范围效率问题。[pdf:E04]  
2. 两种配置都能映射为同一传统 PSFB，并通过 \(n_{\mathrm{eff}}\)、\(L_{\mathrm{out(eff)}}\) 和 \(C_{\mathrm{out(eff)}}\) 的变化计算电流应力。[pdf:E05]  
3. 11-kW 样机在固定配置 set point 上证明了均流、分压、1000-V 箝位和最高 98.3% 的 SiC 效率。[pdf:E11][pdf:E12]  
4. 低压端的收益来自 500 V 处重置 phase shift 并降低半导体电流应力，而不是依赖运行中快速切换拓扑。[pdf:E12]  
5. 完整充电周期收益仍主要来自 battery-profile simulation 与损耗模型，动态重构、闭环充电和真实周期能量效率尚未报告。[pdf:E12][pdf:E13]

**3 句话：**  
1. 论文把一个四倍输出电压范围拆成两个更温和的 PSFB 工作区，并用 relay 在会话前选择。  
2. 解析设计、snubber 和 11-kW 样机共同支持固定模式下的工程可行性与高峰值效率。[pdf:E10][pdf:E14]  
3. 最关键的剩余问题是：当实际电池电压区间重叠或跨越阈值时，静态选模假设是否仍成立。

**1 句话：**  
r-PSFB 的真正贡献是用静态拓扑重构换取宽范围稳态效率，但它尚未证明自己是能安全处理任意充电轨迹与模式边界的完整通用充电器。

## § 9 — 最脆弱的假设

最脆弱的假设是：400-V 与 800-V 电池的实际充电电压区间可以由 500 V 清楚分开，而且一辆车的一次充电全过程不会跨越这个边界，因此三个辅助 relay 只需在能量传输前动作一次。论文直接用这个假设消除了带载重构控制，并以此论证机械开关足够且导通损耗更低。[pdf:E04]（PDF 物理第 4 页，Section II-B）后续设计把 200–500 V 归为 400-V architecture、500–1000 V 归为 800-V+ architecture，并固定低压并联、高压串联。[pdf:E08]（PDF 物理第 8 页，Section V-A）

如果现实中的 pack voltage、BMS 目标、母线扰动或未来车型使两个区间重叠，或一条充电轨迹跨过 500 V，那么静态配置会出现两难：保持并联可能达不到更高电压，保持串联则在低压端失去所声称的低 phase-shift 优势；若改成带载换态，又必须面对 relay 开断电弧、输出中断、磁化/漏感能量释放和二极管过压，而这些都不在论文模型和实验范围内。论文给出的证据是基于所选电压区间的 set-point 测试，没有展示 BMS 数据集对“不重叠”假设的覆盖，也没有 boundary-crossing charging profile 或换态波形。因此，这个假设一旦失效，核心贡献不是稍微降效，而是从“无需动态重构的通用宽范围充电器”退化为“只适用于可预先分类电池的两模式硬件”。

## § 10 — 最小复现实验

一周内最有价值的最小复现不是重做完整 11-kW 样机，而是验证“重构是否真的在同一硬件上重置 phase shift 与 rms current”。可以搭建一个约 1:10 电压比例、数百瓦级的隔离 PSFB：输入 64–84 V，双相同二次绕组，三只低压 relay 或受控开关实现串并联，输出用电子负载扫 25–100 V；同时保留一个不重构、器件和磁件尽量一致的固定连接 baseline。比例缩放只是降低实验危险，不改变论文 Table II 的等效关系。[pdf:E05]（PDF 物理第 5 页，Table II）

实验只测四项：达到每个输出点所需的 phase shift、主侧 rms current、两路二次侧电流/电压不平衡、输入输出功率效率。先在 25–50 V 并联扫点，再在 50–100 V 串联扫点，并在 50 V 两侧各取多个重复点；传统 baseline 用同样输入、功率和温度条件。若重构在边界后显著减小 phase shift 与主侧 rms current，且扣除 relay 与额外磁件损耗后效率仍高于 baseline，就支持核心 claim；若电流不平衡、relay 损耗或 snubber 损耗吃掉理论收益，或增益只存在于模型而不出现在实测，则反驳它。这个实验不声称复现绝对 98.3%，而是隔离检验重构机制本身。

## § 11 — 最强反例设计

最强反例是一条必须跨越重构阈值的连续充电轨迹。用可编程电池模拟器或双向电源构造 450–550 V 的目标电压上升过程，保持功率和电流变化符合充电器能力；先要求系统按论文规则在会话开始前固定为并联，再观察接近 500 V 后能否继续跟踪。它很可能在电压能力上失效。随后允许系统尝试从并联切到串联，但不预设安全换态方案，记录输出中断时间、主侧电流、relay 端电压、二极管尖峰、两路电容电压和负载功率。

如果固定模式无法完成轨迹，而动态换态又产生超出器件裕量的尖峰、明显能量中断或不可接受的充电扰动，那么论文的“宽范围且无需运行中重构”只对预先可分离的 pack classes 成立。这个反例比单纯改变温度或器件参数更强，因为它直接攻击作者把动态 hybrid problem 化为静态选择的前提；它也能排除“效率提高只是理想分类条件下的工作点重排”这一替代解释。

## § 12 — Follow-up Research Idea

**候选想法：面向任意 pack envelope 的可认证 hybrid-state charger。** 这里不把研究目标定义为“在现有 r-PSFB 上加一个更快开关”，而是把问题改成：对可能重叠、跨界或由 BMS 动态改变的电压轨迹，怎样联合选择电气拓扑状态、phase shift 和安全换态路径，并给出全充电过程的可达性与器件应力保证。由于本次严格只使用源 PDF，尚未做外部相关工作检索，以下不声称 novelty。

（a）未满足的需求是静态 500-V 分类不能覆盖未来 pack 架构、低 SOC 极端和边界附近的动态请求；用户真正需要的是不依赖车型标签的连续充电能力。  
（b）电力电子领域会重视这项工作的原因，不是控制算法更复杂，而是它把器件安全、充电连续性和 cycle efficiency 统一成可实测、可认证的系统指标，并要求在真实功率样机上通过 boundary-crossing profile。  
（c）可借鉴 hybrid systems 的 guard/invariant、reachability analysis 和 bumpless transfer：拓扑状态是离散变量，电感电流、电容电压和热状态是连续变量，只有在零电流或受控能量转移集合内才允许换态。  
（d）第一个证伪实验就是 §11 的 450–550 V 轨迹。若控制器不能在限定输出中断、二极管尖峰和 rms current 内完成跨界，或者其全周期效率不优于固定 PSFB，想法立即失败。  
（e）与本文的实质区别是：本文依靠“不跨界”假设消除动态重构；候选工作把跨界本身变成研究对象，并要求安全性证明与全轨迹实测，而不只是在两个静态模式中分别获得高效率。
