# Effinformer: A Deep-Learning-Based Data-Driven Modeling of DC-DC Bidirectional Converters

作者：Qianyi Shang、Fei Xiao、Yaxiang Fan、Wei Kang、Haochen Qin、Ruitian Wang  
出处：IEEE Transactions on Instrumentation and Measurement，Vol. 72，Article 2529013  
年份：2023  
DOI：10.1109/TIM.2023.3318701  
Zotero key：AFZ7V45M  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“能否用神经网络拟合一个变换器”，而是更具体的工程问题：在不知道完整器件参数、又不希望向运行设备额外注入辨识激励的条件下，能否只用 DAB（dual active bridge）双向 DC-DC 变换器端口的电压、电流历史，同时重建稳态纹波和负载扰动后的瞬态，并让同一个模型兼顾计算效率、并行多输出与较长时域预测。作者把这件事表述成 multivariate time-series regression；输入是输入电压与输出电流，输出是输出电压与输入电流。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）[pdf:E04]（PDF 物理页 4，Section III-A，Eqs. (1)–(3)）

这个问题重要有两层原因。第一，DAB 含开关非线性和高频交流环节；详细物理建模依赖电感、电容、寄生参数和器件状态，而商用设备或老化设备的内部参数可能不可得。第二，传统 black-box identification 常需外部激励，可能打扰正常运行；若历史监测数据本来就在采集，非侵入式数据驱动模型有机会降低建模门槛。[pdf:E01]（PDF 物理页 1，Section I）对 EMT/FPGA 研究者而言，它的直接价值是提供一个端口行为 surrogate 的候选生成方式；但论文没有把该 surrogate 放进 EMT 求解器，也没有证明 FPGA 实时执行，所以这里的价值是“可能的模型来源”，不是已经完成的实时仿真方案。

## § 2 — 前人工作与不足

论文原文把既有路线分成三组。BR/RF 一类 classical ML 已用于 buck converter，但稳态和瞬态要用不同模型；RNN/LSTM 能提高非线性拟合能力，却逐点递推，难以并行且训练耗时；WCNN 用一维卷积提取时域特征，但普通 CNN 的 receptive field 有限，若靠堆层扩展会增加计算量。[pdf:E01]（PDF 物理页 1，Section I；refs. [14]–[20]）

Transformer 用 full self-attention 处理长依赖，但每层复杂度为 \(O(L^2)\)。Informer、Autoformer、Reformer 将其压到 \(O(L\log L)\) 量级；论文进一步指出，原 Informer distilling 中的普通 Conv1d receptive field 仍有限，且非 causal 卷积有从未来向过去泄漏信息的风险，同时其全局依赖偏好不一定突出变换器信号中的局部 trend。[pdf:E02]（PDF 物理页 2，Section I 的两项挑战与四点贡献）[pdf:E03]（PDF 物理页 3，Table I、Fig. 1 与 Section II-B）

最接近的电力电子 baseline 是 LSTM、WCNN 和 polytopic black-box model，最接近的时序 baseline 是 Transformer、Informer、Autoformer、Reformer；论文后续都做了对比。[pdf:E09]（PDF 物理页 9，Table V 与 Section V-B）这里要保留一个边界：作者称这是首次把 attention-based 方法用于 power-converter modeling，但本卡只读了该论文 PDF 及其参考文献页，没有独立检索全部同期工作，因此不能把这句话升级为已核实的 novelty 结论。[pdf:E12]（PDF 物理页 12，Conclusion 与 refs. [15]–[36]）

## § 3 — 重建作者的思考路径

可以从论文发表前已有的约束逆向得到 Effinformer，而不先假定其贡献成立。首先，DAB 的输入、输出波形是时间序列；若只依赖端口测量，问题自然变成从历史输入窗口到未来输出窗口的回归。其次，稳态波形同时含高频周期纹波，负载变化又产生低频 trend 与瞬态；只看局部窗口会漏掉慢依赖，只看所有点的 full attention 又昂贵。再次，RNN 的 sequential inference 不利于并行多输出，而 Informer 已经给出 sparse attention 与一次前向生成多个时间点的 decoder。于是合理的设计路径是：以 Informer 为骨架保留 sparse attention，再把 TCN 的 dilated causal convolution 放进 distilling 扩大历史 receptive field，并把 decoder 的 full cross-attention 也稀疏化，让模型优先追踪 trend；最后用 GLU 变体补偿非线性表达能力。[pdf:E02]（PDF 物理页 2，Section I）[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E05]（PDF 物理页 5，Fig. 5、Eqs. (4)–(8)）

这条路径的物理含义不是把开关方程“学会了”，而是用多尺度时间依赖作为端口动态的统计代理：dilation 拉长可见历史，causal padding 防止未来样本进入当前预测，ProbSparse attention 只强化少数高分时间点。它依赖数据覆盖，而不提供电路定律层面的守恒或稳定性保证。

## § 4 — 核心 Intuition

Effinformer 的核心 intuition 是：DAB 端口波形中真正决定下一段趋势的历史位置很少，没必要让每个时间点与每个时间点做 full attention；同时，要靠 dilated causal convolution 扩大只看“过去”的局部感受野。这样 encoder 负责并行压缩长历史，decoder 再用 sparse attention 强调 trend、弱化周期纹波，最后一次前向给出多个输出。[pdf:E05]（PDF 物理页 5，Fig. 5 与 ProbSparse block）[pdf:E06]（PDF 物理页 6，Figs. 7–8 与 Section III-D）

## § 5 — 具体方法与完整 Pipeline

以“输入电压发生扰动，同时电子负载变化，要估计输出电压和输入电流”为例，pipeline 如下。

1. **采集与定义输入输出。** 可编程电源和电子负载扫过运行点，示波器记录 \(v_{\mathrm{in}}, i_{\mathrm{in}}, v_o, i_o\)。网络以 \(v_{\mathrm{in}}\) 和 \(i_o\) 为输入，以 \(v_o\) 和 \(i_{\mathrm{in}}\) 为两个并行输出；论文允许在器件参数已知时额外加入电感、电容、电阻、频率、占空比等特征，但本实验采用最困难的“只有端口量”情形。[pdf:E04]（PDF 物理页 4，Section III-A 与 Fig. 3）
2. **预处理。** 原始数据先经 moving-average filter 与 downsampling，再按 \(X_i^*=(X_i-\mu)/\sigma\) 归一化。论文未报告 moving-average 窗长、downsampling 倍数，也未清楚说明 \(\mu,\sigma\) 是否只由训练集计算。[pdf:E07]（PDF 物理页 7，Section IV-A/B 与 Eq. (11)）
3. **时序表示。** 标量投影和 sinusoidal positional encoding 给样本加入时间位置。输入窗口在 modeling 实验中为 12，输出长度为 1；encoder 为 3 层、decoder 为 2 层、8 heads，batch size 32，训练 10 epochs，early stopping 8，loss 为 MAE。[pdf:E05]（PDF 物理页 5，Eq. (4)）[pdf:E08]（PDF 物理页 8，Table III）
4. **Encoder。** 每个 attention block 用 multihead ProbSparse self-attention 找出少数关键 query；两个 distilling block 以 dilated causal convolution、激活、kernel 3/stride 2 max-pooling 下采样，最终得到约 \(L/4\) 的 feature map。causal padding 只加在时间前侧，目标是既扩大 receptive field，又不使用未来信息。[pdf:E05]（PDF 物理页 5，Fig. 5、Eqs. (5)–(8)）[pdf:E06]（PDF 物理页 6，Fig. 7、Eq. (9)）
5. **Decoder 与输出。** Decoder 接收 encoder 的 \(K,V\)，把原 Informer 的 full cross-attention 换成 ProbSparse attention，并配合 masked ProbSparse self-attention；fully connected layer 同时输出 \(v_o\) 与 \(i_{\mathrm{in}}\)。ReGLU \(y=Ux\odot\max(Vx,0)\) 是论文选择的非线性层。[pdf:E04]（PDF 物理页 4，Fig. 4）[pdf:E06]（PDF 物理页 6，Fig. 8、Eq. (10)）
6. **训练与评估。** 以 MAE 优化，通过 MSE、MAE 和每 epoch 时间评价；作者对各模型做 10 次重复实验后取平均。[pdf:E08]（PDF 物理页 8，Eq. (12) 与 Section IV-C）

面向 EMT + FPGA 的覆盖边界必须说清：论文没有显式开关事件检测、离散 EMT companion model、节点导纳 stamp、Newton iteration 或多速率协同；只把采样波形当作固定窗口时间序列。训练平台是 4 张 V100 GPU、76 GB RAM，代码用 PyTorch；未报告 inference latency、固定步长实时闭环、浮点/定点位宽、量化误差、FPGA DSP/BRAM/LUT 映射、流水线时序或硬件在环结果。[pdf:E07]（PDF 物理页 7，Section IV、Fig. 10 与 Table II）因此，这篇论文验证的是 GPU 上的数据驱动建模，不是 FPGA 实时部署。

## § 6 — 核心数学推导（无形式化数学则跳过）

这篇论文有形式化定义和算子公式，但没有从 DAB 电路方程推导模型稳定性或误差界。核心数学可以分成四步。

第一步把端口建模写成窗口映射：

\[
X_t=\{x_1^t,\ldots,x_{L_x}^t\},\qquad
\hat{Y}_t=\{y_1^t,\ldots,y_{L_y}^t\},\qquad
\hat{Y}_t=F(X_t;\theta).
\]

\(L_x,L_y\) 是输入、输出窗口长度，\(d_x,d_y\) 是特征维数，\(\theta\) 是待训练参数。直观上，电路内部状态被折叠进有限历史 \(X_t\)，模型学习的是观测窗口到输出窗口的条件映射，而非器件级状态方程。[pdf:E04]（PDF 物理页 4，Eqs. (1)–(3)）

第二步用位置编码和 sparse attention 建模依赖。论文采用

\[
\mathrm{PE}_{(\mathrm{pos},2\lambda)}=\sin\!\left(\frac{\mathrm{pos}}{1000^{2\lambda/d}}\right),\quad
\mathrm{PE}_{(\mathrm{pos},2\lambda+1)}=\cos\!\left(\frac{\mathrm{pos}}{1000^{2\lambda/d}}\right),
\]

并写出选中 query 的 scaled dot-product attention

\[
A(Q,K,V)=\operatorname{softmax}\!\left(\frac{\bar QK^\top}{\sqrt{d_k}}\right)V,\qquad
\operatorname{ProbSparse}(Q,K,V)=\operatorname{Attn}(Q,K)V.
\]

Multihead 版本把各 head 的结果 concatenate 后乘可学习矩阵 \(W_o\)。直觉是不同 head 可关注不同时间尺度，ProbSparse 只计算信息量高的 query，从而避免 full attention 的全部两两配对。[pdf:E05]（PDF 物理页 5，Eqs. (4)–(7)）

第三步把 Informer 的 Conv1d distilling 换成 dilated causal convolution：

\[
F(s)=(X *_d F)(s)=\sum_{i=0}^{K-1}F_i * X_{s-d\,i}.
\]

\(K\) 是 kernel size，\(d\) 是 dilation factor。第 \(i\) 个 kernel tap 读取 \(s-di\) 的历史点；堆叠后 receptive field 指数式扩大，而只在时间前侧 padding 保持 causality。论文实例中 dilated convolution kernel 为 3，随后用 kernel 3、stride 2 的 max-pooling 把序列下采样一半。[pdf:E06]（PDF 物理页 6，Eq. (9) 与 Fig. 7）

第四步用 ReGLU \(y=Ux\odot\max(Vx,0)\) 引入乘性 gating，再以

\[
\mathrm{MSE}=\frac1N\sum_{i=1}^{N}(y_t^i-\hat y_t^i)^2,\qquad
\mathrm{MAE}=\frac1N\sum_{i=1}^{N}|y_t^i-\hat y_t^i|
\]

评价输出。[pdf:E06]（PDF 物理页 6，Eq. (10)）[pdf:E08]（PDF 物理页 8，Eq. (12)）

有三处数学边界。其一，论文把 Eq. (11) 中的 \(\sigma\) 在正文称为 variance，但公式形态通常用 standard deviation，定义存在歧义。[pdf:E07]（PDF 物理页 7，Eq. (11) 相邻正文）其二，Eq. (10) 写 \(U,V\)，紧随其后的文字却称 \(W,V\) 且提到公式未出现的 bias，属于记号不一致。[pdf:E06]（PDF 物理页 6，Eq. (10)）其三，复杂度表给出 Effinformer 每层 \(O(L\log L)\)，但论文没有把 dilated convolution、pooling、decoder 和输出长度合并成端到端 inference latency，更没有给出 FPGA 可实现的 cycle-level bound。[pdf:E03]（PDF 物理页 3，Table I）

## § 7 — 实验设计与结论

- **改动本身是否有效？** 问题是 dilated distilling、sparse decoder 和 GLU 各自是否优于原 Informer。实验分别构造 Effinformer_I/II/III。dilated distilling 相对原 Conv1d 把 MSE、MAE 分别降低 26.2% 和 12.5%；decoder 变体达到 MSE 0.0610、MAE 0.1089、549.5 s/epoch；ReGLU 变体为 0.0722、0.1187、567.9 s/epoch。答案是三处改动在同一实验设置下都带来误差收益，但并非每项都降低训练时间。[pdf:E08]（PDF 物理页 8，Table IV、Fig. 12 与 Section V-A）
- **整体模型是否优于 baseline？** 实验比较 LSTM、WCNN、Informer、Transformer、Autoformer、Reformer、polytopic model。Effinformer 的平均 MSE/MAE 为 0.0552/0.0872，539.6 s/epoch；Transformer 为 0.0658/0.0902、687.9 s/epoch；最快的 Reformer 为 519.5 s/epoch但误差为 0.4101/0.4089。答案是在该数据集上 Effinformer 的误差最低、训练时间接近最快组，但“高速度”证据是每 epoch 训练时间，不是实时 inference latency。[pdf:E09]（PDF 物理页 9，Table V）
- **能否重建稳态和瞬态？** 稳态实验在 \(V_{\mathrm{in}}=105\) V、\(P_{\mathrm{Load}}=526.3\) W 下比较纹波；瞬态实验在 \(V_{\mathrm{in}}=100\) V 时把负载功率从 339 W 改到 107.5 W。Fig. 13 显示 Effinformer 输出电压和输入电流更贴近实测纹波，Fig. 14 显示其能跟随电压 overshoot。答案是该原型和工况下的波形拟合优于所列方法，但图中没有报告 overshoot 百分比、settling-time error 或频域纹波误差。[pdf:E09]（PDF 物理页 9，Figs. 13–14 与 Section V-B）
- **是否稳健且可扩展？** 作者在同一数据集的 unseen test set 上画 measured-estimated scatter，并做长预测。短预测实验来自 500 次采集、730000 个样本，约按 7:2:1 划分，设备为 1.5 kW DAB，采样 100 kS/s；Table II 给出开关频率 20 kHz、额定功率 1.5 kW、目标输出 100 V、负载 6–300 \(\Omega\)。[pdf:E07]（PDF 物理页 7，Table II 与 Section IV-A）长预测固定 seq_len 96、label_len 48，pred_len 取 96、192、336、720、1440。Effinformer 在 96/192/336 的 MSE、MAE 都是表中最佳；到 720 时 Reformer 的 MSE 更低，到 1440 时 Informer 的 MAE 更低。答案是中等预测长度表现强，但“全长都最优”不成立。[pdf:E10]（PDF 物理页 10，Section VI）[pdf:E11]（PDF 物理页 11，Table VI 与 Fig. 17）

不得外推的范围包括：训练/验证/测试是否按完整 experiment 分组未报告；输入电压、负载、温度和器件老化的完整覆盖边界未报告；没有第二台硬件、其他拓扑、闭环控制交互、EMT 联立求解、真实 outlier injection 或 FPGA 实时验证。作者自己还承认，强调 trend 会降低 periodicity feature 的预测能力，长预测会相对实测滞后，原因被归于数据中的 perturbation feature 不足。[pdf:E11]（PDF 物理页 11，Section VI）

## § 8 — Take-aways

**5 句话：**  
1. Effinformer 把 DAB 端口建模重写为两个输入到两个输出的 multivariate time-series regression。  
2. 它以 Informer 为骨架，用 dilated causal convolution 扩大只读过去的 receptive field。  
3. Decoder 继续使用 ProbSparse attention，以优先建模 trend 而不是平均对待全部纹波点。  
4. 在一台 1.5 kW DAB 的 730000 样本数据上，它取得最低短期 MSE/MAE，并能跟随一次负载突变的 overshoot。[pdf:E07]（PDF 物理页 7，实验平台与数据集）[pdf:E09]（PDF 物理页 9，Table V 与 Figs. 13–14）  
5. 但它没有证明跨设备、跨老化状态、与 EMT solver 联立或 FPGA 实时执行，长预测还显示 trend/periodicity tradeoff。[pdf:E11]（PDF 物理页 11，Table VI 与讨论）

**3 句话：** Effinformer 的真正变化不是“更大的 Transformer”，而是用 sparse attention 选少量关键历史、用 dilated causal convolution 保留更长的因果局部信息。它在论文单台 DAB 数据上同时提高了短期误差表现和多输出并行能力。它仍是经验 surrogate，工程可复用性取决于数据分布覆盖，不能当成已验证的可组合实时模型。

**1 句话：** 这篇论文证明了“稀疏长依赖 + 因果多尺度局部特征”能在一个 DAB 数据集上形成强端口预测器，但尚未证明它在分布外工况、EMT 联立和 FPGA 时序约束下仍可信。

## § 9 — 最脆弱的假设

最脆弱的假设是：训练数据覆盖了部署时决定端口响应的全部隐藏状态，因此有限历史窗口 \(X_t\) 足以定义稳定、可迁移的映射 \(F(X_t;\theta)\)。一旦器件温度、磁性饱和、死区、老化、控制律、探头偏置或负载谱改变，使相同端口历史对应不同内部状态，模型就可能给出低训练误差但错误的下一步响应；对 EMT 联立而言，这种错误还会反馈到网络电压、电流，代价比离线 forecast 的单步误差更高。

论文提供的证据是：同一 1.5 kW 原型、同一采集系统的约 7:2:1 test set 上，scatter 接近 \(y=x\)，且在同一数据集上延长 pred_len 后仍有竞争力。[pdf:E10]（PDF 物理页 10，Fig. 15 与 Section VI）缺少的关键证据是 run-wise split 说明、未见工况整段留出、跨设备/温度/老化验证和 prediction interval。更重要的是，作者把“同一数据集的 unseen samples”进一步解释为可扩展到 inverter、filter、power supply；这是基于证据的外推，不是论文实验直接证明。[pdf:E10]（PDF 物理页 10，Section V-C）

## § 10 — 最小复现实验

一周内最值得复现的不是完整长预测，而是检验“结构收益是否在无相邻样本泄漏的整段留出下仍存在”。

1. 使用论文给出的 PyTorch 代码入口；论文提供代码地址，但没有在正文确认公开数据是否包含在仓库中。若拿不到作者数据，就用一台可采集端口四量的 DAB，做至少 30 个独立 load-step runs；每个 run 保存原始 100 kS/s 波形，随后固定 moving-average 与 downsampling 参数。[pdf:E07]（PDF 物理页 7，代码地址、Fig. 11 与采集设备）
2. 只实现 Informer 与 Effinformer 两个模型，固定 batch 32、3-layer encoder、2-layer decoder、8 heads、seq_len 12、pred_len 1；所有归一化统计只从训练 runs 计算。[pdf:E08]（PDF 物理页 8，Table III）
3. 按完整 run 划分训练、验证、测试，测试集至少包含训练未出现的两个 load-step 幅度；训练 10 次，记录 \(v_o,i_{\mathrm{in}}\) 的 MSE、MAE、overshoot error、settling-time error 和单 batch inference latency。
4. **支持核心 claim 的标准：** 在两个输出和留出工况上，Effinformer 相对 Informer 的 MSE 都至少下降 20%，overshoot error 不恶化，且 inference latency 不超过 Informer 的 1.2 倍。
5. **反驳标准：** 优势只在 sample-wise random split 出现、run-wise split 后消失；或平均 MSE 降低但 overshoot/settling error 显著恶化。后者说明模型只是把周期纹波或均值拟合得更好，并未更可靠地捕获动态。

这个实验不需要复现所有 baseline，也不需要 FPGA；它直接检验论文最核心的结构 claim 与第 9 节的数据覆盖假设。

## § 11 — 最强反例设计

最强反例是构造“局部波形看起来熟悉，但隐藏物理状态已变化”的 leave-one-regime-out 测试。训练集仍覆盖论文的电压和负载数值范围，却只在一种器件温度与一种 dead-time 下采集；测试时把磁性元件升温、改变 dead-time，或换成同额定值但寄生参数不同的第二台 DAB，再施加训练中已有幅度的 load step。这样输入窗口的 \(v_{\mathrm{in}},i_o\) 可以落在训练分布的数值包络内，内部损耗和瞬态极点却不同。

比较 Effinformer、Informer 与一个只用少量可测参数校正的物理/gray-box baseline；按完整 run 留出，测量输出电压 overshoot、settling time、输入电流峰值和 rollout 稳定性。若 Effinformer 在原设备 random split 上仍有 Table V 的误差优势，却在第二温度或第二设备上系统性低估峰值，且 confidence 无法提示失效，就出现了对论文最有力的替代解释：收益主要来自同一设备相邻波形的统计插值，而不是学到了可迁移的 converter dynamics。论文现有实验没有排除该解释，因为所有短期与长期结果都来自同一数据集，且作者明确报告了长预测滞后与 perturbation feature 不足。[pdf:E11]（PDF 物理页 11，Fig. 17 与 Section VI）

## § 12 — Follow-up Research Idea

**候选想法：带可证伪可信域的被动端口残差模型。** 这不是在 Effinformer 后面再加一个 attention block，而是把目标从“最小化离线波形预测误差”改成“产生可被 EMT 网络安全组合的离散时间端口算子”：保留一个低阶可解释的能量/端口骨架，让网络只学习未建模残差；同时输出分布外分数，并在可信域外回退或拒绝预测。由于本卡没有独立检索相关工作，这只是候选方向，不声称 novelty。

（a）驱动需求是：论文模型在单设备数据上准确，却没有守恒、passivity、跨设备或 rollout 稳定性保证，也没有 FPGA timing 证据；EMT 中一个端口 surrogate 必须在网络反馈下仍可组合。  
（b）潜在研究价值在于把评价标准从单步 MSE/MAE 提升为“端口误差 + 能量一致性 + 分布外失效可见性 + 实时预算”，这更接近电力电子权威期刊重视的工程可实现性和系统价值。  
（c）可借鉴相邻领域的 port-Hamiltonian/passivity-based modeling、set-membership system identification、conformal uncertainty 与 hardware-aware quantization；这些路线是否已有同类组合需要后续全文检索。  
（d）第一个证伪实验是：在第二台 DAB 和两个温度下训练/测试交换，把 learned port model 接入一个包含源阻抗和负载跃变的离散 EMT 回路；若它不能在未知工况下同时满足峰值误差阈值、离散能量不增约束和固定 inference deadline，则该想法失败。  
（e）它与本文的实质区别是：Effinformer 把端口建模当作同分布 time-series forecasting，并在结论中把应用扩展到 RUL、负荷趋势等预测任务；候选方向把“可组合、可拒绝、可实时”本身设为学习目标。[pdf:E12]（PDF 物理页 12，Conclusion 与未来工作）

