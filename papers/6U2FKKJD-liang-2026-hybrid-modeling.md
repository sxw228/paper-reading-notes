# Hybrid Modeling Approach Combining Analytical and Neural Ordinary Differential Equations for Accelerated Simulation of Grid-Tied Inverter｜论文精读证据卡

- 作者：Yaofeng Liang，Zhicong Huang，Yu Chen
- 出处：IEEE Transactions on Power Electronics
- 年份：2026
- DOI：10.1109/TPEL.2026.3659885
- Zotero key：6U2FKKJD

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“如何再做一个更准的 inverter surrogate”，而是一个很具体的时间尺度错配：grid-tied inverter 的开关、LCL filter 和 inner current loop 很快，传统模型因此需要微秒级步长；但大规模新能源场站的系统级稳定性常由慢得多的 outer loop 主导。若所有部件都被迫跟随最快环节推进，长时间、多机仿真会把大量计算花在慢环节不需要的时间分辨率上。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

整机 NN surrogate 虽可用一次 coarse-step forward propagation 代替许多细步迭代，却必须同时学习 inner loop、outer loop、DC 侧、故障逻辑和多种控制切换，网络容易变深、变大，而且训练数据需要覆盖过多工况。作者因此把问题重写为：能否只让 NN 接管真正迫使步长变小的 fast subsystem，同时把慢环节保留为可解释的 analytical model？Fig. 1 把“整机进 NN”和“只替换 switches、filters、inner loop”两种边界直接并列。[pdf:E02]（PDF 物理页 2，Fig. 1 及相邻正文）

这件事的重要性在于，它试图同时保住三项通常互相牵制的属性：coarse-step 的速度、控制与能量路径的物理可解释性，以及对多种系统级工况的适应性。作者的目标不是复现开关纹波、热效应或寄生参数，而是加速故障和扰动下的 system-level transient simulation；这个适用层级决定了后续所有结论的边界。[pdf:E03]（PDF 物理页 2，贡献与建模范围）

## § 2 — 前人工作与不足

论文回顾的第一类方法仍以物理模型为核心：ideal switching、approximate discrete-time switching、switch-state prediction、event-driven framework 和 switching-function model 都在减少事件处理或简化非线性开关；circuit averaging 与 linearization 则进一步忽略周期性 switching behavior，聚焦宏观动态。它们已经能显著快于器件级详细模型，但只要 fast inner loop 仍与 slow outer loop 使用同一小步长，系统级长仿真的主要浪费就没有消失。[pdf:E01]（PDF 物理页 1，Introduction）

第二类方法是整机 NN surrogate。它的优势是绕开高频迭代，用较大的时间步做状态推进；不足则不是简单的“NN 不够准”，而是学习边界过大：load change、控制策略切换、short-circuit fault 等行为都要由同一个网络吸收，容易产生复杂、过参数化模型，抵消本来想获得的计算优势。[pdf:E02]（PDF 物理页 2，Fig. 1 左侧正文）

作者真正改变的是 partition 假设：不再把 converter 当作不可拆的黑箱，而是利用带宽差异和 algebraic constraints 把模型拆成 fast learned part 与 slow analytical part。NODE 只参数化局部 derivative field，轨迹推进仍交给数值积分器；outer loop、DC-bus、PLL 和功率平衡路径则继续显式表达。这样做的潜在收益是更小的网络和更窄的数据覆盖面，但代价是必须证明所选 boundary variables 足以让 learned subsystem 成为闭合动力系统。[pdf:E03]（PDF 物理页 2，NODE 理由、分析模型保留项与贡献）

## § 3 — 重建作者的思考路径

以下是基于论文证据的逆向重建，不是作者逐字陈述。

1. 系统级仿真关心的是 outer-loop stability 与故障恢复，而不是每个 switching edge；因此“全模型由最快时间尺度决定”是首先应拆掉的计算约束。[pdf:E01]
2. 直接做 averaged model 需要知道内部控制和电路细节，商业 inverter 未必开放；直接做整机 NN 又把慢动态和多种保护逻辑一起塞进网络，训练空间过大。[pdf:E02]
3. 物理系统天然写成 state derivative，因此可让 NN 学习 \(\dot{x}\) 而不是一次性预测未来状态，再复用现有 ODE solver 完成任意 coarse-step 的 trajectory generation。这比另造一个带 hidden state 的时序网络更容易嵌入 Simulink。[pdf:E03]
4. 接下来需要选一个可闭合的接口：作者把 grid-side currents \(I_{2d},I_{2q}\) 当状态，把 outer-loop current references 当 algebraic variables，把 \(V_{gd},V_{dc}\) 当 external inputs；NN 以这些量产生 current derivatives。[pdf:E08]（PDF 物理页 5，Fig. 3–4 与 Eq. (13)）
5. 把 AC fast subsystem 拆走后，DC/AC 的电连接也被拆开，所以必须用 equivalent current sources 显式恢复 chopper 消耗和功率平衡。Eq. (15)–(16) 正是在修补这个接口，而不是附带的工程细节。[pdf:E09]（PDF 物理页 5，Eq. (14)–(16)）

由此得到的核心路线是：先按时间尺度与代数接口分区，再用 NODE 学 fast derivative field，最后用 analytical current sources 和控制器重新闭合整个 inverter。

## § 4 — 核心 Intuition

只学习“迫使仿真采用小步长”的部分，而不是学习整个 inverter。NODE 负责 switches、LCL filters 与 inner loop 的快速导数，outer loop、PLL、DC-bus 和保护逻辑仍按物理方程运行；这样 coarse-step 能力来自 learned fast subsystem，可解释性和工况适应性则来自未被替换的 analytical shell。[pdf:E07]（PDF 物理页 4，Section II-B 与 Eq. (12)）[pdf:E09]

## § 5 — 具体方法与完整 Pipeline

论文以三相 LCL grid-tied inverter 为例。原 switch-based model 包含 DC-bus、六开关桥、\(L_1-C_f-L_2\) filter、inner current PI、DC/AC outer voltage loops、PLL、LVRT 和 chopper；研究层级明确忽略热与寄生效应，并假设理想、平衡三相电网。[pdf:E04]（PDF 物理页 3，Section II-A 与 Eq. (1)–(3)）[pdf:E05]（PDF 物理页 3，Fig. 2 与 Eq. (4)–(5)）

完整 pipeline 如下。

1. **保留慢环节。** DC-side 与 grid-side outer PI 由 Eq. (6) 给出，PLL 由 Eq. (8) 给出；LVRT 在电压偏差达到 \(0.05\) 时切换电流优先级并执行 \(I_{\max}\) 限幅。chopper 在 \(V_{dc}>1.05V_{dc,rated}\) 时导通、降到 \(1.025V_{dc,rated}\) 以下时关断。[pdf:E06]（PDF 物理页 4，Eq. (6)–(11) 与 chopper 正文）
2. **替换 fast subsystem。** 作者用一个 fully connected NODE 替换 switches、LCL filters 和 inner loop，网络不直接输出未来电流，而是输出 \(\dot I_{2d,NN},\dot I_{2q,NN}\)，再经数值积分得到 \(I_{2d,NN},I_{2q,NN}\)。Fig. 3–4 展示了 analytical shell、NODE 与 grid 的连接关系。[pdf:E08]（PDF 物理页 5，Fig. 3–4）
3. **定义 learned interface。** NODE 的状态是 \(\mathbf{x}=[I_{2d},I_{2q}]\)，algebraic inputs 是 \(\mathbf{z}=[I_{2d,ref},I_{2q,ref}]\)，external inputs 是 \(\mathbf{u}=[V_{gd},V_{dc}]\)。论文没有输入 \(V_{gq}\)，因为其验证假设理想平衡电网和正确 PLL，使 \(V_{gq}=0\)。[pdf:E11]（PDF 物理页 6，Eq. (17) 及相邻正文）
4. **生成训练数据。** switch-based reference model 用 Simulink 2024b 的 Simscape Electrical Specialized Power Systems 建立；\(P_{in}=4\text{ MW}\)，随机系数每 \(0.15\text{ s}\) 更新一次，每次仿真 \(3\text{ s}\)，Euler 固定步长 \(10^{-6}\text{ s}\)。共运行 180 次，数据下采样到 \(10^5\text{ Hz}\)，六个输入/输出通道约占 1.88 GB。[pdf:E11]（PDF 物理页 6，Eq. (18)–(20) 与 dataset 正文）
5. **训练 NODE。** kernel network 是 \(6\rightarrow48\rightarrow24\rightarrow2\) 的 fully connected network，两个 hidden layers 使用 LeakyReLU；训练用 RK4 forward propagation、sequence MSE、batch size 128、sequence length 5、Adam、初始学习率 \(2\times10^{-3}\)，迭代 100000 次。loss 比较的是积分后的 state sequence，而不是直接拟合导数标签。[pdf:E12]（PDF 物理页 7，Table II 与训练正文）
6. **重新接入物理模型。** PyTorch 权重和激活函数导出到 Simulink MATLAB function block；积分后的 \(dq\)-axis currents 变回 \(abc\) 并驱动 controllable current sources。DC 侧则用 Eq. (15) 表示输入功率与 chopper，用 Eq. (16) 的 \(I_o\) 恢复 DC/AC 功率交换。[pdf:E10]（PDF 物理页 6，Fig. 5）[pdf:E09]
7. **输出系统级轨迹。** hybrid model 与 analytical outer loop、PLL、DC-bus 一起由固定步长 solver 推进，输出 \(P,Q,V_{dc},I_{2d},I_{2q}\) 等系统级量，而不是重建开关纹波。

数值表示、并行和 FPGA 边界必须说清：论文报告的是 MATLAB/Simulink floating-point 计算与 OPAL-RT 5707XG 上的 **CPU-only** real-time simulation；没有报告 fixed-point quantization、FPGA mapping、pipeline latency、DSP/BRAM/LUT 资源或多实例并行调度。因此它证明的是 coarse-step surrogate 的软件与实时 CPU 潜力，不是 FPGA 可实现性。[pdf:E13]（PDF 物理页 7，Table III 计算口径）[pdf:E19]（PDF 物理页 11，Fig. 9、Table VI 与实时平台说明）

## § 6 — 核心数学推导

先看原系统。Eq. (1) 用 \(i_{1k},v_{ck},i_{2k},V_{dc}\) 写出三相 LCL 与 DC-bus 的 ODE；Eq. (3) 将其转到 \(dq\) 坐标，其中 \(I_1,V_c,I_2,V_{dc}\) 都参与状态演化。[pdf:E04] Inner PI 再根据 \(I_{2,ref}-I_2\)、grid voltage 与交叉耦合补偿生成 inverter terminal voltage reference。[pdf:E05]

作者随后把需要学习的关系压缩为

\[
\frac{d\mathbf I_2}{dt}
=F(\mathbf I_2,\mathbf I_{2ref},\mathbf V_g,V_{dc},t),
\tag{14}
\]

并用

\[
\dot{\mathbf x}
=f_{\mathrm{NN}}(\mathbf x,\mathbf z,\mathbf u,\theta,t)
\tag{13}
\]

代替 \(F\)。这里的工程 intuition 是：NN 只近似“当前边界状态到局部斜率”的映射，积分器负责从 \(t_1\) 到 \(t_2\) 累积斜率，因而可以沿用 ODE solver 的步长与接口。[pdf:E08]（PDF 物理页 5，Eq. (13) 与 Fig. 4）[pdf:E09]（PDF 物理页 5，Eq. (14)）

具体 feature assignment 是

\[
\mathbf u=[V_{gd},V_{dc}],\qquad
\mathbf z=[I_{2d,ref},I_{2q,ref}],\qquad
\mathbf x=[I_{2d},I_{2q}].
\tag{17}
\]

这一步并非普通的 feature selection，而是在声称上述六个量加时间编码足以闭合 fast subsystem；它也是全文最关键、最需要挑战的数学假设。[pdf:E11]

分区后 DC 与 AC 的直接电连接被切断，作者用

\[
I_{dc}=\frac{P_{in}}{V_{dc}}
-k_{\mathrm{chop}}\frac{V_{dc}}{R_c},
\tag{15}
\]

表示输入功率与 chopper 消耗，再用

\[
I_o=\frac{3}{2}\frac{V_{gd}I_{2d}+V_{gq}I_{2q}}{V_{dc}}
\tag{16}
\]

把 AC 侧功率折算为 DC-bus current，以维持 power balance。[pdf:E09] 这两式解释了 hybrid model 为什么不只是“NN 接一个 outer loop”：若没有这条显式能量通路，NODE 的电流预测与 DC-bus dynamics 会彼此脱节。

## § 7 — 实验设计与结论

**问题一：coarse step 是否真的减少计算？ → 实验：** 在 MATLAB 中用 RK4 比较 switch-based numerical model、averaged model 与 hybrid model，统一模拟 \(2\text{ s}\)，步长分别为 \(10^{-6}\)、\(5\times10^{-5}\)、\(2\times10^{-4}\text{ s}\)。**答案：** hybrid 每步 3328 FLOPs，高于 numerical 的 454 和 averaged 的 356；但总 FLOPs 为 \(1.33\times10^8\)，低于 numerical 的 \(3.62\times10^9\)，高于 averaged 的 \(5.70\times10^7\)。Table III 的 measured CPU time 分别是 45.5770、0.1272、0.0704 s；按表内数字计算，hybrid 约为 numerical 的 0.154%，但它快于 averaged 的原因被作者归因于 MATLAB 的 BLAS/LAPACK matrix optimization，而不是 FLOP 数更少。[pdf:E13]（PDF 物理页 7，Table III 与相邻解释）

**问题二：故障与扰动下是否仍跟得住 reference model？ → 实验：** 预测评估使用 fixed-step Euler，初始 \(V_{dc}=2000\text{ V}\)、三相 grid peak \(900\text{ V}\)、\(50\text{ Hz}\)，功率从 1–4 MW 均匀取 48 个 steady-state points；比较 \(P,Q,V_{dc},I_{2d},I_{2q}\)。Fig. 6–7 给出 system quantities 和 currents 的 reference、averaged、HybridNODE 波形及 absolute error。[pdf:E14]（PDF 物理页 8，Fig. 6）[pdf:E15]（PDF 物理页 9，Fig. 7） **答案：** Table IV 中 active-power rRMSE 为 0.0069–0.0654，DC-bus voltage 为 0.0003–0.0054，d-axis current 为 0.0069–0.0858；三相短路是这三项中最难的已测工况之一。[pdf:E16]（PDF 物理页 9，Table IV 与测试设置）

测试覆盖三相/单相短路、3.8 MW→1.4 MW→3.8 MW 的功率变化、grid voltage \(\pm5\%\)、DC-bus 降到 96% 与 85%、低 DC-bus 下的功率变化，以及 0.8 MW、\(V_{dc,ref}\) 与 \(V_{gd}\) 各 5% 扰动的幅相特性。短路在 \(t=1\text{ s}\) 施加并持续 \(0.15\text{ s}\)；grid-voltage-rise 工况超过训练数据的 900 V 上界，但只外推了 5% 且持续 0.3 s。[pdf:E16] [pdf:E17]（PDF 物理页 10，测试 2–8 与 Eq. (21)）[pdf:E18]（PDF 物理页 10，Fig. 8）

论文的 rRMSE 定义是

\[
\mathrm{rRMSE}
=\frac{\sqrt{\frac1N\sum_{i=1}^{N}(y_i-\hat y_i)^2}}{\bar y}.
\tag{21}
\]

当 \(Q\) 或 \(I_{2q}\) 的均值接近零时，分母会使指标爆大；Table IV 中多项 reactive-power/q-axis-current rRMSE 超过 1，作者明确说明这不等价于大 absolute error。因此这些通道必须结合 absolute error 或按额定量归一化的误差阅读，不能拿 rRMSE 单独证明“高保真”。[pdf:E17] [pdf:E18]

**问题三：常见工况的实际 wall-clock saving 是否稳定？ → 实验：** Table V 对八种场景各运行五次取平均。**答案：** numerical model 为 51.820–53.995 s，averaged model 为 1.507–1.642 s，hybrid model 为 0.749–0.792 s；作者据此概括 hybrid 只需 switch-based model 的 1–2% simulation time。[pdf:E18]（PDF 物理页 10，Table V）

**问题四：real-time CPU 负担是否下降？ → 实验：** 在 OPAL-RT 5707XG 上只用 CPU 运行并读取 Monitor 的 total CPU usage。**答案：** Table VI 报告 numerical model 在 \(10^{-5}\text{ s}\) 步长为 10.74%，hybrid 在同一步长为 8.75%，在 \(2\times10^{-4}\text{ s}\) 为 0.49%。同一步长的 8.75/10.74≈81.5%，与正文“about 81.4%”一致；但 0.49/10.74≈4.6%，与正文“only 2–3% of the CPU resources”的字面说法不一致，正式引用应以 Table VI 数字为准。[pdf:E19]

总体上，论文证明了一个 simulation-to-simulation 结论：在其理想平衡电网、固定拓扑与控制参数、simulation-generated training data 范围内，hybrid NODE 可以用 \(2\times10^{-4}\text{ s}\) 步长稳定推进，并在所测故障/扰动中接近 switch-based reference，同时显著缩短 CPU time。它没有证明硬件 inverter measurement 下、非理想电网下或 FPGA 上仍保持同样结论。

## § 8 — Take-aways

**5 句话。** 第一，系统级 inverter 仿真的浪费来自 fast inner loop 迫使 slow outer loop 一起使用小步长。[pdf:E01] 第二，作者按带宽和代数接口分区，只让 NODE 替代 switches、LCL filters 与 inner loop。[pdf:E07] 第三，网络学习 current derivative，analytical shell 保留 outer loop、PLL、DC-bus、LVRT 与功率平衡。[pdf:E09] 第四，报告实验在 \(2\times10^{-4}\text{ s}\) 步长下取得接近 reference 的系统级波形，并把常见场景 CPU time 降到 switch-based model 的 1–2%。[pdf:E18] 第五，这些结论仍受 simulation-only data、理想平衡电网、固定控制/参数和 CPU-only 平台限制。[pdf:E11] [pdf:E19]

**3 句话。** 这篇论文最有价值的不是 NODE 本身，而是“只学习时间步瓶颈”的 hybrid partition。实验说明该 partition 在作者构造的 grid-tied LCL inverter 上能把 coarse-step 与 analytical control shell 组合起来。最需要继续验证的是六个 boundary variables 是否真的构成跨工况、跨硬件的充分状态。

**1 句话。** 用 NODE 学 fast derivative field、用物理方程守住慢控制和能量接口，是本文的核心，也正是其最强假设所在。

## § 9 — 最脆弱的假设

最脆弱的假设是：\([I_{2d},I_{2q},I_{2d,ref},I_{2q,ref},V_{gd},V_{dc}]\) 加时间编码足以让 fast subsystem 成为单值、Markovian 的 derivative mapping。原 switch-based model 明明还含有 inverter-side current \(I_1\)、filter capacitor voltage \(V_c\)、inner-PI integrator、switching phase 等内部状态；若两个轨迹在所选六个量上相同、内部状态却不同，则真实 \(\dot I_2\) 可以不同，任何 deterministic \(f_{\mathrm{NN}}\) 都无法同时表示。[pdf:E04] [pdf:E11]

论文为该假设提供的证据是：随机激励训练、1–4 MW 的 48 个测试点、多种短路与扰动、一次略超训练电压范围的测试，以及幅相响应对比。[pdf:E16] [pdf:E17] 但它没有直接做“observed-state collision”检验，也没有覆盖 unbalanced/harmonic grid、PLL phase error、frequency drift、measurement delay/noise、controller parameter drift 或 physical-inverter data。作者反而明确设 \(V_{gq}=0\)、假设 noise 已被商业技术处理，并声称 simulation 与 physical data 的来源差异不影响方法有效性；这项声称尚未由硬件实验支撑。[pdf:E11] [pdf:E12]

如果充分状态假设失效，后果不是误差稍增，而是 Eq. (14) 所需的函数根本不存在或依赖遗漏历史；此时加深网络、增加数据或延长训练都不能根治结构性 state aliasing。

## § 10 — 最小复现实验

一周内最值得复现的是“六变量 NODE 能否在 \(2\times10^{-4}\text{ s}\) 下闭合并跨过作者报告的故障集”，不必先复刻完整 OPAL-RT 平台。

1. 按 Table I 在 Simulink 建同一 LCL inverter，保留 switch-based reference；用 Eq. (18)–(20) 的随机激励范围生成一组训练 trajectories，并保留从未进入训练的三相短路、single-phase fault、\(+5\%\) grid rise 和 85% DC-bus 工况作为 test set。[pdf:E07] [pdf:E11]
2. 实现 \(6\rightarrow48\rightarrow24\rightarrow2\) LeakyReLU network，按 Table II 用 sequence loss 训练 NODE；导出到同一 fixed-step simulation，比较 \(10^{-6}\text{ s}\) reference 与 \(2\times10^{-4}\text{ s}\) hybrid。[pdf:E12]
3. 记录 \(P,V_{dc},I_{2d}\) 的 rRMSE、按额定量归一化的 \(Q,I_{2q}\) absolute RMSE、最大瞬时误差、是否发散，以及同一 CPU 上的 wall time。避免只用接近零均值的 reactive rRMSE。[pdf:E16] [pdf:E17]
4. **支持核心 claim：** 全部预留工况无发散，\(P,V_{dc},I_{2d}\) 的最坏 rRMSE 不高于论文报告的 0.0654、0.0054、0.0858 的约 1.2 倍，且同机 wall time 不超过 switch-based reference 的 2%。**部分支持：** 精度达到上述阈值但 wall time 只降到 2–5%，说明 coarse-step 有效但未复现 headline speedup。**反驳：** 至少两个预留工况的关键误差超过论文最坏值两倍、出现不稳定，或为了稳定必须把步长降到接近 inner-loop sampling time。[pdf:E13] [pdf:E18]

这个实验的价值在于同时检验 accuracy、coarse-step stability 和 speed，而不是只重画一条看起来相似的 waveform。

## § 11 — 最强反例设计

最强反例不是再加一个更严重的 fault，而是证明 learned interface 不闭合。构造两条 switch-based trajectories：通过不同的预激励，使它们在某一时刻拥有近乎相同的 \(I_{2d},I_{2q},I_{2d,ref},I_{2q,ref},V_{gd},V_{dc}\)，但具有不同的 \(I_1,V_c\)、PI integrator state 或 switching phase；随后施加完全相同的 future inputs。若两条 reference trajectory 的 \(\dot I_2\) 或下一步 \(I_2\) 显著不同，就得到“相同 NODE 输入、不同正确输出”的直接证据，Eq. (14) 的 deterministic closure 被推翻。[pdf:E04] [pdf:E11]

为了让碰撞更贴近真实电网，可在预激励中加入 negative-sequence voltage、phase jump、frequency ramp 和 harmonic distortion，使 \(V_{gq}\neq0\) 或 PLL 暂态偏离。评价时不只看平均 rRMSE，而要画出 feature-space 最近邻之间的 derivative disagreement；若 disagreement 超过 reference numerical error，失败原因就是 hidden-state aliasing，而不是网络容量不足。这个反例一旦成立，会直接挑战“只用当前六个量即可把 fast subsystem coarse-step 化”的核心机制。

## § 12 — Follow-up Research Idea

**候选方向：学习“可验证的最小动态端口”，而不是固定 feature 的 current-derivative surrogate。** 由于本卡没有完成该方向的系统相关工作检索，下面不声称 novelty。

**(a) 未满足需求。** 现有方法先人为指定六个 boundary variables，再假定它们足以闭合；面对 grid unbalance、控制器漂移、多 converter 相互作用或 measurement latency，接口可能缺少必要记忆。[pdf:E11]

**(b) 研究价值。** 把目标从“单台 inverter 的 waveform fitting”改成“识别最小、Markovian、energy-consistent 且可组合的 reduced port state”，可同时服务 EMT coarse-step simulation、多机稳定性和实时数字平台。高影响力不应只来自更低测试误差，而应来自可证伪的 state sufficiency、passivity/energy balance 和跨实例 composability。

**(c) 可借鉴工具。** 可结合 nonlinear observability / delay embedding 发现所需历史维度，用 latent state-space 或 Koopman lifting 构造最小动态状态，再用 port-Hamiltonian 或 dissipativity constraint 约束端口能量；最后做 fixed-point sensitivity 分析，判断该端口模型是否适合 FPGA，而不是直接宣称可部署。

**(d) 首个证伪实验。** 先运行第 11 节的 state-collision benchmark：若加入有限 latent/history state 后，相同 learned port state 仍对应显著不同的 reference derivative，或多 inverter weak-grid 仿真出现净能量生成、步长缩小时不收敛，就立即否决该状态定义。

**(e) 与本文的实质区别。** 这不是简单加入 \(V_{gq}\)、换更深网络或扩大训练集；它把“哪些量构成充分状态”从未经验证的设计前提变为待学习、待验证的研究对象，并把单机 trajectory accuracy 提升为端口闭合、能量一致与多实例稳定性的联合目标。论文已经显示 coarse-step hybrid partition 的工程潜力，但 Table VI 仍只是 CPU-only 证据；新的方向必须把可组合性和硬件数值约束当作第一类验收，而不是后续移植事项。[pdf:E19]
