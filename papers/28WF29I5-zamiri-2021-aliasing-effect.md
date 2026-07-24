# Analysis of the aliasing effect caused in hardware-in-the-loop when reading PWM inputs of power converters

作者：Elyas Zamiri、Alberto Sanchez、María Sofía Martínez-García、Angel de Castro  
出处：International Journal of Electrical Power & Energy Systems，136 (2022) 107678  
年份：2022（在线发表于 2021）  
DOI：10.1016/j.ijepes.2021.107678  
Zotero key：28WF29I5  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接研究的问题**不是 Boost converter（升压变换器）的数值模型是否足够精细，而是一个更靠近 HIL（hardware-in-the-loop，硬件在环）接口的问题：外部控制器产生的 PWM 边沿只能在 HIL 的离散采样时刻被读取，边沿位置因而被量化；这种看似不超过一个采样周期的输入误差，是否会在频域中形成低于开关频率的 aliasing（混叠）分量，并进一步变成电感电流或电容电压中的虚假稳态振荡。作者在摘要中把风险直接落到闭环调试：伪振荡可能混淆控制器行为，使 HIL 输出不再代表真实功率级。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，原因是 HIL 的价值建立在“被仿真子系统的动态响应可信”之上。提高 ODE 求解精度、缩短 simulation step（仿真步长）并不能自动消除外部 PWM 与 HIL 时钟不同步造成的边沿丢失；即使采用 FPGA、I/O latency（输入输出延迟）很低，接口仍只能在时钟沿观察 PWM。论文的 Table 1 给出最坏占空比读取误差的量级：当开关周期为 5000 ns、采样周期为 500 ns 时，最大采样误差可达 10%；当二者分别为 10000 ns 和 150 ns 时也仍有 1.5%。[pdf:E02]（PDF 物理页 2，Table 1）

因此，这项工作的工程价值在于把“偶发波形抖动”变成可诊断的频谱机制：先由 PWM 与采样时钟的相对周期预测低频混叠线，再用功率变换器的小信号频率响应判断这些线是否会穿过高增益频段。它提供的主要价值是解释、定位和选参，而不是一个已经完整实现、无额外成本的消除算法。

## § 2 — 前人工作与不足

**论文对前人工作的归纳**分成两类。第一类从 HIL 数值实现入手：缩短仿真步长、简化模型、选择 Forward Euler、Tustin、Adams–Bashforth 或 Runge–Kutta 等 ODE 离散方法，以降低总体误差；第二类直接提高开关输入的时间分辨率，例如 double-interpolation、interpolation–extrapolation、post-correction 和 time-averaged method。作者指出，这些 oversampling（过采样）方案能提高精度，但会增加资源、算法复杂度和补偿延迟；FPGA 让步长更小后，工程上常常省略过采样，但在中高开关频率下，模型计算时间仍可能使采样步长无法远小于开关周期。[pdf:E03]（PDF 物理页 2，Introduction 左栏上半部）

第二类是已有 aliasing 研究。论文引用了通用离散采样的频带搬移、PWM Boost converter 的 duty perturbation（占空比扰动）与 aliased output，以及数字逆变器因采样输出电流而产生的 alias。**作者的直接声称**是：针对“外部 PWM 被 HIL 离散输入读取”这一转换误差，还缺少一套详细频域分析；既有 HIL 工作更关注如何提升输出精度，而没有把采样误差的重复模式、混叠频率和输出状态变量联系起来。[pdf:E04]（PDF 物理页 2，Introduction 左栏中下部）

精确地说，先前方法“不够”并非因为完全不知道采样会出错，而是因为它们主要回答“怎样把误差压小”，没有回答三个诊断问题：误差为什么可能落到很低的频率、哪些 `Tsw–dt–D` 组合最危险、输入频谱怎样经过具体拓扑的动态增益变成输出振荡。本文的增量是把这三步闭合。由于本任务没有检索附件之外的文献，关于“首次”或 novelty（新颖性）的判断只保留为作者声称，不作独立认证。

## § 3 — 重建作者的思考路径

可以从已有工程事实逆向走到本文思路，而不预设论文结论：

1. HIL 模型通常按固定时钟更新；外部 PWM 来自另一硬件时钟，所以每个上升沿和下降沿只能被延迟到下一个可观察采样点。单个边沿误差被限制在 `0` 到 `dt`，但误差符号和大小会随两只时钟的相位滑移而变化。[pdf:E05]（PDF 物理页 2，Section 2 与 Eq. (1) 周边正文）
2. 如果 `Tsw` 与 `dt` 在统一时间量化下可公度，边沿误差序列不会随机消失，而会在若干开关周期后重复。重复序列必然具有一个低于开关频率的基频及其谐波；当重复长度很大时，基频会很低。[pdf:E06]（PDF 物理页 3，Fig. 1）
3. 功率变换器本来会衰减高于开关频率的纹波，但对远低于开关频率的 duty disturbance（占空比扰动）未必有足够衰减。于是高频 PWM 的采样误差可以通过“长重复模式”折叠成低频成分，再被功率级动态放大或保留。[pdf:E07]（PDF 物理页 3，Eq. (2) 及其前后正文）
4. 只看平均 duty error 会漏掉这种问题：短重复模式更像 DC offset，长重复模式则更像低频稳态振荡。真正需要比较的是 sampled PWM（文中记为 PWMH）的谱线与 duty-to-state transfer function（占空比到状态变量传递函数）。
5. 因此最自然的验证路径是：构造若干仅改变 `Tsw`、`dt`、`D` 的案例，先看 PWMH 频谱，再看 Boost 电流频谱和时域波形，最后用独立硬件时钟的 FPGA 实验确认。

这条路径的关键转折是把“每个边沿最多晚一个 `dt`”从局部时间误差，重新理解为一个具有周期结构的调制信号。

## § 4 — 核心 Intuition

PWM 的每个边沿虽然只被量化了不到一个采样周期，但两只时钟的相对相位会产生一个长周期重复的误差图样；图样越长，其基频越低。[pdf:E05]（PDF 物理页 2，Eq. (1) 与同步/异步分类）这个低频分量如果落在功率变换器 duty-to-current 或 duty-to-voltage 的高增益区，就不会像开关纹波那样被自然滤掉，而会表现为 HIL 输出中的虚假低频振荡。[pdf:E08]（PDF 物理页 4，Fig. 3）所以问题的核心不是“采样误差有多大”这一单一标量，而是“采样误差的频率落在哪里，以及功率级在那里有多大增益”。

## § 5 — 具体方法与完整 Pipeline

以论文中最明显的异步案例 Case 3 为例，输入是 `Tsw = 10001 ns`、`dt = 500 ns` 的外部 PWM；作者选择 `D = 0.400` 与 `D = 0.416` 来分别展示较小和较大的混叠幅值。按 Table 2，这一组合的重复长度 `N = 500`，fundamental aliasing frequency（基波混叠频率）为 `199.98 Hz`。[pdf:E09]（PDF 物理页 4，Table 2）完整 pipeline 如下：

1. **采样外部 PWM。** HIL 每隔 `dt` 读取一次数字输入，把真实 PWM 转换为 PWMH。上升沿和下降沿分别产生文中记为 `ET`、`ED` 的检测延迟，二者绝对值范围均为 `0` 到 `dt`。[pdf:E05]（PDF 物理页 2，Section 2）
2. **确定重复模式。** 计算 PWMH 的边沿误差序列经过多少个开关周期重新出现。论文用 `N` 表示重复长度，并以 `N < 10` 作为“接近理想同步”的工作性分类，`N > 10` 归为异步；这不是一般信号处理中的标准同步定义，而是本文用于分组的经验阈值。[pdf:E05]（PDF 物理页 2，Eq. (1) 周边正文）
3. **得到输入混叠谱。** 重复周期为 `N·Tsw`，因此 PWMH 中会出现 `k/(N·Tsw)` 的谱线。固定 `Tsw` 和 `dt` 时，改变 `D` 主要改变谱线幅度，不改变谱线位置；Fig. 2 的四组 FFT 用于展示这一点。[pdf:E10]（PDF 物理页 4，Fig. 2）
4. **把输入谱映射到功率级状态。** 论文采用无损、CCM 小信号 Boost 模型，分别写出 duty 到电感电流和电容电压的传递函数。对每一条 PWMH 子谐波，用对应频率处的 transfer-function gain（传递函数增益）估计输出分量；Fig. 4 显示电感电流频谱具有与 PWMH 相同的主要频率成分。[pdf:E11]（PDF 物理页 3，Eq. (4)）[pdf:E12]（PDF 物理页 3，Eq. (5)–(6) 与参数）[pdf:E13]（PDF 物理页 5，Fig. 4）
5. **与高精度 reference 比较。** MATLAB 中，待测模型按 Table 2 的 `dt` 读取 PWM；另一个 `1 ns` 步长模型作为 reference，以避免低频采样混叠。比较状态变量时域、FFT、MAE 和 peak-to-peak（峰峰值）。[pdf:E04]（PDF 物理页 2，论文目标与实验路线）
6. **进行硬件验证。** Boost HIL 模型用 LabVIEW 实现在 NI myRIO-1900 的 Xilinx Zynq-7010 FPGA 上，模型 latency 为 6 个 FPGA clocks；板载时钟周期为 `25 ns`，所以最小 PWM 采样周期为 `150 ns`。外部 PWM generator 与 myRIO 使用独立硬件，形成真实的 clock-asynchronous 输入条件。[pdf:E14]（PDF 物理页 8，实验平台正文）
7. **输出诊断与缓解建议。** 输出不只是“误差大小”，还包括主误差频率是否等于预测的 aliasing frequency、该频率是否落在模型高增益区，以及轻微调整 `dt` 或使用 oversampling 后是否移出危险区。

论文没有报告具体 ODE 离散算法、fixed-point word length（定点字长）、FPGA LUT/DSP/BRAM 占用、最大时钟裕量、流水并行结构或闭环控制器实现；因此不能从本文判断这些实现细节对结果的独立贡献。

一个直观的同步案例解释了 offset 的来源：Case 1 中 `D = 0.411` 对应真实 on-time `4110 ns`，按 `dt = 150 ns` 读取时只能形成 `4050 ns` 或 `4200 ns` 的离散值；三周期模式的平均值可能成为 `4100 ns` 或 `4150 ns`，因而出现 `−10 ns` 或 `+40 ns` 的平均偏差，且不超过 `dt/N = 50 ns`。[pdf:E15]（PDF 物理页 5，Case 1 模式解释）异步案例则用更长的模式逼近正确平均值，offset 可能更小，但代价是把误差能量放到低频振荡中。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 重复长度为何决定 aliasing 频率

论文把真实开关周期记为 `Tsw`，HIL 输入采样周期记为 `dt`。当二者用同一离散时间单位表示时，PWMH 的采样相位在若干开关周期后回到原位置，重复长度定义为

\[
N = \frac{\operatorname{LCM}(T_{sw},dt)}{T_{sw}}. \tag{1}
\]

[pdf:E05]（PDF 物理页 2，Eq. (1)）这等价于在整数时间单位下的 `N = dt/gcd(Tsw,dt)`。工程含义是：`N` 不是模型内部状态维数，而是外部 PWM 边沿相对于 HIL 采样格点的 phase pattern（相位图样）长度。

既然误差序列每 `N·Tsw` 重复一次，它的 Fourier series 基频就是

\[
f_{aliasing}(k)=\frac{k}{N T_{sw}},\qquad k=1,2,3,\ldots . \tag{2}
\]

[pdf:E07]（PDF 物理页 3，Eq. (2)）因此，大 `N` 会把能量推到低频。这里 Eq. (2) 预测的是可能出现的离散频率位置；具体幅度仍取决于 `D`、初始相位以及边沿误差序列的形状。

### 6.2 输入 duty perturbation 如何变成状态振荡

对无损 Boost converter 的连续导通小信号模型，论文给出 duty perturbation `\tilde d(s)` 到电感电流 `\tilde i_L(s)` 的传递函数

\[
\frac{\tilde i_L(s)}{\tilde d(s)}=
\frac{R_O C V_C s+2V_C}
{R_O L C s^2+L s+(1-D)^2R_O}. \tag{4}
\]

[pdf:E11]（PDF 物理页 3，Eq. (4)）同一扰动到电容电压的传递函数为

\[
\frac{\tilde v_C(s)}{\tilde d(s)}=
\frac{-L V_C s+(1-D)^2R_O V_C}
{(1-D)\left(R_O L C s^2+L s+(1-D)^2R_O\right)}, \tag{5}
\]

并采用稳态关系

\[
V_C=\frac{V_{in}}{1-D}. \tag{6}
\]

[pdf:E12]（PDF 物理页 3，Eq. (5)–(6)）两条传递函数共享二阶分母，表示同一电感–电容动态；电压通道的分子包含 Boost converter 典型的非最小相位特征。对某一 aliasing 谱线 `f_k`，输出小信号幅度的基本估计就是“PWMH 在 `f_k` 的 duty 幅值 × 对应传递函数在 `f_k` 的幅值”。

论文使用 `L = 800 μH`、`C = 80 μF`、`D = 0.4`、`Vin = 12 V`、`RO = 12 Ω` 绘制 Bode plots，并指出约 `1 kHz` 以下的子谐波更容易以较高增益进入输出。[pdf:E12]（PDF 物理页 3，参数正文）[pdf:E08]（PDF 物理页 4，Fig. 3）这解释了为何 Case 3 的 `199.98 Hz` 与 Case 2/4 的约 `667 Hz` 分量比 Case 1 的 `33.333 kHz` 更危险：不是因为 Case 1 没有量化误差，而是其主要重复频率更容易被功率级衰减。

### 6.3 推导的边界

上述推导依赖固定 `Tsw`、固定 `dt`、固定或稳态附近的 `D`，并把 PWMH 误差视为周期信号，再用 linear small-signal model（线性小信号模型）传播。它没有推导 variable-frequency PWM、cycle-to-cycle jitter、闭环快速占空比调制、DCM（断续导通模式）、器件损耗或饱和限制下的频谱。因此 Eq. (2) 是本文实验条件下的确定性 line-spectrum model（线谱模型），不是任意实际 PWM 的通用误差上界。

## § 7 — 实验设计与结论

**问题 1：PWM 采样是否真的产生 Eq. (2) 预测的子谐波？**  
实验：作者设置四组 `Tsw–dt` 组合，包括一个短重复长度案例和三个长重复长度案例，并在每组中选择两个 duty cycles。Table 2 给出的 fundamental aliasing frequencies 分别为 `33.333 kHz`、`666.6 Hz`、`199.98 Hz`、`673.3 Hz`。[pdf:E09]（PDF 物理页 4，Table 2）回答：Fig. 2 的 PWMH FFT 在这些频率族上出现谱线；相同 `Tsw–dt` 下改变 `D` 主要改变幅度，而不改变频率位置。[pdf:E10]（PDF 物理页 4，Fig. 2）

**问题 2：这些输入子谐波会不会进入电感电流？**  
实验：把 PWMH 频谱、Boost 小信号 Bode plots 和电感电流频谱并列比较。回答：电感电流中出现与 PWMH 相同的主要频率成分，幅度由对应频率处的功率级增益调制；低频且输入幅度大的 Case 3、Case 4 最明显。[pdf:E08]（PDF 物理页 4，Fig. 3）[pdf:E13]（PDF 物理页 5，Fig. 4）[pdf:E16]（PDF 物理页 7，Fig. 7）

**问题 3：误差究竟由 `dt` 决定，还是由 `dt–Tsw–D` 的组合决定？**  
实验：作者扫描 duty cycle，比较状态变量 MAE，并进一步扫描 `dt`。回答：更大的 `dt` 通常产生更高的最坏误差，但误差不是随 `dt` 单调变化，而是在特定组合上形成尖峰。Table 3 中最突出的是 Case 3、`D = 0.416`：电感电流 MAE 为 `12.5076%`，电容电压 MAE 为 `4.6137%`；同一 Case 3 在 `D = 0.400` 时电感电流 MAE 仅 `0.1151%`。[pdf:E17]（PDF 物理页 5，Table 3）Fig. 8 的扫描进一步表明，只把 `dt` 从 `500 ns` 改为 `525 ns`，最大误差约可降低 20 倍，说明危险点来自相位重复结构而非单纯“步长越大越差”。[pdf:E18]（PDF 物理页 7，Fig. 8）[pdf:E14]（PDF 物理页 8，Fig. 8 解释正文）

**问题 4：MATLAB 中的振荡能否在 FPGA HIL 上复现？**  
实验：作者在 NI myRIO-1900 FPGA 上实现模型，用独立外部 PWM generator 输入相同案例，观察稳态电感电流，并轻微改变 `dt`。Fig. 9 展示四组硬件波形，Fig. 10 比较 `150→175 ns` 与 `500→525 ns` 的调整。[pdf:E19]（PDF 物理页 8，Fig. 9）[pdf:E20]（PDF 物理页 8，Fig. 10）回答：异步案例的 simulation 与 experiment 量级接近；Case 3、`D = 0.416` 的峰峰振荡为 `1.5 A`（仿真）和 `1.4 A`（实验），Case 4、`D = 0.400` 为 `175 mA` 和 `190 mA`。[pdf:E21]（PDF 物理页 9，Table 4）

**问题 5：所谓“同步案例”在真实硬件中是否只剩 DC offset？**  
实验：Case 1 的理想仿真给出近似零低频峰峰振荡，但硬件仍测到 `85 mA` 与 `160 mA`。回答：作者认为独立时钟不可能保持完美同步，极小频差会使实际系统变成长重复长度的异步情形；因此仿真的“纯 offset”不应被当作硬件可稳定达到的安全状态。[pdf:E21]（PDF 物理页 9，Table 4）[pdf:E22]（PDF 物理页 9，实验对比正文）[pdf:E23]（PDF 物理页 9，Conclusion 前正文）

**论文直接结论**是：输入 PWM 采样产生的 aliasing frequency 能解释主要输出误差成分；在标称电流约 `2.8 A` 的实验中，`dt = 150 ns` 和 `500 ns` 时分别观察到最高约 `190 mA` 和 `1.4 A` 的子谐波振荡；对于无法继续缩短实时步长的系统，可考虑输入过采样或轻微改变 `dt`，把谱线移向更易衰减的频段。[pdf:E24]（PDF 物理页 9，Fig. 10 解释与建议）[pdf:E23]（PDF 物理页 9，Conclusion 前正文）

**不能外推的范围**是：实验只覆盖一个无损 Boost 模型、稳态开环 PWM、有限的 `Tsw–dt–D` 组合和一块 myRIO FPGA；没有闭环控制器、其他拓扑、负载阶跃、变频 PWM、clock jitter 统计、资源开销或稳定性裕量实验。因此“会混淆闭环调试”有合理机制支撑，但本文没有直接完成闭环控制失败的实验验证。

## § 8 — Take-aways

**5 句话：**

1. 外部 PWM 的边沿量化误差会形成重复序列，而不仅是独立随机误差。
2. 重复长度 `N` 把误差能量放到 `k/(N·Tsw)` 的子谐波；`N` 大时，原本高频的 PWM 误差会折叠到低频。[pdf:E07]（PDF 物理页 3，Eq. (2)）
3. 输出是否严重失真由 PWMH 子谐波幅度与功率级在该频率处的增益共同决定，所以 `D`、`Tsw`、`dt` 必须联合考虑。[pdf:E10]（PDF 物理页 4，Fig. 2）[pdf:E08]（PDF 物理页 4，Fig. 3）
4. 论文的 MATLAB 与 myRIO 结果证明，特定组合可把稳态电感电流误差从几乎不可见推到安培级，而轻微改变 `dt` 又可能显著降低它。[pdf:E14]（PDF 物理页 8，参数扫描正文）[pdf:E21]（PDF 物理页 9，Table 4）
5. 最可靠的工程实践不是只追求最小 `dt`，而是检查混叠谱位置、进行 duty/phase sweep，并在必要时采用过采样或避开危险采样比。

**3 句话：**

1. PWM 输入采样误差的危险性取决于其频谱，而不只取决于单边沿最大误差。
2. `N·Tsw` 形成的低频重复模式，经 Boost 的 duty-to-state 增益后可变成明显的虚假稳态振荡。[pdf:E13]（PDF 物理页 5，Fig. 4）
3. 论文把这一机制在 MATLAB 和 FPGA 上闭合，但只在固定周期、稳态、单一拓扑条件下完成验证。

**1 句话：**  
独立时钟下，HIL 对 PWM 的离散读取可以把微小边沿量化变成低频大振荡，所以采样比本身就是模型可信度的一部分。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在分析窗口内 `Tsw`、`dt` 和 `D` 足够固定，使 PWMH 误差具有有限、稳定的重复长度 `N`，因而能够用离散谱线 `k/(N·Tsw)` 表示。** Eq. (1)、Eq. (2)、同步/异步分类、四案例设计以及“轻微调 `dt` 把谱线移开”的缓解方案都依赖这个 stationarity（平稳性）前提。[pdf:E05]（PDF 物理页 2，Eq. (1) 与分类）[pdf:E07]（PDF 物理页 3，Eq. (2)）

这个假设在实际闭环控制器里很容易失效：占空比会逐周期变化，外部 oscillator 会有 phase noise、jitter 和温漂，某些控制器还使用 variable-frequency 或 spread-spectrum PWM。此时严格的 LCM 可能没有稳定工程意义，`N` 会随时间变化，离散线谱会展宽、漂移或变成 cyclostationary/stochastic spectrum（循环平稳/随机频谱）。一旦发生这种情况，本文最强的定量 claim——“主要误差频率可由一个固定 `N` 预测”——就可能失效；较宽泛的结论“异步采样会产生低频误差”仍可能成立。

论文为固定周期条件提供了较强证据：四组 FFT、状态频谱、时域仿真和异步硬件结果相互吻合。它也无意中给出了假设脆弱性的证据：理想 Case 1 仿真认为只应有 offset，但真实硬件因无法保持完美同步而出现 `85–160 mA` 振荡。[pdf:E21]（PDF 物理页 9，Table 4）作者据此承认实际系统中的“同步”并不稳定。[pdf:E23]（PDF 物理页 9，实验总结）缺失的关键证据是：在受控 jitter、frequency drift、动态 duty 和闭环负载扰动下，固定 `N` 模型还能否预测 dominant error band（主误差频带）及其幅值。

## § 10 — 最小复现实验

一周内最有价值的复现不是重做完整 FPGA，而是验证“Eq. (2) 的输入谱线会经过功率级增益出现在输出误差中，并且轻微改变 `dt` 能移除危险峰”。

**数据与工况。** 生成理想外部 PWM，重点复现 Case 3：`Tsw = 10001 ns`，`D = 0.400/0.416`，测试 `dt = 500 ns` 与 `525 ns`；Boost 参数采用 `L = 800 μH`、`C = 80 μF`、`Vin = 12 V`、`RO = 12 Ω`。论文在 `500 ns`、`D = 0.416` 时报告 `N = 500`、fundamental aliasing frequency `199.98 Hz`、电感电流 MAE `12.5076%`，并指出改为 `525 ns` 后最大误差约下降 20 倍。[pdf:E09]（PDF 物理页 4，Table 2）[pdf:E17]（PDF 物理页 5，Table 3）[pdf:E14]（PDF 物理页 8，参数扫描正文）

**实现。** 建立两个使用相同状态方程和相同数值积分器的模型：reference 分支按精确 PWM 事件更新，HIL 分支只在每个 `dt` 采样开关状态并保持到下一采样点。把 numerical integration error（数值积分误差）与 input-sampling error 分离：两分支只在开关状态获取方式上不同。由于论文未报告 MATLAB 模型的具体积分器，复现应明确记录算法，并做步长收敛检查。

**测量。** 对至少一组完整误差重复周期记录 PWMH、`iL` 和 reference `iL`；扫描多个初始 PWM phase。计算 PWMH FFT、`iL` error FFT、current MAE、低频峰峰值，并检查输出主峰是否与输入 aliasing 谱线重合。用 `D = 0.400` 作为同一采样比下的低幅度对照。

**支持标准。** `dt = 500 ns`、`D = 0.416` 时，PWMH 与电流误差在约 `199.98 Hz` 出现共同主峰，电流误差达到论文报告的同一数量级；改为 `525 ns` 后，多数初始相位下的低频误差显著下降；`D = 0.400` 明显较小。[pdf:E25]（PDF 物理页 6，Fig. 6）[pdf:E16]（PDF 物理页 7，Fig. 7）

**反驳标准。** 在数值收敛和相位扫描后，输出误差没有出现预测频带、主要峰与 PWMH 不共频，或 `525 ns` 的改善只来自某个偶然初始相位而非稳健趋势。这样的结果会直接削弱“固定重复模式 + 小信号增益”是主因的 claim。

## § 11 — 最强反例设计

最强反例应直接破坏有限重复长度，而不是换一个普通拓扑。构造两只独立时钟：PWM nominal period 与 HIL `dt` 保持论文案例的平均值，但给 PWM 时钟加入可控的缓慢 frequency drift 和 cycle-to-cycle jitter；平均 duty、功率级参数和 HIL 数值算法保持不变。让“按标称整数 ns 计算的 `N`”在纸面上不变，同时使真实相位不再精确重复。

实验同时输出三种结果：长时间 FFT、短时 spectrogram（时频图）和电感电流误差。固定 `N` 理论预测稳定的 `k/(N·Tsw)` 离散线；反例预期这些线会随相位漂移而展宽或游走，输出误差的主频与幅值由 jitter/drift law（抖动/漂移规律）决定，而非一个固定 LCM。再加入一个完全无 jitter 的 control，确认变化不是数值积分或 Boost 本身造成。

这个攻击最有力，因为它挑战的是 Eq. (1)–(2) 的周期性前提。论文自己的 Case 1 已经露出这一裂缝：仿真近似无低频峰，而硬件因不可能完美同步出现 `85 mA` 和 `160 mA` 的振荡。[pdf:E21]（PDF 物理页 9，Table 4）如果受控漂移实验显示“同一标称 `N` 对应完全不同、非离散的输出误差频带”，那么本文可以保留定性警告，但不能再把固定 `faliasing` 当成真实 HIL 的充分预测器。

## § 12 — Follow-up Research Idea

**候选研究方向：建立“无有限 `N`”的 clock-asynchronous HIL 误差认证模型。** 本任务没有检索附件外相关工作，因此不声称该方向具有 novelty；它是由第 9 节证据约束产生的候选想法。

**（a）未满足的需求。** 真实 HIL 需要的不是在某个固定 `Tsw–dt–D` 下解释一条谱线，而是在独立时钟、jitter、温漂和动态 duty 下回答：输出误差的概率分布、最坏频带和置信上界是什么，怎样在不改变实时模型步长的前提下保证误差不过界。论文已表明轻微调 `dt` 可能把误差降低约 20 倍，但也说明危险峰高度离散且依赖特定组合；这使手工试参难以成为认证方法。[pdf:E18]（PDF 物理页 7，Fig. 8）[pdf:E14]（PDF 物理页 8，Fig. 8 解释）

**（b）为什么可能产生本领域认可的价值。** 在 EMT/HIL/FPGA 方向，高影响研究通常需要把可解释模型、硬件实测、实时可实现性和跨工况泛化同时闭合。一个能给出“在给定 clock uncertainty set（时钟不确定集）下，状态误差超过阈值的概率或上界”的模型，可以直接服务于 HIL 可信度认证、采样时钟设计和控制器测试边界，而不只是解释单个异常波形。

**（c）可借鉴的相邻方法。** 把 PWM–HIL 相位差建模为 circle-valued phase process（圆周相位过程），把 edge quantization error 建模为 cyclostationary 或 stochastic hybrid process（随机混杂过程）；再用 harmonic transfer functions、phase-noise analysis 和 robust control 的工具，把输入误差的频谱包络传播到电流/电压状态。工程上可进一步设计 deliberate clock dithering（有意时钟抖动）或 phase-aware sampling scheduler，把尖锐低频线摊平到功率级易衰减的频带。

**（d）第一个能够证伪它的实验。** 在 FPGA 上用两个可编程独立时钟注入已知 jitter 与 drift，保留论文的 Boost 工况；用一部分时钟条件拟合模型，预测未见条件下的 error PSD、95% peak-to-peak envelope 和 dominant band。若模型不能显著优于本文固定 `N` baseline，或 deliberate dithering 在相同实时预算下不能稳定降低最坏误差，则研究假设被证伪。

**（e）与本文的实质区别。** 本文的问题是“固定周期 PWM 被固定周期 HIL 采样后，会出现哪些离散 aliasing frequencies”；候选工作的目标改为“没有稳定重复周期时，如何给出随机/最坏情况误差认证，并主动整形误差频谱”。前者依赖 LCM 和确定性线谱，后者不要求有限 `N`，输出的是可验证的误差分布、置信边界和实时 mitigation policy（缓解策略）。这不是给现有 pipeline 再加一个滤波模块，而是把研究目标从案例诊断提升为不确定时钟条件下的 HIL 可信度保证。
