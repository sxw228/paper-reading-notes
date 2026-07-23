# Portal Analysis Approach Used for the Efficient Electromagnetic Transient (EMT) Simulation of Power Electronic Systems

- Zotero key：`SKEEWQ9V`
- 作者：Chenxiang Gao, Jin Xu, Keyou Wang, Pan Wu, Zirun Li, Jianqi Zhou, Ryuichi Yokoyama
- 发表：IEEE Transactions on Power Delivery, 2023, 38(6), 4213–4225
- DOI：`10.1109/TPWRD.2023.3305035`
- 源文件：`_source.pdf`
- PDF SHA-256：`3443f5c02bfc9c58589adfc5012b7901f3bd390e4030be6b7bb7976b1e64886b`
- 阅读范围：PDF 物理页 1–13，含附录与参考文献

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样把同一个 nodal analysis（NA，节点分析）程序再并行一点”，而是一个更靠前的计算表示问题：在模块化、级联化的 power electronic（PE）系统中，EMT 仿真为什么必须在每个微秒级时间步反复维护和求解大量内部节点、支路信息，而系统级计算真正关心的往往只是组件端口的电压、电流？作者指出，高频开关与快速控制把暂态时间尺度拉到微秒至秒；若仍用高阶、随开关状态变化的节点导纳矩阵，MMC、PET 等大规模变换器的计算时间会变得不可接受。[pdf:E01]

物理上，一个端口是一对端子：端口电压是两端电位差，端口电流是穿过这对端子的单一流量。许多变换器和基本元件天然通过这种端口与外部网络交换能量。NA 却先把端口拆成两个节点和内部支路，再在全局矩阵中重建它们的关系，因此会重复存储和计算对外部行为没有新增信息的自由度。本文的研究问题可以精确写成：能否把 EMT 的基本组装与求解对象从“node-branch”改成“port-component”，仍保留 Dommel 离散、开关拓扑变化和 stamp（盖章式矩阵组装）的通用性，同时获得更低阶、可分区、可并行的代数系统？[pdf:E02]

这个问题重要在两层。第一层是计算量：EMT 每一步都要更新开关等值、求解网络、再更新历史源；矩阵阶数和依赖链会直接限制可模拟规模。第二层是工程结构：若提速只能依赖某一拓扑的手工等值，模型可维护性和拓扑变化能力会损失。作者试图同时保住通用 stamp 接口和低阶求解结构，而不是只做一个特例快速模型。[pdf:E02][pdf:E04]

## § 2 — 前人工作与不足

作者把已有加速路线分成三类。其一是 generalized Thevenin 等电路等值，通过消去内部节点获得高效模型；作者认为这类方法往往需要复杂的手工编程，且面对拓扑变化时通用性不足。其二是 TLM、latency insertion、controlled-source decoupling 等电路分区；它们用物理或人为延迟切断计算依赖，但可能引入数值稳定性或精度问题。MATE、node splitting 等数值分区更灵活、精确，却会被边界变量数量拖慢。其三是 minimum degree、minimum fill-in、KLU 等稀疏 LU 技术，它们利用节点导纳矩阵的稀疏性，但仍在 NA 表示里工作。[pdf:E01]

因此，作者所针对的具体缺口是：既有路线主要优化“如何解节点矩阵”，很少追问“节点是不是 PE 系统最经济的外部坐标”。PA 继承稀疏、分区和 stamp 思路，但先把方程换到端口坐标，再对得到的新矩阵结构做加速。[pdf:E02]

这里需保留证据边界：以上是本文对 prior work 的归纳，不是本卡对每篇引用文献的独立复核。本文没有给出统一代码基线去比较所有三类路线；实验只直接比较 PSCAD detailed model、同一 VS2022/C++ 环境中的 NA 模型，以及文献 [42] 的 equivalent hierarchical model（EHM）。[pdf:E09][pdf:E10]

## § 3 — 重建作者的思考路径

不预设 PA 已经存在，可以从四个旧事实走到它。

第一，Dommel EMT 本来就把电感、电容离散成 Norton admittance 与 history current source；开关也可表示为受脉冲控制的导纳。也就是说，每一步真正交给网络求解器的是一个线性代数接口，而不是元件内部微分方程本身。[pdf:E03]

第二，network theory 已经提供 Y-parameters：一个多端口组件的外部电流可以由端口电压和等值历史源描述。如果系统只通过端口与组件交换信息，那么每一步更新所有内部支路并非物理必需，而是坐标选择的结果。[pdf:E03][pdf:E04]

第三，NA 的 stamp 成功之处不在“节点”二字，而在于每个组件只向全局矩阵贡献局部、可定位的块。若端口模型也能形成 stamp，就有机会保留模块化和拓扑修改能力。[pdf:E04]

第四，端口连接比共享节点更复杂：串联端口共享电流而不共享电压，并联端口共享电压而电流受 KCL 约束。于是自然需要用 tearing 把网络切成局部块，并把共享电流或共享电压提升为少量边界未知量。只要边界变量少，Diakoptics/Schur-complement 型求解就能先解边界、再并行回代各分区。[pdf:E05][pdf:E06]

这条思考链的关键不是“发现端口很常见”，而是把端口的物理约束、组件外部等值、矩阵 stamp 和分块消元连成一个完整的 EMT 时间步。

## § 4 — 核心 Intuition

PA 的 intuition 是：不要在每个时间步展开并求解系统不关心的内部节点，把每个组件压成端口电压方程，只在组件连接处保留真正需要协调的电流或电压。这样，原来一个高阶全局 nodal solve 被改写成“很多低阶局部端口块 + 一个小边界问题”；端口 tearing 决定依赖边界，BBD 和带状结构才进一步把这些块变成可并行、近线性的计算。[pdf:E03][pdf:E06][pdf:E07]

## § 5 — 具体方法与完整 Pipeline

以一组级联 CHB-DAB power modules（PM）为例，PA 对一个 EMT 仿真步的结构改变如下。

1. **组件化表示。** 对 R、L、C、独立源、半桥、全桥、变压器、Boost 等组件，建立统一的端口方程
   \[
   \mathbf Y_P\mathbf v_P=\mathbf i_P+\mathbf j_P .
   \]
   \(\mathbf j_P\) 包含数值积分产生的 history source 和独立源贡献。对多端口组件，可通过端口短路试验直接求 Y-parameters，也可从低阶 nodal equation 转换。开关使 \(\mathbf Y_P\) 与 \(\mathbf j_P\) 系数随状态变化；作者建议初始化时预计算可能值。[pdf:E03][pdf:E04]

2. **端口 stamp 组装。** 每个组件依据 type、from-port、to-port 把局部 \(y_{ii},y_{ij},j_i\) 写入全局端口矩阵和源向量。与 NA 类似，增加、删除或切换组件只改对应矩阵元素，不必重建全部数据结构。[pdf:E04]

3. **按连接类型 tearing。** 串联端口用共享电流 \(i_{\mathrm{Ser}}\) 作为边界未知量，并用 KCL/KVL 写入 incidence matrix；论文的三分区示例只增加一个边界量，而且受控源只是方程表达，不引入仿真延迟。[pdf:E05] 并联端口若直接以各支路电流为边界，分区数 \(M\) 会带来 \(M-1\) 个电流未知量；作者因此转用 inverse hybrid \(G\)-parameters，以公共电压 \(v_{\mathrm{Par}}\) 为边界，使附加边界量与并联网络数量无关、始终为一个。[pdf:E06]

4. **形成 BBD 扩展方程。** 串、并联 tearing 合并后，时间步网络方程写成
   \[
   \begin{bmatrix}
   \mathbf G_{P,\mathrm{block}} & \mathbf Q\\
   \mathbf Q^\mathsf T & \mathbf 0
   \end{bmatrix}
   \begin{bmatrix}
   \mathbf p_P\\
   \mathbf l_{SP}
   \end{bmatrix}
   =
   \begin{bmatrix}
   \mathbf s_P\\
   \mathbf 0
   \end{bmatrix},
   \]
   其中 \(\mathbf p_P\) 是各分区内部端口未知量，\(\mathbf l_{SP}\) 只包含串联边界电流和并联边界电压。这一步把原本全局耦合的 nodal matrix 变成 block-bordered-diagonal（BBD，块对角加小边界）结构。[pdf:E06]

5. **先边界、后局部。** Diakoptics 消元先用各小块 \(\mathbf G_{Pk}^{-1}\) 累加出边界系统，求 \(\mathbf l_{SP}\)；随后各分区的 \(\mathbf p_{Pk}\) 独立回代。全局高阶逆不再显式出现，跨分区同步只发生在小边界量上。[pdf:E06][pdf:E07]

6. **利用带状结构。** CHB-DAB PM 示例每个模块有 5 个端口、6 个组件；单端口/双端口连接使局部 \(\mathbf G_{Pk}\) 只有主对角线上下相邻元素非零，形成 tridiagonal/1-band matrix。作者用 band sparse LU/TDMA 思路把局部求解降到 \(O(n)\)，并只存三条对角向量而非完整矩阵；\(\mathbf Q_k\) 也仅有两个非零元素。[pdf:E07]

7. **每步执行。** 初始化阶段读 netlist、建立组件与分区、生成 \(\mathbf Q,\mathbf G_P,\mathbf s_P\)。每一仿真步先按 firing pulse 或拓扑变化局部修改 \(\mathbf G_P\)，再求边界和各分区，最后并行更新 \(\mathbf v_P,\mathbf i_P,\mathbf s_P\) 并输出。实现使用 VS2022/C++。[pdf:E07]

因此，PA 改变 EMT 计算结构的顺序是：**先压缩状态表示，再暴露小边界依赖，最后对局部块并行和带状求解**。若只把它理解成 parallel sparse LU，会漏掉最主要的阶数和数据更新缩减。

## § 6 — 核心数学推导

先看为什么端口坐标能消除冗余。论文的两端口示例有 4 个节点、2 个端口。NA 与 PA 分别写成
\[
\mathbf Y_N\mathbf v_N=\mathbf i_N+\mathbf j_N,\qquad
\mathbf Y_P\mathbf v_P=\mathbf i_P+\mathbf j_P.
\]
端口—节点 incidence matrix \(\mathbf M\) 满足
\[
\mathbf M\mathbf v_N=\mathbf v_P,\qquad
\mathbf M^\mathsf T\mathbf i_P=\mathbf i_N.
\]
代入后得到
\[
\mathbf Y_N=\mathbf M^\mathsf T\mathbf Y_P\mathbf M,\qquad
\mathbf j_N=\mathbf M^\mathsf T\mathbf j_P.
\]
物理意义是：NA 的 4 阶矩阵其实把 2 阶端口关系沿端子展开；PA 直接保留未展开的外部关系。[pdf:E03]

多端口组件的直接求法也很直观：短接除端口 \(i\) 外的其他端口，在 \(i\) 端注入电流，得到输入导纳 \(y_{ii}\) 与 transfer admittance \(y_{ij}\)；把所有端口短路则得到 history-source 向量。附录用 Boost converter 展示了开关导纳 \(G_1,G_2\)、电感/电容 Norton 等值 \(G_L//j_L,G_C//j_C\) 如何组成 \(\mathbf Y_P,\mathbf j_P\)，也给出从 3 阶 nodal matrix 和 2×3 incidence matrix 转成 2 端口方程的另一条路径。[pdf:E04][pdf:E12]

分区求解的核心是对 BBD 方程消元。边界量可写为
\[
\mathbf l_{SP}
=
\left(\sum_k \mathbf Q_k^\mathsf T\mathbf G_{Pk}^{-1}\mathbf Q_k\right)^{-1}
\left(\sum_k \mathbf Q_k^\mathsf T\mathbf G_{Pk}^{-1}\mathbf s_k\right),
\]
再由
\[
\mathbf p_{Pk}
=
\mathbf G_{Pk}^{-1}\mathbf s_k
-\mathbf G_{Pk}^{-1}\mathbf Q_k\mathbf l_{SP}
\]
并行恢复各分区。这里真正昂贵的全局同步只剩边界矩阵；每个 \(\mathbf G_{Pk}\) 都可独立因式分解和回代。[pdf:E06][pdf:E07]

这个推导成立于作者采用的线性等值框架。开关非线性被离散为有限状态导纳切换，而不是在每一步求连续 nonlinear algebraic equation；这也是速度与适用范围同时产生的地方。[pdf:E04][pdf:E11]

## § 7 — 实验设计与结论

**问题 1：端口方程是否仍能捕获真实开关动态？** 作者搭建 30 V down-scaled DAB prototype，开关频率 20 kHz，比对输出电压和电感电流。实验与 PA 仿真中输出电压都跟踪 30 V；电感电流峰值分别为 4.5 A 与 4.38 A，作者报告相对误差 2.67%。这项测试说明 PA 至少能重现该 DAB 的稳态开关波形，但它不是“所有误差都小于 2%”的证据。[pdf:E08]

**问题 2：复杂暂态下是否与 detailed EMT benchmark 一致？** 作者在 PSCAD/EMTDC 建立 CHB-DAB PET + PV + BESS microgrid detailed model，并在 PA 中复现启动、2 ms DC short circuit、输出电压参考变化、PV/BESS 接入、辐照变化与 BESS 功率参考变化。LVDC bus voltage 的 maximum relative error（MRE）为 1.57%；高频 PWM 和变压器二次电压工况中，作者报告 MRE 持续低于 2%；功率重分配曲线与 NA benchmark 接近。[pdf:E08][pdf:E09]

**问题 3：提速来自哪里、如何随规模变化？** 作者在同一 VS2022/C++ 环境、Intel i9-12900H/16 GB RAM、1 μs 步长下，模拟 1 s、9–45 个 PM 的三相 PET，并分别计时 network solution、matrix modification、circuit-information update 和 control 等环节。[pdf:E09] 对 27 PM，NA 总 CPU 时间 183.026 s，PA 为 6.660 s；其中 network solution 从 174.940 s 降到 3.728 s。矩阵阶数从 195 降到 146，基本 circuit units 从 547 降到 169。[pdf:E10]

随 PM 从 9 增至 45，PA network-solution time 从 1.234 s 增至 7.966 s，论文据此判断近似线性；NA 对应值从 13.632 s 增至 959.411 s。45 PM 时，PA 总时间为 12.836 s，NA 为 974.406 s，PSCAD detailed model 为 2619.0 s；Table VII 给出的 PA 相对 PSCAD speedup factor 为 204.0。[pdf:E10]

结论边界同样重要：这些是 CPU 离线执行时间，不是 FPGA/HIL 板级结果；即使 45 PM 的 PA 已显著加速，模拟 1 s 仍花 12.836 s，因此论文没有证明 hard real-time deadline。文中“parallel processing”也未报告线程数、核心绑定、同步开销或硬件资源利用率。[pdf:E09][pdf:E10]

## § 8 — Take-aways

**5 句话：**

1. PA 通过端口坐标压缩 PE 系统 EMT 中对外部行为无新增信息的内部节点自由度。[pdf:E03]
2. component stamp 保留了 NA 的模块化与拓扑修改接口，开关状态只需局部更新预计算端口参数。[pdf:E04][pdf:E07]
3. serial/parallel port tearing 把系统整理成局部端口块与少量边界电流/电压，避免用人为延迟换并行。[pdf:E05][pdf:E06]
4. BBD 消元和带状局部矩阵让 network solve 从全局高阶依赖变成小边界同步加独立分区回代。[pdf:E06][pdf:E07]
5. PET benchmark 显示显著 CPU 加速且暂态误差较小，但证据集中在端口丰富、LTI 等值成立的 DAB/PET 场景，并未证明通用 nonlinear 或 real-time 能力。[pdf:E08][pdf:E09][pdf:E10][pdf:E11]

**3 句话：** PA 的主要贡献是改变 EMT 方程的坐标和依赖图，而不只是换一个线性求解器。端口压缩、少边界 tearing、BBD/带状求解三者必须同时成立，论文中的规模收益才会出现。实验支持 DAB/PET 场景的精度和离线 CPU 效率，但真实适用边界由端口压缩率、边界规模、局部矩阵带宽和 LTI 等值质量共同决定。

**1 句话：** 把 PE-EMT 从“求所有节点”改成“协调少数端口”，才是 PA 的计算结构创新。

## § 9 — 最脆弱的假设

最脆弱的假设是：**目标 PE 系统能够被压缩成低阶、稀疏/带状的端口组件，而 tearing 后的边界变量数量相对系统规模保持很小。** 若这个假设不成立，PA 的核心优势会同时失去：端口矩阵阶数接近 nodal matrix，multi-port component 的外部等值可能变稠密，边界 Schur complement 变大，局部矩阵也不再适合 TDMA。

论文提供的正证据来自 CHB-DAB/PET：单相 AC/DC 端口占比高，PM 结构重复，局部 \(\mathbf G_{Pk}\) 呈 1-band，边界量主要是三相电流和 LVDC 电压；对应 benchmark 确实表现出 network-solution time 近线性增长。[pdf:E07][pdf:E10] 论文自己也给出反向边界：不对称条件下的 three-phase port 在 nodal equation 中没有冗余，PA 不降低矩阵阶数；三相端口占比高时效率会减弱。[pdf:E11]

这比“LTI 限制”更直接威胁论文的加速 claim，因为即使 nonlinear component 可以另外建模，只要端口压缩率与小边界条件消失，整体框架仍可能正确，却不再高效。本文没有测试 meshed network、dense multi-port component、边界数随规模增长，或非重复拓扑，因此无法知道速度拐点在哪里。这个判断是基于论文结构和未覆盖工况的推断，不是作者已实测的结论。

## § 10 — 最小复现实验

一周内最有价值的最小复现不是重建完整 PV+BESS microgrid，而是做一个同源双求解器的 CHB-DAB 扩展实验。

- **数据与模型：** 采用论文 Table III 的 PET 关键参数、1 μs 步长，先实现每相 3 PM（共 9 PM），再复制到 18、27 PM；控制和 switch-state sequence 对 NA、PA 共用，避免把控制差异误算成求解器差异。[pdf:E08][pdf:E09]
- **实现：** 同一 C++ 或 Python/NumPy 原型中实现 Dommel Norton companion、NA stamp 与 PA component stamp。PA 端按 equations (22)–(25) 建 BBD 边界解，并保留 network solve、matrix update、state update 的独立计时。[pdf:E06][pdf:E07]
- **正确性测量：** 每一步比较 port voltages/currents，并在一个 DC-fault 清除或参考值阶跃上计算 MRE；另做一次离散功率平衡检查，确保没有 tearing latency。
- **结构测量：** 记录 nodal/portal matrix order、nonzero count、boundary dimension、factorization time、solve time、update time和总时间，而不只报 speedup。
- **支持标准：** 在相同离散和开关序列下，关键波形 MRE 不超过 2%，且 PA 的 network-solve time 从 9 到 27 PM 近似按 PM 数增长，同时边界维数不增长。[pdf:E09][pdf:E10]
- **反驳标准：** 若误差在 switching event 附近系统性增大、必须引入一步延迟才能分区，或边界/填充增长使 PA 与 NA 呈相同扩展趋势，则论文的关键机制没有被复现。

这个实验不声称复现作者全部结果；它只同时验证“代数等价、无延迟 tearing、计算依赖重构”这三个最核心 claim。

## § 11 — 最强反例设计

最强反例应构造一个**端口很多但不可压缩**的 EMT 系统，而不是单纯换一台更慢的电脑。具体可用不对称三相 meshed converter network：每个组件带强耦合 three-phase multi-port model，变压器含 magnetic saturation，线路用多段 distributed parameter model，并让多个分区通过许多端口交叉连接。

对这一系统同时运行：

1. 全局 NA + 同一 sparse LU；
2. 固定 PA；
3. 不做 tearing 的 portal equation，作为区分“端口压缩收益”和“分区收益”的对照。

逐规模记录端口/节点阶数比、boundary dimension、Schur complement fill-in、局部矩阵带宽、每步 nonlinear/component update 时间和总时间。若 PA 的矩阵阶数不降、边界矩阵趋密，且即使数值轨迹与 NA 一致也没有稳定 speedup，便说明论文的“一到两个数量级加速”主要来自 PET 的重复、单相/DC 端口结构，不能外推为一般 PE system 性质。若加入饱和后必须频繁重建 dense port model，PA 还可能因组件等值更新成本而落后。[pdf:E11]

这个反例直接攻击第 9 节的结构假设；它不会把“不支持某个 nonlinear model”误当作纯实现缺陷，而是检验端口表示是否仍能产生作者依赖的低阶、小边界和带状性。

## § 12 — Follow-up Research Idea

**候选想法：自适应混合坐标 EMT 求解器。** 不再要求整张网络固定使用 node 或 port 表示，而是让每个组件/分区在初始化或拓扑事件后，依据可验证的代数代价选择 nodal、portal 或保留内部 state-space 坐标；求解器自动生成跨坐标接口，并以“最小全局耦合代价”而不是“最少节点”作为 partition objective。这里不声称 novelty，因为本卡没有对 mixed-coordinate circuit simulation 做外部检索。

**(a) 未满足需求。** PA 在 PET/MMC 类端口丰富、重复模块上很强，但 three-phase dense coupling、nonlinear magnetics 或复杂线路可能没有压缩收益；全局固定表示会把局部优势变成全局限制。[pdf:E11]

**(b) 研究价值。** 电力与控制领域会更看重可验证的数值等价、跨拓扑稳定性、真实 execution deadline 与工程适用域。若求解器能对异构 PE network 自动选择表示，并给出选择前后的 matrix order、fill-in、boundary size 和 worst-case step time，它改变的是建模与求解共同优化的问题定义，而不是给 PA 追加一个加速模块。

**(c) 可借鉴工具。** 可借鉴 sparse direct solver 的 fill-reducing ordering、graph partitioning 的 separator cost，以及 compiler 的 cost model；每个候选组件表示先生成局部 symbolic sparsity，再估计 Schur fill-in 和事件更新成本。

**(d) 第一个证伪实验。** 建立由 CHB-DAB 模块、不对称 three-phase transformer、饱和支路和 distributed line 组成的异构 benchmark，让固定 NA、固定 PA、mixed solver 在同一离散与硬件上比较轨迹误差和 99.9th-percentile step time。若 mixed solver 的重分区/接口开销超过局部收益，或在开关与饱和事件附近破坏等价性，该方向应被否定。

**(e) 与本文的实质区别。** 本文先假定网络具有适合 PA 的 port characteristic，再把整个系统改写为 portal equation；候选方向把“是否用端口坐标”本身变成可测量、可撤销的局部决策，并把 nonlinear/event update cost 纳入分区目标。

### 证据索引

| ID | PDF 物理页 | 主要定位 | 文件 |
|---|---:|---|---|
| E01 | 1 | 标题、摘要、问题背景、既有加速分类 | `_evidence/E01-p001-title-abstract-intro.png` |
| E02 | 2 | Fig. 1、port characteristic、三项理论贡献 | `_evidence/E02-p002-port-view-contributions.png` |
| E03 | 3 | equations (1)–(4)、node/port 阶数关系、统一组件描述 | `_evidence/E03-p003-nodal-portal-eq01-04.png` |
| E04 | 4 | equations (5)–(9)、多端口参数获取、component stamp | `_evidence/E04-p004-component-model-stamps-eq05-09.png` |
| E05 | 5 | serial tearing、equations (10)–(16)、无 latency 说明 | `_evidence/E05-p005-serial-tearing-eq10-16.png` |
| E06 | 6 | parallel tearing、G-parameters、BBD equations (17)–(24) | `_evidence/E06-p006-parallel-tearing-bbd-eq17-24.png` |
| E07 | 7 | equation (25)、Fig. 7 带状矩阵、Fig. 8 全流程 | `_evidence/E07-p007-schur-band-pipeline-eq25-fig07-08.png` |
| E08 | 8 | DAB prototype、Table II、PET microgrid、实验误差 | `_evidence/E08-p008-dab-prototype-microgrid-fig09-11.png` |
| E09 | 9 | Table III、Figs. 12–13、MRE、效率实验设置 | `_evidence/E09-p009-accuracy-efficiency-fig12-13-eq26.png` |
| E10 | 10 | Tables IV–VII、Figs. 14–16、CPU time 与矩阵阶数 | `_evidence/E10-p010-cpu-matrix-results-tab04-07.png` |
| E11 | 11 | Fig. 17、适用域、LTI 与 three-phase 限制、结论 | `_evidence/E11-p011-discussion-limitations-conclusion.png` |
| E12 | 12 | Boost 附录 equations (28)–(31)、references 起始 | `_evidence/E12-p012-boost-port-derivation-eq28-31.png` |
