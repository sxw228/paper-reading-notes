# Physics-Aware Neural Dynamic Equivalence of Power Systems

作者：Qing Shen、Yifan Zhou、Qiang Zhang、Slava Maslennikov、Xiaochuan Luo、Peng Zhang  
出处：IEEE Transactions on Power Systems，Vol. 39，No. 1，pp. 2341–2344  
年份：2023  
DOI：10.1109/TPWRS.2023.3328162  
Zotero key：S3UTQMTH  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇 letter 研究的是：只掌握外部电网（external system，ExSys）的测量、而未必掌握其完整元件模型时，如何构造一个可以和保留的内部电网（internal system，InSys）闭环联算的动态等值，并让这个等值在故障扰动后仍保留原系统的连续时间动态。作者把困难压缩为两个问题：离散采样的测量如何产生连续时间等值；训练时又如何把 ExSys 对 InSys 的反馈纳入，使闭环联算误差不因双向耦合而积累。[pdf:E01]（PDF 物理页 1，Abstract、Section I）

这不是一般意义上的曲线拟合。动态等值最终要被放回电网仿真闭环：它给出的边界量会改变 InSys，InSys 的响应又成为等值模型的输入。若训练只拟合 ExSys 的单向、开环轨迹，一点局部误差也可能经过这种反馈放大，导致联算轨迹失真。作者因此提出 NeuDyE：用 ODE-Net 表示 ExSys 的连续时间动力学，并用 InSys 的物理模型或由测量估计的物理梯度训练它。[pdf:E01]（PDF 物理页 1，Sections I–III-A）

论文直接声称的价值是：在未知或模型不可用的外部区域上，得到可与已知内部区域共同仿真的连续时间动态等值，并主动控制训练阶段的闭环精度。更谨慎地说，本文给出的证据限于 NPCC 仿真系统中的故障、清除时间和负荷水平变化；它没有证明跨拓扑、跨保护逻辑或实物实时仿真的可靠性。

## § 2 — 前人工作与不足

论文把前人路线分成三类。第一类是结构保持的动态等值和基于小信号模型的 model order reduction，例如文献 [1] 的 structure preservation、文献 [2] 的 parameter-preserving reduction 与文献 [3] 的 slow coherency。这些方法能利用已知模型压缩系统，但强非线性、复杂同调特性以及外部元件模型不可得会削弱其适用性。第二类是受 PMU 高频测量推动的数据驱动动态等值，它绕开了完整元件建模，却常从离散时间数据学习离散映射。第三类是 ODE-Net 与连续时间神经动力系统，为直接学习微分方程提供了工具。[pdf:E01]（PDF 物理页 1，Section I、References [1]–[5]）

作者指出，已有纯数据训练的直接形式只令 ODE-Net 的 ExSys 轨迹贴合测量，相当于只建模 InSys 对 ExSys 的影响；它没有把 ExSys 误差反馈到 InSys 后再回来的闭环效应放入目标函数。因此，开环训练误差很小并不等于闭环联算可靠。传统离散时间 DNN 的另一个不足是：它没有直接处理连续时间微分约束，性能对残余训练误差更敏感；本文 Fig. 7 后续给出了“开环拟合好、闭环轨迹却失效”的例子。[pdf:E02]（PDF 物理页 2，Section III-A）[pdf:E04]（PDF 物理页 4，Fig. 7、Section IV-D1）

需要区分作者论证与已完成的比较：论文引用了上述相关路线，但只有 7 篇参考文献，也没有对所有主流动态等值方法做统一 benchmark。因此，本卡不把 NeuDyE 的新颖性或全面优越性视为已由系统检索证明的结论。

## § 3 — 重建作者的思考路径

以下是基于论文背景与失败模式的逆向重建，不是作者逐字陈述。

第一步，研究者先接受一个工程事实：外部区域的详细模型可能不可得，但边界和部分内部状态的高频测量可以取得。第二步，如果直接学习下一采样时刻的离散映射，模型会与训练采样率绑定，也不自然适配连续时间求解器，于是更合理的目标是学习状态导数。第三步，ODE-Net 正好把“导数由神经网络给出、轨迹由 ODE solver 积分”合为一个连续时间模型，但单独拟合外部轨迹仍只解决开环误差。第四步，动态等值真正的使用场景是和 InSys 闭环联算，因此训练损失必须同时看 ExSys 与 InSys 的状态偏差；这又要求梯度穿过物理方程、代数约束和神经微分方程。第五步，adjoint method 可以在连续时间中反向传播这种闭环损失。最后，若商业软件不暴露物理模型的解析 Jacobian，就尝试利用测量与电网 Jacobian 的稀疏结构估计所需梯度。这个路径自然导向“ODE-Net 表示 + 闭环物理训练 + 稀疏梯度替代”三层结构。

## § 4 — 核心 Intuition

NeuDyE 的核心不是给神经网络额外加一个泛化的 physics loss，而是把神经外部系统真正接回物理内部系统，在闭环联算轨迹上训练。ODE-Net 负责让外部等值以连续时间导数的形式进入求解器，adjoint dynamics 则把内部系统对外部误差的反馈传回网络参数。若拿不到内部物理 Jacobian，PG-NeuDyE 用测量和已知网架稀疏性近似这个梯度。[pdf:E02]（PDF 物理页 2，Fig. 1、Sections III-B–III-C）

## § 5 — 具体方法与完整 Pipeline

以论文的 NPCC 案例为例，完整流程如下。

1. **划分系统并定义接口。** New England 区域的 buses 1–36 作为 InSys，其余区域作为 ExSys；两区通过 bus 29–37 与 bus 35–73 两条 tie-line 相连。论文令 InSys 的发电机、励磁器、调速器状态和线路电流构成 \(s_{in}\)，令 tie-line currents 构成外部等值状态 \(x_{ex}\)。[pdf:E03]（PDF 物理页 3，Fig. 2、Section IV-A）
2. **生成监督轨迹。** 在不同母线施加短路故障并改变清除时间，保存 ExSys 与 InSys 的时间序列测量。论文正文报告 20 个训练场景和 108 个测试场景；数据由 NPCC 电磁机械暂态仿真产生。[pdf:E03]（PDF 物理页 3，Section IV-A）
3. **建立连续时间等值。** 用全连接神经网络 \(N_\theta\) 输出 \(\dot{x}_{ex}\)，由 ODE solver 积分得到外部状态轨迹。把这个神经 ODE 与 InSys 的微分—代数物理模型联接，形成 physics-neural hybrid system。[pdf:E01]（PDF 物理页 1，Eqs. (1)–(2)）
4. **PI-NeuDyE 闭环训练。** 损失同时惩罚 ExSys 和 InSys 状态相对测量的误差；连续 adjoint equations 把闭环损失对网络参数的梯度反向积分。训练收敛后，作者期望神经外部系统与物理内部系统共同复现真实轨迹。[pdf:E02]（PDF 物理页 2，Eqs. (4)–(7)、Fig. 1(a)）
5. **PG-NeuDyE 替代梯度。** 若 TSAT、PSS/E 等商业软件不提供解析物理 Jacobian，就围绕典型工作点做一阶 Taylor 展开，再利用网架给出的 Jacobian 稀疏位置和测量样本做 least-squares regression，恢复训练需要的梯度近似。[pdf:E02]（PDF 物理页 2，Section III-C）[pdf:E03]（PDF 物理页 3，Eqs. (8)–(9)）
6. **闭环测试。** 把训练后的 NeuDyE 代回 InSys，比较边界母线电压、机组频率和 tie-line currents，与原 NPCC 物理模型的轨迹对照；另与离散时间 DNN、纯数据驱动训练以及 PI/PG 两种梯度来源比较。[pdf:E03]（PDF 物理页 3，Figs. 3–4）[pdf:E04]（PDF 物理页 4，Figs. 5–8）

从 EMT + FPGA 实现角度看，论文报告的数值推进只有 NeuDyE 采用 trapezoidal rule；未报告求解步长、多速率安排、故障开关的离散事件实现、代数环求解细节、并行依赖图、定点/浮点格式、FPGA 映射、资源占用、时序、实时步长或 HIL 平台。实际软件环境报告为 Matlab R2022b，原系统电磁机械仿真使用 Power System Toolbox（PST），部分发电机模型与 ISO New England 的 TSAT 模型对齐。[pdf:E03]（PDF 物理页 3，Section IV-A）因此这是一项动态等值学习与仿真研究，不能从本文直接推出可上 FPGA 或可实时执行。

## § 6 — 核心数学推导（无形式化数学则跳过）

先看表示。NeuDyE 直接学习外部状态导数：

\[
\dot{x}_{ex}=N_\theta(x_{ex},s_{in}).
\]

其中 \(x_{ex}\) 是选定的 ExSys 动态状态，\(s_{in}\) 表示 InSys 对 ExSys 的影响，\(\theta\) 是 ODE-Net 参数。接回系统后得到

\[
\begin{cases}
\dot{x}_{in}=P(x_{in},y_{in},y_b),\\
\dot{x}_{ex}=N_\theta(x_{ex},s_{in}),\\
G(x_{in},x_{ex},y_{in},y_b)=0,
\end{cases}
\]

这里 \(x_{in}\)、\(y_{in}\) 分别是 InSys 动态和代数状态，\(y_b\) 是边界状态，\(P\) 与 \(G\) 是 InSys 的动态和代数模型。[pdf:E01]（PDF 物理页 1，Eqs. (1)–(2)）工程直觉是：网络不是直接猜下一时刻波形，而是给出现时刻的“速度”；物理和神经状态由同一个时间推进过程共同演化。

纯数据训练的 Eq. (3) 只最小化 ExSys 轨迹误差。PI-NeuDyE 的 Eq. (4) 改为

\[
\min_\theta \sum_{i=1}^{n}L_i
=\sum_{i=1}^{n}\left(
\lVert x_{ex,i}-\hat{x}_{ex,i}\rVert_2
+\lVert x_{in,i}-\hat{x}_{in,i}\rVert_2
\right),
\]

并同时满足 InSys 与 ExSys 的微分约束。帽号表示测量，\(i\) 表示离散观测时刻。这样，网络参数造成的外部误差只有在经过物理内部系统反馈后仍能使两侧轨迹贴合，才会得到低损失。[pdf:E02]（PDF 物理页 2，Eq. (4)、Section III-B）

困难在于 \(N_\theta\) 输出 \(\dot{x}_{ex}\)，损失却依赖积分后的 \(x_{ex}\) 和 \(x_{in}\)。作者把代数约束吸收到 \(\tilde P(x_{ex},x_{in})\)，并用伴随变量 \(\lambda\)、\(\mu\) 写出 Lagrangian：

\[
\mathcal L=\sum_{i=1}^{n}L_i-\int_{t_0}^{t_n}
\left[\lambda^{T}(\dot{x}_{ex}-N_\theta)
+\mu^{T}(\dot{x}_{in}-\tilde P)\right]dt.
\]

对参数求导并选取合适的 adjoint boundary conditions 后，显式状态灵敏度被吸收到三个反向动力学中：

\[
\frac{d\lambda^T}{dt}
=-\lambda^T\frac{\partial N}{\partial x_{ex}}
-\mu^T\frac{\partial\tilde P}{\partial x_{ex}},
\]

\[
\frac{d\mu^T}{dt}
=-\lambda^T\frac{\partial N}{\partial x_{in}}
-\mu^T\frac{\partial\tilde P}{\partial x_{in}},
\qquad
\frac{d}{dt}\left(\frac{\partial\mathcal L}{\partial\theta}\right)
=\lambda^T\frac{\partial N}{\partial\theta}.
\]

从末端向 \(t=0\) 积分，就得到用于 gradient descent 的 \(\partial\mathcal L/\partial\theta\)。[pdf:E02]（PDF 物理页 2，Eqs. (5)–(7)）作者据此使用“theoretically ensures”描述闭环连续时间一致性；但它是以训练收敛、模型结构正确、梯度正确和数值求解可靠为前提的训练构造，不是给定误差界或闭环稳定裕度的定理。

PG-NeuDyE 处理的是 \(\partial\tilde P/\partial x_{ex}\) 与 \(\partial\tilde P/\partial x_{in}\) 不可直接取得的情况。它在典型工作点 \(\hat{x}^{(0)}\) 周围采用

\[
\tilde P_i^{(m)}
=\tilde P^{(0)}
+\begin{bmatrix}
\frac{\partial\tilde P}{\partial x_{ex}}&
\frac{\partial\tilde P}{\partial x_{in}}
\end{bmatrix}
\begin{bmatrix}
\hat{x}_{ex,i}^{(m)}-\hat{x}_{ex}^{(0)}\\
\hat{x}_{in,i}^{(m)}-\hat{x}_{in}^{(0)}
\end{bmatrix}
+O((\Delta x)^2).
\]

记目标 Jacobian 估计为 \(A\)，已知网架决定哪些元素应为零。对第 \(k\) 行只保留非零位置，论文用

\[
S(A_k^T)\approx
\left(S(X_k)S(X_k)^T\right)^{-1}S(X_k)p_k
\]

做 least-squares estimation。[pdf:E03]（PDF 物理页 3，Eqs. (8)–(9)）这一步的直觉是用稀疏先验降低待估参数数目；它仍依赖局部一阶近似、样本激励充分和回归矩阵可辨识。论文没有给出 Jacobian 估计误差如何传到闭环轨迹误差的界。

## § 7 — 实验设计与结论

**问题 1：在训练位置、不同故障清除时间下，PI-NeuDyE 能否复现闭环动态？** 实验把 NPCC 的 New England 区域设为 InSys：buses 1–36、9 台发电机；ExSys 为 buses 37–140、39 台发电机。原系统中 27 台发电机采用 electromechanical model，21 台采用 voltage-behind-transient-reactance model。Matlab R2022b/PST 生成轨迹，NeuDyE 用 trapezoidal rule 积分。[pdf:E03]（PDF 物理页 3，Fig. 2、Section IV-A）Fig. 3 在 bus 21 的训练故障位置测试两种随机清除时间：清除于 0.5400 s 时，机组频率和边界电压的 mean error 分别为 0.0503% 与 0.0456%；清除于 0.6108 s 时分别为 0.1706% 与 0.1363%。波形同时保留快速振荡和慢衰减趋势。[pdf:E03]（PDF 物理页 3，Fig. 3、Section IV-B1）答案是在该仿真工况内支持。

**问题 2：未见故障位置和时间能否泛化？** 正文报告 20 个训练场景，训练故障母线为 18、19、20、21、28；另有 108 个测试场景，列出的母线为 2、5、9、16、25、28、32、34、35。[pdf:E03]（PDF 物理页 3，Section IV-A）Fig. 4 的 bus voltage、machine speed 和 machine angle 相对误差箱线图大多集中在零附近，作者据此判断对新故障有合理误差。[pdf:E03]（PDF 物理页 3，Fig. 4、Section IV-B2）但正文的训练与测试列表都包含 bus 28，因此不能把所有测试场景都解释成严格的“位置未见”；论文也未给出跨随机种子的汇总表。

**问题 3：负荷参数变化下是否仍准确？** 作者让 InSys 负荷水平在原值的 70%–130% 内随机变化并重新训练 ODE-Net；Fig. 5 展示负荷在故障下增加 28% 的案例，报告 mean error 为 0.0561%。[pdf:E04]（PDF 物理页 4，Fig. 5、Section IV-B3）答案支持“重训练后的参数化案例可拟合”，但不能外推成“一个固定模型无需重训练即可跨 70%–130% 泛化”。

**问题 4：没有解析 InSys 梯度时，PG-NeuDyE 是否可行？** Fig. 6 比较 PI 与 PG：PI final loss 为 0.9969，PG 为 1.0738；PG 收敛稍慢，但其示例动态轨迹与 PI 几乎重合。[pdf:E04]（PDF 物理页 4，Fig. 6、Section IV-C）这支持稀疏测量梯度在该案例中可替代解析梯度，但论文没有报告 Jacobian 估计误差、噪声敏感性或多工况统计。

**问题 5：连续时间和 physics-aware 闭环训练是否必要？** Fig. 7 的离散时间 DNN 在开环训练波形上可贴合真实动态，放入闭环后却明显偏离；NeuDyE 仍跟随真实轨迹。Fig. 8 又在 10 个故障案例上比较 PI-NeuDyE 与纯数据方法的 tie-line current 相对误差：PI 的分布集中于零附近，纯数据方法出现显著更大的离散和偏差。[pdf:E04]（PDF 物理页 4，Figs. 7–8、Section IV-D）这两个对照支持作者的机制解释，但模型容量、训练预算与超参数是否等价未报告，因而还不能排除 baseline 配置差异的替代解释。

整体上，实验覆盖了故障位置、清除时间、负荷变化、解析/估计梯度、连续/离散表示与 physics-aware/纯数据训练。不过网络层数和宽度、数据采样间隔、训练时窗、学习率、优化器、随机种子、噪声水平、训练耗时、推理耗时、硬件、模型阶数、实时性与代码可得性均未报告。结果因此证明的是一个 4 页 letter 中的 NPCC 仿真 proof-of-concept，而不是工业部署资格。

## § 8 — Take-aways

**5 句话。**  
1. NeuDyE 用 ODE-Net 把外部电网等值写成连续时间状态导数，而不是固定采样率的下一步映射。  
2. PI-NeuDyE 把神经外部系统和物理内部系统接成闭环，并同时最小化两侧状态误差。  
3. continuous adjoint 把闭环损失穿过物理—神经混合动力学传回网络参数。  
4. PG-NeuDyE 在解析 Jacobian 不可得时，用测量和网架稀疏性估计训练梯度。  
5. NPCC 仿真支持其在若干故障和负荷变化下的准确性，但复现细节、噪声鲁棒性、拓扑变化和实时实现仍未验证。

**3 句话。**  
NeuDyE 把动态等值从开环波形拟合改成连续时间的闭环物理—神经训练。论文给出的关键证据是：离散 DNN 或纯数据模型即使开环拟合良好，也可能在闭环中失效，而 PI/PG-NeuDyE 在 NPCC 案例中保持较小误差。最重要的保留意见是，实验规模和报告细节不足以把条件性的训练构造等同于一般闭环稳定性保证。

**1 句话。**  
这篇论文最值得带走的思想是：动态等值要按它最终参与的闭环联算方式训练，而不是只在被切开的外部子系统上把曲线拟合好。

## § 9 — 最脆弱的假设

失败代价最大的假设是：作者选取的 \(x_{ex}\) 与 \(s_{in}\) 足以把 ExSys 表成单值、Markovian 的一阶动力学 \(\dot{x}_{ex}=N_\theta(x_{ex},s_{in})\)。案例中 \(x_{ex}\) 只取 tie-line currents，\(s_{in}\) 取 InSys 的发电机、励磁器、调速器状态和线路电流；作者说这些 features 可按测量可用性调整，却没有给出 observability、identifiability 或最小状态证明。[pdf:E01]（PDF 物理页 1，Eq. (1)）[pdf:E03]（PDF 物理页 3，Section IV-A）

这是基于证据的推断：若外部区域存在未观测的控制器、限幅器、保护动作或慢状态，使相同的 \((x_{ex},s_{in})\) 对应不同的 \(\dot{x}_{ex}\)，那么不存在论文假设的确定性 ODE 右端。增加训练数据或更精确求解 adjoint 也无法修复这种状态表示错误。论文的 NPCC 故障、清除时间与负荷变化说明所选表示在固定模型族中可用，但没有构造“相同边界观测、不同隐藏模式”的辨识试验，因此对这个关键假设的证据仍不充分。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 NPCC，而是“闭环训练是否真的比开环训练更抗误差积累”。

1. **数据。** 在一个可完全仿真的两区域小系统上，把一侧当 InSys、另一侧当 ExSys；生成约 20 个训练短路场景和 20 个未见位置/清除时间场景，保存内部状态、边界电压与 tie-line current。保留完整模型只用于产生真值。
2. **实现。** 用相同网络容量和优化预算训练两个 continuous-time 模型：A 只最小化 ExSys 轨迹误差；B 同时最小化接回 InSys 后的 InSys 与 ExSys 轨迹误差。先用自动微分取得物理 Jacobian，暂不实现 PG 版本，避免把验证问题扩大。
3. **测量。** 分别报告开环 one-trajectory error、闭环边界电压/频率/tie-line current 的时间归一化误差、故障清除后最大偏差以及是否出现发散；对每个场景使用相同积分器和步长。
4. **支持标准。** 预先规定：在未见的 20 个故障中，B 的闭环轨迹误差中位数至少比 A 低 50%，且无 B 独有的发散，同时 A、B 的开环误差处于同一数量级，就支持“闭环目标而非单纯容量带来收益”。
5. **反驳标准。** 若控制容量、训练预算和开环误差后，A 与 B 的闭环误差没有稳定差异，或优势随积分步长消失，就反驳这项最核心的机制 claim。

50% 是复现实验为提高可证伪性而预注册的阈值，不是论文报告数字。

## § 11 — 最强反例设计

最强反例是构造“边界观测完全相同、外部隐藏模式不同”的成对场景。让 ExSys 包含会切换的 excitation limiter、governor deadband、保护继电器或受迟滞影响的负荷；选择两段历史，使测试起点的 tie-line current 与所有提供给 \(s_{in}\) 的 InSys features 数值相同，但隐藏控制状态分别位于不同模式。随后施加完全相同的 InSys 扰动。

如果两种模式给出不同的 \(\dot{x}_{ex}\) 或故障后轨迹，那么任何确定性的 \(N_\theta(x_{ex},s_{in})\) 都必须把同一输入映射为两个不同输出，模型形式本身即不可实现。应比较 NeuDyE、带外部历史窗口的模型和显式 hybrid-state 模型：若只有后两者能同时复现两条轨迹，就说明本文成功主要来自案例中接口状态近似 Markovian，而不是 ODE-Net 与 physics-aware 训练对一般外部系统都足够。这一反例比单纯增加噪声更强，因为它直接攻击 Eq. (1) 的可表示性前提。

## § 12 — Follow-up Research Idea

电力系统动态等值的高影响工作通常不仅看平均轨迹误差，还看跨工况稳定性、对未建模事件的失效边界、可解释的物理约束以及进入实际安全评估流程的能力。基于第 9 节，候选方向是把“单一确定性 ODE 等值”改成“带模式不确定性与可拒绝机制的 hybrid belief-state dynamic equivalence”。这不是给 NeuDyE 再加一个网络模块，而是改变输出目标：当边界历史不足以唯一确定外部状态时，模型输出一组可能的动态或带覆盖保证的轨迹集合；检测到不可辨识或越出训练支持域时，明确拒绝给出单一等值。

**(a) 未满足需求。** 调度与安全评估不能把一个在隐藏保护模式下可能分叉的外部区域压成虚假的唯一轨迹；需要知道“等值何时可信、何时必须回退到更完整模型”。  
**(b) 研究价值。** 若能把接口可辨识性、模式切换和误差覆盖统一到一个可用于 contingency analysis 的契约中，它会比继续降低固定 NPCC 工况的平均误差更接近工程安全需求。  
**(c) 相邻工具。** 可借鉴 hybrid systems 的 guard/mode 建模、set-valued system identification、latent state-space models 与 conformal prediction；物理 DAE 仍约束 InSys，边界历史用于维护外部模式的 belief state。  
**(d) 首个证伪实验。** 使用第 11 节的成对隐藏模式数据，要求在观测不可区分阶段，预测集合同时覆盖两条真实分支；一旦额外观测足以区分模式，集合应收缩。若集合仍漏掉一支，或为保证覆盖而始终宽到失去决策价值，方向即被早期证伪。  
**(e) 实质区别。** NeuDyE 假设给定当前状态可输出唯一导数，并以点轨迹误差训练；候选方法把“是否存在唯一可辨识等值”本身纳入问题定义，并允许集合预测或拒绝。由于本任务严格 PDF-only、没有做外部相关工作检索，这只是候选研究想法，不声称 novelty。
