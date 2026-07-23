# Improved Interpolation Algorithm Accounting for Multiple Switching Actions and Reinitialization

- Zotero key：`Q5W4UKM2`
- slug：`cao-improved-interpolation-algorithm2023`
- 作者：Cao Yang、Gu Wei、Xu Mingwang、Liu Wei、Zhang Fei
- 年份与出处：2023，IEEE International Conference on Energy Technologies for Future Grids (ETFG)
- DOI：`10.1109/ETFG55873.2023.10408552`
- 源 PDF：`_source.pdf`
- PDF SHA-256：`13cc8c697640895525f86997af160a332c5b763d564983269ac2f630b090e1b6`
- 阅读边界：以下论文事实均直接取自这份 6 页源 PDF；批评、反例与研究方向会明确标成基于证据的判断，不冒充作者结论。

## § 1 — 研究问题与重要性

论文处理的是固定步长 EMTP 类电磁暂态仿真中的“开关动作不落在整步点”问题。真实二极管可能在 \(t_d\) 电流过零时关断，但离散程序只在 \(t_1\) 算出负电流，往往到 \(t_1+\Delta t\) 才更新开关状态；这段延迟会在电流、电压波形中制造假尖峰和非特征谐波。若一个仿真周期内连续发生多个开关动作，把它们压成同一时刻又会丢失动作顺序，甚至诱发积分振荡。[pdf:E02]

这个问题的重要性不只是“波形更好看”。电力电子系统把离散拓扑变化和连续电磁状态耦合在一起；若为了捕捉每个动作而一味缩小步长，计算量会迅速上升，复杂网络和实时 EMT 仿真的速度目标就更难达到。作者因此追求的是：在不破坏固定整步时间序列、不过度增加计算的前提下，同时处理开关定位、换流后的状态初始化、数值振荡与同一步内的多次动作。[pdf:E01] [pdf:E02]

## § 2 — 前人工作与不足

作者把既有路线分成两类：一类用小步积分直接走到精确开关时刻，准确但计算代价高；另一类用 interpolation 从相邻整步状态恢复动作时刻，无需重新积分，因而更适合提速。PSCAD/EMTDC 的 half-interpolation 已经是可用的固定步方案，但传统方案在多动作、动作瞬间响应和整步重同步上仍有缺口。[pdf:E01]

论文点名的不足很具体：已有多开关算法可能默认同一周期内的动作同时发生，效率高却牺牲时序精度；DIRK 两阶段方案会改变原有整步点排列；加权积分方案可能在连续多动作时不断后移积分点，导致连续若干整步状态拿不到；double-step/double-interpolation 与三次插值方案计算更复杂；B_FIRST 使用 backward Euler，精度受损；TR_FIRST 虽提高精度，却可能不求得下一整步状态，也没有对换流做 reinitialization。[pdf:E01] [pdf:E02] [pdf:E03]

因此，本文真正补的不是一个孤立插值公式，而是把五件原本分散处理的事放进同一固定步流程：integration、event localization、reinitialization、resynchronization 和 multiple switching。[pdf:E03] [pdf:E04]

## § 3 — 重建作者的思考路径

下面是基于论文论证顺序重建的思考路径，不是作者逐字陈述。

第一步，先把误差源拆开：拓扑突变会让隐式梯形法在电感、电容附近产生数值振荡；真实动作位于非整步时刻又会造成事件延迟。前者需要切换积分方式或重设初值，后者需要 event localization，单靠一种处理不够。[pdf:E02] [pdf:E03]

第二步，区分 forced commutation 与 natural commutation。强迫换流由控制信号触发，拓扑突变后要依据电容电荷与电感磁链连续性重新计算初始状态；自然换流由电流或电压条件触发，状态连续，重点是找准 \(t_d\) 并抑制数值振荡。[pdf:E03]

第三步，把工程约束加入推理：固定步仿真最终仍要回到原来的 \(t,t+\Delta t,\ldots\) 序列，且最好不额外重构导纳矩阵。于是较自然的组合是：常规段用隐式梯形法，动作后用两个 half-step backward Euler 消振，线性插值定位并恢复整步点，若检测到下一个自然换流则在同一步内继续循环。[pdf:E03] [pdf:E04] [pdf:E05]

## § 4 — 核心 Intuition

不要把一个步长内的所有开关动作压成同一时刻，而要在同一固定步框架里逐个定位、更新拓扑并继续检查后续动作。动作瞬间先按物理连续性重设状态，再用两个 backward Euler 半步消除梯形积分的振荡，最后插值回原整步时间轴。这样把“事件时刻准确”“状态接续正确”和“整步输出可用”作为一次局部修复，而不是牺牲其中一项换另一项。[pdf:E04] [pdf:E05]

## § 5 — 具体方法与完整 Pipeline

以一个步区间 \((t,t+\Delta t)\) 内先发生强迫换流、随后二极管自然换流为例，流程如下：

1. 在 \(t\) 根据控制信号判断 forced commutation。若发生，按电容电荷守恒和电感磁链守恒，把电容等效为电压源、把电感等效为电流源，源值取换流前状态；若换流直接断开电感或短接电容，则相应等效源取 0。重构开关后的等效拓扑并计算新的初始状态。[pdf:E04]
2. 用 implicit trapezoidal method 从 \(t\) 积分到 \(t+\Delta t\)，检查区间内是否出现自然换流。没有动作就直接进入下一整步；有动作则用线性 interpolation 定位 \(t_d\)。[pdf:E04]
3. 从 \(t\) 与 \(t+\Delta t\) 的状态插值得到动作前的 \(t_d^-\)，切换器件状态。[pdf:E05]
4. 从 \(t_d\) 出发，以 \(\Delta t/2\) 为半步连续做两次 backward Euler，得到 \(t_d+\Delta t/2\) 与 \(t_d+\Delta t\) 的状态；再由这两点插值得到动作后的 \(t_d^+\)，用于数值振荡校正。[pdf:E05]
5. 检查 \((t_d^+,t_d+\Delta t)\) 内是否还有自然换流。有则回到第 3 步逐个处理；若两个动作的间隔小于一个预设“小时间常数”，作者允许把它们视为同时发生以节省计算，但没有在文中给出该阈值的选取公式。[pdf:E04] [pdf:E05]
6. 没有更多动作后，用 \(t_d\) 与 \(t_d+\Delta t\) 的状态插值恢复原来的 \(t+\Delta t\) 整步状态，这就是 resynchronization。[pdf:E04] [pdf:E05]
7. 在 \(t+\Delta t\) 处重新用隐式梯形法推进到 \(t+2\Delta t\)，进入下一周期。[pdf:E05]

作者对单次自然换流给出的额外工作量是三次线性 interpolation 和两次 half-step integration；相对传统线性插值多一次线性插值和一次积分，且积分过程不需要修改导纳矩阵。reinitialization 的等效电路可在仿真前预分析，因此作者判断额外计算较小，但论文没有给出运行时间、复杂度曲线或硬件资源实测。[pdf:E05]

## § 6 — 核心数学推导

论文没有证明新的收敛定理；数学部分是对所用数值构件及其误差项的说明。

隐式梯形积分写成

\[
y(x_{i+1})=y(x_i)+\frac{h}{2}\left[f(x_i,y(x_i))+f(x_{i+1},y(x_{i+1}))\right]-\frac{1}{12}y'''(\xi)h^3 .
\]

其中 \(h\) 是步长，\(f\) 是微分方程右端，\(\xi\) 位于当前积分区间。式末项说明作者采用的截断误差量级为 \(O(h^3)\)：它利用区间两端的斜率，通常比一阶 backward Euler 准确，但在开关突变附近可能振荡。[pdf:E03]

backward Euler 写成

\[
y(x_{i+1})=y(x_i)+h f(x_{i+1},y(x_{i+1}))-\frac{1}{2}y''(\xi)h^2 ,
\]

对应作者给出的截断误差量级 \(O(h^2)\)。它的精度阶次较低，却有更强的数值阻尼，所以本文只在动作后连续使用两个 \(\Delta t/2\) 半步，不把它当作全程积分器。[pdf:E03] [pdf:E04]

线性 interpolation 用相邻两点 \((x_i,f(x_i))\)、\((x_{i+1},f(x_{i+1}))\) 构造

\[
f(x)=\frac{x-x_{i+1}}{x_i-x_{i+1}}f(x_i)
     +\frac{x-x_i}{x_{i+1}-x_i}f(x_{i+1})+R_x ,
\]

论文同时写出了含 \(\frac{f''(\xi)}{2}(x-x_i)(x-x_{i+1})\) 的余项形式。直观上，它假定相邻动作之间的系统轨迹可由直线近似；作者以每个固定步都求解线性网络方程 \(I=GU\) 且 EMT 步长较小来支持这一选择。但“每步代数方程线性”并不自动等价于“跨开关事件的时间轨迹线性”，这是后面最值得检验的假设。[pdf:E03]

## § 7 — 实验设计与结论

**问题 1：改进算法在不同步长下能否保持波形精度？** 作者建立 Boost chopper：360 V 直流源串联 0.001 Ω 电阻，右侧负载 5 Ω，电感 2 mH，两只电容各 5 mF，占空比 0.64，载波频率 5 kHz；仿真总时长 1 s，步长分别为 1 μs、10 μs、100 μs。[pdf:E05]

**实验 1：** 在 C++ 平台实现 traditional linear interpolation 与 improved interpolation，并与 PSCAD/EMTDC 的 half-interpolation 模型对比。观察量是 DC 输出功率 \(P_{dc}\)、A 点电压 \(U_A\) 和开关 \(S_1\) 电流 \(I_1\)，同时比较全时段与约 0.4 s 附近的动作细节。[pdf:E05]

**答案 1：** 作者从 Fig. 5 的波形判断，改进算法与 PSCAD 在稳态状态量上基本一致，早期整体变化也大致吻合；传统线性插值存在明显误差，且步长增大时误差加重。改进算法在 10 μs 下的输出特性基本匹配其 1 μs 结果，因此作者声称它可在 10 μs 这类较大步长保持精度。[pdf:E05] [pdf:E06]

**问题 2：reinitialization 是否让算法在动作瞬间正确响应？** Boost 电路在 \(S_1\) 关断后需要二极管导通；若不重设状态，可能出现作者所称的 “flameout”，即二极管不能进入应有的放电状态。[pdf:E05]

**答案 2：** 作者观察到 improved method 在开关动作瞬间产生响应，而 traditional linear interpolation 与 PSCAD half-interpolation 到下一仿真步才响应，据此认为改进方法对动作瞬间更准确。[pdf:E06]

实验的证据边界也很清楚：文中只有一个小型 Boost 案例和波形图，没有误差范数、事件时刻误差表、运行时间、导纳矩阵更新次数、统计重复或大型系统测试。因此，“不显著增加计算量”和“大步长加速”主要由操作计数与波形对照支撑，不是端到端性能测量。[pdf:E05] [pdf:E06]

## § 8 — Take-aways

**5 句话**

1. 固定步 EMT 的开关误差同时来自事件落在非整步点和拓扑突变后的状态接续，不能只靠缩小步长解决。[pdf:E02]
2. 本文把 implicit trapezoidal、动作后两个 backward Euler 半步、linear interpolation、reinitialization 和 resynchronization 组合成一个多动作流程。[pdf:E04] [pdf:E05]
3. 强迫换流重算初值，自然换流定位 \(t_d\)，同一步内若还有动作则继续循环处理。[pdf:E03] [pdf:E05]
4. 单个 Boost 案例显示 improved method 在 10 μs 下基本匹配自身 1 μs 波形，并比 traditional linear interpolation 更接近 PSCAD 结果。[pdf:E05] [pdf:E06]
5. 论文尚未用大型系统、量化误差与运行时间证明其效率和可扩展性，作者也把 large-scale performance 列为后续工作。[pdf:E06]

**3 句话**

1. 论文的关键贡献是让“逐个开关定位—状态重设—消振—回到整步点”在一个固定步流程中闭环。[pdf:E04] [pdf:E05]
2. Boost 波形支持方法在较大步长下有潜力，但证据仍是单案例、定性比较。[pdf:E05] [pdf:E06]
3. 真正的风险是线性轨迹与近邻动作合并假设没有被系统地压力测试。[pdf:E03] [pdf:E04]

**1 句话**

这是一种物理约束与数值积分混合的开关事件修复流程，结果有希望，但还没有跨越从“小型波形演示”到“可量化、可扩展 EMT 算法”的证据门槛。[pdf:E04] [pdf:E05] [pdf:E06]

## § 9 — 最脆弱的假设

最脆弱的假设是：在相邻整步点以及相邻开关动作之间，目标状态随时间足够接近线性，因此由两点 linear interpolation 得到的 \(t_d\)、\(t_d^-\)、\(t_d^+\) 与重同步整步状态都足够准确。[pdf:E03]

这个假设一旦失效，会同时击穿事件定位、动作后状态和多动作顺序三个环节。高频振荡、刚性 RLC、控制饱和、二极管反向恢复或多个事件间隔接近电路最快时间常数时，轨迹可能具有明显曲率；即使每个时刻的网络代数方程写成 \(I=GU\)，跨时间的状态也不必线性。reinitialization 能修正拓扑突变后的物理初值，却不能补回错误的事件时刻。[pdf:E03] [pdf:E04]

论文提供的正面证据只是 Boost 案例在 1、10、100 μs 三个步长下的波形对比，且 10 μs 表现较好；它没有报告 interpolation residual、局部曲率、事件时间误差，也没有说明何时可把两个近邻动作合并为同一时刻。因此这是基于 PDF 证据的批评，不是论文已证实的失败。[pdf:E05] [pdf:E06]

## § 10 — 最小复现实验

一周内可以只复现 Fig. 4 的 Boost 电路，不必复现完整 EMT 平台。用同一组参数：360 V、0.001 Ω、5 Ω、2 mH、两只 5 mF 电容、占空比 0.64、5 kHz；实现三种求解器：传统 linear interpolation、论文的 improved pipeline、以及 0.1 μs 或带精确事件定位的高分辨率 reference。论文只报告了 1、10、100 μs；0.1 μs reference 是复现实验的设计，不冒充原文设置。[pdf:E05]

测量四类量：每次自然换流的事件时间误差，动作前后电感电流与电容电压误差，\(P_{dc},U_A,I_1\) 的归一化波形误差，以及每仿真秒的积分/插值次数和墙钟时间。先复现 1、10、100 μs 三档，再扫 2、5、20、50 μs，找出误差开始突增的阈值。

若 improved method 在 10 μs 的事件时间和状态误差显著低于传统方法、接近 reference，且运行代价只增加到论文所述的局部额外操作量，就支持核心 claim；若只是视觉上接近、事件误差仍随步长快速增长，或实际运行代价抵消了大步长收益，就反驳“兼顾精度与效率”的强版本。

## § 11 — 最强反例设计

最有力的反例不是再换一个普通变换器，而是构造“高曲率、多事件、近时间尺度”工况：在 Boost 主回路加入弱阻尼寄生 LC，使自然换流附近出现高频振荡；再安排一次 forced turn-off 后，在同一 100 μs 步内连续触发二极管自然导通、自然关断和另一次受控动作。用精确事件求解器生成 ground truth，然后分别运行“逐个处理”和“按小时间常数合并近邻动作”的版本。

如果 linear interpolation 反复把零交叉定位到错误一侧，或合并动作改变了先后顺序，最终造成不守恒的能量跳变、漏检换流或误判 flameout，那么同一例子会同时攻击论文的两根支柱：相邻状态近似线性，以及足够接近的动作可视为同时发生。为了排除“只是步长太大”的替代解释，应在保持每步最多同样事件数的条件下逐渐降低振荡频率；若误差随局部曲率而不是只随 \(\Delta t\) 变化，反例才真正指向机制。

## § 12 — Follow-up Research Idea

在 EMT 数值算法领域，高影响结果通常不只看单一波形，而看事件时刻与状态误差、数值稳定性、计算代价、固定步实时约束，以及在多拓扑、多尺度和大系统上的可复现验证。本文只完成了小型 Boost 的定性波形验证，并明确说 large-scale performance 仍待研究。[pdf:E05] [pdf:E06]

**候选研究想法：把固定阈值的 interpolation recipe 改成“事件簇误差预算器”。** 它不预设所有近邻动作都可安全合并，而是在每个步内根据 interpolation residual、局部曲率、能量/电荷/磁链一致性和候选事件间隔，在线决定三件事：分别处理、作为一个 event cluster 联立处理，或局部缩短子步；对外仍在固定整步点输出。

（a）驱动需求是：论文没有给出“小时间常数”如何选，也无法判断 linear interpolation 何时失效。[pdf:E03] [pdf:E04]  
（b）研究价值在于把“较大固定步下看起来准确”改写成可检查的局部误差契约，并直接关联实时 EMT 的可预测计算预算。  
（c）可借鉴相邻领域的 hybrid-system event detection、embedded local error estimation 和守恒投影；这里是候选连接，未做外部文献检索，不声称 novelty。  
（d）第一个可证伪实验就是第 11 节的高曲率事件簇：若预算器不能在错误发生前触发分离或局部子步，或者触发后成本超过全程小步，它就失败。  
（e）与本文的实质区别是：本文给出固定的七步处理顺序和经验性近邻动作合并规则；新方向把“是否相信线性插值、是否合并事件”本身变成受物理残差约束的在线决策变量。

---

### PDF 证据缓存

- [pdf:E01] [`_evidence/E01-p001-abstract-related-work.png`](_evidence/E01-p001-abstract-related-work.png)：PDF 物理页 1，标题、摘要、研究背景与前人 interpolation 方法。
- [pdf:E02] [`_evidence/E02-p002-problem-fig01.png`](_evidence/E02-p002-problem-fig01.png)：PDF 物理页 2，既有方法限制、两类数值振荡与 Fig. 1 的动作延迟。
- [pdf:E03] [`_evidence/E03-p003-eq01-eq03-principles.png`](_evidence/E03-p003-eq01-eq03-principles.png)：PDF 物理页 3，式 (1)–(3)、reinitialization、resynchronization 与 multiple switching 定义。
- [pdf:E04] [`_evidence/E04-p004-method-reinitialization.png`](_evidence/E04-p004-method-reinitialization.png)：PDF 物理页 4，五项算法构件、状态重设、多动作合并假设与步骤 (1)–(2)。
- [pdf:E05] [`_evidence/E05-p005-pipeline-case-results.png`](_evidence/E05-p005-pipeline-case-results.png)：PDF 物理页 5，步骤 (3)–(7)、Fig. 3 pipeline、Fig. 4 Boost 参数、Fig. 5 波形比较。
- [pdf:E06] [`_evidence/E06-p006-results-limitations.png`](_evidence/E06-p006-results-limitations.png)：PDF 物理页 6，动作瞬间响应、结论、large-scale performance 限制与后续方向。

这些 PNG 保留整页上下文，便于核对段落、公式、图题、坐标与相邻论述；内容真相仍是 `_source.pdf`。
