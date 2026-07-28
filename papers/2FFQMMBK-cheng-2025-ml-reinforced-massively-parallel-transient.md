# Machine-Learning-Reinforced Massively Parallel Transient Simulation for Large-Scale Renewable-Energy-Integrated Power Systems

作者：Tianshi Cheng、Ruogu Chen、Ning Lin、Tian Liang、Venkata Dinavahi
出处：IEEE Transactions on Power Systems, Vol. 40, No. 1, pp. 983–994
年份：2025
DOI：10.1109/TPWRS.2024.3409729
Zotero key：2FFQMMBK

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“让神经网络预测电网是否稳定”，而是一个更具体的计算问题：当光伏阵列、风电场和电池组以设备级或子阵列级细节进入大规模 AC/DC 电网时，传统 electromagnetic transient（EMT）模型的非线性迭代和庞大实体数量会使仿真成本失控。作者以光伏为典型例子指出，单个 100 MW 光伏场可含 30 万片以上组件，而局部遮阴时单片差异可能影响整个阵列；传统 PV 模型又要反复执行 Newton–Raphson 并组装全局 Jacobian，难以扩展到这种粒度。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

作者的答案由两层组成。第一层用 ANN 取代部分 renewable energy system（RES）组件的非线性物理更新：静态 4×4 PV 阵列使用 MLP，具有时间记忆的 DFIG 风电场和锂电池组使用 GRU。第二层不是再发明电网求解器，而是用 Rust/Bevy 的 entity-component-system（ECS）组织数据，再把同一种 ANN 的大量实例合并为 GPU batch；网络节点方程仍按传统 EMT 离散和线性求解。[pdf:E02][pdf:E06]（PDF 物理页 2，作者列出的两项主张；物理页 6，Eq. (11)–(13) 与 Fig. 7）

这件事的重要性在于：详细 RES 模型如果只能做小系统或 lumped model，就无法研究组件不一致性、局部遮阴、储能单体差异如何经变流器和网络耦合放大。论文的工程价值因此不是“机器学习更聪明”，而是把一批形状一致、计算昂贵的局部非线性映射改写成 GPU 擅长的规则矩阵运算，同时保持它们作为 EMT 等效电流源接入网络。[pdf:E01][pdf:E04]（PDF 物理页 1，Introduction；物理页 4，Fig. 2(e)）

## § 2 — 前人工作与不足

按作者自己的相关工作定位，已有路线分成三类。第一类是详细物理 EMT：PV、battery 等模型能表达器件非线性，但需要 Newton–Raphson 或专门的非迭代算法，规模增长时计算和收敛代价高。第二类是在 GPU 上并行传统 PV 和 battery 模型，例如作者引用的 [8]、[9]；它们已有大规模并行能力，但不同模型内部结构和分支逻辑不统一，难形成对 GPU 友好的共同计算形态。第三类是 ANN/RNN 加速 EMT，包括作者引用的 [17]–[19]；论文明确把这些工作描述为 FPGA 上的小规模、特定场景、传统组件探索，尚未扩展到本文这种 RES 建模与大规模 solver integration。[pdf:E01][pdf:E02][pdf:E11]（PDF 物理页 1–2，Introduction；物理页 11，References [17]–[19]）

本文真正补的缺口不是一种新的神经网络单元。MLP、GRU、MSE 和 gradient descent 都是标准工具；作者的新组合是：用 Monte Carlo 物理仿真生成多变量 RES 数据，用统一 ANN 计算形态替代各自不同的非线性更新，再用 ECS、ModelRef 分组和 GPU instancing 把大量同构实体一次批处理。[pdf:E02][pdf:E03][pdf:E07]（PDF 物理页 2–3，贡献与 ANN 基础；物理页 7，GPUBatchManager）

需要限制这个“补缺口”的范围：论文只依据自身综述说明前述 FPGA 工作的不足，本卡没有独立核验 [17]–[19] 的全文，因此不能据此宣布本文在“ML-EMT”或“FPGA data-driven VSC”方向具有普遍 novelty。能确认的是，本文实际完成的是 CPU–GPU 软件体系和三类 RES surrogate 的联合案例，而不是 FPGA 实现。[pdf:E01][pdf:E10]（PDF 物理页 1，Introduction；物理页 10，Performance Evaluation）

## § 3 — 重建作者的思考路径

以下是基于论文证据重建的推断，不是作者逐字陈述。

第一步，研究者会发现瓶颈并不完全在网络矩阵。对于大规模同构光伏，重复执行数十万次相似的非线性 I–V 求解才是高成本部分；而 GPU 在规则稠密矩阵运算上强，在迭代、分支和频繁 host/device 交换上弱。[pdf:E01][pdf:E02]（PDF 物理页 1–2）

第二步，把每个 RES 单元看成端口映射：给定可观测环境量、端口电量和必要历史，输出注入网络的电流以及下一步所需状态。静态 PV 映射可用 MLP；风机和电池有时间记忆，需 GRU。这样做保留外部节点方程，却把局部非线性压成一致的 ANN inference。[pdf:E04][pdf:E05][pdf:E06]（PDF 物理页 4，Fig. 2；物理页 5，Fig. 4–5；物理页 6，Fig. 6）

第三步，单个小网络的 GPU 调用开销可能比计算本身更大，因此不能“一设备一 kernel”。必须让所有采用同一 ModelRef 的实体共享权重、分别占有输入输出槽位，并在每个仿真步只做一次聚合后的 host/device 搬运和 batch inference。[pdf:E07][pdf:E08]（PDF 物理页 7，Section III-C；物理页 8，Fig. 9）

第四步，为证明这不是孤立的 surrogate demo，需要把 ANN 实体插回完整 EMT loop，并同时展示两件事：在局部遮阴、风速变化和短路波形上不严重失真；实体数扩大到百万级时，batch 后的 GPU 路线能显著超过串行 CPU 非线性模型。[pdf:E05][pdf:E09][pdf:E10]（PDF 物理页 5、9–10）

## § 4 — 核心 Intuition

把每个复杂 RES 物理模型变成“端口输入与少量历史到等效电流/状态”的统一神经网络映射，就能避开逐设备的非线性迭代。再让所有同构设备共享一份网络权重、但保留各自输入输出，并合并为少数 GPU batch，规模越大越能摊薄数据搬运和 kernel 启动开销。电网拓扑和节点方程仍由传统 EMT solver 处理，所以 ML 在这里是组件 surrogate，不是网络求解器、保护控制器或稳定性判别器。[pdf:E04][pdf:E07][pdf:E08]（PDF 物理页 4、7–8）

## § 5 — 具体方法与完整 Pipeline

以“一座含 100 个光伏场的微网接入 IEEE 118-Bus”为例，完整 pipeline 如下。

1. **从可信物理模型生成数据。** 4×4 PV 阵列有 16 个独立 irradiance 输入和端口电压 \(V_t\)，输出为 \(I_{out}\)。每个 irradiance 从均值 1000 W/m²、标准差 300 W/m² 的正态分布采样，端口电压在 0 到最大工作电压内均匀采样；传统非线性 EMT 模型生成 2000 万样本。[pdf:E03][pdf:E04]（PDF 物理页 3，Section II-C；物理页 4，Fig. 2）
2. **训练 PV surrogate。** Fig. 2 明示样本按 70% training / 30% validation 划分；MLP 为四个 hidden layers、每层 64 cells，采用动态 learning rate、MSE 和 0.25 dropout。论文报告 dropout 使 validation error 约降低 20%，训练 MSE 约 \(10^{-5}\)，validation MSE 约 \(7\times10^{-5}\)。这里没有单列独立 test set。[pdf:E04][pdf:E05]（PDF 物理页 4，Fig. 2–3；物理页 5，Section II-D 之前）
3. **训练有记忆的 surrogate。** DFIG 风电场和 3×4 battery group 使用单层 GRU。Fig. 6 给出 causal sequence：风电模型用最近 5 个时刻的风速、机械/转速和三相端口量等序列形成时刻 \(t\) 的输出，并把结果作为后续输入；battery 使用长度 3 的温度、端口电压/电流、SOC 序列。风电训练数据中三相接地故障占 5%，故障电阻 0.01 Ω、持续 60 ms；两类 GRU 均训练 100 epochs。[pdf:E05][pdf:E06]（PDF 物理页 5，Fig. 4–5；物理页 6，Fig. 6）
4. **把模型装回 EMT 组件。** PV MLP 输出作为 voltage-controlled current source；风电 GRU 输出三相电流及内部动态量；battery GRU 输出电流和状态量。网络侧仍用 Trapezoidal Rule 得到 \(Yv^{n+1}=I_{eq}^{n+1}\)，再用 LU/KLU 等线性方法求节点电压。[pdf:E04][pdf:E06]（PDF 物理页 4，Fig. 2(e)；物理页 6，Eq. (11)–(13)）
5. **ECS 数据布局与批处理。** 每个电气对象是 entity；环境量、拓扑、admittance、TensorIO 等是 component。初始化时 GPUBatchManager 扫描 ANN，按相同 ModelRef 分组；同组共享模型权重，每个实体在连续全局 tensor 中登记独立输入/输出地址。每个 PreUpdate 中 CPU 写入所有输入，GRU 先移位历史，随后每种模型只做一次聚合拷贝、scaling、inference 和 output scaling，最后把预测电流写回 \(I_{eq}\)。[pdf:E07][pdf:E08]（PDF 物理页 7–8，Section III-C 与 Fig. 9）
6. **扩展到系统 cluster。** 基础案例是 IEEE 118-Bus 与 CIGRE B4 DCS-1 MMC 构成的 AC/DC 网络，Bus 44 接一个 RES microgrid。该微网含 100 个 PV farms、一个 DFIG wind farm 和一个 battery station；每个 PV farm 有 400 个 4×4 MLP PV arrays，即 6400 panels，100 个场合计 64 万 panels。单个微网图中 PV 额定 125 MW，风电与电池各 50 MW。四套系统经 MMC 相连后达到 256 万 panels，并由 8 CPU threads 与 2 GPUs 执行。[pdf:E08][pdf:E09]（PDF 物理页 8，Fig. 10；物理页 9，Section IV）

ML 的真实角色由这条 pipeline 很清楚地限定了：它替代 PV、wind、battery 的局部 constitutive/state update；ECS 负责调度与内存；CPU 负责主仿真数据和网络求解；GPU 负责 Float32 ANN batch inference。论文没有把 inverter/VSC 本体替换成 ANN，Fig. 10 仍把 MLP PV blocks 与 inverter 分开画出。[pdf:E02][pdf:E08]（PDF 物理页 2，Section II 开头；物理页 8，Fig. 10）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有新的 approximation theorem 或稳定性证明，但有三组决定工程实现的数学关系。

**MLP 局部映射。** 每层是

\[
z=f(Wx+b),
\]

训练目标是 \(\min_{W,b}L(y,\hat y)\)，本文使用

\[
\mathrm{MSE}=\frac{1}{n}\sum_{i=1}^{n}\lVert y_i-\hat y_i\rVert_2^2,
\]

并以 \(W_{\mathrm{new}}=W_{\mathrm{old}}-\alpha\nabla_WL\)、\(b_{\mathrm{new}}=b_{\mathrm{old}}-\alpha\nabla_bL\) 更新。工程直觉是：PV 的非线性 I–V 关系不再在每个仿真步迭代求根，而成为固定层数的矩阵乘、bias 和 activation。[pdf:E03]（PDF 物理页 3，Eq. (1)–(5)）

**GRU 的有记忆映射。** update gate \(z_t\)、reset gate \(r_t\)、candidate state \(\tilde h_t\) 和 hidden state \(h_t\) 满足

\[
\begin{aligned}
z_t &= \sigma(W_{xz}x_t+U_{hz}h_{t-1}),\\
r_t &= \sigma(W_{xr}x_t+U_{hr}h_{t-1}),\\
\tilde h_t &= \tanh(Wx_t+U(r_t\odot h_{t-1})),\\
h_t &= (1-z_t)\odot h_{t-1}+z_t\odot\tilde h_t.
\end{aligned}
\]

这里 gate 的作用不是提高并行度，而是让有限历史进入风机和电池的动态等效。代价是每个实体仍需独立的 sequence/hidden state；论文也报告同等规模的 GRU execution time 约为 MLP 的 2–3 倍。[pdf:E03][pdf:E10]（PDF 物理页 3，Eq. (6)–(9)；物理页 10，Performance Evaluation）

**网络时间推进。** 线性 RLC 网络经 Trapezoidal Rule 后写成

\[
Yv^{n+1}=I_{eq}^{n+1},
\]

\[
Y=\frac{\Delta t}{2}G_L+\frac{2}{\Delta t}G_C+G_R,
\]

\[
I_{eq}^{n+1}=i_s+\left(\frac{2}{\Delta t}G_C-\frac{\Delta t}{2}G_L\right)v_n-i_{L_n}+i_{C_n}.
\]

因此 ANN 的输出必须在求 \(v^{n+1}\) 前进入等效电流向量。Fig. 9 的调度顺序是 PreUpdate 内准备输入、GPU inference、UpdateIeq，随后网络写入/求解。GRU 在 Fig. 6 中明确以过去序列产生当前输出，具备因果顺序；但 PV MLP 的 \(V_t\rightarrow I_{out}\) 没有标明 \(V_t\) 是 \(v_n\)、预测值还是内部迭代值，论文没有给出这个代数环的精确时标定义。这不妨碍理解其软件实现，却是做 cycle-accurate FPGA pipeline 前必须补齐的接口契约。[pdf:E06][pdf:E08]（PDF 物理页 6，Eq. (11)–(13) 与 Fig. 6；物理页 8，Fig. 9）

## § 7 — 实验设计与结论

**问题 1：surrogate 能否复现训练物理模型？ → 实验：** PV 用 2000 万仿真样本做 70/30 training/validation；风电与电池比较 GRU 和 reference model 的波形/MSE，风电 validation 含三相接地短路波形。**答案：** 论文报告 PV training MSE 约 \(10^{-5}\)、validation MSE 约 \(7\times10^{-5}\)；GRU 能跟随故障和 discharge curve，但这些 reference 都来自既有物理仿真，不是独立现场测量。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Fig. 2–5）

**问题 2：PV 对稀疏采样遮阴点是否还能工作？ → 实验：** 初始 irradiance 全为 1000 W/m²；1 s 时 S1、S16 分别降到 100、200 W/m²，持续 0.02 s。该组合不在 training set，且约只有 40 个邻近样本量级。**答案：** 额定区 active power relative error 为 0.2%；遮阴后 MLP 输出从 1.25 MW 降到 0.69 MW，相对原模型误差为 4%，inverter AC voltage 图示误差约 1%。这证明了同一 4×4 拓扑和既定输入域内的一次稀疏点外推，不证明跨 topology 或跨 array size 泛化。[pdf:E09]（PDF 物理页 9，Fig. 11(a)–(c) 与 Scenario 1）

**问题 3：GRU 能否跟随风速动态？ → 实验：** 风速在 5 s 从 15 m/s 变为 10 m/s，比较 rotor speed、active power、phase-A current。**答案：** 三项 relative error 都低于 1%；但论文同时指出 GRU 固定 time step，限制其相对 MLP 的适用性。[pdf:E09][pdf:E10]（PDF 物理页 9，Fig. 11(d)–(f)；物理页 10，Scenario 2）

**问题 4：大规模重复实体是否带来实际 acceleration？ → 实验：** 在 Cedar node 上以两块 NVIDIA Tesla V100（每块 5120 CUDA units）、8 CPU threads 比较 serial CPU Newton–Raphson PV 与 GPU MLP；横向增加 panel 数，并独立扫 wind/battery GRU instance 数。**答案：** CPU 在 1.6 万 panels 以下仍占优；超过 100 万 panels 后 speed-up 超过 100；256 万 panels 时图中每步约为 CPU 70.5 s、GPU 0.167 s，正文概括为约 400×。单 GPU 无法承载最大案例，因此使用双 GPU。[pdf:E10]（PDF 物理页 10，Fig. 12 与 Performance Evaluation）

**不得外推的范围。** 论文平台是 CPU–GPU，不是 FPGA；没有 XCKU060、LUT/DSP/BRAM、clock、pipeline initiation interval、功耗或 fixed-point 资源报告。ANN 使用 Float32，而对照 Newton–Raphson 使用 Float64；这只是软件数值格式，不是 FPGA 位宽设计。论文给出 GPUBatchSet 最少约 300 μs 以及 Fig. 12 的 measured time per simulation step，但没有 deadline、尾延迟分布或 worst-case execution time（WCET）证明，也没有宣称最大案例实时。[pdf:E02][pdf:E08][pdf:E10]（PDF 物理页 2，Float32/Float64；物理页 8，Fig. 10(c)；物理页 10，Fig. 12）

## § 8 — Take-aways

**5 句话。**  
1. 论文把 ML 用作 RES 局部物理模型的 surrogate，而不是电网 solver。  
2. MLP 处理静态 4×4 PV array，GRU 处理 lumped DFIG wind farm 和 battery group 的历史依赖。[pdf:E04][pdf:E06]  
3. 可扩展性的关键是同 ModelRef 共享权重、独立 TensorIO 连续排布和按模型类型做单次 batch inference，而不只是“用了 GPU”。[pdf:E07][pdf:E08]  
4. 在同一模型拓扑上复制到 256 万 PV panels 后，双 V100 相对串行 CPU 非线性模型约加速 400×，但仍没有实时或 WCET 证明。[pdf:E09][pdf:E10]  
5. 精度的主要薄弱点是 training distribution：稀疏 partial-shading 区的 PV power error 从额定区 0.2% 上升到 4%。[pdf:E09]

**3 句话。**  
1. 这是一篇“surrogate + data layout + batching”的系统论文，不是新 ANN 结构论文。  
2. 它证明同构设备越多，权重共享和批推理越有价值，但 model generalization 只在固定 4×4 PV 拓扑和有限工况内展示。  
3. 对 FPGA 方向最有价值的是任务分解与同构实例结构；最关键的缺证是 causal schedule、fixed-point、资源、时序和 WCET。

**1 句话。**  
论文证明了重复同一个 learned RES component 可以在 CPU–GPU EMT 中大幅摊薄成本，却没有证明该 learned component 可跨拓扑迁移、可在 FPGA 上确定时延运行，或可稳定替代闭环 VSC 动态。

## § 9 — 最脆弱的假设

最脆弱的假设是：**用单设备/子系统物理仿真数据训练出的局部 surrogate，在被复制成数万同构实体并与网络闭环耦合后，误差仍然局部、平滑且不会积累为系统级错误。**

论文给出的支持是有限但真实的：PV 在一个 training set 未出现的稀疏 shading 组合下维持 4% power error，wind GRU 在 wind-step 中低于 1%，并且短路波形能跟随 reference model。[pdf:E05][pdf:E09][pdf:E10]（PDF 物理页 5、9–10）但这些实验共享原物理模型的数据生成机制；PV 仍是 4×4 topology，wind/battery 是固定 lumped topology，网络中大量 PV 只是复用相同结构和参数，并未用不同串并联规模、不同 inverter controller、不同采样步长或真实站端数据检验迁移。

这个假设一旦失效，400× 只说明“快速计算了一个错误模型”。更危险的是，单个 array 的小 bias 在 6.25 万以上同类 MLP entities 中可能同向叠加，改变 bus voltage，再反馈到各 surrogate 输入。论文没有给出 closed-loop stability/energy/passivity 约束，也没有给出 aggregate error 随 entity count 的上界。因此“单体 waveform 看起来接近”不足以保证百万实体耦合系统的物理可信度；这是基于论文结构的推断，不是作者明确结论。[pdf:E07][pdf:E10]（PDF 物理页 7，batch grouping；物理页 10，scale sweep）

## § 10 — 最小复现实验

一周内最值得复现的是“同一 4×4 PV surrogate 在稀疏 shading 下能否保持闭环 EMT 精度，并且 batch 越大是否真能摊薄成本”，不必重建四套 118-Bus。

- **数据：** 复现论文 Fig. 2 的 4×4 PV physical model，使用 16 路 irradiance 与端口电压输入；先生成 100 万到 200 万样本。训练集保留论文的独立正态 irradiance，另建一个完全不进入 training/validation 的 adversarial test：同列相关遮阴、旁路二极管切换附近电压、快速 voltage sag 三者组合。[pdf:E04][pdf:E09]
- **实现：** 一个 4×64 MLP，70/30 training/validation，Float32；把它作为 controlled current source 放回最小 DC-link + inverter + AC source EMT circuit。分别复制 1、256、4096 个实例，并比较逐实例调用与共享权重 batch。[pdf:E04][pdf:E07]
- **测量：** 每步 \(I_{out}\)、DC bus voltage、AC active power 的 peak error、steady-state error、能量误差；随着实例数增长的 aggregate bus error；平均/99.9%/最大 execution time per step。性能对照必须使用同一硬件、同一步长和同一物理模型精度。
- **支持 claim 的门槛：** held-out correlated shading 下 active-power error 不高于论文报告的 4%，没有自激或随实例数单调放大的系统偏差；batch 在 4096 entities 时明显优于逐实例路径。
- **反驳 claim 的结果：** validation MSE 很低但闭环出现明显相位/能量漂移，或 aggregate error 随实体数增长，或 GPU batch 在目标规模仍慢于对照。任何一项都说明论文的局部拟合指标不能独立支撑系统级 surrogate claim。

## § 11 — 最强反例设计

最强反例不是再换一个随机 irradiance，而是构造**相关分布移位与网络扰动同时发生**：让同一 PV farm 中大量 4×4 arrays 受到空间相关的移动云影，使同一串内遮阴组合集中落在训练正态分布的极低概率区域；同时施加 AC voltage sag，使 inverter DC-link 和 PV port voltage 穿越 I–V 曲线拐点。训练时仍采用论文的独立 irradiance Monte Carlo，不把这类相关事件加入数据。

这个反例针对两层机制。第一，论文已观察到稀疏区只有约 40 个邻近样本且 power error 达 4%，说明 MSE + dropout 不会自动保护尾部区域。[pdf:E09]（PDF 物理页 9，Scenario 1）第二，几万实体共享同一模型权重；若相同 bias 被同步激活，误差不会被 averaging 抵消，反而可能在 bus 上相干叠加。[pdf:E07][pdf:E10]（PDF 物理页 7、10）

判据应是：与 physical reference 比较 aggregate active power、DC-link voltage、AC current 与保护动作时刻；同时检查在相同步长下是否产生虚假的恢复、漏掉 current limit、或出现 reference 中没有的振荡。如果单体 validation 仍好、但系统闭环在该场景明显偏离，就能推翻“局部 ANN 精度足以保证大规模 EMT 可用”的核心解释。论文没有报告 inverter current limiting、switching/event handling 或这类联合扰动，因此目前证据不能排除此反例。

## § 12 — Follow-up Research Idea

### 与“同构光伏 VSC 场站 + XCKU060 上可部署的数据驱动模型”的碰撞

构成实质碰撞的部分有三点。第一，论文已经把**大量同构新能源单元共享一份模型参数、保留逐实例输入输出**作为主要扩展机制；这与同构 VSC 场站采用共享权重的部署设想直接重合。[pdf:E07][pdf:E08]（PDF 物理页 7–8）第二，它已将 learned model 作为 EMT 等效电流源插入时间推进，而不是只做离线预测。[pdf:E04][pdf:E06]（PDF 物理页 4、6）第三，它已在固定拓扑上展示“扩大实例数而不重训模型”的计算扩展：从一个 4×4 PV array 复用到 256 万 panels。[pdf:E08][pdf:E09]（PDF 物理页 8–9）

但它没有封死目标方向。本文 learned block 是 **PV array、lumped DFIG wind farm、battery group**，Fig. 10 中 inverter/VSC 仍是独立传统组件；因此它没有学习 VSC switching/control dynamics。[pdf:E08]（PDF 物理页 8，Fig. 10）平台是 8 CPU threads + 双 Tesla V100，不是 FPGA，更没有 XCKU060 的 LUT/DSP/BRAM、fixed-point 位宽、clock、pipeline、memory bandwidth、功耗或 WCET。[pdf:E09][pdf:E10]（PDF 物理页 9–10）它共享的是模型权重，不是把逐设备动态状态压缩成公共状态；TensorIO 和 GRU history/hidden state 仍按实体分别保存。论文甚至把 state aggregation 列为未来可能手段，说明当前系统没有完成这一点。[pdf:E07][pdf:E10]（PDF 物理页 7、10）它也没有证明跨 VSC 拓扑、跨串并联规模或跨 controller parameter 的泛化。

### 候选研究方向：有物理接口契约的共享参数、稀疏局部状态 FPGA-VSC operator

**未满足需求。** GPU batching 解决吞吐，却没有给 FPGA EMT/HIL 所需的确定时延，也没有定义 VSC surrogate 在节点求解前后的精确 causal contract。目标应从“把 ANN 搬到 FPGA”改成：对同构 VSC 群建立一个共享参数的 causal operator，每个设备只保留可证明必要的少量 local state，并保证固定步长下的端口能量/增量 passivity 边界。

**可能的研究价值。** 电力系统领域更看重可验证的 EMT fidelity、实时性和工程可实现性。若能在 XCKU060 上同时给出：跨 operating point 的闭环误差、固定点误差界、LUT/DSP/BRAM、clock、initiation interval、最大实例数和 measured WCET，并证明状态压缩不会破坏 fault transient，这比再换一个更深网络更接近高影响的硬件 EMT 贡献。

**可借鉴工具。** 可结合 reduced-order modeling 的 state aggregation、control 中的 dissipativity/passivity constraint，以及 FPGA streaming dataflow/quantization-aware training。与本文 ModelRef 权重共享相同的部分保留；新增部分是显式 causal interface、局部状态最小化和 hardware timing contract。

**第一个证伪实验。** 在一个同构 PV VSC station 上固定网络、控制器和步长，选三类完全 held-out 工况：current-limit 进入/退出、DC-link voltage sag、相关 partial shading。把共享 operator 分别部署为 Float32 reference 和 XCKU060 fixed-point pipeline；若任一工况出现保护动作顺序错误、aggregate power/energy error 随实例数增长，或 measured WCET 超过一个 EMT step，则方向被第一轮否证。

**与已有工作的实质区别。** 本文追求 GPU 上大量 RES component inference 的平均吞吐，VSC 仍是传统模型；候选方向追求的是 FPGA 上 learned VSC operator 的确定时延、因果闭合、逐实例最小状态和系统级误差约束。这个区别由本文缺失的实现证据直接限定，但尚未完成对所有 FPGA ML-EMT 文献的全文检索，因此这里只能称为候选研究方向，不声称 novelty。
