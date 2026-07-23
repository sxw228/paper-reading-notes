# A Real-Time Simulation Model with Constant Admittance Matrix for Multiple Grid-Connected Converters System

- 作者：Mingwang Xu，Jiyuan Liu，Wei Gu，Yang Cao，Shuaixian Chen，Fei Zhang，Wei Liu，Yongming Tang，He Li
- 出处：IEEE Transactions on Power Electronics（作者接收稿）
- 年份：2025
- DOI：10.1109/TPEL.2025.3576605
- Zotero key：S2N95R33
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“如何把一个 VSC 算得更快”这么窄的问题，而是：当可再生能源站里有几十乃至上百个网联变流器时，能否同时满足三个通常互相冲突的要求——网络方程可并行、变流器端口没有人为的一步或半步延迟、FPGA 上仍能使用亚微秒级步长。作者给出的目标模型以 half-step prediction-correction 为核心，使变流器对外呈现恒定导纳，并把 ac 侧与 dc 侧无延迟解耦；摘要报告的规模是径向系统 130 台变流器、780 个开关器件、500 ns 步长，径向系统最小步长 80 ns，干线型系统 11 台变流器、66 个开关器件、500 ns 步长。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，是因为电磁暂态 real-time simulation（RTS）必须在真实墙钟时间内完成每一步。如果一个开关状态变化就迫使整网节点导纳矩阵重组、重新分解，或者为了并行而在接口上插入延迟，那么变流器数量、开关频率和网络耦合一增长，实时性、精度与稳定性就会同时承压。论文所瞄准的工程价值因此很具体：把“开关导致的快速内部变化”与“网络求解所看到的端口导纳”分开，使固定网络结构可复用，历史相关量并行更新，最后在同一时间步内闭合端口电压和电流。

这里的“恒定导纳”要准确理解：它不是说变流器的物理行为不再随开关变化，而是说节点求解器看到的本步电压—电流系数保持不变；开关状态、上一时刻储能状态和输入的影响被转移到 history source（历史源）中。这个区分是整篇论文的物理核心，也是它能把数值方法映射为固定矩阵—向量流水线的原因。[pdf:E03]（PDF 物理页 3，Eq. (11)–(15) 及其相邻正文）

## § 2 — 前人工作与不足

按照论文自己的相关工作梳理，已有路线可以分成三类。第一类是 transmission-line decoupling、MATE 和 node tearing：它们把大节点矩阵切成更小矩阵，减轻存储和计算，但主要面向 ac 网络，在多变流器系统上的效率仍不足。第二类是 latency insertion method（LIM）、基于 dc 电容慢动态的接口划分、以及基于储能元件高阶导数的电路分区：它们通过半步或一步接口延迟换取并行，但延迟会改变精度与稳定性，辅助 L/C 还可能改变被仿真的动态。第三类是 SSN、UCM、nodal analysis 和已有 delay-free 方法：它们能在不同程度上消除接口延迟或支持大系统，但节点分解中的电流—电压求解仍不完全并行，或者没有恒定导纳，或者需要串行求解两端口。[pdf:E01]（PDF 物理页 1，Introduction 的 decoupling 综述）[pdf:E02]（PDF 物理页 2，Introduction 的 SSN/UCM/constant-admittance 对比）

论文把不足压缩为两个直接瓶颈。其一，许多电路级解耦依赖半步或一步延迟，误差和允许步长随场景变化；其二，SSN 或 UCM 一类电路求解级解耦没有把计算拆到作者希望的粒度，硬件并行度仍可提高。作者还指出，SiC 器件把开关频率推向数百 kHz 时，RTS 步长可能需要进入几十 ns，这使每步重构大矩阵或增加接口延迟都更难接受。[pdf:E02]（PDF 物理页 2，Introduction 的 two limitations 与高频器件动机）

但这些比较应按论文证据的强度来读。论文确实在后文给出了若干平台、资源和步长表格，却没有在同一硬件、同一电路、同一精度阈值下重跑所有 prior methods。因此“已有方法为什么不够”在机制层面有清楚论证，在全体 benchmark 的公平排序上则仍受平台和模型口径差异限制。

## § 3 — 重建作者的思考路径

可以从一个实时求解器设计者会遇到的最短因果链重建这项工作。

1. 网联 VSC 的真实动态主要储存在 dc 侧电容电压和 ac 侧电感电流中，开关状态决定这些储能元件之间如何耦合。若直接用开关电阻构造全状态方程，状态矩阵的非对角耦合会随开关状态变化。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Eq. (1)–(4)）
2. 传统节点法希望每个元件在当前步写成“固定导纳 × 当前端口未知量 + 已知注入源”。如果能把开关相关项全部推入已知注入源，变流器对网络的导纳贡献就不必随 PWM 重组。
3. 单纯显式推进容易牺牲稳定域，单纯隐式推进又会把开关相关耦合带回当前步矩阵。于是作者把状态矩阵拆为固定的对角部分 \(A_\alpha\) 与随拓扑变化的非对角部分 \(A_\beta\)：固定部分走 trapezoidal correction，变化部分用半步预测值做 central integral。[pdf:E03]（PDF 物理页 3，Eq. (6)–(9)）
4. 这一离散化自然得到“当前端口未知量乘固定系数 \(Y\)，加上由上一时刻状态与输入形成的历史项”的 companion form。此时网络方程仍在 \(t+\Delta t\) 同一步求解，所以并行分区不需要在接口上借用 \(t\) 时刻旧值。
5. 一旦导纳固定，FPGA 就不必每步重新生成和分解任意矩阵；它只需按开关编码选取预存系数，用并行 dot-product pipeline 更新历史源，再让各节点子系统完成固定结构的求解。由此，数值拆分与硬件流水线结构彼此吻合。[pdf:E05]（PDF 物理页 5，Fig. 4 与 Solver Engine Design）

这条思考路径的关键不是先追求 80 ns，而是先改变“开关变化必须改变节点导纳矩阵”这一实现假设。纳秒级步长是这个结构变化在 FPGA 上兑现后的结果。

## § 4 — 核心 Intuition

把变流器拆成一副对网络永远相同的端口“骨架”和一个每步更新的 history source：固定骨架负责当前步的电压—电流闭合，历史源携带储能状态、输入与开关状态。这样，开关仍会改变物理响应，却不再迫使网络求解器重构导纳矩阵；ac、dc 子系统可以在同一时间步并行求解，而不是靠接口延迟互相等待。half-step prediction-correction 的作用，是让这个拆分同时保留较大的稳定域，而不是把所有变化都粗暴地显式化。

## § 5 — 具体方法与完整 Pipeline

以一个带 dc-link 电容、三相 ac 电感和六个功率开关的两电平 VSC 为例，单个仿真步从输入到输出如下。

1. **形成状态与端口量。** 状态取 dc 侧两个电容电压与 ac 侧三相电感电流，写成 \(x=[u_C^\mathsf{T},i_s^\mathsf{T}]^\mathsf{T}\)；外部端口输入由 dc 电流和 ac 端电压组成。开关用 \(R_\mathrm{on}/R_\mathrm{off}\) 电阻状态进入耦合矩阵，且同一桥臂电阻和 \(R_\mathrm{sum}=R_\mathrm{on}+R_\mathrm{off}\)。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Eq. (1)–(5)）
2. **半步预测。** 用当前 \(x_k,u_k\) 做半步显式预测 \(\hat{x}_{k+1/2}\)。这一步把当前开关状态造成的耦合先推进到中点。
3. **整步校正。** 将固定对角项 \(A_\alpha\) 以 trapezoidal 方式处理，将变化的非对角项 \(A_\beta\) 用中点预测值处理，得到
   \[
   x_{k+1}=M x_k+N u_k+Y u_{k+1}.
   \]
   \(M,N\) 吸收历史状态、已知输入和开关相关耦合，\(Y=\frac{\Delta t}{2}(I-\frac{\Delta t}{2}A_\alpha)^{-1}B\) 只由固定量决定。[pdf:E03]（PDF 物理页 3，Eq. (7)–(10)）
4. **生成 history source。** 定义 \(x_{\mathrm{his},k}=M x_k+N u_k\)，于是当前步端口关系变为 \(x_{k+1}=Y u_{k+1}+x_{\mathrm{his},k}\)。物理上，history source 是储能元件“记住的过去”在本步端口上的等效注入；它每步改变，导纳骨架不变。[pdf:E03]（PDF 物理页 3，Eq. (11)–(12)）
5. **同一步网络闭合。** dc 端口可写成电容 companion：
   \[
   u_{C,k+1}=\frac{\Delta t}{2C}i_{\mathrm{dc},k+1}+u_{\mathrm{his},k},
   \]
   ac 端口可写成电感 companion：
   \[
   i_{s,k+1}=\frac{\Delta t}{2L+\Delta t R_\mathrm{on}}u_{s,k+1}+i_{\mathrm{his},k}.
   \]
   对应固定等效电阻为 \(R_{\mathrm{eq},L}=(2L+\Delta t R_\mathrm{on})/\Delta t\) 与 \(R_{\mathrm{eq},C}=\Delta t/(2C)\)。网络求解器把这些固定导纳与外部网络拼接，在 \(k+1\) 步直接解出端口电压、电流；因为使用的是当前步未知量而不是上一时刻接口值，所以作者称其为 delay-free decoupling。[pdf:E03]（PDF 物理页 3，Eq. (13)–(15)）
6. **恢复内部量。** 得到端口量后，再由 Eq. (16)–(17)恢复桥臂开关电压和电流，因此模型不仅保留外部端口响应，也能输出内部电气量。[pdf:E04]（PDF 物理页 4，Eq. (17) 及其前后正文）
7. **扩展到多变流器。** 径向系统中，各 VSC 的 ac/dc companion 可拆成彼此并行的子系统；随着变流器数增加，独立 ac 支路可横向复制。干线型系统含变流器间 liaison line，ac 节点必须进入一个随节点数增长的联合网络求解，因此并行度和步长都不如径向系统。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Application in Multiple Grid-Connected Converters System）
8. **映射到 FPGA。** PWM carrier 与 modulation wave 产生三位开关编码；编码选择 BRAM 中预存的矩阵参数；dot-product pipeline 计算 history source；FSM 调度取数、MAC、输出，并把下一开关信号与矩阵参数读取和当前 dot product 的后半段重叠。硬件使用 Vivado 2023.2/Verilog；参数矩阵量化为 56 bit，正弦和锯齿波为 30 bit，非核心运算为 48 bit（24 个整数位），核心 dot product 为 64 bit（34 个整数位）。[pdf:E05]（PDF 物理页 5，Fig. 4、Solver Engine Design 与 FPGA Implementation）

这个 pipeline 的计算依赖很清楚：所有 history source 可先并行更新；只有共享电气节点的网络部分需要联合闭合。论文没有报告自适应步长，采用固定步长；也没有展示 floating-point FPGA 版本，而是用分层 fixed-point 位宽在误差和资源之间取舍。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 6.1 从物理状态到“固定项 + 开关项”

VSC 的 dc 电容满足 \(C\dot u_C=M_C i_s+i_{\mathrm{dc}}\)，ac 电感满足 \(L\dot i_s=-M_Lu_C-R_\mathrm{on}i_s+u_s\)。合并后是
\[
\dot x=Ax+Bu,\qquad
A=
\begin{bmatrix}
0&C^{-1}M_C\\
-L^{-1}M_L&-L^{-1}R_\mathrm{on}
\end{bmatrix}.
\]
\(M_C,M_L\) 随开关状态改变；\(C,L,R_\mathrm{on}\) 和输入映射 \(B\) 固定。[pdf:E02]（PDF 物理页 2，Eq. (1)–(5)）作者进一步把 \(A=A_\alpha+A_\beta\)：\(A_\alpha\) 是包含恒定导纳元素的对角部分，\(A_\beta\) 是包含变化导纳元素的非对角部分。[pdf:E03]（PDF 物理页 3，Eq. (6) 下方变量定义）

这个拆分的直觉是：对决定数值衰减和刚性的固定自项用隐式味道更强的 trapezoidal correction；对开关改变的交叉耦合，不让它进入当前步待求矩阵，而是使用半步预测值。这样既避免每个开关组合生成不同的当前步导纳，又比整步显式推进保留更大的稳定域。

### 6.2 预测—校正如何产生 history source

半步先算
\[
\hat{x}_{k+1/2}=
\left(I+\frac{\Delta t}{2}A\right)x_k+
\frac{\Delta t}{2}Bu_k.
\]
整步校正把 \(A_\alpha x\) 作 trapezoidal integration，把 \(A_\beta x\) 以中点 \(\hat{x}_{k+1/2}\) 作 central integration。整理后得到
\[
x_{k+1}=Mx_k+Nu_k+Yu_{k+1},
\]
其中
\[
Y=\frac{\Delta t}{2}
\left(I-\frac{\Delta t}{2}A_\alpha\right)^{-1}B.
\]
由于 \(A_\alpha,B,\Delta t\) 固定，\(Y\) 固定；开关相关的 \(A_\beta\) 留在 \(M,N\) 中。再定义
\[
x_{\mathrm{his},k}=Mx_k+Nu_k,
\]
便得到
\[
x_{k+1}=Y u_{k+1}+x_{\mathrm{his},k}.
\]
[pdf:E03]（PDF 物理页 3，Eq. (7)–(12)）

这一步解释了“恒定导纳”和“历史源”并不是两个平行技巧，而是一体两面：若不把随拓扑变化的贡献压进 \(x_{\mathrm{his}}\)，就无法保持 \(Y\) 恒定；若只保存历史源却不用 \(u_{k+1}\) 闭合，接口就会退化成时间延迟。

### 6.3 当前步网络闭合为何无接口延迟

以 ac 侧为例，三相电感端口在 \(k+1\) 写成
\[
i_{s,k+1}=G_Lu_{s,k+1}+i_{\mathrm{his},k},\qquad
G_L=\frac{\Delta t}{2L+\Delta t R_\mathrm{on}}.
\]
把所有变流器的 \(G_L\) 与外部线路导纳装入节点方程，右端是各自的 \(i_{\mathrm{his},k}\) 与独立源，求得的正是 \(u_{s,k+1}\)。再回代得到 \(i_{s,k+1}\)。因此闭环是
\[
\text{旧状态与本步开关}\rightarrow
\text{history source}\rightarrow
\text{同一步节点电压}\rightarrow
\text{同一步端口电流与新状态},
\]
而不是 \(u_{s,k}\rightarrow i_{s,k+1}\) 的一步延迟。只要外部网络拓扑和元件导纳也固定，整网矩阵的分解就可复用；即使外部网络另有变化，至少每台 VSC 的端口导纳贡献仍不因 PWM 状态而改变。

### 6.4 稳定域为什么扩大

论文用测试方程特征根 \(\lambda\) 比较 amplification factor。一步延迟方法为 \(|1+h\lambda|<1\)，modified Euler 为 \(|1+\lambda h/2+\lambda h(1+\lambda h)/2|<1\)，本文方法则多出分母：
\[
\left|
\frac{1+\lambda h/2+\lambda h(1+\lambda h)/2}
{1-\lambda h/2}
\right|<1.
\]
图示的本文稳定域沿负实轴扩展到约 \(-4\)，而前两者约到 \(-2\)。[pdf:E04]（PDF 物理页 4，Fig. 2 与 Eq. (18)–(20)）这个结果说明固定对角项的隐式校正提供了更强的数值阻尼；但它是基于线性测试方程的稳定域比较，不等于对任意开关事件、非线性器件和耦合网络的全局稳定性证明。

## § 7 — 实验设计与结论

- **问题：相对于一步延迟模型，本文模型在常规故障和大步长下是否更接近参考模型？** 实验：作者在 PSCAD/EMTDC 建立 10 kV、三台 P/Q 控制变流器的 reference model，三台分别向电网送出 5 MW、4 MW、10 MW；仿真步长 10 µs，设置 0.5–0.51 s 的 ac 母线 A 相接地故障和 0.9–0.95 s 的第三台变流器 dc 短路，并把 proposed model（PM）与 one-step delay model（DM）比较。[pdf:E06]（PDF 物理页 6，Fig. 5、Fig. 6、Table I）答案：波形上 PM 更接近 reference model；把步长放大到 50 µs 后，论文报告 DM 的 maximum relative error（MRE）大于 10%，PM 小于 4%，支持“优势在大步长时更明显”的 claim。[pdf:E07]（PDF 物理页 7，Large time-step simulation 与 Fig. 9）
- **问题：PM 是否只对离线参考模型有效，还是能逼近真实硬件？** 实验：物理样机采用 Imperix RCP、5 kHz 开关频率、V/F 控制，目标 20 V/50 Hz；dc 源 100 V、负载 20 Ω、dc 电容 1360 µF、ac 电感 5 mH。作者把负载电压参考从 20 V 改为 10 V，并测试一个上桥臂开关丢失 gate pulse 的故障。[pdf:E07]（PDF 物理页 7，Fig. 11–12 及 physical prototype 参数）答案：电压阶跃的峰峰值最大误差为 3.48%；丢脉冲时实验与仿真都出现 A 相正半周消失，说明模型捕获了该故障的主要波形机制。[pdf:E08]（PDF 物理页 8，Fig. 12–13 相邻正文）
- **问题：fixed-point FPGA 实现是否在亚微秒步长下保持精度？** 实验：XCKU060 上单台 VSC 以 500 ns（50 个 clock cycles）运行，与 PSCAD 比较 ac 出口电流和 dc 电压；另比较 time-step-first 与 resource-first 两种硬件策略。[pdf:E08]（PDF 物理页 8，Fig. 14 与 Table II）答案：MRE 分别为 0.45% 与 0.6%。100 MHz 下 time-step-first 使用 2593 LUT、2052 FF、35.5 BRAM、70 DSP，达到 80 ns；resource-first 使用 1316 LUT、1653 FF、35.5 BRAM、21 DSP，步长为 500 ns；150 MHz 的 time-step-first 单 VSC 可到 53 ns，但资源更多。
- **问题：多 VSC 的规模如何随网络拓扑和步长增长？** 实验：径向系统在 500 ns 下逐步增加到 130 台，在 80 ns 下增加到 40 台；干线系统同时测量资源占用与步长。[pdf:E09]（PDF 物理页 9，Table III、Fig. 17）答案：径向 130 台/500 ns 时 DSP 占用 98.91%，径向 40 台/80 ns 时 DSP 达到 100%；干线步长按 \(200+(N-1)\times30\) ns 增长，15 台时为 620 ns、DSP 89.78%，11 台时为 500 ns。干线 15 台的 dc 电压、电网 A 相电流、14–15 台间联络线 A 相电流 MRE 分别为 0.41%、0.86%、2.06%。[pdf:E09]（PDF 物理页 9，Fig. 17–18 及相邻正文）
- **问题：相对商业平台、nodal analysis 和既有 FPGA 方法，资源—步长—规模是否有优势？** 实验：作者汇总 RT-LAB、nodal analysis 和代表性 FPGA 工作的板卡、资源、规模和步长。[pdf:E10]（PDF 物理页 10，Table IV–VII）答案：表中本文达到径向 130 台/500 ns、径向 40 台/80 ns、干线 11 台/500 ns，而 RT-LAB 对应表项为径向 8 台、干线 6 台、1000 ns；与所列单 VSC 方法相比，本文 80 ns 的 LUT/FF/DSP 较低。这个答案支持“有 certain advantages”，但不是严格公平的同平台对照：板卡容量、时钟、模型细节和精度门槛不完全一致，不能把表格直接解释为普遍性能倍数。

实验链覆盖了离线仿真、物理样机和 FPGA RTS，这是论文证据较强的一面。不可外推的范围也很明确：物理样机只有单台 5 kHz VSC；多变流器验证主要是 FPGA 对 PSCAD，且硬件实现因外部控制器数字通道有限，让同一桥臂的多台变流器复用 PWM 信号。[pdf:E05]（PDF 物理页 5，FPGA Implementation 末段）论文以高频 SiC 和独立多变流器为动机，但没有物理展示大量独立控制、异步 PWM、器件寄生和硬件控制器闭环共同存在时的结果。

## § 8 — Take-aways

**5 句话：**  
1. 论文把随 PWM 变化的 VSC 动态拆成固定端口导纳与每步更新的 history source，使网络矩阵不再随开关状态重构。  
2. half-step predictor 处理变化耦合，trapezoidal corrector 处理固定自项，从而在保持 companion form 的同时扩大线性稳定域。  
3. 当前步端口未知量仍进入节点方程，所以 ac/dc 解耦来自代数重排，而不是接口时间延迟。  
4. 这一形式非常适合 FPGA：BRAM 存系数、开关编码选矩阵、dot-product pipeline 更新历史源，固定节点结构负责闭合。  
5. 三层实验支持其精度、资源和规模 claim，但证据集中在理想化开关电阻、固定 L/C、较低物理开关频率和 PWM 复用条件下。

**3 句话：**  
1. 真正的贡献不是一个更快的矩阵乘法器，而是把“拓扑变化”从网络导纳中搬到 causal history source。  
2. 这使径向多变流器可高度并行，而干线联络线仍会重新引入随节点数增长的全局 ac 网络闭合成本。  
3. 论文证明了这套结构在给定 VSC 与 FPGA 条件下有效，但尚未证明它能无损覆盖高频器件非线性、异步事件和参数变化。

**1 句话：**  
用固定导纳守住可复用的网络骨架，用历史源携带每台变流器的快速内部动态，是这篇论文把无延迟闭合、精度和 FPGA 并行放进同一个模型的核心。

## § 9 — 最脆弱的假设

最脆弱的假设是：**所有会随开关和运行状态改变、且对端口响应重要的动态，都能在一个固定步长内被压入显式可计算的 history source，而当前步端口系数仍可保持为由线性 \(L,C,R_\mathrm{on}\) 决定的固定导纳。**

这个假设一旦失效，论文的三个核心收益会一起受损。若器件的当前步端口斜率随电压、电流、温度或导通模式变化，节点方程看到的就不再是固定 \(Y\)；若死区、二极管换流、反向恢复、寄生电容、磁饱和或一个步长内发生的异步事件不能仅由 \(x_k,u_k\) 和离散 gate state 预测，history source 会用错误的能量和相位闭合本步；若改为迭代修正或切换导纳矩阵，又会丢掉作者所依赖的固定矩阵和低延迟。

论文对该假设提供的正面证据包括：线性 VSC 状态方程与 Eq. (11)–(15) 的代数推导、物理样机的电压阶跃与丢脉冲故障、以及 FPGA 对 PSCAD 的低 MRE。[pdf:E03]（PDF 物理页 3，Eq. (11)–(15)）[pdf:E08]（PDF 物理页 8，Fig. 12–14）缺少的证据是：数百 kHz SiC 级物理开关、独立异步 PWM、多台控制器闭环、显著参数漂移和器件非线性同时存在时，固定导纳是否仍能保持误差、能量一致性和多实例稳定性。作者的物理样机开关频率为 5 kHz，而多变流器 FPGA 测试又复用了 PWM，尚未直接覆盖动机中最苛刻的边界。

## § 10 — 最小复现实验

一周内最值得复现的不是 130 台 FPGA，而是“固定导纳 + history source 是否真的在大步长下比一步延迟更准，同时保持同一步网络闭合”。可以用 Python/NumPy 或任一 EMT 工具做一个单 VSC 接线性电网的双精度离线实验。

**数据与工况。** 采用论文物理样机参数作为小功率基线：100 V dc 源、20 Ω 负载、\(C=1360~\mu\mathrm{F}\)、\(L=5~\mathrm{mH}\)、5 kHz PWM、20 V/50 Hz V/F 输出，并加入 20 V→10 V 参考阶跃和单管 gate pulse 丢失；这些参数和扰动有物理样机证据。[pdf:E07]（PDF 物理页 7，physical prototype 参数）另加一个三相 ac 端短路，以观察强暂态。

**实现。**

1. 按 Eq. (5)–(15) 实现本文 half-step prediction-correction，每步记录 \(Y\) 和 \(x_\mathrm{his}\)。
2. 实现论文所比较的 one-step delay 接口模型。
3. 用步长至少小 20 倍的同一开关电阻模型作 reference；三种模型使用完全相同的 PWM 边沿、\(R_\mathrm{on}/R_\mathrm{off}\) 和初值。
4. 在 \(\Delta t=1,10,50~\mu\mathrm{s}\) 下比较负载电压、ac 电感电流、dc 电容电压、故障后恢复时间与离散能量偏差。

**测量与判据。** 首先检查所有开关组合下 \(Y\) 的数值是否逐元素不变，而 \(x_\mathrm{his}\) 随状态改变；这直接验证结构 claim。其次计算相对 reference 的 MRE/RMSE 和故障峰值误差。若 50 µs 下本文模型误差明显小于一步延迟，并达到论文所报告的 PM MRE 小于 4%、DM 大于 10% 的量级，同时无迭代、无矩阵重构，则最小复现支持核心 claim。[pdf:E07]（PDF 物理页 7，Large time-step simulation）若 \(Y\) 随开关变化、本文模型不比 delay baseline 更准、或强暂态中出现 reference 没有的数值能量增长，则核心 claim 在该实现中被反驳。FPGA 综合不是这次最小复现的必要条件，因为它不能替代对数值机制本身的验证。

## § 11 — 最强反例设计

最强反例应直接攻击“变化可以留在 history source，端口导纳仍固定”这一中心，而不是只换一块更小的 FPGA。构造一个弱阻尼干线网络，接入 8–16 台彼此独立、载波不同步的高开关频率 VSC；详细 reference model 显式包含 dead time、体二极管/反向恢复、器件输出电容、温度相关导通压降、饱和电感和 dc-link ESR。让多个 PWM 边沿在一个 80–500 ns 仿真步内错开，并在 liaison line 上施加短路清除与控制模式切换。

对照三种模型：论文的固定导纳 history-source 模型；允许按器件工作区更新端口 Jacobian/导纳并在当前步迭代闭合的模型；极小步长的详细开关 reference。攻击指标不只看单点 MRE，还看每步端口功率不平衡、故障后能量漂移、弱阻尼模态的衰减率、多实例增加时是否出现 reference 中没有的振荡，以及为维持稳定所需的最小步长。

若固定导纳模型在单台、同步 PWM 时仍准确，却在独立异步多实例中出现随台数增长的相位偏差或能量注入，而可变 Jacobian baseline 与 reference 一致，就得到一个有力替代解释：论文的规模结果可能来自“重复、规则的 history source 容易并行”，不等于固定导纳对真实异构多变流器仍成立。这个反例之所以强，是因为论文明确以高频器件和多变流器为动机，却在 FPGA 多机实现中让同桥臂多台变流器复用 PWM，[pdf:E05]（PDF 物理页 5，FPGA Implementation 末段）而干线系统已经显示联络线会压缩并行余量、使步长随 \(N\) 增长。[pdf:E09]（PDF 物理页 9，Fig. 17 及 \(200+(N-1)\times30\) ns 关系）

## § 12 — Follow-up Research Idea

**候选方向：具有可组合稳定性契约的“固定端口导纳 + 学习型 history source”。** 由于本任务没有跨论文检索，下面只提出可证伪的候选研究问题，不声称 novelty。

**(a) 未满足的需求。** 论文的固定导纳结构非常适合预分解网络和 FPGA 并行，但解析 history source 只覆盖所建模的线性 \(L,C,R\) 与离散开关耦合。真实器件的 dead time、寄生、饱和、温漂和未建模控制动态可能破坏这个闭合。需求不是“把神经网络加到现有求解器”，而是保持网络侧固定 \(Y_0\) 的可复用结构，同时让内部源项表达更丰富的历史依赖。

**(b) 可能的研究价值。** 把每台变流器定义为
\[
i_{k+1}=Y_0u_{k+1}+H_\theta(h_k,s_k),
\]
其中 \(H_\theta\) 只读取有限历史 \(h_k\)、gate/event 状态 \(s_k\) 与参数上下文，并满足显式的增益、被动性或耗散约束。研究目标从“单台波形拟合”改为“任意数量实例接入固定网络后仍可闭合、稳定和扩展”。如果成立，它会保留论文最有价值的固定矩阵骨架，同时覆盖解析 companion model 难以描述的内部动态；对 EMT/FPGA 领域的价值应由严格误差、实时步长、资源和多实例稳定性共同评价，而不是只看学习误差。

**(c) 可借鉴的方法或工具。** 可借鉴灰箱 system identification、state-space operator learning、被动性约束和小增益/耗散不等式，把物理 companion form 作为不可更改的端口层，把学习限制在 causal history source。训练数据可来自详细开关模型或少量硬件波形，但网络求解仍只看到固定 \(Y_0\)。

**(d) 第一个证伪实验。** 先在单台 VSC 的多工况数据上训练 \(H_\theta\)，然后不再训练，复制为 32 个参数略有差异、PWM 异步的实例，接入弱阻尼干线网络；同时加入训练中没有的 dc 故障与开关频率变化。若实例数增长后出现净能量生成、闭环不稳定、误差随网络耦合放大，或为了稳定不得不更新 \(Y_0\)/做全局迭代，则“固定导纳下可学习且可组合”被直接证伪。

**(e) 与本文的实质区别。** 本文从已知线性开关电路解析推导 \(M,N,Y\)，history source 是确定性离散公式；候选工作把“哪些内部动态必须显式建模”本身变为研究对象，并要求学习型源项提供跨实例、跨网络的稳定性契约。它改变的是端口模型的定义与验收目标，而不是在当前 FPGA pipeline 后面增加一个误差补偿模块。
