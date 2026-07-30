# A Full-Feedforward Technique to Mitigate the Grid Distortion Effect on Parallel Grid-Tied Inverters

作者：Kiarash Gharani Khajeh、Farzad Farajizadeh、Davood Solatialkaran、Firuz Zare、Jalil Yaghoobi、Nadarajah Mithulananthan  
出处：IEEE Transactions on Power Electronics, Vol. 37, No. 7  
年份：2022  
DOI：10.1109/TPEL.2022.3146235  
Zotero key：FMFFDIHC  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个由“电能质量”和“并联系统稳定性”共同构成的问题：在多个 grid-tied inverter 并联接入同一 PCC 时，电网电压中的背景谐波会经每台逆变器的输出 admittance 转化为并网电流畸变；传统 full-feedforward（FF）虽能压低这种 admittance，却可能因数字控制延迟建模不准而损害弱电网下的稳定性。作者希望只在一台“target inverter”上实施 FF，就抵消整个 multiparallel grid-tied inverter（MPGTI）系统的总并联 admittance，同时维持强稳定性并抑制主导低次谐波。这也是论文摘要直接给出的核心 claim。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，首先是因为 LCL filter 擅长衰减 PWM 产生的高频开关纹波，却对来自电网电压的背景谐波拒斥能力有限；其次，多台逆变器并联后，逐台设计和部署 FF 会增加实现成本。论文指出，配电网中的畸变来源既包括变压器、旋转电机和电弧装置产生的低次谐波，也包括电力电子变换器产生的较高频谐波，并把最高约 9 kHz 的谐波视为不可忽略的实际背景。[pdf:E02]（PDF 物理页 2，Introduction）因此，这不是单纯把某几个 harmonic notch 调深的问题，而是要同时回答“怎样让聚合端口对电网谐波不敏感”和“怎样不因补偿本身引入失稳”。

## § 2 — 前人工作与不足

论文把既有方案分成两类。第一类是 controller harmonic compensation（CHC），即在目标谐波处向 current controller 加入 PR 或 PI 分量以提高 loop gain，从而减小输出 admittance。它的限制不是抽象的“鲁棒性不足”，而是当目标谐波超过 loop-gain cutoff frequency 时会降低 phase margin，甚至失稳；同时，它对不断变化的 grid impedance 敏感。第二类是 feedforward：测量 PCC 电压，经 feedforward transfer function 后叠加到 current controller 输出，以等效注入负 admittance。selective feedforward 适合少量目标频率，但目标增多时设计复杂；传统 FF 可以覆盖一段频率，却因没有准确处理 control-system delay 而可能失稳。[pdf:E02]（PDF 物理页 2，Introduction）

对于 MPGTI，既有做法还默认每台逆变器各配一套 FF。作者认为这在设计、部署和成本上不合理；更关键的是，传统 FF 在什么条件下把并联系统从强稳定推向临界稳定或失稳，此前没有被完整解析。论文的增量边界因此很清楚：它不是首次提出 grid-voltage feedforward，而是把问题提升到“聚合 admittance 由一台 target inverter 补偿”，并把 delay、admittance ratio 与 Nyquist/phase-margin 条件连起来。[pdf:E02]（PDF 物理页 2，contribution list）

## § 3 — 重建作者的思考路径

可以把作者的路径重建为四步。第一步，从端口观点看问题：电网电压谐波之所以进入电流，是因为 MPGTI 对 PCC 呈现非零总并联 admittance；因此最直接的目标不是逐个消除电流谐波，而是把聚合端口 admittance 做小。第二步，注意到并联 admittance 是可加的，所以不必要求每台逆变器分别产生一份负 admittance；理论上，只要一台 target inverter 注入的虚拟 admittance 等于系统总 admittance 的相反数，聚合端口就可被抵消。论文把这个理想关系写成

\[
Y_{f,k}(s)
=-\left(Y_{LT}(s)+\sum_{m=1}^{n}Y_{o,m}(s)\right)
=-Y_T(s).
\]

[pdf:E04]（PDF 物理页 4，Eq. (13) 及 Fig. 6）

第三步，作者发现理论抵消在数字控制器里遇到一个不可忽略的相位源：从采样、计算到 PWM 的总延迟 \(G_d(s)=e^{-\lambda T_s s}\)。传统实用 FF 省略这一项，等效负 admittance 便不再等于 \(-Y_T\)，而是多出随频率旋转的误差。第四步，不再追求不可实现的“全频完美抵消”，而是先用标量权重把 phase-margin 损失限制在强稳定边界内，再仅在第三、第五、第七和第九等主导谐波附近用 damped-resonant compensator 补回拒斥能力。[pdf:E05]（PDF 物理页 5，Eq. (19)-(24)）[pdf:E10]（PDF 物理页 10，Section IV-C 与 Eq. (56)-(65)）

## § 4 — 核心 Intuition

核心 intuition 是：把整个并联系统当成一个 Norton 端口，不需要每台逆变器都“变得理想”，只需要一台 target inverter 对外合成足够的负 admittance，使聚合 admittance 接近零。[pdf:E04]（PDF 物理页 4，Fig. 5-Fig. 6 与 Eq. (13)）但数字延迟使这份负 admittance 发生频率相关相移，所以作者用 \(W_f<1\) 主动放弃一部分取消深度来换取强稳定，再用窄带 resonant booster 只修复主导谐波处的缺口。方法奏效的关键不是“前馈更多”，而是把全频取消、稳定裕度和少数关键频率的谐波拒斥拆成三个可分别约束的对象。

## § 5 — 具体方法与完整 Pipeline

以论文验证的两台相同 single-phase inverter 并联系统为例，完整 pipeline 如下。

1. **建立单机端口模型。** 每台逆变器包含 damped PR current controller、数字控制延迟、inverter gain 和被动阻尼 LCL filter。作者将输出电流写成 Norton 形式 \(I_o(s)=I_s(s)-Y_o(s)V_{PCC}(s)\)，其中 \(I_s\) 是受参考电流驱动的短路电流源，\(Y_o\) 是从 PCC 看入的输出 admittance。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Eq. (1)-(9)）

2. **聚合系统 admittance。** 把所有 inverter 的 \(Y_{o,m}\) 与 local-load admittance \(Y_{LT}\) 相加得到 \(Y_T\)。指定第 \(k\) 台为 target inverter，并令它合成 \(Y_{f,k}=-Y_T\)。理想情况下，新的聚合 admittance 为零，grid current 只剩各 Norton current source 之和。[pdf:E04]（PDF 物理页 4，Eq. (13)）[pdf:E05]（PDF 物理页 5，Fig. 7-Fig. 8 与 Eq. (14)-(20)）

3. **得到可实现但有缺陷的 FF。** 理想 \(F(s)\) 显式包含 \(G_{d,k}^{-1}(s)\)，而传统实用实现把 \(\lambda\) 当作零，得到 \(F'(s)\)。此时总 admittance 变为 \(Y'_{TF}(s)=Y_T(s)(1-G_{d,k}(s))\)，括号内的 modification factor \(\Psi\) 决定 GVHRA（grid-voltage harmonic rejection ability，即电网电压谐波拒斥能力）。低频时 \(|\Psi|\) 小，拒斥好；频率升高后，拒斥变差并可能超过无 FF 情况。[pdf:E05]（PDF 物理页 5，Eq. (19)-(24)）

4. **用 stability-aware 权重限制副作用。** 作者提出

\[
F''(s)=W_f
\times\frac{Y_T(s)}{Y_{o,k}(s)}
\times
\frac{1+G_{L1,k}(s)G_{RC,k}(s)}
{G_{\mathrm{inv},k}(s)G_{L1,k}(s)G_{RC,k}(s)},
\]

其中 \(W_f\) 是非负实数。这个权重让残余 admittance 成为 \(Y''_{TF}=Y_T(1-W_fG_{d,k})\)，并用 admittance phase margin 推导出允许上界；选 \(W_{f\max}\) 可在强稳定约束下保留尽可能大的谐波拒斥。[pdf:E08]（PDF 物理页 8，Section IV-B 与 Eq. (45)）[pdf:E09]（PDF 物理页 9，Eq. (46)-(55)）

5. **为主导谐波增加窄带 booster。** 当 \(W_{f\max}\) 离 1 较远时，单纯降权会牺牲低次谐波拒斥。作者令 \(F'''(s)=F''(s)+F_R(s)\)，其中

\[
F_R(s)=\sum_{r=i}^{z}
\frac{A_r\omega_Ds}{s^2+\omega_Ds+\bar{\omega}_r^2},
\]

并在目标 \(m\omega_0\) 处令 \(F'''(jm\omega_0)=F(jm\omega_0)\)。damped-resonant compensator 同时提供实部和虚部，因而能匹配所需的复数补偿；论文实例选择 \(m\in\{3,5,7,9\}\)。[pdf:E10]（PDF 物理页 10，Eq. (56)-(65)）

6. **数字实现与执行平台。** 论文给出 \(T_s=25\,\mu s\)、\(\lambda=1\)，控制器在 Delfino F28379D C2000 control card 上由 MATLAB/Simulink 实现。[pdf:E12]（PDF 物理页 12，Table II）[pdf:E13]（PDF 物理页 13，Fig. 19 及 experimental setup 正文）论文没有报告定点位宽、量化误差、FPGA resource utilization、pipeline latency、并行调度、多速率划分、开关事件求解策略或 FPGA 映射，因此不能把它当作 FPGA 实时仿真或 FPGA 控制实现证据。除 sampling period 外，控制代码最坏执行时间与采样到 PWM 的分项时序也未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

推导的第一层是“端口取消”。Norton 模型把每台 inverter 的网侧响应拆为受控电流源和 admittance；target inverter 的 feedforward 支路等效为

\[
Y_{f,k}(s)=-F(s)G_{x,k}(s)Y_{o,k}(s).
\]

令其等于 \(-Y_T\)，即可得到包含真实 delay 的理想 \(F(s)\)，并使 \(Y_{TF}=Y_T+Y_{f,k}=0\)。物理上，这表示 PCC 电压谐波看不到可驱动的净并联通道，而不是说每台 inverter 的局部输出电流都没有动态。[pdf:E05]（PDF 物理页 5，Eq. (18)-(20)）

第二层是“为什么传统实用 FF 会失稳”。控制延迟的相位为 \(-\beta(\omega)\)，其中

\[
\beta(\omega)=\lambda_kT_{s,k}\omega,
\qquad
\Psi=1-G_{d,k},
\qquad
|\Psi|=2\sin\!\left(\frac{\beta(\omega)}{2}\right).
\]

因此，低频时 cancellation error 很小，但 \(\angle\Psi=(\pi-\beta)/2\) 会改变总 admittance 相位。作者把稳定性写成 \(Y_T/Y_g\) 的 Nyquist 问题，并定义

\[
PM_{\mathrm{rmin}}
=\frac{\pi}{2}-\angle Y_T(j\omega_{\mathrm{mpm}})-\alpha,
\]

其中 \(\alpha\) 是额外的鲁棒裕度；文中采用 \(30^\circ\) 作为推荐下限。传统 \(F'\) 会使 \(PM\)、\(PM_{\min}\) 和 \(PM_{\mathrm{rmin}}\) 各减少 \((\pi-\beta)/2\)，所以“低频拒斥最好”的区域反而可能是动态性能损失最重的区域。[pdf:E06]（PDF 物理页 6，Eq. (25)-(28) 与 stability categories）[pdf:E07]（PDF 物理页 7，Fig. 9 与 Eq. (29)-(44)）

第三层是“权重怎样给出强稳定边界”。加权后，

\[
Y''_{TF}(s)=Y_T(s)\left(1-W_fG_{d,k}(s)\right).
\]

要求 \(PM_{\mathrm{rmin}}\ge 0\) 可化为

\[
0\le W_f\le
\frac{\cos\theta(\omega_{\mathrm{mpm}})}
{\cos\!\left(\theta(\omega_{\mathrm{mpm}})-\beta(\omega_{\mathrm{mpm}})\right)},
\]

故作者取等号定义 \(W_{f\max}\)。这个式子的工程含义是：已知聚合 admittance 的最坏相位峰值、数字延迟和预留裕度后，计算“还能安全使用多少负 admittance”。权重减小会增加稳定余量，却会削弱 GVHRA；\(W_{f\max}\) 是作者选择的边界折中，而不是无条件的全局最优值。[pdf:E09]（PDF 物理页 9，Eq. (46)-(53)）

最后，resonant booster 在选定 \(m\omega_0\) 处补足 \(F''\) 与理想 \(F\) 的复数差值。这个设计恢复离散谐波点的 cancellation，但会在 target frequencies 附近引入额外相位变化，因此不能把它理解为“免费恢复理想 FF”；论文随后专门检查了这些窄带相移与 grid-admittance intersection 的关系。[pdf:E10]（PDF 物理页 10，Eq. (58)-(65)）[pdf:E11]（PDF 物理页 11，Fig. 12 与 Eq. (66) 附近正文）

## § 7 — 实验设计与结论

作者先固定一个可暴露失稳的测试台：两台相同 single-phase inverter，无 local load，\(L_g=0.9\,\mathrm{mH}\)，\(\alpha=30^\circ\)，由此得到 \(W_{f\max}=0.5452\)。Table II 还报告 \(L_1=L_2=1.1\,\mathrm{mH}\)、\(C=3.33\,\mu\mathrm{F}\)、\(V_{dc}=90\,\mathrm{V}\)、\(V_{ac}=50\,\mathrm{V_{RMS}}\)、峰值参考电流 \(3\,\mathrm{A}\) 和 \(T_s=25\,\mu s\)。注入的第三、第五、第七和第九次电压谐波幅值分别为基波的 4%、3%、2.5% 和 1.5%，相位分别为 \(0^\circ\)、\(90^\circ\)、\(180^\circ\) 和 \(0^\circ\)。[pdf:E11]（PDF 物理页 11，Section V 开头）[pdf:E12]（PDF 物理页 12，Table II-Table III）

按“问题 → 实验 → 答案”看，验证链分三组。

1. **传统 FF 是否真的在弱网失稳？** → MATLAB/Simulink 比较 Scenario I（无 FF、无电压谐波）、II（无 FF、有谐波）和 III（实用 \(F'\)、有谐波）→ \(F'\) 虽显著压低低次谐波，却出现高频振荡；Fig. 18 的 simulation THD 从 Scenario II 的 8.57% 升到 Scenario III 的 18.2%，与论文的 stability analysis 一致。[pdf:E12]（PDF 物理页 12，Scenario III 结果正文）[pdf:E13]（PDF 物理页 13，Fig. 15 与 Fig. 18）

2. **加权 \(F''\) 能否消除失稳？** → Scenario IV 在同一畸变和 \(L_g=0.9\,\mathrm{mH}\) 下只使用 \(W_{f\max}\) 加权 → 波形恢复稳定，simulation THD 为 3.61%，但低次谐波拒斥仍明显不如最终增强版。这个结果支持“权重换稳定”的机制，却也显示 \(F''\) 本身没有恢复理想电流质量。[pdf:E13]（PDF 物理页 13，Fig. 16 与 Fig. 18）

3. **resonant booster 能否同时恢复谐波拒斥？** → Scenario V 使用 \(F'''\) 并针对第三、第五、第七、第九次谐波补偿 → simulation THD 降至 0.42%，接近无谐波基准的 0.17%；实验中 Scenario V 的 THD 为 1.83%，接近实验基准 Scenario I 的 1.33%，并显著低于无 FF 的 10.32% 和仅加权 \(F''\) 的 4.83%。[pdf:E13]（PDF 物理页 13，Fig. 17-Fig. 18）[pdf:E14]（PDF 物理页 14，Fig. 20-Fig. 25）

硬件实验采用两套 full-bridge inverter、被动阻尼 LCL filter、C2000 microcontroller、current/voltage transducer 与 Chroma 61511 programmable AC source；实验波形与频谱用于复核 simulation 的相对趋势。[pdf:E13]（PDF 物理页 13，Fig. 19 与 experimental setup 正文）作者据此声称增强版在 target inverter 上既保持稳定又得到 desirable GVHRA。[pdf:E15]（PDF 物理页 15，Section V-B 末段与 Conclusion）

不得外推的范围同样明确：只验证了两台相同单相 inverter、一个固定 \(L_g\)、无 local load、固定采样延迟和四个指定低次谐波；三相实现、更多并联单元、异构 inverter、参数漂移、设备接入/退出、非整数或抖动 delay、宽频背景畸变、传感器噪声、饱和与控制器算力边界均未做实验报告。论文还指出，booster 在 target frequencies 附近可能带来约 \(+90^\circ\) 相移；对其案例，作者以“需 \(L_g>6\,\mathrm{mH}\) 才触发该交越，而按 SCR=10 计算的 \(L_{g\max}=2.7\,\mathrm{mH}\)”排除了风险，这个结论依赖该系统额定量与 grid 模型。[pdf:E11]（PDF 物理页 11，Fig. 12 与 Eq. (66) 附近正文）

## § 8 — Take-aways

**5 句话**

1. 论文把 MPGTI 的 grid-voltage harmonic 问题转化为聚合端口 admittance shaping，并让一台 target inverter 负责全系统补偿。[pdf:E04]（PDF 物理页 4，Eq. (13)）
2. 传统实用 FF 忽略数字 delay，低频 cancellation 虽深，却可能因 admittance phase rotation 把弱网系统推向失稳。[pdf:E07]（PDF 物理页 7，Fig. 9 与 Eq. (29)-(37)）
3. \(W_{f\max}\) 用明确的 phase-margin 约束把“补偿强度”限制在强稳定边界内。[pdf:E09]（PDF 物理页 9，Eq. (52)-(53)）
4. damped-resonant booster 再把第三、第五、第七和第九次主导谐波处的拒斥能力补回来。[pdf:E10]（PDF 物理页 10，Eq. (56)-(65)）
5. 两台相同 inverter 的 simulation 与实验支持这一机制，但没有证明异构、大规模或时变 MPGTI 中仍成立。[pdf:E14]（PDF 物理页 14，Fig. 20-Fig. 25）

**3 句话**

1. 这项工作的真正贡献不是又加一个 feedforward block，而是把“一台 inverter 合成全系统负 admittance”与 delay-aware stability bound 结合起来。
2. 权重解决稳定性、resonant booster 恢复选定谐波拒斥，二者缺一都会留下可观测缺口。[pdf:E12]（PDF 物理页 12，Table I）
3. 证据足以支持特定双机测试台上的 claim，却不足以支持对任意并联规模、任意 grid 和任意实现平台的普遍保证。

**1 句话**

用一台 target inverter 塑造整个 MPGTI 端口是一个有力的系统级思路，但它的实际可靠性取决于聚合 admittance 与数字 delay 能否被准确、持续地掌握。

## § 9 — 最脆弱的假设

最脆弱的假设是：target inverter 使用的 \(Y_T(s)\)、自身 \(Y_{o,k}(s)\) 和 \(G_{d,k}(s)\) 足够准确且在运行中近似不变，因此计算出的负 admittance、\(W_{f\max}\) 与 resonant booster 仍代表真实并联系统。只要其他 inverter 参数、并联数量、local load 或 delay 发生变化，\(Y_{f,k}\approx-Y_T\) 就会出现幅相误差；更严重的是，误差不仅降低谐波取消深度，还会改变用于 stability bound 的 \(\omega_{\mathrm{mpm}}\) 与 \(\theta(\omega_{\mathrm{mpm}})\)，使原本安全的 \(W_f\) 失去依据。这是基于 Eq. (13)、Eq. (45)-(53) 的证据推断，而不是作者显式验证过的失效结果。[pdf:E04]（PDF 物理页 4，Eq. (13)）[pdf:E09]（PDF 物理页 9，Eq. (46)-(53)）

论文为模型在一个标称双机系统中的有效性提供了 simulation 与硬件一致性证据，但测试对象始终是两台相同 inverter、无 local load、固定 \(T_s\) 与 \(L_g\)。[pdf:E11]（PDF 物理页 11，Section V setup）[pdf:E13]（PDF 物理页 13，experimental setup）它没有报告在线 \(Y_T\) identification、参数扰动 sweep、inverter hot-plug、delay jitter 或饱和下的鲁棒性，因此“强稳定 under any grid condition”应理解为给定模型与推导条件内的结论，而不是对任意实际 MPGTI 的无条件保证。

## § 10 — 最小复现实验

一周内最有信息量的复现，不需要重建完整硬件，可在 MATLAB/Simulink 中搭建两台相同 single-phase inverter 的 average/control model，并严格使用 Table II 的 \(L_1,L_2,C,V_{dc},V_{ac},T_s,\lambda\)、\(L_g=0.9\,\mathrm{mH}\)、\(\alpha=30^\circ\) 与 Table III 的四个电压谐波。[pdf:E12]（PDF 物理页 12，Table II-Table III）

实施四个工况：无 FF 的 distorted grid、传统 \(F'\)、加权 \(F''\) 和增强 \(F'''\)。同时记录 \(Y_{TF}/Y_g\) 的 Nyquist/phase margin、0-10 kHz grid-current THD、150/250/350/450 Hz 分量以及稳态波形。支持核心 claim 的最低标准是：\(F'\) 在该弱网设置下出现论文预测的高频振荡或负 phase margin；\(F''\) 恢复非负 robust margin；\(F'''\) 在不破坏稳定性的同时把四个 target harmonic 和 THD 明显压到 \(F''\) 以下，并重现 Scenario III/IV/V 的相对排序。[pdf:E07]（PDF 物理页 7，stability conditions）[pdf:E13]（PDF 物理页 13，Fig. 15-Fig. 18）

反驳标准也要预先固定：若在同一模型、同一 delay 和同一谐波输入下，\(F'\) 并未呈现稳定性劣化，或 \(F'''\) 的 target-frequency phase perturbation 使 phase margin 低于 \(F''\) 且产生持续振荡，则论文的关键机制或实现细节未被复现。不要只比较一张“看起来更正弦”的波形，因为那无法区分低次谐波下降和高频失稳。

## § 11 — 最强反例设计

最强反例不是再提高一个谐波幅值，而是让“聚合模型可准确集中补偿”这一前提系统性失效。构造四台异构 inverter：不同 LCL 参数、不同 \(T_s\) 和一台带随机一采样周期 delay jitter；运行中接入/切除 local load，并让一台非 target inverter 退出。让 grid impedance sweep 穿过 150、250、350、450 Hz 附近的 admittance intersection，再同时施加论文 Table III 的低次谐波和一组非目标 interharmonic。固定使用初始标称 \(Y_T\)、\(W_{f\max}\) 与 \(F_R\)，不允许在线重整定。

如果此时出现以下任一结果，便会直接挑战论文的核心机制：target inverter 的补偿使聚合 admittance 在某频段大于无 FF 基线；设备切换后 Nyquist locus 穿过 \(-1+j0\)；或 \(F'''\) 虽降低四个目标谐波，却因 target-frequency phase shift 激发并联系统振荡。这一反例有明确的替代解释：双机实验中的改善可能来自标称模型匹配，而不是“一台 target inverter 可稳健治理任意 MPGTI”。论文已经承认 resonant booster 在目标频率附近可能带来额外相移，但只用其双机系统的 \(6\,\mathrm{mH}\) 与 \(2.7\,\mathrm{mH}\) 比较排除风险，因此异构、时变交越正是最有力的攻击点。[pdf:E11]（PDF 物理页 11，Fig. 12 与 grid-inductance constraint）

## § 12 — Follow-up Research Idea

候选方向是把“精确抵消已知 \(Y_T\)”改写为“在线辨识并投影到可认证稳定集合的 aggregate admittance shaping”。未满足的需求是：真实 MPGTI 会扩缩容、接入异构设备并经历 delay 与 grid impedance 变化，离线计算的一台 target inverter controller 很难持续代表整个端口。相邻领域可借鉴 online system identification、robust control 与 passivity projection：target inverter 先用小扰动或运行数据估计局部频段内的 aggregate admittance，再只实现一个满足 passivity/phase-margin certificate 的有界补偿，而不是追求 \(-Y_T\) 的全幅精确取消。

它与本文的实质区别不是“多一个 adaptive block”，而是改变目标函数：从 cancellation depth 最大化改成在不确定集合内最小化最坏 grid-current distortion，同时把稳定性证书作为每次控制器更新的硬约束。第一个证伪实验应直接采用 §11 的四台异构、hot-plug、load switching 和 delay jitter 场景；若在线方案不能在每次拓扑变化后保持 Nyquist 安全边界，或其 150-450 Hz harmonic 指标不优于固定 \(F'''\)，这个方向就应被否决。由于本次严格只读指定 PDF、没有补检相关工作的全文，这只是证据约束下的候选研究方向，不声称 novelty。
