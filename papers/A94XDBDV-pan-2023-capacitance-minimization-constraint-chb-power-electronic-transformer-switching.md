# Capacitance Minimization and Constraint of CHB Power Electronic Transformer Based on Switching Synchronization Hybrid Phase-Shift Modulation Method of High Frequency Link

作者：Yuzhuo Pan，Jiaxun Teng，Chen Yang，Zemin Bu，Baocheng Wang，Xin Li，Xiaofeng Sun

出处：IEEE Transactions on Power Electronics，Vol. 38，No. 5，pp. 6224–6242

年份：2023

DOI：10.1109/TPEL.2023.3239164

Zotero key：A94XDBDV

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是 cascaded H-bridge power electronic transformer（CHB-PET）中一个很具体的工程矛盾：每个 submodule（SM）的瞬时充电功率含有两倍基频分量，传统方案让较大的 SM 电容吸收这部分低频能量，于是电容体积、成本和系统功率密度相互牵制。作者把应用背景放在中压电机驱动和智能电网，并指出 CHB-PET 虽然模块化、易扩展且便于冗余运行，但其 SM 电容通常要按二倍频电压纹波来选大。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 2，Section I）

论文的核心问题不是“怎样再优化一次电容参数”，而是：能否改变二倍频纹波电流的去向，使它不再主要进入 SM 电容，同时又不增加独立硬件滤波器或复杂的 ripple-power 控制环？作者给出的答案是 CHB-SIQAB 拓扑配合 switching synchronization hybrid phase-shift modulation（SSHPSM）：让 SIQAB 原边三座全桥同步换相，在每个高频半周期内形成 switched-capacitor 连接，把三相低频纹波搬到高频变压器原边，再利用三相对称性在磁路中抵消。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Introduction 的三点贡献）

作者报告，在其给定设计和器件选型下，相比传统大电容方案，SM 电容体积减少 85%，成本减少 85.6%。这两个比例对应的是特定电压、电容规格和器件价格的比较，不是所有 CHB-PET 都可直接复用的普适比例。[pdf:E10]（PDF 物理页 10，Fig. 14 与 Eq. (20) 后正文）

从工程价值看，真正有意义的是作者改变了“低频能量必须在各 SM 本地存储”的默认假设。若该机制在额定功率、故障、参数漂移和寿命周期内都成立，就可能把单个 SM 的储能器件从系统体积主导项变成主要处理 switching ripple 的较小元件。这里“可能提高功率密度”是基于论文机制的工程推断；论文没有给出整机体积、整机成本或寿命对比。

## § 2 — 前人工作与不足

论文把既有减容路线分为两类。第一类是硬件滤波，包括继续增大 SM 电容或增加 LC 二次谐振滤波器；优点是直接、有效，缺点是体积和成本上升。第二类是软件或控制方法：third-harmonic injection 通过给 SM 调制电压注入三次谐波来压低二倍频纹波，但需要计算注入谐波的最优幅相；ripple-power transfer 则让后级 dc-dc 变换器主动转移纹波功率，但需要精心设计调节器，而且作者认为相应的动态扰动不能自然消除。[pdf:E02]（PDF 物理页 2，Section I 对 [8]–[15] 的综述）

传统 CHB-QAB 的物理症结可以从阻抗看清：在二倍频处，论文算得 QAB-stage 的输入阻抗大于 SM 电容阻抗，因此二倍频电流更愿意流入电容，造成电压纹波；不引入额外控制时，只能继续增大电容。传统 QAB 还需要原边外接电感，并通过各原边端口与副边之间的 phase shift 控制功率。[pdf:E04]（PDF 物理页 4，Fig. 3、Fig. 4、Eq. (1) 及 Section II-B）

这篇论文相对前述方法的实质变化，是把“测量纹波后调节”换成“由开关连接本身自动重分配纹波”：同步原边全桥使三相电容在高频半周期内等效互联，不再为每相纹波单独设计控制器。它没有证明 third-harmonic injection 或主动功率解耦在所有条件下都更差；它只在自己选取的系统结构、器件和工况下展示了较低电容需求及可接受效率。

## § 3 — 重建作者的思考路径

下面是基于论文证据的逆向重建，不是作者逐字陈述。

第一步，从单个 SM 的能量来源出发。SM 的 switching function 与相电流相乘后，自然得到一个直流分量和一个二倍频分量；三相二倍频分量幅值相同、相位互差 \(120^\circ\)。传统方案把这组三相对称纹波看成三只电容各自必须承受的扰动，于是电容约束与基频 \(f_F\) 成反比，低速电机工况尤其不利。[pdf:E05]（PDF 物理页 5，Eq. (3)–(5)）

第二步，反过来利用这组三相纹波的“对称”而不是只压低其幅值。如果三个 SIQAB 原边全桥在同一时刻使用相同开关状态，三个 SM 电容就可通过原边绕组在每个高频半周期内形成等效并联的 switched-capacitor 网络，端电压相互钳位。此时，小漏感意味着低频纹波看到的是一条比本地电容更低阻的转移通道。[pdf:E05]（PDF 物理页 5，Fig. 5 及 Section III-A）[pdf:E06]（PDF 物理页 6，Fig. 6–8 与 Eq. (7)–(10)）

第三步，必须回答“把纹波送进变压器是否只是把问题挪到副边”。作者用 Fourier 展开指出，二倍频包络在同步高频开关后表现为载波奇次谐波两侧的 \(\pm 2\omega\) sideband，三相原边电流仍保持对称；再利用四绕组磁路的叠加关系，使这些分量在主磁通路径中相互抵消，副边主要保留传递有功功率所需的分量。[pdf:E07]（PDF 物理页 7，Fig. 9、Fig. 10 与 Eq. (11)）[pdf:E08]（PDF 物理页 8，Fig. 11 与 Eq. (12)–(14)）

第四步，重新定义电容的主要任务。若二倍频能量不再主要由 SM 电容吸收，那么电容约束可从“随基频变化的低频储能要求”改写成“吸收 CHB switching ripple 的电荷要求”，从而由 \(f_{\mathrm{SM}}\) 而不是 \(f_F\) 主导。这条思考链说明论文的 idea 不是单独的 modulation trick，而是开关连接、阻抗路径和三相磁通抵消共同组成的机制。

## § 4 — 核心 Intuition

SSHPSM 让三相 SM 电容在每个高频半周期内通过 SIQAB 原边等效并联，因此二倍频纹波电流优先离开本地电容，进入高频变压器原边。[pdf:E06]（PDF 物理页 6，Fig. 6–8）同步开关把该纹波变成三相对称的高频 sideband，主磁通中的对应分量相互抵消，副边不需要承受同样的二倍频功率摆动。[pdf:E07]（PDF 物理页 7，Eq. (11) 与 Fig. 10）这一机制能成立的关键不是“控制得更快”，而是原边漏感足够小、三相连接与电流足够对称；残余漏磁仍会存在。[pdf:E08]（PDF 物理页 8，Eq. (13)、Fig. 11）

## § 5 — 具体方法与完整 Pipeline

以三相 CHB-SIQAB 从中压交流侧向低压直流母线供电为例，完整 pipeline 如下。

1. **输入与 CHB 级。** 三相中压交流经各相串联 SM 合成所需端口电压。每个 SM 的充电电流由其 switching function 与相电流相乘，包含平均功率对应的直流分量和二倍频分量。论文拓扑将三相 SM 连接到一个 single-inductor quad-active-bridge 高压侧的三个端口，副边汇入 LVdc 母线。[pdf:E03]（PDF 物理页 3，Fig. 2）

2. **功率控制。** CHB-stage 保留传统电压与电流控制；SIQAB-stage 只使用 LVdc 电压环。三个原边全桥的调制相角统一为 \(\phi_{\mathrm{FB}}\)，副边为 \(\phi_{\mathrm{FBL}}\)，有功功率由 \(\phi=\phi_{\mathrm{FB}}-\phi_{\mathrm{FBL}}\) 控制。原边取消外接传能电感，主要依靠小漏感；外部传能电感 \(L_s\) 放在副边。[pdf:E05]（PDF 物理页 5，Fig. 5 与 Section III-A）

3. **高频开关事件。** 每个 SIQAB switching cycle 分为 \(T_1\) 和 \(T_2\) 两个半周期。同步原边桥在两个状态中交替改变连接极性，使三只 SM 电容经过原边绕组形成等效并联，周期末端电压相互钳位。论文分析的是连续电路与开关状态，并未给出 EMT 离散积分格式或事件调度算法。[pdf:E05]（PDF 物理页 5，Fig. 5(d)）[pdf:E06]（PDF 物理页 6，Fig. 6–8）

4. **低频纹波转移。** 对直流分量，电容在低频近似开路，功率通过 SIQAB phase shift 送往 LVdc；对二倍频分量，等效互联端口的低阻抗使纹波电流进入 SIQAB 原边。漏感越小，留在 SM 电容中的二倍频电流越小。[pdf:E06]（PDF 物理页 6，Eq. (7)–(10)）

5. **磁路抵消。** 同步高频调制把二倍频包络映射到三相原边电流的 sideband。四绕组 HFT 让三相原边绕组分别覆盖磁芯区段；在三相对称条件下，sideband 引起的主磁通相消，副边主要承载净功率分量。作者的 ANSYS 磁场模型给出的等效漏感约为 \(2\,\mu\text{H}\)。[pdf:E07]（PDF 物理页 7，Fig. 10、Fig. 11 开始处）[pdf:E08]（PDF 物理页 8，Fig. 11 与 Eq. (13)）

6. **电容选型。** 二倍频被转移后，作者只按 SM H-bridge switching cycle 内的电荷摆动计算电容下限。论文设计表将传统约束下的 \(6\,\text{mF}\) 与 SSHPSM 约束下的 \(0.73\,\text{mF}\) 对比；器件选型分别是三只 \(2.4\,\text{mF}/1200\,\text{V}\) 并联和一只 \(1\,\text{mF}/1200\,\text{V}\)。[pdf:E09]（PDF 物理页 9，Table III）仿真按 \(0.73\,\text{mF}\) 建模；正文另有四舍五入后的 \(0.7\,\text{mF}\) 表述。[pdf:E12]（PDF 物理页 12，Table IV）[pdf:E14]（PDF 物理页 14，Section VI-A）

7. **非理想与临界工况检查。** 论文分别考察原边 gate phase 的微小不同步、HFT 三端漏感不一致、10 Hz 低频电机运行，以及并网相电压不对称。其目标不是消除所有不对称，而是判断电压钳位和纹波转移在预设偏差范围内是否仍有效。[pdf:E11]（PDF 物理页 11，Section IV）[pdf:E13]（PDF 物理页 13，Fig. 20 与 Section V-B）

8. **执行平台与未报告项。** 电磁部分使用 ANSYS，系统级 switching simulation 使用 PLECS，硬件用一套 300 W CHB-SIQAB 原型验证。[pdf:E08]（PDF 物理页 8，Fig. 11）[pdf:E14]（PDF 物理页 14，Section VI-A）[pdf:E15]（PDF 物理页 15，Section VII 开头）论文未报告仿真求解器、时间步长、多速率推进、代数环处理、计算依赖图、并行划分、定点数值格式、FPGA 映射、资源占用或实时步长，因此不能据此声称该方法已经实现 EMT real-time simulation 或 FPGA HIL。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 1. 传统电容为什么随基频变大

设 phase-\(x\) 的 SM switching function 和相电流为

\[
s_x=g\sin(\omega t+\theta_x),\qquad
i_x=I_s\sin(\omega t-\varphi+\theta_x).
\]

二者相乘得到

\[
i_{\mathrm{SM}x}
=\frac{I_sg}{2}\cos\varphi
-\frac{I_sg}{2}\cos(2\omega t-\varphi+2\theta_x).
\]

第一项输送平均功率，第二项是二倍频充放电电流；三相的 \(\theta_x\) 使这些二倍频电流彼此错开 \(120^\circ\)。将其积分成允许的 peak-to-peak 电容电压纹波 \(\varepsilon u_C\)，作者采用的传统约束为

\[
C\ge \frac{I_sg}{4\pi f_F\varepsilon u_C}.
\]

因此 \(f_F\) 越低，所需电容越大。[pdf:E04]（PDF 物理页 4，Eq. (2) 与变量定义）[pdf:E05]（PDF 物理页 5，Eq. (3)–(5)）

### 2. 小漏感为什么能把纹波从电容中“拉走”

论文把 SM 电容和 HFT 原边漏感写成

\[
Z_{Cx}=\frac{1}{j\omega C_x},\qquad Z_{LTx}=j\omega L_{Tx}.
\]

纹波电流在本地电容支路和 SIQAB 端口之间按阻抗分流：

\[
i_{Cx,\mathrm{ac}}
=i_{\mathrm{SM}x,\mathrm{ac}}\frac{Z_{ex}}{Z_{Cx}+Z_{ex}},\qquad
i_{Qx,\mathrm{ac}}
=i_{\mathrm{SM}x,\mathrm{ac}}\frac{Z_{Cx}}{Z_{Cx}+Z_{ex}}.
\]

在三相电容和漏感一致的简化条件下，作者把 phase-a 留在电容中的合成纹波化为

\[
i_{Ca}
=i_{\mathrm{SM}a,\mathrm{ac}}\cdot
\frac{1}{1+\dfrac{1}{\omega^2L_TC}}.
\]

当 \(L_T\to 0\) 时，右侧比例趋近于零，这正是“小漏感形成低阻纹波通道”的数学表达。它也同时暴露了一个边界：漏感不是可忽略的实现细节，而是决定残余纹波的核心参数。[pdf:E06]（PDF 物理页 6，Eq. (6)–(10)）

### 3. 同步开关为什么仍保留三相抵消关系

作者用 double Fourier transformation 和 Taylor expansion，把原边电流写成载波奇次谐波与其二倍频 sideband 的叠加：

\[
i_{px}
=\frac{2I_sg}{\pi}\sum_{m=1}^{\infty}
\frac{\sin[(2m-1)\omega_St]}{2m-1}
+\frac{I_sg}{\pi}\sum_{m=1}^{\infty}
\frac{\cos\{[(2m-1)\omega_S\pm2\omega]t+\theta_x\}}{2m-1}.
\]

这里第二组项带有各相 \(\theta_x\)，所以进入 HFT 原边后仍保持三相对称关系。[pdf:E07]（PDF 物理页 7，Eq. (11)）磁阻模型进一步把主磁通分为残余纹波项、原边平均功率项和副边磁动势项；残余纹波项与 \(R_m+R_\delta\) 有关。作者认为漏感为 \(\mu\text{H}\) 量级而励磁电感为 \(\text{mH}\) 量级，因此纹波造成的主磁通残量相对较小。ANSYS 结果中，传统方案与 SSHPSM 方案的最大磁通密度分别为 \(0.6132\,\text{T}\) 和 \(0.6284\,\text{T}\)，作者报告增幅约 2.4%。[pdf:E08]（PDF 物理页 8，Eq. (12)–(14) 与正文）[pdf:E09]（PDF 物理页 9，Fig. 12）

### 4. 新电容约束为什么由 switching frequency 决定

作者把一个 SM switching cycle 内的电荷增量写为

\[
\Delta E_{\mathrm{SM}}
=\frac{i_{\mathrm{SM}x,\max}D_{\mathrm{SM}}}{f_{\mathrm{SM}}},
\]

并得到

\[
\varepsilon u_C
=\frac{\Delta E_{\mathrm{SM}}}{C_x}
=\frac{I_sg^2}{2C_xf_{\mathrm{SM}}},
\qquad
C\ge\frac{I_sg^2}{2f_{\mathrm{SM}}\varepsilon u_C}.
\]

直观上，允许纹波相同时，提高 \(f_{\mathrm{SM}}\) 会缩短每次充电时间，从而减小所需电容。需要注意：论文把 \(\Delta E_{\mathrm{SM}}\) 称为 charging energy，但 Eq. (18) 的量纲是电流乘时间，更接近电荷增量；后续除以 \(C_x\) 得电压也支持这种解释。这是符号命名问题，不改变作者随后使用的电容约束，但复现时应按“电荷”而不是“能量”实现。[pdf:E10]（PDF 物理页 10，Eq. (18)–(20)）

### 5. 三相不对称为何留下不可抵消分量

不对称电压下，作者把电压、电流和调制量分为正序与负序。它们相乘后，二倍频项中一部分仍按三相错相排列，可以在 HFT 原边抵消；另一部分在三相上同相，成为 zero-sequence component。Eq. (28) 给出的 phase-a 残余电容电流正比于 \(I_s^-g^+\) 和 \(I_s^+g^-\) 的组合，因此电压不平衡越强，电容仍需吸收的低频电流越大。[pdf:E13]（PDF 物理页 13，Eq. (24)–(26)）[pdf:E14]（PDF 物理页 14，Eq. (27)–(28)）

## § 7 — 实验设计与结论

### 问题 1：小电容是否仍能把稳态电压纹波限制在与传统方案相当的范围？

**实验。** PLECS 中 Mode 1 使用传统 QAB 和 \(6\,\text{mF}\) SM 电容，Mode 2 使用 SIQAB、SSHPSM 和 \(0.73\,\text{mF}\) 电容。两者共同参数包括 \(750\,\text{V}\) SM 电压、\(6\,\text{kV}\) line-to-line RMS、\(1.2\,\text{MW}\)、50 Hz 基频、2 kHz CHB PWM、每相 8 个 SM 和 20 kHz dc-dc switching；Mode 1 与 Mode 2 的等效传能电感分别为 \(39\,\mu\text{H}\) 和 \(13\,\mu\text{H}\)。[pdf:E12]（PDF 物理页 12，Table IV）

**答案。** Mode 1 用大电容把电压纹波压到 5%；Mode 2 用约为 Mode 1 12% 的电容仍满足 5% 纹波范围，剩余主要是 high-frequency switching harmonic。[pdf:E14]（PDF 物理页 14，Fig. 22 与 Section VI-B）这支持“在该仿真参数点可显著减容”，但没有证明任意功率等级都能保持同样比例。

### 问题 2：二倍频电流是否真的从 SM 电容转移到 SIQAB 原边，并在副边消失？

**实验。** 作者对两种模式的 SM 电容电流和 dc-dc 原边输入电流做 FFT，并观察 HFT 原、副边波形。50 Hz 输入时，Mode 1 的 SM 电容 100 Hz 分量约为 76 A，Mode 2 约为 1.125 A；相反，dc-dc 原边输入的 100 Hz 分量由约 0.5 A 变为约 71 A。HFT 原边出现二倍频包络，副边波形没有同样的低频包络。[pdf:E15]（PDF 物理页 15，Fig. 23–25）

**答案。** 这些结果与论文的“转移而非本地吸收”解释一致，而且同时排除了“只是把电容加大或滤波调参”的替代解释。它们仍是仿真频谱证据；论文没有报告频谱窗函数、稳态截取长度或数值噪声底。

### 问题 3：减容是否换来了不可接受的磁通或损耗？

**实验。** 作者用 ANSYS 比较磁通密度，并根据 SiC MOSFET 开关损耗、导通损耗及 HFT 铁耗、铜耗模型计算不同负载下 dc-dc-stage 的效率。给定器件表中，端口电压为 750 V、switching frequency 为 20 kHz；SSHPSM 原边 RMS 电流高于传统方案，因此作者为两种方案选取了不同的 SiC 器件，并对绕组与磁芯规格分别建模。[pdf:E09]（PDF 物理页 9，Table II、Eq. (15)–(17)）

**答案。** 作者报告 SIQAB-stage 效率可达到约 96%，磁通密度只小幅上升；这说明在其器件选型下，转移纹波并未把 dc-dc-stage 的损耗推到不可用区间。[pdf:E10]（PDF 物理页 10，Fig. 13）但这里比较的是 dc-dc-stage 而非整机效率，且两种方案使用不同原边器件和不同磁芯数量，不能把曲线差异只归因于 modulation。

### 问题 4：理论上需要多大的电容，体积和价格减少多少？

**实验。** Table III 用相同设计点比较传统约束 \(6\,\text{mF}\) 与 SSHPSM 约束 \(0.73\,\text{mF}\)，并按商业电容规格选型。传统方案为三只 \(2.4\,\text{mF}/1200\,\text{V}\) 并联，总体积 \(16.38\,\text{dm}^3\)，列示成本 899.4 美元；优化方案为单只 \(1\,\text{mF}/1200\,\text{V}\)，体积 \(2.49\,\text{dm}^3\)，列示成本 129.87 美元。[pdf:E09]（PDF 物理页 9，Table III）

**答案。** 对这组器件，体积和成本分别下降 85% 与 85.6%。这是“电容器件级”的选型结果，不是完整 PET 的体积或 bill of materials 结果。[pdf:E10]（PDF 物理页 10，Fig. 14）

### 问题 5：微小 gate mismatch 与漏感不一致会不会破坏 switched-capacitor 模式？

**实验。** 对两原边端口，作者设置 \(0.05^\circ\) 不同步、\(50\,\Omega\) 负载和 \(0.1\,\Omega\) 绕组电阻，并将漏感从 \(217\,\mu\text{H}\) 降到 \(1\,\mu\text{H}\)；小漏感时输出趋近输入，表现为 switched-capacitor 而不是 DAB 功率传输。进一步在约 \(2\,\mu\text{H}\) 漏感、漏感差小于 \(0.1\,\mu\text{H}\) 时观察三相端口，电容电压差小于 40 V，纹波小于 5.3%。[pdf:E10]（PDF 物理页 10，Fig. 15 与 Eq. (21)）[pdf:E11]（PDF 物理页 11，Fig. 16、Fig. 17）

**答案。** 在作者选择的窄偏差范围内，没有出现大的端口循环功率，纹波转移仍有效。另一个 \(L_T=1\)–\(6\,\mu\text{H}\)、各端 \(\pm5\%\) 偏差的解析 sweep 中，电流分配变化也很小。[pdf:E12]（PDF 物理页 12，Fig. 18）这不能外推到更大的 dead time、温漂、磁饱和、绕组电阻差或电容失配。

### 问题 6：低速电机和三相电压不对称时是否还能工作？

**实验。** 10 Hz 仿真中，作者保持 \(0.73\,\text{mF}\) 电容并观察 SM 电压和 HFT 电流；结果为 5% 电压纹波，副边主要保留净传能分量。[pdf:E13]（PDF 物理页 13，Fig. 20）并网不对称仿真让 phase-b 电压逐步跌至稳态值的 50%，同时把三相电流控制为对称；SM 电压纹波由 5% 增至 13%，LVdc 纹波由 0.15% 增至 1.2%。[pdf:E14]（PDF 物理页 14，Fig. 21）

**答案。** 低频本身没有让 SSHPSM 的电容约束重新变成 \(1/f_F\)，但 voltage asymmetry 会留下 zero-sequence ripple，因此“fault ride-through”成立的代价是允许更大的电容电压纹波，并非仍保持对称工况下的减容性能。

### 问题 7：硬件原型能否重复主要机制？

**实验。** 论文搭建 300 W、三电平 CHB-stage、每相 2 个 SM 的原型。Table V 给出 \(80\,\text{V}\) line-to-line RMS、40 V SM 与 LVdc 电压、50 Hz 基频、5 kHz CHB PWM、\(100\,\mu\text{F}\) SM 电容、1:1:1:1 HFT、3 mH 副边滤波电感、\(36\,\mu\text{H}\) 等效传能电感和 20 kHz SIQAB switching frequency。[pdf:E16]（PDF 物理页 16，Table V 与 Fig. 27）

**答案。** 50 Hz 对称工况下，实验示波图给出约 3% SM 电压纹波，并覆盖 80% 到满载的变化和功率反向；10 Hz 时纹波约 5%。[pdf:E16]（PDF 物理页 16，Fig. 28）[pdf:E17]（PDF 物理页 17，Fig. 29、Fig. 30）phase-b 电压跌落 50%、三相电流仍对称时，实验纹波由对称工况约 3% 增到 12.5%。[pdf:E17]（PDF 物理页 17，Fig. 31–33）[pdf:E18]（PDF 物理页 18，Section VII-B 与 Conclusion）这验证了低功率原型上的机制，但 300 W 到论文仿真的 1.2 MW 之间存在四个数量级的功率差，磁件、绝缘、寄生参数和热设计的规模效应尚未由硬件闭合。

## § 8 — Take-aways

**5 句话。** 第一，论文不是用控制器估计并抵消二倍频功率，而是用同步开关把三相 SM 电容临时构造成 switched-capacitor 网络。第二，小原边漏感使二倍频电流离开 SM 电容，并以 sideband 形式进入 HFT 原边。第三，三相对称性让这些 sideband 对应的主磁通相互抵消，因此电容约束可从基频储能转向 switching-cycle 电荷摆动。第四，作者在 1.2 MW PLECS 模型中比较了 \(6\,\text{mF}\) 与 \(0.73\,\text{mF}\)，并在 300 W 原型上用 \(100\,\mu\text{F}\) 电容验证了 50 Hz、10 Hz、功率反向和 phase-b 电压跌落工况。[pdf:E12]（PDF 物理页 12，Table IV）[pdf:E16]（PDF 物理页 16，Table V 与 Fig. 28）[pdf:E17]（PDF 物理页 17，Fig. 29–33）第五，最重要的边界是三相不对称会留下 zero-sequence ripple，而高功率硬件、长期器件应力和整机功率密度仍未验证。

**3 句话。** SSHPSM 把低频纹波从“每相电容必须存储的能量”改造成“原边三相可相互抵消的电流”。这一改变在论文的阻抗模型、磁路模型、仿真频谱和 300 W 示波图中得到相互一致的支持。[pdf:E06]（PDF 物理页 6，Eq. (7)–(10)）[pdf:E08]（PDF 物理页 8，Fig. 11）[pdf:E16]（PDF 物理页 16，Fig. 28）它不是无条件减容：小漏感、足够同步和足够三相对称是机制成立的前提。

**1 句话。** 这篇论文最值得记住的是：通过同步开关重构纹波的物理路径，可以比单纯增大电容或增加纹波控制环更直接地降低 CHB-PET 的本地储能需求。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**需要转移的低频纹波在三个原边端口上足够对称，同时原边连接保持足够低阻，使它们能在主磁通路径中互相抵消。**

该假设若失效，论文最核心的“电容只需按 switching ripple 选取”就会失效，因为未抵消分量最终仍要由 SM 电容吸收。论文自己已经给出这一失效机制：phase-b 电压跌落会产生 zero-sequence component；正、负序部分仍可抵消，但零序部分同相，不能靠三相对称消除。[pdf:E13]（PDF 物理页 13，Eq. (26) 后正文）仿真中 phase-b 跌至 50% 后，SM 纹波由 5% 增至 13%；300 W 实验中由约 3% 增至 12.5%。[pdf:E14]（PDF 物理页 14，Fig. 21）[pdf:E17]（PDF 物理页 17，Fig. 33）

论文为这项假设提供了两类有限证据：一是 \(0.05^\circ\) gate mismatch 和约 \(2\,\mu\text{H}\) 小漏感下的端口波形，二是 \(1\)–\(6\,\mu\text{H}\)、各端 \(\pm5\%\) 漏感偏差的解析 sweep。[pdf:E11]（PDF 物理页 11，Fig. 16、Fig. 17）[pdf:E12]（PDF 物理页 12，Fig. 18）但它没有同时叠加电容容差、dead time、温度漂移、磁芯局部饱和、采样/驱动 skew、负序或畸变电流、控制器饱和与高功率绝缘寄生，也没有给出允许纹波与器件寿命之间的边界。作者把 50% 电压跌落下的 12.5% 纹波称为“合理范围”，但 PDF 没有报告电容、电压裕量或保护规范来证明 12.5% 对目标设备必然可接受。[pdf:E18]（PDF 物理页 18，Section VII-B）

因此，最稳妥的结论是：论文证明了该机制对“小幅同步误差、小漏感不一致和单一电压跌落工况”具有可行性，而不是证明它对一般三相不平衡和全尺度寄生参数都鲁棒。

## § 10 — 最小复现实验

一周内最有价值的复现不是搭建完整 PET，而是在 PLECS 或 Simulink Specialized Power Systems 中建立论文 Table IV 的单个三相 CHB-SIQAB switching model，直接验证“二倍频电流从电容转移到原边、但不进入副边”。

**数据与模型。** 使用 \(750\,\text{V}\) SM、50 Hz、2 kHz CHB PWM、20 kHz SIQAB switching、1:1:1:1 HFT，以及每相 8 个等效 SM；先用 Mode 1 的 \(6\,\text{mF}\)，再切换到 Mode 2 的 \(0.73\,\text{mF}\)。[pdf:E12]（PDF 物理页 12，Table IV）论文未报告 solver 和 time step，因此复现者应自行做步长收敛：例如先把最大步长设为 20 kHz 周期的 \(1/100\)，再减半，直到纹波和 FFT 主分量变化低于预先设定的 1%。

**实现。** Mode 1 使用各原边端口独立 phase shift 和传统 QAB 连接；Mode 2 让三个原边全桥共用 \(\phi_{\mathrm{FB}}\)，副边使用 \(\phi_{\mathrm{FBL}}\)，并保留小原边漏感。只实现稳态功率传输、SM 电压平衡和同步 gate，不必先复现完整电机或并网控制。

**测量。**

- SM 电容电流的 100 Hz RMS/FFT 分量；
- SIQAB 原边与副边电流的 100 Hz envelope；
- 每相 SM 电压的 peak-to-peak ripple；
- 原边三相电流和磁动势之和；
- 在 \(L_T=1,2,4,6\,\mu\text{H}\) 及 \(0.05^\circ\) gate skew 下重复上述测量。

论文给出的可对照目标是：SM 电容 100 Hz 分量由约 76 A 降至约 1.125 A，而 dc-dc 原边输入的对应分量由约 0.5 A 增至约 71 A。[pdf:E15]（PDF 物理页 15，Fig. 23、Fig. 24）硬件参数可用 300 W 表格做第二阶段缩比核对，但不是第一周必须项。[pdf:E16]（PDF 物理页 16，Table V）

**支持条件。** 若 \(0.73\,\text{mF}\) 的 Mode 2 在相同功率点把 SM 电容 100 Hz 电流降低至少一个数量级、SM 电压纹波不高于 5%，并且被转移的低频包络出现在原边而不显著出现在副边，就支持核心 claim。[pdf:E14]（PDF 物理页 14，Fig. 22）[pdf:E15]（PDF 物理页 15，Fig. 23–25）

**反驳条件。** 若步长收敛后 100 Hz 电流仍主要流入 SM 电容，或它同样进入副边，或必须把电容重新增大到接近 \(6\,\text{mF}\) 才能维持 5% 纹波，则核心路径解释被反驳。完成稳态后再加入 phase-b 50% sag；若 zero-sequence 残量重现论文报告的纹波上升趋势，则可进一步闭合第 9 节的脆弱假设。[pdf:E17]（PDF 物理页 17，Fig. 31–33）

## § 11 — 最强反例设计

最强反例不是把 gate 信号任意打乱，而是构造一个目标应用中合理、且直接破坏“三相纹波对称”的工况：**深度不平衡电压与 current-control saturation 同时发生，使三相电流也无法维持对称，再叠加温升后的 dead-time skew 和 HFT 端口参数偏差。**

具体做法是从论文的 phase-b 50% sag 出发，[pdf:E17]（PDF 物理页 17，Fig. 31–33）继续 sweep sag depth、故障相角和正/负序功率指令；把电流限幅设在额定值附近，使 controller 在 fault ride-through 期间进入饱和；同时加入实测或保守的 SM 电容容差、绕组电阻差、\(L_T\) 偏差和 gate delay。每个工况都测量：

1. 三相 \(i_{\mathrm{SM}x,\mathrm{ac}}\) 的 positive、negative、zero-sequence 分解；
2. 留在电容中的低频电流与进入 HFT 原边的低频电流之比；
3. 主磁通峰值、原边 circulating current、器件 RMS/peak current；
4. SM 电压峰值与允许纹波越限时间；
5. 在 50 Hz 和 10 Hz 下，满足相同保护边界所需的最小电容。

论文的单一不平衡实验仍把三相电流控制为对称，[pdf:E18]（PDF 物理页 18，Section VII-B）因此它没有覆盖“电压和电流同时不对称”这个更强攻击。若上述试验发现，进入饱和后所需最小电容重新近似随 \(1/f_F\) 增长，或 100% 额定电压器件在保护动作前已越过 ripple/peak limit，那么“SSHPSM 电容约束基本不受低频和故障影响”的外推就不成立。相反，如果在这些组合扰动下仍能保持低残余电容电流、可接受磁通和器件应力，论文最脆弱的假设才得到真正加强。

## § 12 — Follow-up Research Idea

在 power electronics 领域，高影响结果通常不只需要一个更小的仿真参数，还要同时闭合损耗、器件应力、磁件可制造性、故障边界和有代表性功率等级的硬件。基于第 9 节的限制，一个值得研究的非增量候选方向是：**把“依靠三相天然对称来抵消纹波”改写为“对任意 sequence component 都可观测、可路由的 sequence-complete energy port”。**

这个想法不是简单加一个更大的电容。可以在多绕组 HFT 与原边桥的调制自由度中显式增加 zero-sequence energy channel：正常对称工况仍使用 SSHPSM 的被动抵消；检测到负序和零序能量后，通过 common-mode phase 或可重构绕组连接，把不能相消的分量定向送往 LVdc、一个跨三相共享的小储能端口，或受控的磁能通道。其目标从“在对称条件下降低每相电容”变为“在任意序分量下最小化总储能并约束所有器件应力”。

**(a) 未满足需求。** 论文已经显示 phase-b 50% sag 会把实验 SM 纹波从约 3% 推到 12.5%，说明真正限制减容的不是稳态二倍频，而是故障下无法相消的 zero-sequence energy。[pdf:E17]（PDF 物理页 17，Fig. 33）

**(b) 潜在研究价值。** 若同一硬件能在对称工况保持低损耗、在不对称和 current limit 工况下主动路由零序能量，并在中功率原型上证明电容、磁通和半导体应力的联合边界，就会把论文的条件性机制推进成可用于保护设计的系统方法。

**(c) 可借鉴工具。** 可借鉴 symmetrical-component observer、MMC arm-energy balancing、active power decoupling 的功率坐标变换，以及 robust model-predictive control；FPGA 可用于实现低延迟 sequence decomposition 和可预测的 gate scheduling，但这只是执行工具，论文没有提供现成 FPGA 架构。

**(d) 首个证伪实验。** 在带可编程三相电源的多 SM 原型上同时 sweep sag depth、负序电流、功率反向、10–50 Hz、gate skew 和漏感/电容失配。若新增 sequence channel 不能在相同总电容下把最坏 SM ripple 和磁通峰值同时压到预设边界，或其额外开关损耗抵消了减容收益，这个想法即被证伪。

**(e) 与本文的实质区别。** 本文把 zero-sequence 视为不能抵消、最终由三相互联电容吸收的残量；候选方向则把它定义为必须显式分配的独立能量流，并把目标函数扩展到 fault envelope 下的总储能、损耗与器件应力联合最小化。[pdf:E14]（PDF 物理页 14，Eq. (28) 及其后正文）由于本任务严格只使用源 PDF，尚未对相邻工作的专利与论文做完整检索，因此该方向仅是证据约束下的候选想法，不声称 novelty。
