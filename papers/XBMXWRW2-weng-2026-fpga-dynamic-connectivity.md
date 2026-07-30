# High-Fidelity Real-Time Simulation of Power Electronics Converters via FPGA-Accelerated Dynamic Connectionist Neural Network

- 作者：Haowen Weng, Zixiang Liao, Yinbin Chen, Can Wang
- 出处：*IEEE Transactions on Power Electronics*, Vol. 41, No. 1
- 年份：2026
- DOI：10.1109/TPEL.2025.3595452
- Zotero key：XBMXWRW2

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是一般意义上的“用神经网络拟合变换器”，而是一个同时受三条硬约束夹击的问题：器件开通、关断的电压与电流尖峰发生在纳秒尺度，系统级电磁暂态仿真又必须在每个实时步内完成计算，而 FPGA 上可用的乘法器、存储和流水线时序是有限的。商业实时仿真器常用理想开关、binary resistance 或 associated discrete circuit（ADC）模型维持计算速度和固定导纳矩阵，却因此看不见决定开关损耗、EMI、热应力和保护裕度的瞬态波形；物理器件模型能描述这些现象，但复杂非线性方程和工艺参数使它难以实时执行。这一矛盾是论文的工程出发点。[pdf:E01]

作者把目标收紧为：以系统级仿真给出的稳态开关电压 \(V_{ce}\)、电流 \(I_c\) 和结温 \(T\) 为条件，在 FPGA 上每 5 ns 输出一个 IGBT 瞬态电压、电流样本，同时把单个开关模型的 DSP48 消耗压到可扩展的范围。论文直接声称，其 connectionist neural network（带相邻时间节点连接的前馈网络）和 dynamic neuron allocation strategy（DNAS，动态神经元分配策略）可用 47 个 DSP48 达到表中“多数工况 RMS error 小于 2%”的精度，而最近的两个对照分别使用 132 或 128 个 DSP48、报告小于 5% 的误差。[pdf:E02] [pdf:E12]

这件事重要，是因为它试图把“系统级实时闭环”和“器件级开关细节”拆成两个时间尺度：微秒级求解电路网络，纳秒级重建开关瞬态。若这种解耦可信，一块 FPGA 可以在不把整个网络都缩到纳秒步长的情况下，向控制器测试、损耗估算和 EMI/热分析提供更细的开关波形。[pdf:E08] 但这里的“高保真”首先是相对于训练所用的 LTspice 物理模型，而不是已经对真实功率器件完成的全工况计量验证；这个证据边界贯穿全文。

## § 2 — 前人工作与不足

论文把既有 device-level modeling 分为三类。第一类是 Hefner、Kraus–Mattausch、Sheng 等物理或解析模型：它们能在离线仿真中描述器件机理，但非线性方程复杂、参数依赖工艺，难以直接塞进严格的实时步长。第二类是非线性等效电路、piecewise-linear、lookup table、polynomial fitting 和 Norton equivalent 等 behavioral model：计算更轻，但时间分辨率、工况适应性或硬件资源仍受限。第三类是 data-driven model，包括传统机器学习、RNN/LSTM 和深度 FNN；它们绕过器件内部方程，却带来重训练、串行依赖、泛化和 FPGA 部署成本问题。[pdf:E01] [pdf:E02]

与本文最接近的是 Li 等人的 ANN-aided 方法 [26]：把开关瞬态离散成时间节点，每个节点由独立 FNN 拟合，已经做到 5 ns，但不同时间节点的输出互不相连，没有利用波形的时间连续性，且单开关需 128 个 DSP48。[pdf:E02] 论文参考文献给出的完整出处是 Q. Li 等，*IEEE Transactions on Transportation Electrification*, 2023。[pdf:E13] 另一个强对照是 Wang 等人的 SiC MOSFET 等效开关模型 [19]：10 ns、132 个 DSP48、在 LLC 拓扑上 RMS error 小于 5%，但器件级与系统级求解紧耦合，复杂网络中器件瞬态步长仍受系统步长牵制。[pdf:E01] [pdf:E12]

作者识别出的两个具体缺口因此不是笼统的“以前不够准确”。一是**模型结构缺口**：逐时间节点 FNN 牺牲了序列相关性，而普通 recurrence 又会形成上一输出到下一输出的串行反馈，阻塞 FPGA pipeline。二是**资源配置缺口**：同一开关瞬态中，有些时间节点几乎线性，有些节点因不同工况的开关相位错位而高度非线性；给每个节点固定同样多的 hidden neuron，会在简单节点浪费资源、在复杂节点又不够用。[pdf:E04] [pdf:E06]

需要保留一个比较口径风险：Table IV 只给出方法类型、步长、DSP48 和汇总 RMS error，没有说明三个方法是否使用相同器件、相同训练/测试工况、相同误差统计分母或相同 FPGA 实现边界。因此它支持“本文实现的资源—精度组合优于表中报告值”，但不足以构成完全受控的跨论文 benchmark。[pdf:E12]

## § 3 — 重建作者的思考路径

可以不用本文贡献作前提，重建出如下路径。

1. 实时 EMT 首先要让系统级网络每一步都按时收敛。ADC 把开关导通、关断分别等效为小电感和小电容，再离散成固定导纳与历史电流源，从而避免开关动作时重建节点导纳矩阵；这解决“实时求解”，却没有器件真实瞬态。[pdf:E02]
2. 既然厂商校准的 SPICE 模型能离线给出高分辨率波形，可以把昂贵物理模型当作 teacher，把 \(V_{ce},I_c,T\) 到整段 \(v_{ce},i_c\) 的映射离线学出来，在线只做小网络推理。[pdf:E03]
3. 开关波形在相邻 5 ns 样本之间连续，独立 FNN 丢掉了这一信息；自然的补救是把上一时间节点输出反馈到当前节点。但直接按 \(y(t-1)\rightarrow y(t)\) 计算会把所有节点锁成一条串行链，破坏 FPGA 的高吞吐 pipeline。[pdf:E04]
4. 将 recurrence 代数展开到更早的 \(t-3\)，可以在反馈值抵达前预先计算中间项，把“模型记住上一时刻”与“硬件每拍都出结果”同时保住。[pdf:E04] 这一步不是增加网络深度，而是改变依赖调度。
5. 随后观察各时间节点的数据几何：简单节点近似线性，复杂节点因各工况瞬态进度不一致而强非线性。于是问题从“每个节点放几个神经元”转成“如何把同一组硬件计算单元跨时间借用”。[pdf:E06]
6. 稳态条件在一小段开关瞬态内不变，因此简单节点空闲的神经元可以提前计算未来复杂节点的一部分结果，并把结果存到 BRAM；到目标节点时直接取回。这样，动态的是任务表和预计算时刻，物理硬件仍是静态 pipeline。[pdf:E07]
7. 最后，把微秒级 ADC/EMTP 网络求解与 5 ns 器件波形生成并行放在 FPGA 上，以开关沿为事件边界，用系统级稳态量启动器件模型，器件瞬态结束后再回到系统级值。[pdf:E08]

这条路径的真正洞见是：作者没有要求一个统一求解器同时承担两个时间尺度，而是让系统模型负责电路状态、surrogate 负责短暂的器件波形；没有用更大的通用神经网络换精度，而是利用瞬态的时间结构设计可流水的专用网络和任务调度。

## § 4 — 核心 Intuition

开关瞬态既有时间连续性，又只有少数时间节点真正难拟合，所以应当让当前节点看到先前输出，同时让简单节点的空闲计算能力提前服务未来的复杂节点。作者通过展开反馈依赖，使有“记忆”的网络仍能流水并行，再用 BRAM 表驱动的预计算把固定硬件神经元按时间重新分配。[pdf:E04] [pdf:E07] 系统级求解只提供 \(V_{ce},I_c,T\) 和开关事件，器件级网络在事件后的短窗口内生成 5 ns 波形，从而避免把整个 EMT 网络都推进到 5 ns。[pdf:E08]

## § 5 — 具体方法与完整 Pipeline

下面以论文的 bidirectional Buck–Boost case 为例，从离线数据到在线输出重走一次完整 pipeline。

1. **固定系统级开关形式。** ADC 用小电感 \(L_s\) 表示 ON、小电容 \(C_s\) 表示 OFF，并把开关写成固定导纳 \(Y_s\) 与历史电流源。作者又采用 initial error correction，在切换瞬间以先前稳态电压或电流替换初值，抑制 ADC 的虚功率损失与瞬态振荡。[pdf:E02] 节点分析被重排为先合并支路电流源，再用预存的 \(B,C\) 矩阵并行计算 branch voltage/current，仅保留两个顺序阶段。[pdf:E03]
2. **离线生成 teacher data。** 论文选用 Onsemi 提供、按物理机理校准的 FGY160T-65SPD-F085 IGBT SPICE 模型，在 LTspice 中搭建双脉冲式测试电路。Python 扫描 \(V_{ce}=400{:}5{:}600\ \mathrm{V}\)、\(I_c=5{:}5{:}125\ \mathrm{A}\)、\(T=20{:}10{:}100^\circ\mathrm{C}\)，组合成 9225 个工况；gate resistance 固定为 \(20\ \Omega\)，gate voltage 固定为 15 V。[pdf:E03] 每个工况取 750 ns 开通与 2500 ns 关断数据，按 200 MHz 时钟重采样为 5 ns 时间节点，即分别 150 和 500 个节点。[pdf:E03] [pdf:E06]
3. **转置数据组织。** 输入 \(X_i=[V_{ce},I_c,T]\) 表示第 \(i\) 个稳态工况；输出不按“每条波形一行”，而按时间节点转置为 \(Y_j\)，其中包含所有工况在第 \(j\) 节点的 \(v_{ce},i_c\)。这样每个时间节点对应一个小网络，同时能观察该节点横跨工况的数据复杂度。[pdf:E04]
4. **训练 connectionist network。** 每个节点的主干是 input–hidden–output FNN，另加 feedback layer，把前一节点输出 \(y(t-1)\) 乘以时间相关权重 \(W_F(t)\) 后加到当前原始输出 \(Y(t)\)。论文用与传统 FNN 相同的数据、training algorithm 和 epoch 数做结构对照，但没有报告 optimizer、learning rate、训练/验证划分或随机种子；这些训练细节在本文中保持“未报告”。[pdf:E04] [pdf:E05]
5. **把反馈改写为可流水依赖。** 直接 recurrence 会卡住 pipeline；作者把 \(y(t-1)\) 和 \(y(t-2)\) 继续展开，使当前输出依赖更早的 \(y(t-3)\) 与可预计算项。硬件被分成四个连续 stage，在 200 MHz 下并发工作；pipeline 填满后，论文声称每 5 ns 给出一个有效输出。[pdf:E04] [pdf:E05]
6. **离线求 DNAS 调度表。** DNAS 从经验初始化的 `HiddenData` 出发，以 \(E_{\mathrm{Gain}}=1.25\) 判断删减神经元后的 MSE 是否可接受；若简单节点释放出 `Neural_least`，再把这些名额加给高误差节点。[pdf:E06] 在线硬件并不真的增删乘法器：当时间节点 \(t_m\) 只需要 \(n-j\) 个神经元时，空闲的 \(j\) 个单元预计算未来节点 \(t_n\) 的附加神经元输出，写入 storage BRAM；到 \(t_n\) 再按 `index2` 读出，与当前前向结果合并。`index1` 则决定当前激活哪些神经元。[pdf:E07]
7. **映射到 FPGA。** 650 个时间节点网络及其变系数从 BRAM 按 time-node index 读取；tanh 不在线计算，而是做成 lookup table，并在训练时就用相同 LUT 替换理想 tanh，以避免训练—部署函数不一致。[pdf:E08] 论文未报告权重/激活的定点位宽、量化格式、饱和与舍入策略，故不能从 PDF 推定这些数值表示细节。
8. **双速率在线协同。** FPGA 每个系统级步长先执行 ADC 与重排后的 EMTP。控制器比较 \(g(t)\) 与 \(g(t-\Delta t_1)\) 检出开关沿，把当下稳态 \(V_{ce},I_c\) 和结温 \(T\) 交给器件模型，并把 time-node register 置零。器件模型随后以 \(\Delta t_2=5\) ns 输出瞬态；达到开通的 \(N=150\) 或关断的 \(N=500\) 后，输出切回系统级稳态值。[pdf:E08] pipeline 首个有效结果有 32 个 FPGA clock cycle 的启动延迟。[pdf:E09]
9. **在 Buck–Boost case 中执行。** 系统级步长是 400 ns，器件级步长是 5 ns；主电路参数包括 \(U_{\mathrm{high}}=600\) V、\(L=9.1\) mH、20 kHz switching frequency 和 44% duty cycle。FPGA 通过 DAC 输出缩放到 \(-5\) 至 5 V，示波器看到的是实时仿真结果，而不是被测功率器件端子波形；论文再把该结果与 LTspice 离线结果比较。[pdf:E09]
10. **实际执行平台。** 实现使用 Xilinx Kintex-7 XC7K325T 与 LabVIEW FPGA，外接 DAC3174 14-bit 双通道 DAC，最高 500 MSPS。论文列出的器件总量为 407600 registers、203800 LUT、840 DSP48 和 445 BRAM blocks。[pdf:E09] 这说明设计真实映射到了硬件，但没有给出时序收敛报告、最高频率裕量或逐模块 latency/resource breakdown。

## § 6 — 核心数学推导

### 6.1 固定导纳开关与系统级 EMT

ADC 的历史电流源写为

\[
\begin{cases}
i_{\mathrm{on}}(t)=\alpha_{\mathrm{on}}Y_su(t-\Delta t)+\beta_{\mathrm{on}}i(t-\Delta t),\\
i_{\mathrm{off}}(t)=\alpha_{\mathrm{off}}Y_su(t-\Delta t)+\beta_{\mathrm{off}}i(t-\Delta t).
\end{cases}
\tag{1}
\]

其中 \(Y_s\) 是离散后的固定导纳，\(\alpha_{\mathrm{on/off}}\) 与 \(\beta_{\mathrm{on/off}}\) 分别控制上一时刻电压、电流如何进入当前历史源，\(\Delta t\) 是系统级实时步长。稳态匹配要求 ON 时开关电压为零、OFF 时开关电流为零；瞬态匹配则通过阻尼和极点位置减少数值振荡及虚功率损失。[pdf:E02]

作者把传统 nodal EMTP 重排为

\[
\begin{cases}
i_{\mathrm{temp}}(t)=j_a(t)+j_s(t),\\
v_b(t)=B\,i_{\mathrm{temp}}(t),\\
i_b(t)=C\,i_{\mathrm{temp}}(t),\\
j_a(t+\Delta t)=(\alpha+\beta)i_b(t)-\alpha i_{\mathrm{temp}}(t),
\end{cases}
\tag{2}
\]

\[
\begin{cases}
B=-A^{T}Y_n^{-1}A,\\
C=-Y_bA^{T}Y_n^{-1}A+E.
\end{cases}
\tag{3}
\]

\(j_a\) 是支路离散元件形成的历史源，\(j_s\) 是独立电流源，\(v_b,i_b\) 是支路电压、电流；\(A\) 为 node-to-branch incidence matrix，\(Y_n,Y_b\) 是节点与支路导纳矩阵，\(E\) 是单位矩阵。工程直觉是先把所有源合成一个 \(i_{\mathrm{temp}}\)，再让 \(B\) 和 \(C\) 两条矩阵乘法路径并行计算电压、电流，而不是沿传统 EMTP 的多级中间量串行传播。[pdf:E03]

### 6.2 数据沿时间节点转置

论文把全部工况写为 \(X=[X_1,\ldots,X_{\mathrm{OP}}]^T\)，把第 \(j\) 个时间节点的全部输出写为

\[
Y_j=[Y_{j1},\ldots,Y_{ji},\ldots,Y_{j\mathrm{OP}}]^T,\qquad
j=1,\ldots,\mathrm{TN}.
\tag{4}
\]

这里 \(\mathrm{OP}=9225\)，\(X_i\) 含 \(V_{ce},I_c,T\)，\(Y_{ji}\) 含该工况在节点 \(j\) 的 \(v_{ce},i_c\)，\(\mathrm{TN}\) 是时间节点总数。[pdf:E04] 这一转置使“第 267 个节点比第 170 个节点更非线性”成为可直接观察和分配容量的问题，而不是在整条波形上平均掉。

### 6.3 Connectionist feedback 与依赖展开

带反馈的节点输出是

\[
y(t)=Y(t)+W_F(t)y(t-1),
\tag{5}
\]

其中 \(Y(t)\) 是当前 FNN 主干的原始输出，\(W_F(t)\) 是 feedback weight，\(y(t-1)\) 是前一时间节点最终输出。[pdf:E04] 它给模型一个最小的动态状态，但也形成逐节点串行依赖。

先代入一次：

\[
y(t)=Y(t)+W_F(t)\left[Y(t-1)+W_F(t-1)y(t-2)\right].
\tag{6}
\]

再把 \(y(t-2)\) 展开并整理：

\[
y(t)=Y(t)+W_F(t)W_F(t-1)
\left[
\frac{Y(t-1)}{W_F(t-1)}
+Y(t-2)+W_F(t-2)y(t-3)
\right].
\tag{7}
\]

Eq. (7) 的价值不是新的网络表达能力，而是把“必须刚刚算完的 \(y(t-1)\)”改写成可以更早准备的中间项与较早到达的 \(y(t-3)\)，给四级 pipeline 留出计算窗口。Fig. 4 明确画出各延时寄存器、乘法和求和阶段，并给出 200 MHz 下每 5 ns 一个输出的时序意图。[pdf:E04] [pdf:E05]

### 6.4 误差指标

论文用 relative root mean square error：

\[
y_{\mathrm{RRMSE}}=
\sqrt{
\frac{\sum_{j=1}^{N}(y_{\mathrm{pro},j}-y_{\mathrm{ref},j})^2}
{\sum_{j=1}^{N}y_{\mathrm{ref},j}^{2}}
}\times100\%.
\tag{8}
\]

\(y_{\mathrm{pro},j}\) 是模型输出，\(y_{\mathrm{ref},j}\) 是 LTspice reference，\(N\) 是该开关瞬态的节点数。[pdf:E05] 它衡量整段波形的归一化能量误差，能防止不同电压、电流幅值直接比较 RMSE；但单个百分数会掩盖峰值时间偏移、过冲幅值和局部 ringing 等对损耗或 EMI 很敏感的误差，因此仍需查看波形和更针对性的指标。

## § 7 — 实验设计与结论

**问题 1：时间节点 feedback 是否真的比独立 FNN 更准确？** 作者让 traditional FNN 与 connectionist model 使用同一输入层、hidden/output 结构、数据、训练算法和 epoch，只移除 feedback；并比较不同 hidden neuron 数。在 \(V_{ce}=505\) V、\(I_c=15\) A、\(T=50^\circ\mathrm{C}\) 的例子中，3-neuron proposed model 对开通/关断电压和电流的 RRMSE 分别为 0.82%、0.52%、1.24%、1.82%，而 5-neuron traditional model 为 1.07%、2.40%、1.62%、4.22%。因此在这一展示工况下，更小的 connectionist model 仍更贴近 LTspice。[pdf:E05] 但论文没有给出跨工况的 paired statistical test，也没有把训练划分说清，不能把这四个数字外推为任意器件条件下的优势。

**问题 2：DNAS 能否在不增加硬件 neuron unit 的情况下改善误差分布？** 作者在全部 9225 个工况上比较 3-neuron connectionist model 优化前后。RRMSE 小于 1% 的工况占比，开通 \(v_{ce}\) 从 80.83% 增至 96.65%，关断 \(v_{ce}\) 从 78.34% 增至 85.39%，开通 \(i_c\) 从 82.69% 增至 91.51%，关断 \(i_c\) 从 38.01% 增至 62.92%。[pdf:E07] [pdf:E08] 这支持“把简单节点空闲算力预借给复杂节点可降低误差”，尤其是开通电压和关断电流；但关断电流仍有 37.08% 工况未进入 1% 内，不能把优化描述成所有工况都达到 1%。

**问题 3：结构能否满足 5 ns 实时输出？** Fig. 4 给出四级 200 MHz pipeline，论文陈述稳定后每 5 ns 输出一个样本；完整系统有 32 clock cycle startup latency，随后按 150/500 个 time node 生成开通/关断波形。[pdf:E05] [pdf:E09] 这证明的是作者实现所声明的吞吐架构与真实 FPGA 部署；PDF 没有给出 post-route timing report、slack、逐周期 trace 或外部逻辑分析仪结果，因此时序余量仍未报告。

**问题 4：在一个 converter case 中，双速率框架能否重现器件瞬态？** Buck–Boost case 使用 400 ns system-level step 与 5 ns device-level step，20 kHz switching、600 V 高压侧和 44% duty；Fig. 16 是 DAC/oscilloscope 输出，Fig. 17 把 FPGA real-time simulation 与 LTspice offline simulation 的开通/关断 \(v_{ce},i_c\) 叠加，视觉上基本一致。[pdf:E09] [pdf:E10] 论文没有为 Fig. 17 报告综合误差或 switching-loss error，结论只应写成“展示波形对齐”，不能自行补成器件实测精度。

**问题 5：换成更大拓扑和另一器件后，框架还能工作吗？** 三相 inverter case 采用 FGY100T120RWD 1200 V IGBT，\(U_{dc}=700\) V、50 Hz 基波、10 kHz triangle、modulation ratio 0.889、dead time 800 ns；system/device step 分别为 1 μs/5 ns。[pdf:E10] 系统级三相波形、IGBT 开关波形和 LTspice reference 在 Figs. 19–21 中视觉吻合。[pdf:E11] 这说明实现能承载第二个 topology 和 device example；但 PDF 没交代第二器件的数据扫描、训练超参数或是否复用/重训网络，故“跨器件泛化”没有被单独验证。

**问题 6：资源是否支持扩展？** Table III 报告的是包括 PCIe、DAC logic、waveform control 在内的完整 case：Buck–Boost 使用 91/840 DSP48、96/445 BRAM，三相 inverter 使用 291/840 DSP48、171/445 BRAM；相应占比分别是 10.8%/21.6% 与 34.6%/38.4%。[pdf:E11] Table IV 则按 modeling method 比较，本文为 47 DSP48、5 ns、RMS error 小于 2%，Li 等为 128 DSP48、5 ns、小于 5%，Wang 等为 132 DSP48、10 ns、小于 5%。[pdf:E12] 两张表的统计边界不同：前者是完整 case，后者是模型级摘要，不能把 91 或 291 与 47 当作矛盾，也不能据此直接推算任意数量开关的线性容量。

总的实验答案是：论文有真实 FPGA 实现、两个 converter case、5 ns 输出和较完整的资源数字，足以支持“在该仿真参考与平台上可运行且资源较低”。它没有物理 IGBT double-pulse 测量、跨实验室复验、未见训练域外工况或复杂寄生振荡测试，因此不支持“对真实器件与任意拓扑普遍高保真”的强外推。论文结论自己也把适用范围限定为“不表现出复杂寄生振荡的 switching device”。[pdf:E12]

## § 8 — Take-aways

### 五句话

1. 论文把微秒级系统 EMT 与 5 ns 器件瞬态拆开，让实时网络求解与细波形生成并行而非统一缩步长。[pdf:E08]
2. Connectionist feedback 利用相邻时间节点的连续性，代数展开则把 recurrence 改造成可流水的依赖。[pdf:E04] [pdf:E05]
3. DNAS 不增加物理 neuron unit，而是让简单节点预计算复杂节点并把结果暂存 BRAM。[pdf:E07]
4. 在作者的 LTspice reference、9225 工况与 Kintex-7 实现上，方法展示了 5 ns、47 DSP48、表中多数工况 RMS error 小于 2% 的组合，并完成两个 converter case。[pdf:E03] [pdf:E12]
5. 最关键的证据缺口是 reference 与训练来源同为离线 SPICE，且模型只以 \(V_{ce},I_c,T\) 描述瞬态，所以真实器件、门极条件变化、历史状态和复杂寄生下的高保真仍未证明。[pdf:E03] [pdf:E12]

### 三句话

1. 这是一项“按开关瞬态结构设计网络与 FPGA schedule”的专用实时仿真工作，而不是用更大的通用网络暴力拟合。[pdf:E04] [pdf:E07]
2. 它在指定 FPGA 和两类变换器仿真中给出了可信的吞吐、资源与 simulation-to-simulation waveform evidence。[pdf:E09] [pdf:E11]
3. 是否能把该结果升级为真实 device-level fidelity，取决于 \(V_{ce},I_c,T\) 是否构成足够状态，以及对物理测量和训练域外寄生条件的验证。

### 一句话

本文证明了时间耦合网络加跨时间预计算可以把 SPICE 教师的 IGBT 瞬态以 5 ns 低资源重放到 FPGA，但尚未证明这个紧凑输入状态足以覆盖真实器件的全部开关物理。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**在固定 gate network 与器件型号下，开关沿时的 \(V_{ce},I_c,T\) 加 time-node index 足以唯一决定整段 \(v_{ce},i_c\) 瞬态。** 论文明确只把这三个稳态量作为动态输入，忽略 \(R_g,V_g\) 的变化；训练电路则固定 \(R_g=20\ \Omega\)、\(V_g=15\) V。[pdf:E03] 一旦两个物理状态拥有相同 \(V_{ce},I_c,T\)，却因上一周期 history、gate charge、diode reverse recovery、stray inductance/capacitance、结温空间分布或驱动条件不同而产生不同波形，这个映射就不是单值函数；无论网络多准，它都只能给两个真实答案输出同一个预测。

论文为这一假设提供的证据是：在按上述三维参数扫描得到的 9225 个 SPICE 工况内，feedback 与 DNAS 显著改善了 reference fit；两个 converter case 的 FPGA 波形也与 LTspice 离线波形接近。[pdf:E05] [pdf:E07] 但这些证据没有改变输入状态：训练与验证仍基于受控 SPICE 模型，Buck–Boost 的示波器也只是 DAC 输出的 simulation waveform。[pdf:E09] 作者在结论中进一步承认方法尤其适合“不具有复杂寄生振荡”的开关器件，这恰好暴露了该假设最可能失效的区域。[pdf:E12]

因此，本文最弱的地方不是 47 个 DSP48 是否准确，也不是某个波形肉眼是否重合，而是**状态可辨识性**未被验证。若输入没有包含决定未来的最小物理状态，增加数据、神经元或更好的训练都不能从根本上补回被折叠的信息。

## § 10 — 最小复现实验

一周内最值得复现的不是整套三相 inverter，而是“feedback 在相同小网络预算下是否稳定优于独立 time-node FNN”。

**数据。** 用论文同一类 Onsemi SPICE IGBT 测试电路，保留 5 ns 采样、750 ns ON 和 2500 ns OFF，但把扫描缩为 \(V_{ce}=400{:}10{:}600\) V、\(I_c=5{:}10{:}125\) A、\(T=20{:}20{:}100^\circ\mathrm{C}\)，约 1365 个完整工况。必须按“整条工况波形”划分 train/validation/test，不能把同一工况的不同时间节点随机分到两边，否则会泄漏。[pdf:E03]

**实现。** 做两个 3-hidden-neuron 模型：A 是每个 time node 独立 FNN；B 在相同主干上加入 Eq. (5) feedback，并用 Eq. (6)–(7) 的展开检查可流水调度。两者使用完全相同的归一化、loss、optimizer、epoch、seed 和参数量记录；先不做 DNAS，也不复现整套 FPGA，以隔离结构 claim。[pdf:E04]

**测量。** 对 held-out operating conditions 分别统计四类波形的 median、95th percentile 与 worst-case RRMSE，并额外测 turn-on/off delay、peak voltage/current error 与 switching-energy error。RRMSE 按 Eq. (8) 计算；局部指标用于防止整段能量误差掩盖峰值偏差。[pdf:E05]

**支持标准。** 若 B 在至少 4/5 个随机种子中同时降低四类波形的 95th-percentile RRMSE，且 peak/switching-energy error 不恶化，并能把展开后的依赖排成固定 initiation interval 1 的 200 MHz pipeline，则核心结构 claim 得到最小支持。**反驳标准。** 若优势只出现在训练工况、只来自更多参数，或在整工况 hold-out 后消失；或者反馈展开需要的存储/乘法抵消资源收益，则应反驳“时间耦合本身带来可部署的稳健增益”。完成这一步后，才值得加 DNAS 和板级实现。

## § 11 — 最强反例设计

最强反例是构造**相同可见输入、不同真实未来**。在同一 IGBT 上做 double-pulse test，精确配平开关前的 \(V_{ce},I_c,T\)，但准备两种隐藏状态：例如改变 gate resistance 或引入两档 commutation-loop stray inductance，并通过前一脉冲让 diode reverse-recovery/history 不同。对本文模型而言，两次事件的输入三元组与 time-node 都相同，所以它必须输出同一条 \(v_{ce},i_c\)；物理测量却应在 overshoot、ringing frequency、turn-off tail 或 switching energy 上产生可重复差异。论文的输入定义与固定 gate 条件直接给出了这个可攻击面。[pdf:E03]

具体判据可以设为：在测量不确定度之外，两组波形的 peak voltage、峰值电流或 switching energy 至少一项差异显著，而任何单一模型输出对两组中的至少一组超过论文表述的 2% 误差或超出保护/损耗允许带宽。若发生，它不是“网络训练得不够好”，而是证明输入状态不足，因而直接推翻方法能在该场景下高保真重建的机制前提。

为了避免把反例做成不公平的域外攻击，应分两层：先在论文默认的固定 \(R_g,V_g\) 下，只改变可实现的 parasitic/history；若已经失败，说明连默认 gate 条件下的状态也不充分。再改变 \(R_g\) 或 drive voltage，测试论文主动忽略的变量。作者已把适用范围限制为无复杂寄生振荡的器件，因此第二层若失败是确认边界；第一层若失败才是更强的核心反证。[pdf:E12]

## § 12 — Follow-up Research Idea

在 FPGA real-time EMT 领域，高影响工作通常不仅要给更低的平均误差，还要同时满足：可解释的数值/物理边界、可综合且有时序资源证据的硬件实现、跨器件与拓扑验证，以及能和真实测量闭合的工程价值。基于第 9 节，候选方向不是给现有网络再加一层，而是把问题从“由三个稳态数回放一条确定波形”改写为：

**面向事件的、带最小隐状态与不确定性输出的器件端口 surrogate。**

**(a) 未满足需求。** 实际开关瞬态依赖不可由 \(V_{ce},I_c,T\) 唯一表示的 history 与 parasitic；系统级模型又不可能把全部器件内部状态都传给 5 ns 模型。需要找到一个可在线更新、足够小、又能区分“同一端口量但不同未来”的 latent state，并在状态不足时输出可信区间而非伪精确单波形。本文对输入的约束和对复杂寄生的排除给出了直接动机。[pdf:E03] [pdf:E12]

**(b) 研究价值。** 若能证明一个低维 latent state 可由开关前若干系统样本与 gate command 在线估计，并在 Kintex-class FPGA 上保持 5 ns 吞吐，那么贡献会改变 device/system interface：器件模型不再只是静态条件查表，而成为有状态、可验证适用域的实时端口模型。它同时服务 HIL 可信度、保护极值、switching loss 和 EMI 风险，而不是只降低平均 RRMSE。

**(c) 可借鉴方法。** 可从 nonlinear state-space identification、subspace identification 与 reduced-order modeling 借用“最小可观测状态”思想；从 set-membership 或 conformal prediction 借用训练域外不确定性；从 passivity-preserving macromodel 借用端口能量约束。硬件上仍可沿用本文的 time-node pipeline 与 BRAM schedule，而不是引入不可控的大型 recurrent network。[pdf:E05] [pdf:E07]

**(d) 第一个证伪实验。** 使用第 11 节的 matched-\(V_{ce},I_c,T\)、different-history double-pulse dataset。比较三元输入基线与带 latent state 的模型：若后者不能在完全未见的 parasitic/history 组合上同时降低两组波形的 worst-case peak、energy 和 RRMSE，或若其 FPGA initiation interval 无法维持 5 ns，则这个方向立即失败，不应继续扩大模型。

**(e) 与现有工作的实质区别。** 本文及其最接近的 per-time-node FNN 把瞬态视为由当前 operating condition 决定的确定序列；候选方向把“输入状态是否足够”本身变成研究对象，并允许模型在不可辨识时表达不确定性。它改变了问题定义和验证标准，而不是换器件、换拓扑或再加一个 accuracy module。

这是**基于本文证据的候选想法**，尚未对 state-space device surrogate、uncertainty-aware HIL 或 passivity-constrained neural macromodel 做系统相关工作检索，因此不声称 novelty。最先要做的是上述可证伪的 matched-state experiment，而不是先写更复杂的网络。
