# A Semi-Implicit Parallel Leapfrog Solver With Half-Step Sampling Technique for FPGA-Based Real-Time HIL Simulation of Power Converters

- 作者：Jialin Zheng，Yangbin Zeng，Zhengming Zhao，Weicheng Liu，Han Xu，Shiqi Ji
- 出处：IEEE Transactions on Industrial Electronics，Vol. 71，No. 3，pp. 2454-2464
- 年份：2024
- DOI：10.1109/TIE.2023.3265042
- Zotero key：9ELPM74G
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的不是一般意义上的“让 FPGA 算得更快”，而是一个更具体的 RT-HIL 瓶颈：物理控制器的 gate signal 只能在离散仿真时刻被采样，若一个开关周期内采样点太少，即使电路方程本身算得很准，采到的开关相位仍可能错误。论文引用的工程经验是，RT-HIL 的仿真步长通常需要达到控制器开关周期的 \(1/50\) 到 \(1/100\)；宽禁带器件把开关频率推高后，这会把所需步长压到 sub-microsecond 甚至 nanosecond 量级，而 FPGA 上一个串行求解步骤又常需多个时钟周期。[pdf:E01]（PDF 物理页 1，Abstract 与 Section I）

作者据此提出 semi-implicit parallel leapfrog（SPL）solver：先减少一次完整状态推进的依赖链，再利用两组错开半步的状态让 gate signal 在每个 \(T/2\) 都能被消费。论文的核心工程 claim 是：在不把完整计算步 \(T\) 再缩短、也不增加额外硬件成本的情况下，把采样率提高一倍；DAB case 在 25 ns 计算步下获得 12.5 ns 采样步，并展示了 400 kHz 开关下的仿真结果。[pdf:E01]（PDF 物理页 1，Abstract）[pdf:E09]（PDF 物理页 9，Fig. 8、Fig. 11 与 Table III）

价值在于它把“数值积分精度”和“开关边沿采样精度”拆成两个可分别优化的量。在 high-switching-frequency converter 的 RT-HIL 中，控制器看到的是模型输出，而模型能否在正确时刻看到 PWM 边沿会直接影响闭环测试可信度；因此，采样率提升可以比继续堆叠矩阵运算资源更有效。不过，这个价值成立的前提是开关等效本身仍忠实，论文后文明确把基本 switching-function model 限定在 continuous current mode（CCM）。[pdf:E03]（PDF 物理页 3，Section II-B 末段）

## § 2 — 前人工作与不足

论文把既有方案分成 model simplification 与 parallel solving 两类。开关模型方面，associative discrete circuit（ADC）model 可以通过调参保持 admittance matrix 不变，但作者指出它在高开关频率下容易出现不准确的振荡和损耗；dual resistance value（DRV）model 更准确，却因 conductance 随开关状态变化而增加计算成本。inverse-matrix update 和 network tearing 能减轻求逆或分解网络的代价，但预存矩阵会受到 FPGA memory 资源约束。[pdf:E01]（PDF 物理页 1，Section I 右栏）[pdf:E02]（PDF 物理页 2，Section I 左栏）

并行求解方面，coarse-grained 方法常通过 transmission line、缓变电容或电感插入一个步长的 latency 来切分子电路；这会引入潜在不稳定性，而且精度依赖 partition interface 的物理性质。fine-grained 方法更贴合 FPGA，但论文列出的既有代价也很具体：把开关封装成显式实体会丢失实体内部 switching-variable 信息；为 branch-level parallelism 插入电感、电容可能改变系统动态；predictor-corrector 虽能并行开关部分与其余系统，却消耗更多计算资源，电路规模变大时尤为明显。[pdf:E02]（PDF 物理页 2，Section I 左栏）

作者认为这些方法仍把一个仿真步作为顺序、整体的求解单元，所以通常只能在每个完整步采样一次；当 one-step computation 已经难以继续缩短时，采样率也随之封顶。SPL 的区别不是单独发明一种更快的矩阵乘法，而是把 state update 组织为两个相互错开的 half-step subsolver，使“完整计算步”与“可接收新 gate signal 的间隔”不再相同。[pdf:E02]（PDF 物理页 2，Section I 左栏末段与贡献列表）

需要保留一个证据边界：上述 prior-work 比较是本论文作者的归纳，本卡没有用被引论文全文逐项复核。因此，这里可以确认“作者如何定位差距”，不能独立确认所有 baseline 在其最佳实现下都必然具有这些缺点。

## § 3 — 重建作者的思考路径

下面是基于论文背景与失败模式的合理重建，不是作者明说的研发日志。

第一步，一个研究者会发现问题不只在 ODE solver：FPGA 可以提供很低的硬件 latency，但若 matrix update、switch-state update 和 state solve 串成一条链，一次仿真步仍需多个 cycle，控制器的 gate edge 只能等到下一个 step 才生效。[pdf:E01]（PDF 物理页 1，Section I）

第二步，既有 ADC/DRV 与网络分割方案提示了一个方向：若把 switch nonlinearity 隔离到小而规则的单元，让 system-level matrix 固定，就能把昂贵的 topology update 前移到预处理；但不能靠人为插入电抗元件或接口延迟来换并行，因为那会改变原系统。[pdf:E02]（PDF 物理页 2，Section I 与 Fig. 1）

第三步，电路 state 本来就包含 capacitor voltage 与 inductor current。若两类状态在时间上错开半步，并让其中一类在当前半步 implicit、另一类 explicit，那么每个递推式右端可以只依赖已知量；这样就有机会把一个联合方程组拆成独立 dot-product entity，而不需要每步联立求解。[pdf:E04]（PDF 物理页 4，Eq. (6)-(11) 与 Fig. 3）

第四步，一旦两组 state 分别驻留在整数时刻与半整数时刻，switch equivalent source 也可以按相同节拍交错更新。于是每个 \(T/2\) 都出现一个合法的 sampling boundary，而不是单纯把原 solver 强行 clock-doubling；这正好绕开“完整计算步已经缩不动”的限制。[pdf:E05]（PDF 物理页 5，Eq. (12)-(15) 及其后正文）

这条思考路径的关键不是“半步一定更准”，而是先让 half-step 时刻的状态在依赖关系上合法，再把新增采样点真正接入 switching-level update。若只有更密的采样时钟而没有相应的状态与等效源，得到的只是重复读取旧状态。

## § 4 — 核心 Intuition

SPL 的 intuition 是：把一次联合状态推进拆成两组相差半步的递推，一组更新 capacitor voltage，另一组更新 inductor current；每组在需要自己新值时 implicit，在使用另一组时只读已知旧值。这样既能让四类 solver entity 并行，又能在每个 \(T/2\) 用新的 gate signal 更新开关等效源，因此 25 ns 的完整计算步可以提供 12.5 ns 的采样间隔。[pdf:E04]（PDF 物理页 4，Fig. 3）[pdf:E05]（PDF 物理页 5，Eq. (12)-(15) 与并行说明）

## § 5 — 具体方法与完整 Pipeline

以论文中的 dual active bridge（DAB）为例，输入是 converter topology、元件参数、DC sources、当前 state，以及物理 DSP controller 输出的 PWM gate signal；输出是 RT-HIL 中的电压、电流等模拟量，经 FPGA 接口返回给 controller。完整 pipeline 如下。

1. **HPE 建模。** 先把 converter 拆成 switch components 与 linear components，再把每个 half-bridge 作为最小 commutation unit。switch-level part 用受控 voltage source \(E\)、受控 current source \(J\) 与 on-state resistor \(R\) 表示开关行为；system-level part 只接收这些 equivalent sources，因此系统矩阵保持固定并可预处理。[pdf:E03]（PDF 物理页 3，Fig. 2、Table I 与 Eq. (2)-(5)）
2. **开关状态更新。** 在 CCM 下，half-bridge 只采用 \([S_1,S_2]=[1,0]\) 或 \([0,1]\)，Table I 给出相应的 \(k_E,k_J\)。等效源使用上一可用时刻的端口量更新，避免 switch-level 与 system-level 迭代；deadtime、blocking 与 DCM 的 \(00\) 状态不能由这个基本模型直接处理，论文只提出改接 conventional diode switching model，未展示该组合的实时实现或性能。[pdf:E03]（PDF 物理页 3，Table I、Eq. (2)-(5) 与 Section II-B 末段）
3. **AII 状态分解。** state vector 被分成 capacitor voltage \(x_C\) 与 inductor current \(x_L\)。在 \(t_n\rightarrow t_{n+1/2}\) 的前半步，两组分别交替采用 explicit/implicit；在后半步角色互换。合并后得到 \(x_C\) 位于整数时刻、\(x_L\) 位于半整数时刻的 leapfrog recurrence，右端都是已知量。[pdf:E04]（PDF 物理页 4，Eq. (6)-(11)）
4. **HST 调度。** switch-level 被分成 voltage source solver（VSS）与 current source solver（CSS），system-level 被分成 capacitor voltage solver（CVS）与 inductor current solver（ICS）。VSS/CVS 与 CSS/ICS 形成两组交错 entity：同一 half-step 内能并行的 entity 同时计算，相邻 half-step 通过 state machine 交替 enable；gate signal 在每个 half-step 都可进入 source update。[pdf:E04]（PDF 物理页 4，Fig. 3）[pdf:E05]（PDF 物理页 5，Eq. (12)-(15) 之后的 flow 说明）
5. **FPGA 数据路径。** 每个 entity 把固定 matrix-vector multiplication 展开为多个 dot-product unit；一个 \(m\times n\) matrix-vector product 被展开为 \(m\) 个行 dot product，论文描述的 fully parallel realization 使用 \(m\times n\) 个 multiplier、一个 clock cycle。top-level 通过 FIFO 跨 solver 与 ADC/DAC clock domain，并由 MMCM/PLL 与 DDR-LVDS 完成接口时序。[pdf:E05]（PDF 物理页 5，Section IV-A）[pdf:E06]（PDF 物理页 6，Fig. 4）
6. **数值表示与生成流程。** case study 的全部运算使用 64-bit fixed-point，其中 integer bit-width 为 24 bit；C++ kernel 经 Xilinx Vitis HLS 转为 HDL，再用 Vivado 实现到 register-transfer logic。论文未报告逐变量缩放、overflow/saturation policy、rounding mode、word-length sensitivity、完整 HLS directive 或可复用 HDL source。[pdf:E06]（PDF 物理页 6，Section IV-C）
7. **实际平台。** DAB 被映射到 Xilinx VC707（XC7VX485T-2FFG1761C），ADC 为 14-bit ADS4449、最高 250 MSPS，DAC 为 16-bit DAC34H84、最高 1.25 GSPS；论文展示了 FPGA RT-HIL、物理 DSP controller 与 power-level DAB 的连接。[pdf:E07]（PDF 物理页 7，Fig. 5、Section V-A-2 与 Table II）

论文报告的 DAB 拓扑参数包括 \(U_{DC1}=600\ \mathrm{V}\)、\(U_{DC2}=400\text{-}600\ \mathrm{V}\)、\(P_{\max}=30\ \mathrm{kW}\)、\(L_k=42\ \mu\mathrm{H}\)、\(L_m=2.49\ \mathrm{mH}\)、\(C_H=1000\ \mu\mathrm{F}\)、\(C_L=250\ \mu\mathrm{F}\)、\(R_I=R_O=0.001\ \Omega\)，附录 nominal switching frequency 为 20 kHz。[pdf:E10]（PDF 物理页 10，Appendix Table IV）对 200 kHz 与 400 kHz 的 simulation benchmark，论文未报告一套可直接重放的完整 gate sequence、phase-shift command、随机种子或 testbench 文件。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有明确的形式化推导。基础是线性 state-space model：

\[
\dot{x}(t)=Ax(t)+Bu(t),\qquad y(t)=Cx(t)+Du(t).
\]

这里 \(x\) 是独立 state，\(u\) 是 source/input，\(y\) 是 output；问题在于 switch action 改变 topology，直接方法往往要逐步更新 topology matrix。[pdf:E02]（PDF 物理页 2，Eq. (1) 及其后正文）

HPE 先把每个 switch leg 的非线性压到 equivalent-source coefficient 中：

\[
v_E(t_n)=k_Ev_J(t_{n-1}),\qquad i_J(t_n)=k_Ji_E(t_{n-1}),
\]

\[
h(t_n)=
\begin{bmatrix}v_E(t_n)\\ i_J(t_n)\end{bmatrix}
=K_{n-1}y_s(t_{n-1}),
\]

从而把 system equation 改写成

\[
\dot{x}(t)=Ax(t)+Bu(t)+Eh(t),\qquad
y_s(t)=Cx(t)+Du(t)+Fh(t),
\]

其中 \(A,B,C,D,E,F\) 都是固定矩阵。直观上，topology change 不再触发整个 system matrix 重构，而只改变小型 diagonal coefficient \(K\) 和 source vector \(h\)。[pdf:E03]（PDF 物理页 3，Eq. (2)-(5)、Table I）

AII 再将 \(x=[x_C^\top,x_L^\top]^\top\) 与矩阵 \(A\) 按 capacitor/inductor state 分块。前后两个 \(T/2\) 内交替交换 explicit 与 implicit 角色，消元后得到：

\[
x_C^{(n+1)}
=P_-P_+x_C^{(n)}
+TP_-f_C\!\left(x_L^{(n+1/2)},u^{(n+1/2)},h_i^{(n+1/2)}\right),
\]

\[
x_L^{(n+1/2)}
=Q_-Q_+x_L^{(n-1/2)}
+TQ_-f_L\!\left(x_C^{(n)},u^{(n)},h_v^{(n)}\right),
\]

其中

\[
P_-=(I-A_{11}T/2)^{-1},\quad P_+=I+A_{11}T/2,
\]

\[
Q_-=(I-A_{22}T/2)^{-1},\quad Q_+=I+A_{22}T/2.
\]

\(f_C=A_{12}x_L+B_1u+E_1h_i\)，\(f_L=A_{21}x_C+B_2u+E_2h_v\)。这些 inverse 与 matrix coefficient 因矩阵固定而可预处理；运行时每个 recurrence 的右端只含当前已知的另一组 state，因此不需要联合求解 \(x_C\) 与 \(x_L\)。[pdf:E04]（PDF 物理页 4，Eq. (6)-(11)）

最后，output 与 equivalent source 也按相同时间格点错开：

\[
y_s^{(n+1/2)}
=C_1x_C^{(n)}+C_2x_L^{(n+1/2)}
+Du^{(n+1/2)}+F_1h_v^{(n)},
\]

\[
y_s^{(n)}
=C_1x_C^{(n)}+C_2x_L^{(n-1/2)}
+Du^{(n)}+F_2h_i^{(n-1/2)},
\]

\[
h_i^{(n+1/2)}=K_i y_s^{(n)},\qquad
h_v^{(n+1)}=K_v y_s^{(n+1/2)}.
\]

这四式把“可以采样”的时刻与两组 state 的合法输出对齐，所以 half-step sample 不是插值出来的虚拟点。[pdf:E05]（PDF 物理页 5，Eq. (12)-(15)）

论文声称该 leapfrog structure 具有 linear time complexity，并在 FPGA structure 描述中称其具有 second-order numerical stability；但正文未给出 characteristic polynomial、stability region、global truncation error theorem 或跨步长收敛阶实验。因此可以确认递推结构与硬件并行性，不能仅凭本文证据把“二阶稳定性”升级为已证明定理。[pdf:E04]（PDF 物理页 4，Eq. (9)-(11) 后正文）[pdf:E05]（PDF 物理页 5，Section IV-B）

## § 7 — 实验设计与结论

**问题 1：HPE/AII 是否在较短实时步长下保持与 conventional solver 接近的数值结果？ → 实验：** 作者用 variable-step ode45 Simulink model 作为 ideal reference，以 modified one-step EMTP trapezoidal solver 为对照，并在 open-loop 下施加 DC bus voltage 于 0.05 s 从 600 V 降到 500 V 的工况；SPL 的计算步为 25 ns。**答案：** Fig. 6 中 SPL 与 one-step EMTP 的 absolute-error waveform 大体重合，局部 inset 标注两者差异最大为 0.164 A 和 0.0022 A；这支持“在该 DAB、该 transient 下，AII/HPE 没有造成明显额外误差”，但不是对所有步长或 topology 的收敛证明。[pdf:E07]（PDF 物理页 7，Section V-B）[pdf:E08]（PDF 物理页 8，Fig. 6）

**问题 2：HPE 与 AII 是否降低计算时间和 FPGA arithmetic resource？ → 实验：** Table II 在同一 VC707 case 中比较 SPL with HPE、SPL without HPE、modified EMTP。**答案：** 报告的 calculation time 分别为 10.7 ns、18.2 ns、22.3 ns；SPL with HPE 使用 3651 register slices（4.8%）、1483 LUTs（0.4%）、64.5 block RAM（6.3%）与 72 DSP48s（2.6%）。它在 time、register、LUT、DSP 上优于另外两项，但 HPE 的 block RAM 反而高于 without-HPE 的 36.5（3.5%），所以“所有资源都更少”并不成立，准确说法应是总体 arithmetic/timing trade-off 更好、BRAM 有反向代价。[pdf:E07]（PDF 物理页 7，Table II）

**问题 3：RT-HIL waveform 是否接近真实 power converter？ → 实验：** 作者让 20 kHz physical DAB 的 bidirectional power 在约 2 s 内从 \(20\ \mathrm{kW}\) 缓慢变化到 \(-20\ \mathrm{kW}\)，比较 SPL HIL 与 oscilloscope/DL850 记录的 power-level experiment。**答案：** 作者报告动态响应与数值接近；但也明确观察到 ideal switch model 无法复现 physical nonlinear switch 在 zero-current 附近的 oscillation，且不能计算 switching loss 与 input/output power。这一实验验证的是 20 kHz、缓变功率工况下的整体 HIL 可用性，不是 400 kHz 的 power-level validation。[pdf:E08]（PDF 物理页 8，Fig. 7 与 Section V-C）

**问题 4：half-step sampling 在高开关频率下是否优于同为 25 ns step 的 one-step sampling？ → 实验：** 作者在 200 kHz 和 400 kHz 比较 SPL half-step 与 modified EMTP one-step，并以 reference waveform 计算 \(L_O\) current 最大相对误差。**答案：** 200 kHz 时 one-step 为 4.32%，half-step 为 2.08%；400 kHz 时 one-step 为 7.79%，half-step 为 2.23%。作者还报告 400 kHz 下 phase-shift gate detection precision 达到 \(1.8^\circ\)。这直接支持“当 gate edge quantization 成为主要误差源时，\(T/2\) sampling 比每 \(T\) sampling 更好”。[pdf:E08]（PDF 物理页 8，Section V-D）[pdf:E09]（PDF 物理页 9，Fig. 8 与 Fig. 9）

附录 Table V 存在一个应显式保留的内部一致性问题：表头把 400 kHz 的 2.23% 放在 one-step、7.79% 放在 half-step 列，与 Fig. 8 标注、Fig. 9 legend 和正文结论相反；低频行也出现同样的列趋势。因 Fig. 8 直接在曲线上标注 one-step 7.79% 与 half-step 2.23%，本卡采用 Fig. 8/Fig. 9 的方法对应关系，不用 Table V 的列标题作为独立数值依据。[pdf:E09]（PDF 物理页 9，Fig. 8、Fig. 9）[pdf:E10]（PDF 物理页 10，Appendix Table V）

**问题 5：相对 commercial RT-HIL 是否有实际性能优势？ → 实验：** 商用平台以 200 ns sampling step 运行，SPL 以 12.5 ns sampling step 运行；两者都测试 20 kHz 和 400 kHz。**答案：** 20 kHz 下两者 waveform 都被作者判断为 acceptable，400 kHz 下 commercial solver 出现 aliasing oscillation，而 SPL 仍给出规则 waveform。Table III 另报告 SPL/commercial 的 minimum time-step 为 25/145 ns、maximum switching frequency 为 400/200 kHz、largest simulation size 为 120/56 switches。[pdf:E09]（PDF 物理页 9，Fig. 10、Fig. 11、Table III）

这一 commercial comparison 不能被外推成普遍的产品优劣结论：两个平台的 solver、sampling step、hardware capacity 与 toolchain 均不同，论文没有做相同 FPGA、相同 resource budget、相同 model fidelity 的 controlled ablation，也没有报告 jitter、deadline miss、重复试验、置信区间或独立复现。它证明的是本文配置下的系统演示，不是对 commercial solver family 的全面 benchmark。

## § 8 — Take-aways

**5 句话：**

1. HPE 把 switch behavior 隔离为受控源，使 system-level matrix 在 CCM 假设下保持固定。[pdf:E03]（PDF 物理页 3，Eq. (2)-(5) 与 CCM 限制）
2. AII 把 capacitor voltage 与 inductor current 放在错开的时间格点，令四类 solver entity 可以用已知历史量并行递推。[pdf:E04]（PDF 物理页 4，Eq. (6)-(11) 与 Fig. 3）
3. HST 因而在 25 ns 完整计算步内提供 12.5 ns gate sampling，而不是简单缩短整个 solver step。[pdf:E05]（PDF 物理页 5，Eq. (12)-(15)）[pdf:E09]（PDF 物理页 9，Fig. 11）
4. DAB simulation 在 200/400 kHz 下把最大相对误差从 4.32%/7.79% 降到 2.08%/2.23%，且硬件表显示 10.7 ns kernel calculation time。[pdf:E07]（PDF 物理页 7，Table II）[pdf:E09]（PDF 物理页 9，Fig. 8）
5. 最强的证据边界是高频优势只在 ideal/CCM-oriented model 中展示，20 kHz power experiment 已暴露 zero-current oscillation 与 loss modeling 缺口。[pdf:E08]（PDF 物理页 8，Fig. 7 与 Section V-C）

**3 句话：**

1. 论文真正的新机制是把“完整状态更新周期”和“gate signal 可被消费的周期”解耦为 \(T\) 与 \(T/2\)。[pdf:E04]（PDF 物理页 4，Fig. 3）[pdf:E05]（PDF 物理页 5，Eq. (12)-(15)）
2. FPGA entity、fixed-point implementation 和 DAB benchmark 说明该机制能落到真实 hardware schedule，而不只是纸面公式。[pdf:E06]（PDF 物理页 6，Fig. 4 与 Section IV-C）[pdf:E07]（PDF 物理页 7，Fig. 5 与 Table II）
3. 但采样更密只有在 switching model 正确时才有意义，DCM、deadtime 与 zero-current commutation 仍是尚未闭合的风险。[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E08]（PDF 物理页 8，Section V-C）

**1 句话：**

SPL 用时间错位的 state decomposition 换取采样率，但只有当开关等效仍有效时，“采得更快”才真正等于“仿得更准”。[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E05]（PDF 物理页 5，Eq. (12)-(15)）

## § 9 — 最脆弱的假设

最脆弱的假设是：目标 converter 在需要高精度 RT-HIL 的关键区间内，可以用只含 \([1,0]\) 与 \([0,1]\) 两种 half-bridge state 的 CCM switching-function model 忠实表示。这个假设一旦失败，HST 即使把 gate edge 时间量化从 \(T\) 降到 \(T/2\)，也只是在更准确的时刻更新一个错误的 topology。

论文自己给出了两组直接证据。第一，Section II-B 明确说基本模型仅对 continuous current mode 有效，不能直接支持含 deadtime 与 blocking 的 DCM；建议是另接 conventional diode switching model，但没有展示混合后是否还能保持固定矩阵、无迭代、10.7 ns kernel timing 与 half-step schedule。[pdf:E03]（PDF 物理页 3，Section II-B 末段）第二，20 kHz power experiment 已观察到 ideal model 无法复现 physical switch 在 zero-current 附近的 oscillation，并且不能计算 switching loss 与 input/output power。[pdf:E08]（PDF 物理页 8，Section V-C）

缺失的关键证据是：在 deadtime、轻载、功率反向、burst/blocking 和 CCM↔DCM transition 中，solver 是否仍满足 topology fidelity 与 real-time deadline。由于 DAB 本来就会跨越电流零点，这不是边缘美学问题，而可能同时破坏 waveform、loss、phase-shift response 与 controller decision。

## § 10 — 最小复现实验

一周内最值得复现的是“相同 25 ns 计算步下，12.5 ns half-step sampling 是否真的降低 gate-edge quantization error”，而不是先复刻整个 HIL rack。

1. 用 Appendix Table IV 的 DAB 参数建立一个高精度 reference model：\(U_{DC1}=600\ \mathrm{V}\)、\(U_{DC2}=400\text{-}600\ \mathrm{V}\)、\(L_k=42\ \mu\mathrm{H}\)、\(L_m=2.49\ \mathrm{mH}\)、\(C_H=1000\ \mu\mathrm{F}\)、\(C_L=250\ \mu\mathrm{F}\)、\(R_I=R_O=0.001\ \Omega\)。[pdf:E10]（PDF 物理页 10，Table IV）
2. 实现两条使用同一 fixed-point arithmetic 和同一 25 ns state-update budget 的路径：modified one-step trapezoidal/EMTP 每 25 ns 读取 gate，SPL recurrence 每 12.5 ns 更新 \(h_i/h_v\)。先用 64-bit、24 integer bits 与论文一致，再以 floating-point 软件实现作交叉检查。[pdf:E05]（PDF 物理页 5，Eq. (12)-(15)）[pdf:E06]（PDF 物理页 6，Section IV-C）
3. 在 200 kHz 与 400 kHz 下扫描 gate edge 相对 25 ns grid 的所有 offset，并加入一次 phase-shift command step；用 1 ns 或更细的 event-aligned reference 记录 gate-edge latency、\(L_O\) current 最大相对误差与能量误差。
4. 若 half-step 对所有 offset 的最坏 gate latency不超过 12.5 ns，并在 200/400 kHz 把最大 current error 分别压到接近论文的 2.08%/2.23%，且显著低于 one-step 的 4.32%/7.79%，则支持核心 sampling claim；若优势只出现在特定 edge alignment、换 reference 后消失，或 fixed-point recurrence 产生额外误差，则反驳该 claim 的稳健性。[pdf:E09]（PDF 物理页 9，Fig. 8）
5. 最后只对两条 kernel 做一次 Vitis HLS synthesis，检查 critical path 与 resource report 是否允许 25 ns step；无需先接 ADC/DAC 或复刻 power stage。

论文未报告 Fig. 8 的完整 gate sequence 与 phase-shift command，所以这个实验验证的是机制和量级，不声称 byte-for-byte 重现原图。

## § 11 — 最强反例设计

最强反例不是把 circuit 盲目放大，而是让 DAB 在 400 kHz 下受控地进入论文基本模型无法表达的 commutation mode：逐步减小负载并扫描 deadtime，使 transformer current 在部分周期内过零、二极管自然续流，随后加入 power reversal 与短时 blocking。reference 使用带 device diode、deadtime 和寄生参数的 event-driven switching model，并同步采集 power hardware waveform；被测对象同时包括原始 CCM-HPE SPL，以及论文建议的“conventional diode switching model + SPL”组合。

攻击指标应同时测四件事：gate edge 被采到的时间、commutation state 是否正确、\(L_O/L_k\) current 与 port voltage 的 waveform error、以及 deadline/resource 是否仍满足 25 ns step。若原始 SPL 在 timing 上仍达到 12.5 ns，却因漏掉 \(00\) state、diode conduction 或 zero-current oscillation 而产生比 one-step full-switch model 更大的 waveform 与 power error，就出现了明确的替代解释：Fig. 8 的优势来自 ideal CCM model 内的 gate quantization，而不是对真实高频 switching physics 的普遍提升。[pdf:E03]（PDF 物理页 3，DCM 限制）[pdf:E08]（PDF 物理页 8，zero-current mismatch）

若加入 conventional diode model 能恢复 accuracy，却使 system matrix 不再固定、引入迭代或超过实时 deadline，同样会实质挑战核心贡献，因为“模型忠实度、半步采样、固定资源实时性”三者不能同时成立。反之，若混合模型在全部 mode transition 中仍保持较低误差与 deadline，才真正补强论文最薄弱的外推。

## § 12 — Follow-up Research Idea

在 TIE 所属的 industrial electronics / power electronics real-time simulation 领域，高影响工作通常需要同时满足：方法机制清楚、数值与 switching physics 忠实、hardware deadline 可证明、并有跨工况的 controller-或 power-level validation。基于本文证据，值得追的不是再给 SPL 增加一种 topology template，而是把问题改写为：**在 mixed conduction mode 下，如何联合调度 topology event 与 staggered state update，并对每次 mode transition 给出可检查的误差和 deadline contract。**

**(a) 未满足需求。** 宽禁带 converter 的高频运行同时放大 gate sampling、deadtime、diode commutation 和 loss modeling 的重要性；现有 SPL 只闭合了前一项，并在 zero-current 附近暴露模型失配。[pdf:E03]（PDF 物理页 3，Section II-B）[pdf:E08]（PDF 物理页 8，Section V-C）

**(b) 研究价值。** 若一个 solver 能在 CCM、DCM、blocking 与 power reversal 间切换，同时保留 half-step latency 与 bounded resource usage，它会把“更快采样”提升为“事件时刻与物理 mode 都可信”的 RT-HIL guarantee；这比单独增加一个应用 case 更接近本领域认可的系统贡献。

**(c) 可借鉴工具。** 可以借用 hybrid systems 的 mode automaton、complementarity formulation 的 diode/contact condition、local event detection，以及 real-time scheduling 中的 worst-case execution-time analysis。核心架构不是每次事件重做全局 matrix，而是只让受影响的 switch leg 进入局部 complementarity/event solve，其余 linear subspace 继续使用预处理 leapfrog operator。

**(d) 首个证伪实验。** 在同一 FPGA budget 下生成覆盖 CCM↔DCM、deadtime、blocking、功率反转的随机但可重放 gate/load sequence；若任一 transition 使 waveform error 超过 one-step full-switch baseline，或 worst-case execution time 越过 25 ns deadline，该想法立即被证伪。反之，仅在 nominal CCM 提升平均精度不算成功。

**(e) 与本文的实质区别。** 本文固定 switching-function model 后优化采样；这个方向把 mode correctness 与 event timing 本身纳入 solver state 和验收对象，研究目标从“每半步采一次 gate”改为“每个物理 commutation event 都有合法 topology、合法 state 与可兑现 deadline”。由于本卡只使用当前 PDF、没有对相邻 hybrid EMT/FPGA 文献做完整检索，这是一项证据约束下的候选研究方向，不声称 novelty。
