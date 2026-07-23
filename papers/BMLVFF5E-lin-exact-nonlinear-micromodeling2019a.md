# Exact Nonlinear Micromodeling for Fine-Grained Parallel EMT Simulation of MTDC Grid Interaction With Wind Farm

- 作者：Ning Lin；Venkata Dinavahi
- 出处：*IEEE Transactions on Industrial Electronics*, Vol. 66, No. 8
- 年份：2019
- DOI：10.1109/TIE.2018.2860566
- Zotero key：BMLVFF5E

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文要解决的不是一般意义上的“让 EMT 仿真更快”，而是一个长期被计算量逼退的精度问题：能否在含多个 MMC 换流站和风电场的 MTDC 系统级 EMT 仿真中，仍然保留 IGBT 与反并联二极管的 nonlinear micromodel，而不是把它们退化成固定导通/关断电阻的理想开关。这里的 **nonlinear micromodel** 指器件内部的门极、尾电流、二极管结、反向恢复和热网络等行为由非线性电路描述，因而能显现开关过冲、恢复过程和结温；它不是缩小系统，而是把系统中每个开关的物理细节放大到可计算的层级。作者把这个问题放到含 3 个直流子系统、11 个交直流端口的 CIGRÉ B4 MTDC 风电场场景中 [pdf:E03]（PDF 物理页 2，Fig. 1 与 Section II）。

物理上，这种细节决定“器件实际承受了什么”：two-state switch model（TSSM）看不到开关瞬态电流过冲，可能低估器件应力，也不能直接给出器件级损耗和结温。数值上，高阶非线性器件会为每个 MMC 子模块增加节点和 Newton–Raphson 迭代，若把数百至数千个开关塞进一个大矩阵，CPU 串行求解既慢又容易因非线性耦合而发散。论文的摘要和引言明确把“器件级洞察”与“大系统可计算性”视为同一个矛盾 [pdf:E01]（PDF 物理页 1，Abstract）[pdf:E02]（PDF 物理页 1，Introduction）。

所谓 **fine-grained parallel EMT**，就是先把 MMC 臂与每个子模块之间用 V–I 耦合源断开：臂侧收集子模块电压，子模块侧接收臂电流；在一个离散时间步内两边独立求解，步末再交换信息。这样，一个庞大的非线性网络变成大量结构相同、可同时求解的最小子电路。它的物理代价是把连续耦合改成步间信息交换；数值收益则是缩小每次矩阵求解、隔离非线性迭代，并把每个 SM 映射到一个并行线程 [pdf:E04]（PDF 物理页 3，Fig. 4 及相邻正文）。

## § 2 — 前人工作与不足

论文给出的相关工作链条有三层。第一，主流系统级 EMT 工具采用固定 ON/OFF 电阻的 TSSM；第二，为了让大规模 MMC 可算，已有 detailed equivalent model、averaged value model 和连续降阶模型进一步聚合开关；第三，SaberRD、PSpice 一类器件级工具能够使用经实验校准的 IGBT/diode model，但通常只适合小型变换器。作者认为，前两类方法以器件瞬态可见性换取速度，第三类方法则因节点数、非线性迭代和发散风险难以扩展到 MTDC 系统 [pdf:E02]（PDF 物理页 1，Introduction，文献 [8]–[18]）。

已有 circuit partitioning 能把大导纳矩阵拆成小电路，GPU 也已用于电力系统和电力电子 EMT；不足在于 CPU 对拆分后的子电路仍多为顺序执行，而 MMC 中数量最多、计算最重的 nonlinear SM 尚未与 GPU 的 SIMT 结构逐一对齐。论文因此不是单独发明器件模型、分区或 GPU，而是把它们组合成“最小 SM 分区 + 每 SM 一线程 + 系统级 child kernels”的执行链 [pdf:E01]（PDF 物理页 1，Abstract/Introduction）[pdf:E08]（PDF 物理页 5，Fig. 7）。

这里没有做额外的系统性文献检索，因此本节只能复述论文对 prior work 的定位，不能据此声称该组合在 2019 年具有已充分检索的 novelty。

## § 3 — 重建作者的思考路径

可以把作者的思路重建为四步。第一，系统研究真正关心的故障应力、开关过冲和热状态被理想开关遮蔽，但直接把完整器件模型放进 MMC 会形成巨大的非线性矩阵。第二，EMT 在离散时间上推进，若一个时间步内把接口电流视为已知，MMC 臂与每个 SM 可以通过 V–I 源切开，得到最小可分子电路 [pdf:E04]（PDF 物理页 3，Section II-C、Fig. 4）。第三，大量 SM 结构相同，恰好对应 GPU 的 SIMT：同一 kernel 执行同一指令，不同 thread 处理不同 SM [pdf:E08]（PDF 物理页 5，Fig. 7）。第四，原始器件模型仍有内部节点和发散源，因此先把只影响 tail current 的 \(r_{\mathrm{tail}}-C_{\mathrm{tail}}\) 支路移出主子电路，使单个 partitioned SM 从十个节点减到八个，再在每个线程中独立做 Newton–Raphson [pdf:E06]（PDF 物理页 4，Section III-A.3）。

这条路径的关键不是“GPU 比 CPU 快”这一常识，而是先把计算图重构成 GPU 能吃下的同构、局部、独立任务。若不做物理分区，GPU 仍面对一个强耦合大矩阵；若只做分区而不并行，CPU 仍需依次处理大量 SM。

## § 4 — 核心 Intuition

核心 intuition 是：把每个 MMC 子模块当作一个可独立收敛的非线性微电路，并让它在一个 GPU thread 中完成自己的器件线性化、矩阵求解和历史量更新；全系统只在时间步边界交换 V–I 接口量。于是，器件模型越复杂、SM 数量越多，反而越能填满 GPU 的并行资源，而不是让 CPU 的顺序工作量按同样比例增长 [pdf:E08]（PDF 物理页 5，Fig. 7 与 Section III-C）。

## § 5 — 具体方法与完整 Pipeline

以“风速下降并触发 MTDC 系统动态”为例，完整 pipeline 如下。

1. **系统建模。** CIGRÉ B4 DC grid 与五个 offshore wind farms 组成测试系统；DFIG 用 \(\alpha\)-\(\beta\) 状态空间模型表示，风机阵列在 PCC 处聚合，缩放因子 \(N_D\) 表示风机台数 [pdf:E03]（PDF 物理页 2，Fig. 1、Eq. (1)–(7)）。
2. **接口分区。** IM 与外部电路、聚合 DFIG 与整流器侧分别通过 V–I source coupling 连接；MMC 的每个 SM 再从 arm 中拆开。时间步内，arm 汇总所有 \(v_{\mathrm{SM}}\)，SM 读取同一个 \(i_{\mathrm{arm}}\)，两侧完成后交换结果并前进 \(\Delta t\) [pdf:E04]（PDF 物理页 3，Fig. 3–4）。
3. **器件非线性建模。** IGBT 的 MOS channel、gate capacitances、tail current 与二极管的指数结模型、reverse recovery 支路被离散成 Norton 等效；系统级线性元件用 trapezoidal rule，非线性 IGBT/diode 用 Backward Euler [pdf:E05]（PDF 物理页 4，Eq. (8)–(13)）[pdf:E06]（PDF 物理页 4，Eq. (14)–(17)）。
4. **SM 局部求解。** HBSM 的电容、上管、下管贡献组合成 \(G_{\mathrm{SM}}\) 与 \(J_{\mathrm{SM}}\)，再求 \(U_{\mathrm{SM}}=G_{\mathrm{SM}}^{-1}J_{\mathrm{SM}}\)；并联器件以数量因子 \(m\) 缩放。FBSM 使用同样思想，但节点与开关数更多 [pdf:E07]（PDF 物理页 5，Fig. 6、Eq. (18)–(20)）。
5. **GPU 映射。** 一个 nonlinear SM 对应一个 thread；thread 内调用 IGBT/diode device function，更新 \(G,J\)，反复求解直到 \(U\) 收敛。不同 component type 写成不同 child kernel，变量经 global memory 交换 [pdf:E08]（PDF 物理页 5，Fig. 7）。
6. **全局时间推进。** 外层 Kernel0 表示整个 DC grid，并通过 CUDA dynamic parallelism 启动 controller、linear network、SM 等 child kernels；有数据依赖的七类 kernel 仍按顺序执行，但每个 kernel 内的同类元件并行。host CPU 仅负责开始、结束和单向数据传输，EMT 时间循环在 GPU 上完成 [pdf:E09]（PDF 物理页 6，Fig. 8）[pdf:E10]（PDF 物理页 6，Fig. 9–10）。
7. **输出与校验。** 输出包括器件开关波形、结温、风场功率/电压动态、DC fault 响应、稳态潮流和执行时间；器件层与 SaberRD 对比，系统层与 PSCAD/EMTdc 对比。

论文实际执行平台是 Nvidia Tesla V100（5120 CUDA cores、16 GB HBM2）和 2.20 GHz 20-core Intel Xeon E5-2698 v4/128 GB RAM，操作系统为 64-bit Windows 10 [pdf:E10]（PDF 物理页 6，Section IV 开头）。论文没有 FPGA implementation、RTL、定点格式、片上存储或时序收敛报告；因此，本文的细粒度数据流适合启发 FPGA 映射，但不能把 GPU 结果直接写成 FPGA 实时性能。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线不是证明一个新定理，而是把连续非线性器件变成每个时间步可重复求解的线性 Norton companion。

IGBT 的 MOS channel current \(i_{\mathrm{mos}}\) 由 OFF、ON 和 transient 三段函数给出；对端口电压 \(v_d\) 与 gate-related voltage \(v_{cge}\) 做偏导，得到 conductance \(G_{\mathrm{mos}v_d}\) 和 transconductance \(G_{\mathrm{mos}v_{cge}}\)。把当前非线性值减去线性斜率贡献，就得到本次迭代的等效电流源

\[
I_{\mathrm{moseq}}
=i_{\mathrm{mos}}
-G_{\mathrm{mos}v_d}v_d
-G_{\mathrm{mos}v_{cge}}v_{cge}.
\]

直觉上，这是在当前工作点用切线替代弯曲的器件 \(I\)-\(V\) 曲线；每次 Newton–Raphson 更新工作点，直到节点电压不再明显变化。IGBT 三段模型、偏导、Norton current 和 tail-current 分段式分别见 Eq. (8)–(12) [pdf:E05]（PDF 物理页 4）。

二极管静态关系为 \(I_d=I_s(e^{V_j/V_b}-1)\)。在当前 \(V_j\) 处线性化后，

\[
G_j=\frac{\partial I_d}{\partial V_j}
=\frac{I_s}{V_b}e^{V_j/V_b},\qquad
I_{jeq}=I_d-G_jV_j .
\]

其中 \(G_j\) 是本次迭代看见的局部导纳，\(I_{jeq}\) 保存切线与原曲线的截距。电感支路再用 Backward Euler 形成历史电流源；论文说明小时间步使这种低阶离散足够 [pdf:E06]（PDF 物理页 4，Eq. (14)–(17)）。

进入 SM 层后，所有 companion 的导纳贡献组装为 \(G_{\mathrm{SM}}\)，历史项、arm current 与器件等效源组装为 \(J_{\mathrm{SM}}\)，求解 \(U_{\mathrm{SM}}=G_{\mathrm{SM}}^{-1}J_{\mathrm{SM}}\)。物理上，它回答“在给定本步臂电流和器件局部斜率时，这个 SM 内部各节点电压是多少”；计算上，每个 SM 的矩阵维数固定且彼此独立，所以可以一线程一矩阵地批量执行 [pdf:E07]（PDF 物理页 5，Eq. (18)–(20)）。

## § 7 — 实验设计与结论

**问题 1：器件 nonlinear model 是否既准确又可扩展？**  
实验用 100 ns 步长仿真单相 MMC 的 100 ms 过程，比较 SaberRD、single-core CPU 与 V100。Table I 显示，9-L 时 SaberRD 用 1720 s，CPU 用 98.4 s，GPU 用 163.7 s；相对 SaberRD 的 CPU/GPU speedup 分别为 17.5/10.5。GPU 在 21-L 才超过 CPU，并在 33-L 达到 1.55 倍，说明小规模下启动与并行开销占主导，规模增大后 GPU 才显出优势 [pdf:E11]（PDF 物理页 7，Table I）。

**问题 2：micromodel 是否给出理想开关遗漏的器件信息？**  
9-L MMC 在 8 kV dc bus、\(\Delta T=5\,\mu s\)、10 \(\Omega\) gate resistance、\(\pm15\) V drive 下，NBM 与 SaberRD 的 turn-on、turn-off、diode reverse recovery 波形吻合；改变 gate condition 会改变过冲和上升时间。论文还报告，在 PSCAD/EMTdc 的典型 20 \(\mu s\) 步长与默认 TSSM 下，约 190 A 稳态电流出现 6 A 差异，且看不到开关瞬态；调节 TSSM 的 ON-state resistance/voltage drop 后结果更接近 NBM [pdf:E11]（PDF 物理页 7，Fig. 11）[pdf:E12]（PDF 物理页 7，Fig. 12 及相邻正文）。

**问题 3：模型能否保持系统级动态正确？**  
在 DCS1 的 100 台风机场景中，风速在 1 s 内从 11 m/s 降到 8 m/s，DFIG rotor speed 从 188 rad/s 降到约 137 rad/s；单机功率由 1.96 MW 降至约 0.76 MW，两端站功率由 200 MW 降至约 76 MW，inverter dc voltage 瞬时下陷至 199 kV 后恢复。GPU 与 PSCAD/EMTdc 波形基本重合 [pdf:E13]（PDF 物理页 8，Fig. 13 与正文）。这些是论文报告数字，不是从曲线重新估读的高精度测量。

**问题 4：精细开关模型会不会改变系统故障判断？**  
在 \(t=3\) s 发生 pole-to-pole fault 后，FBSM 的 dc current 经振荡降到 0，而 HBSM 超过 10 kA；TSSM 不同 ON-state resistance 会给出不同故障电流/电压，说明器件等效并非对系统级故障完全无关 [pdf:E14]（PDF 物理页 8，Fig. 14）。验证仍是 GPU 对 PSCAD/EMTdc 的 simulation-to-simulation comparison，不是硬件故障实验。

**问题 5：全规模 MTDC 的计算收益有多大？**  
对 1 s、200 ns 步长的 CIGRÉ B4 grid，11 个 401-L MMC 的 V100 执行时间为 1728 s（HBSM）或 1729 s（FBSM）；相对 1 CPU core 的 speedup 为 1302/2608，相对 20 CPU cores 为 134/265。51-L 到 401-L 时 GPU 时间只从约 901/908 s 增到 1728/1729 s，而 CPU 时间增长更快 [pdf:E15]（PDF 物理页 9，Table II）。这证明该 workload 在这套硬件和实现上具有显著规模并行性，但它仍是 1728 s 计算 1 s 物理过程，论文没有声称 real-time。

## § 8 — Take-aways

**5 句话：**

1. nonlinear micromodel 的价值是显现 TSSM 隐去的开关过冲、反向恢复与结温，而不是单纯提高波形采样精度。
2. fine-grained partitioning 把一个大非线性 MMC 矩阵重构为大量最小、同构、可独立收敛的 SM 子电路。
3. 一 SM 一 thread 的映射使器件复杂度从 CPU 的重复串行负担变成 GPU 可并行铺开的工作量。
4. 论文用 SaberRD 做器件级对照、用 PSCAD/EMTdc 做系统级对照，并在 401-L MTDC 规模上报告了相对 CPU 的数量级 speedup [pdf:E15]（PDF 物理页 9，Table II）。
5. 结论只对 GPU、浮点实现、固定很小步长和 simulation-to-simulation validation 闭合；不能直接外推到 FPGA 实时仿真或硬件级器件真实性。

**3 句话：** 先用 V–I coupling 把非线性 SM 切成最小子电路，再让每个 GPU thread 独立完成器件线性化与 Newton–Raphson。这样可以在 MTDC 系统规模保留器件瞬态，并使计算时间随 MMC level 增长得比 CPU 慢。代价是依赖时间步接口近似、同构并行度与极小步长，且论文没有硬件实验。

**1 句话：** 这篇论文证明的核心是“先把物理网络改写成并行友好的局部非线性问题，GPU 才能把器件级 EMT 从小电路推向 MTDC 系统”，而不是“换一块更快的处理器”。

## § 9 — 最脆弱的假设

最脆弱的假设是：**在一个时间步内，MMC arm current 可视为常量，因而 V–I coupling 两侧可以独立求解，到步末再交换信息而不会破坏关键快速瞬态。** 这不是普通实现细节，而是 fine-grained partition 的正确性基础；若故障前沿、二极管 reverse recovery 或强控制切换使接口量在 \(\Delta t\) 内变化显著，局部器件求解即使收敛，也可能收敛到带有一步耦合滞后的错误系统轨迹 [pdf:E04]（PDF 物理页 3，Fig. 4 与“between two neighboring time steps, the currents can be deemed as constant”正文）。

论文对此给出的支持是非常小的 100 ns/200 ns 步长，以及与 SaberRD、PSCAD/EMTdc 的所选工况对照 [pdf:E11]（PDF 物理页 7，Table I）[pdf:E15]（PDF 物理页 9，Table II）。缺失的证据是：步长收敛曲线、接口功率/电荷守恒残差、强刚性工况下的稳定域、以及实验测量。因而“分区提高数值稳定性”是作者结论 [pdf:E16]（PDF 物理页 9，Conclusion），但对多大 \(\Delta t\)、哪些开关/故障条件仍成立，本文没有给出可迁移的误差边界。

## § 10 — 最小复现实验

一周内最值得复现的不是整个 11-terminal MTDC，而是一个 5-L 或 9-L 单相 MMC 的单次 turn-on/off 窗口。

- **数据与模型：** 采用附录给出的 Siemens BSM300GA160D behavioral parameters，搭建一个 HBSM arm；保留 NBM 与一个可调 ON-state resistance/voltage drop 的 TSSM 两条模型路径。论文给出的器件参数起始段见 [pdf:E16]，其余器件、MMC、DFIG 和 dc line 参数见 [pdf:E17]（均为 PDF 物理页 9，Appendix）。
- **实现：** 先在 CPU 上完成一个 SM 的 Eq. (8)–(20) Newton–Raphson companion solver，再把相同代码批量映射到 GPU；用 100 ns 作基准，另外测试 50、200、500 ns。不要先复现完整 MTDC controller。
- **测量：** 比较 peak current、reverse-recovery charge、稳态电流、每步 Newton iteration count、interface power residual 和 wall-clock time。所有数值与一个可信 device-level reference 的同一器件参数对齐。
- **支持标准：** 当步长从 100 ns 减半到 50 ns 时，NBM 的关键波形变化已经很小；NBM 能重现 reference 的过冲/恢复形状，而 TSSM 明显遗漏；批量 SM 数增加后 GPU 相对 CPU 的吞吐优势上升。
- **反驳标准：** 若 NBM 与 reference 的误差不优于调参后的 TSSM，或 V–I partition 的 interface residual 随 SM 数/步长扩大而系统性增长，则论文的“精细模型带来可用洞察且能安全分区”这一核心 claim 不成立。

这里的误差阈值应在复现前依据测量噪声和用途预注册；论文没有提供统一误差百分比，不能事后从图形外观选择阈值。

## § 11 — 最强反例设计

最强反例是制造一个“局部器件极快、系统接口也极快”的工况：在接近 dc fault 的时刻同时触发 gate blocking，并把 cable/arm inductance 降低到接口电流可在一个 200 ns 步内显著变化的范围。对同一电路运行两种求解器：一种使用论文的步末 V–I exchange，另一种把 arm 与 SM 做 monolithic implicit solve；两者使用相同器件模型、相同步长和收敛容差。

若 partitioned solver 的单个 SM 都能收敛，GPU 也保持高吞吐，但它在 fault peak、器件能量或 dc blocking time 上与 monolithic solver 产生不可由步长收敛消除的偏差，就能否定“局部收敛足以保证系统级正确”的替代解释。这个反例直接攻击论文最核心的解耦机制，而不只是更换 GPU 或挑一个更大的网络。论文自己的故障图已经显示 HBSM/FBSM 与 TSSM 参数会显著改变 fault response，因此这一攻击的事实前提成立 [pdf:E14]（PDF 物理页 8，Fig. 14）；但该极端联合工况并未被论文验证，结论目前仍是不确定候选。

## § 12 — Follow-up Research Idea

**候选方向：带接口误差证明的 event-adaptive nonlinear micromodel EMT engine。** 由于没有做充分相关工作检索，这里不声称 novelty。

未满足的需求是：固定 100/200 ns 步长能保护快速器件瞬态，却让整个 MTDC 在平稳阶段也支付同样成本；同时，固定一步 V–I lag 没有可观察的正确性边界。研究目标可从“尽可能并行地跑固定小步长”改成“每个 SM 根据局部非线性和接口功率残差自适应推进，但对跨分区能量误差给出在线上界”。

可借鉴的相邻工具包括 waveform relaxation、asynchronous time integration、conservative co-simulation 和 GPU/FPGA task graph scheduling。GPU 负责不规则的 Newton iteration 与 active-set 变化，FPGA 负责大量固定维数 companion update、接口残差累计和确定性时间戳队列；不过这种异构划分只是基于本文计算结构的推断，论文没有实现 FPGA。

第一个证伪实验应使用第 11 节的 fault-plus-gate-blocking 工况：在相同 wall-clock budget 下，比较固定 200 ns partition、monolithic 50 ns reference 和 event-adaptive engine。若 adaptive 方法不能同时降低计算量、保持 interface energy residual 有界，并在 peak current/absorbed energy 上贴近 reference，这个研究方向就被初步证伪。

它与本文的实质区别不是“把 V100 换成 FPGA”，而是把固定步长、开环耦合改成由可测误差驱动的时间推进与硬件调度；本文的结论证明了细粒度同构并行的规模收益 [pdf:E16]（PDF 物理页 9，Conclusion），新问题则要求并行收益与跨分区正确性一起成为一等目标。
