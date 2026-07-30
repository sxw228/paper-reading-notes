# Average-Value Modeling of Direct-Driven PMSG-Based Wind Energy Conversion Systems

作者：Qiufang Zhang、Jinghan He、Yin Xu、Zeqi Hong、Ying Chen、Kai Strunz  
出处：IEEE Transactions on Energy Conversion，Vol. 37，No. 1，pp. 264–273  
年份：2021（online publication；卷期发表于 2022 年 3 月）  
DOI：10.1109/TEC.2021.3095486  
Zotero key：MGDS4WD8  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个很具体的系统级建模矛盾：direct-driven PMSG-based wind energy conversion system（WECS）既要在大扰动时正确重现变风速、dc-link 能量积累和 low-voltage ride-through（LVRT），又要能在线性化后给出小信号频域特性；但 detailed switching model 为每次开关事件求解，面对大电网、多电力电子模块和重复仿真时计算代价很高。作者因此提出一个完整机组的 average-value model（AVM），用代数或平均状态关系替换快速开关，同时保留风轮、传动链、六相 PMSG、12-pulse diode rectifier、three-phase-interleaved boost converter、crowbar 和 dual three-phase VSI 之间的动态耦合。论文的摘要和引言把目标明确限定为“大信号时域 + 小信号频域 + 高计算效率”，而不是控制器本身的创新。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，是因为短路时保护动作取决于机电能量是否会在 dc-link 中积累，稳定性分析又取决于 PCC 端口 admittance 是否可信；若模型只保留 grid-side converter，就可能把 PMSG 与 rectifier 的恢复动态误判掉。作者选择的工业原型包含两组相差 30 electrical degrees 的三相定子绕组、并联成 12-pulse 的两套 6-pulse rectifier、三路 interleaved boost、dc-link crowbar 和并联 dual VSI，控制侧同时有 tip-speed-ratio、pitch、boost current 与 grid-side decoupled \(dq\) control。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II）

对 EMT + FPGA 使用者而言，这篇工作的直接价值在“降低离线 EMT 与频扫成本”，不是已经给出 FPGA 实现。论文没有报告 HDL、定点位宽、资源占用、流水线、并行调度、硬件在环或实时固定步长，因此不能把其 MATLAB/Simulink 加速结果外推为 FPGA 实时性能。

## § 2 — 前人工作与不足

论文把 prior work 的缺口分成三层。第一，detailed switching model 能准确表示 converter transient，却因反复开关事件而低效；AVM 的已有价值正是用一个 switching interval 内的端口平均效应换取速度，同时尽量保留大信号和阻抗特性。[pdf:E01]（PDF 物理页 1，Section I）

第二，已有 WECS AVM 并非完全不可用，而是适用对象不够完整：文献 [14] 已将 six-phase PMSG 与 converter reduced model 结合，数值效率好，但采用的 prototype 已很少使用；文献 [15] 有 boost、crowbar 和 VSI 的 grid-side AVM，却把 PMSG 与 machine-side converter 简化为 dc voltage source，无法研究风轮与机侧动态；文献 [16]、[17] 覆盖若干 converter 结构，却遗漏 protection system，因而不能模拟 LVRT。[pdf:E01]（PDF 物理页 1，Section I 关于 [14]–[17] 的评述）

第三，不能简单把一种平均方法套到所有器件。12-pulse diode rectifier 会跨越 CCM-1、CCM-2、CCM-3 与 DCM 等导通模式，若逐模式推导 analytical AVM（AAVM），既难穷尽边界，计及 switch parasitics 后推导也不实际；parametric AVM（PAVM）可从 detailed switching model 数值抽取跨工况映射。相反，boost、VSI 与 crowbar 已有可直接写出的平均状态关系，适合 AAVM。[pdf:E04]（PDF 物理页 4，Section IV-C，Eq. (14)–(20) 前后）

## § 3 — 重建作者的思考路径

以下是基于论文证据的重建，不是作者逐字陈述。

1. 先从实际系统研究任务出发：一个模型必须同时服务变风速、grid-side fault 和频域 admittance，而不是只复现某个 converter 的波形。[pdf:E01]（PDF 物理页 1，Section I）
2. 再选择一个仍被 GoldWind、Vensys 等工业系统采用的 diode-rectifier/boost/VSI topology，避免在已少用的 prototype 上继续优化。[pdf:E02]（PDF 物理页 2，Section II 与 Fig. 1）
3. 把整机拆成有明确 input/output interface 的模块，并优先使用积分形式：capacitor 采用 current-input/voltage-output，inductor 采用 voltage-input/current-output；相邻模块若使用同类 interface 会需要 snubber，故 interface 选择本身也是数值稳定性设计的一部分。[pdf:E03]（PDF 物理页 3，Section IV-A）
4. 对每个模块问“解析平均是否仍可控”。six-phase PMSG 在 non-salient、忽略 rotor damping winding 时具有常数 inductance matrix，保留 phase-domain model 即可；rectifier 的导通模式复杂，改用离线抽取的 PAVM；boost、VSI、crowbar 则用 AAVM。[pdf:E03]（PDF 物理页 3，Section IV-B）[pdf:E04]（PDF 物理页 4，Section IV-C）[pdf:E05]（PDF 物理页 5，Section IV-D–F）
5. 最后用相同 operating scenarios 比较 proposed model、detailed model 与不含完整机侧动态的 AVM [15]，分别检验波形、保护恢复、计算成本和 \(dq\) admittance。这样“速度提升”与“没有丢掉关键动态”才同时可观察。

## § 4 — 核心 Intuition

核心 intuition 是：system-level study 不需要逐次重放快速开关，却必须保留开关子系统在端口上的平均电压、电流、功率和保护作用。作者没有强求一个统一公式，而是按器件物理选择 PAVM 或 AAVM，并保留 PMSG 的 phase-domain 动态；因此 reduction 发生在高频 switching event，而不是把机电能量路径一并删掉。[pdf:E04]（PDF 物理页 4，Fig. 3–5 与 Section IV-C）

换句话说，这是一种“异构但接口闭合”的平均建模：rectifier 的复杂模式用 lookup table，boost/VSI/crowbar 用解析平均，模块之间用数值稳定的电压/电流 interface 连接。

## § 5 — 具体方法与完整 Pipeline

以“风速变化后又发生 grid-side voltage sag”为例，完整 pipeline 如下。

1. **机械输入。** 输入 \(v_{\mathrm{wind}}\) 和 pitch angle \(\beta\)。wind-turbine model 用 \(C_p(\lambda,\beta)\) 把风速变为 mechanical power，再由无 gearbox 的 one-mass drive train 将机械/电磁转矩差积分为 shaft speed 与 rotor angle。[pdf:E02]（PDF 物理页 2，Eq. (1)–(4)）[pdf:E03]（PDF 物理页 3，Fig. 2 与 Eq. (5)–(7)）
2. **six-phase PMSG。** 两组三相绕组相差 30 electrical degrees。作者在 phase domain 中计算 stator voltage、flux linkage 和 electromagnetic torque，并把机端写成 six-phase Thévenin equivalent，使其可直接接入 rectifier。该简化依赖 surface-mounted、non-salient 和忽略 rotor damping winding；若不满足，作者建议改用 voltage-behind-reactance model。[pdf:E03]（PDF 物理页 3，Eq. (8)–(13)）
3. **12-pulse diode rectifier PAVM。** 两组三相量分别做 Park transformation；PAVM 用 \(\alpha_k,\beta_k,\phi_k\) 表示平均 ac/dc 端口映射。离线 detailed model 以 line frequency \(f_e\) 与 dynamic impedance \(z_k\) 扫描工作域，生成 lookup table；在线模型以 stator currents、rectified dc voltage 和 frequency 查表，输出 stator voltages 与 rectified dc current。[pdf:E04]（PDF 物理页 4，Eq. (14)–(20)、Fig. 5）
4. **interleaved boost AAVM。** 三路 chopper 用平均 duty interval \(\bar d_{1,k},\bar d_{2,k}\) 表示 CCM/DCM 过渡，将 inductor current 与 dc-link capacitor voltage 写成积分形式；其 input/output orientation 与 rectifier 后的 capacitor、VSI 前的 capacitor 相容。[pdf:E05]（PDF 物理页 5，Eq. (21)–(25)）
5. **crowbar 与 dual VSI AAVM。** grid fault 使能量无法及时送出时，crowbar 的平均电流按 duty 与 dc-link voltage 决定并耗散能量；dual VSI 在 \(dq\) frame 中用 modulation vector 和两路 ac current 的 power-factor angle 给出平均 ac voltage 与 dc current。[pdf:E05]（PDF 物理页 5，Eq. (26)–(31)）
6. **系统输出。** 模型输出 PMSG/rectifier 电流、dc-link voltage、crowbar current、PCC 电流及有功/无功。大信号时直接积分得到 transient；小信号时在 MATLAB/Simulink operating point 上数值 linearization，得到 \(2\times2\) 的 \(dq\) admittance matrix。[pdf:E07]（PDF 物理页 7，Eq. (33) 与 Section V-B）

论文报告 rectifier 的 averaging period 为 \(1/(6f_e)\)，boost 仍保留 carrier frequency 参数；验证使用 variable-step ode23tb。论文未报告统一固定步长执行、多速率 scheduler、algebraic-loop 打断方式、并行计算图、数值精度、FPGA/CPU code generation 或 memory footprint，因此这些不能从 Fig. 3、7–9 的 block diagram 自动推出。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有形式化数学，但不是一个从定理出发的证明；其主线是把每个物理模块改写成可连接、可积分或可查表的平均端口关系。

**1. 风轮与传动链。** 风轮捕获功率为

\[
P_m=0.5C_p(\lambda,\beta)\rho\pi R^2v_{\mathrm{wind}}^3,\qquad
\lambda=\frac{R\omega_m}{v_{\mathrm{wind}}}.
\]

这里 \(C_p\) 是 tip-speed ratio \(\lambda\) 与 pitch angle \(\beta\) 的非线性函数；公式的工程含义是风速通过三次方影响可捕获功率，而 control 通过 \(\lambda,\beta\) 改变功率系数。[pdf:E02]（PDF 物理页 2，Eq. (1)–(4)）

direct drive 无 gearbox，作者采用忽略 friction 的 one-mass model：

\[
\frac{T_m-T_e}{J}=\frac{d\omega_m}{dt},\qquad
\frac{d\theta_r}{dt}=\omega_r=p_n\omega_m,\qquad
T_m=\frac{P_m}{\omega_m}.
\]

它把能量不平衡直接变成 rotor acceleration；没有 two-mass shaft torsion，也没有 frictional damping。[pdf:E03]（PDF 物理页 3，Eq. (5)–(7)）

**2. six-phase PMSG。** phase-domain constitutive equations 为

\[
\mathbf v_{\mathrm{abc6}}=-\mathbf R_6\mathbf i_{\mathrm{abc6}}
+\frac{d\boldsymbol\lambda_{\mathrm{abc6}}}{dt},
\qquad
\boldsymbol\lambda_{\mathrm{abc6}}
=-\mathbf L_6\mathbf i_{\mathrm{abc6}}+\lambda_{\mathrm{pm}}\mathbf F_6(\theta_r).
\]

electromagnetic torque 由磁共能对 rotor angle 的偏导得到，外部接口则写为

\[
\mathbf v_{\mathrm{abc6}}
=-\mathbf Z_{\mathrm{eq}}\mathbf i_{\mathrm{abc6}}
+\mathbf v_{\mathrm{abc6,eq}},\qquad
\mathbf Z_{\mathrm{eq}}=\mathbf R_6+j\omega\mathbf L_6.
\]

直观上，internal electromagnetic state 被压到“等效电压源 + 等效阻抗”的端口形式，但 torque 与 rotor position 的耦合仍保留。[pdf:E03]（PDF 物理页 3，Eq. (8)–(13)）

**3. rectifier 的参数化平均。** 对每组三相绕组 \(k=1,2\)，平均 ac voltage vector 的幅值/相位由 dc voltage 和 \(\alpha_k,\phi_k\) 决定，平均 dc current 则为两组三相 current-vector magnitude 的加权和：

\[
\bar i_{\mathrm{dc}}^{\mathrm{rec}}
=\beta_1\lVert\bar{\mathbf i}_{\mathrm{qd},1}^{\mathrm{rec}}\rVert
+\beta_2\lVert\bar{\mathbf i}_{\mathrm{qd},2}^{\mathrm{rec}}\rVert .
\]

lookup coordinates 用

\[
z_k=\frac{\bar v_{\mathrm{dc}}^{\mathrm{rec}}}
{\lVert\bar{\mathbf i}_{\mathrm{qd},k}^{\mathrm{rec}}\rVert}
\]

表示 load condition，再把 \(\alpha_k,\beta_k,\phi_k\) 做成 \(z_k,f_e\) 的离散函数。它不是从单一 conduction mode 解析推导，而是由 detailed switching simulations 覆盖目标 operating range 后数值抽取。[pdf:E04]（PDF 物理页 4，Eq. (14)–(20)）

**4. boost、VSI 与 crowbar 的解析平均。** boost 的两个平均 interval 为

\[
\bar d_{1,k}=0.5(1+g_k/\Delta),\qquad
\bar d_{2,k}=
\min\left\{
\frac{2L_k\bar i_{L,k}f_\delta}
{\bar d_{1,k}\bar v_{\mathrm{dc}}^{\mathrm{rec}}},
1-\bar d_{1,k}
\right\},
\]

随后 Eq. (24)–(25) 把 \(\bar i_{L,k}\) 与 \(\bar v_{\mathrm{dc}}^{\mathrm{inv}}\) 写成积分量。VSI 的平均 ac voltage 与 modulation-vector magnitude、dc-link voltage 和 modulation angle 成比例；dc current 是两路 ac current magnitude 经 \(\cos\phi_k\) 加权后的和。crowbar 的平均电流为

\[
\bar i_{\mathrm{cb}}
=\bar d_{\mathrm{on}}^{\,2}\bar v_{\mathrm{dc}}^{\mathrm{inv}}/R_{\mathrm{cb}}.
\]

这些式子共同保证 dc-link energy path 在平均后仍可见。[pdf:E05]（PDF 物理页 5，Eq. (21)–(31)）

论文没有给出 AVM 误差上界、numerical stability theorem 或 lookup interpolation 的收敛证明；“准确”来自后续与 detailed model 的数值对比，而不是形式化保证。

## § 7 — 实验设计与结论

**问题 1：变风速下，平均模型是否保留机电动态？ → 实验 → 答案。** 作者构造 \(v_{\mathrm{base}}+v_{\mathrm{gust}}+v_{\mathrm{ramp}}+v_{\mathrm{noise}}\) 的 4.5 s wind profile：gust 在 \(0.5\)–\(1.5\) s，ramp 在 \(2.5\)–\(3.8\) s，峰值达到 \(13\ \mathrm{m/s}\)。当风速越过额定 \(12\ \mathrm{m/s}\)、active power 在约 3 s 超过额定 \(1.5\ \mathrm{MW}\) 时，pitch control 限制功率；proposed model 的 active power、dc voltage 和 dc-link current 与 detailed model 的 transient 基本重合。[pdf:E06]（PDF 物理页 6，Fig. 10 与 Section V-A.1）

**问题 2：grid fault 与 crowbar 动作能否被正确重现？ → 实验 → 答案。** 初始 wind speed 为 \(9\ \mathrm{m/s}\)；\(t=0.5\) s 发生 three-phase short circuit，ac voltage 下降 50%，\(t=1\) s 清除。crowbar 把 dc-link voltage 维持在约 \(1.3\ \mathrm{kV}\)，系统约再用 1 s 恢复。AVM [15] 在恢复期出现明显偏差，而 proposed model 能跟随 detailed model 的 dc-link 突变和短时波动；作者将差异归因于 [15] 未显式保留 PMSG 与 diode rectifier 动态。[pdf:E07]（PDF 物理页 7，Fig. 11 与 Section V-A.2）

**问题 3：速度提升有多大？ → 实验 → 答案。** 三个模型均在 MATLAB/Simulink 中用 ode23tb、maximum time-step \(10^{-3}\) s、relative/absolute tolerance \(10^{-4}\)，运行于 Intel Core i5-8265U @ 1.60 GHz。4.5 s 变风速 case 中，detailed model 用 \(821.83\) s、2,295,918 steps、average step \(1.96\ \mu s\)；proposed model 用 \(14.606\) s、54,083 steps、average step \(90.6\ \mu s\)，对应 CPU time 减少 98.22%、steps 减少 97.64%。2.5 s LVRT case 中，detailed、AVM [15]、proposed model 的 CPU time 分别为 \(594.4\)、\(0.3\)、\(1.1\) s；proposed model 比 [15] 慢，但比 detailed model 减少 99.81%。[pdf:E07]（PDF 物理页 7，Tables I–II 与 Section V-A.3）

**问题 4：小信号 admittance 是否仍可信？ → 实验 → 答案。** operating point 对应 \(9\ \mathrm{m/s}\)，frequency range 为 1–250 Hz，共 20 个离散点；detailed model 用每点 5 s 的 frequency sweep，两个 AVM 用 MATLAB/Simulink linear analysis。Fig. 12 与 Fig. B.1 显示 proposed model 的四个 \(dq\) admittance 元素在研究频段内与 detailed model 接近，而 AVM [15] 在非线性区域、尤其低频处有偏差。frequency-domain 总计算时间分别为 \(16810.36\) s、\(0.69\) s、\(1.276\) s，proposed model 对 detailed model 的 speed-up ratio 为 13174。[pdf:E08]（PDF 物理页 8，Fig. 12、Table III 与 Section V-B）[pdf:E09]（PDF 物理页 9，Fig. B.1）

**参数与外推边界。** rectifier 参数抽取覆盖 \(5\)–\(25\) Hz，dynamic impedance threshold 为 \(90\ \Omega\)，共执行 860 次、每次 0.2 s 的 detailed simulation，耗时约 1.2 CPU-hours；原型额定值为 1.5 MVA、1500 rpm、60 pole pairs，boost carrier 为 5 kHz、VSI carrier period 为 \(100\ \mu s\)。[pdf:E05]（PDF 物理页 5，Section V 开头）[pdf:E09]（PDF 物理页 9，Table A.1）

论文未报告不同机组容量、不同 converter topology、unbalanced fault、internal fault、参数老化、控制器切换、实时硬件、FPGA resource/timing 或 fixed-point error 的实验，因此结果不能外推到这些范围。

## § 8 — Take-aways

**5 句话：**

1. 这篇论文提供的是一台完整 direct-driven PMSG WECS 的异构 AVM，而不是只对某个 grid-side converter 做 reduction。[pdf:E02]（PDF 物理页 2，Fig. 1）
2. 它把模式复杂的 12-pulse rectifier 做成 PAVM，把 boost、VSI 与 crowbar 做成 AAVM，并保留 six-phase PMSG 的 phase-domain 动态。[pdf:E03]（PDF 物理页 3，Section IV）[pdf:E05]（PDF 物理页 5，Section IV-D–F）
3. 相比不含完整机侧动态的 AVM [15]，proposed model 在 LVRT 恢复和低频 admittance 上更接近 detailed model。[pdf:E07]（PDF 物理页 7，Fig. 11）[pdf:E08]（PDF 物理页 8，Fig. 12）
4. 代价是 rectifier 需要离线 detailed simulation 建表，且可信性受抽取域与原 detailed model 质量约束。
5. 论文证明了 MATLAB/Simulink 中的数值效率，但没有证明 FPGA 实时可实现性或给出误差上界。

**3 句话：** 关键不是“平均掉所有动态”，而是只平均 fast switching event，并保留决定能量交换、保护和 admittance 的端口动态。PAVM/AAVM 的组合在作者的变风速、LVRT 与 1–250 Hz case 中显著快于 detailed model，且比删去机侧动态的 AVM 更准确。它仍是有工作域的工程 surrogate，不是域外准确性的保证。

**1 句话：** 这篇论文说明，完整 WECS 的高效系统级模型应按元件物理选择不同 reduction，并把“是否仍保留关键能量路径”放在“是否最快”之前。

## § 9 — 最脆弱的假设

最脆弱的假设是：用 \(f_e\) 与 \(z_k\) 两类 coordinates 建出的 rectifier lookup table，已经覆盖后续 system-level study 会遇到的全部关键 conduction modes 与 terminal behavior。这个假设一旦失效，12-pulse rectifier 的 ac/dc power transfer、PMSG torque、dc-link charging 与 crowbar activation 都会沿同一能量路径同时偏差，整机“大信号 + 小信号都准确”的核心贡献便不再成立。

论文自己给出的边界很清楚：PAVM 的 applicability 取决于 detailed switching model 的准确度和数值抽取时考虑的 operating modes；internal faults 被排除，参数函数按对称 12-pulse rectifier 处理，最终表格只是由 frequency 与 dynamic impedance 唯一确定的离散点。[pdf:E04]（PDF 物理页 4，Section IV-C）作者用 \(5\)–\(25\) Hz、\(z\le 90\ \Omega\) 的抽取域和若干变风速、balanced three-phase fault 工况给了支持，但没有 unbalanced fault、器件参数漂移、winding asymmetry、域外低负载 DCM 或 lookup interpolation 误差证据。[pdf:E05]（PDF 物理页 5，Section V 开头）

因此，更准确的结论是“在已抽取并验证的 operating region 内表现良好”，而不是“对所有 direct-driven PMSG WECS 工况都准确”。

## § 10 — 最小复现实验

一周内最值得复现的是 **12-pulse rectifier PAVM 的 held-out accuracy 与 speed**，而不是从头复刻整台机组的所有 controller；后者有些控制细节被论文转引到文献 [21]，仅凭当前 PDF 无法完全重建。

- **数据与模型：** 用 Table A.1 中 1.5 MVA、1500 rpm、60 pole-pair PMSG 参数，按 Fig. 5 搭 detailed 12-pulse diode rectifier；在 \(f_e=5\)–25 Hz、\(z=0\)–90 \(\Omega\) 范围生成 \(\alpha,\beta,\phi\) lookup table，但预留一组未参与拟合的 \(f_e,z\) 网格点。[pdf:E04]（PDF 物理页 4，Fig. 5 与 Eq. (14)–(20)）[pdf:E09]（PDF 物理页 9，Table A.1）
- **实现：** 按 Fig. 7 构造 PAVM，使用相同 voltage/current inputs 驱动 detailed 与 parametric models；加入从 CCM 到轻载 DCM 的 load ramp，再加入 \(f_e\) ramp。
- **测量：** 比较每个 switching interval 的 averaged dc current、两组三相 fundamental voltage/current magnitude、dc energy error、最大瞬态偏差和 CPU time；另检查 lookup boundary 附近是否出现不连续。
- **预注册判断：** 这是复现者提出的判据，不是论文报告数字。若 held-out points 的 steady-state RMS relative error 不超过 3%、关键 transition 峰值误差不超过 5%，且 CPU speed-up 超过 50 倍，则支持“PAVM 在抽取域内兼顾准确与效率”；若域内出现超过 5% 的系统性误差、模式切换不连续或 power balance 漂移，则反驳该 claim。

这个实验最小，却直接检查整篇方法最不可替代的部分：解析法难以覆盖的 rectifier 是否真的能由有限维 lookup coordinates 可靠替代。

## § 11 — 最强反例设计

最强反例不是再换一个普通风速曲线，而是构造 **lookup representation 无法区分、但真实 switching trajectory 不同** 的两种状态。具体做法是：在相同 \(f_e\) 与相同瞬时 \(z_k\) 下，一组保持对称 balanced operation，另一组引入 winding/diode asymmetry 或 grid-side unbalanced sag 经 dc-link 传播出的二倍频能量脉动，并让负载越过 CCM/DCM boundary。若 \((f_e,z_k)\) 相同，当前 PAVM 会查到相同 \(\alpha_k,\beta_k,\phi_k\)，但 detailed rectifier 可能因相序、历史状态和不对称导通给出不同端口平均值。

实验同时记录 dc-link peak、crowbar on-time/energy、PMSG torque ripple、phase current unbalance 和 fault-clearance recovery。若 PAVM 与 detailed model 的误差足以跨过 crowbar threshold、current limit，或使一个模型判断稳定而另一个判断失稳，就不仅是局部波形误差，而是推翻“该 reduced model 可用于系统级 disturbance study”的机制级反例。这个攻击直接利用论文公开的对称性、internal-fault exclusion 和二维 lookup 假设。[pdf:E04]（PDF 物理页 4，Section IV-C）

论文没有实施这一反例；其成立与否仍然未知。

## § 12 — Follow-up Research Idea

在 power electronics 与 power-system EMT 领域，高影响工作通常需要同时证明端口/能量行为可信、极端工况可证伪、计算收益可重复，并说明实际部署边界；单纯再增加一个 lookup dimension 通常只是增量修补。

**候选想法：带可证伪 domain monitor 的 error-bounded adaptive AVM。** 研究目标不再是“做一个始终固定的 reduced model”，而是让模型在线判断自己何时仍可信：每个 converter module 同时输出端口量和一个基于 power-balance residual、lookup distance、conduction-mode consistency 的 error indicator；indicator 越界时，只把失配模块临时切换为更细的 switched/local subcycle model，恢复域内后再回到 AVM。

（a）驱动需求是：现有 PAVM 在有限抽取域内很快，但没有告诉仿真者何时已经越界；保护与 stability study 又恰好对少数极端片段最敏感。  
（b）研究价值在于把“平均模型是否可信”从离线经验判断变成仿真过程中可观测、可检验的 contract，并把高计算成本限制在少量真正需要的 time window。  
（c）可借鉴 adjacent fields 中的 a posteriori error estimation、trust-region/domain-of-validity detection 与 hybrid simulation；这些只是候选工具，本卡未做外部文献检索。  
（d）第一个证伪实验就是第 11 节的“相同 \((f_e,z)\)、不同不对称 switching history”case：如果 indicator 未报警却出现跨 protection threshold 的端口误差，想法立即失败。  
（e）它与本文的实质区别是改变了问题定义：本文追求一个离线抽取后固定使用的 AVM；候选研究追求一个能暴露自身失效并局部提升 fidelity 的自适应仿真器。

这个方向基于本文 PAVM 工作域与验证范围的证据约束，但相关工作尚未充分检索，因此不声称 novelty。
