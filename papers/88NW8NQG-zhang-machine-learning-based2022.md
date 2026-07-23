# Machine Learning Based Modeling for Real-Time Inferencer-in-the-Loop Hardware Emulation of High-Speed Rail Microgrid

Zhang, Songyang; Liang, Tian; Cheng, Tianshi; Dinavahi, Venkata. IEEE Journal of Emerging and Selected Topics in Industrial Electronics, 2022. DOI: 10.1109/JESTIE.2022.3179959.

证据标记 `[pdf:E..]` 对应同目录 `_evidence/` 下的 PDF 页面上下文图。下文把作者明确声称、基于证据的推断和候选研究判断分开陈述。

## § 1 — 研究问题与重要性

论文要解决的不是“神经网络能否拟合一个电力电子器件”这一宽泛问题，而是：能否把覆盖高铁微电网多种器件和时间尺度的 machine-learning 模型放进真实 FPGA 实时仿真闭环，并周期性用新数据刷新模型，同时守住系统级 1 μs 和器件级 50 ns 的时间步长。作者选择的系统包含自耦变压器整流单元 ATRUS、储能 ESS、TLC-PMSM 推进支路以及 MMC-IM 推进支路，因而同时面对网络耦合、机电动态和开关瞬态。[pdf:E01] [pdf:E04]

其物理意义是：传统 EMT 求解器需要在每个时间步推进网络和器件状态，详细模型越多、步长越小，计算负担越难在真实时钟截止前完成；纯黑盒的大网络虽有拟合能力，却把大量无关变量和参数一起送入矩阵运算，消耗 FPGA 资源并拉长延迟。论文希望把电路分区知识变成 NN 的结构约束，让各局部模型并行推断，再用在线训练吸收温度、老化和环境变化。[pdf:E02] [pdf:E03]

作者报告其 IIL（inferencer-in-the-loop，即让 FPGA 上的 NN 推断器处在实时数据更新闭环中）由 referencer、GPU 训练集群和 FPGA inferencer 三部分组成，并声称最终可在 1 μs/50 ns 两个层级完成实时仿真、误差控制在 0.2% 内。[pdf:E07] [pdf:E12] 这项工作的价值因此不只在“更快拟合”，而在尝试建立从数据采集、训练、权重更新到硬件实时执行的完整链路。

## § 2 — 前人工作与不足

论文把已有方法分成三条线。第一条是传统 EMT、TLM 和器件解析模型：它们保留明确物理结构，但大规模 MMC 网络需要分解，详细 IGBT 模型还可能包含 Newton-Raphson 迭代或指数函数，难在很短步长内完成。[pdf:E04] [pdf:E05] 第二条是一般 ANN/RNN 建模：LNN 把对象当成整体黑盒，拟合能力强，却需要更大的数据集、矩阵和硬件资源；作者此前的三步 RNN converter 模型可做到小于 1% 的误差，但对 PMSM 为保持稳定还要加低通滤波，牺牲了动态带宽。[pdf:E02] [pdf:E06] [pdf:E10] 第三条是已有 FPGA/GPU 实时计算；论文指出 FPGA 适合固定、并行、可定制位宽的 inferencer，GPU 更适合迭代训练，但此前 ML 很少用于电力系统/电力电子实时建模与硬件加速闭环。[pdf:E02]

作者认为真正缺口在“结构、实时性和更新”三者没有合在一起：只用通用 LNN，资源和延迟太高；只用解析模型，复杂非线性与参数变化难处理；只做离线训练，模型无法追踪设备变化。PNN 和 PNNCF 因此不是单纯换一种网络，而是把电路依赖和参数是否变化显式编码进模型边界。[pdf:E03] 需要注意的是，论文的 related work 主要依靠作者给出的文献脉络；本卡按禁联网边界没有额外检索，不能据此独立确认 novelty。

## § 3 — 重建作者的思考路径

一种不预设论文答案的重建路径如下。

1. 实时 EMT 的硬约束是“每一步必须在 deadline 前结束”。当 MMC 子模块数增加、器件模型进入纳秒级开关瞬态时，直接扩大传统求解或黑盒 NN 都会触碰资源与延迟上限。[pdf:E04] [pdf:E05] [pdf:E06]
2. 电路并非全连接因果系统：一个节点主要受相邻节点影响，MMC 也能借 TLM 的历史源和 Thévenin 等效拆成并行子电路。因此，大矩阵里的大量零耦合项不是偶然，而是可利用的结构信息。[pdf:E03] [pdf:E04]
3. 如果按真实耦合边界把 LNN 拆成多个小网络，就能减少矩阵维度并并行执行；如果某一类设备的参数在部署时固定，还可把参数从 runtime feature 移到权重/偏置，进一步减少输入和乘加。[pdf:E03]
4. 仅有小模型还不够，因为设备会随环境和寿命变化。于是需要一个 referencer 产生新数据、GPU 重新训练、FPGA 周期性接收权重的闭环，并用数据选择降低在线训练负担。[pdf:E07] [pdf:E08] [pdf:E09]

这条思路的关键跳跃是：作者把“物理模型知识”用于决定学习问题的分区和特征，而不是要求 NN 从全量信号中重新发现电路稀疏性。基于证据的推断是，这也是论文能同时讨论硬件资源与模型更新的原因。

## § 4 — 核心 Intuition

核心 intuition 是：不要用一个大 NN 吞下整套电力电子系统，而应沿电气耦合和时间尺度把问题拆成可并行的小 NN；对部署后不变的参数，把它们固化进权重而不是反复作为输入。[pdf:E02] [pdf:E03] FPGA 只负责低延迟推断，GPU 负责较慢的训练，模型权重通过数据链路周期性刷新，于是“实时执行”和“在线适应”被放在不同计算平面上。[pdf:E07] 这种设计以一部分跨对象 generalization 换取明确的延迟和资源收益。

## § 5 — 具体方法与完整 Pipeline

以 TLC-PMSM 推进支路在设备发生参数漂移后的更新为例，完整 pipeline 是：

1. **建立 referencer。** referencer 可以是物理系统或经验证的仿真程序；本文实际用 Jetson 上经 PSCAD/EMTDC 校验的 C 程序产生系统级数据，并用 SaberRD 数据产生器件级 IGBT 波形。[pdf:E07] [pdf:E08] [pdf:E10]
2. **按物理结构选模型。** ATRUS 被拆成变压器、双整流器和 LC filter，ESS 被拆成 converter、inductor 和 battery；MMC 用 TLM/Thévenin 等效隔离 arm 与 submodule；TLC 用三步 RNN，PMSM 则按 flux、damping flux、current、torque 和 speed 单元组织 hybrid ANN/RNN。[pdf:E04] [pdf:E05] [pdf:E06]
3. **准备离线初始模型。** 以 PMSM 为例，作者让 speed 在 -0.1–1.5 p.u.、torque 在 0–1.2 p.u. 内变化，1 μs 步长、8 s 产生 8,000,000 组数据，再按 1000 的间隔采样为 8,000 组训练数据。[pdf:E08]
4. **把 inferencer 映射到 FPGA。** Xilinx VCU118 上的 XCVU9P 以 100 MHz 运行，NN 被装入 IP core；Jetson 通过 PCIe 传输数据和更新后的二进制权重。[pdf:E07] [pdf:E08]
5. **在线选数与训练。** Redis 传递测量数据和模型；IGBT 数据 washer 用 gate signal 的显著变化识别 switching transient，每组保留 20 个 50 ns 点，也就是 1 μs 波形，累计到 5,000 组后打乱训练。训练在双 Intel Silver 4216 CPU、四 NVIDIA V100 GPU 的集群上运行。[pdf:E08] [pdf:E09]
6. **停止与更新。** 训练不是永久连续运行，而是在误差低于阈值或达到人工设定次数时停止；新 weights/biases 再送到 FPGA，形成 refined inferencer。[pdf:E09]
7. **实时输出。** 系统级模型每 1 μs 输出一次；IGBT transient unit 在一次 1 μs 执行中输出 20 个点，从而表达 50 ns switching transient。[pdf:E06]

## § 6 — 核心数学推导

论文的数学核心不是一个收敛定理，而是一条“从稀疏电路关系到可并行学习块”的构造链。

首先，LNN 把系统写成一般映射 \(\{y_1,\ldots,y_m\}=f(x_1,\ldots,x_n)\)。对一层线性网络 \(Y=AX\)，作者用含大量零项的 \(5\times5\) 示例说明：若 \((y_1,y_2)\) 只依赖 \((x_1,x_2,x_5)\)，而 \((y_3,y_4,y_5)\) 只依赖 \((x_3,x_4,x_5)\)，就可把 \(A\) 分成较小的 \(B\) 和 \(C\) 块并并行计算，这就是 PNN 的最小数学原型。PNNCF 再把设备参数从变化输入移入固定 weights/biases，降低输入矩阵和计算矩阵的 rank，但也缩小模型可泛化到的参数族。[pdf:E02] [pdf:E03]

其次，MMC submodule 先用 Euler/TLM 离散化。式 (4) 由等效电感、两个开关和电容阻抗组成 \(2\times2\) 系统，求出 submodule current；式 (5)–(6)再由该电流更新 capacitor/switch voltage 与两组 history voltage。作者随后把这个显式更新压缩为式 (7) 的非线性映射：当前电压和 history state 由前一步 history state 与 gate \(g_1,g_2\) 决定；arm-level 式 (8) 则由各 submodule history voltage、dc-link voltage 和前一步 phase current 预测 phase voltage 与上下 arm current。[pdf:E05] 直觉上，TLM 提供“哪些历史量足以把子电路断开”的接口，ANN 只学习接口内部的非线性。

最后，PMSM 的式 (9)–(16)给出 dq-axis voltage、current、flux linkage、short-circuit winding 和 permanent-magnet flux 的物理关系；这些关系决定了 hybrid model 的模块边界。式 (17)更新主 flux increment，式 (18)更新 damping-winding flux，式 (19)由当前 flux 求 currents，式 (20)求 torque，式 (21)推进 rotor angle/speed；作为对照，一般 RNN 只用式 (22)–(23)从可测的 \(v_d,v_q,\omega_r\) 预测 currents/torque。[pdf:E06] [pdf:E07] 这里的“推导”主要证明输入输出依赖如何被拆分，不等价于证明 learned mapping 在训练分布外稳定或守恒。

## § 7 — 实验设计与结论

**问题一：结构化模型能否在 FPGA deadline 内执行？** 作者在 Xilinx VCU118 上报告各模型 latency 和资源。Table I 中完整 MMC 占 49.56% DSP、40.53% LUT，latency 0.92 μs；RNN converter latency 0.64 μs，hybrid PMSM 为 0.84 μs，hybrid IM 为 0.82 μs。器件级 IGBT unit 的一次执行 latency 为 0.63 μs，同时输出 20 个 50 ns 点。[pdf:E08] 这些结果支持“所列单元可放入 1 μs 系统级时限”的工程 claim，但表中没有给出整套多支路 HSR 微电网同时扩展后的最大实例数。

**问题二：按物理结构拆分是否优于一般 RNN？** Fig. 15 比较同一 PMSM 的一般 RNN 与详细 hybrid ANN；两者 steady-state 都跟随 reference，而 hybrid model 在速度/转矩变化段保留更高 signal bandwidth，作者归因于一般 RNN 为稳定性加入 low-pass filter。[pdf:E10] 这支持结构化模型在该工况下改善动态细节，但没有独立统计检验。

**问题三：在线更新是否比离线模型更接近 referencer？** Fig. 16–19 将 referencer、offline inferencer 和 online refined inferencer 并排比较。TLC current/voltage、SiC IGBT transient 和 MMC single-phase voltage 中，refined 曲线更接近 reference；MMC submodule 和 single-phase current 的 offline/online 差异则很小。[pdf:E11] 作者因此声称 IIL 能在 1 μs/50 ns 两层级达到 0.2% 内误差。[pdf:E12] 但正文主要给波形和个别 MAE 训练曲线，未给所有对象、所有工况统一的误差分布或置信区间。

**问题四：在线训练成本由什么决定？** Fig. 12–13 改变 ANN hidden size、RNN sequence length 和 dataset size。作者观察 dataset size 对 update time 最明显，并据此建议 hidden size 为 input size 的 2–4 倍、RNN sequence length 为 3 或 4、ANN 1–2 层、RNN 1 层。[pdf:E09] 这些是本文平台上的经验设计规则，不是跨任务理论最优值。

## § 8 — Take-aways

**5 句话。** 第一，论文把高铁微电网的 ML 建模问题变成“沿电路依赖拆模型、沿时间尺度分工”的硬件系统问题。第二，PNN 利用稀疏耦合把 LNN 拆成并行块，PNNCF 再用固定参数换取更低资源与延迟。[pdf:E03] 第三，TLM history source 和 PMSM 物理方程不是被 NN 抛弃，而是用于规定 NN 的输入、输出和模块边界。[pdf:E05] [pdf:E07] 第四，GPU/Redis/Jetson/FPGA 链路把训练与 inferencing 分离，使 FPGA 上的实时模型可以周期性接收更新。[pdf:E07] [pdf:E08] 第五，实验对“可运行、局部波形更接近 reference”给出直接证据，但对真实设备漂移下的闭环稳定性和泛化仍缺乏充分验证。

**3 句话。** 这篇论文最重要的工程贡献是以 physical decomposition 缩小 NN，再把在线训练与 FPGA deadline 解耦。它展示了多类 HSR microgrid 子系统在 VCU118 上的延迟、资源和波形对比。[pdf:E08] [pdf:E11] 它尚未证明“低 pointwise error”足以保证真实微电网长期闭环可信。

**1 句话。** 用电路结构约束 learned model、用异构硬件分离训练和推断，是本文比“一个更大的 NN”更有价值的主张。

## § 9 — 最脆弱的假设

最脆弱的假设是：**referencer 及其被选择的数据足以代表部署对象正在发生的物理变化，因此降低对 referencer 的 MAE 就意味着在线 IIL 更接近真实系统。** 作者明确说 referencer 可以是物理系统或可信仿真系统，但本文系统级 reference 实际来自经 PSCAD/EMTDC 校验的 C 程序，器件级 reference 来自 SaberRD 数据；同时，在线数据是否进入训练还受人工 update policy 和 switch-transient selector 控制。[pdf:E07] [pdf:E08] [pdf:E09] 作者讨论了 aging、temperature、humidity 引起的变化，却没有在所展示实验里对真实老化器件做受控漂移、盲测或长期闭环验证。

如果 referencer 缺少真实漂移机制，或者 washer 丢掉了决定漂移的低频/稀有状态，那么再快的 retraining 也只会更精确地拟合错误目标。进一步说，这是基于证据的推断：在耦合微电网中，单步 MAE 很小也不自动保证 energy balance、passivity 或长期数值稳定；论文没有提供这些系统级性质的证明。这个假设一旦失败，“online update 提升真实可信度”这一核心贡献会退化为“online update 提升对既有模拟器的拟合度”。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 HSR microgrid，而是一个 **TLC-PMSM 子系统的受控参数漂移更新实验**。

- **数据。** 用一个可复查的开关模型和 PMSM 模型生成三组轨迹：额定参数训练集、未见过的 speed/torque 组合测试集、以及在 winding resistance/flux 等参数上施加缓慢漂移的测试集。保持论文的 1 μs 系统步长；若有 FPGA，则用 VCU118 或同等级器件测真实 latency，否则只把 software 结果标为功能复现，不声称硬件实时性。[pdf:E08]
- **实现。** 建一个三步 RNN TLC model 和论文式 (17)–(21)边界对应的 hybrid PMSM model；先训练 offline model，再只用漂移发生后的短窗口更新一版 refined model。[pdf:E06] [pdf:E07]
- **测量。** 对同一 held-out 漂移轨迹比较 offline/refined 的 MAE、最大误差、关键转矩阶跃后的 settling error，以及 FPGA latency/resource；不要只画重叠波形。
- **支持标准。** refined model 在未参与更新的漂移轨迹上稳定降低 MAE 和最大误差，同时单步执行不超过 1 μs；若还能在预先冻结的评价脚本中达到作者声称的 0.2% 内误差，则对论文核心 claim 形成较强支持。[pdf:E12]
- **反驳标准。** 更新只改善训练窗口、在 held-out 漂移上不改善或导致闭环发散；或者为达到误差目标而超过 1 μs deadline。任一项都足以反驳“在线更新同时保持 accuracy 与 real-time”的强版本 claim。

## § 11 — 最强反例设计

最强反例是构造一个 **单步拟合误差仍低、但长期闭环能量行为错误** 的工况。具体做法是：让 PMSM 参数随温度缓慢漂移，同时在未见过的 regenerative braking 与 dc-bus 能量回灌工况下运行；referencer 使用真实测量，inferencer 仍按论文策略用局部窗口和 MAE 更新。然后比较端口瞬时功率、累计能量误差、dc-bus voltage envelope 和是否出现非物理振荡，而不仅比较 current/voltage pointwise MAE。

这个反例针对论文最核心的替代解释：Fig. 16–19 中 refined 波形更接近 reference，可能只说明局部 supervised fit 改善，并不说明更新后的各子模型在重新耦合后仍保持真实系统的 passivity 和稳定性。[pdf:E11] 如果某个 refined model 的 MAE 小于 offline model，却持续向网络注入非物理能量或在长时域引发 dc-bus 漂移，就说明“低误差 + deadline”不足以构成可信实时数字替身。论文没有报告这类 energy/stability test，因此该反例目前没有被排除。

## § 12 — Follow-up Research Idea

在 EMT、power electronics 和 real-time simulation 领域，高影响工作通常不只看 benchmark MAE，还看严格的硬件实时性、跨工况暂态保真、闭环稳定性、资源可扩展性和真实系统验证。基于第 9 节，候选研究方向是：**把 IIL 从 pointwise model refresh 改成带离散时间端口契约的 online residual identification**。每个 learned subsystem 不直接自由预测全部电压/电流，而是在传统 TLM 端口模型上只学习 residual，并在每次权重更新后强制检查 passivity/energy bound 与 worst-case latency；未通过契约的模型不得进入 FPGA。

（a）驱动需求是防止 referencer mismatch 或局部低 MAE 在网络耦合后变成长期能量漂移；（b）若能同时给出 adaptation、稳定边界和 1 μs 硬件证据，它会把本文的“波形更接近”提升为可组合的实时可信性；（c）可借鉴 passivity-based model reduction、safe online learning、set-membership identification 和 runtime assurance；（d）第一个可证伪实验就是第 11 节的 thermal-drift regenerative-braking 场景：如果带契约 residual model 不能比无约束 IIL 显著降低累计能量误差，或契约检查让 latency 超过 1 μs，该方向的核心承诺失败；（e）它与本文的实质区别是评价和更新目标从单模型 MAE 转向“重新接回网络后仍满足的端口级系统性质”。该想法未经额外相关工作检索，只能标为候选方向，不声称 novelty。
