# A Controller HIL Testing Approach of High Switching Frequency Power Converter via Slower-Than-Real-Time Simulation

作者：Hao Bai、Gang Huang、Chen Liu、Yigeng Huangfu、Fei Gao [pdf:E01]

出处：IEEE Transactions on Industrial Electronics，Vol. 71，No. 8，pp. 8690–8702 [pdf:E01]

年份：2024 [pdf:E01]

DOI：10.1109/TIE.2023.3321992 [pdf:E01]

Zotero key：BN4C9XBE

证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** Controller hardware-in-the-loop（CHIL）要让真实控制器通过数字输入和模拟输出接口闭环控制一个实时运行的变换器模型。高 switching frequency 同时击中了两条硬约束：固定步长模型必须足够快地采到 PWM 边沿，模拟器的 analog output（AO）还必须足够快地把开关周期内的波形送给控制器。论文指出，工程上常取比 switching period 小约 100 倍的 simulation time-step，而当时列举的商业模拟器最小步长约为 100–200 ns；因此超过 100 kHz 后，PWM 采样和离散误差开始变得难以压低。[pdf:E01]（PDF 物理页 1，Introduction）

第二个瓶颈不是求解器，而是 I/O。论文汇总的主流平台 AO 最高 conversion rate 为 0.5–7.8 MSPS；即使 7.8 MSPS 面对 1 MHz 变换器，一个周期理想情况下也只有最多 7 个输出点。作者在 NI USB-7845R 上还测到多通道、±5 V 输出时约 3 μs settling time：20 kHz 正弦每周期约 16 个离散点且已有失真，100 kHz 正弦则完全失真。[pdf:E02]（PDF 物理页 2，Table I、Fig. 1 及相邻正文）

因此，论文真正要解决的问题是：**不升级实时模拟器硬件，能否仍用真实控制器测试原本超出 RTS 能力的高频变换器？** 作者的答案不是继续追求更快的 real time，而是把控制器和仿真模型按同一倍率放慢，让二者在“模拟时间”上仍同步。其工程价值在于把早期代码调试、控制边界探索、故障测试和闭环验证延伸到高频功率变换器，同时避开真实功率原型早期测试的成本与风险。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

## § 2 — 前人工作与不足

**相关文献中的已有结论，按本论文的综述。** 既有路线主要有两类。第一类压缩 FPGA solver latency：论文列举的 state-space、matrix-inversion、predictive 和 direct-mapped 方法分别达到 75/80 ns、平均 36 ns、25 ns 和最小 25 ns 的案例步长。第二类对 gate drive signal 进行 oversampling，再用 interpolation、extrapolation 或 integration 处理一个 simulation step 内的多个采样，以减小 PWM aliasing；并行 oversampling 还试图降低多开关事件的资源和时序代价。[pdf:E01][pdf:E02]（PDF 物理页 1–2，Introduction；相关条目在物理页 12–13 的 References 中列出 [pdf:E12][pdf:E13]）

这些工作已经能显著降低模型计算步长或 PWM 边沿采样误差，但作者指出两项未被同时消除的限制。其一，继续缩短步长会受 FPGA timing closure 和计算资源限制，特别是 200 kHz 以上；oversampling 还会增加信息融合的计算负担。其二，即便内部求解足够快，AO 的 DAC/settling rate 仍可能无法把高频开关波形忠实送出；单纯优化 solver 不会提高模拟接口带宽。[pdf:E02]（PDF 物理页 2，Introduction、Table I、Fig. 1）

论文也专门区分了 processor-in-the-loop（PIL）与 HIL：PIL 主要验证目标处理器上的 object code，并只要求样本间同步；HIL 还包含真实 controller I/O 和物理时间约束。STRTS 针对的正是后者，不能被“把控制算法放到处理器里跑一下”的 PIL 替代。[pdf:E06]（PDF 物理页 6，Section III-D）

## § 3 — 重建作者的思考路径

在不预设论文方案的前提下，可以重建出如下路径。

1. 理想 CHIL 要求 controller time、simulator time 与 physical real time 对齐；RTS 中通常有 \(T_c=h_c\)、\(T_s=h_s\)，真实控制器因此“感觉”自己在驱动真实设备。[pdf:E03]（PDF 物理页 3，Figs. 2–3）
2. 提高 switching frequency 会同时缩短允许的 \(h_s\) 和可供 AO 输出一个周期波形的时间。实验曲线显示，为使 buck 的 two-norm average error 小于约 2%，步长需约为 switching period 的 1/100；端到端 RTS latency 还受 \(T_{sAO}\) 主导。[pdf:E04]（PDF 物理页 4，Fig. 4、Eqs. (1)–(3)）
3. 若硬件无法让 execution cycle 等于这个理想 time-step，与其假装仍是 real time，不如承认 wall-clock 已经慢于 simulation time。关键问题随即变成：控制器能否也按同一倍率变慢，从而保持闭环中的相对时间关系？
4. 如果 controller execution、PWM period 和 simulator execution 都乘以同一个 \(K\)，而控制算法的 \(h_c\) 与模型的 \(h_s\) 保持不变，那么控制器与模型在各自的“模拟时间”里仍同步；同时，每个高频周期在墙钟时间上被拉长，FPGA 和 AO 获得更多执行与 settling 时间。[pdf:E05]（PDF 物理页 5，Eqs. (4)–(11)、Fig. 6）

第 3–4 步是**基于论文证据的合理推断**：作者不是提高了硬件真实带宽，而是把被测闭环变成一个按比例 time dilation 的系统，再假设这种 dilation 不改变控制功能本身。

## § 4 — 核心 Intuition

把高频变换器和控制器都按相同倍率 \(K\) 放慢，真实时间里原本过短的计算、PWM 与 AO 输出窗口就被拉长；但二者在模拟时间里的相对节奏不变，所以仍能闭环。[pdf:E03][pdf:E05]（PDF 物理页 3、5，Figs. 2、6）

换句话说，论文用“放弃 real-time 速度”换取“保留 controller-under-test 与 simulated plant 的相对时序”，从而绕开 solver 和 AO 的绝对带宽上限。它奏效的关键不是模型更精确，而是所有会影响闭环的时间量都能被同倍率缩放。

## § 5 — 具体方法与完整 Pipeline

以论文的 200 kHz synchronous buck 为例，完整 pipeline 如下。

1. **确定模型与 simulation time-step。** MOSFET 和 diode 用 binary resistor model 表示，ON 为小电阻、OFF 为大电阻；电感和电容采用 implicit Euler companion circuit 离散化，再用 nodal analysis 形成 \(G V=I\)。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Figs. 8–9、Eqs. (12)–(16)）
2. **处理开关状态与单步依赖。** FPGA 每个 fixed step 根据 PWM 和 diode voltage 更新开关状态；由上一步变量组装 current-source vector \(I\)，选择预先计算并存储的 \(G^{-1}\)，并行完成 \(V=G^{-1}I\)，再计算 branch voltage/current 并反馈到下一步。论文只明确处理这个两开关 buck 的有限 switch combinations；多开关同时事件、event interpolation 和 EMT 大网络分区均未报告。[pdf:E07]（PDF 物理页 7，Fig. 11 及相邻正文）
3. **映射到 FPGA 并测 execution cycle。** 设计用 LabVIEW FPGA 生成 VHDL，经 Xilinx 工具得到 bitfile，运行在 NI USB-7845R 的 Kintex-7 XC7K70T 上。模型位于 single-cycle timed loop，loop clock 决定 \(T_s\)；论文举例 5 MHz 对应 200 ns，若 timing violation 则必须降低 clock。[pdf:E07]（PDF 物理页 7，Figs. 10–11）
4. **测 AO 并选 slowdown ratio。** 先由目标 PWM sampling error 得到 \(h_s\)，再由模型可实现的 \(T_s\) 得到 \(K_1\)；由 AO conversion cycle \(T_{sAO}\) 和每周期所需输出点数 \(P\) 得到 \(K_2\)，最终取 \(K=\max(K_1,K_2)\)。对 200 kHz case，作者取 \(h_s=20\) ns 对应 0.4% PWM sampling error，\(T_s=200\) ns 得 \(K_1=10\)；测得 \(T_{sAO}=3\) μs，取 \(P=10\) 得 \(K_2=6\)，故用 \(K=10\)。[pdf:E08]（PDF 物理页 8，Section IV-D）
5. **同步修改真实 controller。** 控制器使用 TMS320F28335 DSP。控制算法在 ADC ISR 中运行；进入 STRTS 时，将 TBPRD、DBRED、DBFED 和 CMPA 等 PWM/dead-band 寄存器按 \(K\) 放大，并让 ADC interrupt cycle 同倍率变长。DSP 的 PWM 经 FPGA DIO 输入，FPGA 输出的 inductor current 与 capacitor voltage 经 AO 被 DSP ADC 采样，形成闭环。[pdf:E08]（PDF 物理页 8，Fig. 12 及相邻正文）
6. **执行 CHIL。** 200 kHz 物理 converter 在 STRTS 中表现为 20 kHz PWM；controller execution cycle 从 10 μs 拉长到 100 μs，模型仍用 \(h_s=20\) ns 的模拟步长，但 wall-clock execution cycle 为 200 ns。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Table III 与 Section V-B）

FPGA resource 报告是可复核的：XC7K70T 总计 10,250 slices、82,000 slice registers、41,000 LUTs、135 block RAMs、240 DSP48s；scenario 1 / scenario 2 分别使用 2,920/3,436 slices、6,897/6,736 registers、8,361/9,413 LUTs、1/1 block RAM、202/220 DSP48s。[pdf:E08]（PDF 物理页 8，Table II）但 arithmetic representation（fixed-point 或 floating-point）、word length、rounding/saturation、memory bandwidth、post-route timing slack、功耗和 FPGA build latency 未报告。接口电路原理图、ADC calibration、AO reconstruction/filter、DI 实测 latency 和端到端闭环 latency 也未报告。本文只实现单个 buck，不报告 EMT 多节点系统规模、网络分解、跨 FPGA 并行或 real-power system integration。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文有两层数学：先推导“为什么要慢多少”，再给出 buck 的离散网络。

**1. RTS latency 与 PWM resolution。** RTS 对 PWM 的响应延迟写成

\[
T_{\mathrm{RTS}}=T_{sDI}+T_s+T_{sAO}\le \frac{1}{N}T_{\mathrm{pwm}},
\qquad
\varepsilon=\frac{h_s}{T_{\mathrm{PWM}}}.
\]

这里 \(T_{sDI}\)、\(T_s\)、\(T_{sAO}\) 分别是 digital input、模型执行和 analog output cycle；\(N\) 是希望一个 PWM 周期至少被分成的时间份数；\(\varepsilon\) 是 time-step 相对 PWM period 的采样误差。工程直觉是：模型算得再快，若 AO settling 占掉了大部分周期，控制器仍看不到可信波形。[pdf:E04]（PDF 物理页 4，Eqs. (1)–(3)）

**2. 由两条约束选择 \(K\)。** 计算能力要求

\[
K_1=\frac{T_s}{h_s}=\frac{T_s}{\varepsilon T_{\mathrm{PWM}}},
\]

AO 要求先有 \(N=T_{\mathrm{pwm}}/T_{sAO}\)，再令至少 \(P\) 个点构成一个周期，因此

\[
T_{\mathrm{pwm}}^{*}=P T_{sAO},
\qquad
K_2=\frac{T_{\mathrm{pwm}}^{*}}{T_{\mathrm{pwm}}}
=P\frac{T_{sAO}}{T_{\mathrm{pwm}}}.
\]

最终

\[
K=\max(K_1,K_2),\quad
T_s'=K h_s,\quad
T_c'=K h_c,\quad
T_{\mathrm{pwm}}'=K T_{\mathrm{pwm}}.
\]

\(h_s\) 和 \(h_c\) 是模型内部使用的 simulation/control time-step，不随 wall clock 变；被拉长的是 execution cycle 和 PWM period。论文 Eq. (8) 给出最小值 \(K=\max(K_1,K_2)\)，后文又写应满足 \(K>\max(K_1,K_2)\)；更一致的工程表述应是 \(K\ge\max(K_1,K_2)\)，并取满足实现裕量的最小可行值，因为过大 \(K\) 会继续降低测试效率。[pdf:E05]（PDF 物理页 5，Eqs. (4)–(11)）

**3. Buck 离散网络。** implicit Euler 把电感、电容分别变成 conductance 与 history current source：

\[
i_L^{n+1}=i_L^n+\frac{h_s}{L}v_L^{n+1}
=G_L v_L^{n+1}+J_L^{n+1},
\]

\[
i_C^{n+1}=\frac{C}{h_s}v_C^{n+1}-\frac{C}{h_s}v_C^n
=G_C v_C^{n+1}-J_C^{n+1},
\]

其中 \(G_L=h_s/L\)、\(J_L^{n+1}=i_L^n\)、\(G_C=C/h_s\)、\(J_C^{n+1}=G_Cv_C^n\)。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Eq. (12) 及其变量定义）对四个节点写成 \(GV=I\)；因为只有两只开关，作者预先枚举并存储各 switch state 的 \(G^{-1}\)，在线阶段只做 matrix-vector dot product。[pdf:E07]（PDF 物理页 7，Eqs. (13)–(16)、Fig. 11）这也是 FPGA 能并行化的关键。

## § 7 — 实验设计与结论

**问题 1：同一个可实时运行的 converter，STRTS 是否与 RTS 等效？**  
**实验。** 以 10 kHz buck 为基准，RTS 与 STRTS 使用同一模型和 \(h_s=1\) μs；RTS 的 \(T_s=1\) μs、\(T_c=100\) μs，STRTS 取 \(K=2\)，于是 \(T_s'=2\) μs、\(T_c'=200\) μs，dead band 也从 2 μs 变成 4 μs。输入 50 V、\(L=1\) mH、\(C_{out}=242\) μF、load 5 Ω，采用 current-loop PI。[pdf:E09]（PDF 物理页 9，Table III、Section V-A）作者比较 4 A steady inductor current，以及 1 A↔4 A step responses。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Figs. 14–15）  
**答案。** 论文报告两组波形形状与 transient 一致，差别是 STRTS 的 wall-clock time axis 恰为两倍，因而作者认定其 controller-testing effect 与 RTS 等效。[pdf:E09][pdf:E10] 但论文没有报告 normalized RMSE、overshoot/settling-time difference、重复次数或统计置信区间；“等效”主要来自图形对照，不能外推为已量化的误差界。

**问题 2：面对原 RTS 能力之外的 200 kHz converter，STRTS 是否接近真实 prototype？**  
**实验。** 物理 buck 与 CHIL 使用可互换的同一 DSP controller，只在 software execution cycle 上调整。prototype 参数包括 input 20 V、\(L=16\) μH、\(C_{out}=242\) μF、load 2 Ω，采用 voltage-current double-loop PI；实验 controller time-step/execution cycle 为 10 μs。STRTS 保持 \(h_s=20\) ns，但用 \(K=10\) 令 \(T_s'=200\) ns、\(T_c'=100\) μs，并把 PWM 从 200 kHz 放慢到 20 kHz。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Table III、Section V-B）比较项包括：4 A steady current；6/8/10 V steady output；1 A↔4 A current step；2 V↔10 V voltage step；在 3 A current-control mode 下进行 2 Ω↔4 Ω load disturbance。[pdf:E10][pdf:E11][pdf:E12]（PDF 物理页 10–12，Figs. 16–19）  
**答案。** 作者报告 STRTS 与 prototype 的 steady-state 和 transient 波形一致，只是 wall-clock time axis 被拉长 10 倍，据此声称方法能可信地测试 200 kHz converter。[pdf:E10][pdf:E11][pdf:E12] 仍然没有数值误差指标、重复实验、噪声/量化敏感性、极限稳定工况、fault case 或不同 topology 验证，因此证据只闭合到“单台 synchronous buck、两组 \(K\)、所示 PI 工况下的波形一致性”。

**资源与实时性边界。** scenario 2 使用 3,436 slices、9,413 LUTs、220 DSP48s 等资源，并以 200 ns wall-clock execution cycle 承载 20 ns simulation time-step。[pdf:E08][pdf:E09] 论文未报告 post-route timing margin、资源随 topology size 的 scaling、真实 AO/ADC 端到端 latency distribution 或硬 real-time deadline miss。作者还明确承认 STRTS 调试更慢、数据量更大，部分 commercial simulator/controller 无法分开配置 time-step 与 execution cycle，而且它不能用于涉及 real power 或与真实世界不同步的 system integration/co-simulation。[pdf:E08][pdf:E09]（PDF 物理页 8–9，Section IV-E）

## § 8 — Take-aways

**5 句话：**

1. 高频 CHIL 的瓶颈既有 FPGA solver/PWM sampling，也有 AO conversion/settling，优化其中一项不足以闭合系统能力。[pdf:E01][pdf:E02]
2. STRTS 的核心是让 simulator、controller execution 与 PWM wall-clock period 同倍率放慢，同时保持模型内部 \(h_s\) 和控制 \(h_c\) 不变。[pdf:E05]
3. slowdown ratio \(K\) 由模型计算约束 \(K_1\) 与 AO 输出约束 \(K_2\) 的较大者决定。[pdf:E05]
4. 论文在 10 kHz、\(K=2\) 时与 RTS 对照，并在 200 kHz、\(K=10\) 时与 prototype 对照，展示了 steady、step 和 load-disturbance 波形的一致性。[pdf:E09][pdf:E10][pdf:E11][pdf:E12]
5. 证据尚不能证明所有 controller timing effect 都可按比例保持，也不能覆盖多 converter、fault、system integration 或定量误差界。

**3 句话：**

1. 当 real time 太快而硬件跟不上时，可以把整个 CHIL 闭环按统一比例放慢，而不是继续压榨真实带宽。
2. 这一策略在论文的单个 buck、两种 slowdown ratio 上得到波形级支持，但没有得到统计或跨拓扑支持。
3. 它最适合 software-configurable 的离线 controller test，不适合含不可缩放真实物理环节的 system integration。[pdf:E09]

**1 句话：** STRTS 用同倍率 time dilation 换取高频 CHIL 的可执行性，其价值真实存在，但“等效”成立的范围由所有时间敏感环节是否都能被忠实缩放决定。

## § 9 — 最脆弱的假设

最脆弱的假设是：**所有会影响 controller decision 的时间量，都能随 \(K\) 同倍率缩放，或其未缩放部分小到可以忽略。**

论文直接缩放了 controller execution cycle、PWM period、dead band 和 simulator execution cycle，并用 \(K=2\)、\(K=10\) 的 buck 波形说明基本闭环可保持。[pdf:E05][pdf:E08][pdf:E09] 然而真实控制器中仍可能存在不按 \(K\) 缩放的 ADC acquisition/conversion delay、ISR computation latency、timer quantization、communication timeout、watchdog、asynchronous trip、sensor/anti-alias filter、clock jitter 和外部保护电路。尤其当真实系统接近 stability margin、fault trip 边界或 computation delay 已占控制周期显著比例时，STRTS 会把这些固定 wall-clock delay 在“模拟时间”中缩小到原来的 \(1/K\)，从而可能让一个在真实硬件上会振荡或误触发的 controller 在 CHIL 中看起来正常。

这是**基于证据的合理推断**，不是论文已证明的失败。论文给出的支持限于同一 DSP、简单 PI loop、steady/step/load disturbance 的视觉一致性；它没有给出端到端 latency decomposition、\(K\) sweep、near-instability controller、fault/protection case 或 unscaled peripheral audit。作者自己也明确说 STRTS 不能用于含 real power 的 system integration，间接承认“外部真实时间不能统一缩放”是方法边界。[pdf:E09]（PDF 物理页 9，Section IV-E）

## § 10 — 最小复现实验

一周内最小复现应先验证最核心、且不需要 200 kHz prototype 的 claim：**归一化时间后，\(K=2\) 的 STRTS 是否真的复现 \(K=1\) RTS 的 controller response。**

- **数据与硬件：** 同一 FPGA buck model、同一 DSP controller 和同一 I/O；采用论文 scenario 1 的 10 kHz 参数、\(h_s=1\) μs、current-loop PI、1 A↔4 A reference step。[pdf:E09]
- **实现：** 跑 RTS \(K=1\) 与 STRTS \(K=2\)，除 TBPRD/DBRED/DBFED/CMPA、ADC interrupt 与 FPGA loop execution cycle 按论文规则缩放外，模型、controller gains、initial conditions 和采样通道保持完全相同。
- **测量：** 同步记录 controller ADC 看到的 current、PWM duty、reference、FPGA state；把 STRTS wall-clock axis 除以 2 后重采样对齐，计算 normalized RMSE、peak error、overshoot、rise/settling time difference，并记录 deadline miss 与 I/O latency。
- **预注册判据：** 作为本复现实验自定而非论文报告的门槛，可先要求 current NRMSE ≤2%，overshoot 与 settling time deviation 各 ≤5%，且无额外 deadline miss；同时检查误差是否随 reference direction 一致。
- **支持或反驳：** 满足门槛只支持“该 buck 与该 controller 在 \(K=2\) 下近似等效”；任一方向出现系统性 mismatch，或 mismatch 不能由 measurement noise 解释，就反驳同倍率缩放足以保持闭环的核心 claim。若设备允许，再把 \(K\) 扫到 5 和 10，看误差是否随 \(K\) 单调放大。

## § 11 — 最强反例设计

最强反例不是换一个更复杂 converter，而是保留同一 buck，却加入一个**绝对 wall-clock delay 决定成败**的 controller function。例如在真实 controller 上启用固定 1 μs 的 asynchronous overcurrent trip / desaturation emulation，或构造 computation delay 接近 stability margin 的 control law；该 delay 不随 ISR period 自动乘以 \(K\)。

先在 200 kHz prototype 上调到“故障 pulse duration 或 phase margin 恰好跨越 trip/stability 边界”的工况，再在 \(K=10\) STRTS 中复现完全相同的 controller hardware 和 I/O。若 STRTS 只拉长 plant/PWM/period，却让 1 μs 固定 delay 在 normalized time 中等效为 0.1 μs，它可能不触发、晚触发或显示更大的 phase margin。出现“prototype trip/oscillate，而 STRTS pass”，即使 steady waveform 仍相似，也会直接推翻“等效 controller testing performance”的广义解释。

这个反例强在它给出了具体替代解释：论文观察到的一致性可能来自所测 PI 工况对固定 peripheral delay 不敏感，而不是 uniform time dilation 对所有 controller behavior 都成立。论文当前的 Figs. 16–19 只覆盖 steady、reference step 与 load step，不包含这类 timing-critical fault/protection boundary。[pdf:E10][pdf:E11][pdf:E12]

## § 12 — Follow-up Research Idea

**候选判断，不声称 novelty。** 电力电子与 HIL 领域通常更看重可复核的硬件实现、明确的 timing/error budget、跨 topology 验证和对真实工程边界的解释，而不只是新增一个仿真模块。基于第 9 节，可把研究目标从“所有环节统一乘 \(K\)”改成 **time-dilation-aware CHIL：在变速测试中保持 dimensionless closed-loop timing invariants**。

**(a) 未满足需求。** 现有 STRTS 只显式缩放若干 software-configurable timer；真实 controller 还有不可缩放或离散缩放的 ADC、ISR、communication、protection、sensor/filter 和 clock effects。测试者需要知道哪些时间量已被保持、哪些被扭曲，以及这种扭曲是否足以改变 pass/fail。

**(b) 研究价值。** 新系统不把 \(K\) 当作一个全局假设，而是为每条 sensing/computation/actuation path 建立 normalized latency、jitter、bandwidth 和 quantization budget；能缩放的直接配置，不能缩放的由 latency-in-the-loop / interface emulation 补偿，不能补偿的则给出可证伪的 validity envelope。这样研究对象从“让仿真跑起来”变为“证明 time-dilated HIL 在何种 controller property 上仍等价”。

**(c) 可借鉴工具。** 可借鉴 hybrid systems 的 time-scale transformation、real-time co-simulation 的 logical-time synchronization，以及 networked control 的 delay/jitter robustness analysis；这里只提出连接方向，未做输入包外的相关工作检索。

**(d) 首个证伪实验。** 在同一 200 kHz prototype 与 CHIL 上，选两个分别对 fixed delay 不敏感和接近 stability/protection boundary 的 controller，扫 \(K=1,2,5,10\)。比较原始 STRTS、带 timing compensation 的方案与 prototype 的 normalized waveform、trip decision 和 stability margin；若补偿后 error 不降或 validity envelope 不能预测 failure，该想法即被证伪。

**(e) 与本文的实质区别。** 本文把 time scaling 当作成立前提，并用 waveform similarity 验证两个 case；候选方向把“哪些时间量可缩放、等效性如何量化、何时必须拒绝测试结论”本身变成研究问题。它不是增加一个 converter 或一个 FPGA module，而是把 CHIL 的输出从单一波形升级为带 timing contract 的可信结论。
