# Clustering-Based Modeling and Interaction Analysis of Multiple Differently Parameterized Grid-Side Inverters in PMSG Wind Turbines

作者：Shuhan Liao, Yandong Chen, Meng Huang, Xikun Fu, Xiaoming Zha, Lei Wang, An Luo, Josep M. Guerrero

出处：IEEE Transactions on Energy Conversion, Vol. 36, No. 4, pp. 3031–3043

年份：2021

DOI：10.1109/TEC.2021.3071155

Zotero key：D299JA8D

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个很具体的稳定性分析问题：大型 PMSG 风电场里，多台 grid-side inverter 通过集电线路并接到弱电网，但实际机组的控制参数与线路长度并不完全相同。已有针对“完全相同的并联逆变器”的简化分析依赖系统对称性；参数一旦不同，系统不再整体对称，原来只用两个低阶传递函数区分 internal poles 与 external poles 的办法不再直接成立。作者提出按相同参数将逆变器分组，再利用每组内部仍然存在的对称性，把一个 \(n\) 阶多变量问题化成三个低阶 transfer function matrix 的稳定性判断。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，不只是因为全阶模型“算得慢”。在弱电网中，PCC 电压会随全部逆变器注入电流经电网阻抗产生的压降而变化，所以任意一台逆变器的电流扰动都可能经 PCC 反馈到其他机组；并联系统的稳定性不能由每台单机的稳定性简单推出。论文所用对象是 PMSG 全功率变流风机：发电机侧与电网侧被 full converter 解耦，机械部分和整流器在所研究的 inverter 时间尺度上被近似成 dc-link constant power source；作者还说明，同类 grid-connected inverter 控制结构也见于 PV 系统。[pdf:E02]（PDF 物理页 2，Section II-A 与 Figs. 1–2）

论文直接声称的价值有两层。第一层是计算：不用对全部 \(n\) 台逆变器的 full-order dynamic model 直接做特征值分析。第二层是物理解释：不同参数组互联会改变 common current 的外部稳定性，却不会改变各组内部 interactive current 的稳定性。[pdf:E01]（PDF 物理页 1，Abstract）这里的 common current 是流向电网的组平均/总和分量，interactive current 是只在并联逆变器之间循环、不会进入电网的差分分量；这一区分是理解全文的主线。

## § 2 — 前人工作与不足

根据论文自己的相关工作回顾，已有两条主要路线。

第一条是 linearized state-space modal analysis。它能用 eigenvalue 与 participation factor 找到不稳定模态，并识别哪些 inverter state 对某一 mode 贡献最大；但作者认为，这种结果更像“发现谁参与了振荡”，不能直接解释电流怎样在组内循环、怎样经电网形成组间耦合，因而没有把 interaction mechanism 提炼成可供参数设计使用的结构。[pdf:E01]（PDF 物理页 1，Introduction 对文献 [9]–[11] 的评述）

第二条是 impedance/admittance-based multivariable modeling。直接模型把 \(n\) 台并联逆变器的参考电流到输出电流关系写成 \(n\) 阶 transfer matrix，可以用 generalized Nyquist criterion 或 eigenvalue analysis 判断稳定性；问题是，\(n\) 较大时 characteristic loci 和 eigenvalue 计算负担增加。对完全相同的逆变器，文献 [6]、[7]、[12]、[13] 已经利用对称性把问题拆成 internal/external poles 或 interactive/common currents 两类：前者对应组内循环电流，后者对应注入电网的电流。[pdf:E02]（PDF 物理页 2，Introduction）

真正的缺口不是“以前没人考虑参数不同”这么宽泛，而是先前简化的成立理由——全系统 permutation symmetry——在参数与集电线路不同后消失。全阶多变量模型仍能算，但不再给出低阶、带物理含义的分解；相同逆变器的两传递函数法又不能直接套用。论文的目标因此是找出部分对称性仍存在于哪里，并利用它恢复可解释的低阶结构。需要注意，本文没有联网补充相关工作，也没有证明“按组聚类”在更广文献中具有绝对 novelty；本节只复述 PDF 中的文献定位。

## § 3 — 重建作者的思考路径

下面是基于论文证据的合理重建，不是作者逐字陈述。

1. 从弱电网的物理耦合出发：网络是线性的，任意一台 inverter output voltage 的变化都会通过集电线路与 \(Z_g\) 改变其他 inverter current，因此先把 inverter dynamics 与 network admittance 分开建模，再组合成系统模型。[pdf:E03]（PDF 物理页 3，Section II-B 与 Figs. 3–6）
2. 回到完全相同的并联系统：如果所有支路与控制器相同，电流空间可以分成“所有机组同向变化”的 common 子空间和“组内和为零”的差分子空间。前者看见 grid impedance，后者只看见自身支路阻抗。这解释了为什么既有工作能用 external/internal 两类 poles。[pdf:E04]（PDF 物理页 4，Eqs. (7)–(15)）
3. 观察真实风场虽不具备全局对称性，但通常仍有成批相同机型、相同 controller settings 或相同线路参数。若把相同对象放进同一 group，每组内部的置换对称性仍在；于是可以只在“组平均”之间保留耦合，而把每组内部的差分模态单独拿出来。[pdf:E05]（PDF 物理页 5，Section III-B，Eqs. (17)–(23)）
4. 最后把数学分解转成可检验的物理预测：改变 group B 不应移动 group A 的 internal poles，但会改变共同决定两组 common currents 的 external poles。于是 root locus、PSCAD 时域仿真和 RT-LAB-based 实验都围绕“同向扰动只激发 common mode；单机不对称扰动会激发本组 interactive mode”来设计。

这条路径的关键不是一般意义的 clustering algorithm。作者没有从数据中自动聚类，也没有给出距离函数；“clustering”在正文的严格含义是按相同参数和相同集电线路长度进行确定性分组。对“相近但不完全相同”的支路，论文只提出可以分组的设想，尚未验证误差容限。

## § 4 — 核心 Intuition

把每一组相同逆变器的电流想成“组平均 + 围绕组平均的差分”。组间只能通过 PCC 和电网看到彼此的组平均，所以不同组互联会改变 common-current modes；组内差分电流的和为零，不流入电网，因而其 interactive-current modes 只由本组线路与控制器决定。[pdf:E06]（PDF 物理页 6，Eq. (26)、Table I 与 Section III-C）

因此，系统不需要保持全局对称；只要每个 group 内部严格对称，就能把一个大系统的稳定性拆成“两组各自的 internal stability + 两组耦合的 external stability”三块。

## § 5 — 具体方法与完整 Pipeline

以论文的六台 1.5 MW inverter、两组各三台的例子说明完整 pipeline。

1. **建立网络 admittance matrix。** 把每台 inverter 在网络侧视为电压源，写成
   \[
   \mathbf i=\mathbf G(s)\mathbf v_o .
   \]
   \(\mathbf G\) 的对角元素 \(G_{ii}\) 表示本机电压对本机电流的作用，非对角元素 \(G_{ij}\) 表示第 \(j\) 台电压经 PCC 与 grid impedance 对第 \(i\) 台电流的作用。作者用 superposition 与 Thevenin equivalent circuit 推导这些元素；当 \(Z_g\neq 0\) 时，\(G_{ij}\neq 0\)，组间交互由此出现。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(4) 与 Figs. 3–6）
2. **建立单台 inverter 的 small-signal model。** 对 VOC-controlled grid-side inverter，把 dc-voltage loop、current loop 和 PLL 线性化，得到统一 \(xy\) synchronous frame 下从 current reference 到 output voltage 的 \(2\times 2\) transfer matrix \(H(s)\)。group A 与 group B 参数不同时分别记为 \(H_A(s)\) 与 \(H_B(s)\)。附录给出了 \(H(s)\) 的推导；正文没有报告离散化、switching-event handling 或数值求解器实现。[pdf:E12]（PDF 物理页 12，Appendix Eqs. (A.1)–(A.9)）
3. **用 identical-system 分解建立基准。** 对 \(n\) 台完全相同 inverter，第 \(i\) 台输出电流可写成组内差分项与平均项之和：
   \[
   i_i=\frac1n\sum_{j=1}^{n}(i_i-i_j)+\frac1n\sum_{j=1}^{n}i_j .
   \]
   第一项是 interactive current，第二项是 common current。变换到统一 \(xy\) frame 并接入 \(H(s)\) 后，这两类电流分别由 \(G_{\mathrm{int}}^{xy}H\) 与 \(G_{\mathrm{com}}^{xy}H\) 决定。[pdf:E04]（PDF 物理页 4，Eqs. (7)、(10)–(15)）
4. **按严格相同参数分组。** 六台机中 #1–#3 作为 group A，#4–#6 作为 group B。网络矩阵形成
   \[
   \mathbf G(s)=
   \begin{bmatrix}
   \mathbf G_{AA}(s)&\mathbf G_{AB}(s)\\
   \mathbf G_{BA}(s)&\mathbf G_{BB}(s)
   \end{bmatrix}.
   \]
   整体矩阵不再对称，但每个 block 内的重复结构保留了组内对称性。对 group A，输出电流被写成由 \(G_{\mathrm{intA}}^{xy}H_A\) 控制的组内差分项，以及同时含 \(H_A,H_B\) 的组平均项；group B 同理。[pdf:E05]（PDF 物理页 5，Eqs. (17)–(23)）
5. **只分析三个低阶矩阵。** group A interactive stability 由 \(\det(G_{\mathrm{intA}}^{xy}H_A)=0\) 的 roots 判断，group B 由 \(\det(G_{\mathrm{intB}}^{xy}H_B)=0\) 判断；两组 common currents 合并成 \(R_c\)，external stability 由 \(\det(R_c)=0\) 判断。[pdf:E06]（PDF 物理页 6，Eqs. (24)–(26) 与 Table I）输出不是一条汇总指标，而是三类 poles：A 组 internal、B 组 internal，以及两组耦合的 external poles。
6. **用有选择性的扰动验证 mode 含义。** 对所有 inverter 同时施加 grid-voltage perturbation，理想对称下只激发 common current；只扰动 group A 或 B 中的一台，则会激发该组 interactive current。比较 root-locus prediction、PSCAD waveform 与 RT-LAB-based waveform，检查稳定/不稳定符号以及 oscillation frequency 是否相符。

从 EMT + FPGA 角度，本文报告的是 continuous-time small-signal transfer matrices、root locus、PSCAD off-line simulation 和 RT-LAB-based experiments。开关模型层级、事件定位、integration method、仿真 time step、multi-rate partition、fixed-point/float numerical representation、FPGA resource mapping、pipeline latency、并行架构、RT-LAB chassis/CPU/FPGA 型号均未报告；因此不能把这篇论文当作 FPGA real-time implementation 论文，也不能从波形图推出其硬实时步长。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 网络耦合

网络模型从 \(\mathbf i=\mathbf G(s)\mathbf v_o\) 开始。对第 \(i\) 支路，作者通过关掉其他 voltage sources 求 \(G_{ii}\)，通过只保留第 \(j\) 个 source 并作 Thevenin equivalent 求 \(G_{ij}\)。核心结果是：弱电网 \(Z_g\neq 0\) 时，非对角元素不为零，因此任何 inverter 的 output voltage 都会进入其他 inverter 的 current equation。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(4)）这一步把“PCC 耦合”变成矩阵中的 off-diagonal terms。

### 6.2 identical group 的 common/interactive 正交分解

对完全相同的支路，矩阵所有 diagonal elements 相同、所有 off-diagonal elements 相同。作者定义
\[
G_{\mathrm{int}}=G_{11}-G_{12},\qquad
G_{\mathrm{com}}=G_{11}+(n-1)G_{12},
\]
并进一步得到
\[
G_{\mathrm{int}}=\frac{1}{Z_{li}},\qquad
G_{\mathrm{com}}=\frac{1}{Z_{li}+nZ_g}.
\]
[pdf:E05]（PDF 物理页 5，Eq. (16)；前置定义见物理页 4 的 Eq. (11)）直观上，组内差分电流在 PCC 相加为零，所以看不见 \(Z_g\)；组平均电流流入电网，所以分母含 \(nZ_g\)。这正是 internal stability 与 external stability 的物理来源。

### 6.3 两组系统的低阶化

设 group A 有 \(m\) 台，group B 有 \(n-m\) 台。以 group A 为例：
\[
\begin{aligned}
\mathbf i_{xyi}={}&\frac1m G_{\mathrm{intA}}^{xy}H_A
\sum_{j=1}^{m}(\mathbf i^*_{xyi}-\mathbf i^*_{xyj})\\
&+\frac1m\left(
G_{\mathrm{comA1}}^{xy}H_A\sum_{j=1}^{m}\mathbf i^*_{xyj}
+G_{\mathrm{comA2}}^{xy}H_B\sum_{j=m+1}^{n}\mathbf i^*_{xyj}
\right).
\end{aligned}
\]
[pdf:E05]（PDF 物理页 5，Eq. (23)）第一行只含 group A 的 \(H_A\) 和本组差分，因此 group B 参数不会进入 A 组 interactive dynamics。第二行同时含两组 reference-current sums，是 group A common current 接受组间耦合的通道。group B 的式子结构相同。[pdf:E06]（PDF 物理页 6，Eqs. (24)–(25)）

两组 common-current vectors 最终写成
\[
\begin{bmatrix}
\mathbf i_{\mathrm{comA}}\\
\mathbf i_{\mathrm{comB}}
\end{bmatrix}
=R_c
\begin{bmatrix}
\sum_{j=1}^{m}\mathbf i^*_{xyj}\\
\sum_{j=m+1}^{n}\mathbf i^*_{xyj}
\end{bmatrix}.
\]
于是系统稳定性由三个 determinant 的 roots 分别判断：
\[
\det(G_{\mathrm{intA}}^{xy}H_A)=0,\quad
\det(G_{\mathrm{intB}}^{xy}H_B)=0,\quad
\det(R_c)=0.
\]
[pdf:E06]（PDF 物理页 6，Eq. (26) 与 Table I）这是论文最核心的降阶结论。

### 6.4 单机闭环矩阵

附录把 dc-voltage loop、current loop、坐标变换和 PLL 合并，给出
\[
H(s)=\frac{\Delta\mathbf v_{oxy}}{\Delta\mathbf i^*_{xy}}
=
\frac{K+T_vG_{\mathrm{pll}}}
{K(I-G_{ir}G_i)^{-1}G_{iv}+T_iG_{\mathrm{pll}}}.
\]
[pdf:E12]（PDF 物理页 12，Eq. (A.9)）这里的“分式”是论文对矩阵关系的紧凑写法；它依赖 unity power factor、\(\Delta i_q^*=0\)、工作点线性化以及 dq/xy frame 变换。正文明确省略了 \(G_{\mathrm{com}}^{xy}\) 的详细表达式，[pdf:E04]（PDF 物理页 4，Eq. (13) 后正文）所以复现者需要从网络模型自行构造，而不能只靠卡片中的式子恢复全部实现。

## § 7 — 实验设计与结论

### 问题一：控制参数不同会怎样影响 common 与 interactive stability？

**实验。** 作者构造 systems I–III，每台 inverter 容量 1.5 MW，六台并联，grid SCR 为 3，690 V/10.5 kV transformer equivalent impedance 为 0.045 p.u.，且本组实验不加 collecting line。system I 的 #1–#3 为 group A，#4–#6 为 group B；\(k_{piB}\) 从 0.015 扫到 0.085、step 0.005，\(k_{iiB}\) 从 16 扫到 44、step 2，并与六台 identical inverter 的 systems II、III 比较 root loci。[pdf:E07]（PDF 物理页 7，Table II 与 Fig. 8）

**答案。** 当两组参数不同时，system I 新出现一对比 identical-system external poles 更靠右的 poles，说明组间互联恶化 50–200 Hz 范围的 common-current damping。与此同时，group A 的 internal pole 不随 group B 参数变化，group B 的 internal pole 与 system III 的对应 pole 重合，支持“另一组不改变本组 interactive dynamics”。作者还观察到 medium-frequency damping 对 \(k_{pi}\) 更敏感，而 natural frequency 对 \(k_{ii}\) 更敏感。[pdf:E07]（PDF 物理页 7，Figs. 8–9 相邻正文）

### 问题二：collecting-line difference 是否产生相同机制？

**实验。** systems IV–VI 的 inverter controls 相同。system IV 中 #1–#3 的 line length 固定 10 km，#4–#6 的 \(l_B\) 从 0 扫到 28 km、step 2 km；system V 六条线均为 10 km，system VI 六条线均为 \(l_B\)。论文给出的 line inductance 为 0.0056 mH/km，resistance 为 0.002 \(\Omega\)/km。[pdf:E08]（PDF 物理页 8，Tables III–IV 与 Section IV-B）

**答案。** 当 \(l_B\neq 10\) km，system IV 出现额外 external pole pair，且比 system V 对应 poles 更靠右；internal poles 则仍与各 identical-system 对应 pole 基本重合。作者也承认 line change 会通过 steady-state operating point 让另一组 internal pole 轻微移动，因此“完全不影响”在其仿真里并非数值上绝对不动，而是 dynamic ownership 仍归属本组。[pdf:E08]（PDF 物理页 8，Figs. 10–11 与相邻正文）

### 问题三：small-signal poles 是否对应时域波形？

**实验。** 在 PSCAD 中，dc-link 先由 constant dc-voltage source 充电，到 1.0 s 改由 controlled current source 注入 constant power；2.0 s 施加扰动。对 common mode，所有 inverter 同时经历 5% grid-voltage decrease；对 internal mode，只给一台 inverter 施加 5% input-power decrease，部分实验的 perturbation duration 为 0.05 s。[pdf:E08]（PDF 物理页 8，Section V-A）[pdf:E09]（PDF 物理页 9，Section V-A.1）

**答案。** 控制参数实验中，system I 的 external pole \(-1.084\pm j361.3\) rad/s 对应 \(f_d=57.50\) Hz、damping ratio 0.30%，PSCAD 观测为 57.14 Hz；group A 的不稳定 internal pole \(8.743\pm j354.0\) rad/s 对应 \(f_d=56.35\) Hz、damping ratio \(-2.47\%\)，时域振荡为 60.60 Hz。只扰动 group A 的一台机时，全部机组最终发散到 saturation；只扰动 group B 的一台机时，active power 保持稳定，分别对应 A 组 RHP internal poles 与 B 组 LHP internal poles。[pdf:E09]（PDF 物理页 9，Table V 与 Figs. 12–15）[pdf:E10]（PDF 物理页 10，Table VI 与 Figs. 16–17）

线路实验中，\(l_B=20\) km 时 system IV 的一对 external poles 为 \(11.01\pm j368.30\) rad/s，\(f_d=58.62\) Hz、damping ratio \(-2.99\%\)，时域振荡为 59.42 Hz；而 identical-line systems V、VI 保持稳定。作者用 all-inverter participation factor 说明该 RHP mode 属于 common dynamics。[pdf:E10]（PDF 物理页 10，Figs. 18–20 与 Table VII）

### 问题四：RT-LAB-based 结果是否支持 mode 选择性？

**实验。** 对 system I 分别扰动 #1 inverter dc-link input power、#4 inverter dc-link input power，以及全局 grid voltage。#1 扰动激发 group A interactive mode，#4 扰动激发 group B interactive mode，全局 voltage perturbation 激发 common mode。

**答案。** #1 input power 在 2.0 s 下降 5% 时，三相电流失真且 \(U_{dc}\) 呈约 60 Hz oscillation；#4 下降 5% 时三相电流恢复稳态；grid voltage 下降 5% 时 common-current response 稳定。[pdf:E11]（PDF 物理页 11，Figs. 21–23 与 Section V-B）这些结果支持论文提出的 mode ownership，但不能外推为真实风机硬件验证：论文未报告 RT-LAB 的 hardware configuration、real-time step、solver、I/O interface、controller hardware 或 power stage。

## § 8 — Take-aways

**5 句话。** 1）弱电网中的多 inverter interaction 可以分成流向电网的 common current 与组内循环的 interactive current。2）全系统参数不同会破坏全局对称性，但每组 identical inverter 内部的对称性仍可用于降阶。3）两组系统的稳定性可由 group A internal、group B internal 和 coupled common 三个低阶 transfer matrices 分别判断。[pdf:E06]（PDF 物理页 6，Table I）4）论文的 root locus、PSCAD 与 RT-LAB-based waveforms 都支持“组间互联主要恶化 common-current stability，而另一组不改变本组 interactive-current mode ownership”。5）结论只在 exact grouping、small-signal model 和所测 50–200 Hz cases 中得到验证，不能直接视作任意参数离散度下的鲁棒定理。

**3 句话。** 把每组电流拆成平均与差分，就能把大规模多 inverter 稳定性问题压缩成三个有物理意义的低阶矩阵。不同组通过 PCC 耦合平均分量，组内差分分量原则上只由本组决定。论文证明了这个精确对称情形，但没有给出“近似相同”该如何聚类及误差多大仍可信。

**1 句话。** 这篇论文最有价值的贡献，是用“组内对称、组间只耦合平均量”解释并简化 differently parameterized inverter systems 的稳定性。

## § 9 — 最脆弱的假设

最脆弱的假设是：每个 cluster 内的 inverter controls 与 collecting-line impedances 足够相同，使组内 permutation symmetry 可以被当作精确成立。这个假设一旦失效，组内差分电流的和虽然仍可定义为零，但系统矩阵不再在 common/interactive 子空间间严格 block-diagonal；另一组和 grid impedance 可能通过残余耦合进入原本“只属于本组”的 internal modes，三个低阶矩阵也可能漏掉决定稳定性的 mixed mode。

论文给出的证据是 exact case：两组内分别使用完全相同的 parameters/lines，root loci 与 selective perturbations 符合分解。作者在 Section III-B 提出“line lengths close”时仍可聚类，并称 small tolerance 对 dynamics 影响小；但同一段又明确说 tolerance case 留待 future work，没有给出相似度 metric、error bound、cluster-selection rule 或 stability-margin requirement。[pdf:E06]（PDF 物理页 6，Table I 后正文）

因此，本文最强的结论应读成精确对称模型下的结构性结果，而不是已经验证的 approximate clustering 方法。工程上最危险的情形是 external/internal poles 已接近 imaginary axis 时，即使很小的组内 mismatch 也可能改变 rightmost eigenvalue；论文现有实验没有覆盖这种鲁棒性问题。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 PMSG wind farm，而是“另一组参数是否只移动 common poles、不移动本组 internal poles”这一核心 claim。

1. 在 MATLAB/Simulink、Python control 或 PSCAD 中实现六台 averaged VOC inverter 的 linearized model，直接采用 Table II 的 \(L_f=0.2\) mH、\(C=11750\ \mu\mathrm F\)、\(k_{pv}=3\)、\(k_{iv}=20\)、\(k_{pt}=50\)、\(k_{it}=900\)，设置 SCR=3；group A 固定 \(k_{pi}=0.026,k_{ii}=20\)，group B 扫描论文范围。[pdf:E07]（PDF 物理页 7，Table II）
2. 同时构造 full six-inverter state-space model 与论文三个低阶 matrices，分别计算 rightmost eigenvalues，并按 participation/vector symmetry 把 full-model modes 标成 A-internal、B-internal、common。
3. 做两个时域扰动：全局 \(v_g\) 下降 5%，以及只让 #1 inverter 的 \(P_{in}\) 短时下降 5%。测量每组平均电流、每台机相对组平均的差分电流及 oscillation frequency。
4. 预先定义支持标准：exact grouping 时，三个低阶模型与 full model 对每个 mode 的 stable/unstable sign 必须一致，dominant frequency relative error 不超过 5%；全局扰动的组内差分应保持数值噪声量级，而 #1 扰动应主要激发 A-internal component。
5. 反驳标准：任一低阶矩阵判断为 LHP、但 full model 出现相应 RHP mode；或 group B parameter sweep 显著移动 A-internal pole，且不是 operating-point recomputation error。

如果还有时间，再加入组内 \(\pm1\%,\pm3\%,\pm5\%\) 的 \(k_{pi}\) 与 line-impedance mismatch。这一扩展不再是复现论文已证结论，而是在测试第 9 节指出的未验证鲁棒性。

## § 11 — 最强反例设计

最有力的反例不是简单把 SCR 调得更低，而是专门破坏“组内对称使 common/interactive 严格解耦”这一机制，同时让每个低阶子模型单独看都似乎稳定。

具体做法是先把 exact two-group system 调到三个低阶模型的 rightmost poles 都略在 LHP、且 A-internal 与 common mode frequencies 接近。随后保持每个 group 的 mean parameters 不变，对 A 组的三条线路和三套 current-controller gains 施加和为零的异质扰动，例如一台 \(+5\%\)、一台 \(-5\%\)、一台不变；再用 adversarial search 选择 mismatch direction，使 full-order model 的 rightmost eigenvalue 最大。若 full model 出现由 common 与 A-internal states 共同参与的 RHP mixed mode，而按 group means 构造的 \(G_{\mathrm{intA}}^{xy}H_A\)、\(G_{\mathrm{intB}}^{xy}H_B\)、\(R_c\) 仍全部预测 LHP，就直接推翻“近似相同也可安全聚类”的工程延伸。

这个反例比“参数范围更大时效果不好”更强，因为它提供了替代解释：论文看到的 independence 可能来自精确 permutation symmetry，而不是一种对实际 parameter spread 天然鲁棒的 interaction law。论文的 line-length sweep 只改变 group B 的统一长度，仍保持组内 exact identity；没有测试这种 symmetry-breaking mismatch。[pdf:E08]（PDF 物理页 8，Tables III–IV）

## § 12 — Follow-up Research Idea

**候选想法，不声称 novelty：带残余耦合证书的 uncertainty-aware modal coarse-graining。**

（a）**未满足需求。** 实际风场很少存在参数完全一致的 cluster，工程师真正需要的不是“能不能把相同机组放一组”，而是“给定 parameter dispersion 与 stability margin，这样分组会不会漏掉不稳定 mixed mode”。本文已经指出 tolerance case 未验证，且详细 parameter-design procedure 仍需后续研究。[pdf:E11]（PDF 物理页 11，Conclusion）

（b）**研究价值。** 在电力电子与电能变换领域，高影响结果通常需要同时给出可解释的 stability mechanism、可计算的 design rule 和严格的仿真/实验验证。若能把 exact symmetry decomposition 扩展成“低阶 nominal model + 可计算 residual-coupling bound”，就能让降阶结果从解释性工具变成带失稳漏检上界的工程判据，而不只是多加一个 controller module。

（c）**可借鉴方法。** 可借鉴 matrix perturbation、pseudospectrum、robust control 的 structured singular value，以及 graph equitable partition 的近似商空间。先用投影把状态分成 cluster-average 与 intra-cluster residual，再显式保留打破对称性的 off-block coupling；用其 norm 与 nominal spectral separation 给出“低阶 pole classification 仍有效”的 sufficient condition。

（d）**第一个证伪实验。** 在论文 six-inverter case 上，随机并对抗性地注入 0–10% controller/line mismatch，比较 full-order rightmost eigenvalue 与带 bound 的 coarse model。若存在 full model 失稳而证书仍宣称稳定，或 bound 在所有实用 mismatch 下都松到无法给出任何结论，这个方向的核心价值即被证伪。

（e）**与本文的实质区别。** 本文问的是“exact identical groups 下怎样利用保留下来的 symmetry”；该候选方向把问题改成“symmetry 被破坏后，降阶稳定性判断还能被定量信任到什么程度”。它输出的不是又一个聚类标签，而是 cluster partition、residual coupling、margin certificate 与必要时的自动拆组决策。由于本次严格 PDF-only、没有检索本文之后的相关工作，这一方向只能作为证据约束的候选研究问题，不能宣称尚无人完成。
