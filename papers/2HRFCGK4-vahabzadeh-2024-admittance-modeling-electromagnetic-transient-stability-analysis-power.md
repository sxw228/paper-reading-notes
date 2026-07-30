# Admittance-Based Modeling for Electromagnetic Transient and Stability Analysis of Power-Electronic-Based Energy Conversion Systems

作者：Taleb Vahabzadeh；Arash Safavizadeh；Seyyedmilad Ebrahimi；Juri Jatskevich

出处：IEEE Transactions on Energy Conversion，Vol. 39，No. 3，pp. 1879-1890

年份：2024

DOI：10.1109/TEC.2024.3373794

Zotero key：2HRFCGK4

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“如何把一个 VSC 模型再简化一点”，而是一个同时涉及速度、数值精度和稳定性分析的系统问题：高比例 power-electronic-based energy conversion system 中有许多 VSC，传统详细开关模型需要微秒量级时间步，经典 average-value model（AVM）虽然去掉开关事件，却仍保留大量网络节点，并因 dependent source 与控制器的非迭代接口引入一个时间步延迟；节点矩阵大、可用步长小和接口延迟叠加，使大规模 EMT 仿真昂贵且可能出现数值误差或不稳定。[pdf:E01]（PDF 物理页 1，Abstract/Section I） [pdf:E02]（PDF 物理页 2，Section I）

作者提出 admittance-based modeling for EMTP（ABM-EMTP）：把一个 VSC、LCL filter 和 current-control loop 整体表示成端口 admittance transfer function，离散后化为三相 Norton equivalent，并直接并入全网 nodal equation 同时求解。作者还希望同一组 admittance 在 EMTP 运行点上支持 frequency-domain small-signal stability analysis，从而让时域 EMT 与频域阻抗分析共享一个模型底座。[pdf:E03]（PDF 物理页 2，Section I/II）

这一问题重要，因为现代电网中的关键风险既包括快速暂态，也包括 converter-grid interaction 产生的 sub/super-synchronous oscillation。若模型只能快速却错过稳定性边界，或能准确但无法扩展到多变流器，就不足以服务规划、控制整定与实时仿真。论文以 PSCAD offline simulation 和 RTDS NovaCor real-time simulation 验证，因而其价值主要在 EMTP 数值建模与实时数字仿真，而不是 FPGA 电路实现。[pdf:E01]（PDF 物理页 1，Abstract/Section I） [pdf:E03]（PDF 物理页 2，Section I/II）

## § 2 — 前人工作与不足

详细开关模型能重建 switching waveform，但它是离散、事件驱动模型，需要很小的仿真步长。经典 AVM 通过平均开关细节而连续化，可使用更大步长；问题是其 dependent voltage/current source 与外部网络在非迭代 EMTP 中形成一个时间步接口延迟，控制系统的外部接口也有类似延迟，因而在数十到数百微秒步长上容易出现可见误差甚至数值不稳定。[pdf:E01]（PDF 物理页 1，Abstract/Section I） [pdf:E02]（PDF 物理页 2，Section I）

DI-AVM 已能把 AVM 的 conductance matrix 直接放入网络方程，消除接口延迟；但该矩阵随时间变化，每步都要额外计算，而且 VSC 的内部电气节点数并未减少。换言之，它主要修复延迟，没有同时解决大节点矩阵的成本。[pdf:E02]（PDF 物理页 2，Section I）

传统 impedance-based modeling（IBM）已广泛用于 converter-grid 的频域稳定性分析，也可通过 generalized Nyquist criterion（GNC）定位共振；但它依赖具体 operating point，而运行点通常仍要从时域 EMTP 提取。此前也有用 converter admittance 做时域 simulation 的工作，但其模型以 dependent current source 和 snubber 接入 MATLAB/Simulink，未显著缩小待求 state-space equation，也不适用于 PSCAD、RTDS 这类 nodal-analysis-based EMTP。论文的切入点因此是把“端口 admittance”“EMTP 节点压缩”和“运行点稳定性分析”合成一条路径。[pdf:E02]（PDF 物理页 2，Section I）

论文相关工作部分没有给出与通用 model-order reduction、passivity-preserving macromodel、nonlinear surrogate 或 FPGA EMT accelerator 的直接比较；这些方向对本文的 novelty 校准仍未充分检索，因此本卡不声称其在这些更宽领域中的全局新颖性。

## § 3 — 重建作者的思考路径

以下是基于论文背景与方法结构的合理重建，不是作者逐字陈述。第一步，研究者会看到经典 AVM 的主要数值痛点并非平均模型本身，而是它作为受控源与网络“先后计算”造成的一个时间步延迟；DI-AVM 证明 simultaneous nodal solution 能消除延迟，但其 time-varying conductance 和原节点规模仍然昂贵。[pdf:E02]（PDF 物理页 2，Section I）

第二步，已有 IBM 表明一个含 filter 和 controller 的 VSC 可以只从 PCC 端口看成 input-output transfer function，而且这种 black-box-like terminal model 足以进行小信号稳定性分析。于是自然的问题变成：能否把这个端口 transfer function 用 trapezoidal rule 离散，改写为 EMTP 熟悉的 conductance 加 history current 形式，而不是把内部支路逐个 stamp 进网络？[pdf:E02]（PDF 物理页 2，Section I） [pdf:E03]（PDF 物理页 2，Section I/II）

第三步，若离散 transfer function 能形成 Norton equivalent，则每个 VSC 子系统只需在 PCC 留下三个相节点，内部动态进入 history term；网络矩阵和子系统历史更新由同一时刻的 PCC voltage 共同闭合，不再需要 AVM 的接口延迟。最后，由于时域仿真已提供 operating point，研究者又可把各 VSC 的 complex-αβ admittance 聚合，与 grid impedance 相乘做 GNC，从而把原本分离的 EMT 与阻抗稳定性分析连接起来。[pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)） [pdf:E07]（PDF 物理页 5，Fig. 3、Eqs. (24)-(26)、Sections III/IV） [pdf:E08]（PDF 物理页 6，Eqs. (27)-(34)、Sections IV/V）

## § 4 — 核心 Intuition

核心 intuition 是：EMTP 的外部网络不需要知道 VSC、filter 和 controller 内部有多少节点，只需要知道 PCC 电压变化会产生怎样的端口电流。把这段端口动力学离散成“固定 conductance stamp + 由历史样本计算的 current source”，就能保留动态记忆、缩小 nodal matrix，并在同一时间步内与网络联立求解。[pdf:E03]（PDF 物理页 2，Section I/II） [pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)） 同一个 terminal admittance 还能在 operating point 上转成 complex-αβ small-signal model，用于频率耦合和稳定性判断。[pdf:E07]（PDF 物理页 5，Fig. 3、Eqs. (24)-(26)、Sections III/IV）

## § 5 — 具体方法与完整 Pipeline

以论文的 grid-following two-level VSC 为例，输入是 PCC 三相电压 \(v_{\mathrm{PCC},abc}\)、active/reactive power references \(P^{ref},Q^{ref}\) 和前若干步的 PCC voltage、output current、current-reference histories；输出是当前 VSC 三相注入电流，并通过 Norton equivalent 进入全网节点方程。

1. **建立连续端口模型。** 作者先把 abc 变量用 Clarke transform 变到 stationary αβ frame。VSC 采用 SPWM average model，交流侧含 \(L_1\)-\(C\)-\(L_2\) filter 和阻尼电阻，电流环采用二阶 PR controller；消去内部电压与电流后，得到从 \(v_{\mathrm{PCC},\alpha\beta}\) 和 \(i^{ref}_{2,\alpha\beta}\) 到 \(i_{2,\alpha\beta}\) 的两个 proper transfer functions \(A(s)\) 与 \(B(s)\)。本文案例中 transfer-function order 为 5。[pdf:E04]（PDF 物理页 3，Fig. 1、Eqs. (2)-(11)、Sections II/III）
2. **离散并显式保留历史。** 用 trapezoidal rule 把 \(A(s),B(s)\) 变成 \(A^{disc}(z),B^{disc}(z)\)，再 inverse z-transform。当前端口电流被写成当前 PCC 电压乘一个系数，加上前 \(p\) 步 PCC voltage、VSC output current 和 current reference 的加权和。[pdf:E05]（PDF 物理页 4，Eqs. (12)-(18)）
3. **处理 power-reference 非线性。** \(P^{ref},Q^{ref}\) 到 current reference 的关系含 \(1/\lVert v_{\mathrm{PCC},\alpha\beta}\rVert^2\)，不能直接放入线性 transfer matrix。作者没有每步迭代或每步重新线性化，而是对 current reference 使用带 smoothing 的 three-point linear predictor，再把预测值放入 history term。[pdf:E05]（PDF 物理页 4，Eqs. (12)-(18)） [pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)）
4. **形成三相 Norton equivalent。** 将 αβ conductance 与 history vector 变回 abc，得到 \(i_{2,abc}=G^{ABM}_{abc}v_{\mathrm{PCC},abc}+h^{ABM}_{abc}\)。\(G^{ABM}_{abc}\) 表示 coupled conductances，\(h^{ABM}_{abc}\) 表示 dependent current sources；一个完整 VSC 子系统在外部只留下 PCC 的三个电气节点。[pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)）
5. **并入全网同步求解。** 每步先由 histories 和预测 reference 计算 \(h^{ABM}\)，将 \(G^{ABM}\) 与 \(h^{ABM}\) stamp 进全网 \(G V(t)=h(t)\)，求得当前节点电压，再更新端口电流与 histories。Fig. 3 给出的顺序是 Laplace-domain derivation → admittance transfer matrix → trapezoidal discretization → z-domain ABM → inverse z-transform → time-domain ABM → nodal conductance/history → overall nodal equation。[pdf:E07]（PDF 物理页 5，Fig. 3、Eqs. (24)-(26)、Sections III/IV）
6. **复用为稳定性 add-on。** 在运行点将 VSC admittance 与 grid impedance 统一转到 complex αβ frame；同一母线的 \(N\) 个 VSC admittance 直接相加，然后计算 \(L(s)=Z_{\mathrm{grid}}(s)Y_{\mathrm{load}}(s)\) 的 eigenvalues，以 GNC 判断 gain/phase margin，并保留 \(2\omega_0-\omega\) frequency coupling。[pdf:E07]（PDF 物理页 5，Fig. 3、Eqs. (24)-(26)、Sections III/IV） [pdf:E08]（PDF 物理页 6，Eqs. (27)-(34)、Sections IV/V）
7. **实际实现。** 作者在 PSCAD 5 中用 C code 与 Fortran interface 实现 ABM，在 RSCAD 中用 CBuilder 部署到 RTDS NovaCor；详细开关模型和 AVM 使用软件标准 library components。案例是 22 个 VSC，即 16 个 electronically-interfaced DERs 和 6 个 electronic loads。[pdf:E08]（PDF 物理页 6，Eqs. (27)-(34)、Sections IV/V） [pdf:E09]（PDF 物理页 7，Figs. 4-6、Table I、Section V-A）

开关与事件处理方面，ABM-EMTP 本身使用 AVM，不显式表示 semiconductor switching event；论文未报告 fault-controlled switch、限流器切换或 protection event 的专门处理。时间推进使用统一固定步长的 trapezoidal discretization，未报告 multi-rate 或 adaptive-step。计算依赖是每个 ABM 的局部 history update 加全网 nodal solve；论文未报告线程级并行、GPU 并行或 distributed partition。数值表示、浮点精度和定点化未报告。FPGA 映射、HDL、pipeline、片上存储、DSP/BRAM 资源、时钟频率、WCET 和 FPGA 实测均未报告。

## § 6 — 核心数学推导（无形式化数学则跳过）

**第一层：把内部 VSC 动态消元成端口关系。** 论文从 LCL filter 的电感、电容方程、SPWM average voltage 和 PR controller 出发，得到

\[
i_{2,\alpha\beta}(s)=A(s)v_{\mathrm{PCC},\alpha\beta}(s)+B(s)i^{ref}_{2,\alpha\beta}(s),
\]

\[
A(s)=\frac{\sum_{k=0}^{p}n_{vk}s^k}{\sum_{k=0}^{p}d_ks^k},\qquad
B(s)=\frac{\sum_{k=0}^{p}n_{ik}s^k}{\sum_{k=0}^{p}d_ks^k}.
\]

\(A\) 表示 PCC voltage 到 output current 的端口 admittance 路径，\(B\) 表示 current reference 到 output current 的控制路径；两者共享由 plant、filter 和 controller 决定的 denominator。案例包含两个 inductors、一个 capacitor 和一个二阶 PR controller，因此 \(p=5\)。[pdf:E04]（PDF 物理页 3，Fig. 1、Eqs. (2)-(11)、Sections II/III）

**第二层：把 transfer function 变成 EMTP 可 stamp 的离散关系。** 用 Tustin substitution 后，

\[
A^{disc}(z)=\frac{\sum_{k=0}^{p}b_{vk}z^{-k}}{\sum_{k=0}^{p}a_kz^{-k}},\qquad
B^{disc}(z)=\frac{\sum_{k=0}^{p}b_{ik}z^{-k}}{\sum_{k=0}^{p}a_kz^{-k}}.
\]

inverse z-transform 将 \(z^{-k}\) 解释为 \(k\Delta t\) 的 delay，整理得

\[
i_{2,\alpha\beta}(t)=G^{ABM}_{\alpha\beta}v_{\mathrm{PCC},\alpha\beta}(t)
+h^{ABM}_{\alpha\beta}(t),
\]

\[
G^{ABM}_{\alpha\beta}=
\begin{bmatrix}
b_{v0}/a_0&0\\
0&b_{v0}/a_0
\end{bmatrix}.
\]

\(h^{ABM}_{\alpha\beta}\) 收集过去 \(p\) 步的 PCC voltages、output currents、current references，以及当前预测 reference。工程上这正是“当步可放入 \(G\) 的线性项”和“只依赖已知历史的 current injection”的分离。[pdf:E05]（PDF 物理页 4，Eqs. (12)-(18)）

为避免 nonlinear power-to-current relation 带来迭代或一个时间步延迟，作者使用

\[
\widetilde i^{ref}_{2,\alpha\beta}(t)=
\frac{5}{4}i^{ref}_{2,\alpha\beta}(t-\Delta t)
+\frac{1}{2}i^{ref}_{2,\alpha\beta}(t-2\Delta t)
-\frac{3}{4}i^{ref}_{2,\alpha\beta}(t-3\Delta t).
\]

这不是新的物理模型，而是对当前 current reference 的数值预测。随后用 Clarke pseudo-inverse 得到三相关系

\[
i_{2,abc}(t)=G^{ABM}_{abc}v_{\mathrm{PCC},abc}(t)+h^{ABM}_{abc}(t),
\]

并将其并入全网 nodal equation。[pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)）

**第三层：从同一端口模型构造频域稳定性问题。** 作者在 complex αβ frame 中得到含 \(s-j2\omega_0\) 项的 \(2\times2\) VSC small-signal admittance \(Y^c_{\mathrm{VSC},\alpha\beta}(s)\)，使正频率扰动与 frequency-coupled component 同时保留。平衡 grid impedance 也变换到相同 frame；多个同母线 VSC 则按

\[
Y^c_{\mathrm{load}}(s)=\sum_{i=1}^{N}Y^c_{\mathrm{VSC},i}(s)
\]

聚合，最后计算

\[
L(s)=Z^c_{\mathrm{grid},\alpha\beta}(s)Y^c_{\mathrm{load}}(s),\qquad
\det[\lambda I-L(s)]=0.
\]

当 eigenvalue phase 到 \(-180^\circ\) 时，negative gain margin 表示不稳定。这里的稳定性结论是 operating-point small-signal 结论，不是任意 large-signal transient 的全局证明。[pdf:E07]（PDF 物理页 5，Fig. 3、Eqs. (24)-(26)、Sections III/IV） [pdf:E08]（PDF 物理页 6，Eqs. (27)-(34)、Sections IV/V）

## § 7 — 实验设计与结论

**问题 1：节点压缩是否真实发生？ → 实验：** 在同一 22-VSC 系统中分别建立 detailed switching、classical AVM 和 proposed ABM-EMTP。**答案：** live nodes 分别为 191、147 和 15；ABM 的每个 VSC 子系统只向网络暴露三个 PCC nodes，因此显著缩小 overall nodal equation。[pdf:E09]（PDF 物理页 7，Figs. 4-6、Table I、Section V-A）

**问题 2：压缩后是否还能复现暂态与失稳？ → 实验：** 系统初始时每个 CPL 设为 \(19\,\mathrm{kW}/1\,\mathrm{kVAR}\)，每个 DER 设为 \(5\,\mathrm{kW}/3\,\mathrm{kVAR}\)；从 \(t=0.1\,\mathrm{s}\) 开始，每隔 \(0.3\,\mathrm{s}\) 将 CPL active-power reference 增加 \(7\,\mathrm{kW}\)、DER 增加 \(2\,\mathrm{kW}\)。detailed switching 用 \(1\,\mu s\)，reference AVM 用 \(1\,\mu s\)，比较用 AVM 与 ABM 使用 \(5\,\mu s\)。**答案：** 前两次变化后各模型都调节到新 operating point；\(t=0.7\,\mathrm{s}\) 后 PCC voltage 显著下降，模型均显示 converter-grid interaction 与 CPL negative incremental impedance 相关的失稳。[pdf:E09]（PDF 物理页 7，Figs. 4-6、Table I、Section V-A） [pdf:E10]（PDF 物理页 7，Fig. 6、Section V-A）

**问题 3：较大步长时 ABM 是否比 classical AVM 准确？ → 实验：** 将 AVM 与 ABM 步长增至 \(50\,\mu s\)，并以 \(t=0\) 到 \(0.7\,\mathrm{s}\) 的 DER1 active-power trajectory 计算 cumulative 2-norm error，再扫描更大步长。**答案：** classical AVM 在约 \(50\,\mu s\) 以上误差迅速超过 \(1\%\)；ABM 在 \(400\,\mu s\) 仍约为 \(1\%\)。Table II 给出的可用步长量级为 detailed switching 小于 \(5\,\mu s\)、classical AVM 约 \(10\)-\(50\,\mu s\)、ABM 约 \(400\)-\(500\,\mu s\)。这是该案例、该指标下的结果，不应外推为所有 converter topology 的统一界限。[pdf:E11]（PDF 物理页 8，Figs. 7-9、Table II、Sections V-A/V-B）

**问题 4：速度提升来自哪里、幅度多大？ → 实验：** PSCAD 5 在 Intel Core i5-11500 @ 2.70 GHz 上运行同一 \(0.76\,\mathrm{s}\) study，RTDS NovaCor 使用两个 licensed cores。**答案：** 在 PSCAD 的 \(5\,\mu s\) 步长下，detailed switching、AVM、ABM CPU time 分别为 \(1358.7\,\mathrm{s}\)、\(9.338\,\mathrm{s}\)、\(2.199\,\mathrm{s}\)；在 \(50\,\mu s\) 下 AVM 与 ABM 分别为 \(1.091\,\mathrm{s}\) 与 \(0.222\,\mathrm{s}\)。RTDS 中 classical AVM 与 ABM 的最小可运行 time-step 分别为 \(18.6\,\mu s\) 与 \(3.24\,\mu s\)，最大值分别为 \(37\,\mu s\) 与 \(654\,\mu s\)；作者据此报告 ABM 计算量降低 5.7 倍。论文摘要式贡献还概括为相对 detailed switching 最多约 620 倍、相对 AVM 最多约 6 倍，但这些都是单一 case-study platform 的结果。[pdf:E03]（PDF 物理页 2，Section I/II） [pdf:E12]（PDF 物理页 9，Tables III-IV、Sections V-B/V-C）

**问题 5：同一 admittance 能否正确判断稳定性和 frequency coupling？ → 实验：** 用 EMTP operating points 构造 \(2\times2\) complex-αβ impedance-ratio matrix。Case I 的 CPL/DER set-points 为 \(33/9\,\mathrm{kW}\)，Case II 为 \(40/11\,\mathrm{kW}\)。**答案：** Case I 在 \(185.97\,\mathrm{Hz}\) 与 \(-65.97\,\mathrm{Hz}\) 的 candidate frequencies 具有 positive gain margin，预测稳定；Case II 在 \(201.25\,\mathrm{Hz}\) 与 \(-81.25\,\mathrm{Hz}\) 具有 negative gain margin，预测不稳定。时域 PCC voltage spectrum 显示 \(201.17\,\mathrm{Hz}\) 与 \(81.17\,\mathrm{Hz}\) 峰值，与频域预测接近。[pdf:E12]（PDF 物理页 9，Tables III-IV、Sections V-B/V-C） [pdf:E13]（PDF 物理页 10，Figs. 10-11、Section VI）

**复现边界：** Appendix F 报告了 \(400\,\mathrm{V}\)、\(60\,\mathrm{Hz}\) grid，VSC dc bus \(1\,\mathrm{kV}\)、switching frequency \(10\,\mathrm{kHz}\)，以及 LCL、controller 与 line parameters，可支持重建 electrical case。[pdf:E14]（PDF 物理页 11，Appendix F） 但论文未报告源代码、完整 PSCAD/RSCAD project、编译选项、solver tolerance、CPU 单线程/多线程设置、RTDS task mapping、随机重复次数或 statistical uncertainty。它也未报告 FPGA 资源、定点误差或 FPGA-in-the-loop 实验，因此不能从这些实验推出 FPGA 可实现性。

## § 8 — Take-aways

**5 句话：**

1. 论文把含 filter 和 controller 的 VSC 子系统压缩为端口 admittance，并离散成 EMTP 可直接 stamp 的 Norton equivalent。[pdf:E03]（PDF 物理页 2，Section I/II） [pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)）
2. 历史动态保留在 \(h^{ABM}\) 中，当前 PCC voltage 通过 \(G^{ABM}\) 与全网同时求解，从而避免 classical AVM 的一个时间步接口延迟。[pdf:E05]（PDF 物理页 4，Eqs. (12)-(18)） [pdf:E07]（PDF 物理页 5，Fig. 3、Eqs. (24)-(26)、Sections III/IV）
3. 22-VSC 案例中 live-node count 从 detailed switching 的 191 和 AVM 的 147 降到 15。[pdf:E09]（PDF 物理页 7，Figs. 4-6、Table I、Section V-A）
4. 在该案例中，ABM 支持数百微秒步长仍保持约 \(1\%\) 量级误差，并在 PSCAD/RTDS 上显著减少计算时间。[pdf:E11]（PDF 物理页 8，Figs. 7-9、Table II、Sections V-A/V-B） [pdf:E12]（PDF 物理页 9，Tables III-IV、Sections V-B/V-C）
5. 同一端口 admittance 还能预测 stable/unstable operating point 及 frequency-coupled oscillations，但该频域功能尚未自动化，适用性仍受 small-signal 和建模假设约束。[pdf:E13]（PDF 物理页 10，Figs. 10-11、Section VI）

**3 句话：**

1. ABM-EMTP 的关键不是简单降阶，而是把内部动态移入 history source，同时保持 network solve 的当步耦合。
2. 论文在一个参数完整的 22-VSC PSCAD/RTDS 案例上同时验证了节点压缩、暂态准确性、计算性能和频域稳定性一致性。[pdf:E09]（PDF 物理页 7，Figs. 4-6、Table I、Section V-A） [pdf:E12]（PDF 物理页 9，Tables III-IV、Sections V-B/V-C） [pdf:E13]（PDF 物理页 10，Figs. 10-11、Section VI）
3. 证据尚不能覆盖 saturation、fault switching、dc-link dynamics、异构 converter、自动模型生成或 FPGA implementation。

**1 句话：**

ABM-EMTP 证明了“端口 admittance + Norton stamp + history term”可成为大规模 VSC EMT 与 operating-point stability analysis 的共享数值接口，但尚不是对强非线性、事件驱动和硬件实时场景的通用解。

## § 9 — 最脆弱的假设

失败代价最大的假设是：在研究的 operating range 内，每个 VSC 子系统都能由固定阶数、proper、近似线性的 terminal transfer functions 加一个可预测的 power-to-current reference 充分表示。本文模型固定 dc-link voltage，假设 dc-link capacitor 足够大而忽略其 dynamics；DER 与 electronic load 使用相似的 grid-following VSC/LCL/PR configuration，current reference 的非线性则由 three-point predictor 绕过。[pdf:E04]（PDF 物理页 3，Fig. 1、Eqs. (2)-(11)、Sections II/III） [pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)） [pdf:E08]（PDF 物理页 6，Eqs. (27)-(34)、Sections IV/V）

这个假设在 current limiting、PWM saturation、dc-link energy depletion、fault-induced mode switching、protection action、PLL loss of synchronism、controller gain scheduling 或 converter topology 异构时可能失效。此时端口关系不再由同一组 \(A(s),B(s)\) 和 history coefficients 描述，最严重的后果不是误差稍大，而是 ABM 可能把参考模型中的失稳判成稳定，或因不再被动的拟合 admittance 引入数值不稳定。

论文提供的证据是功率阶跃跨越稳定与不稳定 operating points 时，ABM 与 reference AVM 的 trajectory 和 oscillation frequency 接近，并在 \(400\,\mu s\) 左右仍保持约 \(1\%\) 的 DER1 power 2-norm error。[pdf:E10]（PDF 物理页 7，Fig. 6、Section V-A） [pdf:E11]（PDF 物理页 8，Figs. 7-9、Table II、Sections V-A/V-B） [pdf:E13]（PDF 物理页 10，Figs. 10-11、Section VI） 缺少的关键证据是：受限控制、dc-link dynamics、fault switching 和强参数变化下的端口模型有效域，以及对 passivity、causality 或 error bound 的证明。因此这项假设在论文案例内得到支持，但没有被证明可跨越真实 converter 的 mode boundaries。

## § 10 — 最小复现实验

一周内最值得复现的是“去掉接口延迟后，ABM 在较大时间步下比 classical AVM 更准确”这一核心数值 claim，而不是完整重建全部 22 个 VSC。

1. 用 Appendix F 的 grid、LCL 和 PR-controller parameters 建立一个 grid-following VSC 与一个可调 CPL；分别实现 reference AVM、带 dependent-source one-step delay 的 classical AVM，以及按 Eqs. (12)-(23) 实现的 ABM。[pdf:E05]（PDF 物理页 4，Eqs. (12)-(18)） [pdf:E06]（PDF 物理页 4，Fig. 2、Eqs. (19)-(23)） [pdf:E14]（PDF 物理页 11，Appendix F）
2. 用 \(1\,\mu s\) reference AVM 生成事实基线；按论文的 active-power step 结构运行 \(5,50,200,400\,\mu s\) 四组固定步长。记录 PCC voltage、converter active power、每步 execution time 和是否出现 numerical instability。[pdf:E09]（PDF 物理页 7，Figs. 4-6、Table I、Section V-A）
3. 在 \(t=0\) 到首个 physical instability 前，计算 active-power trajectory 的 normalized cumulative 2-norm error；同时比较 \(t=0.4\,\mathrm{s}\) 附近 transient overshoot 和 settling waveform。[pdf:E11]（PDF 物理页 8，Figs. 7-9、Table II、Sections V-A/V-B）
4. 支持 claim 的结果是：在相同步长下 ABM 误差持续低于 classical AVM，且 classical AVM 随步长增大出现与 one-step delay 一致的相位/幅值误差，而 ABM 到 \(200\)-\(400\,\mu s\) 仍保持有界并接近 reference。反驳结果是：控制器与 plant 相同、实现经交叉核对后，ABM 在 \(50\,\mu s\) 已不优于 AVM，或大步长优势来自不同 solver tolerance、不同 controller timing 而非 Norton simultaneous solution。

这个最小实验不能复现论文的 15-node 系统规模或 RTDS speedup，但能直接证伪其核心数值机制；若通过，再扩展到 4-8 个并联 VSC 检查 node-count 与 runtime scaling。

## § 11 — 最强反例设计

最强反例不是换一个普通负载，而是强迫 converter 穿过“固定端口 transfer function 不再成立”的 mode boundary。具体做法是给 reference switching/AVM 加入有限 dc-link capacitor、current limiter、modulation saturation 和 fault ride-through logic，在 weak-grid 条件下施加三相电压跌落；ABM 仍使用论文的固定 \(A(s),B(s)\) 与 three-point reference predictor。扫 fault depth、clearing time 和 pre-fault power，寻找 reference model 触发限流或 dc-link collapse、而 ABM 仍停留在线性工作模式的区域。

每个工况同时测量三项：一是 PCC current/voltage trajectory 与 normalized error；二是 fault clearing 后是否恢复或失稳；三是从 pre-fault operating point 构造的 \(L(s)\) 是否给出与时域结果一致的 stability classification。若存在一片连续参数区域，使 ABM 将 reference 的 loss of synchronism 或 post-fault oscillatory instability 判断为稳定，且误差不能通过减小 \(\Delta t\) 消除，那么问题来自模型类而非数值步长，会直接推翻“该端口 ABM 可作为统一暂态与稳定性接口”的宽泛解释。论文当前实验未覆盖这些 switching/control mode events，因而不能排除该反例。

## § 12 — Follow-up Research Idea

在 EMT 与 power electronics 领域，高影响工作通常需要同时满足：模型有明确物理边界，数值稳定或误差性质可解释；在多个 converter topology、operating region 和 disturbance class 上与 detailed/reference model 对照；在 PSCAD/RTDS 或 HIL hardware 上给出可复现的 execution-time、real-time deadline 和资源证据。仅在单一案例上再提高一个 speedup 数字通常不足。

**候选想法：具有 passivity certificate 的 mode-aware Norton operator。** 需求来自第 9 节：论文的 fixed transfer function 在 saturation、current limiting 和 dc-link dynamics 出现时可能跨出有效域，但完全恢复详细内部节点又会失去矩阵压缩。新问题不再是“如何拟合一个更高阶 admittance”，而是：能否始终保留一个便于 EMTP 预 stamp 的固定端口 conductance \(G\)，把 nonlinear、mode-dependent 和 history-dependent dynamics 放入受约束的 history current operator \(h_\theta\)，并保证每个模式及模式切换满足 causality、incremental passivity 或可计算的 energy bound？

潜在研究价值在于，它同时保留网络求解结构、允许强非线性模式变化，并把“模型不会向网络凭空注入数值能量”变成可检验条件。可借鉴相邻领域的 hybrid systems、linear-parameter-varying identification、dissipativity/passivity theory 和 constrained recurrent state-space models；但本卡未做完整相关工作检索，因此这只是候选方向，不声称 novelty。

第一个证伪实验应直接使用第 11 节的 weak-grid fault sweep：训练或辨识只用正常运行与部分限流数据，然后在未见过的 fault depth、clearing time 和 dc-link parameter 上比较 fixed-ABM、mode-aware operator 与 detailed model。若 mode-aware model 不能在保持同一 nodal stamp 和 real-time deadline 的同时，显著减少 stability misclassification，并且 passivity constraint 不能阻止数值能量增长，那么该研究路线应被否决。它与本文的实质区别不是增加一个 controller module，而是把端口模型从单一 LTI transfer function 改成带可验证能量边界的 hybrid history operator，同时保留 EMTP 所需的 Norton interface。
