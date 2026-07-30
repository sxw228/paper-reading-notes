# A Novel Resilient Control of Grid-Integrated Solar PV-Hybrid Energy Storage Microgrid for Power Smoothing and Pulse Power Load Accommodation

作者：Manoja Kumar Behera；Lalit Chandra Saikia

出处：IEEE Transactions on Power Electronics, Vol. 38, No. 3, pp. 3965–3980

年份：2022（在线出版；卷期为 2023 年 3 月）

DOI：10.1109/TPEL.2022.3217144

Zotero key：BWKRWMKH

证据说明：

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

本文研究的是一个耦合问题：单相并网光伏微电网既要消化太阳辐照造成的慢变功率波动，又要承受电动机启动、空调和其他 pulse power load 带来的快变功率冲击，同时还要在电网欠压、过压、谐波和故障时维持直流母线与并网电流。作者指出，光伏功率或负载的突变会使 dc-link 电压偏离参考值；电压源逆变器的正常功率变换、并网同步与电能质量都依赖这个中间能量节点保持受控。[pdf:E01]（PDF 物理页 1，Abstract、Section I）

论文把价值落在三个工程量上。第一，H₂/Br₂ redox flow battery（RFB）承担能量型、慢变化功率，supercapacitor（SC）承担功率型、快变化功率，目标是既平滑光伏又减轻 RFB 的快速电流应力。第二，AWMOGI 从受扰电网电压中抽取 fundamental component，给单相 VSI 提供同步模板。第三，ISSA 调参的 TIDF 控制器同时用于 dc-link、MPPT 与 HESS 电流环，试图缩短不同控制子系统的暂态。[pdf:E01]（PDF 物理页 1，Abstract）这三部分如果成立，就能把“储能容量分工”“并网同步”“多环动态”放进一套统一控制，而不是分别优化后再被 dc-link 耦合破坏。

这里的“resilient”应谨慎理解为论文所测试工况下的扰动恢复能力，而不是经形式化证明的韧性保证。论文验证覆盖 MATLAB 仿真和 OPAL-RT real-time simulator（RTS），但没有物理光伏变换器、实际 H₂/Br₂ RFB 或 SC 功率级的实验。[pdf:E12]（PDF 物理页 14，Section V）

## § 2 — 前人工作与不足

论文把前人不足分成四条链路。储能侧，lead-acid 成本低但深放电会加速寿命损失，Li-ion 效率高但大规模成本高，NaS 可扩展却有高温安全风险，VRFB 寿命长但低于额定功率约 20% 时电解液循环效率受限；作者据此选择宣称具备高功率密度、91% round-trip efficiency、快速充放电和 MW 级扩展潜力的 H₂/Br₂ RFB。[pdf:E01]（PDF 物理页 1，Section I-A）HESS 侧，battery–flywheel、battery–SMES、battery–SC 等组合已经存在，但地理约束、机械部件或单一储能的能量/功率密度矛盾仍在；Table I 把作者认为的技术缺口集中为“高效率、快速动态的储能组合尚需深入研究”。[pdf:E03]（PDF 物理页 3，Table I）

控制侧，PID 在不确定性和扰动增加时暂态变大，SMC 需要精确状态与参数，MPC 计算量高，FLC 依赖专家知识；传统 PI 又难以同时照顾 MPPT、dc-link 与双储能电流环的快速动态。[pdf:E02]（PDF 物理页 2，Section I-A）同步滤波侧，PLL 在某些并网阻抗条件下会引入低频负增量电阻；SOGI 难以去 dc offset，MSOGI 和 SO-SOGI 虽改善偏置，却增加积分环节并受积分饱和影响，尤其对低阶主导谐波不理想。[pdf:E02]（PDF 物理页 2，Section I-A）

作者对 HESS 既有功率分配的具体批评更重要：文献 [10]、[11] 用未补偿 battery power 叠加高频分量来抵消电池及其控制器、BDDC 的慢动态，但这会把高频纹波和噪声带进 SC 电流参考，可能使 SC 控制输出不稳定。本文改为 Butterworth LPF 直接分割有效功率需求，再由快电流跟踪器跟踪两条参考。[pdf:E05]（PDF 物理页 5，Section III-B）需要注意，这些前人不足主要来自作者的综述和定性比较；本论文没有重新实现所有 prior method 做统一成本、寿命或鲁棒性基准。

## § 3 — 重建作者的思考路径

以下是基于论文证据的重建，不是作者逐字陈述。一个合理起点是：光伏与负载扰动最终都先表现为 dc-link 功率不平衡，因此先写出

\[
P_L-P_{pv}=\mp P_{bat}\mp P_{sc}\mp P_g ,
\]

把电网、RFB 和 SC 都看成可双向补偿这个缺口的通道。[pdf:E05]（PDF 物理页 5，Eq. (13)）

第二步来自储能的时间尺度差异：若让 RFB 跟踪平均功率，让 SC 跟踪突变功率，就可能在保持 dc-link 的同时减少 RFB 的快速电流摆动。于是用 LPF 把 \(P_{\mathrm{eff}}\) 分成低频 \(P_{\mathrm{lf}}\) 与高频 \(P_{\mathrm{hf}}\)，前者生成 RFB 参考电流，后者生成 SC 参考电流；再给 RFB 加 SOC、22 A 电流和功率约束。[pdf:E05]（PDF 物理页 5，Fig. 2、Eq. (14)、Section III-B）

第三步是认识到 dc-link 控制不能脱离并网同步和 PV 侧功率变化。作者让 AWMOGI 提取电网电压的同相与正交基波分量，用电网电压幅值自适应生成 dc-link 参考，并把 PV 功率以前馈项直接反映到并网电流参考中。[pdf:E04]（PDF 物理页 4，Eq. (6)–(12)）第四步才是控制器选择：用 TIDF 增加分数阶自由度，再用 ISSA 对多个环的 \(K_t,K_i,K_d,n,F\) 联合调参，以总积分平方误差作为适应度。[pdf:E08]（PDF 物理页 9，Sections III-E–III-G、Eq. (39)）这条思路的实质不是某一个新控制块，而是围绕 dc-link 功率平衡把储能分工、同步、前馈和多环调参串起来。

## § 4 — 核心 Intuition

核心 intuition 是把“快功率”和“慢能量”分给不同物理储能：SC 先吞吐瞬时差额，RFB 只跟踪低频部分，因此 dc-link 可以快恢复而 RFB 少承受电流尖峰。与此同时，AWMOGI 从畸变电压中抽取可用的基波模板，PV power feed-forward 让并网电流参考不必等 dc-link 误差积累后才响应。[pdf:E04]（PDF 物理页 4，Fig. 1、Eq. (6)–(12)）TIDF 与 ISSA 的角色是把这些环节的跟踪做快，而不是改变上述物理分工。

## § 5 — 具体方法与完整 Pipeline

以论文的 deficit power mode 为例，输入是单相 230 V、50 Hz 电网，一套由 7 个组件串联、8 串并联构成且 STC 峰值约 11.936 kW 的 PVA，以及 12 kW 负载；随后负载增加 2 kW，辐照再从 1 sun 降到 400 W/m²。[pdf:E13]（PDF 物理页 15，Section V-C、Appendix）完整 pipeline 如下。

1. **PV 与两级功率变换。** 单二极管 PVA 经过 boost converter；INC-VCC 根据 MPP 条件 \(dP_{pv}/dV_{pv}=I_{pv}+V_{pv}dI_{pv}/dV_{pv}=0\) 生成 \(V_{mp}\)，外电压环与内电流环各用 ISSA-TIDF 产生 boost 开关占空控制。[pdf:E06]（PDF 物理页 6，Section III-C、Eq. (19)–(21)）boost 输出进入 dc-link，VSI 再把 dc power 注入单相电网。

2. **并网同步与 dc-link 环。** AWMOGI 输入 PCC 电压，输出同相、正交基波分量；由此估计基波幅值 \(V_{gfa}\) 和单位模板 \(V_{gu}\)。作者取 \(V_{dc,ref}=\psi V_{gfa}\)，其中 \(\psi\ge1.1\)，实际设为 1.22；dc-link 误差经 TIDF 生成损耗分量，PV 功率前馈项 \(I_{Dpv}=2P_{pv}/V_{gfa}\) 与之组合为并网电流幅值，再乘 \(V_{gu}\) 得到瞬时参考，最后用 hysteresis controller 产生 VSI gate pulses。[pdf:E04]（PDF 物理页 4，Eq. (6)–(12)）

3. **HESS 功率分配。** 计算 \(P_{\mathrm{eff}}=P_L-P_{pv}\) 后，以截止频率 3.35 Hz 的 Butterworth LPF 得到 \(P_{\mathrm{lf}}\)，残差为 \(P_{\mathrm{hf}}\)。RFB 参考为

\[
I_{bat,ref}=\frac{P_{\mathrm{lf}}}{V_{bat}},
\]

并被限制在 \(|I_{bat,ref}|<22\text{ A}\) 且 \(10\%\le SOC_{bat}\le90\%\)；SC 则由 \(P_{\mathrm{hf}}/V_{sc}\) 形成参考，论文允许其完全充放电。[pdf:E05]（PDF 物理页 5，Eq. (14)、Section III-B）

4. **模式与开关。** 若功率有余，RFB/SC 充电并在储能达到约束后向电网送出剩余功率；若功率不足，SC 先承担高频瞬态，RFB 跟随低频缺口，达到 RFB 电流或 SOC 边界后由电网补足。Fig. 3 的 flowchart 同时检查 surplus/deficit、RFB SOC、3.35 Hz 分量和最大电流，再决定各 bidirectional dc-dc converter 的 charging/discharging gate pulses。[pdf:E06]（PDF 物理页 6，Fig. 3）

5. **执行平台。** 离线模型在 MATLAB/Simulink 运行；随后完整 plant 和 controller 都部署到 OPAL-RT 4510，host PC 通过 RT-LAB 和 RJ45 LAN 连接，RTS 采样时间为 10 μs，波形由 mixed-domain oscilloscope 显示。[pdf:E12]（PDF 物理页 14，Section V）Appendix 另报离线仿真采样时间 \(T_s=1\,\mu s\)，PV converter 开关频率 20 kHz，RFB 与 SC converter 均为 10 kHz。[pdf:E13]（PDF 物理页 15，Appendix）

这不是 EMT 求解器或 FPGA 实现论文。论文没有报告节点导纳预 stamping、开关事件插值、数值积分格式、多速率调度、fixed-point 位宽、FPGA 资源、pipeline latency、worst-case execution time 或硬件 I/O 闭环；“RTS 可并行计算”只是平台描述，没有给出模型如何分区或实际核数/负载。[pdf:E12]（PDF 物理页 14，Section V）因此不能从 10 μs 实时步长外推出 FPGA 可实现性，也不能把 OPAL-RT 测试写成真实功率级 HIL。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学重点是控制结构推导，不是闭环鲁棒稳定性定理。先看储能接口：boost converter 与双向 dc-dc converter 都由电感电流微分方程描述，RFB 和 SC 的占空比变化 \(d_{bat},d_{sc}\) 是电流环控制输入；这给 TIDF 电流跟踪器提供了对象模型。[pdf:E03]（PDF 物理页 3，Eq. (1)–(2)）[pdf:E04]（PDF 物理页 4，Eq. (3)–(5)）

AWMOGI 的关键是从同一二阶分母生成两条响应：

\[
G_1(s)=\frac{u_1(s)}{V_g(s)}
=\frac{k\omega_o s+k\omega_o\mu}
{s^2+s(2\mu+k\omega_o)+(\omega_o^2+\mu^2+\mu k\omega_o)},
\]

\[
G_2(s)=\frac{u_2(s)}{V_g(s)}
=\frac{k\omega_o^2}
{s^2+s(2\mu+k\omega_o)+(\omega_o^2+\mu^2+\mu k\omega_o)} .
\]

其中 \(\omega_o=100\pi\ \mathrm{rad/s}\)，antiwindup loop gain \(\mu=10^{-2}\)。\(G_1\) 的 band-pass 特性配合负反馈去除 \(u_1\) 中的 dc offset；\(G_2\) 是 low-pass，dc offset 仍会进入 \(u_2\)，所以作者再引入第三支路 \(G_3\) 估计偏置。[pdf:E07]（PDF 物理页 8，Eq. (23)–(25)）稳态时

\[
u_{1\infty}=U_m\sin(\omega_st+\phi_s),\quad
u_{2\infty}=kU_{dc}-U_m\cos(\omega_st+\phi_s),\quad
u_{3\infty}=kU_{dc},
\]

于是 \(D_{\mathrm{AWMOGI}}=u_1\)，\(Q_{\mathrm{AWMOGI}}=u_2-u_3\)，也就是用相减消掉正交通道的 dc 项。[pdf:E07]（PDF 物理页 8，Eq. (26)–(30)）作者通过 pole-zero 分析在 \(k\in[0.1,2.5]\) 中取 \(k=1.2\)，意图在暂态速度与滤波能力之间折中。[pdf:E08]（PDF 物理页 9，Section III-D）

TIDF 是把 PID 的比例环节换成 \(s^{-1/n}\) 型 tilt 项，再保留积分与带滤波导数；\(n\) 理想范围为 1–3。[pdf:E08]（PDF 物理页 9，Section III-E）作者没有解析地证明整套多环闭环稳定，而是用 ISSA 最小化

\[
F(x_i)=\int_0^{T_s}
\left(e_{dc}^2+e_{b1}^2+e_{b2}^2+e_{sc1}^2+e_{sc2}^2+e_{d1}^2+e_{d2}^2\right)dt ,
\]

即把 dc-link、RFB 两向、SC 两向和 PV 电压/电流环的 ISE 合成一个目标。[pdf:E08]（PDF 物理页 9，Eq. (39)）ISSA 使用 50 个 agents、300 次迭代和 25 维搜索，论文称约 40 次迭代后目标达到最小并给出 Table II 的各环参数；但没有报告不同随机种子、参数敏感性或全局最优置信度。[pdf:E08]（PDF 物理页 9，Fig. 7、Table II）

## § 7 — 实验设计与结论

**问题 1：HESS 能否在功率盈余、平衡和不足时正确分工？** 作者在 MATLAB/Simulink 中设置 NPM、DPM、SPM。DPM 中，12 kW 负载先与 PV 匹配，2 s 时增加 2 kW，4 s 时辐照降到 400 W/m²，6 s 时负载降到 8 kW；SC 响应突变，RFB 慢慢增加放电并在 22 A 达限后由电网补足，dc-link 维持在参考附近。[pdf:E10]（PDF 物理页 11，Fig. 15 邻近正文）答案支持了“快慢分工可以工作”，但论文没有给出 RFB current stress 的量化指标，例如高频 RMS、峰值循环数或等效寿命改善。

**问题 2：控制在连续气象和负荷变化下是否仍工作？** 作者输入 NIT Silchar 一天的 irradiance/temperature profile 和印度家庭负荷曲线，每个小时数据映射为 2 s 仿真事件；在 RFB SOC 允许时由 HESS 补缺，达到 22 A 后电网加入。[pdf:E09]（PDF 物理页 10，Fig. 11）答案是 PV 量测被跟踪、dc-link 动态较小、grid voltage 维持；不过这是一条压缩时标的单日 profile，不是跨季节统计，也没有 PV 预测误差或储能退化。

**问题 3：电网幅值扰动下同步和电能质量怎样？** 仿真把 230 V 电网下降 12% 到 202.4 V，报告 \(I_g\) THD 为 2.42%；过压时升至 257.6 V，报告 THD 为 3.29%。[pdf:E11]（PDF 物理页 13，Section IV-C）RTS 欠压测试另报告 THD 2.1%，并声称满足 IEEE 519-2014。[pdf:E13]（PDF 物理页 15，Section V-B）这些结果只证明给定模型、负载与分析窗口中的 THD，不代表所有并网短路比、背景谐波或开关频率下都合规。

**问题 4：相对基线是否更快？** 作者在 L-G fault、3 kW pulse load 和 nonideal grid 条件下，把 dc-link 或 grid rms response 与 PI、TS-fuzzy 比较，并把 AWMOGI 基波幅值估计与 SOGI、MSOGI 比较；曲线显示所提控制恢复更快、偏差更小。[pdf:E10]（PDF 物理页 11，Fig. 14、Fig. 15）Table III 定性标记 AWMOGI 为 low computational burden、very fast dynamic response、good disturbance rejection 且可消除 dc offset。[pdf:E12]（PDF 物理页 14，Table III）然而论文没有给出统一数值表记录 settling time、overshoot、执行时间、内存或统计误差；Table III 的“low/very fast”不能当作资源测量。

**问题 5：实时执行是否复现离线结论？** plant 与 controller 在 OPAL-RT 4510 上以 10 μs 步长运行，测试 day-to-night、PVA-to-grid transition、欠压与 DPM。[pdf:E12]（PDF 物理页 14，Section V）DPM 的 RTS 波形再次显示 12→14 kW 负载、辐照降到 400 W/m² 和随后减载时 RFB/SC/grid 的接力。[pdf:E13]（PDF 物理页 15，Fig. 21、Section V-C）答案是数字实时仿真复现了预期趋势；但 plant 与 controller 同在同一 RTS 中，未报告 I/O delay、ADC/PWM、功率开关 dead time、通信 jitter 或实际储能内部动态，因此验证强度低于 controller-HIL 或 power-HIL。

## § 8 — Take-aways

**5 句话：**

1. 论文用 H₂/Br₂ RFB 加 SC，把 dc-link 功率缺口按 3.35 Hz 截止频率分成慢、快两部分。[pdf:E05]（PDF 物理页 5，Section III-B）
2. RFB 承担低频能量，SC 承担高频功率，电网在储能电流或 SOC 达限后补足剩余缺口。[pdf:E06]（PDF 物理页 6，Fig. 3）
3. AWMOGI 用额外支路消除正交通道中的 dc offset，再为单相并网电流构造基波单位模板。[pdf:E07]（PDF 物理页 8，Eq. (23)–(30)）
4. ISSA-TIDF 统一服务于 dc-link、PV MPPT、RFB 与 SC 电流环，但其参数优势主要由单次 ISE 优化和波形比较支撑。[pdf:E08]（PDF 物理页 9，Eq. (39)、Table II）
5. MATLAB 与 10 μs OPAL-RT 仿真覆盖多种扰动，却没有物理储能/变换器实验，也没有 FPGA、实时资源或严格稳定性证据。[pdf:E12]（PDF 物理页 14，Section V）

**3 句话：**

1. 这项工作的主要贡献是以 dc-link 为中心协调 HESS 时间尺度、并网同步和 PV 前馈，而非单独发明某个控制器。
2. 给定模型中，SC 接瞬态、RFB 接平均功率的机制在负载阶跃、辐照变化和 grid disturbance 下表现合理。
3. 最欠缺的是固定频率分配在储能饱和、延迟、参数偏差和长期脉冲下是否仍可行，以及这种可行性有没有真实硬件和定量 stress 指标支撑。

**1 句话：**

本文展示了一套在数字仿真中有效的 PV-RFB-SC 统一控制，但尚未把“波形恢复良好”提升为对储能寿命、实时计算与硬件扰动都可验证的韧性保证。

## § 9 — 最脆弱的假设

最脆弱的假设是：固定 3.35 Hz 的功率分割能够长期把所有“有害快分量”交给 SC，同时 SC 的能量、功率、电压和 converter headroom 足以完成该任务。作者自己承认 cutoff 越低，RFB 电流越平滑，但需要更大 SC 容量和更高 BDDC 器件功率；最终直接选定 3.35 Hz，并允许 SC 完全充放电。[pdf:E05]（PDF 物理页 5，Section III-B）Appendix 给出的 SC 为 80 F、240 V、5 串 1 并，RFB 为 5.28 kW、22 A 上限，但正文没有给出 SC 的最小/最大电压、SOC 安全边界、等效串联电阻、热限制或连续 pulse 能量预算。[pdf:E13]（PDF 物理页 15，Appendix）

若 pulse train 的频率正落在 cutoff 附近、持续时间足以耗尽 SC headroom，或 converter 因电流/温度饱和而不能跟踪 \(P_{\mathrm{hf}}\)，高频缺口会重新落到 RFB 或 dc-link；这样“减少 RFB 快速电流应力”和“快速 dc-link 恢复”会同时失效。论文提供了若干秒级阶跃、气象 profile 与 RTS 波形，但没有扫 pulse frequency/duty cycle，也没有对 SC 能量饱和或储能参数偏差做边界分析。[pdf:E10]（PDF 物理页 11，Fig. 15 邻近正文）这是基于证据的推断，不是论文显式结论。

## § 10 — 最小复现实验

一周内最值得复现的是 DPM 的“SC 吸收快分量、RFB 只接慢分量”核心 claim，而不是复制整套 ISSA。可以在 MATLAB/Simulink 建立降阶 dc-link、PV power source、RFB/SC 双向 converter 和同一 3.35 Hz LPF；采用 Appendix 的 400 V dc-link、80 F/240 V SC、5.28 kW RFB、22 A RFB 限流和 1 μs 仿真步长。[pdf:E13]（PDF 物理页 15，Appendix）

工况严格复用论文 DPM：0–2 s 为 12 kW 负载且与 PV 匹配，2 s 增加 2 kW，4 s 辐照从 1 sun 降到 400 W/m²，6 s 负载降到 8 kW。[pdf:E13]（PDF 物理页 15，Section V-C）实现三组对照：所提 HESS 分配、取消 SC 只用 RFB、电池与 SC 等比例分担但总功率能力相同。测量 \(V_{dc}\) 峰值偏差与恢复时间、RFB 电流的高通 RMS/最大斜率、SC 能量摆幅、RFB 22 A 饱和时长和 grid import。

若所提分配在不增加 dc-link 最大偏差的前提下，稳定降低 RFB 高频 RMS 和最大 \(di/dt\)，且 SC 不碰能量/电压边界，就支持核心 claim；若优势只来自额外储能功率容量，或 SC 饱和后 RFB stress 与无 SC 基线相同，就反驳其机制解释。为了可证伪，不需要先重跑 300 次 ISSA；可直接使用 Table II 的参数，并把控制器优化误差与储能分工误差分开。

## § 11 — 最强反例设计

最强反例不是再做一个更大负载阶跃，而是设计“频谱—能量双重攻击”。保持平均缺口和论文测试相同，输入一组频率从 0.5 Hz 扫到 10 Hz、duty cycle 逐渐增加的成组 pulse，并把中心频率密集放在 3.35 Hz 附近；同时让 SC 初始电压接近可用下界、RFB SOC 接近 10%，加入可实现的电流限制、converter delay 和传感噪声。这个设计直接攻击固定 LPF 分配与 SC headroom 的共同假设，而不是泛泛声称“极端工况会失败”。

比较对象必须保持总储能额定功率与可用能量相同：固定 3.35 Hz 分配、可变 cutoff 分配、以及基于实时 headroom 的约束分配。若固定分配在某个可重复的 pulse 频带使 SC 饱和，随后出现 dc-link 超限或 RFB 高频 RMS 急升，而 headroom-aware 基线不出现，就说明原论文的好波形来自所选工况与初始状态，而不是普遍有效的快慢解耦。论文没有进行这种 frequency/duty/SOC sweep；因此这是候选反例，不是已观察到的失败。

## § 12 — Follow-up Research Idea

在电力电子与微电网控制领域，高影响工作通常需要明确的稳定性或可行性边界、可复现实验、真实控制硬件/功率级验证，以及对效率、应力、热和计算时序的量化，而不只是在更多扰动波形上优于 PI。基于第 9 节，候选方向是把问题从“按固定频率切分功率”改写为“在储能能量、功率、温度、寿命损伤和实时计算约束下，在线分配可保证的 dc-link 调节能力”。

（a）未满足的需求是：pulse 的频谱会变化，SC headroom 也随历史能量交换变化，固定 cutoff 无法说明什么时候仍能保护 RFB。（b）研究价值在于给出一个可计算的 feasibility envelope：在何种 PV/load 扰动集合内，dc-link 误差和 RFB stress 有上界；超出时控制器应显式降级并向电网请求功率，而非事后饱和。（c）可借鉴 constrained MPC、tube-based robust control、control barrier function 与电池 rainflow/degradation surrogate，把“能量可行域”和“损伤预算”纳入同一分配器。（d）第一个证伪实验就是第 11 节的 pulse frequency/duty/SOC sweep：若新方法在相同总额定能力下不能扩大可行扰动集合，或计算时间无法稳定小于 10 μs，则想法失败。（e）它与本文的实质区别是研究对象从若干固定控制环的波形跟踪，转为带证书的储能可行性与损伤约束；AWMOGI/TIDF 可以保留也可以替换，不再是贡献中心。

由于本次严格只使用该源 PDF，未对 2022 年后的相关工作做外部检索；上述方向是证据约束下的候选研究想法，不声称 novelty。
