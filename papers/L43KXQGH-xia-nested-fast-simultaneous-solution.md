# Shiwei Xia et al. (2025) — Real-Time Modeling Method for Large-Scale Photovoltaic Power Stations Using Nested Fast and Simultaneous Solution

- DOI: `10.1109/TIE.2024.3440469`
- Zotero parent: `L43KXQGH`
- 阅读口径：以下“论文原文”只指本文作者在该 PDF 中明确写出的内容；“相关工作”只复述本文对参考文献的定位，未做独立的全领域检索；批评、复现方案、反例和研究方向均明确标为基于证据的推断或候选判断。

## § 1 — 研究问题与重要性

**论文原文明确声称。** 本文要解决的是大型光伏电站详细 EMT（electromagnetic transient，电磁暂态）实时仿真中的三角矛盾：既要保留开关器件带来的高频动态和 HIL 接口，又要覆盖几十到上百个光伏单元，还必须在每个微秒级时间步内用有限硬件完成计算。大型电站由多层汇集网络和大量级联器件组成，节点数会迅速膨胀；同时，为反映可达数十 kHz 的动态，作者指出 EMT 步长通常需要小于开关时间的 \(1/10\) 到 \(1/50\)。因此，这不是单纯“把离线模型跑快”，而是要让模型压缩、并行调度、硬件资源和实时 deadline 同时成立。[pdf:E01]

**论文原文明确声称。** 作者的目标是把 NFSS（nested fast and simultaneous solution，嵌套快速同步求解）同时用于单元层和电站层：单元层构造固定导纳值的 Norton 接口并保留被消元节点的信息，电站层把光伏单元、汇集支路、子站和外部电网组织成可递归更新的层次求解。摘要给出的结果边界是：与同规模离线模型相比，最大 relative error（RE）小于 4%，并在 \(2.5~\mu s\) 步长内实现 100 单元电站的实时仿真。[pdf:E01]

其工程价值在于，同一套模型若真的能同时访问单元内部状态、保留开关级动态并稳定赶上硬实时 deadline，就比聚合模型更适合控制器 HIL、单元故障传播和站内相互作用研究。但这项价值仍受本文实验覆盖范围约束：论文验证了特定拓扑、器件模型、控制步长和 FPGA，不等于已经证明任意大型光伏电站都能达到相同误差与规模。

## § 2 — 前人工作与不足

以下均是**本文对相关工作的归纳，不是本精读独立核验后的全领域结论**。

在单元层，平均化 inverter 模型已经能显著降低计算量，但作者认为它会丢失开关过程的高频分量和 HIL 所需接口。传统 NFSS 已用于 MMC、power electronic transformer 等模块化电力电子系统，其优点是通过 Norton 等值做无损网络矩阵降维；问题是一个光伏单元包含 PV array、boost、VSC、LC filter 和 transformer 等多个级联设备，直接处理高阶内部节点矩阵仍有昂贵的逆解过程。[pdf:E01] 参考文献列表显示，作者将 Strunz 与 Carlson 2007 年的 NFSS 作为方法源头，并将 MMC/PET 的高效 EMT 建模列为直接先例。[pdf:E11]

在开关建模层，dual resistance value（DRV）可以针对有限开关状态预存矩阵，但若整个 VSC 的网络矩阵随状态变化，存储资源会很大；L/C-switch associative discrete circuit（ADC）可选取 L/C 以维持固定导纳，但仍把 AC、DC 两侧耦在同一网络，无法减少外部端口看到的内部节点。作者因此选择 switching-function controlled-source model：把开关动作放入受控源，使端口导纳固定，并把 AC、DC 两侧拆开。[pdf:E02]

在电站层，clustering equivalent model 通过温度、irradiance、inverter 参数或控制策略等因素聚合同类单元，已能用少量单元近似电站外部特性；作者指出其不足是通常围绕单一主导因素服务特定稳定性分析，聚合后无法访问每个单元内部信息。并行解耦方面，借助 transmission line、transformer、capacitor/inductor 的物理延迟，或人为插入 latency、使用 MATE，都能形成子系统，但作者将其局限归纳为适用性不足或不可忽略的精度损失。RTDS/RT-Lab 的多核 CPU 并行已经提供一定规模的光伏站模型，但若保留逐器件详细模型，规模和硬件成本仍受限；FPGA 有高并行、低延迟优势，却需要与之匹配的模型和求解流程。[pdf:E01] [pdf:E02]

## § 3 — 重建作者的思考路径

**基于论文背景与方法顺序的合理重建。**

第一步不是先选 FPGA，而是先观察拓扑。每个光伏单元虽然内部复杂，却以相同的四端口形式嵌入 35 kV 汇集网络；多个单元再按支路、子站和主变层层聚合。于是一个自然问题是：能否只让外层网络看到每个模块的端口等值，同时保留从端口电压反解内部节点的能力？Fig. 1 和 Fig. 2 给出了这种“模块化拓扑 → 端口接口”的起点。[pdf:E02]

第二步是消除端口矩阵随开关状态变化的障碍。若 VSC 的开关状态直接进入导纳矩阵，NFSS 所需的矩阵逆和等值量难以预计算；把 VSC 表示成 switching-function controlled sources 后，开关动作进入源项，AC、DC 两侧导纳可保持固定。代价是普通受控源解耦会引入一步延迟，因此下一问变成：能否重新排列求解顺序，让本步 AC 电流先生成 \(i_{dc}\)，本步 DC 电压再反馈到 AC，而不是使用上一时步近似？[pdf:E03] [pdf:E04]

第三步把同一个端口代数递归地向上应用。单元 AC 网络先用 Schur complement 压成 Norton 等值；并联单元的等值导纳和电流源直接相加；汇集支路和子站再做一次 NFSS；最后把各子站、主变和 AC grid 放入一个六节点 EMT 网络。每步求解后按相反方向恢复内部节点并更新 history current sources，形成“外层求解向下展开、内层更新向上压缩”的层次循环。[pdf:E04] [pdf:E05] [pdf:E06]

第四步才是把已经暴露出的并行性映射到 FPGA：无数据依赖的 AC/DC 和器件更新并行执行，三相重复计算用 `HLS UNROLL` 展开，多单元和多子站循环用 `HLS PIPELINE` 做 initiation interval \(II=1\) 的流水。这样新增单元主要增加流水深度和保存 history sources 的寄存器，而不必复制所有 DSP/BRAM 计算核心。[pdf:E07]

## § 4 — 核心 Intuition

把每个复杂光伏单元压成一个**固定导纳、随时间更新电流源**的 Norton 端口，并保留从端口回到内部节点的逆向恢复关系，就能让电站网络只解一个小矩阵，而不是每步重解全部器件节点。[pdf:E03] 同样的压缩再嵌套到汇集支路和子站，配合本时步内“AC 电流 → DC 求解 → AC 反馈”的顺序，就能在不主动插入一步延迟的前提下暴露大量并行和流水机会。[pdf:E04] [pdf:E05]

## § 5 — 具体方法与完整 Pipeline

下面用论文的 20 单元、四子站案例说明一个仿真步从输入到输出如何运行。输入包括上一步电站节点电压、各器件的 history current sources、VSC/boost 的门极状态、控制器信号以及温度和 irradiance；输出是本步电站端口电压电流、每个单元内部状态和供下一步使用的新 history sources。

1. **建立固定导纳接口。** 两电平 VSC 不用开关电阻直接改写全网导纳，而用 switching function \(s_a,s_b,s_c\) 把 DC 电压、三相电流映射成 AC 线电压和 DC 电流。这样开关状态出现在受控源而不是端口导纳矩阵中，AC、DC 网络可分别求解。[pdf:E03]
2. **压缩单元 AC 网络。** LC filter 与 transformer 的内部节点组成分块节点导纳方程；消去六个内部节点后，四个外部节点只暴露 \(\mathbf Y_{eq}\) 和 \(\mathbf J_{eq}\)。外层电站得到新端口电压后，再用式 (5) 恢复内部电压，所以“压缩”并非丢掉内部状态。[pdf:E03]
3. **独立求解单元 DC 网络。** boost 的常见开关组合只有三类，作者用 DRV 预存相应结果；电容、电感用 trapezoidal integration 离散。求得 AC 支路电流后立即计算本步 \(i_{dc}\)，DC 网络随后求出 \(V_{dc}\) 和节点电压，再更新 DC history sources 及返回 AC 侧的受控源量。Fig. 5 的先后关系是作者“不引入一步延迟”主张的关键。[pdf:E04]
4. **并联压缩子站。** 一个子站内 \(m\) 个单元并联，因此各单元 \(\mathbf Y_{eq,i}\) 与 \(\mathbf J_{eq,i}\) 直接求和。短传输线使用 \(\pi\)-equivalent；考虑并网开关和故障带来的大幅变化，支路 L/C 改用 backward Euler 以避免 numerical oscillation。支路不同开关状态对应的矩阵在仿真前预计算，实时阶段按控制状态调用。[pdf:E04] [pdf:E05]
5. **再次压缩到子站端口并求全站。** 单元集合和汇集支路组成七节点子站，再用 NFSS 压成与单元同形、参数不同的端口等值。多个子站并联后与 35/220 kV transformer、AC grid 共同构成 Fig. 8 的六节点网络；AC grid 的电压源串联阻抗被离散成 Norton 形式，本步用式 (13) 完成 EMT network solution。[pdf:E05]
6. **沿层次反向恢复和更新。** 从全站电压开始，同时更新 grid/transformer history sources，并恢复各子站内部节点；随后并行更新各单元和汇集支路；最后按“支路 → 子站 → 电站”的顺序重新生成等值电流源，进入下一时步。Fig. 9 展示了这一向下展开、向上回收的递归流程。[pdf:E06]
7. **映射到 FPGA。** 作者用 Xilinx HLS 从 C++ 生成 HDL。单元内 AC/DC 和各器件更新走并行路径，三相循环完全 `UNROLL`；站级每个子站、支路和 PV unit 的循环用 `PIPELINE`，数组 partition 后做到 \(II=1\)。[pdf:E07]
8. **案例参数。** 论文实验的单元采用 \(V_{dc}=0.8~\text{kV}\)，boost 与 VSC switching frequency 均为 \(2~\text{kHz}\)，\(L_{boost}=250~\mu\text{H}\)，\(C_{boost}=32000~\mu\text{F}\)，AC grid 为 50 Hz；这些数值来自 Appendix Tables A-I/A-II，是最小复现应优先锁定的事实参数。[pdf:E10]

## § 6 — 核心数学推导

### 6.1 switching-function controlled-source interface

在“IGBT 与 diode 的 on-state resistance 相同、忽略 dead zone 与 forward conduction voltage”的前提下，式 (1) 把两电平 VSC 写成

\[
\begin{aligned}
v_{ab}&=(s_a-s_b)v_{dc}+\big[(1-2s_a)i_a+(1-2s_b)i_b\big]R_{sw},\\
v_{bc}&=(s_b-s_c)v_{dc}+\big[(1-2s_b)i_b+(1-2s_c)i_c\big]R_{sw},\\
v_{ca}&=(s_c-s_a)v_{dc}+\big[(1-2s_c)i_c+(1-2s_a)i_a\big]R_{sw},\\
i_{dc}&=s_ai_a+s_bi_b+s_ci_c.
\end{aligned}
\]

直觉是：\(s\) 决定 DC bus 如何投影成线电压，同时 \(R_{sw}\) 保留导通压降的电阻部分；反方向用三相瞬时电流和开关函数得到 DC current。开关动作改变源值，但不要求重建 AC/DC 两侧的固定导纳矩阵。[pdf:E03]

### 6.2 NFSS 本质：Schur complement

把外部节点和内部节点的方程分块：

\[
\begin{bmatrix}
\mathbf Y_{11}&\mathbf Y_{12}\\
\mathbf Y_{21}&\mathbf Y_{22}
\end{bmatrix}
\begin{bmatrix}
\mathbf V_{EX}\\
\mathbf V_{IN}
\end{bmatrix}
=
\begin{bmatrix}
\mathbf J_{EX}\\
\mathbf J_{IN}
\end{bmatrix}.
\]

从第二行得到 \(\mathbf V_{IN}=\mathbf Y_{22}^{-1}(\mathbf J_{IN}-\mathbf Y_{21}\mathbf V_{EX})\)，代回第一行：

\[
\underbrace{\left(\mathbf Y_{11}-\mathbf Y_{12}\mathbf Y_{22}^{-1}\mathbf Y_{21}\right)}_{\mathbf Y_{eq}}
\mathbf V_{EX}
=
\underbrace{\left(\mathbf J_{EX}-\mathbf Y_{12}\mathbf Y_{22}^{-1}\mathbf J_{IN}\right)}_{\mathbf J_{eq}}.
\]

这就是 Norton 压缩：外层只解 \(\mathbf V_{EX}\)，但 \(\mathbf Y_{22}^{-1}\)、\(\mathbf Y_{21}\) 和 \(\mathbf J_{IN}\) 仍允许恢复 \(\mathbf V_{IN}\)。因为接口导纳固定，关键矩阵可以预计算；每步主要更新电流源。[pdf:E03]

### 6.3 单元 DC 网络和子站聚合

DC 侧写成

\[
\mathbf V_{DC}=\mathbf Y_{DC}^{-1}\mathbf J_{DC},
\qquad
\mathbf V_{DC}=
\begin{bmatrix}
V_1-V_4&V_2-V_4&V_3-V_4
\end{bmatrix}^{T},
\]

其中 \(\mathbf J_{DC}\) 包含 PV current、各电感/电容 history current 和本步 \(I_{dc}\)。该式本身并不消除 AC/DC 的因果顺序；真正避免一步近似的是 Fig. 5 规定先从本步 AC branch current 形成 \(I_{dc}\)，再解 DC 并把本步 \(V_{dc}\) 反馈回 AC。[pdf:E04]

对同一子站内并联的 \(m\) 个单元，端口等值直接满足

\[
\mathbf Y_{eq,P}=\sum_{i=1}^{m}\mathbf Y_{eq,i},
\qquad
\mathbf J_{eq,P}=\sum_{i=1}^{m}\mathbf J_{eq,i}.
\]

汇集支路满足 \(\mathbf Y_{Brh}\mathbf V_{Brh}=\mathbf J_{Brh}\)，随后再做一次 Schur complement 得到子站端口。论文式 (10) 的矩阵用空白表示部分零项；本卡不把这些排版空白擅自改写成显式数值，精确矩阵布局以 PDF 物理第 5 页为准。[pdf:E05]

### 6.4 外部电网离散和全站求解

AC grid 单相关系 \(v=v_s+R_si+L_s\,di/dt\) 经离散后写成 Norton 形式：

\[
\begin{aligned}
i(t)&=g_{sys}v(t)+J_{sys}(t),\\
g_{sys}&=\frac{\Delta t}{L_s+R_s\Delta t},\\
J_{sys}(t)&=-g_{sys}v_s(t-\Delta t)
+\frac{L_s}{L_s+R_s\Delta t}i(t-\Delta t).
\end{aligned}
\]

选 Fig. 8 的地 \(G\) 为参考后，全站本步只需求

\[
\mathbf V_{station(6\times1)}
=\mathbf Y_{station(6\times6)}^{-1}\mathbf J_{station(6\times1)}.
\]

这说明算法速度并非来自忽略电站层网络，而是把绝大多数内部节点递归压到电流源更新中，让顶层保留一个六节点线性解。[pdf:E05]

### 6.5 误差指标

论文用

\[
ME=\max_i|x_i-y_i|,
\qquad
RE=\frac{\lVert x-y\rVert_2}{\lVert y\rVert_2}
\]

比较实时结果 \(x\) 与离线 PSCAD/EMTDC 结果 \(y\)。RE 是整段波形的二范数相对误差，不是逐时刻最大百分比；因此“RE 小于 4%”不能解读成每个采样点都小于 4%。[pdf:E08]

## § 7 — 实验设计与结论

**平台事实。** 计算端使用 Xilinx `xc7vx690tffg1927-2` FPGA 和 I/O board；控制端一条路径由 RTDS 经 Aurora fiber 闭环，另一条路径由 RCP 设备经 AI/AO、DI/DO 连接，允许实际 controller HIL。精度实验在四个子站、20 个 PV units 上运行，并建立相同 topology 和 parameters 的逐器件 PSCAD/EMTDC offline model。两模型 circuit step 均为 \(2.5~\mu s\)，但实时模型 controller step 为 \(50~\mu s\)，离线模型为 \(2.5~\mu s\)；这个不一致是解释误差时不能忽略的实验条件。[pdf:E06] [pdf:E07]

**问题 1：不同子站环境量变化时，压缩模型能否保留 MPPT 动态？** 实验在 \(t=2~s\) 改变四个子站的 temperature/irradiance：#1 温度 25→30 °C，#2 为 25→20 °C，#3 irradiance 1000→1300 W/m²，#4 为 1000→700 W/m²，记录/仿真 10 s。作者报告 DC bus voltage 轻微变化，PV port voltage/current 随 MPPT 追踪而变化，各波形 RE 小于 2%。答案是在这组异质环境阶跃下支持，但没有覆盖空间连续阴影或快速随机 irradiance。[pdf:E08]

**问题 2：单个单元内部 DC 故障能否被详细模型和 HIL 接口保留？** 在子站 #1 的第一个 PV unit DC bus 于 \(t=2~s\) 施加 transition resistance \(0.2~\Omega\) 的 pole-to-pole fault，持续 0.05 s，由 RCP 控制，记录 10 s。作者展示故障后 DC bus voltage 快速下降，PV array voltage 和 output power 同步下降，清故障后控制使 DC bus 返回额定值。论文在该小节没有另报一个 RE 数字，所以不能从图上估读出精确误差。[pdf:E08]

**问题 3：汇集支路单相接地故障能否保持相间暂态？** 在子站 #1 近单元侧支路于 \(t=2~s\) 施加 A-phase-to-ground fault，grounding resistance \(0.01~\Omega\)，持续 0.05 s。作者报告故障相接近 0，非故障相升至正常值的 \(\sqrt3\) 倍、约 49.5 kV，RE 约 3%；其解释是实时通信延迟和 controller step 差异造成偏差。[pdf:E08] [pdf:E09]

**问题 4：PCC 三相短路时，站级等值是否保持 DC chopper 动态？** 在 PCC 施加 \(0.01~\Omega\)、持续 0.05 s 的 three-phase-to-ground fault。AC-side voltage 降近 0 后，DC bus 上升到 1.12 kV，即 reference 的约 1.4 倍，触发 chopper；作者报告故障期间 RE 小于 3%，并承认通信/控制 delay 使波形错开数个 time steps，从而产生较大 ME。[pdf:E09]

**问题 5：扩大到 100 units 后是否仍满足实时 deadline，资源怎样增长？** 作者建立四子站、100 units 模型并重复 PCC 三相故障。100-unit latency 为 198 clocks，即 1.98 µs；20-unit 为 111 clocks，即 1.11 µs。在 100 MHz 下两者均小于 2 µs，作者留裕量后称可在 2.5 µs step 实时运行，足以支持最高 20 kHz switching frequency。BRAM 均为 268（18.23%），DSP48E 均为 1642（45.61%）；LUT 从 135886（31.37%）增至 239394（55.26%），FF 从 146785（16.94%）增至 493137（56.92%）。作者据此判断 DSP/BRAM 不再是主要 scale limit，保存 history sources 的 LUT/FF 才是，并推算单颗该型号 FPGA 最大可到 150 units。[pdf:E09] [pdf:E10]

**结论边界。** 本文的证据支持“在给定器件模型、四子站拓扑、控制接口和故障/环境工况下，100-unit 模型能赶上 2.5 µs deadline，20-unit 波形与特定 PSCAD reference 的 RE 为几个百分点”。它没有直接证明 150-unit 物理实现的 timing closure，也没有用同一个 \(2.5~\mu s\) controller step 做完全同条件对照；150 units 是作者基于资源限制的推断，maximum RE <4% 是全文汇总 claim。[pdf:E10]

## § 8 — Take-aways

**5 句话。** ① 本文把大型光伏站的复杂度问题重新组织成单元、支路、子站和电站四层端口压缩。② switching-function controlled-source model 让 VSC 的开关状态进入源项，从而为 NFSS 保住固定导纳接口。③ Schur complement 不只缩小顶层网络，还通过逆向恢复保留被消元内部节点，所以能模拟单元故障而非只有站外等值。④ FPGA 上的真正扩展手段是 AC/DC 并行、器件/相并行和 \(II=1\) 流水，100 units 在 100 MHz 下报告 1.98 µs latency。⑤ 结果最应谨慎看待之处，是关键固定导纳/无延迟结论依赖理想化开关模型，而且实时与离线控制步长并不相同。[pdf:E03] [pdf:E07] [pdf:E10]

**3 句话。** ① 核心方法是把每层网络变成固定 \(\mathbf Y\) 加可更新 \(\mathbf J\) 的 Norton interface，并递归恢复内部状态。② 核心实证是在四子站 20-unit 精度案例和 100-unit scale case 中，报告最高几个百分点 RE 与 2.5 µs deadline。③ 它证明了一个有约束的工程 operating point，而不是对任意器件非理想、任意拓扑和任意控制器的普遍保证。[pdf:E06] [pdf:E09]

**1 句话。** 这篇论文最重要的贡献是把 NFSS 的端口代数与 FPGA 的层次流水对齐，使详细光伏站 EMT 模型在特定假设下同时获得内部可见性和百单元实时规模。

## § 9 — 最脆弱的假设

**最脆弱假设：VSC switching-function controlled-source abstraction 在目标工况下既能维持固定导纳，又能通过求解重排等效为“无一步延迟”的真实开关接口。**

这是单点失效假设。式 (1) 明确要求 IGBT 与 diode 具有相同 on-state resistance，并忽略 dead zone 和 forward conduction voltage；固定导纳与 AC/DC 解耦正是建立在开关行为能被受控源完整承载的基础上。[pdf:E03] 若实际 dead time、diode conduction、器件不对称、current zero-crossing 附近换流或 boost discontinuous-conduction 使端口关系依赖额外离散状态，那么 \(\mathbf Y\) 未必仍可视为固定，或 \(\mathbf J\) 的本步更新不足以代表真实能量交换。这样一来，NFSS 的预计算优势和“不增加 delay/error”的核心解释会同时受损，而不仅是多出一点参数误差。

**论文提供的证据。** 20-unit 模型经历环境阶跃、单元 DC fault、汇集支路单相故障和 PCC 三相故障，离线/实时 RE 报告在几个百分点内；其中还包含 RCP HIL 和通信链路，说明方法不是纯软件 toy example。[pdf:E08] [pdf:E09]  
**缺少的证据。** 论文没有给出 dead time、不同 \(R_{on}\)、forward voltage、非连续导通或器件温度漂移的敏感性 sweep，也没有把“重排但无一步延迟”的实现与一个明确保留一步延迟的 baseline 做消融。实时 controller step 为 50 µs、离线为 2.5 µs，更使观测误差混合了接口模型、通信和控制离散三种来源。[pdf:E07] 因此，现有实验支持所选理想化模型内的有效性，但不能隔离验证最脆弱假设在更真实 switching physics 下仍成立。

## § 10 — 最小复现实验

**目标。** 一周内只验证最核心、最可证伪的 claim：在固定导纳接口成立的模型内，Fig. 5 的本时步求解重排比普通 one-step delayed controlled-source coupling 更接近 monolithic EMT reference。

**数据与参数。** 不需要先做 100 units。采用 Appendix Table A-I 的单个 PV unit：\(V_{dc}=0.8~\text{kV}\)，boost/VSC 均为 2 kHz，\(L_{boost}=250~\mu H\)，\(C_{boost}=32000~\mu F\)，\(L_{VSC}=160~\mu H\)，\(C_{filt}=500~\mu F\)，仿真 circuit step 固定为 2.5 µs。[pdf:E10] 使用同一门极序列、同一 PV/MPPT 输入，运行稳态、irradiance step 和 \(0.2~\Omega\)、0.05 s DC pole-to-pole fault；后两项来自论文案例。[pdf:E08]

**实现三个版本。**

1. monolithic reference：单一节点网络内同步解 AC、VSC interface 和 DC；
2. NFSS reordered：按式 (4)/(5) 压缩 AC，先用本步 branch current 形成 \(i_{dc}\)，解 DC 后把本步 \(V_{dc}\) 反馈 AC；
3. delayed baseline：AC、DC 互相使用上一时步量，显式保留 one-step delay。

前两版的离散方法、器件参数和 controller step 必须一致；否则无法把差异归因于求解顺序。测量 DC bus voltage、PV current/power、三相 current、每步 energy-balance residual、ME 和 RE，RE 按论文式 (15) 计算。[pdf:E03] [pdf:E04] [pdf:E08]

**支持标准。** reordered 版本在三类工况中均保持稳定，对 monolithic reference 的关键波形 RE <4%，fault clearing 附近没有系统性的一步相移，而且 RE/energy residual 明显优于 delayed baseline。  
**反驳标准。** reordered 与 delayed 的误差无实质差别，或在相同离散/控制步长下仍出现一步相移、RE ≥4%、错误换流或能量残差累积。这个实验不验证百单元 scale，但能直接检验论文把精度归因于“重排消除 delay”的最关键机制。

## § 11 — 最强反例设计

**基于证据的反例设计。** 构造一个“端口导纳不再近似固定”的 switching stress test：在同一个 PV unit 中加入 IGBT/diode 不同 \(R_{on}\)、非零 forward voltage、可调 dead time、current-dependent diode conduction，并让 boost 在连续/非连续导通边界往返；同时在 AC current zero-crossing 附近触发 PCC voltage sag 或 DC fault。用 0.1–0.25 µs 的详细器件 monolithic EMT 作为 reference，再以论文 2.5 µs NFSS 实现接收完全相同的门极和控制命令。[pdf:E03] [pdf:E09]

这比单纯再加一个更大电站更有攻击力，因为它针对的不是 FPGA 资源，而是方法成立的接口不变量。替代解释是：论文的低 RE 主要来自 reference 与实时模型共享了相同的理想化 switching abstraction，加上所选工况没有强烈激活 dead-time/diode 非线性；并非 NFSS 对真实开关系统天然无损。

应扫描 dead time、器件压降、温度导致的 \(R_{on}\) 不对称、irradiance 和故障相角，测量以下四项：波形 RE/ME、开关事件时间偏差、每周期能量不守恒、错误 conduction state 次数。若存在一块有工程意义的参数区域，使 NFSS 的 RE 超过论文 4% 汇总边界、产生错误 chopper/diode 状态或不能在 2.5 µs 下稳定，而 monolithic reference 正常，那么这就是对“高精度且适用性良好”比扩展规模更强的反例。若误差仍被稳定约束，反而会显著加强论文目前缺失的鲁棒性证据。

## § 12 — Follow-up Research Idea

**候选方向，不声称全球 novelty：从“固定导纳接口”改写为“带在线误差证书和 deadline 约束的 hybrid multiport interface”。** 电气/电力电子实时仿真的高影响研究通常同时要求 EMT fidelity、硬实时 timing closure、可实现硬件成本、HIL 或实际控制器验证，以及在故障和参数不确定性下仍可解释的边界；本文已覆盖其中一部分，但最脆弱处仍是固定导纳接口对真实 switching nonidealities 的适用域。[pdf:E06] [pdf:E09] [pdf:E10]

**(a) 未满足的需求。** 工程上既不希望为所有开关状态重建全网矩阵，也不能默认 dead time、diode conduction 和参数漂移永远足够小。需要一个接口能在大多数时步继续使用预计算 \(\mathbf Y\)，但在端口 residual 表明固定模型即将失真时，局部激活 correction，而不是静默超过误差边界。

**(b) 可能的研究价值。** 把研究目标从“某个理想模型下固定 \(\mathbf Y\) 且很快”改为“对给定非理想集合，实时输出端口量的误差上界，并保证最坏情况下不越过 FPGA deadline”。如果成功，它会同时回答 fidelity 和 schedulability，而不仅是把现有模型多扩几十个 units。

**(c) 可借鉴的相邻方法。** 可结合 hybrid systems 的 mode/event detection、model-order reduction 的 residual estimator、low-rank matrix update（例如只修正被事件激活的端口块）与 real-time systems 的 worst-case execution-time analysis。正常时沿用本文的 NFSS/pipeline；检测到 residual 超阈值时，只对受影响单元切换到局部多模型或 low-rank correction，并把计算预算显式纳入调度。

**(d) 第一个证伪实验。** 用第 11 节的 nonideality sweep 比较三者：原固定 NFSS、全详细 monolithic reference、hybrid residual-corrected interface。预先冻结“RE <4%、无错误 conduction state、每步 <2.5 µs、FPGA LUT/FF 不超过器件容量”四个门槛。若 correction 不能在不越过 deadline/资源上限的情况下显著扩大通过参数域，或 residual 不能提前预测失真，则该方向被第一轮实验否决。

**(e) 与本文的实质区别。** 本文把固定导纳视为构造和预计算效率的基础，并用选定工况的波形误差证明实现可用；候选方向把“接口何时不再可信”本身变成在线状态和可证伪指标，允许局部、受预算约束的模型切换。本文参考文献覆盖 NFSS、switching-function model、ADC/DRV、并行 EMT 与 clustering 等路线，但本卡没有完成针对 hybrid residual certificate 的系统检索，因此这里不能宣称该组合 novel，只能作为由第 9 节证据边界导出的研究假设。[pdf:E02] [pdf:E11]

[pdf:E01]: _evidence/E01-p001-title-introduction.png "PDF physical page 1: title, abstract, introduction"
[pdf:E02]: _evidence/E02-p002-topology-interface.png "PDF physical page 2: Figs. 1-2, interface construction"
[pdf:E03]: _evidence/E03-p003-eq01-eq05-unit-nfss.png "PDF physical page 3: Eqs. (1)-(5), Figs. 3-4"
[pdf:E04]: _evidence/E04-p004-eq06-eq08-unit-pipeline.png "PDF physical page 4: Eqs. (6)-(8), Figs. 5-6"
[pdf:E05]: _evidence/E05-p005-eq09-eq13-station-nfss.png "PDF physical page 5: Eqs. (9)-(13), Figs. 7-8"
[pdf:E06]: _evidence/E06-p006-fig09-fig10-platform.png "PDF physical page 6: Figs. 9-10, station process and FPGA platform"
[pdf:E07]: _evidence/E07-p007-fig11-fig12-experiment-setup.png "PDF physical page 7: Figs. 11-12, HLS algorithms and experiment setup"
[pdf:E08]: _evidence/E08-p008-table01-fig13-fig14.png "PDF physical page 8: Table I, Figs. 13-14, Eqs. (14)-(15)"
[pdf:E09]: _evidence/E09-p009-fig15-fig18-scale-test.png "PDF physical page 9: Figs. 15-18, fault and scale tests"
[pdf:E10]: _evidence/E10-p010-table02-appendix-conclusion.png "PDF physical page 10: Table II, Appendix Tables A-I/A-II, conclusion"
[pdf:E11]: _evidence/E11-p011-references.png "PDF physical page 11: references"
