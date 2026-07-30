# Modeling of Inverter-Based Resources for Power System Harmonics Studies

作者：Wilsun Xu；Roberto Langella；Antonio Bracale；Yuanyuan Sun；Kuo Lung Lian；Yang Wang；Jason David  
出处：IEEE Transactions on Power Delivery, Vol. 40, No. 1, February 2025, pp. 166–177  
年份：2024（在线发表）；卷期出版于 2025 年  
DOI：10.1109/TPWRD.2024.3486566  
Zotero key：2RVAK9MA  
证据说明：

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样让某一种 inverter 的 THD 更低”，而是更靠前、也更基础的问题：在电网谐波潮流与并网评估中，应该用什么等效电路表示 voltage-source converter（VSC）型 inverter-based resource（IBR），以及怎样从真实设备取得这个模型的参数。作者把研究频段限定在工程中最常遇到的低阶至第 50 次谐波，面向 IEEE Std. 1547 与 IEEE Std. 2800 所约束的配电、输电 IBR 并网场景；论文性质是由 IEEE Harmonics Modeling, Simulation and Assessment Task Force 汇总研究与实测证据形成的行业应用型 tutorial，而不是提出单一新控制算法。[pdf:E01]（PDF 物理页 1，Abstract、Introduction）

这个问题重要，是因为传统 line-commutated converter（LCC）通常可近似成谐波电流源，但 VSC 通过 2 kHz 或更高频率的 PWM 把 DC 电压转换到 AC 侧，低阶谐波生成机理、对背景谐波的响应以及多机相位关系均不同；若继续把 VSC-IBR 当作“已知谐波电流源”，模型中最关键的端口阻抗、正负序差异与可能的谐振路径会被漏掉。[pdf:E02]（PDF 物理页 2，Section II、Fig. 1–2）

作者的核心工程判断是：IBR 电站真正值得警惕的往往不是单台合格 inverter 主动注入了多大的低阶谐波，而是其频率相关阻抗、可能的负电阻或容性区间与场站并联电容、电网阻抗共同造成谐振，从而放大已有背景谐波；与此同时，多台 unit 的等效源相角并不稳定，PCC 处的汇总应考虑概率性而非简单算术相加。[pdf:E10]（PDF 物理页 10，Section VII-A）[pdf:E11]（PDF 物理页 11，Conclusion）

## § 2 — 前人工作与不足

最早、也最容易误用的先例是 LCC 的谐波电流源模型。LCC 的换相与工频电压同步，因此其主要谐波电流的相位与端电压存在稳定关系；VSC 的高频载波相位在 unit 之间不必同步，前端 L/LC/LCL filter 又会显著衰减 PWM 产生的高频电压谐波，所以把 LCC 的经验模型直接移植到 VSC 会错认“主导参数”。[pdf:E02]（PDF 物理页 2，Section II–III-A）

针对 VSC，本论文梳理了四条既有模型路线。第一，时域模型（TDM）能较完整地表示开关与控制，但与频域 network harmonic solver 接口困难且计算量较高。第二，小信号 impedance model 通过单频扰动得到 \(Z(f)=V_g(f)/I_g(f)\)，适合 resonance 或 stability 分析，却只描述“一个频率的扰动在同一频率上的响应”，不能直接覆盖多个背景谐波同时存在时的跨频耦合。第三，frequency-coupling matrix（FCM）以及测量得到的常矩阵 \([M]\)、\([W]\) 可以描述耦合，但前者需要开关时刻并数值求解，后者仍需较多矩阵参数。第四，Extended Harmonic Domain、Harmonic State Space 与 Dynamic Phasor 模型把瞬态波形写成随时间变化的 harmonic phasor，在线性化后得到耦合 admittance/impedance；表达力强，但公式复杂，通常只能数值求取。[pdf:E05]（PDF 物理页 5，Section IV-B、Eq. (3)–(6)）

更接近本文落点的是已有 sequence-domain coupled impedance 结果：完整模型含正序、负序同频对角项以及 cross-coupling、cross-sequence 非对角项。其不足不是理论上不完备，而是对行业 study 来说参数过多、OEM 内部控制传递函数常不可得，而且外环与 power loop 带来的精度改善未必足以抵消建模成本。既有仿真与实测还提示非对角项通常远小于对角项，front-end filter 与 inner current loop 才是决定低阶阻抗的主要因素。[pdf:E06]（PDF 物理页 6，Eq. (7)–(8)、Fig. 5）

论文因此不是简单宣布“以前没有模型”，而是把上述模型压缩成一个可测量、可交付给频域谐波网络求解器的工程接口：每个谐波、每个序别使用一个 Norton current source 与一个频率相关 impedance；只有当实测证据显示耦合不可忽略时，才需要回到更完整的 coupled model。[pdf:E07]（PDF 物理页 7，Section V-A、Fig. 6）

## § 3 — 重建作者的思考路径

第一步，从能量转换结构而不是沿用旧设备类别出发。VSC 的开关桥先产生 \(V_{\mathrm{con}}\)，再经 front-end filter 与 unit transformer 接入电网，因此 PWM 侧最自然的物理图像是“谐波电压源在滤波阻抗之后”，不是理想电流源。以 \(f_c=1980\ \text{Hz}\)、\(f_1=60\ \text{Hz}\) 的同步 PWM 例子看，最大谱线在第 33 次附近，而第 31、35 次也是主要分量；它们在到达 grid terminal 前又经过 LCL/transformer 衰减。[pdf:E02]（PDF 物理页 2，Fig. 1–2、Section III-A）

第二步，解释为什么低阶端口行为主要由“响应”而不是“主动生成”决定。死区、DC-link ripple、unbalance 与器件非理想会产生第 3、5、7 次等低阶 non-characteristic harmonics，但论文汇总的量级较小；例如按 \(T_d/T_c=1\%\) 的典型死区估计，第 5 次约为 0.64%，而 2% 端电压不平衡下 VSC-IBR 的第 3 次电流报告范围为 0.8%–1.20%。[pdf:E03]（PDF 物理页 3，Eq. (2)、Table I）[pdf:E04]（PDF 物理页 4，Table II、Section III-C）

第三步，把问题改写为“给定多频端电压，端电流怎样变化”。完整答案是一个受 DC link、inner/outer control loop 与 power loop 影响的 coupled multi-frequency mapping；但已有模型与实验共同指向矩阵近似对角占优，即同频、同序的响应远大于 cross-frequency 与 cross-sequence 响应。[pdf:E05]（PDF 物理页 5，Fig. 4、Eq. (3)–(6)）[pdf:E06]（PDF 物理页 6，Eq. (7)–(8)、Fig. 5）

第四步，保留小量但不可预测的主动谐波源。若完全删掉源项，只剩 \(Z=V/I\)，就无法覆盖死区、厂商特有非理想、较小 DC capacitor、过低 carrier frequency 或不足的 filter；而这些非理想又很难由 EMT simulation 忠实生成，数值算法本身甚至可能产生与真实小谐波同量级的“fake harmonics”。因此作者以 Thévenin/Norton 等效同时容纳“主导 impedance response”和“小但应实测的 emission source”。[pdf:E07]（PDF 物理页 7，Section V-A、Fig. 6）

最后一步，把理论模型变成可执行的参数辨识。对同一 operating point 施加两个小扰动状态，用 \(\Delta V/\Delta I\) 消去未知 current source 得到 \(Z(h)\)；若 grid simulator 近似理想电压源，可在无谐波背景状态直接测得 \(I_s(h)\)；若 \(I_s\) 已证实很小，再退化到单状态 \(V/I\) frequency scan。[pdf:E07]（PDF 物理页 7，Fig. 7、Eq. (9)–(10)）[pdf:E08]（PDF 物理页 8，Eq. (11)–(13)、Fig. 8）

## § 4 — 核心 Intuition

在工程关心的低阶谐波上，一个正常设计的 VSC-IBR 更像“正、负序各有一条频率相关阻抗的支路”，而不像 LCC 那样由确定电流源主导；front-end filter 决定大部分响应，控制环主要修正低阶部分。[pdf:E06]（PDF 物理页 6，Fig. 5、Eq. (8)）为了不把真实设备的死区、DC-link 与厂商非理想丢掉，再在该阻抗旁并联一个小的、相角不确定的 Norton current source，并通过物理测试而非理想化仿真辨识它。[pdf:E07]（PDF 物理页 7，Fig. 6）只要 cross-coupling 保持弱，这个模型就以很少参数保留了谐振评估真正需要的端口行为。

## § 5 — 具体方法与完整 Pipeline

下面用“对一台 grid-following PMSG inverter 建立第 5、7、11、13 次谐波模型”为例重建完整 pipeline。

1. **确定 study 边界。** 输入是给定 fundamental operating point \((V_{g1},I_{g1})\) 下，terminal 的多频 harmonic voltage phasor \([V_g]\)；输出是对应 harmonic current phasor \([I_g]\)。论文主要讨论 \(1<h<f_c/f_1-2\) 的低阶谐波响应，并面向最高第 50 次的工程 study；subsynchronous、near-synchronous dynamic mode 不在本模型范围内。[pdf:E05]（PDF 物理页 5，Eq. (3)）[pdf:E07]（PDF 物理页 7，Section IV-C 末）
2. **先采用完整语义，再决定降阶。** 理论接口是正、负序 coupled impedance block matrix：对角块描述同序同频，非对角块描述 harmonic cross-coupling 与 cross-sequence。若测量或既有设计证据表明非对角项远小于对角项，则将每个 \(h\) 简化为 \(I_{gh+}\approx V_{gh+}/Z_{h+,h+}\)、\(I_{gh-}\approx V_{gh-}/Z_{h-,h-}\)。[pdf:E06]（PDF 物理页 6，Eq. (7)–(8)）
3. **建立实用 Norton equivalent。** 对每个谐波与序别放置 \(Z_+(h)\) 或 \(Z_-(h)\)，并联 \(I_{s,+}(h)\) 或 \(I_{s,-}(h)\)。阻抗承载由 filter 与 controller 决定的背景谐波响应，current source 承载 characteristic、non-characteristic 及其他 device-specific emission；其相角不宜被当作对所有 unit 稳定的确定量。[pdf:E07]（PDF 物理页 7，Fig. 6、Section V-A）
4. **以两状态小扰动测阻抗。** 保持 fundamental operating point 近似不变，在 state 1 与 state 2 分别记录 terminal \(V_{m1}(h),I_{m1}(h)\) 和 \(V_{m2}(h),I_{m2}(h)\)。作者示例建议切入或切出约 3% 的第 \(h\) 次 test voltage，然后以 \(Z(h)=\Delta V_m(h)/\Delta I_m(h)\) 求解；正序、负序 perturbation 要分别重复。[pdf:E07]（PDF 物理页 7，Fig. 7、Eq. (9)–(10)）
5. **在可证实时简化测试。** 若 grid simulator 的 internal impedance 近似为零，state 1 的 harmonic terminal voltage 近似为零，此时 \(I_s(h)=-I_{m1}(h)\) 可直接得到；若 \(I_s(h)\) 相对 state 2 current 很小，阻抗还可用一状态 \(Z(h)\approx V_{m2}(h)/I_{m2}(h)\) frequency scan 得到。[pdf:E08]（PDF 物理页 8，Eq. (11)–(13)）
6. **交叉检查参数。** 将测得的 impedance profile 与 L/LC/LCL filter 的理论 profile 比较；高阶处若显著偏离，应先检查测量、序分解与 OEM 数据。若无法测试实际 unit，可以用包含控制的 EMT/HIL simulation 估计 impedance，但 current source 应尽量来自 physical unit，因为小量非理想谐波可能未被仿真表示。[pdf:E07]（PDF 物理页 7，Section V-A）[pdf:E08]（PDF 物理页 8，Fig. 8–9）
7. **交付给 network solver。** 输出是按 harmonic order 与 sequence 编排的 \(Z_\pm(h)\)、\(I_{s,\pm}(h)\) 及适用 operating region。频域网络求解器据此计算 background harmonic amplification、PCC distortion 与 resonance；多台 unit 的 source phase 不能默认同相，应采用概率性汇总。[pdf:E11]（PDF 物理页 11，Conclusion）

这不是一篇 EMT 离散化或 FPGA implementation 论文。它未报告 switch/event handling 算法、time stepping、多速率调度、计算依赖图、并行划分、fixed-point/浮点数值表示、FPGA resource/latency、实时步长或 FPGA 执行平台；文中仅说明 EMT-based computer simulation 与 hardware-in-the-loop 可作为实际 unit 无法测试时的 impedance 估计手段，不能据此推断任何具体实时实现性能。[pdf:E07]（PDF 物理页 7，Section V-A）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学不是从 switching differential equation 完整推到底，而是分成“谐波生成机理”“多频端口模型”“可测的降阶参数”三层。

**1. PWM 谐波相位为什么在 unit 之间不稳定。** 对同步 PWM，作者把 converter voltage 的主要分量写成

\[
\begin{aligned}
V_{\mathrm{con}}(t)=&V_1\cos(\omega_1t+\theta_1)\\
&+V_{f_c/f_1-2}\cos[(\omega_c-2\omega_1)t+\theta_c-2\theta_1]\\
&+V_{f_c/f_1+2}\cos[(\omega_c+2\omega_1)t+\theta_c+2\theta_1]+\cdots .
\end{aligned}
\]

其中 \(\theta_c\) 不改变 fundamental 的 phase，却直接进入 carrier sideband 的 phase。不同 unit 的 carrier 不同步，而且 \(f_c\) 的小偏差会积累成较大的 \(\theta_c\) 差，因此 characteristic harmonic source 的相角具有随机性，不能在 PCC 按同相电流源相加。[pdf:E03]（PDF 物理页 3，Eq. (1) 及相邻正文）

**2. 死区造成的低阶 non-characteristic harmonic。** 作者引用的近似式为

\[
\frac{V_h}{V_1}=\frac{8}{\pi hM}\left(\frac{T_d}{T_c}\right)
\approx \frac{3.18}{h}\left(\frac{T_d}{T_c}\right),
\]

其中 \(M\) 是 modulation index，典型值 0.8；\(T_d\) 是 deadtime，\(T_c=1/f_c\)。当 \(T_d/T_c=0.01\) 时，第 5 次约为 0.64%。它说明低阶源项不是严格为零，但正常设计下通常比传统大谐波源小。[pdf:E03]（PDF 物理页 3，Eq. (2)、Table I）

**3. 多频端口的原始定义。** 论文先写成一般非线性复函数

\[
[I_g]=f([V_g],V_{g1},I_{g1}),
\]

其中 \([I_g]=[I_{g3},I_{g5},\ldots,I_{gh}]^{T}\)，\([V_g]=[V_{g3},V_{g5},\ldots,V_{gh}]^{T}\)，而 \((V_{g1},I_{g1})\) 指定 fundamental operating point。这个式子的重要性是承认“多频输入可能共同决定多频输出”，而不是先验假定每个 harmonic 独立。[pdf:E05]（PDF 物理页 5，Eq. (3)）

**4. 正负序 coupled impedance。** 在 balanced fundamental voltage 假设下，closed-form 结构可写为

\[
\begin{bmatrix}[V_{g+}]\\[V_{g-}]\end{bmatrix}
=
\begin{bmatrix}
[Z_{+,+}]&[Z_{+,-}]\\
[Z_{-,+}]&[Z_{-,-}]
\end{bmatrix}
\begin{bmatrix}[I_{g+}]\\[I_{g-}]\end{bmatrix}.
\]

\([Z_{+,+}]\)、\([Z_{-,-}]\) 的对角元素表示同 harmonic、同 sequence 响应；其非对角元素与 \([Z_{+,-}]\)、\([Z_{-,+}]\) 表示 cross-frequency 和 cross-sequence coupling。每个元素由 filter、controller transfer function 等决定，而不是 harmonic voltage/current 本身的函数。[pdf:E05]（PDF 物理页 5，Eq. (6)）[pdf:E06]（PDF 物理页 6，Eq. (7) 及定义）

当测得的非对角项远小于对角项时，得到实用近似

\[
I_{gh+}\approx \frac{V_{gh+}}{Z_{h+,h+}},\qquad
I_{gh-}\approx \frac{V_{gh-}}{Z_{h-,h-}}.
\]

这一步把 coupled multi-frequency system 降为正、负序各自独立的 frequency-dependent impedance，也使 harmonic model 与单频 \(Z(f)\) model 在该适用区间会合。[pdf:E06]（PDF 物理页 6，Eq. (8)、Fig. 5）

**5. 两状态辨识为什么能消掉未知源。** 对 Norton circuit 的两个近邻状态，

\[
\begin{aligned}
I_s(h)&=-I_{m1}(h)+\frac{V_{m1}(h)}{Z(h)},\\
I_s(h)&=-I_{m2}(h)+\frac{V_{m2}(h)}{Z(h)}.
\end{aligned}
\]

假设小扰动期间 \(I_s(h)\) 不变，两式相减后直接得到

\[
Z(h)=\frac{V_{m2}(h)-V_{m1}(h)}{I_{m2}(h)-I_{m1}(h)}
=\frac{\Delta V_m(h)}{\Delta I_m(h)}.
\]

这就是最一般的 two-state \(\Delta V/\Delta I\) method；关键不是“测一次 V/I”，而是用差分消除同一 operating point 下未知 current source 的偏置。[pdf:E07]（PDF 物理页 7，Eq. (9)–(10)）

若 test source 近似理想电压源，使 state 1 的 \(V_{m1}(h)=0\)，则

\[
I_s(h)=-I_{m1}(h),
\qquad
Z(h)=\frac{V_{m2}(h)}{I_{m2}(h)+I_s(h)}.
\]

只有进一步证实 \(I_s(h)\ll I_{m2}(h)\) 时，才可简化为

\[
Z(h)\approx \frac{V_{m2}(h)}{I_{m2}(h)}.
\]

因此 \(V/I\) 并非与 two-state method 等价的无条件替代，而是“小源项”条件下的近似。[pdf:E08]（PDF 物理页 8，Eq. (11)–(13)）

## § 7 — 实验设计与结论

实验对象是一台实际 10 kW、380 V、带 LC filter 的 PMSG-IBR，carrier frequency 为 3 kHz；motor 模拟 wind turbine 驱动 PM generator，设备直接连接三相 60 kVA programmable grid simulator，其 internal impedance 很小。电压、电流 measurement chain 的总精度估计均为 0.1%。base case 接近满载且稳态，\(V_{\text{phase}}=219.6\ \text{V}\)、\(I=13.2\ \text{A}\)、\(P=8.7\ \text{kW}\)、\(Q=1\ \text{kVAr}\)。[pdf:E08]（PDF 物理页 8，Fig. 10、Section VI-A）

**问题 1：正常 unit 的 Norton current source 是否足够小？** 实验把 grid simulator 设为只含 fundamental 的近似理想电压源，因而按 Eq. (11)，测得 harmonic current 就是 Norton source 的反号。Table III 中最大两项是第 5 次负序 1.3% 与第 7 次正序 0.6%，其余列示 harmonic 多为 0–0.2%；作者据此判断该 unit 的主动谐波源很小，符合前文的机理分析。[pdf:E09]（PDF 物理页 9，Table III、Section VI-B）

**问题 2：two-state 方法能否得到有物理意义的 impedance？** 作者在目标 harmonic 施加约 4.5% 的正序或负序 step voltage，使用 \(\Delta V/\Delta I\) 得到离散 impedance，再用步长 0.2 harmonic 的单音 interharmonic scan 计算 \(V(f)/I(f)\)，并与 LC filter impedance 比较。三组结果在 \(h\ge 13\) 时吻合良好；第 5、7 次的 \(\Delta V/\Delta I\) 与 \(V/I\) 有小差异，原因是简单 \(V/I\) 没有扣除 Table III 中的 Norton source。Table IV 还显示 87% output 时正负序确有差异，例如第 5 次 \(Z_+=6.16\ \Omega\)、\(Z_-=4.18\ \Omega\)，第 7 次分别为 10.25 与 7.93 \(\Omega\)。[pdf:E09]（PDF 物理页 9，Table IV、Fig. 11、Section VI-C）

**问题 3：impedance 是否随 active power operating point 大幅变化？** 实验在 power factor 接近 1 时测试 25%、50%、75%、87% 四个 active power output level。Fig. 12 显示各 harmonic 的 positive-sequence Norton impedance 变化不大；负序结果因篇幅未画出，但作者称结论相同。相反，Fig. 13 显示 current source 随 output 上升，尤其第 5 次负序与第 7 次正序更明显。[pdf:E09]（PDF 物理页 9，Fig. 12、Section VI-D）[pdf:E10]（PDF 物理页 10，Fig. 13）

**问题 4：忽略 harmonic coupling 是否经得住实测？** 作者逐次注入 3.5% 的正序或负序单一 harmonic voltage，并监视所有列示 harmonic/sequence current。Fig. 14 的 \([I_h]\sim[V_h]\) heatmap 明显对角占优：输入某一 sequence 的第 \(h\) 次电压，主要产生同一 sequence、同一 \(h\) 的电流；背景中仍可见与注入频率无关的第 5 次负序 1.3% 和第 7 次正序 0.6%。这同时支持“弱耦合 impedance + 独立小 source”的分解。[pdf:E10]（PDF 物理页 10，Fig. 14、Section VI-E）

这些实验能支持“在这台正常设计的 10 kW PMSG、LC filter、所测扰动幅值与 operating range 内，uncoupled Norton model 是实用近似”，但不能直接外推到全部 IBR。论文没有给出多厂商、多拓扑、多控制固件或大功率 plant 的统计样本；作者还明确说，需要更多研究判断第 5、7 次处的简化结论能否用于 active front end，并指出 VSC-HVDC 等超大 unit 在设计阶段甚至没有 physical unit 可测。[pdf:E08]（PDF 物理页 8，Fig. 8）[pdf:E09]（PDF 物理页 9，Section VI-C）

## § 8 — Take-aways

**5 句话。** 第一，VSC-IBR 的 PWM characteristic harmonics 主要位于高频并被 front-end filter 衰减，unit 间 source phase 还具有显著随机性。[pdf:E02]（PDF 物理页 2，Fig. 2）第二，第 3–7 次低阶 non-characteristic harmonics 可由 deadtime、unbalance、DC-link 与器件非理想产生，但正常 unit 的量级通常较小。[pdf:E03]（PDF 物理页 3，Eq. (2)）[pdf:E04]（PDF 物理页 4，Table II）第三，面对 grid background harmonics，VSC 的主导端口行为是正、负序不同的 frequency-dependent impedance，完整模型虽有 coupling，但实测常呈对角占优。[pdf:E06]（PDF 物理页 6，Eq. (7)–(8)）第四，工程上应使用 Norton circuit 同时保留 impedance response 与小的 device-specific source，且 source 最好由 physical unit 测量。[pdf:E07]（PDF 物理页 7，Fig. 6）第五，两状态 \(\Delta V/\Delta I\) 是最一般的辨识方法，单状态 \(V/I\) 只有在 source 已证实很小时才可靠。[pdf:E08]（PDF 物理页 8，Eq. (11)–(13)）

**3 句话。** 这篇论文把 VSC harmonic study 的“关键数据”从确定谐波电流源改成了 frequency- and sequence-dependent Norton impedance。物理 PMSG 实验支持弱 coupling、较弱 operating-point dependence 与小 current source，但证据仍集中在单台 10 kW unit。[pdf:E09]（PDF 物理页 9，Table III–IV、Fig. 11–12）对 IBR plant，最大的系统风险因而更可能是 impedance 与电网/电容共同形成 resonance，以及多 unit source 的随机相位聚合，而不是把每台 inverter 的低阶电流简单同相相加。[pdf:E11]（PDF 物理页 11，Conclusion）

**1 句话。** 对 VSC-IBR 谐波研究，应先测清“它怎样以阻抗响应电网”，再用一个小且不确定的 Norton source 补上“它自身还生成什么”。[pdf:E11]（PDF 物理页 11，Conclusion）

## § 9 — 最脆弱的假设

失败代价最大的假设是：**对于需要工程评估的所有重要 operating condition 与 background distortion，真实 IBR 的 multi-frequency、cross-sequence coupling 始终足够弱，因此可以用一组彼此独立且近似不随 operating point 变化的 \(Z_+(h)\)、\(Z_-(h)\) 与 source \(I_s(h)\) 代替完整非线性映射。**

这个假设一旦失效，问题不只是阻抗数值误差变大。若某个 controller、PLL、DC-link、active harmonic function、current limiter 或低 carrier-frequency design 让 off-diagonal coupling 随输入组合或 operating point 显著变化，那么不同 harmonic 不能逐次独立求解，two-state 小扰动得到的 \(Z(h)\) 也不能预测 multi-tone 场景；此时 Norton source 与 impedance 的分解会随状态变化，可能漏判 resonance 或错误估计 PCC distortion。论文自己给出的风险线索包括：只用 filter impedance 在第 5、7 次可能产生约 30% error；low-order impedance 可因 inner loop 变成 negative resistance 或 capacitive reactance；低 carrier frequency、小 DC capacitor、filter 不足和 manufacturer-specific non-ideality 都可能使 generation 不再可忽略。[pdf:E06]（PDF 物理页 6，Fig. 5 后的 sensitivity conclusions）[pdf:E07]（PDF 物理页 7，Section V-A）

论文对该假设提供的最强直接证据，是一台 10 kW PMSG unit 在四个 active power level 下 impedance 变化不大，并且 3.5% 单音 positive/negative-sequence injection 得到的 response matrix 对角占优。[pdf:E09]（PDF 物理页 9，Fig. 12）[pdf:E10]（PDF 物理页 10，Fig. 14）缺失的则是多厂商、不同 filter 与 control architecture、弱网、simultaneous multi-tone distortion、current limiting、large-signal disturbance、firmware mode switching 和大型 IBR 的验证。因而“弱 coupling”应被视为需要针对目标设备与工况先验证的 model-validity condition，而不是 VSC 类别的无条件定律。

## § 10 — 最小复现实验

一周内最值得复现的不是全篇所有公式，而是直接检验上述脆弱假设：**同一台实际 grid-following inverter 能否在未参与辨识的 multi-tone 工况下，被 uncoupled Norton model 准确预测。**

所需数据与设备是一台可安全操作的三相 inverter、programmable grid source 或现有 PHIL/HIL test bench、三相同步 voltage/current waveform 与可做正负序 DFT 的脚本。先固定一个中等 active power、unity power factor operating point；对第 5、7、11、13 次分别施加约 3% 的正序与负序 perturbation，记录无扰动与有扰动两个状态，以 Eq. (9)–(10) 得到 \(Z_\pm(h)\)，并以无扰动状态得到 \(I_{s,\pm}(h)\)。这沿用了论文的 two-state principle，但 harmonic set 与自动处理脚本可以缩小到最少四个频点。[pdf:E07]（PDF 物理页 7，Fig. 7、Eq. (9)–(10)）

然后做盲测：同时注入两种未共同出现在辨识阶段的 harmonic，例如正序第 5 次加负序第 7 次，再改变一次 active power。用独立 Norton branches 预测所有已测 harmonic current，并与实测 phasor 比较；同时记录 off-diagonal current 与对应 diagonal current 的比值。预注册判断规则可设为：若各目标 harmonic 的 complex-current normalized error 在盲测中均不超过 10%，且最大 cross-coupled response 小于 diagonal response 的 10%，则在该设备和测试域内支持简化模型；若任一重复工况中出现超过 20% 的预测误差，或非目标 harmonic current 达到同频 diagonal response 的 20% 以上，则反驳“uncoupled model 足够”的 claim。这里的 10%/20% 是本复现方案为了可证伪而建议的工程阈值，不是论文报告阈值。

为避免把 instrument noise 当成 source，先以 shorted/idle measurement 估计 phasor noise floor，并至少重复三次 two-state test；若 physical unit 不可得，可先在 controller-HIL 上跑通流程，但 HIL 结果只能验证辨识与求解链路，不能替代论文强调的 physical non-ideality evidence。[pdf:E07]（PDF 物理页 7，关于 EMT/HIL 与 physical source measurement 的讨论）

## § 11 — 最强反例设计

最强反例不是找一台 THD 很高的 inverter，而是构造一个场景，让论文的“弱 coupling、弱 operating-point dependence、source 与 impedance 可分离”三项同时受到挑战。具体做法是选择带 active harmonic compensation、grid-support mode 或易触发 current limiter 的商业 VSC，在弱网下同时施加第 5、7 次正负序 distortion 与 2% fundamental unbalance，并跨越轻载、额定、限流边界；先用小信号单音 two-state test 建模，再盲测多音与 mode transition。2% unbalance 会通过 negative-sequence current 与 DC-link second-harmonic ripple 生成第 3 次分量，这正是论文已经指出的跨域转换路径。[pdf:E04]（PDF 物理页 4，Section III-B-2、Table II）

若盲测中出现以下任一结果，就形成有力反例：同一个 \(Z_\pm(h)\) 随 harmonic combination 或 controller mode 大幅漂移；第 \(h\) 次输入在 \(h\pm2\) 或 opposite sequence 产生与 diagonal response 同量级的 current；从 state 1 计算的 \(I_s\) 无法在 state 2 保持不变；或 uncoupled Norton model 预测“无 resonance”而 coupled measurement 显示显著放大。这样可以排除“只是参数测得不准”的替代解释，因为反例针对的是模型可分离性与线性叠加本身。

还应设置一个 passive-filter control：用同一 LC/LCL network、断开或冻结 active control，重复 frequency scan。如果 passive network 已能解释论文式对角占优，而 active controller 在上述 stress case 下引入强 coupling，那么论文单台 PMSG 的结果更可能是“该 filter 与控制工况的性质”，而不是所有 VSC-IBR 的类别性质。这个反例直接利用了论文自己承认的事实：front-end filter 是最显著因素，低阶处 controller 又可改变 resistance/reactance，且现有物理验证只覆盖一台设备。[pdf:E06]（PDF 物理页 6，Fig. 5 与 sensitivity conclusions）[pdf:E08]（PDF 物理页 8，Fig. 10）

## § 12 — Follow-up Research Idea

本领域通常不会仅因模型形式更复杂就认为工作高影响。更有分量的结果应同时满足：在 power-system harmonic/interconnection 问题上有明确系统价值；以多设备、真实 controller 或严格 HIL/physical test 形成可复核证据；能改变 IEEE/CIGRE/OEM model exchange 或 resonance screening 的工程实践；并说明精度、可测性、计算成本与适用边界。本文发表于 IEEE Transactions on Power Delivery，且其论证始终围绕 standards、physical unit test 与 plant interconnection，正体现了这种评价取向。[pdf:E01]（PDF 物理页 1，Abstract、Introduction）

**候选想法：建立“带有效域与不确定性边界的自适应 Norton model certificate”，把研究目标从交付一组固定 \(Z_\pm(h),I_s(h)\) 改成证明某台黑盒 IBR 在哪些 harmonic combination、operating mode 与 grid strength 下可以安全使用 uncoupled Norton model，并在证据触发时自动升级为 coupled multi-frequency model。** 由于本卡未做外部相关工作检索，这只是证据约束下的候选方向，不声称 novelty。

（a）未满足需求在于 OEM 内部参数不可得、VSC configuration 持续演化、大型 unit 设计阶段可能无 physical sample，而单一 nominal impedance curve 又不能表达 model invalidity。论文的 Fig. 8 已明确暴露“大型 VSC-HVDC 无法直接取得 current source”的缺口。[pdf:E08]（PDF 物理页 8，Fig. 8）

（b）其研究价值不在“多加一个 neural network”，而在把 harmonic model 变成可验收的工程 contract：交付 nominal Norton parameters、confidence envelope、适用 operating domain、触发 coupled model 的 diagnostic 与对 resonance prediction 的风险上界。若能跨多厂商 unit 证明这种 certificate 显著减少错误 resonance screening，它有机会影响 interconnection data requirement 与 model validation practice。

（c）可借鉴相邻领域的 set-membership system identification、robust control、uncertainty quantification 与 active experiment design。辨识器先选择信息量最大的正/负序 multi-tone perturbation；实时 EMT/HIL 平台负责在大量 grid strength 与 controller mode 下执行盲测，FPGA 可用于确定性生成扰动、同步采样和在线 phasor/sequence 计算，但具体 fixed-point、latency 与 resource mapping 必须作为新工作的独立实现问题，不能从本文推断。

（d）第一个可证伪实验应是：在至少三种不同 filter/control architecture 的 IBR 上，仅用 low-amplitude single-tone data 建 certificate，再盲测 multi-tone、2% unbalance、weak-grid、不同 P/Q 与 mode transition。若真实 harmonic current 或 resonance peak 经常落在 confidence envelope 之外，或者 adaptive certificate 对未见工况的预测并不优于固定 uncoupled Norton model，这个研究方向即被第一轮实验否定。

（e）它与本文以及单纯“增加 coupled matrix 参数”的实质区别，是把模型选择和失效检测本身变成一等输出：证据支持时保持本文的低成本 Norton model，证据不支持时才升级复杂度，并明确告诉 network study 哪些结论不可外推。这样直接回应第 9 节的核心脆弱假设，也保持电力工程最关心的可测、可交付与系统风险闭合。
