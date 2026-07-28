# Circuit Dynamics Prediction via Graph Neural Network & Graph Framework Integration: Three Phase Inverter Case Study

- 作者：Ahmed K. Khamis；Mohammed Agamy
- 出处：IEEE Open Journal of Power Electronics，Vol. 5，pp. 987–1001
- 年份：2024
- DOI：10.1109/OJPEL.2024.3416195
- Zotero key：64FITWZB

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

### § 1 — 研究问题与重要性

这篇论文研究的不是“让神经网络直接生成三相逆变器的开关波形”，而是一个更具体的 surrogate modeling 问题：能否把功率变换器的拓扑、元件值、寄生参数和控制参数统一编码成 graph，再用同一个 GNN regression 结构预测 line voltage、efficiency 等电路级性能指标。作者选择三相 DC-AC inverter，比较无滤波 R-load 与 LC-filter 两种结构，并在 square-wave modulation、SPWM、单输出与多输出回归之间改变任务。论文摘要把目标概括为：在不同拓扑和参数变化下保持同一模型结构，并报告大多数情形下 \(R^2>99\%\)、MSE 接近 0。[pdf:E01]（PDF 物理页 1，Abstract）

工程价值在于“接口统一”。传统电路仿真器需要每个候选拓扑的 netlist、器件模型和逐步求解；解析模型又常随拓扑、控制方式或近似假设而改写。本文试图把这些变化压到 graph input 中，使预测器的外部接口保持不变。[pdf:E02]（PDF 物理页 2，Section II）如果这一接口真的能跨拓扑、跨工作点、跨器件变化可靠泛化，它可以服务于 design-space screening、在线状态估计或快速预评估。

但“circuit dynamics prediction”这个标题容易让人产生过强理解。论文实际展示的主要输出是 line voltage 与 efficiency 等汇总量；没有展示一个按时间步递推、能重建开关瞬态波形的 state-transition model。[pdf:E08]（PDF 物理页 8，Section V 与 Fig. 9）因此，本卡把已验证贡献限定为“基于图与参数的性能回归”，不把它外推成通用 EMT 瞬态求解器。

### § 2 — 前人工作与不足

论文把既有工作分为几类：graph + reinforcement learning 用于 transistor sizing 或参数优化；GNN 用于 distributed circuit electromagnetic behavior；DeepGEN 用于小规模 analog circuit prediction；GNN 也被用于 analog-layout symmetry constraint extraction。作者认为这些工作已经说明 graph representation 对 circuit design 有用，但尚未闭合“switching converter 的结构与控制变化如何进入同一性能预测模型”这一问题。[pdf:E01]（PDF 物理页 1，Introduction）这里的“尚未闭合”是论文自己的文献判断，不是本卡独立完成的 novelty 检索结论。

更直接的前序工作来自同一作者 2023 年的 homogeneous GNN circuit mapping：它提出 continuous/switching circuits、CCM/DCM 的统一 graph encoding 和 dataset generation，并做了 converter classification。本文复用该 framework，把任务从 classification 推到 regression，并增加 topology/parameter variation、复杂度分析和三相 inverter 实验。[pdf:E02]（PDF 物理页 2，Introduction）从参考文献表可确认该前序论文为 IEEE Open Journal of Circuits and Systems 2023 年文章；论文也引用 GCN、GAT、GraphSAGE、R-GCN 等通用图模型作为方法背景。[pdf:E15]（PDF 物理页 15，References [13]、[32]–[35]）

作者指出的既有方法不足主要有两层。第一，topology-specific transfer-function learning 或固定规模 analog circuit model 很难自然吸收开关、控制模式和连接关系变化。第二，simulation/analytical model 在大规模或高维问题上可能昂贵，并可能依赖不完全成立的简化假设；ML surrogate 可以在训练后降低重复查询成本。[pdf:E02]（PDF 物理页 2，Section II）需要注意：本文没有用相同硬件、相同误差目标对 LTspice 与 GNN 做 wall-clock benchmark，所以“更快”仍是动机与作者主张，不是本文实验已经量化的结论。

### § 3 — 重建作者的思考路径

以下是基于论文材料重建的研究路径，不是作者逐字陈述。

第一步，先把 switching converter 看成“结构 + 属性”的对象，而不是只看成固定长度参数向量。Bond graph 已经提供 0-junction、1-junction、元件节点和 power bond，可保留串并联、能量交换与跨物理域语义。对 switching cell，再用 switched 0/1 junction、零值电流源与控制变量 \(D\) 表达导通路径和关断时的电流中断。[pdf:E03]（PDF 物理页 3，Fig. 2–3）[pdf:E04]（PDF 物理页 4，Section III-A）

第二步，把 bond graph 变成 GNN 能消费的 homogeneous graph。节点的 categorical type 用 one-hot 表示，再拼接元件值、switch current/voltage、frequency、modulation index、\(R_{ds}\)、\(C_{ds}\) 等 analog features；edge 可以携带 duty cycle，取值 0 到 1。[pdf:E04]（PDF 物理页 4，Section III-D）这使“换器件”“换频率”“换 modulation”“加 LC filter”原则上都变成 graph 或 feature 的变化，而不是重新设计网络接口。

第三步，选择 permutation-invariant 的 message passing。GCN 参数数量不依赖 graph node count，global mean readout 又把变长 node set 压成固定维度 graph vector，因此同一回归头可以接收不同规模的图。[pdf:E07]（PDF 物理页 7，Section IV-B 与 Fig. 8）

第四步，在一个可控案例上逐级增加难度：先做无滤波三相 inverter 的单变量回归，再加入 LC filter、寄生参数、SPWM 和多输出，最后用实物 R-load inverter 的测量点检查 simulation-trained relation 是否仍能解释真实效率变化。[pdf:E11]（PDF 物理页 11，Sections V-B、VI）[pdf:E14]（PDF 物理页 14，Section VII）

### § 4 — 核心 Intuition

核心 intuition 是：converter topology 决定“谁与谁交换信息”，元件与控制量决定“交换的信息是什么”；GNN 正好把这两部分分别放进 adjacency/edge 与 node features。只要目标性能主要由这些局部关系经过有限次 message passing 后的全局汇总决定，同一套 GCN + pooling + regression head 就可能处理不同大小的电路图。这里真正改变的假设，是把“每个拓扑需要一套专用方程或模型”改成“拓扑本身就是可学习输入”。[pdf:E06]（PDF 物理页 6，Fig. 5–6）

### § 5 — 具体方法与完整 Pipeline

以三相 two-level inverter 为例，完整 pipeline 如下。

1. **电路到 bond graph。** 三个桥臂的六个开关、DC source、三相 R-load，以及可选的三相 LC filter，被转换为元件节点、0/1 junction 和连接 edge。Fig. 5 同时给出无滤波与 LC-filter 的 circuit/graph 对照，说明加滤波器时增加 \(L\)、\(C\) 节点和连接，但不改变后续 GNN 结构。[pdf:E06]（PDF 物理页 6，Fig. 5）
2. **开关与控制编码。** SPST/SPDT switching cell 由 switched 1-junction/0-junction 表示；关断电流中断用零值 current source \(I_s\) 表示；控制变量 \(D\) 决定连接。节点向量可包含 \(I_{sw}\)、\(V_{ph}\)、\(I_{ph}\)、frequency \(F\)、modulation index \(M\)、\(R_{ds}\)、\(C_{ds}\)，duty cycle 作为 edge feature。[pdf:E03]（PDF 物理页 3，Fig. 2–3）[pdf:E04]（PDF 物理页 4，Section III-D）
3. **统一 feature matrix。** 元件类型用 \([V,I,L,R,C,1,0]\) one-hot 编码，后接 analog values。Eq. (1) 展示单桥臂 12 个节点的矩阵；例如 switch node 带 \(I_{sw},R_{ds},C_{ds}\)，控制相关节点带 \(F,M\)。所有节点向量长度必须一致，但 feature 数量由 designer 决定。[pdf:E05]（PDF 物理页 5，Eq. (1)、Fig. 4）
4. **数据范围。** simulation dataset 的报告范围是 \(R=1\text{–}100\,\Omega\)、\(F=10\,\mathrm{kHz}\text{–}1\,\mathrm{MHz}\)、\(R_{ds}=50\,\mathrm{m}\Omega\text{–}2\,\Omega\)、\(C_{ds}=10\text{–}200\,\mathrm{pF}\)、\(C_f=10\,\mathrm{nF}\)、\(M=0.05\text{–}1\)、\(L_f=50\,\mu\mathrm{H}\)。作者称这些范围参考真实开关和变换器值。[pdf:E05]（PDF 物理页 5，Table 1）
5. **GNN inference。** 输入为 graph \(G\)、node feature matrix \(X\)、adjacency \(A\) 和 edge features \(Z\)。三层 GCN 做 message passing，global mean pooling/readout 得到固定维度 graph embedding，再经两层 fully connected linear layers 输出 \(C\) 个回归量；训练目标是 MSE。[pdf:E06]（PDF 物理页 6，Fig. 6）[pdf:E10]（PDF 物理页 10，Section V-A）
6. **输出。** 案例中的 \(C\) 是一个或两个：line voltage、efficiency。Fig. 9/12 展示 ground truth 与 prediction 的点线关系，以及 \(R_{ds}\)、\(C_{ds}\)、frequency、\(M\) 改变时的输出曲线。[pdf:E08]（PDF 物理页 8，Fig. 9）[pdf:E10]（PDF 物理页 10，Fig. 12）

必须明确三个边界。第一，论文没有给出显式的时间推进：没有 \(x_{t+1}=f(x_t,u_t)\)、event queue、可变步长、多速率或 switching instant 更新。frequency、modulation 和 duty cycle 是输入特征，switch current/voltage 甚至来自 simulation，但网络本身不是逐时间步积分器。[pdf:E04]（PDF 物理页 4，Section III-D）第二，论文没有说明 GNN 训练或 inference 的软件框架、CPU/GPU 型号或实际部署平台；LTspice 是数据生成工具，Fig. 13 中的 controller 与三相 SiC inverter 是测量平台，不能据此推断 GNN 在 controller 上执行。[pdf:E11]（PDF 物理页 11，Fig. 13）第三，论文完全未报告 FPGA、RTL/HLS、fixed-point 位宽、DSP/BRAM/LUT/FF 资源、fmax 或 measured inference latency；因此该软件 GNN 不能直接写成“FPGA 可部署”。

### § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，但它是 network mapping 与复杂度表达，不是 converter differential equation 的推导。

回归关系首先写为

\[
Y=\operatorname{Regression}(X,A,Z),\qquad
X\in\mathbb{R}^{N\times d_{in}},\quad
Y\in\mathbb{R}^{C\times 1}.
\]

其中 \(N\) 是 graph nodes 数，\(d_{in}\) 是每个节点的输入 feature 长度，\(C\) 是预测变量数。GCN 把 \(N\times d_{in}\) 映到 \(N\times d\)，global mean readout 再把变长 node matrix 映到 \(1\times d\)，FC head 输出 \(1\times C\)。[pdf:E08]（PDF 物理页 8，Eq. (2)–(6)）

每层 GCN 的核心更新是

\[
X^{(k+1)}
=\sigma\!\left(
\hat D^{-1/2}\hat A\hat D^{-1/2}X^{(k)}\Theta^{(k)}
\right),
\qquad \hat A=A+I.
\]

\(\hat A\) 加入 self-loop，\(\hat D\) 是其 degree matrix，\(\Theta^{(k)}\) 是第 \(k\) 层共享权重，\(\sigma\) 使用 ReLU。直观上，每个 node 把自身与邻居的 feature 做 degree-normalized aggregation；共享 \(\Theta\) 不随 \(N\) 增长，所以 graph 变大时网络参数数目不必跟着改变。随后 global mean pooling 把全部 node embedding 平均成一个 graph vector，两层 FC 将其变成 line voltage/efficiency。[pdf:E10]（PDF 物理页 10，Eq. (7)–(10) 与正文）

论文还写出两层 FC 与 leaky-ReLU 形式，并用

\[
R^2=1-\frac{\mathrm{RSS}}{\mathrm{TSS}}
=1-\frac{\sum_i(y_i-\hat y_i)^2}
{\sum_i(y_i-\bar y_i)^2}
\]

评价回归拟合。[pdf:E11]（PDF 物理页 11，Eq. (11)–(14)）这解释了 reported \(R^2\)，但 \(R^2\) 高并不自动证明 out-of-distribution topology generalization。

作者给出的 asymptotic expressions 为

\[
T=O\!\left(3(E+NF^2)+(N+128N)+128^2+128^2+128\times2\right),
\]
\[
S=O(N+E+NF+128+128+128+2).
\]

它们描述 graph size 和 feature width 增长时的计算/存储阶数。[pdf:E12]（PDF 物理页 12，Section VI-B）这些式子不是实测 runtime、memory footprint 或 hardware resource report，也没有把 sparse indexing、batching、data movement 和数值位宽计入可部署成本。

### § 7 — 实验设计与结论

**问题 1：同一模型能否拟合无滤波 R-load inverter？** 设计是 square-wave modulation 下扫描 \(V_{in}\)、load \(R\)、frequency \(F\)，做 single-variable regression。答案是 line-voltage percentage error 的均值约 \(0.5735\%\)、标准差约 \(4.89\%\)；Fig. 7 的误差直方图也给出 \(\mu=0.5735,\sigma=4.8958\)。[pdf:E07]（PDF 物理页 7，Fig. 7）[pdf:E12]（PDF 物理页 12，Table 2）

**问题 2：加入 LC filter、寄生参数和 multi-output 后还能否拟合？** 设计逐步增加 LC-filter topology、\(R_{ds}\)、\(C_{ds}\)、SPWM modulation index \(M\)，并同时预测 line voltage 与 efficiency。答案是 simulation case 中，Fig. 9 报告 line voltage \(R^2=0.9993\)、efficiency \(R^2=0.9972\)；LC-filter SPWM case 的 Fig. 11 报告 \(R^2=0.9985\) 与 \(0.9824\)。[pdf:E08]（PDF 物理页 8，Fig. 9）[pdf:E09]（PDF 物理页 9，Fig. 11）Table 2 同时揭示不同 case 的误差离散度差异很大：例如 LC-filter single-output line-voltage 的 \(\sigma=12.8741\%\)，而 LC-filter square-wave multi-output case 的 line-voltage \(\sigma=0.7395\%\)、efficiency \(\sigma=0.2791\%\)。[pdf:E12]（PDF 物理页 12，Table 2）因此不能只用整体 \(R^2\) 代替逐 case 分析。

**问题 3：parameter variation 是否被模型吸收？** 设计是分别按 load resistance、frequency、\(C_{ds}\)、\(R_{ds}\) 和 \(M\) 分桶绘制 prediction-error histogram。作者报告寄生 resistance/capacitance 扫描中多数误差落在 \(\pm2\%\) 内，但 line voltage 的方差通常大于 efficiency；Fig. 10/11 也可见少数尾部接近或超过 \(\pm4\%\)。[pdf:E09]（PDF 物理页 9，Fig. 10–11）[pdf:E13]（PDF 物理页 13，Section VI-C）

**问题 4：simulation relation 能否在真实三相 inverter 上保持？** 实验使用三相 DC-AC inverter 接 R-load，独立改变 DC source、load 与 switching frequency。Table 3 报告测量范围为 DC source 50–200 V、load 50–70 \(\Omega\)、frequency 10–20 kHz，功率开关为 IMBG120R045M1H；scope 样例覆盖 50/100/150 V、50/60 \(\Omega\) 与 10/20 kHz。[pdf:E12]（PDF 物理页 12，Fig. 14）[pdf:E14]（PDF 物理页 14，Table 3）Fig. 15 将 10 kHz 与 20 kHz 下的 measured efficiency 和 predicted efficiency 对比；作者总结 efficiency error 约在 \(+0.5\%\) 到 \(-2\%\) 之间。[pdf:E13]（PDF 物理页 13，Fig. 15）[pdf:E14]（PDF 物理页 14，Section VII-B）

**数据与执行限制。** 论文称 LTspice 数据按 70% training、20% test 划分，但没有说明剩余 10% 的用途，也没有交代 split 是否按 sample 随机、按 parameter range、按 topology 或按 operating scenario 隔离。[pdf:E14]（PDF 物理页 14，Section VII-A1）数据集样本数、epoch、optimizer、learning rate、batch size、seed、重复训练置信区间与 baseline surrogate 均未报告。实验验证是 R-load inverter 的有限 operating points，不等于对 LC-filter、未见 topology、极端 transient 或 fault switching event 的硬件验证。

**资源与 latency。** 论文报告的是 Big-O complexity 和 error metrics，没有给出 GNN inference 的 wall-clock latency、吞吐量、model parameter count、memory peak 或 energy。作者在结论中称训练后可作为“instant simulator”，并提出未来可缩减到 microcontroller；这属于作者的应用展望，不是本文已经完成的实时部署证据。[pdf:E15]（PDF 物理页 15，Conclusion continuation）

### § 8 — Take-aways

**5 句话。**

1. 论文最有价值的部分是把三相 inverter 的 topology、switching junction、元件/寄生参数和 controller parameters 放进同一个 graph interface。
2. 模型是三层 GCN、global mean pooling 和两层 FC 的 graph-level regression，主要预测 line voltage 与 efficiency，而非逐时间步重建开关瞬态。
3. simulation case 的 \(R^2\) 很高，physical R-load case 的 efficiency error 约为 \(+0.5\%\) 到 \(-2\%\)，说明在已覆盖 parameter range 内存在可学习关系。
4. 论文没有充分证明跨未见 topology 的 generalization，也没有排除 simulation-derived node features 带来的 leakage 或 surrogate 成本回流。
5. FPGA、定点化、资源、时序和 measured latency 均未报告，所以它是一个值得继续硬化的软件 GNN prototype，不是 FPGA-ready EMT solver。

**3 句话。**

1. 作者用 bond graph 保留 converter connectivity，再用 GNN 学习 graph-to-performance 映射。
2. 结果支持“已覆盖三相 inverter case 的参数回归有效”，但不支持“通用瞬态仿真或任意拓扑泛化已解决”。
3. 下一步的关键不是再堆一层网络，而是建立 causal state input、严格 topology-disjoint split 和可测量的 real-time hardware budget。

**1 句话。**

这篇论文证明 graph encoding 能把三相 inverter 的结构与参数变化送进统一回归器，但离可验证的 EMT 时间推进和 FPGA 实时部署仍有一整条证据链要补。

### § 9 — 最脆弱的假设

最脆弱的假设是：**构造 GNN input 所需的 analog node features 在 inference 时可廉价、因果地获得，而且不会泄露目标。**

这个假设一旦不成立，核心价值会直接失效。论文的 node features 不只有 nameplate component values，还包括从 simulation 得到的 switch current/voltage \(I_{sw}\)、phase voltage/current \(V_{ph},I_{ph}\)；目标又是 line voltage 与 efficiency。[pdf:E05]（PDF 物理页 5，Eq. (1) 与 Section III-E）如果新 topology 在送入 GNN 前仍需先跑高保真 simulation 才能得到这些状态量，那么 surrogate 并未真正省掉求解；如果这些量与 target 来自同一 simulation trajectory，随机 sample split 还可能让模型利用强相关 proxy，而不是学会可迁移的 circuit law。

论文提供的支持是：参数扫描、两种 filter configuration、square/SPWM 和有限实物工作点下误差较低。它缺少的证据是：只用 inference 时真实可得的 source/control/component/initial-state features，按 topology 和 operating region 完全隔离训练与测试，再与“不用 graph 的 MLP/XGBoost”和 physics-based reduced model 比较。由于 split、样本数和 feature availability 未被完整报告，这个假设仍未闭合。

### § 10 — 最小复现实验

一周内最值得做的不是复刻所有图，而是验证“graph encoding 是否在严格未见结构上提供额外泛化”。

1. 用 LTspice 或开源 circuit simulator 生成三类 two-level inverter 数据：R-load、RL-load、LC-filter；统一扫描 \(V_{dc}\)、\(R/L/C\)、\(F\)、\(M\) 与 \(R_{ds}\)。
2. 只保留 inference 时无需先求解 transient 才能获得的输入：topology、component values、control settings、initial condition；禁止把 target trajectory 中的 \(I_{sw},V_{ph},I_{ph}\) 作为输入。
3. 训练论文式 3-layer GCN + mean pooling + 2-layer FC，并训练参数量相近的 flattened MLP baseline。
4. 训练只看 R-load 与部分 RL-load；测试完全保留 LC-filter topology，并另设 parameter extrapolation test。
5. 测量 line-voltage/efficiency MAE、worst-case relative error、\(R^2\)，同时记录 feature extraction cost 与 end-to-end inference latency。

若 GNN 在 topology-disjoint test 上显著优于 MLP，且不依赖 simulation-derived state features，就支持论文最重要的 graph-interface claim；若两者相当，或 GNN 只有在加入 \(I_{sw},V_{ph},I_{ph}\) 后才表现好，则反驳“拓扑表示本身带来可用泛化”这一强解释。

### § 11 — 最强反例设计

最强反例是一组**相同 graph node/edge vocabulary、相近 steady-state performance、但 switching transient 与控制耦合完全不同**的电路，并要求模型在 topology-disjoint、event-rich 条件下预测。

具体可用 dead-time、device nonlinear capacitance、diode reverse recovery、DC-link imbalance 和 weak-grid impedance 组成测试族。训练集只覆盖理想 switch、balanced R/LC load 和固定 synchronous modulation；测试集加入不对称 dead-time、grid impedance resonance、负载突变与 device temperature drift。输入仍只允许预先可得量，不能注入仿真后的 switch current/phase voltage。替代解释是：原论文的高 \(R^2\) 主要来自平滑 parameter interpolation 和与 target 强相关的 simulation features，而不是 GNN 学到了 switching circuit dynamics。

若在这种测试中 steady-state line voltage 仍近似正确、但 peak current、settling、efficiency 与 stability indicator 系统性失败，就说明 global mean pooling 把决定极端行为的局部状态稀释了，也说明“performance regression”不能替代 EMT/event model。反之，如果模型在 topology/control/event 完全隔离后仍保持低 worst-case error，才真正增强论文关于 generalization 的证据。

### § 12 — Follow-up Research Idea

**候选方向：面向大规模 VSC 场站的层级 causal graph state-stepper，并以 FPGA 可执行约束共同训练。** 这不是对现有 GNN 再加一层，而是把任务从“静态 graph 到汇总性能”改成“在开关事件与网络耦合下，从可测状态推进到下一时刻”，并把部署预算直接写进模型定义。相关工作尚未做充分检索，因此这是证据约束下的候选研究方向，不声称 novelty。

**(a) 未满足的需求。** 大规模 VSC 场站需要同时处理单机内部 fast switching、机间电网耦合、控制器多速率与故障传播。本文的 static graph regression 没有时间推进，也没有证明多 converter composition；对实时 HIL/保护验证而言，仅预测 line voltage/efficiency 不够。

**(b) 研究价值。** 在 power electronics/EMT 领域，高影响结果必须同时给出数值稳定性、跨工况误差、工程实时性和硬件可实现性。一个能保持 network composition、显式推进 state、并在 fixed cycle budget 内运行的 graph model，才可能把 data-driven surrogate 从离线 screening 推向 real-time EMT co-simulation。

**(c) 可借鉴的方法。** 从 graph network simulator 借鉴 message-passing state update，从 switched-system/DAE solver 借鉴 event guard、algebraic constraint projection 与 energy/passivity regularization，从 FPGA design 借鉴 static sparse schedule、fixed-point quantization、operator fusion 和 bounded-memory streaming。模型可分两级：converter-local graph 处理 semiconductor/filter/controller state，station graph 处理 VSC 间线路与 PCC coupling；两级在预定多速率边界交换 Norton/Thevenin 等可组合接口量。

**FPGA 可部署性要求。** 在 architecture 冻结前就限定最大 node degree、message dimension、迭代次数与数值位宽；报告每个 EMT step 的 worst-case cycles、fmax、LUT/FF/DSP/BRAM、on-chip/off-chip traffic 和 end-to-end latency。软件 GNN accuracy 只能是入口，不能替代 RTL/HLS synthesis、timing closure 与 hardware-in-the-loop measurement。

**大规模 VSC 场站要求。** 训练/测试按 converter topology、station size、grid strength 与 fault type 隔离，至少覆盖多机并联、weak-grid resonance、asymmetric fault、control-mode switching 和 converter trip。评价不只看平均 \(R^2\)，还要看 KCL/KVL residual、energy drift、peak error、fault clearing trajectory、long-horizon stability 与实例数增长下的实时步长保持率。

**(d) 第一个可证伪实验。** 先做 2、4、8 台 VSC 的可扩展 feeder benchmark，训练只见 2/4 台和正常/小扰动，测试保留 8 台、weak-grid fault 与 controller mode switch；同一模型在 FPGA prototype 上以固定 EMT step 运行。只要出现以下任一结果，方向即被早期证伪：topology-disjoint trajectory error 随 rollout 发散；constraint projection 仍无法控制能量漂移；8 台时 worst-case latency 超出 step budget；量化后 fault peak error 不可接受。

**(e) 与本文的实质区别。** 本文是 whole-graph mean pooling 后预测少量汇总指标，switching/control 主要作为静态 features，复杂度只做 Big-O 分析。候选方向输出的是可组合的下一步 state 与端口量，显式处理 event/multi-rate/network coupling，并把 FPGA latency/resource 当作一等验收目标。它把 data-driven modeling、hardware realization 和 large-scale VSC composition 连接成同一个可证伪问题，而不是把三者写成互不约束的未来应用。
