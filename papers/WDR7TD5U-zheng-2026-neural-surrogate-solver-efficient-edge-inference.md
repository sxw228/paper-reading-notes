# Neural Surrogate Solver for Efficient Edge Inference of Power Electronic Hybrid Dynamics

- 作者：Jialin Zheng, Haoyu Wang, Yangbin Zeng, Han Xu, Di Mou, Hong Li, Sergio Vazquez, Leopoldo G. Franquelo
- 出处：IEEE Transactions on Industrial Electronics, Vol. 73, No. 6
- 年份：2026
- DOI：10.1109/TIE.2025.3642411
- Zotero key：WDR7TD5U

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

题名、作者、出处、卷期、年份与 DOI 见源 PDF 题名页。[pdf:E01]（PDF 物理页 1，期刊页 9523）

## § 1 — 研究问题与重要性

这篇论文研究的不是“用 neural network 代替整个电力电子系统模型”，而是一个更窄、更工程化的问题：在资源受限的 edge hardware 上，怎样把电力电子系统的连续状态演化与离散开关事件一起快速算出来，同时保留足够的精度和确定的执行节拍。作者把这种任务称为 power electronic system（PES）的 hybrid dynamics inference。它是 HIL、digital twin 和 MPC 的底层能力；困难在于数字控制产生的开关事件会改变电路拓扑，而电感电流、电容电压又在事件之间连续演化，所以求解器既要及时更新离散模型，又要准确积分连续状态。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction，期刊页 9523）

工程瓶颈来自两个方向。固定小步长方法容易在 FPGA 上并行，但为了捕捉事件可能需要极小的 submicrosecond 步长，计算和资源成本随之上升；高阶 variable-step 或 event-driven 方法减少了无意义的步数，却引入矩阵更新、多个串行积分 stage 和波动的执行时间。作者因此把目标定成三者的同时改善：实时性、数值精度和 edge resource consumption，而不是只追求离线仿真的平均速度。[pdf:E01]（PDF 物理页 1，Introduction 右栏）

论文的直接价值在于：如果高保真状态推演可以在 converter 旁边稳定运行，它就不仅能服务 HIL，还能进入闭环控制。作者的案例确实把求解器部署到 Xilinx FPGA，并进一步把 NSS 的状态估计接入 DAB 的 MPC；但这项价值目前只在一个两级 dc-dc converter 案例中展示，不能直接外推到任意拓扑或实物参数漂移场景。[pdf:E05][pdf:E06]（PDF 物理页 5–6，Fig. 5、Fig. 8 与 Hardware Implementation and Application）

## § 2 — 前人工作与不足

论文把既有数值路线分为两类。第一类是 FPGA 友好的 fixed-step 低阶求解：文中点名 50 ns predictor-corrector FPGA 模型和避免开关时重分解 admittance matrix 的 MANA 路线。它们的优势是时序规则、硬件并行直观；不足不是“精度低”这么简单，而是为了正确覆盖开关事件和 stiff dynamics，往往必须持续用很小的步长更新系统模型，矩阵运算和硬件占用都很重。[pdf:E01]（PDF 物理页 1，Introduction）

第二类是 adaptive Runge-Kutta 与 event-driven solver（EDS）。它们通过 local error estimate 或直接对齐事件来减少积分次数，但 step size 与计算时长都会随工况变化，高阶算法还包含串行 stage，难以给 FPGA 留出稳定的 worst-case timing margin。作者据此判断，传统数值方法在 real-time capability、accuracy 与 edge resource 之间存在结构性 trade-off。[pdf:E02]（PDF 物理页 2，Introduction 左栏）

ML 路线已经有 PINN、FNO、neural ODE，以及针对 IGBT switching transient 或电路 topology 的 NN/GNN 方法。论文的判断是：这些方法主要处理 continuous dynamics、smooth ODE/PDE 或直接的系统建模，没有专门拆解“离散事件触发的模型更新”和“事件间连续积分”这两个在线求解瓶颈。NSS 的差异因此不是首次把 NN 用到 power electronics，而是把两个轻量 NN 嵌入 event-driven numerical solver：一个近似开关配置到系统矩阵变化的映射，另一个近似低阶积分器的高阶截断误差。[pdf:E02]（PDF 物理页 2，Introduction 与 contributions）

需要保留一个证据边界：论文引用了上述 prior work，但没有在实验中实现 PINN、FNO、GNN 或 neural ODE baseline；实际 benchmark 是 ODE1/2/4、ODE23/45、DOPRI、EDS 及其 FPGA 版本。因此，“NSS 优于既有 ML solver”不是本文实验闭合的结论。[pdf:E05]（PDF 物理页 5，Table II）

## § 3 — 重建作者的思考路径

以下是基于论文背景与公式的重建，不是作者逐字陈述。

第一步，从 hybrid PES 的结构出发：第 \(k\) 个事件区间内，电路可以写成由开关向量 \(K_k\) 决定的线性时不变系统；事件到来时需要更新 \(A_k,B_k\)，事件之间则需要数值积分。传统 EDS 已经负责定位下一个事件并给出 \(K_k\) 与 \(h_n\)，所以没有必要重新学习 event scheduler。[pdf:E02]（PDF 物理页 2，Fig. 1、Eq. (1)–(3) 与 Event-Driven Dynamics Inference）

第二步，观察 EDS 的重成本不是均匀分布的，而是集中在两个可替换模块：由 \(K_k\) 在线做 matrix multiplication/inversion 以产生系统矩阵，以及为了高精度反复执行高阶积分 stage。前者是离散配置到矩阵的静态非线性映射，后者可以改写为“低阶一步结果 + 可学习 residual”。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Eq. (3)、Fig. 2 与 Eq. (4)–(7)）

第三步，选择两个小 MLP，而不是一个端到端 trajectory predictor。这样，event scheduler、base solver 和状态方程仍保留显式物理角色；NN 只替换最昂贵的矩阵生成与 truncation-error correction。这个拆分也自然对应 FPGA 的 matrix-vector multiply：权重矩阵各行可以并行做 dot product，激活函数由 multithreshold unit 完成。[pdf:E04]（PDF 物理页 4，Fig. 3–4 与 Parallel Neural Processing Units）

第四步，训练顺序也由依赖关系决定。先让 \(f_\theta\) 学会矩阵变化并冻结，再用它生成 \(g_\phi\) 所见的 solver input，以 DOPRI 的高精度轨迹构造低阶 base solver 的 normalized residual。这里的关键思想不是让两个 NN 互相补偿，而是让第二个网络在第一个网络已经固定的误差环境中学习。[pdf:E04]（PDF 物理页 4，Eq. (9)–(11) 与 Training Strategy）

## § 4 — 核心 Intuition

NSS 的核心直觉是：保留 event-driven framework 对开关时刻的组织能力，但把每次事件后的昂贵矩阵重算，换成从开关配置到矩阵增量的一次 NN forward；再把高阶求解器的多 stage 串行计算，换成“低阶一步 + NN 预测的高阶 residual”。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Eq. (5)–(7)）

这两种替换最终都落成规则的 matrix-vector multiplication，因而比传统求解器更适合用 FPGA 空间并行换取固定而短的执行时间。它仍是一个带显式 event scheduler 和 base solver 的 numerical solver，不是脱离物理模型直接猜整段波形的黑盒。[pdf:E04]（PDF 物理页 4，Fig. 3–4）

## § 5 — 具体方法与完整 Pipeline

以论文的两级 dc-dc converter 为例，在线 pipeline 如下。

1. **事件调度。** 沿用 EDS 定位下一开关事件，得到当前 switch configuration \(K_k\) 和事件间隔 \(h_n=t_{n+1}-t_n\)。论文没有用 NN 预测事件时刻。[pdf:E02][pdf:E03]（PDF 物理页 2–3，Event-Driven Dynamics Inference 与 Fig. 2）
2. **离散模型更新。** \(K_k\) 的每个 categorical switch state 先 one-hot encoding，再拼成 \(3d\) 维输入；model network \(f_\theta\) 输出 \(\Delta A_{k,\theta},\Delta B_{k,\theta}\)，与常量矩阵 \(A_0,B_0\) 合成当前状态方程。训练标签来自用 Eq. (3) 对采样的 \(K_k\) 做精确矩阵生成，loss 是两个矩阵预测误差的 Frobenius-norm MSE。[pdf:E03]（PDF 物理页 3，Eq. (5)、(6)、(8) 与 Model Network Design）
3. **低阶时间推进。** base solver 用当前状态、输入、模型矩阵和 \(h_n\) 先计算一个 explicit low-order step。一般形式允许 variable-step Euler 或 Heun；实际 case 的 benchmark 把 NSS 标成“1st + NN”，也就是一阶 base solver 加 neural correction。[pdf:E03][pdf:E05]（PDF 物理页 3、5，Eq. (7) 与 Table II）
4. **连续误差修正。** solver network \(g_\phi\) 根据 solver input 预测 normalized high-order residual，乘回 \(h_n^{p+1}\) 后加到 base result，得到 \(x_{n+1}\)。训练时用 DOPRI reference 与 base one-step prediction 的差构造监督信号。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Eq. (7)、(9)–(11)）
5. **FPGA 映射。** \(f_\theta\) 和 \(g_\phi\) 各实例化一个 NPU；权重矩阵不同行由多个 dot-product units 并行处理，单个 dot product 内又并行处理 vector elements。训练模型从 PyTorch/TensorFlow 导出为 ONNX，量化后经 HLS4ML 转为 synthesizable C/C++，再集成为 RTL IP。两个 NPU 仍按 \(f_\theta\) → base solver → \(g_\phi\) 的系统级顺序执行。[pdf:E04]（PDF 物理页 4，Fig. 4 与 NPU implementation）

案例的物理系统是 25 kHz DAB 加四路并联 200 kHz Buck，部署在 Xilinx XCZU5EV 平台。\(NN_{\text{model}}\) 把 24 维 one-hot switch vector 映射成 110 个矩阵元素，hidden layers 为 64、64，使用 ReLU；\(NN_{\text{solver}}\) 把 122 维 solver bus 映射到 10 维 residual，hidden layers 为 128、128，使用 Tanh。122 维输入由向量化的 \(A_k\) 100 维、\(B_k\) 10 维、state 10 维、input 1 维和 step size 1 维组成。[pdf:E05]（PDF 物理页 5，Fig. 5 与 NSS Training）

训练数据方面，model network 使用 256 个 unique mappings，solver network 使用 DOPRI 生成的 512,000 条 trajectories；数据按 70%/20%/10% 划分。两网都用 Adam 与 MSE，batch size 分别为 64 和 256，最大 epoch 分别为 100 和 200，并采用 early stopping。[pdf:E05]（PDF 物理页 5，Table I 与 NSS Training）

数值表示方面，论文只报告“quantized”以及 HLS4ML/RTL 流程，没有报告定点位宽、scale、rounding、overflow policy，也没有给出量化前后误差。因此这些实现细节必须标记为未报告，不能从资源表倒推出数值格式。[pdf:E04]（PDF 物理页 4，Parallel Neural Processing Units）

## § 6 — 核心数学推导

### 6.1 Hybrid dynamics 的分段模型

一般 PES 写成

\[
\dot{x}(t)=f(t,x(t),u(t)).
\]

在相邻开关事件之间，拓扑不变，作者把它写成

\[
\dot{x}(t)=A_kx(t)+B_ku(t),
\]

而 \(A_k,B_k\) 由常量电路矩阵与 \(K_k\in\{-1,0,1\}^d\) 组合，其中包含 \((I-D_1K_k)^{-1}\)。工程上，这说明“开关状态变化”最终表现为系统矩阵变化，也解释了为什么在线 matrix inversion 是瓶颈。[pdf:E02]（PDF 物理页 2，Eq. (1)–(3)）

### 6.2 把矩阵生成改写成 learned mapping

作者把随 \(K_k\) 变化的部分抽成

\[
f_\theta(K_k)=(\Delta A_{k,\theta},\Delta B_{k,\theta}),
\]

从而使用

\[
\dot{x}\approx(A_0+\Delta A_{k,\theta})x+(B_0+\Delta B_{k,\theta})u.
\]

这不是学习完整 \(A_k,B_k\) 的任意函数，而是保留常量部分、只预测 topology-dependent variations。其监督 loss 对 \(\Delta A_k,\Delta B_k\) 分别使用 Frobenius norm 的平方再取样本平均。[pdf:E03]（PDF 物理页 3，Eq. (5)、(6)、(8)）

### 6.3 把高阶积分改写成 residual correction

传统 \(p\) 阶一步积分写作

\[
x_{n+1}\approx x_n+h_n\psi^p(t,x_n,u_n,K_k).
\]

NSS 则采用低阶 base update \(\psi^1\)，再添加 neural residual：

\[
x_{n+1}\approx x_n+h_n\psi^1(\cdots;A_k,B_k)+h_n^{p+1}g_\phi(\xi_{n-1}).
\]

这里 \(h_n^{p+1}\) 很关键：一个 \(p\) 阶方法的 principal local truncation error 按该量级缩放，网络学习的是把步长幂次除掉后的 residual，而不是把不同步长下的绝对误差混在一起。[pdf:E03]（PDF 物理页 3，Eq. (4)、(7)）

训练时先用 reference state 做 base one-step prediction：

\[
x_{n,\mathrm{base}}=x_{n-1,\mathrm{ref}}+
h_n\psi(t_{n-1},x_{n-1,\mathrm{ref}},u_{n-1},K_k),
\]

再定义

\[
R_n=\frac{x_{n,\mathrm{ref}}-x_{n,\mathrm{base}}}{h_n^{p+1}},
\qquad
L_g=\frac{1}{M}\sum_{n=1}^{M}
\lVert R_n-g_\phi(\xi_{n-1})\rVert_2^2.
\]

因此，若 \(g_\phi\) 精确预测 \(R_n\)，乘回 \(h_n^{p+1}\) 后正好补上 base solver 对 reference 的单步误差。论文的“接近高阶 solver 精度”是由这种 residual fitting 提供机制解释，但论文没有给出全局误差界、stability proof 或对任意 \(h_n\) 的外推保证。[pdf:E04]（PDF 物理页 4，Eq. (9)–(11)）

## § 7 — 实验设计与结论

**问题 1：在未用于训练的动态开关过程中，NSS 能否保持 trajectory accuracy？** 作者用 steady-state data 训练后，在 dynamic process 上比较 NSS 与 DOPRI。Fig. 6(a) 的电流波形和 zoom-in 显示两者高度贴合，NSS 只在 switching instants 计算。[pdf:E05]（PDF 物理页 5，Fig. 6(a) 与 Inference Accuracy）答案是定性支持，但图中没有报告 RMSE、maximum event error 或长期累积误差，所以不能把“贴合”改写成一个未给出的精确误差值。

**问题 2：速度提升来自算法还是 FPGA？** 作者对每个 solver 重复 100 次仿真 10 s dynamic process，并比较 average computation time 与 relative error。CPU 上 NSS 相对同平台 EDS 快 3.2 倍；FPGA 对 NN computation 再给出 7.2 倍加速，合成约 \(3.2\times7.2\approx23\) 倍的 F-NSS 对 CPU EDS 速度提升。作者同时指出，该 EDS 对本问题已经约比 ODE45 快 10 倍。[pdf:E05]（PDF 物理页 5，Fig. 6(b)、Table II 与 Pareto Efficiency）这个 23 倍不是同一硬件上的单因素比较，而是 algorithmic gain 与 cross-platform hardware gain 的乘积，解读时必须保留这点。

**问题 3：单步执行时间是否更稳定？** Fig. 7(a) 比较 single-cycle call time；DOPRI 和 EDS 有波动，NSS 接近 fixed-step solver 的常量时间，并比 ODE4 低 89.2%。[pdf:E05]（PDF 物理页 5，Fig. 7(a) 与 Single-Step Time Stability）这支持更容易留 timing margin，但论文没有报告完整 latency distribution、worst-case percentile 或不同 FPGA clock 下的复测。

**问题 4：FPGA 资源是否下降？** 相对 ODE4 baseline，NSS 的 DSP48/BRAM/LUT utilization 分别为 26.0%/15.0%/22.0%，而 ODE4 为 94.6%/34.7%/62.9%；对应 reduction 为 72.5%、56.8%、65.0%，作者汇总为约 60% overall resource saving。[pdf:E06]（PDF 物理页 6，Table III）这组数据支持在同一 FPGA 上为 control logic 留出空间，但没有包含功耗、时钟频率、routing congestion 或不同 quantization bit width 的敏感性。

**问题 5：推演结果能否真正进入控制闭环？** 作者用 NSS 替代 DAB 的 high-bandwidth current sensors，并接入 MPC。Fig. 8 显示 NSS-based MPC 在一次 switching cycle 内到达新 steady state，而传统 PI 为 7 cycles。[pdf:E06]（PDF 物理页 6，Fig. 8 与 Application in MPC）这是一个有吸引力的 application demonstration，但 PI 与 MPC 本身就是不同 controller；因此该实验不能把全部 transient improvement 唯一归因于 NSS，也没有隔离“理想传感器 MPC”与“NSS 估计 MPC”的差别。

总体上，实验闭合了“在给定模型、给定 converter、给定训练分布和给定 FPGA 上，双 NN surrogate 可以同时降低平均计算时间与资源占用”的案例 claim；它没有闭合跨拓扑泛化、器件非线性、参数漂移、measurement noise、sim-to-real robustness 或形式化 numerical stability。作者自己也明确说明，案例使用 known high-fidelity model 来隔离 solver acceleration，robust surrogate modeling 与 sim-to-real generalization 留待未来工作。[pdf:E06]（PDF 物理页 6，scope clarification）

## § 8 — Take-aways

### 5 句话

1. NSS 保留 event-driven scheduling 与显式 base solver，只用两个 NN 代理矩阵更新和高阶误差修正这两个串行瓶颈。[pdf:E03]
2. \(f_\theta\) 学 switch configuration 到 matrix variation，\(g_\phi\) 学 DOPRI reference 相对低阶一步解的 normalized residual。[pdf:E03][pdf:E04]
3. 两个 NN 都能落成高度并行的 matrix-vector computation，并通过双 NPU 在 FPGA 上顺序流水执行。[pdf:E04]
4. 单一两级 dc-dc 案例报告相对 CPU EDS 的 23 倍组合速度提升、相对 ODE4 的约 60% overall resource saving，以及更稳定的单步计算时间。[pdf:E05][pdf:E06]
5. 结果证明了 solver acceleration 的工程可行性，但没有证明跨模型或 sim-to-real robustness；论文也把后者明确留作未来方向。[pdf:E06]

### 3 句话

NSS 把 hybrid solver 中最昂贵的两个计算块改写成轻量 NN forward，同时不丢掉 event scheduler 和物理状态推进结构。[pdf:E03] 它在一个 Xilinx FPGA 的两级 dc-dc 案例中给出了速度、资源和闭环应用证据。[pdf:E05][pdf:E06] 最重要的阅读边界是：这是一篇 solver acceleration 论文，不是一篇已经解决 model mismatch 与 sim-to-real generalization 的端到端 digital twin 论文。[pdf:E06]

### 1 句话

这篇论文证明“NN 可以做 numerical solver 内部的硬件友好代理”，但尚未证明这个代理在真实模型偏差和分布外事件下仍可靠。

## § 9 — 最脆弱的假设

最脆弱的假设是：部署时遇到的 \(K_k\)、state、input、step size 以及真实系统参数所诱导的 matrix variation 和 truncation residual，与训练数据覆盖的是同一映射或足够接近的分布。若它不成立，\(f_\theta\) 会生成错误的 \(A_k,B_k\)，\(g_\phi\) 又可能在同一步继续给出错误 correction；两种误差会沿 event-to-event 状态递推积累。此时，即使 FPGA latency 很短、resource utilization 很低，核心的“high-fidelity dynamics inference”仍会直接失效。

论文给出的支持是：model network 覆盖 256 个 unique mappings，solver network 有 512,000 条 DOPRI trajectories，并用独立 dynamic process 展示了 waveform match。[pdf:E05]（PDF 物理页 5，NSS Training 与 Fig. 6）但证据缺口更关键：所有 reference 都由 known high-fidelity model 生成，案例没有注入 component tolerance、温漂、磁饱和、dead time、measurement noise 或 unseen topology；作者也明确把 robust surrogate model 与 sim-to-real generalization 留作未来组合。[pdf:E06]（PDF 物理页 6，scope clarification）

因此，“训练分布足以覆盖实际 hybrid dynamics”只是该案例成立所依赖的假设，不是论文已经普遍证明的事实。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 FPGA 资源表，而是 NSS 的核心机制：**在 event-aligned 的相同步长下，低阶积分器加 learned residual，能否以稳定的一步计算代价逼近 DOPRI。**

可以选一个有 2–4 个开关模式、状态维数较小的 switched RLC 或简化 DAB 平均/分段状态空间模型：

1. 枚举或采样 \(K_k\)，由精确电路公式生成 \(A_k,B_k\)，训练一个小 \(f_\theta\)；
2. 用 DOPRI 在多组 duty cycle、负载和 event interval 上生成 reference trajectories；
3. 按 Eq. (9)–(10) 构造 Euler one-step normalized residual，训练 \(g_\phi\)；
4. 在完全 withheld 的 switching sequences 与 step-size range 上比较 Euler、Euler+\(g_\phi\)、DOPRI；
5. 测量 event-point RMSE、maximum error、1000 个连续事件后的累积误差，以及每一步 wall-clock latency 的 median 和 maximum。

若 Euler+\(g_\phi\) 在相同 event-aligned \(h_n\) 下把 error 明显压向 DOPRI，同时 latency 比 DOPRI 更低且更稳定，就支持论文最核心的算法 claim；若只在随机划分的同分布样本上有效、换 switching sequence 或稍扩大 \(h_n\) 就出现累积发散，则反驳其可作为通用 hybrid solver surrogate 的强解读。这个最小实验不能验证论文的 23 倍 FPGA speedup 或 60% resource saving，因为那些结论还依赖特定 HLS、量化、时钟和 XCZU5EV implementation。[pdf:E04][pdf:E05][pdf:E06]

## § 11 — 最强反例设计

最有力的反例不是再换一个普通 converter，而是制造一个 **\(K_k\) 看起来相同、真实连续动力学却发生系统性变化** 的场景。具体做法是：沿用训练过的 converter 与控制序列，在测试时同时加入电感饱和导致的 state-dependent inductance、温升引起的 resistance drift、dead time 与负载突变，并安排短时间内密集或近同时发生的 switching events。\(f_\theta\) 的输入仍只有 \(K_k\)，因此它无法从输入中辨认这些隐藏参数变化；\(g_\phi\) 也只在 known-model DOPRI trajectories 上学过 residual。[pdf:E03][pdf:E05][pdf:E06]

实验应比较四组：真实参数的 DOPRI、nominal-model EDS、nominal NSS、带在线参数/误差修正的 oracle baseline。攻击成功的判据不是“误差稍大”，而是 NSS 的 event-point error 相对 nominal EDS 更快累积，或其状态估计使 MPC 不再保持一次 switching cycle 的稳定过渡，而 latency 与 resource 优势仍然存在。这样可以排除“只是控制器调参不好”的替代解释，直接检验 learned matrix mapping 与 residual correction 是否把 nominal-model bias 放大。

若 NSS 在明确未训练的 parameter shift 与 dense events 下仍能维持 bounded error，论文的核心机制会得到更强支持；若失败，则说明当前 23 倍与 60% 是以未验证的 distribution coverage 换来的，而不是无条件的 solver improvement。这是基于论文输入结构与案例范围的推断，不是作者已经报告的实验结论。

## § 12 — Follow-up Research Idea

### 候选方向：带运行时误差证书的 deadline-guaranteed hybrid solver

电力电子与控制领域的高影响工作通常不只看平均 benchmark，还看 numerical stability、worst-case timing、硬件可实现性、跨工况复现和闭环安全价值。本文已经把推演做得快且资源友好，但最关键的未满足需求是：edge controller 不知道当前 NN correction 是否仍处于可信分布，也不知道错误何时会跨过闭环安全边界。

候选研究目标可以从“让 NN 更准确”改成“在固定 deadline 内，同时输出状态推进与可校准的 local error certificate；证书失效时，切换到有界代价的保守积分/局部重校准”。这不是给 NSS 再叠一个 accuracy module，而是把求解器的输出定义从 point estimate 改成 **state + validity bound + deadline contract**。可借鉴相邻领域的 reachability、a posteriori error estimation、conformal calibration 和 anytime computation，把 event interval、parameter uncertainty 与 quantization error 一起纳入证书；FPGA 端只保留能在 deadline 内执行的轻量 bound propagation。

第一个能证伪它的实验是：在 withheld topology、component drift、dead time、noise 与 dense-event 组合下，检查证书是否同时满足两件事——真实一步误差落在声明 bound 内的频率达到预设 coverage，且 fallback 后 worst-case latency 不越过控制 deadline。如果 bound 经常漏报，或者 fallback 使实时性消失，这个方向就失败。

它与本文的实质区别在于，本文优化 nominal known-model 下的速度、资源和 average accuracy，并未提供 error bound 或 sim-to-real guarantee。[pdf:E05][pdf:E06] 新方向把“何时可以信任 neural surrogate”变成首要研究问题，并把 failure observability 纳入硬件接口。由于本卡未对 certified neural ODE、hybrid reachability 与 conformal time-series solver 做充分相关工作检索，这里只把它标为候选想法，不声称 novelty。
