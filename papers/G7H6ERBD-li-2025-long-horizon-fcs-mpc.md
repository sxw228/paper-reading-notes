# Long-Horizon FCS-MPC Trained 1-D Convolution Neural Networks for FPGA-Based Power-Electronic Converter Control With a Si/SiC Hybrid Converter Case Study

- 作者：Ning Li, Hao Yu, Stephen Finney, Paul D. Judge
- 出处：IEEE Transactions on Industrial Electronics, Vol. 72, No. 9
- 年份：2025
- DOI：10.1109/TIE.2025.3536555
- Zotero key：G7H6ERBD

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的实时控制矛盾：FCS-MPC（finite-control-set model predictive control，有限控制集模型预测控制）把开关状态直接作为离散决策，预测时域越长，通常越有机会在电流质量、开关动作和约束之间作出更好的跨步权衡；但若变流器有 \(n_u\) 个开关状态、预测长度为 \(N_p\)，候选序列数量按 \(n_u^{N_p}\) 增长。长时域因此很快同时撞上运算延迟和 FPGA 资源上限。[pdf:E01] 论文的问题不是“神经网络能否控制变流器”这一宽泛命题，而是：能否让离线长时域 FCS-MPC 充当教师，把昂贵的序列搜索压缩成固定结构的 1-D CNN 在线推理，并在 FPGA 上保住有用的闭环性能？

工程价值来自计算发生位置的改变。传统控制器必须在每个采样周期内完成搜索；本文则允许离线教师不受实时预算约束，把教师选出的六路门极状态变成监督标签，在线只执行一个固定深度网络。若这一替代成立，在线延迟与资源就不再随 \(N_p\) 指数增长，而主要由网络结构决定。论文选择的 PHC（parallel hybrid converter，并联混合变流器）不是最简单的两电平示例：它由低频 Si IGBT 三相桥与部分额定高频 SiC MOSFET 三相桥并联，共有 64 个联合开关状态，还要处理公共直流母线引起的共模环流、SiC 支路电流约束和电流相关开关惩罚。[pdf:E02]

需要先限定论文实际证明的范围。控制器在 OPAL-RT 双机 rapid-control-prototyping 环境中验证：OP4200 承担 FPGA 实时电路仿真，OP4510 的 Kintex-7 FPGA 承担控制器；这是真实独立实时控制器对实时仿真对象的闭环，而不是在有功率器件、传感器非理想和保护链的物理样机上验证。[pdf:E06]

## § 2 — 前人工作与不足

论文给出的第一条既有路线是直接加速 FCS-MPC。sphere decoding algorithm（SDA）可把特定长时域代价函数改写为 integer least-squares 问题，prediction-window 优化、约束化 SDA 和 FPGA 并行搜索也都能降低延迟；但长时域仍面对庞大的搜索空间，而且不是所有复杂代价函数都容易整理成 ILS-SDA 形式。[pdf:E01] 本文的 PHC 代价函数同时含跟踪误差、开关变化、与低频桥电流幅值相关的开关惩罚以及高频桥电流软约束，正是作者用来强调这种表达限制的案例。[pdf:E04]

第二条路线是用离线 MPC 数据训练 MLP。论文引用的已有工作已经把 ANN 用于 boost、NPC、cascaded H-bridge、triple-active-bridge 和 flying-capacitor converter 等任务，因此“用网络模仿 MPC 开关决策”本身不是本文首次提出。[pdf:E02] 作者指出的缺口更窄：dense MLP 参数连接刚性较强，不会显式复用输入中局部信号关系；对包含测量量、参考量和上一拍门极状态的结构化输入，这可能意味着更多参数和较差的闭环表现。对 PHC 这类比二、三电平单桥更复杂的拓扑，既有 learning-based controller 的 FPGA 资源、实时性能及泛化也仍需验证。[pdf:E02]

最直接的 benchmark 是文献 [11] 的 MLP：同样把 15 维输入升到 36 维，再扩展到 72 维、压到 32 维，最后输出 6 个 Sigmoid 概率。本文不是拿 CNN 与一个明显弱小的线性模型比较，而是在相同输入输出任务上比较 dense MLP、原始 CNN、压缩 CNN，并保留可实时实现的 \(N_p=1,2\) FCS-MPC 作为控制基线。[pdf:E05]

## § 3 — 重建作者的思考路径

可以从论文出现之前已经存在的事实重建如下路径。

1. 多步 FCS-MPC 能利用未来若干步的代价信息，但 64 状态 PHC 的搜索树随 \(N_p\) 急剧扩张。DFS 可以用当前最小代价剪枝，FPGA 可以并行展开分支，可这两种办法仍把最坏负担留在每个实时采样周期内。[pdf:E01][pdf:E04]
2. 如果最昂贵的长时域 FCS-MPC 只在离线运行，就可以生成“当前测量/参考/上一门极状态 → 最优下一门极状态”的大规模样本。在线问题于是从组合优化变成固定大小的多标签分类，计算量不再直接取决于教师的时域长度。[pdf:E04]
3. 既然输入不是任意 15 个无关标量，而包含 \(I_G,I_{HF},V_G,I_G^\*,I_{HF}^\*,G_{LF}^i,G_{HF}^i\) 等有物理关联的信号组，那么共享卷积核可能比全连接层更节省参数，并提取电流—电压、参考—测量及两桥互补门极状态的局部关系。[pdf:E04]
4. 即使 CNN 小于 MLP，直接以 32-bit 实现仍可能消耗较多 DSP。因此还需要 pruning、fine-tuning 和较低位宽，把模型压到较便宜的 FPGA 上，同时用闭环波形而不只是分类 accuracy 判断压缩是否破坏控制。[pdf:E06]

这条思路真正改变的是实时求解方式，而不是 PHC 的物理模型或 FCS-MPC 教师目标。网络继承教师数据覆盖到的行为，却不继承在线优化的显式代价比较、状态约束推理或稳定性论证。

## § 4 — 核心 Intuition

先让不受实时预算限制的长时域 FCS-MPC 离线回答“此刻应该施加哪组门极信号”，再让一个小型 1-D CNN 学习这一映射，便可把在线组合搜索换成固定成本的前向传播。卷积的局部连接和权重共享试图用更少参数抓住测量、参考与上一拍门极状态之间的局部关联；剪枝和降位宽则把这种结构优势进一步兑现为 FPGA 资源节省。[pdf:E04][pdf:E06] 代价是在线控制器从“每拍重新优化”变成“相信训练分布中的近似策略”。

## § 5 — 具体方法与完整 Pipeline

以 \(N_p=4\) 的 PHC 控制器为例，完整 pipeline 如下。

1. **构造教师。** PHC 的状态空间模型以网侧电流、SiC 高频桥电流和共模方向电流等为状态，以两个三相桥的六个桥臂电压为控制输入。算例额定容量 16.9 kVA、直流电压 300 V、线电压 172.5 V，控制采样率 100 kHz；代价权重和 22 A 高频桥电流界值列在 Table I。[pdf:E03]
2. **离线搜索标签。** 长时域 FCS-MPC/DFS 沿所有可行开关路径推进状态模型，累计跟踪、开关和软约束代价，剪掉累计代价已经不小于当前最优值的分支，并把最优序列的第一拍六路门极状态作为标签。[pdf:E04]
3. **生成并预处理数据。** 作者分别为 \(N_p=\{1,2,3,4\}\) 生成四个 200,000 样本数据集，瞬态与稳态样本约为 1:3，按 8:1:1 划分训练/验证/测试集；输入按训练集各通道均值和标准差归一化，并加入 Gaussian white noise。[pdf:E05]
4. **执行 CNN。** 15 维输入先经 FC+ReLU 映射为 36 维；随后一层 1-D convolution 使用 4 个输出 channel、kernel size 3，再接 BN、ReLU 和 max pooling；两层 FC 依次得到 32 维和 6 维，末端 Sigmoid 给出六个二值门极标签。[pdf:E04]
5. **训练。** 任务按 multilabel binary classification 训练。作者使用 Adam、batch size 256、100 epochs，cosine annealing 把 learning rate 从 \(10^{-3}\) 降至 \(10^{-5}\)，weight decay 为 \(10^{-5}\)，固定随机种子 114514；软件环境为 PyTorch 2.1.1/Python 3.9，训练机为 RTX 4080 与 i9-13980HX。[pdf:E05]
6. **压缩。** 对 convolution 和 FC 权重做 20% L1 unstructured pruning，以 \(10^{-4}\) learning rate fine-tune，再把训练参数从 float32 量化为 float16。[pdf:E06]
7. **映射到 FPGA。** CNN 与 MLP 先以 C++ 重写，再由 Xilinx Vitis HLS 生成 HDL。未压缩 CNN/MLP 用 32-bit fixed-point；压缩 CNN 最终用 20-bit fixed-point。作者报告 16-bit 尝试在测试中发生 data overflow，因此没有把它当成功结果。[pdf:E06]
8. **实时闭环。** OP4200 运行 PHC 实时电路模型，模拟量送入 OP4510；OP4510 上的 Kintex-7 XC7K410T 执行学习控制器并返回门极信号，100 kHz 记录数据。FPGA resource 和 execution time 由 Vitis HLS synthesis/cosimulation 评估，闭环 THD 与波形由 rapid-control-prototyping 平台记录。[pdf:E06][pdf:E07]

这里没有事件驱动的可变步长，也没有多速率控制：论文报告的是固定 100 kHz 控制步长。数值实现只报告 32-bit 与 20-bit fixed-point，未报告各层整数位/小数位分配、saturation/rounding 规则或最坏情况定点误差界；这些属于复现时必须补齐、但不能从论文推断的细节。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有给出新稳定性定理；数学的作用是定义教师、监督学习目标和预处理。

首先，PHC 教师由连续状态空间模型描述：

\[
\dot{x}_{\alpha\beta\gamma}
=A_{\alpha\beta\gamma}x_{\alpha\beta\gamma}
+B_{\alpha\beta\gamma}u_{\alpha\beta\gamma}
+E_{\alpha\beta\gamma}v_{\alpha\beta\gamma},\qquad
y_{\alpha\beta\gamma}
=C_{\alpha\beta\gamma}x_{\alpha\beta\gamma}
+D_{\alpha\beta\gamma}u_{\alpha\beta\gamma}.
\]

文中令 \(C\) 为单位矩阵、\(D\) 为零矩阵，并在 Eq. (3)–(5) 展开 PHC 的 \(A,B,E\)；工程上它们把两桥电感、电阻、网侧电压和共模支路耦合成下一状态预测。[pdf:E03] 这组方程是离线教师的预测模型，并未嵌入 CNN 在线推理。

教师在 \(N_p\) 步上最小化 Eq. (6)：

\[
J=\sum_{l=k}^{k+N_p-1}
\left(
\lVert y^\*(l+1)-y(l+1)\rVert_{Q_{\rm quad}}^2
+\lVert\Delta u(l)\rVert_{Q_{\rm sw}}^2
+|i_{LFx}|\,\lVert\Delta u(l)\rVert_{Q_{\rm Cur}}^2
+J_{CL}
\right),
\]

\[
J_{CL}=\sum_{l=k}^{k+N_p-1}
\begin{cases}
Q_{CL},& |i_{HFx}(l+1)|\ge i_{\rm bnd},\\
0,& |i_{HFx}(l+1)|<i_{\rm bnd}.
\end{cases}
\]

第一项惩罚预测输出偏离参考；第二项抑制开关变化；第三项让低频桥电流越大时切换代价越高；第四项在高频桥电流越界时加入固定软惩罚。它是 soft constraint，不是把危险开关序列从可行集硬删除，因此即使教师也不保证绝不越界。[pdf:E04]

CNN 的六路输出用 binary cross-entropy 加 \(L_2\) regularization 训练。对样本 \(s\)、门极标签 \(t\)，Eq. (11) 可写为：

\[
\mathcal L_{\rm loss}
=-\frac{1}{N}\sum_{s=1}^{N}\sum_{t=1}^{C}
\left[G^o_{st}\log f_{st}+(1-G^o_{st})\log(1-f_{st})\right]
+\lambda\lVert\theta\rVert^2,\qquad C=6.
\]

这里 \(G^o_{st}\) 是 FCS-MPC 教师标签，\(f_{st}\) 是 CNN 给出的门极概率，\(\theta=\{W,b\}\)。训练最小化的是逐 bit 标签误差，而不是直接最小化闭环 THD、约束违反或稳定性风险，这是后续批评的关键。[pdf:E05]

输入按 Eq. (12) 归一化：

\[
Z'_i=\frac{Z_i-\mu}{\sigma},
\]

其中 \(\mu,\sigma\) 来自训练集各通道。[pdf:E05] 这也意味着部署必须使用完全相同的统计量；论文没有讨论统计漂移或传感器标定变化对控制安全性的影响。

## § 7 — 实验设计与结论

**问题 1：CNN 是否比 MLP 更小，同时保持相近的离线分类能力？ →** 作者在相同四个 horizon 数据集上比较 exact match 和两桥 subsequence accuracy，并统计 CPU 模型的参数/FLOPs。**→ 答案：** CNN 为 3,134 parameters、4,188 FLOPs，MLP 为 5,774 parameters、5,628 FLOPs，即论文报告分别减少 45.6% 和 25.6%；Fig. 6 显示二者分类 accuracy 接近。[pdf:E06] 这支持“结构更小”，但不能单独支持闭环更安全。

**问题 2：资源与时延是否摆脱 horizon 增长？ →** 作者对 16-bit、64-thread FCS-MPC 以及三种 ANN 做 Vitis HLS synthesis/cosimulation。**→ 答案：** \(N_p=2\) FCS-MPC 用 452 DSP、164,765 LUT、7,020 ns；\(N_p=3\) 和 4 分别需要 124% 和 226% LUT，执行时间 33,670 ns 和 202,540 ns，不能满足当前器件/100 kHz 步长。MLP、CNN、compressed CNN 的结构不随教师 horizon 改变；对应时延分别为 2,060、3,320、2,990 ns。[pdf:E07] 因而“在线成本不随 \(N_p\) 增长”在这些固定网络综合结果中成立，但不是对任意 horizon 或网络容量的理论保证。

**问题 3：压缩是否真正省下 FPGA 资源？ →** 对 32-bit CNN 做 20% pruning、fine-tuning 和 20-bit fixed-point 实现，再比较 Table III。**→ 答案：** compressed CNN 用 123 DSP、22,388 FF、50,536 LUT、0 BRAM；32-bit CNN 用 353 DSP、39,594 FF、58,054 LUT、30 BRAM；32-bit MLP 用 483 DSP、25,694 FF、84,618 LUT、30 BRAM。[pdf:E07] 123 相对 483 的 DSP 降幅约 74.5%，与作者“约 75%”的结论相符。相对 32-bit CNN，DSP 显著下降，但 LUT 只从 22% 降到 20%；“所有资源均减少 75%”并不成立。

**问题 4：实时闭环质量是否优于 MLP，并保留长 horizon 的收益？ →** 在 OPAL-RT 平台比较 \(N_p=1\ldots4\) 教师训练出的 MLP/CNN/compressed CNN，并只在可实现的 \(N_p=1,2\) 比较在线 FCS-MPC。**→ 答案：** Table IV 中，FCS-MPC 的 THD 为 5.01%/3.52%（\(N_p=1/2\)）；MLP 为 6.41%/6.21%/5.84%/4.82%；CNN 为 5.97%/4.49%/3.77%/3.14%；compressed CNN 为 6.91%/4.64%/3.79%/3.29%。[pdf:E08] 因此短 horizon 下 FCS-MPC 更好；到 \(N_p=4\)，CNN 比 MLP 好 1.68 个百分点，压缩只使 CNN 增加 0.15 个百分点，但此处没有可实时实现的 \(N_p=4\) FCS-MPC 直接基线。

**问题 5：CNN 是否更好地处理 SiC 支路电流约束？ →** 作者比较 \(N_p=4\) 波形与最大 SiC 电流。**→ 答案：** 报告最大值为 CNN 32.41 A、compressed CNN 35.07 A、MLP 41.56 A，说明 CNN 相对 MLP 越界较小。[pdf:E08] 但 Table I 的 current limit 是 22 A，[pdf:E03] 三者最大值都高于该值；据此只能说“约束违反程度较小”，不能说“始终满足 22 A 限值”。这也暴露了正文/结论中“tightly constraining within the defined current limit”表述与报告最大值之间的张力。

**问题 6：训练外扰动下是否仍能运行？ →** 作者给 compressed CNN 注入训练集中没有的五次/七次电压谐波，并施加三相对称电压跌落 \(1\to0.2\to1\) pu。**→ 答案：** Fig. 12–13 的实时波形未出现论文所称的重大电流扰动，作者据此主张有一定 robustness/generalization。[pdf:E09] 但实验没有给稳定裕度、约束违反积分、恢复时间置信区间或大量随机工况，因此证据只能支持这两个脚本化扰动，不应外推为一般 OOD 安全性。

## § 8 — Take-aways

**5 句话：** ① 论文把长时域 FCS-MPC 从在线组合搜索改成离线教师，把在线控制变为固定结构的六标签 CNN 推理。[pdf:E04] ② 15→36→单层 1-D convolution→32→6 的网络比选定 MLP 少 45.6% 参数和 25.6% FLOPs。[pdf:E06] ③ 20% pruning 与 20-bit fixed-point 把 DSP 降到 123 个，约为 32-bit MLP 的四分之一，同时 \(N_p=4\) THD 仅从 3.14% 增至 3.29%。[pdf:E07][pdf:E08] ④ 优势出现在 FCS-MPC 的 \(N_p=3,4\) 已无法在该 XC7K410T/100 kHz 配置实时实现的区域；在 \(N_p=1,2\) 上，直接 FCS-MPC 的 THD 仍更低。[pdf:E07][pdf:E08] ⑤ 论文证明的是一个 PHC 实时仿真闭环上的工程可行性，不是端到端学习控制器的稳定性、硬约束满足或跨拓扑泛化。

**3 句话：** 长 horizon 的“计算知识”可以离线蒸馏进一个固定成本 CNN，从而换取 FPGA 可实现性。卷积与压缩在该 PHC 上同时改善了资源和相对 MLP 的 THD，但 22 A 约束仍被报告最大电流超过。[pdf:E03][pdf:E08] 真正未解决的是训练分布外的闭环安全，而不是再挤出几个百分点的分类 accuracy。

**1 句话：** 这是一项有说服力的 FPGA resource/latency 与 PHC 实时闭环 case study，但它把长时域搜索风险换成了尚未认证的数据覆盖与稳定性风险。

## § 9 — 最脆弱的假设

最脆弱的假设是：**离线 FCS-MPC 标签上的高分类一致性，足以让定点 CNN 在所有重要闭环状态中复现教师的性能与安全行为。**

这个假设一旦失效，论文的主要工程价值会一起失效。控制系统的数据分布不是固定的：网络某一次选错门极会改变下一拍状态，下一拍输入便可能离开训练分布，随后形成 compounding error；元件参数漂移、传感器偏置、死区、延迟和未覆盖的故障也会把相同“局部信号模式”对应到不同的安全动作。论文的 BCE 又把六个 bit 的每次错误近似等价对待，不知道某个误判是否正好发生在电流约束边界。[pdf:E05]

论文给出的正面证据包括四个各 200,000 样本的数据集、瞬态样本、Gaussian noise、不同训练配置敏感性、两种训练外扰动，以及 OPAL-RT 实时闭环。[pdf:E05][pdf:E09] 缺失的却正是能封闭这个假设的证据：没有闭环稳定性证明，没有硬约束 shield，没有系统性的参数/延迟/噪声 sweep，也没有物理功率级。更直接的是，报告的 \(N_p=4\) 最大 SiC 电流 32.41–41.56 A 均高于 Table I 的 22 A current limit，[pdf:E03][pdf:E08] 表明“相对更小的越界”不能替代“约束已满足”。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 OPAL-RT，而是“20-bit compressed CNN 是否在闭环中保留 32-bit CNN 的性能，同时达到论文所报 FPGA 预算”。

1. 使用论文公开的 training data、C++ CNN 和 Vivado/Vitis project；论文明确给出了相应代码与数据仓库。[pdf:E10]
2. 先复现 \(N_p=4\) 的 32-bit CNN 与 20-bit compressed CNN，在同一 PHC software-in-the-loop 闭环、100 kHz 步长和 Table I 参数上运行。测试稳态、参考阶跃、五/七次谐波和 \(1\to0.2\to1\) pu 电压跌落，并额外加入 \(\pm10\%\) 电感/电阻偏差。
3. 每个工况记录 grid-current THD、最大与累计 SiC 电流越界、门极切换频率、闭环发散/limit cycle，以及 32-bit 与 20-bit 的逐拍门极分歧。不要只复现 test-set accuracy。
4. 对 XC7K410T-1FBG900 重新执行 HLS synthesis/cosimulation，核对 DSP/LUT/FF/BRAM 和 worst-case latency；特别确认定点 rounding、saturation 与各层小数位。
5. **支持标准：** compressed CNN 在所有名义工况相对 32-bit CNN 的 THD 劣化不超过论文的 0.15 个百分点量级、没有新增持续振荡，且综合结果接近 123 DSP、50,536 LUT、2,990 ns。[pdf:E07][pdf:E08] **反驳标准：** 任一 OOD 参数偏差导致持续越界/发散，或真实综合后的位宽与 latency 无法满足 10 μs 周期，即足以否定“压缩后仍保留可用闭环性能”这一核心工程 claim。

这个实验还应把 22 A 作为明确安全阈值报告；若复现实验同样出现 30 A 以上峰值，应把结果解释为“相对 MLP 改善但未满足约束”，而不是照抄结论措辞。

## § 11 — 最强反例设计

最强反例是构造一个**分类 accuracy 仍高、但少数关键误判触发闭环约束失效**的状态序列。具体做法是让 PHC 在高负载、SiC 电流接近 22 A 边界时，同时经历网压相位跳变、0.2 pu 电压跌落、参考电流阶跃和电感偏差；再加入一拍测量/执行延迟，使网络输入仍大多落在常见数值范围内，却改变“当前门极选择对下一拍电流”的真实后果。

对每个时刻同时运行三条控制轨迹：在线 \(N_p=2\) FCS-MPC、32-bit CNN、20-bit compressed CNN。用相同初态和扰动，比较累计代价、最大/持续越界、恢复时间和是否形成 subharmonic/limit cycle。反例成立的判据不是 CNN 的总体标签 accuracy 下降很多，而是它仍保持很高 accuracy，却在少数约束边界样本连续选错，导致教师轨迹恢复而 CNN 轨迹持续越界或失稳。

这个反例直接攻击“离线 imitation loss 可代理闭环安全”的机制。若 CNN 在该实验中仍稳定、满足 22 A 硬阈值，并且资源/时延优势保留，才会显著加强论文主张；若失败，增加普通训练样本或再调一点 pruning 比例并不能解释掉问题，因为失败来自训练目标与控制风险不对齐。

## § 12 — Follow-up Research Idea

**候选想法：把问题从“端到端模仿最优门极”改成“学习提出候选序列，确定性验证器负责最终施加”。** 这不是在 CNN 后再叠一层普通网络，而是重新定义在线任务：CNN 输出少量高概率开关序列或一个可搜索子树；一个带 PHC 模型的固定时延 verifier 在 FPGA 上逐项检查下一步电流硬约束并比较短时域真实代价，无法认证时切换到安全 fallback。优化目标由平均标签 accuracy 改成“在严格 latency budget 内最大化可认证覆盖率，并对未认证状态拒答”。

**（a）需求。** 论文已显示端到端 CNN 能省资源，但最大 SiC 电流仍超过 22 A，且作者自己把 reliability、interpretability、stability analysis 列为限制。[pdf:E03][pdf:E08][pdf:E09] 因而未满足的需求不是更高平均 accuracy，而是可观测、可拒绝、可证明不会把少数高风险错误直接送到门极。

**（b）研究价值。** 电力电子控制重视确定时延、硬约束、故障行为和真实 FPGA 资源。若学习候选器能把 64-叉长时域树压成很小的认证集合，同时 verifier 给出逐拍安全理由，这会把“资源节省”与“运行时保证”统一到同一硬件闭环指标中。

**（c）相邻工具。** 可以借鉴 runtime assurance、selective prediction/conformal risk control、control barrier function 和 branch-and-bound certificate；但 PHC 是离散开关系统，最终实现应落在可流水化的定点状态预测、硬阈值检查和 bounded candidate evaluation，而不是依赖不可控时延的软件求解器。

**（d）首个证伪实验。** 在与本文相同的 XC7K410T、100 kHz 和 \(N_p=4\) 教师数据上，加入参数漂移、相位跳变、谐波与电压跌落的组合 sweep。若 verifier 为保证安全而在大量正常样本上频繁 fallback，导致 latency 超过 10 μs，或硬约束收益以明显 THD 恶化为代价，则该问题重定义没有实际价值。

**（e）实质区别。** 本文 CNN 直接输出最终六路门极，安全完全依赖训练分布；候选方案只让学习器缩小搜索空间，最终动作仍由显式物理模型和可检查约束决定。相关工作在本卡中未做充分全文检索，因此这只是证据约束下的候选研究方向，不声称 novelty。
