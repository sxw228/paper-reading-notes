# Real-Time FPGA-RTDS Co-Simulator for Power Systems

**作者：** Conghuan Yang, Ying Xue, Xiao-Ping Zhang, Yi Zhang, Yuan Chen [pdf:E01]  
**出处：** IEEE Access, Volume 6, pp. 44917–44926 [pdf:E01]  
**年份：** 2018 [pdf:E01]  
**DOI：** 10.1109/ACCESS.2018.2862893 [pdf:E01]  
**Zotero key：** 2REETHNT  
**证据说明：** 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述。** 论文要解决的是：怎样在保持 electromagnetic transient（EMT，电磁暂态）细节和实时步长的同时，把 RTDS 可实时仿真的交流电网规模继续做大。作者把 FPGA 作为 RTDS 的高吞吐扩展，把需要频繁改拓扑、控制器和故障工况的“study system”留在 RTDS，把规模更大但变化较少的“external system”放到 FPGA；两侧都使用 EMT 模型，而不是让 EMT 与 transient stability（TS，暂态稳定）模型相接。论文把贡献概括为 FPGA–RTDS 接口、FPGA 硬件实现与可扩展性，并用一个分区的两区域四机系统和一个 141-bus 系统作验证（PDF 物理页 1，Abstract）。[pdf:E01]

重要性来自两个同时存在、又互相冲突的工程需求。其一，新能源、电力电子和跨区互联使保护、谐波、控制交互及过电压/过电流问题更依赖 EMT 级波形；其二，详细 EMT 模型的计算量限制了可实时求解的交流系统规模。传统做法要么把远端网络等值化而丢掉内部动态，要么把系统拆成 EMT 与 TS 两类模型，但后者的准确性和效率又高度依赖接口技术（PDF 物理页 1，Section I）。[pdf:E02]

**基于证据的推断。** 这篇论文真正瞄准的不是“再做一个更快的单机 EMT solver”，而是把计算规模、建模灵活性和接口一致性三者重新分配：RTDS 提供工程师熟悉的 RSCAD 工作流和易变模型，FPGA 承担规则、重复、可深度流水的外部交流网络计算。价值在于，若这种分工成立，既有 RTDS 用户可以扩展实时 EMT 研究范围，而不必把全部模型、操作界面和结果观察链路迁到一套全新的 FPGA 工具链。

## § 2 — 前人工作与不足

**论文对相关文献的归纳。** 大系统实时仿真的主流折中是 EMT–TS hybrid simulation（混合仿真）。正序等值计算便宜，但在不平衡工况下不准确；扩大接口区域以维持三相平衡会拖慢 EMT 子系统；三序等值在接口处暂态显著时仍可能失真；frequency-dependent network equivalent（FDNE，频率相关网络等值）虽试图降低误差，却把额外计算负担压回 EMT simulator，并仍可能在暂态条件下不准确。作者把根因归结为 EMT 与 TS 使用根本不同的数学模型，因此“既准确又高效”的接口很难设计（PDF 物理页 2，Section I）。[pdf:E03]

另一条路线是直接在 FPGA 上做大规模 EMT。论文指出，已有大交流网 FPGA 实现缺少用于工况操作和结果可视化的 GUI，且未建模同步机励磁与调速系统；面向 MMC 等电力电子装置的 FPGA 实现虽然可获得更小步长，却会遇到系统修改后重新综合耗时、器件拓扑与控制持续演化、通用硬件模型难以稳定抽象等问题。作者因此把 FPGA 的目标限定为模型更成熟、拓扑相对稳定的大型 AC external system，而把灵活性要求高的部分留给 RTDS（PDF 物理页 2，Section I）。[pdf:E04]

不足可以压缩为两类。第一类是**模型语义不一致**：EMT 与 TS 的状态、频率范围和不平衡表示不同，接口等值再复杂也只能近似弥合。第二类是**工具链不完整**：纯 FPGA 方案可能有算力，却不自然具备 RTDS 的交互建模、故障配置和统一可视化。本文的新位置正处在两者之间：它没有消除所有 co-simulation interface（协同仿真接口）问题，而是先消除 EMT–TS 模型类型不一致，再利用传输线传播时延完成显式解耦。

## § 3 — 重建作者的思考路径

下面是基于论文背景与设计约束的逆向重建，不是作者明示的发明时间线。

1. 先承认详细 EMT 是研究快速暂态和不平衡现象所需的模型层级，但 RTDS 资源随网络规模上升很快，因此“全部放进 RTDS”不可持续（PDF 物理页 1，Section I）。[pdf:E02]
2. 再观察工程研究中的网络并非同等易变：关注区需要反复改控制、故障和拓扑，外部网通常更大却更稳定。于是计算平台可以按“修改频率”而不是按“物理元件类型”分工：study system 放 RTDS，external system 放 FPGA（PDF 物理页 4，Section III-A）。[pdf:E05]
3. 为避免 EMT–TS 混合接口的模型变换误差，两侧统一使用 EMT component models；这样接口只传递同一物理层级的端口量，而不再做相量、序分量或频率等值之间的转换（PDF 物理页 2，Section I）。[pdf:E04]
4. 接着寻找能打断代数环的物理边界。若分区边界经过 distributed-parameter transmission line（分布参数传输线），其波传播时间提供了天然延迟；当传播时间不短于一个仿真步，两端可以用上一传播时刻的端口量独立求解（PDF 物理页 4，Section III-A-2）。[pdf:E05]
5. 最后把外部网求解拆成元件类型模块，并让不同模块并行、同类元件流水；系统扩大时优先把新元件塞入现有 pipeline，真正遇到瓶颈才复制模块。这样“网络变大”不必线性地变成“关键路径变长”（PDF 物理页 5，Section IV；PDF 物理页 6，Fig. 7）。[pdf:E06] [pdf:E07]

这条思路的关键转换是：作者不再试图发明一个更复杂的 EMT–TS interface，而是改变分区前提，使接口两边的模型类型相同，并把可解耦性建立在传输线的物理传播延迟上。

## § 4 — 核心 Intuition

把大而稳定的外部交流网编译成 FPGA 上的深流水 EMT engine，把小而常改的研究区保留在 RTDS。两侧经具有传播时延的传输线交换端口电压和电流，因此可以在同一 EMT 语义下各自推进，不必在 EMT 与 TS 之间做近似转换。扩容主要增加流水中的“项目数”，只有超过某个并行模块的时序余量时才需要复制硬件模块。

## § 5 — 具体方法与完整 Pipeline

以 Case 1 的两区域四机系统为例，完整流程如下。

1. **系统分区。** G1、G2 所在区域作为 study system 在 RTDS 中运行；G3、G4 所在区域作为 external system 在 FPGA 中运行；两区由 TL78 连接。论文另在 RTDS 内完整搭建同一系统作为参考，并在 bus 7 施加三相故障（PDF 物理页 6，Section V-A 与 Fig. 8）。[pdf:E08]
2. **建立 FPGA 侧 EMT 元件模型。** 同步机采用 Universal Machine（UM）模型，包含一个 d-axis damper winding 和两个 q-axis damper windings；传输线采用 distributed-parameter model，并在 modal domain 求解后转回 phase domain；电感、电容用 trapezoidal integration（梯形积分）形成 history current 与 constant impedance 的 companion form；故障通过预存的 admittance matrix 和 equivalent resistance 选择，论文还说明多数故障工况实际放在 RTDS 侧以利用 GUI（PDF 物理页 2–3，Section II-A）。[pdf:E09] [pdf:E10]
3. **加入同步机控制和网络求解。** 演示模型包含 IEEE Type AC1A excitation system 与 governor/turbine system；它们同样离散化后按步更新。非线性同步机与线性网络分开求解，compensation method 先得到线性网络的 Thevenin equivalent，再求机端电流，并把机器以 current source 形式送入 nodal equation solver（PDF 物理页 3，Section II-B/C）。[pdf:E11]
4. **形成延迟端口接口。** 边界传输线在两端各表示为一个 Norton equivalent。每一侧只需对端在 \(t-\tau\) 的端电压和线电流；论文要求 wave travelling time \(\tau\) 至少等于一个 simulation time-step，才可保证两侧在当前步计算上解耦（PDF 物理页 4，Section III-A-2 与 Fig. 4）。[pdf:E05]
5. **物理通信与同步。** FPGA 的 SFP transceiver 与 RTDS PB5 processor card 通过双向光纤连接，交换端口电压、电流、RTDS 同步信号和需要显示的 FPGA 输出。论文报告当前链路为 2.0 Gigabaud，并可在每个仿真步、每个方向传输最多 64 个 32-bit signals；FPGA 在每步开始接收同步，数据交换完成后再启动本地网络求解（PDF 物理页 4，Section III-A-2）。[pdf:E12]
6. **在 FPGA 内执行 step 0–6。** Step 0 完成 FPGA/RTDS data exchange；step 1 并行计算 passive elements 与 transmission lines 的 history currents，并预测 rotor speed/angle；step 2 计算 nodal injections 与 Park matrix；step 3 求开路节点电压、\(dq0\) 电压和励磁量；step 4 求 \(dq0\) 定子电流；step 5 求 flux linkage、\(abc\) 定子电流与 nodal voltages；step 6 更新支路电流、电磁转矩和 rotor speed，随后等待本步结束（PDF 物理页 5，Fig. 6 与 Section IV-A）。[pdf:E13]
7. **并行与扩容。** passive element、transmission line、nodal solver、synchronous machine 和 control modules 彼此并行；同类元件在模块内部深度流水。新增 \(k\) 条传输线时，可在现有 transmission-line pipeline 后增加 \(k\) 个 clock cycles；利用传输线对网络矩阵的解耦，扩展块还能与原网络并行求解。若某类元件最终超过该 step 中最长模块的余量，才复制相应模块提高并行度（PDF 物理页 5–6，Section IV 与 Fig. 7）。[pdf:E06] [pdf:E07]
8. **统一观察结果。** FPGA 内部结果经同一光纤送回 RTDS，并在 RSCAD 中与 RTDS 侧信号一起显示。这样用户看到的是一套统一操作与可视化入口，而不是两个割裂的 simulator front-end（PDF 物理页 4–5，Section III-A-3）。[pdf:E12] [pdf:E06]

论文没有报告多速率时间推进；描述的是由 RTDS 同步信号驱动的同一步长流程。它也没有给出 FPGA 内部采用 fixed-point 还是 floating-point、各变量 word length、量化与溢出策略；“32-bit signals”只明确出现在通信链路描述中，不能据此推定内部数值格式。开关/事件处理也只具体到预存故障矩阵，未展示面向高频电力电子开关的通用事件调度。

## § 6 — 核心数学推导（无形式化数学则跳过）

论文的形式化数学不多，核心是同步机状态方程和延迟传输线接口。

**1. 同步机连续模型。** PDF 物理页 2，Section II-A-1，Eq. (1)–(3) 给出：

\[
\mathbf v_{dq0}=-\mathbf R\mathbf i_{dq0}+\frac{1}{\omega_{base}}\frac{d\boldsymbol\lambda_{dq0}}{dt}+\mathbf u,
\]

\[
\boldsymbol\lambda_{dq0}=\mathbf L\mathbf i_{dq0},
\]

\[
T_m=2H\frac{d\omega_r}{dt}+D\omega_r+T_e.
\]

其中 \(\mathbf v_{dq0}\)、\(\mathbf i_{dq0}\)、\(\boldsymbol\lambda_{dq0}\) 分别是 \(dq0\) 电压、电流和磁链向量；\(\mathbf R\)、\(\mathbf L\) 是电阻与电感矩阵；\(T_m\)、\(T_e\)、\(H\)、\(D\) 描述机械输入、电磁转矩、惯量和阻尼。论文说明除时间外均采用 per unit，并把这些方程按 trapezoidal rule 离散后映射为六个硬件子模块。[pdf:E09]

**基于证据的离散化重建。** 从 Eq. (1) 可先整理为

\[
\frac{d\boldsymbol\lambda}{dt}=\omega_{base}\bigl(\mathbf v+\mathbf R\mathbf i-\mathbf u\bigr).
\]

对一个步长 \(\Delta t\) 作梯形积分，可得

\[
\boldsymbol\lambda_n=\boldsymbol\lambda_{n-1}+\frac{\omega_{base}\Delta t}{2}
\left[
(\mathbf v_n+\mathbf R\mathbf i_n-\mathbf u_n)
+(\mathbf v_{n-1}+\mathbf R\mathbf i_{n-1}-\mathbf u_{n-1})
\right].
\]

再代入 \(\boldsymbol\lambda_n=\mathbf L\mathbf i_n\)，就把本步电流写成“本步端电压 + 上一步 history term”的线性代数问题；这正是后续 pipeline 可以重复求解同类机器的原因。论文没有打印这一离散递推式，因此这里是由 Eq. (1)–(2) 与文中“采用梯形积分”说明作出的推导，不是作者原式。[pdf:E09]

**2. 延迟传输线接口。** PDF 物理页 4，Section III-A-2，Eq. (4)–(5) 为：

\[
I_{h,\mathrm{FPGA}}(t-\tau)=-\frac{1}{Z}v_{\mathrm{RTDS}}(t-\tau)-i_{\mathrm{RTDS}}(t-\tau),
\]

\[
I_{h,\mathrm{RTDS}}(t-\tau)=-\frac{1}{Z}v_{\mathrm{FPGA}}(t-\tau)-i_{\mathrm{FPGA}}(t-\tau).
\]

它们把对端延迟到达的电压、电流合成为本端 Norton history current。只要 \(\tau\geq\Delta t\)，本步的 RTDS 解不依赖 FPGA 的“同一时刻未知量”，反之亦然，于是没有即时 algebraic loop；这就是该 co-simulator 能先交换数据、后并行推进的数学基础。[pdf:E05] [pdf:E12]

论文没有给出接口误差上界、离散系统稳定性证明，也没有分析 \(\tau/\Delta t\)、通信抖动或不同数值表示对能量守恒和相位误差的影响。因此这里的数学贡献更接近“可硬件实现的结构化离散与端口解耦”，不是一套带严格误差定理的新算法。

## § 7 — 实验设计与结论

**问题 1：分区 co-simulation 能否复现同一系统在 RTDS 内整体仿真的暂态波形？ → 实验。** Case 1 把两区域四机系统沿 TL78 分成 RTDS 与 FPGA 两区，同时在 RTDS 中完整搭建参考系统；在 bus 7 施加 150 ms 三相故障。比较量包括 bus 6 三相电压、G4 electrical torque，以及 TL78a、TL89a 的三相线电流（PDF 物理页 6，Section V-A 与 Fig. 8）。[pdf:E08] **→ 答案。** Fig. 9 的波形叠加显示故障后的高频振荡、机电振荡、三相不平衡和恢复过程在视觉上高度一致；作者据此认定 same-type EMT models 使专门的 EMT–TS interface technique 不再需要（PDF 物理页 6–7，Fig. 9）。[pdf:E14] [pdf:E15] 但论文没有报告 RMSE、最大误差、相位差或能量误差，因此这只能支持“所展示工况下的定性/图形一致”，不能支持一个已量化的通用精度界。

**问题 2：平台能否承载明显更大的交流网络？ → 实验。** Case 2 使用 141 个三相 bus；其中 5 个 bus 与 G37、G38 在 RTDS，其他网络在 FPGA，接口为 TL3A、TL3B，并在 bus 141 施加 100 ms 三相故障。作者估计若只用 RTDS，需要 4 个 PB5 racks；所提方案使用 1 块 FPGA board 和 1 个 PB5 rack 的一半计算资源（PDF 物理页 7，Section V-B）。[pdf:E16] Fig. 10 展示了 RTDS 小区域与 FPGA 大区域的实际拓扑划分（PDF 物理页 8，Fig. 10）。[pdf:E17] **→ 答案。** RTDS 侧 bus 140、TL2、G37/G38 与 FPGA 侧 bus 41、相邻线路、G14/G15 都给出了故障响应，说明整套链路能在该规模下运行并产生物理上连贯的波形（PDF 物理页 8，Fig. 11–12）。[pdf:E18] 但 Case 2 没有提供同规模 monolithic RTDS 波形作为精度基线，因此它主要验证“运行能力”，不是再次验证“数值等价”。

**问题 3：网络扩展对资源和实时步长的代价是否足够温和？ → 实验。** Case 1 与 Case 2 在 Xilinx Virtex-6、100 MHz 下的最小步长分别为 5.71 μs 与 20.16 μs（PDF 物理页 6，Section V）。[pdf:E14] Table I 报告从 Case 1 到 Case 2，FPGA 区域规模增加超过 20 倍，而各类资源使用量只增加约 3.3–3.7 倍：Case 2 使用 17.4% slice registers、73.2% slice LUTs、10.8% block RAMs 和 40.0% DSP48E1s（PDF 物理页 7，Table I 与 Section VI）。[pdf:E19] Fig. 13 把 Case 2 的 20.16 μs 拆成 step 0–6，并显示关键路径由每一步最慢模块决定（PDF 物理页 9，Fig. 13）。[pdf:E20] 例如 step 1 中 passive-element、transmission-line、rotor prediction 的耗时分别为 1.95、4.05、1.18 μs，因此 passive-element pipeline 理论上还有 2.1 μs，即 100 MHz 下约 210 个元件的余量；作者还以典型 RTS 步长约 50 μs 作为进一步扩容的参照（PDF 物理页 9，Section VI）。[pdf:E21] **→ 答案。** 模块化与流水确实让扩容代价低于网络规模的线性增长，但 LUT 已到 73.2%，说明 Case 2 的首先触顶资源很可能是 LUT，而不是表中平均意义上的“仍有大量余量”；这是基于 Table I 的推断，不是作者给出的瓶颈分析。[pdf:E19]

实验总体支持“可运行、可扩展、在一个参考工况下波形接近”的 claim；它尚未覆盖短接口线、不同故障类型、通信扰动、参数扫频、量化误差和长期实时稳定性，所以不能把结果外推成对任意分区和任意 EMT 工况的无误差保证。

## § 8 — Take-aways

**5 句话：** ① 这篇论文把 FPGA 定位成 RTDS 的外部交流网扩展，而不是替代 RTDS 的完整建模环境。② 两侧统一采用 EMT 模型，确实绕开了 EMT–TS 模型转换这一类接口误差。[pdf:E01] ③ 真正让两侧可并行求解的是接口传输线的传播时延，而不是光纤带宽本身。[pdf:E05] ④ 模块并行、同类元件流水和按瓶颈复制模块，使 141-bus 案例在 20.16 μs 步长下运行，并把资源增长压到小于网络规模增长。[pdf:E19] [pdf:E20] ⑤ 证据最弱的地方是没有量化误差、没有短线接口测试，也没有公开足以独立复现的完整参数与数值格式。

**3 句话：** ① 论文用“RTDS 负责灵活、FPGA 负责规模”的分工，构建了同一 EMT 层级的实时 co-simulator。② Case 1 给出与全 RTDS 参考波形的视觉一致，Case 2 给出 141-bus 运行与资源/时序结果，但精度评价仍以定性曲线为主。[pdf:E15] [pdf:E16] ③ 其可用范围由 \(\tau\geq\Delta t\) 的传输线解耦假设决定。

**1 句话：** 这是一项工程结构上很清楚、硬件结果有说服力，但接口适用边界与误差定量化仍未闭合的 FPGA–RTDS EMT co-simulation 方案（PDF 物理页 9，Conclusion）。[pdf:E22]

## § 9 — 最脆弱的假设

最脆弱的假设是：**总能把 study system 与 external system 的 cut-set 放在一条或多条传播时间不短于仿真步长的 transmission lines 上。** 论文直接把“wave travelling time 至少等于一个 simulation time-step”作为计算解耦条件；Case 1 和 Case 2 也都选择传输线作为接口（PDF 物理页 4，Section III-A-2；PDF 物理页 6–7，Fig. 8 与 Case 2 描述）。[pdf:E05] [pdf:E08] [pdf:E16]

如果边界只能落在短线路、变压器、母联或强耦合多端口网络上，物理传播时间可能小于 \(\Delta t\)。此时 Eq. (4)–(5) 不能仅用已知的 \(t-\tau\) 量完成本步两侧独立求解；强行加入一个整步延迟会带来额外相位滞后和可能的非物理能量交换，不加延迟则重新出现 algebraic loop，需要迭代或隐式耦合。核心贡献并非完全失效——同 EMT 模型仍有价值——但“无需特殊接口技术即可准确解耦”这一最强论点会直接收缩。

论文给出的支持证据是：所选接口传输线下，Case 1 波形与 RTDS 参考图形一致，并且通信与计算能在实时步长内完成。[pdf:E14] [pdf:E15] 缺失证据是：没有扫 \(\tau/\Delta t\)，没有短线或非传输线 cut-set，没有接口数增加后的稳定性分析，也没有以误差指标证明延迟接口只引入可忽略误差。

## § 10 — 最小复现实验

一周内最值得复现的不是完整 141-bus FPGA 系统，而是“同 EMT 模型 + 延迟传输线接口能否把额外 interface error 压到离散误差量级”这一核心机制。

- **数据与模型：** 建一个参数完全自定、可公开的三相双源网络，包含两台简化同步源、RLC 负载和一条 distributed-parameter line；在一端施加三相故障。附件只说明 Case 1 参数来自外部文献，没有给完整参数表，因此无法仅凭本包做严格的 Case 1 数值复现（PDF 物理页 6，Section V-A）。[pdf:E08]
- **实现：** 写两个使用同一 trapezoidal companion models 的版本。版本 A 是单进程 monolithic EMT；版本 B 沿传输线分成两个进程，按 Eq. (4)–(5) 只交换延迟端口电压、电流。先选择 \(\tau\geq\Delta t\)，并用同一初值、同一故障时刻运行（PDF 物理页 4，Eq. (4)–(5)）。[pdf:E12]
- **测量：** 对接口电压/电流、远端母线电压和源电磁功率计算 normalized RMS error、最大瞬时误差、相位偏差与累计能量不平衡；再把 monolithic 模型步长减半，得到其自身离散误差基线。另记录版本 B 每步的最坏执行时间是否低于 \(\Delta t\)。
- **支持条件：** split-vs-monolithic 的误差不显著大于 monolithic step-halving error，且每步都按时完成；这说明接口没有成为主导误差源。
- **反驳条件：** 即使两侧模型和步长完全相同，分区误差仍明显超过单体离散误差、故障后出现持续能量漂移，或计算不能稳定满足 deadline；这会直接削弱论文最核心的准确性或实时性 claim。

这个实验能验证接口原理，但不能验证 Virtex-6 的具体资源效率。后者必须取得相同或等价 FPGA/RTDS 硬件、HDL 与数值格式，而论文没有提供足够实现细节。

## § 11 — 最强反例设计

最强反例是构造一个**无法满足传播时延条件、但又不能任意移动分区边界**的网络。

把 Case 1 的 TL78 替换为一条电气上很短的线路或变压器，使 \(\tau<\Delta t\)；在接口附近施加 single-line-to-ground fault（单相接地故障）并叠加高频扰动，使零序、负序和快速暂态都必须穿过接口。保持两侧 EMT 元件模型完全一致，只改变耦合方式，并扫描 \(\tau/\Delta t\) 从大于 1 到小于 1。基线使用 monolithic EMT；被测方案分别使用论文的显式延迟接口、强制一整步延迟，以及有限次数的本步迭代。

真正有杀伤力的观测不是“曲线看起来有一点不同”，而是出现可预测的机制性失败：随着 \(\tau/\Delta t\) 低于 1，显式接口的相位误差和能量不平衡单调放大，甚至触发数值振荡；而 monolithic 模型在同一步长下仍稳定。若这种现象出现，就能提出一个具体替代解释：Case 1 的高一致性主要来自所选 cut-set 恰好满足 travelling-wave decoupling，而不是该架构对任意 FPGA–RTDS 分区都天然无接口误差。这个反例直接针对论文写明的解耦条件，而不是泛泛质疑硬件规模。[pdf:E05]

## § 12 — Follow-up Research Idea

在 EMT、FPGA 和实时电力系统仿真领域，高影响研究通常要同时给出可复现实物系统、明确的实时 deadline、量化精度、资源可扩展性，以及对困难工况的边界验证。基于第 9 节的限制，一个非增量的候选方向是：**面向任意 cut-set 的有界时延、残差驱动 EMT co-simulation**。这里不声称 novelty；本包没有提供相关全文检索，只能把它作为证据约束下的候选想法。

**（a）未满足需求。** 现实网络的自然研究边界未必经过长传输线。若必须为了 \(\tau\geq\Delta t\) 而移动边界，study system 可能被迫扩大，FPGA 侧也可能包含本应频繁修改的元件，平台最初的“灵活区/稳定区”分工就被破坏。[pdf:E05]

**（b）潜在研究价值。** 把目标从“在有传播延迟的线路上显式解耦”改成“对短线、变压器和多端口 cut-set 也能在固定实时预算内保持可控误差”，会扩大可建模系统类别，并把接口准确性从示例波形提升为可测量的误差–时延折中。

**（c）可借鉴的相邻工具。** 可以设计双模式接口：满足 \(\tau\geq\Delta t\) 时沿用本文的 travelling-wave Norton interface；不满足时，在一个仿真步内执行固定次数的 predictor–corrector / relaxation exchange，并以端口电流、电压残差决定是否启用校正。论文参考文献题名中已出现“implicitly coupled”与“relaxation approach”两类方向，但这里只能确认这些方向被作者列入相关工作，不能据此声称其具体算法或效果（PDF 物理页 9，References [10]–[12]）。[pdf:E23]

**（d）第一个证伪实验。** 使用第 11 节的短线/变压器 cut-set，限定每步最多一到两次校正交换；若在相同硬件预算下，残差驱动接口既不能把能量和相位误差降到 monolithic 离散误差附近，又不能满足实时 deadline，这个想法就应被否定，而不是继续堆模块。

**（e）与本文的实质区别。** 本文通过选择有物理传播延迟的边界来消除同一步耦合；候选方向则把“任意边界下的耦合残差”本身变成实时求解对象，并把固定迭代预算、误差监测与调度共同纳入系统设计。它改变的是问题定义和适用边界，不只是换更大的 FPGA、增加一类元件或把 141-bus 扩成更多 bus。
