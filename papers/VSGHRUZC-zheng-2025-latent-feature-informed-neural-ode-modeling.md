# Latent-Feature-Informed Neural ODE Modeling for Lightweight Stability Evaluation of Black-Box Grid-Tied Inverters

- 作者：Jialin Zheng；Zhong Liu；Xiaonan Lu
- 出处：IEEE Transactions on Power Electronics（由 DOI 身份确定；源 PDF 页眉未给出正式卷、期、页码）
- 年份：2025
- DOI：10.1109/TPEL.2025.3631402
- Zotero key：VSGHRUZC
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

【论文直接陈述】这篇论文要解决的是：在不知道 grid-tied inverter（GTI）内部拓扑、控制器和参数的黑盒条件下，能否只用少量时域扰动轨迹，学习一个既能预测非线性大信号暂态、又能在线性化后给出小信号特征值的统一模型。传统白盒状态空间法依赖厂商通常不公开的控制与参数；阻抗/Nyquist 黑盒法虽不需要内部模型，却只在测量时的工作点附近有效，工作点一变就要重新扫频和建模。论文将问题压缩为“从稀疏轨迹辨识一个可微的连续时间向量场”，并提出 latent-feature-informed neural ODE（LFI-NODE）：用单个 continuous-time neural network 表示系统 ODE，再以轨迹附近估计的 Jacobian 约束训练。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

重要性不只在于少做几次实验。若黑盒模型只能复现波形却不能可靠地给出平衡点附近的特征值，它仍不能回答“这个工作点稳定吗、主导模态在哪里”这一工程问题；反过来，若模型只会拟合各工作点的局部阻抗，它又无法复用跨工作点的大信号信息。论文报告其 GFM inverter 案例仅使用 48 条短暂态轨迹，并声称轨迹误差达到百分之一量级、特征值误差达到十分之一量级，相比基线低一至两个数量级。[pdf:E01]（PDF 物理页 1，Abstract）因此，论文真正追求的价值是把时域轨迹预测和小信号稳定性分析放到同一个可微 surrogate 中，而不是仅做一个更小的 waveform predictor。

## § 2 — 前人工作与不足

【论文对相关工作的归纳】第一类前人方法是白盒 state-space eigenvalue analysis。它可以直接线性化系统 ODE 并检查特征值，物理解释清楚，但前提是知道逆变器内部 governing equations、控制结构与参数；商业设备的专有信息使这个前提经常不成立。[pdf:E01]（PDF 物理页 1，Introduction）

第二类是基于外部扰动测量的 impedance/Nyquist 方法。它适合黑盒设备，但每个阻抗模型来自某一工作点的局部线性化；工作条件变化会触发新的测量—建模循环。论文进一步把数据驱动替代法分为两支：RNN/NARX 一类离散时间网络容易强调大信号轨迹拟合，却没有显式连续向量场，难以直接解析线性化得到 \(A,B\)；frequency-domain NN 则学习“工作点到局部阻抗”的复合映射，局部模型之间缺少共享的内在动力学，跨工作点泛化需要大量样本。论文引用的近期 impedance-profile 方法通常需要超过 1000 个由专用扫频设备测得的阻抗谱。[pdf:E01]（PDF 物理页 1，Introduction）[pdf:E02]（PDF 物理页 2，Section II 与 Fig. 1）

不足的根因不是“前人没有加 Jacobian loss”这么简单，而是学习对象选错了层级：离散网络学习一步到下一步的映射，频域网络学习大量局部解之间的映射；两者都没有把“所有工作点共享的连续时间 ODE”作为首先要识别的对象。LFI-NODE 的实质变化，是让每条轨迹都更新同一个全局向量场，再从该向量场的局部导数回到传统小信号工具。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Unified-Intrinsic-Modeling Paradigm）

## § 3 — 重建作者的思考路径

【基于证据的推断】在不预设本文贡献的情况下，可以这样重建作者的思考路径：

1. 商业 GTI 的稳定性分析不能依赖内部控制器，但只做外部 impedance sweep 又会在工作点变化时重复付出测量成本。[pdf:E01]
2. 不同工作点的局部模型并非毫无关系；它们应当都是同一个非线性连续系统在不同平衡点的线性化。如果直接辨识这个共享的向量场，一条轨迹的信息就可能迁移到多个工作点。[pdf:E02]
3. 普通 NODE 已提供可积分、可自动微分的连续向量场，适合大信号轨迹建模；但有限容量和以 trajectory MSE 为主的训练会优先照顾幅值较大的暂态，平衡点附近决定特征值的细小斜率误差可能被淹没。[pdf:E03]（PDF 物理页 3，Section III-B）
4. 因此，需要从每条轨迹的稳态邻域提取一个紧凑的小信号监督量。最直接的量是局部 Jacobian：用邻域内多点的状态偏差与导数做 least-squares，再把所得 \(J_{\mathrm{ref}}\) 作为 regularizer 的目标。[pdf:E03]（PDF 物理页 3，Eq. 5–7）
5. 最后，用一个 loss 同时约束全局轨迹与局部切空间，使 learned ODE 既能积分出暂态，又能在平衡点线性化后给出特征值。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Eq. 8–11）

这一路径把“数据少”重新解释为“每个样本应服务同一个 intrinsic model”，把“小信号信息弱”重新解释为“需要显式监督局部一阶导数”。

## § 4 — 核心 Intuition

把所有扰动轨迹看作同一个连续动力系统在不同初值和输入下的运动，而不是为每个工作点各学一个模型。普通轨迹 loss 告诉网络“整条路怎么走”，从稳态邻域提取的 Jacobian loss 则告诉它“终点附近地形的斜率是什么”；两者合起来，一个模型才可能同时复现大信号暂态和小信号特征值。[pdf:E03]（PDF 物理页 3，Fig. 2 与 Eq. 8–11）所谓 latent feature 在本文中不是另一个 hidden embedding，而是从观测轨迹中估计、用于监督的局部 Jacobian。

## § 5 — 具体方法与完整 Pipeline

以论文中的 full-order GFM inverter 为例，完整 pipeline 如下。

1. **采集轨迹。** 在 Typhoon HIL 604 上实时仿真 GFM inverter，扫动 PCC voltage magnitude 与 frequency reference，并对两者施加阶跃扰动。benchmark 有 13 个 state variables 和 2 个 external inputs，所以网络接收拼接后的 15 维输入并输出 13 维状态导数；论文共生成 48 条 normalized trajectories，每条 1.0 s，原始采样率 50 kHz。[pdf:E04]（PDF 物理页 4，Section IV-A 与 Fig. 3）
2. **预处理。** 对轨迹使用 zero-phase low-pass filter 抑制高频噪声，再下采样到每条 5000 个训练点。零相位滤波的用意是避免在数值求导前额外引入 phase shift。[pdf:E03]（PDF 物理页 3，Section III-B）[pdf:E04]（PDF 物理页 4，Section IV-A）
3. **构造全局 NODE。** 将 \(z=[x^\mathsf{T},u^\mathsf{T}]^\mathsf{T}\) 输入多层 neural network \(f_{\mathrm{NN}}\)，网络输出 \(\dot{x}\)；ODE solver 从当前状态积分到下一时刻。实验中的三个对比模型都采用三层 tanh 网络、64–128–128 hidden neurons；LFI-NODE 与普通 NODE 使用支持 automatic differentiation 的 `dlode45`，relative tolerance 为 \(10^{-7}\)。[pdf:E02]（PDF 物理页 2，Eq. 2–4）[pdf:E04]（PDF 物理页 4，Section IV-A）
4. **从每条轨迹提取 latent perturbation feature。** 在 \(\|\dot{x}(t)\|\) 最小的时间段取状态均值得到 \(x_{\mathrm{ss}}\)。选取其附近 \(N\) 个样本，以 first-order finite difference 计算 \(\dot{x}_i\)，组成 \(\Delta X\) 与 \(\Delta\dot{X}\)，再做 least-squares：
   \[
   J_{\mathrm{ref}}=\Delta\dot X\,\operatorname{pinv}(\Delta X).
   \]
   多点拟合比只用少量点更能平均噪声，但其可靠性仍取决于数值求导、邻域选择与 \(\Delta X\) 的条件数。[pdf:E03]（PDF 物理页 3，Eq. 5–7）
5. **联合训练。** ODE solver 产生预测轨迹 \(\hat{x}(t)\)，trajectory MSE 构成 \(L_{\mathrm{data}}\)；在预测平衡点对 \(f_{\mathrm{NN}}\) 自动微分得到 \(J_{\mathrm{NN}}\)，其与 \(J_{\mathrm{ref}}\) 的 Frobenius-norm difference 构成 \(L_{\mathrm{jac}}\)。总损失为 \(L_{\mathrm{total}}=\lambda_1L_{\mathrm{data}}+\lambda_2L_{\mathrm{jac}}\)。训练用从每条轨迹抽取的 40-step sliding windows，并运行 1200 iterations。[pdf:E03]（PDF 物理页 3，Eq. 8–11）[pdf:E04]（PDF 物理页 4，Section IV-A/B）
6. **稳定性评估。** 对新输入条件先用 learned ODE 预测大信号响应，再在稳定点线性化 learned vector field、计算 eigenvalues。论文用 normalized input pairs \((0.5,0.9)\) 与 \((0.8,1.2)\) 分别代表 stable 与 unstable case，并以 Typhoon HIL 结果为 ground truth 比较 LFI-NODE、普通 NODE 与 NARX。[pdf:E04]（PDF 物理页 4，Fig. 4–5 与 Section IV-B）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有形式化数学，但需要区分“模型构造公式”和“可证明的误差界”：Eq. 2–11 定义模型与训练目标，Appendix 的 Eq. 12–20 只分析从带噪轨迹估计 \(J_{\mathrm{ref}}\) 的误差，并没有证明训练后的 NODE 必然恢复真实 ODE 或真实稳定边界。

**第一步：把未知 inverter 写成连续向量场。**

\[
\dot{x}=f(x,u;\theta), \qquad
f_{\mathrm{NN}}(z)=W_n\sigma(\cdots \sigma(W_1z+b_1)\cdots)+b_n,
\]
\[
x_{k+1}=x_k+\operatorname{ODESolver}(f_{\mathrm{NN}},x_k,u_k,\Delta t_k).
\]

其中 \(x\) 是 state vector，\(u\) 是 external input，\(\theta\) 是被网络权重吸收的未知动力学参数。intuition 是：网络不直接猜下一采样点，而是输出此刻的“运动速度” \(\dot{x}\)，再由数值积分器生成轨迹；因此这个网络可以在任一平衡点被微分。[pdf:E02]（PDF 物理页 2，Eq. 2–4）

**第二步：从轨迹邻域恢复小信号 Jacobian。**

在平衡点 \(x_{\mathrm{ss}}\) 附近，一阶 Taylor expansion 给出

\[
\Delta \dot{x}\approx J\Delta x,\qquad
\Delta X=[\Delta x_1,\ldots,\Delta x_N],\qquad
\Delta\dot X=[\dot{x}_1,\ldots,\dot{x}_N].
\]

于是 \(J\Delta X\approx\Delta\dot X\)，least-squares 解为

\[
J_{\mathrm{ref}}=\Delta\dot X\,\operatorname{pinv}(\Delta X).
\]

普通语言解释：如果在平衡点附近沿多个方向轻推系统，状态偏差是 \(\Delta X\)，速度变化是 \(\Delta\dot X\)，Jacobain 就是把前者映射到后者的最佳线性矩阵。`pinv` 是 Moore–Penrose pseudoinverse，允许样本矩阵不是方阵。[pdf:E03]（PDF 物理页 3，Eq. 5–7）

**第三步：同时约束轨迹和局部斜率。**

\[
L_{\mathrm{data}}=\frac1T\sum_{k=1}^{T}\|\hat{x}(t_k)-x(t_k)\|_2^2,
\]
\[
J_{\mathrm{NN}}=
\left.\frac{\partial f_{\mathrm{NN}}(x,u)}{\partial x}\right|_{x=\hat{x}_{\mathrm{ss}}},
\qquad
L_{\mathrm{jac}}=\|J_{\mathrm{NN}}-J_{\mathrm{ref}}\|_F^2,
\]
\[
L_{\mathrm{total}}=\lambda_1L_{\mathrm{data}}+\lambda_2L_{\mathrm{jac}}.
\]

\(L_{\mathrm{data}}\) 约束整条 nonlinear trajectory，\(L_{\mathrm{jac}}\) 约束 equilibrium neighborhood 的 local tangent space。后者相当于告诉网络：即使两条预测轨迹肉眼相近，平衡点附近的一阶导数也不能随意，因为 eigenvalues 正是由这个局部线性化决定。[pdf:E03]（PDF 物理页 3，Eq. 8–11）

**第四步：带噪 Jacobian 估计的上界。** 论文设测得状态 \(X_m=X+\eta\)，并把数值求导带来的噪声记为 \(\dot{\eta}\)。若每个样本满足 \(\|\eta(t_i)\|_2\le\sigma_x\)、\(\|\dot\eta(t_i)\|_2\le\sigma_{\dot x}\)，则

\[
\|E_x\|_2\le\sqrt{N}\sigma_x,\qquad
\|E_{\dot x}\|_2\le\sqrt{N}\sigma_{\dot x},
\]
\[
\|J_{\mathrm{ref}}-J_*\|_2
\le
\kappa(\Delta X)
\left(
\frac{\sqrt N\sigma_{\dot x}}{\|\Delta X\|_2}
+
\frac{\sqrt N\sigma_x}{\|\Delta X\|_2}\|J_*\|_2
\right).
\]

这里 \(\kappa(\Delta X)=\|\Delta X\|_2\|\operatorname{pinv}(\Delta X)\|_2\) 是 condition number。该式的直觉是：激励方向越单一，\(\Delta X\) 越 ill-conditioned；轨迹变化越小、求导噪声越大，估计的 Jacobian 越不可信。零相位滤波只能降低噪声项，不能修复缺少独立激励方向的问题。[pdf:E06]（PDF 物理页 6，Appendix Eq. 12–20）

## § 7 — 实验设计与结论

**问题 1：一个统一 continuous-time model 能否同时预测大信号轨迹和小信号 eigenvalues？ →** 作者在 Typhoon HIL 604 上构建 full-order GFM benchmark，训练结构相同的 LFI-NODE、普通 NODE 与 NARX，并在两个未见 normalized input pairs 上比较 \(V_d\)、\(I_q\) 轨迹和稳定点 eigenvalues。**→ 论文给出的答案：** Fig. 5 中 LFI-NODE 与 HIL reference 最接近，普通 NODE 次之，NARX 偏差最大；其中一个条件 stable、另一个 unstable。[pdf:E04]（PDF 物理页 4，Fig. 3–5）

**问题 2：Jacobian guidance 是否改善精度和样本效率？ →** 三个模型采用相同 15-input/13-output、64–128–128 tanh 网络，并在 48 条轨迹上训练 1200 iterations；普通 NODE 与 LFI-NODE 的主要区别是 latent Jacobian term，因此普通 NODE 构成一个接近的 ablation。**→ 论文给出的答案：** Fig. 6 显示 LFI-NODE training error 至少低一个数量级，large-signal trajectory RMSE 与 small-signal eigenvalue absolute error 相比基线低约两个数量级。图中的误差按 state variable 展示，但论文没有报告跨随机种子的均值、方差或置信区间。[pdf:E04]（PDF 物理页 4，实验设置）[pdf:E05]（PDF 物理页 5，Fig. 6 与 Section IV-B）

**问题 3：数值求导和 Jacobian fitting 在 measurement noise 下是否仍可用？ →** 作者在 48 条 clean trajectories 上分别加入标准差 \(\sigma_x=1\times10^{-4}\)、\(5\times10^{-4}\)、\(2\times10^{-3}\) 的 zero-mean Gaussian white noise，其他训练配置不变。**→ 论文给出的答案：** 最高噪声下，时域预测主要表现为平滑度下降，eigenvalue points 仍靠近 reference；作者称误差位于 Appendix 的理论 bounds 内。[pdf:E05]（PDF 物理页 5，Fig. 7–8 与 Section IV-C）需要注意，这个上界约束的是 \(J_{\mathrm{ref}}\) 的估计误差，不是最终 neural ODE 的泛化误差。

**工程证据边界。** 论文报告了 Typhoon HIL 604、DSP controller、oscilloscope、Intel i7-14700、MATLAB R2024b/Deep Learning Toolbox、50 kHz 原始采样和 time-domain real-time HIL testing。[pdf:E04]（PDF 物理页 4，Fig. 3 与 Section IV-A）FPGA 实现、FPGA 资源占用、fixed-point 量化、推理 latency：**未报告**。HIL model 的 real-time solver、仿真步长、I/O latency、overrun 情况和具体硬件映射：**未报告**。除“实时 HIL 仿真”和 50 kHz 数据采样外，online execution cadence 与闭环部署方式：**未报告**。论文称采样用于捕获 fast electromagnetic transients，但 switching frequency、EMT solver、开关级模型时间步与误差控制：**未报告**；其讨论还明确说明本文 HIL 数据提供的是 average-model dynamics，而非物理功率级 switching waveform 的直接验证。[pdf:E05]（PDF 物理页 5，Section IV-D）因此，本实验支持“在一个 HIL GFM benchmark 上的数据效率与精度”，不支持“已在真实商业黑盒 inverter、FPGA 或一般 EMT 平台上部署”。

## § 8 — Take-aways

**5 句话**

1. LFI-NODE 用一个可微 continuous-time neural network 学习黑盒 inverter 的统一 ODE，而不是为每个工作点建立独立局部模型。
2. 它从轨迹稳态邻域用 least-squares 提取 \(J_{\mathrm{ref}}\)，并把 Jacobian matching 加入 trajectory loss。
3. 这使同一模型既能用 ODE solver 预测大信号暂态，又能在平衡点线性化后计算小信号 eigenvalues。
4. 在一个 Typhoon HIL 604 的 13-state GFM 案例中，48 条轨迹足以让论文报告的轨迹和特征值误差优于普通 NODE 与 NARX 一至两个数量级。[pdf:E04][pdf:E05]
5. 但结论尚依赖 full-state access、单一拓扑与 HIL average-model ground truth，真正商业黑盒、partial observability、跨设备迁移和实际部署仍未闭合。

**3 句话**

1. 论文最有价值的点不是“用了 NODE”，而是用局部 Jacobian supervision 补上 trajectory fitting 对小信号斜率不敏感的缺口。
2. 实验在稀疏 HIL 轨迹上同时改善波形与 eigenvalues，但证据仍局限于一个 GFM benchmark、两个 unseen input conditions 和一次报告的训练结果。
3. 若拿不到完整 state vector，本文的 \(J_{\mathrm{ref}}\) 与稳定性结论就需要改写成 partial-observation 下的可辨识性问题。

**1 句话**

LFI-NODE 证明了“全局轨迹 + 局部 Jacobian”是连接黑盒时域辨识和小信号稳定性分析的一条很有力的路径，但尚未证明它在真正不可观测的商业 inverter 上仍能给出可信稳定性判断。

## § 9 — 最脆弱的假设

最脆弱的假设是：**稳定性相关的完整状态能够被访问，且这些观测足以在每个目标平衡点附近可靠估计 full-state Jacobian。** 方法的网络有 13 个状态输出，\(J_{\mathrm{ref}}\) 由状态偏差和状态导数直接计算，最终 eigenvalues 又来自 learned state-space Jacobian；若只测得到 PCC voltage/current，而内部 controller、PLL、filter 或保护状态不可见，那么相同的外部轨迹可能对应不同的内部 realizations 和不同的隐藏模态。[pdf:E03]（PDF 物理页 3，Eq. 5–11）

【论文直接陈述】作者在 Discussion 中承认，对许多 existing or fully black-box systems，某些 variables 可能无法访问；transformer、encoder–decoder 与 latent mapping 可用于 partially observable systems，但这些结构通常 data-hungry，和 converter 的 data-scarce 条件冲突。论文只把 LFI-NODE 与 Latent ODE 结合列作 future work，没有给出 partial-observation 实验。[pdf:E05]（PDF 物理页 5，Section IV-D）

【基于证据的推断】如果 full-state access 不成立，当前核心贡献不是“精度下降一点”，而是稳定性对象本身可能不可辨识：输出轨迹拟合正确并不保证隐藏 eigenmodes 正确。其次，即使状态可测，Eq. 20 还要求 \(\Delta X\) 有良好 condition number；过弱或共线的扰动会让 Jacobian error bound 放大。[pdf:E06] 因而论文对这个关键假设提供的是单一 fully observed HIL benchmark 与加性 Gaussian noise 证据，尚缺少隐藏状态、传感器缺失、跨控制结构和低可激励模态的验证。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 HIL 平台，而是“Jacobian loss 是否真的在不牺牲 trajectory accuracy 的情况下改善 unseen operating point 的 eigenvalues”。

1. **数据。** 按论文引用的 GFM average model 建一个 13-state 仿真，扫 PCC voltage magnitude 与 frequency，生成 48 条 1.0 s step-response trajectories；若无法得到完全相同的 benchmark 参数，就明确将其作为 mechanism reproduction，而非数值复刻。论文 PDF 未报告公开代码、公开 dataset 或随机种子。
2. **实现。** 用相同 64–128–128 tanh 网络实现两个模型：NODE 只用 \(L_{\mathrm{data}}\)，LFI-NODE 增加由稳态邻域估计的 \(L_{\mathrm{jac}}\)。使用相同 optimizer、window sampling、ODE solver tolerance 和训练预算；至少运行 5 个随机种子，避免把一次收敛偶然性当成结论。
3. **测量。** 在两个未参与训练的 stable/unstable input pairs 上同时测 trajectory RMSE、eigenvalue MAE、稳定/不稳定分类是否正确，并记录 \(\kappa(\Delta X)\)。再加入论文的三档 Gaussian noise，观察误差与 condition number 的关系。
4. **支持标准。** 若 LFI-NODE 在多数随机种子和两个 held-out conditions 上保持与 NODE 相当或更低的 trajectory RMSE，同时显著降低 eigenvalue MAE，且 stable/unstable 判断一致，则支持核心 mechanism。
5. **反驳标准。** 若优势只出现在某个随机种子、某个 window/权重设置，或 trajectory RMSE 改善而 eigenvalue 排序与稳定性符号仍错误；又或者控制 \(\kappa(\Delta X)\) 后 Jacobian loss 不再有增益，则论文的核心解释受到反驳。

这个复现实验不需要复刻 FPGA、HIL 或 switching EMT。它验证的是算法机制；若目标变成实时工程部署，论文未报告的 solver step、latency、resource utilization 与 closed-loop timing 必须另行定义。

## § 11 — 最强反例设计

最强反例是构造一对 **training-output indistinguishable、internal-stability different** 的系统。具体做法是：让两个 GFM 模型在训练用的 PCC voltage/current 及可见状态上产生几乎相同的 48 条轨迹，但在其中一个模型里加入一个弱耦合、训练扰动无法激发的内部 controller mode；该 mode 在训练区间内不可观测，却在某个 held-out operating point 穿过虚轴。只把相同可见通道交给 LFI-NODE，然后检查它是否对两个系统给出相同的 learned Jacobian/eigenvalues。

如果模型对两者输出相同稳定性判断，那么“从黑盒 trajectory data 得到 rigorous stability evaluation”的 claim 就必须加上 observability/identifiability 条件；如果它能区分，则要证明区别来自可重复的可见信息，而不是训练噪声或偶然初始化。这个反例比单纯增加 Gaussian noise 更强，因为 Eq. 20 的 noise bound 无法解决不存在于观测中的 mode；它攻击的是信息是否存在，而不是 estimator 是否足够鲁棒。[pdf:E05]（PDF 物理页 5，partial observability discussion）[pdf:E06]（PDF 物理页 6，noise-bound scope）

## § 12 — Follow-up Research Idea

在 power electronics / control 领域，高影响工作通常不仅要求更低 benchmark error，还要求明确的稳定性对象、可验证的数学边界、多拓扑或多设备证据、physical/HIL validation、可复现实现以及对实时部署成本的交代。本文已经有 HIL 与误差界，但 full-state black-box 与真正 partial observation 之间仍有明显断层。

【候选研究想法，未做充分相关工作检索，不声称 novelty】把问题从“在部分观测下输出一个最可能的 ODE 与点估计 eigenvalues”改成 **identifiability-aware stability certification**：模型输出的不是唯一 Jacobian，而是所有与当前观测轨迹一致的 latent dynamics 所对应的稳定性集合；只有当这个集合全部位于稳定域时才给出稳定证书，否则返回“不可判定”并自动设计下一次最有信息量的安全扰动。

- **(a) 未满足的需求。** 商业 inverter 通常只能访问端口量，工程人员需要知道“现有数据是否足以支持稳定结论”，而不只是得到一个看似精确的 eigenvalue。
- **(b) 研究价值。** 它把黑盒稳定性评估从 point prediction 提升为带 epistemic boundary 的 certification，能显式避免隐藏不稳定 mode 被高精度波形拟合掩盖。
- **(c) 可借鉴工具。** 可结合 nonlinear observability / subspace identification 的可辨识性判据、set-membership estimation 或 reachability 的集合传播，以及 active experiment design 选择能改善 \(\Delta X\) condition number、同时满足安全约束的扰动；Neural ODE 仍作为共享的连续动力学表示。
- **(d) 第一个可证伪实验。** 使用第 11 节那对外部轨迹近似相同、内部稳定性不同的系统。新方法必须要么在现有数据下返回“不可判定”，要么设计一个安全扰动把两者分开；若它仍自信地给出同一个错误稳定结论，研究假设立即失败。
- **(e) 与本文的实质区别。** 本文假定可由测得 state trajectories 构造 \(J_{\mathrm{ref}}\)，并输出单一 learned Jacobian；新问题把“哪些稳定性结论可由有限端口观测唯一支持”放在模型拟合之前，允许诚实地拒绝给出无法由数据识别的 eigenvalue。

这不是在 LFI-NODE 后面再加一个 uncertainty head，而是改变成功标准：从“预测误差低”改为“稳定结论有可辨识性依据，证据不足时能拒答并主动获取证据”。
