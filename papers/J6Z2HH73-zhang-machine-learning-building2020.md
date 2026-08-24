# Machine Learning Building Blocks for Real-Time Emulation of Advanced Transport Power Systems

- 作者：Songyang Zhang；Tian Liang；Venkata Dinavahi
- 出处：IEEE Open Journal of Power Electronics
- 年份：2020
- DOI：10.1109/OJPEL.2020.3039117
- Zotero key：J6Z2HH73

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的是一个很具体的工程矛盾：先进交通电力系统，例如 more electric aircraft（MEA），不断加入高频功率电子设备，HIL emulation 又要求每一个固定步长内都算完，但传统 electromagnetic transient（EMT）方法需要随网络规模处理越来越大的节点方程，系统越集成，单步求解延迟越难压缩。作者因此提出 machine learning building blocks（MLBBs）：不在在线执行时使用传统 circuit-oriented transient solver，而是把各设备的输入-输出瞬态关系训练成神经网络模块，再映射到 FPGA 并行执行。[pdf:E01] [pdf:E02]

这个问题重要，不只是因为“AI 能提速”。HIL 的物理用途是让真实控制器在安全、可重复的虚拟电气环境中经历快速动态；若仿真步长赶不上设备开关和控制周期，接口虽然叫“实时”，反馈给控制器的却已经是过期状态。论文选择类似 Boeing 787 的 MEA microgrid 作为案例，系统包含同步发电机、3 个 auto-transformer rectifier units（ATRU）、2 套 PMSM drive 和 energy storage system（ESS），正好把多设备、多时间尺度和功率电子非线性集中到一个系统中。[pdf:E03] [pdf:E04]

论文明确声称，其方法在 FPGA 上同时覆盖 component-level、device-level 和 system-level 模型，并分别以 PSCAD/EMTDC 和 SaberRD 的离线结果作系统级、器件级参照。[pdf:E01] 这里的价值在于：若 learned model 真能保持闭环动态和端口行为，而在线执行只剩固定结构的乘加、activation 与状态更新，就可以避开每步的大型网络矩阵求解，并利用 FPGA 的空间并行性。[pdf:E02] [pdf:E10] 这是作者的技术主张；它并不自动等同于已经证明了所有未见工况下的 HIL 可信度。

## § 2 — 前人工作与不足

论文面对的直接前身是 Dommel 型离散 EMT：电感、电容等元件先离散成“当前等效导纳加历史源”，再由整个网络的节点方程得到本步解。论文用电感的 trapezoidal 离散式展示了这种 history term 如何形成，也引用 Dommel 1969 作为传统数字 EMT 基础。[pdf:E03] [pdf:E11] 这种方法的优势是方程来源和网络耦合都清楚；不足是在线计算仍受网络规模、非线性迭代和节点求解牵制，作者把这视为高密度交通电力系统 HIL 的主要瓶颈。[pdf:E02]

机器学习侧的已有工具并不新：论文列出 ANN、classical RNN（CRNN）、LSTM 和 GRU，指出 RNN 能使用历史状态处理 time-series；LSTM/GRU 有长序列能力，但结构和执行代价更高。[pdf:E02] [pdf:E03] 论文还引用了 RNN complexity、LSTM、GRU、Adam，以及一个面向 MEA 大规模电路实时仿真的 hierarchical zonal method。[pdf:E11] 因而这篇工作的关键不应被概括成“首次用神经网络”或“首次用 FPGA”。更准确地说，作者试图把这些已有构件重新组织成一个面向电力电子实时 emulation 的分层、混合、可并行 building-block 方法。

论文自己揭示了纯黑箱方案为什么不够。单个 PMSM CRNN 在给定正确输入时可以拟合波形，但小步长下 \(y(t)\) 与 \(y(t-1)\) 的差可能小于 \(0.1\%y\)，网络容易把上一时刻值当作当前值；接入闭环后，小输入误差会积累，模型可能失稳。[pdf:E05] 更严重的是，把电流、转矩、转速和转角一起塞入单一相关性模型，会同时学到正反馈式的 internal interlock 和“结果反推原因”的 anti-causal mapping；作者直言神经网络学的是 correlation 而不是 causation。[pdf:E05] [pdf:E06]

需要保留一个证据边界：论文没有给出一套系统的 prior-work benchmark，也没有把 MLBB 与 hierarchical EMT、model-order reduction 或其他 learned simulator 在同一硬件、同一误差指标下比较。它主要比较自己的 FPGA 输出与 PSCAD/EMTDC、SaberRD 参考波形。[pdf:E09] [pdf:E10] 因此，本卡不据此声称 MLBB 的 novelty 已被充分排他性检索证明。

## § 3 — 重建作者的思考路径

可以从论文出现前已经成立的四个线索重建这条路径。第一，传统 EMT 的物理离散可以被写成“当前输入加历史状态”的递推；例如电感的本步电流由上一时刻的 history term 和本步端电压决定。[pdf:E03] 第二，RNN 正好是携带 hidden state 的递推计算图，且 FPGA 适合并行执行其固定乘加结构。[pdf:E02] 因此，先把局部元件递推写成 RNN，并让已知参数直接成为 weight，而不是先把整个电网当成一个黑箱，是自然的第一步。[pdf:E03] [pdf:E04]

第三，设备的物理时间尺度不同。system-level 模型关心端口和控制周期内的动态，可以使用 \(1\,\mu s\) 步长；SiC IGBT switching transient 则需要 \(50\,ns\) 间隔和更细的电压、电流训练数据。[pdf:E04] 这提示模型不应采用同一粒度：慢速 steady-state 路径可由 RNN 递推，快速 switching interval 可由 ANN 专门处理，再在 hybrid model 中切换或组合。[pdf:E04] [pdf:E05]

第四，单一 PMSM 黑箱虽能做 one-step prediction，却破坏了物理因果顺序。电压和电流决定 electromagnetic torque，torque 再驱动机械速度与转角；若模型允许速度和转角“预测”同一时刻 torque，就会把相关性当成逆因果。[pdf:E05] [pdf:E06] 从这个失败模式出发，作者把 PMSM 拆成 current、torque、speed 三个 CRNN unit，使每个 learned block 只承担一段与传统方程相同方向的映射，再与坐标变换和控制器连接。[pdf:E04] [pdf:E06]

由此得到的思想路线不是“让一个更大的网络学会一切”，而是“用电气知识决定边界、因果方向和时间尺度，再让小网络替代边界内难以实时计算或难以取得参数的关系”。这是对作者方法结构的基于证据的重建，不是作者逐字陈述的设计历史。

## § 4 — 核心 Intuition

MLBB 的核心 intuition 是：把复杂交通电力系统拆成具有明确端口、状态方向和时间尺度的局部 learned operator，让每个 operator 像传统元件方程一样被连接，而不是训练一个从全系统历史到全系统未来的单体黑箱。[pdf:E04] 物理分解负责阻止错误的 feedback 和 anti-causal shortcut，神经网络负责逼近局部非线性，FPGA 则让这些固定计算图并行运行。[pdf:E05] [pdf:E06] 对 switching transient 与 steady state 使用不同 block 和不同步长，才能把 \(50\,ns\) 的局部细节与 \(1\,\mu s\) 的系统推进同时放进有限硬件资源。[pdf:E04]

## § 5 — 具体方法与完整 Pipeline

以论文的 MEA case study 为例，完整 pipeline 如下。

1. **定义系统与数据真值。** 作者在 PSCAD/EMTDC 中建立包含 synchronous generator、3 个 ATRU、2 套 PMSM drive 和 ESS 的完整 MEA，用于 system-level training data；ESS 中的 SiC IGBT 细节另在 SaberRD 建模，用于 device-level data。[pdf:E03] 这意味着模型的监督目标是离线仿真器输出，而不是直接测得的飞行器实物数据。

2. **按物理粒度划分 MLBB。** component-level 先处理 inductor 和 capacitor。以电感为例，trapezoidal 离散产生本步端电压、上一时刻电流和 history state 的递推，已知 \(L\) 时可直接把系数写进 CRNN 的 weight 和 bias，不需要训练。[pdf:E03] [pdf:E04] system-level block 用较少 hidden size/layer 表示 converter、rectifier、transformer、generator、PMSM 等设备的外部端口动态，论文采用 \(1\,\mu s\) interval。[pdf:E04]

3. **为快速器件建立 hybrid model。** SiC IGBT block 由两部分组成：接受 5 个输入信号的 device-level ANN 负责 switching transient；接受 3 个 time-series 输入的 system-level RNN 负责 steady state。这样不必让一个长序列大网络同时覆盖相差悬殊的两种动态。[pdf:E04] [pdf:E05] device-level interval 为 \(50\,ns\)，训练集必须包含 turn-on/turn-off 的完整电压、电流过程。[pdf:E04]

4. **沿因果链拆分 PMSM。** 单体 PMSM CRNN 被替换为 current unit、torque unit 和 speed unit：电压、频率等先得到 \(d/q\)-axis current，电流再得到 electromagnetic torque，torque 与 mechanical load 再推进 rotor speed 和 angle；坐标变换、PI 和 SPWM/control signals 保留在连接图中。[pdf:E04] [pdf:E05] 作者的理由不是网络容量不足，而是单体网络容易形成 internal interlock 和 anti-causal shortcut。[pdf:E05] [pdf:E06]

5. **准备和训练数据。** dataset 覆盖多种 operating conditions；作者称无需从原始波形密集连续采样，可以用较大间隔抽样，并将数据用 min-max 或 z-score 归一化到 \((-1,1)\)。[pdf:E06] 默认 network layer size 为 1，经验设置是 hidden size 约为 input size 的 4 倍、sequence length 为 3；在短序列下，CRNN 的 MAE 接近 GRU/LSTM，但计算负担较小，因此成为主要选择。[pdf:E06] 训练使用 MAE、Adam、data shuffling 和 varying learning rate。[pdf:E06] 论文报告训练集群有 196 个 node，最多同时使用 8 个；一个模型在 PC 上需 12-24 h，而单个 cluster node 上需 6-12 h。[pdf:E07]

6. **筛选后部署。** 作者先用不同于 training dataset 的 test dataset 计算 MAE，再把模型放回传统仿真系统跑多种 evaluation condition；通过后才 block-by-block 搭到 FPGA。[pdf:E07] 模型用 C 在 Xilinx HLS 重建为 IP core，进入 Vivado 生成 bitstream，部署到带 XCVU37P 的 Xilinx VCU128；板上时钟为 \(100\,MHz\)。[pdf:E07]

7. **实时运行与观测。** 各 block 在 FPGA 上并行执行，system-level 以 \(1\,\mu s\) 推进，device-level 以 \(50\,ns\) 表示局部 switching transient；输出经 DAC/oscilloscope 观测，并与 PSCAD/EMTDC 或 SaberRD 的同工况波形并列比较。[pdf:E07] [pdf:E08] [pdf:E09]

## § 6 — 核心数学推导

先看物理意义。论文不是凭空把电感替换成 RNN，而是把传统离散方程中的“history source”直接解释成 recurrent hidden state。连续电感关系为

\[
v_m-v_n=L\frac{di_{mn}}{dt},
\]

采用 trapezoidal discretization 后，本步与上一步的端电压共同决定电流增量。作者定义

\[
hist_{mn}(t-\Delta t)=i_{mn}(t-\Delta t)+\frac{\Delta t}{2L}
\{v_m(t-\Delta t)-v_n(t-\Delta t)\},
\]

于是

\[
i_{mn}(t)=hist_{mn}(t-\Delta t)+\frac{\Delta t}{2L}
\{v_m(t)-v_n(t)\},
\]

\[
hist_{mn}(t)=hist_{mn}(t-\Delta t)+\frac{\Delta t}{L}
\{v_m(t)-v_n(t)\}.
\]

这些是 PDF 物理页 3 的 Eq. (5)-(9)。其中 \(v_m,v_n\) 是电感两端节点电压，\(i_{mn}\) 是支路电流，\(L\) 是电感，\(\Delta t\) 是步长；\(\Delta t/(2L)\)、\(\Delta t/L\) 与常数 1 可以直接成为 Fig. 3(b) CRNN 边上的 weight。[pdf:E03] [pdf:E04] 因而 component-level MLBB 在这里本质上是“把已知数值积分器画成 recurrent graph”，不是数据拟合。

神经网络类型的执行代价则由 input size \(i\)、hidden size \(h\)、output size \(o\) 和 activation latency 决定。论文给出的主导项为

\[
T_{ANN}\approx 2ih^2+2oh^2+oT_{\tanh},
\]

\[
T_{CRNN}\approx 2ih^2+2h^3+hT_{\tanh},
\]

\[
T_{LSTM}\approx 8ih^2+14h^3+2hT_{\tanh}+3hT_{\mathrm{sigm}},
\]

\[
T_{GRU}\approx 6ih^2+14h^3+hT_{\tanh}+2hT_{\mathrm{sigm}}.
\]

这些是 PDF 物理页 3 的 Eq. (1)-(4)。它们解释了作者为何在 sequence length 较短时选择 CRNN：LSTM/GRU 的额外 gates 带来更多 \(h^3\) 级矩阵乘加和 activation，而这里并不需要很长的记忆跨度。[pdf:E03] [pdf:E06]

PMSM 的数学作用不是求出一组新的 motor equation，而是确定 learned blocks 的因果边界。论文先列出 \(d/q\) 电压、磁链关系，再把 current block 写成

\[
\{i_q,i_d\}=f(v_q,v_d,\omega_e),
\]

其中 \(v_d,v_q\) 是 \(d/q\)-axis voltage，\(i_d,i_q\) 是对应 current，\(\omega_e\) 是 electrical supply frequency；\(L_d,L_q,R,\lambda_{pm}\) 分别代表轴电感、定子电阻和 permanent-magnet flux linkage。[pdf:E05] 随后 torque block 遵循 PDF Eq. (15)

\[
T_e=\frac{3p}{2}\left[\lambda_{pm}i_q+(L_d-L_q)i_di_q\right],
\]

mechanical block 遵循 Eq. (16)-(17)

\[
J\frac{d\omega_r}{dt}=T_e-T_m-B\omega_r,\qquad
\frac{d\theta_m}{dt}=\omega_r.
\]

这里 \(T_e,T_m,J,B,\omega_r,\theta_m\) 分别是 electromagnetic torque、mechanical torque、moment of inertia、friction factor、rotor speed 和 rotor position angle。[pdf:E05] 分块之后，信息沿“electrical input \(\rightarrow\) current \(\rightarrow\) torque \(\rightarrow\) mechanical state”传播，避免把 \(\omega_r,\theta_m\) 当成同一时刻 \(T_e\) 的反向原因。[pdf:E06]

训练指标为 mean absolute error：

\[
MAE=\frac{1}{n}\sum_{i=1}^{n}|y_i^{pre}-y_i|,
\]

其中 \(y^{pre}\) 是 network prediction，\(y\) 是 expected output，\(n\) 是输出样本数；作者用 Adam 最小化该指标。[pdf:E06] 需要注意，MAE 是点值拟合指标，并不直接度量 closed-loop stability、能量守恒或长期误差积累。

## § 7 — 实验设计与结论

**问题 1：哪种 RNN 和参数组合在精度与执行代价之间更合适？** 作者固定 1 layer，扫描 hidden-size coefficient 与 sequence length，并比较 CRNN、GRU、LSTM 的 MAE。结果显示 LSTM 最低、GRU 接近 LSTM，CRNN 在短 sequence 下相近且负担更小；论文据此采用 hidden size 约为 input size 的 4 倍、sequence length 为 3 的通用起点。[pdf:E06] [pdf:E07] 作者还报告所有 CRNN 在 100 epochs 后都达到 \(1\%\) 以内的 MAE，并用不同于 training data 的 test data 计算曲线。[pdf:E07] 这支持“可以训练到较低 supervised error”，但没有单独证明闭环长期稳定。

**问题 2：分块 PMSM 在负载和速度变化下能否跟随传统模型？** 实验在 \(1,2,3,4,5\,s\) 依次施加工况变化：mechanical torque 在 \(1\,s\) 变为 \(0\) p.u.、\(2\,s\) 变为 \(0.8\) p.u.、\(3\,s\) 变为 \(0.5\) p.u.；speed reference 在 \(4\,s\) 从 \(0.5\) p.u. 升至 \(0.7\) p.u.，在 \(5\,s\) 降至 \(0.3\) p.u.。[pdf:E09] Fig. 10 把实时 oscilloscope 输出置于上方，把 PSCAD/EMTDC 或 SaberRD 结果置于下方，覆盖 rotor angle、\(d/q\) current、torque、speed 及 IGBT voltage/current。[pdf:E08] 作者据波形重合判断 hybrid PMSM dynamic effect 准确；但 Fig. 10 没有报告这些动态段的统一数值误差，因此本卡只把它称为视觉和趋势一致，而不从曲线估读精确误差。

**问题 3：各 system-level block 组合后是否仍能保持端口波形？** Fig. 11 比较 generator、converter、transformer 和 rectifier 的 FPGA 与 PSCAD/EMTDC 输出。[pdf:E09] 论文报告 generator 为 \(300\,V\)、\(400\,Hz\)，transformer line-to-line amplitude 约 \(550\,V\)，rectifier voltage 在负载变化时约围绕 \(520\,V\) 波动，并称各 CRNN block 与传统模型表现几乎相同。[pdf:E10] 这些数值是作者报告值；波形比较仍缺少跨设备、跨工况的误差分布。

**问题 4：多时间尺度 hybrid 是否保留 device switching detail？** Fig. 10(g)(h) 同时输出 IGBT hybrid 内部的 \(1\,\mu s\) system-level steady-state channel 和 \(50\,ns\) device-level transient channel；前者在两点间近似线性跳变，后者显示 turn-off 的 nonlinear voltage/current transient。[pdf:E08] [pdf:E10] 这说明多速率拆分确实产生了 system-level block 看不到的局部形状，但参照仍是 SaberRD 数据，不是器件实测。

**问题 5：硬件能否在 deadline 内完成？** Table 2 报告总利用率约为 \(55.51\%\) BRAM、\(68.24\%\) DSP、\(2.76\%\) FF、\(37.05\%\) LUT；表中 total latency 为 \(820\,ns\)，单个 PMSM block 为 \(810\,ns\)。[pdf:E07] 正文据此称所有 model 都能在 \(1\,\mu s\) 内处理，完整 emulation 以 system-level \(1\,\mu s\)、device-level \(50\,ns\) 实时运行；作为对照，同一 MEA 在一台 16 GB RAM、4-core 3.4 GHz CPU 上用 PSCAD/EMTDC 每仿真 \(1\,s\) 约需 5 min。[pdf:E09] 这有力支持“给定这套网络、这块 FPGA 和这组工况，deadline 可以满足”，但不直接支持任意系统规模都保持相同 speed-up。

## § 8 — Take-aways

**5 句话**

1. MLBB 不是一个覆盖全系统的 monolithic neural simulator，而是按端口、因果关系和时间尺度拆开的 learned building blocks。[pdf:E04]
2. 已知物理关系可以直接变成 recurrent weight；难以显式建模的局部非线性再由训练得到。[pdf:E03] [pdf:E04]
3. PMSM 的单体黑箱会因小步长差分、internal interlock 和 anti-causal correlation 在闭环中失效，物理分块是方法成立的关键而非装饰。[pdf:E05] [pdf:E06]
4. system-level \(1\,\mu s\) 与 device-level \(50\,ns\) 的 hybrid 设计把有限 FPGA 资源集中到真正需要高带宽的 switching interval。[pdf:E04] [pdf:E10]
5. 论文展示了波形一致、低 MAE 和 FPGA deadline，但验证主要相对离线仿真器，尚未闭合实物 HIL、广泛 distribution shift 与长期组合稳定性。[pdf:E07] [pdf:E08] [pdf:E09]

**3 句话**

MLBB 的真正贡献是用电力电子知识规定 neural block 的边界，再利用 FPGA 并行执行，而不是简单地用 AI 替代方程。[pdf:E04] [pdf:E06] 实验支持这套结构在一个 MEA case study 中达到 \(1\,\mu s/50\,ns\) 多时间尺度运行，并复现 PSCAD/EMTDC、SaberRD 的主要波形。[pdf:E08] [pdf:E09] 最重要的未决问题是，这种由数据训练的局部端口模型在未见工况和长时间闭环组合后，是否仍保持物理一致与稳定。

**1 句话**

这篇论文证明了“物理因果分块 + learned local dynamics + FPGA 并行”是可运行的实时 emulation 路线，但还没有证明它是可认证、可外推的 HIL surrogate。

## § 9 — 最脆弱的假设

最脆弱的假设是：**只要每个 MLBB 在训练覆盖的端口工况上具有低 one-step MAE，并按作者给定的因果边界连接，整个闭环系统在未见组合工况下也会保持准确和稳定。**

这个假设一旦不成立，核心贡献会从“可组合 building blocks”退化成“只在给定轨迹附近拟合良好的多个网络”。论文其实已经展示了风险机制：单体 PMSM 模型对小输入误差敏感，会在 closed loop 中振荡；相关性还会产生 anti-causal shortcut。[pdf:E05] [pdf:E06] 分块能排除这两个已知 shortcut，却不能自动保证每个 block 的局部误差在网络连接后不会同向累积，也不能保证 unseen joint state、参数漂移、饱和、故障或传感器偏置仍落在训练分布内。这一段是基于论文证据的推断。

作者提供的正面证据是：training dataset 覆盖多种 working conditions，另有 test dataset，模型还会被放回传统仿真系统通过 evaluation condition 后才上 FPGA；所有 CRNN 报告在 100 epochs 后达到 \(1\%\) 以内 MAE。[pdf:E06] [pdf:E07] 作者也用负载和 speed-reference steps 做了 system-level dynamic comparison。[pdf:E08] [pdf:E09] 但论文没有给出 block interconnection 的 stability proof、energy/passivity constraint、长时误差增长曲线或系统性的 out-of-distribution sweep；硬件台架展示的是 FPGA、DAC、oscilloscope 和 host connection，结果真值仍来自 PSCAD/EMTDC 与 SaberRD，而非独立实物 plant/controller 的闭环 HIL 试验。[pdf:E07] [pdf:E09] [pdf:E10]

因此，论文最有说服力的结论范围应限定为：在作者构造的数据、工况和 MEA topology 上，这些 MLBB 可以按报告资源与步长实时执行并与离线仿真波形一致。把它外推成任意 ATA 工况下都可靠，目前证据不足。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 MEA，而是论文自己暴露的关键机制：**物理因果分块是否真的比单体 PMSM CRNN 更能承受闭环扰动。**

可以按以下最小方案执行：

1. 用论文 Table 3 的 PMSM 基线建立一个可控 \(d/q\) simulation：nominal apparent power \(60\,kVA\)、nominal voltage \(0.3\,kV\)、rated frequency \(60\,Hz\)、stator winding resistance \(0.021\) p.u.、\(d/q\)-axis inductance \(0.689\) p.u.；其余参数也直接取表，不从图中估读。[pdf:E10]
2. 从同一轨迹训练两个 parameter-count 尽量接近的模型：A 是 Fig. 4 的 single CRNN；B 是 Fig. 2(e) 的 current/torque/speed 分块 CRNN。两者都先用论文起点，即 1 layer、hidden size 约 4 倍 input size、sequence length 3，并用 Eq. (18) MAE、Adam 和 shuffled data。[pdf:E04] [pdf:E05] [pdf:E06]
3. 训练后不要只做 teacher-forced one-step test。把两个模型分别接回同一 speed-current closed loop，复现论文在 \(1-5\,s\) 的 load/speed schedule，再额外加入训练中未出现的小 initial-state offset、sensor bias 和参数漂移。[pdf:E08] [pdf:E09]
4. 测量四类结果：\(d/q\) current、torque、speed 的 trajectory error；连续运行中误差是否增长；是否出现非物理 energy injection；每步执行 latency。所有比较使用 simulator 导出的原始数值，不从 plotted curve 估读。
5. 若分块模型在扰动下保持 bounded error 和闭环稳定，而 single CRNN 出现论文 Fig. 4/5 所述的粘滞预测、振荡或 anti-causal sensitivity，就支持“物理分块是关键机制”；若两者表现相当，或分块模型同样在轻微分布偏移下失稳，则会削弱论文最重要的方法论 claim。

这个复现不验证 device-level \(50\,ns\) SiC transient，也不验证完整 VCU128 resource result；它只用最低成本检验“为什么需要 ML building blocks，而不是一个大黑箱”。

## § 11 — 最强反例设计

最强反例不是再找一条波形让 MAE 稍微变大，而是构造一个**每个局部端口值看起来仍在训练范围内，但 block 的联合状态序列从未出现过**的闭环工况。具体做法是：在 PMSM load step 期间同时改变 DC-bus condition、machine parameter 与 sensor delay，使单点电压、电流、速度都不越过训练 min/max，却让它们之间的相位关系和历史依赖发生变化；随后重复 load reversal，延长运行时间，观察局部误差是否经 controller 和 power network 正反馈累积。

攻击指标应包括：相对于 EMT reference 的 long-horizon state error、time-to-divergence、DC-link energy balance residual、torque-current consistency，以及 gate/control saturation 是否被触发。若 MLBB 在 one-step MAE 仍低时出现能量凭空增长、速度振荡或 block 间状态不一致，而相同工况下的 EMT reference 稳定，就说明低 supervised error 不能保证 building-block composability。这会直接击中第 9 节的脆弱假设，而不是只证明“训练数据还可以再多一点”。

论文已经证明单体模型会因 feedback 与 anti-causal shortcut 失败，也说明 training coverage 决定 SiC model 是否 versatile。[pdf:E05] [pdf:E06] 但它没有报告上述联合分布偏移、energy consistency 或 long-horizon stress test。[pdf:E07] [pdf:E09] 因而这个反例的替代解释很明确：Fig. 10/11 的一致性可能来自测试轨迹与训练分布足够接近，而不一定来自 MLBB 连接后具有可迁移的系统级稳定性。这里是反例设计，不是论文已经观察到的失败事实。

## § 12 — Follow-up Research Bet

**主押注：建立双向 electromechanical-vibration MLBB，把 inverter/PMSM 的 electromagnetic torque ripple、结构模态与 air-gap modulation 放进同一个实时闭环，使 FPGA HIL 能直接研究“电气控制怎样激发机械共振，机械位移又怎样改写电磁动力学”。** 新问题不再是给既定电气模型复现一条速度或电流波形，而是：switching 与 current-control 产生的频谱成分落到机座和转子结构模态附近时，能否实时再现由 torque/magnetic-force excitation 到 vibration，再由 air-gap change 回到 flux linkage、current 与 torque 的闭环演化？如果成立，它首次可能让控制器在 HIL 中“感到”自己激发的结构共振，而不是在电气仿真结束后另做一次 vibration post-processing。

核心机制是一条有返回作用的物理因果链。论文已经把 PMSM 拆成 current、torque、speed units，并用 Eq. (14)–(17)规定 \(v_d,v_q,\omega_e\rightarrow i_d,i_q\rightarrow T_e\rightarrow\omega_r,\theta_m\) 的方向。[pdf:E04] [pdf:E05] 新模型在 torque unit 后把电磁转矩脉动和径向磁拉力投影到若干 structural modal coordinates \(q_m,\dot q_m\)，由 motor-mount stiffness/damping 推进位移；位移再改变局部 air-gap，进而改变 \(L_d(q),L_q(q),\lambda_{pm}(q)\) 或 back-EMF，并把更新后的电磁参数送回 current unit 和 Eq. (15) 的 torque relation。于是因果链成为“switching/control spectrum \(\rightarrow\) current harmonics \(\rightarrow\) torque/magnetic-force spectrum \(\rightarrow\) structural resonance \(\rightarrow\) air-gap modulation \(\rightarrow\) flux/current/torque sidebands”。删掉最后一段反馈后，系统只能生成机械响应，不能产生由结构运动反向调制的电流和转矩，因此基本能力会发生改变，而不是少一个附加输出。

至少有四个基本设计变量。第一是**structural modal basis**：保留哪些弯曲、扭转或机座模态，以及电磁力如何投影到各 mode shape。第二是**mechanical boundary**：motor-mount stiffness 与 damping 决定共振频率、带宽和模态耦合。第三是**switching/control spectral placement**：carrier、modulation sideband 与 current-loop bandwidth 相对结构模态的位置决定激励强度。第四是**air-gap sensitivity**：\(\partial L_d/\partial q_m\)、\(\partial L_q/\partial q_m\)、\(\partial\lambda_{pm}/\partial q_m\) 决定机械位移能否留下可观测的电气侧反馈。representation 也随之改变：MLBB 的 hidden state 不再只有电气 history 和 rotor speed/angle，而是增加具有明确空间 mode shape 的 \((q_m,\dot q_m)\)，并让它们进入电磁参数映射。

这个押注建立在论文特异的多时标与硬件证据上。Fig. 2(b) 把 SiC IGBT 的 \(50\,ns\) transient ANN 与 \(1\,\mu s\) steady-state CRNN 组合，Fig. 10(g)(h) 显示细步长 channel 保留了 system-level 线性跳变中看不到的 nonlinear turn-off voltage/current shape；这些 switching edges 正是高频 electromagnetic-force spectrum 的来源之一。[pdf:E04] [pdf:E08] Fig. 10(b)(c)(f)(i) 又展示了 current、torque、speed 在 load 与 speed-reference changes 下沿作者的因果分块共同变化，说明机械状态已经处于 block graph 内，只是论文把它停在刚体 \(J,B,\omega_r,\theta_m\)，没有表示结构振型和 air-gap feedback。[pdf:E05] [pdf:E08] Table 2 报告全部模型总 latency 为 \(820\,ns\)，PMSM block 为 \(810\,ns\)，并给出约 \(68.24\%\) DSP 与 \(55.51\%\) BRAM 使用率；这说明 fixed-step FPGA 路线已成立，也暴露出新增 modal update 必须利用较慢机械时标并严格控制状态数，而不能假定资源无限。[pdf:E07] 附录 Table 3 则把 \(L_d/L_q\)、permanent-magnet strength 和固定 parasitics 当成常数；主押注恰好把其中一部分提升为受结构位移调制的动态量。[pdf:E10]

**最大收益**是把电气 controller、PWM spectrum 与 motor/mount mechanical design 放进同一实时实验对象：研究者可以观察修改 switching frequency、modulation 或 current-loop bandwidth 后，共振峰、air-gap motion、电流 sideband 与 torque ripple 如何一起迁移，从而发现纯 electrical HIL 和单向 vibration calculation 都看不到的闭环模态。**最大科学风险**是实际 air-gap displacement 对 \(L_d,L_q,\lambda_{pm}\) 的反馈可能远弱于 measurement noise、inverter nonideality 或未建模电磁力谐波；若电气侧 sideband 无法随 mechanical boundary 重复变化，双向机制就没有被识别。另一个风险是少数 modal coordinates 无法覆盖 switching harmonics 激发的局部结构形变，导致 learned feedback 只是特定机座上的相关性。

排除“只是多加一个 mechanical filter 或离线后处理”的最小实验，应在同一 inverter–PMSM 台架上同步采集 phase current、DC-link waveform、torque、air-gap displacement 与 accelerometer response，并准备两种已知 mount stiffness/damping。先选择一个 PWM/control sideband 扫过目标 structural mode，再比较三者：A 为原始 electrical MLBB；B 为 A 后接单向 torque-to-vibration modal filter；C 为带 \(q_m\rightarrow air\mbox{-}gap\rightarrow L_d,L_q,\lambda_{pm}\rightarrow current\) 返回作用的双向 MLBB。B 和 C 使用相同 modal basis、force projection 与机械参数。若 B、C 都能复现 vibration resonance，但只有 C 能在两种机座边界下同时预测 phase-current/back-EMF sideband 的幅值、相位和 resonance-frequency shift，才能把收益归因于 air-gap feedback；若 B 与 C 在电气侧无可分辨差异，或 C 只改善 vibration output，这个主机制被反驳。

相对本文及邻近方向，这个候选的四层差异是：**problem** 从 electrical waveform emulation 改为实时 electromechanical-structural closed-loop resonance；**mechanism** 是结构位移改变 air-gap 与电磁参数后返回 current/torque，不是端口辨识、计算调度或事后机械映射；**representation** 是带空间 mode shape 的 modal state 加 displacement-dependent electromagnetic parameters，不是 behavioral state、intervention-conditioned state、waveform/event operator 或 impedance kernel；**experimental object** 是 inverter、PMSM 与 mount structure 构成的共同物理系统，而非纯电气设备或同一 topology 的离线参照。论文只在结论中把 real-time multi-domain emulation 列为未来方向，没有给出上述双向结构机制。[pdf:E10] 本卡未对 electromechanical vibration digital twin、air-gap-coupled motor model 与 real-time multi-domain HIL 的相关全文做充分检索，因此这是证据约束下的候选判断，不声称 novelty。

**Wild-card：**利用 MEA 中 3 个 ATRU 与 2 套 PMSM 的重复设备结构，训练共享 weight、每台设备仅保留一个 manufacturing-variation latent code 的 population MLBB，以共享比例、latent dimension 和设备间参数分布为设计变量，在一块 FPGA 上实时研究同型设备差异如何形成系统级负载分散与母线统计行为。
