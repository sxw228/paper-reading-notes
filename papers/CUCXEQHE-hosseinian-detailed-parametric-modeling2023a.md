# Detailed Parametric Modeling of AC-DC Converters for EMT Simulators

- Zotero key：`CUCXEQHE`
- canonical slug：`hosseinian-detailed-parametric-modeling2023a`
- 作者：Parastoo Sadat Hosseinian；Seyyedmilad Ebrahimi；Juri Jatskevich
- 年份与出处：2023，*IEEE Open Journal of Power Electronics*，Vol. 4，pp. 965-977
- DOI：`10.1109/OJPEL.2023.3328112`
- 唯一内容真相：`_source.pdf`
- PDF SHA-256：`bd744f4d3fd58560db8bf78dd9261bb75a13978f5b2061051114e5bc0187e4ab`
- 阅读口径：以下“论文声称”只表示作者在本文中明确写出或展示；“基于证据的推断”“候选判断”表示本文没有直接证明的分析。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“如何更粗略地模拟变换器”，而是一个更尖锐的矛盾：在 electromagnetic transient（EMT，电磁暂态）仿真中，既想保留二极管/晶闸管 line-commutated rectifier（LCR）和两电平 voltage-source converter（VSC）的开关波形、谐波、纹波与尖锐边沿，又不想让求解器为了逐个处理开关事件而被迫使用约 10 μs 甚至更小的步长。传统 detailed switching model（DSM）逐器件表示开关，细节可信，但离线仿真会变慢，实时仿真还会面临单步计算超过实时窗口的 overrun；事件插值虽可缓解离线误差，却有额外计算成本，并不天然适合实时、固定步长、非迭代求解。[pdf:E01](_evidence/E01-p001-abstract-core-claim.png) [pdf:E02](_evidence/E02-p002-prior-work-contributions.png)

物理上，困难来自两个时间尺度的冲突。系统级网络关注的是毫秒到秒级暂态，但变换器端口波形包含由换相或 PWM 产生的更快细节。DSM 用很密的时间网格“追着每一次开关跳变走”；本文则试图把一个开关周期内反复出现的端口波形结构预先学成参数函数，仿真时直接重建当前采样点的电压和电流。这不是平均掉开关细节，而是用不发生电路拓扑切换的代数关系再现这些细节。[pdf:E01](_evidence/E01-p001-abstract-core-claim.png) [pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)

其价值主要落在两类任务。第一，含大量变换器的离线 EMT 研究可以减少总步数，同时仍观察谐波和 dc ripple；第二，RTDS NovaCor 一类实时平台可以在固定计算预算内承载更大的 EMT 网络。作者报告，直接接口模型在本文算例中可把 LCR 的最大有效步长提高到 150-200 μs，把 VSC 提高到 50 μs，而对照 DSM 的表中上限为 10 μs；这些数字是本文特定系统与判据下的结果，不能直接外推到任意变换器。[pdf:E10](_evidence/E10-p010-vsc-results-and-performance-tables.png)

## § 2 — 前人工作与不足

论文把既有方法分成三条路线。第一条是 DSM：商业 EMT 程序已有成熟组件，逐个半导体器件处理开关状态，因此能给出详细波形；不足是大量离散事件和很小步长。某些实时 switching prediction 方法仍然依赖小步长。离线插值与 zero-crossing detection 可以提高事件时刻精度，但会增加数值处理，并不等价于一个适合固定步长实时求解的低成本模型。[pdf:E01](_evidence/E01-p001-abstract-core-claim.png) [pdf:E02](_evidence/E02-p002-prior-work-contributions.png)

第二条是 dynamic phasor model 和 average-value model（AVM）。它们通过只保留基波、平均量或选定谐波，允许系统级研究使用大步长，却牺牲了逐开关波形。parametric AVM（PAVM）用代数参数函数关联 ac/dc 平均量；generalized PAVM（GPAVM）可在多个旋转 qd 坐标系中重建选定谐波，但增加谐波就增加复杂度；hybrid PAVM/detailed model（HPAVM）用一个 qd 变换和额外参数函数重建谐波与纹波，但平均部分与振荡部分仍分开计算。本文认为这些模型的共同边界是：参数关系建立在 average-value 上，而不是完整瞬时波形上。[pdf:E02](_evidence/E02-p002-prior-work-contributions.png)

第三条是接口方法。用受控电压/电流源把 AVM 接到外部网络，在 PSCAD 这类非迭代 EMTP 求解中通常会引入一拍延迟：网络先给模型旧时刻的端口量，模型再回送新输出。步长增大后，这个延迟可能造成误差甚至不稳定。已有 direct interfacing 工作通过线性化平均值关系，把变换器等效电导并入全网节点方程，但仍只保留基波和 dc 平均量。本文的具体推进，是把“瞬时详细参数模型”和“直接节点接口”放在同一套模型中。[pdf:E02](_evidence/E02-p002-prior-work-contributions.png) [pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png)

需要严格限定 novelty：上述比较是本文作者对其引用文献的归纳，本卡没有读取那些先前论文，因此不能独立宣称本文是首个或唯一方案。

## § 3 — 重建作者的思考路径

以下是基于论文证据的合理重建，不是作者逐字陈述。

第一步，从传统 AVM 的成功经验出发：LCR/VSC 的端口关系虽然由快速开关生成，却不是完全无结构的噪声。把三相量变换到随电源角度旋转的 qd 坐标后，基波变成近似直流量，开关谐波表现为周期纹波；dc 侧本来也由平均量加纹波组成。于是 ac 与 dc 两侧的“整条瞬时波形”可能仍能用少数周期参数关系表示。[pdf:E03](_evidence/E03-p003-system-reference-frames-waveforms.png)

第二步，把平均值参数函数改造成瞬时量参数函数。不要分别计算基波、平均值和各次纹波，而是在每个时刻直接记录三个比值/相角关系：dc 电流相对 qd 电流幅值的比例、qd 电压幅值相对 dc 电压的比例、以及 qd 电流与电压向量的夹角。这样，波形细节不是额外叠加的修正项，而是参数函数随电角度变化时自然带出的结果。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)

第三步，承认这些函数在有损耗、非线性和不同工况下很难解析推导，因此以高保真 DSM 作为离线“教师”：扫描控制量和负载，计算函数样本并存成 lookup table（LUT，查找表）。在线 EMT 仿真只需要查询 LUT 与重建端口量，不再切换拓扑。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png) [pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)

第四步，发现仅有非开关模型还不够。若它仍通过旧一拍的端口变量与网络交换，步长继续增大时会被接口延迟限制。因此先给出易于在现有元件库中实现的 indirect interface，再把非线性瞬时端口关系在上一时刻线性化成 Norton 等效，直接并入节点方程，从接口层消除那一拍延迟。[pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png) [pdf:E07](_evidence/E07-p007-direct-nodal-linearization.png)

## § 4 — 核心 Intuition

变换器的开关细节虽然快，但在给定拓扑、控制量和工况范围内会随电角度重复；因此可以用离线 DSM 把“一个重复周期内，ac/dc 端口量如何瞬时对应”制成 LUT，在线时直接重建波形而不重演每次开关。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)

真正让大步长继续有效的第二个关键，是把重建后的非线性端口关系变成当前时间步可与外部网络同时求解的电导矩阵和历史电流，而不是隔一拍交换受控源信号。[pdf:E07](_evidence/E07-p007-direct-nodal-linearization.png)

## § 5 — 具体方法与完整 Pipeline

以三相六脉波二极管 LCR 为例，完整流程分成一次性的离线建表和每个 EMT 时间步的在线计算。

**离线建表**

1. 用传统 DSM 搭建 Fig. 1 的 ac-LCR-dc 系统。ac 子系统用平衡正弦 Thévenin 源及 \(r_s,L_s\) 表示，三相端口电压、电流通过 Park 变换进入随源角 \(\theta_s\) 旋转的 qd 坐标。[pdf:E03](_evidence/E03-p003-system-reference-frames-waveforms.png)
2. 扫描目标工况。晶闸管 LCR 扫描 firing angle \(\alpha\) 和等效 dc 负载 \(R_l\)；二极管 LCR 没有 \(\alpha\) 这一控制维。VSC 则扫描 modulation index \(M\)、功角 \(\delta\) 和负载。论文用改变电阻负载来覆盖 dynamic impedance，并称所得函数也可用于其他 dc 负载组成；这是一项作者主张，而不是本卡独立验证。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png) [pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)
3. 在每个 DSM 采样点计算 \(w_i,w_v,\phi,z_d,\theta_{\mathrm{rec}}\)。六脉波 LCR 的纹波周期为 \(\beta=2\pi/p=\pi/3\)，因此只保存一个重复周期。对本文采用的同步 SPWM VSC，作者选择奇数且为 3 的倍数的 switching-frequency ratio，使 ac 谐波阶次为 \(6m\pm1\)，dc 与 qd 纹波阶次为 \(6m\)，同样取 \(\beta=\pi/3\)。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)
4. LCR 把样本存成以 \(z_d,\alpha,\theta_{\mathrm{rec}}\) 为坐标的 3-D LUT；VSC 存成以 \(M,\delta,z_d,\theta_{\mathrm{rec}}\) 为坐标的 4-D LUT。在线输入落在网格点之间时做线性插值。建表时间与内存随覆盖范围和分辨率增长，但这是一次性工作。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)

**在线重建**

1. 当前步输入是 LCR 的 \(\alpha\) 或 VSC 的 \(M,\delta\)，以及 \(\theta_s,v_{dc},i_{abc}\)。先将 \(i_{abc}\) 变换为 \(i_{qd}^{s}\)，再算 \(z_d\) 和 \(\theta_{\mathrm{rec}}\)。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)
2. 用这些坐标查询 \(w_i,w_v,\phi\)。由 \(i_{dc}=w_i\lVert i_{qd}^{s}\rVert\) 得到 dc 侧电流；由 \(w_vv_{dc}\) 与相角关系重建 \(v_q^s,v_d^s\)，最后通过 Park 逆变换得到 \(v_{abc}\)。因此外部网络看到的是三相受控电压端口和 dc 电流端口，而模型内部没有六个离散开关不断改变节点拓扑。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png) [pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png)

**两种网络接口**

- IDI-DNSM 用受控源直接接入现有元件库。非迭代 EMTP 程序当前步还没有算出 \(v_{dc}(t)\) 和 \(i_{abc}(t)\)，所以模型实际使用上一时刻输入。某些 dc 网络还需并联 snubber \(R_x\)，再用 \(i_{\mathrm{comp}}(t)=v_{dc}(t-\Delta t)/R_x\) 抵消稳态误差。优点是实现简单，缺点是一拍延迟限制大步长稳定性。[pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png)
- DI-DNSM 在 \(t-\Delta t\) 处对 qd-dc 非线性电压关系线性化，构成 4 端口电阻矩阵 \(R_{\mathrm{CON}}\) 与历史电压项；变换回 abc 后计算 \(G_{\mathrm{CON}}=R_{\mathrm{CON}}^{-1}\)、\(I_{h\mathrm{CON}}=-R_{\mathrm{CON}}^{-1}e_{h\mathrm{CON}}\)，并把它们直接装入全网节点方程。网络节点电压与变换器电流因此在同一步同时求解，无需接口迭代、旧一拍输入、外部 snubber 或补偿源。[pdf:E07](_evidence/E07-p007-direct-nodal-linearization.png)

## § 6 — 核心数学推导

先看物理量。Park 变换

\[
v_{qd}^{s}=K(\theta_s)v_{abc},\qquad i_{qd}^{s}=K(\theta_s)i_{abc}
\]

把三相基波投影到与电源相位同步旋转的二维坐标。若波形只有理想基波，qd 分量接近常数；开关产生的谐波则成为 qd 上的周期纹波。这使“对一个周期建表”成为可能。[pdf:E03](_evidence/E03-p003-system-reference-frames-waveforms.png)

论文用三个瞬时参数函数压缩端口关系：

\[
w_i=\frac{i_{dc}}{\lVert i_{qd}^{s}\rVert},\qquad
w_v=\frac{\lVert v_{qd}^{s}\rVert}{v_{dc}},
\]

\[
\phi=\tan^{-1}\!\left(\frac{i_d^s}{i_q^s}\right)
-\tan^{-1}\!\left(\frac{v_d^s}{v_q^s}\right).
\]

\(w_i\) 表示“同一时刻 qd 电流幅值对应多少 dc 电流”，\(w_v\) 表示“dc 电压对应多少 qd 电压幅值”，\(\phi\) 保存电流向量与电压向量的相对方向。工况用

\[
z_d=\frac{v_{dc}}{\lVert i_{qd}^{s}\rVert}
\]

参数化，周期位置用 \(\theta_{\mathrm{rec}}\) 表示。对六脉波 LCR，\(\beta=2\pi/6=\pi/3\)，因此 \(\theta_{\mathrm{rec}}\) 每 60 电角度重复。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)

在线重建是上述定义的反用：

\[
i_{dc}=w_i\lVert i_{qd}^{s}\rVert ,
\]

\[
v_q^s=w_vv_{dc}\cos\!\left[
\tan^{-1}\!\left(\frac{i_d^s}{i_q^s}\right)-\phi
\right],
\]

\[
v_d^s=w_vv_{dc}\sin\!\left[
\tan^{-1}\!\left(\frac{i_d^s}{i_q^s}\right)-\phi
\right],
\qquad
v_{abc}=K^{-1}(\theta_s)v_{qd}^{s}.
\]

这里的关键不是公式复杂，而是 LUT 给出的 \(w_i,w_v,\phi\) 已含开关周期内的纹波结构；所以在一个较大的固定步长采样点，模型能直接给出该时刻应有的详细端口量。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)

直接接口再做一次局部线性化。把四个端口电压写成四个端口电流的函数，在上一时刻求 Jacobian，得到

\[
V_{\mathrm{CON}}=R_{\mathrm{CON}}I_{\mathrm{CON}}+e_{h\mathrm{CON}}.
\]

其中 \(R_{\mathrm{CON}}\) 的元素既含 \(w_i,w_v,\phi\)，也含它们通过 \(z_d\) 对电流变化的影响。Park 逆变换把 qd 电阻关系转为 abc-dc 四端口矩阵；求逆后得到 Norton 形式

\[
G_{\mathrm{CON}}=R_{\mathrm{CON}}^{-1},\qquad
I_{h\mathrm{CON}}=-R_{\mathrm{CON}}^{-1}e_{h\mathrm{CON}}.
\]

把 \(G_{\mathrm{CON}}\) 和 \(I_{h\mathrm{CON}}\) 装入全网节点方程，才是 DI-DNSM 能去掉接口一拍延迟的数学原因。[pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png) [pdf:E07](_evidence/E07-p007-direct-nodal-linearization.png)

## § 7 — 实验设计与结论

**问题 1：LCR 在稳态模式变化和负载突变时，能否以更大步长重建完整波形？**  
实验：六二极管 LCR 从 \(R_l=5\,\Omega,L_l=2\,\mathrm{mH}\) 的 CCM-1 工况，在 \(t=2\,\mathrm{s}\) 把 \(R_l\) 降为 \(0.5\,\Omega\)，进入 CCM-2；PSCAD/RSCAD DSM 用 10 μs，IDI-DNSM 用 70 μs，DI-DNSM 用 200 μs。作者报告四组 \(v_a,i_a,v_{dc},i_{dc}\) 在稳态和暂态中基本一致；当 DSM 也强行用 70 μs 时，其事件处理产生明显失真，而 IDI-DNSM 仍保持波形。[pdf:E08](_evidence/E08-p008-di-dnsm-flow-and-study-setup.png) [pdf:E09](_evidence/E09-p009-lcr-transient-results.png)  
答案：在本文二极管 LCR 工况下，参数模型确实把有效步长上限从 10 μs 提高到 70/200 μs，同时保留论文图中可见的波形细节。

**问题 2：受控晶闸管换相与 firing-angle 阶跃是否仍可覆盖？**  
实验：晶闸管 LCR 初始 \(\alpha=35^\circ,R_l=3.5\,\Omega,L_l=10\,\mathrm{mH}\)，在 \(t=2\,\mathrm{s}\) 同时把 \(R_l\) 改为 \(1\,\Omega\)、\(\alpha\) 改为 \(15^\circ\)。DSM、IDI-DNSM、DI-DNSM 分别用 10、50、150 μs。作者称三类模型对 ripple、harmonic 和 sharp edge 的暂态重建一致。[pdf:E09](_evidence/E09-p009-lcr-transient-results.png)  
答案：本文算例支持 LUT 对负载与控制量联合变化的覆盖，但没有给出跨建表范围外推的证据。

**问题 3：高频 PWM VSC 是否也适用？**  
实验：两电平 VSC 用 900 Hz SPWM。初始 \(M=0.6,\delta=-15^\circ\)，从 ac 向 dc 传输 80 MW；\(t=1\,\mathrm{s}\) 改为 \(M=0.8,\delta=-10^\circ\)，功率变为 70 MW；\(t=2\,\mathrm{s}\) 后 dc 电压源波动。DSM 用 10 μs，IDI-DNSM 用 25 μs，DI-DNSM 用 50 μs。论文图示各端口量吻合。需要注意，PSCAD 中单个开关构成的 VSC DSM 若关闭插值，准确步长需小于 0.01 μs；表中的 10 μs 对照依赖插值或 RSCAD substep VSC。[pdf:E10](_evidence/E10-p010-vsc-results-and-performance-tables.png)  
答案：本文支持 VSC 上 25/50 μs 的参数化重建，但对照的数值机制并非完全同质，解读“相对 10 μs 提升”时必须保留这一条件。

**问题 4：大步长是否转化为实际 CPU 收益？**  
实验：在 PSCAD 中对 30 s 暂态研究计时。二极管 DI-DNSM 在 200 μs 时为 1.9 s，晶闸管 DI-DNSM 在 150 μs 时为 2.1 s，VSC DI-DNSM 在 50 μs 时为 10.1 s；相应 10 μs DSM 分别为 16.4、19.6、43.1 s。相同步长 10 μs 时，参数模型并不总更便宜，例如二极管 DI-DNSM 为 28.6 s。[pdf:E10](_evidence/E10-p010-vsc-results-and-performance-tables.png)  
答案：收益主要来自允许减少时间步数，而不是单步计算天然比 DSM 更轻；这是理解本文性能 claim 的关键。

实验边界也很清楚：作者展示了 PSCAD 离线仿真和 RSCAD/NovaCor 实时波形，但 CPU 时间表来自 PSCAD build message；论文没有报告 FPGA 映射、资源占用、定点位宽或板级时序，不能把本文直接解释成 FPGA 实现结果。[pdf:E08](_evidence/E08-p008-di-dnsm-flow-and-study-setup.png) [pdf:E10](_evidence/E10-p010-vsc-results-and-performance-tables.png)

## § 8 — Take-aways

**5 句话**

1. 本文把 LCR/VSC 的 ac-dc 端口瞬时关系压缩成 \(w_i,w_v,\phi\) 三个随工况和电角度变化的参数函数，而不是平均掉开关细节。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)
2. 这些函数由 DSM 离线扫描生成，LCR 使用 3-D LUT，VSC 使用 4-D LUT，在线通过插值查询。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)
3. IDI-DNSM 易于用受控源实现，但一拍延迟会限制大步长；DI-DNSM 将线性化后的 Norton 等效直接并入节点方程，消除了这项接口限制。[pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png) [pdf:E07](_evidence/E07-p007-direct-nodal-linearization.png)
4. 本文三个系统中，DI-DNSM 的最大有效步长分别达到二极管 LCR 200 μs、晶闸管 LCR 150 μs、VSC 50 μs，并给出对应暂态波形和 PSCAD CPU 时间。[pdf:E09](_evidence/E09-p009-lcr-transient-results.png) [pdf:E10](_evidence/E10-p010-vsc-results-and-performance-tables.png)
5. 代价是模型有效性依赖建表教师、参数覆盖和低维映射是否足以区分真实内部状态；作者也承认模型不知道一个时间步内部的精确开关时刻。[pdf:E11](_evidence/E11-p011-performance-limitations-conclusion.png)

**3 句话**

1. 论文用 DSM 离线建表、DNSM 在线重建，把开关细节从“实时处理事件”改成“按参数查询瞬时端口关系”。  
2. 直接节点接口使这一重建能在当前时间步与网络同时求解，所以大步长不仅不会被拓扑切换限制，也不再被受控源的一拍延迟限制。  
3. 算例显示显著步长与 CPU 收益，但外推到新的拓扑、器件效应、调制策略或运行域之前，必须重新验证 LUT 的状态充分性和覆盖范围。

**1 句话**

这是一种以离线 DSM 数据换取在线 EMT 步长的详细端口代理模型，其成败取决于“选定 LUT 坐标能否唯一决定当前瞬时端口关系”。

## § 9 — 最脆弱的假设

最脆弱的假设不是“LUT 插值足够快”，而是更根本的**低维、单值闭包假设**：对本文给定的变换器与系统参数，只要知道 LCR 的 \((z_d,\alpha,\theta_{\mathrm{rec}})\) 或 VSC 的 \((M,\delta,z_d,\theta_{\mathrm{rec}})\)，\(w_i,w_v,\phi\) 就是唯一且平滑到足以线性插值的函数。换句话说，两段不同历史若在当前时刻落到同一个 LUT 坐标，必须产生相同的瞬时 ac-dc 端口关系。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png) [pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png)

这个假设可能因未显式进入坐标的内部状态而失效，例如换相重叠随源阻抗变化、器件温度与压降、dead time、磁性元件饱和、控制器限幅、非平衡源、不同调制策略，或同一 \(z_d\) 下不同历史造成的内部能量分布。此时 LUT 会发生“坐标碰撞”：输入键相同，DSM 真值却不同；任何单值插值都只能选一个错误折中。论文的测试使用固定系统参数和预设调制策略，说明方法在这些覆盖域内有效，但没有做专门的坐标碰撞或 out-of-distribution 检验。[pdf:E08](_evidence/E08-p008-di-dnsm-flow-and-study-setup.png) [pdf:E10](_evidence/E10-p010-vsc-results-and-performance-tables.png)

作者给出的边界与这一判断相呼应：DNSM 只有在生成 LUT 的 reference model 已包含某项特性时才能复制它；模型虽能在固定步长采样点预测端口量，却不知道发生在步长内部的精确开关时刻，并建议未来借鉴 UCM 的预测算法。作者还明确指出建表时间和内存取决于范围与分辨率。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png) [pdf:E11](_evidence/E11-p011-performance-limitations-conclusion.png)

因此，本文证据支持的是“在已覆盖的固定参数族中可大步长详细重建”，尚不支持“同一组低维坐标对任意运行历史和参数漂移都充分”。

## § 10 — 最小复现实验

一周内最值得复现的不是完整三类变换器，而是二极管六脉波 LCR 的核心闭环：验证“瞬时 LUT + 间接接口能否在 70 μs 下保留 10 μs DSM 波形”。

1. **数据与系统**：在 PSCAD 或一个可控的固定步长 EMT 原型中复现 Fig. 1 二极管 LCR；使用 Appendix 的 \(E_{\mathrm{rms}}=90\,\mathrm{V},f_e=50\,\mathrm{Hz},r_s=1\,\Omega,L_s=1\,\mathrm{mH},C_f=500\,\mu\mathrm{F},R_x=100\,\Omega\)，并按论文工况扫描 dc 电阻负载。用 10 μs DSM 生成 \(v_{abc},i_{abc},v_{dc},i_{dc}\) 训练轨迹。[pdf:E08](_evidence/E08-p008-di-dnsm-flow-and-study-setup.png) [pdf:E11](_evidence/E11-p011-performance-limitations-conclusion.png)
2. **实现**：按式 (4)-(15) 计算 \(w_i,w_v,\phi,z_d,\theta_{\mathrm{rec}}\)，建 \((z_d,\theta_{\mathrm{rec}})\) LUT，再按 Fig. 6-7 实现 IDI-DNSM。暂不实现 DI 的 4x4 Jacobian，避免把一周时间耗在求解器内部接口上。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png) [pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png) [pdf:E06](_evidence/E06-p006-indirect-and-direct-interface.png)
3. **留出测试**：不要只重放建表点。将 \(R_l=5\,\Omega\) 到 \(0.5\,\Omega\)、\(L_l=2\,\mathrm{mH}\) 的 \(t=2\,\mathrm{s}\) 阶跃作为 held-out transient，并额外留出两个表格网格之间的电阻值，以检验线性插值。
4. **测量**：对 \(v_a,i_a,v_{dc},i_{dc}\) 计算对齐后的 NRMSE、峰值误差、稳态 THD/纹波谱误差；记录最大无发散且误差不过阈值的步长与 30 s 仿真 CPU 时间。阈值应在实验前固定，例如四个波形 NRMSE 均小于 2%，主要特征谐波幅值误差小于 5%，负载阶跃后的峰值和稳态值不出现持续偏差。
5. **支持标准**：若 70 μs IDI-DNSM 在 held-out transient 上达到阈值，而同一步长 DSM 在关闭事件插值时明显失真，并且 DNSM 的运行时间下降，则复现支持本文最核心的“以瞬时参数关系换取大步长”claim。若只在建表轨迹上吻合、留出工况显著退化，或 THD 对相位采样极敏感，则反驳其可复用性，而不是用更密 LUT 事后掩盖。

这项复现不会验证 DI-DNSM 的 200 μs 上限，也不会验证实时 RSCAD；它刻意只验证本文机制链中最便宜、最可证伪的一段。

## § 11 — 最强反例设计

最强反例不是简单把步长再增大，而是主动构造**同一 LUT 坐标、不同 DSM 真值**的状态碰撞。

可用晶闸管 LCR 做双轨迹实验。轨迹 A 使用论文建表时的源电感；轨迹 B 在此前经历一次故障清除或改变源电感，使换相重叠和内部电流历史不同。通过调节 dc 负载和 firing angle，让两条轨迹在某个采样时刻具有相同的 \(z_d,\alpha,\theta_{\mathrm{rec}}\)，并尽量匹配 \(v_{dc}\) 与 \(\lVert i_{qd}^{s}\rVert\)。随后比较 DSM 给出的下一段 \(i_{dc},v_{qd}^{s}\) 与 \(\phi\)。若两个真值显著不同，则同一个 LUT 键必须映射到两个输出，论文的单值参数化在机制上不可能同时正确。[pdf:E04](_evidence/E04-p004-instantaneous-parametric-functions.png)

为了排除“只是插值分辨率不足”这一替代解释，应把碰撞点放在已采样网格点上，并逐步加密 LUT；若误差不随网格加密消失，而是按轨迹历史分成两簇，就说明缺少状态变量。再与 DSM 的 10 μs 解和开关事件插值解对照，可避免把 ground truth 数值误差误判为模型失败。

这个反例直接攻击本文最核心的因果链：若 LUT 坐标不是充分状态，离线建表无法保证在线详细重建；DI 接口即使完全正确，也只会更稳定地求解一个错误端口关系。作者关于“reference model 必须包含待复制特性”和“步内精确开关时刻未知”的讨论，为这种攻击提供了论文内依据。[pdf:E11](_evidence/E11-p011-performance-limitations-conclusion.png)

## § 12 — Follow-up Research Idea

**候选想法：从静态 LUT 代理改写为“可证伪的状态充分性模型”**。本卡没有检索本文之后的相关工作，因此不声称该想法具有 novelty。

（a）**未满足需求**：实时 EMT 不只需要在已知工况上快，还需要在故障、参数漂移、控制饱和和拓扑邻域变化时知道模型何时不可信。本文的静态 LUT 没有显式检测坐标碰撞，也没有对 out-of-distribution 工况给出置信边界。[pdf:E05](_evidence/E05-p005-lookup-tables-runtime-pipeline.png) [pdf:E11](_evidence/E11-p011-performance-limitations-conclusion.png)

（b）**潜在研究价值**：电力电子/EMT 领域通常看重暂态保真度、数值稳定性、确定性实时延迟、与节点求解器的可集成性，以及 HIL 上的可重复验证。若一个模型能在正常域保持本文的大步长优势，又能在 LUT 坐标不充分时在线识别并 fail-closed 地切换到事件感知局部求解，它改变的是“代理模型必须始终给答案”的问题定义，而不只是给 DNSM 再加一个拟合模块。

（c）**可借鉴的相邻方法**：借用 nonlinear system identification 的 delay embedding 判断是否需要历史状态，借用 hybrid automaton 表示离散换相模式，并用 conformal prediction 或 set-membership estimation 给端口输出一个可校准的误差集合。在线模型可以保留 DI-DNSM 的 Norton 接口，但其内部键从固定 \((z_d,\alpha/M,\delta,\theta_{\mathrm{rec}})\) 扩展为经最小性检验选出的状态；检测到同键多值或置信集合过宽时，只对受影响变换器启用局部小步长/事件预测。

（d）**第一个证伪实验**：构造第 11 节的成对历史轨迹，划分建表域内、参数漂移、非平衡和故障恢复四类 held-out 测试。若新增状态仍不能消除同键多值，或不确定性指标无法在波形误差超阈值前报警，这个研究方向首先被否证；不能只报告平均 NRMSE。

（e）**与本文的实质区别**：本文假定参数函数已经是可用的单值映射，研究重点是瞬时重建与两种网络接口；候选方向把“这些坐标是否构成充分状态”本身变成可检验对象，并把拒绝预测/局部回退纳入 EMT 求解契约。它追求的不是更密的 LUT，而是在大步长实时性与失配安全之间建立可观测边界。

---

证据导航：E01=PDF 物理页 1（摘要与问题）；E02=页 2（相关工作与贡献）；E03=页 3（系统、qd 坐标与典型波形）；E04=页 4（式 (5)-(11) 与瞬时参数函数）；E05=页 5（Algorithm 1、LUT 与在线重建）；E06=页 6（间接/直接接口起点）；E07=页 7（线性化、四端口矩阵与 Norton 等效）；E08=页 8（DI 流程与实验设置）；E09=页 9（LCR 暂态）；E10=页 10（VSC、Table 1-2）；E11=页 11（性能、限制、结论与 Appendix）。
