# MPSoC-Based Dynamic Adjustable Time-Stepping Scheme With Switch Event Oversampling Technique for Real-Time HIL Simulation of Power Converters

作者：Jialin Zheng；Yangbin Zeng；Zhengming Zhao；Weicheng Liu；Han Xu；Haoyu Wang；Di Mou  
出处：IEEE Transactions on Transportation Electrification，Vol. 10，No. 2  
年份：2024  
DOI：10.1109/TTE.2023.3310509  
Zotero key：RTSQC3D8  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是单纯“把 HIL 仿真步长做得更小”，而是一个相互牵制的三角矛盾：高开关频率电力电子控制器要求仿真器准确捕获异步到来的 PWM 边沿；电路求解又必须在每个实时期限内完成；FPGA/SoC 的乘法器、片上存储与通信带宽却是有限的。典型高频 LLC、DAB 等变换器的开关频率范围被作者概括为 20–400 kHz，若沿用固定步长和一步一次采样，就往往需要纳秒级步长才能同时压低输入边沿误差和状态积分误差，代价是大量无开关事件时刻也要重复计算。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

作者将问题拆成两个不同时间尺度：采样必须足够密，以辨认开关事件；状态求解却只需在开关事件、二极管自然换流或输出交互等真正改变轨迹的时刻执行。论文据此提出 switch event oversampling（SEO，开关事件过采样）与 dynamic adjustable time-stepping（DAT，动态可调时间步长），并在一台 Zynq UltraScale+ MPSoC 上实现。论文直接声称，在所研究的 32 开关、最高 400 kHz 的四端口 MMAB 案例中，方案相对商业 HIL 仿真器可把最佳情形的相对误差降至约 \(1/42\)，同时把计算存储量降到约 \(1/10\)。这个数字是特定案例与不同硬件/求解器组合下的结果，不应外推成所有变换器上的普遍倍率。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E14]（PDF 物理页 14，Table VI 与 Section VI）

工程价值在于：如果“高频采样”和“高频求解”不再被强制绑定，HIL 平台就可能用有限资源覆盖更高开关频率、更大电路规模，并在 dead time、port blocking 等依赖二极管自然换流的工况下保留事件时序。这直接关系到控制器在低电压穿越、端口闭锁等异常工况中的测试可信度，而不只是稳态波形是否看起来相似。[pdf:E07]（PDF 物理页 7，Section III-C）[pdf:E09]（PDF 物理页 9，Section V-A）

## § 2 — 前人工作与不足

论文把既有路线归为三类。第一类是模型简化：开关电阻模型准确但会造成时变系统矩阵；预存矩阵或优化矩阵求逆减少在线生成，却消耗大量存储并保留串行矩阵操作；associated discrete circuit model 可保持矩阵恒定，但引入虚拟误差，且误差会随开关频率升高。第二类是算法加速：用开关或储能元件做 network tearing，或在求解器中插入延迟、利用预测量并行计算；这能缩短步长，却以更多硬件资源或数值稳定性为代价。第三类是 oversampling：插值、外推或重算状态会随事件数增加计算与响应时间；time averaging 能在一步内吸收多个事件，却会损失高频谐波。[pdf:E02]（PDF 物理页 2，Section I-A–I-C）

这些路线的共同缺口不是“完全没有采样精度”，而是仍把固定采样步与固定仿真步视为同一节拍。普通 oversampling 虽取得了额外边沿信息，却难以把 \(i-1\) 个额外采样点有效送入下一步求解，而且计算完成本身仍引入一步延迟；继续缩短固定步又会增加无意义计算点、压缩单步可用计算时间。作者还指出，固定步求解器难以在实时约束内通过迭代精确定位二极管自然换流。[pdf:E03]（PDF 物理页 3，Fig. 1 与 Section II-A）[pdf:E02]（PDF 物理页 2，Introduction 末段）

论文引用的最近邻思路包括 oversampling HIL、sub-cycle averaging、substep events、event-driven real-time simulation 与 discrete hybrid time-step algorithm；本卡只依据论文自身的相关工作叙述，未独立核读这些参考文献。因此，“SEO+DAT 是否首次以该组合出现”仍未由外部全文检索闭合，本卡不作独立 novelty 宣告。

## § 3 — 重建作者的思考路径

从论文之前已经存在的事实出发，可以重建出如下路径。首先，控制器与仿真器时钟不同步，PWM 边沿落在采样栅格之间是结构性现象；采样延迟会直接变成 duty-cycle 扰动与输出伪振荡。其次，提高 oversampling 倍率能缩小边沿量化误差，却没有回答“这么多采样点如何进入求解器”。再次，电力电子状态轨迹主要在拓扑切换和自然换流处改变动力学方程，因此固定频率求解对大部分无事件区间是在浪费实时预算。最后，MPSoC 同时拥有适合分支、队列和中断的 processor system（PS）以及适合规则矩阵运算的 programmable logic（PL），天然允许把事件逻辑与数值计算拆开。[pdf:E02]（PDF 物理页 2，Section I-B–I-C）[pdf:E08]（PDF 物理页 8，Section IV-B）

基于这些线索，一个研究者会先尝试把 oversampled PWM 压缩成“事件时间戳+切换状态”，而不是把每个采样值都送进求解；再让求解器的时间网格服从这个事件队列；最后把不可预知的二极管换流写成根查找问题，并把新找到的事件重新插回队列。对具有半周期对称性的调制，还可以利用前半周期重建参考波并预测后半周期边沿，从而把原本滞后一周期的信息变成当前周期可用的信息。这里的“思考路径”是基于论文证据的合理推断，不是作者逐字陈述。[pdf:E03]（PDF 物理页 3，Fig. 2）[pdf:E04]（PDF 物理页 4，Eq. (4)、Fig. 3 与 Section III 开头）

## § 4 — 核心 Intuition

SEO 的核心是把高频采样得到的大量 0/1 点压缩成少量“何时切换、切到什么状态”的事件，并在对称调制下用前半周期预测后半周期。DAT 的核心是让状态求解只追着这些事件和二极管零交越走：无事件时迈大步，有事件或精度不足时缩小步长、提高或降低积分阶数。这样，采样分辨率可以很小，而仿真步不必同样小；节省下来的实时预算再用于更准确的矩阵计算与自然换流定位。[pdf:E04]（PDF 物理页 4，Eq. (4) 与 Section II-B–II-C）[pdf:E05]（PDF 物理页 5，Fig. 5）

## § 5 — 具体方法与完整 Pipeline

以论文的四端口 modular multiactive bridge（MMAB）为例，完整 pipeline 如下。

1. **输入与同步。** 输入是物理控制器发出的各桥臂 PWM、已知或可恢复的载波/开关频率，以及电路输入源。对 symmetric modulation，SEO 从上升沿、下降沿或参考驱动信号恢复控制周期中点；前半周期 oversampling 得到已发生事件，结合载波频率和幅值重建参考波，预测后半周期事件；后半周期继续采样并校正预测。作者指出，这允许把离散步从控制周期的 \(1/20\)–\(1/100\) 扩到一个完整控制周期，同时后半周期预测误差仍限制在一个采样步内。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Section II-B）[pdf:E04]（PDF 物理页 4，Section II-B）

2. **非对称调制的退化路径。** 对 asymmetric modulation，无法利用半周期对称性，SEO 仍 oversample，但把一步内所有边沿压缩为
   \[
   s=\{e_1(t_1,\mathrm{state}_1),e_2(t_2,\mathrm{state}_2),\ldots,e_k(t_k,\mathrm{state}_k)\}.
   \]
   下一计算步按该序列安排子步。作者明确承认这一路径仍有一步延迟，并给出典型离散步 \(1\,\mu s\) 的文献性建议；因此它不是与对称调制路径等价的“零延迟”方案。[pdf:E04]（PDF 物理页 4，Eq. (4)、Fig. 3）

3. **开关分离建模。** 每个半桥被替换为包含两只二极管、受控电压/电流源和导通电阻的等效模型。门极状态只形成稀疏 switch matrix \(K_k\)，线性网络矩阵保持不变；这样避免每次拓扑变化都在线重建整个系统矩阵，也保留二极管行为。论文预存 \(K_k\) 及 \(Q_k=(I-D_{21}K_k)^{-1}\)，用较少存储换取少量在线矩阵组合。[pdf:E05]（PDF 物理页 5，Fig. 4、Eq. (6)–(15)）

4. **事件驱动的步长与阶数。** scheduler 比较最近开关事件间隔 \(\Delta t_s=t(e_k)-t(e_{k-1})\) 与最大步长 \(\Delta t_{\max}\)，选择最紧迫的时刻。每一步按 Taylor 展开递推各阶状态导数，依据各阶增量与截断误差需求选择积分阶数；小步通常不必用高阶，大步则用更高阶维持精度。若检测到二极管变量跨过导通/关断阈值，线性插值或 secant method 定位根，再把二极管事件插回队列并重新排步。[pdf:E05]（PDF 物理页 5，Fig. 5、Eq. (12)–(15)）[pdf:E06]（PDF 物理页 6，Eq. (16)–(20)、Fig. 6）

5. **MPSoC 映射。** 平台是 Zynq UltraScale+ XCZU5EV：PS 含四核 1.5 GHz Cortex-A53 与双核 600 MHz Cortex-R5，PL 提供 FPGA 逻辑；论文优先用具确定性实时能力的 R5。事件调度和二极管零交越检测属于分支密集任务，放在 PS；导数计算和数值积分属于矩阵密集任务，放在 PL。PS 以 C++ 实现，PL 经 HLS/VHDL 实现，PS–PL 通过 AXI/TCM 交互，外部控制器通过高速光纤接口连接。[pdf:E07]（PDF 物理页 7，Fig. 7 与 Section IV-A）[pdf:E08]（PDF 物理页 8，Fig. 8 与 Section IV-B–IV-C）

6. **FPGA 内核。** \(m\times n\) matrix-vector multiplication 被拆成 \(m\) 个并行 dot products，每个 \(n\)-维点积使用 \(n\) 个乘法器和 \(n-1\) 个加法器；不同 Taylor 阶次以 pipeline 交叠。论文使用 UNROLL、PIPELINE、ARRAY_PARTITION 以及 BRAM/URAM 等 HLS 手段在吞吐、存储密度与资源间折中，但未给出可直接复用的完整 HDL/HLS 源码、定点位宽、量化策略或综合约束文件，这些均属未报告。[pdf:E08]（PDF 物理页 8，Fig. 8）[pdf:E09]（PDF 物理页 9，Section IV-C）

7. **输出。** PL 产生各端口状态与观测量，经 DAC/高速链路反馈控制器。若 DAC 要求固定输出率，而 DAT 内部步长可变，论文建议在对称调制下把输出步设为开关周期；更高时间分辨率可在输出前插值或 resampling，但论文没有给出该插值链的误差验证。[pdf:E09]（PDF 物理页 9，Section IV-C）

研究案例由四个模块构成，每个模块含 A 型 H 桥、B 型 H 桥与高频变压器，共 32 个开关，模块通过 50 kHz 高频总线连接；Table VII 给出了 20、50、200、400 kHz 频率实验所用的漏感变化与端口额定值，Table VIII 给出了 50 kHz 功率原型的端口电压、总电感、变比和器件型号。[pdf:E09]（PDF 物理页 9，Fig. 9 与 Section V-A）[pdf:E15]（PDF 物理页 15，Table VII–VIII）

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从采样时延到 duty-cycle 误差

令 \(T_{\mathrm{sw}}\) 为控制周期、\(T_{\mathrm{on}}\) 为真实导通时间、\(D_{\mathrm{on}}\) 与 \(D_{\mathrm{off}}\) 为采样造成的开通和关断延迟，则论文 Eq. (1)–(3) 为
\[
D=\frac{T_{\mathrm{on}}}{T_{\mathrm{sw}}},\qquad
D_{\mathrm{HIL}}=\frac{T_{\mathrm{on}}+D_{\mathrm{off}}-D_{\mathrm{on}}}{T_{\mathrm{sw}}},
\]
\[
|D_{\mathrm{HIL}}-D|<\frac{T_{\mathrm{disc}}}{T_{\mathrm{sw}}},\qquad
|D_{\mathrm{HIL}}-D|<\frac{T_{\mathrm{disc}}}{iT_{\mathrm{sw}}}\ \text{（每步 oversample \(i\) 次）}.
\]
直觉是：边沿时间量化误差除以一个开关周期，就是 duty-cycle 误差上界；oversampling 只把量化栅格缩小 \(i\) 倍，却不会自动消除计算产生的一步延迟。[pdf:E03]（PDF 物理页 3，Eq. (1)–(3)、Fig. 1）

### 6.2 从拓扑切换到可预存矩阵

基础电路写成
\[
\dot x=Ax+Bu,\qquad y=Cx+Du. \tag{5}
\]
半桥等效源由门极状态 \(s_1,s_2\) 控制：
\[
v_{\mathrm{ac}+}=s_1v_{\mathrm{dc}},\quad v_{\mathrm{ac}-}=s_2v_{\mathrm{dc}},\quad
i_{\mathrm{dc}}=s_1i_{\mathrm{dc}+}+s_2i_{\mathrm{dc}-}, \tag{6}
\]
并压成 \(u_s=K_ky_s\)（Eq. (7)）。Eq. (8) 把线性网络与开关源分块；化简后的 Eq. (9)–(11) 是
\[
\dot x=A_0x+B_2u+B_1K_ky_s,
\]
\[
y=C_1x+D_{12}u+D_{11}K_ky_s,
\]
\[
y_s=C_2x+D_{22}u+D_{21}K_ky_s.
\]
最后一式是隐式代数环。把它直接消元得到
\[
y_s=Q_k(C_2x+D_{22}u),\qquad Q_k=(I-D_{21}K_k)^{-1}, \tag{13}
\]
进而形成每个事件区间的 \(A_k,B_k,C_k,D_k\)：
\[
\dot x=(A_0+B_1K_kQ_kC_2)x+(B_2+B_1K_kQ_kD_{22})u, \tag{14}
\]
\[
y=(C_1+D_{11}K_kQ_kC_2)x+(D_{12}+D_{11}K_kQ_kD_{22})u. \tag{15}
\]
因此在线变化量被收敛到离散的 \(K_k,Q_k\) 选择，而不是每步执行不定次数的 Newton iteration。论文 Eq. (8) 的完整块矩阵与维度定义、Eq. (12) 的事件间隔 \(\Delta t_s=t(e_k)-t(e_{k-1})\) 均见同页证据。[pdf:E05]（PDF 物理页 5，Eq. (5)–(15)）

### 6.3 可变阶 Taylor 积分

在一个事件区间内，系统矩阵不变，可把系统视作 LTI。论文用 \(p\) 阶 Taylor 展开：
\[
x_{k+1}=x_k+\sum_{i=1}^{p}\frac{x_k^{(i)}}{i!}(\Delta t_k)^i+
\frac{x_k^{(p+1)}}{(p+1)!}(\Delta t_k)^{p+1}, \tag{16}
\]
其中最后一项是截断余项 \(R_n\)。各阶导数递推为
\[
x_k^{(i)}=A_kx_k^{(i-1)}+B_ku_k^{(i-1)},\quad i\ge1, \tag{17}
\]
第 \(i\) 阶增量为
\[
\Delta x_{k,i}=\frac{x_k^{(i)}}{i!}(\Delta t_k)^i. \tag{18}
\]
工程含义是：scheduler 先给出候选 \(\Delta t_k\)，硬件流水计算各阶 \(\Delta x_{k,i}\)，再以增量大小评估所需阶数。论文没有给出全局误差界、统一误差阈值、阶数上下限或 stiff 系统上的稳定域；它只指出 Taylor 显式积分的稳定性类似 explicit Runge–Kutta，弱于 BDF、Adams–Moulton 等隐式方法。[pdf:E06]（PDF 物理页 6，Eq. (16)–(18)）[pdf:E07]（PDF 物理页 7，Section III-C）

### 6.4 二极管自然换流

二极管关断时监测电流，导通时监测电压，统一写成
\[
|y_d(t)-\delta_{\mathrm{bias}}|\le\varepsilon, \tag{19}
\]
其中关断检测 \(\delta_{\mathrm{bias}}=0\)，导通检测 \(\delta_{\mathrm{bias}}=V_f\)。其 \(q\) 阶 Taylor 近似为
\[
y_{d,k}=y_{d,k-1}+\sum_{i=1}^{q}\frac{y_{d,k-1}^{(i)}}{i!}(\Delta t_k)^i+
\frac{y_{d,k-1}^{(q+1)}}{(q+1)!}(\Delta t_k)^{q+1}. \tag{20}
\]
大规模系统可用一次线性插值，精度要求更高的小系统可用 secant method；找到根后改变二极管状态、生成新事件并重排时间步。论文图示中 secant 定位用了两次迭代，但没有证明所有工况两次必然收敛。[pdf:E06]（PDF 物理页 6，Eq. (19)–(20)、Fig. 6）

附录用一个全桥开关状态把上述 \(A_k,B_k\) 具体化为含 \(L_1,C_1,R,R_{\mathrm{on}}\) 的二阶状态方程（Eq. (21)），证明符号分块能落到实际电路；但附录只列一个开关状态，并未给出 32 开关 MMAB 的全部矩阵库。[pdf:E15]（PDF 物理页 15，Fig. 16 与 Eq. (21)）

## § 7 — 实验设计与结论

**问题 1：DAT 的模型与积分是否能复现高精度离线参考？ → 实验：** 在四端口 MMAB 上模拟 0.6 s 低电压穿越，0.2 s 时电网电压降到 0.65 p.u.，0.3 s 恢复；商业离线软件的 Runge–Kutta(4,5) 结果作 reference。**答案：** Fig. 10 中四端口电压和高频变压器电流高度重合；Table I 报告 DAT 用 0.6 s 完成 0.6 s 场景，商业软件用 23.5 s，计算点分别为 281657 与 335120，四个列出的相对误差为 \(5.24\times10^{-6}\)、\(3.47\times10^{-7}\)、\(4.56\times10^{-6}\)、\(1.64\times10^{-5}\)。这里的“实时”是该特定存盘实验达到 1:1，不代表任意模型规模都满足期限。[pdf:E09]（PDF 物理页 9，Section V-B）[pdf:E10]（PDF 物理页 10，Fig. 10、Table I）

**问题 2：DAT 能否比固定步 EMTP 更准确处理二极管自然换流？ → 实验：** 四端口直流母线保持额定值，B 型 H 桥 phase-shift ratios 设为 0、0.1、0.15、0.2，0.01 s 时 Port 3 blocking；比较 DAT、带二极管的 100 ns 固定步 EMTP、无二极管 EMTP与 reference。**答案：** 无二极管模型在 blocking 后明显失真；带二极管 EMTP仍错过换流时刻；DAT 在 Fig. 11(b) 的窗口内使用 5 个计算点，而固定步方案使用 40 个点，并更贴近 reference。该结论支持“事件定位比盲目固定小步更有效”，但没有给出该次事件的独立时间戳真值和最大定位误差。[pdf:E10]（PDF 物理页 10，Section V-B）[pdf:E11]（PDF 物理页 11，Fig. 11）

**问题 3：PS/PL 任务分配是否真的减负？ → 实验：** 用 PS-only、PS/PL collaboration、PL-only 三种分配执行同一场景。**答案：** Table II 中总时间分别为 58.7、13.9、41.3 \(\mu s\)；PS/PL 相比 PL-only 把总时间降低 66.3%，LUT 与 DSP 使用分别降低 79.8% 与 67.3%，相比 PS-only 把 PS time-slot utilization 从 100% 降到 45.59%。这些是综合后的资源/时序数据，但论文未报告多次运行方差。[pdf:E11]（PDF 物理页 11，Table II）

**问题 4：通信是否会吞掉计算加速？ → 实验：** 用 AXI timer 逐段测 RPU、PL、TCM 数据路径。**答案：** 计算任务合计 335 ns，而 PS–PL 通信合计 874 ns；作者明确指出在 \(>100\) kHz 的超高开关频率应用中，通信已成为瓶颈，会压缩可用于模型规模或更高精度的预算。这里是论文自己承认的硬边界，而非本卡推测。[pdf:E11]（PDF 物理页 11，Table III 与正文）

**问题 5：DAT 相对固定步 EMTP 节省多少 FPGA 资源？ → 实验：** 在相同 MPSoC 上比较 DAT、带/不带二极管的 EMTP。**答案：** DAT 使用 319 DSP、15444 LUT、1716.0 Kb BRAM，带二极管 EMTP 使用 771 DSP、44928 LUT、13237.9 Kb BRAM；DAT 的优势主要来自把事件逻辑卸载到 PS、只在事件处计算以及较小矩阵库存。不同硬件部署比较中，MPSoC PS/PL、MPSoC PL-only、Virtex-7 分别使用 319、977、1494 个 DSP；由于芯片容量和结构不同，百分比不能当作纯算法对比。[pdf:E12]（PDF 物理页 12，Table IV–V）

**问题 6：相对商业 HIL，SEO 在频率升高时是否更稳？ → 实验：** 同一物理控制器以 open-loop 驱动两个实时仿真器，在 20、50、200、400 kHz 扫频；DAT 的事件时间分辨率为 5 ns，商业仿真器一步采样为 200 ns。对称调制下，400 kHz 的 DAT 仿真步为 2.5 \(\mu s\)，其中计算 1.35 \(\mu s\)、空闲 1.15 \(\mu s\)。**答案：** 20 kHz 两者接近 reference；50 kHz 时 DAT 的 \(v_{\mathrm{HF}}\)、\(i_{\mathrm{HF2}}\) 相对误差为 \(2.96\times10^{-3}\)、\(3.87\times10^{-3}\)，商业方案为 \(2.45\times10^{-2}\)、\(3.37\times10^{-2}\)；200 kHz 商业方案出现明显振荡；400 kHz 商业方案严重失真，Table VI 给出的 DAT/商业误差分别为 \(9.83\times10^{-3}/3.42\times10^{-1}\) 和 \(1.34\times10^{-2}/5.69\times10^{-1}\)，对应商业误差是 DAT 的 34.8 倍与 42.4 倍。[pdf:E12]（PDF 物理页 12，Section V-D）[pdf:E13]（PDF 物理页 13，Fig. 12–14）[pdf:E14]（PDF 物理页 14，Table VI）

**问题 7：仿真波形能否接近真实功率原型？ → 实验：** 搭建四端口 MMAB 原型，采用 single-phase-shift 与经典 PI 控制，把同一控制器接入 DAT 平台，对比高频电压/电流。**答案：** Fig. 15 的主要波形形状和幅值关系得到复现；实验波形尖峰未复现，作者解释为实时模型忽略了高频母排 stray capacitance 等寄生参数。论文没有给出这组功率实验的误差指标、重复次数或不确定度，因此它支持定性 fidelity，不支持新的定量精度倍率。[pdf:E13]（PDF 物理页 13，Section V-E 与 Fig. 14）[pdf:E14]（PDF 物理页 14，Fig. 15）[pdf:E15]（PDF 物理页 15，Table VIII）

不得外推的范围包括：非对称、变频、随机或 pulse-skipping 调制下的零延迟性能；含大量寄生参数的 stiff 网络；多核 MPSoC 扩展；闭环控制稳定性；更大端口数或不同拓扑上的资源增长规律。论文对这些项未报告完整验证。

## § 8 — Take-aways

**5 句话：**  
1. 论文最重要的动作是把采样时间栅格与数值求解时间栅格分离。  
2. SEO 把 oversampled PWM 压缩成事件序列，并在对称调制下预测后半周期，从而减少一步延迟。  
3. DAT 用事件队列、可变阶 Taylor 积分和二极管根查找，只在动力学真正变化的时刻计算。  
4. MPSoC 的 PS 处理事件逻辑，PL 处理矩阵计算，使 32 开关 MMAB 在最高 400 kHz 案例中保持实时。  
5. 最强结果是特定平台与案例上的 5 ns 事件分辨率、约 \(1/42\) 最佳相对误差和约 \(1/10\) 存储，但它依赖调制对称性、已知控制信息与有限模型刚性。[pdf:E14]（PDF 物理页 14，Table VI 与 Conclusion）

**3 句话：**  
1. 高频 HIL 不必每个采样点都完整求解，关键是把采样点转换成可调度事件。  
2. 事件驱动步长和可变阶积分把算力集中到开关与自然换流处，PS/PL 分工再把逻辑与矩阵运算映射到合适硬件。  
3. 论文在对称调制 MMAB 上证据很强，但非对称调制、stiff 寄生网络和通信瓶颈仍决定其可推广边界。[pdf:E07]（PDF 物理页 7，Section III-C）[pdf:E11]（PDF 物理页 11，Table III）

**1 句话：**  
这项工作的本质是用“高频看、按事件算”替代“高频看、每次都算”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**控制调制具有足够稳定且已知的周期结构，使当前控制周期后半段的全部开关事件能由前半段采样和调制信息可靠预测，并能与仿真器周期同步。** 这是消除一步延迟、把仿真步扩到一个开关周期、进而释放大量计算预算的必要条件；一旦预测信息在实时期限前不可得，SEO 只能退化成论文的 asymmetric 路径，重新出现一步延迟，DAT 的大步长也必须缩小。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Section II-B）[pdf:E04]（PDF 物理页 4，Section II-B–II-C）

它在实际中可能因 variable-frequency modulation、pulse skipping、burst mode、DPWM 区间切换、保护逻辑异步插脉冲/封锁、载波相位复位、控制器时钟抖动或通信丢边沿而失效。论文给出的正面证据是 symmetric modulation 的同步—预测—校正机制，以及 single-phase-shift/open-loop MMAB 在 20–400 kHz 的实验；负面证据则是作者明确承认 asymmetric modulation 仍有一步延迟，并要求尽可能小的步长。论文没有报告预测失配率、校正到达期限、丢边沿恢复策略，也没有在随机或变频调制下测量闭环行为。[pdf:E12]（PDF 物理页 12，Section V-D）[pdf:E14]（PDF 物理页 14，Future Work 前的限制说明）

因此，“DAT 可变步有效”与“SEO 能提前提供正确事件”不能混为一项证据：前者可在离线已知事件上成立，后者决定实时 HIL 能否兑现相同结果。这是基于证据的机制判断。

## § 10 — 最小复现实验

一周内最值得复现的是“事件时间戳是否比固定小步更能决定高频 HIL 误差”，不必先重做完整 MPSoC。

1. **数据与对象：** 按 Fig. 9 和 Table VII 搭一个简化的单模块双有源桥或四端口 MMAB 软件模型；先用 50、200、400 kHz 三档，参数直接采用论文报告值。生成 deterministic symmetric phase-shift PWM，同时保存无量化的真实边沿时间作为 ground truth。[pdf:E09]（PDF 物理页 9，Fig. 9）[pdf:E15]（PDF 物理页 15，Table VII）
2. **实现：** 做三个 solver：高精度离线 reference；200 ns 一步采样+100 ns 固定步 EMTP；5 ns 边沿量化+事件队列+可变阶 Taylor DAT。二极管零交越先用 secant method，并记录每个定位误差和迭代次数。不要先实现 HLS；CPU 版本足以验证算法 claim。
3. **测量：** 对 \(v_{\mathrm{HF}}\)、\(i_{\mathrm{HF}}\) 使用论文的 \(L_2\) 相对误差；同时测 edge timestamp error、漏事件数、每周期状态更新次数、最大单步计算预算。另做一次 Port blocking，比较自然换流时刻。
4. **支持标准：** 随频率从 50 升到 400 kHz，DAT 无漏事件，事件时刻误差不超过 5 ns 量化栅格，波形相对误差显著低于固定步，并以远少于固定步的状态更新次数保持结果。
5. **反驳标准：** DAT 的优势在使用相同真实边沿时消失；或误差主要来自模型/积分而非采样；或二极管事件在容差内仍系统性提前/滞后；或计算点虽少但每事件计算时间超过实时预算。

这只能复现算法机制，不能复现论文的 XCZU5EV 时序、资源占用或商业 HIL 对比；后者需要作者未提供的 HDL/HLS、位宽与商业配置，当前属于未报告材料。

## § 11 — 最强反例设计

最强反例不是再换一个更大电路，而是保持同一 MMAB 与平均功率点不变，只破坏“后半周期可预测”这一核心条件。让控制器在每个周期随机选择 symmetric phase shift、asymmetric edge placement、pulse skipping 或一次异步保护封锁，并叠加受控载波相位复位；构造两组平均 duty 和平均功率相同、但后半周期边沿分布不同的输入。仿真器仍只能看到前半周期 oversampling 和论文假定的调制信息。

攻击指标是：预测事件与真实边沿的最大/均方时间误差、漏事件率、correction 到达时是否已错过该事件的实时求解期限、\(v_{\mathrm{HF}}\)/\(i_{\mathrm{HF}}\) 误差、闭环控制器是否因一步旧反馈产生次谐波或保护误触发。若 SEO 在异步边沿发生后才能校正，而 DAT 已用错误拓扑跨过该时刻，那么“5 ns 采样分辨率”并不等于“5 ns 因果可用事件分辨率”；此时论文相对商业固定步的优势可能来自已知对称调制，而不是一个普适 oversampling 机制。这一替代解释能直接挑战核心 claim。[pdf:E04]（PDF 物理页 4，asymmetric modulation 的一步延迟）[pdf:E13]（PDF 物理页 13，Fig. 12 的 symmetric/open-loop 频率比较）

第二层压力是在上述随机事件下加入论文功率实验中被忽略的 stray capacitance，使系统更 stiff；显式 Taylor 的稳定约束可能迫使 DAT 缩步或升阶，PS–PL 通信又已占 874 ns。若此时事件频率与通信频率同步上升，节省的计算点可能被每事件通信和隐式刚性需求抵消。[pdf:E07]（PDF 物理页 7，stiff-system 讨论）[pdf:E11]（PDF 物理页 11，Table III）[pdf:E14]（PDF 物理页 14，Fig. 15 的寄生参数差异）

## § 12 — Follow-up Research Idea

在电力电子实时仿真领域，高影响工作通常需要同时满足：数值方法有可解释的误差/稳定性边界；硬件映射满足可复核的 worst-case latency；在真实控制器、异常工况和功率原型上展示工程价值。仅把同一 DAT 模块换到另一种变换器，通常只是增量应用。

**候选方向：面向未知调制的“因果事件契约 HIL”。** 研究目标从“利用已知对称性预测 PWM”改成“无论调制是否对称，控制器都以带 deadline 和置信边界的事件时间戳契约向仿真器公布未来/紧急拓扑变化；仿真器对不可预告事件提供可证明的安全退化”。这不是再加一个 predictor，而是重新定义 controller–simulator interface：已计划 PWM 边沿、异步保护事件、自然换流估计和撤销/更正都成为有时限语义的 hybrid events。

- **(a) 未满足需求：** EV traction、wide-bandgap converter 与保护测试会出现变频、burst、pulse skipping 和异步封锁；论文的半周期预测在这些工况下失去零延迟，而固定小步又代价过高。[pdf:E04]（PDF 物理页 4，asymmetric modulation 限制）
- **(b) 研究价值：** 若能给出“事件最晚何时必须公布—solver 最晚何时完成—误差如何随迟到事件增长”的组合保证，就能把当前只在特定调制下成立的性能，提升为可验证的实时系统契约，并直接服务 controller HIL 的保护认证。
- **(c) 相邻方法：** 可借鉴 real-time scheduling 的 deadline analysis、time-sensitive networking 的时间戳与有界延迟、hybrid systems 的 event localization，以及 speculative execution 的验证/撤销思想；但实时 HIL 不允许无限 rollback，必须设计有限窗口的安全 fallback。
- **(d) 首个证伪实验：** 在同一 400 kHz MMAB 上随机混合 symmetric、asymmetric、pulse-skipping 与异步 blocking，注入可控事件通告抖动和丢包。若在既定 hardware budget 下，契约方案不能同时把漏事件率降为零、维持实时 deadline，并把最坏波形误差显著压低于“普通 oversampling + 最小固定步”，该方向即被首轮否证。
- **(e) 实质区别：** 本文用调制对称性换取未来事件；候选方向要求控制器—仿真器显式交换有期限的事件语义，并把未知/迟到事件纳入可证明退化。它改变的是接口与可验证目标，而不只是提高采样倍率或增加一个预测模型。

该方向只依据本论文及其参考文献线索形成，尚未完成紧密相关全文检索，因此明确标为候选想法，不声称 novelty。
