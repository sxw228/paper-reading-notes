# Switching-Period-Synchronization-Based Real-Time Simulation Method Suitable for Power Converters With High Switching Frequency

作者：Jin Xu、Pan Wu、Zirun Li、Keyou Wang、Guojie Li、Bei Han

出处：IEEE Transactions on Industrial Electronics

年份：2025

DOI：10.1109/TIE.2025.3553165

Zotero key：XRMS6SCG

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“如何再把 FPGA 上的一次矩阵运算做快一点”，而是一个更上游的实时调度问题：高频电力电子变换器的开关周期已经进入微秒量级，如果仍要求仿真器在每个很小的数值步长结束时都与现实时间同步，那么为了准确定位开关事件，步长通常被压到开关周期的大约 1%。论文以 100 kHz 为例，这意味着约 100 ns 的步长；在数百千赫兹开关频率下，单位现实时间内要完成的求解次数迅速增多，实时计算预算很容易失守。作者提出 switching period synchronization（SPS）：把一个完整开关周期作为主步长和对外同步间隔，只在周期内部按实际开关事件切成若干可变子步长并顺序推进。论文摘要明确声称，该方法在 on-board charger（OBC）硬件在环实验中支持了 200 kHz 开关频率。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

这个问题重要，是因为 HIL 的价值在于让真实控制器看到一个时间行为足够接近实物的数字对象，而不是为了遵守某一种内部求解器结构。若“采样门极信号”“内部数值积分”“对外输出”和“与墙钟同步”必须使用同一频率，硬件会为大量没有新开关事件的时间点重复付费；若能把它们解耦，仿真器就可能在不丢失事件位置的前提下显著减少同步次数和求解次数。这里真正的工程价值是扩大高开关频率 converter 的实时可模拟范围，并把紧张的 FPGA 时序预算转化为更宽松的开关周期级预算。

## § 2 — 前人工作与不足

论文梳理了几条已有路线。associated discrete circuit（ADC）模型保持等效导纳不变，因此避免每步重构导纳矩阵，但在高开关频率应用中可能出现精度和虚拟振荡问题；resistive switch model（RSM）可以预存所有可能拓扑的逆导纳矩阵，并结合非迭代开关状态预测减少在线计算；平均值模型可以使用大步长，但以失去开关细节为代价。并行化方面，带一步延迟的网络分割容易实现，却可能引入误差和数值不稳定；delay-free 分割精度更好，但实现更复杂，在论文所述背景中更常见于 CPU 平台。已有 FPGA 研究已在特定电路上做到 10–100 ns 量级的实时步长，困难在于硬件性能使步长不可能无限缩小。[pdf:E01]（PDF 物理页 1，Section I）

更接近本文的两类工作是 subcycle averaging / oversampling 与 variable time-step simulation。前者以更高采样频率定位边沿，再在较大的求解步长上使用开关信号平均值；后者允许数值步长随随机开关事件变化，同时只在一个更大的固定间隔上与现实时间同步。这些工作已经说明“事件采样频率、求解步长与同步间隔不必相同”，但本文进一步把 PWM converter 的开关周期提升为显式的主时间单位，并把调制信号到周期内事件序列的关系做成可预计算的 simulated modulation。作者把贡献分为 SPS 调度、DSS-EMT 形式以及支持多开关频率 converter 的 FPGA 通用求解器三部分。[pdf:E02]（PDF 物理页 2，Section I 与贡献列表）

因此，本文的区别不应表述成“首次使用 EMT”“首次使用 FPGA”或“首次使用 variable step”。更准确的说法是：作者改变了必须逐数值步与现实时间同步的假设，把可预测 PWM 周期内的事件定位与对外实时同步分开，再为这种可变子步推进配套一个适合预存系数和矩阵向量乘的 DSS-EMT 实现。

## § 3 — 重建作者的思考路径

可以从经典 Dommel EMT 求解器逆向走到本文。经典流程先由支路历史电流形成节点注入电流，解节点电压，再回算支路电压和电流。作者把这些中间变量消去，将历史电流保留为状态 \(X\)，外部注入保留为输入 \(U\)，节点电压和支路电流组成输出 \(Y\)，得到开关状态相关的离散状态空间表达式。Eq. (10) 把一次推进写成 \(X^{(n+1)}=A(S^{(n)})X^{(n)}+B(S^{(n)})U^{(n)}\) 和 \(Y^{(n)}=C(S^{(n)})X^{(n)}+D(S^{(n)})U^{(n)}\)，Eq. (11) 则把 \(A,B,C,D\) 追溯到支路导纳、节点导纳和关联矩阵。[pdf:E03]（PDF 物理页 3，Eq. (5)–(11)，Section II-B）

接下来会观察到：高频 PWM 电路虽然载波很快，但一个开关周期内并不是每个纳秒都产生新的拓扑；真正改变微分方程系数的是有限个开关边沿。如果调制量在一个周期内近似不变，而且载波规则已知，那么周期内的开关状态序列和每段持续时间可以在求解前由调制量算出。于是，研究者自然会把“对外每个周期同步一次”和“对内在事件处分段积分”组合起来：周期外保持简单、固定的控制器接口，周期内用较少但物理上有意义的子步推进。

最后一个工程问题是如何把这种思路映射到 FPGA。只要每个 \(S_i,\Delta t_{si}\) 对应的系数矩阵能够离散化、预计算并索引，在线核心就不再是求逆或重构网络，而是从 BRAM 取矩阵并执行固定结构的 matrix-vector multiplication（MVM）。这条思考路径说明，SPS 的加速主要来自减少在线推进次数和放宽同步期限，而不是来自一个新的通用线性代数算法。

## § 4 — 核心 Intuition

SPS 的核心是：真实控制器只要求仿真器在正确的外部时刻给出正确的输入输出，不要求每个内部积分子步都与墙钟同步。对周期性 PWM converter，可以先从调制信号恢复一个开关周期内有限的事件顺序，再只在这些事件之间推进模型。这样既保留了开关边沿的时间位置，又把实时 deadline 从几十纳秒级内部步长放宽到微秒级开关周期。[pdf:E04]（PDF 物理页 4，Fig. 2、Table I 与 Fig. 3）

## § 5 — 具体方法与完整 Pipeline

以论文的 OBC 为例，输入是一套真实 DSP controller 在每个控制/开关周期给出的调制信号，处理对象由 50 kHz 的三相 PFC rectifier 和 200 kHz 的 DAB 组成，输出是送回控制器的电压、电流等仿真量。完整 pipeline 如下。

1. **确定主时间尺度。** 对每个子电路取其开关周期 \(T_{sw}\) 作为主步长 \(\Delta t_m\)。在第 \(n\) 个周期内，用调制量 \(D^{(n)}\) 与载波的关系得到每个子步的开关状态 \(S_i^{(n)}\) 和持续时间
   \[
   \Delta t_{si}^{(n)}=f_i(D^{(n)}).
   \]
   周期内依次执行这些子步，但只有主步边界需要与现实时间同步。对 SPWM rectifier，Eq. (14) 由三个调制量相对三角载波的位置给出六个事件时刻，形成七个子步。[pdf:E05]（PDF 物理页 4，Eq. (12)–(14)，Section III-C 与 IV-A）

2. **执行 PFC 的 simulated modulation。** 三相 PFC 有六个互补门极信号。算法先把 \(D_1,D_2,D_3\) 从大到小排序，再按排序修正 Table III 的状态编号，最后用 Eq. (14) 计算各子步持续时间。对图示的 \(D_1\ge D_2\ge D_3\)，七段状态顺序是 I、II、IV、VIII、IV、II、I；这不是在每个细步采样载波，而是直接由调制量重建事件序列。[pdf:E06]（PDF 物理页 5，Fig. 4、Fig. 5、Table II、Table III 与 SPWM 算法框）

3. **执行 DAB 的 simulated modulation。** 论文的 DAB 使用 single phase shift modulation，一个周期被分成四个子步，状态顺序为 I、II、III、IV，持续时间依次为 \((1-D)T_{sw}/2\)、\(DT_{sw}/2\)、\((1-D)T_{sw}/2\)、\(DT_{sw}/2\)。这说明 SPS 需要为具体 modulation scheme 建立“调制量 → 状态序列与持续时间”的关系，而不是无条件适用于任意未知边沿。[pdf:E07]（PDF 物理页 6，Fig. 6、Table IV 与 Table V）

4. **用 variable-step DSS-EMT 推进。** 对第 \(i\) 个子步，求解器按 Eq. (13) 使用 \(S_i^{(n)},\Delta t_{si}^{(n)}\) 选择系数矩阵，更新 \(X_{(i)}^{(n)}\) 并生成 \(Y_{(i)}^{(n)}\)。不同状态和离散子步长度所需的 \(A,B,C,D\) 在初始化阶段预计算并写入存储器；在线阶段只做索引、MVM 和累加。论文还通过增加状态组合与子步来表示开路故障和 dead-time，而不是改变主求解结构。[pdf:E08]（PDF 物理页 6，Fig. 7、Section IV-C 与 V-A）

5. **组织多速率网络。** OBC 被分成 PFC 与 DAB 两个子电路，主步长分别为 20 μs 和 5 μs；decoupling interface 的更新步长取所有主步长的最大公约数，因此该例为 5 μs。初始化时离散化子步时间分辨率 \(\Delta t_b\)，预存系数矩阵；主循环内先交互控制器与解耦接口，再对每个子电路执行 simulated modulation 和按序子步求解，最后输出该周期最后一个子步的结果。[pdf:E09]（PDF 物理页 7，Fig. 8 与 Section V-A）

6. **映射到 FPGA/HIL。** 实验平台由 NI PXIe-7975R FPGA simulator、TMS320F28335 DSP controller、IO module、host PC 和 oscilloscope 组成。矩阵系数采用 32 bit，状态/输入/输出向量采用 25 bit；矩阵归一化到 \([-1,1]\)，文中给出的格式分别是 \(\langle\pm32,1\rangle\) 与 \(\langle\pm25,14\rangle\)。四类 MVM \(A X,B U,C X,D U\) 并行执行，每个 MVM 再拆成逐行 dot product，并对 dot product 做 pipeline。[pdf:E09]（PDF 物理页 7，Fig. 8、Fig. 9 与 Section V）

论文**未报告**以下实现细节：\(\Delta t_b\) 的实际数值、\(Y_{on}/Y_{off}\) 的选值、定点溢出/舍入策略、单个 DP pipeline 的 initiation interval 与 latency、BRAM 的字宽和逐表存储布局、place-and-route slack、I/O 往返延迟、控制器执行时间、deadline jitter 分布以及完整 HIL loop 的 worst-case execution time（WCET）。因此，卡片不能把 Table VII 的 solver 计算时间外推成完整闭环 HIL 延迟，也不能把聚合资源数字外推到其他 FPGA 或任意规模网络。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的形式化推导，其作用是把适合 EMT 的 companion-circuit 模型变成适合 FPGA 预存矩阵和 MVM 的离散状态空间模型。

首先，采用 trapezoidal integration 后，电感和电容被替换为“等效导纳 + 历史电流源”。以支路导纳矩阵 \(Y_b\)、系统关联矩阵 \(M\)、节点导纳矩阵 \(Y_n\) 表示网络，经典 EMT 每步依次计算历史电流、节点注入、节点电压、支路电压与支路电流。作者消去中间变量后，把历史支路电流 \(I_h\) 作为状态：

\[
\begin{aligned}
X^{(n+1)} &= A(S^{(n)})X^{(n)}+B(S^{(n)})U^{(n)},\\
Y^{(n)} &= C(S^{(n)})X^{(n)}+D(S^{(n)})U^{(n)},
\end{aligned}
\]

其中 \(X=I_h\)，\(U=I_s\)，\(Y=[V_n,I_b]^T\)。Eq. (11) 给出

\[
\begin{aligned}
A=B&=\left(\beta-(\alpha+\beta)Y_bM^TY_n^{-1}M\right)\big|_{S^{(n)}},\\
C=D&=\left[-Y_n^{-1}M,\ I-Y_bM^TY_n^{-1}M\right]^T\big|_{S^{(n)}}.
\end{aligned}
\]

直观上，\(M\) 编码连接关系，\(Y_b\) 编码元件在给定步长下的 companion admittance，\(\alpha,\beta\) 区分电感和电容的历史项，而 \(S\) 选择当前开关拓扑。这样，网络拓扑与步长对在线计算的影响被压入了可预计算的矩阵。[pdf:E03]（PDF 物理页 3，Eq. (8)–(11)）

其次，SPS 把普通一步更新扩展到周期内的事件分段：

\[
\begin{aligned}
X_{(i)}^{(n)}&=A(S_i^{(n)},\Delta t_{si}^{(n)})X_{(i-1)}^{(n)}
 +B(S_i^{(n)},\Delta t_{si}^{(n)})U^{(n)},\\
Y_{(i)}^{(n)}&=C(S_i^{(n)},\Delta t_{si}^{(n)})X_{(i-1)}^{(n)}
 +D(S_i^{(n)},\Delta t_{si}^{(n)})U^{(n)}.
\end{aligned}
\]

工程意义是：开关周期仍是对外的一个“原子时间片”，但模型内部严格按拓扑保持不变的时间段依次积分。只要所有子步持续时间之和为 \(T_{sw}\)，最后一个子步结束时就回到下一个真实同步点。[pdf:E05]（PDF 物理页 4，Eq. (12) 与 Eq. (13)）

论文没有给出关于 variable substep 离散化误差、零阶保持 multirate interface 的稳定性、定点量化稳定裕度或 deadline 可调度性的形式化定理。作者只说明矩阵归一化是为了保留足够分数位并满足 eigenvalue stability 的精度需求，但没有展示量化误差上界或 pole/eigenvalue 扫描。因此，数学层面的贡献是模型重写与事件分段表达，不是一个经过证明的全局稳定性结论。

## § 7 — 实验设计与结论

**问题一：SPS 把主步长扩大到开关周期后，动态波形是否仍接近细步长基准？** 作者在 FPGA HIL OBC 上把 PSCAD 50 ns 仿真作为 benchmark；DAB 与 PFC 的 SPS 主步长分别是 5 μs 和 20 μs。工况先进入稳态，再把 dc bus reference 从 800 V 阶跃到 700 V，随后把输出电压 reference 从 400 V 调到 350 V。Fig. 10 对比了 AC 侧电压/电流、dc bus 电压、PFC modulation 和 DAB 输出/调制信号；作者结论是两组波形接近。[pdf:E10]（PDF 物理页 8，Fig. 10 与 Section VI-A）

**问题二：这种接近是否只发生在一个 switching frequency？** 作者把 DAB switching frequency 从 50 kHz 扫到 200 kHz，以输出直流电压相对 PSCAD 的 maximum absolute error \(E_{max}\) 和 error standard deviation \(E_{std}\) 比较 TSS 与 SPS。200 kHz 时，TSS 为 0.6013% / 0.1040%，SPS 为 0.5943% / 0.1051%；50–200 kHz 的五个点上，两者误差处于相近水平，而 SPS 使用的是 \(1/f_{sw}\) 主步长，TSS 使用 \(0.01/f_{sw}\) 步长。论文据此声称，SPS 可在主步长大 100 倍时保持与 TSS 接近的精度。[pdf:E11]（PDF 物理页 8，Table VI、Fig. 11 与相邻正文）

**问题三：方法能否覆盖不止一个标称 OBC 工况？** 作者又比较了 dc-dc converter、cascaded DAB、PFC switch-open fault 和带 0.2 μs dead-time 的 DAB。Fig. 12–14 中 SPS 与 PSCAD 的曲线基本重合，dead-time 图还标出了 0.2、1.8、0.2、0.3、0.2、1.8、0.2、0.3 μs 的子步序列。这个实验支持“已枚举的额外拓扑与 dead-time 可以塞入同一框架”，但它没有证明未知异步事件或自然换相也能被同样处理。[pdf:E12]（PDF 物理页 9，Fig. 12–14 与 Section VI-A）

**问题四：FPGA solver 能否在给定主步内完成？** 160 MHz compilation clock 下，PFC 的 setting time-step 为 20 μs、achieved time-step 为 17.6 μs、消耗 2817 ticks；DAB 对应 5 μs、2.03 μs 和 324 ticks。按表中定义，一个 tick 是 \(1/160\) μs。这证明已实现 solver 在这两个给定配置上有正的步内余量，但 PFC 余量只有约 2.4 μs，且表中没有 jitter、I/O 与控制器时间，因此不能称为完整闭环 WCET 已闭合。[pdf:E13]（PDF 物理页 9，Table VII 与 Table VIII）

**问题五：减少同步/求解次数是否真的带来计算量下降？** 在总仿真时长 0.2 s 的 non-real-time 模式下，50、80、100、160、200 kHz 五个点的 speed-up ratio 分别是 51.42、54.72、58.68、64.56、61.91。作者把“约 50–60 倍”加速归因于 SPS 更大的主步长，并说明这些 non-real-time 数据是为了方便测量 time cost，不能直接当作闭环实时 latency。[pdf:E14]（PDF 物理页 9，Section VI-B 与 Table VIII 讨论）

**问题六：加速是否只是把成本转移到更多 FPGA 资源？** 在同一个 OBC、K7-410T 对比中，SPS 报告 74,361 flip-flops、65,095 LUTs、434 BRAM、32 DSP48；TSS 报告 196,869 flip-flops、137,262 LUTs、91 BRAM、747 DSP48。SPS 显著增加 BRAM，占用 54.6%，但减少 logic 和 DSP；作者解释为预存系数矩阵换取 MVM 资源复用。Table IX 还列出其他论文，但电路、器件和方法不同，不能据此做严格同条件优劣排序。[pdf:E15]（PDF 物理页 10，Table IX）

作者自己给出的边界是：多速率接口使用 zero-order hold，后续可考虑 interpolation/extrapolation 以改善 numerical stability；IGBT-diode pair 被当作 ideal controlled switch，自然换相需要未来加入 switch-status prediction。[pdf:E16]（PDF 物理页 10，Section VII）实验参数还包括 OBC 的 380 V 线电压、1 mH 输入电感、1000 μF dc-side capacitor、20 μH transformer leakage inductance、1000 μF output capacitor、16 Ω load，以及 50/200 kHz 两级 switching frequency。[pdf:E17]（PDF 物理页 11，Table AVIII）这些设置足以复现实验范围，却不包含 SiC/GaN 器件动态、寄生参数、温度变化、物理功率级测量或真实 hardware switching waveform。因此，论文验证的是 source-closed 数字模型与 FPGA HIL 求解器，而不是 power hardware-in-the-loop（PHIL）或器件级开关瞬态。

## § 8 — Take-aways

**5 句话。** 第一，SPS 把实时同步间隔从内部数值步长提升到开关周期，同时仍在周期内按开关事件分段积分。第二，DSS-EMT 把在线求解改造成可预存系数矩阵的 MVM，适合 FPGA pipeline 和资源复用。第三，在论文的 50/200 kHz OBC 上，5/20 μs 主步能够在 2.03/17.6 μs 的 solver 时间内完成，并且相对 PSCAD 的误差与 100 倍更细的 TSS 接近。[pdf:E11][pdf:E13] 第四，代价是预存矩阵带来的 BRAM 增长，以及对可预测周期调制、理想受控开关和已知事件序列的依赖。[pdf:E15][pdf:E16] 第五，最可靠的结论是“对论文覆盖的 PWM converter 和工况，事件驱动的周期级同步可显著减轻实时负担”，而不是“任意 200 kHz power converter 都已被解决”。

**3 句话。** 本文最重要的设计动作是拆开“事件定位”和“墙钟同步”两个时间尺度。它以预计算存储换取在线 MVM，并在一个 FPGA OBC HIL 案例中展示了相近误差和更低 time cost。其外推边界由 modulation 可预测性、异步事件处理和完整闭环 WCET 是否闭合决定。

**1 句话。** 对开关序列可由周期初调制量可靠预测的 converter，SPS 用“周期外同步一次、周期内按事件求解”换来了数量级更宽松的实时预算。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在每个开关周期开始时，调制量足以确定该周期内完整且正确的开关事件序列，并且该序列在周期执行期间不会被未知异步事件改写。** PFC 算法明确把 \(D_1,D_2,D_3\) 视为周期内常数并由排序恢复七个子步，DAB 也由单个 \(D\) 直接生成固定四段序列。[pdf:E06][pdf:E07]

这个假设一旦失效，问题不只是误差稍微增大，而是求解器会选错 \(S_i\) 或错过事件时刻，随后使用错误的拓扑矩阵推进到下一个同步点。现实中可能破坏它的因素包括 cycle-by-cycle current limit、desaturation protection、随机通信延迟、pulse skipping、控制器在周期内更新比较值、二极管自然换相以及依赖状态轨迹才发生的 commutation。论文通过为“已知的 sw1 开路”和固定 dead-time 增加预枚举状态证明了框架的可扩展性，但这仍是离线知道事件类型后的扩展；作者也明确承认当前 IGBT-diode pair 是 ideal controlled switch，自然换相预测属于 future work。[pdf:E12][pdf:E16]

因此，论文为这个假设提供的是 SPWM、single-phase-shift DAB、预设故障和固定 dead-time 的正例，没有提供异步保护边沿、随机 event ordering 或自然换相的压力测试。**基于证据的推断**是：SPS 的有效范围首先由 event predictability 决定，而不是只由标称 switching frequency 决定。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 NI-PXI 平台，而是“主步放大 100 倍后，事件分段是否仍保持与 TSS 相近的误差”这一核心 claim。

- **数据与模型：**按 Table AVIII 建一个 DAB 或更小的 bidirectional dc-dc EMT 模型；生成确定性的 modulation trace，同时注入论文式 reference step。用 50 ns fixed-step TSS/PSCAD 等价模型产生参考轨迹，再实现 Eq. (12)–(13) 的 SPS，主步取 \(T_{sw}\)。[pdf:E11][pdf:E17]
- **实现：**只做 RSM、trapezoidal companion model、DSS 矩阵预计算和事件序列求解。先使用 double precision 隔离调度思想，再切到论文的 32 bit matrix / 25 bit vector 量化，观察误差是否主要来自事件处理还是定点化。[pdf:E09]
- **测量：**比较 \(E_{max}\)、\(E_{std}\)、稳态偏差、reference step 后的峰值与 settling trajectory；同时记录每个物理开关周期需要的子步数、MVM 次数和 wall-clock cost。
- **支持条件：**在论文采用的 50–200 kHz 扫频中，SPS 与 TSS 的 \(E_{max},E_{std}\) 差异保持在同一误差量级，同时每周期求解次数和总 time cost 明显下降，结果就支持论文的核心机制。[pdf:E11]
- **反驳条件：**若结果对 \(\Delta t_b\) 极敏感、在 reference step 后出现系统性相位/峰值偏差、量化后失稳，或保持精度所需的子步/矩阵数量抵消主要加速，则核心 claim 在该最小模型上不成立。

最后增加一个不改变主体工作量的 boundary test：在随机 5% 周期内插入一个周期中途的保护关断，但故意不提前告诉 SPS event generator。它不是复现论文已验证的 nominal claim，而是用来判断第 9 节的核心假设有多脆弱。

## § 11 — 最强反例设计

最强反例是一类“周期内因状态触发而非由周期初 modulation 决定”的 converter 运行场景。构造 DAB 或 PFC，使 cycle-by-cycle overcurrent protection 在载波周期中途关断门极，同时加入二极管自然换相；保护触发时刻由瞬时电流和噪声决定，因此无法从周期初的 \(D\) 预先枚举。用高分辨率 EMT 或示波器记录作为参考，比较三种求解器：论文使用的 50 ns TSS benchmark、只使用周期初 event schedule 的 SPS、以及允许周期内 event interrupt 并局部重排剩余子步的 SPS。[pdf:E10]

攻击点应落在因果时序而不是平均波形上：测量首次错误拓扑的持续时间、过流峰值、保护后一个周期内的电流积分误差、dc bus overshoot，以及错误是否穿过 multirate zero-order-hold interface 传播到另一个子电路。若原始 SPS 在 nominal waveform 上仍好看，却在保护周期漏掉边沿并产生一个 \(T_{sw}\) 量级的错误响应，而 interrupt 版本恢复正确，则“加速来自 DSS-EMT 本身”这一替代解释会被削弱，真正瓶颈被定位为预先固定 event schedule。该反例不会否定 SPS 在规则 PWM 工况下的结果，但会直接否定其对未限定 high-switching-frequency converter 的广泛适用表述。

## § 12 — Follow-up Research Idea

电力电子实时仿真领域的高影响工作通常不只看平均加速比，还看模型真实性、确定性 deadline、跨拓扑可复现性、硬件资源与时序闭合，以及与真实控制器/功率硬件交互时能否暴露危险 failure mode。基于这一标准，一个值得推进但**不声称已有 novelty**的候选方向是：**面向异步事件的 event-contract real-time simulator**。

（a）未满足需求是，周期性 PWM 可以预生成 event schedule，但 protection、自然换相和通信触发会在周期内改写 schedule；现有 SPS 正例与这类事件之间存在明显证据缺口。（b）研究价值不在于再加一个 adaptive-step 模块，而在于把实时仿真的接口契约改成“周期性可预测事件走预计算快路径，异步/状态触发事件走有界 interrupt-correction 路径”，并同时给出 accuracy bound 与 deadline bound。（c）可以借鉴 discrete-event simulation 的 timestamp ordering、real-time systems 的 mixed-criticality scheduling，以及 optimistic simulation 的局部 rollback，但必须把 rollback 限制在当前 switching period 内，避免不可控延迟。（d）第一个可证伪实验就是第 11 节的随机 overcurrent/natural-commutation benchmark：若 interrupt-correction 不能在所有事件密度下同时保持参考误差和硬 deadline，方向就失败。（e）它与本文的实质区别是，本文在周期开始时固定 \(\{S_i,\Delta t_{si}\}\) 并顺序执行；候选系统把 event schedule 本身变成运行期受验证、可被高优先级事件修订的对象。

在没有对 switch-event oversampling、variable-step EMT、real-time discrete-event HIL 和自然换相预测进行额外系统检索前，这只能称为由本文证据边界驱动的候选研究问题，不能称为新的方法或已成立的 novelty。
