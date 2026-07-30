# A Hierarchical Multiarea Hybrid Equivalent for Efficient Simulation of Scalable Power Electronics Systems

- 作者：Cheng Jin，Kangli Liu，Zhendong Ji，Pengyu Wang，Hao Jin，Jianfeng Zhao
- 出处：*IEEE Transactions on Power Electronics*，Vol. 40，No. 11
- 年份：2025
- DOI：10.1109/TPEL.2025.3586035
- Zotero key：6AXZCAXB

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的不是“怎样把某一个换流器模型算得更快”，而是更难的扩展性问题：当大量开关级 power electronics 模块组成一个 EMT（electromagnetic transient，电磁暂态）模型时，怎样避免连接各 circuit partition 的 linking-variable 方程随系统规模一起膨胀，同时还保留开关纹波和控制动态。作者指出，已有 MAHE（multiarea hybrid equivalent）把串联接口写成 Thévenin/阻抗形式、把并联接口写成 Norton/导纳形式，能利用串联阻抗和并联导纳的线性可加性；但在复杂大系统里，串联回路或并联节点本身继续增多，linking matrix 的维数 \(n\) 仍会上升，相关求解成本达到 \(O(n^2)\)–\(O(n^3)\)。论文要解决的核心问题，就是让这个连接问题也能分层，而不是始终形成一个越来越大的全局接口系统。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

工程价值在于，开关级 EMT 的时间步很小，模型规模一大，单次仿真就可能从分钟变成数天。论文的实验确实展示了这种量级差异：在其 MMC-HVDC 案例里，commercial software 1 对“送端 4 台、受端 4 台 MMC”的 0.5 s 仿真平均需要 4833 min，而 single-core HMAHE 为 5.01 min；在 PV 案例里，commercial software 2 对 32 个电站、共 64 套发电系统的 0.5 s 仿真平均需要 291.25 min，而 multicore HMAHE 为 3.79 min。[pdf:E15]（PDF 物理页 15，Case Study 1 efficiency）[pdf:E18]（PDF 物理页 18，Case Study 2 efficiency）这些数字说明，若模型结构允许有效分层，缩小连接方程比单纯加 CPU 核数更可能改变可计算边界。

但应先划清范围。论文验证的是 1 µs 固定步长、C 语言、Intel MKL BLAS 与 OpenMP、双路 Intel Xeon E5-2680 2.50 GHz 共 24 核上的 CPU 仿真。[pdf:E10]（PDF 物理页 10，Program Code Structure）[pdf:E12]（PDF 物理页 12，Case Study 1 setup）[pdf:E14]（PDF 物理页 14，Fig. 27 caption）它没有给出 FPGA mapping、fixed-point 误差、片上资源、流水线 latency 或实时 deadline；因此本文支持“多核 CPU 上的大规模 EMT 加速”，不直接支持“可在 FPGA 上实时运行”。

## § 2 — 前人工作与不足

论文把前人路线分成四类。第一类用电容、电感等 continuous-state 元件作 partition interface，以减少每个子电路的计算步骤；第二类借 transmission-line 的传播延迟天然解耦子系统；第三类用 Schur complement 消去内部变量，得到 reduced-order equivalent；第四类在接口节点使用 Thévenin equivalent，降低 linking current 的处理复杂度。[pdf:E01]（PDF 物理页 1，Introduction 对 refs. [1]–[19] 的归类）参考文献表进一步给出了这些路线的代表工作，包括 circuit partition/event-driven 方法、latency-based 与 transmission-line link、MMC/PET 的 high-speed EMT equivalent、MATE/multilevel MATE，以及 hierarchical linking-domain decomposition。[pdf:E18]（PDF 物理页 18，References [1]–[12]）[pdf:E19]（PDF 物理页 19，References [13]–[30]）

作者自己的直接前作 MAHE [20] 已经能把同一串联回路中的接口合并为 Thévenin equivalents，把同一并联节点中的接口合并为 Norton equivalents；region-folding [21] 又能把重复拓扑实例聚合成 batched matrix calls。[pdf:E01]（PDF 物理页 1，Introduction）问题不是这些方法“没有并行”，而是它们仍可能把所有回路或并联节点放入一个较大的 linking matrix。以本文的记号说，每新增一个 series loop 或 parallel node 都可能增加 \(\sum M_jG_jM_j^T\) 的维数，矩阵求逆或线性求解最终成为新的瓶颈。[pdf:E12]（PDF 物理页 12，Case Study 1 setup 与复杂度说明）

论文真正改变的对象因而不是单个 circuit partition，而是“partition 之间的连接关系”。它新增 linking partition：一种不含电气元件、只容纳 subcircuit/sub-linking partitions 及其连接方程的结构容器；再把 circuit partition 作为树叶、linking partition 作为非叶节点，形成 hierarchical partition tree。[pdf:E02]（PDF 物理页 2，Figs. 1–3 与 Section II）与笼统的“采用层次结构”相比，本文更具体的贡献是：把 mixed Thévenin/Norton interface 在树上递归合并、变换和向上传递，再用 hourglass scheduling 把同层无依赖实例组成 batch。[pdf:E01]（PDF 物理页 1，three contributions）

这里的 novelty 判断只能限定为“论文相对其自述 prior work 的定位”。参考文献中本来就有 hierarchical modeling、multilevel MATE 和 hierarchical linking-domain decomposition；本卡没有做论文之外的系统检索，因此不声称“hierarchy 本身”或“树形分解本身”是首次提出。

## § 3 — 重建作者的思考路径

以下是基于论文问题陈述的逆向重建，不是作者逐字给出的研究日志。

第一步，先承认 modular power electronics 的重复性既是负担也是机会。若把每个模块都展开到一个全局矩阵，变量数会随模块数增长；但很多模块的本地拓扑和矩阵形状相同，真正不同的只是实例数据。已有 region-folding 已说明，同构实例可以进入 homogeneous BLAS batch，而不必改变每个 kernel 的形状。[pdf:E09]（PDF 物理页 9，Fig. 14 后的 region-folding 讨论）

第二步，把 Kirchhoff 规律当成“可组合接口”的物理依据。串联回路满足 KVL，电压降可相加，所以适合保留 impedance/Thévenin 形式；并联节点满足 KCL，注入电流可相加，所以适合保留 admittance/Norton 形式。[pdf:E03]（PDF 物理页 3，Section II 核心概念）这一步给出了一个局部接口语言，但还没有解决接口数量持续增长的问题。

第三步，观察真实大型系统不是一层平面连接，而常常是“submodule → converter → station → system”的嵌套结构。若能把“连接关系”也包装成没有元件的 linking partition，那么一个子树就可以先在本地消掉 enclosed couplings，只向父层暴露 open couplings。于是，上一层看到的不是全部底层变量，而是一个较小的 mixed Thévenin/Norton port。[pdf:E05]（PDF 物理页 5，Fig. 6 与 enclosed/open coupling）

第四步，树上的数据依赖天然分成两个方向：等效量必须从叶到根聚合，根处求出全局 series currents 与 parallel voltages 后，又必须从根到叶回代。把前半程看作 leaf peeling，把后半程看作 champagne tower，便得到 hourglass scheduling；同一层无父子依赖的 partition 可以放进一个 batch。[pdf:E08]（PDF 物理页 8，Section VI-A）[pdf:E09]（PDF 物理页 9，Figs. 12–14）

这条思路的关键不是“把矩阵并行化”本身，而是先用物理接口和树结构改变矩阵问题的形状，再让 BLAS/OpenMP 吃到规则、同构且同层独立的工作量。

## § 4 — 核心 Intuition

HMAHE 的 intuition 可以压缩为三句话：不要一次性解所有 partition 之间的 series current 和 parallel voltage，而要让每个子树先把内部闭合的 KVL/KCL 关系消掉，只向父层交出一个 mixed Thévenin/Norton interface。沿 partition tree 从叶到根递归合并这些接口，在根处只解最高层 coupling variables，再从根到叶回代。这样，系统规模主要增加的是同构 partition 实例和可批处理工作，而不是必然增加同一个 linking matrix 的维数。[pdf:E03]（PDF 物理页 3，Fig. 4 与核心说明）[pdf:E07]（PDF 物理页 7，Fig. 11）

## § 5 — 具体方法与完整 Pipeline

以论文的 scalable PV station 为例，一个可读的输入是：若干 PV panel + boost converter 组成 circuit partition 0，grid-tie dc/ac converter 是 circuit partition 1，两者被 linking partition 1 包装成 PV generation system；多个 station 再并到 circuit partition 2 所代表的 380 V AC grid。论文用 linking partition 1 的 duplicate 属性把系统从 \(2\times1\) 扩展到 \(2\times32\) 套发电系统，而树的类型结构不变。[pdf:E15]（PDF 物理页 15，Case Study 2 setup）[pdf:E16]（PDF 物理页 16，Figs. 29–32）

完整 pipeline 如下。

1. **解析结构，只做一次初始化。** C 程序读取描述 circuit/control units 的 markup simulation file，递归构造 partition tree。circuit partitions 必须是叶节点；linking partitions 是可嵌套的非叶容器。接着执行 leaf peeling 与 champagne tower，生成 hourglass 各层 batch。[pdf:E10]（PDF 物理页 10，Program Code Structure）[pdf:E11]（PDF 物理页 11，Fig. 16）

2. **为 circuit partition 建 mixed interface。** 每个本地 nodal equation 先写成 \(u_j=Z_j(h_j+y_j)\)。置换矩阵 \(S_j\) 把节点按 internal、series、parallel 排列；内部变量被隐藏，只留下 series-side voltage/current 与 parallel-side voltage/current。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(7)）随后交换 parallel voltage 与 parallel current，把串联部分保持为 impedance，把并联部分改写为 admittance，得到 Eq. (8) 的 hybrid excitation 与 hybrid interface；\(P_j,Q_j\) incidence matrices 负责把局部端口映射到父 linking partition 的 coupling list。[pdf:E04]（PDF 物理页 4，Eqs. (8)–(12) 与 Fig. 5）

3. **在 linking partition 内先闭合、再向上暴露。** 同一 linking partition 收集所有子 partition 的 hybrid equivalents。closure matrix \(C_k\) 把 coupling 分为 enclosed series、enclosed parallel、open series、open parallel 四组；enclosed series loop 用 KVL 令电压和为零，enclosed parallel node 用 KCL 令电流和为零，于是内部 coupling 不必传给父层。[pdf:E05]（PDF 物理页 5，Eqs. (14)–(19)）

4. **把剩余 open interface 重新变成可递归的同一语言。** open coupling 先从 hybrid form 还原成 impedance form，再按父层视角用 \(S_k\) 排列，最后重新交换 parallel voltage/current，得到与 circuit partition 相同形状的 mixed interface。Eq. (26) 的输出仍是 series voltage 与 parallel current，输入仍是 series current 与 parallel voltage，所以相同变换可以递归到 root linking partition。[pdf:E06]（PDF 物理页 6，Eqs. (20)–(26) 与 Figs. 7–9）\(P_k,Q_k\) 再把这个 interface 映射到更高一层。[pdf:E07]（PDF 物理页 7，Eqs. (27)–(29) 与 Fig. 10）

5. **一个 timestep 的 bottom-up solve。** 更新 voltage/current sources 与 control signals，并按开关器件 ON/OFF 组合选择预计算的 hybrid admittance/impedance matrix；论文没有采用 event-driven variable step，两个案例均使用 1 µs 固定步长。[pdf:E10]（PDF 物理页 10，simulation step 3）[pdf:E12]（PDF 物理页 12，Case Study 1 timestep）[pdf:E15]（PDF 物理页 15，Case Study 2 timestep）先并发计算所有 circuit partitions，再逐层合并 linking partitions，直到 root。

6. **root solve 与 top-down back-substitution。** root 没有外部 coupling，KVL/KCL 直接形成最高层 linking system；求得 root series currents 与 parallel voltages 后，按 Eqs. (30)–(34) 从父层回传到子 linking partitions，再用 Eq. (13) 回到 circuit partitions 求全部 node voltages。[pdf:E08]（PDF 物理页 8，Eqs. (30)–(36)）[pdf:E05]（PDF 物理页 5，Eq. (13)）

7. **控制与并行执行。** 同层同构 matrix-vector/matrix-matrix 工作进入 `cblas_dgemv_batch()` 与 `cblas_dgemm_batch()`；control units 在不同 partition instances 间用 OpenMP fork-join 并行，但同一 instance 内仍按 pipeline 顺序执行。每个并发 step 结束都有同步 barrier，这正是小系统可能出现 multicore “threshold time”的原因。[pdf:E10]（PDF 物理页 10，BLAS 与同步说明）[pdf:E12]（PDF 物理页 12，OpenMP 说明）循环结束后，程序把选定 waveform 数据写成 MAT file。[pdf:E11]（PDF 物理页 11，Fig. 16）

数值实现方面，已报告 kernel 是 `dgemv/dgemm`，即 double-precision BLAS；论文未报告 sparse storage、pivoting、conditioning monitor、fixed-point 或 FPGA mapping。执行平台是 multicore CPU，而不是 FPGA。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的数学主线可以理解为“对 nodal equation 连续做变量重排、Schur-like 消元和端口形式切换”，目的不是创造新的 Kirchhoff 定律，而是保持每一层都拥有同样可组合的 mixed interface。

**第一步：从局部 nodal equation 得到边界方程。** 对 circuit partition \(j\)，

\[
u_j=Z_j(h_j+y_j). \tag{1}
\]

\(u_j\) 是 node-voltage vector，\(Z_j\) 是 impedance matrix，\(h_j\) 包含 history current 与真实 current source，\(y_j\) 是外部注入。置换矩阵 \(S_j\) 把变量分成 internal \(r\)、series \(s\)、parallel \(p\) 三组；隐藏 internal block 后，边界只依赖 excitation 与 \((i_{sj},u_{pj})\)。[pdf:E03]（PDF 物理页 3，Eqs. (1)–(7)）

**第二步：把边界改写成 mixed Thévenin/Norton form。** 交换 parallel 侧的 \(u_{pj}\) 与 \(i_{pj}\)，Eq. (8) 可概括成

\[
\begin{bmatrix}u_{sj}\\ i_{pj}\end{bmatrix}
=
\underbrace{\begin{bmatrix}B_j^1&B_j^2\\B_j^3&B_j^4\end{bmatrix}}_{\text{hybrid excitation transform}}
\begin{bmatrix}e_{sj}\\e_{pj}\end{bmatrix}
+
\underbrace{\begin{bmatrix}G_j^1&G_j^2\\G_j^3&G_j^4\end{bmatrix}}_{\text{series impedance / parallel admittance}}
\begin{bmatrix}i_{sj}\\u_{pj}\end{bmatrix}. \tag{8}
\]

直觉是：串联侧输出电压、输入电流，像 Thévenin/impedance；并联侧输出电流、输入电压，像 Norton/admittance。于是同一 series loop 的 voltage drop、同一 parallel node 的 injection current 都能线性相加。[pdf:E04]（PDF 物理页 4，Eq. (8)）

**第三步：在 linking partition 内消掉 enclosed couplings。** incidence matrices \(P_j,Q_j\) 把每个子 partition 的局部接口放入父层 coupling list，所有子项相加形成 Eq. (14)。closure matrix \(C_k\) 再把这些和重排为 enclosed/open 四组。对 enclosed series 与 enclosed parallel，分别代入

\[
\sum u^{k,\mathrm{enclosed}}_{sj}=0,\qquad
\sum i^{k,\mathrm{enclosed}}_{pj}=0,
\]

这就是 KVL/KCL。Eqs. (15)–(19) 随后把 enclosed variables 隐藏，只保留会与父层交互的 \(u_{sk}^{open},i_{pk}^{open},i_{sk}^{open},u_{pk}^{open}\)。[pdf:E05]（PDF 物理页 5，Fig. 6 与 Eqs. (14)–(19)）

**第四步：证明递归闭包。** 对 open interface 做 inversing transformation 得到 Eq. (20)，再经 \(S_k\) 重排并把 parallel 部分换回 admittance，得到

\[
\begin{bmatrix}u_{sk}\\ i_{pk}\end{bmatrix}
=
B_k\begin{bmatrix}e_{sk}\\e_{pk}\end{bmatrix}
+
G_k\begin{bmatrix}i_{sk}\\u_{pk}\end{bmatrix}. \tag{26}
\]

它与 Eq. (8) 同构，所以 linking partition 本身可以被父 linking partition 当作一个更大的“虚拟 circuit partition”继续合并。这是 hierarchy 能递归的数学闭包条件。[pdf:E06]（PDF 物理页 6，Eqs. (20)–(26)）

**第五步：root solve 与回代。** \(P_k,Q_k\) 把第 \(k\) 层 interface 映射到第 \(k+1\) 层，Fig. 11 把该映射写成 \(M_kG_kM_k^T\) 型聚合。在 root，外部注入为零，最高层 coupling variables 可概括为

\[
x_{\mathrm{root}}
=-\left(\sum_k M_kG_kM_k^T\right)^{-1}
\left(\sum_k M_kB_ke_k^{\mathrm{root}}\right), \tag{36 的结构}
\]

其中 \(x_{\mathrm{root}}\) 由 root series currents 与 parallel voltages 组成。[pdf:E07]（PDF 物理页 7，Fig. 11）[pdf:E08]（PDF 物理页 8，Eqs. (35)–(36)）之后 Eqs. (30)–(34) 用 inverse permutation/closure matrices 逐层恢复 local couplings，Eq. (13) 再恢复 node voltages。

这套推导证明的是 algebraic equivalence 与可递归的接口形状；论文没有给出这些逆矩阵的 condition-number bound、round-off error bound 或整棵树的 asymptotic complexity theorem。换言之，“等价”有代数结构支撑，“在所有拓扑上都稳定且可扩展”则仍是实验性主张。

## § 7 — 实验设计与结论

论文用两个结构不同但都高度模块化的模型验证 accuracy 与 efficiency，并与匿名的 state-space-based commercial software 1、MNA-based commercial software 2 以及前作 MAHE 比较。MAPE 定义为

\[
\mathrm{MAPE}=\frac{100\%}{n}\sum_{t=1}^{n}\left|\frac{A_t-F_t}{A_t}\right|, \tag{37}
\]

但作者也明确指出，当 \(A_t\) 接近 0 时百分比误差会被异常放大，所以只对远离零的 DC variables 报 MAPE。[pdf:E13]（PDF 物理页 13，Eq. (37) 与说明）

**问题 1：HMAHE 是否保留 switch-level EMT accuracy？ → 实验 → 答案。**  
MMC-HVDC 案例使用 4800 V DC bus、每臂 8 个 submodules、nearest level modulation 和 1 µs timestep；PV 案例使用 620 V PV 输出、1 kV DC bus、boost 与 dc/ac converter 均为 10 kHz switching frequency、同样 1 µs timestep。[pdf:E12]（PDF 物理页 12，Tables I–II）[pdf:E16]（PDF 物理页 16，Table IV）作者比较 start-up 与 steady state 的 AC current、DC voltage、submodule capacitor voltage、active/reactive current、PV voltage 和 boost inductor current。三种软件的波形在图中基本重合，报告的 DC-variable MAPE 处在约 \(10^{-2}\%\) 或更低的量级。[pdf:E13]（PDF 物理页 13，Fig. 22）[pdf:E14]（PDF 物理页 14，Figs. 23–26）[pdf:E17]（PDF 物理页 17，Figs. 33–37）就这两组参数与工况而言，HMAHE 没有以可见的开关波形失真换取速度。

**问题 2：hierarchy 是否改善规模扩展？ → 实验 → 答案。**  
MMC 案例把送端和受端 linking partitions 的 duplicate size 从 1 增至 32；PV 案例把 station 从 2 增至 32。效率试验把 simulation horizon 调为 0.5 s，在同一台双路 Xeon、24-core 机器上报告运行时间均值与标准差。[pdf:E14]（PDF 物理页 14，Fig. 27 setup）[pdf:E17]（PDF 物理页 17，Case Study 2 efficiency setup）HMAHE 的 runtime 曲线随规模增长明显慢于两个 commercial baselines，也优于 flat MAHE 在 linking matrix 变大后的退化趋势。[pdf:E14]（PDF 物理页 14，Fig. 27）[pdf:E18]（PDF 物理页 18，Fig. 38）

具体地，MMC 案例在 commercial software 1 能完成的最大点，即两侧各 4 台 MMC 时，4833 min 对比 single-core HMAHE 5.01 min、multicore HMAHE 9.49 min，对应 964× 与 509×；在两侧各 32 台 MMC 时，commercial software 2 为 264.89 min，对比 32.52 min 与 12.19 min，对应 8.14× 与 21.73×。[pdf:E15]（PDF 物理页 15，Case Study 1 efficiency）PV 案例在 4 个 station 时，commercial software 1 为 871 min，对比 2.61 min 与 2.54 min，对应 333.71× 与 342.91×；在 32 个 station、64 套 generation systems 时，commercial software 2 为 291.25 min，对比 18.23 min 与 3.79 min，对应 15.97× 与 76.84×。[pdf:E18]（PDF 物理页 18，Case Study 2 efficiency）

**问题 3：multicore 是否总比 single-core 快？ → 实验 → 答案是否定的。**  
MMC 两侧少于 4 台时，parallel speed-up 小于 1；小规模系统的同步与调度开销超过了并行收益。[pdf:E15]（PDF 物理页 15，Fig. 28 与正文）PV 案例也呈现相同 crossover：规模增大后 multicore 才超过 single-core。[pdf:E18]（PDF 物理页 18，Fig. 39）这反而增强了实验可信度，因为论文没有把“用了 24 核”包装成无条件加速。

不得外推的范围包括：案例只有 MMC-HVDC 与 PV cluster，扩模主要靠 duplicate 同构单元；commercial software 名称和具体 solver settings 未公开；没有公开源代码、不同 CPU/BLAS 的复测、real-time deadline、fault-rich switching scenario、ill-conditioned network、非规则跨层耦合或 FPGA 结果。因而“在这两个 modular benchmarks 上准确且高效”证据较强，“对任意 scalable power electronics topology 都同样高效”证据不足。

## § 8 — Take-aways

**5 句话。**  
1. HMAHE 把 circuit partition 之间的连接关系也做成可嵌套的 linking partition，从而把一个平面的 linking solve 变成 tree 上的局部消元与根部求解。  
2. 其物理基础是 series impedance 与 parallel admittance 的线性可加性，数学实现是反复切换 Thévenin/Norton hybrid interface。  
3. leaf-to-root 合并与 root-to-leaf 回代形成 hourglass dependency，给 BLAS batch 和 OpenMP 提供同层并行机会。  
4. 在论文的 MMC 与 PV 重复模块案例中，波形与 commercial EMT software 基本一致，而最大报告 speed-up 分别达到 964× 和 76.84×。[pdf:E18]（PDF 物理页 18，Conclusion）  
5. 但可扩展性证据仍依赖“树接口保持较窄、实例高度同构”的结构，且论文没有 FPGA 或 real-time 验证。

**3 句话。**  
HMAHE 的核心是把 mixed Thévenin/Norton equivalent 做成在 partition tree 上闭合的递归接口。hourglass scheduling 让这种代数分层与 batched multicore execution 对齐。实验很有说服力地证明了两个 modular CPU benchmarks，却尚未证明 irregular coupling、数值病态或 FPGA 场景下的普适性。

**1 句话。**  
这篇论文用“先缩小接口问题、再并行同构实例”的方式，让大规模 modular power-electronics EMT 从一个巨型 linking solve 变成可递归、可批处理的树上计算。

## § 9 — 最脆弱的假设

最脆弱的假设是：**随着模块数量增长，系统仍能被分成一棵 open-interface width 较小、同层实例近似独立且大量同构的 partition tree。** 这里的 interface width 是一个子树必须暴露给父层的 open series/parallel coupling variable 数量。只要新增模块主要增加 duplicate instances，而不增加每层 open coupling 的种类和宽度，local matrices 与 hourglass 层数就近似稳定，新增工作会表现为 BLAS batch 中更多独立实例；论文甚至明确说，改变 specific partition 的 instance number 不改变 partition-tree structure。[pdf:E02]（PDF 物理页 2，Section II-C）[pdf:E10]（PDF 物理页 10，Fig. 15 后的 scalability 说明）

这个假设在实际中可能失效。多换流器网络若存在密集的 circulating-current paths、共享滤波器/磁件、跨站 DC/AC coupling、保护联锁或 global control signals，一个子树就可能必须向父层暴露随系统规模增长的 separator。此时上层 \(G_k\) 或 root \(\sum M_kG_kM_k^T\) 仍会变大，递归还会叠加多次 transformation/inversion；HMAHE 可能从“许多小矩阵”退化为“若干仍然很大的矩阵”。

论文提供的支持证据是，MMC 与 PV 两例在 duplicate 1/2 到 32 的扩展下，树结构保持不变，flat MAHE 的 linking matrix 随 series loops/KCL nodes 增大而明显变慢，HMAHE 的 runtime growth 则平缓。[pdf:E15]（PDF 物理页 15，MAHE vs HMAHE 与 Fig. 28）[pdf:E18]（PDF 物理页 18，Figs. 38–39）缺失的证据是：没有用 separator width 随 \(n\) 增长的 irregular topology 做压力测试，也没有报告各层 matrix dimension、condition number、factorization cost 或树构造质量。因此，论文证明了“复制型规模扩展”，尚未证明“耦合复杂度扩展”。

## § 10 — 最小复现实验

一周内最值得复现的不是完整控制系统，而是核心 claim：“在波形等价的前提下，hierarchy 能把由重复并联节点造成的 linking-matrix 增长改成较小 interface 的 batched recursion。”

**数据与模型。** 取论文 PV 案例的 Fig. 29 拓扑、Tables III–IV 参数和 1 µs timestep：每个 station 含两套 PV + boost + grid-tie converter，station 数取 2、4、8、16、32；先只保留论文给出的 voltage/current loops 与 switching frequency，不加入新的故障工况。[pdf:E15]（PDF 物理页 15，Table III 与 setup）[pdf:E16]（PDF 物理页 16，Fig. 29 与 Table IV）

**实现。** 同一份 double-precision 代码实现两个 solver：A 是 flat MAHE，把所有 KCL interfaces 放入一个 linking matrix；B 是两层 HMAHE，先在 station 内合并 Norton equivalents，再在 root bus 求解。第一阶段都只用 single core，排除 OpenMP/MKL scheduling 对算法比较的混淆；第二阶段再把同构 local kernels放入同一个 BLAS batch。每个 switch state 预计算 interface matrix，每步只更新 excitation、选 matrix、bottom-up solve、root solve、top-down back-substitution。

**测量。** 对 0.5 s horizon 记录总 runtime、每步 root/linking solve 时间、每层 matrix dimension、peak memory；另跑 20 ms startup window，与直接 MNA reference 比较 \(u_{dc}\)、\(u_{pv}\)、\(i_L\) 和 grid current。DC variables 用 Eq. (37) MAPE，过零 AC current 改用 normalized RMSE，避免 MAPE 的近零失真。

**预先规定判据。** 这是复现实验自己的判据，不是论文报告值：若所有规模上 DC-variable MAPE < 0.1%、AC normalized RMSE < 0.1%，且 HMAHE 的 root interface dimension 随 station 数保持不变、16/32 station 的 runtime 明显低于 flat MAHE，则核心 claim 得到支持；只要出现波形误差超阈值、root/interface width 实际随规模线性增长，或在 16/32 station 上 HMAHE 不比相同 kernel/backend 的 flat MAHE 快，就算反驳。这个设计能把“代数分层收益”与“多核调度收益”分开。

## § 11 — 最强反例设计

最强反例不是再找一个小系统，而是构造一族**模块数相同、局部元件相同，但跨 partition separator 持续变宽**的网络。具体做法是：从论文的 \(N\)-station PV cluster 出发，不改变每个 station 内部电路；额外给第 \(j\) 个 station 与多个其他 station 加入共享 DC-link impedance、AC tie-line 或 circulating-current branch，使任何 balanced partition tree 的中层 cut 都必须暴露 \(\Theta(N)\) 个 independent series/parallel couplings。控制计算仍用相同 OpenMP，matrix kernels 仍用相同 BLAS，避免后端差异成为替代解释。

实验应同时比较四项：flat MAHE、论文规则生成的 HMAHE、经过 graph partitioning 优化的 HMAHE，以及普通 sparse MNA/Schur solver；横轴不是只有 module count，还要画 measured separator width。若在相同 waveform tolerance 下，HMAHE 的 root/intermediate matrix dimension、runtime 或 memory 与 flat MAHE 同阶，甚至因为层层 transformation 更差，那么“hierarchy 本身带来 scalable simulation”的广义说法就被推翻。结果会支持一个更窄的替代解释：论文的大 speed-up 主要来自被测系统的 homogeneous duplication、固定宽度接口和 batched kernels，而不是对 arbitrary large-scale coupling 的普适优势。

还应在同一反例里逐步降低 line resistance 或把 resonance 调到 timestep 敏感区，监测 Eq. (20)、Eq. (26)、Eq. (36) 所需逆矩阵的 condition number。若接口变宽尚未击败 HMAHE，但数值病态导致误差随树深累积，也会揭示论文未分析的第二条失败路径；不过首要攻击仍是 separator width，因为它直接针对论文的 scalability mechanism。

## § 12 — Follow-up Research Idea

**候选研究方向：从“按设备层级建树”改为“按 separator complexity 与 numerical conditioning 自动选择求解结构”，建立带可证伪 cost certificate 的 adaptive HMAHE。** 这是基于本文证据的候选判断；本卡没有做外部相关工作检索，不声称 novelty。

（a）未满足的需求是，工程模型并不总是规则复制。用户需要在仿真前知道：给定拓扑是否真的适合 HMAHE、哪一层会成为 bottleneck、multicore crossover 在哪里，而不是先跑完大模型后才从 runtime 曲线判断。

（b）它可能产生本领域认可的研究价值，因为电力电子 EMT 的高影响工作不仅看加速倍数，还看 switching fidelity、广泛拓扑适用性、可复现实现和实际硬件可执行性。若能把“可扩展”从一个案例结论变成由 separator width、matrix conditioning、batch homogeneity 和 memory traffic 共同决定的预测式，并在 MMC、PV、PET、multi-terminal DC 等不同 coupling graphs 上通过，就会改变模型组织和 solver selection 的问题定义。

（c）可借鉴相邻领域的 graph tree decomposition、nested dissection、sparse multifrontal solver、low-rank separator compression 与 performance modeling。系统不再强制所有子树使用同一种 hybrid recursion：窄且良态的 separator 用 HMAHE，宽但低秩的 separator 用 compressed Schur interface，宽且病态的部分留给 sparse direct solve；输出不仅是 partition tree，还包括预测 matrix sizes、condition risks、parallel batch sizes 与 runtime range。

（d）第一个证伪实验应生成三族具有相同 component count、但 separator width 分别为 \(O(1)\)、\(O(\sqrt N)\)、\(O(N)\) 的 converter networks。若 cost certificate 不能正确排序三族实际 runtime/memory，或 adaptive solver 在宽 separator 族上不优于最好的 fixed baseline，同时仍保持 switch-level waveform tolerance，这个研究想法就被证伪。

（e）它与本文的实质区别不是“再加一个 graph partitioning 模块”，而是把研究目标从“在预先给定 hierarchy 上递归做 MAHE”改成“以 coupling-graph complexity 和 numerical risk 为一等对象，自动决定 hierarchy 是否成立、哪里应该停止递归以及应选哪类 interface solver”。这直接回应第 9 节最脆弱的假设，也能为将来 FPGA/heterogeneous implementation 提供更诚实的边界：只有 cost certificate 预测出 bounded interface、regular batch 与可控 condition number 的部分，才值得进一步做 fixed-point、pipeline 和片上资源映射。
