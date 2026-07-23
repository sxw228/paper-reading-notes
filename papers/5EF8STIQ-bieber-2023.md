# Universal Equivalent Model for Real-Time CPU/FPGA Co-Simulation of Hybrid Cascaded Multilevel Converters

- Zotero key：`5EF8STIQ`
- corpus order：`30`
- canonical slug：`bieber-2023`
- 作者：Levi Bieber、Liwei Wang、Juri Jatskevich、Wei Li
- 出处：IEEE Access，2023，DOI `10.1109/ACCESS.2023.3235272`
- 源 PDF：`_source.pdf`
- PDF SHA-256：`46737ab4ae96fa146ebc6fa05a6e1418bcc407decf7dd3203bd55b19037030cc`
- 阅读边界：只以该源 PDF 为内容真相；证据页码均为 PDF 物理页，从封面页起按 1 计。
- 硬件证据口径：论文在 OPAL-RT OP5700 的 CPU 与板载 Virtex-7 FPGA 上执行实时仿真，并报告了实时执行时间和 FPGA 资源占用；它没有报告外接控制器 HIL/PHIL、真实功率变流器样机或功率硬件试验。因此，下文所说“硬件验证”只指实时仿真计算平台，不指 H5LC 功率硬件得到验证。[pdf:E07] [pdf:E10] [pdf:E12]

## § 1 — 研究问题与重要性

论文要解决的是：怎样把拓扑复杂、含大量电容状态和故障切换逻辑的 hybrid cascaded multilevel converter（HCMC）放进确定步长的实时 EMT 仿真，同时既不让 CPU 被数百个电容更新和子模块排序拖垮，又尽量保留正常运行、DC 侧故障阻断及故障后充电过程的波形精度。作者以 hybrid five-level converter（H5LC）为最复杂的代表，构造 universal equivalent model（UEM），再把网络与上层控制放在 CPU、把大量并行电容状态和部分低层控制放在 FPGA。[pdf:E01] [pdf:E03] [pdf:E07]

这个问题重要，不只是因为“仿真更快”。VSC-HVDC 控制器的 rapid control prototyping（RCP）和 hardware-in-the-loop（HIL）测试要求仿真器在每个固定步长内完成计算；一旦超时，仿真时间就不再对应物理时间。H5LC 又比经典两电平、三电平和 MMC 多出主变换器状态、flying capacitor（FC）、cascaded full-bridge submodule（FBSM）及 DC 故障旁路逻辑，直接细化建模会把计算量推高。论文实际证明的是这种模型能在 OP5700 上实时执行并与离线 DEM 对照，而不是已经完成一个外部控制器或功率硬件的 HIL 测试。[pdf:E01] [pdf:E02] [pdf:E10] [pdf:E12]

## § 2 — 前人工作与不足

论文给出的技术背景是：两电平、三电平变流器和 MMC 已有实时仿真工作；H3LC 也已有用于高效 EMT 仿真的 detailed equivalent model 与 average-value model。但复杂 HCMC，尤其 H5LC，尚缺少一套把主电路等效、故障模式、电容状态、FBSM 排序与 CPU/FPGA 分工连成完整实时实现的方法。作者还指出，已有 H3LC 模型不具备本文展示的 FPGA 输入输出、排序、逐个 FBSM switching function 等实现细节。[pdf:E02] [pdf:E10]

已有路线的具体不足有两层。第一，CPU-only 方法需要串行更新每个 FBSM、FC 和 pole capacitor（PC）的状态；实际 HVDC 系统每相可有数百个含电容器件，这直接压缩实时步长余量。第二，只把某个 H3LC 化简并不足以说明更复杂 HCMC 的正常、故障阻断和恢复过程都能由同一个等效电路骨架承载。UEM 试图保留统一的受控源、二极管和理想开关骨架，同时承认不同 HCMC 仍需重写各自的电压、电流计算以及可能的 DC fault-blocking 硬件表示。[pdf:E04] [pdf:E05] [pdf:E07]

## § 3 — 重建作者的思考路径

下面是基于论文证据的逆向重建，不是作者逐字陈述。

1. HCMC 的系统级网络只真正需要看到端口电压、电流和故障模式，不必在 CPU 网络求解器里展开每只 FBSM 的开关器件；因此先把主电路压缩为少量受控电压源和简单开关元件。[pdf:E03] [pdf:E04]
2. 不能把所有内部状态一起删掉，因为 FBSM、FC、PC 的历史电压决定下一步端口行为，DC 故障时电流方向还会改变电容充放电规律；因此保留离散电容状态更新，只把它们移出 CPU 网络矩阵。[pdf:E04] [pdf:E05] [pdf:E06]
3. 这些电容更新和每相 FBSM 候选比较彼此高度并行，适合 FPGA；系统网络求解、上层/下层控制与少量含除法的运算更适合 CPU。由此形成“两颗 CPU + 一颗 FPGA”的异构分工。[pdf:E06] [pdf:E07]
4. 完全排序 3×64 个 FBSM 会消耗过多 FPGA logic，因此只找当前最大值和最小值，每个 FPGA 更新周期最多插入或旁路一个 FBSM，再用比 CPU 步长快得多的流水线多次完成追踪。[pdf:E08] [pdf:E09]
5. 最后用正常功率反转和 DC pole-to-pole fault 两类动态过程，对照离线 DEM，检查等效模型是否在降低计算负担时保留所关心的 EMT 波形。[pdf:E10] [pdf:E11]

## § 4 — 核心 Intuition

核心 intuition 是：CPU 只求解“电网眼中的八个受控电压源及其外围简单器件”，FPGA 同时维护产生这些受控源所需的大量内部电容状态与低层开关选择。这样没有把动态记忆抹掉，而是把可并行、重复的内部更新从 CPU 的串行关键路径搬到 FPGA；UEM 的价值来自“端口等效 + 状态仍在”，而不是静态平均化。[pdf:E04] [pdf:E05] [pdf:E07]

## § 5 — 具体方法与完整 Pipeline

以三相、每相 64 个 FBSM 的 H5LC 为例，一次协同计算的 pipeline 如下。

1. **CPU 1 生成控制意图。** CPU 1 执行 VSC-HVDC 上层和下层控制，产生每相 insertion function \(N_{\mathrm{ins},j}\)、director switch 状态 \(\mathbf T_j\)、fault blocking flag \(b\) 和 energization flag \(E\)。它从 CPU 2 接收相电压与相电流，也从 FPGA 接收 PC、FC 和聚合后的 FBSM 电压反馈。[pdf:E06] [pdf:E07]
2. **CPU 2 求解外部网络和 UEM。** CPU 2 运行 VSC-HVDC 网络及 H5LC-UEM。UEM 对三相各使用 nominal/de-blocking 源 \(v_{\mathrm{nom},j}\) 与 fault-blocking 源 \(v_{\mathrm{blk},j}\)，再加上上、下 PC 源，共八个受控电压源；CPU 2 把相电流、DC 电流和若干桥臂/FC 电流送给 FPGA。[pdf:E04] [pdf:E05] [pdf:E07]
3. **FPGA 选择 FBSM 状态。** 对每相 64 个电容电压，FPGA 先在 8 组内串行找局部最大/最小，再以树形比较找全局最大/最小。switching function 根据 \(N_{\mathrm{ins},j}\)、相电流极性和当前插入数，选择应充电的最低电压 FBSM、应放电的最高电压 FBSM，或对应地旁路一个单元；遇到 insertion polarity reversal 时，所有已插入 FBSM 可在一个 FPGA calculation cycle 内反向。[pdf:E08] [pdf:E09]
4. **FPGA 更新内部动态。** FPGA 并行更新 3×64 个 FBSM、6 个 FC 和 2 个 PC 的电压，并据此形成 \(v_{\mathrm{FB},j}\)、\(v_{\mathrm{nom},j}\)、\(v_{\mathrm{blk},j}\)、\(v_{\mathrm{PC},u}\) 和 \(v_{\mathrm{PC},l}\)。为减少 FPGA multiplier 资源，CPU 2 预先把电流乘以 \(T_{\mathrm{FPGA}}/C\) 后再经 PCIe 发送；少量含除法的故障电流计算也留在 CPU。[pdf:E07] [pdf:E09]
5. **模式切换。** 正常时使用 nominal 源；检测 DC fault 后，\(b=1\)，主五电平部分被阻断、UEM 开关改变，FBSM 对双向故障电流产生反向电压并把电流换流至 BTV。故障清除后进入 FC energization，\(E=1\) 时 FBSM 被旁路，FC 充到 \(V_{\mathrm{DC}}/4\) 附近，再恢复功率传输。[pdf:E05] [pdf:E06]

这个 pipeline 的关键边界是：所谓“universal”主要指 Fig. 5 的等效电路骨架可复用；换成 H3LC/H2LC 等拓扑时，EM 内部电路和电压、电流方程仍要按拓扑重新推导，并不是无需建模知识的自动生成器。[pdf:E06] [pdf:E07]

## § 6 — 核心数学推导

数学基础是电容关系 \(i=C\,dv/dt\)。用 Forward Euler 在一个离散步长内积分，得到

\[
v(t+\Delta t)=v(t)+i(t)\frac{\Delta t}{C}.
\]

它的直觉是：本步电流乘以步长给出电荷增量，再除以电容得到电压增量。UEM 对每个 FBSM、FC 和 PC 都保留这一历史状态，所以等效模型不是无记忆受控源。[pdf:E04]

对第 \(j\) 相第 \(i\) 个 FBSM，论文把 switching state \(s_{i,j}\in\{-1,0,1\}\)、fault flag \(b\) 和 energization flag \(E\) 合并进更新式：

\[
v_{c,i,j}(t+\Delta t)=v_{c,i,j}(t)+\left(\bar b E\,i_j(t)+b|i_j(t)|\right)\frac{\Delta t\,s_{i,j}}{C_{\mathrm{SM}}}.
\]

这里最重要的物理含义不是符号本身，而是三种模式：正常时按插入极性和相电流充放电；故障阻断时取电流绝对值，使两种电流方向都对应 FBSM 建立反向阻断电压；FC 充电阶段则旁路 FBSM，避免其被误充放电。卡片按 PDF 公式结构保留这一解释；实际复现时应直接按论文式 (12) 核对括号和乘法次序。[pdf:E05]

每相 cascaded FBSM 的端口电压由状态向量与电容电压向量内积得到：

\[
v_{\mathrm{FB},j}=\mathbf s_j\cdot \mathbf v_{c,j}.
\]

UEM 再用 \(b\) 与 \(E\) 在 nominal、fault-blocking 和 energization 三类受控源表达之间切换。PC/FC 电流不能仅由相电流直接给出，因此论文从详细 H5LC 导通路径逐项推导式 (13)–(26)，再用同一个 Euler 关系更新它们。[pdf:E05] [pdf:E06]

实时性来自时间尺度分离。一个 CPU 步长内可完成的 FPGA 更新次数为

\[
\tau=\frac{T_{\mathrm{CPU}}}{T_{\mathrm{FPGA}}}.
\]

64 个 FBSM 被分成 8 组；组内串行比较需 8 个 FPGA 基本时钟，组间树形比较需 3 个基本时钟。通过流水线，论文给出的更新间隔是 \(T_{\mathrm{FPGA}}=8t_{\mathrm{FPGA}}\)，示例为 80 ns，而一次更新最多改变一个 FBSM 状态。[pdf:E08] [pdf:E09]

## § 7 — 实验设计与结论

### 问题 1：正常功率方向改变时，UEM 是否跟得上详细模型？

实验把 H5LC 在 \(t=0.1\,\mathrm{s}\) 指令为向电网传输 \(0.9\,\mathrm{GW}\)，在 \(t=0.4\,\mathrm{s}\) 改为整流、传输 \(-0.9\,\mathrm{GW}\)。实时 H5LC-UEM 与离线 DEM 的相电流、五电平电压、cascaded FBSM 电压和所抽取的 FBSM capacitor voltages 基本重合。FC 电压有小 DC 偏差；作者把它归因于离线 MATLAB 64-bit double 与实时模型 20-bit resolution 的差别和 FC voltage-balancing control 对量化的敏感性。[pdf:E10] [pdf:E11]

### 问题 2：强动态 DC 故障及恢复过程是否仍保持一致？

实验在 \(t=1\,\mathrm{s}\) 对 100 km、\(\pi\)-section DC cable 中点施加持续 200 ms 的 pole-to-pole short circuit；故障清除后 DC 电压约在 \(t=1.31\,\mathrm{s}\) 回到 300 kV，FC 在 \(t=1.36\,\mathrm{s}\) 开始 energization，约 \(t=1.435\,\mathrm{s}\) 充好后功率恢复到 \(0.9\,\mathrm{GW}\)。UEM 与 DEM 的实功、DC 电流、相电压及 FC/PC 电压整体吻合；故障中实功摆动约为 \(-2.45\) 到 \(1.25\,\mathrm{GW}\)，相 a 电流峰值约 8 kA。[pdf:E10] [pdf:E11]

这里必须克制解释：论文根据器件额定能力判断该暂态对 BTV 和 free-wheeling diode 是安全的，但没有用实际 H5LC 功率硬件测量这一故障。因此这些波形验证的是两种仿真模型的一致性，不是 8 kA 故障下真实变流器的板级或功率级安全试验。[pdf:E11]

### 问题 3：计算负担是否真的下降并满足实时执行？

实时与离线比较都使用 50 µs CPU time-step。OP5700 上，CPU 2 的最小每步执行时间从 DEM 的 13.61 µs 降到 UEM 的 8.92 µs，按论文口径快 34.5%；CPU 1 对两种模型共用，最小执行时间为 2.40 µs。离线单核、64 FBSM/相时，一秒仿真的执行时间由 13.08 s 降到 11.4 s；当 FBSM 数量升到 1000/相，两种模型时间接近，说明 UEM 的离线优势会被其他开销稀释。[pdf:E11] [pdf:E12]

### 问题 4：FPGA 映射是否有真实资源余量？

论文报告 Virtex-7 资源占用：64 FBSM/相时使用 78,877 个 slice LUT（25.98%）、104,066 个 slice register（17.14%）和 1,912 个 multiplexer（0.84%）；256 FBSM/相时分别为 183,292（60.37%）、168,080（27.68%）和 5,128（2.25%）。这证明所述计算已映射到真实 FPGA 资源预算并有扩展余量，但它仍属于实时仿真器计算硬件证据，不包含外部控制器 I/O 延迟、功率接口或真实开关器件。[pdf:E12]

## § 8 — Take-aways

### 5 句话

1. UEM 把复杂 H5LC 主电路压缩成八个受控电压源及简单开关/二极管，同时保留 FBSM、FC、PC 的内部动态状态。[pdf:E04] [pdf:E05]
2. CPU 1 负责控制，CPU 2 负责网络与 UEM 求解，FPGA 负责 192 个 FBSM 加 FC/PC 的电压更新、FBSM sorting/switching 和部分低层 balance control。[pdf:E06] [pdf:E07]
3. 串并结合的 max/min sorter 与流水线让每个快速 FPGA 周期只改一个 FBSM，从而避免完整排序耗尽逻辑资源。[pdf:E08] [pdf:E09]
4. 在正常功率反转和 DC pole-to-pole fault 两个用例里，实时 UEM 与离线 DEM 的关键波形高度一致，但 FC 量化偏差已经暴露出有限精度敏感性。[pdf:E10] [pdf:E11]
5. 论文有 OP5700/FPGA 的实时计算证据，却没有外接 HIL 控制器或真实 H5LC 功率硬件证据。[pdf:E10] [pdf:E12]

### 3 句话

UEM 的主要贡献不是删去内部动态，而是把“外部网络求解”和“内部大量并行状态”分到最合适的处理器上。[pdf:E04] [pdf:E07] 它在作者测试的 H5LC 工况中把 CPU 2 每步时间从 13.61 µs 降到 8.92 µs，并保持与同为 50 µs 步长的离线 DEM 波形接近。[pdf:E10] [pdf:E11] “universal”应理解为可复用的等效骨架，而不是跨拓扑免推导，也不能从实时仿真器结果外推到 HIL 或功率硬件可靠性。[pdf:E06] [pdf:E12]

### 1 句话

这篇论文证明了一个 H5LC 的 CPU/FPGA 实时 EMT 实现能跑得更轻且在给定仿真对照中足够准确，但尚未证明其对任意 HCMC、任意事件时间尺度或真实控制/功率硬件都成立。[pdf:E11] [pdf:E12]

## § 9 — 最脆弱的假设

最脆弱的假设是：在 50 µs CPU 网络步长与更快 FPGA 内部更新之间交换的那组端口量，足以封闭 H5LC 的相关动态；换言之，CPU 看不见的子步事件、PCIe 延迟和拓扑内部快速耦合不会改变外部 EMT 结果。这个假设一旦失效，UEM 即使每个局部电容公式都正确，端口电压仍可能在一个 CPU 步内使用了过时或错误排序的状态，核心的“准确实时等效”就会失效。[pdf:E07] [pdf:E08] [pdf:E09]

论文对这个假设的支持是：正常功率反转、稳态波形及一次 200 ms DC fault 中，实时 UEM 与离线 DEM 基本吻合，而且 OP5700 实测计算时间低于 50 µs 步长预算。[pdf:E10] [pdf:E11] 证据缺口是：离线 DEM 也使用相同的 50 µs CPU time-step，因此两者可能共享同一种步长误差；论文没有独立更细步长 EMT 基准、异步外部控制器、I/O timing 测量或真实硬件故障波形来排除这一替代解释。这一判断属于基于论文证据的批评，不是作者结论。

## § 10 — 最小复现实验

一周内最值得复现的是“异构划分是否在 50 µs 实时预算内保持故障动态”，而不是重做整篇论文。

1. **数据与模型**：按论文设置实现 600 kV H5LC-UEM，64 FBSM/相、六个 FC、两个 PC；保留同参数 DEM，并建立一个更小步长的离线 reference。若有 OP5700/Virtex-7，使用论文的 CPU 1/CPU 2/FPGA 分工；若没有 FPGA，只能完成算法正确性预检，不能宣称复现了实时硬件结果。[pdf:E07] [pdf:E10]
2. **工况**：先跑 \(0.9\rightarrow-0.9\,\mathrm{GW}\) 功率反转，再跑论文的 100 km DC cable 中点、200 ms pole-to-pole fault 及 FC recharge 序列。[pdf:E10] [pdf:E11]
3. **测量**：记录每步 worst-case execution time，而不只记录 minimum；比较相电流、DC 电流、FC/PC 电压、每相 FBSM 电压和故障恢复时刻；另外统计量化偏差与一次 CPU 步内实际完成的 FBSM 状态更新数。
4. **支持标准**：所有实时步都在 50 µs 内完成；相对细步长 reference 的峰值、恢复时刻和稳态纹波误差均在预先设定的工程阈值内；重复运行不出现 deadline miss。
5. **反驳标准**：出现任何 deadline miss，或 DEM/UEM 都接近但二者共同偏离细步长 reference，或改变 fault inception 在 CPU 步内的相位就造成显著误差，即反驳“当前接口和步长已充分封闭动态”这一核心假设。

## § 11 — 最强反例设计

最强反例不是再换一个普通功率指令，而是把故障与 insertion polarity reversal 安排在 CPU 步长内部不同偏移处，并叠加一个外部控制器异步更新。对同一物理初始条件，扫描 fault inception 从 0 到 50 µs 的子步位置，用 1 µs 或更细的独立 EMT 模型作参考；同时限制 PCIe 交换只在原 CPU 边界发生。若 UEM 的峰值电流、BTV 换流时刻、FC 放电深度或恢复时刻对这个相位偏移敏感，而离线细步长模型不敏感，就说明“快 FPGA 内部更新”不能弥补“慢 CPU 端口闭合”的信息缺失。[pdf:E06] [pdf:E08] [pdf:E09]

第二个攻击点是 universality。论文自己说明 H3LC 需要修改 EM 内的 DC-fault-blocking circuitry，并为每种 converter 重新推导电压、电流计算。[pdf:E06] 选一个故障旁路路径或内部储能耦合明显不同的 HCMC，如果它无法只靠重定义受控源输入而保持同一 UEM 骨架，便直接限制“universal”所覆盖的拓扑集合。两种反例都比单纯增加仿真时长更有力，因为它们针对的是模型接口是否封闭，而不是某一组参数是否拟合。

## § 12 — Follow-up Research Idea

**候选想法：把“手工指定 CPU/FPGA 分区的 UEM”改写为“带可证伪误差契约的事件感知异构 EMT 编译”。** 这是基于单篇论文证据提出的方向，尚未做相关工作检索，因此不声称 novelty。

**(a) 未满足需求。** 论文证明了一个 H5LC 实例能实时运行，但对跨拓扑复用、CPU/FPGA 边界的子步误差、worst-case deadline 和外部 HIL I/O 没有统一保证；现实使用者真正需要的是“换拓扑后仍知道哪些状态能移到 FPGA、误差与 deadline 是否仍受控”。[pdf:E06] [pdf:E11] [pdf:E12]

**(b) 研究价值。** 电力电子实时仿真更看重确定时序、故障暂态保真度和工程可部署性。若系统能从 converter conduction graph 与状态方程自动生成端口等效、FPGA state kernel 和跨域接口，并同时给出 worst-case execution time 与事件误差证书，研究目标就从“又实现一个拓扑”提升为“可审计地编译一类拓扑”。

**(c) 可借鉴工具。** 可借鉴 hybrid systems 的 event detection、multirate co-simulation 的接口误差估计、synchronous dataflow 的确定调度，以及 hardware/software co-design 中的 worst-case timing analysis。

**(d) 第一个证伪实验。** 对 H5LC 与至少一个 EM fault circuitry 不同的 HCMC，在同一 OP5700 类平台上自动生成分区；扫描故障子步相位、控制器异步更新和 FBSM 数量。只要任一拓扑无法同时满足预设波形误差和 50 µs worst-case deadline，或自动接口遗漏一个改变端口行为的内部状态，该想法就被第一轮实验否定。

**(e) 与本文的实质区别。** 本文从 H5LC 手工推导 UEM、手工指定 CPU/FPGA 角色，再用 DEM 波形对照证明可行；候选方向把“是否可等效、如何分区、误差是否可接受”本身变成待自动生成和验证的研究对象，并要求独立细步长参考或 HIL timing 证据，而不只要求同一步长 DEM 与 UEM 相符。[pdf:E07] [pdf:E10] [pdf:E11]

### 证据缓存索引

| ID | PDF 物理页 | 主要定位 | PNG |
|---|---:|---|---|
| E01 | 1 | 标题、摘要、问题背景 | [打开](./_evidence/E01-p001-title-abstract.png) |
| E02 | 2 | HCMC/MMC 背景、实时仿真缺口、H3LC 既有模型 | [打开](./_evidence/E02-p002-prior-gap-hcmc.png) |
| E03 | 3 | 四项贡献、H5LC 拓扑与控制入口 | [打开](./_evidence/E03-p003-contributions-topology.png) |
| E04 | 5 | DC fault-blocking 边界、Fig. 5 UEM 骨架、式 (8) | [打开](./_evidence/E04-p005-uem-entry-fault.png) |
| E05 | 6 | Fig. 6 equivalent module、模式受控源、式 (9)–(14) | [打开](./_evidence/E05-p006-equivalent-module-equations.png) |
| E06 | 7 | 故障/充电状态方程、Fig. 7 CPU/FPGA I/O | [打开](./_evidence/E06-p007-fault-energization-cpu-fpga-io.png) |
| E07 | 8 | OP5700 架构、CPU/FPGA 职责、定点与 PCIe 边界 | [打开](./_evidence/E07-p008-cpu-fpga-roles.png) |
| E08 | 9 | 式 (27)、serial/parallel sorting 与 80 ns pipeline | [打开](./_evidence/E08-p009-sorting-latency.png) |
| E09 | 10 | switching function、polarity reversal、FPGA 电压生成 | [打开](./_evidence/E09-p010-switching-voltage-generation.png) |
| E10 | 11 | Fig. 12–13、验证平台、50 µs 步长、正常工况 | [打开](./_evidence/E10-p011-validation-setup-waveforms.png) |
| E11 | 12 | 故障工况、量化误差、Table 2 执行时间 | [打开](./_evidence/E11-p012-fault-test-table2.png) |
| E12 | 13 | Table 3 Virtex-7 资源、CPU 加速与结论 | [打开](./_evidence/E12-p013-resources-conclusion.png) |
