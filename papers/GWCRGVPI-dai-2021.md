# Simulation Credibility Assessment Methodology With FPGA-based Hardware-in-the-Loop Platform：中文精读

- 作者：Xunhua Dai；Chenxu Ke；Quan Quan；Kai-Yuan Cai
- 出处：IEEE Transactions on Industrial Electronics
- 年份：2021
- DOI：10.1109/TIE.2020.2982122
- Zotero key：GWCRGVPI

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“怎样让仿真跑得更快”，而是“怎样让电子控制系统的仿真结果足以被人信任”。复杂控制系统仅靠真实试验很难覆盖所有工况：试验昂贵、效率低，某些危险或法规受限的场景甚至无法反复执行；但仿真又常因平台与真实系统的硬件、软件运行环境不一致，以及缺少统一的定量评价方法而遭到质疑。作者因此把问题拆成两层：先用 FPGA-based HIL 让被测控制器在仿真与实物试验中尽量保持同一运行环境，再用实物与仿真的成对结果计算可比较的可信度指标。[pdf:E01](_evidence/E01-p001-abstract-core-claim.png)（PDF 物理页 1，Abstract）

其工程价值在于把“这条仿真曲线看起来像实测”变成一个可审查的验证流程。平台使用真实控制器，而 FPGA 生成传感器芯片及通信接口所需的信号；同一控制器因而能分别闭环于真实被控对象和仿真被控对象。随后，性能参数、时域响应和频域响应的误差都被映射到 0–1 区间，既可以逐项检查，也可以合成为全局指标。[pdf:E03](_evidence/E03-p002-contributions-and-normalized-framework.png)（PDF 物理页 2，Introduction，贡献列表）

这里的“可信度”应理解为**在给定测试、误差阈值和比较基准下，仿真结果与实物结果的一致程度**，而不是对模型在所有未来工况下都正确的证明。论文后文自己也承认，展示的测试数量有限，因此总指标未必足够全面或有代表性。[pdf:E15](_evidence/E15-p009-conclusion-and-scope-caveat.png)（PDF 物理页 9，Section IV-B.4 与 Conclusion）

## § 2 — 前人工作与不足

论文把既有方法的缺口归纳为“平台不可比”和“指标不可合成”两类。传统纯软件仿真让被控对象模型与控制算法运行在同一台计算机，而真实系统中的控制算法通常运行在专用硬件上；传统 HIL 虽然引入了真实控制器，但商业 CPU 实时机的模型更新频率通常低于 100 kHz，难以仿真需要纳秒级更新的高速 SPI 或高频模拟接口。作者据此主张，FPGA 的高并行 I/O 能力使传感器芯片和接口级行为进入 HIL 闭环，而不只是仿真低频被控对象。[pdf:E02](_evidence/E02-p002-prior-limits-and-hil-gap.png)（PDF 物理页 2，Introduction）

论文点名 AirSim 和 FlightGoggles 作为高保真 3-D 环境与 perception/learning 开发平台，但认为它们主要提高顶层视觉与物理环境的 fidelity，难以覆盖传感器、执行器等底层硬件故障。作者的改动是保留这类 3-D 引擎，同时让 FPGA 模拟控制器所见的传感器原始信号、通信接口、可编程特性、故障模式、老化特性和响应机制。[pdf:E04](_evidence/E04-p003-fig01-02-platform-and-comparison.png)（PDF 物理页 3，Section II-A，Fig. 1–2）

评价方法方面，论文称以往 HIL 工作常由工程师定性比较若干仿真/实测曲线；直接误差指标通常落在 \([0,+\infty)\)，不同物理量又有不同单位和量级，因此很难横向比较或合成。CIFER 的代价函数 \(J\) 也用固定比例因子合并幅值误差与相位误差，量级差异大时可能让其中一项被淹没。[pdf:E03](_evidence/E03-p002-contributions-and-normalized-framework.png)（PDF 物理页 2，Introduction）

以上均是**论文对相关工作的归纳**，本卡未独立核验这些相关文献。论文真正补上的，是一条从“同输入、同控制器的实物/仿真成对测试”到“统一尺度的多维评分”的完整链路；它并没有解决模型验证领域中所有的 coverage、uncertainty quantification 或 certification 问题。

## § 3 — 重建作者的思考路径

可以把作者的思考路径逆向重建为四步。

第一，既然控制器硬件、固件和通信栈本身会影响闭环结果，就不要用另一个软件控制器去代表它，而应让同一台真实控制器先连接真实对象，再连接 HIL 对象。这样，两个试验间最显眼的控制侧差异被消除，剩下的差异更集中地反映模型、传感器仿真和试验环境。[pdf:E04](_evidence/E04-p003-fig01-02-platform-and-comparison.png)（PDF 物理页 3，Fig. 1–2）

第二，若 HIL 只能提供低频状态量，真实控制器看到的接口时序、传感器噪声或故障行为仍不真实。因此用 FPGA 直接产生 SPI、PWM、CAN 等接口信号，并把真实控制器的原有传感器屏蔽，让控制器只能“看见”仿真传感器。

第三，单个误差值无法跨物理量比较，于是先为每一类误差指定可接受阈值 \(\varepsilon\)，再构造单调归一化函数，使 \(e=0\) 对应 1、\(e=\varepsilon\) 对应统一及格线 \(\eta_{\mathrm{pass}}\)、误差增大时评分趋近 0。[pdf:E05](_evidence/E05-p003-secII-C-eq01-02-normalization.png)（PDF 物理页 3，Section II-C，Eq. 1–2）

第四，可信度不是一条曲线的相似度。性能参数、时域轨迹、频域幅相各自揭示不同失真，所以分别评分后再聚合；同时保留最小项 \(\eta_{\min}\)，防止平均值完全掩盖最差测试。[pdf:E08](_evidence/E08-p005-eq11-16-frequency-and-overall.png)（PDF 物理页 5，Section III-C–D，Eq. 11–16）[pdf:E09](_evidence/E09-p006-fig05-eq17-hardware-platform.png)（PDF 物理页 6，Eq. 17）

这条路径的核心是工程可比性：先让实物与仿真的观察通道尽量一致，再谈误差的量化。归一化函数本身并不能创造可信度；它只把已经通过合理实验获得的误差，转成便于比较的分数。

## § 4 — 核心 Intuition

同一个真实控制器分别驱动真实对象和 FPGA-based HIL 对象，相同输入下的输出差异就能较少受控制器硬件与软件差异干扰。把每种误差除以一个具有工程意义的允许尺度，再映射到同一及格线，就能比较原本单位不同的性能、时域和频域结果。多维评分负责回答“平均有多像”，最小评分负责提醒“最差处是否仍可接受”。

## § 5 — 具体方法与完整 Pipeline

以 F450 四旋翼为例，完整 pipeline 如下。

1. **固定被测控制器。** 实物与 HIL 都使用同一套 Pixhawk autopilot。实物试验中，真实传感器把机体运动反馈给控制器；HIL 中，Pixhawk 的机载和外部传感器被屏蔽，传感器引脚改接 FPGA I/O。
2. **搭建实时闭环。** 实时计算机使用 NI PXIe-8133 CPU 模块和 PXIe-7846R FPGA I/O 模块；主机 GPU 负责 3-D 视觉环境。CPU 运行车辆模型，更新频率最高 5 kHz；FPGA 运行传感器模型并生成 SPI、PWM、CAN 等信号，更新频率最高 100 MHz。[pdf:E09](_evidence/E09-p006-fig05-eq17-hardware-platform.png)（PDF 物理页 6，Fig. 5 与 Section IV-A.1）
3. **建立实物比较基准。** 试验对象是对角尺寸 450 mm、质量 1.4 kg、DJI E310 propulsion、LiPo 3S 4000 mAh 电池的 F450。姿态动力学使用穿过质心的单轴低摩擦台架做 sweep-frequency 识别；推进系统另设测量装置。MATLAB/Simulink 中的 F450 模型通过代码生成导入 HIL。[pdf:E10](_evidence/E10-p006-fig06-experimental-setup.png)（PDF 物理页 6，Fig. 6 与 Section IV-A.2）
4. **实施成对激励。** 给真实系统和 HIL 系统施加相同或等价的测试输入，分别收集性能参数、时域曲线和频域响应。传感器噪声试验使用 MPU6000 实测数据，并将电机转速从 0% 阶跃到 50% 来制造振动段。[pdf:E11](_evidence/E11-p007-fig09-sensor-test-procedure.png)（PDF 物理页 7，Fig. 9 与 Section IV-B.1）
5. **按测试类型计算误差。** 标量性能用绝对差；轨迹用采样点 root-mean-square error；频域用 coherence 权重下的 Bode 幅值和相位误差。随机噪声曲线不直接套时域轨迹指标，而改用标准差等统计性能量。
6. **用阈值归一化。** 每类误差 \(e\) 配一个允许阈值 \(\varepsilon\)，经 \(f_{\mathrm{norm}}\) 变成 \((0,1]\) 上的可信度 \(\eta\)，并把及格线统一设为 0.6。
7. **聚合并保留最差项。** 性能、时域、频域分别先聚合，再按权重得到 \(\eta_{\mathrm{all}}\)；另计算所有测试中的最小可信度 \(\eta_{\min}\)。

需要避免一个误读：论文没有提出 EMT 网络离散、开关事件处理或多速率电磁暂态求解器。它报告的是车辆模型与传感器接口的 HIL 架构；没有报告 FPGA 逻辑资源、定点位宽、pipeline latency、时序收敛、RTL 结构或求解器并行分解。因此不能把 5 kHz/100 MHz 外推成某种通用 EMT 实时求解性能。

## § 6 — 核心数学推导

论文的数学核心是一种“误差相对于允许误差的软评分”。对任意非负误差 \(e\) 和正阈值 \(\varepsilon\)，定义

\[
\eta=f_{\mathrm{norm}}(e,\varepsilon)
=\frac{K_e\varepsilon}{\sqrt{(K_e\varepsilon)^2+e^2}},
\qquad
K_e=\frac{\eta_{\mathrm{pass}}}{\sqrt{1-\eta_{\mathrm{pass}}^2}}.
\]

当 \(e=0\) 时 \(\eta=1\)；当 \(e=\varepsilon\) 时 \(\eta=\eta_{\mathrm{pass}}\)；当误差无限增大时 \(\eta\) 趋近 0。论文取 \(\eta_{\mathrm{pass}}=0.6\)，对应 \(K_e=0.75\)。物理上，\(\varepsilon\) 才是“允许多大误差”的工程尺度，公式只是把误差相对该尺度的大小平滑地编码成分数。[pdf:E05](_evidence/E05-p003-secII-C-eq01-02-normalization.png)（PDF 物理页 3，Section II-C，Eq. 1–2）[pdf:E06](_evidence/E06-p004-eq03-07-performance-time-errors.png)（PDF 物理页 4，Fig. 3 后的归一化解释）

**性能量。** 实测性能参数为 \(p_e\)，仿真参数为 \(p_s\)，则

\[
e_p=|p_e-p_s|,\qquad
\varepsilon_p=K_p|p_e|,\qquad
\eta_p=f_{\mathrm{norm}}(e_p,\varepsilon_p).
\]

论文把 \(K_p=5\%\) 作为一般高精度场景的示例，但明确允许依据噪声和测量误差调整；当 \(p_e=0\) 时，\(\varepsilon_p=K_p|p_e|\) 失效，必须另定阈值，例如以 \(|p_s|\) 为尺度。[pdf:E06](_evidence/E06-p004-eq03-07-performance-time-errors.png)（PDF 物理页 4，Eq. 3–5）

**时域量。** 对实测曲线 \(y_e(t_i)\) 与仿真曲线 \(y_s(t_i)\)，论文用

\[
e_t=\sqrt{\frac{1}{n_t}\sum_{i=1}^{n_t}\left(y_e(t_i)-y_s(t_i)\right)^2},
\qquad
\varepsilon_t=K_p\max_{i,j}|y_e(t_i)-y_e(t_j)|,
\qquad
\eta_t=f_{\mathrm{norm}}(e_t,\varepsilon_t).
\]

这里 \(t\) 不一定是时间，也可以是轨迹位置或 throttle-speed 等曲线的自变量。作者提醒，噪声影响下应先平滑，随机噪声/振动本身不适合用该时域指标，而应比较均值、方差或标准差等统计量。[pdf:E06](_evidence/E06-p004-eq03-07-performance-time-errors.png)（PDF 物理页 4，Eq. 6–7）[pdf:E07](_evidence/E07-p005-eq08-10-time-and-frequency-errors.png)（PDF 物理页 5，Eq. 8 及适用范围）

**频域量。** 在 \([f_a,f_b]\) 的采样频率上，实验 Bode 幅值/相位为 \(M_e,P_e\)，仿真为 \(M_s,P_s\)。论文分别计算 coherence 权重 \(W_\gamma(f_i)\) 下的 root-mean-square 幅值误差 \(e_{\mathrm{mag}}\) 与相位误差 \(e_{\mathrm{pha}}\)；精度要求不高时可取 \(W_\gamma\equiv1\)。两个阈值都取实验曲线全范围乘以 \(K_p\)，得到 \(\eta_{\mathrm{mag}}\) 和 \(\eta_{\mathrm{pha}}\)，再合成

\[
\eta_f=\sqrt{\frac{\eta_{\mathrm{mag}}^2+\eta_{\mathrm{pha}}^2}{2}}.
\]

[pdf:E07](_evidence/E07-p005-eq08-10-time-and-frequency-errors.png)（PDF 物理页 5，Eq. 9–10）[pdf:E08](_evidence/E08-p005-eq11-16-frequency-and-overall.png)（PDF 物理页 5，Eq. 11–14）

**系统级聚合。** 每一类先对其若干 \(\eta\) 做均方根聚合得到 \(\bar\eta_p,\bar\eta_t,\bar\eta_f\)，然后

\[
\eta_{\mathrm{all}}
=\sqrt{\alpha_p\bar\eta_p^2+\alpha_t\bar\eta_t^2+\alpha_f\bar\eta_f^2},
\quad
\alpha_p+\alpha_t+\alpha_f=1.
\]

示例权重为 \(\{0.3,0.3,0.4\}\)。由于均方根会让高分项对结果贡献更大，论文另取

\[
\eta_{\min}=\min\{\eta_{p,i},\eta_{t,j},\eta_{f,k}\}
\]

检查最差测试，并以 90% 作为“高可信模型”的示例门槛。[pdf:E08](_evidence/E08-p005-eq11-16-frequency-and-overall.png)（PDF 物理页 5，Eq. 15–16 与权重）[pdf:E09](_evidence/E09-p006-fig05-eq17-hardware-platform.png)（PDF 物理页 6，Eq. 17）

推导中没有从概率模型推出 0.6、5%、10%、90% 或 \(\{0.3,0.3,0.4\}\) 的唯一合理性。这些量是规则和工程选择，而不是定理；因此分数的可解释性依赖阈值与权重是否由外部标准、测量不确定度或风险要求正当化。

## § 7 — 实验设计与结论

**问题一：FPGA 传感器模型能否复现真实传感器的噪声和振动统计？**  
实验把 MPU6000 的 accelerometer、gyroscope 实测信号与 HIL 传感器模型比较，电机指令从 0% 变到 50%，并把数据分为四段。由于波形随机，作者比较标准差而不是逐点时域误差；测试中把阈值取为约 \(10\%|p_e|\)。Table I 的四个可信度为 91.3%、97.4%、90.6%、96.6%，聚合后的性能可信度为 94%。[pdf:E11](_evidence/E11-p007-fig09-sensor-test-procedure.png)（PDF 物理页 7，Fig. 9 与 Section IV-B.1）[pdf:E12](_evidence/E12-p008-tableI-fig10-frequency-test.png)（PDF 物理页 8，Table I）

**问题二：姿态动力学模型的频率响应是否接近实物？**  
实验对 pitch channel 做 sweep-frequency，关注区间为 \([0.25,40]\ \mathrm{rad/s}\)，并用 CIFER 得到 Bode magnitude、phase 和 coherence。报告结果是 \(\eta_{\mathrm{mag}}=97.3\%\)、\(\eta_{\mathrm{pha}}=97.6\%\)、\(\eta_f=97.63\%\)；作为对照，CIFER 代价函数为 \(J=4.359\)。作者据此认为该 pitch 模型相对真实四旋翼具有高频域可信度，但这只验证了该通道和该频带。[pdf:E12](_evidence/E12-p008-tableI-fig10-frequency-test.png)（PDF 物理页 8，Fig. 10 与 Section IV-B.2）

**问题三：指标能否区分不同建模精度，而不只判断“像不像”？**  
实验让四旋翼从 hover 进入 level flight，比较真实飞行、高精度 HIL、低精度 HIL、误差边界和 zero-output 五条曲线。高精度模型的 \(\eta_t=94.4\%\)，低精度模型为 73.8%，误差边界恰为 60.0%，zero-output 为 1.75%；这组人工层级说明公式能按预期排序，并能把阈值映射到及格线。[pdf:E13](_evidence/E13-p008-fig11-frequency-and-time-results.png)（PDF 物理页 8，Fig. 11 与 Section IV-B.3）[pdf:E14](_evidence/E14-p009-tableII-overall-results.png)（PDF 物理页 9，Table II）

**问题四：多类指标能否合成为整个平台的摘要？**  
作者把 \(\bar\eta_p=94.0\%\)、\(\bar\eta_t=94.4\%\)、\(\bar\eta_f=97.63\%\) 按 \(\{0.3,0.3,0.4\}\) 加权，得到 \(\eta_{\mathrm{all}}=95.36\%\)，并报告 \(\eta_{\min}=90.6\%\)。作者随即限定结论：由于这里只展示了少量测试，\(\eta_{\mathrm{all}}\) 和 \(\eta_{\min}\) 可能不够全面或有代表性；只有增加不同角度的测试，指标才更可能代表整个 HIL 系统。[pdf:E14](_evidence/E14-p009-tableII-overall-results.png)（PDF 物理页 9，Section IV-B.4）

因此，实验充分支持“该评分在所选四旋翼测试上可计算、可排序、可合成”，也支持“这套 FPGA-based HIL 能运行这些成对试验”。它没有充分支持“95.36% 是跨工况、跨车辆或认证意义上的真实成功概率”，更没有给出与独立认证标准之间的对应关系。

## § 8 — Take-aways

**5 句话：**

1. 可信仿真的第一步不是设计一个漂亮分数，而是让实物试验与 HIL 试验共享同一真实控制器和尽可能一致的接口边界。
2. FPGA 在本文中的作用是高速生成传感器芯片与通信接口行为，而不是加速 EMT 数值求解。
3. 归一化函数把“误差是否超过允许阈值”变成统一的 0–1 分数，从而让不同物理量可以比较。
4. 性能、时域和频域指标回答不同问题，\(\eta_{\mathrm{all}}\) 与 \(\eta_{\min}\) 分别承担平均摘要和最差项检查。
5. 分数的可信性最终取决于阈值、权重、测试覆盖和实物基准，而这些正是论文验证仍不足的地方。

**3 句话：** 同控制器的成对 HIL/实物试验降低了控制侧差异，使误差更能指向模型与接口。统一尺度让异构误差可以组合，但阈值和权重仍是外部工程判断。四旋翼结果证明方法可用，不证明它天然具有认证效力。

**1 句话：** 这篇论文最重要的贡献，是把 FPGA 接口级 HIL 的“可比实验条件”与阈值归一化的“可合成评分”连成一条流程。

## § 9 — 最脆弱的假设

最脆弱的假设是：**有限的一组成对测试、阈值和权重足以代表安全相关的仿真用途。** 只要该假设不成立，\(\eta_{\mathrm{all}}\) 即使很高，也不能支持“仿真结果可替代实物试验”的核心工程期待。

该假设可能因三类原因失败。第一，测试输入没有覆盖稀有故障、饱和、通信抖动、传感器延迟或环境边界；模型在正常 sweep 和 level-flight 上很像实物，却可能在安全关键瞬态中失败。第二，\(\varepsilon\) 与 \(K_p\) 决定了及格线代表的实际误差，若只按经验或当前数据幅值选择，0.6 在不同系统之间并不具有同一风险含义。第三，权重会把认证关注点编码进总分；若权重与实际 hazard 不一致，95% 只是算术结果，不是风险结论。

论文给出的正面证据是：Table II 的高精度、低精度、边界和 zero-output 按预期得到 94.4%、73.8%、60.0% 和 1.75%，说明指标对这些构造的质量层级有辨别力。[pdf:E14](_evidence/E14-p009-tableII-overall-results.png)（PDF 物理页 9，Table II）缺失的证据则是跨工况复测、阈值来源审计、测量不确定度传播、rare-event coverage 和对外部 certification criterion 的校准。作者关于“测试数量有限”的声明，实际上承认了这一缺口。[pdf:E15](_evidence/E15-p009-conclusion-and-scope-caveat.png)（PDF 物理页 9，Section IV-B.4）

这是**基于证据的批评**，不是作者明确声称其方法已获得认证。

## § 10 — 最小复现实验

一周内最值得复现的不是整套 FPGA 平台，而是“归一化评分是否稳定地区分模型质量”。

1. 准备同一控制器在一条实测 pitch-step 或单轴台架轨迹上的参考数据，并准备一个 nominal 仿真模型。
2. 从 nominal 模型派生三组受控退化：参数小偏差、明显偏差、zero-output。所有模型使用同一时间窗口和采样点。
3. 在看仿真结果前，用测量重复性或明确工程容差固定 \(\varepsilon_t\)，禁止为了得到理想分数事后调阈值。
4. 按 Eq. 6–8 计算各模型 \(\eta_t\)，并做 bootstrap 或重复试验，检查排序和分数方差。
5. 支持 claim 的结果是：不同重复试验中，nominal 始终高于小偏差、小偏差高于明显偏差，误差恰等于阈值的构造稳定映射到 0.6，zero-output 接近 0；若排序随噪声或窗口选择频繁翻转，或轻微改变 \(\varepsilon_t\) 就使合格/不合格反转，则反驳“该指标可作为稳定可信度尺度”的主张。

这个复现只验证 scoring mechanism，不验证 100 MHz 传感器接口、整个平台 fidelity 或跨车辆泛化。它的优势是能把“分数公式的问题”和“FPGA 实现的问题”分开。

## § 11 — 最强反例设计

最强反例是构造一个**全局曲线相似、局部安全行为错误**的场景。选取同一 Pixhawk 和同一四旋翼模型，让 HIL 在绝大多数时段准确复现实物，但在一个短暂且安全关键的传感器接口事件中引入 5–20 ms 的延迟、packet drop、饱和恢复错误或时间戳乱序；真实系统则保留正确接口行为。然后仍按论文的性能、全窗口时域 RMSE 和有限频带 Bode 指标评分。

如果短事件只占很少样本，全窗口 RMSE 可能仍小，稳态性能和扫频结果也可能很高，于是 \(\eta_{\mathrm{all}}\) 与测试级 \(\eta_{\min}\) 都通过；但真实控制器可能触发错误 mode switch、积分 windup 或短暂失稳。这会给出一个具体的替代解释：高分反映的是“多数样本相似”，而非“安全相关接口语义可信”。反例成立的判据是，论文式指标仍判定通过，而事件级安全指标或闭环约束明确失败。

该攻击直接针对方法的代表性假设，而不是泛泛地说“还需更多实验”。它也利用了论文架构的关键事实：FPGA 恰好负责传感器和通信接口，因此接口时序错误是平台可信度必须覆盖、却不能被普通轨迹均值自动保证的对象。

## § 12 — Follow-up Research Idea

**候选方向：从“平均相似度可信度”改为“用途与 hazard 条件化的可信度证据”。** 这里不声称 novelty，因为本卡没有充分检索 simulation V&V、runtime assurance、formal falsification、rare-event testing 和 uncertainty quantification 的相关工作。

驱动需求是：认证或安全决策并不关心一个脱离用途的总分，而关心模型在指定 operational design domain、指定 hazard 和指定控制器决策上的误导概率。可以把测试输入分成正常性能、边界工况、故障注入和接口时序四类；每类先定义必须满足的安全约束与测量不确定度，再报告分层可信度、置信区间、coverage 和最坏 violation，而不是只给 \(\eta_{\mathrm{all}}\)。

它可能产生本领域认可的价值，是因为它把 FPGA-based HIL 的高速故障/接口注入能力与模型 V&V 的证据结构真正连接起来：FPGA 不只是复现传感器，还能主动搜索导致控制器决策分歧的时序与故障边界。可借鉴的相邻工具包括 control-system falsification、robustness metric、importance sampling、conformal risk control，以及基于 hazard analysis 的 test generation。

第一个可证伪实验是：在同一控制器上系统扫描传感器延迟、丢包、饱和和噪声组合，对比论文的 \(\eta_{\mathrm{all}}\) 与新的 hazard-conditioned 指标预测闭环失败的能力。如果新指标不能比原总分更早、更稳定地识别失败边界，或其置信区间在可接受试验量下仍不可用，这个方向就不成立。

它与本文的实质区别不在于“再增加一个指标”，而在于改变评价对象：本文评估的是有限测试中仿真曲线与实测曲线的归一化相似度；候选方向评估的是在明确用途和风险条件下，HIL 模型是否会误导控制器或安全决策。
