# State-Feedback Reshaping Control of Voltage Source Converter

作者：Federico Cecati；Rongwu Zhu；Sante Pugliese；Marco Liserre；Xiongfei Wang  
出处：IEEE Transactions on Power Electronics  
年份：2022  
DOI：10.1109/TPEL.2022.3191428  
Zotero key：6EBZEVAX  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。题名、作者、出处与 DOI 可定位到 PDF 物理页 2 的论文扉页。[pdf:E01]

## § 1 — 研究问题与重要性

这篇论文处理的是 grid-following Voltage Source Converter（VSC）接入弱电网后出现的低频振荡：SRF-PLL、dc-link voltage control（DVC）与 ac voltage control（AVC）不仅各自引入动态，还通过 \(d\)-\(q\) 轴和 ac/dc 两侧相互耦合。低 damping 会表现为过冲大、振荡衰减慢、稳定裕度小；当附近还有其他 converter 时，单台 VSC 的动态还会进入整个电力电子化电网的闭环。作者的核心问题不是“再加一个虚拟阻抗”这么简单，而是：能否在保留常规多环控制的同时，用一个 MIMO active damping feedback 同时整形这些耦合状态，并让工程师只需调一个在线系数即可启停或调节 damping。[pdf:E02]

工程价值在于，传统 SISO admittance reshaping 常把 \(d\)、\(q\) 两通道对称处理，难以补偿 PLL、DVC、AVC 造成的非对称和交叉耦合；dc 侧扰动也常被既有 ac-side 阻抗分析遗漏。论文因此把 VSC、完整主控制器和 grid Thevenin equivalent 一起纳入低频 plant，并在单机、并联系统、实验台和 HIL 中检验控制器。这里的“重要”限定在有平衡点、近/次同步低频动态占主导的 grid-following VSC；论文没有证明它可解决所有大扰动或所有电网阻抗形状。[pdf:E02][pdf:E03]

## § 2 — 前人工作与不足

论文梳理了三条既有路线。第一，降低 PLL bandwidth 可增加弱网 damping，但会牺牲快速电网暂态响应；改用 power synchronization 可改善弱网 damping，却可能在 stiff grid 中引入问题。第二，virtual admittance/impedance reshaping 把某个电压反馈经 \(K(s)\) 注入电流参考，设计直观且常用，但大多采用 SISO 视角，忽略 \(d\)-\(q\) cross-coupling。第三，已有 MIMO control 会重构整套 converter 控制，不过若 plant 没有把原有 PLL、DVC、AVC 的内部状态一起纳入，就不能直接针对“原主控制器造成的动态”做 reshaping。[pdf:E02][pdf:E03]

作者指出，symmetrical PLL 解决了 PLL 所致的部分轴间耦合，却仍忽略 DVC/AVC 和 ac/dc 耦合；传统 SISO feedback 因而只能有限增加 damping，在高 converter penetration、低 SCR 以及多 converter 并联时尤其可能不足。这个不足不是“之前没人考虑 MIMO”，而是既有简化为了可分析、可实施而丢掉了恰好决定低频振荡的耦合状态和 dc-side disturbance channel。[pdf:E02]

本卡不联网补充 2022 年后的相关工作。以上 prior-work 判断仅重述论文 Introduction 和参考文献所建立的边界，不据此声称该方法今天仍具 novelty。

## § 3 — 重建作者的思考路径

在不预设论文方案的前提下，可以把思路重建为四步。首先，弱网问题的直接可观测症状是某些闭环 eigenvalues 的 damping ratio 变小，而不是某个单独 PI 环“坏了”；这提示设计对象应是含主控制器在内的整体闭环 Jacobian。其次，SISO virtual admittance 对一个或两个端口量做对称反馈，而失稳机理来自多个内部状态、两个轴和 dc/ac channel 的共同作用，所以只整形端口 admittance 很可能控制权不足。再次，完整 nonlinear model 可在给定 operating point 上求 equilibrium point 并线性化；一旦得到 \((A,B)\)，经典 pole placement 就能直接指定低 damping modes 的位置。最后，直接在线修改一个 \(2\times 11\) gain matrix 对工程师不友好，因此应把复杂设计留在 offline，把在线操作压缩为一个 \(0\) 到 \(1\) 的 scalar knob。[pdf:E03][pdf:E04][pdf:E05]

这是“基于证据的思路重建”，不是作者逐句自述。它也揭示了方案的交换条件：获得更多 damping control authority 的代价，是依赖更完整的模型、更多状态以及可信的线性化。

## § 4 — 核心 Intuition

传统 virtual admittance 只从少量端口量出发，难以同时对付 \(d\)-\(q\) 非对称、外环耦合和 dc/ac interaction；full state feedback 则可以直接推动所有低 damping eigenvalues 到目标 damping locus。作者把复杂的 \(K\) 固定在 offline 设计阶段，再用 \(\sigma\) 缩放整个反馈，所以在线只需从“原多环控制”连续过渡到“full active damping”。[pdf:E05][pdf:E06]

## § 5 — 具体方法与完整 Pipeline

以一台接在弱网 Thevenin equivalent 后、由 dc-side source 注入功率的 L-filtered grid-following VSC 为例，完整 pipeline 是：

1. **定义低频 plant。** 主控制保留 DVC、AVC、SRF-PLL 和 inner current loop；grid 用 \(Z_g(s)=R_g+sL_g\) 表示。作者把 converter、主控制器与该 grid equivalent 一起作为 reshaping control 的 plant，而不是只看裸 power stage。[pdf:E03]
2. **建立 nonlinear state-space model。** inner current loop 先写成 Norton-equivalent state-space，再与 dc-link、outer loops 和 grid dynamics 合并。状态向量包含 converter current、dc voltage、DVC/AVC/PLL integrator states、PLL angle、current-controller internal voltage 和 grid current，共 11 个 states；reshaping input \(u=(u_d,u_q)^T\) 加到 current reference。[pdf:E04]
3. **求 equilibrium 并线性化。** 给定 hardware/control parameter array \(\Gamma\)、disturbance \(d^\*\) 和 reference \(r^\*\)，先用 Newton-Raphson 求 \(x_e\)；若 equilibrium 不存在，算法不继续。随后计算 Jacobian，得到 \(\dot x=Ax+Bu\)。[pdf:E04]
4. **离线选 poles。** 对每个 open-loop eigenvalue 计算 damping ratio \(\zeta_k\) 和 natural frequency \(\omega_{n,k}\)。低于阈值 \(\bar\zeta=0.4\) 的 mode 沿相同 \(\omega_n\) 移到 \(\zeta=0.4\) locus；已经高于阈值的 mode 不动，以减少 control effort。目标 pole set \(P\) 交给 Matlab `place(A,B,P)` 得到 \(K\)。[pdf:E06]
5. **在线注入 feedback。** 用 \(u=-\sigma K(x-x_e)\) 产生 \(d\)-\(q\) current-reference correction。直接测得 \(v_{dc}\)、\(i_g\)；PI integrator states 从主控制器内部取得；\(i_c\)、\(\delta\)、\(v_{cc}\) 由已有信号和 Eq. (4)-(5) 的简单运算生成。通常 \(\sigma=0\) 表示关闭，\(\sigma=1\) 表示 full active damping；运行中调整时作者建议渐变，以避免 abrupt transient。[pdf:E05][pdf:E06][pdf:E07]
6. **分析与验证。** 先看 eigenvalues 和 \(3\times 3\) disturbance-to-output frequency response，再跨 SCR、voltage、active power operating point 测 robustness；最后与 SISO admittance reshaping 比较，并进入单机实验台和三 VSC HIL。[pdf:E07][pdf:E08][pdf:E09]

从 EMT/FPGA 角度看，这不是 switching-level EMT solver。论文使用连续时间的低频 nonlinear/linearized model 做设计，实验/HIL 才包含实际或实时 converter 行为。switch/event handling、time integration algorithm、多速率调度、fixed-point format、FPGA mapping、resource utilization、parallel dependency graph 和 controller worst-case execution time 均未报告。唯一明确的实时执行信息是三 VSC Typhoon 402 HIL 使用 \(1\,\mu s\) step，converter switching frequency 为 \(2\,kHz\)；论文没有给出该 step 的误差收敛或资源时序报告。[pdf:E10]

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从 current loop 到 11-state nonlinear model

作者先把 current loop 写成 Norton-equivalent state-space：

\[
\begin{aligned}
\dot v_{cc}&=K_i i_c-K_i i_g,\\
\dot i_c&=-\omega_{cc}i_c+\omega_{cc}i_g^\*,\\
v_g&=K_p(i_c-i_g)+v_{cc}.
\end{aligned}
\tag{1}
\]

这里 \(i_c\) 是 current-loop 内部低通状态，\(v_{cc}\) 是 controller-side equivalent voltage，\(i_g^\*\) 是含 reshaping correction 的 current reference。它的直觉是：不追踪 PWM switching，而保留 current loop 在近/次同步频段对外看到的动态。作者再把它和 dc-link power balance、DVC、AVC、PLL、grid current equation 合并为

\[
\dot x=f(x,u,d,r),\qquad y=h(x,u,d,r),
\tag{2}
\]

其中 \(x\in\mathbb{R}^{11}\)、\(u\in\mathbb{R}^{2}\)、\(d=(i_{dc},e)^T\)、\(y=(v_{dc},i_g)^T\)。Eq. (4)-(5) 给出完整 nonlinear differential equations、\(dq\) rotation matrix \(T(\delta)\) 与 rotation matrix \(\Omega\)。这些公式及变量定义均位于 PDF 物理页 5。[pdf:E04]

### 6.2 equilibrium、linearization 与 feedback law

对给定 \(d^\*,r^\*\)，equilibrium 满足 \(f(x_e,0,d^\*,r^\*)=0\)。作者用 Newton-Raphson 从 flat start 迭代求 \(x_e\)，再在 \(x_e\) 处求 Jacobian \(A=\partial f/\partial x\)、\(B=\partial f/\partial u\)。如果 active power 超过 static transfer limit，或电压降得过低，equilibrium 可能不存在；这类 large-signal non-existence 不属于本文 pole-placement control 的处理对象。[pdf:E04]

核心 control law 是

\[
u=-\sigma K(x-x_e),\qquad 0\le \sigma\le 1.
\tag{6}
\]

因此 linearized closed-loop state matrix 为 \(A-\sigma BK\)。\(\sigma=0\) 恢复原多环控制，\(\sigma=1\) 使用完整 pole-placement feedback；中间值让 poles 沿图示轨迹移动。[pdf:E05]

对 \(\lambda_k=\alpha_k+j\beta_k\)，

\[
\zeta_k=-\frac{\alpha_k}{\sqrt{\alpha_k^2+\beta_k^2}},
\qquad
\omega_{n,k}=\sqrt{\alpha_k^2+\beta_k^2}.
\]

若 \(\zeta_k<\bar\zeta=0.4\)，算法保持 \(\omega_{n,k}\) 不变并设

\[
\alpha_k\leftarrow-\bar\zeta\omega_{n,k},\qquad
\beta_k\leftarrow \omega_{n,k}\sqrt{1-\bar\zeta^2}.
\]

然后用目标 poles \(P\) 求 \(K=\operatorname{place}(A,B,P)\)。工程含义是优先增加 modal damping，而不主动改变该 mode 的 natural frequency；高于阈值的 modes 保持原位，避免无谓增大 control effort。[pdf:E06]

### 6.3 disturbance-to-output frequency response

为同时观察 dc-side current disturbance 和 ac grid-voltage disturbance，作者定义

\[
W(s)=C\bigl(sI-(A-\sigma BK)\bigr)^{-1}E+F,
\tag{7}
\]

并按

\[
\begin{pmatrix}v_{dc}(s)\\ i_g(s)\end{pmatrix}
=
\begin{pmatrix}W_{dc}(s)&W_v(s)\\W_i(s)&W_g(s)\end{pmatrix}
\begin{pmatrix}i_{dc}(s)\\e(s)\end{pmatrix}
\tag{10}
\]

分块。off-diagonal blocks \(W_v,W_i\) 就是 ac/dc coupling 的显式表现。Fig. 7 显示增大 \(\sigma\) 会压低低 damping modes 对应的 sharp resonances，但 \(W_v\) 的低频 magnitude 也升高，意味着 ac disturbance 下 dc-voltage settling 可能稍慢。作者明确说明 \(W_g\) 依赖 \(Z_g\)，不能当作通常 impedance-based stability analysis 中的 converter output admittance。[pdf:E07][pdf:E08]

比较基线为

\[
u=B(s)Y_vv_g,
\tag{11}
\]

其中 \(Y_v\) 是对 \(d\)、\(q\) 通道相同的 virtual admittance，\(B(s)\) 是 band-pass filter。它与 Eq. (6) 的关键差别不是“有没有 feedback”，而是 SISO 只反馈 \(v_g\)，MIMO 还利用 \(v_{dc}\)、\(\delta\)、三个 outer-loop integrator states 等，并允许 \(u_d\)、\(u_q\) 两行 gain 不同。[pdf:E09][pdf:E11]

## § 7 — 实验设计与结论

### 问题 1：一个 nominal point 设计出的 \(K\) 能否跨 grid strength 和 operating point 工作？

**实验。** 作者按 SCR \(=1.3\) 设计 reshaping control，再把有效 SCR 扫到 \(1.1\)–\(4.5\)；另在 \(e=0.75\)–\(1.1\) p.u. 和 \(P^\*=0\)–\(1.2\) p.u. 上重新求 equilibrium/linearization、观察 eigenvalues。[pdf:E08][pdf:E09]

**答案。** 在所报告范围内，grid 变 stiff 时 damping 增加；\(e=0.75\) p.u. 时 minimum damping ratio 为 \(0.35\)，\(P^\*=0\) 时为 \(0.35\)，\(P^\*=1.2\) p.u. 附近约 \(30\,Hz\) modes 的 damping 降到 \(0.37\)。\(e<0.7\) p.u. 和 \(P^\*>1.2\) p.u. 未纳入，因为所用 model 下 equilibrium 不存在或超过 static transfer limit。因此这不是对 voltage collapse/large-signal loss of equilibrium 的验证。[pdf:E09]

### 问题 2：MIMO reshaping 是否比 SISO virtual admittance 提供更多 system-level damping？

**实验。** 三台 VSC 接在 SCR \(=1.3\) 的 grid 上，额定 active powers 为 \(1\)、\(1.2\)、\(0.8\,MW\)，switching frequency 均为 \(2\,kHz\)；仅 VSC 1 实施 damping。作者比较 no reshaping、SISO Eq. (11) 和 MIMO Eq. (6) 的全系统 eigenvalue trajectories。[pdf:E09]

**答案。** SISO 在 \(Y_v=10\,S\) 时最大报告 damping ratio 为 \(0.20\)，继续增大 \(Y_v\) 反而把 eigenvalues 推向右半平面；MIMO 在 \(\sigma=1\) 时达到 \(0.32\)。正文和结论称其“50% higher”，但按两个打印值 \(0.32/0.20\) 直接计算是 60% increase；论文没有解释舍入或采用另一未打印基准，因此本卡把“50%”视为作者报告、把算术差异标为未决，而不替作者修正。[pdf:E09][pdf:E10][pdf:E13]

### 问题 3：单机在 dc-side power step 下是否更快衰减？

**实验。** 实验台采用 \(600\,V\) dc link、\(1\,kW\) nominal active power 和 \(10\,kHz\) switching。weak-grid case 的 SCR 为 \(1.6\)，stiff-grid case 为 \(3\)；rectifier 关断造成 \(P_{dc}:1\,kW\rightarrow0\,kW\)。[pdf:E10][pdf:E11]

**答案。** Fig. 13 的 weak-grid waveform 标注 conventional control 的 oscillatory transient 约 \(1.2\,s\)，proposed control 约 \(0.42\,s\)；Fig. 14 的 stiff-grid 标注约 \(2.2\,s\) 对 \(0.4\,s\)。这些是图中 annotation，不是作者给出的统一 settling-time 定义；论文也没有误差条或重复试验统计。[pdf:E11]

### 问题 4：三机系统遇到 converter startup、voltage sag 和 frequency excursion 时能否保持稳定？

**实验。** Typhoon 402 HIL 以 \(1\,\mu s\) time step 实时仿真三台 \(2\,kHz\) switching 的 back-to-back wind-turbine VSC。测试包括 VSC 3 在 \(t=0\) startup、\(0.25\) p.u. symmetrical voltage sag 持续 \(0.5\,s\)，以及 frequency 增加 \(2\,Hz\) 持续 \(0.5\,s\)。[pdf:E10][pdf:E12][pdf:E13]

**答案。** 无 damping 的 startup case 在约 \(0.5\,s\) 后因 dc overvoltage/overcurrent 导致三机 trip；SISO 与 MIMO 均保持 startup 稳定，作者称 MIMO damping 略高。voltage recovery 与 frequency recovery case 中，SISO 出现 persistent oscillations，而 MIMO waveforms 衰减并保持三机稳定。[pdf:E10][pdf:E11][pdf:E12][pdf:E13]

这些结果支撑“在作者测试的 RL-grid、参数范围和扰动中，MIMO state feedback 比所选 SISO baseline 有更强 damping authority”。它们不支撑 FPGA resource/timing、任意 impedance spectrum、通信延迟、measurement noise、current saturation、fault ride-through 或没有 equilibrium 的 large-signal 稳定性；这些内容均未报告。

## § 8 — Take-aways

### 5 句话

1. 论文把 weak-grid low-frequency instability 当成由 PLL、DVC、AVC、dc/ac channel 和 nearby VSC 共同决定的 MIMO closed-loop mode 问题，而不是单一端口阻抗问题。[pdf:E02]
2. 它用 11-state nonlinear model 求 equilibrium、线性化，再通过 pole placement 把低于 \(\zeta=0.4\) 的 modes 移到目标 damping locus。[pdf:E04][pdf:E06]
3. 复杂 gain matrix \(K\) 在 offline 生成，online 只用 \(\sigma\in[0,1]\) 启停或缩放 feedback。[pdf:E05]
4. 在作者的 SCR、operating-point、实验台和三机 HIL 范围内，MIMO feedback 比所选 SISO virtual admittance 更能抑制 oscillation。[pdf:E08][pdf:E10][pdf:E11][pdf:E12][pdf:E13]
5. 结论依赖 low-frequency model、可获得的 11 个 states、有 equilibrium 的 operating region 和作者采用的 RL grid equivalent，不能直接外推到 switching-level EMT/FPGA 或任意 grid impedance。

### 3 句话

1. 这项工作的真正贡献是把 admittance reshaping 从少量端口反馈提升为对主控制器内部状态也有访问权的 MIMO state feedback。
2. 它的工程化亮点是 offline \(K\) 加 online \(\sigma\)，但工程风险也正来自模型、状态和实现误差。
3. 实验证据覆盖 dc/ac disturbances 和 multi-VSC interaction，却没有闭合 delay、noise、saturation、non-RL grid 与数字实现成本。

### 1 句话

这是一种以更完整模型和状态可见性换取更强 low-frequency damping authority 的 VSC reshaping control。

## § 9 — 最脆弱的假设

最脆弱的假设是：**按 nominal low-frequency RL-grid model 得到的 \((A,B)\) 与 11 个可用/可重建 states，足以让同一个 \(K\) 在真实实现和 grid variation 下保持预期 pole-placement authority。** 如果 state reconstruction 含有 delay/noise/bias，current reference 遇到 saturation，或 grid 在相同 fundamental SCR 下具有未建模的 resonant/active impedance，闭环就不再是设计时的 \(A-\sigma BK\)；此时“大 gain、多状态 feedback”可能不只失去优势，还可能激励被平均模型删掉的 modes。

论文给出的正面证据是：\(K\) 在 SCR \(1.1\)–\(4.5\)、有限 voltage/power operating region、单机实验台和三机 HIL 中保持 damping；部分 states 直接测量，部分从主控制器 integrators 或简单关系生成。[pdf:E06][pdf:E08][pdf:E09][pdf:E10] 缺口是：没有 measurement noise、quantization、sampling/actuation delay、state bias、current saturation 或非 RL impedance-shape sweep；Typhoon 的 \(1\,\mu s\) network step 也不等于证明实际 control implementation 没有 delay。[pdf:E10] 这是基于证据的批评，不是论文已经观察到的 failure。

## § 10 — 最小复现实验

一周内可做的最小复现应验证“state-feedback 确实比 SISO baseline 拥有更多 modal damping authority”，而不是复制全部实验台。

1. 在 Matlab/Simulink 或 Python control environment 中实现 Eq. (1)-(5) 的 single-VSC low-frequency model、RL Thevenin grid、DVC/AVC/PLL 和 equilibrium Newton-Raphson；先使用 Table I 的 \(690\,V\)、\(4\,MW\)、\(1200\,V\) dc link、\(22\,mF\)、\(0.1\,mH\) 和 \(2\,kHz\) 参数。[pdf:E08]
2. 在 nominal \(e=1\) p.u.、\(P^\*=1\) p.u. 下线性化，按 Fig. 6 把 \(\zeta<0.4\) 的 modes 移到 \(\zeta=0.4\)，用 `place` 求 \(K\)。论文没有完整报告全部 main-control gains 和 single-VSC \(K\)，因此必须公开自己的 tuning；结果只能算 mechanism reproduction，不能声称 exact numerical replication。
3. 比较 \(\sigma=0\)、SISO Eq. (11) 和 MIMO Eq. (6) 的 minimum damping ratio、Fig. 7 四个 transfer blocks 的 resonance peak，以及一个小 dc-current step 的 settling/overshoot。
4. 把 SCR 从 \(1.1\) 扫到 \(4.5\)，并至少抽查 \(e=0.75,1.0,1.1\) p.u.。若 MIMO 在 nominal case 不能把目标 modes 提到约 \(0.4\)，或在同等 current-reference RMS/control effort 下并不优于 SISO，则核心 mechanism 未复现；若只在自选 tuning 下成功而无法对应论文曲线，应报告“qualitative support”，不能报告“reproduced paper numbers”。

## § 11 — 最强反例设计

最强反例不是把 voltage 降到作者已经排除的“无 equilibrium”区域，而是保持相同 operating point 和 fundamental SCR，却改变 grid impedance 的频谱形状。构造两个 HIL grids：A 是论文假设的 RL Thevenin equivalent；B 在相同 \(50/60\,Hz\) SCR 和 \(R/X\) 下加入 cable/filter resonance 或一个受控 converter 的 active impedance，使近/次同步频段出现额外 phase lag。两者使用同一个按 A 设计的 \(K\)，再叠加有量纲、逐级扫描的 sensor/actuation delay，并限制 current-reference magnitude。

测量 minimum damping ratio、unmodeled-mode participation、current saturation time 和 dc/ac disturbance response；同时保留 SISO baseline。若 MIMO 在 A 中优于 SISO、却在 B 中率先产生右半平面 mode 或更大 sustained oscillation，而 SISO 仍稳定，就能反驳“按最大 grid impedance/最低 SCR 初始化即可覆盖 grid variation”这一最强工程外推。这个反例把“grid strength”与“grid impedance shape”分开，避免只重复作者已经做过的 scalar SCR sweep。

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty：从固定 RL model 的 pole placement，改写为“带在线可证伪安全证书的 impedance-spectrum-aware reshaping”。**

（a）未满足的需求是：实际 multi-converter grid 可在相同 SCR 下呈现完全不同的 frequency-dependent impedance、delay 和 saturation，而固定 \(K\) 的安全范围目前只由离线点扫和实验示例说明。  
（b）电力电子控制领域更看重可解释的稳定边界、严格 HIL/实验验证和可部署性；若控制器能在每次启用 \(\sigma\) 前给出“当前测得 impedance set、delay bound 和 saturation bound 下仍满足最小 damping”的 certificate，它改变的是问题目标，从“给 nominal model 配 poles”转为“只在可证明安全的动态集合内释放 damping authority”。  
（c）可借鉴 robust control 的 structured singular value、Integral Quadratic Constraints（IQC）、gain scheduling，以及 online impedance identification；这些工具用来表达 frequency-shaped uncertainty，而不是只用一个 SCR scalar。  
（d）第一个证伪实验就是第 11 节的 same-SCR/different-spectrum HIL pair：如果 certificate 判为安全而系统仍产生 unstable mode，想法立即失败；如果 certificate 过度保守到几乎总把 \(\sigma\) 压到零，也不具工程价值。  
（e）它与本文的实质区别是：本文 offline 计算一个 \(K\)，用 \(\sigma\) 调强度并凭有限范围验证 robustness；候选方向把 uncertainty set、digital implementation constraints 和 online enable/disable decision 变成控制目标本身，而非事后 robustness test。
