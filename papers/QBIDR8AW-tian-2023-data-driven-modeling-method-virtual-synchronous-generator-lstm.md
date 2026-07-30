# A Data-Driven Modeling Method of Virtual Synchronous Generator Based on LSTM Neural Network

作者：Jiangbin Tian，Guohui Zeng，Jinbin Zhao，Xiangchen Zhu，Zhenhua Zhang  
出处：IEEE Transactions on Industrial Informatics，Vol. 20，No. 4，pp. 5428–5439  
年份：2024（在线发表日期为 2023-12-04）  
DOI：10.1109/TII.2023.3333673  
Zotero key：QBIDR8AW  
证据说明：

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的是：当 virtual synchronous generator（VSG）包含开关谐波、滤波器与线路寄生参数、多机并联、光伏或风电侧波动等复杂因素时，如何避开高阶小信号模型在“复杂度”和“精度”之间的矛盾，直接从运行时序数据建立输入电气量到目标输出电气量的动态映射。作者的核心 claim 是，带有一段历史窗口的 LSTM surrogate 比传统小信号模型、普通 RNN 以及只看前一时刻的 single-step LSTM 更准确、更稳定，并能覆盖 PV VSG、风电 VSG、双机并联和并离网切换等多种仿真场景 [pdf:E01]（PDF 物理页 1，Abstract 与 Section I）。

这个问题重要，不只是因为“神经网络拟合得更好”。VSG 的用途是让电力电子并网装置表现出同步机的虚拟惯量和阻尼；模型若遗漏开关谐波、线路电阻、滤波电容或变压器漏感，就可能在控制参数整定和扰动评估时给出错误的动态判断。论文指出，常用小信号建模会做小角度近似、忽略滤波电容和线路电阻，并把 PWM 调制电压等同于桥臂输出，从而漏掉开关引起的高频分量；双 VSG 并联系统的传递函数甚至可有 29 个以上根 [pdf:E03]（PDF 物理页 3，Section II-B–II-C，Fig. 1–2 与 Eq. (2)–(4)）。因此，若数据驱动模型真能在不显式展开全部内部机理的情况下保持跨工况可信度，它可降低建模门槛；但若它只是在同一仿真器分布内插值，则这种价值不能外推到真实装置。

## § 2 — 前人工作与不足

论文把前人路线分成三类。第一类是 VSG 小信号模型：它们能够给出控制回路与参数的解析关系，但需要简化非线性、寄生元件和高频开关行为，系统一复杂，阶数和参数数目就迅速膨胀 [pdf:E03]（PDF 物理页 3，Section II-B–II-C）。第二类是一般数据驱动模型，例如 BP 网络或微电网等值模型，它们能学习输入输出映射，但未必利用 VSG 电气量的时间相关性。第三类是最接近本文的 Yang 等人 [17]：已经用 LSTM 预测 VSG 下一时刻输出电压，但只输入单一时刻电气量，没有真正使用历史序列，也没有给出完整建模流程或复杂场景验证；Li 等人 [18] 则面向 VSG 集群的数据-物理建模，但没有显式处理电气量的时序相关性 [pdf:E02]（PDF 物理页 2，Section I）。

作者还讨论了 GRU、Transformer、N-BEATS、ST-GAE 和 STGDL 等时序方法，承认 LSTM 不是唯一选择：GRU 更轻量，Transformer 和 N-BEATS 更适合某些长序列或大数据条件，而 LSTM 被选中是因为作者认为它在当前规模数据上较平衡 [pdf:E02]（PDF 物理页 2，Section I）。参考文献表也确认了本文直接依赖的 VSG 数据驱动工作 [17]、VSG cluster 工作 [18] 以及 GRU、Transformer、N-BEATS 和图时序方法 [19]–[22] 的身份 [pdf:E12]（PDF 物理页 12，References [17]–[22]）。因此，本文真正推进的不是发明 LSTM，而是把“多步历史窗口 + VSG 多场景输入输出特征选择 + 完整训练流程 + 多种仿真对比”组合成一套 VSG surrogate 建模方法。

## § 3 — 重建作者的思考路径

下面是基于论文证据的合理重建，不是作者逐字陈述。

第一步，研究者先观察到 VSG 的机理并非未知：转子机械方程、定子电压方程和虚拟励磁方程都可以写出，但为了得到可用的小信号传递函数，必须忽略若干寄生与开关细节；在多机并联、PV 和风电供能时，这个解析模型会进一步变复杂 [pdf:E03]（PDF 物理页 3，Section II）。第二步，既然建模目标主要是预测某个输出电气量，而不是解释每个内部状态，就把问题改写为“从一组同时采集的电压、电流、功率、指令和电网量，学习目标量的映射” [pdf:E04]（PDF 物理页 4，Fig. 3、Table I–II）。第三步，普通 feed-forward 网络不能自然利用历史依赖，早期 single-step LSTM 又只看一个时刻，于是将当前时刻之前的固定窗口作为 LSTM 输入，使 cell state 承载历史影响。第四步，为避免只在单一工况成立，作者在 PV、风电、双 VSG 并联、故障与并离网切换场景中改变参数，分别收集训练、验证和测试数据，再用 RMSE 与 \(R^2\) 选择超参数和比较模型 [pdf:E04]（PDF 物理页 4，Fig. 4 与 Section III-C）。

这条思路的关键转折是：不再努力把所有“难建模因素”逐项写进解析方程，而是让这些因素先在高保真仿真输出中留下痕迹，再让序列模型学习其联合影响。它能降低显式建模负担，却把可信度问题转移到了数据覆盖、仿真器真实性和分布外泛化上。

## § 4 — 核心 Intuition

VSG 当前输出不仅取决于当前指令和电气量，也取决于此前一段时间内惯性、阻尼、控制环和开关行为积累下来的轨迹。LSTM 用门控 cell state 保留这段轨迹，比只看单点的模型更有机会区分“瞬时数值相同但历史不同”的状态 [pdf:E07]（PDF 物理页 7，Section IV-E 与 Algorithm 1）。作者用多工况仿真数据训练这个历史到输出的映射，希望把小信号模型显式丢弃的非线性与高频因素隐含进 surrogate。

## § 5 — 具体方法与完整 Pipeline

以“预测双 VSG 并联时交流母线频率”为例，完整 pipeline 如下。

1. **建立数据源。** 在 MATLAB/Simulink 中建立 VSG 模型；论文分别构造 PV VSG、风电 VSG、双机并联及并离网切换场景。双机实验通过给两台 VSG 配置不同附加电阻和电感制造参数差异 [pdf:E04]（PDF 物理页 4，Section III-C 与 Fig. 4）。
2. **选输入和输出。** 通用候选输入包括 VSG 输出电压、电流、有功/无功功率、输出电压幅值和相角指令、电网频率以及有功/无功指令；三相量只取 A 相。不同场景另加 PV/风电功率、并网指令和 PCC switch 状态。一个场景只选一个典型输出，例如双机并联输出 AC bus frequency [pdf:E04]（PDF 物理页 4，Table I–II）。
3. **覆盖工况并采样。** 对功率指令变化、电网频率跌落、单相接地、两相短路、双机参数差异和并离网切换分别运行仿真，在同类工况内替换参数后重复采集。数据按时间排列为二维数组，第一列是输出，其余列是输入；随后划分 training、validation 和 test set [pdf:E04]（PDF 物理页 4，Section III-C）。
4. **构造历史窗口。** 论文设 PWM switching frequency 为 20 kHz、sampling interval 为 \(1\,\mu s\)，并使用 5000 点、名义长度 5 ms 的历史窗口；Table III 给出的网络为一层 LSTM、10 个 neuron、ReLU、drop size 0.1、Adam、batch size 32、learning rate 0.001 [pdf:E05]（PDF 物理页 5，Table III）。这里必须保留一个原文矛盾：物理页 8 又写“sampling rate 1 ms”且“5 ms 含 5000 点”，只有 \(1\,\mu s\) 才与 5000 点一致，因此严格复现应以 Table III 和代码核对为准，不能把这句单位表述当成已闭合事实 [pdf:E08]（PDF 物理页 8，Section IV-E）。
5. **归一化与训练。** 每个特征用 max–min normalization 缩放到 \([-1,1]\)，LSTM 前向产生预测值，以 MAE 训练，通过反向传播更新权重；validation set 上的 RMSE 与 \(R^2\) 不达标时继续调整超参数，满足标准后导出模型 [pdf:E06]（PDF 物理页 6，Eq. (11)–(12)）[pdf:E07]（PDF 物理页 7，Algorithm 1）。
6. **测试与比较。** 在未参与训练/验证的 test set 上，与 RNN、small-signal model、single-step LSTM、SVR、GRU 和 N-BEATS 比较，并另加白噪声以及 RAE/DTDL preprocessing 检查鲁棒性 [pdf:E10]（PDF 物理页 10，Section V-B–V-E）。

从 EMT/FPGA 实现角度看，论文报告的是“Simulink 生成数据、TensorFlow.Keras 在 CPU/GPU workstation 上训练与评估”的软件 pipeline。它没有报告用于生成数据的 EMT solver 类型、固定步长与事件调度细节，没有说明模型如何逐步反馈进闭环仿真，也没有给出多速率调度、fixed-point 格式、量化误差、FPGA mapping、resource、pipeline initiation interval、latency、WCET 或 HIL 实验。其复杂度分析只给出 LSTM 的渐近量级 \(O(mp^2)\)，并以 \(p=10\)、2 s、\(m=2\times10^6\) 估计为 \(O(2\times10^8)\)；这不是实时执行时延证明 [pdf:E06]（PDF 物理页 6，Section IV-B）。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有建立新的控制理论定理，数学部分主要由“物理 baseline、LSTM recurrence、归一化和误差指标”组成。

首先，VSG 的虚拟转子运动用

\[
J\frac{d\omega}{dt}=T_m-T_e-D(\omega-\omega_0),\qquad
\theta=\int(\omega-\omega_0)\,dt
\]

表示，其中 \(J\) 是虚拟惯量，\(D\) 是阻尼，\(T_m,T_e\) 分别是机械与电磁转矩，\(\omega,\omega_0\) 是实际与额定电角速度，\(\theta\) 是相角 [pdf:E02]（PDF 物理页 2，Eq. (1)）。定子电压与虚拟励磁支路写为

\[
\dot U_{abc}=\dot E_{abc}-\dot I_{abc}(R_{abc}+jX_{abc}),
\qquad
L\frac{di_{abc}}{dt}=e_{abc}-u_{abc}-Ri_{abc}.
\]

这些式子说明输出电压、电流和相角具有真实动态记忆，而不是静态回归关系 [pdf:E03]（PDF 物理页 3，Eq. (2)–(3)）。

作为比较对象，主动功率小信号模型为

\[
G(s)=\frac{P_e^*(s)}{P_{\mathrm{ref}}^*(s)}
=\frac{\omega_0S_E/H}{s^2+(D_P/H)s+\omega_0S_E/H},
\]

其中 \(S_E\) 是同步功率标准值，\(H\) 是惯性时间常数，\(D_P\) 是有功-频率下垂系数。它的简洁来自小角度近似以及对滤波电容、线路电阻和 PWM 高频项的忽略 [pdf:E03]（PDF 物理页 3，Eq. (4) 与 Fig. 2）。

LSTM 用门控 recurrence 保存历史。遗忘门、输入门与候选 cell state 为

\[
f_t=\sigma(W_f[h_{t-1},x_t]+b_f),
\]
\[
i_t=\sigma(W_i[h_{t-1},x_t]+b_i),\qquad
\widetilde C_t=\tanh(W_c[h_{t-1},x_t]+b_C),
\]

再用

\[
C_t=f_t*C_{t-1}+i_t*\widetilde C_t
\]

更新 cell state，输出门与 hidden state 为

\[
o_t=\sigma(W_o[h_{t-1},x_t]+b_o),\qquad
h_t=o_t*\tanh(C_t).
\]

直观上，\(f_t\) 决定保留多少旧状态，\(i_t\) 决定写入多少当前信息，\(o_t\) 决定暴露多少记忆用于预测；\(*\) 是逐元素乘法 [pdf:E05]（PDF 物理页 5，Eq. (6)–(7) 与 Fig. 5）[pdf:E06]（PDF 物理页 6，Eq. (8)–(10) 与 Fig. 6）。

输入归一化使用

\[
x_{\mathrm{std}}=\frac{x-x_{\min}}{x_{\max}-x_{\min}},\qquad
x_{\mathrm{scaled}}=x_{\mathrm{std}}(\mathrm{Max}-\mathrm{Min})+\mathrm{Min},
\]

并把范围设为 \([-1,1]\)。训练 loss 是

\[
\mathrm{MAE}=\frac{\sum_{i=1}^n|y_i-\hat y_i|}{n},
\]

测试报告 RMSE 和 \(R^2\) [pdf:E06]（PDF 物理页 6，Eq. (11)–(12)）。值得注意的是，论文 Eq. (5) 打印的 \(R^2\) 为 \(\sum(\hat y_i-\bar y)^2/\sum(y_i-\bar y)^2\)，而不是常见的 \(1-\mathrm{SSE}/\mathrm{SST}\)；因此仅凭公式无法确定作者代码实际采用哪一定义，复现时必须检查实现 [pdf:E05]（PDF 物理页 5，Eq. (5)）。

## § 7 — 实验设计与结论

实验平台是 MATLAB/Simulink R2022a 生成 VSG 数据，Python 3.9 与 TensorFlow.Keras 2.11.0 建模，workstation 配置为 Intel Xeon W-2245、64 GB RAM 和 NVIDIA 2080 Ti GPU。基础仿真参数包括 \(U_{dc}=800\) V、grid voltage 380 V、50 Hz、\(C_f=100\,\mu F\)、\(L_f=0.8\) mH、\(L_g=1.2\) mH、\(J=0.2\,kg\cdot m^2\)、\(D=15\) [pdf:E08]（PDF 物理页 8，Table IV 与 Section V）。

**问题 1：LSTM 是否比普通 RNN 更能利用 VSG 时序？** 作者在 PV/风电有功指令变化、0.55 Hz 电网频率跌落、A-G 与 A-B 故障、双机有功/无功指令变化和并离网切换上比较输出波形。Table V 中，LSTM 在 PV VSG、wind VSG、parallel、seamless switching 的 \(R^2\) 分别为 0.9998、0.9988、0.9993、0.9961；对应 RNN 为 0.9713、0.9491、0.6883、0.9804，且 LSTM 的 RMSE 均更低 [pdf:E09]（PDF 物理页 9，Fig. 9–11 与 Table V）。答案是在这些 Simulink test sets 上成立，尤其并联场景差距明显；它不等价于真实装置泛化。

**问题 2：数据驱动模型是否优于 small-signal model？** 受控直流源 VSG 在 1.5 s 把有功指令从 100 kW 提高到 150 kW；LSTM 的 RMSE/\(R^2\) 为 0.2672/0.9999，小信号模型为 4.1287/0.9728 [pdf:E10]（PDF 物理页 10，Fig. 12(a) 与 Section V-B）。答案是在该单一仿真阶跃上，LSTM 更贴近“measured data”；这里的 measured data 仍是仿真输出，不是示波器实测。

**问题 3：5000-step history 是否优于 single-step LSTM？** 在 seamless switching、double VSG parallel 和 single VSG 三类实验中，5000-step 模型的 combined RMSE/\(R^2\) 为 0.0928/0.9978，single-step 为 0.4683/0.9474 [pdf:E10]（PDF 物理页 10，Fig. 12(b1)–(b3) 与 Table VI）。答案支持“历史窗口有用”，但论文没有给出窗口长度扫描、有效记忆长度或参数量/训练预算控制，因而不能断言 5000 点是必要或最优。

**问题 4：LSTM 是否是所有时序算法中最好？** Table VII 比较 SVR、RNN、GRU、N-BEATS 和 LSTM。平均 \(R^2\) 最高的是 N-BEATS 0.9986，LSTM 为 0.9985；LSTM 在 PV、wind 与 parallel 场景表现接近最优，而 N-BEATS 在 seamless switching 的 RMSE 更低 [pdf:E11]（PDF 物理页 11，Table VII）。因此论文能支持的是“LSTM 较均衡”，不能支持“LSTM 全面最优”。

**问题 5：噪声下是否稳定？** Table VIII 给白噪声标记从 0 到 40 dB 的结果：最后一行 LSTM baseline 的 \(R^2\) 为 0.8125，LSTM+RAE 为 0.9340，LSTM+DTDL 为 0.9755。作者据此认为 feature extraction/noise processing 能改善鲁棒性 [pdf:E11]（PDF 物理页 11，Table VIII 与 Section V-E）。但噪声注入位置、统计重复次数、置信区间和真实传感器噪声谱未报告。

总体实验结论是：论文较充分地证明了同一仿真生态内的拟合优势，却没有验证真实 VSG、不同仿真器、不同控制器实现、闭环 rollout 稳定性或实时部署。

## § 8 — Take-aways

**5 句话。**  
1. 论文把复杂 VSG 等值建模改写为历史电气量到目标输出量的 sequence regression，并给出从场景设置到超参数调整的完整流程。  
2. 5000-step LSTM 在作者的 PV、风电、并联、故障与并离网 Simulink test sets 上明显优于 RNN 和 single-step LSTM [pdf:E09]（PDF 物理页 9，Table V）[pdf:E10]（PDF 物理页 10，Table VI）。  
3. 与小信号模型相比，它能拟合被解析简化遗漏的非线性与高频痕迹，但这种能力来自训练数据而非新的物理约束。  
4. N-BEATS 的平均 \(R^2\) 略高于 LSTM，噪声 preprocessing 也显著改变结果，因此“选择 LSTM”是平衡性判断，不是算法唯一性结论 [pdf:E11]（PDF 物理页 11，Table VII–VIII）。  
5. 论文没有真实硬件、闭环长期稳定性、fixed-point、FPGA 资源或 WCET 证据，不能直接作为 EMT/FPGA 实时模型的可部署性证明。

**3 句话。**  
1. 最有价值的贡献是把多步历史窗口真正放进 VSG 多场景数据驱动建模流程，而不只是换一个 neural network 名称。  
2. 最强证据是仿真 test set 上对 RNN、small-signal 和 single-step LSTM 的一致优势，最弱环节是数据全部来自作者自己的 Simulink 模型。  
3. 因此应把它视为“promising simulation surrogate”，而不是已经被证明可跨设备、跨步长、闭环稳定或实时部署的 universal VSG model。

**1 句话。**  
这篇论文证明了历史窗口能改善 VSG 仿真 surrogate 的拟合，但尚未证明该 surrogate 在训练分布之外仍保留物理可信度和工程可部署性。

## § 9 — 最脆弱的假设

最脆弱的假设是：**由同一 Simulink 体系生成、按作者方式划分的多工况数据，足以代表模型部署时会遇到的 VSG 动态分布。** 一旦这个假设不成立，LSTM 的高 \(R^2\) 可能只是在仿真器内部做高维插值；它学到的可能是特定控制器、solver、采样设置和参数扫描的联合指纹，而不是可迁移的 VSG 动态规律。

论文给出的正面证据是：同一工况内改变参数、明确区分 training/validation/test set，并覆盖指令变化、频率扰动、故障、双机并联和并离网切换 [pdf:E04]（PDF 物理页 4，Section III-C）；还加入白噪声并尝试 RAE/DTDL preprocessing [pdf:E11]（PDF 物理页 11，Section V-E）。缺失的关键证据是：数据划分是否按独立轨迹而非相邻时间点、训练与测试的参数区间是否真正不相交、是否换过 EMT solver 或 controller、是否在真实 converter 上测试、recursive closed-loop rollout 是否稳定，以及不同 sampling interval 下是否仍保持相同映射。论文甚至声称采样可降到 1 ms 而不损害系统行为，但没有对应实验 [pdf:E06]（PDF 物理页 6，Section IV-B）。这正是失败代价最大的地方。

## § 10 — 最小复现实验

一周内最值得做的不是重画所有论文波形，而是做一个“按轨迹和参数完全隔离”的最小泛化实验。

1. 在一个可获得的 switching VSG Simulink/EMT 模型中，只复现有功指令阶跃场景，采集论文 Table I 的核心输入量与 A 相输出电流；使用 \(1\,\mu s\) 采样并构造 5000 点窗口。  
2. 实现相同的一层 10-neuron LSTM、single-step LSTM 和同规模 RNN，统一 normalization、训练轮次与 parameter budget；另保留一个小信号 baseline。  
3. 不随机打散采样点，而是把完整运行轨迹按 VSG 参数组分开：训练只看一组 \(J,D,L_f,R\)，测试使用完全未见的参数组和未见阶跃幅值。  
4. 同时报 one-step RMSE/\(R^2\) 与 0.5 s recursive rollout 的幅值误差、相位误差和是否发散；复现论文 Eq. (5) 时核对实际 \(R^2\) 实现，避免公式歧义 [pdf:E05]（PDF 物理页 5，Eq. (5) 与 Table III）。  

若 multi-step LSTM 在未见参数组上仍明显优于 RNN、single-step 和 small-signal baseline，并且 recursive rollout 不发散，则核心 claim 得到初步支持；若优势只在随机点划分时存在，换成 trajectory-wise split 后消失，或 one-step 很准而 rollout 漂移，则核心 claim 被实质反驳。论文未报告公开 dataset 或 source code，因此这个复现验证的是方法机制，不承诺逐字节复现其 Table V。

## § 11 — 最强反例设计

最强反例是做一次**采样与开关条件错配的跨域测试**。只在 20 kHz switching frequency、\(1\,\mu s\) sampling interval、固定 dead time 和固定 solver 上训练，然后不微调地测试 10 kHz/40 kHz switching、不同 dead time、传感器 delay、不同 sampling phase，以及 \(2\,\mu s\) 或 \(10\,\mu s\) sampling interval；同时保持低频有功响应看起来相近。这个设计直接攻击作者“非线性映射与 sampling rate 独立”以及“降采样不损害系统行为”的论断 [pdf:E08]（PDF 物理页 8，Section IV-E）[pdf:E06]（PDF 物理页 6，Section IV-B）。

如果 LSTM 主要记住了 20 kHz 开关纹波在固定采样网格上的相位模式，那么一旦开关频率或采样相位改变，one-step RMSE 会突然增大，recursive rollout 还可能产生非物理能量或相位漂移；反而只保留低频结构的小信号/physics baseline 可能更稳。这会给出一个具体替代解释：论文中的高精度来自“对固定仿真采样纹理的拟合”，而不是对可迁移 VSG 动力学的学习。若模型在上述错配下仍稳定，并能保持基波、谐波和功率平衡误差受控，这个反例才算被击败。

## § 12 — Follow-up Research Idea

**候选方向：面向实时闭环的 event-aligned、physics-constrained VSG surrogate compiler。** 这是基于本论文缺口提出的候选判断；本卡未联网检索相关工作，因此不声称 novelty。

**（a）需求。** 当前方法把“拟合历史数据”当作终点，但 EMT/HIL 真正需要的是：在 switching event、fault 和 controller mode change 下，模型能以固定步长递归运行，输出满足电气约束，并有确定的 per-step latency。论文只报告 workstation 上的 TensorFlow.Keras 环境 [pdf:E08]（PDF 物理页 8，Section V），没有 FPGA 或实时闭环证据。

**（b）潜在研究价值。** 把研究目标从 one-step \(R^2\) 改成“跨开关条件的闭环稳定误差 + 物理约束违背率 + 可综合固定时延”，会同时回答模型可信度和实时执行两件事；这比再换 GRU/Transformer 或再加一个 denoiser 更可能形成电力电子领域认可的工程贡献。

**（c）可借鉴工具。** 可从 hybrid system identification 借鉴 event-aligned state update，从 physics-informed learning 借鉴 KCL/KVL、功率平衡或 passivity penalty，从 neural network quantization/HLS 借鉴 fixed-point sensitivity、operator scheduling 和 worst-case latency analysis。具体结构可以是“解析的低频 VSG/Norton 骨架 + 小型 recurrent residual”，让网络只学未建模的开关与寄生残差，而不接管全部物理状态。

**（d）首个证伪实验。** 在完全未见的 switching frequency、dead time、线路参数和 fault clearing time 上，对比本文 LSTM、纯 physics baseline 与 hybrid residual；要求在固定 \(1\,\mu s\) step 下做长时 recursive rollout，并同时通过电流/频率误差、功率不平衡、passivity violation、fixed-point degradation 和 FPGA/HLS latency gate。只要 hybrid 不能在这些指标上同时优于两类 baseline，或者综合后不能满足固定步长，方向就被早期证伪。

**（e）实质区别。** 本文的主要对象是“用一段历史预测下一输出”，评价核心是 Simulink test set 的 RMSE/\(R^2\)；候选方向把对象改成“可递归、事件对齐、受物理约束且可部署的闭环状态更新器”，评价核心也改成跨域稳定性与确定执行时间。这个改变针对的是问题定义和验收标准，而不是单纯增加网络层数或替换 LSTM。
