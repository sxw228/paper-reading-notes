# On Model Order Reduction and Exponential Integrator for Transient Circuit Simulation

- 作者：Cong Wang；Dongen Yang；Jinming Lyu；Yong Dai；Cheng Zhuo；Quan Chen
- 出处：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems，Vol. 43，No. 1，pp. 328–339
- 年份：2023（在线发表；卷期版为 2024 年 1 月）[pdf:E01]
- DOI：10.1109/TCAD.2023.3309734
- Zotero key：IIZI5QDP
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的不是“再发明一种更快的积分器”，而是追问两个长期被分开的加速路线究竟是不是同一件事：频域的 moment-matching model order reduction（MOR）先构造可复用 reduced-order model（ROM），再做时域仿真；exponential integrator（EI）则从矩阵指数的时域解析形式出发，每个时间步用 Krylov subspace 近似 matrix-exponential-vector product（MEVP）。作者的核心 claim 是：在给定条件下，EI 可解释为“每个时间步都做一次单输入、指定展开点的 rational-Krylov moment-matching MOR，然后用 EI 把这个当步 ROM 推进一步”。这一 claim 在摘要与贡献列表中被明确提出，而不是本卡的事后类比。[pdf:E01]

问题重要性有两层。第一，论文指出先进节点全芯片 post-layout 仿真可达到数亿至数十亿未知量并耗费数周，完整 SPICE 精度因此成为 EDA 生产率瓶颈。[pdf:E01] 第二，如果 MOR 与 EI 的 Krylov 计算能被统一解释，就可以把 MOR 的 moment matching、展开点和 ROM 观点，与 EI 的 residual、步长控制和实际输入感知放进同一分析框架；这有助于解释为什么 EI 在多输入时不必承担 block-ROM 随输入数增长的代价，也有助于判断何时应选择可复用 ROM，何时应选择按需、不可复用的当步降阶。这里后半句属于基于论文证据的工程推断，不是论文已证明的通用选型定理。

## § 2 — 前人工作与不足

论文把 PRIMA 及其后续方法作为 projection-based moment-matching MOR 的代表：从线性电路的频域 transfer function 出发，用 block Arnoldi 生成 Krylov basis，使 ROM 在展开点附近匹配原系统若干 moments。对于 \(p\) 个输入、每个输入匹配 \(m\) 个 moments，单展开点 ROM 的维度按 \(mp\) 增长；这正是多输入系统中 basis 构造与 reduced system 尺寸变重的根源。[pdf:E02]

作者归纳了传统 MOR 的三个缺口。其一，多输入要求 ROM 对任意输入波形保持 I/O 关系，basis 与 ROM 尺寸随输入数上升。其二，降阶发生在频域、ROM 却在时域使用，降阶阶段不知道实际 transient waveform，导致 error control、展开点和 moment 数的自动选择困难。其三，大信号非线性器件缺少直接可用的频域模型，实际往往只对线性网络降阶，再与非线性模型耦合。[pdf:E01] 文中也承认 FastEM 一类 input-dependent MOR 能把特定输入近似成 piecewise constant waveform，从而只保留一个输入向量，但其对更复杂、高阶 Laplace 输入的推广，以及 error control、展开点选择和非线性集成仍未解决。[pdf:E07]

另一条 prior line 是基于 Krylov MEVP 的 EI。它直接使用线性 ODE 的矩阵指数解，并已有 rational/shift-and-invert Krylov、posterior residual 与 step adaptivity 等基础。论文引用既有 EI 工作关于 stiffness handling、parallel processing 和 power-grid simulation 的结果，但本论文自己的实验并不重新验证这些所有优势。[pdf:E02] 因而本文真正补的不是 EI 或 MOR 的第一套算法，而是两者在相同 Krylov 几何下的数学关系、适用差异与复杂度解释。

## § 3 — 重建作者的思考路径

下面是基于论文结构重建的可能思考路径，不把最终贡献倒灌成既有事实。

1. 从线性 modified nodal analysis（MNA）方程出发，传统 MOR 和 EI 最终都在反复做“稀疏线性求解 + Krylov basis + 小矩阵计算”；差别似乎主要是一个在频域预处理、一个在时域逐步执行。[pdf:E02]
2. 观察到 EI 的 rational Krylov shift \(\gamma\) 与 MOR 的频域展开点都改变同一个 shifted operator，于是尝试令 \(s_0=1/\gamma\)，比较两边生成的 subspace，而不只比较最终波形。
3. EI 为把 source term 合并到一次 MEVP，会给系统增加一个状态；于是问题变成：这个 \(m+1\) 维 EI basis 是否恰好由一个常数方向加上 \(m\) 维 MOR basis 构成。Lemma 1 给出的正是这种 basis relation。[pdf:E03]
4. 如果 basis 对齐，就分别在 DC 展开点与非零展开点上写出 MOR 后的一步 EI 解和 full-system EI 的 projected 解，比较两者。随后再把非零初值写成额外固定输入，用线性叠加把结论扩展过去。[pdf:E04][pdf:E05]
5. 最后，不把等价性误写成两种工程流程完全相同，而是比较“传统 MOR 一次昂贵但可复用”与“EI 每步便宜但不可复用”的 cost structure，并用 IBM power/ground（P/G）网络做数值核对。

这个路径的关键不是“两个方法都叫 Krylov，所以相同”，而是必须把 expansion point、shift、starting vector、subspace dimension、单步输入和时间推进方式逐一对齐。

## § 4 — 核心 Intuition

EI 每一步只需要解释当前状态与当前实际输入形成的一个向量，因此它隐式构造的是一个为“这一小段轨迹”服务的单输入 ROM；传统 MOR 则要提前为所有潜在输入构造可复用 ROM。把 EI 的 shift 设为 \(\gamma\)、把 MOR 的展开点设为 \(s_0=1/\gamma\) 后，两者的 rational Krylov basis 在增加一个辅助维度后对齐，于是两条计算路径给出同一个 projected one-step solution。[pdf:E05] 代价是 EI 的当步 ROM 下一步通常不能复用，因为 starting vector 随状态和输入改变。

## § 5 — 具体方法与完整 Pipeline

以论文的 ibmpg1t power-grid 测试为具体情境，可把完整 pipeline 写成如下过程。

1. **模型输入。** 线性电路由
   \[
   C\dot{x}(t)+Gx(t)=Bu(t)
   \]
   表示，其中 \(C\) 是 capacitance/inductance matrix，\(G\) 是 conductance matrix，\(B\) 映射 \(p\) 个源，\(x\) 是全状态。论文主要推导假设 \(C\) 可逆；若 \(C\) 奇异，只引用既有 regularization 方法先消去 algebraic constraints，并未在本文给出新证明或实验。[pdf:E02]
2. **传统 MOR 路径。** 在零初值下做 Laplace transform，选 expansion point \(s_0\)，用 block rational Arnoldi 对 \((s_0C+G)^{-1}\) 相关算子构造 \(m\) 阶、\(p\) 输入的 basis \(V_M\)，投影得到 \(mp\) 维 ROM；随后可用 BDF 或 EI 在时域反复仿真同一 ROM。它的优势是 ROM 可被不同输入和时间步复用。[pdf:E06]
3. **EI 路径。** 写成 \(\dot{x}=Ax+C^{-1}Bu\)，其中 \(A=-C^{-1}G\)。在一个时间步 \(h\) 内把输入当作常值 \(u_n\)，用增广矩阵把齐次指数项与 source integral 合并成一次 MEVP；再用 \(\mathcal K_m((I-\gamma\widetilde A)^{-1},\widetilde x_n)\) 的 rational Krylov projection 算近似，并以 residual 控制 subspace dimension。[pdf:E03]
4. **当步输出。** 论文证明在单输入向量 \(b=Bu_n\)、对应 expansion point \(s_0=1/\gamma\) 及匹配维度下，\(m+1\) 维 EI basis 与 \(m\) 维 MOR basis 对齐；EI 的新状态因此等价于先生成当步 ROM、再用 EI 推进一步。下一步重新由新状态和新 \(Bu_{n+1}\) 形成 starting vector，所以这个隐式 ROM 通常不复用。[pdf:E05]
5. **开关、事件与多速率。** 论文只规定同一时间步内输入为常值，没有报告 switch/event detection、拓扑切换、multirate partition 或异步 time wheel。实验中的 pulse source 由固定步长采样；因此不能把本文证明直接外推为开关电力电子 EMT 的 event-exact 求解器。
6. **计算依赖与并行。** 固定 \(\gamma\) 时，EI 全仿真只需一次 sparse LU factorization，之后每步做 forward/back substitution、single-vector Arnoldi orthogonalization 和小 Hessenberg matrix exponential；传统 MOR 则按展开点做 LU，并以 \(p\) 列 block Arnoldi 构造可复用 basis。[pdf:E07] 本文未报告线程数、GPU/FPGA 并行实现、通信开销或并行 speedup。
7. **数值表示与执行平台。** 作者在 Python-based circuit simulator Ahkab 中实现 EI 与 MOR，MOR engine 为 single-point PRIMA；论文未报告 Python/solver 版本、CPU 型号、内存、浮点精度、稀疏 LU 实现或 reproducibility package。[pdf:E08][pdf:E10]
8. **FPGA 映射。** 论文未报告 FPGA architecture、定点格式、DSP/BRAM/LUT 占用、pipeline initiation interval、latency、实时步长或 hardware-in-the-loop 平台。它能给 FPGA 工作提供的是算法级 dependency 与 cost model，而不是可直接验收的硬件方案。

## § 6 — 核心数学推导（无形式化数学则跳过）

**第一步：把 MOR 写成 moment matching。** 对零初值线性 DAE 做 Laplace transform，并定义
\[
M=-G^{-1}C,\qquad R=G^{-1}B,
\]
得到
\[
Y(s)=(I_n-sM)^{-1}R. \tag{3}
\]
block Krylov space \(\mathcal K_m(M,R)=\operatorname{span}(R,MR,\ldots,M^{m-1}R)\) 的 basis \(V_M\) 把 full system 投影成小 ODE；对应 transfer function 在 DC expansion point 匹配前 \(m\) 个 moments。直观上，moment 是 transfer function 在展开点附近的局部级数系数，匹配越多阶，就越能复现该邻域内的频率响应。[pdf:E02]

**第二步：把 EI 写成一次矩阵指数。** 令 \(A=-C^{-1}G\)。一个时间步的解析形式为
\[
x_{n+1}=e^{Ah}x_n+\int_0^h e^{A(h-\tau)}C^{-1}Bu(\tau)\,d\tau. \tag{8}
\]
若步内 \(u(\tau)=u_n\)，则
\[
x_{n+1}=e^{Ah}x_n+h\phi_1(Ah)C^{-1}Bu_n,\qquad
\phi_1(z)=\frac{e^z-1}{z}. \tag{10}
\]
作者把 \(A\)、\(C^{-1}Bu_n\) 和常数 1 组成增广矩阵 \(\widetilde A\)，把上式改写为一次 \(e^{\widetilde Ah}\widetilde x_n\)，再投影到 polynomial 或 rational Krylov subspace；Eq. (13) 与 Eq. (15) 给出 posterior residual 形式。[pdf:E03]

**第三步：对齐两个 basis。** 取 real expansion point \(s_0=1/\gamma\)、零初值、单列 \(b\)，MOR 使用
\[
\mathcal K_m\!\left(-(s_0C+G)^{-1}C,\;(s_0C+G)^{-1}b\right),
\]
EI 使用增广系统的 \(\mathcal K_m((I-\gamma\widetilde A)^{-1},\widetilde x_n)\)。Lemma 1 证明其正交 basis 满足
\[
V_E=
\begin{bmatrix}
0 & V_M\\
1 & 0^\mathsf T
\end{bmatrix}, \tag{18}
\]
也就是 EI 多出来的一维只承载增广常数，其余列就是 MOR basis。[pdf:E03] Appendix 通过显式展开 \((I-\gamma\widetilde A)^{-1}\widetilde x\)、二次和三次作用，再做 orthogonalization，补出 Eq. (21) 所需的前几个 basis vector 关系；这是正文 Lemma 的代数细节，不是另一套算法。[pdf:E11]

**第四步：比较一步解。** DC 情形 \(s_0=0,\gamma=\infty\) 下，Theorem 1 比较 MOR 后 reduced ODE 的 EI 解与 full ODE 在 \(V_E\) 上的 EI projection，得到 \(x_1^{MOR}=x_1^{EI}\)。非零 \(s_0\) 下，Theorem 2 用
\[
V_M^\mathsf TA V_M\approx s_0I+H_M^{-1}
\]
对齐两边，最后得到 \(x_2^{MOR}=x_2^{EI}\)。[pdf:E04][pdf:E05] 需要注意，证明中明确出现近似号，并舍去 Arnoldi relation 的 rank-one update；因此“等价”应理解为在相同 Krylov projection/近似设定下的一步等价，而不是任意维度下 full-order exact flow 的无条件恒等。

**第五步：处理非零初值。** 对 \(x_0\neq0\)，作者令 \(\hat x(t)=x(t)-x_0\)，把问题改写为
\[
C\dot{\hat x}+G\hat x=Bu(t)-Gx_0, \tag{43}
\]
再把 \(-Gx_0\) 当作额外固定输入并用线性叠加，因而将结论扩展到 inhomogeneous initial condition；该步骤依赖系统线性。[pdf:E05]

**第六步：比较复杂度。** 对 circuit size \(N\)、输入数 \(p\)、每个展开点 \(m\) 个 moments、\(k\) 个展开点，论文估计
\[
C_{\mathrm{MOR}}
=k\!\left(C_{\mathrm{LU}}+mpC_{\mathrm{BF}}
+\frac{m(m+1)}{2}p^2C_{\mathrm{OR}}\right), \tag{47}
\]
\[
C_{\mathrm{EI}}
=C_{\mathrm{LU}}+n_t\!\left(mC_{\mathrm{BF}}
+\frac{m(m+1)}{2}C_{\mathrm{OR}}\right). \tag{48}
\]
\(C_{\mathrm{BF}}\) 是复用 LU 后一次 forward/back solve 的代价，\(C_{\mathrm{OR}}\) 是两个 \(N\)-vectors 的 orthogonalization 代价。关键不是 EI 永远更快，而是 MOR 的 block orthogonalization 带 \(p^2\)，EI 则把输入压成一个实际向量，但要支付 \(n_t\) 次不可复用的当步 basis 构造。[pdf:E07]

## § 7 — 实验设计与结论

**问题 1：理论等价是否在数值上成立？ → 实验：** 作者在 Ahkab 中用 ibmpg1t、一个 current source、全 1 初值，取 \(s_0=10^7,10^8,10^9\)，对应 \(\gamma=10^{-7},10^{-8},10^{-9}\)，分别匹配 4、6、8 个 moments，并用 \(h=10^{-11}\) 比较 EI 与“逐步 MOR 后 EI”。**答案：** Table III 的相对差从 \(2.3310\times10^{-14}\) 到 \(6.3915\times10^{-12}\)；多步 pulse waveform 也重合，支持论文设定下的数值等价。[pdf:E08] 这些数值只证明所测 combination，不等于对所有矩阵、shift 和 Krylov tolerance 的证明。

**问题 2：实际输入感知是否让 EI 需要更少 moments？ → 实验：** ibmpg1t 使用 20 个 current pulse sources，固定 \(s_0=10^9\)，EI 与 MOR 都用 10 ps step，reference 用 trapezoidal method 的 1 ps step。**答案：** Fig. 4 中 EI 每步最多 3 个 moments（subspace size 4）已与 reference 良好一致；一次性 MOR 至少需 6 个 moments，5 个时明显失真。作者将差异解释为 MOR 要同时覆盖 20 个输入，而 EI 每步只处理一个实际 \(Bu_n\) 向量。[pdf:E09]

**问题 3：展开点选择谁更稳健？ → 实验：** ibmpg1t 固定 6 个 moments、10 ps step，扫描 expansion point。**答案：** 传统 MOR 在 \(5\times10^8\) 与 \(10^{10}\) 时失真，在 \(10^9\) 与 \(5\times10^9\) 时可接受；作者报告 EI 在更宽范围保持准确，并将其归因于当步 ROM 只需服务一个时间步且已知实际 waveform。[pdf:E09][pdf:E10] 该结论来自一个 benchmark 与 pulse input；论文自己也指出换成 sine input 可能改变 MOR 偏好的展开点，不能外推成固定 universal range。

**问题 4：复杂度中的 \(p\) 与 \(m\) scaling 是否出现？ → 实验：** 使用 IBM P/G ibmpg3t–ibmpg6t 等大例，节点规模从 1M 到 3.2M；EI 固定 1000 steps、两法都取 6 moments，扫描输入数；另在 \(p=100\) 时扫描 moment 数。**答案：** Fig. 6 显示 EI runtime 近似不随 \(p\) 变化、MOR 随 \(p\) 呈 quadratic trend；\(p<100\) 时 MOR 更快，超过约 100 后曲线开始交叉，且更大 case 的 break-even 更早。Fig. 8 中 EI 随 \(m\) 近似线性，MOR 前段近似线性、后段因 orthogonalization 转为 quadratic trend。[pdf:E10]

**实验边界。** 这些 runtime 主要用于验证 scaling；作者明确排除了 reduced-system simulation time，且未报告硬件、solver 版本、内存峰值或统计波动，也没有在 scaling 图旁给出每个点的等精度证明。[pdf:E10] 测试对象均为线性 IBM P/G 网络；没有 nonlinear device、拓扑开关、EMT 多速率、FPGA resource/timing 或 real-time deadline 实验。因此本文支持“线性稀疏 P/G 网络上的等价与趋势”，不支持“已在 FPGA 上实现实时 EMT”。

## § 8 — Take-aways

**5 句话。**  
1. 论文把 EI 解释为每步一次、单实际输入向量、rational-Krylov moment-matching MOR，再在同一步用 EI 推进。  
2. \(s_0=1/\gamma\) 和增广的一维状态把 MOR 与 EI 的 basis 对齐，这是等价性的数学核心。  
3. 传统 MOR 付出一次较重的 block reduction 换取 ROM 复用，EI 则用每步重建换取实际输入感知、residual control 与对多输入数较弱的依赖。  
4. IBM P/G 实验支持 one-step/multi-step 数值一致、EI 用更少 moments，以及两者对 \(p\) 和 \(m\) 的不同 runtime scaling。[pdf:E08][pdf:E09][pdf:E10]  
5. 结论只在论文规定的线性、步内常值输入和 Krylov approximation 条件下闭合，不能直接视为 nonlinear switched EMT 或 FPGA implementation 的证据。

**3 句话。**  
EI 与 moment-matching MOR 不是完全无关的两类数学对象，而是可以在对齐 shift、starting vector 和 basis dimension 后看作同一 projected one-step computation。传统 MOR 的价值是 reuse，EI 的价值是 on-demand；多输入数、时间步数、所需 moments 和稀疏求解/orthogonalization 的相对代价共同决定谁更快。论文给了线性 P/G 网络的有力解释与数值支持，但未处理硬件映射、开关事件和非线性闭环。

**1 句话。**  
这篇论文最有价值的结论是：EI 可以被理解为“只为当前时间步和当前实际输入服务的 moment-matching ROM”，因此它用可复用性换来了更轻的输入维度与更直接的误差控制。

## § 9 — 最脆弱的假设

失败代价最大的假设是：**一个时间步内存在固定的线性算子 \(A=-C^{-1}G\)，且所有源可以压成固定单向量 \(b=Bu_n\)。** 这同时支撑增广矩阵、single-vector Krylov、basis 对齐、非零初值的线性叠加，以及“EI 每步只处理一个输入”的复杂度优势；论文在推导开头明确把讨论限制在线性电路并假设同一时间步内输入常值。[pdf:E03]

在含开关器件、强非线性器件或 event 落在步内的 EMT 中，\(G\) 可能随状态/拓扑改变，source 与 nonlinear current 也不能由一个固定 \(Bu_n\) 完整表示。此时不仅误差可能变大，连“两边生成同一个 Krylov space”的前提也会消失。论文提供的证据是线性 IBM P/G benchmark 和对奇异 \(C\) 的既有 regularization 引用；它没有给 nonlinear/switched case 的等价证明或实验。作者提到 EI 在时域更容易接入 nonlinear terms，但那是方法便利性的讨论，不是本文核心 theorem 已覆盖非线性。[pdf:E06]

此外，核心证明在 Eq. (31) 与 Eq. (40) 使用 projection approximation 并舍去 rank-one Arnoldi update。[pdf:E04][pdf:E05] 因此在最坏 nonnormal/stiff operator、过小 subspace 或不良 shift 下，近似项是否仍受控是实验尚未覆盖的关键问题。

## § 10 — 最小复现实验

一周内最小复现应只验证核心等价，不复刻全部 runtime 图。

1. 取得 ibmpg1t，或构造一个可公开保存的稀疏线性 RC power-grid，使 \(C,G,B\) 与 source pulse 可独立检查。记录矩阵规模、稀疏度、solver、floating-point precision 和 tolerance；这些是原文未报告但复现必须补齐的条件。
2. 实现两条严格共享 LU、Krylov tolerance 与 dense exponential 的路径：A 路径直接对增广系统做 \(m+1\) 维 rational-Krylov EI；B 路径用 \(s_0=1/\gamma\) 构造 \(m\) 维 MOR，当步在 ROM 上做 EI，再映回 full space。
3. 先复刻论文组合：全 1 初值、一个 current source、\(h=10^{-11}\)，扫描 \(s_0=10^7,10^8,10^9\) 与 \(m=4,6,8\)。测
   \[
   \frac{\lVert x^{EI}-x^{MOR}\rVert_2}{\lVert x^{EI}\rVert_2}
   \]
   以及各自 Arnoldi residual；然后跑 100–1000 步 pulse waveform。
4. **支持标准：** 所有组合的一步相对差不高于 \(10^{-10}\)，多步差异与累积 residual 同阶且波形重合。这个阈值略宽于论文报告的 \(10^{-14}\)–\(10^{-12}\) 区间，以容纳 solver 与平台差异。[pdf:E08]
5. **反驳标准：** 在相同 subspace、shift、LU 与 stopping rule 下，差异稳定高于 residual/roundoff 两个数量级，或随步数系统性增长且不能由输入离散误差解释。出现这种结果时应先检查 basis ordering 和增广状态，再判断 theorem 的近似解释是否不足。

这个实验不验证“EI 永远比 MOR 快”；性能结论至少还要增加 \(p\)、\(m\)、\(n_t\) 三维 sweep 和等精度约束。

## § 11 — 最强反例设计

最强反例应留在 theorem 声称的线性、步内常值输入范围内，而不是简单换成论文明确排除的非线性电路。构造一族稳定但高度 nonnormal、谱跨越多个数量级的稀疏 MNA 系统，使 rational Arnoldi 在给定小 \(m\) 和不良 \(\gamma\) 下有很大的末项 \(h_{m+1,m}\)；选择 starting vector 激活未被当前 subspace 捕获的方向。然后在完全相同的 \(m+1\) 与 \(m\) 维设置下，分别计算 full augmented EI projection 与“先 MOR、再 EI”，保留和移除 Eq. (35) 的 rank-one update 各做一次。

这项攻击直接瞄准证明从 Arnoldi relation 走到 \(V_M^\mathsf TAV_M\approx s_0I+H_M^{-1}\) 的近似步骤，而不是攻击实现细节。[pdf:E04] 若两条路径的差异可显著超过 posterior residual，并且差异只在恢复 rank-one term 后消失，那么“equivalent”必须收窄为某个 residual-controlled regime；若差异始终由 residual 严格界定，则反例失败，反而强化论文的解释。为避免替代解释，还应使用 exact dense exponential 作为小规模 oracle，并分别扫描 nonnormality、\(m\) 与 \(\gamma\)。

## § 12 — Follow-up Research Idea

**领域评价判断。** 对 EDA/circuit simulation 而言，高影响工作通常不只要有新的线性代数关系，还要同时给出可证误差边界、对 representative large circuits 的 accuracy/runtime/memory 验证，以及可嵌入实际 simulator 的 event 与 device 处理。这个判断是本卡基于论文问题情境的综合，不是论文原文 claim。

**候选想法：把 ROM/Krylov subspace 变成带证书、可跨步演化的仿真状态。** 传统 MOR 的事实源是“对任意输入可复用的静态 ROM”，EI 的事实源是“只对当前输入有效、每步重建的 subspace”。未满足的需求是：在 waveform 缓慢变化时，EI 丢掉了大量可复用结构；在输入或拓扑突然变化时，静态 MOR 又缺少及时、可验证的更新机制。[pdf:E06]

具体研究目标不是给 EI 再加一个 cache，而是重新定义求解状态为 \((x_n,V_n,\mathcal C_n)\)：\(V_n\) 是可 recycle/augment 的 rational Krylov subspace，\(\mathcal C_n\) 是同时约束 moment mismatch、MEVP residual 与 event crossing 的 certificate。只有 certificate 失效时才扩展或重建 subspace；发生 topology/device mode change 时，把失效原因显式分成 operator change、input-direction change 与 time-step change。可借鉴相邻领域的 recycled Krylov、subspace tracking、switched-system reachability 和 a posteriori error estimation。

它可能产生本领域认可的价值，是因为目标从“选 MOR 还是 EI”改成“在可证明误差下，自动决定何时复用、何时更新、何时清空 subspace”，直接连接 simulator control policy 与 linear algebra cost。第一个证伪实验应使用输入方向缓慢旋转后突然正交跳变、并夹入一次 topology switch 的 RC/RLC 网络；在相同 waveform-error budget 下与 static PRIMA、每步 EI 和无证书 heuristic reuse 比较 total LU 次数、Arnoldi vectors、wall time 与 missed event。若证书不能在突变前后同时维持误差且减少工作量，这个想法即被证伪。

与已有工作的实质区别候选在于：论文提到的 EI-MOR hybrid 仍是组合两类既有方法，而这里把“subspace 的有效域及其失效证据”设为一等状态，并让复用决策受可验证 certificate 驱动。由于本任务严格 PDF-only、没有检索 paper 外相关工作，这只是候选研究方向，不声称 novelty。
