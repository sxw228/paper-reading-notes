# Determination of Optimal Shift Frequency for Shifted Frequency-Based Simulation

作者：Shilin Gao、Ying Chen、Yankan Song、Yue Xia、Zhendong Tan  
出处：IEEE Transactions on Power Systems, Vol. 36, No. 5, pp. 4824–4827  
年份：2021  
DOI：10.1109/TPWRS.2021.3076829  
Zotero key：G4HJD7JE  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇 letter 研究一个很具体的数值问题：在 shifted frequency（SF）仿真中，频谱究竟应该平移多少，才能让离散仿真误差最小。既有 SF 仿真通常直接把 shift frequency 设成电网基频 50 Hz 或 60 Hz；这对单一基频附近的窄带波形直观有效，但当信号同时含有谐波、次同步振荡或其他多个频率分量时，基频不再必然是最优选择。作者把要寻找的值称为 optimal shift frequency（OSF），并把问题从“按习惯选 50/60 Hz”改写成“最小化 SF 离散结果相对精确响应的 2-norm error”。这是论文原文明确提出的研究问题和贡献边界。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

工程上的重要性来自 EMT 仿真的时间尺度矛盾。传统 electromagnetic transients program（EMTP）为了捕捉交流载波及更快动态，常需采用几十微秒量级的小步长；SF 方法先把交流波形的频谱下移、消去高频载波，使稳态和低频或次同步振荡在新坐标系中变化得更慢，因此可以采用更大的步长，节省计算时间。[pdf:E01]（PDF 物理页 1，Section I）如果 shift frequency 选错，坐标变换虽然仍能运行，但离散化所见的剩余频率偏移会变大，精度收益会被侵蚀。因此，OSF 的价值不是改变连续系统的物理模型，而是在给定 SF 表示和离散方法下，把有限步长造成的误差压到最低。

这篇论文的直接价值是给出一个可计算的 OSF，而不是经验调参：单频输入时 OSF 就是该输入频率；多频窄带输入时，OSF 是一个加权五次方平衡方程的唯一解；宽带输入则最小化更完整的误差式。作者还研究了 OSF 与 time-step size 的关系，并用一个并网 PMSG 风电场算例验证理论预测。[pdf:E04]（PDF 物理页 2，Eq. (19)–(23)）[pdf:E05]（PDF 物理页 3，Eq. (24)–(28)）[pdf:E07]（PDF 物理页 4，Fig. 2–3 与 Section IV-B）

## § 2 — 前人工作与不足

论文给出的既有路线可以分成三层。第一层是传统 EMTP：直接在原始交流波形上做时域积分，能保留快速电磁暂态，但为解析载波通常需要几十微秒级步长。第二层是 Marti、Zhang 等工作的 shifted frequency analysis：把频谱按基频平移并去掉交流载波，使稳态、低频和次同步动态可以在更大步长下计算。第三层是 Gao 与 Strunz 的 frequency-adaptive transient simulation，以及 Ye、Xia 等人的多尺度线路和电机模型；它们进一步把 SF 表示用于不同元件和暂态尺度。[pdf:E09]（PDF 物理页 4，References [2]–[7]）论文在引言中以文献 [2]–[7] 概括了这些工作，并明确指出现有 SF 仿真实现都使用 50 Hz 或 60 Hz 作为 shift frequency。[pdf:E01]（PDF 物理页 1，Section I）

不足不在于既有方法“没有频移”，而在于它们没有把频移量本身当成误差优化变量。对单频输入，频移到该频率可把解析包络变为直流量；但对含多个分量的信号，不可能用一个 \(f_s\) 同时消去所有剩余频率。若仍机械地平移 50/60 Hz，某些频率分量的离散误差会被放大。论文进一步指出，既有文献对 broadband 输入会把 \(f_s\) 设为 0，但这也不是由误差最小化得到的 OSF。[pdf:E05]（PDF 物理页 3，Section III-C 与 Eq. (27)–(28)）

论文弥补的是这个误差分析缺口：它从 trapezoidal discretization 出发，写出 SF 仿真结果与精确解析响应的差，再把各频率分量的误差聚合为 2-norm error，最终求使误差最小的 \(f_s\)。它没有解决、也没有报告下列相邻问题：非平稳频谱下的在线 OSF 跟踪、开关事件处的误差、非线性系统的严格误差界、不同离散方法的统一 OSF、实时实现成本，以及 FPGA 映射。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，不是作者逐字陈述。

第一步，研究者已经知道 SF 的计算收益来自“让离散积分器看到更慢的包络”：原始交流波形按 \(f_s\) 平移后，某个频率 \(f\) 在新坐标中的剩余频率是 \(f-f_s\)。若只看一个频率分量，最自然的选择就是 \(f_s=f\)，因为此时该分量在 SF 坐标中成为常量。[pdf:E02]（PDF 物理页 1，Eq. (1)–(4)）

第二步，真实电力系统波形常包含基频、谐波和振荡边带。一个固定 \(f_s\) 不可能同时让所有 \(f_i-f_s\) 为零，于是“频移到基频”不再是数学上自明的最优解。问题需要一个聚合误差指标，才能决定不同频率、幅值和离散误差之间如何权衡。

第三步，先选择最可分析的基准对象：一阶 LTI 系统 \(\mathrm{d}o/\mathrm{d}t=K_Iu(t)\)，令输入是多个稳定正弦分量。线性叠加允许先推导单频精确响应和 SF trapezoidal 响应之差，再把各分量的平方 2-norm error 相加。[pdf:E03]（PDF 物理页 2，Eq. (5)–(14)）

第四步，对窄带条件做 Taylor-Maclaurin 近似，得到误差对频率偏差的主导关系 \((f_i-f_s)^6\)。这样，求 OSF 变成一个一维凸优化问题；一阶导数为零给出五次方平衡式，二阶导数为正保证唯一极小值。[pdf:E04]（PDF 物理页 2，Eq. (15)–(23)）

第五步，研究者会追问：若增大或改变 time-step size，最优频移是否也要重新求。作者利用长仿真时 \(T_s\gg\Delta t\) 的近似，把每个频率分量的权重化为 \(c_i\approx A_i^2n/2\)；所有 \(c_i\) 随步长获得相同倍率，因此求根位置不变，而误差绝对值仍随步长变化。[pdf:E05]（PDF 物理页 3，Eq. (25)–(26)）

最后，把公式放到含次同步振荡的并网 PMSG 风电场中检验：一边扫描 shift frequency 得到经验误差最小点，一边用频率分量和解析方程独立计算 OSF；两者都得到 42.1 Hz。[pdf:E07]（PDF 物理页 4，Fig. 3 与 Section IV-B）

## § 4 — 核心 Intuition

SF 仿真的误差由每个频率分量在平移后留下的“残余转速”驱动；残余频率越大，trapezoidal integration 对该分量的相位和幅值误差越大。单频时把它精确移到零频就是最优，多频时则要找一个加权中心，使所有分量的六次方误差总和最小。这个中心通常不是 50/60 Hz，而是由频率、幅值、观察时长和所用离散方法共同决定的误差最小点。[pdf:E04]（PDF 物理页 2，Eq. (19)–(23)）

## § 5 — 具体方法与完整 Pipeline

论文的方法可以按以下 pipeline 理解。

1. **输入与 SF 表示。** 对真实信号 \(x(t)\) 构造 analytic signal \(x_s(t)=x(t)+j x_H(t)\)，其中 \(x_H\) 是 Hilbert transform；再乘以 \(e^{-j\omega_st}\) 得到 analytic envelope \(x_e(t)\)，\(\omega_s=2\pi f_s\)。连续动态 \(\dot{x}=F(x,t)\) 在 SF 域变成 \(\dot{x}_e=F(x_e,t)-j\omega_sx_e\)。[pdf:E02]（PDF 物理页 1，Eq. (1)–(3)）
2. **时间离散。** 论文采用 trapezoidal method，把上述 SF 动态按步长 \(\Delta t\) 离散；再乘回 \(e^{j\omega_st}\) 可得到原 analytic-signal 坐标下的离散更新式。方法中的 OSF 与这一离散规则绑定，不是与积分器无关的物理常数。[pdf:E02]（PDF 物理页 1，Eq. (4)）[pdf:E03]（PDF 物理页 2，Eq. (5)）
3. **建立可解析误差模型。** 对 LTI 积分环节 \(\dot{o}=K_Iu\) 和单频输入 \(u(t)=A\cos(2\pi ft)\)，分别写出精确响应与 SF trapezoidal 响应，形成瞬时误差和平方 2-norm error。[pdf:E03]（PDF 物理页 2，Eq. (6)–(14)）
4. **窄带 OSF。** 在 \(\pi|f-f_s|\Delta t\ll1\) 且 \(|f-f_s|<f\) 的条件下，用 Taylor-Maclaurin expansion 得到简化误差。单频时 \(f_s=f\)；多频时将每个频率分量的误差相加，求 \(\partial\varepsilon_{\mathrm{sqn}}/\partial f_s=0\)。双频有闭式解，多频用 Newton's method 求唯一根。[pdf:E04]（PDF 物理页 2，Eq. (16)–(23)）[pdf:E05]（PDF 物理页 3，Eq. (24)）
5. **宽带 OSF。** 不再使用窄带简化后的六次方误差，而是保留 Eq. (18) 的分母项，对多分量完整误差式 Eq. (27) 直接做一维最小化 Eq. (28)。[pdf:E05]（PDF 物理页 3，Section III-C）
6. **输出与使用。** 输出是一个 shift frequency \(f_s^\*\)。把它代入同一 SF-based simulator 后，模型结构和时间步进不变，只改变频谱平移中心；理论目标是使指定仿真区间内的 2-norm error 最小。

用论文算例串起来看：先从线路电感电压识别出 18.4、50 和 81.6 Hz 三个频率分量以及 3.2、23.4 和 17.5 A 的对应幅值，再把它们代入 Eq. (23) 求根，得到 \(f_s^\*=42.1\) Hz；随后在 PMSG 风电场 SF 仿真中使用约 42 Hz 的 shift frequency，线路电流比 \(f_s=0,18,50,82\) Hz 等选择更接近 reference。[pdf:E07]（PDF 物理页 4，Fig. 3、Section IV-B）[pdf:E08]（PDF 物理页 4，Fig. 4）

对 EMT + FPGA 实现所需的其他层面，论文的报告边界很窄：开关或事件处理策略未报告；多速率调度未报告；计算依赖图、并行分解和通信方式未报告；浮点或定点数值表示未报告；FPGA 数据通路、资源占用、时序收敛、片上存储和实际执行平台均未报告。论文只测试了若干固定 time-step size，并没有给出硬实时步长或 wall-clock speedup。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有明确的形式化推导。先从坐标变换看其物理意义：

\[
x_e(t)=x_s(t)e^{-j\omega_st},\qquad \omega_s=2\pi f_s .
\]

乘上 \(e^{-j\omega_st}\) 相当于让观察坐标系以 \(f_s\) 旋转，因此原来位于 \(f\) 的分量在新坐标中只剩 \(f-f_s\)。对连续动态 \(\dot{x}=F(x,t)\) 求导时会多出 \(-j\omega_sx_e\)，再用 trapezoidal method 离散。[pdf:E02]（PDF 物理页 1，Eq. (1)–(4)）

对单频输入，论文把 SF 离散结果与精确响应相减，得到平方 2-norm error。施加 \(\pi|f-f_s|\Delta t\ll1\) 和 \(|f-f_s|<f\) 后，主导项化为

\[
\varepsilon_{\mathrm{sqn}}
=cK_I^2\frac{\pi^2\Delta t^4}{36}\frac{(f-f_s)^6}{f^4}.
\]

这里 \(c\) 汇总了幅值、采样时刻和仿真时长的贡献；\(K_I\) 是 LTI 积分环节增益。式中 \((f-f_s)^6\) 表明误差关于 \(f_s=f\) 对称且在那里为零，\(\Delta t^4\) 则说明减小步长会快速降低该近似下的误差。[pdf:E04]（PDF 物理页 2，Eq. (15)–(19)）

对 \(m\) 个窄带分量，平方 2-norm error 为

\[
\varepsilon_{\mathrm{sqn}}
=K_I^2\frac{\pi^2\Delta t^4}{36}
\sum_{i=1}^{m}c_i\frac{(f_i-f_s)^6}{f_i^4},
\]

其中 \(c_i>0\) 包含第 \(i\) 个分量的幅值和时间采样权重。对 \(f_s\) 求导并令其为零，可得

\[
\sum_{i=1}^{m}c_i\frac{(f_i-f_s)^5}{f_i^4}=0.
\]

二阶导数是各项 \((f_i-f_s)^4\) 的正加权和，因此误差函数在非退化情形下严格凸，OSF 是 \([f_1,f_m]\) 内唯一根。双频时可写成五次根加权的闭式式子；更多频率分量没有显式解，论文建议 Newton's method。[pdf:E04]（PDF 物理页 2，Eq. (20)–(23)）[pdf:E05]（PDF 物理页 3，Eq. (24)–(25)）

步长不影响 OSF 的结论依赖一个进一步近似。论文令 \(n=T_s/\Delta t\)，在 \(T_s\gg\Delta t\) 时得到

\[
c_i\approx A_i^2n/2.
\]

改变 \(\Delta t\) 会让所有 \(c_i\) 按相同比例变化，所以它们在求根方程中的公共比例抵消，根的位置不变；但误差值本身仍含 \(\Delta t^4\)，并不是说步长不影响精度。[pdf:E05]（PDF 物理页 3，Eq. (25)–(26)）

对 broadband 输入，论文保留更完整的非线性分母，以 Eq. (27) 定义多频率误差并直接求 \(\min_{f_s}\varepsilon_{\mathrm{sqn}}\)。因此，窄带五次方方程不应无条件外推到 \(\pi|f_i-f_s|\Delta t\) 不再很小的情形。[pdf:E05]（PDF 物理页 3，Eq. (27)–(28)）

## § 7 — 实验设计与结论

**问题一：理论误差曲线是否真的存在可预测的 OSF？**  
实验使用并网 PMSG 风电场。Fig. 1 展示三组风机与变流器支路经变压器、线路汇集到电网；Table I 给出 DC 电容 90000 μF、滤波电阻 0.02 Ω、滤波电感 0.3 mH、converter rated DC voltage 1.1 kV、grid-side converter rated AC voltage 0.62 kV 及控制器 PI 参数。外部网络采用 0.62 kV/35 kV 变压器、0.066 p.u. leakage reactance，线路电阻和电感分别为 1.0 Ω 与 0.02 H。[pdf:E06]（PDF 物理页 3，Fig. 1、Table I 与 Section IV-A）工况在 50 Hz 系统上产生次同步振荡；Fig. 2 给出线路 1-2 的 A 相电压和电流波形。[pdf:E07]（PDF 物理页 4，Fig. 2）

验证方式是用 0.2 ms 步长运行不同 shift frequency 的 SF 仿真，并与 1 μs 小步长 EMTP reference 比较线路 1-2 的 A 相电流 2-norm error。Fig. 3 的误差曲线在 42.1 Hz 处达到最低点；独立地，把 18.4、50、81.6 Hz 和 3.2、23.4、17.5 A 代入 Eq. (23)，也得到 42.1 Hz。两条路径一致，支持“误差模型能定位 OSF”这一 claim。[pdf:E07]（PDF 物理页 4，Fig. 3 与 Section IV-B）论文没有用表格报告最低误差的精确数值，因此不应从曲线估读并声称一个额外精确值。

**问题二：选用 OSF 后，时域结果是否更接近 reference？**  
Fig. 4 比较了 reference 与 \(f_s=0,18,42,50,82\) Hz 的 SF 仿真线路电流。放大图显示 42 Hz 曲线最接近 reference，支持“OSF 改善该工况精度”的结论。[pdf:E08]（PDF 物理页 4，Fig. 4）这项结果只验证了一个网络、一个观测量和一个振荡工况，不能外推成所有 EMT 模型都获得相同比例的误差下降。

**问题三：OSF 是否随 time-step size 改变？**  
论文用 0.02、0.05、0.1、0.2 和 0.4 ms 五个步长重复测试，报告 OSF 保持不变，与 Section III-B2 的推导一致。[pdf:E07]（PDF 物理页 4，Section IV-C 开头）[pdf:E08]（PDF 物理页 4，Section IV-C 结尾）这里被验证的是“最优点位置不变”，不是“不同步长的误差相同”。

实验没有报告仿真软件版本、CPU/GPU/FPGA 平台、运行时间、speedup、内存或逻辑资源、实时 deadline、固定点误差、开关事件处理以及多次随机试验。控制系统细节还被指向参考文献 [10]，没有在本 letter 内完整展开。[pdf:E06]（PDF 物理页 3，Section IV-A）因此，本论文足以支持 OSF 的数值准确性 claim，但不足以支持计算加速、硬实时或 FPGA 可实现性 claim。

## § 8 — Take-aways

**5 句话版：**  
1. SF 仿真不应默认把 50/60 Hz 当成所有多频信号的最佳 shift frequency。  
2. 对 trapezoidal method 和窄带稳定频率分量，平方 2-norm error 的主导项按 \((f_i-f_s)^6\) 增长。  
3. 多频 OSF 是一个加权五次方平衡方程的唯一根，双频可闭式计算，多频可用 Newton's method。  
4. 在 \(T_s\gg\Delta t\) 等近似成立时，改变 time-step size 会改变误差大小，但不改变 OSF 的位置。  
5. 并网 PMSG 风电场算例中，扫描误差和解析计算都给出 42.1 Hz，且约 42 Hz 的时域电流最接近 reference。[pdf:E05]（PDF 物理页 3，Eq. (24)–(26)）[pdf:E07]（PDF 物理页 4，Fig. 3 与 Section IV-B）

**3 句话版：**  
1. 这篇论文把 shift frequency 从经验常数变成了离散误差的优化变量。  
2. 核心结果是用频率和幅值权重求得 OSF，并说明其在特定近似下与步长无关。  
3. 证据来自完整推导和一个 PMSG 风电场算例，但对非平稳、强非线性、开关事件及硬件实时实现仍未闭合。

**1 句话版：**  
在多频 SF 仿真中，应把频移中心选为离散 2-norm error 的最小点，而不是无条件选电网基频。

## § 9 — 最脆弱的假设

最脆弱的假设是：**实际待仿真波形在所考察时间窗内可以被视为若干频率和幅值稳定的正弦分量，而且从一阶 LTI 系统与 trapezoidal discretization 推出的误差排序，仍能代表非线性电力电子网络的误差排序。**

这是核心假设，因为 OSF 方程中的 \(f_i\) 和 \(c_i\) 被当成固定量；如果频率、幅值或网络工作点随事件快速变化，那么一个全局 \(f_s^\*\) 可能只最小化整段平均 2-norm error，却在故障、控制饱和、变流器限幅或频率穿越期间产生很大的局部误差。论文的理论模型明确从 stationary input 的 LTI superposition 出发。[pdf:E03]（PDF 物理页 2，Section II-B 与 Eq. (6)–(14)）它也明确承认结论基于 trapezoidal method，换用 Euler 等离散方法时，误差表达式和 OSF 都会改变。[pdf:E05]（PDF 物理页 3，Section III-B2）

论文为该假设提供的证据是：在一个发生次同步振荡的 PMSG 风电场工况里，三频率分解求出的 42.1 Hz 与扫频最低点一致，并且 42 Hz 时域结果最接近 reference。[pdf:E07]（PDF 物理页 4，Fig. 2–3 与 Section IV-B）缺少的证据是：不同拓扑和控制器、强瞬态或开关事件、非平稳频谱、不同积分器、多个观测量以及 worst-case window error。作者在实践性讨论中声称方法对频率分量数量和值没有限制，但这不等于证明它对随时间变化的频率集合也有效。[pdf:E06]（PDF 物理页 3，Section III-D）

## § 10 — 最小复现实验

一周内最值得复现的不是整套 PMSG 风电场，而是“解析 OSF 是否等于离散仿真的实际误差最小点，并且在有效条件内不随步长移动”。

**数据与模型。** 用论文报告的三组频率和幅值构造

\[
u(t)=3.2\cos(2\pi18.4t)+23.4\cos(2\pi50t)+17.5\cos(2\pi81.6t),
\]

取 \(K_I=1\)，建立 \(\dot{o}=u(t)\) 的精确解析响应和 Eq. (5) 对应的 SF trapezoidal 更新。频率与幅值来自论文算例；\(K_I=1\)、初相位为 0 和固定 4 s 观察窗是复现实验自行规定的条件，而不是论文报告值。[pdf:E03]（PDF 物理页 2，Eq. (5)–(14)）[pdf:E07]（PDF 物理页 4，Section IV-B）

**实现与测量。**

1. 用 Eq. (25) 或一维 root finder 算出理论 \(f_s^\*\)。
2. 对 \(f_s=0\) 到 100 Hz 做细网格扫描，分别以 0.02、0.05、0.1、0.2、0.4 ms 步长运行 SF 仿真。
3. 对每次运行计算相对精确解析响应的离散 2-norm error，记录每个步长的经验最小点和最小误差。
4. 检查 \(\pi|f_i-f_s|\Delta t\ll1\) 是否成立，并把违反条件的点单独标记，避免拿近似式解释其适用域之外的结果。

**支持标准。** 所有满足近似条件的步长，其经验最小点都应接近 Eq. (25) 的同一根；随着步长增大，误差可增大，但最小点不应系统漂移。论文算例给出的参照是 42.1 Hz。[pdf:E05]（PDF 物理页 3，Eq. (25)–(26)）[pdf:E07]（PDF 物理页 4，Fig. 3）

**反驳标准。** 若在无代码错误且近似条件满足时，实际误差曲线出现与理论根显著分离的最小点、多个稳定局部极小值，或最小点随步长发生超出频率网格误差的系统漂移，就直接反驳核心推导在该基准上的可复现性。

## § 11 — 最强反例设计

最强反例不是再换一个固定的谐波组合，而是构造**频谱在仿真过程中快速迁移**的波形，使全局静态 OSF 与局部精度目标发生冲突。例如，令主频从 50 Hz 连续下扫到 40 Hz，同时让一个 20 Hz 次同步分量在中段突然增幅，再加入一次控制限幅或开关事件。对同一高精度 reference，比较四种方案：固定 50 Hz、按全时窗频谱计算的静态 OSF、按短时窗在线更新的 OSF，以及足够小步长的原始 EMTP。

评价指标应同时包含全时窗 2-norm error、10–20 ms 滑动窗口最大误差、事件后峰值误差和相位偏差。如果静态 OSF 只降低全局 2-norm，却在频率穿越或事件窗口比 50 Hz 基线产生更大的最大误差，那么“一个 OSF 能代表该仿真的最佳频移”就只对 stationary/global-average 目标成立，不能支撑更广泛的瞬态准确性主张。

这个反例还提供一个具体的替代解释：论文得到的 42.1 Hz 可能主要是固定观察窗、固定三频率及平方 2-norm weighting 的共同产物，而不是该网络在任意瞬态阶段都应采用的固有频移中心。这个判断属于基于证据的候选攻击，不是论文已经验证的事实；论文只展示了一个稳定频率组合和一个风电场工况。[pdf:E07]（PDF 物理页 4，Fig. 2–3 与 Section IV-B）[pdf:E08]（PDF 物理页 4，Fig. 4 与 Conclusion）

## § 12 — Follow-up Research Idea

**候选研究方向：从离线静态 OSF，转向带稳定性与实现约束的 time-local shift-frequency policy。** 这是一项候选判断；本次严格 PDF-only 阅读没有进行外部相关工作检索，因此不声称 novelty。

**(a) 未满足的需求。** 电力系统高影响研究通常需要理论可解释性、跨工况验证、工程可实现性和对实际系统价值的证明。本文优化的是整段仿真的全局 2-norm error，但真实 EMT/HIL 场景更关心故障、限幅和控制切换附近的 worst-case local error，而且频谱可能随时间变化。一个固定 OSF 无法显式处理这两个目标差异。

**(b) 可能的研究价值。** 新问题不再是“求一个使全局误差最小的标量”，而是“在保持数值稳定、控制 OSF 切换开销的前提下，在线选择 \(f_s(t)\)，最小化窗口化最坏误差或给出可证明误差界”。如果能够证明 \(f_s(t)\) 的更新不会引入坐标跳变，并在多类电力电子网络和事件上降低 worst-case error，这会比给静态公式再加一个应用算例更接近本领域认可的系统性贡献。

**(c) 可借鉴的方法。** 可从 time-frequency analysis 借用短时频谱或 synchrophasor frequency tracking，从 online convex optimization 借用带 switching penalty 的滚动更新，再用 hybrid-system coordinate reset 处理 \(f_s(t)\) 改变时的状态连续性。硬件实现时可以把候选频率、误差上界和更新率限制成小规模流水化计算，但 FPGA 只是实现约束，不是研究贡献本身；本文没有提供任何 FPGA 资源或时序证据。

**(d) 第一个证伪实验。** 使用第 11 节的 chirp、振荡增幅和事件组合，在相同算力预算下比较静态 OSF、在线 policy 和 50 Hz 基线。若在线 policy 不能显著降低滑动窗口最大误差，或其坐标更新产生的额外误差、延迟和硬件开销抵消收益，就应否定该方向的核心价值。

**(e) 与本文的实质区别。** 本文在 stationary multi-frequency、固定 trapezoidal discretization 下求一个离线标量 \(f_s^\*\)，并以全局 2-norm error 为目标。[pdf:E04]（PDF 物理页 2，Eq. (20)–(23)）[pdf:E05]（PDF 物理页 3，Eq. (25)–(28)）候选方向把决策变量改为随时间变化的 policy，把目标改为局部最坏误差与切换成本的联合约束，并把状态连续性和可实现性纳入问题定义；它不是简单换一个应用领域或在原方法后增加模块。
