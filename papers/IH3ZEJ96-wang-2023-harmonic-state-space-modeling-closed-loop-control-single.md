# Harmonic State-Space Modeling and Closed-Loop Control of Single-Stage High-Frequency Isolated DC–AC Converter

作者：Kaixuan Wang；Fengjiang Wu；Jianyong Su

出处：IEEE Transactions on Industrial Electronics, Vol. 71, No. 5

年份：2023（在线发表；卷期为 2024 年）

DOI：10.1109/TIE.2023.3281682

Zotero key：IH3ZEJ96（attachment：4XIQ2FT5）

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是一个“同一台变换器里存在多套时间尺度，却缺少统一模型和对应控制依据”的问题。对象是单相、单级、高频隔离 DC–AC converter：grid-frequency AC、switching-frequency AC 与 DC 分量在一次功率变换中相互耦合，传统定点线性化无法直接处理周期时变稳态，而只选一种 Fourier 基频的建模方法又会把另一时间尺度近似掉。作者因此要建立一个 frequency-domain linear model，既保留高频谐振变量，又显式表示低频谐波之间的耦合，再用该模型解释 DC 侧二倍网频纹波和 AC 侧谐波如何互相传递。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

工程上，这不是单纯追求“更漂亮的波形”。在单相 unity-power-factor 运行时，瞬时功率天然包含平均功率与 \(2\omega_g\) 脉动功率：

\[
P_g^*=\frac{V_m I_m^*}{2}-\frac{V_m I_m^*}{2}\cos(2\omega_g t),
\qquad
i_L=\frac{V_m I_m^*}{2v_{dc}}-\frac{V_m I_m^*}{2v_{dc}}\cos(2\omega_g t).
\]

这意味着 AC 侧即使只送基波功率，DC 侧也会出现 \(2\omega_g\) 电流纹波。增大母线电容 \(C_1\) 可以缓冲这部分功率，但会牺牲功率密度和寿命；若能从控制层面降低纹波，就可能减小对大电容的依赖。[pdf:E02]（PDF 物理页 2，Section II，Eq. (1)–(2)）[pdf:E03]（PDF 物理页 3，Fig. 3 后正文）

## § 2 — 前人工作与不足

论文把既有建模方法的不足分成两个不同问题。对 transformer current 这类纯 switching-frequency 状态，generalized averaging、基于开关行为的 discrete-time model 和 extended describing function 都能处理，但前两类方法依赖具体时域工作模态，extended describing function 则主要以有限谐波近似非线性项。对周期时变的 grid-frequency 稳态轨迹，dynamic phasor 与 harmonic state-space（HSS）可以把周期系统转到频域，并围绕周期轨迹建立 LTI 表示。困难在于：单独使用任一方法时，唯一 Fourier 基频迫使研究者对另一时间尺度作稳态近似，因此得到的是局部且不完整的多频行为描述。[pdf:E01]（PDF 物理页 1，Introduction）

控制方面，multiple PR controllers 能逐个瞄准已知谐波，但并联数量随目标频率增加；PI-RPC 对基波精确跟踪不利；PR-RPC 能兼顾基波跟踪，却依赖 grid frequency 与 sampling frequency；reduced RPC 虽降低存储并提高收敛速度，仍对网频波动敏感。作者据此把不足定义为：现有方案要么需要事先知道并逐个配置谐波频率，要么以周期长度和存储为代价，尚未形成从“统一谐波耦合模型”到“两侧谐波同时抑制”的闭环设计链。[pdf:E02]（PDF 物理页 2，Introduction 的 controller comparison 与 contributions）

这里需要限定证据强度：以上 prior-work 判断是作者在本文 Introduction 中的归纳，本卡没有另行读取被引论文，因此不把它们当作已独立复核的相关文献结论。

## § 3 — 重建作者的思考路径

可以把作者的推理重建为四步。第一，单相瞬时功率必然把 \(2\omega_g\) 分量带到 DC 侧；CF-DAB 拓扑虽然能借 \(C_1\) 缓冲，但“大电容换低纹波”不是高功率密度方案。第二，观察到 AC 侧基波、DC 母线偶次分量和 AC 侧更高奇次分量不是独立的，它们沿变换器的周期系数逐级搬移频率。第三，要验证这条链，不能只做 switching-period average，也不能只做 grid-frequency HSS：前者丢掉周期谐波耦合，后者难以直接容纳高频谐振状态。第四，把 extended describing function 用于 switching-frequency 状态，再把所得周期大信号模型送入 HSS，就能得到跨谐波 transfer matrix；控制器随后不再为每个谐波单独开通道，而让 ILC 对重复误差进行宽频补偿。[pdf:E03]（PDF 物理页 3，Section III-A）[pdf:E05]（PDF 物理页 5，Fig. 6 与 Section IV 开头）

这一路径是“基于论文证据的重建”，不是作者逐字陈述的研发日记。它的关键转折不是发明一种新拓扑，而是把两个各自解决一类时间尺度的问题的建模工具串成同一条可用于控制分析的链。

## § 4 — 核心 Intuition

核心 intuition 是：把高频谐振波形先压缩成随慢时间变化的正余弦系数，再用 HSS 展开这些慢变量的 grid-frequency harmonics，就能在一个线性频域算子里看见“某一频率的扰动会从哪里搬到哪里”。模型显示，AC 侧 \(p\) 次电流谐波主要与 DC 母线的 \(p\pm1\) 次谐波耦合，而 grid-voltage harmonic 主要把同阶分量带入 grid current；因此，两侧电流必须联合控制，且补偿器最好不要依赖事先枚举谐波频率。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Harmonic Coupling Characteristics）

## § 5 — 具体方法与完整 Pipeline

以“200 V DC 输入、311 V AC 侧电压幅值、50 Hz grid、50 kHz switching”的论文原型参数为例，完整 pipeline 如下。[pdf:E04]（PDF 物理页 4，Table I）

1. **拓扑与时间尺度。** DC 侧是 interleaved boost 与 H-bridge，AC 侧是 matrix converter 和 \(LC\) grid filter，两侧经 HF transformer 相连。每个 switching period 内把 \(v_g\) 近似为常数，用 duty \(d_1\)、内部 phase shift \(D_p\) 和外部 phase shift \(\phi\) 调节功率。[pdf:E02]（PDF 物理页 2，Fig. 1–2 与 Section II）
2. **高频变量降维。** 选谐振支路的 \(i_{Lr1}\)、\(v_{Cr1}\) 为高频状态，将各自 switching fundamental 写成 sine/cosine 两个慢变系数；同时取 \(v_{AB}\)、\(v_{CD}\) 的 fundamental approximation。这样避免逐开关模态列举，但也意味着高于基波的 switching harmonics 未进入该层模型。[pdf:E03]（PDF 物理页 3，Eq. (4)–(7)）
3. **组装周期大信号模型。** interleaved boost 用 state-space averaging，后级 DAB 用上述 extended describing function，DC bus 作为前后级桥梁；再加入 AC filter 状态，形成 \(\dot x(t)=A(t)x(t)+B(t)u(t)\)。状态覆盖 \(i_{Lr1s},i_{Lr1c},v_{Cr1s},v_{Cr1c},v_{C1},i_L\)，AC filter 另取 \(v_{cg},i_g\)。[pdf:E03]（PDF 物理页 3，Eq. (3)–(10)）
4. **HSS 与小信号化。** 把周期变量展开为以 \(\omega_g\) 为间隔的 harmonic vector，微分算子变为对角频移矩阵 \(N\)，周期乘法变为 block Toeplitz matrix。先由 \(X=-(A-N)^{-1}BU\) 求周期稳态，再加入 \(\Delta d_1,\Delta\phi\) 等小扰动，得到 harmonic transfer matrix。[pdf:E04]（PDF 物理页 4，Eq. (11)–(12) 与 Table I）[pdf:E05]（PDF 物理页 5，Eq. (13)–(14)）
5. **模型验证与耦合解释。** MATLAB/Simulink 扰动扫频覆盖 20 Hz–20 kHz；实验电源能力把实测扫频限制在 20–500 Hz。作者报告分析、simulation 与 experiment 基本一致，并据 harmonic transfer matrix 画出 Fig. 6 的跨频耦合路径。[pdf:E04]（PDF 物理页 4，Fig. 5 前正文）[pdf:E05]（PDF 物理页 5，Fig. 5–6）
6. **闭环控制。** DC 侧用 voltage/current dual loop 调 \(d_1\)，ILC 把 \(v_{C1}\) 纹波误差作为补偿；AC 侧用 PR 保证 50 Hz 基波零稳态误差，ILC 对剩余宽频误差补偿并调 \(\phi\)。作者用 Nyquist、收敛条件和 frequency response 分析稳定性与频率特性。[pdf:E06]（PDF 物理页 6，Fig. 7–9 与 Eq. (15)–(19)）[pdf:E07]（PDF 物理页 7，Fig. 10–11 与 Eq. (20)–(24)）
7. **实际执行。** 论文报告 MATLAB/Simulink 建模、实物 prototype 和基于 DSP 的在线控制；但未报告 DSP 型号、控制 sampling period、scheduler、数值表示、定点位宽、计算延迟、FPGA 映射、资源占用或 real-time step。因此不能据此声称模型或控制器已经在 FPGA 上实时实现。[pdf:E08]（PDF 物理页 8，Fig. 12 与 Experimental Verification）

## § 6 — 核心数学推导（无形式化数学则跳过）

第一层推导把 switching-frequency waveform 变成慢变量。对谐振电流与电容电压保留 fundamental：

\[
\begin{aligned}
i_{Lr1f}(t)&=i_{Lr1s}(t)\sin(\omega_s t)+i_{Lr1c}(t)\cos(\omega_s t),\\
v_{Cr1f}(t)&=v_{Cr1s}(t)\sin(\omega_s t)+v_{Cr1c}(t)\cos(\omega_s t).
\end{aligned}
\]

直观上，\(s/c\) 系数描述高频正弦在慢时间上的幅值与相位变化。把它们与桥臂电压的 fundamental approximation 代回谐振支路状态方程，就得到含 \(d_1,\phi,|v_{cg}|\) 的周期大信号模型。[pdf:E03]（PDF 物理页 3，Eq. (4)–(8)）

第二层推导是 HSS lifting。将每个周期信号改写为 harmonic coefficient vector 后，

\[
sX=(A-N)X+BU,\qquad
N=\operatorname{diag}(\ldots,-j2\omega_g,-j\omega_g,0,j\omega_g,j2\omega_g,\ldots).
\]

\(N\) 表示每个 harmonic bin 的频移，block Toeplitz matrix 则实现“周期系数与状态相乘等价于频域卷积”。因此，一个输入谐波不只出现在同一输出频率，还可能经非零 Toeplitz off-diagonal block 被搬移到相邻 harmonic bin。[pdf:E04]（PDF 物理页 4，Eq. (11)）

第三层是在周期稳态附近线性化：

\[
X=-(A-N)^{-1}BU,\qquad
s\Delta X=(A_s-N)\Delta X+B_s\Delta U.
\]

再用

\[
G(s)=\Gamma(C)\bigl(sI-\Gamma(A)\bigr)^{-1}\Gamma(B)+\Gamma(D)
\]

得到 harmonic transfer matrix。矩阵的 \(G_{m,n}\) 元素表示第 \(n\) 个输入 harmonic 到第 \(m\) 个输出 harmonic 的传递，因此 Fig. 6 中“\(i_g\) 的 \(p\) 次 ↔ \(V_{C1}\) 的 \(p\pm1\) 次”不是只凭 waveform 猜测，而是 off-diagonal transfer element 的物理解释。[pdf:E04]（PDF 物理页 4，Eq. (12) 与 small-signal model 正文）[pdf:E05]（PDF 物理页 5，Eq. (13)–(14) 与 Fig. 6）

控制层的 p-type ILC 更新律为

\[
\begin{aligned}
\varepsilon_{V1}(k+1)&=(1-\Lambda)\varepsilon_{V1}(k)+\Phi_i e_{V1}(k)+\Gamma_i e_{V1}(k+1),\\
e_{V1}(k+1)&=\Delta v_{C1}(k+1)-\varepsilon_{V1}(k+1).
\end{aligned}
\]

把 memory link 近似成 one-beat delay 后，论文给出

\[
G_{\mathrm{ILC}}(s)=
\frac{\Phi_i+\Gamma_i(1+sT_s)}
{s^2T_s^2+(1+\Lambda)sT_s+\Lambda},
\quad
|\Psi|=\left|\frac{1-\Lambda-\Phi_i}{1+\Gamma_i}\right|<1.
\]

后一个不等式是误差递推收敛的必要条件；它说明 forgetting factor 与 learning gains 不能任意选，但并不自动证明在未建模非线性、饱和、延迟和所有 operating point 下闭环都稳定。[pdf:E06]（PDF 物理页 6，Eq. (15)–(19)）

AC 基波环使用

\[
G_{\mathrm{PR}}(s)=K_P+\frac{K_R\omega_c s}{s^2+2\omega_c s+\omega_0^2},
\]

论文选 \(K_P=0.8\)、\(K_R=150\)、\(\omega_c=2~\mathrm{rad/s}\)、\(\omega_0=100\pi~\mathrm{rad/s}\)。PR 给 50 Hz 附近的零相移/高增益，ILC 再衰减低中频剩余误差；两者的职责不是重复的。[pdf:E07]（PDF 物理页 7，Eq. (21)–(24) 与 Fig. 10–11）

## § 7 — 实验设计与结论

**问题 1：HSS/extended-describing-function 模型能否预测真实 frequency response？** 作者在 MATLAB/Simulink 中从 20 Hz 扫到 20 kHz，并在实验平台上从 20 Hz 扫到 500 Hz；analysis、simulation 和实验点基本重合。作者还称 simulation sweep 的有效精度范围约到 switching frequency 的 40%。这支持“模型能描述本 operating point 下的低中频小信号响应”，但实验没有覆盖到 20 kHz，也没有给出统一的 magnitude/phase error 指标，因此不能外推为全频段精确。[pdf:E04]（PDF 物理页 4，Table I 后扫频设置）[pdf:E05]（PDF 物理页 5，Fig. 5 与对应正文）

**问题 2：两侧谐波是否按模型预测发生耦合？** 在 ideal grid 的 open-loop test 中，AC current amplitude 为 4 A，DC current average 约 3.4 A、\(2\omega_g\) ripple 约 3 A，AC current THD 约 3.18%，主要是第三、第五次谐波。再向 grid voltage 注入 10% third、5% fifth、5% seventh harmonic 后，AC current THD 变为约 5.32%，同阶谐波明显增加。这个实验支持“grid-voltage distortion 同阶进入 grid current，且 AC fundamental 与 DC \(2\omega_g\) ripple 共存”的定性路径。[pdf:E08]（PDF 物理页 8，Fig. 13 与正文）

**问题 3：两侧 ILC 分别启用时是否真的抑制目标谐波？** 在 nonideal grid 下，DC-side ILC 约在 2.5 s 启用，AC-side ILC 约在 5 s 启用。DC \(2\omega_g\) ripple 从约 3.5 A 降到 1.1 A，即报告抑制 68.6%；AC current THD 从约 3.67% 降到 1.98%，且 4 A reference 保持稳态零误差跟踪。这是论文最直接支持控制 claim 的证据。[pdf:E08]（PDF 物理页 8，Fig. 14）[pdf:E09]（PDF 物理页 9，Fig. 14 后正文）

**问题 4：相对 multiple PR 与 PR-RPC 的优势是什么？** 同一平台上的 Fig. 15 显示 multiple PR 有效降低第三、第五、第七次谐波，但对未配置频率的抑制受限；PR-RPC 能压制基频整数倍谐波，但需要保存更多 sampling data。该对比支持 PR-ILC 的宽频与较低存储主张，不过论文没有报告控制器的实际 cycle count、memory bytes、DSP utilization 或统一计算延迟，所以“实现复杂度更低”仍主要由结构分析而非实测资源数据支撑。[pdf:E08]（PDF 物理页 8，Table II）[pdf:E09]（PDF 物理页 9，Fig. 15 与正文）

**问题 5：动态过程是否可接受？** AC reference 由 4 A 变 6 A 或反向变化时，作者报告约 3 ms transient；AC voltage 在 280 V 与 311 V 间阶跃时，AC current regulation 约 1 ms；DC voltage 在 200 V 与 240 V 间作 \(\pm20\%\) 阶跃时，DC bus regulation 约 2 ms 且 AC current 基本不变。这支持该单台原型、所测 operating points 下的快速动态响应，但论文没有给出 overshoot、settling-band 定义、重复试验统计或极端工况。[pdf:E09]（PDF 物理页 9，Fig. 16–18 与正文）

## § 8 — Take-aways

**5 句话：** 第一，单相 1S-HF isolated DC–AC converter 的难点不是只有 \(2\omega_g\) ripple，而是 DC、grid-frequency 与 switching-frequency 状态在同一功率级内耦合。第二，论文用 extended describing function 压缩 switching fundamental，再用 HSS 展开 grid harmonics，得到可用于 small-signal frequency response 与 cross-harmonic analysis 的统一模型。第三，模型揭示 AC current 的 \(p\) 次谐波主要与 DC-bus 的 \(p\pm1\) 次谐波耦合，而 grid-voltage distortion 主要同阶进入 grid current。[pdf:E05]（PDF 物理页 5，Fig. 5–6）第四，PR-ILC 分工为“PR 管基波零误差，ILC 管不预先枚举频率的剩余谐波”，实物实验中 DC ripple 与 AC THD 都明显下降。[pdf:E06]（PDF 物理页 6，Fig. 7–9）[pdf:E09]（PDF 物理页 9，Fig. 14 后正文）第五，结果仍局限于一个 50 Hz、50 kHz prototype 与有限工况，尚无 FPGA、定点、资源和大范围 operating-envelope 证据。

**3 句话：** 这篇论文最有价值的部分，是把多时间尺度的 harmonic coupling 从波形现象变成可计算的 transfer matrix。控制器随后利用这一结构同时照顾 DC 与 AC 两侧，而不是逐个谐波打补丁。它证明了一个有效原型，但没有证明模型与控制在强非线性、功率反向、频率漂移和数字实现约束下仍成立。

**1 句话：** 先用 HSS 看清谐波如何跨端口搬移，再用 PR-ILC 在不枚举每个频率的情况下压低两侧电流谐波。

## § 9 — 最脆弱的假设

最脆弱的假设是：**实际 converter 在关心的 operating range 内，能够由“switching fundamental 的 extended describing function + 某一周期稳态附近的小信号 HSS”充分描述。** 这是整条贡献链的承重点：若 dead time、device nonlinearity、磁化支路、饱和、高次 switching harmonics、轻载/功率反向造成的工作模态变化或大扰动占主导，有限谐波模型的 off-diagonal transfer element 就未必还代表真实耦合，基于该模型的稳定性和控制解释也会失去依据。[pdf:E03]（PDF 物理页 3，Eq. (6)–(8) 的 fundamental approximation）[pdf:E04]（PDF 物理页 4，Small-Signal Model）

论文给出的支持是：在 Table I 的单一参数组上，analysis、switching simulation 与 20–500 Hz experimental sweep 基本一致，并用该平台完成了若干 steady-state 与 step tests。[pdf:E05]（PDF 物理页 5，Fig. 5）[pdf:E09]（PDF 物理页 9，Fig. 16–18）缺失的是：跨 load、power direction、phase-shift boundary、grid impedance、temperature、parameter drift 的模型误差包络，也没有把 higher switching harmonics 与 nonidealities 纳入残差分析。因此，“模型适用于其他 1S-HF isolated converters”是作者提出的可迁移判断，而不是本文实验已经证明的广泛结论。

## § 10 — 最小复现实验

一周内最值得复现的是“模型是否真的预测 cross-frequency coupling”，不必先搭完整功率硬件。

1. 在 MATLAB/Simulink 建立论文 Fig. 1 的 switching model，采用 Table I 的 \(v_{dc}=200~\mathrm{V}\)、\(V_m=311~\mathrm{V}\)、\(f_g=50~\mathrm{Hz}\)、\(f_s=50~\mathrm{kHz}\)、\(C_1=440~\mu\mathrm{F}\) 等参数；并按 Eq. (3)–(14) 实现截断 HSS model。[pdf:E04]（PDF 物理页 4，Table I 与 Eq. (11)–(12)）[pdf:E05]（PDF 物理页 5，Eq. (13)–(14)）
2. 在 \(\Delta v_g\)、\(\Delta d_1\) 或 \(\Delta\phi\) 上注入小幅 sinusoidal perturbation，至少扫描 20–500 Hz；同时记录同频输出与相邻 harmonic bins，例如 \(i_g(p\omega_g)\rightarrow V_{C1}((p\pm1)\omega_g)\)。
3. 预先规定支持标准，而不是事后看曲线：例如在 20–500 Hz 的主要耦合通道上，HSS 与 switching simulation 的 magnitude error 不超过 3 dB、phase error 不超过 \(15^\circ\)，且模型预测的 dominant off-diagonal channel 排名一致。论文没有给出这些阈值，它们是本复现实验的可证伪验收线。
4. 加入一个未建模条件，例如 1–2 \(\mu s\) dead time 或显著 magnetizing current，再重复扫描。若原模型在 nominal case 通过、在未建模 case 明显越界，就同时复现了论文的有效区间和第 9 节的脆弱边界；若 nominal case 也不通过，则核心建模 claim 被反驳。

## § 11 — 最强反例设计

最强反例不是再加一种低阶 grid harmonic，而是让 converter 穿过 **phase-shift 接近零、轻载到功率反向** 的 operating boundary，并保留实际 dead time 与 transformer magnetizing current。该条件会同时削弱 fundamental approximation、改变开关模态，并使“小扰动围绕单一周期轨迹”的前提最容易失效。

实验上，在同一硬件或高保真 switching model 中逐步把功率从额定正向降至零再反向；每个 operating point 都测量 \(d_1/\phi\rightarrow i_L,v_{C1},i_g\) 的 harmonic transfer matrix，并比较 HSS prediction。随后在相同点分别启用 PR-only 与 PR-ILC，观察 THD、\(2\omega_g\) ripple、closed-loop oscillation 与 saturation。若模型的 dominant coupling path 在边界附近改变或误差急剧增大，而 PR-ILC 的改善消失甚至激发振荡，那么“由该统一模型支撑、可普遍抑制两侧谐波”的解释被直接击中；若控制仍有效但模型预测失败，则改善更可能来自 generic error feedback，而非论文声称的模型—耦合—控制因果链。这个反例设计是基于模型适用条件的推断，不是论文已经实施的实验。

## § 12 — Follow-up Research Idea

**候选方向：从单 operating-point HSS controller 转向“带可验证误差包络的 operating-envelope harmonic control”。** 本领域的高影响工作通常不仅要求新模型或更低 THD，还要求严谨的 stability boundary、跨工况实验、工程可实现性和真实数字平台证据。本文尚未满足的需求是：控制器在 power reversal、grid impedance 变化、器件非线性和 parameter aging 下，仍要知道当前 harmonic model 是否可信，而不是默认同一组 Toeplitz coefficients 始终有效。

可以借鉴 robust control 的 structured uncertainty 与 LPV（linear parameter-varying）建模：离线在 power、voltage ratio、phase shift、temperature 等轴上辨识一组 harmonic transfer operators，同时为 truncation/nonideality 残差建立 frequency-dependent uncertainty bound；在线 controller 只在“模型证书仍有效”的区域内调度 PR-ILC gains，超出时转入明确的 robust fallback，而不是继续学习未知动态。它改变的不是多加一个补偿模块，而是把研究目标从“一个点上抑制谐波”改成“给出可验证的谐波控制适用域与失效检测”。

第一个证伪实验应使用完全留出的 operating points：在正向、零功率附近、反向以及不同 grid impedance 下测得 harmonic transfer matrix。若真实响应落在预测 uncertainty envelope 内，且 fixed controller 会失稳或性能越界的点能被在线 certificate 提前识别，而 scheduled controller 保持预先规定的 THD/ripple/stability 界限，则方向得到初步支持；若留出点频繁越界、certificate 无法提前预警，或性能收益只来自更高控制增益，则该想法被否证。本文 PDF 未做充分相关工作检索，因此这只是候选研究方向，不声称 novelty。
