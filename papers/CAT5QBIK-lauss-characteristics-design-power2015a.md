# Characteristics and Design of Power Hardware-in-the-Loop Simulations for Electrical Power Systems

**作者**：Georg F. Lauss；M. Omar Faruque；Karl Schoder；Christian Dufour；Alexander Viehweider；James Langston [pdf:E01]

**出处**：IEEE Transactions on Industrial Electronics，Vol. 63，No. 1，pp. 406–417 [pdf:E01]

**年份**：2016 [pdf:E01]

**DOI**：10.1109/TIE.2015.2464308

**Zotero key**：CAT5QBIK

**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是某一个 interface algorithm（接口算法）的局部改进，而是一个系统设计问题：怎样把 digital real-time simulator（DRTS，数字实时仿真器）、power amplifier（PA，功率放大器）、power interface（PI，功率接口）、interface algorithm（IA，接口算法）、真实 hardware under test（HUT，被测硬件）以及采样与保护链路组合成一个可信、稳定、具有足够带宽且不会损坏设备的 power hardware-in-the-loop（PHIL，功率硬件在环）实验系统。论文在 PDF 物理页 1 的摘要中把目标明确限定为总结 PHIL 的实施要求、关键组成、稳定性与复杂性，并形成当时的 state-of-the-art（技术现状）综述，而不是宣称提出一个统一的新算法 [pdf:E01]。

PHIL 的基本价值是让“软件中的其余电力系统”与“实验室里的真实功率设备”在闭环中交换真实电压、电流和功率。Fig. 1 给出的 voltage-type（电压型）例子是：DRTS 计算出的参考电压经 PI 施加到真实负载，负载电流被测量并反馈到仿真模型；因此真实设备的非理想性、控制器、保护、饱和和动态响应会进入系统级实验，而不必先把它们全部准确建模 [pdf:E02]（PDF 物理页 1，Fig. 1 与 Introduction）。

这个问题重要，是因为纯软件仿真成本低、可重复，但当 HUT 模型不存在或模型本身正是实验要识别的对象时，纯软件结果缺少关键物理反馈；反过来，建设完整电力系统做全尺寸实验可能成本过高、不可行，或者在系统投运后再做影响测试已经不满足安全和工程实践要求。论文将 PHIL 定位为二者之间的受控实验层，但同时强调它不是“接上线就可信”：闭环中的延迟、有限带宽、阻抗比、放大器非线性、采样和滤波会同时决定 accuracy（准确性）、bandwidth（带宽）与 stability（稳定性）[pdf:E08]（PDF 物理页 4，Fig. 3 与 Section III-C）。

## § 2 — 前人工作与不足

论文之前已经存在大量可用部件和局部方法。DRTS 侧已有 PC-based、custom-processor-based、supercomputer-based 和 FPGA-based 四类计算平台，以及 classic nodal admittance（CNA，经典节点导纳）、state-space nodal（SSN，状态空间节点）和 Pejovic/associated discrete circuit（ADC，关联离散电路）三类主要求解路径；这些工作解决了实时计算、开关网络离散化、大系统并行和高速 I/O 等问题 [pdf:E03]（PDF 物理页 2，Section II 与 Fig. 2）。功率接口侧已有 switched-mode、linear 和 generator-type 三类 PA，其功率等级、带宽、成本和非线性特性不同 [pdf:E05]（PDF 物理页 3，Section III-A）。IA 侧已有 ideal transformer model（ITM，理想变压器模型）、partial circuit duplication（PCD，部分电路复制）和 damping impedance method（DIM，阻尼阻抗法），并发展了滤波、multirate（多速率）、dq-reference-frame 和 adaptive（自适应）增强方法 [pdf:E06]（PDF 物理页 3，Section III-B）；Table I 进一步把电压型和电流型 ITM、PCD、DIM 的拓扑与 loop transfer function（环路传递函数）放在同一个比较框架里 [pdf:E07]（PDF 物理页 4，Table I）。

不足不在于“没有人做过 PHIL”，而在于知识是分散的。已有工作往往分别关注实时求解器、某种功率放大器、某个 IA 的稳定区，或单一设备的实验，工程人员仍需自行把计算步长、I/O latency（延迟）、功率级动态、HUT 阻抗、滤波器和安全逻辑拼成一个闭环。本文的贡献是把这些部件放进同一个设计视角，并用两个 PV case study（光伏案例）说明系统级取舍。

更根本的缺口仍未被解决。论文直接指出：非线性 HUT 没有标准 PHIL 方案；HUT 往往正因为“没有模型”才被接入 PHIL，但高准确度稳定性分析又需要知道其结构；一般的非线性、时变 HUT 稳定问题仍是开放问题 [pdf:E11]（PDF 物理页 6，Section III-D.2）。此外，固定步长限制大而刚性的系统，设备功率/电压/转矩能力有限，而且当真实全尺寸系统尚不存在时，没有通用 impact assessment methodology（影响评估方法）把误差分解为 PI 误差、模型误差和其他误差 [pdf:E13]（PDF 物理页 7，Section III-F）。因此，这篇论文提供的是“设计地图与已知边界”，不是一个消除这些边界的统一解。

## § 3 — 重建作者的思考路径

下面是基于论文证据的思考路径重建，不是作者逐句陈述的历史过程。

第一步，研究者先遇到纯软件仿真的边界：真实 inverter（逆变器）、保护装置或负载可能没有可信模型，或者其非线性和控制细节不便公开。完整搭建真实电网又昂贵且危险，因此需要只保留关键硬件、把其余系统放进实时仿真的混合实验。

第二步，把真实硬件接入并不自动得到可信结果。Fig. 1 的结构一旦闭环，DRTS、D/A、PA、HUT、传感器、sample-and-hold（采样保持）和 A/D 就共同构成一个动态系统；实时计算必须在每个固定步长内完成，任何 overrun（超时）都可能造成错误或随机行为 [pdf:E02]（PDF 物理页 1，Fig. 1 后正文）。

第三步，研究重点从“是否能实时运行”转为“闭环能否稳定且保真”。不同求解器决定可达到的步长与系统规模，不同 PA 决定功率范围和动态带宽，不同 IA 改变等效阻抗和环路增益。于是 PHIL 设计不能分别采购部件后再集成，而要从目标现象的频率范围出发，联合选择 DRTS、PA、IA、滤波与系统分区。

第四步，作者会发现一个结构性矛盾：HUT 模型缺失是采用 PHIL 的理由，但闭环稳定和高准确度又要求知道 HUT 的动态特性。论文因此把 adaptive IA、HUT property learning（HUT 特性学习）和 nonlinear stability（非线性稳定性）视为未来方向，同时承认一般问题尚无解 [pdf:E11]（PDF 物理页 6，Section III-D.2）。

第五步，设计框架必须落到可执行流程：先离线建模和开环运行，再检查误差、稳定性、I/O 与软硬件保护，最后才闭合功率回路。论文在 PDF 物理页 6 给出的测试程序正是这种“先证明可控，再通功率”的工程化顺序 [pdf:E12]（Section III-E）。

## § 4 — 核心 Intuition

PHIL 的核心不是把真实硬件简单接到仿真器上，而是把整个软件—功率接口—硬件链路当作一个闭环控制系统设计。目标现象越快、模拟系统越复杂，所需时间步长和接口带宽越苛刻，延迟与非理想动态越容易侵蚀稳定裕度。可信实验来自 accuracy、bandwidth、stability 和 safety 的联合取舍，而不是单项指标最大化。论文的主要作用是给出这套取舍的组件地图、控制论解释和实验边界 [pdf:E08]（PDF 物理页 4，Fig. 3 与 Section III-C）。

## § 5 — 具体方法与完整 Pipeline

本文没有提出一个单一算法 pipeline，而是给出 PHIL 系统的设计与实施 pipeline。一个完整实验可以按以下顺序理解。

1. **定义研究现象并划分系统。** 先决定哪些部分留在 DRTS 中作为 rest-of-system，哪些部分作为真实 HUT。DRTS 输出参考电压或电流，PI 把低功率信号转换为真实功率，HUT 的测量量再回到 DRTS [pdf:E02]（PDF 物理页 1，Fig. 1）。划分不仅由设备可得性决定，也会改变闭环阻抗和稳定裕度。

2. **按时间尺度选择 DRTS 架构与求解器。** 论文把平台分为 PC、专用处理器、超级计算机和 FPGA 四类。CNA 通过节点导纳矩阵求解，SSN 从离散状态空间方程自动形成节点方程并可采用比梯形法更稳定的高阶离散方法；Pejovic/ADC 把开关 ON/OFF 分别表示为小电感/小电容，使导纳矩阵保持不变、实时循环中无需矩阵求逆或 LU 分解，但通常需要低于 3 μs 的很小步长才能准确 [pdf:E03]（PDF 物理页 2，Section II）。

3. **处理开关事件、多速率和并行依赖。** 一类 FPGA 平台可在 0.1–1 μs 范围内仿真开关电路，并与 10–50 μs 的 CPU 仿真接口；另一类模块在 1–4 μs 范围运行，并可接入约 50 μs 的大系统模型。论文还描述了 2 μs subnetwork、traveling-wave transmission-line stub 和 multi-FPGA functional decomposition，用于把高速电力电子局部模型与较慢的大电网模型组合 [pdf:E04]（PDF 物理页 3，Section II）。这说明时间推进通常是固定步长、分区和多速率协同，而不是通用的事件驱动自适应步长。

4. **选择功率放大器。** Switched-mode PA 可覆盖小功率到 MW 级，通常能在电压源或电流源模式运行，动态带宽约可做到 2–10 kHz；linear PA 具有更直接的动态和较少的稳定问题，带宽可达约 20 kHz，但成本、重量、损耗和 MW 级扩展性差；generator-type PA 适用于低中功率、平衡三相场景 [pdf:E05]（PDF 物理页 3，Section III-A）。PA 的 transfer function、slew rate、短路行为、隔离和饱和必须在闭环前识别。

5. **选择 PI 拓扑和 IA。** ITM 易实现、准确度高，但常有稳定性问题；PCD 通过在仿真侧和物理侧复制 linking impedance 扩大稳定区域，但高功率场景加入真实阻抗可能困难；DIM 同时使用电压和电流反馈及 damping impedance，在不要求实际 linking impedance 的条件下通常获得更大的稳定区域 [pdf:E06]（PDF 物理页 3，Section III-B）。Table I 展示了电压型与电流型 ITM、PCD、DIM 的电路和环路传递函数，说明 IA 的本质是重新塑造闭环阻抗与增益 [pdf:E07]（PDF 物理页 4，Table I）。需要时再加入硬件/软件滤波、multirate 或 dq-frame 实现。

6. **实现完整 I/O 链并建立闭环模型。** Fig. 4 把 D/A、anti-aliasing filter、stability filter、A/D、sample-and-hold、PA 和 HUT 放在同一电压型 PI 中；这比理想方框图多出实际延迟、滤波和测量动态 [pdf:E09]（PDF 物理页 5，Fig. 4 与 Section III-D.1）。Fig. 5 再把典型 PHIL 近似成含纯延迟、PA transfer function、HUT impedance 和 feedback transfer function 的连续时间闭环，用于稳定性分析 [pdf:E10]（PDF 物理页 5，Fig. 5）。

7. **按安全程序逐级上线。** 论文建议依次完成 test case、设备选择、完整实时模型、无反馈的离线/开环运行、离线稳定与误差检查、闭环稳定性评估、I/O 验证、软硬件 trip limit（跳闸阈值）验证，最后才执行在线闭环 PHIL [pdf:E12]（PDF 物理页 6，Section III-E）。简单把 DRTS 输出置零不一定是所有设备的安全状态，因此保护逻辑必须针对具体实验定义。

以论文的 500 kW PV inverter 案例说明输入—处理—输出：真实 500 kW 三相 inverter 是 DUT，额定交流电压 200 V、直流工作区间 320–500 V；2.5 MW/1 kV dc variable voltage source（VVS，可变电压源）模拟 PV array，1.5 MVA 480 V/4.16 kV 变压器和 2.5 MW/4.16 kV ac VVS 模拟电网，后者可控带宽约 1.2 kHz。DRTS 运行虚拟配电网和 PV I–V 特性，采用 dq-frame voltage-type ITM，反馈电流 cutoff frequency 为 10 Hz，输出参考量驱动两侧 VVS；系统测量 inverter 的电压、电流、功率、PCC 响应和限流行为 [pdf:E15]（PDF 物理页 8，Section IV-B 与 Fig. 9）。

在模板关心的 FPGA 与数值实现层面，论文报告了平台类别、典型步长、求解器和多 FPGA 分解，但没有报告固定点/浮点位宽、LUT/BRAM/DSP 使用量、时钟频率、place-and-route 时序或 case study 的处理器负载。因此它能指导“选哪一类架构”，不能直接复现一份 FPGA bitstream 或精确资源预算。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文是设计综述，没有给出一个从假设到定理的原创完整推导；其核心数学材料是 Table I 中不同 IA 的 loop transfer function，以及 Fig. 5 的连续时间近似模型。

对 voltage-type ITM，Table I 直接给出

\[
F_0(s)=-T_{VA}(s)T_C(s)\frac{Z_1(s)}{Z_2(s)}e^{-sT_s}.
\]

该式位于 PDF 物理页 4 的 Table I，图中同时保留了 simulated source impedance \(Z_1\)、HUT/load impedance \(Z_2\)、voltage amplifier dynamics \(T_{VA}\)、feedback/measurement dynamics \(T_C\) 和 delay term \(e^{-sT_s}\) [pdf:E07]。

工程直觉如下。\(Z_1/Z_2\) 决定接口两侧阻抗如何放大反馈；放大器与测量链的幅频和相频特性进入同一个环路；纯延迟不改变幅值，却会随频率增加相位滞后。因此，当目标带宽提高、阻抗比使交越频率上移，或 PA/传感器增加额外相位滞后时，稳定裕度会快速下降。PDF 物理页 5 的正文进一步指出，常见连续时间近似把 DRTS 的计算与数据采集开销表示为“两倍仿真步长”的延迟，即使时间步长短至 10 μs，某些软硬件参数组合仍可能不稳定 [pdf:E10]（Fig. 5 后正文）。本文没有把 Table I 的 \(T_s\) 与正文中的“两倍步长”在符号上严格统一，因此这里不强行写出未经论文明确给出的等式。

ITM 的优点是直接、准确，但其阻抗比和延迟直接暴露在环路中。PCD 在两侧加入 \(Z_{12}\) 改写等效阻抗，论文认为可扩大相对 ITM 的稳定区域，但真实高功率侧必须加入该阻抗；DIM 通过电压、电流双反馈与虚拟 damping impedance \(Z^*\) 塑造环路，不要求把 linking impedance 真的接入功率回路，通常兼顾较高准确度和更大稳定区域 [pdf:E06]（PDF 物理页 3，Section III-B）。这不是“免费稳定”：滤波或阻尼会降低有效带宽，参数又依赖 HUT 动态。

论文没有给出适用于任意非线性、时变 HUT 的通用 Nyquist 边界、Lyapunov 证明或可计算稳定域。它明确承认，一般非线性 HUT 仍是开放问题；静态非线性可尝试 Popov criterion，已知主要非线性时可设计 nonlinear DIM，但 generalized IA 的理想配置仍未解决 [pdf:E11]（PDF 物理页 6，Section III-D.2）。

## § 7 — 实验设计与结论

**问题 A：PHIL 能否在低压配电网中复现多台分布式 PV inverter 的电压—无功控制和非线性扰动？ → 实验：** Case Study A 把一个带两台真实 inverter 的 LV network 分区为 DRTS 电网和真实 DUT。两台 inverter 分别为 4.6 kVA 单相与 10 kVA 三相，PV array simulator 的系统带宽为 3 kHz；实验配置可编程线路/中性线阻抗，使用 3×10 kVA 线性四象限 amplifier，其 delay 为 4 μs、slew rate 大于 52 V/μs、signal bandwidth 为 30 kHz。经典 ITM 的总体仿真带宽约 1 kHz，multirate interface 可提高到 2–5 kHz [pdf:E14]（PDF 物理页 7，Fig. 6、Fig. 7 与 Section IV-A）。**→ 答案：** 对毫秒级 PQ/VVC 过程，1 kHz 是作者认为可接受的准确度—稳定性折中，实验轨迹能展示有/无 volt–var control 的差异；PHIL 也复现了非线性负载引起的电流扰动。作者进一步给出适用范围：THD 或 fault ride-through 若要覆盖 20th harmonic，总系统带宽应高于 1 kHz；较慢的有功/无功控制只需约 0.2–0.5 kHz [pdf:E15]（PDF 物理页 8，Fig. 8 前后正文）。

**问题 B：PHIL 能否用于 500 kW grid-connected PV inverter 的 reactive power control（无功控制）和配电网影响测试？ → 实验：** Case Study B 使用真实 500 kW inverter、dc/ac VVS、DRTS 虚拟配电网、变压器、故障开关和低带宽 dq-frame ITM。负荷 profile 每 5 s 更新，PV power profile 每 2 s 更新，并提供低、中、高波动三类 profile；重点结果是在 power factor 0.84 lagging、PV 功率高波动条件下观察 inverter 的功率跟踪和限流 [pdf:E16]（PDF 物理页 9，Fig. 10、Fig. 11）。**→ 答案：** measured inverter terminal voltage 大体跟踪 simulated PCC voltage，实测有功/无功也大体跟踪仿真注入量；当 inverter 达到 current limit，dc/ac power 被限制但仍维持命令功率因数。Fig. 12 同时显示实际瞬时电压、电流波形，作者据此认为测试完成了评估 reactive power function 及其配电网利弊的目标 [pdf:E16]（PDF 物理页 9，Fig. 12 与 Conclusion 前正文）。

这些实验支持的是“在特定设备、已调接口和目标时间尺度下，PHIL 能进行有价值的系统级测试”，不是“PHIL 对任意 HUT 都准确”。论文没有报告统一的 RMS error、phase error、THD error、置信区间、FPGA/CPU 资源、实时 deadline margin 或与全尺寸真实电网的盲测对照。Case B 还明确使用 10 Hz feedback cutoff 和慢变化 profile，因此不能把其 tracking 结果外推到快速故障、控制器 mode transition 或高频谐波场景 [pdf:E15]（PDF 物理页 8，Section IV-B）。

## § 8 — Take-aways

**5 句话：**

1. PHIL 是把 DRTS 中的虚拟电力系统与真实功率设备闭环连接的实验方法，其价值在于保留真实硬件行为，同时避免完整系统试验的成本和风险。
2. DRTS、PA、IA、I/O、HUT 和保护不能独立设计，因为它们共同决定 accuracy、bandwidth、stability 与 safety。
3. 固定步长、计算延迟、放大器动态和接口阻抗会把 PHIL 变成一个典型但困难的闭环控制问题 [pdf:E09]（PDF 物理页 5，Fig. 4 与 Section III-D.1）。
4. ITM 简单准确但可能不稳定，PCD 和 DIM 通过改变等效阻抗扩大稳定区，却分别引入真实阻抗或参数依赖等代价 [pdf:E06]（PDF 物理页 3，Section III-B）。
5. 两个 PV 案例证明 PHIL 对特定慢动态和经过调试的系统很有用，但没有解决未知非线性 HUT 的一般稳定性和误差归因问题。

**3 句话：**

1. 先从要观察的物理频率范围和功率等级反推 DRTS 步长、PA 带宽与 IA，而不是从现有设备正向拼装实验。
2. 任何“稳定且能运行”的 PHIL 都不自动等于“准确”，必须用开环基准、稳定性分析、I/O 校准和安全限值逐级闭合 [pdf:E12]（PDF 物理页 6，Section III-E）。
3. 本文最重要的研究缺口是：HUT 越未知，PHIL 越有价值，但接口越难得到可证明的稳定性与准确性。

**1 句话：**

PHIL 的本质是受功率、实时计算与控制稳定性共同约束的实验型闭环系统，而不是一台更快的离线仿真器。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在整个测试工况内，实验者拥有或能够获得足够准确的 HUT 动态信息，从而选择并整定 IA、滤波与带宽，使闭环同时稳定和准确。** 一旦这个假设不成立，PHIL 的核心贡献会直接失效：不稳定会损坏 HUT，稳定但失真又会产生貌似合理、实际错误的系统结论。

论文自己给出了这个假设的矛盾证据。PDF 物理页 6 明确说，HUT model 不可得往往正是建立 PHIL 的主要动机；但要获得高准确度，又需要关于 HUT architecture 的特定知识，尤其当大系统使实时步长无法继续缩小时。作者还指出 HUT 通常是 nonlinear and time-variant，一般情形尚未被系统解决 [pdf:E11]（Section III-D.2）。

论文提供的支持证据是两个经过工程整定的 PV 案例：Case A 在已知带宽、线性 amplifier 和 ITM/MR interface 下得到合理 VVC 与扰动波形，Case B 用低带宽 dq ITM 获得电压和功率跟踪 [pdf:E14] [pdf:E15] [pdf:E16]。但这些证据没有覆盖未知控制器、工作模式切换、饱和、负增量阻抗或快速故障时 HUT 动态突然改变的情况，也没有给出 HUT uncertainty（不确定性）到输出误差和稳定裕度的量化映射。更严重的是，论文承认没有通用 impact assessment methodology 来区分 PI、模型和其他误差 [pdf:E13]（PDF 物理页 7，Section III-F）。

## § 10 — 最小复现实验

一周内最值得复现的是论文的核心控制论 claim：**延迟、接口带宽和阻抗比会共同决定 voltage-type ITM 的稳定边界与准确度。** 前提是已有一个低压 PHIL 台架，不需要复现 500 kW 系统。

- **数据与工况**：由 DRTS 生成 50/60 Hz 正弦、幅值阶跃和小信号 frequency sweep；软件侧采用可调 \(R_1+L_1\) 源阻抗，真实 HUT 使用可切换的低压 R–L load。设置 6–10 组 \(Z_1/Z_2\) 比值，并人为插入 0、1、2、4 个采样周期的附加 delay。
- **实现**：搭建 Fig. 1/Fig. 5 对应的 voltage-type ITM，记录 DRTS 参考电压、HUT terminal voltage、feedback current 和 PA output。再加入一个可调低通 feedback filter，作为论文所述 software stabilization 的最小版本；不必实现完整 DIM。
- **测量**：对每组参数测 RMS/peak error、phase lag、THD、settling time、最大无持续振荡 bandwidth，以及 deadline overrun。用相同网络的全软件仿真作为基准，并用独立示波器采集真实端口量。
- **支持标准**：随着 delay 或 \(|Z_1/Z_2|\) 增加，稳定边界和可用带宽系统性下降；加入滤波后稳定范围扩大但 tracking bandwidth 下降。这与 Table I 的 ITM 环路结构和 Fig. 5 的 delay 解释一致 [pdf:E07] [pdf:E10]。
- **反驳标准**：在测量误差可忽略的条件下，稳定边界对 delay、阻抗比和滤波几乎不敏感，或者系统即使稳定也无法在目标低频范围内接近全软件基准。前一种结果挑战论文的核心环路解释，后一种结果说明“稳定是准确的前提”仍不足以形成可用 PHIL。

实验应限制在隔离低压、设硬件 overcurrent/overvoltage trip，并先执行论文建议的离线、I/O 和安全检查流程 [pdf:E12]（PDF 物理页 6，Section III-E）。

## § 11 — 最强反例设计

最强反例不是再找一个更复杂电网，而是选一个**动态特性会随工作模式突然改变的 nonlinear HUT**，让固定 IA 在标称点看似稳定，却在实际测试包络内可预测地失效。例如使用带恒功率控制、current limit、PLL 重锁定和 fault ride-through mode 的 grid converter：在标称功率点识别一个线性阻抗并整定 ITM/DIM，然后连续扫 irradiance、grid impedance 和 voltage dip，使 converter 穿越限流与控制模式切换。

攻击的替代解释是：论文案例中的良好 tracking 可能主要来自被测动态很慢、接口低通很强，而不是 PHIL 一般地忠实复制真实系统。Case B 的 feedback cutoff 只有 10 Hz，load/PV profile 分别每 5 s/2 s 更新，作者也承认 interface bandwidth 受限 [pdf:E15] [pdf:E16]。因此反例应同时运行两条路径：一条是 PHIL，另一条是同一 converter 接真实可编程电网源的直接硬件基准；比较 mode transition 前后端口波形、功率、保护动作和稳定性。

若 PHIL 在标称点与真实基准一致，但在模式切换时出现未预测振荡、错误保护动作、显著相位/功率偏差，且这些误差不能由传感器噪声解释，就直接击中第 9 节的核心假设。更强的结果是：降低带宽能恢复稳定，却把关键瞬态过滤掉，使实验在“安全但错误”和“保真但不稳定”之间没有可接受区域。这样的反例会表明，固定模型和固定 IA 的设计框架不足以支持未知、时变、强非线性 HUT。

## § 12 — Follow-up Research Idea

**候选方向：建立“带可证误差预算的自校准 PHIL”（self-calibrating PHIL with a certified error budget）。** 这是基于本文证据提出的候选判断；由于本任务没有检索论文之外的相关工作，不声称 novelty。

**（a）未满足需求。** 当前 PHIL 的核心矛盾是 HUT 越未知，实验价值越高，但稳定性和准确度越依赖 HUT 模型；同时缺少方法把最终误差归因到 HUT 模型、DRTS 离散化、PA、传感器、IA 或接口延迟 [pdf:E11] [pdf:E13]。研究目标应从“把闭环调到能运行”改为“对每个实验结论给出可追溯的误差区间和有效工况域”。

**（b）为什么可能有高研究价值。** 电力、控制与电力电子领域重视严格稳定性、可重复硬件验证、工程安全和真实系统价值。若一个 PHIL 系统能在线声明“当前结果误差上界是多少、哪一部分不确定性占主导、何时必须停止实验”，它会把 PHIL 从经验型 test bench 提升为可审计的实验测量平台，直接影响设备认证、保护测试和大功率原型验证。

**（c）可借鉴的方法。** 可组合 online system identification（在线系统辨识）、set-membership estimation（集合成员估计）、robust/adaptive control（鲁棒/自适应控制）、runtime assurance（运行时保障）与 metrology-style uncertainty budget（计量式不确定度预算）。系统在线注入幅值受限的辨识信号，估计 HUT 局部阻抗/动态及置信集合；控制层根据该集合选择 IA 和 filter；安全层只允许在可证明的稳定—误差 envelope 内运行。

**（d）第一个可证伪实验。** 使用第 11 节的 mode-switching converter，并保留独立真实电网源基准。候选系统必须在 converter 进入限流、PLL 重锁定和负增量阻抗区时，提前收缩有效工况域或调整 IA；其预测置信区间必须覆盖真实端口电压、电流和功率，且误差归因要能区分 interface delay 与 HUT model change。若区间频繁漏掉真实值，或系统只有通过把带宽降到失去研究意义才能保持证书，该方向即被证伪。

**（e）与本文已有工作的实质区别。** 论文中的 adaptive IA 主要目标是通过跟踪 HUT 特性改善稳定性，滤波和 multirate 主要是在既定实验中调整稳定—带宽折中 [pdf:E08] [pdf:E11]。候选方向不只是增加一个 adaptive module，而是改变 PHIL 的输出定义：除了波形，还必须输出在线误差分解、可验证的有效域和拒绝不可信实验的机制；它把“稳定控制问题”与“实验结论是否可认证”连接起来。
