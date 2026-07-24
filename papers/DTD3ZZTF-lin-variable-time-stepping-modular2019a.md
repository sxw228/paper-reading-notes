# Variable Time-Stepping Modular Multilevel Converter Model for Fast and Parallel Transient Simulation of Multiterminal DC Grid

**作者：** Ning Lin；Venkata Dinavahi  
**出处：** IEEE Transactions on Industrial Electronics, Vol. 66, No. 9, September 2019, pp. 6661-6670  
**年份：** 2019  
**DOI：** 10.1109/TIE.2018.2880671  
**Zotero key：** DTD3ZZTF  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文解决的是一个明确的工程矛盾：多端直流电网（multiterminal DC grid, MTDC）的电磁暂态（electromagnetic transient, EMT）仿真既要覆盖系统级网络动态，又希望保留模块化多电平换流器（modular multilevel converter, MMC）内部 IGBT/diode 的开通、关断、反向恢复、损耗和结温等 device-level 细节；但系统规模和模型精度一旦同时增加，固定小步长和非线性迭代会让 CPU 仿真代价迅速失控。作者的直接主张是：把 variable time-stepping（VTS，可变步长）、MMC circuit partitioning（电路分割）和 GPU 大规模并行结合起来，可以使带非线性开关模型的 MTDC 系统级 EMT 仿真变得可行。[pdf:E01]（PDF 物理页 1，Abstract）

重要性不只是“跑得更快”。传统 two-state switch model（TSSM，两状态开关模型）或 average value model（平均值模型）会丢失器件级行为；在直流故障等工况下，忽略 freewheeling diode（续流二极管）或使用不合适的理想开关阻抗会直接改变故障电流。相反，详细 IGBT/diode 模型需要小步长下反复 Newton-Raphson（N-R，牛顿-拉夫逊）迭代，而且器件数量增加时容易出现数值发散。[pdf:E02]（PDF 物理页 1，Introduction 右栏）因此，这项工作的价值是把“系统范围”和“器件保真度”放进同一次仿真，而不是在两者之间被迫二选一。

## § 2 — 前人工作与不足

**论文原文对 prior work 的归纳。** 第一类是 EMT 工具中常见的 TSSM，以及把一条桥臂全部子模块合并的 detailed equivalent model、average value model 及其变体。它们已经能够支持较高层级的 MMC/HVDC 系统研究，但作者指出，在直流线路故障等场景中，模型可能因忽略续流二极管或缺乏合适的开关阻抗而损失准确性。[pdf:E02]（PDF 物理页 1，Introduction 右栏）第二类是器件级非线性 IGBT/diode 模型，它们能输出电压、电流、损耗和热信息，但高阶非线性要求小步长 N-R 迭代，难以直接扩展到系统级 MTDC。[pdf:E02]（PDF 物理页 1，Introduction 右栏）

第三类是既有 VTS 方法。论文引言称，VTS 已在若干相对小的系统中使用，但尚未探索它在带 device-level 细节的大型非线性 MTDC 中的应用。[pdf:E02]（PDF 物理页 1，Introduction 右栏）作者进一步把现有步长判据分为 event-correlated criterion（事件相关判据）、local truncation error（LTE，局部截断误差）和 N-R iteration count（迭代次数）：前两种可用于更一般的线性或非线性系统，第三种专门利用非线性求解器的收敛负担来判断当前动态强度。[pdf:E03]（PDF 物理页 2，Section II-A/B）[pdf:E04]（PDF 物理页 2，Section II-C，Eq. (7)-(8)）

不足不在于单个技术完全不可用，而在于它们没有形成闭环：详细模型缺少可扩展的时间推进和计算架构；VTS 缺少面向大量非线性 MMC 子模块的组织方式；GPU 并行又需要足够多、足够规则且彼此弱耦合的任务。论文的工作是把这三个缺口同时对齐，而不是只提出一个新的 time-step controller。

## § 3 — 重建作者的思考路径

下面是**基于证据的重建**，不是作者逐字给出的研发日志。

第一步，先观察 EMT 轨迹的信息密度并不恒定：稳态阶段波形变化缓慢，开关瞬态、断路器动作和线路故障阶段变化剧烈，因此全程使用最小固定步长会把大量算力花在“没有新信息”的区间。于是可以分别用电压/电流变化率、LTE 或 N-R 迭代次数判断当前阶段是否需要密集采样。[pdf:E03]（PDF 物理页 2，Section II-A/B）[pdf:E04]（PDF 物理页 2，Section II-C）

第二步，单纯放大步长仍解决不了高电平 MMC 的大规模非线性矩阵。作者因此把每个子模块从桥臂中拆出，用有一步延迟的受控电压源/电流源连接；三相、每相两桥臂、每桥臂含 N 个子模块的 MMC 被拆成 6N 个非线性 SM 子系统和 1 个线性主电路子系统。[pdf:E05]（PDF 物理页 3，Fig. 2）[pdf:E06]（PDF 物理页 3，Section III 开头）

第三步，分割后出现大量结构相同的小矩阵，恰好适合 GPU 的 single-instruction-multiple-thread（SIMT，单指令多线程）架构。CPU 负责初始化和数据搬运，GPU 顶层 kernel 再启动各组件 kernel，并通过 device function 计算器件模型。[pdf:E07]（PDF 物理页 5，Fig. 5）[pdf:E08]（PDF 物理页 5，Section IV-A）

第四步，局部自适应必须与系统级时间轴重新对齐。作者把每个 converter 视为一个 VTS system，取其全部 SM 候选步长中的最小值作为该 MMC 的局部步长；传输线和海上风电场等较慢的系统级模型使用较大的固定全局步长，只有当所有 VTS 子系统的时间都越过当前全局时刻后，FTS 系统才前进一步。[pdf:E09]（PDF 物理页 3，Fig. 1）[pdf:E10]（PDF 物理页 3，Section II-D）

## § 4 — 核心 Intuition

快速仿真的关键不是让所有组件都粗略地走大步，而是让每个 MMC 在平稳阶段走大步、在开关或故障瞬态走小步，同时把大量子模块拆成可并行的小问题。为了保证一个 MMC 内所有子系统都收敛，局部步长取全部 SM 所需步长的最小值；为了避免整个 MTDC 都被纳秒级步长拖住，慢系统再用更大的固定步长异步等待快系统追上。[pdf:E10]（PDF 物理页 3，Section II-D）[pdf:E06]（PDF 物理页 3，Section III 开头）[pdf:E11]（PDF 物理页 5，Section III-C）

## § 5 — 具体方法与完整 Pipeline

以论文的四端 MTDC 为例，输入包括两条集成 offshore wind farm（OWF，海上风电场）的 HVDC 链路、4 个 MMC、传输线和控制器。MMC1/2 作为整流器维持 OWF 交流电压，MMC3/4 作为逆变器调节直流侧电压；TL3 连接两条 HVDC 链路形成 MTDC。[pdf:E12]（PDF 物理页 6，Fig. 7 与 Eq. (20)）完整 pipeline 如下。

1. **选择开关模型。** 对系统级研究可用 TSSM；对器件级研究使用 nonlinear behavioral model（NBM，非线性行为模型）。TSSM 的分割 HBSM 由一个 2×2 节点方程求解，并显式包含分割引入的一步延迟电流源。[pdf:E13]（PDF 物理页 3，Section III-A，Eq. (9)）NBM 则把 IGBT 的开通/关断电流源、关断 tail current（尾电流）、二极管指数静态特性与反向恢复、电热网络组合起来。[pdf:E14]（PDF 物理页 4，Fig. 4，Eq. (15)-(17)）

2. **分割 MMC。** 每个 SM 从桥臂主电路中分离，主电路端用延迟一拍的受控电压源，SM 端用延迟一拍的电流源耦合。一个 (N+1)-level 三相 MMC 因而产生 6N+1 个小子系统；主电路缩成固定 5 节点线性网络，HBSM NBM 子模块是 8 节点，FBSM NBM 子模块是 13 节点。[pdf:E06]（PDF 物理页 3，Section III 开头）[pdf:E15]（PDF 物理页 4，Fig. 3，Eq. (10)-(14)）[pdf:E16]（PDF 物理页 5，Eq. (18)-(19) 及相邻正文）

3. **为每个候选局部步长计算判据。** 事件判据用 dv/dt 或 di/dt 识别线路故障、断路器动作或器件切换；LTE 用低阶单步积分结果与高阶 Adams-Moulton 预测结果之差估计误差；NBM 还可直接用 N-R 迭代次数判断非线性强弱。[pdf:E03]（PDF 物理页 2，Section II-A/B）[pdf:E17]（PDF 物理页 2，Eq. (1)-(6)）[pdf:E04]（PDF 物理页 2，Eq. (7)-(8)）

4. **更新步长。** 步长需要放大时通常逐次翻倍直至上限，需要缩小时逐次减半直至下限；若当前已经在最大步长，则先退到次大值。NBM 实验把固定步长参考设为 10 ns，VTS 范围设为 10-500 ns；稳态允许接近 500 ns，瞬态时迭代增加并回落到 10 ns。[pdf:E10]（PDF 物理页 3，Section II-D）[pdf:E11]（PDF 物理页 5，Section III-C）

5. **形成 MMC 局部时间。** 一个 MMC 中各 SM 独立产生候选步长，最终取最小值作为整个 converter 的局部步长，以满足全部 6N+1 个子系统的收敛和精度需求。[pdf:E07]（PDF 物理页 5，Fig. 5 下方相邻正文）

6. **与系统级 FTS 同步。** 论文的四端系统让传输线和 OWF 以 20 μs 固定步长推进，而每个 MMC 在 10-500 ns 内独立 VTS；FTS 模型等待所有 VTS 系统越过当前全局时刻后再更新。[pdf:E09]（PDF 物理页 3，Fig. 1）[pdf:E18]（PDF 物理页 6，Section V-A 与实验平台）

7. **映射到 GPU。** 实验平台是 NVIDIA Tesla V100，报告 5120 CUDA cores、16 GB HBM2 和 900 GB/s memory bandwidth。CPU 启动程序并经 PCIe 3.0 搬运数据，GPU 的 kernel0 表示整体 MTDC，子 kernel 表示各电路组件，器件行为以 device function 调用；NBM SM kernel 内重复 N-R，保存每个 SM 的最终迭代次数，再由 VTS 模块取最大迭代次数决定下一步长。[pdf:E08]（PDF 物理页 5，Section IV-A）[pdf:E19]（PDF 物理页 6，Fig. 6 与 Section IV-B）

8. **输出与验证。** 输出包括系统电压电流、IGBT/diode 开通关断与反向恢复波形、损耗和结温；device-level 结果对照 SaberRD，system-level 结果对照 PSCAD/EMTDC。[pdf:E18]（PDF 物理页 6，实验平台段落）

论文没有报告 FPGA 映射、定点数格式、片上存储规划、流水线 initiation interval、资源利用率或实时硬步长，因此不能把这项 GPU 方案直接解读为 FPGA 实现。它也没有明确报告 CUDA 浮点精度配置；可确认的是操作系统与处理器平台，而不是数值表示细节。[pdf:E08]（PDF 物理页 5，Section IV-A）[pdf:E18]（PDF 物理页 6，实验平台段落）

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学核心是“用高阶预测评估误差，用非线性迭代负担评估动态强度，再把离散器件子系统拆成小矩阵”。

**1. LTE 自适应步长。** 对电感电流或电容电压统一写成一阶微分方程

\[
y' = F(t,y(t)),
\]

其精确一步更新为

\[
y_{n+1}=y_n+\int_{t_n}^{t_{n+1}}F(\tau,y(\tau))\,d\tau.
\]

作者用隐式 s-step Adams-Moulton 方法给出较高精度预测

\[
\bar y_{n+1}=y_n+\sum_{m=n-s+1}^{n+1}\left(\int_0^{\Delta\tilde t}\psi(\tau)d\tau\right)F(t_m,y_m),
\]

其中 Lagrange 插值基函数为

\[
\psi(\tau)=\prod_{\substack{k=n-s+1\\k\ne m}}^{n+1}\frac{\tau-t_k}{t_m-t_k}.
\]

再把它与单步积分得到的 \(y_{n+1}\) 比较：

\[
\epsilon=\left|\frac{\bar y_{n+1}-y_{n+1}}{\bar y_{n+1}}\right|\times100\%.
\]

\(\epsilon\) 大则缩步保证精度，小则放大步长节省计算。实际采用的四阶 AM 预测是

\[
\bar y_{n+1}=y_n+\frac{\Delta\tilde t}{24}(9F_{n+1}+19F_n-5F_{n-1}+F_{n-2}).
\]

这些公式直接对应 PDF 物理页 2 的 Eq. (1)-(6)。[pdf:E17]

**2. N-R 迭代次数判据。** 非线性节点方程可概括为

\[
U_n^k=(G_n^k)^{-1}J_n^k,
\]

当相邻两次迭代满足

\[
\frac{\lVert U_n^{k+1}-U_n^k\rVert}{\lVert U_n^{k+1}\rVert}\le \zeta
\]

时认为收敛。线性网络的 \(k=1\)，非线性 IGBT/diode 在稳态迭代较少、瞬态迭代较多，因此 \(k\) 本身就是可计算的步长信号。[pdf:E04]（PDF 物理页 2，Eq. (7)-(8)）直觉上，它不必额外估计“波形变化是否激烈”，而是直接询问求解器“当前这一步有多难”。

**3. 分割后的离散子模块。** TSSM HBSM 的节点电压由

\[
\begin{bmatrix}U_1(t)\\U_2(t)\end{bmatrix}=
\begin{bmatrix}G_C+R_1^{-1}&-R_1^{-1}\\-R_1^{-1}&R_1^{-1}+R_2^{-1}\end{bmatrix}^{-1}
\begin{bmatrix}I_{Ceq}(t)\\J_s(t-\Delta t)\end{bmatrix}
\]

求得；\(J_s(t-\Delta t)\) 是电路分割引入的一步延迟。[pdf:E13]（PDF 物理页 3，Eq. (9)）电容历史项 Eq. (10)、5 节点 MMC 主电路 Eq. (11)-(13) 和电感历史项 Eq. (14) 把同一套 AM 预测嵌入 SM 电容与桥臂电流的步长控制。[pdf:E15]（PDF 物理页 4，Fig. 3，Eq. (10)-(14)）

**4. 非线性器件模型。** IGBT 核心电流源 \(i_{mos}\) 在 Eq. (15) 中按 gate-emitter capacitor voltage、器件端电压和阈值电压分段；Eq. (16) 增加 turn-off tail current；二极管静态部分采用

\[
I_d=I_s\left(e^{V_j/(nV_T)}-1\right),
\]

并由其余网络描述 reverse recovery（反向恢复）。[pdf:E14]（PDF 物理页 4，Fig. 4，Eq. (15)-(17)）这些器件元件随后装配成 HBSM 的 8×8 导纳矩阵和电流向量 Eq. (18)-(19)。[pdf:E16]（PDF 物理页 5，Eq. (18)-(19)）

**5. 系统级功率交换。** 对连接两条 HVDC 链路的 TL3，论文用

\[
I_{exc}=2\frac{I_{dc1}-I_{dc2}}{Z_{TL}+4Z_L}Z_L
\]

估算相同直流电压参考下的交换电流，并用系统波形验证该数值关系。[pdf:E12]（PDF 物理页 6，Eq. (20)）这不是 VTS 的推导核心，但它说明局部纳秒级 MMC 求解最终仍要保持系统级网络关系。

## § 7 — 实验设计与结论

**问题 1：三种 VTS 判据能否在器件级 MMC 中维持波形并减少计算？** 实验使用单相 9-level MMC、8 kV 直流母线、1 kHz 开关频率和 BSM 300GA 160D IGBT，比较 SaberRD、event criterion、LTE 和 N-R iteration count；最大步长为 500 ns。输出电压几乎一致，稳态时 LTE 与 N-R 可升到最大步长，瞬态时回落到 10 ns。Table I 中，5-level 情况下 N-R VTS 用时 13.8 s，相对 SaberRD 247 s 和 10 ns FTS 218 s 的 speedup 分别为 18 和 16；随着电平提高，N-R 仍是所测 CPU VTS 中最快的一项。[pdf:E20]（PDF 物理页 7，Fig. 8 与 Table I）

**问题 2：器件级开关与热波形是否可信？** 作者把 9-level MMC 的 IGBT turn-on、turn-off、diode reverse recovery 和 junction temperature 与 SaberRD 比较。瞬态区采样点更密，lower IGBT/diode 的结温启动后超过 100 °C，最终上下器件均接近 30 °C，论文称 SaberRD 给出相同波形。[pdf:E21]（PDF 物理页 7，Fig. 9）[pdf:E22]（PDF 物理页 7，Fig. 9 相邻正文）

**问题 3：VTS 是否也能加速较简单的 TSSM HVDC？** LTE 被用于 HBSM/FBSM TSSM，步长范围 1-30 μs，在 arm-current relative error 小于 5% 的条件下，Table II 的 1 s 仿真获得约 21-29 倍 speedup；例如 201-level HBSM 从 77.1 s 降到 3.67 s，FBSM 从 310.2 s 降到 10.63 s。[pdf:E21]（PDF 物理页 7，Table II 及相邻正文）

**问题 4：device-level 模型是否改变直流故障结论？** 在 ±100 kV 四端系统中，作者于 t=5 s 施加 1 Ω pole-pole fault。HBSM 的续流二极管仍把交流侧与直流侧连通，得到约 25 kV residual line-line voltage 和 9.4 kA dc current；FBSM 能完全阻断，电压电流最终为 0。HBSM 下部器件结温在故障保护过程中超过 140 °C，而 FBSM 温度较低。PSCAD/EMTDC 的固定开关电阻会改变故障电流，作者选择 0.4 mΩ 作为较接近 NBM 的默认值。[pdf:E23]（PDF 物理页 7，Section V-C 开头）[pdf:E24]（PDF 物理页 8，Fig. 10 与相邻正文）

**问题 5：整流侧没有 stiff grid 支撑时，模型还能复现系统趋势吗？** 在 OWF 支撑的 HBSM-HVDC 故障中，Grid 1 交流电压在故障后降到约 0，\(I_{dc3}\) 上升到约 10 kA，\(I_{dc1}\) 因失去 stiff AC support 降到 0；作者称 PSCAD/EMTDC 给出一致趋势。[pdf:E25]（PDF 物理页 8，Fig. 11 与相邻正文）

**问题 6：正常运行下的 MTDC 功率交换是否正确？** t=12 s 起，OWF1 风速在 1 s 内从 8 m/s 线性升到 11 m/s，OWF2 反向变化；单台 DFIG 的功率约从 750 kW 升到 2.0 MW，MMC 功率按 100 台聚合，直流电压扰动被逆变站调节并快速恢复，TL3 的 \(I_{exc}\) 与 Eq. (20) 关系吻合。Fig. 12 左右两列分别是 proposed model 与 PSCAD/EMTDC。[pdf:E26]（PDF 物理页 8，Fig. 12 前置正文）[pdf:E27]（PDF 物理页 9，Fig. 12）

**问题 7：CPU VTS 与 GPU 并行叠加后能快到什么程度？** Table III 对 0.1 s、4-terminal NBM 系统给出执行时间。以 201-level 为例，HBSM 的 CPU FTS 为 50,484 s，GPU VTS 为 26.4 s，对应 Sp7=1912；FBSM 的 CPU FTS 为 94,309 s，GPU VTS 为 154 s，对应 Sp10=612。表中最大 Sp7 为 1912，最大 Sp10 为 946，支撑作者“约 2000 倍和 1000 倍”的概括。[pdf:E28]（PDF 物理页 9，Table III）

但实验的外推边界也很清楚。验证依赖 SaberRD 与 PSCAD/EMTDC，而不是实物控制器、hardware-in-the-loop 或实时 FPGA；CPU FTS 的超长执行时间部分通过短时 10 ns 运行估算；GPU 速度优势同时来自 VTS、矩阵分割和 SIMT，论文没有通过完整 ablation 把三者的独立贡献彻底拆开。[pdf:E18]（PDF 物理页 6，实验平台）[pdf:E28]（PDF 物理页 9，Table III 上下文）

## § 8 — Take-aways

**5 句话。** 1）论文把 VTS、MMC circuit partitioning 和 GPU SIMT 组合成一条可运行的 device-to-system EMT pipeline，而不是单独优化某一个求解环节。[pdf:E29]（PDF 物理页 9，Conclusion） 2）事件、LTE 和 N-R 迭代次数分别从物理事件、数值误差和非线性求解难度三个角度控制步长。[pdf:E03]（PDF 物理页 2，Section II）[pdf:E04]（PDF 物理页 2，Eq. (7)-(8)） 3）分割把一个高电平 MMC 变成 6N+1 个小系统，为 GPU 提供足够并行度，但引入一步耦合延迟。[pdf:E06]（PDF 物理页 3，Section III 开头） 4）商业仿真工具对照显示，NBM 能复现开关、反向恢复、结温和系统故障波形，并揭示 TSSM 固定电阻会影响故障电流。[pdf:E22]（PDF 物理页 7，device-level validation）[pdf:E24]（PDF 物理页 8，Fig. 10） 5）最显著的性能数字来自 GPU VTS 对 CPU FTS 的组合比较，最高接近 2000/1000 倍，但不是单一 VTS 算法的纯 speedup。[pdf:E28]（PDF 物理页 9，Table III）

**3 句话。** 1）这篇论文的真正贡献是让器件级非线性模型进入 MTDC 系统级 EMT，而不是只把已有平均模型跑快。 2）它用局部小步长保护瞬态精度，用大步长跳过平稳区，再用电路分割把非线性计算变成 GPU 可吞吐的规则任务。 3）其主要风险是分割的一步延迟和“全 MMC 取最小局部步长”的同步策略在更剧烈、更高电平工况下可能同时损害精度和 speedup。[pdf:E06]（PDF 物理页 3，分割假设）[pdf:E30]（PDF 物理页 9，speedup limitation）

**1 句话。** 这是一套以有限耦合近似换取大规模并行、再以自适应步长把精度集中到瞬态区的详细 MMC-MTDC EMT 仿真方法。[pdf:E29]（PDF 物理页 9，Conclusion）

## § 9 — 最脆弱的假设

最脆弱的假设不是“GPU 足够快”，而是**分割接口的一步延迟在所有关键瞬态中都足够小，可以把相邻时间步的桥臂电流视为常数**。作者明确以“EMT 计算频率很高、相邻步桥臂电流变化很小”来论证分割精度。[pdf:E06]（PDF 物理页 3，Section III 开头）如果这个条件不成立，SM 接收到的是过时电流，主电路接收到的是过时电压，误差会直接进入节点方程、N-R 收敛判断和下一步长选择；这不是结果末端的小偏差，而是核心耦合机制本身失真。

**基于证据的推断。** 该假设最可能在低桥臂电感、极陡故障电流、高 dv/dt/di/dt、多个 SM 近同步切换或最大 VTS 较大时失效。论文的故障与风电工况对 PSCAD/EMTDC 显示了良好趋势，说明在所测参数范围内延迟没有造成明显灾难。[pdf:E24]（PDF 物理页 8，Fig. 10）[pdf:E25]（PDF 物理页 8，Fig. 11）但论文没有给出“分割模型 vs 同一 NBM 的单体紧耦合模型”的误差分解，也没有扫描桥臂电感、接口预测阶数或最大局部步长来建立稳定性边界。

同时，所有 SM 取最小步长的策略使这项假设还有性能侧后果：电平越高，任一 SM 进入切换过程的概率越大，整个 MMC 越容易被迫使用小步长，作者已观察到 speedup 随电平增加下降。[pdf:E30]（PDF 物理页 9，Table III 后分析）这说明“局部自适应”在 converter 内部仍是全局同步的，规模增加后可能退化为近似固定小步长。

## § 10 — 最小复现实验

一周内最值得复现的不是完整四端系统，而是“**N-R iteration-count VTS 能否在保留器件瞬态的同时比 10 ns FTS 更快**”。

实验对象选论文已经给出验证设置的单相 9-level HBSM MMC：8 kV 直流母线、1 kHz 开关频率、VTS 范围 10-500 ns，并使用 Appendix 给出的 BSM 300GA 160D IGBT/diode 参数。[pdf:E18]（PDF 物理页 6，Section V-B）[pdf:E31]（PDF 物理页 10，Appendix device parameters）实现范围只需包含一个相桥臂的分割主电路、NBM HBSM、N-R 求解和迭代次数到步长的映射；不需要先做 GPU。

具体执行：先用固定 10 ns 作为 reference，运行稳态后一次明确的 turn-on/turn-off 或短时直流扰动；再用相同模型运行 10-500 ns VTS。记录 wall-clock time、总步数、每步 N-R 次数、发散次数、输出电压/桥臂电流 RMS error、瞬态 peak error、switching time shift，以及 IGBT/diode 的 turn-on、turn-off 和 reverse-recovery 波形。器件方程和矩阵装配分别对照 Eq. (15)-(19)。[pdf:E14]（PDF 物理页 4，Eq. (15)-(17)）[pdf:E16]（PDF 物理页 5，Eq. (18)-(19)）

预先注册一个**复现实验判据**，明确它不是论文原设门槛：VTS 相对 10 ns FTS 至少降低 5 倍 wall-clock time，稳态 RMS error 不超过 1%，关键瞬态峰值误差不超过 5%，且无额外发散，即视为支持核心 claim；若速度提升不足 2 倍、瞬态峰值/时序误差持续超过 5%，或只能通过频繁退回 10 ns 才稳定，则视为反驳。这个实验能把“步长控制是否有效”与“GPU 是否强大”分开，是成本最低的可证伪路径。

## § 11 — 最强反例设计

最强反例应同时攻击正确性和 speedup：构造一个让桥臂电流在单个允许步长内剧烈变化、且大量 SM 接近同时切换的工况，然后比较 partitioned one-step-delay NBM 与 monolithic tightly coupled NBM。

具体做法是固定器件模型和控制器，逐级减小 arm inductance，并在高调制深度下于一个载波边沿附近施加低阻 pole-pole fault 或强制门极状态突变。对每个工况扫描最大 VTS 50、100、250、500 ns，比较两种模型的故障电流峰值、换相时刻、N-R 迭代轨迹、能量/电荷残差和最终步长序列。论文基准系统使用 50 mH arm inductor、201-level MMC、±100 kV 直流电压，线路和器件参数均已给出，可从这个点向更陡的动态连续外推压力测试。[pdf:E32]（PDF 物理页 9，Appendix system parameters）[pdf:E31]（PDF 物理页 10，Appendix device parameters）

**可预测的失败模式。** 如果一步延迟不是无害近似，partitioned model 会在 monolithic reference 之前或之后错误触发 N-R/步长缩减，造成故障峰值和器件反向恢复偏差；如果最小步长聚合是主要瓶颈，大量近同步切换会把整个 MMC 长时间锁在 10 ns，GPU VTS 的 speedup 会显著坍塌。[pdf:E06]（PDF 物理页 3，分割假设）[pdf:E11]（PDF 物理页 5，10-500 ns 与最小步长逻辑）[pdf:E30]（PDF 物理页 9，电平升高导致 speedup 下降）一旦出现这种结果，就能提出一个具体替代解释：论文的高 speedup 依赖被测工况中接口变量足够平滑和切换足够分散，而不是方法对任意强瞬态都稳健。

## § 12 — Follow-up Research Idea

从论文自身的评价轴看，这一领域的高影响工作需要同时满足 model fidelity、numerical stability、large-scale speedup、商业工具或实际系统验证，以及可落地的计算平台；只提高一个 kernel 的吞吐而不证明误差边界，研究价值有限。[pdf:E29]（PDF 物理页 9，Conclusion）

**候选研究方向：误差预算驱动的异步多速率 MMC EMT，不再用“全 MMC 最小 SM 步长”统一推进。** 这是基于本文证据提出的候选想法，未做外部相关工作检索，因此不声称 novelty。

(a) **未满足需求。** 现方法一方面用一步延迟解耦主电路和 SM，另一方面又把所有 SM 的候选步长压成一个最小值；前者缺少显式接口误差控制，后者在高电平、异步切换时吞掉 VTS 收益。[pdf:E06]（PDF 物理页 3，circuit partitioning）[pdf:E30]（PDF 物理页 9，speedup limitation）

(b) **潜在研究价值。** 新方法让每个 SM 或一组行为相近的 SM 在自己的时间网格上推进，仅在接口误差预算被耗尽时与主电路同步；目标从“尽可能放大统一步长”改成“在可证明的耦合误差范围内最大化异步性”。这既可能保留 device-level fidelity，也可能让 201-level 以上 MMC 不再因单个 SM 切换而全体退回最小步长。

(c) **可借鉴的工具。** 可采用 waveform relaxation（波形松弛）、predictor-corrector interface（预测-校正接口）、局部误差估计和保守的电荷/能量交换约束；这些在本卡中仅作为方法候选，不作为论文已使用的事实。

(d) **第一个证伪实验。** 在第 11 节的低电感、近同步切换故障上，把异步方法与本文的 minimum-step VTS、10 ns FTS 和 monolithic NBM 同时比较。若异步方法不能在相同峰值/时序误差约束下减少总 SM 更新次数，或接口能量残差显著大于本文分割模型，就应立即否定该方向。

(e) **与本文的实质区别。** 本文改变的是步长判据和计算映射，但 converter 内仍共享最小局部步长；候选方法改变的是耦合与同步语义，让“谁必须在何时同步”由可计算误差决定。它不是增加第四种 VTS criterion，也不是把同一 CUDA kernel 搬到 FPGA，而是重新定义高电平 MMC 的时间组织方式。
