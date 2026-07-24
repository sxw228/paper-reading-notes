# A Low-Cost Real-Time Hardware-in-the-Loop Testing Approach of Power Electronics Controls

作者：Bin Lu、Xin Wu、Hernan Figueroa、Antonello Monti  
出处：IEEE Transactions on Industrial Electronics，Vol. 54，No. 2，pp. 919–931  
年份：2007  
DOI：10.1109/TIE.2007.892253  
Zotero key：DSATQRHR  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 论文要解决的问题不是单独设计一种 converter controller，而是建立一套足够便宜、能够满足 hard real-time（硬实时）约束、又能把真实控制器或真实功率硬件接入仿真的 HIL 测试环境，并给出从纯软件设计逐步过渡到真实硬件测试的工程流程。作者把系统称为 VTB-RT：它以 open-source software（开源软件）和 off-the-shelf hardware（现成商用硬件）实现，强调 multisolver、multiplatform 与 hard real-time，并用 boost converter 和 H-bridge inverter 两个控制案例验证可用性。PDF 物理页 1，Abstract。[pdf:E01]

这个问题重要，因为 power electronics controls（电力电子控制）同时受快速开关、采样、A/D 与 D/A 转换、通信和模型积分影响。传统纯软件仿真无法完整暴露真实 I/O、执行时间和硬件非理想性；若控制缺陷直到现场测试才被发现，修改代价和设备风险都会显著上升。论文还指出，当时已有 real-time simulation（实时仿真）方案常见的问题包括 soft real-time、非实时、依赖特定硬件、专有平台成本高，或只支持单一平台和 solver，而 power electronics 对时间精度尤其敏感。PDF 物理页 1，Introduction。[pdf:E02]

**基于证据的推断。** 这篇论文真正试图降低的是“把控制算法送入真实功率级之前的验证门槛”。它把 HIL 从昂贵实验室基础设施变成普通 PC、DAQ 和开源实时内核能够承担的设计环节；价值不只是节省采购费，也在于把算法正确性、实时可执行性和硬件接口问题放进同一个迭代闭环。

## § 2 — 前人工作与不足

**论文对相关文献的概括。** 作者把 RT-Lab、RTDS、HyperSim 等系统归为 proprietary solutions（专有解决方案），并将此前大量 RTS 工作的不足概括为：有的只能 soft real-time 或非实时运行，有的绑定特定硬件，有的依赖昂贵商业平台，有的只支持一个 solver 或一个平台。论文也提到 fixed-step switching-event compensation（定步长开关事件补偿）和 averaging methods（平均模型方法）可以缓解时间精度问题，但这些方法并没有同时解决低成本、硬实时、真实 I/O 耦合和多 solver 兼容。PDF 物理页 1，Introduction；物理页 3，Section III-B。[pdf:E02]

VTB 是 VTB-RT 的非实时前身。它已经具备 multiformalism、multiplatform、multisolver、分布式仿真和交互可视化能力，且可把不同子系统交给不同积分方法与步长；但当真实硬件进入闭环时，Windows 或普通 Linux 无法保证确定性的硬实时推进，因此还缺少一个可靠的时钟、确定性中断、DAQ 驱动和实时执行路径。作者的改进不是推翻 VTB，而是保留模型、solver 和 schematic 文件格式，在 Linux 上加入 RTAI、Comedi 与实时任务，使原有虚拟原型能够进入硬实时。PDF 物理页 2，Sections II–III；物理页 3，Section III-B。[pdf:E03] [pdf:E04]

这篇论文对 prior work 的比较仍然偏定性。它没有提供统一任务上的商业系统基准、购买成本明细、jitter 分布或相同误差阈值下的 cost/performance 曲线。因此，“very-low-cost 且性能可比”在论文中主要由平台配置和两个案例支撑，而不是严格的横向 benchmark；这一点限制了其相对优势的可量化程度。

## § 3 — 重建作者的思考路径

可以把作者走向 VTB-RT 的思考过程重建为五步。

第一，控制器在 averaged model 或理想 switching model 上工作，不代表它能在真实 I/O、损耗和延迟下工作，因此最终必须把至少一部分仿真模型替换为 hardware under test。第二，HIL 中时间不能暂停，solver 每个 step 必须在 deadline 前完成，因此需要由内核级实时任务而不是普通用户进程定义时间。第三，为了不重新建立整套模型生态，最经济的路径是复用 VTB 的 C++ solver、模型和 `.vts` schematic，只替换底层执行环境。第四，真实电气端口不应被简化成随意的单向 signal；RCM 用 across/through variables 和守恒关系表示元件，使 simulation model 与 real hardware 能在同一物理接口语义下耦合。PDF 物理页 2，Eq. (1) 及其后说明。[pdf:E03]

第五，当一个 host 无法在 step 内完成全部求解时，把 plant 和 controller 分到不同实时主机，通过 DAQ 连接进行 distributed simulation（分布式仿真）。这种推理最终形成一条逐级增加真实性的验证路径：先纯软件，再可选的 VTB–Simulink cosimulation，再分布式仿真，最后以真实功率硬件替换 plant model。PDF 物理页 4，Figs. 3–4；物理页 5，Fig. 5。[pdf:E05] [pdf:E06]

## § 4 — 核心 Intuition

保留同一套 controller model 和 solver 接口，逐步把理想 plant model 换成分布式模型乃至真实硬件，就能在不重写控制设计的情况下连续增加测试真实性。RTAI 提供不可回退的 real-time clock，FIFO 把时钟送给用户态 solver，RCM 则让模型与硬件通过符合物理守恒的端口自然耦合；单机算不完时再按 plant/controller 依赖切分到多机。PDF 物理页 2，Eq. (1)；物理页 4，Figs. 3–4；物理页 5，Fig. 5。[pdf:E03] [pdf:E05] [pdf:E06]

## § 5 — 具体方法与完整 Pipeline

### 1. 模型与 solver

VTB-RT 复用 VTB 的 SAC 与 SRC solver。论文的核心物理建模关系来自 resistive companion modeling（RCM）：

\[
I(t)=G(t-h)\,V(t-h)-B(t-h),
\]

其中 \(I\) 是 through-variable vector，\(V\) 是 across-variable vector，\(G\) 是 conductance matrix，\(B\) 是 state-source vector，\(t\) 为当前时间，\(h\) 为 simulation step。作者认为，这种按守恒律表达组件的方式，使 SRC solver 能把 simulation model 与 real hardware 以自然端口关系连接，并支持 virtual power exchange。PDF 物理页 2，Eq. (1) 及变量定义。[pdf:E03]

论文没有报告 fixed-point 数值格式、量化位宽、稀疏矩阵结构、switching event 的精确插值规则或 FPGA 内部 solver 映射。它明确说明 SRC 使用 trapezoidal integration（梯形积分），而 FPGA 只在“recent progress”中作为高速信号调理和 I/O interface，用来减轻快速 PWM 与 encoder signal 的采集/生成负担，不是本文两个核心实验中的主求解器。PDF 物理页 9，Section VI-B；物理页 11，Conclusion and Recent Progress。[pdf:E12] [pdf:E18]

### 2. 实时执行路径

软件栈由 Linux、RTAI、Comedi/Comedilib 和 VTB solver/models 组成。RTAI 在 kernel space 中生成 periodic real-time task，并驱动 8254 clock；每个新 step 的时钟消息写入 real-time FIFO。用户态 Linux process 轮询 FIFO，一旦检测到新 step，严格按 `DAQ input → solve state → DAQ output` 的顺序执行。这样，实时任务负责“什么时候开始下一步”，solver 负责“在这一步内算完什么”，FIFO 则隔离 kernel-space clock 与 user-space computation。PDF 物理页 3，Sections III-B–D；物理页 4，Figs. 3–4。[pdf:E04] [pdf:E05]

### 3. 四阶段设计与测试 pipeline

1. 在 VTB 或 Simulink 中建立 plant 和 controller 的高保真模型，调好控制参数，得到 ideal result。  
2. 可选地把 Simulink controller 导入 VTB 做 cosimulation，检查跨工具接口。  
3. 将 plant 与 controller 分区到不同 host，做实时或非实时 distributed simulation。  
4. 保留 VTB-RT 中的 controller，直接以 real power electronics hardware 替换 plant model，执行 hard real-time HIL。PDF 物理页 5，Fig. 5；物理页 6，Section IV Steps 3–4。[pdf:E06] [pdf:E07]

### 4. Boost converter 例子

作者先在线性化模型上做 pole placement，再在 VTB 中得到 12 V 到 20 V 的理想闭环响应；随后经历 VTB–Simulink cosimulation、VTB 与 dSpace 的非实时分布式仿真，最后把 state-space controller 导出到 VTB-RT，并通过三块 PCI-1710 I/O interface model 与真实 boost converter 交换信号。设计 poles 为 \(-2000\) 和 \(-5000\)，对应 \(k_1=-0.0161\)、\(k_2=-0.0206\)。PDF 物理页 7，Section V-A、Figs. 8–9。[pdf:E08]

实物 HIL 中，输出稳态约为 11.6 V 和 19.2 V，而理想模型为 12 V 和 20 V；作者把差异归因于理想模型未计入真实损耗，并把波形的 piecewise-like behavior 归因于 300 μs 实时 step。更快平台在相似例子中达到 50 μs。PDF 物理页 8，Fig. 10、Table IV 及相邻正文。[pdf:E09]

### 5. H-bridge inverter 例子与分布式执行

第二个例子只用 VTB/VTB-RT 完成 PI controller 设计，省略 Simulink。plant 是整流器、H-bridge 和 1 mH、0.01 Ω 的负载，controller 根据 current feedback 产生 duty ratio；作者先分析单 step delay 下的离散稳定性，再把 plant 与 controller 分到两台相同的 VXI-872Bpc 主机，通过各自 DAQ 的直接 analog connection 交换信号。PDF 物理页 8，Table V、Figs. 11–12 及 Section VI；物理页 9，Section VI-C。[pdf:E10] [pdf:E13]

两个 VTB-RT process 的结构是各自拥有 RTAI clock、solver 和 DAQ，一台运行 plant model，另一台运行 controller model。Appendix 给出的最小安装顺序是 Linux/RTHAL kernel → RTAI → Comedi/Comedilib → 移植并编译 VTB-RT solvers/models。PDF 物理页 10，Figs. 15–16；物理页 12，Fig. 18。[pdf:E15] [pdf:E19]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学部分不复杂，但它把“模型离散化、通信延迟和可实现 step”连成了一个工程稳定性判断。

第一层是 RCM 元件表达式 Eq. (1)。它把元件在上一个离散时刻的端口关系写成 conductance term 与 history/state source 的组合。工程直觉是：每个元件先根据历史状态形成等效代数关系，再由系统 solver 在当前 step 统一求解节点变量；这样既适合固定步长，也便于把真实端口接入统一的 across/through 框架。PDF 物理页 2，Eq. (1)。[pdf:E03]

第二层是 boost controller 的线性 pole placement。作者选择闭环 poles \(-2000\) 和 \(-5000\)，目标输出 20 V，得到 \(k_1=-0.0161\)、\(k_2=-0.0206\)。论文没有在正文重列完整 state-space matrices，因此这里无法从 PDF 独立重推 gains，只能确认这些参数是作者按其引用文献得到并用于后续 HIL。PDF 物理页 7，Section V-A Step 1。[pdf:E08]

第三层是 H-bridge PI controller。作者先指定 open-loop bandwidth 与 phase margin：

\[
\omega_{BW}=2\pi\times100\,\text{Hz}=628\,\text{rad/s},\qquad \phi_{PM}=50^\circ.
\]

考虑 A/D、D/A 与 plant/controller 间信号传输的延迟，以 \(T_s=250\,\mu s\) 修正 phase margin：

\[
\phi^*_{PM}=50^\circ+\Delta\phi
=50^\circ+\frac{\omega_{BW}T_s}{2}
=54.5^\circ.
\]

由此得到 \(K_p=0.0169\)、\(K_i=7.8213\)。PDF 物理页 8，Section VI-A；物理页 9，Section VI-A。[pdf:E11] [pdf:E12]

连续域 open-loop transfer function 为

\[
G_O(s)=\frac{0.506s+234.4}{0.001s^2+0.01s}. \tag{2}
\]

因为 SRC solver 使用 trapezoidal integration，作者用双线性替换 \(s=\frac{2}{T_s}\frac{z-1}{z+1}\) 得到

\[
G_O(z)=
\frac{0.506\frac{2}{T_s}\frac{z-1}{z+1}+234.4}
{0.001\left(\frac{2}{T_s}\frac{z-1}{z+1}\right)^2
+0.01\frac{2}{T_s}\frac{z-1}{z+1}}. \tag{3}
\]

再把 signal processing、conversion、communication 与 integration 总体近似成内部 one-step delay，闭环 characteristic equation 写成

\[
1+\frac{G_O(z)}{z}=0. \tag{4}
\]

这里的 \(1/z\) 就是一拍延迟。对不同 sampling period 做 root locus 后，论文报告当 step 大于 2.1 ms 时系统变得不稳定；实际平台选 250 μs，因此在该近似模型内留有稳定裕度。PDF 物理页 9，Eqs. (2)–(4)、Section VI-B；物理页 8，Fig. 12。[pdf:E12] [pdf:E10]

**批评。** 这个推导证明的是“线性化模型 + 单步等效延迟 + 梯形离散”下的 nominal stability，不等同于证明真实系统在 jitter、偶发 deadline miss、非线性 switching、DAQ saturation 或多步延迟下稳定。论文也没有把数值积分误差与 I/O 延迟误差分离。

## § 7 — 实验设计与结论

**问题 1：低成本 VTB-RT 能否让真实 boost converter 的闭环响应接近纯软件设计？**  
实验：先在 VTB 中模拟 12 V→20 V reference step，再保持 controller 不变，把 plant 替换成真实 boost converter，比较 Fig. 7 与 Fig. 10。软件模型跟踪到 12 V 和 20 V；HIL 稳态约为 11.6 V 和 19.2 V，波形因 300 μs step 呈分段感。作者认为整体瞬态一致，稳态偏差来自真实损耗。PDF 物理页 6，Fig. 7；物理页 7，Section V-A；物理页 8，Fig. 10。[pdf:E07] [pdf:E08] [pdf:E09]

答案：该实验支持“同一 controller 可以从 VTB 平滑迁移到 VTB-RT 并驱动真实硬件”，但没有给出 RMSE、overshoot、settling time 误差或重复实验统计，因此只能证明定性一致，不能证明高精度等价。

**问题 2：VTB-RT 能否在两台主机上实时分割 H-bridge plant 与 PI controller，并保持与非实时仿真一致？**  
实验：在 VTB 中加入一拍 delay，分别施加 10 Hz、1.5 A square-wave reference 和 10 Hz、2.5 A sinusoidal reference，得到 Fig. 14；再把 plant/controller 分到两台 VTB-RT，以 250 μs step 和 analog DAQ link 运行，得到 Fig. 17。PDF 物理页 9，Section VI-C；物理页 10，Fig. 14；物理页 11，Fig. 17。[pdf:E13] [pdf:E14] [pdf:E16]

答案：两组图都显示输出电流跟踪 reference，square-wave 情况具有相似的二阶过渡和尖峰，sinusoidal 情况曲线近似重合，因此支持“分布式实时执行没有改变主要闭环行为”。但作者同样没有给频域误差、相位差、峰值误差或同步 jitter；波形相似是视觉证据，不是严格等效性检验。

**问题 3：实时 step 是否能在实际计算预算内闭合？**  
实验：Table VI 把 250 μs step 分解为 RCM 求解 71 μs、SRC 相关求解/接口 116 μs、输出与 logging 33 μs、additional overhead 30 μs。作者还报告，减少 logging 并使用 Table IV 的更快平台后，该实验达到 100 μs step。PDF 物理页 11，Table VI；物理页 10，Table VI 相邻说明。[pdf:E17] [pdf:E15]

答案：在这两个固定模型与给定平台上，计算时间能够塞进 deadline；同时数据也显示 250 μs 已接近预算总和，logging 和不可解释 overhead 占据了重要余量。论文没有报告 worst-case execution time、长期 deadline-miss count 或调度 jitter，因此“hard real-time”主要由 RTAI 架构和单步时间分解支撑，而不是完整实时性统计。

**不得外推的范围。** 两个案例都是 textbook-scale、低阶控制问题；论文自己承认最小 step 受 CPU、DAQ 和系统复杂度限制，只能覆盖有限 bandwidth。更复杂三相、motor-drive 和高速 PWM 场景需要 FPGA signal-conditioning interface，说明核心平台的 CPU/DAQ 路径并非无条件扩展。PDF 物理页 11，Conclusion and Recent Progress。[pdf:E18]

## § 8 — Take-aways

**5 句话。** ① 论文证明了 open-source Linux/RTAI/Comedi 加普通 PC/DAQ 可以组成可工作的 hard real-time HIL 平台，而不必从昂贵商业系统起步。[pdf:E04] ② 它最重要的工程设计是让 VTB schematic、C++ solver 和 controller model 从非实时环境直接迁移到 VTB-RT，并通过固定四阶段 pipeline 逐步增加真实度。[pdf:E06] ③ RCM 的价值不是一个新控制律，而是提供 simulation model 与 real hardware 共享的物理端口表达。[pdf:E03] ④ 两个案例展示了 boost converter HIL 与 H-bridge 分布式实时仿真的定性一致性，但验证缺少量化误差和实时 jitter 统计。[pdf:E09] [pdf:E16] ⑤ 平台的真正上限是每步总计算/I/O 时间与被测系统 bandwidth 的耦合，FPGA 扩展也正是为绕开高速信号处理瓶颈。[pdf:E17] [pdf:E18]

**3 句话。** VTB-RT 把“可复用模型 + 硬实时调度 + 真实 I/O”组合成一条低成本 HIL 路径。论文的案例证明这条路径能跑通，却没有证明其精度、实时裕度和扩展性在更苛刻 switching system 上仍然成立。阅读时应把它看成一篇系统实现与方法论论文，而不是一种被全面 benchmark 的新 numerical solver。

**1 句话。** 这篇论文的核心贡献，是用可复用 VTB 模型、RTAI 时钟和 RCM 硬件接口把低成本 PC 变成一套能逐步从仿真走到真实功率硬件的 HIL 验证链。

## § 9 — 最脆弱的假设

最脆弱的假设是：**对目标 power-electronics bandwidth 而言，固定 step 内的 solver、DAQ、通信和 logging 总工作量始终能在 deadline 前完成，而且这一 step 所引入的离散化与总延迟仍足够小。** 一旦这个假设失效，系统不仅“精度变差”，还可能发生 deadline miss，使仿真时间落后于物理时间；闭环等效延迟也可能从一拍变成不确定的多拍，直接破坏 Eq. (4) 的稳定性分析。

论文给出的正面证据是：H-bridge 的线性化单步延迟模型在 step 超过 2.1 ms 时才失稳，而实验选择 250 μs；Table VI 的各项时间刚好合计到 250 μs，并且更快平台能做到 100 μs。PDF 物理页 9，Eq. (4) 与稳定性结论；物理页 11，Table VI。[pdf:E12] [pdf:E17]

缺失的证据更关键：没有 worst-case execution time 分布、长时间 deadline-miss 率、不同 switching phase 下的计算峰值、DAQ jitter、异步 event 对固定步长误差的影响，也没有在模型复杂度逐渐上升时测量实时裕度如何塌缩。作者在结论中明确承认平台成本与可用 bandwidth 之间必须折中，并引入 FPGA 接口处理高速和变频 switching signal，这实际上从侧面确认了该假设是系统瓶颈。PDF 物理页 11，Conclusion and Recent Progress。[pdf:E18]

## § 10 — 最小复现实验

一周内最值得复现的不是整套 2007 年软件栈，而是论文的核心可证伪 claim：**同一 controller 从 offline model 迁移到固定步长 HIL 后，主要闭环响应保持一致，并且 step 变小时误差下降。**

使用论文给出的 boost converter 条件：12 V 输入、40 V 额定输出、46 μH 输入电感、1.360 mF 输出电容、35 Ω 负载、50 kHz switching frequency，以及 \(k_1=-0.0161\)、\(k_2=-0.0206\)。先建立 offline switching model，再在一个低压实物 boost 或受控功率级上执行 controller，分别采用 300 μs、250 μs 和 100 μs 的 host update step；若无法安全搭建实物，至少把 plant 放到独立实时进程/主机并保留真实 DAQ loop。论文参数与原始 HIL 对照见物理页 5，Tables II–III；物理页 7，Section V-A；物理页 8，Fig. 10。[pdf:E20] [pdf:E08] [pdf:E09]

测量四项：reference 12 V→20 V 的 steady-state error、overshoot、settling time、每步 execution time/deadline miss。结果支持论文 claim 的标准是：HIL 与 offline 的 transient ordering 和稳定性一致，且从 300 μs 降到 100 μs 时 piecewise artifact 和动态误差显著减小，同时 deadline miss 为零。反驳标准是：即使无 deadline miss，真实响应仍出现无法由损耗解释的系统性偏差；或 step 减小后因计算超时反而产生不稳定。

为了闭合工程复现，安装流程只需保持论文的逻辑顺序：real-time-capable Linux → real-time task/FIFO → DAQ driver → solver/model；不必机械复刻旧版本号。原论文完整顺序见 PDF 物理页 12，Fig. 18。[pdf:E19]

## § 11 — 最强反例设计

最强反例不是再换一种 converter，而是构造一个**计算负载与 switching event 同时呈突发性、并且闭环 bandwidth 接近平台 step 上限**的系统。具体做法是：在 H-bridge 或 motor-drive 模型中加入高速、变频 PWM 与 encoder-like asynchronous signals，逐步增加 switching device 数、I/O channel 数和每步 logging 量；同时把 controller bandwidth 向固定 step 的 Nyquist/延迟边界推进。在每个工况下记录 deadline miss、实际 step jitter、相对高精度 event-aligned reference 的电流误差和闭环 poles 漂移。

这个反例直接攻击论文机制：Table VI 表明 250 μs 已被 71 μs RCM、116 μs SRC、33 μs logging 和 30 μs overhead 用满；如果 event burst 让某些 step 超过预算，Eq. (4) 的 one-step delay 假设就会变成 time-varying delay。PDF 物理页 11，Table VI。[pdf:E17]

它还提供一个替代解释：两个原实验成功，可能主要因为被测对象低阶、参考频率低、动态相对 step 足够慢，而不一定是 RCM natural coupling 本身保证了普遍的高保真。论文提到高速/变频 gating signal 已迫使系统加入 FPGA-based interface，这正是该反例的现实入口。PDF 物理页 11，Conclusion and Recent Progress。[pdf:E18]

若系统在负载突发、异步 event 和接近带宽上限时仍保持零 deadline miss、受控 jitter 和稳定误差界，反例失败；若只需少量复杂度增长就出现不可预测多步延迟或波形失真，则论文的“acceptable resolution”只能限定在轻负载、低 bandwidth 场景。

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty。** 提出一种 deadline-aware、event-aware 的 hybrid HIL architecture：CPU 负责低频状态与控制求解，FPGA front-end 负责 switching-event timestamp、PWM/encoder I/O 和短时局部预测；调度器根据在线 worst-case execution estimate 动态选择 partition、step 与 event batching。研究目标不再只是“以某个固定 step 跑起来”，而是对每个工况同时给出可验证的 deadline margin 与 waveform-error envelope。

(a) **未满足需求。** 原论文已经显示 platform cost、system bandwidth 与 minimum step 强耦合；高速、变频信号又需要 FPGA 接口。现有流程缺少在工作负载变化时可观测、可证明的实时裕度。PDF 物理页 11，Table VI 与 FPGA progress。[pdf:E17] [pdf:E18]

(b) **可能的研究价值。** 在 power electronics/real-time simulation 领域，高影响工作通常需要同时证明 numerical fidelity、deterministic timing、hardware feasibility 和对复杂系统的扩展性。若系统能够在复杂度变化时自动维持误差与 deadline 双约束，它改变的是 HIL 的验收目标，而不是单纯换更快 CPU。

(c) **可借鉴的相邻工具。** 可以借鉴 real-time scheduling 的 worst-case execution analysis、networked control 的 time-varying delay model，以及 FPGA timestamping/event processing。这里是基于论文瓶颈的候选组合，源 PDF 未证明其新颖性。

(d) **第一个证伪实验。** 在相同硬件上比较 fixed-step CPU-only、固定 FPGA I/O、以及 deadline-aware hybrid 三种架构；使用逐步增加 switching/event 密度的 H-bridge workload。若 hybrid 不能在相同资源下同时降低 deadline miss 和波形误差，或其自适应行为引入新的不稳定性，该想法即被证伪。

(e) **与本文的实质区别。** 本文把 FPGA 作为高速 signal-conditioning interface，并把 step 视为平台和模型共同决定的固定结果；候选方向把 event timing、partition 与 step 变成闭环管理对象，并要求输出可审计的实时/误差保证。这是从“低成本实现一套 HIL”转向“在动态 workload 下认证 HIL 可信度”。
