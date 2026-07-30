# Temporal Modeling for Power Converters With Physics-in-Architecture Recurrent Neural Network

作者：Xinze Li、Fanfan Lin、Huai Wang、Xin Zhang、Hao Ma、Changyun Wen、Frede Blaabjerg  
出处：IEEE Transactions on Industrial Electronics, 71(11), 14111–14123  
年份：2024  
DOI：10.1109/TIE.2024.3352119  
Zotero key：43HISH3I  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的是：怎样用很少的实测时序数据建立功率变换器的大信号时域模型，同时让模型保留可解释的电路物理、能在训练域外推断，并避免每换一个工况就重新训练。作者指出，纯知识模型在寄生参数、器件离散性、环境扰动和噪声下容易产生模型失配；纯 data-driven 模型又依赖大量数据、难以可靠外推且缺乏物理解释；把微分方程放进 loss 的 PL-PINN 仍只是软约束，并需要为新工况重训。[pdf:E01]（物理页 1，Abstract 与 Section I）

这件事重要，不只是因为“预测波形更准”。变换器时域模型是设计、控制、状态监测和故障诊断的底座；如果模型能以少量硬件数据校正名义电路模型，又能保留显式的时间推进结构，就可能减少每台样机、每个工作点重新标定的成本。论文在 1 kW multilevel DAB converter 上把问题具体化为：由 TPS 调制、直流工作条件和上一时刻的电感电流，递推预测下一时刻电感电流。[pdf:E03]（物理页 3，Section II 与 Fig. 3）

需要先限定外推含义。本文验证的是同一台 DAB、同一 TPS 策略下改变输入/输出电压的 out-of-domain；它没有证明跨拓扑、跨器件、跨开关频率或跨故障模式的通用迁移。[pdf:E07]（物理页 7，Tables II–III）

## § 2 — 前人工作与不足

论文把既有路线分成三类。第一类是 knowledge-based 方法，例如分段解析模型、状态空间模型和软开关/效率模型；它们具有清楚的物理结构，但面对未建模寄生、硬件个体差异和外界噪声时，名义参数并不等于真实装置。第二类是 FFN、LSTM、GRU 等 data-driven 方法；它们可以从数据拟合复杂映射，但论文引用的 DAB current-stress 建模案例需要接近一百万个数据点，且黑箱模型在训练分布之外不可靠。第三类是 physics-informed 方法，例如通过 labeled loss、physical residual loss 和 boundary loss 串联约束网络的 PL-PINN；其物理只进入目标函数而未进入计算结构，因此优化只能把违背物理的程度压小，不能在结构上排除它。[pdf:E02]（物理页 2，Section I 与 Fig. 2）

作者认为 PL-PINN 还有两个工程不足：新工况会改变 physical/boundary loss，因而需要完整重训；串行的“data-driven 预测后再施加物理 loss”结构可能积累误差，并引入缺少通用选法的多个 loss weight。[pdf:E06]（物理页 6，Section III-E 与 Fig. 9）论文的对比对象因此覆盖 piecewise、FFN、LSTM、GRU、LN-GRU 和 PL-PINN，而不是只与一个弱黑箱 baseline 比较。[pdf:E09]（物理页 9，Table V）

不过，这里的“不足”主要是作者对所选 PL-PINN 结构的理论分析和本论文实现上的对比，并不能自动推广到所有 hard-constrained PINN、differentiable simulator 或结构保持型 neural ODE；论文没有对这些更强的相邻路线做实验比较。

## § 3 — 重建作者的思考路径

下面是基于论文背景证据的重建，不是作者逐字陈述。

第一步，从 DAB 的工程事实出发：电感电流的主导变化由 KVL、桥臂开关状态、母线电压、变比、漏感和等效电阻决定，名义模型已经给出“下一步大致往哪里走”。第二步，承认名义模型无法覆盖电流尖峰、overshoot、寄生和器件差异，因此单靠解析式达不到硬件波形精度。第三步，观察显式 Euler、Heun 或 Runge–Kutta 本来就是“上一状态 + 当前输入 → 下一状态”的递推计算，天然可以展开成 RNN，而不必让一个通用神经网络重新学一次积分规律。[pdf:E04]（物理页 4，Section III-A/B 与 Eqs. (4)–(6)）

第四步，把任务拆成两个责任边界：physics-in-architecture core 负责可写出的电路动力学，LN-GRU 只学习物理模型没有描述的残差；两个输出相加，形成最终预测。第五步，先用实测数据反向校准电路参数 \(\theta\)，再固定物理骨架、训练 LN-GRU 的权重 \(\{w,b\}\)，从而避免两个模块同时争抢同一种误差解释。[pdf:E05]（物理页 5，Figs. 5–6 与 Section III-C/D）第六步，用极少训练序列和电压域外工况来检验这套拆分是否真的带来 data-light 和 no-retraining extrapolation，而不是只在训练集内提高拟合精度。[pdf:E08]（物理页 8，Table IV 与 Fig. 12）

## § 4 — 核心 Intuition

不要让神经网络“学会物理定律”，而是把离散化后的电路方程直接做成 recurrent architecture，使每一步状态推进先沿着已知物理走。再并联一个 LN-GRU，只补偿寄生、尖峰和参数失配等未建模部分；理想情况下，少量数据只需学习较小的残差，而无需重新学习全部变换器动力学。[pdf:E04]（物理页 4，Fig. 4）

## § 5 — 具体方法与完整 Pipeline

以论文的 multilevel DAB under TPS 为例，完整 pipeline 是：

1. **输入与开关表示。** TPS modulator 接收三个位移量 \(D_0,D_1,D_2\) 和工作条件 \(V_1,V_2\)，生成原、副边三电平桥电压以及 \(s_{\mathrm{pri}},s_{\mathrm{sec}}\in\{-1,0,1\}\) 的开关函数。状态是上一采样时刻的漏感电流 \(i_L(t_k)\)。[pdf:E03]（物理页 3，Fig. 3 与 Section II）
2. **物理递推。** 作者由 DAB 高频交流回路的 KVL 写出 \(i_L\) 微分方程，再用显式 Euler 离散为固定步长递推；在一般框架中，也可换成 Heun 或三阶 Runge–Kutta 的 increment function。[pdf:E05]（物理页 5，Fig. 5）
3. **数据残差。** 与物理 core 并联的 LN-GRU 读取同一时序上下文，经一层、48 个神经元和 fully connected layers 输出残差修正。最终状态预测是物理递推与残差输出之和。[pdf:E04]（物理页 4，Fig. 4）[pdf:E08]（物理页 8，Table IV）
4. **分阶段训练。** 先反向传播电路参数 \(\theta\)，以最小测试 loss 的 checkpoint 结束 physics core 训练；再随机选 LN-GRU 超参数并训练 \(\{w,b\}\)，重复到搜索上限，最后加载两个 core 各自最小测试 loss 的 checkpoint，并用 validation set 检验泛化。[pdf:E06]（物理页 6，Figs. 7–8）
5. **前向部署。** 每一步将预测的 \(i_L(t_{k+1})\) 反馈为下一步输入，迭代生成一段波形。论文还描述了 inverse computation，即从状态与输入识别 \(\theta\)，但实验重点是前向波形建模。[pdf:E06]（物理页 6，Fig. 8 与相邻正文）

事件处理只通过离散开关函数和固定采样间隔进入模型；论文没有报告独立事件队列、零交叉处理或变步长积分。多速率时间推进未报告。训练时两个 core 是先后训练，推断结构在概念上并联；实际软件运行平台是 Windows 11、AMD Ryzen 5 5600H、16 GB RAM、Python/PyTorch。[pdf:E07]（物理页 7，Section IV-B）

论文说该递推图“可以”通过 HLS 部署到 FPGA 或 GPU 形成实时 digital twin，但没有实现或测量 FPGA 映射。因而 FPGA device、定点/浮点格式、位宽、资源占用、流水线/并行度、时钟频率、吞吐、端到端延迟均未报告；HIL 未报告；EMT 仿真器耦合未报告；可持续实时步长也未报告。文中的 \(\Delta t=2\times10^{-7}\,\mathrm{s}\) 是模型采样/积分间隔，不是已经验证的实时执行步长。[pdf:E08]（物理页 8，Table IV、Eq. (12) 与 Fig. 12）

## § 6 — 核心数学推导（无形式化数学则跳过）

一般状态空间模型写成

\[
\frac{d x(t)}{dt}=f(x(t);u(t);\theta)
=g(u(t);\theta)x(t)+h(u(t);\theta).
\]

这里 \(x\) 是电感电流、电容电压等状态，\(u\) 是桥电压等输入，\(\theta\) 是电路与控制参数。把连续导数在 \(\Delta t\) 上离散，得到

\[
x(t+\Delta t)=x(t)+\phi(x(t);u(t);\Delta t;\theta)\Delta t ,
\]

其中 \(\phi=\sum_i a_i k_i\)，不同 \(a_i,p_i,q_{i,j}\) 选择对应 Euler、Heun 或 Runge–Kutta。工程直觉是：RNN cell 并非自由拟合状态转移，而是执行一个已知 numerical integrator；可学习的 \(\theta\) 只校准物理参数。[pdf:E04]（物理页 4，Eqs. (4)–(6)）

对本文 DAB，连续模型为

\[
\frac{d i_L(t)}{dt}
=-\frac{R_L}{L_k}i_L(t)
+\frac{s_{\mathrm{pri}}(t)}{L_k}V_1
-\frac{n\,s_{\mathrm{sec}}(t)}{L_k}V_2 ,
\]

其中 \(s_{\mathrm{pri}},s_{\mathrm{sec}}\) 分别由桥臂导通组合取 \(1,-1,0\)。显式 Euler 递推因此是

\[
i_L(t+\Delta t)=i_L(t)+
\left(
-\frac{R_L}{L_k}i_L(t)
+\frac{s_{\mathrm{pri}}(t)}{L_k}V_1
-\frac{n\,s_{\mathrm{sec}}(t)}{L_k}V_2
\right)\Delta t .
\]

这一步把 KVL 直接落实到每个 recurrent step。[pdf:E07]（物理页 7，Eqs. (9)–(10)）[pdf:E08]（物理页 8，Eq. (11)）

总 loss 是各状态回归 loss 的平均：

\[
L(\theta;w,b)=\frac{1}{d}\sum_{i=1}^{d}L_i(\theta;w,b),\qquad
L_i=\frac{1}{N_DN_T}\sum_{j=1}^{N_D}\sum_{k=1}^{N_T}
\left\|x^*_{i,j}(t_k)-o_{i,j}(t_k)\right\|^2 .
\]

它分别用于校准 \(\theta\) 和训练 \(\{w,b\}\)。注意，虽然 physics core 的递推严格遵循选定方程，最终输出还叠加了不受该方程约束的 LN-GRU residual；因此“最终预测严格物理一致”并不能仅由上述推导推出。[pdf:E05]（物理页 5，Eq. (7)）[pdf:E06]（物理页 6，Eq. (8) 与 Figs. 8–9）

采样间隔由调制精度约束

\[
\Delta t\le \frac{\rho}{2f_s}.
\]

本文取 \(f_s=20\,\mathrm{kHz}\)、\(\rho=0.01\)，并配置 \(\Delta t=2\times10^{-7}\,\mathrm{s}\)。这说明离散网格能分辨相移参数的设定精度，但不等于证明 Euler 在所有开关瞬态下稳定，也不等于硬件能够在 200 ns 内完成一次推断。[pdf:E07]（物理页 7，Table II）[pdf:E08]（物理页 8，Table IV 与 Eq. (12)）

## § 7 — 实验设计与结论

**问题 1：少量数据下能否准确复现硬件波形？ →** 作者在 1 kW multilevel DAB 原型上记录 \(v_p,v_s,i_L\)，示波器采样为 8 ns/point；in-domain 条件是 \(V_1=200\,\mathrm{V}\)、\(V_2\in[80,120]\,\mathrm{V}\)、\(f_s=20\,\mathrm{kHz}\)、\(L_k=157\,\mu\mathrm{H}\)，共 1000 条稳态电流序列。训练/测试/验证只用 10/90/900 条，即训练数据为 1%。[pdf:E07]（物理页 7，Table II、Fig. 10 与 Section IV-A）[pdf:E08]（物理页 8，Table IV）**答案：** PA-RNN 在 unit-gain、step-down 和 step-up 波形上比 piecewise、LSTM 和 PL-PINN 更贴近硬件测量；但图形证据主要是视觉贴合，定量结论应看 Table VI。[pdf:E09]（物理页 9，Fig. 13）

**问题 2：训练域外能否不重训？ →** 另采 200 条 out-of-domain 序列，\(V_1=150\,\mathrm{V}\)、\(V_2\in[70,80]\,\mathrm{V}\)、额定功率 600 W，其余未列参数沿用 in-domain；这些数据只进入最终 validation。作者直接改变 Fig. 12 的输入电压，不为 PA-RNN 添加训练。[pdf:E07]（物理页 7，Table III）**答案：** 在展示的四组工况中，PA-RNN 波形最接近硬件；out-of-domain MAE 为 \(0.139\pm0.056\,\mathrm{A}\)，低于 piecewise 的 \(0.338\pm0\,\mathrm{A}\)、GRU 的 \(0.604\pm0.154\,\mathrm{A}\) 和 PL-PINN 的 \(0.548\pm0.162\,\mathrm{A}\)。[pdf:E10]（物理页 10，Fig. 14 与 Table VI）

**问题 3：优势是否只是一次随机训练？ →** 每个算法重复 10 次，比较两种 in-domain 划分和 out-of-domain MAE。低数据划分下，PA-RNN 为 \(0.160\pm0.004\,\mathrm{A}\)，PL-PINN 为 \(0.746\pm0.047\,\mathrm{A}\)，作者据此报告 78.6% 改善；70:20:10 划分下二者分别为 \(0.133\pm0.005\,\mathrm{A}\) 与 \(0.531\pm0.043\,\mathrm{A}\)，作者报告 75.0% 改善，并称 Student’s t-test 支持最佳表现。[pdf:E10]（物理页 10，Fig. 15 与 Table VI）**答案：** 在本文数据与实现中，优势跨随机重复和数据量保持；但正文没有给出 t statistic、自由度或精确 \(p\) 值，无法从 PDF 独立复核显著性计算。

**问题 4：对初始参数与网络规模是否敏感？ →** 作者扫描初始 \(L_k=117\)–\(197\,\mu\mathrm{H}\)、LN-GRU 层数和每层神经元数。**答案：** 图中 in-domain 与 out-of-domain MAE 变化均小于 \(0.03\,\mathrm{A}\)，作者据此认为模型对这三个 hyperparameter 稳健。[pdf:E11]（物理页 11，Fig. 16 与 Section V-E）

不得外推的范围包括：只验证一个 DAB 拓扑、一种 TPS 调制、一台硬件和主要由电压变化构成的 out-of-domain；没有跨器件批次、温度、老化、故障、负载瞬态或拓扑迁移实验。没有 FPGA、HIL 或 EMT 实时闭环实验；没有报告 FPGA 资源、时序或实时步长。

## § 8 — Take-aways

**5 句话。**  
1. PA-RNN 把离散电路方程做成 recurrent core，而不是仅用 physics loss 约束黑箱网络。[pdf:E05]（物理页 5，Fig. 5）  
2. 并联 LN-GRU 学习物理模型未覆盖的 residual，使名义模型能贴近真实硬件波形。[pdf:E04]（物理页 4，Fig. 4）  
3. 在本文 1000 条 in-domain 序列中只用 10 条训练，PA-RNN 的 MAE 为 \(0.160\pm0.004\,\mathrm{A}\)。[pdf:E08]（物理页 8，Table IV）[pdf:E10]（物理页 10，Table VI）  
4. 在 200 条电压域外序列上无需重训，报告 MAE 为 \(0.139\pm0.056\,\mathrm{A}\)。[pdf:E07]（物理页 7，Table III）[pdf:E10]（物理页 10，Table VI）  
5. 论文证明了 CPU/PyTorch 上的离线建模和硬件波形验证，却没有证明 FPGA/HIL/EMT 实时执行。

**3 句话。**  
PA-RNN 的主要贡献是把“已知动力学”和“未知残差”分工，而不是让一个网络同时学习两者。1 kW DAB 实验支持其在少数据和有限电压域外条件下优于所选 baselines。[pdf:E11]（物理页 11，Conclusion）最重要的未决点是：自由 residual 相加后，最终输出是否仍能被称为严格 physics-consistent。

**1 句话。**  
这是一种用物理递推降低学习负担、再用神经残差补偿模型失配的时域建模框架，实验证据有力但“硬物理一致性”和“实时 FPGA 可部署性”仍未闭合。

## § 9 — 最脆弱的假设

最脆弱的假设是：**LN-GRU 学到的 residual 足够小且足够良性，不会抵消 physics core 的守恒结构，因此两个输出相加后的最终预测仍可视为 physically consistent。**

论文确实把 KVL/Euler 递推硬编码进 physics core，但 Fig. 4 的最终输出是 \(o(z)=\phi(z)+\sigma(z)\)，其中 \(\sigma(z)\) 来自自由的 LN-GRU；训练 loss 只惩罚波形回归误差，没有约束最终输出满足 Eq. (9) 的 differential residual。[pdf:E04]（物理页 4，Fig. 4）[pdf:E06]（物理页 6，Eqs. (7)–(8) 与 Fig. 9）因此，基于证据的推断是：physics core 本身保持所选物理，并不自动等价于整个 PA-RNN 输出严格保持该物理。

这个假设在真实装置中可能因 dead time、器件压降、磁性饱和、温升导致的 \(R_L/L_k\) 漂移、寄生振荡或测量相位误差而失效。残差网络可能通过一个数值上准确、但在能量/KVL 意义上不合法的修正去追踪波形。论文给出的支持是同一硬件上低 MAE、有限电压域外波形和 hyperparameter sensitivity；缺少的是对总输出的 KVL residual、能量误差、长时滚动漂移和结构变化下的检验。[pdf:E09]（物理页 9，Fig. 13）[pdf:E10]（物理页 10，Figs. 14–15）

若这一假设不成立，论文最核心的区分——PA-RNN 比 physics-in-loss 更“严格物理一致”——就会削弱为“一个带物理先验的高精度 residual model”。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 1 kW 平台，而是“10 条训练序列是否足以带来无重训域外优势，同时保持总输出物理残差低”。

- **数据：** 从一台可获得的 DAB 或已有示波器记录中固定拓扑与 TPS，采集至少 10 条训练序列、约 90 条 early-stopping 序列，并保留两组 validation：训练电压范围内和一个未参与训练的输入电压。每条记录同步保存 \(V_1,V_2,s_{\mathrm{pri}},s_{\mathrm{sec}},i_L\)。
- **实现：** 复现 Eq. (11) 的 Euler physics core，使用一层 48-neuron LN-GRU residual；同时实现同规格 GRU、piecewise model 和 PL-PINN。训练顺序、MSE、Adam learning rate 0.001 与 L2 regularization 0.001 按 Table IV。[pdf:E08]（物理页 8，Table IV）
- **测量：** 除 waveform MAE 外，计算最终预测代回 Eq. (9) 后的离散 KVL residual，并记录滚动多个开关周期后的 drift；所有模型至少重复 10 次。
- **支持标准：** PA-RNN 在 in-domain 与 out-of-domain 都显著低于 GRU/PL-PINN 的 MAE，out-of-domain 不重训，同时其总输出 KVL residual 不高于纯 physics core 的预定容限。
- **反驳标准：** PA-RNN 只能靠显著增大的 KVL residual 获得低 MAE，或者 out-of-domain MAE/长时 drift 接近纯 GRU，便反驳“architecture 同时带来物理一致和可靠外推”的核心 claim。

论文未报告公开代码或数据链接，所以该复现需要自有波形或向作者取得数据；这是复现成本中的主要不确定项。

## § 11 — 最强反例设计

最强反例不是再换一组 \(V_1,V_2\)，而是构造**波形可以被自由 residual 拟合、但该 residual 会系统性违反物理闭合**的工况。

具体做法是：在 nominal 温度和电流下训练 PA-RNN，然后把磁件推入明显的电流相关 \(L_k(i_L)\) 区域，并同时改变 dead time 或器件压降，使论文 Eq. (9) 的常参数线性物理 core 有意失配；全程不重训。比较三种模型：原 PA-RNN、只允许学习 \(R_L,L_k\) 等物理参数的模型、以及把 learned correction 限制在 KVL/能量守恒可行集内的模型。评价 waveform MAE、Eq. (9) residual、周期能量误差和长时 drift。

如果原 PA-RNN 仍有最低 MAE，却出现最大的 KVL residual 或非物理能量漂移，就会给出一个具体替代解释：论文观测到的“物理一致性”其实来自测试分布内的波形贴合，而不是最终输出的结构保证。如果原 PA-RNN 在这种结构失配下也同时维持低 MAE、低物理 residual 和稳定滚动，则该反例失败，反而加强论文 claim。

## § 12 — Follow-up Research Idea

在 power electronics 领域，高影响结果通常需要的不只是 benchmark MAE，还要有跨工况/跨硬件的可复现实验、物理边界清楚的稳定性或误差解释，以及能落到实时控制/仿真的资源和时序证据。本文完成了单台硬件的波形与算法比较，但尚未完成这些更强闭环。

**候选想法：把“自由波形 residual”改成“守恒可行集内的可学习 constitutive correction”。** 这不是在 PA-RNN 后面再加一个模块，而是改变学习对象：网络不再直接给状态加任意修正，而只学习不确定的元件关系，例如 \(L_k(i,T)\)、\(R_L(T)\)、dead-time 等效电压或寄生支路参数；这些量再进入同一个 KVL/能量一致的 integrator，保证最终状态仍由物理算子产生。

（a）驱动需求是既要吸收真实硬件的 model discrepancy，又不能让追求低 MAE 的 residual 破坏守恒。  
（b）研究价值在于把“物理 core 可解释”升级为“最终输出可审计”，并能同时回答何时可外推、何时必须重新辨识。  
（c）可借鉴 differentiable circuit simulation、port-Hamiltonian systems、constrained neural ODE 和 uncertainty-aware system identification。  
（d）第一个证伪实验就是第 11 节的结构失配工况：若受约束 correction 无法在相近参数量下同时降低 waveform MAE 与物理 residual，或其域外性能显著差于原 PA-RNN，则想法被证伪。  
（e）与本文的实质区别是，本文让 LN-GRU 直接补输出；候选方法只让网络改变物理模型内部可解释的 constitutive relations，最终轨迹始终由守恒结构推进。

由于本次只使用指定 PDF、没有扩展检索相关全文，这一方向仅是证据约束下的候选判断，不声称 novelty。首个工程里程碑应同时报告 CPU/GPU 与 FPGA 的 latency、throughput、numeric format、resource utilization 和可持续实时步长；否则不能把“可由 HLS 部署”升级为实时 EMT/HIL 能力。
