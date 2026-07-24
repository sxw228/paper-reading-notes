# An improved control method for unified power quality conditioner with unbalanced load

**作者**：Ashish Patel，H. D. Mathur，Surekha Bhanot  
**出处**：Electrical Power and Energy Systems，100，129–138  
**年份**：2018  
**DOI**：10.1016/j.ijepes.2018.02.035  
**Zotero key**：CG5WUJQN  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是三相三线制统一电能质量调节器（Unified Power Quality Conditioner，UPQC）在**负载不平衡**时出现的两个耦合问题。第一，传统功率角控制（Power Angle Control，PAC）让串联有源电力滤波器（series APF）与并联有源电力滤波器（shunt APF）平均分担负载无功功率；但串联 APF 只能注入三相平衡功率，按总量平均分配可能使某一相的并联 APF 被迫吸收串联 APF 多送出的无功，从而形成两个变换器之间的无功环流，增加损耗和 UPQC 的总 VA 负担。第二，并联 APF 为补偿不平衡电流而从公共 DC link 交换脉动功率，DC link 电压出现二次频率纹波；这些纹波经 PI 控制器进入源电流参考值，使补偿后的三相源电流仍不够平衡、谐波也更大。作者把这两点作为改进控制的核心对象，并用 Opal-RT 实时仿真验证。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E03]（PDF 物理页 2，Section 1 末段与贡献列表）

这个问题重要，不只是因为“电流波形不好看”。UPQC 的串联 APF 负责电压质量与部分无功支撑，并联 APF 负责负载电流补偿和 DC link 调节，二者共用 DC link；因此无功分配错误会直接抬高器件电流、变压器与变流器容量需求，而 DC link 纹波又会反过来污染源侧电流。论文采用的三相三线 UPQC 拓扑、串并联 APF、注入变压器、接口电感和公共 DC link 的物理关系见 Fig. 1。[pdf:E02]（PDF 物理页 2，Fig. 1）从工程角度看，论文的价值在于同时针对**容量利用率**与**源侧电能质量**，而不是只改进其中一个闭环。

## § 2 — 前人工作与不足

论文对前人工作的判断可分为三层。第一，常规 UPQC 控制已经能用 IRPT/p–q theory、SRFT/d–q theory 或 UVTG 生成补偿参考量，但 IRPT 对非理想源电压较敏感；已有 SRFT-PAC 工作又没有把 sag/swell 补偿完整纳入串联 APF 控制。第二，已有 PAC 通过功率角让串联 APF 分担无功、提高其利用率，但基于源电压参考系的等 VA 分配只在功率角很小时较准确；更关键的是，已有方法没有处理不平衡负载下的无功环流。第三，已有研究曾用 sinusoidal integration block 或 proportional-resonant controller 抑制 DC link 二次纹波，但论文认为这些方案计算更复杂、控制负担更大且动态较慢。[pdf:E03]（PDF 物理页 2，Section 1）这些是**论文对相关文献的概括**，本卡未用外部全文独立复核。

最相关的基线是文献 [16] 的 SRFT-PAC：无论负载是否平衡，都让串联与并联 APF 平均分担总无功。论文指出，这个总量层面的“平均”忽略了串联 APF 的三相平衡输出约束；当最低无功相所需功率小于串联 APF 固定分到的每相功率时，并联 APF 在该相会变成无功吸收者。[pdf:E05]（PDF 物理页 3，Eq. 12–17 与 Section 3）因此，前人方法的不足不是简单的“没有考虑不平衡”，而是**分配变量选错了层级**：它按三相总无功分配，却没有先检查逐相可行性。

## § 3 — 重建作者的思考路径

可以从既有 UPQC 物理约束逆向重建出这篇论文的思路。首先，若串联 APF 只在 sag/swell 时工作，其额定容量在正常工况下长期闲置；PAC 通过让负载电压相对源电压形成相角，使串联 APF 在正常工况也传递无功。功率角受串联注入电压额定值限制，论文用电压 phasor 得到随供电电压变化的最大角度 \(\delta_{\max}\)，并用负载有功与分配给串联 APF 的无功计算所需角度 \(\delta_C\)。[pdf:E04]（PDF 物理页 3，Fig. 2，Eq. 5–11）

其次，把“总无功一半给串联 APF”展开到逐相后，会发现串联 APF 每相都给 \(Q_T/6\)，而不平衡负载的最低无功相可能根本不需要这么多；于是该相并联 APF 的无功指令变为负值，出现一边送、一边吸的环流。继续按绝对值计算两台 APF 的 VA，就会得到 UPQC 总 VA 大于负载总无功的结果。[pdf:E05]（PDF 物理页 3，Eq. 12–17）[pdf:E06]（PDF 物理页 4，Eq. 18–23）这一步把一个看似“公平”的分配策略转化成了可证明的过载条件。

最后，即使无功分配被修正，并联 APF 在补偿负序/不平衡电流时仍会使 DC link 产生二次纹波。传统 PI 不会自动拒绝这个周期分量，反而把它带入 d-axis 源电流参考；既然目标纹波频率已知，用一个窗口正好覆盖一个纹波周期的 moving average，就可以在不引入低截止频率低通滤波器的情况下把该正弦项平均为零。[pdf:E07]（PDF 物理页 4，Section 4.1 与 Fig. 3）[pdf:E08]（PDF 物理页 4，Eq. 25–29）于是论文自然形成两个模块：**可行的逐相无功分配**与**针对二次纹波的有限窗平均**。

## § 4 — 核心 Intuition

不要先把总无功平均分给两台 APF，而要先问：串联 APF 的三相平衡无功输出，在每一相是否都不会超过负载需求；若会超过，就只让串联 APF承担负载中可被三相平衡表示的部分，其余不平衡无功全部交给并联 APF。[pdf:E10]（PDF 物理页 5，Section 4.2.1）同时，把 DC link PI 输出在一个二次纹波周期内取平均，保留维持平均 DC 电压所需的直流分量并抵消周期纹波。[pdf:E08]（PDF 物理页 4，Eq. 25–29）核心不是增加更复杂的控制器，而是把两个错误的“平均”改成两个正确的“平均”：无功分配按逐相可行性平均，DC 控制按纹波周期平均。

## § 5 — 具体方法与完整 Pipeline

论文的完整 pipeline 如下。

1. **采样与系统对象**。输入包括三相源电压、负载电压、负载电流、源电流和 DC link 电压；被控对象是共享 DC link 的串联与并联两套三相 IGBT bridge。串联 APF 经单相注入变压器串入线路，并联 APF 经接口电感并接到 PCC。[pdf:E02]（PDF 物理页 2，Fig. 1）

2. **并联 APF 电流参考生成**。三相 PLL 提供 \(\omega t\)，Park transform 把负载电流从 abc 变到 dq0；低通滤波提取基波分量。DC link 电压误差进入 PI，PI 输出再通过 mean block，得到去除二次纹波的 DC 电流补偿量；该量与 d-axis 负载分量组合后，经 inverse Park transform 得到平衡正弦源电流参考，最后由 hysteresis current controller 产生并联 APF gate pulses。[pdf:E07]（PDF 物理页 4，Fig. 3 与 Section 4.1）

3. **逐相功率测量与无功分解**。每相用单相 Fourier-transform P–Q measurement block 得到 \(P_{La},P_{Lb},P_{Lc}\) 与 \(Q_{La},Q_{Lb},Q_{Lc}\)。算法定义平衡无功 \(Q_{Bal}=3\min(Q_{La},Q_{Lb},Q_{Lc})\)，总无功 \(Q_T=Q_{La}+Q_{Lb}+Q_{Lc}\)，不平衡无功 \(Q_{Unb}=Q_T-Q_{Bal}\)。[pdf:E09]（PDF 物理页 5，Fig. 4）

4. **选择无功分配规则**。若 \(Q_{Unb}\le Q_T/2\)，作者认为不会发生环流，串联与并联 APF 各承担 \(Q_T/2\)；若 \(Q_{Unb}>Q_T/2\)，串联 APF 只承担 \(Q_{Bal}\)，并联 APF 承担剩余的不平衡无功。该分支是论文避免环流与过载的关键。[pdf:E10]（PDF 物理页 5，Section 4.2.1）

5. **计算功率角与限幅**。由分给串联 APF 的 \(Q_{Sr}\) 和负载有功 \(P_L\) 得到候选角 \(\delta_C\)；由当前最小相电压与串联 APF 额定注入能力得到 \(\delta_{\max}\)。最终角度取 \(\delta_F=\min(\delta_C,\delta_{\max})\)，并在除法处使用 limiter 避免零分母。[pdf:E04]（PDF 物理页 3，Eq. 9–11）[pdf:E09]（PDF 物理页 5，Fig. 4）

6. **串联 APF 电压参考生成**。PLL 相位加上 \(\delta_F\) 后生成三相平衡 unit vectors；参考负载电压幅值与这些 unit vectors 相乘形成三相参考负载电压，再由 voltage PWM controller 产生串联 APF gate pulses。Eq. 30 给出相差 \(2\pi/3\) 的三相模板。[pdf:E11]（PDF 物理页 5，Eq. 30）[pdf:E12]（PDF 物理页 5，Fig. 5）

7. **实时执行划分**。论文在 Opal-RT OP4510 上把电力电子电路放到 FPGA computational engine，以 0.5 μs 步长运行；控制算法放到 CPU core，以 15 μs 步长运行，二者经 PCI bus 同步交换测量量和 PWM pulses。[pdf:E13]（PDF 物理页 5，Section 5）[pdf:E14]（PDF 物理页 6，Fig. 6）这属于 real-time digital simulation，而不是一套实物 UPQC 功率样机。

论文给出的具体工况是 415 V、50 Hz 三相源，DC link 为 700 V/5500 μF；负载由三相 diode bridge rectifier、每相 8 Ω 与 5 mH 的平衡 Y 接 RL，以及跨 a–c 相的 8 Ω/40 mH 不平衡支路组成。[pdf:E14]（PDF 物理页 6，Table 1）在这个例子里，算法输入三相瞬时量，输出两套变换器的 gate pulses，目标是让源电流平衡、正弦且与源电压同相，同时让负载电压保持平衡并满足 sag/swell 补偿。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有两组核心推导。

**第一组：功率角约束与无功环流。** 设 \(f_S\) 是供电电压相对额定值的比例，\(f_{Sr,\max}\) 是串联 APF 最大注入电压相对额定源电压的比例，则 phasor 几何给出

\[
\delta_{\max}=\cos^{-1}\!\left(\frac{1+f_S^2-f_{Sr,\max}^2}{2f_S}\right),
\qquad
\delta_C=\sin^{-1}\!\left(\frac{Q_{Sr}}{P_L}\right).
\]

前者表示在当前 sag/swell 条件下，串联 APF 不超过额定注入电压所允许的最大功率角；后者表示为了传递指定串联无功所需的角度。[pdf:E04]（PDF 物理页 3，Eq. 9–11）

对不平衡负载，令 \(Q_T=Q_{La}+Q_{Lb}+Q_{Lc}\)，假设 \(Q_{La}\) 是三相中最小者。传统平均分配令串联 APF 总共承担 \(Q_T/2\)，因此每相固定注入 \(Q_T/6\)，并联 APF 的 a 相无功为

\[
Q_{Sha}=Q_{La}-\frac{Q_T}{6}.
\]

若平衡无功 \(Q_{Bal}=3Q_{La}<Q_T/2\)，就有 \(Q_{Sha}<0\)：串联 APF 在 a 相送出的无功超过负载需求，并联 APF 必须反向吸收。论文继续按两个 APF 无功绝对值相加，推得

\[
VA_{UPQC}>Q_{La}+Q_{Lb}+Q_{Lc}=Q_T,
\]

即变换器处理的总 VA 超过负载实际所需无功。[pdf:E05]（PDF 物理页 3，Eq. 12–17）[pdf:E06]（PDF 物理页 4，Eq. 18–23）这个推导的物理意义是：**三相总功率守恒并不保证逐相没有内部功率循环**。

**第二组：moving average 对二次纹波的消除。** 论文把 DC link 电压误差写成

\[
E_{DC}(t)=E_0+E_2\cos(\omega_2t+\phi_2),
\]

PI 输出为

\[
I_{DC}(t)=K_P E_{DC}(t)+K_I\int_0^t E_{DC}(\tau)\,d\tau.
\]

因此比例项和积分项都含有 \(\omega_2\) 纹波。对 \(I_{DC}\) 在长度 \(2\pi/\omega\) 的运行窗口上求平均；当 mean block 的频率参数满足 \(\omega=\omega_2\) 时，窗口恰好覆盖一个纹波周期，正弦与余弦项的积分为零，只留下维持 DC link 平均电压所需的慢变量。[pdf:E08]（PDF 物理页 4，Eq. 25–29）这解释了为什么作者选择 moving average 而不是低截止频率 low-pass filter：后者也能衰减纹波，但通常会引入更明显的瞬态延迟。

论文还定义了三相量的 percentage unbalance：

\[
\%Unb=\frac{|I_{a,rms}-I_{b,rms}|+|I_{b,rms}-I_{c,rms}|+|I_{c,rms}-I_{a,rms}|}
{I_{a,rms}+I_{b,rms}+I_{c,rms}}\times100.
\]

它衡量三相 RMS 两两差值相对于总 RMS 的比例，用于比较源电流平衡程度。[pdf:E16]（PDF 物理页 7，Eq. 31）这是论文自定义指标，不等同于基于正序/负序分量的标准 voltage/current unbalance factor。

## § 7 — 实验设计与结论

**问题 1：mean block 是否改善稳态源电流质量？** 论文同时接入非线性、平衡 RL 和不平衡 RL 三类负载，先展示 proposed control 下负载电流不平衡且含谐波、并联 APF 注入补偿电流、源电流变得近似平衡正弦；该稳态工况中负载电流 THD 为 10.51%，源电流 THD 为 3.77%，DC link 仍可见二次纹波。[pdf:E15]（PDF 物理页 6，Fig. 7–8 与 Section 6.1）随后用三种控制对比：无 UPQC 时源电流 unbalance/THD 为 27.93%/10.51%，基线“无 mean block”是 2.66%/4.38%，proposed control 是 0.11%/3.59%。答案是：在这组负载与参数下，mean block 显著降低不平衡，并小幅进一步降低 THD。[pdf:E16]（PDF 物理页 7，Table 2 与 Fig. 11）需要注意，Section 6.1 正文另报 proposed steady-state source-current THD 为 3.77%，与 Table 2 的 3.59% 不一致；论文没有解释两者是否来自不同时间窗或 FFT 设置，因此精确 THD 改善幅度存在轻微报告不一致。[pdf:E15]（PDF 物理页 6，Section 6.1）[pdf:E16]（PDF 物理页 7，Table 2）

**问题 2：新的无功分配是否降低 UPQC 总 VA？** 论文用同一不平衡工况比较文献 [16] 式平均分配与 proposed allocation。基线下并联/串联 APF 分别为 12.9 kVA 和 6.9 kVA，总负担 19.8 kVA；proposed control 分别为 13.9 kVA 和 4.4 kVA，总负担 18.3 kVA。[pdf:E17]（PDF 物理页 7，Table 3）论文给出的负载无功为 14.3 kVAr，其中 10 kVAr 不平衡、4.3 kVAr 平衡；新方法让串联 APF 只承担 4.3 kVAr 平衡部分，报告总 VA 相比基线下降 7.6%。[pdf:E18]（PDF 物理页 8，Section 6.1–6.2）答案是：总 VA 降低，但负担不是两台变换器都下降，而是串联 APF 显著减载、并联 APF 略增载。

**问题 3：供电电压 sag/swell 时能否维持负载电压并恢复 DC link？** 对三相 25% sag，串联 APF 增加同相电压分量，负载电压保持不变；DC link 出现 32 V（4.6%）undershoot，并在 0.15 s 内恢复。[pdf:E18]（PDF 物理页 8，Fig. 12 与 Section 6.2）对 25% swell，串联 APF 注入反相有功分量，DC link 出现 26 V（3.7%）overshoot，也在 0.15 s 内恢复。[pdf:E19]（PDF 物理页 8，Fig. 13 与 Section 6.3）答案是：在这两个阶跃扰动下，负载电压维持，DC link 有短暂偏移但能恢复。

**问题 4：负载突变时控制是否稳定？** 论文在运行中接入不平衡 load-3；源电流约 0.07 s 稳定，负载电压与电流约 0.01 s 稳定，DC link 发生 17 V（2.4%）undershoot 并在 0.05 s 内恢复。[pdf:E19]（PDF 物理页 8，Fig. 14 与 Section 6.4）答案是：该特定负载阶跃下闭环没有失稳，但 source-current transient 明显慢于负载端电压/电流。

**问题 5：单相电压 sag 与功率角调度是否合理？** 论文对 phase A 施加 25% sag，series APF 注入不平衡补偿电压，三相负载电压保持平衡，DC link 只有较小 undershoot；同时报告稳态 \(\delta_{\max}=23.1^\circ\)，负载接入时 \(\delta_C\) 从 3.5° 变为 6.0°，最终角度取两者较小值，因此测试中实际由 \(\delta_C\) 决定。[pdf:E20]（PDF 物理页 9，Fig. 15–17 与 Sections 6.5–6.6）答案是：限幅逻辑在所测工况没有成为瓶颈。

验证边界必须说清：这是 Opal-RT real-time simulation，电路模型在 FPGA 上、控制在 CPU 上运行，且只测试了 Table 1 的单一三相三线拓扑、一个主要基线和有限的负载/电压扰动。[pdf:E13]（PDF 物理页 5，Section 5）[pdf:E14]（PDF 物理页 6，Fig. 6 与 Table 1）因此结果支持“该模型与工况下实时可运行并改善指标”，不能直接外推为大功率实物样机的效率、热设计、器件应力、传感噪声鲁棒性或并网标准合规性。

## § 8 — Take-aways

**5 句话版：** ① 传统 PAC 的问题不是无功总量不足，而是把总量平均分配后可能在逐相层面制造内部无功环流。[pdf:E05]（PDF 物理页 3，Eq. 12–17）② 新方法先用三相最小相无功定义可由串联 APF 平衡承担的部分，再决定是平均分配还是把不平衡部分交给并联 APF。[pdf:E09]（PDF 物理页 5，Fig. 4）③ PI 后的 moving average 在窗口频率等于 DC link 二次纹波频率时，可把该周期分量平均为零。[pdf:E08]（PDF 物理页 4，Eq. 25–29）④ 在论文工况中，source-current unbalance 从基线 2.66% 降到 0.11%，THD 从 4.38% 降到 3.59%，UPQC 总 VA 从 19.8 kVA 降到 18.3 kVA。[pdf:E16]（PDF 物理页 7，Table 2）[pdf:E17]（PDF 物理页 7，Table 3）⑤ 这些结论来自 CPU–FPGA 分区的 Opal-RT 实时仿真，而非实物功率级实验。[pdf:E13]（PDF 物理页 5，Section 5）

**3 句话版：** 论文用逐相可行性修正 PAC 无功分配，并用一个纹波周期的 moving average 修正 DC link PI 输出。理论上它解释了平均分配为何在不平衡负载下产生环流，实验上报告了更低的源电流不平衡、THD 和总 VA 负担。[pdf:E21]（PDF 物理页 10，Conclusion）但证据范围仍局限于一套实时仿真模型和同号感性无功负载。

**1 句话版：** 这篇论文最值得记住的是：UPQC 的无功共享必须尊重逐相功率可行性，而 DC link 的周期纹波应在进入电流参考前被针对性消除。

## § 9 — 最脆弱的假设

最脆弱的假设是：**三相负载无功可以用 \(Q_{Bal}=3\min(Q_{La},Q_{Lb},Q_{Lc})\) 分解为“平衡部分 + 非负不平衡部分”，且三相无功需求具有相同符号。** 这是 Fig. 4 分配逻辑和“无环流”证明共同依赖的前提。[pdf:E09]（PDF 物理页 5，Fig. 4）[pdf:E10]（PDF 物理页 5，Section 4.2.1）论文没有明确写出“各相无功必须同为感性”这一假设，但 Eq. 18 把最小相无功直接乘三作为平衡部分，证明也把该最小值当作正的负载需求。[pdf:E06]（PDF 物理页 4，Eq. 18–23）

这个假设在实际配电系统中可能因单相电容补偿、不同相的光伏逆变器 Volt–VAR 控制、轻载电缆容性、相间负载或符号变化的动态无功而失效。若某一相是 capacitive、另两相是 inductive，\(\min(Q_i)\) 可能为负；此时算法得到的“平衡无功”也为负，分配器可能命令串联 APF 吸收无功、并联 APF 同时供应更大的正无功，重新制造它试图消除的环流。这是**基于论文公式的推断**，不是作者报告的实验现象。

论文提供的证据不足以覆盖这个假设：Table 1 的可控负载是 diode rectifier、平衡 RL 和跨相 RL，均未形成一相容性、两相感性的 mixed-sign reactive-power case。[pdf:E14]（PDF 物理页 6，Table 1）因此，论文证明的是其负载类别下的无环流，不是任意不平衡负载下的无环流。

## § 10 — 最小复现实验

一周内最有价值的复现不是重建完整 Opal-RT 平台，而是在 MATLAB/Simulink、PLECS 或等价 switching/averaged model 中复现**无功分配与 mean-block 两个关键 claim**。

- 按 Table 1 建立 415 V、50 Hz、700 V DC link 的三相三线 UPQC；可以先用 averaged converter 降低建模成本，再用较短的 switching run 检查趋势。[pdf:E14]（PDF 物理页 6，Table 1）
- 实现两个控制器：基线为总无功平均分配且 PI 后无 mean block；proposed 版本使用 Fig. 4 的分支规则，并在 DC PI 后加入一个 100 Hz 窗口的 moving average。[pdf:E09]（PDF 物理页 5，Fig. 4）[pdf:E08]（PDF 物理页 4，Eq. 25–29）
- 先运行论文负载组合，再增加一个 mixed-sign case；记录每相 series/shunt reactive power、两个变换器总 kVA、DC-link ripple、源电流 THD 和 Eq. 31 的 percentage unbalance。[pdf:E16]（PDF 物理页 7，Eq. 31）
- 支持论文 claim 的最低标准是：在论文负载下重现“proposed 比基线更低”的方向，并接近 2.66%→0.11%、4.38%→3.59% 和 19.8→18.3 kVA 的报告结果。[pdf:E16]（PDF 物理页 7，Table 2）[pdf:E17]（PDF 物理页 7，Table 3）
- 反驳标准是：在相同测量与功率符号定义下，proposed control 仍出现某相 series APF 供无功而 shunt APF 吸收无功，或总变换器 VA 不降反升；若只在 mixed-sign case 失败，则反驳的是论文 claim 的适用范围，而不是论文给出的同号 RL 工况结果。

这个实验不需要复现 0.5 μs FPGA 电路步长，因为要验证的第一性问题是分配逻辑是否产生环流；待逻辑通过后，再做实时性与 switching fidelity 验证。

## § 11 — 最强反例设计

最强反例是构造一个**总无功仍为感性、但逐相无功符号混合**的负载。令 \(Q_{La}=-2\) kVAr、\(Q_{Lb}=5\) kVAr、\(Q_{Lc}=5\) kVAr，并保持正的总有功 \(P_L\)。按论文规则，\(Q_T=8\) kVAr，\(Q_{Bal}=3\min(Q_i)=-6\) kVAr，\(Q_{Unb}=Q_T-Q_{Bal}=14\) kVAr；由于 \(14>Q_T/2=4\)，Fig. 4 的分支会令串联 APF 承担 \(-6\) kVAr、并联 APF 承担 14 kVAr。[pdf:E09]（PDF 物理页 5，Fig. 4）[pdf:E10]（PDF 物理页 5，Section 4.2.1）

这意味着串联侧吸收 6 kVAr、并联侧供应 14 kVAr，内部至少有 6 kVAr 反向交换，恰好构成论文声称要避免的无功环流；同时 \(\delta_C=\sin^{-1}(Q_{Sr}/P_L)\) 变成负功率角。[pdf:E04]（PDF 物理页 3，Eq. 10）若实现中允许该负角，控制目标被直接反例推翻；若实现中对负值做 clamp，实际算法就不再是论文给出的分配律，并可能留下未补偿无功。这个反例的力量在于它不是调参数让控制器“表现差一点”，而是利用公式本身证明其无环流保证依赖未声明的同号无功域。

## § 12 — Follow-up Research Idea

**候选研究方向：面向任意符号逐相功率的、带可行性证书的 UPQC 联合功率分配控制。** 由于本任务只允许使用源 PDF、未检索外部相关工作，下面不声称 novelty。

(a) **未满足需求**：现有规则用 \(3\min(Q_i)\) 和一个阈值把无功分成平衡/不平衡两块，无法保证 mixed-sign、快速变化或含负序功率时仍无环流；同时它只间接考虑 converter VA 与 DC-link ripple。[pdf:E09]（PDF 物理页 5，Fig. 4）

(b) **潜在研究价值**：把“避免环流”从经验分支改成显式约束，可以给出逐相功率守恒、converter current/VA limit、DC-link energy balance 和负载电压质量的可行性证书。对电力电子与控制领域，高影响价值来自可证明的安全边界、实时实现和实物样机，而不只是多一个波形对比。

(c) **相邻领域工具**：可借鉴 constrained model predictive control、convex power-flow allocation、symmetrical components 和 robust/adaptive estimation。优化变量直接设为每相 series/shunt active-reactive power 或电压/电流参考，目标函数最小化两变换器总 RMS current、内部无功交换和 DC-link ripple；约束中加入 PWM、电压、电流、transformer VA 与动态能量限制。

(d) **首个可证伪实验**：先用第 11 节 mixed-sign 工况做离线/实时仿真；要求所有相满足负载功率平衡、series/shunt 同一相不出现相反方向的无功交换，并在 15 μs 控制预算内收敛。若优化器频繁不可行、总 VA 不低于现有规则，或实时计算超时，这个方向就被早期证伪。论文当前 CPU–FPGA 分区与步长可作为执行预算参考。[pdf:E13]（PDF 物理页 5，Section 5）

(e) **与本文的实质区别**：本文是“先用最小相定义平衡无功，再按阈值选两条规则”；候选方法则把 UPQC 重新定义为一个**逐相、带硬约束的动态功率路由问题**，由求解器或显式控制律在每个采样周期产生可行分配，并输出可验证的无环流证书。后续若能在真实功率级而非仅 FPGA 电路模型上验证效率、热应力与扰动鲁棒性，才构成相对于本文实时仿真的实质推进。[pdf:E14]（PDF 物理页 6，Fig. 6 与 Table 1）
