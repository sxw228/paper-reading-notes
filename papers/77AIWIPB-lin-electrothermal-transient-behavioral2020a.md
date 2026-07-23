# Electrothermal Transient Behavioral Modeling of Thyristor-Based Ultrafast Mechatronic Circuit Breaker for Real-Time DC Grid Emulation

- 作者：Ning Lin；Venkata Dinavahi
- 出处：IEEE Transactions on Industrial Electronics, 67(3), 1660–1670
- 年份：2020
- DOI：10.1109/TIE.2019.2905824
- Zotero key：77AIWIPB

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是“直流断路器能不能动作”这一单一问题，而是：能否把一个由大量串联晶闸管、MOV、机械隔离开关和换流支路组成的 ultrafast mechatronic circuit breaker（UFMCB）做成 **2 μs 步长的 FPGA 实时模型**，同时保留器件级的导通压降、反向恢复、功耗与结温，使同一台仿真器既能评估断路器选型，又能研究它与多端 MMC-HVdc 电网的故障交互。作者指出，理想开关只能告诉我们“通或断”，不能回答某一型号晶闸管是否过热、MOV 与电弧如何改变换流过程，也无法给出可靠的器件容量设计依据；而直接堆叠详细器件模型又会造成节点数和非线性求解量爆炸。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

物理上，直流侧故障没有自然过零点，电流会在很短时间内上升。HBSM-MMC 即使封锁 IGBT，续流二极管仍可能向故障馈能，因此必须让断路器或具有直流故障阻断能力的换流器快速接管能量路径。论文把这个问题放进四端混合 MMC 直流网：两个整流站采用 HBSM，需要 UFMCB；两个逆变站采用可阻断故障的 CDSM。这样，研究对象从孤立的开关器件上升为“器件温度—断路器换流—电网功率恢复”的一条完整因果链。[pdf:E06]（PDF 物理页 6，Fig. 6–8 与 Section IV-B）

工程价值有两层。第一，若结温模型可信，就可以用实际故障与重合闸工况选择不过度裕量的晶闸管，降低样机成本。第二，若模型能在硬实时 deadline 内运行，就可以把外部控制保护器接入 HIL，观察控制命令与虚拟一次系统之间的闭环行为。论文在 Xilinx UltraScale+ VU9P 上给出的 RSNR 方案总延迟为 177 个时钟周期，并据此采用 2 μs 仿真步长；作为对比，原 Gaussian elimination 求解器总延迟为 756 个时钟周期、对应约 8 μs 步长。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E07]（PDF 物理页 7，Section V）

## § 2 — 前人工作与不足

以下是论文对当时相关工作的归纳，而不是本卡重新完成的独立文献检索。作者认为，已有 hybrid HVdc breaker、机械式和固态式断路器分别在开断速度、损耗、容量与成本之间做权衡；UFMCB 已有高压大电流试验和系统级设计方法，但此前主要在简单系统中验证，尚不足以研究它在 MMC 多端直流网中的复杂电磁交互。与此同时，器件级电热模型在小规模离线仿真器中可用，但把几十个甚至更多非线性器件与电网一起用小步长求解，会使处理器仿真极慢。[pdf:E01]（PDF 物理页 1，Introduction）

已有理想开关或固定 ON/OFF 电阻模型的根本不足，是把器件损耗当成一个人为设定量。论文后面的对比显示，PSCAD/EMTDC 理想晶闸管的不同导通电阻会给出明显不同的功耗，而详细模型与 ANSYS/Simplorer 的器件电流波形更接近；因此，若目标是器件选型，固定电阻不是“精度略低”，而是可能改变温升判断。[pdf:E08]（PDF 物理页 8，Fig. 11 及其相邻正文）

已有并行实时模型也不能直接照搬。论文提到，先前 FPGA 上的 full-scale hybrid breaker 利用了拓扑高度对称性做内部电路分区；本文的 UFMCB 拓扑不规则，内部直接分区困难。作者因此改变分区边界：不强行切开断路器内部，而是先用一对耦合电压—电流源把整个 UFMCB 与直流电网分开，再在五节点 UFMCB 内把矩阵求解改写成逐节点 scalar iteration。[pdf:E02]（PDF 物理页 2，Introduction 末段）[pdf:E03]（PDF 物理页 3，Fig. 3 与 Section III-A）

在 MMC 一侧，作者也拒绝用 average value model 代替完整开关模型，因为论文引用的既有结论认为平均模型在直流故障问题上精度不足；但完整 MMC 节点太多，故采用 transmission-line model link（TLM-link）把 submodule 与 arm 解耦。这里的关键不足不是模型“复杂”，而是复杂模型若没有适合 FPGA 的计算依赖图，就无法在实时 deadline 内完成。[pdf:E05]（PDF 物理页 5，Section IV-A）[pdf:E06]（PDF 物理页 6，Fig. 7 与 Eq. 26–27）

## § 3 — 重建作者的思考路径

可以把作者的推理重建为六步。

1. **先从设计问题出发。** UFMCB 的主功率器件是串联晶闸管。样机是否安全，取决于故障开断、正常导通和电弧换流期间的瞬时损耗与结温，而不只取决于端口电压电流。因此必须保留 static I–V、reverse recovery 和 transient thermal impedance。[pdf:E02]（PDF 物理页 2，Fig. 1 与 Section II-A）
2. **再识别规模瓶颈。** 单个详细晶闸管模型有多个内部节点；高压应用必须大量串联或并联，直接复制会同时增加节点数、硬件资源和非线性迭代负担。于是把反向恢复支路用受控源分离，把 NLD 与 SCR logic 合并，形成代表一串器件的 scalable model。[pdf:E02]（PDF 物理页 2，Section II-B）
3. **把电热反馈做成离散时域递推。** 每一步由端电压、电流算损耗，再通过五级 R–C 热网络算结温，最后用新温度更新下一步的 I–V 参数。这样，电学状态推动温度，温度又反馈导通特性，形成可流水化的因果环。[pdf:E03]（PDF 物理页 3，Eq. 5–8）
4. **寻找物理上可接受的系统分区。** 平波电感使端口电流变化相对缓慢，作者据此用耦合源把 UFMCB 从直流网切开，让 breaker 与 grid 可以并行推进，而不是在一个更大的矩阵中一起消元。[pdf:E03]（PDF 物理页 3，Fig. 3 与相邻正文）[pdf:E10]（PDF 物理页 10，Conclusion）
5. **把不适合 FPGA 的矩阵求解改成局部更新。** 五节点 UFMCB 的完整 admittance matrix 每次 nonlinear iteration 都变化，反复 Gaussian elimination 延迟高。若暂用上一轮相邻节点电压，就能逐节点计算本节点电压，五个 scalar equation 可以并行执行，这就是 RSNR 的来源。[pdf:E05]（PDF 物理页 5，Eq. 22–25 与 Fig. 5）
6. **用两级参照验证。** 器件电流、功耗和结温对照 ANSYS/Simplorer；电网侧波形对照 PSCAD/EMTDC。这样分别覆盖“器件模型有没有物理细节”和“系统故障响应有没有走样”，再把设计映射到 FPGA 的 FSM 与固定迭代预算。[pdf:E07]（PDF 物理页 7，Section VI 开头与 Fig. 9–10）

这条路径的重要之处在于：作者不是先写一个 FPGA solver 再寻找应用，而是从 UFMCB 设计所需的可观测量出发，逐层删掉不会改变目标物理量、却会增加实时延迟的内部节点和全局依赖。

## § 4 — 核心 Intuition

核心 intuition 是：**保留器件端口的非线性电热行为，但不要保留所有内部节点；保留网络耦合的物理作用，但不要让所有子系统在同一矩阵里串行求解。** 串联晶闸管先被压缩成 scalable behavioral model，整个 UFMCB 再通过耦合源与电网分离，最后用上一轮邻居电压把五维 nonlinear nodal solve 改成可并行的五个 scalar update。[pdf:E02]（PDF 物理页 2，Fig. 1）[pdf:E03]（PDF 物理页 3，Fig. 3）[pdf:E05]（PDF 物理页 5，Fig. 4–5）

它能奏效的物理前提是 breaker 端口状态不会在一个迭代周期内剧烈到使“上一轮邻居电压”失去代表性；它能在 FPGA 上奏效的计算前提是各器件 companion model 与各节点 update 可并行流水，而迭代次数可用一个很小的固定上界覆盖。[pdf:E07]（PDF 物理页 7，Fig. 9–10 与相邻正文）

## § 5 — 具体方法与完整 Pipeline

以论文的 120 kV 单断路器故障试验为例，输入是直流源、80 Ω 负载、100 mH 平波电感、UFMCB 各器件参数、门极与保护命令；输出既有断路器端口电压电流，也有每组 SCR 的电流、功耗和结温。完整 pipeline 如下。

1. **晶闸管电气层。** 用温度相关系数 \(A,B,C,D\) 构造 ON-state \(v_{AK}(i_{AK})\)，再由 \(G_{AK}=i_{AK}/v_{AK}\) 得到 nonlinear conductance；SCR logic 根据正向电压、门极脉冲、零电流和 turn-off time \(t_q\) 决定通断。反向恢复由 \(R_r-L_r\) 支路及受控电流源表示。[pdf:E02]（PDF 物理页 2，Eq. 1–3 与 Fig. 1）
2. **可扩展串联层。** 60 个串联 5STF 28H2060 不被展开成 60 份四节点模型。作者把 NLD 与 SCR logic 合并、把小参数 reverse-recovery branch 通过 VCCS 分离，使一串器件对外仍呈现所需的 static 与 recovery 行为，却显著减少内部节点。[pdf:E02]（PDF 物理页 2，Section II-B）[pdf:E07]（PDF 物理页 7，试验设置）
3. **电热递推层。** 每个 2 μs time-step 用 trapezoidal rule 由 \(v_{AK}i_{AK}\) 计算损耗；五级 thermal R–C companion network 接收该功耗，输出 junction temperature \(T_{vj}\)，再更新下一步的温度敏感系数。论文明确不为 UFMCB 配外部冷却系统，热模型使用器件固有 transient thermal impedance。[pdf:E03]（PDF 物理页 3，Eq. 5–8 与 Section II-C）
4. **UFMCB 元件层。** LCS 的 IGBT static I–V 被按温度做 piecewise linear representation；MOV 的强 nonlinear I–V 被分成 11 段；UFD 可用 ideal switch，也可用 Mayr arc model，其状态变量是 \(\ln g\)，其中 \(g\) 是 arc conductance，\(\tau_M\) 与 \(P_M\) 分别控制弧的时间尺度和 cooling power。[pdf:E04]（PDF 物理页 4，Eq. 9–19）
5. **断路器—电网接口层。** 耦合电压源 \(V_p\) 把 UFMCB 对直流电网的压降反馈给网侧，耦合电流源 \(J_s\) 把线路电流送给 breaker 侧。这样 breaker 与 grid 可并行求解；没有 breaker 时令 \(V_p=0\)，原网侧拓扑不需重构。[pdf:E03]（PDF 物理页 3，Fig. 3）[pdf:E04]（PDF 物理页 4，Section III-A 开头）
6. **RSNR 求解层。** 每轮先更新 SCR、MOV、MB 的 companion parameters，再由上一轮相邻节点电压求五个节点的当前值；达到 convergence threshold 即停止。硬件实现为固定三轮，以覆盖论文试验观察到的最多三轮迭代。[pdf:E05]（PDF 物理页 5，Eq. 21–25）[pdf:E07]（PDF 物理页 7，Fig. 10 与相邻正文）
7. **MMC 与系统层。** CDSM/HBSM submodules 通过 TLM-links 从 arm 中解耦，arm 侧形成 Norton companion model。四端网在 STN1 附近施加 pole-to-pole fault：CDSM 站自阻断，HBSM 站由 UFMCB 隔离故障，以观察健康端口能否继续供电。[pdf:E06]（PDF 物理页 6，Fig. 6–8 与 Eq. 26–27）
8. **FPGA 映射与输出。** SCR、MOV、MB、Solver2 和 Update 各自成为 Vivado HLS module，中间用 D-latch 和 data-valid 信号传递；FSM 协调 parallel module、三轮 N–R 与 state update。论文给出的整机资源占用为 10,268 LUT、5,241 FF、84 DSP，分别约占器件可用量的 0.87%、0.22%、1.23%。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E07]（PDF 物理页 7，Fig. 9–10）

## § 6 — 核心数学推导

### 6.1 从器件曲线到可求解的 companion conductance

作者先用

\[
v_{AK}=A+B i_{AK}+C\sqrt{i_{AK}}+D\ln(i_{AK}+1)
\]

拟合晶闸管导通态 static I–V，再定义

\[
G_{AK}(i_{AK})=\frac{i_{AK}}{v_{AK}(i_{AK})}.
\]

物理意义是：保留真实器件“电流越大，压降与损耗并非常数”的性质，但对网络求解器仍暴露成一个每步可更新的 conductance。\(A,B,C,D\) 随温度变化，论文以 25 °C 与 125 °C 的 datasheet/I–V curve 做线性插值。[pdf:E02]（PDF 物理页 2，Eq. 1–2）

### 6.2 从电功率到结温

一个 time-step 内，作者把损耗积分用二阶 trapezoidal rule 离散。因为令 \(T-T_0=\Delta t\)、\(N_t=1\)，核心就是用步首与步末的 \(v_{AK}i_{AK}\) 平均值表示该步平均功耗。随后用五个串联 R–C 支路拟合

\[
Z_{\mathrm{th}}(t)=\sum_{i=1}^{5}R_{\mathrm{th}(i)}\,\left(1-e^{-t/\tau_i}\right),
\]

其中每一项都是热阻与括号内 transient factor 的乘积。作者再由 \(C_{\mathrm{th}(i)}=\tau_i/R_{\mathrm{th}(i)}\) 建立 thermal companion model。每个热电容的 history current 保存过去热量，五支路合成得到 \(T_{vj}\)，再反馈下一步器件参数。[pdf:E03]（PDF 物理页 3，Eq. 5–8）

这相当于把热扩散写成一个“有记忆的电路”：功耗是注入电流，温度是节点电压，热阻和热容决定热量释放速度。它避免求解三维热场，但保留了多时间常数温升。

### 6.3 从五维 nonlinear matrix 到五个 scalar update

传统 N–R 每轮需求解

\[
\mathbf U^k=(\mathbf G^{-1})^k\mathbf J^k.
\]

若 \(\mathbf G\) 随 nonlinear elements 每轮改变，就必须反复 factorization。作者从矩阵第 \(i\) 行直接隔离出

\[
U_i^k=(G_{ii}^k)^{-1}
\left(J_{\mathrm{eq}i}^k-\sum_{j\ne i}G_{ij}^kU_j^k\right).
\]

真正让它可并行的是下一步近似：把未知的本轮邻居 \(U_j^k\) 换成上一轮 \(U_j^{k-1}\) 加 successive-iteration error \(\xi_j\)。随着迭代推进，\(\xi_j\) 变小，直到相对变化满足 Eq. 21 的 threshold。它与 Jacobi iteration 的形式相似，但 \(J_{\mathrm{eq}i},G_{ii},G_{ij}\) 也会随 nonlinear state 更新，所以作者称之为 relaxed scalar Newton–Raphson。[pdf:E05]（PDF 物理页 5，Eq. 21–25）

工程直觉是：用“多做几轮便宜的并行 scalar calculation”换掉“一轮昂贵的 matrix elimination”。在论文的五节点模型与测试工况中，作者观察到最多三轮迭代，因此硬件 FSM 固定执行三轮；这是一项实测设计选择，不是论文给出的普适 convergence theorem。[pdf:E07]（PDF 物理页 7，Fig. 10 与相邻正文）

### 6.4 MMC 侧的 TLM decoupling

MMC submodule 与 arm 通过 characteristic impedance \(Z_0\) 的 TLM-link 交换 history source。arm conductance 写为

\[
G_{\mathrm{arm}}=(N_LZ_0+Z_{L_{u,d}})^{-1},
\]

相应 history voltage 汇总成 Norton current source \(J_{\mathrm{arm}}\)。物理上，每个 submodule 不再等待整条 arm 同步求解；计算依赖通过一个 time-step 的历史量切断，从而获得并行度，但也把 decoupling accuracy 与所选步长、接口参数联系起来。[pdf:E06]（PDF 物理页 6，Eq. 26–27 与 Fig. 7）

## § 7 — 实验设计与结论

### 问题 1：单个 behavioral thyristor 是否保留导通逻辑与 reverse recovery？

**实验：** 在 ±200 V、60 Hz 电源和 100 Hz gate pulse 的测试电路中，把提出的模型与 ANSYS/Simplorer detailed physics-based model 对比。  
**答案：** 两者的导通与 reverse-recovery waveforms 视觉上高度重合；在 gate 为正但 anode voltage 为负的 P2 时刻，SCR 保持 OFF，说明门极逻辑没有把反向偏置器件错误触发。论文没有报告 waveform error norm，只给图形对齐，因此证据支持“行为相符”，不支持一个未给出的百分比精度。[pdf:E03]（PDF 物理页 3，Fig. 2）

### 问题 2：RSNR 是否真的换来硬实时速度与低资源占用？

**实验：** 在 VU9P 上综合原 Gaussian elimination solver 与 RSNR solver。  
**答案：** Solver latency 从 242 降到 49 cycles，UFMCB 总 latency 从 756 降到 177 cycles；对应可用 time-step 从约 8 μs 缩短到 2 μs，作者称为 four-times speedup。RSNR 整机占 10,268 LUT、5,241 FF、84 DSP，均低于可用资源的 1.3%。这验证了 hardware timing/resource claim，但论文没有给出不同规模节点数下的 scaling curve。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E07]（PDF 物理页 7，Section V）

### 问题 3：详细器件模型是否改变断路器设计判断？

**实验：** 120 kV 直流源经 100 mH 电感、80 Ω 负载和 UFMCB 供电；100 ms 时发生 1 Ω line-to-ground fault，50 μs 后触发保护，每个 SCR symbol 代表 60 个串联 5STF 28H2060。将 HIL 与 ANSYS/Simplorer、PSCAD/EMTDC 对比。  
**答案：** MOV \(M_2\) 的 protection voltage 约 170 kV，最终把约 4.4 kA fault current 降到零；详细模型与 Simplorer 的 SCR current 相符，而 PSCAD ideal SCR 的功耗依赖人为 ON resistance。用 5STF 28H2060 时最高结温约 27 °C；容量更小、成本更低的 5STF 05D2425 最高约 41 °C，作者据此认为后者在该额定场景仍有裕量、更加合适。这里的“更合适”只对论文测试的电压、功率和热边界成立。[pdf:E07]（PDF 物理页 7，Section VI-A 的试验设置）[pdf:E08]（PDF 物理页 8，Fig. 11–12 与相邻正文）

### 问题 4：UFD arc model 会不会影响 SCR stress？

**实验：** 比较 ideal UFD、\(P_M=1000\) kW 和 \(P_M=100\) kW 的 Mayr arc 参数。  
**答案：** 1000 kW case 与 ideal switch 的 SCR current 几乎相同；100 kW 时 arc duration 更长，102–102.5 ms 间电流被转移到 UFD–\(M_0\) path，SCR1 结温约 35 °C，而 ideal/1000 kW case 超过 40 °C。这说明一个“更真实”的 arc 并不只是修饰波形，它会改变器件 thermal stress 分配。[pdf:E09]（PDF 物理页 9，Fig. 14 与相邻正文）

### 问题 5：UFMCB 与 CDSM-MMC 的联合保护能否在四端网中隔离故障并维持健康端供电？

**实验：** 四端网初始各端约 ±2 kA、约 200 kV，两个整流站各输出约 400 MW；5 s 时在 STN1 附近施加 pole-to-pole fault。STN1 的 CDSM-MMC blocking，STN2 的 UFMCB 动作，HIL 对照 PSCAD/EMTDC。  
**答案：** STN1 侧 \(V_{dc1}\) 与 \(I_{dc1}\) 降至零，STN2 未被迫 blocking，功率恢复并经 interlink 支援健康端。作者正文称 STN3 接收功率加倍至“about 800 MW”，但 Fig. 15 在展示时刻标出的 HIL/PSCAD 数值约为 639/647 MW；这可能反映暂态、损耗或读图时刻差异，论文没有进一步解释，因此本卡不把“800 MW”当成已闭合的精确 validation value。[pdf:E09]（PDF 物理页 9，Fig. 15 与相邻正文）

### 问题 6：永久故障下重合闸逻辑是否可观察？

**实验：** 在 UFMCB 开断后，160 ms later 尝试 reclosure。  
**答案：** \(M_2\) 在开断期间维持接近 290 kV，令电流过零；由于故障仍存在，重合后又发生一次开断。HIL 与 PSCAD/EMTDC 的主要趋势相符，说明模型能把 protection sequence 和一次电路响应放在同一实时执行中。[pdf:E10]（PDF 物理页 10，Fig. 16 与相邻正文）

总体而言，实验支持“器件级波形可对照、硬件 deadline 可满足、系统级故障趋势可对照”三项 claim；但验证以 waveform visual agreement 为主，缺少统一误差指标、convergence margin 和参数空间覆盖。因此不能从这些实验外推到所有 UFMCB rating、所有 MMC 拓扑或所有 fault stiffness。

## § 8 — Take-aways

### 5 句话

1. 这篇论文把 UFMCB 的价值从“快速切断电流”扩展到“实时观察每组晶闸管的损耗和结温”，因此能直接服务器件选型。[pdf:E01]（PDF 物理页 1，Abstract）
2. 它通过 scalable thyristor model 删除串联器件的内部节点，却保留 static I–V、reverse recovery 与 thermal memory。[pdf:E02]（PDF 物理页 2，Fig. 1）[pdf:E03]（PDF 物理页 3，Eq. 4–8）
3. 它通过耦合源、TLM-link 和 RSNR，把原本全局串行的 nonlinear matrix problem 改造成 FPGA 可并行的局部递推。[pdf:E03]（PDF 物理页 3，Fig. 3）[pdf:E05]（PDF 物理页 5，Eq. 22–25）[pdf:E06]（PDF 物理页 6，Fig. 7）
4. 在论文给定硬件与测试系统上，RSNR 把总 latency 从 756 cycles 降至 177 cycles，使 2 μs time-step 成为可能。[pdf:E06]（PDF 物理页 6，Table I）[pdf:E07]（PDF 物理页 7，Section V）
5. 最大证据缺口不是“波形完全不对”，而是没有以数值误差和 worst-case convergence sweep 证明固定三轮 RSNR 在更强耦合、更快电流变化和更多参数组合下仍可靠。

### 3 句话

1. 物理上，它用电热 behavioral model 把开断波形连接到器件温度与容量选择。  
2. 计算上，它用 node elimination 与 delayed/local coupling 把复杂度换成可控的迭代误差和并行度。  
3. 证据上，它在特定单断路器与四端网工况中成立，但普适稳定性仍是开放问题。

### 1 句话

这是一项把“足够详细的器件物理”压缩成“能在 FPGA deadline 内运行的网络接口”的工作，其真正边界取决于 decoupling 与三轮 RSNR 在最坏故障下是否仍收敛。

## § 9 — 最脆弱的假设

最脆弱的假设是：**平波电感和所选 2 μs 步长足以限制端口状态变化，使耦合源/TLM 使用的历史量与 RSNR 使用的上一轮邻居电压保持“足够新”，并且五节点 nonlinear solve 总能在固定三轮内收敛到不会改变保护与温升判断的精度。**

这个假设一旦失效，论文的核心贡献会同时从两边受损：如果增加迭代数，可能错过 real-time deadline；如果仍固定三轮，node voltage、MOV segment、SCR current 和 loss 会产生连锁误差，最终让结温与开断时刻失真。危险工况包括更小的 smoothing inductance、更低 fault resistance、更陡的 current rise、MOV segment boundary 附近的强 nonlinear switching、UFD arc 突变，以及 breaker 与 converter control 同时改变拓扑。

论文给出的支持证据是：测试系统使用 100 mH 电感，作者观察到最多三轮迭代；在这些工况中，HIL 与 ANSYS/Simplorer 或 PSCAD/EMTDC 的波形趋势相符，并且 FSM 的 177-cycle latency 满足 2 μs step。[pdf:E07]（PDF 物理页 7，试验设置、Fig. 10 与相邻正文）[pdf:E08]（PDF 物理页 8，Fig. 11–12）[pdf:E09]（PDF 物理页 9，Fig. 15）

缺失的证据是 convergence theorem、每步 residual trace、maximum error bound、不同 \(L_{dc}\)/fault resistance/operating point 的 sweep，以及“第三轮尚未收敛时硬件如何处置”的 fail-safe。Appendix 给出了单一四端网与器件参数集，但没有覆盖参数空间。[pdf:E10]（PDF 物理页 10，Appendix）因此，本卡把“固定三轮在广泛系统中可靠”视为尚未证实的外推，而不是论文已证明的事实。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重建完整四端 MMC，而是复现 **五节点 UFMCB 的 RSNR 与一个 monolithic reference solver 的逐步对照**。

### 数据与实现

- 从 Appendix 录入 UFMCB、UFD 和两类 ABB thyristor parameters；先用论文的 120 kV、80 Ω、100 mH、1 Ω fault 和 60 串联 SCR test case。[pdf:E07]（PDF 物理页 7，Section VI-A）[pdf:E10]（PDF 物理页 10，Appendix）
- 实现相同的 SCR static I–V、reverse recovery、thermal R–C、11-segment MOV、Mayr UFD 和五节点 Norton companion network。
- 同一 time-step 同时运行两条 solver：A 为完整 nonlinear Newton–Raphson/矩阵求解，收敛到严格 residual；B 为论文 RSNR，固定三轮。
- 先复现 \(L_{dc}=100\) mH，再扫描 50、20、10、5 mH；fault resistance 扫描 1、0.5、0.1 Ω，并把故障起始时刻放在不同 MOV segment 与 SCR commutation phase。

### 测量

逐步记录五个 node voltages、各 SCR currents、\(M_2\) voltage、solver residual、iteration count、fault clearing time、每步 energy loss 与 peak junction temperature。若有 FPGA，只需把 RSNR kernel 综合并测 cycles；没有 FPGA 时，先用 dependency graph 推导 critical path，仍可验证数值 claim。

### 预注册判据

以下是复现实验建议阈值，不是论文报告的阈值：在原始 100 mH case 中，RSNR 相对 reference 的 node-voltage/current normalized RMSE 不高于 1%，fault clearing time 不差超过一个 2 μs step，peak junction temperature 不差超过 1 °C，且每步第三轮 residual 均低于预设 \(10^{-6}\) relative threshold。满足这些条件，并重现 177-cycle architecture，算支持论文核心 claim；任何原始 case 中的明显越界都直接反驳。

stress sweep 不要求所有点都通过，但必须画出“最小电感/最低故障电阻—需要迭代数—误差—deadline”的边界。如果论文固定三轮在现实可达参数点出现未收敛，且误差改变器件选型或保护动作，就是对其可推广性的强反证。

## § 11 — 最强反例设计

最强反例是制造一个 **接口变化快、nonlinear segment 同时切换、固定三轮恰好来不及追上** 的故障，而不是泛泛地说“模型可能不准”。

具体做法是把 \(L_{dc}\) 从论文的 100 mH 逐步减小，在低 fault resistance 下令故障恰好发生于主支路换流、UFD arc conductance 快速变化和 \(M_2\) 进入高斜率 piecewise segment 的同一窗口。对同一输入运行：

1. 不分区的 monolithic implicit reference；
2. 保留耦合源但将 RSNR 迭代到严格收敛；
3. 论文的 fixed-three-iteration RSNR。

若第 2 条与 reference 接近、而第 3 条出现 residual 累积、错误的 MOV segment、SCR current peak 偏移或 fault clearing time 改变，就能把失败明确归因于固定 iteration budget；若第 2 条本身也偏离，则反例击中耦合源/TLM 的 history-based decoupling，而不是 RSNR 实现细节。

最有杀伤力的判据不是单点电压误差，而是决策翻转：reference 判定 5STF 05D2425 超过 thermal margin，而论文模型仍判定安全；或 reference 判定保护未在 deadline 内清除，而论文模型判定成功。因为论文的目标正是器件选型与实时保护测试，这类反例会直接否定核心用途。该反例的事实前提来自论文明确依赖的平波电感分区、三轮 RSNR、MOV/UFD nonlinear model 与结温反馈。[pdf:E03]（PDF 物理页 3，Fig. 3）[pdf:E04]（PDF 物理页 4，Eq. 10–19）[pdf:E07]（PDF 物理页 7，Fig. 10）[pdf:E08]（PDF 物理页 8，器件选型结论）

## § 12 — Follow-up Research Idea

在电力电子实时仿真与 HIL 领域，高影响工作通常不仅要展示更小步长或更多器件，还要同时给出：对关键 switching transient 的可信度、最坏情况下的 real-time guarantee、可复现的硬件资源/latency，以及对真实控制保护测试或设备设计的直接价值。本文已覆盖 latency、device/system cross-tool comparison 和一个设计案例，但没有闭合“参数变化后 fixed iteration 是否仍可信”的保证。

因此可以提出一个候选方向：**把 fixed-three-iteration HIL emulator 改造成带在线误差证书的 deadline-aware electrothermal co-simulation。** 它不把目标定义为“平均更快”，而定义为：每个 time-step 都必须在 deadline 前给出一个带 residual/error bound 的结果；如果当前耦合过强，系统应在预先综合好的多级 kernel 中切换 iteration budget、局部合并 partition，或显式标记该步不具备设计判据资格。

### (a) 未满足的需求

工程师使用 HIL 做器件选型时，需要知道“这个温度值可信到什么范围”，而不是只知道仿真没有超时。论文的固定三轮在已测场景有效，但没有说明何时失效，也没有 fail-closed signal。

### (b) 可能的研究价值

若能在 FPGA 上同时保证 deadline 与 error envelope，就能把实时仿真从 waveform generator 提升为可用于 protection/thermal decision 的 certified instrument。价值不来自再快 20%，而来自把“实时性—数值可信度”从隐含 trade-off 变成可观测、可验证的 contract。

### (c) 可借鉴的相邻领域

可以借鉴 waveform relaxation 的 a posteriori residual estimation、hybrid-systems 的 event localization、real-time scheduling 的 mixed-criticality budget，以及 numerical linear algebra 中 asynchronous/Jacobi convergence monitor。关键是把这些方法压缩成固定资源、bounded latency 的 hardware primitive，而不是在 CPU 上事后检查。

### (d) 第一个可证伪实验

用 §11 的二维或三维 stress sweep，要求系统在每个参数点输出 error bound；再与 monolithic reference 的真实误差比较。若证书频繁低估误差，或为了保持可信不得不超过 2 μs deadline，这个方向的核心设想就被证伪。

### (e) 与已有工作的实质区别

本文的贡献是通过固定分区和固定三轮 RSNR 达成一个已验证工况下的 2 μs execution；候选工作把问题改写为“在 topology event 和参数漂移下，实时执行结果何时仍可作为设计证据”。本卡没有对该方向做系统相关工作检索，因此它只是由本文证据缺口驱动的候选研究想法，**不声称 novelty**。
