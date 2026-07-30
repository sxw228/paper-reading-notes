# An Equivalent Switching Model for FPGA-Based Real-Time Simulation of SiC MOSFET Transient Behaviors in Power Electronic Converters

- 作者：Shinan Wang, Xizheng Guo, Kai Li, Yongjie Yin, Zonghui Sun, Xiaojie You
- 出处：*IEEE Transactions on Power Electronics*, Vol. 40, No. 9
- 年份：2025
- DOI：10.1109/TPEL.2025.3573128
- Zotero key：69CY3T2T

以上书目信息与论文题名见 PDF 物理页 1。[pdf:E01]

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“SiC MOSFET 能否被精细建模”，而是一个受实时约束的问题：能否把 SiC MOSFET 的纳秒级开关暂态放进整台电力电子变换器的 FPGA real-time simulation（RTS）里，同时把步长压到 10 ns、避免非线性迭代，并把乘法器和片上存储消耗控制在可部署范围内。作者指出，高频 SiC 器件的暂态持续时间约为 100 ns 或更短，要有效分辨它，仿真步长应不大于 10 ns；理想开关、associated discrete circuit 和传统 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 模型不描述非线性开关过程，因而也不能可靠给出开关损耗。[pdf:E01]

这个问题重要，是因为 HIL 的价值在于让真实控制器与虚拟功率级实时交互；如果功率级只保留稳态开关逻辑，控制器虽然“跑起来了”，但看不到器件的电压/电流过冲、gate crosstalk、软开关换流和损耗。相反，半导体 physics-based 模型虽能描述载流子与电磁过程，却涉及复杂的非线性微分方程和工艺相关参数，难以在 FPGA 上以纳秒步长求解。[pdf:E01] 因此，论文真正追求的是“足够物理、又足够便宜”的中间层模型：保留决定系统级暂态的 gate loop、junction capacitance、channel region 和 stray inductance，但把它们编译成固定时延、可并行的代数计算。

## § 2 — 前人工作与不足

论文把已有路线分成几类，并给出了较具体的失败原因。[pdf:E02]

- 理想开关、associated discrete circuit 和 \(R_{\mathrm{on}}/R_{\mathrm{off}}\) 模型计算便宜，但没有非线性 switching transient，因而不能同时回答暂态波形与 switching loss。
- 文献 [14] 用指数/对数函数分段拟合器件暂态，并把 system-level 与 device-level 模型分别流水化；问题不是拟合能力不足，而是长 pipeline delay 限制了最小实时步长。
- 文献 [15] 用 piecewise simplified state equations 做到了整机 50 ns RTS，但用 forward Euler（FE）解耦器件层和系统层；对高刚性、高频电路，FE 容易产生数值振荡，而且 50 ns 本身不足以分辨约 100 ns 的 SiC 暂态。
- 文献 [16] 用 feed-forward neural network 拟合 turn-ON/OFF 波形，在 FPGA 上达到 5 ns；代价是需要大量训练数据，而且换器件型号或厂家就要重新提取数据，部署与泛化成本高。
- 文献 [17] 用 LUT 表示变化的结电容和寄生参数，也达到 5 ns device-level RTS；作者认为其计算资源消耗偏高、扩展性仍需讨论，而且同样采用 FE，稳定性受限。
- 文献 [18] 把 SiC MOSFET 处理成二值电阻并联寄生电容，资源很省、也容易并入系统网络方程，但对真实 switching transient 的精度不足。

因此，本文并非第一次做 device-level FPGA RTS；它针对的是既有方法之间尚未闭合的三角矛盾：短步长、暂态精度和可扩展资源消耗不能同时满足。需要注意的是，论文的 prior-work 对比主要来自作者自己的分类和 Table III 的汇总；Table III 以 “Low/Middle/High” 粗粒度标注 accuracy，没有统一误差指标或同平台复跑，因此它只能说明设计取向，不能作为严格的 head-to-head 性能排名。[pdf:E09]

## § 3 — 重建作者的思考路径

从已有知识出发，可以重建出如下路径。

第一步，先问“暂态中哪些物理量不能删”。理想开关失败，说明至少要保留 gate-source 动态、Miller coupling、非线性 \(C_{\mathrm{rss}}\) 与 \(C_{\mathrm{oss}}\)、channel conduction region，以及功率回路 stray inductance；否则 \(v_{ds}\)、\(i_d\)、\(v_{gs}\) 的换流形状和损耗没有来源。[pdf:E02][pdf:E03]

第二步，再问“哪些求解结构必须删”。完整 device state equations 会与外部网络一起形成高阶、刚性的方程组；若每个 10 ns 步都迭代求解，FPGA 的时序和 DSP48 预算很快失控。Backward Euler（BE）的电容 companion model 提供了突破口：每个电容在当前步可以写成 conductance 加 history current source，既保留记忆，又把微分关系变成代数关系。[pdf:E03]

第三步，把单管问题提升为 half-bridge 基本单元。上下管的内部状态原本耦合在同一桥臂 KCL/KVL 中；如果直接以整个变换器为状态空间，阶数随桥臂数增长。作者反过来先在桥臂内部消元，得到以 \(v_h,i_h\) 和历史量为输入、以两管 \(v_{ds}\) 为输出的低阶矩阵方程，再通过 latency insertion 与外部 passive network 解耦。[pdf:E04][pdf:E05]

第四步，把非线性从“在线求函数”改成“离线算系数、在线查表”。结电容曲线按 datasheet 的 \(v_{ds}\) 采样，矩阵系数预先存进 LUT；channel transfer characteristic 在 active region 用一条切线近似。于是每步只需根据上一时刻 \(v_{ds},v_{gs}\) 选择 conductance region、索引系数，并执行固定数量的乘加。[pdf:E07][pdf:E08]

最后，验证必须分两层：先用 LTSpice 参考模型检查单桥臂/变换器的波形与损耗，再把 DPT 和 LLC 做成真实 FPGA RTS，与硬件功率实验比较。这样才能分别回答“代数简化有没有毁掉器件暂态”和“定点化、布线与实时步长有没有毁掉最终整机结果”。[pdf:E05][pdf:E08][pdf:E09]

## § 4 — 核心 Intuition

核心 intuition 是：不要在 FPGA 上实时“求解一个 SiC MOSFET”，而要提前把它编译成随工作区切换的 Norton 等效支路。BE 把结电容的记忆压进 history current source，half-bridge 消元把高阶联立状态方程压成低阶代数矩阵，LUT 再把非线性参数变成索引。[pdf:E03][pdf:E04] 这样，器件暂态与外部网络就能在同一时间步并行推进，而不需要 nonlinear iteration；代价是连续的 channel/diode 物理被近似为少数 conductance region。[pdf:E05][pdf:E07]

## § 5 — 具体方法与完整 Pipeline

以论文的 full-bridge LLC 为例，一个 10 ns 时间步内的输入、处理和输出如下。

1. **离线参数化。** 从器件 datasheet 读取 junction capacitance 与 transfer characteristic。作者把 \(C_{\mathrm{iss}}\) 近似为常数，对随 \(v_{ds}\) 强烈变化的 \(C_{\mathrm{rss}}\) 和 \(C_{\mathrm{oss}}\) 均匀采样，并用相应电容值预计算系统矩阵系数后存入 FPGA LUT。active region 的二次 transfer curve 不直接在线计算，而是在 \(i_{ch}=i_L/2\) 处用切线代替；更高精度可增加分段，计算资源不变，但存储资源随分段数线性增加。[pdf:E07]

2. **接收当前外部量和上一时刻状态。** 每个 half-bridge 模块接收 dc-side voltage \(v_h(k)\)、load current \(i_h(k)\)、两只管的 gate drive \(v_{dr}(k)\)，并读取上一时刻的 \(v_{ds}(k-1)\)、\(v_{gs}(k-1)\) 与 \(i_d(k-1)\)。系统网络模块则接收桥臂输出和自己的历史状态。[pdf:E04][pdf:E08]

3. **选择导电区和 LUT 系数。** 每只 MOSFET 根据上一时刻 \(v_{ds},v_{gs}\) 选择 cutoff、active/linear 或反并联二极管/ON region 对应的 \(G_{\mathrm{sw}}\)。两只管各有三类 conductance，桥臂共有九种组合，包括误导通模式；随后用上一时刻 \(v_{ds}\) 索引 LUT 中的电容相关矩阵参数。[pdf:E03][pdf:E08]

4. **构造 BE history sources。** gate loop 与 power loop 中的 \(C_{\mathrm{iss}},C_{\mathrm{rss}},C_{\mathrm{oss}}\) 被离散成当前步 conductance 和由前一步状态决定的 history current sources，gate drive 也进入一个等效历史源。单管最终表现为 \(G^*_{\mathrm{sw}}\) 与 \(i_d^{\mathrm{his}}\) 并联，再与 drain stray inductance 串联。[pdf:E03]

5. **在 half-bridge 内消元并并行计算。** 作者先用桥臂 KCL/KVL 消去内部中间量，再把原式改写为 Eq. (12)：当前两管 \(v_{ds}\) 直接由真实输入 \(i_h,v_h\)、历史电流源和上一时刻 \(i_d\) 计算，不必先串行得到 \(i_h^*,v_h^*\)。\(v_{gs}\) 和 \(i_d\) 可用相同方式并行求得；每个时间步总计需要 44 次乘法。[pdf:E05]

6. **与外部网络并行推进。** half-bridge transient calculation 和 system circuit calculation 都用 BE，并通过 register 与 latency insertion 交换边界量。Fig. 9 的硬件结构显示器件芯片以 200 MHz 为平台频率、实时模型以 100 MHz 时钟推进，即 10 ns 一步；half-bridge 与 system network 两侧的乘加可以同时执行。[pdf:E08]

7. **定点输出。** LLC 实现中，输入/输出变量采用 35-bit signed fixed point，LUT 固定参数采用 21-bit signed fixed point；输出包括每只管的 \(v_{ds},v_{gs},i_d\) 以及系统侧的 resonant current、capacitor voltage 等状态。[pdf:E09] 论文没有报告定点缩放规则、溢出/饱和策略或逐变量量化误差预算，这些实现细节不能从现有证据补写。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从物理支路到两个耦合微分关系

gate current 由 \(C_{gs}\) 与 \(C_{gd}\) 的 displacement current 构成，drain current 则由 channel current 与 \(C_{gd},C_{ds}\) 的 displacement current 共同决定。利用

\[
C_{\mathrm{rss}}=C_{gd},\qquad
C_{\mathrm{iss}}=C_{gd}+C_{gs},\qquad
C_{\mathrm{oss}}=C_{gd}+C_{ds},
\]

并用 \(v_{gd}=v_{gs}-v_{ds}\) 消去 \(v_{gd}\)，作者把 Eq. (1) 重写为

\[
\begin{cases}
R_g C_{\mathrm{iss}}\dfrac{dv_{gs}}{dt}
-R_g C_{\mathrm{rss}}\dfrac{dv_{ds}}{dt}
=V_{dr}-v_{gs},\\[4pt]
C_{\mathrm{oss}}\dfrac{dv_{ds}}{dt}
-C_{\mathrm{rss}}\dfrac{dv_{gs}}{dt}
=i_d-i_{ch}.
\end{cases}
\tag{2}
\]

第一行描述 gate drive 如何给 \(C_{gs}\) 充电并经 \(C_{gd}\) 受到 drain dv/dt 反馈；第二行说明 drain current 中有多少进入 channel、多少用于改变结电荷。Eq. (1)–(2) 与变量定义见 PDF 物理页 2。[pdf:E02]

### 6.2 用分段 conductance 代替在线 channel 方程

channel 与反并联二极管被归并为

\[
G_{\mathrm{sw}}=
\begin{cases}
G_{\mathrm{on}}, &
(v_{gs}>V_{th}\land v_{ds}\le v_{gs}-V_{th})\ \lor\ v_{ds}\le 0,\\[2pt]
\dfrac{g_{fs}(v_{gs}-V_{th})}{v_{ds}}, &
v_{gs}>V_{th}\land v_{ds}>v_{gs}-V_{th},\\[6pt]
G_{\mathrm{off}}, &
v_{gs}\le V_{th}\land v_{ds}>0.
\end{cases}
\tag{3}
\]

\(G_{\mathrm{on}}\) 取 drain-source on-resistance 的倒数，\(G_{\mathrm{off}}\) 可取 \(10^{-5}\,\mathrm{S}\)。作者同时把 body diode 的 ON-resistance 与 OFF-state conductance 近似为 MOSFET channel 的对应值，并明确承认：body-diode conduction 越久，switching-loss 误差越大；其合理性建立在二极管导通很短、且不主导总损耗的假设上。[pdf:E03]

### 6.3 Backward Euler 把电容记忆变成 Norton 支路

对 Eq. (2) 用步长 \(h\) 的 BE 离散，即以 \([v(k)-v(k-1)]/h\) 代替导数。消去当前 \(v_{gs}(k)\) 后得到

\[
i_d(k)=G_{\mathrm{sw}}^*(k)v_{ds}(k)
+i_{ds}^{\mathrm{his}}(k)
+i_{gs}^{\mathrm{his}}(k)
-i_{dr}^{\mathrm{his}}(k)
\equiv G_{\mathrm{sw}}^*(k)v_{ds}(k)+i_d^{\mathrm{his}}(k).
\tag{5}
\]

这里 “his” 表示由前一步状态或当前外部输入构成的 history source；Eq. (6) 给出 \(G_{\mathrm{sw}}^*\) 和三个历史源的显式系数。工程上，这一步把“解电容微分方程”变成“算一个并联 conductance 与 current source”。作者选 BE 而不是 FE，是因为包含多尺度电感、电容的 transient state equation 刚性高，FE 的稳定性强烈依赖参数。[pdf:E03]

### 6.4 从单管 Norton 支路到 half-bridge 代数模型

上下管满足

\[
\begin{cases}
i_{d,H}(k)-i_{d,L}(k)=i_h(k),\\
v_{ds,H}(k)+\dfrac{L_{d,H}}{h}\!\left[i_{d,H}(k)-i_{d,H}(k-1)\right]
+v_{ds,L}(k)+\dfrac{L_{d,L}}{h}\!\left[i_{d,L}(k)-i_{d,L}(k-1)\right]
=v_h(k).
\end{cases}
\tag{7}
\]

把两只管的 Eq. (5) 代入，可把桥臂写成

\[
\mathbf v_{ds}(k)=\mathbf N^*(k)\,\mathbf z^*(k),
\qquad
\mathbf v_{ds}=
\begin{bmatrix}v_{ds,H}\\v_{ds,L}\end{bmatrix},
\quad
\mathbf z^*=
\begin{bmatrix}i_h^*\\v_h^*\end{bmatrix}.
\tag{10}
\]

Eq. (7)–(11) 的意义不是创造新的器件物理，而是把两个器件与 stray inductance 的联立关系在桥臂内部解析消元，使外部网络只看到两个端口量。[pdf:E04]

### 6.5 消掉串行中间量

直接按 Eq. (10) 计算仍要先得到 \(i_h^*,v_h^*\)，形成串行路径。作者进一步展开这些中间量，得到

\[
\mathbf v_{ds}(k)
=\mathbf N^*(k)\mathbf z(k)
+\mathbf N^*_{i,\mathrm{his}}(k)\mathbf i_d^{\mathrm{his}}(k)
+\mathbf N^*_{i,d}(k)\mathbf i_d(k-1),
\qquad
\mathbf z(k)=
\begin{bmatrix}i_h(k)\\v_h(k)\end{bmatrix}.
\tag{12}
\]

因此，当前步的真实端口输入、所有历史源和上一时刻 drain current 可以直接进入并行乘加；附录给出三个矩阵的显式表达。[pdf:E05][pdf:E10]

### 6.6 非线性 transfer characteristic 的硬件近似

datasheet active-region 曲线先写成

\[
i_{ch}=k_{fs}(v_{gs}-V_{th})^2,
\tag{14}
\]

再在 \(i_{ch}=i_L/2\) 处用切线近似：

\[
i_{ch}=g_{fs}(v_{gs}-V'_{th}),\qquad
g_{fs}=2\sqrt{k_{fs}i_L}.
\tag{15}
\]

这样避免了在线平方/开方，但也把 dynamic channel behavior 压成一个由选定工作点决定的线性斜率。作者明确说该线性化不能准确反映 short-channel effect，主要影响 channel switching time；其是否真的只“较少影响”过冲和损耗，要由更宽工况验证，而不能从公式本身推出。[pdf:E07]

## § 7 — 实验设计与结论

### 问题 1：等效模型是否比系统级理想开关更接近 device reference？

**实验。** 作者在 Buck DC/DC 上选择 GeneSiC G3R30MT12J 与 Wolfspeed CAB006M12GM3 两种器件，用 LTSpice 模型作 reference，并与 MATLAB/Simulink SPS 理想开关模型比较；文中说明两个 MATLAB/Simulink 模型均以 1 ns 步长运行。比较量包括 \(u_{dc},i_L,v_{ds1},i_{d1}\)，并放大 turn-ON/OFF 瞬间。[pdf:E05]

**答案。** SPS 不能给出 switching process，并在系统状态上产生明显 cumulative error；proposed model 的系统状态和开关变量基本跟随 LTSpice。它还能呈现 drain dv/dt 引起的 gate crosstalk、switching duration 与 overshoot，但状态切换瞬间仍有误差，而且 load current 越大越明显；作者把原因归结为等效 conductance 难以表达 channel current 在 active region 与 linear region 之间的连续转换。[pdf:E05][pdf:E06]

### 问题 2：模型能否计算 switching loss？

**实验。** 在 G3R30MT12J Buck 工况中扫 drain current，并把 proposed model 的 \(E_{\mathrm{on}},E_{\mathrm{off}}\) 与 LTSpice 比较。[pdf:E06]

**答案。** 作者报告 turn-ON loss 平均误差 11.1%，turn-OFF loss 平均误差 9.8%，且误差随 drain current 增加而下降。[pdf:E06] 这支持“模型能给出有量级意义的损耗”，但不支持“损耗已达到几个百分点的高精度”；论文也没有给出误差分布、最大误差或不同温度下的结果。

### 问题 3：10 ns FPGA RTS 能否跟随真实 DPT 暂态？

**实验。** 作者在 XC7K325TFFG900-2 FPGA RTS 平台和实际 DPT 硬件平台上，在不同 load current 下比较 \(v_{ds}\) 与 \(i_d\) 的 turn-ON/OFF 波形。[pdf:E06][pdf:E08]

**答案。** 主 switching transition 的持续时间、过冲和动态趋势与硬件波形较一致，但 10 ns 步长不能准确模拟 stray parameters 引起的高频 tail oscillation；作者指出 DSP48 logic delay 与布局布线的 network delay 使进一步缩短实时步长很困难。[pdf:E08] 因此，证据支持“主暂态包络可实时重现”，不支持“所有高频 ringing 都被解析”。

### 问题 4：方法能否用于 soft-switching 整机，而不是只用于 DPT？

**实验。** 作者实现 full-bridge LLC resonant converter，在 200 kHz 和 250 kHz 两种 switching frequency 下比较 FPGA RTS 与硬件实验。LLC 参数包括 \(L_r=3\,\mu\mathrm H\)、\(L_m=450\,\mu\mathrm H\)、\(C_r=8\,\mathrm{nF}\)、\(C_o=650\,\mu\mathrm F\)、\(R_o=9\,\Omega\)、变比 \(n=1.25\)、输入 375 V；波形比较覆盖 resonant current 与 MOSFET \(v_{ds}\) 的多个换流区间。[pdf:E09]

**答案。** 以 150 ns transient window 计算 RMS error，200 kHz 时 \(i_{Lr}\) 为 4.43%、\(v_{ds,H}\) 为 2.38%；250 kHz 时分别为 5.14% 与 2.48%。[pdf:E10] 这说明在两组已测工况下，电压暂态误差约 2.5%，电流误差约 5.2%。论文结论段写“RMS error below 5%”，但 Table VI 明确含有 5.14%，所以本卡以表格数值为准，不复述“全部低于 5%”这一不严格概括。[pdf:E10]

### 问题 5：实时性和资源代价是否改善？

**实验。** 单个 half-bridge transient module 报告资源为 11 206 LUTs（5.50%）、1142 FlipFlops（0.28%）、132 DSP48s（15.71%）和 36 IOs（7.2%）。完整 LLC proposed model 为 24 527 LUTs（12.03%）、1860 FFs（0.46%）、192 DSP48s（22.86%）；同 bit width、同 time-step 的 time-piecewise model 为 27 965 LUTs（13.72%）、2082 FFs（0.51%）、359 DSP48s（42.74%）。[pdf:E08][pdf:E09]

**答案。** 在作者这套实现中，Eq. (12) 与 LUT 化确实把完整 LLC 的 DSP48 从 359 降到 192，约减少 46.5%，同时维持 10 ns step；LUT 与 FF 也有小幅下降。[pdf:E09] 但论文没有提供 post-route slack、最高可达频率、功耗或多桥臂扩展曲线；“数值稳定”主要由采用 BE 与实验波形间接支持，没有专门的长时稳定性或极端参数对照试验。

## § 8 — Take-aways

**5 句话：**

1. 本文把含 gate circuit、nonlinear junction capacitance、channel region 和 stray inductance 的 SiC MOSFET，压缩成 \(G_{\mathrm{sw}}^*\) 并联 history current source 的实时等效支路。[pdf:E03]
2. half-bridge 内部解析消元和 Eq. (12) 去掉了串行中间量，使器件暂态与外部网络能够以固定乘加结构并行推进，每步共 44 次乘法。[pdf:E05]
3. FPGA 上的非线性不是在线求复杂函数，而是用 datasheet-sampled LUT 和 active-region 切线换取确定时延。[pdf:E07][pdf:E08]
4. 10 ns DPT/LLC 实验支持主换流包络和整机状态的实用精度，但不支持高频 tail oscillation；Buck loss 的平均误差仍约为 10%。[pdf:E06][pdf:E08]
5. 最关键的研究边界不是“是否实时”，而是静态分段 conductance 在多大工况包络内仍代表动态 channel/diode physics，论文只做了有限的器件、频率和工作点覆盖。[pdf:E06][pdf:E07][pdf:E10]

**3 句话：**

1. 这是一种面向 FPGA 编译结构设计的 behavioral model：用 BE history source 保留记忆，用 half-bridge 消元获得并行性，用 LUT 承担非线性。[pdf:E03][pdf:E05]
2. 它在一套硬件上以 10 ns step 把完整 LLC 的 DSP48 用量从 time-piecewise model 的 359 降至 192，并在已测工况得到 \(v_{ds}\) RMS error 不超过 2.48%、\(i_{Lr}\) 不超过 5.14%。[pdf:E09][pdf:E10]
3. 这些结果足以证明工程可行性，但不足以证明跨温度、gate resistance、长 body-diode conduction 与高频 ringing 的普适精度。

**1 句话：**

本文证明了“先把器件暂态编译成固定成本的桥臂代数算子”可以在 FPGA 上达到 10 ns 整机 RTS，但其可信范围仍由分段 conductance 的物理近似而不是算力决定。[pdf:E05][pdf:E08]

## § 9 — 最脆弱的假设

最脆弱的假设是：**由上一时刻 \(v_{gs},v_{ds}\) 选择的少数静态 conductance region，加上一条固定工作点的 transfer-characteristic 切线，足以代表真实 channel 与 body-diode 在换流过程中的连续动态。**

这个假设一旦失效，受影响的不只是某个局部参数，而是整篇论文的核心交换：作者正是靠 region selection 和 LUT coefficient selection 消除了 nonlinear iteration、固定了 44 次乘法并实现外部网络并行。如果真实器件在阈值附近、温度变化、不同 gate resistance、大电流或 third-quadrant conduction 下跨越这些边界的方式与静态曲线不一致，模型会在错误时间选择 \(G_{\mathrm{sw}}\)，进而同时污染 \(v_{ds}\)、\(i_d\)、switching loss 和下一步 history sources。[pdf:E03][pdf:E05][pdf:E08]

论文其实给出了三条警报。第一，作者承认 equivalent conductance 难以表达 active/linear region 之间 channel current 的连续转换，且切换误差随 load current 增大而变明显。[pdf:E06] 第二，active-region 二次 transfer curve 被单切线代替，作者承认这不能准确反映 short-channel effect 并会改变 channel switching time。[pdf:E07] 第三，body diode 被近似成与 MOSFET channel 相同的 ON/OFF conductance；作者明确说二极管导通越久，loss error 越大，只因当前假定其 conduction duration 很短才认为可接受。[pdf:E03]

现有证据覆盖两种 Buck 器件、DPT 的若干 load current，以及 LLC 的 200/250 kHz，但没有 temperature、gate resistance、deadtime、器件批次和长 third-quadrant conduction 的系统 sweep。[pdf:E05][pdf:E08][pdf:E09] 因而，“在这些展示工况有效”是论文直接支持的结论；“对高频 SiC converter 普遍有效”仍是有待扩展验证的外推。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 LLC FPGA，而是 Eq. (3)–(6)、Eq. (12) 和 LUT 参数化能否在 **10 ns、无迭代** 条件下保住换流精度。

**数据与参考。** 选 G3R30MT12J，使用论文 Table I 的 Buck/DPT 参数和 datasheet 的 \(C_{\mathrm{rss}}(v_{ds})\)、\(C_{\mathrm{oss}}(v_{ds})\)、transfer curve；以厂家 LTSpice model 的 1 ns 仿真作 reference。论文对应设置和两个器件的参数入口见 PDF 物理页 5。[pdf:E05]

**实现。** 在 MATLAB/Simulink 或一段定点友好的 C/HDL reference code 中实现：三段 \(G_{\mathrm{sw}}\)、BE history sources、按 \(v_{ds}(k-1)\) 索引的 junction-capacitance LUT、Eq. (12) half-bridge solve。先用 floating point 复现算法本身，再把输入/输出量化为 35 bit、LUT 系数 21 bit，以便区分模型误差和 quantization error。[pdf:E03][pdf:E05][pdf:E09]

**实验矩阵。** 保持 10 ns step，至少扫 5、10、20、30、40 A 五个 drain-current 点，并增加三档 external gate resistance。每个 turn-ON/OFF 记录 150 ns window 内的 \(v_{ds},i_d,v_{gs}\)、switching duration、peak overshoot、\(E_{\mathrm{on}},E_{\mathrm{off}}\)，同时确认每步没有迭代且计算路径固定。150 ns RMS window 与论文整机误差口径一致。[pdf:E10]

**支持条件。** 若在预先规定的多数工况中，\(v_{ds}\) transient RMS error 不高于 2.5%、current RMS error 不高于 5.2%，且 \(E_{\mathrm{on}},E_{\mathrm{off}}\) 的跨工况平均误差分别不高于约 12% 和 10%，即可认为复现支持论文展示的精度量级；这些阈值分别取自 Table VI 和 Fig. 7 的报告结果，而不是另造标准。[pdf:E06][pdf:E10]

**反驳条件。** 若仅改变 gate resistance 或 load current 就频繁触发错误 region、波形出现数值振荡，或损耗/过冲误差显著超过上述量级，则核心 claim 被反驳；即使某一标称点波形好看，也不能算复现成功。

## § 11 — 最强反例设计

最强反例是构造一个 **长 third-quadrant conduction 后再 hard commutation** 的 half-bridge，而不是单纯把频率再提高。

具体做法是：在同一 SiC half-bridge 上把 deadtime 从几十纳秒扫到数百纳秒甚至 \(1\,\mu\mathrm s\)，让 low-side body diode 在可控时长内承载负载电流；同时交叉扫 junction temperature、load current 和 external gate resistance。随后使另一只管 turn-ON，比较硬件、可信 device SPICE 与 proposed model 的 diode-conduction voltage、commutation charge、\(v_{ds}/i_d\) overshoot、\(E_{\mathrm{on}}\) 和 150 ns RMS error。论文自己的近似把 body diode 的 ON/OFF conductance 视为 channel 对应值，并假设其导通短、不主导损耗；这个试验有意让该假设不成立。[pdf:E03]

如果模型误差随 diode-conduction duration 单调放大，尤其是 switching loss 或换流峰值远超 Buck 中约 10% 的损耗误差，而提高 LUT sampling density 仍不能修复，就说明问题不在结电容查表，而在 conductance state definition 本身。[pdf:E06][pdf:E07] 这会直接挑战“同一个非迭代等效模型可适应 power electronic converters”的范围。反之，如果在这一压力工况下仍维持论文 Table VI 的误差量级，才是对核心机制更强的支持。

## § 12 — Follow-up Research Idea

电力电子与实时仿真领域通常看重：模型是否保持关键物理约束、是否在真实硬件和多工况下可验证、是否能以确定时延映射到 FPGA，以及精度—资源—步长之间是否给出可复现的边界。基于 §9，候选方向是：**把研究目标从“逐点拟合 switching waveform”改成“学习并认证一次 commutation 的 charge/energy map”，再把这个 event map 编译成定时可证的 FPGA 算子。** 这是候选判断；本卡没有做额外相关工作检索，因此不声称 novelty。

**(a) 未满足的需求。** 现模型用上一时刻电压选择静态 conductance，难以表达跨区连续 channel current、长 body-diode conduction 和未被 10 ns 采样解析的快速 ringing；但直接恢复完整 device nonlinear solve 又会失去固定时延。[pdf:E06][pdf:E07][pdf:E08]

**(b) 可能的研究价值。** 新问题不再要求每个 10 ns sample 都追随全部高频细节，而要求一次换流前后的 terminal charge、energy dissipation、peak stress 与状态跳变满足守恒和误差界。若能在相同 DSP/latency 下对未见 temperature、gate resistance 和 deadtime 维持这些物理量的误差界，它比增加 LUT 分段更能支撑 HIL 中的损耗、保护和可靠性研究。

**(c) 可借鉴的相邻工具。** 可以借鉴 hybrid systems 的 event map、switched-DAE 的 charge conservation、passivity-preserving model reduction，以及带单调性/能量约束的 surrogate。离线由高保真 SPICE 或实验辨识“pre-commutation state \(\rightarrow\) post-commutation state + dissipated energy”的低维映射；在线只在检测到换流事件时调用固定深度的 piecewise-affine 或 rational map，事件之间仍用本文的 BE network solver。

**(d) 第一个证伪实验。** 采用 §11 的 deadtime × temperature × current × gate-resistance 留一组合测试；训练时完全不见其中一组器件/温度，部署后同时比较 terminal charge error、energy error、peak-stress error、DSP48、critical-path delay 和是否严格按 10 ns deadline 完成。若受约束 event map 在未见工况不能显著优于 Eq. (3)–(15)，或为了精度必须引入不确定迭代，它就应被淘汰。

**(e) 与本文的实质区别。** 本文把连续器件物理压成“每个 sample 的等效 conductance”；候选方法把换流定义成“跨越一个事件窗口的守恒状态变换”。它改变的是建模对象和验收目标，不是给现有 LUT 再加一个 correction module。
