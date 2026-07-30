# Fast Transient Simulation of System-Level Power Delivery Networks via Parallel Waveform Relaxation

作者：Alessandro Moglia、Antonio Carlucci、Stefano Grivet-Talocia、Siddharth Kulasekaran、Kaladhar Radhakrishnan  
出处：IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 15, No. 1  
年份：2025  
DOI：10.1109/TCPMT.2024.3410146  
Zotero key：2QU5U53K  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文解决的是一个 post-layout power integrity（PI）验证问题：当多核处理器的 PCB、封装、芯片 PDN、去耦器件、每核 fully integrated voltage regulator（FIVR）及其反馈控制都已经确定后，如何在 realistic current stimuli 下快速完成高精度瞬态仿真，确认所有供电电压仍处于规定范围。作者面向的不是几个局部器件，而是带几十乃至上百个 core、每核独立稳压回路、并嵌入电磁场求解器所产生 interconnect macromodel 的整机级 PDN；论文直接声称传统 SPICE 路线在此规模上过慢或不收敛，并报告其并行 WR 实现最多使用 60 个计算线程。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

Fig. 1 给出的对象可读成三层：共享输入网络 \(G_1\) 把平台电压送到各核；每核有开关等效块 \(S_k\)、输出网络 \(G_{2;k}\)、控制器 \(K_k\) 和负载电流源；不同 core 既通过共享 \(G_1\) 相互耦合，又各自形成闭环稳压。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II 开头）这使问题的重要性不只是“矩阵很大”：电磁互连带来大量动态状态，多个闭环和负载瞬态又要求长时间步进，而设计者真正关心的是所有端口、所有时刻的最坏电压偏差。

边界必须说清：这篇论文研究的是 CPU 上的 PDN transient circuit simulation。它没有报告电磁暂态（EMT）电网求解器、FPGA 映射、硬实时步长或开关级功率电子实现，因此不能把“瞬态仿真很快”外推成“已经实现 EMT/FPGA 实时仿真”。

## § 2 — 前人工作与不足

论文把已有路线分成两类。第一类把少量局部非线性嵌入 full-wave electromagnetic solver；作者认为它适合特殊案例，但难以同时覆盖 PCB、封装和芯片的多尺度整机互连。第二类先由频域场求解得到 scattering response，再用 passive rational fitting 转成 SPICE 可用的 behavioral circuit；这已经是 PI 的标准流程，但把大规模 interconnect state-space model、FIVR 控制和负载一起交给通用电路求解器，仍然会遭遇状态规模、非线性和时间推进的复合成本。[pdf:E01]（PDF 物理页 1，Section I）

作为本文的直接参考，作者使用两种“未分区”解：工业 HSPICE，以及对完整方程组 (1) 采用固定步长 implicit Euler 的直接积分。后者利用控制延迟 \(T_k\geq\delta t\)，把当前步的 duty cycle 当作已由历史样本确定的量，从而每一步只解系数矩阵不变的线性系统并预先做 LU factorization。[pdf:E03]（PDF 物理页 3，Eq. (1c)–(3) 与 Section II-A）这说明本文并不是用新积分格式替代旧积分格式，而是在相同离散模型上改变求解依赖。

WR 本身也不是本文原创。作者明确把论文定位为 application paper：LP、TP 和二者组合的 LPTP 分别借鉴既有 interconnect/SI waveform relaxation 工作，再针对具有多组电压反馈回路的 PI 拓扑定制。此前工作的缺口不是“没人知道 WR”，而是没有说明如何为这种共享输入 PDN 加每核闭环的结构选择 partition、怎样组织 state-space realization 才能真正降低每个分区的成本，以及怎样在共享内存 CPU 上取得可观的端到端加速。[pdf:E04]（PDF 物理页 4，Section III、Eq. (4)–(11)）

## § 3 — 重建作者的思考路径

以下是基于论文结构重建的思路，不是作者逐句陈述的发明史。

第一步，先把系统写成两个可组合 operator：共享输入网络 \(G_1\) 把各核输入电流映射为各核输入电压，每核子系统 \(C_k\) 则把本核输入电压与负载电流映射为开关输入电流和输出电压。由于 \(G_{2;k}\)、控制器和 averaged FIVR 按 core 分组，最自然的并行单位就是一个 core。

第二步，观察接口的物理阻抗关系。论文称 \(G_1\) 输出阻抗约为 \(1\,\mathrm{m}\Omega\)，而 core 子网输入阻抗约为 \(1\,\mathrm{k}\Omega\)；因此用 ideal voltage source 驱动 core、用 ideal current source 驱动输入网络的 longitudinal decoupling 接近阻抗匹配意义下的好选择。[pdf:E05]（PDF 物理页 5，Fig. 2、Eq. (10)–(12) 与 Section III-D）

第三步，用 Gauss–Jacobi WR 把被切断的接口量作为上一轮 waveform 的 relaxation source。这样每个分区可对整个时间窗独立前进，之后再交换完整波形；代价是同一窗口需反复求解，收益是分区之间没有本轮数据依赖。作者没有采用通常收敛更快的 Gauss–Seidel，因为其顺序依赖会破坏完全并行；较长仿真可进一步用 windowing，但本文实验时间窗未使用该优化。[pdf:E06]（PDF 物理页 6，Section III-D 与 IV-A）

第四步，意识到“画出了分区”并不等于“算得更少”。若标准 state-space realization 中每个输入都激励全部状态，则计算一个阻抗子块与计算完整阻抗矩阵的主成本近似相同。于是作者把问题从单纯的 circuit partition 推进到 model realization：通过频率采样、vector fitting 和 passivity enforcement 构造 block-diagonal multi-SIMO realization，使每个输入只激励自己的状态块，TP 才能把真正较小的子模型交给不同线程。[pdf:E08]（PDF 物理页 8，Fig. 5、Eq. (16)–(21)）

这条思考链的关键转折是：并行效率由“被切断的电路拓扑”和“模型内部状态结构”共同决定，而不是由 core 数或线程数单独决定。

## § 4 — 核心 Intuition

把跨分区耦合暂时当作上一轮已经知道的整段波形，每个 core 就能在本轮独立求解；只要被滞后的耦合足够弱，几轮迭代就能恢复原耦合系统的解。真正让并行有效的不是 WR 这个标签，而是把 \(G_1\) 变成 multi-SIMO block realization，使“每核一个线程”同时意味着“每核只计算一小块状态”。因此这是一种用少量重复迭代换取大规模并行、并用模型结构避免每个分区仍背负全局成本的方法。

## § 5 — 具体方法与完整 Pipeline

以一个共享输入 PDN、多个受控 core 子系统和分段阶跃负载为例，完整 pipeline 如下。

1. **建立统一模型。** 输入网络 \(G_1\) 与每核输出网络 \(G_{2;k}\) 都用 descriptor/state-space 方程表示；反馈误差 \(e_k\) 进入 controller \(K_k\)，controller 输出受 \([d_{\min},d_{\max}]\) clipping 的 duty cycle。FIVR switch 使用 low-frequency averaged ideal-transformer model，而不是逐个 PWM 边沿的 switching model；负载是 ideal current stimulus。[pdf:E03]（PDF 物理页 3，Eq. (1c)–(2)）
2. **做 dc 初始化与固定步长离散。** 在 nominal load 下先求所有变量的 dc operating point，再以 implicit Euler 和固定 \(\delta t\) 推进。由于 PWM 延迟至少一个步长，当前线性系统的系数矩阵固定，可预先 LU factorization。[pdf:E03]（PDF 物理页 3，Eq. (3) 与 Section II-A）
3. **选择 partition。** WR-LP 在共享 \(G_1\) 与全部 \(C_k\) 之间横切：所有 \(C_k\) 并行求解，再由一个 \(G_1\) 汇总更新接口电压。WR-TP 为每个 core 切出 \(G_{1;k}+C_k\)，跨 core 的输入网络耦合由上一轮 relaxation source 提供。WR-LPTP 则外层做 TP、内层做有限次 LP，不等待内层完全收敛。[pdf:E05]（PDF 物理页 5，Fig. 2、Eq. (10)–(12)）
4. **按整段 waveform 迭代。** 每轮从 \(t_1\) 到 \(t_{Q_{\max}}\) 求完整波形，而不是像 SPICE 那样每个时间点先完全收敛再前进。所有 core 输出完成后同步，更新 relaxation source，并用各输出电压相对上一轮的 infinity norm 是否低于 \(\epsilon\) 决定停止。[pdf:E07]（PDF 物理页 7，Algorithm 1 与 Eq. (13)–(15)）
5. **让分区与状态结构对齐。** 对输入 impedance \(Z_1(s)\) 采样并做 vector fitting，将其转成 block-diagonal multi-SIMO realization。此后每个 \(x_{1;k}\) 的 state update 可独立执行，只有输出贡献汇总形成同步点；同一结构既能提高 TP，也能把 LP 中原先串行的 \(G_1\) 更新大部并行化。[pdf:E08]（PDF 物理页 8，Fig. 5、Eq. (18)–(21)）
6. **在共享内存 CPU 上执行。** WR-TP 的每个线程求一个 \(G_{1;k}+C_k\) 并计算其对其他端口 relaxation source 的贡献；WR-LPTP(\(m\)) 在每个 outer iteration 中只做 \(m=1\) 或 \(2\) 次 inner LP 再交换跨 core 信息。[pdf:E09]（PDF 物理页 9，Algorithm 2、Eq. (22)–(27) 与 Section IV-E）实现使用 C、OpenMP 和 Intel MKL，在共享内存工作站/服务器上运行；论文明确没有使用 GPU 或网络 worker。[pdf:E06]（PDF 物理页 6，Section IV-A）

论文没有报告 adaptive/multirate time stepping、开关事件定位、定点数、FPGA 资源映射、deterministic WCET 或硬实时 I/O。它报告的是离线 CPU transient solver，不应补写成未做过的硬件 pipeline。

## § 6 — 核心数学推导（无形式化数学则跳过）

### 1. 离散为什么能保持每步线性

对任意状态 \(x\)，论文采用

\[
\left.\frac{dx}{dt}\right|_{t_q}\approx
\frac{x(t_q)-x(t_{q-1})}{\delta t}.
\]

同时，\(d_k(t_q-T_k)\) 来自至少一个历史时间步，因此 averaged switch 关系 \(v_{2;k}=d_kv_{1;k}\)、\(i_{1;k}=-d_ki_{2;k}\) 在当前步中只含已知的 \(d_k\)。所以每个时间步要解的是线性方程，而不是在 duty cycle 上再做当前步非线性迭代。[pdf:E03]（PDF 物理页 3，Eq. (1h)–(3)）

### 2. LP 是接口波形上的 fixed-point

把每核系统记为 \(C_k\)，共享输入网记为 \(G_1\)，LP 的两步是

\[
\{i_{1;k}^{\nu},v_{o;k}^{\nu}\}
=C_k(v_{1;k}^{\nu},-i_{s;k}),
\]

\[
\{v_{1;1}^{\nu+1},\ldots,v_{1;N_c}^{\nu+1}\}
=G_1(i_{1;1}^{\nu},\ldots,i_{1;N_c}^{\nu}).
\]

上一式的 \(N_c\) 个实例完全独立，下一式把所有 interface currents 汇总到 \(G_1\)。若 \(G_1\) 成本远小于单个 \(C_k\)，论文的 cost model 给出接近 \(1/N_T\) 的理想缩放；若 \(G_1\) 反而占主导，LP 的串行段会使缩放接近 1，即几乎没有收益。[pdf:E04]（PDF 物理页 4，Eq. (4)–(7)）[pdf:E07]（PDF 物理页 7，Eq. (13)–(15)）

### 3. TP 把跨 core 耦合变成 relaxation source

输入网络的卷积响应被拆成

\[
v_{1;k}=V^{dc}_{1;k}
+z_{1;kk}\star\delta i_{1;k}+w_{1;k},
\qquad
w_{1;k}=\sum_{k'\ne k}z_{1;kk'}\star\delta i_{1;k'}.
\]

第 \(\mu\) 轮只用第 \(\mu-1\) 轮的 \(w_{1;k}\)，故每个 \(G_{1;k}+C_k\) 可独立求解；LPTP 再用 inner index \(\nu\) 对本核 input-core 接口做 LP。[pdf:E05]（PDF 物理页 5，Eq. (10)–(12)）作者在线性化 nominal operating point 后检查三种 iteration operator 的 frequency-domain spectral radius，两个 benchmark 上都小于 1，因此对其所测线性化模型得到 unconditional convergence；这不是对任意 PDN 非线性或任意 partition 的普遍证明。[pdf:E05]（PDF 物理页 5，Section III-D）

### 4. multi-SIMO 为什么改变成本

标准 realization 中，阻抗子块

\[
z_{1;kk'}(t)=C_{1;k}e^{A_1t}B_{1;k'}
\]

仍包含全局 \(A_1\)，算一个子块并未明显比算完整矩阵便宜。multi-SIMO 让 \(A_1\) 与 \(B_1\) 按输入分块，使

\[
z_{1;kk'}(t)=C_{1;kk'}e^{A_{1;k'}t}B_{1;k'},
\]

指数或离散 state update 只作用于较小的 \(A_{1;k'}\)。这就是模型结构从“逻辑可分”变为“计算可分”的数学原因。[pdf:E08]（PDF 物理页 8，Eq. (16)–(20)）

## § 7 — 实验设计与结论

### 问题一：线程增加时能否接近理想缩放？

**实验。** 作者对 60-core server benchmark 的 full model、standard ROM 和 block-ROM 分别运行 WR-LP、WR-TP、WR-LPTP(1) 与 WR-LPTP(2)，线程数最多到 60，并把 runtime 与 \(N_T^{-1}\) 理想线比较。Fig. 6 同时画出对 direct implicit-Euler reference 的真实 worst-case error，以及对上一轮的 stopping estimate。[pdf:E10]（PDF 物理页 10，Fig. 6）

**答案。** full model 因全局状态耦合而很快饱和；standard ROM 总耗时最低但缩放也会饱和；multi-SIMO block-ROM 几乎理想缩放到 30 threads，60 threads 才受串行同步段限制。也就是说，线程数不是充分条件，state-space block structure 才是可扩展性的前提。

### 问题二：小系统也值得用 WR 吗？

**实验。** 4-core mobile benchmark 只测试 1、2、4 threads，仍比较三种模型与四种 WR 方案；Fig. 7 给出 runtime、对 reference 的误差和 stopping estimate。[pdf:E11]（PDF 物理页 11，Fig. 7）

**答案。** block-ROM 仍能给出接近理想的并行缩放，但系统太小，重复求解多个 WR iteration 的代价高于直接串行解。论文因此明确得出：总体模型复杂度低时 WR 不合适；在所测 mobile case 中，TP 是 WR 变体里表现最好的方案。

### 问题三：比较是否覆盖了规模、精度和实际运行平台？

**实验。** server 有 60 cores、每核 3 phases、57 load ports，共 3420 个输出端口；mobile 有 4 cores、每核 4 phases、36 load ports，共 144 个输出端口。server 与 mobile 分别施加每核 20 A/3 ns 和 10 A/5 ns 的阶跃序列，分别运行 11 000 和 50 000 个时间步。平台是双路、每路 24-core/48-thread、2.65 GHz、1024 GB RAM 的共享内存服务器；线程数选为 core 数的整数因子以避免 load imbalance。[pdf:E12]（PDF 物理页 12，Table II 与 Section V）

**答案。** 测试覆盖了一个小型与一个大型真实产品 PDN 模型，并用所有输出端口、所有时间步的最大偏差评价精度；但 workload 只是规则的 current-step sequence，硬件平台也只有这一台大内存 CPU 服务器，不能据此推出不同 NUMA、GPU、FPGA 或真实 workload 下的相同缩放。

### 问题四：WR 的误差与 runtime 到底是多少？

**实验。** 以 \(\epsilon=10^{-4}\,\mathrm{V}=0.1\,\mathrm{mV}\) 为停止阈值，Table III 报告所有模型与 WR scheme 的 runtime。server standard ROM 的 WR-LP 在 60 threads 时为 0.93 s，对应 direct C reference 7.20 s；大多数 server 配置在 5–7 个 outer WR iterations 后停止，但 WR-LPTP(1) 的 block-ROM 列为 10 轮。正文把整体收敛概括为 5–7 轮，而表格明确保留了这个较慢例外。Fig. 8 显示前三轮 LP/TP waveform 逐步贴近 reference。[pdf:E13]（PDF 物理页 13，Fig. 8、Table III 与 Section V-A）

**答案。** 在 server standard ROM 上，分区并行可把直接 C 积分的秒级时间进一步降到 1 s 以下；但 block-ROM 因状态数更大，虽缩放更理想，绝对 runtime 不一定更低。WR-LPTP(1) 的收敛最差，说明只做一次 inner LP 不足；\(m=2\) 更稳。

### 问题五：相对 HSPICE 的结论能否直接解释为“普遍三数量级加速”？

**实验。** mobile HSPICE runtime 为 1792 s，三种模型相对 HSPICE 的最大输出电压偏差约 3.3 mV；server HSPICE netlist 则未收敛。[pdf:E12]（PDF 物理页 12，Section V）论文结论写道，结合 MOR 与 parallel WR，相对 HSPICE 的总体 speedup 超过三个数量级，并再次强调几乎理想的并行效率只在 interconnect state-space matrix 具有特定 block-partitioned structure 时出现。[pdf:E14]（PDF 物理页 14，Section VI）

**答案与保留。** “HSPICE 未收敛而 WR 数秒完成”证明了工程可用性差异，却不能形成有穷的 runtime ratio；对 mobile，Table III 在 0.1 mV 阈值下最快列出的 WR runtime 为 2.71 s，\(1792/2.71\approx661\)，不到 \(10^3\)。因此“超过三数量级”应作为作者的总体结论保留，不宜把它改写为两个 benchmark、每种 WR 配置都被 Table III 直接证明的统一数字。实验也没有与 silicon measurement 比较，3.3 mV 是不同仿真路线之间的偏差，不是硬件真值误差。

## § 8 — Take-aways

**5 句话。**

1. 论文把 system-level multicore PDN 的完整瞬态仿真拆成共享输入网与 per-core 闭环子系统，并用 WR 迭代恢复被暂时切断的耦合。
2. LP、TP、LPTP 都不是新 WR 理论，贡献在于针对实际 PI 拓扑、模型结构和共享内存执行的组合设计。
3. 并行是否有效首先取决于 state-space realization 是否真正分块，而不是图上是否画出了分区。
4. 60-core server 上 standard ROM 的 WR-LP 可低于 1 s，block-ROM 可近理想缩放到 30 threads，但小型 mobile case 仍以直接串行法更合适。
5. 结果只支持 averaged-FIVR、CPU/OpenMP/MKL 的离线 PDN 仿真，不能外推为 switching-level EMT、FPGA 或硬实时实现。

**3 句话。**

1. WR 用几次整段波形的重复计算换取 per-core 并行。
2. multi-SIMO block realization 是把这种并行从拓扑概念变成实际加速的关键。
3. 方法对大而结构合适的 PDN 有效，对小系统、强耦合或结构不匹配模型未必占优。

**1 句话。**

这篇论文最重要的启示是：system-level PDN transient simulation 的可扩展性由 partition、coupling strength 与 model realization 三者共同决定。

## § 9 — 最脆弱的假设

最脆弱的假设是：**按 core 分区后，跨 core 耦合足够弱、足够集中在共享输入网络 \(G_1\)，并且能用可分块的 multi-SIMO realization 表示。** 只有这样，Gauss–Jacobi 用上一轮跨分区 waveform 才会在少数轮次内收敛，同时每个线程才真正只承担一小块状态。

如果存在强烈的 cross-core on-chip coupling、共享输出电感/电容、耦合控制器、接近不阻尼 resonance 的输入网，或 switching-level 行为使 nominal-point linearization 不能代表实际轨迹，那么 iteration operator 的 spectral radius 可能接近甚至超过 1。结果不是仅仅“慢一点”：WR 可能需要很多轮或不收敛，分区也可能失去独立性，核心加速机制同时失效。

论文给出的正面证据是接口约 \(1\,\mathrm{m}\Omega\) 对 \(1\,\mathrm{k}\Omega\) 的阻抗不对称、两个 benchmark 线性化 iteration operator 的 spectral radius 小于 1、以及多数 server 配置在 5–7 轮达到 0.1 mV；Table III 中 WR-LPTP(1) block-ROM 的 10 轮是较慢例外。[pdf:E05]（PDF 物理页 5，Section III-A 与 III-D）[pdf:E13]（PDF 物理页 13，Section V-A 与 Table III）不足之处是只验证了两个产品模型、规则阶跃负载与 averaged switch；没有对 coupling strength、resonance damping、controller interaction 或 partition mismatch 做系统 sweep。full model 的并行效率已经表明，一旦 realization 不匹配，结构优势会显著退化。[pdf:E10]（PDF 物理页 10，Fig. 6）

## § 10 — 最小复现实验

一周内最有价值的最小复现不是重建完整 60-core 产品，而是做一个 **4-core、两种等价输入网 realization 的对照实验**。

1. 建立同一组 passive \(4\times4\) input impedance response：一份使用普通全局 state-space realization，另一份用 per-input multi-SIMO block realization；二者先在频域和 direct transient response 上验证等价。
2. 每个 core 接一个相同的 averaged buck/output-network/controller 小模型，使用论文的 fixed-step implicit Euler、dc 初始化和 10 A/5 ns 分段阶跃；实现 direct solver、WR-LP 与 WR-TP。
3. 在线程数 1、2、4 下测量 wall-clock runtime、parallel efficiency、每轮相对 direct solution 的全端口全时步最大误差，以及“相邻两轮误差”是否会过早触发停止。
4. 支持核心 claim 的结果是：两种 realization 精度一致，multi-SIMO 版本在 4 threads 下明显接近 \(1/4\) 缩放，并在少数迭代达到 0.1 mV，而普通 realization 明显饱和。
5. 反驳核心 claim 的结果是：在相同 transfer function 与相同实现质量下，multi-SIMO 没有端到端加速，或 stopping estimate 小于 0.1 mV 时真实误差仍超限。

这个实验复现的是“模型结构使分区计算真正变小”这一机制，不需要声称复现论文的商业 PDN 数据或 60-core 绝对 runtime。

## § 11 — 最强反例设计

最强反例是一个 **保持模型规模不变、只连续增强跨 core coupling 的参数化 PDN**。令输入 impedance matrix 的 off-diagonal block 乘以 \(\alpha\)，并逐步减小共享 resonance 的 damping；对每个 \(\alpha\) 计算 nominal-point iteration operator 的 spectral radius，再运行相同 WR-TP/WR-LPTP 和 direct solver。所有 workload、time step、线程数、模型 order 与 stopping threshold 保持不变。

如果 \(\alpha\) 增大时 spectral radius 接近 1，迭代数和 runtime 急升；或 spectral radius 在 nominal point 仍小于 1，但负载大阶跃使非线性 trajectory 上 WR 停止估计失真，这就给出两种具体失败机制：一是“弱耦合”不成立导致 relaxation 本身失效，二是局部线性收敛判断不能代表大信号闭环过程。若此时 direct solver 反而更快且稳定，便直接推翻“该 partition 在系统级 PDN 上普遍有优势”的宽泛解释，同时不否定论文在两个已测 benchmark 上的结果。

## § 12 — Follow-up Research Idea

**候选想法：把问题从“人工选择 LP/TP/LPTP”改写成“在给定 PDN 上联合合成 partition、interface condition 与 state-space realization，并为收敛和端到端成本给出可检验证书”。** 由于未在本任务中检索 PDF 之外的相关工作，这里不声称 novelty。

（a）未满足的需求是：论文已经显示 full、standard ROM、block-ROM 的最佳方案不同，小系统与大系统的最佳方案也不同，但当前流程仍依赖人工预处理和事后 benchmark。  
（b）潜在研究价值在于把“某两个产品上有效”提升为“对一个新 PDN，先预测是否值得 WR、怎样分区、会收敛多快”，减少昂贵的试错。  
（c）可借鉴相邻领域的 optimized domain decomposition、graph partitioning、robust control spectral-radius bounds 与 task-graph performance modeling；目标函数不是单纯最小 cut，而是同时最小化 relaxation contraction factor、每分区计算量和同步成本。  
（d）第一个证伪实验是留出一组具有强 cross-core coupling、不同 resonance damping 和不同 core 数的 PDN，只用模型矩阵预测最佳策略；若预测方案的真实 end-to-end runtime 不能稳定优于 direct solver 与三种固定 partition 中的最佳者，或收敛证书不能覆盖实测 error，则想法失败。  
（e）它与本文的实质区别是：本文在固定拓扑上定制并比较三种 WR scheme；候选工作把“是否分、在哪里分、用什么 realization、是否应直接求解”本身变成受约束的自动决策问题。
