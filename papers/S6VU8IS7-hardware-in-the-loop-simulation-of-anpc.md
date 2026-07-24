# Hardware-in-the-Loop Simulation of ANPC Based on Modified Predictor–Corrector Method

作者：Xin Gao、Yuanyuan Huang、Shaojie Li、Changxing Liu、Zhongqing Sang  
出处：*Symmetry*, Vol. 17, 2025, Article 2121  
年份：2025  
DOI：10.3390/sym17122121  
Zotero key：S6VU8IS7

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的问题是：三电平 ANPC（active neutral-point-clamped）包含大量高速开关和可变拓扑，完整开关建模会增加矩阵维度与 FPGA 资源；把电路分成子系统虽能降低单块计算量，却常因子系统交换上一拍数据而引入 simulation latency 和数值振荡。作者希望通过无一拍延迟的并行分区、modified predictor–corrector solver，以及简化的 FCS-MPC 控制，把 ANPC 开关级 HIL 的最小步进压到 60 ns 以下（PDF 物理页 1，Abstract）[pdf:E01]。

该问题重要，是因为 ANPC 常用于高功率、高电压应用，直接做功率级实验成本高、周期长；HIL 可以让真实控制器在实验室面对接近开关时间尺度的 plant。真正的工程目标不是“仿真总时间更短”，而是在每个确定 deadline 内完成全部状态更新和 I/O，使控制器看到的电压、电流不因计算链过长而错过开关事件（PDF 物理页 2–3，Introduction）[pdf:E02][pdf:E03]。

## § 2 — 前人工作与不足

论文提到 averaged ANPC model 能描述稳态与低频动态，但最小实时步长仍大；PM-ANPC decoupled-DC-link equivalent model 的最小实时步长为 6 μs。FPGA 路线已经把复杂 power converter 的 device-level model 推到 50 ns，hierarchical cascaded SST 则报告 500 ns；因此纳秒级 FPGA HIL 本身不是空白（PDF 物理页 2–3，Introduction）[pdf:E02][pdf:E03]。

与本文最接近的是既有 latency insertion method 和 parallel predictor–corrector。论文明确引用一项“no simulation latency in subsystem partitioning”的既有工作：按常见元件分区、在一个离散区间内并行运行，并在电力牵引系统上达到 50 ns。本文的较可信增量不是首次发明无延迟分区，而是把 predictor 滞后一拍的求解方式、ANPC 三子系统划分、中性点电压补偿和简化 FCS-MPC 组合到 Speedgoat Artix-7 实现中（PDF 物理页 3，Introduction 末段）[pdf:E03]。

## § 3 — 重建作者的思考路径

可以从工程依赖关系重建作者路径：

1. ANPC 完整状态矩阵与 18 个相臂开关状态使串行状态更新路径过长，必须利用 FPGA 并行性。
2. 在 DC bus capacitors 和三相 shunt inductors 处分区，可把大矩阵变成若干较小子系统；若直接串行传值，最长时间是各块之和。
3. 让所有子系统同时计算，最长时间只由最慢子系统决定；三相电感不是普通 one-port，需要假设 load-side neutral point 并补偿子系统之间的 neutral voltage。
4. 普通 predictor–corrector 中 corrector 等待 predictor，仍形成两段串行关键路径；把 predictor 推迟一拍，当前 corrector 就能直接使用已准备好的预测值。
5. 普通三电平 FCS-MPC 遍历 \(3^3=27\) 个三相组合；将三相拆成三个并行 half-bridge 单元，每相只比较 \(+U_{dc}/2,0,-U_{dc}/2\) 三个候选，可进一步缩短控制计算。
6. 最后用两台 Speedgoat 构成 controller/plant HIL，并与 Matlab Simpower Systems（SPS）及 serial partition 比较波形、误差、资源与 critical path（PDF 物理页 6–12，Sections 2.2–4.2）[pdf:E05][pdf:E06][pdf:E07][pdf:E08][pdf:E09][pdf:E10]。

## § 4 — 核心 Intuition

核心 intuition 是：把“当前步必须等待的结果”变成“上一拍已经准备好的预测量”，就能让 predictor、corrector 和各电路子系统并行工作；只要步长足够小，陈旧一拍的 predictor 仍可能近似当前状态。与此同时，把 27 个联合开关候选分成三相各 3 个局部候选，以较短依赖链换取更小的 FPGA step（PDF 物理页 6、10–11，Sections 2.3 与 3.2）[pdf:E05][pdf:E08][pdf:E09]。

## § 5 — 具体方法与完整 Pipeline

以 \(U_{dc}=800\text{ V}\)、\(R=8\,\Omega\)、\(L=2\text{ mH}\) 的实验为例：

1. **开关拓扑。** 每相由 Sx1–Sx6 六个全控器件构成，输出电平为 \(+U_{dc}/2,0,-U_{dc}/2\)，零电平有多条冗余通路。Table 1 给出 P、OV1、OV2、OW1、OW2、N 六种状态与门极组合（PDF 物理页 4–5，Fig. 1–2 与 Table 1）[pdf:E04]。
2. **离散 load model。** 对星形 RL 负载用小采样周期近似导数，得到
   \[
   i_x(k+1)=\frac{T_s}{L}U_x(k)+\left(1-\frac{T_sR}{L}\right)i_x(k),
   \]
   作为电路推进与 FCS-MPC 的预测基础（PDF 物理页 6，Eq. (1)–(3)）[pdf:E05]。
3. **简化 FCS-MPC。** 每相只预测三个输出电平下的下一拍电流，并以 \([i(k+1)-i_{\mathrm{ref}}]^2\) 为 cost，选择最小者映射到该相六个开关。三个 three-step half-bridge controller 并行，替代串行遍历 27 个三相组合（PDF 物理页 6–7，Section 2.3、Fig. 3 与 Eq. (4)）[pdf:E05][pdf:E06]。
4. **分区。** ANPC 在 DC bus capacitance 和三相 shunt inductance 处分为 subsystems I、II、III；subsystem II 再按 A/B/C 三相对称拆分。三相电感通过假设负载侧 neutral point 并补偿子系统间 neutral voltage 实现无延迟解耦（PDF 物理页 8–9，Figs. 5–7 与 Section 3.1）[pdf:E07]。
5. **modified predictor–corrector。** 普通 predictor 与 corrector 串行；本文将 predictor 滞后一拍，使当前 corrector 使用 \(\hat y_n\)，从而试图把两段计算并行化（PDF 物理页 10–11，Eq. (8)–(11) 与 Figs. 8–9）[pdf:E08][pdf:E09]。
6. **HIL 架构。** 两台 Speedgoat IO324 通过模拟/数字 I/O 闭环：一台在 Artix-7 FPGA 上运行 ANPC plant，另一台在 CPU 环境运行 FCS-MPC controller；host 通过 Ethernet 监控，MATLAB/Simulink 版本为 2022b（PDF 物理页 11–12，Section 4.1 与 Figs. 10–11）[pdf:E09][pdf:E10]。
7. **比较。** parallel partition 与 serial partition 都使用和 SPS 相同的参数，比较 output current、误差、三相不平衡，以及 HDL 资源与 minimum delay path（PDF 物理页 12–15，Section 4.2–4.3）[pdf:E10][pdf:E11][pdf:E12][pdf:E13]。

## § 6 — 核心数学推导（无形式化数学则跳过）

连续 RL 关系在源 PDF 中写为 \(U_x(t)=L\,di_x/dt+R_x(t)\)，结合文字说明与 Eq. (3)，此处量纲上应理解为 \(R i_x(t)\)；Eq. (3) 又出现 \(R_x/L_x\) 的符号不一致。工程上它意图表达标准 RL forward Euler，而不是新的负载理论（PDF 物理页 6，Eq. (1)–(3)）[pdf:E05]。

普通显式 Euler 是

\[
y_{n+1}=y_n+h f(t_n,y_n).
\]

论文随后讨论隐式 Euler 与 trapezoidal rule，并给出普通 predictor–corrector：

\[
\hat y_{n+1}=y_n+h f(t_n,y_n),
\]

\[
y_{n+1}=y_n+\frac{h}{2}\left[f(t_n,\hat y_{n+1})+f(t_n,y_n)\right].
\]

其中 corrector 必须等待 predictor，所以硬件时间相加（PDF 物理页 9–10，Eq. (5)–(9) 与 Fig. 8）[pdf:E08]。

本文改为：

\[
\hat y_n=y_{n-1}+h f(t_{n-1},y_{n-1}),
\]

\[
y_{n+1}=y_n+\frac{h}{2}\left[f(t_n,\hat y_n)+f(t_n,y_{n+1})\right].
\]

这样 \(\hat y_n\) 在当前步开始前已经存在（PDF 物理页 10–11，Eq. (10)–(11) 与 Fig. 9）[pdf:E08][pdf:E09]。但 Eq. (11) 右侧仍含未知 \(y_{n+1}\)，本质上是隐式方程；源 PDF 没有说明 FPGA 中如何解析消元、迭代几次，或 actual plant equations 如何对应这一步。论文只用 Lipschitz continuity 与 \(\mathrm{Re}(K)<0\) 口头声称稳定，没有给 test equation 的递推特征根、稳定域或误差阶推导（PDF 物理页 11，Section 3.2 末段）[pdf:E09]。因此 58 ns 的 timing 结果可以独立成立，但“solver 一般更稳定、更准确”的数学证据并未闭合。

## § 7 — 实验设计与结论

**问题一：简化 FCS-MPC 能否产生合理输出？ → 实验：** 比较 FCS-MPC 与 SPWM 的 ANPC current waveform。**答案：** Fig. 4 显示基本趋势一致，FCS-MPC 视觉上更平滑；但没有 THD、steady-state error、dynamic response 或同等 switching frequency 的定量指标，因此只得到定性支持（PDF 物理页 7，Fig. 4）[pdf:E06]。

**问题二：parallel partition 是否接近 SPS？ → 实验：** 使用 Table 2 的 \(U_{dc}=800\text{ V}\)、\(C_x=4700\,\mu\text{F}\)、\(f_s=50\text{ Hz}\)、\(R_l=8\,\Omega\)、\(L_l=2\text{ mH}\)，比较 output current \(i_\alpha\)。**答案：** 论文在 0.002 s 报告约 2.7% 误差，其他时刻波形接近；Figs. 13–14 显示 parallel-SPS 差值带小于 serial-SPS（PDF 物理页 13–14，Table 2 与 Figs. 12–14）[pdf:E11][pdf:E12]。但没有全时域 RMSE、最大误差、开关事件对齐误差或统计重复。

**问题三：三相不平衡下是否仍可运行？ → 实验：** 将一相 load inductance 加倍。**答案：** Fig. 15 显示 SPS、parallel 和 serial 的正弦电流趋势接近；论文没有报告相别误差或不平衡指标，所以只能说明该单一工况没有明显失稳（PDF 物理页 14–15，Fig. 15）[pdf:E12][pdf:E13]。

**问题四：并行是否缩短关键路径？ → 实验：** 比较 resource 与 minimum delay path。**答案：** Parallel/serial 均用 46 个 multipliers；parallel 使用 81 个 adders、63 个 registers，serial 为 85、60；minimum delay path 分别为 58.179 ns 与 83.474 ns，parallel 缩短约 30.3%（PDF 物理页 15，Table 3）[pdf:E13]。这是全文最扎实的定量结果。

**问题五：精度提升来自 solver 还是去掉分区延迟？ → 现有实验：** parallel 与 serial 同时改变了数据依赖和求解方式，且没有 forward Euler、普通 predictor–corrector、modified solver 的严格 ablation。**答案：** 现有证据无法把误差改善独立归因于 modified predictor–corrector；“更稳定、更准确”强于实验所能支持的范围（PDF 物理页 13–16，Section 4 与 Conclusions）[pdf:E11][pdf:E12][pdf:E13][pdf:E14]。

## § 8 — Take-aways

**5 句话：**

1. 论文把 ANPC 分成可并行计算的子系统，并处理三相电感的 neutral-voltage coupling（PDF 物理页 8–9，Section 3.1）[pdf:E07]。
2. predictor 滞后一拍，使当前 corrector 能使用预先得到的预测量，目标是消除串行等待（PDF 物理页 10–11，Eq. (10)–(11)）[pdf:E08][pdf:E09]。
3. 简化 FCS-MPC 将 27 个联合候选拆成三相各 3 个候选并行计算（PDF 物理页 6–7，Section 2.3）[pdf:E05][pdf:E06]。
4. Speedgoat 综合结果把 minimum delay path 从 83.474 ns 降到 58.179 ns，而主要资源数量变化很小（PDF 物理页 15，Table 3）[pdf:E13]。
5. 58 ns 工程结果可信，但一般稳定性、solver 精度阶与跨工况误差优势没有被充分证明。

**3 句话：** 这篇论文完成了 ANPC 无延迟并行分区及 Speedgoat 实现。它对关键路径的改善有明确综合数据，对 waveform accuracy 的证据却主要是少量曲线。真正欠缺的是隐式 corrector 的硬件实现说明、solver ablation 和开关事件附近的定量误差。

**1 句话：** 它首先是一项成功的 ANPC FPGA 关键路径优化，而不是已经严密证明的一般新数值求解器。

## § 9 — 最脆弱的假设

最脆弱的假设是：当 \(h\) 很小时，滞后一拍生成的 \(\hat y_n\) 在当前拓扑下仍足够准确，且 neutral-voltage compensation 不会放大这份陈旧信息的误差。功率开关翻转是 non-smooth event；若 predictor 按上一拍拓扑计算，而当前拍两相同时换流，状态导数可能立即改变，误差会集中在最需要精确定位的开关边界（PDF 物理页 10–11，modified predictor–corrector 的依赖关系）[pdf:E08][pdf:E09]。

论文的正面证据只有一个普通 RL 工况、一个单相电感加倍工况和约 50 ms 波形；没有扫描 timestep、switching phase、load stiffness、多开关同步事件或 DC capacitor imbalance，也没有报告事件后峰值误差（PDF 物理页 13–15，Figs. 12–15）[pdf:E11][pdf:E12][pdf:E13]。若这一假设失效，parallel timing 仍可能更快，但“没有精度损失、稳定性更高”的核心解释会失效。

## § 10 — 最小复现实验

一周内最值得复现的是“并行方法是否在同样 deadline 下真的更准”：

1. **数据。** 使用 Table 2 的基准参数，再增加高刚性低电感负载、两相同步换流和 DC capacitor imbalance 三组 stress cases（PDF 物理页 13，Table 2）[pdf:E11]。
2. **实现。** 建立高精度 event-driven reference、serial partition、parallel modified predictor–corrector；额外实现 forward Euler 与普通 predictor–corrector ablation。
3. **测量。** 报告全时域 normalized RMSE、最大误差、开关后 1 μs 内峰值误差、数值振荡次数，以及同一 Artix-7 target 的 post-route critical path、latency 与 initiation interval。
4. **支持 claim。** Parallel 在低于 60 ns 的同时，多工况误差不高于 serial，并在开关事件后不出现持续振荡。
5. **反驳 claim。** 陈旧 predictor 在同步换流或高刚性负载下产生系统性更大峰值误差；或 Eq. (11) 的实际隐式求解不能包含在 58.179 ns 路径内。

## § 11 — 最强反例设计

最强反例是“预测期间拓扑失效”：在一个仿真步边界附近同时触发两相换流，把负载电感逐步降低以增大 \(di/dt\)，并扫描换流相位与 timestep。比较使用高精度事件定位的参考、使用当前拓扑的 serial predictor–corrector，以及使用上一拍 predictor 的本文方法。

如果本文方法的误差峰值稳定集中在拓扑切换后，并随 \(h\,di/dt\) 增长，而 serial 方法没有同样趋势，就能说明当前论文中 parallel error band 更小只是特定工况与曲线尺度的结果，而不是 solver 的普遍属性。这个反例不否定 parallel hardware schedule 的价值，但会直接否定“并行且不损失精度”的强结论（PDF 物理页 14–16，parallel/serial error 与 Conclusions）[pdf:E12][pdf:E13][pdf:E14]。

## § 12 — Follow-up Research Idea

**候选想法：从固定极小步长的无延迟分区，转向带 worst-case time 与事件误差保证的 event-synchronous partitioned HIL。**

（a）未满足需求是：功率电子仿真的主要误差集中在换流事件附近；平滑区固定使用 58 ns 浪费资源，事件区又不保证足够准确。（b）本领域高影响价值来自可综合实现、跨工况实机/CHIL 验证、确定性最坏执行时间与可解释误差界。（c）可借鉴 hybrid systems 的 event localization、conservative co-simulation、waveform relaxation 和 FPGA local multirate scheduling。（d）第一个证伪实验是在相同 FPGA 资源预算下比较多相同步换流；若事件同步方法不能降低峰值误差，或 worst-case execution time 无法保持实时，就应放弃。（e）它与本文的实质区别是目标不再只是压低固定 critical path，而是根据事件和分区误差决定何时同步、何处细化，并同时证明 deadline 与误差上界。

在没有系统检索最新 event-aware FPGA power-electronics HIL 文献前，这只能称为候选研究方向，不声称具有 novelty。
