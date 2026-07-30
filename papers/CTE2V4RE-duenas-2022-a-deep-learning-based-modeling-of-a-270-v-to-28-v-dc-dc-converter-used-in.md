# A Deep Learning-Based Modeling of a 270 V-to-28 V DC-DC Converter Used in More Electric Aircrafts

**作者**：Gabriel Rojas-Dueñas、Jordi-Roger Riba、Manuel Moreno-Eguilaz [pdf:E01]  
**出处**：IEEE Transactions on Power Electronics, Vol. 37, No. 1  
**年份**：2022  
**DOI**：10.1109/TPEL.2021.3098468  
**Zotero key**：CTE2V4RE  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个很具体的工程问题：当一台 270 V-to-28 V 航空 DC-DC step-down converter 的内部拓扑、元件参数和控制器都不可见时，能否只用端口实验波形，得到一个同时复现稳态 ripple 与负载突变瞬态的黑盒模型。作者选择的端口输入是输入电压 \(V_\mathrm{in}\) 和输出电流 \(I_\mathrm{out}\)，预测输出则是输入电流 \(I_\mathrm{in}\) 和输出电压 \(V_\mathrm{out}\)；因此问题被写成多变量时序回归，而不是拓扑辨识或参数估计。[pdf:E05]

这个问题在 more electric aircraft（MEA）中重要，是因为系统往往同时包含不同厂商的变换器、逆变器、滤波器和 constant power load（CPL）。传统 white-box 模型需要知道被动元件、寄生参数和控制环节，但 datasheet 通常不提供足够内部信息；高频开关、寄生效应和制造商差异又会显著改变 ripple 与动态响应。论文据此把“保护厂商机密”与“仍可在系统设计阶段做动态仿真”视为黑盒建模的直接价值。[pdf:E02]

论文直接声称，离线实验数据训练的 LSTM-NN 可以覆盖广泛负载条件，并在训练后以较低计算负担复现实物变换器行为；它以真实航空 step-down converter 的实验数据和既有模型对比来支撑这一点。[pdf:E01] 但“较低计算负担”只在文字中陈述，论文没有给出单步 inference latency、目标处理器、实时步长或最坏执行时间；因此本卡不把它提升为实时仿真或 FPGA 可实现性结论。

## § 2 — 前人工作与不足

论文把前人方法分成三类。white-box 依赖完整物理方程和内部参数；gray-box 保留部分结构知识；black-box 只依据端口输入输出学习行为。对内部未知的商用航空变换器，作者认为第三类最符合信息边界。[pdf:E02]

更具体地说，作者指出：

- frequency-domain two-port 模型需要高频阻抗分析仪和频域/时域转换，相关工作只分析 CCM，并只覆盖两三个负载条件；
- Hammerstein 模型把线性动态与非线性部分分开，但模型依赖 operating point；
- time-domain transfer-function 辨识需要先人为选择候选传递函数，再做优化；
- polytopic 方法需要多个局部模型及电流阶跃，实验和模型管理更复杂；
- state-space averaging 仍要求已知拓扑；
- 已有 LSTM converter 模型使用仿真数据、没有优化 hyperparameter，也没有准确复现 ripple 与即时瞬态。[pdf:E03]

论文的改变不是发明新的 LSTM cell，而是把端口时域测量、单一跨 CCM/DCM 的 sequence model，以及 learning-rate range test 加 Bayesian optimization（BOA）的 hyperparameter tuning 串成一条离线系统辨识流程。作者还强调，该流程无需持续注入专门激励、无需频域转换，并可用一个模型覆盖多个 operating point、CCM 与 DCM。[pdf:E04] 这些是论文原文的比较主张；它没有用统一的原始数据和统一调参预算重新实现所有前人方法，因此不能把比较结果解读成对所有 black-box 方案的普遍支配。

## § 3 — 重建作者的思考路径

可以把作者可能的思考路径还原为五步。

第一，商用航空变换器的内部结构不可得，但四个端口电量可测，因此研究对象应从“电路结构”改写为“端口时序映射”。第二，稳态 ripple 和负载突变都带有历史依赖，单个静态回归点或固定 operating-point transfer function 不足以表达这类记忆。第三，普通 RNN 在长序列上容易出现梯度衰减，LSTM 通过 input、forget、output gate 保存或丢弃历史信息，更适合把先前时间步对当前输出的影响保留下来。[pdf:E06] 第四，LSTM 的表现高度依赖 learning rate、hidden units、regularization 等 hyperparameter；穷举成本高，因此先用 LR range test 缩小 learning-rate 区间，再用 BOA 选择组合。[pdf:E08] 第五，要验证“一个模型跨 operating point 工作”，实验数据必须覆盖输入电压、负载功率、CCM/DCM 以及负载连接/断开，而测试集必须独立于训练阶段。

这里最后一步包含本卡的重建性判断，而不是论文已经证明的一般定理。论文确实将实验分为 training、validation、test，并让每个 experiment 包含一次 load change；但是 PDF 没有充分报告按时间、工况或负载硬件分组的切分细节，因而“真正独立”仍需在复现时核实。[pdf:E05][pdf:E06]

## § 4 — 核心 Intuition

核心 intuition 是：把未知变换器看成一个有记忆的端口算子，而不是先猜它的拓扑或传递函数；只要训练数据覆盖了部署时会遇到的历史与工况，LSTM 的 hidden/cell state 就可能吸收控制环、开关 ripple 和 conduction-mode transition 的综合动态。BOA 不改变模型的物理含义，它只是降低“手工调参恰好调对”对结果的影响。真正让方法成立的不是 deep learning 这一标签，而是“可测端口历史足以决定未来端口响应”以及“训练分布覆盖部署分布”这两个前提。

## § 5 — 具体方法与完整 Pipeline

以一次从低负载切换到高负载的实验为例，完整 pipeline 如下。

1. **建立可控实验端口。** 被辨识对象是 Vicor DCM3714xD2K31E0yzz 隔离 regulated converter。其规格为 160-420 V 输入、28 V 输出、500 W 最大输出、700 kHz switching frequency，额定功率 10% 以下进入 DCM。输出侧并联八个由不同拓扑 DC-DC converter 加电阻构成的 CPL，并用 transistor 与 microcontroller 控制连接/断开。[pdf:E11]
2. **自动采集四路波形。** 计算机控制 load change 和 oscilloscope，记录 \(V_\mathrm{in}, I_\mathrm{out}, I_\mathrm{in}, V_\mathrm{out}\)。实验装置使用 BK Precision 9205 电源、Tektronix MDO3024 200 MHz/2.5 GS/s oscilloscope、两只 TCP0030A current probe 和两只 THDP200 voltage probe。共完成 1512 个 experiment，其中 1000 个用于 network training，512 个用于 accuracy test。[pdf:E12]
3. **形成 sequence regression。** 在时间步 \(t\)，输入向量 \(x_t=[V_\mathrm{in}(t), I_\mathrm{out}(t)]\)，目标为 \(y_t=[I_\mathrm{in}(t), V_\mathrm{out}(t)]\)。作者要求 sampling frequency 高于 converter commutation frequency，以保留 ripple；实际采样率、每段 sequence length、归一化方法、batch size 和 validation 样本数未报告。[pdf:E05]
4. **预处理并拆分数据。** Fig. 1 的流程把 measurement 送入 data preprocessing，再分为 training/validation 与 test；每个 experiment 包含一次 load change。PDF 没有给出预处理算子的具体定义，也没有公开逐 experiment split 清单。[pdf:E05][pdf:E06]
5. **调 learning rate 与其他 hyperparameter。** 先增加 learning rate，观察 RMSE/accuracy 直到训练趋于发散，从而给 BOA 一个 LR 搜索区间；再用 Gaussian-process surrogate 和 acquisition function 选择下一组 hyperparameter。若最小 validation RMSE 未过阈值，就重新定义搜索范围；过阈值后保存组合并完整训练。[pdf:E05][pdf:E08]
6. **训练与预测。** 网络由 sequence input layer、LSTM hidden layer、fully connected layer 和 regression output layer组成。文中 BOA 实际评估 30 个 LSTM-NN，每个训练 80 epochs；最终表列出的 optimum 为 96 neurons、learning rate 0.01415、gradient decay factor 0.9799、L2 regularization \(9.06\times10^{-7}\)，硬件为 GeForce RTX 2080 Super，软件为 MATLAB Deep Learning Toolbox。[pdf:E13]
7. **测试。** 调参后网络用 300 epochs 训练，validation frequency 为 15；在 512 个 test experiment 上计算 \(I_\mathrm{in}\) 与 \(V_\mathrm{out}\) 的 mean RMSE 和 \(R^2\)，并与 NARX-NN、WNN、polytopic、state-space averaging、1-D CNN 比较。[pdf:E14]

对 EMT + FPGA 读者必须明确：论文没有给出 switching/event 的显式离散处理，没有 EMT numerical integration、multi-rate scheduling、稀疏网络求解或并行依赖分析；也没有 FPGA mapping、定点表示、资源、时序、pipeline initiation interval、host-link overhead 或 real-time step。表 IV 的 “Time elapsed” 是训练/建模比较中的耗时，不能当作 inference latency 或实时执行证据。[pdf:E14]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有从 converter physics 推导 state equation；形式化部分是标准 LSTM recurrence 与 BOA 目标。

LSTM 在每个时间步先计算三个 gate 和一个候选记忆：

\[
\begin{aligned}
I_t &= \sigma(W_i x_t + R_i h_{t-1} + b_i),\\
F_t &= \sigma(W_f x_t + R_f h_{t-1} + b_f),\\
O_t &= \sigma(W_o x_t + R_o h_{t-1} + b_o),\\
G_t &= \tanh(W_g x_t + R_g h_{t-1} + b_g).
\end{aligned}
\]

其中 \(I_t\) 决定写入多少新信息，\(F_t\) 决定保留多少旧状态，\(O_t\) 决定暴露多少内部状态，\(G_t\) 是候选更新；\(W\) 是输入权重，\(R\) 是 recurrent weight，\(b\) 是 bias。然后

\[
c_t=F_t\cdot c_{t-1}+I_t\cdot G_t,\qquad
h_t=O_t\cdot\tanh(c_t),
\]

最后由 fully connected layer 给出

\[
y_t=W_{fc}h_t+b_{fc}.
\]

这些分别对应 PDF 物理页 4 的 Eq. (1)-(7)。工程直觉是：converter 的当前 \(I_\mathrm{in}\) 与 \(V_\mathrm{out}\) 不只依赖当前端口激励，也依赖控制器和储能元件留下的历史；\(c_t\) 是模型保存这种历史的可学习容器。[pdf:E07] 但 \(c_t\) 不是已辨识的电感电流或电容电压，论文没有证明它与任何真实 state 一一对应。

BOA 把 hyperparameter tuning 写成

\[
x^\star=\arg\max_{x\in X} f(x),
\]

其中 \(X\) 是 hyperparameter search space，\(x^\star\) 是最优组合；作者用 Gaussian-process surrogate 根据过去评估结果更新对未知 objective \(f(x)\) 的估计，并采用 expected improvement per second plus 平衡 exploration 与 exploitation。[pdf:E09] 这部分优化的是训练配置，不提供 converter model 的稳定性、误差上界或跨分布 generalization 保证。

## § 7 — 实验设计与结论

**问题 1：一个模型能否覆盖 CCM 与 DCM 的稳态 ripple？**  
实验把 training、validation、test 点铺在 240-300 V 输入电压和不同输出功率区域，图中同时覆盖 DCM、过渡区域和 CCM；Table I 给出的器件 DCM 条件是低于 50 W。[pdf:E10][pdf:E11] 作者分别展示 \(V_\mathrm{in}=270\text{ V}, P=94.5\text{ W}\) 的 CCM 与 \(V_\mathrm{in}=247\text{ V}, P=22.3\text{ W}\) 的 DCM 波形。答案是：在展示的两个工况中，LSTM 对 \(I_\mathrm{in}\) 与 \(V_\mathrm{out}\) 的 ripple、frequency 和 mean value 比其他比较方法更接近 measured waveform。[pdf:E14][pdf:E15]

**问题 2：平均数值误差是否优于比较模型？**  
作者在 512 个 test experiment 上计算 mean RMSE 与 \(R^2\)。proposed approach 的 \(I_\mathrm{in}\) RMSE 为 0.0185、\(V_\mathrm{out}\) RMSE 为 0.0172，两个输出的 \(R^2\) 分别为 0.991 与 0.985；表中的 NARX-NN 对应值为 0.0401、0.0342、0.948、0.902，其他四种方法也未超过 proposed approach。答案是在该数据集与各自训练流程下，LSTM 的表内 accuracy 最好，但训练耗时 1718.63 s，不是最快。[pdf:E14]

**问题 3：能否复现 load connection/disconnection 的瞬态 overshoot？**  
作者展示 load disconnection：\(V_\mathrm{in}=252\text{ V}\)，功率从 116 W 变为 34.81 W；以及 load connection：\(V_\mathrm{in}=288\text{ V}\)，功率从 46.08 W 变为 97.34 W。Fig. 13-15 的答案是，几种模型的宏观 transient response 相近，但 LSTM 最接近 measured overshoot，尤其在断载即时响应的 \(I_\mathrm{in}\) 与 \(V_\mathrm{out}\) 上。[pdf:E15][pdf:E16]

**问题 4：失败集中在哪里？**  
Fig. 16 的 scatter plot 在大部分 test point 上接近斜率 1，但作者报告，在 CCM-to-DCM transition 的 102 个相关 case 中有 7 个出现明显 instantaneous current overshoot 误差，占 6.86%；示例为 measured current 0.19 A、estimated current 0.276 A。作者说这不影响 steady state 或 estimated response time，但它直接暴露了模型最难的区域正是 conduction-mode boundary。[pdf:E17]

**问题 5：验证范围能外推到哪里？**  
论文只测试同一实验装置、同一目标 converter、给定 240-300 V 电源范围和八个实验 CPL 的 load change。它明确没有测试 sudden input-voltage transient，因为实验电源的转换速度慢于 converter controller 所需时间。[pdf:E10] 温度、老化、器差、故障、不同源阻抗、不同控制固件、未见 CPL 动态，以及多 converter interconnection 均未报告；因此结论不能外推到这些条件。

## § 8 — Take-aways

**5 句话**

1. 论文把内部未知的 270 V-to-28 V 航空 DC-DC converter 建模成由 \(V_\mathrm{in},I_\mathrm{out}\) 历史到 \(I_\mathrm{in},V_\mathrm{out}\) 的 LSTM sequence regression。
2. LR range test 与 BOA 用来选择训练 hyperparameter，最终单一模型覆盖了文中采样的 CCM、DCM、steady-state ripple 和 load-change transient。
3. 在 512 个 test experiment 上，表内 proposed approach 的两个输出 RMSE 最低、\(R^2\) 最高。[pdf:E14]
4. 最有价值的证据是实物 converter、多个实际 CPL、明确的 transient waveform 和对 conduction-mode transition 失败案例的披露，而不是 “deep learning” 标签本身。
5. 最关键的限制是训练与测试仍来自同一实验分布，且 fast input-voltage transient、环境/老化变化、实时 inference 和 FPGA 实现均未验证。

**3 句话**

1. 这是一种用端口实验历史替代内部拓扑知识的离线 black-box identification。
2. 它在已覆盖工况中比五个比较模型更准确地重现 ripple 与 load-step overshoot，但在 CCM-to-DCM boundary 仍有可见失败。
3. 论文证明了“本实验分布内的 waveform fitting”，没有证明“任意航空工况下可实时、稳定地作为 EMT/FPGA component model”。

**1 句话**

这篇论文最可信的贡献是：真实航空 DC-DC converter 的端口时序可以由调参后的 LSTM 在已覆盖 CCM/DCM 与 load-step 工况内高精度拟合，而其分布外、稳定性和实时实现边界仍未闭合。[pdf:E17]

## § 9 — 最脆弱的假设

最脆弱的假设是：**训练数据中的端口历史已经覆盖部署时决定 converter 未来响应的全部关键状态与扰动。** 如果这个假设不成立，LSTM 即使在随机留出的同分布 test experiment 上有很高 \(R^2\)，也可能在新的 source dynamics、CPL 控制器、温度、老化或 mode transition 上给出错误但看似平滑的波形。

论文为该假设提供的正面证据是：实验覆盖 240-300 V、多负载功率、CCM/DCM、1512 个 load-change experiment，且 512 个 test experiment 的总体误差很低。[pdf:E10][pdf:E12][pdf:E14] 反面证据同样明确：fast input-voltage transient 被排除；CCM-to-DCM 的 7/102 个 case 已出现 overshoot 失配；实际 sampling frequency、split protocol、sequence length、预处理与 uncertainty estimate 未报告。[pdf:E10][pdf:E17]

因此，基于证据的判断是：论文支持的是“观测分布内 interpolation”，而不是“whole behavior”在开放航空工况中的充分辨识。这个假设一旦失败，核心贡献会直接从 converter model 降为特定数据集的 waveform emulator。

## § 10 — 最小复现实验

一周内不必复建完整 MEA distribution system，可以只验证“一个 LSTM 是否真的跨 CCM/DCM boundary 优于无记忆或较短记忆模型”。

**数据。** 使用同型号 converter 或可获得的 270 V-to-28 V regulated converter，采集 \(V_\mathrm{in},I_\mathrm{out},I_\mathrm{in},V_\mathrm{out}\)。在安全功率范围内选 3 个输入电压、4 个稳态功率点，并安排至少两组跨越约 50 W conduction-mode boundary 的 connect/disconnect sequence。采样率必须高于被测器件 switching frequency；本论文器件为 700 kHz，但实际复现实验的采样率应以设备 bandwidth 与 anti-aliasing 设计确定，而不是照抄未报告值。[pdf:E11]

**实现。** 用四层 sequence-input/LSTM/fully-connected/regression 结构，先复用论文报告的 96 hidden units、LR 0.01415、gradient decay 0.9799、L2 \(9.06\times10^{-7}\) 作为起点；同时实现一个 NARX 或 1-D CNN baseline。论文说 datasets 和 codes “available upon request”，PDF 本身没有附可直接运行的数据与代码，因此这一步可能需要自行采集或向作者申请。[pdf:E13]

**切分。** 不做随机点切分，而是整段保留一个输入电压、一个 CPL 组合和全部 CCM-to-DCM transition 作为 out-of-group test；这样可以防止相邻 waveform 泄漏让 \(R^2\) 虚高。

**测量。** 报告两个输出的 RMSE、\(R^2\)、overshoot amplitude error、settling-time error，并画 measured-versus-estimated waveform。支持核心 claim 的最低条件不是复刻某个表格数字，而是 LSTM 在被整组留出的 CCM、DCM 与跨界 transient 上都稳定优于 baseline，且 overshoot 优势没有只出现在随机同分布样本。若优势在 grouped split 下消失，或 boundary error 系统性增加，就反驳“一个模型覆盖完整运行区域”的解释。

## § 11 — 最强反例设计

最强反例不是再找一个平均 RMSE 稍差的 operating point，而是构造**端口瞬时值相近、隐藏内部状态不同**的两类历史。训练集只含论文式的稳态输入电压加 load change；测试时加入三种整组未见扰动：快速 \(V_\mathrm{in}\) step、不同控制带宽的 CPL、以及温升后从 CCM 向 DCM 的反复切换。对每类扰动，匹配相同的当前 \(V_\mathrm{in}\) 与 \(I_\mathrm{out}\)，但让 converter 内部 controller/integrator 与 energy-storage state 不同。

如果相同可见端口历史窗口对应多个未来响应，有限窗口 LSTM 就面临不可辨识性；如果它仍输出单一平滑轨迹，平均 RMSE 可能不高，却会漏掉稳定性相关的 overshoot。论文自己已经给出两个攻击入口：它没有采集 fast input-voltage transient，并在 CCM-to-DCM transition 上出现 6.86% 的 instantaneous overshoot failure。[pdf:E10][pdf:E17]

反例成立的判据是：在整体 grouped test 中，LSTM 相对 gray-box/NARX baseline 的优势消失，或者产生足以改变 protection threshold、bus-voltage margin 或 settling-time 判断的系统误差。那将说明现有结果更可能来自同分布 interpolation，而不是已学到可迁移的 converter dynamics。

## § 12 — Follow-up Research Idea

在 power electronics 领域，高影响工作通常不仅要求低平均误差，还要求明确的物理边界、跨工况实验、闭环稳定性、可复现性，以及面向实际仿真/控制平台的可实现证据。当前论文在真实实验与 waveform fidelity 上较强，但在 distribution shift、uncertainty、interconnection stability 与 deterministic execution 上没有闭合。

一个不声称 novelty 的候选方向是：**把“离线单波形预测”改写为“带可拒绝机制的端口行为契约”。** 模型不只输出 \(I_\mathrm{in},V_\mathrm{out}\) 的点估计，还输出 uncertainty 与 domain-of-validity；训练目标同时约束端口增量耗散或 passivity，并在输入历史落到训练域外时拒绝给出“可信模型”结论。它改变的是问题定义：目标不再是把所有工况都压进一个高 \(R^2\) emulator，而是在可证明的有效域内提供可组合模型，在有效域外暴露未知。

- **未满足需求**：MEA 系统级仿真必须知道模型何时不可信，否则小概率 CCM/DCM transition error 可能被当成真实稳定裕度。
- **潜在研究价值**：把 accuracy、uncertainty coverage、interconnection stability 与 execution budget 放进同一套可证伪验收，比单纯增加 LSTM depth 更接近工程采用。
- **可借鉴工具**：nonlinear system identification 的 state observability、passivity/dissipativity、distributionally robust learning 与 conformal prediction。
- **首个证伪实验**：训练仍只用本文式 load change，测试整组 withheld 的 fast input-voltage step、未见 CPL 和温度变化；同时把多个 learned converter 接到同一 DC bus。若 uncertainty 不能在高误差前升高，或 passivity constraint 仍不能阻止 interconnection instability，想法即被证伪。
- **与本文的实质区别**：本文优化的是已采样分布中的 point prediction；候选工作优化的是“何时允许相信、何时必须拒绝以及多个模型连接后是否仍安全”。若后续要求 FPGA/EMT 实现，还必须另行报告定点误差、资源、pipeline、WCET 与 real-time step；本文没有提供这些证据。

由于本卡严格只使用源 PDF、没有联网完成相关工作检索，这一方向仅是证据约束下的候选研究想法，不声称 novelty。
