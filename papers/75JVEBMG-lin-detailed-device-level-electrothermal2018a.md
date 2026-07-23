# Detailed Device-Level Electrothermal Modeling of the Proactive Hybrid HVDC Breaker for Real-Time Hardware-in-the-Loop Simulation of DC Grids

作者：Ning Lin；Venkata Dinavahi  
出处：IEEE Transactions on Power Electronics, Vol. 33, No. 2, pp. 1118–1134  
年份：2018  
DOI：10.1109/TPEL.2017.2685423  
Zotero key：75JVEBMG  
证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文要解决的不是“如何再做一个 HVDC breaker（高压直流断路器）模型”，而是一个跨尺度矛盾：proactive hybrid HVDC breaker（主动式混合高压直流断路器，HHB）在真实设备中由大量串并联 IGBT、snubber（缓冲电路）、MOV、UFD、LCS 和 RCB 组成，设计者需要知道单器件的开关波形、损耗和结温；但电网级 HIL（hardware-in-the-loop，硬件在环）又要求模型在 FPGA 上以实时速度运行。作者因此把目标定为：保留 full-scale（全尺寸）拓扑和 device-level（器件级）信息，同时把计算量压到可供 MTDC（多端直流）系统实时仿真的水平。论文摘要直接给出三类 IGBT 模型、全尺寸 breaker 分区、单元复用和 electrothermal network（电热网络）这四个组成部分，并声称以 HIL 与商业离线工具的比较验证其准确性。[pdf:E01]（PDF 物理页 1，Abstract）

这个问题重要，首先因为 MTDC 的故障处置不能简单照搬点对点 HVDC：若一条直流线路故障就切除整流站交流侧断路器，供电中断可能扩展到部分乃至整个直流系统；HHB 的价值正是把故障段在数毫秒内局部隔离，同时维持健康输电走廊运行。论文还指出，scaled-down（缩比）模型虽然足以验证控制和保护逻辑，却通常省略真实数量的 IGBT、内部节点和 snubber，因此无法可靠回答“器件选型、阵列尺寸、缓冲参数和冷却是否合适”这类设计问题。[pdf:E01]（PDF 物理页 1，Introduction）

解决这一矛盾的工程价值有两层。系统层面，它让研究者在三端 MMC-HVDC 网络中测试 fault detection、breaker sequence 和故障后功率重分配；器件层面，它把 IGBT 的瞬态损耗和结温带回 EMT（electromagnetic transient，电磁暂态）模型，使同一仿真可以反过来指导 MB 与 LCS 的器件数量和 cooling condition（冷却条件）。这是论文区别于只看线路电流或母线电压的传统电网模型的核心价值主张。[pdf:E02]（PDF 物理页 2，Introduction 末段）

## § 2 — 前人工作与不足

论文对既有方法的归纳可分为四类；以下是作者在源 PDF 中的定位，并未用包外文献独立校准 novelty。

第一类是以 TSSM（two-state switch model，两状态开关模型）为核心的 scaled-down HHB。它把 MB 和 LCS 近似为导通/关断两种电阻，主支路通常只保留一个或两个 IGBT 等效，节点少、矩阵小，适合验证 system-level 控制与保护。但它丢掉了实际 IGBT 数量、snubber 和内部状态，既不能给出可信的 switching transient，也不能准确计算损耗与结温，因而不适合 breaker hardware design。[pdf:E01]（PDF 物理页 1，Introduction 下半部）

第二类是 conventional full-scale model（传统全尺寸模型）。它保留真实器件数量和拓扑，理论上能展示更多内部现象；代价是数百个节点形成大规模矩阵，离线仿真很慢，在实时平台上还会造成不可接受的 FPGA 资源占用。更关键的是，若全尺寸模型内部仍只用 TSSM，拓扑虽然详细，器件物理仍不够详细，所以“全尺寸”本身不等于“高 fidelity（高保真）”。[pdf:E02]（PDF 物理页 2，Introduction 左栏）

第三类是 CFM（curve-fitting model，曲线拟合模型）。它仍是两节点器件，稳态电阻来自 IGBT 的静态 I–V 曲线，turn-off current（关断电流）则由实验或商业软件获得的采样波形写入 LUT（lookup table，查找表）。它比 TSSM 更能计算稳态和开关损耗，并保持较低矩阵维数；不足是其暂态电流形状不会随外部电磁环境自动变化，snubber 或工作点改变后往往需要重新调整 LUT。[pdf:E02]（PDF 物理页 2，Introduction 中段）；[pdf:E03]（PDF 物理页 7，Section III-D、III-E）

第四类是 NBM（nonlinear behavioral model，非线性行为模型）。作者把它视为最通用、最接近商业 device-level 工具的模型，因为它显式表示 MOSFET-like channel、非线性电容、tail current 和最低导通压降；但原始 fourth-order NBM（四阶 NBM）节点多、非线性强，需要多次 Newton–Raphson（N–R）迭代，容易受初值影响或不收敛，难以直接进入实时 HIL。[pdf:E02]（PDF 物理页 2，Introduction 中段）；[pdf:E03]（PDF 物理页 7，Section III-E）

因此，本文真正针对的缺口不是单纯“模型不够精确”或“仿真不够快”，而是缺少一种同时处理三件事的架构：保留 full-scale breaker 的系统影响；按任务切换不同器件 fidelity；利用重复结构与 FPGA parallelism（并行性）把计算压缩到实时或近实时。TLM（transmission line modeling，传输线建模）和 voltage–current source coupling（电压–电流源耦合）在此前已经提供了电路分区思路，本文把这种思路进一步用到 HHB 的重复器件阵列和 FPGA 映射上。[pdf:E02]（PDF 物理页 2，Introduction 中后部）

## § 3 — 重建作者的思考路径

下面是基于论文证据逆向重建的思考路径，不把本文的最终方案预先当作前提。

首先，从保护过程看，HHB 的不同部件承担不同物理任务。line protection（线路保护）触发后，LCS 先撤去 gate signal，UFD 约用 2 ms 完成开断，随后 MB 关断并把故障电流转移到 MOV，电流归零后 RCB 才打开。MB 在这一瞬间承受快速电压、电流交叠，所以其 switching waveform、snubber 和瞬态损耗至关重要；LCS 更长时间工作在导通状态，其 steady-state loss（稳态损耗）反而更重要。[pdf:E04]（PDF 物理页 3，Fig. 1、Section II-B 与 Section III 开头）

其次，真实 breaker 由大量结构相同的单元组成。若每个 IGBT、每个 snubber 节点都放进一个整体 admittance matrix（导纳矩阵），计算成本随矩阵维数急剧上升；但若所有单元同步、内部电压均衡，那么大量重复状态其实携带的是同一份信息。一个自然方向便是先把电气连接用受控源断开成可并行子电路，再只详细求解一个 representative unit（代表单元）。论文在 Fig. 2 中明确把 full-scale HHB 经由电压–电流源耦合分解，并把 UFD、LCS 和 MOV 按单元均分。[pdf:E05]（PDF 物理页 4，Fig. 2 与 Section III-A）

第三，器件模型不应“一种精度打天下”。若问题只是保护逻辑和系统暂态，理想两状态开关足够；若要兼顾实时速度与损耗、结温，二节点 CFM 更合适；若要让波形随电磁环境变化，则必须保留更一般的 NBM。于是合理的设计不是寻找唯一最复杂模型，而是建立同一 breaker topology 下可替换的 fidelity ladder（保真度阶梯）。这一步是对已有 TSSM、CFM 与 NBM 优缺点的工程折中，而不是从数学上宣称某一模型普遍最优。[pdf:E06]（PDF 物理页 6，Section III-C、III-D）

最后，器件电气参数随结温变化，而结温又由损耗决定，单向的“电气仿真后再离线算温度”无法形成闭环。因此需要把 thermal RC network 直接离散进每个时间步：电气模型给出电压和电流，热网络更新 junction temperature，温度再更新阈值和静态参数。由于作者继续沿用“所有器件相同”的假设，只需为被选中的代表 IGBT 建一个详细电热网络。[pdf:E07]（PDF 物理页 9，Section III-F、Fig. 6、Eq. (31)–(33)）

把这四步连起来，就得到本文的思路：先按物理任务决定需要保留的器件现象，再利用 breaker 的重复对称结构降维，最后把不同 fidelity 的 IGBT 与电热反馈映射到并行 FPGA pipeline。这个重建属于基于证据的推断，而非作者逐句给出的研发日志。

## § 4 — 核心 Intuition

把 full-scale HHB 看成大量同步且相同的重复单元，而不是一个必须整体求解的巨大电路；通过 voltage–current source coupling 把单元物理解耦，只求一个代表单元即可保留全尺寸拓扑对系统的影响。[pdf:E05]（PDF 物理页 4，Fig. 2）在这个固定拓扑里，TSSM、CFM 和简化 NBM 分别覆盖“最快”“实时且有器件细节”“最通用但更慢”三个 operating point。[pdf:E06]（PDF 物理页 6，Section III-C）再把 power loss → junction temperature → electrical parameters 的反馈闭合，并把各子电路做成并行 FPGA modules，模型就能在系统级实时性和器件级解释力之间按需取舍。[pdf:E07]（PDF 物理页 9，Section III-F）；[pdf:E08]（PDF 物理页 11，Fig. 8、Fig. 9）

## § 5 — 具体方法与完整 Pipeline

以论文中的三端 MMC-HVDC 场景为例：整流站连接两个逆变站，Line 1 中点发生短路，Line 2 保持健康；系统额定直流电压为 200 kV，整流侧功率为 400 MW，线路长 200 km，breaker 总 MOV 保护电压为 340 kV，串联 HHB unit 数为 100。[pdf:E09]（PDF 物理页 16，Appendix）完整 pipeline 如下。

1. **系统与事件输入。** MMC 用 averaged value model（平均值模型，AVM）表示，线路采用 Bergeron/TLM 等效；保护侧计算 voltage derivative protection 与 overcurrent protection。论文的 HIL 实验在 50 ms 时让 Line 1 短路，Line 2 继续传输，以观察故障隔离后健康通道是否维持运行。[pdf:E04]（PDF 物理页 3，Fig. 1、Eq. (2)）；[pdf:E10]（PDF 物理页 12，Section V 开头）

2. **按真实器件组成构造 HHB。** 每个 breaker 包含 current-limiting inductor、RCB、UFD、LCS、MOV、MB 和 snubber。论文用 3×3 IGBT array 说明“串联承压、并联承流”的单元结构；实验中每个 unit 的故障电流由三个并联 IGBT 平分，而多个 unit 串联形成总保护电压。[pdf:E05]（PDF 物理页 4，Fig. 2）；[pdf:E11]（PDF 物理页 15，Fig. 13 结果讨论）

3. **分区与代表单元。** UFD、LCS、MOV 和 MB 被按 unit 拆分，unit 之间通过耦合电压源与电流源保持电气联系；TLM 让线路、电容和电感跨子电路交换 incident pulse（入射脉冲）。在“所有 unit 相同且同步”的条件下，只对任意一个 HHB unit 求解，并用一个并联 IGBT 代表该 unit 中其余并联器件，从而避免把全部内部节点放入同一矩阵。[pdf:E05]（PDF 物理页 4，Section III-A）；[pdf:E06]（PDF 物理页 6，Eq. (12)–(15) 前后的正文）

4. **选择 IGBT fidelity。** Type-1 使用 TSSM，在 \(R_{on}\) 与 \(R_{off}\) 间切换，适合系统级实时 HIL，但不显示开关细节。Type-2 使用 CFM：稳态由温度相关的分段线性 I–V 表示，turn-off 由 LUT 中的电流采样驱动，可实时给出损耗和结温。Type-3 使用简化 NBM：从 fourth-order 模型保留 MOSFET behavior、非线性电容和 tail current，再通过 sensitivity analysis 与子模型并行化把参与 nodal solve 的核心降为 second-order，同时把结果修正项独立计算。[pdf:E06]（PDF 物理页 6，Section III-C、III-D）；[pdf:E03]（PDF 物理页 7，Fig. 5、Section III-E）；[pdf:E12]（PDF 物理页 8，Section III-E.3–4）

5. **离散时间求解与热反馈。** MOV 被写成 nonlinear Norton equivalent，并分成十个 piecewise-linear 区间以减少 N–R 迭代；RCD snubber 用 backward Euler 离散成等效电阻和 history current；NBM 中的非线性电流源、电容和 tail current 也被线性化为导纳与等效电流源。每一步用 \(v_{CE}i_C\) 得到功率损耗，四支路 thermal RC network 更新 \(T_j\)，再按 \(y(T_j)=kT_j+p\) 更新 IGBT 参数。[pdf:E13]（PDF 物理页 5，Eq. (5)–(9)）；[pdf:E06]（PDF 物理页 6，Eq. (10)–(14)）；[pdf:E12]（PDF 物理页 8，Eq. (22)–(29)）；[pdf:E07]（PDF 物理页 9，Eq. (31)–(33)）；[pdf:E14]（PDF 物理页 10，Eq. (34)）

6. **FPGA 映射与依赖调度。** 目标平台是 Xilinx Virtex-7 xc7vx485tffg1761-2；作者用 Vivado HLS 把 C/C++ 子电路函数综合成 IP cores，各模块在 pipeline 中并行，VHDL top-level state machine 负责启动、收敛判断和时间步同步。Type-1/Type-2 最多设置两次迭代，Type-3 设置三次；已完成的模块在状态机中等待最慢模块和本时间步结束。论文没有报告独立的 multi-rate scheme；它展示的是单一顶层步进下的模块级并行与条件重迭代。[pdf:E14]（PDF 物理页 10，Section IV、Table II）；[pdf:E08]（PDF 物理页 11，Fig. 8、Fig. 9）

7. **数值表示与执行速度。** Fig. 8 把内外信号标成 32-bit vector，但正文未明确说明这些 32 bit 是 fixed-point 还是 floating-point，也没有给出 quantization error study，因此不能把“32 bit”进一步解释为某种经过认证的数值格式。[pdf:E08]（PDF 物理页 11，Fig. 8）Type-1 与 Type-2 以 100 MHz 工作，\(T_{clk}=10\) ns；考虑迭代后 HHB 每步约占 80 个时钟周期，并在状态机中等待同步，论文判定二者可实时运行。Type-3 以 125 MHz 工作，统一单次 nominal latency 为 125 个时钟周期且需要三次迭代，因此整体比 real time 慢三倍。[pdf:E14]（PDF 物理页 10，Table II 后正文）；[pdf:E10]（PDF 物理页 12，Section IV 末段）

8. **输出与验证。** device-level 输出包括 MB/LCS 的 \(v_{CE}\)、\(i_C\)、单 IGBT 损耗和结温；system-level 输出包括各站直流电压、电流、功率以及 MOV、snubber、MB 的能量分配。作者分别以 SaberRD 和 PSCAD/EMTDC 为比较基线，再检查不同 IGBT fidelity、不同 snubber 与 full-scale/scaled-down breaker 是否得到一致或有解释差异的结果。[pdf:E10]（PDF 物理页 12，Section V）；[pdf:E15]（PDF 物理页 13，Fig. 10、Fig. 11）；[pdf:E11]（PDF 物理页 15，Fig. 15）

一次具体故障的时序是：50 ms 时 Line 1 短路，LCS 退出、UFD 用约 2 ms 打开，MB 随后关断并由 MOV 在约 4 ms 内清除故障电流，故障段总计约 6 ms 被隔离；之后健康 Line 2 接管功率，系统在不足 100 ms 内进入新的稳态。[pdf:E10]（PDF 物理页 12，Section V）；[pdf:E16]（PDF 物理页 14，Fig. 13）；[pdf:E09]（PDF 物理页 16，Fig. 15 讨论）

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有明确的形式化数学，但重点不是提出新定理，而是把 nonlinear device physics 转成每个 EMT 时间步可解的 Norton form，并通过结构假设降低矩阵维数。

**1. MOV 的非线性与故障清除约束。** 作者用幂律表示 varistor 的 I–V 关系：

\[
i_v=\left(\frac{v_v}{k_vV_{ref}}\right)^{\alpha_v}I_{ref},
\]

再在当前工作点求微分导纳 \(G_v=\partial i_v/\partial v_v\)，把非线性支路改写成 \(G_v\) 与等效电流源 \(I_{veq}=i_v-G_vv_v\)。这使 MOV 可以进入每步线性矩阵，但仍需 N–R 更新；作者报告原始暂态可能超过 20 次迭代，因此把曲线 piecewise-linearize 为十段。[pdf:E13]（PDF 物理页 5，Eq. (5)–(7) 与相邻正文）故障清除电压的设计关系为

\[
V_{ref}=\frac{I_{f,\max}L}{\Delta t_2}+U_{dc},
\]

它的直觉是：MOV 电压除了承担直流母线电压，还要在目标时间 \(\Delta t_2\) 内消耗电感中对应的电流变化能量；保护电压越高，清流越快，但器件承压也越高。[pdf:E13]（PDF 物理页 5，Eq. (8)）；[pdf:E06]（PDF 物理页 6，Eq. (9)）

**2. Snubber 的离散化。** 对 RCD snubber，作者在 MB turn-off 的主要阶段把它等效为 RC，并用 backward Euler 得到

\[
R_{eq}=R_{sD}+\frac{\Delta t}{C_s},
\]

同时用 \(I_h(t)\) 保存电容的 history contribution。工程含义是：电容不再作为额外动态节点参与大矩阵，而是变为一个当前等效电阻加一个由上一步状态更新的电流源。[pdf:E06]（PDF 物理页 6，Eq. (10)、Eq. (11)）

**3. 重复单元如何进入矩阵。** 分区后的一个 \(N\)-node HHB unit 写成 \(\mathbf U_{HHB}=\mathbf G^{-1}\mathbf J\)，并联 IGBT 数 \(m\) 直接乘在对应的 IGBT 导纳和电流源项上。由于 unit 相同，作者只求一个 unit；对于 TSSM/CFM 两节点器件，最终甚至只剩一个未知 nodal voltage，可由总 Norton current 除以总 conductance 得到。[pdf:E06]（PDF 物理页 6，Eq. (12)–(15)）这里的 speedup 并非来自近似求解器，而是来自对称性：用一个状态代表许多被假定完全相同的状态。

**4. CFM 的稳态与关断。** 第 \(i\) 个分段的静态电阻为

\[
R_{ss,i}=\frac{V_{CE}}{I_C}=\frac{1}{k_i(T_j)}+\frac{b_i(T_j)}{k_i(T_j)I_C}.
\]

这相当于用温度相关的分段直线拟合 datasheet I–V curve。关断时则在节点方程中减去 programmed current source \(I_{MB}(t)\)，其值按 LUT 的时间索引读取；所以 CFM 能复现一条预先测得的 turn-off waveform，却不会自动对新的 snubber 环境重塑波形。[pdf:E03]（PDF 物理页 7，Eq. (16)、Eq. (17) 与 Section III-D）

**5. NBM 的线性化、敏感度裁剪和并行化。** 对 MOSFET-like nonlinear current \(i_{mos}\)，作者构造

\[
I_{moseq}=i_{mos}-G_{mosv_d}v_d-G_{mosv_{cge}}v_{cge},
\]

其中两个 \(G\) 是对应偏导数；tail-current 部分也作同类 Norton linearization。随后用 Jacobian sensitivity criterion：若某支路对节点方程的微分贡献在任意时刻都远小于其他支路贡献之和，就从矩阵中移除。论文据此省去 \(G_{tailv_d}\)、\(G_{tailv_{cge}}\)、\(G_{Cce}\) 和 \(I_{taileq}\)，并把 MOSFET behavior 与 tail-current behavior 拆成可并行子模型。[pdf:E12]（PDF 物理页 8，Eq. (23)–(29)、Section III-E.3–4）最终 collector current 由

\[
i_C=i_{mos}+i_{Ccg}+i_{tail}
\]

合成，参与主 nodal solve 的矩阵维数降到 3；其余子模型用于结果修正。作者据此声称 N–R 次数、非线性和矩阵规模同时下降，最大可用 time step 也增大。[pdf:E07]（PDF 物理页 9，Eq. (30) 与前后正文）

**6. 电热闭环。** 四支路 junction-to-case thermal network 被离散成：

\[
T_j=\sum_{i=1}^{4}\left[(P_{loss}+I_{hi})\left(\frac{1}{R_i}+\frac{2\tau_i}{R_i\Delta t}\right)^{-1}\right]+T_e,
\]

其中 \(I_{hi}\) 与 capacitor TLM stub 的 incident pulse 一起保存热网络历史；环境温度 \(T_e\) 设为 25 °C。[pdf:E07]（PDF 物理页 9，Fig. 6、Eq. (31)–(33)）静态器件参数再按

\[
y(T_j)=kT_j+p
\]

更新。作者之所以用线性温度函数，是因为 datasheet 只给了 25 °C 和 125 °C 两组曲线；若有更多温度点，论文明确允许换成 nonlinear function。[pdf:E14]（PDF 物理页 10，Eq. (34) 与相邻正文）

这些公式共同形成一个闭环：network state 决定器件电压电流，器件损耗决定 \(T_j\)，\(T_j\) 又改变下一步 IGBT 参数。其数值核心是“非线性支路在当前步做局部线性化，动态储能支路变成 history source”，其工程核心则是“只把对输出最重要的状态留在主矩阵中”。

## § 7 — 实验设计与结论

**问题 1：复杂 IGBT 模型是否真的改善 device-level accuracy？** → 作者让带 RCD snubber 的 MB IGBT 关断，以 SaberRD 的 fourth-order device model 为参考，同时比较 NBM、CFM 和 TSSM 的 HIL 波形。→ NBM 显示约 1.6 μs 的器件关断、明显 tail current，以及约 23 μs 的缓慢 \(v_{CE}\) 上升；CFM 的关断电流按 LUT 为约 2.5 μs；TSSM 把电流波形拉成理想直线，因此显著低估 transient loss。NBM case 的瞬态损耗峰值约 37 kW，而 CFM/NBM 的结温曲线接近 SaberRD，TSSM 无法形成可信的电热闭环。[pdf:E10]（PDF 物理页 12，Section V-A）；[pdf:E15]（PDF 物理页 13，Fig. 10）

**问题 2：模型能否分辨 snubber 对器件应力的影响？** → 作者把 RCD snubber 换成 RC snubber，再比较 NBM、CFM 与 SaberRD。→ NBM 会随外部电磁环境改变 turn-off behavior，而 CFM 在两个 snubber case 中仍给出相同的 2.5 μs current waveform，暴露了 LUT 模型的环境适应性限制。RC case 中 \(v_{CE}\) 与 \(i_C\) 更强地重叠，瞬态损耗约 500 kW，结温瞬时上升约 0.7 °C；RCD case 的相应温升约 0.08 °C，因此 RCD 明显降低 MB switching loss。[pdf:E10]（PDF 物理页 12，Section V-A 末段）；[pdf:E15]（PDF 物理页 13，Fig. 11 与正文）

**问题 3：电热模型能否指导 IGBT array 与 cooling design？** → 作者在 1 kA 和 4 kA 稳态直流电流下分别观察 MB 与 LCS 的结温。→ 对 MB，单个 IGBT 构成的 1×1 unit 即使在 4 kA case 中最高温度也约为 55 °C，论文据此判断容量足够；对 LCS，1 kA 时单器件可用，但 4 kA 自冷却时结温可超过 100 °C，安全裕度过小，需要 2×2 array 或外部冷却。实验还支持一个更细的结论：MB 的 design 需要 switching transient model，而 LCS 的温升主要由 static characteristic 决定，CFM 的稳态部分已足够。[pdf:E16]（PDF 物理页 14，Fig. 12 与相邻正文）

**问题 4：三种 fidelity 是否会改变 breaker 的主要系统级保护结果？** → 作者比较 Type-1、Type-2、Type-3 的 MOV voltage 和 line current，并以 PSCAD/EMTDC 对照。→ 三者给出的基本波形形状相同：breaking time 约 2 ms，fault clearance time 约 4 ms。Type-1/Type-2 可实时执行，Type-3 的示波器横轴因运行慢三倍而显示为 6 ms 与 12 ms，折算后仍对应 2 ms 与 4 ms。[pdf:E16]（PDF 物理页 14，Fig. 13）；[pdf:E11]（PDF 物理页 15，Fig. 13 讨论）

**问题 5：full-scale topology 是否比 scaled-down topology 更能预测系统行为？** → 作者把相同 snubber 参数分别用于 full-scale 和 scaled-down breaker，并用 HIL 与 PSCAD/EMTDC 比较。→ scaled-down model 产生 full-scale model 中没有的 breaker-voltage 和 line-current oscillation；反过来，把为 scaled-down model 调过的高 snubber resistance 用到 full-scale model，也会引入不合适的振荡。作者据此认为 snubber design 不能从缩比拓扑直接平移到真实阵列。[pdf:E16]（PDF 物理页 14，Fig. 14）；[pdf:E11]（PDF 物理页 15，Fig. 14 讨论）

**问题 6：器件 fidelity 会怎样影响 energy accounting？** → 作者统计 MOV、snubber 与 MB 在 RC/RCD 两种 case 中的吸能，并与 SaberRD 比较。→ MOV 始终吸收绝大部分能量，约 3.07–3.25 MJ；RCD snubber 约吸收 7.9–8.3 kJ，而 RC snubber 约为 23.1–24.0 kJ，约高三倍。Type-1 对 MB energy 的结果偏低，因为理想开关关断不准确；Type-3 最接近 SaberRD，Type-2 次之。[pdf:E16]（PDF 物理页 14，Table III）；[pdf:E11]（PDF 物理页 15，Table III 讨论）

**问题 7：模型是否能支持三端 MTDC 的故障隔离与功率重分配？** → 作者在 Line 1 施加 long-term fault，用 Type-2 full-scale HHB 做实时 HIL，并以 PSCAD/EMTDC 验证；同时运行 scaled-down HHB 作为对照。→ full-scale case 中各站约 200 kV 的直流电压在故障后下跌，约 6 ms 完成故障段隔离，之后恢复；Rectifier 与 Inverter-1 的故障电流被切断，电流在不足 100 ms 内重分配到健康的 Inverter-2。scaled-down case 则出现持续可达 100 ms 的高频 oscillation、故障电流不能立即清除和功率反复交换。[pdf:E11]（PDF 物理页 15，Fig. 15）；[pdf:E09]（PDF 物理页 16，Fig. 15 讨论）

**问题 8：硬件成本和实时性如何？** → 作者在 Virtex-7 上综合各模块并报告 latency、LUT、FF、DSP。→ HHB-1、HHB-2、HHB-3 的 nominal latency 分别为 40、38、67–125 \(T_{clk}\)；LUT 占用分别为 1.79%、1.66%、4.77%，DSP 占用分别为 0.82%、0.93%、3.79%。结合状态机迭代后，Type-1/Type-2 达到实时，Type-3 慢三倍；论文结论还声称，相较 conventional full-scale model，利用代表单元使硬件资源至少下降两个数量级。[pdf:E14]（PDF 物理页 10，Table II）；[pdf:E10]（PDF 物理页 12，Section IV 末段）；[pdf:E09]（PDF 物理页 16，Conclusion）

这些结论不能外推到所有实际 breaker。验证对象是一个三端、17-level MMC 的仿真系统、一个 5SNA 2000K450300 IGBT parameter set、一块 Virtex-7，以及特定 line-to-ground fault 和 snubber configuration；“ground truth”来自 SaberRD 与 PSCAD/EMTDC，而非带大量真实串并联器件的物理 HHB prototype。[pdf:E07]（PDF 物理页 9，Fig. 7）；[pdf:E10]（PDF 物理页 12，Section V）；[pdf:E09]（PDF 物理页 16，Appendix）

## § 8 — Take-aways

**5 句话。**（1）本文的首要贡献是把 full-scale HHB 的真实重复拓扑与 FPGA-real-time EMT 计算放进同一架构，而不是只提升某一个 IGBT 方程的精度。[pdf:E01]（PDF 物理页 1，Abstract） （2）真正的降维来自“所有单元相同、同步且内部均衡”这一对称性，因此只求一个代表 unit 和一个代表 IGBT。[pdf:E05]（PDF 物理页 4，Section III-A）；[pdf:E06]（PDF 物理页 6，Section III-C） （3）TSSM、CFM、NBM 不是简单的优劣排序，而是 system-level speed、real-time device detail 和 environmental generality 三种不同权衡。[pdf:E06]（PDF 物理页 6，Section III-C）；[pdf:E03]（PDF 物理页 7，Section III-E） （4）实验最有说服力的部分不是三种模型都能清除故障，而是 full-scale topology 与 electrothermal feedback 会改变 snubber、MB loss、LCS cooling 和 array sizing 的设计判断。[pdf:E15]（PDF 物理页 13，Fig. 11）；[pdf:E16]（PDF 物理页 14，Fig. 12、Table III）；[pdf:E11]（PDF 物理页 15，Fig. 14） （5）Type-2 是本文给出的实时折中点，Type-3 更通用但慢三倍，且所有结论仍只经过软件基准与 FPGA emulator 验证。[pdf:E10]（PDF 物理页 12，Section IV–V）

**3 句话。**（1）作者用 circuit partitioning 保留 full-scale breaker 的系统影响，同时用代表单元消除重复计算。[pdf:E05]（PDF 物理页 4，Fig. 2） （2）CFM 在实时速度下给出损耗与结温，简化 NBM 则用更高成本换取对不同 electromagnetic environment 的适应性。[pdf:E10]（PDF 物理页 12，Section V-A）；[pdf:E15]（PDF 物理页 13，Fig. 10、Fig. 11） （3）这套方法最值得记住的风险是：它对 nominal symmetric array 很强，但尚未证明能捕捉真实多器件阵列中的 worst-device stress。

**1 句话。** 这篇论文把“精确模拟全部器件”改写为“精确模拟一个被假定能代表全部器件的单元”，由此换得 full-scale topology、device-level electrothermal information 与 FPGA HIL 之间可用的工程折中。[pdf:E06]（PDF 物理页 6，Section III-C）；[pdf:E09]（PDF 物理页 16，Conclusion）

## § 9 — 最脆弱的假设

最脆弱、失败代价最大的假设是：**所有串联 HHB units 以及每个 unit 内的并联 IGBT 都相同、同步，内部节点始终良好均衡，所以一个任意 unit、一个任意并联 IGBT 和一个 thermal network 可以代表整个 breaker。** 作者在介绍 full-scale model 时明确说 MB chain 的 IGBT 被假定同步、内部节点 well balanced；随后又据此只建一个 representative unit，并让一个并联 IGBT 代表其余器件。[pdf:E05]（PDF 物理页 4，Section III-A）；[pdf:E06]（PDF 物理页 6，Section III-C）

这个假设一旦不成立，论文最重要的 design-level claim 会比 system-level claim 更早失效。论文自己的模型已经表明 IGBT 静态参数显著依赖 \(T_j\)，并用 25 °C 与 125 °C 两个 datasheet operating points 做线性插值；也就是说，只要不同 unit 的温度状态不相同，它们的阈值、导通特性和损耗就不再完全相同。[pdf:E07]（PDF 物理页 9，Section III-F）；[pdf:E14]（PDF 物理页 10，Eq. (34)、Table I）基于证据的推断是：器件参数差异、gate timing 差异、初始热状态差异或冷却不均都可能产生 differential mode（差模）应力；这些差异未必明显改变总 line current，却可能把某一个 IGBT 的 \(v_{CE}\)、loss 或 \(T_j\) 推到比代表模型预测更高的水平。

这会直接动摇“用结温决定 1×1、2×2 array 与 cooling”的结论，因为 Fig. 12 报告的是代表器件温度，而不是一个非同质阵列中的最大器件温度分布。[pdf:E16]（PDF 物理页 14，Fig. 12）论文提供的证据是：在完全对称的模型设定下，HIL、SaberRD 与 PSCAD/EMTDC 的 aggregate waveform 和代表器件 waveform 能对齐；缺少的证据是：对 unit-to-unit variation、不同初温、不同 gate delay 或单器件老化做 perturbation test，更没有真实多器件 stack 的 maximum-stress measurement。因此，这个假设对“保护逻辑可仿真”可能不是致命的，对“breaker 设计可由代表单元可靠指导”却是致命的。

## § 10 — 最小复现实验

一周内最值得复现的不是整套三端 FPGA HIL，而是本文的结构性核心 claim：**在完全对称条件下，代表单元分区模型是否与直接 full-array 求解等价，并显著减少计算。**

数据采用论文 Appendix 的系统尺度作为边界：\(U_{dc}=200\) kV、线路 200 km、总 \(V_{ref}=340\) kV、\(I_{ref}=2\) kA、\(R_s=10\ \Omega\)、\(C_s=30\ \mu\text F\)、100 个串联 HHB units，以及 25/125 °C 的 IGBT static parameter set。[pdf:E09]（PDF 物理页 16，Appendix）但论文没有公开 CFM 的完整 turn-off LUT，也没有列出所有 thermal RC、tail-current 与 nonlinear-capacitance 参数，因此一周复现应明确限定为“分区等价性与计算缩放”，不声称精确重画 Fig. 10–12。[pdf:E03]（PDF 物理页 7，CFM/NBM parameter discussion）；[pdf:E07]（PDF 物理页 9，thermal parameters 依赖 datasheet）；[pdf:E09]（PDF 物理页 16，Appendix）

实现上，用 Python、Julia 或 MATLAB 建两个离散 EMT solver。直接模型先取可计算的 8 个串联 units、每 unit 3 个并联理想 TSSM，显式保留每个 unit 的 MOV 与 snubber；分区模型则严格按 Fig. 2(d) 和 Eq. (10)–(15) 只求一个代表 unit，再按串并联比例还原总电压电流。MOV 用 Eq. (5)–(9) 的 Norton linearization，snubber 用 Eq. (10)–(11) 的 history source；\(R_{on}\)、\(R_{off}\) 可选取同一组归一化测试值，因为本实验比较的是两个 solver 在相同元件参数下的等价性，而不是拟合指定器件。[pdf:E05]（PDF 物理页 4，Fig. 2）；[pdf:E13]（PDF 物理页 5，Eq. (5)–(9)）；[pdf:E06]（PDF 物理页 6，Eq. (10)–(15)）

测量四项：line current 与 breaker voltage 的最大绝对/相对误差；各部分吸能误差；每步矩阵维数与 wall-clock time；N 从 2、4、8、16 增长时的计算缩放。支持 claim 的结果是：在完美对称条件下，直接模型与分区模型在 time-step convergence 后误差落到数值容差内，同时代表模型的求解规模基本不随 unit 数增长。反驳 claim 的结果是：即使所有器件和初始状态完全相同，两模型仍出现不可消除的波形或能量差异，或者代表模型没有显著计算收益。

这个最小实验不验证论文全部 device-level accuracy，却能在一周内直接验证其最关键的算法基础。一旦结构等价性成立，再把 Type-2 CFM 或 thermal network 加进去才有意义；若结构等价性不成立，后续更复杂器件模型只会掩盖根本问题。

## § 11 — 最强反例设计

最强反例不是再换一种 fault，也不是证明 Type-3 更慢，而是制造一个**aggregate system waveform 仍然正确、但代表单元严重漏掉 worst-device stress** 的场景。

具体做法是：在一个可直接求解的 8–10 unit 串联、每 unit 3 个并联 IGBT 的小型 full-array model 中，保持总 MOV、snubber 和线路参数不变，但让一个 unit 的初始 \(T_j\) 为 125 °C，其余 unit 为 25 °C，并使用论文 Eq. (34) 与 Table I/Appendix 中的温度相关参数更新器件静态特性；随后施加与论文相同类型的 line fault。[pdf:E14]（PDF 物理页 10，Eq. (34)、Table I）；[pdf:E09]（PDF 物理页 16，Appendix）125 °C 不是在此声称为典型现场初温，而是一个利用论文自身参数范围构造的 adversarial stress test（对抗性压力测试）。

同时运行两种模型：一是逐 unit 的 heterogeneous full-array model；二是论文式 single-representative-unit model，后者只能选 25 °C、125 °C 或某个平均温度。预先规定反例成立条件：总 line current 和 breaker voltage 的误差仍小于 2%，但代表模型对最大单器件 \(v_{CE}\)、turn-off energy 或 peak \(T_j\) 的低估超过 10%。这些百分比是实验判据，不是论文报告数字。

若出现这种结果，替代解释会非常具体：论文与 PSCAD/SaberRD 对齐的 aggregate waveform 只能证明 network-level equivalent 正确，不能证明“任意一个 unit 就能代表最危险的 unit”；而 array sizing 和 cooling guidance 恰恰取决于最大应力，不取决于平均应力。这个反例直接攻击 circuit partitioning 的对称性前提，同时允许论文的 system-level protection conclusion 继续成立，因此比泛泛地说“模型没有实物验证”更有杀伤力。

## § 12 — Follow-up Research Idea

从本文自身的评价逻辑看，本领域有影响力的研究需要同时给出 device physics fidelity、EMT numerical stability、FPGA latency/resource、system-level fault behavior 和可落实到器件选型的 design value；只提高某一条曲线的拟合精度通常不够。本文已经覆盖 nominal symmetric case 下的这些维度，但没有覆盖多器件非同质性和 worst-device guarantee。[pdf:E14]（PDF 物理页 10，Table II）；[pdf:E16]（PDF 物理页 14，Fig. 12、Table III）；[pdf:E09]（PDF 物理页 16，Conclusion）

候选研究方向是：**面向非同质阵列的 common-mode + differential-mode electrothermal envelope HIL**。它不再把目标定义为“重现一个代表 IGBT 的 nominal waveform”，而是“在不逐个模拟全部器件的前提下，实时给出 breaker 总体暂态以及所有器件最大电压、最大损耗和最大结温的可信 envelope（包络）”。由于本任务只使用源 PDF、未检索包外相关工作，这里明确把它标为候选想法，不声称 novelty。

（a）**未满足需求。** 真实设计需要的是最危险器件是否越界，而本文的单 unit/单 thermal network 只能给 nominal representative state；只要 temperature-dependent parameter 使单元失配，平均波形正确也可能掩盖局部过应力。[pdf:E06]（PDF 物理页 6，代表单元假设）；[pdf:E14]（PDF 物理页 10，Eq. (34)）

（b）**潜在研究价值。** 若模型能以接近 Type-2 的实时成本同时输出 system waveform 和 worst-device bounds，它会把 HIL 从 control/protection test 扩展到 tolerance-aware breaker design、cooling design 和在线 health margin evaluation。这改变了研究目标，而不是在现有模型后再加一个温度模块。

（c）**可借鉴的相邻方法。** 可以把完全对称阵列分解为一个 common mode 与少量 differential modes，并结合 reduced-order modeling、uncertainty propagation 和 event-triggered refinement：正常时只推进 common mode 和几个“sentinel units（哨兵单元）”，检测到电压或温度分散增大时再动态增加 differential states。FPGA 上仍保留模块级 parallelism，但计算资源按不平衡程度分配，而不是按物理器件数固定增长。

（d）**第一个证伪实验。** 用一个可直接求解的 heterogeneous small-array NBM/CFM model 作为 reference，在初温、阈值、gate delay 和 thermal resistance 上施加有界扰动；要求候选模型对 maximum \(v_{CE}\)、maximum turn-off energy 和 maximum \(T_j\) 的误差不超过预设 5%，同时每步执行时间不超过本文 Type-2 路径的两倍。若包络漏掉任何 reference maximum，或为了不漏而退化到逐器件求解，则该想法被证伪。5% 与两倍都是研究设计阈值，不是论文原始结果。

（e）**与本文的实质区别。** 本文用 symmetry 消除 differential states，输出一个 nominal representative device；候选方法把 differential states 本身视为研究对象，目标是给出 non-identical array 的 stress envelope。它不是 Type-4 IGBT model，也不是把本文移植到另一种 HVDC topology，而是把问题从“实时重现名义行为”改成“实时保证最坏器件行为不被降阶模型漏掉”。
