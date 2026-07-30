# Optimal Control of Semi-Dual Active Bridge DC/DC Converter With Wide Voltage Gain in a Fast-Charging Station With Battery Energy Storage

**作者**：Md Ahsanul Hoque Rafi；Jennifer Bauman  
**出处**：IEEE Transactions on Transportation Electrification, Vol. 8, No. 3, pp. 3164–3176  
**年份**：2022  
**DOI**：10.1109/TTE.2022.3170737  
**Zotero key**：JW323723  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文研究的是一个很具体的 fast-charging station 功率变换问题：当 stationary BESS 直接接在公共 dc bus 上、EV battery 又通过隔离型 dc/dc converter 充电时，BESS 与 EV 的 SOC 同时变化，会让 converter 的输入、输出电压都跨越很宽范围。最难的常见工况恰好是“BESS 满、EV 空”，也就是高输入电压、低输出电压；此时传统 phase-shift converter 往往有很高的环流、峰值电流和开关损耗。作者以 350–550 V 输入、150–450 V 输出的应用窗口为目标，并把“在不牺牲高输出电压工况效率的前提下，提高高输入/低输出工况效率”设为核心工程问题。[pdf:E01]（PDF 物理页 1，Abstract、Introduction 与 Fig. 1）

重要性不只在某一个 converter 的百分点。BESS 能缓冲 fast charger 对弱电网的冲击并降低 demand charge，但如果 BESS-to-EV 这一级在最常见的大压差工况损耗很高，储能架构的系统优势会被热设计、器件额定值和能源损失抵消。论文直接报告：10 kW 样机在 25 A constant-current 充电下，相对 dual phase shift（DPS）控制最高提高 3.5 个百分点，峰值效率达到 97.6%；这些数字说明优化对象不是轻载小信号，而是实际高功率能量通道。[pdf:E01]（PDF 物理页 1，Abstract）

## § 2 — 前人工作与不足

论文把相关路线分成几层。FB-LLC 可通过变频获得宽增益，但变频使磁性元件设计和多相 interleaving 复杂，元件容差还会造成各相增益不一致；传统 PSFB 固定频率、容易交错，但只能 buck，低变换比时 freewheeling 很长，环流和导通损耗上升，次级 diode 还承受反向恢复或 ringing。DAB 用全控整流换来双向与宽控制自由度，但 DCFC 的这一级只需单向功率，semi-DAB 因少两个次级 active switch 与 gate driver 而更合适，同时仍保留 buck/boost 能力。[pdf:E02]（PDF 物理页 2，Introduction 与 Fig. 2）

对 semi-DAB 本身，已有工作包括：以 peak current 为目标的 optimal DPS、面向轻载的 variable-frequency 或 multimode control、minimum-current-stress hybrid control，以及扩展 ZVS 区间的方法。作者指出这些工作要么主要改善轻载，要么增益范围有限，要么没有与 DPS 做直接效率比较；而宽电压变化又意味着 ZVS 不能处处保持。因而真正的缺口不是“没有 phase-shift control”，而是缺少一种能在高负载、宽输入/输出范围内在线选择 bridge structure 和 phase shift、并在目标工况用 DPS 作公平基线的控制法。[pdf:E02]（PDF 物理页 2，Introduction 相关工作段）

## § 3 — 重建作者的思考路径

以下是基于论文背景与失效模式的重建，不是作者逐字给出的研发日志。第一步，从 DCFC+BESS 架构出发，可发现 converter 的困难不是单一输入扰动，而是两个 battery voltage 独立变化；设计必须同时覆盖 high-step-down 和接近 unity gain。第二步，从 PSFB/DPS 的损耗机制看，高输入/低输出时，full bridge 在 clamped inductor 上施加的电压过大，电流每个 switching interval 都被推到较高峰值；即使能 soft turn-on，turn-off current 与 RMS current 仍会制造损耗。第三步，semi-DAB 已经有 dc-blocking capacitor 和不对称的次级有源/二极管结构，因此可以问：是否不改功率器件，只重排 primary bridge 的开关状态，就让 inductor 实际看到约一半输入电压？第四步，一旦 half bridge 可用，问题就从“连续调一个 phase shift”变成“在 half/full bridge 和三类 buck/boost conduction mode 之间做离散选择”；这要求先把 load-dependent mode boundary 和每种 mode 的 phase/duty 解析出来，再在线比较 peak current，而不是离线穷举控制轨迹。[pdf:E03]（PDF 物理页 3，Introduction 末段与 Section II 开头）

这条路径的关键约束也很清楚：不能只在轻载改善，不能丢掉高输出电压能力，不能让在线优化变成高维搜索，还必须保留闭环修正和结构切换的可执行性。RBOC 因此可以理解为“解析模式分类 + bridge reconfiguration + 小范围闭环微调”的组合，而不是一个单独的新 PWM 波形。

## § 4 — 核心 Intuition

RBOC 的核心是：在高输入、低输出时，把 primary 从 full bridge 重构为 half bridge，让 clamped inductor 看到的有效输入电压减半，于是电流上升斜率、peak current、turn-off loss 和 RMS conduction loss 一起下降。需要更高增益时则回到 full bridge，避免 half bridge 为获得同样输出而要求过大的 phase shift。控制器不遍历所有开关组合，而是先按 gain 与 load 判断三类 mode，再在候选 bridge 之间比较解析估算的 peak current。[pdf:E03]（PDF 物理页 3，RBOC 贡献、Eqs. (1)–(2)）

## § 5 — 具体方法与完整 Pipeline

以 `Vin=500 V、Vout=200 V、Iout=25 A` 的 charging point 为例，完整 pipeline 如下。

1. **读取 operating point。** EV 向控制器提供 measured `Vout`、`Iout`、`Iref`、`Vref` 以及 CC/CV mode；BESS 侧提供 `Vin`。论文把 full-bridge gain 定义为 \(M_{\mathrm{full}}=nV_{\mathrm{out}}/V_{\mathrm{in}}\)，half-bridge gain 定义为 \(M_{\mathrm{half}}=2nV_{\mathrm{out}}/V_{\mathrm{in}}\)，其中 \(n\) 是 transformer turns ratio。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(2)）
2. **识别 load-dependent mode。** 在 \(M'<1\) 时，converter 可能是 Type 1 buck，也可能因 duty-cycle loss 进入 Type 2 boost；在 \(M'>1\) 时是 Type 3 boost。Type 1 full bridge 使用 internal 与 external phase shift，Type 2/3 主要使用 SPS；half bridge 失去 internal phase-shift 自由度，Type 1 改以 `S1/S2` duty cycle 调节。[pdf:E04]（PDF 物理页 4，Figs. 4–5 与 Eqs. (3)–(7)）[pdf:E05]（PDF 物理页 5，Figs. 6–8 与 Eqs. (8)–(11)）[pdf:E06]（PDF 物理页 6，Type 2 与 Eqs. (12)–(17)）[pdf:E07]（PDF 物理页 7，Type 3 与 Eqs. (18)–(22)）
3. **选择 bridge structure。** 控制器先计算 buck/boost boundary \(M_b\)。若 half/full 两个 gain 都小于 1，就比较它们与 \(M_b\) 的关系；只有候选分别落在不同 mode 时才计算两种结构的 peak current。若 \(M_{\mathrm{half}}>1>M_{\mathrm{full}}\)，还要判断 half-bridge Type 3 是 CCM 还是 DCM，并受预设的 \(D_{\mathrm{boost\_max}}\) 限制；若两个 gain 都大于 1，则选 full bridge，因为所需 phase shift 更小。Fig. 13 给出了完整决策树。[pdf:E08]（PDF 物理页 8，Fig. 13 与 Eqs. (23)–(29)）
4. **生成 feedforward phase/duty。** 对所选 mode，RBOC block 用对应解析式估计 `D`、`D1`、`D2` 或 `Dc`；这些量直接进入 PWM path，而不是再对全部 phase-shift 组合做在线搜索。[pdf:E08]（PDF 物理页 8，Fig. 13 与 Eqs. (23)–(29)）
5. **闭环微调。** Duty-cycle and phase-shift adjustment（DPA）block 用 CC 或 CV PI controller 只修正该 mode 真正需要的量；其余 duty/phase 通道输出零。PWM generator 最终产生 `S1–S6` gate signals。结构切换时 PI 被 reset，RBOC 以小步改变 phase shift，切换完成后再启用相应 PI。[pdf:E09]（PDF 物理页 9，Fig. 16、Table I 与 closed-loop control 正文）
6. **输出物理效果。** 论文给出的解释是：在 200 V output、1.3:1 turns ratio 时，half-bridge RBOC 的 inductor current 上升阶段只有 15 V，而 full-bridge DPS 是 290 V；因此 RBOC 的 peak current 明显更低。到输出电压升高、两条效率曲线相交时，RBOC 直接采用 DPS，不强行维持 half bridge。[pdf:E09]（PDF 物理页 9，Fig. 15 及其下方正文）

从 EMT/FPGA 复现角度看，论文给出了 switch-level 分段等效电路、事件时刻 \(t_0\ldots t_5\)、100 kHz switching hardware 和 phase/duty 解析关系，但**未报告** EMT solver、数值积分形式、controller sampling period、multirate 调度、计算延迟、并行依赖图、fixed/floating-point 表示、量化位宽或 FPGA mapping。实验照片只标出 microcontroller，未给出型号、firmware 执行时间、资源占用或 HIL 平台；simulation 使用 PLECS/MATLAB。[pdf:E10]（PDF 物理页 10，Table II、Fig. 17 与 Section IV）

回到开头的 500/200 V、25 A 示例，Table III 显示 controller 最终选择 half bridge、Type 3 boost；估计的 external phase-shift duty 为 0.17，simulation 为 0.14，experiment 为 0.15。这说明解析 feedforward 把工作点送到正确 mode 和相近 phase，DPA 再负责小范围闭环修正。[pdf:E11]（PDF 物理页 11，Table III）

## § 6 — 核心数学推导（无形式化数学则跳过）

数学主线不是对完整 nonlinear converter 求全局最优，而是先用每个 switching stage 的 inductor volt-second balance 得到 mode-specific phase/duty，再把 peak current 当成结构选择目标。

**1. Gain 归一化。** Full bridge 时

\[
M_{\mathrm{full}}=\frac{nV_{\mathrm{out}}}{V_{\mathrm{in}}},
\]

half bridge 因 transformer terminal 只看到 \(V_{\mathrm{in}}/2\)，故

\[
M_{\mathrm{half}}=\frac{nV_{\mathrm{out}}}{V_{\mathrm{in}}/2}
=\frac{2nV_{\mathrm{out}}}{V_{\mathrm{in}}}.
\]

同一物理 operating point 在 half bridge 下的归一化 gain 是 full bridge 的两倍，这就是“改结构等价于改控制难度”的数学来源。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(2)）

**2. Type 1 full-bridge buck。** 在电流绝对值上升和回落的两个 stage，clamped-inductor voltage 分别为

\[
v_{L_c}=-V_{\mathrm{in}}+nV_{\mathrm{out}}, \qquad
v_{L_c}=nV_{\mathrm{out}}.
\]

令 \(D_1\) 为 primary internal phase-shift duty、\(D_2\) 为 primary-to-secondary external phase-shift duty，对半个 switching period 做 volt-second balance：

\[
(-V_{\mathrm{in}}+nV_{\mathrm{out}})(1-D_1)\frac{T_s}{2}
+nV_{\mathrm{out}}D_2\frac{T_s}{2}=0,
\]

于是

\[
M'=\frac{nV_{\mathrm{out}}}{V_{\mathrm{in}}}
=\frac{1-D_1}{1-D_1+D_2}.
\]

ZCS 的工程含义是：secondary switch 必须等到 \(i_{L_c}\) 过零后再 turn on，所以 \(D_2\) 不是任意自由度，而是有下界。[pdf:E04]（PDF 物理页 4，Fig. 4 与 Eqs. (3)–(7)）

当 Type 1 处于 DCM，论文把它映射为 nonisolated buck DCM，定义

\[
K=\frac{2L_c}{n^2R_{\mathrm{load}}(T_s/2)},
\qquad
M'=\frac{2}{1+\sqrt{1+4K/(1-D_1)^2}},
\]

并得到

\[
D_1=1-\sqrt{\frac{4K}{(2/M'-1)^2-1}},
\qquad
D_2=\left(\frac{1}{M'}-1\right)(1-D_1).
\]

这一步把 voltage、load、inductance 和 switching period 直接变成 feedforward phase-shift estimate。[pdf:E05]（PDF 物理页 5，Eqs. (8)–(9)）

**3. Type 1 half-bridge buck。** 由于 dc-blocking capacitor 把 transformer terminal 的平均电压约束为零，`S1` 与 `S2` 使用相同 duty、相差半个周期；两个有功 stage 的 inductor voltage 是

\[
v_{L_c}=\frac{V_{\mathrm{in}}}{2}-nV_{\mathrm{out}},
\qquad
v_{L_c}=-\frac{V_{\mathrm{in}}}{2}-nV_{\mathrm{out}}.
\]

用上升、下降时间 \(D_cT_s\) 与 \(D_{ci}T_s\) 写出 peak current，再用

\[
M'=\frac{nV_{\mathrm{out}}}{V_{\mathrm{in}}/2}
=\frac{D_c-D_{ci}}{D_c+D_{ci}},
\qquad
I_0=ni_{\mathrm{peak}}(D_c+D_{ci})
\]

即可联立求所需 duty。[pdf:E05]（PDF 物理页 5，Eqs. (10)–(11)）[pdf:E06]（PDF 物理页 6，Eqs. (12)–(15)）

**4. Type 2/3 boost。** Type 2 即使 \(M'<1\) 也可能因 CCM duty-cycle loss 进入 boost，此时 primary 两个 leg 同相，只调 secondary external phase shift；论文由三个 stage 的 \(v_{L_c}=V_{\mathrm{in}}+nV_{\mathrm{out}}, V_{\mathrm{in}}, V_{\mathrm{in}}-nV_{\mathrm{out}}\) 联立 peak current、gain 与 average output current。Type 3 的 \(M'>1\) boost 仍使用 SPS，但 peak current 的发生时刻改变；DCM 下外移相可由 Eq. (22) 直接求得。[pdf:E06]（PDF 物理页 6，Eqs. (16)–(17)）[pdf:E07]（PDF 物理页 7，Eqs. (18)–(22)）

**5. 在线结构选择。** Buck/boost boundary 由

\[
M_b^2+aM_b-1=0,\qquad
a=\frac{4L_c}{n^2R_{\mathrm{out}}(T_s/2)}
\]

给出。控制器再用 Eqs. (25)–(29) 比较 half/full bridge 的 \(i_{\mathrm{peak}}\)，并检查 CCM/DCM boundary。这里的“optimal”是**在论文限定的 mode、phase-shift 上限和 peak-current surrogate 下的离散最优选择**，不是对所有器件损耗、参数不确定性和动态性能的全局最优证明。[pdf:E08]（PDF 物理页 8，Fig. 13 与 Eqs. (23)–(29)）

推导边界必须保留：论文明确说明这些解析式忽略 dead time 与 dc-blocking capacitor value 的影响，只声称它们足以近似定位 mode 和 phase/duty；\(D_{\mathrm{boost\_max}}\) 的具体取值、选择依据也未报告。[pdf:E03]（PDF 物理页 3，Section II 引言末段）

## § 7 — 实验设计与结论

**问题 1：解析控制器能否在宽电压点估出正确 mode 与 phase/duty？**  
**实验**：作者在 PLECS/MATLAB 与 10 kW hardware 上比较三个代表点。样机参数为：350–550 V 输入、150–450 V 输出、25 A 最大输出、10 kW 最大功率、100 kHz switching frequency、13:10 transformer ratio、6 µH transformer leakage inductance、2 µF dc-blocking capacitor；主/次级 active half bridge 用 CAB011M12FM3，四只次级 diode 用 C4D40120D。[pdf:E10]（PDF 物理页 10，Table II 与 Fig. 17）  
**答案**：Table III 中，450/150 V Type 2 half bridge 的估计/仿真/实验 external duty 是 0.14/0.11/0.13，peak current 是 31/29/28 A；500/200 V Type 3 half bridge 对应 0.17/0.14/0.15 与 26/25/29 A；550/275 V Type 1 full bridge 的估计/仿真/实验 peak current 是 63/64/64 A。结果支持解析式能把 controller 带到正确邻域，PI 只需微调，但论文没有报告跨全工作域的误差分布或最坏误差。[pdf:E11]（PDF 物理页 11，Table III）

**问题 2：降低 peak current 的物理机制是否出现在真实波形中？**  
**实验**：Fig. 18 在 450/150 V 比较 RBOC half bridge 与 DPS full bridge；Figs. 19–20 再覆盖 500/200 V Type 3 和 550/275 V Type 1。  
**答案**：450/150 V 下，RBOC 波形显示 ZVS，DPS 的 peak current 超过 RBOC 的两倍，因此 primary switches 的 turn-off current 也超过两倍；另外两个点分别显示 Type 3 的 secondary turn-off peak 与 Type 1 DCM/ZCS 行为。[pdf:E11]（PDF 物理页 11，Figs. 18–20 及下方正文）

**问题 3：较低 peak current 是否转化为 converter efficiency？**  
**实验**：在 25 A CC mode 下，以 DPS 为基线，对 `Vin=450/500/550 V` 测量多组输出电压；输入功率由 Sorensen SGX-600V-25 A dc source 测得，输出侧为三台并联 Chroma 63800 series ac+dc load。  
**答案**：在 200 V 输出时，500 V 和 550 V 输入下分别约提高 3 与 3.5 个百分点；最大改善点为 550/200 V，RBOC 为 97.6%，DPS 为 94%。在 450/500/550 V 输入下，RBOC 分别从 200/250/275 V 输出起采用 DPS，所以高输出区不再声称优于 DPS，而是与其相同。[pdf:E12]（PDF 物理页 12，Fig. 21 与 Efficiency 正文）

**问题 4：half/full bridge 离散切换和负载变化是否会导致明显失控？**  
**实验**：Fig. 22 展示 half-bridge Type 3 到 full-bridge Type 1 的结构切换；phase shift 每 2 ms 改 10°，总切换约 26 ms。Fig. 23 在 CV mode 做 50% load transition，正文描述 current 从 15 A 变到约 6 A。  
**答案**：示波器波形支持切换可执行，且 output-voltage trace 未显示肉眼可见的大幅失控；但论文没有给 voltage overshoot、settling time、THD、EMI、thermal transient 或 repeated-transition endurance 的数值指标，因此不能把该图外推为完整动态稳定性证明。[pdf:E12]（PDF 物理页 12，Figs. 22–23 与 Dynamic Behavior）

**问题 5：作者的最终 claim 到哪里为止？**  
论文结论把证据限定为：25 A rated、400 V 时 10 kW 的样机，在所测宽输入/输出点相对 DPS 最高提高 3.5 个百分点、峰值效率 97.6%，并能在线识别 mode、给出 phase/duty 而无须搜索整个控制空间。未来工作仍是 parameter selection；论文未给 aging、battery ripple、bidirectional power、fault operation、多相 interleaving、不同器件平台或车规环境验证。[pdf:E13]（PDF 物理页 13，Conclusion）

## § 8 — Take-aways

**5 句话**

1. Semi-DAB 在 BESS-fed DCFC 中的核心难点是同时覆盖 high-input/low-output 与接近 unity-gain 工况，而不是只把 phase shift 调得更精细。
2. RBOC 通过 half/full bridge reconfiguration 改变 inductor 看到的有效输入电压，再以 peak current 作为 mode-selection 指标。
3. 解析 mode boundary 使 controller 能在线估计 phase/duty，闭环 PI 只负责小修正。
4. 10 kW、25 A 样机支持其在高输入/低输出区相对 DPS 最高提高 3.5 个百分点，并在高输出区回退为同一 DPS 行为。[pdf:E12]（PDF 物理页 12，Fig. 21）
5. 证据仍局限于稀疏 operating points、单一 hardware 和未包含 dead time/Cdc 影响的解析模型，不能直接等同于全域 loss-optimal 或 robust-optimal。

**3 句话**

RBOC 的真正贡献是把宽增益 semi-DAB 控制重写成一个可解析的 hybrid mode-selection 问题。它在目标工况用结构重构显著降低 peak current，并用硬件效率证明这个机制有工程价值。它最需要后续补强的是 loss model、parameter uncertainty 和 bridge-transition 的定量鲁棒性。

**1 句话**

用 bridge reconfiguration 先改变“电流为什么会变大”，再用 phase shift 微调“电流需要多大”，比始终在 full bridge 上优化 DPS 更有效。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**在所有候选 mode 中，最小 clamped-inductor peak current 足以可靠指示最高总效率。** 这是 RBOC 决策树的根基；论文的理由是 semi-DAB 可实现 ZVS/ZCS turn-on，主要损耗因而来自 high-current turn-off，而 peak current 降低通常也会降低 RMS conduction loss。[pdf:E07]（PDF 物理页 7，Section III-A）

这个假设可能在真实硬件中失效，因为 total loss 还受 switching-node capacitance、diode reverse recovery、dead time、transformer/core/copper loss、dc-blocking capacitor ripple、gate timing、temperature 与器件离散性影响。Half bridge 即使 peak current 更低，也可能因 conduction path、soft-switching margin 或磁通偏置付出额外损耗；接近 mode boundary 时，解析参数误差还可能让 controller 选错结构。论文给出的效率曲线确实支持三个输入电压下的目标区间，却没有 loss breakdown、温度扫描、元件容差扫描或全二维 operating map；推导还主动忽略 dead time 和 Cdc value。因此这是“被当前样机支持的工程近似”，不是已证明普适的 efficiency theorem。[pdf:E03]（PDF 物理页 3，推导假设）[pdf:E12]（PDF 物理页 12，Fig. 21）

## § 10 — 最小复现实验

一周内最有价值的复现不是先造 10 kW 样机，而是在 PLECS/MATLAB 建一个 switch-level semi-DAB，验证“mode 解析 + peak-current mechanism”。

1. 按 Table II 设置 `Vin=350–550 V`、`Vout=150–450 V`、`Iout=25 A`、`fs=100 kHz`、`n=13:10`、`Lc=6 µH`、`Cdc=2 µF`；实现 full-bridge DPS、half-bridge SPS/duty control 和 Fig. 13 的 RBOC decision tree。[pdf:E08]（PDF 物理页 8，Fig. 13）[pdf:E10]（PDF 物理页 10，Table II）
2. 先跑 Table III 的 450/150、500/200、550/275 V 三点，记录 mode、`D/D1/D2`、transferred power、\(i_{L_c,\mathrm{peak}}\) 和 RMS current。作为本复现实验的预注册判据，可要求 peak current 距论文 experiment 不超过 10%，duty 不超过 0.02；这是复现者设定的验收阈值，不是论文原有 claim。
3. 再锁定 550/200 V，对 RBOC half bridge 与 DPS full bridge 施加相同 power command，检查 current-rise stage 的 inductor voltage 是否复现约 15 V 对 290 V，并验证 RBOC peak/RMS current 均下降。[pdf:E09]（PDF 物理页 9，Fig. 15 下方正文）
4. 最后加入一组最小 nonideality sensitivity：dead time、switch on-resistance 和 output capacitance 各做低/中/高三级。若 RBOC 在相同 power、voltage 与 switching frequency 下不能稳定降低 peak current，或 realistic loss model 显示 DPS 总损耗更低，则核心机制被反驳；若 peak-current 优势稳定而 total-loss 优势随参数变化，则说明应保留物理机制、否定“peak current 等价于 loss optimum”的强版本。

论文未报告 PI gains、controller sampling、\(D_{\mathrm{boost\_max}}\) 数值与完整 PLECS model，因此该复现能验证 feedforward/mode-selection claim，却不能声称 bit-exact 重现作者 firmware。

## § 11 — 最强反例设计

最强反例不是再找一个效率稍低的点，而是构造一个**peak-current 最小与 total-loss 最小发生分离**的工作域。做法是围绕 half/full bridge boundary 建立二维 `Vin–Vout` 密集扫描，并在每一点对所有合法 half/full、Type 1–3、SPS/DPS 候选做受约束穷举；约束相同 output power、switching frequency、device SOA 与 output ripple，同时用经过 double-pulse 和 calorimetric measurement 标定的 device/transformer loss model 计算总损耗。

随后改变 junction temperature、dead time、\(L_c\)、Cdc、transformer parasitic 和 diode recovery。若存在一个连续且工程常见的区域，使 RBOC 选择的结构拥有最低 \(i_{\mathrm{peak}}\)，但另一个候选因更好的 ZVS margin、更少的 diode loss 或更低 magnetic loss 而持续拥有更高效率，那么论文的 mode-selection objective 就被直接推翻，而不只是“样机还能优化”。更强的 hardware 版本是在 mode boundary 上做 repeated bidirectional voltage sweep：如果参数漂移导致 bridge chatter、热振荡或效率迟滞，而论文的解析 controller 无法观察这些状态，则其“任何 operating point 在线确定最优控制”的表述必须收缩为特定静态参数下的近似最优。

## § 12 — Follow-up Research Idea

**候选方向：从 peak-current RBOC 改写为 uncertainty-aware hybrid loss control，并对 bridge transition 给出可证伪的安全包络。** 由于这里只按输入 PDF 阅读、没有补充检索相关工作，以下不声称 novelty。

**（a）未满足需求。** Fast charger 需要在 aging、temperature、battery ripple 与元件容差下持续高效，而不只是 nominal parameter 下选到较小 peak current；同时 bridge transition 不能依赖肉眼看似平滑的单次波形。

**（b）研究价值。** 电力电子领域通常重视明确损耗机制、可实现 controller、宽工况 hardware map、dynamic transition 与可复现的 thermal/electrical validation。若能同时给出效率增益、soft-switching margin、SOA 和 transition bound，就把问题从“更好的 phase-shift rule”提升为“带不确定性的 hybrid power-converter operation envelope”。

**（c）相邻方法。** 可借鉴 hybrid systems 的 guard-set/invariant-set 分析、robust model predictive control，以及 set-membership online identification。Controller 不再把 \(i_{\mathrm{peak}}\) 当唯一 objective，而是在线更新少量可辨识 loss parameters，并只在被验证安全的 guard set 内切换 half/full bridge；复杂 loss estimation 可低频运行，100 kHz PWM 仍由解析 feedforward 执行。

**（d）第一个证伪实验。** 在同一 10 kW platform 上预注册 100 个跨 `Vin–Vout–temperature–load` 点和 1000 次 boundary transition，对比原 RBOC 与新 controller。若新方法不能在不增加过压/过流与 transition time 的条件下显著降低 energy loss，或在线辨识误差使 guard-set violation 超出预设上限，就淘汰该方向。

**（e）与本文的实质区别。** 本文优化的是 nominal mode 下的 clamped-inductor peak current，并用 PI 做局部修正；候选方向优化的是带参数不确定性的 measured total loss 与 transition safety，其状态、目标函数和验收对象都改变了，而不是简单增加一个控制模块。最直接的起点是把论文已经承认未纳入的 dead time、Cdc 与 parameter selection 纳入可辨识模型，再检查“最小 peak current”何时仍是正确 surrogate、何时必须被替换。[pdf:E13]（PDF 物理页 13，Conclusion 与 future work）
