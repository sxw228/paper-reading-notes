# Circuit Topology Aware GNN-Based Multi-Variable Model for DC-DC Converters Dynamics Prediction in CCM and DCM

作者：Ahmed K. Khamis；Mohammed Agamy
出处：*Neural Computing and Applications* 36, 20807–20822
年份：2024
DOI：10.1007/s00521-024-10293-0
Zotero key：K7VW84V3

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“给定过去波形，逐步预测未来状态”，而是另一个更窄的问题：能否把 DC-DC converter 的**电路连接、元件参数和控制参数**统一编码成 graph，再由一个 graph-level regression model 同时预测 voltage gain 与 inductor current ripple。作者用 Buck、Boost、Buck-boost 三种 topology，覆盖 CCM 与 DCM 两种工作模式；摘要给出的总指标是 \(R^2=99.51\%\)、MSE \(=0.0263\) [pdf:E01]（PDF 物理页 1，Abstract）。

这个问题重要，是因为传统的 converter surrogate 往往绑定某个固定输入维度或固定 topology；一旦 topology 改变，手工排列的特征向量和模型接口也要跟着改变。graph representation 让节点数和连接关系成为输入的一部分，因此一个共享参数的 GNN 在形式上可以接收大小不同的电路图。论文进一步希望把 duty cycle、switching frequency、\(R\)、\(L\) 等 operating point 信息一起放进图中，让模型不只分辨“这是什么电路”，还返回该电路在该 operating point 下的两个稳态 performance metrics [pdf:E02]（物理页 2，Contributions）。

但题目里的 “dynamics prediction” 容易造成误解。全文定义的监督样本是彼此独立模拟的 operating points；模型输入没有 \(x_t\)、历史窗口或初始状态，输出也不是 \(x_{t+1}\) 或一段 waveform，而是每张 graph 对应的 gain 和 ripple 标量 [pdf:E06]（物理页 6，Section 4）[pdf:E09]（物理页 9，Section 5.2）。因此，本卡把它归类为**稳态/operating-point 的静态 graph regression**，而不是动态状态递推或 trajectory rollout。

## § 2 — 前人工作与不足

作者把 prior work 分成两类。第一类已经把电路表示成 graph，但任务主要是 transistor sizing、analog layout constraint、electromagnetic response 或 FPGA HLS operation-delay prediction；节点、边和任务定义各不相同。Table 2 明确列出 GraphSAGE、GCN、GAT、Deep-GEN 等代表方法，并指出不少表示没有直接编码 series/parallel connection，或 edge feature 为空 [pdf:E04]（物理页 4，Table 2）。第二类是作者此前的 bond-graph mapping 工作 [13]：它把 element ID 与 normalized component value 放在 node feature 中，把 continuous connection 置 1、把 switching duty cycle 放在 edge feature 中，并支持 classification、regression、clustering [pdf:E05]（物理页 5，Table 2 continued）。

论文认为一般 graph theory、bond graph、Y-admittance representation 各有取舍。它选择 bond graph 的理由是：0/1 junction 可以表达串并联关系，switching cell 可以通过受 \(D\) 与 \(\bar D\) 控制的连接表达，且表示保留 CCM/DCM 所需的 switching semantics；代价是 causality assignment 更复杂，graph 可能更大 [pdf:E03]（物理页 3，Table 1 与 Section 3.1）。

这里真正被补上的缺口是“用同一个 graph regression interface 处理三种 converter topology 与多组参数”，不是“首次实现 circuit GNN”，也不是“首次建立 converter dynamics model”。尤其要注意，论文自己的 related-work table 已经承认 graph-based circuit prediction、transferable sizing 和 circuit representation 等方向存在；它的区别主要在 bond-graph-based switching representation 与两个 converter performance targets 的组合 [pdf:E04]（物理页 4，Table 2）[pdf:E05]（物理页 5，Table 2 continued）。

## § 3 — 重建作者的思考路径

下面是基于正文证据的重建，不是作者逐字陈述。

第一步，研究者会发现 converter 的 topology 本身就是结构化变量。把 Buck、Boost、Buck-boost 强行展平成同长度 vector，要么丢失连接语义，要么为每类 topology 维护一套特征布局。graph 则天然允许节点数和 adjacency 变化。

第二步，仅有 netlist adjacency 不够。switching converter 的行为不仅取决于“谁连着谁”，还取决于 switch 在一个周期内存在连接的比例、switching frequency、energy-storage element 和 load。于是需要一个能把 KVL/KCL connection 与 switching semantics 同时放进 graph 的表示。bond graph 的 0-junction、1-junction、source、storage、resistive element，正好提供这套中间语言 [pdf:E03]（物理页 3，Section 3.1）。

第三步，把 circuit element 与 junction 变成 node，把 connection 变成 edge；element ID 和 value 进入 node feature，duty cycle 进入 switching edge，frequency 进入作为 control source 的 node。这样 topology change 表现为 node/edge incidence 的变化，parameter change 表现为 feature value 的变化 [pdf:E05]（物理页 5，Section 3.2）。

第四步，使用共享权重的 message passing，把不同大小的 graph 压成固定长度 embedding，再用 global mean pooling 与 fully connected layers 输出两个 scalar。这条路径同时满足“可变 graph 输入”和“固定维数 regression 输出”，因此作者把多 topology 与多 parameter operating points 放进同一个监督学习问题 [pdf:E07]（物理页 7，Eq. 7–13 与 Fig. 3）。

## § 4 — 核心 Intuition

电路的性能不只由元件数值决定，也由元件如何连接决定；因此不要把 topology 当作一个外加 class label，而要让 message passing 直接在物理连接 graph 上聚合。再用 global mean pooling 把任意节点数的 graph 压成固定长度 vector，就能让一个 regression head 接收不同 topology。这里学到的是“graph 与 operating point 到稳态指标”的映射，不是时间演化律。

## § 5 — 具体方法与完整 Pipeline

以一个 Boost converter operating point 为例，完整 pipeline 是：

1. **从 circuit 到 bond graph。** 电感、电容、电阻、电压源/电流源以及 0/1 junction 成为 graph node；串并联和能量流连接成为 edge。switching cell 被展开为受 \(D\) 与 \(\bar D\) 控制的 0/1-junction connection [pdf:E03]（物理页 3，Section 3.1）。
2. **构造 topology-aware features。** node feature 含 element ID 的 one-hot encoding 和 normalized component value；continuous edge 的 feature 为 1，switching edge 的 feature 为 duty cycle；switching frequency 作为 control-source node 的属性。Fig. 2 展示了三种 converter 的 circuit 与 graph，它们的 topology change 直接体现为节点与边的不同排列，而不是一个单独的 topology token [pdf:E05]（物理页 5，Table 2 与 Section 3.2）[pdf:E06]（物理页 6，Fig. 2）。
3. **形成单样本输入。** 每个 operating point 产生一张 \(G=(X,A,e)\)：\(X\) 是 node-feature matrix，\(A\) 是 adjacency，\(e\) 是 edge feature/weight。该输入描述当前 topology 和 \(R,L,F,D\) 等参数；没有过去时刻的 waveform、state history 或未来控制序列 [pdf:E08]（物理页 8，Section 5.1，Eq. 15–20）。
4. **message passing。** 正文称使用三层 GCN，让每个 node 聚合邻居与自身信息；共享参数使 parameter count 在形式上不绑定 graph 的节点数。随后 global mean readout 把所有 node embedding 平均为一个长度 \(d\) 的 graph vector [pdf:E08]（物理页 8，Sections 4.3、5.1、5.2）。
5. **regression head。** 两个 fully connected linear layers，中间用 LeakyReLU，并配 dropout；训练目标是 MSE。输出向量长度 \(\ell=2\)，对应 voltage gain 和 inductor current ripple。正文的曲线与散点实际把 ripple 表示成 natural-log quantity，图中 ground truth 可为负；但 Table 5 仍简称 “current ripples”，论文没有清楚交代 log transform、normalization 与反变换 [pdf:E07]（物理页 7，Eq. 11–13）[pdf:E11]（物理页 11，Section 5.4.2）[pdf:E13]（物理页 13，Fig. 8）。
6. **训练与评测。** 18,000 张 graph 以 70%/30% 划分 train/test，另有 2,200 张 “unseen validation” graph；optimizer 是 Adam，learning rate 为 0.02。数据覆盖三种 topology、CCM/DCM，以及不同 inductance、load、frequency、duty cycle [pdf:E09]（物理页 9，Section 5.2）[pdf:E10]（物理页 10，Fig. 5 及下方正文）。

这里的 “unseen” 只被定义为未参加训练的 graph samples。论文没有报告按 topology 分组的 split，也没有说把某一种 topology 完整留出。因此验证集最多证明在相同三类 topology 和相同参数定义下的 held-out operating-point prediction；不能据此说模型测试过 unseen topology。

**target leakage 判断。** 正文列出的 input feature 没有直接包含 gain 或 ripple；Fig. 5 也把 “True Variables” 只接到 loss branch，而不是接回 GCN input，因此没有看到把 label 直接喂给模型的证据 [pdf:E10]（物理页 10，Fig. 5）。但 gain/ripple 由同一组理想 \(D,R,L,F\) 与 topology 生成，而论文没有交代参数采样的去重、相邻 grid point 分组或 split 前后的 simulation-run 隔离。高分可能主要来自同一公式族内的密集 interpolation；这不是已经证实的直接 leakage，却是当前 split 无法排除的 evaluation weakness [pdf:E09]（物理页 9，Table 3 与 Section 5.2）。

论文也没有给出 waveform sampling interval、prediction horizon 或 rollout length，因为 pipeline 根本没有时间推进。没有 event detection、多速率离散化或 switching-step integration；CCM/DCM 是 dataset 中 operating regime 的覆盖，而不是模型在时间轴上检测并推进 mode transition。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，但核心是标准 GCN regression，不是 converter state equation 的推导。

首先，作者把监督学习写成从输入 \(x\) 到输出 \(y\) 的回归，并用 squared loss

\[
L(f(x),y)=(f(x)-y)^2
\]

最小化预测与 ground truth 的差异 [pdf:E07]（物理页 7，Eq. 5）。这里的 \(x\) 是一张 operating-point graph，不是动态系统的时刻状态。

GCN 的 layer update 写为

\[
X^{(k+1)}
=
\sigma\!\left(
\hat U^{-1/2}\hat A\hat U^{-1/2}X^k\Theta^k
\right),
\]

其中 \(\hat A=A+I\) 加入 self-loop，\(\hat U\) 是 \(\hat A\) 的 degree matrix，\(\Theta^k\) 是第 \(k\) 层共享权重。直观上，每个 node 把邻居的 feature 按 degree normalization 后求和，再做线性变换与 nonlinear activation；所以改变 connection 会改变信息传播路径 [pdf:E07]（物理页 7，Eq. 8–9）。

不同大小的 graph 通过 global mean pooling 变成固定长度 vector：

\[
\phi=\frac{1}{N_i}\sum_{n=1}^{N_i}x_n,
\]

其中 \(N_i\) 是第 \(i\) 张 graph 的节点数。这个平均使 output head 不依赖节点排列，也允许节点数变化；但平均也可能抹平“相同局部 motif 出现多少次”的规模信息，因此形式上可接收大 graph 不等于已经证明 scale generalization [pdf:E07]（物理页 7，Eq. 10）。

最终模型可概括为

\[
Y=\operatorname{Regression}(X,A,e),
\]

\[
X\in\mathbb{R}^{N\times d_{\mathrm{in}}},
\quad
GCN^{(k)}:\mathbb{R}^{N\times d_{\mathrm{in}}}\rightarrow
\mathbb{R}^{N\times d},
\quad
GMR:\mathbb{R}^{N\times d}\rightarrow\mathbb{R}^{1\times d},
\quad
FC:\mathbb{R}^{1\times d}\rightarrow\mathbb{R}^{1\times\ell}.
\]

这些式子明确表明输出来自整图 readout，而不是 \(x_{t+1}=F(x_t,u_t)\) 的 recurrence [pdf:E08]（物理页 8，Eq. 15–20）。

作者还给出三层 GCN 的渐近复杂度：

\[
O\!\left(3(e+Nd_{\mathrm{in}}^2)+(N+dN)+2d^2+d\,OL\right)
\]

以及 space complexity

\[
O(N+e+Nd_{\mathrm{in}}+3d+OL).
\]

它们只说明计算量如何随 graph size 增长，不是实际 latency、吞吐量或资源占用。Fig. 4 只在约 10–12 个 node、每 node 约 9 个 feature 的三类小 graph 上代入复杂度量级 [pdf:E08]（物理页 8，Section 4.3）[pdf:E09]（物理页 9，Fig. 4）。

对于物理 target，Table 3 给出理想 converter 的稳态 gain 与 CCM/DCM boundary。例如 CCM Buck、Boost、Buck-boost 的 gain 分别为 \(D\)、\(1/(1-D)\)、\(-D/(1-D)\)；DCM gain 和边界还依赖 \(R,L,T_s\) [pdf:E09]（物理页 9，Table 3）。这进一步说明 benchmark 很大程度上是在学习理想稳态公式族，而不是学习 transient dynamics。

## § 7 — 实验设计与结论

**问题 1：一个共享 GNN 能否拟合三种 topology、两种 mode 下的两个输出？**  
实验：用 18,000 张 graph 的 70%/30% train/test split，再用 2,200 张 held-out validation graph；输入包含 topology、\(R,L,F,D\)，输出为 gain 与 ripple [pdf:E09]（物理页 9，Section 5.2）。  
答案：正文报告 validation \(R^2=99.49\%\) [pdf:E11]（物理页 11，Section 5.4.2）；Table 5/摘要又报告 total \(R^2=0.9951\) [pdf:E15]（物理页 15，Table 5）[pdf:E01]（物理页 1，Abstract）。二者接近但并不相同，论文没有明确它们分别对应哪个 split 或 aggregation。

**问题 2：graph embedding 是否区分 topology 与 CCM/DCM？**  
实验：把 global-mean-pool output 降为 2-D 并按 converter/mode 着色，同时画 gain 与 ripple 曲线。  
答案：六个 topology-mode groups 在 2-D 图中形成可辨的区域，作者据此认为 embedding 同时编码 structure 与 operating condition [pdf:E12]（物理页 12，Fig. 7）。这是 representation 的可视化证据，但不是 unseen-topology generalization test；同一批已知类别形成 cluster 不能证明新类别可预测。

**问题 3：逐 topology 的预测精度如何？**  
实验：画 prediction 对 ground truth 的散点图并报告 MSE、\(R^2\)。  
答案：Fig. 8 给出的 voltage-gain \(R^2\) 为 Buck 0.9997、Boost 0.9977、Buck-boost 0.9988；ripple \(R^2\) 为 0.9863、0.9962、0.9847 [pdf:E13]（物理页 13，Fig. 8）。其中 Boost ripple 的 MSE 在 Fig. 8 写作 0.0172，而 Table 5 写作 0.172，存在十倍不一致 [pdf:E13]（物理页 13，Fig. 8）[pdf:E15]（物理页 15，Table 5）。因此不能把该项 MSE 当成已闭合的精确结果。

**问题 4：参数变化是否被模型响应？**  
实验：在 \(R=1\text{–}20\,\Omega\)、\(L=1\text{–}10\,\mu H\)、\(F=10\,\mathrm{kHz}\text{–}1\,\mathrm{MHz}\)、\(D=0.01\text{–}0.85\) 范围内画按参数分组的 prediction-error histogram [pdf:E11]（物理页 11，Table 4）[pdf:E14]（物理页 14，Fig. 9）。  
答案：作者认为各参数范围内 error mean 较小，且 duty-cycle 变化被 edge feature 响应。需要保留两个限制：这些都是训练数据定义范围内的 interpolation；Fig. 9 caption 称 “absolute prediction error”，但横轴实际有负值，因此画的是 signed error 而非 absolute error [pdf:E14]（物理页 14，Fig. 9）。

**问题 5：模型是否可跨 topology、跨规模或部署到硬件？**  
实验：没有。论文只给出三种小 graph 的渐近复杂度，未报告 hold-one-topology-out、larger unseen graph、不同 cell 数量、真实 converter waveform、parameter count、runtime、inference latency、memory footprint、数值精度、量化、FPGA synthesis 或硬件实测 [pdf:E08]（物理页 8，Section 4.3）[pdf:E09]（物理页 9，Fig. 4）。  
答案：这些能力没有被本文证明。作者在 conclusion 中把 framework 外推到 “any circuit”，但实验范围不足以支撑该强表述 [pdf:E15]（物理页 15，Conclusion）。

数据也不是公开可下载的：Data Availability 只说可向作者索取，同时又称数据含 proprietary/confidential information、属于尚未完成项目 [pdf:E15]（物理页 15，Data Availability）。因此本文结果目前不能按原数据做严格独立复现。

## § 8 — Take-aways

**5 句话。**  
第一，这是一篇 topology-aware 的静态 graph regression 论文，不是动态状态递推论文。第二，它用 bond graph 把 element type/value、connection、duty cycle 和 switching frequency 放进统一 graph input，并对 Buck、Boost、Buck-boost 的 gain 与 log-scale ripple 做联合预测。第三，在包含这三种已知 topology 的 held-out samples 上，论文报告约 0.995 的总体 \(R^2\)，但 split 语义、部分 MSE 数字和 target transform 交代不完整。第四，实验没有留出整种 topology，也没有扩大 node count，所以不能证明跨 topology 或跨规模泛化。第五，论文没有 FPGA、实时仿真或硬件部署证据；它与 FPGA-native 研究的交集限于 graph representation 和多 topology 训练思路。

**3 句话。**  
该方法把 converter topology 与 operating parameters 编成 graph，再用 GCN、global mean pooling 和 FC head 预测两个稳态指标。高 \(R^2\) 证明了已知三类理想 converter 参数域内的 interpolation 能力，但没有证明 temporal dynamics、unseen topology、scale transfer 或 hardware deployment。对固定同构 VSC 场站的价值更可能是训练阶段的 topology-aware representation，而不是可直接部署的 FPGA 动态模型。

**1 句话。**  
它证明“graph 可作为多种理想 DC-DC converter 稳态 surrogate 的共享输入接口”，没有证明“一个可跨 topology、可跨规模、可在 FPGA 上递推真实 converter dynamics 的原生模型”。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**graph 中显式编码的 topology、\(R,L,F,D\) 等 feature 已足以让 gain 与 ripple 成为单值函数 \(Y=F(X,A,e)\)**。只要两个真实 converter 具有相同 graph input，却因未编码的 capacitor/inductor ESR、switch/diode voltage drop、dead time、磁饱和、温度、control-loop state、初始能量或测量带宽而产生不同 ripple 或 transient，监督目标就不再是这个输入的单值函数，模型无论多大都无法恢复被省略的信息。

论文为该假设提供的证据，是理想 simulation-derived dataset 中三种 topology、规定 \(R,L,F,D\) 范围的高 held-out \(R^2\) [pdf:E11]（物理页 11，Table 4 与 Section 5.4.2）[pdf:E13]（物理页 13，Fig. 8）。它缺少的证据更关键：没有 hardware data、parasitic variation、closed-loop transient、initial-condition variation、out-of-range test，也没有说明 simulation fidelity 与 ripple label 的具体计算窗口。Data Availability 还使外部研究者无法直接审计 feature 与 label 是否存在未披露的共同生成变量 [pdf:E15]（物理页 15，Data Availability）。

**目标方向的碰撞判断。** 对“训练时覆盖多 topology、部署时固定同构光伏 VSC 场站 topology 的 FPGA-native model”，本文构成**部分方法碰撞**：它已经明确提出多 topology graph 输入、共享 GCN 参数和固定维度 readout；如果拟议贡献只写成“用 GNN 在多 topology 上训练一个 converter surrogate”，碰撞很强 [pdf:E02]（物理页 2，Contributions）。但它没有 VSC、PV station、多 converter interaction、state recurrence、long-horizon stability、fixed-topology specialization、multi-instance composability 或 FPGA implementation。因而它不碰撞“多 topology graph teacher → 固定同构 topology 的 causal dynamic model → FPGA-native implementation”这条更完整的核心链路；这些环节目前仍是本文的缺口，不是本文已证明的能力。

## § 10 — 最小复现实验

一周内可做一个“先复现 interpolation，再专门测试 topology claim”的最小实验：

1. 用理想 Buck、Boost、Buck-boost simulation 或公开公式生成 graph samples；参数只用论文范围：\(R=1\text{–}20\,\Omega\)、\(L=1\text{–}10\,\mu H\)、\(F=10\,\mathrm{kHz}\text{–}1\,\mathrm{MHz}\)、\(D=0.01\text{–}0.85\) [pdf:E11]（物理页 11，Table 4）。保存 gain 和 \(\log(\Delta I_L)\)，并明确记录 CCM/DCM 判据。
2. 实现最小 3-layer GCN + global mean pooling + 2-layer MLP；同时实现一个强但简单的 baseline：flattened physical parameters 加 topology one-hot 的 MLP。论文未报告 hidden width、dropout rate、batch size、epoch、seed，所以这些不能声称“精确复现”，应公开固定为一套最小配置。
3. 做两个 split。A 是 sample-level random split，用来判断能否复现论文的高 interpolation \(R^2\)；B 是 leave-one-topology-out，例如只训练 Buck 与 Boost，完整测试 Buck-boost。
4. 测量每个 target、每个 topology 的 \(R^2\)、MAE、worst-decile error；对 ripple 同时在 log space 与反变换后的 physical unit 报告，避免只在 log domain 看起来很准。
5. 支持核心 claim 的最低结果是：A split 中 GNN 达到接近论文的 \(R^2\)，且明显优于同容量 MLP。反驳“跨 topology”外推的结果是：B split 显著退化、误差在 CCM/DCM boundary 集中，或 MLP 与 GNN 无显著差别。由于原始数据不公开，这个实验验证的是核心机制，不是逐字节复现报告数字 [pdf:E15]（物理页 15，Data Availability）。

## § 11 — 最强反例设计

最强反例不是再随机抽一批相同 topology 的 operating points，而是构造**输入 graph 在论文 feature space 中相同、真实目标却不同**的一对系统。

具体做法是准备两个 nominally identical Boost converters：graph topology、\(R,L,F,D\) 完全相同；其中一个使用理想 switch/diode 与低 ESR 元件，另一个加入已测得的 diode drop、switch on-resistance、inductor DCR、capacitor ESR、dead time 和温升。对两者施加相同 input voltage 与 duty-cycle step，从同一 nominal operating point 记录稳态 gain、ripple 以及 5–20 个 switching periods 的 transient waveform。按本文 feature encoder，两者得到相同 \(X,A,e\)，模型必须给出同一个输出；如果实际 ripple 或 mode-transition behavior 显著不同，就直接证明 feature sufficiency 假设失败。

再加一个 topology-level attack：训练只覆盖 Buck、Boost、Buck-boost，测试一个节点数更大、含相同局部 motifs 的 interleaved 或 cascaded converter。若 global mean pooling 把 component multiplicity 稀释，或 message-passing depth 不足以覆盖全 graph，模型会在形式上“接收”新 graph，却不能保持正确的 gain/ripple scaling。原论文只评测约 10–12 node 的三种 graph，未提供这种 holdout [pdf:E09]（物理页 9，Fig. 4）。

这个反例的判定标准很硬：只要出现相同论文输入对应多种可信 ground truth，静态 regression claim 在真实系统上就不是误差稍大，而是问题本身欠定；只要 unseen topology/scale 的误差远高于 sample-level random split，就不能再用“GNN 可接收不同大小 graph”代替“已证明跨 topology/规模泛化”。

## § 12 — Follow-up Research Idea

**候选想法：topology-conditioned dynamic teacher 与 fixed-topology FPGA student 的双阶段建模。** 相关工作尚未做系统检索，因此这里不声称 novelty。

**（a）未满足的需求。** 多 topology 数据可以帮助模型学到可迁移的 circuit motifs，但实际光伏 VSC 场站部署往往是大量固定同构单元。部署端真正需要的是带 initial state、control history 与 exogenous grid input 的 causal state transition，并在长时间 rollout、converter 并联和 mode/event 变化下稳定；本文的两个稳态 scalar 不能满足这个需求。

**（b）潜在研究价值。** 研究目标从“一个 variable-size GNN 直接预测稳态指标”改成“训练阶段用 graph teacher 学结构先验，部署阶段把知识蒸馏成固定 topology、可证明资源上界和 rollout stability 的 FPGA student”。这不是简单增加一个模块，而是改变了 train-time representation 与 deploy-time architecture 必须相同的假设。固定同构 topology 允许离线展开 adjacency、消除通用 message-passing 调度，并把每层映射为规则 streaming datapath。

**（c）相邻领域工具。** 可借鉴 neural operator/state-space model 的 causal rollout、physics-informed residual、graph-to-circuit compilation、knowledge distillation，以及 FPGA HLS 中的 fixed-point quantization、pipeline initiation interval 与 resource-aware co-design。teacher 处理多 topology；student 只处理一个已知 VSC cell graph，但保留 Kirchhoff residual 或 port-level passivity/stability constraint。

**（d）第一个证伪实验。** 在训练中覆盖多种 converter/VSC topology，完整留出一种 topology 与一种更大 scale；然后把 teacher 蒸馏到固定目标 topology 的 student。比较四类模型：纯固定-topology MLP/RNN、直接部署的通用 GNN、graph-teacher-distilled student、physics solver。若蒸馏 student 在 long-horizon waveform error、mode-transition failure rate、closed-loop stability 和 FPGA latency/resource 上不能同时优于最简单 fixed-topology baseline，这个想法立即被证伪。

**（e）与本文的实质区别。** 本文的输入是单张 operating-point graph，输出是 gain 与 log-scale ripple；训练和部署都使用同一通用 GNN，且没有硬件实现 [pdf:E08]（物理页 8，Section 5.1）[pdf:E13]（物理页 13，Fig. 8）。候选方向的输入包含 state/history 与因果 control，输出是可 rollout 的 next-state/waveform；graph 主要服务于跨 topology 训练，最终 FPGA student 针对固定同构 topology 编译。它继承本文“topology should be represented, not merely labeled”的洞见，但把核心问题从稳态 interpolation 改为可组合、可综合、可长期稳定的动态算子。
