# Black-Box Modeling of DC-DC Converters Based on Wavelet Convolutional Neural Networks

作者：Gabriel Rojas-Dueñas、Jordi-Roger Riba、Manuel Moreno-Eguilaz  
出处：IEEE Transactions on Instrumentation and Measurement  
年份：2021  
DOI：10.1109/TIM.2021.3098377  
Zotero key：7DQGB3MP（附件 VLXC6EEH）  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是一个很具体的工程问题：当商用 DC-DC converter 的拓扑、器件参数和控制器均由厂商保密时，怎样只凭端口可测的电压、电流，重建它在稳态纹波和负载突变期间的输入电流与输出电压。作者以 more electric aircraft（MEA）的 270 V 高压母线到 28 V 低压母线为对象，因为该系统包含来自不同厂商的 power converter，而系统设计者又必须在规划、预防、设计和优化阶段预测这些器件对整个配电网的影响。论文明确要求一个合格模型同时再现均值、纹波、开关频率特征和扰动瞬态，而不仅是一个平均值模型；这也是 black-box 建模在这里有价值的原因。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

作者的核心技术 claim 是：将端口时序先做离散小波变换（DWT），再把多尺度系数交给 convolutional neural network（CNN）学习，可以在不访问内部电路的条件下，以较低计算负担同时拟合高频开关纹波和低频负载瞬态。论文把它称为离线、非侵入式的 wavelet convolutional neural network（WCNN）识别方法，并把用途限定在机载系统的规划、设计、优化和维护，而不是在线控制器本身。[pdf:E02]（PDF 物理页 2，Introduction 末段）

工程价值在于“可用的端口替身”：若模型在目标工况内可信，MEA 工程师可以在不迫使供应商公开知识产权的情况下，把 converter 的端口行为纳入系统级仿真。这里必须保留一个边界：论文验证的是一台特定商用 270 V-to-28 V converter 和特定实验分布，不能仅凭摘要中的“可扩展到其他 converter”就把结果外推为通用模型。

## § 2 — 前人工作与不足

论文把已有路线分为三类。white-box 方法需要拓扑、确定性方程、内部器件模型和待辨识参数；state-space averaging 也依赖 converter 的数学结构。这些信息恰好是商用模块最常缺失的，因此 white-box 在本问题上不是精度不够，而是输入条件不成立。[pdf:E01]（PDF 物理页 1，Introduction）

black-box 方面，Hammerstein 和 Steiglitz IIR 模型需要向 duty cycle 施加外部激励，作者将其评价为复杂、耗时且鲁棒性有限。polytopic 方法在每个 operating point 建立 small-signal G-parameter 模型，局部结果可以准确，但要为每个工况保留模型，且不能准确跨越 continuous conduction mode（CCM）与 discontinuous conduction mode（DCM）。基于 frequency response function 的 terminal characterization 也不能再现 DCM，并依赖 network analyzer 等昂贵设备。[pdf:E02]（PDF 物理页 2，Introduction 前半）

数据驱动路线中，作者此前的 NARX recurrent neural network 能拟合 buck converter，却要训练 100 个以上的网络，代价较高；wavelet artificial neural network（WANN）能提取多频率特征，但此前主要用于分类和故障诊断。论文据此提出的差异不是“第一次用神经网络”，而是把 DWT 的多分辨率表征、CNN 的局部 pattern 提取和一个覆盖广 operating points 的实验集组合起来，用一个回归网络同时拟合纹波与负载瞬态。[pdf:E02]（PDF 物理页 2，Introduction）

需要谨慎对待作者对 prior work 的评价：这些比较来自本文的文献叙述和后续实验，不是本卡独立复核相关论文后的结论；本任务没有联网补充全文，因此不声称 WCNN 的 novelty 已被穷尽性检索确认。

## § 3 — 重建作者的思考路径

以下是基于论文证据重建的合理推断，不是作者逐句给出的研究日记。

第一步，研究者先接受现实约束：内部开关状态、控制律和器件参数不可得，唯一稳定可获取的是端口的 \(V_{\mathrm{in}}, I_{\mathrm{in}}, V_{\mathrm{out}}, I_{\mathrm{out}}\)，所以问题必须被改写为 terminal time-series 的输入到输出映射。[pdf:E01]（PDF 物理页 1，Introduction）

第二步，他们注意到目标输出包含两个时间尺度。700 kHz switching 带来微秒级纹波，负载接入或断开则产生毫秒级瞬态；只拟合平均量会漏掉系统级电磁和控制相互作用，而只做局部 small-signal 模型又难以跨工况。[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E06]（PDF 物理页 6，Table 1）

第三步，从信号处理角度，DWT 能把原始时序分成 approximation 与多个 detail 分量，使低频瞬态和高频纹波在不同尺度上显式出现；从机器学习角度，CNN 的 weight sharing 和局部连接可在转换后的系数对象上寻找重复 pattern，而不需要 RNN 的反馈状态。于是作者把时序重排为 CNN 可接受的三维对象，并在输出端用 inverse DWT（IDWT）恢复 \(I_{\mathrm{in}}\) 与 \(V_{\mathrm{out}}\)。[pdf:E03]（PDF 物理页 3，Eq. (5) 与 Section II-B）[pdf:E04]（PDF 物理页 4，Fig. 2–3）

第四步，black-box 的“鲁棒”不能来自物理方程，只能来自实验覆盖，因此数据采集被设计为从近空载到额定功率的广负载区间，并让每个实验都包含一次 load change。最后再用 Bayesian optimization 搜索滤波器和训练超参数，以免手工选择网络规模成为主要误差源。[pdf:E05]（PDF 物理页 5，Fig. 4 与 Section III-A）[pdf:E06]（PDF 物理页 6，Section III-B）

## § 4 — 核心 Intuition

WCNN 的核心 intuition 是：先把 converter 波形拆成“慢变化的工作点/瞬态”和“快变化的开关纹波”等尺度，再让 CNN 在这些尺度组成的对象上寻找局部 pattern，通常比让一个网络直接从原始序列中同时发现所有时间尺度更容易。输入端的 DWT 与输出端的 IDWT 只改变表示方式，不需要知道 converter 拓扑；真正决定可用性的，是训练数据是否覆盖部署时会遇到的端口激励。[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E04]（PDF 物理页 4，Fig. 2–3）

## § 5 — 具体方法与完整 Pipeline

以一次 270 V 母线下的负载断开实验为例，完整 pipeline 如下。

1. **采集端口波形。** 微控制器按计算机指令接通或断开八个并联负载 converter，示波器同步采集时间、\(V_{\mathrm{in}}\)、\(I_{\mathrm{in}}\)、\(V_{\mathrm{out}}\)、\(I_{\mathrm{out}}\)。模型把可视为外部条件的 \(V_{\mathrm{in}}\) 和 \(I_{\mathrm{out}}\) 作为输入，把 \(I_{\mathrm{in}}\) 和 \(V_{\mathrm{out}}\) 作为输出。[pdf:E04]（PDF 物理页 4，Section II-C）[pdf:E06]（PDF 物理页 6，Fig. 6–7）
2. **预处理。** 作者先用 low-pass filter 降低测量噪声，再归一化输入和输出。滤波器的具体截止频率、阶数和相位特性未报告；这意味着现有 PDF 不能完全复现预处理，也无法判断滤波是否削弱了部分 switching harmonic。[pdf:E04]（PDF 物理页 4，Section II-D）
3. **多尺度变换。** 对每条输入和训练目标时序分别执行 multilevel DWT，母小波为 Daubechies 10（db10）。分解产生 approximation \(A_0\) 与 detail \(D_0,D_1,\ldots,D_n\)；论文说分解层数依据 2.5 MHz 采样、converter switching frequency 和 transient response 选择，但没有报告最终 \(n\)。[pdf:E03]（PDF 物理页 3，Eq. (5) 后文字）
4. **重排为 CNN 输入。** Fig. 2 把系数排成三维对象：\(x\) 轴是 DWT 后的 steps，\(y\) 轴是 \(V_{\mathrm{in}}\) 与 \(I_{\mathrm{out}}\) 的各分解层，\(z\) 轴是不同实验；单次推理时不再需要 \(z\) 轴的实验堆叠。[pdf:E04]（PDF 物理页 4，Fig. 2）
5. **WCNN 回归。** 网络依次包含两层 convolution、两层 max pooling、fully connected layer 和 regression layer，并使用 batch normalization 与 ReLU。两层 convolution 是作者通过比较不同深度后选出的 accuracy/compute 折中，而不是由电路阶次推导得到。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Eq. (6)）
6. **训练与调参。** Adam 负责更新权重；Bayesian optimization sequentially 训练 30 个候选网络，搜索 learning rate、gradient decay factor、每层 filter 数以及 filter 的宽和高。最终表列出 11 个 filters、\(3\times10\) filter、learning rate 0.02661、GDF 0.8006、mini-batch 128、pool size 5、\(L_2=10^{-4}\)。调参阶段每个候选用 500 epochs；随后正文又说明最终训练设为 3000 epochs，这是 PDF 中可读到的两个不同阶段，不应合并成一个数字。[pdf:E05]（PDF 物理页 5，Fig. 4）[pdf:E07]（PDF 物理页 7，Table 3–4 与其后正文）
7. **恢复输出并评测。** regression 输出的 wavelet-domain 表示经 IDWT 还原为 \(I_{\mathrm{in}}(t)\) 和 \(V_{\mathrm{out}}(t)\)，再在按“整次实验”隔离的 test set 上计算 RMSE 与 \(R^2\)，并检查 steady-state ripple、load transient 和 measured-versus-estimated scatter。[pdf:E04]（PDF 物理页 4，Fig. 3）[pdf:E07]（PDF 物理页 7，Section IV）

这不是显式 switching/event 模型：没有开关器件、拓扑状态、事件检测器或数值积分器，开关与 load-change 的影响都隐含在采样波形中。论文也没有报告多速率 time stepping、在线 inference latency、固定步长实时执行、并行计算图、定点位宽、量化误差或 FPGA 映射；只报告训练使用 MATLAB Deep Learning Toolbox 和 GeForce RTX 2080 Super GPU，数据采集控制用 Python。[pdf:E06]（PDF 物理页 6，实验设备段）[pdf:E07]（PDF 物理页 7，Section IV 末段）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文没有从 converter 电路方程推导 WCNN，也没有给出稳定性、泛化误差或物理一致性定理；其数学内容是各处理层的定义。理解这些式子的重点，是看清“表示变换”和“回归器”分别做了什么。

卷积层写为
\[
C_k=W_k*x ,
\]
其中 \(x\) 是输入对象，\(W_k\) 是第 \(k\) 个 filter/feature map 的权重，\(*\) 表示卷积，\(C_k\) 是提取出的特征。激活层再计算
\[
Y_k=f(C_k).
\]
这两式的直觉是：同一个局部检测器在不同时间/尺度位置共享权重，随后用非线性函数保留有用响应。[pdf:E03]（PDF 物理页 3，Eq. (1)–(2)）

batch normalization 按 PDF 中 Eq. (3)–(4) 写成
\[
\hat{x}_i=\frac{x_i-\mu_B}{\sqrt{\sigma_B^2+\varepsilon}},\qquad
y_i=\gamma\hat{x}_i+\beta ,
\]
其中 \(\mu_B,\sigma_B^2\) 是 mini-batch 输入的均值和方差，\(\varepsilon\) 提高数值稳定性，\(\gamma,\beta\) 是训练中更新的 scale 与 offset。它把各通道先标准化再允许网络恢复合适的尺度，从而缓和训练过程中 activation 分布漂移。[pdf:E03]（PDF 物理页 3，Eq. (3)–(4)）

论文将 DWT 定义为
\[
\mathrm{DWT}(j,k)=\frac{1}{2^j}\int f(t)\,
\psi\!\left(\frac{t-k2^j}{2^j}\right)\,dt ,
\]
其中 \(f(t)\) 是 converter 时序，\(\psi(t)\) 是 mother wavelet，\(j\) 是 scale coefficient，\(k\) 是 translation coefficient。增大或减小 \(j\) 相当于改变观察窗口，让同一波形在不同时间尺度上投影为 scaling 与 wavelet coefficients；作者选 db10 来表示 disturbance feature，并把系数组织为 \(A_0,D_0,\ldots,D_n\)。这里按 PDF 原式誊写，论文没有进一步证明 db10 或该归一化形式对本 converter 是最优的。[pdf:E03]（PDF 物理页 3，Eq. (5) 及相邻定义）

ReLU 为
\[
f(x)=
\begin{cases}
x,&x\ge 0,\\
0,&x<0,
\end{cases}
\]
用来把负 activation 截为零。作者声称这样可避免 saturation 并改善训练；IDWT 虽是输出恢复的关键步骤，PDF 没有给出其公式或边界处理方式。[pdf:E04]（PDF 物理页 4，Eq. (6) 与 Fig. 3）

因此，这一节能重建的是“DWT → CNN layer → IDWT”的计算关系，不能重建一个具有电路物理约束的 state equation。尤其没有方程保证能量守恒、因果性、passivity 或与外部 source/load impedance 互连后的稳定性。

## § 7 — 实验设计与结论

**问题 1：训练数据是否覆盖了 converter 的主要负载工况？** 作者用 Vicor DCM3714xD2K31E0yzz 商用模块搭建实验，额定输入范围 160–420 V、额定输出 500 W、额定输出电流 17.86 A、switching frequency 700 kHz；实验负载由八个不同类型的 DC-DC converter 加电阻组成，并由微控制器切换。作者要求工况从近空载覆盖到额定功率，以跨越未知的 CCM/DCM 区域。[pdf:E06]（PDF 物理页 6，Table 1–2 与 Section III-B）答案是“负载幅值覆盖较宽”，但论文没有用独立 conduction-mode 标签证明每一种 mode 都被覆盖，也没有报告每个 operating point 的分布。

**问题 2：test set 是否与训练数据分离？** 共完成 1000 次实验，500/250/250 次分别用于 training/validation/test；每次实验保存 time、\(V_{\mathrm{in}}\)、\(I_{\mathrm{in}}\)、\(V_{\mathrm{out}}\)、\(I_{\mathrm{out}}\) 五个向量，采样率 2.5 MHz。test experiments 没有参与训练，这比把同一条长波形随机切点再分割更能避免直接泄漏。[pdf:E07]（PDF 物理页 7，Section III-B 末段与 Section IV）但所有实验的输入电压均设为 270 V，激励类型也只有 load connection/disconnection，所以分离的是同一实验分布内的新试次，不是新电压、新硬件或新环境。

**问题 3：DWT 是否比直接 CNN 有贡献？** Table 5 在同一数据上比较 WCNN 与不使用 DWT 的 CNN。WCNN 的 \(I_{\mathrm{in}}/V_{\mathrm{out}}\) RMSE 为 0.0093/0.0077，\(R^2\) 为 0.9965/0.9956，time elapsed 为 515 s；无 DWT 的 CNN 分别为 0.0094/0.0082、0.9958/0.9931 和 1332 s。表格没有在 RMSE 列头明确写单位，因此本卡不擅自补单位。[pdf:E07]（PDF 物理页 7，Table 5）答案是：在这组实现中，DWT 明显缩短了报告的 training time，并带来较小的 accuracy 改善；但没有多随机种子、置信区间或显著性检验，不能把差异归因得过强。

**问题 4：相对其他 time-series / black-box 模型是否更准？** 同一表中，LSTM-NN、WANN、NARX NN 和 polytopic model 的 \(R^2\) 均低于 WCNN；WCNN 尤其在 \(V_{\mathrm{out}}\) RMSE 上优于 NARX（0.0077 对 0.144）和 polytopic（0.0077 对 0.198）。然而这些 baseline 的模型容量与调参预算不完全等价：LSTM 使用 grid search，NARX/ polytopic 来自作者实现，WCNN 使用 30 次 Bayesian optimization，因此结果证明的是“本文实现组合的整体表现”，不是单独 CNN 或 DWT 的无条件优越性。[pdf:E05]（PDF 物理页 5，比较方案说明）[pdf:E07]（PDF 物理页 7，Table 5）

**问题 5：模型是否再现了稳态纹波与负载瞬态？** Fig. 9 显示在 270 V steady state 下，WCNN 的 \(I_{\mathrm{in}}\) 与 \(V_{\mathrm{out}}\) 波形贴近 measured curve，而多种 baseline 主要跟住均值、没有跟住 ripple/commutation frequency。瞬态例子从 264.2 W 变为 148.8 W；Fig. 10–11 显示 WCNN 对电流下降和电压过冲的时序与幅度最接近 measured curve。Fig. 12 汇总全部 test experiments，拟合斜率分别为 1.0003（输入电流）与 0.9996（输出电压）。[pdf:E07]（PDF 物理页 7，Fig. 9 与 Fig. 10 引入段）[pdf:E08]（PDF 物理页 8，Fig. 10–12）答案是在已测 test distribution 内支持“可重建均值、纹波和代表性 load transient”。

**问题 6：是否证明了实时或 FPGA 可执行性？** 没有。论文报告的是 offline training、GPU 型号和 time elapsed，没有报告单步 inference latency、memory footprint、实时步长、worst-case execution time、fixed-point sensitivity 或 FPGA resource/timing。因此“low computational burden”和“estimation very fast”是作者结论，但不能从现有实验转换成 real-time EMT/FPGA 验收结论。[pdf:E02]（PDF 物理页 2，Introduction 末段）[pdf:E07]（PDF 物理页 7，Table 5 与平台说明）

## § 8 — Take-aways

**5 句话：**

1. 论文把一台信息不透明的 270 V-to-28 V 商用 converter 改写为端口时序回归问题，只用 \(V_{\mathrm{in}},I_{\mathrm{out}}\) 预测 \(I_{\mathrm{in}},V_{\mathrm{out}}\)。
2. DWT 把高频 switching ripple 与低频 load transient 显式分到多个尺度，CNN 再从变换后的对象中学习 pattern，IDWT 恢复时域输出。
3. 1000 次、2.5 MHz 采样的实验按整次试验分为 500/250/250，test set 内的 \(R^2\) 约为 0.996，波形也覆盖 steady ripple 和代表性 transient。[pdf:E07]（PDF 物理页 7，数据集说明与 Table 5）
4. 与无 DWT CNN 及多种 baseline 相比，本文 WCNN 在该实现中兼得较低 RMSE 和较短 training time，但比较没有多随机种子或不确定度。
5. 最大边界是训练和测试都固定在 270 V、同一台 converter、同类 load-change 分布，且没有实时、物理一致性或 FPGA 证据。

**3 句话：**

1. 这篇论文的有效贡献是把多尺度信号处理与 CNN 结合成一个可从端口数据学习 converter 波形的 offline black-box pipeline。
2. 它在同分布实验 test set 上很好地拟合了输入电流、输出电压、纹波和瞬态，并显示 DWT 对训练效率有益。[pdf:E08]（PDF 物理页 8，Fig. 10–12 与 Conclusions）
3. 它尚未证明跨输入电压、跨硬件、跨老化条件的泛化，也未证明模型互连后的稳定性或实时硬件可实现性。

**1 句话：**

WCNN 是一个在单台 converter、固定 270 V 实验分布内很准确的多尺度端口波形拟合器，但还不是经过跨工况、物理稳定性和 FPGA 实时性验证的通用 converter surrogate。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**训练集覆盖的端口激励分布足以代表模型部署时会遇到的分布。** 这个假设一旦不成立，black-box 模型没有电路方程或物理约束可以帮助它在训练域外保持正确，论文最核心的“robust、可用于系统规划并可扩展到其他 converter”就会失效。

论文给出的支持证据是：负载工况从近空载覆盖到额定功率，每次实验都包含 load change，1000 次实验中有 250 次完全留作 test，且 Fig. 12 对这些 test trials 呈现接近 1 的拟合斜率。[pdf:E06]（PDF 物理页 6，Section III-B）[pdf:E07]（PDF 物理页 7，数据集划分）[pdf:E08]（PDF 物理页 8，Fig. 12）

缺失的证据同样关键：尽管器件额定输入范围是 160–420 V，全部实验却固定为 270 V；论文没有跨输入电压、source impedance、温度、老化或另一台同型号样机测试，也没有说明 train/test 的负载组合是否严格不重叠。[pdf:E05]（PDF 物理页 5，Section III-A 末段）[pdf:E06]（PDF 物理页 6，Table 1）因此，“在同一分布内新试次上准确”有证据，而“对实际部署扰动鲁棒”仍是证据不足的作者外推。

## § 10 — 最小复现实验

一周内最值得复现的不是完整飞机配电系统，而是 **DWT 是否在严格 held-out experiments 上同时改善 ripple/transient accuracy 与训练时间**。

数据方面，优先向作者索取论文所说可通过 e-mail 提供的 1000 次实验；若未取得，就不能声称“精确复现”，只能用现有实验台采集一个较小的替代数据集。严格复现实验应保留 2.5 MHz 原采样和五个向量，并按整次 load-change experiment 分割，不能把同一瞬态的相邻采样点泄漏到 train/test。[pdf:E07]（PDF 物理页 7，数据集与代码可得性说明）

实现两个除 DWT 外完全相同的模型：A 为 low-pass/normalize → 两层 CNN → regression，B 为 low-pass/normalize → db10 multilevel DWT → 同一 CNN → IDWT。固定数据 split，至少运行多个随机 seed；同时记录 \(I_{\mathrm{in}},V_{\mathrm{out}}\) 的 RMSE、\(R^2\)、steady-state ripple spectrum error、瞬态峰值误差、settling-time error 与 wall-clock training time。论文未报告 DWT level 和 low-pass 参数，因此要把二者列为显式实验变量，而不是偷偷任选一个值。

若 B 在多数 seed 上稳定降低 transient/ripple error，且 training time 明显小于 A，就支持论文关于多尺度表示的核心 claim；若差异在 seed 变化后消失、只来自模型容量或预处理，或者 B 只改善均值而破坏 switching ripple，则反驳该 claim。这个实验不需要重建所有 baseline，却能直接检验论文最可归因于 DWT 的增量。

## § 11 — 最强反例设计

最有力的反例是制造 **输入电压 covariate shift**：只用论文的 270 V 数据训练 WCNN，然后在同一台 converter 的 200 V、270 V、380 V 下施加完全相同的 load connection/disconnection 序列，分别测量 \(I_{\mathrm{in}}\) 和 \(V_{\mathrm{out}}\)。这三个电压都位于论文给出的 160–420 V 额定范围内，但训练数据只覆盖其中一个点。[pdf:E05]（PDF 物理页 5，固定 270 V 的实验假设）[pdf:E06]（PDF 物理页 6，Table 1）

攻击指标应包括：原始波形 RMSE、switching ripple 频谱、瞬态峰值与 settling time，以及预测功率 \(V_{\mathrm{in}}I_{\mathrm{in}}\) 与输出功率 \(V_{\mathrm{out}}I_{\mathrm{out}}\) 的物理一致性。若 270 V 仍维持 Table 5 的水平，而 200/380 V 的误差和能量不一致显著放大，就得到一个具体替代解释：论文中的“robustness”主要来自同分布重复采样，而不是 WCNN 学到了可跨工作条件复用的 converter dynamics。由于 \(V_{\mathrm{in}}\) 名义上已经是模型输入，这个反例尤其强；失败不能简单归因于“模型没有接收电压信息”，只能归因于训练激励没有让模型识别该维度。

## § 12 — Follow-up Research Idea

在 instrumentation、power electronics 与 EMT/HIL 交叉领域，高影响结果通常不仅要求 test-set waveform accuracy，还要求跨器件与跨工况验证、可解释的失效边界、与外部网络互连后的数值稳定性，以及可在目标实时硬件上实现的 latency/resource 证据。基于第 9 节的缺口，一个候选研究方向是：**把 black-box converter modeling 从“单一实验分布内的波形回归”改写为“带不确定度与 passivity 约束的可组合端口 operator 学习”。** 由于本任务未补充检索相关全文，这只是候选想法，不声称 novelty。

**(a) 未满足需求。** 系统设计者真正需要的不是在某批 load steps 上误差最小的曲线拟合器，而是一个放进未知 source/load network 后仍能给出可信区间、拒绝超出训练域的输入，并避免凭空产生能量的 terminal model。本文很高的同分布 \(R^2\) 不能回答这个系统级问题。[pdf:E08]（PDF 物理页 8，Fig. 12 与 Conclusions）

**(b) 研究价值。** 若模型能在 160–420 V、不同 source impedance 和 load sequence 下保持可校准 uncertainty，并通过 passivity/dissipativity test，它就从“离线 surrogate”变成可安全组合的系统设计部件；再证明 fixed-point implementation 的误差与 worst-case latency，才有资格进入 EMT/FPGA 或 HIL 场景。

**(c) 可借鉴方法。** 可从 neural operator 或现代 causal state-space model 借鉴长时序输入到输出映射，从 control theory 借鉴 incremental passivity/dissipativity constraint，从 active learning 借鉴选择最能缩小不确定度的电压—负载实验。DWT 可以保留为多尺度前端，但不再被当成稳定性来源。

**(d) 第一个证伪实验。** 用稀疏的输入电压和 load-step 组合训练，在未见过的中间/边界电压、不同 source impedance 以及两个 converter 级联时测试。若 uncertainty interval 不能覆盖真实误差，或模型在一个参考物理模型稳定的互连中违反 passivity 并诱发虚假振荡，这个方向的核心主张就被证伪。

**(e) 与本文的实质区别。** 本文优化的是一台 converter 在固定 270 V 数据分布内的 \(I_{\mathrm{in}},V_{\mathrm{out}}\) 点对点回归误差；候选方向把研究目标改为“可组合、知道自己何时不可信、满足端口物理约束的动态 operator”，评价对象也从单条 waveform 扩展为互联系统的稳定性与硬件可执行性。这不是简单增加一层网络或更换应用领域，而是改变 black-box model 的成功定义。
