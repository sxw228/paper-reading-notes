# A Device-Level Transient Modeling Approach for the FPGA-Based Real-Time Simulation of Power Converters

- 作者：Hao Bai；Huan Luo；Chen Liu；Damien Paire；Fei Gao
- 出处：IEEE Transactions on Power Electronics, Vol. 35, No. 2
- 年份：2020
- DOI：10.1109/TPEL.2019.2918590
- Zotero key：RQUEF5PX
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。`[pdf:E..]` 指向可打开的页面证据，页码按 PDF 文件首页为物理第 1 页计。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的实时仿真矛盾：要看清 IGBT 开关瞬态，步长必须短；但把器件的非线性、寄生电容、杂散电感和二极管反向恢复都放进网络求解，又会显著增加每一步的计算量。作者希望在 FPGA 的固定截止时间内，同时保留“器件级波形”和“整机网络响应”，而不是只能二选一。论文把这个目标落在了一个可检验的工程指标上：在 FPGA 上以 50 ns 固定步长运行含器件级 IGBT/diode 的 dc-dc-ac 变换器模型，并用离线 Saber 结果检查误差。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，不只是因为波形更好看。器件级模型能直接给出开关管的电压、电流应力、寄生参数影响、开关损耗和效率；这些量关系到控制器 HIL 测试之外的器件选型、热设计与故障边界。系统级理想开关模型可以复现较慢的电气动态，却不能真实表达 IGBT 的非线性开通、关断、尾电流与二极管反向恢复。[pdf:E01]（PDF 物理页 1，Introduction 右栏）

## § 2 — 前人工作与不足

作者把既有方法分成三类。第一类是理想开关、两值电导、associated discrete circuit 和 Thevenin/Norton 等系统级或准理想模型；它们适合高吞吐网络仿真，但不包含真实的 IGBT 非线性开关瞬态。第二类把静态网络与动态器件模型分开算；动态量必须等静态网络更新后才能更新，形成额外计算延迟，而且器件级行为没有真正参与同一个变换器网络方程。第三类让非线性器件等效电路直接进入网络求解，但 Newton-Raphson 等迭代使可实现步长停留在微秒量级；作者还指出，当时基于 curve fitting 的器件等效模型实现了 500 ns 步长，对小于 500 ns 的快速瞬态仍不足。[pdf:E01]（PDF 物理页 1，Introduction 右栏）[pdf:E02]（PDF 物理页 2，Introduction 延续）

因此，论文真正要补的缺口不是“此前没有器件模型”，而是缺少一种能让器件瞬态参与实时网络计算、又不把每步计算拖入非线性迭代的表示。作者采用的取舍是牺牲一部分连续非线性精度，把开关过程改写成少数可判别、可线性求解的物理阶段。[pdf:E02]（PDF 物理页 2，Section II 前的贡献概述）

## § 3 — 重建作者的思考路径

可以从此前已有的三个事实重建这条路径。第一，感性负载下的 IGBT/diode 开关波形并非无结构的任意非线性：IGBT 依次经历 cutoff、active、saturation，二极管则有 ON/OFF 与反向恢复过程。第二，电感电流与电容电压可以通过 circuit partitioning 在一个时间步内作为半桥的输入源，半桥的端口电压、电流再返回外部网络；这让器件子模型可以与大网络暂时解耦。第三，FPGA 适合固定数据通路、并行分区和查表，却不擅长时延不定的迭代求根。[pdf:E02]（PDF 物理页 2，Fig. 1、Fig. 2 与 Section II-A）

由此，一个自然的研究路线是：先用器件工作区边界把一次硬开关瞬态切成有限阶段，再把每个阶段写成连续线性状态方程；阶段内用固定代价的隐式积分，阶段间用有限状态机和零交叉条件切换；最后用外部网络分区把这些器件求解器并行嵌入整机。这个段落是基于论文结构的逆向推断，不是作者逐字陈述。

## § 4 — 核心 Intuition

核心 intuition 是：不要在每个 50 ns 步内反复求解完整的非线性 IGBT，而是先判断器件正处于哪一个物理阶段，只求该阶段对应的线性连续模型。外部网络把电感电流和电容电压当作已知输入，器件模型返回端口量；于是复杂非线性被转换成“有限状态机选择 + 固定矩阵运算 + 查表”。[pdf:E03]（PDF 物理页 3，Fig. 3 与四阶段说明）[pdf:E04]（PDF 物理页 4，Fig. 4、Eq. (16)-(17)）

## § 5 — 具体方法与完整 Pipeline

以论文中的半桥为例，完整 pipeline 如下：

1. **网络输入。** 通过 circuit partitioning，把外部电感电流 \(I_L\) 和电容电压 \(V_{cap}\) 作为半桥器件子模型本步的外部输入；子模型需要返回 \(v_{ce}\) 与二极管/直流侧电流等端口量。[pdf:E02]（PDF 物理页 2，Fig. 1）
2. **选择正在开关的一对器件。** 根据 \(I_L\) 的方向判断上管或下管 IGBT/diode pair 是当前 switching pair；另一对器件仍需更新状态，但不走同一开关瞬态路径。[pdf:E06]（PDF 物理页 6，Fig. 6）
3. **识别四个阶段。** Phase 1 是 IGBT cutoff、diode ON；Phase 2 是 IGBT active、diode ON；Phase 3 是 IGBT active、diode OFF；Phase 4 是 IGBT saturation、diode OFF。边界分别来自 \(v_{ge}\) 与阈值、diode reverse-recovery 条件以及 \(v_{ce}\) 与饱和压降的关系。[pdf:E03]（PDF 物理页 3，Fig. 3 与 Section II-A）[pdf:E04]（PDF 物理页 4，Fig. 4）
4. **求解阶段内连续行为。** 模型保留 gate-emitter/collector-emitter 电压、tail-current 电容状态和 reverse-recovery 电感电流等状态；不同阶段用相应线性化方程描述，并统一成状态空间形式。阶段内采用 Backward Euler，避免每步 Newton-Raphson 迭代。[pdf:E03]（PDF 物理页 3，Eq. (1)-(12)）[pdf:E04]（PDF 物理页 4，Eq. (13)-(17)）
5. **查表处理非线性电容。** \(C_{cg}\) 和 \(C_{ce}\) 仍随 \(V_{cg}\) 变化，但作者把 datasheet 曲线离散成查找表，并用前一时间步的 \(V_{cg}\) 取值；与电容相关的系数由 host 预计算后存入 FPGA LUT。[pdf:E04]（PDF 物理页 4，Eq. (17) 后正文）[pdf:E05]（PDF 物理页 5，Section III-A）
6. **更新全局网络。** 外部线性网络以 Forward Euler 分区，器件子模型以 Backward Euler 求解；所有分区在本步独立计算后，再汇总端口量、全局变量与 history values，供下一步使用。[pdf:E05]（PDF 物理页 5，Fig. 5、Eq. (18)-(22) 与 Section III-A）
7. **FPGA 调度。** 四个阶段各自映射到 case structure，由 phase selector 驱动；整机用 SCTL 固定在 20 MHz，因而每个实时步为 50 ns。[pdf:E06]（PDF 物理页 6，Fig. 6）[pdf:E08]（PDF 物理页 8，Fig. 12 下方与 Table IV）

物理上，这条 pipeline 的关键是把“本步网络给器件什么电流/电压”和“器件本步给网络什么端口响应”分开，并把器件内部的非线性变化限制在可判别的阶段内。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的形式化数学。四个阶段虽然方程不同，但都被写成

\[
\dot{x}_i=A_i x_i+B_{i1}u_{i1}+B_{i2}u_{i2},
\]

其中 \(x_i=[v_{ge},v_{ce},v_{Ctail},i_{Lrr}]^T\) 是器件内部状态，\(u_{i1}=[V_g,V_{th},V_{d(on)},V_{s(on)}]^T\) 是内部源，\(u_{i2}=[I_L,V_{cap}]^T\) 是外部网络注入。直观地说，\(A_i\) 决定当前阶段内部状态如何自演化，两个 \(B\) 分别把驱动/器件参数和外部网络作用带入状态变化。[pdf:E04]（PDF 物理页 4，Eq. (16)）

对时间步 \(h\) 使用 Backward Euler 后，

\[
x_i^{n+1}=\hat A_i x_i^n+\hat B_{i1}u_{i1}^{n+1}+\hat B_{i2}u_{i2}^{n+1},
\]

其中 \(\hat A_i=(I-hA_i)^{-1}\)，\(\hat B_{i1}=h(I-hA_i)^{-1}B_{i1}\)，\(\hat B_{i2}=h(I-hA_i)^{-1}B_{i2}\)。这一步的工程意义是把阶段内连续微分方程变成固定矩阵乘加；当阶段和电容 LUT 条目已知时，不再需要在线迭代求根。[pdf:E04]（PDF 物理页 4，Eq. (17)）

外部网络则用 Forward Euler，并通过端口输入输出消元与器件离散式合成全局 Eq. (22)。作者给出的稳定性判据是：合成更新矩阵 \(\hat A_{ne}\) 的全部特征值位于复平面的单位圆内。[pdf:E05]（PDF 物理页 5，Eq. (18)-(22) 与稳定性段落）需要谨慎的是，论文给出了判据与结构推导，但没有在正文中展示覆盖所有参数和工作点的特征值扫描；因此“稳定性已被普遍证明”不能从本文直接推出。

## § 7 — 实验设计与结论

**问题一：器件级开关瞬态是否接近高精度参考？** 作者在 FPGA 上运行 double-pulse test，以 Saber 的 `igbt1_3` 模型为参考，器件基于 ABB 5SND 0800M170100，杂散电感为 40 nH，覆盖 200-1000 A 集电极电流与 400-1200 V 电压，实时步长 50 ns。结果是：Tables I-II 中除电流上升时间 \(t_r\) 外，其余开关时间相对误差低于 5%；\(t_r\) 误差为 5%-8%，作者把它归因于 50 ns 时间分辨率和 transfer characteristic 线性化。开通、关断损耗误差在所测工况下低于 5.1%。[pdf:E06]（PDF 物理页 6，Fig. 7、Tables I-II 与验证正文）[pdf:E07]（PDF 物理页 7，Fig. 8 与左栏正文）

**问题二：方法能否扩展到完整变换器并满足实时 deadline？** 作者选择两相 interleaved boost 级联三相 two-level inverter，将电路分成九个子电路；含开关的 Sub 2-6 用所提 IGBT/diode model，其余分区求解滤波电容和负载。所有变量采用 per-unit 缩放和 signed 40-bit 定点表示，顶层 SCTL 运行于 20 MHz，实现 50 ns 步长且报告无 timing violation。[pdf:E07]（PDF 物理页 7，Fig. 9-11、Table III 与 Section IV-A/B）[pdf:E08]（PDF 物理页 8，Fig. 12 下方正文）

**问题三：整机精度与资源代价如何？** 20 ms 开环测试中，FPGA 与 Saber 的三相电流、boost 电流、母线电压、器件电压电流、功率和效率进行比较。Table V 的各平均误差为 0.059%-0.285%；十个状态量组成的矩阵相对 Saber 的 two-norm error 为 0.162%，而论文设置的 system-level model 为 8.146%。XC7K410T 上使用 35.6% slices、9.3% registers、25.0% LUTs、11.4% block RAMs 和 21.4% DSP48s。[pdf:E08]（PDF 物理页 8，Fig. 12 与 Table IV）[pdf:E09]（PDF 物理页 9，Tables V-VI、Eq. (23)-(24)）

这些结果支持“在该器件、该硬开关模型和该案例规模下，50 ns 固定步长可实时运行且比所用系统级基线更接近 Saber”。它们不等于对任意拓扑、任意快速器件或真实硬件测量的普遍验证；论文的参考主要是离线仿真工具，而不是示波器实测波形。

## § 8 — Take-aways

**5 句话：** 这篇论文把 IGBT/diode 瞬态按器件工作区和二极管状态分为四段。每一段使用线性连续模型，段内 Backward Euler，段间有限状态机切换。外部网络通过 Forward Euler circuit partitioning 与器件子模型解耦，使 FPGA 可以并行求解。作者在 XC7K410T 上实现 20 MHz SCTL，即 50 ns 固定步长，并以 Saber 验证 double-pulse 与 dc-dc-ac 案例。[pdf:E06]（PDF 物理页 6，Fig. 6-7）精度的代价主要来自线性化、有限时间分辨率和资源随开关数量增长。[pdf:E09]（PDF 物理页 9，Limitations）

**3 句话：** 最重要的贡献不是一个更复杂的器件等效电路，而是把物理开关过程重写成适合 FPGA 的确定时延计算图。证据表明它在论文所测工况下兼顾了 50 ns deadline、器件波形和整机精度。它的边界同样清楚：低于 50 ns 的瞬态无法被真实表达，单 FPGA 资源会限制可扩展的开关数量。[pdf:E09]（PDF 物理页 9，Limitations）

**1 句话：** 用物理阶段把连续非线性变成有限状态的线性求解，是本文实现器件级 50 ns FPGA 实时仿真的核心。

## § 9 — 最脆弱的假设

最脆弱的假设是：实际 switching trajectory 总能按 hard-switching 条件单向穿过论文定义的四个阶段边界，使 phase selector 在一个步长内得到唯一、无抖振的阶段。作者明确以 hard-switching 为条件，并认为 gate signal 初始化、边界顺应波形趋势和单向转换足以保证没有 chattering。[pdf:E04]（PDF 物理页 4，Fig. 4 与 phase identification 正文）

这个假设一旦失效，核心贡献会直接受损，因为错误阶段意味着选择错误的线性方程，而不只是多一点数值误差。在 soft switching、寄生振铃、门极噪声、反向恢复多次过零或一个 50 ns 步内跨越多个边界时，状态可能并非单向；基于前一步 \(V_{cg}\) 的电容 LUT 还可能进一步推迟边界判断。这是基于模型结构的风险推断。论文给出了典型 hard-switching 的 Saber 对比，但没有报告上述边界工况的实验，因此该假设尚未被广泛验证。

## § 10 — 最小复现实验

一周内最小复现应只做 single IGBT/diode pair 的 double-pulse test，不必先搭完整 dc-dc-ac。使用论文同类的 5SND 0800M170100 参数，建立四阶段状态机、Eq. (16)-(17) 的 Backward Euler 更新和基于前一步 \(V_{cg}\) 的电容 LUT；外部参考用 Saber、SPICE 或另一种经收敛检查的高分辨率离线模型。测试至少覆盖 400/400、600/600、800/800、1000 V/1000 A 四个文中图示工况，并固定 50 ns 步长。[pdf:E06]（PDF 物理页 6，Fig. 7 与 Tables I-II）

测量 \(v_{ce}\)、\(i_c\)、\(v_{ge}\)、turn-on/off delay、rise/fall time，以及 \(E_{on}\)、\(E_{off}\)。若除 \(t_r\) 外的开关时间误差大体不超过 5%、\(t_r\) 处于论文报告的 5%-8% 偏差范围、损耗误差不超过约 5.1%，且每一步的计算图能在 50 ns deadline 内完成，就支持论文最核心的可实现性 claim；若阶段误判频繁、误差明显越界或 deadline 只能靠删掉寄生参数满足，则反驳该 claim。[pdf:E07]（PDF 物理页 7，Fig. 8 与验证结论）

## § 11 — 最强反例设计

最强反例不是再换一个常规电流点，而是制造“一个固定步内多次跨阶段边界”的工况。可选用更快的 IGBT/SiC 等效器件或加入可控的 gate-loop/commutation-loop 寄生，使 \(v_{ge}\)、\(v_{ce}\) 和反向恢复电流在阈值附近振铃；同时安排 soft-switching 到 hard-switching 的过渡。用 1 ns 或更细的收敛参考追踪真实事件序列，再以原论文 50 ns solver 运行相同电路，记录漏掉的边界、错误 phase、峰值应力误差和损耗误差。

如果参考解在一个 50 ns 宏步内发生 Phase 2→3→2 或跨过两个以上阶段，而 FPGA 状态机仍只能单向切换一次，那么即使宏观电流 RMS 仍接近，器件级峰值与损耗 claim 也已经失败。这个反例直接攻击论文承认的时间尺度边界：作者明确指出低于 50 ns 的瞬态超出模型的真实表达能力，且更快开关器件会带来挑战。[pdf:E09]（PDF 物理页 9，Limitations）

## § 12 — Follow-up Research Idea

电力电子实时仿真领域通常同时看重物理保真、确定性 deadline、硬件资源、可扩展拓扑规模以及可复现的板级/HIL 验证；只把离线误差再降一点，通常不足以形成高影响贡献。

**候选研究想法：确定宏步、事件自适应微步的可验证器件求解器。** 未满足的需求是：控制器与外部网络仍要求固定 50 ns I/O 节拍，但器件内部的真正事件可能远快于 50 ns。可以把问题从“所有状态都按同一个固定步长推进”改成“外部端口每 50 ns 确定交付，器件内部在本宏步内按误差界和事件界自适应执行有限个微步”，并为最坏微步数设置可综合的硬上限。这可能带来本领域认可的价值，因为它直接挑战本文最脆弱的时间尺度假设，同时保留 HIL 所需的确定时序。

相邻领域可借鉴 hybrid systems 的 event localization、validated numerics 的局部误差界，以及 real-time scheduling 的 worst-case execution time 分析。第一个可证伪实验就是第 11 节的振铃/soft-switching 工况：若在同等 FPGA 资源和固定 50 ns 端口 deadline 下，内部微步仍不能显著降低峰值与损耗误差，或最坏事件密度迫使超时，那么这个想法失败。它与本文的实质区别不是再增加一个阶段或更换器件参数，而是把统一固定步长的求解目标改成“宏观确定节拍 + 微观事件分辨率 + 明确误差界”。由于本次只阅读了源 PDF、没有对外检索紧密相关工作，这只是候选方向，不声称 novelty。
