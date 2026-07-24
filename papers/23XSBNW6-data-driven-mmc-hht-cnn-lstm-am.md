# Data-Driven Modeling of Modular Multilevel Converters Based on HHT and CNN-LSTM-AM Neural Network

作者：Jiangbin Tian、Jinbin Zhao、Guohui Zeng、Xiangchen Zhu、Bo Huang、Lei Wang  
出处：*IEEE Transactions on Industrial Electronics*, Vol. 72, No. 9, 2025, pp. 8725–8735  
年份：2025  
DOI：10.1109/TIE.2024.3433509  
Zotero key：23XSBNW6

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的问题是：MMC（modular multilevel converter，模块化多电平换流器）的机理模型维数高、内部电气量耦合复杂，能否不显式求解完整机理方程，而从运行数据中学习“过去一段时间的可测电气量 → 下一采样点目标电气量”的映射。作者选用 CNN-LSTM-AM，其中 CNN 负责输入特征提取，LSTM 负责时间依赖，attention mechanism 负责对 LSTM 输出加权；对于普通电气量难以直接拟合的频率，再加入 HHT（Hilbert–Huang transform）产生的瞬时频率和瞬时幅值特征（PDF 物理页 1，Abstract）[pdf:E01]。

工程意义有两层。第一，MMC 的子模块电容电压、桥臂环流、功率和交流量同时变化，详细开关或平均机理模型往往需要在精度与计算效率之间折中；一个快速 surrogate（代理模型）可能服务于在线预测、控制器评估或 digital twin。第二，论文关注的是单步预测：Fig. 1 明确把数据驱动模型定义成“预测一个时间步后的电气量”，所以它首先是有真实历史观测持续校正的短时预测器，而不是已经证明能够脱离真实系统独立滚动的 MMC 仿真器（PDF 物理页 2，Fig. 1 与 Section I-B）[pdf:E02]。

## § 2 — 前人工作与不足

作者将相关路线分为 mechanism model 与 nonmechanism model。机理路线通过小信号模型解释系统内部动态，但推导、线性化与简化会带来工作量和适用边界；非机理路线则从运行数据学习输入输出映射。论文列举了 fully convolutional network 潮流计算、physics-informed VSC impedance identification，以及以机器学习模拟 MMC-MPC 控制器的工作；这些工作说明神经网络已进入电力电子建模与控制，但并不等于已经建立 MMC 被控对象的多电气量时序代理（PDF 物理页 1–2，Section I-A）[pdf:E01][pdf:E02]。

最接近的直接起点是作者团队此前的 VSG 数据驱动模型。本文认为既有 VSG-LSTM 在频率预测、抗干扰和更复杂映射上不足，因此把对象推进到 MMC，并采用 CNN-LSTM-AM 与 HHT。需要准确界定其增量：CNN-BiLSTM-AM 组合来自既有时间序列工作，本文的实质贡献是把这类结构用于 MMC 多电气量单步建模，并为频率增加 HHT 特征；源 PDF 没有提供 CNN-only、LSTM-AM 或 causal HHT 的独立消融，因此不能把精度提升分别归因于 CNN、attention 或 HHT 的某一内部机制（PDF 物理页 2，Section I-B）[pdf:E02]。

## § 3 — 重建作者的思考路径

从论文前提可以重建出如下路径：

1. MMC 机理建模复杂，但运行轨迹已经携带电气量之间的映射关系，因此先把问题改写成监督式单步预测。
2. 电压、电流和功率具有时间相关性，单个时刻不足以描述状态，故用 50 个历史采样点作为输入窗口。
3. 纯 LSTM 能记忆时间依赖，却未必能在多特征复杂映射中稳定筛选信息，于是前接 CNN、后接 attention。
4. 网频是周期信息，原始电气量直接回归效果不好，于是先用 EMD/Hilbert 分析提取 IMF 的瞬时频率与幅值。
5. 用多组运行指令训练，以未直接参与训练的功率指令变化、负载变化和不平衡电网工况测试，再与纯 LSTM 和一个小信号模型比较（PDF 物理页 2–7，Sections I-B、IV、V、VI-A）[pdf:E02][pdf:E05][pdf:E06][pdf:E07]。

这条路径能得到高精度的一步拟合器，但还没有自然跨过三个部署门槛：HHT 特征能否严格因果获得、预测误差在 free-running（自由滚动）时是否累积、训练外参数与控制模式变化时模型是否仍满足电气约束。后续批评围绕这三个缺口展开。

## § 4 — 核心 Intuition

核心 intuition 是：不要让一个静态网络只看当前点，而让模型观察过去 5 ms 的多电气量轨迹，用 LSTM 保存时间状态，并用 CNN 与 attention 重新组织信息后预测下一个点。对于频率，先把电压、电流分解成与周期变化更直接相关的 IMF 瞬时量，再交给同一时序模型（PDF 物理页 4–6，Table I、Section IV、Section V-B）[pdf:E04][pdf:E05][pdf:E06]。

## § 5 — 具体方法与完整 Pipeline

以逆变模式下有功指令阶跃为例，完整 pipeline 如下：

1. **选取可测特征。** 逆变侧候选量包括上下桥臂子模块电容电压、三相环流、有功指令、A 相电压电流、P、Q 与频率；整流侧还包括故障指令、交流侧量、DC 侧电压与功角。平衡电网下只取一相电压电流；某个特征作为输出时不再作为输入（PDF 物理页 5，Table III 与 Section V-A）[pdf:E05]。
2. **形成时序窗口。** 大部分实验的采样间隔为 0.1 ms，time step/window 为 50，即用此前 5 ms 预测 5.1 ms 的一个点。Section VI-D 为观察 PWM 周期内波动改用 1 μs 采样（PDF 物理页 4、6、8，Table I、Section V-B、Section VI-D）[pdf:E04][pdf:E06][pdf:E08]。
3. **归一化与切分。** 输入和输出使用 max-min normalization 映射到 \([-1,1]\)，随后分为训练集与 validation set，以 MAE 训练，并按 RMSE 与 \(R^2\) 调整超参数（PDF 物理页 3、6，Fig. 3、Eq. (4)、Algorithm 1）[pdf:E03][pdf:E06]。
4. **运行 CNN-LSTM-AM。** Table I 给出的设置是 64 个卷积 filters、kernel size 1、pool size 1、20 个 LSTM neurons、dropout 0.1、Adam、batch size 32、learning rate 0.001。kernel 与 pool 都为 1，说明 CNN 在该配置下主要做逐时刻的特征混合，并未扩大时间轴感受野或降采样（PDF 物理页 4，Table I）[pdf:E04]。
5. **频率分支。** 对 A 相电压、电流做 HHT。作者在一次 1–1.1 s、A 相电压跌至初值 60% 的分析中，选出电压 IMF1 的瞬时频率，以及电流 IMF1/IMF2 的瞬时幅值，作为频率模型新增输入（PDF 物理页 5，Fig. 5 与 Section IV）[pdf:E05]。
6. **单步输出。** 每个训练模型输出一个目标电气量的下一采样值。Table II 报告 workstation 上 CNN-LSTM-AM 对一个输出的单步 prediction time 为 0.339 ms；论文因此明确指出，在该硬件上使用 0.1 ms 采样做控制没有意义，采样间隔应大于推理时间（PDF 物理页 4，Table II 与 Section III-B）[pdf:E04]。

论文的 FPGA 边界需要明确：它研究的是 MMC 数据驱动模型，并未把网络推理映射到 FPGA；源 PDF 报告的计算环境是 Intel Xeon W-2245、64 GB RAM、两块 NVIDIA 2080 Ti，算法为 Python 3.9 与 TensorFlow/Keras（PDF 物理页 7，Section VI-A）[pdf:E07]。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有提出新的 MMC 状态方程，形式化部分主要是标准 LSTM、HHT 和误差指标。LSTM 的遗忘门、输入门与输出门写为：

\[
f_t=\sigma(W_f[h_{t-1},x_t]+b_f),
\]

\[
i_t=\sigma(W_i[h_{t-1},x_t]+b_i),\qquad
C_t=f_t C_{t-1}+i_t\widetilde C_t,
\]

\[
o_t=\sigma(W_o[h_{t-1},x_t]+b_o),\qquad
h_t=o_t\tanh(C_t).
\]

物理意义是：遗忘门决定保留多少历史状态，输入门决定写入多少新信息，输出门决定当前暴露多少记忆；这些公式说明 LSTM 如何保留时间依赖，但没有把 MMC 的能量守恒、开关拓扑或电容电压边界写入网络（PDF 物理页 3，Eq. (1)–(3)）[pdf:E03]。

HHT 部分先对 IMF \(x(t)\) 做 Hilbert transform，再写成解析信号 \(A[x(t)]=x(t)+j h(t)=a(t)e^{j\theta(t)}\)，由幅值和相位变化获得瞬时量（PDF 物理页 4–5，Eq. (5)–(8)）[pdf:E04][pdf:E05]。但源 PDF 的 Eq. (5) 在积分核中写的是 \(x(t)/(t-s)\)，而标准积分应随积分变量变化；Eq. (7) 又写成 \(\arctan(x/h)\)，与 Eq. (6) 的实部/虚部关系不一致。这些可能是排印错误，也可能影响复现；论文没有代码来区分两种情况。

评估式同样存在可复现风险。Eq. (10) 把 \(R^2\) 写成 \(\sum(\hat y_i-\bar y)^2/\sum(y_i-\bar y)^2\)，而不是常用的 \(1-\mathrm{SSE}/\mathrm{SST}\)（PDF 物理页 6，Eq. (9)–(10)）[pdf:E06]。因此，表中 \(R^2\) 若来自标准库，公式只是写错；若程序按文中公式实现，数值含义会改变。正式复现必须同时报告标准定义并公开计算脚本。

## § 7 — 实验设计与结论

**问题一：完整网络是否优于纯 LSTM？ → 实验：** 逆变工况在 2 s 将有功指令从 700 kW 提到 1000 kW，预测子模块电压、三相环流、电压电流和 P/Q。**答案：** Table V 的 combined \(R^2\) 为 0.9967，LSTM 为 0.9863；多数输出 RMSE 更低。这个实验支持“完整组合在该一步预测任务上更准”，但没有单独验证 CNN 或 attention 的因果贡献（PDF 物理页 7–8，Section VI-B、Fig. 9、Table V）[pdf:E07][pdf:E08]。

**问题二：整流侧负载变化是否仍可拟合？ → 实验：** 0.8 s 并联一个 100 Ω 电阻，1 s 时 DC 负载由 100 Ω 变为 50 Ω。**答案：** Table VI 的 combined \(R^2\) 为 0.9662，LSTM 为 0.9365；但 DC 电压 \(U_{\text{load}}\) 的 \(R^2\) 只有 0.8645，说明复杂、弱相关输出仍是短板（PDF 物理页 7–8，Section VI-C 与 Table VI）[pdf:E07][pdf:E08]。

**问题三：是否优于小信号模型？ → 实验：** 以 1 μs 采样预测 0.6 s 时有功从 70 kW 到 100 kW 的变化，并与简化小信号模型比较。**答案：** CNN-LSTM-AM 报告 RMSE 3501.2582、\(R^2=0.9995\)，小信号模型为 12410.4559 与 0.9503（PDF 物理页 8–9，Section VI-D 与 Fig. 10(a)）[pdf:E08][pdf:E09]。由于神经网络直接学习生成测试轨迹的详细数据，而小信号模型有意简化结构，这一比较不能外推为“数据驱动模型普遍优于机理模型”。

**问题四：HHT 是否改善频率预测？ → 实验：** 在不平衡电网数据上比较普通 CNN-LSTM-AM 与 HHT-CNN-LSTM-AM。**答案：** Fig. 10(b) 定性显示加入 HHT 后能跟随更快的频率变化；源 PDF 明确说明该不平衡电网数据来自 Matlab/Simulink，但未给频率 RMSE、\(R^2\)、因果窗口实现或端点处理，因此只能得到定性支持（PDF 物理页 9，Fig. 10(b) 与 Section VI-E）[pdf:E09]。

**问题五：能否按主要采样率实时控制？ → 实验事实：** 主要数据间隔为 0.1 ms，而 workstation 单步推理为 0.339 ms。**答案：** 论文自己判定该硬件上 0.1 ms 控制采样不可行；因此当前证据是离线预测精度，不是已闭合的实时控制实现（PDF 物理页 4，Table II 与 Section III-B）[pdf:E04]。

## § 8 — Take-aways

**5 句话：**

1. 论文把 MMC 建模改写成“过去 50 个采样点到下一采样点”的监督学习问题（PDF 物理页 6，Section V-B）[pdf:E06]。
2. CNN-LSTM-AM 在给定逆变与整流测试中比纯 LSTM 获得更高的一步拟合精度（PDF 物理页 8，Tables V–VI）[pdf:E08]。
3. HHT 为频率提供更直接的瞬时特征，但证据只有定性曲线，因果实现未说明（PDF 物理页 5、9，Fig. 5 与 Fig. 10(b)）[pdf:E05][pdf:E09]。
4. 0.339 ms 的单步推理慢于主要实验的 0.1 ms 采样间隔，所以论文没有证明该实现可实时闭环（PDF 物理页 4，Table II）[pdf:E04]。
5. 这项工作证明了给定分布内的高精度单步拟合，没有证明可自由滚动、跨参数稳定且满足物理约束的 MMC digital twin。

**3 句话：** 最实在的结论是完整网络在两个给定工况的一步预测上优于纯 LSTM。最具特色的 HHT 频率分支同时也是证据最薄弱的部分，因为缺少数字指标、实时边界与 causal 实现。若面向 EMT/HIL 或 MPC，下一步应优先验证多步稳定性、因果性和确定性推理时间。

**1 句话：** 它得到的是高精度 MMC 时序插值器，而不是已经完成实时与物理闭合的 MMC 替代模型。

## § 9 — 最脆弱的假设

最脆弱的假设是：部署时模型能够因果获得与训练时等价的历史特征，而且一步预测误差在模型自己的输出被重新送回时不会累积。普通输出依赖真实历史窗口持续校正；频率分支又依赖 HHT 的 IMF 和 Hilbert transform。若测试阶段对完整序列离线分解，时刻 \(t\) 的特征可能受未来样本与端点处理影响，形成 target leakage；源 PDF没有说明滑动窗口 EMD、边界延拓、实时延迟或只使用过去样本的实现（PDF 物理页 4–5，Section IV）[pdf:E04][pdf:E05]。

论文提供的正面证据是给定仿真/平台数据上的单步拟合与一个 HHT 定性曲线；缺失的是自由滚动、观测噪声、参数漂移、故障外推、能量约束与不确定度测试。若这一假设失效，digital twin 和“提前一个时间步用于控制”的应用设想都会首先失效（PDF 物理页 9–10，Section VII 与 Conclusion）[pdf:E09][pdf:E10]。

## § 10 — 最小复现实验

一周内最有信息量的复现应同时检验“网络结构收益”和“HHT 是否因果”：

1. **数据。** 建立一个可复现 MMC 仿真，生成多条互不相邻的轨迹：有功阶跃、DC 负载变化、频率扰动和一个未见参数偏差。整条轨迹分配给 train/validation/test，禁止重叠窗口跨集合。
2. **实现。** 复现 Table I 的 LSTM 与 CNN-LSTM-AM；增加 persistence、线性 ARX 两个低成本 baseline。频率分支分别使用原始量、完整序列离线 HHT、仅看过去窗口的 causal HHT（PDF 物理页 4–5，Table I 与 Section IV）[pdf:E04][pdf:E05]。
3. **测量。** 报告标准定义的一步 RMSE/\(R^2\)、10/50/200 步 free-running 误差、桥臂能量或电容电压约束违例，以及单样本 worst-case latency。
4. **支持 claim。** 在按轨迹隔离的测试集上，完整网络稳定优于 baseline；causal HHT 仍改善频率；50–200 步滚动不发散；推理时间满足所声明的采样 deadline。
5. **反驳 claim。** 优势只在随机切窗或完整序列 HHT 下出现，换成 causal HHT 后消失，或一步误差小但滚动迅速漂移。

## § 11 — 最强反例设计

最强反例是“实时可见信息截断”实验。生成训练中没有的频率阶跃或短时 chirp，在多个随机时刻截断可见序列，只允许模型使用截断点之前的样本；比较完整序列 HHT、固定长度 causal HHT 与数字 PLL 特征。随后让各模型在没有真实测量纠正的条件下自由滚动 10–20 ms。

如果只有完整序列 HHT 保持 Fig. 10(b) 的跟随效果，而 causal HHT 在每个窗口末端出现大误差、延迟或振荡，说明提升主要来自不可部署的离线信号处理，而不是网络学会了 MMC 的频率动态。若单步表现仍好但自由滚动产生电容电压漂移或功率不平衡，这会同时反驳其 digital twin 与一步超前控制应用的强解释（PDF 物理页 9，Fig. 10 与 Section VII）[pdf:E09]。

## § 12 — Follow-up Research Idea

**候选想法：把目标从“逐输出单步拟合”改成“带物理约束、因果频率前端和失效检测的 MMC neural state-space model”。**

（a）未满足需求是：EMT、MPC 与 digital twin 需要能独立推进的状态，而不是每一步依赖真实系统纠正的插值器。（b）电力电子领域认可的高影响证据应包括跨参数、跨工况、HIL/样机验证、确定性 latency 和电气约束，而不仅是平均拟合分数。（c）可借鉴 neural state-space、Koopman representation、contraction/stability regularization、conformal uncertainty，以及数字 PLL 或 causal filter bank。（d）第一个证伪实验就是按轨迹隔离、因果特征、200 步自由滚动并施加未见参数偏差；若约束违例或 worst-case latency 不优于普通 LSTM，想法即失败。（e）它与本文的实质区别是把研究对象从“采样点间统计映射”改为“可持续推进并知道自己何时失效的动态系统模型”。

在没有系统检索最新 MMC physics-constrained neural state-space 文献前，这只能称为候选方向，不声称具有 novelty。
