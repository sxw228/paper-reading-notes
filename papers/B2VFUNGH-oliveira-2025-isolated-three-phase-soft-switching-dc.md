# Isolated Three-Phase Soft-Switching DC-DC Converter With Reduced Voltage Stress on Rectifier Diodes for Off-Board Chargers

**作者**：Raimundo Nonato Moura de Oliveira；José Willamy Medeiros de Araújo；Luiz Henrique Silva Colado Barreto；Dalton de Araujo Honorio；Demercil de Souza Oliveira, Jr.  
**出处**：IEEE Transactions on Power Electronics，Vol. 40，No. 7，pp. 9407–9417  
**年份**：2025  
**DOI**：10.1109/TPEL.2025.3544514  
**Zotero key**：B2VFUNGH  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。  
**实现范围**：FPGA 未报告；HIL 未报告；实时仿真未报告；EMT 离散化、时间步长与网络求解细节未报告。论文的验证链是解析建模、开关级仿真与 10 kW 实验样机。

## § 1 — 研究问题与重要性

这篇论文要解决的是一个具体的功率变换问题：怎样让面向 level 2/level 3 电动汽车非车载充电器的隔离 dc–dc 级，在固定频率 PWM 下覆盖约 200–920 V 的电池电压范围，同时降低高频整流二极管的反向电压应力，并在较宽负载范围内保留 soft switching。作者把目标落在一台 10 kW 样机上，而不是只给出拓扑概念或低功率演示；摘要报告额定输出范围 200–920 V、峰值效率超过 98%。这是论文原文的目标与结果陈述，不等于已经独立证明其全球 novelty。[pdf:E01]（PDF 物理页 1，标题、Abstract 与 Introduction）

问题之所以重要，是因为充电器要适配不同车型时，电池包电压可能从 200 V 跨到 920 V。DAB、LLC 和传统 PWM 各有代价：DAB 在偏离最优电压点时 soft-switching 与效率范围受限；LLC 的宽增益通常依赖较宽的变频范围和更复杂的谐振腔、控制设计；传统 PWM 虽然控制直观，但变压器漏感会造成有效占空比损失，输出 LC 结构又不能天然保证整流二极管钳位。若能把二极管峰值反压限制在 1.2 kV 器件可承受的范围，就可能避免二极管串联或更高 PIV 器件带来的成本和性能代价。

## § 2 — 前人工作与不足

论文把先前路线分成三类。第一类是 DAB：优势是双向功率流，问题是宽电压比下 circulating current、soft-switching 边界和效率都会恶化。第二类是 LLC/CLLC：它们可获得 soft switching，但为覆盖宽电压范围，往往需要宽频率调节、复杂 resonant tank 设计，或增加 mode/reconfiguration。第三类是固定频率 PWM：结构与控制相对直接，但 leakage-inductance 引起的占空比损失和整流侧过压需要额外处理。[pdf:E01]（PDF 物理页 1，Introduction 右栏）

作者点名的紧密先例包括：一台最高约 700 V、3.5 kW 的三电平 CLLC；一台通过 voltage-doubler/current-doubler 重构实现 150–1000 V 的 11 kW 两级谐振变换器；一类以 buck 级换取宽输出范围、但 buck hard switching 限制频率的两级三电平方案；以及使用 snubber 或整流侧重构来约束二极管应力的 PWM/谐振方案。论文认为这些路线的问题不是简单“没考虑宽范围”，而是为了宽范围引入了继电器、接触器、多工作模式、变频、额外开关或全功率 buck 级，进而带来不连续切换、控制复杂度或低压/重载效率下降。作为作者自己的比较框架，这些论点可以解释设计动机；但本文没有对每篇先例做统一器件、磁件和热设计下的重新实验，因此不能把表格中的峰值效率直接当作公平 head-to-head 结论。[pdf:E02]（PDF 物理页 2，Introduction 与 Fig. 1–2）

## § 3 — 重建作者的思考路径

下面是基于论文背景与先例的重建，不是作者逐字陈述。一个可能的推理起点是先固定工程约束：隔离、10 kW 级、200–920 V、固定 switching frequency、无继电器重构，并且整流二极管不能承受传统 PWM 在漏感与 parasitic resonance 下产生的过高反压。若沿用单相全桥或单个三相桥，扩大 gain range 往往会把问题转移到极小占空比、过大的滤波器或二极管钳位网络。

下一步可以从既有 three-phase ZVS PWM converter 与 three-phase hybridge rectifier 出发：三相错相天然把功率与纹波分散到多个相，hybridge/current-multiplier 整流结构又有较低二极管电压应力的历史线索。于是把两个三相逆变桥接到六个单相高频变压器，用互补的 \(D\) 与 \(1-D\) 调制，让两个桥在不同占空比区域接力供能；再利用三相对称性，把一个 switching period 中的 18 个阶段压缩成每区三个代表阶段分析。这里真正被“再利用”的并不只是拓扑，而是 leakage inductance：它一方面造成 duty-cycle loss，另一方面又为开关结电容的充放电提供 ZVS 所需能量。[pdf:E03]（PDF 物理页 3，Fig. 3–4 与 Region 01 分析）

## § 4 — 核心 Intuition

核心直觉是：用两个相同载波、相差互补占空比的三相桥，把宽输出电压调节拆成三个连续占空比区域；再由六变压器加三相 current-multiplier rectifier 把能量汇总，使二极管反压不必随输出电压一比一抬升。三相错相降低合成输出纹波，而漏感既解释增益损失，也在合适负载与 dead time 下帮助实现 ZVS。代价是器件和磁件数量显著增加，且“全范围都 soft switching”并不成立。

## § 5 — 具体方法与完整 Pipeline

以实验样机的 \(V_{\mathrm{in}}=600\ \mathrm{V}\) dc bus 为例，完整能量路径如下。

1. **生成门极信号。** Bridge 01 的上桥臂使用占空比 \(D\)，下桥臂使用互补信号；Bridge 02 的上桥臂使用 \(1-D\)，下桥臂同样互补。每个桥的三相载波彼此错开 \(120^\circ\)，两个桥共用同一组载波基准。[pdf:E02]（PDF 物理页 2，Fig. 2 与其下方 PWM 描述）
2. **高频逆变与隔离。** 两个三相桥共含 12 个主动开关，分别驱动六个单相高频变压器 \(T_{a1},T_{b1},T_{c1},T_{a2},T_{b2},T_{c2}\)。变压器完成 galvanic isolation 与变比匹配；论文把六个漏感折算到原边并在理论中统一记为 \(L_d\)。
3. **整流与电流合成。** 六个次级绕组接到由 \(D_1\)–\(D_6\) 组成的 current-multiplier rectifier。三个滤波电感 \(L_1,L_2,L_3\) 的电流在输出端相加，再由 \(C_o\) 平滑为负载电压 \(V_o\)。拓扑图同时显示了两个三相桥、六变压器、六二极管和三路输出电感的真实连接。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II-A）
4. **按占空比进入工作区。** 忽略漏感导致的边界偏移时，Region 01 对应 \(D\le 0.33\)，Region 02 对应 \(0.33\le D\le0.66\)，Region 03 对应 \(0.66\le D\le1\)。每区在一个周期有 18 个阶段，但波形对称性允许作者只分析三个代表阶段；Region 01 的代表阶段依次是 linear-current transition、energy transfer 和 freewheeling。[pdf:E03]（PDF 物理页 3，Fig. 3–4 与正文）
5. **在 Region 02/03 改变参与传能的相。** Region 02 中会出现两只上桥臂开关重叠，部分阶段由三只输出电感同时接收能量，另一些阶段只由部分电感续流；Region 03 则出现三只上桥臂重叠。各阶段持续时间显式含 \(D,T_s,L_d,I_o,V_{\mathrm{in}}\)，因此漏感与负载电流直接改变有效占空比。[pdf:E04]（PDF 物理页 4，Fig. 5 与 Eq. (2)–(8)）
6. **得到输出并闭环调节。** 三路电感电流的合成纹波进入 \(C_o\)，控制器以 \(V_o\) 为反馈变量调 \(D\)。理论 gain 在前两个区域随 \(D\) 上升、在第三个区域随 \(D\) 下降；作者后续用小信号模型设计单一 PI/PID 型控制器覆盖前两个区域。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的分段解析模型。第一步是在一个含 18 个阶段的 switching period 内，对每个输出电感施加 volt-second balance。令 \(G=V_o/V_{\mathrm{in}}\)、\(T_s=1/f_s\)，并把六个漏感等效为 \(L_d\)，得到

\[
G=
\begin{cases}
2D-\dfrac{2I_oL_d}{T_sV_{\mathrm{in}}}, &
\dfrac{1}{6}-\dfrac{2I_oL_d}{T_sV_{\mathrm{in}}}<D\le\dfrac{1}{3},\\[6pt]
2D-\dfrac{6I_oL_d}{T_sV_{\mathrm{in}}}, &
\dfrac{1}{3}+\dfrac{2}{3}\dfrac{2I_oL_d}{T_sV_{\mathrm{in}}}<D\le\dfrac{2}{3},\\[6pt]
4-4D-\dfrac{6I_oL_d}{T_sV_{\mathrm{in}}}, &
\dfrac{2}{3}<D\le1-\dfrac{2I_oL_d}{T_sV_{\mathrm{in}}}.
\end{cases}
\]

这就是 Eq. (10)。直观上，理想 gain 的斜率在 Region 01/02 为 \(+2\)，Region 03 变为 \(-4\)；所有区域都减去与 \(I_oL_d/(T_sV_{\mathrm{in}})\) 成正比的 leakage duty loss。因此负载越重或漏感越大，可用占空比区间越被压缩。Fig. 7 还显示 Region 01 与 02 之间存在一个近似恒 gain 的过渡子区。[pdf:E05]（PDF 物理页 5，Fig. 7–8 与 Eq. (9)–(10)）

作者用 Table II 的样机参数把解析式与开关仿真比较。Fig. 9 显示 normalized gain、单个滤波电感纹波与合成输出纹波的理论曲线和仿真点基本重合；Table II 同时给出 \(f_s=50\ \mathrm{kHz}\)、\(t_d=70\ \mathrm{ns}\)、\(L_d=5\ \mu\mathrm{H}\)、\(L_1=L_2=L_3=1\ \mathrm{mH}\)、\(V_{\mathrm{in}}=600\ \mathrm{V}\)、\(P_o=10\ \mathrm{kW}\) 等设计点。[pdf:E06]（PDF 物理页 6，Table II 与 Fig. 9）

第二步是平均小信号建模。对 Region 01，作者用 \(i_L\) 与 \(v_c\) 为状态，定义 \(R_d=2f_sL_d\) 表示漏感造成的 duty loss，并在线性化工作点附近得到

\[
G_{v/d}(s)=2V_{\mathrm{in}}
\frac{r_{se}C_os+1}{a_2s^2+a_1s+a_0},
\]

\[
a_2=LC_o\left(1+\frac{r_{se}}{R_o}\right),\qquad
a_1=\left[r_{se}+R_d\left(1+\frac{r_{se}}{R_o}\right)\right]C_o+\frac{L}{R_o},\qquad
a_0=\frac{R_d}{R_o}+1.
\]

Region 02 的状态矩阵形式不变，但与 duty loss 相关的 \(R_d\) 项增为三倍；Region 03 的输入矩阵改为含 \((4-4D)/L\) 的形式。Fig. 11–12 表明前两区的 Bode 曲线只在约 1 kHz 附近有较小差异，解析模型与 ac-sweep 仿真吻合。[pdf:E07]（PDF 物理页 7，Fig. 10–12 与 Eq. (12)–(18)）这套推导是分段稳态平均与工作点线性化，不是全局稳定性定理；论文也没有给出参数不确定性下的误差界。

## § 7 — 实验设计与结论

**问题 1：宽输出范围下，二极管应力是否真的被压低？** 作者搭建 10 kW 实验样机，Table II 的主设计点是 600 V 输入、920 V 额定输出、50 kHz、70 ns dead time、5 \(\mu\mathrm{H}\) 等效漏感和 1 mH 三路滤波电感。样机照片显示两个 inverter bridge、六只高频变压器、rectifier diodes 与三路 filter inductors 是独立硬件模块。[pdf:E08]（PDF 物理页 8，Fig. 13 与 Section IV 开头）在 \(D=0.25,0.50,0.658\) 三个点，Fig. 14 的二极管反压平台约 720 V，作者报告由 reverse recovery 与寄生谐振引起的尖峰不超过 1.2 kV，因此可以使用 1.2 kV SiC 二极管；同一组波形显示电感纹波在 \(D=0.25\) 最大、\(D=0.50\) 最小。[pdf:E09]（PDF 物理页 9，Fig. 14 及相邻正文）

**问题 2：soft switching 是否覆盖轻载？** Fig. 15 比较 \(I_o=11.3\ \mathrm{A}\) 与 \(3.8\ \mathrm{A}\) 的开关波形。\(3.8\ \mathrm{A}\) 对应 normalized output current 0.27、dead time 70 ns，此时作者明确指出只有 \(S_{51}\) 实现 ZVS；因此实验支持的是“存在负载相关的 ZVS 区域”，不是“所有开关、所有负载都 ZVS”。[pdf:E09]（PDF 物理页 9，Fig. 15 与其上下文）

**问题 3：宽电压范围下效率如何？** Fig. 16 给出四个输出电压的效率曲线：920 V 的最大效率为 98.13%，800 V 为 98.01%，400 V 为 97.17%，200 V 为 95.04%。这验证了固定频率 PWM 在离散电压点的可行性，也同时说明低压端并非“无明显效率下降”：从 920 V 到 200 V，峰值效率下降约 3.09 个百分点。[pdf:E09]（PDF 物理页 9，Fig. 16 与正文）

**问题 4：闭环能否应对负载变化？** 作者基于 Eq. (15) 用 pole placement 设计控制器，包含 integrator、位于半个 switching frequency 的 pole 和靠近 1 kHz resonance 的 zero。Fig. 19 在 \(V_o=500\ \mathrm{V}\) 下施加 1.8 kW 到 4.6 kW 的 load step，输出电压回到 500 V 附近；论文只定性称 settling time 可接受，没有报告精确 settling time、overshoot 指标或多电压点动态测试。[pdf:E10]（PDF 物理页 10，Fig. 19 与 Section IV 末段）

**问题 5：主要损耗来自哪里，synchronous rectification 能否改善？** Fig. 18 的解析 loss breakdown 把 transformer、diode、snubber、MOSFET switching、inductor 和 MOSFET conduction loss 分别估为 32%、25%、20%、11%、7% 和 5%。但这个分解假设全部 semiconductor 都实现 ZVS，并忽略 power diode reverse-recovery loss；它是模型估算，不是逐项量热实测。把二极管替换为 G3R12MT12KA 做 synchronous rectification 的 98.82% 也是解析预测，论文报告其相对原设计提高约 0.45 个百分点，并未给出对应硬件效率曲线。[pdf:E10]（PDF 物理页 10，Fig. 18 与上方延续正文）

实验没有报告 FPGA 实现、HIL 平台、实时仿真器、固定 EMT 步长、WCET、资源占用、定点格式或网络节点规模；不能把这篇论文当成 EMT+FPGA 加速证据。

## § 8 — Take-aways

**用 5 句话总结：**

1. 作者提出一种双三相桥、六高频变压器和三相 current-multiplier rectifier 组成的隔离 PWM dc–dc 变换器。
2. \(D\) 与 \(1-D\) 的互补三相调制把调压过程分成三个连续工作区，并在固定 switching frequency 下覆盖宽输出范围。
3. 10 kW 样机在三个代表占空比点把二极管反压尖峰保持在 1.2 kV 以下，支持使用 1.2 kV SiC 二极管。
4. 峰值效率在 920 V 为 98.13%，但在 200 V 降到 95.04%，因此“宽范围高效”要带着明显的低压端代价来理解。
5. soft switching 依赖负载与 dead time，轻载实验中并非所有开关都实现 ZVS。

**用 3 句话总结：**

1. 这项工作的主要价值是把宽电压、固定频率、低二极管应力和 10 kW 硬件验证放进同一拓扑。
2. 解析 gain、小信号模型、仿真和样机波形基本互相对应，但全范围器件应力、动态性能与 loss breakdown 的证据强度并不相同。
3. 最需要继续验证的是寄生参数、器差、温度和负载瞬变共同作用时，1.2 kV 二极管安全裕度是否仍然成立。

**用 1 句话总结：**

这是一种以更多开关和磁件换取固定频率宽增益与较低整流二极管应力的 10 kW 三相隔离 dc–dc 方案，其 nominal 性能有力，但 worst-case 保证尚未建立。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在 200–920 V 全工作范围、器件与寄生参数偏差、温度和负载瞬变共同存在时，整流二极管峰值反压仍有足够裕度低于 1.2 kV。** 这条假设一旦失效，标题中的“reduced voltage stress”就不能再支撑选用 1.2 kV 二极管，核心成本与性能优势会直接消失。

论文给出的直接证据是 \(D=0.25,0.50,0.658\) 三个稳态波形点，平台约 720 V、观察到的尖峰不超过 1.2 kV；没有报告对 \(L_d\)、reverse-recovery、结电容、变压器 stray capacitance、布线电感、温度和测量带宽的 corner sweep，也没有在 Region 01/02、02/03 边界附近做全负载动态扫描。更重要的是，Fig. 18 的损耗分解假设所有开关均 ZVS且忽略二极管 reverse recovery，而 Fig. 15 在 normalized current 0.27 时明确只观察到 \(S_{51}\) ZVS，这说明模型的 nominal 假设不能直接外推到轻载 worst case。[pdf:E09]（PDF 物理页 9，Fig. 14–16）[pdf:E10]（PDF 物理页 10，Fig. 18 及其假设）

复现还有一个内部口径风险：Table I 把 proposed topology 的 frequency 列为 40 kHz，而 Table II 的实验 switching frequency 是 50 kHz。论文没有解释这是比较表采用另一设计点还是排版错误；若磁件、漏感、ZVS 区域与损耗按不同频率计算，读者不能把两列参数无条件拼成同一个样机条件。[pdf:E06]（PDF 物理页 6，Table I–II）

## § 10 — 最小复现实验

一周内最有价值的最小复现不是重建完整 10 kW 样机，而是做一个**含非理想寄生参数的开关级 stress-envelope 复现**。

1. **数据与模型。** 使用论文的 \(V_{\mathrm{in}}=600\ \mathrm{V}\)、\(f_s=50\ \mathrm{kHz}\)、\(t_d=70\ \mathrm{ns}\)、\(L_d=5\ \mu\mathrm{H}\)、三只 1 mH 滤波电感及 10 kW 额定条件；实现 Fig. 1 的两个三相桥、六变压器、六二极管与 \(D/(1-D)\) 调制。把 MOSFET \(C_{\mathrm{oss}}\)、二极管 reverse-recovery、变压器 stray capacitance 和布线电感显式加入模型。
2. **扫描。** 先复现 \(D=0.25,0.50,0.658\)，再对 \(D\in[0.1,0.95]\)、轻载到额定负载、\(L_d\) 与寄生参数的合理容差做 sweep，尤其加密 \(D\approx1/3\) 与 \(2/3\) 的区域边界。
3. **测量。** 记录六只二极管各自的 plateau voltage 与 peak reverse voltage、三路电感纹波、每只主开关 turn-on 前的 \(v_{DS}\)，并标记 ZVS 成立范围。不要从图上估读不存在的精确效率数据。
4. **支持标准。** nominal 三点应重现约 720 V 平台、\(D=0.25\) 最大纹波与 \(D=0.50\) 最小纹波；在预先声明的寄生容差范围内，所有二极管峰值仍应低于 1.2 kV，并保留明确工程裕度。
5. **反驳标准。** 只要一个合理 corner 在稳态或负载阶跃中超过 1.2 kV，或 ZVS 范围显著窄于 Fig. 10/15，论文最重要的器件选型外推就被反驳。若条件允许，再以一相缩比 double-pulse fixture 实测最危险 corner，专门校准仿真中的 reverse-recovery 与 stray-inductance 参数。

## § 11 — 最强反例设计

最强反例是构造一个**二极管过压由寄生谐振主导、而不是由理想拓扑决定**的受控实验。使用与论文相同的输入、器件电压等级和调制，在三组可交换变压器/母排中有意形成低、中、高三档漏感与 stray inductance；在冷态和高结温下，从轻载向重载及重载向轻载双向阶跃，并扫过 \(D=1/3\) 与 \(2/3\) 两侧。用足够带宽、低环路电感的差分探头同时捕获六只二极管的 reverse voltage 和两只代表开关的 \(v_{DS}/i_D\)，而不是只测一只器件或只展示稳定波形窗口。

这个反例的替代解释是：论文观察到的约 720 V 平台可能确实由拓扑设定，但“尖峰不超过 1.2 kV”可能只是当前样机寄生网络、探测点和三个占空比的结果。若高寄生、高温或跨区瞬变让任一二极管超过 1.2 kV，或必须增加显著 snubber 才能保持安全，那么 reduced plateau stress 仍可能成立，却不足以推出“可可靠使用 1.2 kV 二极管”的工程结论。相反，若所有预注册 corner 都保有一致裕度，且相同条件下的 phase-shift full bridge 即使优化 snubber 仍有更高峰值，这会显著加强作者的核心主张。

## § 12 — Follow-up Research Idea

电力电子领域通常把高影响工作建立在四件事的组合上：清楚的新问题或新拓扑、可核验的解析机制、足够功率等级的硬件、以及覆盖器件应力、效率、动态和 thermal/corner 条件的工程证据。只在 nominal 点提高零点几个百分点，通常不如建立一个可迁移、可设计、可验证的安全边界有价值。

**候选想法：把“低二极管应力拓扑”改写为“带可认证器件应力包络的宽压充电器”。** 这不是再增加一个 clamp，而是改变设计目标：联合选择拓扑参数、\(D\)、dead time 与允许功率，使整流二极管峰值、ZVS 条件和结温在制造公差与运行不确定性下都有显式保证。

- **(a) 未满足需求。** 当前论文证明了若干 nominal 点，却没有告诉工程师“在什么寄生、温度、老化和负载变化集合内，1.2 kV 器件一定安全”。
- **(b) 研究价值。** 若能把解析 gain、混杂开关状态和实验标定组成一个可审计 stress envelope，成果可以直接服务器件降额设计、磁件公差分配和充电模块认证，价值高于单点效率优化。
- **(c) 相邻方法。** 可借鉴 robust control、interval analysis、hybrid-system reachability 与 reliability engineering；用少量硬件辨识更新寄生参数集合，再由在线调制器只在已认证的 \(D\)-load-dead-time 安全集内运行。
- **(d) 第一个证伪实验。** 预先给出参数区间和“所有二极管 \(v_R<1.2\ \mathrm{kV}\)”的预测，然后在可交换漏感、布线电感和温度的样机上主动寻找越界；任何落在声明区间内的越界都直接证伪模型。
- **(e) 实质区别。** 本文回答“某一拓扑在样机若干点是否表现良好”；候选工作回答“怎样计算并实验认证一整个器件安全运行集合”。由于本卡只使用该 PDF 及其参考文献线索，没有完成外部全文 novelty 检索，因此这个方向只能称为候选研究想法，不能声称尚无人做过。
