# Sinusoidal Phase Shift Modulation for V2H Operational Mode in Current-Fed Bidirectional Onboard Charger

**作者：** Manish Kumar；Sumit Kumar Pramanick；Bijaya Ketan Panigrahi  
**出处：** IEEE Transactions on Transportation Electrification，Vol. 10，No. 2  
**年份：** 2023（在线发表；源 PDF 的当前卷期版本为 2024 年 6 月）  
**DOI：** 10.1109/TTE.2023.3298819  
**Zotero key：** 8RWZG7SG  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是一般意义上的“逆变器如何输出正弦电压”，而是一个受拓扑约束的具体问题：怎样让一台单级、隔离、current-fed、无大容量电解电容的双向车载充电器，在电网掉电后把车载电池变成住宅备用电源，并同时保持 230 V 级正弦输出、G2V/V2H 模式切换和软开关。作者使用的功率级是 L-L 型单级 converter：电池侧为 voltage-fed full bridge（VFFB），住宅交流侧为 current-fed half bridge（CFHB），二者由 high-frequency transformer（HFT）隔离；直流侧只保留用于滤除开关纹波的小 film capacitor，让二倍工频的 sinusoidal ripple current（SRC）进入电池。[pdf:E01]（PDF 物理页 1，Abstract、Introduction）

工程矛盾在于，传统两级 OBC 容易分别完成 PFC 与隔离 dc-dc 控制，却需要两次功率变换和吸收二倍频能量的大电解电容；这增加损耗、体积和故障敏感性。单级拓扑能减少中间环节，但 V2H 要求输出交流电压在每个 50 Hz 周期内连续改变，而相移功率级原本更擅长调节常值直流量。论文因此把研究问题收紧为：能否把“相移角本来就应随正弦输出而变化”这一规律直接写进 PWM pulse generation，使外层只需一个简单的同步旋转坐标系 PI 控制器。[pdf:E02]（PDF 物理页 2，Introduction 末段与贡献 1–4）

如果这一机制成立，价值有三层。第一，停电时 OBC 可以直接承担 V2H 住宅供电，不再只是给电池充电。第二，SRC charging/discharging 允许显著减小 dc-link capacitance，改善功率密度与电解电容寿命瓶颈。第三，若交流侧 ZCS 与直流侧 turn-on ZVS 确实覆盖整个输出周期和负载范围，100 kHz 级隔离变换的开关损耗就可被压低。论文在 1.5 kW 原型上验证了这些功能，但没有给出整机功率密度、长期电池老化或极端工况可靠性数据，因此这些更高层价值仍不能由本文单独确认。[pdf:E01]（PDF 物理页 1，Abstract）

## § 2 — 前人工作与不足

论文把 prior work 分成三条路线。第一条是两级 OBC：active front-end 完成 PFC，隔离 dc-dc stage 完成电池侧变换，中间大电解电容吸收二倍频功率。这条路线控制清楚，但有双功率级、器件数和 dc-link capacitor 可靠性代价。[pdf:E01]（PDF 物理页 1，Introduction）

第二条是既有单级 bidirectional OBC。[16]、[17] 支持双向功率流和软开关，但要联合调节 switching frequency、duty ratio 与 phase shift，控制自由度多；[18] 支持 V2H，却增加 unfolding bridge 和 resonant tank；[19] 使用 interleaved totem-pole 与 SRC charging，但需要额外 clamping capacitor 抑制 HFT leakage-inductance 引起的开关节点尖峰。作者没有说这些方案不能工作，而是把代价准确地放在额外功率器件、passive components 或 multi-variable control 上。[pdf:E02]（PDF 物理页 2，Introduction 的 [16]–[19] 对比）

第三条是与本文功率级最接近的工作。[23] 已提出 L-L 型单级 isolated current-fed half-bridge converter，并利用 active current commutation 自然钳位交流侧 switch-node voltage；但它没有研究 V2H 所需的输出交流电压控制。[24] 又在同一类 converter 的 G2V 模式中降低 HFT circulating current，仍没有解决 V2H 下相移角必须随交流周期变化的问题。[pdf:E02]（PDF 物理页 2，Introduction 末段）

所以作者针对的缺口很具体：不是再发明一套功率级，而是在已有 L-L current-fed hardware 上，为 V2H 引入一种把 rectified-sinusoidal phase shift 内生到 pulse generator 的调制，并用实验回答它能否同时实现电压调节、模式切换和软开关。论文没有系统检索 2023 年之后的相关方案，本卡也依协议没有联网补充文献，因此这里不能把该缺口外推成当前仍成立的 novelty 判断。

## § 3 — 重建作者的思考路径

以下是基于论文前置事实的逆向重建，不是作者逐字陈述。

第一步，从已存在的 L-L current-fed topology 出发。该拓扑已经具有隔离、双向功率流、交流侧有源换流钳位和 SRC charging 的基础，因此没有必要重做 power stage；真正缺的是 V2H control。[pdf:E02]（PDF 物理页 2，关于 [23]、[24] 的讨论）

第二步，把 V2H 输出看成一串很短的 switching intervals。100 kHz switching period 远短于 50 Hz 输出周期，所以在第 \(k\) 个 interval 内，期望交流电压 \(v_l^{(k)}\) 可以近似为常值；下一 interval 再更新这个常值。这样，直流相移功率级的局部分析仍可复用，只是所需 effective duty 随 \(|\sin(\omega t)|\) 缓慢变化。[pdf:E03]（PDF 物理页 3，Section III-A 开头、Fig. 2）

第三步，识别 conventional phase-shift PI 的结构性失配。若 PI 直接输出两个 carrier 之间的相移，它面对的是一个随 50 Hz 周期变化的 rectified-sinusoidal steady-state command，而不是常值工作点；作者据此认为普通 PI 无法做到零稳态误差。[pdf:E04]（PDF 物理页 4，Eq. (2) 后的 conventional pulse-generation 讨论）

第四步，不让 PI 追逐整条正弦，而让 pulse generator 本身产生这条形状：用两条相差 \(180^\circ\) 的 triangular carriers、一个 rectified-sinusoidal reference、SR latches 与极性逻辑合成两侧 gate pulses。外层 PI 只修正输出幅值误差，换流顺序仍由固定逻辑保证。[pdf:E04]（PDF 物理页 4，Fig. 3、Eq. (3)–(7)）

第五步，再检查这套逻辑是否保留原拓扑的软开关机制。作者把半个 switching interval 分成四个 stage，逐段写出 HFT leakage current、boost-inductor current 与 switch current，利用电流自然过零实现交流侧 ZCS，并利用 HFT current 给 device output capacitance 充放电来实现直流侧 ZVS turn-on。[pdf:E05]（PDF 物理页 5，Fig. 4、Stage 1–4）

## § 4 — 核心 Intuition

V2H 所需的 phase shift 不是一个要由 PI 从零“学会”的任意波形，而是由目标交流电压决定的 rectified sine。作者把这条 sine shape 固化进 carrier comparison 与 latch logic，让 PI 只管输出电压幅值。功率级的电流换向再为交流侧 turn-off 提供 ZCS、为直流侧 turn-on 提供 ZVS，因此同一调制同时服务于波形生成和开关损耗控制。[pdf:E04]（PDF 物理页 4，Eq. (2)–(7)、Fig. 3）

## § 5 — 具体方法与完整 Pipeline

以“电网掉电后，345 V 车载电池给 230 V、1.5 kW 住宅负载供电”为例，完整 pipeline 如下。

1. **功率级与能量路径。** 电池通过 VFFB、外串联电感 \(L_s\)、HFT 和交流侧 CFHB 向负载送能。CFHB 的两条 current-fed legs 各串一个 boost inductor \(L_1,L_2\)；交流侧 \(C_{ac}\) 滤除 switching ripple，电池侧 \(C_{bat}\) 只滤高频纹波而允许 SRC。[pdf:E02]（PDF 物理页 2，Fig. 1、Table I）
2. **掉电检测与 mode selection。** SOGI-PLL 连续估计 grid-voltage d-axis component \(v_g^d\)。当它低于 \(0.45\) p.u. 时，comparator 报告 grid outage，mode selector 从 G2V 切到 V2H；论文说该 threshold 用于避免间歇 sag 引起 false detection。[pdf:E06]（PDF 物理页 6，Fig. 5 与 Section III-C）
3. **输出电压控制。** 微控制器内部生成正弦参考及其相位 \(\theta_l\)，把实测 \(v_l\) 经 SOGI 和 \(\alpha\beta\)-to-\(dq\) 变换得到 \(v_l^d,v_l^q\)。在同步坐标系中 \(v_l^q=0\)，PI 只调节 \(v_l^d\) 到 \(v_l^{d*}\)，再把 control signal 变回 \(\alpha\beta\) frame 交给 PWM generator。[pdf:E06]（PDF 物理页 6，Fig. 5、Section III-C）
4. **sinusoidal phase-shift pulse generation。** 两条 triangular carriers 相差 \(180^\circ\)，rectified-sinusoidal reference 与它们比较；一个 50% duty 的 control signal \(C\) 标识 carrier slope，两个 SR latches 生成 \(S_{AT}/S_{AB}\) 和 \(S_{BT}/S_{BB}\)。再根据输出半周极性，把对应 dc-side pulse 与 \(S_{1ag},S_{2ag},S_{1bg},S_{2bg}\) 同步。[pdf:E03]（PDF 物理页 3，Fig. 2 与 V2H switching description）[pdf:E04]（PDF 物理页 4，Fig. 3、Eq. (3)–(7)）
5. **一个 switching interval 内的事件序列。** 半个 interval 分为四段：Stage 1 中 \(S_{AT},S_{BB}\) 导通，HFT current 与 boost-inductor current 建立；Stage 2 由 \(S_{BB}\) turn-off 触发 device capacitance 换流并把 dc-side HFT voltage 钳到零；Stage 3 换到 \(-V_{bat}\)，HFT current 下降到零；Stage 4 反向建立 current，同时交流侧目标 switch current 下降到零，实现 ZCS。另半个 interval 对称重复。[pdf:E05]（PDF 物理页 5，Fig. 4、Eq. (8)–(20)）[pdf:E06]（PDF 物理页 6，Eq. (21) 后的 half-cycle symmetry）
6. **硬件参数与执行平台。** 原型额定 1.5 kW、\(V_g=230\ \mathrm{V_{rms}}\)、\(f_g=50\ \mathrm{Hz}\)、\(V_{bat}=300\text{–}400\ \mathrm{V}\)、\(f_{sw}=100\ \mathrm{kHz}\)，\(L_1=L_2=1.5\ \mathrm{mH}\)、\(L_s=7.5\ \mu\mathrm{H}\)、\(C_{bat}=150\ \mu\mathrm{F}\)、\(C_{ac}=4.7\ \mu\mathrm{F}\)。control scheme 与 gate-pulse combinational logic 运行在 TI TMS320F28397D 与 Xilinx XC6SLX4 组成的 custom DSP-FPGA interface board 上。[pdf:E06]（PDF 物理页 6，Fig. 6、Table II）[pdf:E07]（PDF 物理页 7，Section IV-A 开头）

从 EMT/FPGA 角度必须保留几项“论文未报告”。本文给出了 switching event 的连续时间分段模型，但没有报告用于 EMT simulation 的离散积分格式、network matrix、solver dependency 或 real-time step。100 kHz carrier 与 50 Hz output 构成明确的时间尺度分离，但控制采样频率、ADC/PWM pipeline latency、DSP 与 FPGA 的精确 partition、fixed-point/float 数值表示、word length、FPGA resource、timing closure、WCET 和端到端 deadline 都未报告。因此它证明的是 FPGA-assisted gate generation 的 converter 实验，不是可据此直接复现的 FPGA real-time EMT architecture。

## § 6 — 核心数学推导（无形式化数学则跳过）

核心推导先把 50 Hz 正弦输出离散到第 \(k\) 个 switching interval。作者令

\[
v_l^{(k)}(\tau)=V_m\sin(\omega_g\tau),\qquad \tau=k t_{sw}.
\]

这里的物理含义是：在一个 10 \(\mu\mathrm{s}\) switching interval 内把目标交流电压视为不变，跨 interval 才沿 50 Hz 正弦更新；10 \(\mu\mathrm{s}\) 是由 Table II 报告的 100 kHz 换算而来。[pdf:E04]（PDF 物理页 4，Eq. (1)）[pdf:E06]（PDF 物理页 6，Table II）

由 HFT 变比和电池电压决定的总 dc-side duty 为

\[
D^{(k)}
=\frac{2n\left|v_l^{(k)}(\tau)\right|}{V_{bat}}
+\left(\alpha^{(k)}+\beta^{(k)}\right).
\]

第一项是产生目标 HFT/输出电压所需的 effective duty；\(\alpha^{(k)}+\beta^{(k)}\) 是 HFT current reversal 占用的 duty loss。因为 \(|v_l|\) 是 rectified sine，\(D^{(k)}\) 以及它所定义的 phase shift 也自然呈 rectified-sinusoidal shape。这是整篇论文最关键的数学观察。[pdf:E04]（PDF 物理页 4，Eq. (2) 及其后变量解释）

为了把该 shape 直接写进 pulse generator，作者构造归一化 reference

\[
m^{(k)}(\tau)=\left|v_{\mathrm{ref}}^{(k)}\right|
=\frac{nV_m}{V_{bat,\min}}\left|\sin(\omega\tau)\right|,
\]

再分别在两条反相 carrier 的 positive/negative slope 上 set 或 reset SR latch。Eq. (4)–(7) 给出 \(S_{AT}\) 与 \(S_{BT}\) 的 Boolean recurrence；它们不是一般的 sine PWM，而是把 carrier slope、output polarity 和 latch state 共同编码进 gate sequence。[pdf:E04]（PDF 物理页 4，Eq. (3)–(7)、Fig. 3）

软开关证明依赖 piecewise-linear current。Eq. (8)–(20) 分别描述四个 stage 中 HFT leakage current 与各 switch current 的线性上升或下降；\(\alpha\) 与 \(\beta\) 的 interval duration 由 HFT current、\(L_t\)、\(V_{bat}\) 决定。例如

\[
\alpha^{(k)}\frac{t_{sw}}{2}
=\frac{nL_t\left|i_{lk}^{(k)}(t_2)\right|}{V_{bat}},
\qquad
\beta^{(k)}\frac{t_{sw}}{2}
=\frac{nL_t\left|i_{lk}^{(k)}(t_0)\right|}{V_{bat}}.
\]

这说明“duty loss”不是任意补偿项，而是电感电流完成反向所需的实际换流时间。[pdf:E05]（PDF 物理页 5，Eq. (18)）[pdf:E06]（PDF 物理页 6，Eq. (21)）

论文还用 semiconductor conduction/turn-off energy、inductor copper/core loss 与 HFT IGSE core-loss model 估计效率。Eq. (22)–(25) 的损耗模型使用 datasheet 参数和 analytical current expressions；它支撑 measured/theoretical efficiency curve 的一致性判断，但不是 sinusoidal phase-shift modulation 成立的前提。[pdf:E08]（PDF 物理页 8，Eq. (22) 与 Loss Analysis）[pdf:E09]（PDF 物理页 9，Eq. (23)–(25)、Fig. 13）

## § 7 — 实验设计与结论

**问题 1：调制能否在真实功率级产生随交流周期变化的 phase shift，并输出正弦电压？**  
实验：作者在 \(V_{bat}=345\ \mathrm{V}\)、\(P_o=1.5\ \mathrm{kW}\) 的 V2H full-load 条件下，同时测量 \(v_l,i_{ac},i_{bat},i_{lk},v_{pq},v_{rs}\)，并分别放大 output-voltage peak 与 zero crossing。  
答案：Fig. 8 显示 phase shift 在 peak 最大、zero crossing 最小，且输出为正弦；这直接支持“phase shift shape 已嵌入 pulse generation”，但图中没有给出 phase-shift tracking error 的数值。[pdf:E07]（PDF 物理页 7，Fig. 8 与相邻正文）

**问题 2：面对不同住宅负载，output voltage quality 是否仍可接受？**  
实验：分别接入 resistive-inductive load 和 diode-bridge-plus-capacitor nonlinear load。  
答案：在线性/感性负载下，作者报告 output-voltage THD 和 output-current THD 均为 2.29%，battery-current THD 为 2.76%；非线性负载下，相应数值变为 3.29%、22.9% 和 42.36%。作者指出 3.29% 的 output-voltage THD 低于 IEC 61000-2-2 的 8% limit。这里能得出的结论是“电压波形仍受控”，不能把较高的 nonlinear-load current/battery-current THD 说成已被消除。[pdf:E07]（PDF 物理页 7，Fig. 9(a)(b) 后正文）[pdf:E08]（PDF 物理页 8，首段）

**问题 3：控制器能否应对 load step 和 G2V/V2H transition？**  
实验：负载在 \(0.5\ \mathrm{kW}\) 与 \(1.5\ \mathrm{kW}\) 之间突变；另在 grid outage 时从 G2V 切到 V2H，并在电网恢复、PLL 重同步后切回 G2V。  
答案：作者报告 output voltage 保持在 \(230\ \mathrm{V_{rms}}\)，模式切换“smooth”；恢复侧在 \(v_g^d>0.45\) p.u. 时识别电网恢复，等待 \(v_g^d\) 升至 1 p.u. 表示 PLL 完成同步后才回到 G2V。论文没有给出 interruption time、overshoot、settling time 或 transfer-time standard comparison，因此“seamless”只能理解为所示示波图未出现明显失控。[pdf:E07]（PDF 物理页 7，Fig. 9(c)、Fig. 10）[pdf:E08]（PDF 物理页 8，dynamic response 与 transition 正文）

**问题 4：battery voltage 改变时，V2H regulation 是否保持？**  
实验：在 700 ms 内把 \(V_{bat}\) 从 380 V（文中标作 90% SOC）降到 320 V（10% SOC），观察 \(v_l,i_{ac},i_{bat}\)。  
答案：输出交流电压在该 accelerated sweep 中保持调节。作者明确说明真实电池放电会持续数小时，所以该实验验证的是 controller tracking ability，不是电池容量、thermal drift 或长期稳定性。[pdf:E07]（PDF 物理页 7，Fig. 11）[pdf:E08]（PDF 物理页 8，Fig. 11 解释）

**问题 5：soft switching 是否在输出 peak 与 zero crossing 都出现？**  
实验：分别放大交流侧 \(S_{1ag}\) 与直流侧 \(S_{BT}\) 在 output-voltage peak/zero crossing 附近的 \(v_{gs},v_{ds}\) 和 HFT voltage。  
答案：交流侧在 gate falling edge 时 \(v_{ds}=0\)，作者据 body-diode conduction 和 current natural zero 判断为 ZCS；直流侧在 gate rising edge 时 \(v_{ds}=0\)，判断为 ZVS turn-on。Fig. 12 支持这两个采样位置，但没有给出所有 load、temperature、battery voltage 和每个 switching event 的 soft-switching margin map。[pdf:E08]（PDF 物理页 8，Fig. 12 与相邻正文）

**问题 6：效率和损耗表现怎样？**  
实验：在 \(V_{bat}=345\ \mathrm{V}\) 下测量 0.5–1.5 kW 的 G2V/V2H efficiency，并与 analytical loss model 对比；满载时再展示 loss distribution。  
答案：作者报告 V2H peak efficiency 为 93.1%，G2V 为 94.3%；light-load charging/discharging efficiency 分别为 88.6% 和 87.5%。Table III 中一些既有 1-S OBC 的表列 efficiency 达到 95%–97%，所以本文不能据此宣称效率领先；它的证据重点是用较简单 modulation 在本原型上同时得到 V2H regulation 与 ZCS/ZVS。[pdf:E09]（PDF 物理页 9，Table III、Fig. 13）[pdf:E10]（PDF 物理页 10，Fig. 14、Efficiency 与 Conclusion）

**不得外推的范围。** 论文没有报告 EMI、conducted/radiated emissions、isolation qualification、thermal cycling、battery-aging comparison、long-duration blackout、more-than-1.5-kW hardware、full 300–400 V × full-load matrix、failure statistics、FPGA resources/timing 或 grid-forming protection。实验支持的是一台 1.5 kW laboratory prototype 上所展示的工况，不是量产 OBC 的完整合规性或 lifetime 证据。

## § 8 — Take-aways

**5 句话**

1. 论文在既有 L-L current-fed bidirectional OBC 上补齐了 V2H 所需的 sinusoidal output-voltage modulation。[pdf:E02]（PDF 物理页 2，贡献 1–4）  
2. 核心做法是把 rectified-sinusoidal phase shift 直接嵌入 carrier/latch pulse generation，而不是让 conventional PI 逐点追踪相移角。[pdf:E04]（PDF 物理页 4，Eq. (2)–(7)）  
3. 四阶段换流利用 HFT/boost-inductor current 让交流侧实现 ZCS、直流侧实现 turn-on ZVS。[pdf:E05]（PDF 物理页 5，Fig. 4、Stage 1–4）[pdf:E08]（PDF 物理页 8，Fig. 12）  
4. 1.5 kW、100 kHz DSP-FPGA 原型验证了 230 V regulation、线性与非线性负载、0.5–1.5 kW load step、G2V/V2H transition 和 320–380 V accelerated battery sweep。[pdf:E06]（PDF 物理页 6，Table II）[pdf:E07]（PDF 物理页 7，Fig. 8–11）[pdf:E08]（PDF 物理页 8，实验解释）  
5. 本文强项是拓扑、调制、控制与硬件波形闭合；基于证据的批评是，它没有报告全 operating-envelope soft-switching margin、长期电池/热/EMI 与 FPGA implementation metrics。

**3 句话**

1. 作者把 V2H 相移角应有的正弦形状内生到 PWM generator，使外环控制从 waveform tracking 简化为 amplitude regulation。[pdf:E04]（PDF 物理页 4，Fig. 3）  
2. 原型结果支持输出电压质量、模式切换和所测点的 ZCS/ZVS，但只覆盖有限工况。[pdf:E07]（PDF 物理页 7，Fig. 8–11）[pdf:E08]（PDF 物理页 8，Fig. 12）  
3. 因而它是一个有实物证据的 converter-control contribution；基于缺失项的判断是，它没有形成效率领先、量产可靠性或 FPGA real-time computation 的完整证明。

**1 句话**

这篇论文的本质，是用“结构化生成相移”替代“控制器追踪相移”，从而让同一单级无电解电容 OBC 在 V2H 中兼顾正弦输出与软开关。[pdf:E04]（PDF 物理页 4，Eq. (2)–(7)）[pdf:E08]（PDF 物理页 8，Fig. 12）

## § 9 — 最脆弱的假设

失败代价最大的假设是：**在所有作者声称覆盖的 output-voltage phase 与 loading conditions 下，HFT leakage/boost-inductor current 都有足够且方向正确的换流能量，使交流侧 current 能自然归零、直流侧 device capacitance 能在 gate edge 前完成充放电。**

如果这个条件在 very-light-load、battery-voltage corner、nonlinear-load current crest、dead-time error、magnetic tolerance、device \(C_{oss}\) 非线性、temperature 或 aging 下失效，pulse generator 仍可能输出看似正常的 230 V sine，但开关会转为 hard switching。这样一来，论文最重要的“简单 modulation 仍能在全周期获得 ZCS/ZVS”的解释、loss model 假设和 efficiency 优势会一起松动。

论文给出的正面证据是 Fig. 12：在 output peak 与 zero crossing 两处，实测交流侧 \(v_{ds}=0\) 的 turn-off/ZCS 条件和直流侧 \(v_{ds}=0\) 的 turn-on/ZVS 条件；Fig. 8 也显示相移随 output phase 改变。[pdf:E07]（PDF 物理页 7，Fig. 8）[pdf:E08]（PDF 物理页 8，Fig. 12）缺失的是逐 switching event 的 commutation-energy margin、跨 Table II 所列 300–400 V battery range 与原型 load range 的二维 envelope、temperature/tolerance sweep 和 soft-switching failure boundary。[pdf:E06]（PDF 物理页 6，Table II）因此“全 output cycle 与不同 loading conditions”目前是有限采样支持的作者结论，不是穷尽性证明。

## § 10 — 最小复现实验

一周内最值得复现的不是整台量产 OBC，而是“embedded sinusoidal phase shift 是否在报告工况内同时维持 output regulation 与 soft-switching condition”。

1. **数据与模型。** 按 Table II 建立 switching model：\(V_g=230\ \mathrm{V_{rms}}\)、50 Hz、\(V_{bat}=300\text{–}400\ \mathrm{V}\)、\(f_{sw}=100\ \mathrm{kHz}\)、\(L_1=L_2=1.5\ \mathrm{mH}\)、\(L_s=7.5\ \mu\mathrm{H}\)、\(C_{bat}=150\ \mu\mathrm{F}\)、\(C_{ac}=4.7\ \mu\mathrm{F}\)，并使用 Fig. 7 的 resistive-inductive 与 diode-bridge-capacitor loads。[pdf:E06]（PDF 物理页 6，Table II、Fig. 7）
2. **实现。** 实现 Eq. (3)–(7) 的 two-carrier/SR-latch gate generator、Fig. 5 的 \(dq\)-frame PI voltage loop，以及 Fig. 4 的四阶段 switching sequence；先在 switching simulation 中跑通，再把同一 gate logic 放进一块可用 FPGA 或 logic-in-the-loop target。需要明确：论文未给 PI gains、dead time 和 digital word length，复现者必须公开自己采用的数值，不能把它们伪装成论文参数。
3. **工况。** 先严格复现 \(V_{bat}=345\ \mathrm{V}\)、\(P_o=1.5\ \mathrm{kW}\)，再做 0.5→1.5 kW load step；分别测 output peak、zero crossing 的 phase shift、\(v_{gs}\)、\(v_{ds}\)、switch current 和 output THD。
4. **支持标准。** 在同一负载定义下，output-voltage THD 落在论文 2.29%（linear/inductive）和 3.29%（nonlinear）附近；load step 后保持 230 \(\mathrm{V_{rms}}\) 且不失稳；每个被测 peak/zero-crossing event 在 gate edge 前满足交流侧 current 近零、直流侧 \(v_{ds}\) 近零。为避免“近零”事后解释，应在实验前按 probe noise 与器件额定值固定阈值，例如 5% rated current/voltage。
5. **反驳标准。** 在报告工况和合理 dead-time/parasitic 参数下，phase shift shape 无法复现，output-voltage THD 明显越出预注册误差带，或 peak/zero crossing 任一位置稳定出现 hard-switching event，都足以反驳核心 claim 的可复现性。simulation 能验证机制和逻辑，但不能单独复现 93.1% hardware efficiency。

## § 11 — 最强反例设计

最强攻击不是再接一种普通负载，而是主动寻找“output voltage 仍正常、soft switching 已失效”的分离场景。具体做法是把 \(V_{bat}=300,345,400\ \mathrm{V}\)，load 从 1.5 kW 向 very-light-load 逐级下降，再叠加 diode-bridge-capacitor 的高 crest factor；对 \(L_s\)、HFT leakage、dead time、device \(C_{oss}\) 和 winding resistance 做温度与容差 sweep。每个 50 Hz phase bin 都记录 turn-on/turn-off 前的 \(v_{ds}\)、switch current 与 commutation completion time，而不是只在 peak 和 zero crossing 截两张波形。

如果在某个低功率或参数 corner，外环仍把 \(v_l\) 调到 230 \(\mathrm{V_{rms}}\)，THD 也保持在 8% 以下，但直流侧在 gate rising edge 前 \(v_{ds}\) 尚未归零，或交流侧 turn-off 时 current 不为零，那么 alternative explanation 就成立：良好输出主要来自 voltage loop 和 output filter，并不证明 proposed modulation 在整个 operating envelope 保证软开关。该反例会直接击中论文的核心机制，而不只是说明效率略有下降。论文现有 Fig. 12 只覆盖 peak/zero-crossing 的有限示波点，不能排除此类 failure boundary。[pdf:E08]（PDF 物理页 8，Fig. 12）

## § 12 — Follow-up Research Idea

在 power electronics 与 transportation electrification 领域，高影响工作通常不仅看新 modulation 名称，还看硬件功率等级、wide-envelope efficiency、soft-switching boundary、thermal/EMI/reliability、保护与标准相关性。基于第 9 节，候选方向是：**把 soft-switching 从“调制自然产生的结果”改写为一个在线可观测、可约束的 hybrid-system invariant。** 这里不声称 novelty，因为本卡没有补充检索 adaptive dead-time、commutation control、model-predictive modulation 或 control-barrier-function 相关工作。

**(a) 未满足需求。** 固定 carrier/latch logic 在 nominal prototype 上有效，但量产器件的 \(C_{oss}\)、magnetics、dead time、temperature、battery voltage 和 load crest factor 都会漂移；工程上真正需要的是每次 switching event 都有可量化 commutation margin，而不是若干示波截图。

**(b) 研究价值。** 研究目标从“生成正确的正弦 phase shift”变成“在不牺牲 V2H voltage quality 的条件下，保证或显式报告每个 event 的 ZVS/ZCS feasibility”。本文原型额定 1.5 kW；若候选工作能在更高功率硬件上给出 envelope、efficiency、EMI 与 failure boundary，这比单纯调 PI 或增加一个补偿项更符合本领域对可实现性与可靠性的评价。[pdf:E06]（PDF 物理页 6，Table II）

**(c) 可借鉴方法。** 可把 power-stage piecewise model 写成 hybrid automaton，用 event-triggered observer 从 \(v_{ds}\) transition time 与 current zero crossing 估计 commutation margin，再用 robust model-predictive control 或 control barrier function 约束下一 interval 的 \(\alpha+\beta\)、dead time 或 phase-shift correction。关键是控制量仍受 output-voltage/THD 与 circulating-current penalty 共同约束，不能通过无限增加换流电流“买到”软开关。

**(d) 首个证伪实验。** 直接在本文 Table II envelope 上做 300–400 V、0.05–1.5 kW、linear/nonlinear load、cold/hot 与磁件容差的自动 sweep。若 fixed modulation 本来就在所有 corner 保持足够 margin，在线 invariant 没有减少 hard-switching events 或损耗，该方向没有必要；若 observer 的 margin 估计不能提前预测真实 \(v_{ds}\)/current violation，也应立即否决。

**(e) 与本文的实质区别。** 本文预先编码 rectified-sinusoidal phase shift，并通过有限波形点证明软开关；候选工作则把“换流是否完成”设为每个 event 都要测量和维持的控制约束，允许系统在元件与工况漂移时显式调整或报告不可行。它改变的是问题定义和可证伪对象，不只是把本文 modulation 换一个应用或叠加一个普通 PI loop。
