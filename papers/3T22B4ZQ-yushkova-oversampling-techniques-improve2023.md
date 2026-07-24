# Oversampling Techniques to Improve the Accuracy of Hardware-in-the-Loop Switching Models

作者：Marina Yushkova、Alberto Sanchez、Angel de Castro [pdf:E01]（PDF 物理页 1，标题与作者栏）  
出处：IEEE Transactions on Power Electronics，Vol. 38，No. 5，May 2023 [pdf:E01]（PDF 物理页 1，页眉与首页）  
年份：2023  
DOI：10.1109/TPEL.2023.3243702 [pdf:E01]（PDF 物理页 1，首页 DOI）  
Zotero key：3T22B4ZQ  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文处理的是一个很具体、却会破坏 HIL（Hardware-in-the-Loop，硬件在环）可信度的问题：开关电源的真实 PWM 或 gate signal 可能在一个数值积分步长内部发生跳变，但最朴素的实时模型只在仿真时钟边沿读取一次 ON/OFF 状态。这样，模型不是单纯“晚看见了一个边沿”，而是把整个积分区间错误地归给了某个开关模态，进而把电感电流和电容电压的状态增量算错。作者直接陈述，这种输入读取分辨率不足会产生数值误差和真实系统中不存在的低频/次谐波振荡；缩小积分步长虽然直观，但复杂实时模型受 FPGA 关键路径和实时截止期限制，不能无限缩小 [pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）。

这个误差的工程量级并不小。论文用异步 buck converter 举例：在积分步长 `dt = 500 ns`、开关频率约 `99.7118 kHz`、固定 duty cycle `41.11%` 时，仅约 `0.09%` 的 duty 读取误差，就可对应超过 `10%` 的电感电流误差，并形成周期性次谐波 [pdf:E02]（PDF 物理页 3，Table I、Fig. 1 及右栏说明）。这说明在某些 HIL 工况里，更高阶数值方法、更多有效位或更精细的器件参数并不是首要矛盾：若开关事件的时间占比读错，输入误差会遮蔽这些改进。

论文的价值是把“积分步长”和“输入事件时间分辨率”解耦。模型仍可用满足实时性的较大积分步长推进状态，但用更快的采样时钟记录一步内各开关模态持续了多久，再把这些信息用于下一次状态更新。若这一机制成立，就能在不改变原数值方法和主仿真时间网格的前提下，显著压低 PWM 异步采样造成的伪振荡，并使高开关频率 converter、较复杂拓扑或较大步长模型仍有机会满足实时性与精度要求。

## § 2 — 前人工作与不足

论文把既有方案分成三类。第一类是用于 averaged model 的 time averaging 或 sub-cycle averaging：它们利用过采样后的占空比平滑输出，已能削弱输入读取造成的人工低频谐波，但对象是平均模型，不是保留开关瞬态的 switching model；作者还指出其潜在代价包括高频开关谐波衰减和实时计算延迟 [pdf:E01]（PDF 物理页 1，Section I-A）[pdf:E03]（PDF 物理页 2，Section I-A）。

第二类是 missed switching event 之后的 post-interpolation/post-correction。早期方法会回退时间、改变步长或改变原始时间网格，因此难以满足严格实时约束；FICS（fixed step-size and clock synchronization）避免了部分问题，但论文指出其计算负担和精度收益未被完整量化。针对多个开关事件的插值/外推组合在离线仿真中有改善，但额外复杂度是否能在实时环境中承受仍不清楚 [pdf:E03]（PDF 物理页 2，左栏相关工作）。

第三类是商业 HIL 的 GDS oversampling。论文认可 Typhoon HIL 已展示输入过采样能够减小不希望出现的振荡，但公开资料没有给出可复核的数学算法和 FPGA 实现细节 [pdf:E03]（PDF 物理页 2，左栏末段）。因此本文真正要补的缺口不是“第一次想到多采几次 PWM”，而是：为 switching model 给出固定一步延迟、固定时间网格、可综合到 FPGA 的明确算法；同时比较顺序敏感与顺序无关两种实现的精度、资源和最小时钟周期，并处理一步内多个 switching event。

作者的 novelty 声明是：顺序方法借鉴既有软件思路，而只保留各状态时间比例、并行计算所有模态贡献的 ApPar（parallel approach）据其所知此前未被提出；论文以单事件异步 buck 和双事件同步 buck 做 MATLAB 与 HLS 对比，再把 ApPar 实装到 FPGA [pdf:E03]（PDF 物理页 2，Section I-B）。由于本任务严格不使用包外材料，这里只能记录作者的 novelty 声明，不能独立认证其全球首创性。

## § 3 — 重建作者的思考路径

可以从一个失败诊断开始重建作者的路径。第一步，观察到状态误差与 duty 读取误差呈相同周期，而不是与 forward Euler（FE）本身的截断误差呈同一规律；这提示主要误差源是“开关模态持续时间分配错误”，不是连续状态方程本身 [pdf:E02]（PDF 物理页 3，Fig. 1 与相邻正文）。第二步，把 PWM 采样频率提高：如果事件检测误差由积分步长的一半量级，变成由更小 sampling step 决定，那么无需缩小主积分步长也能恢复更准确的模态占比 [pdf:E04]（PDF 物理页 4，Fig. 3 与相邻正文）。

第三步，最自然的算法是按真实发生顺序逐段积分：先用事件前模态推进到中间状态，再用事件后模态继续推进。这就是 ApSeq，物理解释最直接，也保留了顺序信息；但后一个子段依赖前一个子段的中间状态，天然形成串行数据依赖 [pdf:E05]（PDF 物理页 5，Fig. 4、Eq. (4) 与说明）。当一步内有多个事件时，关键路径会随事件数增加，这对 FPGA 实时模型不利 [pdf:E06]（PDF 物理页 6，Fig. 5 与左栏说明）。

第四步是本文最关键的抽象：在足够短的积分步长内，是否可以不保存事件顺序，只保存每个模态在本步所占的时间比例，并把各模态的斜率贡献并行相加？这会丢掉“先发生哪个模态”对中间状态的影响，但能消除串行依赖。作者据此提出 ApPar；其判断是，在电力电子 HIL 常用的小步长下，顺序项带来的精度差异很小，而并行结构节省的关键路径更重要 [pdf:E07]（PDF 物理页 5，Eq. (6)、Eq. (7) 与说明）。这一段是基于论文证据重建的思考路径，不是作者逐句写出的研发日志。

## § 4 — 核心 Intuition

不要把一个积分步内的 PWM 当作单一 ON 或 OFF，而要把它看成若干开关模态及各自持续时间的组合。ApSeq 按模态出现顺序逐段推进状态；ApPar 则从步首状态同时计算各模态斜率，再按持续时间加权求和，因此牺牲少量顺序信息，换取更短、更易扩展的 FPGA 数据路径 [pdf:E05]（PDF 物理页 5，Eq. (4)）[pdf:E07]（PDF 物理页 5，Eq. (6)）。论文的核心赌注是：在足够小的 HIL 积分步长里，输入事件时间误差远大于丢弃顺序造成的高阶差异，所以“正确的模态占比”比“严格的模态顺序”更重要。

## § 5 — 具体方法与完整 Pipeline

以论文的异步 buck 为例，其参数包括 `Vin = 200 V`、`Vout = 100 V`、`C = 35 μF`、`L = 850 μH`、`R = 7.5 Ω`；同步 buck 在此基础上加入器件与导通损耗，并允许 high-side、low-side、deadtime 三种模态 [pdf:E02]（PDF 物理页 3，Table I 与 Fig. 2）。完整 pipeline 如下。

1. **高频采样输入。** FPGA 以 `dt_samp` 采集 PWM/gate signal；论文实验统一使用 `dt_samp = 10 ns`。在一个主仿真步 `dt` 内，不保存全部 bit stream，而用少量 counter 累计各开关状态出现的采样点数或持续时间；多事件同步 buck 还要分别统计 ON、deadtime、OFF 等模态 [pdf:E06]（PDF 物理页 6，Fig. 5）[pdf:E08]（PDF 物理页 7，Section IV-A）。

2. **固定一步缓存。** 当前步收集到的模态信息用于下一仿真步计算，形成固定一个 simulation step 的同步延迟。作者强调，输出不是先给错误值再回改，而是在固定延迟后直接更新为校正后的状态；由于主步长远小于 switching period，这一延迟被视为可接受 [pdf:E03]（PDF 物理页 2，右栏实现边界）。

3. **选择状态更新算法。** 普通 FE 只使用时钟边沿看到的一个模态。ApSeq 将一步拆成按事件顺序排列的子区间，逐段计算中间状态；其硬件又分为复用算术单元的 `ApSeq_r` 和不复用、展开长公式的 `ApSeq_nr`。ApPar 不计算中间状态，只用各模态在本步的时间比例，对从步首状态求得的模态斜率做加权和 [pdf:E05]（PDF 物理页 5，Eq. (4)–(5)）[pdf:E07]（PDF 物理页 5，Eq. (6)）。

4. **处理多个 switching event。** 对同步 buck，一步内可能出现 `on → deadtime → off`，也可能是别的排列。ApSeq 必须按出现次序串行执行；ApPar 把所有模态贡献并行生成，最后做一次 weighted sum，因此事件数增加时延迟增长更慢 [pdf:E06]（PDF 物理页 6，Fig. 5 与 Section III-B）。

5. **数值与 FPGA 映射。** 论文用 32-bit IEEE 754 floating-point、forward Euler 和 Xilinx Vivado HLS；综合目标是低端 `xc7a35ticsg324-1L` FPGA。作者认为采样只需 counter 和少量状态信息，无需大容量 waveform memory [pdf:E08]（PDF 物理页 7，Section IV 设置）[pdf:E09]（PDF 物理页 8，Section IV-B）。实验版用 C++ 在 Vitis HLS 建模，再导出到 Vivado；外部 waveform generator 提供固定 PWM，ILA（Integrated Logic Analyzer，集成逻辑分析仪）采集状态变量 [pdf:E10]（PDF 物理页 9，Fig. 9 与 Section V）。

一个具体例子是 `dt = 500 ns`、`dt_samp = 10 ns`：一步内约有 50 个采样间隔。若 ON 占 21 个、OFF 占 29 个，ApPar 不关心二者先后，只按 `21/50` 与 `29/50` 加权两套模态斜率；ApSeq 则还要记录事件位置并先后推进。二者最终都在固定一步延迟后输出新的 `iL`、`vC`，但 ApPar 的计算图没有前后子区间的状态依赖。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确形式化数学。异步 buck 的连续状态为电感电流 `iL` 与电容电压 `vC`，基础方程是

\[
\frac{di_L}{dt}=\frac{v_L}{L},\qquad
\frac{dv_C}{dt}=\frac{i_C}{C}.
\]

`vL` 与 `iC` 由开关状态和电感电流符号决定；例如闭合开关时 `vL = vin - vC`，打开开关时可能是 `vL = -vC`、`vin-vC` 或 `0`。这意味着 commutation moment 不只改变一个布尔输入，而是切换整套状态导数 [pdf:E11]（PDF 物理页 4，Eq. (1)–(2)）。

普通 forward Euler 在一个完整步长内只用步首导数：

\[
i_{L,n+1}=i_{L,n}+v_{L,n}\frac{dt}{L},\qquad
v_{C,n+1}=v_{C,n}+i_{C,n}\frac{dt}{C}.
\]

若事件发生在步内，`vL,n`、`iC,n` 只代表其中一个模态，因此错误来自把整段 `dt` 都乘到了错误斜率上 [pdf:E11]（PDF 物理页 4，Eq. (3) 与说明）。

为便于解释 Eq. (4)，令 `Δt1 = te - t0`、`Δt2 = t1 - te`。ApSeq 先用事件前模态得到中间状态，再用事件后模态继续推进：

\[
\begin{aligned}
i'_{L1}&=i_{L0}+v_{L0}\frac{\Delta t_1}{L},&
v'_{C1}&=v_{C0}+i_{C0}\frac{\Delta t_1}{C},\\
i_{L1}&=i'_{L1}+v'_{L1}\frac{\Delta t_2}{L},&
v_{C1}&=v'_{C1}+i'_{C1}\frac{\Delta t_2}{C}.
\end{aligned}
\]

第二段的斜率依赖中间状态，所以必须等第一段完成；这正是 ApSeq 的串行关键路径 [pdf:E05]（PDF 物理页 5，Fig. 4、Eq. (4) 与正文）。`ApSeq_nr` 把相同代数关系展开为一个长表达式，数学结果相同，但允许 HLS 以不同方式优化组合逻辑 [pdf:E05]（PDF 物理页 5，Eq. (5)）。

ApPar 则把两段斜率都在步首状态处求出，直接做持续时间加权：

\[
\begin{aligned}
i_{L1}&=i_{L0}+\frac{v'_{L0}\Delta t_1+v''_{L0}\Delta t_2}{L},\\
v_{C1}&=v_{C0}+\frac{i'_{C0}\Delta t_1+i''_{C0}\Delta t_2}{C}.
\end{aligned}
\]

因此它只需要各模态总占比，不需要事件顺序 [pdf:E07]（PDF 物理页 5，Eq. (6) 与说明）。基于 Eq. (4) 与 Eq. (6) 的推断是：二者差异来自“第二段斜率是否在中间状态重新计算”；当 `dt` 很小、一步内状态变化有限时，这个顺序差异通常比完全错读模态持续时间小，但论文没有给出对任意拓扑都成立的误差上界。

实验误差用 mean absolute error：

\[
\mathrm{MAE}=\frac{1}{n}\sum_{j=1}^{n}|y_j-x_j|,
\]

其中 `yj` 是待测模型，`xj` 是 golden model [pdf:E08]（PDF 物理页 7，Eq. (9)）。相对 FE 的精度改善定义为

\[
\mathrm{improvement}(\%)=\frac{\mathrm{error}_{FE}-\mathrm{error}_{Approach}}{\mathrm{error}_{FE}}\times100,
\]

[pdf:E12]（PDF 物理页 8，Eq. (10)）。硬件实验对次谐波的改善则用无过采样与有过采样的 oscillation amplitude 之差除以前者 [pdf:E13]（PDF 物理页 9，Eq. (11)）。

## § 7 — 实验设计与结论

**问题一：过采样是否真的消除了异步 PWM 读取造成的主要数值误差？** 作者建立异步无损 buck 与带损耗同步 buck，使用相同 converter equations 构造 `1 ns` 步长、所有 ON/OFF/deadtime 均与时间网格对齐的 golden model；待测模型使用 `dt = 10–1000 ns`、`dt_samp = 10 ns`、`fsw ≈ 99.71 kHz`、duty `41.11%`，总仿真 `27 ms`，并以 MAE 比较 FE、ApSeq 与 ApPar [pdf:E14]（PDF 物理页 6，Fig. 6 与 reference model 说明）[pdf:E08]（PDF 物理页 7，Fig. 8 与 Section IV-A）。答案是：没有 oversampling 时出现显著次谐波；两种 oversampling 曲线在图的分辨率下基本重合。只取 5 个中间点时，异步 buck 的 `iL` 改善约 `68.2%`、`vC` 改善约 `59.8%`；从 30 个点起，多数组合已达到约 `97%–99%`，500 ns 步长时异步 buck 的改善约为 `99.36%–99.46%` [pdf:E12]（PDF 物理页 8，Table II–III）。

**问题二：closed-loop 下，控制器是否会自动压掉这种误差？** 作者用 `R(z)=0.0001/(z-1)` 的 PI controller 把电容电压调到 `70 V`，并去除 switching ripple 以观察 sampling subharmonic。无过采样时电容电压人工振荡约 `0.9 V`，即平均值的 `1.3%`；使用任一 oversampling 后降到约 `0.19 V`，即 `0.27%` [pdf:E14]（PDF 物理页 6，Eq. (8)、Fig. 7 前置说明与数值）。答案是控制闭环不能可靠消除输入时间量化误差，反而会让 HIL controller test 建立在伪动态上；oversampling 才直接针对误差源。

**问题三：ApPar 是否比 ApSeq 更适合 FPGA？** 作者将 FE、`ApSeq_r`、`ApSeq_nr`、ApPar 用 Vivado HLS 综合到 `xc7a35ticsg324-1L`。异步 buck 的最小周期分别为 `124.94 ns`、`250.72 ns`、`241.82 ns`、`188.73 ns`；同步 buck 分别为 `236.95 ns`、`552.11 ns`、`540.33 ns`、`322.91 ns`。因此 ApPar 相对 FE 的时间开销为 `1.51×` 和 `1.36×`，而顺序方案约为 `1.94×–2.33×`；LUT/FF 大体都增加到约两倍，ApPar 并不是资源最省的绝对赢家，但关键路径明显最好 [pdf:E09]（PDF 物理页 8，Table IV–V）。答案是论文的“parallel”优势主要体现为 minimum achievable period，而不是显著降低全部资源。

**问题四：ApPar 在真实 FPGA HIL 中能否复现实验趋势？** 作者用外部固定 PWM、FPGA、ILA 和计算机搭建开环硬件实验，以避免 closed-loop controller 掩盖 oversampling 效果；FE 与 ApPar 分别使用其可实现的约 `130 ns` 与 `190 ns` 主步长 [pdf:E10]（PDF 物理页 9，Fig. 9 与 Section V）。测试覆盖 `99.71–113.09 kHz`、duty `13.64%–41.11%`，实验 waveform 中 oversampling model 与 `1 ns` offline reference 基本重合，而 regular FE 出现大幅低频包络 [pdf:E15]（PDF 物理页 10，Fig. 10）。Table VI–VII 报告电感电流 oscillation decrease 为 `92.48%–98.98%`，电容电压为 `94.62%–99.64%`；相同参数下 re-simulation 与实验误差的差距不超过约 `±1%` [pdf:E16]（PDF 物理页 10，Table VI–VII 与下方正文）。答案是 ApPar 的核心现象在该 buck 平台上得到硬件支持。

不得外推的范围也很明确：论文只验证两种 buck 数学模型、最多两个 switching event，并只对基础异步 buck 做硬件实验；硬件实验使用固定外部 PWM，不是实际 closed-loop controller；器件强非线性、磁饱和、复杂换流网络、故障事件和大量一步内事件都未覆盖。 作者在结论中把数值误差改善概括为最高约 `98%`，把实验次谐波抑制概括为最高约 `99%` [pdf:E17]（PDF 物理页 11，Fig. 11 与 Section VI）。

## § 8 — Take-aways

**5 句话：**

1. HIL switching model 的主要误差可能来自 PWM 事件在积分步内部发生，而不是来自 FE 阶数本身 [pdf:E02]（PDF 物理页 3，Fig. 1）。
2. 输入 oversampling 通过恢复各开关模态的持续时间，把输入时间分辨率从主积分步长中解耦出来。
3. ApSeq 保留事件顺序但形成串行依赖，ApPar 只保留模态占比并行计算，因此更适合多个 switching event [pdf:E05]（PDF 物理页 5，Eq. (4)）[pdf:E06]（PDF 物理页 6，Fig. 5）。
4. 在两种 buck 模型里，ApPar 与 ApSeq 的 MAE 改善几乎相同，而 ApPar 的 HLS minimum period 明显更短 [pdf:E12]（PDF 物理页 8，Table II–III）[pdf:E09]（PDF 物理页 8，Table IV–V）。
5. FPGA 实验显示过采样能把报告工况中的低频振荡压低约 `92%–99.6%`，但论文尚未证明 ratio-only 抽象对任意拓扑都可靠 [pdf:E16]（PDF 物理页 10，Table VI–VII）。

**3 句话：**

1. 论文把 PWM 异步采样误差重新表述为“一步内模态占比错误”，并用高频 counter 获取占比。
2. 最重要的工程结果不是 ApPar 更准，而是它在几乎不损失精度的情况下显著缩短 FPGA 关键路径。
3. 最重要的科学未决问题是：什么时候事件顺序可以忽略，什么时候相同占比却会产生不同终态。

**1 句话：**

用高频采样恢复开关模态占比，再用并行加权状态更新替代顺序子步积分，是这篇论文在实时性与精度之间找到的核心折中。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在目标 HIL 步长下，事件顺序对一步终态的影响足够小，以至于仅知道各模态持续时间比例就能接近顺序积分。** 这是 ApPar 成立的必要条件；若两个序列拥有相同 ON/OFF/deadtime 占比，却因先后顺序不同而进入不同的导通分支或产生明显不同的中间状态，ApPar 会把它们压缩成同一个输入并输出同一结果。

这个假设在论文工况中有经验支持：异步与同步 buck、`dt_samp = 10 ns`、`dt = 50–1000 ns` 时，ApPar 与 ApSeq 的误差曲线近乎重合，差异被作者描述为电压最多约四位小数、电流约五位小数的量级 [pdf:E08]（PDF 物理页 7，Fig. 8 与右栏末段）[pdf:E12]（PDF 物理页 8，Table II–III）。多事件同步 buck 也表明并行加权在两个事件时没有明显精度崩溃 [pdf:E06]（PDF 物理页 6，Fig. 5 与 Section III-B）。

但证据缺口同样关键。Eq. (2) 显示异步 buck 的开关打开模态还依赖 `iL` 的正、负或零；若一步内电流跨零，先 ON 后 OFF 与先 OFF 后 ON 可能进入不同的二极管导通路径 [pdf:E04]（PDF 物理页 4，switch-state equations）。在 discontinuous conduction、deadtime 很长、器件非线性强、谐振状态变化快、fault transient 或一步内事件数较多时，“顺序项很小”未必成立。论文没有给出可跨拓扑的误差界，也没有在这些边界工况上验证，因此“可直接迁移到任意拓扑”应视为作者主张，而不是已经闭合的普适结论。

## § 10 — 最小复现实验

一周内最有价值的复现不是先做完整 FPGA，而是复现“占比足够、顺序可忽略”这一核心 claim。

使用 Python、MATLAB 或 Julia 实现论文的两种 buck 状态方程和 FE。建立 `1 ns`、PWM 边沿完全可定位的 golden model；待测组使用 `dt_samp = 10 ns`，主步长取 `100、200、300、500、1000 ns`，开关频率与 duty 选用 `99.71 kHz/41.11%`，再加入两组不与时间网格整除的频率和 duty。实现三条路径：单点 FE、按事件顺序更新的 ApSeq、按模态占比加权的 ApPar；记录 `iL`、`vC` 的 MAE、低频包络振幅，以及 ApPar 与 ApSeq 的直接差值。论文给出的 reference、步长范围和 MAE 定义可直接复用 [pdf:E08]（PDF 物理页 7，Eq. (9) 与实验设置）。

预先规定支持标准：在至少四个主步长上，ApSeq/ApPar 相对 FE 的 improvement 与 Table II–III 相差不超过 `±2` 个百分点；当一步内有至少 30 个 sampling interval 时，两者都达到 `≥95%` 改善，且 ApPar 与 ApSeq 的改善率差不超过 `1` 个百分点 [pdf:E12]（PDF 物理页 8，Table II–III）。反驳标准：ApPar 在多个步长上稳定比 ApSeq 差 `>5` 个百分点，或 oversampling 后低频包络仍与 FE 同量级。这个实验只需几百行状态更新代码，却能直接检验论文最重要的数值机制。

## § 11 — 最强反例设计

最强反例应专门利用 ApPar 丢弃的那一维信息：**构造相同模态占比、不同事件顺序的两条 PWM 序列。** 令异步 buck 的初始 `iL` 略大于零，并选择足够大的主步长，使 OFF 区间可能让电流在步内跨零。序列 A 先 OFF 后 ON，序列 B 先 ON 后 OFF；两者 ON 与 OFF 的总持续时间完全相同。根据 Eq. (2)，A 可能先经历正电流续流、跨零后进入另一开关分支，而 B 先把电流抬高，后续 OFF 段未必跨零 [pdf:E04]（PDF 物理页 4，Eq. (2)）。

ApPar 只看总占比，所以对 A、B 给出同一更新；高分辨率 event-driven reference 和 ApSeq 则应给出不同终态，因为后半段导数取决于前半段产生的中间状态 [pdf:E05]（PDF 物理页 5，Eq. (4)）[pdf:E07]（PDF 物理页 5，Eq. (6)）。实验扫动初始电流、`dt/L` 比例、负载、deadtime 与事件数，并测量一步终态误差和长期次谐波。如果存在一片稳定参数区，使 ApSeq 跟随 reference、ApPar 却系统性选择错误导通分支或形成新的低频误差，那么论文的核心机制不是“普遍可忽略顺序”，而只是“在本文小步长 buck 工况中顺序影响较小”。这个反例比泛泛增加噪声或更换拓扑更强，因为它保持 ApPar 的全部可见输入不变，只改变被算法主动丢弃的信息。

## § 12 — Follow-up Research Idea

候选方向是建立一种**带可验证误差界的事件抽象 HIL 求解器**：系统不预先固定只用 ApSeq 或 ApPar，而是在线判断当前一步的开关模态是否近似可交换。若顺序敏感度低，就使用 ratio-only ApPar；若处于电流跨零、deadtime、饱和、强非线性或多事件聚集区，就触发有限次数的顺序子步或 event-local correction。研究目标从“提出一个更快算法”改为“在给定 FPGA 时间与资源预算下，为每一步选择最便宜且满足误差证书的事件表示”。

(a) 未满足的需求是，论文证明了 ApPar 在两个 buck 模型上很好，却没有告诉工程师何时可以安全忽略事件顺序；实际 HIL 更需要可解释的失效边界，而不只是平均 benchmark。  
(b) 在 EMT、FPGA 与 power electronics 领域，高影响价值来自同时满足严格实时截止期、可综合资源约束、跨拓扑精度和硬件实验；一个能给出在线误差界并自动降级的求解框架，比再增加一种固定 oversampling 公式更接近可部署基础能力。  
(c) 可借鉴 hybrid systems 的 mode-transition analysis、数值 ODE 的 local error estimator，以及用于判断两种模态先后是否近似等价的 noncommutativity/commutator 思路；实现上把估计器约束为少量乘加、比较器和有限状态机。  
(d) 第一个可证伪实验就是第 11 节的“相同占比、反转顺序”数据集：估计器必须在 ApPar 误差变大前触发顺序处理，并在普通小步长区保持 ApPar；若它不能对跨零与 deadtime 工况给出保守上界，方向即失败。  
(e) 与本文的实质区别是，本文选择一个固定的 ratio-only 并行更新，并依靠经验结果说明顺序影响小 [pdf:E10]（PDF 物理页 9，Section IV-C）；候选研究把“顺序能否忽略”本身变成在线可检验对象，并把准确性声明从特定拓扑的统计结果提升为逐步决策与失效证书。

由于本任务未检索包外相关工作，这一方向只标为候选研究想法，不声称 novelty。
