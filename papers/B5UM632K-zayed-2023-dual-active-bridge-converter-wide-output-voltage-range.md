# A Dual-Active Bridge Converter With a Wide Output Voltage Range (200–1000 V) for Ultrafast DC-Connected EV Charging Stations

- 作者：Omar Zayed；Ahmed Elezab；Ahmed Abuelnaga；Mehdi Narimani
- 出处：IEEE Transactions on Transportation Electrification，Vol. 9，No. 3，pp. 3731–3741
- 年份：2023
- DOI：10.1109/TTE.2022.3232560
- Zotero key：B5UM632K
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是一般意义上的“再做一个 DAB”，而是一个由 dc-connected 快充站结构逼出来的接口矛盾：站内共享前端给出固定 dc-bus，而车辆电池端可能要求从 200 V 到 1000 V 的宽电压；单个功率模块还必须隔离、双向、易并联扩容，并在整个范围内保持合理的器件利用率和效率。作者把目标明确为一台直接连接固定母线、覆盖 200–1000 V 的 bidirectional dc/dc module，并用 10 kW、1 kV 原型验证。PDF 物理页 1 的摘要、Fig. 1 与 Table I 同时给出了固定母线场景、目标电压范围和不同车辆电池电压的工程背景。[pdf:E01]

这个问题重要在两个层次。站级上，dc-connected 架构把集中整流、RES 和 ESS 接在共享母线上，减少每个充电桩重复的前端级；模块级上，同一套硬件若能服务 400 V 与 800 V 平台，就能提高桩的利用率并降低为车型分档配置硬件的成本。作者还指出 ultrafast charging 常指 350 kW 以上，400 V 系统会很快碰到电缆重量和电流限制，因此高压电池正在增多；这使“同时兼容旧车与新车”成为真实的基础设施问题，而不只是实验室里的宽增益挑战。该背景和“320 km 轻型 EV、80% SOC、10 min”示例位于 PDF 物理页 2。[pdf:E02]

需要限定外推：本文实验对象是一个 10 kW module 和电阻负载，不是完整 350 kW 充电站，也没有连接真实电池、车桩通信、保护或计量系统。因此，论文直接证明的是模块拓扑与设计方法的可行性，而不是整站 ultrafast charging 已经完成系统级验证。

## § 2 — 前人工作与不足

作者在引言中把已有 charging-pole dc/dc 方案的不足归为五类：依赖 multistage ac-connected 架构、无法高效覆盖宽电压、器件数或器件 kVA 过高、非隔离、以及单向而无法 V2G。论文点名比较了 conventional DAB、three-level/NPC DAB、series/parallel-reconfigurable three-phase DAB、LLC、partial-power processing 等路线，并声称所列方案至少同时带有两类限制。关键结构性原因是：ac-connected 方案常让各自的前端共同参与调节输出电压，而共享前端的 dc-connected 站不能把这一自由度复制给每个 charging pole。上述归纳及引用范围见 PDF 物理页 2 的 Introduction 与 contributions。[pdf:E02]

论文并不是从零发明 series/parallel 概念。Section II 明确把两种模式放在既有 IPOS 与 IPOP converter 经验下解释：前者用串联输出分担高电压，后者用并联输出分担电流；本文把它们合到一台 dual-secondary DAB 中。该 prior-mechanism 定位见 PDF 物理页 3 的 Section II-A。[pdf:E03] conventional DAB 的具体困难则由 PDF 物理页 4 的 Fig. 6 显示：固定变比在远离 unity gain 的 200–1000 V 区域出现较高 primary rms current，作者据此把 current/voltage stress 与成本、性能下降连接起来。[pdf:E04]

论文给出的器件级对比更具体。Table II 在统一缩放到 10 kW 后，将 conventional DAB、文献 [13] 的 NPC DAB 与 proposed DAB 比较：归一化 total kVA 分别为 2.7、2.6 和 1；proposed DAB 的 primary/secondary switch 数为 4/8，无额外 diode 或 flying capacitor，复杂度标为 medium。这个表支持“更高器件利用率”的方向性论据，但它依赖文中说明的理想平衡和额定量换算，并非三台等条件原型的实测 BOM、损耗或成本对比。证据位于 PDF 物理页 5，Table II 及相邻 Eq. (14)–(15)。[pdf:E05]

所以本文真正补的缺口是：在固定输入母线条件下，把输出重构能力放进隔离 DAB 的双次级侧，再用面向完整 charging profile 的能量效率而非单一额定点来选参数。本文没有做系统性文献复现，也没有证明所有既有方案都不能经过重新设计达到相同目标；“优于前人”应理解为作者所选模型和对比边界内的结论。

## § 3 — 重建作者的思考路径

可以从 conventional DAB 的已知失败模式逆向走到本文方案。第一步，DAB 的最低电流应力通常出现在电压增益接近 unity 的区域；固定变比的 converter 若被迫横跨 200–1000 V，会在远离 unity gain 时产生较大的 reactive current。作者用相同 \(n\)、\(L_{\text{shim}}\)、\(f\) 的 10 kW conventional DAB current map 展示了这种离开 400 V 最优点后电流应力迅速上升的现象，见 PDF 物理页 4，Fig. 6 与相邻讨论。[pdf:E04]

第二步，与其让一个固定变比覆盖五倍电压范围，不如让硬件在两个较窄的有效增益区间之间切换。已有 IPOS/IOPP 思路已经表明，串联输出适合分担高电压，并联输出适合分担大电流；把同一磁芯上的两组等匝次级做 series/parallel reconfiguration，就能让 P-mode 和 S-mode 分别围绕自己的 unity-gain 区域工作。作者的 Fig. 2 给出两种连接，Fig. 3 再把 Idle、P-mode、S-mode 和断开输出的 T-mode 组织成状态机；这些是论文 idea 之前就可由 DAB、IPOS/IOPP 与模块化快充经验连接起来的线索。模式状态和等效模型见 PDF 物理页 3，Fig. 3–4 与 Section II。[pdf:E03]

第三步，若 converter 最终工作在整段充电曲线上，额定点效率就不是正确目标。实际充电过程对不同电压、电流点停留的能量不同，因此应先把 charging profile 转成等能量样本，再让优化器在这些点上累计损耗。最后才自然得到本文的两部分方案：可重构拓扑负责把电气工作点拉回低应力区，energy-weighted GA 负责在真实使用分布上选 turns ratio 和 shim inductance。

## § 4 — 核心 Intuition

普通 DAB 在固定变比下要硬扛五倍输出电压范围，偏离 unity gain 时 circulating current 和器件应力会变坏；本文通过两组相同次级在低压时并联、高压时串联，让同一套开关在两个更友好的增益区间工作。然后它不以某一个 rated point 的峰值效率为目标，而按充电过程中实际传递的能量给各 operating point 加权，从而把磁件和电感参数优化到“整段充电少损耗”，而不是“单点最好”。这两条机制分别由 PDF 物理页 3–5 的 mode/equivalent model、current map 和 optimal transition 分析支撑。[pdf:E03] [pdf:E04] [pdf:E05]

## § 5 — 具体方法与完整 Pipeline

以固定 \(V_{\text{in}}=800\text{ V}\)、目标输出从 400 V 升到 1000 V 的一次充电过程为例，完整 pipeline 如下。

1. **决定输出连接。** 低于 transition voltage \(V_T\) 时进入 P-mode，两个次级 dc 输出并联，mode-switch states 为 \([S_{p1},S_{p2},S_s]=[1,1,0]\)；高于 \(V_T\) 时进入 S-mode，两个次级串联，状态为 \([0,0,1]\)。若充电过程中要求换模，先进入 T-mode、停用输出并令三个 mode switch 全关，再进入目标模式。作者设想多模块充电桩逐个换模，使任意时刻仍有其他模块供能；这不是单模块无缝切换。状态机和三电压源到二电压源的等效过程见 PDF 物理页 3，Fig. 3–4。[pdf:E03]
2. **在选定模式内传功。** 主、次级 active bridge 以 SPS 产生方波，通过两只相等的 secondary shim inductors 传递功率。S-mode 的 conversion-ratio parameter \(M=2\)，P-mode 为 \(M=1\)；控制量是两侧桥电压的 phase shift \(\phi\)。低功率时作者允许使用 TPS 进一步压低 rms current。[pdf:E03] [pdf:E05]
3. **选择 mode-transition threshold。** 简化方案用理想 \(V_{T,\mathrm{ideal}}\)；更优方案求使两种模式 rms current 相等的 \(V_{T,\mathrm{opt}}\)，从而避免在错误模式中承受额外 circulating current。PDF 物理页 4–5 的 Eq. (10)–(13) 与 Fig. 7–8 给出计算和 current map。[pdf:E04] [pdf:E05]
4. **把 charging profile 变成优化样本。** 论文使用 CP400、CP600、CP800 三条 profile。CP400 来自 2015 Nissan Leaf 的 50 kW、400 V session，并缩放为每模块 10 kW；CP600 与 CP800 是 generic profile。每条曲线按相等充电能量 \(q_j\) 切段，以能量加权平均得到 \((q_v,q_i)\)，使时间长但能量小的点不会被简单采样频率放大。数据来源和 Eq. (16)–(20) 位于 PDF 物理页 6，Fig. 9–11。[pdf:E06]
5. **运行 GA 和 loss model。** GA 在 \(0.35<n<0.75\)、\(10\,\mu\text{H}<L'_{\text{shim}}<80\,\mu\text{H}\) 内搜索，约束包括 800 V input、200–1000 V output、10 kW、36 A、100 kHz、core-loss density、winding current density 和 capacitor ripple。每个候选参数都重新选择器件，通过厂商 LUT、analytical Fourier model、ZVS constraint、conduction/switching/magnetic losses 计算所有量化点效率，再最小化 \(-\eta_{wt}\)。三条 profile 在研究中取等权，结果为 \(n=0.5\)、折算到 primary 的 \(L'_{\text{shim}}=40\,\mu\text{H}\)，模型给出 \(\eta_{wt}>98\%\)。PDF 物理页 7 的 Fig. 12、Eq. (21) 与相邻正文记录了目标函数和结果。[pdf:E07]
6. **完成 magnetics 与原型。** core 选择后再优化 \(B_{\max}\) 和匝数以最小化 core plus copper loss。原型采用双 E71/33/32 core stack、fully interleaved winding，最终 Table III 报告 12:6:6 匝、每个 secondary \(L_{\text{shim}}=20\,\mu\text{H}\)、100 kHz、10 kW、800 V input、200–1000 V output、36 A maximum output current；控制器为 TI Delfino F28379D 200 MHz DSP。硬件和规格见 PDF 物理页 8，Fig. 13–15 与 Table III。[pdf:E08]

本文采用的是稳态 Fourier/harmonic model 和 manufacturer LUT loss model，没有给出 EMT 离散状态方程、数值积分方法、仿真步长或多速率策略；也没有报告 fixed-point/float 数据格式、FPGA 映射、pipeline latency、并行计算资源或实时步长。论文所说的模块并联与逐个换模是功率模块的站级编排，不是计算并行；唯一明确的数字执行平台是 200 MHz DSP。[pdf:E08]

## § 6 — 核心数学推导（无形式化数学则跳过）

数学主线是“把两条对称次级支路化成一个等效 DAB，再用 rms current 和 energy efficiency 连接拓扑选择与参数优化”。

首先，模式只改变 secondary voltage 与 output voltage 的关系：

\[
M=\frac{V_{\text{out}}}{V_s},\qquad
M=
\begin{cases}
1,&\text{P-mode}\\
2,&\text{S-mode}
\end{cases}
\]

因此归一化增益为 \(k=V_{\text{out}}/(nV_{\text{in}}M)\)。在 SPS 下，作者把主、次级方波展开为奇次 Fourier harmonics，由每一谐波两端电压差除以 leakage/shim reactance 得到 \(i_L\)，再求 real power 与 rms current。关键结果为

\[
P_{\text{out}}
=\sum_{i=1,3,5,\ldots}
\frac{8nV_{\text{in}}V_{\text{out}}\sin(i\phi)}
{M(i\pi)^3 fL_{\text{shim}}},
\qquad
I_{\text{out}}=\frac{P_{\text{out}}}{V_{\text{out}}},
\]

\[
i_{L,\mathrm{rms}}
=\frac{2\sqrt{2}n^2}{\pi^2 fL_{\text{shim}}}
\sqrt{\sum_{i=1,3,5,\ldots}\frac{1}{i^4}
\left[
\left(\frac{V_{\text{out}}}{Mn}\right)^2+V_{\text{in}}^2
-2\frac{V_{\text{in}}V_{\text{out}}\cos(i\phi)}{Mn}
\right]}.
\]

它的物理含义是：对给定传输功率，\(k\) 离 1 越远，两端方波幅值越不匹配，电感中不做有用功的 rms current 越大。公式、变量定义与 conventional DAB current map 位于 PDF 物理页 4，Eq. (3)–(9)、Fig. 5–6。[pdf:E04]

其次，理想换模点要求被切入的 S-mode 比 P-mode 更接近 unity gain，即 \(1-k_S<k_P-1\)，从而得到

\[
V_{T,\mathrm{ideal}}=\frac{4}{3}nV_{\text{in}}.
\]

更精确的 \(V_{T,\mathrm{opt}}\) 令两模式的 \(i_{L,\mathrm{rms}}\) 相等：

\[
\frac{3V_{T,\mathrm{opt}}^2}{4n}
-V_{\text{in}}V_{T,\mathrm{opt}}
\left(2\cos\phi_P-\cos\phi_S\right)=0,
\]

\[
\phi_m=\frac{\pi}{2}
\left(
1-\sqrt{1-\frac{4MI_{\text{out}}fL_{\text{shim}}}{nV_{\text{in}}}}
\right),\quad m\in\{P,S\}.
\]

这里 \(V_{T,\mathrm{opt}}\) 不是固定的拓扑常数，而依赖 load、\(n\)、\(L_{\text{shim}}\)、\(f\)；这解释了 Fig. 8 的 transition boundary 为什么会随输出电流改变。推导与器件额定值换算见 PDF 物理页 4–5，Eq. (10)–(15)。[pdf:E04] [pdf:E05]

最后，作者没有按时间等间隔采样 profile，而先令每个样本代表相同能量：

\[
J_{\text{total}}=\int_0^{t_{\max}}V_{\text{out}}(t)I_{\text{out}}(t)\,dt,
\qquad q_j=\frac{J_{\text{total}}}{N_q}.
\]

每个能量区间内，\(q_v\) 和 \(q_i\) 分别以另一变量作为权重求平均；随后目标函数为

\[
\eta_{wt}
=\frac{1}{N_q\sum_{nb=1}^{N_b}W_{nb}}
\sum_{nb=1}^{N_b}\sum_{nq=1}^{N_q}\eta W_{nb},
\qquad
\eta=\frac{100P_{\text{out}}}{P_{\text{out}}+P_{\text{loss}}}.
\]

这使 GA 优化的是整个 session 交付能量的效率，而不是几个等时间样本的算术平均。量化定义见 PDF 物理页 6，Eq. (16)–(20)；weighted objective、参数边界和最优点见 PDF 物理页 7，Eq. (21) 与 Fig. 12。[pdf:E06] [pdf:E07]

## § 7 — 实验设计与结论

**问题 1：两种连接能否覆盖目标电压并保持次级对称？** → 作者在 \(V_{\text{in}}=800\text{ V}\) 下记录 200、400、600、800、1000 V 的 bridge voltage 与 inductor current waveforms；200/400 V 用 P-mode，600–1000 V 用 S-mode。→ 稳态波形显示各目标点可运行，S-mode 两个 secondary voltages 匹配；但论文没有展示正在带载时从 P 到 S 或从 S 到 P 的完整 transient waveform。Fig. 16–17 位于 PDF 物理页 9。[pdf:E09]

**问题 2：TPS 是否能改善高增益点？** → 在 1000 V、10 kW、\(k=5/4\) 下分别使用 SPS 与 TPS。→ 论文报告效率由 95.8% 提升到 97.9%，并观察到更低 magnetic volt-second stress；该数字及试验说明位于 PDF 物理页 8 的 Section IV-A，波形位于物理页 9 的 Fig. 17。[pdf:E08] [pdf:E09]

**问题 3：全电压范围的额定包络效率怎样？** → output voltage 以 100 V 步长从 200 V 扫到 1000 V，在 \(P_{\text{out}}\le10\text{ kW}\)、\(I_{\text{out}}\le36\text{ A}\) 包络上测量。→ 作者报告全范围效率高于约 95%；Fig. 18 还与文献 [13] 的 multilevel DAB 曲线比较，但并非同一实验平台的 head-to-head prototype test。设置和结论见 PDF 物理页 8，相邻 Fig. 18 位于物理页 9。[pdf:E08] [pdf:E09]

**问题 4：并联次级能否均流，且低载是否稳健？** → 在 400 V P-mode 下取 9.3、6.15、3.13、1.2 kW 四点测 dc current sharing，并在五个输出电压下从 \(1/4\) load 扫到 full load。→ Table IV 的 dc sharing error 随功率下降由 0.8% 增至 6.6%；正文另报 secondary ac winding maximum rms sharing error 为 3.2%。作者还报告最差至 \(1/4\) load、200 V 时，五条效率曲线的最大 variation 仍小于 6%。证据位于 PDF 物理页 9 的 Table IV、Section IV-B 与物理页 10 的 Fig. 19。[pdf:E09] [pdf:E10]

**问题 5：按充电过程累计的能量效率是否仍高？** → 原型运行 CP400 和 CP800 两条 profile。→ 两条曲线 peak efficiency 都约 98.4%；session weighted energy efficiency 分别为 97.9% 和 97.5%。最低效率在 profile 末端约 \(1/10\) rated load 仍高于 90.1%；作者推断多模块站可关掉部分模块、提高剩余模块负载率，因而避开该低效点，但没有整站实验。数值与 Fig. 20 位于 PDF 物理页 9–10。[pdf:E09] [pdf:E10]

实验边界必须保留：GA 设计时用了三条 profile，其中 CP600、CP800 是 generic；原型 energy-profile test 只展示 CP400、CP800。论文没有公开原始 charging-session 数据、loss LUT、GA seed/population/convergence settings、完整热状态、EMI、功率密度、长时可靠性、mode-switch lifetime、动态换模 transient 或 V2G 反向功率实验，也未报告 measurement uncertainty。因此“98% for three profiles”主要是设计模型结果，不能与两条原型 profile 的实测 weighted efficiency 混为一项证据。

## § 8 — Take-aways

**5 句话。** 这篇论文用同一磁芯的两组次级在低压并联、高压串联，把 fixed-bus DAB 的 200–1000 V 难题拆成两个较容易的增益区间。P/S mode 选择的直接目标是让工作点接近 unity gain，从而压低 circulating rms current 和器件 kVA。设计阶段先把 charging profile 量化为等能量 operating points，再用 GA 优化 transformer ratio 与 shim inductance。10 kW、800 V input、1 kV output capability 的 SiC prototype 在稳态电压扫点、均流和两条 profile 上给出了较高效率证据。最明显的缺口是没有验证带载动态换模、整站模块协同、真实电池与长期器件可靠性。

**3 句话。** 本文的核心不是单独的 mode switching 或单独的 GA，而是用 reconfigurable gain 扩大高效区、再用 energy-weighted objective 选择实际使用分布上的最优参数。原型结果支持静态宽范围可行性与高效率，但尚未闭合“ultrafast station 中可安全、连续、长期换模”的系统 claim。它是很强的 module-level engineering evidence，不是完整 charging-station certification。

**1 句话。** 用串/并联双次级把五倍电压范围折叠成两个接近 unity gain 的工作区，再按真实交付能量而非额定点去优化 DAB。[pdf:E03] [pdf:E06] [pdf:E10]

## § 9 — 最脆弱的假设

最脆弱的假设是：**P/S reconfiguration 可以在实际多模块充电站中安全、连续、低代价地执行，因而静态端点效率能够转化为整段充电的系统收益。** 这是核心贡献的门轴，因为没有可靠换模，converter 要么只能固定在一种连接而重新遭遇宽增益应力，要么在换模时造成 output interruption、过压/过流或额外损耗。

论文给出的正面证据是 Fig. 3 的 T-mode 状态机：换模时先 deactivate output 并把三个 mode switch 置零；作者进一步提出多模块逐个换模，使任意时刻还有模块给车辆供能。[pdf:E03] 但实验只展示各电压点的稳态波形和效率，没有展示带载换模时的 dc-bus/output transient、contactor/bidirectional-switch commutation、模块间 current redistribution、控制延迟、precharge、故障恢复或寿命循环。[pdf:E08] [pdf:E09] 因此这里的结论属于“论文机制加有限证据支持下仍未闭合的关键假设”，不是论文已经验证的事实。

## § 10 — 最小复现实验

一周内最值得复现的是“reconfigurable gain 是否确实在相同器件与相同功率下压低 rms current”，而不是从零复制 10 kW 高压硬件。

- **数据与参数：** 直接采用 Table III 的 \(V_{\text{in}}=800\text{ V}\)、\(f=100\text{ kHz}\)、\(n=0.5\)、每次级 \(L_{\text{shim}}=20\,\mu\text{H}\)、\(P_{\max}=10\text{ kW}\)、\(I_{\max}=36\text{ A}\)，在 200、400、600、800、1000 V 上取 paper 的 power-current envelope。[pdf:E08]
- **实现：** 在 PLECS、PSIM 或 MATLAB switching model 中建立 conventional single-secondary DAB 与 proposed dual-secondary P/S DAB；保持总 silicon rating、dead time、transformer ratio 和 modulation policy 一致。先复算 Eq. (5)–(13) 的 \(\phi\)、\(i_{L,\mathrm{rms}}\) 与 \(V_{T,\mathrm{ideal/opt}}\)，再用 switching waveform 交叉验证；低功率点另加入同一 TPS policy。[pdf:E04] [pdf:E05]
- **测量：** 每点记录 delivered power、primary/secondary rms current、peak current、ZVS 是否成立和估算 loss；同时做 secondary inductance ±5%、dead-time mismatch 和 mode-switch on-resistance sweep。
- **支持标准：** proposed selector 在大部分 200–1000 V grid 上的 rms current 和 total device VA 均低于同额定 conventional DAB，且参数扰动后优势不消失；Fig. 7–8 的低应力区和 transition boundary 能定性复现。
- **反驳标准：** 在公平 modulation 与器件额定下，rms current 优势只来自 TPS 或参数选择而不是 P/S topology；或者 ±5% mismatch、dead time 和 mode-switch parasitic 足以让应力超过 conventional baseline。

完整 GA 的严格复现一周内无法闭合，因为论文未报告原始 CP600/CP800 时间序列、component LUT、GA 配置与全部器件温度模型；因此不应以“我跑出了另一个 98%”冒充复现 Eq. (21) 的设计结果。

## § 11 — 最强反例设计

最强攻击不是再挑一个低效率点，而是做一套**等额定、等调制、包含真实换模代价的 matched baseline test**，检验优势究竟来自 topology，还是来自 SiC、TPS、magnetics 和有利参数共同作用。

具体做法是搭建 proposed DAB 与 conventional/NPC DAB 两个功率相同的模块，统一 semiconductor technology、总 silicon area、100 kHz、冷却边界、transformer temperature rise 和控制带宽；用同一批真实 400/800 V charging profiles 循环运行。对 proposed module 施加 secondary inductance drift、gate-delay mismatch 和 contactor latency，并在高电流、transition threshold 附近反复 P↔S；测量 output interruption、overshoot、branch current、ZVS loss、累计 delivered-energy efficiency 和 mode-switch cycle life。论文的静态均流证据已经显示误差会在低功率增大，说明 mismatch 是有机制依据的攻击方向。[pdf:E04] [pdf:E09]

如果把换模损耗、额外开关/contactor、热漂移与模块间 redistribution 纳入后，proposed design 的 energy efficiency、器件 VA 或可靠性不再优于 matched baseline，那么“宽范围高性能主要来自 P/S reconfiguration”的解释就被推翻；更合理的替代解释将是“优良 semiconductor、TPS 和针对测试点优化的 magnetics”贡献了大部分收益。反之，若在这些扰动下仍保持低应力、无中断且累计效率领先，核心机制才获得强于本文的证据。

## § 12 — Follow-up Research Idea

电力电子与 transportation electrification 领域通常把高影响研究建立在清楚的器件/拓扑机制、宽工况原型、可比较 baseline、热与保护边界、动态过程和可工程化价值上；只有 steady-state peak efficiency 不足以支撑站级影响。

基于第 9 节，候选方向是：**把“单模块稳态 energy-efficiency optimization”改写为“带 switching risk、thermal aging 与服务连续性约束的 station-level hybrid co-design”。** 它不是给本文再加一个 controller，而是改变优化对象：决策变量同时包括每个模块的 P/S state、transition timing、power sharing、允许的 temperature/aging budget 和车辆需求；目标从 \(\eta_{wt}\) 最大化改为单位交付能量的损耗、换模风险与寿命消耗的 Pareto frontier。

- **未满足需求：** 本文依赖多模块逐个换模来保持供电，却没有把其他模块在换模时增加的 current、效率与 aging 计入目标。[pdf:E03] [pdf:E10]
- **潜在研究价值：** 若能证明 station-level scheduling 会改变最优 transformer ratio、transition boundary 或模块数量，就把 topology design 与 charger fleet operation 真正连接起来，而非只改善一个控制环。
- **可借鉴方法：** hybrid systems 的 mode-dependent dynamics、reliability-aware model predictive control、chance constraints，以及 power-module digital twin 中的 junction-temperature/contactor-aging state。
- **首个证伪实验：** 三模块实验台运行重复的 400/800 V profiles，注入一只模块的 5% impedance drift 与随机 contactor delay；比较固定 \(V_T\)+轮流换模和 risk-aware scheduler。若 output interruption、累计损耗、peak junction temperature 与等效寿命都无显著改善，该方向的核心连接即被证伪。
- **与本文实质区别：** 本文把每个 quantized point 的静态 component loss 汇总为 \(\eta_{wt}\)；该方向把换模本身、模块耦合和随时间演化的健康状态纳入事实模型，研究单位从 converter operating point 变为 charging-station service trajectory。

由于本卡按输入边界没有另行检索 2023 年后的相关工作，这一方向只应标为**候选研究想法**，不声称 novelty。
