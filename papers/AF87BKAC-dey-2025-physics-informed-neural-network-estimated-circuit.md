# Physics Informed Neural Network—Estimated Circuit Parameter Adaptive Modulation of DAB

- 作者：Saikat Dey；Ayan Mallik
- 出处：IEEE Transactions on Power Electronics，Vol. 40，No. 10
- 年份：2025
- DOI：10.1109/TPEL.2025.3574873
- Zotero key：AF87BKAC

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的是一个很具体的控制失配问题：loss-optimized triple-phase-shift（TPS）通常假定 DAB 的串联电感和寄生电阻已知且不变，但电感会随磁通密度、温度、气隙和开关频率变化，器件导通电阻也会受温度和退化影响。控制器若仍使用名义参数计算 \(\delta_p\)、\(\delta_s\) 和 \(\phi\)，原本的“最优”工作点可能变成高 RMS 电流、丢失 ZVS、效率下降甚至热设计恶化的工作点。作者因此要用低带宽的直流侧电压、电流和既有控制量，在线估计影响功率流的等效串联电感 \(L_t\) 与等效寄生电阻 \(R_t\)，再让调制器随参数变化更新 TPS duty，而不是把参数漂移当成不可见扰动。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）[pdf:E02]（PDF 物理页 2，Section I）

这个问题的重要性来自高频 DAB 的损耗机制：在 100 kHz GaN 原型中，有限的 MOSFET \(C_{\mathrm{oss}}\)、deadtime 和寄生参数会共同决定换流时是否真正实现 ZVS；电感变化不仅改变功率基值，还会移动 soft-switching 区域。论文的 2 kW 实验把总等效串联电感人为降低 30%，发现冻结名义参数的 TPS 扩大了 partial-ZVS/hard-switching 区，而参数自适应 TPS 的全工况平均效率高出约 1.4%、最高高出 3.2%。这说明参数误差并非只影响“模型精度”，而会直接变成可测的开关损耗和电流应力。[pdf:E16]（PDF 物理页 16，Section VI 与 Table V）[pdf:E17]（PDF 物理页 17，Figs. 20–22）

论文所展示的价值有两层。第一层是控制价值：在不让神经网络进入 100 kHz switching-cycle 关键路径的前提下，慢速更新参数、快速更新调制 duty。第二层是诊断价值：同一估计量还可能服务于 component health monitoring；不过本文真正实验闭合的是参数自适应调制，而不是器件寿命诊断。

## § 2 — 前人工作与不足

以下是作者在论文中对相关工作的归纳，未在本卡中独立复核每篇引用文献。

对 DAB modulation optimization，作者把已有实现分成三类。closed-form 方法基于理想、无损的 time-domain model，表达式简单、适合数字控制器，却忽略寄生参数、deadtime 和 switching loss，容易把 duty 推向真实硬件的次优点；LUT 方法可以容纳更精细的非理想模型，但存储容量与网格分辨率直接冲突；ANN 直接预测最优相移，省去在线数值优化，却需要大量仿真或硬件数据，而且训练标签仍会继承所用 DAB 模型的误差。[pdf:E01]（PDF 物理页 1，Section I）[pdf:E02]（PDF 物理页 2，Section I）

对参数估计，作者同样指出三条不充分的路径。高带宽电流采样加 volt-second law 可以估计电感，但传感器昂贵、易受噪声影响，而且不给出寄生电阻；理想 DAB 模型的反算不需要额外学习器，却因真实损耗和非理想性而产生较大误差；已有 GA/ANN 或 PINN 工作多在较简单 converter、SPS 或较低开关频率下验证，且没有把估计器闭合进一个真实硬件的并行实时控制架构。作者引用的 buck-converter PINN 报告约 ±5% 平均预测误差，但本文认为其 converter 复杂度和控制自由度不足以直接覆盖 100 kHz TPS DAB。[pdf:E02]（PDF 物理页 2，Section I）

本文试图补上的缺口不是“再换一种 NN”，而是把四个此前分离的环节接成一条链：nonideality-inclusive 物理模型、loss-optimal TPS 合成、data-light 参数估计、以及不阻塞主控制器的在线部署。[pdf:E03]（PDF 物理页 3，Fig. 1 与 contributions）

## § 3 — 重建作者的思考路径

下面是基于论文证据的合理重建，不是作者逐字给出的研究日志。

1. TPS 有三个调制自由度，理论上比 SPS/DPS 更有机会同时降低 RMS 电流和 switching loss；但只有在模型能正确描述寄生参数、deadtime 和 \(C_{\mathrm{oss}}\) 换流时，这些自由度才会导向真实硬件的低损耗点。传统 ideal lossless model 对电感反算可产生 5%–20% 的误差，因此先要提高物理模型保真度。[pdf:E04]（PDF 物理页 4，Section II-A/II-B）
2. 即使离线找到了最优 TPS，真实 \(L\) 与 \(R_{\mathrm{ds,on}}\) 仍会漂移；把最优 duty 只写成电压与功率的函数，不足以长期保持同一损耗最小点。[pdf:E02]（PDF 物理页 2，Section I）
3. 直接测高频电流或用理想模型反算参数各有明显缺陷，纯 data-driven NN 又需要大量硬件标签。因此，一个能接近硬件的解析模型可以同时承担两件事：生成补充训练数据，并把功率守恒/功率流一致性写入训练 loss。
4. 在线控制不能等待复杂优化或 PC 推理。于是将时间尺度拆开：DSP 在快路径中计算低阶 polynomial duty 并由 PI 产生 \(\phi\)，PC 上的 NN 只在慢路径中估计 \(L_t,R_t\)，通过 SPI 间歇更新。[pdf:E14]（PDF 物理页 14，Section V-A/V-B）[pdf:E15]（PDF 物理页 15，Section V-C）
5. 最终自然形成“离线精细建模与优化—混合数据训练—在线慢估计—DSP 快调制”的结构，而不是让 NN 端到端接管 gate generation。

## § 4 — 核心 Intuition

核心 intuition 是：不要让神经网络直接猜每个 switching-cycle 的最优 gate，而让它只估计会缓慢移动最优点的两个 lumped circuit parameters，再把这两个量交给已经由物理模型离线求好的 duty map。物理模型既约束 NN 学到的参数必须能解释输入/输出功率，又用于构造 loss-optimal TPS map。这样，参数漂移只需触发低频率的 \(L_t,R_t\) 更新，DSP 的快速电压环和 duty 计算不必等待 NN。[pdf:E03]（PDF 物理页 3，Fig. 1）[pdf:E15]（PDF 物理页 15，Section V-C）

## § 5 — 具体方法与完整 Pipeline

完整 pipeline 分为离线建模、离线训练和在线控制三部分。

1. **建立 NIFDM。** 作者把 primary/secondary bridge 的 quasi-square voltage 展开为奇次 Fourier harmonics，在每个 harmonic 上建立包含漏感、磁化电感、频变 winding resistance、capacitor ESR、transformer intra/inter-winding capacitance 与 switch on-resistance 的等效网络；随后加入 deadtime 期间 MOSFET \(C_{\mathrm{oss}}\) 充放电形成的非理想 bridge voltage，并计算 conduction、switching 与 magnetic core loss。[pdf:E04]（PDF 物理页 4，Eqs. (1)–(2)）[pdf:E05]（PDF 物理页 5，Fig. 4 与 Eqs. (3)–(11)）[pdf:E06]（PDF 物理页 6，Eqs. (12)–(20)）[pdf:E07]（PDF 物理页 7，Eqs. (21)–(26)）[pdf:E08]（PDF 物理页 8，Eqs. (27)–(34)）
2. **离线合成最优 TPS。** 在 \(\delta_p,\delta_s,\phi\in[0,\pi/2]\) 内，用 MATLAB `fmincon` 和 multistart 最小化总 DAB loss，同时以输出功率满足负载为 nonlinear constraint。扫描 \(V'_{\mathrm{out}}=80\)–150 V、\(P_{s,\mathrm{out}}=0\)–2 kW，以及 \(L_p,L'_s,R_{l,p},R_{l,s}\) 的离散范围，得到 852,390 行最优控制数据。[pdf:E09]（PDF 物理页 9，Fig. 9 与 optimization formulation）[pdf:E10]（PDF 物理页 10，dataset ranges）
3. **把最优解压缩为 DSP 可执行函数。** 作者定义
   \[
   L_t=L_p+\left(\frac{n_p}{n_s}\right)^2L'_s,\qquad
   R_t=R_{l,p}+\left(\frac{n_p}{n_s}\right)^2R_{l,s},
   \]
   并把 \(\delta_p^\*\) 与 \(\delta_s^\*\) 分别拟合成 \(V'_{\mathrm{out}},P_{s,\mathrm{out}},L_t,R_t\) 的四阶四变量 polynomial；\(\phi\) 不进入该 feedforward fit，而由输出电压 PI loop 给出。[pdf:E10]（PDF 物理页 10，Section III 与 Fig. 10）
4. **构造 PINN 训练数据。** 总数据量为 5000 条，其中 1000 条来自自动化硬件 test bench，4000 条由 NIFDM 生成；数据随机分成 70% training、20% validation、10% test。论文列出的原始采样量为 \(V_{\mathrm{in}},V_{\mathrm{out}},I_{\mathrm{in}},I_{\mathrm{out}},\delta_p,\delta_s,\phi\)，并派生 \(P_{\mathrm{loss}}=V_{\mathrm{in}}I_{\mathrm{in}}-V_{\mathrm{out}}I_{\mathrm{out}}\)。MLP 使用两层各 64 个 ReLU hidden neurons，输出 \(L_t,R_t\)。[pdf:E11]（PDF 物理页 11，Section IV-A）[pdf:E12]（PDF 物理页 12，Figs. 13–14 与 Table III）
5. **用 physics loss 训练。** custom loss 同时惩罚 \(L_t,R_t\) 的监督误差和 NIFDM 根据预测参数得到的输入/输出功率误差；\(\lambda=0.8\) 是作者通过 grid search 选出的权重。Keras/TensorFlow 2.6 在 i7-12900KF CPU 上训练约 30 s，230 epochs 后停止。[pdf:E13]（PDF 物理页 13，Eq. (36)、Fig. 15 与 Section IV-E）
6. **在线部署。** 预训练 `.h5` 模型运行在 Intel i7 PC；TMS320F28379D DSP 采样七个原始量，经 10 kHz low-pass filter、16-bit fixed-point encoding 后通过 10 kHz SPI 传给 PC。NN 约每 30 s 更新一次 \(L_t,R_t\)；DSP 用最新参数执行 polynomial duty map，若新参数尚未返回则继续使用旧值。每个 duty polynomial 的报告执行时间约 8 μs，PI 加 polynomial 的完整控制计算约 18 μs，因此采用 downsampled control cycle 服务于 100 kHz power stage。[pdf:E14]（PDF 物理页 14，Section V-A/V-B）[pdf:E15]（PDF 物理页 15，Fig. 18 与 Section V-C）

一个真实例子是 \(V_{\mathrm{in}}=160\) V、\(V'_{\mathrm{out}}=100\) V、\(P_{s,\mathrm{out}}=1.4\) kW。\(L_p\) 从 5.35 μH 切换到 2.15 μH 后，\(\phi\) 先由 0.58 调到 0.395 维持输出，但冻结的 \(\delta_p=0.285,\delta_s=0.1707\) 使两个 bridge 各有一个 leg 丢失 soft switching；30 s 更新后，NN 给出 \(L_t=7.97\) μH、\(R_t=63\) mΩ，DSP 将 duty 改为 \(\delta_p=0.241,\delta_s=0.067\)，四个 switching legs 恢复 soft switching，inductor RMS current 降低 8.5%，效率由 97.55% 升至 98.07%。[pdf:E16]（PDF 物理页 16，Section VI）[pdf:E17]（PDF 物理页 17，Fig. 21）

需要保留一个复现歧义：Section IV-A 的文字最终列出八个 NN 输入变量（四个电压/电流量、\(P_{\mathrm{loss}}\) 和三个控制量），Table III 却报告 input layer 为 7 neurons，Fig. 13 的 feature extraction 图又没有给出完全一致的计数。PDF 因此不足以唯一确定训练张量的实际列集合。[pdf:E12]（PDF 物理页 12，Fig. 13、Table III 与相邻正文）

## § 6 — 核心数学推导

第一步是把 TPS bridge voltage 放到 frequency domain。对第 \(k\) 次 harmonic，作者写成
\[
\vec V_{p,k}=\frac{4V_{\mathrm{in}}}{k\pi}\cos(k\delta_p)\angle 0^\circ,\qquad
\vec V_{s,k}=\frac{4V_o}{k\pi}\cos(k\delta_s)\angle(-k\phi).
\]
直观上，\(\delta_p,\delta_s\) 决定各次 harmonic 的幅值，\(\phi\) 决定两桥之间的相位，因此三者共同塑造电感电流和功率流。[pdf:E04]（PDF 物理页 4，Eqs. (1)–(2)）

第二步是把每个 harmonic 送入含寄生参数的复阻抗网络。以 primary branch 为例，\(Z_p(k)=R_p(k)+jk\omega_sL_p\)；作者经过 star–delta 等效得到 primary/secondary harmonic currents，再叠加到时域。由 harmonic amplitudes 可计算 RMS current，并由 voltage/current phasor 的实功分量得到 \(P_{p,\mathrm{ac}}\) 与 \(P_{s,\mathrm{ac}}\)。两者绝对值之差形成 conduction loss 的基础。[pdf:E05]（PDF 物理页 5，Eqs. (3)–(11)）

第三步专门处理 deadtime。作者用 MOSFET body capacitance 的充放电电流 \(i_p=-2C_{\mathrm{oss}}\dot x\) 与等效电感网络建立二阶方程，求出 deadtime 内 drain voltage \(x(t)\)，再按电流方向和 \(T_d\) 构造 piecewise bridge voltage。该 nonideal transition 的 Fourier components 被加回理想 bridge voltage，形成 Eqs. (19)–(20) 的 modified harmonic voltages；其工程含义是：ZVS 不再用一个理想电流符号条件代替，而是显式计算有限 \(C_{\mathrm{oss}}\) 在 deadtime 内能否完成放电。[pdf:E06]（PDF 物理页 6，Eqs. (12)–(20)）

第四步把损耗写成优化目标。conduction loss 为
\[
P_{\mathrm{cond}}(\delta_p,\delta_s,\phi)
=|P_{p,\mathrm{ac}}|-|P_{s,\mathrm{ac}}|,
\]
switching loss 由 channel voltage-current overlap 与不完全 ZVS 时的 \(C_{\mathrm{oss}}\) energy dissipation 相加；core loss用 fitted Steinmetz equation 表示。最终
\[
P_{\mathrm{DAB\,loss}}
=P_{\mathrm{cond}}+P_{\mathrm{SW}}+P_{\mathrm{core}},
\]
并由 secondary AC power 扣除 secondary switching/core loss得到输出功率约束。[pdf:E07]（PDF 物理页 7，Eqs. (21)–(26)）[pdf:E08]（PDF 物理页 8，Eqs. (27)–(34)）

第五步是从数值最优解得到实时 duty map：
\[
\delta_p^\*=\sum_{0\le i+j+k+l\le4}a_{i,j,k,l}
P^i(V'_{\mathrm{out}})^jL_t^kR_t^l,
\]
\(\delta_s^\*\) 使用同结构的 \(b_{i,j,k,l}\)。四阶不是理论上唯一正确的阶数，而是作者在 fit error、效率损失和 10 μs switching period 之间做的工程折中。[pdf:E10]（PDF 物理页 10，Section III）

最后，PINN 的核心不是把 differential equation 直接嵌入网络，而是把 NIFDM 的 power prediction 写入 supervised loss：
\[
\begin{aligned}
\mathcal L={}&\operatorname{MSE}(L_{t,\mathrm{pred}},L_{t,\mathrm{act}})
+\operatorname{MSE}(R_{t,\mathrm{pred}},R_{t,\mathrm{act}})\\
&+\lambda\left[
\operatorname{MSE}(P_{p,\mathrm{in,pred}},P_{p,\mathrm{in,act}})
+\operatorname{MSE}(P_{s,\mathrm{out,pred}},P_{s,\mathrm{out,act}})
\right].
\end{aligned}
\]
前两项要求参数标签匹配，后两项要求这些参数送入 NIFDM 后还能解释实际输入/输出功率；\(\lambda\) 控制数据一致性与物理一致性的权衡。[pdf:E13]（PDF 物理页 13，Eq. (36)）

## § 7 — 实验设计与结论

- **NIFDM 是否比 ideal model 更接近硬件？→** 作者在 160 V–100 V/200 W、primary partial ZVS 与 secondary full ZVS 的工况比较 ILM、NIFDM 与实验波形。**答案：**该点的 NIFDM 输出功率误差为 0.43%，比 ILM 的误差低 16.2 个百分点。[pdf:E06]（PDF 物理页 6，Fig. 7 与相邻正文）论文另在不同位置报告 NIFDM 对硬件的平均 modeling error 为 5.8%、用于 4000 条 synthetic samples 的模型为 4.6%，而 abstract 使用“power-flow absolute error within 5%”；这些是不同上下文的口径，不能合并成一个统一误差指标。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E11]（PDF 物理页 11，Section IV-A）
- **四阶 polynomial 是否足够准且能实时执行？→** 作者用 852,390 个离线最优点拟合 \(\delta_p^\*,\delta_s^\*\)，并在 TMS320F28379D 上计时。**答案：**两项 fit error variance 分别为 3.1% 和 2.7%；四阶 fit 的估算效率 compromise 为 0.04%，低于三阶的 0.16% 与二阶的 0.39%；单次报告执行时间 7.7 μs，小于 10 μs switching period。[pdf:E10]（PDF 物理页 10，Figs. 10–11 与相邻正文）
- **physics loss 在 limited data 下是否有用？→** 在相同 5000 条数据上比较 PINN 与 pure data-driven NN，并在随机留出的 test set 上评估。**答案：**PINN 对 \(L_t,R_t\) 的 MAE 为 2.7%、3.1%；纯 data-driven model 为 5.9%、11%，至少需要 20,000 条数据才达到相近精度。[pdf:E13]（PDF 物理页 13，Fig. 16 前文）[pdf:E14]（PDF 物理页 14，Fig. 16 与相邻正文）
- **参数自适应是否能抵消 30% 等效串联电感下降？→** 在 2 kW/100 kHz GaN DAB 上用 MOSFET bypass 一段 primary inductor，对完整 \(V'_{\mathrm{out}}\)–load 区域比较 nominal、adaptive-reduced-\(L_t\) 与 frozen-duty-reduced-\(L_t\) 三种情况。**答案：**adaptive TPS 相对 frozen TPS 的全图平均效率增益为 1.4%，最高为 3.2%，并缩小 partial-ZVS/hard-switching 区。[pdf:E16]（PDF 物理页 16，Fig. 20 的实验说明）[pdf:E17]（PDF 物理页 17，Fig. 20）
- **更新参数后，单点波形机制是否与效率变化一致？→** 在 160 V→100 V/1.4 kW 与 160 V→140 V/0.7 kW 两个工况，记录切换电感前、参数尚未更新、参数更新后三组 bridge voltage/current。**答案：**前一工况恢复四腿 soft switching、RMS current 降 8.5%、效率由 97.55% 升至 98.07%；后一工况重新获得 soft switching、RMS current 降 5%、效率由 96.1% 升至 96.87%。[pdf:E17]（PDF 物理页 17，Figs. 21–22）[pdf:E18]（PDF 物理页 18，Section VI）
- **双向功率与在线估计是否仍有效？→** 作者在 \(-2\) 至 2 kW、secondary dc-link 120/100/140 V 下测效率，并在不同电感、电阻设置下记录 SPI 输入和 NN 输出。**答案：**三组双向曲线报告 peak efficiency improvement 4%、average gain 1.8%；在线 \(L_t,R_t\) 估计的最大误差为 4.3%、9.2%，平均误差为 0.87%、1.4%，而 ideal analytical method 的 \(L_t\) average absolute error 为 10%。[pdf:E18]（PDF 物理页 18，Fig. 23 与 Section VI）[pdf:E19]（PDF 物理页 19，Fig. 24）

这些实验没有证明“所有 DAB、所有 drift mechanism、所有 switching frequency 下都有效”。可支持的范围是一台 2 kW、100 kHz、160 V primary、80–150 V secondary 的 GaN laboratory prototype，参数变化主要通过切换离散电感、串入电阻和改变并联器件数来模拟；NN 运行在外部 i7 PC，参数约 30 s 更新一次。论文还明确展示了即使使用所提 overall-loss-optimal TPS，也存在不能实现全腿 ZVS 的 operating bands。[pdf:E11]（PDF 物理页 11，Fig. 12）[pdf:E15]（PDF 物理页 15，Section V-C）[pdf:E16]（PDF 物理页 16，Table V）

## § 8 — Take-aways

**5 句话：**

1. 论文把 DAB 的参数估计、loss model、TPS optimization 和硬件控制闭合成一个可运行系统，而不是只报告离线 NN accuracy。
2. NIFDM 显式处理寄生 RLC、deadtime、有限 \(C_{\mathrm{oss}}\) 和多类损耗，使“最优 duty”更接近真实换流条件。[pdf:E04]（PDF 物理页 4，Section II-B）[pdf:E08]（PDF 物理页 8，Eqs. (27)–(34)）
3. PINN 用 1000 条 hardware data 加 4000 条 physics-model data，在随机 test split 上把 \(L_t,R_t\) MAE 做到 2.7%、3.1%。[pdf:E11]（PDF 物理页 11，Section IV-A）[pdf:E14]（PDF 物理页 14，Fig. 16）
4. 快慢路径分离是工程关键：DSP 不等待 NN，NN 约 30 s 才更新慢变参数，因此 100 kHz power stage 可以继续运行。[pdf:E15]（PDF 物理页 15，Section V-C）
5. 30% 电感变化下的平均 1.4% 效率收益很有工程意义，但它只在单台实验原型和人为参数变化上闭合，尚不能等同于真实热漂移、磁饱和和长期退化鲁棒性。[pdf:E16]（PDF 物理页 16，Section VI）[pdf:E20]（PDF 物理页 20，Conclusion）

**3 句话：**

1. 作者用高保真 frequency-domain model 同时生成最优 TPS map 和 PINN 的 physics loss。
2. PINN 估计 lumped \(L_t,R_t\)，DSP 再用 polynomial map 更新 duty，从而避免 NN 进入 switching-cycle 串行关键路径。
3. 实验显示这种结构能在离散电感变化后恢复部分 soft-switching 与效率，但 domain shift 和参数可辨识性仍是最关键的未决问题。

**1 句话：**

这篇论文最值得带走的是“用慢速物理约束估计去修正快速、可验证的传统控制器”，而不是“用神经网络直接控制 DAB”。

## § 9 — 最脆弱的假设

最脆弱的假设是：在运行域内，steady-state dc voltages/currents 与 \(\delta_p,\delta_s,\phi\) 足以把真实硬件压缩成一个对控制有用、近似唯一且慢变的 \((L_t,R_t)\)，并且 NIFDM 的结构误差小到不会把错误的“等效参数”送进 duty optimizer。

这项假设一旦不成立，论文的整条链会同时失效。作者已经承认 primary/secondary 的独立电感和各个寄生电阻无法从 power-flow model 分别辨识，只能估 lumped \(L_t,R_t\)；\(L_m\) 被视为远大于 series inductance，其他参数变化被排除。[pdf:E09]（PDF 物理页 9，Section III）[pdf:E11]（PDF 物理页 11，Section IV-A）训练数据中 80% 来自同一个 NIFDM，physics loss 又用同一个 NIFDM 评价预测参数，因此未建模的磁饱和、温度相关 deadtime/\(C_{\mathrm{oss}}\)、传感偏置或动态功率流可能同时污染 synthetic labels 和 physics constraint。随机拆分 training/validation/test 也没有检验“整种温度、器件或电感状态完全未见”的 out-of-distribution generalization。[pdf:E11]（PDF 物理页 11，Section IV-A）[pdf:E12]（PDF 物理页 12，data split）

论文给出的正面证据是：离散改变电感和电阻后，在线估计在实验域内仍保持较低误差，并且新参数带来的 duty change 与 ZVS/RMS/效率改善一致。[pdf:E17]（PDF 物理页 17，Figs. 21–22）[pdf:E18]（PDF 物理页 18，real-time validation）缺少的证据是：真实温升、磁通相关非线性、老化和快速 load cycling 下，同一 \((L_t,R_t)\) 是否仍然可辨识并足以决定最优 duty。30 s 更新周期进一步要求参数变化必须足够慢。[pdf:E15]（PDF 物理页 15，Section V-C）

## § 10 — 最小复现实验

一周内最值得复现的不是整张效率地图，而是“physics loss 是否真的改善未见参数状态的估计，并让预测参数产生接近 oracle 的 duty 改善”。PDF 没有公开 852,390 行 optimization data、polynomial coefficients、5000 条训练数据或可执行模型，而且 NN 输入列数存在歧义，因此无法只凭论文精确重放作者数值；最小实验应明确验证机制而非伪装成 exact replication。

具体做法如下：

1. 在已有 100 kHz DAB bench 或可信 switching simulation 上固定 \(V_{\mathrm{in}}=160\) V、\(V'_{\mathrm{out}}=100\) V，设置 nominal 与约 \(0.7L_{t,\mathrm{nom}}\) 两个电感状态，在 0.4–1.6 kW 采集 \(V_{\mathrm{in}},V_{\mathrm{out}},I_{\mathrm{in}},I_{\mathrm{out}},\delta_p,\delta_s,\phi\) 和独立功率计数据。
2. 不做随机 point split；把整个 reduced-\(L_t\) 状态留作 test。训练相同参数量、相同数据量的 pure MLP 与 PINN。针对 PDF 的输入歧义，预注册两种输入：七个 raw signals，以及额外加入 derived \(P_{\mathrm{loss}}\) 的八变量版本，分别报告结果而不事后挑最好者。[pdf:E12]（PDF 物理页 12，Fig. 13、Table III）
3. 用 LCR/impedance measurement 或已知元件组合给出 \(L_t,R_t\) ground truth；比较两种模型在完整未见电感状态上的 MAE 与 power residual。
4. 将预测 \(L_t,R_t\) 送入一个重新实现的 local TPS optimizer，比较 frozen-nominal、PINN-predicted 与 oracle-parameter 三组控制；记录四腿 ZVS、inductor RMS current 和功率计效率。

若 PINN 在整个未见状态上达到不劣于论文 real-time test 的误差量级（\(L_t\) 最大误差约 4.3%、\(R_t\) 最大误差约 9.2%），并且 predicted-parameter TPS 相对 frozen TPS 显著提高效率或恢复 ZVS、同时接近 oracle TPS，就支持核心 claim。[pdf:E18]（PDF 物理页 18，real-time error results）如果 PINN 只在随机 split 上优于 MLP、在整状态 holdout 上不再占优，或其 duty update 不能改善 ZVS/RMS/效率，则反驳“limited-data physics constraint 足以支持参数自适应调制”的核心机制。

## § 11 — 最强反例设计

最强反例不是再换一个 nominal 电感值，而是制造“一个 lumped、慢变 \(L_t,R_t\) 不再足以描述硬件”的工况。让 DAB 在接近 Fig. 12 incomplete-ZVS boundary 的轻/中载与 1.4 kW 之间每 5 s 循环，同时把磁件和 GaN 温度从冷态推到热态；选用具有明显 current-dependent incremental inductance 的磁件，使 \(L\) 随负载电流改变，而 \(R_{\mathrm{ds,on}}\)、winding resistance、\(C_{\mathrm{oss}}\) 和 deadtime effect 同时随温度改变。5 s 负载周期刻意快于论文约 30 s 的参数更新周期。[pdf:E11]（PDF 物理页 11，Fig. 12）[pdf:E15]（PDF 物理页 15，Section V-C）

实验同时运行原 PINN-adaptive、frozen nominal 和由高带宽电流/温度/阻抗测量提供的 oracle control，逐周期记录预测 \(L_t,R_t\)、ZVS residual voltage、RMS current、效率和 peak current。若相同 dc steady-state features 对应多个不同的 incremental inductance/optimal duty，PINN 只能输出一个折中“有效参数”；若该折中让 adaptive controller 在 ZVS constraint 或效率上系统性差于 frozen controller，就直接击穿参数可辨识性假设。

这个反例还排除了一个替代解释：本文的收益可能主要证明“已知的 30% 电感切换后，重新优化 duty 有用”，而不充分证明 PINN 能跟踪真实、耦合、连续的器件漂移。只有在上述非线性热动态下 estimator 仍优于 frozen 与纯 data-driven baseline，才能把收益可靠归因于 physics-informed parameter tracking。

## § 12 — Follow-up Research Idea

**候选方向：用 set-membership identification 与 safe extremum seeking 取代单点参数回归。** 这里不创造新的物理状态名：具体对象是“与最近一段 dc measurements 和 switching observations 一致的一组可能 DAB 模型”，其角色是估计记录；控制目的仍是效率最大化且不违反 ZVS、peak-current 和 thermal constraints；手段是在安全小扰动下测 local loss gradient，并对模型集合做 worst-case duty selection。set-membership identification、robust control 和 safe extremum seeking 均是相邻控制领域的成熟概念，本卡不声称这一组合对 DAB 具有 novelty。

驱动它的未满足需求是：论文必须先假定真实硬件能被唯一的 \(L_t,R_t\) 表示，而实验恰恰没有覆盖温度、饱和和老化导致的多参数耦合。新方向不再追求“猜中真实元件参数”，而问“当前证据允许哪些模型，以及哪组 duty 对这些模型都安全且低损耗”。NN 可以保留为模型集合的 prior 或快速 surrogate，但不能再作为唯一真相；DSP 仍执行快 control map，supervisory layer 只慢速缩小模型集合并更新允许的 duty region。

它可能产生本领域认可的价值，是因为评价对象从 test-set parameter MAE 改为硬件约束违反率、最坏效率 regret 和 domain-shift robustness，更贴近高功率 converter 的工程风险。可以借鉴 robust MPC 的 constraint tightening、set-membership system identification、dual control 的“控制同时激励辨识”思想，以及 safe Bayesian optimization 对未知 loss surface 的受约束探索。

第一个可证伪实验直接采用第 11 节的 thermal/load cycling：比较原 PINN point estimate、set-membership safe optimizer、frozen TPS 与 oracle，在相同扰动能量和计算预算下测 ZVS violation、peak current、效率 regret 与恢复时间。若模型集合迅速膨胀到无法提供比 frozen TPS 更好的 duty，或安全 probing 的额外损耗抵消了全部收益，这个方向就被第一轮实验否定。

它与本文的实质区别不是“多加一个 uncertainty head”，而是改变问题定义：本文先估一个参数点再查最优 duty；候选方向直接维护与观测一致的模型集合，并以约束下的决策质量而非参数点误差作为最终目标。由于本卡未对这一组合进行系统相关工作检索，以上仅是证据约束下的候选研究方向，不作 novelty 声明。
