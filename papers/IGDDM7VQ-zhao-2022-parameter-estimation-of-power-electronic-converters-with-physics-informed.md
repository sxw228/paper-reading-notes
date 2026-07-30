# Parameter Estimation of Power Electronic Converters With Physics-Informed Machine Learning

作者：Shuai Zhao，Yingzhou Peng，Yi Zhang，Huai Wang  
出处：IEEE Transactions on Power Electronics，Vol. 37，No. 10  
年份：2022  
DOI：10.1109/TPEL.2022.3176468  
Zotero key：IGDDM7VQ  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是一个很具体的工程问题：能否只利用 Buck 变换器控制系统本来就能取得的电感电流 \(i_L\) 和输出电压 \(v_o\)，在线或准在线地反推出电感、电容、等效串联电阻、开关管导通电阻、输入电压、负载等内部参数，而不额外注入扰动、增加传感器或拆机测量。作者把它定位为 condition monitoring 的基础能力，因为原位参数既可支持 adaptive control，也可支持故障诊断和健康状态评估；纯数据驱动方法又受制于电力电子数据量小、工况分布变化和黑箱输出可能违反物理规律三个问题。以上是论文在摘要和 Section I 的明确陈述（PDF 物理页 1）[pdf:E01]。

这项工作的价值不只在“估得准”。若一套估计方法必须向控制器注入伪随机扰动，或者依赖高采样率全波形和复杂的 \(s/z\) 域处理，它在关键任务设备上就可能因安全、计算量或可扩展性而失去实用性。论文希望证明：把已有的 Buck 微分方程直接嵌入神经网络训练，可以用正常负载变化产生的稀疏峰值数据完成参数反演，同时保持一定的抗噪声和跨器件组合能力（Section I，PDF 物理页 2）[pdf:E02]。这里的“在线”需要谨慎理解：论文设想数据由 edge 端采集后送至 cloud 端训练，训练耗时对按月退化的 condition monitoring 不敏感；它没有实现控制周期内的实时在线估计（Section III-A，PDF 物理页 7）[pdf:E07]。

## § 2 — 前人工作与不足

论文把前人方法分成两类。第一类是 purely data-driven：例如用前馈神经网络学习 dc-link ripple harmonics 与电容值的关系，或用 adaptive neuro-fuzzy inference system 从可测电压得到电容老化指标。这类方法容易实现，但需要足够覆盖工况的数据；在样本少、训练与测试分布不一致、外部扰动存在时，输出的泛化与物理可信性不足（Section I，PDF 物理页 1）[pdf:E01]。

第二类是利用物理模型的 hybrid data-driven 或 system-identification 方法。论文点名了基于 Buck 状态空间模型与 biogeography-based optimization 的参数搜索，以及基于动态模型与 generalized gradient descent 的 interleaved boost 参数估计。它们通常比纯数据方法更准、更稳，但论文归纳出三项工程负担：往控制器注入 pseudorandom binary sequence 可能不被安全规范接受；频域变换难以扩展到复杂系统；离散化近似会把误差带入参数估计（Section I，PDF 物理页 2）[pdf:E02]。

作者借用 PINN 的已有思想，把微分方程的可微物理约束纳入 supervised learning。需要区分的是：PINN、implicit Runge–Kutta（IRK）和 automatic differentiation 都不是本文原创；本文的贡献是把这些部件针对开关 Buck 的峰到峰参数反演组织成一个具体方案，并用仿真与硬件案例验证。论文声称“不需要复杂 \(s/z\) 域变换和离散化技术”，但实际仍使用 IRK time-stepping；更准确的理解是它避免了手工建立低阶离散传递函数，而不是完全消除了时间离散（Section I–II，PDF 物理页 2–4）[pdf:E02][pdf:E04]。

## § 3 — 重建作者的思考路径

以下是基于论文前置事实的思路重建，不是作者逐字陈述。

第一步，研究者已知 Buck 的开关状态、KCL/KVL 和元件模型可以写成低维微分方程；未知元件值只是方程中的系数。于是参数监测可被重写成 inverse problem：寻找一组参数，使模型在可测状态之间的演化与真实变换器一致（Section II-A–B，PDF 物理页 3）[pdf:E03]。

第二步，现场真正容易得到的不是无噪声连续轨迹，而是有限采样、不同步且带 ADC 量化的电流和电压。若只拟合端点，端点之间的轨迹不可见；若用普通数值求解器反复前向积分，每次优化都要解开关微分方程，且误差会与参数误差混在一起。因此需要一个既能表示端点之间潜在轨迹、又能让物理方程参与梯度传播的可微结构。

第三步，IRK 提供了桥梁：用 \(q\) 个 latent stage 表示两个可测端点之间的状态，并用 backward/forward equations 把端点、latent states 和未知参数绑在同一个计算图中。神经网络不直接从波形“猜参数”，而是预测 latent states；参数则出现在物理层里，通过端点重构误差与网络权重一起反向传播（Section II-C–D，PDF 物理页 4–5）[pdf:E04][pdf:E05]。

第四步，研究者还需要降低采样量。开关纹波的上下峰恰好处在 \(S=1\) 与 \(S=0\) 两个区间的交界，一个峰既是前一区间的结束状态，也是后一区间的初始状态。由此可以在不显式采集 gate signal 的情况下复用数据，并把采样率降到 \(2f_{\mathrm{sw}}\)（Section II-E，Fig. 5，PDF 物理页 6）[pdf:E06]。这四步合起来，才得到本文的 PIML 参数估计方案。

## § 4 — 核心 Intuition

核心 intuition 是：电流和电压的峰值不是彼此孤立的样本；它们必须能被同一组 Buck 物理参数连接成一段合法的开关动态。神经网络负责补出看不见的中间状态，IRK 与 Buck 方程负责检查这些中间状态是否能同时解释前后端点；训练若能压低端点重构误差，物理层中的未知参数也会被反向推到一组与数据相容的值（Fig. 4 与 Eq. (12)，PDF 物理页 5）[pdf:E05]。

真正改变问题难度的不是“网络更深”，而是把原本无限多种端点插值限制在满足已知动力学的集合内。这样做减少了数据需求，但也把成败压在一个更强的前提上：写入物理层的模型必须足够接近真实装置，而且现有激励必须让待估参数可辨识。

## § 5 — 具体方法与完整 Pipeline

以 48 V 输入、24 V 输出的 Buck 为例，论文的完整 pipeline 如下。

1. **建立连续物理模型。** 对 \(S=1\) 和 \(S=0\) 两个开关状态，使用 Buck 的 \(i_L\)、电容电压与 \(v_o\) 动态，把 \(L,R_L,C,R_C,R_{\mathrm{dson}},V_{\mathrm{in}},V_F,R\) 写成未知参数集合。Fig. 1 给出拓扑，Eq. (1) 给出状态模型；作者随后把它改写为 \(u_t+\mathcal N[u;\theta]=0\) 的形式（Section II-A–B，PDF 物理页 3）[pdf:E03]。

2. **收集峰到峰样本。** 负载变化、启动、停机或输入电压变化造成 transient。对每个开关周期只保留 \(i_L\) 与 \(v_o\) 的上下峰及两峰之间的 \(\Delta t\)。一个低峰可同时作为 \(S=0\) 区间的结束和 \(S=1\) 区间的开始，高峰反之；因此不必另外采 gate signal，名义采样率为 \(2f_{\mathrm{sw}}\)（Fig. 5，PDF 物理页 6）[pdf:E06]。

3. **构造 latent-stage 网络。** 网络输入是 \(i_L(t_n),v_o(t_n),S,\Delta t\)，输出是 \(q\) 个 \(i_L\) latent states 与 \(q\) 个 \(v_o\) latent states。Fig. 4 中，前半部是普通全连接网络，后半部不是自由权重层，而是由 IRK backward/forward equations 和 Buck 方程构成的物理层（Section II-D，PDF 物理页 5）[pdf:E05]。

4. **联合优化。** 物理参数 \(\theta\) 与网络权重、bias 一起进入参数集 \(\Theta\)。损失由前后端点的电流、电压重构平方误差组成；因为物理层显式可微，标准 back-propagation 可穿过物理层更新 \(\theta\)。仿真实现使用 TensorFlow，五层、每层 50 neurons，先 Adam、后 full-batch L-BFGS；Adam learning rate 为 0.001，\(\beta_1=0.9,\beta_2=0.999\)，训练 200,000 epochs（Section II-D、III-A，PDF 物理页 5–6）[pdf:E05][pdf:E06]。

5. **输出并校验参数。** 输出包括元件与系统参数。仿真以真值计算 percentage error；硬件中因离线 LCR 测量与运行态值有差异，作者用相对基准组的 parameter variation，而不是绝对值误差作为主要比较量（Section IV-C，PDF 物理页 9–10）[pdf:E09][pdf:E10]。

对 EMT + FPGA 读者，边界必须说清楚：论文没有报告 EMT 实时仿真器、固定实时步长、multi-rate scheduler、开关事件插值、矩阵并行分解、fixed-point 数值格式、FPGA resource/latency、HLS/RTL 映射或板上部署。其训练运行在 Intel Xeon E5-2620 2.4 GHz CPU 上，约 15 min，并被设想为 cloud 端慢时标 condition monitoring；这不是 FPGA 在线推理或硬实时估计结果（Section III-A，PDF 物理页 7）[pdf:E07]。因此不能从本文外推“已证明适合 FPGA 实时部署”。

## § 6 — 核心数学推导（无形式化数学则跳过）

先从一般动力系统出发：

\[
u_t+\mathcal N[u;\lambda]=0.
\]

这里 \(u\) 是可测状态，\(\lambda\) 是待估参数。对相邻可测时刻 \(t_n,t_{n+1}=t_n+\Delta t\)，IRK 引入 \(q\) 个不可测 latent stages \(u(t_n+c_i\Delta t)\)。其 backward 与 forward 关系为

\[
u_i(t_n)=u(t_n+c_i\Delta t)+\Delta t\sum_{j=1}^{q}a_{ij}\mathcal N[u(t_n+c_j\Delta t);\lambda],
\]

\[
u_i(t_{n+1})=u(t_n+c_i\Delta t)+\Delta t\sum_{j=1}^{q}(a_{ij}-b_j)\mathcal N[u(t_n+c_j\Delta t);\lambda].
\]

\(\{a_{ij},b_j,c_i\}\) 来自 \(q\)-stage IRK 的 Butcher tableau。直觉上，第一式要求 latent trajectory 能“倒推”到起点，第二式要求同一条 trajectory 能“前推”到终点；未知 \(\lambda\) 同时出现在两端约束中（Eq. (4)–(7)，PDF 物理页 4）[pdf:E04]。

对 Buck，作者把电感电流和输出电压分别写成

\[
\frac{di_L}{dt}+\mathcal N[i_L;\theta]=0,\qquad
\mathcal N[i_L;\theta]
=\frac{(S R_{\mathrm{dson}}+R_L)i_L+v_o-SV_{\mathrm{in}}+(1-S)V_F}{L},
\]

\[
\frac{dv_o}{dt}+\mathcal N[v_o;\theta]=0,\qquad
\mathcal N[v_o;\theta]
=\frac{v_o+C R_C R\,\mathcal N[i_L;\theta]-Ri_L}{C(R_C+R)},
\]

其中

\[
\theta=\{L,R_L,C,R_C,R_{\mathrm{dson}},V_{\mathrm{in}},V_F,R\}.
\]

这一步把可辨识的物理意义带入网络：例如 \(R_L\) 与 \(R_{\mathrm{dson}}\) 都通过电流压降影响 \(di_L/dt\)，因此它们容易形成耦合；这与后文发现二者单独误差大、总和 \(R_D=R_L+R_{\mathrm{dson}}\) 更稳定一致（Eq. (8)–(11)，PDF 物理页 4）[pdf:E04]。

训练目标为四类端点重构误差之和：

\[
\begin{aligned}
E(\Theta)=&
\sum_n\left[(i_L(t_n)-\hat i_L(t_n))^2+
(i_L(t_{n+1})-\hat i_L(t_{n+1}))^2\right]\\
&+\sum_n\left[(v_o(t_n)-\hat v_o(t_n))^2+
(v_o(t_{n+1})-\hat v_o(t_{n+1}))^2\right],
\end{aligned}
\]

\(\Theta=\{w,b,\theta\}\)。网络 latent states、网络参数与物理参数并不是分阶段求解，而是在同一 loss 下联合优化（Eq. (12)，PDF 物理页 5）[pdf:E05]。

作者用 IRK 截断误差 \(O(\Delta t^{2q})\) 选择 stage 数，并写出

\[
q=0.5\log(\epsilon)/\log(\Delta t).
\]

对最大 \(\Delta t=50~\mu s\) 和 64-bit machine precision \(\epsilon=2.2\times10^{-16}\)，论文计算最低 \(q>1.82\)，但实际取 \(q=20\)，以弱化截断误差和 \(q\) 对后续结果的影响（Eq. (13)，PDF 物理页 6）[pdf:E06]。这只是数值截断误差的选择依据，不是参数可辨识性或 optimizer 全局收敛的证明。

## § 7 — 实验设计与结论

**问题 1：少量数据能否在理想条件下估准？**  
实验：MATLAB Buck 仿真使用 Table I 的 48 V/24 V、20 kHz、\(C=164.5~\mu F\)、\(R_C=0.201~\Omega\)、\(L=725~\mu H\)、\(R_L=0.314~\Omega\) 等设置；三次负载变化各收集 120 个 switching periods，共 360 个峰到峰样本。网络为 \(5\times50\)，\(q=20\)（Section III-A、Table I，PDF 物理页 6）[pdf:E06]。  
答案：Table II 报告 clean data 下各参数 error 均显示为 0.1%；表注说明小于 0.1% 的结果统一向上显示为 0.1%，因此不能据表得到更精细的误差。Fig. 6 显示训练误差下降时平均参数误差同步下降（PDF 物理页 7）[pdf:E07]。

**问题 2：ADC、噪声与采样不同步会不会破坏估计？**  
实验：把仿真信号量化为 12 bit；电流、电压的量化步长分别为 2.4 mA 与 7.3 mV；加入 1、5、10 倍 Gaussian noise，并加入 \([0,2]~\mu s\) 的随机不同步（Section III-A，PDF 物理页 7）[pdf:E07]。  
答案：最差组合 ADC-Sync-10noise 的平均 error 是 4.9%，但单项并不都稳健：\(R_L\) 为 13.0%，\(R_{\mathrm{dson}}\) 为 27.3%，二者之和 \(R_D\) 为 3.6%；这说明总体平均值掩盖了参数耦合。作者据此把 \(R_D\) 作为联合健康指标（Table II，PDF 物理页 7–8）[pdf:E07][pdf:E08]。

**问题 3：结果是否只是某个网络宽深度的偶然产物？**  
实验：分别改变 hidden layers 与 neurons，对 clean data 和“ADC + synchronization + 10 倍 noise”的 poor data 测试。  
答案：Table III–IV 显示当网络超过约 3 layers、30 neurons 后，clean data 平均 error 接近 0.1%，poor data 多在约 4.7%–5.2%；论文正文把稳定范围概括为约 7%，与表中多数具体格值并不完全一致。作者最终选择 \(5\times50\)，但没有报告随机 seed 方差、独立 validation set 或与等参数量 data-only network 的受控 ablation（Section III-B、Tables III–IV，PDF 物理页 8）[pdf:E08]。

**问题 4：在真实硬件、不同器件和额定值下还能跟踪参数变化吗？**  
实验：20 kHz Buck prototype 用 12-bit HDO4054A oscilloscope 采集峰值；替换三只开关器件与四只电容，测试 48/24 V 和 24/12 V 两种额定条件。每组进行三次独立采集，每次仍由三段负载变化得到总计 360 pairs（Section IV-A–B，PDF 物理页 8–9）[pdf:E08][pdf:E09]。  
答案：Table V 表明 \(C\) 与 \(R_C\) 的 variation 大体跟随 LCR benchmark，输入电压和三个负载也较稳定；但 48/24 V 的 C4M3 组中，\(R_D\) benchmark variation 是 28.0%，估计为 46.5%。作者把差异归因于 \(R_{\mathrm{dson}}\) 对温度、电流的依赖、\(R_L\) 的电流依赖、遗漏的高阶寄生以及采集扰动（Table V 与 Section IV-C，PDF 物理页 10）[pdf:E10]。硬件网络宽深度扫描以离线 LCR 值为参照，在超过约 3 layers、30 neurons 后平均 error 稳定在约 10.0%–10.7%，作者概括为低于 11%（Table VI，PDF 物理页 11）[pdf:E11]。

**不得外推的范围。** 硬件验证是单一 Buck topology、手动负载阶跃、有限器件组合与两组电压等级；没有长时老化轨迹、温度 sweep、控制器闭环变化、多 topology、故障瞬态、跨设备预训练或真实 fleet distribution shift。另有一个复现时必须先核实的内部不一致：仿真 Table I 报告 \(L=725~\mu H\)（PDF 物理页 6）[pdf:E06]，硬件 Section IV-A 却报告 LCR 测得 \(L=7.25~\mu H\)（PDF 物理页 9）[pdf:E09]，两者相差 100 倍且正文没有解释这是不同硬件设计还是排版错误。

## § 8 — Take-aways

**5 句话：**

1. 本文把 Buck 连续动态模型、IRK latent stages 与深度网络放进同一个可微计算图，用端点重构误差反演元件参数（Fig. 4，PDF 物理页 5）[pdf:E05]。
2. 峰到峰共享把采样率降为 \(2f_{\mathrm{sw}}\)，三段负载瞬态只需 360 pairs；这是真正支撑 data-light claim 的工程设计（Fig. 5 与 Section III-A，PDF 物理页 6）[pdf:E06]。
3. 仿真平均误差很低且能承受所测试的 ADC、噪声和不同步，但 \(R_L\) 与 \(R_{\mathrm{dson}}\) 的单独估计明显不稳，联合量 \(R_D\) 更可信（Table II，PDF 物理页 7）[pdf:E07]。
4. 硬件结果证明该方法不只是干净仿真上的演示，却也暴露出 model mismatch：C4M3 的 \(R_D\) 变化量估计 46.5%，而基准为 28.0%（Table V，PDF 物理页 10）[pdf:E10]。
5. 论文是一个有说服力的 Buck case study，不是关于可辨识性、全局收敛、跨拓扑泛化或 FPGA 实时实现的完整证明；作者自己也把 loss weighting、suboptimal solution、网络设计与最小数据量列为开放问题（Section IV-E，PDF 物理页 11）[pdf:E11]。

**3 句话：**  
物理层把端点数据限制在 Buck 动力学允许的轨迹上，因此 360 个峰值对就能提供有意义的参数估计。实验支持“在给定 Buck、给定激励与给定扰动范围内可用”，但并未证明每个物理参数都唯一可辨识。最实用的结论是：PIML 能减少数据，但模型误差会直接变成参数偏差。

**1 句话：**  
这篇论文最重要的启示是：把物理写进 loss 能用更少数据反演变换器参数，但估计可信度的上限由物理模型的真实性与参数可辨识性决定。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在采集到的峰到峰 transient 范围内，作者写入 PINN 的低阶 Buck 模型既足够真实，又能让各个未知参数从 \(i_L,v_o\) 端点中唯一或近似唯一地辨识。**

这一个假设失效，核心贡献就会直接失效，因为训练 loss 只检查端点重构，不检查“得到的参数是不是那一个真实物理原因”。不同的 \(R_L\) 与 \(R_{\mathrm{dson}}\) 组合可以产生接近的总压降；温度、电流、死区、器件非线性和寄生支路又可能被 optimizer 吸收到错误的常参数里。此时 loss 仍然很低，输出也满足“所写模型”的物理约束，但参数并不代表真实元件。

论文给出的正面证据是：在人为设定的仿真扰动中，多数参数和平均误差稳定；硬件中 \(C\)、\(R_C\)、\(V_{\mathrm{in}}\) 与负载变化也大体跟随 benchmark（Tables II、V，PDF 物理页 7、10）[pdf:E07][pdf:E10]。反面证据同样来自论文：最差仿真中 \(R_{\mathrm{dson}}\) error 为 27.3%，硬件 C4M3 的 \(R_D\) variation 从 benchmark 28.0% 偏到 46.5%，作者明确承认温度、电流依赖与高阶寄生没有进入模型（PDF 物理页 10）[pdf:E10]。论文还未给出 structural identifiability 分析、参数置信区间、Jacobian condition number、多解搜索、温度 sweep 或 model-discrepancy detector；因此“低 loss 等于正确参数”仍是未经证明的关键跃迁。

## § 10 — 最小复现实验

一周内最小复现应只验证一个 claim：**在同样 360 个峰到峰样本下，加入 Buck 物理层是否比纯 data-driven 映射更能在噪声与小幅工况变化下恢复参数。**

数据可先用 MATLAB/Simulink 或一个独立 ODE/开关模型生成：按论文 Table I 设置 48/24 V、20 kHz，在三次负载阶跃中各取 120 periods，形成 \(\{i_L(t_n),i_L(t_{n+1}),v_o(t_n),v_o(t_{n+1}),\Delta t\}\) 共 360 pairs（PDF 物理页 6）[pdf:E06]。实现三种 estimator：论文的 \(5\times50\)、\(q=20\) PINN；相同容量但不含物理层的 MLP；以及直接对同一连续模型做 nonlinear least squares。固定 train/test transient，至少运行 10 个随机 seeds；随后加入 12-bit quantization、10 倍论文噪声和 \([0,2]~\mu s\) 不同步。

测量每个参数而不只是平均 error，并同时记录 endpoint prediction error、训练时间、不同 seed 方差和参数 Jacobian 的 condition number。若 PINN 在未见 load step 上的参数 median error 与 seed spread 都显著低于 MLP，且不只是在 endpoint prediction 上获胜，就支持“physics improves data efficiency/robustness”；若三种方法都能拟合端点，但 PINN 的 \(R_L,R_{\mathrm{dson}}\) 随 seed 大幅互换，或者 PINN 只在训练 transient 上准确，就反驳“可可靠估计各个物理参数”的强版本。论文公开声称附带 code/data，但本卡未联网取得或核验其当前可用性（Section I，PDF 物理页 2）[pdf:E02]。

## § 11 — 最强反例设计

最强反例不是再加更大的白噪声，而是制造**可预测的 model mismatch 与参数不可辨识**。让真实硬件的 \(R_{\mathrm{dson}}\) 随 junction temperature 和电流变化，让 \(R_L\) 随电流与频率变化，同时保留一个未建模的 dead-time/diode recovery 压降。训练数据只覆盖常温、窄负载区间的三次 transient；测试则放到高温和不同 duty/load 区间。PINN 仍被迫输出一组常数 \(\theta\)。

攻击成功的判据是：模型在 \(i_L,v_o\) 端点上仍有很小 reconstruction loss，但同一数据由多组 \((R_L,R_{\mathrm{dson}},V_F)\) 得到近似相同 loss，且估计参数相对四线测量或温度校准基准产生系统偏差。进一步可沿最小特征值对应方向扰动参数；若输出轨迹几乎不变，就直接展示 inverse problem 的平坦方向。这个反例针对的是“物理约束保证参数可信”而非“网络能拟合波形”，也正好放大论文已观察到的 \(R_D\) 偏差与遗漏温度/寄生问题（Section IV-C，PDF 物理页 10）[pdf:E10]。若方法在这个设置下能主动报告不可辨识或扩大 uncertainty，而不是给出自信的错误点估计，核心机制才算通过更强检验。

## § 12 — Follow-up Research Idea

候选研究方向是：**从 point-estimation PINN 改为 identifiability-aware、model-discrepancy-aware 的集合参数估计器。** 本领域的高影响研究通常不仅看算法平均误差，还看严格硬件验证、跨工况可实现性、故障安全性和是否能给工程决策一个可信边界；因此下一步不应只是换一种网络或再加一个传感器。

（a）驱动需求：condition monitoring 最危险的不是“误差略大”，而是 low loss 下给出一个看似精确、实际不可辨识的健康参数。论文当前只输出点值，且已经观察到 \(R_L/R_{\mathrm{dson}}\) 耦合、\(R_D\) hardware bias 与模型遗漏（PDF 物理页 7、10）[pdf:E07][pdf:E10]。

（b）研究价值：把任务改成“只有在当前激励足以辨识、模型残差与已知不确定性相容时才输出窄参数集合；否则输出不可辨识方向和需要的额外 transient”，可把 PIML 从估计器升级为安全诊断器。这个改变直接服务于实际 condition monitoring，而不是只改善 benchmark 平均数。

（c）可借鉴工具：从 nonlinear system identification 借 structural/practical identifiability，从 Bayesian inverse problems 借 posterior geometry，从 optimal experiment design 借最小安全激励选择；再增加一个显式 model-discrepancy state 吸收温度、死区和寄生的系统残差。这里仅是基于本文证据提出的候选组合，未做外部相关工作检索，不声称 novelty。

（d）第一个证伪实验：在温度 × 负载二维网格上重复第 11 节反例，对比普通 PINN 与新方法。若新方法不能在参数实际偏离时扩大 interval、标出 \(R_L/R_{\mathrm{dson}}\) 平坦方向，或其 interval 经常不覆盖真实值，就立刻否定方案。

（e）实质区别：本文问“如何用 physics + 360 samples 得到一组参数”；新问题问“当前数据与模型到底允许我们对哪些参数知道到什么程度，以及下一段最小安全 transient 应怎样选择”。它改变了输出对象、成功标准和数据采集闭环，不是给现有 PINN 再堆一层网络。
