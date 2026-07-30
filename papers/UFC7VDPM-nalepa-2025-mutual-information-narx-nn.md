# Mutual Information-Enhanced NARX-NN Digital Twins for Power Electronics in Smart Grid Applications — 中文精读证据卡

- 作者：Radosław Nalepa；Karol Najdek
- 出处：IEEE Transactions on Smart Grid，Vol. 16，No. 6，pp. 4421–4436
- 年份：2025
- DOI：10.1109/TSG.2025.3601021
- Zotero key：UFC7VDPM

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的问题不是“能否用神经网络拟合一个 Boost 变换器”，而是：能否从可测时序中系统地确定采样率、输入、延迟和记忆维数，构造一个既能看见 PWM 周期内动态、又足够轻量的 NARX-NN Digital Twin Instance（DTI），从而绕开实时求解开关电路微分方程的成本。论文以闭环电压控制、连续导通模式（CCM）的 Boost 变换器为对象，输出是电感电流估计 \(\hat i_L\)。作者把详细电磁暂态模型在嵌入式实时环境中的计算负担，和普通平均模型遗漏开关周期内信息，视为同一工程矛盾的两端。[pdf:E01]

这个问题对 converter-rich smart grid 有三层价值。第一，器件级模型若仍依赖变步长求解器，就很难大量复制并放进实时仿真、监测或诊断系统；本文的高保真数据生成本身就花费约 28 小时，而候选网络一次推理只需要数千次浮点运算。[pdf:E03] 第二，电感电流的纹波、控制引起的振荡和 CCM/DCM 边界行为发生在 PWM 周期内；只拟合平均量会抹去这些可能触发保护或影响控制的短时动态。第三，若输入和延迟由相关性、mutual information（MI）和相空间重构规则导出，而不是完全靠试错，模型结构至少有一部分可以追溯到时序依赖，而不只是一个不可解释的参数堆。

需要把论文的工程主张限定清楚：作者实际完成的是 MATLAB-SIMULINK 中的 DTI 建模、仿真验证和离线 transfer learning（TL），并给出计算量估算；没有把网络综合到 FPGA、没有报告定点位宽、流水线结构、资源占用或板上实测 latency。因此“适合 FPGA/ARM 实时部署”在本文中是基于 FLOPs 的可行性判断，不是硬件实现结论。[pdf:E10][pdf:E11]

## § 2 — 前人工作与不足

论文梳理的最相关路线有四类。已有 NARX 或动态神经网络能在不做数值积分的情况下表示功率变换器平均动态，但没有系统优化 delay 或 embedding，因而对 PWM 周期内行为和动态工况的泛化有限；用于 Boost 变换器 DCM/CCM 的 NARX-ANN 也主要建模平均模式。ML-EMT 的 FPGA HIL 路线追求高保真，但作者认为其 compactness 和 interpretability 不足。针对 IGBT 开关暂态的 ANN 模型能处理快速开关行为，却仍是缺少系统 delay 配置的黑盒。另有用 PSO 校准 physics-based DT 的工作，重点是长期可靠性而非本文关注的高时间分辨率动态和实验泛化。[pdf:E02]

作者声称的新意不是发明 NARX、MI、VIF 或 FNN 中的任何一个，而是把它们排成一条结构选择链：相关性与 Variance Inflation Factor（VIF）先去除明显冗余，self-Mutual Average Information（sMAI）选择采样率和反馈延迟，cross-MAI（cMAI）选择外生输入延迟，False Nearest Neighbours（FNN）选择 embedding dimension，最后才训练 NARX-NN。[pdf:E01][pdf:E09] 这一定位来自论文本身；本卡没有在论文之外做完整 novelty 检索，因此不把“首次”或“唯一”当成已独立核实的事实。

比“以前没考虑 MI”更准确的不足是：此前工程模型常把采样率、tap delay、输入变量和网络宽度一起当作超参数搜索，得到的网络即使误差小，也不容易解释它为什么需要这段记忆、为什么某个输入有用。本文试图先用时序统计和相空间几何压缩结构搜索空间，再让网络只学习剩余的非线性映射。不过，这种“可解释”主要是结构来源可追溯，不等于神经网络内部因果关系或安全边界已被解释。

## § 3 — 重建作者的思考路径

以下是基于论文背景和实验设计重建的推理路径，不是作者逐字陈述。

1. 详细 Boost 模型含开关、寄生参数、输入滤波和闭环控制，能够生成真实感较强的电流纹波，但实时重复求解代价高；先把任务改写成“用历史可测量量直接预测下一时刻电感电流”。[pdf:E03]
2. 普通 feedforward NN 没有记忆，而 NARX 可以显式接收过去的输入和过去的输出；于是关键不再是“要不要记忆”，而是“记多久、隔几步取样、需要几维”。
3. 固定 PWM 系统的状态不仅取决于负载和电压误差，也取决于当前位于开关周期的哪个相位；因此加入一个每周期 1 到 10 的 clock-like signal，把 250 kHz 数据采样与 25 kHz 开关周期对齐。[pdf:E06]
4. 可选信号很多且强共线，直接全部输入会放大冗余。先用相关系数、回归斜率和 VIF 做预筛选，再用 MI 检查非线性时间依赖，避免只保留线性相关性最高的量。
5. sMAI 曲线的局部极值给出采样率和反馈 delay 的候选，cMAI 给出每个外生输入相对 \(i_L\) 的 delay；FNN 再检查低维 delay vector 是否把不同状态错误地挤在一起。[pdf:E07][pdf:E08][pdf:E09]
6. 最后比较 4D/5D 和多种网络宽度，并用闭环而非仅 open-loop 表现筛选模型，因为递归预测中的小误差会反馈并累积。physics-based 输入在 open-loop 仍有竞争力、在 closed-loop 却没有泛化，这反过来支持保留 MI 选择出的控制和相位信息。[pdf:E10]

这条路径的核心改变，是把 NARX 的“历史窗口”从随手设置的超参数变成主要由数据结构分析确定的对象。代价是模型更依赖训练数据是否真的覆盖部署时会访问的动态吸引域。

## § 4 — 核心 Intuition

NARX-NN 不需要重建每个电路元件的微分方程，只要一组带延迟的可测信号能把当前动态状态“展开”出来，feedforward NN 就能学习从这个历史切片到下一时刻电感电流的映射。MI 决定哪些时间间隔仍携带有用而不过度重复的信息，FNN 决定需要多少个历史坐标才能避免把不同状态叠在一起，而 clock-like input 显式告诉网络当前 PWM 相位。[pdf:E01][pdf:E09] 因此，本文真正的机制不是“更大的网络”，而是先把时间结构组织对，再让一个小网络拟合。

## § 5 — 具体方法与完整 Pipeline

以论文的 Boost 变换器为例，完整 pipeline 如下。

1. **构造唯一目标和激励数据。** 高保真 SIMULINK/Simscape 模型的额定输入、输出电压分别为 50 VDC 和 100 VDC，输出功率点为 100 W、230 W、400 W，电感名义值为 670 \(\mu\text{H}\)，开关频率 25 kHz。负载电阻在 25–99.9 \(\Omega\) 间变化，并叠加 10 Hz–1 kHz、幅值 1.5 \(\Omega\) 的 beat components。完整序列为 9.24 s、2,309,999 个样本，去掉 12 ms startup 后使用 2,307,000 个样本；模型目标是 \(i_L\)。[pdf:E03]
2. **选择实时可得输入。** 作者从二十多个候选时序经预探索缩减后，以相关性、inclination angle 和 VIF 做八轮迭代。最终外生输入为
   \[
   \mathbf u=[i_{\mathrm{out}},\,v_{\mathrm{out,error}},\,t_{\mathrm{on}},\,clk]^\mathsf T ,
   \]
   其中 \(clk\) 是每个 PWM 周期取 1–10 的 clock-like signal。最终 VIF 均低于 10；动态电阻 \(v_{\mathrm{in}}/i_{\mathrm{out}}\) 因与 \(i_{\mathrm{out}}\) 冗余且实际需计算而被舍弃。[pdf:E06]
3. **用 sMAI 选择采样率与反馈延迟。** 作者在候选采样率上计算 \(i_L\) 的 sMAI，取 first local maximum 对应的 250 kHz，正好是开关频率的 10 倍；在该采样率下，sMAI 的 first minimum 为 \(\tau=5\)，即半个开关周期，用作 \(i_L\) feedback 的基本 delay。[pdf:E07][pdf:E08]
4. **用 cMAI 选择外生 delay。** \(i_{\mathrm{out}}\)、\(v_{\mathrm{out,error}}\)、\(t_{\mathrm{on}}\)、\(clk\) 的基本 delay 分别为 2、2、5、2 个样本。4D 时经 \(\tau_{\mathrm{md}}=(m_D-1)\tau\) 得到最大窗口 6、6、15、6；5D 时为 8、8、20、8。反馈 \(i_L\) 对应为 15 或 20 个样本。[pdf:E08]
5. **用 FNN 选 embedding dimension。** 对 delay-embedded point 计算相邻点从 \(m_D\) 到 \(m_D+1\) 维后的距离增量；FNN 比例稳定后选择 4D 和 5D 两个候选。4D 配三层、每层 17 个神经元，5D 配三层、每层 19 个神经元；输入和 feedback 都先经过 delay embedding，再进入 feedforward network。[pdf:E09]
6. **训练与闭环筛选。** 数据按索引固定分为 770,000 个训练样本、770,000 个验证样本和 767,000 个测试样本。训练使用 MATLAB 的 Levenberg-Marquardt、`mapminmax` 和 early stopping，先 open-loop 训练，再闭合 feedback 做 closed-loop 评估；作者试过 1,000 多种层宽、层数和 embedding 组合。[pdf:E05][pdf:E09][pdf:E10]
7. **仿真扰动和实验 TL。** 仿真测试包含 nominal、\(2.5K_P\)、\(C_{\mathrm{out}}-15\%\) 和 \(L-5\%\)。实验上先直接把仿真网络用于 80,000-sample test window，再用另一个 175,000-sample window 做 offline TL，最后回到同一 test window 比较。[pdf:E12][pdf:E13][pdf:E14]
8. **评估计算与部署路径。** 作者估算 3×19 网络为 2,548 FLOPs/step，在 250 kHz 下按 20% margin 需要约 0.796 GFLOPS；3×17 为 1,974 FLOPs/step、约 0.617 GFLOPS。[pdf:E10] 论文未实现 FPGA 数据通路、定点量化或多速率调度；8-bit、sparsification、FPGA/ASIC 都被列为后续部署路径，而非已完成结果。[pdf:E11]

## § 6 — 核心数学推导

### 6.1 Delay embedding：把一条波形变成“状态坐标”

对采样序列 \(X=(x_i)\)，论文定义
\[
\hat X_{\alpha}^{(m_D,\tau)}
=\langle x_{\alpha+(a-1)\tau}\mid a=1,\ldots,m\rangle .
\]
它的直观含义是：不直接观察所有电路内部状态，而是把同一可测量量在间隔 \(\tau\) 的 \(m_D\) 个时刻排成一个向量，用这段历史作为当前状态的代理。实时形成该窗口至少需要
\[
l_{\min}=(m-1)\tau+1
\]
个样本。[pdf:E05]

这依赖 Takens-style delay embedding 的思想，但论文实际系统有闭环、PWM discontinuity、噪声和外生输入，因此这里更适合把定理理解为结构启发，而不是已证明满足所有嵌入条件的严格保证。[pdf:E04]

### 6.2 Mutual Average Information：找“既不同又相关”的时间间隔

论文的 sMAI 为
\[
\operatorname{sMAI}(X_i,X_{i-\tau})
=\sum_{g=1}^{N}\sum_{h=1}^{N}P_{gh}(\tau)
\log_2\frac{P_{gh}(\tau)}{P_gP_h},
\qquad N=\sqrt[3]{l}.
\]
\(P_{gh}\) 是当前值与延迟值落入二维 bins 的联合概率，\(P_g,P_h\) 是边缘概率。值高表示延迟后的变量仍带有大量共同信息。作者用 sMAI 的 first local maximum 选择 250 kHz 采样率，用 first minimum 选择 feedback delay；把第二个序列换成另一个输入 \(Y_{i-\tau}\) 就得到 cMAI，用其 first minimum 选择外生 delay。[pdf:E07]

这里有一个重要区分：first minimum 作为 delay 是常见 heuristic，本文的数据给出了清晰曲线，但没有证明它对所有 converter 或非平稳工况都是最优；作者也明确说还需跨拓扑和工况验证。[pdf:E08] 同样，FNN 的 \(r_{\mathrm{tol}}=10\)、\(a_{\mathrm{tol}}=2\) 没有做 threshold sensitivity，因此 4D/5D 选择是否对阈值稳健仍未闭合。[pdf:E09]

### 6.3 FNN：检查维数是否把不同状态压在一起

若一个邻居从 \(m_D\) 维升到 \(m_D+1\) 维后距离变化过大，就被判为 false neighbour：
\[
\frac{|\,^{(m_D+1)}\delta_\alpha-\,^{(m_D)}\delta_\alpha|}
{\,^{(m_D)}\delta_\alpha}>r_{\mathrm{tol}}
\quad\text{或}\quad
|\,^{(m_D+1)}\delta_\alpha-\,^{(m_D)}\delta_\alpha|>a_{\mathrm{tol}}.
\]
论文取 \(r_{\mathrm{tol}}=10\)、\(a_{\mathrm{tol}}=2\)，再用
\[
\tau_{\mathrm{md}}=(m_D-1)\tau
\]
把基本 delay 转成整个 embedding window 的跨度。[pdf:E09] FNN 的物理直觉是：若 2D/3D 观察把本来不同的开关状态投影到同一区域，就需要增加历史坐标；当 FNN 接近稳定的低值，再增加维数只会增加冗余和噪声。

### 6.4 计算量与“可解释性”公式

作者把每个神经元的乘加、bias 和 activation 近似为 \(2\iota+2\) FLOPs，得到多层网络一次 forward pass 的估算式，并据此计算 3×19 和 3×17 两个模型的 GFLOPS 需求。[pdf:E10] 这只计算 arithmetic work，没有包含 memory access、delay buffer、activation 实现、接口和 FPGA pipeline stall，所以它是上板前的预算，不是 deadline 已满足的测量。

论文还从二阶连续系统经 backward finite difference 得到
\[
y_i=G(y_{i-\tau},y_{i-2\tau},\ldots;u_i,u_{i-\tau},u_{i-2\tau},\ldots),
\]
再用神经网络 \(F(\cdot)\) 近似 \(G(\cdot)\)，用来解释为什么显式 delay 与动态系统有关。随后定义 effort \(E(h,m)=10hm+4h^2+6h+2\)，以及 \(I(h,m)=1/E(h,m)\) 作为“interpretability function”。[pdf:E11] 前半段提供了有用的结构直觉；后半段实际上把低计算复杂度定义成高 interpretability，没有通过人类理解任务、feature attribution 或故障诊断实验验证，因此不能把 \(I\) 当作通用的可解释性度量。

## § 7 — 实验设计与结论

**问题 1：MI 是否能给出不过采样、又保留 PWM 内动态的采样率？ → 实验：** 对完整 \(i_L\) 序列在多种 \(f_{\mathrm{ds}}\) 下计算 sMAI 峰值。**答案：** first local maximum 出现在 250 kHz 附近，之后峰值趋于饱和；作者据此选择 10 samples/PWM cycle。这个结论只在本数据和固定 25 kHz 开关频率上验证。[pdf:E08]

**问题 2：结构化输入与 embedding 是否比物理直觉或低维窗口更适合 closed-loop？ → 实验：** 比较 physics-based Ph1/Ph2、统一 2D/3D、按 FNN 指定的 per-signal dimension、以及最终 4D/5D 网络；先看 open-loop，再闭环运行。**答案：** physics-based 输入在 open-loop 有竞争力，但 closed-loop 泛化失败；最终 3×17/4D 和 3×19/5D 被选出。[pdf:E10] 不过 4D 与 5D 同时改变了 embedding dimension 和网络宽度，因此“维数本身造成提升”没有被完全隔离。另一个评测边界是：数据由三次相同 load sequence 组成，再按连续索引切成约等长的 train/validation/test；nominal test 因而接近一次重复轨迹，而不是全新的 excitation profile。[pdf:E03][pdf:E05]

**问题 3：5D 是否在参数扰动下比 4D 稳定？ → 实验：** 在 nominal、\(2.5K_P\)、\(C_{\mathrm{out}}-15\%\)、\(L-5\%\) 四种仿真工况比较 current RMSE、transient extrema 和 steady-state error。**答案：** nominal 下 5D/4D RMSE 为 0.00519/0.00622 A；\(2.5K_P\) 下为 0.0188/0.0333 A；\(L-5\%\) 下为 0.0535/0.0735 A，5D 更好。例外是 \(C_{\mathrm{out}}-15\%\)：4D 为 0.0691 A、5D 为 0.0723 A，且 5D 出现 \(-20.270\%\) transient minimum。[pdf:E12][pdf:E13] 因而更准确的总结是“5D 在多数测试和总体 transient stability 上更好”，不是无例外地全面优于 4D。

**问题 4：仿真训练的模型能否迁移到真实装置？ → 实验：** 在实验 test window 上比较 TL 前后；TL 使用另一个时间窗口。**答案：** TL 前 RMSE 为 0.204 A（4D）和 0.239 A（5D）；TL 后降至 0.0542 A 和 0.0346 A。常规 transient 大多在 \(\pm5\%\) 内，但 test set 中未在 TL 数据出现的深度磁饱和把 5D minimum error 拉到 \(-13.4\%\)，4D 为 \(-18.59\%\)。[pdf:E13][pdf:E14] 这既证明少量装置数据可以显著校正 sim-to-real gap，也直接暴露了未覆盖磁性非线性的代价。

**问题 5：模型是否保留频率响应？ → 实验：** Fig. 13 在 100/250/400 W、100 V 条件下，用 PRBS 覆盖 110 Hz–3 kHz、Sinestream 延伸到 50 kHz，并与 simulation baseline 比较。**答案：** amplitude RMSE 在 250 W 时由 4D 的 5.50 dB 降到 5D 的 4.57 dB，在 400 W 时由 4.62 dB 降到 3.89 dB；但 100 W 时 4D 更好（5.61 vs. 6.23 dB），所有工况的 phase RMSE 都超过 30°。[pdf:E14][pdf:E15] 论文内部有一个小的不一致：Table I 把 rated output power 写成 230 W，而 Fig. 13 标为 250 W；这里的频域数字按 Fig. 13 报告。[pdf:E03][pdf:E15] 因此“到 50 kHz 的 amplitude tracking”有依据，“频域整体高精度”则没有；而且该频域基线仍来自仿真，不是实验频响。

## § 8 — Take-aways

### 用 5 句话总结

1. 本文把 NARX 的采样率、输入 delay 和 embedding dimension 从手工超参数改造成 sMAI/cMAI/FNN 驱动的结构选择问题。
2. 10-step clock-like input 是捕捉固定 25 kHz PWM 周期内相位的关键工程设计。[pdf:E06]
3. 5D 模型在多数仿真扰动、TL 后实验 RMSE 和中高负载 amplitude tracking 上优于 4D，但并非所有工况都占优。[pdf:E12][pdf:E14][pdf:E15]
4. offline TL 明显缩小 sim-to-real gap，同时未见过的深度磁饱和仍产生 \(-13.4\%\) 的 5D 瞬态误差。[pdf:E13][pdf:E14]
5. 小于 1 GFLOPS 是有价值的计算预算结果，但本文没有完成 FPGA/ARM 上的硬实时验收。[pdf:E10][pdf:E11]

### 用 3 句话总结

这篇论文最有价值的不是换了一个网络，而是用 MI 和相空间几何显式设计网络的时间记忆。实验表明这种结构在闭环和迁移后有潜力，但优势受训练吸引域覆盖、固定 PWM 相位和模型容量混杂影响。它是一条可信的轻量 DTI 构造路线，不是已经闭合的通用 converter digital twin。

### 用 1 句话总结

先用 MI/FNN 把“该记住哪些时刻”设计对，再用小 NARX-NN 学映射，能得到轻量且较稳健的 Boost DTI，但其可信边界仍由训练数据覆盖的运行域决定。

## § 9 — 最脆弱的假设

最脆弱的假设是：**训练激励、固定 PWM 时基和少量 TL 数据已经覆盖部署时会访问的主要动态吸引域。** 如果这个假设不成立，delay embedding 即使在训练集上展开得很好，也可能把新的物理状态投影到旧状态附近，NARX-NN 便只能平滑外推，而不是恢复真实状态。

论文给出的正面证据是：训练序列覆盖 25–99.9 \(\Omega\) 负载、加入多频激励，并在多个参数扰动和实验数据上测试；5D 多数情况下比 4D 稳定。[pdf:E03][pdf:E12] 但缺失更关键：训练明确排除了 thermal effect、bus/setpoint variation，网络以 CCM 为设计域，也没有测试变开关频率、多装置差异或多 converter interaction。[pdf:E01][pdf:E15]

最直接的反证已经出现在论文内部。实验中约 19 A 的 full-load step 引发深度磁饱和，使电感瞬时下降超过 50%；仿真峰值只有约 16.5 A，且没有这种饱和。这个未覆盖事件使 TL 后 5D 仍出现 \(-13.4\%\) 瞬态误差。[pdf:E13] 所以，方法的主要风险不是平均 RMSE 还不够低，而是 unseen attractor/region 出现时没有在线判别“当前已离开训练域”的机制。

## § 10 — 最小复现实验

一周内最值得复现的不是整套硬件，而是“MI/FNN 选出的时间结构是否真的带来 closed-loop 泛化”。

1. 按 Table I 搭建或取得同等级 Boost switching model，固定 \(f_{\mathrm{sw}}=25\) kHz、\(f_{\mathrm{ds}}=250\) kHz，生成包含负载阶跃、band-limited noise 和 10 Hz–1 kHz beat components 的序列；保留一个 nominal train set 和 \(2.5K_P\)、\(C_{\mathrm{out}}-15\%\)、\(L-5\%\) 三个完全不参与训练的 test sets。[pdf:E03][pdf:E12]
2. 复算 sMAI/cMAI 与 FNN，确认是否得到 \(\tau=\{2,2,5,2,5\}\) 和 4D/5D 候选。实现相同外生输入和 closed-loop NARX。
3. 为避免论文中的容量混杂，至少训练三组相同 3×19 宽度的模型：MI/FNN-5D、MI/FNN-4D、以及 delay 被随机打乱但输入相同的 control。每组使用相同 split、优化器和至少 5 个随机初始化。
4. 测量每个 test set 的 current RMSE、transient max/min、closed-loop divergence 次数，以及推理 wall-clock；不只报告 open-loop loss。

**支持核心 claim 的结果：** 5D 在多数随机种子和至少三个 test conditions 中稳定降低 closed-loop RMSE/发散率，并且打乱 delay 后显著退化。**反驳核心 claim 的结果：** 优势在同宽度控制后消失、只来自更大的 3×19 网络，或随机/简单等间隔 delay 与 MI/FNN 无显著差别。这个实验不需要先复现 TL 或 FPGA，就能检验论文最核心的结构选择机制。

## § 11 — 最强反例设计

最有力的反例不是再加噪声，而是**只改变 PWM 时基，让模型面对训练时没有的 phase clock**。本文的 250 kHz 采样率、\(\tau=5\) feedback delay、10-step clock 和 25 kHz 开关频率彼此锁定；因此模型可能学到的是“固定十格 PWM 索引上的波形模板”，而不是可迁移的 converter dynamics。[pdf:E06][pdf:E08]

具体实验可在相同电路、相同负载和相同 100 V setpoint 下，训练仅用 25 kHz，然后测试 20、22.5、27.5、30 kHz，以及在一个运行段内连续调频。设置三种输入方案：原始 10-step clock 不变、按新周期重新离散 clock、使用归一化连续 PWM phase。若原模型在负载和电压范围完全不变时仍明显失真，而归一化 phase 版本恢复，则说明主要失败来自固定时基，而不是功率级发生了全新物理变化。

这个反例能区分两个解释：强解释是 MI/FNN 找到了系统可推广的动态坐标；替代解释是它只为单一 \(f_{\mathrm{sw}}\) 找到了有效索引。若后者成立，论文关于 modular、scalable smart-grid DTI 的外推会受到根本限制，因为实际多 converter 系统可能有不同载波频率、异步相位和动态调频。

## § 12 — Follow-up Research Idea

**候选方向：从 sample-index NARX 改为 phase-equivariant hybrid-event digital twin。** 这里的 phase-equivariant 指：当 PWM 周期或采样率改变时，模型内部表示随归一化开关相位一致变换，而不是依赖固定第 1–10 个 sample。由于本卡没有对论文之外的相关工作做充分检索，以下只作为证据约束的候选想法，不声称 novelty。

**（a）未满足需求。** 多 converter smart grid 中，各装置可能异步开关、变频、降频或发生采样抖动；固定 \(\tau\) 和固定 10-step clock 难以直接组合。真正可扩展的 DTI 需要把“物理事件间隔”与“采样索引间隔”分开。

**（b）可能的研究价值。** 将状态更新定义在 turn-on、turn-off、saturation entry 等事件上，并用归一化 PWM phase 在事件之间插值，可以把单一 converter 的轻量 emulator 变成可在不同 carrier clocks 下组合的模块。研究目标也从“固定工况下一步电流最小 RMSE”改变为“在时基变化和异步组合下保持状态一致性与有界误差”。

**（c）可借鉴的相邻方法。** 可结合 hybrid systems 的 mode/event representation、neural controlled differential equation 的 irregular-time update、以及 equivariant representation 对 phase shift 的约束。VIF/MI 仍可用于信号筛选，但 MI 的 lag 应从 sample count 改为 physical time 或 normalized phase。

**（d）第一个证伪实验。** 只在 25 kHz 单 converter 上训练，然后零样本测试 20–30 kHz 连续变频；进一步把两个载波异步的 Boost DTI 接到共享母线上。若 event/phase 模型不能在相同参数量和小于 1 GFLOPS 预算下，同时把 current RMSE 和闭环发散率控制在 fixed-clock NARX 的域内表现附近，这个方向就应被否决。

**（e）与本文的实质区别。** 本文在固定 250 kHz sample grid 上通过 sMAI/cMAI 选择整数 delay，并把 PWM 周期编码成 10-step clock；新方向把事件时间和相位变成模型的基本坐标，使 sampling schedule 成为外部观测方式而非模型动力学本身。它不是给现有 NARX 再加一个输入，而是重新定义 DTI 的时间轴与多 converter 组合接口。
