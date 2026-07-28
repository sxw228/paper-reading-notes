# Wang et al. 2025：面向并行 EMT 的 state-variable-preserving 建模

作者：Qiguo Wang、Jin Xu、Keyou Wang、Guojie Li、Zhenyuan Feng  
出处：*IET Generation, Transmission & Distribution*，2025，19:e70013  
DOI：10.1049/gtd2.70013  
Zotero key：GADZUETV

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文原文明确声称。** 可再生能源电站的 EMT 仿真面对一个直接冲突：聚合模型虽然快，却不能忠实表达站内故障、多个电站的级联事故，以及电站与电网之间的振荡；完整 detailed model（DM）保留微秒级开关过程和站内拓扑，却会随着 inverter-based resources（IBR）数量增长形成高维求解负担。作者要解决的不是一般意义上的降阶，而是：在保留每个发电单元原始状态变量和开关行为的前提下，消去外部系统不必看到的内部节点，并把一个由大量 IBR 组成、经公共母线连接的电站拆成适合无延时并行求解的子系统。[pdf:E01]（PDF 物理页 1，Abstract 与 Introduction）

这个问题重要，是因为站内故障和次同步振荡恰好取决于单元内部动态与控制状态；把几十或上百台设备聚成一台等值机，可能得到“电站总功率差不多”的结果，却失去保护动作、局部故障传播和单元间差异所需的信息。反过来，如果只能运行全详细模型，规模扩大后的计算时间会使大量工况扫描、在线分析乃至实时仿真失去可行性。论文因此同时提出 state-variable-preserving（SVP）单元模型和 node tearing 网络分区：前者收缩每个单元对外暴露的求解规模，后者把公共母线电压作为低维关联变量，减少分区间串行瓶颈。[pdf:E01]（PDF 物理页 1，Abstract）

**基于证据的合理推断。** 这项工作的价值不只在“单次仿真更快”，还在于把精度问题和并行问题分开：单元内部的物理状态由 SVP 保存，分区间的数据依赖由 node tearing 处理。若这两个层次确实能独立成立，就可以在不更换研究对象的情况下，把同一类详细 EMT 模型映射到更多 CPU 核或其他高并行硬件。

## § 2 — 前人工作与不足

**相关文献中的已有结论。** 论文把既有提速路线分为三组。第一组是 device-level 简化，包括 average-value model 和 dynamic phasor model；它们通过忽略或平滑开关过程来增大步长。第二组是 station-level 聚合，包括 single-machine equivalent 和按工况聚类的 multi-machine equivalent；它们减少电站内等值单元数。第三组保留详细 EMT，但改进求解：matrix exponential 与 Krylov subspace 用于多时间尺度或高维状态空间，state-space nodal method 通过状态变量分组消除组内节点，已有 integrated equivalent model 则把风电设备的 EMT 电路组合成电站等值。[pdf:E01][pdf:E02]（PDF 物理页 1–2，Introduction）

作者指出这些路线各有硬缺口。平均值/相量模型省略器件开关，电站聚合模型丢失站内结构，因此不适合内部故障与电站—电网振荡；已有 integrated equivalent 在结构变化时要重建，且能消掉的节点有限，规模仍随新能源单元数增长。[pdf:E01][pdf:E02]（PDF 物理页 1–2，Introduction）

并行 EMT 的既有接口又分成 delay-based 与 delay-free。semi-implicit delayed decoupling 和 latency insertion 能做细粒度分区，但交互延时带来误差，常需微秒级步长维持数值稳定。Diakoptics、bordered block diagonal、compensation model、multi-area Thévenin equivalent 以及 node splitting 属于无延时分区，但本质上多沿支路切分；当许多发电簇连到同一公共母线时，需要串行求解的关联电流维数随分区数增长。论文也列出 loop-current tearing、nested fast simultaneous solution 与 linking-domain extraction，但明确说这些方法针对特定拓扑，难以直接用于新能源电站解耦。[pdf:E02]（PDF 物理页 2，Introduction）

**边界说明。** 上述优缺点是本文作者对相关工作的归纳，不等于本卡独立复核了每篇被引论文；尤其“难以应用”的程度仍需回到各原始文献验证。

## § 3 — 重建作者的思考路径

下面是**基于证据的合理推断**，不是作者逐字陈述的发明过程。

第一步，研究者会发现，真正需要保留的是决定未来演化的状态变量，而不是每个内部节点都必须对全网联立求解。控制理论告诉我们，一个系统的离散 state-space 表达可以从输入和状态得到输出；EMT 中电感、电容经 trapezoidal integration 后，本来就由等值导纳与历史电流源表达。因此可以尝试把内部节点方程代数消元，同时把动态元件的历史电流继续作为状态保存。[pdf:E03][pdf:E04]（PDF 物理页 3–4，Sections 3.1–3.1.5）

第二步，消元后的单元若只向外呈现三相端口，就能写成“受控等值导纳 + 受控历史电流源”。开关状态并未被平均掉，而是选择不同的系数矩阵；控制器仍按 MPPT、PI 与 PWM 的离散流程更新开关。[pdf:E05][pdf:E06]（PDF 物理页 5–6，Sections 3.2–3.3，Figure 4）

第三步，即使每个单元变小，整站仍会随单元数增长。观察电站拓扑后，关键不是任意找一条支路切开，而是利用“多个 PV cluster 同接一个 35 kV 公共母线”的结构，把母线三相电压设为唯一关联量。先串行求这个三维变量，再并行回代各簇节点电压；这比每个分区都引入三相关联电流更适合公共母线拓扑。[pdf:E06][pdf:E07]（PDF 物理页 6–7，Figures 5–6，Equations 12–14）

第四步，单元内部状态更新彼此独立，簇级节点方程在公共母线电压已知后也彼此独立，于是自然得到两层并行：底层并行模型更新，顶层并行分区求解。[pdf:E08][pdf:E09]（PDF 物理页 8–9，Figures 7–8）

## § 4 — 核心 Intuition

SVP 的核心是：**保留会影响下一时刻的状态，不保留全网无需显式求解的内部节点**；通过离散状态空间消元，一个开关型 PV 单元对外只表现为三相端口上的受控导纳和受控历史电流源。[pdf:E04][pdf:E06] node tearing 的核心是：**公共母线拓扑真正共享的是母线电压，而不是每个分区各自的一组切口电流**；把这一个三相电压作为关联变量，就能把串行界面的维数从 \(3n\) 降为 3。[pdf:E07]

## § 5 — 具体方法与完整 Pipeline

以论文中的 collecting-and-distributing PV plant 为例，输入是 \(n\) 个并联到 35 kV 母线的 PV clusters；每簇含 \(m\) 个串联连接的 PV generation units，每个单元含 \(k\) 个并联 DC/DC converters。单元电路由 PV array、Boost、VSC 与 LCL filter 组成。[pdf:E03][pdf:E09]（PDF 物理页 3、9，Figures 2、9）

1. **建立单元电气方程。** PV array 用非线性伏安关系表示；开关和二极管采用小导通电阻开关模型，开通导纳取 \(10^6\)，关断取 0；电感、电容用 trapezoidal method 的 companion circuit 表示。作者把 filter outlet 定义为外部输出节点，其余为内部节点，形成内部节点电压方程、历史电流更新式和端口电流式。[pdf:E04]（PDF 物理页 4，Equations 1–5）
2. **代数消去内部节点。** 选动态元件历史电流 \(\mathbf I_{\mathrm{hPV}}\) 为状态、端口电压 \(\mathbf U_{\mathrm{PV}}\) 为输入、端口电流 \(\mathbf I_{\mathrm{PV}}\) 为输出，将节点方程整理为离散状态空间 Equation (6)，再由 Equation (7) 给出六个系数矩阵 \(\mathbf A_{\mathrm{PV}}\) 到 \(\mathbf F_{\mathrm{PV}}\)。内部节点电压不再出现在端口输出式中。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Equations 6–7）
3. **保留控制与开关。** Boost controller 保留 perturb-and-observe MPPT、外电压环、内电流环和 PWM；inverter controller 保留 DC 电压/无功外环与 \(dq\) 电流内环。离散控制根据上一时刻的电压、电流和控制量生成 Boost 与 inverter 的开关状态，再据此选取/更新 SVP 系数矩阵。[pdf:E05]（PDF 物理页 5，Equations 8–11，Figure 3）
4. **形成 SVP 端口模型。** 每个单元对外收缩为一个 single three-phase node，即受开关状态和内部状态控制的等值导纳与历史电流源组合。与拓扑有关的系数矩阵可由 netlist、元件类型/参数和开关状态在初始化阶段生成并存储。[pdf:E06]（PDF 物理页 6，Figure 4 与 Section 3.3）
5. **按公共母线做 node tearing。** 全站 nodal admittance matrix 写成各分区对角块与公共母线关联块。Equation (13) 先用各分区的 Schur-complement 贡献求公共母线电压 \(\mathbf U_p\)，Equation (14) 再并行回代 grid-side partition 与各 PV clusters 的节点电压。[pdf:E07]（PDF 物理页 7，Equations 12–14）
6. **执行层次并行时间步。** 每步先更新控制器、开关和单元 SVP 系数，形成各簇 \(\mathbf Y_{kk}\) 与 \(\mathbf I_k\)；再求关联母线 \(\mathbf U_p\)；随后并行求 \(\mathbf U_g,\mathbf U_1,\ldots,\mathbf U_n\)，并并行更新内部历史电流。底层并行不同单元的状态与端口量，顶层并行不同分区的节点方程。[pdf:E08][pdf:E09]（PDF 物理页 8–9，Figures 7–8）

输出包括每个分区的节点电压、每个单元端口电流以及被保留的内部历史状态。论文实际执行平台是 multi-core CPU，不是 FPGA；也未报告定点数表示、片上存储布局、流水线、资源占用、时序收敛或 FPGA 实时步长。作者只在结论中建议更大网络可配合 CPU clusters 或 GPUs。[pdf:E09][pdf:E11]（PDF 物理页 9、11）

## § 6 — 核心数学推导

先看单元内部。内部节点的 nodal analysis 可写为

\[
\mathbf Y_{\mathrm{in}}(t)\mathbf U_{\mathrm{in}}(t)=\mathbf I_{\mathrm{in}}(t),\qquad
\mathbf I_{\mathrm{in}}(t)=\mathbf I_{\mathrm{inj}}(t)-\mathbf M_{\mathrm{h-in}}^{T}\mathbf I_{\mathrm{hPV}}(t)+\mathbf Y_{\mathrm{o-in}}^{T}\mathbf U_{\mathrm{PV}}(t).
\]

这里 \(\mathbf M_{\mathrm{h-in}}\) 记录每个历史电流源流入/流出哪个内部节点，\(\mathbf Y_{\mathrm{o-in}}\) 记录内部节点与输出节点的导纳连接。companion circuit 的历史电流按 Equation (3) 用上一时刻内部/端口电压及历史值更新，而端口电流由 Equation (5) 得到。[pdf:E04]（PDF 物理页 4，Equations 2–5）

消去 \(\mathbf U_{\mathrm{in}}\) 后得到论文的核心离散形式：

\[
\begin{aligned}
\mathbf I_{\mathrm{hPV}}(t)
&=\mathbf A_{\mathrm{PV}}\mathbf I_{\mathrm{hPV}}(t-\Delta t)
+\mathbf B_{\mathrm{PV}}\mathbf U_{\mathrm{PV}}(t-\Delta t)
+\mathbf E_{\mathrm{PV}}\mathbf I_{\mathrm{inj}}(t-\Delta t),\\
\mathbf I_{\mathrm{PV}}(t)
&=\mathbf C_{\mathrm{PV}}\mathbf I_{\mathrm{hPV}}(t)
+\mathbf D_{\mathrm{PV}}\mathbf U_{\mathrm{PV}}(t)
+\mathbf F_{\mathrm{PV}}\mathbf I_{\mathrm{inj}}(t).
\end{aligned}
\]

其中 Equation (7) 明确给出六个矩阵，例如
\(\mathbf A_{\mathrm{PV}}=\mathbf K-2\mathbf Y_{\mathrm{h-in}}\mathbf Y_{\mathrm{in}}^{-1}(t-\Delta t)\mathbf M_{\mathrm{h-in}}^{T}\)，
\(\mathbf D_{\mathrm{PV}}=\mathbf Y_{\mathrm{o-in}}\mathbf Y_{\mathrm{in}}^{-1}(t)\mathbf Y_{\mathrm{o-in}}^{T}-\mathbf Y_{\mathrm{o-PV}}\)。工程直觉是：\(\mathbf Y_{\mathrm{in}}^{-1}\) 把内部节点的即时线性约束折叠进端口系数，历史电流仍作为显式状态跨时间步传播，所以“节点被消掉”不等于“动态被聚合掉”。[pdf:E04][pdf:E05]（PDF 物理页 4–5，Equations 6–7）

再看全站。Equation (12) 把 grid、各 PV cluster 和公共母线分成 block matrix。对各非公共分区做 block elimination 后，公共母线电压为

\[
\mathbf U_p=
\left(\mathbf Y_{pp}-\mathbf Y_{pg}\mathbf Y_{gg}^{-1}\mathbf Y_{gp}
-\sum_{k=1}^{n}\mathbf Y_{pk}\mathbf Y_{kk}^{-1}\mathbf Y_{kp}\right)^{-1}
\left(\mathbf I_p-\mathbf Y_{pg}\mathbf Y_{gg}^{-1}\mathbf I_g
-\sum_{k=1}^{n}\mathbf Y_{pk}\mathbf Y_{kk}^{-1}\mathbf I_k\right).
\]

得到 \(\mathbf U_p\) 后，每个分区都可独立按 Equation (14) 回代。三相公共母线使 \(\mathbf U_p\) 的维数固定为 3；作者对比说，沿 \(n\) 个支路切分需要 \(3n\) 维关联电流。因此 node tearing 不是减少各分区本体矩阵的阶数，而是缩短必须串行完成的接口求解。[pdf:E07]（PDF 物理页 7，Equations 12–14 及其后正文）

**不确定性。** 论文没有给出这些矩阵的条件数、稀疏实现细节或浮点误差传播界，也没有形式化证明 SVP 与 DM 在任意非线性开关事件下严格等价；可靠性主要由后续数值实验支持。

## § 7 — 实验设计与结论

**问题 1：SVP 能否保持站内故障响应？ → 实验。** 作者设 \(n=3,m=10,k=6\)，switching frequency 为 5 kHz，以 PSCAD fully detailed model 为 DM 基线；在 \(t=0.8\) s 于 cluster 1 的 PV unit 2 出口施加持续 40 ms 的三相接地故障，比较 35 kV bus voltage \(V_c\)、该单元 DC voltage \(V_{dc2}\) 与 active power \(P_2\)。→ **答案。** 图 10 中 SVP 与 DM 波形高度重合，作者报告相对误差均小于 3%。[pdf:E09][pdf:E10][pdf:E11]（PDF 物理页 9–11，Section 6.1.1，Figure 10，Conclusion）

**问题 2：SVP 能否保留由单元控制参数引起的振荡？ → 实验。** \(t=0.5\) s 时把 cluster 1、PV unit 1 的 inverter voltage outer-loop gain 从 1 阶跃到 10，并比较 SVP、DM 与 aggregation model（AM）的 35 kV 母线波形及 Fourier result。→ **答案。** SVP 与 DM 均得到 0.17 p.u./30.0 Hz，AM 得到 0.13 p.u./30.1 Hz；作者据此认为 SVP 保留了内部状态所决定的振荡，而 AM 的幅值偏差可能影响保护动作时刻和位置。[pdf:E09][pdf:E10]（PDF 物理页 9–10，Section 6.1.2，Figure 11）

**问题 3：开关状态和步长是否破坏数值稳定性？ → 实验。** 作者计算不同 switch states 与 10/20 µs simulation step 下 state matrix 的 dominant eigenvalues，并观察其相对 unit circle 的位置。→ **答案。** 开关状态变化对 dominant eigenvalue 分布无显著影响，但步长增大使特征值向单位圆边界移动，可能诱发数值振荡；论文因此只证明了所选步长下的稳定性，没有给出一般稳定步长上界。[pdf:E10][pdf:E11]（PDF 物理页 10–11，Figure 12 与 Section 6.1.3）

**问题 4：规模扩大时是否真正提速？ → 实验。** 平台为 12th Gen Intel Core i7-12700H；DM 与 SVP 均用 C++，步长 10 µs、仿真时长 1 s，并用 Windows timing functions 计时。PV unit 数为 1、10、20、50、100 时，DM 用时依次为 12.146、1035.756、3432.948、13,367.593、47,851.882 s；SVP 用时为 7.778、38.342、62.863、134.287、328.594 s，对应 speedup 1.56、27.01、54.61、99.55、145.63。[pdf:E09][pdf:E11]（PDF 物理页 9、11，Section 6.2，Table 1）

这些数字支持“该实现的优势随站规模增大”的 claim，但不能直接外推到实时硬件。论文没有报告各算法的线程数绑定、CPU 利用率、内存流量、并行调度开销或 PSCAD 与 C++ 实现之间的等实现公平性，也没有 FPGA/GPU 实测。作者自己指出，多核 CPU 的线程数不足以一次并行求完所有独立状态，重复批次计算仍使 SVP 时间随单元数增长。[pdf:E11]（PDF 物理页 11，Section 6.2）

附录给出的主要电气参数包括 light intensity 1200 W/m²、temperature 25°C、\(C_f=10\) mF、\(L_b=2\) mH、\(C_{dc}=10\) mF、LCL 中 \(L_1,L_2,L_3=2\) mH、\(C_1,C_2,C_3=0.1\) mF、\(L_4,L_5,L_6=0.5\) mH，低压/高压变压器短路参数分别为 \(0.001+j0.15\) p.u. 与 \(0.001+j0.1\) p.u。[pdf:E12]（PDF 物理页 12，Table A1）

## § 8 — Take-aways

**5 句话。**

1. SVP 用离散状态空间消掉单元内部节点，但继续显式更新动态元件历史电流与控制状态，因此目标不是传统 aggregation。[pdf:E04][pdf:E06]
2. 一个 PV unit 对外被压缩为 single three-phase node 上的受控导纳和受控历史电流源，开关状态通过六个系数矩阵进入模型。[pdf:E05][pdf:E06]
3. node tearing 把公共母线三相电压当作关联变量，使接口维数为 3，而 branch cutting 在 \(n\) 个分区下为 \(3n\)。[pdf:E07]
4. 两层并行分别利用单元状态更新和分区节点求解的独立性。[pdf:E08][pdf:E09]
5. 单个 CPU 案例显示小于 3% 的故障误差、与 DM 一致的 0.17 p.u./30.0 Hz 振荡结果，以及 100 单元时 145.63 倍 speedup，但尚无跨拓扑、跨平台或实时硬件验证。[pdf:E10][pdf:E11]

**3 句话。** 这篇论文把“保状态”和“消节点”同时实现，再利用公共母线结构把全站接口压成一个三相电压。[pdf:E04][pdf:E07] 它的实验说明这种结构化消元在所测 PV plant 上比 aggregation 更忠实、比 DM 更快。[pdf:E09][pdf:E10][pdf:E11] 最大的未决问题是：当单元不再是单一三相端口、簇之间不再只经一个公共母线耦合时，精度与并行优势还能保留多少。

**1 句话。** SVP + node tearing 的本质，是只把真正跨边界的三相母线电压留给串行求解，其余原始动态状态留在可并行的单元内部。

## § 9 — 最脆弱的假设

最脆弱的假设是：**每个 IBR 单元对站级网络可完整收缩为一个三相 AC 端口，而各发电簇之间只通过同一个三相公共母线发生需要即时联立的耦合。**

这个假设一旦不成立，两部分贡献会同时受损。若单元之间共享 DC bus、公共控制器、保护逻辑、通信状态或额外接地/共模通道，单元状态更新就不再彼此独立；若电站存在多个联络母线、环网或跨簇支路，关联变量也不再是固定三维的 \(\mathbf U_p\)。此时强行只保留单一 AC 端口会丢失物理耦合，而把缺失耦合全部升级为接口变量又会使 node tearing 的低维串行优势消失。

论文提供的证据是一个 collecting-and-distributing PV topology：多个 PV clusters 并联到同一 35 kV bus，且 Figure 8 的层次并行明确依赖各单元内部状态独立、各分区在 \(\mathbf U_p\) 已知后独立。[pdf:E06][pdf:E08][pdf:E09]（PDF 物理页 6、8–9，Figures 6、8、9）但论文没有用多母线、共享 DC link、集中式保护或跨单元控制做压力测试。因此，**论文原文证明的是该拓扑上的可行性；将它推广为任意 IBR 电站的普适接口，是尚未闭合的不确定推断。**

## § 10 — 最小复现实验

一周内最值得复现的不是整座 100-unit 电站，而是“SVP 是否在同一开关序列下保存 DM 的内部状态到端口映射”。

1. 用 Table A1 参数搭一个 PV array + Boost + VSC + LCL 的单单元 DM，步长先固定为 10 µs；动态元件全部用与论文一致的 trapezoidal companion model。[pdf:E04][pdf:E12]
2. 从同一 netlist 构造 Equations (2)–(7) 的 SVP 矩阵。第一阶段让 DM 生成开关序列，并把完全相同的开关序列喂给 SVP，以隔离控制器/PWM 实现差异；第二阶段再加入 Equations (8)–(11) 的控制闭环。[pdf:E04][pdf:E05]
3. 在端口施加电压扰动和一次内部三相接地故障，逐步比较端口电流、DC-link 电压、filter 状态与所有历史电流状态；同时在 1、10、20 个独立单元上记录每步矩阵形成、公共端口求解和状态更新的耗时。
4. **支持标准（复现者预先设定，并非论文原阈值的完整复述）：** 同一开关序列下状态与端口残差接近浮点消元误差；闭环故障波形相对误差不超过论文报告的 3%；增加独立单元数后 SVP 总耗时明显慢于线性增长的 DM。
5. **反驳标准：** 即使强制相同开关序列，SVP 仍出现持续状态漂移、事件时刻错位或端口误差超过 3%；或者速度优势主要来自 DM/PSCAD 与自写 C++ 的实现差异，而在同一代码框架内消失。

这个最小实验首先验证代数机制，再验证闭环实现，能避免“波形看起来接近，但其实两边用了不同开关事件或不同求解器”的替代解释。

## § 11 — 最强反例设计

最强反例是构造一个**双单元、双端口耦合**的电站：两个 VSC 的 AC 侧仍接同一母线，但 Boost/DC 侧共享一个有限阻抗 DC bus，并由集中式保护在任一单元过流时同时改变两台机的限流/闭锁状态。随后在一个单元 DC 侧施加故障，使扰动通过共享 DC bus 和保护状态同时传播到另一个单元。

对照组保留完整共享 DC network 与保护状态联立求解；攻击组按论文默认边界把每台机各自压成 single three-phase AC node，只通过公共 AC 母线 \(\mathbf U_p\) 交换关联量。测量另一台机的 DC voltage、限流触发时刻、AC current、母线电压及 dominant eigenvalues。若攻击组要么漏掉跨单元传播、要么必须把共享 DC 电压和保护状态都提升为新的关联变量才能恢复精度，就说明“保存单元内部状态”本身不足以保证系统级 state-variable-preserving：接口选择才是决定性条件。

这个反例比单纯加大步长更有力，因为它直接挑战论文两层独立性的结构前提，而不是只挑战某个数值参数。论文现有实验只覆盖单公共 AC 母线结构，不能排除该失败模式。[pdf:E08][pdf:E09][pdf:E10]

## § 12 — Follow-up Research Idea

**候选研究方向：从固定 single-port SVP 转向 error-controlled adaptive interface preserving。** 这只是基于本论文局限提出的候选想法；尚未对紧密相关工作做系统检索，因此不声称 novelty。

**（a）未满足需求。** 真实 IBR 电站可能包含共享 DC link、多母线、集中保护与通信耦合。固定把所有内部量隐藏、只留下三相 AC 端口，无法同时保证误差和低维接口；固定把所有可疑量都暴露，又会失去并行收益。

**（b）研究价值。** 电气与电力电子领域通常要求方法同时有数值可信度、故障/控制工况覆盖、工程可实现性和真实平台加速证据。一个能在运行中给出接口误差指示，并只在必要时把某个内部状态“提升”为跨分区关联变量的方法，会把当前“拓扑适配就快”的结果改写为“在给定误差预算下自动寻找最小接口”，这是问题定义的变化，而不只是多加一个硬件后端。

**（c）可借鉴工具。** 可从 graph separator / Schur complement、adaptive domain decomposition、residual-based error estimation 和 hybrid-system event detection 借鉴：离线根据 netlist 找候选 separator，在线监测隐藏状态对端口残差或邻区灵敏度；当阈值越界时临时提升共享 DC voltage、保护状态等变量，稳定后再降回局部状态。

**（d）第一个证伪实验。** 使用 §11 的共享 DC bus 反例，再加入单母线基准；要求自适应方法在两类拓扑上都把关键波形误差控制在预先设定阈值内，同时关联变量维数和 wall-clock time 明显低于“全部边界变量都联立”的保守方案。若它频繁提升变量导致接口规模接近全模型，或在离散保护事件前无法及时预警，该方向即被首个实验否证。

**（e）与本文的实质区别。** 本文预先固定 SVP 单元边界与公共母线关联变量，并在该结构上设计层次并行；候选方法把“哪些状态应留在分区内、哪些必须成为公共关联变量”本身变成受误差约束的在线决策。它延续 Equation (6) 的状态保存和 Equations (13)–(14) 的 block elimination，但不再假设接口永远是单一三相节点。[pdf:E04][pdf:E07]
