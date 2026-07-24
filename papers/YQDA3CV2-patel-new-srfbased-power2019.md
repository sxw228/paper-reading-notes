# A new SRF-based power angle control method for UPQC-DG to integrate solar PV into grid

作者：Ashish Patel；Hitesh Datt Mathur；Surekha Bhanot [pdf:E01]（PDF 物理页 1，标题与作者栏）  
出处：*International Transactions on Electrical Energy Systems*，29:e2667 [pdf:E01]（PDF 物理页 1，页脚与论文首页）  
年份：2019 [pdf:E01]（PDF 物理页 1，期刊卷期信息）  
DOI：10.1002/etep.2667 [pdf:E01]（PDF 物理页 1，首页 DOI）  
Zotero key：YQDA3CV2  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的是一个很具体的功率电子容量失配问题：在太阳能 PV 接入直流母线的 UPQC-DG 中，shunt APF（并联有源电力滤波器）不仅要补偿负载无功和谐波，还要把 PV 有功送往负载；series APF（串联有源电力滤波器）在电网电压正常时却几乎没有 VA 负担。作者因此提出 SRF-based PAC（基于同步参考坐标系的功角控制），让 series APF 通过有意改变负载电压相位来承担一部分无功，从而降低 shunt APF 的 kVA 压力并提高两台变流器的容量利用率 [pdf:E01]（PDF 物理页 1，Summary）。

这个问题重要，不只是因为“功率质量要好”，而是因为 UPQC-DG 把原本由独立并网逆变器承担的 PV 功率传输任务并入 shunt APF：如果仍按传统 UPQC 控制，系统最忙的变流器会更忙，最闲的变流器仍然闲置，最终会推高 shunt APF 额定容量、器件成本和热设计压力。论文的工程价值在于试图不增加主功率硬件，只通过参考量和功率分配规则重用 series APF 的空闲容量，同时继续维持负载电压、源电流波形和直流母线 [pdf:E02]（PDF 物理页 2，Introduction 中 UPQC-DG 与 PAC 的动机）。

## § 2 — 前人工作与不足

以下比较是论文作者在引言中的归纳，未使用包外文献独立复核。

传统 IRP/p-q theory 控制计算简单、响应快，但作者指出它在非理想电网电压下表现不好；已有 SRF/d-q theory 的 PV-UPQC-DG 控制利用 PLL 处理电压畸变，却没有处理 series 与 shunt APF 额定容量的高效利用。已有 PAC 能让 series APF 分担无功，但基于 p-q theory 的版本仍对非理想供电敏感；已有 SRF-PAC 有的没有把 sag/swell 补偿纳入 series APF 控制，有的追求两台 APF 等 VA、算法复杂且只在小功角下较准确。更关键的是，这些普通 UPQC 的 PAC 公式没有显式容纳 DG 注入有功，不能直接套到 UPQC-DG [pdf:E02]（PDF 物理页 2，Introduction 的 prior-work 比较）。

作者还指出，已有面向 PV-UPQC-DG 的 p-q PAC 工作要求供电电压平衡且无谐波，并且没有细致建模 PV 发电系统。由此，本文试图同时补三个缺口：用 SRF/PLL 提高对供电波形的适应性；把 PV 有功从 series APF 所见的有效负载有功中扣除；用较简单的瞬时三相功率估计来得到功角，并用 series APF 额定值限制最大功角 [pdf:E02]（PDF 物理页 2，提出方法前的限制与三项 salient features）。

论文没有给出与这些 prior PAC 算法在相同模型、相同扰动下的直接算法级对比，也没有报告计算时间或 CPU load。因此，“计算更少、瞬态更快”主要是作者的设计主张；实验真正直接支持的是 PAC 与 no-PAC 两种控制下的功率分担和波形表现，而不是相对其他 SRF-PAC 算法的计算优势。

## § 3 — 重建作者的思考路径

基于论文给出的背景，可以把作者的思考过程逆向重建为以下链条；这是基于证据的合理推断，不是作者逐字陈述。

第一步，观察硬件利用率不对称。UPQC-DG 的 shunt APF 同时承担 PV 有功、负载无功、谐波补偿和 DC-link regulation，而 series APF 在正常电压下只补很少的电压误差。既然两者共用直流母线，最自然的优化不是再加变流器，而是把一部分无功工作转移给 series APF [pdf:E02]（PDF 物理页 2，PAC 对 UPQC-DG 的意义）。

第二步，利用 PAC 的物理机制：series APF 不再只注入与源电流同相的补偿电压，而是注入带相角的电压，使负载电压相对源电压产生功角 δ。这样 series APF 的电压与线路电流近似正交时，可以主要交换无功，而不需要持续交换大量有功 [pdf:E03]（PDF 物理页 3，Section 3 对固定/可变 PAC 的解释）[pdf:E04]（PDF 物理页 4，Fig. 2 相量图）。

第三步，发现固定 δ 不够。sag、normal、swell 下，为维持同一个 δ 所需的 series voltage 不同；若按最坏 swell 选额定值，正常和 sag 时 series APF 又会闲置。因此 δ 应随 supply-voltage fraction 改变，并由 series APF 最大可注入电压反算上限 δmax [pdf:E03]（PDF 物理页 3，fixed 与 variable PAC）[pdf:E04]（PDF 物理页 4，Eq. 7–9）。

第四步，把 DG 纳入功率几何。普通 UPQC 用负载有功 PL 作为功角关系的有功基准；UPQC-DG 中 PV 通过 shunt APF 提供了一部分负载有功，所以 series APF 所见的净有功应写成 PL−PPV。由此把原公式改为 δ=sin⁻¹(QSr/(PL−PPV)) [pdf:E04]（PDF 物理页 4，Eq. 10–11）。

第五步，为降低实现复杂度，直接用控制器已有的三相负载电压、电流和 PV 直流量估计 PL、QL、PPV，经 low-pass filter 取得平均值；再令最终功角为需求功角与额定上限的较小者。series APF 用 unit-vector template 与 voltage PWM，shunt APF 用 SRF、PI DC-link regulation 和 hysteresis current control，boost converter 用 incremental-conductance MPPT [pdf:E05]（PDF 物理页 5，Fig. 3）[pdf:E06]（PDF 物理页 6，Eq. 13–17 与 Sections 4.1–4.3）[pdf:E07]（PDF 物理页 7，Eq. 18）。

## § 4 — 核心 Intuition

核心直觉是：series APF 的“电压注入能力”不必只留给偶发 sag/swell，它也可以通过旋转负载电压参考相位，在正常运行时承担负载无功。控制器用实时功率估计决定需要多大的 δ，再用由 series APF 额定电压推导出的 δmax 截断它，从而把无功尽可能推给 series APF、但不越过其容量边界 [pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. 7–11）[pdf:E05]（PDF 物理页 5，Eq. 12 与 Fig. 3）。

UPQC-DG 与普通 UPQC 的关键差别只有一个却决定公式是否成立：PV 已承担的有功必须从 PL 中减掉。换言之，作者不是重新设计整个 UPQC，而是修改“功角由哪一个净功率工作点决定”，然后让既有 series/shunt/boost 三套控制围绕这个功角协同工作。

## § 5 — 具体方法与完整 Pipeline

论文系统是三相三线 UPQC-DG：series APF 和 shunt APF 都是 IGBT 三相三桥臂逆变器，共用 700 V DC link；PV array 通过 boost converter 接入直流母线；series injection transformer、interfacing inductor 和高通 RC filter 构成主电路接口 [pdf:E03]（PDF 物理页 3，Fig. 1 与 Section 2）[pdf:E08]（PDF 物理页 8，Table 1）。

以“415 V/50 Hz 电网、三组负载、PV 在最大功率点运行”为例，完整 pipeline 如下：

1. **采样与功率估计。** 采样三相负载电压/电流、源电压/电流、PV 电压/电流和 DC-link voltage。由瞬时三相乘积得到 PL，由线电压与相电流得到 QL，由 VPV·IPV 得到 PPV；PL、QL 在 nonlinear load 下会振荡，因此先 low-pass filtering [pdf:E06]（PDF 物理页 6，Eq. 13–15）。
2. **需求功角。** Fig. 3 把滤波后的 QL 作为希望由 series APF 承担的 QSr 候选，用 δc=sin⁻¹(QSr/(PL−PPV)) 计算需求功角。作者在分母可能为零的位置加入 limiter [pdf:E05]（PDF 物理页 5，Section 4.1 与 Fig. 3）[pdf:E04]（PDF 物理页 4，Eq. 11）。
3. **额定值约束。** 根据当前 supply-voltage fraction fs 与 series-voltage rating fraction fSr,max 计算 δmax；最终 δF=min(δc,δmax)。这使 series APF 在有足够无功需求时尽量接近满容量，但在 sag/swell 下随可用电压余量调整 [pdf:E04]（PDF 物理页 4，Eq. 7–9）[pdf:E06]（PDF 物理页 6，δc 与 δmax 的选择逻辑）。
4. **series APF 参考生成。** 三相 PLL 给出基波相角 ωt，把 δF 加到 ωt 上生成三相 unit vectors；乘以期望负载电压幅值后得到相移后的 vL,abc*，再由 voltage PWM controller 产生 series APF gate pulses [pdf:E06]（PDF 物理页 6，Eq. 16 与 Section 4.1）。
5. **shunt APF 电流控制。** 将 iL,abc 经 Park transform 变到 dq0；low-pass filter 提取 fundamental in-phase d-axis component，减去 PV 供给的有功电流分量，再叠加 DC-link PI controller 的补偿量，逆变换成平衡正弦 source-current references。实际 source currents 与 references 进入 hysteresis current controller，生成 shunt APF gate pulses [pdf:E05]（PDF 物理页 5，Fig. 3B）[pdf:E06]（PDF 物理页 6，Eq. 17 与 Section 4.2）。
6. **boost converter。** incremental-conductance MPPT 利用最大功率点处 dP/dV=0，即 dI/dV=−I/V，积分调节 duty-cycle correction，再经 PWM 驱动 boost switch [pdf:E07]（PDF 物理页 7，Eq. 18 与 Section 4.3）。
7. **实时执行与多速率。** Opal-RT OP-4510 的 FPGA engine 运行 UPQC-DG electrical plant，Fig. 4 标注 Ts=0.5 μs；CPU core 运行 controller，Ts=15 μs。两者通过 measurements 与 control signals/switching pulses 闭环交换，仿真结果经 analog outputs 记录并传到 host PC [pdf:E07]（PDF 物理页 7，Section 5.1 与 Fig. 4）。

EMT/FPGA 实现边界必须说清：论文报告了开关级 plant、hysteresis/PWM 事件和 CPU-FPGA 多速率闭环；没有报告 FPGA 内部网络撕裂后的具体分区、并行调度、逻辑资源、时序裕量、通信延迟、数值定点/浮点格式或 controller-to-HDL mapping。这些内容不能从“plant 在 FPGA 上以 0.5 μs 运行”外推出来。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确形式化数学，核心是把 series-voltage 几何约束、负载/PV 功率平衡和参考信号生成串起来。

**1. 从相量三角形得到可用功角上限。** 设正常负载电压幅值为 k，sag 后源电压幅值为 k′，定义 fs=k′/k、fSr=|V′Sr|/k。由 Fig. 2 的余弦定理：

\[
f_{Sr}=\sqrt{1+f_s^2-2f_s\cos\delta}.
\]

当 series APF 注入达到额定 fSr,max 时：

\[
\delta_{max}=\cos^{-1}\!\left(\frac{1+f_s^2-f_{Sr,max}^2}{2f_s}\right).
\]

直觉上，δmax 不是固定保护阈值；source-voltage magnitude 改变时，相量三角形可容纳的相移也改变，所以 sag/swell 时必须在线重算 [pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. 7–9）。

**2. 用净有功决定需求功角。** 普通 UPQC 的关系为 δ=sin⁻¹(QSr/PL)，本文把分母改为净有功：

\[
\delta_c=\sin^{-1}\!\left(\frac{Q_{Sr}}{P_L-P_{PV}}\right),
\qquad
Q_{Sr,max}=(P_L-P_{PV})\sin\delta_{max}.
\]

物理意义是：PV 已经通过 shunt APF 向负载供给 PPV，series APF 所面对的有功工作点只剩 PL−PPV。控制框图实际把 QL 送入功角计算，若 QL 对应的 δc 超过 δmax，就只能由 series APF 提供 QSr,max，其余无功交给 shunt APF [pdf:E04]（PDF 物理页 4，Eq. 10–11）[pdf:E05]（PDF 物理页 5，Eq. 12 与 Fig. 3）。

**3. 直接从现有测量估计功率。** 论文采用：

\[
P_L=v_{La}i_{La}+v_{Lb}i_{Lb}+v_{Lc}i_{Lc},
\]

\[
Q_L=\frac{v_{Lbc}i_{La}+v_{Lca}i_{Lb}+v_{Lab}i_{Lc}}{\sqrt{3}},
\qquad
P_{PV}=V_{PV}I_{PV}.
\]

PL、QL 在 nonlinear load 下含有振荡，作者用 low-pass filter 取平均。工程优势是无需新增传感量；代价是功率估计和滤波动态直接进入 δ 环节 [pdf:E06]（PDF 物理页 6，Eq. 13–15）。

**4. 把功角写进三相电压参考。** PLL 给出 ωt，最终功角 δF 加到三个相位：

\[
\begin{bmatrix}U_a\\U_b\\U_c\end{bmatrix}
=
\begin{bmatrix}
\sin(\omega t+\delta_F)\\
\sin(\omega t+\delta_F-2\pi/3)\\
\sin(\omega t+\delta_F+2\pi/3)
\end{bmatrix}.
\]

再乘期望负载电压峰值得到 series APF 的 load-voltage references。这里的 δF=min(δc,δmax) 是方法最核心的非线性限幅 [pdf:E06]（PDF 物理页 6，Eq. 16）。

**5. shunt APF 的 SRF 提取。** Eq. 17 用标准 Park transform 将 iL,abc 转为 Id、Iq、I0；与 PLL 同步的 fundamental in-phase current 在 d 轴成为近似 DC，可经 low-pass filter 提取。随后设置 q、0 轴参考为零，并对 d 轴做 PV feed-forward 与 DC-link PI 修正，以生成平衡、正弦、unity-power-factor 的 source-current reference [pdf:E06]（PDF 物理页 6，Eq. 17 与其后正文）。

**6. PV MPPT。** 最大功率点满足 dP/dV=0。因 P=VI，可得 I+V·dI/dV=0，即 dI/dV=−I/V；积分器最小化 dI/dV+I/V 并修正 boost duty cycle [pdf:E07]（PDF 物理页 7，Eq. 18）。

## § 7 — 实验设计与结论

**问题 1：PAC 能否把无功从 shunt APF 转移到 series APF，同时保持基本功率质量？**  
实验：在 415 V、50 Hz 三相三线系统中连接一组 thyristor bridge nonlinear load 和两组 RL load；DC link 为 700 V，series/shunt ratings 分别为 9/20 kVA，PV array 额定 15.3 kW [pdf:E08]（PDF 物理页 8，Table 1–3）。稳态波形显示 source voltage 与 source current 同相，series voltage 与 source current 近似正交，报告最大可达功角为 23.1° [pdf:E08]（PDF 物理页 8，Section 6.1）[pdf:E09]（PDF 物理页 9，Fig. 5–6）。答案：在该平衡、净负载工况下，PAC 达到了预期的无功转移和 unity power factor。

**问题 2：对不同 nonlinear-load harmonic pattern，源电流能否继续接近正弦？**  
实验：把 thyristor rectifier firing angle 设为 0°、30°、60°。Table 4 报告 load-current THD 分别为 10.09%、9.22%、9.38%，source-current THD 分别为 2.12%、3.13%、4.25%；三种都低于论文采用的 5% 判断线 [pdf:E10]（PDF 物理页 10，Fig. 7–8 与 Table 4）。答案：在这三个谐波工况中，shunt SRF/hysteresis control 能显著压低源电流 THD，但 30°/60° 工况的较强低次谐波使 source THD 上升。

**问题 3：PV 出力阶跃时，负载和 DC link 是否被隔离？**  
实验：solar irradiation 从 1000 W/m² 阶跃到 600 W/m²。作者报告 source-current THD 为 2.84%，source current 随 PV 输出降低而平滑增加，load current 不承受 PV 波动，DC link 基本维持 700 V [pdf:E10]（PDF 物理页 10，Section 6.2 的输入变化）[pdf:E11]（PDF 物理页 11，Fig. 9–10 后正文）[pdf:E12]（PDF 物理页 12，Fig. 11）。答案：在该单次阶跃和给定控制参数下，功率缺口主要由源电流补上，负载侧波形与 DC link 保持稳定。

**问题 4：25% sag/swell 下能否保持负载电压？**  
实验：分别施加 25% supply-voltage sag 和 25% swell。sag 时 series APF 注入同相有功分量、DC link 短时下跌后被 PI/PV 支撑；swell 时 series APF 吸收有功并经 shunt APF 回送负载。Fig. 12–13 显示负载电压幅值被维持，源/shunt 电流按功率方向变化 [pdf:E11]（PDF 物理页 11，Sections 6.3–6.4）[pdf:E12]（PDF 物理页 12，Fig. 12）[pdf:E13]（PDF 物理页 13，Fig. 13）。答案：对论文采用的平衡 25% 扰动，动态仿真支持 voltage compensation 与 DC-link recovery；没有给出恢复时间、峰值偏差或误差积分等量化指标。

**问题 5：负载变化和同时扰动下是否仍能工作？**  
实验：断开 load-3 后，无功需求降至 4.45 kVAr，作者称由 series APF 单独承担；另测试 sag+load increase 与 sag+irradiance decrease。对应 Fig. 14–16 中负载电压保持，DC link 有短暂 under/overshoot 后恢复，source/shunt currents 按功率缺口变化 [pdf:E12]（PDF 物理页 12，Section 6.5）[pdf:E13]（PDF 物理页 13，Fig. 14 与 Section 6.6）[pdf:E14]（PDF 物理页 14，Fig. 15–16）。答案：方法在作者选择的组合扰动中未失稳，但论文没有系统扫过扰动幅值、相位、持续时间、参数不确定性或测量噪声。

**问题 6：PAC 是否真正改善两台 APF 的 VA sharing？**  
实验：在相同工况下对比 with-PAC 与 without-PAC。稳态时 series APF 从 0.5 kVA 增到 6.6 kVA，shunt APF 从 17.8 kVA 降到 14.8 kVA；作者换算为 series/shunt capacity utilization 73.41%/73.97%，而 no-PAC 为 5.56%/88.95%，并报告 shunt loading 降低 16.9%。swell 时 no-PAC shunt 为 21.2 kVA，超过其 20 kVA rating；PAC 为 19.1 kVA [pdf:E14]（PDF 物理页 14，Section 6.7）[pdf:E15]（PDF 物理页 15，Table 5 与 Conclusion）。答案：这是论文最强的直接证据，说明在给定额定值和工作点上 PAC 通过使用 series APF 的余量降低了 shunt APF 负担。

不得外推的范围包括：没有物理功率柜实验；controller 不在 FPGA fabric 上；没有 unbalanced/harmonic source-voltage 测试矩阵；没有 net-export 工况；没有效率、损耗、器件温升、DC-link ripple 指标、FPGA resource/timing 或端到端 latency 报告。

## § 8 — Take-aways

**5 句话。** 这篇论文把 UPQC-DG 的容量问题定义为“shunt APF 过载、series APF 闲置”的功率分配失衡。它用 PAC 让 series APF 通过负载电压相移承担无功，并用额定电压推导 δmax 防止过度注入。相对普通 UPQC，关键公式把有功基准从 PL 改为 PL−PPV。Opal-RT 实时仿真显示，在给定 9/20 kVA series/shunt ratings 下，稳态 shunt loading 从 17.8 kVA 降到 14.8 kVA，报告降幅 16.9% [pdf:E15]（PDF 物理页 15，Table 5 与 Conclusion）。证据支持“特定平衡、净负载工况下的更好 VA sharing”，但还不支持高 PV 渗透率、反向潮流、物理硬件或 controller-on-FPGA 的普适结论。

**3 句话。** 方法的本质是用 δF=min(δc,δmax) 把 series APF 的空闲电压容量转换为无功承担能力。实验最有力的结果是 PAC/no-PAC 的 Table 5，而不是波形“看起来稳定”。最大未决问题是 PL−PPV 接近零或变号时，核心功角公式会奇异，而论文只给 limiter、没有跨零工况验证 [pdf:E05]（PDF 物理页 5，Section 4.1）。

**1 句话。** 这是一个工程上清晰、实时仿真证据充分但运行包络仍窄的 UPQC-DG 功率分配控制方案。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**净有功 PL−PPV 始终为正、远离零，并且经过滤波后足够平滑。** 核心需求功角直接写成 δc=sin⁻¹(QSr/(PL−PPV))；当 PV 接近负载有功时，分母趋零，比例会越界或对微小测量误差极敏感；当 PV 超过负载、系统进入 net export 时，分母变号，功角符号和功率流向都会发生结构性改变。作者明确承认分母可能为零，并加入 limiter，但没有给出 limiter 形式、抗饱和策略、跨零连续性或稳定性论证 [pdf:E05]（PDF 物理页 5，Section 4.1）。

论文的测试工作点恰好避开了这个问题：PV array 最大功率为 15.3 kW，而 Table 5 的稳态负载有功为 32.7 kW；即使满辐照，净有功仍约为 17.4 kW，远未接近零 [pdf:E08]（PDF 物理页 8，Table 3）[pdf:E15]（PDF 物理页 15，Table 5）。因此，论文提供的证据说明该假设在其测试系统中成立，却没有说明方法在高 PV penetration、轻载、储能回馈或 islanded/export 模式下仍成立。

这是比“没有做更多扰动”更致命的假设，因为它位于 Eq. 11 的分母。一旦不成立，出问题的不只是性能下降，而是功角参考本身失去良态定义，进而可能引发 δ clipping、series/shunt power allocation 和 DC-link control 的联动失真。

## § 10 — 最小复现实验

一周内最值得复现的是论文最强 claim：**PAC 是否能在不越过 series APF rating、不恶化 source-current quality 的前提下，降低 shunt APF VA loading。** 不需要先复现完整 Opal-RT 平台，可以使用同一组开关级或足够高保真的三相仿真模型。

- **数据与参数：** 采用 Table 1–3 的 415 V/50 Hz、700 V DC link、9 kVA series APF、20 kVA shunt APF、三组负载和 15.3 kW PV array [pdf:E08]（PDF 物理页 8，Table 1–3）。
- **实现：** 做两个控制版本。baseline 保持 conventional/no-PAC；实验组实现 Eq. 9、11–17、δF=min(δc,δmax)、series voltage PWM、shunt SRF+hysteresis 和 boost MPPT。先做 firing angle=0° 的 steady state，再做 1000→600 W/m² irradiation step。
- **测量：** 计算 |SSr|、|SSh|、series/shunt rating utilization、source-current THD、source power factor、DC-link mean/ripple，并记录 δF 是否触发 δmax。
- **支持标准：** 稳态结果应至少重现方向和数量级：PAC 下 |SSr| 接近 6.6 kVA、|SSh| 接近 14.8 kVA，而 no-PAC 约为 0.5/17.8 kVA；series 不超过 9 kVA，source-current THD 维持低于 5% [pdf:E10]（PDF 物理页 10，Table 4）[pdf:E15]（PDF 物理页 15，Table 5）。允许因开关频率、滤波器和测量窗不同存在合理偏差。
- **反驳标准：** 若 shunt VA 没有明显下降，或下降是以 series overrating、DC-link 持续偏移、source THD 超限或低频振荡为代价，则核心 claim 不成立。若只能在精确调参、无噪声的单一工作点成立，也应把 claim 限缩为工作点特定结果。

## § 11 — 最强反例设计

最强反例不是再加一个普通 sag，而是把 **PPV/PL 从 0.5 连续扫到 1.2，让 PL−PPV 穿过零**，同时保持一个固定无功需求。实验应缓慢降低负载或提高等效 PV 出力，使系统依次经历净取电、近零净有功和反向送电；在穿零附近叠加小幅 irradiance ripple 或测量噪声，观察 δc、δF、QSr、|SSr|、|SSh|、DC-link voltage 和 source current。

这个反例直接攻击 Eq. 11 的数学结构。可预测的失败模式是：δc 在分母趋零时迅速饱和，limiter 造成不连续或长时间钳位；分母变号后，series APF 的有功/无功方向与原控制假设不再一致；shunt DC-link loop 和 PAC loop 可能相互争夺功率，导致 VA sharing 恶化或 DC-link oscillation [pdf:E04]（PDF 物理页 4，Eq. 11）[pdf:E05]（PDF 物理页 5，limiter 说明）。

若该实验失败，就会给论文结果一个更具体的替代解释：Table 5 的改善可能不是一个覆盖“PV grid integration”全运行域的规律，而是因为测试系统始终处在 PL 显著大于 PPV 的正向潮流区域 [pdf:E08]（PDF 物理页 8，15.3 kW PV）[pdf:E15]（PDF 物理页 15，约 32.7 kW 负载有功）。相反，若经过零点仍能保持连续、容量不越界且 DC link 稳定，才真正强化方法的普适性。

## § 12 — Follow-up Research Idea

**候选研究方向，不声称 novelty：面向双向潮流的约束功率分配 PAC。** 电力电子与实时仿真领域的高影响工作通常不仅需要漂亮波形，还需要覆盖宽运行包络、明确稳定性与容量约束、可重复的硬实时实现，并最终由 HIL/physical prototype 验证。本文的最关键未满足需求是：现有 δc 公式在 PL−PPV≈0 或反向潮流时不良态，而未来高 PV penetration、储能和轻载场景会频繁进入这一状态。

研究目标不再是“给 Eq. 11 加一个更聪明的 limiter”，而是把问题重新定义为：**在 source-voltage disturbance、双向有功、负载无功和 DC-link energy balance 同时存在时，在线求解 series/shunt APF 的受约束复功率分配。** 状态和约束至少包括 |SSr|≤rated、|SSh|≤rated、load-voltage error、source-current THD/proxy、DC-link energy 和功角连续性；控制输出可以是 δ、series-voltage magnitude/phase 与 shunt-current reference，而不是先算一个可能奇异的反正弦。

可借鉴的相邻工具是 hybrid/constrained model predictive control、control barrier function 或基于 atan2 的连续复功率几何参数化，再配合 disturbance observer 处理 low-pass delay 与测量噪声。FPGA 侧的研究价值在于把有限预测域或显式控制律映射成确定时延的控制计算，而不是像本文一样只把 electrical plant 放在 FPGA 上；需要报告固定/浮点格式、资源、worst-case latency、CPU/FPGA communication 和 closed-loop timing margin。

第一个能够证伪该方向的实验应沿用本文 OP-4510 多速率框架，但让净有功在 −5 kW 到 +20 kW 之间扫过零，同时施加 25% sag、irradiance step 和 load-Q step。若新方法不能在所有可行点保持两台 APF 不越额定、DC link 有界、负载电压恢复，并且其 worst-case computation time 不能落在控制周期内，这个研究方向就失败。它与本文的实质区别在于：本文用解析功角公式和 clipping 在正向潮流工作点分担无功；候选方向把双向潮流、容量边界、动态稳定性和硬实时可实现性统一成首要问题。
